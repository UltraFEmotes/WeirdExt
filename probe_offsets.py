#!/usr/bin/env python3
"""Find Player.Team and Humanoid.Health/MaxHealth live and record them in the matching profile.

    sudo .venv/bin/python probe_offsets.py team     # join a game that has teams
    sudo .venv/bin/python probe_offsets.py health   # you will be asked to take damage

Both are optional profile fields: team colors / team check and health bars stay
off until they are recorded. A field is written only when exactly one offset
survives every check.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys

from rbxl.esp_reader import ESPReader, OffsetSpec
from rbxl.memory import MemoryFault, find_roblox_pid
from rbxl.profiles import select_profile

WINDOW = 0x800
MAX_ROUNDS = 6


def attach():
    pid = find_roblox_pid()
    if pid is None:
        raise RuntimeError("Roblox is not running")
    profile = select_profile()
    spec = OffsetSpec.from_report(profile / "offsets.json").with_camera_evidence(profile / "camera.json")
    reader = ESPReader.attach(pid, spec)
    local = reader.pointer(reader.players + spec.local_player)
    if reader.klass(local) != "RBX::Player":
        raise RuntimeError("local player not found")
    return profile, reader, local


def record(profile, fields, method):
    path = profile / "offsets.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    for name, value in fields.items():
        report["resolved"][name] = {"value": value, "method": method, "confidence": 1.0}
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"[probe] recorded {', '.join(f'{name} = {value:#x}' for name, value in fields.items())} in {path}")


def roster(reader):
    return [player for player in reader.children(reader.players, 128) if reader.klass(player) == "RBX::Player"]


def probe_team(profile, reader, local):
    players = roster(reader)
    window = reader.mem.read(local, WINDOW)
    candidates = []
    for offset in range(0, WINDOW, 8):
        team = struct.unpack_from("<Q", window, offset)[0]
        if reader.klass(team) != "RBX::Team" or reader.klass(reader.pointer(team + reader.spec.parent)) != "RBX::Teams":
            continue
        # Every player's slot must hold nothing or a Team.
        slots = [reader.pointer(player + offset) for player in players]
        if all(slot == 0 or reader.klass(slot) == "RBX::Team" for slot in slots):
            candidates.append(offset)
    print(f"[probe] Player.Team candidates: {[hex(offset) for offset in candidates]} across {len(players)} players")
    if len(candidates) != 1:
        raise RuntimeError("Player.Team is not unique; join a game with teams (and you on one) and retry")
    record(profile, {"Player.Team": candidates[0]}, "live probe: only Player slot pointing at a Team under Teams")


def humanoid_of(reader, player):
    character = reader.pointer(player + reader.spec.character)
    for child in reader.children(character, 128):
        if reader.klass(child) == "RBX::Humanoid":
            return child
    raise RuntimeError("your character has no Humanoid yet; wait until you spawn")


def floats(reader, address):
    return struct.unpack(f"<{WINDOW // 4}f", reader.mem.read(address, WINDOW))


def probe_health(profile, reader, local):
    humanoid = humanoid_of(reader, local)
    full = floats(reader, humanoid)
    # Health and MaxHealth are equal at full health; MaxHealth never moves with damage.
    pairs = [(h * 4, m * 4) for h, health in enumerate(full) if 0 < health <= 1e6
             for m, maximum in enumerate(full) if m != h and maximum == health]
    previous = full
    for round_number in range(1, MAX_ROUNDS + 1):
        input(f"[probe] round {round_number}: take some damage (fall, get hit), then press Enter… ")
        humanoid = humanoid_of(reader, local)  # respawns replace the Humanoid
        current = floats(reader, humanoid)
        pairs = [(h, m) for h, m in pairs
                 if current[h // 4] != previous[h // 4] and 0 <= current[h // 4] <= current[m // 4]
                 and current[m // 4] == full[m // 4]]
        previous = current
        print(f"[probe] {len(pairs)} Health/MaxHealth pairs remain")
        if len({h for h, _ in pairs}) == 1 and len(pairs) >= 1:
            break
    healths = {h for h, _ in pairs}
    if len(healths) != 1:
        raise RuntimeError("Humanoid.Health is not unique; retry and take damage each round")
    health = healths.pop()
    # Several MaxHealth candidates can share the value; prefer the nearest field after Health.
    maximum = min((m for h, m in pairs), key=lambda m: (m < health, abs(m - health)))
    for player in roster(reader):
        try:
            other = floats(reader, humanoid_of(reader, player))
        except (RuntimeError, MemoryFault):
            continue
        if not 0 <= other[health // 4] <= other[maximum // 4]:
            raise RuntimeError(f"another player's Health/MaxHealth at {health:#x}/{maximum:#x} is inconsistent")
    record(profile, {"Humanoid.Health": health, "Humanoid.MaxHealth": maximum},
           "live probe: field that tracked damage while its MaxHealth sibling stayed fixed")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("field", choices=("team", "health"))
    args = parser.parse_args(argv)
    profile, reader, local = attach()
    try:
        (probe_team if args.field == "team" else probe_health)(profile, reader, local)
    finally:
        reader.close()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, MemoryFault, OSError) as exc:
        print(f"[probe] {exc}", file=sys.stderr)
        raise SystemExit(1)
