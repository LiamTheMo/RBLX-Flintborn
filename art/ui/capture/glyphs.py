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

Glyphs in HERO (the stand-in Kit.ItemIcon draws for armour without art) also
get a hero copy, `<name>__hi`: the source icon resampled from its kit sheet at
the size the Forge picture draws the glyph at 1440p (slice_lobby_kit.py HERO_PX
x 0.62), then recoloured the same way. Its manifest entries (the glyph's `hi`
and the copy's own) are written here; run art/ui/pack_atlas.py afterwards.
"""
import json
from pathlib import Path

import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SPRITES = ROOT / "art" / "ui" / "sprites"
MANIFEST = SPRITES / "manifest.json"
sys.path.insert(0, str(ROOT / "art" / "ui"))
import slice_lobby_kit as kit  # noqa: E402
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


# Glyphs drawn in the hero boxes: Kit.ItemIcon's kind glyph is 0.62 of its box.
HERO = {"lk_glyph_ink_backpack"}
HERO_GLYPH_PX = int(np.ceil(int(kit.HERO_BOX * 0.62) * kit.HERO_UI))


def build(source, mode: str, rgb):
    """The glyph of icon `source` (a PNG path, or a float RGBA array)."""
    if isinstance(source, Path):
        a = np.asarray(Image.open(source).convert("RGBA")).astype(np.float32) / 255
    else:
        a = np.asarray(Image.fromarray(kit.to_u8(source), "RGBA")).astype(np.float32) / 255
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
            if name in HERO:
                hero(name, icon, mode, rgb)
    print(json.dumps(entries, indent=2))


def hero(name: str, icon: str, mode: str, rgb):
    """Writes glyph `name`'s hero copy from icon `icon`'s kit-sheet crop and
    links it in the manifest."""
    part = next(p for p in kit.PARTS if p["name"] == f"lk_icon_{icon}")
    ctx = {}
    base, _ = kit.build_part(part, ctx)
    source, (ow, oh) = ctx["source"], ctx["size"]
    f = HERO_GLYPH_PX / max(base.shape[:2])
    up = f / min(source.shape[1] / ow, source.shape[0] / oh)
    copy, f, _ = kit.build_copy(part, base, ctx, f, sharpen=up if up > 1 else None)
    image = build(copy, mode, rgb)
    copy_name = name + kit.HI_SUFFIX
    image.save(SPRITES / f"{copy_name}.png")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest[name]["hi"] = copy_name
    entry = {"file": f"{copy_name}.png", "w": image.width, "h": image.height, "slice": None,
             "scale": round(f, 4), "of": name}
    prev = manifest.get(copy_name, {})
    if prev.get("atlas") and (prev.get("w"), prev.get("h")) == (image.width, image.height):
        entry["atlas"], entry["rect"] = prev["atlas"], prev["rect"]
    manifest[copy_name] = entry
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"{copy_name}: {image.width}x{image.height} x{f:.3f}")


if __name__ == "__main__":
    main()
