# Play window UI spec

Reference: `art/reference/ui/lobby/05_play.png`; kit sheets in `art/reference/ui/lobby/kit/`
(index: `art/reference/ui/lobby/README.md`).
Design resolution: 1672 × 941. Status: Draft (measured; open questions at the end).
Source of truth for build: the reference. Raw measurements and crops:
`art/ui/kit/analysis/play/` (scripts shared from `art/ui/kit/analysis/lobby/tools/`).

## Overview

Modal window opened by the HUD's Play tile (`docs/ui/LobbyScreen.md`). It shows
the destination region (illustrated map with an X marker, region name plaque,
four detail rows), the player's party, the player's equipped hotbar, and a large
PLAY button. It closes with the X button (and Esc / gamepad B). The lobby HUD
stays visible underneath a full-screen dim overlay. **Deviation from the old UI:
there is no server picker** (owner decision; the mockup has none either).

Typography: Merriweather Bold everywhere (conclusion and evidence in
`docs/ui/LobbyScreen.md` → Typography). TextSize = Merriweather Bold em size whose
rendered ink height matches the measured ink height, ±1.

## Tokens

| Token | Value | Used by |
|---|---|---|
| Overlay | #000000, BackgroundTransparency 0.29 | full-screen dim behind the window (measured alpha 0.706 here, 0.715 in the Party mockup) |
| Color.WindowParchment | #FDD7A0 (lower left) … #FEDEAD (right column) | window fill (part of the frame image) |
| Color.FrameRim | #994A14 | wood rim between the two dark outlines |
| Color.TitleInk | fill #371601, edge #110200 | "PLAY" and region title |
| Color.Ink | #150300–#1B0801 | labels, values, headings, names |
| Color.PlaqueParchment | #FDD49E (title), #FAC686 (region) | plaques |
| Color.RuleDetail | #F5CE9E (1 px) | rules between detail rows |
| Color.RuleSection | #E9B17D (1–2 px) | rule above "YOUR PARTY" |
| Color.RowFill / RowBorder | #FEE1B2 / #E1A76B | party row box |
| Color.Badge | #562006–#652808 | slot number badges |
| Color.Leather | top #C4441A → bottom #AE3511 | PLAY button |
| Color.CloseLeather | #B33D12 | close button |
| Color.Cream | #F8E5CA (glyph), #FDF0D0 (text, edge #5D0900) | PLAY glyph/text, close X |
| Color.IconInk | #3B1402 | detail row glyph icons |
| Font.Serif | Merriweather Bold | all text |

## Element tree

