"""Body-target selection and bounded mouse corrections. No input injection here."""
from __future__ import annotations

import math

from .w2s import project

HEAD_PARTS = ("Head",)
TORSO_PARTS = ("UpperTorso", "Torso")
MAX_STEP = 35


def eligible(target, frame, settings):
    """Shared by ESP filtering and aim: not you, not a teammate (when checked), not dead."""
    if target.is_local:
        return False
    if settings.team_check and target.team and target.team == frame.local_team:
        return False
    return target.health is None or target.health > 0


def _aim_point(target, settings, project_point, center):
    """World point for the chosen body part, plus its screen projection."""
    parts = dict(target.parts)
    if settings.aim_part == "closest":
        best = None
        for world in (target.position, *parts.values()):
            point = project_point(world)
            if point is not None:
                error = math.dist(point, center)
                if best is None or error < best[0]:
                    best = error, world, point
        return (best[1], best[2]) if best else (target.position, project_point(target.position))
    names = HEAD_PARTS if settings.aim_part == "head" else TORSO_PARTS
    world = next((parts[name] for name in names if name in parts), target.position)
    return world, project_point(world)


def aim_step(frame, fov, viewport, settings, elapsed, basis_mode="columns", locked=None):
    """Return a correction toward the chosen target in the radius.

    Priority picks by crosshair distance or world distance. A sticky lock
    keeps the previous target while it stays eligible and inside the radius.
    No visibility claim, prediction, firing or input action; the native
    helper independently gates delivery.
    """
    if (not settings.aim_enabled or not frame.complete or frame.rotation is None
            or frame.position is None or not math.isfinite(elapsed) or not 0 < elapsed <= 0.1
            or not math.isfinite(fov) or not 1 < fov < 179
            or not all(math.isfinite(value) and value > 0 for value in viewport)):
        return None
    center = viewport[0] / 2, viewport[1] / 2

    def project_point(world):
        point = project((frame.rotation, frame.position), fov, viewport, world, basis_mode)
        if point is None or not 0 <= point[0] <= viewport[0] or not 0 <= point[1] <= viewport[1]:
            return None
        return point

    candidates = []
    for target in frame.targets:
        if not eligible(target, frame, settings):
            continue
        world, point = _aim_point(target, settings, project_point, center)
        if point is None:
            continue
        error = point[0] - center[0], point[1] - center[1]
        if math.hypot(*error) > settings.aim_radius:
            continue
        rank = math.hypot(*error) if settings.aim_priority == "crosshair" else math.dist(frame.position, world)
        candidates.append((rank, target, world, point, error))
    if not candidates:
        return None
    sticky = [candidate for candidate in candidates if settings.aim_sticky and candidate[1].address == locked]
    _, target, world, point, error = sticky[0] if sticky else min(candidates, key=lambda candidate: candidate[0])
    gain = -math.expm1(-60 * min(elapsed, 0.05) / settings.aim_smoothing)
    dx, dy = error[0] * gain, error[1] * gain
    length = math.hypot(dx, dy)
    if length > MAX_STEP:
        dx, dy = dx * MAX_STEP / length, dy * MAX_STEP / length
    return {"dx": dx, "dy": dy, "x": point[0] / viewport[0], "y": point[1] / viewport[1],
            "name": target.name, "world": list(world), "key": target.address}
