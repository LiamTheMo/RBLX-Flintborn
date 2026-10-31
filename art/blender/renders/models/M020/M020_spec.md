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
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m020_study\`.
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

## Stage 1: Modelling (modeller, 2026-10-28)

Builder `art/blender/kit/mcp/m020.py` (`build()`), driven in a background Blender on port 9878 with the work file
`art/blender/assets/kit/wip/M020.blend` (saved after every build). Collection `Kit/M020 Hardwood Stump`.

- **Trunk** (`trunk()`): six 16-vertex rings (z −0.15, 0.5, 1.2, 2.0, 2.8, 3.55) plus the rim ring; a crest on each
  root azimuth, grooves ±22°, a crest on each diagonal (8 lobes lined up with the roots). Mean radius, groove depth and
  buttress bulge as §1.4 (bulge σ 16° instead of 20°, so the groove verts beside each root don't poke past the root's
  flanks). Jitter r ±0.035, z ±0.03, twist ±3°; diagonals mostly one way (15 % flipped), so the lobes read as long
  vertical facets, not noise.
- **Rim and cut face built into the body top** (no boolean): rim ring on the 16 trunk azimuths at `RIM_Z` (radius =
  outline + 0.22, dipped 0.06 at the grooves), zipped (`_zip`, any vertex counts) to an inner edge on the cut-face
  outline, a 0.06 wall down to the 13-vertex outline loop, then four ring loops (12, 12, 11, 10 verts at 0.80, 0.60,
  0.42, 0.22 R, stepped up 0.012–0.030) and the centre (+0.035). The outline carries the flattened front-left sector
  (az 240 ± 22, 0.87) and the shallow dips (§1.3).
- **Height:** first built at the spec's 4.30; the f34 W : H came out 1.585 (sheet 1.688), so `RIM_Z` went to **4.15**
  (cut face top 4.09; inside decision 2's ±0.2). Now f34 1.625, front 1.691.
- **Roots** (`_root()`): 7-sided "house" sections (flat bottom, shoulders at 0.45 h, upper flanks ±0.25 w at 0.78 h,
  ridge) at stations 1.3 … 4.2 (profile §1.4, mapped to each root's tip distance), the subtle hump, ±5° twist with the
  bottom kept flat, and a blunt sloped end (end ring 0.72 w / 0.42 h, then a tip point at 0.22 h). Front root height
  ×0.95 and width ×1.15 (the spec's 1.08 / 1.35 made a bulbous blob in front of the trunk in the long-lens f34). Each
  root has its own bottom z (−0.05 … −0.11), so no coplanar caps meet in the union.
- **Leaf clumps** (`_clump()`): six broad kite leaves (M019 recipe: 8-point outline, ridge, keel; fold 0.3), all
  starting at the hub centre under a low 5-sided crown (r 0.14 s, apex 0.08 s), so each leaf's base runs through the
  crown (a first version with leaves starting on the crown's skin left 5 separate shells). Leaf L 1.35 s, W 0.64 s
  (W : L 0.47), pitch 38–66°, tips nearly level. 5-sided brown stem stub; the crown's sunk foot is painted `stem` too.
- **Hero clumps:** FL span 2.7, FR 2.2 (fan 300°), BL 2.2, BR 2.7 (fan 260°, toward the back). BL/BR are dropped
  straight down onto their root's top/back flank (hub sunk 0.1). FL/FR start at their ground hubs and slide toward the
  axis only until a probe build of the clump overlaps the body (`_overlaps`; 0.1 each), so the hero stays one shell.
  Final hubs: FL (−1.83, −1.93, 0.22), FR (1.45, −2.22, 0.2), BL (−2.97, −0.04, 1.01), BR (2.77, 0.31, 1.15). The
  clumps are bigger than the spec's span 2.0 / leaf 1.1: at that size the f34 leaf share was 9–11 % (sheet 14.3 %).
- **Parts:** `body_part` (trunk + 4 stubs = roots cut at d 2.9 with flat ends, no sockets), `cut_face_part` (13-sided,
  0.55 thick, the same ring loops on top), `root_part` (left root from d 2.0, flat attach face), `clump_part` (span 2.0).
- **Comparison cameras:** decision 9's `f34_sheet (0,12)`, `front_sheet (0,10)`, `diag_sheet (45,8)` and
  `diag34_sheet (45,12)`, plus `top_sheet (0,89)` and an extra `f34_e15_sheet (0,15)`, all through M018's 3× long lens
  (the sheet is drawn near-orthographic; with the kit lens the near front root swelled and the cut top didn't open).
  Close-ups `cut_cu`, `root_cu`, `under_cu`; exploded and parts shots.

**Measured against the sheet (`m020.measure()`, the study's masks on both images):**

| View | W : H sheet (ours) | Leaves L | Cut W | Bark B |
| --- | --- | --- | --- | --- |
| f34 (f34_sheet) | 1.688 (1.625) | .143 (.144) | .093 (.051) | .764 (.805) |
| front (front_sheet) | 1.574 (1.691) | .148 (.146) | .052 (.041) | .800 (.813) |
| side (diag_sheet) | 1.476 (1.578) | .120 (.156) | .032 (.028) | .847 (.816) |
| r34 (diag34_sheet) | 1.525 (1.472) | .093 (.155) | .051 (.053) | .856 (.792) |
| top (top_sheet) | 1.045 (1.060) | .197 (.198) | .307 (.294) | .496 (.508) |

- The f34 top profile is within ±0.07 everywhere except f .10 (.55 against .43: the BL clump stands a little further
  left) and f .95 (.58 against .46: the right root tip is a little high). Width per height is within ±0.05 except at
  h .7 (.49 against .63: the sheet's BL/BR clumps reach higher).
- f34 cut share .051 against .093: at e 12 the cut top opens 0.21 (sin 12°); the sheet draws it at 0.31 (≈ 18°, §3.1).
  `f34_e15_sheet` shows the e 15 look.
- Diagonal views: the composition matches (4 roots; 3 clumps, the small one at the centre on the ground, the biggest
  raised at the right). Our side root tips stand higher (.45–.48 against .13–.15) and the trunk is relatively wider
  (.53 against .45 at h .8): the sheet's side/rear cells are a different drawing (§3.3), and the hero governs.
- Top: the + of roots, back root shortest, front widest, 4 clumps in the notches; W : D 1.06. The back clumps sit
  further forward than in the sheet's top (width at h .8–.9 .33/.21 against .59/.41): hero placement governs (§3.5).

## Stage 2: Optimisation and cleanup

Pipeline per object (`_make`): `M.union_loose` (exact union of each shell in turn) → `m004.floor_cut` at the ground →
`m016._clean_mesh` (weld, ears, inner pockets, m011 sliver clean, forced slivers) → `_finish` (M.finish plus a repair
loop) → `_polish`. The polish splits quads, re-fans the floor cap (`beautify_fill`, a Steiner point in big floor
needles, and the long edges of any floor needle split at their midpoints: flat, so nothing moves), forces slivers at
5°, re-centres and redoes the UVs.

| Object | Tris (budget) | Size (studs) | Shells | Non-manifold / boundary / wire / loose | Min corner | Self-intersections |
| --- | --- | --- | --- | --- | --- | --- |
| ChoppedHardwoodStump (hero) | **1888** (4000) | 8.97 × 8.47 × 4.17 | 1 | 0 / 0 / 0 / 0 | 5.01° | 0 |
| ChoppedHardwoodStumpBody | 638 (1000) | 7.32 × 7.33 × 4.17 | 1 | 0 / 0 / 0 / 0 | 5.11° | 0 |
| ChoppedHardwoodStumpCutFace | 142 (1000) | 3.66 × 3.56 × 0.58 | 1 | 0 / 0 / 0 / 0 | 17.71° | 0 |
| ChoppedHardwoodStumpRoot | 102 (1000) | 2.68 × 2.31 × 2.24 | 1 | 0 / 0 / 0 / 0 | 11.14° | 0 |
| ChoppedHardwoodStumpLeafClump | 208 (1000) | 1.94 × 1.70 × 1.49 | 1 | 0 / 0 / 0 / 0 | 5.43° | 0 |

- All objects: zero-area faces 0, n-gons 0, duplicate verts 0, normals outward, no custom normals, origin at the
  bottom centre (K.check clean), rotation 0, scale 1.
- Hero size against the 9.0 × 8.5 × 4.3 target: W −0.03, D −0.03, H −0.13 (the deliberate height change above).
- Earlier failures, for the verifier:
  - FL / FR clumps that didn't touch a root left a second shell (fixed by the overlap probe).
  - Clump seeds 20081/20082/20084 left 2 non-manifold edges where two FL leaves met edge-on, plus a few crossing faces
    at BR (the seeds are now 20091/20092/20094).
  - A 3.1° floor needle at the FL hub's ground contact (fixed by the midpoint split).

## Stage 3: UV

`M.smart_uv` with angle 45, ANGLE_BASED re-unwrap and margin 0.008 (gap 0.016), then `m012._uv_unfold`.

| Object | Islands | Overlap pairs | Flipped | Min gap | Density min / med / max | Conformal stretch p95 |
| --- | --- | --- | --- | --- | --- | --- |
| Hero | 392 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.012 |
| Body | 43 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.020 |
| CutFace | 6 | 0 | 0 | 0.0162 | 1.0 / 1.0 / 1.0 | 1.000 |
| Root | 9 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.018 |
| LeafClump | 62 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.020 |

## Stage 4: Materials, colour and texture

**Pass 1 (dome, `m020.calibrate()`):** each key on the kit test dome against §5.4's targets. **Pass 2 (hero):**
fitted on the lit hero views (f34_sheet first, then front and top), as linear-light factors.

| Key | Target | Dome hex (rendered) | Final hex (pass 2) |
| --- | --- | --- | --- |
| m020_bark | #855A3F | #694935 (131, 90, 66) | **#72503A** (×1.2) |
| m020_bark_light | #9C6847 | #7B553C (154, 104, 73) | **#865D42** (×1.2) |
| m020_bark_shadow | #6E4F3D | #584133 (110, 80, 63) | **#604738** (×1.2) |
| m020_cut | #E1B27D | #B0926C (223, 179, 125) | **#B09368** (G, B trimmed: the hero read pinker than the sheet) |
| m020_cut_light | #F9CE9A | red clipped on the dome; from m020_cut's dome ratio #C3A786 | **#C3A880** |
| m020_cut_ring | #F6BC7A | #C69969 (252, 188, 122) | **#C69A65** |
| m020_cut_pale | #FDDFB3 | clipped (the dome gave a pink #F9B499); from m020_cut's ratio #C6B59C | **#C6AF8D** (outer band too pale on the top) |
| m020_leaf | #5AA515 | #4C8814 (88, 162, 21) | **#52A61A** |
| m020_leaf_tip | #7CC216 | #659E15 (120, 191, 22) | **#6CC11B** (hue 87°) |
| m020_leaf_base | #3E8012 | #366C11 (61, 125, 19) | **#3A8517** |
| m020_stem | #624921 | #4C3810 (97, 73, 38) | **#4C3810** |

Final rendered medians against the sheet:

| Region | Sheet | Ours | Notes |
| --- | --- | --- | --- |
| Bark, f34 / front / top | #845942 / #8B5E44 / #825740 | #805841 / #7F5841 / #825B45 | within 4 / 12 / 5 |
| Bark, f34 by height (bottom → top fifth) | #704D3B #7E5743 #8F6146 #81563E #956144 | #78553E #825B43 #895F45 #8B5F44 #916348 | darkest at the bottom, as on the sheet |
| Cut face, f34 / front / top | #FEDDAA / #FDDBA9 / #F5C690 | #FFD7A2 / #FFD7A3 / #FDD299 | within 8 / 6 / 12 |
| Ring bands, top view (pith, light, ring, light, outer) | #F4BA78 #F4C58E #F1B572 #F5C48D #F9D09D | #FDBF78 #FAD199 #FEC079 #FCD39A #FFE5B5 | same order; dark ↔ light 18–25 levels (≥ 8) |
| Leaves, f34 / front / top | #428F14 / #499213 / #3F8812 | #439014 / #418B13 / #5EBF19 | f34 within 1; our studio lights the top from above |
| Diagonal views (bark / leaves) | #885C43 / #468F12 | #6C4A35 / #36730E | the studio's sun is behind-left of the az 45 camera: not fitted (M013/M017 practice) |

**Blending** (by position, never by facing; quarter steps through `K.mix_key`):
- **Trunk:** z < 0.6 → 45 % `bark_shadow`, fading out by z 1.2; within 6° of a groove and z < 3 → 25 %; z > 3.2 →
  25 % `bark_light`; broad noise patches (scale 0.5, level 0.3) → 25 % light; rim top 25 % light; inner wall 25 %
  shadow.
- **Roots:** by height within the local section: below 0.4 h → 55 % shadow, fading out by 0.6 h (halved on the last
  0.4 stud); broad light patches elsewhere. Body stub ends 75 % shadow.
- **Cut face:** by radius over the outline radius: pith `cut_ring`, 0.22 `cut_light`, 0.42 `cut_ring`, 0.60
  `cut_light`, 0.80 `cut_pale`. Faces within 0.05 of a ring edge take the 50 % mix. Disc sides are `cut`.
- **Leaves:** base → mid → tip along each leaf's length (bands 0.12–0.40 and 0.60–0.88, ±0.08 noise, keel toward the
  base). Crown `leaf_base`; its sunk foot and the stub are `stem`.
- **Floor** (after the cut):
  - `cut` within 0.7 of a root tip along the root: the underside view's pale ends. This follows decision 3 and is the
    one deliberate down-facing selection (29 faces on the hero, visible in `under_cu`).
  - `leaf_base` beside a leaf.
  - Plain `bark` elsewhere.

**Tint:** per piece ±4 % (`tint_var` 0.04), with broad mottling: bark amp 0.05 at scale 0.5, cut 0.025 at 0.7,
leaves 0.035 at 0.5. No per-face confetti.

**Finish:** bark rough 0.9 (shadow 0.95), cut 0.85, leaves 0.8 low-spec (foliage specular), stem 0.9; no metal.

**K.check facing correlation:**
- Hero 0.45 (leaf family), clump 0.44, root 0, cut face 0.
- The Body part read 0.50 because the checker's hue clustering puts the cut-wood keys in the bark family; with the
  bark keys alone it is 0.15. The Body and hero carry `kit_shading_ok = "cut-wood top is its own material (sawn face),
  grouped with bark by hue"`.
