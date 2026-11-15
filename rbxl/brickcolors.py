"""Roblox BrickColor numbers to RGB, from Roblox's published BrickColor reference."""
import json
from pathlib import Path

_PALETTE = {int(number): tuple(entry["rgb"]) for number, entry in
            json.loads((Path(__file__).with_name("brickcolors.json")).read_text(encoding="utf-8"))["colors"].items()}


def rgb(number):
    """(r, g, b) 0-255 for a BrickColor number, or None for an unknown number."""
    return _PALETTE.get(number)
