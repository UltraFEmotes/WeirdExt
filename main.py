#!/usr/bin/env python3
"""WeirdExt — a macOS ARM64 external with a native overlay and settings.

Projection always reads the current camera FOV. The FOV control changes the
game camera rather than overriding projection. --headless omits the GUI.
Stop with Ctrl+C or the WE menu. Right Shift toggles the menu.
"""
from __future__ import annotations

import argparse
from collections import deque
import contextlib
from dataclasses import replace
import json
import math
import os
import platform
from pathlib import Path
import pwd
import subprocess
import sys
import threading
import time

from rbxl.esp_reader import ESPReader, Frame, OffsetSpec
from rbxl.esp_settings import Settings
from rbxl.aim import aim_step
from rbxl.camera_aim import CameraAimController
from rbxl.camera_control import CameraController
from rbxl.explorer import build_tree
from rbxl.input_state import InputState
from rbxl.movement import MovementController, MovementSpec
from rbxl.physics_control import PhysicsController, PhysicsSpec
from rbxl.session import SessionHealth, SessionRecovery, SessionWatcher
from rbxl.native_build import build_overlay
from rbxl.profiles import select_profile
from rbxl.memory import MemoryFault, find_roblox_pid
from rbxl.w2s import basis, basis_rows, project


BONES = (("Head", "UpperTorso"), ("UpperTorso", "LowerTorso"),
         ("UpperTorso", "LeftUpperArm"), ("LeftUpperArm", "LeftLowerArm"), ("LeftLowerArm", "LeftHand"),
         ("UpperTorso", "RightUpperArm"), ("RightUpperArm", "RightLowerArm"), ("RightLowerArm", "RightHand"),
         ("LowerTorso", "LeftUpperLeg"), ("LeftUpperLeg", "LeftLowerLeg"), ("LeftLowerLeg", "LeftFoot"),
         ("LowerTorso", "RightUpperLeg"), ("RightUpperLeg", "RightLowerLeg"), ("RightLowerLeg", "RightFoot"),
         ("Head", "Torso"), ("Torso", "Left Arm"), ("Torso", "Right Arm"),
         ("Torso", "Left Leg"), ("Torso", "Right Leg"))
HEAD_TOP = 0.8   # studs from the Head centre to the top of the head
FOOT_DROP = 0.6  # studs from a foot/leg centre to the sole
BOX_PADDING = 3  # pixels around the projected body


