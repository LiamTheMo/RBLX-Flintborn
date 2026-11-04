# 052 Boardwalk — spec

Reference: `art/blender/assets/references/052.png` (remade, "BOARDWALK / BUILDING MODEL STUDY", PAGE 052). The earlier
spec followed the old sheet; git history keeps it. Builder: `art/blender/kit/mcp/m052.py` (on `kit_parts` /
`kit_build`, rewritten from scratch). Procedure: `art/blender/kit/mcp/STAGES.md`, `HOUSE_RULES.md`.

## Brief

- **Sheet:** 052 Boardwalk (remake: yes). Family: none (timber language shared with 048 / 050: chamfered square posts,
  bolt blocks, knee braces).
- **Class and budget:** structure (walked on), ceiling 6000, plan 5400. Built: hero 1864, Straight 1464, parts ≤ 108.
  The sheet is chunky low-poly ("broad planar faces, crisp edges"), so the model needs far less than the ceiling.
- **Size:** module length is the house **16-stud pitch** (the notes say it tiles; cell C tiles two). The deck height
  comes from the sheet's proportions at that pitch: in the front cell the deck top stands 175 px (4× crop) above the
  ground over a 920 px run of the module, and the rail post tops 300 px. That gives **deck top 3.0** (3.04) and rail
  post tops 5.15. The side cell's R6 figure (5 studs = 77.5 px) gives deck 2.82, posts to 5.24, so both agree. Depth
  from the top cell (length : depth with stubs and blocks 2.78) and the f34: **planks 6.0 across**. Hero **18.75 L
  (stairs foot -10.75 to 7.99) × 6.90 W (bolts) × 5.15 H**; deck top 3.00.
- **Hero view:** f34 at camera (-24, 19) (fitted against the cell). The r34 is a redraw of the f34 (rail far, stairs
  left; content only). Front = -Y elevation (az 0). Side = an end elevation, compared from +X mirrored, because it draws
  the rail on the left and no stairs (content only). Rear (az 180) and top are content only.
