# UI style guide

The single entry point for anyone who makes or changes the game's UI. Read this
first; it is complete enough to work from on its own. Where another document
is the authority, this guide summarises it and links to it:

| Document | Authority for |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | The contract: scaling, ScreenGuis, the Kit's structure, server work, atlas plan, file ownership. **§12 decisions (D1–D26) override everything else**, this guide included |
| [KIT.md](KIT.md) | The Kit's API: every component's constructor, props, methods and states; roles; stand-ins; capture limits |
| Screen specs: [LobbyScreen](LobbyScreen.md), [InventoryScreen](InventoryScreen.md), [SettingsScreen](SettingsScreen.md), [PartyScreen](PartyScreen.md), [PlayScreen](PlayScreen.md), [ForgeScreen](ForgeScreen.md), [CraftingScreen](CraftingScreen.md), [JournalScreen](JournalScreen.md), [ListWindows](ListWindows.md), [HudScreen](HudScreen.md) | Per-screen measurements, element trees, data and deviations |
| [ITEM_ART.md](ITEM_ART.md) | Which art and tint every catalog item draws |
| [`art/ui/kit/CATALOG.md`](../../art/ui/kit/CATALOG.md) | Every `lk_` sprite: source sheet and box, size, 9-slice insets, atlas, role (generated) |
| [`art/reference/ui/lobby/README.md`](../../art/reference/ui/lobby/README.md) | The reference images (mockups and kit sheets) |
| [UI_PROGRESS.md](UI_PROGRESS.md) | Status of every screen and the verification rounds |
| [MANUAL_VALIDATION.md](../MANUAL_VALIDATION.md#rebuilt-ui-the-shared-kit-and-the-seven-lobby-screens) | Checks that need a real device |

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
| [`01_hud.png`](../../art/reference/ui/lobby/01_hud.png) | Lobby HUD layout: currencies and settings (top right), 2 × 3 menu tiles (left), Party panel (right), XP bar and six-slot hotbar (bottom centre); HUD positions under every window (D8) | `Screens/LobbyHud` (no player card: owner decision) |
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
| D11 | Inventory categories | All, Tools, Materials, Food, Plants (only if classifiable from catalog data), Misc | [InventoryScreen](InventoryScreen.md) |
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
| `readyFill` / `readyDot` / `readyEdge` | `#E7E9A2` / `#0CE01A` / `#9DA35A` | Status green | The generic set-status pill (`badge.ready`) and green dot (trade lock, save status); not used by the party since D24 |
| `leaderTint` | `#FFF0D2` | Leader gold (multiply) | Badge "leader" plaque tint; not used by the party since D24 |
| `leaderTag` / `notReadyTint` | `#FDD18A` / `#C8C8C8` | — | Kept from the Ready era; no reader |
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
| Section headers | Shrink to fit (the phone boost never truncates them) |
| Player names (PlayerRow) | Desktop: shrink to fit (`shrinkName`, default true). Touch: keep the size, end in "…", and a pressable row shows the whole name in a tooltip. The lobby HUD keeps one size for every row on phones |
| List row titles | Truncate; a pressable row whose title is cut shows it whole in a tooltip |
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

Screens use these defaults unless their spec measured something else (the
built grids: Inventory slots 91 × 99 at a 99.6 × 107.3 pitch; HUD tiles
88 × 84 at 102 × 94; HUD hotbar pitch 96.4; Play slots 71 × 77 at 82).

### 5.5 Panels and insets

| Variant | Role / art | Use |
|---|---|---|
| `inset` | `panel.inset` (`lk_panel_inset`) | A thin rounded border drawn on parchment: columns, the detail card, the Play map, party rows. The default |
| `card` | `panel.card` (`lk_panel`) | A paper card with leather corners: Party columns, Forge columns, quest details |
| `plaque` | `panel.plaque` (`lk_plaque_small`) | A small paper plaque with centred text (status messages over the map) |
| `plain` | none | Grouping without a frame |
| `SectionHeader` | text + `divider.ink` (default) or `divider.hairline` | Column headings in caps over a rule |

### 5.6 HUD regions and anchoring

The lobby HUD (`Screens/LobbyHud`) pins its regions to the screen edges inside
a root sized to 1/scale of the screen (`Kit.Scale.Hud`):

| Region | Anchor | Place and size (design px) |
|---|---|---|
| Coins, Gems, Settings | top right | 53 from the right, y 70; 302 × 46 (phones: 350 wide, pills 150 / 124) |
| Menu tiles 2 × 3 | left, vertically centred | x 68, centre at 448 / 941 of the height; 190 × 272; tiles 88 × 84 at a 102 × 94 pitch |
| Party panel | top right | 53 from the right, y 258; 294 × 244 |
| XP bar and hotbar | bottom centre | 49 from the bottom; 572 × 124; slot lefts 0, 96, 193, 289, 386, 482 |

The run's HUD uses the same parts and measures from
[`HudLayout.json`](../../src/shared/UI/HudLayout.json) ([HudScreen](HudScreen.md)):
party frames top left (39, 60), compass top centre (y 60, 481 × 46), vitals top
right (53 in, y 60, 315 × 65 rows at a 76 pitch), status, objective and event
cards under them (y 289, 337, 483), tiles at x 68, the same bottom bar, and the
touch attack button bottom right.

While a window is open the HUD stays where M01 has it (D8) under the veil
(`#050403` at 0.30) and, on Medium and High graphics, a size 8 blur.

**Top bar.** `Kit.Scale.TopInset(gui)` measures how far the Roblox top bar
reaches; windows keep below `max(inset, topInsetMin 52)` plus their margin. The
lobby HUD moves its top regions down only when the inset plus 2 px
(`TOP_GAP`) passes the mockup's top margin (`TOP_Y` 60).

### 5.7 Scaling, form factors and safe areas

| Surface | Scale |
|---|---|
| HUD | `HudModel.HudScale`: `min(W / 1672, H / 941)` × the player's UI scale, clamped to 0.34–1.6 (`hudMin`, `hudMax`). On phones and touch tablets × 0.9 (`phoneHud`) and never below 0.5 (`phoneFloor.hud`) |
| Windows | Desktop: `min(fitRoom, canvasFit × UiScale)`, so at 1672 × 941 a window draws at its mockup size; phones and touch tablets: `fitRoom` (fill the room below the top bar, 4 px margin). Clamped to 0.3–1.4 (`windowMin`, `windowMax`). `fitRoom = min((W − 2m) / w, (H − top − 2m) / h)` |
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
`ZIndexBehavior = Sibling`. DisplayOrders (`order`): HUD 1, top stack 5, windows
20, dialogs 30, toasts 40, tooltip 45, subtitles 50. The veil reaches past the
safe area. Notches and the thumbstick and jump zones are device checks.

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
| Slider | A number in a range | knob `plate` / `round`; track `dark` / `paper`; value box | + dragging | [Slider](KIT.md#slider) |
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

### 6.5 Items: art, tint and the no-art placeholder

- Item art comes only from `ItemInfo.Icon(itemId) → (icon name, tint?)` in
  [`src/shared/Items/ItemInfo.luau`](../../src/shared/Items/ItemInfo.luau),
  resolved by `ItemInfo.Sprite`; an item's own `lk_item_<id>` / `item_<id>` sprite
  wins when one exists. [ITEM_ART.md](ITEM_ART.md) lists every item (144 items:
  12 exact, 83 stand-in, 49 none).
- **Tints** are `ImageColor3` multiplies: they darken or shift a hue (iron
  greyer, a berry redder) and can never lighten. Items that need lighter art
  need real art.
- **No art** (D23): the slot, row or detail picture shows a neutral kind glyph
  in `inkSoft` at transparency 0.6 (`Art.STAND_IN_FADE`): a hammer for tools and
  weapons, a backpack for armour, a chest for everything else. It reads as
  "picture missing", never as a real item; the item's name is in the
  `KitItemName` attribute for tooltips and detail cards (`KitStandIn` marks it).
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
  veil sinks clicks to the world and HUD.
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

Re-running writes identical files; existing sprites stay byte-identical when
only new parts are added. `python3 art/ui/slice_lobby_kit.py <name>` builds one
part without touching the manifest (for trying a box).

### 9.2 9-slice insets and edges

- `slice_ = [l, t, r, b]` in output px is the 9-slice inset (corners, rivets and
  ornaments lie inside it); it goes to the manifest `slice`. In Roblox:
  `ScaleType = Slice`, `SliceCenter = Rect(l, t, w − r, h − b)`; the corner scale is
  `clamp(min(drawn / stored), 0.15, 1)` (`HudModel.SliceScale`). Atlas sprites are
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
| `atlas_lk_items` | Item art (`ItemInfo.ART_SPRITES`) | uploaded |
| `atlas_lk_play` | The sheet-21 Play art (D26), 1024 × 256 | new: uploaded by the owner |
| `atlas_island` | The island painting | uploaded |

- **Never change an uploaded atlas.** Once an atlas is uploaded its bytes and
  rects are live: adding a sprite to its group moves other sprites. New art goes
  into a new group (as `atlas_lk_play` did); check the old atlases' sha1 is
  unchanged after packing.
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
  stand-in until it loads, then swaps to the art (no flash on a normal load).
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

---

## 10. Screen catalogue

Captures are written to `art/ui/captures/` (not committed; rebuild with
`python3 art/ui/capture/capture.py <scene>`).

| Screen | File | Controller | Spec | Capture scenes | Capture |
|---|---|---|---|---|---|
| Lobby HUD (M01) | `src/client/Hud/Screens/LobbyHud.luau` | `LobbyHudController` | [LobbyScreen](LobbyScreen.md) | `lobby_hud`, `lobby_hud_states`, `lobby_hud_phone`, `lobby_hud_wide`, `lobby_hud_flow`, `lobby_hud_failed` | `art/ui/captures/lobby_hud.png` |
| Inventory and Vault (M02) | `Screens/InventoryWindow.luau` | `VaultController` (lobby), `InventoryController` (run) | [InventoryScreen](InventoryScreen.md) | `inventory_backpack`, `inventory_vault`, `inventory_states`, `inventory_world`, `inventory_flow` | `art/ui/captures/inventory_backpack.png` |
| Settings (M03) | `Screens/SettingsWindow.luau` | `SettingsController` | [SettingsScreen](SettingsScreen.md) | `settings`, `settings_phone`, `settings_phone_small`, `settings_flow` | `art/ui/captures/settings.png` |
| Party (M04) | `Screens/PartyWindow.luau` | `PartyController` | [PartyScreen](PartyScreen.md) | `party`, `party_states`, `party_phone`, `party_flow` | `art/ui/captures/party.png` |
| Play (M05) | `Screens/PlayWindow.luau` | `PlayController` | [PlayScreen](PlayScreen.md) | `play`, `play_states`, `play_phone` (844 × 390, 2000 × 924), `play_flow` | `art/ui/captures/play.png`, `play_phone.png`, `play_phone_2.png` |
| Ancestral Forge (M06) | `Screens/RecipeWindow.luau` (mode forge) | `ForgeController` | [ForgeScreen](ForgeScreen.md) | `forge`, `forge_phone`, `forge_phone_small`, `forge_flow` | `art/ui/captures/forge.png` |
| Field crafting | `Screens/RecipeWindow.luau` (mode crafting) | `CraftingController` | [CraftingScreen](CraftingScreen.md) | `crafting`, `crafting_flow` | `art/ui/captures/crafting.png` |
| Quest Journal (M07) | `Screens/JournalWindow.luau`, `Hud/IslandMap.luau` | `JournalController` | [JournalScreen](JournalScreen.md) | `journal`, `journal_phone`, `journal_flow` | `art/ui/captures/journal.png` |
| Market, Trade, Progress | `src/client/Hud/ListWindow.luau` | `WalletController`, `TradeController`, `ProgressionController` | [ListWindows](ListWindows.md) | `market_flow`, `trade_flow`, `progress_flow` | `art/ui/captures/market_flow.png` |
| World map | `MapController` + `Hud/IslandMap.luau` | `MapController` | [ListWindows](ListWindows.md#world-map-mapcontroller) | `map_flow` | `art/ui/captures/map_flow.png` |
| In-world HUD | `Hud/Vitals`, `BottomBar`, `PartyFrames`, `Compass`, `ObjectivePanel`, `EventPanel`, `InteractionPrompt`, `DamageNumbers` | `HudController` | [HudScreen](HudScreen.md) | `world_hud`, `world_hud_states`, `world_hud_phone`, `world_hud_wide`, `world_hud_flow` | `art/ui/captures/world_hud.png` |
| Overlays, notices, loot, storage, world menu | `Hud/NoticeCard.luau`, overlay controllers | `NoticeController`, `LootController`, `StorageController`, `WorldMenuController`, … | ARCHITECTURE §4.8 | `notices`, `world_overlays`, `world_overlays_phone`, `world_overlays_flow`, `world_menu` | `art/ui/captures/world_overlays.png` |
| Kit gallery | `src/client/Hud/Kit/*` | — | [KIT](KIT.md) | `kit_gallery` (9 pages), `kit_gallery_failed`, `kit_gallery_flow`, `sprite_loader_flow` | `art/ui/captures/kit_gallery.png` … `kit_gallery_9.png` |

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
- **Phone pages**: `lobby_hud_phone`, `play_phone`, `party_phone`,
  `journal_phone`, `forge_phone`, `settings_phone`, `world_hud_phone`,
  `world_overlays_phone` (844 × 390, touch only, the top bar 58 px down; `play_phone`
  page 2 is a 2000 × 924 phone), `settings_phone_small` and `forge_phone_small`
  (667 × 375); wide: `lobby_hud_wide`, `world_hud_wide` (2560 × 1080). There is
  no tablet scene: copy a phone scene with a touch-only 1024 × 768 or 1280 × 800
  viewport.
- **Failed-art pages**: `lobby_hud_failed`, `kit_gallery_failed`
  (`__failImages = true` makes every image report a failed load).
- **States**: set `DebugState` on a component root (`Kit.Debug.Force`); flow
  scenes fire real events and run leak checks (×20 open / close, instance and
  connection counts).
- **Not drawn** in captures: blur, rotation, CanvasGroup transparency, tweens
  (they finish at once), device safe areas and real touch; Absolute sizes are
  zero.

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
[MANUAL_VALIDATION.md](../MANUAL_VALIDATION.md#rebuilt-ui-the-shared-kit-and-the-seven-lobby-screens).
