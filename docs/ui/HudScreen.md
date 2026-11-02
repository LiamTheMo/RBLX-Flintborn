# In-world HUD spec (Kit)

The HUD players see during a run. There is no mockup: it is built only from the
shared Kit (`docs/ui/KIT.md`; ARCHITECTURE §4.8, D15) so it reads as the same
game as the lobby HUD (`art/ui/captures/lobby_hud.png`). The hotbar, XP bar and
menu tiles use the lobby HUD's parts and measures. Places and sizes live in
`src/shared/UI/HudLayout.json` (design px on the 1672 × 941 canvas); art, type
and colours come only from the Kit. Status: Built.

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
- The screen's edges (D29, `HudController.PlaceTop` with the screen from
  `Kit.Scale.HudScreen`, re-run when `Kit.Scale.OnSafeInsetsChanged` fires):
  every region pinned to the left or right edge (vitals, status, objective,
  world event, menu tiles, tribe frames) follows the edge rule
  (`Kit.Scale.PinToEdge`, STYLE_GUIDE §5.7): 24 design px from the screen's
  edge while it lies wholly in the top 30 % or the bottom 25 % of the screen,
  at least the device safe inset (`Kit.Scale.SafeInsets`) where it reaches the
  middle band, where a notch can be.
- Root scale `Kit.Scale.Hud` (HudModel.HudScale, × 0.9 on touch phones and
  tablets, never below the `phoneFloor.hud` 0.5).
- The top bar (D28, `HudController.TopBar` / `PlaceTop`, re-run when the scale,
  the screen or `GuiService.TopbarInset` changes): the compass sits in Roblox's
  top bar, its plaque centred on the bar's button line (`HudModel.TopRow`:
  Roblox's 44 px buttons end 2 px above the inset, so under a 58 px bar the row
  is y 12–56 and its centre 34 screen px; the plaque never above design y 14,
  so its arrow stays on screen) and on the screen's centre, moved right just
  enough to keep 16 design px from Roblox's left-hand buttons
  (`TopbarInset.Min.X`; 230 screen px when the engine does not say) and from
  the vitals (`HudModel.RowCentre`); with no room there it drops below the bar.
  The right-hand column (vitals, status, objective, world event) starts level
  with the buttons' top (below the bar only when the bar's right-hand area
  reaches over it). The left-hand regions (tribe frames; on phones the tiles
  and the world event) move down together below the bar. Regions pinned to
  the bottom stay. Theme's banner column starts below the compass waypoints
  (on phones below the tribe strip).
- Form factors (`Kit.Scale.FormFactor`): each HudLayout entry may carry a
  `touch` table (phones and tablets: larger text, two-line objective rows) and a
  `phone` table (phones: places for the short canvas); `Layout.ForScreen`
  merges them. When the form factor changes (`Kit.Scale.OnFormFactorChanged`)
  the regions are mounted again and refilled from the live state.

## Regions

