"""dumper.derive — walk the live object graph and recover the whole table.

Nothing here reads a number out of the previous dump except as a tie-breaker
hint. Every field is found by locating a structure and validating it against an
invariant that survives a build update: rotation matrices stay orthonormal,
child vectors stay contiguous, names stay libc++ strings, primitives keep a
position inside the world, humans keep a health pair.
"""

from __future__ import annotations

import math
import struct
import time
from dataclasses import dataclass, field

from rbxl.memory import MemoryFault

from . import prims
from .scan import collect_qwords, find_aligned_qword, find_many, iter_chunks
from .snapshots import bound_object_samples, summarize_primitive_samples
from .solve import SERVICE_NAMES, ScanBudgetExceeded, Walker, module_span, solve_instance_layout

WINDOW = 0x1400
BIG_WINDOW = 0x3000


@dataclass
class Finding:
    path: str
    value: int
    method: str
    confidence: float


@dataclass
class Report:
    findings: dict[str, Finding] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    layout: object | None = None
    module_base: int = 0
    datamodel: int = 0
    workspace: int = 0
    camera: int = 0
    players: int = 0
    evidence: dict[str, object] = field(default_factory=dict)

    def get(self, path: str) -> int | None:
        found = self.findings.get(path)
        return found.value if found else None

    def set(self, path: str, value: int | None, method: str, confidence: float = 0.9):
        if value is None or value < 0:
            return
        self.findings[path] = Finding(path, value, method, confidence)


def _float_at(buf: bytes, off: int) -> float:
    return struct.unpack_from("<f", buf, off)[0]


def _point(blob: bytes, off: int) -> tuple[float, float, float]:
    return struct.unpack_from("<3f", blob, off)


