"""Select the runtime profile whose binary identity matches the installed client."""
import hashlib
import json
import os
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


def give_back(path: Path):
    """Probes run under sudo; hand files they create back to the user who ran sudo."""
    if os.geteuid() == 0 and os.environ.get("SUDO_UID"):
        os.chown(path, int(os.environ["SUDO_UID"]), int(os.environ["SUDO_GID"]))


def write_json(path: Path, payload, *, exclusive: bool = False):
    with open(path, "x" if exclusive else "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    give_back(path)


def select_profile(client: Path = CLIENT) -> Path:
    digest = binary_sha256(client)
    for directory in sorted(PROFILES.iterdir()):
        if directory.is_dir() and profile_sha256(directory) == digest:
            return directory
    raise RuntimeError(f"no profile matches the installed Roblox (sha256 {digest[:16]}…); "
                       "build one with: sudo .venv/bin/python update_profile.py")
