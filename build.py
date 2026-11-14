#!/usr/bin/env python3
"""Validate and compile WeirdExt's macOS ARM64 helpers without attaching to a game."""
from __future__ import annotations

import argparse
import platform
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
PROFILE = ROOT / "profiles" / "0.745.0.7451137"


def run(command):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout or f"command failed: {command[0]}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="syntax/type/profile checks only; do not build binaries")
    args = parser.parse_args(argv)
    try:
        if platform.system() != "Darwin" or platform.machine() != "arm64":
            raise RuntimeError("WeirdExt requires native ARM64 macOS; do not use a Rosetta Python")
        if sys.version_info < (3, 11):
            raise RuntimeError("Python 3.11 or newer is required; Python 3.14 is recommended")
        swift, clang = shutil.which("swiftc"), shutil.which("clang")
        if swift is None or clang is None:
            raise RuntimeError("install Xcode Command Line Tools with: xcode-select --install")

        scripts = [ROOT / name for name in (
            "main.py", "build.py", "dump_offsets.py", "inspect_camera_accessors.py",
            "inspect_geometry_accessors.py", "inspect_movement_accessors.py", "inspect_physics_accessors.py")]
        scripts += list((ROOT / "dumper").glob("*.py"))
        scripts += [path for path in (ROOT / "rbxl").glob("*.py")
                    if path.name not in ("state.py", "offsets.py")]
        for script in scripts:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        run([swift, "-swift-version", "5", "-typecheck", str(ROOT / "rbxl" / "esp_overlay.swift")])
        run([clang, "-Wall", "-Wextra", "-fsyntax-only", str(ROOT / "dumper" / "sweepc.c")])

        from rbxl.esp_reader import OffsetSpec
        from rbxl.movement import MovementSpec
        from rbxl.physics_control import PhysicsSpec

        spec = OffsetSpec.from_report(PROFILE / "offsets.json").with_camera_evidence(PROFILE / "camera.json")
        MovementSpec.from_evidence(PROFILE / "movement.json", spec.binary_sha256)
        PhysicsSpec.from_evidence(PROFILE / "physics.json", spec.binary_sha256)
        print(f"[build] {len(scripts)} Python sources, Swift types, C syntax and runtime profile validated")
        if args.check:
            return 0

        from rbxl.native_build import build_helper
        from dumper.scan import ensure_tool

        overlay = build_helper(swift, ROOT / "rbxl" / "esp_overlay.swift")
        sweeper = ensure_tool()
        if sweeper is None:
            raise RuntimeError("C sweeper compilation failed; check your Clang installation")
        print(f"[build] overlay: {overlay}")
        print(f"[build] sweeper: {sweeper}")
        print("[build] complete; no game was opened, attached to or modified")
        return 0
    except (OSError, RuntimeError, ValueError, KeyError, SyntaxError, subprocess.SubprocessError) as exc:
        print(f"[build] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
