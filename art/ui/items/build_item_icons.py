#!/usr/bin/env python3
"""Build every catalog item's own icon from the owner's item art.

Inputs : art/ui/items/ICONS.json (catalog id -> display name, family, source
         PNG, atlas group) and the PNGs it names in src/assets/Models/2D
         (512 x 512 RGBA, one item each, named after the display name).
Outputs: art/ui/sprites/lk_item_<CatalogId>.png      the slot icon, SLOT_PX square
         art/ui/sprites/lk_item_<CatalogId>__hi.png  its hero copy, HERO_PX square
         their entries in art/ui/sprites/manifest.json (the slot icon's `hi`
         names the hero copy; the copy's `scale` / `of` link it back), the
         slot icons packed into the ICONS.json atlas groups (pack_atlas.py),
         "" placeholders in src/shared/UI/UiAssetIds.json for the new atlases
         and hero images, and src/shared/UI/UiSprites.json synced.

    python3 art/ui/items/build_item_icons.py
    python3 art/ui/items/build_item_icons.py --contact <dir>   # also contact sheets

Every item gets the same treatment, so the icons read as one set:
  * the kit pipeline's alpha clean-up at the source's resolution
    (slice_lobby_kit.clean_alpha: the faint background-removal haze and specks
    dropped, only true pin-holes filled, interiors opaque, a re-ramped 1-2 px
    anti-aliased edge, rim pixels take the colour of the nearest solid pixel);
  * trimmed to the art, centred on a square whose long side holds the art with
    MARGIN_PX (at the slot size) of transparent margin all round;
  * that square resampled with premultiplied Lanczos to the slot size and,
    from the same source pixels, to the hero size, so the copy covers exactly
    the slot icon's design rectangle and only gets sharper; both are
    downscales (no sharpening) and keep the art's own colours;
  * alpha snapped (below 3 / 255 -> 0, above 0.96 -> 1) and colour bled into
    the transparent pixels, so bilinear filtering never pulls in black.

The slot icon (SLOT_PX: the biggest slot draws an item 67 design px, 94 px on
a 1440p screen) is packed into atlases; the hero copy (HERO_PX: the 254 px
Forge and Crafting picture at the 1440p window scale 1.4) is an image of its
own, fetched only where a hero box draws it (Widgets only draws a `__hi` copy
once its image has loaded), so phones never download a stack of big atlases.

Deterministic (two or three minutes): re-running writes identical files.
Never move an item to another atlas once that atlas is uploaded (pack_atlas.py
refuses): put new items in a new group in ICONS.json.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(ROOT / "scripts"))
import pack_atlas  # noqa: E402
import slice_lobby_kit as kit  # noqa: E402
import roblox_upload_ui_assets as uploader  # noqa: E402

MAPPING = HERE / "ICONS.json"
SOURCE = ROOT / "src" / "assets" / "Models" / "2D"
SPRITES = ROOT / "art" / "ui" / "sprites"
MANIFEST = SPRITES / "manifest.json"
IDS_FILE = ROOT / "src" / "shared" / "UI" / "UiAssetIds.json"

PREFIX = "lk_item_"
HERO_SUFFIX = "__hi"
# Slot icon: 9 a row in a 1024 atlas (4 px gaps), 81 an atlas.
SLOT_PX = 110
# Transparent margin round the art, in slot pixels (the hero copy scales it).
MARGIN_PX = 4
HERO_PX = kit.HERO_PX
# Background-removal pin-holes are a few pixels; real gaps (between berries,
# a workbench's legs) are bigger and stay open.
HOLE_MAX = 8


def load_mapping():
    data = json.loads(MAPPING.read_text(encoding="utf-8"))
    items = data["items"]
    pngs = {}
    for item_id, entry in items.items():
        for key in ("name", "family", "png", "atlas"):
            if not entry.get(key):
                raise ValueError(f"{item_id}: no {key} in {MAPPING.name}")
        if not entry["atlas"].startswith("atlas_"):
            raise ValueError(f"{item_id}: atlas {entry['atlas']!r} must start with atlas_")
        if entry["png"] in pngs:
            raise ValueError(f"{entry['png']} is mapped twice ({pngs[entry['png']]}, {item_id})")
        pngs[entry["png"]] = item_id
        if not (SOURCE / entry["png"]).is_file():
            raise ValueError(f"{item_id}: {entry['png']} is not in {SOURCE.relative_to(ROOT)}")
    unmapped = sorted(p.name for p in SOURCE.glob("*.png") if p.name not in pngs)
    return items, unmapped


def groups(items):
    """{atlas group: [slot sprite names]} from the mapping, names sorted."""
    out = {}
    for item_id, entry in sorted(items.items()):
        out.setdefault(entry["atlas"], []).append(PREFIX + item_id)
    return out


def build_icon(path):
    """(slot icon, hero copy) float RGBA arrays for one source PNG."""
    a = np.asarray(Image.open(path).convert("RGBA"), np.float32) / 255.0
    h, w = a.shape[:2]
    a = kit.clean_alpha(a, (0, 0, w, h), hole_max=HOLE_MAX)
    ys, xs = np.nonzero(a[..., 3] > 0)
    if len(xs) == 0:
        raise ValueError(f"{path.name} is empty")
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    # The square around the art: its long side fills SLOT_PX - 2 * MARGIN_PX.
    side = max(x1 - x0, y1 - y0) * SLOT_PX / (SLOT_PX - 2 * MARGIN_PX)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    pad = int(np.ceil(side)) + 8
    padded = np.pad(a, ((pad, pad), (pad, pad), (0, 0)))
    box = (pad + cx - side / 2, pad + cy - side / 2, pad + cx + side / 2, pad + cy + side / 2)
    # Colour bleeds 24 px into the transparent pixels at both sizes: the slot
    # icon's reach its atlas neighbours' gap, the hero copy (an image of its
    # own) only needs what bilinear filtering reads round its silhouette.
    slot = kit.finish_hires(kit.resize(padded, SLOT_PX, SLOT_PX, box), 1)
    hero = kit.finish_hires(kit.resize(padded, HERO_PX, HERO_PX, box), 1)
    return slot, hero


def write_manifest(made):
    """Rewrites the lk_item_ entries (kept in place, new ones appended in name
    order, stale ones dropped), then packs the atlases."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest = {n: (made[n] if n.startswith(PREFIX) else e) for n, e in manifest.items()
                if not n.startswith(PREFIX) or n in made}
    for name in sorted(made):
        if name not in manifest:
            manifest[name] = made[name]
    manifest = pack_atlas.build(manifest)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def write_placeholders(names, stale):
    """"" (not uploaded yet) for every new atlas and hero image; uploaded ids
    are never touched, and only placeholders of images no longer made go."""
    ids = uploader.load_json(IDS_FILE)
    for name in stale:
        if ids.get(name) == "":
            del ids[name]
    for name in names:
        ids.setdefault(name, "")
    uploader.write_json(IDS_FILE, ids)


