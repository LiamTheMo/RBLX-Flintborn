# 070 Ruined Lean-To — spec

Reference: `art/blender/assets/references/070.png` (remade 2026-11-04; "RUINED LEAN-TO / BUILDING MODEL STUDY", page 070).
Builder: `art/blender/kit/mcp/m070.py` → `build()`, on the shared library (`kit_parts` / `kit_build`). Procedure:
`art/blender/kit/mcp/STAGES.md`; standing answers: `HOUSE_RULES.md`. The old builder and spec (built 2026-11-03
against the previous sheet, never verified) are in git history; this rebuild keeps their names and the stone, ivy
and lashing recipes, and re-measures everything on the new sheet.

## Brief

- **Sheet:** 070 Ruined Lean-To (remake: yes). Family: none.
- **Class and budget:** structure, ceiling 6000, plan 5850 (built 5828). The 10 % margin went to the ivy, which the
  remade sheet draws much denser than the old one; every part is under 1000.
- **Size:** FR post top 12.0 (house rule) = 144.5 px in the front cell → 0.083 stud/px, the same scale in the side and
  rear cells (FR post 142.5 px). From that: FL post 9.4, back post 11.3, wall courses 1.95 (22.5 px), peak 7 courses
  13.65 (166.5 px → 13.8), side wall 4 courses 7.8 (95 px → 7.9), banner 2.0 wide, top 9.3, tips 3.1. Hero bbox
  19.53 W × 17.35 D × 14.04 H (with ivy, moss, rubble and the banner knob).
- **Hero view:** f34 (front three-quarter), near-frontal and drawn in strong perspective (the back post's px/stud is
  0.75 of the front posts'): compared at az 0, el 24, lens 1.5. Front, side, rear: orthographic, scale as above. r34:
  a mirrored redraw of the front (content only; compared mirrored at az 145). Top cell and floor plan: content only —
  they draw the long side wall on the right but the banner still front-right, and a square canvas tied at four corners;
  the hero governs (side wall at −X, canvas tied at three posts with its front pulled down).
- **Parts:**
  | Part | What | Tris |
  | --- | --- | --- |
  | RuinedLeanToWallBlock | one chamfered block 2.5 × 2.3 × 1.95, chipped corner | 36 |
  | RuinedLeanToWallSection | the exploded view's ruin chunk with an opening, ivy run, moss | 538 |
  | RuinedLeanToRubble | three loose chipped blocks | 108 |
  | RuinedLeanToCanopy | canvas with pulled-down front, rope tail and toggle | 304 |
  | RuinedLeanToPost | 12.0 post (no footing), X-lashing, two collar bands | 324 |
  | RuinedLeanToBanner | crossarm + knob, dark pole, hem sleeve, three-point cloth, white diamond | 316 |
  | RuinedLeanToBedroll | leather roll, gold caps, two straps | 180 |
  | RuinedLeanToTable | the exploded "Table / Bench": three-plank bench, seat 1.50 | 244 |
  | RuinedLeanToCrate | closed X-braced crate 2.30 | 220 |
  | RuinedLeanToBarrel | lidded hooped barrel 2.72 | 204 |
- **Palette** (sheet medians, then `MODEL.calibrate` and a class check on the renders; hexes in `PALETTE`): stone
  #CFAEA5 lit faces / swatch #CDB2AA, matte; timber #9B4C15 (lit #D17C30); canvas #FEEDC3 (swatch #FADEB4); ivy
  #6E8F01 median, lit lime #BDCF04; banner #CB2222; rope #E59F3D; crate wood #975211 / panels #773D20; leather
  #914C21; mat gold #C8913E with teal-blue stripes. All matte (roughness 0.8–0.95), iron hoops 0.45 metal.
- **Lights / VFX:** none. The assembled views show no light or effect; the exploded view's lantern on a bracket post
  is not in any assembled view and is left out (no `heat_glow`).
- **Collision:** hero precise; WallBlock, Table, Crate box; WallSection, Rubble, Post, Bedroll, Barrel hull;
  Canopy, Banner none.
- **Checks switched on in kit_verify:** `cls="structure"`; `foliage={"keys": ("leaf",)}` (5° sweep on the ivy);
  `walk` along x −1.55 from y −12 into the lean-to (ride, `skip=("mat",)`, turn at (−1.55, −0.4) on the mat). The
  builder's `lean_check`: canvas underside ≥ 6.9 over the walk lane (path ±1.0), crate tops 2.30.
- **Departures from HOUSE_RULES:** none against the rules themselves. Against the sheet: the canvas' low point is
  6.55 (underside 6.45) over the right crate, not the sheet's 5.2, so the underside stays ≥ 6.9 over the walk lane
  (measured 6.95); crates 2.30 and barrel 2.72 (the sheet draws them about 3.1); the sheet's character is 6.7 studs
  at the post scale (R6 is 5); ground ferns and grass tufts left out (no ground scatter).
- **Questions for the main session:** none.

## Stage 1 — Modelling

Build frame: front −Y (open), +X right (open, banner), side wall at −X, back wall at +Y, ground z 0, x 0 midway
between the front posts.
- **Masonry** (`walls`): `P.block` (36 tris, chamfer 0.16, creased long faces) split into planar triangles where
  warped (`flatten`, from m068) — 48 blocks, depth 2.3, courses 1.95, joints 0.05, seats 0.015, running bond from the
  old builder's `_layout` (target 2.9 long: the front cell's blocks are about 37 px). Back wall y 4.0–6.3, x −9.3…6.6:
  courses 0–3 full, course 4 to x 5.4, course 5 x −7.0…2.4, course 6 (the peak, 13.65) x −5.0…1.5 — the front cell's
  skyline. Side wall x −9.3…−7.0, courses 0–3 from y −6.3 (7.8 at the front end), course 4 from y −1.4 (9.75); the
  corner pier alternates between the walls. Nine chipped top corners (stone_light facets). Five rubble blocks in front;
  stone footings under the posts (FL 1.5 × 0.5, back 1.25 × 1.3 dark, FR 2.0 × 1.0).
