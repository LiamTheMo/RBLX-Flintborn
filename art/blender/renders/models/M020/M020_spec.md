# 020 Hardwood Stump — spec

Reference: `art/blender/assets/references/020.png`. The sheet's own title is "FLINTBORN HARDWOOD STUMP — Individual Asset
Reference, Stylized / Low Poly / Game Ready Look", footer "FLINTBORN — INDIVIDUAL MODEL STUDY, PAGE 22/132". INDEX.md
row 20 calls it "Flintborn hardwood stump study". The image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m020.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`
(three agents: Build = stages 1–3, Finish = stages 4–6, Verify = stage 7).

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7).

Sheet text:
- **Header:** "A chopped hardwood stump with broad, faceted forms and clean, solid colors. Stylized, chunky, and
  readable from a distance. Matches the FLINTBORN woodland style."
- **Modeling notes:**
  - "Chunky, low poly, readable silhouette."
  - "Broad flat-shaded faces, no surface noise."
  - "Stump body + separate cut face, root modules and leaf clumps."
  - "Simple geometric forms, consistent with FLINTBORN style."
  - "Clean joins between parts, no micro details."
  - "Keep proportions and angles consistent across all views."
  - "Use solid colors from palette, no textures or gradients" (but see §3.8).
- **Palette:** Cut Wood ("Pale wood, low saturation"), Bark ("Warm brown timber"), Shadow Bark ("Darker brown for
  contrast"), Leaf ("Clean green, solid color").
- **Exploded labels:** Cut Face, Stump Body, Root Module (×4), Leaf Clump (×4).
- **Close-ups:** "Cut Face Close-Up" ("Faceted rings with simple stepped planes."); "Root Junction Close-Up"
  ("Simple angled junction, clean planes. No small details."); "Underside View" ("Flat underside with clear planes.
  Roots aligned to stump body.").
- **Game context:** `src` and GDD.md have no hardwood-stump node id. The old R06 kit sheet has `HardwoodStump`
  (13.8 × 12.1 × 6.5, trunk top about 6.1 Ø, 5 roots, 1072 tris, `harvest_hit` + `harvest_deplete`), which owns the
  `HardwoodStump*` names (§8).

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is
`#F2EEE8` (242, 238, 232). The masks are `cls()` in `m.py` (HSV):
- **L, leaves:** sat ≥ 0.30, hue 62–160°, g > 50.
- **W, cut wood:** hue 27–52°, sat 0.12–0.60, v ≥ 0.80. (Lit bark facets are hue 22–24°, so they stay out.)
- **B, bark:** sat ≥ 0.18, hue ≤ 45° or ≥ 340°, v < 0.97. Includes the bark rim, the stem stubs and the shadowed
  disc sides of the exploded Cut Face.
- **O, other:** ground shadow and dark edges; not counted in the shares.

**Scratch study material** (pure Python, no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m020_study\`.
Run with `C:/Users/Orang/.local/bin/python3.14.exe`.
- **Helpers:** `png.py` (reader, `crop`), `m.py` (masks, view boxes `V`), `bb.json` (silhouette boxes).
- **Measurements:** `measure.py` → `measure_out.txt` (shares, profiles, width per height); `comps2.py` (cut-face and
  clump components per view); `barkprof.py` (bark-only top/bottom profiles); `trunkw.py` (trunk width per height);
  `arms.py` (top-view root widths and centrelines); `outline.py` (top-view cut-face outline radius by azimuth);
  `rings.py`, `rings2.py` (radial ring bands: top view, f34, close-up, exploded disc).
- **Colour:** `sw.py` (swatches), `samp.py` (views, deciles, height bands), `samp2.py` (exploded parts),
  `samp3.py` (close-ups), `leafrad.py` (leaf base → tip).
- **Names:** `blendnames.py` (kit .blend), `blendall.py` (every sheet .blend).
- **Crops:** `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `cu_cut.png`,
  `cu_root.png`, `cu_under.png`, `pal.png`, `notes.png`; grids `g_*.png` (10 % grid on the silhouette bbox, red =
  centre lines); mask previews `cls_*.png`.
- **Zooms:** `z_f34_top.png` (cut top and rim), `z_f34_base.png`, `z_f34_front.png` (front root), `z_f34_ltip.png`,
  `z_f34_rtip.png` (root tips), `z_top_c.png`, `z_expl_body.png`, `z_expl_cut.png`, `z_expl_roots.png`,
  `z_expl_rootR.png`, `z_expl_leafB.png`, `z_expl_leafR.png`, `z_expl_leafTL.png`, `z_r34_base.png`.
- **To run the scripts on our renders,** point `R` (in `m.py`) at the render, set `P` to its background colour and
  re-run `measure.py` (it rewrites `bb.json`).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a resource node / world prop). Hero budget 4000 tris, each part under 1000. The plan
  in §4.3 lands at about 1900–2300.
- **Overall read (check this first).** One squat, chunky, chopped tree stump:
  - a **flared, fluted trunk** (8 broad vertical lobes, wider at the base) with a **pale ringed cut top** inset in a
    thin bark rim;
  - **four big buttress roots in a +** (front, left, right, back) that flow out of the trunk's lower half as broad
    angular wedges and slope down to blunt tips on the ground;
  - **four bright leaf clumps tucked into the four notches** between the roots.
  - It is wider than tall (hero W : H 1.69). It must read as one object with the roots growing out of the trunk, not
    a cylinder with four logs stuck to it.
  - Hero shares: bark 76 %, cut wood 9 %, leaves 14 %.
- **Focal silhouettes, in order:**
  1. The trunk's flared trapezoid with the notched, ringed cut-top ellipse and its bark lip.
  2. The four root wedges: a straight top ridge falling from the trunk (z ≈ 2.0 at d 2.5) to a blunt sloped tip.
  3. The leaf clumps' broad pointed leaves (6 per clump, kite-shaped, never spiky).
- **Target size: about 9.0 W × 8.5 D × 4.3 H studs** (H = 0.78 of the 5.5-stud character). Cut face Ø 3.6, trunk top
  outer Ø 4.1, root tips 4.0–4.6 from the axis. Tolerances W ±0.35, D ±0.35, H ±0.2. Decision §8.1.
  - **How it was derived.** The sheet has no character. The anchor is the leaf: hero clumps measure 88–98 px across
    against a 190 px cut face, so a leaf is about 0.27 of the cut-face Ø. Leaves like M018/M019's (L 0.85–1.1) make the
    cut face about 3.4–4.0. Ø 3.6 gives 52.8 px/stud in the f34, 26 px/stud in the front cell.
  - **Why this size.** A 4.1-stud trunk (about 1.1 m) is a big old hardwood next to the 22.5-tall W05 oak; a
    character's axe swing lands on the trunk side (chest height). R06 `HardwoodStump` was 13.8 × 12.1 × 6.5 (a
    character-sized stump, taller than the player); W05 `LowStump` is 4.6 Ø × 4; camp `Stump` 3.4 Ø × 2.4.
  - **Height compromise.** The cells disagree on trunk height: trunk height / cut-face Ø is 1.08 in the hero, 1.29 in
    the front cell, about 1.4 in the exploded body and r34, 1.5–1.6 in the side and rear. H 4.3 puts the hero W : H
    within −4 % and the front cell within +7 % (§3.2).
- **Build frame:** front −Y, +X right, ground z 0, origin = the trunk axis on the ground. The bbox centre then sits at
  about (−0.1, −0.28); stage 2 re-centres to the bbox bottom centre.

### 1.2 Measured views (`measure.py`, `comps2.py`)

| View (box) | Silhouette bbox (px) | W : H | Leaves L | Cut wood W | Bark B | Cut face (W comp.) |
| --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (15,112,540,412) | 54–530 × 125–407 | 1.688 | 14.3 % | 9.3 % | 76.4 % | 190 × 59 px, f .33–.72, h .79–1.00 |
| Rear three-quarter (545,112,1010,412) | 582–980 × 141–402 | 1.525 | 9.3 % | 5.1 % | 85.6 % | 156 × 34, f .27–.66 |
| Front (12,476,264,662) | 18–251 × 503–651 | 1.574 | 14.8 % | 5.2 % | 80.0 % | 94 × 19, f .30–.70 |
| Side (264,476,512,662) | 279–493 × 504–649 | 1.476 | 12.0 % | 3.2 % | 84.8 % | 80 × 12, f .30–.67 |
| Rear (512,476,764,662) | 524–752 × 503–650 | 1.551 | 12.3 % | 3.5 % | 84.2 % | 88 × 13, f .29–.68 |
| Top (764,456,1012,664) | 787–994 × 462–660 | 1.045 (W : D) | 19.6 % | 30.7 % | 49.7 % | 99 × 99, centre f .504, h .543 |

