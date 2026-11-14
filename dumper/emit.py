"""dumper.emit — write a fresh offsets.py from what the solver actually proved."""

from __future__ import annotations

import datetime
import importlib.util
import inspect
import json


def load_seed_table(path: str) -> tuple[list[tuple[str, str, int]], str]:
    """Read the previous dump so its class/attribute order is preserved."""
    spec = importlib.util.spec_from_file_location("_seed_offsets", path)
    if spec is None or spec.loader is None:
        return [], "unknown"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = getattr(module, "Offsets", None)
    if root is None:
        return [], "unknown"

    order: list[tuple[str, str, int]] = []
    for class_name, cls in inspect.getmembers(root, inspect.isclass):
        for attr, value in inspect.getmembers(cls):
            if attr.startswith("_"):
                continue
            if isinstance(value, int):
                order.append((class_name, attr, value))
    version = getattr(root, "ROBLOX_VERSION", "unknown")
    return order, version


def client_version(binary_path: str) -> str:
    import os
    import plistlib

    contents = os.path.dirname(os.path.dirname(binary_path))
    plist_path = os.path.join(contents, "Info.plist")
    if os.path.exists(plist_path):
        try:
            with open(plist_path, "rb") as handle:
                data = plistlib.load(handle)
            return str(data.get("CFBundleShortVersionString", "unknown"))
        except (OSError, ValueError):
            pass
    return "unknown (live build)"


def render(
    findings: dict,
    seed: list[tuple[str, str, int]] | None,
    version: str,
    module_base: int,
    notes: list[str],
    stale_ok: bool = True,
) -> str:
    seed = seed or []
    classes: dict[str, dict[str, int]] = {}
    order: list[str] = []
    for class_name, attr, value in seed:
        classes.setdefault(class_name, {})[attr] = value
        if class_name not in order:
            order.append(class_name)

    derived: dict[str, dict[str, tuple[int, float]]] = {}
    for path, finding in findings.items():
        class_name, _, attr = path.partition(".")
        derived.setdefault(class_name, {})[attr] = (finding.value, finding.confidence)

    for class_name, attrs in derived.items():
        if class_name not in order:
            order.append(class_name)
        for attr in attrs:
            classes.setdefault(class_name, {}).setdefault(attr, attrs[attr][0])

    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Dumped by rbxl offset dumper (macOS live solver)",
        f"# Roblox Version: {version}",
        "# Architecture: arm64",
        f"# Module base during dump: {module_base:#x}",
        f"# Generated: {stamp}",
        f"# Fields resolved: {len(findings)}",
        "",
        "class Offsets:",
        f'    ROBLOX_VERSION = "{version}"',
        '    ARCHITECTURE = "arm64"',
        "",
    ]

    resolved = 0
    stale = 0
    for class_name in order:
        attrs = classes.get(class_name, {})
        if not attrs:
            continue
        if not stale_ok and not derived.get(class_name):
            continue
        lines.append(f"    class {class_name}:")
        for attr in sorted(attrs):
            value = attrs[attr]
            live = derived.get(class_name, {}).get(attr)
            if live is not None:
                value = live[0]
                resolved += 1
                mark = f"  # candidate: heuristic confidence {live[1]:.2f}"
            elif stale_ok:
                stale += 1
                mark = "  # stale: carried over, not re-proved on this build"
            else:
                continue
            lines.append(f"        {attr} = {value}{mark}")
        lines.append("")

    lines.append(f"# resolved: {resolved}  stale: {stale}")
    lines.append("")
    return "\n".join(lines)


def write_report(path: str, findings: dict, notes: list[str], module_base: int, version: str,
                 evidence: dict | None = None):
    payload = {
        "version": version,
        "module_base": module_base,
        "resolved": {
            path: {
                "value": finding.value,
                "method": finding.method,
                "confidence": finding.confidence,
            }
            for path, finding in findings.items()
        },
        "notes": notes,
        "evidence": evidence or {},
    }
    with open(path, "x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
