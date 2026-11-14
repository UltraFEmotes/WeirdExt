"""dumper.macho — minimal Mach-O 64 reader for the client image.

The binary carries its own class map: every C++ vtable is preceded by a
pointer to a typeinfo record whose name field is the mangled class
(`N3RBX9WorkspaceE`). Parsing the on-disk image turns "is this pointer an
Instance?" from a heuristic into a lookup — segment vmaddrs give the slide,
sections give the data ranges a vtable can live in.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

MH_MAGIC_64 = 0xFEEDFACF
LC_SEGMENT_64 = 0x19

DATA_SEGMENTS = ("__DATA_CONST", "__DATA", "__AUTH_CONST", "__AUTH", "__DATA_DIRTY")


@dataclass(frozen=True)
class Section:
    segname: str
    name: str
    addr: int
    size: int
    offset: int

    @property
    def end(self) -> int:
        return self.addr + self.size


@dataclass(frozen=True)
class Segment:
    name: str
    vmaddr: int
    vmsize: int
    fileoff: int
    filesize: int
    init_prot: int


class MachOError(Exception):
    pass


class MachO:
    """Segment/section table plus virtual-address reads from the file."""

    def __init__(self, path: str):
        self.path = path
        with open(path, "rb") as handle:
            self.blob = handle.read()
        self.segments: list[Segment] = []
        self.sections: list[Section] = []
        self._parse()

    @property
    def text_vmaddr(self) -> int:
        for segment in self.segments:
            if segment.name == "__TEXT":
                return segment.vmaddr
        return self.segments[0].vmaddr if self.segments else 0

    def _parse(self):
        blob = self.blob
        if len(blob) < 32:
            raise MachOError("file too short to be Mach-O")
        magic = struct.unpack_from("<I", blob, 0)[0]
        if magic != MH_MAGIC_64:
            raise MachOError(f"not a 64-bit Mach-O (magic {magic:#x})")
        ncmds, sizeofcmds = struct.unpack_from("<II", blob, 16)
        offset = 32
        end = min(len(blob), 32 + sizeofcmds)
        while offset + 8 <= end and len(self.segments) < 256:
            cmd, cmdsize = struct.unpack_from("<II", blob, offset)
            if cmdsize < 8:
                break
            if cmd == LC_SEGMENT_64:
                name = blob[offset + 8:offset + 24].split(b"\0", 1)[0].decode("latin-1")
                vmaddr, vmsize, fileoff, filesize, _maxp, initp, nsects, _fl = (
                    struct.unpack_from("<QQQQIIII", blob, offset + 24)
                )
                self.segments.append(Segment(name, vmaddr, vmsize, fileoff, filesize, initp))
                sect = offset + 72
                for _ in range(nsects):
                    if sect + 80 > len(blob):
                        break
                    sname = blob[sect:sect + 16].split(b"\0", 1)[0].decode("latin-1")
                    gname = blob[sect + 16:sect + 32].split(b"\0", 1)[0].decode("latin-1")
                    addr, size = struct.unpack_from("<QQ", blob, sect + 32)
                    soff = struct.unpack_from("<I", blob, sect + 48)[0]
                    self.sections.append(Section(gname, sname, addr, size, soff))
                    sect += 80
            offset += cmdsize
        del ncmds

    # -- address translation ---------------------------------------------
    def read_vaddr(self, vaddr: int, size: int) -> bytes:
        for segment in self.segments:
            if segment.vmaddr <= vaddr < segment.vmaddr + segment.filesize:
                delta = vaddr - segment.vmaddr
                start = segment.fileoff + delta
                return self.blob[start:start + size]
        return b""

    def vaddr_to_file(self, vaddr: int) -> int | None:
        for segment in self.segments:
            if segment.vmaddr <= vaddr < segment.vmaddr + segment.filesize:
                return segment.fileoff + (vaddr - segment.vmaddr)
        return None

    def sections_of(self, names) -> list[Section]:
        wanted = set(names)
        return [s for s in self.sections if s.name in wanted]

    def data_spans(self) -> list[tuple[int, int]]:
        """Virtual ranges that can legally hold a vtable pointer target."""
        spans = []
        for segment in self.segments:
            if segment.name in DATA_SEGMENTS and segment.vmsize:
                spans.append((segment.vmaddr, segment.vmaddr + segment.vmsize))
        return spans

    def text_spans(self) -> list[tuple[int, int]]:
        return [
            (segment.vmaddr, segment.vmaddr + segment.vmsize)
            for segment in self.segments
            if segment.name == "__TEXT"
        ]


def client_binary(regions) -> str | None:
    """Path of the running client's main executable, from the region map."""
    best = None
    for start, size, path, _prot in regions:
        if not path:
            continue
        base = path.rsplit("/", 1)[-1]
        if not base.startswith("Roblox"):
            continue
        if base.endswith(".dat") or ".framework" in path:
            continue
        if best is None or start < best[0]:
            best = (start, path)
    return best[1] if best else None


def image_slide(mach: MachO, regions) -> int | None:
    """live __TEXT base minus the file's __TEXT vmaddr."""
    lowest = None
    for start, size, path, _prot in regions:
        if not path:
            continue
        if path != mach.path:
            continue
        if lowest is None or start < lowest:
            lowest = start
    if lowest is None:
        return None
    return lowest - mach.text_vmaddr
