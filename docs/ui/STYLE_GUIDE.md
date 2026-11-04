# UI style guide

The single entry point for anyone who makes or changes the game's UI. Read this
first; it is complete enough to work from on its own. Where another document
is the authority, this guide summarises it and links to it:

| Document | Authority for |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | The contract: scaling, ScreenGuis, the Kit's structure, server work, atlas plan, file ownership. **§12 decisions (D1–D30) override everything else**, this guide included |
| [KIT.md](KIT.md) | The Kit's API: every component's constructor, props, methods and states; roles; stand-ins; capture limits |
| Screen specs: [LobbyScreen](LobbyScreen.md), [InventoryScreen](InventoryScreen.md), [SettingsScreen](SettingsScreen.md), [PartyScreen](PartyScreen.md), [PlayScreen](PlayScreen.md), [ForgeScreen](ForgeScreen.md), [CraftingScreen](CraftingScreen.md), [JournalScreen](JournalScreen.md), [ListWindows](ListWindows.md), [HudScreen](HudScreen.md) | Per-screen measurements, element trees, data and deviations |
| [ITEM_ART.md](ITEM_ART.md) | Every catalog item's icon: source PNG and atlas |
| [`art/ui/kit/CATALOG.md`](../../art/ui/kit/CATALOG.md) | Every `lk_` sprite: source sheet and box, size, 9-slice insets, atlas, role (generated) |
| [`art/reference/ui/lobby/README.md`](../../art/reference/ui/lobby/README.md) | The reference images (mockups and kit sheets) |
| [UI_PROGRESS.md](UI_PROGRESS.md) | Status of every screen and the verification rounds |
| [MANUAL_VALIDATION.md](../release/MANUAL_VALIDATION.md#rebuilt-ui-the-shared-kit-and-the-seven-lobby-screens) | Checks that need a real device |

Contents:
1. [Visual identity](#1-visual-identity)
2. [References](#2-references)
3. [Colour palette](#3-colour-palette)
4. [Typography](#4-typography)
5. [Layout and scaling](#5-layout-and-scaling)
6. [Components](#6-components)
7. [Motion and sound](#7-motion-and-sound)
8. [Interaction and input](#8-interaction-and-input)
9. [Art pipeline](#9-art-pipeline)
10. [Screen catalogue](#10-screen-catalogue)
11. [QA](#11-qa)

Terms used throughout:
- **design px**: pixels on the 1672 × 941 mockup canvas. Everything is built in
  design px; one `UIScale` per surface maps it to the screen.
- **token**: a named value in [`src/shared/UI/KitTokens.json`](../../src/shared/UI/KitTokens.json)
  (colour, font, text role, spacing, scale, motion, order, sound).
- **role**: what a piece of art is for (`button.primary`, `icon.playRune`). The
  role table `KitModel.ROLES` in [`src/shared/UI/KitModel.luau`](../../src/shared/UI/KitModel.luau)
  maps roles to `lk_` sprites. Screens name roles, never sprites.
- **`lk_` sprite**: a part sliced from the owner's kit sheets by
  `art/ui/slice_lobby_kit.py` (or built from one by `art/ui/capture/glyphs.py`).
- **M01–M07**: the seven screen mockups; **sheet NN**: kit sheet `NN_*.png`.

---

## 1. Visual identity

### 1.1 The look

Flintborn is a primitive-fantasy survival game on a shattered island, and its UI
looks like the gear of the people who live there: **warm parchment sheets
stitched into stained leather**, held by leather corner pieces, clasps, rivets
and rope, written on in dark brown ink. Accents are few and earned: a gold glow
for what is selected, the honey-yellow of experience, the red, green and orange
of the body's needs, the cold blue of runes and crystals (the Play art of sheet
21). Icons are painted, chunky and outlined, like the mockups' storybook
illustrations.

How screens should feel:
- **Hand-made and tactile.** Every frame, button, slot and bar is a painted
  part from the kit sheets, never a flat rectangle. Plates lift a little under
  the pointer (scale 1.03) and press in (0.96).
- **Calm and readable.** Large ink titles, generous parchment, one clear action
  per window (a single leather primary button, usually at the bottom right).
  Text is dark ink on light paper or cream on leather, never light-on-light.
- **Honest.** Only real data and real features appear (D2, D7, D20): no invented
  difficulty, no placeholder numbers, bars at the true fraction.
- **One world.** The lobby, the run's HUD and every window read as the same
  game, because they are built from the same parts (D15).

### 1.2 The unity rule (D15)

Every screen, including the restyled ones without a mockup, is built **only
from Kit components and `lk_` art**. No screen draws its own frame, button,
slot, bar or tab. Where a mockup shows art the kit lacks, use the closest `lk_`
part and record the deviation (D19); never draw ad-hoc shapes. The island
painting (`pm_map_island`, role `map.island`) is the one painted asset from
outside the `lk_` kit.

### 1.3 Do and don't

| Do | Don't |
|---|---|
| Build from `Kit.*` components and name roles and tokens | Name an `lk_` sprite, a hex colour or a font in screen code |
| Put every word in a live label (localisable, honest) | Bake text into art (the slicer paints words out of plates) |
| Use the parchment / leather pairing: ink on paper, cream on leather | Put cream text on paper, or dark ink on leather |
| Use one primary (leather) action per window; secondary actions on parchment | Use several leather buttons of equal weight side by side (except an answer pair such as Accept / Decline) |
| Use `ink:<id>` flat glyphs on parchment and `white:<id>` on leather | Use full-colour icons as small section glyphs, or flat glyphs as menu tiles |
| Let state art and kit tints show states (hover, pressed, selected glow) | Add native `UIStroke` / `UICorner` / gradients for looks (only stand-ins and the gold glow use them) |
| Build from design numbers | Lay out from `AbsoluteSize` (the capture harness has none, and it changes with the scale) |
| Keep strings to characters Merriweather has ("(Permanent)", "Sprint is now LeftShift") | Use ★ or → in UI strings (Merriweather lacks them) |
| Keep text at or above the phone floors (§4.5) and touch targets at 44 screen px (§8) | Shrink text to fit below 9 screen px |
| Record every deviation from a mockup in the screen's spec and, if it is an owner decision, in ARCHITECTURE §12 | Silently drift from the mockups |
| Use rotation-free art | Rely on `Rotation`, `CanvasGroup` transparency or image gradients for looks (captures cannot show them) |

---

## 2. References

All references live in [`art/reference/ui/lobby/`](../../art/reference/ui/lobby/README.md)
at the design resolution. The mockups set layout, size and colour; the kit
sheets supply the parts. The sheets came from background removal (fills at
alpha 250–254, a faint red or yellow fringe at alpha 1–63), so parts are always
cleaned by the slicer (§9.1), never cut by hand.

### 2.1 Screen mockups (1672 × 941)

| File | Source of truth for | Built as |
|---|---|---|
| [`01_hud.png`](../../art/reference/ui/lobby/01_hud.png) | Lobby HUD layout: currencies (top-right corner; the settings button moved to the bottom-left corner, D27–D30), 2 × 3 menu tiles (left; on phones the run's 3 × 2, D30), Party panel (right), XP bar and six-slot hotbar (bottom centre); HUD positions under every window (D8) | `Screens/LobbyHud` (no player card: owner decision) |
| [`02_inventory.png`](../../art/reference/ui/lobby/02_inventory.png) | The model window: frame, banner header (icon, title, ink underline, close), category column, slot grid, detail card, primary action; also the Play window's chrome (D25) | `Screens/InventoryWindow` |
| [`03_settings.png`](../../art/reference/ui/lobby/03_settings.png) | Large notched tabs, sliders, checkboxes with descriptions, key-bind boxes, Reset / Apply footer | `Screens/SettingsWindow` (D1, D2, D21) |
| [`04_party.png`](../../art/reference/ui/lobby/04_party.png) | Centred header with ornaments, member rows, invite search and list, Party Details | `Screens/PartyWindow` (D5, D6, D17, D24: no Readied Status) |
| [`05_play.png`](../../art/reference/ui/lobby/05_play.png) | Play content: island map with the crater marked, region detail rows, party row, equipment slots, PLAY | `Screens/PlayWindow` with Inventory's chrome (D7, D25) and the sheet-21 art (D26) |
| [`06_forge.png`](../../art/reference/ui/lobby/06_forge.png) | Small-caps title with a handwritten subtitle, recipe cards, requirement cards, quantity stepper, materials list | `Screens/RecipeWindow` (D4, D13) |
| [`07_quest_journal.png`](../../art/reference/ui/lobby/07_quest_journal.png) | Side tabs, quest rows, objective rows with round checks, reward tiles, Claim, quest progress | `Screens/JournalWindow` (D12) |

### 2.2 Kit sheets

Sprite names drop the `lk_` prefix here; CATALOG.md has every box and size.

| Sheet | Source of truth for | Main sprites |
|---|---|---|
| `01_panel_layouts.png` | Inset panels, status dots, small square buttons, portrait and round frames, plaques | `panel_inset`, `dot_*`, `portrait_frame`, `frame_hollow_circle`, `button_square_*`, `plaque_*_bar`, `tile_paper` |
| `02_hollow_frames_hud_buttons.png` | Hollow frames, the blank HUD square, corner pieces, rails, category tab, item tiles (lifted icons) | `button_hud`, `corner_*`, `frame_hollow_*`, `rail_h/v`, `tab_category`, `icon_spear/rope/berries/mushroom/hide/bone` |
| `03_buttons_states.png` | **All button states**: leather (primary) and parchment (secondary) × normal / hover / pressed / disabled, close ×4, square glyph buttons and glyphs, notched plaques, small parchment buttons, the play and check glyphs | `button_leather_*`, `button_paper_*`, `button_close_*`, `button_square_paper`, `glyph_*`, `plaque_notched_*`, `button_paper_small_*`, `glyph_play`, `glyph_check_white` |
| `04_window_frames.png` | The window frame (9-sliced to every window) and the clasped variant | `window_frame`, `window_clasp_frame` |
| `05_slots_badges_bars.png` | Slot states (normal, selected, hover, disabled, locked), number and count badges, XP track | `slot_*`, `slot_hotbar`, `badge_*`, `bar_track`, `plaque_small` |
| `06_menu_icons.png` | Menu tile icons and currency icons, crown, invite glyph | `icon_backpack/portal/scroll/market/anvil/trade/gear/coin/gem/crown`, `glyph_invite`, `button_invite_card` |
| `07_hud_parts.png` | HUD parts: menu tile plate, currency pill, settings button, player card | `tile_frame`, `currency_pill`, `button_settings`, `player_card` |
| `08_stat_bars.png` | Value pill, small tiles (the composed bars are references only) | `pill_value`, `tile_small` |
| `09_controls.png` | Controls: search, dropdown, flat buttons, list rows, checkboxes, toggles, slider, scrollbar, steppers, key caps, tooltip, divider | `search`, `dropdown*`, `button_flat_*`, `row_*`, `checkbox_*`, `toggle_*`, `slider_*`, `scroll_*`, `button_stepper_*`, `stepper_box`, `keycap*`, `tooltip*`, `divider_diamond` |
| `10_inventory_parts.png` | Inventory grid slots, detail card, white backpack tab icon, material icons | `slot_item_normal/selected`, `card_detail`, `icon_backpack_white`, `icon_logs/stones/plank` |
| `11_icons_extra.png` | 20 menu, section and side-tab icons | `icon_party`, `icon_map`, `icon_trophy`, `icon_journal`, `icon_chest`, `icon_hammer`, `icon_magnifier`, `*_alt`, … |
| `12_quest_forge_parts.png` | Inner panel, hollow paper frame, check rows and tiles, plain tile, thin bar frame, tool icons | `panel`, `frame_hollow`, `row_check_*`, `tile_check_*`, `tile_blank`, `bar_frame_thin`, `icon_hatchet`, `icon_pickaxe` |
| `13_popups_notices.png` | Confirm dialog frame, toast plate, lock, cursor | `dialog_frame`, `toast_frame`, `icon_lock`, `icon_cursor` |
| `14_ornaments.png` | Ornaments: clasps, ornate corners, dividers (line, ornament, vertical), plaques, straps, banners, arrow tabs, leaf and rune emblems, rivets, rope | `clasp_*`, `corner_ornate_*`, `divider_*`, `plaque_paper/leather`, `tab_arrow_*`, `emblem_leaf`, `emblem_rune`, … |
| `15_play_party_parts.png` | Play and Party compositions (layout reference), invite button, capped frame, plain parchment map | `button_invite`, `frame_hollow_capped`, `map_parchment` |
| `16_icons_status_items.png` | 20 status, stat and item icons | `icon_heart/lightning/drumstick/star/check/cross/warning/hourglass/clock/gift/log/stone/plant_fiber/stone_axe`, … |
| `17_icons_world.png` | 20 world and map icons (Play detail rows, quests, item stand-ins) | `icon_mountain/tree/cave/campfire/ruin/rocks/crystals/magma_ore/totem/treasure/paw/tusk/map_pin/…` |
| `18_stat_bars_states.png` | Bar fills (red, green, orange, yellow), bar frames | `bar_fill_red/green/orange/yellow`, `bar_frame`, `bar_frame_plain`, `statbar_frame` |
| `19_progress_bars_badges.png` | Blue fill, progress rings, framed status icons | `bar_fill_blue`, `ring_track/half/full`, `icon_flag`, `icon_build` |
| `20_stat_bars_widths.png` | Bar widths (reference only: covered by the 9-sliced fills and frames) | none exported |
| `21_play_rune_stones.png` | **The Play art (D26)**: the stone-framed crystal play arrow and two rune pillars | `icon_play_rune`, `icon_play_rune_small`, `pillar_rune_left`, `pillar_rune_right` |

### 2.3 Decided deviations (ARCHITECTURE §12)

The owner's decisions and reconciled measurements. They override the mockups,
the specs and every other section. Full text:
[ARCHITECTURE §12](ARCHITECTURE.md#12-decisions-resolved-these-override-anything-above).

| # | Topic | Decision (summary) | See |
|---|---|---|---|
| D1 | Settings tabs | 4 tabs as in M03; Accessibility settings move into Graphics and Audio | [SettingsScreen](SettingsScreen.md) |
| D2 | Mockup-only settings | FOV, Interaction Range, Auto Loot, Item Notifications and Language are not shown: only settings that work | [SettingsScreen](SettingsScreen.md) |
| D3 | Ready | Advisory Ready (**superseded by D24**) | — |
| D4 | Forge quantity | Kept: a server-validated batch count 1..`ForgeRules.MAX_BATCH` (10), atomic | [ForgeScreen](ForgeScreen.md) |
| D5 | Party size | Cap 8 ("1/8"); 7 rows at the mockup pitch, the 8th scrolls | [PartyScreen](PartyScreen.md) |
| D6 | Party details | No Play Style row; Join Type "Invite Only"; Created from `createdAt` | [PartyScreen](PartyScreen.md) |
| D7 | Play window | No server selection; only real data rows (no invented difficulty or recommended level) | [PlayScreen](PlayScreen.md) |
| D8 | Dim overlay | Veil `#050403` at transparency 0.30; the HUD stays where M01 has it | §5.6 |
| D9 | Blur | On for Medium and High graphics, size 8; never in captures | §7 |
| D10 | Item descriptions | Short authored lines live in `ItemInfo` (UI layer); otherwise the derived line | [InventoryScreen](InventoryScreen.md) |
| D11 | Inventory categories | All, Tools, Materials, Consumables (once "Food"), Plants (only if classifiable from catalog data), Misc; All on the first tab shows everything the player has | [InventoryScreen](InventoryScreen.md) |
| D12 | Journal side tabs | Book quests, trophy progression, map pin island map, party opens Party | [JournalScreen](JournalScreen.md) |
| D13 | Fonts | Merriweather Heavy titles (Bold fallback), Bold labels, Regular body; Patrick Hand for handwriting; Forge title in fake small caps | §4 |
| D14 | UI sounds | Silent until the owner supplies ids; the Kit keeps the hook | §7 |
| D15 | Unity | Every screen only from Kit components and `lk_` art | §1.2 |
| D16 | Who presses Play | Anyone solo; in a party only the leader (Ready part superseded by D24) | [PlayScreen](PlayScreen.md) |
| D17 | Opening Party | The HUD party panel's title row and add-player button, and the Journal's party tab | [LobbyScreen](LobbyScreen.md) |
| D18 | Ready controls | Ready tags and toggle (**superseded by D24**); invite buttons read "Invited" (disabled paper) while pending — still current | [PartyScreen](PartyScreen.md) |
| D19 | Missing art | Use the closest `lk_` art and list it as a deviation; never ad-hoc shapes; Play's map is the real island art | [KIT §8](KIT.md#8-deviations-from-the-mockups-d19-closest-lk_-art) |
| D20 | XP and counts | Bars show the real fraction, not the mockup's drawn fill | §6 Bar |
| D21 | Controls | No Crouch; defaults Interact E, Backpack B, Map M | [SettingsScreen](SettingsScreen.md) |
| D22 | Fix round 3 | Party views only to changed players; loot and chest takes by stable key with in-flight guard; item art and rarity dot from the server's `catalogId`; Forge `maxCount` counts backpack room; trade invite toast answers directly | [ListWindows](ListWindows.md) |
| D23 | Fix round 4 | The lobby HUD never takes gamepad selection by itself (explicit RB entry, B leaves); items without art show a neutral "picture missing" glyph; two leather tones; one Settings tab rule; the client asks for its party view on start | §6, §8 |
| D24 | Ready removed | No Ready anywhere (server, Party window, HUD dots, Play); only a solo player or the leader presses Play; the leader is marked by the crown alone (no Leader tag) | [PartyScreen](PartyScreen.md), [PlayScreen](PlayScreen.md) |
| D25 | Play window chrome | Inventory's size (1187 × 650), header, clasps and close corner; map in an inset panel; section headings instead of plaques; primary leather PLAY at the bottom right | [PlayScreen](PlayScreen.md) |
| D26 | Play rune art | Sheet 21: the crystal arrow is the Play tile's and the Play header's icon and the PLAY button's glyph; two rune pillars stand at the PLAY button's ends; own atlas `atlas_lk_play`; portal and white glyph until it is uploaded | [PlayScreen](PlayScreen.md#play-rune-art-d26), §9.6 |
| D27 | HUD corner round | World vitals 240 × 50 at pitch 58; no client save-status tag; Coins and Gems alone at the top right (its Settings placement, bottom right by the jump button, is superseded by D28) | [LobbyScreen](LobbyScreen.md), [HudScreen](HudScreen.md) |
| D28 | HUD layout round | World HUD: the compass in Roblox's top bar, level with its buttons and clear of them; vitals, status, objective and world event from the top-right corner down; menu tiles at the left edge. Both HUDs: Settings at the bottom left (its horizontal places and the Settings place are superseded by D29) | [HudScreen](HudScreen.md), [LobbyScreen](LobbyScreen.md) |
| D29 | HUD edges round | The HUD guis draw on the whole screen; the edge rule (24 design px from the screen's edge in the top 30 % / bottom 25 %, at least the device safe inset beside the middle band). Its placements are superseded by D30 | [HudScreen](HudScreen.md), [LobbyScreen](LobbyScreen.md), [SettingsScreen](SettingsScreen.md) |
| D30 | HUD grid round | One grid for both HUDs (§5.6): margin M 24, gap G 12, right-hand column 315 wide; each column stacks with G and keeps one edge by the edge rule applied to the whole column; the shared pieces (tiles, Settings, level/XP bar and hotbar, the right-hand column's top, edge and width) in the same place in both HUDs; Settings M from the left and the bottom; the hotbar M above the bottom edge | [HudScreen](HudScreen.md), [LobbyScreen](LobbyScreen.md), [SettingsScreen](SettingsScreen.md) |

Other recorded deviations (not numbered): the lobby HUD has no player card
(each party row shows level and XP instead; [LobbyScreen](LobbyScreen.md)),
and the per-component art substitutions in [KIT §8](KIT.md#8-deviations-from-the-mockups-d19-closest-lk_-art).

---

## 3. Colour palette

Every colour is a token in `KitTokens.json` `colors`, read with
`Kit.Tokens.Color(key)`. Screens pass token names (`color = "inkSoft"`), never
hex. Most of the look's colour comes from the art itself; the tokens colour
text, native rules and dots, tints laid over art, and the stand-ins drawn
before the art loads (§9.5). Values were sampled as box medians from the
mockups and sheets (ARCHITECTURE §3.2 records the sources).

### 3.1 Parchment

| Token | Hex | Swatch | Role and use |
|---|---|---|---|
| `paper` | `#FCDAB1` | Parchment | Window interior; paper stand-in fill; HUD text outline over the world |
| `paperLight` | `#FEE2BA` | Light parchment | Rows, unselected tabs, key caps; hover and focus stand-in fill |
| `paperDeep` | `#FBD4A5` | Deep parchment | Detail card and search field (M02); no current reader (reference) |
| `paperSelected` | `#FED895` | Selected parchment | Selected row stand-in fill (M06) |
| `paperDisabled` | `#E2CAAE` | Faded parchment | Disabled paper stand-in; label colour on a disabled primary (leather) button |
| `slot` | `#FCDBB3` | Slot parchment | Empty slot stand-in fill |
| `paperEdge` | `#B88654` | Parchment edge | 2 px stroke of paper stand-ins and pills |
| `hairline` | `#EECBA4` | Hairline | The faint 2 px rule (`divider.hairline`): detail rows, section header rules on light cards, list row rules |
| `photoBackdrop` | `#C9B19B` | Photo grey-beige | Behind a transparent headshot when a portrait asks for a backdrop |
| `emptyDot` | `#CC9F77` | Empty slot disc | The flat tan disc of an empty party slot (`portrait.empty`) |
| `railTrack` / `railThumb` | `#E8C49A` / `#9F6F4C` | Thin rail | The 8 px flat scroll rail of the HUD party list and long lists |

### 3.2 Leather

| Token | Hex | Swatch | Role and use |
|---|---|---|---|
| `leather` | `#A53A0F` | Leather | Primary button stand-in fill (M02 EQUIP) |
| `leatherHover` / `leatherPressed` / `leatherDisabled` | `#C03F0D` / `#7C2B08` / `#AA7654` | Leather states | Stand-in fills for those states (sheet 03) |
| `leatherEdge` | `#5D1D06` | Leather rim | 2 px stroke of leather stand-ins |
| `corner` | `#8A2E0F` | Corner leather | M04 corner pieces; no current reader (reference) |
| `rail` | `#290D02` | Window rail | Window stand-in stroke (3 px) |
| `leatherBright` | `#FFFFFF` | Bright tone (multiply) | Leather sprite at its own colour: the bright tone (Settings APPLY, the `play` plaque by default) |
| `leatherTint` | `#DEFFFF` | Primary tone (multiply) | The default tone of every leather sprite (EQUIP, CLAIM, Invite, PLAY in the Play window, close buttons, number badges, clasps) |
| `leatherDark` | `#D5E0FF` | Dark tone (multiply) | The dark tone (Forge FORGE, Party CLOSE) |

The three tones are `ImageColor3` multiplies chosen by `Kit.Button` `tone =
"bright" | "primary" | "dark"` (D23). A multiply can only darken or shift hue, so
mockup leather that is lighter or bluer than the sprite cannot be matched by a
tint (measured ΔE2000: EQUIP 1.5, Invite 2.5, FORGE 0.7, CLOSE 2.2; APPLY 3.2 and
PLAY 4.5 are limited by the art).

### 3.3 Ink and text

| Token | Hex | Swatch | Role and use |
|---|---|---|---|
| `ink` | `#220A01` | Ink | Titles, names, values, HUD text; icon and glyph stand-ins; the ink colour of `ink:` glyphs |
| `inkHeader` | `#340C00` | Header ink | Section headers (`sectionHeader` role) |
| `inkLabel` | `#160C05` | Label ink | Row titles and labels, tabs, counts |
| `inkBody` | `#4E2E12` | Body ink | Descriptions (`body`) |
| `inkSoft` | `#6C4F31` | Soft ink | Secondary text (`bodySoft`, `small`), disabled labels on paper, the faded "picture missing" glyph |
| `inkHand` | `#522307` | Hand ink | Handwritten subtitles (`subtitleHand`) |
| `muted` | `#A58260` | Muted | "Empty Slot" and other muted lines; disabled stand-in glyphs; grey status dot stand-in |
| `placeholder` | `#B4906B` | Placeholder | Search and text field placeholders |
| `cream` | `#FFFFFE` | Cream | Text and glyphs on leather (buttons, badges, the stat bar value) |
| `short` | `#9B1A12` | Short red | A count below what is needed (Forge requirements), refusals, warnings |
| `white` / `black` | `#FFFFFF` / `#000000` | — | Neutral constants; no current colour reader |

### 3.4 Rules, accents and states

| Token | Hex | Swatch | Role and use |
|---|---|---|---|
| `rule` | `#C89868` | Rule | Thin rules (M06) |
| `ruleDark` | `#301200` | Title underline | The ink rule under window titles and section headers (`divider.ink`) |
| `divider` | `#6B3A14` | Divider | Stand-in colour of rule art |
| `glow` | `#FDAA09` | Gold glow | Selected / hover / focus stroke (3 px) on stand-ins; the gamepad focus ring |
| `gold` | `#FDBC07` | Gold | Crown and gold checkbox stand-ins, the ticked ring, gold highlights in lists |
| `checkTint` | `#FFD52A` | Check gold (multiply) | Tint of the ticked checkbox (`variant = "gold"`, M03) |
| `badge` | `#7B2E0D` | Badge leather | Number badge plate (sheet 05); no current colour reader (the art carries it) |
| `toggleOn` | `#698010` | Toggle green | Toggle on stand-in; "on" accents in lists and notices |
| `readyFill` / `readyDot` / `readyEdge` | `#E7E9A2` / `#0CE01A` / `#9DA35A` | Status green | The generic set-status pill (`badge.ready`) and green dot (trade lock); not used by the party since D24 |
| `leaderTint` | `#FFF0D2` | Leader gold (multiply) | Badge "leader" plaque tint; not used by the party since D24 |
| `emptyIconTint` | `#78746E` | Empty grey (multiply) | The icon of an empty stat bar (Vitals), darkened toward grey |
| `veil` | `#050403` | Veil | Full-screen dim behind windows, at transparency 0.30 (D8; `veil.transparency`) |

### 3.5 Bars

| Token | Hex | Swatch | Fill role |
|---|---|---|---|
| `xp` | `#FCA502` | Honey | `bar.fill.yellow` stand-in: XP, slider fill, ring fill |
| `track` | `#59290B` | Dark track | `bar.track` stand-in: the dark well |
| `health` | `#FB371C` | Health red | `bar.fill.red` stand-in; red status dot |
| `stamina` | `#5DB702` | Stamina green | `bar.fill.green` stand-in |
| `food` | `#FC7A04` | Food orange | `bar.fill.orange` stand-in |
| `blue` | `#2997FC` | Timer blue | `bar.fill.blue` stand-in: timers, boss and progress bars |

### 3.6 Rarity

| Token | Hex | Token | Hex |
|---|---|---|---|
| `rarityCommon` | `#A99A88` | `rarityMythic` | `#C9402F` |
| `rarityUncommon` | `#5E9C3A` | `raritySecret` | `#2BB3A8` |
| `rarityRare` | `#3F7FCF` | `rarityExclusive` | `#D9599F` |
| `rarityEpic` | `#8E52C4` | | |
| `rarityLegendary` | `#E09A12` | | |

Rarity is shown as a small flat accent dot (`Kit.Badge` variant `rarity`,
`:SetRarity(name)`) on slots and rows, and always together with the rarity's
name in text (detail cards, tooltips). Colour-blind players get the palette
from `Theme.ColourBlindRarity`; never rely on the colour alone.

### 3.7 Tints laid over art (`tints`)

| Key | Multiply | Used for |
|---|---|---|
| `hover` | 0.93 | Normal art drawn for hover / focus when the role has no hover sprite |
| `pressed` | 0.80 | Pressed without a pressed sprite |
| `disabled` | 0.72 | Disabled, busy (and the Play pillars when PLAY is disabled) |
| `locked` | 0.72 | Locked |

### 3.8 Contrast

WCAG contrast ratios of the flat token pairs (art varies around these):

| Pair | Ratio | Note |
|---|---|---|
| `ink` / `inkLabel` / `inkHeader` on `paper` | 14.2 / 14.5 / 13.2 | Titles and labels: excellent |
| `inkBody` on `paper` | 9.2 | Body text |
| `inkHand` on `paper` | 9.9 | Handwriting |
| `inkSoft` on `paper` | 5.6 | Secondary text: meets 4.5 |
| `short` on `paper` | 6.2 | Short counts |
| `cream` on `leather` | 6.5 | Button labels |
| `cream` on `leatherDisabled` | 3.9 | Disabled labels are meant to recede |
| `muted` on `paper` | 2.7 | Decorative only ("Empty Slot"); never for information you need to read |
| `placeholder` on `paper` | 2.2 | Placeholders only (they vanish on typing) |
| `rule` / `hairline` on `paper` | 1.9 / 1.2 | Rules are structure, not content |

Text over the 3D world (HUD level and XP text, the RB Menu hint) gets a thin
paper outline (§4.4) because the world behind it can be any colour.

---

## 4. Typography

### 4.1 Fonts (`KitTokens.json` `fonts`)

| Key | Family | Weight | Use |
|---|---|---|---|
| `display` | Merriweather | Heavy (900; Roblox falls back to Bold) | Window titles, big detail titles |
| `heading` | Merriweather | Bold | Section headers, names, labels, buttons, values, counts, HUD text |
| `body` | Merriweather | Regular | Descriptions, row labels, small text, placeholders |
| `hand` | Patrick Hand | Regular | The handwritten subtitle (Forge) and other notes |
| `symbol` | Builder Sans | Bold | Stand-in glyphs only (▶ ✓ ✕ ⚙ before the art loads) |

`legacy` names the `Enum.Font` used to measure text, and `weightWidth`
(Regular 1, Bold 1.02, Heavy 1.02) corrects measured widths for weight. The
capture harness ships the faces in `art/ui/fonts` (Merriweather Regular, Bold
and Black for Heavy; Patrick Hand; SIL OFL).

### 4.2 Text roles (`KitTokens.json` `text`)

Sizes are design px. They are a little under the specs' cap-height sizes
because Merriweather runs wider than the mockup face; a screen that must hit a
spec number passes `textSize` / `size`.

| Role | Font | Size | Colour | Caps | Typical use |
|---|---|---|---|---|---|
| `windowTitle` | display | 42 | ink | yes | INVENTORY, PLAY (Inventory and Play pass 44) |
| `detailTitle` | display | 38 | ink | | Big detail titles, plaque text |
| `subtitleHand` | hand | 20 | inkHand | | Forge subtitle |
| `itemTitle` | heading | 27 | ink | | Stone Axe in the detail card |
| `buttonL` | heading | 36 | cream | yes | Large buttons (PLAY passes 34) |
| `button` | heading | 24 | cream | yes | EQUIP, CLAIM, CLOSE |
| `buttonS` | heading | 18 | cream | | Invite, small buttons |
| `tab` / `tabLarge` | heading | 18 / 22 | inkLabel | | Tabs / Settings large tabs |
| `sectionHeader` | heading | 20 | inkHeader | yes | YOUR PARTY, YOUR EQUIPMENT |
| `rowTitle` | heading | 19 | inkLabel | | Row titles, detail labels |
| `rowLabel` | body | 16 | inkLabel | | Setting labels |
| `body` / `bodySoft` | body | 15 | inkBody / inkSoft | | Descriptions / sublabels |
| `small` | body | 13 | inkSoft | | "+1 more in your backpack" |
| `muted` | body | 15 | muted | | "Empty Slot" |
| `value` | heading | 17 | ink | | +10, 1 / 10 |
| `count` | heading | 19 | inkLabel | | Slot counts |
| `hudName` / `hudSmall` | heading | 20 / 15 | ink | | HUD names / LV and XP text |
| `currency` | heading | 19 | ink | | 2,450 |
| `keycap` | heading | 16 | ink | | Key caps |
| `badgeNum` | heading | 14 | cream | | Hotbar 1–6 |
| `tag` | heading | 14 | ink | | Pills and tags |
| `placeholder` | body | 15 | placeholder | | Search placeholders |
| `label` | body | 14 | cream | | Labels on dark backgrounds (galleries, notes) |

### 4.3 Small caps

Merriweather has no small-caps face. `Kit.Text.SmallCaps(text, role?, ratio?)`
(or `smallCaps = true` on Text and Window) builds RichText with the first letter
of each word at the role size and the rest upper-cased at 40 / 46 of it, as M06
draws "ANCESTRAL FORGE" (`smallCapsSizes = {initials, rest}` overrides). Use it
only for the Forge title and titles that copy it; every other caps role simply
upper-cases (`caps` in the role, applied by `Core.SetText`).

### 4.4 Outline

- **No outline on parchment or leather.** Ink on paper and cream on leather
  read on their own (the mockups' soft halo is an image-generator artefact).
- **Text over the 3D world** (HUD level and XP text, the RB Menu hint) uses
  `outline = true`: a 1 px paper `UIStroke` at transparency 0.1 (or a colour
  token, e.g. `outline = "ink"` behind cream).
- **The stat bar value** is cream with a 2 px ink outline, centred over the
  fill and the empty track.

### 4.5 Phones: text boost and floors

- **Boost.** On phones and touch tablets (`Kit.Scale.IsSmallTouch`, §5.7) the
  roles listed in `phoneText.roles` (sectionHeader, body, bodySoft, small,
  muted, rowLabel, rowTitle, value, count, hudName, hudSmall, currency, keycap,
  tag, label, placeholder, buttonS, tab, badgeNum) draw `phoneText.scale` = 1.2×
  larger (`Core.TextBoost`), and at least the phone text floor: the size that
  draws at `phoneText.minPx` = 9 screen px in a typical window
  (`refWindow` 1110 × 690 below a 60 px top bar). Titles and big button labels
  keep their size. The boost re-applies when the form factor changes.
- **Floor for scaled labels.** A label with `scaled = true` shrinks to fit but
  never past its role size and never below `minTextPx` = 9 screen px
  (`Widgets.TextCap`, which follows the parent UIScales).
- Effective sizes at 844 × 390: HUD small text 15 × 1.2 × 0.5 = 9 px, HUD names
  20 × 1.2 × 0.5 = 12 px; in windows (scale about 0.5–0.6) body text 9–11 px,
  row titles 11–13 px, window titles 21–25 px.

### 4.6 Truncate or shrink

| Text | Rule |
|---|---|
| Plain labels (`Core.Label`, `Kit.Text` without `scaled`) | One line, truncated with "…" (`TextTruncate.AtEnd`); `wrap = true` wraps instead |
| Labels that must stay whole (values, detail rows, PLAY, "+n more") | `scaled = true`: shrink to fit, floor 9 screen px |
| Section headers | Shrink to fit (the phone boost never truncates them); give the box room past its rule where a phone boost needs it (Settings' headers reach their emblem) |
| Player names (PlayerRow) | Desktop: shrink to fit (`shrinkName`, default true). Touch: keep the size, end in "…", and a pressable row shows the whole name in a tooltip. The lobby HUD keeps one size for every row on phones; the world HUD's tribe strip widens its cells for the longest name (`party.phone.cellMaxW`), so only a very long name is cut |
| List row titles | Truncate; a pressable row whose title is cut shows it whole in a tooltip. Rows whose names must read whole (Forge and Crafting recipes and materials, Journal quests) pass `fitTitle`: shrink to fit down to `Kit.Core.FitFloor()` (12 design px; the phone text floor on phones), then two balanced lines where the row has room (recipe rows grow to hold them) |
| Button labels | Centred with the icon; the room is the plate minus its rivet margins (`max(16, 0.35 × height)` each side) |

---

## 5. Layout and scaling

### 5.1 The canvas

Everything is built in design px on the **1672 × 941** canvas
(`KitTokens.json` `reference`), from design numbers (the spec's measurements),
never from `AbsoluteSize`. Positions use `rect = {x, y, w, h}` in the parent's
design px, or `size` plus `layoutOrder` inside a layout. Every `lk_` plate is
drawn outset by its sprite's transparent margin (`KitModel.EDGES`), so the
art's visible edge lies exactly on the rect.

### 5.2 Windows

| Window | Size (design px) | Header |
|---|---|---|
| Inventory and Vault | 1187 × 650 | banner: backpack icon, title 44 at x 138, ink underline, clasps right |
| Play | 1187 × 650 (D25) | Inventory's header with the rune play icon (D26) |
| Settings | 1098 × 656 | banner, large tabs |
| Party | 1120 × 631 | centred title with tree ornaments |
| Ancestral Forge / Crafting | 1102 × 680 | banner with small-caps title and handwritten subtitle |
| Quest Journal | 1172 × 688 (1072 frame + 50 px side tabs each side) | banner, side tabs |
| Market, Trade, Progress (ListWindow) | 1180 × 690 | banner, large tabs |
| World map | 1000 × 860 | banner (map icon) |
| ConfirmDialog | 560 × 330 (default) | centred title over an ornate rule |
| Toast | 430 × 84 | plate with emblem icon |

### 5.3 Header anatomy (`Kit.Window`, banner header)

Defaults, in window design px:

| Part | Default | Inventory and Play (measured from M02) |
|---|---|---|
| Header icon | 76 × 76 at (40, 12) (`windowIcon`) | 71 × 77 at (40, 15), art fitted |
| Title | `windowTitle` at x 140 (`windowTitleX`), y 24, 54 tall (y 14, 50 tall with a subtitle) | size 44 at x 138 |
| Subtitle | `subtitleHand` at (142, 62), 26 tall | — |
| Underline | the ink rule with tapering ends, y 80, from x 127 to 8 px before the close button | (113, 78), 995 wide |
| Close button | 60 × 60 (`closeButton`) 22 px in from the right (`closeInset`), y 18 | 60 × 57 at (1103, 18) |
| Clasps | `lk_clasp_*` centred on the frame edge at 20 % and 86 % of the height | right side at 18 % and 90 % |
| Body | from y 100 (`windowHeaderH`), inset 24 (`windowPad`) | — |

The plaque header (M05) puts the title on `window.plaque` (no screen uses it
since D25); the centred header (M04: Party, the world menu) centres the title
with two ornament icons (56 px, 20 px gap) and a full rule. New windows use the
banner header.

### 5.4 Spacing tokens (`KitTokens.json` `space`)

| Token | Value | Token | Value |
|---|---|---|---|
| windowPad | 24 | touchMin | 44 (screen px) |
| colGap | 14 | minTextPx | 9 (screen px) |
| sectionHeaderH | 34 | windowHeaderH | 100 |
| rowParty / rowCategory / rowCard / rowLine | 52 / 64 / 72 / 36 | windowTitleX / windowIcon | 140 / 76 |
| slot / slotPitch | 90 / 99 | closeButton / closeInset | 60 / 22 |
| hotbarSlot / hotbarPitch | 86 / 97 | toastW × toastH, toastGap, toastMax | 430 × 84, 10, 3 |
| tile | 86 | toastClear / toastSlide | 180 / 24 |
| fallbackCorner / Slot / Window | 8 / 6 / 10 | tooltipMaxW / tooltipPad | 300 / 14 |
| fallbackStroke / Window | 2 / 3 | longPress | 0.5 s |
| glowStroke / focusStroke / focusOutset | 3 / 3 / 3 | windowMargin / phoneMargin | 8 / 4 |
| pillCorner | 7 | topInsetMin | 52 |
| slotGlowOutset | 3 | debounce | 0.15 s |
| minTextDesign | 12 (design px) | | |

`minTextDesign` is the least size the kit draws a label at when it picks the
size or a screen passes one (`Core.TextFloor`); a smaller size is raised to it.

Screens use these defaults unless their spec measured something else (the
built grids: Inventory slots 91 × 91 (square) at a 99.6 pitch; HUD tiles
88 × 84 at 102 × 94; HUD hotbar slots 89 × 89 at a 96.4 pitch; Play slots
77 × 77 at 85). Hotbar and loadout slots are always square.

### 5.5 Panels and insets

| Variant | Role / art | Use |
|---|---|---|
| `inset` | `panel.inset` (`lk_panel_inset`) | A thin rounded border drawn on parchment: columns, the detail card, the Play map, party rows. The default |
| `card` | `panel.card` (`lk_panel`) | A paper card with leather corners: Party columns, Forge columns, quest details |
| `plaque` | `panel.plaque` (`lk_plaque_small`) | A small paper plaque with centred text (status messages over the map) |
| `plain` | none | Grouping without a frame |
| `SectionHeader` | text + `divider.ink` (default) or `divider.hairline` | Column headings in caps over a rule |

### 5.6 HUD regions and anchoring: the HUD grid (D30)

Both HUDs (the lobby's `Screens/LobbyHud` and the run's `HudController`)
place their regions on **one grid**, defined once in
[`HudLayout.json`](../../src/shared/UI/HudLayout.json):

| Token (`grid`, `gear`) | Value (design px) | Means |
|---|---|---|
| `grid.margin` (**M**) | 24 (12 screen px on a phone at HUD scale 0.5) | between the screen's edge and every region pinned to it: top, left, right, bottom |
| `grid.gap` (**G**) | 12 (6 on a phone) | between stacked or neighbouring HUD pieces |
| `grid.column` | 315 | the width of the right-hand column's pieces in both HUDs |
| `grid.topBand` / `bottomBand` | 0.30 / 0.25 | the corner bands of the edge rule (§5.7) |
| `gear` | 52 × 52 (square: the tile frame with the ink gears glyph), ring gap 12, pad 44 | the ⚙ both HUDs draw |

A region names its column (`"column": "right"`, `"left"` or `"bottom"`)
instead of carrying offsets; `Hud/Layout.ForScreen` resolves it, and
`Hud/Layout.PlaceColumns` (the one placement both HUDs call) stacks each
column's shown pieces from its top with G between them (a hidden piece takes
no room) and keeps the whole column to one edge (§5.7). The rects are the
art's visible edges (kit plates are drawn outset by their sprites' margins,
§5.1).

| Region | Lobby | Run | Place |
|---|---|---|---|
| Right-hand column | Coins + Gems row (165 + G + 138), Party panel (315 × 244) | vitals (315 × 50 rows, pitch 58), status plaques (right-aligned), FIND EXTRACTION, world event (desktop and tablets) | from M below the screen's top (below the bar only when its right-hand area reaches over), G apart, 315 wide, one right edge: the first piece is the top-right corner piece |
| Left-hand column | menu tiles | tribe frames (desktop), menu tiles, world event (phones) | one left edge; stacked pieces from G under Roblox's top-bar buttons, G apart |
| Menu tiles | the run's grid | `tiles` | desktop and tablets 2 × 3, 88 × 84 at a 102 × 94 pitch, centred at 0.476 of the height; phones 3 × 2, 80 × 80 at 88 × 86, G under Roblox's buttons |
| Level/XP bar and hotbar | the run's group | `bottom` | 572 × 124, centred, M above the bottom edge; the XP bar (356) centred over the hotbar, level text 7 px left of it, XP text 11 px right, XP pop-ups over it; the lobby's update notice centred, G above it |
| Settings | the run's ⚙ | `gear` | the bottom-left corner: M from the left and M from the bottom; above Roblox's thumbstick ring only where the ring reaches the corner (a phone without a side inset) (`HudModel.GearCorner`) |
| Compass | — | `compass` | centred in Roblox's top bar's row, clear of its buttons and the right-hand column (D28); the phone tribe strip centred under it |
| Boost list | — | `BoostHudController.Position` | G right of the ⚙ (or its touch pad), its foot M above the bottom edge |

While a window is open the HUD stays where M01 has it (D8) under the veil
(`#050403` at 0.30) and, on Medium and High graphics, a size 8 blur.

**Top bar.** `Kit.Scale.TopInset(gui)` measures how far the Roblox top bar
reaches; windows keep below `max(inset, topInsetMin 52)` plus their margin.
`HudModel.TopRow` gives the bar's button row (44 px buttons ending 2 px above
the inset: y 12–56 under a 58 px bar). The right-hand columns start M from
the top (on a phone that is level with the buttons' top), below the bar only
when the bar's right-hand area (`GuiService.TopbarInset`) ends before them;
the left-hand stacks start G under the buttons' foot; the compass sits on the
buttons' centre line (`HudController.PlaceTop`, `LobbyHud:_place`).

### 5.7 Scaling, form factors and safe areas

| Surface | Scale |
|---|---|
| HUD | `HudModel.HudScale`: `min(W / 1672, H / 941)` × the player's UI scale, clamped to 0.34–1.6 (`hudMin`, `hudMax`). On phones and touch tablets × 0.9 (`phoneHud`) and never below 0.5 (`phoneFloor.hud`) |
| Windows | Desktop: `min(fitRoom, canvasFit × UiScale)`, so at 1672 × 941 a window draws at its mockup size; phones and touch tablets: `fitRoom` (fill the room below the top bar, 4 px margin), but a small window (a dialog) draws at most `scale.touchSmallMax` = 1.25 × the scale of a typical window (`phoneText.refWindow`), so it is not blown up to fill the screen (`KitModel.WindowScale`). Clamped to 0.3–1.4 (`windowMin`, `windowMax`). `fitRoom = min((W − 2m) / w, (H − top − 2m) / h)` |
| Toasts, tooltips, notice cards | HUD scale, never below 0.6 on phones (`phoneFloor.overlay`) |

**Form factors** (`Kit.Scale.FormFactor`): `phone` = touch only and the viewport
under 500 px tall (`phoneHeight`); `tablet` = touch only and the short side under
900 (`tabletShortSide`); `desktop` = everything with a keyboard, consoles and big
touch screens. `IsSmallTouch` (phone or tablet) switches on window fill, the
text boost and the HUD floor; `OnFormFactorChanged` re-applies them when the
screen or the input devices change. Consoles get the desktop layout with
gamepad navigation (§8).

**Example window scales** (printed by `play_phone`): Play (1187 × 650) at
844 × 390: 0.508; at 2000 × 924: 0.982; at the 1672 × 941 design size on
desktop: 1.

**Safe areas.** Every Kit ScreenGui has `IgnoreGuiInset = true`,
`ScreenInsets = DeviceSafeInsets`, `ResetOnSpawn = false` and
`ZIndexBehavior = Sibling`, except the HUD guis (D29, below). DisplayOrders
(`order`): HUD 1, top stack 5, windows 20, dialogs 30, toasts 40, tooltip 45,
subtitles 50. The veil reaches past the safe area. Real notches and the
thumbstick and jump zones stay device checks.

**Screen edges and safe areas (D29, per column since D30).** The HUD guis (`FlintbornHud`,
`FlintbornHudOverlay`, `FlintbornLobbyHud`, `FlintbornSettingsButton`) draw on
the whole screen (`Kit.Scale.FullScreen`: `ScreenInsets = None`,
`ClipToDeviceSafeArea = false`), so their corner regions can reach the
screen's edges. `Kit.Scale.SafeInsets()` measures the device safe area (two
hidden probe guis, one `None`, one `DeviceSafeInsets`) and
`Kit.Scale.OnSafeInsetsChanged` re-places the HUDs when it changes. The edge
rule (`HudModel.EdgeGap` with the grid, applied by `Hud/Layout.PlaceColumns`
to a whole column, so its pieces keep one edge):

| Where the column lies (every shown piece, its whole height) | Gap from the screen's physical edge, for the whole column |
|---|---|
| In the top 30 % or the bottom 25 % of the screen (the corner bands: no notch or island there on a phone held sideways) | M, 24 design px (12 pt on a phone at HUD scale 0.5) |
| Reaching the middle band anywhere | M or the device safe inset on that side, whichever is larger (47 pt on a notched 844 × 390 iPhone) |

So a column never splits: on a notched iPhone the vitals stand at the 47 pt
inset with the objective under them (D29 had the vitals at the edge and the
objective at the inset), and the lobby's pills with the Party panel. Corner
pieces that stand alone (Settings, the hotbar group) are in a corner band and
keep M. Desktop and wide screens have no insets, so every edge region sits at
M there. Roblox's own buttons and touch controls sit inside the safe area
(`HudModel.Thumbstick` takes the insets).

**Touch hit pads.** Every interactive component's invisible hit button grows
until it covers at least 44 screen px at the component's real scale (the art
does not change). Neighbouring controls must leave room for their pads (§8).

---

## 6. Components

Every component is `Kit.X.new(parent, props)` with `.root`, `:Destroy()`,
callbacks as props and setters as methods; the full API is in
[KIT §6](KIT.md#6-components). States (§6.1) are shared.

### 6.1 States

| State | Trigger | Drawn as |
|---|---|---|
| normal | — | normal art |
| hover | mouse over, only while the mouse is the input | hover art, else normal art × 0.93; tiles, slots, icon buttons, pills and play plaques also scale to 1.03 |
| focused | gamepad selection | normal art with the gold focus ring (3 px, 3 px outside the visible control); scales to 1.03 where hover does |
| pressed | mouse button, touch or gamepad A held | pressed art, else × 0.80; scale 0.96, Back-out release |
| selected | `:SetSelected(true)` | selected art: gold glow on slots, tiles, rows and side tabs; leather on tabs |
| disabled | `:SetEnabled(false)` | disabled art, else × 0.72; not interactive or selectable |
| locked | `:SetState("locked")` | locked art (slots) or disabled art + lock; still selectable, a press explains why |
| busy | `:SetBusy(true)` | disabled art, label "…", not interactive |
| capturing / open / empty | key cap waiting / dropdown open / empty slot or row | hover art (pulsing label) / hover art / normal art, no item |

Priority when several hold: disabled > busy > locked > capturing > selected >
pressed > open > focused > hover > empty > normal. Force any state with the
`DebugState` attribute (§11).

### 6.2 Catalogue

| Component | Use it for | Variants | States | KIT.md |
|---|---|---|---|---|
| Screen | Every modal window or dialog layer (veil, blur, one-at-a-time, Escape / B) | layer `window` / `dialog` | open, closed | [Screen](KIT.md#screen) |
| Window | The frame, header and close button of a window | header `banner` (default), `plaque`, `centered`; clasps; small caps; subtitle | — | [Window](KIT.md#window) |
| Panel / SectionHeader | Columns and cards inside a window; column headings | `inset`, `card`, `plaque`, `plain`; header rule `ink` / `hairline` | — | [Panel](KIT.md#panel--sectionheader) |
| Button | Text actions | `primary` (leather), `secondary` (parchment), `play` / `playSecondary` (notched plaque), `flat`; sizes s 42 / m 58 / l 76; tone bright / primary / dark; optional icon | normal, hover, pressed, disabled, busy, focused | [Button](KIT.md#button) |
| IconButton | Icon-only actions | `close`, `paper`, `leather`, `small`, `round`, `hud`, `tile`, `settings`, `invite`, `plus`, `minus`, `dropdown`; optional badge | + selected | [IconButton](KIT.md#iconbutton) |
| Tab / TabGroup | Switching pages or filters | `category` (arrow plate when selected), `arrow`, `horizontal`, `large`, `side` | + selected; count plaque | [Tab](KIT.md#tab--tabgroup) |
| Slot | Items: grid, hotbar, loadout | `item` (inventory), `hotbar` (number badge); count text or plaque; Permanent mark | + selected, locked, empty | [Slot](KIT.md#slot) |
| Bar | Values and progress | fills `xp`, `health`, `stamina`, `food`, `blue`, …; frames `track`, `none`, `well`, `thin`, `stat` | value (eased) | [Bar](KIT.md#bar), [§13](KIT.md#13-stat-bar) |
| Ring | Circular progress (sheet 19) | — | value | [§11](KIT.md#11-polish-round) |
| Checkbox | On/off with a label and description | `box`, `gold`, `tile`, `ring` | + checked | [Checkbox](KIT.md#checkbox) |
| Toggle | A bare on/off switch | — | + on | [Toggle](KIT.md#toggle) |
| Slider | A number in a range | one look everywhere: dark track, yellow fill, parchment knob with leather corners (drawn at its own aspect); value box | + dragging | [Slider](KIT.md#slider) |
| Dropdown | One choice of a short list | `openUp` | + open | [Dropdown](KIT.md#dropdown) |
| SearchBox / TextField | Filtering lists / typing a code | with or without clear ✕ | normal, focused, disabled | [SearchBox](KIT.md#searchbox) |
| Stepper | Quantities | paper or leather buttons; `allLabel` | − / + disable at limits | [Stepper](KIT.md#stepper) |
| KeyCap | Key and button prompts, rebinding | `cap`, `flat`; gamepad key and hide-on-touch | + capturing | [KeyCap](KIT.md#keycap) |
| Divider | Rules | `rule`, `ink`, `hairline`, `ornate`, `diamond`, `vertical` | — | [Divider](KIT.md#divider) |
| ListRow | Lists of things to pick | `row`, `card`, `soft`, `line`, `option`; icon, subtitle, value, chevron | + selected, locked | [ListRow](KIT.md#listrow) |
| PlayerRow | People | full or `compact`; crown, level and XP bar, action button, empty slot | + selected, empty | [PlayerRow](KIT.md#playerrow) |
| Badge | Counts, numbers, status | `count`, `number`, `new`, `dot`, `dotRed/Yellow/Green/Grey`, `rarity`, `ready`, `notReady`, `leader` | — | [Badge](KIT.md#badge) |
| CurrencyPill | Coins and Gems | coins, gems | hover, pressed | [CurrencyPill](KIT.md#currencypill) |
| Portrait | Headshots | `square`, `round`, `none`; backdrop | — | [Portrait](KIT.md#portrait) |
| Picture | A role drawn as a picture | any role (`hud.leaf`, `panel.party`, `map.island`, `deco.pillarLeft`, …) | normal, disabled | [§10](KIT.md#10-fix-round-new-props-and-roles-all-additive-defaults-noted) |
| Icon / ItemIcon | Menu, status and world icons; item art | icon id, role name or `ink:` / `white:` glyph; item id | — | [Icon](KIT.md#icon--itemicon) |
| Text | Every label | any text role; small caps; outline | — | [Text](KIT.md#text) |
| Scroll | Lists longer than their box | vertical / horizontal; kit rail or `thin` rail | — | [Scroll](KIT.md#scroll) |
| Toast | Short notices | `quest`, `item`, `info`, `warn`; actions | in, out | [Toast](KIT.md#toast) |
| ConfirmDialog | Questions before an action | danger, hold-to-confirm, custom body | busy | [ConfirmDialog](KIT.md#confirmdialog) |
| Tooltip | Names and reasons | side top / right | shown | [Tooltip](KIT.md#tooltip) |

### 6.3 Button tone and variant rules

- **One primary per window**: the leather `primary` button for the window's
  main action (EQUIP, STORE IN VAULT, CLAIM, FORGE, APPLY, PLAY). Secondary
  actions (RESET, CANCEL, DROP) are parchment `secondary`.
- **Tones** (D23): `primary` is the default (EQUIP, CLAIM, Invite, the Play
  window's PLAY); `bright` for the brightest mockup leather (Settings APPLY;
  the `play` plaque defaults to it); `dark` for the darkest (Forge FORGE,
  Party CLOSE on the notched plaque).
- **Notched plaques** (`play`, `playSecondary`) are for a big centred footer
  action (Party CLOSE, the world menu's Play); they have no hover art and lift
  to 1.03 instead.
- **Disabled**: the primary plate stays leather (desaturated) with
  `paperDisabled` text; parchment and plaques turn pale with `inkSoft` text.
- **Invited** (D18): `SetVariant("secondary")`, `SetLabel("Invited")`,
  `SetEnabled(false)` while the invite is pending.
- **Answer pairs** (trade invite toast): Accept primary, Decline secondary,
  side by side.

### 6.4 Icons and glyphs

| Kind | Where | How |
|---|---|---|
| Full-colour icons (`lk_icon_*`) | Menu tiles, HUD buttons, window headers, toasts, detail rows, items | `icon = "backpack"` resolves `lk_icon_backpack` |
| Role icons | Art that has a role and a fallback (the Play rune art) | `icon = "icon.playRune"` / `"mark.playRune"` (§9.6) |
| Flat ink glyphs (`ink:<id>`) | Section header and tab glyphs on parchment; the "picture missing" glyph | `lk_glyph_ink_<id>`, built by `glyphs.py` |
| Flat white glyphs (`white:<id>`) | The same glyphs on leather (a selected tab, a button) | `lk_glyph_white_<id>` |
| Square-button glyphs | + − ✓ ✕ and arrows on `paper` / `leather` / `small` / `round` squares | square buttons prefer `lk_glyph_<id>`; cream on leather |
| White art | `lk_glyph_play`, `lk_glyph_check_white`, `lk_icon_backpack_white` | drawn white on leather, tinted ink on paper |

### 6.5 Items: icons, stand-ins and the no-art placeholder

- **Every item draws its own icon, and only that**: `ItemInfo.ItemSprite(itemId)`
  → `lk_item_<CatalogId>`, built from the owner's item art by
  [`art/ui/items/build_item_icons.py`](../../art/ui/items/build_item_icons.py)
  (§9.7) and packed into `atlas_lk_items4_1` / `_2`. Every place an item is
  shown (inventory and vault slots, the hotbars, list rows in the Market,
  Trade, loot and storage windows, recipe rows, the Inventory detail card and
  the Forge / Crafting picture) draws it through `Kit.ItemIcon` (`Art.ItemIcon`
  → `Art.Icon`). There is no older item art behind it (the `ItemInfo.Icon`
  kit-art table is gone; [ITEM_ART.md](ITEM_ART.md) lists every icon).
- **While the icon's atlas loads** (§9.5; past `Art.GRACE`, so a normal load
  never flashes) the picture shows the item's **kind glyph** (`Art.KindGlyph`: ⚒ tools and weapons, ▤ armour, ◇ everything else;
  `Art.ITEM_KIND_GLYPH`), in `inkSoft` at the no-art fade, never a letter. The
  icon replaces it by itself the moment `SpriteLoader` reports the atlas loaded
  (`SpriteLoader.OnState`): nothing is rebuilt and no window has to be
  reopened. The `item_icons_flow` capture checks this for slots, the hotbar,
  list rows, recipe rows, the detail card and the Forge picture.
- **Hero boxes** (the Forge / Crafting picture, the Inventory detail card) draw
  the slot icon until the item's own 356 px hero copy `lk_item_<id>__hi` has
  loaded on that client, which then takes its place in the same label
  (`Widgets`, §9.7).
- **No art** (D23): an id that is not a catalog item (or an icon missing from
  the sprite table) shows the neutral kind glyph
  in `inkSoft` at transparency 0.6 (`Art.STAND_IN_FADE`): a hammer for tools and
  weapons, a backpack for armour, a chest for everything else. It reads as
  "picture missing", never as a real item; the item's name is in the
  `KitItemName` attribute for tooltips and detail cards (`KitStandIn` marks it).
- **Dimming** (a locked slot, row or recipe picture) uses `Kit.Dim(root,
  amount)`, which composes with each part's resting fade (`KitRestFade`) instead
  of overwriting it, so a dimmed and then undimmed stand-in returns to its 0.6
  fade, never to solid ink. Never set `ImageTransparency` to 0 to undim.
- Rarity: a flat rarity dot (§3.6) plus the rarity name in text.

---

## 7. Motion and sound

### 7.1 Motion tokens (`KitTokens.json` `motion`)

| Key | Time | Easing | Used by |
|---|---|---|---|
| hover | 0.12 s | Quad Out | hover tint and scale to 1.03 (`scale.hover`) |
| press | 0.07 s | Quad Out | press scale to 0.96 (`scale.pressed`) |
| release | 0.18 s | Back Out | back to 1 after a press |
| windowOpen | 0.22 s | Quint Out | window UIScale 0.94 (`scale.windowFrom`) → 1, veil fade in, blur in |
| windowClose | 0.15 s | Quad In | the reverse; then the gui is disabled |
| toastIn / toastOut | 0.25 s / 0.2 s | Quint Out / Quad In | toasts slide 24 px and fade |
| bar | 0.25 s | Quad Out | bar fills ease to the new value |
| count | 0.4 s | Quad Out | currency count-up |
| knob | 0.12 s | Quad Out | toggle knob |
| pulse | 0.6 s | Sine InOut | a key cap waiting for a key |
| reducedFade | 0.1 s | Linear | the cap on fades under reduced motion |

Rules: `Kit.Motion.Play(instance, key, goal)` cancels a running tween on the same
property first, so states never fight. Only scale, position and transparency
move; nothing rotates. Status text fades in with the `hover` timing.

**Reduced motion** (`Theme.ReducedMotion()`, the game setting, or
`GuiService.ReducedMotionEnabled`): every move and scale lands at once and fades
take at most 0.1 s.

**Blur** (D9): one shared `Lighting.KitBlur` (size 8, `blur.size`) eases in with
the first open window and out with the last, only when the graphics quality is
automatic or at least level 4 (`blur.minQuality`); it is ref-counted and always
removed on close. Captures never show it.

### 7.2 Sound

`Kit.Sound.Play(key)` with keys `hover`, `click`, `open`, `close`, `error`,
`success`. The ids in `KitTokens.json` `sounds` are empty, so the UI is silent
until the owner supplies sounds (D14); sounds are pooled under SoundService so
the Effects volume applies. Hover sounds play only with a mouse, never on touch.

---

## 8. Interaction and input

`Kit.Input.Type()` reports the input in use ("mouse", "keyboard", "touch",
"gamepad"; the last input decides, so a touchscreen laptop follows what was
used last). Components and screens adapt to it live (`Kit.Input.Watch`).

| Input | Rules |
|---|---|
| Mouse | Hover shows only while the mouse is the input; tooltips on hover; a press shows while the button is held and acts on release; leaving the control or releasing elsewhere cancels it |
| Keyboard | Key hints and the hotbar's 1–6 badges show with a mouse or keyboard only; Escape closes the top layer (Roblox may also take Escape for its menu; B is the dependable back) |
| Touch | No hover; every control's hit pad reaches 44 screen px; text boxes grow to 44 px tall; tooltips on a 0.5 s hold; keyboard hints hidden (`Kit.Input.Hint` returns nil); a single "Respond" button replaces small ✓ / ✕ pairs whose pads would overlap |
| Gamepad | The gold focus ring marks the selection (Roblox's default selection box is replaced); A presses; B closes the top layer; d-pad / stick moves between `NextSelection*` neighbours each screen sets; tooltips on selection; key caps show button names (`Kit.Input.GAMEPAD_NAMES`: A, B, X, Y, LB, RB, LT, RT, LS, RS, View, Menu, D-Up …) |

- **One window at a time.** `Kit.Modal` opens one window layer: opening a
  window closes the one before; a ConfirmDialog stacks on the dialog layer
  above it. Escape and gamepad B close the top layer (the dialog first). The
  veil sinks clicks to the world and HUD; a mouse click on it, outside the
  window, closes the top layer the same way (`Kit.Screen` prop
  `dismissOutside = false` keeps a layer that must not close by accident). A
  tap on it does nothing: on touch screens the X is in easy reach.
- **Default selection.** When a window opens and the last input is a gamepad,
  its default control is selected (Play: the PLAY button); closing it restores
  the selection that was there before.
- **The lobby HUD never selects itself** (D23). A controller player walks with
  the stick; RB (`ButtonR1`, free in the lobby) moves selection onto the menu
  tiles (`Kit.Input.EnterHud`, the "RB Menu" hint shows over the tiles while a
  gamepad is in use) and B leaves HUD navigation.
- **Keybind hints by input** (`Kit.Input.Hint(keyboardText, gamepadKey)`):
  keyboard text with a keyboard or mouse, the gamepad button's name with a
  gamepad, nothing on touch. KeyCap `gamepadKey` / `hideOnTouch` switch by
  themselves.
- **Neighbours' pads.** Leave enough room between controls that their 44 px
  pads do not overlap at the phone scale; where they cannot, the higher one
  wins, so put the riskier action (PLAY, DROP) where an overlap cannot trigger
  it.

---

## 9. Art pipeline

### 9.1 Kit sheets to `lk_` sprites

[`art/ui/slice_lobby_kit.py`](../../art/ui/slice_lobby_kit.py) (numpy and
Pillow, deterministic) turns each part, a hard-coded box on a sheet in
`PARTS`, into `art/ui/sprites/lk_<name>.png`, its `manifest.json` entry, the
contact sheets and CATALOG.md. For every part:

1. **Crop** the box plus 8 px (`PAD`).
2. **Paint-out ops** (when listed): `erase` / `erase_mask` repaint baked text,
   digits or icons from the surrounding paper or leather (push-pull fill plus
   that material's grain); `lift` takes an icon off its tile (flood fill of the
   backing up to the icon's dark outline); `clear`, `copy`, `mirror_x`,
   `crop_opaque` for special parts.
3. **Clean alpha** (`clean_alpha`): drop the keying fringe (alpha below 64,
   `LO` 0.25) and loose specks (components below `min_area` or 0.4 % of the
   largest, or whose centre lies outside the box; `keep = "largest"` keeps one
   component); fill pin-holes up to 150 px (`hole_max`; `fill = "all"` / `"none"`);
   make interiors fully opaque (the sheets hold fills at 250–254); re-ramp
   alpha between 0.25 and 0.85 so the silhouette keeps a 1–2 px anti-aliased
   edge.
4. **Decontaminate edges**: semi-transparent rim pixels and filled holes take
   the colour of the nearest solid pixel (no red or yellow tint).
5. **Resize** with premultiplied Lanczos to the on-screen size: `scale` (output /
   source) or `size` (the long side). Icons are stored at about 1.5 × their
   largest on-screen size (menu icons `ICON` 112, world icons 96).
6. **Recolour** a flat fill to the mockup's colour when `recolor` is set.
7. **Finish**: snap alpha (below 3 / 255 → 0, above 0.96 → 1), bleed colour 24 px
   into the transparent pixels (bilinear filtering never pulls in black or
   red), and keep a 2 px transparent margin (`EDGE_PAD`).

**High-resolution copies.** Parts listed in `HIRES` also write
`lk_<name>__hi.png` at f = min(2, the sheet's headroom over the 1× export):
corners and edges at f, a nine-slice's stretched middle kept at its 1× length.
The 1× sprite's manifest entry gains `"hi": "<name>__hi"`; the copy's entry
holds its own `w`/`h`/`slice`/`rect` in its own pixels plus `scale` (f) and
`of`. `Widgets` draws the copy only where the art is magnified (more than 0.75
design px per art px) and the copy's atlas has an id, so pieces keep their
design size and a stale id never draws the wrong rects (`UiAssets.Placement`).
`Kit.Icon` and `Kit.ItemIcon` never draw an icon past 1.0 design px per pixel
of the art that draws at that size (`maxScale`, `Art.Capped`: the 1× art and
the copies that take over below that limit; pass `false` to opt out), so in
slots, rows, tiles and the Journal illustration a box bigger than the art
centres it.

**Hero copies.** The hero boxes (the Forge and Crafting picture, 254 design px,
and the Inventory detail card's 152 × 166 icon) pass `maxScale = false`: every
item fills the box, the same size as any other. Only items are drawn there, so
only the item icons have hero copies (`lk_item_<id>__hi`, 356 px: `HERO_PX`, the
Forge box at the 1440p window scale 1.4), built by `build_item_icons.py` (§9.7);
the kit parts have none. A copy of scale s ≤ 2.1 draws once the art is
magnified past 0.75; a sharper one past `UiAssets.HiFrom(s)` = max(1, s / 2.8),
so it is never shrunk more than 2× at 1440p: the hero copies draw in the hero
boxes only, and slots, rows and the Journal illustration keep their 1× (or 2×)
art.

Re-running writes identical files; existing sprites stay byte-identical when
only new parts are added. `python3 art/ui/slice_lobby_kit.py <name>` builds one
part without touching the manifest (for trying a box).

### 9.2 9-slice insets and edges

- `slice_ = [l, t, r, b]` in output px is the 9-slice inset (corners, rivets and
  ornaments lie inside it); it goes to the manifest `slice`. In Roblox:
  `ScaleType = Slice`, `SliceCenter = Rect(l, t, w − r, h − b)`; the corner scale is
  `clamp(min(drawn / stored), 0.15, 1)` (`HudModel.SliceScale`; its optional
  `artScale` divides by a high-resolution copy's f). Atlas sprites are
  drawn as nine plain pieces with whole-pixel corners (phones mis-draw Roblox's
  slice of an atlas rectangle).
- Some parts stretch along one axis only (`ONE_AXIS`: search, dropdown, bars,
  rails, arrow tabs…): keep their stored height (or width).
- `KitModel.EDGES` holds each plate's transparent margin round its visible edge;
  regenerate with `python3 art/ui/capture/capture.py --edges` after a plate
  changes size.

### 9.3 Flat glyphs

[`art/ui/capture/glyphs.py`](../../art/ui/capture/glyphs.py) recolours existing
icons into flat glyphs: `lk_glyph_ink_<id>` (`#220A01`) and `lk_glyph_white_<id>`
(`#FFFFFE`), "solid" (the whole silhouette) or "line" (the dark drawing only).
Where the sheets have no drawing, the closest icon stands in (gamepad from the
compass, speaker from the speech bubble, monitor from the map, refresh from the
compass arrow, info from "!"; KIT §8). It prints the manifest and GROUPS entries
for new glyphs.

### 9.4 Atlases and upload

- [`art/ui/pack_atlas.py`](../../art/ui/pack_atlas.py) packs the sprites listed
  in `GROUPS` into atlas images (at most 1024 px a side, 4 px gap, shelf packing
  with a guillotine fallback, power-of-two height) and writes each packed
  sprite's `atlas` and `rect` into `manifest.json`. Phones refuse bursts of image
  downloads, so a screen should need one or two atlases.

| Atlas | Holds | Status |
|---|---|---|
| `atlas_lk_lobby` | What the lobby HUD draws on join plus what every window shares (slots, rows, small buttons, dots, badges, bars, the window frame) | uploaded |
| `atlas_lk_window` | Window parts and controls (buttons and states, tabs, fields, checkboxes, toggles, sliders, tooltips, dialog) | uploaded |
| `atlas_lk_icons` | Menu, section and status icons; ink and white glyphs | uploaded |
| `atlas_lk_items` | Kit icons cut from the kit sheets' item drawings (heart, star, warning, tusk, build, campfire, hatchet, …). Items no longer draw them; menus, stat rows, events, notices and the Journal use them as icons, so the uploaded atlas stays as it is | uploaded |
| `atlas_lk_play` | The sheet-21 Play art (D26), 1024 × 256 | new: uploaded by the owner |
| `atlas_lk_build` | `lk_icon_build2`, the build icon lifted whole (the Build tile, Field Crafting's header; `lk_icon_build`'s planks are cut off), 1024 × 128 (KitModel `icon.build`, `lk_icon_build` as its fallback) | uploaded |
| `atlas_island` | The island painting | uploaded |
| `atlas_lk_lobby_hi` | High-resolution copies: frames, bars, slots, paper buttons, pills, tile frame, round frame, toast, panel | new: uploaded by the owner |
| `atlas_lk_window_hi` | High-resolution copies: dialog, leather buttons, tabs, plaques, inset panel, steppers, clasps, play glyph | new: uploaded by the owner |
| `atlas_lk_journal_hi` | High-resolution Journal illustrations | new: uploaded by the owner |
| `atlas_lk_items4_1`, `atlas_lk_items4_2` | Every catalog item's own 110 px icon (`lk_item_<id>`, §9.7): 81 and 63 icons (replace `atlas_lk_items3_*`, which replaced `atlas_lk_items2_*`: the red Adamantine art, then the redrawn spears) | uploaded |
| (no atlas) `lk_item_<id>__hi` | The 144 item icons' 356 px hero copies, one image each | uploaded |
| `atlas_island_hi_1_1` … `_2_2` | The island painting at 2040 px as 2 × 2 tiles | new: uploaded by the owner |

- **Never change an uploaded atlas.** Once an atlas is uploaded its bytes and
  rects are live: adding a sprite to its group moves other sprites. New art goes
  into a new group (as `atlas_lk_play` did); check the old atlases' sha1 is
  unchanged after packing. A group nothing draws any more may be removed whole
  (its sprites, PNGs and ids with it): the parchment-era atlases (`atlas_lobby`,
  `atlas_hud`, `atlas_ui`, `atlas_pieces`, `atlas_map`, `atlas_window_*`), their
  `pm_*` sprites and the first HUD's unprefixed sprites went that way, as did
  the kit item art's hero copies (`atlas_lk_items_hi_*`, never switched on).
  Their uploads stay on Roblox and in `uploaded_decals.json`, and
  `--resolve` never brings an id back for a name the manifest no longer lists.
- **High-resolution sheets are additive.** `Widgets` draws a `__hi` copy only
  once its sheet has actually loaded on that client (`SpriteLoader.State`);
  until then, and for good if it never loads, the 1x art draws, and the sheet is
  fetched in the background. A plain (not 9-sliced) image whose copy loads
  later takes the copy in the same label (an item's hero copy in the Forge
  picture). The kit's high-resolution sheet ids (`atlas_lk_*_hi`,
  `atlas_island_hi_*`) are blank in `UiAssetIds.json` (their uploads are
  recorded in `uploaded_decals.json`): after they were switched on, the UI on a
  phone lost its parchment art, so they stay off until they are re-enabled and
  checked on a phone. The item hero images (`lk_item_<id>__hi`) are on.
- An empty id `""` in `UiAssetIds.json` is a placeholder for an atlas not
  uploaded yet; the game and captures draw the 1× art meanwhile, and
  `--dry-run --atlases` lists the pending atlases. `pack_atlas.py` refuses to
  change an atlas that has an id.
- `python3 scripts/roblox_upload_ui_assets.py --sprites` syncs sizes, insets,
  atlas and rect from the manifest into
  [`src/shared/UI/UiSprites.json`](../../src/shared/UI/UiSprites.json) (local, no
  key).
- The **upload** is the owner's step: `--dry-run --only <atlas>` lists it;
  `--upload --only <atlas>` (with `ROBLOX_API_KEY` and `ROBLOX_CREATOR_USER_ID` or
  `ROBLOX_CREATOR_GROUP_ID`) uploads it and writes the id into
  [`src/shared/UI/UiAssetIds.json`](../../src/shared/UI/UiAssetIds.json) and
  `art/ui/uploaded_decals.json`. Upload atlases by name with `--only`; the loose
  `lk_` PNGs stay as per-sprite fallbacks and are not uploaded one by one.
- At run time `UiAssets` reads both JSON files; `Widgets.HasArt(name)` is true
  when the sprite or its atlas has an id, and `Widgets.Sprite` draws it as its
  atlas rectangle. `SpriteLoader` fetches images one at a time, on-screen ones
  first, and prefetches closed menus' atlases.

### 9.5 Before and while art loads

- A role whose sprite has no uploaded id (or whose image fails) draws the
  Kit's **stand-in** for its `material`: paper / leather / slot / window plates
  with a brown stroke and rounded corners, tracks and fills as pills, rules as
  lines, glyphs and icons as a symbol in ink (KIT §7). Hover, focus and
  selection add the 3 px gold glow.
- An uploaded image that has not arrived after `Art.GRACE` (2 s) shows the
  stand-in until it loads, then swaps to the art by itself (no flash on a
  normal load, no rebuild). An item's stand-in is its kind glyph (§6.5).
- A role with a **`fallback`** icon draws that icon while its own sprite has no
  art (the Play rune icon falls back to the portal, the crystal glyph to the
  white play glyph).
- Material **`deco`** draws nothing until its art arrives (the rune pillars).
- Captures preview un-uploaded PNGs, so the art look is checked before upload;
  `--uploaded-only` shows the fallback look, and the `*_failed` scenes show
  every image failing.

### 9.6 Adding a part end to end (worked example: the sheet-21 Play art)

1. **Reference.** Save the owner's sheet as the next number in
   `art/reference/ui/lobby/kit/` (`21_play_rune_stones.png`, 1448 × 1086, RGBA) and
   add its row to the [README](../../art/reference/ui/lobby/README.md).
2. **Find the boxes.** Label the alpha ≥ 0.5 components (`label()` in the slicer
   does it): left pillar (108, 75, 636, 1063), arrow (559, 317, 967, 853), right
   pillar (857, 76, 1382, 1063).
3. **Add parts** to `PARTS` in `slice_lobby_kit.py`, sized for their use and
   stored at about 1.5 ×: `icon_play_rune` (size 112, the tile's ~60–70 px and the
   header's 77 px), `icon_play_rune_small` (size 60, the button's 40 px glyph),
   `pillar_rune_left` / `_right` (size 156: the pillars draw 96 px tall, 1.6 × the
   60 px button), each `keep = "largest"` with a role and note for the catalog.
4. **Slice.** `python3 art/ui/slice_lobby_kit.py`, then check `git status`: only
   the new PNGs, appended manifest entries, CATALOG.md and the contact sheets
   change; every existing `lk_` PNG stays byte-identical. Look at the new parts
   on light and dark backgrounds (no fringe, no halo).
5. **Roles.** Add them to `KitModel.ROLES`: `icon.playRune` and `mark.playRune`
   (material `glyph`, glyph ▶, `fallback` to the art already uploaded), and
   `deco.pillarLeft` / `deco.pillarRight` (material `deco`, `edge = false`). Add
   them to `tests/luau/kit_roles.spec.luau`, and stand-in glyphs to `Art.GLYPHS`.
6. **Use them** in screens by role: `LobbyHudModel.TILES` Play icon
   `"icon.playRune"`; PlayWindow's header `icon = "icon.playRune"`, the PLAY
   button `icon = "mark.playRune"`, and two `Kit.Picture`s for the pillars placed
   from design numbers (PlayScreen.md), dimmed with the button.
7. **Atlas.** Add a new group (`atlas_lk_play`) to `pack_atlas.py`, run it, check
   the four uploaded `atlas_lk_*.png` sha1 are unchanged, re-run the slicer (the
   catalog's Atlas column), and run
   `python3 scripts/roblox_upload_ui_assets.py --sprites`.
8. **Verify.** Captures of every affected scene, desktop and phone, plus
   `--uploaded-only` (the fallback) and the failed pages (§11);
   `python3 tests/luau/run.py`; `stylua --check src tests/luau`;
   `python3 scripts/roblox_upload_ui_assets.py --dry-run --only atlas_lk_play`
   lists exactly the new atlas.
9. **Record** the decision in ARCHITECTURE §12 (D26) and the screen specs, then
   hand the atlas to the owner to upload.

### 9.7 Item icons

The owner's item art is one 512 × 512 RGBA PNG per catalog item in
`art/ui/items/source/` (named after the display name in kebab case, "/" as
"and": `bone-legs-and-boots.png`). It is source art for the icon build only;
the game draws the packed atlases.
[`art/ui/items/ICONS.json`](../../art/ui/items/ICONS.json) maps each catalog id
to its display name, family, PNG and atlas group;
[`build_item_icons.py`](../../art/ui/items/build_item_icons.py) (deterministic,
two or three minutes) makes, for each item:

- the alpha clean-up of §9.1 step 3 at the source's resolution (only true
  pin-holes, up to 8 px, are filled; gaps between berries or legs stay open);
- a square around the trimmed art, its long side holding the art with a 4 px
  (slot) margin, resampled with premultiplied Lanczos to **`lk_item_<id>`**, 110
  px (the biggest slot draws an item 67 design px, 94 px at 1440p), and from the
  same source pixels to **`lk_item_<id>__hi`**, 356 px (`HERO_PX`), the slot
  icon's `hi` copy (scale 3.24, so it draws past `HiFrom` 1.16: in the Forge /
  Crafting picture and the Inventory detail card only); both downscales, no
  recolour, then the §9.1 step 7 finish (alpha snap, colour bleed);
- the manifest entries; the slot icons packed into the ICONS.json groups
  (`pack_atlas.item_groups`), "" placeholders in `UiAssetIds.json` for the new
  atlases and every hero image, and `UiSprites.json` synced.

The hero copies are **images of their own**, not atlases (a 1024 atlas holds
eight; 18 sheets would choke phones): `Widgets` gates a copy without an atlas
on its own image (`readyImage`), so it draws only once loaded, fetched in the
background when a hero box first wants it; the box shows the slot icon until
then and the copy takes its place in the same label when it arrives. Upload
with
`python3 scripts/roblox_upload_ui_assets.py --upload --only 'atlas_lk_items4_*,lk_item_*__hi'`
(146 images; throttling waits as asked, an interrupted run continues when
re-run). Never move an item between uploaded atlases: a new item goes into a
new group in ICONS.json.

The slot icons are **not** gated: `Kit.ItemIcon` draws `lk_item_<id>` from the
moment the atlas has an id, with the item's kind glyph standing in until the
atlas has loaded on that client (§6.5). An earlier build held the new atlases
back until loaded and drew the older kit art meanwhile; slots built before the
atlas arrived never redrew, so phones kept the old icons. That gate and the
older art are gone. The `item_icons_flow` capture scene forces the atlases
pending, then loaded, and checks every kind of item picture swaps from its kind
glyph to its icon with nothing rebuilt, and the hero copy taking over the Forge
picture; the `item_info` spec checks every catalog item has its icon and hero
copy in `UiSprites.json`.

---

## 10. Screen catalogue

Captures are written to `art/ui/captures/` (not committed; rebuild with
`python3 art/ui/capture/capture.py <scene>`).

| Screen | File | Controller | Spec | Capture scenes | Capture |
|---|---|---|---|---|---|
| Lobby HUD (M01; the HUD grid, §5.6) | `src/client/Hud/Screens/LobbyHud.luau`, `Hud/Layout.luau` (grid placement shared with the run) | `LobbyHudController` | [LobbyScreen](LobbyScreen.md) | `lobby_hud`, `lobby_hud_states`, `lobby_hud_phone` (844 × 390 notched, 667 × 375, 2000 × 924), `lobby_hud_wide`, `lobby_hud_flow`, `lobby_hud_failed` | `art/ui/captures/lobby_hud.png` |
| Inventory and Vault (M02) | `Screens/InventoryWindow.luau` | `VaultController` (lobby), `InventoryController` (run) | [InventoryScreen](InventoryScreen.md) | `inventory_backpack`, `inventory_vault`, `inventory_states`, `inventory_world`, `inventory_flow`, `inventory_phone` | `art/ui/captures/inventory_backpack.png` |
| Settings (M03) | `Screens/SettingsWindow.luau` | `SettingsController` | [SettingsScreen](SettingsScreen.md) | `settings`, `settings_phone`, `settings_phone_small`, `settings_flow` | `art/ui/captures/settings.png` |
| Party (M04) | `Screens/PartyWindow.luau` | `PartyController` | [PartyScreen](PartyScreen.md) | `party`, `party_states`, `party_phone`, `party_flow` | `art/ui/captures/party.png` |
| Play (M05) | `Screens/PlayWindow.luau` | `PlayController` | [PlayScreen](PlayScreen.md) | `play`, `play_states`, `play_phone` (844 × 390, 2000 × 924), `play_flow` | `art/ui/captures/play.png`, `play_phone.png`, `play_phone_2.png` |
| Ancestral Forge (M06) | `Screens/RecipeWindow.luau` (mode forge) | `ForgeController` | [ForgeScreen](ForgeScreen.md) | `forge`, `forge_phone`, `forge_phone_small`, `forge_flow` | `art/ui/captures/forge.png` |
| Field crafting | `Screens/RecipeWindow.luau` (mode crafting) | `CraftingController` | [CraftingScreen](CraftingScreen.md) | `crafting`, `crafting_flow` | `art/ui/captures/crafting.png` |
| Quest Journal (M07) | `Screens/JournalWindow.luau`, `Hud/IslandMap.luau` | `JournalController` | [JournalScreen](JournalScreen.md) | `journal`, `journal_phone`, `journal_flow` | `art/ui/captures/journal.png` |
| Market, Trade, Progress | `src/client/Hud/ListWindow.luau` | `WalletController`, `TradeController`, `ProgressionController` | [ListWindows](ListWindows.md) | `market_flow`, `trade_flow`, `progress_flow` | `art/ui/captures/market_flow.png` |
| World map | `MapController` + `Hud/IslandMap.luau` | `MapController` | [ListWindows](ListWindows.md#world-map-mapcontroller) | `map_flow` | `art/ui/captures/map_flow.png` |
| In-world HUD (the HUD grid, §5.6) | `Hud/Vitals`, `BottomBar`, `PartyFrames`, `Compass`, `ObjectivePanel`, `EventPanel`, `InteractionPrompt`, `DamageNumbers`, `OverheadHealth`, `Hud/Layout.luau`; the ⚙ (`SettingsController`) and boost list (`BoostHudController`) on the same grid | `HudController` | [HudScreen](HudScreen.md) | `world_hud`, `world_hud_states`, `world_hud_phone` (844 × 390 notched, 667 × 375, 2000 × 924), `world_hud_wide`, `world_hud_flow` (each world page also builds the lobby HUD at its screen and checks the shared pieces match), `overhead_health` (the bars over hurt players) | `art/ui/captures/world_hud.png`, `world_hud_phone.png` |
| Overlays, notices, loot, storage, world menu | `Hud/NoticeCard.luau`, overlay controllers | `NoticeController`, `LootController`, `StorageController`, `WorldMenuController`, … | ARCHITECTURE §4.8 | `notices`, `world_overlays`, `world_overlays_phone`, `world_overlays_flow`, `world_menu` | `art/ui/captures/world_overlays.png` |
| Kit gallery | `src/client/Hud/Kit/*` | — | [KIT](KIT.md) | `kit_gallery` (9 pages), `kit_gallery_failed`, `kit_gallery_flow`, `sprite_loader_flow`, `item_icons_flow` (item icons: kind glyph while pending, icon once loaded) | `art/ui/captures/kit_gallery.png` … `kit_gallery_9.png` |

Screens are display only: they take data through setters and report presses
through callbacks; controllers fetch data and call remotes.

---

## 11. QA

### 11.1 The capture harness

[`art/ui/capture/capture.py`](../../art/ui/capture/capture.py) bundles the game's
own Luau (`src/shared`, `src/client`), a headless GUI runtime (`gui_env.luau`) and
a scene from `art/ui/capture/scenes/`, runs it with the standalone `luau` CLI and
renders what the scene dumps (`render.py`, with the real fonts). Needs `luau` on
PATH, numpy and Pillow.

```bash
python3 art/ui/capture/capture.py play                    # -> art/ui/captures/play.png (+ _2, _3 … per page)
python3 art/ui/capture/capture.py play --page 2           # one page
python3 art/ui/capture/capture.py play --uploaded-only --suffix _fallback   # only uploaded art: the fallback look
python3 art/ui/capture/capture.py settings --compare art/reference/ui/lobby/03_settings.png [--crop x y w h]
python3 art/ui/capture/capture.py --all                   # every scene
python3 art/ui/capture/capture.py --edges                 # print KitModel.EDGES
python3 art/ui/capture/capture.py journal --out x.png --bg none
```

- `--compare` writes `<name>_compare.png` (side by side) and `<name>_overlay.png`
  (50 % blend) and prints the mean colour difference.
- **Phone pages**: `lobby_hud_phone`, `play_phone`, `party_phone`, `inventory_phone`,
  `journal_phone`, `forge_phone`, `settings_phone`, `world_hud_phone`,
  `world_overlays_phone` (844 × 390, touch only, the top bar 58 px down; `play_phone`
  page 2 is a 2000 × 924 phone; `world_hud_phone` and `lobby_hud_phone` add
  667 × 375 and 2000 × 924 pages), `settings_phone_small` and `forge_phone_small`
  (667 × 375); wide: `lobby_hud_wide`, `world_hud_wide` (2560 × 1080). There is
  no tablet scene: copy a phone scene with a touch-only 1024 × 768 or 1280 × 800
  viewport.
- **Roblox's own controls** (`__robloxChrome` in `gui_env.luau`): the HUD scenes
  draw stand-ins for the top-bar buttons (the logo and the menu / chat pill,
  reaching x 212 as on a notched 844 × 390 iPhone) and set
  `GuiService.TopbarInset` to match; touch pages add the jump button and the
  classic thumbstick ring. **Device safe area** (D29): `opts.insets =
  __NOTCHED_PHONE` (47 px at each side) models a notched iPhone held sideways:
  Roblox's controls move inside the safe area, a notch stand-in is drawn at the
  left edge and the side strips beside the middle band are shaded; the 844 × 390
  pages of `world_hud_phone` and `lobby_hud_phone` use it, and the flow scenes
  feed the same insets through Kit.Scale's probe guis.
  `art/ui/capture/hud_checks.luau` (bundled with every scene) places the HUDs
  as the controllers do (`__placeWorldHud`, `__worldGear`, `__placeLobbyHud`)
  and checks the HUD grid (D30, ±1 px): the corner pieces M from both their
  edges (the top-right column's first piece, Settings, the hotbar's foot),
  every column's pieces on one edge (the edge rule for the whole column) with
  the widths the spec names and G between stacked pieces, the desktop tiles
  centred, the XP bar centred over the hotbar; that every region reaching the
  middle band keeps inside the insets; that no HUD region overlaps another,
  leaves the screen or meets those controls or a notch (`__checkWorldHud`,
  `__checkLobbyHud`); and, on every world page, that a lobby HUD built at the
  same screen puts the shared pieces (tile grid, Settings, bottom group, the
  right-hand column's top piece and the second piece's edge and width) in the
  same place. `__checkBoosts` checks the boost list beside the ⚙. A failed
  check fails the scene.
- **Failed-art pages**: `lobby_hud_failed`, `kit_gallery_failed`
  (`__failImages = true` makes every image report a failed load).
- **States**: set `DebugState` on a component root (`Kit.Debug.Force`); flow
  scenes fire real events and run leak checks (×20 open / close, instance and
  connection counts).
- **Not drawn** in captures: blur, rotation, CanvasGroup transparency, tweens
  (they finish at once), real notches and rounded screen corners (only their
  modelled insets) and real touch; Absolute sizes are zero.

### 11.2 Verification checklist

For every screen or change:

- [ ] Captures of every affected scene, desktop and phone (and wide where it
      has one), read by eye; every state page.
- [ ] Positions within **±2 design px** of the mockup or spec (frames, tabs,
      grids, buttons, rules), checked with `--compare` overlays.
- [ ] Flat colours within **ΔE2000 ≤ 3** of the mockup's median for each element
      (cards, pills, tracks, leather plates); whole-screen means include the
      world behind the veil and are only a trend.
- [ ] Text **≥ 9 screen px** on phones (844 × 390 and 667 × 375); the phone scenes
      print their smallest text.
- [ ] Touch targets **≥ 44 screen px**, and neighbouring pads do not overlap at
      the phone scale.
- [ ] Nothing under the Roblox top bar, off-screen or clipped by a frame.
- [ ] Gamepad: the default selection, `NextSelection*` neighbours, B closes, the
      selection comes back.
- [ ] The fallback (`--uploaded-only`) and failed pages look acceptable.
- [ ] `python3 tests/luau/run.py` passes; `stylua --check src tests/luau` is clean;
      the kit gallery's `Kit.Art.Missing()` assertion holds.
- [ ] Art changes: existing `lk_` PNGs and uploaded atlases byte-identical;
      `--dry-run --only <atlas>` lists exactly the new atlas.
- [ ] Deviations recorded in the screen spec and, for owner decisions,
      ARCHITECTURE §12.

### 11.3 Device checks

Blur, motion, safe areas, the toast lane, real touch, gamepad focus and how the
uploaded art draws on phones need a device: the list is in
[MANUAL_VALIDATION.md](../release/MANUAL_VALIDATION.md#rebuilt-ui-the-shared-kit-and-the-seven-lobby-screens).
