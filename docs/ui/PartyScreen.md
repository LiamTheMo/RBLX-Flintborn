# Party window UI spec

Reference: `art/reference/ui/lobby/04_party.png`; kit sheets in `art/reference/ui/lobby/kit/`
(index: `art/reference/ui/lobby/README.md`).
Design resolution: 1672 × 941. Status: Draft (measured; open questions at the end).
Source of truth for build: the reference, changed by the owner decisions marked
**Deviation**. Raw measurements and crops: `art/ui/kit/analysis/party/`
(scripts shared from `art/ui/kit/analysis/lobby/tools/`).

## Overview

Modal window for managing the party, opened from the HUD Party panel
(`docs/ui/LobbyScreen.md`, open question 3). Header with a camp emblem and
"PARTY". Three columns: **Your Party** (leader row and empty slots), **Invite
Players** (search box and a list of players with Invite buttons), and on the right
**Party Details** (key/value rows; the mockup's Readied Status card under it is
removed, D24). A leather CLOSE button sits under the columns and an X button in the top
right. The HUD stays visible under the full-screen dim overlay (#000000 at
BackgroundTransparency 0.29; measured alpha 0.715 in this mockup, see LobbyScreen).

Owner decisions (deviations from the reference):
- Party cap is **8**: "1/8" in the Your Party header and "1 / 8" in Members (mockup "1/10").
- Party Details has **no "Play Style" row**.
- Join Type shows **"Invite Only"** (as in the mockup; it is now the only value).
- **No Ready and no Leader tag (D24).** The Readied Status card, its Ready / Not
  Ready toggle and the "k of n ready" tally are removed; Party Details takes the
  whole right column (top y 245, bottom y 693; the space under its rows stays
  empty). Member rows carry no Ready / Not Ready tags, and the leader is marked
  only by the crown beside the name.

Typography: Merriweather Bold for all text (evidence in `LobbyScreen.md` →
Typography). TextSize = Merriweather Bold em size whose rendered ink height
matches the measured ink height, ±1.

## Tokens

| Token | Value | Used by |
|---|---|---|
| Overlay | #000000, BackgroundTransparency 0.29 | dim behind the window |
| Color.WindowParchment | #FDDDB0 | window fill (frame image) |
| Color.TitleInk | fill #4A250C, edge #2A0B02 | "PARTY" |
| Color.EmblemInk | #582908 (tent), trees #A16C40 (left) / #844D23 (right), ground line #703814 | header art |
| Color.HeadingInk | #2E0700–#320A00 | column headings and "1/8" |
| Color.Ink | #000000–#0A0703 | names, detail values |
| Color.InkSoft | #3D2813–#5A4027 | "LV. n" under names |
| Color.LabelInk | #764422 | detail labels |
| Color.EmptyInk | #A88363 | "Empty Slot" |
| Color.PanelFill | #FEE5C1 | sub-panel fill (barely lighter than the window) |
| Color.PanelStroke | #ECB782, 2 px | sub-panel border |
| Radius.Panel | 8 px | sub-panels |
| Color.HeadingRule | top px #643B17–#765030, bottom px #BB936E–#C29F7D (2 px total) | rule under each column heading |
| Color.RowRule | #EFC79D (1 px) | row separators |
| Color.SlotDot | #DEB791 | empty-slot circles |
| Color.SearchFill / SearchStroke | #FEE7C6 / #84613F | search box |
| Color.PlaceholderInk | #825F44 | "Search players..." |
| Color.LeaderPill | fill #FBD08B, stroke #7E5221 | "Leader" pill |
| Color.ReadyPill | fill #E8EAA2, stroke #275B13, dot #07E71A | "Ready" pill |
| Color.IconDisc | #461D04 | info and check discs |
| Color.LeatherInvite | #9F3813 | Invite buttons |
| Color.LeatherClose | #90310F | CLOSE button |
| Color.CloseX | #B14311 | X button leather |
| Color.Cream | #FEFBF2 (Invite text), #F9F9F9 (CLOSE text, edge #601F0A) | text on leather |

