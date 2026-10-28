# Market, Progress, Trade & notice cards UI spec

Reference: `art/reference/ui/parchment/11_panel_layouts.png` (the generic window
frames and the small card). These screens have no sheet of their own, so they
share one parchment list window (`Hud/ListWindow`) and one notice card
(`Hud/NoticeCard`). Status: Built.

## List window

Design size 1180 × 720 px (the window's UIScale fits it to the screen, up to 1.4×).

| Element | Bounds (x, y, w, h) | Build |
|---|---|---|
| Frame | 0, 0, 1180, 720 | `pm_frame_window`: frame B of the sheet, its inner panels and mark repainted as paper; 9-sliced with corners deep enough to hold the rope bindings |
| Title plate | 340, 6, 500, 116 | `pm_button_leather`, cream 40 pt title |
| Close | 1054, 52, 64, 62 | `pm_button_x` (B on a gamepad: closes the question first, then the window) |
| Corner | 70, 58, 260, 48 | Coins / Gems (`pm_icon_coin`, `pm_icon_gem`) on the Market |
| Tab column | 44, 132, 304, 532 | `pm_inset`; tabs 280 × 80 every 88 px (`Parchment.Tab`) |
| Page | 362, 132, 774, 532 (no tabs: 44, 132, 1092, 532) | `pm_inset` holding a scrolling list |
| Status | 70, 668, 1040, 34 | ink-soft line |
| Confirm | over the page | `pm_inset` card, `pm_button_claim` (armed after a delay where the action cannot be undone) and Cancel |

Page items: **Section** (diamond, capitals, rule), **Line** (wrapping text, tones
ink / soft / good / warn / gold), **Row** (84 px rounded paper card `pm_stat_chip_tall`:
item icon `item_<catalogId>` or a category glyph, title, wrapping detail, a value
with a coin or gem, up to four 150 × 54 buttons `pm_button_claim` / `pm_button_paper`,
or the green check `pm_check_green` when done), **Buttons** (a right-aligned row),
**Input** (label and `pm_search_box` field), **Pair** (two cards side by side).

| Screen | Controller | Tabs | Contents |
|---|---|---|---|
| Market (lobby) | `WalletController` | Shop, Sell, Offers, Codes | stock by category with price and BUY; backpack and vault sales (SELL, SELL 10, SELL ALL — never for a Forge reagent); vault upgrade, perk respec (asks first) and Robux offers with their earnable route; code box. Quests moved to the Journal. |
| Progress | `ProgressionController` | Overview, Perks, Rebirth, Titles | level and masteries; perk ranks with BUY; rebirth requirements and REVIEW REBIRTH (Reset / Kept / Gained, armed after 1.5 s); titles. Perks and Rebirth are lobby-only. |
| Trade (lobby) | `TradeController` | — | players to invite; during a trade YOU GIVE / YOU GET with lock state, countdown, CANCEL / LOCK OFFER / CONFIRM, a Gems box, backpack items (ADD / REMOVE) and tradeable vault materials (+1, +10, ALL, REMOVE). |

## Notice card

`pm_card` 9-sliced at half corner size, 420–480 px wide, growing with its text:
title (22 pt ink), text (18 pt ink-soft), optional buttons. Used by the server
notice (`NoticeController`, its own gui 90 px from the top), the trade invite
(ACCEPT / DECLINE), the run toast (`InventoryController`) and the extraction
receipt (`VaultController`), the last three in the shared top-centre column.

## Verification

`capture.py market_flow` (buy, sell 10, no sell-all for a reagent, respec asks,
code; Shop/Sell/Offers pictures), `progress_flow` (masteries, perk buy, rebirth
armed only after its delay), `trade_flow` (invite, add item, +10 material, gems,
lock), `notices`.

## World map

`MapController` (run, Map key / DPadDown / nav bar): a 900 × 880 window. The
painted island (`Hud/IslandMap`, as in the Journal) fills the opening of
`pm_frame_hollow` (frame C of the panel layouts sheet, its mark covered by the
band beside it), with the compass rose, a leather MAP plate, close and zoom
buttons. Pins mark the safe camps and main landmarks (press for the name plate);
diamonds mark active portals and announced events (`IslandMap:SetMarkers`);
the cream dot is you, followed while zoomed in until you pan. An authored map
shows plain parchment with its camps, portals and events. The safe-camp notice
is a notice card above the hotbar. Capture: `map_flow`.
