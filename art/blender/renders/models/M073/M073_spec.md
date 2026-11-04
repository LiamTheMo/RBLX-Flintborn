# 073 Barricade — spec

Reference: `art/blender/assets/references/073.png` (remade sheet, "BARRICADE / BUILDING MODEL STUDY", page 073).
Builder: `art/blender/kit/mcp/m073.py` → `build()`, on the shared library (`kit_parts` / `kit_build`). No earlier
builder or spec existed: this is a new build. Procedure: `art/blender/kit/mcp/STAGES.md`; standing answers:
`HOUSE_RULES.md`.

## Brief

- **Sheet:** 073 Barricade (remake: yes, but no earlier model). Family: none.
- **Class and budget:** structure (a wall module, nothing to walk into or under), ceiling 6000, plan 3600 (built
  3502). Every part under 1000.
- **Size:** the side cell's R6 block figure is 105 px tall = 5 studs → 0.0476 stud/px; the front cell is at the same
  scale (post 121 px from ground to cap, both cells). From that: post top 5.75 (cap shoulder 5.33), post 1.16 square
  (24–25 px), footing stones 0.95 tall and about 1.55 × 1.7, top rail 3.48–4.52, bottom rail 0.90–1.90 (built
  1.00–2.00 so it clears the stones), rails 0.80 deep (top cell), rope band 3.52–4.48, brace foot about 2.4–3.0
  behind the post axis (side cell), brace about 0.55–0.7 thick. The sheet's module is 225–235 px = 10.7–11.2 studs
  long (post spacing 3.18). Hero bbox 10.66 W × 4.17 D × 5.75 H.
- **Tile pitch:** 32/3 = 10.667 studs along X (three modules fill two 16-stud tiles). Seams at x ±5.333; only the
  bottom-rail stubs reach them (end faces 0.002 inside, same section at both ends); stored points `attach_w` /
  `attach_e` (seam centres on the ground, facing ∓X) and `m073_pitch`, `m073_seams` on the hero.
- **Hero view:** f34 (front three-quarter, camera front-left) at az −30, el 14. Front, side, rear: orthographic. r34
  (camera rear, +X side) at az 150: a redraw, content only. Top cell: content only. Tiling cell: compared with the
  hero and a copy at +pitch.
- **Parts:**
  | Part | What | Tris |
  | --- | --- | --- |
  | LashedBarricade (hero) | the module | 3502 |
  | LashedBarricadePost | 1.16 chamfered grooved post, chamfered pyramid cap, 4.83 tall | 116 |
  | LashedBarricadeRail | one module-length rail 10.66 × 0.80 × 1.04, grooved | 52 |
  | LashedBarricadeBrace | rear brace 0.54 × 0.72, top cut for a post's rear face, level foot | 54 |
  | LashedBarricadeLashing | three touching round rope turns sized for the post | 288 |
  | LashedBarricadeStone | faceted footing stone with a flat top | 40 |
- **Palette** (swatch medians; rendered medians as calibration targets): wood base swatch #9A5823, rendered lit
  front #C06D25 → `m073_wood`; wood highlight swatch #D98636, cap tops render #FDAE5A → `m073_wood_hi` (used half
  way, for the caps only); rope swatch #EEB766, rendered #FCD787 → `m073_rope` (+ `m073_rope_deep` strand); stone
  swatch #90909D, rendered #989499 → `m073_stone`. All matte. Foliage swatch is "reserved": not used.
- **Lights / VFX:** none (the sheet shows no glow, light or effect).
- **Collision:** hero `box` (tiling module); Post, Rail, Brace `box`; Lashing `none` (dressing); Stone `hull`.
- **Checks switched on in kit_verify:** `cls="structure"`, `seams={"pitch": (32/3, 0, 0)}`, `stored` attach points
  and pitch.
