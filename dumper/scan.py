"""dumper.scan — chunked sweeps over an attached address space.

`bytes.find` is memchr-backed, so a whole address space is walkable in a few
seconds: read 4 MiB, hunt the needle, advance. Holes inside a region are
skipped page-wise instead of aborting the sweep.

The hot paths (qword span filter, literal find) have a native backend in
dumper/sweepc.c: same regions, same rules, C speed. The Python sweep stays
as the fallback for fake memories in tests and for stripped environments
where the tool cannot be built.
"""

from __future__ import annotations

import os
import struct
import subprocess
import sys

from rbxl.memory import MemoryFault

CHUNK = 1 << 22
HOLE_STEP = 1 << 16

_TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
TOOL_SRC = os.path.join(_TOOL_DIR, "sweepc.c")
TOOL_BIN = os.path.join(_TOOL_DIR, "sweepc")

_SWEEP_RECORD = struct.Struct("<QQ")

SYSTEM_PREFIXES = (
    "/usr/lib",
    "/System",
    "/Library/Apple",
)


CLIENT_IMAGE_PREFIX = ("RobloxPlayer", "Roblox")


def is_system_path(path: str) -> bool:
    return path.startswith(SYSTEM_PREFIXES)


def is_noise_file(path: str) -> bool:
    """File-backed pages that are not the client image: resource .dat files,
    frameworks, dylibs. ICU data alone carries hundreds of false name hits."""
    if not path:
        return False
    if is_system_path(path):
        return True
    return not path.rsplit("/", 1)[-1].startswith(CLIENT_IMAGE_PREFIX)


def iter_chunks(mem, regions, chunk: int = CHUNK, max_bytes: int | None = None,
                 include_system: bool = False, max_region: int = 64 << 30,
                 max_faults: int = 3000, checkpoint=None):
    """Yield (address, bytes) for readable runs, bisecting around holes.

    Sparse reservations report multi-terabyte sizes that are almost entirely
    unmapped; a flat walk would crawl them at 64 KiB a step. Bisecting costs
    log2(size/64KiB) probes per hole and a fault budget caps the damage.
    Unless include_system is set, only the anonymous heap and the client's own
    image are swept.
    """
    total = 0
    for start, size, path, prot in regions:
        if checkpoint is not None:
            checkpoint()
        if not (prot & 1):
            continue
        if not include_system and is_noise_file(path):
            continue
        if size > max_region:
            continue

        faults = 0
        stack = [(start, start + size)]
        while stack:
            if checkpoint is not None:
                checkpoint()
            lo, hi = stack.pop()
            if lo >= hi:
                continue
            n = min(chunk, hi - lo)
            if max_bytes is not None:
                n = min(n, max_bytes - total)
                if n <= 0:
                    return
            try:
                data = mem.read(lo, n)
            except MemoryFault:
                faults += 1
                if faults > max_faults:
                    break
                if hi - lo <= HOLE_STEP:
                    continue
                mid = lo + min(n, hi - lo) // 2
                stack.append((mid, hi))
                stack.append((lo, mid))
                continue
            total += len(data)
            yield lo, data
            if lo + n < hi:
                stack.append((lo + n, hi))


def sweep_order(regions):
    """Malloc heap first: instance names live in writable anonymous zones.

    Address order wastes the read budget on huge read-only mappings (the dyld
    cache and Apple's ObjC/Swift metadata arrive early and carry false name
    hits), so the sweep is prioritised: writable anon, then anon, then file.
    """
    def rank(region):
        _start, _size, path, prot = region
        if not path:
            return (0, 0) if (prot & 2) else (1, 0)
        return (2, 0)
    return sorted(regions, key=lambda r: (rank(r), r[0]))


def find_bytes(mem, regions, needle: bytes, limit: int | None = None, **kw):
    """Yield every address holding `needle`."""
    hits = 0
    for base, data in iter_chunks(mem, sweep_order(regions), **kw):
        view = memoryview(data)
        offset = 0
        while True:
            idx = data.find(needle, offset)
            if idx < 0:
                break
            yield base + idx
            hits += 1
            if limit is not None and hits >= limit:
                return
            offset = idx + 1


def find_aligned_qword(mem, regions, value: int, limit: int | None = None, **kw):
    """Yield 8-byte aligned addresses whose stored pointer equals `value`."""
    needle = struct.pack("<Q", value)
    hits = 0
    for addr in find_bytes(mem, regions, needle, limit=None, **kw):
        if addr & 7:
            continue
        yield addr
        hits += 1
        if limit is not None and hits >= limit:
            return


def collect_qwords(buf: bytes):
    """Yield (offset, value) for every aligned qword in a buffer."""
    for off in range(0, len(buf) - 7, 8):
        yield off, struct.unpack_from("<Q", buf, off)[0]


def heap_regions(regions):
    """Anonymous mappings, writable first — where C++ objects actually live."""
    def rank(region):
        _start, _size, path, prot = region
        if path:
            return 2
        return 0 if (prot & 2) else 1
    return [r for r in sorted(regions, key=lambda r: (rank(r), r[0])) if not r[2]]


