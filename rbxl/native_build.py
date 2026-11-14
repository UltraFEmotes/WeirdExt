"""Content-addressed native app builds so Accessibility identity survives reruns."""
import hashlib
import json
import os
from pathlib import Path
import plistlib
import subprocess
import tempfile


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


def build_helper(compiler: str, source: Path):
    version = subprocess.run([compiler, "--version"], capture_output=True, text=True, timeout=15, check=True)
    source_hash = hashlib.sha256(source.read_bytes() + version.stdout.encode() + b"swift5-O-app-v1").hexdigest()
    cache = source.parent.parent / ".weirdext-native"
    cache.mkdir(mode=0o755, parents=True, exist_ok=True)
    destination = cache / source_hash[:20]
    if destination.exists():
        return _verified_executable(destination, source_hash)
    print("[esp] building WeirdExt.app", flush=True)
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
        result = subprocess.run([compiler, "-swift-version", "5", "-O", str(source), "-o", str(binary)],
                                capture_output=True, text=True, timeout=120)
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
