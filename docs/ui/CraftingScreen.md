# Crafting & Forge screen UI spec

Reference: `art/reference/ui/parchment/09_crafting.png`. Design resolution: the
window art's own 1629×742 px, cut from the sheet at (23, 58); every position below
is a reference-sheet pixel. Status: Built.

## Overview

One recipe window (`Hud/CraftingPanel`) in two modes:

| | Crafting (runs) | Forge (lobby) |
|---|---|---|
| Controller | `CraftingController` (Craft key, nav bar) | `ForgeController` (Forge tile) |
| Window art | `pm_window_crafting` (title baked) | `pm_window_forge` (title word erased; "ANCESTRAL FORGE" written) |
| Tabs | Weapons, Tools, Armor, Smelting, Food & potions, Siege & stations (`CraftingRules.CATEGORIES`) | Tools, Weapons, Armor, Supplies, Permanent (`ForgeRecipes.Categories`) |
| Counts | carried (`InventoryController.Count`) | vault (`ForgeSnapshot`) |
| Main button | CRAFT / SMELT / NEED <STATION>; stepper and Craft all for smelting | FORGE / CONVERT / LOCKED |
| Right column | SMELTING: the running job (name, done/count, bar, time left, ✕ stops) or an empty slot that opens Smelting; STATIONS NEARBY with ticks; a hint | FROM YOUR VAULT: the gear a Permanent conversion can use (the only one is chosen for you) and the rules; THE FORGE notes otherwise |

Pressing the chosen tab again shows every recipe. Rows show a count badge (how
many the inputs pay for; grey when the station is not in reach) and are drawn in
ink when craftable here. A Permanent conversion opens a confirmation over the
card naming the item, its quality roll and the cost; its CONVERT button arms after
1.5 s.

Item icons: a recipe shows `item_<catalogId>` once uploaded, until then its
category glyph.

## Element tree

| Element | Bounds (x, y, w, h) | Build |
|---|---|---|
| Close | 1538, 70, 100, 94 | transparent over the baked ✕ |
| Search | 82, 178, 393, 44 | `pm_search_box` + TextBox |
| Tabs | 82 + i·(393/n), 235, 393/n − 3, 60 | `pm_ctab` / `pm_ctab_selected` + glyph (`pm_glyph_sword/tools/armor/bag/heart/bench/diamond`) |
| Rows | 78, 305, 410, 462 (70 high, 77 pitch) | `pm_recipe_row` / `pm_recipe_row_selected` |
| Picture | 560, 230, 250, 360 | item icon, or the category glyph at 140 px, 35% faded |
| Name, chips | 827, 230, 334, 58 · 827/938/1057, 295 | 42 pt; `pm_stat_chip_tall` + `ItemInfo.Stats` |
| Requires | 827, 414 · cards 828, 447, up to 332 wide | `pm_req_card`; have green (#2E7D24) or red (#A3271B) / need |
| Stepper | 535 / 595 / 667, 670 | `pm_stepper_minus` / `_field` / `_plus` (smelting only) |
| Main button | 754, 655, 280, 92 (forge: 706) | `pm_button_craft` |
| Craft all | 1041, 672, 125, 60 | `pm_button_paper` |
| Job row | 1205, 230, 400, 94 | `pm_queue_row` (✕ baked); empty `pm_queue_empty` |
| Stations | 1222, 392 + 52·i | `pm_check_on` / `pm_check_off` |

## Verification

`capture.py crafting` (tools chosen with a smelt running; the Smelting tab);
`crafting_flow` (an instant craft sends no count, nothing without a furnace, the
stepper sets the batch, Craft all, ✕ stops); `forge_flow` (FORGE, a conversion asks
first and arms only after its delay, cancel, a locked recipe).

## Fix round 3

Shares the recipe window with the Forge (ForgeScreen.md, fix round 3): phone
row notes, wrapped long notes, gamepad selection kept on re-render, selectable
material rows. The ×20 open/close check in `crafting_flow` counts instances
and connections.
