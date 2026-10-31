# 029 Ancient Root — spec

Reference: `art/blender/assets/references/029.png`. The sheet's own title is "32 / 132 — ANCIENT ROOT", subtitle
"FLINTBORN — INDIVIDUAL MODEL STUDY", top right "STYLIZED-CONCEPT GAME ASSET REFERENCE", footer "FLINTBORN — INDIVIDUAL
MODEL STUDY, PAGE 32/132". INDEX.md row 29 calls it "Ancient root model study". The image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m029.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`
(one modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7).

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7).

Sheet text:
- **Cells:** Front Three-Quarter, Rear Three-Quarter, Front, Side (Right), Rear, Top, Exploded Construction, three
  close-ups, Material Palette, Modeling Notes.
- **Modeling notes:**
  1. "Modular parts: two root halves, sapstone, leaf clumps, rocks, and base."
  2. "Clean low-poly shapes with broad, flat faces. Keep forms chunky and readable."
  3. "Simple solid colors, no textures or noise. Match FLINTBORN low-poly primitive style." (but see §3.8)
  4. "Parts designed to interlock with flat joining surfaces for clean assembly."
  5. "Maintain consistent silhouette and proportions across all views."
- **Palette** (labelled): Root Wood, Rock (Primary), Rock (Secondary), Sapstone (Green), Leaf Foliage (§5.1).
- **Exploded labels:** Root Half (Left), Root Half (Right), Green Sapstone, Leaf Clump (two drawn), Rocks (Side), Base.
- **Close-ups:** "Close-Up: Root Junction" with "Faceted Root Surface" and "Leaf Inset Between Roots"; "Close-Up: Base &
  Joining" with "Rocks Support Root Ends" and "Flat Joining Surfaces"; "Underside View" with "Flat Base (For
  Placement)".
- **Game context:** `src` has no node id for it. The old **R08** kit sheet has `AncientRoot` (10.06 W × 7.89 D × 6.69 H,
  1229 tris, "massive twisting root arch over a large green sapstone mineral nodule on a dark soil mound ringed with
  chunky rocks", one `ore_glint` on the sapstone) with parts `AncientRootBase`, `AncientRootHalfLeft`,
  `AncientRootHalfRight`, `AncientRootLeafClump`, `AncientRootMineralNodule` (2.83 × 2.39 × 3.75), a depleted
  `AncientRootDepleted` and the drop `GreenSapstone`. MODEL_PROGRESS row R08 calls that build a "blocky plank arch
  (ref twisting roots); smooth egg sapstone". It owns every `AncientRoot*` name (§8).
- **Design doc:** WorldModeling §11 table, row "Emberbloom / Frost Shrub / Mooncap / Ancient Root": "Keep event inserts
  separate: … mineral nodule. Reuse the common plant grammar. Effects, if later requested, must not conceal the
  geometry during approval." §12 (resources): "The depleted state usually retains the host or base and removes the
  harvestable inserts." Both feed decisions §8.6 and §8.8.

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is
`#F3EDE5` (243, 237, 229). The masks are `cls()` in `m_cls.py` (HSV):
- **background:** max channel difference from the paper < 16, **or** sat < 0.10 with v ≥ 0.78. The second rule
  takes the soft grey ground shadow out, so silhouettes and shares never include the shadow (lesson from 020/021).
- **L, leaves:** green family (hue 48–160°, sat ≥ 0.22, g > 45) with hue < 80° or sat ≥ 0.70. The foliage is a
  vivid yellow-green (hue 66–72°, sat 0.85–0.96).
- **S, sapstone:** the rest of the green family: a soft mid green (hue 93–106°, sat 0.42–0.53).
- **R, root wood:** hue 12–36°, sat ≥ 0.40, v ≥ 0.25.
- **K, stone:** base + rocks: hue ≤ 45° or ≥ 300° (or sat < 0.12), v 0.14–0.80. Base and rocks share one colour
  family, so the masks can't split them; "K grey" (sat < 0.22) is reported as a sub-share (the greyer lit rock
  faces), and the rocks are sampled with tight boxes (§5.2).
- **O, other:** dark contact lines and edges; 1.6–3.0 % of the silhouette; not counted in the shares.

**Scratch study material** (pure Python, Pillow + numpy; no Blender), in
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m029_study\`.
Run from that folder with
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\venv22\Scripts\python.exe`.
- **Helpers:** `m.py` (loader, HSV, view boxes `V`, `crop`), `m_cls.py` (masks, preview colours), `measure_lib.py`
  (components), `bb.json` (silhouette boxes).
- **Measurements:** `measure.py` → `measure_out.txt` (bbox, shares, top / root-only top / bottom profiles, width per
  height, root runs per height, leaf and sapstone components); `expl.py` (exploded parts, root widths along their
  axes); `runs.py` (root widths perpendicular to the hero legs, crest thickness); `egg.py` (sapstone width profile and
  bands, leaf hub → tip bands); `holes.py` (see-through gaps).
- **Layout fitting:** `proxy.py` + `layout2.json` (point-splat proxy of §2, orthographic projection into any
  camera: W : H, shares, egg position, profiles). Crude (flat kite leaves, sparse splats), so use it for positions and
  W : H only.
- **Colour:** `samp.py` → `samp_out.txt` (swatches, per-view medians and quartiles, deciles, height bands, exploded
  parts, close-ups); `samp2.py` (individual rocks, base floor, underside).
- **Crops** (2×): `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `row.png` (the four small
  views), `expl.png`, `cu_junc.png`, `cu_base.png`, `cu_under.png`, `pal.png`, `notes.png`; mask previews `cls_*.png`,
  `cls_hero.png`, `cls_row.png`; proxy renders `px_*.png`, `px_cmp.png`.
- **Zooms** (3–4×): `z_f34_crown.png`, `z_f34_left.png`, `z_f34_right.png`, `z_r34_crown.png`, `z_top_crown.png`,
  `z_rear_crown.png`.
- **To run the scripts on our renders,** point `R` (in `m.py`) at the render, set `P` to its background colour, set
  `V` to the render's cell box and re-run `measure.py` (it rewrites `bb.json`).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a resource node / world prop). Hero budget 4000 tris, each part under 1000. The plan
  in §4.3 lands at about 2500–3100.
- **Overall read (check this first).** A **flat, round, faceted stone base** ringed by chunky grey-mauve **boulders**,
  a big **faceted green egg (the sapstone)** standing on the base just right of centre, and **two thick, twisting,
  warm-orange root halves arching over it**:
  - **Root L** rises from a **massive buttress foot at the front-left** (a thick column plus a spur that runs out to
    the left along the ground), climbs over the egg, crests above it and **ends in a blunt, club-like end that hangs
    down at the upper right**, resting on Root R's shoulder.
  - **Root R** starts as a **blunt end standing up behind the crest at the back-left** (the "hump" over Root L's
    crest in the hero), runs right behind L's crest and over the egg's back-top, and descends the right side to a
    blunt foot at the front-right.
  - **Two upright leaf fans** grow from behind the two legs (left: 5 leaves, right: 4), spreading outward and up like
    hands of cards. They are not flat rosettes and not cups.
  - It must read as **one gnarled root arch protecting a gem**, not two bent pipes, and the base must read as **one
    low flat slab** with distinct boulders on its rim, not a rock pile (lesson from 021).
  - Hero shares (f34): root 46 %, stone (base + rocks) 24 %, leaves 15 %, sapstone 15 %.
- **Focal silhouettes, in order:**
  1. The arch: L's thick leg on the left, the crest across the top (flat-topped, h .96–.99 for f .40–.75), R's thinner
     leg falling to the right.
  2. The egg framed by the arch: W : H 0.81, widest just below its middle.
  3. The two leaf fans flaring out on both sides, and the boulder ring along the bottom.
- **Target size: about 9.9 W × 7.6 D × 6.2 H studs** (H = 1.13 of the 5.5-stud character: the crest clears a
  player's head; tolerances W ±0.4, D ±0.4, H ±0.25). Sapstone 2.65 W × 2.45 D × 3.45 H (0.63 C, waist-to-chest
  high). Root L Ø 2.5 at the foot → 1.9 mid-leg → 1.55 on the crest → 1.45 club end; Root R Ø 1.45 top end → 1.2 body
  → 0.85 foot. Leaves 2.2–2.9 long. Decision §8.1.
  - **How it was derived.** The sheet has no character. The f34 is fitted at **49.5 px per stud** (az 0, e 13, §3.1):
    - the egg is drawn at the same size in the hero (132 × 167 px) and the exploded view (137 × 169 px), so it is
      the most reliable internal anchor; at 49.5 px/stud it is 2.65 × 3.45, within 7 % of R08's
      `AncientRootMineralNodule` (2.83 × 3.75) and the R08 hero's width (10.06);
    - the fitted layout (§2, `proxy.py`) then gives W 9.9–10.3 (leaf tips), H 6.26 and puts the egg at (.599, .397)
      in the f34 against the sheet's (.596, .420).
  - **Why this size.** "Ancient" plus a resource the player walks up to: the arch should stand over the player
    (1.1 C) while the egg stays reachable at chest height. It sits between its neighbours: M021 Root Cluster
    9.4 × 7.7 × 5.0 (roots Ø 1.0–1.3), R08 `AncientRoot` 10.06 × 7.89 × 6.69. The roots are clearly thicker than
    021's (Ø 1.2–2.5), which is the "ancient" read.
- **Build frame:** front −Y, +X right, ground z 0, origin = the base's plan centre. The egg sits at X +1.0, so the
  composition is asymmetric on purpose; stage 2 re-centres to the bbox bottom centre.

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | Leaves L | Sapstone S | Root R | Stone K (grey sub-share) |
| --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (15,120,551,490) | 38–527 × 131–463 (490 × 333) | **1.471** | 15.2 % | 15.1 % | 46.1 % | 23.7 % (6.1) |
| Rear three-quarter (554,120,1008,490) | 568–987 × 140–463 (420 × 324) | 1.296 | 19.5 % | 11.5 % | 45.6 % | 23.4 % (5.2) |
| Front (15,525,287,741) | 31–276 × 554–719 (246 × 166) | 1.482 | 14.9 % | 17.9 % | 42.7 % | 24.5 % (5.9) |
| Side (Right) (291,525,516,741) | 302–501 × 553–724 (200 × 172) | 1.163 | 21.0 % | 13.0 % | 48.8 % | 17.2 % (3.9) |
| Rear (519,525,761,741) | 529–751 × 554–720 (223 × 167) | 1.335 | 22.3 % | 12.3 % | 36.5 % | 28.9 % (5.5) |
| Top (764,525,1008,741) | 776–994 × 531–722 (219 × 192) | 1.141 | 18.1 % | 13.3 % | 40.1 % | 28.5 % (7.6) |

- **The "Front" cell is the f34 drawing again** at 0.5 scale: W : H 1.482 against 1.471, the same profiles within
  0.05, the same clumps (.149/.549 against .161/.546; .863/.522 against .866/.555); only the egg is drawn 0.06 W
  further left (.539 against .596).
- **Verifier tolerance:** shares ±4 points (S ±3); positions ±0.06 of W/H unless stated.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .36 | .46 | .64 | .63 | .79 | .80 | .77 | .87 | .96 | .99 | .99 | .96 | .97 | .96 | .94 | .85 | .77 | .61 | .63 | .47 | .40 |
| r34 | .32 | .45 | .67 | .66 | .76 | .78 | .88 | .96 | .98 | .99 | .98 | .95 | .96 | .96 | .93 | .86 | .72 | .69 | .70 | .53 | .50 |
| Front | .36 | .47 | .67 | .65 | .78 | .80 | .78 | .88 | .96 | .99 | .99 | .98 | .98 | .95 | .88 | .69 | .76 | .62 | .64 | .45 | .36 |
| Side | .47 | .48 | .64 | .65 | .61 | .78 | .85 | .92 | .98 | 1.0 | 1.0 | .99 | .99 | .98 | .96 | .85 | .71 | .65 | .59 | .60 | .30 |
| Rear | .36 | .60 | .69 | .67 | .82 | .87 | .91 | .95 | .94 | .93 | .92 | .99 | .99 | .96 | .92 | .90 | .82 | .69 | .70 | .45 | .37 |
| Top | .40 | .73 | .73 | .71 | .82 | .87 | .92 | .97 | .99 | .99 | .95 | .97 | .97 | .93 | .96 | .98 | .91 | .90 | .79 | .69 | .68 |

The f34's ends (.36 / .40) are the lowest leaf tips; f .10–.30 (.63–.80) is the left fan; f .40–.75 the flat crest;
f .80–.95 the right fan over R's leg.

**Root-only top line** (leaves excluded; 0 = no root wood in that column):

```
f34   .00 .12 .25 .37 .43 .53 .77 .87 .96 .98 .99 .96 .97 .96 .94 .84 .59 .47 .41 .30 .00
front .00 .21 .33 .41 .49 .62 .78 .87 .96 .99 .98 .97 .98 .94 .88 .63 .53 .41 .34 .19 .00
r34   .00 .26 .34 .41 .48 .59 .88 .95 .98 .99 .98 .94 .96 .95 .93 .85 .71 .58 .47 .38 .00
side  .00 .00 .00 .33 .53 .78 .84 .91 .97 1.0 .99 .99 .99 .97 .95 .85 .70 .61 .46 .35 .29
rear  .00 .19 .39 .40 .81 .86 .90 .94 .93 .93 .91 .98 .98 .96 .91 .67 .58 .46 .41 .29 .00
top   .00 .34 .41 .45 .50 .61 .70 .84 .92 .94 .93 .86 .87 .87 .84 .81 .61 .52 .70 .35 .00
```

In the f34 the root line climbs steadily from L's spur toe (.12 at f .05) to the crest (.96–.99 at f .40–.70), then
falls along R to .30 at f .95: an asymmetric arch, steeper on the right.

**Bottom profiles** (lowest silhouette pixel per column; the base outline): f34 `.34 .10 .08 .05 .02 .01 .00 .01 .01
.01 .01 .01 .02 .02 .02 .03 .05 .06 .09 .11 .39` (the base ellipse rises 0.08–0.11 H toward the sides: e ≈ 12–15°);
front `.09 .07 .04 .02 …` (flatter, e ≈ 8–10°); side, rear and top near-flat in the middle, rising 0.10–0.21 at the
ends (top .37/.26/.14 on the left: a high camera).

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .05@.28 .88@.05 .96@.02 .89@.06 .98@.02 .82@.09 .87@.07 .66@.18 .55@.21 .37@.36 .02@.47
r34    .17@.41 .80@.08 .96@.03 .97@.01 .94@.04 .89@.11 .84@.08 .72@.18 .56@.22 .42@.31 .03@.45
front  .39@.31 .99@.00 .95@.02 .90@.06 .96@.02 .82@.10 .85@.09 .64@.18 .52@.21 .33@.36 .04@.45
side   .41@.33 .92@.03 .98@.02 .93@.07 .95@.01 .87@.10 .85@.10 .57@.23 .51@.27 .39@.34 .17@.43
rear   .33@.32 1.00@.00 .96@.02 .92@.03 .96@.02 .83@.08 .88@.05 .87@.06 .61@.19 .49@.28 .04@.56
top    .11@.44 .69@.14 .84@.11 .91@.04 .96@.00 .92@.03 .92@.07 .88@.05 .65@.20 .57@.29 .04@.41
```

**Root runs per height** (f34; root-wood runs across the row, as f from–to): the two legs and where they merge.

```
h .2  L-spur .07-.19 | L-column .33-.44 (between rocks) | R-foot .89-.98
h .3  L .12-.46 (foot + spur flare, 167 px)  | R .81-.94 (64 px)
h .4  L .18-.47                              | R .76-.91
h .5  L .24-.46 (108 px)                     | R .72-.83 (54 px; its left edge hidden by the egg)
h .6  L .27-.49                              | R .70-.79
h .7  L .30-.56 (+ the back hump)            | .58-.64 (R's shoulder under the crest) | R .68-.75
h .8  crest .33-.76 (one run)
h .9  crest .37-.73
```

**Components** (`measure.py`): centre (f, h); extent; size in px.