def find_pointer_slots(mem, regions, spans, align: int = 16, limit: int | None = None,
                       max_bytes: int | None = None, progress=None):
    """Yield (address, value) for every aligned qword holding a value in `spans`.

    A 4 MiB chunk is 512k qwords; comparing that as a numpy array is three
    orders of magnitude faster than a Python loop, and this sweep runs over the
    entire heap to find vtable-bearing objects.
    """
    try:
        import numpy as np
    except ImportError:  # pragma: no cover - numpy is present on the target
        np = None

    emitted = 0
    total = 0
    for base, data in iter_chunks(mem, regions, chunk=1 << 22, max_bytes=max_bytes):
        total += len(data)
        if progress is not None and total % (256 << 20) < (1 << 22):
            progress(total)
        usable = len(data) - (len(data) % 8)
        if usable <= 0:
            continue
        if np is not None:
            words = np.frombuffer(data, dtype="<u8", count=usable // 8)
            mask = np.zeros(words.shape, dtype=bool)
            for lo, hi in spans:
                mask |= (words >= lo) & (words < hi)
            indexes = np.flatnonzero(mask)
            pairs = ((base + int(i) * 8, int(words[i])) for i in indexes)
        else:
            pairs = (
                (base + off, struct.unpack_from("<Q", data, off)[0])
                for off in range(0, usable, 8)
                if any(lo <= struct.unpack_from("<Q", data, off)[0] < hi for lo, hi in spans)
            )
        for address, value in pairs:
            if address % align:
                continue
            yield address, value
            emitted += 1
            if limit is not None and emitted >= limit:
                return
    del total


def ensure_tool() -> str | None:
    """Build the native sweeper once; None if clang is unavailable."""
    try:
        if os.path.exists(TOOL_BIN) and os.path.getmtime(TOOL_BIN) >= os.path.getmtime(TOOL_SRC):
            return TOOL_BIN
        subprocess.run(["clang", "-O2", "-o", TOOL_BIN, TOOL_SRC],
                       check=True, capture_output=True, timeout=60)
        return TOOL_BIN
    except (OSError, subprocess.SubprocessError):
        return None


def tool_available() -> bool:
    return ensure_tool() is not None


def _run_sweep(args: list[str], stdin: bytes | None = None) -> bytes:
    result = subprocess.run(args, input=stdin, capture_output=True, timeout=1800)
    if result.returncode != 0:
        raise MemoryFault(f"sweepc failed ({result.returncode}): "
                          f"{result.stderr.decode('utf-8', 'replace').strip()}")
    return result.stdout


def c_find_spans(mem, spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Native (address, value) hits for qwords landing inside `spans`.

    Requires a real task port (the caller is already root, so task_for_pid
    succeeds) and the compiled tool; raises MemoryFault otherwise so the
    caller can fall back to the Python sweep."""
    tool = ensure_tool()
    if tool is None or not hasattr(mem, "task"):
        raise MemoryFault("native sweeper unavailable")
    args = [tool, "spans", str(mem.pid)]
    args += [f"{lo:x}:{hi:x}" for lo, hi in spans]
    blob = _run_sweep(args)
    out = []
    for addr, value in _SWEEP_RECORD.iter_unpack(blob):
        out.append((addr, value))
    return out


def c_find_bytes(mem, needles: list[bytes], limit_per: int = 64) -> dict[int, list[int]]:
    """Native literal search over writable anonymous memory.

    Returns {needle_index: [addresses]} in the order `needles` was given."""
    tool = ensure_tool()
    if tool is None or not hasattr(mem, "task"):
        raise MemoryFault("native sweeper unavailable")
    args = [tool, "find", str(mem.pid), str(limit_per)]
    stdin = b"\n".join(needles) + b"\n"
    blob = _run_sweep(args, stdin=stdin)
    found: dict[int, list[int]] = {index: [] for index in range(len(needles))}
    for addr, index in _SWEEP_RECORD.iter_unpack(blob):
        if index < len(needles) and len(found[index]) < limit_per:
            found[index].append(addr)
    return found


def find_rtti_slots(mem, regions, spans, resolve, align: int = 16,
                    max_bytes: int | None = None, progress=None):
    """Yield (address, value) for aligned slots holding a resolved vtable.

    `resolve(value) -> bool` is called once per distinct value per chunk, not
    once per slot. A heap of 7 GiB holds ~900M qwords but only a few hundred
    thousand distinct pointers into the image, so this is the difference
    between a two-minute sweep and a twenty-second one.
    """
    try:
        import numpy as np
    except ImportError:  # pragma: no cover
        np = None

    emitted = 0
    total = 0
    for base, data in iter_chunks(mem, regions, chunk=1 << 22, max_bytes=max_bytes):
        total += len(data)
        if progress is not None and total % (256 << 20) < (1 << 22):
            progress(total)
        usable = len(data) - (len(data) % 8)
        if usable <= 0:
            continue
        if np is None:  # pragma: no cover
            for off in range(0, usable, 8):
                value = struct.unpack_from("<Q", data, off)[0]
                if resolve(value):
                    address = base + off
                    if address % align == 0:
                        yield address, value
                        emitted += 1
            continue

        words = np.frombuffer(data, dtype="<u8", count=usable // 8)
        mask = np.zeros(words.shape, dtype=bool)
        for lo, hi in spans:
            mask |= (words >= lo) & (words < hi)
        indexes = np.flatnonzero(mask)
        if not len(indexes):
            continue
        values = words[indexes]
        unique, inverse = np.unique(values, return_inverse=True)
        flags = np.fromiter((resolve(int(v)) for v in unique), dtype=bool, count=len(unique))
        selected = indexes[flags[inverse]]
        for index in selected:
            address = base + int(index) * 8
            if address % align:
                continue
            yield address, int(words[index])
            emitted += 1
    del emitted


def find_many(mem, regions, needles, limit_per: int = 64, **kw) -> dict[str, list[int]]:
    """One sweep of the address space, many needles. The read dominates, so
    batching every pattern into a single pass costs about as much as one."""
    out: dict[str, list[int]] = {needle: [] for needle in needles}
    for base, data in iter_chunks(mem, regions, **kw):
        for needle in needles:
            hits = out[needle]
            if len(hits) >= limit_per:
                continue
            offset = 0
            while len(hits) < limit_per:
                index = data.find(needle, offset)
                if index < 0:
                    break
                hits.append(base + index)
                offset = index + 1
    return out
