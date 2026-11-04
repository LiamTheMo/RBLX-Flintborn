# 068 Timber Hut — spec

Reference: `art/blender/assets/references/068.png` (1024 × 1536, remade 2026-11-03: "TIMBER HUT", "PAGE 068",
"BUILDING MODEL STUDY"). Builder: `art/blender/kit/mcp/m068.py` → `build()`, on the shared library (`kit_parts`,
`kit_build`, `kit_verify`). The earlier study and fix rounds (old sheet) are in git history.

## Brief

- **Sheet:** 068 Timber Hut (remake: yes). Family: none.
- **Class and budget:** building, ceiling 8000, plan about 7500 (built 7532).
- **Size:** set by the house door (3.60 × 7.00 clear) on a 2.60 floor; the sheet's heights, as fractions of the
  chimney top in the side cell, then give plate top 11.20 (sheet 0.572, ours 0.577), ridge 16.00 (0.826 / 0.825),
  stone 2.30 (0.145 / 0.12–0.13), wall length 16.40 (1.55 of the plate height; ours 1.46). Hero 20.65 × 24.41 × 19.40;
  walls 14.40 × 16.40 over the corner posts.
- **Hero view:** f34 at (−46, 22). Other cells: side (90, 3) and front (−42, 8) direct; rear = the −X elevation
  mirrored front to back (−90, 3, mirror); r34 a redraw, compared mirrored at (35, 18), content only; top content
  only, compared turned a quarter (`rot90` 1) because the sheet draws the stairs on an eave side.
- **Parts:**
  | Part | What | Tris |
  | --- | --- | --- |
  | TimberCabinRoofPanel | +X canvas slab, 4 × 2 panel seams, four U clips | 456 |
  | TimberCabinRidgeBeam | pitched-top beam, pale ends, golden band near each end | 280 |
  | TimberCabinChimney | two stone blocks, flashing collar, crenellated flued cap | 132 |
  | TimberCabinBanner | pole, crossarm with X lashing and iron bands, red banner with white emblem | 632 |
  | TimberCabinLantern | one door lantern on its wall bracket | 180 |
  | TimberCabinWallPanel | back wall: five plank rows between two corner posts | 336 |
  | TimberCabinWindowWall | +X wall with the centred barred window and inner shutter, two posts | 488 |
  | TimberCabinDoorFrame | door posts on golden caps, lintel, header, closed leaf (hinge stored) | 288 |
  | TimberCabinGableFrame | collar, crossed bargeboards, saddle, cleats, eave-beam ends | 176 |
  | TimberCabinFloor | ten deck planks, underlay, threshold, sill, short feet | 464 |
  | TimberCabinStairs | two two-plank treads on blocks | 160 |
  | TimberCabinFoundation | +X run of four blocks and its corner block | 180 |
- **Palette** (sheet medians → calibrated base): timber `#C46826` side / `#A7521A` f34 → `#9C5C26`; timber_end
  `#F09A44` → `#BF8241`; timber_deep `#8E4618` → `#754118`; canvas `#FEF1CD` → `#EADCBC`; stone `#B3A6A7` → `#8F8A91`,
  light `#A29CA3`, dark `#7F7B82`; iron `#5E5B60` (swatch `#737276`) → `#585861`, metal 0.4; rope `#ECA01C` →
  `#BB871C`; banner `#E61B1C` → `#B6191C`; white `#D7D6D3`; glow `#F8B428` emission 1.0 (Neon); soot `#1F1E23`.
  All matte (roughness 0.85–1.0) except iron (0.55).
- **Lights / VFX:** three Neon lanterns, a `heat_glow` socket each; one thin pale `chimney_smoke` at the flue.
- **Collision:** hero `precise`; RoofPanel, RidgeBeam, Chimney, WallPanel, Floor, Foundation `box`; WindowWall,
  DoorFrame, Stairs `precise`; GableFrame `hull`; Banner, Lantern `none`.
- **Checks switched on in kit_verify:** `escape` (box (−6.55, −7.55, 2.65)–(6.55, 7.55, 14.4), allow the doorway
  x ±1.80, z 2.60–9.78 at the wall plane); `walk` (one path from (0, −14.5) up the stairs, through the door, round the
  room and back out; turning room at three floor points); sockets per object; `house_check` (floor tops, door clear,
  headroom, stair tops).
- **Departures from HOUSE_RULES:**
  - Hero 7532 is 6 % under the ceiling, not 10 %: the sheet's plank, frame and rope detail needs it.
  - A 0.08 door sill in the wall plane (top 2.68): the closed leaf stops on it, and grazing rays from the room floor
    leave by the door. The lintel moved up to 9.68 so the clear opening above the sill stays 3.60 × 7.00.
  - The escape box stops at 14.4 (under the ridge beam), not at the apex: higher grid points sit above the canvas
    under the chimney cap's overhang and count as enclosed.
  - Barrel 2.72 and crate 2.30 at kit size; the sheet draws them about 1.6× bigger (recorded miss).
- **Questions for the main session:** none.

## Recorded misses (view conflicts, not blockers)