- **Posts and rope:** 1.04-square chamfered posts (front cell 12.5 px) at FL (−5.88, −6.0) top 9.4, back
  (−0.99, 3.2) top 11.3, FR (5.88, −6.0) top 12.0, bevelled tops with pale end grain. `P.rope_turn` turns (40 tris)
  and `x_lashing`-style diagonals on the chosen faces: FL turns 7.45 / 8.75 with X on the front and outer faces; back
  post turns 9.85 / 10.85 (no X: its back face is 0.28 off the wall); FR turns 8.85 / 10.55 with X on the front face;
  gold collars of two turns (FL 0.75, FR 1.30 and 4.70). A 0.56 × 0.6 crossbeam rests on the side wall's front-end top
  (sunk 0.02) against the FL post's back face, between its turns.
- **Canvas** (`canvas_top` + `canvas_sheet`, the m066 slab with its rims split into triangles): tied at the FL inner
  corner 8.25, the FR inner corner 9.30 and gathered across the back post's flat front face at 10.35 (0.82 wide, 0.03
  off the face); edge and centre sag, X creases; the front edge pulled by a straight tent (in u) to the low point
  (1.35, −2.6, 6.55) over the right crate, fading to the back as (1 − v)^1.3 — the sheet's V front edge and the crease
  up from the low point. 9 × 5 grid, 0.10 thick. A rope tail (0.95) and toggle hang under the low point.
- **Banner:** round crossarm (r 0.20) from the FR post's +X face at 9.62 to x 9.25 with a knob; a red hem sleeve round
  it; the three-point cloth x 7.0–8.95 (top 9.33, tips 3.10, notches 3.95) with the white diamond, inner diamond and
  side points on both faces; a dark pole (r 0.20) behind it from the ground to 10.05.
- **Props:** two closed X-braced crates (m066 recipe, braces 0.10 proud) at (−3.95, −4.25) and under the low point;
  lidded barrel (4.0, −3.9) beside the FR post; a small lidded box (1.2) behind the FR post (hero view); bedroll along
  the back wall x −5.25…−2.05 on its 6-sided gold straps; the gold mat with two teal stripes on the floor.