| Region | Place (design px) | Kit parts | Data |
|---|---|---|---|
| Tribe frames | top left (24, 60; left edge by the edge rule), 294 wide, 58 + 50 per row | `Panel` card, `SectionHeader` "TRIBE n" (party icon), per member a compact `PlayerRow` (portrait 40, name) and a `Bar` health fill on the track | tribe-mates on this server (`TribeId`), alphabetical, up to 3 rows; n counts them all; hidden when none |
| Compass | in Roblox's top bar: centred on its button line (desktop y 14–60, phones 22–46 screen px) and on the screen, clear of Roblox's buttons (D28), 481 × 46; waypoints just under it (+52) | `Panel` plaque, ink `Divider` ticks, `Text` letters (`hudSmall`, cardinals 20), leather `Icon` arrow_down marker, waypoint `Icon`s under it | camera yaw; landmarks (mountain), camps (campfire), portals (portal), extraction countdowns (exit), events (category icon) |
| Vitals | top-right corner (24 from the right by the edge rule, D29; level with Roblox's buttons' top: design y 12 under a 58 px bar on desktop, 12 screen px on every screen; D28), 240 × 50, pitch 58 (D27; was 315 × 65 at 76); the value draws at 19 design px (22.8 on touch: 11.4 screen px on a phone) | `Bar` frame "stat": one paper plate across the bar (`lk_bar_frame_plain`, as sheets 08 / 18 without the value plaque) with the icon at its left and the dark track (`lk_bar_track`) and fill after it; the value ("85/100") is centred in the track in cream with an ink outline: heart/health, lightning/stamina, drumstick/food | Humanoid `Health`/`MaxHealth` ("85/100"); `Stamina`, `Food` fractions shown out of 100 |
| Low state | on a stat bar at ≤ 25 % | warning `Icon` on the icon tile, the icon pulses (`Motion.Pulse`; steady with reduced motion) | same values |
| Status | right-aligned under the vitals, y 188 (the column's top + 176), 38 high, right edge by the edge rule | one `Panel` plaque per line with an `Icon` and `Text` | medicine lock (hourglass, "Medicine ready in 12.4 s"), `FoodHealing` (heart), hunger slow (warning) |
| Objective | right, right under the status row, y 236 (column top + 224), right edge by the edge rule, 315 × 134 (touch: 315 × 162, each task on two lines: the task, then pin, distance and progress) | `Panel` card, `SectionHeader` (exit icon, "FIND EXTRACTION"), per task a `Checkbox` ring (read only), `Text`, map_pin `Icon` + distance, progress; a task too long shrinks to 70 % and then ends in "…" | `HudModel.ExtractionObjective` (nearest countdown, else nearest portal) |
| World event | right, under the objective, y 382 (touch: y 410), right edge by the edge rule, 315 wide, at least 128 high and growing with its text | `Panel` card, `SectionHeader` (category icon, "WORLD EVENT", countdown at its right), name (`rowTitle`), wrapped rarity and blurb (`bodySoft`, up to 3 lines, 15 on touch), the place ("NE, 312 m") after a map_pin on its own line | `HudModel.WorldEvent`; hidden while none runs |
| Menu tiles | the left edge, x 24 by the edge rule (D29; D28 had 39), centred at y 0.476, the lobby's 2 × 3 grid (88 × 84, pitch 102 / 94) | `IconButton` tile: backpack, hammer (Craft), build, party (Tribe), map, trophy (Progress); `Tooltip` names the bound key, the gamepad button ("Backpack (Y)") or nothing on touch (`Kit.Input.Hint`) | `HudController.MENU` |
| Level and XP | bottom centre, 49 up, 572 × 124 (as the lobby) | "LV. n" `Text`, `Bar` xp on the track (356 × 16), "450/750 XP" `Text`; at the cap a full bar, the real level and "Max level" | progression snapshots (`ProgressionController.Changed`) |
| Hotbar | under the XP bar, 6 × `Slot` hotbar 89 × 89 (square) at the lobby's x, y 35 in the bottom group | `Slot` with `ItemIcon` art via itemId, count, Permanent star, leather number badge (keyboard and mouse only), gold glow when selected | run inventory `area == "hotbar"`; badges read `Binds.Label("HotbarN")` and follow `Kit.Input.Watch`; the selection follows the equipped slot |
| Interaction prompt | BillboardGui over the prompt's part, 230–420 × 64 (touch: × 70, object line 15), at the HUD scale | `Panel` plaque, `KeyCap` (live key: Interact bind, gamepad button or TAP), action `Text` (`rowTitle`), object `Text` (`small`), `Bar` xp hold bar; the plaque widens for the longer line (with `Kit.Core.FIT_SLACK`), so on touch only a text past 420 ends in "…" | ProximityPrompt texts; redrawn on rebinds and text changes |
| Damage numbers | world billboards | display font (`fonts.display`), `gold` with an `ink` outline | `CombatFeedback` hits, when Show Damage is on |
| Touch attack | touch only, bottom right (right 300, bottom 60; phones right 220, bottom 30: right of the hotbar, left of the Roblox jump button), 130 × 124 | `IconButton` round with the spear icon; the Kit pads its hit area | press = swing or start the bow draw, release fires |
| Settings | bottom-left corner (D29): 24 from the left and the bottom, 52 × 46; touch screens: left of Roblox's thumbstick ring, centred on its height, or above the ring where there is no room beside it (`HudModel.GearCorner`; see Phones) | `IconButton` settings (`SettingsController`'s own HUD-scaled gui `FlintbornSettingsButton`, `SettingsController.GEAR` / `GearPosition`); gamepad: left of the first hotbar slot, under the bottom-left tile (Map; `SettingsController.LinkGear`) | opens Settings (also the Settings key, O by default) |
| Hit marker, bow draw | screen centre (−70 / +48) | `Panel` plaque with `Text` ("Hit 12" in ink, "Hurt -8" in `short`); `Bar` well with "Range 60%" | `CombatFeedback`; draw time |

## Phones (touch, viewport under 500 px high)

At scale 0.5 the canvas is about 1688 × 780 (844 × 390) or 1334 × 750
(667 × 375), and Roblox's touch controls take the corners: the jump button the
bottom right (about 95 × 90 screen px) and the dynamic thumbstick the left 40 %
below the top third. The `phone` entries arrange the HUD around them:

