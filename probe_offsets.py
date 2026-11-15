#!/usr/bin/env python3
"""Find optional live-only offsets and record them in the matching profile.

    sudo .venv/bin/python probe_offsets.py team      # Player.Team; join a game that has teams
    sudo .venv/bin/python probe_offsets.py health    # Humanoid.Health/MaxHealth; you take damage
    sudo .venv/bin/python probe_offsets.py subject   # Camera.CameraSubject + Instance.WeakThis (read-only)
    sudo .venv/bin/python probe_offsets.py teleport  # solver position; you stand still, it lifts you
    sudo .venv/bin/python probe_offsets.py viewport  # Camera viewport size (int16 pair); you resize the window

Features that need a field (team colors, health bars, spectate, teleport) stay
off until it is recorded. A field is written only when exactly one offset
survives every check.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
import time

from rbxl.esp_reader import ESPReader, OffsetSpec
from dumper import prims
from rbxl.memory import MemoryFault, find_roblox_pid
from rbxl.movement import MachFieldWriter
from rbxl.physics_control import PhysicsController, PhysicsSpec
from rbxl.profiles import select_profile, write_json

WINDOW = 0x800
MAX_ROUNDS = 6


def attach():
    pid = find_roblox_pid()
    if pid is None:
        raise RuntimeError("Roblox is not running")
    profile = select_profile()
    spec = OffsetSpec.from_report(profile / "offsets.json").with_camera_evidence(profile / "camera.json")
    reader = ESPReader.attach(pid, spec)
    local = reader.pointer(reader.players + spec.local_player)
    if reader.klass(local) != "RBX::Player":
        raise RuntimeError("local player not found")
    return profile, reader, local


def record(profile, fields, method):
    path = profile / "offsets.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    for name, value in fields.items():
        report["resolved"][name] = {"value": value, "method": method, "confidence": 1.0}
    write_json(path, report)
    print(f"[probe] recorded {', '.join(f'{name} = {value:#x}' for name, value in fields.items())} in {path}")


def roster(reader):
    return [player for player in reader.children(reader.players, 128) if reader.klass(player) == "RBX::Player"]


def probe_team(profile, reader, local):
    players = roster(reader)
    window = reader.mem.read(local, WINDOW)
    candidates = []
    for offset in range(0, WINDOW, 8):
        team = struct.unpack_from("<Q", window, offset)[0]
        if reader.klass(team) != "RBX::Team" or reader.klass(reader.pointer(team + reader.spec.parent)) != "RBX::Teams":
            continue
        # Every player's slot must hold nothing or a Team.
        slots = [reader.pointer(player + offset) for player in players]
        if all(slot == 0 or reader.klass(slot) == "RBX::Team" for slot in slots):
            candidates.append(offset)
    print(f"[probe] Player.Team candidates: {[hex(offset) for offset in candidates]} across {len(players)} players")
    if len(candidates) != 1:
        raise RuntimeError("Player.Team is not unique; join a game with teams (and you on one) and retry")
    record(profile, {"Player.Team": candidates[0]}, "live probe: only Player slot pointing at a Team under Teams")


def humanoid_of(reader, player):
    character = reader.pointer(player + reader.spec.character)
    for child in reader.children(character, 128):
        if reader.klass(child) == "RBX::Humanoid":
            return child
    raise RuntimeError("your character has no Humanoid yet; wait until you spawn")


def floats(reader, address):
    return struct.unpack(f"<{WINDOW // 4}f", reader.mem.read(address, WINDOW))


def probe_health(profile, reader, local):
    humanoid = humanoid_of(reader, local)
    full = floats(reader, humanoid)
    # Health and MaxHealth are equal at full health; MaxHealth never moves with damage.
    pairs = [(h * 4, m * 4) for h, health in enumerate(full) if 0 < health <= 1e6
             for m, maximum in enumerate(full) if m != h and maximum == health]
    previous = full
    for round_number in range(1, MAX_ROUNDS + 1):
        input(f"[probe] round {round_number}: take some damage (fall, get hit), then press Enter… ")
        humanoid = humanoid_of(reader, local)  # respawns replace the Humanoid
        current = floats(reader, humanoid)
        pairs = [(h, m) for h, m in pairs
                 if current[h // 4] != previous[h // 4] and 0 <= current[h // 4] <= current[m // 4]
                 and current[m // 4] == full[m // 4]]
        previous = current
        print(f"[probe] {len(pairs)} Health/MaxHealth pairs remain")
        if len({h for h, _ in pairs}) == 1 and len(pairs) >= 1:
            break
    healths = {h for h, _ in pairs}
    if len(healths) != 1:
        raise RuntimeError("Humanoid.Health is not unique; retry and take damage each round")
    health = healths.pop()
    # Several MaxHealth candidates can share the value; prefer the nearest field after Health.
    maximum = min((m for h, m in pairs), key=lambda m: (m < health, abs(m - health)))
    for player in roster(reader):
        try:
            other = floats(reader, humanoid_of(reader, player))
        except (RuntimeError, MemoryFault):
            continue
        if not 0 <= other[health // 4] <= other[maximum // 4]:
            raise RuntimeError(f"another player's Health/MaxHealth at {health:#x}/{maximum:#x} is inconsistent")
    record(profile, {"Humanoid.Health": health, "Humanoid.MaxHealth": maximum},
           "live probe: field that tracked damage while its MaxHealth sibling stayed fixed")


def qword(window, offset):
    return struct.unpack_from("<Q", window, offset)[0]


def probe_subject(profile, reader, local):
    """CameraSubject is a smart pointer: (Humanoid*, control block). Every Instance keeps
    its own (self, control block) pair; spectate copies a target's pair into the camera."""
    humanoid = humanoid_of(reader, local)
    camera = reader.pointer(reader.workspace + reader.spec.camera)
    if reader.klass(camera) != "RBX::Camera":
        raise RuntimeError("CurrentCamera not found")
    window = reader.mem.read(camera, WINDOW)
    subjects = [(offset, qword(window, offset + 8)) for offset in range(0, WINDOW - 8, 8)
                if qword(window, offset) == humanoid]
    print(f"[probe] Camera slots holding your Humanoid: {[hex(offset) for offset, _ in subjects]}")
    body = reader.mem.read(humanoid, WINDOW)
    matches = [(offset, self_offset) for offset, control in subjects if prims.plausible_ptr(control)
               for self_offset in range(0, WINDOW - 8, 8)
               if qword(body, self_offset) == humanoid and qword(body, self_offset + 8) == control]
    # The self pair must hold for every other Humanoid too.
    others = [humanoid_of(reader, player) for player in roster(reader) if player != local
              and reader.klass(reader.pointer(player + reader.spec.character)) in ("RBX::Model", "RBX::ModelInstance")]
    matches = [(offset, self_offset) for offset, self_offset in matches
               if all(reader.pointer(other + self_offset) == other
                      and prims.plausible_ptr(reader.pointer(other + self_offset + 8)) for other in others)]
    print(f"[probe] (CameraSubject, WeakThis) candidates: {[(hex(a), hex(b)) for a, b in matches]} "
          f"checked against {len(others)} other Humanoids")
    if len(matches) != 1:
        raise RuntimeError("CameraSubject is not unique; spawn in, keep the default camera and retry")
    subject, weak_this = matches[0]
    record(profile, {"Camera.CameraSubject": subject, "Instance.WeakThis": weak_this},
           "live probe: camera smart pointer equal to the local Humanoid's own (self, control) pair")