| View | Leaf clumps | Sapstone |
| --- | --- | --- |
| f34 | left .161, .546 (f .00–.30, h .31–.83, 147 × 173); right .866, .555 (f .71–1.00, h .34–.78, 143 × 147) | .596, .420 (f .47–.73, h .18–.68, 132 × 167) |
| r34 | left .159, .560 (f .00–.30, h .28–.81); **inner .420, .257 (f .24–.60, h .10–.39, 152 × 96, in front of the egg's lower left)**; right .905, .556 (f .82–1.00, h .39–.72) | .638, .458 (f .51–.76, h .21–.69) |
| front | left .149, .549; right .863, .522 | .539, .409 (f .39–.69, h .16–.68) |
| side | left .114, .472 (h .30–.67); **front-low .309, .204 (f .14–.51, h .03–.42)**; right .914, .511 (small) | .634, .470 (f .49–.77, h .21–.70) |
| rear | left .211, .467 (f .00–.40, h .23–.70, the biggest); right .828, .637 (f .65–1.00, h .31–.90) | .466, .394 (f .34–.60) |
| top | left .146, .605; back-right .763, .866; right .880, .651 | .567, .400 (f .42–.72, h .20–.62) |

**See-through gap** (`holes.py`): only one, in the f34 (and the front cell): **f .63–.70, h .67–.73** (34 × 23 px,
≈ 0.7 × 0.45 stud), framed by L's crest above, L's hanging club end to the right and R's shoulder below and left.
Nice to have (§3.11).

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, governs; `f34.png`, `cls_f34.png`, zooms).** The fit (§2, `proxy.py`) puts the camera
**straight in front (az ≈ 0) at e ≈ 13°**, not at a three-quarter azimuth (§3.1).
- **Root L:** the dominant mass. Its **foot** is a broad buttress at the front-left: a thick column that drops behind
  the big front-left boulder (sheet (117–212, 370–462)) and a **spur** running out left along the ground to a blunt
  toe at the far left (f .06–.15, h .02–.20). There is a deep V-notch between column and spur. The leg climbs right
  at about 60° (perpendicular Ø ≈ 95–110 px = 1.9–2.2 studs at h .5; 167 px across with the spur at h .3), bends over
  at the crest (vertical thickness 68–98 px = 1.4–2.0; top flat at h .96–.99), and **ends in a blunt club that hangs
  down at the upper right** (sheet x 370–410, y 202–238; X ≈ +1.8…+2.6), resting on R's shoulder.
- **Root R:** its **top end** is the rounded hump that shows **behind L's crest at the upper left** (sheet
  (183–303, 132–218): it stands slightly higher than L's crest at f .40–.45). It passes behind L, shows again as a
  dark band **under L's crest, over the egg's top** (sheet (320–357, 218–245)), then descends the right side
  (perpendicular Ø ≈ 45–60 px, partly hidden by the egg; 64 px across at h .3) to a **blunt foot** at the front-right
  edge (f .89–.98, h .02–.20) with a boulder in front of it.
- **Bark relief (`z_f34_left.png`, `z_f34_right.png`, `cu_junc.png`):** long facets run **along** each limb, 3–4
  across the visible width, separated by **real creases**: a dark V-groove, then a lit ridge. On L's leg, 2–3 such
  creases are visible at once; R's leg has one sharp lit ridge along its top. Facets are 0.5–1.0 stud wide and
  1.0–2.0 long. There are knots and bulges, no smooth tube anywhere (lesson from 020's "smooth cone").
- **Sapstone:** a faceted egg (geodesic triangles; 5- and 6-valent vertices), standing on the base floor (bottom at
  h .18, i.e. on the base top). About 20–26 triangles show on the near side. Light from the upper left: pale facets
  top-right `#C4E986`, deep green bottom `#446634`.
- **Leaf fans:** left 5 leaves, from nearly horizontal (tip pointing left and a little down) to nearly vertical, like
  a hand of cards spread up and left from behind L's leg; right 4 leaves spread up and right from behind R's leg.
  Each leaf is a **thick faceted kite**: a ridge down its middle, a lit half and a dark half, W : L ≈ 0.45, the
  widest point at about 0.4 L, a sharp tip.
- **Base and rocks:** the base front edge is a low faceted slab (0.3–0.45 stud face). Between the boulders its flat,
  slightly undulating top reads as **one continuous floor** in front of the egg (sheet (255–430, 400–465)). Six
  boulders show: far-left (by L's toe, in shade), big front-left (in front of L's column), front-mid, small centre
  (in front of the egg's lower left), right-mid (right of the egg's foot), right (in front of R's foot).

**Rear three-quarter (`r34.png`).** The hero again, from the **front-left** (§3.2): L's foot and spur at the left, the
egg right of centre, R's hump behind the crest at the top-left, R falling to the right. Two differences: more
boulders in the front ring (8–9 visible), and an **inner leaf fan** of 3 broad leaves in front of the egg's lower
left (f .24–.60, h .10–.39) that no front view shows.

**Side (Right) (`side.png`).** A narrow redraw (W : H 1.163) of the same arch: a broad leg on the left rising to a
crest at the centre-left, a thinner leg falling to the right, the egg in the opening, the "inner" fan big at the
bottom-left. From +X the layout can't show an arch (L is seen end-on); see §3.3.

**Rear (`rear.png`, `z_rear_crown.png`).** The arch mirrored: the **hanging club end is at screen left** and the long
leg falls to screen right, with R's hump sticking up behind at the top centre-right. From behind (az 180), screen left
is +X, so this agrees with the layout: L's club end is at +X (§3.4). The leaf fan at the left (the biggest leaf
component) is the right (+X) fan seen from behind.

**Top (`top.png`, `z_top_crown.png`).** Not a plan view: a high front view (e ≈ 45–50°, perspective; §3.5). L climbs
from the front-left foot to the crest and over to its club end; R's hump stands at the back-left with two dark
boulders behind it; R's descent shows below L's club end; boulders ring the front and back; fans left and right
(the right fan reaches round to the back-right).

**Close-ups.**
- **Root Junction** (648,780,1009,1025): L's crest and club end from the front-right; the label "Faceted Root
  Surface" sits on a broad crease-bounded facet; "Leaf Inset Between Roots" points at the right fan's leaves where
  they come out between the club end and R; more leaves sit in the opening under the arch (the r34's inner fan).
- **Base & Joining** (648,1055,1009,1262): the base slab's front edge (0.3–0.5 face, broad facets), boulders on the
  rim against the root feet ("Rocks Support Root Ends"); "Flat Joining Surfaces" points at the flat top where a
  boulder and a foot sit on the slab.
- **Underside View** (648,1300,1009,1497): a **flat oval base** `#7B6558` (flat-shaded, one plane); the rim is lumpy:
  fused rim lumps bulge 0.2–0.4 past the slab edge at the left and back. Drawn obliquely, about 1.6 : 1.

### 1.4 Parts (Exploded Construction (15,752,645,1249), `expl.png`)

Scale: the exploded egg (137 × 169 px) equals the hero's (132 × 167), so the exploded is drawn at the hero's scale
(49.5 px/stud). The roots and fans, however, are drawn **smaller** than in the hero (§3.6). The hero governs.
Facet language everywhere: broad flat-shaded facets, irregular triangles, no smoothing.

#### Base: (202,1105,486,1234), 285 × 130 px (`expl.png` bottom)

- **What it is:** a low round slab with a **flat inner floor** and a **rim of low fused lumps** (front-left, front,
  front-right, right, back-right). The rim lumps are part of the slab: wide (1.2–1.8), low (0.25–0.45 proud of the
  floor), merging into each other with shallow creases. It reads as **one object**.
- **Size (hero):** plan **8.6 × 6.8** (an irregular 14-gon, radius ±6 % by broad sectors), floor top z 0.35 (±0.06
  broad undulation, facets 0.8–1.5 across), rim top z 0.6–0.8, flat underside at z 0.
- **Construction:** `_base(seed)`:
  - a lofted slab: 14-gon footprint, rings at z 0 (outer, flat bottom), 0.25 (outer, slight bulge +3 %), rim top 0.45
    (0.92 R), floor edge 0.38 (0.80 R), floor centre fan; vertex jitter ±0.04;
  - 7 rim lumps (`K.hull_rock`, 5–6-sided footprints, 2 rings, quiet tops), sunk 55–65 % into the slab edge so only a
    low shoulder shows (table §2.1), one exact union; the floor stays clear in front of the egg;
  - flat underside, floor-cut at z 0.
- **Triangles:** slab about 120 + 7 lumps × 40 → **about 400** after the union (limit 1000).

#### Rocks (Side) and boulders: exploded (133,1115,207,1177) 75 × 63, (200,1078,266,1130) 67 × 53, (414,1074,534,1145) 121 × 72 (3 rocks)

- **What they are:** chunky boulders (WorldModeling §12.1): 5–7-sided footprints, 2–3 height rings, a few big side
  facets, a quieter top, height 0.65–0.85 of width. Lit tops lighter and greyer (Rock (Secondary)).
- **Sizes:** 0.95–1.9 across, 0.7–1.45 high (§2.1, 9 in the hero). The exploded draws 6 (2 + 1 at the left, 3 at the
  right).
- **Construction:** `_rock(w, h, seed)` = `K.hull_rock`; 40–60 tris each; each sunk 0.1–0.2 into the base (or the
  ground at the rim) and touching its neighbours or a root foot where the sheet shows contact.
- **Triangles:** 9 × 50 ≈ **450**.

#### Green Sapstone: (270,895,406,1063), 137 × 169 px

- **Shape:** a faceted **egg**, W : H **0.81**; width profile (fraction of max width at h = 0, .1 … 1.0):
  `.04 .61 .83 .91 .96 .97 .89 .80 .69 .39 .02` (widest at h .4–.5; the top narrower and slightly pointed, the
  bottom rounder). Geodesic facets: an **icosphere subdivision 1** (80 tris, 42 verts) is the sheet's density (about
  20–26 visible triangles, 10–12 silhouette corners).
- **Size (hero):** **2.65 W × 2.45 D × 3.45 H**; bottom at z 0.30 (sunk 0.05 into the floor, or seated on a small flat
  5-gon bottom face; §8.6).
- **Construction:** `_sapstone(seed)`: `ico(subdiv=1)` scaled to the size above; egg warp: radius × (1 − 0.22 t) for
  t = height above the equator / half-height (top narrower); equator at 0.45 H; vertex jitter ±0.04; flatten the
  lowest vertex ring onto a small seat face. No subdivision; no smoothing.
- **Triangles:** **80–90**.

#### Root Half (Left): (142,793,342,985), 201 × 193 px

- **Shape:** a thick bent limb: one end a fat blunt foot (lower left), the other a fat blunt club (upper right).
  Widths along its axis (5 → 95 %): `49 74 81 62 58 64 70 81 79 65` px: a **dog-bone** with bulges at about 20 % and
  80 % and a narrower middle (0.75 of the ends). Axis length 243 px (≈ 6.3 studs as drawn).
- **In the hero** it is longer and much thicker (§3.6): about **8.6 studs** along its centreline plus a 1.7-stud
  spur, Ø 2.5 → 1.45 (table §2.2).
- **Section:** a **10-sided** tube; ring radius ±8 % by broad sectors, ±10° twist per ring; the foot section is an
  ellipse 1.25 : 1 (wider along X).
- **Relief (lesson from 020, measurable):** along every leg, **3 longitudinal creases** (V-grooves) **0.12–0.18 stud
  deep** (about 0.08 Ø; pull one vertex column in, or two adjacent columns for a wider groove), with ridges between
  them; **2 knots** per limb (+12–18 % radius over 0.6–0.9 of length, at s ≈ 0.25 and 0.65); the creases wander
  ±15° round the limb along its length (twist), so they read as gnarled wood, not flutes on a column.
- **Foot:** the column and the spur meet in a **V-notch 0.25–0.35 deep** at the ground. The spur is a flattened tube
  (height 0.7 of width), Ø 1.6 → 0.6, ending in a blunt toe (domed 5–6-gon, not a point).
- **Club end:** a domed cap: 2 rings closing to a small 5-gon, bulged +10 %. Bark-coloured: **no pale cut wood on
  this sheet**.
- **Construction:** `_root(path, radii, seed, sides=10, creases=…)` along a Catmull–Rom path through the §2.2 control
  points (stations about 0.55 apart, 0.35 round the crest bend); the spur as a second tube unioned at the foot.
- **Triangles:** 10 × 2 × about 20 stations ≈ 400 + spur ≈ 100 + cap ≈ 20 → **about 520**.

#### Root Half (Right): (369,780,552,985), 184 × 206 px

- **Shape:** a long S-curved limb: a fat blunt top end (upper left), a knee, a narrower lower leg and a tapered foot.
  Widths along its axis (5 → 95 %): `43 67 70 55 60 60 55 44 43 33` px: the top end fattest (Ø ratio 1.0), body 0.85,
  lower leg 0.65, foot 0.5. Axis length 261 px.
- **In the hero:** about **8.1 studs** along its centreline, Ø 1.45 (top end) → 1.2 → 0.85 (foot).
- **Section and relief:** as L's (10 sides; 2–3 creases 0.10–0.15 deep; one **sharp lit ridge** along the top of the
  descending leg, seen in `z_f34_right.png`; 1–2 knots).
- **Ends:** the top end a domed cap (stands up behind L's crest); the foot a blunt angled end face (a 6-gon sloped
  about 50°) resting on the base / ground, no flare.
- **Triangles:** 10 × 2 × about 17 ≈ 340 + caps ≈ 30 → **about 370**.

#### Leaf Clump: exploded (125,983,240,1090) 116 × 108 and (411,960,519,1064) 109 × 103 px

- **Shape:** an **upright fan**: 6–7 leaves from one hidden point, spread in a V/fan from about 15° to 90° above
  horizontal on both sides (exploded) or one-sided like a hand of cards (hero: left fan 5 leaves opening to −X, right
  fan 4 leaves opening to +X). Height : span **0.93–0.94 exploded, 1.03–1.18 hero** — never a flat rosette and
  never a closed cup.
- **Leaf:** a **thick faceted kite** (a flattened bipyramid): narrow neck at the base, widest at 0.4 L, straight
  sides to a sharp tip, **W : L ≈ 0.45**, a raised ridge down the front and the back (thickness 0.12–0.16 L in total),
  so every leaf has a lit half and a dark half. Hub → tip colour: dark yellow-green at the base, lime at the tip.
- **Size (hero governs):** leaves 2.2–2.9 long (exploded leaves about 1.4: drawn smaller); fan span about 3.0 × 3.5
  (left) and 2.9 × 3.0 (right).
- **Construction:** `_leaf(L, W, seed)`: 6-point outline + front and back ridge lines → a closed shell of 16–20 tris;
  `_fan(hub, leaves, seed)` places them by (yaw, pitch, length) from §2.3, each leaf ±8 % L, ±6 % W, ±6° roll; a
  hidden 6-sided hub cone (radius 0.22, 12 tris) in `leaf_base`.
  - **Bowties (lesson from 019–021):** start each leaf's neck **inside** the hub cone (base centre at 0.6 × hub
    radius from the axis, below the cone's top ring), give the neck a real width (≥ 0.08), and never let two leaves
    share a vertex. The union then cuts a full loop. Run `M.audit()` (`nonmanifold_verts` must be 0) after each
    fan, and `M.fix_bowties` if needed.
- **Triangles:** 5 × 18 + 12 ≈ 100 (left), 4 × 18 + 12 ≈ 85 (right); the part (exploded 7-leaf fan) about 140.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, origin = the base's plan centre). From `proxy.py` /
`layout2.json`, fitted to the f34 at (az 0, e 13), checked at the r34 (−40, 15).
Sheet → world in the f34: X = (x − 282.5) / 49.5; screen up u = (463 − y) / 49.5 = z cos 13° + (Y + 3.5) sin 13°.

### 2.1 Base, rim lumps and boulders

| Piece | Centre (x, y) | Size Ø × height | Sheet evidence | Paint |
| --- | --- | --- | --- | --- |
| Base slab | (0, 0) | 8.6 × 6.8 plan; floor z 0.35, rim 0.45 | f34 base ellipse; bottom profile rise .08–.11 H at the sides; R08 base 8.97 × 7.89 | `base` |
| Rim lumps ×7 (fused) | azimuths (0 = +X, 90 = back) 15°, 60°, 120°, 165°, 205°, 300°, 340°, on the slab edge | 1.2–1.8 wide, 0.25–0.45 proud of the floor | exploded base rim; underside lumps past the edge | `base`, tops 30 % `rock` |
| Far-left boulder | (−4.3, +0.2) | 1.0 × 0.9 | f34 (45–95, 360–412), in shade beside L's toe | `rock` |
| Big front-left boulder | (−2.4, −2.7) | 1.8 × 1.45 | f34 (117–212, 370–462), in front of L's column ("Rocks Support Root Ends") | `rock` |
| Front-mid boulder | (−0.75, −2.8) | 1.35 × 1.15 | f34 (214–285, 395–460) | `rock` |
| Small centre boulder | (−0.35, −1.6) | 0.95 × 0.7 | f34 (256–306, 380–416), at the egg's lower left | `rock` |
| Right-mid boulder | (2.75, −1.0) | 1.05 × 0.9 | f34 (386–442, 359–402), right of the egg's foot | `rock` |
| Right boulder | (3.5, −2.35) | 1.25 × 1.0 | f34 (425–489, 390–442), in front of R's foot | `rock` |
| Back boulders ×3 | (−1.6, 2.9); (0.4, 3.1); (2.6, 2.6) | 1.4 × 1.1; 1.3 × 1.0; 1.1 × 0.95 | top cell: two dark boulders behind R's hump, one at the back-right | `rock` |

