# Inventory screen UI spec

Reference: `art/reference/ui/lobby/02_inventory.png` (Backpack tab). Kit:
`art/reference/ui/lobby/kit/` (index in `art/reference/ui/lobby/README.md`).
Design resolution: 1672 × 941 (the image size). Every bound below is design px
from the top-left of the screen, measured from the image (±1–2 px); "rel" is
relative to the window's top-left (243, 150).
Status: Draft (measured spec for the lobby UI rebuild). Source of truth for build:
the reference image. The old parchment inventory spec this file replaces
described `08_inventory_vault.png`, which has been removed.

## Overview

A modal window over the lobby. It opens from the Backpack tile of the HUD menu
grid (and the Backpack key), shows the player's **Backpack** (lobby backpack) or
**Vault** (two tabs), filters by search text and category, and shows the chosen
item in a detail card with an EQUIP action. A dark overlay covers the whole
screen, including the HUD, while it is open. The close button (top right) closes
it. The HUD drawn under the overlay in the mockup is not a layout source: its
hotbar and XP bar sit about 42 px lower and its party panel is moved compared
with `01_hud.png`; keep the HUD as built from `01_hud.png` and only dim it.

There is no Vault mockup. The Vault tab uses the same layout; see
[Vault tab (assumptions)](#vault-tab-assumptions).

## Tokens

Colours are medians of flat areas (`col.py`) or glyph cores (`ink2.py`, pixels
70 % of the way from the background to the darkest/lightest value).

| Token | Value | Used by |
|---|---|---|
| Overlay | #0E0C08 at ~68 % opacity (BackgroundTransparency ≈ 0.32); see [Dim overlay](#dim-overlay) | Full-screen dim |
| Parchment | #FDDBB0 (window body), #FDD9AE (grid area), #FDD5A6 (detail card) | Window, slots, card |
| Parchment.Raised | #FEE5C3 | Inactive tab (Vault) fill |
| Parchment.Active | #F3B67A (body), outline #7E6040–#916032 | Active category arrow tab (All) |
| Leather | #A83D0D–#AB4012 (tab), #A0380D (EQUIP), #AF4410→#8B340C (close, lit top → shaded bottom) | Active tab, EQUIP, close |
| Ink.Title | #2C1204 (core) | INVENTORY |
| Ink.Strong | #1B0F08 (labels), #1A0802 (All), #2A1105 (item name), #26190D (stat values), #0A0402 (counts) | Labels, values |
| Ink.Label | #2D1C0E | Stat labels |
| Ink.Muted | #715334 | Item description |
| Ink.Placeholder | #A37F5C (text), #7C5637 (magnifier) | Search box |
| Ink.OnLeather | #FAF3EC (tab label), #FBF6F0 (EQUIP), #F7EEE0 (close ✕) | Text on leather |
| Glyph.Brown | #48230E–#593017 (cores) | Category and stat icons |
| Rule.Soft | #E9C092, 2 px | Category row rules |
| Rule.Card | #F2C697, 2 px (lum ≈ 170–190) | Detail card rules |
| Rule.Divider | #F0C294, 2 px | Grid / card divider |
| Rule.Title | #533820, 2 px, tapering at both ends | Title underline |
| Stroke.Slot | 1–2 px #1B0700–#2C0E00 with 1 px light rim #FFEBC1 outside and inside | Item slot |
| Glow.Selected | 7–8 px ring: outer #D76100, core #FFFFCE/#FCC646, inner #AC4D06 | Selected slot |
| Stroke.Search | 1–2 px #B88654 | Search box |
| Font.Serif | Merriweather (see [Typography](#typography)) | All text |

## Typography

Font family: **Merriweather** (the repo's `serif`, `HudLayout.json`
`fontFaces.serif` = Merriweather Bold). Confirmed as the closest family by
letter shape (R leg, Y, S, a, g, numerals) in 3× side-by-side crops
(`art/ui/kit/analysis/inventory/font_sbs1.png`) and by width: at matched cap
height, Merriweather Bold sets "Stone Axe" at 131 px (mock 131) and "INVENTORY"
at 264 px (mock 276). Differences:

- Titles (INVENTORY) are heavier than Merriweather Bold: thicker stems, darker
  colour (ink coverage 0.42 vs 0.44 at a size that is 4 % narrower). Options:
  (a) Merriweather **Black** (900) if the Studio family lists it; (b) Bold with a
  1 px UIStroke in the ink colour; (c) Bold as is.
- Row labels (category names, stat labels, search placeholder) and the
  description read as a lighter weight than Bold; Merriweather **Regular**
  matches their stroke weight better (IoU 0.52 vs 0.47 on "Harvest Power").
- The mockup's lowercase is smaller relative to caps (x-height / cap height ≈
  0.69–0.70) than Merriweather (0.76), so at the same cap height Merriweather
  lowercase is ~10 % taller. Accept (no closer Roblox serif).

TextSize = cap height ÷ 0.74 (Merriweather cap height is 0.74 em, measured from
`art/ui/fonts/Merriweather-Bold.woff`; same rule as `LobbyScreen.md`). Confirm
with a capture.

| Text | Weight (proposed) | Cap height (px) | TextSize | Colour | Align |
|---|---|---|---|---|---|
| INVENTORY | Black (or Bold, see above) | 31 ('I' 186–216) | 42 | Ink.Title | left |
| Backpack / Vault (tabs) | Bold | 15 (279–293) | 20 | #FAF3EC on leather / #1C1207 on parchment | left |
| Search placeholder "Search items..." | Regular | 12 (343–354) | 16 | #A37F5C | left |
| Category labels | Bold (active) / Bold or Regular (rest) — mock looks the same weight on all rows | 14–15 | 20 | #1A0802 / #1B0F08 | left |
| Slot count | Bold | 15 (406–420) | 20 | #0A0402 | right, bottom |
| Item name "Stone Axe" | Bold | 20 ('S' 481–501 incl. overshoot) | 27 | #2A1105 | left |
| Description | Regular | 12 ('A' 517–528) | 16 | #715334 | left, wrapped, line pitch 22 px |
| Stat label | Regular | 13 (587–599) | 18 | #2D1C0E | left |
| Stat value | Bold | 13 (587–599) | 18 | #26190D | right |
| EQUIP | Bold | 16 ('E' 730–745) | 22 | #FBF6F0 | centre |

No text stroke or shadow is visible on any text (glyph edges go straight from
ink to background in `px.py` scans).

## Element tree

Z-order: Overlay < Window frame < content (rules, slots, cards) < icons/text <
selected-slot glow (drawn over the slot outline). Anchor intent: the window is
centred horizontally (centre x 836 = screen centre) with its top at y 150
(centre y 475.5, 5 px below screen centre); use AnchorPoint (0.5, 0.5) at
(0.5, 0.5) + (0, 5) under the screen's UIScale, or top-centre at y 150 — both
give the same layout at the design resolution. Everything inside is offset from
the window's top-left.

| Element | Parent | Bounds x, y, w, h (screen) | rel (window) | Appearance | Content | Kit part / build |
|---|---|---|---|---|---|---|
| Overlay | ScreenGui | 0, 0, 1672, 941 | — | Overlay token; covers the HUD | — | native Frame |
| Window | Overlay | 243, 150, 1187, 652 | 0, 0 | parchment body, 4–5 px dark outline (#140000 core, leather-brown mid), inner orange rule ~10 px in (x 253 / 1418, y 159 / 789–790); leather corner brackets with rivets at all four corners (TL bracket ≈ 243–275 × 149–167, protrudes ≤ 3 px above); two side clasps on the right edge at ≈ 1411, 256, 21, 20 and 1415, 732, 17, 18 | — | **Kit 10** inventory window (40, 48, 706 × 782: same brackets and right-side clasp; title, icon, close, tabs, search and slots are baked in and must be erased) or **kit 04** frame 1 (48, 43, 1082 × 426: right-side clasps at ≈ y 150 and 385). 9-slice either; corners ≈ 45 px |
| HeaderIcon | Window | 283, 165, 71, 77 | 40, 15 | full-colour backpack | — | kit 10 window header backpack (≈ 85, 90) or kit 06 backpack (47, 41, 339 × 341) / kit 11 backpack (45, 63, 219 × 233), scaled |
| Title | Window | ink 383, 186, 276, 31 (incl. O overshoot 185–217) | 140, 36 | Font per Typography | "INVENTORY" | native TextLabel; suggest frame 383, 172, 320, 56, TextYAlignment Center |
| TitleRule | Window | 370, 235, 948, 2 (fades out ≈ 1310–1318) | 127, 85 | Rule.Title | — | native Frame + UIGradient transparency at the ends (kit 14 dividers have diamond ends, which the mockup lacks) |
| CloseButton | Window | 1346, 168, 60, 57 | 1103, 18 | leather square, ✕ #F7EEE0, 4 rivets | — | **kit 03** close button normal (342, 329, 140 × 135); hover 537, pressed 734, disabled 933 (same row) |
| Tab.Backpack (active) | Window | 262, 258, 170, 58 | 19, 108 | leather #AB4012, dark outline, rivets | icon 277, 266, ≈34 × 40 (cream line backpack); label ink 328, 279, 82, 15 | **kit 10** Backpack tab (1209, 55, 302 × 89; also baked at 73, 210 in the kit window); generic: kit 03 wide leather (44, 63) |
| Tab.Vault (inactive) | Window | 441, 259, 165, 56 | 198, 109 | parchment #FEE5C3, dark outline, rivets | chest icon 448, 269, 56, 36; label ink 521, 279, 46, 15 | **kit 10** Vault tab (1210, 154, 301 × 86); generic: kit 03 wide parchment (44, 199) |
| SearchBox | Window | 266, 329, 215, 41 | 23, 179 | fill #FAD5A9, Stroke.Search, rounded ≈ 6 px | magnifier 277, 339, 22, 21; placeholder ink 310, 343, 101, 12 | **kit 10** search box (780, 264, 444 × 76) or kit 09 (26, 52, 489 × 114); 9-slice; TextBox over it from x 306 |
| CategoryList | Window | 267, 386, 219, 364 | 24, 236 | — | 6 rows | native Frame + UIListLayout (pitch below) |
| Category.All (active) | CategoryList | 267, 386, 219, 54 (body to x 475, arrow tip at 486, 412) | 24, 236 | Parchment.Active, 1–2 px outline, rivets, 3 px lighter inner rim | grid icon 283, 397, 33, 33; label "All" x 340, cap 406–420 | **kit 10** category arrow tab (1283, 261, 328 × 97, grid icon baked) ; kit 02 arrow plaque (653, 547, 278 × 67) and kit 14 parchment arrow tab (698, 848, 252 × 98) are alternatives |
| Category.Tools | CategoryList | row centre y 472 | — | no fill | hammer icon 283, 456, 35, 36; label x 340, cap 465–479 | icon: kit 10 detail-card hammer glyph (≈ 815–855, 555–590) |
| Category.Materials | CategoryList | centre y 537 | — | — | rocks icon 281, 520, 37, 36; label cap 531–544 | icon not in kit (stone-pile glyph) |
| Category.Food | CategoryList | centre y 601 | — | — | apple icon 283, 583, 33, 37; label cap 593–609 | icon not in kit |
| Category.Plants | CategoryList | centre y 666 | — | — | leaf icon 286, 648, 29, 37; label cap 658–673 | icon not in kit |
| Category.Misc | CategoryList | centre y 730 | — | — | sack icon 282, 711, 35, 38; label cap 723–737 | icon not in kit |
| Category rules | CategoryList | x 270–472, y 504, 569, 633, 697; 2 px | — | Rule.Soft; under Tools, Materials, Food, Plants (none under All or Misc) | — | native Frame (or kit 14 plain divider) |
| ItemGrid | Window | 492, 331, 592, 421 | 249, 181 | — | 6 × 4 slots | UIGridLayout CellSize 92 × 99, CellPadding 8 × 8 (column x 492, 592, 690, 790, 891, 991; row y 331, 438, 545, 653) |
| Slot (normal) | ItemGrid | 92 × 99 | — | parchment #FDDBB0, Stroke.Slot, rounded ≈ 4 px, rivet dots in the corners | item icon centred (≈ 70 px); count | **kit 05** slot normal (65, 45, 269 × 260) or kit 10 slot (788, 75, 159 × 154); both are square (aspect 1.03) — the mockup slot is taller (0.93), so 9-slice |
| Slot glow (selected) | Slot | 490, 328, 97, 103 for slot (0,0): ring 7–8 px, ≈ 2–3 px outside the slot outline, soft orange halo 1–2 px beyond | — | Glow.Selected | — | **kit 05** slot selected (375, 45, 283 × 262) or kit 10 selected (981, 73, 168 × 162) |
| Slot count | Slot | right edge = slot right − 8/9, bottom = slot bottom − 8/9; e.g. "1" ink 666–673 × 406–420 in slot 592, 331 | — | Font per Typography, no badge | quantity | native TextLabel; kit 05 count tags ("12" 1238, 367; "99" 1390, 355) are badges the mockup does not use |
| Slot (empty) | ItemGrid | last cell, 991, 653 | — | same slot art, no icon | — | kit 05 slot normal |
| GridDivider | Window | 1095, 261, 2, 516 | 852, 111 | Rule.Divider | — | native Frame |
| DetailCard | Window | 1112, 259, 296, 520 | 869, 109 | parchment #FDD5A6, 2 px soft border #EFC499/#F1B57D (no dark outline) | — | kit 10 detail card (773, 367, 320 × 440: its icon frame, stat glyphs, rules and leather button are baked; the mockup has no icon frame) or native Frame + UIStroke |
| DetailIcon | DetailCard | 1185, 297, 152, 166 (+ soft ground shadow to y ≈ 470) | 942, 147 | item art, centred on x 1261 | selected item | item sprite (`item_<catalogId>`); kit 16 stone axe (1177, 593, 195 × 248) for the mock item |
| ItemName | DetailCard | ink 1132, 481, 131, 21 | 889, 331 | per Typography | "Stone Axe" | native TextLabel x 1131, width 258 |
| ItemDescription | DetailCard | ink 1131, 516, 237, 39 (2 lines: 516–532, 538–554) | 888, 366 | per Typography | "A reliable tool for chopping wood / and gathering resources." | native TextLabel 1131, 512, 258, 46, TextWrapped |
| CardRule (×4) | DetailCard | x 1131–1388; y 571, 612, 653, 693; 2 px | — | Rule.Card | — | native Frame |
| StatRow (×3) | DetailCard | rows 1131, 572, 258, 40 / 613 / 653; centres y 592, 633, 673 | — | — | icon 1143, 583 (23 × 23) / 1142, 621 / 1143, 662; label x 1180; value right edge x 1385 | icons: kit 10 detail-card glyphs hammer / clock / weight (≈ 815–855 × 555–700) |
| Stat 1 | StatRow | — | — | — | "Harvest Power" · "+10" | — |
| Stat 2 | StatRow | — | — | — | "Attack Speed" · "0.9s" | — |
| Stat 3 | StatRow | — | — | — | "Durability" · "100 / 100" | — |
| EquipButton | DetailCard | 1126, 709, 270, 61 | 883, 559 | leather #A0380D, dark outline, 4 rivets, darker bottom lip | "EQUIP" centred on x 1260 | **kit 10** leather button (1306, 827, 267 × 79) or kit 03 wide leather (44, 63, 345 × 106) + its hover/pressed/disabled; 9-slice (mock aspect 4.4 vs kit 3.4) |

Grid contents in the mockup (row by row, count in brackets; "—" = no count):
stone axe (—, selected), pickaxe (1), spear (1), torch (6), logs (32), stones (28) /
plank (18), rope (12), plant fibre bundle (8), berries (14), white flowers (6),
mushroom (11) / axe (1), pickaxe (1), metal ingot (4), cloth (9), bone (7), hide (3) /
grass bundle (5), fern (9), coconut (4), shell (3), ore (6), empty. Icons for axe,
spear, torch, logs, stones, plank, rope, flowers, berries, mushroom, hide and bone
exist as kit 02 item tiles (855–1645 × 735–914); logs, stones, plank also in kit 10
(763–1141 × 827–923); kit 16 has stone axe, log, stone, plant fibre. Real slots
show `item_<catalogId>` sprites.

## Measurements log

Helpers live in `art/ui/kit/analysis/inventory/tools/` (run from the repo root);
`measure_inventory_settings.sh` re-runs everything below and writes
`art/ui/kit/analysis/inventory/measurements.txt`, `dim_overlay.txt` and
`kit_parts.txt`. The skill's `ref_tools.py` (info, grid, crop) was used for size,
overlay grids and 4–6× crops.

- Size: `ref_tools.py info` → 1672 × 941 RGB for 01/02/03.
- Window outline: `px.py 02 row 500 236 275` (dark 243–247, parchment from 248),
  `row 500 1405 1440` (dark 1423–1429), `col 700 140 180` (dark 150–154),
  `col 700 780 810` (dark 795/796–801).
- Tabs, header: `edges.py 02 row 270 240 1435 110` (Backpack 262–431, Vault
  441–605), `col 270 150 800 110` (tab 258–315), `col 600 150 800 110` (title
  rule 235–236, Vault 259–314, slot rows 331/332–429, 438–536, 545–643, 653–751).
- Close: `edges.py row 172 1330 1420 90`, `col 1352 155 240 90`, `row 215`,
  `col 1400 155 240 90` → 1346–1405 × 168–224.
- Search: `edges.py row 360 250 495 200` (266–268 … 480), `col 450 320 380 200`
  (329 … 369).
- All tab: `edges.py col 275 320 790 150` (386, 439); tip from a 6× crop
  (`ref_tools.py crop --box 440,380,70,65 --scale 6` → `all_tip.png`).
- Category rules: `px.py col 420 498 512` etc. (rules at 504, 569, 633, 697, lum
  192–202); extents `edges.py row 504 250 490 208`.
- Grid: `edges.py row 337/660/745 480 1100 120` (columns 492/493–583, 592–682,
  690–782, 790–882, 891–982, 991–1083), `col 498/1080 320 760 120` (rows).
- Selected glow: `px.py row 380 484 502` (490 #CF7A3E, 491 #D76100, 493–494
  #FDF5B0/#FFFFCE, 496 #AC4D06), `col 540 323 340` (328–334).
- Detail card / divider: `px.py row 450 1090 1122` (divider 1095–1096, card
  edge 1112–1113), `row 450 1398 1430` (card edge 1407–1408, window rule 1418),
  `col 1200 250 272` (card top 259–260), `col 1200 768 798` (card bottom 778).
  Rules: `edges.py col 1320 555 705 210` and `row 571/613/653/693 1115 1405 210`.
- EQUIP: `edges.py row 718 1110 1410 90` (1126 … 1395), `col 1150 690 790 90`
  (709 … 769).
- Icon and label boxes: `obj.py 02 80 …` (distance > 80 from the box median) and
  a luminance mask for the header backpack (283, 165, 71, 77).
- Text: `ink.py` row clusters (thresholds 90–175; `light` for text on leather).
- Colours: `col.py` box medians and `ink2.py` glyph cores.
- Fonts: `fontcmp.py` (render at matched height, compare width / IoU / ink; results
  in `font_compare.txt`) and `sbs.py` (`font_sbs1.png`).

## Dim overlay

Measured by fitting each screen to the HUD image (`01_hud.png`) over
background-only regions (`dimch.py`, `dimmap.py`): out = k · hud + c.

| Screen | k (R, G, B) | c (R, G, B) | ⇒ overlay alpha | ⇒ overlay colour | Tile k range (80 px tiles) |
|---|---|---|---|---|---|
| 02 Inventory | 0.306, 0.319, 0.353 | 9.7, 8.1, 5.2 | 0.65–0.69 | ≈ #0E0C08 | 0.28–0.39 (median 0.32) |
| 03 Settings | 0.252, 0.272, 0.329 | 6.0, 5.8, 4.7 | 0.67–0.75 | ≈ #080807 | 0.20–0.38 (median 0.30) |

- No blur: the best-fitting Gaussian blur of the HUD image is σ 0–1 px
  (`blur.py`), i.e. none.
- The HUD panels are dimmed too (player card parchment #FBD3A6 → #645343 in 02,
  #574A3D in 03, k ≈ 0.40 / 0.35), slightly less than the background. The
  overlay is darker toward the bottom and left of 03 (k 0.20–0.26) than at the
  top right (0.34–0.38); treat this as image noise, not a vignette, unless the
  art lead says otherwise.
- Build: one full-screen Frame, BackgroundColor3 #0E0C08 (or #000000),
  BackgroundTransparency 0.32 (02) / 0.30 (03 median); one shared value of
  **0.30–0.32** reproduces both within the measured spread. Open question 1.

## States

| Element | Default | Hover | Pressed | Selected / active | Disabled | Focus (gamepad) | Source |
|---|---|---|---|---|---|---|---|
| Tab (Backpack / Vault) | parchment, ink label, coloured icon | kit 03 parchment hover (407, 200: gold rim) | kit 03 parchment pressed (771, 199) | leather, cream label + cream line icon (Backpack in mock) | — | gold rim (as hover) | mock (active/inactive), kit 03 rows 1–2 |
| Category row | no fill | kit 09 list row hover (544, 316: gold rim) or a light Parchment.Active tint | — | arrow tab (kit 10 1283, 261) | — | as hover | mock (All active); hover not in mock |
| Item slot | kit 05 normal | kit 05 hover (706, 45: orange rim) | — | kit 05 / mock selected glow | kit 05 disabled (1028, 45: grey) — e.g. item not usable here | as hover | mock + kit 05 |
| Locked slot (vault capacity not bought) | — | — | — | — | kit 05 locked (1345, 45) | — | kit 05; not in mock |
| Search box | placeholder | — | — | focused: caret, typed text in Ink.Strong, placeholder hidden | — | — | implied |
| CloseButton | kit 03 close normal | kit 03 hover (537, 329) | kit 03 pressed (734, 329) | — | — | hover art | kit 03 |
| EquipButton | leather | kit 03 leather hover (409, 63) | kit 03 pressed (774, 63) | — | kit 03 disabled (1146, 63) — nothing selected or not equippable | hover art | kit 03 |
| Detail card | selected item | — | — | — | empty state (no item selected) not in mock: open question 4 | — | — |

## Motion and effects

None shown. The selected slot glow is static in the mock. Opening/closing motion
follows the lobby's other windows (not specified by this reference).

## Data and behavior

| Element | Shows / does | Data source or remote | Notes |
|---|---|---|---|
| Tab.Backpack | lobby backpack items | `VaultSnapshot` (RemoteFunction: vault and lobby backpack view), `VaultController` | Backpack holds `GameConstants.BACKPACK_SLOTS` = 50 slots |
| Tab.Vault | vault items | `VaultSnapshot` | `VAULT_START_SLOTS` 25 + 25 per upgrade |
| SearchBox | filters the grid by name | `ItemInfo.Matches(name, query)` | case-insensitive, plain text |
| Category rows | filters by category | `ItemInfo.CATEGORIES` = All, Tools, Materials, Food; `ItemInfo.InCategory` | **Plants and Misc have no backing category** (open question 2) |
| ItemGrid | one slot per item stack, count when quantity > 1 (mock also shows "1") | items from the snapshot; icon `item_<catalogId>` | 24 cells visible; 50 (backpack) / 25+ (vault) need a scroll region (open question 3) |
| Slot count | quantity | item.quantity | mock shows "1" on single tools but nothing on the selected stone axe (open question 5) |
| DetailIcon / ItemName | selected item art and name | ItemCatalog | — |
| ItemDescription | flavour text | **none**: ItemCatalog has no description field | open question 6 |
| Stat rows | Harvest Power, Attack Speed, Durability | `ItemInfo.Stats(item)` returns up to three {glyph, text} chips (damage + cooldown for weapons, "Tier n" + kind for tools, armour %, healing, food, boosts, ×quantity) | **labels and values differ** from the mock; **no durability** in the catalog (open question 7) |
| EquipButton | equips the selected item | world: `InventoryController` EQUIP/USE/PUT AWAY; lobby: no equip action exists (the old lobby screen had STORE/TAKE) | open question 8 |

## Vault tab (assumptions)

No mockup. Assumed, to be confirmed (open question 9):

1. Same window, title "INVENTORY" and header icon; the Vault tab takes the
   leather style and the Backpack tab the parchment style. Icon colours swap is
   unknown: the active Backpack icon is a cream line icon, the inactive Vault
   chest a full-colour icon. Options: (a) keep each tab's icon as is in both
   states; (b) use a cream line chest when Vault is active and a coloured
   backpack when Backpack is inactive (no art for either in the kit).
2. Same search box, category list, 6-column grid, divider and detail card; the
   grid shows vault contents.
3. Vault capacity (25 + 25 per upgrade) is not shown anywhere in the mock.
   Options: (a) a "n / cap" counter after the tab row (e.g. right of the Vault
   tab, x ≈ 620–1083, y 270–305); (b) locked slots (kit 05 locked) after the
   last owned slot; (c) nothing.
4. The detail card's action for vault items: options (a) TAKE (move to
   backpack), (b) EQUIP as in the mock, (c) both (two buttons in the card width,
   each ≈ 129 × 61 with an 12 px gap).
5. Moving items between Backpack and Vault (STORE / TAKE, STORE ALL in the old
   screen) has no control in the mock.

## Asset map

| Asset | Kit source | Size in mock | 9-slice | Status |
|---|---|---|---|---|
| Window frame | kit 10 window (40, 48, 706 × 782) with baked contents erased, or kit 04 frame 1 (48, 43, 1082 × 426) | 1187 × 652 | yes (corners ≈ 45 px) | to slice |
| Close button ×4 states | kit 03 (342/537/734/933, 329, ≈140 × 135) | 60 × 57 | no (scale) | to slice |
| Tab leather / parchment ×states | kit 10 tabs (1209, 55 / 1210, 154); kit 03 wide buttons rows 1–2 for hover/pressed/disabled | 170 × 58, 165 × 56 | yes | to slice |
| Tab icons | kit 10 tab icons (cream backpack ≈ 1240, 68; chest ≈ 1243, 170) | 34 × 40, 56 × 36 | no | to slice |
| Header backpack | kit 10 window header (≈ 85, 90) / kit 06 (47, 41) | 71 × 77 | no | to slice |
| Search box | kit 10 (780, 264, 444 × 76) | 215 × 41 | yes | to slice |
| Category arrow tab | kit 10 (1283, 261, 328 × 97; grid icon baked — slice without it, or keep for "All" only) | 219 × 54 | yes (arrow end fixed) | to slice |
| Category icons | grid: kit 10 arrow tab; hammer: kit 10 card glyph; rocks / apple / leaf / sack: **not in kit** | ≈ 33–37 px | no | new art needed |
| Slot normal / selected / hover / disabled / locked | kit 05 (65/375/706/1028/1345, 45) | 92 × 99 (selected 97 × 103) | yes | to slice |
| Detail card | kit 10 (773, 367, 320 × 440) or native | 296 × 520 | yes | to slice / native |
| Stat glyphs | kit 10 card glyphs hammer / clock / weight | 23 × 23 | no | to slice |
| EQUIP button ×states | kit 10 (1306, 827, 267 × 79) / kit 03 row 1 | 270 × 61 | yes | to slice |
| Scrollbar (if added) | kit 10 (1603, 378, 29 × 357) / kit 09 (1521, 461, 45 × 265) | — | yes | optional |
| Item icons | kit 02 item tiles, kit 10 materials, kit 16; game `item_<catalogId>` sprites | ≈ 70 px in slot, 152 × 166 in card | no | per item |

Kit sheets came from background removal: fills at alpha 250–254 and a faint
red/yellow fringe (alpha 1–63) must be cleaned when slicing (README).

## Open questions

Each has the default that will be used if unanswered.

1. **Overlay strength**: one shared value for every lobby window? Default:
   #0E0C08 (or black) at BackgroundTransparency 0.31.
2. **Plants and Misc categories** have no `ItemInfo` category. Options: (a) add
   Plants and Misc to `ItemInfo.CATEGORIES` with a family mapping (Misc = items
   with no category today: armour, ammunition, siege items, placeables); (b) show
   only All, Tools, Materials, Food. Default: (b) until gameplay adds them.
3. **More items than 24 cells**: options (a) the grid area becomes a vertical
   ScrollingFrame (6 columns, 107 px row pitch) with a thin scrollbar in the
   12 px gap between grid (x 1083) and divider (x 1095); (b) pages. Default (a).
4. **Detail card with nothing selected**: options (a) select the first item on
   open (as the mock does); (b) an empty card with a hint. Default (a).
5. **Count on single items**: the mock shows "1" on tools but nothing on the
   selected stone axe. Default: show the count only when quantity > 1.
6. **Item descriptions** don't exist in data. Default: hide the description and
   move the first rule up; or add a `description` field to `ItemCatalog`.
7. **Stat rows**: mock labels (Harvest Power, Attack Speed, Durability) vs
   `ItemInfo.Stats` chips. Default: three rows from `ItemInfo.Stats` (icon from
   the chip glyph, label + value split from the chip text); durability omitted.
8. **EQUIP in the lobby**: what does it do (set a loadout item for the next run?
   move to hotbar?). Default: the button shows the action the old screens had
   for that place (TAKE / STORE in the lobby), disabled when none applies.
9. **Vault tab layout and actions**: see the assumptions above.
10. **Title weight**: Merriweather Black (if available) or Bold. Default Bold +
    1 px stroke in Ink.Title if Black is unavailable.

## Deviations from reference

- Merriweather's lowercase is ~10 % taller than the mockup's at equal cap
  height; titles may be lighter if only Bold is used.
- Kit slots are square; the mockup's are 92 × 99, so the slot art is 9-sliced
  (rivets stay in the corners).
- The mockup's gentle ground shadow under the detail icon is part of the item art
  (or a separate soft ellipse image); no native equivalent.

## Fix round 3

- **Rarity**: a small rarity dot (Kit rarity badge) on each slot's bottom left
  for Uncommon and rarer items, and after the item's name in the detail card
  for every item.
- **All** uses the scroll icon (the chest read as the Vault; the mockup's grid
  is not in the kit).
- **Gamepad** (R23): when the slots arrive after the window opened on a
  gamepad, selection moves to the first slot rather than staying on ✕.
- Items without kit art (bows, swords, daggers, armour) show the Kit's neutral
  kind glyph; their names are in the tooltip and detail card (ITEM_ART.md).
