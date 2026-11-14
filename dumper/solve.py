"""dumper.solve — recover the Instance layout without trusting any offset.

Primary route: RTTI. Every polymorphic object starts with a vtable pointer, and
every vtable carries a typeinfo record naming its class (`RBX::Workspace`,
`RBX::Humanoid`, ...). Sweep the heap once for pointers into the image's data
segments, resolve each unique vtable to a class name, and the object graph
falls out: instances of known classes, their `Name` string (`== class name` for
a service), and their child vector (elements must themselves be RTTI objects).

Fallback route: the original name-byte sweep, for builds that strip RTTI.
Nothing here reads a number from the seed table.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from collections import Counter, deque
from dataclasses import dataclass, field

from rbxl.memory import MemoryFault

from . import prims
from .rtti import ImageModel
from .scan import (CLIENT_IMAGE_PREFIX, collect_qwords, c_find_spans,
                   find_many, find_rtti_slots, heap_regions)

SERVICE_NAMES = ("Workspace", "Players", "Lighting", "Camera", "Terrain", "ReplicatedStorage")
NAME_CAP = 0x600
WINDOW = 0x1400
MAX_CHILD_SCAN = 200_000

# Service instances are named exactly after their class, which is what turns
# "where is Name?" into a self-labelled search instead of a guess.
SELF_NAMED = ("Workspace", "Players", "Lighting", "Camera", "Terrain", "StarterGui")


@dataclass
class InstanceLayout:
    name: int = -1
    children: int = -1
    children_end: int = -1
    stride: int = 16
    parent: int = -1
    name_kind: str = "sso"   # "sso" = std::string inline, "ptr" = pointer to it
    confidence: float = 0.0
    services: dict[str, int] = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)
    children_kind: str = "inline"  # "ptr" = instance slot -> vector container
    object_model: object | None = field(default=None, repr=False, compare=False)
    root_candidates: tuple[int, ...] = field(default=(), repr=False)

    @property
    def trusted(self) -> bool:
        return self.name >= 0 and self.children >= 0


class WalkError(Exception):
    pass


class ScanBudgetExceeded(WalkError):
    """A bounded discovery stage stopped; do not launch another broad scan."""


def module_span(regions) -> tuple[int, int]:
    """The client image's mapped range. Instance objects open with a vtable
    pointer into it; Luau string pools and Apple runtime data do not."""
    low = high = 0
    for start, size, path, _prot in regions:
        if not path:
            continue
        if not path.rsplit("/", 1)[-1].startswith(CLIENT_IMAGE_PREFIX):
            continue
        if low == 0 or start < low:
            low = start
        high = max(high, start + size)
    return low, high


def looks_like_instance(mem, span: tuple[int, int], obj: int) -> bool:
    try:
        head = mem.u64(obj)
    except MemoryFault:
        return False
    return span[0] <= head < span[1]


class Walker:
    """Reads names and children through a solved layout."""

    def __init__(self, mem, layout: InstanceLayout):
        self.mem = mem
        self.layout = layout
        self._names: dict[int, str] = {}

    def raw_name(self, inst: int) -> str | None:
        if inst <= 0:
            return None
        if self.layout.name_kind == "ptr":
            return self._name_behind_pointer(inst)
        try:
            raw = self.mem.read(inst + self.layout.name, 24)
        except MemoryFault:
            return None
        text = prims.decode_short_string(raw)
        if text is not None:
            return text
        target = prims.long_string_target(raw)
        if target is None:
            return None
        ptr, size = target
        try:
            return self.mem.read(ptr, size).decode("utf-8", "replace")
        except MemoryFault:
            return None

    def _name_behind_pointer(self, inst: int) -> str | None:
        """Names stored as shared_ptr<Name> / StringRef: one hop, then decode.

        Live 0.745 evidence: the pointer lands on bare NUL-terminated chars
        ("Players\0") with no size byte and no std::string header, so the
        printable-run case is load-bearing, not defensive."""
        try:
            pointer = self.mem.u64(inst + self.layout.name)
        except MemoryFault:
            return None
        if not prims.plausible_ptr(pointer):
            return None
        try:
            head = self.mem.read(pointer, 0x40)
        except MemoryFault:
            return None
        text = prims.decode_short_string(head[:24])
        if text is not None:
            return text
        cut = head.find(b"\0")
        if cut > 0 and all(32 <= b < 127 for b in head[:cut]):
            try:
                return head[:cut].decode("utf-8")
            except UnicodeDecodeError:
                pass
        target = prims.q(head, 0)
        if prims.plausible_ptr(target):
            try:
                blob = self.mem.read(target, 0x80)
            except MemoryFault:
                return None
            cut = blob.find(b"\0")
            if 0 < cut <= 0x80:
                try:
                    return blob[:cut].decode("utf-8")
                except UnicodeDecodeError:
                    return None
        return None

    def name(self, inst: int) -> str:
        cached = self._names.get(inst)
        if cached is None:
            cached = self.raw_name(inst) or ""
            self._names[inst] = cached
        return cached

    def children(self, inst: int, limit: int | None = None) -> list[int]:
        return _children_walkable(self.mem, self.layout.children, self.layout.stride,
                                  inst, limit=limit, storage=self.layout.children_kind)

    def find_child(self, inst: int, name: str) -> int | None:
        for child in self.children(inst):
            if self.name(child) == name:
                return child
        return None

    def parent_of(self, child: int) -> int:
        """Instance.Parent, discovered as a back-pointer to its own parent."""
        if self.layout.parent >= 0:
            try:
                return self.mem.u64(child + self.layout.parent)
            except MemoryFault:
                return 0
        return 0

    def window(self, inst: int, size: int = WINDOW) -> bytes:
        try:
            return self.mem.read(inst, size)
        except MemoryFault:
            return b""


# ---------------------------------------------------------------------------
# RTTI route
# ---------------------------------------------------------------------------
CACHE_PATH = os.path.join(tempfile.gettempdir(), "rbxl_rtti_cache.json")


def _load_object_cache(path: str, mem, model: ImageModel) -> dict | None:
    """Reuse a recent sweep, but only after re-reading every object's vptr.
    The client reallocates; a cache that cannot prove itself is dropped."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    if data.get("pid") != mem.pid or data.get("slide") != model.slide:
        return None
    objects: dict[int, object] = {}
    for addr_text, vtable_text in data.get("objects", []):
        addr = int(addr_text, 16)
        vtable = int(vtable_text, 16)
        ref = model.class_of(vtable)
        if ref is None:
            continue
        try:
            if mem.u64(addr) != vtable:
                continue
        except MemoryFault:
            continue
        objects[addr] = ref
    return objects or None