- **Departures from HOUSE_RULES:**
  - Tile pitch 32/3, not 16: at the sheet's character scale the module is about 10.7 long; a 16 pitch would mean
    5-stud bays (openings 2.3:1, unlike the sheet) or a module scaled to 8.6 tall against a 5-stud figure. 32/3 keeps
    the sheet's proportions and still composes with the 16-stud grid (3 modules = 2 tiles).
  - The module is 5 % shorter than the sheet's at figure scale (post spacing 2.97 against 3.18): the end posts' turns
    must stop inside the seam.
  - Bottom rail 1.00–2.00 instead of the measured 0.90–1.90, to clear the footing stones' tops (0.88–0.96).
- **Rulings against the sheet's cells (hero governs):**
  - No lower band lashings in the hero: none of the assembled cells (f34, r34, front, rear, side) show any; only the
    exploded view's loose posts carry them. The Lashing part is the exploded view's three-turn ring.
  - Braces: the side and top cells draw a rear prop to the ground, the front and f34 cells a diagonal between the posts.
    Built as one shape that does both: from the rear face of posts 2 and 3 out toward the end posts and back to the
    ground (about 42° from horizontal), so the front view shows a diagonal between the rails and its foot below the
    bottom rail, and the top view shows angled stubs where the sheet draws straight ones.
  - The top rail stops in the end posts (the f34, front and side cells show turns all round the end posts); the r34
    cell's top-rail stub is not built. The bottom rail's stubs run to the seams so tiled modules have a continuous
    bottom rail (the tiling cell).
- **Questions for the main session:** none.

## Stage 1 — Modelling

Build frame: front −Y, +X right, ground z 0, centred on x 0, post axes on y 0. Every piece is its own closed shell (no
booleans); 44 shells in the hero.
- **Posts** (`post`): `loft` of an 8-sided chamfered section (half 0.58, chamfer 0.12) with a V-groove (0.07 wide,
  0.03 deep) down each broad face, three rings: foot (stone top − 0.03), cap shoulder 5.33, flat cap top 5.75 at
  0.56 of the section. Caps are a chamfered pyramid with a flat top. x = ±4.448, ±1.483.
- **Stones** (`stone`): convex hull of a chamfered base ring on z 0 (half 0.78 × 0.86 at the end posts, 0.72 × 0.82
  inside), a low waist (0.18–0.24 H) and a flat top ring 1.12 × the post section; seeded inward-only jitter, heights
  0.95 / 0.88 / 0.90 / 0.96; broad Tint mottling.
- **Rails** (`rails`): 0.80 × 1.04 (top) / 1.00 (bottom), chamfer 0.06, grooved front and back; one span per bay
  seated 0.03 into the post side faces; bottom-rail stubs from the end posts to x ±5.3313.
