# 051 Rope Crossing — spec

Reference: `art/blender/assets/references/051.png` (remade 2026-11-03, "ROPE CROSSING / BUILDING MODEL STUDY"). The
earlier spec followed the old sheet; git history keeps it. Builder: `art/blender/kit/mcp/m051.py` (on `kit_parts` /
`kit_build`). Procedure: `art/blender/kit/mcp/STAGES.md`, `HOUSE_RULES.md`.

## Brief

- **Sheet:** 051 Rope crossing (remake: yes). Family: none (shares m050's rope-turn language).
- **Class and budget:** structure (a bridge, walked on), ceiling 6000, plan 5400. Built: hero 5322, parts ≤ 524.
- **Size:** the side cell's R6 figure is 79 px for 5 studs (15.8 px/stud); the front cell is 120 px tall (post tops
  y 521 → ground 640), stone tops 52–60 px above the ground, posts 59 px above the stones, post centres 202.5 px apart
  (1.69 H), the deck sagging 13 px below the stone tops, the upper rail's low point 15 px above them. The top cell gives
  L : W 2.76 at the posts and 8 planks over 0.75 of the post spacing. Built at H 7.20: stone tops **3.47**, post tops
  7.20, post centres ±6.10 × ±2.30, deck 3.47 at the ends → 2.67 at mid-span, rail low point 4.37. Hero **17.39 L ×
  8.64 W × 7.20 H**.
- **Hero view:** f34 at camera (-20, 20) (fitted from the across / along offsets of the post pairs; no single camera
  fits the drawing, see below). r34 (160, 20) is a redraw of the f34 (content only). Front (0, 0) is the -Y long side,
  rear (180, 0) the +Y side, side (90, 0) the end, top (0, 89.9) a plan with the long axis horizontal.
- **Parts:**
  | Part | What | Tris target |
  | --- | --- | --- |
  | RopeBridge (hero) | 4 stones + 9 chunks, 4 posts (turns, cloth), 8 planks, 2 upper rails, 12 hangers, 4 diagonals, 4 backstays, 14 lower-rail links | ≤ 5400 (5322) |
  | RopeBridgeEndPost | base block, shaft and cap, two rope turns, the cloth lashing | ≤ 600 (524) |
  | RopeBridgePlank | one 1.00 × 0.62 × 4.70 plank, pegs on its end faces | 56 |
  | RopeBridgeMainRope | one upper rope rail coil to coil with 6 knots | 464 |
  | RopeBridgeLowerRope | one continuous lower rail along the deck curve | 100 |
  | RopeBridgeHangerRope | one hanger with its middle knot and knot foot | 60 |
  | RopeBridgeAnchorStone | one anchor stone with its chunks | 168 |
- **Palette:** swatches (flat medians): Timber Dark `#BF6426`, Timber Light `#E5C18D`, Rope `#E6C18C`, Stone Light
  `#C0BFBF`, Stone Mid `#9C9DA0`, Cloth Wrap `#C53A34`; header `#C36828 #E6C493 #ACADAF #85A056 #27A4D0` (green and blue
  are sheet chrome). The drawing governs over the swatches: its timber renders orange-brown (no tan timber anywhere) and
  its rope a saturated gold. Keys: `m051_wood` (planks), `m051_wood_light` (cap tops), `m051_wood_deep` (posts),
  `m051_wood_dark` (peg holes; base blocks 25 % toward it), `m051_rope` / `m051_rope_dark` (one strand),
  `m051_peg`, `m051_cloth` / `m051_cloth_dark` (knot), `m051_stone` / `m051_stone_mid`; all matte, metal 0.
- **Lights / VFX:** none (the sheet shows no glow, light or effect).
- **Collision:** hero precise (walked on); EndPost hull, Plank box, AnchorStone hull, the three rope parts none.
- **Checks to switch on in kit_verify:** `cls="structure"`; `walk` from stone top to stone top (paths y 0 / ±0.3,
  x -7.6 → 7.6, feet floor 2.62 so the proxy rides down the sag, planks and stones skipped as floors, turning at the
  mid-span (0, 0, 2.67) and on the stone top (-6.9, 0, 3.47)). Not a tiling module: no seams.
- **Departures from HOUSE_RULES:**
  - **Stone tops 3.47, not the 2.60 raised floor.** The anchor stones are half the sheet's height; at 2.60 they read
    as low plinths (front W : H about 1.2 against the sheet's 0.8). 3.47 = four 0.8675 risers (the riser rule holds),
    the sheet's character scale gives 3.3–3.8, and the deck's low point lands at 2.67, next to the house 2.60. One
    constant (`ST`); everything else is built relative to it.
  - **Both ends open:** the side and top cells draw a rope across each end between the two posts at chest height
    (about 2.0 above the stone tops); it would stop a player walking on, so it is left out (as the old ruling).
- **Questions for the main session:** keep `ST` 3.47 (sheet look) or set the house 2.60 (stones 25 % lower)?

### Reading the sheet (recorded misses, not blockers)

- **f34 camera.** The f34 draws each end's two posts almost side by side while showing the long side broadly; fitting
  the post offsets gives az -19 / el 19, but then the far posts should stand about 40 px higher than drawn. (-20, 20)
  keeps the layout (near end lower left, far end upper right); W : H 1.63 against the cell's 1.85 (the cell crop holds
  the title).
- **Across width.** The side cell draws the posts 3.4 apart (centre to centre); the top cell's L : W gives 4.6. Built
  4.6 so a player fits between the base blocks (3.16 clear); side cell W : H 1.16 against 0.90.
- **Stone pairs.** The side cell draws two stones with an open gap, the top cell one outline per end with a notch, the
  f34 two stones at -X and one block at +X. Built: two stones per end whose tops meet in a 0.10 seam (walkable) with a V
  gap opening below (as the old ruling).
- **Exploded cubes.** Four unlabelled pegged cubes near the post feet are not built (not in any assembled view, and
  there is no room between the stone edge and the base block); the lower rail ends at the end planks.
- **Planks.** The faint lengthwise line and end cross-lines on the plank tops are not modelled (flat-shaded faces); 8
  planks (top and exploded cells) against the front cell's ambiguous 7 blocks.
