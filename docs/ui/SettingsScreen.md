# Settings screen UI spec

Reference: `art/reference/ui/lobby/03_settings.png` (Gameplay tab). Kit:
`art/reference/ui/lobby/kit/` (index in `art/reference/ui/lobby/README.md`).
Design resolution: 1672 × 941 (the image size). Every bound below is design px
from the top-left of the screen, measured from the image (±1–2 px); "rel" is
relative to the window's top-left (287, 150).
Status: Draft (measured spec for the lobby UI rebuild). Source of truth for build:
the reference image. The old parchment spec this file replaces described
`10_settings.png`, which has been removed; the live code it describes
(`src/client/Hud/SettingsPanel.luau`) is mapped below.

## Overview

The modal Settings window, opened by the HUD gear button (top right), the ⚙
button in the world, or the Settings key (O). A dark overlay covers the whole
screen, including the HUD (same overlay as the Inventory screen, see
[`InventoryScreen.md` → Dim overlay](InventoryScreen.md#dim-overlay); 03 measures
k ≈ 0.30, overlay ≈ #080807 at 70 % opacity). Tabs down the left choose a page;
the mock shows Gameplay. The page has a left column (GAMEPLAY: sliders,
checkboxes, Language dropdown) and a right column (KEY BINDS). RESET and APPLY
sit at the bottom right; a line-art plant sits at the bottom left. The close
button is top right. As in the Inventory mock, the dimmed HUD under the overlay
is shifted (hotbar ≈ 38 px lower, party panel moved); keep the HUD from
`01_hud.png`.

## Tokens

| Token | Value | Used by |
|---|---|---|
| Overlay | ≈ #080807–#0E0C08, BackgroundTransparency ≈ 0.30 | Full-screen dim |
| Parchment | #FDE0BA (body), #FEE2BF (key column) | Window body |
| Parchment.Raised | #FEE2BE | Inactive tabs, RESET (#FEDBB0) |
| Leather | #B7461C (top) → #9E3611 (bottom) on the active tab; #B64720 APPLY; close #A64214 | Active tab, APPLY, close |
| Ink.Title | #3E1806 (core; Inventory title measures #2C1204 — one token, open question 7) | SETTINGS |
| Ink.Heading | #0A0705 | GAMEPLAY, KEY BINDS |
| Ink.Strong | #080604 (tab labels), #130703 (values), #100C08 (key text), #18120A (dropdown value) | Labels, values |
| Ink.Label | #1F160F (slider / Language labels), #221A14 (checkbox titles), #2E170D (key labels) | Row labels |
| Ink.Muted | #714B2D | Checkbox descriptions |
| Ink.OnLeather | #FBF5EE (tab label), #FBF8F3 (tab icon), #FBF5F1 (APPLY), #F9F7F7 (close ✕) | — |
| Glyph.Dark | #0A0100–#0A0200 | Title gear, inactive tab icons |
| Sketch | #612E11–#733E1E line art | Tents, signpost, plant |
| Slider.Fill | #FDB104 (lighter top edge, #F6A80A bottom) | Slider filled part |
| Slider.Track | #793E1E | Slider empty part |
| Slider.Knob | #FDDEB5 fill, dark outline | Knob |
| Box.Value | fill #FDDEB8, 1–2 px stroke #AE8058, radius ≈ 3 px | Slider value boxes |
| Box.Key | fill #FDDEB8, 1 px stroke #96623B, radius ≈ 2 px | Key caps |
| Check.Fill | #FCBB0F, 2 px dark outline, check #090600 | Checkbox on |
| Dropdown | fill #FEDDB3, 2 px stroke #2D0C00, chevron #401408 | Language |
| Rule.Title | #70462E, 2 px, fading in at the left | Title underline |
| Rule.Heading | #C49061, 1–2 px | Under GAMEPLAY / KEY BINDS |
| Rule.Section | #DFAE83, 1 px | Between sliders and checkboxes |
| Rule.Key | #F0CCA6, 1 px (very faint) | Between key rows |
| Rule.Column | #D6A270 1 px (x 564) / #D7A575 2 px (x 993) | Column dividers |
| Rule.Bottom | #90603D, 2 px | Above the buttons |
| Font.Serif | Merriweather (see [Typography](#typography)) | All text |

## Typography

Merriweather confirmed as the closest Roblox family (same evidence as
`InventoryScreen.md`; settings crops in
`art/ui/kit/analysis/settings/font_sbs.png`): at matched height Merriweather Bold
sets "SETTINGS" 232 px wide (mock 231). Title stems are heavier than Bold (see
Inventory: Black, or Bold + 1 px stroke). Row labels ("Camera Sensitivity",
"Move Forward"), checkbox descriptions and the dropdown value have a lighter,
book-weight look: Merriweather **Regular** matches their weight better
(IoU 0.55 vs 0.47 on "Camera Sensitivity"); widths match within 3–5 %.
TextSize = cap height ÷ 0.74.

| Text | Weight (proposed) | Cap height (px) | TextSize | Colour | Align |
|---|---|---|---|---|---|
| SETTINGS | Black (or Bold) | 31 ('S' 189–220 incl. overshoot) | 42 | Ink.Title | left |
| Tab labels | Bold | 17–18 ('A' of Audio 384–401) | 24 | Ink.OnLeather (active) / Ink.Strong | left |
| GAMEPLAY, KEY BINDS | Bold | 16–17 (268–284) | 22 | Ink.Heading | left |
| Slider labels, Language | Regular | 12–13 ('C' 319–331) | 17 | Ink.Label | left |
| Slider values | Bold | 12–13 (351–362) | 17 | Ink.Strong | centre |
| Checkbox titles | Regular (mock reads medium) | 12–13 ('A' 543–554) | 17 | #221A14 | left |
| Checkbox descriptions | Regular | 10 ('A' 564–573) | 14 | Ink.Muted | left |
| Dropdown value | Regular | 13 ('E' 670–682) | 17.5 | #18120A | left |
| Key labels | Regular | 13 (318–330) | 17.5 | #2E170D | left |
| Key text | Bold | 12–13 (319–330) | 17 | #100C08 | centre |
| RESET | Bold | 16 (751–766) | 22 | #3B1302 | left of centre (after icon) |
| APPLY | Bold | 17 (750–766) | 23 | Ink.OnLeather | centre |

## Element tree

Z-order: Overlay < Window frame < rules, dividers, sketches < tabs, controls <
text and icons < open dropdown list (topmost, above the key column). Anchor
intent: window centred horizontally (centre x 835) with its top at y 150 (centre
y 477.5, 7 px below screen centre); same rule as the Inventory window.

| Element | Parent | Bounds x, y, w, h (screen) | rel (window) | Appearance | Content | Kit part / build |
|---|---|---|---|---|---|---|
| Overlay | ScreenGui | 0, 0, 1672, 941 | — | Overlay token | — | native Frame |
| Window | Overlay | 287, 150, 1097, 656 | 0, 0 | parchment, 4–5 px dark outline (core #1E0000–#230900), inner orange rule ≈ 9–10 px in (x 296 / 1374, y 159–160 / 795); leather corner brackets at all four corners (top ones protrude ≈ 3–5 px above the top edge; TL ≈ 290–325 × 145–170); side clasps near the bottom on both edges at ≈ 284, 756, 18, 18 and 1371, 756, 15, 18 | — | **kit 04** parchment window (9-slice; frame 1 at 48, 43, 1082 × 426 has right clasps higher up, frame 3 at 56, 490, 303 × 413 a left clasp near the bottom: no kit frame has both bottom clasps) or kit 10 window frame with contents erased |
| TitleIcon | Window | 337, 172, 63, 65 | 50, 22 | solid dark gear (Glyph.Dark), faint highlight | — | **not in kit** (kit 06 gear 907, 411 and kit 11 gear 328, 334 are stone-coloured full-colour icons) — options: recolour kit 11 gear to Glyph.Dark, or new glyph |
| Title | Window | ink 422, 188, 231, 34 | 135, 38 | per Typography | "SETTINGS" | native TextLabel; suggest frame 420, 175, 300, 56 |
| TitleRule | Window | 317, 237, 973, 2 (faint 317–390, full from ≈ 419 to 1290) | 30, 87 | Rule.Title | — | native Frame + UIGradient (transparent at the left end) |
| CloseButton | Window | 1304, 169, 61, 57 | 1017, 19 | leather square, ✕, rivets | — | **kit 03** close normal (342, 329, 140 × 135) + hover / pressed / disabled in the same row |
| TabList | Window | 314, 259, 237, 360 | 27, 109 | — | 4 tabs, pitch 93 | UIListLayout Padding 13 |
| Tab.Gameplay (active) | TabList | 314, 259, 237, 81 | 27, 109 | leather gradient (#B7461C → #9E3611), dark outline, rope/leather lashings on all four corners (≈ 12 × 12 each, at the outline) | gamepad icon 336, 282, 50, 38 (cream); label "Gameplay" x 405, cap 292–308 | **kit 03** wide leather (44, 63, 345 × 106; rivets instead of lashings — lashings **not in kit**, closest kit 14 rope knot 391, 250 / 647, 241) ; the active tab is 3 px wider and 1 px taller than the inactive ones and starts 2 px further left |
| Tab.Audio | TabList | 316, 353, 234, 80 | 29, 203 | parchment #FEE2BE, dark 1–2 px outline, rivets | speaker icon 340, 376, 44, 35; label x 408, cap 384–401 | **kit 03** wide parchment (44, 199, 344 × 106) |
| Tab.Graphics | TabList | 316, 446, 234, 80 | 29, 296 | as Audio | monitor icon 340, 467, 44, 40; label x 408 | kit 03 wide parchment |
| Tab.Controls | TabList | 316, 539, 234, 80 | 29, 389 | as Audio | gears icon 340, 556, 45, 47; label x 408 | kit 03 wide parchment |
| Tab icons | Tabs | see rows | — | Glyph.Dark on parchment, cream on leather | — | gamepad / speaker / monitor / gears glyphs **not in kit** |
| ColumnDivider.Left | Window | 564, 259, 1, 442 | 277, 109 | Rule.Column | — | native Frame |
| ColumnDivider.Right | Window | 993, 259, 2, 442 | 706, 109 | Rule.Column | — | native Frame |
| Header.Gameplay | Window | ink 590, 268, 130, 17 | 303, 118 | per Typography | "GAMEPLAY" (page name, upper case) | native TextLabel x 588 |
| HeaderRule.Left | Window | 588, 298, 263, 2 | 301, 148 | Rule.Heading | — | native Frame |
| Emblem.Tents | Window | 864, 258, 103, 54 | 577, 108 | Sketch line art (tents, trees, rope) | — | **not in kit** (kit 14 leaf emblem 1259, 622 is the same line-art style) |
| SliderRow ×3 | Window | label x 596; track 596, 351 / 419 / 487, 286 × 14; value box 897, 341 / 410 / 477, 74 × 31–33 | — | see below | — | — |
| Slider label | SliderRow | ink x 596, cap tops 319 / 390 / 458 | 309, 169 … | per Typography | "Camera Sensitivity" / "Field of View (FOV)" / "Interaction Range" | native TextLabel |
| Slider track | SliderRow | 596, 351, 286, 14 (row 1); 596, 419, 286, 14; 596, 487, 286, 14 | 309, 201 … | rounded ends (radius 7), 1–2 px dark outline; fill Slider.Fill up to the knob centre, Slider.Track after | — | **kit 05** XP bar track + fill (199, 846 / 199, 779, 890 × 57) recoloured, or native Frames + UICorner; kit 09 slider track (941, 500, 399 × 36) is a parchment track and does not match |
| Slider knob | SliderRow | 23 × 26; mock positions x 786 (y 345), 768 (414), 759 (482) | — | Slider.Knob, rounded ≈ 3 px | — | **not in kit** as drawn (kit 09 knob 1390, 485 is a round orange ball) — native Frame + UIStroke + UICorner, or new art |
| Value box | SliderRow | 897, 341, 74, 32 / 897, 410, 74, 31 / 897, 477, 74, 33 | 610, 191 … | Box.Value | "1.0" / "90" / "6", centred on x 933.5 | native Frame + UIStroke (kit 09 number field 308, 607 has stepper arrows the mock lacks) |
| SectionRule | Window | 587, 527, 385, 1 | 300, 377 | Rule.Section | — | native Frame |
| CheckRow ×2 | Window | box 598, 542, 32, 33 / 597, 598, 33, 33; title x 651 cap 543 / 597; description x 651 cap 564 / 619 | 311, 392 … | Check.Fill (on) | "Auto Loot" / "Automatically pick up nearby items"; "Show Item Notifications" / "Display a message when you pick up items" | **kit 09** checkbox (off 27, 469, 104 × 101; on 154, 469, 105 × 102); kit "on" is parchment with a dark tick, the mock fills the box gold — recolour or new art |
| Language label | Window | ink x 597, cap 671–682 | 310, 521 | per Typography | "Language" | native TextLabel |
| Dropdown | Window | 734, 657, 236, 43 | 447, 507 | Dropdown token, small corner notches/rivets | value "English" x 753; chevron 937, 673, 16, 10 | **kit 09** dropdown (538, 53, 489 × 113: inner rule and a ▼ triangle; mock uses a ⌄ chevron) 9-slice; list rows kit 09 (26, 318 normal / 544, 316 hover / 1065, 319 disabled) |
| Header.KeyBinds | Window | ink 1019, 267, 139, 18 | 732, 117 | per Typography | "KEY BINDS" | native TextLabel |
| HeaderRule.Right | Window | 1018, 298, 188, 2 | 731, 148 | Rule.Heading | — | native Frame |
| Emblem.Signpost | Window | 1222, 247, 127, 57 | 935, 97 | Sketch line art (signpost, rocks, grass) | — | **not in kit** |
| KeyRow ×10 | Window | label x 1031, cap top 318 + 36·i (i = 0…9); key cap 1237, 312 + 35.9·i, 101 × 27; rules y 343 + 36·i at x ≈ 1030–1230 | 744, 162 … | Box.Key, Rule.Key | see list below | native Frame + UIStroke (kit 09 key caps 736–1415 × 605–721 are raised 3D caps; the mock's are flat outlined boxes) |
| BottomRule | Window | 402, 717, 948, 2 | 115, 567 | Rule.Bottom | — | native Frame |
| Sketch.Plant | Window | 314, 672, 226, 118 | 27, 522 | Sketch line art (plant, stones, grass), sits on the window's bottom rule | — | **not in kit** |
| ResetButton | Window | 838, 731, 232, 55 | 551, 581 | parchment #FEDBB0, dark outline, corner lashings | refresh icon 901, 743, 27, 30 (#311205); "RESET" ink 944, 751, 66, 16 | **kit 03** wide parchment (44, 199) + states; lashings and refresh icon **not in kit** |
| ApplyButton | Window | 1084, 730, 261, 56 | 797, 580 | leather #B64720, dark outline, corner lashings | "APPLY" ink 1179, 750, 75, 17, centred on x 1216 | **kit 03** wide leather (44, 63) + states |

Key rows in the mock (label · key text): Move Forward · W; Move Backward · S;
Move Left · A; Move Right · D; Jump · Space; Interact · E; Open Backpack · B;
Open Map · M; Sprint · Left Shift; Crouch · Left Ctrl. Key caps are all 101 px
wide (text centred on x 1287), whatever the text length.

Slider knob positions in the mock (knob centre along the 286 px track): Camera
0.70, FOV 0.64, Interaction Range 0.61 of the track.

## Measurements log

Helpers in `art/ui/kit/analysis/inventory/tools/` (run from the repo root);
`measure_inventory_settings.sh` re-runs all of these into
`art/ui/kit/analysis/settings/measurements.txt`. Crops and overlays from
`ref_tools.py grid/crop` are in `art/ui/kit/analysis/settings/`.

- Window: `px.py 03 row 450 280 300` (dark 286/287–290), `row 450 1370 1392`
  (1379/1380–1383), `col 800 140 160` (149/150–154), `col 800 790 812` (800–805).
- Ornaments: difference mask against the dimmed HUD image (`|03 − (0.30·01 + 6)| >
  60`) at one pixel outside each edge; corner and clasp crops in
  `frame_ornaments.png`.
- Title, gear: `ink.py 03 415,180,260,50 90`, `ink.py 03 325,160,90,80 90`.
- Title rule: `edges.py row 236–240 296 430 180` and `row 237 290 1385 150`.
- Close: `edges.py row 176 1290 1380 70`, `col 1310 160 235 70`.
- Tabs: `edges.py col 330 250 630 70` (259 … 339, 353 … 432, 446 … 525, 539 …
  618), `row 290/380/470/600 300 570 70` (314–550 active, 316–549 inactive).
- Dividers: `edges.py col 564 240 720 200`, `col 993 250 710 205`; bottom rule
  `row 717/718 380 1360 160`; heading rules `px.py col 700 290 304` (298) and
  `edges.py row 298 580 1000 190`, `row 298 1010 1360 190`; section rule
  `edges.py row 527 585 990 212`; key rules `edges.py col 1150 300 680 212`.
- Sliders: `edges.py row 357/426/494 585 980 70` (track 596–881, knobs),
  `col 650 340 375 90` etc. (track rows), `col 797/779/770 … 70` (knob rows).
- Value boxes: `edges.py row 345 885 980 160`, `col 910 335 515 160`.
- Checkboxes: `edges.py row 545 590 640 90`, `col 613 535 640 90`, `row 615`.
- Dropdown: `edges.py row 690 720 980 120`, `col 760 650 705 120`.
- Key caps: `edges.py col 1242 300 680 150`, `row 325 1225 1345 130`.
- Buttons: `edges.py row 745/770 820 1360 70`, `col 880/1150/1300 720 800 70`.
- Bounding boxes of icons, sketches and labels: luminance masks (lum < 90–170),
  excluding the bottom rule for the plant.
- Text: `ink.py` row clusters; colours `col.py` and `ink2.py`; fonts `fontcmp.py`
  and `sbs.py` (`font_compare.txt`, `font_sbs.png`).

## States

| Element | Default | Hover | Pressed | Selected / on | Disabled | Focus (gamepad) | Source |
|---|---|---|---|---|---|---|---|
| Tab | parchment, dark icon + label | kit 03 parchment hover (407, 200: gold rim) | kit 03 parchment pressed (771, 199) | leather, cream icon + label, corner lashings, 2 px larger | — | gold rim | mock + kit 03 |
| Slider | knob at value | knob ×1.1 or gold rim (not in mock) | drag: knob follows the pointer, fill follows the knob, value box updates live | — | — | ←/→ steps the value | implied |
| Value box | shows value | — | — | — | — | — | display only in the mock (open question 6) |
| Checkbox | on: gold fill + tick | gold rim | — | off: kit 09 empty box (27, 469) | — | gold rim | mock (on) + kit 09 (off) |
| Dropdown | closed, chevron down | kit 09 hover row style | opens a list below (or above near the bottom); rows kit 09 list rows | open: chevron up (not in kit) | — | gold rim | implied; list not in mock |
| Key cap | key text | gold rim | capturing: text "…" (current code) | — | fixed keys (Move, Jump: not rebindable) and no keyboard: muted (open question 3) | gold rim | implied + `SettingsPanel` |
| RESET | parchment | kit 03 parchment hover | kit 03 parchment pressed | — | kit 03 parchment disabled (1146, 200) | — | kit 03 |
| APPLY | leather | kit 03 leather hover (409, 63) | kit 03 leather pressed (774, 63) | — | kit 03 leather disabled (1146, 63): nothing to save | — | kit 03 + `SettingsPanel:SetDirty` |
| Close | kit 03 close | kit 03 hover | kit 03 pressed | — | — | — | kit 03 |

## Motion and effects

None shown. The current window opens instantly (`Parchment.Screen`).

## Data and behavior

Real settings: `src/shared/Settings/SettingsRules.luau` (values, ranges,
defaults), `src/shared/Settings/Keybinds.luau` (rebindable keys),
`src/client/Controllers/SettingsController.luau` (draft, APPLY via `SaveSettings`
/ `SaveKeybinds`, RESET of the open tab, close discards the draft) and
`src/client/Hud/SettingsPanel.luau` (current view: five tabs Gameplay, Audio,
Graphics, Controls, Accessibility).

### Mockup controls → real settings

| Mock control | Real setting | Notes |
|---|---|---|
| Camera Sensitivity slider, "1.0" | `cameraSensitivity` (10–100 %, step 1, default 50) | mock shows a multiplier: display `SettingsRules.MouseSensitivity(v)` with one decimal (0.2–2.0; default 1.0). The mock knob sits at 0.70 of the track, which with 10–100 % would be ≈ 73 % (1.5×): mock values are illustrative |
| Field of View (FOV) slider, "90" | **none** | no FOV setting exists |
| Interaction Range slider, "6" | **none**, and not a client choice | reach is set by the server per prompt (`ProximityPrompt.MaxActivationDistance` in `ResourceService`, `DropService`, `StorageService` …); a client value cannot widen it without a gameplay and security change |
| Auto Loot checkbox | **none** | pickups go through prompts / `GroundDrops` |
| Show Item Notifications checkbox | **none** | — |
| Language dropdown | **none** | Roblox picks the locale; the game has no language setting or `LocalizationService` use |
| Key: Move Forward / Backward / Left / Right (W S A D), Jump (Space) | not rebindable | `Keybinds.IsAllowed` keeps W A S D and Space with Roblox; show as fixed (current code shows Move W A S D as fixed caps) |
| Key: Interact · E | `Interact` (default **E**) | matches (defaults changed in GDD 1.24) |
| Key: Open Backpack · B | `Backpack` (default **B**) | matches |
| Key: Open Map · M | `Map` (default **M**) | matches |
| Key: Sprint · Left Shift | `Sprint` (default LeftShift) | matches; display text differs: `Keybinds.Display` → "Shift", `SettingsPanel.KeyText` → "SHIFT", mock "Left Shift" |
| Key: Crouch · Left Ctrl | **removed** (GDD 1.24: the game has no crouch) | row dropped; the key list ends at Sprint |
| RESET / APPLY | `SettingsController` reset (open tab) / apply | match |

### Real settings with no place in the mock (proposed placement, same row styles)

Options, not decisions. Row pitches from the mock: slider row 69 px (label cap
319 → 390 → 458), checkbox row 55–56 px (542 → 598), key row 36 px.

| Real setting | Kind | Proposed tab | Row style |
|---|---|---|---|
| `musicVolume` (0–100, default 75) | number | Audio | slider row, value "75" |
| `effectsVolume` (0–100, default 80) | number | Audio | slider row |
| `subtitles` (default on) | boolean | Audio (and Accessibility, as now) | checkbox row: "Subtitles" / "Show alert sounds as text" (description text needed) |
| `graphicsQuality` (Low / Medium / High) | choice | Graphics | dropdown row (the Language row's style) |
| `uiScale` (0.8–1.4, step 0.1) | number | Graphics (and Accessibility, as now) | slider row, value "1.0×" |
| `invertCamera` | boolean | Gameplay (replacing FOV/Range or after the checkboxes) or Controls | checkbox row |
| `showDamage` | boolean | Gameplay | checkbox row |
| `showNames` | boolean | Gameplay | checkbox row |
| `colourBlindMode` | boolean | Accessibility | checkbox row |
| `reducedMotion` | boolean | Accessibility | checkbox row |
| Replay tutorial | action | Accessibility | RESET-style parchment button |
| Keys `Drop` Q, `Hotbar1–6` 1–6, `Craft` V, `Build` X, `Rotate` R, `Tribe` T, `Progression` P, `Settings` O (plus the five above) | rebindable | Controls (full list); Gameplay right column keeps the mock's 10-row KEY BINDS | key row; the 18 rebindable actions (23 rows with the five fixed movement keys) exceed the 10 rows that fit (y 312–662), so the Controls list needs a ScrollingFrame or two columns of key rows |

Gameplay page with only real settings (one option): Camera Sensitivity slider;
then checkbox rows Show Damage, Show Names, Invert Camera (each needs a
description line); no dropdown. Leaving FOV, Interaction Range, Auto Loot, Show
Item Notifications and Language out removes 2 slider rows, 2 checkbox rows and the
dropdown.

**Accessibility (5th tab)**: the mock has four tabs at pitch 93 (259–618). A
fifth at the same pitch would span 632–712 and overlap the plant sketch
(314–540 × 672–790). Options: (a) five tabs at pitch 72 (tab height ≈ 62) in the
same 259–618 band; (b) keep 80 px tabs and move or drop the plant sketch;
(c) merge Accessibility into Graphics (UI Scale, Colour-blind, Reduced motion)
and Audio (Subtitles) and move Replay tutorial to Gameplay.

### Mock controls with no backing setting (flags)

1. Field of View (FOV) — would need a new setting (camera FieldOfView) and
   server rules entry.
2. Interaction Range — gameplay reach is server-authoritative; not buildable as
   a client preference.
3. Auto Loot — new feature.
4. Show Item Notifications — new setting (pickup toasts).
5. Language — no localization system in the game.
6. Mock default keys E / B / M / Left Ctrl differ from the real defaults
   F / Tab / N / C.

## Asset map

| Asset | Kit source | Size in mock | 9-slice | Status |
|---|---|---|---|---|
| Window frame | kit 04 (frames at 48, 43 / 56, 490; no frame has bottom clasps on both sides) or kit 10 window frame | 1097 × 656 | yes | to slice; clasps may need adding |
| Close ×4 states | kit 03 (342/537/734/933, 329) | 61 × 57 | no | to slice (shared with Inventory) |
| Tab leather / parchment ×states | kit 03 wide buttons rows 1–2 (44/409/774/1146, 63 and 44/407/771/1146, 199) | 237 × 81 / 234 × 80 | yes | to slice |
| Corner lashings (active tab, RESET, APPLY) | not in kit (kit 14 rope knots 391, 250 / 647, 241 are the closest) | ≈ 12 × 12 | no | new art |
| Title gear, tab glyphs (gamepad, speaker, monitor, gears), refresh icon | not in kit (kit 11 gear 328, 334 is full colour) | 63 × 65; 44–50 px; 27 × 30 | no | new art (or recolour) |
| Sketches: tents, signpost, plant | not in kit | 103 × 54, 127 × 57, 226 × 118 | no | new art |
| Slider track + fill | kit 05 XP track/fill (199, 846 / 199, 779) recoloured, or native | 286 × 14 | yes | to slice / native |
| Slider knob | not in kit as drawn | 23 × 26 | no | native or new art |
| Checkbox on / off | kit 09 (154, 469 / 27, 469) — kit "on" differs (no gold fill) | 32 × 33 | no | to slice + recolour |
| Dropdown + list rows | kit 09 (538, 53; rows 26, 318 / 544, 316 / 1065, 319) | 236 × 43 | yes | to slice |
| Value box, key caps | native (kit 09 key caps are 3D) | 74 × 32, 101 × 27 | — | native |
| RESET / APPLY ×states | kit 03 rows 1–2 | 232 × 55, 261 × 56 | yes | to slice |

## Open questions

Each has the default that will be used if unanswered.

1. **Mock-only controls** (FOV, Interaction Range, Auto Loot, Show Item
   Notifications, Language): build them? Default: leave them out; show only
   real settings in the mock's row styles.
2. **Five tabs vs four**: see the Accessibility options above. Default (a): five
   tabs at pitch 72.
3. **Fixed movement keys** (W A S D, Space): show them? Default: show them as in
   the mock but not clickable (muted cap style).
4. **Default keys**: change `Keybinds` defaults to the mock's E / B / M / Left
   Ctrl, or show the real bindings? Default: show the real bindings (caps are
   data-driven).
5. **Key text format**: mock "Left Shift", "Left Ctrl", "Space" (title case,
   full names) vs current "SHIFT" / "CTRL". Default: the mock's format.
6. **Value boxes**: display only, or typed input? Default: display only.
7. **Title ink**: #2C1204 (Inventory) vs #3E1806 (Settings) measured. Default:
   one token, #2C1204.
8. **Right column on other tabs**: KEY BINDS only on Gameplay (as mock)?
   Default: Gameplay shows the 10-row KEY BINDS; Audio / Graphics /
   Accessibility leave the right column for that tab's extra rows; Controls uses
   both columns for the full key list.
9. **Checkbox descriptions** for real settings: text needed for each.
10. **Camera Sensitivity display**: multiplier ("1.0") as the mock, or percent as
    the current code? Default: multiplier.

## Deviations from reference

- Merriweather's lowercase is ~10 % taller than the mock's at equal cap height.
- Title weight may be lighter if Merriweather Black is not available.
- Kit parts differ where noted (slider knob, gold checkbox, flat key caps,
  corner lashings, line-art sketches, dark glyph icons).