def display_packet(frame: Frame, fov: float, viewport, settings: Settings, basis_mode: str = "columns"):
    """Project each body to a box (from its real parts when readable), skeleton and labels.

    The diamond marks overlay center only; it cannot validate camera fields.
    Targets off screen or behind the camera become direction arrows.
    """
    if basis_mode not in ("columns", "rows"):
        raise ValueError("mode must be 'columns' or 'rows'")
    targets, offscreen = [], []
    boresight = {"x": 0.5, "y": 0.5}
    if frame.rotation is not None and frame.position is not None:
        cframe = (frame.rotation, frame.position)
        right, up, _ = basis_rows(frame.rotation) if basis_mode == "rows" else basis(frame.rotation)
        teams = sorted({target.team for target in frame.targets if target.team})

        def screen(world):
            return project(cframe, fov, viewport, world, basis_mode)

        for target_index, target in enumerate(frame.targets):
            teammate = bool(target.team) and target.team == frame.local_team and not target.is_local
            if settings.team_check and teammate:
                continue
            parts = dict(target.parts)
            extremes = [target.position, *parts.values()]
            if "Head" in parts:
                head = parts["Head"]
                extremes.append((head[0], head[1] + HEAD_TOP, head[2]))
            extremes += [(x, y - FOOT_DROP, z) for name, (x, y, z) in parts.items()
                         if name in ("LeftFoot", "RightFoot", "Left Leg", "Right Leg")]
            points = [point for point in map(screen, extremes) if point is not None]
            if len(points) >= 3:
                left = min(point[0] for point in points) - BOX_PADDING
                top = min(point[1] for point in points) - BOX_PADDING
                width = max(point[0] for point in points) + BOX_PADDING - left
                height = max(point[1] for point in points) + BOX_PADDING - top
                x, y = (left + width / 2) / viewport[0], (top + height / 2) / viewport[1]
                w, h = width / viewport[0], height / viewport[1]
            else:
                # No readable limbs: fixed-height estimate around the root part.
                low = screen((target.position[0], target.position[1] + 0.55 * settings.box_height,
                              target.position[2]))
                high = screen((target.position[0], target.position[1] - 0.45 * settings.box_height,
                               target.position[2]))
                if low is None or high is None:
                    x = y = h = -1.0
                else:
                    x = (low[0] + high[0]) / (2 * viewport[0])
                    y = (low[1] + high[1]) / (2 * viewport[1])
                    h = (high[1] - low[1]) / viewport[1]
                w = h * settings.box_ratio * viewport[1] / viewport[0]
            distance = math.dist(frame.position, target.position)
            team = teams.index(target.team) + 1 if target.team else 0
            if not 0 <= x <= 1 or not 0 <= y <= 1 or not 0.001 < h < 2.5:
                if not target.is_local:
                    relative = [target.position[axis] - frame.position[axis] for axis in range(3)]
                    across = sum(relative[axis] * right[axis] for axis in range(3))
                    rise = sum(relative[axis] * up[axis] for axis in range(3))
                    if math.hypot(across, rise) > 1e-6:
                        offscreen.append({"angle": math.atan2(-rise, across), "name": target.name,
                                          "distance": distance, "team": team})
                continue
            bones = []
            for start_name, end_name in BONES:
                if start_name in parts and end_name in parts:
                    start, end = screen(parts[start_name]), screen(parts[end_name])
                    if start is not None and end is not None:
                        bones += [start[0] / viewport[0], start[1] / viewport[1],
                                  end[0] / viewport[0], end[1] / viewport[1]]
            health = None
            if target.health is not None and target.max_health:
                health = min(max(target.health / target.max_health, 0.0), 1.0)
            targets.append({"name": target.name, "x": x, "y": y, "w": w, "h": h,
                            "target_index": target_index, "distance": distance, "bones": bones,
                            "health": health, "team": team, "teammate": teammate})
    return {"targets": targets, "offscreen": offscreen, "status": frame.status,
            "roster": frame.roster_count, "fov": fov, "boresight": boresight, "complete": frame.complete}


class UpdateStats:
    """One-second rolling completed-snapshot rate; not a claimed render FPS."""
    def __init__(self):
        self.samples = deque()

    def record(self, started, completed):
        self.samples.append((completed, max(0.0, completed - started) * 1000))
        while len(self.samples) > 1 and completed - self.samples[0][0] > 1.0:
            self.samples.popleft()
        span = completed - self.samples[0][0]
        return {"sample_hz": (len(self.samples) - 1) / span if span > 0 else 0.0,
                "read_ms": self.samples[-1][1]}


def helper_identity():
    options = {}
    environment = os.environ.copy()
    # Keep UI in the original console user's identity when Python needs
    # root for Mach reads. This helper never receives a task port.
    if os.geteuid() == 0 and os.environ.get("SUDO_UID"):
        uid = int(os.environ["SUDO_UID"])
        account = pwd.getpwuid(uid)
        if uid != 0:
            options.update(user=uid, group=account.pw_gid, extra_groups=[])
            environment.update(HOME=account.pw_dir, USER=account.pw_name, LOGNAME=account.pw_name)
    return environment, options