- The front boulders stand **apart** (0.1–0.4 gaps, or touching at one edge), so the floor shows between them as in
  the f34 (sheet (255–430, 400–465)). They must not merge into a wall or a heap.

### 2.2 Roots (centre-line control points, x, y, z; Ø = diameter)

| Root | Control points | Ø along the points | Notes |
| --- | --- | --- | --- |
| L | (−2.65, −1.5, 0.55) → (−2.07, −1.3, 1.57) → (−1.47, −1.1, 2.91) → (−0.68, −0.9, 4.24) → (0.0, −0.7, 5.45) → (1.0, −0.62, 5.4) → (1.6, −0.58, 5.1) → (2.0, −0.52, 4.75) → club end (2.15, −0.5, 4.3) | 2.5 (foot, ellipse 1.25 : 1) → 2.3 → 1.9 → 1.7 → 1.55 → 1.5 → 1.48 → 1.45 → 1.45 (club, +10 % bulge) | f34 run centres at h .3/.5/.7 (X −2.07/−1.47/−0.68); crest top z ≈ 6.2 (f34 h .99); club end at sheet (370–410, 202–238) |
| L spur | (−2.65, −1.5, 0.5) → (−3.4, −1.55, 0.42) → toe (−4.25, −1.6, 0.3) | 1.6 → 1.0 → 0.6 (flattened, height 0.7 of width) | f34 toe f .06–.15, h .02–.20 |
| R | top end (−1.1, 1.0, 5.15) → (−0.4, 0.8, 4.85) → (0.5, 0.5, 4.55) → (1.2, 0.3, 4.3) → (1.9, 0.05, 4.05) → (2.42, −0.2, 3.38) → (2.8, −0.4, 2.74) → (3.38, −0.6, 2.09) → (3.83, −0.8, 1.45) → (4.3, −0.95, 0.8) → foot (4.5, −1.05, 0.45) | 1.45 (top end, domed) → 1.35 → 1.25 → 1.2 → 1.2 → 1.2 → 1.15 → 1.1 → 1.0 → 0.9 → 0.85 | the hump top u 6.67 at X −0.25 → top surface z ≈ 5.8; the band over the egg u 4.4–4.95; the leg's run centres h .7….2 |

- **Contact and joins** (sheet note 4: "flat joining surfaces"):
  - Each foot sinks **0.15–0.2 Ø** into the base (exact union, a clean contact line, no pads). The spur toe rests on
    the slab edge / ground (underside z 0–0.1).
  - **L's club end overlaps the front of R's shoulder** by about 0.3 (union): the club "rests on" R, as drawn.
  - **R rests on the egg's back-top** at about (0.8–1.4, 0.3, 3.7): with the egg unioned, R sinks 0.05–0.1 into
    it; with the egg as a separate shell (§8.6), keep a 0.01–0.03 clearance (no intersections). Further down R
    hugs the egg's right flank with 0.15–0.25 clearance (z 2.7–3.4).
  - L passes in front of the egg's top-left (y −0.7 at the crest); its leg is 0.5–0.7 clear of the egg's left side.
- **Crossing order:** L in front (−Y) of R everywhere they overlap in the f34; R's top end rises behind L's crest and
  shows above it at f .40–.45.

### 2.3 Sapstone and leaf fans

| Piece | Placement | Size | Sheet evidence | Notes |
| --- | --- | --- | --- | --- |
| Sapstone | centre (1.0, 0.0), bottom z 0.30 | 2.65 W × 2.45 D × 3.45 H | f34 .596, .420 (proxy .599, .397); h .18–.68 | egg axis upright, a slight 4° lean to −X |
| Left fan | hub (−2.3, −0.4, 2.0), sunk 0.15 into L's back-left flank; a back boulder or rim lump under it | 5 leaves, (yaw°, pitch°, L): (188, −20, 2.55), (172, 8, 2.6), (155, 35, 2.65), (132, 60, 2.75), (105, 80, 2.9) | f34 f .00–.30, h .31–.83; lowest tip at X −4.95, z ≈ 1.7; top tip z ≈ 4.8 | yaw 0 = +X, 90 = back; the fan plane faces the front, tilted 20–30° back |
| Right fan | hub (3.35, −0.15, 1.95), sunk 0.15 into R's back flank | 4 leaves: (−8, −18, 2.3), (12, 15, 2.35), (38, 45, 2.45), (68, 72, 2.6) | f34 f .71–1.00, h .34–.78; lowest tip X ≈ 5.0, z ≈ 2.3; top tip z ≈ 4.6 | the junction close-up's "Leaf Inset Between Roots" |
| (Option) Inner fan | hub (1.6, 1.5, 0.35) on the floor behind the egg, or (−0.2, −1.9, 0.35) in front (§3.2) | 3 leaves, L 1.8–2.0, pitch 40–75° | r34 .420, .257 (152 × 96 px); side .309, .204 | decision §8.4 |