- **Lashings** (`lashing`): round 6-sided rope (twist off, one strand in `rope_deep`). Turns r 0.16, centreline 0.14
  off the faces (inner strand 0.02 in): end posts at 3.68 / 4.00 / 4.32, inner posts 3.66 / 4.34. Each turn is the
  mitred offset octagon cut on every side face a top-rail span enters: the run follows that side face to the rail's
  front or rear face and ends 0.04 into it (so turns wrap the joint without passing through the rail). Diagonals
  r 0.13 lie over the turns at 0.35 off the faces (0.06 into the turns); their ends wrap the post corner into the
  rail face beside the post, or on an end post's outer side go over the turn and tuck 0.03 into the post face. Inner
  posts: an X on the front and on the rear (the first diagonal dives round the turns to 0.20 off the face at the
  crossing, the second stays over); end posts: one diagonal over the three turns on each face (front lower-left to
  upper-right, as the front cell's post 1).
- **Braces** (`brace`): 0.54 (horizontal) × 0.72 section, grooved; corner lines from an aim point inside the post
  toward a foot at (post x ∓ 2.25, y 2.55); the top ring where each line leaves the post's rear face 0.012 inside
  it, the aim point solved so the top end's highest point is 3.40 (under the lowest turn, 3.50) and its footprint
  is centred on the rear face (±0.408 of the ±0.448 flat: a planar end); foot cut level on z 0. Measured: top end
  z 1.98–3.40, foot x −4.28…−3.18, y 2.03–3.07, 41.9° from horizontal.
- Parts are built by the same functions; the Lashing part's turns step 0.30 (touching) so it chains to the ground.

Checks: shell placement read back from `P.GEO` (rail spans, brace footprint `on_rear_face: true`,
`all_lines_hit_post: true`).

## Stage 2 — Optimisation and cleanup

`kit_verify.run` (via `build()`): **0 problems**. Hero 3502 / 6000 tris (rope 2344, wood and caps 988, stone 170);
parts 116 / 52 / 54 / 288 / 40. 0 non-manifold edges and verts, boundary, wire, loose, zero-area, n-gons, duplicate
verts; 0 winding errors and inward faces; no self-intersections; floating 0, unchained 0, buried 0 (deepest 0.08,
the diagonals in the turns under the rope-in-rope 0.08 rule); min face corner 1.7° (floor 0.3°). Origin at the
bounding-box bottom centre (hero offset y 0.987: the braces make the box deeper behind), transforms applied.
Seams: 0 crossing triangle pairs at the 32/3 pitch, gap 0.004, end sections identical (12 / 12 faces, mismatch 0.0),
nothing past ±5.333.

Fixes on the way: the first turn runs ran along the side face inside the post (buried 0.12) — replaced by the
explicit side-face cut; diagonals that started inside their turns (buried 0.12) — replaced by arcs over the turns;
a brace end that spanned the rear face and chamfer (the post's corner 0.06–0.12 inside the brace) — the footprint is
now centred on the rear face alone. The Post part sets `kit_shading_ok` (its lighter cap is the only up-facing area,
so the colour/normal correlation reads it as painted light; the cap is cut end grain).

## Stage 3 — UV

`kit_build` cleanup: Smart UV (angle 45, margin 0.008) per object; kit_verify reports no UV overlaps, flips, gap or
border problems on any object.

## Stage 4 — Materials and colour

Swatches sampled from the palette cell (medians): wood base #9A5823, wood highlight #D98636, rope #EEB766, stone
#90909D. Rendered medians on the sheet: post lit front #C46F26 (f34) / #B86822–#BD6A23 (front), rail front #C26E26,
rail top #FBA14E, cap tops #FDAE5A, front-cell cap facet #FCAD4F, rope #FCD787 (f34) / #FBDD8F (front), stone
#8E888C (f34) / #A29EA7 (front). `MODEL.calibrate` toward wood #C06D25 (brown), wood_hi #F5A048 (brown), rope
#FCD787 (all), rope_deep #E0B060 (all), stone #98949A (stone) gave the PALETTE hexes: wood #995F25 (renders
190,109,37), wood_hi #C68744 (250,160,71), rope #E5B079 (255,215,136), rope_deep #B0925A (221,175,97), stone #7B7D87
(149,147,153). Caps use `m073_wood_x_hi_50` (role: cut end grain; the f34 cap faces are a little lighter than the post
faces under the same light). Colour by role only; Tint mottling on the stones (0.05) and ±0.05 per piece. Roughness
0.8–0.95, no metal.

## Stage 5 — Lighting

Nothing: the sheet shows no emissive part or light. No Studio-side settings.

## Stage 6 — VFX

Nothing: the sheet shows no glow, dust, smoke or other effect. Export STATS: 0 sockets, 0 glow keys on every object.

## Renders and compare

`M073_views.png`: f34, r34, front, side, rear, top (sheet views), exploded, scale (5.5-stud character beside it).
Close-ups `lash_cu`, `end_cu`, `brace_cu` (`build(close=True)`). `m073.compare()` writes the six-cell compare sheet;
`m073.tile_compare()` the hero and a copy at +pitch against the tiling cell (both to the temp folder).

Compare notes (content W : H sheet / ours): f34 1.70 / 1.39, r34 1.67 / 1.34, front 2.15 / 1.85, rear 2.05 / 1.79,
top 2.25 / 2.71, tile 3.08 / 3.71. The sheet crops include the soft ground shadow, which widens them; the remaining
gap is the 5 % shorter module (departure above). Known minors:
- the front cell shows the braces only between the rails; ours also shows their feet below the bottom rail, and the
  top view's brace stubs are angled (ruling above);
- the bottom-rail stubs stand 0.30 past the end posts (the front cell draws the rails flush; they make the tiled
  bottom rail continuous);
- the X lashings read a little thinner and flatter than the sheet's chunky bands in the small front cell;
- the stones are a little boxier than the sheet's flared trapezoids.

## Rulings (main session, 2026-11-04)

- **No lower band lashings on the hero:** confirmed. The assembled cells govern; the exploded view's lower bands
  belong to the loose posts only.
- **Accepted as recorded in the brief:** hero name LashedBarricade (W12 owns Barricade*), tile pitch 32/3 (three
  modules per two 16-stud tiles), bottom rail at 1.00–2.00 to clear the stones, braces from the rear faces of posts
  2 and 3, top rail stopping in the end posts, box collision.
- **Suite note for the next shared-library batch:** kit_verify's seams section compare reports a false mismatch when
  a module's seam end is two separate faces.

## Stage 7 — verification (R1)

**Result: FAIL, 6.5 / 10.** Fresh verifier, read-only, in a background session on the work-file copy
`wip/M073v.blend` (nothing rebuilt or saved). Technically clean, and the tiling is right. Two visual blockers, both in
the hero cell: the rope lashings and the footing stones. The model has the sheet's content: four capped posts on
stones, two rails, lashings at the top rail, two rear braces, and a module that tiles. Verifier renders and compare
sheets are in `renders/models/M073/verify/` (gitignored).

### Technical

- **kit_verify** (the builder's `VERIFY`: `cls="structure"`, seams at pitch 32/3, stored attach points; hero and all
  five parts, hero budget 6000, `TARGET_SIZE`): **0 problems**, 1.8 s.
  - Hero LashedBarricade **3502 / 6000** tris, 44 shells, 10.663 × 4.169 × 5.75, origin bottom centre (offset y
    0.987). Parts: Post 116, Rail 52, Brace 54, Lashing 288, Stone 40 (all < 1000).
  - 0 non-manifold, bowties, boundary / wire / loose, zero-area faces, n-gons, duplicate verts; 0 winding, parity
    and self-intersection problems; floating 0, unchained 0, buried 0 (deepest 0.08: diagonals in turns, the
    rope-in-rope rule); min corner 1.705°. UVs clean on every object.
  - **Seams:** 0 crossing triangle pairs with a copy at +10.667, gap 0.004, end sections 12 / 12 faces over z
    1.00–2.00, mismatch 0.0 (the known false mismatch didn't fire), extent ±5.3313, nothing past the seams. Seam
    close-ups (`seam_f34_cu`, `seam_r34_cu`): the end posts stand 0.61 apart, the bottom rail runs on unbroken, the
    two end lashings almost touch. Clean, and close to the sheet's tiling cell.
- **Names, collision, materials:** hero and parts `LashedBarricade<Part>`; no other model or export uses the name.
  Collision: hero, Post, Rail and Brace `box`, Lashing `none`, Stone `hull`. Materials `m073_wood`,
  `m073_wood_x_hi_50` (caps), `m073_rope`, `m073_rope_deep`, `m073_stone`. Stored `attach_w` / `attach_e`,
  `m073_pitch`, `m073_seams`. No sockets (none on the sheet).
- **Scale:** side cell, figure 105 px = 5 studs, post 121 px = 5.76 against ours 5.75. Front cell, at 21.2 px per stud
  (posts 122 px = 5.75): post spacing 3.16 against ours 2.97 (6 % short, the recorded departure), post 1.12 against
  1.16, top rail 3.34–4.54 against 3.48–4.52, bottom rail 0.87–1.85 against 1.00–2.00 (ruled). Brace top about 3.1
  against 3.40 (side cell); brace foot about 3.05 behind the post axis against 3.1.

### Views against the sheet (compare.py, content W : H sheet / ours)

- **f34 (1.695 / 1.387).** Same layout. Three visible differences:
  - the lashings (B1);
  - the stones (B2);
  - the braces: the sheet shows a bold diagonal in bays 1 and 3; ours shows a small wedge in bay 1 and nothing in
    bay 3 (ruled shape, minor 1).

  The W : H gap is mostly the sheet's ground shadow plus the 6 % short bay.
- **Front (2.146 / 1.846).** Without the shadow the sheet's module is about 1.94 : 1, so the real gap is about 5 %.
  That reads as slightly tall, not wrong (minor 2). The inner posts' X reads as a flat "Z" of sticks spreading onto
  the rails (B1). The stones read as straight-sided plinths (B2). The braces show only below the bottom rail (ruled).
- **Side (0.825 / 0.692).** The brace angle and foot match. The lashing stands out much further: its depth is 2.1
  (turns 1.76, diagonals 2.16), against about 1.55 on the sheet (B1, minor 3).
- **Rear (2.048 / 1.791) and r34 (1.67 / 1.336).** Redraws, judged on content. Braces, X lashings, the turns on the
  end posts and the stones are all present. Our braces cross the bottom rail to the ground (ruled).
- **Top (2.254 / 2.708).** Octagonal caps, the rail and two rear stubs are present. The stubs are angled (ruled). The
  lashing rings show wider than the caps (minor 3).
- **Tiling (3.081 / 3.705).** Content matches: paired end posts, continuous bottom rail, both lashings. The W : H gap is
  two short modules plus the shadow.
- **Exploded and reusable parts.** Post, Rail, Brace, Lashing (three-turn ring) and Stone are all there. The sheet's
  notched posts and brace tenon are not modelled (minor 4).
- **Colour** (medians over material masks, f34 / front, sheet → ours):

  | Material | Median | Lit 30 % |
  | --- | --- | --- |
  | Wood | #B96925 → #A9601F; #B96923 → #A96020 | #D68538 → #C47430 |
  | Rope | #FCCE77 → #FFD989; #FBD480 → #FFD989 | |
  | Stone | #83818C → #8E8C92; #9D99A2 → #8F8D92 | |

  Lit wood renders about 8–9 % dark (minor 5). Rope and stone are on target.

### Blockers

- **B1. The rope lashings don't read as the sheet's neat lashings.** On the sheet each post has compact round turns
  that hug it, and the inner posts carry a bold X on the face: about 1.43 wide outside, about 37° (centrelines 1.17
  wide × 0.87 high). On ours:
  - the diagonals' ends wrap the post corner and run along the side faces onto the rails, so the arms reach ±1.08
    from the post axis;
  - the slope is about 20° (centrelines ±0.95, rising 0.68);
  - the diving stroke crosses only 0.20 off the face, inside the turns' depth.

  At sheet scale this reads as a flat "Z" of sticks splaying over the rail. The 6-sided turns read as stacked flat
  slats. Fix, in `m073.py`:
  1. In `arm_end`, on rail sides: drop the run along the side face to the rail. End each arm at the post's front or
     rear corner, x ±0.60 from the post axis (outer width about 1.46), dipping 0.03–0.06 into the turn it ends on.
  2. Set `TURNS["mid"]` to (3.60, 4.40), so the X rises 0.80 over about 1.2 (about 34°). The lowest turn's underside,
     3.44, still clears the brace top at 3.40.
  3. Set `X_MID` to (0.30, O2), so both strokes of the X read.
  4. Set `RT_SIDES` from 6 to 8 for rounder rope: rope about 2344 → 3125 tris, hero about 4300 / 6000, Lashing part
     384.
  5. Re-run kit_verify (bury pairs: rope in rope ≤ 0.08) and compare the front and f34 cells.
- **B2. The footing stones read as cut plinths, not the sheet's flared footing rocks.**

  | Cell | Sheet base | Sheet top | Top : base | Ours |
  | --- | --- | --- | --- | --- |
  | Front | 1.95 | 1.37 | 0.70 | base 1.48–1.56 (after jitter), top 1.30, 0.83 |
  | Side | 1.85 | | | |

  Our waist at 0.18–0.24 H keeps the lower quarter near-vertical, so every cell shows straight-sided blocks. Fix:
  1. `STONES` base halves (0.87, 0.95) for all four. 0.87 is the most the end stones take inside the seam:
     4.448 + 0.87 = 5.318 < 5.323, which the existing assert enforces.
  2. Keep `STONE_TOP_K` 1.12, so the top is 1.30 and top : base about 0.75.
  3. Move the waist to 0.32–0.42 H at 0.88–0.94 of the base, so the sides slope in facets like the sheet's rocks.
  4. Check that the brace feet (x −4.28…−3.18, y 2.03–3.07) stay clear (the stones reach y ±0.95) and that the D
     target (4.1 ± 0.3) holds.

### Minors

1. The braces barely show in the f34 and front cells. The sheet draws bold diagonals between the rails. Their shape is
   ruled, so this is recorded only.
2. The module is 6 % short at figure scale (post spacing 2.97 against 3.16), a recorded departure. The front reads
   slightly tall, not wrong.
3. The lashings stand further off the posts than on the sheet: half-depth 0.88 (turns) and 1.08 (diagonals) against
   about 0.78. B1's arm change brings the diagonals in. Bringing `TURN_OFF` toward 0.10 would close the rest.
4. The exploded view's notched posts and brace tenon are not modelled. They are hidden in the assembly.
5. The lit wood is 8–9 % darker than the sheet in the f34 and front cells. One-constant fix: `m073_wood` #995F25 →
   about #A56828 (linear × 1.2), or re-run `MODEL.calibrate` for WOOD.
6. The bottom-rail stubs stand 0.30 past the end posts, and the r34 top-rail stub is not built (both ruled), recorded
   only.

## Fix after R1

Fix modeller, on the work file `wip/M073.blend` (rebuilt from `m073.py`, saved). Both blockers and minor 5 addressed;
minor 3 (lashing depth) closed with B1.

### B1 lashings

- **Rope section:** 8 sides (was 6), flattened against the post as the joint detail's bands. A local `band()` (P.rope
  with separate half sizes along and across the up axis): turns 0.16 half height × 0.12 radial half (inner flat sunk
  0.02, `TURN_OFF` 0.091), diagonals 0.15 half width on the face × 0.10 half thickness. Diagonals sit 0.05 into the
  turns they cross (`ARC_R` 0.153 across, `ARC_V` 0.215 over the top / bottom).
- **Inner posts:** `TURNS["mid"]` = (3.60, 4.40); lowest turn underside 3.452, above the brace top 3.40. `arm_end` on
  rail sides: each arm stops at the post's front / rear corner (centreline x ±0.561 over the turn) with one 0.12 step
  round the chamfer that dips 0.01 further into the turn, so the cut end turns away; no run onto the rail. Both strokes
  of the X stay over the turns and one passes 0.12 under the other at the crossing (`X_MID` = (O2 − 0.12, O2),
  `X_DIVE` off).
- **Measured (post 1 front X):** outer 1.418 wide (x −0.709…0.709 from the post axis; sheet about 1.43), 3.459–4.541
  tall, centrelines rise 0.80 over 1.12 = 35.5° (sheet about 37°). Lashing half-depth: turns 0.782 (sheet about 0.78;
  was 0.88), X 0.936 (was 1.08). Whole inner lashing 1.56 wide (turns).
- The front and rear cells now read as an X on each inner post (compare `front`, `rear`); the f34 cell shows rounded
  bands with the X over them.

### B2 footing stones

- `STONES` base halves (0.87, 0.95) for all four, base jitter 0.96–1.0 (was 0.92–1.0), `STONE_TOP_K` 1.12 kept.
- Measured: base 1.711–1.735 wide × 1.87–1.89 deep, top 1.299, top : base 0.75; heights 0.88–0.96. End stones reach
  x ±5.315 (< 5.323 inside the seam). Brace feet (y 2.03–3.07) are clear of the stones (y ±0.95). Hero D 4.02 (target
  4.1 ± 0.3).
- Stone part 58 tris (was 40).

### Wood colour (minor 5)

`m073_wood` #995F25 → #A56828. Wood medians over a brown mask, sheet → ours: f34 #B16423 → #B86A22 (lit 30 % #C57128
→ #CD7E32), front #B66723 → #B76A22 (lit 30 % #C26F27 → #BF7427). On target within about 4 %.

### Departures from the verifier's prescription

- **Stone waist:** two rings, not one: 0.28–0.34 H at 0.94–0.97 of the base and 0.56–0.64 H at 0.85–0.89. A single
  waist at 0.32–0.42 H gives a straight frustum. The front cell's rock, measured at 10×, is a convex bell: about 1.27
  wide near the top, 1.65 at 40 % down and 1.95 at the base. Two rings give that convex profile with the top kept at
  1.30.
- **Arm end x:** the corner sits at x ±0.561 (not 0.60) because the diagonals now lie closer to the face (O2 0.244,
  was 0.37). The step round the chamfer brings the outer width to 1.42, the sheet's figure.
- **Under-stroke:** the −45° dive round the turns is dropped (`X_DIVE` off). With it, the under-stroke ran deeper and
  in shadow along its whole length, and the small front cell read a "Z" plus a stub. Both strokes now lie over the
  turns and only cross 0.12 apart.
- **End posts kept at x ±4.448** (`END_X` keeps the R1 layout, so the stones still fit the seam). With the thinner
  turns, the end lashings stop at x ±5.23. Neighbouring modules' end lashings are now 0.21 apart at the seam (they
  were 0.006). The sheet's tiling cell shows a small gap there too.