- **Verifier tolerance:** shares ±4 points (W ±2.5); positions ±0.06 of W/H unless stated.
- **Ellipse openness** (cut-face height / width): f34 0.31 (≈ 18°), r34 0.22, front 0.20 (≈ 12°), side and rear 0.15
  (≈ 8.5°). The ground contacts give the f34 a lower true elevation (§3.1).

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f; all labels):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .24 | .37 | .43 | .59 | .59 | .67 | .93 | .96 | .98 | 1.0 | .99 | .99 | .98 | .99 | .98 | .86 | .65 | .71 | .61 | .46 | .19 |
| Front | .18 | .34 | .53 | .54 | .67 | .78 | .97 | .98 | .99 | .99 | 1.0 | .99 | .99 | .98 | .97 | .87 | .64 | .70 | .55 | .54 | .17 |
| Side | .13 | .37 | .46 | .54 | .51 | .67 | .96 | .98 | .99 | .99 | 1.0 | 1.0 | .99 | .99 | .97 | .66 | .69 | .63 | .55 | .41 | .15 |
| Rear | .16 | .46 | .48 | .69 | .64 | .84 | .97 | .99 | .99 | 1.0 | 1.0 | 1.0 | .99 | .99 | .97 | .63 | .67 | .69 | .55 | .42 | .14 |
| r34 | .38 | .43 | .53 | .64 | .58 | .91 | .95 | .97 | .99 | 1.0 | 1.0 | 1.0 | .99 | .98 | .88 | .74 | .62 | .64 | .52 | .36 | .25 |
| Top (h = back) | .54 | .57 | .66 | .68 | .79 | .77 | .77 | .92 | .99 | .99 | .99 | .92 | .87 | .88 | .90 | .93 | .79 | .61 | .59 | .57 | .48 |

**Bark-only top line of the roots** (`barkprof.py`, leaves excluded; the root ridge as it falls to the tip), every
0.025 f from each end:

```
f34   left  .24 .30 .37 .41 .43 .45 .46 .49 .50 .53 | trunk .63 .74 .93     (left tip bottom h .18-.22)
f34   right .19 .25 .31 .38 .40 .44 .46 .49 .51 .62 | trunk .86 .89 .98     (right tip bottom h .12-.16)
front left  .18 .26 .34 .36 .39 .42 .44 .47 .51 .64 | trunk .78 .96         (side tips bottom h .10-.14)
front right .17 .26 .33 .35 .39 .42 .45 .47 .54 .67 | trunk .87 .96
```

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .02@.46 .36@.23 .97@.03 .93@.02 .87@.06 .72@.16 .74@.17 .63@.22 .47@.28 .42@.30 .02@.44
r34    .02@.26 .74@.14 .87@.00 .94@.04 .91@.02 .86@.07 .73@.14 .57@.23 .47@.24 .45@.24 .01@.54
front  .13@.42 .53@.18 .98@.01 .92@.03 .85@.11 .85@.08 .72@.15 .71@.16 .49@.26 .47@.27 .02@.49
side   .12@.18 .93@.03 .95@.03 .90@.05 .84@.12 .78@.14 .59@.24 .57@.26 .45@.27 .43@.28 .11@.48
rear   .10@.21 .79@.11 .96@.02 .90@.04 .91@.06 .79@.12 .71@.14 .61@.24 .47@.25 .45@.26 .14@.43
top    .08@.50 .21@.43 .64@.20 .71@.14 .80@.08 .99@.00 .74@.14 .56@.19 .59@.18 .41@.35 .03@.41
```

**Trunk width per height** (bark + cut run through the centre, `trunkw.py`), fraction of W:

```
h      .55  .60  .65  .70  .75  .80  .85  .90  .95
f34    .56  .53  .51  .49  .48  .47  .46  .38* .36*     (* inside the cut-face ellipse)
front  .58  .56  .54  .52  .50  .49  .48  .47  .46
side   .52  .50  .49  .48  .46  .45  .44  .43  .43
```

**Components** (`comps2.py`): centre (f, h); extent f and h.

| View | Leaf clumps |
| --- | --- |
| f34 | back-left .195, .574 (f .13–.25, h .47–.70, 62 × 66 px); front-left .268, .219 (f .16–.34, h .07–.41, 88 × 98, the biggest); front-right two leaf groups .626, .266 and .696, .181 (f .59–.75, h .13–.36); back-right .863, .541 (f .78–.97, h .38–.71, 89 × 94) |
| front | .160, .546 (h .41–.70); .246, .190 (h .07–.37); .650, .198 (h .09–.35); .869, .524 (h .35–.70) |
| r34 | left .139, .521 (+ a leaf at .054, .393); centre .516, .166 (h .09–.28); right .812, .600 (h .46–.78, 81 × 85, biggest) |
| side | left .129, .404 (h .28–.54); centre .533, .119 (h .03–.24, small); right .847, .512 (h .33–.72, biggest) |
| rear | left .138, .503; centre .518, .122 (small); right .855, .498 (biggest) |
| top | NW .204, .692; SW .224, .242; NE .703, .808; SE .780, .280 (each about 50 × 50 px) |

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, governs; `g_f34.png`).** It is **not** a 3/4 view: the camera looks straight down the
front root (az ≈ 0) from above (ground-contact elevation ≈ 12–15°; §3.1).
- **Trunk:** a fluted, slightly flared column; its silhouette runs from 0.42–0.46 W at the rim to 0.56 W at h .55,
  where the left and right roots take over. 4–5 vertical grooves show across the front half (8 lobes round).
- **Cut top:** a pale ellipse 0.40 W wide (190 × 59 px) inside a thin bark rim; the outline is notched where flutes
  meet the rim (front-right at f ≈ .56 and right at f ≈ .71, `z_f34_top.png`). The rim stands a hair proud of the cut
  face at the back right (its inner wall shows).
- **Roots:** left root to the far left (tip at f 0, h .18–.24), right root to the far right (tip f 1.0, h .12–.19),
  front root straight at the camera under the trunk (bottom h 0 at f .40–.55, a broad blunt end about 2.3 studs
  wide). The back root is hidden.
- **Leaf clumps:** 4 visible: front-left (biggest, on the ground left of the front root), front-right (small, right of
  the front root), back-left (behind/on the left root, h .47–.70) and back-right (on the right root, h .38–.71). The
  back-right clump's leaves overlap the right root's top, so it sits **on** that root's back flank.
- **Bark facets:** many irregular mid-size triangles (edges about 0.4–0.7 stud), flat shaded, broad lit planes on the
  root tops; no noise.

**Front (`g_front.png`).** The same composition as the f34 at a lower elevation (≈ 10°); the trunk is drawn taller
(W : H 1.574). 4 clumps at the same fractions.

**Rear three-quarter, side, rear (`g_r34.png`, `g_side.png`, `g_rear.png`).** All three are the **same diagonal
composition**: the camera looks into a notch, so 4 roots show (two coming toward the camera at centre-left and
centre-right, two at the far sides) and 3 clumps (a small one on the ground at the centre front, a mid-height one at
the left, the biggest one raised at the right). Side and rear are near-identical drawings (§3.3).

**Top (`g_top.png`, `z_top_c.png`; image top = back).** A **+**:
- the cut face is a roundish 13–14-gon (99 px) with concentric faceted rings, centred slightly back (h .543) and a
  thin dark bark ring round it;
- roots point back (az ≈ 97°), left (≈ 185°, its centreline 0.4 forward), right (≈ 355°) and front (≈ 271°, tip bending
  to ≈ 275°). The front root is the widest and longest, the back root the shortest (§2.1);
- the clumps sit in the four diagonal notches;
- the cut-face outline (`outline.py`, radius / 49.5 px by azimuth, 0 = +X, 90 = back) is 0.94–1.02 almost all round,
  with one **flattened sector at the front-left (az 222–258°, down to 0.85)** and shallow dips at 54–66°, 120–132°,
  306° and 342–354°.

**Close-ups.**
- **Cut Face** (689,742,1003,869): faceted concentric rings: a darker pith disc, a light band, a darker ring, a light
  band, a palest outer band, then the brown rim with a lit top edge. The ring boundaries are facet edges: "simple
  stepped planes" (§1.4).
- **Root Junction** (689,906,1003,1058): the root's top ridge runs straight into a buttress plane on the trunk; one
  big angled plane, no seam, no small details.
- **Underside** (689,1092,1003,1252): seen from below, the base is a flat, faceted star; four roots aligned with the
  trunk's lobes. **Each root tip shows a pale cut-wood end** (`#DAAB78`, the Cut Wood swatch) only from below
  (decision §8.3).

