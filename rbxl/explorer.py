"""Bounded, read-only game tree snapshots for the Explorer window.

Every walk carries hard caps: node count, depth, per-node children, wall
clock. Truncated branches are labeled so the picture never lies about being
complete. No writes, no heap scans — children come from the solved layout.
"""
from __future__ import annotations

import time

MAX_NODES = 2000
MAX_DEPTH = 8
MAX_KIDS = 64
BUDGET_SECONDS = 4.0


def build_tree(reader, root, max_nodes=MAX_NODES, max_depth=MAX_DEPTH,
               max_kids=MAX_KIDS, budget_seconds=BUDGET_SECONDS):
    """Nested {name, cls, kids, truncated} dicts; dedupes by address."""
    started = time.monotonic()
    nodes = 0

    def visit(address, depth, seen):
        nonlocal nodes
        if address in seen or nodes >= max_nodes:
            return {"name": "…", "truncated": True, "kids": []}
        seen.add(address)
        nodes += 1
        node = {"name": reader.name(address) or "?",
                "cls": reader.klass(address) or "?", "kids": []}
        if depth >= max_depth or nodes >= max_nodes:
            node["truncated"] = True
            return node
        if time.monotonic() - started > budget_seconds:
            node["truncated"] = True
            return node
        truncated = False
        for child in list(reader.children(address, limit=max_kids))[:max_kids]:
            if nodes >= max_nodes or time.monotonic() - started > budget_seconds:
                truncated = True
                break
            node["kids"].append(visit(child, depth + 1, seen))
        if len(node["kids"]) == max_kids:
            truncated = True
        if truncated:
            node["truncated"] = True
        return node

    return visit(root, 0, set())