- The floor uses plain `bark`: a darker floor key pushed the bark family to 0.6–0.7.

## Stage 5: Lighting

Skipped (decision 8). The sheet shows an ordinary sunlit stump: no emissive key, no light.

Requires Manual Validation in Studio:
- the cut face keeps its rings under the game's sun (no clip to flat cream);
- the bark's low/high gradient and the leaves' base/tip gradient survive the palette export.

## Stage 6: VFX

Skipped (decision 8). The sheet shows no glow, sparkle, dust or chips. No sockets (the renders used vfx=True, with
nothing to realise).

## Modeller's notes for the verifier

- Builder: `m020.build()`. Measuring: `m020.measure()` (needs the renders). The renders are in this folder; the
  `*_sheet` shots use a 3× long lens. Compare:
  - `f34_sheet` with the sheet's front three-quarter;
  - `front_sheet` with the front cell;
  - `diag_sheet` with the side and rear cells;
  - `diag34_sheet` with the rear three-quarter;
  - `top_sheet` with the top.
- Deliberate departures from the spec (each explained above):
  - height 4.15, not 4.30;
  - clumps bigger (span 2.2–2.7, leaf 1.35 s), and FL / FR 0.1 nearer the axis;
  - front root height ×0.95 and width ×1.15;
  - floor key `bark`, not `bark_shadow`;
  - `kit_shading_ok` on the Body and the hero.