### 1.4 Parts (Exploded Construction (15,730,680,1262), `expl.png`)

Scale: the exploded body's inset cut face is 147 px = Ø 3.6 → **about 41 px per stud** in the exploded view. The
exploded parts are drawn about 1.25× the hero's scale relative to their clumps (the hero governs sizes).

#### Stump Body (263,841,489,1067), 227 × 227 px (`z_expl_body.png`)

- **What it is:** the trunk with a flared base, 8 broad vertical lobes, a bark rim round a ringed top, and **4 short
  buttress stubs** at the base, one per root. In the exploded each stub ends in a dark rectangular **socket** (the
  root modules' attach point, with dashed arrows); between the stubs the base has 4 shallow valleys.
- **In the hero** the sockets are filled by the roots and never seen: **don't model holes** (decision §8.4). The Body
  part's stub ends are flat faces in `bark_shadow`.
- **Construction:** `_body()`:
  - a lofted 16-vertex ring trunk, 8 rings (z −0.1 for the floor cut, 0.45, 1.0, 1.6, 2.3, 3.0, 3.65, rim);
  - the 16 vertices per ring are placed explicitly: for each root azimuth a_i a **crest** at a_i and **grooves** at
    a_i ± 22°, plus a crest on each diagonal midway between neighbouring roots (4 + 8 + 4 = 16), so lobes line up
    with the roots ("Roots aligned to stump body");
  - **mean radius** (valley/diagonal azimuths): z 0 → 2.45, 0.5 → 2.35, 1.0 → 2.27, 1.6 → 2.20, 2.3 → 2.13,
    3.0 → 2.08, 3.65 → 2.05, rim → 2.03 (outer);
  - **grooves** pushed in 0.10 at the top, 0.16 at z ≤ 1.0 (groove vertex radius × (1 − depth / r));
  - **buttress bulge** on each root azimuth (Gaussian in azimuth, σ 20°): +0 at z ≥ 3.7, +0.08 at 3.0, +0.2 at 2.6,
    +0.4 at 2.1, +0.7 at 1.5, +1.0 at 0.9, +1.25 at z ≤ 0.3. That makes the f34's trunk-edge radius (2.07 at z 3.7,
    2.16 at 3.2, 2.30 at 2.6, 2.52 at 2.1) and hands over to the root module;
  - jitter: radius ±0.05, z ±0.04, ring twist ±4°; triangulate with beauty fill and flip a few diagonals by seed so
    the facets read as the sheet's irregular triangles; no smoothing;
  - **rim (collar):** the top ring's outer edge at z 4.30 (±0.05 per vertex, with a 0.06 dip where a groove meets the
    rim), an inner edge 0.25 inside that follows the cut-face outline, and a short inner wall down to the disc
    (rim 0.06 proud of the cut face);
  - the body's floor under the disc at z 3.69 (hidden by the disc).
- **Triangles:** 16 × 7 bands × 2 = 224, rim 16 × 3 × 2 = 96, stub end faces and floor ≈ 40 → **about 360**.

#### Cut Face (293,730,464,807), 172 × 78 px; body inset face (305,833,451,871) 147 × 39 (`z_expl_cut.png`)

- **Shape:** a thick pale slab: **Ø 3.6** (R 1.8), **thickness 0.55** (0.15–0.17 Ø on the sheet), 12–14-sided outline
  (13 recommended) following the top view: radius jitter ±3 %, the flattened front-left sector (az 220–260° at
  0.87 R) and shallow dips (0.92 R) at az ≈ 300° and 345° that line up with the rim notches in the f34.
- **Rings ("faceted rings with simple stepped planes"):** loops at **0.22, 0.42, 0.60, 0.80 and 1.0 R**, so the bands
  are real edges for §5.5. Inner loops are roundish 10–12-gons (±4 % jitter), not copies of the notched outline.
  Loop heights give the stepped planes: centre +0.035, 0.22 R +0.030, 0.42 R +0.026, 0.60 R +0.018, 0.80 R +0.012,
  1.0 R 0. Keep the whole face within 0.04 of flat.
- **Sides:** one band, `cut` (the swatch colour); the exploded shows 4–5 small dark speck knots on the sides, which
  are inside the rim in the hero, so skip them.
- **Position in the hero:** centred on the axis, top at **z 4.24**, bottom at 3.69 (inside the collar). Its sides are
  removed by the union.
- **Construction:** `_cut_face(seed)`: centre fan + 4 bands + side band + bottom. **Triangles:** 13 + 4 × 26 + 26 +
  11 ≈ **155**.

#### Root Module ×4: exploded (64,906,219,1000) 156 × 95, (114,990,245,1135) 132 × 146, (513,971,644,1110) 132 × 140 (`z_expl_roots.png`, `z_expl_rootR.png`)

- **Shape:** a chunky angular wedge: tall at the trunk end (a flat attach face), a straight-to-slightly-humped top
  ridge sloping down to a **blunt, sloped tip** on the ground; flat bottom; cross-section a 7-sided "house" (flat
  bottom, shoulders, a top ridge). In the exploded the top line has a faint hump-dip-bulge; in the hero the ridge is
  nearly straight. Big flat facets, no small detail.
- **Profile (measured on the hero, left root; d = plan distance from the trunk axis):** ridge height **2.0 at d 2.5,
  1.7 at 2.9, 1.45 at 3.4, 1.2 at 3.8, 0.95 at 4.2, 0.3 at the tip (4.55)**. The last 0.35 is the sloped blunt end
  face (about 60°).
- **Plan width (top view, left root):** 2.3 at d 2.2, 2.0 at 2.8, 1.85 at 3.2, 1.7 at 3.45, 1.55 at 3.7, 1.3 at 3.95,
  1.0 at 4.2, about 0.7 at the end face.
- **Construction:** `_root(az, d_tip, h_scale, w_scale, seed, bend=0, offset=0)`:
  - 8 stations from d 1.3 (buried 1.0 inside the trunk/stub) to the tip, heights and widths from the profile above
    (scaled per root, §2.1); a subtle ±0.06 h hump at s 0.35 (−) and 0.6 (+);
  - section verts: bottom ±0.45 w at z −0.05, shoulders ±0.5 w at 0.45 h, upper ±0.28 w at 0.82 h, ridge at h
    (ridge offset ±0.08 w by seed);
  - tip: close with a 3-step fan sloping down to the floor;
  - jitter ±0.05, twist ±5° per station; beauty triangulation; floor-cut at z 0;
  - **pale underside tip** (decision §8.3): the tip's end-face triangles whose normal points ≥ 60° below horizontal
    get `cut` (they are invisible from any camera above the ground; they show only in the underside view).
- **Triangles:** 7 × 7 bands × 2 = 98 + tip 7 ≈ **105** each.

#### Leaf Clump ×4: exploded (365,1083,501,1205) 137 × 123, (203,851,270,914), (507,887,572,951), (201,1082,283,1159) (`z_expl_leafB.png`, `z_expl_leafR.png`)