class Overlay:
    def __init__(self, executable, pid, inset_top, viewport):
        self.viewport = viewport
        self.lock = threading.Lock()
        self.write_lock = threading.Lock()
        self.ready = threading.Event()
        self.health = {}
        self.pending_settings = None
        self.quit_requested = False
        self.pending_input = None
        self.pending_explorer = False
        command = [str(executable), str(pid)]
        command.append(str(inset_top))
        environment, options = helper_identity()
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        text=True, bufsize=1, start_new_session=True,
                                        env=environment, **options)
        self.thread = threading.Thread(target=self._read_viewport, daemon=True)
        self.thread.start()

    def _read_viewport(self):
        for line in self.process.stdout:
            try:
                event = json.loads(line)
                if event.get("type") == "ready":
                    self.ready.set()
                    continue
                if event.get("type") == "health":
                    with self.lock:
                        self.health = event
                    continue
                if event.get("type") == "settings":
                    with self.lock:
                        self.pending_settings = event.get("settings")
                    continue
                if event.get("type") == "quit":
                    with self.lock:
                        self.quit_requested = True
                    continue
                if event.get("type") == "input":
                    state = InputState.from_event(event, time.monotonic())
                    with self.lock:
                        self.pending_input = state
                    continue
                if event.get("type") == "explorer_refresh":
                    with self.lock:
                        self.pending_explorer = True
                    continue
                size = float(event["width"]), float(event["height"])
                if all(math.isfinite(value) and value > 0 for value in size):
                    with self.lock:
                        self.viewport = size
            except (ValueError, KeyError, TypeError):
                continue

    def wait_ready(self, timeout=10):
        deadline = time.monotonic() + timeout
        while not self.ready.is_set():
            code = self.process.poll()
            if code is not None:
                raise RuntimeError(f"overlay exited during startup (code {code}); no game attach attempted")
            if time.monotonic() >= deadline:
                raise RuntimeError("overlay startup handshake timed out; no game attach attempted")
            self.ready.wait(0.05)

    def size(self):
        with self.lock:
            return self.viewport

    def delivery_status(self):
        with self.lock:
            health = self.health.copy()
        if not health:
            return "native delivery awaiting telemetry"
        age = health["age_ms"]
        age_label = f"{age:.0f} ms" if age is not None else "no valid frame"
        return (f"native receive/draw {health['receive_hz']:.1f}/{health['draw_hz']:.1f} Hz; "
                f"age {age_label}; rejected {health['rejected']}; {health['reason']}")

    def take_settings(self):
        with self.lock:
            settings = self.pending_settings
            self.pending_settings = None
            return settings

    def wants_quit(self):
        with self.lock:
            return self.quit_requested

    def take_input(self):
        with self.lock:
            state, self.pending_input = self.pending_input, None
        return state

    def take_explorer(self):
        with self.lock:
            pending, self.pending_explorer = self.pending_explorer, False
        return pending

    def send(self, packet):
        if self.process.poll() is not None:
            return False
        try:
            with self.write_lock:
                self.process.stdin.write(json.dumps(packet, allow_nan=False) + "\n")
                self.process.stdin.flush()
            return True
        except (BrokenPipeError, OSError):
            return False

    def send_control(self, packet):
        """Control commands use plain JSON (NaN cannot appear)."""
        return self.send(packet)

    def close(self):
        with contextlib.suppress(BrokenPipeError, OSError):
            self.process.stdin.close()
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        self.thread.join(timeout=1)
        self.process.stdout.close()


@contextlib.contextmanager
def launch_overlay(pid, args):
    executable = build_overlay()
    overlay = Overlay(executable, pid, args.inset_top, (args.width, args.height))
    try:
        overlay.wait_ready()
        print("[esp] native overlay ready", flush=True)
        yield overlay
    finally:
        overlay.close()