def _save_object_cache(path: str, mem, model: ImageModel, objects: dict):
    payload = {
        "pid": mem.pid,
        "slide": model.slide,
        "objects": [[hex(addr), hex(ref.vtable)] for addr, ref in objects.items()],
    }
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)
    except OSError:
        pass


def vtable_objects(mem, regions, model: ImageModel, verbose: bool = False,
                   cap: int = 400_000, cache_path: str | None = CACHE_PATH):
    """Return (objects: dict[addr -> ClassRef], census: Counter[class name]).

    One sweep. The vtable -> class map is memoised inside ImageModel, so the
    per-slot cost is a dict lookup and only the distinct vtable addresses pay
    the three reads.
    """
    objects: dict[int, object] = {}
    census: Counter = Counter()
    if cache_path:
        cached = _load_object_cache(cache_path, mem, model)
        if cached:
            for addr, ref in cached.items():
                objects[addr] = ref
                census[ref.name] += 1
            if verbose:
                print(f"  · cache hit: {len(objects)} objects revalidated by vptr")
            return objects, census
    reporter = (lambda total: print(f"  · swept {total / (1 << 30):.2f} GiB, "
                                    f"{len(objects)} objects, {len(census)} classes")
                ) if verbose else None

    def resolve(value: int) -> bool:
        ref = model.class_of(value)
        return ref is not None and "::" in ref.name

    _t0 = time.time()
    try:
        hits = c_find_spans(mem, model.data_spans)
        if verbose:
            print(f"  · native sweep: {len(hits)} candidate slots "
                  f"in {time.time() - _t0:.1f}s")
    except MemoryFault:
        if verbose:
            print("  · native sweeper unavailable, falling back to python sweep")
        hits = list(find_rtti_slots(mem, heap_regions(regions), model.data_spans,
                                    resolve, progress=reporter))
    for addr, value in hits:
        ref = model.class_of(value)
        if ref is None or "::" not in ref.name:
            continue
        objects[addr] = ref
        census[ref.name] += 1
        if len(objects) >= cap:
            break
    if cache_path:
        _save_object_cache(cache_path, mem, model, objects)
    if verbose:
        print(f"  · {len(objects)} RTTI objects across {len(census)} classes")
        for name, count in census.most_common(12):
            print(f"      {count:<8} {name}")
    return objects, census


