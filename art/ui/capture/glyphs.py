#!/usr/bin/env python3
"""Build the kit's flat ink and white glyphs from existing lk_ icons.

The mockups draw section and tab glyphs as flat dark ink (white on leather);
the kit sheets only hold full-colour icons. Each glyph here is one lk_icon_*
recoloured: "solid" keeps the whole silhouette, "line" drops the icon's light
fills so its dark drawing reads as line art (a magnifier's lens, a book's
pages). Writes art/ui/sprites/lk_glyph_ink_<id>.png and lk_glyph_white_<id>.png
and prints their manifest entries for the asset artist's manifest and GROUPS.

    python3 art/ui/capture/glyphs.py

Where the sheets have no drawing of the mockup's glyph, the closest icon stands
in (the "source" column; KIT.md lists them).
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SPRITES = ROOT / "art" / "ui" / "sprites"
COLOURS = {"ink": (0x22, 0x0A, 0x01), "white": (0xFF, 0xFF, 0xFE)}

# glyph id: (source icon, mode)
GLYPHS = {
    "gamepad": ("compass", "line"),  # no gamepad drawing in the kit
    "speaker": ("speech", "line"),  # no speaker drawing in the kit
    "monitor": ("map", "line"),  # no monitor drawing in the kit
    "gears": ("gear_alt", "solid"),
    "refresh": ("compass_arrow", "solid"),  # no circular-arrow drawing in the kit
    "people": ("party", "solid"),
    "magnifier": ("magnifier", "line"),
    "info": ("exclamation", "solid"),  # the kit has "!" but no circled "i"
    "check": ("check", "solid"),
    "anvil": ("anvil", "solid"),
    "book": ("journal", "line"),
    "trophy": ("trophy", "line"),
    "map_pin": ("map_pin", "solid"),
    "backpack": ("backpack", "solid"),
    "chest": ("chest", "line"),
    "hammer": ("hammer", "solid"),
    "compass": ("compass", "line"),
    "compass_rose": ("compass_arrow", "line"),
}


def build(source: Path, mode: str, rgb):
    a = np.asarray(Image.open(source).convert("RGBA")).astype(np.float32) / 255
    lum = 0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]
    cut = 0.72 if mode == "line" else 1.1
    alpha = a[..., 3] * np.clip((cut - lum) / 0.12, 0, 1)
    out = np.zeros_like(a)
    out[..., 0], out[..., 1], out[..., 2] = (c / 255 for c in rgb)
    out[..., 3] = alpha
    return Image.fromarray((out * 255).round().astype(np.uint8), "RGBA")


def main():
    entries = {}
    for glyph, (icon, mode) in GLYPHS.items():
        source = SPRITES / f"lk_icon_{icon}.png"
        for colour, rgb in COLOURS.items():
            name = f"lk_glyph_{colour}_{glyph}"
            image = build(source, mode, rgb)
            image.save(SPRITES / f"{name}.png")
            entries[name] = {"file": f"{name}.png", "w": image.width, "h": image.height, "slice": None}
    print(json.dumps(entries, indent=2))


if __name__ == "__main__":
    main()