Bounds: design px `x, y, w, h` from the canvas top-left. ±1–2 px unless noted.
Z-order from bottom: HUD → Overlay → Window frame → window children in the order
listed (the title plaque draws over the map's top edge; the close button draws
over the frame's top-right bracket).

| Element | Parent | Bounds | Anchor intent | Appearance | Content / data | Kit part |
|---|---|---|---|---|---|---|
| Overlay | ScreenGui | 0,0,1672,941 | full screen | Overlay token; blocks input to the HUD | — | native |
| Window | Overlay | 309,127,1053,665 | centre: AnchorPoint 0.5,0.5 at (0.5, 0.5) with offset (−1, −11); window centre is 835,459.5 | parchment fill, outer dark outline 2 px, 3 px wood rim #994A14, inner dark outline 1 px; L-shaped leather corner brackets with rope ties at all four corners (≈50 × 50, overhang ≈2–3 px); torn/dashed inner edge | — | 15 play window frame (46,51,907,663) for the corner style; 04 window A (47,43,1083,426) for a plain 9-slice body; 14 corner pieces (95,49,101,92 etc.) |
| CloseButton | Window | 1294,136,54,52 | window top-right; inset 14 px from the right edge, 9 px from the top edge | red-orange leather square #B33D12, dark outline 2 px, 4 rivets, rounded ≈4 | closes the window | 03 close button normal (341,328,142,137); hover (537,329), pressed (734,329), disabled (932,329) |
| CloseButton.X | CloseButton | fill 1309,150,23,23 (≈27 with outline) | centred | cream X #F8F1D9 with dark outline | — | part of the 03 button |
| TitlePlaque | Window | 356,157,276,87 | window top-left | parchment plaque #FDD49E, torn edges, dark outline 2 px, 3 px darker bottom edge, rivets in the corners | — | 02 parchment plaque (371,544,255,70); 14 parchment plaque (68,852,290,102) |
| TitlePlaque.Text | TitlePlaque | ink 400,175,183,49 | centred in plaque (text centre x 491.5, plaque centre 494) | Serif Bold **64**, TextColor #371601, UIStroke 1.5 px #110200 | "PLAY" | native |
| Map | Window | 350,219,520,542 | window left column | torn parchment sheet (edges vary ±3 px) with a thin dark edge, painted island map inside | region map image (per region) | 15 plain map (1157,663,336,324) and the map inside the 15 play window are different paintings; the volcanic island here is new art |
| Map.Rune | Map | 385,281,41,69 | map top-left | dark brown rune #391303 painted on the map | decorative | 14 rune emblem (1384,653,103,186); part of the map art in the mockup |
| Map.Marker | Map | 649,412,23,23 (centre 660,423) | on the region's location | red X #ED4105 with dark outline | marks the selected region | 13 cross (1438,812) is a different red X; draw with the map or as a small image |
| RegionPlaque | Window | 894,223,423,70 | right column top | parchment plaque #FAC686, thin brown outline (L≈100–150, lighter than the window outline), rivets in corners | — | 02 parchment plaque (371,544,255,70) stretched; 03 notched parchment plaque (541,652,442,123) is close but notched |
| RegionPlaque.Text | RegionPlaque | ink 920,238,364,37 | centred (text centre x 1102, plaque centre 1105.5) | Serif Bold **45**, TextColor #2D1305, UIStroke 1 px #120101 | region display name ("Shattered Crater") | native |
| Details | Window | 905,300,410,160 | right column | 4 rows, label column x 967, value column x 1139–1142 | — | native |
| Details.Row[i] | Details | rows centred at y ≈ 318, 357, 396, 435 (pitch ≈39) | — | icon + label + value | see below | native |
| Details.Row.Icon | Row | 908,306,34,27 / 910,344,30,28 / 910,383,31,27 / 909,421,32,29 | left column, centre x ≈ 925 | flat dark-brown glyphs #3B1402: volcano (snow-capped peak), palm tree, crossed hammer and pick, treasure chest (the chest is painted brown/orange, not flat) | — | no flat glyphs in the kit. Closest coloured: 17 mountain (42,87,252,205), 17 tree (312,58,219,238), 11 hammer (605,591,227,225), 17 chest (562,608,282,194) / 11 chest (307,607,260,201) |
| Details.Row.Label | Row | ink x 967; caps at y 313, 352, 390, 429 | left aligned | Serif Bold 15–16, Color.Ink | "Region", "Biome", "Difficulty", "Recommended" | native |
| Details.Row.Value | Row | ink x 1139–1142 | left aligned | Serif Bold 15–16, Color.Ink | region name, biome, difficulty, "Level n+" | native |
| Details.Rule (×3) | Details | x 957..1311, y 338, 377, 417; 1 px (slight 1 px slope over the width) | — | Color.RuleDetail | — | native |
| SectionRule | Window | 897,466,419,2 | right column | Color.RuleSection | — | native |
| PartyHeading | Window | ink 899,481,139,15 | left aligned x 899 | Serif Bold 20, Color.Ink; mockup spacing is ≈9 % wider than Merriweather | "YOUR PARTY" | native |
| PartyRow | Window | 896,507,421,56 | right column | fill #FEE1B2, 1–2 px border #E1A76B, corner radius ≈6 | one row per member (see open q. 1) | 15 party rows inside the play window (≈605..918 × 170..475, rounded light boxes) |
| PartyRow.Crown | PartyRow | 913,525,23,19 (fill 915,527,19,15) | row left | gold crown #FCC60D | leader only | 06 crown (945,721,193,160) / 15 crown (839,781,79,67) |
| PartyRow.Headshot | PartyRow | 949,510,50,49 | — | headshot on grey-beige backdrop, 1 px light frame, radius ≈3 | member thumbnail | native ImageLabel |
| PartyRow.Name | PartyRow | ink 1017,528,92,13 | left | Serif Bold 16, Color.Ink | DisplayName | native |
| PartyRow.Level | PartyRow | ink 1258,529,39,12; right edge x 1297 (19 px inside the row) | right aligned | Serif Bold 15, Color.Ink | "LV. 12" | native |
| EquipmentHeading | Window | ink 898,578,196,18 | left aligned x 898 | Serif Bold 20 (render match 19), Color.Ink; spacing ≈9 % wider | "YOUR EQUIPMENT" | native |
| EquipSlot[i] (×6) | Window | x 887, 962, 1037, 1112, 1185, 1259 (pitch ≈74.4), y 606, w 69–72 (use 71), h 77 | right column | parchment #FDD8AA, 2 px dark outline, rounded ≈5, rivets in the corners, 2–3 px darker bottom edge | — | 05 numbered slots (77,499,237,234 …), 15 play window hotbar (≈125..855 × 495..605), 02 numbered hotbar (25,749,120,126 …) |
| EquipSlot.Badge | EquipSlot | slot x+3, y+3, 19 × 18 | slot top-left | leather badge #562006, rounded ≈3 | — | 05 badges (87,363,100,98 …) |
| EquipSlot.Number | Badge | numeral cap 10–11 | centred | Serif Bold 14, #F2E2C8 | "1"…"6" | native |
| EquipSlot.Item | EquipSlot | ≈ slot x+10, 617, 54, 60 | diagonal, lower-left to upper-right | item icon | equipped item (mock: stone axe, spear, plant-fibre bundle, empty ×3) | 02 item tiles / 16 icons (as HUD hotbar) |
| PlayButton | Window | body 895,696,416,72; with rope knots 889..1323 × ≈705..760 | right column bottom | leather, vertical gradient #C4441A → #AE3511, dashed light stitching inset ≈5 px, rivets, dark outline 2 px, rope knot ties on both short ends | starts the run (see Data) | 03 PLAY button (43,812,362,124) and the 15 play window button (≈283..703 × 615..695); the knots are from 14 rope knots (391,250,93,106) |
| PlayButton.Glyph | PlayButton | 1028,715,29,35 | left of the text, 26 px gap | cream triangle #F8E5CA with dark outline, slightly rounded | — | part of the 03 PLAY button |
| PlayButton.Text | PlayButton | ink 1082,717,109,30 | text+glyph group centred on the button (group 1028..1191, centre 1109.5; button centre 1103) | Serif Bold **40**, TextColor #FDF0D0, UIStroke 1 px #5D0900 | "PLAY" | native |

Right-column grid: content x 894–1328; vertical rhythm plaque 223 → details 300 →
rule 466 → heading 481 → row 507 → heading 578 → slots 606 → button 696.

## Measurements log

Scripts: `art/ui/kit/analysis/play/measure_play.py` → `measure_log.txt`
(uses `art/ui/kit/analysis/lobby/tools/`).

- Window frame: luminance rows 300/450/600 and cols 500/800/1100. Left: outline
  309–310 (L 10–21), rim 311–313, inner outline 314, paper 315. Right: inner
  1355–1356, rim 1357–1359, outline 1360–1361. Top: 127–128 / 129–131 / 132.
  Bottom: 786–787 / 788–789 / 790–791. → 309..1361 × 127..791.
- Window paper component (parchment class) 315..1358 × 130..788.
- Close button: row 162 outline at 1294–1295 and 1345–1347; col 1320 top 136–137,
  bottom 185–186. Leather-only component 1296,137,49,48. X: largest L>200
  component 1309,150,23,23.
- Title plaque: row 200 outline 356–357 / 630–631; col 490 top 157, bottom
  241–243 (incl. 2 px shadow).
- Region plaque: row 260 edges 895–896 / 1315; col 1100 top 223–224, bottom 291–292.
- Map: row 500 edge 351–352 / 867–868; cols 680/750/820 top 220–222;
  cols 420/600 bottom 756–759.
- Dividers: rows darker than the rows ±3 px by >8 L: 338, 377, 417 (x 957..1311)
  and 466 (x 897..1315).
- Party row: row 540 border 896–897 / 1315–1316; col 1150 507–508 / 561–562.
- Slots: `outer()` from paper components → L 887/962/1037/1112/1185/1259,
  R 958/1032/1107/1180/1254/1327, T 606, B 682.
- PLAY button: row 732 → outline 889–891 (knot), body edge 898; right body 1309,
  knot to 1323; rows 715/750 → body edge 895–896; col 1100 → 696–697 / 766–767.
- Text (`tsize_run.run`, ink at the paper/ink midpoint): "PLAY" title 183×49 →
  65 (cap 47); "Shattered Crater" 364×37 → 44.5; detail labels/values 12–13 px →
  14.5–16; "YOUR PARTY" 139×15 → 19.5; "LiamTheMo" 92×13 → 16; "LV. 12" 39×12 →
  15–16; "YOUR EQUIPMENT" 196×18 → 19; button "PLAY" 109×30 → 40.
- Title ink: row 200 through "P": edge #110200, interior #371601; row 262 through "S" of the region title: edge #120101, interior #2D1305; row 732 through the button "P": edge #5D0900, interior #FDF0D0.
- Colours: median boxes listed at the end of `measure_log.txt`.
- Overlay: `art/ui/kit/analysis/lobby/dim_overlay_log.txt` (alpha 0.706,
  colour ≈ black).

## States

| Element | Default | Hover | Pressed | Disabled | Other | Source |
|---|---|---|---|---|---|---|
| CloseButton | 03 normal | 03 hover (gold rim) | 03 pressed (darker) | — | — | kit 03 row 3 |
| PlayButton | as reference | 03 leather hover (brighter, gold rim) | 03 leather pressed (darker) | 03 leather disabled (desaturated tan) | "Starting…" / countdown while teleporting (open q. 3) | kit 03 rows 1, 6 |
| EquipSlot | as reference | 05 hover | — | — | empty slot shows the badge only | kit 05 |
| PartyRow | as reference | — | — | — | — | — |
| Map / marker | static | — | — | — | marker pulse not in reference | — |

## Data and behavior

| Element | Shows / does | Data source | Server validation |
|---|---|---|---|
| Map, marker, RegionPlaque, Details | the destination region: name, biome, difficulty, recommended level, map image, marker position | region config (shared module) | — |
| PartyRow(s) | party members, leader crown, level | party replica | — |
| EquipSlot ×6 | the player's hotbar loadout, slots 1–6 | equipment replica | — |
| PlayButton | requests start of the run for the party | remote to the matchmaking/teleport service | server checks the leader and party state, and teleports (no Ready step, D24) |
| CloseButton | closes the window | client | — |

There is no server picker (owner decision).

## Open questions

1. Party list with up to 8 members. The mockup has room for one 56 px row.
   Options: (a) the row area becomes a scroll region one row tall; (b) compact row
   of up to 8 headshots with the leader crown; (c) the section grows and pushes
   "YOUR EQUIPMENT" down. Default: (a).
2. Who can press PLAY, and when? **Resolved (D24):** a solo player or the party
   leader, at any time; other members see PLAY disabled with "The party leader
   starts the run." There is no Ready step and no ready line in the deploy check.
3. Feedback after PLAY: text change, spinner, or close the window. Default: button
   goes to the disabled look with "STARTING…" until teleport.
4. Is the map interactive (several regions to pick)? The mockup shows one region
   and no picker. Default: one region, map is decorative.
5. Detail icons are flat glyphs (volcano, palm, tools) and one painted chest; the
   kit has only painted versions. Options: new flat glyph images, or the coloured
   kit icons at ≈30 px. Default: coloured kit icons until glyphs exist.
6. Clicking an equipment slot: nothing, or open Inventory? Default: nothing.

## Deviations from reference

- **Owner decision D25 (window chrome):** the window uses the Inventory
  window's size (1187 × 650) and chrome instead of mockup 05's plaque style:
  the portal icon, "PLAY" at Inventory's title size and position, the plain
  ink underline, Inventory's clasps and close-button corner, and no raised
  title plaque. The map sits in an inset panel (Inventory's detail-card
  style) with the real island art and crater marker. The right column opens
  with a "SHATTERED CRATER" section heading over a hairline (no plaque), then
  the detail rows with hairlines, YOUR PARTY and YOUR EQUIPMENT as standard
  section headers, the six slots and the primary leather PLAY button with the
  play glyph at the bottom right. The element tree above records the mockup.
- Owner decision: no server picker (the old lobby had one; the mockup has none).
- Owner decision: the HUD's Play tile opens this window.
- In the mockup the HUD hotbar and XP bar under the overlay sit 29–33 px lower than
  in the HUD mockup; keep them where `LobbyScreen.md` puts them.
- The world behind the overlay is a darker, bluer, softened render in the mockup;
  the overlay alone will not reproduce it (LobbyScreen open question 1).
- Headings "YOUR PARTY" / "YOUR EQUIPMENT" are ≈9 % wider than Merriweather Bold at
  the same height (wider tracking); Roblox text has no tracking control, so they
  render slightly narrower.

## Fix round 3

- **Map** (V14): the painting sits on the paper sheet with a 17 px margin; the
  rune is drawn in ink so it reads on the sea. The painting itself is the
  game's island art (D19), not the mockup's.
- **Messages** sit on a paper plaque over the map's bottom edge (two lines when
  needed), clear of the window frame.
- **Loadout slots** are selectable: a gamepad reaches them (PLAY up → slots →
  ✕) and the tooltip names the item and its count (R20). Their 1–6 badges show
  only with a mouse or keyboard.
- **Ready** was removed (D24): members no longer get a Ready button; a refusal
  of PLAY shows under the map only (no second toast, M1).
- **Phones**: "+n more in your backpack" at 16; detail values start further
  left so "10 · Low to Extreme" keeps 9 screen px.
- Party rows are taken apart through maids (Kit components included, L10).