- **Scale figure.** The side cell's grey figure (80 px) would make the hut 9 studs long; the house door sets the size.
- **Chimney:** front half on the +X slope (f34 and the mirrored rear cell); the side and r34 cells put it at the back.
- **Rear cell** (the −X wall): drawn without a window; the f34 and r34 show one, so ours has it.
- **r34:** its dressing and chimney are a mirror of the f34's, and it shows a lantern on the back gable; ours keeps
  the hero's three lanterns.
- **Top cell:** stairs on an eave side; ours on the gable (every other view).
- **Floor plan (close-up B):** planks run across the room; ours run along Y (the exploded deck reads either way).
- **Plank rows:** the elevations show four rows, the f34 about five; ours has five (the window fits rows 3–4).
- **f34 W : H** 1.37 sheet against 1.22 ours: the sheet's oversized barrel, crate and banner widen it.

## Stage 1 — Modelling

Continued the shared-library builder (every exploded part has its own function; the hero is assembled from the same
functions). Fixes this round:
- `P.bracket` needs a 3D wall point: both lantern brackets now pass `(x, y, 0)`.
- Stone blocks: `P.block`'s creased and chipped faces are warped quads, which the ray-parity check read as inward
  faces (20 blocks). `flatten()` in m068 splits warped quads into their two triangles (no tri cost). **Belongs in
  kit_parts:** `block()` should emit those faces as triangles itself.
- Chimney cap: the flue floor sat 0.003 below the cap's underside (4 self-hits); flue depth now 0.45, merlons 0.78
  so they stay 0.02 off the flue wall.
- Run blocks overlap 0.004 at their ends instead of 0.02 gaps (the chamfers still draw the V joint).
- Door sill, lintel at 9.68, leaf 2.62–9.66.
- Ridge beam ends 0.90 past the bargeboards with one golden band (two touching turns) 0.37 from each end: the old pair
  of bands framed the end face and read as a gold shield.
- Wall plank end bands only on some planks over 5.0 long and one step darker (they read as brickwork before);
  saves 456 tris.
- Eave lantern moved to y −5.40, base 6.50, so it hangs over the window's front jamb as on the f34 (bottom 6.50:
  a character walks under it).
- Views and compare cameras retuned to the sheet: f34 (−46, 22), front (−42, 8), top turned; exploded layout in
  three bands like panel 4.

## Stage 2 — Optimisation and cleanup

kit_verify, building class: **0 problems**. Hero 7532 / 8000, 328 closed shells; non-manifold, boundary, wire,
loose, zero-area, n-gons, duplicate vertices, bowties, winding errors, self-hits and parity-inward all 0; normals
outward; origin at the bottom centre (offset (−0.022, −0.494, 0) in the build frame); transforms applied; no
modifiers or custom normals; thinnest corner 1.04°. Floating 0, unchained 0, buried 0 (deepest 0.042, rope in pole).
Every part under 1000 (largest the Banner, 632) and clean on the same checks.
- **Escape scan:** 709,501 rays from 733 interior points, 224 floor points and 146,367 seam points; 16,925 leave by
  the doorway, **0 elsewhere**.
- **Walk:** stairs rises 0.87 / 0.86 / 0.87, the sill 0.08; minimum clearance 0.40 (the front course beside the
  stairs), 0 intersecting steps; headroom 7.00 in the doorway, 9.41 under every interior member; turning room 3.44
  at the room centre and 2.83 at the back corners, 0 intersecting yaws.
- **house_check:** floor tops 2.60 everywhere, door 3.60 wide × 7.00 above the sill (7.08 above the floor), stair
  tops 1.73 / 0.87.

## Stage 3 — UV

kit_build's angle-based unwrap (margin 0.008), overlaps cut free: 0 overlapping pairs, 0 flipped, island gap 0.016,
border 0.008, density 0.998–1.001, conformal stretch p95 1.0.

## Stage 4 — Materials, colour and texture

Calibrated with `MODEL.calibrate` against the sheet medians (TARGETS in the builder); the canvas was set by hand
(`#EADCBC`) because the dome test clips at white and pushed it pink. Tint mottling per piece (`P.texture`), hem
bands toward canvas_deep along the eaves and round the chimney, plank and post bands by position.
Final renders against the sheet (same masks, compare crops):

| Cell | Timber sheet / ours | Canvas | Stone | Banner | Wood share |
| --- | --- | --- | --- | --- | --- |
| f34 | `#A7521A` / `#A85A20` | `#FEF1CD` / `#FFFFE2` | `#A09394` / `#9B9091` | `#E31C1B` / `#DB191A` | 57.7 / 57.1 % |
| front | `#A95317` / `#A5581F` | `#FDF0C9` / `#FFFFE2` | `#938A8C` / `#9A8F90` | `#E81D1B` / `#DB191A` | 65.5 / 64.7 % |
| side | `#C06523` / `#844718` | `#FDF1CA` / `#FBE6BE` | `#ADA1A3` / `#777277` | — | 54.5 / 55.0 % |

Recorded, not scored: the side and rear elevations face away from the studio key light, so their wood and stone
render about 30 % darker than the sheet's evenly lit elevations; the lit canvas slope clips toward white.

## Stage 5 — Lighting

