"""Read-only ESP snapshots using same-binary evidence and a reciprocal tree.

Discovery runs outside frame sampling. Projection always uses the actual
camera FOV; missing camera/local-player state marks a frame incomplete.
"""
from __future__ import annotations

import hashlib
import json
import math
import struct
from dataclasses import dataclass, replace
from pathlib import Path

from dumper import prims
from dumper.solve import InstanceLayout, Walker, WalkError, solve_instance_layout
from rbxl.memory import MachProcess, MemoryFault, find_roblox_candidates


@dataclass(frozen=True)
class OffsetSpec:
    name: int
    parent: int
    children: int
    character: int
    primitive: int
    primitive_frame: int
    camera: int
    camera_frame: int
    local_player: int | None
    binary_sha256: str
    fov: int | None = None  # Camera.FieldOfView candidate; unvalidated
    fov_unit: str = "degrees"
    camera_verified: bool = False

    def with_camera_evidence(self, path: Path):
        """Apply same-binary, unambiguous offline getter evidence over heuristics."""
        evidence = json.loads(path.read_text(encoding="utf-8"))
        if evidence.get("binary_sha256") != self.binary_sha256:
            raise ValueError("camera getter evidence and offset report have different binary identities")
        selected = evidence.get("selected")
        if not isinstance(selected, dict) or selected.get("camera_fov_unit") != "radians":
            raise ValueError("camera evidence lacks supported, unique getter-backed fields")
        for key, property_name in (("camera_cframe_offset", "CFrame"), ("camera_fov_offset", "FieldOfView")):
            offset = selected.get(key)
            rows = evidence.get("candidates", {}).get(property_name, [])
            if (type(offset) is not int or not 0 <= offset <= 0x10000 or not rows
                    or any(row.get("offset") != offset for row in rows)):
                raise ValueError(f"camera evidence has missing or conflicting {property_name} getters")
        print(f"[esp] static Camera getters: CFrame +{selected['camera_cframe_offset']:#x}; "
              f"FOV +{selected['camera_fov_offset']:#x} radians -> degrees "
              f"(replaces report candidate {self.fov!r})", flush=True)
        return replace(self, camera_frame=selected["camera_cframe_offset"],
                       fov=selected["camera_fov_offset"], fov_unit="radians", camera_verified=True)

    @classmethod
    def from_report(cls, path: Path):
        report = json.loads(path.read_text(encoding="utf-8"))
        fields = report["resolved"]

        def value(name):
            result = fields[name]["value"]
            if type(result) is not int or not 0 <= result <= 0x10000:
                raise ValueError(f"invalid offset: {name}")
            return result

        if value("Instance.ChildrenIndirect") != 1 or value("Instance.ChildrenEnd") != 8:
            raise ValueError("the reader requires pointer-to-vector children with end delta 8")
        frame = value("Primitive.CFrame")
        camera_frame = value("Camera.CFrame")
        if value("Primitive.Position") != frame + 36 or value("Camera.Position") != camera_frame + 36:
            raise ValueError("CFrame report does not describe nine rotation floats then translation")
        static = report["evidence"]["static_geometry_accessors"]
        selected = static.get("selected")
        digest = static.get("binary_sha256", "")
        if not selected or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("report lacks getter-backed geometry and binary identity")
        primitive = value("BasePart.Primitive")
        if (selected["basepart_primitive_offset"] != primitive
                or selected["primitive_cframe_offset"] != frame):
            raise ValueError("static getter and reported geometry offsets disagree")
        return cls(value("Instance.Name"), value("Instance.Parent"), value("Instance.ChildrenStart"),
                   value("Player.ModelInstance"), primitive, frame, value("Workspace.CurrentCamera"),
                   camera_frame, value("Players.LocalPlayer") if "Players.LocalPlayer" in fields else None,
                   digest,
                   value("Camera.FieldOfView") if "Camera.FieldOfView" in fields else None)


@dataclass(frozen=True)
class Target:
    name: str
    position: tuple[float, float, float]
    is_local: bool = False


@dataclass(frozen=True)
class Frame:
    rotation: tuple[tuple[float, float, float], ...] | None
    position: tuple[float, float, float] | None
    targets: tuple[Target, ...]
    roster_count: int
    status: str
    fov: float | None = None  # camera-read candidate; None = unusable
    local_position: tuple[float, float, float] | None = None
    complete: bool = True  # False means a failed camera read, not a valid empty scene.
    camera_address: int | None = None
    roster: tuple[tuple[int, str], ...] = ()  # (address, display name) pairs


def decode_frame(raw: bytes):
    if len(raw) != 48:
        return None
    floats = struct.unpack("<12f", raw)
    if not prims.orthonormal3(floats[:9], tol=0.04):
        return None
    if not all(math.isfinite(v) and abs(v) <= 1e6 for v in floats[9:]):
        return None
    return (tuple(tuple(floats[row * 3:row * 3 + 3]) for row in range(3)), tuple(floats[9:]))


