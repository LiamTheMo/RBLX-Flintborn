# Journal screen UI spec

Reference: `art/reference/ui/lobby/07_quest_journal.png`. Kit: `art/reference/ui/lobby/kit/`
(sheet numbers below are the file prefixes). Design resolution: 1672 × 941 (the image
size); every bound is a screen pixel of the mockup, x, y, w, h from its top-left, ±1–2 px.
Status: Draft. Source of truth for build: the reference image. This replaces the spec of
the previous parchment Journal (All / Daily / Main tabs and the island map).

Raw crops, font comparisons and the measuring scripts are in
`art/ui/kit/analysis/journal/` (the shared helpers live in `art/ui/kit/analysis/forge/`).

## Overview

The Quest Journal (GDD §10.1, §25), a modal parchment window over the dimmed lobby HUD,
opened by the Quests (scroll) tile of the HUD menu grid (`JournalController.Toggle`) and
closed by ✕, ButtonB or the tile. Four icon tabs hang off the window's left edge (book
active, trophy, map pin, party). The book tab shows: the quest list on the left (5 rows,
one selected), and on the right the selected quest's illustration, title and description,
OBJECTIVES rows with progress and a check circle, REWARDS tiles, a CLAIM button, and a
QUEST PROGRESS bar along the bottom ("1 / 5 Completed").

## Dim overlay and the HUD behind

Same method as `ForgeScreen.md` (least-squares fit against `01_hud.png`).

| Region | k (R, G, B) | offset c | Note |
|---|---|---|---|
| Player card + currencies + gear (zero-offset fit) | 0.344, 0.338, 0.346 | — | bright parchment #FACF9F → #564637 (86, 70, 55) |
| Same, free fit | 0.325, 0.312, 0.313 | 4.3, 4.9, 5.0 | implies overlay colour ≈ #060707 |
| Sky / mountains, grass, trees, scene right | 0.274–0.291 | — | |

- Overlay: near-black at **≈ 68 % opacity** (range 66–72 %), **BackgroundTransparency
  ≈ 0.32** (0.28–0.34), colour #000000 to #0F0D0B. Matches the forge mockup within the
  measuring noise; one shared value fits both. No reliable blur evidence.
- The HUD stays visible under the overlay. The window hides the XP bar. The hotbar sits
  **37 px lower** than in `01_hud.png` (cross-correlation, dx 0); the forge mockup has
  40 px. See Open questions.

## Tokens

| Token | Value | Used by |
|---|---|---|
| Color.Overlay | #000000 @ 0.32 transparency | dim layer |
| Color.Parchment | #FDDCB1 (body), #FDD3A1 (scorched band under the top edge) | window |
| Color.FrameEdge | dark #0C0A07 1 px, orange rim 5 px (#CC7633–#DE8B43), dark 2 px, then parchment (left edge 300–307; right 1363–1371; top 150–155; bottom 829–837) | window edge |
| Color.Leather | #9F3610 (top / middle), #892808 (bottom); ✕ #AA3E11 | CLAIM, ✕ |
| Color.RowFill | #FCDFB9 | quest rows, objective rows |
| Color.RowOutline | #D6AD81 2 px (quest rows), #C79B73 1 px + light line under it (objective rows), #DAB689 2 px (reward tiles) | rows, tiles |
| Color.SelectOrange | #FB6B11 (2–3 px, #FD7816 → #FC5B04) with a 1 px light inner line #FEF2CA | selected quest row |
| Color.SelectFill | #FEE2B2 (left edge #FDDBA4) | selected quest row |
| Color.TabFill | #FED6A6 (inactive), #FDE0B4 (active) | side tabs |
| Color.TabActiveRim | dark 1 px, orange #FB8706–#FFA416 2 px, dark 1 px inside | active tab |
| Color.Rule | #AB7B53 (header), #C09167 (list scroll rule x 735), #E1B283 (x 351), #D8AF87 (y 395), #E9C298 (y 627), #D3A373 (y 776) | rules |
| Color.CheckRing | #CC9F73, ring ≈ 3 px, outer Ø 30 | objective circles |
| Color.Track | #683C1E, outline #48321E | progress bar track |
| Color.Fill | #FEA403, top highlight #FAD06C | progress bar fill |
| Color.InkTitle | #431D05 (median), #310B00 (core) | QUEST JOURNAL |
| Color.Ink | #000000–#1C0300 (core) | titles, labels, counts |
| Color.InkSoft | #362315 (row subtitles), #5F452D (objective descriptions) | secondary text |
| Color.OnLeather | #FFFFFF | CLAIM, ✕ glyph |
| Font.Serif | Merriweather Bold | titles, labels, counts |
| Font.Body | Merriweather Regular (or Balthazar, see Fonts) | subtitles, descriptions |

