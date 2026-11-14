"""Spectate by pointing Camera.CameraSubject at another player's Humanoid.

CameraSubject is a smart pointer (object, control block). Every Instance keeps
its own (self, control block) pair, so a target's pair is copied in whole. One
extra strong and weak reference is added first: if Roblox later releases the
pointer we wrote (a respawn resets the subject), its counts stay balanced and
one reference leaks instead of freeing a live object.
"""
import struct

from dumper import prims
from .memory import MemoryFault
from .movement import MachPointerWriter

STRONG_COUNT, WEAK_COUNT = 8, 16  # libc++ __shared_weak_count fields after the vtable


class SpectateController:
    def __init__(self, reader, writer=None):
        spec = reader.spec
        if spec.camera_subject is None or spec.weak_this is None:
            raise ValueError("needs Camera.CameraSubject and Instance.WeakThis; run probe_offsets.py subject")
        self.reader = reader
        self.writer = writer or MachPointerWriter(reader.mem)
        self.target = 0
        self.camera = 0
        self.original = None
        self.written = None
        self.status = "Not spectating"

    def _humanoid(self, player):
        reader = self.reader
        character = reader.pointer(player + reader.spec.character)
        if reader.klass(character) not in ("RBX::Model", "RBX::ModelInstance"):
            return 0
        return next((child for child in reader.children(character, 128) if reader.klass(child) == "RBX::Humanoid"), 0)

    def _self_pair(self, humanoid):
        pair = self.reader.mem.read(humanoid + self.reader.spec.weak_this, 16)
        address, control = struct.unpack("<QQ", pair)
        if address != humanoid or not prims.plausible_ptr(control):
            raise MemoryFault("target Humanoid has no matching self pointer pair")
        return pair, control

    def start(self, player, name):
        self.stop()
        reader = self.reader
        humanoid = self._humanoid(player)
        if not humanoid:
            raise MemoryFault(f"{name} has no Humanoid right now")
        pair, control = self._self_pair(humanoid)
        camera = reader.pointer(reader.workspace + reader.spec.camera)
        if reader.klass(camera) != "RBX::Camera":
            raise MemoryFault("CurrentCamera not found")
        original = reader.mem.read(camera + reader.spec.camera_subject, 16)
        if reader.klass(struct.unpack_from("<Q", original)[0]) != "RBX::Humanoid":
            raise MemoryFault("camera subject is not a Humanoid (custom camera?)")
        for field in (STRONG_COUNT, WEAK_COUNT):
            count = struct.unpack("<q", reader.mem.read(control + field, 8))[0]
            if not 0 <= count < 1 << 32:
                raise MemoryFault("target control block counts are implausible")
            self.writer.write(control + field, struct.pack("<q", count + 1))
        self.writer.write(camera + reader.spec.camera_subject, pair)
        self.target, self.camera, self.original, self.written = player, camera, original, pair
        self.status = f"Spectating {name}"

    def stop(self):
        """Restore your own subject only if the camera still holds ours and you still exist."""
        if self.written is None:
            return
        reader = self.reader
        try:
            current = reader.mem.read(self.camera + reader.spec.camera_subject, 16)
            if current == self.written and reader.klass(struct.unpack_from("<Q", self.original)[0]) == "RBX::Humanoid":
                self.writer.write(self.camera + reader.spec.camera_subject, self.original)
        finally:
            self.target, self.camera, self.original, self.written = 0, 0, None, None
            self.status = "Not spectating"

    def tick(self, roster):
        """Stop when the target leaves or respawns, or when Roblox changes the subject itself."""
        if self.written is None:
            return
        reader = self.reader
        try:
            current = reader.mem.read(self.camera + reader.spec.camera_subject, 16)
        except MemoryFault:
            current = None
        if current != self.written:
            self.target, self.camera, self.original, self.written = 0, 0, None, None
            self.status = "Spectate ended (camera changed)"
            return
        if self.target not in roster or self._humanoid(self.target) != struct.unpack_from("<Q", self.written)[0]:
            self.stop()
            self.status = "Spectate ended (target left or respawned)"

    def close(self):
        self.stop()
