#!/usr/bin/env python3
"""Build a runtime profile for the installed Roblox client after an update.

    sudo .venv/bin/python update_profile.py

Join a game first. Offline getter evidence (geometry, camera, movement,
physics) comes from the binary and the instance layout from one live
discovery. Writes profiles/<version>-<sha8>/ and never overwrites a profile.
Then, for a new or already-matching profile, finds a module global that
leads to the live DataModel within two pointer hops and records it once
attaching through it reaches the same DataModel (fast attach).

Live-only fields are added afterwards by their probes:
    probe_jump_velocity.py   solver velocity (Infinite Jump, Fly)
    probe_offsets.py team    Player.Team (team colors, team check)
    probe_offsets.py health  Humanoid.Health/MaxHealth (health bars)
"""
from __future__ import annotations

import json
import sys

from dumper.arm64_accessors import inspect_geometry_accessors
from dumper.camera_accessors import inspect_camera_accessors
from dumper.derive import Deriver
from dumper.emit import client_version
from dumper.solve import WalkError
from dumper.macho import MachO
from dumper.movement_accessors import inspect_movement_accessors
from dumper.physics_accessors import inspect_physics_accessors
from rbxl.esp_reader import ESPReader, OffsetSpec
from rbxl.fast_attach import find_chain
from rbxl.memory import MachProcess, MemoryFault, find_roblox_pid
from rbxl.movement import MovementSpec
from rbxl.physics_control import PhysicsSpec
from rbxl.profiles import CLIENT, PROFILES, binary_sha256, give_back, profile_sha256, write_json

# Heuristic findings that probe_offsets.py must confirm before the runtime trusts them.
PROBE_ONLY = ("Humanoid.Health", "Humanoid.MaxHealth", "Player.Team")


def offline_evidence(mach):
    geometry = inspect_geometry_accessors(mach)
    camera = inspect_camera_accessors(mach)
    movement = inspect_movement_accessors(mach)
    physics = inspect_physics_accessors(mach)
    if geometry["selected"] is None or camera["selected"] is None:
        raise RuntimeError("geometry or camera getters are not unique in this build")
    if len(movement["selected"]) != 4 or len(physics["selected"]) != 9:
        raise RuntimeError("movement or physics getters are incomplete in this build")
    print("[update] offline getters: geometry, camera, movement and physics resolved", flush=True)
    return geometry, camera, movement, physics


def live_findings():
    pid = find_roblox_pid()
    if pid is None:
        raise RuntimeError("Roblox is not running; join a game first")
    mem = MachProcess(pid)
    try:
        regions = list(mem.regions())
        # The renderer chain is found by RTTI in add_fast_attach, not by the deriver's heap-wide scan.
        report = Deriver(mem, regions, verbose=True, skip_renderer=True).run()
    finally:
        mem.close()
    if report.layout is None or report.layout.children_kind != "ptr":
        raise RuntimeError("live layout does not use pointer-to-vector children; the reader cannot use it")
    return report


def build_offsets(report, geometry, camera, digest):
    resolved = {path: {"value": finding.value, "method": finding.method, "confidence": finding.confidence}
                for path, finding in report.findings.items() if path not in PROBE_ONLY}
    getter = "same-binary static getter"
    selected = geometry["selected"]
    cframe = selected["primitive_cframe_offset"]
    camera_frame = camera["selected"]["camera_cframe_offset"]
    resolved.update({
        "BasePart.Primitive": {"value": selected["basepart_primitive_offset"], "method": getter, "confidence": 1.0},
        "Primitive.CFrame": {"value": cframe, "method": getter, "confidence": 1.0},
        "Primitive.Position": {"value": cframe + 36, "method": getter, "confidence": 1.0},
        "Camera.CFrame": {"value": camera_frame, "method": getter, "confidence": 1.0},
        "Camera.Position": {"value": camera_frame + 36, "method": getter, "confidence": 1.0},
        "Camera.FieldOfView": {"value": camera["selected"]["camera_fov_offset"], "method": getter, "confidence": 1.0},
        # The reader walks pointer-to-vector children: begin, then end 8 bytes later.
        "Instance.ChildrenEnd": {"value": 8, "method": "pointer-to-vector end delta", "confidence": 1.0},
    })
    return {"version": client_version(str(CLIENT)), "resolved": resolved,
            "evidence": {"static_geometry_accessors": {"binary_sha256": digest, "selected": {
                key: selected[key] for key in ("basepart_primitive_offset", "primitive_cframe_offset",
                                               "primitive_position_offset")}}},
            "notes": report.notes}