POSITION_WINDOW = 0x1000   # solver body bytes searched for the position
POSITION_TOLERANCE = 3.0   # studs; the solver may track the centre of mass, not the root part
LIFT = 10.0


def probe_teleport(profile, reader, local):
    physics = PhysicsController(reader, PhysicsSpec.from_evidence(profile / "physics.json", reader.spec.binary_sha256))
    if physics.spec.solver_body is None:
        raise RuntimeError("run probe_jump_velocity.py first; teleport uses the same solver body")
    physics.character = physics._character()
    physics._scan(time.monotonic())
    root, body = physics._solver()
    pose = [root + physics.spec.velocity - 12, root + physics.spec.velocity_mirror - 12]
    position = struct.unpack("<3f", reader.mem.read(pose[0], 12))
    window = reader.mem.read(body, POSITION_WINDOW)
    candidates = []
    for code, width in (("f", 4), ("d", 8)):
        for offset in range(0, POSITION_WINDOW - 3 * width + 1, width):
            values = struct.unpack_from(f"<3{code}", window, offset)
            if all(abs(a - b) <= POSITION_TOLERANCE for a, b in zip(values, position)) and abs(values[1]) > 0.5:
                candidates.append((offset, code))
    print(f"[probe] your position {tuple(round(v, 2) for v in position)}; solver body candidates: "
          f"{[(hex(offset), code) for offset, code in candidates]}")
    if not candidates:
        raise RuntimeError("no solver body value near your position; nothing recorded")
    writer = MachFieldWriter(reader.mem)
    # The three float copies sit 72 bytes apart, each a (position, velocity) block; the
    # engine's choice among them varies with state, so teleport moves all of them together.
    blocks = sorted({offset for offset, code in candidates if code == "f"
                     and any((offset - other) % 72 == 0 and offset != other
                             for other, other_code in candidates if other_code == "f")})
    print(f"[probe] position blocks 72 bytes apart: {[hex(offset) for offset in blocks]}")
    if len(blocks) < 2:
        raise RuntimeError("no 72-byte block family among the candidates; nothing recorded — paste this output")

    def write_all(lift):
        root, body = physics._solver()
        for offset in blocks:
            current = struct.unpack("<f", reader.mem.read(body + offset + 4, 4))[0]
            writer.write(body + offset + 4, struct.pack("<f", current + lift))
        for copy in pose:
            current = struct.unpack("<f", reader.mem.read(copy + 4, 4))[0]
            writer.write(copy + 4, struct.pack("<f", current + lift))

    def trial(held):
        before = struct.unpack("<3f", reader.mem.read(pose[0], 12))
        target = before[1] + LIFT
        write_all(LIFT)
        if held:
            # Re-assert for ~50 ms so a physics step cannot restore the old copy in between.
            for _ in range(3):
                time.sleep(0.016)
                current = struct.unpack("<f", reader.mem.read(pose[0] + 4, 4))[0]
                if current < target - 0.5:
                    write_all(target - current)
        time.sleep(0.15)
        after = struct.unpack("<3f", reader.mem.read(pose[0], 12))
        moved = after[1] - before[1] > LIFT * 0.6
        print(f"[probe]   {'held' if held else 'once'}: y {before[1]:.2f} -> {after[1]:.2f} {'LIFT' if moved else '-'}",
              flush=True)
        time.sleep(1.6)  # land before the next test
        return moved

    input("[probe] stand still on flat ground, then press Enter (10 lifts of 10 studs)… ")
    once = sum(trial(False) for _ in range(5))
    held = sum(trial(True) for _ in range(5))
    print(f"[probe] all blocks: once {once}/5, held {held}/5", flush=True)
    if max(once, held) < 4:
        raise RuntimeError("teleport by position copies is not reliable (need 4/5); nothing recorded — paste this output")
    path = profile / "physics.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    report["solver"]["positions"] = blocks
    report["solver"]["position_hold"] = held > once
    report["solver"].pop("position", None)
    report["solver"].pop("position_type", None)
    write_json(path, report)
    print(f"[probe] recorded solver positions {[hex(offset) for offset in blocks]} "
          f"({'held' if held > once else 'single'} write) in {path}")