Lantern glass `m068_glow` at emission 1.0 exports as Neon. Studio: each `heat_glow` socket carries a soft amber halo
emitter and a PointLight (`#FFB347`, brightness 1, range 12, flicker). Windows read dark (inner shutters); no other
light. Requires Manual Validation in Studio: lantern glow at night, interior darkness with the door open.

## Stage 6 — VFX

Hero: three `heat_glow` sockets at the glass centres (L1 (−8.30, −5.40, 7.50), L2 / L3 (∓4.70, −9.10, 7.20)) and one
`chimney_smoke` at the flue (2.20, −1.95, 18.60): thin pale puffs (`#BDB8B4`–`#E4E0DC`, rate 2, no light emission).
Lantern part one `heat_glow`, Chimney part one `chimney_smoke`. Export stats: hero 4 sockets, glow key `m068_glow`.

## Stored points

Hero: `m068_centre` (floor centre), `m068_threshold` (+ facing −Y), `m068_chimney`, `m068_hinge` (axis bottom
(−1.80, −7.59, 2.62) in the build frame, closed yaw 0, open yaw 95). DoorFrame: `m068_hinge` (open yaw 0). Lantern:
`m068_hang`, `m068_mount`. Chimney: `m068_flue`. Banner: `m068_top`.

## Renders

`M068_views.png` (f34, r34, front, side, rear, top, exploded, scale) and the close-ups `junction_cu`, `apex_cu`,
`chimney_cu`, `door_cu`, `inside_cu`, `underside_cu`, `base_cu` in this folder. Sheet against render:
`m068.compare()` writes `<temp>/RBLX-Flintborn/compare/M068/M068_compare.png`.

## Main session rulings (2026-11-04)

The brief's departures stand and are not to be scored:
- the 0.08 door sill (clear 7.00 above it);
- the escape box stopping at 14.4;
- kit-size barrel and crate;
- the f34 governing over the other cells: chimney in the front half, a window on both long walls, five plank rows, the
  door-set scale.

## Stage 7 verification (round 1)

**Result: FAIL, 7.5 / 10.** Technically clean: kit_verify finds nothing, the escape scan finds no leaks and the walk
passes. One visual blocker: the roof framing (bargeboards and the eave line) is about half as heavy as the sheet draws
it, in the hero view and every elevation. Verified read-only on a copy of the work file (`wip/M068v.blend`) in a
background session; nothing was rebuilt or saved. Renders are in `<temp>/...`.

### Technical (re-measured)

- **kit_verify** (`cls="building"`, the builder's `VERIFY` options plus the brief's size and every stored point):
  **0 problems** (49 s).
  - Hero: 7532 / 8000 tris, 328 shells, 20.652 × 24.413 × 19.400.
  - All zero: non-manifold edges, bowties, boundary, wire, loose, zero-area faces, n-gons, duplicate verts, winding
    errors, self-hits, parity-inward faces and negative volumes.
  - Normals outward; origin at the bottom centre (offset (−0.022, −0.494, 0)); transforms applied; no modifiers or
    custom normals; thinnest corner 1.04°.
  - Floating 0, unchained 0 (34 grounded shells), buried 0 (deepest 0.042, rope in pole); pierces 0.
  - UV: 0 overlaps, 0 flips, island gap 0.016, border 0.008, density 0.998–1.001.
  - Tint against normal: worst 0.0.
  - Sockets: chimney_smoke at (2.20, −1.95, 18.60) and three heat_glow, exactly as Stage 6. The Lantern and Chimney
    parts carry one each. Glow key `m068_glow`.
  - Every stored point is present, and the hinge's axis matches LEAF / HINGE in the build frame. `K.check` is clean.
  - All 12 parts are clean and under 1000 tris; the largest is the Banner at 632.
- **Escape scan:** 709,501 rays from 733 interior, 224 floor and 146,367 seam points: 16,925 leave by the door and
  **0 leave anywhere else**.
- **Interior renders:** flat renders on a magenta background, six cube faces from each of three points: room centre
  (0, 0, 6), back-left corner (−5, 5.5, 3.2), and high under the +X slope by the door (4.5, −5.5, 12.5). Magenta shows
  only toward the door. Every sampled magenta pixel traces back through the doorway, grazing the jambs at most (x
  ±1.94 at the outer wall plane). No see-through seams.
- **Walk:**
  - Rises 0.87 / 0.86 / 0.87, then the 0.08 sill.
  - Minimum clearance 0.40 (blk_F1 beside the stairs); 0 intersecting steps.
  - Headroom 7.00 in the doorway.
  - Turning room: 3.44 at the room centre and 2.83 at both back corners, 0 intersecting yaws.
- **house_check:** floor tops 2.60 everywhere; door x ±1.80, top 9.683, so 7.003 clear above the sill; stair tops
  1.73 / 0.87; headroom 9.41 under every interior member.
- These numbers match Stage 2 to the last digit.

### Views against the sheet

`compare.compare(68, COMPARE)` at 480 px, f34 / front / side again at 724 px, plus matched crops of the f34 at 3.2×
sheet scale. Colours are medians of matching regions, sheet / ours.

