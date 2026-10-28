# 013 Sulfur — spec

Reference: `art/blender/assets/references/013.png` (SULFUR; the sheet header says "PAGE 7/132", INDEX.md lists it as
13; 1024 × 1536 px). Builder: `art/blender/kit/mcp/m013.py` → `build()`. The current builder is an untested quick
draft; §9 lists where it departs from the sheet.

User direction for every model: colours "need to match the master reference and blend into the colors nearby. please
ensure all color and textures are being made and applied." Shapes must match the sheet.

All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, top-left origin. Measurements come from the sheet's own pixels
with two masks:
- **sulfur**: max > 110, sat > 0.42, r > b + 60, g > b + 50, |r − g| < 60;
- **rock**: not paper (within 18 of #EEEAE3), max < 232, sat < 0.25, not sulfur.

The scripts are in the session scratchpad (`m013_study/measure.py`, `prof.py`, `cols.py`, `samp.py`, `grade.py`).

## Study (2a)

### 1. Classification, size and scale

- **Classification:** full asset (resource node). Hero budget 4000 tris; each part 1000.
- **What it is:** three big chamfered blocks of lemon-yellow sulfur and one small nugget, sitting on a **flat stack
  of three horizontal rock strata**, with 7 small faceted rocks round the foot. WorldModeling §12.4: "Sulfur: chunky
  yellow mineral blocks on a broad stepped slab." Leave substantial host rock visible.
- **Target size: about 10.4 W × 8.8 D × 7.0 H studs.** Height is about 1.27× the 5.5-stud character, in line with
  M010 Gold (9.6 × 9.6 × 7.6) and M009 (7.4 H). Tolerances: W ±0.4, D ±0.5, H ±0.3.
  - The sheet's front, side and rear views are not level. They look down about 10–15°: the slab tops show, and the
    ground contact at the left and right ends sits about 0.09 H above the front-most rock's. So their apparent heights
    include about 1 stud of receding top surface.
  - Apparent ratios: front W : H 1.31, side D : H 1.11. Taking off that stud gives W 10.4, D 8.8 and H about 6.9.
  - The kit's own front, side and rear cameras sit at 4° (`M.VIEWS`). Our front render will therefore read **wider
    and lower than the sheet** (expect W : H about 1.45 against 1.31). For a like-for-like check, also render the
    hero at elevation 11° (front 0°, side 90°, rear 180°) through `M.views(..., extra={...})`. Compare those with the
    sheet, and the true sizes with this table.

**Measured views** (bbox of sulfur ∪ rock, base rocks included):

| View (search box) | bbox (px) | W : H | Sulfur share of silhouette | Sulfur spans (W fraction) | Sulfur lowest point (H) |
| --- | --- | --- | --- | --- | --- |
| Front three-quarter (60,110,510,455) | 60–503 × 131–444 | 1.42 | 38 % | 0.17–0.91 | 0.40 |
| "Rear" three-quarter (540,110,975,455) | 540–962 × 123–445 | 1.31 | 36 % | 0.16–0.84 | 0.36 |
| Front (25,535,265,725) | 25–256 × 546–722 | 1.31 | 42 % | 0.13–0.90 | 0.38 |
| Side (280,535,500,725) | 286–479 × 547–721 | 1.11 (D : H) | 39 % | 0.17–0.90 | 0.35 |
| Rear (505,535,755,725) | 513–745 × 546–722 | 1.32 | 31 % | 0.10–0.91 | 0.46 |
| Top (762,525,1000,738) | 786–987 × 531–734 | 0.99 | 45 % | 0.14–0.92 | — |

- **Reading:** a broad, low, layered rock table. From the front and the top it is about half yellow; from the back,
  rock dominates, with the yellow tops peeking over. The rock is about the lower half of the height and the sulfur
  the upper half.
- **Verifier check:** the sulfur share per view (±5 points), the sulfur's lowest point per view, and the W : H ratios
  at the matching elevation.

### 2. Silhouette and proportions per view

All heights are fractions of the view's apparent H; all widths are fractions of W.

**Front three-quarter (hero, governs):**
- Three chamfered yellow blocks in a row on the top slab, overlapping:
  - a **small cube-ish left chunk**, crop-local top about 0.82 H;
  - a **tall, long block behind centre**, the top of the model;
  - a **long, low brick at the front right**, overlapping the tall block's lower right. It is the biggest front face
    on the sheet.
- A small yellow **nugget** sits at the front-right foot of the brick, on the slab's front edge (sheet px about
  (440, 305), about 0.09 W wide).
- The top slab is a long, rounded lozenge whose front-right lobe runs out to the right. Its front wall shows 6–7
  large wall facets across.
- Under it, two more strata step in and out. At the left all three strata show; at the right the top slab sits over
  the lowest stratum.
- A **rock knob** rises at the slab's right end, behind the brick (sheet px about (455–490, 260–305)). It is also seen
  in the front view (x 0.91–0.96, top 0.55 H) and in the "rear" three-quarter.
- **Base rocks:** a big one at the front left, one at the front centre, one at the front right, and a small one at
  the far right.

**Front** (W 231 × H 176 px; column profiles from `prof.py`):

| Region | x (W) | Top (H) | Visible bottom (H) |
| --- | --- | --- | --- |
| Left chunk | 0.13–0.32 | 0.78–0.80 | 0.55 (behind the slab rim) |
| Tall chunk | 0.31–0.68 | 0.99 (peak at x 0.52–0.57) | 0.57 |
| Front-right brick | 0.44–0.89 | 0.75 → 0.70 (falls to the right) | 0.38 (front edge) |
| Rock top at the left end | 0.05–0.13 | 0.55–0.60 | — |
| Right-end knob | 0.91–0.96 | 0.52–0.55 | — |

- **Strata seams, at the left end:** h 0.35 (top slab / base upper) and h 0.18 (base upper / plinth).
- **At the right**, the top slab's front wall runs from 0.41 down to its seam at 0.19. That is the same seam, drawn
  lower because the front-right lobe is nearer the elevated camera.
- **Base rocks** (x fractions): 0.02–0.13, 0.30–0.54 (the largest), 0.76–0.93, 0.93–1.0.

**Side** (camera at +X, so the front is at screen right). Column luminance profiles (`cols.py`) give the strata
without depth mixing:
- At x 0.25 (back): rock 0.49 → seam 0.32–0.29 → stratum → seam 0.17 → base rock.
- At x 0.55: top-slab chamfer 0.46–0.44, wall to 0.32, seam 0.31, middle stratum to 0.24, dark groove 0.23–0.20,
  plinth to 0.02.
- At x 0.85 (front): brick to 0.41, contact line 0.38, slab 0.37–0.25, seam 0.24, stratum to 0.12, seam 0.14,
  plinth.
- **So the three strata are about equally thick** (0.12–0.16 H each). They are horizontal, dropping only about
  0.07 H (about 0.5 stud) from back to front.
- Sulfur occupies the top half. The tall block is at the back (screen left) and the brick at the front (screen
  right), its front face near vertical.
- **Base rocks** (x fractions): 0.03–0.20 (back right), 0.20–0.42 (a larger right-side rock), 0.83–0.95 (front
  right).

**Rear** (camera at +Y, so screen right = −X):
- The tall block's top sits at the centre (0.32–0.68 W, top 1.0).
- Two side chunk tops at 0.73 H show left and right (0.10–0.32 and 0.68–0.91).
- Rock rises to 0.59 between them: the top slab's back terrace seen through the gaps.
- The top slab is the widest stratum here (0.94–0.95 W at 0.36–0.41 H), overhanging the base upper (0.88 W at
  0.23–0.27) with a dark undercut seam at about 0.32.
- The plinth below shows a broad chamfered front.
- **Base rocks** only at the two back corners: 0.03–0.21 (= +X) and 0.65–0.85 plus 0.86–0.96 (= −X). There is **no
  rock at the back centre.**

**Top:**
- **Footprint:** a near-round rounded oval (bbox 0.99; principal axes 1.14 : 1, major axis at −49° in image space,
  i.e. front-left to back-right). The outline is lumpy, made of broad straight segments.
