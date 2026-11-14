"""Opt-in game-camera FOV writes; projection always uses the value read back."""
import math
import struct

from .memory import MemoryFault
from .movement import MachFieldWriter


class CameraController:
    def __init__(self, reader, writer=None):
        if not reader.spec.camera_verified or reader.spec.fov is None or reader.spec.fov_unit != "radians":
            raise ValueError("camera FOV writes require same-binary getter evidence")
        self.reader = reader
        self.writer = writer or MachFieldWriter(reader.mem)
        self.camera = 0
        self.original = None
        self.applied = None
        self.failed = False
        self.status = "Default FOV"

    def _resolve(self):
        reader = self.reader
        if reader.klass(reader.root) != "RBX::DataModel" or reader.klass(reader.workspace) != "RBX::Workspace":
            return 0
        camera = reader.pointer(reader.workspace + reader.spec.camera)
        return camera if camera and reader.klass(camera) == "RBX::Camera" else 0

    def _restore(self):
        if self.original is not None and self._resolve() == self.camera:
            address = self.camera + self.reader.spec.fov
            if self.original != self.applied and self.reader.mem.read(address, 4) == self.applied:
                self.writer.write(address, self.original)
        self.original = self.applied = None

    def tick(self, settings):
        if not settings.fov_enabled:
            try:
                self._restore()
                self.failed = False
                self.status = "Default FOV"
            except (MemoryFault, OSError) as exc:
                self.status = f"FOV restore failed: {exc}"
            return
        if self.failed:
            return
        camera = self._resolve()
        if camera != self.camera:
            self.camera = camera
            self.original = self.applied = None
        if not camera:
            self.status = "Waiting for camera"
            return
        desired = None
        try:
            degrees = float(settings.fov)
            if not math.isfinite(degrees) or not 30 <= degrees <= 120:
                raise ValueError("FOV must be 30–120")
            address = camera + self.reader.spec.fov
            current = self.reader.mem.read(address, 4)
            actual = math.degrees(struct.unpack("<f", current)[0])
            if not math.isfinite(actual) or not 1 < actual < 179:
                raise MemoryFault("camera FOV read is invalid")
            if self.original is None:
                self.original = self.applied = current
            desired = struct.pack("<f", math.radians(degrees))
            if current != desired:
                self.writer.write(address, desired)
            self.applied = desired
            if self.reader.mem.read(address, 4) != desired:
                raise MemoryFault("FOV readback mismatch")
            self.status = f"FOV {degrees:g}°"
        except (MemoryFault, OSError, ValueError) as exc:
            self.failed = True
            try:
                if desired is not None and self.reader.mem.read(camera + self.reader.spec.fov, 4) == desired:
                    self.applied = desired
                self._restore()
            except (MemoryFault, OSError):
                pass
            self.status = f"FOV paused: {exc}. Turn FOV off to retry."

    def close(self):
        try:
            self._restore()
        except (MemoryFault, OSError) as exc:
            print(f"[camera] FOV restore failed: {exc}", flush=True)