- Known leftovers:
  - The f34 cut top opens less than the sheet's (camera e 12 by decision 9).
  - In the diagonal cells the sheet's side root tips are lower and its trunk narrower.
  - The sheet's top view puts the back clumps further back.
  - The root part is a plain wedge: the exploded modules' hump-dip is only ±0.06 h here.
  - The clump part on its own reads a little tulip-like. Its leaves rise 38–66° to match the hero's upright clumps;
    the sheet's exploded clump is flatter.
  - In the exploded shot, the right and back root copies are partly hidden behind the body.
- Shared helpers untouched. `m020.py` imports `m004`, `m011`, `m012` and `m016` (m016's `_clean_mesh` and
  `_self_hits`).

## Stage 7 — Verification (round 1)

Independent verifier, 2026-10-28. Read-only background Blender on port 9880, with `wip/M020_verify.blend` (not saved;
`build()` not called). Fresh renders were made with `m020.render_views()` into the verifier's scratch folder (the
`*_sheet` cameras of decision 9, 3x lens), then put side by side with sheet crops at equal height. Everything below
was re-measured with the verifier's own bmesh, BVH and UV-raster scripts, plus `m020.measure()`/`stats()` (the study's
masks) on the fresh renders.

**Result: FAIL, 5/10.** The mesh is technically clean, and the medians and silhouette ratios are on target. Three
features read clearly unlike the sheet: the trunk's flutes and notched rim, the leaf clumps, and the Root part.

### Technical checks (all re-measured)

| Object | Tris (budget) | Size (studs) | Shells | Non-man. / boundary / wire / loose | N-gons / zero-area / dup | Winding | Min corner | Self-hits | UV overlap px / flips / outside |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ChoppedHardwoodStump | 1888 (4000) | 8.966 × 8.470 × 4.175 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | consistent, volume +80.2 | 5.01° | 0 | 0 / 0 / 0 |
| …Body | 638 (1000) | 7.322 × 7.332 × 4.175 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | ok, +72.5 | 5.11° | 0 | 0 / 0 / 0 |
| …CutFace | 142 (1000) | 3.662 × 3.558 × 0.585 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | ok, +5.31 | 17.71° | 0 | 0 / 0 / 0 |
| …Root | 102 (1000) | 2.679 × 2.314 × 2.238 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | ok, +5.12 | 11.14° | 0 | 0 / 0 / 0 |
| …LeafClump | 208 (1000) | 1.941 × 1.701 × 1.489 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | ok, +0.19 | 5.43° | 0 | 0 / 0 / 0 |

- **Size against the decided 9.0 × 8.5 × 4.3:** W −0.03, D −0.03, H −0.125. All inside the tolerance (±0.35 / ±0.35 /
  ±0.2).
- **Interior faces:** none. Every object is one closed manifold shell with 0 self-intersections, so nothing can be
  enclosed.
- **Origin and transforms:** the origin is at the bbox bottom centre (local bbox centre (0, 0), min z 0). Rotation is
  0, scale is 1, there are no modifiers and no custom normals. Shading is flat.
- **UVs:** `UVMap` is present on all objects.
- **Materials:** Principled BSDF throughout, with a `Tint` corner attribute (spread 0.90–1.06 per key; no confetti).
  Roughness is 0.8–0.95, there is no metal, and no material has emission.
- **Root ridges** (bark-only raycast down, d = distance from the trunk axis): F 1.98 / 1.61 / 1.35 / 1.17 at d 2.5 / 2.9
  / 3.4 / 3.8; L 2.24 / 1.68 / 1.42 / 1.23. The ridges follow the spec profile. The plan azimuths of the root peaks
  (355°, ~100°, 190°, ~273°) are also correct.
- **Trunk relief** (bark-only radius by azimuth): z 2.5 is 2.03–2.40 (median 2.11); z 3.0 is 1.97–2.21; z 3.5 is
  1.91–2.10; z 3.9 is 1.86–2.05. Away from the root bulges the lobes vary by only about ±0.05–0.08 stud (±3 %).
