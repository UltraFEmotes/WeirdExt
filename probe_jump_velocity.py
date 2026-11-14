#!/usr/bin/env python3
"""Find which in-memory velocity copy Roblox's solver actually integrates from.

The known Primitive PV pair is overwritten one physics step after a mid-air
write, so it is an output mirror. This probe, run while your character falls:
  1. walks pointers out of the root Primitive and its assembly (two levels)
     and finds float/double triples that equal the live velocity, skipping
     other body parts' Primitive PV pairs;
  2. writes +50 into each candidate's Y during a fall and calls it a hit only
     if the mirror's Y follows to about +40 (50 minus 50 ms of gravity);
  3. retests hits twice, because a landing also flips velocity upward;
  4. records a unique one-hop float hit as the profile's physics "solver" entry.

    sudo .venv/bin/python probe_jump_velocity.py

Jump off something tall (or keep jumping) while it runs.
"""
from __future__ import annotations

from collections import deque
import json
import math
import struct
import sys
import time

from rbxl.esp_reader import ESPReader, OffsetSpec
from rbxl.memory import MemoryFault, find_roblox_pid
from rbxl.movement import MachFieldWriter
from rbxl.physics_control import PhysicsController, PhysicsSpec
from rbxl.profiles import select_profile
from dumper import prims

FALLING = -8.0            # studs/s; below this the Humanoid is airborne
STEP_TOLERANCE = 3.5      # Y may lag the mirror by one 60 Hz gravity step
AXIS_TOLERANCE = 0.75
ANCHOR_WINDOW = 0x1000    # bytes either side of the root Primitive and assembly
OBJECT_WINDOW = 0x800     # bytes scanned from each followed pointer
POINTER_SPAN = 0x400      # header bytes searched for pointers to follow
MAX_DEPTH = 2
MAX_OBJECTS = 400
MAX_TESTS = 80
BOOST = 50.0
SETTLE = 0.05
HIT_FLOOR = 15.0          # a real hit reads ~+40; landings read ~0..+10
CONFIRMATIONS = 2
FORMATS = (("f", 4), ("d", 8))


def velocity(controller):
    root = controller.root_part.primitive
    return struct.unpack("<3f", controller.reader.mem.read(root + controller.spec.velocity, 12))


def wait_for_fall(controller, label):
    print(f"[probe] {label}: jump now (waiting for velocity.y < {FALLING:g})", flush=True)
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        current = velocity(controller)
        if current[1] < FALLING:
            return current
        time.sleep(0.005)
    raise RuntimeError("no fall observed within 60 s")


def objects(controller):
    """Breadth-first pointer walk from the root Primitive and its assembly."""
    reader, spec = controller.reader, controller.spec
    primitive = controller.root_part.primitive
    seeds = [("primitive", primitive, -ANCHOR_WINDOW, 2 * ANCHOR_WINDOW)]
    assembly_ref = reader.pointer(primitive + spec.primitive_assembly)
    if assembly_ref:
        seeds.append(("assembly", assembly_ref - spec.assembly_adjustment, -ANCHOR_WINDOW, 2 * ANCHOR_WINDOW))
    # path = (seed label, pointer offsets...) from the seed to this object
    found = {base: (label, low, size, (label,)) for label, base, low, size in seeds}
    queue = deque((base, label, (label,)) for label, base, _, _ in seeds)
    while queue and len(found) < MAX_OBJECTS:
        base, label, path = queue.popleft()
        if len(path) > MAX_DEPTH:
            continue
        try:
            header = reader.mem.read(base, POINTER_SPAN)
        except MemoryFault:
            continue
        for offset in range(0, POINTER_SPAN, 8):
            pointer = prims.q(header, offset)
            if not prims.plausible_ptr(pointer) or pointer in found:
                continue
            child = f"{label}+{offset:#x}->"
            found[pointer] = (child, 0, OBJECT_WINDOW, path + (offset,))
            queue.append((pointer, child, path + (offset,)))
    return found


def is_part_pv(controller, address):
    reader, spec = controller.reader, controller.spec
    return any(reader.klass(address - field) == "RBX::Primitive"
               for field in (spec.velocity, spec.velocity_mirror))