- **f34 (hero), W : H 1.336 / 1.216.** The layout matches:
  - the door gable on the right; the barred window toward the front of the −X wall, with its lantern on an eave
    bracket over the front jamb;
  - two door lanterns; the stone course with taller corner blocks; the 4 × 2 canvas grid with four golden ties per
    eave;
  - the chimney in the front half of the +X slope; the banner pole at the back-left corner; two-tread stairs.

  The stone-to-post ratio at the front corner matches (sheet 0.52, ours 0.47). The door stands open (house rule); the
  barrel and crate are kit-sized (ruled). Colours:

  | Region | Sheet | Ours |
  | --- | --- | --- |
  | −X wall | `#A8551E` | `#A3571E` |
  | Banner | `#E51B1C` | `#DB191A` |
  | Lantern glass | `#FAC816` | `#FFBE21` |
  | Barrel | `#B86115` | `#B36025` |
  | Stone, front corner block | `#A79798` | `#978D8E` |
  | Canvas | `#FEF2CE` | `#FFFFE2` (clips; recorded, not scored) |

  Where it differs, see Blocker 1 and the minors.
- **Front (−42, 8), W : H 1.318 / 1.315.** Same content and layout. This cell shows the thin framing most clearly: the
  back gable's bargeboard is a near-vertical block about 2 studs wide on the sheet and a thin diagonal on ours. The
  banner and its pole read small and low (Minor 1).
- **Side (90, 3), W : H 1.04 / 1.17.** The extra width is our stairs inside the crop. The proportions match: plate
  0.574 / 0.583 of the chimney top, ridge 0.82 / 0.83, chimney above the ridge 0.15 / 0.17, stone course 0.153 /
  0.143. The face is about 30 % darker from the studio light (recorded). Frame members compared with the planks on
  the same face:
  - window frame: sheet `#F19335` against `#C56A28` planks (about 1.25×), ours `#90521F` against `#824618` (1.1×);
  - corner posts: sheet `#DA752A`, about 1.1× the planks; ours the same as the planks;
  - bargeboards about 1.8 studs wide on the sheet and 0.9 on ours;
  - corner posts about 1.8 studs on the sheet and 1.1 on ours.
- **Rear (−90, 3, mirrored), 1.217 / 1.244.** Same reading as the side cell. The extra window, the plank row and the
  chimney position are all ruled.
- **r34 (mirrored), 1.305 / 1.199.** A redraw, judged on content: crossed bargeboards, a collar and frame posts on the
  back gable, the window, the banner on its X-lashed crossarm, the barrel. The r34's gable lantern and mirrored
  dressing are recorded misses.
- **Top (turned), 1.266 / 1.185.** Content matches: the panel grid, ties on both eaves, the chimney with its dark
  flue, the frame ends and the barrels. The stairs on the gable are a recorded miss.
- **Close-up A** against `junction_cu`: the octagonal eave-beam end with a pale end face, the iron bracket plate with
  two rivets and a golden peg are all there.
- **Exploded:** every labelled part has a counterpart.

### Blockers

1. **The roof framing is about half the sheet's weight.** Seen in the f34 (governing), front, side and rear.
   - **Bargeboards.** Ours are 0.90 wide (`BB_Y` 9.25–10.15) by 0.92 deep. The sheet draws them about 1.6–1.8 wide:
     side and rear cells 55–60 px against our 28 at the same scale; the f34's back gable board about 1.3 studs
     apparent against our 0.67. The sheet's crossed tips are heavy blocks wrapped by the golden saddle, where ours
     read as thin sticks with a small cap.
   - **Eave line.** On the sheet a thick eave beam, about 1 stud of visible face, runs under the canvas edge the full
     length, and the golden U ties wrap it. On ours the plate sits 0.25 behind and under the canvas edge, so the hero
     view shows only the 0.12 canvas edge with small ties.
   - **Side effect.** In the f34, a pale sliver of the +X slope's underside shows between the front bargeboard and
     the gable boards. The sheet's wider board covers that gap.
   - **Fix:**
     - Widen the bargeboards outward to about 1.6 (`BB_Y` ≈ (9.25, 10.85)) and deepen them to about 1.1 (`BB_D`);
       scale the cleats, saddle and tip blocks to match.
     - Bring a fascia or eave beam out to the canvas edge: either move the plate out to |x| ≈ 7.0–7.55 so its outer
       face is flush with or just proud of the canvas edge, or add a fascia board of about 0.5 × 0.8 under the edge
       along the full eave. Re-seat the ties so they wrap it.
     - Expect hero depth to grow by about 1.4 (update `TARGET_SIZE`) and roughly 50 tris for the fascia.
     - Re-run kit_verify with escape and walk, and re-check the f34 / front / side pairs.

### Minors (recorded; fix if cheap)

1. **Banner and pole read small and low.**
   - Cloth: 6.40 drop × 2.14 wide. The sheet measures about 7.8 × 2.35 in the f34 and about 8.4 × 3.1 in the front
     cell.
   - Pole: ours stops 0.5 above the crossarm, plus the block. The f34 and front show about 2–2.5 studs of pole and a
     block above the arm.
   - Fix: `BAN_DROP` to about 7.6, the sleeve span to about 2.5, and `POLE_TOP` up about 1.5 with `ARM_Z` unchanged.
     The pole is not a ruled kit-size prop.