- **VFX:** no sockets, no children and no emissive keys, as decision 8 requires. Stage 5 and 6 skips are justified.
- **`kit_shading_ok`:**
  - The **Body** waiver is justified. My re-measure gives a bark-family facing correlation of 0.16, and bark plus the
    cut keys 0.505. The pale sawn top is a real separate material, like `REGION_KEYS` `wood_end`.
  - On the **hero** the waiver isn't needed (stored 0.45; mine: bark 0.22, bark + cut 0.36), but it is harmless.
  - The leaf family reads 0.45 (under 0.5). That's because `leaf_tip` faces sit where the leaves level out (mean
    n.z 0.83) and the keel faces are pushed toward `leaf_base` (the spec's rule). Watch it if the leaves are reworked.
  - Within the cut family, the down-facing `cut` root-tip floor faces are decision 3's deliberate material. That is
    accepted.

### Views against the sheet (fresh renders)

| View (camera) | W : H sheet / ours | L / W / B shares, sheet → ours |
| --- | --- | --- |
| f34 (f34_sheet 0,12) | 1.688 / 1.625 | .143/.093/.764 → .144/.051/.805 |
| front (front_sheet 0,10) | 1.574 / 1.691 | .148/.052/.800 → .146/.041/.813 |
| side, rear (diag_sheet 45,8) | 1.476, 1.551 / 1.578 | .120/.032/.847 → .156/.028/.816 |
| r34 (diag34_sheet 45,12) | 1.525 / 1.472 | .093/.051/.856 → .155/.053/.792 |
| top (top_sheet 0,89) | 1.045 / 1.060 | .197/.307/.496 → .198/.294/.508 |

- **f34 top profile:** within ±0.07 except at f .10 (.56 against .43) and f .95 (.60 against .46).
- **Composition:** 3 roots plus 4 clumps in the f34 and front. In the diagonals, 4 roots plus 3 clumps, with the
  centre clump lowest and the right one biggest. In the top, a + with the back root shortest and the front widest. All
  as the sheet.

### Colours (study masks; median / lit quartile / shade quartile; Δ = ours − sheet, per channel)

| Region | Sheet | Ours | Δ |
| --- | --- | --- | --- |
| Bark f34 | #845942 / #B47B58 / #583D2C | #805841 / #9A6A4D / #593E2E | median −4,−1,−1; **lit −26,−17,−11** |
| Bark front | #8B5E44 / #B37B5A | #7F5841 / #9A6B4E | −12,−6,−3; lit −25,−16,−12 |
| Bark f34 by fifth (bottom → top) | #704D3B #7E5743 #8F6146 #81563E #956144 | #78553E #815942 #885E45 #8B6045 #926448 | darkest at the bottom, as the sheet |
| Bark diagonal (side / r34) | #885C43 / #865A41 | #6C4A35 / #6D4A35 | −28,−18,−14 (studio sun behind the az-45 camera) |
| Body part / exploded body | #855A3F | #8E6246 | +9,+8,+7 |
| Root part / exploded FL module | #8F6146 | #97684B | +8,+7,+5 |
| Cut face f34 / front / top | #FEDDAA / #FDDBA9 / #F5C690 | #FFD7A2 / #FFD7A3 / #FDD299 | +1,−6,−8 / +2,−4,−6 / +8,+12,+9 |
| Cut lit / shade, f34 | #FEEBC0 / #FCC887 | #FFE0B1 / #FFC789 | ring contrast survives |
| CutFace part, top / sides | #FDD49E / #C3925F | #FECF92 / #C39D68 | +1,−5,−12 / 0,+11,+9 |
| Leaves f34 | #428F14 / lit #70BE12 / shade #195913 | #469018 / #7AE021 / #25580C | median +4,+1,+4; lit +10,+34,+15 |
| Leaves top | #3F8812 / shade #1B5111 | #60C01C / #408715 | **+33,+56,+10**; no dark leaf halves |
| Exploded clump / clump part | #5EAB15 | #367A10 | −40,−49,−5 (upright tulip leaves turned from the light) |
| Stem stub | #624921 | #4F3B20 | −19,−14,−1 (the key `#4C3810` equals the dome's *rendered* value) |
| Underside bark | #684B3B | #3A261B | −46,−37,−32 (studio light from above; plain floor) |

- **Medians:** the f34 and front medians and the bark height gradient match. Blending is smooth: quarter-step mixes,
  with no hard patches except at real material changes.
- **Contrast:** the sheet's lit facets are much brighter (lit quartile about 26 levels up). Most of that is geometry:
  the sheet's flute flanks and root-ridge planes turn toward the sun (see B1).

### Blockers

**B1. The trunk reads as a smooth frustum with a plain elliptical cut top.**
- **On the sheet:** the trunk has deep V-flutes running the full height, giving 8 lobes. In the f34 there are 4–5
  strong vertical ridges across the front. The bark rim breaks into lobes, and the cut-top outline is notched where
  the flutes meet the rim: the f34's front-right and right notches, and a stepped drop on the right.
- **Ours:** the lobes vary by only about ±0.06 stud (±3 %) above z 2.5. The rim and outline are a clean ellipse; the
  0.04–0.13 outline dips don't read.
- **Fix in `m020.py`:**
  - Raise `GROOVE` to about **((1.0, 0.38), (2.5, 0.32), (3.65, 0.26))**, so the grooves cut 0.25–0.4 stud between
    crests. Narrow `GROOVE_OFF` to about 18°, so each groove is a sharp V between broad lobes.
  - Make the lobe crests stand out by about 0.08 on the 4 diagonal crests.
  - Carry the grooves through the rim: raise `RIM_DIP` to about 0.18. Push the cut-face `outline()` inward by about
    0.12–0.18 R at the groove azimuths (5–8 notches, not 2–3 shallow dips), so the rim and cut edge show the sheet's
    notches. Keep the inset and the 0.06 lip.
- **Re-check:** in `f34_sheet`, 4–5 readable grooves across the front, rim notches at f ≈ .56 and .71, and the bark
  lit quartile within 12 of `#B47B58`. Keep the silhouette within §4 step 5.2 (the trunk width .44–.50 W at h .8 will
  shrink a little; re-tune the mean radius if needed).

**B2. The leaf clumps are upright, crumpled "tulips", not the sheet's broad flat kite rosettes.**
- **On the sheet:** each clump is a star of 5–7 broad, flat, pointed kite leaves fanning outward and low. Each leaf
  has a crisp lit half and a dark half across the midrib; the exploded clump lies almost flat.
- **Ours:**
  - `LEAF_PITCH` 38–66° plus the +8° handle stands the leaves up into a cup, and `FOLD` 0.3 with `RIDGE` 0.08 L folds
    each one into a narrow V. In the f34 and front they read as curled lettuce or grass.
  - The top view shows no dark halves (shade quartile #408715 against #1B5111). The exploded clump renders 40–50
    levels too dark because the leaves are turned from the light.
  - FL and FR also show a dark brown stalk on the ground (the hub foot is painted `stem`, about 0.25 stud visible).
  - The LeafClump part has a long visible stem.
- **Fix:**
  - Set `LEAF_PITCH` to about (15, 35) and drop the handle offset to +0–4°, with tips level or drooping slightly
    (`LEAF_SLOPE` (−18, −4)).
  - Set `FOLD` to about 0.12 and `RIDGE` to about ((0.42, 0.05), (0.76, 0.025)), so each leaf is a broad, near-flat kite
    with a midrib crease.
  - Keep W : L 0.5. Consider `LEAF_W` 0.70 so leaves read broad from the f34.
  - For BL and BR, keep the fan but tilt the clump normal less (rosettes lying on the root flank).
  - Keep the hub foot below the ground or root surface (`sink` ≥ the crown height) and use `leaf_base` on any visible
    part. Shorten the LeafClump part's stem so only a stub shows (≤ 0.1 of the clump height).
- **Re-check:** the leaf share stays within ±4 of 14.3 % in the f34. If it drops, raise the span back toward 2.7, not
  the pitch. The top leaf median should come within 15 of `#3F8812`, with visible dark halves. Compare the exploded
  clump with the sheet's flat six-leaf star.

**B3. The Root part reads as a rock, not a root module.**
- **Ours:** `root_part` starts at d 2.0, which gives 2.68 long × 2.24 high. L : H is 1.2 against the spec's 1.6–2.0,
  and the exploded BL module is 1.64. In the parts shot and the exploded view it reads as a boulder.
- **Fix:** start the part at d 1.3 (or 1.0) with the flat attach face, so L : H is about 1.7. Make the ridge line
  visible: raise `HUMP` to about ±0.10 h, as the exploded modules show a hump, a dip and a bulge. Keep the 7-sided
  house section.
- **Re-check:** the part's bbox L : H and the parts shot against the exploded cells.

### Minors (no change needed for a pass; note or fix while in there)

1. **f34 cut-top share** is .051 against .093 (camera e 12, a known §3.1 leftover). B1's notches will add a little.
2. **Diagonal views:** the bark is 28 levels dark from the studio sun's side, the side root tips stand higher (top
   profile ends .40/.49 against .13/.15), and the trunk is wider. This is the known §3.3 drawing conflict, and the
   hero governs.
3. **Underside** renders very dark (#3A261B against #684B3B) under the overhead studio light. The pale root-tip ends
   are tiny and read dark olive: decision 3 is technically there but barely visible. Optional: lengthen `TIP_PALE` to
   about 1.0.
4. **The `m020_stem` key** `#4C3810` is the dome's rendered value, not a calibrated key. The stub renders 19/14 levels
   darker than `#624921`; recalibrate it (one `K.calibrate` call).
5. **Stale `studs` property:** the hero says "9.0 x 8.5 x 4.4" and the Body "7.4 x 7.4 x 4.3", but the true heights are
   4.175 and 4.175 (set before the floor cut and polish). Rewrite it after `_polish`.
6. **The `cut_cu` and `root_cu` close-up cameras** are framed too wide or on the wrong junction: the cut face fills
   about 1/4 of the frame, and the root shot shows mostly the trunk side. Tighten them (`cut_cu` radius about 1.4
   centred on the cut face; `root_cu` on the right root at az about −30) so the next verifier can compare them with
   the close-ups.
7. **Clump positions in the top view:** FL and FR sit a little further out than the sheet's top (the hero governs,
   §3.5). Accepted.

### The modeller's departures, judged

- **Height 4.15 (measured 4.175):** accepted. It's inside decision 2's ±0.2, and the f34 W : H is 1.625 against 1.688.
- **Bigger clumps (span 2.2–2.7):** accepted for the size. The leaf share matches, but the leaf form is B2.
- **FL and FR moved 0.1 toward the axis:** accepted.
- **Front root height ×0.95, width ×1.15:** accepted. The f34 silhouette matches.
- **Floor key `bark`:** accepted. It's invisible from above; see minor 3.
- **`kit_shading_ok` on Body and hero:** accepted (justified above).
- **Root part as a "plain wedge":** not accepted (B3).
- **Clump "tulip-like":** not accepted (B2).

## Round 2 fixes (modeller)

Fresh modeller, 2026-10-28. Background Blender on port 9879 with `wip/M020.blend` (saved after every good build).
Everything is in `m020.py` (`build()`); shared helpers and m004/m011/m012/m016 untouched. The renders in this folder
are the round-2 renders.

### B1 trunk: fixed (flutes, lobed rim, notched stepped outline)

- `GROOVE` ((1.0, 0.38), (2.5, 0.32), (3.65, 0.26)), `GROOVE_OFF` 18°, the four diagonal crests +0.08 (`CREST_OUT`).
- **Trunk relief** (Body part, bark radius by azimuth, min / median / max): z 2.5 1.93 / 2.04 / 2.40; z 3.0 1.84 /
  1.96 / 2.20; z 3.5 1.78 / 1.91 / 2.14. Round 1 was 1.97–2.21 and 1.91–2.10, so the lobes now vary ±0.18 instead
  of ±0.06–0.10.
- **Notched outline:** `outline()` now has a stepped notch at 6 of the 8 groove azimuths (13, 79, 167, 253, 289 and
  337°). Each is 0.12–0.15 R deep, with a steep 4° jog on one side and a 12° slope on the other, so they read as the
  sheet's steps, not V cuts. 115° and 203° are left plain: notching all 8 at 0.12–0.18 made the top view a cog, against
  the sheet's roundish 13–14-gon (`z_top_c.png`). The outline loop is built on the notch azimuths (28 verts). The inner
  rim edge and the outline loop step down 0.04 at each notch.
- **Lobed rim:** the rim ring follows the outline azimuths, so it is notched too, and its outer edge dips `RIM_DIP`
  0.16 into each notch. The trunk's top ring is zipped to it. The 0.80 ring loop also carries a vertex on each notch,
  so no zip triangle can reach across a notch (the first attempt left 8–11 crossings there).
- **Re-check:** `f34_sheet` shows rim notches at f ≈ .55 (front-right, 289°) and ≈ .69 (right). 3–4 grooves read
  across the front, the centre one strongest. Bark lit quartile `#A97350` against `#B47B58` (Δ −11, −8, −8: within
  12; round 1 was −26, −17, −11).
- Silhouette unchanged: f34 W : H 1.625, top profile as round 1.

### B2 leaf clumps: fixed (flat star rosettes)

- `LEAF_PITCH` (24, 46). Leaves alternate between the lower and upper third of the range, so neighbours stack one
  above the other instead of crossing near-coplanar. Handle +2° (`LEAF_HANDLE`), `LEAF_SLOPE`
  (−18, −4), `FOLD` 0.14, `RIDGE` ((0.42, 0.075), (0.76, 0.035)), `LEAF_W` 0.70, roll ±12°.
  - **Departure on pitch:** the verifier suggested (15, 35). At (15, 35) the f34 leaf share fell to 10.6 % (sheet
    14.3 %) and the leaves read as flat grass from the e 12 camera. (24, 46) gives 13.5 % with the spans unchanged;
    the sheet's hero clumps fan up about 30–45°. The **LeafClump part** uses the flatter (15, 33)
    (`CLUMP_PART_PITCH`), matching the exploded cell's near-flat star.
  - FOLD 0.14 and ridge 0.075 (verifier: 0.12 and 0.05) give a little more crease, so each half takes its own shade.
- BL and BR normals tilted less ((∓0.2, 0.25, 1.0); was (∓0.35, 0.4, 0.85)). FR fan 240°, so no leaves point into the
  front root. Ground clumps slide 0.15 past first contact (`CLUMP_SINK_GROUND`).
- **Hub foot** stays `leaf_base`: no brown stalk above ground. **LeafClump part:** hub sink 0.06, stem 0.06. The
  visible stub below the lowest leaf is 0.033 of the 0.86 clump height (0.04; limit 0.1).
- **Two-tone leaves:** the near-flat leaves no longer turn a half away from the studio light. So each leaf's right
  half, in its own frame (the same side on every leaf whichever way it faces, so not colour by facing), reads
  `LEAF_HALF` 0.35 further toward the base. Keel undersides are now mid-green (`KEEL_TOWARD_BASE` 0; was 0.5 toward
  the base), so the f34, which sees them, isn't darker than the top view, which doesn't.
- **Re-check:**
  - leaf share f34 13.5 % (14.3 ± 4), front 13.4 % (14.8);
  - top leaf median `#499613` against `#3F8812` (Δ +10, +14, −1: within 15; round 1 +33, +56, +10);
  - top shade quartile `#2E690C` (round 1 `#408715`, sheet `#1B5110`): the dark halves show, though still lighter
    than the sheet's (the studio's top light is overhead);
  - exploded clumps `#53A718` against `#5EAB15` (round 1 was 40–50 levels dark).

