"""Content-addressed native app builds so Accessibility identity survives reruns."""
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parent.parent
IMGUI = ROOT / "third_party" / "imgui"
OVERLAY_SOURCES = [ROOT / "rbxl" / "overlay.mm"] + [IMGUI / name for name in (
    "imgui.cpp", "imgui_draw.cpp", "imgui_tables.cpp", "imgui_widgets.cpp",
    "backends/imgui_impl_metal.mm", "backends/imgui_impl_osx.mm")]
COMPILE_FLAGS = ["-std=c++17", "-fobjc-arc", "-I", str(IMGUI), "-I", str(IMGUI / "backends")]
LINK_FLAGS = [flag for framework in ("AppKit", "Metal", "MetalKit", "QuartzCore", "GameController",
                                     "ApplicationServices", "Carbon") for flag in ("-framework", framework)]


def compiler():
    found = shutil.which("clang++")
    if found is None:
        raise RuntimeError("clang++ not found; install Xcode Command Line Tools with: xcode-select --install")
    return found


def check_overlay():
    """Syntax/type check of the overlay source alone; vendored ImGui is not rechecked."""
    result = subprocess.run([compiler(), *COMPILE_FLAGS, "-Wall", "-Wextra", "-fsyntax-only",
                             str(OVERLAY_SOURCES[0])], capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise RuntimeError("overlay check failed:\n" + result.stderr)


def _verified_executable(directory, source_hash):
    executable = directory / "WeirdExt.app" / "Contents" / "MacOS" / "WeirdExt"
    manifest = directory / "build.json"
    try:
        metadata = json.loads(manifest.read_text())
        if (executable.is_symlink() or metadata["source_sha256"] != source_hash
                or hashlib.sha256(executable.read_bytes()).hexdigest() != metadata["binary_sha256"]):
            raise ValueError("build identity mismatch")
    except (OSError, KeyError, ValueError) as exc:
        raise RuntimeError(f"native build cache is incomplete or changed: {directory}") from exc
    return executable


def build_overlay():
    clang = compiler()
    version = subprocess.run([clang, "--version"], capture_output=True, text=True, timeout=15, check=True)
    digest = hashlib.sha256(version.stdout.encode() + " ".join(COMPILE_FLAGS + LINK_FLAGS).encode()
                            + b"imgui-metal-O2-app-v1")
    for source in OVERLAY_SOURCES + sorted(IMGUI.glob("*.h")) + sorted(IMGUI.glob("backends/*.h")):
        digest.update(source.read_bytes())
    source_hash = digest.hexdigest()
    cache = ROOT / ".weirdext-native"
    cache.mkdir(mode=0o755, parents=True, exist_ok=True)
    destination = cache / source_hash[:20]
    if destination.exists():
        return _verified_executable(destination, source_hash)
    print("[esp] building WeirdExt.app (first build compiles Dear ImGui, ~30 s)", flush=True)
    with tempfile.TemporaryDirectory(prefix="build-", dir=cache) as temporary:
        release = Path(temporary) / "release"
        app = release / "WeirdExt.app"
        contents = app / "Contents"
        binary = contents / "MacOS" / "WeirdExt"
        binary.parent.mkdir(mode=0o755, parents=True)
        info = {"CFBundleIdentifier": "dev.weirdext.overlay", "CFBundleExecutable": "WeirdExt",
                "CFBundleName": "WeirdExt", "CFBundlePackageType": "APPL", "CFBundleVersion": "1",
                "CFBundleShortVersionString": "1.0", "LSUIElement": True, "NSHighResolutionCapable": True}
        (contents / "Info.plist").write_bytes(plistlib.dumps(info))
        result = subprocess.run([clang, *COMPILE_FLAGS, "-O2", *map(str, OVERLAY_SOURCES), *LINK_FLAGS,
                                 "-o", str(binary)], capture_output=True, text=True, timeout=300)
        if result.returncode:
            raise RuntimeError("native build failed:\n" + result.stderr)
        os.chmod(binary, 0o755)
        signed = subprocess.run(["/usr/bin/codesign", "--force", "--sign", "-", "--identifier",
                                 "dev.weirdext.overlay", str(app)], capture_output=True, text=True, timeout=30)
        if signed.returncode:
            raise RuntimeError("native app signing failed:\n" + signed.stderr)
        (release / "build.json").write_text(json.dumps({"source_sha256": source_hash,
            "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest()}))
        try:
            os.rename(release, destination)
        except OSError:
            # A concurrent build may have published the same source identity.
            if not destination.exists():
                raise
        return _verified_executable(destination, source_hash)
