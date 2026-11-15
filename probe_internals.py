#!/usr/bin/env python3
"""Find engine internals that have no reflected property: TaskScheduler, its jobs,
the job and FakeDataModel links to the DataModel, and the VisualEngine view matrix.

    sudo .venv/bin/python probe_internals.py      # in any game, camera not moving

Read-only. Prints what it finds; offsets that come out unique are recorded in the
matching profile (TaskScheduler.*, Job.*, FakeDataModel.*, VisualEngine.*).
"""
from __future__ import annotations

from collections import Counter, defaultdict
import json
import math
import struct
import sys

from dumper import prims
from dumper.scan import c_find_spans
from dumper.solve import vtable_objects
from rbxl.esp_reader import ESPReader, OffsetSpec
from rbxl.memory import MemoryFault, find_roblox_pid
from rbxl.profiles import select_profile, write_json
from verify_offsets import ancestors

WINDOW = 0x800
JOB_WINDOW = 0x400
ENGINE_WINDOW = 0x1000
MIN_JOBS, MAX_JOBS = 4, 512


def window(reader, address, size):
    while size >= 0x40:
        try:
            return reader.mem.read(address, size)
        except MemoryFault:
            size //= 2
    return b""


def qwords(raw):
    return [(offset, struct.unpack_from("<Q", raw, offset)[0]) for offset in range(0, len(raw) - 7, 8)]


def text_at(reader, raw, offset):
    """A printable std::string (libc++, short or long) stored at raw[offset:offset+24]."""
    chunk = raw[offset:offset + 24]
    if len(chunk) < 24:
        return None
    if prims.is_long_string(chunk):
        target = prims.long_string_target(chunk)
        if not target or not 0 < target[1] < 128:
            return None
        try:
            value = reader.mem.read(target[0], target[1]).decode("ascii")
        except (MemoryFault, UnicodeDecodeError):
            return None
    else:
        value = prims.decode_short_string(chunk)
    return value if value and value.isprintable() and any(c.isalpha() for c in value) else None


def module_slots(reader, target):
    """Module-relative offsets of globals in the client's data segments that hold `target`."""
    base = reader.mem.main_image_base()
    needle = struct.pack("<Q", target)
    slots = []
    for low, high in reader.model.data_spans:
        raw = reader.model.read(low, high - low)
        index = raw.find(needle)
        while index >= 0:
            if index % 8 == 0:
                slots.append(low + index - base)
            index = raw.find(needle, index + 1)
    return slots


