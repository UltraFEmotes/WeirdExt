"""rbxl.memory — external memory access to a remote arm64 process via Mach VM.

task_for_pid() against a hardened-runtime target (Roblox ships Hyperion on
Apple silicon) returns KERN_FAILURE (5) when the caller is not root or the
target's task port is protected. Run the loader under `sudo`; if it still
fails with KERN_PROTECTION_FAILURE (2) the task port is guarded by the
platform and no amount of retrying will change that.
"""

from __future__ import annotations

import ctypes
import ctypes.util
import struct
import subprocess
import threading

KERN_SUCCESS = 0
KERN_INVALID_ADDRESS = 1
KERN_PROTECTION_FAILURE = 2
KERN_FAILURE = 5

VM_REGION_BASIC_INFO_64 = 9
KR_NAMES = {
    1: "KERN_INVALID_ADDRESS",
    2: "KERN_PROTECTION_FAILURE",
    3: "KERN_NO_SPACE",
    4: "KERN_INVALID_ARGUMENT",
    5: "KERN_FAILURE",
    6: "KERN_RESOURCE_SHORTAGE",
}

USER_SPACE_MIN = 0x1_0000_0000
USER_SPACE_MAX = 0xFFFF_FFFF_FFFF

_lib = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True)

_kern_return_t = ctypes.c_int
_mach_port_t = ctypes.c_uint
_mach_vm_address_t = ctypes.c_uint64
_mach_vm_size_t = ctypes.c_uint64


class VmRegionBasicInfo64(ctypes.Structure):
    # boolean_t is an int in mach/vm_region.h — sizing shared/reserved as bytes
    # shrinks the struct to 32 and the kernel rejects count=8 with
    # KERN_INVALID_ARGUMENT. Real layout is 40 bytes, count 10.
    _fields_ = [
        ("protection", ctypes.c_int),
        ("max_protection", ctypes.c_int),
        ("inheritance", ctypes.c_uint),
        ("shared", ctypes.c_int),
        ("reserved", ctypes.c_int),
        ("offset", ctypes.c_uint64),
        ("behavior", ctypes.c_int),
        ("user_wired_count", ctypes.c_ushort),
    ]


_lib.task_for_pid.argtypes = [_mach_port_t, ctypes.c_int, ctypes.POINTER(_mach_port_t)]
_lib.task_for_pid.restype = _kern_return_t

_lib.mach_port_deallocate.argtypes = [_mach_port_t, _mach_port_t]
_lib.mach_port_deallocate.restype = _kern_return_t

_lib.mach_vm_read_overwrite.argtypes = [
    _mach_port_t,
    _mach_vm_address_t,
    _mach_vm_size_t,
    _mach_vm_address_t,
    ctypes.POINTER(_mach_vm_size_t),
]
_lib.mach_vm_read_overwrite.restype = _kern_return_t

_lib.mach_vm_region.argtypes = [
    _mach_port_t,
    ctypes.POINTER(_mach_vm_address_t),
    ctypes.POINTER(_mach_vm_size_t),
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(_mach_port_t),  # object_name out port — omit it and libffi
]                                # feeds the kernel a garbage 7th argument
_lib.mach_vm_region.restype = _kern_return_t

_lib.proc_regionfilename.argtypes = [
    ctypes.c_int,
    ctypes.c_uint64,
    ctypes.c_char_p,
    ctypes.c_uint32,
]
_lib.proc_regionfilename.restype = ctypes.c_int

try:
    _SELF_TASK = ctypes.c_uint.in_dll(_lib, "mach_task_self_").value
except ValueError:  # pragma: no cover - only on very old SDK layouts
    _SELF_TASK = 0


class MemoryFault(Exception):
    """A read touched an unmapped or unreadable address."""


def is_plausible_pointer(value: int) -> bool:
    """User-space range check for *byte addresses*. Alignment is a pointer-value
    property (see dumper.prims.plausible_ptr), not an address property: strings
    and raw byte reads land wherever they land."""
    return USER_SPACE_MIN <= value < USER_SPACE_MAX


ROBLOX_NAMES = ("RobloxPlayer", "RobloxPlayerBeta", "Roblox")


def roblox_candidates(ps_output: str) -> list[tuple[int, int]]:
    """(pid, rss_kb) for processes whose executable name matches the client.

    Several Roblox-named processes can run at once; the real game client is
    the multi-GB one, so callers pick by footprint instead of by line order.
    """
    out = []
    for line in ps_output.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) != 3:
            continue
        pid_text, rss_text, comm = parts
        name = comm.rsplit("/", 1)[-1]
        if name not in ROBLOX_NAMES:
            continue
        try:
            out.append((int(pid_text), int(rss_text)))
        except ValueError:
            continue
    return out