- **Shape:** a **six-leaf star** radiating from one hub (`z_expl_leafB.png`: 6 leaves about 60° apart, ±12°), with a
  **short brown stem stub** at the hub (`z_expl_leafR.png`, `#624921`). Each leaf is a broad pointed **kite**: narrow
  base, widest at 0.45 L, straight sides to a pointed tip, **W : L ≈ 0.5**, a midrib fold that splits it into a lit and
  a shaded half. The leaves rise 30–60° from the hub's plane; tips droop slightly.
- **Size (hero governs):** clump span **2.0** (FL, BR), 1.7 (BL), 1.6 (FR); leaf L 0.9–1.1, W 0.45–0.55. The exploded
  clumps are drawn about 1.6× bigger; don't copy that.
- **Construction:** `_leaf_clump(span, seed, fan=360)`:
  - 6 leaves via the M018/M019 broad kite recipe (8-point outline `[(0.25, 0.40), (0.55, 0.50), (0.82, 0.28)]`,
    camber 0.06 L, keel 0.03 L, 16 tris each). **Use the broad-leaf recipe, not the old `NS["leaf"]`** (spiky).
  - A hidden 5-sided hub cone (10 tris) and a 5-sided stem stub (Ø 0.14, L 0.3, 10 tris) pointing into the support.
  - Per leaf: ±8 % L, ±6 % W, ±12° yaw, ±6° roll by seed. `fan` limits the yaw spread for clumps on a root flank
    (about 240°, no leaves pointing into the root or trunk).
  - **About 116 tris** per clump.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, origin = trunk axis). The aligned sheet cameras make screen x =
plan X, so the hero positions transfer directly; screen up = z cos e + Y sin e.

### 2.1 Trunk, cut face, roots

| Piece | Placement | Size | Sheet evidence | Notes |
| --- | --- | --- | --- | --- |
| Trunk (body) | axis at (0, 0) | rim outer r 2.03 at z 4.30; base r 2.45 (valleys) | f34 trunk width .42–.46 W at the rim, .56 W at h .55; top rim ring 0.95–1.10 R | 8 lobes aligned with the roots |
| Cut face | centred, top z 4.24 | R 1.8, 0.55 thick | top 99 px disc, f34 190 px | rim 0.06 proud |
| Root F (front) | az 271°, tip bending to 275° (tip centre x +0.35) | d_tip 4.55; h × 1.08 (2.15 at d 2.5); w × 1.35 (2.7 at d 2.9, 1.5 at 4.0, 0.8 at 4.5) | top front arm 2.8 wide at d 2.7–3.2; f34 broad blunt end 2.3 wide | the biggest root |
| Root L (left) | az 185°, centreline offset 0.4 toward −Y | d_tip 4.6; h × 1.0; w × 1.0 | f34 tip f 0 (4.73), front cell 4.5, top 4.4 | the profile root |
| Root R (right) | az 355° | d_tip 4.4; h × 1.0; w × 0.88 (1.75 at d 2.9, 1.1 at 3.95) | f34 4.28, front 4.42, top 4.4 | |
| Root B (back) | az 97° (centreline offset 0.4 toward −X) | d_tip 3.95; h × 0.92; w × 0.95 (2.1 at d 2.7, 1.0 at 3.7) | top only | the shortest; seen in the top and kit rear renders |

**Expected hero:** X −4.6 … +4.4, Y −4.55 … +3.95, z 0 … 4.30 → **9.0 × 8.5 × 4.3**.
- **f34_sheet (0, 12) checks:** W : H 1.60–1.72 (sheet 1.688; predicted about 1.62).
- **front_sheet (0, 10):** W : H 1.57–1.76 (sheet 1.574; predicted about 1.69; known +7 %).
- **Top:** W : D 1.00–1.10 (sheet 1.045); cut face / W 0.40–0.48 (sheet 0.478; a perspective camera above enlarges
  the top, §3.4).

### 2.2 Leaf clumps

| Clump | Hub (x, y, z) | Span / leaf L | Leaf direction | Sheet evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| FL, front-left notch | (−2.05, −2.15, 0.05), on the ground | 2.0 / 1.1 | full star, leaves 35–60° up, fanning to −X−Y | f34 f .16–.34, h .07–.41 (X −3.3 … −1.7, top z ≈ 1.75); top SW .224, .242 → (−2.47, −2.5) | the biggest; hub touching both roots' flanks or the ground |
| FR, front-right notch | (1.55, −2.45, 0.05), on the ground | 1.6 / 0.9 | 30–50° up, toward +X−Y | f34 f .59–.75, h .13–.36 (X 0.6 … 2.0); top SE .780, .280 → (2.43, −2.2) | compromise between hero and top (§3.5) |
| BL, on the left root's back flank | (−2.7, 0.55, 1.1) | 1.7 / 1.0 | fan 240°, 40–65° up, toward −X+Y | f34 f .13–.25, h .47–.70; top NW .204, .692 → (−2.64, 1.24) | hub sunk 0.1 into the root flank |
| BR, on the right root's back flank | (2.5, 0.9, 1.0) | 2.0 / 1.1 | fan 240°, 45–65° up, toward +X+Y | f34 f .78–.97, h .38–.71 (X 2.3 … 4.0, overlaps the right root's top); top NE .703, .808 → (1.74, 2.2) | hero governs; the top's NE is 1.2 further back (§3.5) |

- **Contact rule:** every hub sinks 0.1 into a root, the trunk or the ground; slide a clump along its notch's
  bisector, or along the f34 depth axis (+Y moves it up the screen by 0.208 per stud at e 12), until it touches.
- **From f34_sheet:** all 4 clumps visible; from the diagonal cameras (§3.3), 3 visible (FR at the centre, FL left,
  BR right).

## 3. View conflicts and resolutions

### 3.1 The "front three quarter" is an elevated front view

- **Evidence.** Its left and right roots are symmetric about the trunk, the front root points straight at the camera,
  and 4 clumps show in the 4 notches: an aligned camera (az ≈ 0). The ground contacts (front-root tip at h 0, side
  tips at h .13–.22) give e ≈ 12–15°, but the cut-face ellipse is drawn open as if at 18°.
- **Resolution.** Compare the sheet's f34 with an extra **`f34_sheet (0, 12)`** (and `(0, 15)` if the cut top reads
  too thin). The kit **front34 (−28, 12)** has no sheet counterpart (it shows 4 roots at an angle): self-consistency
  only. The hero governs (WorldModeling §1.1).

### 3.2 The front cell is the same view, drawn taller

- **Evidence.** Same composition and clump fractions as the f34 at e ≈ 10°, but W : H 1.574 against the f34's 1.688;
  trunk height / cut-face Ø 1.29 against 1.08.
- **Resolution.** H 4.3 (§1.1) splits the difference in the hero's favour. Compare with **`front_sheet (0, 10)`**;
  kit `front (0, 4)` is the same azimuth, lower. Accept front-cell W : H up to +12 %; record the miss.

### 3.3 Side, rear and rear three-quarter are one diagonal drawing

- **Evidence.**
  - All three show 4 roots and 3 clumps (small at the centre on the ground, mid-height left, biggest raised right).
    Side and rear are almost pixel-identical; the r34 is the same at e ≈ 12.6°.
  - A + of roots seen from a true side (az 90) or rear (180) looks like the front (3 roots, 4 clumps), so neither
    label can be literal.
  - Of the four diagonals, only **az 45 (camera front-right)** puts a small ground clump (FR) at the centre, a raised
    big clump (BR) at the right and FL at the left.
- **Resolution.** Compare the side and rear cells with an extra **`diag (45, 8)`** and the r34 with
  **`diag34 (45, 12)`**: shares, 4 roots, 3 clumps, centre clump lowest, right clump biggest. The kit `side (90, 4)`,
  `rear (180, 4)` and `rear34 (152, 12)` have no sheet counterpart (self-consistency; they're the only check on the
  back root and back of the trunk besides the top view). Record the misses.

### 3.4 Top view: the cut face looks bigger

- **Evidence.** In the top view the roots reach 2.1 cut-face radii from the axis; in the f34 and front cells 2.4–2.6.
  The top render is a perspective shot from above: the cut face (4.3 up) is nearer the camera than the root tips on
  the ground, so it is magnified about 1.17×.