- **Chunks** (fractions of the bbox, back = 0):
  - small chunk x 0.14–0.44, 0.36–0.67 from the back, a turned square;
  - tall block x 0.33–0.82, 0.10–0.53, turned about 20°;
  - brick x 0.48–0.92, 0.39–0.81, turned about −25° (it follows the slab's front-right edge).
- The chunk pile covers about 60 % of the top slab.
- The visible rock rim is widest at the left and back-left (the terrace) and narrowest at the right.
- Base rocks peek out at the lower left and the right.

**Underside (close-up, (567,948,865,1103)):**
- One broad flat planar bottom: an 8–10-sided outline, matte.
- A chamfer band runs up to the walls.
- Base rocks at the corners stick out past the rim.
- "Closed, simplified underside. Broad planar faces."

**Chunk-to-rock junction (close-up, (567,795,865,932)):**
- The chunk's flat bottom sits on the slab's flat top. Its lower chamfer row stays visible above the contact line.
- The rock round it is broken into broad planes.
- No fillet, no gap, no noise.

**Relative thickness (close-up, (567,1120,865,1268)):** a chunk stands about 2.5–3× a stratum's thickness ("chunky
proportions with bold, readable forms").

### 3. Parts (exploded view, box (30,790,550,1260))

Four labelled parts: Sulfur Chunk, Host Rock (Top), Host Rock (Base) and Base Rock. The arrows drop each chunk
straight down onto the top slab, and the top slab straight down onto the base.

**Shared rock language:**
- Every stratum is a **thick, flat, pillow-edged slab**: a flat top, a top chamfer band (about 0.3–0.4 stud wide at
  35–45°), and a near-vertical wall broken into large planar facets (each 1.5–2.5 studs long, alternately tilted a
  few degrees).
- A lower chamfer tucks the wall in by about 0.3, which makes a **dark undercut groove at every seam**. The bottom is
  flat.
- Outlines are irregular rounded lozenges of broad straight segments, never circles or perfect ellipses.
- The strata are **horizontal and stacked flat**, each outline offset 0.2–0.6 from its neighbours. So the sides show
  stepped ledges, never one flush wall.

#### 3.1 Sulfur Chunk: exploded centre chunk (188,800,342,908); variants (97,855,208,948) and (287,880,418,975)

- **Shape: a chamfered block.** A box with every edge bevelled broadly (chamfer about 0.20–0.24 of each side, one
  segment), and each corner cut by a small triangle or pentagon.
- Each big face is **gently broken into 2–4 nearly coplanar planes** (2–6° apart). Faces read flat but hand-cut, never
  domed or noisy.
- The bottom is a flat contact face.
- About 30–45 planar polygons per chunk after merging (`bmesh.ops.dissolve_limit` at 3°), 60–100 tris.
- W : H in the exploded is 1.19 / 1.43 / 1.38 for the three. The sheet's chunks are blocks, longer than tall, **not
  crystals and not plain boxes**.
- **Construction:**
  - Take the convex hull of the 24 corner-chamfer points (3 per corner, as in the draft).
  - Add one bulge point on each side-face centre (pushed out 3–5 % of that dimension) and two on the top along the
    long axis. Each face then hulls into 3–4 planes.
  - Jitter the points by broad sides (±4 %), not per point. Keep the bottom 4–8 points coplanar.
  - Then dissolve_limit at 3° and BEAUTY-triangulate.
- **Reuse:** this is one reusable part. Build the hero's three blocks from **copies of the finished part mesh**, as
  `m011._paste` / M012's `hero()` do (STAGES: "assemble the hero strictly from those parts"). Vary them by
  non-uniform scale, yaw, a 90° turn or a mirror, so the three don't read as clones.
- In the exploded render, show three variants as temporary linked copies, as M011 did with its crystals.
- **Hero instances** (starting values; build frame, front −Y, ground z 0):

| Instance | Centre (x, y) | Bottom z | Size W × D × H | Yaw | Notes |
| --- | --- | --- | --- | --- | --- |
| Tall block (back centre) | (+0.2, +1.2) | 3.35 | 4.0 × 3.1 × 3.6 | +15° | the model's top, 6.95; upright |
| Brick (front right) | (+1.9, −1.2) | 3.0 | 4.4 × 2.9 × 2.7 | −12° | long and low, W : H about 1.6; overlaps the tall block's lower front by about 0.5; sits on the lower shelf |
| Left chunk | (−2.6, +0.1) | 3.35 | 2.6 × 2.4 × 2.4 | +30° | cube-ish; tilt about 6° towards −X (the front view shows its top tipping left) |
| Nugget | (+3.7, −2.4) | 3.0 | 1.0 × 0.9 × 0.55 | +40° | squat domed mini block at the brick's front-right foot, on the slab's front edge; a scaled copy is fine |

- **Seating:** sink each chunk only **0.08–0.12** into its slab top, so the lower chamfer row stays visible (Detail
  A). The draft's 0.35 sink hides it.
- The chunks touch and interpenetrate their neighbours a little; the hero union merges them.

#### 3.2 Host Rock (Top): exploded (75,968,415,1100)

One stratum with a **tiered top**.
- **Plan:** a long rounded lozenge, about **9.8 × 7.4**, centre (+0.2, −0.1), yaw −8°. 16 points per ring,
  superellipse exponent about 2.6, broad sector jitter ±5 %. The front-right lobe reaches x ≈ +4.9.
- **Section:**
  - bottom z 2.25; main (shelf) top **3.1**;
  - a **raised back-left terrace**: a second, thinner hull (about 6.6 × 4.6, centre (−1.0, +0.9), top **3.45**,
    bottom buried at 2.9), unioned in. That gives a real step of about 0.35 with its own chamfer, as the exploded slab
    shows (a step line running diagonally across the top).
  - The terrace's front edge runs diagonally between the tall block's front and the brick's back, so the tall block
    and the left chunk sit on the terrace and the brick on the lower shelf.
- **Right-end knob:** a small hull of about 2.0 × 2.2, centre (+4.3, +0.6), top about 3.6, unioned into the slab end
  behind the brick (§2).
- **Rings for each hull** (fractions of the hull's height and half-extent):

| Ring | z | Radius |
| --- | --- | --- |
| Bottom (undercut) | 0.0 | 0.90 |
| Lower wall | 0.22 | 1.0 |
| Upper wall | 0.72 | 0.99 |
| Top (chamfer) | 1.0 | 0.88 |

- It is the widest stratum at the back (rear view) and overhangs the base upper by about 0.3 there.
- Seen from below it has a flat bottom (hidden in the hero).

#### 3.3 Host Rock (Base): exploded (55,1080,410,1225)

The sheet draws it as **two fused strata**: the labelled upper slab and an unlabelled lower plinth directly under
it, with a seam groove between them. It is the only unlabelled solid on the sheet, so it belongs to this part, as
M012 folded its unlabelled seat into a labelled part.

- **Base upper:** about **9.6 × 7.6**, centre (+0.1, +0.2), yaw +5°, z 1.2 → 2.35. 14–16 points per ring, the same
  rings as §3.2. Narrower than the top slab at the back; it shows at the left under the top slab (front three-quarter
  left end).
- **Plinth:** about **9.4 × 7.8**, centre (−0.2, +0.1), yaw −3°, z 0 → 1.3. Its outline is a little more rectangular
  (exponent about 3).
  - It sticks out about 0.3–0.5 past the base upper at the front left (exploded) and is set back at the right.
  - Its bottom ring is inset to 0.92 for the underside chamfer, then cut flat at z 0 (`m004.floor_cut`).
- The two overlap by 0.1 and are unioned. The undercut chamfers make the dark groove.

#### 3.4 Base Rock: exploded (175,1195,250,1250), the front one; 6–7 shown round the base

- **Shape:** a squat faceted dome, H : W about 0.65–0.75.
  - A small flat-ish top facet (pentagon) ringed by 5–6 sloped facets, then a near-vertical lower ring, then a flat
    bottom.
  - About 10–14 faces, 30–50 tris.
  - The draft's `BASE_RINGS` ((0, 0.92, 6), (0.4, 1.0, 6), (0.75, 0.7, 5), (1.0, 0.25, 3)) matches this well.
- **Reuse:** one reusable part; the hero uses scaled and rotated copies.
- Each sits against the plinth, its centre about at the plinth's edge, sunk about 0.3–0.5 into the plinth wall and
  floor-cut at z 0.
- **Count 7, no rock at the back centre** (rear view) and none at the front centre between x −0.5 and +2.5 (front
  view):

| Rock | Centre (x, y) | W × D × H | Seen in |
| --- | --- | --- | --- |
| Front centre-left (largest) | (−0.9, −3.6) | 2.5 × 2.1 × 1.6 | front 0.30–0.54; front three-quarter centre |
| Front left | (−4.3, −2.6) | 2.2 × 1.9 × 1.5 | front three-quarter big left; front 0.02–0.13 |
| Front right | (+3.6, −3.4) | 1.9 × 1.7 × 1.3 | front 0.76–0.93; side front |
| Right | (+5.0, +1.0) | 1.8 × 1.6 × 1.2 | side 0.20–0.42; front far right |
| Back right | (+4.1, +3.2) | 1.6 × 1.4 × 1.0 | rear 0.03–0.21; side back |
| Back left | (−2.6, +3.5) | 2.0 × 1.7 × 1.3 | rear 0.65–0.85 |
| Back-left small | (−4.4, +2.9) | 1.2 × 1.0 × 0.8 | rear 0.86–0.96; exploded small back-left rock |

#### 3.5 Starting layout summary (build frame, front −Y, ground z 0)

| Piece | Centre (x, y) | z range | Plan size | Yaw |
| --- | --- | --- | --- | --- |
| Plinth (Base) | (−0.2, +0.1) | 0 – 1.3 | 9.4 × 7.8 | −3° |
| Base upper (Base) | (+0.1, +0.2) | 1.2 – 2.35 | 9.6 × 7.6 | +5° |
| Top slab: shelf | (+0.2, −0.1) | 2.25 – 3.1 | 9.8 × 7.4 | −8° |
| Top slab: terrace | (−1.0, +0.9) | 2.9 – 3.45 | 6.6 × 4.6 | −8° |
| Top slab: right knob | (+4.3, +0.6) | 2.9 – 3.6 | 2.0 × 2.2 | — |
| Chunks / nugget | §3.1 table | | | |
| Base rocks | §3.4 table | 0 – 1.6 | | |

- **Expected hero size:** strata 9.8 W; base rocks take it to about 10.4 W × 8.8–9.0 D; tall block top 6.95 H.
- **Tune against:** the sulfur shares and the lowest points in §1, the front-view chunk table in §2, and the side-view
  seam heights.

### 4. View conflicts and resolutions

1. **The "rear three-quarter" is not a rear view.**
   - It shows the brick's long front face and the nugget at its foot, with the small chunk at screen left and the tall
     block behind. That is the front of the pile, seen from the **front right** (azimuth about +30°).
   - The real back is given only by the Rear view: the tall block centred, two side tops, rock rising between them and
     no nugget.
   - **Resolution:** build to the front, front three-quarter, top and rear views. Use the sheet's "rear
     three-quarter" for the right flank (the right-end knob, the right-side base rocks, the brick's right end).
   - Verifier: compare it with an **extra render at azimuth +28, elevation 12** of the hero, not with the kit's rear34
     (azimuth 152).
2. **Camera elevation.** The sheet's front, side and rear views look down about 10–15°; the kit's look down 4° (§1).
   Compare true sizes, or render the extra 11° set.
3. **Strata count.** The exploded view labels two host parts; the hero shows three strata. Resolution: Host Rock
   (Base) = base upper + plinth, fused (§3.3).
4. **Top view and side views.** The top view's footprint is near round (bbox 0.99, axes 1.14); front and side give
   W : D about 1.18. Resolution: W : D 1.18 (10.4 × 8.8). The top view's camera is probably slightly tilted.
5. **Shelf step or perspective?** In the front view the brick's visible bottom (0.38 H) is far lower than the left
   chunk's (0.55 H).
   - That is more than the 10–15° camera can explain for the 1.3 stud of depth between their front edges in the top
     view. So the brick really sits lower.
   - Resolution: the lower front-right shelf (§3.2). If the step reads fussy in renders, a shelf sloping 6–8° down to
     the front right is an acceptable fallback; record which was used.
6. **The exploded top slab looks narrower and longer** than in the hero (exploded perspective). The hero views govern
   its plan size.

## 5. Colour plan for stage 4

### 5.1 Swatches (flat; `M.raw_sample` medians of the inner 48 px)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Sulfur | (42,1342,90,1390) | #FEE04D | 50°, 0.70, 1.00 |
| Sulfur Shadow | (148,1342,197,1390) | #C4B145 | 51°, 0.65, 0.77 |
| Host Rock | (255,1342,304,1390) | #988F8D | 11°, 0.07, 0.60 |
| Base Rock | (361,1342,410,1390) | #6F625C | 19°, 0.18, 0.44 |

### 5.2 Rendered regions (pre-measured)

Re-sample with `K.sample(..., "vivid")` for the sulfur and `M.sample(..., "stone")` for the rock. Medians first,
then the lit quartile (top 25 % by luminance) and the shade quartile (low 25 %).

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Sulfur, front three-quarter, all chunks | (137,131,466,320) | sulfur | #EBCA2D | #FDEF63 | #BEA225 |
| Sulfur, front three-quarter, tall block | (215,135,365,250) | sulfur | #F1D22E | #FDED5B | #C6A921 |
| Sulfur, front three-quarter, brick top | (290,205,440,240) | sulfur | #FDEF5B | #FEF877 | #EAC723 |
| Sulfur, front three-quarter, brick front face | (285,235,390,310) | sulfur | #D3B72B | #F3D534 | #B49B27 |
| Sulfur, front three-quarter, left chunk (in shade) | (80,190,175,290) | sulfur | #C1AB31 | #FCED67 | #AD9729 |
| Sulfur, front view | (56,546,233,657) | sulfur | #F1D330 | #FDEF5F | #BBA42B |
| Sulfur, side view | (319,547,461,661) | sulfur | #ECD134 | #FEF25F | #C3AB2B |
| Sulfur, rear view | (536,546,724,642) | sulfur | #EED333 | #FDEE61 | #C0A524 |
| Sulfur, top view | (815,553,971,699) | sulfur | #F7DE43 | #FEF168 | #BAA228 |
| Sulfur, exploded, all three | (95,798,420,980) | sulfur | #EFD033 | #FEF369 | #B89D1E |
| Sulfur, junction close-up | (640,797,862,930) | sulfur | #D8B319 | #F3CD22 | #937409 |
| Host, front view top-slab wall | (30,625,250,660) | rock | #A8978E | #C1AFA6 | #686263 |
| Host, side view top slab | (300,615,470,665) | rock | #988B87 | #C2B0A7 | #686364 |
| Host, rear view top slab | (515,600,745,665) | rock | #91827C | #BEAAA0 | #6B6361 |
| Host, top view (slab rim) | (786,531,987,734) | rock | #9A887E | #C1B4AF | #645C5A |
| Host, front three-quarter shelf top (lit) | (300,300,470,330) | rock | #BDA99F | #C3AFA6 | #AF9A8E |
| Host, front three-quarter all strata | (90,250,500,400) | rock | #7F716B | #BDABA3 | #544B48 |
| Host, exploded top slab | (75,968,415,1100) | rock | #8A7E7C | #BDAAA2 | #564C46 |
| Host, exploded base (both strata) | (55,1080,410,1200) | rock | #756B68 | #B3A099 | #4E4642 |
| Lower strata, front view | (30,662,250,712) | rock | #7B6C66 | #B5A199 | #514946 |
| Lower strata, side view | (300,668,470,705) | rock | #776862 | #BBA69F | #4D4643 |
| Lower strata, rear view | (560,668,690,715) | rock | #75655D | #96847E | #584E49 |
| Seam / undercut, front three-quarter left | (70,320,150,350) | rock | #56504F | #645E5F | #453F3D |
| Underside, flat bottom (close-up) | (600,1030,840,1095) | rock | #574F4B | #5D544F | #514945 |
| Rock beside a chunk (junction close-up) | (570,860,700,930) | rock | #9B877D | #B2A097 | #756A65 |
| Base rock, front three-quarter front left | (80,385,185,445) | rock | #9B847D | #B49E97 | #756862 |
| Base rock, front three-quarter centre | (255,385,345,445) | rock | #8C7D7B | #B9A59E | #6A5C56 |
| Base rock, front view | (90,690,140,722) | rock | #8B7D7A | #BDA9A2 | #5D5451 |
| Base rock, exploded front | (175,1195,250,1250) | rock | #998580 | #BCA7A2 | #706059 |

### 5.3 How the sulfur grades from yellow to the olive shadow

Luminance deciles of the sulfur pixels in the front three-quarter (`grade.py`), dark to light:

```
#A98E1A #C2A727 #CAAE28 #D4B92C #E7C527 #EDCC29 #F3D32E #F6DB37 #FDED5C #FEF673
hue 49   50      50      50      49      50      50      52      54      57
sat .85  .80     .80     .79     .83     .83     .81     .78     .64     .55
```

The exploded chunks give almost the same ladder (#AB901A … #FEF774).

- **The "olive" shadow is darkened yellow at the same hue** (49–50°), with saturation held at about 0.8. It is not
  a greener hue.
- **Only the brightest 20 %** (the lit crests and top faces) lift towards a pale lemon: hue 54–57°, saturation
  0.55–0.64.
- **No white or near-white anywhere.** p95 is #FEF76C.
- **Per chunk, top to bottom** (exploded, so no rock shading; 4 height bands):

| Chunk | Top | Band 2 | Band 3 | Bottom |
| --- | --- | --- | --- | --- |
| Centre | #FDF270 | #F8DD3F | #EFD336 | #E7C935 |
| Left | #FDF165 | #EECE2B | #D1B022 | #B59B21 |
| Right | #FDEC54 | #FCDD35 | #EECC22 | #C8A91F |

- On the assembled model the bottom band at the rock contact goes deeper: junction close-up bottom band #977609.
  Chunks in another chunk's shadow (the left chunk) sit at a median of #C1AB31.
- **What is lighting and what is paint:**
  - Most of the ramp is the studio light: the lemon crests come from the sun, the olive undersides from shade.
  - The swatch pair (Sulfur / Sulfur Shadow) says the painter also intends **a darker olive-gold region low on each
    chunk and in the crevices between chunks and at the rock**. That is a position field (occlusion-like), which is
    allowed.
  - Never pick a face's key by its facing.

### 5.4 Rock tones

- **Hue:** host rock renders as a **warm mauve-grey**, hue 16–21°, saturation 0.12–0.16. That is warmer and more
  saturated than its swatch (11°, 0.07).
  - Lit tops go pinkish beige (#BDA99F).
  - Shaded walls go cool neutral grey: the exploded top slab's shade band is #8E8583 at 11°, 0.08, and its bottom
    band #726A69.
  - Most of that warm/cool split is the studio's warm key and cool fill. Paint only a mild, broad warm/cool
    variation.
- **The strata darken downwards:** top-slab walls #A8978E / #988B87 / #91827C (front / side / rear) against lower
  strata #7B6C66 / #776862 / #75655D.
  - Part of that is shadow under the overhangs. But the exploded base, which has no slab resting on it, still renders
    darker and browner than the exploded top slab (#756B68 against #8A7E7C).
  - So the lower strata are painted towards the darker, browner **Base Rock** tone (#6F625C, 19°, 0.18), and the
    seams are dark grooves.
- **Base rocks** render #8B7D7A–#9B847D, hue 15–18°, saturation 0.14–0.16. They are brighter than their swatch
  because they stand in full light: a slightly browner, warmer stone than the slab walls beside them, so they sit in
  the darker foot band and blend into it.
- **No yellow staining on the rock**, even right beside a chunk: the junction rock is #9B877D, hue 19°. Sulfur
  against rock is a hard material edge.

### 5.5 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Targets are rendered medians for the dome calibration, not swatches.

| Key | Calibration target | Where |
| --- | --- | --- |
| `m013_sulfur` | #F0D230 | all chunk bodies (front / side / rear / exploded medians #ECD134–#F1D330) |
| `m013_sulfur_light` | #F8E04A (subtle step) | the upper crest band of each chunk, the top 15–20 % of its height. The pale lemon (#FDEF5F) comes from the sun; this key only keeps the crest from going mustard. Drop it if calibration makes it read white. |
| `m013_sulfur_shadow` | #C8AC2A (between the shade quartile #BEA225 and the swatch #C4B145) | the bottom 25–35 % of each chunk, the crevices where chunks touch, and the faces within about 0.5 of the rock |
| `m013_host` | #9B8B84 (mean of the front / side / rear / top slab medians) | top-slab walls and top, base-upper walls |
| `m013_host_cool` | #8E8584 (11°, about 0.07; swatch-like) | broad cool-grey weathering patches across all strata |
| `m013_host_dark` | #776862 (lower-strata medians #75655D–#7B6C66) | the plinth, the seam grooves and undercut chamfers, the underside |
| `m013_base` | #94817B (base-rock medians #8B7D7A–#9B847D; swatch #6F625C) | the 7 base rocks |

- The draft's palette (#F8DF3C, #C9BC3E, #8F8684, #817876, #776A66) is uncalibrated; replace it.
- **Calibration warnings:**
  - The sulfur targets have red near the clip (#F…), so the calibrated sulfur keys will sit near full saturation.
    Lower specular rather than raising brightness if the dome washes to lemon-white.
  - `K.sample`'s vivid mask should catch the sulfur. If the shadow key is too dark it may fall out of the vivid mask;
    use the sulfur mask above as a fallback.
  - For the rock, use `M.sample`'s stone mask (paper dropped). `K.sample`'s own stone mask (sat < 0.18) drops warm
    pixels, as M011 found.

### 5.6 Blending

`K.blend` / M011's `_grade`, mode `"blend"`, steps 3, over explicit face lists. Fields are positions in the shared
build frame, never facing.

- **Sulfur, per chunk, in the chunk's own frame:**
  - u = height fraction (0 bottom, 1 top) + 0.12 × broad noise (scale about 0.5) + 0.1 × (lateral position along the
    long axis), so the band edges wander and don't line up with face rows.
  - shadow → sulfur over u 0.15–0.40 (75 / 50 / 25 % mixes); sulfur → light over u 0.82–0.97.
  - Then an **occlusion field:** faces within 0.5 stud of another chunk or of the rock get at least a 50 % mix to the
    shadow key, and within 0.15 the full shadow. The crevices between the three blocks and the contact row go olive,
    as on the sheet (left chunk #C1AB31; junction bottom #977609).
  - Keep the correlation with facing below 0.5 (`K.check`). The lateral and noise terms are what break it; M012's
    height-only bands scored 0.65.
- **Rock, strata grade (vertical, by z in the build frame):**
  - top slab = `host`;
  - base upper = 25 % towards `host_dark`;
  - plinth = 50–75 % towards `host_dark`;
  - the plinth's bottom 0.4 stud and the underside = `host_dark`.
- **Seams:** faces of the undercut and top chamfers within 0.25 stud of a stratum boundary → 75 % `host_dark`, so
  each seam reads as a dark groove line (sheet #56504F).
- **Weathering:** broad noise (scale about 0.2, patches 4–5 studs) host ↔ host_cool, level 0.3, width 0.5. Mild:
  the sheet's rock is "clean, solid".
- **Base rocks:** `base`; crown faces (top 30 % of each rock) 25 % towards `host` so they blend with the slab walls;
  the ground-contact row 25 % towards `host_dark`.
- **Hard edges only where sulfur meets rock.** They are separate keys, so this is automatic. No yellow bleed onto the
  rock.

### 5.7 Texture (Tint) and finish

**Tint:**
- Per piece: `tint_var` about 0.04, so neighbouring strata, chunks and base rocks differ slightly.
- `K.texture`, rock: amp 0.05–0.06, patches about 2 studs (scale 0.45), jitter ±0.015.
- `K.texture`, sulfur: amp 0.03, scale about 0.9, jitter ±0.01.
- The sheet says "no texture noise", so the mottling stays broad and calm, never confetti.

**Finish:**

| Material | Roughness | Specular | Metal | Notes |
| --- | --- | --- | --- | --- |
| Sulfur | 0.55–0.6 | low (about 0.3) | 0 | waxy matte; soft lemon highlights, never white glints |
| Host rock | 0.92 | normal | 0 | matte |
| Base rock | 0.92 | normal | 0 | matte |

## 6. Lighting and VFX observations (for stages 5 and 6)

What the sheet shows:
- **No glow:** shade faces drop to olive (#A98E1A at the 10th percentile), unlike M012's self-lit amber. There are
  no emissive parts, no halo, no bloom and no yellow light on the rock.
- **No fumes, vapour, smoke, dust or sparkle** in any view or close-up. The notes stress "clean, solid colors".

**Stage 5:** skip. Record "sheet shows no emissive parts or glow". Do not make any sulfur Neon.

**Stage 6:** skip for ambient effects. Record "sheet shows no fumes, dust or sparkle; sulfur is matte, so no
ore_glint".
- The old R02 kit sulfur node carried `vapour` and `harvest_hit` sockets. Those were that sheet's choices; this sheet
  shows none, and M001–M012 carry no harvest sockets. Don't add vapour.
- If the main session later wants harvest feedback across all nodes, a `harvest_hit` socket at the pile's front
  (about (+1.0, −2.6, 4.5)) with chips ["#F0D230", "#C8AC2A"] is the natural one. That is not a sheet requirement.

## 7. Naming

The draft's names (`build()` specs):

| Draft name | Part | Clash? |
| --- | --- | --- |
| `Sulfur` | hero | free |
| `SulfurChunk` | Sulfur Chunk | **taken by the R02 kit sheet** (R02_stats.json, `scripts/kit/R02/sulfur_node.py`). `M.mk` would silently rename it `SulfurChunkM013`. |
| `SulfurHostTop` | Host Rock (Top) | free |
| `SulfurHostBase` | Host Rock (Base) | free |
| `SulfurBaseRock` | Base Rock | **taken by R02**; it would become `SulfurBaseRockM013`. |

- R02 also owns `SulfurNode`, `SulfurHostRock`, `SulfurNodeDepleted`, `SulfurChunkDrop` and `SulfurChunkDrop2`.
- **Recommended names:** `Sulfur` (hero), `SulfurBlock` (Sulfur Chunk), `SulfurHostTop`, `SulfurHostBase`,
  `SulfurFootRock` (Base Rock). A repo grep found none of these elsewhere. Record the reason here, as M011 and M012 did.
- Palette keys: `m013_*` (no clash).

## 8. Pitfalls to avoid

1. **Two slabs instead of three strata.** The hero shows three horizontal strata with dark seam grooves; Host Rock
   (Base) is two of them, fused.
2. **Elliptical hull slabs.** A 10-point ellipse reads as a smooth pebble or a lens. Use 14–16-point rounded lozenges
   with broad sector jitter, a top chamfer band, faceted walls and an undercut.
3. **A flat, un-tiered top.** The brick must sit on the lower front-right shelf, with the back-left terrace about
   0.35 higher, and the right-end knob behind the brick.
4. **Flush strata.** Offset each stratum's outline 0.2–0.6 so the sides show stepped ledges. The top slab overhangs at
   the back.
5. **Crystal or plain-box chunks.** Chunks are long chamfered blocks with broad bevels (about 22 %), slightly broken
   faces and a flat bottom; no points, no spikes, no perfect boxes.
6. **Chunks sunk too deep.** Their lower chamfer row must show above the rock (Detail A); sink about 0.1.
7. **Chunks not from the part.** The hero chunks and base rocks must be copies of the finished part meshes.
8. **Base rocks round the whole back.** None at the back centre or the front centre; seven in all (§3.4). Don't push
   them so far out that W exceeds about 10.6.
9. **Colour by facing, or noise-threshold patches.**
   - The draft paints sulfur-shadow faces where `noise > 0.35`, which gives random hard patches, and blends the host
     with `steps=1`. Both break STAGES rule 4.
   - Use the §5.6 fields, steps 3, with in-between keys.
10. **White or lemon-white sulfur.** The p95 is #FEF76C. Keep specular low and roughness about 0.55–0.6.
11. **A greenish shadow.** The olive is darker yellow at hue 49–50°, not a green. Calibrate to #C8AC2A.
12. **Grey, cold rock.** The rock renders warm mauve-grey (hue 16–21°). Calibrate on the warm targets; the cool key is
    only for broad patches.
13. **Yellow staining or glow on the rock.** Not on the sheet.
14. **Thin faces.** Bevel strips on the chunks and chamfer bands on the slabs: keep their triangles above 5°, splitting
    long chamfer strips at the wall-facet stations, as M012 did.
15. **Inventing VFX.** No vapour or glints (§6).

## 9. The draft builder (`m013.py`) judged against the sheet

**Keep:**
- the four-part split;
- the corner-chamfered convex-hull chunk idea, `a._finish`, the 24 corner points;
- `BASE_RINGS` for the base rocks;
- `keep_bottom=True` hull rocks;
- `m004.floor_cut`;
- the `M.mk` / `union_loose` / `finish` / `views` flow;
- the chunk positions, which are within about 0.5 of §3.1.

**Change:**
- **Slabs:**
  - 2 → 3 strata (`SLABS` has only Base 10.2 × 7.6 × 1.9 and Top 9.0 × 6.6 × 1.7).
  - The top slab is too small against the base; on the sheet it is about as large and overhangs at the back.
  - 10–11 points per ring → 14–16.
  - No terrace, step or knob.
  - `SLAB` rings ((0, 0.94), (0.25, 1.0), (0.75, 0.99), (1, 0.86)) are close to §3.2's; keep the idea.
- **Chunks:**
  - Built independently per seed; the hero must paste the part.
  - The tall block's 2.9 H is too short (§3.1: 3.6).
  - Sunk 0.35 → about 0.1.
  - No face bulge points: faces come out as single flat octagons, slightly too machined.
  - The noise-threshold shadow patches must go.
- **Base rocks:**
  - 8 placed evenly round, including (+1.2, +3.8) at the back centre, which the rear view rules out.
  - Use §3.4's seven.
  - The current spread makes W about 11.9 against the target 10.4.
- **Sizes:** the draft hero is about 11.9 W × 9.4 D × 6.0 H; the target is 10.4 × 8.8 × 7.0.
- **Colour:** an uncalibrated palette; hard random patches; host blend `steps=1`. Replace with §5.
- **Names:** two clash with R02 (§7).

## Correction (main session, 2026-10-28): side-view direction

The kit's side camera (`VIEWS["side"]` = azimuth 90) sits at +X and looks along −X with Z up, so screen right is +Y: the model's BACK (fronts face −Y). Wherever this spec says the side view's right is the front, read it mirrored. Stage 1 should confirm this with a probe render before using side-view numbers. The 3D layout is unaffected.

## Stage 1 — Modelling

`m013.py` was rewritten from scratch (only the draft's four-part split, the 24-point chamfered hull idea and
`m004.floor_cut` survive). `build()` makes, in `FlintbornWorldKit.blend` under `Kit/M013 Sulfur`:

| Object | Part (sheet) | Builder | How |
| --- | --- | --- | --- |
| `Sulfur` | hero | `hero()` | pasted from the finished parts (`m011._paste`), `M.union_loose`, floor-cut at the ground, cleanup passes |
| `SulfurBlock` | Sulfur Chunk (reusable) | `block()` | hull of 24 corner-chamfer points (every edge bevelled 22 % of its side, corner triangles; corner groups shifted ±4 % so faces break), two gentle bulge points per side face and a short top ridge (7°), `dissolve_limit` 3°, BEAUTY |
| `SulfurHostTop` | Host Rock (Top) | `host_top()` | shelf slab + raised back-left terrace slab + right-end knob dome, unioned |
| `SulfurHostBase` | Host Rock (Base) | `host_base()` | base-upper slab + plinth slab, unioned (the dark groove between them is their chamfer and undercut) |
| `SulfurFootRock` | Base Rock (reusable) | `foot_rock()` | `K.hull_rock`, squat dome rings with a 5-point flat-ish top |

Naming: `SulfurChunk` / `SulfurBaseRock` belong to R02, so the parts are `SulfurBlock` / `SulfurFootRock` (main-session
decision; all five names were free before the build).

**Strata (`slab()`)**: not hulls but explicit lofts of four rings on a 14–16-point superellipse lozenge outline
(broad sector jitter, never per point): a bottom ring inset 0.3 (the undercut, reaching the wall 0.25 up), two wall
rings that wander ±0.1 in plan and ±0.08 in height (each wall facet leans its own way), a top ring inset 0.36 over the
top 0.3 (about a 40° chamfer). Caps are fanned from their centres (no slivers across a 16-gon). Concave lobes are
allowed: the top slab carries a front-right lobe, the plinth a front-left one.

**Layout used (build frame, front −Y, ground z 0)**, changed from §3.5 where the renders asked for it:

| Piece | Centre (x, y) | z | Plan | Yaw | Change from §3.5 |
| --- | --- | --- | --- | --- | --- |
| Plinth | (−0.4, 0.05) | 0 – 1.15 | 9.1 × 7.7, exp 3, lobe front-left | −3° | thinner, offset left |
| Base upper | (−0.25, 0.25) | 1.05 – 2.1 | 9.4 × 7.5 | +5° | lower, further left |
| Top slab: shelf | (0.4, −0.3) | 2.0 – 2.8 | 9.6 × 7.3, lobe front-right | −10° | 0.3 lower, pushed forward and right |
| Top slab: terrace | (−0.9, 0.95) | 2.6 – 3.15 | 6.6 × 4.7 | −8° | 0.3 lower (the 0.35 step kept) |
| Top slab: knob | (4.15, 0.75) | 2.4 – 3.35 | 2.0 × 2.2 dome | — | a faceted dome, not a slab |
| Tall block | (0.15, 1.2) | bottom 3.05 | 4.0 × 3.1 × 3.9 | +15° | taller (top 6.95) |
| Brick | (1.65, −1.2) | bottom 2.7 | 4.6 × 3.0 × 2.95 | −12°, part mirrored | 0.25 left, larger |
| Left chunk | (−2.6, 0.3) | bottom 3.0 | 2.7 × 2.5 × 2.6 | +30°, part turned 90°, tilted 6° to −X | larger |
| Nugget | (3.55, −2.6) | bottom 2.7 | 1.05 × 0.95 × 0.6 | +40°, turned and mirrored | — |
| Foot rocks (7) | §3.4, the end rocks pulled in: front-left (−3.95, −2.75), right (4.5, 1.1) 1.7 wide, back-right (3.8, 3.1), back-left small (−4.35, 2.6) | sunk 0.1, floor-cut | §3.4 sizes | varied | none at the back or front centre |

- Why the stack went 0.35 lower and the blocks taller: at the sheet's camera elevation (renders at 11°) the first
  layout put the sulfur's lowest point at 0.49 H (sheet 0.38) and the sulfur at 37 % of the silhouette (sheet
  42–46 %).
- Why the end rocks moved in: the §3.4 spread made the hero 11.1 wide (target 10.4 ± 0.4).
- Blocks sit 0.1 into their slab top (terrace 3.15, shelf 2.8), so their lower bevel row shows (Detail A).
- Seat check (`_seats`): the tall block, brick and nugget bottoms lie fully on their tops; the tilted left chunk's
  bottom corner is 0.12 past the terrace's top outline (it rests over the terrace chamfer; no gap shows in any view).

**Cleanup done in stage 1** (so the numbers below hold): `union_loose`, `m012._drop_inner`, `m011._clean` with the
ground / shelf / terrace planes locked, `m012._force_slivers`, `_finish` (M.finish plus repairs), `_polish` (all
triangles, corners opened past 5°, bottom-centre origin, UVs: Smart UV 45° islands re-unwrapped angle-based, margin
0.008, overlaps cut free) and `_seal`. `_seal` exists because the sliver collapses left one flap and pinhole on the
hero where a foot rock meets the plinth groove; it removes the flap and fills the hole. Part offsets into the build
frame are stored as `m013_offset`.

**Placeholder colour keys** (the uncalibrated §5.5 targets; stage 4 calibrates and blends): `m013_sulfur` (blocks),
`m013_host` (top slab), `m013_host_dark` (base strata), `m013_base` (foot rocks). `m013_sulfur_shadow` is defined but
unused: a bottom-row placeholder tripped `K.check`'s facing test (the bottom row faces down), so stage 4 places it by
position fields.

### Measured (final build)

| Object | Tris | Size (studs) | Shells | Non-manifold / boundary | n-gons | Smallest corner |
| --- | --- | --- | --- | --- | --- | --- |
| Sulfur (hero) | 1540 / 4000 | 10.66 × 8.88 × 6.95 | 1 | 0 / 0 | 0 | 5.0° |
| SulfurBlock | 58 / 1000 (41 planes before triangulation) | 4.01 × 3.13 × 3.28 | 1 | 0 / 0 | 0 | 15.1° |
| SulfurHostTop | 320 / 1000 | 9.70 × 7.85 × 1.35 | 1 | 0 / 0 | 0 | 3.6° |
| SulfurHostBase | 310 / 1000 | 9.90 × 7.78 × 2.10 | 1 | 0 / 0 | 0 | 5.3° |
| SulfurFootRock | 42 / 1000 | 2.16 × 1.98 × 1.50 | 1 | 0 / 0 | 0 | 20.9° |

All normals outward; `K.check` reports no problems. Target 10.4 × 8.8 × 7.0 (W ±0.4, D ±0.5, H ±0.3): all within.

Silhouette numbers use the §1 masks on our renders; the rock mask also needs sat > 0.17 there, so the floor shadow
drops out. The sheet column is the same masks on the sheet (first number) and the §1 table (second).

| Our view (azimuth, elevation) | Sheet view | W : H ours / sheet | Sulfur share ours / sheet | Sulfur lowest point (H) ours / sheet |
| --- | --- | --- | --- | --- |
| front34 (−28, 12) | front three-quarter | 1.22 / 1.39–1.42 | 0.40 / 0.38–0.41 | 0.50 / 0.40 |
| r34_sheet (+28, 12) | "rear three-quarter" | 1.23 / 1.30–1.31 | 0.40 / 0.36–0.41 | 0.43 / 0.36 |
| front_el11 (0, 11) | front | 1.34 / 1.31 | 0.41 / 0.42–0.46 | 0.45 / 0.38 |
| side_el11 (90, 11) | side (mirrored) | 1.07 / 1.10–1.11 | 0.43 / 0.39–0.44 | 0.43 / 0.35 |
| rear_el11 (180, 11) | rear | 1.26 / 1.30–1.32 | 0.44 / 0.31–0.32 | 0.48 / 0.46 |
| top (0, 89) | top | — | 0.57 / 0.45 | — |

**Side-view direction (the correction above): confirmed.** The kit's side render (azimuth 90) shows the brick at
screen LEFT and the tall block at the right. The sheet's side view has the brick at the right, so it is the mirror of
the kit's (or a view from −X). Compare `side.png` / `side_el11.png` mirrored, or `side_left_el11.png` (azimuth −90).

### View by view

- **Front three-quarter:** three chamfered blocks in a row (cube-ish left chunk, tall block behind, long brick at the
  front right), the nugget at the brick's front-right foot, three strata with grooves, the front-left / centre / right
  foot rocks, as on the sheet. Ours reads narrower (W : H 1.22 against 1.4) and the pile sits a little higher on the
  rock.
- **"Rear three-quarter" (r34_sheet, azimuth +28):** the brick's front face dominant, the nugget at its foot, the left
  chunk at screen left, the tall block behind, the knob behind the brick's right end, the right-side foot rocks. Matches.
- **Front (11°):** W : H matches; sulfur span 0.13–0.92 of W (sheet 0.13–0.90); the brick's top falls to the right.
- **Side:** the strata step out, the top slab overhanging at the front. The knob shows between the brick and the tall
  block a little more than on the sheet.
- **Rear:** the tall block centred, the two side chunks either side, rock rising between them; the top slab widest.
  The sulfur share from behind (0.44) is higher than the sheet's 0.31: the sheet's back terrace and slab hide more of
  the blocks.
- **Top:** left chunk, tall block (back) and brick (front right) laid out as on the sheet; the rock rim widest at the
  left and back-left. Our footprint is more oval (1.27) than the sheet's near-round one (0.99, which §4.4 puts down to
  a tilted camera), and the chunks cover more of it (0.57 against 0.45).
- **Underside:** one broad flat base, a chamfer band, the foot rocks at the edge.
- **Exploded:** three block variants (temporary linked copies at the hero's tall / left / brick placements) over the
  top slab (step line and knob visible), over the fused base strata, a foot rock in front.

### Left for later stages

- Stage 2: `SulfurHostTop`'s smallest corner is 3.6° (above 3°, under the 5° polish target); everything else is at
  least 5°.
- Possible stage-1 follow-ups if the verifier asks: the rear view's sulfur share (raise the back of the terrace, or set
  the side chunks lower), the front three-quarter's W : H (a wider, lower pile), the top view's covered share.
- Stage 4: all colour (`m013_sulfur_shadow` by a position field; the strata grade; the seam grooves). Stages 5 and 6:
  nothing on the sheet (§6).

## Stage 2+3 — Cleanup and UV

All changes are in `m013.py`; the model was rebuilt with `m013.build()` in the open `FlintbornWorldKit.blend`, which was then saved.

**Stage 2 changes**

- **The 3.6° corner on `SulfurHostTop` came from the terrace.** The 3.6° needle lay on the flat shelf top, between
  two crease verts 0.19 apart and a front shelf-ring vert 3.06 away. A terrace wall-ring vert sat 0.006 above the
  shelf plane, so the collapse failed the link condition (three shared neighbours). No near-flat flip opened it
  (`m009._flip_thin`: 0 flips), and opening it with a nudge would have needed a 0.08 move. The cause was that the
  terrace's lower wall ring (2.72–2.81) straddled the shelf top (2.8). **Fix:** `TERRACE` bottom 2.6 → 2.5, so that
  ring (now 2.64–2.75) is buried in the shelf. The outline seed sequence is unchanged, so the outline and the visible
  step (2.8 → 3.15) are the same; the terrace's wall/chamfer break moves 0.035 lower.
  - Shape check against the round-2 mesh (BVH, nearest surface): the largest vertex shift is 0.12 studs (old to
    new) and 0.07 (new to old).
  - The only geometry that changed is the terrace wall above the shelf, which the blocks mostly cover.
  - Hero and part bounding boxes are identical to three decimals (hero 10.655 × 8.885 × 6.95). The renders read as
    before.
  - `SulfurHostTop` now cleans with no slivers left and needs no forced polish (smallest corner 5.0°).
- **`_seal` was fixing a real defect, at the wrong point; it is replaced.** Tracing the hero step by step:
  - The mesh was manifold after paste, `union_loose`, `floor_cut` and `_drop_inner`.
  - `m011._clean` then made one edge with four faces (0.013 long, at (−1.80, −3.05, 1.15), where the front-centre
    foot rock grazes the plinth / base-upper groove).
  - The union had left an **ear** there: a vert on two edges whose faces were a 7e-5 sq-stud triangle and the
    hexagon wrapped round it.
  - `_clean`'s two-edge dissolve skips verts with a triangle face. Its BEAUTY triangulation then clipped that ear a
    second time, which put four faces on one edge.
  - `M.finish`'s `repair_nonmanifold` deleted the two smallest faces, which left a 4-edge pinhole that `holes_fill`
    could not close. `_seal` filled it at the very end.
  - **Fix:** `_dissolve_ears()` runs first in `_clean_mesh` (hero and both strata parts). It dissolves such verts,
    merging the speck into its n-gon; the surface moves under 0.015.
  - The hero now has 0 non-manifold edges and 0 holes at every step. `_seal` is deleted. `m011._clean` also leaves
    fewer slivers and specks: 1 / 0 now, 3 / 4 before.
- Nothing else needed changing.
  - The tris are far under budget (hero 1540 / 4000), so no reduction was needed.
  - The existing passes already met every 2c check: `union_loose`, `_drop_inner`, `m011._clean`,
    `m012._force_slivers`, `_finish`, `_polish` (`m012._tri_quads`, corners ≥ 5°, bottom-centre origin with the
    offset following) and `_drop_unused`.

**Stage 3 changes**

- `UV` gains `min_angle` (= the island angle, as M009), so `smart_uv` never falls back to lower angles. Folds are
  cut free by `m012._uv_unfold` instead.
- Island angle per object (`UV_ANGLE`, via `_uv(o)`): I compared 40° and 45° ANGLE_BASED and kept, for each object,
  the one with the lower worst conformal stretch.

  | Object | Worst conformal stretch, 40° | Worst conformal stretch, 45° | Chosen |
  | --- | --- | --- | --- |
  | Hero | 1.035 | 1.234 (one fold cut, 5.9° worst angle change) | 40° |
  | `SulfurHostBase` | 1.000 | 1.041 | 40° |
  | `SulfurHostTop` | 1.081 | 1.021 | 45° |
  | Block | equal | equal | 45° (fewer islands) |
  | Foot rock | equal | equal | 45° (fewer islands) |

- Also tried on the hero: 50° (1.234 worst, 1.051 p95), CONFORMAL 45° (2 overlaps, 1.341) and plain Smart UV 45°
  (1.375 worst, 1.214 p95). All were worse.

### Measured (MCP, after the final build)

| Object | Tris / budget | Verts | Size (studs) | Shells | Non-manifold edges / verts | Boundary | Wire | Loose | Zero-area | Dup verts | n-gons | Self-intersections | Normals | Smallest corner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sulfur (hero) | 1540 / 4000 | 766 | 10.66 × 8.88 × 6.95 | 1 | 0 / 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | outward | 5.0° |
| SulfurBlock | 58 / 1000 | 31 | 4.01 × 3.13 × 3.28 | 1 | 0 / 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | outward | 15.1° |
| SulfurHostTop | 324 / 1000 | 164 | 9.70 × 7.85 × 1.35 | 1 | 0 / 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | outward | 5.0° (was 3.6°) |
| SulfurHostBase | 310 / 1000 | 157 | 9.90 × 7.78 × 2.10 | 1 | 0 / 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | outward | 5.3° |
| SulfurFootRock | 42 / 1000 | 23 | 2.16 × 1.98 × 1.50 | 1 | 0 / 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | outward | 20.9° |

**The 2c checks below hold for all five objects.**

- **Faces and shading:** all faces are triangles (0 quads, 0 n-gons), flat shaded, with no custom split normals.
- **Object setup:** no modifiers, no parent, no children. Rotation is (0, 0, 0) and scale is 1.
- **Origin:** the bounding-box bottom centre, offset (0, 0, 0). The parts' `m013_offset` follows each re-centring.
- **No interior faces:** each mesh is one closed manifold shell with no self-intersections, checked by BVH
  triangle overlap between faces that share no vert. So there is no room for interior faces or inner shells;
  `_drop_inner` found 0 pockets.
- **`K.check`:** no problems reported.
- **Unused data:** `_drop_unused` purged the 20 orphaned M013 meshes from the rebuilds. No orphaned `Sulfur*` or
  `m013` meshes are left, and there are no M013 images and no `_m013_*` temporary objects.
  - Materials: `FB_m013_base`, `FB_m013_host`, `FB_m013_host_dark` and `FB_m013_sulfur` are each used by the hero
    and one part.
  - `m013_sulfur_shadow` does not exist as a material: `palette()` defines it but no face uses it, and the purge
    removes it. Stage 4 places it.

### UV (`M.uv_stats`, layer `UVMap`, after the final build)

| Object | Angle | Islands | Overlaps (cross-island) | Flipped | Min gap / border | Density min / med / max | Conformal worst / p95 | Area worst | Angle change worst | Texels / stud @1024 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sulfur (hero) | 40° | 316 | 0 (0) | 0 | 0.016 / 0.008 | 1 / 1 / 1 | 1.035 / 1.000 | 1.019 | 1.88° | 27.4 |
| SulfurBlock | 45° | 14 | 0 (0) | 0 | 0.016 / 0.008 | 1 / 1 / 1 | 1.015 / 1.012 | 1.007 | 0.81° | 99.3 |
| SulfurHostTop | 45° | 59 | 0 (0) | 0 | 0.016 / 0.008 | 1 / 1 / 1 | 1.021 / 1.002 | 1.013 | 1.20° | 54.8 |
| SulfurHostBase | 40° | 39 | 0 (0) | 0 | 0.016 / 0.008 | 1 / 1 / 1 | 1.000 / 1.000 | 1.000 | 0.00° | 45.6 |
| SulfurFootRock | 45° | 10 | 0 (0) | 0 | 0.016 / 0.008 | 1 / 1 / 1 | 1.053 / 1.049 | 1.043 | 2.65° | 199.3 |

- **Margin:** 0.008 round every island, so the gap between islands is 0.016, well above the skill's 0.002 minimum.
- **Unfold:** no faces needed cutting free by `_uv_unfold` in the final build.
- **Exporter:** the GLB exporter writes its own palette UVs; this layer serves FBX/OBJ and texture work.

### Left for later stages

- Stage 4: all colour (unchanged from stage 1's list).
- The tilted left chunk's seat is still 0.12 past the terrace's top outline (as in stage 1; no gap shows).

### Self-intersection fix (after verifier round 2)

The tables above predate the stage-1 re-layering of the strata (plinth 0–1.0, base upper 0.95–1.9). On that layout,
the hero had 3 crossing face pairs, each 0.2–0.3 deep, at (4.1, 1.6, 1.0) and (4.2, 0.9, 1.1).

**Cause, traced step by step.** The hero had 0 crossing pairs after the union, the floor cut, `_clean_mesh` and
`_finish`. All 3 appeared in `_polish`, in `m012._force_slivers`' last-resort `_nudge`.
- The right foot rock (4.5, 1.1), at yaw 110°, grazed the base-upper undercut at about z 1.3 with one upper facet.
  That left a 3° needle in the narrow crevice.
- The nudge opened the needle by moving a corner, but it checks only the turn of the faces round that corner, not
  the facing wall. The moved corner went through the groove's wall.

**Fix.** The rock's yaw went 110° → 125°. Turned 15°, it meets the groove with no needle, so there is nothing to
nudge. Its place and size, and the hero's bounds (10.66 × 8.88 × 6.95), are unchanged, and the side render reads the
same.
- I tried the alternatives the same way: rock out 0.2 or 0.3 (also 0 crossings, but the hero 0.1–0.2 wider) and the
  rock 1.1 tall (0 crossings).
- `build()` now runs `_self_hits()` on every object. It is the BVH triangle-pair test as `m009._self_hits`, and any
  crossing pairs are added to `problems`.

**Re-measured after `m013.build()`, with stage 4 colour applied.**

| Object | Tris | Crossing pairs | Non-manifold / boundary | Shells | Smallest corner | UV overlaps / worst conformal |
| --- | --- | --- | --- | --- | --- | --- |
| Sulfur | 1510 | 0 | 0 / 0 | 1 | 5.0° | 0 / 1.049 |
| SulfurBlock | 50 | 0 | 0 / 0 | 1 | 13.4° | 0 / 1.007 |
| SulfurHostTop | 314 | 0 | 0 / 0 | 1 | 5.0° | 0 / 1.019 |
| SulfurHostBase | 302 | 0 | 0 / 0 | 1 | 5.2° | 0 / 1.024 |
| SulfurFootRock | 42 | 0 | 0 / 0 | 1 | 20.9° | 0 / 1.053 |

`K.check` and `problems` are both clean, and the colour pass ran.

## Stage 4 — Materials, colour and texture

All changes are in `m013.py`:
- `palette`, `TARGETS`, `calibrate`, `_drop_calib` and `_sulfur_spec`;
- the "stage 4" constants;
- `_Inst`, `_instances`, `_block_bvhs`, `_seam_tree`, `_tint`, `colour` and `SHADING_OK`;
- the colour step in `build()`.

Geometry and UVs are untouched: `colour()` only rewrites the face keys and the Tint layer on the finished meshes. The
hero and part audits are identical to stage 2+3 (hero 1540 tris, 10.66 × 8.88 × 6.95, one shell, 0 non-manifold,
0 boundary). `FlintbornWorldKit.blend` was rebuilt with `m013.build()` and saved.

### Keys and calibration

The targets are the sheet's rendered medians (§5.2 / §5.5), not the swatches. Two passes:

1. **Dome.** `m013.calibrate()` wraps `K.calibrate` as M009's does:
   - stone keys are sampled unfiltered (`M.sample(..., "all")`);
   - the sulfur keys are held at specular 0.3 every round;
   - the orphaned `T_Calib` meshes are purged afterwards (none left).

   Every key rendered on the dome within 2 levels of its target. The light key needed a second run from a scaled
   start: its first run oscillated on the clipped red channel.
2. **Hero.** On the hero, the dome hexes rendered 1.3–1.4× too dark in linear light: sulfur median #D2B929 against
   #F1D330, top-slab wall #908480 against #A8978E. (The dome's top faces the sun; the hero's walls and block sides
   don't.)
   - Each key was corrected in linear light by sheet ÷ hero: the geometric-mean gain over the §5.2 regions of the
     front three-quarter, front (11°), side (az −90, 11°) and top views.
   - The rear view is lit by the fill only, so it is reported, not fitted.
   - Three rounds, each render masked by an alpha pass (floor hidden, transparent film).

| Key | Target (sheet as rendered) | Dome-calibrated → dome render | **Final hex** | Role |
| --- | --- | --- | --- | --- |
| `m013_sulfur` | #F0D230 | #B4A420 → #EFD330 | **#C8B221** | the block body |
| `m013_sulfur_light` | #F8E04A | #BBAE3A → #F9E048 | **#C2C155** | the crest band, fitted to the top view's lit faces (#FBF465 against #FEF168) |
| `m013_sulfur_shadow` | #C8AC2A | #97871B → #C7AC2C | **#C3A92F** | low on each block, in the crevices and at the rock: a little darker and more olive than the body (hue 51°, sat 0.76 against 53°, 0.83) |
| `m013_host` | #9B8B84 | #736B6B → #998A83 | **#857976** | the top slab |
| `m013_host_cool` | #8E8584 | #6A676B → #8D8583 | **#7B7576** | broad cool weathering patches |
| `m013_host_dark` | #776862 | #595050 → #776863 | **#4E4645** | the lower strata, seams and underside |
| `m013_base` | #94817B | #6E6464 → #92817B | **#786D70** | the 7 foot rocks |

The in-between keys (`*_x_*_25/50/75`; 24 keys in all on the hero) come from `K.mix_key`.

### Method (all position fields, never facing)

`colour(o)` runs in `build()` on the hero first (it was pasted from the parts' placeholder keys), then on each part,
with the same fields. A face's region comes from the builder's key: sulfur; host = top slab; host dark = base strata
(base upper above z 1.1, plinth below); base = foot rocks.

**Sulfur.** Each face is mapped back into its block's own part frame: the nearest of the hero's four
`_block_matrix` copies by box norm, or the identity for `SulfurBlock`. So the part and its hero copies carry the same
grading.
- u = height fraction in the block + 0.12 × broad noise (scale 0.5, per-copy offset) + 0.1 × the position along the
  long axis.
- Shadow → sulfur over u 0–0.22 (100 / 75 / 50 / 25 %). Sulfur → light over u 0.82–0.97.
- Occlusion, by the distance to the hero's rock surface or to another block (BVH; for the lone block, its contact
  plane): full shadow within 0.05, 50 % at 0.2, none past 0.45.
- The shadow mix is the larger of the height term and the occlusion term.

**Rock.**
- **Strata grade** towards host dark: top slab 0; base upper 25 %; plinth 50 % at z ≥ 0.9 to 75 % at z ≤ 0.5 (z plus
  0.12 × noise).
- **Seams:** by distance to each stratum's undercut ring (the shelf's at z 2.0, the base upper's at 1.05;
  `_seam_tree`). Full host dark within 0.2, fading out by 0.5: the dark groove lines.
- **Weathering:** host ↔ host cool by broad noise (scale 0.2, level 0.45, width 0.5, so at most 75 %), only where a
  face is at most 25 % dark.
- **Foot rocks:** the crown (above 0.7 of the rock's height) goes 25 % towards host, so it blends into the slab walls.
  The contact row (below 0.22) goes 25 % towards host dark.
- Sulfur against rock is a hard edge (separate keys). There is no yellow on the rock.

**Tint.**
- Per-piece levels: blocks 0.97–1.02, strata 0.98–1.0, foot rocks 0.96–1.03.
- Times broad mottling: rock amp 0.055, scale 0.45; sulfur amp 0.03, scale 0.9, in block-local coordinates.
- Plus ±1–1.5 % per-face jitter.
- Result: hero Tint 0.90–1.09 (sd 0.029), calm patches with no confetti, within the exporter's 0.05 row tolerance at
  32 levels.

**Finish.** Sulfur: roughness 0.58, Specular IOR Level 0.3 on every sulfur key, mix keys included (`_sulfur_spec`),
metal 0. Rock: roughness 0.92, metal 0.

**K.check** reports no problems.
- The sulfur's facing correlation is 0.29 on the hero, and the block is under the gate.
- The rock strata correlate at 0.67 (hero) and 0.69 (`SulfurHostBase`): the darker stack sits low, and the top slab's
  lit top is the upper stratum.
  - This is waived with the reason in `SHADING_OK`, as M011 did. The sheet's exploded base, with nothing over it,
    renders darker than the exploded top slab.
  - Ending the plinth ramp at 75 %, so the underside is not full dark, took it from 0.72 to 0.67.

### Target against got

Sheet regions from §5.2; ours are the same boxes mapped through each view's model bbox. Each cell is median / lit
quartile / shade quartile.

| Region | Sheet | Ours |
| --- | --- | --- |
| Sulfur, front three-quarter, all chunks | #EBCA2D / #FDEF63 / #BFA324 | #EBCB28 / #FFE842 / #B0951E |
| Sulfur, front three-quarter, tall block | #F1D22E / #FDED5B / #C6A91E | #F1CE2C / #FFEB42 / #D4B325 |
| Sulfur, front three-quarter, brick top | #FDEF5B / #FEF877 / #EBC823 | #EFCD27 / #F6D328 / #E7C623 |
| Sulfur, front three-quarter, brick front | #D3B72B / #F2D534 / #B49B27 | #EAC925 / #EFCD27 / #7D6A19 |
| Sulfur, front three-quarter, left chunk | #C1AB31 / #FCED67 / #AD9729 | #EBC927 / #FFE63F / #D8B920 |
| Sulfur, front | #F1D330 / #FDEE5F / #BBA42A | #EBCA2A / #FFEA44 / #95801A |
| Sulfur, side | #ECD134 / #FDF15F / #C3AB2B | #E0C032 / #FFE84A / #9B861C |
| Sulfur, rear (lit by the fill; not fitted) | #EED333 / #FDEE62 / #C1A622 | #C5B028 / #DDC336 / #9B861C |
| Sulfur, top | #F7DE43 / #FEF168 / #BAA228 | #FAEB4F / #FBF465 / #D4C037 |
| Host, front top-slab wall | #A8978E / #C1AFA6 / #686263 | #A7968D / #AF9D96 / #85756D |
| Host, side top slab | #988B87 / #C2B0A7 / #686365 | #93837A / #AF9D95 / #594E49 |
| Host, rear top slab | #91827C / #BEAAA0 / #6B6361 | #827571 / #8F817D / #5B524E |
| Host, top-view rim | #9A887E / #C1B3AD / #645C5A | #9F928B / #AA978F / #665B57 |
| Host, front three-quarter, all strata | #7F716B / #BDABA3 / #544B48 | #907F79 / #AB9B94 / #5F5450 |
| Lower strata, front | #7A6C66 / #B5A098 / #514945 | #776861 / #968480 / #3B3431 |
| Lower strata, side | #776861 / #BBA69F / #4D4642 | #81726A / #9B8980 / #5C524E |
| Lower strata, rear | #75655D / #96847E / #584E4A | #645A57 / #7B6E6B / #4B4342 |
| Foot rock, front three-quarter, left | #9B847D / #B49D97 / #756862 | #907E7B / #A6928E / #695C59 |
| Foot rock, front three-quarter, centre | #8C7D7B / #B9A59E / #6A5C56 | #92807D / #958380 / #776861 |
| Foot rock, front | #8B7D7A / #BDA9A2 / #5E5451 | #91807C / #958380 / #524848 |
| Exploded top slab | #8A7E7C | #A69891 |
| Exploded base strata | #756A68 | #85756D |
| Exploded chunks, all | #EFD033 / #FEF369 / #B89D1E | #ECCA27 / #FFE73E / #9E891C |

**Sulfur by height band** (the view's model bbox in fifths, top band first; sheet → ours):

| View | Sheet | Ours |
| --- | --- | --- |
| Front three-quarter | #F4D835 #E8C72C #DBC02A | #F5E140 #EBCA27 #B49A22 |
| Front | #F9DD3C #F2D230 #E7CA2E | #F5E243 #ECCA2A #BB9F21 |
| Side | #FAE344 #EBD033 #E3CA31 | #F2DD3A #DFBF2E #AC9422 |

**Hue checks.**
- Sulfur medians: 50–51° at saturation 0.80–0.83 (sheet 49–50°, 0.79–0.83).
- The olive shade is the same hue, not greener.
- Rock walls: 19–21° at saturation 0.15 (sheet 21°, 0.15).
- Nothing renders white: the brightest sulfur decile is #FFF35C.

### What is left, and why

- **Medians:** within about 6 levels in every fitted view, for the sulfur body, the top slab, the lower strata and
  the foot rocks.
- **Lit quartile:** the sheet's is paler (bluer) than ours on the block sides. That is the sheet renderer's highlight;
  our top view's lit faces already match.
- **Shade and the bottom band:** ours are darker than the sheet's (bottom band #B49A22 against #DBC02A).
  - The cause is the studio's shade on the down-facing bevels, plus cast shadows.
  - A test with every shadow key set to the body colour moved that band by under 2 levels. Paint cannot lift it
    without painting inverse light.
- **Cast shadows:** the sheet's left chunk (#C1AB31) and brick front (#D3B72B) sit in its light's cast shadow; ours
  are lit. That is lighting, so it is not painted.
- **Rear views:** the rear and the "rear three-quarter" (az +28) read 15–25 levels darker on the lower strata. Only the
  fill light reaches them there; the paint is fitted to the front-lit views.
- **Seam, front three-quarter left** (sheet #56504F, ours #998880): the mapped box lands on the base-upper wall, not in
  the groove. The stratum outlines differ from the sheet's there (geometry, stage 1). Our grooves are painted full host
  dark.
- **Exploded strata:** our exploded top slab and base render lighter than the sheet's (#A69891 / #85756D against
  #8A7E7C / #756A68), because the sheet's exploded shot carries more shade. The top-to-base step goes the same way.

### Stages 5 and 6

Nothing found in stage 4 changes §6.
- **No emissive sulfur:** the shade faces drop to olive (darkest decile #7F6B1B), and a Neon part would flatten them.
- **No `ore_glint`:** the finish is matte and waxy (roughness 0.58, specular 0.3).
- Skip stage 5 ("sheet shows no emissive parts or glow") and stage 6 ("no fumes, dust or sparkle").

### Stage 1 fixes (after verifier round 1)

Verifier round 1 scored the model 6/10: the technical checks and colour medians passed, the shape failed. The
coordinator's five findings were applied in `m013.py`. Stage 2's `_dissolve_ears`, stage 3's per-object UV angle and
stage 4's colour pass are unchanged, and all ran in the rebuild.

**1. Strata thickness was inverted (a thin top plate on thick lower strata).**
- Plinth 0–1.15 → **0–1.0**; base upper 1.05–2.1 → **0.95–1.9**; top-slab shelf 2.0–2.8 → **1.8–3.0**. The shelf now
  has a 0.65 near-vertical wall band (2.05–2.7) under its 0.3 chamfer.
- `UPPER_Z` (stage 4's split between the base upper and the plinth) 1.1 → 0.97, and the `PLINTH_DARK` ramp
  ((0.9, 0.5), (0.5, 0.75)) → ((0.8, 0.5), (0.45, 0.75)), scaled with the thinner plinth.

**2. The brick stood 1.1–1.5 back from the shelf's front edge.**
- The shelf's top edge bows forward in the middle (y −3.44 at x −1, −3.95 at x 2, −3.27 at x 4). The coordinator's
  y −1.85 with yaw −12 still left the brick's left end 0.6 back while its right end reached the edge. Its overhang also
  showed past the rim in the top view.
- Final: centre **(1.6, −1.95)**, yaw −12° → **−3°**, 4.3 × 2.9 × 2.65 (W : H 1.62), bottom 2.85 (0.15 into the
  shelf). Its front runs along the shelf's edge with the ends at the chamfer, and a narrow strip of shelf shows
  mid-front. Its back still overlaps the tall block's lower front.
- Nugget **(3.85, −3.3)**, bottom 2.75: off the brick's front-right corner, partly buried in it, on the front chamfer.
  Its seat is 0.23 past the shelf's top outline by design.

**3. The back rock didn't rise.**
- The terrace is now (−0.65, 1.0), 7.1 × 4.8, bottom 2.5 (its lower wall ring, 2.67–2.83, stays buried under the
  shelf top 3.0, as stage 2 required).
- Its top is one plane tilted up towards the back (`slab(..., rise=TERRACE_RISE)`, 0.05 per stud at plan angle 82°):
  **3.6 at the centre, about 3.5 at the front edge, 3.7 at the back**. `terrace_z()` gives its height anywhere.
- It was made 0.5 wider to the right so the tall block's footprint stays on it. With the terrace top no longer level,
  the stage-2 plane lock now holds only the shelf's bottom and top.
- Knob lifted with the slab: (4.15, 0.75), 2.55–3.6.

**4. The tall block was cube- or ball-like.** Now 4.2 × 2.9 × 3.43 (W : H 1.22), bottom 3.52 on the terrace, top
6.95. Its centre moved y 1.2 → 0.95: it was 0.3 deeper than needed and, together with the brick, covered 0.63 of the
top view (sheet 0.45). The left chunk is (−2.25, 0.7), 2.7 × 2.5 × 2.3 (W : H 1.17), bottom 3.4, its top 5.78 (0.83 of
the tall block's, as in the sheet's front view).

**5. The blocks read as faceted gems.** `BLOCK` bevel 0.22 → **0.15**; side bulges 7° → **4°**; top ridge 7° →
**3°** (`bulge_top`). The part now has 34 planes (was 41) and 50 tris; its big faces read flat.

Seat check (`_seats`, now with sink and overhang): every block's flat bottom lies inside its top. Sinks: tall
0.02–0.15, brick 0.15, left 0.08–0.27 (tilted), nugget 0.25. Nothing hangs over the shelf below a terrace edge.

#### Measured after the fixes (MCP, final build)

| Object | Tris / budget | Size (studs) | Shells | Non-manifold / boundary | n-gons | Normals | Smallest corner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Sulfur (hero) | 1502 / 4000 | 10.66 × 8.88 × 6.95 | 1 | 0 / 0 | 0 | outward | 5.0° |
| SulfurBlock | 50 / 1000 | 4.01 × 3.11 × 3.28 | 1 | 0 / 0 | 0 | outward | 13.4° |
| SulfurHostTop | 314 / 1000 | 9.70 × 7.96 × 1.90 | 1 | 0 / 0 | 0 | outward | 5.0° |
| SulfurHostBase | 302 / 1000 | 9.90 × 7.78 × 1.90 | 1 | 0 / 0 | 0 | outward | 5.2° |
| SulfurFootRock | 42 / 1000 | 2.16 × 1.98 × 1.50 | 1 | 0 / 0 | 0 | outward | 20.9° |

- `K.check`: no problems.
- Stage 4's colour pass ran: 24 keys on the hero. The facing correlations are hero 0.63 and `SulfurHostBase` 0.68,
  both waived by `SHADING_OK`.
- `FlintbornWorldKit.blend` saved.

Silhouettes were measured on renders of the hero with the studio floor hidden (no cast shadow). The kit's cameras are
used: the same azimuth and elevation, 480 × 400. Mask: not background (within 14 of #F1E8D8), and sulfur where hue
and saturation say yellow. Sheet values are from the coordinator's / §1 table.

| View (azimuth, elevation) | W : H ours / sheet | Sulfur lowest point (H) before → now / sheet | Sulfur share now / sheet |
| --- | --- | --- | --- |
| front34 (−28, 12) | 1.23 / 1.42 | 0.51 → 0.50 / 0.40 | 0.38 / 0.38–0.41 |
| r34_sheet (+28, 12) | 1.22 / 1.31 | 0.43 → 0.41 / 0.36 | 0.38 / 0.36–0.41 |
| front_el11 (0, 11) | 1.33 / 1.31 | 0.45 → 0.43 / 0.38 | 0.39 / 0.42–0.46 |
| side_el11 (90, 11) | 1.07 / 1.10 | 0.49 → 0.42 / 0.35 | 0.37 / 0.39–0.44 |
| side_left_el11 (−90, 11) | 1.09 / — | → 0.54 | 0.30 |
| rear_el11 (180, 11) | 1.26 / 1.31 | — | **0.33** (was 0.44) / 0.31 |
| top (0, 89) | — | — | 0.59 (was 0.63) / 0.45 |

#### What moved and what did not, and why

- **Rear share is fixed:** 0.44 → 0.33 (target 0.31–0.36). The tilted terrace rises between the blocks in the rear
  view as on the sheet.
- **The sulfur's lowest point dropped only 0.01–0.07.**
  - The thicker top slab raises the rock top by 0.2 (2.8 → 3.0), and the brick's bottom rose with it (2.7 → 2.85).
  - Moving the brick forward lowers it on screen by only about 0.1 stud at 11–12°.
  - On a perspective camera (`FB_Cam`, 50 mm), the stack below the brick's front edge spans 153 px for 3 studs while
    the 4 studs of sulfur above span 163 px. The near, low rock is magnified.
  - Reaching 0.38–0.40 would mean the brick's front sitting about 0.6 below the shelf top. That conflicts with the
    prescribed 1.8–3.0 top slab, unless the shelf's front-right part slopes down (§4.5's fallback, 6–8°). This is not
    done; it is for the coordinator to choose.
- **front34 W : H stays 1.23** (sheet 1.42) while the front matches (1.33 / 1.31).
  - A probe render at az −28 gave 1.22 at elevation 12°, 1.12 at 20°, and 1.19 at az −40 / 15°. No camera or height
    change on our side reaches 1.42.
  - The sheet's three-quarter view is wider than its front (1.42 against 1.31), and its az +28 view is narrower
    (1.30). That needs a footprint elongated from back-left to front-right (yaw about −25° to −30°) seen nearly
    broadside from az −28. Ours is elongated along x (shelf yaw −10°).
  - The likely fix is to turn the whole strata stack, and the layout on it, by about −15° in plan. That changes every
    view, so it is left as a decision for the coordinator.
- **Underside view:** the tall block's top shows past the far edge of the slab from below at −45° / az 20. That is the
  steep camera seeing past the back rim, not an overhang: the block's footprint lies inside the terrace.

### Stage 4 fixes after verifier round 1

These were done on the reshaped stack (the Stage 1 fixes above). Geometry and UVs are unchanged; only `palette()` and
`STRATA_DARK` changed. The model was rebuilt with `m013.build()` and `FlintbornWorldKit.blend` saved. `K.check`
reports no problems. The facing correlation is hero 0.61 and `SulfurHostBase` 0.61, both waived as before. The hero is
1502 tris with 22 keys; no orphaned `FB_m013_*` materials remain.

**What changed.** The verifier's colour notes, and the fix for each:

1. **The sulfur shade quartile was 20–40 levels too dark.**
   - Lower contrast across the sulfur keys: the body went #C8B221 → **#D3C03A** and the shadow #C3A92F → **#D0B53A**.
   - The shadow lifts with the body and stays a slightly darker olive.
   - Both were fitted in linear light on the new shape's front three-quarter, front and side regions.
   - The fields are unchanged and nothing is painted by facing.
2. **The lit sides were mustard** (saturation 0.74 against 0.61).
   - The body's blue went up (#…21 → #…3A).
   - The light key is paler and less saturated: #C2C155 → **#C9C462**.
3. **The front three-quarter's lower rock band was about 12 levels light.**
   - Host dark went #4E4645 → **#443D3D** (×0.77 in linear over the two steps).
   - The base upper now sits 50 % towards host dark, up from 25 %. At 50 % it no longer takes the cool weathering.
   - Turning off the foot-rock crown blend was tested and moved the band under 2 levels, so it was kept.

**Re-measured on the new shape** (median / lit quartile / shade quartile):

| Region | Sheet | Before (verifier) | Now |
| --- | --- | --- | --- |
| Sulfur, front three-quarter, all chunks | #EBCA2D / #FDEF63 / #BFA324 | #E2C225 / #F5E644 / #BBA01F | #EFD239 / #FFED53 / #C6AE30 |
| Sulfur, front three-quarter, tall block | #F1D22E / #FDED5B / #C6A91E | #E6C429 / #F5EA50 / #C8AA20 | #F2D23A / #FFEE5B / #D4B832 |
| Sulfur, front three-quarter, brick front | #D3B72B / #F2D534 / #B49B27 | #E2C122 / #F1D028 / #C5A820 | #EFD237 / #FFE13F / #C3AA31 |
| Sulfur, front | #F1D330 / #FDEE5F / #BBA42A | #E3C227 / #F6E640 / #A78E1C | #F0D33B / #FFEE54 / #B19B28 |
| Sulfur, side | #ECD134 / #FDF15F / #C3AB2B | #DDBE2E / #FBE85B / #B09C1F | #EACE41 / #FFF36A / #BAA931 |
| Sulfur, "rear three-quarter" (az +28) | #E4C530 / #FDEE5D / #C4A825 | — | #EDD03C / #FFF15F / #AC9A27 |
| Sulfur, rear (lit by the fill; not fitted) | #EED333 / #FDEE62 / #C1A622 | #C4AC24 / #D9C338 / #A6911B | #D0BB35 / #E6D248 / #B09E2B |
| Sulfur, top | #F7DE43 / #FEF168 / #BAA228 | #FBF062 / #FCF465 / #D9C840 | #FFF771 / #FFF875 / #E2D24E |
| Host, front top-slab wall | #A8978E | #A69389 | #A69389 |
| Host, side top slab | #988B87 | #97857B | #97857B |
| Host, top-view rim | #9A887E | #9B8A82 | #9A8982 |
| Host, front three-quarter, all strata | #7F716B | #97857D | #95857C |
| Lower strata, front | #7A6C66 | #7A6C65 | #736661 |
| Lower strata, side | #776861 | #83746D | #786A65 |
| Lower strata, rear | #75655D | #615754 | #58504E |
| Front three-quarter rock, band 0.6–0.8 H | #7A6B65 | #8C7C75 | #84756E |
| Foot rock, front three-quarter left / centre / front | #9B847D / #8C7D7B / #8B7D7A | #907F7C / #92807D / #92807C | #907E7C / #92807D / #91807C |

**Lit saturation (sheet 0.61–0.63):** front three-quarter 0.67, front 0.67, side 0.58, az +28 0.63; before, 0.74.
Medians are within about 5 levels in every fitted view.

**What is left:**
- **Top view:** it now reads paler than the sheet (median #FFF771 against #F7DE43). The block tops take the full sun
  there, and the body was fitted to the side views.
- **Az +28 shade quartile:** still about 20 levels dark (#AC9A27 against #C4A825). This is the down-facing bevels in
  the key light's shade.
- **Rock trade-off:** the front three-quarter's lower band is still about 8 levels light, while the front view's lower
  strata are now 6 levels dark. That is the paint trade-off between the two views. What remains of the difference is
  the deeper undercut shadow at the sheet's left end, which is geometry and light.

## Result

- **Verifier round 1:** FAIL, 6/10, on shape.
- **Verifier round 2:** 7/10. Shape and colour both passed; one technical blocker remained: the right foot rock crossed the base seam after the polish nudge. Stage 2 fixed it by turning the rock, and `build()` now checks every object for self-intersections. The main session confirmed 0 crossing pairs on all five objects before committing, under the 2-round cap.
- **Open minors:**
  - front34 W:H is 1.23 against the sheet's 1.42, and the sulfur sits 0.05–0.10 H high. Closing these would need the whole layout rotated or the shelf sloped, so they were left as they are.
  - In the top view the blocks cover 0.59 against 0.45, and the colour is paler than the sheet's.
  - The rock in front34 renders light. Most of this is the sheet's undercut shade.
  - The nugget reads as a flat cube.
