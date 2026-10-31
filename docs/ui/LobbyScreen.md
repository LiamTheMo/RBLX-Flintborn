# Lobby HUD UI spec

Reference: `art/reference/ui/lobby/01_hud.png` (layout and sizes), kit sheets in
`art/reference/ui/lobby/kit/` (the parts to slice; index in `art/reference/ui/lobby/README.md`).
Design resolution: 1672 × 941 (the reference image size).
Status: Draft (measured; open questions at the end).
Source of truth for build: the reference. Raw measurements, scripts and crops:
`art/ui/kit/analysis/lobby/`.

This file replaces the earlier lobby spec, which described the old parchment
sheets and an Enter button with a server dropdown. Neither exists in the new UI.

## Overview

The lobby place's always-on, non-modal HUD. Top left: the player card (portrait,
name, level, XP bar, leaf emblem). Top right: Coins pill, Gems pill, settings
button. Left: a 2 × 3 grid of square menu tiles (icons only, no labels). Right:
the Party panel (title with count, member rows, empty-slot rows, scrollbar).
Bottom centre: the level/XP bar and the six-slot hotbar.

Menu tiles open full-screen modal windows (Inventory, Play, Quests, Shop, Forge,
Trade). The Play tile opens the Play window (`docs/ui/PlayScreen.md`); the Party
panel's add-friend button opens the Party window (`docs/ui/PartyScreen.md`, see
open question 3). While a modal window is open, the HUD stays visible under a
dim overlay (see "Modal dim overlay" below).

## Tokens

Colours are medians of flat boxes (`med()` / `ref_tools.py sample --boxes`),
±3 per channel from texture noise. Box coordinates are in the Measurements log.

| Token | Value | Used by |
|---|---|---|
| Color.Parchment | #FAD2A5 | Card plate, pills, party panel (fallback fill under the kit images) |
| Color.ParchmentLight | #FCD4A0 / #FCDAAD | Hotbar slot / menu tile centre |
| Color.Ink | #170300 (core), reads as #1C0801 | All dark HUD text |
| Color.Outline | #312515 | Dark outer edge of pills, slots, tiles (part of the kit image) |
| Color.XpFill | top #FFDE43 → body #F9A901 → bottom #C98609 | Card XP bar and bottom XP bar fill |
| Color.XpTrack | #5D2F0D (card) / #59290B (bottom bar) | Empty part of both XP bars |
| Color.XpBarOutline | #644A30 (1 px) then #2F0A00 (1 px) | Bottom XP bar frame (part of the kit image) |
| Color.PhotoBackdrop | #C9B19B (card), #CAB6A4 (party) | Grey-beige backdrop behind headshots |
| Color.RuleSoft | #DFB48C | Party panel row rules |
| Color.RuleTitle | #E5BB90 | Party panel title rule |
| Color.SlotDot | #CC9F77 | Empty party slot dots |
| Color.ScrollThumb / ScrollTrack | #A0704D / #E1BB90 | Party panel scrollbar |
| Color.Badge | #652808 (fill), numeral #F2E2C8 | Hotbar number badges |
| Font.Serif | Merriweather, Bold (`Font.fromName("Merriweather", Enum.FontWeight.Bold)`) | Every HUD text (see Typography) |

## Typography

Font conclusion (applies to the Play and Party windows too): **Merriweather Bold
is confirmed** as the closest Roblox family. Evidence (crops in
`art/ui/kit/analysis/lobby/font/`):
- Rendered Merriweather Bold at the matched ink height reproduces the reference
  string widths within ±5 % for most strings ("LiamTheMo" 115 vs 116 px,
  "Shattered Crater" 362 vs 364 px, "Empty Slot" 76 vs 77 px, "CLOSE" 81 vs 81 px).
- Letter shapes match: double-storey a and g, ball terminals on r and a, wedge
  serifs, large x-height (measured x/cap 0.73 vs Merriweather 0.75).
