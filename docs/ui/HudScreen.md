# In-world HUD spec (Kit)

The HUD players see during a run. There is no mockup: it is built only from the
shared Kit (`docs/ui/KIT.md`; ARCHITECTURE §4.8, D15) so it reads as the same
game as the lobby HUD (`art/ui/captures/lobby_hud.png`). The hotbar, XP bar and
menu tiles use the lobby HUD's parts and measures. Places and sizes live in
`src/shared/UI/HudLayout.json` (design px on the 1672 × 941 canvas) on the
HUD grid both HUDs share (D30, STYLE_GUIDE §5.6: margin M 24, gap G 12,
right-hand column 315 wide); art, type and colours come only from the Kit.
Status: Built.

Code: `Controllers/HudController.luau` (data and input; `HudController.Mount`
builds every region), `Hud/Vitals`, `BottomBar`, `PartyFrames`, `Compass`,
`ObjectivePanel`, `EventPanel`, `InteractionPrompt`, `DamageNumbers`;
`Controllers/CombatController.luau` (touch attack, hit marker, bow draw).

## Screen setup

- `FlintbornHud`: DisplayOrder `hud` (1), `IgnoreGuiInset`, the whole screen
  (`Kit.Scale.FullScreen`: `ScreenInsets = None`, `ClipToDeviceSafeArea =
  false`; D29), `ResetOnSpawn = false`, enabled only while
  `SessionStates.IsAtRisk`.
- `FlintbornHudOverlay` (order 2, always on, the whole screen too): XP pop-ups
  above the XP bar, so they also show outside a run.
- The HUD grid (D30, `HudController.PlaceTop` with the screen from
  `Kit.Scale.HudScreen`, re-run when `Kit.Scale.OnSafeInsetsChanged` fires
  and when a column piece shows, hides or changes height): the regions name
  their column in `HudLayout.json` and `Hud/Layout.PlaceColumns` (the
  lobby's placement too) stacks each column's shown pieces with G between
  them and keeps the whole column to one edge: M from the screen's side
  while every piece lies in the top 30 % or the bottom 25 % of the screen,
  else M or the device safe inset (`Kit.Scale.SafeInsets`), whichever is
  larger, where a notch can be.
- Root scale `Kit.Scale.Hud` (HudModel.HudScale, × 0.9 on touch phones and
  tablets, never below the `phoneFloor.hud` 0.5).
- The top bar (D28, D30, `HudController.TopBar` / `PlaceTop`, re-run when
  the scale, the screen or `GuiService.TopbarInset` changes): the compass
  sits in Roblox's top bar, its plaque centred on the bar's button line
  (`HudModel.TopRow`: Roblox's 44 px buttons end 2 px above the inset, so
  under a 58 px bar the row is y 12–56 and its centre 34 screen px; the
  plaque never above design y 14, so its arrow stays on screen) and on the
  screen's centre, moved right just enough to keep 16 design px from
  Roblox's left-hand buttons (`TopbarInset.Min.X`; 230 screen px when the
  engine does not say) and from the right-hand column (`HudModel.RowCentre`);
  with no room there it drops below the bar. The right-hand column starts M
  from the screen's top (below the bar only when the bar's right-hand area
  reaches over it); the left-hand stack (the desktop tribe frames; on phones
  the tiles and the world event) starts G under Roblox's buttons' foot. The
  bottom group stays M above the bottom edge. Theme's banner column starts
  below the compass waypoints (on phones below the tribe strip).
- Form factors (`Kit.Scale.FormFactor`): each HudLayout entry may carry a
  `touch` table (phones and tablets: larger text, two-line objective rows) and a
  `phone` table (phones: places for the short canvas); `Layout.ForScreen`
  merges them. When the form factor changes (`Kit.Scale.OnFormFactorChanged`)
  the regions are mounted again and refilled from the live state.

## Regions

