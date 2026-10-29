# Inventory & Vault screen UI spec

Reference: `art/reference/ui/parchment/08_inventory_vault.png`. Icons from
`04_icons.png`. Design resolution: the window art's own 1494×786 px, cut from the
sheet at (148, 6); every position below is a reference-sheet pixel.
Status: Built. Source of truth for build: the reference sheet.

## Overview

One parchment window (`Hud/InventoryPanel`) serves both places:

| Place | Controller | Title | Left pane | Right pane | Middle | Actions |
|---|---|---|---|---|---|---|
| Lobby | `VaultController` (Inventory and Vault tiles, Backpack key) | INVENTORY & VAULT | lobby backpack (`VaultSnapshot`) | vault items, then materials; capacity bar = item slots | → STORE, ← TAKE, STORE ALL | TAKE, STORE; ×1 / ×10 / ×100 / All picker for a material |
| World | `InventoryController` (Backpack key, nav bar) | INVENTORY | the 50 backpack slots in place | HOTBAR (6, with keys) and ARMOUR (Head, Chest, Legs) | → to hotbar (or wear), ← to backpack, DROP | EQUIP / USE / PUT AWAY, WEAR, TAKE OFF |

Category tabs (All, Tools, Materials, Food; `ItemInfo.Category`) and the search
box filter both panes: the lobby hides what does not match, the world dims it in
place (slot positions matter there). The sort button cycles Saved / Name / Count
in the lobby and is hidden in the world. In the world, choosing a slot and then
another moves or swaps the item (an armour slot wears it).

A vault material deposit the vault cannot hold in full opens a confirmation card
over the detail strip ("N would be deleted. Deposit anyway?", GDD §53).

Item icons: a slot shows the sprite `item_<catalogId>` once uploaded
(`ItemSlot.IconFor`); until then it writes the item's name. Permanent items carry
a ★, uncommon and rarer items a rarity stripe, stacks a count badge.

## Tokens (additions)

| Token | Value | Used by |
|---|---|---|
| badge | #3A2418 | Count badges |
| selectGlow | #F7B32B | Chosen slot ring, picked amount |
| line2 | #B89366 | Middle column dashes and marks |

## Element tree

| Element | Bounds (x, y, w, h) | Sprite / build |
|---|---|---|
| Window art | 148, 6, 1494, 786 | `pm_window_inventory` (two tiles; panes, title plate and ✕ baked; title erased) |
| Title | 560, 30, 550, 58 | 40 pt cream |
| Category tabs | 48,114 · 44,250 · 44,380 · 44,510 (≈122×124) | `pm_side_tab_selected` / `pm_side_tab`, icons `pm_cat_all/tools/materials/food` |
| Left title, search, sort | 219,136 · 497,141,226,42 · 737,141,77,42 | 33 pt; `pm_search_box` + TextBox; `pm_sort_button` |
| Panes | 206,194,626,418 · 956,194,626,418 | scrolling sections of 93×96 slots, 6 to a row (pitch 100.6 × 105.5) |
| Slot | 93 × 96 | `pm_item_slot` (Hud/ItemSlot) |
| Right icon, title, capacity | 968,136,66,53 · 1047,136 · bar 1272,152,194,23 · 1478,143 | `pm_icon_chest`; gold fill |
| Arrows | 851,276,82,71 · 851,375,82,70 | `pm_arrow_right` / `pm_arrow_left` |
| Square button | 836, 516, 112, 89 | `pm_button_square` (STORE ALL / DROP) |
| Detail slot, name | 240,637,142,119 · 407,638,440,50 | ItemSlot; 32 pt |
| Stat chips | 408 / 526 / 640, 698, 104, 43 | `pm_stat_chip` + `pm_glyph_sword/hammer/weight`; `ItemInfo.Stats` |
| Amount picker | 766 + 74·i, 698, 68, 43 | `pm_stat_chip` with gold ring when picked |
| Actions | 1104,655,222,76 · 1348,655,222,76 | `pm_button_action` |
| Status | 408, 745, 680, 26 | 17 pt leather |

## Verification

`python3 art/ui/capture/capture.py inventory` renders the lobby layout (pinned
to the sheet's place), a chosen vault material with the picker, and the world
layout; `vault_flow` and `inventory_flow` drive both controllers (store, an
overflow that asks first, take, STORE ALL; move to the hotbar, swap, wear, take
off, drop).