### Numbers

`kit_verify`: **0 problems**. Hero **3934 / 6000** (rope about 2710, wood and caps 988, stones about 236), 44 shells,
10.663 × 4.02 × 5.75. Parts: Post 116, Rail 52, Brace 54, Lashing 384 (three flattened 8-sided turns, 1.56 × 1.56 ×
0.85), Stone 58. Floating 0, buried 0 (deepest 0.076: diagonals in turns, within the rope-in-rope 0.08 rule), min
corner 1.07°. Seams: 0 crossing pairs at 32/3, gap 0.004, end sections 12 / 12 faces, mismatch 0.0, extent ±5.3313,
nothing past the seams. compare.py (W : H sheet / ours): f34 1.695 / 1.362, r34 1.67 / 1.327, front 2.146 / 1.84,
side 0.825 / 0.676, rear 2.048 / 1.797, top 2.254 / 2.778, tile 3.081 / 3.705 (written to the temp folder).
`M073_views.png` and the close-ups were re-rendered.

## Stage 7 — verification (R2)

**Result: PASS, 8.0 / 10.** Fresh verifier, read-only, in a background session on the refreshed work-file copy
`wip/M073v.blend` (nothing rebuilt or saved). Both R1 blockers are resolved, and the fix broke nothing technical.
Verifier renders, compare pairs and close-ups (`cu_*`) are in `renders/models/M073/verify/r2/` (gitignored).

