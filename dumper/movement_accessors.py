"""Offline Humanoid getter and speed-shadow extraction. No live process access."""
from __future__ import annotations

import hashlib
import struct

from .arm64_accessors import _address_pair, _rtti_name, _words
from .camera_accessors import _registrations, _this_adjustment


def _owner(mach, constructor, value_type):
    words = _words(mach, constructor, 0x180)
    prefix = "N3RBX10Reflection14PropDescriptorINS_8HumanoidE" + value_type
    for index in range(len(words) - 2):
        pair = _address_pair(words[index], words[index + 1], constructor + index * 4)
        if not pair or pair[0] != 8 or words[index + 2] != 0xA9006008:
            continue
        name = _rtti_name(mach, pair[1])
        if name and name.startswith(prefix) and "10GetSetImplIMNS_12HumanoidPropE" in name:
            raw = mach.read_vaddr(pair[1] + 32, 8)
            if len(raw) == 8:
                return {"vtable": pair[1], "mangled": name, "dispatch": struct.unpack("<Q", raw)[0]}
    return None


def _file_address(mach, offset):
    for segment in mach.segments:
        if segment.fileoff <= offset < segment.fileoff + segment.filesize:
            return segment.vmaddr + offset - segment.fileoff
    return None


def _humanoid_vtables(mach, adjustment):
    """Only matching Itanium Humanoid RTTI and the exact secondary offset-to-top."""
    name_offset = mach.blob.find(b"N3RBX8HumanoidE\0")
    name_address = _file_address(mach, name_offset) if name_offset >= 0 else None
    if name_address is None:
        return []
    result = []
    cursor = 0
    while (cursor := mach.blob.find(struct.pack("<Q", name_address), cursor)) >= 0:
        if cursor % 8 == 0:
            name_pointer = _file_address(mach, cursor)
            if name_pointer is not None:
                typeinfo = name_pointer - 8
                index = 8
                while (index := mach.blob.find(struct.pack("<Q", typeinfo), index)) >= 0:
                    if index % 8 == 0 and struct.unpack_from("<q", mach.blob, index - 8)[0] == -adjustment:
                        address = _file_address(mach, index)
                        if address is not None:
                            result.append(address + 8)
                    index += 1
        cursor += 1
    return result


def _speed_shadow(mach, registration, adjustment, relative):
    registration_words = _words(mach, registration, 96)
    setters = []
    for index in range(len(registration_words) - 1):
        pair = _address_pair(registration_words[index], registration_words[index + 1], registration + index * 4)
        if pair and pair[0] == 5:
            setters.append(pair[1])
    if len(setters) != 1:
        return []
    setter = setters[0]
    words = _words(mach, setter, 0x180)
    candidates = []
    for index in range(len(words) - 4):
        # str s8,[x19,#speed]; ldr x8,[x19]; ldr x8,[x8,#slot]; mov x0,x19; blr x8
        if (words[index] != (0xBD000268 | ((relative // 4) << 10))
                or words[index + 1] != 0xF9400268
                or words[index + 2] & 0xFFC003FF != 0xF9400108
                or words[index + 3:index + 5] != [0xAA1303E0, 0xD63F0100]):
            continue
        slot = ((words[index + 2] >> 10) & 0xFFF) * 8
        for vtable in _humanoid_vtables(mach, adjustment):
            raw = mach.read_vaddr(vtable + slot, 8)
            if len(raw) != 8:
                continue
            notification = struct.unpack("<Q", raw)[0]
            notify = _words(mach, notification, 12)
            if (len(notify) != 3 or notify[0] != (0xD1000008 | (adjustment << 10))
                    or notify[1] != (0xBD400000 | ((relative // 4) << 10))
                    or notify[2] & 0xFFC003FF != 0xBD000000):
                continue
            check = adjustment + (((notify[2] >> 10) & 0xFFF) * 4)
            candidates.append({"offset": check, "setter": setter, "setter_store_site": setter + index * 4,
                               "notification_vtable": vtable, "notification_slot": slot,
                               "notification": notification, "notification_words": notify})
    return candidates


def inspect_movement_accessors(mach):
    candidates = {key: [] for key in ("WalkSpeed", "JumpPower", "UseJumpPower", "WalkSpeedCheck")}
    for property_name in ("WalkSpeed", "JumpPower", "UseJumpPower"):
        is_bool = property_name == "UseJumpPower"
        for registration, getter, constructor in _registrations(mach, property_name):
            owner = _owner(mach, constructor, "bE" if is_bool else "fE")
            if owner is None:
                continue
            adjustment = _this_adjustment(mach, owner["dispatch"])
            words = _words(mach, getter, 8)
            opcode = 0x39400000 if is_bool else 0xBD400000
            if (adjustment is None or len(words) != 2 or words[1] != 0xD65F03C0
                    or words[0] & 0xFFC003FF != opcode):
                continue
            relative = ((words[0] >> 10) & 0xFFF) * (1 if is_bool else 4)
            candidates[property_name].append({"offset": adjustment + relative, "registration": registration,
                                             "getter": getter, "getter_words": words,
                                             "this_adjustment": adjustment, "descriptor_rtti": owner})
            if property_name == "WalkSpeed":
                candidates["WalkSpeedCheck"].extend(_speed_shadow(mach, registration, adjustment, relative))
    selected = {}
    for key, rows in candidates.items():
        offsets = {row["offset"] for row in rows}
        if len(offsets) == 1:
            selected[key] = offsets.pop()
    return {"binary_path": mach.path, "binary_sha256": hashlib.sha256(mach.blob).hexdigest(),
            "candidates": candidates, "selected": selected,
            "limitations": ["Offline instruction evidence only; no live reads/writes performed.",
                            "WalkSpeedCheck names the shadow copied by the native WalkSpeed notification.",
                            "External field writes do not invoke setters or establish server acceptance."]}