## Fonts

Compared in 3× renders under the reference crops (`font_title.png`, `font_rowtitle.png`,
`font_desc.png`, `font_detailtitle.png`); widths at the measured cap height.

| Text | Measured | Closest Roblox family | Fit |
|---|---|---|---|
| QUEST JOURNAL | cap 40 (Q tail to 227), 396 px wide, bold serif with rounded wedge serifs | **Merriweather Bold**, TextSize ≈ 53 at equal cap height (47 to match width) | Merriweather is 13 % wider at equal cap height; letter shapes close. No condensed serif is built in. |
| Quest titles, objective titles, detail title | bold serif, small x-height | **Merriweather Bold** | 13–17 % wider at equal cap height |
| Subtitles and descriptions | book serif, regular weight | **Merriweather Regular** (the repo's family) | 10–14 % wider; alternative **Balthazar** matches the description width exactly (309 vs 309 px) and has a similar book shape. Balthazar is believed to be a Roblox built-in family; confirm in Studio's font picker. |
| All-caps labels (OBJECTIVES, REWARDS, QUEST PROGRESS) | bold serif caps | Merriweather Bold | within −3 … +5 % |

Merriweather: TextSize ≈ cap height / 0.75. A faint light halo (2 px ring a few levels
lighter than the paper) surrounds dark text, as on the forge; optional.

## Element tree

Bounds are screen px (x, y, w, h). Children of Window unless noted.

| Element | Parent | Bounds | Anchor intent | Appearance | Content | Kit piece |
|---|---|---|---|---|---|---|
| Overlay | ScreenGui | 0, 0, 1672, 941 (bleed past safe area) | full screen | see Dim overlay | — | native |
| Window | Overlay | 300, 150, 1072, 688 | horizontally centred on the screen (centre x 835.5); vertically 23 px below centre (centre y 493.5) — the forge window is centred | parchment, scorched outline (Color.FrameEdge), dashed stitch line ≈ 6 px in; no side clasps | — | 04 window frames (e.g. 450–1107, 505–770, no clasps) as a 9-slice |
| CornerTL / TR / BL / BR | Window | 300, 145, 45, 45 / 1325, 146, 48, 44 / 300, 780, 45, 57 / 1325, 780, 48, 57 | window corners | leather brackets #933511 with rivets | — | 04 corners; 14 corner pieces (95–325, 50–245) |
| SideTabs | ScreenGui (or Window, drawn above it) | 250, 251, 93, 365 | window's left edge: they overlap the frame from x 300 to 336 | four square tabs, pitch ≈ 94 | — | 05 item slot normal (65–333, 45–302) and hover (707–977, orange rim); 10 slot selected (985–1147, 75–228, orange #EF7204) |
| Tab1 (active, quests) | SideTabs | 250, 251, 93, 87 | top | Color.TabActiveRim around Color.TabFill (active), notched corners | open book icon (272, 275, 55, 42), orange leather #B84004 | 10 slot selected; icon: 11 journal book (880–1100, 830–1075) is a closed book; no open-book icon on the sheets |
| Tab2 (trophy) | SideTabs | 255, 345, 82, 84 | under Tab1 | dark 1 px outline, Color.TabFill, small corner rivets | trophy silhouette (272, 370, 48, 42), dark brown #582201 | 05 slot normal; icon: 11 trophy (1125–1365, 330–560) is full-colour gold |
| Tab3 (map pin) | SideTabs | 255, 438, 82, 86 | under Tab2 | as Tab2 | pin over a folded map (270, 457, 52, 48), dark brown | icon: 17 map pin (70–270, 840–1070) + 11 map (850–1100, 330–560), both full-colour |
| Tab4 (party) | SideTabs | 255, 533, 82, 84 | under Tab3 | as Tab2 | three-person silhouette (270, 552, 52, 48), dark brown | icon: 11 party (570–840, 330–560), full-colour |
| HeaderIcon | Window | 364, 159, 84, 88 | top-left | ink-drawn compass rose, dark brown #350C00, small red-brown centre dot | — | none matching: 11 compass (1140–1345, 585–810) is a gold pocket compass; 17 compass arrow (315–540, 845–1065) a gold arrow in a ring |
| Title | Window | 457, 182, 396, 40 (cap top 182, baseline 221) | top-left, left-aligned | Merriweather Bold, Color.InkTitle | "QUEST JOURNAL" | native text |
| HeaderRule | Window | 339, 242, 992, 2 | under title | Color.Rule #AB7B53, arrowhead at the left end (339–360), interrupted by the compass's south point (395–416) | — | 14 divider (60–850, 475–570); no arrow-ended rule on the sheets |
| Close | Window | 1295, 172, 59, 56 | top-right | leather square, rivets, white ✕ | — | 03 close button, normal (345–480, 330–462) and states |
| ListRuleLeft | Window | 351, 260, 1, 506 | list left | #E1B283 | — | 14 vertical divider (895–985, 285–570) |
| ListScrollRule | Window | 735, 261, 1, 506 | between list and detail | #C09167, arrowheads at both ends (reads as a scroll indicator) | — | 14 vertical divider with diamond ends; no arrow version |
| QuestList | Window | 362, 261, 359, 505 | left column | vertical list, pitch ≈ 103.5, 5 rows visible | rows | ScrollingFrame |
| QuestRow (normal) | QuestList | 363, y, 357, 95 (y 361, 465, 568, 671) | list | Color.RowFill, 2 px Color.RowOutline, radius ≈ 8 | — | 09 list row normal (25–515, 318–432; has a dark outline and a dot); 01 "list + cards" soft card |
| QuestRow (selected) | QuestList | 362, 261, 359, 92 | list | Color.SelectFill, Color.SelectOrange border with a soft glow, radius ≈ 8 | — | 09 list row selected (545–1035, 318–432, gold #F8A40A); 10 slot selected is the closer orange |
| Row.Icon | QuestRow | 368–467 × row y + 14 … + 89 (≈ 90 × 72), centred x ≈ 418 | row left | full-colour illustration icon | per quest | logs: 16 log (30–275, 880–1080) / 10 logs / 12 wood tile; shelter: 17 hut (1130–1365, 835–1065) differs (mockup is a stilt watchtower); tools: 12 axe + pickaxe (crossed, no single kit piece); campfire: 17 campfire (850–1070, 70–300); pier in water: no kit piece (17 wave, rope bridge nearby) |
| Row.Title | QuestRow | 482, row y + 22, ≤ 200, 17 (cap) | left-aligned | Merriweather Bold cap 16–17 → TextSize ≈ 22 (19 width-matched), #000000 | "Gather Supplies", "Build a Shelter", "Craft Tools", "Light the Campfire", "Explore the Island" | native text |
| Row.Subtitle | QuestRow | 483, row y + 51, ≤ 200, 12–13 (cap) | under title | Merriweather Regular cap 12–13 → TextSize ≈ 16.5 (15 width-matched), Color.InkSoft #362315 | "Collect basic resources.", "Prepare a place to stay.", "Make tools for survival.", "Bring warmth to camp.", "Discover new areas." | native text |
| Row.Chevron | QuestRow | 693, row y + 40, 8, 16 | right, vertically centred | ">" glyph, #0E0000 | — | 09 list rows carry the same chevron |
| Illustration | Window | 756, 262, 217, 122 | detail top-left | painted scene: logs, rocks, plants | per quest | none (built from 16 log, 17 rocks, plants) |
| DetailTitle | Window | 981, 268, 265, 30 (cap; baseline 297, descender to 307) | right of illustration, left-aligned | Merriweather Bold cap 30 → TextSize ≈ 39 (33.5 width-matched), #1A0200 | "Gather Supplies" | native text |
| DetailDesc | Window | 984, 318, 326, 44 (two lines, baselines 332 and 356, pitch 24) | under title, left-aligned, wraps | Merriweather Regular cap 15 → TextSize ≈ 20 (17.5 width-matched), #130603 | "Collect basic resources from around / the island to prepare for your journey." | native text |
| DetailRule1 | Window | 755, 395, 587, 2 | detail width | #D8AF87, arrowhead at the right end | — | 14 divider |
| ObjectivesHead | Window | 755, 407, 117, 14 (cap) | left | Merriweather Bold cap 14 → TextSize ≈ 18 | "OBJECTIVES" | native text |
| ObjectiveRow | Window | 752, y, 590, 58–60 (y 432, 497, 562) | detail width, pitch 65 | Color.RowFill, 1 px #C79B73 outline with a light line inside, radius ≈ 6 | — | 12 objective rows (70–828, 195–322 and 330–455) carry checkbox, icon tile, bar, count and CLAIM; mockup rows are simpler. 12 check rows (48–440, 655–737) for the plain row |
| Obj.Icon | ObjectiveRow | 764, row y + 9, 50, 42 | row left | material icon | wood, stone, plant fibre | 16 log / 10 logs; 12 stone tile / 10 stones; 19 leaf sprig (810–890, 135–230) |
| Obj.Title | ObjectiveRow | 836, row y + 11, ≤ 250, 15 (cap) | left-aligned | Merriweather Bold cap 15 → TextSize ≈ 20 (17 width-matched), #0B0100 | "Collect Wood", "Collect Stone", "Collect Plant Fiber" | native text |
| Obj.Desc | ObjectiveRow | 836, row y + 33, ≤ 300, 11–12 (cap) | under title | Merriweather Regular cap 12 → TextSize ≈ 15 (13 width-matched), #5F452D | "Chop down trees around the island.", "Mine rocks and boulders.", "Gather plants and bushes." | native text |
| Obj.Count | ObjectiveRow | right edge 1274, row y + 21, 16 tall | right-aligned before the circle | Merriweather Bold digits → TextSize ≈ 21 (18 width-matched), #000000 | "12 / 20", "8 / 15", "3 / 10" | native text |
| Obj.Check | ObjectiveRow | 1296, row y + 15, 30, 30 | row right, vertically centred | empty ring, Color.CheckRing | — | none (kit has square checkboxes: 09, 12); native Frame + UICorner 1 + UIStroke 3, or image. Done state: options 12 check tile (1153–1222, 900–972), 16 check (600–835, 370–555) |
| DetailRule2 | Window | 752, 627, 590, 2 | detail width | #E9C298, arrowhead at the right end | — | 14 divider |
| RewardsHead | Window | 756, 637, 93, 14 (cap) | left | Merriweather Bold cap 14 → TextSize ≈ 18 | "REWARDS" | native text |
| RewardTile | Window | 751, 662, 92, 104 / 849, 662, 91, 104 / 946, 662, 93, 104 / 1045, 662, 101, 104 | left to right, gap ≈ 7 | fill #FDE3C1, 2 px #DAB689, radius ≈ 8 | — | 12 material tiles (1150–1493, 785–875); 05 slot normal (smaller rivets) |
| Rew.Icon | RewardTile | ≈ tile x + 13, 675, 68, 55 | tile upper part | item / coin icon | wood logs, two rocks, fern sprig, coin | 16 log / 10 logs; 12 stone tile; 19 leaf sprig; 02 coin (597–667, 645–712) / 06 coin |
| Rew.Amount | RewardTile | right edge ≈ tile x + 82, baseline 730, ≈ 15 tall | bottom-right of the icon, over it | Merriweather Bold → TextSize ≈ 19, #070301 | "x50", "x30", "x20", "x250" | native text |
| Rew.Label | RewardTile | centred, cap 742–753 | tile bottom | Merriweather Bold cap 12 → TextSize ≈ 15 (13 width-matched), #020101 | "Wood", "Stone", "Plant Fiber", "Coins" | native text |
| Claim | Window | 1159, 661, 183, 88 | right of rewards, bottom-right of detail | leather, dark outline, many brass rivets along the edge, slight drop shadow | "CLAIM" (1211, 694, 82, 21 cap; Merriweather Bold → TextSize ≈ 27, 24 width-matched; #FFFFFF) | 12 CLAIM (945–1120, 557–625) is 175 × 68; 03 wide leather button states (row 1) for hover / pressed / disabled |
| BottomRule | Window | 350, 776, 980, 2 | above progress | #D3A373 | — | 14 divider |
| ProgressLabel | Window | 498, 793, 143, 13 (cap) | bottom, left of bar | Merriweather Bold cap 13 → TextSize ≈ 16.5, #010000 | "QUEST PROGRESS" | native text |
| ProgressBar | Window | 657, 790, 375, 18 | bottom centre | dark outline #48321E, track #683C1E, inner 659–1029; fill #FEA403 with a light top line, ends at x 767 (29 % of the inner width), rounded ends | — | 05 XP bar fill and track (200–1090, 778–835); 19 bars (empty 48–470, 450–545) |
| ProgressText | Window | 1049, 791, 126, 15 (cap) | right of bar | Merriweather Bold cap 15 → TextSize ≈ 20 (16.5 width-matched), #020100 | "1 / 5 Completed" | native text |

Z-order (back to front): HUD → Overlay → Window art → rules → rows, tiles → icons and
text → corner brackets → SideTabs (over the frame's left edge) → Close.

## Measurements log

Run from the repo root; helpers as in `ForgeScreen.md` (`art/ui/kit/analysis/forge/*.py`).

- Window edges: pixel dumps along rows 500 / 680 (x 292–318), row 600 (x 1352–1380) and
  column 900 (y 140–165, 815–842) of `07_quest_journal.png`; brackets with
  `mask.py <img> leather 290 135 55 55` and the other corners.
- Side tabs: `parchruns.py <img> col 262 240 640 2`, `col 268`, `col 328`, rows 270–600;
  dark-outline runs (luma < 90) on columns 262 / 330 and rows 270 / 380 / 470 / 560;
  pixel profiles across the active tab's rim (row 300 x 246–262, column 300 y 246–262).
- Quest rows: `edges.py <img> col 470 255 780 30`, `col 680`, rows 300 / 400 / 520 / 720.
- Rules: inline numpy line extents (rows 242–243, 395–396, 627–628, 776–777; columns
  349–353, 733–738).
- Objectives, circles, rewards, CLAIM, close: `edges.py` on row 461 / 526, row 461
  x 1285–1345, columns 1311, rows 670 / 760, columns 760 / 1140; dark-outline runs on
  column 1250 and row 705 (CLAIM), row 200 and column 1326 (close).
- Progress bar: pixel dumps along row 798 and columns 700 / 900.
- Text: `python3 art/ui/kit/analysis/journal/measure_journal.py`.
- Colours: `python3 art/ui/kit/analysis/journal/colors_journal.py`; title ink percentiles
  inline.
- Check: `art/ui/kit/analysis/journal/overlay_check.png` draws the main bounds on the
  mockup; every box sits on its element's edge.
- Kit rim colours: median of saturated rim pixels in kit 05 selected / hover, 09 list
  row selected, 03 small parchment gold, 10 slot selected.
- Dim overlay and HUD shift: as in `ForgeScreen.md`, against this image.

## States

| Element | Default | Hover | Pressed | Selected | Disabled | Focus (gamepad) | Source |
|---|---|---|---|---|---|---|---|
| Side tab | parchment tile | not shown (kit 05 hover is the orange rim) | not shown | orange rim (Tab1) | for a tab with no content (see Data) | not shown | reference, kit 05 / 10 |
| QuestRow | soft card | not shown | not shown | orange border (row 1) | — | not shown | reference |
| QuestRow status | not shown: today's rows show finished-and-waiting / under way / claimed dots (`questReady`, `questOpen`, `questDone`) | | | | | | current JournalPanel |
| Obj.Check | empty ring (all three under way) | — | — | done: not shown | — | — | reference |
| Claim | leather, looks enabled | kit 03 hover | kit 03 pressed | — | kit 03 disabled: needed while unfinished, claimed ("CLAIMED") or a claim is on its way | not shown | reference shows it enabled although no objective is complete |
| Close | leather ✕ | kit 03 close hover | pressed | — | — | not shown | kit 03 |

Scroll regions: QuestList (5 visible; the catalog has 8 quests; the double-arrow rule at
x 735 reads as its scroll indicator) and possibly the objectives (3 rows fit between
y 432 and 621).

## Motion and effects

None shown.

## Data and behavior

Remotes: `QuestView` (refreshed every 5 s while open, `JournalController.refresh`) and
`QuestClaim(questId)`. Each quest from `EconomyRules.QuestView`: `id, name, tier, coins,
gems?, booster?, count, needed, claimed, repeats ("Daily" | "Once"), action`.

| Element | Shows / does | Data source | Notes |
|---|---|---|---|
| QuestRow title | quest name | `name` ("Gather 100 times", "Extract once", "Craft 15 items", "Defeat 10 creatures", "Open 2 caches", "Extract 3 times", "Defeat a boss", "Defeat the Guardian") | mockup names are narrative ("Gather Supplies") |
| QuestRow subtitle | one line | **no direct source**. Options: the objective line from `JournalPanel.OBJECTIVES[action]` ("Gather from resource nodes", …); repeat + tier ("Daily · Easy"); a new description field in `QuestCatalog` | |
| QuestRow icon, Illustration | per-quest art | **no source**; options: one icon per `action` (Harvest, Extract, Craft, Enemy, Cache, Boss, Guardian) from the kit (e.g. 17 paw / tusk for Enemy, 11 chest or 17 treasure chest for Cache, 11 portal for Extract) | |
| DetailTitle | quest name | `name` | |
| DetailDesc | two lines | **no source** (see subtitle options) | |
| Objectives | one row per objective | each quest has exactly **one** objective: `action`, `count` / `needed` | the mockup shows three per quest. Obj.Title / Obj.Desc options: `OBJECTIVES[action]` and the quest name; the count is `count / needed`; the circle is done when `count >= needed`. |
| Rewards | one tile per reward | `coins` (250 / 1,000 / 3,000 by tier), `gems` (25 or 50 on some quests), `booster` (XP boost on DailyExtractions) | no item rewards exist (the mockup's Wood / Stone / Plant Fiber tiles have no source); today's icons: `pm_icon_coin`, `pm_icon_gem`, `pm_icon_bolt` ("XP Boost") |
| Claim | pays a finished quest | `QuestClaim(id)`; enabled when `count >= needed`, not `claimed`, and no claim in flight; label "CLAIMED" after | outcome text ("Reward claimed." / `Reasons.Text(reason)`) has no place in the mockup |
| QUEST PROGRESS | n / m Completed | **no direct source**; options: claimed quests / quests listed; finished (count ≥ needed) / listed; daily only | mockup fill (29 %) does not match its own text (1 / 5 = 20 %) |
| Daily reset, repeat type | — | `repeats`, `QuestCatalog.Period` (UTC day) | the old All / Daily / Main tabs have no counterpart in the mockup; options: a filter, section headers in the list, or the trophy tab for one-time quests |
| Side tab: book | quests | `QuestView` | active in the mockup |
| Side tab: trophy | no achievement system exists in the code. Options: the Progress window's content (`ProgressionController`: level, mastery tracks, titles, rebirth, perks); one-time quests (`repeats == "Once"`, e.g. Defeat the Guardian); leave disabled until achievements exist | | |
| Side tab: map pin | Options: the island map the current Journal already draws (`Hud/IslandMap`, pins for camps and landmarks, quest places from `JournalPanel.PLACES`); the world map (`MapController`) is world-place only | | |
| Side tab: party | Options: the lobby party (`LobbyController.PartyView()`, the Party screen in `04_party.png`); party or tribe quests do not exist; tribes (`TribeController`) are world-place only | | |

## Asset map

| Asset | Kit source | Size in mockup | 9-slice | Status |
|---|---|---|---|---|
| Window frame | 04 (e.g. 450–1107, 505–770, no clasps) | 1072 × 688 | yes, corners ≈ 45 px | to slice |
| Side tab normal / active | 05 slot normal; 10 slot selected (orange) | 82 × 84, active 93 × 87 | yes | to slice |
| Tab glyphs (book, trophy, map pin, party) | 11 / 17 icons are full-colour; mockup glyphs are dark-brown silhouettes (book orange) | ≈ 52 × 46 | no | to make (silhouettes) |
| Compass rose | none | 84 × 88 | no | to make |
| Close (4 states) | 03 row 3 | 59 × 56 | no | to slice |
| Quest row normal / selected | 09 list rows (normal, selected) or native Frame + UIStroke + UICorner | 357 × 95, 359 × 92 | yes | either |
| Chevron | 09 list row chevron | 8 × 16 | no | to slice or text glyph |
| Objective row, reward tile | native (soft outline) or 01 soft card / 12 material tile | 590 × 59, ≈ 92 × 104 | yes | either |
| Check ring | none | 30 × 30 | no | native |
| CLAIM (4 states) | 03 wide leather button / 12 CLAIM | 183 × 88 | yes | to slice |
| Progress bar track / fill | 05 XP bar (200–1090, 778–835) | 375 × 18 | yes (3-slice) | to slice |
| Arrow-ended rules | none; 14 dividers | various | 3-slice | to make or native |
| Quest icons, illustration | 16, 17, 12, 10 (see tree); several missing | ≈ 90 × 72, 217 × 122 | no | partly missing |

## Open questions

1. Side tabs trophy / map pin / party: which content (options under Data)? Tabs with no
   content: hidden, disabled, or shown?
2. Multiple objectives and item rewards per quest do not exist in the data; build for one
   objective and coin / gem / boost rewards, or extend `QuestCatalog`?
3. Quest descriptions, subtitles and illustrations have no source.
4. QUEST PROGRESS: what n / m counts; the mockup fill (29 %) disagrees with its text (20 %).
5. CLAIM appears enabled while every objective is under way: confirm it is disabled until
   the quest is finished (current behaviour).
6. Daily vs one-time quests and the daily reset are not shown.
7. Row status (ready / under way / claimed) and the claim message are not shown.
8. Window vertical position: 23 px below centre (clears the top HUD) vs centred like the
   forge window.
9. Bottom HUD under the modal: hotbar 37 px lower than in `01_hud.png`.
10. Body face: Merriweather Regular (repo family, 10–14 % wider) or Balthazar (width
    match; confirm it ships).

## Deviations from reference

- Serif text sets wider in Merriweather than in the mockup at equal cap height (see Fonts).
- No letter-spacing control in Roblox.

## Fix round 3

- **Rewards** (V6): a long amount ("x250") moves the tile's icon up and left so
  the two never overlap.
- **Description** (V7): shrinks to fit its box instead of running into the
  OBJECTIVES rule.
- **Phones** (R9): the Daily / Main tag at 16, row lines at 16 and objective
  lines at 16 (9 screen px or more at the phone window scale).
- Opens with the gamepad flag when the last input is a gamepad.