- **Resolution.** Elevations govern the root reach (tips 4.4–4.6). Judge the top by root directions (±8°), relative
  root lengths (back shortest, front widest), the 4 clumps in the notches and W : D. Cut face / W tolerance
  0.40–0.48.

### 3.5 Clump positions: hero against top

- **Evidence.** FR: hero X ≈ 1.2 (tucked right of the front root), top (2.43, −2.2). BR: hero X 2.3–4.0 with leaves
  over the right root, top (1.74, 2.2) between the back and right roots.
- **Resolution.** The hero governs. FR is a compromise (1.55, −2.45); BR sits on the right root's back flank
  (2.5, 0.9, 1.0). Top tolerance ±0.12 W for FR and BR (±0.07 for FL and BL).

### 3.6 Exploded against hero

- **Sizes:** exploded clumps and the body are drawn larger relative to the cut face; the exploded body is taller
  (trunk height ≈ 1.4 cut-face Ø). The hero governs.
- **Sockets:** construction notation, not built (§1.4, decision §8.4).
- **Root module shape:** the exploded modules have a visible hump-dip-bulge ridge; the hero's ridges are nearly
  straight. Keep the hump subtle (±0.06 h).

### 3.7 Underside view: pale root tips

- Only the underside shows pale ends on the root tips; every elevation view shows bark tips. Resolution: pale only on
  the downward-facing tip triangles (decision §8.3).

### 3.8 "Solid colors, no gradients" against the user's blended-colour rule

- The user's rule wins, and the sheet itself shows painted variation:
  - the cut face's alternating ring bands (2 darker, 3 lighter) and a palest outer band;
  - the leaves are dark green at the base and lime at the tips (base `#3A7A10` → tips `#74BE16`–`#86C816` on the
    unshadowed exploded clumps: paint, §5.3);
  - the roots' lower thirds are darker and greyer (`#765441`, sat .45, the Shadow Bark swatch) than their tops even on
    lit faces, and the trunk base is greyer than its top (§5.3).
- Keep Tint low so the stump still reads "clean, solid".

### 3.9 Effects

- The sheet shows none (no glow, sparkle, dust or chips). Stage 5/6 add nothing by default (§7).

## 4. Construction plan (Build agent, stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `body()` → `ChoppedHardwoodStumpBody`: trunk + 4 buttress stubs (flat ends at d ≈ 2.7) + rim, **plus the cut
     face unioned in** (the exploded body has a ringed top). Compare with the exploded body: flared, 8 lobes, 4 stubs,
     4 valleys, pale ringed top inside a thin rim.
   - `cut_face()` → `ChoppedHardwoodStumpCutFace`: Ø 3.6, 0.55 thick, 13 sides, 5 ring loops, stepped.
   - `root()` → `ChoppedHardwoodStumpRoot`: the left root's parameters (the representative module), with its flat
     attach face.
   - `leaf_clump()` → `ChoppedHardwoodStumpLeafClump`: span 2.0, 6 leaves, stem stub.
   - Render a parts shot (`extra`, about (−20, 15)) laid out like the exploded. Compare:
     - root: chunky wedge, flat bottom, 7-sided section, ridge falling to a blunt sloped tip, L : H ≈ 1.6–2.0;
     - cut face: 12–14 sides, thickness 0.15 Ø, rings visible as facets;
     - leaf W : L 0.45–0.55, 6-leaf star with a brown stub;
     - body: lobes and stubs as above.
2. **Hero:**
   1. `_paste` (m011 pattern) the body (without the separate disc), the cut face (top z 4.24), 4 roots (§2.1, each with
      its own seed) and 4 clumps (§2.2, each with its own seed and yaw).
   2. One exact self-union, then `union_loose`, then `m004.floor_cut` at z 0.
   3. Origin at the bbox bottom centre; transforms applied. One closed shell (decision §8.6).
3. **Budget** (§4.3): hero about 1900–2300 (limit 4000), each part ≤ about 400 (limit 1000). Spend any spare on the
   trunk (up to 20 sides × 9 rings) if the facets read too big against the sheet; never on smoothing.
4. **Placeholder keys** (stage 1): `m020_bark`, `m020_cut`, `m020_leaf`. Stage 4 adds the rest (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** one squat stump; roots grow out of the trunk with no seam (extra `root_cu (-15, 12)` framed on
      the right-root junction against the Root Junction close-up); the cut top is inset in a bark rim; clumps nestle in
      the notches.
   2. **f34_sheet (0, 12) against the f34 cell:**
      - W : H 1.60–1.72; shares within ±4 (W ±2.5) of 14.3 / 9.3 / 76.4;
      - top profile within ±0.07; the root ridge lines (bark-only) within ±0.06;
      - trunk width .44–.50 W at h .8, .52–.60 at h .55;
      - cut-face ellipse 0.37–0.43 W wide;
      - clump centres within ±0.07 (§1.2); exactly 3 roots visible.
   3. **front_sheet (0, 10) against the front cell:** shares ±4, W : H 1.57–1.76, 4 clumps at §1.2 ±0.08.
   4. **Top (0, 89):** the + (root directions ±8°), back root shortest, front widest, 4 clumps in the 4 notches
      (±0.07; FR and BR ±0.12), W : D 1.00–1.10, cut face / W 0.40–0.48, the flattened front-left sector visible.
   5. **diag (45, 8) against side and rear; diag34 (45, 12) against the r34:** shares ±5, 4 roots, 3 clumps (centre
      lowest, right biggest).
   6. **Kit views** (front34, rear34, front, side, rear, underside): self-consistency only; the underside shows a flat
      faceted star.
   7. **Parts against their cells** (§4.1).
   8. **Hero size** 9.0 × 8.5 × 4.3 (±0.35 / ±0.35 / ±0.2).
6. **Stage 2:**
   - zero non-manifold, boundary, wire and loose elements; no zero-area faces or n-gons; normals outward;
   - no faces under 5° where roots, the rim, the disc and clump hubs meet bark (m011 `_tidy` / `_desliver`);
   - don't decimate the cut-face ring loops (they carry §5.5's rings), the root sections below 6 sides, or the leaves'
     8-point outlines.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Body (16 × 8 rings, rim, stubs) | 1 | 360 | 360 |
| Cut face (13 sides, 5 loops, stepped) | 1 | 155 | 155 |
| Root modules (7-sided, 8 stations) | 4 | 105 | 420 |
| Leaf clumps (6 × 16 + hub 10 + stem 10) | 4 | 116 | 464 |
| **Sum before union** | | | **about 1400** |
| **Hero after union** (seams, slivers, floor cut) | | | **about 1700–2300** (limit 4000) |
| Parts: Body (with disc) / CutFace / Root / LeafClump | | | about 480 / 155 / 105 / 116 (limit 1000) |

## 5. Colour plan (Finish agent, stage 4)

### 5.1 Swatches (flat; medians of a 54 × 58 box inside each)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Cut Wood | (46,1316,100,1374) | `#E1B27D` | 32°, 0.44, 0.88 |
| Bark | (162,1316,215,1374) | `#A97552` | 24°, 0.51, 0.66 |
| Shadow Bark | (281,1316,336,1374) | `#755541` | 23°, 0.44, 0.46 |
| Leaf | (404,1316,459,1374) | `#478623` | 98°, 0.74, 0.53 |

- **Cut Wood** equals the **sides** of the exploded Cut Face (`#E2B37B`) and the underside root tips (`#DAAB78`); the
  top-facing rings render much paler (`#F5C690`–`#FEDDAA`, §5.2).
- **Bark** sits between the rendered median (`#855A3F`) and the lit quartile (`#B47B58`): lighter than any rendered
  median. Calibrate on the render, not the swatch.
- **Shadow Bark** matches the roots' lower thirds (`#765441`) and the underside (`#684B3B` median, `#755541`-ish
  upper deciles): a painted low-bark colour.
- **Leaf** is darker and less saturated than the exploded clumps (`#5CA716`), close to the hero median (`#428F14`).

