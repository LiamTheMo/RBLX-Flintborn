# 015 Ember Meteor — spec

Reference: `art/blender/assets/references/015.png` (EMBER METEOR, "Individual Model Study"; the sheet header says
"14 — FLINTBORN" and the footer "PAGE 14/132"; INDEX.md lists it as 15, "Ember Meteor model study"; 1024 × 1536 px).
Builder: `art/blender/kit/mcp/m015.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`.
Sibling to rework in parallel: 009 Iron Meteor (`M009_spec.md`), whose crack approach is reused here (§6).

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Glow and VFX ship wherever
the sheet shows them. On the sibling 009 the user said "the crackes on the rock are not apparent and has no depth",
so **every glowing crack here is a real slot with walls and a recessed glowing floor, and every core window is a
real gap between pieces through which the separate core ball is seen** (§6). No painted grooves.

All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, top-left origin. Paper is `#F2EDE6`. Masks (`measure.py`
`cls()`):
- **O, glow orange:** r ≥ 120, r − b ≥ 70, r > g + 30.
- **L, dark ember lip / red-tinted wall:** r − b ≥ 22, r > g + 12, mean < 105.
- **B, base rock (warm):** (g − b ≥ 6, r − b ≥ 16, mean ≥ 80) or (r − b ≥ 26, mean ≥ 85).
- **S, shell:** anything else that is not paper (mean < 228).
- Base-rock shade facets with g ≈ b fall into S; the shell's lit facets stay out of B. So the meteor shares
  below are slight under-counts of orange. Use the same scripts on both images for comparisons.

Scratch study material (pure Python, no Blender), in the session scratchpad
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m015_study\`:
- `png.py` (reader, `crop`, `sample`);
- `measure.py` (`cls`, bboxes, shares, top profiles), `runs.py` (orange runs per row: cracks and windows),
  `samp.py` + `samp_run.py` (region colours, quartiles, luminance deciles), `comps.py` (exploded part bboxes),
  `gridcrop.py` (views with a 10 % grid: `g_front.png`, `g_side.png`, `g_rear.png`, `g_top.png`, `g_f34.png`,
  `g_r34.png`), `viz.py` (mask preview `cls.png`);
- crops `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `ex_A.png`, `ex_B.png`,
  `ex_C.png`, `ex_core.png`, `ex_rocks.png`, `junc.png`, `under.png`, `thick.png`, `vfx.png`, `vfx3.png`.
- To run them on our renders, point `R` at the render and set `P` to the render's background colour.

## 1. Study (2a)

### 1.1 Classification, size and scale

- **Classification:** full asset (event resource node). Hero budget 4000 tris; each part under 1000.
- **What it is:** a hot faceted ember core (a chunky orange polyhedron) held in an open cup of **four dark faceted
  rock-shell pieces** that lean in round it like split petals, with **open gaps** between them through which the
  core shows, and **two to three thin glowing cracks with real depth** cut into the shell pieces. A ring of **pale
  warm base rocks** hugs the foot. The sheet's words: "A fractured meteor with a hot ember core … Built from a small
  set of reusable rock pieces and a faceted ember core"; "Maintain open gaps between shell pieces to reveal the
  core"; "Core sits above base rocks". WorldModeling §12.5: a broad heavy outer mass with a few intentional
  fractures and a core insert; separate shell pieces, core and low rim.
- **Target size: about 11.5 W × 10.0 D × 7.6 H studs** over the rocks (H about 1.38× the 5.5-stud character, in
  line with M009 Iron Meteor at 7.4 and M014 Starstone at 7.8; the old R04 EmberMeteor was 9.5 × 8.5 × 7.5).
  Tolerances W ±0.5, D ±0.6, H ±0.3. The shell group alone is about 10.9 W × 9.0 D.
  - How it was derived: the ground-contact line rises 0.04–0.05 H at the ends of the front, side and rear views
    (`bottom` scan), so those views look down about **6°** (±2°). With H = 7.6 the measured ratios (front
    W : H_app 1.34, side D : H_app 1.14, top W : D 1.08 overall and 1.16 for the shells alone) solve to
    W ≈ 11.5, D ≈ 10.0.
- **Stud mappings used below** (build frame: front −Y, +X right, ground z 0):
  - front view X = −5.75 + 11.5 f;
  - rear view X = +5.75 − 11.5 f (screen right is −X);
  - side view (camera +X, screen right is the front) Y = +5.0 − 10.0 f;
  - top view X = −5.75 + 11.5 f, Y = −5.0 + 10.0 d, where d is the fraction from the image bottom (the front);
  - heights z ≈ 7.6 h (apparent; ±0.4 for points far in front of or behind the middle).

### 1.2 Measured views

| View (box) | Silhouette bbox (px) | W : H | Glow O share of meteor | Lip L share | Base-rock share of silhouette | Orange spans (W; H) |
| --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (20,130,460,445) | 23–451 × 134–436 | 1.42 | 22.9 % | 6.0 % | 29.5 % | 0.38–0.91; 0.13–0.88 |
| Rear three-quarter (470,150,845,445) | 470–833 × 159–432 | 1.33 | 17.4 % | 7.4 % | 28.9 % | 0.09–0.92; 0.15–0.85 |
| Front (20,508,270,716) | 26–261 × 528–704 | 1.34 | 26.3 % | 5.6 % | 26.6 % | 0.30–0.92; 0.15–0.86 |
| Side (276,508,510,716) | 291–491 × 527–703 | 1.14 (D : H) | 17.7 % | 8.5 % | 27.2 % | 0.20–0.87; 0.19–0.71 |
| Rear (516,508,767,716) | 522–757 × 534–704 | 1.38 | 24.2 % | 6.9 % | 25.9 % | 0.10–0.89; 0.15–0.85 |
| Top (773,508,1003,716) | 787–992 × 523–712 | 1.08 (W : D) | 27.0 % | 7.1 % | 26.0 % | 0.34–0.76; d 0.11–0.84 |

- "Meteor" = S + O + L pixels. Glow O is the bright orange only; L is the dark red lips and red-tinted walls.
- Reading: from every side and from above, a quarter of the meteor is glowing core. This is far more orange than
  M009 (2–4 %): the core is exposed through wide windows, not just cracks.

**Top profiles** (highest silhouette pixel per column, as a fraction of H; `measure.py`):

| f | 0.00 | 0.05 | 0.10 | 0.15 | 0.20 | 0.25 | 0.30 | 0.35 | 0.40 | 0.45 | 0.50 | 0.55 | 0.60 | 0.65 | 0.70 | 0.75 | 0.80 | 0.85 | 0.90 | 0.95 | 1.00 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front | .09 | .53 | .62 | .70 | .78 | .82 | .79 | .74 | .78 | .95 | 1.0 | .99 | .97 | .95 | .93 | .87 | .81 | .76 | .70 | .49 | .11 |
| Side | .07 | .38 | .55 | .67 | .77 | .82 | .86 | .91 | .95 | .98 | .99 | .96 | .92 | .86 | .84 | .79 | .70 | .63 | .59 | .42 | .09 |
| Rear | .09 | .49 | .64 | .77 | .84 | .89 | .94 | .97 | 1.0 | .93 | .79 | .98 | .98 | .95 | .93 | .90 | .83 | .73 | .64 | .51 | .10 |
| f34 | .13 | .18 | .48 | .62 | .70 | .78 | .85 | .83 | .78 | .89 | .99 | .99 | .98 | .96 | .92 | .86 | .80 | .74 | .61 | .42 | .12 |
| r34 | .13 | .40 | .55 | .64 | .71 | .77 | .84 | .85 | .77 | .84 | .96 | 1.0 | .98 | .97 | .95 | .92 | .86 | .79 | .73 | .52 | .15 |

**Base-rock tops** (highest B pixel per column before the shell, fraction of H, every 0.025 f; `—` = no rock seen):

```
f      .00 .03 .05 .07 .10 .12 .15 .17 .20 .23 .25 .28 .30 .33 .35 .38 .40 .42 .45 .47 .50 .53 .55 .57 .60 .62 .65 .68 .70 .72 .75 .78 .80 .82 .85 .88 .90 .93 .95 .97 1.0
front   —   —   —  .15  —   —   —  .15 .17 .19 .20 .19 .17 .15 .12 .09 .12 .14 .16 .18 .16 .15 .13 .09  —  .24 .28 .32 .35 .36 .38 .39 .39 .36 .32 .28  —  .23 .22 .20 .09
side    —   —   —   —   —   —  .15 .14 .20 .19 .16  —   —  .20  —  .23 .24 .26 .27 .28 .27 .26 .24 .23 .22 .23  —   —  .28 .27 .25 .23 .21 .17 .15 .17 .18 .18 .17 .13 .07
rear    —   —   —  .16 .19 .20  —  .24 .26 .28  —  .31 .33 .34 .32 .29  —   —  .16 .18 .20 .18 .16 .14  —  .16 .18 .20 .22 .24 .22 .19 .18 .16  —  .16 .19 .21 .19 .18 .08
```

