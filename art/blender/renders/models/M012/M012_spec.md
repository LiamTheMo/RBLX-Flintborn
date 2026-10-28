# 012 Amber — spec

Being remade from scratch at the user's request (2026-10-28). The user's verdict: "the amber still also needs major work. it's texture and coloring is completely off and the wood near it is also terribly made." Colours must match the master and blend into their neighbours, and every colour and texture must be made and applied.

Reference: `art/blender/assets/references/012.png` (AMBER, page 12; 1024 × 1536 px). Builder: `art/blender/kit/mcp/m012.py` → `build()`. It is rewritten from scratch; the old `beam()` and `nodule()` are not reused.

Assets (collection `Kit/M012 Amber`). The names are kept from the first build; the R03 kit sheet owns `AmberNodule`.

- `Amber`: the hero.
- `AmberCrystalMain`: Amber Nodule (Main Crystal).
- `AmberWoodFront`: Wood Base (Front).
- `AmberWoodBack`: Wood Base (Rear), plus the unlabelled centre seat (see §3.4).
- `AmberWoodLeft`: Side Wood (Left).
- `AmberWoodRight`: Side Wood (Right).

All pixel boxes below are in sheet pixels `(x0, y0, x1, y1)`, top-left origin. All measurements come from the sheet's own pixels: extents were measured with an amber mask (sat > 0.6, val > 0.6, hue < 61°) and a wood mask (0.2 < sat < 0.75, val < 0.85, hue 5–43°, not amber).

## Study (2a), for the remake

### 1. Classification, size and scale

- **Classification:** full asset (resource node). Hero budget 4000 tris; each part 1000.
- **Target size:** about **9.0 W × 7.2 D × 7.0 H studs**, about 1.3× the 5.5-stud character. The old build was 9.2 × 7.8 × 6.9, and that scale was not criticised. Tolerances: W ±0.4, D ±0.5, H ±0.3.
- **Measured view ratios.** The orthographic views are slightly perspective, and the "Front" view is turned a little to the left, like a gentle three-quarter.

| View (box) | W : H | What dominates the outline |
| --- | --- | --- |
| Front (20,525,245,700) | 1.27 | nodule (0.59 of the width, slightly right of centre), low beams across the front |
| Side right (250,525,440,700) | 0.94 (D:H) | tall planks at the back, nodule leaning forward at the front |
| Rear (445,525,640,700) | 1.07 | tall planks, nodule showing upper-left |
| Side left (645,525,825,700) | 0.95 (D:H) | tall planks at the back, nodule at the front |
| Top (830,525,1010,700) | 0.97 (footprint, near square) | nodule round-oval, about 0.65 of the width, in a ring of wood |

- **The top view conflicts with the side views:** the top view gives a square footprint, the side views a depth of about 0.95 H. D ≈ 7.2 is the compromise. Record which one wins.
- **Amber share of the silhouette.** This is a quick check for the verifier: amber pixels ÷ (amber + wood) pixels.

| View | Front 3/4 | Front | Top | Rear 3/4 | Rear | Side R | Side L |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Amber share | 41 % | 42 % | 42 % | 21 % | 21 % | 17 % | 13 % |

- **Reading:** from the front and from above, it is a big amber egg resting in a low nest of wood. From behind and from the sides, it is a stack of tall leaning planks with the amber peeking over and beside them. **Low front, tall back.**

### 2. Silhouette and proportions (per view)

All heights are fractions of the total height H; all widths are fractions of the total width W.

**Front three-quarter (hero, governs):** box (205,110,620,450).
- The nodule's top is the model's top. The nodule spans 0.58 W.
- Its visible amber stops 0.24 H above the ground. The lower quarter is hidden behind the front beam and the seat.
- A long split beam lies diagonally across the front. Its left end is raised (top about 0.49 H) on a chunky front-left block (about 0.33 H tall); its right end comes down to the ground at the front-right (top about 0.25 H).
- At the left: an upright post with a shorter plank behind it. The post's top is at 0.77 H, and it leans slightly outward.
- At the right: two upright planks, tops at about 0.45 H and 0.57 H, leaning slightly outward.
- A small block wedges in between the nodule and the beam, left of centre. This is the end of the centre seat.

**Front view:**
- W:H 1.27. The nodule is 0.59 W wide; its centre is +0.05 W right of the model's centre.
- Left post 0.77 H; right planks 0.57 H.
- The beam's front face is about 0.2 H tall.

**Side right and side left:**
- D:H 0.94–0.95.
- The nodule takes the front 45 % of the depth and leans forward (top towards the front) by about 12–15°.
- Two tall planks rise at the back, tops at 0.96 H and 0.94 H in these views, with a broad shorter slab (top 0.56 H) standing in front of them.
- A low block (top about 0.32 H) sits at the front foot.

**Rear three-quarter (630,110,1005,450) and rear view:**
- The tallest plank reaches 0.94–0.96 H and the second 0.83 H. A broad slab in front of them reaches 0.62–0.75 H; it is the biggest single wood face on the sheet.
- At the other side: a short upright (0.59 H) over lying blocks (tops about 0.32 H).
- The nodule shows over the lower wood on one side, about 40 % of it visible.

**Top view:**
- The nodule is an oval of about 0.65 W, set towards the front-right.
- Wood rings about 70 % of its perimeter: two long diagonal planks across the back-left, blocks down the left, and blocks at the right and front-right.
- The front-centre is open.

**Underside (Detail C):** a broad, dead-flat base made of the coplanar bottoms of three or four big blocks, with the beam resting above them. "Flat base for stable placement."

**The tilt of the nodule:**
- In the front view, the front three-quarter and the rear view, the egg's top sits towards −X of its belly.
- In both side views it leans towards the front.
- So the long axis tilts about **8° towards −X and 12° towards −Y** (top front-left).

**Resolving the view conflicts.** WorldModeling §1.1: the hero view governs.
- The side and rear views show the back planks a little taller than the nodule; the front views show nothing behind the nodule's top.
- Resolution: the tallest plank's top sits at **0.90–0.93 H**, directly behind the nodule's upper back, inside the nodule's front-view outline. From the front it stays hidden; from the side and back it reads as nearly level with the nodule's top.
- The rear view and the rear three-quarter disagree on which side the tall planks stand. Pick the layout below, and record it.

### 3. Parts (exploded view, box (15,730,670,1495))

Five labelled parts and one unlabelled seat. Every wood piece on the sheet is **split timber**: long boards and blocks with roughly **rectangular cross-sections**. None is a round log or a pentagonal pillar.

Every piece shares the same features:
- **chamfered long edges**, a narrow bevel that catches a bright tan line;
- **broad, gently broken long faces**, with facets running along the grain;
- **deliberate angled end cuts**, many with a chamfered rim;
- often **two boards fused side by side**, with a V groove between them and their ends staggered.

The arrows show the assembly:
- the nodule drops into the centre seat;
- Side Wood (Left) drops onto the left end of the front base;
- Side Wood (Right) drops behind the rear block.

#### 3.1 Amber Nodule (main crystal): box (240,772,476,1073)

- **Shape:** a chunky faceted egg.
  - Width : height 0.78–0.80; depth : width about 0.88.
  - In the hero: about **5.3 W × 4.6 D × 6.7 H**.
  - The top end is a little narrower (a smaller cap) and the bottom broad and blunt.
  - The widest point is at 45–55 % of the height from the bottom.
- **Facets: about 36–44 broad flat polygons in all.** About 18–22 show on one side. They are gem-like rows of kites, pentagons and trapezoids, not a geodesic ball of small triangles.
  - **Crown:** a short ridge or small cap at the top (2–3 facets).
  - **Upper ring:** 6 kite or pentagon facets.
  - **Belt at the widest point:** 6–7 big facets, the largest on the stone. The central front facet spans about 1/3 of the width.
  - **Lower ring:** 6 tall trapezoids narrowing downwards.
  - **Bottom:** a broad blunt cap, hidden in the seat.
  - Edges meet in Y-junctions of 3 (some 4); each facet is 1.2–2.2 studs across.
- **Suggested construction.** Convex hull of staggered rings, then `bmesh.ops.dissolve_limit` at 3–5° to merge coplanar hull triangles into broad facets, then BEAUTY triangulation. Check that the merged polygon count lands at 36–44.

