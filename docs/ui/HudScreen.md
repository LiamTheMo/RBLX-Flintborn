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
- Root scale `Kit.Scale.Hud` (HudModel.HudScale, × 0.9 on short touch screens).
  The top regions move down together when the Roblox top bar reaches past y 60
  (`HudController.PlaceTop`, as the lobby HUD's `SetTopInset`), and Theme's
  banner column starts below the compass waypoints.

## Regions

| Region | Place (design px) | Kit parts | Data |
|---|---|---|---|
| Tribe frames | top left (39, 60), 294 wide, 58 + 50 per row | `Panel` card, `SectionHeader` "TRIBE n" (party icon), per member a compact `PlayerRow` (portrait 40, name) and a `Bar` health fill on the track | tribe-mates on this server (`TribeId`), alphabetical, up to 3 rows; n counts them all; hidden when none |
| Compass | top centre, y 60, 481 × 46 | `Panel` plaque, ink `Divider` ticks, `Text` letters (`hudSmall`, cardinals 20), leather `Icon` arrow_down marker, waypoint `Icon`s under it | camera yaw; landmarks (mountain), camps (campfire), portals (portal), extraction countdowns (exit), events (category icon) |
| Vitals | top right (right 53, y 60), 315 × 65, pitch 76 | `Bar` frame "stat" (sheets 08, 18, 20: icon tile, fill, value plaque): heart/health, lightning/stamina, drumstick/food | Humanoid `Health`/`MaxHealth` ("85/100"); `Stamina`, `Food` fractions shown out of 100 |
| Low state | on a stat bar at ≤ 25 % | warning `Icon` on the icon tile, the icon pulses (`Motion.Pulse`; steady with reduced motion) | same values |
| Status | right-aligned under the vitals, y 289, 38 high | one `Panel` plaque per line with an `Icon` and `Text` | medicine lock (hourglass, "Medicine ready in 12.4 s"), `FoodHealing` (heart), hunger slow (warning) |
| Objective | right, y 337, 315 × 134 | `Panel` card, `SectionHeader` (exit icon, "FIND EXTRACTION"), per task a `Checkbox` ring (read only), `Text`, map_pin `Icon` + distance, progress | `HudModel.ExtractionObjective` (nearest countdown, else nearest portal) |
| World event | right, y 483, 315 × 128 | `Panel` card, `SectionHeader` (category icon, "WORLD EVENT", countdown at its right), name (`rowTitle`), wrapped line (`bodySoft`) | `HudModel.WorldEvent`; hidden while none runs |
| Menu tiles | left, x 68, centred at y 0.476, the lobby's 2 × 3 grid (88 × 84, pitch 102 / 94) | `IconButton` tile: backpack, hammer (Craft), build, party (Tribe), map, trophy (Progress); `Tooltip` "Craft (C)" names the bound key | `HudController.MENU` |
| Level and XP | bottom centre, 49 up, 572 × 124 (as the lobby) | "LV. n" `Text`, `Bar` xp on the track (356 × 16), "450/750 XP" `Text`; at the cap a full bar and "Max level · rebirth in the lobby" | progression snapshots (`ProgressionController.Changed`) |
| Hotbar | under the XP bar, 6 × `Slot` hotbar 89 × 93 at the lobby's x | `Slot` with `ItemIcon` art via itemId, count, Permanent star, leather number badge, gold glow when selected | run inventory `area == "hotbar"`; badges read `Binds.Label("HotbarN")`; the selection follows the equipped slot |
| Interaction prompt | BillboardGui over the prompt's part, 230–420 × 64, at the HUD scale | `Panel` plaque, `KeyCap` (live key: Interact bind, gamepad button or TAP), action `Text` (`rowTitle`), object `Text` (`small`), `Bar` xp hold bar | ProximityPrompt texts; redrawn on rebinds and text changes |
| Damage numbers | world billboards | display font (`fonts.display`), `gold` with an `ink` outline | `CombatFeedback` hits, when Show Damage is on |
| Touch attack | touch only, bottom right (right 300, bottom 60), 130 × 124 | `IconButton` round with the spear icon; the Kit pads its hit area | press = swing or start the bow draw, release fires |
| Hit marker, bow draw | screen centre (−70 / +48) | `Panel` plaque with `Text` ("Hit 12" in ink, "Hurt -8" in `short`); `Bar` well with "Range 60%" | `CombatFeedback`; draw time |

## Behaviour (unchanged)

- Hotbar keys (Hotbar1–6 binds) and slot presses select and use a slot
  (`InventoryController.ActivateHotbar`); the right bumper steps the selection.
  The hotbar stays visible while the backpack is open.
- Every value is the server's replicated value; bars show the real fraction (D20).
- Gamepad: tiles and slots are linked as grids; the Kit's hover art is the
  selection cue.

## Verification

```bash
python3 art/ui/capture/capture.py world_hud          # two sample runs (tribe, solo at the level cap)
python3 art/ui/capture/capture.py world_hud_states   # low vitals, forced tile and slot states, done objective
python3 art/ui/capture/capture.py world_hud_phone    # 844 × 390 touch, top bar 58 px, attack button
python3 art/ui/capture/capture.py world_hud_wide     # 2560 × 1080
python3 art/ui/capture/capture.py world_hud_flow     # HudController.Start driven by real signals (checks)
```

The scenes draw over `art/reference/lobby_map.png` (a world picture without UI).

## Known limits (Kit requests)

- A stat-bar fill narrower than its end caps hides (under about 21 % on a 315 px
  stat bar), so very low health reads as an empty well; the value plaque and the
  low mark still show it.
- `hudSmall` ink text (LV and XP beside the bar, as on the lobby) has no outline
  or plate, so it is hard to read over dark ground.
- Bows have no item art yet (`ItemInfo`), so their slot shows the name.