## Element tree

Bounds: design px `x, y, w, h` from the canvas top-left, ±1–2 px unless noted.
Z-order from bottom: HUD → Overlay → Window → header art and sub-panels → rows →
pills/buttons → X button.

### Frame and header

| Element | Parent | Bounds | Anchor intent | Appearance | Content / data | Kit part |
|---|---|---|---|---|---|---|
| Overlay | ScreenGui | 0,0,1672,941 | full screen | Overlay token; blocks HUD input | — | native |
| Window | Overlay | 274,143,1124,637 | centre: AnchorPoint 0.5,0.5 at (0.5,0.5), offset (0, −10); window centre 835.5,461 | parchment, outer dark outline 1–2 px, 3 px wood rim, inner dark outline 2 px (paper starts at x 280, y 149); leather corner brackets: TL ≈273,142,53,37, TR ≈1349,141,49,43, BL ≈271,746,42,36, BR ≈1361,746,41,36 (overhang ≈1–2 px); small leather side clasps on both short sides near y ≈688; the top edge rises slightly in the middle behind the header (≈x 600..1080) | — | 04 window A (47,43,1083,426) has the side clasps; 15 party window (979,60,516,548) for the bracket style |
| CloseX | Window | 1324,168,56,53 | top-right, inset 18 px from the right edge, 25 px from the top | red-orange leather #B14311, dark outline 2 px, 4 rivets, rounded ≈4 | closes | 03 close button normal (341,328,142,137) + hover/pressed/disabled to the right |
| CloseX.Glyph | CloseX | fill 1341,183,24,24 (≈28 with outline) | centred | cream X with dark outline | — | part of the 03 button |
| Header.Tent | Window | 697,177,42,42 | header group | flat dark-brown tent/crossed-poles glyph #582908 | decorative | not in the kit (new art) |
| Header.Title | Window | ink 767,180,153,36 | header group | Serif Bold **48**, TextColor #4A250C, UIStroke 1 px #2A0B02 | "PARTY" | native |
| Header.TreesLeft | Window | 639,184,46,43 | header group | two pine silhouettes, light brown #A16C40 | decorative | not in the kit (new art) |
| Header.TreesRight | Window | 947,173,71,55 | header group | three pine silhouettes, brown #844D23 | decorative | not in the kit (new art) |
| Header.Ground | Window | 481,226,781,8 | under the header group | hand-drawn tapered line #703814, 1 px at the ends, ≈5 px thick between x 560 and 1119, densest at y 229–231 | decorative | 14 dividers (60,476,787,19) are straight; new art or a stretched 14 divider |

Header group spans x 639..1017 (centre 828, 7.5 px left of the window centre);
title centre x 843.5.

### Column 1: Your Party (sub-panel)

