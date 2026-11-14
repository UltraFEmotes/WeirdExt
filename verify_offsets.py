#!/usr/bin/env python3
"""Check reflected offsets against a live game, and find identity fields by known value.

    sudo .venv/bin/python verify_offsets.py      # join any game first

1. Samples real instances of every reflected class (and subclasses, via RTTI)
   and reads each property where the dump says it is. A value that cannot be
   that type (a bool that is not 0/1, a non-finite float, a reference that is
   not an Instance, an unreadable string, a CFrame that is not a rotation)
   fails it. Results go to dumps/<version>/verification.json; export_offsets.py
   drops failed reflected offsets and promotes heuristic ones that passed.
2. Finds DataModel PlaceId / JobId (from Roblox's own log), GameId and CreatorId
   (Roblox web API for that place) and Player UserId (web API for your username)
   by searching for those exact values, and records them in the profile.

Plausibility is evidence, not proof: a wrong offset can hold a plausible value.
Read-only: nothing in the game is written.
"""
from __future__ import annotations

from collections import defaultdict, deque
import json
import math
import os
from pathlib import Path
import pwd
import re
import struct
import sys
import urllib.request

from dumper import prims
from dumper.macho import MachO
from dumper.reflection import reflect
from dumper.rtti import simplify
from rbxl.esp_reader import ESPReader, OffsetSpec
from rbxl.memory import MemoryFault, find_roblox_pid
from rbxl.profiles import CLIENT, select_profile, write_json

ROOT = Path(__file__).resolve().parent
SAMPLES_PER_CLASS = 6
MAX_NODES = 30000
MAX_DEPTH = 10
MAX_CHILDREN = 512
WORLD_LIMIT = 1e7
SEARCH_WINDOW = 0x2000
JOIN = re.compile(r"Joining game '([0-9a-fA-F-]{36})' place (\d+)")


# ---- live instance census -----------------------------------------------------------

def ancestors(reader, typeinfo, cache):
    """Class names of a typeinfo and its bases (single and multiple inheritance RTTI)."""
    if typeinfo in cache:
        return cache[typeinfo]
    cache[typeinfo] = set()
    names = set()
    try:
        mangled = reader.model.cstring(reader.mem.u64(typeinfo + 8))
        if mangled:
            names.add(simplify(mangled).removeprefix("RBX::"))
        base = reader.mem.u64(typeinfo + 16)
        if prims.plausible_ptr(base) and reader.model.in_data(base):          # __si_class_type_info
            names |= ancestors(reader, base, cache)
        else:                                                                  # __vmi_class_type_info
            count = struct.unpack("<I", reader.mem.read(typeinfo + 20, 4))[0]
            for index in range(min(count, 16)):
                parent = reader.mem.u64(typeinfo + 24 + 16 * index)
                if prims.plausible_ptr(parent) and reader.model.in_data(parent):
                    names |= ancestors(reader, parent, cache)
    except MemoryFault:
        pass
    cache[typeinfo] = names
    return names


def census(reader):
    """Up to SAMPLES_PER_CLASS live instances for every class name in each instance's ancestry."""
    samples, cache = defaultdict(list), {}
    queue, seen = deque([(reader.root, 0)]), {reader.root}
    while queue and len(seen) < MAX_NODES:
        address, depth = queue.popleft()
        try:
            ref = reader.model.class_of(reader.mem.u64(address))
        except MemoryFault:
            continue
        if ref is not None:
            for name in ancestors(reader, ref.typeinfo, cache):
                if len(samples[name]) < SAMPLES_PER_CLASS:
                    samples[name].append(address)
        if depth < MAX_DEPTH:
            for child in reader.children(address, MAX_CHILDREN):
                if child not in seen:
                    seen.add(child)
                    queue.append((child, depth + 1))
    print(f"[verify] walked {len(seen)} instances; {len(samples)} class names have samples", flush=True)
    return samples


# ---- plausibility per type ------------------------------------------------------------

