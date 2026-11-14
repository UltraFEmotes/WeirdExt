"""Narrow offline BasePart collision/assembly-PV decoder. No live access."""
import hashlib
import struct

from .arm64_accessors import _address_pair, _branch_target, _rtti_name, _words, inspect_geometry_accessors
from .camera_accessors import _registrations, _this_adjustment
from .movement_accessors import _file_address


def _part_owner(mach, constructor, value_type):
    words = _words(mach, constructor, 0x180)
    prefix = "N3RBX10Reflection14PropDescriptorINS_8BasePartE" + value_type
    for index in range(len(words) - 2):
        pair = _address_pair(words[index], words[index + 1], constructor + index * 4)
        if not pair or pair[0] != 8 or words[index + 2] != 0xA9006008:
            continue
        name = _rtti_name(mach, pair[1])
        if name and name.startswith(prefix) and "10GetSetImplIMNS_12BasePartPropE" in name:
            raw = mach.read_vaddr(pair[1] + 32, 8)
            if len(raw) == 8:
                return {"vtable": pair[1], "mangled": name, "dispatch": struct.unpack("<Q", raw)[0]}
    return None


def _part_vtables(mach, adjustment):
    index = mach.blob.find(b"N3RBX4PartE\0")
    name = _file_address(mach, index) if index >= 0 else None
    if name is None:
        return []
    tables = []
    cursor = 0
    while (cursor := mach.blob.find(struct.pack("<Q", name), cursor)) >= 0:
        address = _file_address(mach, cursor)
        if cursor % 8 == 0 and address is not None:
            pointer = 8
            while (pointer := mach.blob.find(struct.pack("<Q", address - 8), pointer)) >= 0:
                if pointer % 8 == 0 and struct.unpack_from("<q", mach.blob, pointer - 8)[0] == -adjustment:
                    vtable = _file_address(mach, pointer)
                    if vtable is not None:
                        tables.append(vtable + 8)
                pointer += 1
        cursor += 1
    return tables


def decode_collision(mach, getter, adjustment):
    wrapper = _words(mach, getter, 8)
    if len(wrapper) != 2 or wrapper[0] != (0xD1000000 | (adjustment << 10)):
        return None
    target = _branch_target(wrapper[1], getter + 4)
    words = _words(mach, target, 16) if target is not None else []
    if (len(words) != 4 or words[0] & 0xFFC003FF != 0xF9400008
            or words[1] & 0xFFC003FF != 0x39400108
            or words[2] & 0xFFC003FF != 0x53000100 or words[3] != 0xD65F03C0):
        return None
    shift, last = (words[2] >> 16) & 31, (words[2] >> 10) & 31
    if shift != last or shift >= 8:
        return None
    return {"part_primitive": ((words[0] >> 10) & 0xFFF) * 8,
            "collision_flags": (words[1] >> 10) & 0xFFF, "collision_mask": 1 << shift,
            "getter": getter, "part_getter": target, "words": words}


def decode_assembly_links(mach, setter, geometry):
    words = _words(mach, setter, 0x200)
    rows = []
    for index in range(len(words) - 5):
        if words[index] != 0xAA1503E0 or words[index + 3] != 0xAA0003F5:
            continue
        assembly_call = _branch_target(words[index + 1], setter + (index + 1) * 4, link=True)
        root_call = _branch_target(words[index + 2], setter + (index + 2) * 4, link=True)
        if assembly_call is None or root_call is None:
            continue
        assembly = _words(mach, assembly_call, 4)
        if assembly and (branch := _branch_target(assembly[0], assembly_call)) is not None:
            assembly_call = branch
        assembly = _words(mach, assembly_call, 20)
        root = _words(mach, root_call, 16)
        if (len(assembly) != 5 or assembly[0] & 0xFFC003FF != 0xF9400008
                or assembly[1] & 0xFFC003FF != 0xD1000109
                or assembly[2:] != [0xF100011F, 0x9A8903E0, 0xD65F03C0]
                or len(root) != 4 or root[0] & 0xFFC003FF != 0xF9400008
                or root[1] & 0xFF00001F != 0xB4000008
                or root[2] & 0xFFC003FF != 0xD1000100 or root[3] != 0xD65F03C0):
            continue
        # The setter passes root + motion_offset to the same update helper
        # independently recovered from the CFrame getter.
        if (words[index + 4] & 0xFFC003FF != 0x91000000
                or _branch_target(words[index + 5], setter + (index + 5) * 4, link=True) != geometry["update_helper"]):
            continue
        motion = (words[index + 4] >> 10) & 0xFFF
        rows.append({"primitive_assembly": ((assembly[0] >> 10) & 0xFFF) * 8,
                     "assembly_adjustment": (assembly[1] >> 10) & 0xFFF,
                     "assembly_root": ((root[0] >> 10) & 0xFFF) * 8,
                     "root_adjustment": (root[2] >> 10) & 0xFFF,
                     "motion_offset": motion, "setter": setter, "assembly_getter": assembly_call,
                     "root_getter": root_call, "assembly_words": assembly, "root_words": root})
    return rows