- **Dressing:** four `P.moss` patches on exposed tops; ivy (`P.ivy`, tent leaves) — R1 the peak's inner face (main +
  two branches, down to 6.6 below the canvas line), R2 the peak's outer face, R3 the outer face's +X end, R4 the side
  wall's front end, R5 the side wall's outer face; 64 leaves placed, 62 kept.
- **Fixes over the library and the old build:**
  - `lower_pads`: `P.ivy` seats each lip stem 0.06 into its pad and the stem's slope to the edge sinks it 0.07–0.08 (the
    old build's suite failure). The pads' tops are lowered to 0.035 over the stone, so a stem rests 0.01 over its pad
    and dips 0.03 at most. Worth moving into `kit_parts.ivy` (pad top at stem bottom − 0.01).
  - `prune_leaves`: `P.ivy` does not keep leaves off neighbouring leaves or branch stems; on dense curtains two or three
    sink 0.05–0.075. The later leaf of each such pair is dropped with its register entries (this build: 2). Worth a
    leaf-leaf check inside `kit_parts.ivy`.
  - `flatten` (m068) on every block; the canvas slab with split rims (m066).

## Stage 2 — Optimisation and cleanup

kit_verify (`cls="structure"`), 0 problems: hero **5828 / 6000**, 208 closed shells, 0 non-manifold, bowtie, boundary,
wire, loose, zero-area, n-gon or duplicate; normals outward, 0 winding or parity errors; floating 0 / unchained 0;
buried 0 (deepest 0.044: rope turns in post faces and pads under stems); no pierced thin sheets; min corner 0.37°
(canvas back-edge strip, floor 0.3°). Origin at the bbox bottom centre (`m070_offset` [−0.291, −1.761, −0.005]: the
strap flats sit 0.005 into the ground), transforms applied, no modifiers. Hero tris by kind: blocks 1728, leaves
~990, rope turns 480, stems ~300, canvas 304, crate braces 288, crates 228+, rubble 180, barrel 204, bedroll 180,
emblem 136, posts 132, moss 104, footings 108, rest under 100 each.
Parts: WallBlock 36, WallSection 538, Rubble 108, Canopy 304, Post 324, Banner 316, Bedroll 180, Table 244, Crate 220,
Barrel 204; all 0 problems.
Walk: lane x −1.55, y −12 → 0.6: min clearance 0.205 (left crate's brace), 0 intersecting steps, rise 0.14 onto the
mat, headroom over the path 6.94; turning at (−1.55, −0.4, 0.14) 0.925 clear at every yaw. `lean_check`: canvas
underside over the lane (±1.0) ≥ 6.952 (at (−0.55, −3.25)); crate tops 2.30; barrel rim 2.72 (lid 2.66).

## Stage 3 — UV

kit_build's cleanup: angle-based unwrap, margin 0.008; kit_verify reports no UV overlaps, flips, gap or border
problems on any object. The exporter writes its own palette UVs.

## Stage 4 — Materials and colour

Medians sampled on the hero cell (`<temp>/m070` scripts, numpy in the Blender session), then `MODEL.calibrate` on the
studio dome for stone, timber, plank, wood_dark, ivy, ivy_lime, banner, rope, leather and mat; the light / dark keys
derived from those; then a class check (timber, red, canvas, green, stone, rope medians and lit quartiles) of the
compare renders against the sheet crops, which raised timber, banner, rope and ivy a step (the dome renders brighter
than the hero's mixed faces). Final, hero cell (sheet → ours): timber median #9A4D18 → #9F5015; red #D52524 →
#DC2321; canvas #FEEDC1 → #FFE7B5; ivy #6A8805 → #6D880C (lit #B2CB09 → #AEC813); stone #A48D87 → #B99A93 (lit
#D1B8AD → #E2C4B9, a little light); rope #E2993C → #D1923B (raised again after this check). Front cell: timber
#974C11 → #A75015, stone #A18985 → #AC928A. Side and rear cells read darker in our studio (the key light is
front-left; the sheet lights every face): recorded, not scored. Foliage covers about half the sheet's green share —
the sheet's ground ferns are not modelled and its ivy is still denser.
Colour by role and position only: foot courses blend toward stone_dark (30 %, 15 %), chipped facets stone_light,
footings by role, canvas hem / rim deeper by distance from the edge, ivy tones by height rank (P.ivy), mat stripes by
place. Per-piece Tint ±0.05 and broad mottling. K.check passes (crate bottom and lid at the mean Tint, m066).

## Stage 5 — Lighting

None: no emissive or light in any assembled view. The exploded view's lantern is left out (Brief). No Studio-side
settings.

## Stage 6 — VFX

None: the sheet shows no smoke, glow or particles; the export STATS line reports 0 sockets and no glow keys.

## Renders and compare

`build()` writes `art/blender/renders/models/M070/` (`M070_views.png`: f34, front, side, rear, top, exploded, scale;
`build(close=True)` adds `lash_cu`, `low_cu`, `ivy_cu`, `pad_cu`). `m070.compare()` writes the side-by-side sheet to
`<temp>/RBLX-Flintborn/compare/M070/M070_compare.png` (or `out_dir`). Content W : H (sheet / ours): f34 1.37 / 1.06
(the sheet's wide-angle perspective and ferns), r34 1.36 / 1.06, front 1.32 / 1.45, side 1.27 / 1.19, rear 1.34 / 1.25,
top 1.05 / 1.15. Known misses, all recorded: the f34's perspective makes the far back post and canvas peak read lower
on the sheet; the low point is higher (headroom); the top cell's square canvas and right-hand wall; the rear cell's
crates outside the back wall; the side cell's two-block-deep wall column; denser sheet ivy.

## Main session rulings (2026-11-04)

The recorded departures stand and are not to be scored:
- the canvas low point kept at 6.55 for the walk lane's 6.9 headroom;
- kit-size crates and barrel;
- no ground ferns;
- no lantern;
- the hero view governing over the top cell's layout.

The hero at 5828 against 6000 is accepted, because the margin went to the denser ivy the remade sheet draws.

## Stage 7 verification (round 1)

**Result: PASS, 7.5 / 10.** Re-measured independently in a background session on the work file copy `wip/M070v.blend`
(nothing rebuilt or saved). There are no blockers. The minors below are what is left between the model and the sheet.
None of them is covered by the main session rulings, and none is broken. Renders and crops are in `<temp>/v070/`.

### Technical

- **kit_verify.** Run on the hero and all ten parts with the builder's options (`cls="structure"`, `walk=WALK`,
  `foliage={"keys": ("leaf",)}`): **0 problems** in 17.8 s.
  - Hero: 5828 / 6000 tris, 208 closed shells. Size 19.53 × 17.35 × 14.04, origin at the bottom centre, transforms
    applied, no modifiers or custom normals.
  - Hero geometry: 0 non-manifold edges, bowties, boundary, wire, loose, zero-area faces, n-gons or duplicate verts.
    0 winding, parity, self-intersection or negative-volume shells, and 0 register mismatches.
  - Hero thin corners: min corner 0.366° (canvas strip, floor 0.3°); 25 corners are under 3°.
- **Contact and burial.** Floating 0, unchained 0, 25 grounded shells. Buried 0, deepest 0.044 (moss in block),
  checked with edge midpoints.
  - Ivy, all under 0.05: leaf in stem 0.040, stem in leaf 0.027, leaf in leaf 0.025, pad in stem 0.023.
  - Others: rope tail in canvas 0.042, rope diagonal in turn 0.037, canvas in post 0.030.
  - No pierced thin sheets (11 thin shells).
- **UV and colour.** UV: 1922 islands, 0 overlaps or flips, gap 0.016, border 0.008. Tint against normal: worst 0
  (stone foot blends −0.26 within shell, under 0.3). K.check clean. Sockets none, glow keys none, as the brief says.
- **Parts**, each 0 problems and under 1000 tris:

  | Part | Tris | Size |
  | --- | --- | --- |
  | WallBlock | 36 | 2.5 × 2.3 × 1.95 |
  | WallSection | 538 | 7.52 × 2.94 × 10.10 |
  | Rubble | 108 | |
  | Canopy | 304 | 10.76 × 8.21 × 4.38 |
  | Post | 324 | 11.02 tall (no footing) |
  | Banner | 316 | |
  | Bedroll | 180 | |
  | Table | 244 | seat 1.50 |
  | Crate | 220 | 2.30 |
  | Barrel | 204 | 2.72 |

  Collision tags match the brief.
- **Foliage, 5° sweep.** 62 hero leaves: whole leaves edge-on **0.0 %** at every azimuth step at el 0, 5, 10 and 20.
  The mean-plane edge-on share peaks at 39.6–47.3 %, which is reported only. WallSection (6 leaves): 0.0 %.
- **Walk under the canvas.** Lane x −1.55, y −12 → 0.6: minimum clearance 0.205 (left crate's brace), 0 intersecting
  steps, one rise of 0.14 onto the mat. Headroom above the feet is 6.935 at (−0.55, −2.9). Turning at
  (−1.55, −0.4, 0.14): 0.925 clear at every yaw.
- **`lean_check`.** Canvas underside over the lane (±1.0) is ≥ 6.952 at (−0.55, −3.25). Both crate tops are 2.30;
  barrel lid 2.66.
- **Canvas geometry.** Lowest canvas vertex is z 6.45 at (1.42, −2.48), matching the ruled 6.55 low point. A ray grid
  over the interior finds nothing under 6.8 except the toggle (5.99 under the low point). The canvas plan area is 33.1,
  which is 61 % of the 54.1 triangle between the three posts.

### Views against the sheet

The compare sheet was re-run (`m070.compare`, then again at 720 px). I also rendered four trial hero cameras and
nine close-ups (FR, FL and back-post lashings, low point, peak ivy, banner, props, side wall's outer face, wall tops).

- **f34 (hero).**
  - **Camera.** At the compare camera (az 0, el 24, lens 1.5), the canvas reads as a peaked pyramid. Its gathered back
    corner stands 0.61 of the FL post's screen height above the front ties; on the sheet it is 0.24. The whole back
    (peak, back post) also stands much higher over the front than the sheet draws it.
  - **Matched camera.** At **el 12, lens 0.8** (content W : H 1.27 against the sheet's 1.37; 1.06 at the current
    camera) the read is close to the sheet:
    - a cream sheet sloping from the back post to the two front ties, with its front edge dipping toward the right
      crate;
    - the peak with its ivy curtain left of centre and the stepped skyline;
    - the side wall and crossbeam at the left, and the banner on its crossarm at the right;
    - barrel, crates, bedroll and mat in the same order.
  - **Low point.** The dip is much shallower than the sheet's deep V. That is the ruled 6.55 low point, so it is not
    scored.
- **front.**
  - The peak, the stepped back wall, the side-wall column and the posts all match (the FR post is 12.0).
  - **Back-post top.** On the sheet it is 0.75 stud under the FR post's top, against about 1.4 here at lens 3.
  - **Canvas ties.** Normalised to the FR post's height:

    | Point | Sheet | Ours |
    | --- | --- | --- |
    | Back tie above the FL tie | 0.18 | 0.19 |
    | FR tie above the FL tie | 0.14 | 0.09 |
    | Low point under the FL tie | 0.27 | 0.15 |

    The low point is the ruled one.
  - Props and rubble match the sheet's order.
- **side.**
  - **Canvas.** The sheet's low corner sits about 2.7 studs behind the FR post, which supports the builder's y −2.6. The
    canvas sag and the tall two-block back-wall column match.
  - **Banner.** The sheet does not draw it in this cell; ours shows it edge-on. Content cell, recorded only.
- **rear.**
  - The wall outline, the peak right of centre, and the post tops at both ends all match.
  - **Ivy.** The sheet's two ivy curtains are full and leafy; ours are thin single runs (green share 3.0 % against
    8.5 %, the sheet's figure including some ferns).
  - **Crates and banner.** The sheet's crates outside the back wall are a recorded miss. The banner shows at the left
    here; the sheet hides it.
- **r34 (mirrored, content only).**
  - Everything is present: banner post, back post, canvas, bedroll, mat, crates and the ivied wall.
  - **Canvas.** It reads as a narrow triangular sail rising to the back post; the sheet draws a broad sagging tarp.
  - **Ivy.** The sheet has ivy curtains all over the outer face; ours has one run.
- **top (content only).** The canvas plan is an arrowhead: a triangle from the back post to the front posts with a deep
  notch to the low point. It covers about a quarter of the interior; the sheet's square canvas covers nearly all of
  it. The ruling covers three ties against four. The narrowness is recorded under Minors.
- **Exploded and parts.** Every named part is present (lantern and bracket post left out by ruling).
  - The Canopy part is the hero's wedge, where the sheet's canopy is a square sheet with four corner tabs.
  - The sheet's exploded bedroll is a gold spiral roll; ours follows the hero's brown roll with gold caps.
- **Close-ups.**
  - **FR lashing.** Gold collars, an X on the front face, and the canvas corner meeting the post under the lower
    collar.
  - **Lashing cell.** The sheet draws chunky round rope with the canvas pulled into the knot. Our X diagonals read as
    thin flat slats, and the canvas corner butts the post instead of being bound.
  - **Back post.** The gather and its two collars are clean.
  - **Other details.** The crossbeam to the side wall is there. The banner (hem sleeve, three points, white diamond,
    dark pole) matches. Moss patches read flat.
- **Colours** (sheet hero cell → our hero render, class medians, with the lit quartile in brackets):

  | Material | Sheet | Ours |
  | --- | --- | --- |
  | timber | #964C17 (#CB6818) | #9F4F15 (#A95016) |
  | canvas | #FEEDC2 | #FFEABC |
  | ivy | #6C8B05 (#B2CC05) | #6D8A09 (#B2CF10) |
  | banner | #D62624 | #DC2321 |
  | rope / gold | #E19639 | #DD933C |
  | stone | #A48A85 (#E0C6BE) | #B99B94 (#E2C2B8) |

  - Front cell stone: #A18882 → #B3958E.
  - Rear and side stone: #C2A49D → #A38B8A and #C0A39D → #8C7775. These are darker under the studio's front-left key,
    which HOUSE_RULES records rather than scores.
  - Timber's lit faces lack the sheet's bright orange (#CB6818 against #A95016). This is a lighting split, recorded.

### Blockers

None.

### Minors

1. **Canvas plan narrowness** (largest gap). The canvas covers 33 of the 54 plan units between its three ties, because
   the front edge is pulled back 3.4 studs to the low point at y −2.6. It reads as a narrow sail in r34, top and the
   Canopy part, where the sheet draws a broad sagging tarp.
   - Fix if wanted: keep the ruled z 6.55 and x 1.35, but bring the low point forward to about y −4.0. Then make the
     front edge sag in z rather than pull back in plan (a softer tent in u), so the canvas covers about 80 % of the
     triangle. Re-check `lean_check` (≥ 6.9 over x −2.55 … −0.55).
2. **Hero compare camera.** el 24 / lens 1.5 exaggerates the back's height and makes the canvas look like a pyramid.
   el 12 / lens 0.8 matches the sheet's framing better (W : H 1.27 against 1.37); suggest it for `COMPARE["f34"]` and
   the `f34_sheet` view.
3. **Ivy density.** The ivy is about half the sheet's: the rear and r34 curtains are single runs, and the green share
   is 1.7–3.0 % against the sheet's 5.9–8.5 % (ferns ruled out). The budget leaves 172 tris; more ivy would need cuts
   elsewhere (for example rope-turn or brace tris).
4. **Lashing read.** The X diagonals read as flat slats, not the sheet's round rope, and the canvas corners butt the
   posts rather than being bound into the knot (lashing close-up cell).
5. **Ivy stem stubs.** The tops of several ivy stems stick up above the wall tops as bare brown twigs: the peak top in
   the hero view, and the top-down wall tops. The sheet's ivy spills over the top edge with leaves.
6. **Side and rear cells.** The banner is visible edge-on (side) and at the left (rear) where the sheet omits it. These
   are content cells, recorded only.
7. **Lit timber.** It is a step darker than the sheet's lit orange. This is studio lighting, recorded.
