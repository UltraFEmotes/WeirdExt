"""Body-target selection and bounded mouse corrections. No input injection here."""
from __future__ import annotations

import math

from .w2s import project


def aim_step(frame, fov, viewport, settings, elapsed, basis_mode="columns"):
    """Return a correction for the nearest non-local projected body in the radius.

    O(n) time and O(1) extra storage. No visibility/team claim, prediction, firing,
    cached pose, or input action. The native helper independently gates delivery.
    """
    if (not settings.aim_enabled or not frame.complete or frame.rotation is None
            or frame.position is None or not math.isfinite(elapsed) or not 0 < elapsed <= 0.1
            or not math.isfinite(fov) or not 1 < fov < 179
            or not all(math.isfinite(value) and value > 0 for value in viewport)):
        return None
    center = viewport[0] / 2, viewport[1] / 2
    nearest = None
    best_squared = settings.aim_radius ** 2
    for target in frame.targets:
        if target.is_local:
            continue
        point = project((frame.rotation, frame.position), fov, viewport, target.position, basis_mode)
        if point is None or not 0 <= point[0] <= viewport[0] or not 0 <= point[1] <= viewport[1]:
            continue
        error = point[0] - center[0], point[1] - center[1]
        distance_squared = error[0] ** 2 + error[1] ** 2
        if distance_squared < best_squared:
            best_squared = distance_squared
            nearest = target, point, error
    if nearest is None:
        return None
    target, point, error = nearest
    gain = -math.expm1(-60 * min(elapsed, 0.05) / settings.aim_smoothing)
    dx, dy = error[0] * gain, error[1] * gain
    length = math.hypot(dx, dy)
    if length > 35:
        dx, dy = dx * 35 / length, dy * 35 / length
    return {"dx": dx, "dy": dy, "x": point[0] / viewport[0], "y": point[1] / viewport[1],
            "name": target.name, "world": list(target.position)}
