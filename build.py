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
        clang = shutil.which("clang")
        if clang is None:
            raise RuntimeError("install Xcode Command Line Tools with: xcode-select --install")

        scripts = [ROOT / name for name in (
            "main.py", "build.py", "dump_offsets.py", "update_profile.py", "export_offsets.py", "probe_offsets.py",
            "probe_jump_velocity.py", "inspect_camera_accessors.py", "inspect_geometry_accessors.py",
            "inspect_movement_accessors.py", "inspect_physics_accessors.py")]
        scripts += list((ROOT / "dumper").glob("*.py"))
        scripts += [path for path in (ROOT / "rbxl").glob("*.py")
                    if path.name not in ("state.py", "offsets.py")]
        for script in scripts:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        from rbxl.native_build import build_overlay, check_overlay

        check_overlay()
        run([clang, "-Wall", "-Wextra", "-fsyntax-only", str(ROOT / "dumper" / "sweepc.c")])

        from rbxl.esp_reader import OffsetSpec
        from rbxl.movement import MovementSpec
        from rbxl.physics_control import PhysicsSpec

        profiles = sorted(path for path in (ROOT / "profiles").iterdir() if path.is_dir())
        for profile in profiles:
            spec = OffsetSpec.from_report(profile / "offsets.json").with_camera_evidence(profile / "camera.json")
            MovementSpec.from_evidence(profile / "movement.json", spec.binary_sha256)
            PhysicsSpec.from_evidence(profile / "physics.json", spec.binary_sha256)
        print(f"[build] {len(scripts)} Python sources, overlay types, C syntax and "
              f"{len(profiles)} runtime profile(s) validated")
        if args.check:
            return 0

        from dumper.scan import ensure_tool

        overlay = build_overlay()
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
