"""Opt-in local-Humanoid writes backed by same-binary offline evidence.

Writes are separate Mach operations, not an atomic transaction. Readback and
conditional best-effort rollback detect failures; server acceptance is unknown.
"""
from __future__ import annotations

import contextlib
import ctypes
from dataclasses import dataclass
import json
import math
from pathlib import Path
import struct

from .memory import MemoryFault, _lib, is_plausible_pointer

_lib.mach_vm_write.argtypes = [ctypes.c_uint, ctypes.c_uint64, ctypes.c_void_p, ctypes.c_uint32]
_lib.mach_vm_write.restype = ctypes.c_int


@dataclass(frozen=True)
class MovementSpec:
    walk_speed: int
    walk_speed_check: int
    jump_power: int
    use_jump_power: int

    @classmethod
    def from_evidence(cls, path: Path, binary_sha256: str):
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("binary_sha256") != binary_sha256:
            raise ValueError("movement evidence belongs to a different binary")
        selected = report.get("selected", {})
        keys = ("WalkSpeed", "WalkSpeedCheck", "JumpPower", "UseJumpPower")
        for key in keys:
            offset = selected.get(key)
            rows = report.get("candidates", {}).get(key, [])
            if (type(offset) is not int or not 0 <= offset <= 0x10000 or not rows
                    or any(row.get("offset") != offset for row in rows)):
                raise ValueError(f"movement evidence missing or ambiguous: {key}")
            if key != "UseJumpPower" and offset % 4:
                raise ValueError(f"unaligned movement field: {key}")
        occupied = [set(range(selected[key], selected[key] + (1 if key == "UseJumpPower" else 4))) for key in keys]
        if any(left & right for index, left in enumerate(occupied) for right in occupied[index + 1:]):
            raise ValueError("movement fields overlap")
        return cls(*(selected[key] for key in keys))


class MachFieldWriter:
    """Uses the already-owned task port; never opens another process or changes protection."""
    def __init__(self, mem):
        self.mem = mem

    allowed_sizes = (1, 4)

    def write(self, address, payload):
        if len(payload) not in self.allowed_sizes or not is_plausible_pointer(address):
            raise ValueError("unsupported write size or invalid address")
        buffer = ctypes.create_string_buffer(payload)
        result = _lib.mach_vm_write(self.mem.task, address, ctypes.addressof(buffer), len(payload))
        if result:
            raise MemoryFault(f"mach_vm_write failed at {address:#x}: kernel code {result}")
        if self.mem.read(address, len(payload)) != payload:
            raise MemoryFault(f"movement write readback mismatch at {address:#x}")


class MachRotationWriter(MachFieldWriter):
    """Exactly nine float32 rotation values; translation is never included."""
    allowed_sizes = (36,)


class MachVectorWriter(MachFieldWriter):
    """Exactly three float32 values: one velocity vector."""
    allowed_sizes = (12,)


class MachPointerWriter(MachFieldWriter):
    """One 8-byte count or a 16-byte (object, control block) smart-pointer pair."""
    allowed_sizes = (8, 16)


