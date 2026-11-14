"""Offline reflection dump: every registered property's field offset, from Mach-O bytes.

Roblox registers each property with a name, a getter and a PropDescriptor
constructor. The constructor installs a PropDescriptor<Class, Type>::GetSetImpl
vtable, whose RTTI name gives the class and value type, and whose dispatch
thunk adds the class's property-base adjustment. The getter is usually one
load from the object, so field offset = adjustment + load displacement.

Only recognised instruction shapes are decoded. Shapes marked heuristic are
returned separately and must be confirmed live before anyone relies on them.
No process is opened and no code is executed.
"""
from __future__ import annotations

from collections import defaultdict
import re
import struct

import numpy as np

from .arm64_accessors import _address_pair, _branch_target, _rtti_name, _words

DESCRIPTORS = ("N3RBX10Reflection14PropDescriptorI", "N3RBX10Reflection17RefPropDescriptorI",
               "N3RBX10Reflection18EnumPropDescriptorI")
BUILTIN = {"b": "bool", "c": "char", "h": "uint8", "s": "int16", "t": "uint16", "i": "int", "j": "uint",
           "l": "int64", "m": "uint64", "x": "int64", "y": "uint64", "f": "float", "d": "double"}
RET = 0xD65F03C0
REGISTRATION_WINDOW = 24   # instructions after the name load that may hold the getter and constructor call
# (mask, value, bytes) for a load into the return register from x0.
RETURN_LOADS = ((0xFFC003FF, 0xBD400000, 4), (0xFFC003FF, 0xFD400000, 8), (0xFFC003FF, 0xB9400000, 4),
                (0xFFC003FF, 0xF9400000, 8), (0xFFC003FF, 0x39400000, 1), (0xFFC003FF, 0x79400000, 2),
                (0xFFC003FF, 0x3DC00000, 16))
EXACT = {"load", "first-load", "reference", "pair-load", "string", "shared-pair", "q-pair", "pointer"}


def _immediate(word, scale=1):
    return ((word >> 10) & 0xFFF) * scale << (12 if scale == 1 and word & (1 << 22) else 0)


def _type_name(mangled):
    """One Itanium <type> in the forms these descriptors use; returns (name, rest)."""
    if mangled[:1] in BUILTIN:
        return BUILTIN[mangled[0]], mangled[1:]
    if mangled.startswith("N"):
        rest, parts = mangled[1:], []
        while rest and not rest.startswith("E"):
            if rest.startswith(("S_", "St")):
                parts.append("std" if rest.startswith("St") else "RBX")
                rest = rest[2:]
                continue
            match = re.match(r"\d+", rest)
            if not match:
                return None, rest
            length, start = int(match.group()), len(match.group())
            parts.append(rest[start:start + length])
            rest = rest[start + length:]
            if rest.startswith("I"):  # skip template arguments
                depth = 0
                for index, char in enumerate(rest):
                    depth += char == "I"
                    depth -= char == "E"
                    if depth == 0:
                        rest = rest[index + 1:]
                        break
        return "::".join(part for part in parts if part != "RBX"), rest[1:]
    match = re.match(r"\d+", mangled)
    if match:
        length, start = int(match.group()), len(match.group())
        return mangled[start:start + length], mangled[start + length:]
    return None, mangled


KINDS = {DESCRIPTORS[0]: "value", DESCRIPTORS[1]: "reference", DESCRIPTORS[2]: "enum"}


def descriptor_types(mangled):
    """(class, value type, kind) from a PropDescriptor-family RTTI name."""
    for prefix in DESCRIPTORS:
        if mangled.startswith(prefix):
            cls, rest = _type_name(mangled[len(prefix):])
            value, _ = _type_name(rest) if rest else (None, None)
            kind = KINDS[prefix]
            if kind == "reference":
                value = "Instance"
            elif value and "basic_string" in value:
                value = "string"
            return cls, value, kind
    return None, None, None


def _cstring(mach, address):
    raw = mach.read_vaddr(address, 128).split(b"\0", 1)[0]
    try:
        return raw.decode("ascii")
    except UnicodeDecodeError:
        return None


