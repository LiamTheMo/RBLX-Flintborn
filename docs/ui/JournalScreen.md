# Journal screen UI spec

Reference: `art/reference/ui/parchment/07_journal.png` (window, list, quest card,
map and the component strip under it). Icons from `04_icons.png`.
Design resolution: the window art's own 1632×772 px, cut from the sheet at
(20, 18); every position below is a reference-sheet pixel.
Status: Built. Source of truth for build: the reference sheet.

## Overview

The modal Journal (GDD §10.1, §25), opened by the lobby's Quests tile. The quest
list on the left (All / Daily / Main tabs), the chosen quest's card in the middle
and the painted island map on the right. Quests come from `QuestView` (refreshed
every 5 s while open); CLAIM calls `QuestClaim` for a finished quest.

The map is `art/ui/map/island.png`, painted by `art/ui/map/render_island.py`
from the game's own terrain functions (BiomeCatalog zones, IslandLayout heights,
water, rivers and pools): it covers 4,400 studs centred on the island, north up.
Rerun the script when the island layout changes, then the slicer.

## Tokens (additions; see SettingsScreen.md and LobbyScreen.md)

| Token | Value | Used by |
|---|---|---|
| listPaper / listEdge | #EBCB9A / #C59462 | Quest list backing |
| slotEdge | #D4A069 | Reward slots |
| questReady | #FFC029 | Status dot: finished, claim waiting |
| questOpen | #A28969 | Status dot: under way |
| questDone | #43C33F | Status dot: claimed; finished progress bar |

## Element tree

| Element | Bounds (x, y, w, h) | Sprite / build |
|---|---|---|
| Window art | 20, 18, 1632, 772 | `pm_window_journal` (two tiles; title plate, ✕, card and map frames baked) |
| Close (touch area) | 1560, 50, 90, 84 | transparent button |
| Tabs All / Daily / Main | 63,144,122,54 · 189,146,125,52 · 316,146,125,52 | `pm_jtab_leather` (selected) / `pm_jtab_paper`, 25 pt label |
| List | 66, 200, 372, 468 | native backing; scrolling rows of 360×86 every 92.5 px |
| Row | — | `pm_quest_row` / `pm_quest_row_selected` (scroll icon and chevron baked), name 21 pt at x 96, status dot 26 px at x 293 |
| Active strip | 76, 675, 354, 76 | `pm_button_strip`, "N Active Quests" cream; press jumps to a claimable quest |
| Card icon | 480, 152, 118, 106 | `pm_icon_scroll` |
| Title | 606, 160, 312, 76 | 42 pt, shrinks and wraps |
| Dividers | 476, 241 / 521, 446, 28 | native lines + `pm_glyph_mountain` |
| Objective | box 484,287 · text 534,284 · bar 535,321,305,21 · count 850,312 | `pm_check_off` / `pm_check_green`; gold fill, green when done |
| Notes / message | 486, 372, 430, 140 · 486, 478, 430, 32 | tier and reset; a claim's outcome |
| Rewards | slots 493 + 107·i, 588, 95, 88 | native slot, `pm_icon_coin` / `pm_icon_gem` / `pm_icon_bolt`, amount 23 pt |
| CLAIM | 506, 682, 388, 78 | `pm_button_claim`, 40 pt cream; "CLAIMED" once paid; dimmed unless finished |
| Map | 974, 141, 638, 611 | `pm_map_island` in a clipping frame (zoom 1–3.4×), `pm_map_pin` per place, `pm_map_label` name plate |
| Zoom + / − | 1546,540,62,62 · 1546,606,62,63 | `pm_button_zoom_in` / `_out` |
| Compass | 1500, 146, 93, 117 | `pm_compass_rose` tinted ink |

Pins: the two safe camps and six landmarks (Shattered Keep, Frostpeak Summit,
Fallen Temple, Emberhollow Mouth, Timberwatch Tower, Old Lighthouse). Pressing a
pin shows its name plate; a Guardian or boss quest shows the Keep's.

## States

| Control | Rest | Hover / focus | Pressed | Disabled |
|---|---|---|---|---|
| Row | paper row | ×0.93 | ×0.80 | — |
| Row (selected) | gold-edged row | — | — | — |
| Tab | paper | ×0.93 | ×0.80 | — |
| Tab (selected) | leather, cream text | — | — | — |
| CLAIM | leather | ×0.93 | ×0.80 | ×0.72 (not finished, claimed, or a claim on its way) |

## Verification

`python3 art/ui/capture/capture.py journal` renders the All tab (pinned to the
sheet's place), the Daily tab with a finished quest, and the Main tab;
`journal_flow` drives the controller (open, a refused claim, a claim, tabs,
close). In-Studio and device checks are in `docs/MANUAL_VALIDATION.md`.
