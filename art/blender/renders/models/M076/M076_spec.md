# 076 Watchtower — spec

Reference: `art/blender/assets/references/076.png` ("WATCHTOWER / BUILDING MODEL STUDY", page 076, remade sheet).
Builder: `art/blender/kit/mcp/m076.py` → `build()`, on the shared library (`kit_parts` / `kit_build`). No earlier
builder or spec existed: this is a new build. Procedure: `art/blender/kit/mcp/STAGES.md`; standing answers:
`HOUSE_RULES.md`.

## Brief

- **Sheet:** 076 Watchtower (remake: yes, first build). Family: none.
- **Class and budget:** structure (open, climbable lookout), ceiling 6000, plan about 4500 (built 4378). Every part
  under 1000. Large-model verification (one model per verifier, up to two rounds).
- **Size:** the side cell's R6 figure is 89 px = 5 studs → 17.8 px / stud. Sheet in studs: total 14.4 (finial top),
  footings 1.5 tall, lower girt about 2.5–2.9, deck beam 7.4–8.3, deck about 8.3, rail top 9.5, post tops / eave
  10.6–11.2, roof apex about 13.0; post outer span 7.0 at z 1.9, 6.3 at the deck, 6.2 at the top (they lean in). Built:
  footings 1.40, posts' centres |x| = |y| 3.25 at the footing top to 2.75 at the post top (15.70), lean 2.0°; girt
  2.30–2.90; deck rim beams 7.40–8.38; **deck (plank top) 8.35**; rail top 11.30; canvas apex 17.90; finial top 19.12.
  Hero bbox **8.80 W × 10.53 D (with the ladder) × 19.12 H**.
- **Hero view:** f34 (front three-quarter, az −35, el 20). r34 from the rear-left (az −145, el 20). Front, side, rear:
  orthographic at az 0 / 90 / 180 (the side cell is seen from +X: front on the left, the ladder sloping out left).
  Top at el 89.9. Rear, r34 and top are redraws: judged on content.
- **Parts:**
  | Part | What | Tris |
  | --- | --- | --- |
  | TimberWatchtower (hero) | the whole tower | 4378 |
  | TimberWatchtowerPost | one leaning post: three segments, deck and rail block collars, six pegs | 364 |
  | TimberWatchtowerBrace | one lower-bay X brace (two boards, one over the other) and its peg | 56 |
  | TimberWatchtowerRailing | one side: bottom rail, top rail, three balusters | 92 |
  | TimberWatchtowerDeckFloor | four rim beams and six planks | 280 |
  | TimberWatchtowerCanvasRoof | the canvas pyramid and its four block corner caps | 656 |
  | TimberWatchtowerRoofFinial | octagonal base, neck, ball | 142 |
  | TimberWatchtowerBanner | rod with ball knobs, hem sleeve, point-tipped cloth, cream double diamond | 244 |
  | TimberWatchtowerLadder | two rails, eight rungs | 280 |
  | TimberWatchtowerFooting | tapered stone block | 44 |