def find_roblox_candidates() -> list[tuple[int, int]]:
    try:
        out = subprocess.run(
            ["ps", "-axo", "pid=,rss=,comm="],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    return roblox_candidates(out)


def find_roblox_pid() -> int | None:
    """The running Roblox CLIENT: the matching process with the largest RSS."""
    candidates = find_roblox_candidates()
    if not candidates:
        return None
    return max(candidates, key=lambda c: c[1])[0]


class MachProcess:
    """Read-only handle on another process' address space."""

    def __init__(self, pid: int):
        self.pid = pid
        self._local = threading.local()
        port = _mach_port_t(0)
        kr = _lib.task_for_pid(_SELF_TASK, pid, ctypes.byref(port))
        if kr != KERN_SUCCESS:
            raise MemoryFault(
                f"task_for_pid({pid}) failed: {KR_NAMES.get(kr, kr)}. "
                f"Re-run with sudo; a hardened target refuses task ports otherwise."
            )
        self.task = port.value

    def close(self):
        """Release this handle's task send right; callers must stop reads first."""
        task = self.task
        self.task = 0
        if task:
            _lib.mach_port_deallocate(_SELF_TASK, task)

    # -- raw reads ---------------------------------------------------------
    def _scratch(self, size: int) -> ctypes.Array:
        buf = getattr(self._local, "buf", None)
        if buf is None or len(buf) < size:
            buf = ctypes.create_string_buffer(max(size, 0x2000))
            self._local.buf = buf
        return buf

    def read(self, address: int, size: int) -> bytes:
        if size <= 0:
            return b""
        if not is_plausible_pointer(address):
            raise MemoryFault(f"refusing implausible address {address:#x}")
        buf = self._scratch(size)
        out_size = _mach_vm_size_t(0)
        kr = _lib.mach_vm_read_overwrite(
            self.task,
            _mach_vm_address_t(address),
            _mach_vm_size_t(size),
            _mach_vm_address_t(ctypes.addressof(buf)),
            ctypes.byref(out_size),
        )
        if kr != KERN_SUCCESS or out_size.value != size:
            raise MemoryFault(
                f"read {size:#x} at {address:#x} failed: {KR_NAMES.get(kr, kr)}"
            )
        # Slice the requested bytes directly: .raw copies the whole reusable
        # allocation (at least 8 KiB) even for an 8-byte pointer read.
        return buf[:size]

    # -- typed reads -------------------------------------------------------
    def u8(self, address: int) -> int:
        return self.read(address, 1)[0]

    def i32(self, address: int) -> int:
        return struct.unpack("<i", self.read(address, 4))[0]

    def u32(self, address: int) -> int:
        return struct.unpack("<I", self.read(address, 4))[0]

    def u64(self, address: int) -> int:
        return struct.unpack("<Q", self.read(address, 8))[0]

    def f32(self, address: int) -> float:
        return struct.unpack("<f", self.read(address, 4))[0]

    def f32s(self, address: int, count: int) -> list[float]:
        return list(struct.unpack(f"<{count}f", self.read(address, 4 * count)))

    def i32s(self, address: int, count: int) -> list[int]:
        return list(struct.unpack(f"<{count}i", self.read(address, 4 * count)))

    def safe_u64(self, address: int) -> int:
        try:
            return self.u64(address)
        except MemoryFault:
            return 0

    # -- regions -----------------------------------------------------------
    def regions(self, limit: int = 8192):
        """Yield (start, size, path, protection) for the top-level VM regions."""
        address = _mach_vm_address_t(1)
        info = VmRegionBasicInfo64()
        count = ctypes.c_uint(ctypes.sizeof(VmRegionBasicInfo64) // 4)
        name_buf = ctypes.create_string_buffer(4096)
        object_name = _mach_port_t(0)

        for _ in range(limit):
            size = _mach_vm_size_t(0)
            count.value = ctypes.sizeof(VmRegionBasicInfo64) // 4
            kr = _lib.mach_vm_region(
                self.task,
                ctypes.byref(address),
                ctypes.byref(size),
                VM_REGION_BASIC_INFO_64,
                ctypes.byref(info),
                ctypes.byref(count),
                ctypes.byref(object_name),
            )
            if object_name.value:
                _lib.mach_port_deallocate(_SELF_TASK, object_name.value)
                object_name.value = 0
            if kr != KERN_SUCCESS or size.value == 0:
                return
            path = ""
            n = _lib.proc_regionfilename(
                self.pid, address.value, name_buf, ctypes.sizeof(name_buf)
            )
            if n > 0:
                path = name_buf.value.decode("utf-8", "replace")
            yield address.value, size.value, path, info.protection

            next_addr = address.value + size.value
            if next_addr <= address.value:
                return
            address = _mach_vm_address_t(next_addr)

    def main_image_base(self, executable_name: str = "RobloxPlayer") -> int | None:
        """Lowest region belonging to the client's main executable = module base."""
        best: int | None = None
        for start, _size, path, _prot in self.regions():
            if not path:
                continue
            if path.rsplit("/", 1)[-1].startswith(executable_name):
                if best is None or start < best:
                    best = start
        return best
