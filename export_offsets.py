#!/usr/bin/env python3
"""Export the matching profile as a public offset dump for macOS ARM64.

    .venv/bin/python export_offsets.py            # profile matching the installed client
    .venv/bin/python export_offsets.py --profile profiles/<dir>

Writes dumps/<version>/offsets.hpp, offsets.json and offsets.cs, grouped as
Namespace::Name like common Windows dumps: the profile's live-confirmed
offsets plus every reflected property whose getter decodes to an exact shape
(dumper/reflection.py). A reflected value that disagrees with a confirmed one
stops the export. Heuristic decodes go to unverified.json, not the headers.
macOS ARM64 layouts differ from Windows; these values are for the macOS client
only. No game process is opened.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from dumper.macho import MachO
from dumper.reflection import reflect
from rbxl.profiles import CLIENT, PROFILES, select_profile, write_json

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
    ("DataModel.PlaceId", "DataModel", "PlaceId"),
    ("DataModel.GameId", "DataModel", "GameId"),
    ("DataModel.CreatorId", "DataModel", "CreatorId"),
    ("DataModel.JobId", "DataModel", "JobId"),
    ("Player.UserId", "Player", "UserId"),
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
    ("DataModel", "PlaceId"): "int64",
    ("DataModel", "GameId"): "int64 (universe id)",
    ("DataModel", "CreatorId"): "int64",
    ("DataModel", "JobId"): "std::string",
    ("Player", "UserId"): "int64",
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


# Confirmed profile offsets that reflection must reproduce exactly.
CROSS_CHECKS = (("Humanoid", "Health"), ("Humanoid", "MaxHealth"), ("Humanoid", "WalkSpeed"), ("Humanoid", "JumpPower"),
                ("Humanoid", "UseJumpPower"), ("Camera", "FieldOfView"), ("Camera", "CameraSubject"),
                ("Workspace", "CurrentCamera"), ("Instance", "Parent"), ("Instance", "Name"))


def load_verification(profile_sha, directory):
    """verify_offsets.py results for this exact binary, or an empty result."""
    path = directory / "verification.json"
    if not path.exists():
        return {"exact": {}, "heuristic": {}}
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("binary_sha256") != profile_sha:
        raise RuntimeError(f"{path} was made for a different client; rerun verify_offsets.py")
    return report


def verdict(verification, section, cls, name, entry):
    """The live verdict, only if it was made at the offset this dump uses."""
    result = verification[section].get(cls.replace("::", "_"), {}).get(name, {})
    return result.get("verdict") if result.get("offset") == f"{entry['offset']:#x}" else None


def reflected(curated, verification):
    """Reflected properties as (namespace, name, value, note, type), checked against curated values.

    Exact decodes are kept unless the live check failed them; heuristic decodes are
    included only when the live check passed them."""
    result = reflect(MachO(str(CLIENT)))
    exact = result["exact"]
    dropped = [(cls, name) for cls, props in exact.items() for name in props
               if verdict(verification, "exact", cls, name, props[name]) == "fail"]
    promoted = {(cls, name): entry for cls, props in result["heuristic"].items() for name, entry in props.items()
                if verdict(verification, "heuristic", cls, name, entry) == "pass"}
    known = {(namespace, name): value for namespace, name, value in curated}
    for cls, name in CROSS_CHECKS:
        entry = exact.get(cls, {}).get(name)
        if entry is None or entry["offset"] != known.get((cls, name)):
            raise RuntimeError(f"reflection disagrees with the confirmed {cls}.{name} "
                               f"({entry and hex(entry['offset'])} vs {hex(known.get((cls, name), 0))}); not exporting")
    rows = {(cls, name): (entry, None) for cls, props in exact.items() for name, entry in props.items()
            if (cls, name) not in dropped}
    rows.update({key: (entry, "heuristic decode, passed live check") for key, entry in promoted.items()})
    entries = []
    for cls, name in sorted(rows):
        entry, note = rows[(cls, name)]
        namespace = cls.replace("::", "_")
        if (namespace, name) in known:
            continue
        if "then" in entry:
            note = "; ".join(filter(None, (f"at *(object + {entry['offset']:#x}) + this", note)))
            entries.append((namespace, name, entry["then"], note, entry["type"]))
        else:
            entries.append((namespace, name, entry["offset"], note, entry["type"]))
    result["dropped"], result["promoted"] = dropped, list(promoted)
    return entries, result


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
    curated = list(entries)
    version = offsets.get("version") or profile.name
    verification = load_verification(offsets["evidence"]["static_geometry_accessors"]["binary_sha256"],
                                      DUMPS / version)
    reflected_entries, reflection = reflected([(namespace, name, value) for namespace, name, value in curated],
                                              verification)
    entries = [(namespace, name, value, NOTES.get((namespace, name)), None) for namespace, name, value in curated]
    entries += reflected_entries
    meta = {
        "platform": "macOS ARM64 (Apple Silicon)",
        "roblox_version": offsets.get("version") or profile.name,
        "binary_sha256": offsets["evidence"]["static_geometry_accessors"]["binary_sha256"],
        "dumped_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "dumper": "WeirdExt export_offsets.py",
        "total": len(entries),
        "confirmed_live": len(curated),
        "reflected": len(reflected_entries),
        "dropped_by_live_check": len(reflection["dropped"]),
        "promoted_by_live_check": len(reflection["promoted"]),
    }
    promoted = set(reflection["promoted"])
    unverified = {cls.replace("::", "_"): {name: {"offset": f"{entry['offset']:#x}", "type": entry["type"]}
                                          for name, entry in sorted(props.items()) if (cls, name) not in promoted}
                  for cls, props in sorted(reflection["heuristic"].items())}
    return meta, entries, unverified


def grouped(entries):
    groups: dict[str, list[tuple[str, int, str | None]]] = {}
    for namespace, name, value, note, value_type in entries:
        comment = "; ".join(part for part in (value_type, note) if part)
        groups.setdefault(namespace, []).append((name, value, comment or None))
    return groups


def banner(meta, comment):
    lines = ["WeirdExt offsets — macOS ARM64", "",
             f"Roblox Version  : {meta['roblox_version']}",
             f"Binary SHA-256  : {meta['binary_sha256']}",
             f"Dumped At       : {meta['dumped_at']}",
             f"Total Offsets   : {meta['total']} ({meta['confirmed_live']} confirmed live, "
             f"{meta['reflected']} from reflection)",
             "", "macOS layouts differ from Windows; use these with the macOS client only."]
    return "\n".join(f"{comment} {line}".rstrip() for line in lines)


def render_hpp(meta, groups):
    out = ["#pragma once", banner(meta, "//"), "", "#include <cstdint>", "", "namespace Offsets {"]
    for namespace, items in groups.items():
        out.append(f"    namespace {namespace} {{")
        for name, value, note in items:
            out.append(f"        inline constexpr uintptr_t {name} = {value:#x};" + (f"  // {note}" if note else ""))
        out.append("    }")
    out.append("}")
    return "\n".join(out) + "\n"


def render_cs(meta, groups):
    out = [banner(meta, "//"), "", "namespace Offsets", "{"]
    for namespace, items in groups.items():
        out.append(f"    public static class {namespace}")
        out.append("    {")
        for name, value, note in items:
            out.append(f"        public const long {name} = {value:#x};" + (f"  // {note}" if note else ""))
        out.append("    }")
    out.append("}")
    return "\n".join(out) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--profile", type=Path, help=f"profile directory under {PROFILES}")
    args = parser.parse_args(argv)
    profile = args.profile or select_profile()
    meta, entries, unverified = collect(profile)
    groups = grouped(entries)
    directory = DUMPS / meta["roblox_version"]
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "offsets.hpp").write_text(render_hpp(meta, groups), encoding="utf-8")
    (directory / "offsets.cs").write_text(render_cs(meta, groups), encoding="utf-8")
    write_json(directory / "offsets.json", {"meta": meta, "offsets": {
        namespace: {name: f"{value:#x}" for name, value, _ in items} for namespace, items in groups.items()}})
    write_json(directory / "unverified.json", {"meta": {**meta, "note": "heuristic getter decodes; confirm live "
                                                         "before use"}, "offsets": unverified})
    print(f"[export] {meta['total']} offsets ({meta['confirmed_live']} confirmed live, {meta['reflected']} reflected) "
          f"in {len(groups)} namespaces for {meta['roblox_version']} -> {directory.relative_to(ROOT)}/")
    print(f"[export] live check: {meta['dropped_by_live_check']} reflected offsets dropped, "
          f"{meta['promoted_by_live_check']} heuristic ones promoted")
    print(f"[export] {sum(map(len, unverified.values()))} heuristic decodes -> unverified.json")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print(f"[export] {exc}", file=sys.stderr)
        raise SystemExit(1)