def _floats(reader, address, count):
    return struct.unpack(f"<{count}f", reader.mem.read(address, 4 * count))


def _float_ok(value):
    """Finite and sane, or infinite (Roblox uses math.huge for e.g. MaxDistance); never NaN."""
    if math.isinf(value):
        return True
    return math.isfinite(value) and abs(value) < WORLD_LIMIT and (value == 0 or abs(value) > 1e-6)


def _string(reader, address):
    raw = reader.mem.read(address, 24)
    if prims.is_long_string(raw):
        target = prims.long_string_target(raw)
        if target is None or not 0 <= target[1] < 4096:
            return None
        text = reader.mem.read(target[0], target[1]) if target[1] else b""
    else:
        text = prims.decode_short_string(raw)
        return text
    try:
        decoded = text.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return decoded if decoded.isprintable() else None


def check(reader, address, kind, value_type):
    """(plausible, informative) for one value, or None when the type cannot be judged."""
    if kind == "reference" or value_type == "Instance":
        pointer = reader.mem.u64(address)
        if pointer == 0:
            return True, False
        return reader.klass(pointer) is not None, True
    if kind == "enum":
        value = struct.unpack("<i", reader.mem.read(address, 4))[0]
        return 0 <= value < 4096, value != 0
    if value_type == "bool":
        value = reader.mem.read(address, 1)[0]
        return value in (0, 1), False
    if value_type == "float":
        value = _floats(reader, address, 1)[0]
        return _float_ok(value), value != 0
    if value_type == "double":
        value = struct.unpack("<d", reader.mem.read(address, 8))[0]
        return math.isfinite(value) and abs(value) < 1e15 and (value == 0 or abs(value) > 1e-12), value != 0
    if value_type in ("Vector3", "Color3", "Vector2"):
        values = _floats(reader, address, 2 if value_type == "Vector2" else 3)
        ok = all(_float_ok(value) for value in values)
        if value_type == "Color3":
            ok = ok and all(-0.01 <= value <= 255.01 for value in values)
        return ok, any(values)
    if value_type == "CoordinateFrame":
        values = _floats(reader, address, 12)
        return prims.orthonormal3(values[:9], tol=0.05) and all(_float_ok(v) for v in values[9:]), True
    if value_type == "string":
        text = _string(reader, address)
        return text is not None, bool(text)
    return None


def verify(reader, table, samples):
    """{namespace: {name: {verdict, samples}}} for every entry of a reflect() table."""
    results = {}
    for cls, props in table.items():
        instances = samples.get(cls, [])
        for name, entry in props.items():
            verdict, tested, informative = "no-sample", 0, False
            for instance in instances:
                try:
                    address = instance + entry["offset"]
                    if "then" in entry:
                        address = reader.mem.u64(address) + entry["then"]
                    outcome = check(reader, address, entry.get("kind"), entry.get("type"))
                except MemoryFault:
                    outcome = (False, False)
                if outcome is None:
                    verdict = "untestable"
                    break
                tested += 1
                informative |= outcome[1]
                if not outcome[0]:
                    verdict = "fail"
                    break
            else:
                if tested:
                    verdict = "pass" if informative else "inconclusive"
            results.setdefault(cls.replace("::", "_"), {})[name] = {"verdict": verdict, "samples": tested,
                                                                     "offset": f"{entry['offset']:#x}"}
    return results


# ---- identity fields by known value ---------------------------------------------------

def console_home():
    user = os.environ.get("SUDO_USER")
    return Path(pwd.getpwnam(user).pw_dir) if user else Path.home()


def current_join():
    logs = sorted((console_home() / "Library/Logs/Roblox").glob("*.log"), key=lambda path: path.stat().st_mtime)
    for path in reversed(logs):
        matches = JOIN.findall(path.read_text(errors="replace"))
        if matches:
            return matches[-1][0], int(matches[-1][1])
    raise RuntimeError("no 'Joining game' line in the Roblox logs; join a game first")


def fetch(url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response)


