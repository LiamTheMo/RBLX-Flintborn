# 050 Timber Bridge — spec

Reference: `art/blender/assets/references/050.png` (remade 2026-11-03, "TIMBER BRIDGE / BUILDING MODEL STUDY"). The
earlier spec followed the old sheet; git history keeps it. Builder: `art/blender/kit/mcp/m050.py` (on `kit_parts` /
`kit_build`). Procedure: `art/blender/kit/mcp/STAGES.md`, `HOUSE_RULES.md`.

## Brief

- **Sheet:** 050 Timber bridge (remake: yes). Family: none.
- **Class and budget:** structure (a bridge, walked on), ceiling 6000, plan 5400. Built: hero 4416, parts ≤ 338.
- **Size:** the side view (one scale, 4 posts) measured in sheet px: post centres 233.5 / 326.5 / 416.5 / 509.5 (bay
  92 px), posts 20 px, deck and stringer ends 214–528 (314 px), post tops 104 px above the ground line, deck top 59 px,
  boards 12 px, stringer 14 px; R6 90 px (= 5 studs → 18 px/stud). The tiling cell puts 3 bays + an end-post gap of
  ~0.7 post widths in one module, which is the 314 px span, so the module is one **16-stud tile** (0.051 stud/px; R6
  scale would give 17.4, 8 % larger). Hero **15.996 L × 6.780 W (pegs, ±3.390) × 4.90 H**; deck top 2.60.
- **Hero view:** f34 at camera (-37, 23) (fitted from the cap positions: along / across foreshortening). r34 is a
  redraw of the f34 (content only). Front and rear cells are the short ends (az -90 / 90), side is the -Y long
  elevation (az 0), top is a two-bay plan drawn turned (content only).
- **Parts:**
  | Part | What | Tris target |
  | --- | --- | --- |
  | TimberBridge (hero) | 8 legs and 8 upper posts on the stringer line, 16 boards + 2 end strips, 2 stringers on the long sides, 4 crossbeams, 4 knee braces, 12 blocks (8 pegged), 16 rope turns, 6 rope rails | ≤ 5400 (4416) |
  | TimberBridgePost | upper post with its two turns, side block and end block | ≤ 500 (338) |
  | TimberBridgePlank | one deck board 0.87 × 0.54 × 6.0 | 28 |
  | TimberBridgeStringer | full-length 16.0 stringer | 28 |
  | TimberBridgeCrossbeam | crossbeam between the stringers | 28 |
  | TimberBridgeBrace | 38° knee brace in the long-side plane | 12 |
  | TimberBridgeRope | one sagging rope rail (one bay) | 152 |
- **Palette:** swatches (header and §5, flat medians): wood `#C16926`, tan `#E9BA7E`, cream `#E5D9C8`, grey `#A7ADB2`,
  green `#78A949`, blue `#0FA2DA`. Rendered f34 targets: board tops `#E78237`, cap tops `#FBA13E`, post faces
  `#933F06` / `#AE4D0A`, blocks `#BA530B`, legs `#843A0B`, stringer `#703410`, brace `#73350A`, rope `#F7C556`, pegs
  `#F8CB61`. Keys: `m050_wood` (boards), `m050_wood_deep` (posts and legs), `m050_block` `#A4530B` (side and end
  blocks), `m050_wood_dark` (stringers, crossbeams, braces), `m050_wood_light` (cap tops), `m050_rope` / `m050_rope_dark` (groove strand),
  `m050_peg`; all matte (rough 0.85–0.95, pegs 0.55), metal 0. Cream, grey, green and blue unused (sheet chrome).
- **Lights / VFX:** none (the sheet shows no glow, light or effect).
- **Collision:** hero precise (walked on); Post hull, Plank / Stringer / Crossbeam box, Brace hull, Rope none.
- **Checks to switch on in kit_verify:** `cls="structure"`; `walk` along the deck (paths y 0 / ±0.6 from x -7.95 to
  7.95, feet z 2.60, boards skipped as the floor, turning at (0, 0) and (-4.7, 0)); `seams` pitch (16, 0, 0).
- **Departures from HOUSE_RULES:** none. Notes:
  - deck top at the house raised-floor 2.60 (sheet scale gives 3.0): the legs under the stringers are 0.4 shorter than
    the sheet draws them; above-deck heights are the sheet's (posts 2.30 above the deck);
  - the module length is the house 16-stud pitch (R6 scale gives 17.4).