| Region | Place (design px) | Kit parts | Data |
|---|---|---|---|
| Tribe frames | the left-hand column's top: G under Roblox's buttons (desktop y 68), its left edge the column's (M on desktop), 294 wide, 58 + 50 per row | `Panel` card, `SectionHeader` "TRIBE n" (party icon), per member a compact `PlayerRow` (portrait 40, name) and a `Bar` health fill on the track | tribe-mates on this server (`TribeId`), alphabetical, up to 3 rows; n counts them all; hidden when none |
| Compass | in Roblox's top bar: centred on its button line (desktop y 14–60, phones 22–46 screen px) and on the screen, clear of Roblox's buttons (D28), 481 × 46; waypoints just under it (+52) | `Panel` plaque, ink `Divider` ticks, `Text` letters (`hudSmall`, cardinals 20), leather `Icon` arrow_down marker, waypoint `Icon`s under it | camera yaw; landmarks (mountain), camps (campfire), portals (portal), extraction countdowns (exit), events (category icon) |
| Vitals | the right-hand column's first piece (D30): M from the top and from the right while the column stays in the corner band (desktop x 1333–1648, y 24–190), 315 × 50 rows (the column's width; D27 had 240), pitch 58; the value draws at 19 design px (22.8 on touch: 11.4 screen px on a phone) | `Bar` frame "stat": one paper plate across the bar (`lk_bar_frame_plain`, as sheets 08 / 18 without the value plaque) with the icon at its left and the dark track (`lk_bar_track`) and fill after it; the value ("85/100") is centred in the track in cream with an ink outline: heart/health, lightning/stamina, drumstick/food | Humanoid `Health`/`MaxHealth` ("85/100"); `Stamina`, `Food` fractions shown out of 100 |
| Low state | on a stat bar at ≤ 25 % | warning `Icon` on the icon tile, the icon pulses (`Motion.Pulse`; steady with reduced motion) | same values |
| Status | G under the vitals (desktop y 202), 38 high, the plaques right-aligned on the column's edge; shown only while a line applies (the column restacks) | one `Panel` plaque per line with an `Icon` and `Text` | medicine lock (hourglass, "Medicine ready in 12.4 s"), `FoodHealing` (heart), hunger slow (warning) |
| Objective | G under the status plaques, or under the vitals while none shows (desktop y 252 / 202), the column's edge, 315 × 134 (touch: 315 × 162, each task on two lines: the task, then pin, distance and progress) | `Panel` card, `SectionHeader` (exit icon, "FIND EXTRACTION"), per task a `Checkbox` ring (read only), `Text`, map_pin `Icon` + distance, progress; a task too long shrinks to 70 % and then ends in "…" | `HudModel.ExtractionObjective` (nearest countdown, else nearest portal) |
| World event | G under the objective (desktop y 398), the column's edge, 315 wide, at least 128 high and growing with its text | `Panel` card, `SectionHeader` (category icon, "WORLD EVENT", countdown at its right), name (`rowTitle`), wrapped rarity and blurb (`bodySoft`, up to 3 lines, 15 on touch), the place ("NE, 312 m") after a map_pin on its own line | `HudModel.WorldEvent`; hidden while none runs |
| Menu tiles | the left-hand column's edge (desktop x 24), centred at 0.476 of the height, 2 × 3 (88 × 84, pitch 102 / 94; HudLayout `tiles`, which the lobby draws too) | `IconButton` tile: backpack, hammer (Craft), build, party (Tribe), map, trophy (Progress); `Tooltip` names the bound key, the gamepad button ("Backpack (Y)") or nothing on touch (`Kit.Input.Hint`) | `HudController.MENU` |
| Level and XP | bottom centre, M up (D30; D27–D29: 49), 572 × 124 (the lobby's group, HudLayout `bottom`); the XP bar (356) centred over the hotbar at x 108, the level text ending 7 px left of it, the XP text from 11 px right of it, the XP pop-ups over it | "LV. n" `Text`, `Bar` xp on the track (356 × 16), "450/750 XP" `Text`; at the cap a full bar, the real level and "Max level" | progression snapshots (`ProgressionController.Changed`) |
| Hotbar | under the XP bar, 6 × `Slot` hotbar 89 × 89 (square) at the lobby's x, y 35 in the bottom group | `Slot` with `ItemIcon` art via itemId, count, Permanent star, leather number badge (keyboard and mouse only), gold glow when selected | run inventory `area == "hotbar"`; badges read `Binds.Label("HotbarN")` and follow `Kit.Input.Watch`; the selection follows the equipped slot |
| Interaction prompt | BillboardGui over the prompt's part, 230–420 × 64 (touch: × 70, object line 15), at the HUD scale | `Panel` plaque, `KeyCap` (live key: Interact bind, gamepad button or TAP), action `Text` (`rowTitle`), object `Text` (`small`), `Bar` xp hold bar; the plaque widens for the longer line (with `Kit.Core.FIT_SLACK`), so on touch only a text past 420 ends in "…" | ProximityPrompt texts; redrawn on rebinds and text changes |
| Overhead health bars | a BillboardGui over each other player's head while they are below full health, 72 × 12 bar (+ an 18 px "Downed" line), at the HUD scale clamped to 0.75–1.15; see [Overhead health bars](#overhead-health-bars) | `Bar` health fill on the track; downed: `food` (orange) fill under a `Text` "Downed" (`hudSmall` 15, cream, ink outline) | Humanoid `Health`/`MaxHealth`; `Downed`, `DownedHealth` player attributes; Show Health Bars setting |
| Damage numbers | world billboards | display font (`fonts.display`), `gold` with an `ink` outline | `CombatFeedback` hits, when Show Damage is on |
| Touch attack | touch only, bottom right (right 300, bottom 60; phones right 220, bottom 30: right of the hotbar, left of the Roblox jump button), 130 × 124 | `IconButton` round with the spear icon (axe or pickaxe while one is held; drumstick, heart or lightning while food, medicine or a draught is, GDD §59); the Kit pads its hit area | press = swing or start the bow draw, release fires; holding a consumable, press = eat or drink it (one item per press) |
| Settings | the bottom-left corner (D30): M from the left and M from the bottom (desktop x 24–76, y 865–917), 52 × 52, square (HudLayout `gear`, the lobby's too; the menu tiles' 9-sliced frame with the ink gears glyph, 2026-11-04); on touch screens the same unless Roblox's thumbstick ring reaches the corner (a phone without a side inset), then above the ring (`HudModel.GearCorner`; see Phones) | `IconButton` settings (`SettingsController`'s own HUD-scaled gui `FlintbornSettingsButton`, `SettingsController.GearSize` / `GearPosition`); gamepad: left of the first hotbar slot, under the bottom-left tile (Map; `SettingsController.LinkGear`) | opens Settings (also the Settings key, O by default) |
| Hit marker, bow draw | screen centre (−70 / +48) | `Panel` plaque with `Text` ("Hit 12" in ink, "Hurt -8" in `short`); `Bar` well with "Range 60%" | `CombatFeedback`; draw time |

