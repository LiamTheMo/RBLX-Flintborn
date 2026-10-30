"""Pack the UI's sprites into a few atlas images.

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

Art too big for one image (the screens' window frames) is packed as its
tiles, each at full resolution.

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
    # The kit every window shares (ListWindow, Parchment controls, notice cards):
    # the Market, Progress and Trade windows need only this.
    "atlas_ui": [
        "pm_frame_window", "pm_inset", "pm_button_leather", "pm_button_claim", "pm_tab_leather",
        "pm_tab_paper", "pm_card", "pm_button_x", "pm_button_check", "pm_icon_coin", "pm_icon_gem",
        "pm_stat_chip_tall", "pm_check_green", "pm_check_on", "pm_check_off", "pm_slider_knob",
        "pm_stepper_field", "pm_stepper_minus", "pm_stepper_plus", "pm_dropdown", "pm_keycap",
        "pm_item_slot", "pm_glyph_armor", "pm_glyph_bag", "pm_glyph_bench", "pm_glyph_diamond",
        "pm_glyph_gamepad", "pm_glyph_gear", "pm_glyph_hammer", "pm_glyph_heart", "pm_glyph_monitor",
        "pm_glyph_mountain", "pm_glyph_person", "pm_glyph_sound", "pm_glyph_sword", "pm_glyph_tent",
        "pm_glyph_tools", "pm_glyph_weight",
    ],
    # The pieces of the Crafting, Forge, Inventory, Journal and Settings screens
    # and the lobby's popups.
    "atlas_pieces": [
        "pm_panel", "pm_button_parchment", "pm_recipe_row", "pm_recipe_row_selected", "pm_queue_row",
        "pm_queue_empty", "pm_req_card", "pm_search_box", "pm_ctab", "pm_ctab_selected",
        "pm_button_craft", "pm_side_tab", "pm_side_tab_selected", "pm_sort_button", "pm_cat_all",
        "pm_cat_food", "pm_cat_materials", "pm_cat_tools", "pm_button_action", "pm_button_square",
        "pm_arrow_left", "pm_arrow_right", "pm_icon_chest", "pm_quest_row", "pm_quest_row_selected",
        "pm_jtab_leather", "pm_jtab_paper", "pm_button_strip", "pm_icon_bolt", "pm_icon_scroll",
        "pm_button_apply", "pm_button_reset",
    ],
    # The world map's frame, the map pieces the Journal shares, and the run's
    # interaction prompt frame.
    "atlas_map": [
        "pm_frame_hollow", "pm_compass_rose", "pm_map_pin", "pm_map_label", "pm_button_zoom_in",
        "pm_button_zoom_out", "frame_bar_hollow",
    ],
    # The island map painting (Journal and world map).
    "atlas_island": ["pm_map_island"],
    # Each screen's window frame is two tiles (too wide for one image), each in
    # an atlas of its own at full resolution.
    **{
        f"atlas_window_{screen}_{half}": [f"pm_window_{screen}__1_{half}"]
        for screen in ("crafting", "forge", "inventory", "journal", "settings")
        for half in (1, 2)
    },
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


def pack_tight(sizes):
    """Guillotine packing, largest first, best short-side fit: tighter than
    shelves for a few big pieces among many small ones."""
    free = [(0, 0, SIDE, SIDE)]
    placed = {}
    bottom = 0
    for name in sorted(sizes, key=lambda n: (-max(sizes[n]), -sizes[n][0] * sizes[n][1], n)):
        w, h = sizes[name][0] + GAP, sizes[name][1] + GAP
        best = None
        for index, (fx, fy, fw, fh) in enumerate(free):
            if w <= fw and h <= fh:
                key = (min(fw - w, fh - h), fy, fx)
                if best is None or key < best[0]:
                    best = (key, index)
        if best is None:
            raise ValueError(f"atlas overflow at {name}")
        fx, fy, fw, fh = free.pop(best[1])
        placed[name] = (fx, fy)
        bottom = max(bottom, fy + sizes[name][1])
        if fw - w < fh - h:
            free += [(fx + w, fy, fw - w, h), (fx, fy + h, fw, fh - h)]
        else:
            free += [(fx + w, fy, fw - w, fh), (fx, fy + h, w, fh - h)]
        free = [r for r in free if r[2] > 0 and r[3] > 0]
    return placed, bottom


def build(manifest):
    for entry in manifest.values():
        entry.pop("atlas", None)
        entry.pop("rect", None)
    for group, names in GROUPS.items():
        images = {name: Image.open(SPRITES / manifest[name]["file"]).convert("RGBA") for name in names}
        sizes = {name: image.size for name, image in images.items()}
        try:
            placed, height = pack(sizes)
        except ValueError:
            placed, height = pack_tight(sizes)
        # Power-of-two height keeps the texture compact on the GPU.
        side = 1 << max(0, (height - 1).bit_length())
        canvas = Image.new("RGBA", (SIDE, min(SIDE, side)), (0, 0, 0, 0))
        for name, (x, y) in placed.items():
            canvas.alpha_composite(images[name], (x, y))
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