| Element | Parent | Bounds | Appearance | Content / data | Kit part |
|---|---|---|---|---|---|
| YourPartyPanel | Window | 304,245,360,448 | Color.PanelFill, 2 px Color.PanelStroke, radius 8 | — | native (01 layout panels are full windows, not insets) |
| Heading.Icon | panel | 323,263,36,26 | three-people glyph #391101 | — | 11 party icon (572,354,267,203) is painted; flat glyph is new art |
| Heading.Text | panel | ink 374,269,136,16 | Serif Bold 21 (cap 15–16), Color.HeadingInk | "YOUR PARTY" | native |
| Heading.Count | panel | ink 536,268,44,18 (digits cap 15) | Serif Bold 21, Color.HeadingInk, 26 px right of the heading | **Deviation: "1/8"** (mockup "1/10") | native |
| Heading.Rule | panel | 320,297,329,2 | Color.HeadingRule | — | native (two 1 px frames) |
| LeaderRow | list | 320,299,328,77 (to the rule at y 376) | no fill | the leader (cap 8 members in all rows) | native |
| LeaderRow.Headshot | LeaderRow | 320,313,57,55 | headshot on #D3C1B1, 2 px dark outline, radius ≈4 | thumbnail | native |
| LeaderRow.Name | LeaderRow | ink 395,323,101,14 | Serif Bold 17, Color.Ink | DisplayName | native |
| LeaderRow.Level | LeaderRow | ink 396,347,39,11 | Serif Bold 15, Color.InkSoft | "LV. 12" | native |
| LeaderRow.Crown | LeaderRow | 538,333,23,17 (fill 540,335,19,13) | gold crown | leader only | 06 crown (945,721,193,160) / 15 crown (839,781,79,67) |
| LeaderRow.LeaderPill | LeaderRow | 573,323,75,33 | fill #FBD08B, 1–2 px #7E5221, radius ≈6 | "Leader" text ink 588,334,45,11, Serif Bold 14, #5F3007 | 03 small parchment button, hover look (804,816,222,114) has the gold rim; or native |
| MemberRow (other members) | list | same layout as LeaderRow, no crown/pill | — | member headshot, name, level | not shown in the mockup (open q. 1) |
| EmptyRow[i] (×6 visible) | list | rows between rules at y 376, 428, 481, 533, 586, 638, 691; pitch ≈52.4; x 320..648 | no fill | free slots | native |
| EmptyRow.Dot | EmptyRow | 332,y,34,35 with y = 385, 438, 491, 543, 595, 648 (centres x 349, y 402, 455, 508, 560, 612, 665) | flat circle Color.SlotDot | — | native (UICorner 0.5); 01 status dot (904,687,39,39) is framed |
| EmptyRow.Label | EmptyRow | ink x 396, cap 11 px, first at 396,397,77,15 | Serif Bold 14, Color.EmptyInk | "Empty Slot" | native |
| RowRule (×6) | list | x 321..647, y 376, 428, 481, 533, 586, 638; 1 px | Color.RowRule | — | native |

### Column 2: Invite Players (sub-panel)

