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
    # Lobby kit (lk_): everything the lobby HUD draws on join except item art, and
    # what the run HUD and every window share with it (slot, row, small-button and
    # dot states, badges, bars, stat frame, rings), so the lobby's first screen
    # needs this atlas and atlas_lk_items only (docs/ui/ARCHITECTURE.md §6).
    "atlas_lk_lobby": [
        "lk_badge_count", "lk_badge_count_wide", "lk_badge_number", "lk_bar_fill_blue", "lk_bar_fill_green",
        "lk_bar_fill_orange", "lk_bar_fill_red", "lk_bar_fill_yellow", "lk_bar_frame", "lk_bar_frame_plain",
        "lk_bar_frame_thin", "lk_bar_track", "lk_button_invite", "lk_button_paper_disabled",
        "lk_button_paper_hover", "lk_button_paper_normal", "lk_button_paper_pressed",
        "lk_button_paper_small_disabled", "lk_button_paper_small_hover", "lk_button_paper_small_normal",
        "lk_button_settings", "lk_button_square_small", "lk_currency_pill", "lk_dot_brown", "lk_dot_green",
        "lk_dot_red", "lk_dot_yellow", "lk_frame_hollow_circle", "lk_frame_round", "lk_glyph_check",
        "lk_glyph_cross", "lk_glyph_ink_hammer", "lk_icon_anvil", "lk_icon_backpack", "lk_icon_coin",
        "lk_icon_crown", "lk_icon_exclamation", "lk_icon_gem", "lk_icon_lock", "lk_icon_market",
        "lk_icon_party", "lk_icon_portal", "lk_icon_scroll", "lk_icon_trade", "lk_keycap", "lk_keycap_wide",
        "lk_panel", "lk_plaque_paper", "lk_player_card", "lk_portrait_frame", "lk_ring_full", "lk_ring_track",
        "lk_row_disabled", "lk_row_hover", "lk_row_normal", "lk_slot_disabled", "lk_slot_hover",
        "lk_slot_item_normal", "lk_slot_item_selected", "lk_slot_locked", "lk_slot_normal", "lk_slot_selected",
        "lk_statbar_frame", "lk_tile_blank", "lk_tile_frame", "lk_toast_frame", "lk_window_frame",
    ],
    # Each window's own parts and controls: frames, buttons and their states, tabs,
    # rows, dividers, fields, checkboxes, toggles, sliders, tooltips, dialog. The
    # planned atlas_lk_controls fits in here, and the planned atlas_lk_slots and
    # atlas_lk_hud_world fit in atlas_lk_lobby, so a window needs one atlas less.
    "atlas_lk_window": [
        "lk_button_close_disabled", "lk_button_close_hover", "lk_button_close_normal",
        "lk_button_close_pressed", "lk_button_flat_disabled", "lk_button_flat_leather", "lk_button_flat_paper",
        "lk_button_hud", "lk_button_leather_disabled", "lk_button_leather_hover", "lk_button_leather_normal",
        "lk_button_leather_pressed", "lk_button_square_leather", "lk_button_square_paper",
        "lk_button_stepper_minus", "lk_button_stepper_plus", "lk_checkbox_off", "lk_checkbox_on",
        "lk_clasp_left", "lk_clasp_right", "lk_dialog_frame", "lk_divider_diamond", "lk_divider_line",
        "lk_divider_ornament", "lk_divider_vertical", "lk_dropdown", "lk_dropdown_button", "lk_emblem_leaf",
        "lk_emblem_rune", "lk_panel_inset", "lk_pill_value", "lk_plaque_notched_disabled",
        "lk_plaque_notched_leather", "lk_plaque_notched_paper", "lk_plaque_small", "lk_row_bullet",
        "lk_scroll_thumb", "lk_scroll_track", "lk_search", "lk_slider_knob", "lk_slider_track",
        "lk_tab_arrow_leather", "lk_tab_arrow_paper", "lk_tab_category", "lk_tile_check_off",
        "lk_tile_check_on", "lk_toggle_off", "lk_toggle_on", "lk_tooltip", "lk_tooltip_tail",
    ],
    # Menu, section and status icons and the flat ink / white glyphs.
    "atlas_lk_icons": [
        "lk_glyph_arrow_down", "lk_glyph_arrow_left", "lk_glyph_arrow_right", "lk_glyph_arrow_up",
        "lk_glyph_check_white", "lk_glyph_checkmark", "lk_glyph_chevron_right", "lk_glyph_ink_anvil",
        "lk_glyph_ink_backpack", "lk_glyph_ink_book", "lk_glyph_ink_check", "lk_glyph_ink_chest",
        "lk_glyph_ink_compass", "lk_glyph_ink_compass_rose", "lk_glyph_ink_gamepad", "lk_glyph_ink_gears",
        "lk_glyph_ink_info", "lk_glyph_ink_magnifier", "lk_glyph_ink_map_pin", "lk_glyph_ink_monitor",
        "lk_glyph_ink_people", "lk_glyph_ink_refresh", "lk_glyph_ink_speaker", "lk_glyph_ink_trophy",
        "lk_glyph_invite", "lk_glyph_minus", "lk_glyph_play", "lk_glyph_plus", "lk_glyph_white_anvil",
        "lk_glyph_white_backpack", "lk_glyph_white_book", "lk_glyph_white_check", "lk_glyph_white_chest",
        "lk_glyph_white_compass", "lk_glyph_white_gamepad", "lk_glyph_white_gears", "lk_glyph_white_hammer",
        "lk_glyph_white_info", "lk_glyph_white_magnifier", "lk_glyph_white_map_pin", "lk_glyph_white_monitor",
        "lk_glyph_white_people", "lk_glyph_white_refresh", "lk_glyph_white_speaker", "lk_glyph_white_trophy",
        "lk_icon_anvil_hammer", "lk_icon_backpack_small", "lk_icon_backpack_white", "lk_icon_berry_bush",
        "lk_icon_check", "lk_icon_chest", "lk_icon_clock", "lk_icon_compass", "lk_icon_compass_arrow",
        "lk_icon_cross", "lk_icon_crown_gem", "lk_icon_exit", "lk_icon_flag", "lk_icon_gear", "lk_icon_gift",
        "lk_icon_hammer", "lk_icon_hourglass", "lk_icon_journal", "lk_icon_log", "lk_icon_magnifier",
        "lk_icon_mail", "lk_icon_map", "lk_icon_map_pin", "lk_icon_mountain", "lk_icon_paw", "lk_icon_ruin",
        "lk_icon_totem", "lk_icon_treasure", "lk_icon_tree", "lk_icon_trophy",
    ],
    # Item art (ItemInfo.ART_SPRITES): hotbar, inventory, forge, journal, rewards.
    "atlas_lk_items": [
        "lk_icon_berries", "lk_icon_bone", "lk_icon_build", "lk_icon_campfire", "lk_icon_crystals",
        "lk_icon_drumstick", "lk_icon_hatchet", "lk_icon_heart", "lk_icon_hide", "lk_icon_lightning",
        "lk_icon_logs", "lk_icon_magma_ore", "lk_icon_mushroom", "lk_icon_pickaxe", "lk_icon_plank",
        "lk_icon_plant_fiber", "lk_icon_rocks", "lk_icon_rope", "lk_icon_runestone", "lk_icon_spear",
        "lk_icon_star", "lk_icon_stone", "lk_icon_stone_axe", "lk_icon_stones", "lk_icon_torch", "lk_icon_tusk",
        "lk_icon_warning",
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
