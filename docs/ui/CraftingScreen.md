# Field Crafting screen UI spec

Field crafting in a run is the Ancestral Forge's recipe window in its
`"crafting"` mode: one layout, `Hud/Screens/RecipeWindow`, built only from the
Kit and measured from `art/reference/ui/lobby/06_forge.png`. The layout, the
element tree and the deviations shared with the Forge are in
[ForgeScreen.md](ForgeScreen.md); this page lists what crafting mode changes.
Design px are the 1102 × 680 window's. Status: Built.

## The two modes

| | Field Crafting (runs) | Ancestral Forge (lobby) |
|---|---|---|
| Controller | `CraftingController` (Craft key, HUD Craft tile) | `ForgeController` (Forge tile) |
| Header | build icon, "Field Crafting" in small caps, hand subtitle "Make tools and supplies from what you carry." | anvil, "Ancestral Forge", its subtitle |
| Categories (the RECIPES dropdown) | All, Weapons, Tools, Armor, Smelting, Food & potions, Siege & stations (`CraftingRules.CATEGORIES`) | All, Tools, Weapons, Armor, Supplies, Permanent (`ForgeRecipes.Categories`) |
| Counts | what you carry (`InventoryController.Count`) | the vault (`ForgeSnapshot`) |
| Row note | the station ("Workbench", "By hand"), plus the first stat in short form ("Workbench · Harvest 4 per hit"), or the smelt time ("Furnace · 2 s each") | the first stat, or the unlock line of a locked recipe |
| QUANTITY | smelting only, with **All** (as many as the ore allows); other recipes make one per request (`CraftingRules.BatchCount`) | special recipes, up to the snapshot's `maxCount` |
| Main button | CRAFT / SMELT, or NEED <STATION> (disabled) away from the station | FORGE / CONVERT / LOCKED |
| Right column | YOUR MATERIALS (shorter list), SMELTING (the running job's line, its bar and **Stop**), STATIONS NEARBY | YOUR MATERIALS |

## Crafting mode layout (window design px)

| Element | Rect | Notes |
|---|---|---|
| Stepper (with All) | 483, 610, 222 × 44 | shown for smelting only |
| Main button | 713, 599, 220 × 66 | narrower than the Forge's to leave the stepper its All |
| YOUR MATERIALS list | 763, 164, 312 × 262 | |
| SMELTING header | 782, 446, 276 × 26 | `sectionHeader` 18 |
| Job line | 782, 472, 276 × 24 | `RecipeModel.JobText`: "Copper Bar 2 / 5 · 7 s left", or "Nothing smelting" |
| Job bar | 782, 502, 190 × 20 (phones 156 × 20) | orange fill on the track |
| Stop | 984, 492, 74 × 40 (phones 950, 490, 108 × 44) | secondary, small; enabled while a smelt runs. Phones and touch tablets widen it (the bar gives way) so the boosted "Stop" fits its plate |
| STATIONS NEARBY header | 782, 538, 276 × 26 | |
| Stations line | 782, 564, 276 × 24 | "Workbench, Furnace" |

A locked recipe's picture is dimmed with `Kit.Dim`, which keeps an item
without art at its faded stand-in glyph (STYLE_GUIDE §6.5).

## Data and behaviour

- The window rechecks which stations are in reach and ticks the running
  smelt's time left every `CraftingController.WATCH_SECONDS` while it is open.
- The running smelt comes from the server's `Smelt*` player attributes
  (`SmeltRecipe`, `SmeltCount`, `SmeltDone`, `SmeltSeconds`, `SmeltEndsAt`).
- Refusals read as words: the controller's own lines for crafting codes, else
  `Reasons.Text` (every server code has a line; unknown ones read "That didn't
  work.").

## Verification

`capture.py crafting` (Smelting with Copper Bar chosen, QUANTITY with All, a
smelt running and Stop live; Tools away from a workbench: NEED WORKBENCH,
disabled); `crafting_flow` (an instant craft sends no count, nothing without a
furnace, the stepper sets the batch, All, Stop, and a ×20 open / close check
counting instances and connections).
