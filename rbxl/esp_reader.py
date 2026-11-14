"""Read-only ESP snapshots using same-binary evidence and a reciprocal tree.

Discovery runs outside frame sampling. Projection always uses the actual
camera FOV; missing camera/local-player state marks a frame incomplete.
"""
from __future__ import annotations

import hashlib
import json
import math
import struct
import time
from dataclasses import dataclass, replace
from pathlib import Path

from dumper import prims
from dumper.macho import MachOError
from dumper.rtti import ImageModel
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
    # Optional same-binary findings; each feature that needs one is unavailable without it.
    humanoid_health: int | None = None
    humanoid_max_health: int | None = None
    player_team: int | None = None
    fast_slot: int | None = None   # module-relative global that leads to the DataModel
    fast_hops: tuple[int, ...] = ()  # pointer offsets followed from that global

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
        def optional(name):
            return value(name) if name in fields else None

        fast = report.get("fast_attach")
        if fast is not None:
            slot, hops = fast.get("slot"), fast.get("hops")
            if (type(slot) is not int or slot < 0 or slot % 8 or not isinstance(hops, list)
                    or not 1 <= len(hops) <= MAX_FAST_HOPS
                    or any(type(hop) is not int or not 0 <= hop <= 0x10000 or hop % 8 for hop in hops)):
                raise ValueError("malformed fast_attach chain")
        health = optional("Humanoid.Health"), optional("Humanoid.MaxHealth")
        if (health[0] is None) != (health[1] is None):
            raise ValueError("Humanoid.Health and Humanoid.MaxHealth must be recorded together")
        return cls(value("Instance.Name"), value("Instance.Parent"), value("Instance.ChildrenStart"),
                   value("Player.ModelInstance"), primitive, frame, value("Workspace.CurrentCamera"),
                   camera_frame, optional("Players.LocalPlayer"), digest, optional("Camera.FieldOfView"),
                   humanoid_health=health[0], humanoid_max_health=health[1],
                   player_team=optional("Player.Team"),
                   fast_slot=fast["slot"] if fast else None, fast_hops=tuple(fast["hops"]) if fast else ())


MAX_FAST_HOPS = 3
PART_CLASSES = ("RBX::Part", "RBX::MeshPart", "RBX::WedgePart")
ROOT_PARTS = ("HumanoidRootPart", "Head", "UpperTorso", "Torso")
# Extremities bound the box; the full set also draws the skeleton (R15 and R6 rigs).
EXTREMITY_PARTS = ("Head", "LeftHand", "RightHand", "LeftFoot", "RightFoot",
                   "Left Arm", "Right Arm", "Left Leg", "Right Leg")
SKELETON_PARTS = EXTREMITY_PARTS + ("UpperTorso", "LowerTorso", "Torso", "LeftUpperArm", "LeftLowerArm",
                                    "RightUpperArm", "RightLowerArm", "LeftUpperLeg", "LeftLowerLeg",
                                    "RightUpperLeg", "RightLowerLeg")
BODY_RESCAN_SECONDS = 1.0


Vector = tuple[float, float, float]


@dataclass(frozen=True)
class Target:
    name: str
    position: Vector
    is_local: bool = False
    address: int = 0
    parts: tuple[tuple[str, Vector], ...] = ()
    health: float | None = None
    max_health: float | None = None
    team: int = 0  # Team instance address; 0 = no team or offset unavailable


