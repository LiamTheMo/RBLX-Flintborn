# Forge screen UI spec

Reference: `art/reference/ui/lobby/06_forge.png`. Kit: `art/reference/ui/lobby/kit/`
(sheet numbers below are the file prefixes). Design resolution: 1672 × 941 (the image
size); every bound is a screen pixel of the mockup, x, y, w, h from its top-left, ±1–2 px.
Status: Draft. Source of truth for build: the reference image.

Raw crops, font comparisons and the measuring scripts are in `art/ui/kit/analysis/forge/`.

## Overview

The Ancestral Forge (GDD §15–16, §25.3), lobby only. A modal parchment window over the
dimmed lobby HUD, opened by the Forge tile of the HUD menu grid (`ForgeController.Toggle`)
and closed by the ✕ button, ButtonB, or the Forge tile again. Three columns: RECIPES (list,
one row selected), the selected recipe (name, picture, description, REQUIRES cards,
QUANTITY stepper, FORGE button), and YOUR MATERIALS (vault materials, one row
highlighted). The window replaces the forge mode of `Hud/CraftingPanel`.

## Dim overlay and the HUD behind

Measured by fitting `modal = k × hud + c` per channel over HUD parts that sit in the
same place in `01_hud.png` and this image (player card, Coins, Gems, gear) and over open
scenery (sky, grass, trees). The fit boxes are in the Measurements log.

| Region | k (R, G, B) | offset c | Note |
|---|---|---|---|
| Player card + currencies + gear (zero-offset fit) | 0.326, 0.326, 0.339 | — | median of bright parchment pixels: #FACF9F (250, 207, 159) → #514335 (81, 67, 53), ratio 0.324–0.333 |
| Same, free fit | 0.273, 0.266, 0.280 | 12.3, 11.5, 8.8 | implies overlay colour ≈ #110F0C |
| Sky / mountains right of window | 0.311 | — | |
| Grass bottom-left, trees left, scene right | 0.304–0.320 | — | |