VIEWPORT_WINDOW = 0x800  # Camera bytes searched for the viewport size


def viewport_pairs(reader, camera):
    """{offset: (w, h)} for int16 pairs in the camera that look like a window size."""
    raw = reader.mem.read(camera, VIEWPORT_WINDOW)
    pairs = {}
    for offset in range(0, VIEWPORT_WINDOW - 3, 2):
        width, height = struct.unpack_from("<hh", raw, offset)
        if 200 <= width <= 8000 and 150 <= height <= 6000 and 0.5 <= width / height <= 3.5:
            pairs[offset] = (width, height)
    floats = {}
    for offset in range(0, VIEWPORT_WINDOW - 7, 4):
        width, height = struct.unpack_from("<ff", raw, offset)
        if 200 <= width <= 8000 and 150 <= height <= 6000 and width.is_integer() and height.is_integer():
            floats[offset] = (int(width), int(height))
    return pairs, floats


def probe_viewport(profile, reader, local):
    """The camera's viewport size is the pair that changes, consistently, when the window is resized."""
    camera = reader.pointer(reader.workspace + reader.spec.camera)
    if reader.klass(camera) != "RBX::Camera":
        raise RuntimeError("CurrentCamera not found")
    before, before_floats = viewport_pairs(reader, camera)
    print(f"[probe] window-sized int16 pairs: {[(hex(o), v) for o, v in before.items()]}")
    print(f"[probe] window-sized float pairs: {[(hex(o), v) for o, v in before_floats.items()]}")
    input("[probe] now RESIZE the Roblox window noticeably (drag a corner), then press Enter… ")
    after, after_floats = viewport_pairs(reader, camera)
    changed = [offset for offset, size in before.items() if offset in after and after[offset] != size]
    changed_floats = [offset for offset, size in before_floats.items()
                      if offset in after_floats and after_floats[offset] != size]
    print(f"[probe] int16 pairs that followed the resize: {[(hex(o), before[o], after[o]) for o in changed]}")
    print(f"[probe] float pairs that followed the resize: "
          f"{[(hex(o), before_floats[o], after_floats[o]) for o in changed_floats]}")
    if len(changed) != 1:
        raise RuntimeError("viewport size is not unique; resize more and retry — paste this output")
    fields = {"Camera.ViewportInt16": changed[0]}
    matching = [offset for offset in changed_floats if after_floats[offset] == after[changed[0]]]
    if len(matching) == 1:
        fields["Camera.ViewportSize"] = matching[0]
    record(profile, fields, "live probe: the window-sized pair that followed a window resize")


PROBES = {"team": probe_team, "health": probe_health, "subject": probe_subject, "teleport": probe_teleport,
          "viewport": probe_viewport}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("field", choices=tuple(PROBES))
    args = parser.parse_args(argv)
    profile, reader, local = attach()
    try:
        PROBES[args.field](profile, reader, local)
    finally:
        reader.close()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, MemoryFault, OSError) as exc:
        print(f"[probe] {exc}", file=sys.stderr)
        raise SystemExit(1)
