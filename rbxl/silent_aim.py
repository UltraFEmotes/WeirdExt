"""Silent aim: make the mouse's ray land on the target without moving the camera or cursor.

Guns that aim with Mouse.Hit or Camera:ScreenPointToRay turn the cursor position
into a ray using the camera's viewport size: the ray's x slope is
(2*px - width) / height and its y slope is (height - 2*py) / height, both
scaled by tan(fov/2). Writing a stretched viewport size (the camera's int16
pair) makes the cursor's ray equal the target's ray; the camera itself is
untouched. A writer thread re-asserts the value every few milliseconds because
Roblox rewrites the field, and restores the real size whenever there is no
target. Games that raycast from the camera or validate shots on the server are
not affected.
"""
import struct
import threading
import time

from .memory import MemoryFault
from .movement import MachFieldWriter

MAX_SHIFT = 0.65     # largest stretch of either axis, as a fraction of the real size
MIN_SCREEN = 0.01    # target screen coordinate too close to an edge to divide by
WRITE_PERIOD = 0.004  # seconds between re-asserts; Roblox may restore the real size every frame
MAX_FAULTS = 50       # consecutive failed writes (~0.2 s) before giving up; one can lose a race with Roblox


def stretched_size(real, mouse, target):
    """Viewport (width, height) that maps the cursor's ray onto the target's.

    real is the true size in pixels; mouse and target are 0..1 from the top-left."""
    width, height = real
    ty = min(max(target[1], MIN_SCREEN), 1 - MIN_SCREEN)
    spoof_h = height * mouse[1] / ty
    spoof_h = min(max(spoof_h, height * (1 - MAX_SHIFT)), height * (1 + MAX_SHIFT))
    # x slope is divided by the height, so the width follows the (clamped) height ratio.
    spoof_w = width * (2 * mouse[0] - spoof_h / height * (2 * target[0] - 1))
    spoof_w = min(max(spoof_w, width * (1 - MAX_SHIFT)), width * (1 + MAX_SHIFT))
    return tuple(int(round(min(max(value, 1), 32767))) for value in (spoof_w, spoof_h))


class SilentAimController:
    def __init__(self, reader, writer=None):
        if reader.spec.viewport_int16 is None:
            raise ValueError("needs Camera.ViewportInt16; run probe_offsets.py viewport")
        self.reader = reader
        self.writer = writer or MachFieldWriter(reader.mem)
        self.camera = 0
        self.real = None      # (width, height) Roblox last set
        self.status = "Off"
        self._want = None     # (address, packed size) to hold, or None
        self._held = None     # (address, packed size) currently written by us
        self._error = None
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, name="silent-aim", daemon=True)
        self._thread.start()

    def _camera(self):
        camera = self.reader.pointer(self.reader.workspace + self.reader.spec.camera)
        if camera != self.camera:
            self.restore()
            self.camera, self.real = camera, None
        return camera if self.reader.klass(camera) == "RBX::Camera" else 0

    def tick(self, target_point, mouse, focused):
        """target_point and mouse are 0..1 game-view coordinates from the top-left."""
        if self._error is not None:
            raise self._error
        if not self._camera():
            self.restore()
            self.status = "Camera not found"
            return
        address = self.camera + self.reader.spec.viewport_int16
        current = struct.unpack("<hh", self.reader.mem.read(address, 4))
        with self._lock:
            ours = self._held is not None and self._held[1] == struct.pack("<hh", *current)
        if not ours:
            self.real = current   # not our value, so it is Roblox's real size (tracks resizes)
        if target_point is None or mouse is None or not focused:
            self.restore()
            self.status = "No target in FOV" if focused else "Focus Roblox"
            return
        size = stretched_size(self.real, mouse, target_point)
        with self._lock:
            self._want = address, struct.pack("<hh", *size)
        self.status = "Active"

    def restore(self):
        with self._lock:
            self._want = None

    def _run(self):
        faults = 0
        while not self._stop.wait(WRITE_PERIOD):
            with self._lock:
                want, held = self._want, self._held
            try:
                if want is not None:
                    if self.reader.mem.read(want[0], 4) != want[1]:
                        self.writer.write(*want)
                    held = want
                elif held is not None:
                    if self.real is not None:
                        self.writer.write(held[0], struct.pack("<hh", *self.real))
                    held = None
                faults = 0
            except MemoryFault as exc:
                faults += 1
                if faults >= MAX_FAULTS:
                    self._error, held = exc, None
                    with self._lock:
                        self._want = None
            with self._lock:
                self._held = held

    def stop(self):
        """End the writer without touching the game (its tree may already be gone)."""
        self._stop.set()
        self._thread.join(timeout=1)

    def close(self):
        self.restore()
        time.sleep(WRITE_PERIOD * 3)   # let the writer put the real size back
        self.stop()
