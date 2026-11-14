"""Offline, strict Camera property getter decoding; never attaches or executes code."""
from __future__ import annotations

import hashlib
import math
import struct

from .arm64_accessors import _address_pair, _branch_target, _rtti_name, _words


def _registrations(mach, property_name):
    import numpy as np

    strings = []
    needle = property_name.encode("ascii") + b"\0"
    for section in mach.sections:
        if section.name != "__cstring":
            continue
        raw = mach.blob[section.offset:section.offset + section.size]
        start = 0
        while (index := raw.find(needle, start)) >= 0:
            start = index + 1
            if index == 0 or raw[index - 1] == 0:
                strings.append(section.addr + index)
    for section in mach.sections:
        if section.name != "__text":
            continue
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
                site = section.addr + index * 4
                if index + 1 >= len(words) or _address_pair(int(words[index]), int(words[index + 1]), site) != (1, string):
                    continue
                getter = None
                for cursor in range(index + 2, min(index + 24, len(words) - 1)):
                    pc = section.addr + cursor * 4
                    pair = _address_pair(int(words[cursor]), int(words[cursor + 1]), pc)
                    if pair and pair[0] == 3:
                        getter = pair[1]
                    constructor = _branch_target(int(words[cursor]), pc, link=True)
                    if constructor is not None:
                        # Member-pointer adjustments must be zero, not merely
                        # inferred from the thunk's CameraProp base adjustment.
                        if (getter is not None and cursor >= index + 4
                                and [int(word) for word in words[cursor - 2:cursor]] == [0xD2800004, 0xD2800006]):
                            yield site, getter, constructor
                        break


def _camera_owner(mach, constructor, value_type):
    """Identify the allocated member-getter descriptor by its stored RTTI vtable."""
    words = _words(mach, constructor, 0x180)
    prefix = "N3RBX10Reflection14PropDescriptorINS_6CameraE" + value_type
    for index in range(len(words) - 2):
        pair = _address_pair(words[index], words[index + 1], constructor + index * 4)
        # stp x8, x24, [x0]: allocated GetSetImpl receives its own vtable.
        if pair is None or pair[0] != 8 or words[index + 2] != 0xA9006008:
            continue
        name = _rtti_name(mach, pair[1])
        if not name or not name.startswith(prefix) or "10GetSetImplIMNS_10CameraPropE" not in name:
            continue
        raw = mach.read_vaddr(pair[1] + 32, 8)
        if len(raw) == 8:
            return {"vtable": pair[1], "mangled": name, "dispatch": struct.unpack("<Q", raw)[0]}
    return None


def _this_adjustment(mach, dispatch, cframe=False):
    words = _words(mach, dispatch, 80 if cframe else 36)
    if cframe:
        if len(words) != 20 or words[:4] != [0xA9BE4FF4, 0xA9017BFD, 0x910043FD, 0xAA0803F3]:
            return None
        prefix = words[4:7]
        if words[7:] != [0xA940A808, 0x8B8A0520, 0x3600006A, 0xF9400009,
                         0xF8684928, 0xD63F0100, 0xAD400400, 0xAD000660,
                         0x3DC00800, 0x3D800A60, 0xA9417BFD, 0xA8C24FF4, 0xD65F03C0]:
            return None
    else:
        if len(words) != 9 or words[3:] != [0xA940A401, 0x8B890500, 0x36000069,
                                          0xF9400008, 0xF8614901, 0xD61F0020]:
            return None
        prefix = words[:3]
    if prefix[0] & 0xFFC003FF != 0x91000028 or prefix[1:] != [0xF100003F, 0x9A8803E9 if cframe else 0x9A8803E8]:
        return None
    return (prefix[0] >> 10) & 0xFFF


def _radians_to_degrees(mach, address):
    words = _words(mach, address, 28)
    if (len(words) != 7 or words[:3] != [0x52A86688, 0x1E270101, 0x1E210800]
            or words[5:] != [0x1E211800, 0xD65F03C0]):
        return None
    # adrp x8, constant-page; ldr s1, [x8, #offset], followed by division.
    pair = _address_pair(words[3], 0x91000108, address + 12)
    if pair is None or pair[0] != 8 or words[4] & 0xFFC003FF != 0xBD400101:
        return None
    constant_address = pair[1] + (((words[4] >> 10) & 0xFFF) * 4)
    raw = mach.read_vaddr(constant_address, 4)
    if len(raw) != 4 or not math.isclose(struct.unpack("<f", raw)[0], math.pi, abs_tol=1e-7):
        return None
    return {"address": address, "words": words, "pi_address": constant_address,
            "pi_value": struct.unpack("<f", raw)[0]}


def inspect_camera_accessors(mach):
    candidates = {"CFrame": [], "FieldOfView": []}
    for property_name, value_type in (("CFrame", "NS_15CoordinateFrameEE"), ("FieldOfView", "fE")):
        for registration, getter, constructor in _registrations(mach, property_name):
            owner = _camera_owner(mach, constructor, value_type)
            if owner is None:
                continue
            adjustment = _this_adjustment(mach, owner["dispatch"], cframe=property_name == "CFrame")
            if adjustment is None:
                continue
            words = _words(mach, getter, 8)
            if len(words) != 2:
                continue
            row = {"registration": registration, "property_getter": getter,
                   "constructor": constructor, "descriptor_rtti": owner,
                   "this_adjustment": adjustment, "getter_words": words}
            if property_name == "CFrame":
                if words[0] & 0xFFC003FF != 0x91000000 or words[1] != 0xD65F03C0:
                    continue
                row["offset"] = adjustment + ((words[0] >> 10) & 0xFFF)
            else:
                if words[0] & 0xFFC003FF != 0xBD400000:
                    continue
                conversion = _branch_target(words[1], getter + 4)
                conversion = _radians_to_degrees(mach, conversion) if conversion is not None else None
                if conversion is None:
                    continue
                row.update(offset=adjustment + (((words[0] >> 10) & 0xFFF) * 4),
                           unit="radians", conversion=conversion)
            candidates[property_name].append(row)
    selected = None
    if all(len({row["offset"] for row in rows}) == 1 for rows in candidates.values()):
        selected = {"camera_cframe_offset": candidates["CFrame"][0]["offset"],
                    "camera_fov_offset": candidates["FieldOfView"][0]["offset"],
                    "camera_fov_unit": "radians"}
    return {"binary_path": mach.path, "binary_sha256": hashlib.sha256(mach.blob).hexdigest(),
            "candidates": candidates, "selected": selected,
            "limitations": ["Static getter decoding only; no process was attached or getter executed.",
                            "Camera.CFrame may differ from a custom or late-adjusted render pose.",
                            "This does not establish viewport placement or live Primitive freshness."]}