### B3 Root part: fixed

- `root_part` starts at d 1.0 with the flat attach face. Its attach end is capped at the trunk-edge height
  (`PART_ROOT_CAP`, 2.1 falling to 2.0 at d 2.5), with a part-only hump `PART_HUMP` ±0.10 (hump, dip, bulge). The hero
  roots keep ±0.06, because their ridges were verified against the hero profile.
- Size 3.69 × 2.42 × 2.10: **L : H 1.76** (round 1: 1.2; target 1.6–2.0). 124 tris. It reads as a wedge in the parts
  shot and the exploded view.

### Minors

- **`m020_stem`:** `K.calibrate` re-run. The key `#4C3810` renders `#614926` on the dome against `#624921` (within 6),
  so it already was a calibrated key; the dark stub in round 1 was its shaded thin peg. The stub is now 0.04 of the
  clump height and barely visible.
- **`studs`** is rewritten from the final mesh after `_polish` (hero "9.0 x 8.5 x 4.2", Body "7.3 x 7.3 x 4.2").
- **Close-ups:**
  - `CUT_CU` (−15, 35), centred on the cut face, radius 1.45: the cut face fills the frame, rim notches and rings show;
  - `ROOT_CU` (0, 14) on the right root's junction, radius 1.6: trunk at the left, the root's ridge running out to the
    right, as in the sheet's close-up.
