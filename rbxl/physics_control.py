"""Local collision-bit changes and edge-triggered root-PV jump boosts."""
from dataclasses import dataclass, fields
import json
import math
from pathlib import Path
import struct

from .memory import MemoryFault
from .movement import MachFieldWriter

PART_CLASSES = ("RBX::Part", "RBX::MeshPart", "RBX::WedgePart")


@dataclass(frozen=True)
class PhysicsSpec:
    collision_flags: int
    collision_mask: int
    primitive_assembly: int
    assembly_adjustment: int
    assembly_root: int
    root_adjustment: int
    motion_offset: int
    velocity: int
    velocity_mirror: int

    @classmethod
    def from_evidence(cls, path: Path, digest: str):
        report = json.loads(path.read_text())
        if report.get("binary_sha256") != digest:
            raise ValueError("physics evidence belongs to a different binary")
        selected = report.get("selected", {})
        for field in fields(cls):
            value = selected.get(field.name)
            rows = report.get("collision" if field.name.startswith("collision") else "velocity", [])
            if (type(value) is not int or not 0 <= value <= 0x10000 or not rows
                    or any(row.get(field.name) != value for row in rows)):
                raise ValueError(f"missing or conflicting physics field: {field.name}")
        mask = selected["collision_mask"]
        if not 1 <= mask <= 128 or mask & (mask - 1):
            raise ValueError("collision mask is not a single byte bit")
        if selected["velocity_mirror"] - selected["velocity"] != 72 or selected["velocity"] % 4:
            raise ValueError("unrecognized paired PV layout")
        return cls(**{field.name: selected[field.name] for field in fields(cls)})


@dataclass(frozen=True)
class BodyBinding:
    part: int
    primitive: int
    ancestry: tuple[tuple[int, int], ...]

    def valid(self, reader):
        return (reader.klass(self.part) in PART_CLASSES
                and reader.pointer(self.part + reader.spec.primitive) == self.primitive
                and reader.klass(self.primitive) == "RBX::Primitive"
                and all(reader.pointer(child + reader.spec.parent) == parent for child, parent in self.ancestry))