| Region | Phone place |
|---|---|
| Compass | in the top bar's row, 22–46 screen px; on 844 × 390 centred (x 301–543, Roblox's buttons end at about x 212), on 667 × 375 moved 38 design px right (x 232–473) to keep 8 screen px from them |
| Menu tiles | top left at the left edge by the edge rule (D29), below the top bar (y 59–142 screen px), 3 × 2, 80 × 80 tiles at pitch 88 / 86 (40 screen px; the Kit pads the touch area to 44). They reach the middle band, so on a notched 844 × 390 iPhone they stand at the 47 pt safe inset (x 47–175; D28 had 55), on a phone without a notch 12 pt in (x 12–140); their bottom row reaches about 12 screen px into the thumbstick zone's top edge |
| World event | top left under the tiles (y 238 design px), left edge by the edge rule (the middle band: x 47 on a notched phone, 12 without a notch): the right-hand column has no room for it above the jump button on phones (the card grows to about 94 screen px); the header title shrinks so it never meets the countdown |
| Tribe frames | one short strip hanging under the compass waypoints (centred, the compass top + 82, 50 high; 63–88 screen px under a 58 px bar): the tribe icon and count, then the members side by side (portrait, name, health bar; the cells widen from 150 up to `cellMaxW` 250 for the longest name, so only a longer one ends in "…"); above the thumbstick zone and clear of the jump button. Banners start below it |
| Vitals, status, objective | right column from the top-right corner (844 × 390: vitals y 12–95, status 100–119, objective 124–205), ending far above the jump button (y 300). The vitals lie in the top band, so they keep 12 pt from the screen's edge (x 712–832); the status and objective reach the middle band, so on a notched iPhone their right edge stands at the 47 pt safe inset (x 639–797), on a phone without a notch 12 pt in |
| Touch attack | right 220, bottom 30 |
| Settings | the bottom-left corner (D29, `HudModel.GearCorner`). On a notched 844 × 390 iPhone Roblox's thumbstick ring starts 72 pt in (25 pt inside the safe area), so the button sits between the screen's edge and the ring: x 23–49, centred on the ring's height (y 323–347, in the bottom band, so it may leave the safe inset), its 44 pt touch pad (x 14–58) 14 pt clear of the ring. On a phone without a notch (667 × 375) the ring starts 25 pt in, leaving no room beside it, so it stands above the ring as in D28: x 12–38, y 250–273, its foot 12 pt over the ring (y 285), its pad (x 3–47) in the outer tenth of the screen. Clear of the hotbar (its level text from x 279 / 190) and of the boost list, which starts right of it (`BoostHudController.PHONE_LEFT`) |
| Hotbar | as on desktop; hotbar key badges hidden |

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
  B again goes back into it.

## Behaviour (unchanged)

- Hotbar keys (Hotbar1–6 binds) and slot presses select and use a slot
  (`InventoryController.ActivateHotbar`); the right bumper steps the selection.
  The hotbar stays visible while the backpack is open.
- Every value is the server's replicated value; bars show the real fraction (D20).

## Verification

```bash
python3 art/ui/capture/capture.py world_hud          # two sample runs (tribe, solo at the level cap), Roblox's top-bar buttons drawn
python3 art/ui/capture/capture.py world_hud_states   # low vitals, forced tile and slot states, done objective
python3 art/ui/capture/capture.py world_hud_phone    # 844 × 390 notched (47 px side insets), 667 × 375, 2000 × 924 touch: top bar 58 px, jump button and thumbstick drawn
python3 art/ui/capture/capture.py world_hud_wide     # 2560 × 1080
python3 art/ui/capture/capture.py world_hud_flow     # HudController.Start driven by real signals (checks, the live placement)
```

Every scene runs the layout checks in `art/ui/capture/hud_checks.luau`
(`__checkWorldHud`): the compass in the top bar's row (its centre within
10 px of the buttons' centre line) and 8 px or more from Roblox's buttons, its
waypoints under it, the vitals level with the buttons' top, the objective
right under the vitals and status (within 70 design px of the vitals' foot)
with the event under it, the tiles below the bar, every edge region at the gap
the edge rule gives (D29), Settings in the bottom-left corner left of the
hotbar (desktop 24 from both edges; touch left of the thumbstick ring and
centred on it, or above it where there is no room), and no region overlapping
another, leaving the screen, reaching the middle band outside the safe insets
or meeting Roblox's buttons, the jump button, the thumbstick ring or a notch.
The 844 × 390 page of `world_hud_phone` models a notched iPhone (47 px side
insets, `__NOTCHED_PHONE`); `world_hud_flow` feeds the same insets through
Kit.Scale's probe guis and checks the live placement with and without them.

The scenes draw over `art/reference/lobby_map.png`, a stand-in: it is the lobby
village, because the repo has no in-world screenshot. In game the world HUD
(vitals, objective, world event and the rest) is built only in the world place
(`HudMode.ReplacesLegacy`) and shown only during a run (`SessionStates.IsAtRisk`);
the lobby never shows it.

## Known limits (Kit requests)

- A stat-bar fill narrower than its end caps hides (under about a fifth of a
  stat bar), so very low health reads as an empty well; the value plaque and the
  low mark still show it.
- `hudSmall` ink text (LV and XP beside the bar, as on the lobby) has no outline
  or plate, so it is hard to read over dark ground.
- Bows have no item art yet (`ItemInfo`); their slot shows the Kit's neutral
  kind glyph.
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