- **Parts:**
  | Part | What | Tris target |
  | --- | --- | --- |
  | TimberBoardwalk (hero) | 12 planks, 8 support posts + blocks + bolts, 6 side beams, 4 joists, 2 headers, 14 braces, 5 rail posts, 4 rails + 2 stubs, 3-tread stair on 2 sleepers | ≤ 5400 (1864) |
  | TimberBoardwalkStraight (variant) | tiling continuation: no stairs, no -X end posts | ≤ 5400 (1464) |
  | TimberBoardwalkRailPost | back rail post with its end stub | 64 |
  | TimberBoardwalkSupportPost | support post, bolt block, bolt | 68 |
  | TimberBoardwalkRailPlank | one rail segment (bay 3.66) | 28 |
  | TimberBoardwalkFloorPlank | one deck plank 1.31 × 0.40 × 6.0 | 28 |
  | TimberBoardwalkStairs | three stacked slabs + two sleepers | 108 |
  | TimberBoardwalkCrossbeam | one side beam segment between support posts (the exploded view's "Crossbeam") | 28 |
  | TimberBoardwalkBrace | 45° knee brace | 12 |
- **Palette:** swatches (flat medians): Timber Primary `#B05A1C`, Timber Light `#EDA75E`, Timber Pale `#E2C697`,
  Hardware `#ABA8A3`, Accent Green `#93A474`, Accent Blue `#37B1E1`. The drawing uses only the timber: rendered f34
  medians deck top `#F58D3C`, stair top `#F18A3A`, rail front `#FB9D4C`, lit leg side `#C6641A`, block `#D06812`,
  bolt `#F89834`, shaded post face `#89410F`. Keys: `m052_wood` (planks, posts, rail, blocks, treads), `m052_wood_deep`
  (beams, joists, headers, braces, sleepers), `m052_wood_light` (rail post cap tops, cap bevel 50 %), `m052_bolt`
  (bolt heads: the sheet draws them pale orange, not the grey hardware swatch). Matte (rough 0.85; bolt 0.55), metal 0.
  Pale, grey, green and blue are not used (none appear in the drawing).
- **Lights / VFX:** none.
- **Collision:** hero and Straight precise (walked on); RailPost / RailPlank / FloorPlank / Crossbeam box, SupportPost /
  Stairs / Brace hull.
- **Checks to switch on in kit_verify:** `cls="structure"`; `walk` from the stair foot up onto the deck and along it
  (paths y -1.4 / 0 / 1.0 from x -11.6 to 7.4, feet z 0, ride, planks / treads / sleepers / headers skipped as floor
  and risers, turns at x 0 / ±5.4, y -0.4, z 3.0); `seams` pitch (16, 0, 0) on TimberBoardwalkStraight (the hero's
  stairs pass -8). Builder checks: `deck_check` (plank tops 3.00, stair tops) and `junction_check` (hero then Straight at
  +16).
- **Departures from HOUSE_RULES:**
  - **Deck top 3.00, not 2.60.** The sheet's proportions at the 16-stud pitch give 3.0, the same reasoning as 048's
    4.40 ruling (the remakes govern). The stairs still keep risers within the rule: four rises of 0.75.
  - **A second exported model, TimberBoardwalkStraight** (role variant, 1464 tris, as m069's StockadeStraight). The hero
    has stairs at -X, so it can't repeat; the Straight continues a run and shares the end posts of the module before it.
- **Questions for the main session:** none. (If the main session prefers deck 2.60, change `DECK_TOP` and `RAIL_Z` /
  `RP_TOP`: the stairs then give 0.65 rises.)

### Reading the sheet (recorded misses, not blockers)

- **Stairs.** The f34 and front cells draw two slabs plus the deck (three rises of 1.0 at our height). Close-up A, the
  exploded view, the parts list and the notes ("three-step staircase", "Stairs (3 Steps)") draw three treads. Built
  three treads (four rises of 0.75), which keeps the house riser limit. The top view draws the stairs over the front
  ~40 % of the end only; the f34 and close-up A run them across the whole end, and we built that.
- **Counts.** The notes and parts list say 6 back rail posts and 5 support posts. Every drawn view shows 5 rail posts and
  4 support posts a side (front and rear cells; rear legs at the ends and thirds), so we built 5 and 4 + 4 (the drawing
  governs). Braces: the front / rear cells draw knee braces on both inner sides of every leg (6 a long side), and the
  side cell and the f34's right end draw one diagonal under each end; built 12 + 2 (the parts list says ×4).
- **Rear cell** is a redraw of the front without stairs; ours, seen from +Y, shows the stairs on the right.
- **Side cell** (W : H 1.04) is narrower than ours (1.33) and the top cell (2.69) is deeper; the f34 and top govern
  the 6.0 depth.
- **Top cell** shows a bolt dot on each rail post cap and bolt blocks at the two front corners only. Ours has plain caps
  and a block on every support post (front / rear cells and the f34).
- **Tiling cell C:** two modules share their end supports and rail. Built as the hero followed by Straight modules:
  one post row at each joint, 9 rail posts and 7 support rows for two modules, as the cell. The joint bay is
  4.0 / 5.33 (rail / supports) against the hero's 3.66 / 4.83.

## Stage 1 — Modelling (2026-11-04)

Build frame: long axis X, front (open long side) -Y, back rail +Y, stairs at -X, ground z 0, deck centred on x 0 /
y 0. The hero's origin is its bbox bottom centre, so `m052_offset` is (-1.376, 0, 0). Every piece is its own closed
shell (no booleans), seated 0.002–0.02 into what carries it.
- **Deck:** 12 planks laid across the width, 1.315 wide, 0.02 gaps, 0.40 thick (top 3.00), long edges chamfered 0.05,
  ends at y ±3.00; the run's end planks reach x ±7.998 (the seam planes).
- **Support posts:** 8, 1.0 square (vertical edges chamfered 0.05), x ±7.25 / ±2.417, y ±2.50 (outer faces flush with
  the plank ends), ground to the plank underside. On each outer long face, a chamfered bolt block (1.12 × 0.84, 0.25
  proud, z 2.00–2.84, over the beam line and the plank ends) and a bevelled square bolt head (0.52, 0.20 proud): the
  sheet's rounded knob. End posts' outer x faces at ±7.75 (the planks overhang 0.25, as the front cell draws).
- **Frame:** side beams between the posts under the plank ends (|y| 2.42–2.92, 0.08 behind the post faces, z
  2.00–2.62); a joist across under the deck at each post pair (0.6 wide); a header across each end on the end posts'
  outer x faces (x ±7.73–7.99). These are the f34's continuous fascia under the plank ends and the end beam on the
  right end (050's verifier blocker: keep the frame on the long sides).
- **Braces:** knee braces in the long-side planes (|y| 2.55–2.85), 45°, 0.34 wide, from each post's inner x face up to
  the beam underside 1.10 along; one diagonal under each end (front end post's inner face up to the end joist).
- **Railing:** 5 back rail posts, 0.85 square, x ±7.325 / ±3.663 / 0, y 2.575 (outer faces on the plank ends),
  standing on the planks (sunk 0.02) to 5.15 with an 0.08 cap bevel. The rail (0.38 × 0.43, z 4.12–4.55) runs between
  them, butted into the post faces; a chamfered stub block on each end post's outer face (to x ±7.99) is the rail end
  the f34, front and top cells show past the end posts.
- **Stairs:** three stacked slabs across the -X end (y ±2.95), tops 0.75 / 1.50 / 2.25 (runs 0.92). Each sits 0.003
  into the one below; the bottom slab sits on two sleepers (the f34's dark feet). The lower two run back into the end
  posts' outer faces; the top one stops on the header.
- **TimberBoardwalkStraight:** the same module without stairs and without its -X end posts, header and end brace.
  Supports at x -3.417 / 1.917 / 7.25 and rail posts at -4.675 / -0.675 / 3.325 / 7.325 keep the run's rhythm from
  the module before. Its -X side beams and rail run to x -7.99 and meet that module's header and stub 0.02 away.
- Parts as the sheet's parts list. TimberBoardwalkCrossbeam is the long member the exploded view labels "Crossbeam".
- **Candidate for kit_parts:** `pad()` (a plate sunk into a face with a bevelled front: bolt block, stub, square bolt),
  copied from m048 as the brief asked. 048 and 052 now both carry it.

## Stage 2 — Optimisation and cleanup

kit_verify (`cls="structure"`, walk, seams on the Straight): **problems []** (1.4 s). Tris: hero 1864 / 6000 (post
444, plank 336, brace 168, beam 168, block 160, bolt 160, rail 152, joist 112, tread 84, header 56, sleeper 24);
Straight 1464 / 6000; parts RailPost 64, SupportPost 68, RailPlank 28, FloorPlank 28, Stairs 108, Crossbeam 28,
Brace 12. Hero 78 closed shells; 0 non-manifold / bowtie / boundary / wire / loose / zero-area / n-gon / duplicate;
0 winding errors, self-hits, parity-inward or negative shells; min corner 44.6°. Floating 0, unchained 0, buried 0
(deepest 0.02). Every object is the same. Origin at the bottom centre, transforms applied, no modifiers or custom normals.
Sizes: hero 18.748 × 6.90 × 5.15, Straight 15.996 × 6.90 × 5.15.
- **Walk (hero):** all three paths climb 0 → 0.75 → 1.50 → 2.25 → 3.00 (rises 0.75, the last 0.748 + 0.002) and walk
  the deck to x 7.4. Clearance: 0.25 (y -1.4, to the front end post), 0.45 (centre), 0.15 (y 1.0, to the rail posts).
  0 intersecting steps; nothing overhead. Turns at (0 / ±5.4, -0.4) clearance 1.04 / 0.675, 0 intersecting yaws. Clear
  width between the rail posts' inner faces (y 2.15) and the open front edge (y -3.0): 5.15.
- **Seams (Straight, pitch 16):** 0 crossing triangle pairs, gap 0.004, nothing past ±8.000. End sections identical:
  the end planks' faces, z 2.65–2.95, mismatch 0.0.
- **Junction (hero then Straight at +16, `junction_check`):** 0 crossing pairs, closest 0.004 (hero max x 7.998,
  Straight min x 8.002).
- `deck_check`: 60 samples a module, every plank top 3.000; stair tops 0.75 / 1.50 / 2.25.

## Stage 3 — UV

kit_build cleanup (Smart UV, margin 0.008): hero 550 islands, Straight 349. 0 overlaps, 0 flips, min gap 0.016,
border 0.008, density even, conformal stretch p95 1.00 / 1.08.

## Stage 4 — Materials, colour and texture

We calibrated as 050 did: render the hero at the f34 camera with `compare.py` (600 px high), sample the same regions in
the sheet crop and the render (medians), and correct each key per channel in linear light. We didn't use the dome,
because the sheet's light darkens the -Y faces far more than the studio does.

| Region | Sheet | Ours (first: `#C46A27` …) | Ours (final) |
| --- | --- | --- | --- |
| Deck top | `#F58D3C` | `#FD8130` | `#F58F3A` |
| Stair top | `#F18A3A` | `#FA7E2E` | `#F28D38` |
| Bolt block (lit) | `#D06812` | `#DA6A20` | `#D2772A` |
| Lit leg side | `#C6641A` | `#DE6D21` | `#D77A2B` |
| Bolt head | `#F89834` | `#FFC663` | `#FF9B3C` |
| Shaded post / leg -Y face | `#89410F` / `#92450F` | — | `#D5792B` (studio light; recorded) |
| Whole model, brown median | `#B45A17` | `#E26F23` | `#DB7C2C` (studio light; recorded) |

Final keys: wood `#BE7531`, wood_light `#E19348`, wood_deep `#965520`, bolt `#EC8E3A`. Colour by role and position only
(beams and braces wood_deep; rail post cap bevel 50 % and tops toward wood_light); per-piece Tint ±5 % (planks and
treads ±6 %) so the deck is not one flat colour. Tint against normal worst 0.0. The lit tops, the blocks and the bolts
match. The sheet's -Y faces and underside are much darker than ours, because its light falls from behind-left; that
is the lighting difference HOUSE_RULES records rather than scores.

## Stage 5 — Lighting: skipped

The sheet shows no lantern, glow or emissive part. No Studio-side lighting needed.

## Stage 6 — VFX: skipped

No smoke, sparkle or other effect on the sheet; no sockets (export STATS: 0 sockets, 0 glow keys).

## Renders and compare

`build(close=True)` writes `M052_views.png` (f34, r34, front, side, rear, top, exploded, scale), `stair_cu.png`
(close-up A) and `under_cu.png` (close-up B). `m052.compare()` writes the side-by-side sheet to
`<temp>/RBLX-Flintborn/compare/M052/` (cell boxes in `m052.COMPARE`). `m052.tile_compare()` places the Straight at
+16 behind the hero and pairs it with cell C. W : H, sheet / ours: f34 2.089 / 2.181, r34 2.092 / 1.848 (a redraw),
front 3.48 / 3.73 (our third tread), side 1.04 / 1.33, rear 2.83 / 3.65 (ours shows the stairs), top 2.69 / 2.71,
tile 6.02 / 4.92. The sheet crops of f34, r34 and tile include their captions, which inflate the sheet's height.

## Modeller's notes for the verifier

- Hero view: the f34 governs; compare the r34 on content only, and the side cell mirrored against +X.
- Seams run on TimberBoardwalkStraight (`VERIFY["seams"]["obj"]`); the hero to Straight joint is `junction_check`.
- Remaining look differences: three treads against the f34's two (house riser limit); the front faces and underside
  read lighter than the sheet (studio light); plank seams are 0.02 gaps with 0.05 chamfers, so they read as fine V
  lines rather than the sheet's inked lines; bolt heads are bevelled squares, the sheet's slightly rounder.

## Main session rulings (2026-11-04)

1. **Deck top 3.00** from the remade sheet's proportions at the 16-stud pitch stands (as 048's 4.40). The three
   0.75 risers keep the walk-up rule.
2. **`TimberBoardwalkStraight`** (the hero without stairs and -X end posts, for continuing a run) is accepted as a variant.
3. The drawing governs the counts (5 rail posts, 4 supports a side, 12 knee braces, three steps); the text counts are
   recorded misses.

## Stage 7 verification (round 1)

**Result: PASS, 8/10.** No blockers. Verified read-only in a background session on the `wip/M052v.blend` copy (built
after the current `m052.py`); nothing rebuilt or saved. Scratch renders in `<temp>/RBLX-Flintborn/v052/`.

### Technical (re-run)

- `kit_verify.run` on all nine objects (`cls="structure"` for TimberBoardwalk and TimberBoardwalkStraight, parts
  `part`; sizes; walk; seams on the Straight at pitch 16): **problems []**, 1.5 s. Hero 1864 / 6000, 78 shells;
  Straight 1464 / 6000, 60 shells; parts RailPost 64, SupportPost 68, RailPlank 28, FloorPlank 28, Stairs 108,
  Crossbeam 28, Brace 12. Every object: 0 non-manifold / bowtie / boundary / wire / loose / zero-area / n-gon /
  duplicate; outward normals, 0 winding errors; floating 0, unchained 0, buried 0 (deepest 0.02); min corner 44.6°;
  origin at the bottom centre, transforms applied, no modifiers or custom normals. UV 550 islands, 0 overlaps / flips,
  gap 0.016, border 0.008. Sizes 18.748 × 6.90 × 5.15 and 15.996 × 6.90 × 5.15. `K.check` clean on both (KITSTAT ok).
- **Walk, stair foot onto the deck** (y -1.4 / 0 / 1.0, x -11.6 → 7.4, feet z 0, ride): every path rises 0.75,
  0.75, 0.75, 0.748 (+0.002) to 3.00; 0 intersecting steps; nothing overhead. Clearance 0.25 / 0.45 / 0.15 (front end
  post, end joist, back rail post). Turns at x 0 / ±5.4: clearance 1.04 / 0.675, 0 intersecting yaws. Straight walked
  end to end at z 3.0 (three paths): 0 intersecting steps, clearance ≥ 0.15.
- **Seams (Straight, pitch 16):** 0 crossing pairs, gap 0.004, end sections identical (z 2.65–2.95, mismatch 0.0),
  nothing past ±8.000.
- **Hero to Straight joint:** `junction_check` 0 crossing pairs, closest 0.004 (hero max x 7.998, Straight min x
  8.002). kit_verify seams with `with` gives the same for the hero → Straight pair (0 crossing, sections identical).
  The hero → hero and Straight → hero pairs fail as expected (the stairs pass -8); the hero only starts a run.
- `deck_check`: 60 samples a module, all plank tops 3.000; stair tops 0.75 / 1.50 / 2.25.

### Views against the sheet

`m052.compare()` (height 480) and `tile_compare()`, plus silhouette overlays (wood-colour masks, aligned on top,
bottom and right edges) and close-ups. W : H sheet / ours: f34 2.09 / 2.18, r34 2.10 / 1.85, front 3.48 / 3.75, side
1.04 / 1.33, rear 2.82 / 3.64, top 2.68 / 2.71, tile 6.02 / 4.92.
- **f34 (governs):** reads as the sheet: 12 planks across (the sheet draws 12–13), 4 front support posts at the ends
  and thirds, each with a bolt block over the beam band, knee braces on the inner sides of every post, one diagonal
  under the right end rising from the front post (as the sheet's right end), 5 back rail posts on the deck with the
  rail between them and end stubs past both end posts, stairs across the whole -X end on dark feet. Overlay IoU 0.73.
  The remaining silhouette offsets (rail posts drift up to ~0.9 stud along the back) come from the sheet's
  perspective: its back edge is drawn longer than its front edge, which a near-orthographic camera can't match. The
  third tread is ruled.
- **Front:** overlay IoU 0.70. Deck top 3.07 / 3.07 (sheet / ours, scaled to the 5.15 top), beam underside 1.91 / 2.0,
  rail post tops aligned, post positions within ~0.2 stud except the first (sheet ~0.3 further in). The rail band is
  thinner than the sheet's: 4.05–4.61 against 4.12–4.55 (minor 1).
- **Side (mirrored, content only):** rail post with its stub, deck, two legs, one diagonal: all present. The sheet's
  diagonal rises from the rail-side leg, ours from the front leg; the f34's right end (governs) matches ours. The sheet
  draws a face-on bolt on the end face of the front leg; ours has blocks on the long faces only (front, rear and f34
  cells). The recorded W : H miss stands.
- **Rear / r34 (redraws, content only):** posts at the ends and thirds, braces both sides of each post, blocks on every
  rear post, 5 rail posts. Ours shows the stairs at the right, as recorded.
- **Top (content only):** 12 planks, 5 rail posts, stairs at the left end, blocks along both long sides. The recorded
  misses stand (sheet: bolt dots on the caps, front-corner blocks only, stairs over ~40 % of the end, rail drawn past
  the plank ends).
- **Close-up A (stairs / post):** chunky stacked slabs against the end post with its block and bolt, dark feet under
  the bottom slab; matches. Our bottom slab is 0.50 thick on 0.25 sleepers, so it reads thinner than the two above;
  the sheet's three slabs are equal (minor 2).
- **Close-up B (underside):** our renders from below (el -15 / -18) show side beams, a joist across at every post pair,
  knee braces and the end diagonals, all closed and seated. The sheet's cell draws heavier post-top collars and one
  long diagonal to a crossbeam; ours carries the same members as plates and knee braces (minor 3). The builder's
  `under_cu` camera (el -4) barely looks under the deck (minor 6).
- **Tiling (cell C):** hero + Straight at +16: 9 rail posts and 7 support rows, one post row at the joint, plank seam
  closed, as the cell. Joint bays 4.0 / 5.33 against 3.66 / 4.83 (recorded). At each joint the hero's 0.54 rail stub
  sits proud of the 0.38 × 0.43 rail, a small knob where the cell draws a plain rail (minor 4).
- **Parts against the parts list:** RailPost with stub, SupportPost with block and bolt, FloorPlank, Stairs (three
  steps), Crossbeam, Brace match their cells. The sheet's "Rail (×1)" is one long rail; ours is one bay (2.85)
  (minor 5).
- **Colour** (medians, sheet f34 crop / our f34 render): deck top `#F28B3B` / `#F28D39`, stair top `#F78F3D` /
  `#F38E39`, bolt block `#D86812` / `#D2772A`, bolt `#F79432` / `#FF9B3B`, beam front `#A85012` / `#A2521A`, support
  post front `#C66319` / `#D77A2B`. Lit and role colours match. The faces the sheet's light leaves in shade read much
  lighter here: rail front `#AF5615` / `#DB7C2C`, rail post front `#A95315` / `#D97B2B`, post side `#69310C` /
  `#C26E28`, whole-model wood median `#B55A17` / `#DB7C2D`. Studio lighting: recorded, not scored (HOUSE_RULES).

### Blockers

None.

### Minors

1. The rail section (0.38 × 0.43) reads thin against the front cell's ~0.56 band (4.05–4.61). Optional: `RAIL_Z`
   (4.05, 4.58), with the stub a touch larger.
2. Bottom tread 0.50 thick on 0.25 sleepers against the sheet's three equal slabs. Optional: sleepers about 0.10 high
   and a thicker bottom slab.
3. Underside: no post-top collars where the beams bear and no long diagonal as close-up B draws (content close enough;
   the knee braces and joists carry it).
4. A rail stub knob at each module joint (the hero's or a Straight's +X end against the next Straight's rail).
5. The RailPlank part is one bay, not the sheet's single long rail.
6. `CLOSE["under_cu"]` at el -4 doesn't show the underside; an elevation of about -15 would match cell B.
7. Already recorded and ruled, not rescored: the third tread, the counts (5 rail posts, 4 supports a side, 14 braces),
   deck top 3.00, the side / top / rear cell differences, square bolt heads, studio-light shading, joint bay widths.