def candidates(controller, live):
    mem = controller.reader.mem
    result = {}
    for base, (label, low, size, path) in objects(controller).items():
        try:
            raw = mem.read(base + low, size)
        except MemoryFault:
            continue
        for code, width in FORMATS:
            for offset in range(0, len(raw) - 3 * width + 1, width):
                values = struct.unpack_from(f"<3{code}", raw, offset)
                if not all(math.isfinite(v) for v in values):
                    continue
                if (abs(values[1] - live[1]) <= STEP_TOLERANCE and abs(values[0] - live[0]) <= AXIS_TOLERANCE
                        and abs(values[2] - live[2]) <= AXIS_TOLERANCE and abs(live[1]) > 1):
                    address = base + low + offset
                    if address not in result and not is_part_pv(controller, address):
                        result[address] = (f"{label} {low + offset:+#x} ({'float' if code == 'f' else 'double'})",
                                           code, width, path, low + offset)
    return result


def trial(controller, writer, address, code, width, label):
    before = wait_for_fall(controller, f"test {label}")
    payload = struct.pack(f"<{code}", BOOST)
    if width == 8:
        # MachFieldWriter only takes 1- or 4-byte writes; a double is two halves.
        writer.write(address + 8, payload[:4])
        writer.write(address + 12, payload[4:])
    else:
        writer.write(address + 4, payload)
    time.sleep(SETTLE)
    after = velocity(controller)
    hit = after[1] > HIT_FLOOR
    print(f"[probe]   mirror.y {before[1]:.2f} -> {after[1]:.2f} after {SETTLE * 1000:.0f} ms"
          f"{'  <-- follows' if hit else ''}", flush=True)
    return hit


def main():
    pid = find_roblox_pid()
    if pid is None:
        raise RuntimeError("Roblox is not running")
    profile = select_profile()
    spec = OffsetSpec.from_report(profile / "offsets.json").with_camera_evidence(profile / "camera.json")
    reader = ESPReader.attach(pid, spec)
    controller = PhysicsController(reader, PhysicsSpec.from_evidence(profile / "physics.json", spec.binary_sha256))
    controller.character = controller._character()
    if not controller.character:
        raise RuntimeError("local character not found")
    controller._scan(time.monotonic())
    if controller.root_part is None:
        raise RuntimeError("HumanoidRootPart not found")
    writer = MachFieldWriter(reader.mem)
    print(f"[probe] root Primitive {controller.root_part.primitive:#x}", flush=True)

    live = wait_for_fall(controller, "scan")
    found = candidates(controller, live)
    print(f"[probe] live velocity {live[0]:.2f}, {live[1]:.2f}, {live[2]:.2f}; "
          f"{len(found)} non-part copies (testing up to {MAX_TESTS})", flush=True)
    for address, (label, *_) in found.items():
        print(f"         {address:#x}  {label}", flush=True)

    confirmed = []
    for address, (label, code, width, path, field) in list(found.items())[:MAX_TESTS]:
        print(f"[probe] {label}", flush=True)
        if not trial(controller, writer, address, code, width, label):
            continue
        if all(trial(controller, writer, address, code, width, f"confirm {label}") for _ in range(CONFIRMATIONS)):
            confirmed.append((label, code, path, field))
    print(f"[probe] confirmed solver copies: {[label for label, *_ in confirmed] or 'none in scanned range'}",
          flush=True)
    reader.close()
    # The runtime reads *(root Primitive + body_pointer) + velocity as floats.
    usable = [(path, field) for _, code, path, field in confirmed
              if code == "f" and len(path) == 2 and path[0] == "primitive"]
    if len(usable) != 1:
        print("[probe] nothing recorded: need exactly one confirmed float one hop from the Primitive", flush=True)
        return 1
    (_, body_pointer), velocity = usable[0]
    path = profile / "physics.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    report["solver"] = {"body_pointer": body_pointer, "velocity": velocity,
                        "evidence": [f"probe_jump_velocity.py: +{BOOST:g} Y write during free fall followed "
                                     f"{1 + CONFIRMATIONS}/{1 + CONFIRMATIONS} times"]}
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"[probe] recorded solver body_pointer {body_pointer:#x}, velocity {velocity:#x} in {path}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, MemoryFault, OSError) as exc:
        print(f"[probe] {exc}", file=sys.stderr)
        raise SystemExit(1)