def _read_prefix(mem, address: int, size: int, minimum: int = 24) -> bytes:
    """Read a bounded prefix without losing a small header to a large fault."""
    while size >= minimum:
        try:
            return mem.read(address, size)
        except MemoryFault:
            if size == minimum:
                break
            size = max(minimum, size // 2)
    return b""


def _normalize_service_candidates(mem, objects, model, limit=256, verbose=False):
    """Replace service subobject aliases with ABI-validated complete objects."""
    normalize = getattr(model, "complete_object", None)
    if not callable(normalize):
        return
    wanted = {"RBX::" + name for name in SELF_NAMED + ("DataModel",)}
    candidates = [(addr, ref) for addr, ref in objects.items() if ref.name in wanted][:limit]
    moved = rejected = 0
    for addr, ref in candidates:
        top = normalize(addr)
        if top is None:
            rejected += 1
            objects.pop(addr, None)
            continue
        if top != addr:
            moved += 1
            objects.pop(addr, None)
            objects[top] = ref
    if verbose:
        print(f"  · service bases: {len(candidates)} checked, {moved} adjusted, "
              f"{rejected} rejected", flush=True)


def _find_name_offset(mem, objects, model, verbose=False) -> tuple[int, str, list[str]]:
    direct: Counter = Counter()
    indirect: Counter = Counter()
    for key in SELF_NAMED:
        targets = [addr for addr, ref in objects.items() if ref.name.endswith("::" + key)]
        if not targets:
            continue
        for addr in targets[:6]:
            # The name scan needs only NAME_CAP plus the trailing string
            # bytes. Reading the default 0x1400 can cross a mapping boundary
            # even when the instance header itself is readable.
            window = _read_prefix(mem, addr, NAME_CAP + 24)
            if not window:
                if verbose:
                    print(f"  · name probe {key} {addr:#x}: header unreadable", flush=True)
                continue
            matched = False
            for off in range(0, min(NAME_CAP, len(window) - 23), 8):
                if prims.decode_short_string(window[off:off + 24]) == key:
                    direct[off] += 1
                    matched = True
                    break
            for off in range(0, min(NAME_CAP, len(window) - 7), 8):
                pointer = prims.q(window, off)
                if not prims.plausible_ptr(pointer):
                    continue
                target = _read_prefix(mem, pointer, 0x60, minimum=16)
                if target.startswith(key.encode() + b"\0") or prims.decode_short_string(target[:24]) == key:
                    indirect[off] += 1
                    matched = True
                    break
            if verbose and not matched:
                print(f"  · name probe {key} {addr:#x}: {len(window):#x} header bytes, "
                      "no exact self-name", flush=True)
    if direct:
        offset, hits = direct.most_common(1)[0]
        return offset, "sso", [f"{hits} self-named services carry Name inline at {offset:#x}"]
    if indirect:
        offset, hits = indirect.most_common(1)[0]
        return offset, "ptr", [f"{hits} self-named services carry Name behind a pointer at {offset:#x}"]
    raise WalkError("no self-named instance exposed a name, inline or indirect")


def _discover_named_services(mem, objects, model, limit: int = 128) -> dict:
    """Probe pointers in census objects for service instances missed by the sweep.

    Returned addresses are RTTI candidates, not proof of parentage. The name
    and child-vector solvers must still validate the resulting layout.
    """
    wanted = {"RBX::" + name for name in SELF_NAMED + ("DataModel",)}
    discovered = {}
    seen = set(objects)
    preferred = ("RBX::Player", "RBX::Workspace", "RBX::Lighting",
                 "RBX::Humanoid", "RBX::Part", "RBX::ModelInstance")
    by_class = {name: [] for name in preferred}
    for addr, ref in objects.items():
        if ref.name in by_class and len(by_class[ref.name]) < limit:
            by_class[ref.name].append(addr)
    anchors = []
    for name in preferred:
        anchors.extend(by_class[name][:max(1, limit // len(preferred))])
    if not anchors:
        anchors = list(objects)[:limit]
    queue = deque(anchors[:limit])
    scanned = set()
    started = time.monotonic()
    while queue:
        addr = queue.popleft()
        if time.monotonic() - started >= 15.0:
            raise ScanBudgetExceeded("service pointer probe time budget exhausted")
        if addr in scanned:
            continue
        if len(scanned) >= limit:
            break
        scanned.add(addr)
        try:
            head = mem.read(addr, 0x100)
        except MemoryFault:
            continue
        for off in range(0, len(head) - 7, 8):
            pointer = prims.q(head, off)
            if pointer in seen or not prims.plausible_ptr(pointer):
                continue
            seen.add(pointer)
            try:
                vptr = mem.u64(pointer)
            except MemoryFault:
                continue
            ref = model.class_of(vptr)
            if ref is not None and ref.name in wanted:
                normalize = getattr(model, "complete_object", None)
                if callable(normalize):
                    top = normalize(pointer)
                    if top is None:
                        continue
                    pointer = top
                    if pointer in objects or pointer in discovered:
                        continue
                    seen.add(pointer)
                discovered[pointer] = ref
                # Follow a small service frontier so an uncensused Workspace
                # can expose an uncensused DataModel without a heap resweep.
                queue.appendleft(pointer)
    return discovered


def _find_children(mem, objects, name_off: int, model, verbose: bool = False,
                   budget_seconds: float = 15.0) -> tuple[int, int, list[str]]:
    """Score bounded vector samples, reading each object header just once.

    At most 600 headers and 4096 distinct 256-byte vector samples are read.
    The time budget is checked between reads; it cannot interrupt a syscall.
    No votes are returned if the scan exhausts its budget.
    """
    del name_off, model  # Layout scoring here uses census membership only.
    started = time.monotonic()
    next_progress = started + 1.0
    sample_cache: dict[tuple[int, int], bytes] = {}
    votes: Counter = Counter()
    addresses = list(objects)[:600]
    if verbose:
        print(f"  · children scan: {len(addresses)} headers, "
              f"16-entry samples, {budget_seconds:g}s budget", flush=True)

    def check_budget():
        if time.monotonic() - started >= budget_seconds:
            raise ScanBudgetExceeded("children scan time budget exhausted; no layout accepted")

    for checked, addr in enumerate(addresses, 1):
        check_budget()
        try:
            header = mem.read(addr, NAME_CAP + 8)
        except MemoryFault:
            continue
        for off in range(0, min(NAME_CAP, len(header) - 15), 8):
            begin = prims.q(header, off)
            end = prims.q(header, off + 8)
            if not prims.plausible_ptr(begin) or not prims.plausible_ptr(end) or end <= begin:
                continue
            span = end - begin
            for stride in (16, 8):
                if span % stride or not 2 <= span // stride <= MAX_CHILD_SCAN:
                    continue
                count = min(span // stride, 16)
                key = (begin, count * stride)
                if key not in sample_cache:
                    check_budget()
                    if len(sample_cache) >= 4096:
                        raise ScanBudgetExceeded("children scan sample budget exhausted; no layout accepted")
                    try:
                        sample_cache[key] = mem.read(*key)
                    except MemoryFault:
                        sample_cache[key] = b""
                payload = sample_cache[key]
                if len(payload) != key[1]:
                    continue
                sample = [prims.q(payload, i * stride) for i in range(count)]
                if all(kid in objects for kid in sample):
                    votes[(off, stride)] += 1
        now = time.monotonic()
        if verbose and (now >= next_progress or checked == len(addresses)):
            print(f"  · children scan: {checked}/{len(addresses)} headers, "
                  f"{len(sample_cache)} samples, {now - started:.1f}s", flush=True)
            next_progress = now + 1.0
    check_budget()
    if not votes:
        return -1, 16, []
    ranked = votes.most_common(8)
    best_off, best_stride = ranked[0][0]
    evidence = [f"child vector {best_off:#x} stride {best_stride} "
                f"votes {ranked[0][1]}/{len(addresses)} objects (bounded samples)"]
    return best_off, best_stride, evidence


def _window(mem, addr: int, size: int = WINDOW) -> bytes:
    try:
        return mem.read(addr, size)
    except MemoryFault:
        return b"\0" * size


def _children_walkable(mem, children_off: int, stride: int, obj,
                       limit: int | None = None, storage: str = "inline") -> list[int]:
    """Resolve a vector to object pointers (stride 16 = shared_ptr: ptr first)."""
    try:
        container = obj + children_off
        if storage == "ptr":
            container = mem.u64(container)
            if not prims.plausible_ptr(container):
                return []
        raw = mem.read(container, 16)
    except MemoryFault:
        return []
    begin = prims.q(raw, 0)
    end = prims.q(raw, 8)
    if (not prims.plausible_ptr(begin) or end <= begin or stride not in (8, 16)
            or (end - begin) % stride):
        return []
    count = (end - begin) // stride
    if not 1 <= count <= MAX_CHILD_SCAN:
        return []
    if limit is not None:
        count = min(count, limit)
    try:
        blob = mem.read(begin, count * stride)
    except MemoryFault:
        return []
    if len(blob) != count * stride:
        return []
    out = []
    for i in range(count):
        child = prims.q(blob, i * stride)
        if prims.plausible_ptr(child):
            out.append(child)
    return out


def _find_indirect_children(mem, objects, model, name_off, name_kind,
                            verbose=False, budget_seconds=15.0):
    """Find pointer-to-vector layouts using reciprocal child back-pointers.

    This tests container structure, RTTI and readable names rather than any
    platform-specific offset. A candidate needs two distinct named children
    pointing back to the owner at the same unambiguous slot.
    """
    started = time.monotonic()
    next_progress = started + 1
    cache = {}
    probe_layout = InstanceLayout(name=name_off, name_kind=name_kind)
    names = Walker(mem, probe_layout)
    buckets = {}
    for addr, ref in objects.items():
        if ref.name.startswith("RBX::"):
            bucket = buckets.setdefault(ref.name, [])
            if len(bucket) < 4:
                bucket.append(addr)
    preferred = ["RBX::" + name for name in SELF_NAMED + ("DataModel", "Player", "Part")]
    classes = preferred + sorted(set(buckets) - set(preferred))
    anchors = [addr for name in classes for addr in buckets.get(name, [])][:64]
    votes = Counter()

    def read(addr, size):
        if time.monotonic() - started >= budget_seconds:
            raise ScanBudgetExceeded("indirect children scan time budget exhausted")
        key = (addr, size)
        if key not in cache:
            if len(cache) >= 4096:
                raise ScanBudgetExceeded("indirect children scan read budget exhausted")
            try:
                cache[key] = mem.read(addr, size)
            except MemoryFault:
                cache[key] = b""
        return cache[key]

    if verbose:
        print(f"  · indirect children scan: {len(anchors)} headers, "
              f"{budget_seconds:g}s budget", flush=True)
    for checked, owner in enumerate(anchors, 1):
        header = read(owner, 0x200)
        for off in range(0, len(header) - 7, 8):
            pointer = prims.q(header, off)
            if not prims.plausible_ptr(pointer) or pointer == owner:
                continue
            vector = read(pointer, 16)
            if len(vector) != 16:
                continue
            begin, end = prims.q(vector, 0), prims.q(vector, 8)
            if not prims.plausible_ptr(begin) or not prims.plausible_ptr(end) or end <= begin:
                continue
            for stride in (16, 8):
                span = end - begin
                if span % stride or not 2 <= span // stride <= MAX_CHILD_SCAN:
                    continue
                count = min(span // stride, 16)
                payload = read(begin, count * stride)
                if len(payload) != count * stride:
                    continue
                children = {prims.q(payload, i * stride) for i in range(count)}
                if len(children) < 2:
                    continue
                common = None
                for child in children:
                    if not prims.plausible_ptr(child) or child == owner:
                        common = set()
                        break
                    child_header = read(child, 0x200)
                    if len(child_header) < 8:
                        common = set()
                        break
                    ref = model.class_of(prims.q(child_header, 0))
                    if ref is None or not ref.name.startswith("RBX::") or not names.raw_name(child):
                        common = set()
                        break
                    parents = {slot for slot in range(0, len(child_header) - 7, 8)
                               if prims.q(child_header, slot) == owner}
                    common = parents if common is None else common & parents
                    if not common:
                        break
                if common and len(common) == 1:
                    votes[(off, stride, next(iter(common)))] += 1
        now = time.monotonic()
        if verbose and (now >= next_progress or checked == len(anchors)):
            print(f"  · indirect children scan: {checked}/{len(anchors)} headers, "
                  f"{len(cache)} reads, {now - started:.1f}s", flush=True)
            next_progress = now + 1
    if not votes:
        return None
    ranked = votes.most_common()
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return None  # Ambiguous layouts must not become offsets.
    (offset, stride, parent), count = ranked[0]
    return offset, stride, parent, [f"indirect child container {offset:#x}, stride {stride}, "
                                    f"reciprocal Parent {parent:#x}, votes {count}"]


def _recover_service_tree(mem, objects, model, layout, verbose=False,
                          budget_seconds=15.0) -> dict:
    """Recover a root through bounded object pointers, not census membership.

    Accept a DataModel only when its sampled children include Workspace and
    another service and at least two distinct services point back to it at
    the same offset. No seed offsets or instance-name equality is required.
    """
    started = time.monotonic()
    preferred = ("RBX::DataModel", "RBX::Lighting", "RBX::Players",
                 "RBX::Workspace", "RBX::Player", "RBX::Part")
    buckets = {name: [] for name in preferred}
    for addr, ref in objects.items():
        if ref.name in buckets and len(buckets[ref.name]) < 16:
            buckets[ref.name].append(addr)
    queue = [addr for name in preferred for addr in buckets[name]]
    seen = set()
    resolved = {}

    def check_budget():
        if time.monotonic() - started >= budget_seconds:
            raise ScanBudgetExceeded("service tree recovery budget exhausted; no root accepted")

    def resolve(addr):
        if addr not in resolved:
            check_budget()
            if len(resolved) >= 8192:
                raise ScanBudgetExceeded("service tree pointer budget exhausted; no root accepted")
            try:
                resolved[addr] = model.class_of(mem.u64(addr))
            except MemoryFault:
                resolved[addr] = None
        return resolved[addr]

    def validate_root(root):
        children = set(_children_walkable(mem, layout.children, layout.stride,
                                          root, limit=512, storage=layout.children_kind))
        services = {}
        parent_votes = {}
        for child in sorted(children):
            check_budget()
            ref = resolve(child)
            if ref is None or ref.name not in {"RBX::" + name for name in SERVICE_NAMES}:
                continue
            try:
                header = mem.read(child, NAME_CAP + 8)
            except MemoryFault:
                continue
            offsets = {off for off in range(0, len(header) - 7, 8)
                       if off != layout.children and prims.q(header, off) == root}
            if not offsets:
                continue
            services[ref.name.removeprefix("RBX::")] = child
            for off in offsets:
                parent_votes.setdefault(off, set()).add(child)
        if "Workspace" not in services or len(services) < 2:
            return None
        candidates = [off for off, children in parent_votes.items() if len(children) >= 2]
        if len(candidates) != 1:
            return None
        parent = candidates[0]
        # Every exported service must participate in this same parent edge.
        services = {name: addr for name, addr in services.items()
                    if addr in parent_votes[parent]}
        if "Workspace" not in services or len(services) < 2:
            return None
        layout.parent = parent
        services["DataModel"] = root
        layout.services.update(services)
        layout.evidence.append(f"RTTI DataModel {root:#x}: {len(services) - 1} services, "
                               f"reciprocal Parent {parent:#x}")
        if verbose:
            print(f"  · service tree: DataModel {root:#x}, Parent {parent:#x}, "
                  f"services {sorted(services)}", flush=True)
        return {addr: resolve(addr) for addr in services.values()}

    if verbose:
        print(f"  · service tree recovery: {len(queue)} anchors, "
              f"{budget_seconds:g}s budget", flush=True)
    # At most 128 headers and 8192 pointer targets, even if the graph cycles.
    for addr in queue:
        check_budget()
        if addr in seen:
            continue
        if len(seen) >= 128:
            break
        seen.add(addr)
        ref = resolve(addr)
        if ref is not None and ref.name == "RBX::DataModel":
            found = validate_root(addr)
            if found:
                return found
        try:
            header = mem.read(addr, 0x200)
        except MemoryFault:
            continue
        for off in range(0, len(header) - 7, 8):
            pointer = prims.q(header, off)
            if not prims.plausible_ptr(pointer) or pointer in seen:
                continue
            target = resolve(pointer)
            if target is not None and target.name in preferred[:4] and pointer not in queue:
                queue.append(pointer)
    if verbose:
        print(f"  · service tree recovery: no reciprocal root from {len(seen)} headers", flush=True)
    return {}


def _solve_via_rtti(mem, regions, verbose: bool = False,
                    cache_path: str | None = CACHE_PATH) -> InstanceLayout:
    model = ImageModel(mem, regions, verbose=verbose)
    if verbose:
        print(f"  · image {model.path.rsplit('/', 1)[-1]} slide {model.slide:#x}, "
              f"{len(model.data_spans)} data spans")
    objects, census = vtable_objects(mem, regions, model, verbose=verbose, cache_path=cache_path)
    if not objects:
        raise WalkError("no RTTI objects in the heap — vtables not resolvable")

    _normalize_service_candidates(mem, objects, model, verbose=verbose)
    discovered = _discover_named_services(mem, objects, model, limit=48)
    objects.update(discovered)
    if verbose:
        print(f"  · bounded pointer probe found {len(discovered)} service/root candidates", flush=True)
        for addr, ref in list(discovered.items())[:8]:
            print(f"      {addr:#x} {ref.name}", flush=True)
    try:
        name_off, name_kind, name_evidence = _find_name_offset(mem, objects, model, verbose=verbose)
    except WalkError:
        discovered = _discover_named_services(mem, objects, model)
        if verbose:
            print(f"  · bounded pointer probe found {len(discovered)} service candidates")
            for addr, ref in list(discovered.items())[:8]:
                print(f"      {addr:#x} {ref.name}")
        if not discovered:
            raise
        objects.update(discovered)
        name_off, name_kind, name_evidence = _find_name_offset(mem, objects, model, verbose=verbose)
    if verbose:
        print(f"  · name candidate {name_off:#x} ({name_kind}); scanning children", flush=True)
    indirect = _find_indirect_children(mem, objects, model, name_off, name_kind,
                                       verbose=verbose)
    parent = -1
    children_kind = "inline"
    if indirect is not None:
        children_off, stride, parent, child_evidence = indirect
        children_kind = "ptr"
    else:
        children_off, stride, child_evidence = _find_children(
            mem, objects, name_off, model, verbose=verbose)
    if children_off < 0:
        raise WalkError("no child vector whose elements are RTTI objects")

    layout = InstanceLayout(name=name_off, children=children_off,
                             children_end=children_off + 8, stride=stride,
                             name_kind=name_kind, children_kind=children_kind, parent=parent,
                             object_model=model)
    walker = Walker(mem, layout)
    if verbose:
        print(f"  · child-vector candidate {children_off:#x}, stride {stride}, "
              f"storage {children_kind}", flush=True)
    recovered = _recover_service_tree(mem, objects, model, layout, verbose=verbose)
    objects.update(recovered)

    # Score the layout end to end: a real child vector leads to objects that
    # have their own names and their own children.
    score = 0.0
    for addr, ref in objects.items():
        if not ref.name.endswith(("::Workspace", "::Players", "::DataModel", "::Lighting")):
            continue
        kids = walker.children(addr, limit=512)
        named = [kid for kid in kids if walker.raw_name(kid)]
        score += 1.0 + 2.0 * len(named)
        score += sum(1.0 for kid in named if walker.children(kid, limit=16))
    if score <= 0:
        raise WalkError("layout resolved but no service tree walked")

    layout.confidence = min(1.0, score / 60.0)
    layout.evidence.extend(name_evidence + child_evidence)
    layout.evidence.append(f"{len(objects)} RTTI objects, {len(census)} classes, score {score:.0f}")

    # Services are self-identifying: the RTTI class *is* the service name, so
    # the resolver hands the tree root straight to the deriver.
    for key in SELF_NAMED + ("DataModel",):
        candidates = [addr for addr, ref in objects.items() if ref.name.endswith("::" + key)]
        if not candidates:
            continue
        candidates.sort(key=lambda a: -len(walker.children(a, limit=512)))
        layout.services.setdefault(key, candidates[0])

    parent = _find_parent_offset(mem, layout, objects)
    if layout.parent < 0:
        layout.parent = parent
    if parent >= 0:
        layout.evidence.append(f"Parent back-pointer at {parent:#x}")
    layout.root_candidates = tuple(addr for addr, ref in objects.items()
                                   if ref.name == "RBX::DataModel")
    return layout


def _find_parent_offset(mem, layout: InstanceLayout, objects) -> int:
    votes: Counter = Counter()
    walker = Walker(mem, layout)
    for addr, ref in objects.items():
        if not ref.name.endswith(("::Workspace", "::Players")):
            continue
        for kid in walker.children(addr, limit=512):
            window = _window(mem, kid)
            for off, value in collect_qwords(window):
                if value == addr and off != layout.children:
                    votes[off] += 1
                    break
    return votes.most_common(1)[0][0] if votes else -1


# ---------------------------------------------------------------------------
# Fallback: name-byte sweep
# ---------------------------------------------------------------------------
def _vector_candidates(buf: bytes) -> list[tuple[int, int, int]]:
    """(begin_offset, stride, count) triples that could be a child vector."""
    found = []
    limit = min(len(buf) - 16, 0x1000)
    for off in range(0, limit, 8):
        begin = prims.q(buf, off)
        if not prims.plausible_ptr(begin):
            continue
        end = prims.q(buf, off + 8)
        if end <= begin:
            continue
        span = end - begin
        if span >= (1 << 22):
            continue
        for stride in (16, 8):
            if span % stride == 0:
                count = span // stride
                if 1 <= count <= MAX_CHILD_SCAN:
                    found.append((off, stride, count))
    return found


def _name_hits(mem, regions, names, max_occ: int = 512) -> dict[str, list[int]]:
    patterns = {name: prims.sso_pattern(name) for name in names}
    raw = find_many(mem, regions, list(patterns.values()), limit_per=max_occ)
    return {name: raw[pattern] for name, pattern in patterns.items()}


def _solve_via_names(mem, regions, names=SERVICE_NAMES, verbose=False) -> InstanceLayout:
    hits = _name_hits(mem, regions, names)
    occurrences = [(n, a) for n, addrs in hits.items() for a in addrs]
    if not occurrences:
        raise WalkError(
            "no service name strings found in the heap — is this really the "
            "Roblox client, and did the task port open?"
        )

    span = module_span(regions)
    if span[0] == 0:
        raise WalkError("client image not found in the region map — cannot anchor vtables")

    votes: dict[tuple[int, int, int], int] = {}
    for _name, addr in occurrences:
        for name_off in range(0, 0x800, 8):
            inst = addr - name_off
            if inst & 15 or not prims.plausible_ptr(inst):
                continue
            if not looks_like_instance(mem, span, inst):
                continue
            try:
                buf = mem.read(inst, WINDOW)
            except MemoryFault:
                continue
            for begin_off, stride, count in _vector_candidates(buf):
                if count < 2:
                    continue
                votes[(name_off, begin_off, stride)] = (
                    votes.get((name_off, begin_off, stride), 0) + 1
                )

    if not votes:
        raise WalkError("no child-vector layout matched any name offset")

    ranked = sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))[:1500]
    best_score = -1.0
    best_layout: InstanceLayout | None = None
    for (name_off, begin_off, stride), _votes_count in ranked:
        layout = InstanceLayout(name=name_off, children=begin_off,
                                children_end=begin_off + 8, stride=stride)
        walker = Walker(mem, layout)
        instances = sorted({addr - name_off for _n, addr in occurrences})
        score = 0.0
        named_children = 0
        for inst in instances:
            if not walker.raw_name(inst):
                continue
            kids = walker.children(inst)
            if not kids:
                continue
            valid = [kid for kid in kids
                     if looks_like_instance(mem, span, kid) and walker.raw_name(kid)]
            if not valid:
                continue
            named_children += len(valid)
            score += 1.0 + 2.0 * len(valid)
            score += sum(1.0 for kid in valid if walker.children(kid))
        if verbose:
            print(f"  candidate name={name_off:#x} children={begin_off:#x} "
                  f"stride={stride} named_children={named_children} score={score:.1f}")
        if score > best_score:
            best_score = score
            best_layout = layout

    if best_layout is None or best_score <= 0:
        raise WalkError("no layout hypothesis resolved children names — heap scan inconclusive")

    best_layout.confidence = min(1.0, best_score / (3.0 * max(1, len(occurrences))))
    best_layout.evidence.append(
        f"{len(occurrences)} name strings, {len(votes)} layout hypotheses, "
        f"winning score {best_score:.1f}"
    )
    return best_layout


def solve_instance_layout(mem, regions, names=SERVICE_NAMES, verbose=False,
                          cache_path: str | None = CACHE_PATH,
                          rtti_only: bool = False) -> InstanceLayout:
    try:
        return _solve_via_rtti(mem, regions, verbose=verbose, cache_path=cache_path)
    except ScanBudgetExceeded:
        raise
    except Exception as exc:  # noqa: BLE001 - any RTTI failure falls back to names
        if verbose:
            print(f"  · RTTI route failed: {exc}")
        if rtti_only:
            raise WalkError(f"RTTI discovery unavailable: {exc}") from exc
        layout = _solve_via_names(mem, regions, names, verbose=verbose)
        layout.evidence.append(f"RTTI route unusable: {exc}")
        return layout


def discover_parent_offset(mem, walker: Walker, parent: int, child: int, window: int = 0x1400) -> int:
    try:
        buf = mem.read(child, window)
    except MemoryFault:
        return -1
    needle = parent
    for off, value in collect_qwords(buf):
        if value == needle:
            return off
    return -1