class Deriver:
    def __init__(self, mem, regions, verbose: bool = False,
                 renderer_budget: float = 15.0, skip_renderer: bool = False):
        if not math.isfinite(renderer_budget) or renderer_budget <= 0:
            raise ValueError("renderer_budget must be finite and positive")
        self.mem = mem
        self.regions = list(regions)
        self.verbose = verbose
        self.report = Report()
        self.walker: Walker | None = None
        self.primitive_samples: list[bytes] = []
        self.world_points: list[tuple[float, float, float]] = []
        self.camera_frame: tuple[tuple[float, ...], tuple[float, float, float]] | None = None
        self.camera_viewport: tuple[float, float] | None = None
        self.module_span: tuple[int, int] = (0, 0)
        self.object_model = None
        self._class_cache: dict[int, str | None] = {}
        self.renderer_budget = renderer_budget
        self.skip_renderer = skip_renderer
        self.geometry_accessors = None

    # -- plumbing ---------------------------------------------------------
    def log(self, message: str):
        if self.verbose:
            print(f"  · {message}")

    def win(self, addr: int, size: int = WINDOW) -> bytes:
        if not prims.plausible_ptr(addr):
            return b""
        span = self.module_span
        if span[0] <= addr < span[1]:
            return b""  # module image, not a heap object
        try:
            return self.mem.read(addr, size)
        except MemoryFault:
            return b""

    def fall(self, step: str):
        self.report.notes.append(step)

    def _class_name(self, addr: int) -> str | None:
        """Use the existing RTTI model; require a complete object, not an alias."""
        if self.object_model is None:
            return None
        if addr in self._class_cache:
            return self._class_cache[addr]
        self._class_cache[addr] = None
        try:
            ref = self.object_model.class_of(self.mem.u64(addr))
        except MemoryFault:
            return None
        if ref is None or self.object_model.complete_object(addr) != addr:
            return None
        self._class_cache[addr] = ref.name
        return ref.name

    def _unique_vote(self, votes: dict[int, int], label: str) -> int | None:
        if not votes:
            return None
        best = max(votes.values())
        winners = [off for off, count in votes.items() if count == best]
        if len(winners) != 1:
            self.fall(f"{label}: ambiguous candidates {', '.join(hex(off) for off in sorted(winners))}")
            return None
        return winners[0]

    # -- entry ------------------------------------------------------------
    def run(self) -> Report:
        self._class_cache.clear()
        for start, _size, path, _prot in self.regions:
            if path and path.rsplit("/", 1)[-1].startswith(("RobloxPlayer", "Roblox")):
                if self.report.module_base == 0 or start < self.report.module_base:
                    self.report.module_base = start

        self.module_span = module_span(self.regions)
        layout = solve_instance_layout(self.mem, self.regions, verbose=self.verbose)
        self.object_model = layout.object_model
        mach = getattr(self.object_model, "mach", None)
        if mach is not None:
            from .arm64_accessors import inspect_geometry_accessors

            accessors = inspect_geometry_accessors(mach)
            self.report.evidence["static_geometry_accessors"] = accessors
            self.geometry_accessors = accessors["selected"]
            if self.geometry_accessors is not None:
                self.log(f"static BasePart CFrame accessor: Primitive "
                         f"+{self.geometry_accessors['basepart_primitive_offset']:#x}, "
                         f"frame +{self.geometry_accessors['primitive_cframe_offset']:#x}")
        self.walker = Walker(self.mem, layout)
        self.report.layout = layout
        self.report.set("Instance.Name", layout.name, "heap name sweep + vector solve", layout.confidence)
        self.report.set("Instance.ChildrenStart", layout.children, "child vector solve", layout.confidence)
        self.report.set("Instance.ChildrenIndirect", int(layout.children_kind == "ptr"),
                        "1: ChildrenStart points to vector; 0: vector inline", layout.confidence)
        self.report.set(
            "Instance.ChildrenEnd",
            layout.children_end - layout.children,
            "child vector solve (delta from ChildrenStart)",
            layout.confidence,
        )

        services = self._service_instances()
        workspace = self._pick(services, "Workspace")
        if workspace is None:
            raise RuntimeError("Workspace absent from validated service tree and name candidates")
        self.report.workspace = workspace

        self._instance_parent(workspace)
        datamodel, dm_workspace_off = self._locate_datamodel(workspace, services)
        self.report.datamodel = datamodel
        self.report.set("DataModel.Workspace", dm_workspace_off, "parent whose child vector holds Workspace")

        self._camera(workspace)
        self._world(workspace)
        self._players(datamodel)
        self._visual_engine(datamodel)
        return self.report

    # -- services ---------------------------------------------------------
    def _name_occurrences(self) -> dict[str, list[int]]:
        patterns = {name: prims.sso_pattern(name) for name in SERVICE_NAMES}
        raw = find_many(self.mem, self.regions, list(patterns.values()), limit_per=512)
        return {name: raw[pattern] for name, pattern in patterns.items()}

    def _service_instances(self) -> dict[str, int]:
        assert self.walker is not None
        found: dict[str, int] = dict(self.walker.layout.services)
        if "Workspace" in found and "DataModel" in found:
            return found
        for name, addrs in self._name_occurrences().items():
            for addr in addrs:
                inst = addr - self.walker.layout.name
                if self.walker.name(inst) != name:
                    continue
                if len(self.walker.children(inst)) < 1:
                    continue
                found.setdefault(name, inst)
        return found

    @staticmethod
    def _pick(services: dict[str, int], name: str) -> int | None:
        value = services.get(name)
        return value if value else None

    # -- datamodel --------------------------------------------------------
    def _locate_datamodel(self, workspace: int, services: dict[str, int]) -> tuple[int, int | None]:
        assert self.walker is not None
        root = services.get("DataModel")
        if root and self.walker.layout.parent >= 0:
            if (self.walker.parent_of(workspace) == root
                    and workspace in self.walker.children(root)):
                self.report.set("Instance.Parent", self.walker.layout.parent,
                                "reciprocal service edges to RTTI DataModel")
                # A vector entry is not an inline DataModel.Workspace field.
                offsets = [off for off, value in collect_qwords(self.win(root))
                           if value == workspace]
                return root, offsets[0] if len(offsets) == 1 else None
        wanted = {"Workspace"}
        for extra in ("Players", "Lighting", "ReplicatedStorage"):
            if extra in services:
                wanted.add(extra)

        slots = list(find_aligned_qword(self.mem, self.regions, workspace, limit=4096))
        self.log(f"{len(slots)} slots point at Workspace")
        for slot in slots:
            for off in range(0, 0x1000, 8):
                candidate = slot - off
                if not prims.plausible_ptr(candidate) or candidate == workspace:
                    continue
                if not self.walker.raw_name(candidate):
                    continue
                kids = {self.walker.name(c) for c in self.walker.children(candidate)}
                if wanted <= kids:
                    self.report.datamodel = candidate
                    self.report.datamodel = candidate
                    self.report.set("Instance.Parent", self._parent_offset(candidate, workspace),
                                    "child back-pointer to DataModel")
                    return candidate, off
        raise RuntimeError("DataModel not found around the Workspace back-references")

    def _parent_offset(self, parent: int, child: int) -> int:
        buf = self.win(child)
        for off, value in collect_qwords(buf):
            if value == parent:
                self.log(f"Parent at {off:#x}")
                return off
        return -1

    def _instance_parent(self, workspace: int):
        del workspace  # parent offset is solved once the DataModel is known

    # -- camera -----------------------------------------------------------
    def _camera(self, workspace: int):
        assert self.walker is not None
        camera = self.walker.find_child(workspace, "Camera")
        if camera is None:
            self.fall("camera: no Camera child under Workspace")
            return
        self.report.camera = camera
        buf = self.win(workspace)
        for off, value in collect_qwords(buf):
            if value == camera:
                self.report.set("Workspace.CurrentCamera", off, "pointer to the Camera child")
                break

        cbuf = self.win(camera, WINDOW)
        cframe_off = self._rotation_block(cbuf)
        self.camera_frame = None
        if cframe_off >= 0:
            self.report.set("Camera.CFrame", cframe_off, "orthonormal 3x3 in the Camera instance", 0.98)
            self.report.set("Camera.Rotation", cframe_off, "same block as CFrame", 0.9)
            pos_off = cframe_off + 36
            if prims.vec3_sane(cbuf, pos_off):
                self.report.set("Camera.Position", pos_off, "translation after the CFrame rotation", 0.95)
                self.camera_frame = (prims.f32s(cbuf, cframe_off, 9), _point(cbuf, pos_off))

        for off in range(0, len(cbuf) - 4, 4):
            value = _float_at(cbuf, off)
            if 10.0 < value < 130.0 and (cframe_off < 0 or abs(off - cframe_off) > 48):
                self.report.set("Camera.FieldOfView", off, "single in-range float (10..130 deg)", 0.75)
                break

        best = (-1, -1.0)
        for off in range(0, len(cbuf) - 8, 4):
            w, h = struct.unpack_from("<2f", cbuf, off)
            if 240.0 < w < 9000.0 and 120.0 < h < 9000.0:
                ratio = w / h if h else 0
                if 0.4 < ratio < 3.0 and w * h > best[1]:
                    best = (off, w * h)
        if best[0] >= 0:
            self.report.set("Camera.ViewportSize", best[0], "largest sensible width/height pair", 0.8)
            self.camera_viewport = struct.unpack_from("<2f", cbuf, best[0])

    @staticmethod
    def _rotation_block(buf: bytes) -> int:
        for off in range(0, min(len(buf), 0x1000) - 36, 4):
            if prims.orthonormal3(prims.f32s(buf, off, 9)):
                return off
        return -1

    # -- world + primitives ----------------------------------------------
    def _world(self, workspace: int):
        assert self.walker is not None
        buf = self.win(workspace)
        best = None
        for off, value in collect_qwords(buf):
            if not prims.plausible_ptr(value) or value == workspace:
                continue
            if self.object_model is not None and self._class_name(value) != "RBX::World":
                continue
            world = self.win(value, 0x1400)
            for vec_off in range(0, min(len(world), 0x1200) - 16, 8):
                begin = prims.q(world, vec_off)
                end = prims.q(world, vec_off + 8)
                if not prims.plausible_ptr(begin) or end <= begin:
                    continue
                span = end - begin
                stride = 8 if span % 8 == 0 else (16 if span % 16 == 0 else 0)
                if not stride:
                    continue
                count = span // stride
                if not 8 <= count <= 500_000:
                    continue
                samples = []
                try:
                    blob = self.mem.read(begin, min(count, 24) * stride)
                except MemoryFault:
                    continue
                ok = 0
                for i in range(min(count, 24)):
                    ptr = prims.q(blob, i * stride)
                    if not prims.plausible_ptr(ptr):
                        continue
                    if self.object_model is not None and self._class_name(ptr) != "RBX::Primitive":
                        continue
                    sample = self.win(ptr, 0x300)
                    if len(sample) < 0x300:
                        continue
                    if self._primitive_like(sample):
                        ok += 1
                        samples.append(sample)
                if samples and ok / max(1, min(count, 24)) > 0.5:
                    score = ok
                    if best is None or score > best[0]:
                        best = (score, off, vec_off, samples)
        if best is None:
            self.fall("world: no primitive array under Workspace")
            return
        _score, world_off, prim_off, samples = best
        self.report.set("Workspace.World", world_off, "object holding the primitive array")
        self.report.set("World.Primitives", prim_off, "contiguous array of primitive pointers")
        self.primitive_samples = samples
        self._primitive_fields(samples)

    @staticmethod
    def _primitive_like(sample: bytes) -> bool:
        for off in range(0, 0x2C0, 4):
            try:
                vals = prims.f32s(sample, off, 3)
            except struct.error:
                return False
            if all(0.05 < v < 4096.0 for v in vals):
                return True
        return False

    def _primitive_fields(self, samples: list[bytes]):
        typed = self.object_model is not None
        if typed and len(samples) < 2:
            self.fall("primitive fields: need at least two distinct typed Primitive samples")
            return
        cframe_votes: dict[int, int] = {}
        for sample in samples:
            scan_end = min(len(sample), 0x800 if typed else 0x400)
            for off in range(0, scan_end - 48 + 1, 4):
                if prims.orthonormal3(prims.f32s(sample, off, 9)):
                    if len(sample) >= off + 48 and prims.vec3_sane(sample, off + 36):
                        cframe_votes[off] = cframe_votes.get(off, 0) + 1
                        if not typed:
                            break

        if typed:
            unanimous = {off: count for off, count in cframe_votes.items() if count == len(samples)}
            selected = None
            if self.geometry_accessors is not None:
                expected = self.geometry_accessors["primitive_cframe_offset"]
                if (self.report.get("BasePart.Primitive") ==
                        self.geometry_accessors["basepart_primitive_offset"] and expected in unanimous):
                    selected = expected
                else:
                    self.fall("Primitive.CFrame: static accessor and live field/sample evidence disagree")
            else:
                selected = self._unique_vote(unanimous, "Primitive.CFrame")
            cframe_off = selected if selected is not None else -1
            if cframe_off < 0:
                self.fall(f"Primitive.CFrame: withheld; {len(unanimous)} unanimous blocks "
                          f"across {len(samples)} typed samples")
        else:
            cframe_off = max(cframe_votes, key=cframe_votes.get) if cframe_votes else -1
        # Size cannot overlap the rotation/translation block it sits beside.
        blocked = range(cframe_off, cframe_off + 48) if cframe_off >= 0 else range(0, 0)
        size_votes: dict[int, int] = {}
        for sample in samples:
            for off in range(0, min(len(sample), 0x800 if typed else 0x400) - 12 + 1, 4):
                if any(start in blocked for start in range(off, off + 12)):
                    continue
                x, y, z = struct.unpack_from("<3f", sample, off)
                if 0.05 < x < 4096.0 and 0.05 < y < 4096.0 and 0.05 < z < 4096.0:
                    if max(x, y, z) > 0.3:
                        size_votes[off] = size_votes.get(off, 0) + 1
        if cframe_off >= 0:
            method = ("ARM64 BasePart CFrame getter chain + unanimous typed Primitive samples"
                      if typed and self.geometry_accessors is not None
                      else "orthonormal 3x3 across primitives")
            self.report.set("Primitive.CFrame", cframe_off, method, 0.97)
            self.report.set("Primitive.Orientation", cframe_off, "same block", 0.9)
            self.report.set("Primitive.Rotation", cframe_off, "same block", 0.9)
            pos_off = cframe_off + 36
            self.report.set("Primitive.Position", pos_off, "translation after CFrame", 0.97)
            self.world_points = [
                _point(s, pos_off) for s in samples if prims.vec3_sane(s, pos_off)
            ]
        if size_votes:
            if typed:
                unanimous = {off: count for off, count in size_votes.items() if count == len(samples)}
                size_off = self._unique_vote(unanimous, "Primitive.Size")
                if size_off is None or cframe_off < 0:
                    self.fall("Primitive.Size: withheld; no unique non-overlapping size block")
                    return
                votes = size_votes[size_off]
            else:
                size_off, votes = max(size_votes.items(), key=lambda kv: kv[1])
            ratio = votes / max(1, len(samples))
            if ratio >= 0.5:
                self.report.set("Primitive.Size", size_off,
                                f"positive float triple on {ratio:.0%} of primitives", min(0.95, ratio))

    # -- players ----------------------------------------------------------
    def _players(self, datamodel: int):
        assert self.walker is not None
        players = self.walker.find_child(datamodel, "Players")
        if players is None:
            self.fall("players: Services list has no Players child")
            return
        self.report.players = players

        child_ids = set(self.walker.children(players))
        if self.object_model is not None:
            child_ids = {addr for addr in child_ids if self._class_name(addr) == "RBX::Player"}
        model_off_votes: dict[int, int] = {}
        local_votes: dict[int, int] = {}
        health_votes: dict[int, int] = {}
        primary_votes: dict[int, int] = {}
        primitive_off_votes: dict[int, int] = {}
        layouts = self.walker.layout
        vec_offsets = range(layouts.children, layouts.children +
                            (8 if layouts.children_kind == "ptr" else 24), 8)
        seen_parts = set()
        typed_primitive_links: dict[int, dict[int, bytes]] = {}
        primitive_windows: dict[int, bytes] = {}

        pbuf = self.win(players, BIG_WINDOW)
        for off, value in collect_qwords(pbuf):
            if value != players and value in child_ids and off not in vec_offsets:
                local_votes[off] = local_votes.get(off, 0) + 1

        for player in child_ids:
            pdata = self.win(player, BIG_WINDOW)
            if not pdata:
                continue
            for off, value in collect_qwords(pdata):
                if (value == player or not prims.plausible_ptr(value)
                        or not self.walker.raw_name(value)):
                    continue
                if self.object_model is not None and self._class_name(value) not in (
                        "RBX::ModelInstance", "RBX::Model"):
                    continue
                character = value
                kids = self.walker.children(character)
                if not kids:
                    continue
                humanoid = None
                for kid in kids:
                    if self.object_model is not None:
                        if self._class_name(kid) == "RBX::Humanoid":
                            humanoid = kid
                            break
                        continue
                    pair = self._health_pair(self.win(kid, 0x800))
                    if pair is not None:
                        humanoid = kid
                        health_votes[pair] = health_votes.get(pair, 0) + 1
                        break
                if humanoid is None:
                    continue
                model_off_votes[off] = model_off_votes.get(off, 0) + 1
                kids_set = set(kids)
                if self.object_model is not None:
                    kids_set = {kid for kid in kids_set if self._class_name(kid) in (
                        "RBX::Part", "RBX::MeshPart", "RBX::WedgePart",
                        "RBX::CornerWedgePart", "RBX::UnionOperation")}
                for poff, pval in collect_qwords(self.win(character, 0x800)):
                    if pval in kids_set and poff not in vec_offsets:
                        primary_votes[poff] = primary_votes.get(poff, 0) + 1
                for part in sorted(kids_set)[:8]:
                    if part in seen_parts:
                        continue
                    seen_parts.add(part)
                    for boff, bval in collect_qwords(self.win(part, 0x800)):
                        if bval == part or not prims.plausible_ptr(bval):
                            continue
                        if self.object_model is not None and self._class_name(bval) != "RBX::Primitive":
                            continue
                        if self.object_model is not None:
                            if bval not in primitive_windows:
                                if len(primitive_windows) >= 32:
                                    continue
                                for size in (0x800, 0x400, 0x300):
                                    sample = self.win(bval, size)
                                    if len(sample) == size:
                                        break
                                primitive_windows[bval] = sample
                            sample = primitive_windows[bval]
                            if sample:
                                primitive_off_votes[boff] = primitive_off_votes.get(boff, 0) + 1
                                typed_primitive_links.setdefault(boff, {})[bval] = sample
                            continue
                        sample = self.win(bval, 0x300)
                        if len(sample) == 0x300 and self._primitive_like(sample):
                            primitive_off_votes[boff] = primitive_off_votes.get(boff, 0) + 1

        if local_votes:
            self.report.set("Players.LocalPlayer", self._unique_vote(local_votes, "LocalPlayer"),
                            "Players slot pointing at one of its own Player children")
        if model_off_votes:
            self.report.set("Player.ModelInstance", self._unique_vote(model_off_votes, "Character"),
                            "player slot pointing at a humanoid-bearing model")
        if health_votes:
            health_off = max(health_votes, key=health_votes.get)
            self.report.set("Humanoid.Health", health_off, "float pair health<=maxhealth, stable across players")
            self.report.set("Humanoid.MaxHealth", health_off + 32, "32-byte sibling of Health", 0.85)
        if primary_votes:
            self.report.set("Model.PrimaryPart", self._unique_vote(primary_votes, "PrimaryPart"),
                            "model slot pointing at one of its own parts")
        if primitive_off_votes:
            primitive_off = self._unique_vote(primitive_off_votes, "Primitive")
            self.report.set("BasePart.Primitive", primitive_off,
                            "part slot pointing at typed Primitive" if self.object_model is not None
                            else "part slot pointing at a primitive-shaped object")
            if primitive_off is not None and self.object_model is not None:
                links = list(typed_primitive_links.get(primitive_off, {}).items())[:16]
                self.log(f"primitive fields: {len(links)} distinct typed samples via "
                         f"BasePart+{primitive_off:#x} (no world-array scan)")
                self.report.evidence["primitive_samples"] = {
                    "part_primitive_offset": primitive_off,
                    "known_addresses": sorted(primitive_windows),
                    "samples": [{"address": addr, "bytes_hex": blob.hex()} for addr, blob in links],
                }
                self.report.evidence["primitive_analysis"] = summarize_primitive_samples(
                    links, known_addresses=primitive_windows)
                bounded = bound_object_samples(links, known_addresses=primitive_windows)
                self.primitive_samples = [blob for _, blob, _ in bounded]
                clipped = sum(len(blob) < len(raw) for (_, blob, _), (_, raw) in zip(bounded, links))
                self.log(f"primitive sample bounds: {clipped}/{len(links)} clipped at known next object")
                self._primitive_fields(self.primitive_samples)
        if self.object_model is not None:
            self.fall("Humanoid.Health/MaxHealth: withheld; float ranges alone do not identify health fields")

    @staticmethod
    def _health_pair(buf: bytes) -> int | None:
        if len(buf) < 0x400:
            return None
        for off in range(0, 0x300, 4):
            health = _float_at(buf, off)
            max_health = _float_at(buf, off + 32)
            if 0.0 <= health <= 10_000.0 and 1.0 <= max_health <= 10_000.0:
                if health <= max_health + 0.01 and health > 0.0:
                    return off
        return None

    # -- visual engine ----------------------------------------------------
    def _visual_engine(self, datamodel: int):
        if self.skip_renderer:
            self.fall("visual engine: skipped by request; no renderer offsets emitted")
            return
        started = time.monotonic()
        next_progress = started + 1.0
        if self.verbose:
            print(f"  · renderer scan: {self.renderer_budget:g}s budget", flush=True)

        def checkpoint():
            nonlocal next_progress
            now = time.monotonic()
            if now - started >= self.renderer_budget:
                raise ScanBudgetExceeded("renderer scan budget exhausted")
            if self.verbose and now >= next_progress:
                print(f"  · renderer scan: {now - started:.1f}s elapsed", flush=True)
                next_progress = now + 1.0

        try:
            self._scan_visual_engine(datamodel, checkpoint)
        except ScanBudgetExceeded:
            self.fall("visual engine: time budget exhausted; renderer offsets omitted, "
                      "other candidates retained")
            if self.verbose:
                print("  · renderer scan stopped at budget; writing other candidates", flush=True)

    def _scan_visual_engine(self, datamodel: int, checkpoint):
        checkpoint()
        if not self.report.module_base:
            self.fall("visual engine: main image not found in the region map")
            return

        slots = list(find_aligned_qword(self.mem, self.regions, datamodel,
                                        limit=8192, checkpoint=checkpoint))
        self.log(f"{len(slots)} slots hold the DataModel pointer")
        fake_candidates = set()
        for slot in slots:
            checkpoint()
            for off in range(0, 0x800, 8):
                candidate = slot - off
                if prims.plausible_ptr(candidate):
                    fake_candidates.add(candidate)
        if not fake_candidates:
            self.fall("visual engine: no FakeDataModel candidates")
            return

        module_regions = [
            (s, n, p, prot) for (s, n, p, prot) in self.regions
            if p and p.rsplit("/", 1)[-1].startswith(("RobloxPlayer", "Roblox"))
        ]
        data_spans = getattr(self.object_model, "data_spans", None)
        if data_spans is not None:
            # Engine globals belong to Mach-O data segments, not instruction
            # bytes in __TEXT. Intersect with the live map to preserve holes.
            module_regions = [
                (max(start, lo), min(start + size, hi) - max(start, lo), path, prot)
                for start, size, path, prot in module_regions
                for lo, hi in data_spans
                if max(start, lo) < min(start + size, hi)
            ]
        seen: set[int] = set()
        best: tuple[float, int, int, int, int] | None = None
        for base, data in iter_chunks(self.mem, module_regions, include_system=True,
                                      checkpoint=checkpoint):
            for off, value in collect_qwords(data):
                if off % 512 == 0:
                    checkpoint()
                if not prims.plausible_ptr(value) or value in seen or value == datamodel:
                    continue
                if self.module_span[0] <= value < self.module_span[1]:
                    continue
                seen.add(value)
                if self.object_model is not None and self._class_name(value) != "RBX::Graphics::VisualEngine":
                    continue
                ve = self.win(value, BIG_WINDOW)
                if len(ve) < 0x200:
                    continue
                for hit, ivalue in collect_qwords(ve):
                    if hit % 512 == 0:
                        checkpoint()
                    if ivalue not in fake_candidates:
                        continue
                    if self.object_model is not None and self._class_name(ivalue) != "RBX::DataModel":
                        continue
                    fbuf = self.win(ivalue, 0x800)
                    for rdm_off, rdm in collect_qwords(fbuf):
                        if rdm != datamodel:
                            continue
                        score, matrix_off = self._view_score(ve, checkpoint=checkpoint)
                        candidate = (score, matrix_off, base + off, hit, rdm_off)
                        if best is None or candidate[0] > best[0]:
                            best = candidate

        checkpoint()
        if best is None:
            self.fall("visual engine: no module slot chained to the DataModel")
            return

        score, matrix_off, slot, fakedm_off, rdm_off = best
        if matrix_off < 0:
            self.fall(f"visual engine: chain found but no view matrix ({score:.0%} of points)")
        self.report.set("VisualEngine.Pointer", slot - self.report.module_base,
                        "module slot holding the VisualEngine", 0.97)
        self.report.set("VisualEngine.FakeDataModel", fakedm_off, "VisualEngine slot to FakeDataModel", 0.97)
        self.report.set("FakeDataModel.RealDataModel", rdm_off, "FakeDataModel slot to DataModel", 0.97)
        if matrix_off >= 0:
            self.report.set("VisualEngine.ViewMatrix", matrix_off,
                            f"projects {score:.0%} of world points inside the frustum", min(0.97, score))

    def _camera_bits(self):
        """Camera position, forward/right/up candidates, fov and viewport."""
        if not self.report.camera or not self.camera_frame:
            return None
        rot, pos = self.camera_frame
        fov_off = self.report.get("Camera.FieldOfView")
        vp_off = self.report.get("Camera.ViewportSize")
        cbuf = self.win(self.report.camera, WINDOW)
        if fov_off is None or vp_off is None or len(cbuf) < vp_off + 8:
            return None
        fov = _float_at(cbuf, fov_off)
        width, height = struct.unpack_from("<2f", cbuf, vp_off)
        if not (1.0 < fov < 170.0) or width <= 1 or height <= 1:
            return None
        rows = [tuple(rot[0:3]), tuple(rot[3:6]), tuple(rot[6:9])]
        cols = [tuple(rot[0::3]), tuple(rot[1::3]), tuple(rot[2::3])]
        bases = []
        for right, up, back in (rows, cols):
            bases.append((right, up, tuple(-c for c in back)))
        return pos, fov, width, height, bases

    def _agreement(self, matrix: tuple[float, ...]) -> float | None:
        """How well a candidate matrix matches the camera's own projection."""
        bits = self._camera_bits()
        points = self.world_points[:64]
        if bits is None or len(points) < 6:
            return None
        pos, fov, width, height, bases = bits
        tan_half = math.tan(math.radians(fov) * 0.5)
        aspect = width / height
        best = 0.0
        for right, up, look in bases:
            hits = 0
            counted = 0
            for point in points:
                rel = (point[0] - pos[0], point[1] - pos[1], point[2] - pos[2])
                depth = sum(a * b for a, b in zip(rel, look))
                if depth <= 0.05:
                    continue
                sx = (sum(a * b for a, b in zip(rel, right)) / (depth * tan_half * aspect)) * 0.5 * width + 0.5 * width
                sy = (0.5 - sum(a * b for a, b in zip(rel, up)) / (depth * tan_half) * 0.5) * height
                ndc = prims.project_ndc(matrix, point)
                if ndc is None:
                    continue
                cx, cy, _cz, cw = ndc
                if cw <= 1e-3:
                    continue
                mx = (cx / cw * 0.5 + 0.5) * width
                my = (0.5 - cy / cw * 0.5) * height
                counted += 1
                if abs(mx - sx) < 8.0 and abs(my - sy) < 8.0:
                    hits += 1
            if counted >= 6:
                best = max(best, hits / counted)
        return best

    def _view_score(self, engine: bytes, checkpoint=None) -> tuple[float, int]:
        points = self.world_points[:64]
        if not points:
            return 0.0, -1
        camera = self.camera_frame[1] if self.camera_frame else None
        best = (0.0, -1)
        for off in range(0, min(len(engine), BIG_WINDOW) - 64, 4):
            if checkpoint is not None and off % 64 == 0:
                checkpoint()
            matrix = prims.f32s(engine, off, 16)
            if not all(abs(v) < 1e7 for v in matrix):
                continue
            # A perspective VP matrix has a unit-length w row: w == -z_view.
            wrow = math.sqrt(matrix[12] ** 2 + matrix[13] ** 2 + matrix[14] ** 2)
            if not 0.9 <= wrow <= 1.1:
                continue
            if camera is not None:
                # The eye point sits on the optical axis: clip x and y vanish.
                clip = prims.project_ndc(matrix, camera)
                if clip is None:
                    continue
                cx, cy, cz, cw = clip
                scale = max(1.0, abs(cw), abs(cz))
                if abs(cx) > 0.02 * scale or abs(cy) > 0.02 * scale:
                    continue

            hits = 0
            screen = set()
            for point in points:
                ndc = prims.project_ndc(matrix, point)
                if ndc is None:
                    continue
                cx, cy, _cz, cw = ndc
                if cw <= 1e-3:
                    continue
                nx, ny = cx / cw, cy / cw
                if abs(nx) < 1.5 and abs(ny) < 1.5:
                    hits += 1
                    screen.add((round(nx, 2), round(ny, 2)))
            if len(screen) < 4:
                continue
            score = hits / len(points)
            if score < 0.6:
                continue

            # Decisive test: the matrix must agree with the camera's own maths,
            # pixel for pixel, on the same points.
            agreement = self._agreement(matrix)
            if agreement is not None:
                if agreement < 0.7:
                    continue
                score = agreement
            if score > best[0]:
                best = (score, off)
        return best if best[0] >= 0.6 else (best[0], -1)