class MovementController:
    """Single polling-thread owner. Disabled by default; no pose or task-port discovery."""
    def __init__(self, reader, spec: MovementSpec, writer=None):
        self.reader, self.spec = reader, spec
        self.writer = writer or MachFieldWriter(reader.mem)
        self.humanoid = 0
        self.character = 0
        self.resolved_character = 0
        self.patches = {}
        self.failed = False
        self.status = "Off"

    def _resolve(self):
        reader = self.reader
        try:
            if (reader.klass(reader.root) != "RBX::DataModel" or reader.klass(reader.players) != "RBX::Players"
                    or reader.klass(reader.workspace) != "RBX::Workspace"):
                return 0
            if reader.spec.local_player is None:
                return 0
            local = reader.pointer(reader.players + reader.spec.local_player)
            if (not local or reader.klass(local) != "RBX::Player"
                    or reader.pointer(local + reader.spec.parent) != reader.players
                    or local not in reader.children(reader.players, 128)):
                return 0
            character = reader.pointer(local + reader.spec.character)
            if not character or reader.klass(character) not in ("RBX::Model", "RBX::ModelInstance"):
                return 0
            candidates = [child for child in reader.children(character, 128)
                          if reader.klass(child) == "RBX::Humanoid"
                          and reader.pointer(child + reader.spec.parent) == character]
        except (MemoryFault, OSError):
            # Mid-teardown reads (leaving a game) must never kill the tick.
            return 0
        self.resolved_character = character
        return candidates[0] if len(candidates) == 1 else 0

    def _restore(self, feature):
        for address, (original, applied) in reversed(list(self.patches.get(feature, {}).items())):
            if original != applied and self.reader.mem.read(address, len(applied)) == applied:
                self.writer.write(address, original)
        self.patches.pop(feature, None)

    def _apply(self, feature, values):
        record = self.patches.setdefault(feature, {})
        # Preflight every field before the first write, including both speed fields.
        current = {address: self.reader.mem.read(address, len(payload)) for address, payload in values}
        for address, payload in values:
            raw = current[address]
            if len(raw) == 4:
                value = struct.unpack("<f", raw)[0]
                if not math.isfinite(value) or not 0 <= value <= 1000:
                    raise MemoryFault("movement field failed live scalar checks")
            elif raw not in (b"\0", b"\1"):
                raise MemoryFault("UseJumpPower failed boolean checks")
            if address not in record:
                record[address] = raw, raw
        for address, payload in values:
            original = record[address][0]
            try:
                if current[address] != payload:
                    self.writer.write(address, payload)
            except (MemoryFault, OSError):
                # A failed readback may follow a successful write. Record an
                # observed new value, but retain the previous applied value
                # when the write failed before changing anything.
                with contextlib.suppress(MemoryFault, OSError):
                    if self.reader.mem.read(address, len(payload)) == payload:
                        record[address] = original, payload
                raise
            record[address] = original, payload
        if any(self.reader.mem.read(address, len(payload)) != payload for address, payload in values):
            raise MemoryFault("movement fields changed during write/readback")

    def tick(self, settings):
        enabled = settings.walk_speed_enabled or settings.jump_power_enabled
        if not enabled and not self.patches:
            self.failed = False
            self.status = "Off"
            return
        if self.failed and enabled:
            return
        current = self._resolve()
        if current != self.humanoid or self.character != self.resolved_character:
            # Never touch an old/deallocated character after a respawn.
            self.patches.clear()
            self.humanoid = current
            self.character = self.resolved_character
        if not current:
            self.status = "Waiting for character"
            return
        try:
            if settings.walk_speed_enabled:
                speed = float(settings.walk_speed)
                if not math.isfinite(speed) or not 0 <= speed <= 150:
                    raise ValueError("WalkSpeed must be in 0..150")
                payload = struct.pack("<f", speed)
                self._apply("speed", [(current + self.spec.walk_speed, payload),
                                      (current + self.spec.walk_speed_check, payload)])
            else:
                self._restore("speed")
            if settings.jump_power_enabled:
                power = float(settings.jump_power)
                if not math.isfinite(power) or not 0 <= power <= 200:
                    raise ValueError("JumpPower must be in 0..200")
                self._apply("jump", [(current + self.spec.use_jump_power, b"\1"),
                                     (current + self.spec.jump_power, struct.pack("<f", power))])
            else:
                self._restore("jump")
            self.failed = False
            self.status = (" · ".join(
                ([f"Speed {settings.walk_speed:g}"] if settings.walk_speed_enabled else [])
                + ([f"Jump {settings.jump_power:g}"] if settings.jump_power_enabled else []))) if enabled else "Off"
        except (MemoryFault, ValueError, OSError) as exc:
            self.failed = True
            for feature in tuple(self.patches):
                with contextlib.suppress(MemoryFault, OSError):
                    self._restore(feature)
            pending = " Restoration still pending." if self.patches else ""
            self.status = f"Paused: {exc}.{pending} Turn Speed and Jump off to retry."

    def close(self):
        if self.patches and self._resolve() == self.humanoid and self.character == self.resolved_character:
            for feature in tuple(self.patches):
                try:
                    self._restore(feature)
                except (MemoryFault, OSError) as exc:
                    print(f"[movement] restoration incomplete: {exc}", flush=True)
        self.patches.clear()