def registrations(mach):
    """(name address, getter, constructor) for every `adrp/add x1, name ... adrp/add x3, getter ... bl`."""
    cstrings = [(section.addr, section.addr + section.size) for section in mach.sections if section.name == "__cstring"]
    text = next(section for section in mach.sections if section.name == "__text")
    words = np.frombuffer(mach.blob[text.offset:text.offset + text.size // 4 * 4], dtype="<u4")
    for raw_index in np.nonzero((words & np.uint32(0x9F00001F)) == np.uint32(0x90000001))[0]:  # adrp x1
        index = int(raw_index)
        if index + 1 >= len(words):
            continue
        pair = _address_pair(int(words[index]), int(words[index + 1]), text.addr + index * 4)
        if not pair or pair[0] != 1 or not any(low <= pair[1] < high for low, high in cstrings):
            continue
        getter = None
        for cursor in range(index + 2, min(index + REGISTRATION_WINDOW, len(words) - 1)):
            pc = text.addr + cursor * 4
            loaded = _address_pair(int(words[cursor]), int(words[cursor + 1]), pc)
            if loaded and loaded[0] == 3:
                getter = loaded[1]
            constructor = _branch_target(int(words[cursor]), pc, link=True)
            if constructor is not None:
                if getter is not None and text.addr <= getter < text.addr + text.size:
                    yield pair[1], getter, constructor
                break


def descriptor_owner(mach, constructor):
    """(vtable, mangled RTTI, dispatch) of the GetSetImpl the constructor installs, or None."""
    words = _words(mach, constructor, 0x200)
    for index in range(len(words) - 1):
        pair = _address_pair(words[index], words[index + 1], constructor + index * 4)
        if not pair:
            continue
        name = _rtti_name(mach, pair[1])
        if name and name.startswith(DESCRIPTORS) and "GetSetImpl" in name:
            raw = mach.read_vaddr(pair[1] + 32, 8)
            if len(raw) == 8:
                return pair[1], name, struct.unpack("<Q", raw)[0]
    return None


def this_adjustment(mach, dispatch):
    """Offset of the class's property base: the dispatch thunk's add/sub arithmetic on the
    instance pointer (x1), followed through the register it lands in (e.g. sub then add)."""
    register, total = None, None
    for word in _words(mach, dispatch, 48):
        if (word & 0x7F800000) not in (0x11000000, 0x51000000) or not word >> 31:   # 64-bit ADD/SUB immediate
            if total is not None and (word & 0xFFC00000) in (0xA9400000, 0xF9400000):   # first load: done
                break
            continue
        source, destination = (word >> 5) & 31, word & 31
        amount = _immediate(word) * (-1 if word & 0x40000000 else 1)
        if source == 1 and total is None:
            register, total = destination, amount
        elif total is not None and source == register == destination:
            total += amount
    return total or 0


def _object_loads(words):
    """Displacements loaded from the object pointer (x0 or copies) before the first return."""
    aliases, seen = {0}, []
    for word in words[:30]:
        if (word & 0xFFE0FFE0) == 0xAA0003E0 and ((word >> 16) & 31) in aliases:   # mov xD, xS
            aliases.add(word & 31)
            continue
        base, target = (word >> 5) & 31, word & 31
        if (word & 0x3B000000) == 0x39000000 and (word >> 22) & 1 and base in aliases:   # LDR unsigned imm
            size = 16 if (word >> 26) & 1 and (word >> 23) & 1 else 1 << (word >> 30)
            seen.append(((word >> 10) & 0xFFF) * size)
        elif (word & 0x7F800000) == 0x11000000 and base in aliases and target not in aliases:
            seen.append(_immediate(word))
        if (word & 0xFFFFFC1F) == 0xD65F0000:
            break
    return seen


def decode_getter(mach, getter, base=0, depth=0):
    """Field location for one getter, or None. `how` names the recognised shape."""
    words = _words(mach, getter, 120)
    if len(words) < 2:
        return None
    first = words[0]
    for mask, value, size in RETURN_LOADS:
        if first & mask == value:
            return {"offset": base + ((first >> 10) & 0xFFF) * size, "how": "load" if words[1] == RET else "first-load"}
    if (first & 0xFFC003FF) == 0x91000000 and words[1] == RET:                 # add x0, x0, #imm  (const T&)
        return {"offset": base + _immediate(first), "how": "reference"}
    if (first & 0xFFC003FF) in (0x2D400000, 0x6D400000):                       # ldp s/d, [x0, #imm]
        return {"offset": base + ((first >> 15) & 0x7F) * (4 if first & 0x40000000 == 0 else 8), "how": "pair-load"}
    if (first & 0xFFC003E0) == 0xA9400000:                                     # ldp xA, xB, [x0]  (shared_ptr)
        return {"offset": base + ((first >> 15) & 0x7F) * 8, "how": "shared-pair"}
    if (first & 0xFFC003E0) == 0xAD400000:                                     # ldp qA, qB, [x0]  (CFrame)
        return {"offset": base + ((first >> 15) & 0x7F) * 16, "how": "q-pair"}
    if (first & 0xFFC003E0) == 0x39C00000:                                     # ldrsb: libc++ string size byte
        return {"offset": base + ((first >> 10) & 0xFFF) - 23, "how": "string"}
    if (first & 0xFF8003FF) in (0xD1000000, 0x91000000) and depth < 3:         # sub/add x0, x0, #imm; b target
        delta = _immediate(first) * (-1 if (first & 0xFF8003FF) == 0xD1000000 else 1)
        target = _branch_target(words[1], getter + 4)
        if target is not None:
            return decode_getter(mach, target, base + delta, depth + 1)
    if (first & 0xFFC003FF) == 0xF9400008:                                     # ldr x8, [x0, #a]; ldr r, [x8, #b]
        second = words[1]
        for mask, value, size in RETURN_LOADS:
            if (second & 0xFFC0001F) == (value & 0xFFC0001F) and (second >> 5) & 31 == 8:
                return {"offset": base + ((first >> 10) & 0xFFF) * 8, "then": ((second >> 10) & 0xFFF) * size,
                        "how": "pointer"}
    if (first & 0x9F000000) == 0x90000000:                                     # adrp: a global, not a field
        return {"how": "global"}
    seen = _object_loads(words)
    if not seen:
        return None
    pair = [offset for offset in seen if offset + 8 in seen]   # smart pointer: (object, control block)
    return {"offset": base + (pair[0] if pair else seen[0]), "how": "heuristic"}


def reflect(mach):
    """{"exact": {class: {name: entry}}, "heuristic": {...}, "conflicts": [...], "counts": {...}}."""
    owners, exact, heuristic, conflicts = {}, defaultdict(dict), defaultdict(dict), []
    counts = defaultdict(int)
    for name_address, getter, constructor in registrations(mach):
        if constructor not in owners:
            owners[constructor] = descriptor_owner(mach, constructor)
        owner = owners[constructor]
        if owner is None:
            continue
        counts["registrations"] += 1
        name = _cstring(mach, name_address)
        cls, value_type, kind = descriptor_types(owner[1])
        decoded = decode_getter(mach, getter)
        if not name or not cls or decoded is None:
            counts["unresolved"] += 1
            continue
        if decoded["how"] == "global":
            counts["global"] += 1
            continue
        entry = {"type": value_type, "kind": kind, "offset": this_adjustment(mach, owner[2]) + decoded["offset"],
                 "how": decoded["how"]}
        if "then" in decoded:
            entry["then"] = decoded["then"]
        table = exact if decoded["how"] in EXACT else heuristic
        previous = table[cls].get(name)
        if previous and (previous["offset"], previous.get("then")) != (entry["offset"], entry.get("then")):
            conflicts.append((cls, name, previous, entry))
            continue
        table[cls][name] = entry
        counts[decoded["how"]] += 1
    for cls, name, _, _ in conflicts:   # one name, two readings: publish neither
        exact.get(cls, {}).pop(name, None)
        heuristic.get(cls, {}).pop(name, None)
    return {"exact": dict(exact), "heuristic": dict(heuristic), "conflicts": conflicts, "counts": dict(counts)}
