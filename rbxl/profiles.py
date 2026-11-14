"""Select the runtime profile whose binary identity matches the installed client."""
import hashlib
import json
from pathlib import Path

PROFILES = Path(__file__).resolve().parent.parent / "profiles"
CLIENT = Path("/Applications/Roblox.app/Contents/MacOS/RobloxPlayer")


def binary_sha256(path: Path = CLIENT) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def profile_sha256(directory: Path) -> str | None:
    try:
        report = json.loads((directory / "offsets.json").read_text(encoding="utf-8"))
        return report["evidence"]["static_geometry_accessors"]["binary_sha256"]
    except (OSError, ValueError, KeyError, TypeError):
        return None


def select_profile(client: Path = CLIENT) -> Path:
    digest = binary_sha256(client)
    for directory in sorted(PROFILES.iterdir()):
        if directory.is_dir() and profile_sha256(directory) == digest:
            return directory
    raise RuntimeError(f"no profile matches the installed Roblox (sha256 {digest[:16]}…); "
                       "build one with: sudo .venv/bin/python update_profile.py")
