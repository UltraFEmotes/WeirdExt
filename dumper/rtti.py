"""dumper.rtti — resolve heap objects to their C++ class through RTTI.

An object whose first qword is a vtable address is polymorphic. The vtable's
`[-1]` slot points at a typeinfo record whose `+8` field is the mangled class
name. So one pointer, three reads, and the heap stops being anonymous bytes:
`this is an RBX::Workspace`, `this is an RBX::Humanoid`.

The client ships ~17k `N3RBX...` typeinfo names, so the class map is complete
without a symbol table, a PDB, or a single number from a previous dump.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

from rbxl.memory import MemoryFault

from . import macho as macho_mod

MAX_NAME = 512


def simplify(mangled: str) -> str:
    """`N3RBX9WorkspaceE` -> `RBX::Workspace`; leaves non-nested names alone."""
    if not mangled.startswith("N"):
        return mangled
    out = []
    index = 1
    while index < len(mangled):
        char = mangled[index]
        if char == "E":
            break
        if char.isdigit():
            digits = index
            while digits < len(mangled) and mangled[digits].isdigit():
                digits += 1
            length = int(mangled[index:digits])
            piece = mangled[digits:digits + length]
            if not piece:
                return mangled
            out.append(piece)
            index = digits + length
            continue
        # substitutions / templates / qualifiers: give up on the pretty form
        return mangled
    if not out:
        return mangled
    return "::".join(out)


@dataclass(frozen=True)
class ClassRef:
    vtable: int
    typeinfo: int
    mangled: str
    name: str


class ImageModel:
    """The client image as addressable bytes: data spans preloaded so class
    resolution costs slicing, not syscalls."""

    def __init__(self, mem, regions, verbose: bool = False, path: str | None = None):
        self.mem = mem
        self.regions = list(regions)
        self.verbose = verbose
        path = path or macho_mod.client_binary(self.regions)
        if not path:
            raise macho_mod.MachOError("no Roblox client binary in the region map")
        self.path = path
        self.mach = macho_mod.MachO(path)
        slide = macho_mod.image_slide(self.mach, self.regions)
        if slide is None:
            raise macho_mod.MachOError(f"client image {path} is not mapped")
        self.slide = slide
        self.data_spans = [(lo + slide, hi + slide) for lo, hi in self.mach.data_spans()]
        self.text_spans = [(lo + slide, hi + slide) for lo, hi in self.mach.text_spans()]
        self._blobs: list[tuple[int, int, bytes]] = []
        self._class_cache: dict[int, ClassRef | None] = {}
        self._preload()

    # -- preloading --------------------------------------------------------
    def _preload(self):
        for segment in self.mach.segments:
            if segment.name == "__PAGEZERO" or not segment.filesize:
                continue
            if segment.init_prot & 1 == 0:
                continue
            lo = segment.vmaddr + self.slide
            size = min(segment.filesize, 512 << 20)
            try:
                data = self.mem.read(lo, size)
            except MemoryFault:
                continue
            self._blobs.append((lo, lo + len(data), data))

    def read(self, vaddr: int, size: int) -> bytes:
        for lo, hi, blob in self._blobs:
            if lo <= vaddr < hi:
                start = vaddr - lo
                if start + size <= len(blob):
                    return blob[start:start + size]
                return blob[start:]
        try:
            return self.mem.read(vaddr, size)
        except MemoryFault:
            return b""

    def cstring(self, vaddr: int, limit: int = MAX_NAME) -> str | None:
        if not any(lo <= vaddr < hi for lo, hi in self.text_spans):
            return None
        raw = self.read(vaddr, limit)
        if not raw:
            return None
        cut = raw.find(b"\0")
        if cut <= 0:
            return None
        chunk = raw[:cut]
        if not all(32 <= b < 127 for b in chunk):
            return None
        return chunk.decode("ascii")

    # -- reverse lookup: class name -> vtables ----------------------------
    def name_vaddr(self, mangled: str) -> int | None:
        needle = mangled.encode()
        for lo, _hi, blob in self._blobs:
            start = 0
            while True:
                index = blob.find(needle, start)
                if index < 0:
                    break
                start = index + 1
                before = blob[index - 1] if index else 0
                after = blob[index + len(needle)] if index + len(needle) < len(blob) else 0
                if 32 <= before < 127 or 32 <= after < 127:
                    continue
                return lo + index
        return None

    def typeinfos_of(self, mangled: str) -> list[int]:
        name_vaddr = self.name_vaddr(mangled)
        if name_vaddr is None:
            return []
        needle = struct.pack("<Q", name_vaddr)
        found = []
        for lo, hi, blob in self._blobs:
            if not self.in_data(lo):
                continue
            start = 0
            while True:
                index = blob.find(needle, start)
                if index < 0:
                    break
                start = index + 1
                if index % 8 == 0:
                    found.append(lo + index - 8)
        return found

    def vtables_of(self, mangled: str) -> list[int]:
        """Every address point an object of this class can carry as its vptr."""
        vtables = []
        for typeinfo in self.typeinfos_of(mangled):
            needle = struct.pack("<Q", typeinfo)
            for lo, hi, blob in self._blobs:
                if not self.in_data(lo):
                    continue
                start = 0
                while True:
                    index = blob.find(needle, start)
                    if index < 0:
                        break
                    start = index + 1
                    if index % 8 == 0:
                        vtables.append(lo + index + 8)
        return sorted(set(vtables))

    # -- class resolution --------------------------------------------------
    def in_data(self, value: int) -> bool:
        return any(lo <= value < hi for lo, hi in self.data_spans)

    def complete_object(self, address: int, max_adjustment: int = 0x10000) -> int | None:
        """Normalize an Itanium C++ base subobject via vtable[-2].

        A secondary vptr identifies the dynamic class but its address is not
        the start of that class's fields. Reject construction vtables with
        positive offset-to-top and require matching RTTI at the proposed top.
        """
        try:
            vptr = self.mem.u64(address)
        except MemoryFault:
            return None
        ref = self.class_of(vptr)
        if ref is None:
            return None
        try:
            raw = self.mem.read(vptr - 16, 8)
        except MemoryFault:
            return None
        if len(raw) != 8:
            return None
        adjustment = struct.unpack("<q", raw)[0]
        if not -max_adjustment <= adjustment <= 0 or adjustment % 8:
            return None
        top = address + adjustment
        if top <= 0 or top % 8:
            return None
        try:
            primary = self.class_of(self.mem.u64(top))
        except MemoryFault:
            return None
        if primary is None or primary.mangled != ref.mangled:
            return None
        return top

    def class_of(self, vtable: int) -> ClassRef | None:
        cached = self._class_cache.get(vtable, 0)
        if cached != 0:
            return cached
        self._class_cache[vtable] = None

        if not self.in_data(vtable):
            return None
        try:
            typeinfo = self.mem.u64(vtable - 8)
        except MemoryFault:
            return None
        if not self.in_data(typeinfo):
            return None
        try:
            nameptr = self.mem.u64(typeinfo + 8)
        except MemoryFault:
            return None
        mangled = self.cstring(nameptr)
        if not mangled:
            return None
        if not (mangled.startswith("N") or mangled[:1].isalpha()):
            return None
        ref = ClassRef(vtable, typeinfo, mangled, simplify(mangled))
        self._class_cache[vtable] = ref
        return ref
