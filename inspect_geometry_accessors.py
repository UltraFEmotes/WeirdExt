#!/usr/bin/env python3
"""Corroborate geometry offsets from an installed Mach-O; no live attach."""
import argparse
import json

from dumper.arm64_accessors import inspect_geometry_accessors
from dumper.macho import MachO


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", nargs="?", default="/Applications/Roblox.app/Contents/MacOS/RobloxPlayer")
    parser.add_argument("--json", help="new output path for instruction-level evidence")
    args = parser.parse_args(argv)
    report = inspect_geometry_accessors(MachO(args.binary))
    print(f"binary sha256: {report['binary_sha256']}")
    chosen = report["selected"]
    if chosen is None:
        print(f"no unique supported getter chain ({len(report['candidates'])} matches)")
        return 1
    print(f"descriptor: {chosen['descriptor_rtti']['mangled']}")
    for key in ("registration", "property_getter", "part_getter", "primitive_getter", "update_helper"):
        print(f"{key}: {chosen[key]:#x}")
    for key in ("basepart_primitive_offset", "primitive_cframe_offset", "primitive_position_offset"):
        print(f"{key}: {chosen[key]:#x}")
    for limitation in report["limitations"]:
        print(f"! {limitation}")
    if args.json:
        with open(args.json, "x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