(The front view's far-left rock is shaded and reads as S; by eye its top is about 0.24.)

### 1.3 Silhouette and composition per view

**Front (and the sheet's front three-quarter; see §3.1):**
- **Left boulder** (the FL piece): f 0.0–0.45, peak at f 0.22–0.25 (X ≈ −3.0), h 0.82 (z ≈ 6.2). Its left flank
  runs from (0.0, 0.45) through (0.12, 0.70) to the peak. From the peak it falls right to (0.42, 0.59), the top of
  the crack.
- **Sliver**, a narrow lobe of the same piece: f 0.33–0.52, top at about (0.41, 0.57) (X ≈ −1.0, z ≈ 4.4), in front
  of the core's lower left. **Crack 1** separates it from the boulder (§1.5).
- **Core window:** the core shows from h 0.18 to 0.83. It is widest at h 0.49 (f 0.46–0.75, 3.5 studs) and narrows
  to a slot at the bottom (f 0.53–0.58 at h 0.18) and to a point at the top (f 0.44–0.49 at h 0.83). Its left edge
  is the sliver (f 0.45) below h 0.59 and the boulder (f 0.34–0.40) above; its right edge is the FR and BR pieces
  (f 0.70–0.75).
- **Top pieces:** a dark top-left facet at f 0.40–0.47, h 0.85–0.97 is the BL piece peeking over; the big piece
  from the peak at f 0.47–0.52 (h 1.0) whose top edge slopes right to (0.82, 0.82) and then down the right flank to
  (0.95, 0.40) is BR. Its underside overhangs the core's top right; the strip between them is dark red (L).
- **Crack 2:** thin and near vertical at f 0.83–0.91, from h 0.73 down to h 0.25, close to BR's right silhouette
  (§1.5).
- **Base rocks** (x span, top h): far left 0.00–0.13 (≈0.24); left 0.11–0.37 (0.20); centre front 0.36–0.58 (0.18,
  low); **big right 0.56–0.88 (0.39, the tallest, a pointed dome)**; right 0.84–0.99 (0.23); a tiny one at
  0.76–0.90 (0.12).

**Side (camera +X; screen right is the front):**
- **BR**, the nearest big piece, fills f 0.05–0.62 (Y +4.5 … −1.2) with its peak at f 0.48–0.50 (Y ≈ 0), h 1.0.
  **Its crack runs diagonally across it**, from (0.45, 0.69) down to (0.20, 0.39), and continues past its glowing
  top as a dark closed hairline up to (0.62, 0.80).
- **Side window:** the core at f 0.62–0.87 (Y −1.2 … −3.7), h 0.22–0.69, widest at h 0.45–0.49 (2.5 studs).
- Front pieces at the screen right: FL's top behind (f 0.63–0.80, h 0.88) and FR in front (f 0.78–0.92,
  h 0.25–0.65).
- **Base rocks:** 0.00–0.14 (0.15), 0.06–0.32 (0.20), **0.28–0.62 (0.28, broad)**, 0.58–0.83 (0.28), 0.80–0.99
  (0.18), tiny 0.80–0.88.

**Rear (camera +Y; screen right is −X):**
- **Screen left = BR from behind:** a big rounded mass at f 0.03–0.42 (X +5.4 … +0.9) rising to its peak at f 0.40
  (X ≈ +1.15), h 1.0. **The BR crack** crosses its upper part from (0.41, 0.82) down to (0.12, 0.54).
- **Back notch:** at f 0.50 (X ≈ 0) the silhouette dips to h 0.79. The core shows through it.
- **Rear window:** the core at h 0.19–0.82, widest at h 0.58 (f 0.37–0.66, 3.4 studs), a slot at the bottom (f 0.45–0.47
  at h 0.19) and a point at the top (f 0.52–0.56 at h 0.82).
- **Screen right = BL:** an upper leaning slab with its peak at f 0.55–0.60 (X −0.6 … −1.15), h 0.98, sloping down to
  (0.80, 0.62). Below and outside it is a lower mass (f 0.55–0.96, up to h 0.62): BL's foot plus FL's back end.
  **Crack 5** runs down it at f 0.77–0.88 (X −3.1 … −4.4), from h 0.58 to h 0.15.
- **Base rocks:** 0.00–0.17 (0.20), **0.15–0.45 (0.34, the big back rock)**, 0.40–0.58 (0.20), 0.58–0.83 (0.24),
  0.82–1.00 (0.21).

**Top (front at the bottom):**
- **Four shell pieces in quadrants round a central cross-shaped opening:**
  - bottom-left FL: the biggest, a long slab lying diagonally from the back-left (f 0.1, d 0.6) to the
    front-centre (f 0.58, d 0.08), about 7.8 × 3.5;
  - top-left BL: a flattish lozenge, f 0.22–0.53, d 0.62–0.88;
  - top-right BR: a narrower egg, f 0.62–0.87, d 0.45–0.85;
  - bottom-right FR: a lozenge, f 0.55–0.90, d 0.08–0.48.
- **Glow from above:** a central diamond of core, widest at d 0.43 (f 0.38–0.76, 4.4 studs). From it run a
  **front channel** that narrows from 2.7 wide at d 0.33 to 0.45 at d 0.11 (f 0.52–0.56), a **back channel** about
  1.0 wide at f 0.53–0.62 (X +0.3 … +1.4) for d 0.62–0.81, and a short **right arm** at d 0.46–0.52 (f 0.62–0.75)
  between FR and BR. The left side is closed: FL's back end meets BL.
- **Base rocks** ring the back and both sides: back-left, back, a tiny back-centre one (f 0.45–0.55, d 0.93–1.0),
  back-right, right, a small right one (f 0.88–0.98, d 0.40–0.50), front-right and left. The front rocks are hidden
  under FL and FR (§3.5).

**Close-ups:**
- **Shell to Core Junction (652,788,1006,948):** "Shell pieces overlap the core with open gaps. Keep faces flat and
  clean." Two shell pieces meet over the core in a V. Their edges are crisp and their inner walls dark and
  red-tinted (`#625156`, shade `#4F2B2B`). The core's facets below run hot (`#FDAF44`, light `#FECF68`). The core
  passes **behind** the shell edges: it is overlapped, never set flush in a socket.
- **Underside View (652,958,1006,1105):** "Core sits above base rocks. Maintain clear separation and open gaps. No
  hidden geometry." Seen from low and in front, the core's lower facets (`#DB451A`) hang above the rock tops, with
  **dark gaps** (`#3B3435`) between the rocks and under the core. The core touches no rock.
- **Shell Thickness (652,1118,1006,1265):** "Rock shell pieces are solid low-poly forms with simple thickness. Keep
  clean, flat faces and bold edges." A big solid shell chunk with **one crack cut into it**: dark lip lines on both
  edges, a bright inner wall face visible on one side, widest (15 px) near the top, 6–8 px lower, tapering out.
  The pieces are solid, not hollow.
- **VFX overlay (18,1300,320,1475):** "Ember Glow VFX (separate asset). Simple emissive glow and floating ember
  shards. Not part of the solid geometry." (§7.)

### 1.4 Parts (exploded construction, box (18,780,642,1265))

Labels: three × "Shell Piece (Rock Shell)", "Ember Core (Ember Core)", "Base Rock (Base Rock)". The arrows push the
three shell pieces and the rocks in towards the core. The scale is set by the exploded core (159 × 166 px, 5.0 studs
in the hero): **about 32 px per stud**. Facet language: broad flat planes with crisp, slightly bevel-lit edges; no
crumbs or spikes. The shells' facets are 1–2.5 studs across, the rocks' 0.6–1.5.

#### Part A, the elbow slab with a crack: (95,828,300,1072); crop `ex_A.png`

- **Shape: a long, chunky, bent slab.** It is 7.9 studs along its bent axis (253 px) with a section of about
  3.6 × 3.3. The **lower section** is fat and stands near vertical (about 15° lean), about 0.45 of the length, with
  a chiselled bottom end. The **upper arm** leaves it at an elbow of about 130°, rising at about 40° from horizontal,
  with a section of about 3.4 × 3.1 and a flat chamfered end facet.
  - The long faces are broken into 3–4 broad planes, with a crease line along the elbow.
  - 30–45 facets in all.
- **Crack (A's own):**
  - It starts at the elbow on the front face as a **V notch, 0.45–0.5 wide** (14–17 px).
  - It runs **down the lower section's front face**: first down and across (about 35° off vertical) for about
    0.3 of its run, then nearly straight down, curving back slightly at the bottom, and it exits through the bottom
    edge.
  - Width 0.20–0.28 (6–9 px), tapering to 0.12 (4 px) at the bottom. Length about 4.4 studs (55 % of the piece).
  - It leaves a **narrow strip** on one side, about 0.35–0.4 of the lower section's width. In the hero this strip
    is the front view's sliver.
- **Glow spill:** the face turned to the core carries a red-orange tint (L pixels at x 210–229, y 952–1024). That
  is spill, painted in stage 4; it is not a crack.
- **Construction:** union two convex hulls, lower section and arm (5–6 rings each, 6–7 points per ring, broad
  sector jitter ±6 %), overlapping 0.4 at the elbow. Merge coplanar triangles (`dissolve_limit` 3–4°), then BEAUTY
  triangulation. Then carve the crack slot (§6.2). 60–110 tris before the slot, 150–230 after.

#### Part B, the flattish cap: (311,800,467,898); crop `ex_B.png`

- **Shape: a lentil or flattened lozenge.** 157 × 99 px, which is about **5.0 long × 3.6 wide × 2.7 thick**.
  - A low faceted dome top (one big ridge facet plus 5–6 sloped facets).
  - A sharp-ish belt edge round its widest ring, at about 0.4 of the thickness from the bottom.
  - A shallower, darker underside of 5–6 facets.
  - Drawn tilted about 15° (long axis rising to the left).
- **No crack.** Its underside reads dark and warm (`#46393C`, 346°, sat 0.19): that is the core's glow on the face
  turned to it, painted as spill.
- **Construction:** hull of 4 rings: bottom 2 points r 0.35; bottom ring 7 points r 0.75; belt 9 points r 1.0;
  top ring 7 points r 0.70 at +0.75 T; a 2-point top ridge at 1.0 T. Ellipse 5.0 × 3.6, jitter ±5 %.
  24–32 facets, 50–70 tris.

#### Part C, the egg chunk with a ridge crack: (457,887,581,1036); crop `ex_C.png`

- **Shape: a tall, rounded, faceted egg or almond.** 125 × 150 px, about **3.6 wide × 3.2 deep × 5.0 long**.
  - Blunt rounded top, slightly narrower bottom, a ridge down its upper-right flank.
  - Drawn tilted about 25° (top to the left). 28–36 facets.
- **Crack (C's own):** runs along the ridge from just below the top shoulder down to about 0.6 of the length.
  - Length about 2.3–2.5 studs (45–50 % of the piece).
  - Widest 0.25–0.37 (8–12 px) in its upper-middle, tapering to 2 px at both ends.
  - A narrow strip, 0.6–0.9 wide, lies on the outer side of the crack, like A's strip.
- **Construction:** hull of 6 rings (bottom 0.0 r 0.55; 0.15 r 0.85; 0.4 r 1.0; 0.65 r 0.95; 0.85 r 0.7; top
  0.97–1.0, 2–3 points r 0.3), 7 points per ring on a 3.6 × 3.2 ellipse, jitter ±6 %. Merge at 3–4°, then carve
  the crack slot (§6.2). 60–80 tris before the slot, 110–160 after.

#### The Ember Core: (282,917,440,1082); crop `ex_core.png`

- **Shape: a chunky faceted ball**, 159 × 166 px, which is **5.0 W × 4.8 D × 5.2 H**.
  - Its silhouette is an irregular 8–9-gon: a flat top-left edge, a top-right vertex, a near-vertical right edge, a
    lower point right of centre and a near-vertical left edge.
  - Facets are a mix of large pentagons, quads and triangles, **24–32 in all** (12–16 visible from one side), each
    1.2–2.2 studs across. They read like a coarse truncated icosahedron, never a smooth sphere.
- **Colour reading** (§5.3): hot yellow on the upper-right facets, orange belt, deep red-orange lower left.
- **Construction:** convex hull of about 34–40 Fibonacci points with a 0.93–1.05 radial wobble, scaled to
  5.0 × 4.8 × 5.2. `dissolve_limit` at 4–6° to reach 24–32 broad facets, then BEAUTY. 50–90 tris. Check the merged
  facet count.

#### Base Rock: cluster (40,1020,600,1240); crop `ex_rocks.png`

- **Nine rocks** in the exploded, with sizes in studs (W × H as drawn):

  | Rock | Size |
  | --- | --- |
  | left small | 2.4 × 2.1 |
  | **big front-left** | **5.4 × 3.3** |
  | mid-left tall | 2.4 × 2.4 |
  | pebble | 0.7 × 0.7 |
  | centre-front small | 2.0 × 1.4 |
  | centre-behind | 2.1 × 1.6 |
  | centre-right low | 2.5 × 1.6 |
  | **right big** | **4.1 × 2.8** |
  | far-right tall | 2.7 × 2.8 |

- **Shape:** rounded faceted cobbles and domes. Smoother than M014's (20–34 facets of 0.6–1.5 studs), with a flat
  bottom and a blunt off-centre crown. H : W runs 0.55 (low), 0.75 (dome) and 1.0 (tall).
- **Construction:** one part `EmberMeteorBaseRock`, a `K.hull_rock` dome with `keep_bottom=True`, rings about
  (0.0, 0.92, 8), (0.25, 1.0, 8), (0.55, 0.85, 7), (0.80, 0.55, 6), (0.95, 0.2, 3). 36–56 tris.
  - The hero uses transformed copies: non-uniform scale 0.6–1.5 per axis, a z turn and mirroring.
  - If one shape reads repetitive across 12 copies, allow up to 3 variants (round dome, tall dome, low cobble) and
    record it, as M009 allows.

### 1.5 Cracks and windows: measured per view (`runs.py`)

Positions are (f, h) as above; widths are glow pixels per row, converted at about 20 px per stud (front, rear and
side) and 17.8 (top).

| View | Feature | Path, top → bottom | Width (studs) | Notes |
| --- | --- | --- | --- | --- |
| Front | **Crack 1** (boulder / sliver) | (0.42, 0.59) → (0.37, 0.49) → (0.31, 0.35), jog → (0.32, 0.25) → (0.33, 0.18) into the rocks; X −0.9 → −2.2 → −2.0, z 4.5 → 1.4 | 0.15–0.44; widest 0.44 at h 0.39 (the jog); typical 0.25 | glow all along; the dark lips are visible |
| Front | **Crack 2** (BR right flank) | (0.83, 0.73) → (0.88, 0.62) → (0.90, 0.42) → (0.91, 0.35) → (0.89, 0.25); X +3.8 → +4.7, z 5.5 → 1.9 | 0.10–0.30; widest at h 0.45–0.49 | BR's crack seen edge-on (§3.3) |
| Front | Core window | widest h 0.49: f 0.46–0.75; h 0.62: 0.43–0.69; h 0.76: 0.38–0.50; h 0.25: 0.53–0.62 | 3.5 max | bottom slot 0.6 wide |
| Side | **BR crack** | (0.45, 0.69) → (0.37, 0.62) → (0.30, 0.56) → (0.23, 0.49) → (0.20, 0.39); Y +0.5 → +3.0, z 5.2 → 3.0 | 0.20–0.50; widest at h 0.52 | continues as a dark hairline up to (0.62, 0.80) |
| Side | Side window | f 0.62–0.87, h 0.22–0.69 (Y −1.2 … −3.7, z 1.7 … 5.2) | 2.5 max at h 0.45–0.49 | |
| Rear | **BR crack** | (0.41, 0.82) → (0.31, 0.75) → (0.23, 0.68) → (0.17, 0.61) → (0.12, 0.54); X +1.0 → +4.4, z 6.2 → 3.9 | 0.10–0.50; widest at h 0.58 | |
| Rear | **Crack 5** (BL foot) | (0.77, 0.58) → (0.83, 0.51) → (0.87, 0.44) → (0.88, 0.33) → (0.86, 0.19) → (0.85, 0.15); X −3.1 → −4.4 → −4.0, z 4.4 → 1.1 | 0.15–0.45; widest at h 0.44 | a short second strand at f 0.86–0.87, h 0.54–0.58 |
| Rear | Rear window | widest h 0.58: f 0.37–0.66; h 0.44: 0.37–0.57; h 0.75: 0.40–0.57; h 0.19: 0.45–0.47 | 3.4 max | point at the top (0.52–0.56, h 0.82) |
| f34 | Crack 1 / core / crack 2 | crack 1 f 0.39–0.49, h 0.14–0.60 (widest 13 px, 0.6 at h 0.44); core f 0.44–0.76, h 0.21–0.87; crack 2 f 0.80–0.91, h 0.27–0.77 | | the same picture as the front (§3.1) |
| Top | Diamond, channels, arm | see §1.3 | front channel 0.45 → 2.7; back 1.0; arm about 0.6 | |

- **Crack character:** long straight runs with one or two sharp jogs, widest at a jog or at the top, tapering to
  nothing at the ends. They are thin: 0.15–0.45 wide, typically 0.25. The ends continue as closed dark hairlines.
- **Windows:** wide diamond or V openings between pieces, narrowing to a slot at the bottom and a point at the top.
- **Colour gradient across a crack** (luminance deciles, front crack 1):

  ```
  #5A1E13 #793932 #A5402B #B55129 #E95314 #EF6118 #F6711A #F8881B #F9A31B #FBBB3A
  ```

  That is a dark lip, then a red-brown wall (the Ember Shadow swatch `#C04F30`), then an orange wall, then a hot
  yellow floor. The side BR crack and the thickness close-up are the same within 10–15 levels. This is the depth
  read (§6).

## 2. Layout (starting values; tune to §1.2–§1.5)

Build frame: front −Y, +X right, ground z 0, studs. Every piece is a transformed copy of a finished part mesh
(m011 `_paste` pattern). Non-uniform instance scale stays within 0.8–1.6 per axis, so crack widths stay 0.15–0.5
and depths at least 0.9 (§6.2).

### 2.1 Core

| Piece | Part | Centre | Size | Notes |
| --- | --- | --- | --- | --- |
| Core | `EmberCore` | (+0.4, −0.7, 3.25) | 5.0 × 4.8 × 5.1 | bottom z 0.7, top z 5.8 (0.76 H). The top-view diamond centre (+0.6, −0.3) and the side window (Y −1.2 … −3.7) pull Y in opposite directions; −0.7 is the compromise. |

### 2.2 Shell pieces

| Piece | Part | Footprint (X; Y) | Top | Orientation | Its crack shows as |
| --- | --- | --- | --- | --- | --- |
| **FL**, front-left boulder | A (`EmberMeteorSlab`), mirrored in X if needed so the strip falls right of the crack | −5.6 … +0.1; −4.4 … +1.6 | elbow peak (−3.0, −1.2, 6.2); sliver top (−1.0, −3.5, 4.4) | lower section stands at the front centre-left (base centre ≈ (−1.6, −3.0)), crack face to the front (−Y, turned ≈10° to +X); arm reaches back-left and gently up to its end at about (−5.0, +1.0, 4.0–4.6) | front crack 1: X −0.9 → −2.2, z 4.5 → 1.4; strip = sliver |
| **BR**, back-right, tallest | C (`EmberMeteorChunk`) at about ×(1.5, 1.5, 1.5) | −0.4 … +5.6; −1.4 … +4.6 | inner top (+1.15, +0.6, 7.6) | leans about 25° in toward the core (−X, slightly −Y); its broad outer flank faces +X and the back | P1 (+1.4, +1.0, 6.6) → P2 (+3.2, +1.6, 5.4), jog → P3 (+4.3, +2.2, 4.4) → P4 (+4.7, +3.0, 3.2), then taper. Gives side (Y +0.5 → +3.0), rear (X +1.0 → +4.4) and, edge-on, front crack 2 (X ≈ +3.8 … +4.7). |
| **BL**, back-left | C mirrored at about ×(1.25, 1.25, 1.3) | −4.2 … +0.4; +0.6 … +4.4 | upper edge z 7.3–7.5 from X −1.2 to +0.3, peak at (−0.6, +1.2) | leans about 35° in toward +X and the front | rear crack 5 on its outer (−X) lower flank: X −3.1 → −4.4, z 4.4 → 1.1 |
| **FR**, front-right | B (`EmberMeteorCap`) at about ×(0.9–1.0) | +1.0 … +4.8; −4.6 … −2.4 | inner upper edge (+1.6, −2.6, 4.8) | tilted 35–45°, leaning in, its broad top facing up and out (front-right) | none (B has no crack) |

- **Rules the pieces must satisfy:**
  - **Overlap the core 0.3–0.8** along their inner faces, so the union leaves crisp junction creases (the "Shell
    to Core Junction"). No coplanar or exact contact.
  - **Leave the core's top uncovered from above** apart from the four piece corners: the top view's diamond is
    4.4 wide. The tall BR and BL tops stand round it like petals, not over it.
  - **Leave open gaps:** the front window (the sliver's right edge at X ≈ −0.6 up to z 4.5, the boulder at
    X −1.4 … −1.9 above; FR and BR's left edges at X +2.3 … +2.9); the back window (BR inner edge X ≈ +1.5, BL inner
    edge X ≈ −1.8 at z 4.4, closing to a notch at X ≈ 0, z 6.0); the +X side window between BR's front edge (Y ≈ −1.2)
    and FR's back edge (Y ≈ −2.6 … −3.0).
  - FL's arm end meets BL's foot on the −X side: no window there (the top view's left side is closed).
- **Why this mapping** (§3.4 has the alternatives): it uses all three exploded shells. A (the long slab) is the top
  view's long bottom-left piece, and its crack with the strip is the front view's crack plus sliver. C (the egg
  with the ridge crack) is the top view's egg-shaped top-right piece, and its crack is the long diagonal crack seen
  in the side and rear views. B (the flattish lozenge) is the bottom-right lozenge. A second C (mirrored) carries
  the rear view's crack 5.

### 2.3 Base rocks (`EmberMeteorBaseRock` copies; floor-cut at z 0)

| Rock | Centre (X, Y) | W × D × H | Seen in |
| --- | --- | --- | --- |
| F1 far left | (−5.1, −0.4) | 1.9 × 2.0 × 1.8 | front 0.00–0.13 (≈0.24); top left |
| F2 left | (−3.0, −3.6) | 3.0 × 2.4 × 1.6 | front 0.11–0.37 (0.20) |
| F3 centre front (low) | (−0.4, −4.4) | 2.5 × 2.0 × 1.35 | front 0.36–0.58 (0.18); in front of the core's bottom slot |
| **F4 big right (tall)** | (+2.6, −3.6) | 3.6 × 3.0 × 2.9 | front 0.56–0.88 (0.39, pointed dome); side 0.58–0.83 (0.28) |
| F5 tiny front right | (+3.7, −4.9) | 1.2 × 1.0 × 0.8 | front 0.76–0.90 (0.12) |
| S1 right | (+5.2, −0.3) | 2.4 × 3.0 × 1.9 | front 0.84–0.99 (0.23); side 0.28–0.62 (0.28) |
| S2 small right | (+5.4, −1.9) | 1.1 × 1.0 × 0.9 | top f 0.88–0.98, d 0.40–0.50 |
| B1 back right | (+4.8, +2.6) | 2.0 × 2.0 × 1.6 | rear 0.00–0.17 (0.20); side 0.06–0.32 |
| **B2 big back** | (+2.3, +3.9) | 3.4 × 2.6 × 2.6 | rear 0.15–0.45 (0.34) |
| B3 back centre | (−0.1, +4.6) | 2.1 × 1.7 × 1.5 | rear 0.40–0.58 (0.20) |
| B4 back left | (−2.4, +4.0) | 2.9 × 2.2 × 1.8 | rear 0.58–0.83 (0.24) |
| B5 left back | (−4.8, +2.4) | 2.0 × 2.0 × 1.6 | rear 0.82–1.00 (0.21) |
| P1 pebble | (+0.3, +5.1) | 0.9 × 0.8 × 0.7 | top f 0.45–0.55, d 0.93–1.0 |

- Rock tops reach at most 0.39 H (F4) and cover the shells' bottom 15–40 %. They sink 0.2–0.4 into the shell feet
  and into each other so they union. 1–3 small ones may stay separate shells (as M009).
- **No rock touches the core:** keep at least 0.2 clear ("Core sits above base rocks … open gaps"). The underside
  render must show dark gaps between the rock tops and the core's lower facets.

**Expected hero:** about 11.5 × 10.0 × 7.6. BR's inner top is the highest point (7.6) and BL's is 7.3–7.5. Tris:
core 50–90; A 150–230; C 110–160 (twice); B 50–70; rock part 36–56 (× 13 ≈ 600). Union total about 1300–2000,
well under 4000.

## 3. View conflicts and resolutions

### 3.1 The sheet's three-quarter views are nearly the sheet's front and rear

- The f34 has the same feature order and spans as the front: boulder peak 0.30 against 0.25, crack 1 at 0.39–0.49
  against 0.31–0.42, crack 2 at 0.80–0.91 against 0.83–0.91. Its W : H is 1.42 against 1.34.
- The r34 likewise matches the rear.
- Both are about **12–15° off axis at about 10° elevation**; the kit's `front34` (−28, 12) and `rear34` (152, 12)
  are twice as far round.
- **Resolution:** build to the orthographic views. Compare the sheet's f34 and r34 with extra renders at
  **(−14, 10)** and **(166, 10)**. Judge the kit's front34 and rear34 for sanity only (expect more of FL's left face
  and less of the core window: an O share of about 15–20 % instead of 23 %).

### 3.2 Camera elevation

- The sheet's front, side and rear look down about 6°; the kit's look down 4°. So the kit's renders read about
  0.02 H flatter on top.
- **Resolution:** add extras `front_sheet (0, 7)`, `side_sheet (90, 7)` and `rear_sheet (180, 7)` through
  `M.views(..., extra=...)`. Compare the §1.2 profiles and the §1.5 tables on those, with tolerance ±0.06 h.

### 3.3 Crack 2 (front) and the BR crack (side and rear) are one crack

- One polyline across BR's +X / back flank (P1–P4 in §2.2) lands within about ±0.07 f of the side and rear tables.
- Seen from the front, BR's +X flank is edge-on, so the same crack appears near the right silhouette as a near
  vertical line. The sheet's z 1.9 bottom is lower than P4 (3.2).
- **Resolution:** let the crack's last segment turn down the flank (P4 → (+4.8, +2.4, 2.2), tapering). If it then
  shows in the side view below h 0.39, that is acceptable, because rocks hide most of it.

### 3.4 Crack 5 (rear) has no part of its own

- The exploded shows three shell parts and two cracks (A and C).
- **Resolution:** BL is a second, mirrored copy of C, placed so that its crack faces out on the back-left lower
  flank.
- **Alternative**, if C reads wrong as BL from the top or the rear: use B as BL (the top view's top-left piece is
  lozenge-like) and C′ as FR with its crack turned inward (hidden). Crack 5 is then lost, and that must be
  recorded. The main session decides.

### 3.5 The top view hides the front rocks and is tilted

- Back and side rocks show whole; the front ones (F2, F3, F4) do not appear past FL and FR. FL and FR may overhang
  them slightly, or the top camera leans back a little.
- **Resolution:** the front, side and rear views govern the rocks; the top view governs the shell arrangement, the
  cross-shaped opening and the glow share from above (27 %). Compare with the kit's top (0, 89) and an extra
  (0, 78).

### 3.6 The windows don't line up exactly between views

- Side window Y −1.2 … −3.7 against the top view's right arm at d 0.46–0.52 (Y ≈ −0.4 … +0.2).
- Rear notch at X ≈ 0 against the top back channel at X +0.3 … +1.4.
- **Resolution:** tolerance ±0.8 stud on window edges. Priorities: front window > rear window > top diamond > side
  window. Record the final edges.

### 3.7 Exploded and hero leans and sizes differ

- The exploded draws A's arm at 40° and C at 25° tilt. The hero orientations come from the views (§2.2).
- C becomes BR at about ×1.5. That is allowed: transformed copies of finished parts, like M014's rocks.

### 3.8 "No baked lighting, glow, or particle effects in the mesh" (modelling notes) against the user's VFX rule

- The user's standing rule wins: the core and the crack floors ship as emissive (Neon) faces, and the glow, light
  and embers ship as sockets (§7). Nothing is baked into vertex colours.
- The sheet's "VFX overlay (separate)" is satisfied by sockets, which are separate from the mesh.
- The note "simple solid colours" likewise yields to the user's blended regions plus Tint (§5.5).

## 4. Construction plan (Stage 1)

1. **Write the parts first**, each with its own function and checked against its exploded cell: `slab()` (A),
   `cap()` (B), `chunk()` (C), `core()`, `base_rock()`. Render an exploded shot (`extra`) laid out as the sheet's:
   the core in the centre, A upper left, B above, C right, nine rocks below.
2. **Crack slots in A and C** (§6.2), with 3 wall rows and a floor row kept as colour geometry.
3. **Hero:**
   1. `_paste` A, C, C′ and B with the §2.2 transforms, the core, and 13 rock copies.
   2. One exact self-union (m011 `_self_union`), then `union_loose`, then `m004.floor_cut` at z 0.
4. **Placeholder keys** (stage 1): `m015_shell`, `m015_ember_lip`, `m015_ember_wall`, `m015_core`, `m015_core_hot`,
   `m015_core_deep`, `m015_base`. Stage 4 adds the others (§5.5).
5. **Stage 1 acceptance** (render, compare every view, measure):
   1. **Profiles:** front, side and rear top profiles within ±0.06 h of §1.2 on the sheet-elevation extras.
      Rock tops within ±0.05.
   2. **Glow shares** (O only, same mask) within ±4 points per view: front 26 %, side 18 %, rear 24 %, top 27 %,
      f34 extra 23 %, r34 extra 17 %. With placeholder colours expect higher; stage 4's lips and core_deep bring it
      down.
   3. **Windows:** spans per §1.5 within ±0.07 f / ±0.08 h. The front window must be widest near mid-height and
      narrow to a slot at the bottom.
   4. **Cracks:** 2 in the front view, 1 in the side, 2 in the rear, with paths within ±0.07 f / ±0.08 h of §1.5.
      Measured through the MCP with BVH ray pairs, 5 points per crack:
      - lip-to-lip opening 0.15–0.5, peaks at jogs and tops;
      - floor width about 0.45 of the opening;
      - depth from the lip to the floor at least 0.9 (§6.2);
      - ends taper to closed over 0.6–1.0, then a dark hairline.
   5. **Core:** 24–32 broad facets; 0.3–0.8 into every shell; at least 0.2 from every rock; its top uncovered from
      above.
   6. **Parts against their cells** (shape, proportions, facet count, crack placement and length).
   7. **Hero size** 11.5 × 10.0 × 7.6 (±0.5 / ±0.6 / ±0.3).

## 5. Colour plan (Stage 4)

### 5.1 Swatches (flat; medians of a 26 × 24 box inside each)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Rock Shell | (878,195,904,219) | `#474347` | 300°, 0.06, 0.28 |
| Rock Mid | (878,242,904,266) | `#908888` | 0°, 0.06, 0.56 |
| Base Rock | (878,289,904,313) | `#B8A193` | 23°, 0.20, 0.72 |
| Ember Core | (878,338,904,362) | `#FD7732` | 20°, 0.80, 0.99 |
| Ember Shadow | (878,385,904,409) | `#C04F30` | 13°, 0.75, 0.75 |

- **Rock Shell** is the shell's dark body tone (the render's dark quartile is `#373134`–`#3F3A3F`).
- **Rock Mid** is its lit facets and light patches (lit quartile `#867A7F`–`#8E8183`).
- **Ember Shadow** is the red-brown of the crack walls (decile 4, `#B55129`) and the core's deep lower facets
  (`#CD3D1A`–`#DF461B`).

### 5.2 Rendered regions (`samp_run.py`; median, lit quartile, shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Shell, f34 all | (20,130,460,445) | S | `#60595F` | `#8E8183` | `#373133` |
| Shell, f34 left boulder | (60,175,235,390) | S | `#524F59` | `#82777C` | `#353133` |
| Shell, f34 BR | (235,135,430,330) | S | `#6D6262` | `#8E8386` | `#3B3335` |
| Shell, front view | (26,528,261,704) | S | `#685E63` | `#8B7F83` | `#373134` |
| Shell, side view | (291,527,491,703) | S | `#5C565D` | `#867A7F` | `#3B373C` |
| Shell, rear view | (522,534,757,704) | S | `#5B545A` | `#887B7E` | `#373135` |
| Shell, top view | (787,523,992,712) | S | `#61595E` | `#A29494` | `#3F3A3E` |
| Shell, exploded A | (95,828,300,1092) | S | `#5D575E` | `#786F75` | `#3D393F` |
| Shell, exploded B | (311,800,467,898) | S | `#46393C` (warm underside) | `#928587` | `#332D30` |
| Shell, exploded C | (457,887,581,1036) | S | `#5D5458` | `#7C7175` | `#3B3032` |
| Shell, thickness close-up | (652,1118,840,1265) | S | `#5A545A` | `#797178` | `#3A3538` |
| Shell inner wall (junction) | (770,810,830,880) | S+L | `#625156` | `#918386` | `#4F2B2B` |
| Shell round the underside | (655,960,700,1060) | S | `#37333A` | `#5A5359` | `#272124` |
| Gaps between rocks (underside) | (700,1040,830,1080) | S | `#3B3435` | `#5B4B48` | `#1D1616` |
| Lips / red walls, f34 | (20,130,460,445) | L | `#623A36` | `#735A52` | `#512018` |
| Lips / red walls, front / rear / top | | L | `#653835` / `#68413B` / `#6C3B34` | `#725B53` | `#542117` |
| Core, f34 window | (240,180,345,400) | O | `#FD7E25` | `#FEBB4A` | `#BB370A` |
| Core, front window | (105,540,200,690) | O | `#FD812A` | `#FEB746` | `#BF3E12` |
| Core, side window | (415,560,470,680) | O | `#FC6D24` | `#FDB040` | `#9C3E1B` |
| Core, rear window | (600,560,680,690) | O | `#FC6921` | `#FEB241` | `#A52F0B` |
| Core, top | (860,560,950,700) | O | `#FC7324` | `#FECE5A` | `#B1340D` |
| Core, exploded all | (282,917,440,1082) | O | `#FD6D27` | `#FDBD59` | `#DC451B` |
| Core, exploded upper right (hot) | (360,930,440,1000) | O | `#FDBD57` | `#FDD875` | `#FD7124` |
| Core, exploded lower left (deep) | (282,1000,360,1082) | O | `#E4491E` | `#FD6D25` | `#CA3D1A` |
| Core, junction close-up | (700,860,840,948) | O | `#FD9734` | `#FDCB62` | `#C6441B` |
| Core, underside close-up | (680,960,820,1060) | O | `#DB451A` | `#FE9737` | `#AB2F13` |
| Crack 1, front | (95,600,130,690) | O+L | `#E25D21` | `#FAA829` | `#6F3026` |
| Crack 2, front | (215,545,250,665) | O+L | `#C45823` | `#FA9B20` | `#762D1B` |
| BR crack, side | (325,570,395,640) | O+L | `#DB531E` | `#FBA22B` | `#882B1A` |
| BR crack, rear | (545,575,625,640) | O+L | `#D15025` | `#FD731F` | `#7F3629` |
| Crack 5, rear | (695,595,735,680) | O+L | `#CB541F` | `#F8971F` | `#7D2D1C` |
| Crack, exploded A | (130,940,175,1080) | O+L | `#DE4B1E` | `#FC9D24` | `#653429` |
| Crack, exploded C | (520,920,565,990) | O+L | `#DE6828` | `#FCB537` | `#A4371B` |
| Crack, thickness close-up | (780,1120,840,1265) | O+L | `#F25B21` | `#FDAA2E` | `#A4331C` |
| Base rocks, f34 | (20,330,460,445) | B | `#AC9389` | `#D0B7AB` | `#8A756A` |
| Base rock, f34 big right (F4) | (290,320,410,430) | B | `#A38A7D` | `#CCB3A7` | `#867268` |
| Base rocks, front | (26,630,261,704) | B | `#B0988D` | `#D7BEB0` | `#8C776E` |
| Base rocks, side | (291,630,491,703) | B | `#B2978C` | `#DAC0B2` | `#957D72` |
| Base rocks, rear | (522,630,757,704) | B | `#B59B8E` | `#D5BBAE` | `#947C71` |
| Base rocks, exploded | (60,1035,600,1230) | B | `#B89E93` | `#D7BEB1` | `#8F796E` |
| Base rocks, underside | (652,1000,840,1105) | B | `#B0978B` | `#D2B9AD` | `#8B756C` |

### 5.3 How the colour works

**Shell.**
- One dark violet-grey family: hue 290–340°, sat 0.07–0.11. Medians `#5B545A`–`#685E63` per view.
- Front-view luminance deciles:

  ```
  #2B2628 #393336 #3E393F #50494F #615A61 #6E6367 #776C71 #7C7378 #887D80 #95898D
  ```

- The lit/shade split is the studio light. Paint broad regions only: light patches toward Rock Mid, dark patches
  toward Rock Shell.
- **Glow spill on the shell** (`spill` scan, distance to the nearest glow pixel):
  - far shell is cool, `#5A5660` (264°);
  - within 1–10 px (≈0.5 stud) of a crack or window it warms to `#685D5E`–`#695F62` (342–355°, sat 0.10–0.11);
  - the faces turned to the core go darker and red, `#625156` → `#4F2B2B`;
  - the exploded B underside is `#46393C`.

  That is the core's light, and it is what makes the windows read as lit cavities. Paint it as a position field
  (distance to the core / crack floor); add the light in stage 5.

**Cracks: four steps by depth** (§1.5 deciles):
1. Lip `#5A1E13`–`#682E26`.
2. Red-brown wall `#793932`–`#B55129`, around the Ember Shadow swatch.
3. Orange wall `#E95314`–`#F6711A`.
4. Hot floor `#F8881B`–`#FBBB3A` (p95 `#FDBD2A`–`#FEB928`).

**Core.**
- Hue 11–43°: hot yellow upper facets, orange belt, deep red-orange lower facets.
- Exploded deciles:

  ```
  #CD3D1A #DF461B #F9541D #FD5E21 #FD6924 #FD7026 #FD8030 #FD9236 #FDB752 #FDD571
  ```

- In the hero windows the lowest deciles fall to `#9C2509`–`#A22204` under the overhangs and the shell edges. The
  hot region is the core's crown and upper-right (top view lit `#FECE5A`; junction `#FDAF44`). The deep region is
  the lower third and the underside (`#DB451A`).

**Base rocks.**
- Warm pinkish beige, hue 17–23°, sat 0.19–0.24. Medians `#AC9389`–`#B89E93`; swatch `#B8A193`.
- Shade quartile `#8A756A`–`#957D72` (lighting). Contact gaps go near black (`#3B3435`, shadow).
- Rock pixels within 3 px of glow are only slightly warmer and darker (`#A6857B`, sat 0.26): **the sheet shows no
  orange wash on the rocks**.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered medians, not swatches. Use `M.sample(..., "stone")` for shell and rock and
`K.sample(..., "vivid")` for the glow.

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m015_shell` | `#5F585E` (mean of the view medians) | shell bodies | rough 0.88, metal 0 |
| `m015_shell_light` | `#7C7378` (decile 8; toward Rock Mid `#908888`) | broad patches, about 25 %, 2–4 facets each | rough 0.88 |
| `m015_shell_dark` | `#45404A` (Rock Shell `#474347`; dark deciles `#3E393F`) | broad patches; the ground band of each shell (bottom ~1.0 above the rocks); shell faces under the core and in the contact gaps (underside `#37333A`) | rough 0.9 |
| `m015_shell_warm` | `#685D5E` (measured spill) | shell faces within ~0.5 of a crack lip or a window rim; the faces of A and B turned to the core (`#625156`) | rough 0.88 |
| `m015_ember_lip` | `#5E2620` (crack decile 1–2 / L median `#623A36`) | crack lip band (0–0.25 d) and lip chamfer; shell inner walls within ~0.3 of the core surface (L share 5.6–8.5 %) | rough 0.85, emission 0 |
| `m015_ember_wall` | `#B04A2C` (Ember Shadow `#C04F30`; deciles `#A5402B`–`#B55129`) | crack wall band 0.25–0.55 d | rough 0.75, emission 0 (solid; see §7.1) |
| `m015_core` | `#FD7428` (Ember Core `#FD7732`; window medians `#FC6921`–`#FD812A`) | crack wall band 0.55–1.0 d; the core's belt | **emission ≥ 1.0 → Neon** |
| `m015_core_hot` | `#FDB548` (window light quartiles `#FEB746`–`#FEBB4A`; exploded hot `#FDBD57`; crack floor p90 `#F9A31B`–`#FBBB3A`) | crack floors; the core's crown and upper facets | **emission ≥ 1.0 → Neon** |
| `m015_core_deep` | `#D9441A` (exploded deep `#E4491E`; underside `#DB451A`; decile 2 `#DF461B`) | the core's lower third and underside; core faces within 0.4 of a shell (occlusion) | rough 0.5, **emission 0** (solid and lit, so its facets shade; see §7.1) |
| `m015_base` | `#B39A8F` (front, side and rear medians `#B0988D`–`#B59B8E`; swatch `#B8A193`) | rock bodies | rough 0.92 |
| `m015_base_light` | `#C8AFA3` (deciles 7–8) | broad patches on the rocks, about 25 % (never tops by facing) | rough 0.92 |
| `m015_base_dark` | `#8F786D` (shade quartiles `#8C776E`–`#957D72`) | ground-contact row (bottom 20–25 % of each rock by height); rock faces within 0.3 of a shell or a neighbour | rough 0.92 |

- **Calibration warnings:**
  - The core and crack-floor targets sit near r = 255, so calibrated hexes clip in red. Lower the specular rather
    than raising emission if the core washes to yellow-white; `#FDD571` is the brightest the sheet goes.
  - Calibrate `shell_warm`, `ember_lip` and `ember_wall` on their own dome, then re-measure in the hero with VFX
    on, because the stage 5 light also tints them.
  - `K.sample`'s stone mask (sat < 0.18) drops warm lit rock pixels (sat up to 0.24). Use `M.sample` "stone" for
    the rocks, as M011, M013 and M014 did.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Shell:**
  - body `shell`; broad noise (scale about 0.2, patches 3–5 studs), shell ↔ shell_light at level 0.3 and
    shell ↔ shell_dark at level −0.3;
  - **ground band:** height above the local rock tops < 1.0 → 50 % `shell_dark`;
  - **spill field:** d is the distance to the nearest glow face (core surface or crack floor):
    d < 0.25 → 75 % `shell_warm`, < 0.5 → 50 %, < 0.9 → 25 %;
  - **cavity field:** shell faces within 0.3 of the core surface → `ember_lip`, blended to `shell_warm` by 0.6.
  - So the gradient into a window runs shell → shell_warm → ember_lip → the core's own colours.
- **Cracks:** grade the wall rows by **depth below the uncut outer surface** (ray to the part's pre-carve hull),
  never by normal: lip, then ember_wall, then core, then core_hot (floor).
  - `blend` steps 3 across lip ↔ ember_wall (both solid).
  - core and core_hot are glow keys, so their boundaries are geometric rows and hard by construction.
  - Along each crack, fade the floor from core_hot to core over the last 25 % toward each tapered end, so the ends
    cool, as on the sheet.
- **Core:** field u = height fraction + 0.25 × lateral toward (+X, +Y) + 0.1 × broad noise:
  - u < 0.30 → `core_deep`;
  - 0.30–0.65 → `core`;
  - > 0.65 → `core_hot`;
  - plus the occlusion rule (within 0.4 of a shell → core_deep).
  - The facing correlation must stay below 0.5 (`K.check`). The hot crown faces up, so the lateral and noise terms
    matter; M012's height-only bands scored 0.65.
- **Base rocks:** body `base`; noise patches `base_light` (level 0.3); ground row and shell-contact faces → 25–50 %
  `base_dark`; crown (top 30 % of each rock) 0 %. Their pale beige must meet the dark shell with a soft dark contact
  band, not a hard line.
- **Hard edges only** where genuinely different materials meet: shell against core (separate meshes in the union)
  and shell against rock. Those are automatic, because they are separate keys on separate faces.

### 5.6 Texture (Tint) and finish

- **Tint:** per piece `tint_var` about 0.04, so neighbouring shells and rocks differ slightly.
  - `K.texture` shell: amp 0.07, scale 0.45, jitter ±0.02 (as m011 stone).
  - Rocks: amp 0.05.
  - Core and crack keys: none. Neon and emissive keys ignore Tint in the export.
  - Broad and calm, never confetti.
- **Finish:**

  | Material | Roughness | Specular | Metal | Notes |
  | --- | --- | --- | --- | --- |
  | Shell keys | 0.88–0.9 | normal | 0 | matte; bold lit edges come from the facets |
  | Lip and wall keys | 0.75–0.85 | low | 0 | solid |
  | Core keys | 0.45–0.5 | low | 0 | flat-shaded facets; `core` and `core_hot` emissive (Neon) |
  | Base rocks | 0.92 | normal | 0 | matte |

- **Shading waiver:** `K.check` may flag `baked_shading` on the crack wall bands, because depth correlates with
  facing on walls. Waive it with a reason (m011 `SHADING_OK`): "crack wall bands graded by depth below the lip (the
  sheet's lip → ember → orange → hot gradient)".

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- Shell median within about 8 levels of `#5F585E` per view.
- Window core medians within about 12 levels of `#FD7E25`–`#FC6921`.
- Crack quartiles near `#6F3026` / `#E25D21` / `#FAA829`.
- Rock median within about 10 levels of `#B0988D` (front) **with VFX on**.
- Glow shares per §4, step 5, check 2.

## 6. Depth: how the cracks and windows get it

### 6.1 Windows (core seen between pieces)

The core is a separate ball (`EmberCore`) set inside the cup of four solid shell pieces, which overlap it by
0.3–0.8. Where the pieces part, the eye sees the core's own facets 0.8–2.0 studs behind the shell rims. Three things
carry the depth:
1. **Real geometry:** the shell rims are thick (solid pieces, 2–4 studs through), so their side walls show at every
   oblique angle.
2. **Graded colour:** the rim walls go shell → shell_warm → ember_lip; the core goes deep in the occluded strips
   next to the rims and hot in the open.
3. **Light:** the stage 5 light sits in front of the window, in the open, so the rim walls catch the glow and the
   overhang undersides stay dark red. That is the sheet's L band (`#512018`–`#735A52`).

### 6.2 Cracks (slots cut into a solid part)

Reuse M009's flared-wedge cutter, here as the **primary** route, because A and C are solid pieces, not hollow
sector shells. For each crack polyline on the part's surface (nodes with an opening G):
- **Per segment,** one convex-hull cutter of 5 rings, offset along the local inward normal:

  | Ring | Depth | Half-width |
  | --- | --- | --- |
  | Outside | +0.5 | G/2 |
  | Lip chamfer | 0.08, **one side only** | G/2 + 0.06 (that side reads lower) |
  | Wall 1 | 0.25 d | lerp(G, g)/2 |
  | Wall 2 | 0.55 d | lerp(G, g)/2 |
  | Floor | d, flat | g/2, with **g = 0.45 G** |

  So the walls splay outward and show from oblique views.
- **Joints:** overlap 0.12; no wedge stubs.
- **Ends:** taper G to 0.04 over the last 0.6–1.0 of the run, then stop. The sheet's dark hairline continuation can
  be a 0.03-wide, 0.15-deep closed cut, or simply the `ember_lip` → `shell_dark` blend along a facet edge.
- **Openings G in part space:**
  - A: 0.45–0.5 at the elbow notch, 0.22–0.28 along the run, a 0.35 peak at the jog, tapering to 0.12 at the bottom
    exit. The A crack exits through the bottom edge, so in the hero it disappears behind F2 and F3.
  - C: 0.3–0.35 at the widest, 0.2 typical, tapering at both ends.
  - Instance scaling (≤1.5) brings them to 0.15–0.5 in the hero.
- **Depth d:** 1.0 (A) and 0.9 (C) in part space, so the depth is at least 2.5–4× the opening. The part must stay
  at least 0.8 thick behind the floor everywhere; check with a ray probe. In the hero, a floor that lands inside the
  core simply unions into it, which is fine.
- **Carve:** `M.carve` (exact difference) of the union of a crack's cutters, done once per part.
- **Face rows to keep** (stage 2 must not dissolve them, because they are colour geometry): lip chamfer, wall band
  1 (0–0.25 d), wall band 2 (0.25–0.55 d), wall band 3 (0.55 d–d), floor.
- **Check through the MCP (BVH ray pairs, 5 stations per crack):**
  - opening 0.15–0.5;
  - floor width 0.4–0.5 of the opening;
  - depth ≥ 0.9 (hero);
  - floor faces carry `core_hot`, the lowest wall row `core`, the middle row `ember_wall`, the top row and chamfer
    `ember_lip`.
  - From the front, side and rear views at least one wall band per crack must be visible, plus the floor in the
    widest stretch.

### 6.3 What is reused from M009, and what differs

| Topic | M009 Iron Meteor plan | M015 Ember Meteor |
| --- | --- | --- |
| Shell | hollow sector pieces cut from one hull by seam cones; seams are the gaps between pieces | **solid** pieces ("solid low-poly forms with simple thickness"); four separate transformed part copies round a core |
| Orange share | 2–4 % (cracks only) | **17–27 %**: wide windows onto the core, plus cracks |
| Cracks | the seams between pieces, onto the core | **slots cut into A and C**, with their own floors (§6.2); the core shows in the windows |
| Depth grading | lip → ember → core → hot by depth below the lip | the same four steps and the same depth field (§5.5) |
| Cutter | M009's "alternative" flared wedge cutter | the same cutter as the primary route |
| Floor colour | core_hot, fading toward the ends | the same |
| Light | outside the mesh at the seams, shadows on (no light inside the meteor) | the same; in front of the front and back windows |
| Embers | at the seam lips | floating shards round the whole meteor (VFX panel) |
| Rim rocks | about 12 + small stones, pale | 13 copies of one part (up to 3 variants), pale warm beige; **never touch the core** |

## 7. Lighting and VFX plan (Stages 5 and 6)

**What the sheet shows:**
- The core is self-lit: its shade facets stay orange-red, and the deepest are `#9C2509` under the overhangs.
- The cracks glow from a hot floor.
- The shell rims next to the glow are warm (spill), the overhang undersides dark red.
- The rocks are only faintly warmed.
- The separate "Ember Glow VFX" panel adds a soft warm halo hugging the silhouette (`#F8DCC0`–`#F9D5B0`, about
  0.3–0.8 stud out) and **about 10 floating faceted ember shards** round both flanks and above, 0.5–3 studs from
  the silhouette, from h 0.1 to above the top.
  - Shards are 0.4–0.8 studs, orange (`#FD6A22`, `#FE5A1B`, `#FE6815`) or hot (`#FD9F2A`, `#FEBD79`, `#FCC074`).
  - A few tiny sparks are about 0.15.
- No smoke, no dust, no heat shimmer drawn.

### 7.1 Stage 5 (lighting)

- **Emissive (Neon) keys: `m015_core` and `m015_core_hot`** at emission ≥ 1.0 (start at 1.2). Each exports as a Neon
  glow piece, one per key, with no collision.
  - Two keys means two Neon pieces (more only if a piece is split over MAX_TRIS). Check the export STATS line.
  - Reason: the core and the crack floors are the asset's light source and must read hot in Roblox at any time of
    day.
- **Not Neon: `m015_core_deep`** (emission 0). In Roblox Neon is unlit and one flat colour per piece. A lit, solid
  deep key on the core's lower third and occluded strips keeps the facet steps and the "Ember Shadow" read.
  - Emission between 0 and 1 does nothing in Roblox except drop the Tint. Don't use it as a "subtle glow".
  - Likewise `ember_wall` and `ember_lip` stay solid.
- **Lights:** PointLights in the open, never inside the mesh. M009's lesson: a light inside the meteor shone through
  and turned the rim rocks peach.
  - **L1, front window:** about (+0.7, −4.3, 3.8), in front of the window and above F3 and F4. Colour `#FF7A22`,
    brightness 0.9, range 10, shadows true, flicker true.
  - **L2, back window:** about (+0.3, +3.7, 4.4). Brightness 0.6, range 7, shadows true, flicker true.
  - Check by BVH that each point is at least 0.8 stud from every surface after any layout change.
  - Record the hero-local positions in Roblox axes (x, z, −y) as m011's `STUDIO_LIGHT` did.
- **Checks:**
  - With VFX on, the front rock median stays within about 10 levels of `#B0988D`.
  - The shell rims next to the windows warm toward `#685D5E`.
- **Studio note to record:** the glow halo relies on the place's default Bloom. With Bloom off, the Neon core and
  floors still read and the heat_glow emitters carry the halo.

### 7.2 Stage 6 (VFX), using kinds in `art/blender/lib/vfx.py`

- **`heat_glow` × 2** (they carry L1 and L2 above): the "simple emissive glow".
  - Emitter `glow_soft`, colour `["#FFB347", "#FF6A1A"]`, size [1.4, 2.0] (scale about 1.5), transparency
    [0.6, 1.0], rate 2–3, speed [0.2, 0.4].
  - Emitter shape spread over each window: about [3.0, 4.0, 0.6] (front) and [2.5, 4.0, 0.6] (back), Roblox XYZ.
- **`embers` × 2:** the "floating ember shards".
  - **E1, top opening:** about (+0.5, −0.4, 6.4), in open air above the core's crown (BVH ≥ 0.5 from surfaces).
    Overrides: colour `["#FEBD79", "#FD6A22", "#FE5A1B"]`, size [0.55, 0.2], rate 3, lifetime [2.0, 3.5],
    speed [0.6, 1.4], spread 70, drag 0.6, acceleration [0, 0.5, 0], shape [5.0, 1.0, 4.0]. They drift up and out
    round the flanks, as on the panel.
  - **E2, front window:** about (+0.7, −3.8, 2.8). Rate 1.5, otherwise the same.
  - `ember_dot` ("small glowing faceted dot") matches the faceted shards; no new texture is needed.
- **Not added** (the sheet shows none): smoke, dust, ore_glint (the core is molten, not glossy ore; the R04 sheet
  made the same call) and heat shimmer.
- **Harvest sockets** (`harvest_hit` / `harvest_deplete`): the old R04 EmberMeteor had them; the numbered M-models
  so far (m009, m011–m013) do not. The main session decides.
- All sockets go on the hero only, as in m011–m014. Render with `vfx=True`. If the preview stand-ins veil the
  model, render the compare set with them hidden plus one extra shot with them, and record that. The export STATS
  line must report 4 sockets and 2 glow pieces.

## 8. Naming

The R04 kit sheet owns the old Ember Meteor set (`scripts/kit/R04/ember_meteor.py`, `R04_stats.json`,
`art/roblox/kit/R04/manifest.json`): `EmberMeteor`, `EmberMeteorShellPiece`, `EmberMeteorShellPieceB`,
`EmberMeteorCore`, `EmberMeteorImpactBase`, `EmberMeteorDepleted`, `CooledEmberFragment`, `CooledEmberFragmentB`,
and the keys `r04_ember_core`, `r04_lava_crack`, `r04_meteor_rock`, `r04_impact_rock`, `r04_cooled_ember`.
`M.mk` would silently rename a clash to `<name>M015`, so avoid them all.

**Proposed names** (a `git grep -w` of the whole repo found none of them):

| Object | Part | Why |
| --- | --- | --- |
| `EmberMeteorDeposit` | hero | R04 owns `EmberMeteor`; matches 009's `IronMeteorDeposit` |
| `EmberMeteorSlab` | Shell Piece A (elbow slab with crack) | R04 owns `EmberMeteorShellPiece*` |
| `EmberMeteorCap` | Shell Piece B (flattish cap) | |
| `EmberMeteorChunk` | Shell Piece C (egg with ridge crack) | |
| `EmberCore` | Ember Core | the sheet's own label; R04 owns `EmberMeteorCore` |
| `EmberMeteorBaseRock` | Base Rock | R04 owns `EmberMeteorImpactBase` |

- Palette keys `m015_*` (§5.4; none in use). Collection `Kit/M015 Ember Meteor`.
- **Export decision (main session):** the sheet labels three distinct shell parts, so the proposal is to export all
  three plus the core and the base rock (6 objects with the hero). M009 exported one shell piece; the alternative is
  to export only `EmberMeteorSlab` and keep B and C as build-only `_m015_*` objects.

## 9. Pitfalls to avoid

1. **Painted or shallow cracks.** Every crack is a slot at least 0.9 deep with splayed walls in three rows and a hot
   floor. Depth reads from the dark lip, the red-brown wall and the hot floor, not from orange alone (§6.2).
2. **A closed ball with cracks.** This meteor is an open cup: wide windows onto a separate core ball, glowing 17–27 %
   of the meteor per view. A shell that covers the core's top or closes the front window fails the top and front
   views.
3. **A hollow shell.** The sheet says the pieces are solid. Don't reuse M009's hollow sector shells here.
4. **A smooth or spherical core.** It is a chunky 24–32-facet polyhedron, 5.0 × 4.8 × 5.2. Not an icosphere, not a
   gem.
5. **The core touching the rocks**, or sitting on the ground. It hangs at z 0.7–5.8, at least 0.2 from every rock,
   held by the shells.
6. **Even-width zigzags.** Long straight runs, 1–2 sharp jogs, widest at the jog or the top, tapered ends, no stubs.
7. **Over-wide cracks to "add depth".** The sheet's cracks are 0.15–0.45 wide. If a crack still looks flat, fix the
   wall bands and the floor heat first.
8. **Neon on everything.** Only `core` and `core_hot` are Neon. `core_deep`, the lips and the walls stay solid.
   Emission between 0 and 1 is useless in Roblox.
9. **Lights inside the mesh.** Lights go in the open in front of the windows, with shadows on; check that the rocks
   stay `#B0988D`.
10. **Colour by facing.** The shell's lit and shade split and the rocks' are lighting. Paint positions only: spill,
    cavity, ground band, crack depth, core height plus lateral.
11. **Rocks too pink or too grey.** Medians `#AC9389`–`#B89E93`. **Shell too light.** Medians `#5B545A`–`#685E63`;
    the Rock Mid swatch `#908888` is the lit tone, not the body.
12. **Exact booleans.** Overlap everything (core 0.3–0.8 into shells, rocks 0.2–0.4 into shells, crack cutters 0.12
    at joints); never coplanar contact. Keep the cutters' outer ring 0.5 outside the surface.
13. **Instance scale eating the cracks.** Keep instance scale at 1.6 or less per axis, and re-measure crack openings
    and depth in the hero, not only in the parts.
14. **Comparing the wrong views.** The sheet's f34 and r34 are about 13° off axis, not 28°. Use the §3 extras at
    the sheet's elevations.
15. **Thin slivers.** The crack walls and lip chamfers make long thin faces. Split them at the cutter stations and
    keep triangles above 5° (M012's lesson). Remove boolean slivers with m011's `_tidy` / `_desliver`, but lock the
    crack rows and the ground plane.
16. **Naming clashes** with R04 (§8). Only one agent drives Blender at a time. No commits, pushes or exports in
    stage agents.

## Decisions (main session, 2026-10-28)

- Shell exports: export all three shell parts (`EmberMeteorSlab`, `EmberMeteorCap`, `EmberMeteorChunk`), as the sheet labels three distinct pieces.
- Back-left piece: a mirrored copy of C, which keeps the rear view's second crack.
- Harvest sockets: none for now, consistent with m009 and m011–m013. Gameplay sockets can be added to every node later in one pass.
- Names: as proposed (`EmberMeteorDeposit`, `EmberMeteorSlab`, `EmberMeteorCap`, `EmberMeteorChunk`, `EmberCore`, `EmberMeteorBaseRock`).

## Correction (main session, 2026-10-28): side-view direction

The kit's side camera (`VIEWS["side"]` = azimuth 90) sits at +X and looks along −X with Z up, so screen right is +Y: the model's BACK (fronts face −Y). Wherever this spec says the side view's right is the front, read it mirrored. Stage 1 should confirm this with a probe render before using side-view numbers. The 3D layout is unaffected.

## Stage 1 — Modelling

Builder: `art/blender/kit/mcp/m015.py` (`build()`; `iterate()` = build without the full render set plus the sheet-angle
preview). Collection `Kit/M015 Ember Meteor`; `FlintbornWorldKit.blend` saved through the MCP. Renders in
`art/blender/renders/models/M015/`: the kit's seven views, `front_sheet (0, 7)`, `side_sheet (90, 7)`, `rear_sheet (180, 7)`,
`top78`, `f34_sheet (-14, 10)`, `r34_sheet (166, 10)`, `exploded`, five `part_*` shots and `M015_views.png`.
Side-view direction confirmed by render: `side_sheet` (camera +X) has the front on the LEFT, so every side number below
is compared with the sheet's side mirrored (`MEASURE_VIEWS` / `MIRRORED` in the builder).

### What was built

Each part has its own function; the hero is pasted strictly from the finished part meshes (`m011._paste`) and unioned.

- **`EmberMeteorSlab` (A, `slab()`)**: two convex hulls, unioned. A lower section (3.3 long, 6-point rings 3.9 × 3.5,
  leaning 12° towards +X) and an arm leaving the elbow at heading 62° (towards +X +Y, away from the crack face), rising
  20°, 3.9 long, its end ring small and dropped 0.45 b, so the end is one big slanted facet and the peak sits mid-arm
  (the front view's rounded boulder, not a log). 64 merged facets before the slot. Crack on the lower section's front
  (−Y) face (`SLAB_CRACK`): a wide notch at the elbow (G 0.46), down and across, a jog (0.36), then nearly straight
  down, closing 0.65 above the bottom (see deviations).
- **`EmberMeteorCap` (B, `cap()`)**: hull of the spec's four rings plus a 2-point ridge; 5.0 × 3.45 × 2.7, 45 facets,
  50 tris. No crack.
- **`EmberMeteorChunk` (C, `chunk()`)**: hull of six 6-point rings (3.6 × 3.2 × 5.0) with a ridge point at +X on the
  0.4 / 0.65 / 0.85 rings; 59 facets. Crack (`CHUNK_CRACK`) beside the ridge (θ −8 … −16°), from 0.81 L down to
  0.30 L, widest 0.34 in its upper middle, a jog at 0.57 L, tapering closed at both ends.
- **`EmberCore` (`core()`)**: hull of 32 Fibonacci points (wobble 0.95–1.04) on 5.0 × 4.8 × 5.2, with hull triangles
  within 20° merged (`CORE_MERGE`; 9° left 40 facets): **32 broad facets, 60 tris**. Placeholder keys by height plus a
  lean to +X +Y: `core_deep` below, `core` belt, `core_hot` crown.
- **`EmberMeteorBaseRock` (`base_rock()`)**: `K.hull_rock` dome, flat bottom, blunt 3-point crown, 49 facets, 58 tris.
  One variant only (13 copies, non-uniform scale, turns, mirrors).
- **Crack slots (§6.2)**: `crack_stations()` snaps control rays onto the part's uncut surface, resamples to at most
  0.42 apart and smooths the normals. `_crack_tube()` lofts one closed cutter per crack. Its cross-section runs lid
  (+0.5) → lip chamfer on side A (0.08 deep, +0.06 set-back) → wall rows at 0.25 d and 0.55 d → a flat floor 0.45 G
  wide, so the walls splay. Closed ends converge to a line (depth × 0.55 there, so the end wall leans in). `M.carve`
  (exact) cuts it, and the cutter's faces carry the keys into the slot: lip band and chamfer `m015_ember_lip`,
  0.25–0.55 d `m015_ember_wall`, 0.55 d–d `m015_core`, floor `m015_core_hot`. Depth d = 1.0 (A) and 0.9 (C, ×1.2–1.75
  in the hero).
- **Cleanup**:
  - `_clean()` is m011 `_clean` (ears, quads, slivers) with every vert on a lip or ember-wall face locked (colour
    geometry) and the ground plane kept flat.
  - `_finish()` is `M.finish` (UVs 45° ANGLE_BASED, margin 0.008), then holes filled and slivers forced until nothing is
    under 3°.
  - `_ground_keys()` gives each floor-cap face the key of the wall it closes (the scan fill had made the whole
    underside `m015_core`).
- **Hero layout** (`PIECES`: location, spin about the part's own Z, lean heading and angle, part-axis scale, mirror):

  | Piece | Part | Location | Spin | Lean | Scale | Mirror | Core overlap |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | Core | EmberCore | (0.15, −0.75, 3.2) | 20 | — | 1.04 | | |
  | FL | Slab | (−1.6, −3.05, −0.4) | 10 | — | 1.0 | yes | 0.71 |
  | BR | Chunk | (5.3, 2.8, −0.3) | 60 (crack faces about 48°, back-right) | 30° to heading 205 | (1.4, 1.2, 1.75) | | 0.88 |
  | BL | Chunk | (−4.4, 2.95, −0.3) | −92 (crack faces about 100°, back) | 28° to heading −25 | (1.35, 1.15, 1.62) | yes | 0.55 |
  | FR | Cap | (2.55, −1.95, 2.8) | 25 | 50° to heading −65 | (0.85, 0.95, 0.95) | | 0.45 |

  - Rocks (`ROCKS`) follow §2.3, pulled in about 5 % (F1 at −4.8, S1 at 4.6, the back row at Y 3.7–4.8) and sunk 0.3.
  - Core to rock: F4 is 0.23 clear (target ≥ 0.2) and every other rock 1.0–3.5. The core sits above the rocks with dark
    gaps (underside render).
- **Core decision:** the core is **not** a separate shell. It overlaps all four shells by 0.45–0.88 (target 0.3–0.8; BR
  is 0.08 over) and is unioned in, so the junctions are crisp creases ("Shell pieces overlap the core with open gaps").
  A free-floating core would touch nothing and need hidden support; overlapping reads as the sheet and keeps one closed
  mesh.

### Measured (MCP, final build)

| Object | Tris / budget | Size (studs) | Shells | Non-manifold / boundary | Self-crossings | Min corner | Keys |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EmberMeteorDeposit | 2122 / 4000 | 12.04 × 10.73 × 7.47 | 2 (meteor + pebble P1) | 0 / 0 | 0 | 3.42° | core, core_deep, core_hot, shell, ember_lip, ember_wall, base |
| EmberMeteorSlab | 518 / 1000 | 5.21 × 5.82 × 5.80 | 1 | 0 / 0 | 0 | 3.46° | shell, lip, wall, core, core_hot |
| EmberMeteorCap | 50 / 1000 | 5.03 × 3.45 × 2.70 | 1 | 0 / 0 | 0 | 28.1° | shell |
| EmberMeteorChunk | 302 / 1000 | 3.70 × 3.12 × 4.93 | 1 | 0 / 0 | 0 | 3.02° | shell, lip, wall, core, core_hot |
| EmberCore | 60 / 1000 | 4.72 × 4.72 × 5.13 | 1 | 0 / 0 | 0 | 35.0° | core, core_deep, core_hot |
| EmberMeteorBaseRock | 58 / 1000 | 2.62 × 2.42 × 1.90 | 1 | 0 / 0 | 0 | 17.9° | base |

- Normals are outward, there are no n-gons, and `K.check` is clean.
- Hero size against the 11.5 × 10.0 × 7.6 target: W is 0.04 over the ±0.5 band, D 0.13 over ±0.6, H in band.
- The slab and chunk are well above the spec's tri estimates (150–230 and 110–160), because the slot walls keep three
  rows plus the chamfer and floor at every station. Both are still under 1000.

### Against the sheet (orthographic label rasters, `measure()`; sheet tables §1.2 and §1.5)

| View | Profile error mean / worst | Glow O share, ours / sheet | W : H, ours / sheet |
| --- | --- | --- | --- |
| front (0, 7) | 0.074 / 0.23 | 21.5 / 26.3 % | 1.47 / 1.34 |
| side (90, 7, mirrored) | 0.104 / 0.21 | 16.8 / 17.7 % | 1.36 / 1.14 |
| rear (180, 7) | 0.064 / 0.18 | 17.2 / 24.2 % | 1.53 / 1.38 |
| top (0, 78) | — | 19.5 / 27.0 % | 1.13 / 1.08 |
| f34 (−14, 10) | — | 20.8 / 22.9 % | 1.41 / 1.42 |
| r34 (166, 10) | — | 14.0 / 17.4 % | 1.49 / 1.33 |

O here is the core keys plus the ember-wall faces, in placeholder colours. The lip share is 1.3–2.2 % against the
sheet's 5.6–8.5 %; the sheet's L also counts the red-tinted rims, which stage 4's spill and cavity fields add.

- **Front.** FL reads as the sheet's boulder, with the sliver and crack 1 in front of the core, BL's tip peeking over
  the top left, BR's peak at the top right, and FR as the dark mass right of the window, on F4.
  - Profile: f 0.20–0.30 within 0.03. The worst error is at f 0.45–0.50 (ours 0.76, sheet 0.95–1.0): the sheet's BR
    peak sits over the window centre, ours at f 0.6, so the core's crown shows there.
  - Window rows (f): h 0.25 0.47–0.60 (sheet 0.53–0.62, the bottom slot); h 0.49 0.40–0.56 (sheet 0.46–0.75: ours is
    1.9 studs wide against 3.5, because FR and F4 cover its right half); h 0.62 0.31–0.65 (0.43–0.69); h 0.76 0.44–0.56
    (0.38–0.50).
  - Crack 1 runs from f 0.31–0.33 at h 0.2–0.25 up to the notch at (0.42, 0.6); the sheet's is f 0.31–0.42, h 0.18–0.59.
  - **Crack 2 (BR's crack edge-on) does not show in the front view**: BR's crack faces back-right.
- **Side (mirrored).** BR fills the back two-thirds, with its crack running diagonally across its +X face; FR sits at the
  front edge.
  - Crack: f 0.16–0.23 at h 0.62–0.82 plus the lower run; the sheet's is f 0.20–0.45, h 0.39–0.69, so ours sits higher
    and steeper.
  - Window onto the core: f 0.51–0.61 at h 0.49 (sheet 0.62–0.87); about 1.0 stud against 2.5.
  - Profile: worst at the back end (BR's back flank stands higher than the sheet's 0.42–0.59).
- **Rear.** The two leaning back pieces frame a V window onto the core: a diamond, a slot at the bottom and a point at
  the top.
  - Point at h 0.82: f 0.46–0.49 (sheet 0.52–0.56).
  - Width at h 0.58: f 0.45–0.57 (sheet 0.37–0.66): 1.4 studs against 3.4.
  - One crack on each piece: BR's on its upper outer flank (left); crack 5 on BL at f 0.68–0.80, h 0.35–0.70 (sheet
    0.77–0.88, h 0.15–0.58). Ours is higher because C's crack runs 0.30–0.81 L.
- **Top.** Four pieces in quadrants round a central diamond of core, widest at d 0.49, f 0.30–0.69 (sheet f 0.38–0.76 at
  d 0.43: the same width, 0.07 to the left). The crack tops of BR and BL show as short glowing slots near the piece tops.
- **Cracks in the hero** (`crack_probe()`, BVH ray pairs, 5 stations per crack; the end stations are the tapers):

  | Crack | Opening (lip to lip) | Floor | Depth (surface → floor) |
  | --- | --- | --- | --- |
  | FL (crack 1) | 0.45 (elbow notch), 0.28, 0.31 (jog), 0.17 | 0.25, 0.21, 0.14, 0.08 | 0.95, 0.90, 1.00, 1.00 |
  | BR (×1.2–1.75) | 0.33, 0.40, 0.31, 0.19 | 0.17, 0.23, 0.17, 0.11 | 0.57 (top taper), 0.91–1.24, 1.02, 0.55 (bottom taper) |
  | BL (×1.15–1.62) | 0.32, 0.39, 0.29, 0.18 | 0.17, 0.22, 0.17, 0.11 | 0.55 (taper), 0.86–1.17, 0.94, 0.52 (taper) |

  - Openings are 0.17–0.45 (target 0.15–0.5) and floors 0.45–0.6 of the opening.
  - Depth is at least 0.9 along the open runs, except BL's 0.86 at one station.
  - One station per crack sits on a jog, where the side ray ran along the slot; it reports 2.0+ and is ignored.
- **Parts against their cells.** A is a chunky bent slab with its crack and strip on the lower section (`part_slab`); C
  a faceted egg with the crack beside its ridge (`part_chunk`); B the flat lozenge; the core a chunky 32-facet ball; the
  base rock a rounded dome. The exploded render lays them round the core, with the 13-rock ring below.

### Deviations and decisions

- A's crack closes 0.65 above the part's bottom instead of exiting through it. Run out, the slot crossed the hero's
  floor cut and the ground cap triangulated its outline into a 0.78° sliver. In the hero, F2 and F3 hide the last stud.
- BL leans 28° and BR 30° in towards each other, to put their peaks near the centre in the front view (on the sheet both
  peaks sit at f 0.40–0.52). Straight egg copies can't also keep the sheet's wide rear window, because the sheet's pieces
  curve like petals. So the rear and side windows are narrower than drawn, and the rear and top glow shares are 7–7.5
  points low.
- BR's crack faces back-right (side and rear), so the front view's crack 2 is lost; recorded, not chased.
- The hero is 0.04 wider and 0.13 deeper than the tolerance band (rocks S1 and F1, BR's back).

### Left for later stages

- **Stage 2:** min corners are 3.0–3.5° on the hero, slab and chunk (target 5°, with the wall rows locked: the m009
  `_polish` pattern with `WALL_KEYS` = lip + ember wall). The hero's 2nd shell is pebble P1 (allowed). Keep the slot
  rows.
- **Stage 4:** every key is a placeholder. The spill and cavity fields (§5.5) will add the sheet's L band. The core's
  three keys come from a height + lateral field; its facing correlation is not checked yet.
- **Shape follow-ups if the verifier asks:**
  - widen the front window (FR further right, or smaller);
  - open the rear window (less lean on BL and BR, at the cost of the front-view peaks);
  - lower BR's crack in the side view;
  - make the hero 0.1–0.2 narrower.

### Stage 1 rework (overall read)

The main session's review of the first pass: it read as "rocks round a campfire" — small, low, separate boulders
ringing a big exposed orange ball, with oversized base rocks. The sheet is one big rounded fractured meteor, height
0.8–0.9 of its width, whose tall faceted pieces close round the core like a cracked egg shell that has partly opened.
The core glows through one main opening and thin seams, and its crown is covered. `m015.py` was rewritten; the
first-pass layout above is superseded.

**Construction (now).**
- **One common dome** (`dome()`): a convex hull of six 8-point rings, 10.2 × 9.2 at the belt, 7.3 high plus a crown
  lift. It is mirror-symmetric about the plane x = `XC` (0.3), steep-flanked with a broad shoulder, and its back half
  rises up to 0.6 higher, so the back pieces stand tallest. 75 merged facets.
  - The first try (10 points on 7 rings, 121 facets) read as a smooth ball, so it was cut down to fewer, bigger planes.
- **Core** (`core()`): the same 32-point Fibonacci hull, now built from the x ≥ 0 half and mirrored, so it is symmetric
  and the mirrored back-left piece still fits it. 5.3 × 5.1 × 5.3, 31 facets, 58 tris, centre (XC, −0.65, 3.05).
- **Four pieces = dome sectors.** Vertical seam planes through the centre at azimuths front −75°, right −5°, back 90°
  (on the mirror plane) and left 185° (the right seam's mirror) give the top view's cross. Each piece is built by
  `piece_obj()` with exact booleans:
  1. dome ∩ its sector prism, stopping 0.04 short of each seam line (no coplanar contact in the union);
  2. minus the hollow: the core hull scaled 0.9 with the core's own 20° merge, so each piece's inner face lies about
     0.25 inside the core and the union leaves crisp creases;
  3. minus the openings it borders;
  4. minus the slot cutters along its seams and its own crack;
  5. floor-cut at the ground, with loose crumbs dropped.
- **Openings** (`OPENINGS`): diamond frusta from inside the core outward, flare 1.22, so the rims splay a little and
  read as lit cavity walls (`m015_ember_lip`).
  - front: centred on the core, slightly right, 4.4 × 5.0;
  - rear: on the mirror plane, 3.9 × 4.7;
  - side: +X, cut from FR only, 2.7 × 3.9;
  - crown: vertical, 3.5 × 4.1, where the four seams meet.
  - The side opening was moved back 0.6: at first it met the front opening and cut FR into two shells.
- **Seams and cracks** use the same lofted slot cutter as the first pass: splayed walls with rows at 0.25 d and 0.55 d
  (lip / ember wall / core band) and a hot floor 0.45 G wide.
  - Seams: depth 1.25, G 0.36–0.55, no chamfer (keeps them mirror-exact), stations every 0.75. The left seam's cutter
    is the exact mirror of the right one's.
  - Cracks: crack 1 down FL's front left of the window (the boulder | sliver crack), and the BR crack running
    diagonally down its back-right flank (mirrored onto BL as crack 5). Depth 1.0, G up to 0.42, one-side chamfer,
    tapered closed at both ends.
- **Part mapping** (changed; recorded): the shells are now the dome's sectors, not independent shapes.
  - `EmberMeteorSlab` (A) is FL: the long piece wrapping from the front window round the left side, with crack 1.
  - `EmberMeteorCap` (B) is FR, between the front and side windows.
  - `EmberMeteorChunk` (C) is BR, the tallest, with its crack.
  - The back-left piece is the Chunk mirrored about x = XC (the main session's decision kept). The dome, core, rear
    window, crown opening and back seam are symmetric, and the left seam is the right one's mirror, so the mirrored
    copy fits exactly.
  - The hero pastes FL, FR, BR, mirrored BR, the core and 13 stones, all from the finished part meshes. The pieces sit
    0.05 below the ground so the floor cut never runs along their own flat bottoms.
  - The sheet's exploded shapes (elbow slab, lozenge, egg) are no longer matched literally: the shells are curved dome
    sectors. That is what lets them close into the meteor silhouette.
- **Base rocks:** 13 low stones round the foot (`ROCKS` by azimuth and distance, × 0.88), 0.7–1.7 high. The part is a
  2.4 × 2.25 × 1.3 rounded stone.
- **Cleanup additions:**
  - `_ground_slivers()` fixes thin floor-cap triangles fanned onto a 0.1 ground edge where a stone meets a piece. It
    first tries a merge (when the link condition allows), then a flip, then splits the cap's long edges.
  - `gaps()` now reports core-to-rock clearance and core contact. The shells' overlap with the core is fixed by
    construction (0.9 hollow); the old nearest-face depth was unreliable through slotted pieces.

**Measured (MCP, final build).**

| Object | Tris / budget | Size (studs) | Shells | Non-manifold / boundary | Self-crossings | Min corner |
| --- | --- | --- | --- | --- | --- | --- |
| EmberMeteorDeposit | 3360 / 4000 | 11.13 × 10.24 × 7.34 | 1 | 0 / 0 | 0 | 3.05° |
| EmberMeteorSlab (FL) | 614 / 1000 | 5.75 × 4.17 × 6.95 | 1 | 0 / 0 | 0 | 3.21° |
| EmberMeteorCap (FR) | 354 / 1000 | 4.67 × 3.94 × 6.95 | 1 | 0 / 0 | 0 | 3.06° |
| EmberMeteorChunk (BR) | 744 / 1000 | 4.79 × 4.78 × 7.39 | 1 | 0 / 0 | 0 | 3.36° |
| EmberCore | 58 / 1000 | 4.91 × 4.72 × 5.23 | 1 | 0 / 0 | 0 | 18.6° |
| EmberMeteorBaseRock | 58 / 1000 | 2.41 × 2.25 × 1.30 | 1 | 0 / 0 | 0 | 9.9° |

- Normals are outward, there are no n-gons, and `K.check` is clean.
- Hero size is inside every tolerance band (11.5 ± 0.5, 10.0 ± 0.6, 7.6 ± 0.3).
- The core touches all four pieces and clears every stone by at least 1.14.

**Against the sheet** (orthographic rasters at the sheet's elevations; side compared mirrored).

| View | Meteor W : H (shells only) | Profile error mean / worst | Glow share, ours / sheet | Lip share, ours / sheet |
| --- | --- | --- | --- | --- |
| front | 1.22 (H = 0.82 W) | 0.101 / 0.31 | 21.9 / 26.3 % | 14.2 / 5.6 % |
| side | 1.09 (H = 0.92 W) | 0.066 / 0.20 | 11.7 / 17.7 % | 13.0 / 8.5 % |
| rear | 1.27 (H = 0.79 W) | 0.066 / 0.28 | 16.9 / 24.2 % | 8.3 / 6.9 % |
| top | — | — | 16.0 / 27.0 % | 18.4 / 7.1 % |
| f34 (−14, 10) | — | — | 16.7 / 22.9 % | — |
| r34 (166, 10) | — | — | 13.5 / 17.4 % | — |

- **Front.** One tall dome, peaked over the back, with crack 1 on FL left of a large diamond window onto the core, and
  the front seam running up from the window's top to the crown. The core's crown is covered.
  - Window (f of the hero width): h 0.25 0.46–0.59 (sheet slot 0.53–0.62); h 0.49 0.36–0.71 (sheet 0.46–0.75, 3.9
    studs against 3.5); h 0.62 0.44–0.63 (0.43–0.69); closing to a point at h 0.76 (0.52–0.55; the sheet's top point
    0.44–0.49 at h 0.83).
  - Profile worst at f 0.50: the back seam's V notch at the crown shows through the top silhouette (ours 0.80,
    sheet 1.0). On the sheet that notch is seen only from the rear.
  - The sheet's crack 2 (right flank) is not reproduced; the right seam sits on the +X limb.
- **Side (mirrored).** A closed dome: BR's broad flank with its diagonal crack, the right seam as a glowing line, and
  the side window at f 0.52–0.72, h 0.25–0.62 (sheet f 0.62–0.87, h 0.22–0.69; ours sits 0.1 further back and is
  narrower).
- **Rear.** Matches best: two tall back pieces with a diamond window between them, h 0.58 f 0.38–0.65 (sheet
  0.37–0.66). It is a slot at the bottom (h 0.25, 0.50–0.53) and a point at the top (h 0.76, 0.48–0.54; sheet h 0.82,
  0.52–0.56). The back seam continues above and below, with a crack on each piece.
- **Top.** Four quadrant pieces round a central diamond of core with glowing cross seams, as the sheet's top view. The
  diamond is 2.2 studs wide (f 0.38–0.60) against the sheet's 4.4, and the seams' outer runs show as glowing channels.
- **f34 and r34:** the same read as front and rear.
- **Slots in the hero** (`crack_probe()`; ray pairs):

  | Slot | Opening | Floor | Depth |
  | --- | --- | --- | --- |
  | crack 1 (FL) | 0.30–0.41 | 0.12–0.17 (0.38 at the elbow notch) | 1.02–1.16 |
  | BR crack (and BL mirrored) | 0.30–0.37 | 0.13–0.15 | 1.03–1.04 |
  | right seam | 0.36–0.44 | 0.17–0.28 | 1.26–1.29 |

  - The tapered ends close to 0.1, depth 0.98.
  - The back and front seam probes run along the 0.08 hairline or into the openings, so their depth reads 1.1–2.7
    (through to the core).

**Left open.**
- **Glow shares are low by 4–11 points** (top worst: the crown opening is half the sheet's 4.4-wide diamond).
  - Widening the openings further eats the pieces' crowns, which the main session asked to keep.
  - The lip share is high instead (the opening rims and the hollow seen past the core's edge are `ember_lip`). On the
    sheet those rims render lit orange-red, so stage 4 can move the outer rim rows toward `ember_wall` / `core`. That
    would recover most of the gap in the O share.
- The seam walls of the openings have no depth rows (each rim is one frustum face). Stage 4 may need `K.refine` there
  for blends.
- **Stage 2:** min corners are 3.05–3.4° (target 5°, with the slot rows locked as before).


## Stage 2+3 — Cleanup and UV

All changes are in `m015.py`. I rebuilt with `m015.build()` in the open `FlintbornWorldKit.blend` and saved it through
the MCP. Every number below was re-measured through the MCP after the final build.

**Stage 2: `_polish(o)`** runs on each part after `_finish` and the ground keys, before the hero pastes the part, and
then on the hero. It leaves every face a triangle, opens every corner under `POLISH_LIM` = 5°, puts the origin back at
the bottom centre (the `m015_offset` follows) and re-makes the UVs. Each thin face gets the first of these that works,
least invasive first:

1. a near-flat same-key flip (`m009._flip_thin`; the surface moves at most 0.08);
2. `_slide`: a corner slides within its own flat facet, or along its own straight feature line (a slot row, lip line,
   crease or ground edge). Slot verts may slide too, because the surface and every row and key line stay where they
   are;
3. `_remesh`: the near-flat facet round the face (one key, normals within 3.5°) is re-triangulated as a constrained
   Delaunay triangulation (`mathutils.geometry.delaunay_2d_cdt`), with up to 12 new inner verts on the old surface.
   Nothing moves. New verts are kept out of the lens where they would make a thin triangle with an outline edge,
   which can't be split;
4. `m009._nudge_free` (up to 0.08) of a free corner;
5. `_collapse`: a free vert merges onto a neighbour up to 0.25 away. Two verts under `LOCK_MERGE` = 0.1 apart may
   merge even on a slot, and the smallest such move wins;
6. `_nudge_far`: the same nudge, searched over 26 directions, up to 0.1.

Every move is undone, or refused beforehand, if it makes faces cross.

- **Lock.** `_wall_verts` holds every vert within 1e-3 of a slot cutter's surface, plus every ember-wall vert.
  - The cutters are rebuilt from `ST`; the hero's include the 0.05 `SINK`.
  - That covers the lip line, chamfer row, 0.25 d and 0.55 d rows and the floor of every seam and crack.
  - The openings' rims and the hollow carry the lip key, but they are not slot rows, so they are free like the shell.
    Stage 1's slivers were mostly there: 66 of the hero's 107 sub-5° faces had all three verts on lip-keyed faces.
- **Determinism fix.** `m014._hull` passed `dissolve_limit` a Python set of edges, which iterates by memory
  address. The core therefore came out at 58 or 60 tris, with a min corner of 18.6° or 4.8° / 8.0°, from one build
  to the next, and the hero changed with it. `m015._hull` (also used by `base_rock`) passes the edges in index order.
  The core is now 58 tris and 18.61° on every build, which is stage 1's mesh.
- **`build()` now also returns** `corner5`, `interior` (ray parity: a point 2e-3 off a face along its normal lies
  inside on 2 of 3 rays), `inner_shells` (`m009._inner_shells`) and `uv` (`M.uv_stats`). Any non-zero result is added
  to `problems`. `POLISH_ON = False` rebuilds the stage-1 meshes for A/B checks.

**Operations per object (final build)**

| Object | Flips | Slides | Remeshes (new verts) | Nudges | Collapses (slot merges, largest move) |
| --- | --- | --- | --- | --- | --- |
| EmberMeteorDeposit | 1 | 6 | 8 (12) | 9 | 3 (1, 0.011) |
| EmberMeteorSlab | 1 | 1 | 7 (10) | 2 | 3 (3, 0.021) |
| EmberMeteorCap | 1 | 4 | 10 (14) | 3 | 0 |
| EmberMeteorChunk | 0 | 3 | 6 (8) | 2 | 2 (2, 0.030) |
| EmberCore, EmberMeteorBaseRock | — | — | — | — | — (already past 5°) |

### Measured (MCP, final build)

| Object | Tris / budget | Verts | Size (studs) | Shells | Non-manifold / boundary / wire / loose | Zero-area / dup verts | Quads / n-gons | Self-crossings | Interior faces / inner shells | Normals | Min corner (stage 1) | Origin offset | Transforms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EmberMeteorDeposit | 3468 / 4000 (3360) | 1724 | 11.13 × 10.24 × 7.34 | 1 | 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | outward | 5.01° (3.05°) | 0, 0, 0 | applied |
| EmberMeteorSlab | 628 / 1000 (614) | 314 | 5.75 × 4.17 × 6.95 | 1 | 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | outward | 5.27° (3.21°) | 0, 0, 0 | applied |
| EmberMeteorCap | 382 / 1000 (354) | 193 | 4.67 × 3.94 × 6.95 | 1 | 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | outward | 5.11° (3.06°) | 0, 0, 0 | applied |
| EmberMeteorChunk | 756 / 1000 (744) | 380 | 4.79 × 4.78 × 7.39 | 1 | 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | outward | 5.02° (3.36°) | 0, 0, 0 | applied |
| EmberCore | 58 / 1000 | 31 | 4.91 × 4.72 × 5.23 | 1 | 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | outward | 18.61° | 0, 0, 0 | applied |
| EmberMeteorBaseRock | 58 / 1000 | 31 | 2.41 × 2.25 × 1.30 | 1 | 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | outward | 9.85° | 0, 0, 0 | applied |

- On all six: no custom split normals, no modifiers, no parent or children, rotation 0 and scale 1, one UV layer
  (`UVMap`), and only the `FB_m015_*` keys in use. `K.check` reports nothing.
- **Purge.** `_drop_unused` removed 23 orphan M015 meshes: the build's temporaries and the replaced datablocks.
  - No `_m015_*` objects, orphan M015 meshes or unused `FB_m015_*` materials are left.
  - Every mesh is named after its object, and the collection holds exactly the six objects.
- **Hero gaps unchanged.** The core touches all four pieces and clears every stone by 1.14–3.57.

**Slots and silhouette against stage 1.** This is a true A/B: one build with `POLISH_ON = False`, which reproduces the
saved stage-1 `crack_probe()` and `measure()` exactly, then the final build.
- **Slot verts.** Every stage-1 slot vert lies within 0.0133 of the new surface.
  - Over 0.001: 12 of 945 on the hero, 3 of 237 on the slab, 0 of 100 on the cap, 4 of 301 on the chunk.
  - Over 0.01: one, the same vert on the slab and the hero, on the front seam's upper run (build (0.56, −2.10, 6.3)),
    where a slot merge took place.
- **Slot profile** (scratch probe `slot_profile`): the width across every seam and crack at 0.05, 0.25, 0.55 and
  0.85 d, at 9 stations each.
  - The slab, cap and chunk are identical to stage 1.
  - On the hero, the right seam and back seam widths differ by at most 0.006, apart from runs inside the openings.
  - The front seam's centre-ray depth changes by −0.015, −0.013 and +0.007 at three stations. That ray runs down the
    0.08 hairline onto the core.
- **`crack_probe()`.** Every opening is unchanged. The table below has the only changes; everything else matches
  stage 1 to two decimals.

  | Slot, station | Stage 1 | Now | Why |
  | --- | --- | --- | --- |
  | crack 1, station 0, floor | 0.38 | 2.17 | The depth went 1.142 → 1.148, so the floor ray at depth − 0.05 now passes just under the slot floor into the core gap at the elbow notch. At a fixed 0.85 d both builds read 2.11. |
  | front seam, stations 0 and 3, floor / depth | 0.88 / 1.69, 0.68 / 1.17 | 0.89 / 1.68, 0.65 / 1.18 | Hairline probe. |
  | back seam, stations 1 and 2, floor | 3.90, 3.15 | 3.92, 3.17 | Inside the rear and crown openings. |

- **Silhouette** (`measure()`).
  - Profile errors are unchanged: front 0.100 / 0.31 (was 0.101), side 0.066 / 0.20, rear 0.065 / 0.28 (was 0.066).
  - Single profile columns differ by 0.01, and the glow and lip shares by at most 0.003.
  - Renders: `front_sheet` and the stage-1 copy are indistinguishable by eye. Pixel diffs are 0.4–1.4 % of pixels,
    all along edges and the horizon line, which is sampling noise. The core and base-rock part shots are identical.

### UV (`M.uv_stats`, layer `UVMap`; Stage 3)

`UV_ANGLE` and `_uv(o)` follow M013 and M014. Each object gets a Smart UV island angle, its island borders become
seams, and each island is re-unwrapped ANGLE_BASED with an exact margin of 0.008 and `min_angle` equal to the angle,
so there is no silent fallback. Any faces the unwrap folds are cut free by `m012._uv_unfold`. For each object I
compared 35°, 40°, 45°, 50° and 55° on the polished meshes and chose by worst conformal stretch, then p95, then
fewest islands.

| Object (worst / p95, islands, faces cut free) | 35° | 40° | 45° | 50° | 55° | Chosen |
| --- | --- | --- | --- | --- | --- | --- |
| EmberMeteorDeposit | **1.054 / 1.007, 476, 59** | 1.118 / 1.010, 396, 8 | 1.070 / 1.014, 444, 67 | 1.170 / 1.023, 338, 72 | 1.544 / 1.064, 287, 97 | 35° |
| EmberMeteorSlab | 1.074 / 1.013, 48 | **1.033 / 1.010, 48, 1** | 1.073 / 1.011, 46, 2 | 1.047 / 1.016, 33, 1 | 1.312 / 1.060, 60, 26 | 40° |
| EmberMeteorCap | **1.029 / 1.008, 32** | 1.029 / 1.009, 28 | 1.034 / 1.013, 24, 1 | 1.049 / 1.020, 24, 1 | 1.049 / 1.023, 22 | 35° |
| EmberMeteorChunk | 1.048 / 1.010, 90, 34 | **1.018 / 1.010, 83, 34** | 1.094 / 1.014, 81, 34 | 1.094 / 1.014, 79, 34 | 1.094 / 1.023, 77, 34 | 40° |
| EmberCore | 1.056 / 1.053, 20 | 1.056 / 1.053, 14 | 1.056 / 1.053, 11 | **1.000 / 1.000, 8** | 1.143 / 1.132, 6 | 50° |
| EmberMeteorBaseRock | **1.021 / 1.015, 16** | 1.049 / 1.045, 11 | 1.082 / 1.070, 8 | 1.103 / 1.077, 8 | 1.089 / 1.079, 7 | 35° |

| Object | Angle | Islands | Overlaps / cross-island | Flipped | Faces cut free | Min gap / border | Fill | Density min / med / max | Conformal worst / p95 | Area worst | Worst angle change | px / stud at 1024 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EmberMeteorDeposit | 35° | 476 | 0 / 0 | 0 | 59 | 0.016 / 0.008 | 0.275 | 1 / 1 / 1 | 1.054 / 1.007 | 1.046 | 2.15° | 24.2 |
| EmberMeteorSlab | 40° | 48 | 0 / 0 | 0 | 1 | 0.016 / 0.008 | 0.471 | 1 / 1 / 1 | 1.033 / 1.010 | 1.044 | 1.17° | 66.0 |
| EmberMeteorCap | 35° | 32 | 0 / 0 | 0 | 0 | 0.016 / 0.008 | 0.427 | 1 / 1 / 1 | 1.029 / 1.008 | 1.044 | 1.23° | 72.2 |
| EmberMeteorChunk | 40° | 83 | 0 / 0 | 0 | 34 | 0.016 / 0.008 | 0.434 | 1 / 1 / 1 | 1.018 / 1.010 | 1.023 | 0.94° | 59.0 |
| EmberCore | 50° | 8 | 0 / 0 | 0 | 0 | 0.016 / 0.008 | 0.374 | 1 / 1 / 1 | 1.000 / 1.000 | 1.000 | 0.00° | 71.4 |
| EmberMeteorBaseRock | 35° | 16 | 0 / 0 | 0 | 0 | 0.016 / 0.008 | 0.523 | 1 / 1 / 1 | 1.021 / 1.015 | 1.014 | 1.15° | 209.6 |

- The faces cut free are union S-steps: the chunk's 34 at every angle, where the slots meet the hollow, and the
  hero's 59.
- The hero's fill (0.275, 24 px per stud) is low because 476 islands each carry the margin. That is harmless: the
  GLB exporter writes its own palette-cell UVs, and this layer only has to exist and be clean.

### Left for later stages

- Stage 4 onwards as listed under Stage 1. Remeshed facets keep their key and Tint value, so stage 4's fields colour them
  like their neighbours.
- The hero has 532 tris of headroom (3468 / 4000) for any stage-4 `K.refine`.

## Stage 4 — Materials, colour and texture

All changes are in `m015.py` (`palette()`, `calibrate()`, `colour()` / `colour_all()`, `report()`), run from
`finish_stages()` at the end of `build()`, after stage 2's polish and stage 3's UVs. Stage 4 only changes material
indices and Tint, so there are no geometry or UV changes and no `K.refine`. The rims needed no refine: the booleans and
the polish had already split each rim wall into 60–110 triangles, so a per-face depth grade is fine enough. Rebuilt in
the open `FlintbornWorldKit.blend` and saved through the MCP. All numbers were measured through the MCP on the final
build.

### Method

- **Faces are classified by the construction surface they lie on**, not by key or facing (`_classify`). The classes
  are:
  - rock: the hero's base-key faces;
  - core: on the core hull at `CORE_AT`;
  - ground: z = 0;
  - slot: on a seam or crack cutter;
  - `rim_<opening>`: on an opening frustum;
  - hollow: on the 0.9-scale hollow;
  - dome: within 0.15 of the uncut dome;
  - sector: the hidden seam hairline walls.
- Everything is in the shared piece build frame:
  - the hero's mesh + offset + SINK;
  - a part's mesh + offset;
  - the core part + `CORE_AT`.
  So the slab, cap and chunk parts are coloured face for face like the same piece in the hero. Each base rock uses
  its own part frame, through its placement.
- The pass repeats: Tint is reset first, and the classes come from the geometry.
- **Measured with the study's own masks.** `report()` renders the hero at the sheet's angles (front / side / rear at
  el 7, top 78, f34 (−14, 10), r34 (166, 10)). It applies `measure.py`'s `cls()` (O / L / S / B), ported to numpy as
  `_cls_px`, inside the hero's own pixels, using a label render as the mask. `sheet_stats()` runs the same masks on the
  sheet's view boxes.
  - The full-box sheet shares differ slightly from §1.2's bbox shares: front 24.5 %, side 16.3 %, rear 22.4 %,
    top 23.8 %, f34 20.7 %, r34 15.6 %.
  - `light=True` realises the sockets' PointLights (no particle stand-ins).

### Sampling and calibration (two passes)

- **Targets** are §5.4's rendered medians (`TARGETS`).
- **Pass 1, test dome** (`calibrate()`): the m009 / m014 wrapper. Stone keys are sampled unfiltered, the Neon preview
  is kept on every round, and the `T_Calib` meshes are purged.
- **Pass 2, hero** (`report()`, VFX off): the shell family rendered 9–26 levels under the sheet in the lit views
  (front `#4E484E` against `#685E64`; f34 `#575057` against `#60595F`; top `#575156` against `#61595E`). The dome's top
  faces the key light and the hero's flanks don't, the same as M014. So the four shell keys were scaled ×(1.41, 1.38,
  1.34) in linear light, the geometric mean of the three views' gains.
- The rocks matched straight from pass 1 (front `#AC9389` against `#AF968C`), so they kept their pass-1 hexes.

| Key | Target (rendered) | Dome render | Final hex | Rough | Emission | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `m015_shell` | `#5F585E` | `#615A60` | `#534F58` (pass 2) | 0.88 | 0 | |
| `m015_shell_light` | `#7C7378` | `#7C7378` | `#6C676F` (pass 2) | 0.88 | 0 | |
| `m015_shell_dark` | `#45404A` | `#49444C` | `#3B3743` (pass 2) | 0.9 | 0 | |
| `m015_shell_warm` | `#685D5E` | `#695F60` | `#5B5358` (pass 2) | 0.88 | 0 | used only through its 25 / 50 % mixes |
| `m015_ember_lip` | `#5E2620` | `#5C2720` | `#4A211D` | 0.85 | 0 | specular 0.06 |
| `m015_ember_wall` | `#B04A2C` | `#AF4A2D` | `#A74F34` | 0.75 | **1.0 (Neon)** | stage 5 decision |
| `m015_core` | `#FD7428` | `#FF7429` | `#FB7430` | 0.5 | **1.0 (Neon)** | |
| `m015_core_hot` | `#FDB548` | `#FFB449` | `#FBAB4E` | 0.5 | **1.0 (Neon)** | |
| `m015_core_deep` | `#D9441A` | `#D7441A` | `#A33A16` | 0.5 | 0 | solid, lit; specular 0.06 |
| `m015_base` | `#B39A8F` | `#B1998E` | `#857774` | 0.92 | 0 | was the placeholder `#B39A8F`, which rendered peach `#E7C0A9` |
| `m015_base_light` | `#C8AFA3` | `#C8AFA4` | `#968885` | 0.92 | 0 | |
| `m015_base_dark` | `#8F786D` | `#8D786C` | `#6A5D58` | 0.92 | 0 | used only through its 25 / 50 % mixes |

- Mix keys come from `K.mix_key` and are solid. They include `shell_x_light/dark/warm_25–75`, `ember_lip_x_ember_wall_50`,
  `ember_lip_x_core_deep_25–75`, `shell_warm_x_ember_lip_50` and `base_x_light/dark_25–75`.
- `EMBER_SPEC` puts 0.06 specular on every lip, rim and deep key, mixes included. Flintkit made the mixes at 0.2, and a
  white sheen turned the lit front rim salmon pink (lit quartile `#D8716A`).

### Colouring (position fields; never by facing)

- **Shell outside (dome faces):**
  - one tone per coplanar facet, from broad noise at the facet centre (scale 0.2, dead zone 0.12, quarter steps toward
    `shell_light` / `shell_dark`);
  - minus a ground band among the rocks (hero z < 1.0 → −0.5, < 2.0 → −0.25);
  - per face, warm spill from the distance to the nearest glow surface (core hull, slot cutter or opening frustum):
    < 0.2 → 50 % `shell_warm`, < 0.45 → 25 %.
  - The spec's 0.25 / 0.5 / 0.9 ramp warmed 68 % of the shell's area, because four seams and two cracks put most
    broad facets' centres within 0.9 of a glow. Now the warm faces are only the narrow fragments along the rims and
    slot lips.
- **Seam hairline walls (hidden):** `shell_dark` down to 0.3 deep, then `ember_lip`.
- **Slots (seams and cracks):** graded by depth below the uncut dome as a fraction t of the nearest station's slot
  depth:
  - t < 0.07, the chamfer row: `ember_lip`, the dark lip line;
  - < 0.25, the lip row: `ember_lip_x_ember_wall_50`, solid red-brown;
  - < 0.55: `ember_wall` (Neon);
  - < 0.93: `core` (Neon);
  - the floor: `core_hot` where the local opening G ≥ 0.28, otherwise `core`, so the tapered crack ends and the seams'
    closed feet cool.
  - Hero floors: 79 faces hot, 30 cooled to core.
  - The first try, with plain lip on the whole lip row, left the cracks reading as dark grooves from the front (slot
    median `#381511`, L share twice the sheet's). The sheet's crack deciles run about 1 lip, 2 red-brown and 7
    orange / hot.
- **Window rims** (each piece side is one frustum wall): s = (distance to the dome) / (distance to the dome + distance to
  the core), so 0 is the outer edge and 1 the core.
  - s < 0.2: `shell_warm_x_ember_lip_50`;
  - < 0.35: `ember_lip`;
  - < 0.55: `lip_x_deep_50`;
  - < 0.75: `lip_x_deep_75`;
  - beyond: `core_deep`.
  - All solid, so the big rim faces keep their lit facet steps and read lit orange-red next to the core (front rim
    median `#8A3922`, lit `#CA4822`), dark red at the lip. That is the spec's cavity gradient: shell → shell_warm →
    ember_lip → the core's colours.
  - Hollow faces get `lip_x_deep_25`. This happens only on the parts; the hero's hollow is inside the core.
- **Core:** hf is the height fraction, folded back above 0.8 with slope 1.5. Then
  u = 0.75 hf + 0.22 × (x / rx) + 0.15 × noise:
  - u < 0.24: `core_deep`;
  - u < 0.56: `core`;
  - otherwise: `core_hot`.
  - In the hero, a core face within 0.4 of a shell is `core_deep` (occlusion strips under the rims).
  - Why: the spec's (+X, +Y) lateral term made the whole back of the core hot (rear `#FFB348`), and height at full
    weight made the crown hot from the top (`#FFB348` against the sheet's orange `#FC7325`). A lateral weight of 0.35
    made the side window all hot; 0.15 lost the front's hot facets. With the fold and a +X lean of 0.22, the front,
    side, top and f34 windows each read an orange median with a hot lit quartile, as the sheet does.
  - The core part reads hot upper right, orange belt and deep lower left, like the exploded core: 13 hot, 26 core and
    19 deep of its 58 faces.
- **Base rocks** (each in its own part frame):
  - light patches by noise (scale 0.7) toward `base_light`;
  - in the hero, faces within 0.25 / 0.5 of a shell go 50 / 25 % toward `base_dark` (a soft contact band against the
    dark shell), the crown never.
  - The ground-contact row (u < 0.22 → 25 % dark) was tried and dropped: K.check's baked-shading score went to 0.80 on
    the 58-tri stone, whose low ring is its down / outward-facing ring (as on M009).
- **Tint:** one value per coplanar facet group, so there is no per-triangle confetti. Tint = per-piece level × (1 +
  amp × 1.6 × broad noise):
  - shell: amp 0.06, scale 0.45; piece levels FL 1.0, FR 0.97, BR 1.03, BL 0.98;
  - walls and rims: amp 0.03;
  - core_deep: amp 0.03;
  - rocks: amp 0.05 in each rock's own frame with its own noise offset, and per-rock levels 0.97–1.03;
  - the Neon keys: Tint 1 (the exporter ignores it).
- **K.check:** clean on all six objects. Baked-shading scores: hero 0.10, slab 0, cap 0, chunk 0.04, core 0, rock 0. No
  waiver was needed; `SHADING_OK` is kept for the case that it trips.

### Re-measured against the sheet (final build; `cls()` masks; VFX off / VFX on)

| View | Glow O share, sheet / ours off / ours on | Lip L share, sheet / off / on | Shell S median, sheet / ours (on) | Glow O median and lit quartile, sheet / ours (on) | Base B median, sheet / ours (on) |
| --- | --- | --- | --- | --- | --- |
| front (0, 7) | 24.5 / 24.9 / 27.0 % | 5.2 / 12.9 / 11.5 % | `#685E64` / `#595258` | `#FC7D27` `#FDB745` / `#FF7429` `#FFB449` | `#AF968C` / `#AE9489` (off `#AB9389`) |
| f34 (−14, 10) | 20.7 / 21.9 / 24.1 % | 5.4 / 12.1 / 10.0 % | `#60595F` / `#645C63` | `#FD7C25` `#FEB747` / `#FF7329` (core region lit `#FFB449`) | `#AC9389` / `#B0988D` |
| top (0, 78) | 23.8 / 21.9 / 22.1 % | 6.2 / 12.1 / 12.7 % | `#61595E` / `#645C62` | `#FC7325` `#FECD5A` / `#FF7329` (core region lit `#FFB449`) | `#C1A699` / `#B0978B` |
| side (90, 7) | 16.3 / 12.2 / 12.3 % | 7.8 / 4.9 / 5.0 % | `#5D565D` / `#534D54` | `#FC6C23` `#FDB040` / `#FF7329` `#FFB449` | `#B2978C` / `#84736C` (studio shade) |
| rear (180, 7) | 22.4 / 16.8 / 17.5 % | 6.3 / 7.3 / 8.1 % | `#5B545A` / `#545057` | `#FB6521` `#FEB140` / `#FF7429` `#FF7429` | `#B49A8D` / `#8E7B75` (studio shade) |
| r34 (166, 10) | 15.6 / 15.3 / 16.5 % | 6.5 / 7.9 / 8.3 % | `#5C555A` / `#555057` | `#FC6F22` `#FDAA3B` / `#FF7329` `#FF7429` | `#B2978A` / `#8E7974` (studio shade) |

- **Glow share** against stage 1's placeholder shares, which were 4–11 points under:
  - front, f34, top and r34 are now within ±3.4 with the lights on (front +2.5, f34 +3.4, top −1.7, r34 +0.9);
  - side is −4.0 and rear −4.9. Those windows are narrower than drawn (stage 1 geometry), and their rims sit in the
    studio key light's shade.
  - The recovery came from the rim walls, graded to lit lip → deep orange-red that counts as O, and the Neon
    `ember_wall` row in every slot.
- **Lip share** is still 1.5–2.4× the sheet's in front, f34 and top. Our rims are wider flared walls than the sheet's
  thin red edges: stage 1's `flare` 1.22 makes their outer band and shade quartile dark red. Side, rear and r34 are
  within 1.8 points.
- **Shell:** f34 +4, top +3, r34 −6, rear −6, side −10, front −15 levels (sum of channels / 3).
  - The front and f34 disagree in opposite directions: the sheet's front is lighter than its f34, ours is darker. One
    palette can't match both; the average error of the three lit views is −3.
  - Side and rear sit in the kit studio's shade (key light from the front-left). The sheet lights every view.
- **Glow:** every window's O median is `#FF7329`–`#FF7429` against the sheet's `#FB6521`–`#FD7C25`. Every lit
  quartile except the rear and r34 reaches the hot key, as the sheet's do. The rear and r34 cores show no hot facet
  (the hot lean is +X).
- **Rocks:** front and f34 are within 4 levels of the sheet, and VFX on moves the front rock median by +3 levels
  (`#AB9389` → `#AE9489`), so there is no orange wash. The top-view rocks are 16 darker than the sheet's (`#C1A699`).
  Side, rear and r34 are in studio shade.
- **Cracks:** slot region (front / f34, VFX on) medians are `#562217` / `#6A2A1C` with lit quartile `#AF4A2D`, against
  the sheet's crack quartiles `#6F3026` / `#E25D21` / `#FAA829`.
  - The label region includes every seam's lip rows seen in shade, so the median is darker than the sheet's crack-1
    box.
  - In the renders every crack and seam reads as a glowing slot: a dark lip line, the red-brown Neon wall, the
    orange core row and the hot floor in the wide stretches.

### Parts and notes

- **Parts are coloured like the hero**, face for face, by the same build-frame fields. Their hollow sides (the cap's
  and chunk's inner faces) read graded lip → orange-red.
- **Purged:** `_drop_unused` drops calibration meshes and unused `FB_m015_*` materials (including the unused parent
  keys `shell_warm` and `base_dark`, which are kept in the palette and set by `palette()`).
- **Left for stage 1 / 2 (geometry, not changed here):** on the `EmberMeteorSlab` part render, the crack-1 elbow notch
  shows a white pin-hole: the slot floor breaks through into the hollow, as stage 2 recorded ("crack 1, station 0,
  floor 2.17"). In the hero the core fills it.

## Stage 5+6 — Lighting and VFX

### Stage 5: lighting

- **Neon keys: `m015_core` `#FB7430`, `m015_core_hot` `#FBAB4E` and `m015_ember_wall` `#A74F34`**, all at emission 1.0
  (the exporter's `GLOW_EMISSION`). The Blender preview shows them unlit (`_glow_mats`), as Roblox's Neon does. **The
  export should report 3 glow pieces**, not the spec's 2.
  - Why ember_wall is Neon: with it solid, the slot walls sat in their own shade and rendered `#381511`–`#481810`, and
    the cracks read as dark grooves. On the sheet they glow red-brown to orange (the M009 lesson that made its ember
    band Neon).
  - Depth grading is kept by colour steps: dark solid lip → solid red-brown lip row → Neon red-brown wall → Neon
    orange → Neon hot floor.
  - `core_deep`, the lip, the rim mixes and every shell and rock key stay solid and lit, so the rims and the core's
    lower facets keep their facet shading.
- **Lights (PointLights in the window recesses, in the open, shadows on, flicker on):**

  | Light | Build point | Hero-local Roblox (x, y, z) | Colour | Brightness | Range | Clearance |
  | --- | --- | --- | --- | --- | --- | --- |
  | front window (`heat_glow_1`) | (0.9, −4.3, 3.6) | (0.47, 3.60, 3.98) | `#FF7A22` | 0.7 | 10 | 1.42 from the nearest surface, outside the solid |
  | back window (`heat_glow_2`) | (0.3, 3.6, 4.2) | (−0.13, 4.20, −3.92) | `#FF7A22` | 0.9 | 8 | 1.28, outside |

  - Changed from the spec's 0.9 / 0.6. With those, the front rims lit to O and front / f34 went 4.6 / 5.1 points over
    the sheet's share. The back window faces away from the studio key, so its light carries more.
  - Neither light is inside the meteor; a ray-parity check confirms both are outside.
  - With the lights on, the rocks moved at most 3 levels (no peach wash), and the rims next to the windows read lit
    orange-red (front rim `#713822` → `#8A3922`).
- **Studio notes:**
  - The sheet's soft halo hugging the silhouette (`#F8DCC0`–`#F9D5B0`) relies on the place's default Bloom over the
    Neon core and walls, plus the heat_glow puffs.
  - With Bloom off, the Neon still reads and the emitters carry the halo.
  - Both lights cast shadows, so the shells keep the light in the windows; that costs two shadowed PointLights per
    node.

### Stage 6: VFX

Sockets go on the hero only (`_vfx`, via `K.socket` on the finished hero; `SOCKETS`). `fx_check()` tests every socket
and its spawn box on a 5³ grid (ray parity).

| Socket | Build point | Emitter | Clearance | Grid points inside the hero |
| --- | --- | --- | --- | --- |
| `heat_glow_1` | (0.9, −4.3, 3.6) | Heat: `glow_soft`, `#FFB347` → `#FF6A1A`, size 1.4–2.0, transparency 0.6–1.0, rate 2.5, speed 0.2–0.4, shape [1.8, 2.4, 0.4] (fits inside the front window's diamond) | 1.42 | 0 / 125 |
| `heat_glow_2` | (0.3, 3.6, 4.2) | the same, rate 2.0, shape [1.4, 2.2, 0.4] | 1.28 | 0 / 125 |
| `embers_1` | (0.3, 0.0, 8.4), above the crown | Embers: `ember_dot`, colour sequence `#FEBD79` → `#FD6A22` → `#FE5A1B`, size 0.55 → 0.45 → 0.15, lifetime 2–3.5, rate 3, speed 0.6–1.4, spread 70, drag 0.6, rise 0.5, shape [4.0, 0.6, 3.5] | 1.73 | 0 / 125 |
| `embers_2` | (0.9, −5.6, 2.6), in front of the front window | the same, rate 1.5, shape [2.0, 1.0, 0.6] | 1.59 | 0 / 125 |

- The ember colours and sizes are the sheet's VFX panel shards: 0.4–0.8 studs, orange `#FD6A22` / `#FE5A1B`, hot
  `#FEBD79`, shrinking to 0.15 sparks.
- The spec's E1 point (0.5, −0.4, 6.4) was moved above the dome top (z 8.4): at z 6.4 a 5 × 1 × 4 spawn box would
  reach into the shell round the crown opening.
- **Not added** (the sheet shows none): smoke, dust, ore_glint, heat shimmer, and harvest sockets (main-session
  decision).
- **Renders:** `render_views` now renders with `vfx=True` (the lights plus the glow and ember stand-ins). The stand-ins
  don't veil the model: soft puffs over the windows and a few floating shards. The compare numbers above come from
  `report()`, with VFX off (no lights) and on (lights only).
- **For the main session's export:** the STATS line should report 4 sockets and 3 glow pieces (core, core_hot,
  ember_wall).

### Build fixes (after verifier round 1)

Built in the GUI through the MCP with `m015.build()` and saved. The finish stages ran unchanged inside the build: the
palette, the colour pass and the sockets.

**What crashed Blender (twice) and what fixed it.**
- **The crash.** In stage 2's `_remesh`, a near-degenerate old triangle passed `intersect_point_tri_2d` and gave
  barycentric weights of about 1e7. The "lifted" new vertex landed 16 million studs below the Chunk, and the hero's exact
  union then crashed inside `meshintersect::find_patches`.
- **Diagnosis.** Reproduced headless in a throwaway background Blender that never saved, with `bg_build.py` in the
  scratchpad. Each step was traced until the Chunk's `_polish` showed the wild vertex.
- **Fix 1:** `lift()` accepts only weights inside the triangle.
- **Fix 2:** `_remesh` gives up on a region where a locked vertex would lose all its edges (a dead-vertex reference).
- **Guard:** `_sane()` stops the build before the hero's unions if any part has a vertex more than 30 studs out.
- **Core check:** `core_present` in `build()` checks by ray parity that the core survived the unions. Cutting FR's
  front and side windows one at a time had left a crossing face pair, and core ∪ FR came out empty, so the core vanished
  silently. FR's front and side frusta are now one cutter, with the pillar taken out of it; then the crown is cut.

**Findings.**
1. **Slab see-through at crack 1: fixed.**
   - `_cap()` limits every slot station's depth to the shell thickness below it (to the hollow or an opening),
     minus 0.15. Stations capped: crack 1 4, BR crack 2, right seam 3, back seam 3, front seam 9.
   - Crack 1's upper stations are now 0.73 / 0.60 deep (they were 1.0 through a 0.8-thick wall).
   - The Slab is a closed genus-0 surface (Euler characteristic 2; it was 0).
   - A bow-tie vertex that the sliver collapse left at the front window's top corner (χ 1) is split by
     `_fix_bowties()`.
2. **Sightlines.**
   - The back seam now overlaps 0.08 (`SEAM_HAIR["back"]` = −0.04). BR and the mirrored BL fuse along the mirror plane;
     the coincident cut faces union cleanly.
     - Overlapping every seam broke the hero (the core was lost, 4 crossings), so the front, right and left seams keep
       their 0.08 gap.
   - FR keeps a pillar between its front and side windows (`PILLAR_AZ` −60 … −47).
   - The dome's back lift is zero on the seam plane, and the summit ridge sits in front of the crown opening.
   - The rear window's centre is 0.6 lower.
   - `see_through()`, raster holes at about 0.026 stud per pixel over 16 views:
     - hero: (180, 7) 3 px and (−45, 45) 4 px, both grazing slits under 0.05 stud wide over the core's crown, between
       the crown shaft's rim and the rear / front window rims;
     - before: front 3, rear 11, top 7, (45, 20) 1, (−45, 20) and (135, 20) reported by the verifier;
     - Chunk: none.
     - Slab: 5 px at (0, 78), and Cap: its two windows. Both are the part's own openings into its open hollow (there is
       no core in a part). The Cap is genus 1 by design: the pillar bridges its two windows.
   - Closing the last grazing slits by keeping every window's top under a crown shaft started at 5.2 made the Slab and
     Chunk polish cross faces and lost the core. Reverted, and recorded in `OPENINGS`.
3. **Back-seam V on the front silhouette: fixed.** The back seam closes over el 64–72. The front profile at mid-width is
   0.98 / 0.99 (it was 0.80).
4. **Windows.**
   - Rear: hw 2.3. At h 0.49 it spans f 0.38–0.65 (sheet 0.37–0.66). Rear glow 22.0 % against the sheet's 24.2 % (the
     verifier's 22.8 %); it was 17.5 %.
   - Side: hw 1.8, moved forward, but its front part is held back by the FR pillar. At h 0.49 it spans f 0.57–0.65
     (sheet 0.62–0.87). Side glow is 8.5 % against 17.7 %. **Still open**: the pillar and the side window trade off.
5. **Rocks.** A larger table:
   - F4 2.6 tall (0.34–0.35 H at the front, against the sheet's 0.39); F2, S1, B2 and B4 at 0.25–0.3 H.
   - The front rock tops now read 0.16–0.34 H (the sheet's 0.09–0.39).
   - Rock cover of the silhouette: front 25.2 %, side 24.1 %, rear 23.7 %, top 22.2 % (sheet 26–29 %; it was 13–16 %).
   - The core clears every stone by at least 0.35 (F4).

**Polish and cleanup additions.**
- `_force5()`: `m012._force_slivers` at 5° and then `_merge_needles` (merging needle edges under 0.05, kept only if the
  mesh stays manifold with no crossings), then `_polish` again for the origin and the UVs.
- `_fix_bowties()`.
- `_ground_slivers` (floor caps).

**Measured (MCP, final saved build).**

| Object | Tris | Size (studs) | Shells | Non-manifold edges / verts, boundary | Crossings | Interior | Min corner | UV islands / overlaps / flipped |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EmberMeteorDeposit | 3862 / 4000 | 11.08 × 10.50 × 7.55 | 1 | 0 / 0, 0 | 0 | 0 | 5.00° | 475 / 0 / 0 |
| EmberMeteorSlab | 682 | 5.75 × 4.17 × 7.60 | 1 | 0 / 0, 0 | 0 | 0 | 5.09° | 91 / 0 / 0 |
| EmberMeteorCap | 442 | 4.67 × 3.97 × 7.47 | 1 | 0 / 0, 0 | 0 | 0 | 5.08° | 59 / 0 / 0 |
| EmberMeteorChunk | 796 | 4.87 × 4.61 × 7.34 | 1 | 0 / 0, 0 | 0 | 0 | 5.02° | 104 / 0 / 0 |
| EmberCore | 58 | 4.91 × 4.72 × 5.23 | 1 | 0 / 0, 0 | 0 | 0 | 18.6° | 8 / 0 / 0 |
| EmberMeteorBaseRock | 58 | 2.41 × 2.25 × 1.30 | 1 | 0 / 0, 0 | 0 | 0 | 9.9° | 16 / 0 / 0 |

- Hero size is inside all three bands (11.5 ± 0.5, 10.0 ± 0.6, 7.6 ± 0.3). The core is present; no inner shells; `K.check`
  is clean.
- **Sockets** (`fx_check`): all four outside the solid, with no spawn-box point inside. Clearances: embers 1.75 / 0.98,
  heat_glow 1.55 / 0.99. The front heat_glow moved to (0.9, −4.9, 3.8): after the rocks grew, 6 of its 125 spawn points
  were inside.
- **Slots** (`crack_probe`; opening / floor / depth):
  - crack 1: 0.30–0.40 / 0.12–0.18 / 0.60–1.02;
  - BR crack: 0.30–0.37 / 0.13–0.15 / 1.03–1.04 (0.85–0.98 at the tapers);
  - right seam: 0.36–0.44 / 0.17–0.21 / 1.26–1.27.
  - The other seam stations fall in the hairline or the openings, so their probe values are not slot depths.
- **Against the sheet** (glow share ours / sheet; profile error mean / worst):

  | View | Glow share | Profile error |
  | --- | --- | --- |
  | front | 21.9 / 26.3 % | 0.090 / 0.27 |
  | side | 8.5 / 17.7 % | 0.090 / 0.24 |
  | rear | 22.0 / 24.2 % | 0.093 / 0.29 |
  | top | 15.6 / 27.0 % | — |
  | f34 | 20.4 / 22.9 % | — |
  | r34 | 17.3 / 17.4 % | — |

  Meteor W : H 1.25 (front), 1.05 (side), 1.25 (rear).
- **Renders** (`M015_views.png`, VFX on): one rounded meteor dome on a ring of broad pale stones. The core shows through
  the front and rear diamonds and the crown, and crack 1 runs beside the front window. The side view shows its window
  and the right seam; the underside is dark stone.

**Left for the Finish agent / round 2.**
- Side glow (8.5 % against 17.7 %) and top glow (15.6 % against 27 %) are still low. Widening the side window means
  narrowing or moving the FR pillar (sightlines); widening the crown eats the crowns.
- Two grazing see-through slits remain in the hero (3–4 px, under 0.05 stud).
- The lip share is 9–13 % against the sheet's 6–9 %: the rims are dark; colour could lift the outer rim rows.
- The colour pass ran on the new geometry, but nobody re-calibrated it against the new rims and pillar.

## Verifier round 1: findings for stages 4–6 (main session, 2026-10-28)

The round-1 verifier failed 015 at 6/10. Its build findings are handled under "Build fixes (after verifier round 1)" above. These are the colour, lighting and VFX findings, which the next modeller must fix:

- **Cracks read as dark grooves, not glowing embers (blocker).**
  - Lip rows dominate the crack faces. Keep the dark-red lip only on the chamfer row.
  - Make the crack walls Neon `ember_wall` from depth 0.07–0.25, and `core` from 0.3 down.
  - Push `ember_wall` toward `#D85A22`, so the crack medians land near the sheet's `#E25D21` and more than 60 % of crack pixels read bright.
- **Rim colour.** The window rims give a dark-red lip share of 9–13 %, against the sheet's 6–9 %. Lift the outer rim rows toward orange (less lip).
- **Shell contrast is low.** Use a noise dead zone of 0.05 and full light/dark facets, so the dark shell mottling reads like the sheet.
- **Embers only at the crown and front.** Add flank ember sockets, left and right, outside the solid (`fx_check`).
- **Glow share still short after the build fixes:** side 8.5 % against the sheet's 17.7 %, and top 15.6 % against 27.0 %. Colour can recover part of this (brighter crack walls on the side and crown). A geometry change to the FR pillar or the crown opening must not reopen the sightlines (`see_through`) or eat the crowns.
- Re-calibrate (`K.calibrate`) against the new rims and pillar. The existing colour pass ran on the new geometry, but was never re-measured.

## Stage 4–6 (round 2)

Modeller round 2, after verifier round 1 (the work list above). Run in a background Blender (`bgmcp.py`, port 9879,
work file `art/blender/assets/kit/wip/M015.blend`), never the GUI. Every change is in `m015.py`. No geometry, UV or
slot-cutter change: the colour pass, the palette, the measurement code and two sockets only. The full `m015.build()`
was re-run at the end; every geometry number is identical to "Build fixes (after verifier round 1)".

### What changed in the builder

- **Cracks and seams (`SLOT_ROWS`, `FLOOR_HOT_G` 0.28 → 0.22).** The old lip → wall 50 % row was solid and sat in the
  slot's own shade, so 81–97 % of crack pixels fell in the dark lip class L (the sheet: 16–23 %).
  - A probe of the slot faces showed why moving the hot row deeper did nothing. A 0.3-wide, 1.0-deep slot shows only its
    chamfer and the top quarter of its far wall from any sheet view. Moving hot from t 0.93 to 0.45 changed no crack pixel.
  - The four depth steps are therefore packed into what is seen:
    - the chamfer (t < 0.07): `ember_lip`, the dark lip line;
    - wall band 1 (t 0.08–0.25), split at its triangles' centroids: upper `ember_wall`, lower `core` (a red → orange
      sawtooth that reads as a gradient along the crack);
    - band 2 down (t ≥ 0.3): `core_hot`, cooling to `core` where the slot narrows (G < 0.22), as the floor does.
  - Hero slot faces: 681 hot, 97 cooled.
- **`ember_wall` → `#C95E2A`** (renders `#D75B23`; the verifier's target `#D85A22`), still Neon. Its Tint is now 1, like
  `core` and `core_hot`, so every Neon key is one flat colour.
- **Window rims (`RIM_KEYS`, `RIM_STEPS`, `_pillar_wall`).** Bands, outer → core:
  1. `shell_warm`;
  2. `shell_warm` / `ember_lip` 50 (the thin dark lip line);
  3. `ember_lip` / `core_deep` 75;
  4. `core_deep` (solid, lit orange-red);
  5. Neon `ember_wall` at the junction.
  - The band limits are set per opening, because the flared rims fill very different shares of each view.
  - The FR pillar's two cut walls are told apart by construction plane (`_f` front-window side, `_s` side-window side).
  - Measured by making one opening's rims fully Neon and the rest grey (glow points added, % of the meteor):

    | Rims | Points added per view |
    | --- | --- |
    | front frustum | front 3.7, f34 1.8, top 1.6 |
    | pillar, front-window wall | front 6.5, f34 7.9 |
    | pillar, side-window wall | side 7.9 (no other view) |
    | rear frustum | rear 8.2, r34 10.1 |
    | crown | top 7.0 |
    | side frustum | front 8.0, f34 3.9, top 3.2, side 1.9 |

    - With every rim grey: front 22.7, side 6.2, rear 17.1, top 18.2, f34 19.8, r34 13.6 %.
  - Final `RIM_STEPS` (the s where bands 1–4 end):

    | Rims | Bands 1–4 end at s |
    | --- | --- |
    | front, pillar_f | 0.62 / 0.72 / 0.84 / 0.92 |
    | pillar_s | 0.05 / 0.08 / 0.1 / 0.12 |
    | side | 0.35 / 0.45 / 0.58 / 0.68 |
    | rear | 0.45 / 0.55 / 0.68 / 0.78 |
    | crown | 0.1 / 0.15 / 0.2 / 0.25 |

  - So the side window's main rim, as the side view sees it (the pillar's side-window wall), glows almost wholly. That
    is the side-glow recovery, without touching the pillar geometry.
- **Facet flood bug fixed (`_facets`).** `m012._facets` floods into any edge-connected coplanar face, whatever its class.
  The core loop therefore painted 17 rear-rim faces `core_deep` (a core facet was coplanar with them), and the Tint
  groups ran across class borders. `colour()` now uses a flood bounded to the list it is given.
- **Core (`CORE_LAT` 0.22 → 0, `CORE_FWD` 0.07 toward −Y, `CORE_NOISE` 0.15 → 0.2, `CORE_CAP` / `FOLD` 0.75 / 1.5,
  `CORE_BANDS` (0.24, 0.44), `CORE_OCC` 0.4 → 0.25).**
  - Before, every window core measured lit quartile `#FF7429` (no hot facet showed) and the side window 83 % hot.
  - The occlusion strips in shade read L (front core 19 % L).
  - The 58 facets make the hot share jump a facet at a time (front 26 / 53 % at band 0.44 / 0.43). The band keeps
    every window's median orange with hot facets in the lit quartile.
- **Shell tone (`SHELL_TONE`):** dead zone 0.12 → 0.05, width 0.3 → 0.15 (full light/dark steps), seed 15061 → 15071.
  - With full steps, 15061 put a dark bias on the front quarter (14 sq studs `shell_dark` against 5 `shell_light`;
    front shell median 20 levels under the sheet).
  - Of eight seeds, 15071 is even (mean tone front +0.11, back −0.06, left −0.22, right +0.34). It keeps K.check's
    baked-shading score ≤ 0.08.
  - 15121 and 15091 were as even but lit the up-facing facets (score 0.37 / 0.42), which reads as painted light.
- **Sockets:** two flank `embers` sockets added (`SOCKETS`). Now six in all, four `embers` and two `heat_glow`.
- **Measurement:** `report()` now returns per-region cls() make-up (`reg_cls`), crack-only stats (`crack`: slot faces
  whose nearest station is a crack, label colour cyan) and core-only stats (`core_px`). `sheet_cracks()` measures the
  sheet's five crack boxes (§5.2) on their O + L pixels.

### Calibration (two passes)

| Key | Target | Pass 1 hex (dome render) | Pass 2 gain (linear) | Final hex |
| --- | --- | --- | --- | --- |
| `m015_shell` | `#5F585E` | `#4B4751` (`#60595F`) | × 1.24 | `#534F5B` |
| `m015_shell_light` | `#7C7378` | `#635F68` (`#7C7478`) | × 1.95 | `#88828E` |
| `m015_shell_dark` | `#45404A` | `#34313E` (`#47424B`) | × 0.67 | `#2A2732` |
| `m015_shell_warm` | `#685D5E` | `#524B51` (`#685D5F`) | × 1.24 | `#5C535B` |
| `m015_ember_lip` | `#5E2620` | `#522420` (`#602620`) | — | `#522420` |
| `m015_ember_wall` (Neon) | `#D85A22` | `#C95E2A` (`#D75B23`) | — | `#C95E2A` |
| `m015_core` (Neon) | `#FD7428` | `#FB7430` (`#FF7429`) | — | `#FB7430` |
| `m015_core_hot` (Neon) | `#FDB548` | `#FBAB4E` (`#FFB449`) | — | `#FBAB4E` |
| `m015_core_deep` | `#D9441A` | `#AE3F19` (`#DA451A`) | × 1.3 | `#C4481E` |
| `m015_base` | `#B39A8F` | `#8F7F7C` (`#B49A8F`) | × 0.89 | `#887875` |
| `m015_base_light` | `#C8AFA3` | `#9F908D` | × 0.89 | `#978986` |
| `m015_base_dark` | `#8F786D` | `#72635E` | × 0.89 | `#6C5E59` |

- **Pass 1:** `calibrate()` on the test dome. Every key ended within 6 levels of its target. The rock keys came out
  brighter than round 1's (`#8F7F7C` against `#857774`) in this session's studio, so they were not reused.
- **Pass 2:** `report(light=True)` on the hero, over all six sheet views, in two rounds.
  - Shell medians were 6–25 levels under the sheet, and the lit quartile 20–30 under in the lit views.
  - After the seed change, the medians were about 10 over and the shade quartile 15–25 over the sheet's `#373134`.
  - `core_deep` × 1.3: the front and f34 rims read 40–57 % L. The core's shade quartile is now `#CB3E17` / `#CA3E18`
    (rear / r34), against the sheet's `#A52F0E` / `#BA360E`.
  - Rocks × 0.89: the front and f34 rocks were 9–19 levels over.

### Re-measured (final build, `report(light=True)`, cls() masks inside the hero's pixels; sheet = full view boxes)

| View | Glow O, ours / sheet | Lip L, ours / sheet | Shell S median (lit, shade): ours / sheet | Glow median, lit: ours / sheet | Rock B median: ours / sheet |
| --- | --- | --- | --- | --- | --- |
| front | 25.5 / 24.5 % | 6.8 / 5.2 % | `#686067` (`#94878D`, `#4A4449`) / `#685E64` (`#8B7F83`, `#373134`) | `#FF7429` `#FFB449` / `#FC7D27` `#FDB745` | `#B29489` / `#AF968C` |
| side | 14.1 / 16.3 % | 1.9 / 7.8 % | `#686063` / `#5D565D` | `#D75B23` `#FFB348` / `#FC6C23` `#FDB040` | `#87746C` / `#B2978C` (studio shade) |
| rear | 21.2 / 22.4 % | 5.8 / 6.3 % | `#605861` / `#5B545A` | `#FF7429` `#FF7429` / `#FB6521` `#FEB140` | `#8A7973` / `#B49A8D` (studio shade) |
| top | 24.8 / 23.8 % | 4.4 / 6.2 % | `#5E575F` / `#61595E` | `#FF7429` `#FFB449` / `#FC7325` `#FECD5A` | `#B39487` / `#C1A699` |
| f34 | 22.2 / 20.7 % | 6.0 / 5.4 % | `#72646B` / `#60595F` | `#FF7429` `#FFB449` / `#FD7C25` `#FEB747` | `#B5978C` / `#AC9389` |
| r34 | 18.1 / 15.6 % | 6.5 / 6.5 % | `#605862` / `#5C555A` | `#FF7329` `#FF7429` / `#FC6F22` `#FDAA3B` | `#8A7973` / `#B2978A` (studio shade) |

- **Glow share by `measure()`** (the key-label raster the verifier used; sheet = §1.2 bbox shares):

  | View | Now | Sheet | Round 1 |
  | --- | --- | --- | --- |
  | front | 23.1 | 26.3 | 21.9 |
  | side | 18.3 | 17.7 | 8.5 |
  | rear | 26.6 | 24.2 | 22.0 |
  | top | 20.5 | 27.0 | 15.6 |
  | f34 | 18.7 | 22.9 | 20.4 |
  | r34 | 23.5 | 17.4 | 17.3 |

  - This raster counts every `core*` and `ember_wall*` face as glow, lit or not. The rendered cls() share above is the
    better colour measure.
- **Core hot share (O pixels at r ≥ 245, g ≥ 140):**

  | View | Ours | Sheet |
  | --- | --- | --- |
  | front | 26 % | 37 % |
  | f34 | 21 % | 40 % |
  | side | 35 % | 29 % |
  | rear | 18 % | 28 % |
  | r34 | 17 % | 30 % |
  | top | 41 % | 33 % |

### Cracks against the sheet (crack-only pixels)

`sheet_cracks()` on the O + L pixels of the §5.2 boxes. `bright` is the share in the cls() glow class O; `hot` is the
share at r ≥ 245, g ≥ 140.

| Crack | Median | Lit | Shade | bright | L | hot |
| --- | --- | --- | --- | --- | --- | --- |
| sheet crack 1, front | `#E25E20` | `#FAA82E` | `#723126` | 81.5 % | 18.5 % | — |
| sheet crack 2, front | `#C45822` | `#F99B2B` | `#752E1D` | 80.5 % | 19.5 % | — |
| sheet BR, side | `#DB531E` | `#FBA12C` | `#822C1C` | 83.6 % | 16.4 % | — |
| sheet BR, rear | `#D15025` | `#FD721F` | `#753E36` | 76.7 % | 23.3 % | — |
| sheet crack 5, rear | `#CB541F` | `#F89622` | `#6F2E24` | 78.8 % | 21.2 % | — |
| **ours, front** | `#E66325` | `#FFAC46` | `#4D1F14` | 83.7 % | 15.5 % | 18.1 % |
| **ours, f34** | `#FF963A` | `#FFB449` | `#B64C1F` | 90.9 % | 8.7 % | 51.1 % |
| **ours, top** | `#D75B25` | `#FF8C37` | `#4F1F15` | 70.2 % | 29.8 % | 13.0 % |
| **ours, side** | `#D75B23` | `#FFA643` | `#31110E` | 63.6 % | 36.4 % | 14.9 % |
| **ours, r34** | `#D15822` | `#FF7329` | `#451B16` | 62.6 % | 37.4 % | 1.5 % |
| **ours, rear** | `#56251D` | `#D75B23` | `#411915` | 42.4 % | 57.6 % | 0 % |
| round 1, front / side / rear | `#511F13` / `#3C160E` / `#481E19` | `#A8472C` / `#9E4228` / `#723022` | | 18 / 15 / 9 % | 81 / 86 / 91 % | 0 % |

- The front, f34 and top cracks now read as the sheet's: a dark lip edge, red-orange wall and hot centre line.
- The rear and r34 still read lip-heavy. In our geometry the BR crack and its mirror run down the flanks, so the rear
  view sees them nearly edge-on (mostly chamfer). The sheet draws the BR crack across the face of the upper back. That
  is crack placement (stage 1), not colour.

### Lighting and VFX (stage 5 + 6)

- **Neon pieces** (emission 1.0, one flat colour, Tint 1): `core` `#FB7430`, `core_hot` `#FBAB4E` and `ember_wall`
  `#C95E2A`. Export: 3 glow pieces. Everything else is solid.
- **Lights:** unchanged. Two shadowed, flickering PointLights `#FF7A22` in the window recesses, outside the solid (front
  0.7 / range 10; back 0.9 / range 8).
- **Sockets (`fx_check`, final build; build frame, clearance, spawn-box grid points inside):**

  | Socket | Point | Clearance | Grid points inside |
  | --- | --- | --- | --- |
  | heat_glow_1 | (0.9, −4.9, 3.8) | 1.55 | 0 / 125 |
  | heat_glow_2 | (0.3, 3.6, 4.2) | 0.99 | 0 / 125 |
  | embers_1, crown | (0.3, 0.0, 8.4) | 1.75 | 0 / 125 |
  | embers_2, front | (0.9, −5.6, 2.6) | 0.98 | 0 / 125 |
  | **embers_3, left flank** | (−5.6, −0.3, 4.0), shape [0.8, 3.6, 3.0], rate 1.5 | 1.37 | 0 / 125 |
  | **embers_4, right flank** | (6.4, −0.3, 4.0), the same | 1.57 | 0 / 125 |

  - The flank boxes stand 1.2 out from the shell's widest point at z 1.5–6 (x −4.39 / +5.21), from z 2.2 to 5.8, as the
    VFX panel's shards float round both flanks.
  - The export STATS line should report **6 sockets and 3 glow pieces**.

### Checks (final `m015.build()`, saved)

| Object | Tris | Size (studs) | Shells | Non-manifold edges / verts, boundary | Crossings | Interior | Min corner | UV islands / overlaps / flipped |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EmberMeteorDeposit | 3862 / 4000 | 11.08 × 10.50 × 7.55 | 1 | 0 / 0, 0 | 0 | 0 | 5.00° | 475 / 0 / 0 |
| EmberMeteorSlab | 682 | 5.75 × 4.17 × 7.60 | 1 | 0 / 0, 0 | 0 | 0 | 5.09° | 91 / 0 / 0 |
| EmberMeteorCap | 442 | 4.67 × 3.97 × 7.47 | 1 | 0 / 0, 0 | 0 | 0 | 5.08° | 59 / 0 / 0 |
| EmberMeteorChunk | 796 | 4.87 × 4.61 × 7.34 | 1 | 0 / 0, 0 | 0 | 0 | 5.02° | 104 / 0 / 0 |
| EmberCore | 58 | 4.91 × 4.72 × 5.23 | 1 | 0 / 0, 0 | 0 | 0 | 18.6° | 8 / 0 / 0 |
| EmberMeteorBaseRock | 58 | 2.41 × 2.25 × 1.30 | 1 | 0 / 0, 0 | 0 | 0 | 9.9° | 16 / 0 / 0 |

- `core_present` true; no inner shells.
- `K.check` clean. Baked-shading scores: hero 0, slab 0.07, cap 0.08, chunk 0, core 0, rock 0.
- `crack_probe` is unchanged:
  - crack 1: opening 0.30–0.40, floor 0.12–0.18, depth 0.60–1.02;
  - BR crack: opening 0.30–0.37, floor 0.13–0.15, depth 1.03–1.04.
- `see_through` is unchanged from round 1, as no geometry changed:
  - hero: (180, 7) 3 px and (−45, 45) 4 px, the known grazing slits under 0.05 stud;
  - Slab: (0, 78) 6 px, its own opening;
  - Cap: its two windows into its open hollow (by design: a part has no core).

### Left over

- **Side glow** is 14.1 % rendered against the sheet's 16.3 %, and the `measure()` share 18.3 against 17.7 %. Most of
  it is now the pillar's side wall glowing Neon `ember_wall`, which reads as a flat orange-red plane beside the core in
  the side view. A wider real side window (geometry) would read better.
- **r34** is 2.5 points over the sheet and the rear 1.2 under. The rear rims serve both views, and the r34 sees more of
  them than the sheet's r34 does.
- **Rear / r34 cracks** read lip-heavy because they run down the flanks, edge-on to those views (stage 1 placement).
- **Core hot facets:** front, f34, rear and r34 are 10–20 points under the sheet's hot share. The 58-facet core flips a
  whole big facet at a time, so finer control needs more core facets.
- **Side, rear and r34 rocks** sit in the kit studio's shade (`#87746C`–`#8A7973` against the sheet's evenly lit
  `#B2978C`). That is the studio key light; the sheet lights every view.
- **Shell:** the f34 median is 15 levels over the sheet and the front matches. The sheet's front and f34 disagree, so
  one palette cannot match both.

## Stage 7 — Verification (round 2)

Independent verifier (did no other stage). This was a read-only run in a background Blender (port 9880) on
`art/blender/assets/kit/wip/M015_verify.blend`. I did not save, did not call `build()`, and sent the fresh renders to the
scratchpad (`kit_models.MODEL_RENDERS` redirected), so the committed renders are untouched. I measured the geometry with
my own bmesh/BVH script, not the builder's numbers. I used the builder's `see_through`, `crack_probe`, `gaps`,
`fx_check`, `measure`, `report(light=True)` and `sheet_stats` as instruments, and I cross-checked colour with my own
patch sampler on both images.

**Verdict: PASS, 7/10.** Nothing is broken, and every round-1 colour, lighting and VFX finding is fixed or within
tolerance. The remaining differences from the sheet are the stage-1 dome-sector concept (a main-session decision) and
the placement of the BR crack. They are recorded below as minors, for the commit notes.

### Re-measured (own script)

| Object | Tris | Size (studs) | Shells | NM edges / verts / boundary / wire / loose | n-gons / zero-area / dup verts | Winding conflicts, volume | Self-hits | Interior | Min corner (faces < 5°) | UV: layer, flipped, overlap cells @1024 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EmberMeteorDeposit | 3862 / 4000 | 11.08 × 10.50 × 7.55 | 1 | 0/0/0/0/0 | 0/0/0 | 0, +306.9 | 0 | 0 | 5.00° (0) | UVMap, 0, 0 |
| EmberMeteorSlab | 682 / 1000 | 5.75 × 4.17 × 7.60 | 1 | 0/0/0/0/0 | 0/0/0 | 0, +61.3 | 0 | 0 | 5.09° (0) | UVMap, 0, 0 |
| EmberMeteorCap | 442 / 1000 | 4.67 × 3.97 × 7.47 | 1 | 0/0/0/0/0 | 0/0/0 | 0, +37.6 | 0 | 0 | 5.08° (0) | UVMap, 0, 0 |
| EmberMeteorChunk | 796 / 1000 | 4.87 × 4.61 × 7.34 | 1 | 0/0/0/0/0 | 0/0/0 | 0, +65.3 | 0 | 0 | 5.02° (0) | UVMap, 0, 0 |
| EmberCore | 58 / 1000 | 4.91 × 4.72 × 5.23 | 1 | 0/0/0/0/0 | 0/0/0 | 0, +60.1 | 0 | 0 | 18.61° (0) | UVMap, 0, 0 |
| EmberMeteorBaseRock | 58 / 1000 | 2.41 × 2.25 × 1.30 | 1 | 0/0/0/0/0 | 0/0/0 | 0, +3.4 | 0 | 0 | 9.85° (0) | UVMap, 0, 0 |

- **Hero size** is inside the decided bands: 11.5 ± 0.5, 10.0 ± 0.6 and 7.6 ± 0.3. D is 10.50, near the top of its
  band.
- **Origin** is at the bottom centre on all six: the local bbox bottom centre is (0, 0, 0). Rotation is 0 and scale 1,
  with no modifiers, parents or custom split normals.
- **Normals and faces:** normals are outward (consistent winding, positive volume). All faces are triangles, and all
  UVs lie in 0–1.
- **Materials:** the hero uses 26 `FB_m015_*` keys and mixes, and every material slot is used. The Neon keys are
  `core` `#FB7430`, `core_hot` `#FBAB4E` and `ember_wall` `#C95E2A`. Each has emission strength 1.0, no Tint mix node,
  and Tint 1.000 on every face on every object, so each is one flat colour. Every other key is solid (emission 0).
  Export: 3 glow pieces.
- **Core:** present (ray parity at `CORE_AT`). It touches all four shells. Its clearance to the rocks is ≥ 0.35 (F4),
  so ≥ 0.2 holds. A ray straight down at the core centre hits `core_hot` at z 5.65, so the crown opening is open.
- **Sockets:** 6 in all, 2 `heat_glow` (each with a shadowed PointLight `#FF7A22`) and 4 `embers` (crown, front, left
  flank, right flank).
  - Every socket point is outside the solid, with clearance 0.98–1.75.
  - On my finer 7³ spawn-box grid (5 rays, majority), five sockets have 0 points inside. **heat_glow_2 has 6 / 343
    inside**, 0.02–0.03 deep at the two top corners of its box (build (−0.4 / 1.0, 3.4–3.53, 4.93), the rear window's
    top rim). The builder's 5³ grid misses them.
- **Sightlines (`see_through`):**
  - hero: (180, 7) 3 px and (−45, 45) 4 px, the known grazing slits under 0.05 stud;
  - Chunk: none;
  - Slab: (0, 78) 6 px, its own opening;
  - Cap: its two windows, open through its hollow, by design.
- **Slots (`crack_probe`, opening / floor / depth):**
  - crack 1 (FL): 0.30–0.40 / 0.12–0.18 / 0.60–1.02. The two upper stations are 0.73 and 0.60 deep, capped by the
    wall's thickness.
  - BR crack: 0.30–0.37 / 0.13–0.15 / 1.03–1.04 (tapers 0.85 / 0.98).
  - right seam: 0.36–0.44 / 0.17–0.21 / 1.26–1.27.

### Against the sheet (fresh renders at the spec cameras; side compared mirrored)

`measure()` (key-label raster): profile error mean / worst, front 0.090 / 0.27, side 0.090 / 0.24, rear 0.093 / 0.29.
Meteor W : H: front 1.25, side 1.05, rear 1.25. Rendered cls() O share, ours / sheet, with lights on:

| View | Front | f34 | Top | Side | Rear | r34 |
| --- | --- | --- | --- | --- | --- | --- |
| O share | 25.5 / 24.5 | 22.2 / 20.7 | 24.8 / 23.8 | 14.1 / 16.3 | 21.2 / 22.4 | 18.1 / 15.6 |

**Colours.** Ours − sheet, per channel (R, G, B). Shell, rim and core come from the label-masked medians (`report`
against `sheet_stats`); lip, wall and rock from my own patch masks on both images.

| Region | Front | f34 | Top | Side | Rear | r34 |
| --- | --- | --- | --- | --- | --- | --- |
| Shell median | `#686067` / `#685E64`: (0, +2, +3) | `#72646B` / `#60595F`: (+18, +11, +12) | `#5E575F` / `#61595E`: (−3, −2, +1) | `#686063` / `#5D565D`: (+11, +10, +6) | `#605861` / `#5B545A`: (+5, +4, +7) | `#605862` / `#5C555A`: (+4, +3, +8) |
| Shell shade quartile | `#4A4449` / `#373134`: (+19, +19, +21) | `#4E484D` / `#373133`: (+23, +23, +26) | | | `#433F46` / `#373135`: (+12, +14, +17) | |
| Core O median | `#FF7429` / `#FC7D27`: (+3, −9, +2) | `#FF7429` / `#FD7C25`: (+2, −8, +4) | `#FF7429` / `#FC7325`: (+3, +1, +4) | `#D75B23` / `#FC6C23`: (−37, −17, 0) [pillar wall] | `#FF7429` / `#FB6521`: (+4, +15, +8) | `#FF7329` / `#FC6F22`: (+3, +4, +7) |
| Core lit quartile | `#FFB449` / `#FDB745`: (+2, −3, +4) | | `#FFB449` / `#FECD5A`: (+1, −25, −17) | | `#FF7429` / `#FEB140`: (+1, −61, −23) [no hot facet] | `#FF7429` / `#FDAA3B`: (+2, −54, −18) |
| Hot core patch | `#FFB449` / `#FDB443`: (+2, 0, +6) | (+2, +1, +7) | (+2, −21, −13) | (+2, +4, +10) | (+1, +3, +10) | (+2, +11, +15) |
| Ember wall (red-orange) | `#D45422` / `#C03A16`: (+20, +26, +12) | (+31, +25, +19) | (+23, +46, +26) | (+11, +37, +19) | (+19, +15, +14) | (+1, +10, +12) |
| Lip | `#7A371E` / `#863920`: (−12, −2, −2) | (−9, +10, +19) | (−20, −1, −6) | (−19, −14, −14) | (−16, +2, −7) | (−1, 0, −8) |
| Base rock | `#B29489` / `#AF968C`: (+3, −2, −3) | `#B5978C` / `#AC9389`: (+9, +4, +3) | `#B39487` / `#C1A699`: (−14, −18, −18) | `#87746C` / `#B2978C`: (−43, −35, −32) | `#8A7973` / `#B49A8D`: (−42, −33, −26) | `#8A7973` / `#B2978A`: (−40, −30, −23) |

- **Cracks** (crack-only pixels; ours against the sheet):
  - front: `#E66325` / `#E25E20`, bright 84 / 82 %;
  - f34: `#FF963A`, 91 %;
  - top: 70 %;
  - side: `#D75B23` / `#DB531E`, 64 / 84 %;
  - r34: 63 %;
  - **rear: `#56251D` / `#D15025`, 42 / 77 %.**
- **Read by view** (side-by-side crops checked):
  - **Front and f34:** a good read. Crack 1 is a glowing slot with a dark lip, red wall and hot centre, left of a
    diamond window onto the faceted core. The dark faceted shell is mottled, with pale stones at the foot.
  - **Top:** a central diamond of core with glowing cross seams, close to the sheet's cross-shaped opening.
  - **Side and rear:** the weakest views (minors 1–3).

### Round-1 findings, one by one

| Round-1 finding | Status |
| --- | --- |
| Slab see-through at crack 1 | **Fixed.** Only the Slab's own top opening (6 px) remains; crack 1 is capped 0.15 short of the hollow. |
| Hero sightlines (front 3, rear 11, top 7 px, …) | **Fixed** apart from the two known grazing slits (3 and 4 px, under 0.05 stud). Minor. |
| Back-seam V on the front silhouette | **Fixed.** The front profile reads 0.98–0.99 at mid-width. |
| Rear window too narrow | **Fixed.** Rear O share 21.2 against 22.4 %. |
| Rocks too small or low | **Fixed.** Front rock tops 0.16–0.34 H; rock median within 3–9 levels in the lit views. |
| Cracks read as dark grooves (blocker) | **Fixed** in front, f34, top and side (64–91 % bright; the sheet 77–84 %). **The rear is still lip-heavy (42 %)**: the crack runs edge-on to that view. Minor 1. |
| Rim lip share 9–13 % | **Fixed:** 1.9–6.8 % against the sheet's 5.2–7.8 %. |
| Low shell contrast | **Mostly fixed.** The front median matches to 3 levels, but the shade quartile is still 12–26 levels lighter than the sheet's `#373134`. Minor 5. |
| Embers only at the crown and front | **Fixed.** Left and right flank `embers` sockets, outside the solid. |
| Glow share short (side 8.5 %, top 15.6 %) | **Fixed numerically** (side 14.1 / 16.3 %, top 24.8 / 23.8 %). The side recovery is mostly the flat Neon pillar wall. Minor 2. |
| Re-calibrate against the new rims | **Done** (two passes, recorded under Stage 4–6 round 2). |

### Itemised list (no blockers)

1. **Minor: the BR crack and its mirror read edge-on in the rear and side views.**
   - On the sheet's rear, the BR crack crosses the face of the upper-left piece diagonally, and crack 5 runs down the
     right piece. On the sheet's side, BR's crack runs diagonally across the big piece's face.
   - Ours run down the flanks at about 135° and 45°, so both views see them near the silhouette as thin lines. Rear
     crack pixels are 42 % bright, against the sheet's 77 %.
   - Fix (stage 1, if ever reopened): move the BR crack's control rays about 25–35° toward the rear view's face (and
     the mirror with it), then re-run the polish and see-through checks.
2. **Minor: the side window's glow is mostly the FR pillar's flat Neon `ember_wall` wall.**
   - It reads as one flat orange-red plane (`#D75B23`), not the faceted core; the core itself is 2007 px against the
     wall's 9257 px.
   - In Roblox the core is flat Neon too, so the in-game difference is small. The real fix is a wider side window
     (stage 1 geometry).
3. **Minor: the overall gestalt is a closed conical/bell dome with diamond windows and full-height glowing seams.**
   - The sheet has four separate lumpy boulders round a core that bulges forward. The side and rear read symmetric
     where the sheet is asymmetric.
   - The front profile's flanks are low: f 0.05 / 0.95 at 0.26 / 0.24 H, against the sheet's 0.53 / 0.49, so the
     sheet's boulders bulge to the edges.
   - From the top the dome covers most of the rock ring (top rock share 10 % against 16 %).
   - This is the main session's stage-1 rework decision, so it is recorded and not failed.
4. **Minor: core hot facets.**
   - The rear and r34 windows show no `core_hot` facet: lit quartile `#FF7429` against `#FEB140`, G −61.
   - The core has no deep shading in the windows: front shade `#DD5922` against the sheet's `#B53B11`, because Neon is
     flat.
   - Fix: let `CORE_FWD` or the noise put one `core_hot` facet in the upper rear window. This is colour only.
5. **Minor: the shell shade quartile is 12–26 levels lighter than the sheet's**, and the f34 median is 11–18 levels
   over. The dark facets could go one step darker (`shell_dark` mix weight up), without moving the front median.
6. **Minor: the Neon `ember_wall` is more orange than the sheet's crack walls**: rendered `#D75B23` / `#D45422` against
   the sheet's `#B5310F`–`#CC3610` (G +15…+46). The crack medians still match (front `#E66325` / `#E25E20`), so this
   is optional.
7. **Minor: rocks in the side, rear and r34 views render 23–43 levels darker than the evenly lit sheet.** This is the
   kit studio's key-light shade, as on other models; the lit views match within 3–9 levels. The top-view rocks are 14–18
   under.
8. **Minor: heat_glow_2's spawn box has 6 / 343 grid points 0.02–0.03 inside the rear window's top rim.**
   - Fix: `BACK_LIGHT["pos"]` (0.3, 3.6, 4.2) → (0.3, 3.9, 4.2). I verified that shifts of +0.2 to +0.4 give 0 / 343
     inside.
9. **Minor: crack 1's two upper stations are 0.60–0.73 deep**, against the ≥ 0.9 target. This is capped by the shell
   thickness so the slot can't break through, and it is recorded in the build fixes.
10. **Minor: the exported Cap and Slab parts have openings into their hollows** (Cap see-through by design, genus 1).
    Standalone, those parts are not the sheet's solid lozenge and elbow slab; this follows the main session's
    dome-sector mapping.
11. **Minor: the hero has 138 tris of headroom** (3862 / 4000), so any later geometry fix (1, 2) must trade tris.
