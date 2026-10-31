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

- `FlintbornHud`: DisplayOrder `hud` (1), `IgnoreGuiInset`, `DeviceSafeInsets`,
  `ResetOnSpawn = false`, enabled only while `SessionStates.IsAtRisk`.
- `FlintbornHudOverlay` (order 2, always on): XP pop-ups above the XP bar, so they
  also show outside a run.
- Root scale `Kit.Scale.Hud` (HudModel.HudScale, × 0.9 on touch phones and
  tablets, never below the `phoneFloor.hud` 0.5).
  The top-pinned regions move down together when the Roblox top bar reaches past
  y 60 (`HudController.PlaceTop`, as the lobby HUD's `SetTopInset`); regions
  pinned to the bottom stay. Theme's banner column starts below the compass
  waypoints.
- Form factors (`Kit.Scale.FormFactor`): each HudLayout entry may carry a
  `touch` table (phones and tablets: larger text, two-line objective rows) and a
  `phone` table (phones: places for the short canvas); `Layout.ForScreen`
  merges them. When the form factor changes (`Kit.Scale.OnFormFactorChanged`)
  the regions are mounted again and refilled from the live state.

## Regions

| Region | Place (design px) | Kit parts | Data |
|---|---|---|---|
| Tribe frames | top left (39, 60), 294 wide, 58 + 50 per row | `Panel` card, `SectionHeader` "TRIBE n" (party icon), per member a compact `PlayerRow` (portrait 40, name) and a `Bar` health fill on the track | tribe-mates on this server (`TribeId`), alphabetical, up to 3 rows; n counts them all; hidden when none |
| Compass | top centre, y 60, 481 × 46 | `Panel` plaque, ink `Divider` ticks, `Text` letters (`hudSmall`, cardinals 20), leather `Icon` arrow_down marker, waypoint `Icon`s under it | camera yaw; landmarks (mountain), camps (campfire), portals (portal), extraction countdowns (exit), events (category icon) |
| Vitals | top right (right 53, y 60), 315 × 65, pitch 76 | `Bar` frame "stat": one paper plate across the bar (`lk_bar_frame_plain`, as sheets 08 / 18 without the value plaque) with the icon at its left and the dark track (`lk_bar_track`) and fill after it; the value ("85/100") is centred in the track in cream with an ink outline: heart/health, lightning/stamina, drumstick/food | Humanoid `Health`/`MaxHealth` ("85/100"); `Stamina`, `Food` fractions shown out of 100 |
| Low state | on a stat bar at ≤ 25 % | warning `Icon` on the icon tile, the icon pulses (`Motion.Pulse`; steady with reduced motion) | same values |
| Status | right-aligned under the vitals, y 289, 38 high | one `Panel` plaque per line with an `Icon` and `Text` | medicine lock (hourglass, "Medicine ready in 12.4 s"), `FoodHealing` (heart), hunger slow (warning) |
| Objective | right, y 337, 315 × 134 (touch: 315 × 162, each task on two lines: the task, then pin, distance and progress) | `Panel` card, `SectionHeader` (exit icon, "FIND EXTRACTION"), per task a `Checkbox` ring (read only), `Text`, map_pin `Icon` + distance, progress; a task too long shrinks to 70 % and then ends in "…" | `HudModel.ExtractionObjective` (nearest countdown, else nearest portal) |
| World event | right, y 483 (touch: y 511), 315 wide, at least 128 high and growing with its text | `Panel` card, `SectionHeader` (category icon, "WORLD EVENT", countdown at its right), name (`rowTitle`), wrapped rarity and blurb (`bodySoft`, up to 3 lines, 15 on touch), the place ("NE, 312 m") after a map_pin on its own line | `HudModel.WorldEvent`; hidden while none runs |
| Menu tiles | left, x 68, centred at y 0.476, the lobby's 2 × 3 grid (88 × 84, pitch 102 / 94) | `IconButton` tile: backpack, hammer (Craft), build, party (Tribe), map, trophy (Progress); `Tooltip` names the bound key, the gamepad button ("Backpack (Y)") or nothing on touch (`Kit.Input.Hint`) | `HudController.MENU` |
| Level and XP | bottom centre, 49 up, 572 × 124 (as the lobby) | "LV. n" `Text`, `Bar` xp on the track (356 × 16), "450/750 XP" `Text`; at the cap a full bar, the real level and "Max level" | progression snapshots (`ProgressionController.Changed`) |
| Hotbar | under the XP bar, 6 × `Slot` hotbar 89 × 93 at the lobby's x | `Slot` with `ItemIcon` art via itemId, count, Permanent star, leather number badge (keyboard and mouse only), gold glow when selected | run inventory `area == "hotbar"`; badges read `Binds.Label("HotbarN")` and follow `Kit.Input.Watch`; the selection follows the equipped slot |
| Interaction prompt | BillboardGui over the prompt's part, 230–420 × 64 (touch: × 70, object line 15), at the HUD scale | `Panel` plaque, `KeyCap` (live key: Interact bind, gamepad button or TAP), action `Text` (`rowTitle`), object `Text` (`small`), `Bar` xp hold bar; on touch long texts end in "…" | ProximityPrompt texts; redrawn on rebinds and text changes |
| Damage numbers | world billboards | display font (`fonts.display`), `gold` with an `ink` outline | `CombatFeedback` hits, when Show Damage is on |
| Touch attack | touch only, bottom right (right 300, bottom 60; phones right 220, bottom 30: right of the hotbar, left of the Roblox jump button), 130 × 124 | `IconButton` round with the spear icon; the Kit pads its hit area | press = swing or start the bow draw, release fires |
| Hit marker, bow draw | screen centre (−70 / +48) | `Panel` plaque with `Text` ("Hit 12" in ink, "Hurt -8" in `short`); `Bar` well with "Range 60%" | `CombatFeedback`; draw time |

## Phones (touch, viewport under 500 px high)

At scale 0.5 the canvas is about 1688 × 780 (844 × 390) or 1334 × 750
(667 × 375), and Roblox's touch controls take the corners: the jump button the
bottom right (about 95 × 90 screen px) and the dynamic thumbstick the left 40 %
below the top third. The `phone` entries arrange the HUD around them:

| Region | Phone place |
|---|---|
| Menu tiles | top left (39, 60), 3 × 2, 80 × 80 tiles at pitch 88 / 86 (40 screen px; the Kit pads the touch area to 44); their bottom row reaches about 12–17 screen px into the thumbstick zone's top edge |
| World event | top left under the tiles (39, 238); the header title shrinks so it never meets the countdown |
| Tribe frames | one short strip under the compass (centred, y 142 before the top-bar shift, 50 high): the tribe icon and count, then the members side by side (portrait, name ending in "…", health bar); above the thumbstick zone and clear of the jump button. Banners start below it |
| Vitals, status, objective | right column as on desktop; the objective ends above the jump button |
| Touch attack | right 220, bottom 30 |
| Hotbar, compass | as on desktop; hotbar key badges hidden |

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
python3 art/ui/capture/capture.py world_hud          # two sample runs (tribe, solo at the level cap)
python3 art/ui/capture/capture.py world_hud_states   # low vitals, forced tile and slot states, done objective
python3 art/ui/capture/capture.py world_hud_phone    # 844 × 390 touch, top bar 58 px, attack button
python3 art/ui/capture/capture.py world_hud_wide     # 2560 × 1080
python3 art/ui/capture/capture.py world_hud_flow     # HudController.Start driven by real signals (checks)
```

The scenes draw over `art/reference/lobby_map.png`, a stand-in: it is the lobby
village, because the repo has no in-world screenshot. In game the world HUD
(vitals, objective, world event and the rest) is built only in the world place
(`HudMode.ReplacesLegacy`) and shown only during a run (`SessionStates.IsAtRisk`);
the lobby never shows it.

## Known limits (Kit requests)

- A stat-bar fill narrower than its end caps hides (under about 21 % on a 315 px
  stat bar), so very low health reads as an empty well; the value plaque and the
  low mark still show it.
- `hudSmall` ink text (LV and XP beside the bar, as on the lobby) has no outline
  or plate, so it is hard to read over dark ground.
- Bows have no item art yet (`ItemInfo`); their slot shows the Kit's neutral
  kind glyph.
- Needs a device: the real jump button and thumbstick geometry, and whether
  ButtonSelect reaches Roblox's own selection mode while bound to Progress.