| Element | Parent | Bounds | Appearance | Content / data | Kit part |
|---|---|---|---|---|---|
| InvitePanel | Window | 670,245,371,448 | as YourPartyPanel | — | native |
| Heading.Icon | panel | 693,262,26,27 | magnifier glyph #381000 | — | 09 search box glyph (inside 25,52,490,114) |
| Heading.Text | panel | ink 738,269,162,16 | Serif Bold 21 (cap 15), Color.HeadingInk | "INVITE PLAYERS" | native |
| Heading.Rule | panel | 687,297,336,2 | Color.HeadingRule | — | native |
| SearchBox | panel | 685,314,340,42 | fill #FEE7C6, 1–2 px #84613F, radius ≈7 | TextBox | 09 search box (25,52,490,114) and 15 search row (432,904,372,84) have leather corners; the mockup box is plain: native |
| SearchBox.Icon | SearchBox | 697,326,20,19 | magnifier glyph #3E1000 | — | as heading icon |
| SearchBox.Placeholder | SearchBox | ink 728,329,115,16 | Serif Bold 15, PlaceholderColor3 #825F44 | "Search players..." | native |
| InviteList | panel | 686,367,337,323 (to the panel's inner bottom) | scroll region, row pitch 66 | players that can be invited | native ScrollingFrame |
| InviteRow.Headshot | row | 689,375,52,51 (row 2: 689,441,52,51) | headshot, 2 px dark outline, radius ≈4 | thumbnail | native |
| InviteRow.Name | row | ink 756,384,104,17 / 756,450,82,18 | Serif Bold 17, Color.Ink | DisplayName ("ForestRanger", "SunnyVale") | native |
| InviteRow.Level | row | ink 756,407,38,10 / 756,473,31,11 | Serif Bold 13–15, Color.InkSoft | "LV. 15", "LV. 8" | native |
| InviteRow.InviteButton | row | 914,379,108,45 / 914,445,108,45 | leather #9F3813, dashed light stitching, rivets, 2 px dark outline, 3 px darker bottom edge | text "Invite" ink 946,395,44,13, Serif Bold 16, #FEFBF2 | 03 leather wide button (43,63,347,107) or 01 small leather button (33,671,266,63) |
| InviteRow.Rule | row | x 688..1021, y 367, 433, 500; 1 px | Color.RowRule | — | native |

### Column 3: Party Details and Readied Status

| Element | Parent | Bounds | Appearance | Content / data | Kit part |
|---|---|---|---|---|---|
| DetailsPanel | Window | 1047,245,322,265 | as YourPartyPanel; shares its bottom border line (y 508–509) with ReadiedPanel; corners curve apart at the ends | — | native |
| Details.Icon | panel | 1064,261,31,30 | disc #461D04 with a white "i" | — | not in the kit (new art or native circle + text) |
| Details.Heading | panel | ink 1111,269,148,16 | Serif Bold 21 (cap 15), Color.HeadingInk; mockup ≈13 % narrower than Merriweather | "PARTY DETAILS" | native |
| Details.Rule | panel | 1063,297,290,2 | Color.HeadingRule (lighter here: bottom px #D5B08B) | — | native |
| Details.Row[i] | panel | label left x 1074, value right edge x 1346; cap tops y 318, 354, 390, (425), 461; pitch ≈35.8; rule under each row at y 341, 377, 413, 449, 485 (x 1073..1347, 1 px, Color.RowRule) | label Serif Bold 15 Color.LabelInk; value Serif Bold 15 Color.Ink | see the next table | native |
| ReadiedPanel | Window | 1047,507,322,186 | as YourPartyPanel | — | native |
| Readied.Icon | panel | 1064,523,31,31 | disc #4F2004 with a white check | — | 16 check (597,365,240,192) is green; flat disc is new art |
| Readied.Heading | panel | ink 1111,532,155,15 | Serif Bold 20, Color.HeadingInk | "READIED STATUS" | native |
| Readied.Rule | panel | 1063,560,290,2 | Color.HeadingRule (#8E653E) | — | native |
| ReadyRow (one per member) | list | 1063,566,289,64 (to the rule at y 629–630, x 1063..1351) | — | member and ready state | native ScrollingFrame for 8 rows (open q. 2) |
| ReadyRow.Headshot | ReadyRow | 1063,574,49,48 | headshot, 2 px dark outline, radius ≈4 | thumbnail | native |
| ReadyRow.Name | ReadyRow | ink 1128,591,87,13 | Serif Bold 16, Color.Ink | DisplayName | native |
| ReadyRow.Pill | ReadyRow | 1267,581,85,34 | fill #E8EAA2, 1–2 px #275B13, radius ≈6 | state | native; status dots from 13 (green 903,820,51,52; yellow 978,820; red 1053,820) |
| ReadyRow.Pill.Dot | Pill | ≈1278,591,12,12 (core 1280,593,9,9) | #07E71A with dark outline | — | 13 green status dot |
| ReadyRow.Pill.Text | Pill | ink 1300,592,40,15 | Serif Bold 14, #0C0F03 | "Ready" | native |

Party Details rows (after the owner decisions):

| Row | Label | Value (mockup → spec) | Value bounds in mockup |
|---|---|---|---|
| 1 | Party Leader | "LiamTheMo" (leader DisplayName; mockup renders it smaller, TextSize ≈13, ink 1275,319,71,11, as if shrunk to fit) | right edge 1346 |
| 2 | Members | "1 / 10" → **"1 / 8"** | 1312,354,34,12 |
| 3 | Join Type | "Invite Only" (fixed) | 1272,390,74,15 |
| 4 | ~~Play Style~~ | **removed** (mockup "Casual") | — |
| 5 → 4 | Created | "Just now" (relative time since the party was formed) | 1287,461,59,12 |

With Play Style removed, the rows keep the 35.8 px pitch; see open question 3
for the freed space.

### Footer

| Element | Parent | Bounds | Appearance | Content / data | Kit part |
|---|---|---|---|---|---|
| CloseButton | Window | 711,703,250,60 (incl. 3–5 px darker bottom edge) | centred on x 836; leather #90310F, dashed light stitching, rivets, 2 px dark outline | closes the window | 03 leather wide button normal (43,63,347,107), hover (409,63), pressed (773,63), disabled (1145,63) |
| CloseButton.Text | CloseButton | ink 795,723,81,19 | Serif Bold 25, #F9F9F9, UIStroke 1 px #601F0A | "CLOSE" | native |

## Measurements log

Scripts: `art/ui/kit/analysis/party/measure_party.py` → `measure_log.txt`.

- Window frame: rows 300/450/600, cols 500/800/1100. Left: rim 275–277, inner
  outline 278–279, paper 280 (outer outline merges with the near-black overlay at
  ≤274). Right: inner 1391–1392, rim 1393–1395, outline 1396–1397. Top: outline
  143–144, rim 145–146, inner 147–148, paper 149. Bottom: 772–774 / 775–777 /
  778–779. → 274..1397 × 143..779.
- Brackets: orange-leather colour components (R−G>55) per corner, plus 5× and 4×
  crops (`corner_tl_5x.png`, `corner_tr_close_4x.png`); ±3 px.
- X button: row 195 outline 1324–1325 / 1377–1378; col 1352 168–169 / 218–220;
  leather component 1326,169,52,49; glyph = largest L>200 component 1341,183,24,24.
- CLOSE button: row 731 711 / 959–960; col 835 703–704 / 757–762.
- Sub-panels: luminance dips (>12 below the line median) on row 680 (304–305,
  662–663, 670–671, 1040, 1047–1048, 1366–1368) and cols 480/860/1200 (245–246,
  691–692, 508–509). Corner radius: first border pixel per row at the top-left
  corner moves 310→304 over y 245→251, so r ≈ 7–8.
- Rules: rows darker than the rows ±3 px: headings 297–298; Your Party 376, 428,
  481, 533, 586, 638; Invite 367, 433, 500; Details 341, 377, 413, 449, 485;
  Readied 560–561 and 629–630. Ground line: L<150 per row, 226..233, widest
  x 481..1261 at y 232–233.
- Headshots: luminance profiles through each (rows 340/400/466/597, cols
  348/715/1087), e.g. leader 320..376 × 313..367.
- Pills/search: leader pill row 339 573 / 647, col 610 323 / 355; search row 335
  685 / 1024, col 850 314 / 355; ready pill row 597 1267 / 1351, col 1310 581 /
  614; invite button row 400 914 / 1021, col 967 379 / 423.
- Dots: flood fill (tol 25) → 34 × 35 at x 332.
- Text (`tsize_run.run`): "PARTY" 153×36 → 47.5; headings 16 px → 19.5–21 (widths
  −9 to −13 % vs Merriweather: the mockup's heading face is narrower); names 14–18
  → 16.5; "LV." lines 10–11 → 13–15; detail labels/values 12–15 → 14–16; "Empty
  Slot" 77×15 → 14; "Search players..." → 15; "Invite" → 15.5; "Ready" → 14;
  "CLOSE" 81×19 → 25.
- Colours: median boxes at the end of `measure_log.txt`.

## States

| Element | Default | Hover | Pressed | Disabled | Other | Source |
|---|---|---|---|---|---|---|
| CloseX | 03 close normal | 03 hover | 03 pressed | — | — | kit 03 row 3 |
| CloseButton | 03 leather normal | 03 leather hover | 03 leather pressed | — | — | kit 03 row 1 |
| InviteButton | leather | 03 leather hover | 03 leather pressed | 03 leather disabled (party full, or not leader) | "Invited" pending state (open q. 4) | kit 03 row 1 |
| SearchBox | placeholder | — | — | — | focused: caret, placeholder hidden; typed text Color.Ink | native |
| ReadyPill | Ready: green pill and dot | — | — | — | Not ready: options in open q. 5 | 13 status dots |
| LeaderRow / MemberRow | as reference | 09 list row hover (544,316,493,119) if rows get actions (kick, promote) | — | — | — | open q. 6 |
| EmptyRow | dot + "Empty Slot" | — | — | — | — | — |

## Data and behavior

| Element | Shows / does | Data source | Server validation |
|---|---|---|---|
| Header count, Members value | members / 8 | party replica | server owns the cap (8) |
| Your Party list | leader first (crown only, D24), then members, then empty slots up to 8 | party replica | — |
| SearchBox + InviteList | players in this lobby server not in the party, filtered by name as the user types | client list of Players, filtered locally | — |
| InviteButton | sends an invite | remote `InviteToParty(userId)` | server checks the sender is leader (or allowed), the party is not full, the target is valid, rate limit |
| Party Leader / Join Type / Created | leader name, "Invite Only", time since creation | party replica | — |
| CloseX / CloseButton | close the window | client | — |

## Open questions

1. Cap 8 in the Your Party list. The mockup shows 7 rows (leader + 6 empty) filling
   the panel (y 299..691). Options: (a) list is a ScrollingFrame, row pitch 52.4,
   the 8th row scrolls (default); (b) row pitch 49 so 8 rows fit; (c) row pitch
   52.4 with a shorter leader row.
2. Readied Status with 8 members: the panel shows one 64 px row and has room for
   ≈2. Options: (a) ScrollingFrame (default); (b) a compact grid of headshots with
   a status dot.
3. Space freed by removing Play Style (≈36 px). Options: (a) leave it empty, keep
   both panels' bounds (default); (b) shrink Party Details by 36 px and grow
   Readied Status by 36 px (border moves from y 508 to ≈472).
4. Invite pending state: does the button change to "Invited" (disabled) after
   sending? Default: yes, until the invite expires or is answered.
5. Not-ready look: options (a) same pill in grey/tan with the 13 yellow or red dot
   and text "Not Ready"; (b) hide the pill. Default: (a) with the yellow dot.
   How does a player toggle their own ready state? The mockup has no control.
   Options: click your own pill; a separate Ready button; the Play window's PLAY
   button. Default: click your own pill.
6. Leader actions (kick, promote, leave party) are not in the mockup. Default: none
   in this window; add later.
7. Header art (tent, trees, ground line) and the flat icon glyphs (people, info,
   check) are not in the kit. Default: slice them from the mockup at 1× as
   temporary images until kit art exists.
8. The 1 px rule under each Details row also appears under the last row (y 485).
   Default: keep it.

## Deviations from reference

- Owner decisions: "1/8" and "1 / 8" (cap 8, mockup 10); no Play Style row; Join
  Type fixed to "Invite Only"; no Readied Status card, no Ready / Not Ready or
  Leader tags (D24): Party Details fills the right column and the leader row
  shows only the crown. The measurements of the mockup's Leader pill and
  Readied Status rows above record the mockup only.
- Column headings in the mockup are 9–13 % narrower than Merriweather Bold at the
  same height; they render up to 22 px wider in Roblox. Even then each heading keeps
  ≥ 80 px clear to its panel's right edge (e.g. "PARTY DETAILS" 1111..≈1281 vs edge
  1366), so no change is needed.
- The HUD hotbar and XP bar under the overlay sit 14–17 px lower in this mockup
  than in the HUD mockup; keep the HUD positions.
- The world behind the overlay is a darker, bluer, softened render in the mockup;
  see LobbyScreen open question 1.

## Fix round 3

- **Rows update in place** (M3): `SetData` keys every row (member, invite,
  player, empty slot, detail) by its player or label and keeps a row
  whose contents did not change; only changed rows are rebuilt, gamepad
  targets follow (`PartyWindow:Rows(list)` returns a list in order). Search
  waits 0.3 s after the last keystroke.
- **Pending state** lives in PartyController (`Answer`, `AnswerBusy`,
  `Changed`); the HUD uses it (M2).
- **Phones**: names, levels and button labels at 15 (9 screen px or more);
  long names end in "…"; "Invited" fits its button (V9); a long Party Leader
  value ends in "…" so "Party Leader" keeps its room (R12).
- **Party Details icon**: the book glyph (the "!" read as a warning, V15).
- Opens with the gamepad flag when the last input is a gamepad (R6).