class PhysicsController:
    def __init__(self, reader, spec: PhysicsSpec, writer=None):
        self.reader, self.spec = reader, spec
        self.writer = writer or MachFieldWriter(reader.mem)
        self.character = 0
        self.bindings = []
        self.root_part = None
        self.original_bits = {}
        self.last_scan = -math.inf
        self.space_seen = 0
        self.noclip_failed = False
        self.status = "Off"
        self.jump_note = ""

    def _character(self):
        reader = self.reader
        try:
            if (reader.spec.local_player is None or reader.klass(reader.root) != "RBX::DataModel"
                    or reader.klass(reader.players) != "RBX::Players"):
                return 0
            player = reader.pointer(reader.players + reader.spec.local_player)
            if (reader.klass(player) != "RBX::Player"
                    or reader.pointer(player + reader.spec.parent) != reader.players
                    or player not in reader.children(reader.players, 128)):
                return 0
            character = reader.pointer(player + reader.spec.character)
            resolved = character if reader.klass(character) in ("RBX::Model", "RBX::ModelInstance") else 0
        except (MemoryFault, OSError):
            # Mid-teardown reads (leaving a game) must never kill the tick.
            return 0
        return resolved

    def _scan(self, now):
        """Direct part children of the character only — the reference design.

        Only direct character parts are covered, not nested accessory handles."""
        reader = self.reader
        self.last_scan = now
        bindings, root_part = [], None
        for child in reader.children(self.character, 128):
            if reader.pointer(child + reader.spec.parent) != self.character:
                continue
            if reader.klass(child) not in PART_CLASSES:
                continue
            primitive = reader.pointer(child + reader.spec.primitive)
            binding = BodyBinding(child, primitive, ((child, self.character),))
            if binding.valid(reader):
                bindings.append(binding)
                if reader.name(child) == "HumanoidRootPart":
                    root_part = binding
        self.bindings, self.root_part = bindings, root_part

    def _restore_collisions(self):
        reader, mask = self.reader, self.spec.collision_mask
        for primitive, (binding, original_bit) in tuple(self.original_bits.items()):
            if self._character() == self.character and binding.valid(reader) and original_bit:
                address = primitive + self.spec.collision_flags
                current = reader.mem.read(address, 1)[0]
                if not current & mask:
                    self.writer.write(address, bytes([current | mask]))
            del self.original_bits[primitive]

    def _noclip(self):
        reader, mask = self.reader, self.spec.collision_mask
        for binding in self.bindings:
            if not binding.valid(reader):
                continue
            address = binding.primitive + self.spec.collision_flags
            current = reader.mem.read(address, 1)[0]
            self.original_bits.setdefault(binding.primitive, (binding, current & mask))
            if current & mask:
                self.writer.write(address, bytes([current & ~mask]))

    def _boost(self, strength):
        reader, spec, binding = self.reader, self.spec, self.root_part
        if binding is None or not binding.valid(reader):
            raise MemoryFault("root part unavailable")
        assembly_ref = reader.pointer(binding.primitive + spec.primitive_assembly)
        if not assembly_ref:
            raise MemoryFault("assembly unavailable")
        root_ref = reader.pointer(assembly_ref - spec.assembly_adjustment + spec.assembly_root)
        root = root_ref - spec.root_adjustment if root_ref else 0
        if (reader.klass(root) != "RBX::Primitive"
                or not any(body.primitive == root and body.valid(reader) for body in self.bindings)):
            raise MemoryFault("local assembly root is not a known part")
        if not math.isfinite(strength) or not 0 <= strength <= 200:
            raise ValueError("Jump must be in 0..200")
        addresses = [root + spec.velocity + 4, root + spec.velocity_mirror + 4]
        original = []
        for offset in (spec.velocity, spec.velocity_mirror):
            # The paired PV blocks ARE the layout proof: CFrame at velocity-48,
            # mirror pose at mirror-48 must both decode as orthonormal frames.
            if reader.frame_at(root, offset - 48) is None:
                raise MemoryFault("root PV layout is invalid")
            values = struct.unpack("<3f", reader.mem.read(root + offset, 12))
            if not all(math.isfinite(value) and abs(value) <= 1000 for value in values):
                raise MemoryFault("root velocity is invalid")
            original.append(struct.pack("<f", values[1]))
        payload = struct.pack("<f", strength)
        try:
            for address in addresses:
                self.writer.write(address, payload)
            if any(reader.mem.read(address, 4) != payload for address in addresses):
                raise MemoryFault("jump boost readback changed")
        except (MemoryFault, OSError):
            for address, previous in zip(addresses, original):
                try:
                    if self._character() == self.character and binding.valid(reader) and reader.mem.read(address, 4) == payload:
                        self.writer.write(address, previous)
                except (MemoryFault, OSError):
                    pass
            raise

    def tick(self, settings, inputs, now):
        new_press = inputs.space_presses > self.space_seen
        self.space_seen = max(self.space_seen, inputs.space_presses)
        if not settings.noclip and not settings.infinite_jump and not self.original_bits:
            self.noclip_failed, self.status = False, "Off"
            return
        current = self._character()
        if current != self.character:
            self.character = current
            self.bindings, self.root_part = [], None
            self.original_bits.clear()
            self.last_scan = -math.inf
        if not current:
            self.status = "Waiting for character"
            return
        if now - self.last_scan >= 0.05:
            try:
                self._scan(now)
            except (MemoryFault, OSError):
                self.bindings, self.root_part = [], None
        notes = []
        try:
            if not settings.noclip:
                self._restore_collisions()
                self.noclip_failed = False
            elif not self.noclip_failed:
                self._noclip()
            if settings.noclip:
                notes.append("Noclip on" if not self.noclip_failed else "Noclip paused; toggle off to retry")
        except (MemoryFault, OSError) as exc:
            self.noclip_failed = True
            try:
                self._restore_collisions()
            except (MemoryFault, OSError):
                pass
            notes.append(f"Noclip paused: {exc}")
        if settings.infinite_jump:
            if not inputs.fresh(now):
                notes.append("Infinite Jump waiting for keyboard input")
            elif not inputs.available:
                notes.append("Infinite Jump needs Input Monitoring: Allow keyboard input…")
            elif not inputs.focused:
                notes.append("Infinite Jump: focus Roblox")
            elif new_press:
                try:
                    self._boost(float(settings.jump_power))
                    self.jump_note = f"Jump boost (Space #{inputs.space_presses})"
                except (MemoryFault, OSError, ValueError) as exc:
                    self.jump_note = f"Jump skipped: {exc} (Space #{inputs.space_presses})"
                notes.append(self.jump_note)
            else:
                notes.append(self.jump_note or "Infinite Jump ready — tap Space")
        else:
            self.jump_note = ""
        self.status = " · ".join(notes) or "Off"

    def close(self):
        try:
            self._restore_collisions()
        except (MemoryFault, OSError) as exc:
            print(f"[physics] collision restore incomplete: {exc}", flush=True)