### 5.2 Rendered regions (`samp.py`, `samp2.py`, `samp3.py`, `rings*.py`, `leafrad.py`; median / lit quartile / shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Bark, f34 / front / top | V | B | `#845942` / `#8B5E44` / `#825740` | `#B47B58` / `#B37B5A` / `#B47956` | `#583D2C` / `#5F4130` / `#5C4132` |
| Bark, r34 / side / rear | V | B | `#865A41` / `#885C43` / `#895D43` | `#B77D5B` / `#B47C5B` / `#B57D5D` | `#5C402F` / `#5D4130` / `#604131` |
| Bark, exploded body (unshadowed) | (263,841,489,1067) | B | `#855A3F` | `#A46F4F` | `#5A3D2D` |
| Exploded body by height, bottom → top fifth | bands of the body box | B | `#805840` / `#835940` / `#865B41` / `#875A3D` / `#8B5A3D` | `#946549` … `#C17D50` | |
| Bark by height, f34, h 0–.2 / .2–.4 / .4–.6 / .6–.8 / .8–1 | bands | B | `#704D3B` / `#7E5843` / `#8F6146` / `#81563E` / `#996245` | `#AC7656` / `#B77D5B` / `#B97D5A` / `#A46C49` / `#D48E5D` | `#402C20` … |
| Root modules, exploded: bottom / mid / top third | FL (114,990,245,1135); R (513,971,644,1110); BL (64,906,219,1000) | B | FL `#765441` / `#936447` / `#9D6B4E`; R `#815740` / `#855B43` / `#A9714E`; BL `#624230` / `#78523B` / `#B07654` | | |
| Root junction close-up | (689,906,1003,1058) | B | `#855940` | `#B57B59` | `#55392A` |
| Underside close-up | (689,1092,1003,1252) | B | `#684B3B` (21°, 0.43) | `#9F6E51` | `#523B2F` |
| Underside root-tip ends | W components in the underside box | W | `#DAAB78` / `#D7A97F` / `#DEAC78` | `#E9B885` | `#D1A170` |
| Bark rim, f34 top band (lit lip, v > 0.62) | (195,118,420,200) | B | `#C58154` | `#DF9662` | `#A66B47` |
| Bark rim, top view / cut close-up | (840,500,945,610) / (689,742,1003,869) | B | `#80553C` / `#8F5E40` | `#BC7C52` / `#C48053` | `#5C3F2E` / `#704A34` |
| Cut face, f34 / front / top / side / rear / r34 | V | W | `#FEDDAA` / `#FDDBA9` / `#F5C690` / `#FDD9A5` / `#FDDAA9` / `#FDDBA7` | `#FEEBC1` / `#FEE8C0` / `#FAD4A2` … | `#FCC887` / `#FDC98A` / `#F0B573` … |
| Cut face, close-up | (689,742,1003,869) | W | `#FBD09B` | `#FEE0B2` | `#F7BD7C` |
| Cut face, exploded disc top / body inset | (293,730,464,807) / (305,833,451,871) | W | `#FDD49E` / `#F8CC97` | `#FEE7BD` / `#FDDDAD` | `#E2B278` / `#F4BD7E` |
| Cut face sides, exploded disc | (293,780,465,808) | W / B | `#E2B37B` / `#C59460` (shaded side) | | |
| Leaves, f34 / front / top | V | L | `#428F14` / `#499213` / `#3F8812` | `#71BE13` / `#7BC414` / `#78BE14` | `#1A5A13` / `#215812` / `#1B5210` |
| Leaves, r34 / side / rear | V | L | `#3E8813` / `#468F12` / `#458C11` | `#6FBC1A` / `#7EC516` / `#80C715` | `#1A5811` / `#235D0F` / `#23590E` |
| Leaf clumps, exploded (bottom / TL / right / left-low) | §1.4 boxes | L | `#5EAB15` / `#569D15` / `#57A116` / `#5CA716` | `#86CA15` / `#86C918` / `#88C919` / `#81CA17` | `#2D7113` … |
| Stem stub (exploded right clump) | (505,930,525,948) | B | `#624921` (37°, 0.66, 0.38) | `#6F5027` | `#493719` |

**Ring bands** (radial medians, dark ↔ light; r as a fraction of the cut-face radius):

| r / R | 0–.2 (pith) | .2–.4 | .4–.6 (ring) | .6–.8 | .8–1.0 (outer) | rim |
| --- | --- | --- | --- | --- | --- | --- |
| Close-up, centre (763,795) R 118, y × 0.40 | `#F8BD7A` / `#F5BA76` | `#F9CD98` / `#FAD09D` | `#F8BF80` / `#F9BF7D` | `#F9CE99` / `#FCD3A0` | `#FEDEB2` / `#FDE2B5` | |
| Top view, centre (891,554) R 49.5 | `#F4BB78`–`#F5B879` | `#F2C087`–`#F6CB93` | `#EFB77A`–`#F2B672` | `#F4BD80`–`#F5C58E` | `#F9CF9A`–`#F9D09C` | `#B27E53` → `#A96943` |
| f34, centre (298,150) R 90, y × 0.31 | `#FECF8F`–`#FDD194` | `#FEDDAB`–`#FEE0AF` | `#FCCF96`–`#FED192` | `#FDDEA6`–`#FEE4B3` | `#FEE8B9` → edge `#FBC687` | |

Deciles (dark → light), f34:

```
bark   #463024 #583F33 #684737 #784F36 #7F543C #8A5E45 #95684B #AC6E46 #AD7759 #C8865B
cut    #FBBF7B #FCCB87 #FECF92 #FDD49A #FCDDA6 #FDDFAD #FEE4B1 #FEE6BA #FEE9C0 #FEEFC5
leaves #134514 #175F1A #2C6F12 #397F0F #448911 #469818 #5DA60C #64B310 #67B51F #7FCA14
```

### 5.3 How the colour works

**Bark.**
- One warm brown family: hue 21–24°, sat 0.45–0.56. The big lit/shade spread (`#463024` → `#C8865B`) is the sun on
  the faceted forms; never paint by facing.
- **Painted signals:**
  1. **Shadow Bark low:** root lower thirds `#765441`/`#624230` (sat .45) and the underside `#684B3B`, against tops
     `#9D6B4E`–`#A9714E`; the exploded body's bottom fifth `#805840` (sat .50) against its top `#8B5A3D` (sat .56).
     So the low bark is darker **and greyer** in paint, not only in shade.
  2. **Warmer, slightly lighter upper trunk and rim lip:** body top fifth sat .56; the rim's top edge renders
     `#C58154` (mostly sun on an up-facing band; paint it `bark_light` to keep the lip readable, as in the close-up).
  3. **Flute grooves** read darker in every view (shade quartiles): mostly light, so only a light painted touch.
- The root junction close-up is plain `#855940`: no seam darkening.

**Cut face.**
- A pale warm tan, hue 32–37°, sat 0.28–0.52. Up-facing, so it renders much paler than the swatch.
- **Rings are paint plus stepped facets** (every view agrees): **pith r < 0.22 darker** (sat ~0.51), **0.22–0.42
  light** (0.38), **ring 0.42–0.60 darker** (0.49), **0.60–0.80 light** (0.38), **outer 0.80–1.0 palest** (0.29). The
  dark bands are about 10–14 levels darker and +0.11 sat. WorldModeling §11: "1–2 broad rings or color bands" (here
  2 plus the pith).
- The f34 shows a thin darker edge at 0.95–1.0 R (`#FBC687`): the rim's shade on the face; not painted.

**Leaves.**
- Vivid yellow-green: hue 82–98° (bases up to 108–113°), sat 0.84–0.89.
- **Base → tip** (every clump, unshadowed exploded): base `#3A7A10`–`#448816` (96°), middle `#5DAB16` (91°), tips
  `#74BE16`–`#86C816` (82–86°). The hero's back clumps are darker at the base (`#1E6413`) from the trunk's shade:
  keep them on the normal keys.
- The midrib fold gives each leaf a lit and a shaded half (geometry, not paint).

**Stem stubs:** olive-brown `#624921`, distinct from the red-brown bark (37° against 22°).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