- **Expected hero:** X −5.0 … +5.0 (leaf tips), Y −3.5 … +3.9, z 0 … 6.2 → **about 9.9 × 7.6 × 6.2**.
- **Proxy checks** (orthographic, `proxy.py layout2.json`):
  - `f34_sheet (0, 13)`: W : H 1.52 (sheet 1.471; the proxy's flat leaves run wide, real fans will land nearer
    1.47), egg (.599, .397) against (.596, .420), root share 44.0 (46.1), leaf 12.2 (15.2: the proxy's kites are
    thin), stone 29.9 (23.7: the proxy fills the base).
  - `r34_sheet (−40, 15)`: W : H **1.299** (sheet 1.296); egg (.577, .445) against (.638, .458).
  - `side_sheet (90, 10)`: W : H 1.03 (sheet 1.163; §3.3). `rear (180, 10)`: 1.48 (sheet 1.335; §3.4).
  - `top_sheet (0, 50)`: 1.39 (sheet 1.141: the sheet's top is a perspective shot; §3.5).

## 3. View conflicts and resolutions

### 3.1 The "front three-quarter" is an elevated front view

- **Evidence.** The base ellipse is symmetric about the image centre and rises 0.08–0.11 H at both sides; with the base
  8.6 × 6.8 that is e ≈ 12–15°. The egg's fitted position matches only at az ≈ 0 (.599 against .596). L's foot, the
  crest and R's foot lie left-to-right as a front view would show them.
- **Resolution.** Compare the f34 and front cells with an extra **`f34_sheet (0, 13)`**. The kit `front34 (−28, 12)` has
  no sheet counterpart: self-consistency only. The hero governs (WorldModeling §1.1).

### 3.2 The rear three-quarter is the hero from the front-left, with an extra fan

- **Evidence.** It shows the same arch the same way round (L's foot left, the club end right, R's hump behind the crest
  at the top-left), which a real rear view would mirror (the real rear cell does, §3.4). The proxy's W : H at
  (−40, 15) is 1.299 against the sheet's 1.296.
- **The inner fan** (3 broad leaves in front of the egg's lower left) appears in the r34, the side cell and the
  junction close-up, but **not** in the f34, the front or the top, which all show boulders and bare floor there. As a
  front-left feature it would contradict three front views.
- **Resolution.** Compare with **`r34_sheet (−40, 15)`**: W : H ±0.08, shares ±5 (leaves may run up to −6 without the
  inner fan), the egg right of centre, R's hump at the top-left. Inner fan: decision §8.4. The kit `rear34 (152, 12)`
  is self-consistency only.

### 3.3 The side (right) cell is a narrow redraw of the hero

- **Evidence.** It draws an arch with the egg in its opening. From +X (the kit side camera at az 90 sits at +X, so
  screen right is the model's back) L runs straight away from the camera: it reads as a column with the club end near
  the top, R's leg comes near on the left half, and the egg is partly hidden (proxy W : H 1.03 against 1.163). No
  single camera on the hero's layout gives the sheet's side arch.
- **Resolution.** Compare the kit `side (90, 4)` and an extra `side_sheet (90, 10)` by shares (±6), W : H 1.00–1.20, the
  egg visible between the legs, both fans visible. Record the arch shape as a known miss.

### 3.4 The rear cell agrees with the layout (mirrored arch)

- **Evidence.** The club end hangs at screen left and the long leg falls to screen right; from az 180, screen left is
  +X, which is where L's club end is. R's hump shows behind at the top centre-right (−X side from the back).
  The rear's W : H (1.335) is narrower than the proxy's 1.48, and its leaves (22 %) are heavier.
- **Resolution.** Compare the kit `rear (180, 4)` and an extra `rear_sheet (180, 10)`: club end at the left, the hump at
  the top centre-right, egg visible through the arch, shares ±6, W : H 1.30–1.50.

### 3.5 The top cell is a high front view, in perspective

- **Evidence.** Its W : H 1.141 is far below any orthographic view of the layout (1.39 at e 50, 1.44 at e 89); the
  near crest is enlarged. Its content is the hero's, seen from about e 45–50.
- **Resolution.** Compare with **`top_sheet (0, 50)`** by composition: R's hump at the back-left with two boulders behind
  it, L climbing from the front-left foot, the egg below and right of the crest, boulders ringing front and back, fans
  left and right; shares ±6. Don't chase W : H. The kit `top (0, 89)` is self-consistency only (an oval base, the arch
  crossing it from front-left to right, the egg right of centre).

### 3.6 Exploded against hero

- **Egg:** the same size in both (137 × 169 against 132 × 167 px), so the exploded is at the hero's scale.
- **Roots:** drawn shorter and thinner: L 6.3 studs long, Ø 1.2–1.6 as drawn, against the hero's 8.6 + spur and Ø 1.45–
  2.5; R 6.4 against 8.1. **The hero governs.** The exploded's dog-bone (fat ends, slimmer middle) and S-curve
  (R) carry over as shape language: knots near the ends, a slimmer middle on L's crest relative to its foot and club.
- **Fans:** exploded 2.3 across with 6–7 leaves about 1.4 long; hero 3.0 × 3.5 with 5 / 4 leaves 2.2–2.9 long. Hero
  governs for the hero; the `...LeafClump` part follows the exploded fan (7 leaves, both sides) at the hero's leaf
  size.
- **Base:** the exploded base shows its rim lumps clearly; in the hero most are hidden behind boulders.

### 3.7 Flat joining surfaces

- **Evidence.** "Parts designed to interlock with flat joining surfaces" and the base close-up's "Flat Joining Surfaces"
  pointer on the flat slab top where a boulder and a foot sit.
- **Resolution.** Feet and boulders sit on the slab's flat floor and sink 0.1–0.2 into it with exact unions (one clean
  contact line). No pads, no sockets. The base's own top stays flat (±0.06) wherever a foot or boulder sits.

### 3.8 "Simple solid colors, no textures or noise" against the user's blended-colour rule

- The user's rule wins (memory "Kit colouring"), and the sheet itself shows painted variation:
  - the roots get lighter toward the crest and darker toward the feet (exploded L by height `#A1683F` → `#A56E49` →
    `#B0744B`; exploded R's lower two thirds `#925D38`/`#8D5A35` against its top `#AF7244`);
  - the boulders' lit tops are greyer (Rock (Secondary) `#AEA9A8`; lit rock faces `#A08A7D`–`#A89286`, sat 0.17–0.22)
    than the warm base (`#796155`, sat 0.30);
  - the leaves run dark at the hub (`#5A6B05`) to lime at the tip (`#8CA518`–`#A7B81E`);
  - the egg is darker at its foot (`#517D48`) than its body (`#689E5F`).
- Keep Tint low so it still reads "clean".

### 3.9 Two greens

- The palette deliberately separates **Sapstone (Green)** `#96C670` (hue 93°, sat 0.43: soft, cool, minty) from **Leaf
  Foliage** `#879222` (hue 66°, sat 0.77: olive-lime). On the renders: sapstone hue 95–106°, sat 0.42–0.53; leaves hue
  66–72°, sat 0.85–0.96. They must stay apart after calibration (§5.4); merging them is the main colour risk here.

### 3.10 Root ends: no cut wood

- Unlike 020/021, every root end on this sheet (L's club, L's toe, R's top end, R's foot) is **bark-coloured**: no pale
  cut tip anywhere. Ends are domed or bluntly angled caps.

### 3.11 The see-through gap under the crest

- **Evidence.** One small window in the f34 (f .63–.70, h .67–.73, ≈ 0.7 × 0.45) between L's crest, its club end and R's
  shoulder.
- **Resolution.** Nice to have: it appears if L's crest bottom stays above z ≈ 4.35 at X 1.3–2.0 and R passes low
  there. Don't distort §2 to force it; record whether it shows.

### 3.12 Effects

- The sheet shows none (no glow, sparkle, dust or particles; the egg has a dark shade side, so it isn't emissive).
  Stages 5 and 6 add nothing by default (§7).

## 4. Construction plan (stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `base()` → `SapstoneRootArchBase`: slab + 7 rim lumps, flat underside. Compare with the exploded base (a flat
     floor inside a low lumpy rim) and the underside close-up.
   - `rock()` → `SapstoneRootArchRock`: one boulder (the big front-left, 1.8 × 1.45). Compare with the exploded rocks.
   - `sapstone()` → `SapstoneRootArchSapstone`: the egg. Compare its width profile with §1.4 (±0.05 per band).
   - `root_left()` → `SapstoneRootArchRootLeft`: L with spur, creases, knots and club end. Compare with the exploded L
     (dog-bone, blunt ends) and with the hero's leg in the f34.
   - `root_right()` → `SapstoneRootArchRootRight`: R. Compare with the exploded R (S-curve, fat top end, tapered foot).
   - `leaf_clump()` → `SapstoneRootArchLeafClump`: the exploded 7-leaf fan (both sides). Height : span ≥ 0.9.
   - Render a parts shot (`extra`, about (−20, 15)) laid out like the exploded.
2. **Hero:**
   1. `_paste` (m011 pattern) the base, 9 boulders, L, R, the egg and 2 fans at §2.
   2. Exact unions one piece at a time, saving between (STAGES "Booleans"): base + boulders, + L, + R, + fans (+ egg
      if §8.6 is "union"); then `union_loose`, then `m004.floor_cut` at z 0.
   3. Origin at the bbox bottom centre; transforms applied. Shells: one, or two with the egg separate (§8.6).
3. **Budget** (§4.3): hero about 2500–3100 (limit 4000); each part under 1000. If over, drop boulder rings to 2 and
   rim lumps to 5 before cutting root sides; roots keep 10 sides and their creases; the egg keeps ico-1.
4. **Placeholder keys** (stage 1): `m029_root`, `m029_base`, `m029_rock`, `m029_sap`, `m029_leaf`. Stage 4 adds the
   rest (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** a gnarled two-root arch over a faceted green egg on a flat round base with boulders; the arch
      grips the egg; fans upright on both sides.
   2. **`f34_sheet (0, 13)` against the f34 cell:**
      - W : H 1.40–1.54; shares within ±4 (S ±3) of L 15.2 / S 15.1 / R 46.1 / K 23.7;
      - top profile within ±0.07, root-only top line within ±0.08, width per height within ±0.07 at h .1 … .9;
      - **root runs** at h .3 / .5 / .7 within ±0.05 of §1.2 (L at h .5 spans .24–.46: a thick leg, about 2× R's
        width at the same height);
      - egg at (.596, .420) ±0.04, W : H of its visible part 0.79 ±0.06; fans at §1.2 ±0.06 with height : span
        ≥ 1.0; R's hump visible behind L's crest at f .30–.54, its top level with or above the crest at f .40–.45;
      - 6 boulders visible, the floor visible between them in front of the egg (a continuous band at h ≤ .19 across
        f .44–.80).
   3. **`r34_sheet (−40, 15)`:** W : H 1.22–1.38; egg right of centre (f .58–.70); shares ±5 (leaves −6 allowed).
   4. **`top_sheet (0, 50)`**, **`side_sheet (90, 10)`**, **`rear_sheet (180, 10)`**: composition per §3.3–3.5; shares ±6.
   5. **Kit views** (front34, rear34, front, side, rear, top, underside): self-consistency; the underside shows one
      flat base plane with lumps past its edge.
   6. **Bark relief (measurable, lesson from 020):** sample the bark radius about the centreline by azimuth (2° steps)
      at three stations on L's leg (z 1.5, 2.5, 3.5) and two on R's (z 2.0, 3.0): every station must show ≥ 3
      creases with min/median radius ≤ 0.90 (grooves 0.12–0.18 deep on L, 0.10–0.15 on R) and a spread of at
      least ±0.12 stud. Knots: the radius along each limb must rise ≥ 12 % over its neighbours at 2 places.
   7. **Base reads as one slab (lesson from 021):** in the parts shot the base silhouette is a low lozenge with
      W : H ≥ 4 : 1 (rim lumps ≤ 0.45 proud); in `f34_sheet` the boulders are separate objects on its rim, not a
      continuous heap; no boulder is taller than 1.5.
   8. **Parts against their cells** (§4.1), and **hero size** 9.9 × 7.6 × 6.2 (±0.4 / ±0.4 / ±0.25).
6. **Stage 2:**
   - zero non-manifold edges **and vertices** (`M.audit()` `nonmanifold_verts` 0; bowties at leaf hubs, the egg's
     seat and where the club end meets R), zero boundary, wire and loose elements; no zero-area faces or n-gons;
     normals outward;
   - no faces under 5° where roots, boulders, fans and the base meet (m011 `_tidy` / `_desliver`);
   - don't decimate root sections below 10 sides, the creases, the egg below ico-1, or the leaves' kite outlines.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Base (slab + 7 rim lumps, after its own union) | 1 | 400 | 400 |
| Boulders (hull rocks) | 9 | 50 | 450 |
| Root L (10 sides, ~20 stations, spur, club cap) | 1 | 520 | 520 |
| Root R (10 sides, ~17 stations, 2 caps) | 1 | 370 | 370 |
| Sapstone (ico-1 egg) | 1 | 85 | 85 |
| Leaf fans (5 + 4 leaves × 18, 2 hubs × 12) | 2 | 100 / 85 | 185 |
| **Sum before union** | | | **about 2010** |
| **Hero after union** (contact seams, slivers, floor cut) | | | **about 2500–3100** (limit 4000) |
| Parts: Base / Rock / Sapstone / RootLeft / RootRight / LeafClump | | | about 400 / 60 / 85 / 520 / 370 / 140 (limit 1000) |

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 20 × 16 box inside each, x 36–56)

| Swatch (label) | Box | Hex | HSV | Reads as |
| --- | --- | --- | --- | --- |
| Root Wood | (36,1297,56,1313) | `#9F6840` | 25°, 0.60, 0.62 | roots (= exploded L median `#A66E47` within 9) |
| Rock (Primary) | (36,1338,56,1354) | `#80685D` | 19°, 0.27, 0.50 | base and boulder bodies (= exploded base `#7E675C`) |
| Rock (Secondary) | (36,1378,56,1394) | `#AEA9A8` | 10°, 0.03, 0.68 | the grey lit tops of the boulders (rendered `#A08A7D`–`#A89286`) |
| Sapstone (Green) | (36,1418,56,1434) | `#96C670` | 93°, 0.43, 0.78 | the egg's lit body (rendered lit quartile `#A4D57E`) |
| Leaf Foliage | (36,1459,56,1475) | `#879222` | 66°, 0.77, 0.57 | leaves (between the mid and tip bands) |

### 5.2 Rendered regions (`samp.py`, `samp2.py`, `egg.py`; median / lit quartile / shade quartile by luminance)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Roots, f34 / front / r34 | bbox | R | `#A16942` / `#A16943` / `#A06943` | `#D08F5E` / `#C98A59` / `#CF8D5D` | `#6C4426` / `#6D4628` / `#72492A` |
| Roots, side / rear / top | bbox | R | `#A97048` / `#AD7348` / `#AB7045` | `#D69765` / `#D39361` / `#C88958` | `#7A4E2D` / `#6F492A` / `#794F2F` |
| Roots, exploded L / R (unshadowed) | (140,790,345,990) / (365,780,555,990) | R | `#A66E47` / `#935E38` | `#BC7D4F` / `#CB8B5A` | `#855635` / `#6D472A` |
| Exploded L by height third (bottom → top) / R | boxes | R | `#A1683F` → `#A56E49` → `#B0744B` / `#925D38` → `#8D5A35` → `#AF7244` | | |
| Roots by height, f34 h 0–.2 / .2–.4 / .4–.6 / .6–.8 / .8–1 | bands | R | `#845532` / `#925F39` / `#A26A42` / `#AB7248` / `#C88755` | | |
| Roots, junction / base close-ups | cu boxes | R | `#A66E48` / `#96613D` | `#D69868` / `#BE7F50` | `#70482A` / `#6C4528` |
| Stone (base + rocks), f34 / front / r34 | bbox | K | `#796256` / `#776256` / `#6B594E` | `#997F73` / `#988174` / `#9E867A` | `#4B3E36` / `#51433B` / `#453830` |
| Stone grey sub-mask (sat < .22), f34 | bbox | K | `#7D6E6A` (13°, .15) | `#A89286` | `#5B4E49` |
| Base floor f34 / base front edge / underside / base close-up floor | (300,418,400,440) / (250,445,420,462) / (720,1340,940,1460) / (760,1150,900,1190) | K | `#796155` / `#7A6257` / `#7B6558` / `#81695C` (sat .28–.30) | `#917466` / `#8A6F61` / `#7F685B` / `#997D6F` | `#745D52` / `#6B564B` / `#756055` / `#705B51` |
| Exploded base / rocks L2, L1, R3 | boxes | K | `#7E675C` / `#796358`, `#6C5A50`, `#78635A` | `#A0887B` / `#927B70`, `#8E776C`, `#A68D80` | `#594B43` / … |
| Boulders, f34: big front-left / front-mid / small / right-mid / right / far-left (shade) | §2.1 boxes | K | `#7C6C67` (14°, .17) / `#705C52` / `#7B6A60` / `#725F56` / `#8D7364` / `#4F423C` | `#907A72` / `#A0887D` / `#A08A7D` / `#A68D7F` / `#9F877A` / `#605552` | `#56473F` / `#54463F` / `#493C36` / `#3E352E` / `#6B574B` / `#362C25` |
| Boulders, base close-up L / R | (670,1110,760,1170) / (890,1110,990,1160) | K | `#796660` / `#967D6F` | `#A18A7F` / `#A28B81` | `#5B4E49` / `#605047` |
| Sapstone, f34 / front / r34 / side / rear / top | bbox | S | `#699850` / `#6FA355` / `#72A34E` / `#86BB5A` / `#649245` / `#71A356` | `#C4E986` / `#AFDF81` / `#BAE47D` / `#B1DD7C` / `#90C25C` / `#B0DE77` | `#446634` / `#436836` / `#476C35` / `#4B7539` / `#334F25` / `#4A703A` |
| Sapstone, exploded (unshadowed) | (268,893,408,1065) | S | `#70A660` (106°, .42) | `#A4D57E` | `#51834C` |
| Sapstone by height fifth, exploded / f34 (bottom → top) | bands | S | `#517D48` `#629B54` `#689E5F` `#99CF79` `#98CE76` / `#436637` `#65944B` `#78A757` `#90C068` – | | |
| Leaves, f34 / front / r34 / side / rear / top | bbox | L | `#6D7F07` / `#6B7E0A` / `#677A05` / `#6E810D` / `#72860B` / `#70820D` | `#AEC01E` / `#A8BD1E` / `#A7BD19` / `#ACC01B` / `#A7BC1D` / `#A7BC1C` | `#455202` / `#4A5803` / `#3F4B02` / `#485502` / `#4D5B04` / `#444E02` |
| Leaves, exploded L / R | boxes | L | `#74870D` / `#6A7E10` | `#9EB217` / `#A1B51C` | `#506103` / `#4E5D03` |
| Leaves, exploded fan hub → tip (5 radial bands) | hubs (183,1088) / (466,1060) | L | `#5A6B05` `#647607` `#728508` `#819711` `#8CA518` / `#4F5E07` `#58690B` `#6B8009` `#8A9F14` `#A7B81E` | | |

Deciles (dark → light), f34:

```
root   #59391F #73492A #875734 #905E3B #9A643E #A76E44 #B6784C #C68654 #CE8E5C #D89967
stone  #352514 #51433C #62534A #6E5A50 #776054 #7B6558 #846C5F #8A7466 #947C71 #A88E81
sap    #304924 #476C38 #588142 #65934B #66964E #73A454 #7AA855 #8DBF5A #BCE383 #C7EB95
leaves #394303 #495702 #576704 #607106 #687A03 #708306 #798C11 #8FA30D #ABBE1B #B6CA3D
```

### 5.3 How the colour works

**Roots.**
- One warm orange-brown family: hue 24–26°, sat 0.57–0.62. Clearly warmer and far more saturated than the base and
  boulders (19–22°, sat 0.15–0.30): that contrast is the asset's main read.
- **Painted signals:**
  1. **Lighter toward the crest:** exploded L's top third `#B0744B` against its bottom `#A1683F` (+12 levels on an
     unshadowed part, so paint); R's top end `#AF7244` against its lower body `#8D5A35`.
  2. **Darker toward the feet:** exploded R lower two thirds `#925D38`/`#8D5A35`; f34 bottom band `#845532` (part
     shade, part paint).
  3. The creases are dark from geometry (light), not paint. Don't paint the grooves.

**Base and boulders.**
- One mauve-brown family, hue 14–22°, v 0.42–0.55. The **base** is the warmer, more saturated member (sat 0.28–0.30:
  floor `#796155`, underside `#7B6558`); the **boulders** are a touch greyer (sat 0.17–0.27, `#7C6C67`–`#796660`) with
  **lighter, greyer lit tops** (Rock (Secondary): rendered `#A08A7D`–`#A89286`).
- **Painted signals:** boulder tops (upper 35 % of each boulder's height) blend toward `rock_light`; the base's
  lowest band and the floor right round each foot and boulder a touch darker (`base_dark`); the rim lumps' tops 30 %
  `rock`.

**Sapstone.** A soft mid green, hue 95–106°, sat 0.42–0.53. Light from the upper left gives the pale facets
(`#C4E986`) and the deep shade (`#446634`); paint only a gentle foot-darkening (exploded bottom band `#517D48`) and a
slightly lighter upper body (`#86BC68` region), by height, never by facing.

**Leaves.** Vivid olive-lime, hue 66–72°, sat 0.85–0.96. Hub → tip ramp `#5A6B05` → `#8CA518` (exploded, unshadowed);
the ridge fold gives each leaf its lit and dark half (geometry).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

The calibration targets are rendered medians of **unshadowed** regions (exploded parts and close-ups), not swatches.
`K.sample` kinds: `"brown"` for the root keys; `"stone"` (or `"all"` on tight boxes) for base and boulders; `"green"`
for the sapstone and the leaves (check the green filter accepts hue 66–72 at sat 0.9; otherwise `"vivid"` or `"all"`
on tight boxes).

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m029_root` | `#A06A44` (exploded L `#A66E47`; swatch `#9F6840`) | roots, the default | rough 0.9 |
| `m029_root_dark` | `#8C5935` (exploded R lower thirds `#925D38`/`#8D5A35`) | the last 1.5 studs to each foot, the spur, the bottom 35 % of each section by position | rough 0.92 |
| `m029_root_light` | `#B0744B` (exploded L top third; R top `#AF7244`) | crest and club tops above z 4.6, R's top end, as a 40 % mix; broad patches | rough 0.9 |
| `m029_base` | `#7B6458` (floor `#796155`, underside `#7B6558`, exploded base `#7E675C`) | base slab and floor, the default | rough 0.95 |
| `m029_base_dark` | `#6B564B` (base front-edge shade; floor next to feet) | z < 0.15 on the slab edge; floor within 0.4 of a foot or boulder, soft | rough 0.95 |
| `m029_rock` | `#7A6762` (big front-left `#7C6C67`, close-up rock `#796660`; sat ≈ 0.18) | boulders, the default; rim-lump tops 30 % | rough 0.9 |
| `m029_rock_light` | `#A2918A` (lit tops `#A08A7D`–`#A89286` pulled toward Rock (Secondary) `#AEA9A8`) | boulder tops above 65 % of their height, 50 % mix, blending over 2 steps | rough 0.88 |
| `m029_sap` | `#70A660` (exploded median) | the egg, the default | rough 0.55 |
| `m029_sap_light` | `#86BC68` (between the median and the swatch `#96C670`) | upper 40 % of the egg as a 50 % mix | rough 0.55 |
| `m029_sap_dark` | `#557F48` (exploded bottom band `#517D48`) | lowest 15 % of the egg | rough 0.6 |
| `m029_leaf` | `#6E8209` (exploded mid bands `#647607`–`#728508`; f34 median `#6D7F07`) | leaf middles | rough 0.8, `low_spec` |
| `m029_leaf_tip` | `#8CA518` (outer band) | outer 30 % of each leaf | rough 0.8, `low_spec` |
| `m029_leaf_base` | `#56680A` (inner bands `#5A6B05`/`#4F5E07`) | inner 25 %, hub cones | rough 0.8, `low_spec` |

**Calibration warnings:**
- **Roots against stone:** after calibration the `f34_sheet` medians must keep the sat gap: roots `#A16942` ±10 with
  sat ≥ 0.55; stone `#796256` ±10 with sat ≤ 0.32.
- **Boulders against base:** boulder bodies at least 0.06 less saturated than the floor, and their lit quartile within
  12 of `#A08A7D`, never white-grey (hue 14–22° stays).
- **Two greens (§3.9):** sapstone median within 12 of `#699850` (f34), hue 95–106°, sat 0.40–0.55; leaves within 12 of
  `#6D7F07`, hue ≤ 74°, sat ≥ 0.82. Greens calibrate darker than the painted sheet (kit memory): trust the render
  match, not the swatch.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Roots** (fields: arc length s from each foot along the limb, normalised; height fraction within the local section;
  world z):
  - `root` base;
  - s < 0.2 from a foot (and the whole spur) → up to 55 % `root_dark`, fading out by s 0.35;
  - bottom 35 % of each section → 30 % `root_dark` (position in the section frame, not the normal);
  - z > 4.6 (crest, club top, R's top end) → 40 % `root_light`;
  - broad patches (`K.patches` scale 0.8, level 0.3) between `root` and a 30 % `root_light` mix, each patch with a 50 %
    then 25 % edge ring (020's minor 1); never single faces.
- **Base:** `base`; slab edge z < 0.15 → 40 % `base_dark`; floor within 0.4 of a foot or boulder → 35 % `base_dark`
  (soft, 3 steps); rim-lump tops → 30 % `rock`; broad patches `base` ↔ 25 % `rock`.
- **Boulders:** `rock`; above 65 % of each boulder's height → 50 % `rock_light`, 2 steps down to `rock`; contact band
  (lowest 15 %) → 25 % `base_dark`.
- **Sapstone:** height fraction t: t < 0.15 `sap_dark`, 0.15–0.6 `sap`, t > 0.6 → 50 % `sap_light`; 3 steps.
- **Leaves** (field = each leaf's along-length t): t < 0.25 `leaf_base`; 0.25–0.7 `leaf`; t > 0.7 `leaf_tip`; 3 steps,
  ±0.08 noise on t; hub cone `leaf_base`.
- **Hard edges only** where materials meet: root | base, root | boulder, root | egg, egg | base, leaf | root.

### 5.6 Texture (Tint) and finish

- **Tint** (`tint_var` per piece about 0.04): roots `K.texture` amp 0.05, scale 0.5 (facet-group mottling); base amp
  0.05, scale 0.7; boulders amp 0.06, scale 0.5 (each broad face a slightly different tone, as on the sheet); sapstone
  amp 0.03; leaves amp 0.035. Never per-triangle confetti.
- **Finish:**

| Material | Roughness | Specular | Metal | Notes |
| --- | --- | --- | --- | --- |
| Root keys | 0.9 / 0.92 / 0.9 | normal | 0 | matte wood |
| Base / base_dark / rock / rock_light | 0.95 / 0.95 / 0.9 / 0.88 | normal | 0 | matte stone |
| Sapstone keys | 0.55 / 0.55 / 0.6 | normal | 0 | a faint mineral sheen, no glow |
| Leaf keys | 0.8 | `FOLIAGE_SPEC` (`low_spec=True`) | 0 | matte |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- `f34_sheet`: roots `#A16942` ±10, stone `#796256` ±10, sapstone `#699850` ±12, leaves `#6D7F07` ±12; lit/shade
  spreads within 15 of §5.2; shares per §4 step 5.2.
- Root height bands: the top band lighter than the bottom band by ≥ 40 levels (sheet `#C88755` against `#845532`).
- Parts shot: root L median `#A66E47` ±10 with its top third lighter than its bottom by ≥ 10; boulder lit tops greyer
  (sat ≤ 0.24) than the base floor (sat ≥ 0.27); the egg's bottom band darker than its middle by ≥ 15.
- Leaves: tips lighter than hubs in the parts shot.

## 6. Joins and contact

- **Feet on the base:** L's column and R's foot sink 0.15–0.2 Ø into the slab; L's spur toe rests on the slab edge;
  exact unions; one clean contact line ("flat joining surfaces").
- **L's club on R:** overlap 0.3, one union; no collar.
- **R over the egg:** union (sink 0.05–0.1) or clearance 0.01–0.03 if the egg is separate (§8.6).
- **Egg on the base:** seated on a small flat bottom face at the floor height (sink 0.05 if unioned).
- **Boulders:** each sinks 0.1–0.2 into the slab (or ground at the rim); the big front-left boulder touches L's column,
  the right boulder touches R's foot ("Rocks Support Root Ends").
- **Fan hubs:** sunk 0.15 into a root flank; leaf necks start inside the hub cone (§1.4 bowties).
- **Ground:** floor-cut at z 0 (`m004.floor_cut`): one flat underside ("Flat Base (For Placement)").
- No coplanar faces between pieces; overlap everything; add union pieces one at a time and save between (STAGES
  "Booleans").

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** an ordinary sunlit root arch over a matte green stone. No glow, light, sparkle, dust or
particles anywhere; the egg has a dark shade side, so it is not emissive. WorldModeling §1.2 forbids "an ordinary asset
recolored neon with a glow halo", and the §11 row for Ancient Root says "Effects, if later requested, must not conceal
the geometry during approval".

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight:** nothing on the sheet glows.
- **Studio note (Requires Manual Validation):** check in Studio that the two greens stay apart (soft mint egg against
  olive-lime leaves) under the game's sun, that the roots stay clearly warmer than the stone, and that the boulder tops
  read lighter than the base.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **Recommended: none.** The sheet shows no effect, and WorldModeling §11 makes effects for this asset "if later
  requested". Record "Stage 6 skipped: sheet shows no VFX".
- **Option** (decision §8.8): the R08 precedent and the resource-node precedent (M016, M019): **one `ore_glint`** on
  the sapstone, sparse, so the harvestable gem catches the eye:
  - location: the egg's upper front, about (1.0, −0.6, 2.6);
  - overrides: `color ["#E6F7C8", "#B6E08A"]`, `size [0, 0.5, 0]`, `rate 0.8`, `lifetime [0.5, 0.8]`, `shape` about
    [2.4, 3.0, 2.2] (Roblox X, Y up, Z), `light None`;
  - check the export STATS line reports 1 socket; render with `vfx=True`.
- **Not recommended:** `crystal_glow` / `crystal_halo` / any light (the egg isn't lit from inside), `dust`, harvest
  sockets (not on this sheet; M009–M026 decided against them).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by `git grep` of the repo and every sheet .blend (zstd-decompressed) searched with
`m020_study/blendall.py`:
- **R08 kit:** `AncientRoot`, `AncientRootBase`, `AncientRootDepleted`, `AncientRootHalfLeft`, `AncientRootHalfRight`,
  `AncientRootLeafClump`, `AncientRootMineralNodule`, drop `GreenSapstone`; key `r08_leaf_green` ("Ancient Root leaf
  clumps"), `r08_rock`. (`AncientRoot` occurs 58 times in `FlintbornWorldKit.blend`; `RootHalf` 12; `GreenSapstone` /
  `Sapstone` 3.)
- **W05:** `AncientRootModuleA/B/C` (9 hits in `W05.blend`).
- **`src`:** no node id.
- `M.mk` would silently rename a clash to `<name>M029`, so avoid all of these.

**Proposed names.** `SapstoneRootArch` (and `RootArch`) occur nowhere in the repo, the decompressed kit .blend or any
sheet .blend; `m029_` and `M029` are unused.

| Object | Part | Why |
| --- | --- | --- |
| `SapstoneRootArch` | hero | R08 owns `AncientRoot*`; a root arch over a sapstone |
| `SapstoneRootArchBase` | Base | R08 owns `AncientRootBase` |
| `SapstoneRootArchRock` | Rocks (Side) (one boulder) | |
| `SapstoneRootArchSapstone` | Green Sapstone | R08 owns `GreenSapstone` / `AncientRootMineralNodule` |
| `SapstoneRootArchRootLeft` | Root Half (Left) | R08 owns `AncientRootHalfLeft` |
| `SapstoneRootArchRootRight` | Root Half (Right) | R08 owns `AncientRootHalfRight` |
| `SapstoneRootArchLeafClump` | Leaf Clump | R08 owns `AncientRootLeafClump` |

- Palette keys `m029_*` (§5.4). Collection `Kit/M029 Ancient Root`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **9.9 W × 7.6 D × 6.2 H, roots Ø 0.85–2.5, egg 2.65 × 2.45 × 3.45** (recommended: egg-anchored,
   the crest just over the player's head, between M021 and R08), or ×1.2 (11.9 × 9.1 × 7.4) for a landmark-scale
   "ancient" node.
2. **Hero camera:** **`f34_sheet (0, 13)`** governs (recommended, §3.1); the kit front34 is self-consistency only.
3. **Root thickness and length:** **the hero's** (L Ø 2.5 → 1.45 with a spur, 8.6 long; R Ø 1.45 → 0.85, 8.1 long)
   (recommended), not the exploded's thinner, shorter halves (§3.6).
4. **Leaf fans:** **2 (left 5 leaves, right 4; the f34, front, top and exploded)** (recommended), or add the r34 /
   side cells' inner fan (3 leaves, about 60 tris): behind the egg at (1.6, 1.5) so the front views stay clean
   (preferred if added), or in front of the egg's lower left as the r34 draws it (contradicts f34, front and top).
5. **"Flat joining surfaces":** **feet and boulders sunk 0.1–0.2 into the slab's flat floor with exact unions, no pads**
   (recommended, §3.7).
6. **Hero packaging:** **two closed shells in the hero: the arch assembly (base, boulders, roots, fans) and the
   sapstone as its own shell, not unioned** (recommended: WorldModeling §11 "keep event inserts separate: … mineral
   nodule", and §12's depleted state removes the harvestable insert; R rests on the egg with 0.01–0.03 clearance), or
   one closed shell with the egg unioned (the M019 precedent, simpler checks).
7. **Exports:** the hero plus 6 parts (`...Base`, `...Rock`, `...Sapstone`, `...RootLeft`, `...RootRight`,
   `...LeafClump`) (recommended). No depleted variant or drops unless asked (R08 had both; this sheet shows neither).
8. **Stage 5/6:** **no emission, light or VFX** (recommended: the sheet shows none; WorldModeling §11), or one sparse
   `ore_glint` on the sapstone (§7.2; the R08 / M016 / M019 precedent).
9. **Comparison cameras** (recommended, §3): `f34_sheet (0, 13)` for the f34 and front cells, `r34_sheet (−40, 15)`
   for the r34, `side_sheet (90, 10)`, `rear_sheet (180, 10)`, `top_sheet (0, 50)`; kit front34, rear34, front, side,
   rear, top and underside as self-consistency only; extras `junction_cu (30, 20)` framed on L's club end and the
   right fan, `base_cu (−15, 10)` on the front floor and boulders, and a parts shot `(−20, 15)`.
10. **Names** as proposed.

## 9. Pitfalls to avoid

1. **Bent pipes.** The roots are gnarled: 10-sided sections with 3 creases 0.12–0.18 deep, 2 knots each, wandering
   ridges, a buttress foot with a spur and a V-notch on L, domed blunt ends. A smooth swept tube fails (020 failed as a
   "smooth cone"). Measure the relief (§4 step 5.6).
2. **Two equal arches.** L is the big one (Ø 2.5 → 1.45, foot spur, club end on R); R is slimmer (1.45 → 0.85) with its
   top end standing up behind the crest. Not mirrored, not equal.
3. **A rock pile base.** The base is one low flat slab with a low lumpy rim; 9 separate boulders stand on and around it
   with floor visible between them (021 failed as a rock pile).
4. **Flat rosettes or cups.** The fans are upright, one-sided hands of thick faceted kite leaves; height : span ≥ 1.0 in
   the hero, ≥ 0.9 for the part (021 failed with flat rosettes; 020's leaves were the opposite case, as their sheet
   drew flat stars: follow this sheet).
5. **A smooth or spiky egg.** Ico subdivision 1 stretched into an egg (widest at 0.45 H, narrower top), 80–90 tris; no
   subdivision 2+ (too smooth), no crystal spikes.
6. **Merged greens.** Sapstone soft mint (hue 95–106°, sat ~0.47) against olive-lime leaves (66–72°, sat ~0.9).
7. **Pale cut tips.** None on this sheet: every root end is bark.
8. **Comparing with the wrong camera.** The f34 is an elevated front view; the r34 is a front-left view of the hero;
   the side is a redraw; the rear is mirrored (and agrees); the top is a high perspective front view (§3).
9. **Floating fans or egg.** Hubs sink 0.15 into a root flank; the egg sits on its seat; R rests on the egg.
10. **Bowtie vertices** at leaf hubs, at the egg's seat and where the club end meets R: `M.audit()` `nonmanifold_verts`
    must be 0; start leaf necks inside the hub cone.
11. **Colour by facing.** Dark roots by arc length and section height; boulder tops by height within each boulder; the
    egg by height. `K.check` facing correlation < 0.5.
12. **Exact booleans.** Overlap everything; no coplanar faces; add pieces one at a time and save between; remove slivers
    with m011's `_tidy` / `_desliver`.
13. **Naming clashes** with R08 `AncientRoot*` / `GreenSapstone` and W05 `AncientRootModule*` (§8). No commits,
    pushes or exports in the modeller's stages.

## Decisions (main session, 2026-10-28)

The recommendations are accepted, with one change (6):
1. Size: 9.9 W × 7.6 D × 6.2 H.
2. Hero camera: `f34_sheet (0, 13)` governs.
3. Roots: the hero's thickness and length, not the exploded view's.
4. Two leaf fans, upright, with height to span ≥ 1.0 in the hero.
5. Joins: feet and boulders sunk 0.1–0.2 into the flat floor with exact unions, and no pads.
6. **Packaging: one closed shell**, with the sapstone united like every other kit hero (015's core, 019's lumps), so the kit-wide `shells == 1` check holds. The sapstone still ships as its own exported part (`SapstoneRootArchSapstone`).
7. Hero plus the 6 parts; no depleted variant and no drops.
8. No VFX.
9. Comparison cameras: `f34_sheet (0, 13)`, `r34_sheet (−40, 15)`, `side_sheet (90, 10)`, `rear_sheet (180, 10)` and `top_sheet (0, 50)`, plus the junction, base and parts extras.
10. Names as proposed (`SapstoneRootArch*`).

Bark relief targets (10-sided sections, 3 creases 0.12–0.18 deep, 2 knots per root) are binding. Keep the two greens apart with the spec's hue and saturation guards. `nonmanifold_verts` must be 0.


## Stage 1: Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m029.py`, `build()`: about 25 s of geometry and 20 s of renders in a background session.
Seeds are fixed and the current values need no retries. Each exploded part has its own function, and the hero is pasted
from the same builders.
- **Base** (`base_raw`): a lofted 14-gon slab with rings at z -0.06, 0.25, 0.45 (rim) and about 0.38 (floor edge), a
  9-vertex inner floor ring and a centre. The floor undulates +-0.06 by broad noise. Seven low hull rim lumps
  (`RIM_LUMPS`, top z 0.56-0.78) are sunk into the edge, fused with one exact union, and the slab is floor-cut flat. The
  part is 9.31 x 7.24 x 0.78 (slab plan 8.6 x 6.8 plus the lumps).
- **Boulders** (`BOULDERS`): nine, at the spec 2.1 positions. The back three moved 0.25 back, so the hero is 7.61 deep.
  Each is a chunky hull rock (point rings 6 / 7 / 6 / 4, jitter 0.15). Boulders on the rim stand on the ground
  (floor-cut); boulders on the floor sink 0.15 into it.
- **Sapstone** (`_sapstone`): bmesh `create_icosphere(subdivisions=2)`, which is the spec's "icosphere subdivision 1"
  (42 verts, 80 tris). bmesh's `subdivisions=1` is the bare 12-vertex icosahedron, which read as a crystal point in
  round 1a.
  - The sphere is turned (21, 13, 9 deg) so no pole sits on top.
  - Each vertex takes its height from its latitude and its radius from the sheet's egg width profile (`SAP_PROFILE`).
  - It is normalised to 2.65 x 2.45 x 3.45, with a flat seat and a 4 deg lean to -X.
  - Centre (1.3, 0), bottom z 0.30. The centre moved from 1.0 to 1.3, which took the f34 egg centre from .543 to .574
    (sheet .597).
- **Roots** (`_tube` for L, the spur and R):
  - **Paths:** 10-sided rings (8 on the spur) along Catmull-Rom paths through the spec 2.2 control points.
    - Round 1b raised L's crest to a flat top at z 6.1 over X -0.3 .. 1.4, with the club end hooking down at X 2.6
      onto R's shoulder.
    - R's lower leg moved 0.2 right to hug the egg.
  - **Rings:** set in the local up frame, with stations 0.68 apart (0.38 round bends).
  - **Radius:** diameter list x broad sectors (+-7 %) x knots x per-vertex jitter (+-6 %). Each vertex slides +-0.13
    along the limb, except round tight bends: there the slide folded the inner side (7 self-intersections at the hook
    in round 1a).
  - **Creases and ridges:** three crease columns pulled in (L 0.16 x r/0.95, R 0.14 x r/0.6). R has one ridge column
    pushed out 0.06, L has two. The ring twists slowly (+-12 deg), so the creases wander.
  - **Knots:** L at s 0.3, 0.62 and 0.97 (the club); R at s 0.05, 0.3 and 0.62.
  - **L's foot:** diameter 3.0 -> 2.8 with an elliptical buttress (1.5 : 1 along X, fading over 2.4 studs). The leg is
    then 3.1-3.4 wide at f34 h .3, as drawn. The feet run on under the ground into the slab.
  - **Joins and ends:** the spur is fused to L with one union. L's club end and R's top end have domed caps; the feet
    end in buried fans.
- **Leaf fans** (`fan`):
  - **Leaves:** thick hexagonal kites (`KITE`, W : L 0.48, front ridge 0.075 L, back keel 0.06 L, neck 0.14 wide),
    stacked 0.12 apart along the fan normal (0, -0.9, 0.42).
  - **Hubs (round 1c):** moved out to the legs' outer back flanks, 0.3 inside the bark, so the blades show beside the
    legs. Before, only their tips showed over the leg edges.
    - Left: low on L's buttress, origin (-2.89, -0.82, 1.64), 5 leaves 2.05-3.05 long.
    - Right: on R's back-left, origin (3.0, -0.18, 2.54), 4 leaves 1.65-2.5 long.
- **Leaf clump part:** 7 leaves round a hidden 6-sided hub (r 0.3), with yaws at least 45 deg apart. Two leaves 15 deg
  apart had crossed into self-intersecting slivers. Seed 29645; the guard tries up to 8 seeds, and the first is clean.

Hero assembly, in order:
1. Paste the fused base, 9 boulders, L, R, the egg and both fans.
2. Run 21 exact unions, one shell at a time, with merge distance 0 (so the leaf necks are not welded).
3. Cut the floor at z 0.
4. Run m016 `_clean_mesh`, then finish and polish.
5. Run `M.fix_bowties` (0 bowties needed).

## Stage 2: Optimisation and cleanup

| Object | Tris | Size (W x D x H) | Shells | Non-manifold edges / verts | Boundary | Self-hits |
| --- | --- | --- | --- | --- | --- | --- |
| SapstoneRootArch (hero) | 2350 / 4000 | 9.92 x 7.61 x 6.10 | 1 | 0 / 0 | 0 | 0 |
| SapstoneRootArchBase | 464 | 9.31 x 7.24 x 0.78 | 1 | 0 / 0 | 0 | 0 |
| SapstoneRootArchRock | 42 | 1.78 x 1.38 x 1.45 | 1 | 0 / 0 | 0 | 0 |
| SapstoneRootArchSapstone | 80 | 2.63 x 2.45 x 3.38 | 1 | 0 / 0 | 0 | 0 |
| SapstoneRootArchRootLeft | 388 | 8.06 x 3.00 x 6.10 | 1 | 0 / 0 | 0 | 0 |
| SapstoneRootArchRootRight | 338 | 6.55 x 3.21 x 5.78 | 1 | 0 / 0 | 0 | 0 |
| SapstoneRootArchLeafClump | 316 | 3.99 x 2.86 x 2.73 | 1 | 0 / 0 | 0 | 0 |

Every object also has:
- no wire edges, loose verts, zero-area faces or n-gons;
- no face corner under 5 deg;
- outward normals, flat shading and no custom normals;
- its origin at the bottom centre, with transforms applied.

`K.check` reports no problems. The hero is within its target of 9.9 x 7.6 x 6.2 (+-0.4 / 0.4 / 0.25).

## Stage 3: UV

Every object uses `M.smart_uv`: angle 45, an ANGLE_BASED re-unwrap, margin 0.008 (gap 0.016, border 0.008).
- 0 overlaps and 0 flipped triangles.
- Texel density min / median / max is 1.0 / 1.0 / 1.0.
- Conformal stretch p95 is 1.02-1.04.
- The hero has 371 islands at 33.6 texels per stud at 1024.

## Stage 4: Materials, colour and texture

**Pass 1** (`calibrate()` on the kit dome, targets from spec 5.4). Every key rendered within 6 of its target:

| Key | Hex | Key | Hex |
| --- | --- | --- | --- |
| root | #7E5739 | rock_light | #7F7676 |
| root_dark | #6F492B | sap | #5A8854 |
| root_light | #8A5F40 | sap_light | #6B995B |
| base | #62524C | sap_dark | #43693C |
| base_dark | #554740 | leaf | #5B6D07 |
| rock | #615454 | leaf_tip | #728817 |
| | | leaf_base | #495A08 |

**Pass 2** (the hero's `f34_sheet` render against the f34 cell). Factors are per channel (R, G, B), in linear light:

| Keys | Factors |
| --- | --- |
| Root keys, step 1 | x (1.12, 1.06, 1.0) |
| Root keys, step 2 | x (1.15, 1.12, 1.1) |
| root_light, extra (crest band) | x (1.35, 1.3, 1.25) |
| root_dark, extra (foot band) | x 0.85 |
| sap keys | x (1.3, 1.22, 1.0) |
| sap_light | x (1.45, 1.35, 1.1) |
| leaf_tip | x (1.25, 1.2, 1.0) |

**Final `PALETTE`:**

| Key | Hex | Key | Hex |
| --- | --- | --- | --- |
| root | #8E5E3C | rock_light | #7F7676 |
| root_dark | #6E4628 | sap | #669554 |
| root_light | #A8724B | sap_light | #7FAF5F |
| base | #62524C | sap_dark | #49703C |
| base_dark | #554740 | leaf | #5B6D07 |
| rock | #615454 | leaf_tip | #7E9417 |
| | | leaf_base | #495A08 |

**Re-measured** on the f34_sheet render against the f34 cell, with the study's masks:

| Region | Sheet median / lit | Ours median / lit | Guard |
| --- | --- | --- | --- |
| Roots | #A16942 / #D08F5E | #9E643F / #CD8555 | sat 0.60 (>= 0.55) |
| Stone | #796256 / #997F73 | #746058 / #93817A | sat 0.24 (<= 0.32) |
| Sapstone | #699850 / #C4E986 | #65924C / #8CC06B | hue 99, sat 0.48 |
| Leaves | #6D7F07 / #AEC022 | #6E820D / #9BB219 | hue 70, sat 0.90 |
| Root bands, bottom -> top | #845532 ... #C88755 | #955E3A ... #C98252 | top - bottom +52 in R |

- The two greens stay apart: sapstone hue 99 / sat 0.48 against leaves hue 70 / sat 0.90.
- The egg's lit facets render darker than the sheet's near-white highlights (#8CC06B against #C4E986), because the arch
  shades the egg in our studio.

**Blending** (by position only; every mix on 25 / 50 / 75 % steps):
- **Roots:**
  - darker toward each foot by arc length: full root_dark at the foot, fading out by 0.4 of the limb; the whole spur is
    dark;
  - 25 % darker on the lower 20 % of each section (section frame);
  - root_light 0-75 % by world z from 3.7 to 5.3;
  - broad noise patches with 50 % and 25 % rings.
- **Base:**
  - an edge band (z < 0.22) up to 50 % base_dark;
  - the floor within 0.45 of a foot or boulder up to 50 % base_dark;
  - lump tops 25 % rock;
  - broad 25 % rock patches.
- **Boulders:**
  - rock_light 0-50 % by height within each boulder, plus broad position patches;
  - the lowest 12 % at 25 % base_dark.
- **Sapstone:** a dark seat ring, a 25 % lighter upper body and broad mineral patches.
- **Leaves:** a hub -> mid -> tip ladder along each leaf (3 steps, +-0.06 noise).

**Texture:** broad Tint mottling, tint_var 0.04 per piece. Amplitude / scale: roots 0.05 / 0.5, base 0.05 / 0.7,
boulders 0.06 / 0.5; sapstone amplitude 0.03, leaves 0.035.

**Facing check** (`baked_shading`, limit 0.5):

| Object | Correlation |
| --- | --- |
| Hero | 0.30 |
| Sapstone | 0.44 |
| RootLeft | 0.42 |
| RootRight | 0.43 |
| LeafClump | 0.08 |
| Base, Rock | 0.0 |

A stronger height ramp on the egg failed the check (0.81), so the egg's darker foot is left to the lighting.

**Finish** (roughness): roots 0.9 / 0.92, base 0.95, rocks 0.9 / 0.88, sapstone 0.55 / 0.6, leaves 0.8 with
FOLIAGE_SPEC.

## Stage 5: Lighting

Skipped (decision 8): no emissive key and no light.

Studio note (Requires Manual Validation): under the game's sun, check that:
- the soft-green egg stays apart from the olive-lime leaves;
- the roots stay clearly warmer than the stone;
- the boulder tops read greyer than the base.

## Stage 6: VFX

Skipped (decision 8): the sheet shows no glow, sparkle, dust or particles, so there are no sockets. The renders use
`vfx=True`, with nothing to realise.

## Modeller's measurements

The comparison renders are `f34_sheet (0, 13)`, `r34_sheet (-40, 15)`, `side_sheet (90, 10)`, `rear_sheet (180, 10)`
and `top_sheet (0, 50)`, all with a 3x lens. `m029.measure()` applies the study's masks to both the sheet and the
render. The table gives sheet / ours for each value; the shares are percentages.

| View | W : H | Leaves | Sapstone | Root | Stone | Top-profile error (mean / max) |
| --- | --- | --- | --- | --- | --- | --- |
| f34 | 1.473 / 1.546 | 15.2 / 13.0 | 15.1 / 13.7 | 46.1 / 46.9 | 23.7 / 26.4 | 0.057 / 0.19 |
| r34 | 1.297 / 1.179 | 19.5 / 13.8 | 11.5 / 8.6 | 45.6 / 52.7 | 23.4 / 24.9 | 0.084 / 0.19 |
| side | 1.164 / 1.128 | 21.0 / 2.5 | 13.0 / 9.8 | 48.8 / 41.7 | 17.2 / 46.1 | 0.21 / 0.64 |
| rear | 1.337 / 1.347 | 22.3 / 13.8 | 12.3 / 13.4 | 36.5 / 40.1 | 28.9 / 32.6 | 0.086 / 0.36 |
| top | 1.141 / 1.385 | 18.1 / 10.0 | 13.3 / 9.1 | 40.1 / 40.3 | 28.5 / 40.7 | 0.074 / 0.17 |

The f34 egg centre is at (.574, .405) against the sheet's (.597, .418).

**Bark relief** (`m029.bark_relief()`): rays square to the centre line in 2 deg steps, counting only this root's own
surface.

| Station | Creases (depth >= 0.06) | Depths | min / median | Spread (max - min) / 2 |
| --- | --- | --- | --- | --- |
| L z 1.5 | 2 | 0.21, 0.15 | 0.83 | 0.38 |
| L z 2.5 | 3 | 0.23, 0.11, 0.20 | 0.86 | 0.31 |
| L z 3.5 | 3 | 0.23, 0.12, 0.15 | 0.81 | 0.17 |
| R z 2.0 | 3 | 0.09, 0.09, 0.21 | 0.77 | 0.19 |
| R z 3.0 | 3 | 0.14, 0.10, 0.16 | 0.79 | 0.19 |

**Knots** (mean radius at least 12 % over the minima on both sides):
- L: s .18-.23 (1.27), .43 (1.15), .66 (1.16).
- R: s .17 (1.36), .34 (1.39), .68 (1.19), .91 (1.26).

## Modeller's notes for the verifier

- **How to measure:** run `m029.measure()` and `m029.bark_relief()` after `m029.build()`. The renders are in this
  folder. The hero camera is `f34_sheet`; the kit front34, rear34 and top views are self-consistency only (spec 3).
- **Known misses:**
  - **r34:** W : H 1.18 (target 1.22-1.38) and a root share of 52.7 (+7). From (-40, 15), L's leg covers more of the
    egg's left than the sheet's r34 drawing does. The sheet's r34 inner fan is not modelled (decision 4).
  - **Side cell:** it is a redraw (spec 3.3). From +X the right fan is edge-on (leaves 2.5 %) and the base floor fills
    the view.
  - **Top cell:** a perspective drawing; its W : H is not chased.
  - **See-through gap:** the gap under the crest (spec 3.11) does not show.
  - **L at z 1.5:** 2 creases, not 3; the spur fuses over the third there.
  - **f34 W : H:** 1.546, which is 0.006 over the 1.54 limit.
- **Leaf fans:** they are upright hands of thick hexagonal kites. In places the overlapping leaves still read as a dense
  cluster rather than the four or five clean, separate blades drawn on the sheet.
- **Egg:** it sits in the arch's shadow in the studio, so its rendered lit quartile is darker than the sheet's.
- **Rock part:** a single 42-tri boulder (the big front-left one).

## Stage 7 — Verification (round 1)

Independent verifier, 2026-10-29. Read-only: a background session on port 9882 with
`art/blender/assets/kit/wip/M029_verify.blend`, never saved, and `build()` not called. Fresh renders went to
the scratchpad (`v029_renders/M029/`) through `m029.render_views()` with `kit_models.MODEL_RENDERS` redirected, so this
folder's renders were not touched. Comparisons use the study's masks on both images, plus tight-cropped
side-by-sides (`v029_cmp/t_*.png`).

**Verdict: FAIL, 6/10.** The technical side is clean, and the colours mostly match the sheet. Two of the sheet's
defining reads don't match: the root arch's relation to the egg, and the leaf fans.

### Re-measured (all objects; `M.audit` plus my own checks)

| Object | Tris | Size (W x D x H) | Shells | NM edges / verts | Boundary | Self-hits | Inverted / interior | Min corner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SapstoneRootArch | 2350 / 4000 | 9.92 x 7.61 x 6.10 (target 9.9 x 7.6 x 6.2: within) | 1 | 0 / 0 | 0 | 0 | 0 / 0 | 5.01 deg |
| ...Base | 464 | 9.31 x 7.24 x 0.78 | 1 | 0 / 0 | 0 | 0 | 0 / 0 | 5.09 |
| ...Rock | 42 | 1.78 x 1.38 x 1.45 | 1 | 0 / 0 | 0 | 0 | 0 / 0 | 10.6 |
| ...Sapstone | 80 | 2.63 x 2.45 x 3.38 (2.65 x 2.45 x 3.45) | 1 | 0 / 0 | 0 | 0 | 0 / 0 | 38.7 |
| ...RootLeft | 388 | 8.06 x 3.00 x 6.10 | 1 | 0 / 0 | 0 | 0 | 0 / 0 | 6.09 |
| ...RootRight | 338 | 6.55 x 3.21 x 5.78 | 1 | 0 / 0 | 0 | 0 | 0 / 0 | 9.18 |
| ...LeafClump | 316 | 3.99 x 2.86 x 2.73 | 1 | 0 / 0 | 0 | 0 | 0 / 0 | 5.2 |

Every object also has:
- no n-gons, wire edges, loose or duplicate verts, or zero-area faces;
- consistent winding and outward normals (signed volume, plus ray-parity tests on every face);
- no custom normals and no modifiers;
- rotation 0 and scale 1, with the origin at the bottom centre (bbox offset 0, 0, 0);
- a `Tint` colour attribute.

The hero is one shell with the sapstone united (decision 6), and `K.check` reports no problems.
- **UV:** one `UVMap` per object; 0 overlaps and 0 flips; gap 0.016 and border 0.008; density 1.0 / 1.0 / 1.0; conformal
  stretch p95 1.02-1.04; the hero has 371 islands at 33.6 texels per stud.
- **Materials:** Principled, no emission or metal. Roughness is 0.9 on roots, 0.95 on base, 0.55 on sapstone and 0.8
  on leaves. Faces take blend steps of 25 / 50 / 75 %.
- **Facing correlation:** hero 0.30, sapstone 0.44, roots 0.42 / 0.43, leaf clump 0.08 (all under 0.5), so nothing is
  coloured by facing.
- **Bark relief** (`bark_relief()`, re-run):
  - L at z 1.5 / 2.5 / 3.5: 2 / 3 / 3 creases, min / median 0.83 / 0.86 / 0.81, spread 0.38 / 0.31 / 0.17;
  - R at z 2.0 / 3.0: 3 / 3 creases, 0.77 / 0.79, spread 0.19 / 0.19;
  - knots: L at s .18, .23, .43, .66; R at .09, .17, .34, .68, .86, .91.

  Everything passes except L at z 1.5 (2 creases, not 3).

### Views against the sheet (`measure()` on my renders; sheet / ours)

| View | W : H | Leaves | Sapstone | Root | Stone | Top error mean / max |
| --- | --- | --- | --- | --- | --- | --- |
| f34 | 1.473 / 1.546 | 15.2 / 13.0 | 15.1 / 13.7 | 46.1 / 46.9 | 23.7 / 26.4 | 0.057 / 0.19 |
| r34 | 1.297 / 1.179 | 19.5 / 13.8 | 11.5 / 8.6 | 45.6 / 52.7 | 23.4 / 24.9 | 0.084 / 0.19 |
| side | 1.164 / 1.128 | 21.0 / 2.5 | 13.0 / 9.8 | 48.8 / 41.7 | 17.3 / 46.1 | 0.21 / 0.64 |
| rear | 1.337 / 1.347 | 22.3 / **13.8** (-8.5, tolerance +-6) | 12.3 / 13.4 | 36.5 / 40.2 | 28.9 / 32.6 | 0.086 / 0.36 |
| top | 1.141 / 1.385 | 18.1 / 10.0 | 13.3 / 9.1 | 40.1 / 40.3 | 28.6 / 40.7 | 0.074 / 0.17 |

**f34 root runs** (f, sheet / ours):

| h | Sheet | Ours |
| --- | --- | --- |
| .3 | L .12-.46 | L .09-.39 |
| .4 | L .17-.47 | L .15-.40 |
| .5 | L .24-.47, R .73-.84 | L .19-.41, R .70-.82 |
| .6 | L .27-.50 | L .24-.44 |
| .7 | L .30-.56, R .68-.75 | L .27-.46, R .53-.77 |

Other f34 measurements:
- **Egg:** f .47-.73 / .45-.70, centre (.597, .418) / (.574, .405).
- **Background inside the arch box** (f .35-.80, h .20-.85): sheet 2.1 %, ours **11.5 %**.
- **Right leaf fan:** sheet f .71-1.00 (143 px), ours **f .75-.90 (68 px)**. Top profile at f .90 / .95 / 1.0: sheet .63 /
  .47 / .40, ours .44 / .32 / .31.
- **r34 L leg width at h .5:** sheet 0.30 W, ours 0.23 W.

### Colours (sheet / ours, same masks)

| Region | Median | Lit quartile | Shade quartile |
| --- | --- | --- | --- |
| Roots, f34 | #A16942 / #9E643F (3, 5, 3) | #D08F5E / #CD8555 (3, 10, 9) | #6C4426 / #754B30 (9, 7, 10) |
| Stone, f34 | #796256 / #746058 (5, 2, 2) | #997F73 / #93817A (6, 2, 7) | #4B3E36 / #50443E (5, 6, 8) |
| Sapstone, f34 | #699850 / #65924C (4, 6, 4) | **#C4E986 / #8CC06B (56, 41, 27)** | #446634 / #486938 (4, 3, 4) |
| Leaves, f34 | #6D7F07 / #6E8210 (1, 3, 9) | #AEC022 / #9BB21B (19, 14, 7) | #455202 / #5A6A08 (21, 24, 6) |
| Root L part / exploded | #A16640 / #A66E47 (5, 8, 7) | thirds bottom -> top: #965E3A -> #C78152 / #A1683F -> #AF744B | |
| Sapstone part / exploded | #72A357 / #70A660 (2, 3, 9) | #91C972 / #A4D67E (19, 13, 12) | thirds #64924C -> #91C36D / #59894F -> #99CF78 |
| Leaf part / exploded L | **#5F700B / #74870D (21, 23, 2)** | #8CA11A / #9EB21D | thirds #45530B -> #7E9217 / #64750C -> #89A018 |
| Rock part / exploded rock | #70615C / #776359 (7, 2, 3) | #8B7771 / #A58C7F (26, 21, 14) | |

- **Two greens:** sapstone hue 98.6, sat 0.48; leaves hue 70.5, sat 0.88. They stay apart.
- **Root vs stone:** root sat 0.60 against stone sat 0.24, so the gap holds.
- **f34 root height bands, bottom -> top:**
  - sheet #845532 #915F39 #A26941 #AB7248 #C88755;
  - ours #955E3A #955F3B #A76B43 **#955F3C** #C98252.

  The top band is +52 in R over the bottom (target at least 40), but band 4 is darker than band 3, so the ramp isn't
  monotonic.

### Blockers

1. **The arch stands open instead of gripping the egg, and the two roots don't read as twisting together.** This is the
   model's defining read.

   What's wrong:
   - In the f34, L's inner edge sits 0.06-0.10 W left of the sheet at every height (h .3-.7: .39 / .40 / .41 / .44 /
     .46 against .46 / .47 / .47 / .50 / .56). That leaves a strip of daylight about 0.4 stud wide between L's leg
     and the egg, and more above the egg's right shoulder. The arch box is 11.5 % background against 2.1 %.
   - At h .7, L's run ends at .46 against the sheet's .56: the crest bends over too high and too thin.
   - R's top end shows as a small knob (f34) and as a separate log end sticking out to the left (r34, top), not as the
     broad hump that stands behind L's crest across f .30-.54.
   - The club end curls under into a horizontal shelf with a dark slot below it (f34, junction close-up). The sheet
     shows a smooth, thick down-bend resting on R.
   - From the r34 the leg is too thin (0.23 W against 0.30): the buttress ellipse is 1.5 : 1 along X.

   Fix in `ROOTS`:
   - **L, ctrl 3-5:** move right by about 0.45 X, to (-1.6, -1.3, 1.57), (-1.0, -1.1, 2.91) and (-0.4, -0.9, 4.2).
     Then L's inner flank meets the egg in the f34 (0-0.05 projected gap) and its outer edge lands at f .12 / .24 /
     .30 at h .3 / .5 / .7.
   - **L, crest:** lower the start of the bend (ctrl (-0.3, -0.75, 5.05) -> about (0.0, -0.75, 4.85)) and raise the
     crest diameters to 1.8-1.9, so L's run at h .7 reaches f ~ .56.
   - **L, cross-section:** cut the ellipse to about 1.2 : 1, or give the leg about 2.2 of depth in Y at z 2-4, so the
     r34 leg is 0.28-0.32 W wide.
   - **R's top end:** make it a broad domed hump about Ø 1.6 at about (-0.6, 1.0, 5.5), behind L's crest. Its top
     should show level with or just above the crest at f .30-.54, and no end cap should be visible from the r34 or the
     top view.
   - **R's descent:** pull it in against the egg's right flank: (1.9, 0.05, 4.05) -> about (1.75, 0.0, 4.0) and
     (2.6, -0.2, 3.4) -> about (2.4, -0.2, 3.45). Keep Ø about 1.3.
   - **Club end:** replace the curl-under ((2.45, -0.5, 4.65), (2.6, -0.48, 4.1)) with a smooth down-bend that
     overlaps R's shoulder by about 0.3. No horizontal ledge.

   Re-check:
   - f34 L runs within +-0.05 of the sheet;
   - background in the arch box at most 4 %;
   - the r34 W : H in 1.22-1.38 (now 1.18) and its root share within +-5 (now +7.1).

2. **The leaf fans don't read as the sheet's big, separate kite blades spread like a hand of cards.**

   What's wrong:
   - The left fan reads as a dense, spiky, overlapping cluster.
   - The right fan sits mostly behind R's leg (68 px wide against 143) and doesn't reach out to the right (top profile
     at f .90-1.0 is .44 / .32 / .31 against .63 / .47 / .40).
   - The rear leaf share is 13.8 against 22.3 (fails +-6).
   - The LeafClump part reads as a low agave rosette, with its outer leaves near horizontal. Its height : span is
     **0.68**; the spec target is at least 0.9, and the exploded fan is an upright V.

   Fix in `FANS`, `CLUMP` and `RIDGE` / `KEEL`:
   - **Right fan hub:** move it to R's outer back flank, about (3.6, 0.0, 2.2).
   - **Right fan leaves:** use spec 2.3's set, (yaw, pitch, L) = (-8, -18, 2.3), (12, 15, 2.35), (38, 45, 2.45),
     (68, 72, 2.6). The current lengths of 1.65 and 1.9 are too short, so the lowest tip should reach X ~ 4.9 at
     z ~ 2.3.
   - **Left fan hub:** move it about 0.35 further to -X, so each blade clears the buttress.
   - **Both fans:** raise `FAN_STAGGER` from 0.12 to about 0.25, so the blades separate in depth.
   - **Ridges:** raise the front ridge to about 0.11 L and the keel to about 0.08 L, so each blade has a crisp lit half
     and dark half as drawn.
   - **Part:** set every pitch to at least 35 deg (for example 40-85 deg), so H : span is at least 0.9 and the clump
     reads as the exploded upright fan.

   Re-check:
   - f34 right-fan component at f .71-1.00 +-0.04;
   - leaf shares within +-4 (f34) and +-6 (rear, r34);
   - 4-5 individually countable blades per fan in the f34.

### Minors

1. **f34 W : H** is 1.546, against a limit of 1.54. It should come back in once the fans spread outward rather than
   upward.
2. **The egg's lit facets are dull.** The lit quartile is #8CC06B against #C4E986 (56, 41, 27), and the part's top
   third is #91C36D against #99CF78.
   - Lighten `sap_light` by about x1.15 linear and widen its band down to t 0.5.
   - Keep the facing correlation under 0.5 (it is 0.44 now, so it has little room).
3. **The leaves are darker than the sheet** in the part shot: median #5F700B against #74870D, and the hub band #45530B
   against #64750C. In the f34 the shade quartile is 21-24 lighter than the sheet (a weak lit/dark split). Raise
   `leaf_base` and `leaf` by about x1.2, and the ridge change in blocker 2 sharpens the split.
4. **The root height ramp is not monotonic** in the f34: band 4 is #955F3C against the sheet's #AB7248. The root L part's
   top third (#C78152) is about 24 lighter than the exploded's (#AF744B). Ease `root_light` slightly and extend its
   band lower (z 3.3-5.3).
5. **The base is a thin plate with small rim studs.** The sheet's exploded and base close-up show a chunkier slab front
   lip and broad fused rim lumps. Raise the slab's outer ring to about 0.35 at the edge, and make the rim lumps 1.4-1.8
   wide and 0.35-0.45 proud. Optional.
6. **The front boulders read smaller than the sheet's.** The big front-left one is about 0.13 W against 0.19 W. Consider
   about x1.2 on the front-left and front-mid boulders.
7. **Bark facets** come out as many small, crumpled triangles rather than the sheet's long facets (1-2 studs) separated
   by crisp grooves. L at z 1.5 has 2 creases, not 3. Consider a step of about 0.9 on straight runs and less per-vertex
   jitter (0.06 -> 0.03).
8. **The side cell** is a known miss (spec 3.3): from +X the base dominates and the right fan is edge-on (leaves
   2.5 %). The top cell's W : H is not chased (3.5). The see-through gap (3.11) doesn't show. All three are accepted
   per the spec.

## Round 2 fixes (modeller)

Fresh modeller, 2026-10-29. Background session on port 9882 with `art/blender/assets/kit/wip/M029.blend` (saved after
the final build). All changes are in `m029.py`; `build()` runs in about 45 s (geometry about 25 s), fixed seeds.

### Measuring

- New `m029.arch_stats()` / `m029.arch_measure()` reproduce the round-1 verifier's arch reads on the sheet and our
  `*_sheet` renders:
  - root runs at h .3-.7;
  - the background share in the arch box (f .35-.80, h .20-.85);
  - the right fan's extent: the widest contiguous run of columns right of f .6 that hold at least 3 leaf pixels. On
    the sheet this gives exactly the verifier's .71-1.00, 143 px;
  - the widest root run at h .5.

  On the round-1 renders it gave 11.6 % background (verifier 11.5) and the same runs.
- **Mask change:** `_classes` now also counts the studio's warm-grey ground shadow (hue 30-70, sat < 0.11, value
  > 0.62) as background, as the sheet's soft shadow already is. Before, our shadow counted as stone and stretched
  our f34 bbox to the right, which is part of why round 1 saw the right fan end at f .90. All numbers below use it.
- `bark_relief()` also returns the crease angles.

### Blocker 1: the arch and the two roots

Changes in `ROOTS`:
- **L's leg and crest:**
  - control points 3-5 moved 0.45 right, to (-1.6, -1.3, 1.57), (-1.0, -1.1, 2.91) and (-0.4, -0.9, 4.2);
  - the crest bend starts at (0.0, -0.75, 4.85), with diameters 1.9 / 1.85 / 1.75;
  - the foot ellipse is 1.2 : 1 (was 1.5), and the leg diameters are 2.45 / 2.15 / 1.95 (were 2.35 / 1.95 / 1.75);
  - the club knot is gone.
- **L's end:**
  - The curl-under is replaced by a smooth down-bend: (1.35, -0.5, 5.1), (1.8, -0.45, 4.5), (2.08, -0.4, 3.8),
    (2.32, -0.35, 3.2), with diameters 1.75 down to 0.8.
  - It comes down in front of R's shoulder and tapers into it. Its end dome is buried in R.
  - L stays in front of R where they cross (spec 2.2).
  - No shelf or slot shows in the f34 or in the junction close-up.
- **R's top end:**
  - It is a broad hump, Ø 1.6 at about (-0.45, 0.75, 5.3), standing behind L's crest.
  - Its end dives into the back of L's leg at (-1.1, -0.55, 3.8), so no log end shows.
  - The hump path uses 6 points for an even bend. A tighter bend folded its inner side (6-7 self-hits).
  - The back half of the hump keeps the plain mid brown: crest light is capped at 25 % where `y > 0.2` and
    `x < 0.5`. So the two roots read apart where they cross, as drawn.
- **R's descent:**
  - It is pulled in against the egg, to (1.62, 0.0, 3.95) and (2.28, -0.2, 3.4).
  - It is thicker at the shoulder (1.55 / 1.5 / 1.4).
  - The lower leg moved 0.06-0.18 left, to (2.95, -0.4, 2.74), (3.32, -0.6, 2.09) and (3.68, -0.8, 1.45), with
    diameters 1.3 / 1.3 / 1.15.
- **Egg:**
  - `SAP_C` moved 1.3 -> 1.18, so L hugs it.
  - H went 3.45 -> 3.65 (3.57 after the seat), with fuller shoulders in `SAP_PROFILE`.
  - The f34 egg top is now at h .66 (sheet .68). Its centre is (.605, .396) against the sheet's (.597, .418).

| f34 L run (f) | Sheet | Round 1 | Round 2 | Inner edge delta |
| --- | --- | --- | --- | --- |
| h .3 | .12-.46 | .09-.39 | .13-.47 | +.01 |
| h .4 | .17-.47 | .15-.40 | .21-.48 | +.01 |
| h .5 | .24-.46 | .19-.41 | .26-.50 | +.04 |
| h .6 | .27-.50 | .24-.44 | .30-.53 | +.03 |
| h .7 | .30-.56 | .27-.46 | .32-.76 (merged) | see below |

- **h .7 row:** it runs on from L into R's shoulder, which shows under the crest (root class). The sheet's opening
  shows two small gaps there instead, so L's own inner edge can't be separated in that row.
- **Arch-box background:** 3.2 % (sheet 2.1, round 1 11.5; target at most about 4).
- **r34:**
  - W : H is 1.165 (round 1 1.179, target 1.22-1.38): **not met**.
  - Root share is 49.5 (sheet 45.7, within +-5; round 1 52.7).
  - The widest root run at h .5 is 0.27 W (sheet 0.30, round 1 0.23).
  - Why the width falls short: from (-40, 15) the width is set by the base and boulders on the left and by R's foot
    on the right, and the hero is narrower than the sheet's drawing. The sheet shows L's buttress at the far left
    (spec 3.2: its r34 reads nearer -20 to -25 deg).
  - L's leg now hugs the egg in the f34, so from -40 it covers more of the egg (sapstone share 4.4 against 11.5). The
    two cameras pull against each other.
- **f34:** W : H is 1.418 (sheet 1.473, limit <= 1.54). The top-profile error (mean / max) is 0.035 / 0.19 (round 1
  0.057 / 0.19).

### Blocker 2: the leaf fans

- **Both fans:**
  - Each fan grows from a fixed `origin` just inside its root; FAN_INFO reports how deep the origin is sunk.
  - Each has 4 kite blades: three big ones about 45 deg apart as drawn, and a fourth half-hidden.
  - The blades are stacked `FAN_STAGGER` 0.25 apart, with the lower blades in front, as on the sheet. Before, the
    upright blade was in front and hid the others.
- **Left fan:** origin (-2.2, -0.55, 2.3), leaves (175, -12, 2.95), (165, 34, 2.75), (130, 58, 2.3) and
  (155, 82, 2.8). The tips land on the sheet's (-4.9, 1.75), (-4.25, 3.7) and (-2.8, 4.9).
- **Right fan:**
  - Origin (3.5, -0.1, 2.5), on R's outer back flank.
  - Leaves (0, -14, 1.5), (20, 42, 1.75) and (45, 60, 1.8).
  - The upright blade grows from behind R's shoulder, through a new optional 4th value: a per-leaf base offset.
  - The lowest tip is at X 4.95 (the W limit).
- **Blade shape:**
  - Width is now set per fan (`w`): 0.56 of L, against the global 0.48, for the sheet's broad kites.
  - The front ridge is 0.11 L and the back keel 0.08 L.
- **f34:**
  - 4 separate blades can be counted in each fan (close-ups `o_lfan` / `o_rfan`).
  - The right fan runs f **.76**-1.00, 100 px, against the sheet's .71-1.00, 143 px (round 1 .75-.90, 64 px).
  - Its left end is .01 outside the +-.04 target, because L's down-bend hides the base of the upright blade.
- **Leaf shares (sheet / ours):**
  - f34: 15.2 / 15.9;
  - rear: 22.3 / **16.5** (-5.8, within +-6; round 1 13.8);
  - r34: 19.5 / 15.4 (-4.1).
- **LeafClump part:** the pitches are now 51-85 deg (were 22-82), and H : span is **0.94** (round 1 0.68).

### Minors

1. **f34 W : H:** 1.418, within the 1.54 limit.
2. **Sapstone:**
   - `sap_light` x1.15, then the sap keys x(1.2-1.25, 1.2, 1.1) in calibration; the light band now starts at t 0.5.
   - f34 median / lit / shade: ours #659049 / #91C767 / #4C6D39, sheet #699850 / #C4E986 / #446634.
   - The egg's lit facets are still darker than the sheet's near-white, because the arch shades the egg in our studio.
   - Facing correlation is 0.41 (< 0.5).
3. **Leaves:**
   - `leaf` and `leaf_base` x1.2; `leaf_tip` x1.28.
   - f34 median / lit / shade: ours #74890D / #A5BE18 / #627508, sheet #6D7F07 / #AEC022 / #455202.
   - The shade side is still lighter than the sheet's, because the studio key lights the back of the left fan.
4. **Root height ramp:**
   - f34 bands, bottom -> top: ours #8A5838, #8E5A38, #A96C43, **#9C633D**, #CB8455; sheet #845532, #915F39,
     #A26941, #AB7248, #C88755.
   - The bottom three bands now ramp up, and the top band is +65 in R over the bottom.
   - Band 4 is still darker than band 3. It is the crest's underside and the arch interior, in shadow. Two tries
     didn't move it: a steeper crest ramp (crest light over z 3.5 -> 4.6), and dropping the section-underside
     darkening on the crest (z > 3.5). So the darkness comes from the lighting, not the paint.
   - Changes made: `ROOT_DARK` x0.86 (#664125), foot field (0.1, 0.36), and `root_light` eased to #A46F49.
   - A world-height foot field was tried and reverted: it failed the facing check (RootLeft 0.53).
5. **Base:**
   - The outer bulge ring went up 0.25 -> 0.36, for a chunkier lip.
   - The rim lumps are 1.5-1.9 wide and 0.32-0.43 proud, with broader tops (`RIM_RINGS` top 0.75).
   - The base part is now 9.55 x 7.35 x 0.9.
6. **Boulders:**
   - Front-left and front-mid are x1.25, at (2.25, 1.9, 1.75) and (1.7, 1.5, 1.4).
   - Right-mid is now (1.3, 1.15, 1.15), which also closes the lower right of the arch box.
   - The Rock part is 2.23 x 1.7 x 1.75.
7. **Bark:** `STEP` 0.68 -> 0.9 and per-vertex radius jitter 0.06 -> 0.03, for longer facets and crisper grooves.
   `bark_relief` gives:

   | Station | Creases | Depths |
   | --- | --- | --- |
   | L z 1.5 | **2** | 0.29, 0.09 |
   | L z 2.5 | 3 | 0.23, 0.21 |
   | L z 3.5 | 3 | 0.26, 0.20 |
   | R z 2.0 | 3 | 0.14, 0.10, 0.21 |
   | R z 3.0 | **2** | 0.11, 0.17 |

   - **L at z 1.5:** the section leans about 40 deg, so its lower half (rays at 100-230 deg) runs into the floor and
     slab. Only 2 of its 3 grooves can be measured.
     - A foot-only 4th groove was tried and reverted: its minimum fell where a left-fan blade blocks the ray.
   - **R at z 3.0:** it lost one measurable crease because R now presses against the egg, so its inner rays hit the
     egg.
   - **Knots:** L at s .25 / .43 / .63; R at s .12-.21, .35, .49, .82 and .93.

### Checks (final build; `problems` empty)

| Object | Tris | Size (W x D x H) | Min corner | UV islands | Stretch p95 |
| --- | --- | --- | --- | --- | --- |
| SapstoneRootArch | 2566 / 4000 | 10.02 x 7.61 x 6.14 (target 9.9 / 7.6 / 6.2: within) | 5.0 | 400 | 1.01 |
| ...Base | 502 | 9.55 x 7.35 x 0.90 | 5.08 | 75 | 1.03 |
| ...Rock | 42 | 2.23 x 1.70 x 1.75 | 10.7 | 9 | 1.02 |
| ...Sapstone | 80 | 2.65 x 2.45 x 3.57 | 39.5 | 9 | 1.06 |
| ...RootLeft | 442 | 7.18 x 3.23 x 6.12 | 5.03 | 49 | 1.01 |
| ...RootRight | 498 | 6.84 x 2.98 x 6.14 | 6.89 | 72 | 1.03 |
| ...LeafClump | 414 | 2.86 x 2.28 x 2.68 | 5.0 | 74 | 1.01 |

Every object also has:
- 1 shell;
- 0 non-manifold edges and verts, 0 boundary, wire or loose elements, and no zero-area faces, n-gons or duplicate
  verts;
- outward normals and 0 self-intersections;
- rotation 0, scale 1, no modifiers and a `Tint` attribute;
- clean UVs: 0 overlaps and 0 flips, gap 0.016, border 0.008, density 1.0.

`K.check` is clean.
- **Facing correlation:** hero 0.09, RootLeft 0.33, RootRight 0.18, Sapstone 0.41, LeafClump 0.20.
- **The two greens stay apart:** leaves hue 70 / sat 0.91, sapstone hue 96 / sat 0.49.
- **Root vs stone:** sat 0.60 against 0.27.

**Final `PALETTE`:**

| Key | Hex | Key | Hex |
| --- | --- | --- | --- |
| root | #93623E | rock_light | #877B76 |
| root_dark | #664125 | sap | #70A258 |
| root_light | #A46F49 | sap_light | #96CB6B |
| base | #69564C | sap_dark | #4E783E |
| base_dark | #5B4A40 | leaf | #637708 |
| rock | #695954 | leaf_tip | #8EA618 |
| | | leaf_base | #50620A |

**f34 medians (sheet / ours):**

| Region | Sheet | Ours |
| --- | --- | --- |
| Roots | #A16942 | #A36841 |
| Stone | #796256 | #796458 |
| Sapstone | #699850 | #659049 |
| Leaves | #6D7F07 | #74890D |

### Known misses, for the verifier

- **r34 W : H** is 1.165, against 1.22-1.38. This is a camera and drawing mismatch (spec 3.2), and the f34 hug the
  verifier asked for makes L hide the egg from -40.
- **The f34 h .7 run** merges with R's shoulder under the crest.
- **The right fan's left end** is at f .76 (target .71 +- .04).
- **Root band 4** is darker than band 3 (the crest underside in shadow).
- **Bark:** L at z 1.5 and R at z 3.0 each have 2 measurable creases. Both are occluded, as explained above.
- **Accepted per the spec:**
  - the side cell is still the known miss;
  - the parts' exploded shapes follow the hero (decision 3);
  - the LeafClump is a 7-leaf rosette, not the exploded drawing's planar V.

## Stage 7 — Verification (round 2)

Independent verifier (not the round-1 verifier, no other stage), 2026-10-29. Read-only: background session on port 9882
with `art/blender/assets/kit/wip/M029_verify.blend`, never saved, `build()` not called, session stopped at the end.
Fresh renders went to the scratchpad through `m029.render_views()` with `kit_models.MODEL_RENDERS` redirected. They are
pixel-identical to this folder's `*_sheet` and part renders (mean difference 0.000/255), so the verify file is the
current builder's output. Side-by-sides use the study's masks on tight crops of both images.

**Verdict: PASS, 8/10.** Both round-1 blockers are fixed to their targets, or to within 0.01 of them. The technical
side is clean. The remaining misses are camera/drawing mismatches, studio lighting, or small reads, and none is
broken.

### Re-measured (own scripts: `M.audit`, BVH self-overlap, ray-parity inversion, corner angles, `M.uv_stats`, `baked_shading`)

| Object | Tris | Size (W x D x H) | Shells | NM edges / verts | Boundary | Self-hits | Inverted | Min corner | UV islands / overlaps / flips | Facing corr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SapstoneRootArch | 2566 / 4000 | 10.02 x 7.61 x 6.14 (target 9.9 / 7.6 / 6.2 +-0.4 / 0.4 / 0.25: within) | 1 | 0 / 0 | 0 | 0 | 0 | 5.0 | 396 / 0 / 0 | 0.09 |
| ...Base | 502 | 9.55 x 7.35 x 0.90 | 1 | 0 / 0 | 0 | 0 | 0 | 5.08 | 75 / 0 / 0 | 0.0 |
| ...Rock | 42 | 2.23 x 1.70 x 1.75 | 1 | 0 / 0 | 0 | 0 | 0 | 10.7 | 9 / 0 / 0 | 0.0 |
| ...Sapstone | 80 | 2.65 x 2.45 x 3.57 | 1 | 0 / 0 | 0 | 0 | 0 | 39.5 | 9 / 0 / 0 | 0.41 |
| ...RootLeft | 442 | 7.18 x 3.23 x 6.12 | 1 | 0 / 0 | 0 | 0 | 0 | 5.03 | 49 / 0 / 0 | 0.34 |
| ...RootRight | 498 | 6.84 x 2.98 x 6.14 | 1 | 0 / 0 | 0 | 0 | 0 | 6.89 | 72 / 0 / 0 | 0.18 |
| ...LeafClump | 414 | 2.86 x 2.28 x 2.68 | 1 | 0 / 0 | 0 | 0 | 0 | 5.0 | 74 / 0 / 0 | 0.20 |

- **Every object also has:** no n-gons, wire edges, loose or duplicate verts, or zero-area faces; outward normals; no
  custom normals or modifiers; rotation 0 and scale 1; origin at the bottom centre (bbox offset 0, 0, 0); a CORNER
  `Tint` attribute.
- **UVs:** gap 0.016, border 0.008, density 1.0 / 1.0 / 1.0, conformal p95 1.01-1.06.
- **Kit checks:** `K.check` is empty, and every KITSTAT line is ok. The hero is one shell with the sapstone united
  (decision 6).
- **Facing:** all correlations are under 0.5, so nothing is coloured by facing.
- **The two greens stay apart:** f34 leaves #74890D (hue 70, sat 0.91) against sapstone #659049 (hue 96, sat 0.49).
- **Root against stone:** sat 0.60 against 0.27.

### Mask change (round-2 `_classes`): fair

The new rule (hue 30-70, sat < 0.11, value > 0.62 counts as background) was checked on both images:
- **Our renders:** it flips 1,699 px (f34) and 8,800-13,500 px (side, rear, top). Their medians are #BCB6AC and
  #A6A29A, the low-saturation warm grey of the studio ground shadow. Only 0-8 of the flipped pixels are enclosed by
  object pixels on all four sides.
- **The sheet:** it flips only 22-94 px per cell (pale highlight specks, under 0.1 %).
- **Stone is safe:** stone renders at hue 15-25, outside the 30-70 window, so lit stone isn't dropped.

### Round-1 blockers

**Blocker 1 (arch grips the egg; two roots): fixed.**

f34 L runs (f, sheet / ours):

| h | Sheet | Ours | Inner-edge delta |
| --- | --- | --- | --- |
| .3 | .12-.46 | .13-.47 | +.01 |
| .4 | .17-.47 | .21-.48 | +.01 |
| .5 | .24-.46 | .26-.50 | +.04 |
| .6 | .27-.50 | .30-.53 | +.03 |

- **Runs:** all four are within the +-.05 target.
- **Arch-box background:** 3.2 % (target <= 4, sheet 2.1, round 1 11.5). L's leg now sits against the egg in the
  side-by-side.
- **Club end:** a smooth, thick down-bend tapering onto R's shoulder, with no shelf or slot (`junc_cu`). It matches the
  junction close-up.
- **R's top end:** no log end shows in the r34 or the top view, and the crest reads as two lobes there.
- **r34:** root share 49.5 against 45.7 (within +-5). The widest root run at h .5 is 0.27 W against 0.30.

**Blocker 2 (leaf fans): fixed.**
- **f34 shares:** leaf 15.9 against 15.2 (+-4).
- **Rear share:** leaf 16.5 against 22.3 (-5.8, within +-6).
- **r34 share:** leaf 15.4 against 19.5 (-4.1, within +-6).
- **Right fan:** f .76-1.00, 100 px, against .71-1.00, 143 px. The left end misses the +-.04 target by .01 (round 1:
  .75-.90, 68 px).
- **Blades:** 4 separate kites can be counted in each fan in the f34, with a crisp lit half and dark half.
- **LeafClump:** H : span 0.94 (target >= 0.9; round 1 0.68).

### Remaining misses, judged

1. **r34 W : H 1.165 against 1.22-1.38: accept (camera, not model).** I rendered the hero at other azimuths with the
   same 3x lens and el 15:

   | Azimuth | W : H | Root | Sapstone | Top-error mean |
   | --- | --- | --- | --- | --- |
   | -20 | 1.303 | 46.5 | 9.1 | 0.035 |
   | -25 | 1.265 | 47.2 | 8.0 | 0.040 |
   | -30 | 1.237 | 47.9 | 6.8 | 0.045 |
   | -40 | 1.171 | 49.2 | 4.4 | 0.057 |

   At -20 the model matches the drawing (sheet 1.297 / 45.7 / 11.5). That confirms spec 3.2: the sheet's r34 is drawn
   nearer -20 to -25 deg, and the -40 camera (decision 9) is what misses. Optional: switch `SHEET_VIEWS["r34_sheet"]`
   to (-22, 15).
2. **f34 h .7 run merges (.32-.76): accept.** The sheet has L .30-.56, R's shoulder .58-.64 and R .68-.75, so the
   only difference is the two 0.02-0.04 W slivers of daylight, which are the see-through gap (spec 3.11, nice to have).
3. **Root band 4 is darker than band 3: accept (lighting).**
   - f34 bands, bottom -> top: ours #8A5838 #8E5A38 #A96C43 **#9B633D** #CB8455; sheet #845532 #915F39 #A26941
     #AB7248 #C88755.
   - Band 4 is off by (16, 15, 11). It is the crest underside and the arch interior, in the studio shadow.
   - Top minus bottom is +65 in R (target >= 40).
   - The paint ramp itself is monotonic. A world-height fix fails the facing check, as the modeller found.
4. **Bark stations: accept (the misses come from occlusion).** I checked them ray by ray.

   | Station | Creases | Finding |
   | --- | --- | --- |
   | L z 1.5 | 2 | Rays at 100-230 deg hit rock and base (radii 2.1-2.9), so the lower half can't be measured. |
   | R z 3.0 | 2 | Rays at 150-210 deg hit the sapstone, the egg contact blocker 1 asked for. Clear grooves at about 95 and 300 deg. |
   | L z 2.5 | 3 | The third crease is a real groove about 0.1 deep. The reported 0.67 is inflated by a leaf hit at 282 deg. |
   | L z 3.5 | 3 | The third crease is about 0.13 deep. |
   | R z 2.0 | 3 | |

   - **Knots:** L at s .25 / .43 / .63; R at s .12-.21, .35, .49, .82 and .93.
   - **Facets:** in the side-by-sides, long facets run along the limbs. They are a little softer than the sheet's
     crisply ridged bark.

### Views against the sheet (`measure()`; sheet / ours)

| View | W : H | Leaves | Sapstone | Root | Stone | Top error mean / max | Read |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | 1.473 / 1.418 | 15.2 / 15.9 | 15.1 / 12.9 | 46.1 / 43.9 | 23.6 / 27.4 | 0.035 / 0.19 | Matches: arch over the egg, L's leg on the left, crest flat at h .97-1.0, fans both sides, boulder ring. |
| r34 | 1.297 / 1.165 | 19.5 / 15.4 | 11.5 / 4.4 | 45.7 / 49.5 | 23.4 / 30.7 | 0.056 / 0.19 | Camera (above). The sheet's inner fan is not modelled (decision 4). |
| side | 1.158 / 1.031 | 21.0 / 2.9 | 13.1 / 10.1 | 48.8 / 47.4 | 17.2 / 39.7 | 0.164 / 0.66 | Known miss (spec 3.3, a redraw). |
| rear | 1.337 / 1.408 | 22.3 / 16.5 | 12.3 / 14.9 | 36.5 / 41.8 | 28.8 / 26.8 | 0.056 / 0.17 | Arch from behind, fans both sides. The egg shows more (the sheet hides it behind the unmodelled inner fan); sapstone centre f .40 against .47. |
| top | 1.141 / 1.32 | 18.1 / 15.0 | 13.3 / 7.0 | 40.1 / 45.5 | 28.5 / 32.6 | 0.085 / 0.21 | High front view (spec 3.5). L's crest now covers more of the egg from 50 deg. |

Other f34 measurements:
- **Egg centre:** (.605, .396) against (.597, .418).
- **Root top line:** within .05 at f .35-.90. At f .25 / .30 it is .48 / .60 against .53 / .77: R's hump doesn't
  stand out past L's crest at the upper left the way the sheet's does (minor 1).

### Colours (sheet / ours, same masks; difference in R, G, B)

| Region | Median | Lit quartile | Shade quartile |
| --- | --- | --- | --- |
| Roots, f34 | #A16942 / #A36841 (2, 1, 1) | #D08F5E / #D18756 (1, 8, 8) | #6C4426 / #7A4E31 (14, 10, 11) |
| Stone, f34 | #796256 / #7A6458 (1, 2, 2) | #987F73 / #988276 (0, 3, 3) | #4B3E36 / #56473E (11, 9, 8) |
| Sapstone, f34 | #699850 / #659049 (4, 8, 7) | #C4E986 / #91C767 (51, 34, 31) | #446634 / #4C6D39 (8, 7, 5) |
| Leaves, f34 | #6D7F07 / #74890D (7, 10, 6) | #AEC022 / #A5BE18 (9, 2, 10) | #455202 / #627508 (29, 35, 6) |
| Root L, part / exploded | #9B6342 / #A66E47 (11, 11, 5) | #D18756 / #BC7D50 | #7F5031 / #855635 |
| Root R, part / exploded | #B17249 / #935E38 (30, 20, 17) | #CF8656 / #CB8B5A | #784C30 / #6D472A |
| Sapstone, part / exploded | #80B65C / #71A660 (15, 16, 4) | #A4E175 / #A4D67E (0, 11, 9) | #639148 / #51844C |
| Leaf clump, part / exploded | #627509 / #74870D (18, 18, 4) | #9AB116 / #9EB21D (4, 1, 7) | #435205 / #506103 |

- **Egg lit quartile:** the f34 lit quartile is dull, but the part render's lit quartile matches the sheet (#A4E175
  against #A4D67E). The paint is right, and the f34 gap is the arch's studio shadow.
- **Egg render noise:** the f34 shows sample noise on the egg's shaded left half. That is studio render noise, not
  texture: the egg's Tint amplitude is 0.03, and the part render is clean.

### Items

No blockers.

Minors (optional, cheap):
1. **R's hump reads weakly at the upper left of the f34.** The root top is .60 against .77 at f .30. Fix: in `ROOTS`
   R, move the hump's end point about 0.5 further to -X and 0.2 up (currently diving into L at (-1.1, -0.55, 3.8)), so
   its top shows past L's crest at f .25-.35. Keep the 6-point bend that avoids self-hits.
2. **Right fan left end:** f .76 against .71 +- .04 (.01 out). Fix: move the right fan origin about 0.15 to -X, or
   give the upright blade a little more yaw to -X.
3. **r34 camera:** change `r34_sheet` to (-22, 15) so the comparison matches the drawing (measured above). This is
   documentation only.
4. **Egg slightly slim.** Exploded W : H is 0.81 and our part is 0.70-0.74 (2.65 x 3.57). Fix: `SAP_SIZE` W / D
   x1.05, if the f34 egg width allows.
5. **Leaf clump part about 18 darker** than the exploded clump (median). In the hero the leaves are 7-10 lighter than
   the sheet, so leave the keys and accept it.
6. **Root R part median about 25 lighter** than the exploded R (its crest band shows more from the parts camera).
   Cosmetic.
7. **Accepted, unchanged:**
   - band 4 (lighting);
   - the h .7 merge and the see-through gap (3.11);
   - the bark stations (occlusion);
   - the side cell (3.3);
   - the top cell (3.5);
   - the rear egg exposure, from the unmodelled inner fan (decision 4);
   - the egg lit quartile and the studio render noise;
   - the hero's UV island count, 396 (the spec says 400).