| Ring | Height (fraction of the nodule's height) | Points | Radius (fraction of the half-width) | Offset |
| --- | --- | --- | --- | --- |
| Top cap | 0.97 | 2–3 | — | — |
| A | 0.85 | 6 | 0.55 | — |
| B | 0.64 | 7 | 0.93 | half a step |
| C | 0.42 | 7 | 1.0 | aligned with B, so the belt has planar trapezoids |
| D | 0.18 | 6 | 0.78 | — |
| Bottom | 0.02 | 3–4 | 0.4 | — |

  - Jitter each ring ±6 % of its radius in broad sectors, never per vertex in a noisy way.
- **The seat.** It sits sunk into the centre seat; its bottom is about 0.3 above the ground and 0.4–0.5 into the seat's V.
  - The visible amber starts about 0.24 H up at the front.
  - About 25 % of the nodule's height is hidden at the front and about 60 % of its back half (behind the tall planks).
  - The joint is "clean" (Detail B): wood simply overlaps amber, with no gap and no fillet. Boolean-union the hero as in M011.

#### 3.2 Wood Base (Front): box (40,1200,480,1470)

- **Main beam:** one long split beam, about **7.6 long × 1.7 wide × 1.4 tall** (length ≈ 4.5× width).
  - It is **two boards fused side by side** (each about 0.85 × 1.4). A V groove runs the full length along the top, and the far end shows two separate end faces staggered about 0.4 apart.
  - The end faces are cut obliquely (20–35° off square). Each is a broad face broken into 2–3 planar facets, with a chamfered rim.
- **Stub block** at its left end: a squat block of about **2.0 × 1.6 × 1.7 tall**, lying beside and under the beam's left end. In the hero this is the chunky front-left lump (about 0.33 H).
- **Placement in the hero:** across the front, turned about 15–20° in plan (left end further back).
  - The left end rests on the stub block, raised about 1.2.
  - The right end is on the ground at the front-right.
  - Slope about 10°.

#### 3.3 Wood Base (Rear): box (410,1240,620,1365)

- **The block:** one chunky block of about **3.0 long × 1.8 wide × 1.5 tall**.
  - Split vertically at one end into two halves, with a deep V notch about 1/3 of the length.
  - Stepped, chamfered end cuts.
- **Placement:** at the back-right, under the foot of Side Wood (Right).
- In the assembled views this is the lying block under the tall planks at the back.

#### 3.4 Centre seat (unlabelled): box (265,1105,505,1290)

- **Two boards stacked as a cradle:**
  - a front block of about 3.6 × 1.7 × 1.4;
  - a back block of about 3.4 × 1.4 × 1.4 lying behind and about 0.3 higher, offset along its length.
- A chamfered groove runs between them, and their tops make a shallow V seat.
- The nodule's arrows point straight into it.
- **Recommendation:** build it with its own function (`wood_seat`) and include it in `AmberWoodBack`. The sheet names only five parts, and the Rear leader line is ambiguous. In the exploded render, show it as its own floating group under the nodule, as the sheet does.
- In the hero it is mostly hidden. Its ends show as the small block wedged beside the nodule's lower left (front three-quarter) and from the top.

#### 3.5 Side Wood (Left): box (40,930,290,1230)

Four pieces, five boards.

- **Upright post:**
  - about **1.0 × 1.0 × 5.4 tall** (top 0.77 H), square section, chamfered corners;
  - the top is a blunt four-sided chamfer to a small flat top, like a hewn post end;
  - in the hero it stands at the left of the nodule and leans 8–10° outward (−X).
- **Thin plank behind it:**
  - about 0.55 × 1.1 × 4.0 (top about 0.57 H);
  - its top is cut at an angle;
  - it stands behind-left and is partly hidden.
- **Lying split slab** at their foot:
  - about **2.8 long × 1.6 × 1.2**, two boards with a lengthwise groove and staggered ends;
  - lying diagonally at the front-left, under or beside the front beam's raised end.
- **Lying square block** behind the post:
  - about 2.2 × 1.0 × 1.0;
  - lying diagonally back towards the nodule (it fills the gap between the post and the seat).

#### 3.6 Side Wood (Right): box (470,950,650,1230)

Three planks in a leaning tepee.

- **Tall central plank:**
  - about **1.4 wide × 0.85 thick × 6.4 long** (top 0.90–0.93 H);
  - the top tapers to about 60 % of its width, with two sloped chisel faces and a narrow flat top;
  - stands at the back-right, behind the nodule's right shoulder, leaning 5° in towards the nodule.
- **Partner plank** fused alongside:
  - about 1.1 × 0.85 × 5.4 (top about 0.8 H);
  - its top is cut squarer, with a chamfer.
- **Shorter plank** leaning out about 25° from vertical:
  - about 1.6 wide × 0.9 × 4.0;
  - this is the broad slab that shows beside the nodule's right side in the front views (0.45–0.57 H) and as the big front slab in the side and rear views.
- **Bottoms:** flat cuts at the ground.

#### 3.7 Suggested layout (build frame, front −Y, ground z 0; starting values, tune against the views)

| Piece | Centre (x, y) | Notes |
| --- | --- | --- |
| Nodule | (+0.4, −0.2) | bottom z 0.3; tilt 8° to −X and 12° to −Y |
| Seat front block | (+0.3, −0.7) | length along X |
| Seat back block | (+0.2, +0.9) | top about 1.7 |
| Front beam | from (−4.0, −2.0) to (+3.8, −3.2) | left end on the stub block at (−3.4, −2.7) |
| Side Left | x −3.9 … −2.4, y −0.4 … +1.8 | post at (−3.2, +0.3) |
| Side Right | x +2.2 … +3.9, y +0.6 … +3.0 | tall plank at (+2.0, +2.2); the leaning slab towards the right, about (+3.4, +0.6) |
| Rear block | (+1.6, +2.9) | under Side Right's foot |
| Short rear plank | around (−0.8, +2.6) | optional: Side Left's thin plank may move here if the rear views need a second tall plank on that side |

### 4. Wood: how to make it read as weathered split timber

What the sheet's wood is (Detail B and the exploded close-ups):

- **Cross-section:** a rectangle of about 1 : 0.6–1, with all four long edges **chamfered**, so each board is a 6–8-sided prism.
  - Chamfer width about 10 % of the board width (0.10–0.18 studs).
  - The chamfers catch the light as bright tan lines along every long edge; the sheet's "amber-bright" pixels inside wood boxes are exactly these lines.
- **Long faces:** "broad planar faces", but each long face is **broken along the grain** into 2–4 long, narrow planar facets at slight angles, like an axe-split or hewn face.
  - The facets run the length of the board. They are never random triangles across it.
- **Grain:** darker streaks run lengthwise down the faces (Detail B upright), and the board's facet breaks follow them.
- **Splits:** two boards fused side by side with a deep V groove between them, ends staggered 0.3–0.6. Used on the front beam, the rear block, the side-left slab and the seat pair.
- **End cuts:** angled planar ends (10–35° off square) with a chamfered rim. Some show a step where one board of a pair is longer.
  - Upright tops are chisel- or pyramid-chamfered.
  - **No jagged splinter teeth and no random hull jitter at the ends.** The sheet's ends are clean, deliberate cuts.
- **Proportions:** boards are long, at least 2.5–5× their thickness. Blocks are chunky (about 2× long). Everything is thick and heavy; no thin sticks or spikes.

**Construction recipe** (WorldModeling §6.3 and §13.1, adapted to split timber):

- Each board is a lofted prism: a chamfered rectangle (8 points) placed at **4–6 stations** along its axis, about 1.2–1.6 apart.
- Each station gets a small perpendicular offset (±0.04–0.08) and a small twist (±3°), so every long face breaks into long planar facets along the grain.
- The end stations are cut by the end plane, with the chamfer ring kept.
- Splitting the chamfer strips at the stations keeps their triangles above 5° (a 0.15-wide strip over a 1.5-long segment is about 5.7°). Unsplit full-length strips would fail stage 2's thin-face check (about 1.4°).
- Fused boards: build two prisms, overlap them by about 0.1, and union them. The meeting chamfers form the V groove.
- Each piece rests on something: the ground, another piece or the nodule. Nothing floats.

**What made the old wood look "terrible"** (the old `M012_views.png`, `beam()`):

- **One primitive for everything.** Every piece was a convex hull of two jittered pentagons, so each read as a smooth, tapered pentagonal log or pillar. There were no chamfers, no flat sides, no split boards and no grooves.
- **The ends were hull caps of jittered points:** small random slanted triangles, not cuts.
- **The uprights tapered to half width,** so they read as spikes or chimneys (rear and side tiles).
- **The groups were wrong.** Single beams stood where the sheet has groups of 2–4 boards. The front read as two clean stacked lumber logs, a "lumber pile". There was an invented extra "Rear" group of smooth pillars, and the side-left lying slabs and the right-hand tepee were missing.
- **Pieces floated or stuck out** (an exploded render with floating stubs; a dark beam end jutting from the side view).
- **Colour.** The front wood rendered too light and orange: median #B8754C against the sheet's #754B31. The rear, side and underside wood went chocolate: #664029, #583723 and #4C2E1C, against the sheet's #7A4F34, #905B3B and #6A452E. The sheet's wood stays a moderate mid brown from every angle.
  - The light and dark keys were random noise patches (#9C6845 / #84563A), not grain streaks or worn edges.

### 5. Amber: shape and how its colour works on the sheet

**Shape:** see §3.1. It is a cut-gem egg with broad facets.

**Colour regions.** There are no neutral-white highlights anywhere. The bright body tones are saturated yellow (p95 #FEDB46); only the thin seams and vertex glints reach a pale yellow (#FFFCAC). A grid of medians over the exploded nodule (5 columns × 6 rows, top row first) shows the pattern:

```
#F78E46 #FC8322 #FEB735 #FEC343    --
#F7863E #FD8122 #FEC934 #FED242 #FDBC35
#EB6A1E #FD931E #FDA829 #FD8220 #FE992C
#E98526 #E16211 #FD8715 #FE8B1E #FC791C
#DF7210 #E26B0E #EB8711 #FD9512 #EE6314
  --    #D06319 #D15D0C #D85C0F #EA6115
```

- **Light (yellow) core:** the upper-centre to upper-right facets, about the top 40 % and centre-right. The light region is not on the lit (left) side, so it is painted, not lighting.
- **Mid orange:** most of the belt and the right flank.
- **Dark orange:** the bottom row and the lower-left flank.
- The front three-quarter and front view show the same pattern: yellow in the upper centre-right; orange to darker red-orange at the lower left and at the bottom by the wood.
- **Shares of amber pixels by hue** (consistent across views):

| Hue band | Exploded | Front 3/4 | Rear 3/4 | Detail A | Target share |
| --- | --- | --- | --- | --- | --- |
| Yellow (≥ 36°) | 21 % | 26 % | 33 % | 40 % | light ≈ 25 % |
| Light orange (27–36°) | 36 % | 35 % | 35 % | 25 % | light–mid mixes ≈ 35 % |
| Orange (21–27°) | 36 % | 35 % | 28 % | 35 % | mid ≈ 30 % |
| Red-orange (< 21°) | 8 % | 4 % | 4 % | 1 % | dark ≈ 10 % |

**Blending facet to facet.**
- Neighbouring facets step through in-between tones: yellow → yellow-orange → orange → deep orange. There are never isolated yellow triangles in a field of orange.
- Each facet is one main tone ("simple solid colour regions", Detail A) with **angular darker inclusions** inside it: soft-edged darker-orange shapes covering about 15–20 % of a facet's area (most visible in the belt facets).
- **Bright seams:** thin, bright yellow lines run along the facet edges, and small star-like glints (pale yellow, #FFFCAC) sit at a few upper vertices. This is the sheet's "inner glow" cue. Glint positions:
  - exploded nodule: (347,831), (343,906), (412,877);
  - front three-quarter: (446,174), (467,209), (517,268), all on the upper-centre-right facets;
  - Detail A: (804,874).
- **Don't model the seams.** Hairline bevel strips would break stage 2's thin-face rule. The seams read from the contrast between light and mid neighbours, plus the stage 6 glints.

**The amber stays bright from every angle.**
- Rear three-quarter nodule: median #FD901B, light quartile #FEC435.
- Side right: median #FB861D.
- The shade quartile is still a saturated #C95D0D. Its luminance is about 0.6 of the lit quartile; the wood's is about 0.46. So it reads translucent and lightly self-lit.
- The old build's rear and side amber went dull brick (#C0531A, #B75121). That is the main reason it read "completely off", along with the near-white facets and white glints from roughness 0.3.

**Surface finish:** smooth and glossy-looking but without white speculars. Use roughness about 0.45 and low specular, so the studio sun never washes a facet to cream or white. No transparency.

### 6. Colour plan for stage 4

**Swatches** (flat `M.raw_sample` medians):

| Swatch | Box | Hex |
| --- | --- | --- |
| Amber Light | (32,218,70,255) | #FECD64 |
| Amber Mid | (32,275,70,312) | #FE7719 |
| Amber Dark | (32,332,70,368) | #D25117 |
| Wood | (32,390,70,426) | #8E5E3D |

**Rendered regions to sample.** These are pre-measured here with the masks above. Re-sample with `K.sample(..., "vivid")` for the amber; for the wood use `"brown"`, but only on the pure-wood boxes, because `brown` and `vivid` both catch the other material.

| Region | Box | Median | Lit (top 25 %) | Shade (low 25 %) |
| --- | --- | --- | --- | --- |
| Amber, exploded nodule (all) | (240,772,476,1073) | #FD861D | #FEC538 | #DC6010 |
| Amber, exploded upper third | (240,772,476,872) | #FDAA33 | #FED340 | #FC7B21 |
| Amber, exploded middle third | (240,872,476,972) | #FD881E | #FEA92C | #E06312 |
| Amber, exploded lower third | (240,972,476,1073) | #E46A0F | #FD9713 | #D0570D |
| Amber, front 3/4 upper-centre yellow | (395,150,485,240) | #FEC025 | #FED138 | #FC8019 |
| Amber, front 3/4 left-mid facets | (320,205,385,275) | #E1630D | #EA8114 | #D65A0E |
| Amber, front 3/4 all | (240,120,560,370) | #FB8113 | #FEC029 | #C95D0D |
| Amber, rear 3/4 | (716,120,895,325) | #FD901B | #FEC435 | #C95C07 |
| Amber, Detail A | (690,765,915,950) | #FD9924 | #FED843 | #F37317 |
| Wood, front 3/4 front beam | (300,330,500,420) | #72492F | #B2774F | #54341F |
| Wood, front 3/4 all | (205,110,620,450) | #754B31 | #B4784F | #573621 |
| Wood, rear 3/4 big slab | (840,260,970,420) | #835336 | #B67A50 | #633D26 |
| Wood, side-right view | (330,540,440,700) | #905B3B | #BB7E53 | #6F482E |
| Wood, exploded front beam | (80,1250,440,1450) | #714A30 | #B77D56 | #5E3D28 |
| Wood, exploded beam end (end grain) | (395,1365,465,1440) | #9F6741 | #AA6F45 | #73482B |
| Wood, exploded rear block end / side | (550,1260,600,1340) / (430,1290,530,1350) | #8F5936 / #644029 | | |
| Wood, Detail C underside | (720,1300,980,1450) | #6A452E | #AA734E | #64412A |
| Wood beside the amber (Detail B) | (690,1050,915,1195) | #885532 | #AF7348 | #633F29 |

**Keys** (start from these; calibrate with `K.calibrate`; write the calibrated hexes into `palette()`):

| Key | Start target (rendered) | Where |
| --- | --- | --- |
| `m012_amber_light` | #FEC029 → #FED138 | the upper-centre core facets |
| `m012_amber_mid` | #FB8113 → #FD861D | the belt and most facets |
| `m012_amber_dark` | #D0570D → #C95D0D | the bottom row and lower-left flank |
| `m012_amber_core` (optional) | #FEE554 | the 2–4 brightest facets at the very top-centre (exploded upper p95); the stage 5 Neon candidate, see §7 |
| `m012_wood` | #754B31 → #7A4F34 | the main brown (all wood medians fall between #714A30 and #835336) |
| `m012_wood_dark` | #5B3A24 | lengthwise grain streaks, the V grooves between split boards, the underside and ground-contact band (Detail C #6A452E reads darker overall) |
| `m012_wood_light` | about #A06A44 | the chamfer strips along the long edges and the worn top arrises. The sheet's lit tan lines peak around #C08255, but most of that is lighting, so calibrate the base, not the highlight. |
| `m012_wood_end` | #9F6741 | the cut end faces (end grain): a region, not facing; slightly lighter and warmer |
| `m012_wood_warm` | about #885532 | a subtle amber bleed on wood within about 0.5 stud of the nodule (Detail B reads slightly warmer and more saturated than the general wood). Keep it subtle: the sheet shows no strong orange cast. |

- **Calibration warning:** the sheet's amber has its red channel clipped (#FE…). Calibrating in linear light cannot push a channel past 1.0, so the calibrated amber keys will sit near full saturation. Lower specular rather than raising brightness if the dome renders washed out.

**Blending** (`K.blend` / `_grade`, mode `"blend"`, steps 3, over explicit face lists as in M011; never by facing):

- **Amber field.** A position field in the nodule's own frame:
  - core-ness = 0.6 × (height fraction) − 0.5 × (distance from a core point at 62 % height, about 0.15 W right of centre and 0.2 D forward, inside the stone) + 0.12 × broad noise.
  - Bands: dark → mid over the lowest 15–35 %; mid → light over the upper-centre core.
  - Re-measure the hue shares against the table in §5.
- **Amber inclusions.** Split each broad facet into a coplanar fan of 3–5 triangles from an off-centre interior point (still planar, so it shades as one facet). Give 1 triangle in each mid or light facet the 25–50 % mix towards the next darker key. These are the sheet's angular inclusions. Keep each sub-triangle above 5°.
- **Wood grain.** A noise field stretched along each piece's own long axis: about 0.15 along the length and 1.2 across it. Blend it wood ↔ wood_dark (25/50/75 mixes) so the streaks run lengthwise. The facet breaks already follow the grain, so the streaks sit on whole long facets.
- **Wood regions:**
  - chamfer strips → `wood_light`, or a 50 % mix of it;
  - end faces → `wood_end`;
  - V grooves and the faces within 0.4 of the ground → mix towards `wood_dark`;
  - faces within 0.5 of the nodule → mix 25–50 % towards `wood_warm`.
- **Hard edges only where amber meets wood.** They are separate keys, so this is automatic.

**Texture (Tint):**
- Wood: `tint_var` about 0.05 per board, so neighbouring boards differ slightly as on the sheet. `K.texture` amp 0.06–0.08, patches about 1.5 studs, jitter ±0.015.
- Amber: amp about 0.03, scale about 0.9.
- Mottling must be visible but never confetti.

**Finish:**

| Material | Roughness | Specular | Metal |
| --- | --- | --- | --- |
| Amber | about 0.45 | low (no white glints) | 0 |
| Wood | 0.9 | normal | 0 |

### 7. Lighting and VFX observations (for stages 5 and 6)

**What the sheet shows:**
- The amber looks lit from within: bright yellow seams along the facet edges, star glints at a few upper vertices, and shade facets that stay saturated orange.
- There is no halo, no bloom on the paper and no orange light cast on the wood (wood beside the amber is only slightly warmer).
- No smoke, embers or dust.

**Stage 5 lighting:**
- Do **not** make the whole nodule Neon (emission ≥ 1). The exporter makes those faces Neon parts in one flat colour, which would erase the light/mid/dark facet regions.
  - Emission between 0 and 1 does nothing in Roblox except drop the Tint (`export_kit_roblox.py`, `Colour.emissive`). So don't use it as a "subtle glow" either.
- Recommended: a `crystal_glow` socket with its light set to amber, about #FFA63A, brightness 0.6–0.8, range 8–10, no flicker.
  - Place it outside the solid, about 0.8–1.0 stud in front of the nodule's lower front facets.
  - It keeps the shade side and the nearby wood warm in Roblox. That is the sheet's "stays bright from every angle", which keys alone can't guarantee under in-game lighting.
- Optional: emissive `m012_amber_core` on just 2–4 top-centre facets (Neon) for the user's "glowing resin → emissive part" rule ([[kit-vfx-always]]). Decide from a Studio-style render; if it reads as a light bulb, drop it and record why.

**Stage 6 VFX:**
- 2–3 `ore_glint` sockets with colour ["#FFF4C8", "#FEC029"], sparse (about 0.3–0.5 per second each).
- Box them tightly round the upper-facet vertices where the sheet's star glints sit: the upper-centre and upper-right junctions (§5, glint positions).
- Render with `vfx=True`.

### 8. Pitfalls to avoid

1. **Random convex hulls.** No convex hull of random points for the nodule or the wood. The nodule's facets come in deliberate rows; merge coplanar hull triangles into broad polygons. The wood is lofted chamfered prisms.
2. **Wrong wood primitives.** No pentagonal logs, tapered spikes, smooth pillars or round logs. Every board is a chamfered rectangle with long grain-aligned facets and deliberate end cuts.
3. **Splinter jitter.** No jitter "splinters" at the ends. Use clean angled cuts and chisel tops; at most a step between split boards.
4. **Single beams.** The sheet's pieces are groups: two fused boards, a post with a plank, a three-plank tepee.
5. **Floating pieces.** Every piece rests on the ground, another piece or the nodule, and the base is dead flat (Detail C).
6. **A nodule sitting high and fully exposed.** Its lower quarter is hidden at the front and its back half behind the tall planks. Low front, tall back.
7. **Tall planks above the nodule in the front view.** Keep the tallest at 0.90–0.93 H, behind the nodule's upper back.
8. **Colour by facing.** Never colour by which way a face points. No noise-threshold confetti on the amber: use a blended core field with in-between keys. No isolated yellow triangles, no near-white facets, no white specular (roughness 0.3 did that).
9. **Dull shade-side amber.** It must stay saturated orange (median ≥ #FB8113 in the rear three-quarter). Check the rear, side and top renders, not just the front.
10. **Wood too orange in front or chocolate at the back.** Re-measure the wood medians in all views against #754B31–#905B3B. Calibrate the base; don't eyeball.
11. **Wood colour.** No grey or green weathering on this wood: the sheet's is all warm brown. Weathering is darker lengthwise streaks and lighter worn edges.
12. **Thin faces.** Full-length chamfer strips make sub-2° triangles; split them at the stations. Keep fan sub-triangles above 5°.
13. **Neon or partial emission on the whole nodule.** See §7.

## Stage 1 — Modelling (remake)

Builder `art/blender/kit/mcp/m012.py` rewritten from scratch (nothing of the old `beam()` / `nodule()` kept). Each exploded part is its own function in one shared build frame (studs, front −Y, ground z 0); the hero `Amber` is pasted from the **finished** part meshes (`hero()` → `m011._paste` through each part's recorded `m012_offset`) and exact-unioned into one closed shell.

### What was built

- **`board()`: the one wood primitive.** A chamfered rectangle (8 corners, chamfer 0.16 on every long edge, plus 1–2 grain points on every broad face) lofted through stations about 1.3 apart. Each inner station is nudged ±0.09, twisted ±3.5° and scaled ±6 % per axis, and the grain points move ±0.1 in and out, so every broad face breaks into long planar facets along the grain. The end rings lie on deliberate cut planes, oblique 8–30°, with a chamfered rim. Upright tops are a hewn pyramid (`PYRAMID`) or a chisel (`CHISEL`). There is no hull jitter and no splinters. Chamfer strips get `m012_wood_light` and end cuts `m012_wood_end`, so stage 4 has the regions ready. `pair()` fuses two boards side by side, overlapping 0.1, so their chamfers meet in a V groove, with staggered ends.
- **`nodule()` → `AmberCrystalMain`.** A convex hull of staggered rings: crown 3 points, A 6, B 7, C 7 (B and C aligned, sharing a sector jitter, for the big belt facets), D 6, bottom 4. Radii come from broad sector jitter (±5 % + ±3 %), and the rings tilt gently in height (±3 %) so no row reads as a level band. Coplanar hull triangles merge at 4° into **47 facets** (§3.1 asked 36–44; the rows stay broad, about 1.2–2.2 studs across), then BEAUTY triangulation. Built upright at its own origin. The hero places it with `_nod_matrix()`: bottom at (0.9, 0.25, 0.3), top leaning 8° to −X and 12° to −Y.
- **`wood_front()` → `AmberWoodFront`.** A 7.6-long beam of two fused boards (1.5 tall × 1.15 each, groove along the top, ends staggered −0.35 / +0.45, oblique ends). Its left end rests 1.5 up on a squat stub block (2.0 × 1.9 × 1.85, oblique outer end); its right end is on the ground at the front right. Turned about 11° in plan, sloping about 11°.
- **`wood_back()` → `AmberWoodBack`.**
  - The centre seat: two boards rolled in towards each other into a shallow V, which the nodule drops into.
  - The **rear split block**: two fused halves with a V notch and staggered tops (see the layout decisions).
- **`wood_left()` → `AmberWoodLeft`.** A hewn post (1.35 square, top 5.4 = 0.77 H, leaning 6° out), a shorter plank behind it (1.5 × 0.75, angled top, about 0.57 H), a lying split slab (two boards) along the left foot under the beam's raised end, and a lying square block running back from the post towards the tepee.
- **`wood_right()` → `AmberWoodRight`.** The tepee behind the nodule: the tall chisel-topped plank (1.9 × 1.15, apex 6.2 = 0.88 H), a shorter fused partner (1.5 × 1.1, top about 0.72 H, squarer chamfered top), and the broad shorter plank (2.3 × 1.05) leaning back 12° from their feet. That last plank is the rear views' big slab.

**Cleanup kept inside stage 1,** so the hero is already one closed shell:
- `_drop_inner` removes the sealed pockets left where a third piece roofs the V groove of a fused pair, and crumb shells (under 2 % of the main shell's area); the opening a crumb leaves is closed.
- `m011._clean` runs at `CLEAN_MOVE`.
- `_force_slivers` + `_nudge` clear the last needles and caps (moves of 0.004–0.06 stud at union creases).
- `m004.floor_cut` makes each wood part's flat base (Detail C).

### Layout decisions (view conflicts)

- **Tall planks at back-centre and −X, not at back-right.** I worked out the sheet's cameras with `frame_box`'s azimuths. The rear view (screen right = −X) and the rear three-quarter (screen right ≈ −X) agree: the tall planks stand right of the nodule on screen, i.e. at −X, with the nodule upper-left (+X). So the tepee's tall plank stands at x ≈ 0, y 2.45; the partner at −1.35; the big slab leans back at −0.45. The tall plank sits behind the nodule's crown, hidden in the front and front three-quarter views (checked in the renders), as §2 asked.
- **§3.7's layout (tepee at +X) was not used.** It mirrors the rear views.
- **The rear split block stands on end at the front right**, foot (3.2, −1.25), leaning 4° out. This deviates from §3.3, which has it lying at the back right. Reasons:
  - The hero views show two right-hand uprights (tops 0.45 / 0.57 H) right of the nodule, in front of its lower-right edge.
  - The rear views show a short upright at that side.
  - The sheet's assembled views show no lying block at the back right.
  - The split block's two staggered halves give exactly those two tops (about 0.47 / 0.6 H here).
  - Its foot leans against the seat's end, so `AmberWoodBack` stays one shell.
  - The part's own shape (chunky split block, notch, stepped chamfered ends) is the sheet's.
- **Side views:** that split block stands in front of the nodule's lower middle from +X. The sheet's side-right view shows a mid slab there too, but ours covers a little more of the amber.

### Measured (MCP, after the build)

| Object | Tris | Size W × D × H (studs) | Shells | Non-manifold / boundary / wire | Loose / zero-area / dup / n-gons | Min face angle | Normals | Origin |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Amber` (hero) | 2598 / 4000 | 9.22 × 7.51 × 7.04 | 1 | 0 / 0 / 0 | 0 / 0 / 0 / 0 | 3.41° | outward | bottom centre |
| `AmberCrystalMain` | 62 / 1000 (47 facets) | 5.59 × 4.72 × 6.70 | 1 | 0 / 0 / 0 | 0 / 0 / 0 / 0 | 27.1° | outward | bottom centre |
| `AmberWoodFront` | 678 / 1000 | 8.58 × 3.57 × 2.98 | 1 | 0 / 0 / 0 | 0 / 0 / 0 / 0 | 5.0° | outward | bottom centre |
| `AmberWoodBack` | 644 / 1000 | 7.01 × 3.84 × 4.57 | 1 | 0 / 0 / 0 | 0 / 0 / 0 / 0 | 5.1° | outward | bottom centre |
| `AmberWoodLeft` | 596 / 1000 | 3.65 × 4.77 × 5.59 | 1 | 0 / 0 / 0 | 0 / 0 / 0 / 0 | 3.2° | outward | bottom centre |
| `AmberWoodRight` | 490 / 1000 | 3.66 × 2.75 × 6.18 | 1 | 0 / 0 / 0 | 0 / 0 / 0 / 0 | 3.4° | outward | bottom centre |

- Target size: 9.0 ± 0.4 × 7.2 ± 0.5 × 7.0 ± 0.3. All three are within tolerance; D is at the top of its band.
- Transforms are applied.
- `K.check` raises one flag: the nodule's placeholder light / mid / dark bands correlate with facing (corr 0.65). These are stage 1 placeholders by height; stage 4 replaces them with the §6 core field.
- Materials, placeholders only: `m012_amber_light/mid/dark`, `m012_wood`, `m012_wood_light` (chamfer strips), `m012_wood_end` (cut ends).
- UVs: Smart UV at 45°, seams from islands, angle-based, margin 0.008 (`UV`, as M011). Stage 3 should re-measure them.
- The `.blend` was saved through the MCP.

### View by view (renders/models/M012/)

- **Front three-quarter (governs).**
  - The amber egg sits in a low nest with the long fused beam across its lower third (left end raised on the stub, right end on the ground), a hewn post and a shorter plank at the left, and the split upright pair at the right in front of the egg's lower-right edge.
  - Nothing shows behind the crown. Visible amber starts about 0.3 H up.
  - The sheet's nodule fills a little more of the width (about 0.59 W against our about 0.52 W in this view).
- **Front.** Nodule 0.60 W, centred on the model. Left post 0.73 H; right uprights about 0.5 H; beam front face about 0.2 H. Matches the sheet.
- **Rear three-quarter.** Nodule upper-left, the tall plank and partner right of it, the big leaning slab in front, the left post group at the far right. Same reading as the sheet: low +X, tall back.
- **Rear.** Tall plank at centre, big slab in the foreground, nodule peeking at the upper left. Matches.
- **Side (right).** Nodule at the front, tepee at the back. Here the split upright covers more of the amber's lower middle than on the sheet.
- **Top.** Oval nodule towards the front, ringed about 70 % by wood (tepee and slab at the back, the left group, the right uprights, the beam in front). Matches.
- **Underside.** Flat base of the boards' floor cuts.
- **Exploded and part shots.** Each part on its own. The nodule is upright, as on the sheet.

### Left for later stages

- **Stage 2:**
  - Re-verify the slivers (the minimum is 3.2–3.4° on the hero, left and right) and the one quad left on `AmberWoodLeft`.
  - Optionally trim the nodule to 36–44 facets: `NOD_MERGE` above 4°, or 6/6/6/6 rings.
- **Stage 3:** re-measure the UVs.
- **Stage 4:** all colour work.
  - The amber core field and inclusions (§6).
  - Wood grain along each board's own axis. `board()` knows the axis, so stage 4 can rebuild the fields from the PARTS functions.
  - Calibrate the chamfer-strip and end-cut regions.
- **Stages 5 and 6:** the crystal_glow socket and ore_glint sockets (§7) on the hero.

### Stage 1 fixes (after verifier round 1)

Verifier round 1 scored 5/10. These are its shape findings and what changed in `m012.py`. Everything later stages added (`_polish`, `_tri_quads`, `_force_slivers`, `_uv_unfold`, the colour passes, `BOARDS`, `_vfx`) still runs inside `build()`.

**1. Crisp split timber (blocking).**
- `board()` defaults are now half what they were:
  - station wobble ±0.04 (was ±0.09);
  - twist ±1.5° (was ±3.5°);
  - per-axis scale ±3 % (was ±6 %);
  - grain break ±0.05 (was ±0.1).
- One grain point per broad face, and only on faces 0.8 or wider.
- `CHAMFER` is 0.1 (was 0.16). `SEG` is 1.0 (was 1.3), so the chamfer strips' triangles stay above stage 2's 5° (atan(0.1/1.0) = 5.7°).
- New pointed ends, `end["point"]`:
  - `("pyramid", push, off_u, off_v)`: four sloped faces to one apex.
  - `("chisel", push, ridge, off_u)`: the narrow sides slope up to a short ridge through the thickness, so the broad faces end in a gable point.
  - No upright has a flat or domed top any more:

    | Upright | Point |
    | --- | --- |
    | Left spire | pyramid |
    | Plank behind it | chisel |
    | Tall tepee plank | chisel |
    | Partner | pyramid |
    | Leaning slab | chisel |
    | Both halves of the right split pair | chisel |
    | New back-right upright | chisel |

- Left spire: slimmer (1.05 square, was 1.35) and moved behind the beam's raised end, foot (−3.05, 0.75).
- Right split pair: wider (2.5), leaning 9° out. It now stands clear to the right of the amber in the front three-quarter view.

**2. Seams and inclusions on the nodule (blocking; geometry for stage 4).** `_seams()` runs inside `nodule()` after the facet merge:
- Facet edges longer than `SEAM_SEG` = 1.05 get extra verts (`bisect_edges`: verts only, the facets stay whole).
- Every facet above `SEAM_LOW` = 0.24 of the height gets a **coplanar inset border strip `SEAM` = 0.1 stud wide** (`inset_individual`, depth 0). Its triangles are about 5.4° or more.
- The facet's inside is **poked from a point 22 % of the way to one corner**. The fan triangles are cut into `PATCHES` = 3 contiguous angular sub-patches (2 on small facets). Those are the inclusions.
- Facets lower down sit in the seat. They are only poked (tag "plain"), to keep the part in budget.
- The silhouette and facet planes are unchanged: 47 facets.

**How stage 4 finds them (tagged faces).**
- `NOD_FACES` records every nodule triangle in the nodule's own frame as `(triangle verts, kind, facet, patch)`. Kind is `"seam"`, `"patch"` or `"plain"`; patch is −1 for seams and plain faces.
- Every build refills it. After a Blender restart, `nod_regions()` refills it from a probe build.
- **`nod_regions(o, mat=None)`** returns `{polygon index: (kind, facet, patch)}` for a mesh made from the nodule. A face takes the tag of the recorded triangle its centre lies on (BVH, within 0.06 stud), so stage 2's flips, collapses and nudges keep the tags: all 882 faces of the part match.
  - `mat` defaults to the part's `m012_offset` frame.
  - For the hero, pass the hero-mesh-to-nodule-frame matrix. Stage 4 colours the part, and the hero inherits through `_paste`.
- I changed `colour_nodule` minimally so it uses the tags. Stage 4 may refine:
  - Facets are grouped by the recorded facet id, not by normal. The merged facets are planar only to `NOD_MERGE`, and grouping by normal had split some into per-triangle bands.
  - The inclusion is now a whole patch, the facet's patch lowest in the field.
  - Seams go two ladder steps lighter, on **one side of each edge only** (the facet with the higher id; neighbours found by shared verts). The line is therefore one strip, 0.1 stud wide; lighting both sides read as a heavy cage.

**3. Underside (major).**
- The seat is now three boards (12021, 12022, 12023), each 1.8–1.9 tall, filling the footprint under the nodule's lower half.
- Underside view: amber is 0.038 of the frame (was 0.11; sheet 0.03) and 0.076 of the amber + wood pixels. The base reads as one block of wood.

**4. Amber share (minor).**
- Nodule narrower and more egg-like: `NOD` 5.4 × 4.6 × 6.7 (was 5.6 × 5.0). Ring radii: crown 0.27, A 0.6, B 0.92, C 1.0 at 0.4 H, D 0.8.
- New short chisel-pointed upright at the back right in `AmberWoodBack` (seed 12027, foot (2.25, 1.85), about 0.52 H, its foot in the seat's back board). The sheet's rear views show a short upright over lying blocks on that side, and from the front it stays behind the nodule's flank.
- Amber share (amber ÷ amber + wood, the spec's masks) on the renders:

| View | Front 3/4 | Front | Top | Rear 3/4 | Rear | Side | Underside |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Now | 0.37 | 0.40 | 0.41 | 0.20 | 0.14 | 0.25 | 0.08 (0.038 of frame) |
| Sheet | 0.41 | 0.42 | 0.42 | 0.21 | 0.21 | 0.17 | 0.03 of frame |
| Round 1 | — | — | 0.50 | 0.29 | — | 0.34 | 0.11 of frame |

- The side view is still above the sheet. The sheet's side views put tall planks across the nodule's back half, but the hero front views show nothing behind its crown (§2, hero governs). Covering it from the side would mean planks visible above the nodule's shoulders from the front.

**Measured after the fixes (MCP, after `build()`):**

| Object | Tris | W × D × H (studs) | Shells | Non-manifold / boundary | Min corner |
| --- | --- | --- | --- | --- | --- |
| Amber (hero) | 3364 / 4000 | 9.18 × 7.31 × 6.94 | 1 | 0 / 0 | 5.02° |
| AmberCrystalMain | 882 / 1000 (47 facets; 562 seam, 281 patch, 39 plain faces) | 5.39 × 4.34 × 6.70 | 1 | 0 / 0 | 5.10° |
| AmberWoodFront | 626 | 8.61 × 3.57 × 2.99 | 1 | 0 / 0 | 5.11° |
| AmberWoodBack | 892 | 7.11 × 5.52 × 4.20 | 1 | 0 / 0 | 5.16° |
| AmberWoodLeft | 602 | 3.45 × 4.87 × 5.42 | 1 | 0 / 0 | 5.45° |
| AmberWoodRight | 378 | 3.68 × 2.47 × 5.94 | 1 | 0 / 0 | 5.02° |

- None of the objects has wire edges, loose verts, zero-area faces, duplicate verts or n-gons. Normals point outward and origins sit at the bottom centre.
- The hero's UVs have 0 overlaps, 0 flipped triangles and a minimum gap of 0.016.
- The hero carries its 4 sockets: crystal_glow and 3 × ore_glint.
- `K.check` still flags the nodule's colour correlating with facing, as before.
- The `.blend` is saved.

**For the other stages:**
- **Stage 6:** the `GLINTS` points snap to the nearest nodule vertex. The nodule changed shape and now has seam verts, so check that the three glint boxes still sit on upper light-facet junctions (hero-local now: (1.73, −0.96, 5.79), (0.86, −2.22, 5.51), (2.32, −0.2, 5.05)).
- **Stage 4:** re-calibrate.
  - The narrower nodule changed the facet areas, so re-check the hue shares.
  - Tune how bright the seams are and how deep the inclusions go.
  - Colour the new boards (12022, 12027) through `BOARDS`; they are recorded like the others.

## Stage 2+3 — Cleanup and UV

Builder changes in `m012.py` (rebuilt through the MCP with `m012.build()`; renders rewritten; `.blend` saved):

- **`_polish(o)`** runs on every part (before the hero pastes them) and on the hero, after `_finish`:
  - **`_tri_quads`:** every face becomes a triangle, cut along the diagonal that keeps the larger smallest corner. The one quad left on `AmberWoodLeft` was a thin wedge whose better diagonal already existed as an edge of the next two triangles, so neither BEAUTY nor `_force_slivers` could split it cleanly; the old split made a 0.21° needle. The blocking edge is now rotated out first, then the quad is cut.
  - **`_force_slivers(o, lim=POLISH_LIM)`** with `POLISH_LIM = 5.0`: flips, collapses and nudges of at most 0.015 stud open the last corners under 5°. Before: hero 3.41°, left 3.23°, right 3.41° (3 / 2 / 2 faces under 5°). Ground verts stay on the ground.
  - The origin goes back to the bottom centre (the part's `m012_offset` follows). Then `M.smart_uv(o, **UV)` runs on the final mesh.
- **`_uv_unfold(o)`:** the angle-based unwrap folded an island where a union left a shallow S-step (two nearly parallel faces, dot 0.99, stacked 0.06–0.45 apart). That gave the hero 7 and `AmberWoodBack` 2 same-island overlap pairs. Plain Smart UV at 45° or 66°, conformal, and 30° / 35° all still overlapped, so the smaller face of each pair is cut free along seams and the mesh re-unwrapped with the same method and margin (hero: 4 faces cut; `AmberWoodBack`: 2).
- `UV` is unchanged: Smart UV at 45° → seams from islands → `ANGLE_BASED`, margin 0.008 (gap 0.016).
- The nodule was not trimmed (47 facets, 62 tris, min corner 27°). It already reads as broad rows; fewer facets would change the silhouette for no budget gain.
- **Silhouette is unchanged.** A pixel XOR of the object mask against the stage 1 renders differs by 0.01–0.12 % per view (front34 176 px of 139,881; front 169 of 162,924; worst underside 114 of 96,739), i.e. anti-aliasing at the moved verts.
- **Unused data:** `_drop_unused` purges this build's orphan M012 meshes (21 per rebuild). No orphan `m012` / `Amber` meshes or materials are left. The two orphans in the file (`FB_m011_rock_cool`, `VFXPreview_mat_glow`) are not M012's and were left alone.

### Measured (MCP, after the rebuild)

| Object | Tris | Size W × D × H | Shells | NM / bnd / wire / loose | Zero / dup / n-gon / quad | Self-isect | Min corner | Normals | Origin / xforms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Amber` | 2618 / 4000 | 9.22 × 7.51 × 7.04 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 | 5.00° | outward | bottom centre / applied |
| `AmberCrystalMain` | 62 / 1000 | 5.59 × 4.72 × 6.70 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 | 27.14° | outward | bottom centre / applied |
| `AmberWoodFront` | 678 / 1000 | 8.58 × 3.57 × 2.98 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 | 5.00° | outward | bottom centre / applied |
| `AmberWoodBack` | 644 / 1000 | 7.01 × 3.84 × 4.57 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 | 5.13° | outward | bottom centre / applied |
| `AmberWoodLeft` | 596 / 1000 | 3.65 × 4.77 × 5.59 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 | 5.19° | outward | bottom centre / applied |
| `AmberWoodRight` | 490 / 1000 | 3.66 × 2.75 × 6.18 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 | 5.00° | outward | bottom centre / applied |

No custom split normals, flat shading, no modifiers. One closed shell per object means no interior pockets (`_drop_inner` removed 1 each on Back and Left during the build).

UVs (`M.uv_stats`, layer `UVMap`):

| Object | Islands | Overlap pairs | Flipped | Min gap / border | Density min / med / max | Conformal worst / p95 | Area worst | Angle change worst | Texels/stud @1024 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Amber` | 493 | 0 | 0 | 0.016 / 0.008 | 1 / 1 / 1 | 1.028 / 1.002 | 1.019 | 0.90° | 28.7 |
| `AmberCrystalMain` | 14 | 0 | 0 | 0.016 / 0.008 | 1 / 1 / 1 | 1.000 / 1.000 | 1.000 | 0.00° | 71.4 |
| `AmberWoodFront` | 62 | 0 | 0 | 0.016 / 0.008 | 1 / 1 / 1 | 1.048 / 1.019 | 1.045 | 1.41° | 80.4 |
| `AmberWoodBack` | 122 | 0 | 0 | 0.016 / 0.008 | 1 / 1 / 1 | 1.022 / 1.004 | 1.017 | 1.25° | 68.7 |
| `AmberWoodLeft` | 90 | 0 | 0 | 0.016 / 0.008 | 1 / 1 / 1 | 1.022 / 1.009 | 1.017 | 1.23° | 88.6 |
| `AmberWoodRight` | 37 | 0 | 0 | 0.016 / 0.008 | 1 / 1 / 1 | 1.053 / 1.020 | 1.051 | 2.36° | 86.4 |

Before stage 3: `AmberWoodLeft` had 1 flipped triangle with conformal stretch 744 and density max 3.84 (the wedge quad); the hero had 7 and `AmberWoodBack` 2 overlap pairs. All three are now clean.

### Left for later stages

- **Stage 4:** `K.check` still flags the nodule's placeholder light / mid / dark bands as following facing (corr 0.67). These are the stage 1 placeholders, to be replaced by the §6 core field.
- The hero's 493 islands come from the union's many small facets. That is fine for the exporter's own palette UVs; any baked texture would want the per-part UVs.

## Stage 4 — Materials, colour and texture

All colour work is in `m012.py`: `palette()` and the "stage 4" section (`colour_parts` → `colour_nodule`, `colour_wood`, reusing `m011._Paint`, `m011._grade` and `m011._mottle`). It runs on the **finished** part meshes, after `_polish` (cleanup, origin, UVs), and edits only material indices and the `Tint` attribute. The hero inherits the colour through `m011._paste` and the union. `board()` now records each board's frame (start, axis, length, u/v, half width/thickness) in `BOARDS`, keyed by seed, so the grain can run along each board's own axis after the unions.

**Geometry and UVs are unchanged.** Every part has the same vertex count, face count, vertex-position sum and UV sum as stage 2+3: nodule 33 v / 62 f, front 341 / 678, back 324 / 644, left 300 / 596, right 247 / 490. The hero is 1301 v / 2618 f, as before.
- The hero's vertex-position sum moves by ±0.007 between identical rebuilds; I measured two back-to-back runs with no change in between. Its UV sum moves too. This is pre-existing non-determinism in the hero's union cleanup, not this stage. Counts, minimum corner (5.00°) and UV overlaps (0) are stable.
- After the final build: every object is one shell; 0 non-manifold, 0 boundary edges; 0 UV overlap pairs on all six; minimum corners 5.00 / 27.14 / 5.00 / 5.13 / 5.19 / 5.00°. `K.check` reports **no problems**.

### 1. Sampled targets

The masks are the same on the sheet and on our renders (`m012_meas.py` in the scratchpad):
- **amber:** sat > 0.76, val > 0.45, hue 8–61°. This is tighter than §5's sat > 0.6, which let lit wood into the side-view amber, e.g. the sheet side "amber" #B26932.
- **wood:** 0.2 < sat < 0.75, 0.12 < val < 0.85, hue 5–43°, not amber.

Sheet boxes are §1/§6's (sheet pixels). On our side, each whole 480 × 400 render cell is measured. Hue shares are given as yellow ≥ 36° / light orange 27–36° / orange 21–27° / red-orange < 21°.

Swatches (`M.raw_sample`): Amber Light #FECD64, Mid #FE7719, Dark #D25117, Wood #8E5E3D. The rendered sheet is the target, not the swatches.

### 2. Keys (calibrated) and finish

| Key | Hex | Rough | Specular | Where |
| --- | --- | --- | --- | --- |
| `m012_amber_light` | #FDAE30 | 0.45 | 0 | core facets (upper +X flank) |
| `m012_amber_mid` | #F86E18 | 0.45 | 0 | belt, most facets |
| `m012_amber_dark` | #A04808 | 0.45 | 0 | bottom row, lower −X flank |
| `m012_wood` | #6D482E | 0.9 | 0.5 | broad long faces |
| `m012_wood_dark` | #4F2D11 | 0.9 | 0.5 | grain streaks, V grooves and creases |
| `m012_wood_light` | #8E6241 | 0.9 | 0.5 | worn chamfer strips, lighter worn streaks |
| `m012_wood_end` | #8D5F3D | 0.9 | 0.5 | cut ends, rims and upright floor cuts (end grain) |
| `m012_wood_warm` | #7B4C28 | 0.9 | 0.5 | warm bleed on wood beside the amber |

The `K.mix_key` in-between keys at 25 / 50 / 75 % carry the gradients:
- amber dark → mid #B6520C / #CC5B10 / #E26414;
- amber mid → light #F97E1E / #FA8E24 / #FC9E2A;
- wood → dark #664127 / #5E3A20 / #563418;
- wood → light #754E33 / #7E5538 / #865C3C;
- wood → warm #70492C / #744A2B / #784B2A.

**22 keys are in use on the hero.** Metal is 0 and emission 0 everywhere.

How the keys were set:
- **Calibration.** `K.calibrate` (test dome, kit studio, vivid / brown masks), targets amber light #FEC228 / mid #FC861A / dark #D85C0E and wood #7A4F34 / dark #5B3A24 / light #A06A44 / end #9F6741 / warm #8A5532.
  - First result: amber #FD9624 / #F86A16 / #A34D09; wood #5B3B25 / #41240C / #775135 / #764F32 / #673F20, each within 6 levels on the dome.
- **Correction against the hero renders.** The dome is fully lit and the model is not, so I corrected each key in linear light against the hero renders, as on M011:
  - **Wood ×1.47 (linear).** With the dome hexes the hero front three-quarter came out #6A452F against #784E33.
  - **Amber light raised to #FDAE30.** On the nodule's upper facets it rendered golden #FFAF24, not the sheet's yellow.
  - **Amber mid a touch yellower, #F86E18.** Shade-side mid faces read red.
  - **Amber dark #A04808.**
- **Amber specular is 0** on every amber key, including the mixes, which `_mi` creates with flintkit's default 0.2. Even the foliage 0.06 left the crown, seen at a grazing angle, reflecting the studio sky as a cream-white facet (#FFFFBC at the top of front34 / rear34). Now it renders amber (#EE600D / #FF8C1B). There are no white glints anywhere.

### 3. Blending (position fields; never facing)

**Amber, `colour_nodule`:**
- **Facets.** Coplanar, edge-connected triangles (normal dot > 0.9995) are grouped into the nodule's 49 facets, so each facet keeps one main tone.
- **Field per facet**, in the nodule's own frame: 0.3 × height/H − 0.7 × distance to a core point / H + 0.25 × broad noise, minus a crown drop of up to 0.4 above 0.82 H.
  - The core point is (0.25 W, 0, 0.6 H): upper, towards +X, centred front to back, so the yellow shows from the front *and* the rear views, as on the sheet.
  - The sheet's top view shows the crown orange, with the yellow on the upper flank, hence the crown drop.
- **Ranking and grading.** Facets are ranked by the field, and the rank (cumulative area fraction) is graded with `m011._grade` (K.blend "blend", steps 3):
  - dark → mid over rank 0–0.2;
  - plain mid over 0.2–0.28;
  - mid → light over 0.28–1.0.

  Neighbouring facets step through the in-between tones, and the shares come out at the sheet's whatever the facet sizes are.
- **Inclusions without touching geometry.** In each of the 11 mid-or-lighter facets made of two or more triangles, the triangle lowest in the field drops one step darker (two steps on facets over 1.5 studs²). These are the sheet's angular darker shapes. §6's coplanar fan split was not used: it changes the triangle count, and this stage must not change geometry.
- **Result on the nodule:** dark 2, dark→mid 4 / 5 / 6, mid 12, mid→light 12 / 9 / 8, light 4 triangles. `K.check`'s baked-shading score is 0.40 on the nodule and 0.21 on the hero, under the 0.5 limit with no waiver. The core sits on the +X side, away from the studio key at −X front.

**Wood, `colour_wood`, per part with that part's boards:**
- **Own board.** Each face's own board is the nearest board box (signed distance). Its grain coordinates are (along × 0.15, across u × 1.2, across v × 1.2) in that board's frame, so the streaks run lengthwise on each board, uprights included.
- **Broad faces.** Grain noise from 0.07 to 0.57 grades wood → wood_dark (dark streaks). The other end of the same noise, below −0.2, grades wood → wood_light up to 50 % (lighter worn streaks).
- **Chamfer strips.** wood → wood_light by a second grain noise, 0.5 ± 0.6, so mostly 25–75 %: worn edges that wander along the board.
- **Cut ends** are `wood_end`. **Floor cuts** under uprights (board axis |z| > 0.6) are end grain too; under lying boards they are long faces.
- **V grooves and creases.** Broad or chamfer faces within 0.12 of another board's box take the 50 % dark mix. That is the groove between fused boards and the crease where one board lies on another (108–137 faces per part).
- **Warm bleed.** Broad faces within 0.7 stud of the nodule's surface (its hero placement, BVH) are graded wood → wood_warm by distance: full at contact, through 75 / 50 / 25 %. This covers 58 faces on the front part, 124 on the back (mostly the hidden seat), 15 on the left and 41 on the right.
- **No ground band.** §6 suggested darkening faces near the ground, but the underside already renders darker than the sheet's (see §5 below), and M011's verifier read a painted foot band as painted shadow.

`mode="hard"` is never used: amber and wood are separate keys, so their edge is hard by construction.

### 4. Texture (Tint)

- **Wood:**
  - each board carries its own ±5 % Tint from `mk`'s tint_var;
  - `_mottle` adds amp 0.07, patches about 1.5 studs (scale 0.65) and ±1.2 % jitter.
  - Range 0.875–1.088.
- **Amber:** a per-facet drift (amp 0.03, scale 0.9, no per-triangle jitter), so each facet stays one flat tone. Range 0.946–1.009.
- **Confetti check.** In the renders the mottling reads as broad patches and lengthwise streaks; I saw no per-triangle confetti.

### 5. Target vs got (final build, saved)

Each cell is median / lit (top 25 %) / shade (low 25 %), followed by the hue shares where given.

| Region | Sheet | Ours |
| --- | --- | --- |
| Amber, front 3/4 | #FB8113 / #FEBE25 / #D65A0B; 25/38/32/5 % | #FF8F1A / #FFB224 / #F7640B; 33/32/34/1 % |
| Amber, front | #FC8412 / #FEBD23 / #D4590C; 23/41/30/6 | #FF8C1A / #FFB224 / #C7570B; 30/39/29/2 |
| Amber, rear 3/4 | #FD871A / #FEBB29 / #C65006; 28/37/28/7 | #FF921C / #FFBC29 / #FB7617; 32/55/12/1 |
| Amber, rear | #FC871A / #FDB629 / #C04F06; 26/35/34/5 | #FF921C / #FFBC2A / #F6620E; 30/51/18/1 |
| Amber, side | #F87D13 / #FDAE27 / #B64C05; 18/36/40/7 | #FF881A / #FFAA24 / #D26412; 20/65/14/1 |
| Amber, top | #FA8219 / #FEAB2E / #C85915; 17/46/28/9 | #FF8918 / #FF9F21 / #FF670F; 12/48/40/0 |
| Amber, exploded nodule → part | #FC811B / #FEA82A / #DB5F10; 13/40/38/8 | #FF8716 / #FFBB27 / #F3610A; 27/26/44/3 |
| Nodule upper / middle / lower third (median) | #FD9D2A / #FD871E / #E46A10 | #FFAC22 / #FF9A1C / #FD620D |
| Amber in the underside view | #FB8C1B | #FF8A1A |
| Wood, front 3/4 | #784E33 / #B5784E / #583722 | #805337 / #A26B48 / #6B462D |
| Wood, front | #794E32 / #B2764B / #583822 | #7E5236 / #996745 / #603E29 |
| Wood, exploded parts (all) → exploded render | #7D5134 / #B67C54 / #603E27 | #7F5236 / #9D6947 / #573722 |
| Wood, exploded beam → part_woodfront | #724A31 / #B87E56 / #5F3E28 | #815438 / #9E6949 / #764B31 |
| Wood beside the amber, front 3/4 (wood within 10 px of amber) | #A0653D (Detail B #8B5734) | #966543 |
| Wood, top | #805539 | #986443 |
| Wood, rear 3/4 | #7F5235 | #6E4830 |
| Wood, rear | #89583A | #68442E |
| Wood, side | #8C593A | #583822 |
| Wood, underside (Detail C) | #6A462E | #3D2518 |
| End grain (sheet beam end → our beam's right end) | #A36940 | #7F5337 |

Reading the table:

- **Amber stays bright and saturated from every angle.** The medians are all #FF7E–#FF92 with the green channel within about 6–15 of the sheet's; the old build went brick #C0531A on the rear.
  - The hue shares match in the front three-quarter and front views (within about 8 points per band).
  - The rear and side views run a little more light orange than the sheet's orange. The top view is close (12 / 48 / 40 against 17 / 46 / 28).
  - Lit quartiles are within about 12. Shade quartiles are at or a little brighter than the sheet's: the studio's rear fill keeps the shade side warm.
- **Amber zoning.** The nodule's upper third is yellower than the sheet's (55 % yellow against 38 %), and its lower third is a little redder and brighter: #FD620D against #E46A10, with the sheet's lower third holding 41 % light orange. The bands hold these against the hero views, which govern and match.
- **The hero-view wood matches.** Front three-quarter +8, front +5, and the exploded wood overall within 2 levels.
- **The rest of the wood spread is the studio, not paint.** The studio's key light is fixed in the world, while the sheet lights every view. With the same paint:
  - the top view reads lighter (+24);
  - the rear three-quarter (−17), rear (−33), side (−52) and underside (−45) read darker. Nothing lights the underside view from below, and the rear fill only partly reaches the rest.
  - Painting the back pieces lighter would paint lighting in, so the base is set so the governing hero views sit a few levels over the sheet, as a compromise.
  - The same applies to the end grain: our measured beam end faces away from the key. The `wood_end` key is about 1.3× lighter than `wood`, like the sheet's.
- **Warm bleed.** The wood beside the amber reads lighter and warmer than the general wood, as on the sheet (#966543 against #A0653D in the front three-quarter).

### 6. Reaching Roblox (checked against `export_kit_roblox.py`'s logic; nothing exported)

- **Palette keys.** All 22 keys on the six objects are flintkit palette materials with `flintkit_hex` equal to `KIT_PALETTE`. None is emissive or water, so none becomes Neon and none drops its Tint.
- **Tint levels** (clusters at a 0.004 spacing):
  - All amber keys fit at 1–7 levels, and most wood keys at 13–30.
  - Four wood keys exceed 32 clusters and are quantised by the exporter to 32 quantile levels: `m012_wood` (34), `m012_wood_end` (45, from many small end-cap fan triangles), `m012_wood_x_dark_50` (39). The worst error stays small because patches are broad and the per-face jitter is only ±1.2 %.
- **Specular / roughness** do not export. Roblox shades by its own lighting, and the palette texture carries the key × Tint colour.
- **Housekeeping.** The 20 orphan `T_Calib*` meshes from calibration were purged. `_drop_unused` removed no M012 materials, because every mix in the palette is in use. The .blend was saved through the MCP and is not dirty.

### Left for later stages

- **Stage 5:**
  - Per §7, don't make the nodule Neon: it would flatten the graded facets into one colour.
  - The `crystal_glow` PointLight (#FFA63A, about 0.6–0.8, range 8–10) in front of the lower facets is what keeps the amber's shade side and the nearby wood warm in Roblox. In the Blender studio the paint alone already reads bright from every angle.
- **Stage 6:**
  - The `ore_glint` sockets belong on the upper +X flank, where the light core facets are; that is the sheet's glint area.
  - Positions: the facets with key `m012_amber_light` / `_x_amber_light_75` on `AmberCrystalMain`, through `_nod_matrix()`.
- **Verifier:**
  - Measure with the amber mask sat > 0.76; at sat > 0.6 the side views count lit wood as amber.
  - Expect the rear, side and underside wood to read darker than the sheet's. That is studio lighting (see §5).

### Fixes after verifier round 1

Round 1 failed at 5/10. Stage 1 has since reworked the geometry (see "Stage 1 fixes (after verifier round 1)"):
- crisper boards (chamfer 0.1, pointed uprights);
- a narrower egg with tagged seam strips and 2–3 inclusion patches per facet (`NOD_FACES` / `nod_regions`);
- a three-board seat and a new upright (12027).

This pass changes only material indices, Tint and palette hexes. The counts are stage 1's: hero 3364, nodule 882, front 626, back 892, left 602, right 378 tris. Minimum corners 5.02–5.45°; 0 UV overlaps on all six; 4 sockets on the hero. **`K.check` reports no problems**: baked-shading 0.22 on the hero and 0.32 on the nodule, with no waiver.

#### What changed in `m012.py`

1. **Amber reads as a gem, not matte plastic.**
   - **Glowing seams.** The seam strips (one side of each facet edge, `nod_regions` kind "seam") step up a seam ladder by their facet's rank (`SEAM_STEPS`):
     - rank < 0.2: no line;
     - rank 0.2–0.5: +1 step;
     - rank 0.5–0.8: +2 steps;
     - rank > 0.8: +3 steps.

     The ladder runs `_ladder()` + light → `amber_glow` 50 % → `amber_glow`. New key `m012_amber_glow` #FDB76E (dome renders #FFEC81, the sheet's pale-yellow seam) only ever appears on seams. So in the core the lines read pale yellow, and lower down they fade to a faint lighter edge or nothing: lines, not a cage. 278 seam faces.
   - **Inclusions both ways**, per tagged patch:
     - **Darker:** in every facet, the patch lowest in the field drops two ladder steps (three on facets over 1.5 studs²). 40 facets.
     - **Lighter:** in facets of rank ≥ 0.3, another patch goes one step lighter where a broad noise over the patch centres is above 0.1 (`AMBER_INCL_LIGHT`). 17 facets.
   - **Red-orange at the lower −X.** `m012_amber_dark` is now #924A0E (was #A04808). It renders dark orange at the base hue and red-orange where shaded, so the shade quartiles came down and the red share rose to about 9 % in the front three-quarter view.
     - A redder key, #8A380C, pushed red-orange to 20–23 % of every view. The renderer's gamma reddens darker saturated orange.
   - **Field re-tuned for the narrower nodule.**
     - core (0.25 W, −0.1 D, 0.6 H): a little forward, so the rear views carry less yellow;
     - noise 0.3;
     - crown drop 0.6 above 0.82 H (the sheet's crown is orange; this also keeps baked-shading under 0.5);
     - dark → mid over rank 0–0.2, mid → light over 0.34–1.0.
   - Amber specular stays 0 on every amber key and mix.
2. **Wood weathering.**
   - **Chamfer strips are full `m012_wood_light` #A06A44** (was 25–75 % of #8E6241): the sheet's bright tan edge lines. They drop to 75 % only where a wear noise along the board is below −0.3.
   - **Angular chips** (`CHIP`): a second, isotropic noise in each board's own frame (scale 1.1, patches of a few triangles).
     - Above 0.36: a lighter worn chip, 75 % `wood_light`.
     - Below −0.32: a darker knock, 75 % `wood_dark`.
     - Each chip has a one-step rim (50 %) over a 0.12 band.
     - 49/31, 102/39, 31/42 and 37/21 light/dark chips on the front, back, left and right parts.
   - **Less dark groove.** `GROOVE` reach is 0.05 (was 0.12): 64 / 101 / 36 / 44 faces. Grain dark streaks start at 0.15 (level 0.4, was 0.32). `wood_x_dark_50` is now 11.1 % of the hero's wood area (round 1: 14.6 %), shared between grain streaks, chip rims and grooves.
   - **Base raised.** `m012_wood` #6E4A2F, `wood_end` #98663F, `wood_warm` #84522B. The hero's area-weighted mean wood albedo (key × Tint, linear) is now **#7E5333** (round 1: #704A2D; swatch #8E5E3D).
     - I tried #765032 (+8 % on the old base): the front three-quarter median went to #8F5D3B, +23 over the sheet's. The chamfers and light chips already carry the lift, so the base sits between.
3. **The new boards** (seat 12022 and upright 12027) are coloured like the others through `BOARDS`: `AmberWoodBack` now colours 6 boards.

#### Palette now

| Key | Hex | Where |
| --- | --- | --- |
| `m012_amber_glow` | #FDB76E | seam lines in the core only |
| `m012_amber_light` | #FDAE30 | core facets, upper +X flank |
| `m012_amber_mid` | #F66816 | belt, most facets |
| `m012_amber_dark` | #924A0E | lower −X and bottom; darker inclusions |
| `m012_wood` | #6E4A2F | broad faces |
| `m012_wood_dark` | #4F2D11 | grain streaks, knocks, grooves |
| `m012_wood_light` | #A06A44 | chamfer lines, worn chips and streaks |
| `m012_wood_end` | #98663F | cut ends, pointed tops, upright floor cuts |
| `m012_wood_warm` | #84522B | bleed beside the amber |

- **Finish.** Amber has roughness 0.45 and specular 0; wood has roughness 0.9. Metal and emission are 0 everywhere.
- **Mixes in use.**
  - Amber: dark → mid #AB5210 / #C45912 / #DD6014; mid → light #F87A1C / #FA8B23 / #FB9C2A; light → glow 50 % #FDB24F.
  - Wood: → dark #664328 / #5E3C20 / #573418; → light #7A5234 / #875A3A / #94623F; → warm #744C2E / #794E2D / #7E502C.
- **25 keys are in use.**
- **Nodule area by key:**
  - mid 16.6 %;
  - mid → light 25 / 50 / 75: 13.8 / 13.5 / 9.7 %;
  - light 9.1 %;
  - light → glow 50 % 0.9 %, glow 3.0 %;
  - dark → mid 75 / 50 / 25 % dark: 10.8 / 9.2 / 11.5 %;
  - dark 1.9 %.

#### Target vs got (final build, saved)

Masks as in §1 (amber sat > 0.76). Each cell is median / lit / shade, then the hue shares (yellow / light orange / orange / red-orange).

| Region | Sheet | Ours |
| --- | --- | --- |
| Amber, front 3/4 | #FB8113 / #FEBE25 / #D65A0B; 25/38/32/5 | #FF9119 / #FFC72B / #F85F0C; 34/30/26/9 |
| Amber, front | #FC8412 / #FEBD23 / #D4590C; 23/41/30/6 | #FF911A / #FFC72B / #EA5E0C; 33/35/19/13 |
| Amber, rear 3/4 | #FD871A / #FEBB29 / #C65006; 28/37/28/7 | #FF911F / #FFAC26 / #FF6910; 38/19/40/3 |
| Amber, rear | #FC871A / #FDB629 / #C04F06; 26/35/34/5 | #FF7A15 / #FFA825 / #DC560C; 29/17/51/2 |
| Amber, side | #F87D13 / #FDAE27 / #B64C05; 18/36/40/7 | #FF841A / #FFA824 / #D25E0D; 19/48/24/10 |
| Amber, top | #FA8219 / #FEAB2E / #C85915; 17/46/28/9 | #FF7512 / #FFA524 / #C2550B; 12/27/60/0 |
| Amber, exploded nodule → part | #FC811B / #FEA82A / #DB5F10; 13/40/38/8 | #FF8D18 / #FFCA2C / #D6580B; 29/26/37/9 |
| Nodule upper / middle / lower third | #FD9D2A / #FD871E / #E46A10 | #FF9B1F / #FF901B / #FA610D |
| Wood, front 3/4 | #784E33 / #B5784E / #583722 | #865738 / #BF7B4E / #6D462C |
| Wood, front | #794E32 / #B2764B / #583822 | #855839 / #AF704A / #6B442B |
| Wood, exploded parts | #7D5134 / #B67C54 / #603E27 | #875939 / #B4764C / #664027 |
| Wood, exploded beam → part_woodfront | #724A31 / #B87E56 / #5F3E28 | #845739 / #AB6F4D / #7A5034 |
| Wood beside the amber, front 3/4 | #A0653D / #BC7D51 / #6A3E21 | #A56F4B / #C78050 / #784C30 |
| Wood, rear 3/4 | #7F5235 / #B2774E / #5E3B25 | #704B32 / #9E6742 / #5A3B26 |
| Wood, rear | #89583A | #6D4931 |
| Wood, side | #8C593A | #5F3D27 |
| Wood, top | #805539 | #9A6540 |
| Wood, underside | #6A462E | #42291A |

Reading the table:

- **Amber.**
  - **Medians.** All hero views are within about 15 green levels of the sheet's (the red channel is clipped in both).
  - **Red-orange** is now 9–13 % in the front views (round 1: 1–3 %).
  - **Shade quartiles came down.** Front three-quarter #F85F0C (round 1 #F7640B), front #EA5E0C, side #D25E0D, top #C2550B and the part #D6580B are within about 20 of the sheet's. The rear three-quarter shade (#FF6910 against #C65006) is still bright: the studio's rear fill lights that side of the egg evenly.
  - **Light-orange share is low in the rear views** (17–19 % against 35–37 %), with more orange instead. The rear views look at the mid belt from behind, where the seams and the lighter inclusions are sparse.
  - **The top view** reads more orange than the sheet's (60 % against 28 %). The crown drop that keeps the colour from following facing makes the crown orange.
  - **Seams and inclusions.** These are visible in every amber view: pale-yellow lines on the upper flank, fading out lower down, with darker and lighter angular patches inside the facets.
- **Wood.**
  - **Lit quartiles now reach the sheet's tan:** front three-quarter #BF7B4E against #B5784E (round 1 #A56C48), the chamfer lines and worn chips.
  - **Medians** are +8 to +18 over the sheet in the lit views (front three-quarter, front, exploded) and darker in the rear, side and underside. That spread is the studio lighting the verifier accepted.
  - **The shade quartile** is still lighter than the sheet's in the lit views (#6D462C against #583722): the fill light, not paint.

#### Reaching Roblox (exporter logic; nothing exported)

- All 25 keys are palette materials with a matching `flintkit_hex`. None is emissive or water.
- **Tint range** 0.895–1.096.
- **Tint levels.** Four wood keys exceed 32 Tint clusters and are quantised to 32 quantile levels: `m012_wood` 40, `m012_wood_end` 40, `m012_wood_light` 37 and `m012_wood_x_dark_50` 37. The patches are broad and the jitter is ±1.2 %, so the error is small. All amber keys fit.
- **Housekeeping.** The calibration orphans (`T_Calib*`) were purged. The only orphans left are M011's and the VFX preview material. The .blend was saved through the MCP and is not dirty.

#### Left for later

- **Stage 6:** the core moved 0.1 D forward, but the three `GLINTS` junctions still sit on light facets. Their nearest nodule verts touch `amber_glow` + light / light_75 / light_50 faces (checked through the MCP), so no change is needed.
- **Verifier:**
  - Measure amber with sat > 0.76.
  - In the rear three-quarter view the shade quartile and the light-orange share are the remaining studio-bound gaps (see above).

## Stage 5+6 — Lighting and VFX

Decision: **no emissive faces. The hero `Amber` carries four sockets:** one `crystal_glow` (a soft amber PointLight in front of the nodule) and three `ore_glint` (sparse amber twinkles at the light-facet junctions on the upper +X flank). The parts carry none.

Built in `m012.py`:
- `STUDIO_LIGHT`, `GLINTS`, `GLINT_REACH` / `GLINT_PAD`, `GLINT`, `_glint_fx` and `_vfx`, passed as `M.mk(..., fx=_vfx(nodule))` on the hero.
- No geometry, UV, palette key, Tint or material changed.

### Why no emission (no Neon)

- **What the sheet shows.** The amber reads lit from within: bright seams, star glints, and shade facets that stay saturated orange. It casts no halo on the paper and no orange light on the wood (§7).
- **Emission ≥ 1.0 would flatten the facets.** `export_kit_roblox.py` (`GLOW_EMISSION` = 1.0, `Colour.glow`) turns those faces into Neon parts, one flat colour per key, ignoring Tint. On the nodule that erases the graded dark → mid → light facets and the inclusions, and Neon blooms: the "light bulb" §7 warns about.
- **The optional `m012_amber_core` Neon facets were dropped too.** The brightest top facets are already `amber_light` (#FDAE30 → #FECD64 rendered). A Neon patch there would bloom as a hot spot the sheet doesn't have.
- **Emission between 0 and 1 doesn't help either.** It doesn't glow in Roblox; it only sets `Colour.emissive` and drops the Tint.
- **Checked.** All 22 M012 keys have `flintkit_spec[2]` = 0.

### Sockets (children of `Amber`, collection `M012 Amber`)

All values were measured through the MCP on the saved build:
- **Hero-local:** the socket's `location`, in Blender studs from the hero's bottom-centre origin.
- **Manifest:** the exporter's `to_rbx(x, z, −y)` of the socket's position minus the hero's origin.

All four: `vfx_scale` 1.0, no `trigger`, identity parent inverse.

| Socket | Kind | Hero-local (x, y, z) | Manifest (Roblox x, y, z) | Settings |
| --- | --- | --- | --- | --- |
| `VFX_Amber_crystal_glow_1` | `crystal_glow` | (1.2478, −4.8213, 4.4) | (1.2478, 4.4, 4.8213) | PointLight `#FFA63A`, brightness 0.7, range 8, `shadows` true, `flicker` false; no emitters |
| `VFX_Amber_ore_glint_1` | `ore_glint` | (2.0798, −1.1323, 6.074) | (2.0798, 6.074, 1.1323) | upper-right junction of three light facets; box 0.64 × 0.77 × 0.83 (Roblox x, y, z); rate 0.5/s; size 0 → 0.6 → 0 |
| `VFX_Amber_ore_glint_2` | `ore_glint` | (0.9218, −2.5723, 5.685) | (0.9218, 5.685, 2.5723) | upper front-centre junction (light / light_75 / light); box 0.87 × 0.82 × 0.55; rate 0.35/s; size 0 → 0.5 → 0 |
| `VFX_Amber_ore_glint_3` | `ore_glint` | (2.6908, −0.2013, 5.09) | (2.6908, 5.09, 0.2013) | +X flank junction of four light / light_75 facets; box 0.53 × 0.81 × 0.80; rate 0.25/s; size 0 → 0.45 → 0 |

**The glint emitter** (`GLINT`, passed as an `emitters` override):
- texture `spark_diamond`;
- colour `#FFF4C8` → `#FEC029` (pale-cream flash fading to amber yellow);
- transparency 0.1 → 1.0, lifetime 0.5–0.8 s;
- speed 0, spread 0 (they twinkle in place);
- light emission 1.0, rotation 0–90°.

As M011 found, only the `emitters` override sets the colour: `vfx.add` replaces top-level keys, and nothing reads a top-level `color` for this kind.

### Light placement

- **Final point.** Build frame (1.2, −4.6, 4.4): in front of the nodule and above the front beam. It is hero-local (1.2478, −4.8213, 4.4), because the hero's build offset is (−0.0478, 0.2213, 0).
- **Clearance (BVH on the hero).** Outside the solid. The nearest amber facet is 1.836 away, the nearest wood 2.995 away, and the ground 4.4 below.
- **Why not the study's 0.8–1.0 stud.** I first placed it at (0.9, −3.6, 3.4), 0.92 from the amber and 1.58 from the wood. In the vfx preview that left a round hot spot on the lower front facets: +28 levels at the 99th percentile over a no-light render. It read as a light bulb inside the egg and broke the flat facet regions (Detail A).
- **Effect from the final point.** Scratch renders, front three-quarter + front, light vs no light:
  - amber: mean +2.1, 99th percentile +14, spread evenly with no visible spot;
  - wood: mean +0.7, 99th percentile +3.0: "slightly warmer", no halo;
  - everything else (paper, ground): 99th percentile +2.
- **Shadows on.** The nodule blocks the light from the tepee and rear planks, so the back stays wood-brown. The shade side it lifts is the front and lower front, which the beam half-hides.
- **Range 8, not 10.** It still covers the whole nodule from this point. It keeps the amber pool on the ground in front small, since the sheet shows no light on the ground.

### Glint placement

- **The fit (`_glint_fx`).** Each `GLINTS` entry is a build-frame point snapped to the nearest nodule vertex through `_nod_matrix() @ _frame(nodule)`.
  - The box is that vertex plus the points `GLINT_REACH` = 0.45 stud along each of its hull edges, padded by `GLINT_PAD` = 0.05.
  - So the box hugs the surface round the junction, like M011's tip fit.
- **The junctions.** All three sit where `amber_light` / `amber_mid_x_amber_light_75` facets meet on the upper +X flank and crown: the sheet's star-glint area (§5, §7). In the build frame they are the vertices at (2.11, −0.92, 6.14), (0.93, −2.5, 5.77) and (2.77, 0.09, 5.16).
- **Junction moved off the wood.** The mid-flank junction at (2.62, −1.65, 4.45) is also all light facets, but the front-right split block's top touches the nodule 0.33 from it. 3 % of its outside spawn points were closer to wood than to amber, so it was swapped for (2.77, 0.09, 5.16), which is 0.82 clear of wood.
- **Measured (1000 random points per box, BVH on the saved hero):**
  - "Unoccluded" casts a ray toward the front three-quarter camera.
  - "Distance" runs from each outside point to the nearest amber face.

  | Box | Outside the solid | Unoccluded | Distance 95th pct / max | Closer to wood than amber |
  | --- | --- | --- | --- | --- |
  | 1 | 57 % | 52 % | 0.36 / 0.51 | 0 |
  | 2 | 43 % | 43 % | 0.28 / 0.44 | 0 |
  | 3 | 50 % | 26 % (on the +X side, faces away from that camera) | 0.26 / 0.41 | 0 |

  - **Contact.** No twinkle can spawn more than 0.51 stud from an amber face, under a particle's own peak size, so each one touches its facet junction.
  - **Socket points.** Each lies 0.09–0.16 inside the surface. The rest of each box is inside the nodule and hidden.
- **Rate.** About 1.1 twinkles a second in all, at 0.5–0.8 s each: under one on screen at a time, sparse as §7 asks.

### Renders (`build()` renders with `M.views(vfx=True)`)

- **Glints.** Small cream-yellow diamond stand-ins sit right on the upper-right facet junctions in the front three-quarter, front, rear three-quarter and top views. None floats in the air or on the wood.
- **Light.** It is a subtle even lift; the amber reads as before, with no glow spot. Nothing changed in the side, rear, underside or part renders.
- The exploded and part shots carry no sockets: the parts have none.

### Reaching Roblox (read from `export_kit_roblox.py`; nothing exported)

- **Socket collection.** `sockets(obj)` collects every child with `vfx_kind` of the `Amber` hero. Its manifest entries are `name`, `kind`, `position` = `to_rbx(world − origin)` (the table's Roblox column), `vfx_scale` 1.0, `trigger` null, and `spec` = the socket's `roblox` JSON (the light dict, or the glint emitter with its `shape`, `rate`, `size` and `color`).
- **No beams.** No `end`, `axis` or `normal` are written. No `flow` either.
- **STATS.** The STATS line should count 4 vfx sockets for `Amber`; confirm it when the main session exports.
- **Textures.** `ore_glint` needs `art/vfx/textures/spark_diamond.png`, which already exists (M011 uses it). `crystal_glow` needs none.
- **No Neon.** No M012 key is emissive, so the export writes no Neon pieces and keeps the Tint on every key.

### Studio-side setup (one per placed Amber)

| Property | Value |
| --- | --- |
| Instance | the manifest's `crystal_glow` socket: an `Attachment` in the Amber MeshPart with a `PointLight` inside |
| Attachment position | `Vector3.new(1.248, 4.4, 4.821)` from the asset origin (bottom centre of the footprint) |
| `Color` | `#FFA63A` = `Color3.fromRGB(255, 166, 58)` |
| `Brightness` | 0.7 (tune 0.5–0.9 under the game's Future lighting) |
| `Range` | 8 studs, times the placed model's scale |
| `Shadows` | true (the nodule keeps the light off the rear planks) |
| Animation | none (steady) |

- **Glints.** Each `ore_glint` is a `ParticleEmitter` on its own Attachment, `Shape` Box with the listed size, `EmissionDirection` irrelevant (speed 0), `LightEmission` 1.
- **Performance.** One PointLight per node. Where several Amber nodes stand close together, set `Shadows` false on all but the nearest few, or drop `Range` to 6.
- **Harvest.** When the node is depleted, disable the light and the emitters with the nodule.
- **Ground pool.** If a warm pool on the ground in front reads as a halo under night lighting, lower `Range` to 7 before lowering `Brightness`.

### Housekeeping and checks

- **Rebuild.** `m012.build()` was rebuilt through the MCP: `K.check` reports no problems, the hero has 2618 tris and 1 shell, and the parts are unchanged.
- **One generic fix in `_polish`.** Its bottom-centre re-centring now moves the object's children (the VFX sockets) by the same offset, as `M.finish` already does. Before, sockets added through `mk(fx=...)` would have drifted by the polish offset. Only the hero has children; no mesh is affected.
- **Content check against the .blend as stage 4 saved it (order-independent, face by face).**
  - The five parts are identical in vertices, palette keys and Tint.
  - The hero matches on every palette key and Tint. One vertex differs by 0.0057 stud.
- **Pre-existing non-determinism (not from this stage):**
  - `nodule()`'s convex hull comes out in a different face order on each build in the same session. Hence the hero's vertex order, and the angle-based UV layout of the nodule and hero, differ between builds. One `_nudge` vertex also moved, by 0.006.
  - Keys and Tint per face are unchanged.
  - Stage 3 or the main session may want to sort the hull faces if byte-identical rebuilds matter.
- **Saved.** The .blend was saved through the MCP; no M012 orphan meshes and no `VFXPreview_*` objects are left.

### Left for later stages

- **Verifier:**
  - Check the glints on the upper-right junctions in the front three-quarter, rear three-quarter and top renders.
  - Check that there is no glow spot on the amber and no orange cast on the wood.
- **Main session:** confirm `STATS M012 ...` reports 4 vfx sockets on export.
- **Studio (Requires Manual Validation):** brightness and range under the game's Lighting, per the table above.

## Result

Verifier round 2: PASS, 7/10, no blocking issues. Round 1 had failed at 5/10.

Open minors, kept for a later polish pass:
- The rear uprights read as near-vertical posts with symmetric caps. The sheet shows fewer, broader slabs that lean outward, with slanted cuts.
- The amber shows less than the sheet in the rear view (0.12 against 0.22) and more in the side view (0.22 against 0.17).
- In the top view the nodule sits forward of centre.
- The egg's latitude rings show as a regular belt.
- The lit band is a little yellow in the front three-quarter view.
- The inclusion patches repeat into a star on the front.
