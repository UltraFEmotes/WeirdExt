"""dumper.prims — primitive readers and structural validators.

Every validator here is offset-agnostic: it answers "does this look like a
libc++ string / a rotation matrix / a primitive" without knowing where the
field lives. The solver uses them to *locate* fields instead of assuming them.
"""

from __future__ import annotations

import math
import struct

PTR_MIN = 0x1_0000_0000
PTR_MAX = 0xFFFF_FFFF_FFFF

FLT_MIN_ABS = 1e-6
WORLD_LIMIT = 1.0e6


def plausible_ptr(value: int) -> bool:
    return PTR_MIN <= value < PTR_MAX and (value & 0x7) == 0


def q(buf: bytes, off: int) -> int:
    return struct.unpack_from("<Q", buf, off)[0]


def f32s(buf: bytes, off: int, count: int) -> tuple[float, ...]:
    return struct.unpack_from(f"<{count}f", buf, off)


def finite_floats(buf: bytes, off: int, count: int, limit: float = WORLD_LIMIT) -> bool:
    try:
        vals = f32s(buf, off, count)
    except struct.error:
        return False
    return all(math.isfinite(v) and abs(v) <= limit for v in vals)


# --------------------------------------------------------------------------
# libc++ std::string (24 bytes, SSO in the first 24, no heap indirection for
# names shorter than 23 bytes — which every service and part name is).
# --------------------------------------------------------------------------
def is_long_string(raw: bytes) -> bool:
    if len(raw) < 24:
        return False
    return bool(struct.unpack_from("<Q", raw, 16)[0] & 0x8000_0000_0000_0000)


def decode_short_string(raw: bytes) -> str | None:
    if len(raw) < 24 or is_long_string(raw):
        return None
    size = raw[0] & 0x7F
    if size == 0 or size > 22:
        return None
    try:
        text = raw[1 : 1 + size].decode("utf-8")
    except UnicodeDecodeError:
        return None
    if not text.isprintable():
        return None
    return text


def long_string_target(raw: bytes) -> tuple[int, int] | None:
    if len(raw) < 24 or not is_long_string(raw):
        return None
    ptr = struct.unpack_from("<Q", raw, 0)[0]
    size = struct.unpack_from("<Q", raw, 8)[0] & 0x7FFF_FFFF_FFFF_FFFF
    if not plausible_ptr(ptr) or size > 512:
        return None
    return ptr, size


def sso_pattern(text: str) -> bytes:
    """Byte sequence a short name occupies inside an instance: size byte + data."""
    raw = text.encode()
    return bytes([len(raw)]) + raw


# --------------------------------------------------------------------------
# Geometry / matrices
# --------------------------------------------------------------------------
def orthonormal3(vals: tuple[float, ...], tol: float = 0.02) -> bool:
    """True when 9 floats form a proper rotation (unit rows, mutually orthogonal)."""
    if len(vals) != 9:
        return False
    if not all(math.isfinite(v) for v in vals):
        return False
    r = [vals[0:3], vals[3:6], vals[6:9]]
    for row in r:
        n = math.sqrt(sum(c * c for c in row))
        if abs(n - 1.0) > tol:
            return False
    for i in range(3):
        for j in range(i + 1, 3):
            dot = sum(a * b for a, b in zip(r[i], r[j]))
            if abs(dot) > tol:
                return False
    # right-handed: det == +1
    det = (
        r[0][0] * (r[1][1] * r[2][2] - r[1][2] * r[2][1])
        - r[0][1] * (r[1][0] * r[2][2] - r[1][2] * r[2][0])
        + r[0][2] * (r[1][0] * r[2][1] - r[1][1] * r[2][0])
    )
    return det > 0.9


def vec3_sane(buf: bytes, off: int, limit: float = WORLD_LIMIT) -> bool:
    return finite_floats(buf, off, 3, limit)


def project_ndc(matrix: tuple[float, ...], point: tuple[float, float, float]):
    if len(matrix) != 16:
        return None
    x, y, z = point
    cx = matrix[0] * x + matrix[1] * y + matrix[2] * z + matrix[3]
    cy = matrix[4] * x + matrix[5] * y + matrix[6] * z + matrix[7]
    cz = matrix[8] * x + matrix[9] * y + matrix[10] * z + matrix[11]
    cw = matrix[12] * x + matrix[13] * y + matrix[14] * z + matrix[15]
    if not all(math.isfinite(v) for v in (cx, cy, cz, cw)):
        return None
    return cx, cy, cz, cw