2. **Frame members don't read lighter than the planks.**
   - The window frame (`mix(TIMBER, TIMBER_END, 0.30)`) renders darker than the planks around it on the side face.
     On the sheet it is the brightest wood on that face, and in the f34 it is `#DB7924` against `#A8551E` planks.
   - Corner posts and door posts are a step lighter on the sheet: door post `#EF8830` against ours `#AE5D21`.
   - Fix: the window frame toward `TIMBER_END` (about 0.7), and a slight `TIMBER_END` lift on post faces.
3. **Corner posts:** about 1.8 wide in the side and rear elevations, about 1.25 in the f34; ours are 1.10. Judge this
   after Blocker 1. The f34 governs, so it is minor.
4. **Gable infill** above the collar: horizontal planks on the sheet (f34 and front), vertical boards on ours.
5. **Ridge beam:** a round log with two golden bands in the exploded panel; ours is a pitched-top square beam. Only
   the ends show in the assembled views.
6. **Stairs:** the sheet's upper tread spans the door posts (about 5.8–6.4 wide); ours is 4.80, narrower than the
   posts.
7. **Lantern iron:** reads darker than the sheet's lit grey-brown (`#958282` against `#5F5B5E`). The glass matches.
8. **Exploded render:** the RoofPanel almost vanishes, cream on the pale floor, in `exploded.png`. The part itself is
   fine (7.53 × 18.49 × 4.97, 456 tris). This is presentation only.

## Main session after round 1 (2026-11-04)

Fix round:
1. **Blocker: heavier roof framing, as the verifier gives it.**
   - Bargeboards about 1.6 wide and 1.1 deep, with the cleats, saddle and tips scaled to match.
   - A visible eave beam or fascia under the canvas edge along the full eave, with the ties re-seated on it.
   - Update `TARGET_SIZE`, then re-run kit_verify with the escape scan and the walk.
2. **Minors 1, 2, 6 and 7:**
   - a bigger banner and a taller pole;
   - the window frame the brightest wood, and door and corner posts a step lighter;
   - the upper stair tread spanning the door posts;
   - lantern iron toward `#5F5B5E`.
3. **Minor 3:** re-judge the corner posts after the blocker fix; about 1.25 if they still read thin in the f34.

Minors 4, 5 and 8 stay recorded. Round 2 goes to a fresh verifier.

## Fixes after round 1

Applied the main session's fix list in `m068.py` and rebuilt in a background session on the light work file. No part
was renamed or dropped.

### Blocker: roof framing

- **Bargeboards** 1.60 wide × 1.10 deep (`BB_Y` (9.25, 10.85), `BB_D` 1.10; were 0.90 × 0.92), 0.98 proud of the
  canvas. Cleats 0.50 × 0.36 × 2.10 (0.25 past both faces), the saddle 0.90 wide and 0.57 over the V (`SADDLE`). Heels
  stop at x 7.30 on the eave beam's top: past 7.455 the board's underside clears the beam's top chamfer (0.025–0.06).
  The ridge beam's pale ends stay 0.90 past the boards (`RIDGE_END` 11.75), its golden band 0.37 from each end.
- **Eave beam** (`PLATE`): 1.25 × 1.00 (was 0.90 × 0.80), x 6.30–7.55, z 10.20–11.20. Its outer face is 0.10 proud
  of the canvas edge, which rests on its top corner (0.016 off at the chamfer start). The beam ends reach |y| 11.90,
  1.05 past the boards. To keep the beam top at 11.20 and five plank rows, `ROW_PITCH` is now 1.58, so the rows top
  out at 10.20 and the window, bars and shutter follow (opening 5.46–8.62). The door (top 9.68, clear 3.60 × 7.00 over
  the sill) did not change; the lintel is 0.52 deep. The beam faces take the posts' timber_end lift (0.20), so the beam
  reads apart from the top plank row.
- **U ties** re-seated by the same profile: over the canvas edge, round the beam's outer chamfer, down its 1.00 face
  and under it to the wall. They now wrap a visible beam, as on the sheet.
- **Bracket plates, pegs and rivets** (close-up A): recentred on the deeper beam (plate z 10.43–10.97), 0.62 in from
  the beam end, so they clear the bargeboard foot.
- **The pale sliver** of +X canvas underside between the gable boards and the bargeboard (f34, front): closed by a fly
  rafter under each gable overhang (`FLY_Y`, four rafters, 64 tris). The outer purlin segments now butt them.
- **Gable infill:** the outer board round the eave beam's inner edge gets its own fan (`faces`). With the 1.00 beam,
  the ear-clipper had left 0.315° slivers there; the thinnest hero corner is back to 1.008°.
- The eave lantern L1 moved out to x −8.65 (base (−8.65, −5.40, 6.50), glass socket (−8.65, −5.40, 7.50)) to clear the
  wider beam. The bracket arm is still about 1.1 long.

### Minors 1, 2, 3, 6, 7

- **Banner** (Minor 1): cloth drop 7.60 (was 6.40), sleeve span 2.50 (was 2.14), emblem 1.40 × 2.25. The arm's outer
  iron band and knob moved out 0.36. `POLE_TOP` is now 14.40, so 2.0 of pole stands over the crossarm (`ARM_Z` 12.40
  unchanged), with the block on top at 15.00.
