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