- **Palette** (sheet medians of the rendered cells; swatches in brackets): timber rendered #C86A22 [#B66024] →
  `#B96825`; cut ends / pegs `#D08A3E`; dark infill rendered #7C4521 / #552C13 → `#523018`; deck planks rendered
  #B7652D → `#A65A26`; canvas rendered #F7D7AA–#FDEBBC [#FDDCA9] → `#DEB890` by hand (lit, it read #FFFFCC yellow at
  `#E8D2AE`); canvas deep `#BE9A74`; stone rendered #ABAAA9–#BBB5AF [#C4C2C0] → `#A9A9AC`; banner rendered #E22212
  [#E1241B] → `#F0281C`; banner deep `#8A1410`; cream emblem `#F2E8D6`. All matte (roughness 0.8–0.95). The optional
  green accent: none (no cell shows it).
- **Lights / VFX:** none (sheet note: no baked lighting or effects; no lantern).
- **Collision:** hero precise (players climb and walk on it); Post, Brace, Railing, CanvasRoof hull; DeckFloor,
  Footing box; Ladder precise; Finial, Banner none.
- **Checks switched on in kit_verify:** `cls="structure"`; `walk` = the climb (below); stored `m076_deck`,
  `m076_ladder_foot`. The builder's `tower_check`: deck top by rays, headroom over the deck inside the railing, clear
  width, ladder numbers.
- **Departures from HOUSE_RULES and from the sheet (ruled here):**
  - **Upper storey heightened for headroom.** The sheet's figure gives a deck at 8.3 with the rail top only 1.2 and
    the eave only 2.3 above it; a 5-stud player could not stand under that roof. The lower storey keeps the sheet's
    heights (deck 8.35); the rail top is 2.95 over the deck and the canvas underside is at least 6.9 over it inside the
    railing (measured 7.07), so the posts run to 15.70 and the hero is 19.1 tall against the sheet's 14.4 (front W : H
    0.47 against 0.88). This is the main visible difference from the sheet.
  - **Width:** posts set a little wider than the sheet (post outer span 7.6 at the footings, 7.05 at the deck, against
    7.0 / 6.3) so the deck has 5.57 clear between the railings and room for the ladder gap.
  - **One ladder, at the front centre**, leaning 75° against the front rim beam from a foot 2.2 in front of the deck
    edge (the side cell draws it sloping out front; the top and deck-plan cells show it at the front centre). The
    sloping ladders on the left and right in the f34 / r34 cells are not built: no ortho, top or plan cell shows them,
    and they read as redraws of the front ladder.
  - **The deck plan's "ladder opening"** is built as the 3.1 gap in the front railing between two newel posts, with the
    ladder's rails rising 2.40 over the deck through it as hand holds. A hatch inside the deck would put the ladder
    behind the banner and inside the infilled front wall. The sheet's ladder stops at the lower girt; ours reaches the
    deck edge (the brief's climb).
  - **Banner behind the ladder:** the banner hangs under the front rim beam in front of the infill and the ladder
    stands in front of it (0.3–1.4 clear), so its rungs cross the cloth in the front view. The sheet draws the ladder
    below the banner.
  - **Grey blocks on the deck edges** (top and deck-plan cells): not built. No front, side or rear cell shows anything
    grey at the deck edge.
  - **Ladder rules** (none in HOUSE_RULES): rung tops every 0.931 (the deck edge is the ninth step), 2.40 clear
    between the rails for a 2-stud character, 75° lean.
  - **Walk proxy:** the default spec box with its lowest 1.0 slimmed to 0.40 half depth (feet/shins), so the ride
    proxy's footprint (samples at ±0.45) meets a step before the box does.
- **Questions for the main session:** none.

## Stage 1 — Modelling

Build frame: front −Y (banner, ladder), +X right, ground z 0, centred on x 0 / y 0. A post's centre is
`c(z) = 3.25 − 0.035 (z − 1.40)` in both |x| and |y|; face pieces are built in a sheared face frame (u along the face, z
up, w outward from the leaning post plane), so infill, braces, girts and rails follow the lean. Every piece is its own
closed shell (no booleans), seated 0.002–0.05 into what holds it.
- **Footings:** tapered chamfered stone blocks (2.30 base, 2.04 at 1.02, 1.70 top, 1.40 tall), the lower band a shade
  deeper.
- **Posts:** 1.0 square (chamfer 0.06), each three segments (`P.leg`, horizontal end caps) joined by the **deck collar**
  (7.25–8.50, 1.30 square) and the **rail collar** (10.80–11.40, 1.20 square), bevelled tops (block joinery); round
  six-sided pegs on each collar's two outer faces and on the post's outer faces at the girt (24 pegs).
- **Lower storey:** girt 0.60 × 0.80 on every face; five dark vertical infill planks per face (trapezoids, 0.025 V gaps,
  the outer two stepped in under the deck collars); X braces on the right, left and rear faces (back board on the
  infill, front board over it, ends cut level into girt and rim beam and stopped at the collars, a peg at the
  crossing); a centre leg under the side and rear girts (the side and rear cells).
- **Deck:** four rim beams 7.40–8.38 between the deck collars (outer face 0.1 inside the collar's), six planks
  0.35 thick along X between them, top 8.35.
- **Railing:** bottom rail 8.70–9.05, top rail 10.90–11.30 between the rail collars, three balusters per side; the
  front rails stop at two newel posts (|x| 1.55–1.91, to 11.45) either side of the ladder gap.
- **Roof:** one closed canvas slab (0.12) over a mirrored grid (0, 0.5, 1.1, 1.7, 2.25, 3.75), each cell split toward
  the centre so the hips run on grid edges: a flat apex (|r| ≤ 0.5) at 17.90, concave faces (exponent 1.2) down to flat
  corners at 15.80 (r ≥ 2.25, resting 0.02 into the post tops), an eave band beyond 2.25 dropping 0.25 / stud, each
  face dipping toward its middle line (0.12, plus 0.10 toward the eave) so the eave droops between the corners; the
  band a shade deeper, the rim deeper. Block corner caps 1.70 square × 0.70 on the flat corners (centred 0.35 outside
  the post axis, as the top cell). Finial: octagonal base (0.84 across, bevelled), neck r 0.16, faceted ball r 0.38.
- **Banner:** rod r 0.12 (|x| ≤ 1.72) at z 7.24 under the front rim beam, ball knobs r 0.17 seated 0.01 into the
  beam, dark hem sleeve, cloth 2.80 wide from 7.07 to sides 4.70 and a point at 3.50, at y −3.40 (clear of the
  infill, which leans out going down); cream double diamond on the front.
- **Ladder:** rails 0.28 × 0.32, level-cut feet on the ground (back face y −5.80) and level-cut tops at 10.75; the
  back face crosses the front rim beam's top front edge (seated 0.02); eight square rungs 0.24, tops 0.931 … 7.449.

## Stage 2 — Optimisation and cleanup

kit_verify clean (problems list empty) on the hero and all nine parts:
- Tris: hero 4378 / 6000 (140 shells); parts 364, 56, 92, 280, 656, 142, 244, 280, 44 (all < 1000).
- 0 non-manifold edges, bowties, boundary / wire / loose, zero-area faces, n-gons, duplicate verts; 0 winding errors,
  0 inward faces, 0 self-intersections; 0 floating / unchained shells; 0 buried (collars over the infill corners and
  the brace tops fixed during the build); no pierced thin sheets; transforms applied, no modifiers or custom normals;
  origins at the bottom centre (hero offset y −0.865: the ladder's reach).

## Stage 3 — UV

`kit_build.cleanup` (angle-based unwrap, margin 0.008): kit_verify's UV check clean on every object.

## Stage 4 — Materials and colour

Sheet medians from the rendered cells (`M.sample`) and swatches (`M.raw_sample`); colours by role and position:
timber, paler cut-end pegs, cap tops and bevels; infill planks alternate a step toward timber; deck planks alternate a
step toward dark; collar and newel bevel bands toward the cut end; footings' lower band deeper; canvas eave band and
rim deeper. Broad Tint mottling on planks, infill, footings, canvas and cloth; per-piece Tint ±0.05. Canvas, banner,
stone and infill set by hand against the compare renders (medians, sheet → ours, f34 / front): timber #C26117 →
#CF6B20 / #D26D1D → #D36C20; infill #562A0D → #5B3014 / #522C13 → #552D10; stone #B8B4B1 → #B5B0AC; banner #E22212 →
#D22415; canvas #FDE3B4 → peach cream after the last change (the lit faces were #FFF2B8 one step earlier).

## Stage 5 — Lighting

Nothing: the sheet shows no light, glow or lantern ("no baked lighting, effects"). No Studio-side setup.

## Stage 6 — VFX

Nothing: the sheet shows no effect. No sockets.

## Checks

- **Climb** (kit_verify `walk`, ride on, max rise 1.0, lift 0.12, ladder skipped in the clearance): x 0 from y −9 up
  the ladder, through the railing gap, then round the deck ((0, 1.2) → (−1.5, 1.2) → (−1.5, −1.0) → (1.5, −1.0) →
  (1.5, 1.2)). The proxy rides rung to rung (rises 0.91–0.95) and onto the deck at 8.35; min clearance 0.12 (the
  lift, over the planks), 0 intersecting steps, headroom 6.72 at the deck's front edge (0, −3.7) under the eave band.
  Turning room at (0, 0.2) and (0, −1.2) on the deck: clearance 0.12, 0 intersecting yaws.
- **tower_check:** deck top 8.350 at all 16 samples; **headroom over the deck inside the railing ≥ 7.07** (rays up on
  a 9 × 9 grid, the post corners left out; HOUSE_RULES 6.9); clear between the railings 5.57; railing gap 3.10;
  canvas underside lowest 15.09 (eave edge, outside the railing); finial top 19.12.
- **Requires Manual Validation (Studio):** climb the ladder with a default character. The precise-collision rungs
  should trigger Humanoid climbing at 75° and a 0.93 pitch. If they don't, add an invisible, non-rendering TrussPart
  (2 wide) along the ladder's back face.

## Renders and compare

`M076_views.png` (f34, r34, front, side, rear, top, exploded, scale) and `m076.compare()` (written to
`<temp>/RBLX-Flintborn/compare/M076/` by default). Content W : H, sheet / ours: f34 0.76 / about 0.55, front 0.88 /
0.47, rear 0.68 / about 0.45, top 0.97 / 0.92. Ours is narrower for its height because of the taller upper storey
(departure above).

Known minors: the tall open upper storey (about 4 studs between rail top and eave, sheet about 1); the banner is seen
through the ladder's rungs in the front view; the roof's corner caps read larger than the sheet's against the
narrower canvas; the sheet's canvas faces show soft centre creases, while ours shows a single dip line per face; no
sloping side ladders and no grey deck-edge blocks (ruled out); the rear cell's low sill under the girt is a single
centre leg.

## Rulings (main session, 2026-11-04)

- **Taller upper storey for headroom:** accepted in principle. Gameplay headroom (6.9 on the deck) governs over the
  sheet's eave height, as for 070's canvas low point. The verifier judges whether the tower still reads as the
  sheet's; if it doesn't, the fix must bring the proportions closer (shorter open storey, taller railing or half
  wall, a lower deck) without dropping deck headroom under 6.9.
- **Accepted as recorded:** one ladder at the front centre (the side ladders in the 3/4 views are not built), the
  ladder opening as a railing gap with handhold rails, banner behind the ladder, no grey deck-edge blocks, the
  ladder rules and walk proxy. Studio check: climbing the ladder (add an invisible TrussPart if the rungs don't
  trigger climbing).

## Stage 7 — verification (R1)

**Result: FAIL, 6.5 / 10.** Fresh verifier, read-only, in a background session on `wip/M076v.blend` (nothing rebuilt
or saved). Renders, compare pairs, sheet crops and close-ups (`cu_*`) are in `renders/models/M076/verify/`.

### Technical (all clean)

- **kit_verify** (the builder's `VERIFY`, hero budget 6000, parts 1000): **0 problems** in 5.8 s. Hero **4378 / 6000**,
  140 shells, 8.80 × 10.53 × 19.12; parts Post 364, Brace 56, Railing 92, DeckFloor 280, CanvasRoof 656, RoofFinial
  142, Banner 244, Ladder 280, Footing 44. Floating 0, unchained 0, buried 0 (deepest 0.05), min corner 0.315°; no
  topology, winding, parity, UV, pierce or colour-by-normal problems. Names and collision as the brief.
- **Climb (walk):** rides rung to rung (rises 0.91–0.95), onto the deck at 8.35, 0 intersecting steps, min clearance
  0.12; turning room at both deck points, 0 intersecting yaws; headroom on the path 6.72 at (0, −3.7) (the ladder exit
  under the eave band, outside the railing line).
- **tower_check:** deck top 8.350 at every sample; headroom inside the railing **7.07**; clear between railings 5.57;
  newel gap 3.10; rail top 11.30. Ladder 75°, rung pitch 0.931, 2.40 between the rails.
- **Colour** (medians over hue masks, sheet → ours, f34 / front): timber #CD6718 → #D06B20 / #D66F1D → #D36C20;
  infill #53280D → #5A3014 / #512A12 → #552C0F; banner #E91D13 → #EF2315 / #E61E15 → #EA2214; stone #ABA8A7 →
  #B3ADAA / #ADABAA → #B3AEAB; canvas #FDE2B3 → #FFE2A8 / #FDEABA → #FFE7AA (cream, not salmon). Side and rear read
  darker (studio light, recorded only). Top-cell cap tops #E0731A → #FF9637 (too pale).

### Measured proportions (sheet front cell without its ground shadow)

compare.py's content W : H counts the sheet's soft ground shadow (front 0.877, side 0.693): the sheet front's own
bounding box is 142 × 252 px = **8.0 × 14.2 studs, W : H 0.56** (ours 8.8 × 19.12, **0.46**). Sheet heights at
17.8 px / stud: deck beam 7.5–8.3, rail top 9.3, eave / cap bottom 10.3, cap top 11.5, apex 14.0, finial 14.2. Shares
of the height, sheet → ours: lower storey (to the deck) 58 % → 44 %, open upper storey 14 % → 38 %, roof with finial
27 % → 18 %; roof rise over its width 0.47 → 0.28.

### Blockers

1. **The tower reads as a stilted lookout, not the sheet's squat tower** (all four elevation cells and f34 / r34). The
   headroom ruling explains a taller upper storey, but here it combines with a narrow footprint and a small roof, so
   the open storey (rail top 11.30 → eave 15.1–15.8, about 4 studs) dominates and the front W : H is 0.46 against
   0.56.
2. **The roof reads as a flared pagoda hat under four slabs, not the sheet's canvas pyramid** (`cu_roof`, `cu_cap`,
   side and front pairs). The sheet's canvas is a tall, straight-sided hip pyramid (rise about 0.47 of its width) whose
   eave runs level from corner cap to corner cap. Ours is concave (PEXP 1.2), only 2.10 high from the corners, has flat
   corner wings and a drooping eave band, and sits inside the posts in the elevations. The 1.70 × 0.70 corner caps read
   as flat plates floating above it; the sheet's caps are compact cubes with a small top block at the eave corners.

**Fix (one change for both, measured):** keep headroom over the deck at 7.0 (≥ 6.9) and rebalance round it.
- **Lower the deck:** `DECK` 8.35 → **7.40**. Rim beams 6.45–7.43; collars move with the deck; girt stays 2.30–2.90,
  so the braced bay is 2.90–6.45 (3.55 tall). Ladder: 7 rungs at 0.929 pitch (`RIM_TOP / 8`), top `DECK + 2.40`.
- **Widen:** `CB` 3.25 → **3.75**, `CT` 2.75 → **3.25** (lean stays 0.5, 2.3°). Footing outer span 9.80; clear between
  the railings 6.56.
- **Raise the railing:** top rail `DECK + 2.90 … 3.30` (rail top 10.70; was 2.55 … 2.95 over the deck).
- **Straight roof:** one hip pyramid, no flat-corner cells or separate eave band: `PEXP` 1.0, `S_FACE` ≤ 0.04,
  `S_EAVE` 0, canvas half size `HC` = `CT + 0.5 + 0.30` = **4.05**, eave top **13.62** (level all round), rise **3.65**
  to the flat apex (`RF` 0.5) at **17.27**; canvas underside at the railing's inner line (|r| 3.18) = DECK + 7.00. Post
  top `E` = **13.83** (seated 0.02 into the canvas underside over the post's outer edge). Finial top about **18.49**.
- **Caps:** compact cubes on the post axes, about **1.30 square × 1.00 tall** with a small top block (0.70 square ×
  0.20), sunk 0.02 into the canvas's low side; top key `mix(TIMBER, TIMBER_END, 0.3)`.
- **Result:** hero about **9.8 × 18.5** (front W : H **0.53** against the sheet's 0.56); lower storey 40 %, open storey
  34 % (rail top → eave 2.92, was about 4.1), roof with finial 26 % (sheet 27 %); roof rise / width 0.45. tower_check
  must still report headroom ≥ 6.9 inside the railing and the deck at `DECK` everywhere; rerun the climb.

### Minors

1. The climb's headroom at the deck's front edge (0, −3.7), where the ladder comes through the railing gap, is 6.72
   now and will be about 6.4 under the straight eave. It is outside the railing line and above a 5.5 player: record.
2. Cap tops are too pale from above (top cell #FF9637 against #E0731A): the 0.6 `TIMBER_END` mix on `top_key`; 0.3
   is enough (one line, also in the fix).
3. The sheet's front, side and rear cells show a centre upright in the upper storey (rail to eave, a peg at the rail)
   and, on the front, two short hanger brackets either side of the banner. Neither is built.
4. Exploded render: posts stand behind the deck and roof and overlap them; the sheet's panel lays the parts out apart.
5. Footings: the exploded cell shows a square socket in each footing's top; ours is flat (hidden by the post).
6. Departures already ruled stand: one front ladder at 75° (the sheet's reaches the girt at about 55°), the railing
   gap, the banner behind the ladder (rungs cross the cloth in the front view), no grey deck-edge blocks.
7. Suite note: compare.py's content W : H includes the sheet's soft ground shadow (front 0.877 against a bounding box
   of 0.56), which overstates the gap; measure proportions from the object's box, or mask out low-saturation shadow.

## Fix after R1

Both blockers taken as one change, on the verifier's measured prescription (departures below). Rebuilt in
`wip/M076.blend` (saved); `M076_views.png` re-rendered; `m076.compare()` re-run.

**What changed**
- **Lower, wider tower:** `DECK` 8.35 → 7.40 (rim beams 6.45–7.43, deck collars 6.30–7.55, the braced bay 2.90–6.45);
  `CB` / `CT` 3.25 / 2.75 → 3.75 / 3.25 (lean 2.4°, footing outer span 9.80, clear between the railings 6.54).
- **Taller railing:** top rail `DECK + 2.90 … 3.30` (top 10.70), rail collars 10.20–10.80, newel tops 10.85.
- **Straight roof:** one hip pyramid, `S_FACE` 0.04 (zero on the hips, at the apex and along the eave), no concave
  exponent, flat-corner cells or eave band: `HC` 4.05, level eave top 13.62 (underside 13.50), rise 3.65 to the flat
  apex (`RF` 0.5) at 17.27; finial top 18.49. The rim is one shade deeper (0.45 toward `CANVAS_DEEP`).
- **Caps:** compact blocks 1.30 square × 1.10 with a 0.70 × 0.20 top block, `top_key` mix 0.6 → 0.3, standing at
  the canvas corners (below).
- **Ladder:** 7 rungs, pitch 0.929 (`RIM_TOP / 8`), top `DECK + 2.40` = 9.80, foot at y −6.04, 75°.
- **Banner:** follows the lower deck and the wider infill: y −3.89 (0.08 clear of the infill at the tip), cloth from
  6.14 to sides 4.30 and a point at 3.30 (kept above the girt), emblem at 5.00.
- `tower_check` casts its deck rays down the planks' middles (a plank seam fell on the old sample line).

**Measured**
- kit_verify (`VERIFY`): **0 problems**. Hero **4590 / 6000** (147 shells), 9.80 × 11.27 × 18.49; parts Post 384,
  Brace 56, Railing 92, DeckFloor 280, CanvasRoof 816, RoofFinial 142, Banner 244, Ladder 252, Footing 44. Floating 0,
  unchained 0, buried 0 (deepest 0.05), no thin-sheet pierces, min corner 0.617°.
- Climb: rung to rung (rises 0.90–0.95) onto the deck at 7.40, 0 intersecting steps, min clearance 0.105; turning room
  at both deck points (0.12, 0 intersecting yaws); headroom on the path 6.12 at (0, −4.0), the ladder exit under the
  eave edge, outside the railing line (verifier's minor 1, recorded).
- tower_check: deck top 7.400 at all 16 samples; **headroom inside the railing 7.00** (≥ 6.9); clear between the
  railings 6.54; newel gap 3.10; rail top 10.70.
- Heights: footing 1.40, girt 2.30–2.90, deck 7.40, rail top 10.70, cap bottom 13.45, post top 13.47, eave 13.62, cap
  top 14.55 (block 14.73), apex 17.27, finial 18.49. Rail top → eave **2.92** (was about 4.1).
- Proportions: front bounding box W : H **0.53** (9.80 / 18.49; sheet 0.56; R1 0.46). Shares of the height: to the
  deck 40 %, deck → eave 34 %, roof with finial **26 %** (sheet 27 %). Roof rise / canvas width 0.45. compare.py content
  W : H (sheet with its shadow / ours): f34 0.76 / 0.64, r34 0.81 / 0.64, front 0.88 / 0.54, side 0.69 / 0.61, rear
  0.68 / 0.55, top 0.97 / 0.95.

**Departures from the prescription**
- **Caps at the canvas corners, not centred on the post axes and sunk into the canvas.** The canvas climbs 1.03 per
  stud there, so a cap on the post axis (spanning |r| 2.6–3.9) either crosses the thin canvas (kit_verify's pierce
  check) or, with the canvas corner cut out for it, leaves the hip open above a 1.0-tall cap (the first try showed that
  hole in f34). The sheet's front cell puts the cap's inner face over the post axis with most of the cap outside the
  canvas corner, so the canvas corners are cut out 0.75 in from the eave and the caps stand there: centre 3.95, inner
  face 3.30 (post axis 3.25), 0.55 beyond the canvas edge. The body is 1.10 tall (not 1.00) so it hides the cut-out
  corner (canvas 14.40 at it, cap top 14.55). The canvas stops 0.01 short of the caps (contact): seated, the caps'
  vertical edges would cross it.
- **Post top 13.47, not 13.83:** the posts seat 0.02 into the caps' undersides. Over each post's inner half, which
  runs on under the canvas, a sloped **post head** (an L-shaped block on the post top, its top 0.02 into the canvas
  underside on both sides of the hip, part of `TimberWatchtowerPost`) carries the canvas, so from the deck the posts
  meet the roof.

**Left as minors:** the sheet's scalloped eave valance (ours a plain 0.12 rim); the centre upright in the upper
storey and the banner hanger brackets; the exploded layout; the footings' socket; the ruled departures (one front
ladder, railing gap, banner behind the ladder, no grey deck-edge blocks).

## Stage 7 — verification (R2)

**Result: PASS, 8 / 10.** Fresh verifier, read-only, in a background session on `wip/M076v.blend` (nothing rebuilt or
saved). Compare pairs, renders and close-ups (`cu_*`) are in `renders/models/M076/verify/r2/`.

### Technical (all clean)

- **kit_verify** (the builder's `VERIFY`, hero 6000, parts 1000): **0 problems** in 5.6 s. Hero **4590 / 6000**, 147
  shells, 9.80 × 11.27 × 18.49; parts Post 384, Brace 56, Railing 92, DeckFloor 280, CanvasRoof 816, RoofFinial 142,
  Banner 244, Ladder 252, Footing 44 (all < 1000). Floating 0, unchained 0, buried 0 (deepest 0.05), no thin-sheet
  pierces, min corner 0.617°.
- **Climb (walk):** rung to rung (rises 0.90–0.95) onto the deck at 7.40, 0 intersecting steps, min clearance 0.105
  (plank2); turning room at both deck points 0.12, 0 intersecting yaws; path headroom 6.12 at (0, −4.0), the ladder
  exit under the eave edge, outside the railing line (above a 5.5 player; recorded).
- **tower_check:** deck top 7.400 at all 16 plank-middle samples; **headroom inside the railing 7.002** (≥ 6.9); clear
  between the railings 6.54; newel gap 3.10; rail top 10.70. Sampling the planks' middles is a fair fix (it measures
  the walk surface, not a seam).
- **Colour** (medians over hue masks, sheet → ours): timber f34 #D36919 → #D06B20, front #D76F1E → #D46C20; canvas
  f34 #FCDFB1 → #FFE5A9, front #FDE8B7 → #FFE8AB, top #F8DAAC → #F3D3A4; top-cell orange (cap tops, ladder) #E3761B →
  #F5862D (R1 #FF9637: better, still a step pale). Side and rear canvas read tan (studio light, recorded).

### Proportions (measured)

Sheet front cell's own bounding box (saturated or dark pixels, the pale ground shadow masked out): 149 × 255 px, W : H
**0.58** (R1's box 0.56); ours 9.80 / 18.49 = **0.53** (R1 0.46). Shares of the height, sheet → ours: to the deck 58 % →
40 %, deck → eave 14 % → 34 %, roof with finial 27 % → 26 %. compare.py content W : H (sheet with its shadow / ours):
f34 0.76 / 0.64, r34 0.81 / 0.64, front 0.88 / 0.54, side 0.69 / 0.61, rear 0.68 / 0.55, top 0.97 / 0.95.

### R1 blockers

1. **Proportions: resolved within the headroom ruling.** The lower, wider tower (deck 7.40, posts 3.75 → 3.25, footing
   span 9.80) with the taller railing (top 10.70) and the eave at 13.62 now reads as the sheet's squat four-post tower in
   every elevation and in f34 / r34: the braced lower storey and the roof carry the silhouette, and the open band
   between rail top and eave is 2.92 (R1 about 4.1). It is still taller than the sheet's (about 1 stud), which the 6.9
   headroom ruling requires; recorded, not a blocker.
2. **Roof: resolved.** A straight hip pyramid with a level eave, rise / width 0.45 (sheet 0.47), a flat apex and the
   turned finial (octagonal base, neck, ball: matches the joint-detail cell). The caps are compact cubes (1.30 × 1.10)
   with a small top block at the eave corners, as the sheet's; front and f34 roof outlines match the sheet's within a
   few pixels at cell scale.

### Fixer's departures (judged)

- **Caps at the canvas corners** (centre 3.95, inner face 3.30 over the post axis, canvas cut out 0.75 and stopping
  0.01 short): accepted. It is how the sheet's front and top cells place them, the joins read closed in f34, front and
  `cu_cap`, and from above (`cu_cap_top`) the cap covers the cut-out; only the cap's own shadow shows beside it.
- **Post tops 13.47 seated into the caps, with a sloped post head under the canvas:** accepted. From the deck
  (`cu_deck_eye`, `cu_deck_up`) the posts meet the canvas underside; the heads read as pointed post tops, which is
  odd only from inside and invisible from outside.
- **tower_check sampling the plank middles:** accepted (see above).

Nothing the fix touched broke: the climb, headroom 7.00, the banner (0.08 clear of the infill at its tip, 0.12 at its
sides, 0.2 at the top; no pierce or bury), the ladder top through the railing gap (`cu_ladder_top`), and the budgets.

### Minors (none blocking)

1. Upper storey still about 2.9 studs open between rail top and eave against the sheet's 1 (headroom ruling).
2. The sheet's roof is slightly bell-shaped with a scalloped eave valance; ours is a straight pyramid with a plain
   0.12 rim.
3. Cap tops a step paler than the sheet's from above (#F5862D against #E3761B): `top_key` mix 0.3 → 0.15 would close
   it (one line, ship-time optional).
4. The banner is smaller in the hero than the sheet's (2.8 × 3.1 against about 3.4 × 5) and mostly behind the ladder
   (the ladder-in-front departure is ruled).
5. Still not built (recorded in R1): the centre upright in the upper storey, the banner hanger brackets, the footings'
   socket; the exploded render overlaps the posts with the deck and roof.
6. The climb's headroom at the ladder exit (0, −4.0) is 6.12, outside the railing line.
7. Ruled departures stand: one front ladder at 75°, the railing gap, banner behind the ladder, no grey deck-edge
   blocks. Studio check: the ladder's rungs trigger climbing (TrussPart fallback).
