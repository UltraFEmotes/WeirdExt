"""Local collision-bit changes, edge-triggered jump boosts and fly, all on the local character."""
from dataclasses import dataclass, fields
import json
import math
from pathlib import Path
import struct
import time

from .memory import MemoryFault
from .movement import MachFieldWriter, MachVectorWriter
from .w2s import basis, basis_rows

PART_CLASSES = ("RBX::Part", "RBX::MeshPart", "RBX::WedgePart")
SOLVER_TOLERANCE = 5.0  # studs/s; one gravity step is ~3.3


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
    solver_body: int | None      # Primitive -> solver body; None until probe_jump_velocity.py records it
    solver_velocity: int | None
    solver_positions: tuple[int, ...] = ()  # float position copies; recorded by probe_offsets.py teleport
    solver_position_hold: bool = False       # re-assert the move for ~50 ms

    @classmethod
    def from_evidence(cls, path: Path, digest: str):
        report = json.loads(path.read_text())
        if report.get("binary_sha256") != digest:
            raise ValueError("physics evidence belongs to a different binary")
        selected = report.get("selected", {})
        static = [field.name for field in fields(cls) if not field.name.startswith("solver")]
        for name in static:
            value = selected.get(name)
            rows = report.get("collision" if name.startswith("collision") else "velocity", [])
            if (type(value) is not int or not 0 <= value <= 0x10000 or not rows
                    or any(row.get(name) != value for row in rows)):
                raise ValueError(f"missing or conflicting physics field: {name}")
        mask = selected["collision_mask"]
        if not 1 <= mask <= 128 or mask & (mask - 1):
            raise ValueError("collision mask is not a single byte bit")
        if selected["velocity_mirror"] - selected["velocity"] != 72 or selected["velocity"] % 4:
            raise ValueError("unrecognized paired PV layout")
        solver = report.get("solver")
        body = solver_velocity = None
        positions, hold = (), False
        if solver is not None:
            body, solver_velocity = solver.get("body_pointer"), solver.get("velocity")
            positions, hold = tuple(solver.get("positions", ())), solver.get("position_hold", False)
            if (type(hold) is not bool or len(positions) > 8
                    or any(type(offset) is not int or offset % 4 or not 0 <= offset <= 0x10000 for offset in positions)):
                raise ValueError("malformed solver position evidence")
            if (type(body) is not int or type(solver_velocity) is not int or body % 8 or solver_velocity % 4
                    or not 0 <= body <= 0x10000 or not 0 <= solver_velocity <= 0x10000):
                raise ValueError("malformed solver body velocity evidence")
        return cls(**{name: selected[name] for name in static}, solver_body=body, solver_velocity=solver_velocity,
                   solver_positions=positions, solver_position_hold=hold)


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
        self.vector_writer = MachVectorWriter(reader.mem)
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

    def _solver(self):
        """Validated (root Primitive, solver body) of the local assembly.

        The PV pair is refreshed from the solver body every physics step, so
        only the body's velocity changes motion mid-air."""
        reader, spec, binding = self.reader, self.spec, self.root_part
        if spec.solver_body is None:
            raise MemoryFault("solver body offsets not in profile; run probe_jump_velocity.py")
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
        for offset in (spec.velocity, spec.velocity_mirror):
            # The paired PV blocks ARE the layout proof: CFrame at velocity-48,
            # mirror pose at mirror-48 must both decode as orthonormal frames.
            if reader.frame_at(root, offset - 48) is None:
                raise MemoryFault("root PV layout is invalid")
        body = reader.pointer(root + spec.solver_body)
        if not body:
            raise MemoryFault("solver body unavailable")
        pv = struct.unpack("<3f", reader.mem.read(root + spec.velocity, 12))
        solved = struct.unpack("<3f", reader.mem.read(body + spec.solver_velocity, 12))
        if not all(math.isfinite(value) and abs(value) <= 1000 for value in pv):
            raise MemoryFault("root velocity is invalid")
        # Structural proof: the body's velocity tracks the PV copy within one 60 Hz gravity step.
        if not all(math.isfinite(a) and abs(a - b) <= SOLVER_TOLERANCE for a, b in zip(solved, pv)):
            raise MemoryFault("solver body velocity does not match the part")
        return root, body

    def _velocity_targets(self, root, body):
        spec = self.spec
        return [body + spec.solver_velocity, root + spec.velocity, root + spec.velocity_mirror]

    def _boost(self, strength):
        if not math.isfinite(strength) or not 0 <= strength <= 200:
            raise ValueError("Jump must be in 0..200")
        root, body = self._solver()
        addresses = [address + 4 for address in self._velocity_targets(root, body)]
        original = [self.reader.mem.read(address, 4) for address in addresses]
        payload = struct.pack("<f", strength)
        try:
            # Each write is read back by the writer; a later physics step may
            # legitimately integrate the value, so no batch readback here.
            for address in addresses:
                self.writer.write(address, payload)
        except (MemoryFault, OSError):
            for address, previous in zip(addresses, original):
                try:
                    if (self._character() == self.character and self.root_part.valid(self.reader)
                            and self.reader.mem.read(address, 4) == payload):
                        self.writer.write(address, previous)
                except (MemoryFault, OSError):
                    pass
            raise

    def teleport(self, destination, now):
        """Move every solver position copy and both pose copies by the same offset; zero velocity.

        The engine trusts different copies in different states, so all move together."""
        if not self.spec.solver_positions:
            raise MemoryFault("solver positions not in profile; run probe_offsets.py teleport")
        if not all(math.isfinite(value) and abs(value) <= 1e6 for value in destination):
            raise ValueError("teleport destination is not a finite world position")
        current = self._character()
        if not current:
            raise MemoryFault("local character unavailable")
        if current != self.character or self.root_part is None:
            self.character = current
            self._scan(now)
        root, body = self._solver()
        mem = self.reader.mem
        part = struct.unpack("<3f", mem.read(root + self.spec.velocity - 12, 12))
        shift = [destination[axis] - part[axis] for axis in range(3)]
        self._shift(root, body, shift)
        for address in self._velocity_targets(root, body):
            self.vector_writer.write(address, struct.pack("<3f", 0.0, 0.0, 0.0))
        if self.spec.solver_position_hold:
            # Re-assert for ~50 ms so a physics step cannot restore an old copy in between.
            for _ in range(3):
                time.sleep(0.016)
                part = struct.unpack("<3f", mem.read(root + self.spec.velocity - 12, 12))
                remaining = [destination[axis] - part[axis] for axis in range(3)]
                if max(abs(value) for value in remaining) > 0.5:
                    self._shift(root, body, remaining)

    def _shift(self, root, body, shift):
        mem = self.reader.mem
        for address in ([body + offset for offset in self.spec.solver_positions]
                        + [root + self.spec.velocity - 12, root + self.spec.velocity_mirror - 12]):
            values = struct.unpack("<3f", mem.read(address, 12))
            self.vector_writer.write(address, struct.pack("<3f", *(values[axis] + shift[axis] for axis in range(3))))

    def _fly(self, settings, inputs, rotation, basis_mode):
        """Velocity = camera-relative WASD plus Space/Shift, rewritten every tick; hover when idle."""
        if rotation is None:
            raise MemoryFault("camera pose unavailable")
        right, up, back = basis_rows(rotation) if basis_mode == "rows" else basis(rotation)
        keys = inputs.keys
        forward = ("w" in keys) - ("s" in keys)
        strafe = ("d" in keys) - ("a" in keys)
        lift = ("space" in keys) - ("shift" in keys)
        direction = [-back[axis] * forward + right[axis] * strafe + (lift if axis == 1 else 0)
                     for axis in range(3)]
        length = math.sqrt(sum(value * value for value in direction))
        speed = float(settings.fly_speed)
        velocity = [value / length * speed for value in direction] if length > 1e-6 else [0.0, 0.0, 0.0]
        root, body = self._solver()
        payload = struct.pack("<3f", *velocity)
        for address in self._velocity_targets(root, body):
            self.vector_writer.write(address, payload)

    def tick(self, settings, inputs, now, camera_rotation=None, basis_mode="columns"):
        new_press = inputs.space_presses > self.space_seen
        self.space_seen = max(self.space_seen, inputs.space_presses)
        if not settings.noclip and not settings.infinite_jump and not settings.fly and not self.original_bits:
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
        if settings.fly:
            if not inputs.fresh(now) or not inputs.available:
                notes.append("Fly needs keyboard input: Allow keyboard input…")
            elif not inputs.focused:
                notes.append("Fly: focus Roblox")
            else:
                try:
                    self._fly(settings, inputs, camera_rotation, basis_mode)
                    notes.append("Fly on")
                except (MemoryFault, OSError) as exc:
                    notes.append(f"Fly paused: {exc}")
        self.status = " · ".join(notes) or "Off"

    def close(self):
        try:
            self._restore_collisions()
        except (MemoryFault, OSError) as exc:
            print(f"[physics] collision restore incomplete: {exc}", flush=True)