- **`TIP_PALE`** 1.0: the pale cut-wood root ends now read in `under_cu` (34 floor faces). Floor faces next to a leaf
  take `leaf_base` only when small (under 0.06): the long floor fans showed as green streaks underneath.
- The exploded clump and stem colours are fixed with B2.

### Self-intersections: a guarded local clean

The flat leaves lie close over each other and over the roots. The shared `m016._clean_mesh` then left 10–35
crossings: its BEAUTY triangulation of the booleans' bent n-gons split some straight through a neighbour, and a few
sliver collapses pushed faces through. `m020._clean_mesh` runs the same sequence with two local changes (no shared
file edited):
- `_tri_safe` fans each n-gon from the corner whose triangles cross nothing;
- `_desliver` gets a `movable` guard (`_crosses`) that refuses any move pushing a face through a non-neighbouring one.

Result: 0 self-intersections on every object.

### Stage 4 again (two passes)

- **Pass 1 (dome, `m020.calibrate()`, all keys):** bark `#6A4933`, bark_light `#7C553B`, bark_shadow `#584033`, cut
  `#B09368`, cut_light `#C3A880`, cut_ring `#C19969`, cut_pale `#C7B69A`, leaf `#4D8814`, leaf_tip `#679E15`,
  leaf_base `#366B11`, stem `#4C3810`.
- **Pass 2 (hero, linear factors):** bark ×1.18, bark_light ×1.75, bark_shadow ×1.0, leaves ×(0.9, 1.12, 1.0). The cut
  keys keep their round-1 pass-2 values, since the cut top barely changed. The bark light patches are broader and
  lighter (`patch_level` 0.15, `patch_mix` 0.75 on trunk and roots, placed by noise position); they carry the sheet's
  lit facets.

| Key | Final hex |
| --- | --- |
| m020_bark | `#734F38` |
| m020_bark_light | `#A06F4E` |
| m020_bark_shadow | `#584033` |
| m020_cut / cut_light / cut_ring / cut_pale | `#B09368` / `#C3A880` / `#C69A65` / `#C6AF8D` |
| m020_leaf / leaf_tip / leaf_base | `#498F14` / `#62A615` / `#337111` |
| m020_stem | `#4C3810` |

| Region | Sheet (median / lit / shade) | Ours |
| --- | --- | --- |
| Bark f34 | `#845942` / `#B47B58` / `#583D2C` | `#895C42` / `#A97350` / `#5D412E` |
| Bark front | `#8B5E44` / `#B37B5A` / `#5F4130` | `#885C42` / `#A97250` / `#5D402D` |
| Bark f34 by fifth (bottom → top) | `#704D3B #7E5743 #8F6146 #81563E #956144` | `#78543D #845B42 #8D6044 #885B40 #976748` |
| Body part / exploded body | `#855A3F` | `#8C5F44` (+7, +5, +5) |
| Root part / exploded root | `#8F6146` | `#926347` |
| Leaves f34 | `#428F14` / `#71BE13` / `#195A13` | `#408313` / `#63B71B` / `#224C07` |
| Leaves front | `#499213` | `#3E7D12` (−11, −21, −1) |
| Leaves top | `#3F8812` / `#78BE14` / `#1B5110` | `#499613` / `#62B617` / `#2E690C` |
| Exploded clumps | `#5EAB15` | `#53A718` |
| Cut f34 / front / top | `#FEDDAA` / `#FDDBA9` / `#F5C690` | `#FFD6A1` / `#FFD6A2` / `#FDD29A` (as round 1) |

- Facing correlation (`kit_baked_shading`): hero 0.35, Body 0.48 (waiver as round 1), Root 0.23, CutFace 0,
  LeafClump 0. `K.check` is clean.
- Colour leftovers:
  - the top-view bark median is `#93664A` against `#825740` (+17), from the overhead studio light on the root tops
    and the light patches;
  - the front cell's leaves are 21 levels short in G (the f34 governs);
  - the diagonal views are dark, as in round 1 (the studio sun is behind the az-45 camera).

### Checks (round-2 build)

| Object | Tris (budget) | Size | Shells | NM / boundary / wire / loose | N-gons / zero-area / dup | Min corner | Self-hits | UV overlap / flipped / min gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ChoppedHardwoodStump | 1808 (4000) | 8.97 × 8.47 × 4.17 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | 5.00° | 0 | 0 / 0 / 0.016 |
| …Body | 798 (1000) | 7.32 × 7.33 × 4.17 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | 5.26° | 0 | 0 / 0 / 0.016 |
| …CutFace | 210 (1000) | 3.62 × 3.55 × 0.58 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | 8.74° | 0 | 0 / 0 / 0.016 |
| …Root | 124 (1000) | 3.69 × 2.42 × 2.10 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | 11.14° | 0 | 0 / 0 / 0.016 |
| …LeafClump | 174 (1000) | 2.39 × 2.21 × 0.86 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | 5.79° | 0 | 0 / 0 / 0.016 |

- Normals are outward everywhere. Hero size against 9.0 × 8.5 × 4.3: −0.03 / −0.03 / −0.13 (unchanged, inside the
  tolerance).
- Views (sheet / ours): f34 W : H 1.688 / 1.625, shares L .143 / .135, W .093 / .048, B .764 / .817; front W : H
  1.574 / 1.691; r34 1.525 / 1.511; top W : D 1.045 / 1.063.
- Stages 5 and 6 are unchanged: no emission, no VFX.

### For the round-2 verifier

- Compare `f34_sheet`, `front_sheet`, `diag_sheet`, `diag34_sheet` and `top_sheet` with their cells; `cut_cu` and
  `root_cu` with the close-ups; `exploded` and `part_*` with the exploded cells. `m020.measure()` now also reports
  lit and shade quartiles (`Blit`, `Bshade`, `Llit`, `Lshade`).
- Departures to judge:
  - hero leaf pitch (24, 46), not (15, 35);
  - FOLD 0.14 and ridge 0.075;
  - 6 notches, not 8, 0.12–0.15 deep; RIM_DIP 0.16;
  - the painted darker right leaf half (`LEAF_HALF`);
  - the broader bark light patches;
  - the local guarded clean.
- Leftovers:
  - the f34 cut-top share is .048 against .093 (camera e 12, §3.1);
  - the BL clump and right root tip stand a little high in the f34 top profile (f .05/.10: .45/.53 against
    .37/.43; f .95: .60 against .46), as in round 1;
  - the light bark patches can read as flat blocks in the low kit `front` view.

