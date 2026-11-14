"""Offline analysis of bounded, caller-supplied memory snapshots.

Known object starts bound preceding captures. This does not infer allocation
sizes for isolated objects or identify the semantic owner of duplicate poses.
"""
from __future__ import annotations

from bisect import bisect_right

from . import prims


def bound_object_samples(samples, known_addresses=()):
    """Return (address, bounded bytes, next known start) for each capture."""
    starts = sorted(set(known_addresses) | {addr for addr, _ in samples})
    bounded = []
    for addr, blob in samples:
        index = bisect_right(starts, addr)
        next_start = starts[index] if index < len(starts) else None
        size = min(len(blob), next_start - addr) if next_start is not None else len(blob)
        bounded.append((addr, blob[:size], next_start))
    return bounded


def equal_block_groups(samples, offsets, size=48):
    """Group byte-equal blocks across every capture; equality is not ownership."""
    groups = []
    for offset in sorted(offsets):
        for group in groups:
            reference = group[0]
            if all(len(blob) >= max(offset, reference) + size
                   and blob[offset:offset + size] == blob[reference:reference + size]
                   for blob in samples):
                group.append(offset)
                break
        else:
            groups.append([offset])
    return groups


def summarize_primitive_samples(samples, known_addresses=()):
    bounded = bound_object_samples(samples, known_addresses)
    blobs = [blob for _, blob, _ in bounded]
    offsets = []
    if len(blobs) >= 2:
        for off in range(0, min(map(len, blobs)) - 48 + 1, 4):
            if all(prims.orthonormal3(prims.f32s(blob, off, 9))
                   and prims.vec3_sane(blob, off + 36) for blob in blobs):
                offsets.append(off)
    return {
        "sample_count": len(samples),
        "bounds": [
            {"address": addr, "captured_bytes": len(original), "analysis_bytes": len(blob),
             "next_known_start": next_start}
            for (addr, blob, next_start), (_, original) in zip(bounded, samples)
        ],
        "cframe_candidates": [
            {"offset": off, "position_offset": off + 36,
             "positions": [list(prims.f32s(blob, off + 36, 3)) for blob in blobs]}
            for off in offsets
        ],
        "equal_pose_groups": equal_block_groups(blobs, offsets),
        "limitations": [
            "Bounds use known object starts, not allocator-reported object sizes.",
            "Captures were read separately and are not an atomic process snapshot.",
            "Equal pose bytes do not identify current, cached, local or world-space semantics.",
            "All offsets remain candidates; no runtime consumer was observed.",
        ],
    }