- **Frame members** (Minor 2): window frame `mix(TIMBER, TIMBER_END, 0.85)` (was 0.30). Post faces get a timber_end
  lift: corner posts 0.20, door posts 0.65 (`POST_LIFT`, `DPOST_LIFT`).
- **Corner posts** (Minor 3): re-judged in the f34 after the blocker fix and still thin beside the heavier framing.
  Now 1.25 square (`POST` 6.10–7.35 × 7.10–8.35).
- **Stairs** (Minor 6): the upper tread is 6.00 wide, spanning the door posts (|x| 1.80–2.90). Its blocks moved out to
  |x| 2.10–2.70. The lower tread stays 4.80. Rises are unchanged.
- **Lantern iron** (Minor 7): measured first, against the round-1 render. In the f34 the lit lantern roof is
  `#8A7B7B` on the sheet and was `#5E5A5F` on ours, and the bracket `#605A61` against `#4C494D`. Ours was darker, so
  the lanterns and their brackets get a new lighter, warmer key `m068_lantern_iron` `#797175` (roughness 0.6, metal
  0.3). Other iron keeps `m068_iron`.

### Re-measured

- **kit_verify** (`cls="building"`, the builder's `VERIFY`): **0 problems**. The hero is 7596 / 8000 tris (+64, the
  fly rafters), 332 shells, 20.76 × 24.74 × 19.40 (`TARGET_SIZE` updated), offset (−0.076, −0.331, 0).
  - Zero non-manifold, boundary, zero-area, n-gons, duplicate verts, winding errors, self-hits, parity-inward faces
    and negative volumes.
  - Thinnest corner 1.008°. Floating 0, buried 0 (deepest 0.029).
  - UV: 0 overlaps, gap 0.016, border 0.008.
  - Sockets: chimney_smoke at (2.20, −1.95, 18.60), heat_glow at L1 (−8.65, −5.40, 7.50) and L2 / L3
    (∓4.70, −9.10, 7.20). Every stored point is present.
  - Parts unchanged in tris, all clean: RoofPanel 456, RidgeBeam 280, Chimney 132, Banner 632, Lantern 180,
    WallPanel 336, WindowWall 488, DoorFrame 288, GableFrame 176, Floor 464, Stairs 160, Foundation 180.
- **Escape scan:** 711,553 rays from 757 interior, 224 floor and 144,491 seam points. 16,740 leave by the door and
  **0 leave anywhere else**.
- **Walk:** rises 0.87 / 0.86 / 0.87, then the 0.08 sill; minimum clearance 0.40 (blk_F1); 0 intersecting steps;
  headroom 7.00 in the doorway. Turning room is 3.44 at the room centre and 2.83 at the back corners, with 0
  intersecting yaws.
- **house_check:** floor tops 2.60; door x ±1.80, top 9.683, so 7.003 clear over the sill; stair tops 1.73 / 0.87;
  interior headroom 9.41.
- **Framing against the sheet** (side cell, scaled by eave height over the ground in each image):

  | Member | Sheet | Ours, round 1 | Ours now |
  | --- | --- | --- | --- |
  | Bargeboard band | about 1.9 studs | 0.97 | 1.60 |
  | Visible eave-beam face | about 1.1 | 0.70 | 0.88 (1.00 tall; the canvas edge covers the top) |

  In the f34 and front cells the bargeboards and the crossed tips now read as heavy blocks. The eave beam shows
  under the whole canvas edge with the ties wrapping it. The top cell shows the wide boards and beam ends.
- **Colours** (f34 unless noted; sheet / ours, after):

  | Region | Sheet | Ours |
  | --- | --- | --- |
  | Planks | `#A8531E` | `#A3571E` |
  | Window jamb | `#DD7B26` | `#C87C34` (was `#C17630` at 0.70) |
  | Door post | `#EE872F` | `#CA7A32` (was `#AE5D21` in round 1) |
  | Corner post | `#A0501E` | `#AD6123` |
  | Lantern roof | `#8A7B7B` | `#897C7A` |
  | Lantern bracket | `#605A61` | `#716665` |
  | Side cell: window jamb against planks | `#F8A64A` against `#BF6628` | `#9F632A` against `#834618` |

  The window frame is now the lightest wood on its face. The side face is still about 30 % darker under the studio
  light (recorded).
- **Renders:** `M068_views.png`, the sheet views, exploded, scale and the seven close-ups were re-rendered.
  `m068.compare()` writes `<temp>/RBLX-Flintborn/compare/M068/M068_compare.png`.

## Stage 7 verification (round 2)

**Result: PASS, 8.5 / 10.** Round 1's blocker is fixed: the bargeboards and the eave beam now carry the sheet's
weight in the f34, front, side and rear cells. The model is technically clean: kit_verify finds nothing, the escape
scan finds no leaks and the walk passes. Nothing left is a blocker; the minors below are recorded. Verified read-only
on a copy of the work file (`wip/M068v.blend`) in a background session; nothing was rebuilt or saved. Renders are in
`<temp>/...`.

### Technical (re-measured)