## Phones (touch, viewport under 500 px high)

At scale 0.5 the canvas is about 1688 × 780 (844 × 390) or 1334 × 750
(667 × 375), and Roblox's touch controls take the corners: the jump button the
bottom right (about 95 × 90 screen px) and the dynamic thumbstick the left 40 %
below the top third. The `phone` entries arrange the HUD around them:

| Region | Phone place |
|---|---|
| Compass | in the top bar's row, 22–46 screen px; on 844 × 390 centred (x 301–543, Roblox's buttons end at about x 212), on 667 × 375 moved 38 design px right (x 232–473) to keep 8 screen px from them |
| Menu tiles | the left-hand column's top: G under Roblox's buttons (y 62–145 screen px under a 58 px bar), 3 × 2, 80 × 80 tiles at pitch 88 / 86 (40 screen px; the Kit pads the touch area to 44); the lobby draws the same grid (D30). The column reaches the middle band, so on a notched 844 × 390 iPhone it stands at the 47 pt safe inset (x 47–175), on a phone without a notch M (12 pt) in (x 12–140); the bottom row reaches about 15 screen px into the thumbstick zone's top edge |
| World event | the left-hand column, G under the tiles (844 × 390: y 151–235), the column's edge (x 47 on a notched phone, 12 without a notch), 315 wide: the right-hand column has no room for it above the jump button on phones; the header title shrinks so it never meets the countdown |
| Tribe frames | one short strip hanging under the compass waypoints, centred on the compass wherever it moves (D30; the compass top + 82, 50 high; 64–88 screen px under a 58 px bar): the tribe icon and count, then the members side by side (portrait, name, health bar; the cells widen from 150 up to `cellMaxW` 250 for the longest name, so only a longer one ends in "…"); above the thumbstick zone and clear of the jump button. Banners start below it |
| Vitals, status, objective | the right-hand column (D30), M (12 pt) from the top, G (6 pt) apart, 315 design px (157 pt) wide: 844 × 390 vitals y 12–95, status 101–120, objective 126–207, ending far above the jump button (y 300). The column reaches the middle band, so it keeps one edge: on a notched iPhone the 47 pt safe inset for every piece (x 640–797; D29 had the vitals at 832 and the objective at 797, the misalignment the owner flagged), on a phone without a notch M (x 674–832) |
| Touch attack | right 220, bottom 30 |
| Settings | the bottom-left corner (D30, `HudModel.GearCorner`): on a notched 844 × 390 iPhone Roblox's thumbstick ring starts 72 pt in (25 pt inside the safe area), so the button takes the corner itself, M from the left and from the bottom: x 12–38, y 355–378, its 44 pt touch pad (x 3–47) 25 pt clear of the ring and its foot level with the hotbar's. On a phone without a notch (667 × 375, or 844 × 390 without insets) the ring starts 25 pt in and reaches the corner, so it stands above the ring as in D28: x 12–38 (the left-hand column's edge), its foot 12 pt over the ring (667 × 375: y 250–273). Clear of the hotbar and of the boost list, which starts G right of its pad with its foot M above the bottom edge (`BoostHudController.Position`) |
| Hotbar | as on desktop: M (12 pt) above the bottom edge, centred (844 × 390: x 279–564, y 334–378); hotbar key badges hidden |

All world HUD text is at least 9 screen px on phones (body roles 1.2 ×, the
compass letters included).

## Gamepad

- Every tile has its own button: Backpack Y, Craft D-Up, Build D-Right,
  Tribe D-Left, Map D-Down, Progress View (ButtonSelect stays on Progress).
  Tile tooltips name them while a gamepad is in use.
- The HUD never takes the selection by itself: a gamepad player walks as soon
  as the run starts. While the HUD shows, its first tile is only registered as
  the target for UI navigation (`Kit.Input.SetHudDefault`, with its immediate
  selection undone), and the D-pad moves through tiles and slots (linked
  grids). With a control selected the stick moves the selection instead of the
  character, so **B** hands the stick back (`FlintbornHudRelease`, below
  Kit.Modal's B, which still closes windows first). Windows still select their
  default control when opened with a gamepad.
- The right bumper steps the hotbar selection.
- Build mode opens with the current piece selected; B leaves the palette and
  B again goes back into it. While building, RB / LB turn the piece (instead of
  stepping the hotbar or dropping) and RT places it (GDD §60).

## Behaviour

- Hotbar keys (Hotbar1–6 binds) and slot presses select and use a slot
  (`InventoryController.ActivateHotbar`); the right bumper steps the selection.
  A hotbar slot is always held and highlighted (GDD 1.31): slot 1 at the start,
  an empty slot is bare hands, and the held slot's key again keeps it. A
  consumable's slot is held like a tool (GDD §59): the attack input (click, the
  touch attack button, RT) eats or drinks it.
- While the local player eats or drinks, `ConsumeController` shows a kit stat
  bar (food fill, the item kind's icon, "Eating Cooked Meat") 300 × 46, centred
  52 px under the screen centre, where the bow draw bar sits (one item is held
  at a time). It follows the server's `ConsumeItem` / `ConsumeStart` /
  `ConsumeEnd` attributes (`world_hud_flow` page 1).
  The hotbar stays visible while the backpack is open.
- Every value is the server's replicated value; bars show the real fraction (D20).

## Overhead health bars

Owner request: while a player is below their maximum health, a bar over their
head that every player sees. `Hud/OverheadHealth.luau` draws it (started by
`HudController`, so world place only: players cannot be damaged in the lobby);
the rules are pure in `src/shared/UI/OverheadHealthModel.luau`
(`overhead_health.spec.luau`).

- **When:** shown while the character is alive and its health, rounded up as
  the HUD's health row shows it, is below the maximum (`Mode` "hurt"). Back at
  full it stays at full for `LINGER_SECONDS` (1.2 s), then fades out
  (`toastOut`); a new hit during the linger or the fade brings it straight back.
  Death, leaving, respawning and the setting turning off remove it at once.
- **Downed** (the `Downed` player attribute; Humanoid health sits at 1): the bar
  shows the downed pool (`DownedHealth` of `GameConstants.DOWNED_HEALTH`) in the
  orange fill under a "Downed" line, so a downed tribe-mate reads apart from a
  hurt one at range (the colour) and up close (the word). The revive prompt is
  unchanged.
- **Whose:** every other player. Your own is hidden
  (`OverheadHealthModel.SHOW_OWN = false`): the HUD's health row already shows it.
  Everyone's bar is red: a green tint for tribe-mates was left out because green
  is the stamina fill, and the tribe frames already list tribe-mates' health.
- **Names:** the name tag stays Roblox's (Show Names). Roblox's own overhead
  health bar (shown when damaged) never shows: `CoreGuiController` sets the local
  player's `HealthDisplayDistance` to 0 at start in both places, and each watched
  character's `HealthDisplayType` is AlwaysOff as well, so there is one bar. The bar's foot sits
  `STUDS_ABOVE_HEAD` (1.5) studs over the head's top plus a 14 px lift, above the
  name tag.
- **Size and range:** drawn in screen px (`Content` at the billboard's UIScale),
  so it reads at range and is never huge up close; the scale is the HUD's,
  clamped to `MIN_SCALE` 0.75 (phones, whose HUD scale is about 0.4: a 54 × 9
  px bar, the "Downed" line at 11 px) and `MAX_SCALE` 1.15 (at most an 83 × 14 px
  bar). `AlwaysOnTop` is off
  so walls and terrain hide it; `MaxDistance` 100 studs; `LightInfluence` 0 so
  night does not darken it.
- **Cost:** per player only signal connections (`HealthChanged`, `MaxHealth`,
  the two attributes, CharacterAdded / Removing); no per-frame work. A billboard
  is built the first time that character is hurt, disabled while hidden and
  destroyed with the character, so a 30-player server at full health has none.
- **Setting:** Settings, Gameplay, "Show Health Bars" (`showHealthBars`,
  attribute `ShowHealthBars`, default on) hides every bar at once.
- **Capture:** `overhead_health` draws `OverheadHealth.Draw`'s content as a
  billboard's frame (the harness draws no 3D world or BillboardGui): hurt 72 %,
  35 %, 8 % and downed at half and a sixth of the pool, at the desktop scale, the
  phone scale and 3×.

## Verification

```bash
python3 art/ui/capture/capture.py world_hud          # two sample runs (tribe, solo at the level cap), Roblox's top-bar buttons drawn
python3 art/ui/capture/capture.py world_hud_states   # low vitals, forced tile and slot states, done objective
python3 art/ui/capture/capture.py world_hud_phone    # 844 × 390 notched (47 px side insets), 667 × 375, 2000 × 924 touch: top bar 58 px, jump button and thumbstick drawn
python3 art/ui/capture/capture.py world_hud_wide     # 2560 × 1080
python3 art/ui/capture/capture.py world_hud_flow     # HudController.Start driven by real signals (checks, the live placement; page 1 the eating bar)
python3 art/ui/capture/capture.py overhead_health    # overhead health bars: hurt and downed, desktop, phone and 3x
```

Every scene runs the layout checks in `art/ui/capture/hud_checks.luau`
(`__checkWorldHud`, ±1 px): the compass in the top bar's row (its centre
within 10 px of the buttons' centre line) and 8 px or more from Roblox's
buttons, its waypoints under it; the HUD grid (D30): the vitals M from the
top (and from the right while the column stays in the corner band), the
right-hand column's pieces on one edge (the edge rule for the whole column),
315 wide, G apart; the left-hand column on one edge, its stacked pieces from G
under Roblox's buttons, the desktop tiles centred at 0.476; the phone tribe
strip centred under the compass; the hotbar M above the bottom edge and
centred with the XP bar centred over it; Settings M from the left and the
bottom (above the thumbstick ring only where the ring reaches the corner);
no region overlapping another, leaving the screen, reaching the middle band
outside the safe insets or meeting Roblox's buttons, the jump button, the
thumbstick ring or a notch; and a lobby HUD built at the same screen putting
the shared pieces in the same place (tile grid, Settings, bottom group, the
right-hand column's top piece and the second piece's edge and width).
The 844 × 390 page of `world_hud_phone` models a notched iPhone (47 px side
insets, `__NOTCHED_PHONE`); `world_hud_flow` feeds the same insets through
Kit.Scale's probe guis and checks the live placement with and without them.

The scenes draw over `art/reference/lobby_map.png`, a stand-in: it is the lobby
village, because the repo has no in-world screenshot. In game the world HUD
(vitals, objective, world event and the rest) is built only in the world place
(`HudMode.WorldHud`) and shown only during a run (`SessionStates.IsAtRisk`);
the lobby never shows it.

## Known limits (Kit requests)

- A stat-bar fill narrower than its end caps hides (under about a fifth of a
  stat bar), so very low health reads as an empty well; the value plaque and the
  low mark still show it.
- `hudSmall` ink text (LV and XP beside the bar, as on the lobby) has no outline
  or plate, so it is hard to read over dark ground.
- Needs a device: the real jump button and thumbstick geometry, and whether
  ButtonSelect reaches Roblox's own selection mode while bound to Progress.

## Final audit fixes

- **No save indicator** (D27): the client draws no "Saved" / "Saving…" tag in
  either place. The server still saves and sets the `SaveStatus` attribute
  (the lobby re-reads its deploy preview on it).
- **XP pop-ups** ("+40 XP · Gathered") stack above the XP bar in both HUDs (the
  lobby HUD moved them there from beside the tiles), in cream (gold for a
  level-up, which also says "Level up!") with an ink outline. While a window is
  open the HUD lane is under the veil, so a gain shows in the toast lane
  instead.
- **World event card**: the Vegetation blurb is "Prized plants have sprouted"
  (the card reads "<rarity> · <blurb>", and "Rare · Rare plants…" repeated
  itself); `hud_model.spec` checks no blurb names a rarity.
- **Downed card** redraws on its replicated attributes instead of every frame;
  the boss card ticks at 0.25 s only while a boss or the horn can show (1 s
  otherwise); the legacy event list skips its 1 s tick with no event running.

## Owner layout round (D28)

(The horizontal places and the Settings place below are superseded by D29,
"Owner edges round" at the end.)

From the owner's annotated phone screenshot (`art/ui/verify/owner/hud_move_request.jpg`,
an 844 × 390 iPhone; pink boxes and arrows):

| Drawing | Built |
|---|---|
| Box at the top centre, level with Roblox's buttons | The compass moves up into the top bar's row (desktop y 60 → 14–60, phones 59 → 22–46 screen px), centred and clear of Roblox's buttons (`HudController.PlaceTop`); its waypoints follow it |
| Vitals bracketed, arrow up to where the "Saved" pill was | The vitals start level with the buttons' top in the top-right corner (y 60 → 12; phones 59 → 12 screen px) |
| Objective, arrow up | Status, objective and world event move up with them (y 236 / 284 / 430 → 188 / 236 / 382; phones: the objective from y 171 to 124 screen px) |
| Tile grid bracketed, arrow left | The grid moves to the left edge: x 68 → 39 (desktop, the tribe frames' edge), 39 → 16 on phones (8 screen px in from the safe area: on a notched iPhone the 47 pt left of it is the notch side's safe area, so the grid cannot reach the screen's edge the arrow points at) |
| (owner message) Settings to the bottom left, in both places | Both HUDs' Settings button: bottom left, above the thumbstick ring on touch (see Phones) |

The "Sprint" button, attack button, hotbar, XP bar and interaction prompt keep
their places.

## Owner edges round (D29)

(Its placements are superseded by D30, "Owner grid round" below; the
whole-screen guis and the safe-area probes stay.)

From the owner's second annotated phone screenshot
(`art/ui/verify/owner/world_move_request_2.jpg`, the D28 build on a notched
844 × 390 iPhone; pink boxes and arrows). The HUD now draws on the whole
screen and keeps out of the notch by the edge rule (Screen setup).

| Drawing | Built (844 × 390 notched iPhone; desktop 1672 × 941) |
|---|---|
| Vitals bracketed, box at the top-right corner | The vitals' right edge 12 pt from the screen's edge (x 712–832, y 12–95; D28: 770); desktop 24 px (x 1408–1648) |
| FIND EXTRACTION, arrow up and right, box at the right edge under the vitals | The status plaques and the objective stay right under the vitals (y 100–119, 124–205) and move right to the safe inset: they reach the middle band, where the notch can be, so their right edge stands at 797 (D28: 770) rather than in the box at the very edge; desktop 24 px from the edge (x 1333–1648). The world event follows the same rule |
| Tile grid bracketed, box from the left edge | The tiles move left by the edge rule: on the owner's notched phone the grid reaches the middle band (y 59–142), so it stops at the 47 pt safe inset (x 47; D28: 55); on phones without a notch 12 pt in, on desktop x 24 (D28: 39). The tribe frames (desktop) and the phone world event follow |
| Settings, arrow down, box left of the thumbstick ring near the bottom | Bottom-left corner left of the ring, centred on its height: x 23–49, y 323–347 (D28: x 55–81, y 265–288, above the ring); above the ring only where there is no room beside it; desktop 24 px from the left and the bottom |
| Compass (not marked) | Unchanged in the top bar's row |

## Owner grid round (D30)

The owner on the live D29 HUD (phone): "both the lobby and play UI should be
unified in terms of location of shared UI elements. otherwise try to line
things up as close to the edges of the screen as possible and line up assets
together. right now the status bar and the quest menu are not lined up. and
the settings button should be like exactly in the corner — a few pixels away
from the left, and the same amount of pixels away from the bottom."

| Request | Built (844 × 390 notched iPhone; desktop 1672 × 941) |
|---|---|
| One layout for both HUDs | One grid (`HudLayout.json` `grid`, `gear`, `tiles`, `bottom`; `Hud/Layout.PlaceColumns`), used by this HUD and the lobby's: margin M 24 design px (12 pt on a phone), gap G 12 (6 pt), right-hand column 315 wide. The tiles, Settings, the level/XP bar and hotbar and the right-hand column's top, edge and width are the same in both, checked on every world capture page |
| Status bar and quest menu lined up | The right-hand column keeps one edge: vitals, status plaques, objective and world event at x 640–797 on the notched iPhone (the column reaches the middle band, so the 47 pt inset for all of it; D29: vitals 712–832, objective 639–797); desktop x 1333–1648. One width, 315 (the vitals widen from 240), G between the pieces, and the objective closes up under the vitals while no status line shows |
| Settings exactly in the corner | M from the left and from the bottom of the physical screen: x 12–38, y 355–378 (D29: x 23–49, y 323–347); desktop x 24–76, y 871–917. Above the thumbstick ring only on a phone without a side inset, where the ring itself reaches the corner |
| As close to the edges as possible, assets lined up | The right-hand column M from the top (desktop y 24; D29: 12); the hotbar group M above the bottom edge (D29: 49), level with Settings' foot; the XP bar centred over the hotbar; the left-hand stack G under Roblox's buttons; the boost list G right of Settings, its foot M above the bottom; the phone tribe strip centred under the compass |