def to_image(a):
    return Image.fromarray(kit.to_u8(a), "RGBA")


def contact(icons, heroes, out_dir):
    """Contact sheets: every slot icon at 1x on dark and light, and the hero
    copies of a few items at their full size."""
    out_dir.mkdir(parents=True, exist_ok=True)
    cols, cell, label = 12, SLOT_PX + 12, 14
    rows = (len(icons) + cols - 1) // cols
    for bg, suffix in (((0x20, 0x20, 0x20), "dark"), ((0xF0, 0xE6, 0xD2), "light")):
        sheet = Image.new("RGBA", (cols * cell, rows * (cell + label)), bg + (255,))
        draw = ImageDraw.Draw(sheet)
        ink = (230, 230, 230, 255) if suffix == "dark" else (40, 30, 20, 255)
        for index, (item_id, image) in enumerate(icons):
            x, y = (index % cols) * cell + 6, (index // cols) * (cell + label) + 6
            draw.rectangle((x - 1, y - 1, x + SLOT_PX, y + SLOT_PX), outline=(128, 128, 128, 255))
            sheet.alpha_composite(image, (x, y))
            draw.text((x, y + SLOT_PX + 2), item_id[:20], fill=ink, font=kit.font(10))
        sheet.save(out_dir / f"item_icons_{suffix}.png")
    sheet = Image.new("RGBA", (len(heroes) * (HERO_PX + 8) + 8, HERO_PX + 16), (0xF0, 0xE6, 0xD2, 255))
    for index, (_, image) in enumerate(heroes):
        sheet.alpha_composite(image, (8 + index * (HERO_PX + 8), 8))
    sheet.save(out_dir / "item_icons_hero.png")


HERO_SAMPLE = ("WoodenSpear", "IronChest", "Elderberry", "Workbench", "MithrilBow", "GuardianFang")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--contact", type=Path, help="also write contact sheets into this folder")
    args = parser.parse_args(argv)
    items, unmapped = load_mapping()
    for name in unmapped:
        print(f"warning: {name} in {SOURCE.relative_to(ROOT)} is mapped to no item")
    made, icons, heroes = {}, [], []
    for item_id, entry in sorted(items.items()):
        slot, hero = build_icon(SOURCE / entry["png"])
        name, copy = PREFIX + item_id, PREFIX + item_id + HERO_SUFFIX
        kit.save(slot, SPRITES / f"{name}.png")
        kit.save(hero, SPRITES / f"{copy}.png")
        made[name] = {"file": f"{name}.png", "w": SLOT_PX, "h": SLOT_PX, "slice": None, "hi": copy}
        made[copy] = {"file": f"{copy}.png", "w": HERO_PX, "h": HERO_PX, "slice": None,
                      "scale": round(HERO_PX / SLOT_PX, 4), "of": name}
        icons.append((item_id, to_image(slot)))
        if item_id in HERO_SAMPLE:
            heroes.append((item_id, to_image(hero)))
    stale = sorted(p.stem for p in SPRITES.glob(f"{PREFIX}*.png") if p.stem not in made)
    for name in stale:
        (SPRITES / f"{name}.png").unlink()
    # The atlas groups the slot icons go into: pack_atlas.py reads them from
    # ICONS.json too (pack_atlas.item_groups).
    atlases = groups(items)
    if atlases != pack_atlas.item_groups():
        raise ValueError("pack_atlas.item_groups() disagrees with ICONS.json")
    write_manifest(made)
    write_placeholders(sorted(atlases) + sorted(n for n in made if n.endswith(HERO_SUFFIX)), stale)
    uploader.sync_sprites()
    if args.contact:
        contact(icons, heroes, args.contact)
    print(f"{len(items)} items: {len(items)} slot icons ({SLOT_PX} px) in {len(atlases)} atlases "
          f"({', '.join(f'{g} {len(n)}' for g, n in sorted(atlases.items()))}), "
          f"{len(items)} hero images ({HERO_PX} px)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
