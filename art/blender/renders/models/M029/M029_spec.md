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
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m029_study\`.
Run from that folder with
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\venv22\Scripts\python.exe`.
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