def _velocity_caches(mach, geometry, motion):
    # Bounded search around the known kinematic update helper for the paired
    # PV-copy routine, not a scan for plausible floating-point values.
    start = geometry["update_helper"]
    words = _words(mach, start, 0x3000)
    rows = []
    for index in range(len(words) - 40):
        if (words[index] != 0xF9400008 or words[index + 1] & 0xFF00001F != 0xB4000008
                or words[index + 2] != 0xD65F03C0):
            continue
        body = words[index:index + 40]
        for cursor in range(3, len(body) - 6):
            if (body[cursor] & 0xFFC003FF != 0x91000260 or body[cursor + 1] != 0xAA1403E1
                    or body[cursor + 3] & 0xFFC003FF != 0x91000260
                    or _branch_target(body[cursor + 2], start + (index + cursor + 2) * 4, link=True) is None):
                continue
            first, second = ((body[cursor] >> 10) & 0xFFF), ((body[cursor + 3] >> 10) & 0xFFF)
            if motion + first == geometry["primitive_cframe_offset"] and second - first == 72:
                rows.append({"velocity": motion + first + 48, "velocity_mirror": motion + second + 48,
                             "pv_copy": start + index * 4, "copy_site": start + (index + cursor) * 4,
                             "copy_words": body[cursor:cursor + 4]})
    return rows


def inspect_physics_accessors(mach):
    geometry = inspect_geometry_accessors(mach)["selected"]
    collision, velocity = [], []
    if geometry is not None:
        for name, value_type in (("CanCollide", "bE"), ("AssemblyLinearVelocity", "NS_7Vector3EE")):
            for site, getter, constructor in _registrations(mach, name):
                owner = _part_owner(mach, constructor, value_type)
                adjustment = _this_adjustment(mach, owner["dispatch"]) if owner else None
                if adjustment is None:
                    continue
                if name == "CanCollide":
                    row = decode_collision(mach, getter, adjustment)
                    if row and row["part_primitive"] == geometry["basepart_primitive_offset"]:
                        collision.append({**row, "registration": site, "owner": owner})
                else:
                    for table in _part_vtables(mach, adjustment):
                        raw = mach.read_vaddr(table + 16, 8)
                        if len(raw) != 8:
                            continue
                        thunk = struct.unpack("<Q", raw)[0]
                        words = _words(mach, thunk, 8)
                        target = _branch_target(words[1], thunk + 4) if len(words) == 2 else None
                        if target is None or words[0] != (0xD1000000 | (adjustment << 10)):
                            continue
                        for links in decode_assembly_links(mach, target, geometry):
                            for caches in _velocity_caches(mach, geometry, links["motion_offset"]):
                                velocity.append({**links, **caches, "registration": site, "owner": owner})
    selected = {}
    if len({(row["collision_flags"], row["collision_mask"]) for row in collision}) == 1:
        selected.update(collision_flags=collision[0]["collision_flags"], collision_mask=collision[0]["collision_mask"])
    keys = ("primitive_assembly", "assembly_adjustment", "assembly_root", "root_adjustment",
            "motion_offset", "velocity", "velocity_mirror")
    if len({tuple(row[key] for key in keys) for row in velocity}) == 1:
        selected.update({key: velocity[0][key] for key in keys})
    return {"binary_sha256": hashlib.sha256(mach.blob).hexdigest(), "selected": selected,
            "collision": collision, "velocity": velocity,
            "limitations": ["Static fields and instruction paths only, not live behavior.",
                             "External writes bypass contact notifications, wakeups, and PV dirty counters.",
                              "Runtime jump writes validate a known local assembly root and paired PV frames; live engine acceptance is unverified."]}