## Stage 7 — Verification (round 2)

Independent verifier (not the round-1 verifier, no other stage), 2026-10-28. Read-only background Blender on port 9881
with `wip/M020_verify.blend` (not saved; `build()` not called). `kit_models.MODEL_RENDERS` was pointed at the
verifier's scratch folder before `m020.render_views()`, so nothing in this folder was overwritten. Everything below
was re-measured with the verifier's own bmesh / BVH / UV-raster scripts and `m020.measure()` on the fresh renders,
and every view was put side by side with its sheet crop at equal height.

**Result: PASS, 7/10.** All three round-1 blockers are fixed. The mesh is clean on every check. The model reads as the
sheet's stump: a fluted, flared trunk with a notched rim and a ringed cut top, four wedge roots in a +, and four leaf
star clumps in the notches. The leftovers below are minors. The first one (hard bark light patches) is the one worth
fixing if a modeller is free.

### Technical checks (all re-measured)

| Object | Tris (budget) | Size (studs) | Shells | NM / boundary / wire / loose | N-gons / zero-area / dup | Winding | Min corner (< 5°) | Self-hits | UV overlap px / flipped / outside |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ChoppedHardwoodStump | 1808 (4000) | 8.966 × 8.470 × 4.175 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | consistent, vol +77.9 | 5.00° (0) | 0 | 0 / 0 / 0 |
| …Body | 798 (1000) | 7.322 × 7.332 × 4.175 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | ok, +69.9 | 5.26° (0) | 0 | 0 / 0 / 0 |
| …CutFace | 210 (1000) | 3.617 × 3.545 × 0.585 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | ok, +5.27 | 8.74° (0) | 0 | 0 / 0 / 0 |
| …Root | 124 (1000) | 3.689 × 2.420 × 2.100 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | ok, +8.41 | 11.14° (0) | 0 | 0 / 0 / 0 |
| …LeafClump | 174 (1000) | 2.389 × 2.210 × 0.860 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | ok, +0.19 | 5.79° (0) | 0 | 0 / 0 / 0 |

- **Size** against the decided 9.0 × 8.5 × 4.3: W −0.034, D −0.030, H −0.125, all inside ±0.35 / ±0.35 / ±0.2.
- **Origin and transforms:** the local bbox centre is (0, 0) with min z 0 on every object. Rotation is 0, scale is 1.
  There are no modifiers, no custom normals and no children. All faces are flat-shaded.
- **Interior faces:** none. Every object is one closed manifold shell with 0 self-intersections.
  - A parity probe 2 mm off each face found 1 hero face (FL hub, `leaf_base`), and at 10 mm 4 more (FL/FR hubs, one
    bark face under a leaf). All are back-to-back leaf blades, or a leaf lying 0.4–4 mm over bark. They face each
    other and the faces are outward. These are contacts, not interior faces (minor 6).
- **UVs:** `UVMap` is on all objects, with 0 overlap pixels (1024 raster), 0 flipped, 0 outside, 0 zero-area. Texel
  density p5 / p95 is 0.99–1.01 of the median.
- **Materials:** Principled BSDF with a `Tint` multiply. The base colours equal the spec's final keys (`#734F38`,
  `#A06F4E` light / `#956748` at 75 %, `#584033`, cut `#B09368` / `#C3A880` / `#C69A65` / `#C6AF8D`, leaf `#498F14` /
  `#62A615` / `#337111`, stem `#4C3810`). Roughness is 0.8–0.95, metal 0, emission 0. `K.check` returns `[]`. Stored
  `kit_baked_shading` is hero 0.35, Body 0.48, Root 0.23, CutFace 0, LeafClump 0.
- **Waivers:**
  - The Body/hero `kit_shading_ok` (the cut-wood top grouped with bark by hue) is still justified.
  - The down-facing pale root-tip floor faces are decision 3.
  - **The painted darker leaf half (`LEAF_HALF`)** is accepted. It is chosen in each leaf's own frame (the same side
    on every leaf), so across a clump the dark halves face every direction. It does not colour by world facing: the
    leaf family reads 0 on the clump part. It gives the sheet's two-tone leaf read that flat leaves under an overhead
    light otherwise lose.
- **VFX / lighting:** no sockets and no emissive keys (decision 8).
- **Trunk relief** (bark radius from the trunk axis, 2° steps): z 2.5 1.93 / 2.04 / 2.40, z 3.0 1.84 / 1.96 / 2.20,
  z 3.5 1.78 / 1.91 / 2.14 (min / median / max). That is ±0.18 against round 1's ±0.06.
- **Cut-face outline:** measured radius by azimuth on the Body. There are 6 stepped notches at 12–16°, 80–84°, 168°,
  252–256°, 288–292° and 336–340°, each 0.20–0.26 stud deep (0.12–0.14 R). The flattened front-left sector is at
  232–248° (1.62–1.66).

### Round-1 items

| Item | Status | Evidence |
| --- | --- | --- |
| B1 trunk flutes, notched rim | **Fixed** | Lobes ±0.18. The f34 shows 3–4 dark vertical grooves across the front (the centre one strongest). Rim notches at the front-right and right. Bark lit quartile is −11 / −8 / −8 (round 1: −26 / −17 / −11). The sheet's lobes and rim scallops are still bolder (minor 5). |
| B2 leaf clumps | **Fixed** | Six broad kites per clump, low and fanned, with a lit and a dark half. They read as stars in the top, f34 and front. f34 leaf share .135 (sheet .143). No brown stalk on the ground. Top leaves +10 / +14 / +1 (round 1: +33 / +56 / +10). The part is a near-flat star with a 0.04-height stub. |
| B3 Root part | **Fixed** | 3.69 × 2.42 × 2.10, L : H 1.76 (target 1.6–2.0). In the parts shot it reads as a humped wedge with a tall attach end and a blunt tip. |
| m1 f34 cut share | Leftover (accepted, decision 9 camera) | .048 against .093 |
| m2 diagonal views | Leftover (accepted, §3.3) | bark −25 / −17 / −13, side tips higher |
| m3 underside | Fixed enough | Pale tips show at all four root ends in `under_cu`. The view is still dark under the overhead studio light. |
| m4 stem key | Fixed | Recalibration confirmed the key. The stub is now 0.04 of the clump height. |
| m5 `studs` | Fixed | Hero "9.0 x 8.5 x 4.2", Body "7.3 x 7.3 x 4.2" match the mesh. |
| m6 close-up cameras | Improved | `cut_cu` shows the ringed top, notches and rim. `root_cu` shows the right root's junction (still a little wide). |
| m7 top clump positions | Leftover (accepted, §3.5) | |

### The round-2 departures, judged

- **Hero leaf pitch (24, 46) instead of (15, 35):** accepted. The sheet's hero clumps do fan up about 30–45°, and the
  f34 leaf share holds (.135). The part uses (15, 33), which suits the exploded cell's flatter star.
- **FOLD 0.14, ridge 0.075:** accepted. The leaves read as broad kites with a crease, not V-gutters.
- **6 notches, not 8 (0.12–0.15 R, RIM_DIP 0.16):** accepted. The sheet's top view is a roundish 13–14-gon, not a cog.
  The f34 shows the front-right and right notches where the sheet has them. The notches read as sharp steps or cracks
  rather than the sheet's broad scalloped lobes (minor 5).
