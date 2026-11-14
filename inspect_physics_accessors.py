#!/usr/bin/env python3
"""Offline collision and assembly-PV evidence; never opens a process."""
import argparse
import json

from dumper.macho import MachO
from dumper.physics_accessors import inspect_physics_accessors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", nargs="?", default="/Applications/Roblox.app/Contents/MacOS/RobloxPlayer")
    parser.add_argument("--json", help="new output path (never overwritten)")
    args = parser.parse_args(argv)
    report = inspect_physics_accessors(MachO(args.binary))
    print(json.dumps(report, indent=2))
    if len(report["selected"]) != 9:
        return 1
    if args.json:
        with open(args.json, "x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