class ESPReader:
    def __init__(self, mem, model, layout, spec: OffsetSpec):
        if spec.fov_unit not in ("degrees", "radians"):
            raise ValueError("unsupported camera FOV storage unit")
        self.mem, self.model, self.spec = mem, model, spec
        # Cache object bindings only. Poses and ownership links are read anew
        # on every snapshot; respawns/replacements invalidate their bindings.
        self._body_bindings: dict[int, tuple[int, int, int]] = {}
        self.walker = Walker(mem, layout)
        self.root = layout.services.get("DataModel", 0)
        self.players = layout.services.get("Players", 0)
        self.workspace = layout.services.get("Workspace", 0)
        if not all((self.root, self.players, self.workspace)):
            raise RuntimeError("discovery did not recover DataModel, Players and Workspace")

    @classmethod
    def attach(cls, pid: int, spec: OffsetSpec, *, fresh=False):
        print(f"[esp] attaching read-only to pid {pid}; {'fresh' if fresh else 'cached'} discovery", flush=True)
        mem = MachProcess(pid)
        try:
            for bypass_cache in ((True,) if fresh else (False, True)):
                try:
                    options = {"cache_path": None} if bypass_cache else {}
                    # The reader requires RTTI. A name-only fallback cannot be
                    # used here and delayed every failed rejoin with another scan.
                    layout = solve_instance_layout(mem, list(mem.regions()), verbose=True,
                                                   rtti_only=True, **options)
                    model = layout.object_model
                    if model is None:
                        raise WalkError("ESP requires RTTI-backed root discovery")
                    if hashlib.sha256(model.mach.blob).hexdigest() != spec.binary_sha256:
                        raise RuntimeError("installed binary differs from offset report; generate a new report")
                    if (layout.name, layout.parent, layout.children, layout.stride, layout.children_kind) != (
                            spec.name, spec.parent, spec.children, 16, "ptr"):
                        raise RuntimeError("live discovered layout differs from offset report")
                    reader = cls._select_session(mem, model, layout, spec)
                    print(f"[esp] discovery complete: DataModel {reader.root:#x}", flush=True)
                    return reader
                except WalkError:
                    if bypass_cache:
                        raise
                    print("  · retrying discovery with a fresh object sweep", flush=True)
        except WalkError as exc:
            mem.close()
            candidates = find_roblox_candidates()
            detail = ", ".join(f"pid {p} ({rss >> 10} MB)" for p, rss in candidates[:4])
            raise RuntimeError(
                f"no loaded Roblox session on pid {pid} ({exc}). "
                f"Roblox processes: {detail or 'none'}; largest client is auto-picked."
            ) from exc
        except BaseException:
            mem.close()
            raise

    @classmethod
    def _select_session(cls, mem, model, layout, spec):
        """Bind services from ONE reciprocal root, never independently by size."""
        walker = Walker(mem, layout)
        ready = []
        roots = layout.root_candidates or (layout.services.get("DataModel", 0),)
        for root in roots[:256]:
            services = {"DataModel": root}
            for child in walker.children(root, limit=512):
                try:
                    ref = model.class_of(mem.u64(child))
                    if (ref is not None and ref.name in ("RBX::Players", "RBX::Workspace")
                            and mem.u64(child + spec.parent) == root):
                        services[ref.name.removeprefix("RBX::")] = child
                except MemoryFault:
                    continue
            if not all(services.get(key) for key in ("DataModel", "Players", "Workspace")):
                continue
            candidate = cls(mem, model, replace(layout, services=services), spec)
            try:
                frame = candidate.snapshot()
            except (RuntimeError, MemoryFault, OSError):
                continue
            if frame.complete and frame.fov is not None:
                ready.append(candidate)
        if len(ready) != 1:
            raise WalkError(f"{len(ready)} loaded reciprocal roots; waiting for one active game")
        return ready[0]

    def close(self):
        self.mem.close()

    def validate_session(self):
        if (self.klass(self.root) != "RBX::DataModel" or self.klass(self.players) != "RBX::Players"
                or self.klass(self.workspace) != "RBX::Workspace"):
            raise RuntimeError("root/service objects changed")
        children = set(self.children(self.root, 512))
        if any(service not in children or self.pointer(service + self.spec.parent) != self.root
               for service in (self.players, self.workspace)):
            raise RuntimeError("service tree detached from DataModel")

    def pointer(self, address):
        try:
            value = self.mem.u64(address)
        except MemoryFault:
            return 0
        return value if prims.plausible_ptr(value) else 0

    def klass(self, address):
        vptr = self.pointer(address)
        ref = self.model.class_of(vptr) if vptr else None
        return ref.name if ref else None

    def name(self, address):
        pointer = self.pointer(address + self.spec.name)
        if not pointer:
            return None
        try:
            raw = self.mem.read(pointer, 64)
        except MemoryFault:
            return None
        end = raw.find(b"\0")
        if end <= 0:
            return None
        text = raw[:end].decode("utf-8", "replace")
        return text if text.isprintable() else None

    def children(self, address, limit=128):
        return self.walker.children(address, limit=limit)

    def frame_at(self, address, offset):
        for _ in range(2):
            try:
                frame = decode_frame(self.mem.read(address + offset, 48))
            except MemoryFault:
                frame = None
            if frame is not None:
                return frame
        return None

    def _player_position(self, player_addr: int):
        """World position of a player's body (HRP -> Head -> torso chain),
        read through the getter-backed Primitive CFrame. Used for targets
        AND for the local player, whose position cross-checks the camera."""
        character = self.pointer(player_addr + self.spec.character)
        if not character or self.klass(character) not in ("RBX::ModelInstance", "RBX::Model"):
            self._body_bindings.pop(player_addr, None)
            return None
        if self.pointer(player_addr + self.spec.parent) != self.players:
            self._body_bindings.pop(player_addr, None)
            return None
        binding = self._body_bindings.get(player_addr)
        if binding is not None:
            owner, part, primitive = binding
            if (owner == character and self.pointer(part + self.spec.parent) == character
                    and self.klass(part) in ("RBX::Part", "RBX::MeshPart", "RBX::WedgePart")
                    and self.pointer(part + self.spec.primitive) == primitive
                    and self.klass(primitive) == "RBX::Primitive"):
                frame = self.frame_at(primitive, self.spec.primitive_frame)
                return frame[1] if frame is not None else None
            self._body_bindings.pop(player_addr, None)
        parts = {}
        for part in self.children(character, 128):
            name = self.name(part)
            if name in ("HumanoidRootPart", "Head", "UpperTorso", "Torso"):
                parts[name] = part
        for part_name in ("HumanoidRootPart", "Head", "UpperTorso", "Torso"):
            part = parts.get(part_name)
            if part is None:
                continue
            if self.klass(part) not in ("RBX::Part", "RBX::MeshPart", "RBX::WedgePart"):
                continue
            if self.pointer(part + self.spec.parent) != character:
                continue
            primitive = self.pointer(part + self.spec.primitive)
            if not primitive or self.klass(primitive) != "RBX::Primitive":
                continue
            frame = self.frame_at(primitive, self.spec.primitive_frame)
            if frame is not None:
                self._body_bindings[player_addr] = character, part, primitive
                return frame[1]
        return None

    def snapshot(self, show_local=False):
        self.validate_session()
        camera = self.pointer(self.workspace + self.spec.camera)
        if not camera or self.klass(camera) != "RBX::Camera":
            return Frame(None, None, (), 0, "CurrentCamera not resolved; drawing paused", complete=False)
        camera_frame = self.frame_at(camera, self.spec.camera_frame)
        if camera_frame is None:
            return Frame(None, None, (), 0, "Camera CFrame failed structural checks; drawing paused", complete=False)
        fov = None
        if self.spec.fov is not None:
            try:
                candidate = struct.unpack("<f", self.mem.read(camera + self.spec.fov, 4))[0]
            except MemoryFault:
                candidate = float("nan")
            degrees = math.degrees(candidate) if self.spec.fov_unit == "radians" else candidate
            if math.isfinite(degrees) and 1.0 < degrees < 179.0:
                fov = float(degrees)
            elif self.spec.fov and not getattr(self, "_fov_warned", False):
                self._fov_warned = True
                print(f"[esp] FOV candidate at Camera+{self.spec.fov:#x} read {candidate!r} "
                      f"{self.spec.fov_unit} (invalid after unit conversion) — falling back to --fov", flush=True)
        roster = [addr for addr in self.children(self.players, 128)
                   if self.klass(addr) == "RBX::Player"
                   and self.pointer(addr + self.spec.parent) == self.players]
        roster_set = set(roster)
        for stale_player in self._body_bindings.keys() - roster_set:
            del self._body_bindings[stale_player]
        local = self.pointer(self.players + self.spec.local_player) if self.spec.local_player is not None else 0
        local = local if local in roster else 0
        local_position = self._player_position(local) if local else None
        targets = []
        for player in roster:
            if player == local and not show_local:
                continue
            position = self._player_position(player)
            if position is not None:
                targets.append(Target(self.name(player) or f"Player {player:#x}", position, player == local))
        status = "Connected — macOS ARM64 external"
        if not local:
            status += "; local player unknown"
        elif local_position is None:
            status += "; YOUR character position unreadable — camera cross-check unavailable"
        if not targets:
            status += "; no readable target positions"
        roster_named = tuple((addr, self.name(addr) or f"Player {addr:#x}") for addr in roster)
        return Frame(camera_frame[0], camera_frame[1], tuple(targets), len(roster), status,
                     fov, local_position, complete=bool(local), camera_address=camera, roster=roster_named)
