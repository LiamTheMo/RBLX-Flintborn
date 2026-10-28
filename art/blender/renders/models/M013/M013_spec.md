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
