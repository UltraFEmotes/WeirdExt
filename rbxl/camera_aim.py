"""Smoothed game-camera rotation writes; no mouse injection or firing."""
import math
import struct

from .memory import MemoryFault
from .movement import MachRotationWriter


def _normalize(vector):
    length = math.sqrt(sum(value * value for value in vector))
    if not math.isfinite(length) or length < 1e-9:
        raise ValueError("zero-length direction")
    return tuple(value / length for value in vector)


def _cross(left, right):
    return (left[1] * right[2] - left[2] * right[1], left[2] * right[0] - left[0] * right[2],
            left[0] * right[1] - left[1] * right[0])


def _quaternion(matrix):
    trace = sum(matrix[index][index] for index in range(3))
    if trace > 0:
        scale = math.sqrt(trace + 1) * 2
        return (scale / 4, (matrix[2][1] - matrix[1][2]) / scale,
                (matrix[0][2] - matrix[2][0]) / scale, (matrix[1][0] - matrix[0][1]) / scale)
    index = max(range(3), key=lambda axis: matrix[axis][axis])
    second, third = (index + 1) % 3, (index + 2) % 3
    scale = math.sqrt(1 + matrix[index][index] - matrix[second][second] - matrix[third][third]) * 2
    result = [0.0] * 4
    result[0] = (matrix[third][second] - matrix[second][third]) / scale
    result[index + 1] = scale / 4
    result[second + 1] = (matrix[index][second] + matrix[second][index]) / scale
    result[third + 1] = (matrix[index][third] + matrix[third][index]) / scale
    return tuple(result)


def look_rotation(current, position, target, gain):
    """Quaternion SLERP keeps each intermediate row-major basis orthonormal."""
    forward = _normalize(tuple(target[index] - position[index] for index in range(3)))
    reference = (0, 0, 1) if abs(forward[1]) > 0.999 else (0, 1, 0)
    right = _normalize(_cross(forward, reference))
    up, back = _cross(right, forward), tuple(-value for value in forward)
    desired = tuple((right[row], up[row], back[row]) for row in range(3))
    first, second = _normalize(_quaternion(current)), _normalize(_quaternion(desired))
    dot = sum(left * right for left, right in zip(first, second))
    if dot < 0:
        second, dot = tuple(-value for value in second), -dot
    gain = min(max(gain, 0), 1)
    if dot > 0.9995:
        quaternion = _normalize(tuple(left + gain * (right - left) for left, right in zip(first, second)))
    else:
        angle = math.acos(min(1, dot))
        left, right = math.sin((1 - gain) * angle) / math.sin(angle), math.sin(gain * angle) / math.sin(angle)
        quaternion = _normalize(tuple(left * a + right * b for a, b in zip(first, second)))
    w, x, y, z = quaternion
    return ((1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)),
            (2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)),
            (2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)))


class CameraAimController:
    def __init__(self, reader, writer=None):
        if not reader.spec.camera_verified:
            raise ValueError("camera aim requires verified camera getters")
        self.reader = reader
        self.writer = writer or MachRotationWriter(reader.mem)
        self.failed = False
        self.status = "Off"

    def tick(self, frame, step, settings, inputs, elapsed, now):
        if not settings.aim_enabled or settings.aim_method != "camera":
            self.failed, self.status = False, "Off"
            return None
        if self.failed:
            return None
        if not inputs.fresh(now) or not inputs.focused or not inputs.aim_held:
            self.status = "Hold the aim key in Roblox"
            return None
        if not frame.complete or step is None or not 0 < elapsed <= 0.1:
            self.status = "Camera read failed" if not frame.complete else "No target in radius"
            return None
        reader = self.reader
        camera = reader.pointer(reader.workspace + reader.spec.camera)
        if (not camera or camera != frame.camera_address or reader.klass(camera) != "RBX::Camera"
                or reader.klass(reader.root) != "RBX::DataModel"
                or reader.klass(reader.workspace) != "RBX::Workspace"):
            self.status = "Camera changed"
            return None
        current = reader.frame_at(camera, reader.spec.camera_frame)
        if current is None:
            self.failed = True
            self.status = "Camera pose read failed. Turn Aim off to retry."
            return None
        try:
            gain = -math.expm1(-60 * min(elapsed, 0.05) / settings.aim_smoothing)
            rotation = look_rotation(current[0], current[1], step["world"], gain)
            payload = struct.pack("<9f", *(value for row in rotation for value in row))
            self.writer.write(camera + reader.spec.camera_frame, payload)
            self.status = "Aiming at " + step["name"]
            return tuple(tuple(struct.unpack_from("<3f", payload, row * 12)) for row in range(3))
        except (MemoryFault, ValueError, OSError) as exc:
            self.failed = True
            self.status = f"Camera aim paused: {exc}. Turn Aim off to retry."
            return None