- **kit_verify** (`cls="building"`, the builder's `VERIFY` with escape, walk and sockets, plus `TARGET_SIZE` and
  every stored point): **0 problems** (40 s).
  - Hero 7596 / 8000 tris, 332 shells, 20.760 × 24.739 × 19.400, offset (−0.076, −0.331, 0).
  - All zero: non-manifold edges, bowties, boundary, wire, loose, zero-area faces, n-gons, duplicate verts, winding
    errors, self-hits, parity-inward faces, negative volumes and shells unmatched to the register.
  - Normals outward; origin at the bottom centre; transforms applied; no modifiers or custom normals; thinnest
    corner 1.008°.
  - Floating 0, unchained 0 (34 grounded shells), buried 0 (deepest 0.029, rope in pole); pierces 0 (12 thin
    shells).
  - UV: 0 overlaps, 0 flips, island gap 0.016, border 0.008, density 0.999–1.002.
  - Tint against normal: nothing judged. `timber_x_end_20` correlates −0.41 with z, but its spread is 0.8 %, under
    the 1.5 % floor: the posts' darker foot bands, which is colour by position.
  - Sockets: chimney_smoke (2.20, −1.95, 18.60), heat_glow at L1 (−8.65, −5.40, 7.50) and L2 / L3
    (∓4.70, −9.10, 7.20); the Lantern and Chimney parts one each. Glow key `m068_glow` (emission 1.0).
  - Stored points all present. The hinge axis (−1.80, −7.59, 2.62) in the build frame, closed yaw 0, open 95; the
    DoorFrame's open yaw 0. `K.check` clean. Collision keys as the brief.
  - All 12 parts clean and under 1000 tris, tri counts as "Fixes after round 1" (Banner 632 the largest).
- **Escape scan:** 711,553 rays from 757 interior, 224 floor and 144,491 seam points: 16,740 leave by the door and
  **0 leave anywhere else**.
- **Interior renders:** flat renders on a magenta world, six cube faces from each of seven points (room centre,
  both front corners low, back-left low, back-right high, high under the +X slope by the door, high in the back
  gable). Magenta shows only toward the door. 8,188 magenta pixels were traced as rays; all cross the inner wall plane
  inside the doorway. One pixel grazes out past the jamb's chamfer (x −2.17 at the outer wall plane), as round 1
  found. No see-through seams at the re-pitched plank rows, the eave beam, the gable boards or the fly rafters.
- **Walk:** rises 0.87 / 0.86 / 0.87, then the 0.08 sill; minimum clearance 0.40 (blk_F1); 0 intersecting steps;
  headroom 7.00 in the doorway. Turning room 3.44 at the room centre and 2.83 at both back corners, 0 intersecting
  yaws.
- **house_check:** floor tops 2.60 everywhere; door x ±1.80, top 9.683, so 7.003 clear over the sill; stair tops
  1.73 / 0.87; interior headroom 9.41.
- These match "Fixes after round 1" to the last digit.

### Blocker check (round 1's roof framing)

- **Bargeboards: fixed.** They are 1.60 × 1.10. In the f34 the front gable's crossed boards, cleats and saddle now
  read as heavy blocks, as on the sheet. In the side and rear cells the board band is about 50 px against the sheet's
  45–55 px for a house of the same width. The pale canvas sliver at the front gable is gone.
- **Eave beam: fixed.** It now reads as a beam under the canvas edge along the whole eave, with the ties wrapping it.
  In the f34, measured against the top plank row on the same wall (6× / 4× crops), the visible beam face is 0.61 of a
  plank row on the sheet and about 0.56 on ours. In the side cell the band is about 20 px against the sheet's 25 px.
  The beam ends project with octagonal pale end faces, iron plates and golden pegs (close-up A).

### Fix-list items

- **Banner and pole (Minor 1): improved.** The pole stands 2.0 over the crossarm with its block, as in the f34 and
  front cells. The cloth is still a little small: its drop is 0.64 of the eave height in the front cell (sheet 0.77)
  and about 0.8 in the f34 (sheet about 1.0). Recorded (Minor 2 below).
- **Frame colours (Minor 2): done.** f34, sheet / ours: planks `#AE571E` / `#A5581F`, window jamb `#D67725` /
  `#C57A33`, door post `#F08831` / `#CA7A33`, front corner post `#9E4F1B` / `#AD6123`. The window frame is now the
  lightest wood on both long faces, and the door posts read a clear step lighter than the planks. They are still
  darker than the sheet's door post (Minor 3).
- **Corner posts (Minor 3): done** at 1.25, the f34's width. The side and rear cells draw about 1.7 (recorded, the
  f34 governs).
- **Stair tread (Minor 6): done.** The upper tread is 6.00 and spans the door posts, as in the f34. The walk is
  unchanged.
- **Lantern iron (Minor 7): correct against the sheet.** The fixer's reading holds. Grey-masked medians over each
  lantern in the f34, sheet / ours: door lantern `#8E7268` / `#665A59`–`#776867`, eave lantern `#6B5C60` /
  `#736766`. Ours lies inside the sheet's range; round 1's `#5F5B5E` target would have been darker than the sheet.
  The sheet's iron has more lit / dark contrast (lit `#ABA2A3`, dark `#3C3334`; ours `#948786` / `#6A5F5E`).
  Recorded, not scored. The glass is `#FDDB08` / `#FFBE21`.
