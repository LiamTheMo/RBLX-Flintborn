"""Pack the lobby's and the in-world HUD's sprites into a few atlas images.

Phones refuse bursts of separate image downloads: in each session only the
first handful of HUD sprites loaded. Each atlas is one image (at most
1024 x 1024, Roblox's largest), so a screen needs one or two downloads instead
of dozens; Widgets.Sprite shows a sprite as its rectangle of the atlas
(ImageRectOffset / ImageRectSize, with the 9-slice centre relative to it).

Reads art/ui/sprites/<name>.png and manifest.json; writes art/ui/sprites/
atlas_<group>.png and, for every packed sprite, "atlas" and "rect" [x, y, w, h]
in manifest.json (sync to UiSprites.json with
`python3 scripts/roblox_upload_ui_assets.py --sprites`). Sprites keep their own
files and ids as the fallback while an atlas is not uploaded.

    python3 art/ui/pack_atlas.py

slice_parchment.py runs this after slicing, since it rewrites the manifest.
"""
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SPRITES = HERE / "sprites"
MANIFEST = SPRITES / "manifest.json"
SIDE = 1024
# Space between sprites; their edges are already bled into transparent pixels,
# so filtering at a rectangle's border never reaches a neighbour.
GAP = 4

GROUPS = {
    # What the lobby shows on joining (the popups' panel opens later).
    "atlas_lobby": [
        "pm_lobby_profile", "pm_lobby_enter", "pm_lobby_party", "pm_lobby_server",
        "pm_lobby_coins", "pm_lobby_gems", "pm_lobby_gear", "pm_fill_xp", "pm_icon_crown",
        "pm_button_add_friend", "pm_tile_inventory", "pm_tile_vault", "pm_tile_quests",
        "pm_tile_shop", "pm_tile_forge", "pm_tile_trade",
    ],
    # What the in-world HUD shows during a run.
    "atlas_hud": [
        "pm_hud_compass", "pm_hud_health", "pm_hud_stamina", "pm_hud_food", "pm_hud_xp",
        "pm_hud_slot", "pm_hud_slot_selected", "pm_hud_card", "pm_stat_chip", "pm_button_paper",
        "compass_marker", "icon_run", "icon_storm", "icon_mountain", "icon_tower", "icon_waypoint",
    ],
}


def pack(sizes):
    """Shelf packing, tallest first: {name: (x, y)} or raises when it overflows."""
    order = sorted(sizes, key=lambda n: (-sizes[n][1], -sizes[n][0], n))
    placed = {}
    x = y = shelf = 0
    for name in order:
        w, h = sizes[name]
        if x + w > SIDE:
            x, y = 0, y + shelf + GAP
            shelf = 0
        if y + h > SIDE:
            raise ValueError(f"atlas overflow at {name}")
        placed[name] = (x, y)
        x += w + GAP
        shelf = max(shelf, h)
    return placed, y + shelf


def build(manifest):
    for entry in manifest.values():
        entry.pop("atlas", None)
        entry.pop("rect", None)
    for group, names in GROUPS.items():
        sizes = {}
        for name in names:
            entry = manifest[name]
            sizes[name] = (entry["w"], entry["h"])
        placed, height = pack(sizes)
        # Power-of-two height keeps the texture compact on the GPU.
        side = 1 << max(0, (height - 1).bit_length())
        canvas = Image.new("RGBA", (SIDE, min(SIDE, side)), (0, 0, 0, 0))
        for name, (x, y) in placed.items():
            canvas.alpha_composite(Image.open(SPRITES / manifest[name]["file"]).convert("RGBA"), (x, y))
            w, h = sizes[name]
            manifest[name]["atlas"] = group
            manifest[name]["rect"] = [x, y, w, h]
        canvas.save(SPRITES / f"{group}.png", optimize=True)
        manifest[group] = {"file": f"{group}.png", "w": canvas.width, "h": canvas.height, "slice": None}
        print(f"{group}: {len(placed)} sprites, {canvas.width}x{canvas.height}")
    return manifest


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    MANIFEST.write_text(json.dumps(build(manifest), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