def camera_sanity(cam_pos, cam_rotation, local_pos, basis_mode="columns"):
    """Heuristics only: custom cameras and first person need not match these bands."""
    if not (cam_pos and local_pos and cam_rotation):
        return None
    right, up, back = basis_rows(cam_rotation) if basis_mode == "rows" else basis(cam_rotation)
    forward = tuple(-c for c in back)
    delta = tuple(local_pos[i] - cam_pos[i] for i in range(3))
    distance = math.dist(cam_pos, local_pos)
    length = math.sqrt(sum(c * c for c in delta))
    cosine = (sum(a * b for a, b in zip(delta, forward)) / length) if length else None
    angle = math.degrees(math.acos(max(-1.0, min(1.0, cosine)))) if cosine is not None else None
    distance_ok = distance <= 40.0
    angle_ok = angle <= 45.0 if angle is not None else None
    notes = [
        f"camera↔your character {distance:.1f} studs — "
        + ("within default-camera heuristic" if distance_ok
           else "outside default-camera heuristic; not proof of a wrong offset"),
        (f"camera forward vs camera→you {angle:.0f}°" if angle is not None else
         "camera forward vs camera→you undefined (coincident positions)")
        + " — diagnostic only; custom/first-person cameras can differ",
    ]
    return {"distance": distance, "angle": angle, "distance_ok": distance_ok,
            "angle_ok": angle_ok, "notes": notes}


def _pump_controls(state, overlay):
    """Terminal stdin -> live FOV/inset/quit; the overlay stays visible so
    calibration can be watched without rerunning discovery."""
    for line in sys.stdin:
        parse_control(line, state, overlay)
        if state.get("quit"):
            return


def _print_diagnostics(frame, packet, fov, fov_source, viewport, basis_mode="columns"):
    """Per-second alignment evidence: camera, per-target world and pixels,
    plus the third-person camera cross-check against your own character."""
    if frame.position is None:
        return
    print(f"[esp]   cam=({frame.position[0]:.1f}, {frame.position[1]:.1f}, "
          f"{frame.position[2]:.1f})  fov={fov:.1f} ({fov_source})  "
          f"vp={viewport[0]:.0f}x{viewport[1]:.0f}", flush=True)
    sanity = camera_sanity(frame.position, frame.rotation, frame.local_position, basis_mode)
    if sanity is not None:
        for note in sanity["notes"]:
            print(f"[esp]   {note}", flush=True)
    elif frame.local_position is None:
        print("[esp]   camera cross-check unavailable (your character position unreadable)",
              flush=True)
    for marker in packet["targets"]:
        target = frame.targets[marker["target_index"]]
        print(f"[esp]   {marker['name'][:16]:<16} world=({target.position[0]:.1f}, "
              f"{target.position[1]:.1f}, {target.position[2]:.1f})  "
              f"px=({marker['x'] * viewport[0]:.0f}, {marker['y'] * viewport[1]:.0f})  "
              f"box={marker['w'] * viewport[0]:.0f}x{marker['h'] * viewport[1]:.0f}", flush=True)