- **Painted darker leaf half:** accepted (see Waivers).
- **Broader bark light patches:** accepted in the sheet views, but see minor 1.
- **Guarded local clean (`_tri_safe`, `_desliver` guard):** accepted. It leaves 0 self-hits and 0 slivers under 5°.
  No shared file was touched.

### Views against the sheet (fresh renders, `m020.measure()`)

| View (camera) | W : H sheet / ours | L / W / B shares, sheet → ours |
| --- | --- | --- |
| f34 (f34_sheet 0,12) | 1.688 / 1.625 | .143/.093/.764 → .135/.048/.817 |
| front (front_sheet 0,10) | 1.574 / 1.691 | .148/.052/.800 → .134/.038/.828 |
| side (diag_sheet 45,8) | 1.476 / 1.614 | .120/.032/.847 → .135/.027/.838 |
| r34 (diag34_sheet 45,12) | 1.525 / 1.511 | .093/.051/.856 → .136/.051/.812 |
| top (top_sheet 0,89) | 1.045 / 1.063 | .197/.307/.496 → .257/.279/.464 |

- **f34 top profile** (sheet → ours): f .05 .37 → .45, f .10 .43 → .53 (BL clump high and far left); f .20 .59 → .52,
  f .85 .71 → .62 (the BR clump sits lower and reads darker than the sheet's bright raised star); f .95 .46 → .60
  (right root tip high). Everything else is within ±0.07.
- **Trunk and cut top:** the fluted trunk and notched rim read in f34, front and top. The rings show in the right order
  (darker pith, light, darker ring, light, palest outer) in `top_sheet` and `cut_cu`. They are softer than the sheet's
  close-up but visible.
- **Roots:** a + in the top view, the back root shortest and the front widest. They are wedges with ridges falling to
  blunt tips. The junction is one plane with no seam.
- **Clumps:** 4 in the f34 and front, 3 in the diagonals (centre lowest, right biggest), 4 in the notches in the top.

### Colours (Δ = ours − sheet, per channel; median / lit quartile / shade quartile)

| Region | Sheet | Ours | Δ |
| --- | --- | --- | --- |
| Bark f34 | `#845942` / `#B47B58` / `#583D2C` | `#895C42` / `#A97350` / `#5D412E` | +5,+3,0 / −11,−8,−8 / +5,+4,+2 |
| Bark front | `#8B5E44` / `#B37B5A` | `#885C42` / `#A97250` | −3,−2,−2 / −10,−9,−10 |
| Bark f34 by fifth (bottom → top) | `#704D3B #7E5743 #8F6146 #81563E #956144` | `#78543D #845B42 #8D6044 #885B40 #976748` | +8,+7,+2 / +6,+4,−1 / −2,−1,−2 / +7,+5,+2 / +2,+6,+4; darkest at the bottom |
| Bark top | `#825740` | `#93664A` | +17,+15,+10 (overhead studio light on the root tops) |
| Bark side / r34 | `#885C43` / `#865A41` | `#6F4B36` / `#6F4C37` | −25,−17,−13 / −23,−14,−10 (studio sun behind the az-45 camera) |
| Cut f34 / front / top / side | `#FEDDAA` / `#FDDBA9` / `#F5C690` / `#FDD9A5` | `#FFD6A1` / `#FFD6A2` / `#FDD29A` / `#FED29E` | +1,−7,−9 / +2,−5,−7 / +8,+12,+10 / +1,−7,−7 |
| Cut shade f34 | `#FCC887` | `#FFC788` | +3,−1,+1 |
| Leaves f34 | `#428F14` / `#71BE13` / `#195A13` | `#408313` / `#63B71B` / `#224C07` | −2,−12,−1 / −14,−7,+8 / +9,−14,−12 |
| Leaves front | `#499213` | `#3E7D12` | −11,−21,−1 |
| Leaves top | `#3F8812` / shade `#1B5110` | `#499613` / `#2E690C` | +10,+14,+1 / +19,+24,−4 |
| Leaves side / r34 | `#468F12` / `#3E8813` | `#315F0D` / `#37700F` | −21,−48,−5 / −7,−24,−4 (studio side) |

The sheet-facing medians (f34, front, cut, bark gradient) are within about 12. The large deltas are the known
studio-lighting cases (top bark, diagonal views).

### Minors (none blocking; cheap fixes given)

1. **Bark light patches have hard edges.** On the hero, 80 edges go straight from `bark` to `bark_x_light_75`, and 8
   from `light_75` to `shadow_50`. There is no 50 % step. Together with the ring-band face layout, this shows as flat
   rectangular light slabs on the back of the trunk in the kit `rear` and `rear34` views, and as a zig-zag sawtooth on
   the Root part. STAGES stage 4 says "avoid hard random patches", and the sheet shows none from any side.
   - **Fix (`m020.py`):** in the trunk and root painters, give each patch a one-face rim. Bark faces next to a
     `light_75` face become `bark_x_light_50` (or `_25`). Alternatively, lower `patch_mix` to 0.5 and keep
     `patch_level`. Then re-check that the f34 bark lit quartile stays within 12 of `#B47B58`.
2. **f34 clump heights.** The BL clump stands high and far left (+.08 / +.10), and the BR clump low (−.07 / −.09) and
   in the trunk's shade. The sheet's BR clump is a bright star raised on the right root. The right root tip is +.14
   high.
   - **Fix (optional):** raise the BR hub about 0.3 along the root flank and lower BL about 0.2.
3. **Top-view leaf share** is .257 against .197 (+6, outside ±4). The flatter round-2 leaves spread wider from above.
   The hero governs; accepted.
4. **f34 cut share** is .048 against .093 (the camera is e 12 by decision 9; the e 15 shot opens it a little).
5. **Rim notches** read as sharp cracks or teeth rather than the sheet's broad scalloped lobes. The sheet's trunk lobes
   also bulge more. This is acceptable for a pass.
6. **Leaf contacts:** a few back-to-back leaf blades at the FL/FR hubs lie 0.4–4 mm apart. They don't intersect and
   are invisible at play distance.
7. **Diagonal views and underside** are dark (studio light, as in round 1). Front-cell leaves are 21 levels short in
   G.
8. **Presentation only:** in the exploded shot, the front root copy overlaps the body. A fresh session that renders
   without `build()` (CLUMP_INFO empty) floats two clumps high. Neither affects the export.

Not blocking for the main session. Stages 5 and 6 (no light, no VFX) stand. Studio validation of cut-face clipping and
the gradients is still "Requires Manual Validation".

## Main session after verification round 2 (2026-10-28)

Applied minor 1: `_patch()` gives the bark light patches a 50 % then 25 % edge ring (`PATCH_RAMP` 0.08 of noise), on the trunk and the roots. Hard `bark` → `bark_x_light_75` edges on the hero went from 80 to 14. The rebuild in the kit file gave a hero of 1808 tris, one shell, 0 non-manifold, `problems` empty, `K.check` clean. Export: 5 assets, 0 problems. From the back the patches still read as faint slabs, because the trunk faces there are large; that is left for a polish pass.
