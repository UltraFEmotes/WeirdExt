#!/usr/bin/env python3
"""Recover Camera CFrame/FOV getters and units offline; preserve existing reports."""
import argparse
import json

from dumper.camera_accessors import inspect_camera_accessors
from dumper.macho import MachO


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", nargs="?", default="/Applications/Roblox.app/Contents/MacOS/RobloxPlayer")
    parser.add_argument("--json", help="new evidence output path (never overwritten)")
    args = parser.parse_args(argv)
    report = inspect_camera_accessors(MachO(args.binary))
    print(json.dumps(report, indent=2))
    if report["selected"] is None:
        return 1
    if args.json:
        with open(args.json, "x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