@dataclass
class _Body:
    character: int
    root: tuple[int, int]                  # (part, primitive)
    parts: tuple[tuple[str, int], ...]     # (name, primitive)
    humanoid: int
    scanned: float


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
    local_team: int = 0


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
        self._bodies: dict[int, _Body] = {}
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
            if spec.fast_slot is not None:
                try:
                    reader = cls._fast_attach(mem, spec)
                    print(f"[esp] fast attach: DataModel {reader.root:#x} via the profile's global chain", flush=True)
                    return reader
                except (WalkError, MemoryFault, MachOError) as exc:
                    # The chain is a profile shortcut; the sweep remains the source of truth.
                    print(f"[esp] fast attach unavailable ({exc}); running full discovery", flush=True)
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
    def _fast_attach(cls, mem, spec):
        """Module global -> pointer hops -> DataModel: a few reads, no heap sweep."""
        base = mem.main_image_base()
        if base is None:
            raise WalkError("client image is not mapped")
        root = mem.u64(base + spec.fast_slot)
        for hop in spec.fast_hops:
            if not prims.plausible_ptr(root):
                raise WalkError("fast-attach chain broke before the DataModel")
            root = mem.u64(root + hop)
        if not prims.plausible_ptr(root):
            raise WalkError("chain did not reach a DataModel pointer")
        model = ImageModel(mem, list(mem.regions()))
        if hashlib.sha256(model.mach.blob).hexdigest() != spec.binary_sha256:
            raise RuntimeError("installed binary differs from offset report; generate a new report")
        ref = model.class_of(mem.u64(root))
        if ref is None or ref.name != "RBX::DataModel":
            raise WalkError("chain target is not a DataModel (game still loading?)")
        layout = InstanceLayout(name=spec.name, children=spec.children, children_end=spec.children + 8,
                                stride=16, parent=spec.parent, name_kind="ptr", children_kind="ptr",
                                object_model=model, root_candidates=(root,))
        return cls._select_session(mem, model, layout, spec)

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

    def _scan_body(self, character, now):
        """Bind a character's parts once; snapshots then read only their poses."""
        root, parts, humanoid = {}, [], 0
        for child in self.children(character, 128):
            if self.pointer(child + self.spec.parent) != character:
                continue
            kind = self.klass(child)
            if kind == "RBX::Humanoid":
                humanoid = child
                continue
            if kind not in PART_CLASSES:
                continue
            name = self.name(child)
            primitive = self.pointer(child + self.spec.primitive)
            if not name or not primitive or self.klass(primitive) != "RBX::Primitive":
                continue
            if name in ROOT_PARTS:
                root[name] = (child, primitive)
            if name in SKELETON_PARTS:
                parts.append((name, primitive))
        chosen = next((root[name] for name in ROOT_PARTS if name in root), None)
        if chosen is None:
            return None
        return _Body(character, chosen, tuple(parts), humanoid, now)

    def _body(self, player_addr, now):
        character = self.pointer(player_addr + self.spec.character)
        if (not character or self.klass(character) not in ("RBX::ModelInstance", "RBX::Model")
                or self.pointer(player_addr + self.spec.parent) != self.players):
            self._bodies.pop(player_addr, None)
            return None
        body = self._bodies.get(player_addr)
        part, primitive = body.root if body else (0, 0)
        # Respawns replace the character; the root binding is rechecked every frame.
        if (body is None or body.character != character or now - body.scanned >= BODY_RESCAN_SECONDS
                or self.pointer(part + self.spec.parent) != character
                or self.pointer(part + self.spec.primitive) != primitive
                or self.klass(primitive) != "RBX::Primitive"):
            body = self._scan_body(character, now)
            if body is None:
                self._bodies.pop(player_addr, None)
                return None
            self._bodies[player_addr] = body
        return body

    def _read_target(self, player_addr, now, wanted):
        """World pose of a player's body plus the requested parts, health and team."""
        body = self._body(player_addr, now)
        if body is None:
            return None
        frame = self.frame_at(body.root[1], self.spec.primitive_frame)
        if frame is None:
            return None
        parts = []
        for name, primitive in body.parts:
            if name in wanted and (pose := self.frame_at(primitive, self.spec.primitive_frame)) is not None:
                parts.append((name, pose[1]))
        health = max_health = None
        if self.spec.humanoid_health is not None and body.humanoid:
            try:
                health, max_health = (struct.unpack("<f", self.mem.read(body.humanoid + offset, 4))[0]
                                      for offset in (self.spec.humanoid_health, self.spec.humanoid_max_health))
            except MemoryFault:
                health = max_health = None
            if not (math.isfinite(health or math.nan) and math.isfinite(max_health or math.nan)
                    and 0 < max_health <= 1e6):
                health = max_health = None
        return frame[1], tuple(parts), health, max_health, self.team(player_addr)

    def team(self, player_addr):
        if self.spec.player_team is None:
            return 0
        team = self.pointer(player_addr + self.spec.player_team)
        return team if team and self.klass(team) == "RBX::Team" else 0
    def snapshot(self, show_local=False, skeleton=False):
        self.validate_session()
        now = time.monotonic()
        wanted = SKELETON_PARTS if skeleton else EXTREMITY_PARTS
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
        for stale_player in self._bodies.keys() - roster_set:
            del self._bodies[stale_player]
        local = self.pointer(self.players + self.spec.local_player) if self.spec.local_player is not None else 0
        local = local if local in roster else 0
        local_read = self._read_target(local, now, ()) if local else None
        local_position = local_read[0] if local_read else None
        targets = []
        for player in roster:
            if player == local and not show_local:
                continue
            read = local_read if player == local else self._read_target(player, now, wanted)
            if read is not None:
                position, parts, health, max_health, team = read
                targets.append(Target(self.name(player) or f"Player {player:#x}", position, player == local,
                                      player, parts, health, max_health, team))
        status = "Connected — macOS ARM64 external"
        if not local:
            status += "; local player unknown"
        elif local_position is None:
            status += "; YOUR character position unreadable — camera cross-check unavailable"
        if not targets:
            status += "; no readable target positions"
        roster_named = tuple((addr, self.name(addr) or f"Player {addr:#x}") for addr in roster)
        return Frame(camera_frame[0], camera_frame[1], tuple(targets), len(roster), status,
                     fov, local_position, complete=bool(local), camera_address=camera, roster=roster_named,
                     local_team=self.team(local) if local else 0)