- **Hangers.** 6 per side on planks 2–7 plus a diagonal to each end plank (front cell: 4 hangers + 2 diagonals
  visible; f34 about 7).
- **Cloth.** Red shows small in the front cell, larger in the rear and on the end faces in the f34: built as a wrap
  round each post's outer end (end face and the outer halves of both long faces), with a knot at its (end, +Y) corner
  and one tail on each of those faces.

## Stage 1 — Modelling (2026-11-04)

Build frame: long axis X, front -Y, ground z 0, symmetric about both axes but for stone facets and chunks.
- **Anchor stones** (4): lofted shells through five 9-point rings (ground, 1.39, 2.75, 3.27, flat top): deck-side face
  at |x| 5.00 vertical down to 2.75 (clear of the end planks' feet, 0.08 at the closest), then flaring to 4.20 at the
  ground (the front and top cells' inward flare); outer face 7.95 (top) → 8.30; long face 3.35 → 3.60; cleft face
  0.05 → 0.80 (the pair's V gap); a corner cut on the outer corner, two facet columns (ridge and groove) on each outer
  face, 0.20 chamfer on the outer top edges. Loft quads split on the shorter diagonal (non-planar facets).
- **Chunks** (9): faceted blocks against the stone faces, pushed out by bisection until they sink 0.02 (hull-to-hull,
  dense face sampling; sliver hull faces dropped from the planes). The near-left stone carries the big lower step
  block the f34 shows.
- **Posts** (4): base block 1.44 square (z 3.45 → 4.27, chamfer 0.05); shaft 1.10 → cap 1.26 at 6.45, bevel 0.07 to
  the top at 7.20, a 0.20 square peg hole 0.06 deep (one shell). Two twisted rope turns under the cap (m050 `wraps`:
  12 points, rounded corners; Ø 0.28, 6 sides, `twist=True` reads as rope, `twist=False` read as flat plates). Cloth
  wrap 0.46 tall, 0.05 thick, 0.004 off the shaft, 0.003 under the lower turn; knot lump and tails (1.00 and 0.80
  long) at the (end, +Y) corner.
- **Deck:** 8 planks 1.00 × 0.62 × 4.70 (|y| 2.35), pitch 1.205 (0.205 gaps), each tilted so both top edges lie on
  z = 2.67 + 0.80 (x / 4.7175)²; the end planks' outer top edges at 3.452 (the chamfer) beside the stone tops (0.28
  gap). A square peg on every end face.
- **Rope** (all twisted): upper rails Ø 0.22 (6 sides) in the planes y ±2.00, a catenary from 0.03 inside the turns
  (x ±5.32, z 6.18, between the two turns) to 4.37 at mid-span, a knot bulge (Ø 0.36) at each hanger; hangers Ø 0.14 (4 sides) from 0.05 inside the knot down to a knot
  foot on the plank top (along the plank's normal, sunk 0.02) with a middle knot at 38 %; diagonals Ø 0.20 from under
  the lower turn's span side to knot feet on the end planks; backstays Ø 0.22 from under the turn's end side to knot
  feet on the stone tops at |x| 7.35; lower rail links Ø 0.18 between the plank sides at mid-height (0.03 into each).
  Knots are rings of the rope itself (`vrope`, a variable-radius twisted tube): a separate knot shell round a rope
  buries the rope inside it.

## Stage 2 — Optimisation and cleanup

kit_verify (`cls="structure"`, walk): **problems []**.
- Tris: hero 5322 / 6000 (turns 1152, rails 928, hangers 720, posts 544, stones 594, cloth 400, planks + pegs 448,
  diagonals + backstays 368, links 168); EndPost 524, Plank 56, MainRope 464, LowerRope 100, HangerRope 60,
  AnchorStone 168 (all < 1000).
- 105 closed shells; 0 non-manifold / bowtie / boundary / wire / loose / zero-area / n-gon / duplicate; 0 winding
  errors, 0 parity-inward, 0 self-hits; floating 0, unchained 0 (13 grounded); buried 0 (deepest 0.072 hanger in
  rail knot, rope-in-rope limit 0.08; cloth in knot 0.046); thin-sheet pierces 0; min corner 2.4° (the cloth wraps'
  ear-clipped caps; floor 0.3°).
- Sizes: hero 17.388 × 8.639 × 7.20, origin bottom centre (offset -0.033, -0.043, 0 from the stones' asymmetric
  facets), transforms applied, no modifiers or custom normals.
- **Walk:** centre path clearance 0.49, side paths (y ±0.3) 0.191 (to the rope turns at the posts), 0 intersecting
  steps, largest rise 0.14 per 0.1 step (riding the plank chain), no overhead headroom limit; turning at mid-span 0.78,
  on the stone top 0.41, 0 intersecting yaws. Clear 3.16 between base blocks, 2.98 between turns, 3.86 between the
  hangers.
- Deck check: stone tops 3.470, end plank edges 3.452, plank tops 3.318 / 3.005 / 2.796 / 2.692 (on the curve).

## Stage 3 — UV

kit_build cleanup (Smart UV, margin 0.008): hero 2155 islands, 0 overlaps, 0 flips, min gap 0.016, border 0.008,
density even, conformal stretch p95 1.022 (parts 1.000–1.059).

## Stage 4 — Materials, colour and texture

Calibrated as M050: the compare renders against the same sheet cells, class medians (wood, rope, red, stone) matched
with per-channel linear ratios (the dome calibration does not see the studio's directional split), then re-measured.

| Class (cell) | Sheet median / lit / dark | Ours median / lit / dark |
| --- | --- | --- |
| Wood (f34) | `#AA5111` / `#E7812C` / `#6D2F08` | `#B15D1A` / `#DF7B2C` / `#9B4512` |
| Wood (front) | `#A54C11` / `#C96619` / `#72300A` | `#A94912` / `#BF621B` / `#9A4210` |
| Rope (front) | `#F4AA34` / `#FDBD3C` / `#E09025` | `#F2A832` / `#FFBB39` / `#AF7A22` |
| Red (f34) | `#BA1E10` / `#E02F19` / `#811008` | `#BB1E12` / `#C21F13` / `#AD1D11` |
| Stone (f34) | `#B9B3AE` / `#C4C4C8` / `#88898C` | `#BAB6B4` / `#D6D0CA` / `#A9A5A3` |
| Stone (front) | `#BDB7B2` / `#C6C3C5` / `#969595` | `#B6B1B0` / `#CEC9C4` / `#9C9999` |

Final keys: wood `#B06825`, wood_light `#E37D2C`, wood_deep `#9C4C15`, wood_dark `#5E2909`, rope `#E2A63B`, rope_dark
`#C98D2C`, peg `#EDB641`, cloth `#AA2216`, cloth_dark `#8A1A10`, stone `#ADAEB1`, stone_mid `#84878F`. By role and
position only: base blocks 25 % toward wood_dark, cap bevel 50 % and top toward wood_light, plank ends 30 % toward
wood_deep, stone faces toward stone_mid by height (45 % in the lowest 30 %, 20 % to 62 %) and in the cleft (35 %), the
chunks 45 %; Tint ±6 % per plank, ±3 % per stone with broad mottling; Tint vs normal worst 0.0.
Recorded (studio lighting): our shaded wood and stone faces are lighter than the sheet's (`#9B4512` / `#6D2F08`), our
stone tops warm-lit (`#D6D0CA` / `#C4C4C8`), the top view's plank tops brighter (`#DC7825` / `#C9691E`). Class shares:
wood 37.0 / 37.5 (f34), red 1.3 / 1.4 (f34), stone 41.7 / 53.7 (f34: the sheet's composition is lower and wider);
rope 15–19 against 5.5–8.6: the sheet's thin ropes lose their shaded strands to the wood and ink classes; the rope
diameters are measured from the front cell (rail 3 px ≈ Ø 0.18, coils 0.48 for two turns) and built at 0.22 / 0.28.

## Stage 5 — Lighting: skipped

The sheet shows no lantern, glow or emissive part. No Studio-side lighting needed.

## Stage 6 — VFX: skipped

No smoke, sparkle or other effect on the sheet; no sockets (export stats: 0 sockets, 0 glow keys).

## Renders and compare

`build(close=True)` writes `M051_views.png` (f34, r34, front, side, rear, top, exploded, scale), `lash_cu.png` and
`hanger_cu.png` (the sheet's close-ups 5 and 6). `m051.compare()` writes the side-by-side sheet to
`<temp>/RBLX-Flintborn/compare/M051/` (cell boxes in `m051.COMPARE`). W : H, sheet / ours: f34 1.852 / 1.634, r34
1.507 / 1.657, front 2.296 / 2.373, side 0.897 / 1.157, rear 1.983 / 2.358 (the sheet's rear is narrower than its own
front), top 2.047 / 2.012.

## Modeller's notes for the verifier and the main session

- Names: hero and the EndPost / Plank / MainRope / HangerRope / AnchorStone parts keep the old names; LowerRope is
  new (the sheet's "Lower Rope Rail"); the old Brace and PegBlock parts are gone with the old design. The previous
  export (`art/roblox/kit/M051/manifest.json`) still lists the old set.
- Candidates for `kit_parts`: `vrope` (an open twisted rope with a radius per path point, so knots are bulges of the
  rope), the U-shaped cloth wrap (`P.ext` of a U outline round a post's end), and the sliver-plane filter in
  `_hull_planes` (a near-collinear hull triangle gave a wrong plane and a chunk buried 0.3 deep).
- Leftover look differences: the f34 camera compromise; open ends; wider across than the side cell; ropes a little
  thicker than the front cell measures; studio shading lighter than the sheet's.

## Main session rulings (2026-11-04)

1. **Stone tops 3.47** (four 0.8675 risers) stand: the sheet draws the anchor stones at about half the model's height,
   and the riser rule still holds.
2. **No rope across the entrances** and the wider post spacing from the top cell stand: both keep the crossing walkable.
3. The removed Brace and PegBlock parts leave the export when the model ships.

## Stage 7 verification (round 1)

**Result: FAIL, 7/10.** One blocker: the red cloth lashing. Technically clean. The rope layout, sag, deck, posts and
stones match the sheet within the rulings and recorded misses.

### Technical

I re-ran everything on a copy of the work file (`wip/M051v.blend`; geometry checked against the current builder with
`deck_check`).
- `kit_verify.run(all 7 objects, cls="structure", walk=m051.WALK)`: **problems []** (2.8 s). Hero 5322 / 6000 tris
  (11 % under), 105 shells. Parts: EndPost 524, Plank 56, MainRope 464, LowerRope 100, HangerRope 60, AnchorStone 168.
  0 non-manifold, bowtie, boundary, wire, loose, zero-area, n-gon or duplicate. 0 winding errors, 0 parity-inward,
  0 self-hits. Floating 0, unchained 0 (13 grounded). Buried 0; deepest 0.072, a hanger in a rail knot (rope-in-rope
  limit 0.08); cloth in knot 0.046. 0 thin-sheet pierces. Min corner 2.42 deg (56 corners under 3 deg; floor 0.3).
  UV: 2155 islands, 0 overlaps, 0 flips, gap 0.016, border 0.008, stretch p95 1.022. Tint against normal: worst 0.0.
  Size 17.388 × 8.639 × 7.20, origin at the bottom centre, transforms applied, no modifiers or custom normals.
  0 sockets. Collision: hero precise; EndPost and AnchorStone hull; Plank box; the three ropes none.
- **Walk:** clearance 0.49 on the centre path and 0.191 on the y ±0.3 paths (to the rope turns at the posts).
  0 intersecting steps. Largest rise 0.139, the proxy footprint stepping across plank edges. Turning room 0.78 at
  mid-span and 0.407 on the stone top, 0 intersecting yaws.
- **Deck** (`m051.deck_check`): stone tops 3.470 ×6; end plank edges 3.452; plank tops 3.318 / 3.005 / 2.796 / 2.692,
  symmetric and equal at y -1.5 / 0 / 1.5; rail low point 4.37. Matches the brief and the rulings.
- **Counts:** 4 stones and 9 chunks; 4 posts with 8 turns, 4 cloth bands, 4 knots and 8 tails; 8 planks and 16 pegs;
  2 rails, 12 hangers, 4 diagonals, 4 backstays, 14 lower-rail links. All as the spec says.
- **Compare** (`m051.compare()` to `<temp>/...`), W : H sheet / ours: f34 1.852 / 1.634, r34 1.507 / 1.657, front
  2.296 / 2.373, side 0.897 / 1.157, rear 1.983 / 2.358, top 2.047 / 2.012. These are the modeller's numbers exactly.
  The side and rear differences are the ruled post spacing and the sheet's narrower rear drawing.

### Views against the sheet

The colour classes are medians from the sheet crop and our render (shares are % of content pixels). The red class
counts only true red; the earlier dark-wood bleed is excluded.

| Cell | Red share | Red median / lit | Rope share | Rope median | Wood median / dark | Stone median / lit |
| --- | --- | --- | --- | --- | --- | --- |
| f34 sheet | 2.1 | `#AD210D` / `#E5331A` | 9.7 | `#EF9134` | `#A14C0F` / `#622907` | `#B7B2AD` / `#C5C5C9` |
| f34 ours | 1.5 | `#BA1F12` / `#C21F13` | 17.3 | `#FFAA33` | `#AF561A` / `#97400F` | `#BBB6B4` / `#DBD6D1` |
| front sheet | 2.1 | `#B32A0D` / `#EA3715` | 10.0 | `#EF9B2F` | `#A14A0F` / `#652908` | `#BDB6B2` / `#CAC5C9` |
| front ours | 1.2 | `#BA1E12` / `#C21F13` | 17.3 | `#F1A632` | `#A94912` / `#933F0F` | `#B6B1B0` / `#D1CCC7` |
| rear sheet | 4.0 | `#B4230E` / `#EB3217` | 10.2 | `#EE992E` | `#A44D10` / `#652A0A` | `#B9B3AF` / `#CAC7C8` |
| rear ours | 1.8 | `#AB1C11` / `#B11C12` | 18.8 | `#E09E32` | `#9F4611` / `#8B3C0E` | `#A2A3A8` / `#B7B7B9` |
| r34 sheet / ours | 1.9 / 2.0 | | 10.9 / 17.7 | `#F09334` / `#E59C32` | `#9B470E` / `#9F5119` | `#B5B0AC` / `#A1A1A5` |
| top sheet / ours | 0 / 0 | | 3.9 / 18.5 | `#D88630` / `#FF992F` | `#CA691D` / `#DA7725` | `#BFB8B4` / `#C7C3C1` |

- **f34 (hero).** The layout matches: near end lower left, far end upper right, two posts per end on faceted stones,
  the sagging rail with knotted hangers, diagonals to the end planks, and backstays to knots on the stone tops. The
  post pairs read stacked on a diagonal and the span reads shorter than the drawing; the drawing fits no single
  camera, so this is the recorded camera compromise and not scored. **The cloth does not read:** see blocker 1.
  Our stones are lofted with many triangulated facets; the sheet's are clean boxy blocks with big chunks at the base
  (minor 3).
- **Front.** Silhouette, post spacing (1.69 H), stone-to-post ratio, the deck sag (0.80 against about 0.8–1.0 on the
  sheet), the rail low point and 6 hangers plus a diagonal per end all match. Ours has a red band on the outer half of
  each post's front face, with no knot and no tail. The sheet draws a knot at each post's outer front edge with a tail
  hanging about a third of the post height.
- **Rear.** Content matches (narrower drawing recorded). Our knot and tails sit at the (end, +Y) corner, so they show
  here, but they are small: red 1.8 % against 4.0 %.
- **r34** (redraw, content only): matches. This is the only view where the red share agrees (2.0 / 1.9).
- **Side.** These differences are ruled or recorded: posts wider apart, no entrance rope, stone tops meeting over a V
  gap where the sheet has an open gap. The sheet also draws stacked timber between the posts above the stone tops;
  ours shows stone there (minor 5). Our stone ends sit in the studio's shade (`#8D8D92` against `#BFB9B4`): studio
  lighting, recorded.
- **Top** (content only): 8 planks, posts at the stone corners, rails and the knot feet all match. Differences:
  - the entrance rope is ruled out;
  - the rope turns read as gold rings round each cap (1.62 across against the 1.26 cap), where the sheet shows plain
    caps;
  - the sheet's timber between each post pair and the short corner braces are not built (minor 5);
  - the sheet's dots at the plank ends are not built.
- **Close-up 5** (`<temp>/.../cu5.png`, az -35 / el 15): the two-turn coils and backstays match. The red is a flat
  band under the coil. The sheet's knotted ribbon, with tails hanging to near the base block, is missing (blocker 1).
- **Close-up 6:** plank chunk, end pegs, hanger knots at the rail, middle knots and knot feet, and the diagonal to the
  end plank all match. The lower rail is invisible here: its links sit 0.35 inside the plank ends, at mid-height in
  0.205 gaps. The sheet shows it plainly between the plank ends (minor 4).
- **Colour.** Wood matches in the front and f34 medians (`#A94912` / `#A14A0F`); the shaded wood is lighter (studio,
  recorded). Stone medians are within about 6 per channel; the lit faces are warmer and lighter (studio). Cloth
  matches at the median but is dull when lit (`#C21F13` against `#E5331A`). The rope is more yellow than the sheet's
  orange-gold (f34 `#FFAA33` against `#EF9134`) and covers about 1.7 times the sheet's share (minor 2).
- **Walk** (eye renders from the stone top and mid-span): the entrance is open and the turns clear the side paths.
  The deck reads as a continuous sagging walk.

### Blockers

1. **The cloth lashing reads as a flat red label, not the sheet's knotted ribbons.**
   - **What's wrong.** Each post has one knot (a 0.22 cube) and two flat tails (0.30 × 0.71 and 0.32 × 0.91), all at
     the (end, +Y) corner. So nothing but the band shows in the hero f34, the front view or close-up 5.
   - **What the sheet shows.** Its cloth is the accent of the post: a knot bunch at a camera-facing corner, with two
     ribbon tails hanging from under the coil to near the base block top (about 1.2–1.5 studs). The front view has
     them at each post's outer front edge; the f34 and close-up 5 on the near faces of all four posts.
   - **Measured.** Red share is 1.2 % against 2.1 % (front), 1.8 % against 4.0 % (rear) and 1.5 % against 2.1 % (f34).
   - **Fix:**
     - Give every post a knot and tails at its (end, -Y) corner as well as the (end, +Y) one, so both long faces carry
       them as in the front and rear cells.
     - Make the knot a bunched lump of about 0.35, not a cube.
     - Lengthen the tails to about 1.2–1.4, down to about z 4.4, just above the base block top at 4.27.
     - Widen the tails to about 0.32–0.36, with a slight outward splay or a twist so they read as ribbons, not plates.
     - Brighten `m051_cloth` a step, toward `#B82418`, so the lit red nears `#E5331A`.
     - Cost: about +250–350 tris, which leaves the hero near 5650 / 6000.
     - Re-run kit_verify: cloth in knot stays at or under 0.05, and the tails must not pierce the base block.

### Minors (record or fix while the cloth is open; none blocks on its own)

1. The f34 camera compromise (az -20 / el 20): recorded, not scored.
2. **Rope weight and hue.** The rope covers 17–19 % of content against the sheet's about 10 % in the front, f34 and
   rear views, and it is more yellow. Two options:
   - thin the rails to Ø 0.18–0.20 (the front cell measures 0.18);
   - shift `m051_rope` slightly toward orange (for example `#E09A36`).
3. **Stones.** The lofted rings, split into triangles, give a busy crumpled facet pattern; the sheet has broad planar
   faces with softened edges. The sheet's base chunks are bigger and stacked: 3–4 on the near-left stone, up to about
   40 % of its height. Ours has 2–3 per stone, and only one per stone is above 0.7 tall (largest 1.40 × 0.65 × 1.25);
   the outer-face chunks are pebbles of about 0.3 × 0.75 × 0.5. Planar facet columns and one or two more block chunks
   per near stone would read closer.
4. **Lower rope rail** nearly invisible (links 0.35 inside the plank ends). Moving them to about |y| 2.20–2.25 would
   show them between the plank ends as on the sheet. The LowerRope part is one continuous rope at mid-plank height,
   so it would run through planks if placed with them. That is fine as a standalone part, but it differs from the
   hero's links.
5. **Timber between the post pairs.** The side and top cells draw timber between each end's post pair, and the top
   cell short braces from the posts to the end planks. The hero shows stone there, so record it as a miss.
6. The plank top dots and board line in the top cell and close-up 6 are not modelled (flat-shaded faces); recorded.
7. The studio shading differences (shaded wood and stone lighter, the side view's stone ends in shade) are recorded,
   not scored.

## Main session after round 1 (2026-11-04)

Fix round, in this order:
1. **Blocker: the cloth reads as knotted ribbons.** Do the verifier's fix:
   - a knot and tails at both end corners of every post;
   - a bunched knot about 0.35;
   - tails 1.2–1.4 long and 0.32–0.36 wide with a slight splay;
   - `m051_cloth` toward `#B82418`.
   Keep the cloth within 0.05 of its knot, with no tail through the base block.
2. **Rope:** rails Ø 0.18–0.20 and `m051_rope` toward `#E09A36`, so the rope share and hue come closer to the sheet.
3. **Lower rail:** move the links out to |y| 2.20–2.25 so they show between the plank ends. Make the LowerRope part a set of
   links that match the hero.
4. **Stones:** broader flat faces, and bigger stacked base chunks (3–4 on the near-left stone, up to about 40 % of its
   height), if the budget allows.

Minors 1, 5, 6 and 7 stay recorded. Round 2 goes to a fresh verifier.

## Fixes after round 1

Fix modeller, 2026-11-04, on the main session's list. Only the builder changed (`m051.py`), then a rebuild.

1. **Cloth: a knotted ribbon at both end corners of every post.**
   - **Knot.** Each post now has a bunched knot at its (end, -Y) **and** (end, +Y) corner, 8 in all (`knot_points`). Each
     is a jittered three-level faceted lump about 0.35 across and 0.30 tall, standing out of the corner. Two anchor
     points sit inside the wrap's 0.05 thickness, either side of the corner. Their chord passes 0.046 inside the wrap's
     outer corner (cloth in knot 0.046, limit 0.05) and stays clear of its inner corner, so no knot edge crosses the
     thin wrap. Colour: `m051_cloth_dark`.
   - **Tails.** Two ribbon tails sit under each knot, side by side on the long face (`TAILS`), 16 in all:
     - they start 0.02 under the knot, lie 0.003 on the wrap, then settle 0.004 off the shaft;
     - the tips stand 0.05 off the shaft at z 4.36 and 4.48 (0.09 and 0.21 over the base block top);
     - the first tail is 0.19 wide and leans 0.03 toward the corner; the second is 0.16 wide and leans 0.08 away from
       it; both widen 6 % at the tip. That is the splay.
     - From the knot centre (z 5.69) to the tips is 1.33 and 1.21.
   - **Planar tails.** Every tail ring is level and at one offset, so every quad is a planar trapezoid. A twisted or
     slanted tip was tried first; its non-planar quads failed the parity-inward check (2 faces per tail).
   - **Tails are 0.19 / 0.16 wide, not 0.32-0.36.** The sheet's front, rear and close-up 5 cells draw two narrow ribbons
     whose pair is about 0.35 wide, hanging from the knot in a V. Measured with 0.34 + 0.32 tails, red covered
     3.9 % of the front view against the sheet's 2.2 %. So the 0.32-0.36 is used as the width of the pair: 0.36
     under the knot, about 0.48 at the tips.
   - **No tails on the end face.** The first try put one tail on the end face and one on the long face at each corner.
     That gave red at 7.3 % in the side view against the sheet's 0.1 %, because the side cell draws no ribbons on
     the end faces. It gave 3.6 % against 2.2 % in the f34. The end face keeps the round-1 wrap and now shows the
     two knots.
   - **Colour.** `m051_cloth` `#AA2216` → `#B82418`, `m051_cloth_dark` `#8A1A10` → `#951B11`.
2. **Rope.**
   - The upper rails are Ø 0.19 (`MAIN_R` 0.11 → 0.095). The knots and the other ropes are unchanged.
   - `m051_rope` `#E2A63B` → `#E09A36`; `m051_rope_dark` `#C98D2C` → `#C78328` (same ratio).
3. **Lower rail.**
   - The links moved out to |y| 2.22 (`LOW_Y`; the hangers stay at 2.00). Each link's outer surface is at 2.31,
     0.04 inside the plank ends, so the links show in the gaps between the plank ends (checked by eye on a close
     render at the deck edge).
   - The LowerRope part is now the hero's seven -Y links (`lower_points`), joined end to end through the plank
     positions into one rope. Each span between two plank faces is exactly a hero link. Kept as one shell so the part
     passes the floating check (seven loose links would float).
4. **Stones.**
   - **Planar faces.** Every ring is now the ground outline with each edge line moved in by its own face's taper
     (`_inset`) and the corners re-intersected. So each side quad is a planar trapezoid, and each facet is one flat
     face from the ground to the chamfer, without the crumpled triangle pattern. The ridges and grooves keep full
     depth up to the chamfer; before, they halved above 2.75.
   - **Colour bands.** These now follow the rings, so no colour break runs across a flat face: 45 % toward
     `stone_mid` below 1.04, 15 % from 1.04 to 2.75 (before: 45 % below 1.04, 20 % to 2.15 by face centre).
   - **Chunks.** The chunks are boxy blocks now: near-vertical sides, a softened shoulder and one broken top corner,
     20 tris each. A chunk listed after a bigger one at the same place comes to rest in front of it (`spur` pushes
     against the stone and the earlier chunks), which gives the stacking.
     - Near-left stone: 4 chunks, the largest 1.70 × 0.80 × 1.40 (40 % of the stone height), with a 0.55 block in
       front of it.
     - Near-right stone: 3 chunks (1.25 tall, with a block in front).
     - Back stones: unchanged.
   - **Footprint.** The chunks widen the footprint from 17.39 × 8.64 to 17.62 × 9.24. The origin offset is now
     (-0.069, -0.341), because the front chunks stand out further than the back ones.

Kept from round 1: the band (U wrap, 0.46 tall), the backstays, and everything not named above.

### Re-measured

- **kit_verify** (`cls="structure"`, walk from stone top to stone top): **problems []**.
  - Tris: hero **5698** / 6000 (stones 360, chunks 220, post bases 112, posts 432, rope turns 1152, wrap 112,
    knots 230, tails 448, diagonals 184, backstays 184, planks 224, pegs 224, rails 928, hangers 720, links 168).
  - Parts: EndPost 618, Plank 56, MainRope 464, LowerRope 108, HangerRope 60, AnchorStone 170 (all < 1000).
  - Shells: 119 closed. 0 non-manifold, bowtie, boundary, wire, loose, zero-area, n-gon or duplicate. 0 winding
    errors, 0 parity-inward, 0 self-hits.
  - Floating 0, unchained 0 (15 grounded). Buried 0; deepest 0.072 (hanger in rail knot, unchanged), cloth in knot
    0.046. 0 thin-sheet pierces. Min corner 2.07°.
  - UV: 2192 islands, 0 overlaps, 0 flips, gap 0.016, border 0.008, stretch p95 1.00. Tint against normal: worst 0.0.
  - Size 17.619 × 9.240 × 7.20, origin at the bottom centre, transforms applied.
- **Walk.**
  - Clearance: centre path 0.453, y ±0.3 paths 0.164 / 0.169 (to the knots; before, 0.191 to the turns).
  - 0 intersecting steps; largest rise 0.139.
  - Turning room: 0.786 at mid-span and 0.349 on the stone top (to a knot), 0 intersecting yaws.
- **Deck** (`deck_check`): unchanged. Stone tops 3.470 ×6; end plank edges 3.452; plank tops 3.318 / 3.005 /
  2.796 / 2.692; rail low point 4.37.
- **Compare** (`m051.compare()` to `<temp>/...`). W : H, sheet / ours:

  | Cell | Sheet | Ours |
  | --- | --- | --- |
  | f34 | 1.852 | 1.625 |
  | r34 | 1.507 | 1.657 |
  | front | 2.296 | 2.410 |
  | rear | 1.983 | 2.379 |
  | top | 2.047 | 1.905 |

  The front, rear and top ratios moved with the wider chunk footprint.
- **Colour classes** (shares in % of content pixels; medians and lit = top-decile luminance, sheet crop / our
  render):

  | Cell | Red share | Red median / lit | Rope share | Rope median |
  | --- | --- | --- | --- | --- |
  | f34 | 2.2 / 3.2 | `#AD210D` `#E93A1D` / `#C92113` `#CE2C17` | 7.1 / 14.0 | `#F39936` / `#FFA231` |
  | front | 2.2 / 2.7 | `#B32A0D` `#EA3D17` / `#CA2013` `#CE2C16` | 8.1 / 12.3 | `#F4A330` / `#FEA32F` |
  | rear | 4.0 / 2.7 | `#B4230E` `#EE3A1C` / `#BB1D12` `#B72B13` | 7.9 / 13.6 | `#F4A330` / `#E6982E` |
  | side | 0.1 / 3.3 | | 5.0 / 3.0 | |

  - **Before this round (verifier):** red front 1.2, rear 1.8, f34 1.5; rope f34 `#FFAA33`.
  - **Red share.** The model is front-back symmetric, so it cannot give both the front's 2.2 and the rear's 4.0. It
    sits between them at 2.7.
  - **f34 red.** The f34 runs high because the posts fill more of our frame: the camera compromise makes the span read
    shorter. The far posts' inner faces also carry knots and tails there.
  - **Side red.** The side view's red is the round-1 wrap across the end faces plus the knots.
  - **Lit cloth.** Lit cloth stays duller than the sheet's (`#CE2C17` against `#E93A1D`): the studio light, recorded.
  - **Rope.** The rope's hue now matches the sheet's orange-gold (front `#FEA32F` / `#F4A330`). Its share is still
    about 1.6× the sheet's: the sheet's thin ropes lose their shaded strands to the ink and wood classes.
  - **Wood and stone.** Wood medians: f34 `#B25E1B` / `#A64F10`, front `#A94F16` / `#A34D10`. Stone medians: f34
    `#BDB9B7` / `#BAB4AF`, front `#B5B1AF` / `#BDB7B2`.
- **Renders.**
  - `build(close=True)` was rendered into the scratch folder and copied into this folder. In this session, Blender's
    render saves straight into the repo folder failed now and then with "cannot save" (a file lock). A plain copy
    over the same files worked.
  - The close-ups `lash_cu.png` / `hanger_cu.png` show the knot with its two splayed tails on the near faces, and the
    lower-rail links between the plank ends.

### Left for the verifier

- The knots stand at the end corners, as the fix list asks. The sheet's front and rear cells place the knot about a
  third of the way in from the outer edge of the long face.
- The side cell shows no red; ours shows the end-face wrap and two knots per post (wrap from round 1, kept).
- Minors 1, 5, 6 and 7 stay recorded (main session).

## Stage 7 verification (round 2)

**Result: PASS, 8/10.** Round 1's blocker is fixed: each post now shows a red knot with two ribbon tails on its
camera-facing long faces in the front, f34 and close-up views. The rope, lower-rail and stone fixes all landed, and
they brought no new problem. Technically clean. Nothing left is a blocker; the minors below are recorded.

### Technical

I re-ran the checks in my own background session, on a copy of the work file (`wip/M051v.blend`, saved after the
builder's last change). I did not rebuild or save.
- `kit_verify.run(all 7 objects, cls="structure", walk=m051.WALK)`: **problems []** (17.4 s; 10.3 s of it UV).
  - Hero 5698 / 6000 tris (5 % under), 119 shells: stones 360, chunks 220 (11), post bases 112, posts 432, turns
    1152, cloth wrap 112, knots 230 (8), tails 448 (16), diagonals 184, backstays 184, planks 224, pegs 224, rails
    928, hangers 720, links 168.
  - Parts: EndPost 618, Plank 56, MainRope 464, LowerRope 108, HangerRope 60, AnchorStone 170.
  - 0 non-manifold, bowtie, boundary, wire, loose, zero-area, n-gon or duplicate. Normals outward. 0 winding errors,
    0 parity-inward, 0 self-hits, 0 negative volumes, 0 shells unmatched to the register.
  - Floating 0, unchained 0 (15 grounded). Buried 0. Deepest 0.072, a hanger in a rail knot (rope-in-rope limit 0.08);
    rail in turn 0.052; cloth band in knot 0.046. 28 thin cloth shells, 0 pierces. Min corner 2.07° (63 corners
    under 3°; floor 0.3°).
  - UV: 2192 islands, 0 overlaps, 0 flips, gap 0.016, border 0.008, stretch p95 1.00. Tint against normal: worst 0.0.
  - Size 17.619 × 9.240 × 7.20; origin at the bottom centre (stored offset -0.069, -0.341, 0); transforms applied; no
    modifiers or custom normals. 0 sockets, 0 glow keys. Collision: hero precise; EndPost and AnchorStone hull; Plank
    box; MainRope, LowerRope and HangerRope none.
- **Walk** from stone top to stone top: clearance 0.453 on the centre path and 0.164 / 0.169 on the y ±0.3 paths
  (nearest: a cloth knot). 0 intersecting steps. Turning room 0.786 at mid-span and 0.349 on the stone top, 0
  intersecting yaws.
- **Deck** (`m051.deck_check`): stone tops 3.470 ×6, end plank edges 3.452, plank tops 3.318 / 3.005 / 2.796 /
  2.692 (equal at y -1.5 / 0 / 1.5), rail low point 4.37. No problems.
- **Compare** (`m051.compare()` to `<temp>/...`). W : H, sheet / ours: f34 1.852 / 1.625, r34 1.507 / 1.657, front
  2.296 / 2.410, side 0.897 / 1.234, rear 1.983 / 2.379, top 2.047 / 1.905.
  - These match the modeller's numbers.
  - The side ratio isn't in the modeller's table. It grew from 1.157 because the new chunks stand out past the stones.

### Blocker check (round 1 blocker 1: the cloth)

- **Close-up 5** (az -35 / el 15, my render). Both near posts show a dark-red bunched knot at the outer corner under
  the lower turn. Two narrow ribbons hang from it in a slight V, down to just above the base block. This reads as the
  sheet's knotted ribbon, not a label.
- **Front.** Each post has a knot at its outer front edge and two tails down the outer part of the front face, as the
  sheet draws them. Red share is 2.7 % against the sheet's 1.7 %.
- **f34 (hero).** The near posts carry the knot and tails on their camera-facing long faces. The far posts show them on
  the faces turned toward the camera. Red is 3.1 % against 2.2 %. The sheet's f34 has the same layout: bunches at the
  corners under the coil, with ribbons down to about mid-post.
- **Rear and r34.** The same on the +Y faces. Rear red is 2.7 % against 3.7 %; r34 is 3.1 % against 1.8 %.
- **Kit_verify.** The cloth band sits 0.046 inside the knots (limit 0.05). No tail goes into the base block: the tips
  are 0.09–0.21 above it. No thin cloth shell is pierced.
- **Fixed.**

The other fix-list items:
- **Rope.** The rails are Ø 0.19 and the hue moved to orange-gold. The front rope median is `#FCA22F` against the
  sheet's `#EB972A`, and the f34 is `#FE9D2F` against `#ED8D2D`. Rope share, by my classifier: front 13.8 against
  12.3, f34 17.1 against 12.8, rear 16.2 against 12.1. That is close in the front; in the f34 and rear it is still
  about 1.3× the sheet's.
- **Lower rail.** At |y| 2.22 the links show as short gold rope pieces in the gaps between the plank ends, at
  mid-height. I checked this at close-up 6's angle and at a low front angle. They read thinner and more broken up than
  the sheet's continuous rail, but they are there.
- **Stones.**
  - Each facet is now one planar face from the ground to the chamfer: broad faces with vertical ridge and groove
    columns, and no crumpled triangles.
  - The near-left stone carries 4 boxy chunks stacked in front of its outer face, the largest about 40 % of the stone
    height. The near-right stone carries 3.
  - These read close to the sheet's chunky base blocks.
- **Nothing new broke.** I checked the post, deck and stone close-ups and every compare pair. The knots stay clear of
  the backstays and diagonals, the walk paths and turning room still clear, and no shell floats or is buried.

### Views against the sheet

Colour classes are medians from the sheet crop and our compare render: share % / median / top-decile lit /
bottom-decile dark.

| Cell | Red | Rope | Wood | Stone |
| --- | --- | --- | --- | --- |
| f34 sheet | 2.2 `#B4210F` `#EA3D1F` | 12.8 `#ED8D2D` | 29.6 `#97450F` / dark `#592205` | 50.7 `#B7B1AD` / lit `#C5C6C9` |
| f34 ours | 3.1 `#C92113` `#D22C16` | 17.1 `#FE9D2F` | 31.2 `#AF551A` / dark `#923F0F` | 42.4 `#BFBBB7` / lit `#DDD9D5` |
| front sheet | 1.7 `#C02C0F` `#ED461F` | 12.3 `#EB972A` | 25.5 `#9B470F` / dark `#5C2206` | 52.8 `#BCB6B1` / lit `#CCC7C9` |
| front ours | 2.7 `#CA2013` `#D22915` | 13.8 `#FCA22F` | 24.1 `#A94912` / dark `#843E0F` | 48.0 `#B5B1AF` / lit `#D2CDC7` |
| rear sheet | 3.7 `#BB240F` `#EF3D21` | 12.1 `#EB9529` | 23.7 `#9D4810` | 52.0 `#B9B3AF` |
| rear ours | 2.7 `#BB1D12` `#B92A13` | 16.2 `#E3972E` | 23.8 `#9F4611` | 48.8 `#A6A6A9` |
| r34 sheet / ours | 1.8 / 3.1 | 14.6 / 16.7 | `#8E400E` / `#9F4E18` | `#B4AFAB` / `#A2A3A8` |
| side sheet / ours | 0.0 / 3.7 | 10.4 / 4.4 | `#A54F12` / `#80360C` | `#BFB9B4` / `#8D8E92` |
| top sheet / ours | 0.0 / 0.1 | 8.8 / 43.4 | 49.5 `#C9681E` / 6.2 `#B8601F` | `#BFB9B5` / `#C3C0BE` |

The top row's rope and wood split is a classifier artefact. Our lit plank tops fall just over the 27° hue line into
the rope class. The recorded difference is real, though: our plank tops are brighter and more orange in the top view.

- **f34 (hero).** The layout matches:
  - near end lower left, far end upper right;
  - two posts per end on faceted stones, with two-turn coils and the red knots and ribbons;
  - the sagging rail with knotted hangers, diagonals to the end planks, and backstays to the stone tops;
  - stacked chunks at the near stones' feet.

  The post pairs stand on a diagonal and the span reads shorter than in the drawing. That is the recorded camera
  compromise (minor 1).
- **Front.** These match: the silhouette, post spacing, stone-to-post ratio, the deck sag, the rail low point, 6
  hangers plus a diagonal per end, and the cloth at each post's outer front edge. The sheet's base chunks sit
  centred under each stone's front face. Ours sit toward each stone's outer side.
- **Rear.** Content matches. The sheet's narrower drawing is recorded. Our wood and stone are a shade darker here
  (studio).
- **r34** (a redraw, judged on content only): matches.
- **Side.** The ruled and recorded differences remain: the wider post spacing, no entrance rope, and stone tops that
  meet over a V gap. The sheet draws stacked timber between the posts; ours has none (minor 5, recorded). New since
  round 1, all minor:
  - the knots and the end-face wrap show red (3.7 % against the sheet's 0.0 %);
  - the chunks widen the outline (W : H 1.234 against 0.897).

  Our end faces sit in the studio's shade (stone `#8D8E92` against `#BFB9B4`): studio lighting, recorded.
- **Top** (content only): these match: 8 planks, posts at the stone corners, the rails with their knots, and the knot
  feet. The differences:
  - the chunks now poke out past the stone outlines as separate grey blocks, where the sheet draws clean rounded
    rectangles;
  - the coil rings read round each cap;
  - the timber between the post pairs and the plank-end dots are missing (recorded).
- **Close-up 5:** the coils, the backstays with knot feet and the red knot with its ribbons all match. The sheet's
  bunch wraps more of the front face; ours sits at the corner. The modeller noted this, and it reads.
- **Close-up 6:** these match: the plank blocks, end pegs, hanger knots at the rail, middle knots, knot feet, the
  diagonal to the end plank, and now the lower-rail links between the plank ends.
- **Colour.**
  - Wood medians match the hue. Ours is a little lighter: rear within 3 per channel, front within 14, f34 within 24
    (`#AF551A` against `#97450F`). The shaded wood is lighter than the sheet's ink-dark shading (studio, recorded).
  - Stone medians match within about 8 per channel in the front and f34. The lit stone is warmer and lighter (studio).
  - The cloth median is a little brighter than the sheet's; the lit cloth is duller (`#D22C16` against `#EA3D1F`;
    studio, recorded).
  - The rope hue now matches the sheet's orange-gold, a little brighter.

### Blockers

None.

### Minors (record; none blocks)

1. The f34 camera compromise (az -20 / el 20): recorded, not scored.
2. **Rope share.** Still about 1.3× the sheet's in the f34 and rear (17.1 / 12.8, 16.2 / 12.1); close in the front
   (13.8 / 12.3). The thickest ropes left are the coil turns (Ø 0.28) and the backstays (Ø 0.22). If the model is opened again,
   thin them to about 0.24 and 0.19.
3. **Side view red.** The end-face wrap and the knots show red (3.7 %) where the side cell draws none. If the model is
   opened again, end the wrap at the corners: that leaves only the knots' edges in this view.
4. **Chunk footprint.** The front chunks stand out past the stone outline: the top view shows them as separate blocks,
   and the side W : H grew to 1.234. In the front view they sit toward each stone's outer side, where the sheet centres
   them under the face. Pulling the outermost two or three chunks in by about 0.2–0.3 would tidy the top outline.
5. **Lower rail.** The links show, but as short broken pieces. The sheet's rail reads as one continuous rope past the
   plank ends. Recorded.
6. Timber between the post pairs and the top cell's corner braces are not built (round 1 minor 5, recorded).
7. Plank-top dots and board lines are not modelled; the top view's plank tops are brighter than the sheet's
   (recorded).
8. Studio shading differences (shaded wood and stone lighter, the side and rear faces in shade, lit cloth duller) are
   recorded, not scored.