def parse_control(line: str, state, overlay=None):
    """Terminal commands; fov changes the camera, never the projection model."""
    parts = line.split()
    if not parts:
        return
    command = parts[0].lower()
    try:
        if command == "fov" and len(parts) == 2:
            if parts[1].lower() in ("auto", "reset"):
                state["fov_request"] = (False, 70.0)
                print("[esp] FOV reset", flush=True)
            else:
                value = float(parts[1])
                if not math.isfinite(value) or not 30 <= value <= 120:
                    raise ValueError
                state["fov_request"] = (True, value)
                print(f"[esp] Camera FOV -> {value:g}", flush=True)
        elif command == "basis":
            mode = parts[1].lower() if len(parts) == 2 else "flip"
            current = state.get("basis_mode", "columns")
            if mode == "flip":
                state["basis_mode"] = "rows" if current == "columns" else "columns"
            elif mode in ("rows", "columns"):
                state["basis_mode"] = mode
            else:
                print("[esp] basis: flip | rows | columns", flush=True)
                return
            print(f"[esp] basis reading -> {state['basis_mode']} (watch the boxes snap)", flush=True)
        elif command == "inset" and len(parts) == 2:
            value = float(parts[1])
            if not math.isfinite(value) or not 0 <= value <= 200:
                raise ValueError
            if overlay is not None:
                overlay.send_control({"cmd": "inset", "value": value})
            state["inset"] = value
            print(f"[esp] inset -> {value:g} pt", flush=True)
        elif command == "pos" and len(parts) == 3:
            dx, dy = float(parts[1]), float(parts[2])
            if not (math.isfinite(dx) and math.isfinite(dy)) or max(abs(dx), abs(dy)) > 2000:
                raise ValueError
            if overlay is not None:
                overlay.send_control({"cmd": "nudge", "dx": dx, "dy": dy})
            state["pos"] = (dx, dy)
            print(f"[esp] overlay offset -> ({dx:g}, {dy:g}) pt; get the diamond onto the crosshair",
                  flush=True)
        elif command == "quit":
            state["quit"] = True
        else:
            print("[esp] commands: fov <deg> | fov auto | basis flip | inset <pt> | "
                  "pos <dx> <dy> | quit", flush=True)
    except ValueError:
        print("[esp] bad value; try: fov 62 | fov auto | inset 0 | quit", flush=True)


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path,
                        help="profile directory; default: the one matching the installed Roblox binary")
    parser.add_argument("--pid", type=int)
    parser.add_argument("--fps", type=float, default=60.0,
                        help="target fresh memory samples per second (default: 60; actual rate is shown)")
    parser.add_argument("--diagnostics", action="store_true",
                        help="print verbose per-target diagnostics once per second (off for smooth polling)")
    parser.add_argument("--inset-top", type=float, default=28.0, help="windowed title-bar inset in points; fullscreen uses zero")
    parser.add_argument("--show-local", action="store_true")
    parser.add_argument("--box-height", type=float, default=5.4, help="box height in studs (default: 5.4)")
    parser.add_argument("--box-ratio", type=float, default=0.6, help="box width/height ratio (default: 0.6)")
    parser.add_argument("--headless", action="store_true", help="print projected targets, no overlay")
    parser.add_argument("--seconds", type=float, default=0.0, help="poll duration after discovery; zero means until Ctrl+C")
    parser.add_argument("--width", type=int, default=1280, help="headless/fallback viewport width")
    parser.add_argument("--height", type=int, default=720, help="headless/fallback viewport height")
    args = parser.parse_args(argv)
    if not math.isfinite(args.fps) or not 1 <= args.fps <= 60:
        parser.error("--fps must be in [1, 60]")
    if not math.isfinite(args.seconds) or args.seconds < 0:
        parser.error("--seconds must be finite and nonnegative")
    if not math.isfinite(args.inset_top) or not 0 <= args.inset_top <= 100:
        parser.error("--inset-top must be in [0, 100]")
    if args.width <= 0 or args.height <= 0:
        parser.error("viewport dimensions must be positive")
    if not math.isfinite(args.box_height) or not 1 <= args.box_height <= 20:
        parser.error("--box-height must be in [1, 20] studs")
    if not math.isfinite(args.box_ratio) or not 0.2 <= args.box_ratio <= 2:
        parser.error("--box-ratio must be in [0.2, 2]")
    if args.pid is not None and args.pid <= 0:
        parser.error("--pid must be positive")
    return args


def attach_session(pid, spec, *, fresh=False):
    """One discovery pass; raises on failure so callers can retry cleanly."""
    return ESPReader.attach(pid, spec, **({"fresh": True} if fresh else {}))


