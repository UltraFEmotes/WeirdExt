"""Narrow offline ARM64 getter extraction from Mach-O bytes.

This recognizes an explicit instruction chain, not general ARM emulation.
Unsupported or ambiguous shapes produce no selected accessor. No process is
opened and no getter is executed.
"""
from __future__ import annotations

import hashlib
import struct


def _words(mach, address, size):
    raw = mach.read_vaddr(address, size)
    return list(struct.unpack(f"<{len(raw) // 4}I", raw[:len(raw) // 4 * 4]))


def _address_pair(first, second, pc):
    if first & 0x9F000000 != 0x90000000 or second & 0xFFC00000 != 0x91000000:
        return None
    register = first & 31
    if (second >> 5) & 31 != register:
        return None
    immediate = (((first >> 5) & 0x7FFFF) << 2) | ((first >> 29) & 3)
    if immediate & (1 << 20):
        immediate -= 1 << 21
    return second & 31, (pc & ~0xFFF) + (immediate << 12) + ((second >> 10) & 0xFFF)


def _branch_target(word, pc, link=False):
    if word & 0xFC000000 != (0x94000000 if link else 0x14000000):
        return None
    immediate = word & 0x3FFFFFF
    if immediate & (1 << 25):
        immediate -= 1 << 26
    return pc + immediate * 4


def _rtti_name(mach, vtable):
    raw = mach.read_vaddr(vtable - 8, 8)
    if len(raw) != 8:
        return None
    raw = mach.read_vaddr(struct.unpack("<Q", raw)[0] + 8, 8)
    if len(raw) != 8:
        return None
    text = mach.read_vaddr(struct.unpack("<Q", raw)[0], 512).split(b"\0", 1)[0]
    try:
        return text.decode("ascii")
    except UnicodeDecodeError:
        return None


def _constructor_owner(mach, address):
    words = _words(mach, address, 0x100)
    # This shape preserves the descriptor's this pointer in x19.
    if 0xAA0003F3 not in words:  # mov x19, x0
        return None
    for index in range(len(words) - 2):
        pair = _address_pair(words[index], words[index + 1], address + index * 4)
        if pair is None:
            continue
        register, vtable = pair
        store = words[index + 2]
        if (store & 0xFFC00000 == 0xF9000000 and (store >> 10) & 0xFFF == 0
                and (store >> 5) & 31 == 19 and store & 31 == register):
            name = _rtti_name(mach, vtable)
            if name and name.startswith("N3RBX10Reflection14PropDescriptorINS_8BasePartENS_15CoordinateFrameE"):
                return {"vtable": vtable, "mangled": name}
    return None


def extract_accessor_chain(mach, getter):
    """Recognize a 48-byte CFrame copy through Part and Primitive getters."""
    words = _words(mach, getter, 0x34)
    if len(words) < 13:
        return None
    # Preserve the sret buffer in x19, adjust this, call, copy exactly 48 bytes.
    # Strict forms intentionally reject branchy or differently lowered getters.
    if (words[:3] != [0xA9BE4FF4, 0xA9017BFD, 0x910043FD]
            or words[10:13] != [0xA9417BFD, 0xA8C24FF4, 0xD65F03C0]
            or words[3] != 0xAA0803F3  # mov x19, x8
            or words[4] & 0xFFC003FF != 0xD1000000  # sub x0, x0, #imm
            or words[6:10] != [0xAD400400, 0xAD000660, 0x3DC00800, 0x3D800A60]
            or words[12] != 0xD65F03C0):
        return None
    part_getter = _branch_target(words[5], getter + 20, link=True)
    if part_getter is None:
        return None
    part = _words(mach, part_getter, 8)
    if len(part) != 2 or part[0] & 0xFFC003FF != 0xF9400000:  # ldr x0, [x0, #imm]
        return None
    primitive_offset = ((part[0] >> 10) & 0xFFF) * 8
    primitive_getter = _branch_target(part[1], part_getter + 4)
    if primitive_getter is None:
        return None
    primitive = _words(mach, primitive_getter, 40)
    if len(primitive) != 10:
        return None
    if (primitive[:3] != [0xA9BE4FF4, 0xA9017BFD, 0x910043FD]
            or primitive[7:] != [0xA9417BFD, 0xA8C24FF4, 0xD65F03C0]
            or primitive[3] != 0xAA0003F3  # mov x19, x0
            or primitive[4] & 0xFFC003FF != 0x91000000  # add x0, x0, #imm
            or primitive[6] & 0xFFC003FF != 0x91000260  # add x0, x19, #imm
            or primitive[9] != 0xD65F03C0):
        return None
    update_helper = _branch_target(primitive[5], primitive_getter + 20, link=True)
    if update_helper is None:
        return None
    frame_offset = (primitive[6] >> 10) & 0xFFF
    return {
        "property_getter": getter, "part_getter": part_getter,
        "primitive_getter": primitive_getter, "update_helper": update_helper,
        "basepart_primitive_offset": primitive_offset,
        "primitive_cframe_offset": frame_offset,
        "primitive_position_offset": frame_offset + 36,
        "getter_words": words[:13], "part_words": part, "primitive_words": primitive,
    }


def inspect_geometry_accessors(mach):
    """Locate CFrame registration sites, require owner RTTI, trace exact getters."""
    import numpy as np

    sections = [section for section in mach.sections if section.name == "__text"]
    strings = []
    for section in mach.sections:
        if section.name != "__cstring":
            continue
        raw = mach.blob[section.offset:section.offset + section.size]
        start = 0
        while True:
            index = raw.find(b"CFrame\0", start)
            if index < 0:
                break
            start = index + 1
            if index == 0 or raw[index - 1] == 0:
                strings.append(section.addr + index)
    candidates = []
    for section in sections:
        raw = mach.blob[section.offset:section.offset + section.size // 4 * 4]
        words = np.frombuffer(raw, dtype="<u4")
        indexes = np.nonzero((words & np.uint32(0x9F000000)) == np.uint32(0x90000000))[0]
        ops = words[indexes].astype(np.int64)
        immediate = (((ops >> 5) & 0x7FFFF) << 2) | ((ops >> 29) & 3)
        immediate = np.where(immediate & (1 << 20), immediate - (1 << 21), immediate)
        pages = ((section.addr + indexes.astype(np.int64) * 4) & ~0xFFF) + (immediate << 12)
        for string in strings:
            for raw_index in indexes[pages == (string & ~0xFFF)]:
                index = int(raw_index)
                if index + 1 >= len(words):
                    continue
                site = section.addr + index * 4
                if _address_pair(int(words[index]), int(words[index + 1]), site) != (1, string):
                    continue
                getter = constructor = None
                for cursor in range(index + 2, min(index + 24, len(words) - 1)):
                    pc = section.addr + cursor * 4
                    pair = _address_pair(int(words[cursor]), int(words[cursor + 1]), pc)
                    if pair and pair[0] == 3:
                        getter = pair[1]
                    call = _branch_target(int(words[cursor]), pc, link=True)
                    if call is not None:
                        constructor = call
                        break
                if getter is None or constructor is None:
                    continue
                owner = _constructor_owner(mach, constructor)
                if owner is None:
                    continue
                chain = extract_accessor_chain(mach, getter)
                if chain is not None:
                    candidates.append({**chain, "registration": site,
                                       "constructor": constructor, "descriptor_rtti": owner})
    identities = {(row["basepart_primitive_offset"], row["primitive_cframe_offset"])
                  for row in candidates}
    return {
        "binary_path": mach.path, "binary_sha256": hashlib.sha256(mach.blob).hexdigest(),
        "candidates": candidates,
        "selected": candidates[0] if len(identities) == 1 else None,
        "limitations": [
            "Static instruction analysis only; no getter or update helper was executed.",
            "The getter invokes an update helper; external reads can bypass that synchronization.",
            "Position uses the contiguous 9-float rotation plus 3-float translation interpretation.",
            "Unrecognized or conflicting instruction shapes are not resolved by guessing.",
        ],
    }