- Overlay: near-neutral black at **68 % ± 4 % opacity** (Frame BackgroundColor3 #000000 to
  #110F0C, **BackgroundTransparency ≈ 0.32**, range 0.28–0.36). Same value on the journal
  (see `JournalScreen.md`). The current veil (`veil` #1A0E06 at 0.45) is lighter and
  warmer than the mockup.
- Blur: no consistent evidence (edge energy is lower in some areas and higher in others;
  the scene itself was redrawn between mockups). Options: no blur, or a small BlurEffect.
- The whole HUD (player card, currencies, gear, menu grid, party panel, XP bar, hotbar)
  stays visible under the overlay; the window covers its middle.
- Mockup difference: the hotbar sits **40 px lower** and the XP bar **50 px lower** than in
  `01_hud.png` (cross-correlation of the hotbar and XP-bar strips, dx 0). The top HUD is
  not shifted. See Open questions.

## Tokens

Colours are medians of flat boxes (`colors_forge.py`).

| Token | Value | Used by |
|---|---|---|
| Color.Overlay | #000000 @ 0.32 transparency (see above) | dim layer |
| Color.Parchment | #FEE1B8 (window interior, column backgrounds #FEE0B6) | window, columns |
| Color.FrameOutline | #170E06 (outer 1–2 px), #DB9F60 inner stitch line 6 px inside | window edge |
| Color.Leather | #98300C–#9E360D (top), #94310E (bottom) | FORGE, −/+, ✕ |
| Color.Rule | #BF9264 (top rule y 248), #A87445 (column rule x 657), #B37F4E (rule x 1046), #DCAA75 (left rule x 320), #D8AC7B / #D0A474 (centre dividers) | rules |
| Color.CardFill | #FDE2BB (recipe rows), #FDE2BC (material rows), #FDE0B7 (requires cards) | rows, cards |
| Color.CardOutline | #E8C394 (recipe rows), #ECC396 (material rows), #ECC89A (requires cards) | 2 px soft outline |
| Color.SelectFill | #FED692 (centre) → #FEDA9B (left edge) → #FDD287 (bottom) | selected recipe row |
| Color.SelectGold | outer #FCCA48, 1 px line #240803, inner #FEC737 | selected recipe row border |
| Color.HighlightFill | #FDD696 | highlighted material row |
| Color.HighlightOutline | #E2A04B (2 px, a little darker on the right and bottom) | highlighted material row |
| Color.InkTitle | #2E0C05 (core #2A0803–#320F07) | window title |
| Color.Ink | #1E0000–#240600 (core) | section heads, names, counts |
| Color.InkHand | #57280B (subtitle), #583517 (row descriptions), #1F0902 (centre description) | handwritten texts |
| Color.CountShort | #8A0101 core, #99150E median | the red "6" |
| Color.OnLeather | #FDFBF9 (label), #FBEBD5 (anvil glyph), #FAF7F4 (✕) | button glyphs and labels |
| Color.ArtSmear | #F4CEA2 | painted smear behind the picture |
| Font.Serif | Merriweather Bold (the repo's `serif`) | all non-handwritten text |
| Font.Hand | Comic Neue Angular Regular (closest; see Fonts) | subtitle, row descriptions, centre description |

## Fonts

Compared in 3× renders under the reference crops (`fontcmp.py`, outputs
`font_title.png`, `font_subtitle*.png`). Widths are at the measured cap height.

| Text | Measured | Closest Roblox family | Fit |
|---|---|---|---|
| ANCESTRAL FORGE | caps 35 px, small caps 30 px (ratio 0.86), 405 px wide | **Merriweather Bold** as faux small caps: RichText with the initials at TextSize ≈ 46 and the rest at ≈ 40 | width 406 vs 405; wedge serifs, G spur and R leg match |
| Turn raw materials… | ascender 16 px, x-height 9 px, 443 px wide, thin monoline, double-storey a | **Comic Neue Angular** (Roblox's Cartoon font) at TextSize ≈ 23.5 | Comic Neue renders 431 px (−3 %); letter shapes match. Roblox ships the Angular cut (angled stroke ends) while the mockup has round ends. Alternatives: Patrick Hand (bolder, −14 % width), Indie Flower (single-storey a, −10 %), Kalam (slanted). Uncertain. |
| Recipe descriptions, centre description | same handwritten face | Comic Neue Angular | row text −1 %, centre text +8 % |
| IRON PICKAXE, names, heads, counts, FORGE | bold serif | Merriweather Bold | all-caps heads within ±6 % of width; mixed-case names and IRON PICKAXE set 12–21 % wider than the mockup at equal cap height. Options: match cap height (wider text), or match width (TextSize in the "width" column below). |

Merriweather Bold: TextSize ≈ cap height / 0.75. Comic Neue: TextSize ≈ cap height / 0.68.
Text halo: a faint lighter ring 2 px out from dark text (#FCE7C3 against #FEDFB4); optional,
e.g. a 1 px cream UIStroke at high transparency. No dark text strokes. Text on leather has
no visible stroke.

## Element tree

Bounds are screen px (x, y, w, h). All elements are children of Window unless noted;
anchor intent "window" means fixed offsets inside the window.

| Element | Parent | Bounds | Anchor intent | Appearance | Content | Kit piece |
|---|---|---|---|---|---|---|
| Overlay | ScreenGui | 0, 0, 1672, 941 (bleed past safe area) | full screen | see Dim overlay; z below Window, above HUD | — | native |
| Window | Overlay | 285, 132, 1102, 682 | screen centre (window centre 835.5, 472.5 vs screen 836, 470.5) | parchment with a dark scorched outline: dark 285–289 (#170E06 with an orange line inside), parchment from 290; dashed stitch line 6 px in (#DB9F60) | — | 04 large window (≈50–1127, 45–467) as a 9-slice; mockup aspect 1.62 vs kit 2.55 |
| CornerTL / TR / BL / BR | Window | 283, 132, 42, 43 / 1345, 131, 43, 44 / 284, 770, 41, 44 / 1340, 770, 45, 45 | window corners | leather brackets #8E320F with two rivets | — | 04 corner brackets (part of the frame); 14 corner pieces (95–325, 50–245) |
| ClaspL1 / L2 | Window | 283, 281, 22, 32 / 283, 726, 27, 33 | left edge | leather tab with rivet, #A13E12 | — | 04 side clasps (right edge of the large window, ≈1105–1130, 140–165 and 375–400); 14 clasps (398–440, 65–185) |
| ClaspR1 / R2 | Window | 1366, 281, 22, 32 / 1360, 726, 28, 33 | right edge | as above, #A94E19 | — | same |
| HeaderIcon | Window | 338, 147, 101, 89 | top-left | anvil with a hammer resting on it, dark outlines | — | 17 anvil + hammer (1105–1360, 320–550); 11 anvil (1125–1365, 50–300) has no hammer |
| Title | Window | 470, 163, 405, 35 (cap top 163, baseline 197) | top-left, left-aligned | Merriweather Bold faux small caps, Color.InkTitle | "ANCESTRAL FORGE" ("A" and "F" at 35 px cap) | native text |
| Subtitle | Window | 469, 210, 443, 17 (ascender 210, baseline 225) | under title, left-aligned | Font.Hand ≈ 23.5, #57280B | "Turn raw materials into tools for the island." | native text |
| Close | Window | 1289, 158, 63, 61 | top-right | leather square, dark outline, 4 rivets, white ✕ (glyph ≈ 1300–1340, 172–205) | — | 03 close button, normal (345–480, 330–462), with hover / pressed / disabled to its right |
| TopRule | Window | 322, 248, 1028, 2 | under header | #BF9264, small curl at each column join | — | 14 divider (60–850, 475–570), plain |
| RecipesColumn | Window | 320, 248, 338, ≈520 (left rule fades out by y ≈ 768) | left | rules only: left x 320 (#DCAA75), right x 657 (#A87445, runs to y 787) | — | 01 three-column layout (1030–1508, 60–325) shows the same column rules |
| RecipesHead | RecipesColumn | 343, 268, 80, 14 | column top-left | Merriweather Bold cap 14 → TextSize ≈ 18, Color.Ink | "RECIPES" | native text |
| RecipeList | RecipesColumn | 337, 294, 304, 458 | column | vertical list, pitch ≈ 76.6 px, 6 rows visible | rows | ScrollingFrame (see States) |
| RecipeRow (normal) | RecipeList | 339, 373, 301, 69 (rows 2–6 at y 373, 449, 525, 601, 678; heights 69, 69, 69, 71, 74) | list | fill #FDE2BB, 2 px soft outline #E8C394, radius ≈ 6, no rivets | — | 01 "list + cards" soft card outline (720–978, 383–512); 09 list row normal (25–515, 318–432) is the closest row but has a dark outline, dot and chevron |
| RecipeRow (selected) | RecipeList | 337, 294, 304, 74 | list | Color.SelectFill, border: 2 px gold #FCCA48, 1 px #240803, 2 px gold #FEC737; dark rivet dots in the 4 corners | — | 03 small parchment button, gold state (808–1022, 815–928); 09 list row selected (545–1035, 318–432) |
| Row.Icon | RecipeRow | 351, row y + 2, 66, 64 (row 1: 345, 302, 85, 65) | row left, centred x ≈ 383 | full-colour item icon with dark outline | output item | 12 pickaxe (1170–1300, 645–770); 12 axe (1020–1150, 640–765) / 16 stone axe; 02 spear tile; 11 hammer (605–830, 595–810); 11 torch (885–1060, 580–830); 17 campfire (850–1070, 70–300) |
| Row.Name | RecipeRow | 440, row y + 18, ≤ 190, 15 (cap) | row, left-aligned | Merriweather Bold cap 15 → TextSize 20 (17 width-matched), Color.Ink | "Iron Pickaxe", "Stone Hatchet", "Stone Spear", "Stone Hammer", "Wooden Torch", "Campfire" | native text |
| Row.Desc | RecipeRow | 441, row y + 44, ≤ 190, 11 (cap) | under name | Font.Hand cap 11 → TextSize ≈ 14.5, #583517 | "Mine stone and ore." etc. | native text |
| CentreColumn | Window | 657, 248, 389, ≈540 | middle | rules: left x 657, right x 1046 (#B37F4E, to y 797) | — | 01 three-column layout |
| RecipeName | CentreColumn | 705, 267, 214, 24 (cap) | column top, left-aligned at x 705 | Merriweather Bold caps, cap 24 → TextSize 32 (29 width-matched), Color.Ink | "IRON PICKAXE" | native text |
| Picture | CentreColumn | 755, 310, 242, 233 (ink); smear 725–962 × 338–522 | centred x ≈ 875 | large item art with dark outline over a soft painted smear #F4CEA2 | output item | 12 forge recipe card picture (945–1180, 160–420), framed there; mockup has no frame |
| Description | CentreColumn | 709, 556, 274, 45 (two centred lines, baselines 570 and 595, pitch 25) | centred on x ≈ 847 | Font.Hand cap 15 → TextSize ≈ 20–21.5, #1F0902 | "A sturdy iron pickaxe for mining / stone and ore more efficiently." | native text |
| Divider1 | CentreColumn | 674, 608, 356, 2 | full column width | #D8AC7B, dot at each end | — | 14 divider with end dots (60–850, 555–570) |
| RequiresHead | CentreColumn | 686, 623, 83, 13 (cap) | left | Merriweather Bold cap 13 → TextSize ≈ 16.5 | "REQUIRES" | native text |
| ReqCard1 / 2 | CentreColumn | 681, 645, 167, 65 / 857, 645, 171, 65 | left to right, gap 9 | fill #FDE0B7, 2 px outline #ECC89A, radius ≈ 6 | one input | 01 soft card (as rows); 12 requirement rows (1195–1460, 180–420) for the data pattern |
| Req.Icon | ReqCard | 695, 657, 53, 46 / 871, 654, 54, 49 | card left | material icon | input | 10 material icons: logs (765–870, 828–918), stones (902–1000); no iron-ore icon on any sheet |
| Req.Name | ReqCard | 765, 660, 54, 11 (cap) / 941, 660, 36, 11 | right of icon | Merriweather Bold cap 11 → TextSize ≈ 15 (13 width-matched), Color.Ink | "Iron Ore" / "Wood" | native text |
| Req.Count | ReqCard | 765, 683, 42, 16 / 942, 683, 50, 16 | under name | Merriweather Bold digits 16 px → TextSize ≈ 21; RichText: have coloured, " / need" in Color.Ink | "6 / 4" (6 in Color.CountShort), "12 / 3" | native text |
| Divider2 | CentreColumn | 673, 722, 371, 2 | full column width | #D0A474, dot at left end | — | 14 divider |
| QuantityHead | CentreColumn | 676, 757, 85, 13 (cap) | bottom-left | Merriweather Bold cap 13 → TextSize ≈ 16.5 | "QUANTITY" | native text |
| Minus | CentreColumn | 778, 742, 43, 44 | bottom row | leather square, dark outline, 4 rivets, white "−" bar (≈ 787–811, 761–769) | — | no leather −/+ on the sheets: 09 steppers (33–138 and 165–272, 610–712) are parchment with dark glyphs; 03 glyph buttons likewise; 01 small leather square (570–637, 673–733) + glyph is the leather option |
| QtyField | CentreColumn | 826, 741, 63, 46 | between − and + | parchment #FEE2BB, 1 px brown outline #8C562A, rivet dots | "1" (digit 20 px tall → TextSize ≈ 26, centred) | 01 small parchment square (655–722, 673–733); 05 count badge (1240–1345, 368–462) |
| Plus | CentreColumn | 893, 742, 43, 44 | right of field | as Minus with "+" | — | as Minus |
| ForgeButton | CentreColumn | 958, 731, 260, 66 (dark drop shadow to y ≈ 800) | bottom-right of the centre area | leather #98300C, dark outline, 6 brass rivets; icon + label group centred on x ≈ 1085 | anvil glyph (1015, 746, 39, 35, #FBEBD5) + "FORGE" (1077, 755, 80, 19 cap; Merriweather Bold → TextSize ≈ 25, 23 width-matched; #FDFBF9) | 12 FORGE button (1150–1397, 557–625) has no icon; 03 PLAY / CONFIRM (45–402 / 427–785, 813–933) show the icon + label layout; 03 leather states row 1 for hover / pressed / disabled |
| MaterialsColumn | Window | 1046, 248, ≈304, ≈470 | right | left rule x 1046 | — | 01 three-column layout |
| MaterialsHead | MaterialsColumn | 1067, 269, 180, 15 (cap) | column top-left | Merriweather Bold cap 15 → TextSize ≈ 20 | "YOUR MATERIALS" | native text |
| MaterialList | MaterialsColumn | 1064, 299, 280, 395 | column | vertical list, pitch ≈ 67, 6 rows visible | rows | ScrollingFrame |
| MaterialRow | MaterialList | 1065, y, 278, 59 (y 299, 366, 431, 498, 566, 634) | list | fill #FDE2BC, 2 px outline #ECC396, radius ≈ 6 | — | 01 soft card; 09 list row normal |
| MaterialRow (highlighted) | MaterialList | 1065, 431, 278, 59 | list | Color.HighlightFill, Color.HighlightOutline, no rivets, no dark line | "Iron Ore 6" | 09 list row selected (545–1035, 318–432), gold; differs (no glow, no dot, no chevron) |
| Mat.Icon | MaterialRow | 1078, row y + 7, 53, 46 | row left | material icon | material | 10 logs / stones; 02 item tiles: berries (1120–1240, 830–910), plant fiber (995–1105, 830–910); 19 leaf sprig (810–890, 135–230) for Fiber; no iron-ore or clay icon on any sheet |
| Mat.Name | MaterialRow | 1149, row y + 22, ≤ 150, 14 (cap) | left-aligned | Merriweather Bold cap 14 → TextSize ≈ 18 (17 width-matched) | "Wood", "Stone", "Iron Ore", "Fiber", "Berries", "Clay" | native text |
| Mat.Count | MaterialRow | right edge 1326, row y + 23, 15 tall | right-aligned | Merriweather Bold digits → TextSize ≈ 20 | 12, 28, 6, 14, 9, 4 | native text |

Z-order (back to front): HUD → Overlay → Window art → rules and cards → rows → icons and
text → clasps and corner brackets (they overlap the frame edge) → Close.

## Measurements log

Run from the repo root. `T=<skill>/scripts/ref_tools.py`; helpers in
`art/ui/kit/analysis/forge/` (`runs.py` colour runs, `edges.py` edge clusters, `ink.py`
and `mlib.py` text ink boxes and row profiles, `mask.py` colour-class bounding boxes,
`parchruns.py` parchment spans, `ruler.py` labelled zoom crops, `kitgrid.py` kit sheets
on a grid, `halo.py` text halo rings, `fontcmp.py` font renders).

- Size: `python3 $T info art/reference/ui/lobby/06_forge.png` → 1672 × 941, RGB.
- Window edges: `python3 $T scan --row 480 --start 270 --end 340 --tol 8 …06_forge.png`
  (dark at 285, parchment from 291), same at 1350–1410 (dark 1380–1386), `--col 800`
  120–170 (dark 132–136) and 780–830 (dark 808–813).
- Corners / clasps: `python3 art/ui/kit/analysis/forge/mask.py <img> leather 275 125 50 50`
  and the three other corners; clasps from per-row leather counts at x 282–300 and
  1368–1390 (rows 281–312 and 726–758).
- Rules: `edges.py <img> col 620 240 800 40` (rows and selected row edges), inline numpy
  extents (top rule y 247–250 spans 322–1378, rules x 320 / 657 / 1046 from y 250).
- Rows: `edges.py <img> col 1250 280 720 40` (material rows), `edges.py <img> row 360 300 680 25`
  (selected recipe row x 337–640).
- Requires cards: `edges.py <img> row 690 670 1045 40`, `col 700 630 720 40`.
- Buttons: dark-outline runs (luma < 80) along row 765 and columns 799, 914, 1100, 1180;
  `mask.py <img> notparch 824 735 66 55` (quantity field); zooms `r_forgebtn.png`,
  `r_stepper.png`.
- Text: `python3 art/ui/kit/analysis/forge/measure_forge.py` (all text boxes, cap tops,
  baselines, ink cores).
- Colours: `python3 art/ui/kit/analysis/forge/colors_forge.py`.
- Check: `overlay_check.png` draws the main bounds of this table on the mockup; every box
  sits on its element's edge.
- Halo: `python3 art/ui/kit/analysis/forge/halo.py <img> 465 155 420 50 110`.
- Fonts: `fontcmp.py <img> 465 155 420 50 "A|NCESTRAL |F|ORGE" cap 35 font_title.png
  art/ui/fonts/Merriweather-Bold.woff …`; subtitle against Comic Neue, Patrick Hand,
  Indie Flower and Kalam (Google Fonts OFL files fetched outside the repo); width table
  from Pillow `getlength` at matched cap height.
- Dim overlay: least-squares fit per channel of this image against `01_hud.png` over
  45,65,340,65 (player card), 1320,72,110,42, 1452,72,96,42, 1568,72,48,42, and over
  scenery boxes 1400,130,260,120 / 0,700,250,240 / 0,150,60,500 / 1400,520,270,250; bottom
  HUD shift by normalised cross-correlation of 555–1120 × 800–890 (hotbar) and
  560–1100 × 765–790 (XP bar).

## States

| Element | Default | Hover | Pressed | Selected | Disabled | Focus (gamepad) | Source |
|---|---|---|---|---|---|---|---|
| RecipeRow | soft card | not shown (kit 03 small parchment hover is gold) | not shown | gold border + gold fill (row 1) | locked recipes exist in data, not shown | not shown | reference row 1; kit 03, 09 |
| MaterialRow | soft card | not shown | — | highlighted (Iron Ore) | — | not shown | reference |
| ReqCount | have in ink | — | — | — | have in red (the "6") | — | reference (meaning ambiguous, see Open questions) |
| Minus / Plus | leather | kit 03 leather hover (410–750) | kit 03 pressed (775–1123) | — | kit 03 disabled (1147–1490); at quantity 1 the mockup still shows Minus enabled | not shown | kit 03 |
| ForgeButton | leather + icon | kit 03 hover | kit 03 pressed | — | kit 03 disabled (needed: locked, short, busy) | not shown | kit 03 |
| Close | leather ✕ | kit 03 close hover (538–677) | pressed (735–875) | — | — | not shown | kit 03 |

Scroll regions: RecipeList (6 rows visible; the real list is 8 special recipes plus one
Permanent conversion per eligible gear piece) and MaterialList (6 visible; the vault holds
any number of material types). The mockup shows no scrollbar; kit 09 has one
(1520–1567, 460–725; thumb 1600–1647, 478–620) and kit 10 another (1603–1632, 378–735).

## Motion and effects

None shown. The selected recipe row and the highlighted material row are static; no glow
pulse is implied.

## Data and behavior

Remotes: `ForgeSnapshot` (lobby, `ForgeService.snapshot`) and `ForgeCraft(recipeId,
sourceId?, nonce)`. Counts come from the vault only (`ForgeRules.Owned`).

| Element | Shows / does | Data source | Notes |
|---|---|---|---|
| RecipeList rows | one row per Forge recipe | `ForgeSnapshot().recipes[]`: `id, kind, category, name, output, quantity, unlocked, requirement, inputs[{catalogId, name, owned, needed}]`, Permanent ones also `tier, family, sources[]` | Mockup rows (Stone Hatchet, Stone Spear, Stone Hammer, Wooden Torch, Campfire) are field-crafting style names; only Iron Pickaxe is a Forge recipe. The real list: Iron Pickaxe, Iron Axe, Iron Sword, Iron Head / Chest / Legs, Flint Arrow ×50, Potion ×2, then Permanent conversions sorted by tier. Name text = `recipe.name` (+ " ×N" when `quantity > 1`, as today). |
| Row.Icon / Picture | output item art | `ItemSlot.IconFor(output)` | today falls back to a category glyph when no icon is uploaded |
| Row.Desc / Description | one-line and two-line flavour text | **no source** | no description field exists in `ItemCatalog`, `ForgeRecipes` or `ItemInfo`. Options: add descriptions to the catalog or recipes; show derived text (`ItemInfo.Stats` lines, category, unlock text); leave empty. |
| Categories | — | `ForgeRecipes.Categories` (Tools, Weapons, Armor, Supplies, Permanent) | the mockup has no category tabs; today's window has one tab per category. Options: one list with category headers; a filter control; no grouping. |
| Locked recipes | — | `unlocked == false`, `requirement` ("Unlock: extract 1 time(s), …") | not shown in the mockup; a locked row state and where the unlock text goes are needed |
| RequiresCards | one card per input: icon, name, owned / needed | `inputs[]` (sorted by name on the server) | Iron Pickaxe really needs Iron Bar 20 + Wood 10; the mockup shows Iron Ore 4 + Wood 3. Two cards fit; Flint Arrow has 3 inputs, Permanent conversions up to 4–5 (e.g. Guardian's Fang: Ancient Ember, Guardian Heart, Charged Core, Glow-Fur), so the card row must take more cards or wrap. |
| ReqCount colour | red have count | today: `haveEnough` #2E7D24 / `haveShort` #A3271B on the have number | in the mockup 6 / 4 is red although 6 ≥ 4, and 12 / 3 is plain ink, not green. See Open questions. |
| QUANTITY stepper | how many to forge | **no server support** | `ForgeCraft` takes no count and `ForgeRules.Craft` makes exactly one result per request (one nonce, one receipt). `CraftingPanel.MAX_BATCH` (50) is used for smelting only; forge mode hides the stepper today. Options: N sequential requests, each with its own nonce, stopping at the first failure; a server change adding a validated count; hide the stepper. Upper bound if kept: `min(owned // needed)` over inputs (the entry's `can`), also bounded by lobby backpack space (`BackpackFull`). Not the same as `recipe.quantity` (items per craft, e.g. 50 arrows). |
| ForgeButton | sends the craft | `ForgeCraft(recipeId, sourceId, nonce)`, retried once with the same nonce on transport failure | label "FORGE"; Permanent recipes use "CONVERT" and first open a confirmation naming the exact source item (`CraftingPanel:Confirm`, 1.5 s arm delay). Enabled only when every input is covered, unlocked, not busy, and (Permanent) a source is chosen. Server reasons shown via `Reasons.Text`: InTrade, TradeSettling, InTransit, Locked, MissingMaterials, BackpackFull, WrongSource. |
| Status line | "Forged. Check your lobby backpack or vault." / "Not forged: …" | `ForgeController.submit` | no place for it in the mockup |
| Permanent sources | vault gear the conversion can use | `recipe.sources[]` (`instanceId, name, qualityRoll`) | today the right column lists them; the mockup's right column is YOUR MATERIALS. Needs a place (options: in the centre column under REQUIRES, a picker popup, or the right column switches content for Permanent recipes). |
| YOUR MATERIALS | every vault material and its count | not in `ForgeSnapshot` (it only carries each recipe's own inputs). `VaultSnapshot().materials[]` has `catalogId, name, quantity`, sorted by name. Options: call `VaultSnapshot`, or extend `ForgeSnapshot` with the vault material map. | Mockup names vs catalog: "Fiber" is "Plant Fiber"; "Berries" has no catalog item (Juniper Berry, Elderberry, Raspberry exist); Iron Ore, Wood, Stone, Clay exist. |
| Highlighted material | Iron Ore | client-side | Iron Ore is an input of the selected recipe and its count (6) is the red "have" number in REQUIRES. Wood is also an input but is not highlighted. Options: highlight the limiting input (the one with the lowest owned / needed, here Iron Ore 6/4 = 1 craft vs Wood 12/3 = 4); highlight every input of the selected recipe; highlight a material the player clicked (selection of its own); highlight a short input. |
| Close / ButtonB | closes; ButtonB closes the confirmation first | `ForgeController` | — |
| Refresh | snapshot on open and after each craft | `ForgeController.refresh` | — |

## Asset map

| Asset | Kit source | Size in mockup | 9-slice | Status |
|---|---|---|---|---|
| Window frame | 04 large window (≈50–1127, 45–467) | 1102 × 682 | yes: corners ≈ 42 px, clasps placed separately | to slice |
| Side clasp | 04 (≈1105–1130, 140–165) or 14 (398–440, 65–185) | 22 × 32 | no | to slice |
| Anvil + hammer icon | 17 (1105–1360, 320–550) | 101 × 89 | no | to slice |
| Close button (4 states) | 03 row 3 | 63 × 61 | no | to slice |
| Soft card (rows, requires cards) | 01 "list + cards" card (720–978, 383–512) | 301 × 69, 278 × 59, 167 × 65 | yes, or native Frame + UIStroke 2 px + UICorner 6 | either |
| Selected row frame | 03 small parchment, gold (808–1022, 815–928) | 304 × 74 | yes | to slice |
| Highlighted row frame | none exact; 09 list row selected | 278 × 59 | yes, or native | either |
| Leather button (4 states) | 03 row 1 (normal 45–388, 62–168) | 260 × 66 | yes | to slice |
| Anvil glyph (white) | none; silhouette from 17 or 11 anvil | 39 × 35 | no | to make |
| − / + leather squares | none; 01 small leather square (570–637, 673–733) + glyph | 43 × 44 | no | to make |
| Quantity field | 01 small parchment square (655–722, 673–733) | 63 × 46 | yes | to slice |
| Dividers with end dots | 14 (60–850, 475–570) | 356 × 2 | horizontal 3-slice, or native line + dots | either |
| Item / material icons | 10, 11, 12, 16, 17, 02 (see tree) | 53–66 px rows, 242 px picture | no | iron ore, clay, stone hatchet (stone head), stone hammer: none on the sheets |

## Open questions

1. Red have count: what does red mean when have ≥ need (6 / 4)? Options: limiting input;
   short input (mockup numbers then wrong); the input linked to the highlighted material.
   Today's code colours have green / red by enough / short.
2. Highlighted material row: rule for which row is highlighted (options under Data).
3. QUANTITY: server has no batch forge (options under Data). Should Minus show disabled
   at 1 (kit 03 disabled state exists)?
4. Descriptions (row and centre): no data source.
5. Categories, locked recipes, Permanent sources and the status line have no place in the
   mockup.
6. Bottom HUD position under the modal: mockup moves the hotbar down 40 px and the XP bar
   down 50 px (the journal mockup: hotbar 37 px). Options: keep the HUD where it is (only
   dimmed); slide the bottom bar down while a modal is open.
7. Handwritten face: Comic Neue Angular is the nearest shipped family but has angled
   stroke ends; Patrick Hand is the next option. Confirm in Studio's font picker.
8. Mixed-case serif text sets 12–21 % wider in Merriweather Bold than in the mockup:
   match cap height or width?
9. Requires row with 3–5 inputs: wrap, shrink, or scroll.

## Deviations from reference

- Small caps are faked with RichText size tags (Roblox has no small-caps feature).
- No letter-spacing control in Roblox: the subtitle's generous spacing is approximated by
  the font's own width.