- Weight: the reference ink mass is 1.1–1.2× Merriweather Bold and 1.4–1.6×
  Regular, so Bold, not Regular, for every string (the extra mass is the
  reference's soft edge, not a heavier face).
- Regular is not used anywhere in the HUD.

TextSize rule: TextSize = the Merriweather Bold em size whose rendered ink
height equals the measured ink height of the same string (cap height ≈ 0.743 em,
so TextSize ≈ cap ÷ 0.743). Values below are rounded to whole px, ±1.

## Element tree

Bounds are design px `x, y, w, h` from the top-left of the 1672 × 941 canvas,
measured from parchment-class components, luminance scanlines and ink boxes
(±1–2 px unless noted). "Outer" bounds include the dark outline of the kit art.
Z-order: listed parents draw under their children; HUD regions do not overlap.

### Top-left: player card (anchor: top-left)

**Removed from the game HUD** (owner decision): the lobby HUD draws no player
card. Each party member's row in the Party panel shows their level and a small
XP bar instead. The table below records the mockup only.

| Element | Parent | Bounds | Appearance | Content / data | Kit part |
|---|---|---|---|---|---|
| PlayerCard | HUD | 39,60,359,81 | union of portrait frame and name plate | — | 07 player card (95,33,771,178): portrait frame + plate in one image. Kit is 0.466× scale of the mockup, same proportions (771×178 → 359×83) |
| PlayerCard.PortraitFrame | PlayerCard | 39,60,87,81 | light carved-wood frame with gold corner flourishes, 2 px dark outline | — | 07 card, left part (≈95..280 × 33..211); 01 portrait plaque (521,890,408,88) is an alternative |
| PlayerCard.Photo | PortraitFrame | 49,69,67,63 | headshot on #C9B19B backdrop, square corners, sits inside the frame window | `Players:GetUserThumbnailAsync(HeadShot)` of the local player | native ImageLabel |
| PlayerCard.Plate | PlayerCard | 130,62,268,76 | parchment plate, torn top/bottom edges, dark outline 3–4 px, rivet dots in right corners; a 3–4 px gap shows the world between frame and plate | — | 07 card, right part (≈280..866) |
| PlayerCard.Name | Plate | ink 148,81,116,16 | Serif Bold 19, Color.Ink, left aligned, cap top y 82, baseline y 96 | DisplayName ("LiamTheMo") | native |
| PlayerCard.Level | Plate | ink 148,108,41,12 | Serif Bold 16, Color.Ink, left | "LV. 12" (level) | native |
| PlayerCard.XpBar | Plate | 198,109,161,12 | track #5D2F0D, 1 px dark outline, fully rounded ends (radius 6) | XP into level ÷ XP for level | 05 XP fill and track (198,779,891,58) / (198,845,891,59), 9-sliced |
| PlayerCard.XpFill | XpBar | 199,110,119,10 at the mock value | Color.XpFill gradient (vertical, highlight in the top 3 px) | width = fraction (mock shows 0.74; 450/750 would be 0.60) | 05 XP fill |
| PlayerCard.Leaf | Plate | 363,78,16,44 | dark brown leaf-on-stem emblem #2E0A00 | decorative | 14 leaf emblem (1259,621,76,202) |

### Top-right: currencies and settings (anchor: top-right)

| Element | Parent | Bounds | Appearance | Content / data | Kit part |
|---|---|---|---|---|---|
| Coins | HUD | 1317,70,116,46 | parchment pill #FAD6B0, 2 px dark outline, 3 px darker bottom edge, rivet dots in corners | — | 07 coins (915,85,245,105) |
| Coins.Icon | Coins | 1329,77,30,31 | gold coin with dark outline | — | 06 coin (171,706,204,200); 02 coin button (595,645,73,70) is the framed version |
| Coins.Value | Coins | ink 1368,86,46,16 | Serif Bold 18, Color.Ink, left aligned at x 1368, vertically centred | Coins, thousands separator ("2,450") | native |
| Gems | HUD | 1450,70,101,46 | as Coins | — | 07 gems (1189,81,240,108) |
| Gems.Icon | Gems | 1464,78,23,30 | blue hexagonal gem | — | 06 gem (605,700,159,215) |
| Gems.Value | Gems | ink 1501,86,27,14 | Serif Bold 18, Color.Ink; centred in the space right of the icon (x 1487..1546) | Gems ("125") | native |
| Settings | HUD | 1567,70,52,46 | square parchment button, same frame as the pills | opens Settings window | 07 settings (1458,82,118,108); 02 gear button (784,642,78,70) |
| Settings.Glyph | Settings | 1579,80,26,25 | dark brown gear #2E1004 | — | part of the 07 button; 06 gear (907,411,286,280) is a grey 3-D gear, not the flat glyph |

Gaps: Coins → Gems 17 px, Gems → Settings 16 px; right margin 53 px; top margin 70 px.

### Left: menu grid (anchor: left, vertically centred group)

Tiles are 88 × 84 (±1), columns at x 68 and 170 (pitch 102, gap 14), rows at
y 312, 406, 500 (pitch 94, gap 10). Group bounds 68,312,190,273; group centre
y 448.5 (screen centre 470.5).

| Element | Bounds | Icon (approx. bounds, ±4) | Opens | Kit part (tile / icon) |
|---|---|---|---|---|
| Tile.Inventory | 68,312,88,84 | backpack 84,326,55,61 | Inventory window | 07 tile (771,239,203,196) / 06 backpack (47,41,339,342) |
| Tile.Play | 170,312,88,84 | stone portal with orange play triangle 182,322,64,68 | Play window | 07 tile (1011,239,205,196) / 06 portal (438,48,405,324) |
| Tile.Quests | 68,406,88,84 | rolled scroll 80,420,61,58 | Quest Journal | 07 tile (1253,239,204,196) / 06 scroll (872,70,333,295) |
| Tile.Shop | 170,406,88,84 | striped market stall 182,420,64,59 | Shop | 07 tile (771,462,203,188) / 06 market (1276,59,345,304) |
| Tile.Forge | 68,500,88,84 | anvil and hammer 77,512,68,62 | Forge | 07 tile (1009,462,205,189) / 06 anvil (62,399,340,296) |
| Tile.Trade | 170,500,88,84 | hands passing a pouch 179,516,71,53 | Trade | 07 tile (1253,462,204,189) / 06 trade (487,409,370,264) |

Tile frame: parchment #FCDAAD centre fading to #F9C783 near the rim, gold corner
flourishes, 2 px dark outline (#1x0x0x, L ≈ 20). No text labels.
Kit difference: kit 07 lays the tiles out 3 × 2; the mockup is 2 × 3 (Inventory,
Play / Quests, Shop / Forge, Trade). The kit 07 tile includes its icon; to reuse
one frame for all six, slice an empty frame from 01 slot frames
(28..880 × 763..862) or 05 slot normal (64,45,271,260) and layer the 06 icon.

### Right: Party panel (anchor: right, top-aligned at y 258)

| Element | Parent | Bounds | Appearance | Content / data | Kit part |
|---|---|---|---|---|---|
| PartyPanel | HUD | 1325,258,294,244 | parchment #F8D5AD, double dark outline (outer 1–2 px, 2–3 px wood rim, inner 2 px), leather corner brackets top-left/top-right (protrude ≈2 px), small leather tabs on the right edge (y ≈ 300) and bottom edge (x ≈ 1380) | — | 07 party panel (153,235,549,428). The mockup panel is ≈15 px taller than the kit at the same width (kit aspect 1.28, mockup 1.20): 9-slice it |
| PartyPanel.Title | PartyPanel | ink 1357,287,66,15 | Serif Bold 20, Color.Ink | "PARTY" | native |
| PartyPanel.Count | PartyPanel | ink 1444,285,41,17 | Serif Bold 20, Color.Ink (digits cap 15 = title cap) | members / cap. **Deviation: "1/8"** (real cap 8), mockup shows "1/10" | native |
| PartyPanel.TitleRule | PartyPanel | 1354,311,235,2 | Color.RuleTitle | — | native Frame |
| MemberRow | PartyPanel | 1353,313,242,51 | no fill | one per member (cap 8) | native |
| MemberRow.Headshot | MemberRow | 1353,320,41,38 | headshot on #CAB6A4, 1 px light frame, radius ≈3 | member thumbnail | native |
| MemberRow.Name | MemberRow | ink 1410,334,79,10 | Serif Bold 13, Color.Ink, left | DisplayName | native |
| MemberRow.Crown | MemberRow | 1517,333,19,14 (fill 1519,335,15,10) | gold crown #FCB10A, dark outline | shown for the party leader only | 06 crown (945,721,193,160) / 15 crown (839,781,79,67); not 16 crown, which has a red gem |
| AddFriendButton | MemberRow | 1549,321,45,34 | parchment #F4C695, 2 px dark outline #170x0x, radius ≈4, glyph person-plus #1B0D08 ≈ 22×18 centred | opens invite (open question 3) | 15 invite button (955,764,124,100); 07 party panel's own button. Not 06 invite card (two people, different frame) |
| Rule (×4) | PartyPanel | x 1353..1576, y 364, 400, 435, 471; 1 px | Color.RuleSoft | row separators | native |
| EmptyRow (×n) | list | pitch ≈35.6 below y 364 | — | free slots up to the cap | native |
| EmptyRow.Dot | EmptyRow | 1358,377,13,13 / 1358,412,13,13 / 1358,448,13,13 | flat circle Color.SlotDot | — | native (UICorner 0.5); 09 list row dot is the same idea |
| Scrollbar.Track | PartyPanel | 1588,366,8,111 | Color.ScrollTrack, fully rounded | — | 09 scrollbar track (1520,461,47,266) is a framed version; mockup is flat |
| Scrollbar.Thumb | Track | 1588,366,8,63 at the mock position | Color.ScrollThumb, fully rounded | list scroll position | 09 thumb (1601,477,47,144) is leather; mockup is flat |

Member rows show no ready dot and no Leader tag: the crown alone marks the
leader (D24).

The list area (member row + empty rows) is a scroll region from y 313 to the
panel's inner bottom (≈ y 489): 1 member row (51 px) + 3 visible empty rows
(35–36 px each). With the cap at 8 there are 7 rows after the member row, so the
list scrolls.

### Bottom centre: XP bar and hotbar (anchor: bottom-centre)

| Element | Parent | Bounds | Appearance | Content / data | Kit part |
|---|---|---|---|---|---|
| XpBar.Level | HUD | ink 574,770,46,13 | Serif Bold 17, Color.Ink, right edge 7 px left of the bar | "LV. 12" | native (07 shows it on a small plaque at 305..380 × 697; the mockup has no plaque) |
| XpBar | HUD | 631,768,356,16 | 1 px #644A30 + 1 px #2F0A00 outline, track #59290B, fully rounded | XP fraction | 07 bar (400,691,786,29); 05 fill/track |
| XpBar.Fill | XpBar | 633,770,238,12 at the mock value | Color.XpFill gradient | fraction (mock 0.67; 450/750 = 0.60) | 05 XP fill |
| XpBar.Value | HUD | ink 998,770,96,13 | Serif Bold 17 (digit cap 12), Color.Ink, left 11 px right of the bar | "450/750 XP" (XP into level / XP for level) | native (07 shows a plaque behind it; mockup has none) |
| Hotbar | HUD | 550,799,571,93 | 6 slots, pitch 96.4 (x 550, 646, 743, 839, 936, 1032), gap ≈8 | — | 07 hotbar (254..1418 × 735..900) |
| Hotbar.Slot[i] | Hotbar | x_i,799,89,93 | parchment #FCD4A0, 2 px dark outline, rounded ≈5, 3 px darker bottom edge, rivet dots in corners | — | 07 slot (254,735,172,165); 05 numbered slot (77,499,237,234); 02 numbered hotbar (25,749,120,126) |
| Hotbar.Slot[i].Badge | Slot | x_i+4,803,22,21 | leather #652808 square, rounded ≈3, inset 4 px from the slot's top-left | — | 05 badges 1–6 (87,363,100,98 …); baked into 07 slots |
| Hotbar.Slot[i].Number | Badge | numeral cap 11 | Serif Bold 15, #F2E2C8 | "1"…"6" (key bind) | native |
| Hotbar.Slot[i].Item | Slot | ≈ x_i+12,811,66,74 | item icon, bottom-left to top-right diagonal | equipped item (mock: 1 stone axe, 2 spear, 3 plant-fibre bundle, 4–6 empty) | 02 item tiles axe (855,735,128,82), spear (992,735,117,82), plant fibre (992,824,117,90); 16 stone axe (1177,593,196,249), plant fibre (594,862,237,228) |

## Modal dim overlay (behind the Play and Party windows)

Measured by comparing the HUD parts in `04_party.png` and `05_play.png` with the
same parts in `01_hud.png` (11 flat patches: papers, inks, XP track/fill, gold,
gem blue; least-squares per channel, `dimfit.py`):

| Screen | Per-channel gain (R, G, B) | Offset | Overlay alpha | Overlay colour |
|---|---|---|---|---|
| 05_play | 0.316, 0.277, 0.289 | 1.8, 6.5, 4.7 | 0.706 | ≈ #030907 |
| 04_party | 0.296, 0.272, 0.287 | 0.4, 3.7, 3.3 | 0.715 | ≈ #010505 |

Spec: a full-screen Frame, BackgroundColor3 #000000, BackgroundTransparency
**0.29** (alpha 0.71), above the HUD and below the window. The offsets are within
JPEG-level noise, so the colour is black. Red is kept slightly more than green
and blue (gain 0.30 vs 0.28), a faint warm cast; ignore it or use #000000 at 0.29.

The HUD under the overlay is not blurred (edge-gradient ratio equals the dim
ratio: 0.25–0.30 for tiles and pills). The 3-D world behind it is a different,
darker and bluer, softened render (sky correlation drops to 0.70, texture ratio
0.03–0.10). See open question 1.

## Measurements log

Tools: `ref_tools.py` (skill scripts) for info/grid/crop/sample, plus the scripts
in `art/ui/kit/analysis/lobby/tools/` (`m.py`: scanline runs, luminance profiles,
ink boxes, flood fills, outward/inward edge marching; `comps.py`: alpha
components; `tsize.py`: Merriweather render matching). Full output in
`art/ui/kit/analysis/lobby/measure_log.txt`; rerun with
`python3 art/ui/kit/analysis/lobby/measure_lobby.py`.

- `ref_tools.py info 01_hud.png` → 1672 × 941 RGB, no alpha.
- `ref_tools.py grid --step 10 --major 5` and `crop --scale 3..5` for locating
  (crops saved as `*_4x.png`, `portrait_5x.png`, `party_panel_3x.png`).
- Parchment-class components (R>205, G>170, B>110, R−B>40):
  `parchment_components.txt`. Example: Coins paper 1319..1430 × 72..112.
- Outer bounds: `outer()` marches out from the paper box to the end of the dark
  run (L<110) on 3 scanlines per side; e.g. Coins L 1317, R 1432, T 70, B 115.
  Over busy background (card, tiles, party panel) edges were read from
  luminance profiles instead: portrait row 100 L=20–54 at x 37..41 → edge 39;
  plate col 300 dark run 62..65 and 134..137; party panel row 380 outline 1325 /
  1618, col 1450 258 / 501.
- Tiles: `box_from_inside()` (first L<75 pixel from inside) gives outlines at
  69/154 (x), 312/394, 406/488, 500/584 (y); outer = +1 px.
- Hotbar: `outer()` → L 550/646/743/839/936/1032, R +88, T 799, B 891.
- XP bars: `runs()` row 114 (card): outline 198, fill to 317, track to 358;
  row 776 (bottom): outline 631/632, fill to 870, track to 986; col 700: 768..783.
- Party panel internals: rule rows from "row darker than ±3 px rows" scans
  (y 311–312, 364, 399–401, 435–436, 470–471); dots by flood fill (13 × 13);
  add-friend button from row 338 (1549/1593) and col 1570 (321/354);
  scrollbar from col 1591 (thumb 366..428 L≈125, track 429..476 L≈193).
- Text: ink boxes at the midpoint threshold between paper and ink; TextSize from
  `tsize_run.run()` (render matching). Raw: "LiamTheMo" 116×16 → 19.0;
  "LV. 12" 41×12 → 16; "2,450" 46×16 → 17.5; "125" 27×14 → 17; "PARTY" 66×15 → 19.5;
  member name 79×10 → 12 (width suggests 13); bottom "LV. 12" 46×13 → 17;
  "450/750 XP" digits 12 px → 16–17 (the slash is shorter than Merriweather's).
- Colours: `med()` median boxes listed at the end of `measure_log.txt`, e.g.
  plate (300,92,40,6) #FAD2A5 std 2.0; bottom XP track (900,773,80,6) #59290B
  std 1.1.
- Dim overlay: `dimfit.py` → `dim_overlay_log.txt`; HUD offsets in the modal
  mockups: `hud_offsets.py` → `hud_offsets_log.txt`.

## States

| Element | Default | Hover | Pressed | Selected / active | Disabled | Source |
|---|---|---|---|---|---|---|
| Menu tile | as reference | warm glow rim like 05 slot hover (706,45,271,260) | darker, like 05 pressed parchment | — (modal open could keep it lit; open q. 6) | greyed like 05 disabled (1027,45,271,259), for locked features | kit 05 states; not shown in the mockup |
| Settings button | as reference | 05/03 parchment hover (gold rim) | 03 parchment pressed | — | — | kit 03 rows 2 / 6 |
| Add-friend button | as reference | 03 small parchment hover (804,816,222,114) | 03 pressed | — | hidden or disabled when party is full or player is not leader (open q. 4) | kit 03 |
| Hotbar slot | as reference | 05 hover (706,45,271,260) | — | equipped/active slot: 05 selected gold frame (375,44,283,263) | 05 disabled | kit 05; the mockup shows no selected slot |
| Party list | scrolls when rows exceed the visible 4 | — | — | — | — | scrollbar in the mockup |
| Gamepad focus | — | — | — | — | — | not in reference; use the hover look as focus |

## Data and behavior

| Element | Shows / does | Data source | Server validation |
|---|---|---|---|
| PlayerCard | local player headshot, DisplayName, level, XP fraction | player profile replica (level, xp, xpToNext) | read-only |
| Coins / Gems | balances with thousands separators | currency replica | read-only |
| Settings | opens Settings window | client | — |
| Menu tiles | open their windows; Play opens the Play window | client UI router | windows request data as needed |
| PartyPanel | party members (cap **8**), leader crown, "n/8" | party service replica | server owns membership and cap |
| AddFriendButton | opens invite flow | client | invites validated server-side |
| XP bar + text | level, XP / XP-to-next | profile replica | read-only |
| Hotbar | equipped tools per slot 1–6, key binds 1–6 | inventory/equipment replica | equip requests validated server-side |

## Asset map

| Asset | Source (sheet: x,y,w,h in sheet px) | Shown at (design px) | Notes |
|---|---|---|---|
| Player card | 07: 95,33,771,178 | 359 × 81 | portrait window must be cut out for the live headshot |
| Pill frame | 07: 915,85,245,105 (coins) | 116 × 46 / 101 × 46 | 9-slice; same frame for Gems |
| Square HUD button | 07: 1458,82,118,108 | 52 × 46 | settings |
| Menu tile frame | 07 tiles (771..1457 × 239..650) or 05 slot normal | 88 × 84 | icon layered on top if the frame is shared |
| Menu icons | 06: backpack, portal, scroll, market, anvil, trade | ≈ 55–71 px | also in 11 (row 1) |
| Party panel frame | 07: 153,235,549,428 | 294 × 244 | 9-slice (taller than kit) |
| Crown | 06: 945,721,193,160 | 19 × 14 | |
| Add-friend button | 15: 955,764,124,100 | 45 × 34 | |
| XP fill / track | 05: 198,779,891,58 / 198,845,891,59 | 161 × 12 and 356 × 16 | 9-slice horizontally |
| Hotbar slot + badge | 05: 77,499,237,234 (numbered) or 02: 25,749,120,126 | 89 × 93 | numbers can be native text over 05 blank badges |
| Item icons | 02 item tiles / 16 icons | ≈ 66 × 74 | |
| Leaf emblem | 14: 1259,621,76,202 | 16 × 44 | |

Kit sheets came from background removal: fills sit at alpha 250–254 and edges
carry a red/yellow fringe at alpha 1–63; clean both when slicing (README).
Component boxes for every sheet: `art/ui/kit/analysis/lobby/kit_components/`.

## Open questions

1. World behind modals. The mockups show a darker, bluer, softened world. Options:
   (a) overlay only, #000000 at 0.29 transparency (default);
   (b) overlay plus a Lighting BlurEffect while a modal is open;
   (c) overlay plus a ColorCorrection tint toward blue.
2. HUD position under modals. In `05_play.png` the XP bar and hotbar sit 29–33 px
   lower than in `01_hud.png`, in `04_party.png` 14–17 px lower; the card, pills
   and tiles do not move. Options: (a) HUD stays put, offsets are mockup drift
   (default); (b) slide the bottom bar down while a modal is open.
3. What opens the Party window: the add-friend button, a click on the panel, or
   both? Default: both; add-friend also focuses the search box.
4. Add-friend button for non-leaders and a full party: hide, or show disabled?
   Default: disabled (kit 03 disabled look).
5. Play tile icon. In `04`/`05` the dimmed Play tile shows a bare play triangle
   instead of the portal. Default: keep the portal from `01` (one icon).
6. Should the tile of the open window stay highlighted? Default: no.
7. XP fills in the mockup (0.74 card, 0.67 bar) do not match 450/750 (0.60).
   Default: both bars use the real fraction.

## Deviations from reference

- Owner decision: party count shows the real cap, **"1/8"**, not "1/10".
- Owner decision: the Play tile opens the Play window.
- Hotbar and XP bar keep their `01_hud.png` positions under modals (q. 2 default).
- The mockup's text has a soft dark halo from the image generator; TextLabels have
  none. No UIStroke on HUD text.
- Merriweather has no letter-spacing control; where the mockup is tighter or looser
  (±5–10 %), keep the font's default spacing.

## Fix round 3

- **Phones and touch tablets** (`Kit.Scale.IsSmallTouch`, re-applied on
  `Kit.Scale.OnFormFactorChanged`): party names draw at 15 (9 screen px at the
  0.5 HUD floor) at one size for every row (`shrinkName = false`; a long name
  ends in "…", so the leader's name no longer shrinks below the others, V13),
  rows take the panel's width and the add-player button moves into the title
  row beside the count; the Coins and Gems pills widen (150 / 124) for long
  values; the game-update plaque grows to 72 px and wraps onto two lines.
- **Invites on touch** (R7): one "Respond" button (touch-sized) opens the Party
  window's invitations instead of the 34 px ✓ / ✕ pair whose 44 px pads
  overlapped. Desktop keeps ✓ / ✕; both disable while the answer is on its way
  (`PartyController.AnswerBusy`).
- **Card level**: the label widens to its text and the card's XP bar starts
  after it; at the level cap the card reads the level number (the XP line says
  "Max level").
- **Hotbar badges** 1–6 show only while a mouse or keyboard is the input
  (`Kit.Input.Watch`); touch and gamepad have no number keys.
- **Gamepad** (R6): `Kit.Input.SetHudDefault(<Inventory tile>)` registers the
  HUD's entry point; the HUD never takes selection at build or spawn.
- **One feedback per refusal** (M1, M2): answers go through
  `PartyController.Answer`; while PartyController reports a request
  (`Reporting()`) the HUD does not toast LobbyController's "Party: …" status.
- A failed start disconnects everything it connected and destroys the HUD
  before falling back (L9).