def build_controllers(reader, args, spec):
    """Fresh controllers for a (re)attached reader; movement/physics off."""
    camera_control = movement = physics = camera_aim = None
    camera_status = "Default FOV"
    movement_status = "Off"
    physics_status = "Off"
    try:
        camera_control = CameraController(reader)
        camera_status = camera_control.status
    except ValueError as exc:
        camera_status = f"FOV unavailable: {exc}"
    try:
        camera_aim = CameraAimController(reader)
    except ValueError as exc:
        print(f"[camera-aim] unavailable: {exc}", flush=True)
    try:
        movement_spec = MovementSpec.from_evidence(args.profile / "movement.json", spec.binary_sha256)
        movement = MovementController(reader, movement_spec)
        movement_status = movement.status
    except (OSError, ValueError, KeyError) as exc:
        movement_status = f"Movement unavailable: {exc}"
        print(f"[movement] {movement_status}", flush=True)
    try:
        physics = PhysicsController(reader, PhysicsSpec.from_evidence(args.profile / "physics.json", spec.binary_sha256))
        physics_status = physics.status
    except (OSError, ValueError, KeyError) as exc:
        physics_status = f"Noclip/Infinite Jump unavailable: {exc}"
        print(f"[physics] {physics_status}", flush=True)
    return (camera_control, camera_status, movement, movement_status,
            physics, physics_status, camera_aim)


def close_controllers(camera_control, movement, physics):
    for controller in (camera_control, physics, movement):
        if controller is not None:
            try:
                controller.close()
            except Exception as exc:
                print(f"[session] controller cleanup failed: {exc}", flush=True)