def add_fast_attach(directory):
    path = directory / "offsets.json"
    offsets = json.loads(path.read_text(encoding="utf-8"))
    if "fast_attach" in offsets:
        print(f"[update] {directory.name} already has fast attach; nothing to do")
        return 0
    pid = find_roblox_pid()
    if pid is None:
        raise RuntimeError("Roblox is not running; join a game first")
    spec = OffsetSpec.from_report(path).with_camera_evidence(directory / "camera.json")
    reader = ESPReader.attach(pid, spec)
    try:
        chain = find_chain(reader)
        if chain is None:
            raise RuntimeError("no module global leads to the live DataModel within two hops; profile left unchanged")
        slot, hops = chain
        print(f"[update] chain: global +{slot:#x} -> {' -> '.join(f'+{hop:#x}' for hop in hops)}", flush=True)
        offsets["fast_attach"] = {"slot": slot, "hops": list(hops),
                                  "method": "module global chain resolved to the live DataModel"}
        candidate = directory / "offsets.fast.json"
        write_json(candidate, offsets)
        # Prove it the way main.py will use it before replacing the profile.
        try:
            fast = ESPReader._fast_attach(reader.mem, OffsetSpec.from_report(candidate).with_camera_evidence(
                directory / "camera.json"))
            if fast.root != reader.root:
                raise RuntimeError("fast attach reached a different DataModel")
        except (WalkError, RuntimeError) as exc:
            candidate.unlink()
            raise RuntimeError(f"{exc}; profile left unchanged") from exc
        candidate.replace(path)
    finally:
        reader.close()
    print(f"[update] fast attach verified (DataModel {reader.root:#x}) and recorded in {directory.name}")
    print("[update] rejoin a different server and run main.py: 'fast attach' confirms the chain survives")
    return 0


def main():
    digest = binary_sha256(CLIENT)
    for existing in PROFILES.iterdir():
        if existing.is_dir() and profile_sha256(existing) == digest:
            return add_fast_attach(existing)
    directory = PROFILES / f"{client_version(str(CLIENT))}-{digest[:8]}"
    mach = MachO(str(CLIENT))
    geometry, camera, movement, physics = offline_evidence(mach)
    report = live_findings()
    offsets = build_offsets(report, geometry, camera, digest)

    directory.mkdir()
    give_back(directory)
    files = {"offsets.json": offsets, "camera.json": camera, "movement.json": movement, "physics.json": physics}
    for name, payload in files.items():
        write_json(directory / name, payload, exclusive=True)
    # The same loaders main.py uses; a profile that fails here is unusable.
    spec = OffsetSpec.from_report(directory / "offsets.json").with_camera_evidence(directory / "camera.json")
    MovementSpec.from_evidence(directory / "movement.json", spec.binary_sha256)
    PhysicsSpec.from_evidence(directory / "physics.json", spec.binary_sha256)
    print(f"[update] wrote and validated {directory}")
    add_fast_attach(directory)
    print("[update] next: probe_jump_velocity.py, probe_offsets.py team, probe_offsets.py health")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, MemoryFault, OSError, ValueError, KeyError) as exc:
        print(f"[update] {exc}", file=sys.stderr)
        raise SystemExit(1)