### Technical

- **kit_verify** (the builder's `VERIFY`, hero budget 6000, `TARGET_SIZE`, hero and all five parts): **0 problems**.
  - Hero **3934 / 6000** tris, 44 shells (rope turns 14 / 1672, diagonals 12 / 1040, rails 416, posts 464, stones
    234, braces 108), 10.663 × 4.02 × 5.75, origin bottom centre. Parts: Post 116, Rail 52, Brace 54, Lashing 384,
    Stone 58 (all < 1000).
  - 0 non-manifold, boundary, bowties, n-gons, zero-area faces, duplicate verts; 0 winding, parity, negative-volume
    and self-hit problems; min corner 1.07°. Floating 0, unchained 0, buried 0: deepest 0.076 (diagonal in turn,
    rope-in-rope ≤ 0.08), turn into rail 0.04, everything else ≤ 0.03. UVs: 0 overlaps or flips, min gap 0.016.
  - **Seams** at 32/3: 0 crossing pairs, gap 0.004, end sections 12 / 12 faces over z 1.00–2.00, mismatch 0.0,
    extent ±5.3313, nothing past the seams.
- **Shell read-back:** brace tops 3.40, lowest inner turn underside 3.452 (0.052 clear); end lashings stop at
  x ±5.23 (0.206 between neighbours at the seam); end stones reach x ±5.315 (inside 5.333); stone tops 0.88–0.96
  under the bottom rail 1.00; brace feet y +0.57…+3.07 from the post axis, clear of the stones (±0.95).

### Views against the sheet (compare.py, content W : H sheet / ours)

f34 1.695 / 1.362, r34 1.67 / 1.327, front 2.146 / 1.84, side 0.825 / 0.676, rear 2.048 / 1.797, top 2.254 / 2.778,
tile 3.081 / 3.705; the gaps are the sheet's ground shadow plus the recorded short module, as in R1.

- **B1 lashings: resolved.** Front and rear cells now read as one bold X on each inner post, inside the turns (outer
  1.42 wide against the sheet's 1.43, centrelines about 35°), no longer a "Z" spreading onto the rails. In the f34
  cell the inner posts show the X over rounded bands; the end posts' three flattened turns read like the joint
  detail's chunky bands (`cu_end_f34`). Lashing half-depth 0.78 (turns) / 0.94 (X) against about 0.78.
- **B2 stones: resolved.** Front and side cells read as flared trapezoid footings (top 1.30, base 1.71–1.74, top :
  base 0.75; sheet 0.70), no longer straight plinths. In f34 they read as flared footing stones under each post.
- **Departures judged:** all four accepted.
  - The two-ring stone waist gives the convex flare the front cell shows; a single waist would be a plain frustum.
  - Arm ends at ±0.561 with the chamfer step give the sheet's outer width.
  - Dropping the under-stroke dive is what makes the X read in the front and rear cells; the 0.12 step still shows
    the crossing order up close.
  - The 0.21 gap between neighbouring end lashings reads like the tiling cell's small gap; the tiled bottom rail
    stays continuous.
- **Colour** (medians over masks, sheet → ours): wood f34 #AE6323 → #B86A22, front #B46622 → #B76A22 (minor 5 of
  R1 closed); stone f34 #8E8B93 → #908E93, front #9E9AA2 → #928F95; rope f34 #FCCD75 → #FFCB81, front #FBD27F →
  #FFC179.

### Blockers

None.

### Minors

1. The stones are smooth, symmetric bells. The sheet's are chunkier, angular rocks with a distinct sloped facet band
   round the flat top; up close in f34 ours read a little like pedestals (`cu_stone_f34`).
2. The X arms read as rigid dowels: their blunt octagonal cut ends stand proud at the post corners
   (`cu_inner_f34`), where the sheet's rope wraps round the corner out of sight. They are fine at sheet scale.
3. The end posts carry one diagonal per face, which reads as a single slash. The sheet's front cell suggests a small
   crossing there too. Recorded only.
4. The rope reads slightly more orange than the sheet in the front cell (median #FFC179 against #FBD27F; lit 30 % on
   target). This is the `rope_deep` strand share. Optional: nudge `m073_rope_deep` toward `m073_rope`.
5. From the top, the stones' back corners peek past the lashing rings (top cell content only).
6. R1 minors 1, 2, 4 and 6 stand: the brace shape, short module, notches and tenon, rail stubs and r34 stub are all
   ruled or recorded.