def main(argv=None):
    args = arguments(argv)
    movement = None
    camera_control = None
    physics = None
    camera_aim = None
    reader = None
    recovery = None
    try:
        if sys.platform != "darwin" or platform.machine() != "arm64":
            raise RuntimeError("WeirdExt requires native ARM64 macOS, not Windows, Linux or Rosetta")
        args.profile = args.profile or select_profile()
        print(f"[esp] profile {args.profile.name}", flush=True)
        spec = OffsetSpec.from_report(args.profile / "offsets.json").with_camera_evidence(
            args.profile / "camera.json")
        pid = args.pid or find_roblox_pid()
        if pid is None:
            raise RuntimeError("Roblox is not running")
        manager = contextlib.nullcontext(None) if args.headless else launch_overlay(pid, args)
        with manager as overlay:
            settings = Settings(show_local=args.show_local, box_height=args.box_height,
                                box_ratio=args.box_ratio, fps=args.fps)
            if overlay:
                overlay.send_control({"cmd": "settings_state", "settings": settings.event()})
            recovery = SessionRecovery(lambda candidate_pid: attach_session(candidate_pid, spec, fresh=True),
                                       find_roblox_pid)
            try:
                reader = attach_session(pid, spec)
            except (RuntimeError, MemoryFault, OSError) as exc:
                print(f"[session] waiting for a loaded game: {exc}", flush=True)
                if overlay:
                    overlay.send_control({"cmd": "target_pid", "value": 0})
            movement_status = "Not connected"
            camera_status = "Not connected"
            physics_status = "Not connected"
            inputs = InputState()
            session = SessionWatcher()
            if reader is not None:
                (camera_control, camera_status, movement, movement_status,
                 physics, physics_status, camera_aim) = build_controllers(reader, args, spec)
            state = {"inset": None, "quit": False, "basis_mode": "columns"}
            control = threading.Thread(target=_pump_controls, args=(state, overlay), daemon=True)
            control.start()
            print("[esp] WeirdExt — macOS ARM64 external; overlay stays visible; "
                  "terminal: fov <deg> | fov auto | basis flip | inset <pt> | pos <dx> <dy> | quit",
                  flush=True)
            print(f"[esp] live sampling target {args.fps:g} Hz; native drawing 60 Hz; "
                  "only console output is limited to once per second", flush=True)
            started = time.monotonic()
            next_sample = started
            stats = UpdateStats()
            last_console = -math.inf
            last_movement = -math.inf
            last_aim = started
            aim_lock = None
            explorer_open = False
            health = SessionHealth()
            last_pid_check = started
            reported_attempt = 0
            rejoining = reader is None
            last_physics_log = None
            while not state["quit"] and (not args.seconds or time.monotonic() - started < args.seconds):
                tick = time.monotonic()
                if overlay:
                    if overlay.wants_quit() is True:
                        break
                    update = overlay.take_settings()
                    if isinstance(update, dict):
                        try:
                            settings = Settings.from_event(update)
                        except ValueError as exc:
                            print(f"[settings] rejected: {exc}", flush=True)
                    if (native_input := overlay.take_input()) is not None:
                        inputs = native_input
                    if overlay.take_explorer() is True:
                        explorer_open = True
                request = state.pop("fov_request", None)
                if request is not None:
                    settings = replace(settings, fov_enabled=request[0], fov=request[1])
                    if overlay:
                        overlay.send_control({"cmd": "settings_state", "settings": settings.event()})
                if reader is None:
                    attached = recovery.poll(tick)
                    if attached is not None:
                        pid, reader = attached
                        (camera_control, camera_status, movement, movement_status,
                         physics, physics_status, camera_aim) = build_controllers(reader, args, spec)
                        if physics is not None:
                            physics.space_seen = inputs.space_presses
                        inputs = InputState(space_presses=inputs.space_presses)
                        health = SessionHealth()
                        last_pid_check = tick
                        if overlay:
                            overlay.send_control({"cmd": "target_pid", "value": pid})
                    elif recovery.attempts != reported_attempt:
                        reported_attempt = recovery.attempts
                        print(f"[session] discovery attempt {reported_attempt}; "
                              f"{recovery.error or 'waiting for game'}", flush=True)
                frame = Frame(None, None, (), 0, "Waiting for a loaded game — retrying discovery",
                              complete=False)
                try:
                    if reader is not None:
                        if tick - last_pid_check >= 1.0:
                            last_pid_check = tick
                            current_pid = find_roblox_pid()
                            if current_pid != pid:
                                raise RuntimeError(f"Roblox process changed: {pid} → {current_pid}")
                        # Validate the tree and camera before any controller tick.
                        # Readable RTTI alone is not ownership.
                        frame = reader.snapshot(settings.show_local, settings.esp_skeleton)
                        if not health.observe(frame, tick):
                            raise RuntimeError(f"session stayed incomplete: {frame.status}")
                        if frame.complete and frame.fov is not None:
                            if physics is not None:
                                physics.tick(settings, inputs, time.monotonic(), frame.rotation,
                                             state["basis_mode"])
                                physics_status = physics.status
                            if tick - last_movement >= 0.1:
                                if movement is not None:
                                    movement.tick(settings)
                                    movement_status = movement.status
                                if camera_control is not None:
                                    camera_control.tick(settings)
                                    camera_status = camera_control.status
                                last_movement = tick
                            if rejoining:
                                session.observe_rejoin(tick)
                                rejoining = False
                        else:
                            camera_status = movement_status = physics_status = "Game loading — features paused"
                except Exception as exc:
                    print(f"[session] invalidated ({exc}); waiting for the next game", flush=True)
                    # Do not restore fields into a detached game tree.
                    # Restoration is only attempted on a validated shutdown.
                    movement = camera_control = physics = camera_aim = None
                    SessionRecovery._dispose(reader)
                    reader = None
                    inputs = InputState(space_presses=inputs.space_presses)
                    rejoining = True
                    frame = Frame(None, None, (), 0, "Game changed — waiting for you to load in",
                                  complete=False)
                    camera_status = movement_status = physics_status = "Waiting for next game — features paused"
                    if overlay:
                        overlay.send_control({"cmd": "target_pid", "value": 0})
                if frame.complete:
                    session.observe([address for address, _ in frame.roster], dict(frame.roster), tick)
                timing = stats.record(tick, time.monotonic())
                fov, fov_source = frame.fov, "camera"
                if fov is None:
                    frame = replace(frame, rotation=None, position=None, targets=(),
                                    complete=False, status=(frame.status if not frame.complete else "Camera FOV unavailable"))
                    fov, fov_source = 70.0, "paused"
                viewport = overlay.size() if overlay else (args.width, args.height)
                elapsed = tick - last_aim
                last_aim = tick
                # The sticky lock lasts one right-mouse hold.
                aim_lock = aim_lock if inputs.aim_held else None
                step = (aim_step(frame, fov, viewport, settings, elapsed, state["basis_mode"], aim_lock)
                        if frame.complete and timing["read_ms"] < 50 else None)
                aim_lock = step["key"] if step is not None else None
                if camera_aim is not None and step is not None and frame.complete:
                    try:
                        rotation = camera_aim.tick(frame, step, settings, inputs, elapsed, time.monotonic())
                        if rotation is not None:
                            frame = replace(frame, rotation=rotation)
                    except (MemoryFault, OSError, RuntimeError) as exc:
                        camera_aim = None
                        print(f"[camera-aim] paused: {exc}", flush=True)
                packet = display_packet(frame, fov, viewport, settings, state["basis_mode"])
                packet.update(timing)
                packet.update(options=settings.overlay_options(), movement_available=movement is not None,
                              movement_status=movement_status, camera_available=camera_control is not None,
                              camera_status=camera_status, aim_enabled=settings.aim_enabled,
                              aim_radius=settings.aim_radius, aim_method=settings.aim_method,
                              noclip_available=physics is not None, noclip_status=physics_status,
                              toasts=session.feed(tick))
                packet["aim"] = step
                if overlay:
                    if not overlay.send(packet):
                        print("[esp] overlay closed", flush=True)
                        break
                    if explorer_open and reader is not None and frame.complete:
                        explorer_open = False  # One snapshot per Refresh/open request.
                        try:
                            tree = build_tree(reader, reader.root)
                            overlay.send({"type": "explorer", "tree": tree})
                        except (MemoryFault, OSError):
                            overlay.send({"type": "explorer", "tree":
                                          {"name": "Read failed", "truncated": True, "kids": []}})
                while session.events:
                    print(f"[session] {session.events.pop(0)}", flush=True)
                # Session transitions have their own messages. Physics status
                # is meaningful only for a validated frame, and logs on change.
                if frame.complete and (settings.infinite_jump or settings.noclip):
                    if physics_status != last_physics_log:
                        print(f"[physics] {physics_status}", flush=True)
                        last_physics_log = physics_status
                else:
                    last_physics_log = None
                if tick - last_console >= 1:
                    if args.headless:
                        print(json.dumps(packet, allow_nan=False), flush=True)
                    else:
                        print(f"[esp] roster {frame.roster_count}; boxes {len(packet['targets'])}; "
                              f"FOV {fov:g} ({fov_source}); basis {state['basis_mode']}; "
                              f"read {timing['sample_hz']:.1f} Hz / {timing['read_ms']:.1f} ms; "
                              f"{frame.status}; {overlay.delivery_status() if overlay else ''}", flush=True)
                        if args.diagnostics:
                            _print_diagnostics(frame, packet, fov, fov_source, viewport, state["basis_mode"])
                    last_console = tick
                # Absolute deadlines prevent sleep overshoot accumulating each
                # frame. Slow reads skip missed slots rather than queueing work.
                next_sample = max(next_sample + 1 / settings.fps, time.monotonic())
                time.sleep(max(0, next_sample - time.monotonic()))
        return 0
    except KeyboardInterrupt:
        print("\n[esp] stopped", flush=True)
        return 130
    except (OSError, ValueError, KeyError, RuntimeError, MemoryFault, subprocess.SubprocessError) as exc:
        print(f"[esp] {exc}", file=sys.stderr, flush=True)
        return 1
    finally:
        if recovery is not None:
            recovery.close()
        if reader is not None:
            try:
                reader.validate_session()
                close_controllers(camera_control, movement, physics)
            except Exception as exc:
                print(f"[session] skipping stale restoration: {exc}", flush=True)
            SessionRecovery._dispose(reader)


if __name__ == "__main__":
    raise SystemExit(main())
