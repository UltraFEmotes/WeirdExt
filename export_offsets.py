#!/usr/bin/env python3
"""Export the matching profile as a public offset dump for macOS ARM64.

    .venv/bin/python export_offsets.py            # profile matching the installed client
    .venv/bin/python export_offsets.py --profile profiles/<dir>

Writes dumps/<version>/offsets.hpp, offsets.json and offsets.cs, grouped as
Namespace::Name like common Windows dumps. Only offsets the profile holds
evidence for are exported. macOS ARM64 layouts differ from Windows; these
values are for the macOS client only. No game process is opened.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from rbxl.profiles import PROFILES, select_profile, write_json

ROOT = Path(__file__).resolve().parent
DUMPS = ROOT / "dumps"
# Report key -> (namespace, public name). Order here is the order in the dump.
RESOLVED = (
    ("Instance.Name", "Instance", "Name"),
    ("Instance.Parent", "Instance", "Parent"),
    ("Instance.ChildrenStart", "Instance", "ChildrenStart"),
    ("Instance.ChildrenEnd", "Instance", "ChildrenEnd"),
    ("Instance.WeakThis", "Instance", "This"),
    ("Players.LocalPlayer", "Players", "LocalPlayer"),
    ("Player.ModelInstance", "Player", "ModelInstance"),
    ("Player.Team", "Player", "Team"),
    ("Workspace.CurrentCamera", "Workspace", "CurrentCamera"),
    ("Camera.CFrame", "Camera", "Rotation"),
    ("Camera.Position", "Camera", "Position"),
    ("Camera.FieldOfView", "Camera", "FieldOfView"),
    ("Camera.CameraSubject", "Camera", "CameraSubject"),
    ("BasePart.Primitive", "BasePart", "Primitive"),
    ("Primitive.CFrame", "Primitive", "Rotation"),
    ("Primitive.Position", "Primitive", "Position"),
    ("Humanoid.Health", "Humanoid", "Health"),
    ("Humanoid.MaxHealth", "Humanoid", "MaxHealth"),
)
NOTES = {
    ("Instance", "Name"): "pointer to std::string",
    ("Instance", "ChildrenStart"): "pointer to a vector of 16-byte smart pointers",
    ("Instance", "ChildrenEnd"): "end pointer, relative to the children vector",
    ("Instance", "This"): "(self, control block) smart pointer pair",
    ("Camera", "Rotation"): "nine floats, row-major; Position follows at +36",
    ("Camera", "FieldOfView"): "float, radians (vertical)",
    ("Camera", "CameraSubject"): "(object, control block) smart pointer pair",
    ("Primitive", "Rotation"): "nine floats, row-major; Position follows at +36",
    ("Primitive", "AssemblyLinearVelocity"): "copy refreshed from the solver body each physics step",
    ("PrimitiveFlags", "CanCollide"): "bit mask in Primitive::Flags (a byte)",
    ("Humanoid", "WalkSpeedCheck"): "must equal WalkSpeed",
    ("Humanoid", "UseJumpPower"): "bool",
    ("SolverBody", "Pointer"): "Primitive -> solver body that physics integrates",
    ("SolverBody", "Position"): "Vector3; copies follow every BlockStride bytes",
    ("SolverBody", "Velocity"): "Vector3; write here to change motion mid-air",
    ("SolverBody", "BlockStride"): "bytes between (position, velocity) copies",
}


def collect(profile: Path):
    offsets = json.loads((profile / "offsets.json").read_text(encoding="utf-8"))
    movement = json.loads((profile / "movement.json").read_text(encoding="utf-8"))["selected"]
    physics = json.loads((profile / "physics.json").read_text(encoding="utf-8"))
    resolved = offsets["resolved"]
    entries = [(namespace, name, resolved[key]["value"]) for key, namespace, name in RESOLVED if key in resolved]
    entries += [("Humanoid", name, movement[name]) for name in ("WalkSpeed", "WalkSpeedCheck", "JumpPower", "UseJumpPower")
                if name in movement]
    selected = physics["selected"]
    entries += [("Primitive", "Flags", selected["collision_flags"]),
                ("PrimitiveFlags", "CanCollide", selected["collision_mask"]),
                ("Primitive", "AssemblyLinearVelocity", selected["velocity"])]
    solver = physics.get("solver") or {}
    if "body_pointer" in solver:
        entries.append(("SolverBody", "Pointer", solver["body_pointer"]))
        positions = solver.get("positions") or []
        if positions:
            entries.append(("SolverBody", "Position", positions[0]))
        entries.append(("SolverBody", "Velocity", solver["velocity"]))
        if len(positions) > 1:
            entries.append(("SolverBody", "BlockStride", positions[1] - positions[0]))
    meta = {
        "platform": "macOS ARM64 (Apple Silicon)",
        "roblox_version": offsets.get("version") or profile.name,
        "binary_sha256": offsets["evidence"]["static_geometry_accessors"]["binary_sha256"],
        "dumped_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "dumper": "WeirdExt export_offsets.py",
        "total": len(entries),
    }
    return meta, entries


def grouped(entries):
    groups: dict[str, list[tuple[str, int]]] = {}
    for namespace, name, value in entries:
        groups.setdefault(namespace, []).append((name, value))
    return groups


def banner(meta, comment):
    lines = ["WeirdExt offsets — macOS ARM64", "",
             f"Roblox Version  : {meta['roblox_version']}",
             f"Binary SHA-256  : {meta['binary_sha256']}",
             f"Dumped At       : {meta['dumped_at']}",
             f"Total Offsets   : {meta['total']}",
             "", "macOS layouts differ from Windows; use these with the macOS client only."]
    return "\n".join(f"{comment} {line}".rstrip() for line in lines)


def render_hpp(meta, groups):
    out = ["#pragma once", banner(meta, "//"), "", "#include <cstdint>", "", "namespace Offsets {"]
    for namespace, items in groups.items():
        out.append(f"    namespace {namespace} {{")
        for name, value in items:
            note = NOTES.get((namespace, name))
            out.append(f"        inline constexpr uintptr_t {name} = {value:#x};" + (f"  // {note}" if note else ""))
        out.append("    }")
    out.append("}")
    return "\n".join(out) + "\n"


def render_cs(meta, groups):
    out = [banner(meta, "//"), "", "namespace Offsets", "{"]
    for namespace, items in groups.items():
        out.append(f"    public static class {namespace}")
        out.append("    {")
        for name, value in items:
            note = NOTES.get((namespace, name))
            out.append(f"        public const long {name} = {value:#x};" + (f"  // {note}" if note else ""))
        out.append("    }")
    out.append("}")
    return "\n".join(out) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--profile", type=Path, help=f"profile directory under {PROFILES}")
    args = parser.parse_args(argv)
    profile = args.profile or select_profile()
    meta, entries = collect(profile)
    groups = grouped(entries)
    directory = DUMPS / meta["roblox_version"]
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "offsets.hpp").write_text(render_hpp(meta, groups), encoding="utf-8")
    (directory / "offsets.cs").write_text(render_cs(meta, groups), encoding="utf-8")
    write_json(directory / "offsets.json", {"meta": meta, "offsets": {
        namespace: {name: f"{value:#x}" for name, value in items} for namespace, items in groups.items()}})
    print(f"[export] {meta['total']} offsets for {meta['roblox_version']} -> {directory.relative_to(ROOT)}/")
    for namespace, items in groups.items():
        print(f"  {namespace:15} " + "  ".join(f"{name}={value:#x}" for name, value in items))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print(f"[export] {exc}", file=sys.stderr)
        raise SystemExit(1)