def find_int64(reader, address, value):
    window = reader.mem.read(address, SEARCH_WINDOW)
    return [offset for offset in range(0, SEARCH_WINDOW - 7, 8) if struct.unpack_from("<q", window, offset)[0] == value]


def find_string(reader, address, text):
    window = reader.mem.read(address, SEARCH_WINDOW)
    return [offset for offset in range(0, SEARCH_WINDOW - 23, 8)
            if (target := prims.long_string_target(window[offset:offset + 24])) and target[1] == len(text)
            and reader.mem.read(target[0], len(text)) == text.encode()]


def identity(reader, profile):
    job, place = current_join()
    universe = fetch(f"https://apis.roblox.com/universes/v1/places/{place}/universe")["universeId"]
    creator = fetch(f"https://games.roblox.com/v1/games?universeIds={universe}")["data"][0]["creator"]["id"]
    local = reader.pointer(reader.players + reader.spec.local_player)
    username = reader.name(local)
    players = {reader.name(player): player for player in reader.children(reader.players, 128)
               if reader.klass(player) == "RBX::Player"}
    lookup = fetch("https://users.roblox.com/v1/usernames/users", {"usernames": list(players)})["data"]
    ids = {row["requestedUsername"]: row["id"] for row in lookup}
    user = ids[username]
    print(f"[verify] place {place}, universe {universe}, creator {creator}, job {job}, you {username} ({user}); "
          f"{len(ids)} players with known ids")
    found = {"DataModel.PlaceId": find_int64(reader, reader.root, place),
             "DataModel.GameId": find_int64(reader, reader.root, universe),
             "DataModel.CreatorId": find_int64(reader, reader.root, creator),
             "DataModel.JobId": find_string(reader, reader.root, job),
             # Your id may sit in several slots; the real field holds every player's own id.
             "Player.UserId": [offset for offset in find_int64(reader, local, user)
                               if all(struct.unpack("<q", reader.mem.read(players[name] + offset, 8))[0] == user_id
                                      for name, user_id in ids.items() if name in players)]}
    path = profile / "offsets.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    for key, offsets in found.items():
        print(f"[verify] {key}: {[hex(offset) for offset in offsets]}")
        if len(offsets) == 1:
            report["resolved"][key] = {"value": offsets[0], "method": "verify_offsets.py: unique match for the "
                                       "live value (Roblox log / web API)", "confidence": 1.0}
    write_json(path, report)


def main():
    pid = find_roblox_pid()
    if pid is None:
        raise RuntimeError("Roblox is not running; join a game first")
    profile = select_profile()
    spec = OffsetSpec.from_report(profile / "offsets.json").with_camera_evidence(profile / "camera.json")
    reader = ESPReader.attach(pid, spec)
    try:
        try:
            identity(reader, profile)
        except (OSError, KeyError, IndexError, ValueError, RuntimeError) as exc:
            print(f"[verify] identity fields skipped: {exc}", flush=True)
        reflection = reflect(MachO(str(CLIENT)))
        samples = census(reader)
        report = {"binary_sha256": spec.binary_sha256,
                  "exact": verify(reader, reflection["exact"], samples),
                  "heuristic": verify(reader, reflection["heuristic"], samples)}
    finally:
        reader.close()
    for section in ("exact", "heuristic"):
        tally = defaultdict(int)
        for props in report[section].values():
            for result in props.values():
                tally[result["verdict"]] += 1
        print(f"[verify] {section}: {dict(tally)}")
    directory = ROOT / "dumps" / (json.loads((profile / "offsets.json").read_text())["version"] or profile.name)
    directory.mkdir(parents=True, exist_ok=True)
    write_json(directory / "verification.json", report)
    print(f"[verify] wrote {directory.relative_to(ROOT)}/verification.json; now run export_offsets.py")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, MemoryFault, OSError, ValueError, KeyError, IndexError) as exc:
        print(f"[verify] {exc}", file=sys.stderr)
        raise SystemExit(1)
