"""rbxl.w2s — constructed world-to-screen projection.

No engine matrix is trusted: the projection is built from the camera's
CFrame (rotation rows + position) and an explicit vertical FOV.
The tested 48-byte layout is nine row-major rotation floats followed by
three translation floats (not an interleaved 3x4). The rotation COLUMNS are
the world-space basis vectors (X=right, Y=up, Z=back), and Camera FOV is
the vertical field of view in degrees (default 70).
"""

from __future__ import annotations

import math

Viewport = tuple[int, int]  # (width, height)
Rotation = tuple[tuple[float, float, float], ...]
CFrame = tuple[Rotation, tuple[float, float, float]]


def basis(rotation: Rotation) -> tuple[tuple[float, float, float], ...]:
    """World-space basis vectors from the stored rotation rows: columns."""
    return tuple(
        (rotation[0][c], rotation[1][c], rotation[2][c]) for c in range(3)
    )


def basis_rows(rotation: Rotation) -> Rotation:
    """The rows themselves as basis vectors — the transposed reading."""
    return tuple(tuple(row) for row in rotation)


def project(cframe: CFrame, fov_degrees: float, viewport: Viewport,
            world: tuple[float, float, float],
            mode: str = "columns") -> tuple[float, float] | None:
    """World point -> pixel coordinates, or None when behind the camera.

    depth is the distance along the camera's -back axis; a point straight
    ahead lands at the viewport centre; screen y grows downward. mode picks
    the basis reading: "columns" (default) or "rows" (transposed) for the
    live A/B test."""
    width, height = viewport
    if (not math.isfinite(fov_degrees) or not 1 < fov_degrees < 179
            or not all(math.isfinite(v) and v > 0 for v in viewport)):
        raise ValueError("projection requires positive dimensions and FOV in (1, 179)")
    if mode not in ("columns", "rows"):
        raise ValueError("mode must be 'columns' or 'rows'")
    rotation, position = cframe
    if not all(math.isfinite(v) for row in rotation for v in row):
        return None
    if not all(math.isfinite(v) for v in (*position, *world)):
        return None
    right, up, back = basis_rows(rotation) if mode == "rows" else basis(rotation)
    rel = (world[0] - position[0], world[1] - position[1], world[2] - position[2])
    x = rel[0] * right[0] + rel[1] * right[1] + rel[2] * right[2]
    y = rel[0] * up[0] + rel[1] * up[1] + rel[2] * up[2]
    z = rel[0] * back[0] + rel[1] * back[1] + rel[2] * back[2]
    depth = -z
    if depth <= 0.05:
        return None
    tan_half = math.tan(math.radians(fov_degrees) / 2.0)
    aspect = width / height
    ndc_x = (x / depth) / (tan_half * aspect)
    ndc_y = (y / depth) / tan_half
    return (width * (0.5 + 0.5 * ndc_x), height * (0.5 - 0.5 * ndc_y))