- **Questions for the main session:** none. (A deck at 3.0 would match the sheet's leg length exactly; one constant.)

### Reading the sheet (recorded misses, not blockers)

- The front and rear (short-end) cells draw a rope swag across the end and two braces in the end plane; the f34 / r34
  (governing) and the notes ("Both short ends are open") show open ends and knee braces on the long sides in the end
  bays (side cell agrees). Built: open ends, four long-side knee braces (= "two braces per short end").
- Front / rear cells draw the end deck as four board ends; the governing views lay the boards across the width.
- The top cell is a two-bay plan (3 post rows) with edge strips; built three bays as every other cell.
- The exploded view's corner "L" pieces and leg stubs are construction shorthand; posts are one piece ground to cap.

## Stage 1 — Modelling (2026-11-04)

Build frame: long axis X, front -Y, ground z 0, symmetric about both axes. Seam contract in the builder docstring.
- **Posts:** 8 at x ±2.35 / ±7.05 (bay 4.70), y ±2.50; 1.0 square, vertical edges chamfered 0.05, 0 → 4.90, an
  0.08 cap bevel to a flat top (the sheet's softened cap). One shell each.
- **Deck:** 16 boards across the width, 0.87 × 0.54 (top 2.60, bottom 2.06), 0.04 edge chamfer, 0.94 pitch (5 to a
  bay, 4 between posts as the side cell draws). The 4 boards on post rows run between the posts' inner faces (sunk
  0.01); the rest run the full width to y ±3.0 (the posts' outer faces). An end strip (0.445 wide, square edges so the
  end section is one flat face) runs full width from 0.003 off the end posts to the seam at x ±7.998.
- **Frame:** 2 stringers end to end (x ±7.998, |y| 1.40–2.01, z 1.42–2.07: sunk 0.01 into posts and boards; the side
  cell's beam ends past the end posts), 4 crossbeams on the post rows between them (0.6 wide).
- **Blocks and pegs:** a 1.1 × 1.05 × 0.25 block on every post's outer long face (z 1.45–2.50, 0.003 off the face), a
  0.65-tall block on each end post's end face under the end strip (to x ±7.84); a square peg (0.40, proud 0.10, low
  pyramid dome 0.04: `P.bolt`) centred on each — the junction close-up's square peg.
- **Braces:** 4 knee braces, 45°, 0.45 wide, |y| 1.85–2.35 (straddling the leg face and stringer underside), from the
  end leg's inner face at z 0.30–0.94 to the stringer underside 1.13 along (side cell ≈ 1.3 at sheet scale).
- **Rope:** two turns per post (Ø 0.22, centres z 3.93 / 4.13, sunk 0.02, touching), loops following the post's
  offset outline with rounded corners; six rails (Ø 0.22), catenaries from wrap to wrap at z 4.03 sagging to 3.32 (0.72
  above the deck), ends seated 0.025 into the turns. No rope across the ends.
- `P.rope_band` (8-point twisted turns) read as flat plates with mitre spikes on a square post; the builder's own
  `wraps()` (12 points, 6-sided, spiral groove strand, corner arcs about a point 0.10 inside the post corner so the
  tube never folds) reads as round coils. **Candidate for kit_parts:** a rounded-rectangle turn round square timber.

## Stage 2 — Optimisation and cleanup

kit_verify (`cls="structure"`, walk, seams): **problems []**. Tris: hero 4696 / 6000 (rope 16 turns × 144 + 6 rails ×
152 = 3216, 68 %); parts Post 400, Plank 28, Stringer 28, Crossbeam 28, Brace 12, Rope 152. 82 closed shells, 0
non-manifold / bowtie / boundary / loose / zero-area / n-gon, 0 winding errors, floating 0 / unchained 0, buried 0
(deepest 0.061 rope in rope, limit 0.08), min corner 7.5°. Sizes 15.996 × 6.786 × 4.90, origin bottom centre,
transforms applied. Deck check: 54 samples, every board top 2.600.
- **Walk:** centre path clearance 0.63, side paths (y ±0.6) 0.238 to the turns, 0 intersecting steps, no rises
  (level 2.60 end to end), no headroom limit (nothing overhead); turning at (0, 0) and (-4.7, 0) clearance 0.708, 0
  intersecting yaws. Clear width between the turns 3.60 (posts' inner faces 4.0).
- **Seams:** pitch 16: 0 crossing triangle pairs, gap at the seam 0.004, nothing past ±8.000, end sections identical
  (z 1.42–2.60, mismatch 0.0).

## Stage 3 — UV

kit_build cleanup (Smart UV, margin 0.008): 740 islands, 0 overlaps, 0 flips, min gap 0.016, border 0.008, density
even, conformal stretch p95 1.107.

## Stage 4 — Materials, colour and texture

Calibrated by rendering the hero at the f34 camera with `compare.py` and matching the same regions of the sheet's f34
(per-channel linear ratios), not the dome, because the studio lights the posts' -X faces far more than the sheet:

| Region | Sheet | Ours |
| --- | --- | --- |
| Board tops | `#E88438` | `#E28437` / `#E58536` |
| Cap tops | `#FBA33F` | `#FFA03E` |
| Post -Y face | `#AC4B0C` | `#AE4D17` |
| Post -X face | `#7C3403` | `#A34816` (studio light; recorded) |
| Legs | `#843A0B` / `#6C2F05` | `#873911` / `#903D12` |
| Side block | `#BA540C` | `#B3581D` |
| Rope (Y median) | `#FBD064` | `#FFD05A` |

Final keys: wood `#B47031`, wood_light `#E8873A`, wood_deep `#9C4E1B`, wood_dark `#7A3812`, rope `#E2AE55`,
rope_dark `#C99441`, peg `#EDBF5E`. Colour by role and position only (legs below z 1.42 70 % toward wood_dark, cap
bevel 60 % and top toward wood_light); per-board Tint ±6 % so the deck is not one flat colour; K.check / Tint vs normal
worst 0.0. Class shares (f34): sheet W 55.4 / K 37.0 / Y 7.6, ours W 72.7 / K 15.7 / Y 11.6 — the W / K split is the
lighting (the sheet's light falls from the left, darkening post sides and the deck underside); Y is higher because
the turns are wider in the render than the sheet's thin drawing at that scale (rails cut to Ø 0.22, turns Ø 0.22).

## Stage 5 — Lighting: skipped

The sheet shows no lantern, glow or emissive part. No Studio-side lighting needed.

## Stage 6 — VFX: skipped

No smoke, sparkle or other effect on the sheet; no sockets.

## Renders and compare

`build(close=True)` writes `M050_views.png` (f34, r34, side, front, rear, top, exploded, scale), `joint_cu.png`,
`under_cu.png`. `m050.compare()` writes the side-by-side sheet to `<temp>/RBLX-Flintborn/compare/M050/`
(cell boxes in `m050.COMPARE`). W : H, sheet / ours: f34 1.650 / 1.631, r34 1.633 / 1.632, side 3.149 / 3.268,
front 1.444 / 1.361, rear 1.458 / 1.361, top 0.623 / 0.421 (two-bay plan).

## Modeller's notes for the verifier

- Leftover look differences: legs shorter than the sheet's (deck 2.60 rule); the short-end cells' end swag and
  end-plane braces (not built, hero governs); the sheet's turns read as fatter twisted coils in the junction close-up
  than ours (smooth 6-sided tubes with a groove strand); post -X faces lighter than the sheet (studio light).
- Stored points and sockets: none.

## Stage 7 verification (round 1)

**Result: FAIL, 6/10.** Technically clean; one visual blocker: the frame (stringers and knee braces) sits a stud
inside the long sides, so the hero view loses the timber beam under the board ends and the diagonal braces.

### Technical (kit_verify, re-run on a copy of the work file, 2026-11-04)

`kit_verify.run` on the hero and all six parts, `cls="structure"`, `size` (15.996, 6.786, 4.90), the builder's `WALK`
paths and turns, `seams` pitch (16, 0, 0): **problems []** (2.1 s).
- Hero 4696 / 6000 tris, 82 shells (post 8, rope_wrap 16, block 12, peg 12, plank 18, stringer 2, crossbeam 4, brace
  4, rope_rail 6). 0 non-manifold, bowtie, boundary, wire, loose, zero-area, n-gon or duplicate; 0 winding errors,
  self-hits, parity-inward or negative shells; min corner 7.52°. Floating 0, unchained 0, 8 grounded; buried 0
  (deepest rope_rail in rope_wrap 0.061, under the 0.08 rope pair limit). UV 740 islands, 0 overlaps / flips, gap
  0.016, border 0.008, stretch p95 1.107. Tint against normal worst 0.0. Transforms applied, origin bottom centre,
  no modifiers or custom normals, K.check clean, no sockets (none wanted).
- Parts: Post 400, Plank 28, Stringer 28, Crossbeam 28, Brace 12, Rope 152, each one or more clean closed shells.
- Size 15.996 × **6.780** × 4.90. The spec and builder docstring give 6.786 / pegs to ±3.393; the pegs reach ±3.390
  (within the 0.01 target tolerance).
- Walk: centre path clearance 0.63 (to the crossbeams below the feet), side paths ±0.6 clearance 0.238 to the turns,
  0 intersecting steps, level 2.60 end to end, nothing overhead; turns at (0, 0) and (-4.7, 0) clearance 0.708, 0
  intersecting yaws.
- Seams at 16: 0 crossing pairs, gap 0.004, extent ±7.998, nothing past the seams, end sections identical
  (z 1.42–2.60, mismatch 0.0).

### Views against the sheet

`compare.py` (the builder's `COMPARE` boxes) into `<temp>/.../cmp/`, and again at 570 px high for f34, r34, side and
front. W : H sheet / ours: f34 1.650 / 1.631, r34 1.633 / 1.632, side 3.149 / 3.268, front 1.444 / 1.361, rear
1.458 / 1.361, top 0.623 / 0.421.
- **f34 (governs):** layout, post count (4 + 4), three bays, five boards a bay across the width, the post heights
  above the deck, the two turns under each cap and six sagging rails all match. The long sides do not: on the sheet
  each long side shows a board-end face and directly under it a thick stringer face (column at render x 570 between
  front posts 2 and 3: board end 16 px, then stringer 25 px, `#552007`–`#73350E`, then the ground shadow), the pegged
  block bridging post and stringer, and a large knee brace in the long-side plane from the end leg up to the
  stringer. Ours shows only the 0.54 board end (25 px) and then open background. The boards look like a slab on four
  pairs of free-standing legs, and the braces are barely visible slivers behind the legs.
- **Joint close-up:** the sheet's stringer runs under the board ends, flush with the post's outer face, with the block
  over the junction and the brace dropping from the stringer underside. In `joint_cu.png` and `under_cu.png` there is
  only shadow under the board ends.
- **Side:** heights check out against the sheet in sheet px (0.051 stud/px): post tops 2.35 above the deck (ours
  2.30); turns 0.71–1.22 below the top (ours 0.66–1.08); rail sag 0.64 (ours 0.72), low point 0.74 above the deck
  (ours 0.72); side block 0.2–0.9 below the deck top (ours 0.1–1.15); four boards visible between posts. Brace: the sheet's
  runs at about 38° and reaches 1.6 along the stringer underside from the leg face. Ours is 45° and reaches 1.13 (low
  end height matches, 0.35–0.9 after scaling to our 1.42 stringer underside). Past the end posts the sheet draws the
  end block at deck level (top at the deck top, about 0.5 proud) above a short stringer stub. Ours has the end strip
  0.45 past the posts with the end block tucked under it.
- **r34:** a redraw of the f34; same content and the same long-side difference.
- **Front / rear:** as recorded in the brief (end swag and end-plane braces drawn there; the governing views and the
  notes have open ends). Not scored.
- **Top:** two-bay plan (recorded). Its content includes a beam strip along each long side on the post line, which
  agrees with the f34 / close-up reading of the stringers.
- **Exploded / parts:** six parts as the parts panel lists (Post x8 with turns, Deck Plank, Stringer x2, Crossbeam x4,
  Brace x4, Rope Segment x6). The sheet's exploded view drops the posts onto the stringer line, with legs below.
- **Colour** (hex medians, sheet f34 / ours at the same camera): board tops `#E58038` / `#E88839`, cap tops
  `#FDA746` / `#FFA742`, post -Y face `#AC4C0A` / `#AE4D17`, side block `#B9540A` / `#AA4C16`, leg -Y face
  `#A84C0F` / `#903D12`. Post -X face `#7B3304` / `#A34816` and board end faces `#A35012` / `#CC752C` are studio
  light (recorded).

### Blockers

1. **Stringers and knee braces sit inside the long sides.** Stringers are at |y| 1.40–2.01 and braces at |y|
   1.85–2.35, while the board ends and post outer faces are at 3.00. The hero, r34 and joint views lose the sheet's
   continuous timber beam under the board ends and its visible diagonal braces. The Stringer part note ("beam under
   the board ends") also does not match the geometry. **Fix:**
   - Move the stringers onto the post line, outer face 0.03–0.05 inside the board ends (about |y| 2.05–2.95, z
     1.42–2.07, full length to ±7.998 as now, so Stringer stays "x2"). The sheet's exploded view stands the posts on
     the stringer line with legs below, so split each post at the stringer into a leg (0 → 1.43) and an upper post
     (2.06 → 4.90), each seated 0.01 into the stringer. Keep TimberBridgePost as the upper post with its turns and
     block; the leg goes into the hero. Bay segments between the posts, seated in the posts' ±X faces, are the
     fallback.
   - Widen the crossbeams to meet the new stringer inner faces.
   - Move the four braces into the long-side plane (|y| about 2.25–2.75, under the stringer). Lengthen them to the
     sheet's 35–40°, reaching about 1.5–1.6 along the stringer underside from the leg face.
   - Re-run walk and seams. The end section changes but stays the same at both ends.

### Minors (recorded, not blocking)

- Brace angle and reach (45°, 1.13 against about 38°, 1.6), if not handled with the blocker.
- End blocks: the sheet draws them at deck level (top at the deck top, about 0.5 proud). Ours sit under the
  0.45 end-strip overhang, so the back-left one, prominent on the sheet, nearly vanishes in the f34.
- Rope turns read as flat stacked straps, wider off the post than the sheet's tight round coils. Rope also reads
  heavier and paler: yellow-pixel share about 1.7× the sheet's in the f34, median `#FFD05B` against `#FABE56`.
- Legs darkened 70 % toward wood_dark (`#903D12` against the sheet's `#A84C0F`): the sheet's legs are the post colour
  on the lit face.
- Side blocks slightly dark (`#AA4C16` against `#B9540A`).
- Spec and builder size 6.786 / pegs ±3.393 against the measured 6.780 / ±3.390. The hero note says "twisted rope
  turns", but the turns are `twist=False` with a groove strand.

## Main session after round 1 (2026-11-04)

Fix round, in this order:
1. **Blocker: the frame goes on the long sides.** Do the verifier's fix:
   - stringers on the post line, just inside the board ends;
   - posts split into a leg and an upper post seated on the stringer;
   - crossbeams widened to meet the stringers;
   - braces in the long-side plane at about 35–40°.
   Re-run walk and seams.
2. **End blocks:** at deck level and about 0.5 proud, so the back-left one reads in the f34.
3. **Rope:**
   - turns as tight round coils, like m048's corner-cut twisted turns, not flat straps;
   - rails and turns a little thinner;
   - colour toward `#FABE56`.
4. **Colour:**
   - legs the same colour as the posts;
   - side blocks toward `#B9540A`.
5. **Text:** correct the size, the rope-turn note and the Stringer part note.

Round 2 goes to a fresh verifier.

## Fixes after round 1

The main session's fix list, nothing else (2026-11-04, `m050.py` rebuilt in the light work file).

1. **Frame on the long sides (blocker).**
   - Stringers on the post lines: |y| 2.05–2.96 (outer face 0.04 inside the board ends at 3.00), z 1.42–2.07 (top
     sunk 0.01 into the boards), full length to ±7.998; still two (Stringer x2).
   - Posts split at the stringer: a leg (0 → 1.43, sunk 0.01 into the stringer underside, kind `leg`) and an upper post
     (2.06 → 4.90, sunk 0.01 into the stringer top). TimberBridgePost is the upper post with its turns, side block and
     end block; the legs are in the hero only. The side block (unchanged size and place) now bridges post and stringer.
   - Crossbeams widened to |y| 2.06 (0.01 into the stringers' inner faces): 4.12 long.
   - Braces in the long-side plane: |y| 2.25–2.75 (inside the leg and the stringer), 38° from horizontal, reaching
     1.55 along the stringer underside from the leg face; low cut on the leg's inner face at z 0.22–0.79.
   - Every full-width board now rests on both stringers; the post-row boards rest on the crossbeams.
2. **End blocks.** At deck level, z 2.06–2.60 (top at the deck top, sitting 0.01 into the stringer end), the post's
   width (|y| 2.004–2.996), from 0.01 inside the end post's end face to the seam (±7.998): 0.45 proud of the post, the
   most the 16-stud seam allows. Chamfered 0.04 like the boards. The end strip now runs between the two end blocks
   (|y| ≤ 2.014, sunk 0.01 into them), so the walk surface stays continuous across the join. The end-face peg is
   dropped (it would cross the seam); 8 pegs remain, on the side blocks.
3. **Rope.**
   - Turns: m048's corner-cut twisted turns (12 points, 5 sides, `twist=True`, corners cut 0.10 along each side),
     r 0.10 (was 0.11 straps), centres z 3.95 / 4.13 (touching), inner strands sunk 0.02 (0.017 measured into the
     posts); 120 tris each (was 144).
   - Rails r 0.10 (was 0.11), ends 0.65 off the post axis, seated about 0.03 into the turns (deepest rope in rope
     0.056, limit 0.08).
   - `m050_rope` `#E2AE55` → `#D4A04F`, `m050_rope_dark` `#C99441` → `#BC8A3B`.
4. **Colour.** Legs are `m050_wood_deep`, the post colour (no darkening toward wood_dark). Side and end blocks get
   their own key `m050_block` `#A4530B` (posts keep `m050_wood_deep`).
5. **Text.** Size 6.780 (pegs ±3.390) in the brief, the builder's docstring and `TARGET_SIZE`; the hero and Post notes
   describe the twisted turns that are now built; the Stringer note gives the new 0.91 × 0.65 section on the long side
   under the board ends and posts; the Brace note gives 38° in the long-side plane; the Rope Segment note no longer
   says twisted (the rails are smooth 6-sided tubes with a groove strand).

### Re-measured

kit_verify (`cls="structure"`, size, walk, seams): **problems []** (2.5 s).
- Tris: hero 4416 / 6000 (leg 8 × 28, post 8 × 44, rope_wrap 16 × 120, block 12, peg 8, plank 18, stringer 2,
  crossbeam 4, brace 4, rope_rail 6 × 152); parts Post 338, Plank 28, Stringer 28, Crossbeam 28, Brace 12, Rope 152.
- 86 closed shells; 0 non-manifold, bowtie, boundary, loose, zero-area, n-gon; 0 winding errors, self-hits,
  parity-inward or negative shells; min corner 12.9°. Floating 0, unchained 0, buried 0 (deepest rope_wrap / rope_rail
  0.056, limit 0.08; everything else ≤ 0.03). UV 1240 islands, 0 overlaps / flips, gap 0.016, border 0.008. Size
  15.996 × 6.780 × 4.90. Deck check: 54 samples, every board top 2.600.
- Walk: centre path clearance 0.63 (crossbeam below the feet), side paths ±0.6 clearance 0.254 to the turns, 0
  intersecting steps, no rises, nothing overhead; turns at (0, 0) and (-4.7, 0) clearance 1.149, 0 intersecting yaws.
- Seams at 16: 0 crossing pairs, gap 0.004, extent ±7.998, nothing past the seams, end sections identical (13 faces
  each end, z 1.42–2.60, mismatch 0.0).

Colour (hex medians, sheet f34 / ours at the same camera, `compare.py` at 640 px high):

| Region | Sheet | Ours |
| --- | --- | --- |
| Side block (front post 2) | `#B7510A` | `#B8530B` |
| Leg -Y face (front post 2) | `#A94D0F` | `#AE4D17` |
| Post -Y face (front post 2) | `#A64B0A` | `#AE4D17` |
| Rope, hue 36–55° pixels | `#F7C755` | `#FFC858` |
| Rope, RGB yellow mask | `#F8C059` | `#FBB44E` |

The two rope masks bracket the sheet (the lit strands clip red). Rope pixel share is now about 0.7–1.3× the sheet's
depending on the mask (was 1.7×).

Compare (`m050.compare()`, `<temp>/.../cmp/M050_compare.png`), W : H sheet / ours: f34 1.650 / 1.631, r34 1.633 /
1.637, side 3.149 / 3.268, front 1.444 / 1.361, rear 1.458 / 1.361, top 0.623 / 0.421.
- f34 / r34: each long side now shows the board-end face over the dark stringer face, the pegged block over the
  junction, and the knee brace under the stringer in the end bays (front-left and back-right in the f34); the
  back-left end block reads at deck level past its post.
- Side: post, stringer under the board row, block bridging both, braces from the leg to the stringer underside at the
  sheet's angle; the end blocks stand 0.45 past the end posts at deck level over the stringer ends.
- `joint_cu.png` / `under_cu.png`: the stringer runs under the board ends with the block over the junction and the
  brace dropping from the stringer underside, as the joint close-up.

Left as before (recorded misses): legs 0.4 shorter than the sheet's (deck 2.60 rule); the short-end cells' end swag
and end-plane braces; post -X faces lighter than the sheet (studio light); the sheet's end block is a little taller
(about 0.85) than ours (0.54, the board depth, because the stringer runs under it to the seam).

## Stage 7 verification (round 2)

**Result: PASS, 8/10.** Round 1's blocker is fixed: each long side now shows the board ends over a dark stringer
face, with the pegged block over the joint and the knee brace in the long-side plane. The other fix-list items are in,
and the fixes added no technical problem. The leftovers are cosmetic or already recorded.

### Technical (kit_verify, re-run on a copy of the work file, 2026-11-04)

`kit_verify.run` on the hero and all six parts, `cls="structure"`, size (15.996, 6.780, 4.90), the builder's `WALK`
paths and turns, `seams` pitch (16, 0, 0): **problems []** (2.3 s).
- Hero 4416 / 6000 tris, 86 shells (leg 8, post 8, rope_wrap 16 × 120, block 12, peg 8, plank 18, stringer 2,
  crossbeam 4, brace 4, rope_rail 6 × 152). 0 non-manifold, bowtie, boundary, wire, loose, zero-area, n-gon or
  duplicate. 0 winding errors, self-hits, parity-inward or negative shells. Min corner 12.9°.
- Contact: floating 0, unchained 0, 8 grounded (the legs).
- Burial: 0 buried. Deepest is rope_wrap / rope_rail at 0.056, under the 0.08 rope pair limit; peg / block 0.03;
  rope_wrap in post 0.017; everything else 0.01.
- UV: 1240 islands, 0 overlaps or flips, gap 0.016, border 0.008. Tint against normal worst 0.0. Transforms applied,
  origin bottom centre, no modifiers or custom normals, K.check clean, no sockets (none wanted).
- Parts: Post 338, Plank 28, Stringer 28 (15.996 × 0.91 × 0.65), Crossbeam 28 (0.6 × 4.12 × 0.65), Brace 12
  (1.55 × 0.5 × 1.211, 38°), Rope 152. Every part is clean.
- Walk: the centre path clears by 0.63 (crossbeam below the feet). Side paths at ±0.6 clear the turns by 0.254. 0
  intersecting steps, level 2.60 end to end, nothing overhead. Turns at (0, 0) and (-4.7, 0) clear by 1.149, 0
  intersecting yaws.
- Seams at 16: 0 crossing pairs, gap 0.004, extent ±7.998, nothing past the seams, end sections identical (13 faces
  each end, z 1.42–2.60, mismatch 0.0).

### Blocker check (round 1's blocker: frame on the long sides)

- **f34, column between front posts 2 and 3** (sheet crop scaled to the render, `compare.py` at 480 px high):
  - sheet: board end 15 px `#9A480E`, then stringer 23 px `#682D0A`–`#74350E`, then ground shadow;
  - ours: board end 22 px `#CD752C`, then stringer 20 px `#843510`, then background.
  The stringer face now shows directly under the board ends along both long sides in the f34 and r34. The pegged
  blocks bridge post and stringer. The knee braces show under the stringer in the end bays (front-left and
  back-right in the f34, the matching pair in the r34).
- **Joint close-up** (own renders at the end post and a middle post): the stringer runs under the board ends, the
  block sits over the post-stringer junction, and the brace drops from the stringer underside to the leg. The end
  block sits at deck level, 0.45 past the end post, over a stringer stub. This is the sheet close-up's layout.
- **Side:** post, stringer under the board row, block bridging both, end blocks at deck level past the end posts. The
  braces run from the leg's lower part to the stringer underside at the sheet's angle and reach. The low cut is at
  about 0.2–0.8 of the leg height; the sheet's is about 0.22–0.67.
- **Other fix-list items:**
  - End blocks: at deck level (z 2.06–2.60). The back-left one reads in the f34.
  - Rope: m048 corner-cut twisted turns at r 0.10, and thinner rails. Rope colour and pixel share now match the
    sheet: yellow mask median `#F8C65F` on the sheet against `#FFC156` ours, share 2.13 % against 2.07 %.
  - Colours: legs are the post colour, and side blocks are on target (table below).
  - Text: size, rope-turn and Stringer notes corrected.
- **New problems from the fixes:** none found. Board-row boards, crossbeams, legs and upper posts seat 0.01. The
  walk surface is continuous across the end strip and end blocks.
  - One tiny gap: the stringer (|y| 2.05–2.96) is 0.09 narrower than the post (2.0–3.0). This leaves a 0.04–0.05 slot
    between the leg top and the upper-post bottom at the post's inner and outer edges. It is hidden by the side block
    and the crossbeam from every normal view.

### Views against the sheet

`compare.py` with the builder's `COMPARE` boxes at 480 px high into `<temp>/.../v2/cmp/`, plus own close-ups. W : H,
sheet / ours:

| Cell | Sheet | Ours |
| --- | --- | --- |
| f34 | 1.652 | 1.634 |
| r34 | 1.633 | 1.642 |
| side | 3.142 | 3.250 |
| front | 1.442 | 1.363 |
| rear | 1.458 | 1.363 |
| top | 0.627 | 0.422 |

- **f34 (governs):** these match the sheet: layout, 4 + 4 posts, three bays, the boards across the width, the
  post-above-deck height, two turns under each cap, six sagging rails, the long-side board-end and stringer band,
  the pegged blocks, the end-bay knee braces, and the deck-level end blocks. Legs read shorter (deck 2.60 rule,
  recorded).
- **r34:** a redraw of the f34, with the same content. Matches.
- **Side:** matches on content and heights (see the blocker check). Rails sag to about 0.72 above the deck, as
  before.
- **Front / rear:** the sheet's end swag and end-plane braces are recorded misses (the hero and the notes say open
  ends). In these cells the turns show pointed lens-shaped ends past the post sides, where the sheet's coils are
  round (minor 1).
- **Top:** two-bay plan with edge strips (recorded). The content is right: posts, caps, boards across the width, and
  rails along the long sides. The studio throws rope shadows across the deck.
- **Exploded / scale:** six parts as the parts panel lists. The R6 marker stands about at post-top height, as on the
  sheet.
- **Colour** (hex medians, sheet f34 / ours at the same camera):

  | Region | Sheet | Ours | Note |
  | --- | --- | --- | --- |
  | Board tops | `#E68436` | `#DA8537` | |
  | Cap tops | `#FDA245` | `#FFA943` | |
  | Post -Y face | `#AC4C0A` | `#AE4D17` | |
  | Leg -Y face | `#A84C0E` | `#AE4D17` | |
  | Side block, lower part | `#A74905` | `#B8530B` | the fixer's upper patch, sheet `#B7510A` |
  | Brace | `#893D08` | `#893E1E` | |
  | Stringer face | `#682D0A`–`#74350E` | `#843510` | |
  | Rope | `#F8C65F` | `#FFC156` | |
  | Post -X face | `#763204` | `#A34816` | studio light, recorded |
  | Board end faces | `#9A480E` | `#CD752C` | studio light, recorded |

### Blockers

None.

### Minors (recorded, not blocking)

1. **Rope turns are faceted and pointed.** They are m048's corner-cut 5-sided twisted turns, as the fix list asked.
   In the f34 they read as twisted bands. Close up and in the front / rear cells, though, each turn is a flattish
   faceted strap whose corner segments end in lens-shaped points about 0.14 past the post faces. The sheet's coils are
   fat, round tubes with round ends.
   - **Fix, if wanted:** 6–8 sides on the turns. At 6 sides that is 16 × 144 = 2304 tris, hero about 4800.
   - Or round the corner arcs with two or three points per corner instead of one 45° cut.
2. **Stringer looks thin in the f34.** On the sheet's f34 the stringer face is about 1.5× the board-end face (23 : 15
   px); ours is about 0.9× (20 : 22). The side cell (14 : 12 px) agrees with ours, so this is a sheet inconsistency.
   Recorded only.
3. **Stringer slightly lighter than the sheet:** `#843510` against `#682D0A`–`#74350E`. Within the studio-light
   spread; no change needed.
4. **Stale brief and table text.** The Brief still gives hero 4696 / parts ≤ 400 / "12 pegged blocks". The parts table
   gives Post 400 and a "45° knee brace". The palette line says "legs 70 % toward it" and has no `m050_block` key.
   Built: hero 4416, Post 338, 8 pegs on 12 blocks, braces 38°, legs `m050_wood_deep`, blocks `m050_block`
   `#A4530B`. **Fix:** update the Brief bullets and table.
5. **Slots beside the stringer.** A 0.04–0.05 slot between leg top and upper-post bottom where the post is wider than
   the stringer (|y| 2.0–2.05 and 2.96–3.0). Not visible in any sheet view. If wanted, stringers at |y| 2.0–3.0 less
   0.04 on the outside, or the upper post on a 0.91-wide foot.
6. **Already recorded and unchanged:**
   - legs 0.4 shorter than the sheet's (deck 2.60 rule);
   - the short-end cells' swag and end-plane braces;
   - the top cell's two-bay plan;
   - post -X faces lighter than the sheet (studio light);
   - the end block at 0.54 tall against the sheet's about 0.85.