- **No new problems from the fixes.** The five plank rows at pitch 1.58 close under the eave beam; the window
  (5.46–8.62) sits in rows 3–4. The fly rafters show only as a recessed second member under each front bargeboard
  (Minor 5). L1 at x −8.65 hangs clear over the window's front jamb.

### Views against the sheet

`compare.compare(68, COMPARE)` at 600 px, with matched crops at 2–6×. Colours are masked medians, sheet / ours.

- **f34 (hero), W : H 1.336 / 1.247.** The layout matches: the door gable on the right; the window toward the front
  of the −X wall with its lantern on an eave bracket; two door lanterns; the stone course with taller corner blocks;
  the 4 × 2 canvas grid with four ties per eave; the chimney in the front half of the +X slope; the banner pole at the
  back-left corner; two treads. The framing now reads as heavy as the sheet's. The difference in W : H comes from
  the sheet's oversized props (ruled). Colours: −X wall `#A5531D` / `#A3571E`, front wall `#B45C16` / `#B26021`,
  banner `#E71C1D` / `#DB191A`, front corner stone `#A69697` / `#9B9191`, −X stone run `#84777B` / `#958B8C`, canvas
  `#FEF1CD` / `#FFFFE2` (clips; recorded, not scored).
- **Front (−42, 8), 1.316 / 1.357.** Same content and layout. The back gable's board now reads as a heavy block, and
  the pole stands over the crossarm with its block. The banner is a little short and narrow (Minor 2).
- **Side (90, 3), 1.039 / 1.230.** The wall proportions match: stone length over eave-beam height is 1.61 on the
  sheet and 1.56 on ours. The extra width is the gable overhang (Minor 1). The bargeboard bands and the eave beam
  with its four ties match in weight. The window frame reads light. The face is about 30 % darker from the studio
  light (recorded).
- **Rear (−90, 3, mirrored), 1.217 / 1.257.** Same reading as the side cell. The extra window is ruled.
- **r34 (mirrored), 1.306 / 1.230.** A redraw, judged on content: crossed bargeboards, the collar and frame posts on
  the back gable, the window, the banner on its X-lashed arm, the barrel. The back gable sits in deep shade under
  the long overhang (Minor 1; the light is recorded).
- **Top (turned), 1.268 / 1.226.** Content matches: the panel grid, ties on both eaves, the chimney with its dark
  flue, the wide boards and the beam ends. The sheet's eave beams show about 0.8 outside the canvas edge from above;
  ours show 0.10 (part of Minor 4). The stairs on the gable are a recorded miss.
- **Close-ups:** close-up A (`junction_cu`) matches. In `apex_cu`, the crossed tips, saddle and banded ridge-beam end
  are all there. `door_cu` shows the open leaf, golden post caps and the wide upper tread. `inside_cu` and
  `underside_cu` show a dark shutter, rafters and purlins, and no gaps.
- **Exploded:** every labelled part has a counterpart. The RoofPanel is still faint on the pale floor (round 1's
  Minor 8, presentation only).

### Blockers

None. Nothing is broken, and nothing reads clearly unlike the sheet in the governing view.

### Minors (recorded; fix only if cheap)

1. **Gable overhang reads long in the side, rear and top cells.** Those cells draw the bargeboards over the corner
   posts: their outer face is about 0.5 past the corner stones, and the eave beam ends about 0.9 past. Ours are 2.1
   and 3.15 past (`BB_Y` (9.25, 10.85), `PLATE` end 11.90, stones to 8.75). Bargeboard length over stone length:
   sheet 1.05, ours 1.25 (side cell). Top cell length over width: 1.25 / 1.47. The f34 governs, and it shows the
   front board foot standing ahead of the corner post as ours does, so this is not scored. If the elevations should
   match: `BB_Y` about (8.40, 10.00) with the canvas ends and fly rafters following, and the beam ends at about 10.9.
   Re-run kit_verify with the escape scan and the walk after any such change.
2. **Banner still a little small** in the front cell (drop 0.64 / 0.77 of the eave height, width 0.18 / 0.27). It
   is close in the f34. A cheap fix: `BAN_DROP` about 8.4 and a `SLEEVE` span of about 2.9.
3. **Door posts** `#CA7A33` against the sheet's `#F08831`. A `DPOST_LIFT` of about 0.9 would bring them closer. The
   window jamb (`#C57A33` / `#D67725`) is close enough.
4. **Eave beam distinctness.** Its weight is right, but it has the planks' tone (lift 0.20) and sits 0.55 proud of
   the wall. The sheet's beam reads as a separate member, with a lit top bevel, a shadow under it and chunkier ties
   (about 0.4 wide against our thin straps). From above it shows about 0.8 outside the canvas edge (ours 0.10).
5. **Fly rafters** show under the front bargeboards as a second, recessed member with a dark slot (f34 and front).
   The sheet draws one solid board there. Harmless; recorded.
6. **Lower stair tread** 4.80 against the upper 6.00. The sheet's two treads are about the same width.
7. **Standing recorded minors:** vertical gable infill (sheet: horizontal planks), the square ridge beam (sheet: a
   round log), the faint exploded RoofPanel, and corner posts drawn about 1.7 in the side and rear cells.
