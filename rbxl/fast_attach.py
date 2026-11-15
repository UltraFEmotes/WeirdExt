"""Instant attach: a client module global that leads to the live DataModel.

find_chain() searches the heap objects referenced from the client's own data
segments (no heap sweep) for a pointer path to the DataModel. learn() verifies
a found path by attaching through it and saves it in the profile, so the next
attach takes a few reads instead of a full sweep.
"""
from __future__ import annotations

from dataclasses import replace
import json

from dumper import prims
from dumper.solve import WalkError
from .memory import MemoryFault
from .profiles import write_json

OBJECT_WINDOW = 0x1000  # bytes of each object searched for the next pointer


def _qwords(data):
    usable = len(data) - len(data) % 8
    return enumerate(memoryview(data)[:usable].cast("Q"))


def _window(mem, address, size):
    while size >= 0x80:
        try:
            return mem.read(address, size)
        except MemoryFault:
            size //= 2
    return b""


def find_chain(reader):
    """(module-relative slot, hops) from a global to reader.root, or None.

    One-hop chains win; two-hop chains go through an object whose RTTI class is
    DataModel (Roblox's FakeDataModel)."""
    mem, model, real = reader.mem, reader.model, reader.root
    base = mem.main_image_base()
    spans = model.data_spans + model.text_spans
    module = min(lo for lo, _ in spans), max(hi for _, hi in spans)

    def heap_pointer(value):
        return prims.plausible_ptr(value) and not module[0] <= value < module[1]

    globals_ = {}
    for lo, hi in model.data_spans:
        for index, value in _qwords(model.read(lo, hi - lo)):
            if heap_pointer(value):
                globals_.setdefault(value, lo + index * 8 - base)
    chains, middles = [], {}
    for target, slot in globals_.items():
        for index, value in _qwords(_window(mem, target, OBJECT_WINDOW)):
            if value == real:
                chains.append((slot, (index * 8,)))
            elif heap_pointer(value) and value not in globals_:
                middles.setdefault(value, (slot, index * 8))
    if not chains:
        for fake in [value for value in middles if value != real and reader.klass(value) == "RBX::DataModel"]:
            slot, first = middles[fake]
            for index, value in _qwords(_window(mem, fake, OBJECT_WINDOW)):
                if value == real:
                    chains.append((slot, (first, index * 8)))
    if not chains:
        return None
    return min(chains, key=lambda chain: (len(chain[1]), chain[0]))


def learn(reader, profile):
    """Find, verify and save a chain for this reader's DataModel; returns the updated spec or None."""
    from .esp_reader import ESPReader  # deferred: esp_reader imports this module's users

    chain = find_chain(reader)
    if chain is None:
        return None
    slot, hops = chain
    spec = replace(reader.spec, fast_slot=slot, fast_hops=tuple(hops))
    try:
        if ESPReader._fast_attach(reader.mem, spec).root != reader.root:
            return None
    except (WalkError, MemoryFault, RuntimeError):
        return None
    path = profile / "offsets.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    report["fast_attach"] = {"slot": slot, "hops": list(hops),
                             "method": "module global chain resolved to the live DataModel"}
    write_json(path, report)
    return spec