The calibration targets are rendered medians of **unshadowed** regions (exploded parts and the close-ups), not
swatches.
- **`K.sample` kinds:** `"brown"` for the bark keys (`#855A3F`: r − g 43, sat 0.53, passes); `"green"` for the
  leaves; `"all"` on tight boxes for the cut-face bands (cream fails `"brown"`'s sat filter) and the stem.

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m020_bark` | `#855A3F` (exploded body median; root junction close-up `#855940`) | trunk and roots, the default | rough 0.9 |
| `m020_bark_light` | `#9C6847` (root top thirds `#9D6B4E`; between median and the Bark swatch `#A97552`) | upper trunk (z > 3.2) as a 30 % mix, the rim's top faces, broad patches | rough 0.9 |
| `m020_bark_shadow` | `#6E4F3D` (root lower thirds `#765441` / `#624230`, underside `#684B3B`; swatch `#755541`) | lower thirds of roots, trunk base, stub ends, groove touch | rough 0.95 |
| `m020_cut` | `#E1B27D` (swatch = disc sides `#E2B37B` = underside tips `#DAAB78`) | cut-face sides, the downward root-tip triangles | rough 0.85 |
| `m020_cut_light` | `#F9CE9A` (close-up light bands `#F9CD98`–`#FAD09D`) | bands 0.22–0.42 and 0.60–0.80 | rough 0.85 |
| `m020_cut_ring` | `#F6BC7A` (close-up pith and ring `#F5BA76`–`#F8BF80`) | pith (< 0.22) and ring (0.42–0.60) | rough 0.85 |
| `m020_cut_pale` | `#FDDFB3` (close-up outer band `#FEDEB2`–`#FDE2B5`) | outer band 0.80–1.0 | rough 0.85 |
| `m020_leaf` | `#5AA515` (exploded clump medians `#569D15`–`#5EAB15`) | leaf middles | rough 0.8, `low_spec` |
| `m020_leaf_tip` | `#7CC216` (tips `#74BE16`–`#86C816`) | outer 30 % of each leaf | rough 0.8, `low_spec` |
| `m020_leaf_base` | `#3E8012` (bases `#3A7A10`–`#448816`) | inner 30 %, keel faces, hub | rough 0.8, `low_spec` |
| `m020_stem` | `#624921` (stub) | the 4 stem stubs | rough 0.9 |

**Calibration warnings:**
- **Cut face is near the clip in the hero** (`#FEDDAA` median, R 254–255). Calibrate the three band keys on the
  close-up values; then check the f34_sheet render's cut-face median within 10 of `#FEDDAA` and the top render's within
  12 of `#F5C690`. If the bands wash out to one colour in the f34, lower the specular, not the contrast between keys.
  The band contrast (dark ring vs light band) must survive: ≥ 8 levels in the f34_sheet render.
- **Bark:** calibrate on the parts shot of the body (unshadowed) against `#855A3F`, then check the f34_sheet median
  `#845942` ±10 and the side-view medians `#885C43` ±10.
- **Leaves:** greens calibrate darker than the painted sheet (kit memory); trust the render match. The hero leaf
  median must land within 12 of `#428F14` with sat ≥ 0.8; `m020_leaf_tip` stays ≤ 88° hue. Don't reuse M018's keys
  (those leaves were much duller); M019's vivid keys (`#5C9E16` / `#72B41C` / `#4F9113` targets) are the closest
  precedent.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Bark** (fields: world z, each root's along-length s and height fraction within its section, angular distance to
  the nearest groove):
  - `bark` base;
  - **roots:** faces whose centre is below 0.4 of the local section height → 55 % `bark_shadow`, blending to 0 at
    0.6 h; tip end region (last 0.4 stud) plain `bark`;
  - **trunk base:** z < 0.6 → 45 % `bark_shadow`, fading by z 1.2;
  - **upper trunk:** z > 3.2 → 30 % `bark_light`; the rim's top faces `bark_light` (hard to the cut face);
  - **groove touch:** faces within 6° of a groove azimuth, z < 3.0 → 20 % `bark_shadow` (position, not facing);
  - broad patches (`K.patches` scale 0.8, level 0.3) between `bark` and a 35 % `bark_light` mix; never single faces;
  - stub ends of the Body part → `bark_shadow`.
- **Cut face** (field = radius on the face / R, from the ring loops):
  - 0–0.22 `cut_ring`; 0.22–0.42 `cut_light`; 0.42–0.60 `cut_ring`; 0.60–0.80 `cut_light`; 0.80–1.0 `cut_pale`;
  - `mode="blend", steps=2` on each ring edge so the bands read as soft stepped bands, not stripes;
  - sides `cut`; **hard** edge to the rim.
- **Root-tip underside triangles:** `cut`, hard edge.
- **Leaves** (field = each leaf's along-length t from its construction frame):
  - t < 0.3 `leaf_base`; 0.3–0.7 `leaf`; t > 0.7 `leaf_tip`; 3 steps, ±0.08 noise on t;
  - keel faces +0.25 toward `leaf_base`; the hub `leaf_base`; the stub `stem` (hard);
  - FL and BR (the big sunlit clumps) shift 0.1 toward the tip; BL and FR as is.
- **Hard edges only** where materials meet: rim | cut face, bark | root-tip cut, bark | stem, stem | leaf hub.

### 5.6 Texture (Tint) and finish

- **Tint** (`tint_var` per piece about 0.04, so each root and clump differs slightly):
  - bark: `K.texture` amp 0.05, scale 0.5 (broad mottling per facet group, matching the sheet's lighter/darker
    facet patches);
  - cut face: amp 0.025 (clean);
  - leaves: amp 0.035, scale 0.5;
  - never per-triangle confetti.
- **Finish:**

| Material | Roughness | Specular | Metal | Notes |
| --- | --- | --- | --- | --- |
| Bark keys | 0.9 / 0.9 / 0.95 | normal | 0 | matte timber |
| Cut keys | 0.85 | normal (lower if the bands wash out) | 0 | matte sawn wood |
| Leaf keys | 0.8 | `FOLIAGE_SPEC` (`low_spec=True`) | 0 | matte |
| Stem | 0.9 | normal | 0 | |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Bark:** f34_sheet median within 10 of `#845942`; parts-shot body within 8 of `#855A3F`; root lower thirds darker
  and greyer (sat ≤ 0.48) than root tops; f34 bottom band (h 0–.2) the darkest band.
- **Cut face:** f34_sheet median within 10 of `#FEDDAA`; top within 12 of `#F5C690`; ring order (pith dark, light,
  ring dark, light, outer palest) visible in the top render and an extra `cut_cu (-15, 35)` close-up.
- **Leaves:** f34_sheet median within 12 of `#428F14`, sat ≥ 0.8; tips lighter than bases in the parts shot.
- **Shares** per §4, step 5.2.

## 6. Joins and contact (no cracks or seams on this sheet)

- **Roots into the trunk:** each root starts at d 1.3, buried ≥ 0.9 inside the trunk's buttress; the buttress bulge
  and the root's first stations overlap so one plane runs from root ridge to trunk ("Simple angled junction"). One
  exact union; no seam ring.
- **Cut face into the collar:** the disc's sides sit inside the rim; its top 0.06 below the rim top; the body's floor
  under it is removed by the union. No coplanar faces (body floor at 3.69 must not coincide with the disc bottom:
  use 3.66 for the floor or 3.72 for the disc bottom).
- **Clumps:** hubs sunk 0.1–0.15 into ground (FL, FR) or root flank (BL, BR); stems point into the support.
- **Ground:** floor-cut at z 0 (`m004.floor_cut`): a flat underside ("Flat underside with clear planes").
- Overlap everything; exact booleans (pitfall 11).

## 7. Lighting and VFX plan (Finish agent, stages 5 and 6)

**What the sheet shows:** an ordinary sunlit stump. No glow, light, sparkle, dust, chips or particles anywhere. The
pale cut face is diffuse wood under the sun (its shade quartile `#FCC887` is still cream), not emission.
WorldModeling §1.2 forbids "an ordinary asset recolored neon with a glow halo".

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight:** nothing on the sheet glows. Emission ≥ 1.0 would export as flat Neon and
  erase the cut face's rings.
- **Studio note (Requires Manual Validation):** check in Studio that the cut face doesn't clip to flat cream under the
  game's sun (its rings must survive) and that the bark's low/high gradient and the leaf base/tip gradient survive the
  palette export.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **Recommended: none.** The sheet shows no effect, and M009 and M011–M019 decided against harvest sockets. Record
  "Stage 6 skipped: sheet shows no VFX".
- **Option** (decision §8.8): the R06 `HardwoodStump` pair, if the main session wants chopping feedback on wood nodes:
  - `harvest_hit` at the trunk front, (0, −2.25, 2.0), colour override `["#E1B27D", "#A97552"]` (cut-wood and bark
    chips);
  - `harvest_deplete` at the base centre, (0, 0, 0.5), same colours, `shape` about [6, 1, 6].
- **Not recommended:** `dust` (nothing floats on the sheet), `ore_glint` (a stump doesn't sparkle), any light.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by `git grep` of the repo, plus every sheet .blend (zstd-decompressed) searched with
`blendall.py` (`HardwoodStump` occurs 57 times in `FlintbornWorldKit.blend` and 58 in `R06.blend`):
- **R06 kit:** `HardwoodStump`, `HardwoodStumpBody`, `HardwoodStumpCutFace`, `HardwoodStumpRoot`,
  `HardwoodStumpChunk`, `HardwoodStumpBarkStrip`, `HardwoodStumpLowStump`; keys `r06_hardbark`, `r06_rootbark`,
  `r06_cutwood`, `r06_leaf`, `r06_dirt`. Also `SoftwoodLogStump`.
- **W05:** `LogAndStump*`, `LowStump`, `OakLeafClump`. **W06:** `LeafClumpLarge/Medium/Small`. **R05:**
  `BerryShrubLeafClump`. **M019:** `ResinBranchLeafClump`. **Camp sheet 06 / lobby:** `Stump`, `ChoppingStump`.
  **V10:** `ResinheartStump*`. **W16:** `ColumnStump`.
- **`src`:** no hardwood or stump node id.
- `M.mk` would silently rename a clash to `<name>M020`, so avoid all of these.

**Proposed names.** None occur in the repo, the decompressed kit .blend or any sheet .blend; `m020_` is unused.

| Object | Part | Why |
| --- | --- | --- |
| `ChoppedHardwoodStump` | hero | R06 owns `HardwoodStump`; the header calls it "a chopped hardwood stump" |
| `ChoppedHardwoodStumpBody` | Stump Body (with the cut face unioned in, as drawn) | R06 owns `HardwoodStumpBody` |
| `ChoppedHardwoodStumpCutFace` | Cut Face | R06 owns `HardwoodStumpCutFace` |
| `ChoppedHardwoodStumpRoot` | Root Module (the left root as the representative) | R06 owns `HardwoodStumpRoot` |
| `ChoppedHardwoodStumpLeafClump` | Leaf Clump | W05, W06, R05 and M019 own other `*LeafClump` names |

- Palette keys `m020_*` (§5.4). Collection `Kit/M020 Hardwood Stump`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **9.0 × 8.5 × 4.3, cut face Ø 3.6** (recommended: leaf-anchored, a big old hardwood stump at chest
   height to the character), or R06's scale (about 13.8 × 6.5, ×1.5, taller than the player).
2. **Trunk height:** **4.3 to the rim** (recommended: hero W : H −4 %, front cell +7 %), or 4.1 (hero-exact; front
   +13 %), or 4.7 (matches the side/rear/exploded drawings; hero −12 %).
3. **Pale root-tip ends** (underside view only): **include them on the downward-facing tip triangles** (recommended:
   cheap, matches the underside close-up, invisible from any camera above ground), or plain bark tips.
4. **Body sockets:** **not modelled**; Body part stub ends are flat `bark_shadow` faces (recommended: hidden in the
   hero; holes add risk), or model recessed sockets in the Body part only.
5. **Cut face:** **an inset 0.55-thick disc, rim 0.06 proud, rings as stepped facet loops plus colour bands**
   (recommended: matches the hero rim and both close-ups), or flush with the rim.
6. **Hero packaging:** **one closed shell** (recommended: STAGES default and the one-mesh-per-asset contract), or
   roots/clumps as separate objects.
7. **Exports:** the hero plus 4 parts (`...Body`, `...CutFace`, `...Root`, `...LeafClump`) (recommended). R06's
   drops and `LowStump` depleted state are not on this sheet and are not built unless asked.
8. **Stage 5/6:** **no emission, light or VFX** (recommended: the sheet shows none; consistent with M009–M019), or the
   R06-style `harvest_hit` / `harvest_deplete` pair with wood-chip colours (§7.2).
9. **Comparison cameras** (recommended, §3): `f34_sheet (0, 12)` for the hero, `front_sheet (0, 10)` for the front
   cell, `diag (45, 8)` for the side and rear cells, `diag34 (45, 12)` for the r34, kit top for the top; kit front34,
   rear34, side, rear, underside as self-consistency only; extras `root_cu (-15, 12)`, `cut_cu (-15, 35)` and a parts
   shot `(-20, 15)`.
10. **Clump placement conflicts** (§3.5): **hero governs** (recommended), with the top's FR/BR offsets recorded.
11. **Names** as proposed.

## 9. Pitfalls to avoid

1. **Cylinder with logs stuck on.** The roots must grow out of buttress flares on the trunk with one continuous plane
   (Root Junction close-up). Check the junction extra and the f34 left/right trunk edges (2.52 at z 2.1 widening into
   the root ridge).
2. **A tall stump.** The hero is squat: W : H 1.69 in the f34, roots joining at about half the trunk height. Don't
   copy the side/rear drawings' taller trunk.
3. **Comparing with the wrong camera.** The sheet's "front three quarter" is an aligned elevated front view; the
   side/rear/r34 are one diagonal view (§3.1–§3.3). The kit front34/side/rear have no counterparts.
4. **A raised slab top.** The cut face is inset in a thin bark rim; no pale disc sides show above the bark in any hero
   view.
5. **Painted-only rings or a plain flat top.** The rings are stepped facet loops **and** colour bands: pith, light,
   dark ring, light, palest outer. Don't decimate the ring loops in stage 2.
6. **Round smooth trunk or noisy trunk.** 8 lobes with real grooves, irregular mid-size triangles (0.4–0.7 stud
   edges), flat shading; no subdivision, no per-vertex noise beyond ±0.05.
7. **Logs for roots.** Roots are angular wedges (7-sided "house" section, flat bottom, ridge on top), tall at the
   trunk (2.0 at d 2.5) and blunt at the tip; not tubes, not cones.
8. **Spiky leaves.** Broad kites (W : L 0.45–0.55), six per clump, midrib fold; use the broad-leaf recipe, not
   `NS["leaf"]`.
9. **Floating clumps.** BL and BR sit on the root flanks (hub sunk 0.1); FL and FR on the ground in the notches.
10. **Colour by facing.** Shadow bark goes by height within the root/trunk, never by normal; `K.check` facing
    correlation < 0.5. The pale root-tip triangles are chosen by the tip region and their downward normal: that is a
    material (cut wood on the underside), so record it as the one deliberate normal-based selection.
11. **Exact booleans.** Overlap everything: roots ≥ 0.9 into the trunk, the disc 0.55 into the collar, hubs 0.1 into
    their support, floor cut at z 0; no coplanar faces (body floor vs disc bottom). Remove slivers with m011's
    `_tidy` / `_desliver`.
12. **Washed-out cut face.** It renders near the clip in the hero; keep ring contrast ≥ 8 levels.
13. **Naming clashes** with R06 `HardwoodStump*`, `*LeafClump`, `LowStump`, `Stump` (§8). Only one agent drives
    Blender at a time; no commits, pushes or exports in stage agents.

## Decisions (main session, 2026-10-28)

All recommendations are accepted:
1. Size: 9.0 × 8.5 × 4.3.
2. Trunk height: 4.3.
3. Pale cut-wood root tips on the down-facing tip triangles only.
4. No body sockets.
5. Cut face inset in the bark rim.
6. One closed shell.
7. Hero plus 4 parts; no depleted variant.
8. No VFX.
9. Comparison cameras: `f34_sheet (0,12)`, `front_sheet (0,10)`, `diag (45,8)`, `diag34 (45,12)`.
10. The hero view governs clump placement.
11. Names as proposed: `ChoppedHardwoodStump`, plus `Body`, `CutFace`, `Root` and `LeafClump` suffixes.