def job_vectors(reader, scheduler, jobs_known):
    """(offset, jobs) for vectors in an object whose 16-byte entries point at known jobs."""
    raw = window(reader, scheduler, WINDOW)
    found = []
    for offset, begin in qwords(raw):
        end = struct.unpack_from("<Q", raw, offset + 8)[0] if offset + 16 <= len(raw) else 0
        if not prims.plausible_ptr(begin) or end <= begin or (end - begin) % 16:
            continue
        count = (end - begin) // 16
        if not MIN_JOBS <= count <= MAX_JOBS:
            continue
        try:
            entries = [struct.unpack_from("<Q", reader.mem.read(begin, count * 16), index * 16)[0] for index in range(count)]
        except MemoryFault:
            continue
        typed = [entry for entry in entries if entry in jobs_known]
        if len(typed) >= max(MIN_JOBS, count * 3 // 4):
            found.append((offset, entries))
    return found


def references(reader, regions, values):
    """{value: [addresses holding it]} across writable heap memory, via the native sweeper."""
    del regions  # the native sweeper walks the task's writable anonymous memory itself
    found = defaultdict(list)
    wanted = set(values)
    spans = sorted((value, value + 1) for value in wanted)
    for address, value in c_find_spans(reader.mem, spans):
        if value in wanted:
            found[value].append(address)
    return found


def job_storage(reader, regions, jobs_known):
    """Heap addresses where several job pointers sit together: the job list's storage."""
    holders = references(reader, regions, jobs_known)
    addresses = sorted(address for values in holders.values() for address in values)
    clusters, current = [], []
    for address in addresses:
        if current and address - current[-1] > 0x40:
            clusters.append(current)
            current = []
        current.append(address)
    clusters.append(current)
    return [cluster for cluster in clusters if len(cluster) >= MIN_JOBS]


def job_name_offset(reader, jobs):
    """Offset where most jobs hold a printable name string."""
    votes, names = Counter(), defaultdict(dict)
    for job in jobs:
        raw = window(reader, job, JOB_WINDOW)
        for offset in range(0, len(raw) - 23, 8):
            name = text_at(reader, raw, offset)
            if name:
                votes[offset] += 1
                names[offset][job] = name
    if not votes:
        return None, {}
    offset, hits = votes.most_common(1)[0]
    return (offset, names[offset]) if hits >= len(jobs) * 3 // 4 else (None, {})


def view_score(matrix, camera, rotation, row_major):
    """How well a 4x4 matrix projects points in front of the camera to the screen centre."""
    m = [matrix[i * 4:(i + 1) * 4] for i in range(4)] if row_major else [matrix[i::4] for i in range(4)]
    forward = [-rotation[0][2], -rotation[1][2], -rotation[2][2]]
    hits = 0
    for distance in (5.0, 20.0, 80.0):
        point = [camera[i] + forward[i] * distance for i in range(3)] + [1.0]
        clip = [sum(m[r][c] * point[c] for c in range(4)) for r in range(4)]
        if clip[3] <= 0.01:
            return 0
        x, y = clip[0] / clip[3], clip[1] / clip[3]
        hits += abs(x) < 0.05 and abs(y) < 0.05
    return hits


def view_matrix_offset(reader, engine, camera, rotation):
    raw = window(reader, engine, ENGINE_WINDOW)
    best = []
    for offset in range(0, len(raw) - 63, 4):
        matrix = struct.unpack_from("<16f", raw, offset)
        if not all(math.isfinite(v) and abs(v) < 1e7 for v in matrix):
            continue
        for row_major in (True, False):
            if view_score(matrix, camera, rotation, row_major) == 3:
                best.append((offset, "row-major" if row_major else "column-major"))
    return best


def main():
    pid = find_roblox_pid()
    if pid is None:
        raise RuntimeError("Roblox is not running; join a game first")
    profile = select_profile()
    spec = OffsetSpec.from_report(profile / "offsets.json").with_camera_evidence(profile / "camera.json")
    reader = ESPReader.attach(pid, spec)
    found = {}
    try:
        regions = list(reader.mem.regions())
        # Fresh sweep: a cached object list can be a small stale subset.
        objects, census = vtable_objects(reader.mem, regions, reader.model, verbose=True, cache_path=None)
        lineage, cache = {}, {}
        for address, ref in objects.items():
            lineage[address] = ancestors(reader, ref.typeinfo, cache)
        jobs_known = {address for address, names in lineage.items() if "TaskScheduler::Job" in names}
        job_classes = Counter(objects[address].name for address in jobs_known)
        print(f"[internals] {len(jobs_known)} live TaskScheduler::Job objects in {len(job_classes)} classes; "
              f"e.g. {job_classes.most_common(8)}")
        for name in ("RBX::Graphics::VisualEngine", "RBX::Graphics::RenderView", "RBX::DataModel"):
            print(f"[internals] {name}: {census.get(name, 0)} live")

        # TaskScheduler has no RTTI of its own. Work backwards: heap storage holding several
        # job pointers is the job list; whatever points at its start is the scheduler.
        storages = job_storage(reader, regions, jobs_known)
        print(f"[internals] job-list storage candidates: {[(hex(c[0]), len(c), hex(c[1] - c[0]) if len(c) > 1 else '-') for c in storages]}")
        # The cluster can start mid-list (unclassified or empty entries before it): look for
        # pointers to any 16-byte slot up to 64 entries before it.
        starts = {cluster[0] - 16 * back: cluster for cluster in storages for back in range(0, 64)}
        owners = references(reader, regions, list(starts))
        # A static TaskScheduler lives in the client's own data segment, which the heap sweeper skips.
        base = reader.mem.main_image_base()
        for start, cluster in sorted(starts.items()):
            for slot in module_slots(reader, start):
                end = reader.mem.u64(base + slot + 8)
                entries = (end - start) // 16 if end > start and (end - start) % 16 == 0 else None
                print(f"[internals]   list begin {start:#x} ({(cluster[0] - start) // 16} entries before the cluster) "
                      f"held by module global +{slot:#x}; end {end:#x} ({entries} entries)")
        for start, holders in sorted(owners.items()):
            cluster = starts[start]
            for holder in holders:
                end = reader.mem.u64(holder + 8)
                entries = (end - start) // 16 if end > start and (end - start) % 16 == 0 else None
                print(f"[internals]   list begin {start:#x} ({(cluster[0] - start) // 16} entries before the cluster) "
                      f"<- held at {holder:#x}; end {end:#x} ({entries} entries)")
                for back in range(0, WINDOW, 8):
                    slots = module_slots(reader, holder - back)
                    if slots:
                        print(f"[internals]     global(s) {[hex(g) for g in slots]} -> object {holder - back:#x}, "
                              f"list at +{back:#x}")
                        if len(owners) == 1 and len(holders) == 1 and len(slots) == 1 and entries:
                            found["TaskScheduler.Pointer"] = slots[0]
                            found["TaskScheduler.JobStart"], found["TaskScheduler.JobEnd"] = back, back + 8
                        break

        jobs = sorted(jobs_known)
        # Base-class Job fields: the name string and the DataModel pointer every job carries.
        names, models = Counter(), Counter()
        for job in jobs:
            raw = window(reader, job, JOB_WINDOW)
            for offset in range(0, len(raw) - 23, 8):
                if text_at(reader, raw, offset) and len(text_at(reader, raw, offset)) > 3:
                    names[offset] += 1
            for offset, value in qwords(raw):
                if value in objects and objects[value].name == "RBX::DataModel":
                    models[(offset, reader.root - value)] += 1
        name_offset, name_hits = names.most_common(1)[0] if names else (None, 0)
        (model_offset, delta), model_hits = models.most_common(1)[0] if models else ((None, None), 0)
        print(f"[internals] Job name: +{name_offset:#x} in {name_hits}/{len(jobs)} jobs; "
              f"Job DataModel: +{model_offset:#x} -> root - {delta:#x} in {model_hits}/{len(jobs)} jobs")
        if name_offset is not None and name_hits >= len(jobs) // 3:
            found["Job.Name"] = name_offset
        if model_offset is not None and model_hits >= len(jobs) * 2 // 3:
            found["Job.DataModel"] = model_offset
            found["DataModel.InstanceFromJob"] = delta
        for job in jobs:
            raw = window(reader, job, JOB_WINDOW)
            label = text_at(reader, raw, name_offset) if name_offset is not None else None
            print(f"[internals]   {objects[job].name:48} name {label!r}")

        graphics = sorted((name, count) for name, count in census.items() if "Graphics" in name)
        print(f"[internals] Graphics classes live: {graphics[:25]}")

        # FakeDataModel: another DataModel-class object that points at the real one.
        fakes = []
        for address, ref in objects.items():
            # Skip the real DataModel's own subobjects: its self pointer is not a fake.
            if ref.name == "RBX::DataModel" and abs(address - reader.root) > 0x1000:
                links = [o for o, v in qwords(window(reader, address, WINDOW)) if v == reader.root]
                if links:
                    fakes.append((address, links))
        print(f"[internals] FakeDataModel candidates: {[(hex(a), [hex(o) for o in l]) for a, l in fakes]}")
        if len(fakes) == 1 and len(fakes[0][1]) == 1:
            found["FakeDataModel.RealDataModel"] = fakes[0][1][0]

        # VisualEngine view matrix, checked against the live camera.
        camera = reader.pointer(reader.workspace + spec.camera)
        frame = reader.frame_at(camera, spec.camera_frame) if camera else None
        engines = [a for a, ref in objects.items() if ref.name == "RBX::Graphics::VisualEngine"]
        for view in [a for a, ref in objects.items() if ref.name == "RBX::Graphics::RenderView"]:
            links = [o for o, v in qwords(window(reader, view, WINDOW)) if v in engines]
            print(f"[internals] RenderView {view:#x}: VisualEngine@{[hex(o) for o in links]}")
            if len(links) == 1:
                found["RenderView.VisualEngine"] = links[0]
        print(f"[internals] VisualEngine objects: {[hex(a) for a in engines]}")
        if frame is not None:
            rotation, position = frame
            for engine in engines:
                matrices = view_matrix_offset(reader, engine, position, rotation)
                print(f"[internals]   {engine:#x}: view matrix candidates {[(hex(o), k) for o, k in matrices]}")
                if len(matrices) == 1:
                    found["VisualEngine.ViewMatrix"] = matrices[0][0]
                slots = module_slots(reader, engine)
                print(f"[internals]   {engine:#x}: module globals {[hex(s) for s in slots]}")
                if len(engines) == 1 and len(slots) == 1:
                    found["VisualEngine.Pointer"] = slots[0]
    finally:
        reader.close()

    path = profile / "offsets.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    found = {key.replace(" ", ""): value for key, value in found.items()}
    for key, value in found.items():
        report["resolved"][key] = {"value": value, "method": "probe_internals.py: unique live match", "confidence": 1.0}
    write_json(path, report)
    print(f"[internals] recorded: {', '.join(f'{k}={v:#x}' for k, v in found.items()) or 'nothing unique'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, MemoryFault, OSError, ValueError, KeyError) as exc:
        print(f"[internals] {exc}", file=sys.stderr)
        raise SystemExit(1)
