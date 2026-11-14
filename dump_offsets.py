#!/usr/bin/env python3
"""dump_offsets.py — re-derive the Roblox macOS offset table from a live client.

    sudo python3 dump_offsets.py --out offsets.py --seed rbxl/offsets.py -v

The solver never trusts a number from the seed. It locates the heap, finds the
service name strings, solves the Instance layout from child-vector structure,
then walks DataModel -> Workspace -> World -> Primitives -> Camera -> Players and
estimates fields against invariants. Findings remain unvalidated candidates;
unresolved seed values are not included in the emitted table.
"""

from __future__ import annotations

import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dumper.derive import Deriver  # noqa: E402
from dumper.emit import client_version, load_seed_table, render, write_report  # noqa: E402
from rbxl.memory import MachProcess, MemoryFault, find_roblox_pid  # noqa: E402


def client_binary(mem) -> str:
    for start, _size, path, _prot in mem.regions():
        if path and path.rsplit("/", 1)[-1].startswith("RobloxPlayer"):
            del start
            return path
    return ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Roblox macOS live offset dumper")
    parser.add_argument("--pid", type=int, default=None, help="client pid (auto-detected)")
    parser.add_argument("--out", default="offsets_derived.py", help="offset file to write")
    parser.add_argument("--json", default=None, help="optional JSON evidence report")
    parser.add_argument("--seed", default=None, help="previous offsets.py, used only for output ordering")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--skip-renderer", action="store_true",
                        help="omit VisualEngine/FakeDataModel discovery")
    parser.add_argument("--renderer-budget", type=float, default=15.0,
                        help="renderer scan budget in seconds (default: 15; checked between reads)")
    args = parser.parse_args(argv)
    if not math.isfinite(args.renderer_budget) or args.renderer_budget <= 0:
        parser.error("--renderer-budget must be finite and positive")

    for path in (args.out, args.json):
        if path and os.path.exists(path):
            print(f"output already exists; choose a new path: {path}", file=sys.stderr)
            return 2

    pid = args.pid or find_roblox_pid()
    if not pid:
        print("no Roblox client running (RobloxPlayer not in the process table)", file=sys.stderr)
        return 2

    try:
        mem = MachProcess(pid)
    except MemoryFault as exc:
        print(f"attach failed: {exc}", file=sys.stderr)
        return 3

    print(f"attached to pid {pid}")
    regions = list(mem.regions())
    binary = client_binary(mem)
    version = client_version(binary) if binary else "unknown (live build)"
    print(f"client {binary or '<unknown>'}  version {version}")

    deriver = Deriver(mem, regions, verbose=args.verbose,
                      renderer_budget=args.renderer_budget, skip_renderer=args.skip_renderer)
    try:
        report = deriver.run()
    except Exception as exc:  # noqa: BLE001 - surfaced to the operator verbatim
        print(f"derivation stopped: {exc}", file=sys.stderr)
        return 4

    seed: list[tuple[str, str, int]] = []
    if args.seed and os.path.exists(args.seed):
        seed, _ = load_seed_table(args.seed)

    text = render(report.findings, seed, version, report.module_base, report.notes, stale_ok=False)
    with open(args.out, "x", encoding="utf-8") as handle:
        handle.write(text)
    if args.json:
        write_report(args.json, report.findings, report.notes, report.module_base, version,
                      evidence=report.evidence)

    print(f"\n{len(report.findings)} heuristic candidates (not independently validated):")
    for path in sorted(report.findings, key=lambda p: (-report.findings[p].confidence, p)):
        finding = report.findings[path]
        print(f"  {path:<38} {finding.value:<8} {finding.confidence:>4.0%}  {finding.method}")
    for note in report.notes:
        print(f"  ! {note}")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
