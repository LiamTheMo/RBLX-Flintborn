# 036 Rock Cluster — spec

Reference: `art/blender/assets/references/036.png` (1024 × 1536 px). The sheet's title is "ROCK CLUSTER", with "39 /132"
at the top left, "FLINTBORN / INDIVIDUAL MODEL STUDY" at the top right and "PAGE 39/132" in the footer. INDEX.md row 36
calls it "Flintborn rock cluster model study" (the sheet's own page number, 39, is not the index number).
Builder: `art/blender/kit/mcp/m036.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7).

Sheet text:
- **Section headers:** "1. ASSEMBLED VIEWS", "2. ORTHOGRAPHIC VIEWS", "3. EXPLODED CONSTRUCTION",
  "4. CONSTRUCTION CLOSE-UPS", "5. MATERIAL PALETTE", "6. MODELING NOTES".
- **View labels:** "FRONT THREE-QUARTER VIEW", "REAR THREE-QUARTER VIEW", "FRONT VIEW", "SIDE VIEW", "REAR VIEW",
  "TOP VIEW".
- **Exploded labels:** "Rock A (tall, main)", "Rock B (medium)", "Rock C (medium)", "Rock D (small)", "Rock F (small)",
  "Foliage Cluster (reusable)", "Flower Cluster (reusable)". A sixth, unlabelled small rock sits in the middle (called
  **E** here); a pebble sits beside F. Dashed arrows drop each rock and cluster to the ground.
- **Close-ups:**
  - "ROCK / ROCK JUNCTION": "Rocks meet with simple contact surfaces (flat faces, no complex blend)."
  - "UNDERSIDE VIEW": "Flat bottoms for clean ground placement."
  - "ROCK THICKNESS / CROSS-SECTION": "Hollow, single-shell geometry (stylized). Consistent thickness. No internal
    detail." (see §3.8)
- **Material palette:** "Main Rock (large faces)", "Rock Shadow (facets)", "Moss / Leaves", "Leaf Highlight".
- **Modeling notes:**
  - "Built from three main rock meshes and smaller supporting rocks."
  - "Separate foliage and flower meshes (reusable)."
  - "Broad, flat-shaded faces — keep it chunky and readable."
  - "Simple, solid colors, no texture noise." (but see §3.10)
  - "Flat bottoms for stable placement on ground."
  - "Maintain consistent silhouettes across all views."
  - "Keep pivots at base center for easy placement."
  - "Reuse individual rock and foliage pieces for variations."
- **Game context:** an environment prop (a landmark rock group with dressing). The old W01 kit sheet already has a
  "Rock Cluster": `RockCluster` (19.0 W × 11.7 D × 10.7 H, 4174 tris, three boulders, passed round 3 at 7.5/10),
  `RockClusterA` (6.8 × 6.1 × 10.5), `RockClusterB`, `RockClusterC`, `RockClusterLinear`, `RockClusterCrescent`,
  `RockClusterTriangular`; M004 owns `ObsidianRockCluster` (§8). W01's builder (`art/blender/kit/mcp/w01.py`,
  `cluster_rock()`, `cluster_hero()`, `GABLE`/`BULK`/`DOME_LOW` rings, `herb_bush`, `flower5`, `place_mounds`,
  `TUFT_CAP`) and its goals file (`art/blender/renders/kit/W01/rock_cluster_goals.md`) are the nearest recipes; its
  open minors were "Rock C a little egg-like" and "moss caps sit as small tufts rather than draping".

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is
`#FBF7EE` (251, 247, 238), tolerance 12. The masks are `cls()` in `m.py` (HSV):
- **R, rock:** hue ≤ 45° or ≥ 190°, sat 0.03–0.42, v 0.22–0.985, and not G/F/B. Lit faces are warm peach (hue
  20–27°), shaded faces cool lavender (hue 300–350°, sat 0.04–0.06); both are R.
- **G, green:** hue 45–150°, sat ≥ 0.28, v ≥ 0.12. Moss caps and foliage; split by position (§1.2).
- **F, flower:** white petals (sat < 0.10, v ≥ 0.95) and yellow centres (hue 36–56°, sat ≥ 0.55, v ≥ 0.7). Under 1.5 %.
- **B, ground shadow:** neutral grey, sat < 0.03, v 0.45–0.95 (`#AEAEB0`–`#B8B8B8`). **Treated as background**: it is
  in no silhouette, profile or share below.
- **O, other:** dark creases, outlines and anti-aliasing; in silhouettes but not in the shares (3.0–3.6 %).

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m036_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14 with Pillow and numpy; no scipy, so `m.py` has
its own `label()`).
- **Helpers:** `m.py` (masks `cls()`, view boxes `V` and `X`, `preview()`, `label()`), `zoom.py` (crop + upscale),
  `grid.py` (crop + upscale with a labelled sheet-pixel grid).
- **Measurements:** `measure.py` → `measure_out.txt`, `bb.json` (silhouettes, shares, top/bottom profiles, width per
  height, R/G per fifth); `comps.py` → `comps_out.txt`, `comp_*.png` (rock components per view); `rocks.py` →
  `rocks_out.txt`, `facets_*.png` (per-rock widths per height and flat-facet segmentation); `greens.py` (green
  components per view); `profcmp.py` (profile comparisons, flipped and not); `proj.py`, `layout.py` (plan layout
  projected to each camera); `flowers.py`.
- **Colour:** `samp.py` → `samp_out.txt` (swatches; medians, lit and shade quartiles and deciles per region).
- **Names:** `blendall.py`, `names.py` (every sheet and wip `.blend`, zstd-decompressed).
- **Crops:** `f34.png`, `r34.png`, `row2.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `cu.png`,
  `pal.png`; grids `g_f34.png`, `g_r34.png`, `g_front.png`, `g_side.png`, `g_rear.png`, `g_top.png`, `g_explA.png`,
  `g_under.png`; zooms `z_f34_AB.png` (A, B, C in the hero), `z_expl_rocks.png` (exploded A, B, C, E); mask previews
  `cls_*.png`.
- **To run the scripts on our renders:** point `R` (in `m.py`) at the render, set `P` to its background colour, set
  the boxes in `V` to the render cells, and re-run `measure.py`, `comps.py`, `rocks.py` (with new per-rock boxes) and
  `samp.py`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (an environment prop: a landmark rock group). Hero budget 4000 tris, each part under
  1000. The plan in §4.3 lands at about 2400–3200.
- **Overall read (check this first).** A **group of separate, big-faceted, warm grey-pink rocks**, each its own clear
  form:
  - **Rock A**, a tall faceted pillar-egg (about 1.45 × as tall as wide) at the back right of centre, with a lobed
    lime moss cap on its narrow sloping crown;
  - **Rock B**, a squat upright block (about as tall as wide) at the front left, with a broad sloping crown carrying a
    flat lobed moss mat and a small leaf sprig at its back right;
  - **Rock C**, a low faceted dome at the front right, bare;
  - **two more bare domes at the back** (G at the back right, H at the back left of centre), seen only in the rear,
    rear three-quarter, side and top views (§3.3);
  - **small rocks** round the foot: D at the far left, E at the front centre, F at the far right, plus three at the back
    and a pebble;
  - **chunky round-leaf clover clusters** tucked into every joint and round the foot, about seven with a white
    five-petal flower, and a tall stacked column of leaves between C and A on the right.
  - Hero shares (front three-quarter): rock 74.8 %, green 24.4 % (moss caps about 5, foliage about 19), flowers 0.8 %.
- **Focal silhouettes, in order:**
  1. A's tall crowned outline rising over the group: steep faceted sides, the crown a narrow sloping face at 0.91 of the
     front height, A's right flank stepping down to the right foliage column.
  2. B's blocky outline to the left: a near-vertical left flank, a broad flat crown at 0.59 of the height with the moss
     mat on it.
  3. C's low dome to the right at 0.41, overlapping A's foot.
  4. The foliage tufts at both ends (left tuft to h .41, right column to h .64) and the small rocks at the foot.
- **Target size: dressed 12.6 W × 10.8 D × 8.0 H studs (A's moss top); A's rock crown 7.3** (1.33 × the 5.5-stud
  character; moss top 1.45 ×). Tolerances: W ±0.5, D ±0.6, H ±0.3; each rock's W, D and H ±0.3. Decision §8.1.
  - **How it was derived.** The sheet has no character. Ratios are measured (§1.2): W : H 1.425 in the front cell, 1.433
    in the f34; D/W 0.86 (side cell 216 px against the front cell's 258 px; both cells are drawn at about the same
    scale, H 175 and 181 px); the top view gives W : D 1.081 but is drawn smaller and with perspective (§3.4). A
    camera elevation of about 8–12° adds about 0.8 stud of screen height (the crowns of B and C show as faces). Worked
    through in `layout.py`: with W 12.6 at 20.5 px/stud, the front cell's 181 px is 8.8 studs of screen height, of
    which about 0.8 is depth seen from above → A's moss top about 8.0, A's crown about 7.3 (0.91 of the screen height,
    as drawn).
  - **Why this size.** A main rock a little over head height (1.33 × the character), B about chest-to-head high (0.85
    ×), C waist-to-chest high (0.58 ×), small rocks shin high. It gives the kit a mid-size cluster next to W01's big
    `RockCluster` (19 W, A 10.5 tall) and M035's squat `MossyBoulder` (12.0 × 11.1 × 7.8, crown 6.4), rather than
    repeating either. At this size leaves are 0.45–0.6 long, flowers 0.4 across and small rocks 0.9–1.7 across, all
    reasonable against a 5.5-stud character.
- **Build frame:** front −Y, +X right, ground z 0, origin = the bbox bottom centre (stage 2 re-centres).

### 1.2 Measured views (`measure.py`, `comps.py`, `greens.py`)

| View (box) | Silhouette bbox (px) | W : H | Rock R | Green G | Flower F | Other O | px/stud (W 12.6) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (17,108,530,430) | 52–508 × 108–426 | 1.433 | 74.8 % | 24.4 % | 0.76 % | 3.6 % | 36.3 |
| Rear three-quarter (530,108,1007,430) | 551–977 × 122–424 | 1.409 | 75.1 % | 24.1 % | 0.74 % | 3.0 % | — (az 208, §3.2) |
| Front (17,512,283,708) | 17–274 × 523–703 | 1.425 | 73.3 % | 25.7 % | 1.04 % | 3.3 % | 20.5 |
| Side (285,512,511,708) | 295–510 × 527–701 | 1.234 (D : H) | 70.5 % | 28.1 % | 1.33 % | 3.3 % | 20.0 (D 10.8) |
| Rear (513,512,764,708) | 514–756 × 528–701 | 1.397 | 71.4 % | 27.1 % | 1.42 % | 3.3 % | 19.3 |
| Top (766,512,1007,708) | 787–973 × 529–701 | 1.081 (W : D) | 70.6 % | 28.8 % | 0.64 % | 4.4 % | 14.8 (drawn smaller) |
| Exploded (17,786,645,1248) | 32–617 × 786–1234 | 1.305 | 72.4 % | 25.0 % | 2.68 % | 5.3 % (incl. labels) | A 32, B 36, C 29 |

- Shares are of R + G + F; the ground shadow (B) is background. **Moss caps** (G on A's and B's crowns): front A cap 12 %
  and B cap 9 % of G (about 3.1 + 2.4 = 5.5 % of the silhouette); f34 10 % + 11 % of G (about 5.2 %); rear 14 % of G
  (A only, 3.8 %); side 15 % (A only, 4.2 %).
- **Verifier tolerance:** shares ±4 points (caps ±1.5, flowers ±0.5); positions ±0.06 of W/H unless stated.
- **R/G per fifth of the height (bottom → top):** f34 76/23 75/25 76/23 74/26 69/30; front 72/27 73/26 74/25 80/19 59/39;
  rear 75/23 68/31 65/33 94/5 48/50; side 56/43 77/21 67/33 100/0 51/48; r34 77/22 70/29 78/21 89/10 48/51. The top
  fifth is A's crown and its moss; the fourth fifth is nearly all bare A.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .28 | .32 | .42 | .44 | .54 | .65 | .69 | .69 | .69 | .75 | .86 | .95 | .99 | .99 | .94 | .89 | .76 | .66 | .57 | .43 | .24 |
| Front | .25 | .37 | .39 | .48 | .60 | .65 | .66 | .65 | .70 | .81 | .93 | .98 | .97 | .92 | .87 | .76 | .64 | .54 | .54 | .33 | .16 |
| r34 | .16 | .11 | .43 | .54 | .60 | .63 | .79 | .87 | .94 | .98 | .99 | .94 | .90 | .83 | .67 | .68 | .63 | .57 | .50 | .36 | .24 |
| Rear | .21 | .28 | .42 | .60 | .60 | .61 | .74 | .84 | .92 | .95 | .99 | .98 | .90 | .84 | .74 | .59 | .64 | .56 | .49 | .32 | .14 |
| Side | .17 | .21 | .34 | .42 | .54 | .53 | .65 | .81 | .92 | .97 | .98 | .95 | .86 | .77 | .59 | .49 | .40 | .30 | .00 | .00 | .15 |
| Top (h = back) | .36 | .24 | .61 | .82 | .87 | .95 | .95 | .97 | .91 | .98 | .99 | .98 | .95 | .95 | .95 | .97 | .95 | .93 | .90 | .82 | .62 |

- `profcmp.py` (41 samples): front against f34 mean 0.060 (max 0.219, at A's left edge where the f34 sits higher);
  rear against r34 0.044; r34 against f34 0.124, flipped 0.112; rear against front 0.074, flipped 0.100. So the f34 is
  the front drawing, the r34 is the rear drawing, and neither back cell is the front mirrored (§3.1–§3.3).
- The plateau at .65–.70 over f .25–.40 (front) is B's crown and moss; the peak at f .50–.65 is A's moss; the shoulder at
  .54–.64 over f .80–.90 is the right foliage column.

**Bottom profiles** (lowest silhouette pixel; the ends are foliage and small rocks):

```
f34    .28 .24 .13 .10 .08 .08 .05 .05 .05 .02 .01 .02 .01 .01 .02 .02 .04 .06 .12 .13 .21
front  .14 .12 .09 .07 .05 .04 .03 .04 .03 .01 .01 .02 .02 .03 .02 .03 .04 .07 .11 .10 .15
r34    .16 .10 .07 .03 .02 .03 .03 .02 .00 .02 .02 .00 .00 .02 .03 .08 .08 .08 .13 .18 .24
rear   .21 .07 .06 .03 .03 .03 .02 .02 .01 .02 .02 .02 .00 .01 .01 .02 .04 .06 .06 .09 .11
side   .16 .08 .06 .03 .03 .02 .02 .02 .01 .01 .01 .01 .02 .02 .03 .07 .07 .10 .00 .00 .13
```

**Width per height, whole silhouette** (width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .01@.52 .76@.13 .93@.07 .96@.04 .88@.08 .72@.19 .65@.22 .49@.32 .31@.48 .23@.51 .04@.60
r34    .01@.39 .83@.04 .90@.06 .90@.08 .83@.10 .76@.14 .66@.15 .42@.27 .36@.30 .25@.36 .01@.47
front  .00@.49 .82@.06 .97@.03 .93@.05 .82@.11 .74@.16 .65@.19 .38@.39 .29@.45 .21@.47 .01@.57
side   .12@.41 .80@.04 .87@.01 .77@.08 .64@.16 .57@.16 .40@.30 .36@.31 .29@.35 .18@.38 .01@.47
rear   .02@.58 .97@.01 .95@.04 .89@.06 .84@.09 .76@.13 .69@.15 .42@.29 .35@.33 .22@.38 .01@.50
top    .07@.73 .45@.43 .65@.28 .93@.02 .83@.10 .85@.10 .86@.14 .85@.13 .83@.13 .70@.20 .03@.50
```

The step from about .65 to .38–.49 between h .6 and .7 (front, f34, rear) is where B's crown (and G's in the rear) ends
and only A continues: **above h .7 only A and its moss remain, 0.21–0.31 of W wide**.

**Rock components** (`comps.py`, R eroded once; sheet px):

| View | Components |
| --- | --- |
| Front | A + C merged 128–243 × 537–699 (50.7 % of R); B 52–150 × 596–695 (36.2 %); F 242–271 × 648–672; D 27–46 × 666–683; E 118–153 × 680–700 |
| f34 | A + C 272–461 × 123–421 (50.8 %); B 130–309 × 222–411 (37.6 %); F 458–507 × 321–367; D 82–122 × 344–382; E 244–309 × 384–423 |
| Rear | G + H + A merged 534–712 × 543–699 (84 %); B's back 710–744 × 611–686; a small rock 597–626 × 682–699 |
| r34 | A + H 663–869 × 144–422 (57 %); B's back 854–956 × 250–397 (14 %); G 590–719 × 279–416 (22 %); a small rock 701–741 × 390–422 |
| Side | A + C + B merged 336–451 × 545–699 (83 %); G 457–481 × 630–665; small rocks 428–451 × 678–696 and 458–473 × 674–687; B sliver 312–329 × 636–660 |
| Top | B (lower left) 814–908 × 571–673; G (upper right) 897–970 × 534–608; C (lower right) 903–965 × 628–694; a small rock 874–898 × 532–555 |

**Per-rock boxes, read on the grids** (`g_*.png`; sheet px; h = fraction of the cell's silhouette height):

| Rock | Front | f34 | Rear | Side | r34 |
| --- | --- | --- | --- | --- | --- |
| A | x 128–222 (94 px), crown y 538 (h .91), moss to 523 (1.0); crown face x 140–175 | x 263–428, crown y 122 (h .95) | x 578–695 (117 px), crown 553 (h .85) | x 337–455 (D 118 px), crown 547 (h .88) | x 660–830, crown 165 |
| B | x 52–151 (99 px), crown 596 (h .59), moss to 583 | x 130–310, crown 222 (h .64) | right rock x 707–745, top 610 (h .52, foliage over it) | sliver x 308–330 behind C, top 632 | right dome x 854–956, top 250 (h .57) |
| C | x 152–244 (92 px), top 628 (h .41) | x 307–460, top 290 (h .43) | hidden behind G | front dome x 318–425 (D 107 px), top 622 (h .45) | hidden |
| G | hidden | hidden | left dome x 530–612 (82 px), top 617 (h .48) | right x 448–481, top 630 (h .41) | left dome x 590–718, top 280 |
| H | hidden | hidden | front-centre dome x 625–715 (90 px), top 640 (h .35) | hidden | front-centre dome x 735–870, top 330 |

**Green components** (`greens.py`; f across, h up):

| View | Moss caps | Foliage |
| --- | --- | --- |
| Front | A f .48–.63, h .83–1.0; B f .20–.40, h .54–.67 | left tuft f .03–.21, h .04–.41; B/A notch sprig f .38–.47, h .58–.71; centre column (A's foot and round E) f .41–.67, h .01–.48; right column f .73–.98, h .22–.64; right low sprig f .88–1.0, h .10–.22 |
| f34 | A f .55–.67, h .84–1.0; B f .24–.45, h .58–.76 | left f .04–.25, h .08–.45; centre f .44–.70, h .00–.50; right column f .77–1.0, h .25–.66; right low f .89–.97, h .11–.22 |
| Rear | A f .37–.58, h .83–1.0 | left (on and beside G) f .03–.30, h .07–.65; centre (between G and H) f .29–.56, h .02–.45; right (between H and B) f .63–.90, h .15–.66; far right f .94–1.0, h .08–.30 |
| r34 | A f .36–.56, h .81–1.0 | above G f .14–.30, h .45–.66; centre f .30–.54, h .02–.44; right f .62–.84, h .07–.69; far left low tufts f .05–.20 |
| Side | A f .38–.56, h .84–1.0 | front f .04–.46, h .01–.59 (incl. B's moss above C); back f .46–.89, h .0–.51 |
| Top (h = back) | none drawn | back arc f .12–.68, h .60–.98; right between G and C f .62–1.0, h .31–.72; front centre f .43–.69, h .06–.26; left f .08–.16 |

**Flowers** (white, five rounded petals, yellow domed centre; on top of a cluster; hand count): front 4 (left tuft, A's
foot, two in the right column); f34 3–4; rear 3–4 (on G's top, between G and H, between H and B); r34 3; side 2; top 1–2;
exploded 4 (one per Flower Cluster). Flower Ø about 13 px in the f34 = 0.36 studs; 0.35–0.45 in the build.

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, governs; `f34.png`, `z_f34_AB.png`).** The same drawing as the front cell from a
little higher (§3.1).
- **A** stands behind B and C: a tall faceted pillar whose crown is a narrow sloping face (moss on it), steep straight
  left and right flanks, the shaded left flank as two or three long faces, the lit front as one long shield-shaped
  face (from just under the crown down behind B's crown level) flanked by long quads. About 16–20 facets visible.
- **B** at the front left: an upright block, its left flank near-vertical in shade, its crown a broad flat polygon
  tilted toward the viewer (visible as a face, so the camera is above), its lit front made of big irregular triangles
  (long slivers next to wide ones), widest at about 0.6 of its height. The moss mat covers the crown's front-left half
  and hangs over the front-left edge; a leaf sprig sits at the back right where B meets A. About 15–17 facets visible.
- **C** at the front right: a low dome overlapping A's foot, a flat-ish crown polygon, broad faces down to the ground,
  no moss. About 14–18 facets visible.
- **Creases:** a dark crease runs where B's right edge meets A (from B's crown down to the ground, partly hidden by the
  centre foliage) and where C's top meets A. The rocks read as **separate forms**, not one pile: B forms its own rock
  component (37.6 % of R); A and C merge only through their overlap.
- **Foliage:** a tall left tuft with a flower against B's left foot (D in front of it); a flower cluster in the crevice
  at A's foot between B and C; low clusters left and right of E at the front; a tall stacked column with two flowers
  between C's back and A's right flank; a sprig at F.
- **Ground shadow:** neutral grey to the left (light from the right); background.

**Front (`front.png`, `g_front.png`).** The f34 drawing again (W : H 1.425 against 1.433), every rock at the same
fraction within 0.04.

**Rear three-quarter (`r34.png`, `g_r34.png`).** A true back-left view (az ≈ 208, §3.2): G as a big bare dome at the
left, A in the centre with its moss, H as a low dome at the front centre (nearest the camera), B's back as a dome at the
right with foliage over its top, small rocks between. Foliage above G with a flower, in the gap between G and H with a
flower, and between H and B with a flower.

**Rear (`rear.png`, `g_rear.png`).** A true rear view (az 180): G at the left (the model's right), H at the centre
right, B's back at the right partly behind foliage, A behind. Three flowers at the same places as the r34.

**Side (`side.png`, `g_side.png`).** The kit side camera at +X (screen left = front, screen right = back, §3.3): C as the
front dome at the left of centre, A behind it in the centre, B's left-front corner as a dark sliver at the far left with
its moss and sprig showing above C, G at the right partly behind A and foliage, small rocks at the back.

**Top (`top.png`, `g_top.png`; image top = back).** B as the big polygon at the lower left, C at the lower right, G at
the upper right, a small rock at the top centre, foliage in an arc round the back and down the right between G and C, a
cluster at the front centre. **No moss caps are drawn and A is not distinguishable** (§3.4).

**Close-ups.**
- **Rock / Rock Junction** (657,812,1007,984): A's lit left flank (big flat faces, one long ridge) meeting C's top in a
  plain V crease, a clover cluster tucked into the joint. "Simple contact surfaces (flat faces, no complex blend)": the
  rocks touch or overlap slightly; nothing is filleted or merged.
- **Underside View** (657,1010,1007,1182): a rock (B, with moss on its crown and two small rocks at its sides) from below:
  **one big flat bottom polygon of about 11 irregular corners**, 148 × 116 px against the rock's about 160 × 130 px, so
  the flat bottom spans about 0.85–0.92 of the rock's width. Colour `#7E746C` (unlit).
- **Rock Thickness / Cross-Section** (657,1210,1007,1479): A cut open: a tall faceted rock (W : H 0.81 on screen,
  widest at h .34, sloping crown) drawn as a thin hollow shell with a cream cut rim. A stylised note (§3.8).

### 1.4 Parts (Exploded Construction (17,786,645,1248), `expl.png`, `z_expl_rocks.png`, `g_explA.png`)

Scale: the exploded is drawn from about 20–25° above and at mixed scales (A 32, B 36, C 29 px/stud for the hero sizes).
**The hero governs every size** (A especially, §3.5); the exploded gives shapes, facets and the part list.

#### Rock A (tall, main) (276,804,434,983) 159 × 180 px incl. moss

- **Shape (hero):** a tall faceted pillar-egg, **H/W 1.40–1.55, H/D 1.30–1.40**, widest at h .25–.45, the crown a
  narrow sloping face group 0.40–0.50 of the max width, tilted 8–15° down toward the front left; a hexagonal crown ring;
  long vertical side faces (several run 0.45–0.6 of the height); the biggest single face is the lit front "shield"
  (about 1.6 × 2.6 studs). Flat bottom.
- **Exploded widths per height** (rock only, h .0 → 1.0): `.03 .49 .72 .89 .87 .86 .91 .82 .74 .62 .06` (from above, so
  the bottom rows curve in); W : H on screen 0.88, i.e. drawn squatter than the hero (§3.5).
- **Moss:** a lobed lime cap (7–9 oak-leaf lobes, 1.6–1.9 across, 0.25–0.4 thick, draping 0.3–0.6 down the crown
  edge); a small olive moss smear (`#6F7637`) on the upper left (shaded) face, about 0.5 × 0.8.
- **Hero size:** 5.0 W × 5.4 D × 7.3 H (crown); moss top 8.0.
- **Construction:** `rock_a()` via `K.hull_rock(..., keep_bottom=True)` with rings (height frac, radius frac, points)
  about `(0.0, 0.90, 7), (0.30, 1.0, 7), (0.62, 0.92, 6), (0.85, 0.66, 5), (1.0, 0.42, 4)`, radial jitter 0.10–0.12,
  azimuth jitter ±0.35 of a step, lean (−0.08, −0.06) so the crown slopes front-left. Thin one point from the 0.30 and
  0.62 rings on the front so the shield face forms. **About 50–90 tris.**

#### Rock B (medium) (130,924,301,1073) 172 × 150 px

- **Shape (hero):** a squat upright block, **H/W 0.92–1.02**, widest at h .45–.60, still 0.65–0.75 of the max width at
  h .9 (a broad crown), steep near-vertical left flank; the crown a broad polygon of 2–3 faces with normal z > 0.9 spanning
  0.55–0.65 of W, tilted 10–15° toward the front; big irregular triangles on the front.
- **Exploded widths per height:** `.04 .54 .76 .89 .98 .99 .95 .88 .80 .70 .48`; f34 B (left foot hidden by foliage)
  `.05 .51 .57 .65 .86 .91 .98 .92 .83 .71 .02`.
- **Moss and sprig:** a flat lobed moss mat 2.4–2.8 × 1.8 on the crown's front-left half, hanging 0.3–0.5 over the
  front-left edge; a three-to-five-leaf clover sprig at the crown's back right (exploded `#6F7932` in shade,
  hero lime).
- **Hero size:** 4.8 W × 4.4 D × 4.7 H.
- **Construction:** `rock_b()` via `K.hull_rock` rings about `(0.0, 0.88, 7), (0.25, 0.97, 7), (0.55, 1.0, 7),
  (0.82, 0.86, 6), (1.0, 0.60, 5)`, jitter 0.10, tilt the crown ring 10–15° forward. **About 50–80 tris.**

#### Rock C (medium) (391,963,522,1084) 132 × 122 px incl. moss

- **Shape (hero):** a low faceted dome, **H/W 0.66–0.76**, widest at h .35–.50, crown polygon 0.40–0.55 of W, broad
  faces down to a flat bottom.
- **Exploded widths per height:** `.19 .62 .80 .92 .96 .98 .93 .85 .75 .64 .02`.
- **Moss:** a small lobed tuft (1.2 across) in the exploded only; the hero C has none (§3.6).
- **Hero size:** 4.5 W × 4.8 D × 3.2 H. **Reused** as G (4.2 × 4.2 × 3.6) and H (4.7 × 3.8 × 2.8) by rotation and
  non-uniform scale ("Reuse individual rock … pieces").
- **Construction:** `rock_c()` via `K.hull_rock` rings about `(0.0, 0.92, 7), (0.30, 1.0, 7), (0.62, 0.86, 6),
  (0.86, 0.58, 5), (1.0, 0.30, 3)`, jitter 0.11. **About 44–70 tris.**

#### Small rocks D, E, F (+ pebble): D (66,1050,124,1107) 59 × 58, E (303,1028,383,1096) 81 × 69, F (516,1078,575,1140) 60 × 63 px

- **Shape:** chunky faceted lumps with flat bottoms, 10–18 facets, a near-flat top face; D and F rounder (h/w 0.75–0.90),
  E flatter (h/w 0.55–0.65). D carries an olive moss smear at its left foot (`#6B7331`); F has a few moss specks and a
  pebble (about 0.35 of F) beside it.
- **Exploded widths per height:** D `.03 .69 .76 .75 .81 .93 .86 .75 .66 .49 .10`; E `.21 .59 .88 .88 .96 .88 .81 .67 .64
  .44 .06`; F `.07 .57 .87 .95 .77 .80 .87 .78 .68 .53 .05`.
- **Hero sizes:** D 1.0 × 0.9 × 0.8; E 1.7 × 1.4 × 1.0; F 1.4 × 1.3 × 1.2; pebble 0.5 × 0.45 × 0.3; three back instances
  (§2.3).
- **Construction:** `small_rock(w, d, h, seed)` via `K.hull_rock` rings `(0.0, 0.9, 6), (0.35, 1.0, 6), (0.75, 0.75, 5),
  (1.0, 0.35, 3)`, `keep_bottom=True`, jitter 0.12: **20–36 tris** each; pebble 12–16.

#### Foliage Cluster (reusable) ×4 drawn, Flower Cluster (reusable) ×4 drawn

Exploded boxes (sheet px): plain (118,1099,177,1161), (190,1117,259,1180), (259,1092,302,1136), (418,1124,468,1174);
flower (315,1130,390,1192) big, (284,1174,328,1211) small, (446,1114,499,1155), (502,1145,552,1189).
- **Shape:** a rosette of 6–10 **rounded, spoon-shaped (obovate) leaves** in two tiers rising from one root point: low
  outer leaves splayed out and darker, inner leaves upright with yellow-lime tips; chunky, faceted, cupped solids. On
  screen W : H 0.9–1.3 (true h/w 0.6–0.9). Leaf length 0.45–0.6, width 0.30–0.40.
- **Flower Cluster:** the same rosette with one white five-petal flower (rounded petals, a domed yellow centre) on top;
  the big one also has a smaller second flower bud at its foot (exploded (284,1174)).
- **Hero sizes:** clusters 1.2–2.2 across, 0.8–1.4 tall; tall stacked columns (two clusters stacked up a flank) to 2.5–3.4.
- **Construction:** `cluster(size, seed, flower=False)` from `K.clover` / `K.leaf(shape="round", fold 0.15–0.2,
  thick 0.06–0.08)` in 2 tiers; flower from W01's `flower5` (petals Ø 0.4, centre a 6-sided dome). **About 80–110 tris
  per cluster, + 50–80 per flower.**

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0). Plan X from the front cell (X = (x − 145.5) / 20.5); plan Y from the
side cell (Y = (x − 402.5) / 20.0, screen left = front), the rear cell (X = −(x − 635) / 19.3) and the top view.
`proj.py` projects this layout to every camera; the results are quoted in §3.

### 2.1 Rocks

| Piece | Centre (x, y), base z | Size W × D × H | Rot | Sheet evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| A, tall main | (+1.0, +1.0), 0 | 5.0 × 5.4 × 7.3 | crown slopes front-left | front x 128–222 (X −0.8 … +3.7), crown h .91; side D 118 px; rear centre | moss cap on the crown; olive smear on the upper left face |
| B, medium block | (−2.2, −1.8), 0 | 4.8 × 4.4 × 4.7 | crown tilted 10–15° to the front | front x 52–151 (X −4.6 … +0.3), crown h .59; r34 right dome; rear right; top lower left | moss mat front-left of the crown; sprig back right |
| C, medium dome | (+2.6, −2.2), 0 | 4.5 × 4.8 × 3.2 | 0 | front x 152–244 (X +0.3 … +4.8), top h .41; side front dome; top lower right | bare in the hero |
| G, back-right dome (C mesh) | (+3.5, +2.8), 0 | 4.2 × 4.2 × 3.6 | about 150° | rear left dome (X +1.2 … +5.4), h .48; r34 left dome; side right; top upper right | bare; foliage + flower on its top-back |
| H, back low dome (C mesh) | (−1.8, +3.4), 0 | 4.7 × 3.8 × 2.8 | about 70° | rear front-centre dome (X −4.2 … +0.5), h .35; r34 front-centre | bare; nearest rock in both back views |
| D, small | (−5.5, −1.8), −0.05 | 1.0 × 0.9 × 0.8 | — | front x 27–46 (X −5.8 … −4.9) | in front of the left tuft; moss smear at its left foot |
| E, small flat | (−0.5, −4.5), −0.05 | 1.7 × 1.4 × 1.0 | — | front x 118–153 (X −1.3 … +0.4) | at the front between B and C |
| F, small | (+5.5, −0.6), −0.05 | 1.4 × 1.3 × 1.2 | — | front x 242–271 (X +4.7 … +6.1) | pebble beside it at (+6.1, −1.3) |
| D′ back-left (D mesh) | (−4.6, +3.6), −0.05 | 1.0 × 0.9 × 0.8 | — | rear x 718–740; r34 right small | |
| E′ back-centre (E mesh) | (+0.8, +4.9), −0.05 | 1.4 × 1.2 × 0.8 | — | rear x 600–628 (X +0.4 … +1.8); r34 701–741; top small top-centre | |
| F′ back-right (F mesh) | (+5.3, +4.2), −0.05 | 1.1 × 1.0 × 0.9 | — | side x 458–473; rear pebble x 555–575 | |

- **Expected extents:** rocks X −5.95 … +6.3, Y −5.2 … +5.4; with foliage about X −6.3 … +6.3, Y −5.4 … +5.4 →
  **12.6 × 10.8 × 8.0**.
- **Contact:** rocks touch or overlap by 0–0.15 at their meeting faces ("simple contact surfaces"); B's right flank
  against A's left foot; C's back-left shoulder against A's front foot; G against A's back-right; H against A's back
  left and B's back. No booleans between rocks (§6).
- **f34_sheet (0, 12):** W : H 1.38–1.49 (sheet 1.433); B crown at h .59–.69, C top at h .38–.48, A crown at h .90–.97.
- **front_sheet (0, 8):** W : H 1.37–1.48 (sheet 1.425); A x .43–.80, B .14–.52, C .52–.88 (±0.04).
- **side_sheet (90, 8):** D : H 1.18–1.29 (sheet 1.234).

### 2.2 Rock-shape targets (binding; measure with `M.audit`, own bmesh code and `rocks.py`/facet segmentation on the renders)

Recent failures: M023's lobes were "soccer-ball" facets (Fibonacci planes, ±6 % jitter), M031's rocks were mauve and
upright slabs, M035 needed big irregular triangles. These numbers are measured on the sheet:

| Target | Value | Sheet evidence |
| --- | --- | --- |
| Tris per rock (before any refine) | A 50–90; B 50–80; C 44–70; small 20–36; pebble 12–16 | 14–20 facets visible per main rock per view; 11–18 flat regions (§ next row) |
| Flat regions per main rock per elevation render (threshold 5, regions ≥ 0.4 % of the rock's area) | 11–18 | exploded A 11, B 14, C 15, E 12; f34 B 15; front B 17 (threshold 4: 13–18) |
| Largest facet, share of its rock's projected area | **A 16–26 %** (the front shield); **B 10–17 %**; **C 12–19 %**; small 8–20 % | threshold 4–5: expl A .22–.24, B .10–.17, C .12–.18, f34 B .12–.13, front B .10–.11; E .07–.10 |
| Largest facet, true area | A 2.5–4.5 sq studs; B 2.0–3.5 (the crown); C 1.8–3.2; ≥ 4 × the rock's median facet | — |
| Facet size spread | triangle area CV ≥ 0.6; edge length CV ≥ 0.35 (floor excluded) | slivers next to wide triangles on every rock |
| Vertex valence | 3–8 (floor-fan centre excluded), mean 4.5–6.0, no single valence on more than 45 % of the verts | fans of 4–6 on the hero rocks |
| No regular pattern | no pentagon/hexagon faces; no vertex ringed by 5–6 near-equal (±15 % area) triangles at more than 3 vertices of a rock; no icosphere, Fibonacci-plane or UV-sphere construction | — |
| No upright slabs | every rock's H/W within its row of §1.4: A 1.40–1.55, B 0.92–1.02, C 0.66–0.76, G 0.80–0.92, H 0.55–0.65, D 0.75–0.85, E 0.55–0.65, F 0.80–0.90; wall-facing (normal within 15° of horizontal) area ≤ 0.35 of A's non-floor area, ≤ 0.30 for B, ≤ 0.20 for the domes and small rocks | only A is taller than wide |
| Widest section | A at h .25–.45 (crown 0.40–0.50 of max); B at h .45–.60 (≥ 0.65 at h .9); C at h .35–.50 (0.55–0.65 at h .9) | §1.4 width rows |
| Base flatness | one flat floor (face or fan) spanning **0.75–0.90 of the max width in X and Y**; floor area 0.55–0.75 of the max horizontal section; 9–12 floor-outline corners | underside close-up: 148 × 116 px floor against about 160 × 130, about 11 corners |
| Crowns | A: 2–4 faces with normal z > 0.8, together 2.0–2.5 across, sloping 8–15°; B: 2–3 faces with normal z > 0.9 spanning 2.6–3.2; C: 2–4 faces spanning 1.8–2.4 | f34 / front / exploded crowns |
| Distinct forms | in front_sheet (R eroded once, as `comps.py`), B is its own component of 30–42 % of R (sheet 36.2 %); a dark crease or a tone step of ≥ 25 levels along ≥ 70 % of the B–A boundary; A's left edge visible between B's crown and A's crown over ≥ 1.2 studs; in the top render B, C and G read as separate outlines | the rocks are a group, not a pile |

### 2.3 Foliage, flowers and moss (instances)

| Piece | Root (x, y), z | Variant / size | Sheet evidence | Seat |
| --- | --- | --- | --- | --- |
| Moss cap A | on A's crown | lobed mat 1.8 × 1.6, 0.3 thick | front f .48–.63, h .83–1.0 | conformed (sink 0.03–0.06), draping 0.3–0.6 |
| Moss mat B | B's crown, front-left half | lobed mat 2.6 × 1.8, 0.25 thick | front f .20–.40, h .54–.67; f34 x 160–255 | conformed; hangs 0.3–0.5 over the front-left edge |
| FL1 left tuft, flower | (−5.0, −1.0), 0 | tall flower cluster, w 1.9, h 2.3 | front f .03–.21, h to .41, flower at h .32 | leans on B's left flank, behind D |
| FL2 B sprig | (−0.6, −0.6), on B's crown (z ≈ 4.5) | small plain, w 1.0, h 0.8 | front f .38–.47, h .58–.71; exploded B's sprig | at the B/A notch, leaves against A |
| FL3 A-foot flower | (+0.1, −1.0), z ≈ 1.6 on C's back-left shoulder and A's foot | flower cluster, w 1.6, h 1.2 | front centre flower at h .45; junction close-up | in the crevice between B, A and C |
| FL4 front low left | (−1.2, −4.0), 0 | plain, w 1.4, h 0.9 | front f .41–.50, h .0–.25 | left of E |
| FL5 front low right | (+0.9, −4.3), 0 | plain, w 1.5, h 0.9 | front f .50–.67, h .0–.25 | right of E, in front of C's left foot |
| FL6 right column, 2 flowers | (+4.5, +0.2), 0 → stacked to z ≈ 4.8 | tall: a plain cluster with a flower cluster above, w 2.0, h 3.2 | front f .73–.98, h .22–.64, flowers at h .34 and .37; f34 right column | between C's back and A's right flank, in front of G |
| FL7 right sprig | (+5.6, −1.6), 0 | small plain, w 0.9, h 0.6 | front f .88–1.0, h .10–.22 | beside F |
| FL8 on G, flower | (+3.0, +4.0), z ≈ 3.0 on G's top-back + a trail down G's +X side | flower cluster, w 1.6, h 1.4 | rear left f .03–.30, h to .65, flower at h .61; r34 above G | on G's crown edge |
| FL9 back centre, flower | (+0.9, +3.8), 0 | flower cluster, w 1.7, h 1.6 | rear centre f .29–.56, flower at h .38 | between G and H, against A's back |
| FL10 back left, flower | (−3.6, +1.4), 0 → up B's back | tall flower cluster, w 2.0, h 2.8 | rear right f .63–.90, h to .66, flower at h .28; r34 right | between H and B, leaning on B's back |
| FL11 far back-left | (−5.2, +2.4), 0 | plain, w 1.3, h 0.9 | rear far right f .94–1.0; top left | |

- 11 cluster instances from **two meshes** (Foliage and Flower Cluster) by scale and rotation, plus FL6's stack; 7
  flowers (FL1, FL3, FL6 × 2, FL8, FL9, FL10). Visible counts then land within ±1 of every view: front 4, rear 3–4, r34
  3, side 2.
- **The front centre stays readable:** between FL4/FL5 and B's and C's feet, bare rock meets the ground over about
  X −0.2 … +0.5 behind E.
- **Seats.** Clusters root at z 0–0.05 or on a rock surface (`K.conform` / `K.top_at`); leaves may touch rocks but cut no
  more than 0.05 into them; tall clusters lean 10–20° toward the rock behind them. Small rocks: base 0.04–0.06 below z 0,
  then the floor cut gives each a flat bottom.

## 3. View conflicts and resolutions

### 3.1 The "front three-quarter" is an elevated front view; the front cell is the same drawing

- **Evidence.** Every rock sits at the same fraction within 0.04 in both (A .43–.80 against .42–.82; B .14–.52 against
  .17–.56; C .52–.88 against .56–.89); top profiles within mean 0.060; W : H 1.433 against 1.425; B's crown shows as a
  face in both (so both cameras are above).
- **Elevation:** B's crown face is about 10 px deep in the front cell and its foot outline curves about 8 px over its
  half-width, giving about 8–11°; the f34 shows a little more of the crowns (B crown at h .64 against .59).
- **Resolution.** Compare the f34 cell with an extra **`f34_sheet (0, 12)`** and the front cell with **`front_sheet (0,
  8)`**. In stage 1 render f34_sheet once at e 8, 12 and 16 and keep the best top-profile fit. **The kit `front34 (−28,
  12)` is a front-left camera and shows a different arrangement**: self-consistency only.

### 3.2 The rear three-quarter is a back-LEFT view (az ≈ 208), not the kit rear34 (152) and not the f34 mirrored

- **Evidence.** The r34 matches the rear cell (profile mean 0.044) and not the f34 flipped (0.112). Projecting §2's
  layout (`proj.py`): at **az 208** (camera at back-left) G lands at f .08–.37 (sheet left dome .09–.39), A at .26–.61
  (sheet .26–.65), H at .36–.67 (sheet front-centre dome .43–.75) and **B at .56–.88 (sheet right dome .71–.95, with
  foliage over its top, as on B's crown)**. At az 152 (the kit's back-right rear34) B would fall at .35–.71 behind H
  and nothing would explain the right-hand dome.
- **Resolution.** Compare the r34 cell with an extra **`r34_sheet (208, 12)`**: shares ±4, profile ±0.08, G left, H
  front centre, B's back right, A's moss at f .36–.56. The kit `rear34 (152, 12)` is self-consistency only.

### 3.3 Rear and side are real cameras on the same layout

- **Rear (az 180):** screen left = the model's right. G at f .07–.38 (sheet .07–.40), H at .42–.76 (sheet .46–.83), B's
  back at the right partly behind foliage, C hidden behind G (C 3.2 tall against G 3.6). Compare with
  **`rear_sheet (180, 8)`**: shares ±5, profile ±0.08, 3–4 flowers.
- **Side (az 90, camera at +X, screen right = back):** C at f .05–.47 as the front dome (sheet .10–.60), A at .31–.78
  (sheet .20–.74), G at .52–.89 partly hidden (sheet right rock .71–.86), B hidden behind C except its moss and sprig
  above C's top and a sliver at the far left. At az −90 the tall B would stand at the screen right, which the cell does
  not show. Compare with **`side_sheet (90, 8)`** (or the kit `side (90, 4)`): D : H ±0.06, C and G on the correct
  sides.

### 3.4 Top view: no moss and no distinct A

- **Evidence.** The top cell draws B (lower left), C (lower right), G (upper right) and a small rock at the top centre
  with a foliage arc round the back and right, but no moss caps and no separate outline for A (the tallest rock, which
  a camera above would show largest). It is also drawn smaller (14.8 px/stud) and with perspective.
- **Resolution.** The elevation views govern. Judge the top render by: B, C and G as separate outlines in their
  quadrants; foliage round the back and right and at the front centre; W : D 1.10–1.22 (sheet 1.081, accepted miss if
  the side's D/W 0.86 holds). Record "the top view draws no A and no moss" as a known miss.

### 3.5 Rock A: tall in the hero, an egg in the exploded

- **Evidence.** Hero A: H/W 1.75 in the front (94 px wide, 165 px from the crown to the ground, including about 16 px of
  elevation shift), 1.35 in the side (H/D), 1.26 in the rear, 1.5 in the r34. Exploded A: W : H 0.88 including its moss,
  about H/W 1.05 for the rock, drawn from 20–25° above at a larger scale. The cross-section shows a tall A again (H/W
  1.24 on screen from above).
- **Resolution.** The hero governs: **A 5.0 × 5.4 × 7.3, H/W 1.46, H/D 1.35** (mean of the elevation views after the
  elevation correction). Keep the exploded's facet layout (hexagonal crown ring, long side faces, the front shield,
  widest at h .3–.45). The squat exploded proportion is a known miss for the RockA part.

### 3.6 Moss: on A and B in the hero, also on C in the exploded

- **Evidence.** Every elevation view shows moss on A's crown and on B's crown (B's hidden from behind); C, G and H are
  bare in the front, f34, rear, r34 and side. The exploded puts a small tuft on C.
- **Resolution.** Moss caps are their own closed shells (§8.6), so the hero's C, G and H instances carry none; the
  `…RockC` part export carries the tuft, as drawn. Small olive smears (A's upper left face, D's foot) are paint.

### 3.7 Counts: "three main rock meshes and smaller supporting rocks"

- The front shows 3 main + 3 small; the back views add two more domes (G, H) and three small rocks; the exploded shows
  3 main + 3 small + a pebble, 4 foliage and 4 flower clusters. **Resolution:** 3 main rock meshes (A, B, C), with C
  reused as G and H; 3 small-rock meshes (D, E, F) reused at the back; 1 pebble; 2 cluster meshes placed 11 times with 7
  flowers (§2.3). Each view's counts then land within ±1.

### 3.8 "Hollow, single-shell geometry … consistent thickness"

- **Evidence.** The cross-section draws A as a thin shell with a cream cut rim. A Roblox MeshPart is already hollow: a
  closed surface with nothing inside.
- **Resolution.** Build every rock as **one closed manifold shell with no inner wall and no internal faces** (STAGES
  stage 2 forbids interior faces, and an inner wall would double the tris). "Single shell" and "no internal detail" are
  met; the drawn wall thickness is not modelled. Record this; don't render a cut.

### 3.9 Palette names against the renders

- Both rock swatches are warm: "Main Rock (large faces)" `#CFB9AE` (hue 20°, sat 0.16, R > G > B) and "Rock Shadow
  (facets)" `#A99691` (hue 12°, sat 0.14, R > G > B, G − B only 5). The rendered rock median is `#C0A597`–`#C4A899`
  (hue 20–21°, sat 0.21–0.22): **warmer and more saturated than either swatch**. The lavender of the shaded faces (hue
  300–350°, B ≥ G by 2) is the cool sky fill, not paint (§5.3). The green swatches (`#BBC162`, sat 0.49; `#E1D85B`, sat
  0.60) are much paler than the rendered greens (sat 0.85–0.98). Use swatches as starting colours only; calibrate on the
  unshadowed exploded renders.

### 3.10 "Simple, solid colors, no texture noise" against the user's blended-colour rule

- The user's rule wins, but keep it quiet: whole-facet light and shadow patches on the rocks ("Rock Shadow (facets)"),
  height bands on the moss, tiered leaves, low Tint. No per-triangle confetti.

### 3.11 Ground shadow

- A soft neutral grey (`#AEAEB0`–`#B8B8B8`) to the left of every view. It is lighting, not geometry: background in
  every measurement, and not modelled.

## 4. Construction plan (stages 1–3)

1. **Parts first,** each from its own function and checked against its exploded cell:
   - `rock_a_part()` → `MossyRockClusterRockA`: A with its moss cap and smear. Compare with the exploded A from about
     (−20, 22) (facets, crown ring, shield face) and with §2.2 (H/W against the hero, not the exploded).
   - `rock_b_part()` → `MossyRockClusterRockB`: B with its moss mat and sprig.
   - `rock_c_part()` → `MossyRockClusterRockC`: C with the exploded's tuft.
   - `small_rock_part()` → `MossyRockClusterSmallRock`: D (with its moss smear).
   - `foliage_part()` → `MossyRockClusterFoliage`: the plain cluster.
   - `flower_part()` → `MossyRockClusterFlowerCluster`: the cluster with its flower.
   - Render a parts shot (`extra`, about (−20, 22)) laid out like the exploded.
2. **Hero:**
   1. Build A, B, C as hulls; place G and H as rotated, non-uniformly scaled copies of C's verts (re-hull or transform;
      no shared faces); place the small rocks and pebble; floor-cut every rock at z 0.
   2. Paint the rocks (stage 4 needs the face lists; keep the original facet ids before any refine).
   3. Build the moss shells and conform them to A's and B's crowns (sink 0.03–0.06).
   4. Place the 11 clusters and 7 flowers (§2.3).
   5. `M.fix_bowties`, origin at the bbox bottom centre, transforms applied.
3. **Budget** (§4.3): hero about 2400–3200 (limit 4000); each part under 400 (limit 1000). If over, drop leaves from the
   back clusters' hidden sides first; never thin a main rock below its §2.2 minimum.
4. **Placeholder keys** (stage 1): `m036_rock`, `m036_moss`, `m036_leaf`, `m036_petal`, `m036_pollen`. Stage 4 adds the
   rest (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** a group of separate big-faceted warm rocks: tall A behind, block B front left, dome C front right,
      two bare domes behind; moss on A and B; clover with white flowers in the joints and round the foot.
   2. **f34_sheet against the f34 cell:** W : H 1.38–1.49; shares within ±4 of 74.8 / 24.4 / 0.8 (caps 5.2 ± 1.5); top
      profile within ±0.08 (mean ≤ 0.05); rock boxes per §1.2 ± 0.04; 3–4 flowers.
   3. **front_sheet against the front cell:** W : H 1.37–1.48, shares ±4 of 73.3 / 25.7 / 1.0, profile ±0.08; B its own
      rock component of 30–42 % of R.
   4. **r34_sheet (208, 12) against the r34 cell, rear_sheet against the rear cell, side_sheet against the side cell:**
      shares ±5, profiles ±0.1, G / H / B on the sides of §3.2–§3.3, rock counts ±1, 3–4 flowers in the back views.
   5. **Top (0, 89):** B, C, G separate outlines; foliage round the back and right; W : D 1.10–1.22; no A outline and
      no moss are the known misses.
   6. **Rock-shape targets** (§2.2), every one, on each hero rock and each rock part.
   7. **Parts against their cells** (§4.1); a **junction extra** `junc_cu (15, 10)` framed on the A–C contact and FL3
      against the Rock / Rock Junction close-up; an **underside extra** of the RockB part from below (az 0, e −35)
      against the Underside View (flat floor of 9–12 corners spanning 0.75–0.90 of the width).
   8. **Hero size** 12.6 × 10.8 × 8.0 (±0.5 / ±0.6 / ±0.3); each rock per §2.1 ± 0.3.
   9. **Scale shot:** the hero beside a 5.5-stud character marker (the kit-relative-scale rule).
6. **Stage 2:**
   - every shell closed and manifold: zero non-manifold edges and verts (`nonmanifold_verts` 0), boundary, wire and
     loose elements; no zero-area faces or n-gons; normals outward;
   - no interior faces; rocks don't share faces (they may overlap by up to 0.15);
   - no decimation of a main rock below its §2.2 minimum, small rocks below 10 facets.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density (leaves and petals included).

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Rock A | 1 | 50–90 | 50–90 |
| Rock B | 1 | 50–80 | 50–80 |
| Rock C (+ G, H) | 3 | 44–70 | 132–210 |
| Small rocks D/E/F (+ 3 back) + pebble | 6 + 1 | 20–36 / 12–16 | 130–230 |
| Moss cap A, mat B | 2 | 80–150 | 160–300 |
| Clusters (plain and flower, about 8 leaves) | 11 + 1 stacked | 80–110 | 960–1320 |
| Flowers (5 petals + centre) | 7 | 50–80 | 350–560 |
| **Hero** | | | **about 1830–2790; 2400–3200 with the stacked column and extra leaves** (limit 4000) |
| Parts: RockA / RockB / RockC / SmallRock / Foliage / FlowerCluster | | | about 150–240 / 150–250 / 100–130 / 20–36 / 80–110 / 130–190 (limit 1000) |

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 50 × 26–30 box inside each, x 50–100)

| Swatch | Box | Hex | HSV | Channel order |
| --- | --- | --- | --- | --- |
| Main Rock (large faces) | (50,1305,100,1334) | `#CFB9AE` | 20°, 0.16, 0.81 | R > G > B |
| Rock Shadow (facets) | (50,1352,100,1380) | `#A99691` | 12°, 0.14, 0.66 | R > G > B (G − B 5) |
| Moss / Leaves | (50,1398,100,1424) | `#BBC162` | 64°, 0.49, 0.76 | G > R > B |
| Leaf Highlight | (50,1441,100,1468) | `#E1D85B` | 56°, 0.60, 0.88 | R > G > B |

There is no swatch for the petals, the flower centres or the moss smear; they are sampled from the renders below.

### 5.2 Rendered regions (`samp.py`; median / lit quartile / shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Rock, f34 / front / rear / r34 / top / side | view boxes | R | `#C0A597` / `#C4A899` / `#BFA496` / `#BEA395` / `#C8AB9D` / `#B09991` | `#E6C8B8` / `#E9CCB7` / `#EBCEBA` / `#E9CDBA` / `#EACDB9` / `#E7CAB5` | `#746E70` / `#746E70` / `#756F71` / `#756F71` / `#786F6C` / `#746D6E` |
| Rock A / B / C, f34 | (265,120,430,290) / (128,205,312,415) / (307,290,460,420) | R | `#BFA497` / `#B99D8F` / `#CAADA0` | `#E8CBBB` / `#E2C4B1` / `#ECD4C4` | `#6E696D` / `#716C6E` / `#827771` |
| Rock A / B / C, front | (128,538,222,625) / (48,596,153,700) / (152,628,246,700) | R | `#C6AA9A` / `#C0A595` / `#CAAD9E` | `#ECCEB9` / `#E8CBB5` / `#E9D0BF` | `#716C6E` / `#746D6F` / `#80756E` |
| Rock G / H, rear | (528,617,612,699) / (625,640,715,700) | R | `#AB958F` / `#C0A396` | `#ECCEB8` / `#EBD1BF` | `#716B6C` / `#8A7D7D` |
| **Rock, exploded A / B / C (no cast shadow)** | (270,786,440,990) / (125,895,305,1075) / (388,940,525,1088) | R | **`#C0A598` / `#BFA598` / `#B09992`** | `#E2C6B4` / `#E0C4AF` / `#E5CCB8` | `#736D70` / `#746D70` / `#796E6B` |
| Rock thirds, exploded A (top / mid / bot) | | R | `#DFC4B0` / `#C3A899` / `#BCA293` | `#EED5C2` / `#DCBFAB` / `#D0B5A1` | `#736F74` / `#716C71` / `#776D69` |
| Rock thirds, exploded B | | R | `#D4BAA9` / `#C3A99C` / `#948481` | `#EBD1BF` / `#DBBDA8` / `#C4ABA0` | `#7C7577` / `#746F73` / `#746B6B` |
| Rock thirds, exploded C | | R | `#DBC2B4` / `#AC9793` / `#AB948B` | `#EFD5BF` / `#E2C6B3` / `#CFB3A1` | `#938381` / `#776E6E` / `#796C68` |
| Rock thirds, front B | (51,596,151,696) | R | `#C5ABA0` / `#C5AA9A` / `#958582` | `#EED1BB` / `#E5C6AC` / `#CAAFA3` | `#716D72` / `#746E70` / `#776E6B` |
| Small rocks, exploded E / D / F | §1.4 boxes | R | `#C2A997` / `#B4998C` / `#BCA091` | `#E6CBB6` / `#E5CBB7` / `#E7CBB9` | `#7C7271` / `#766F70` / `#6D6665` |
| Junction close-up (lit A flank) | (657,812,1007,984) | R | `#D5B9A5` | `#E4CABC` | `#9C8B88` |
| Underside close-up, flat bottom (unlit) | (700,1045,840,1150) | R | `#7E746C` (27°, 0.14, 0.49) | `#827870` | `#766D66` |
| Moss smear, exploded A's left face / D's foot | (270,870,300,940) / (62,1070,90,1110) | G | `#6F7637` (67°, 0.53, 0.46) / `#6B7331` | `#77803A` / `#768032` | `#686C38` / `#5E622F` |
| **Moss caps, exploded A / B / C** | (285,786,395,835) / (140,893,262,940) / (415,942,505,982) | G | **`#B3BA1B` / `#AEB916` / `#B7BE17`** | `#DAD620` / `#D6D31A` / `#DBD61E` | `#748A13` / `#64890B` / `#809111` |
| Moss caps, f34 A / f34 B / front A / front B / rear A / r34 A | cap boxes | G | `#AFBA0F` / `#BBBF13` / `#B2B90A` / `#B6BC0D` / `#B8BC0C` / `#B8BE0E` | `#D3D012` / `#DAD516` / `#D5D30E` / `#DBD610` / `#D6D510` / `#D9D611` | `#7A8F0E` / `#72870E` / `#72840F` / `#6A810D` / `#73860D` / `#7A8F0C` |
| **Foliage, exploded plain 1 / 2 / 4** | §1.4 boxes | G | **`#8AB204` / `#86B505` / `#8BAE05`** | `#BAD307` / `#C0D50E` / `#C7D508` | `#508001` / `#4E8302` / `#507803` |
| Foliage, exploded flower clusters big / small / R1 / R2 | §1.4 boxes | G | `#90B508` / `#85A80A` / `#B1C20A` / `#92B109` | `#C6D512` / `#CED40F` / `#D8D817` / `#D4D713` | `#507D05` / `#446C04` / `#5C7A06` / `#608805` |
| Foliage, f34 below h .6 / front / rear / side / r34 / top | view boxes | G | `#719606` / `#7C9A07` / `#7E9C07` / `#799806` / `#779705` / `#759307` | `#BCD109` / `#C6D30B` / `#C2D10A` / `#BFC907` / `#BCCF06` / `#BFCE09` | `#3B5E04` / `#3F5B07` / `#405C06` / `#3F5A07` / `#385604` / `#3A5606` |
| Junction close-up leaves | (657,812,1007,984) | G | `#94B608` | `#C9D617` | `#4C7703` |
| Petals, f34 / front / exploded | | white | `#FEFEFC` / `#FEFEFC` / `#FFFEFD` | `#FFFFFE` | `#F6F4E6` / `#F8F6E3` / `#F4F0E3` |
| Flower centre, f34 / front / exploded | | yellow | `#DED217` / `#DBCB11` / `#E0D21F` | `#E8DC1D` / `#E7DB24` / `#E9DC29` | `#CFBE14` / `#C9BD0C` / `#D1BD18` |
| Ground shadow, f34 / top / exploded | | B | `#AEAEB0` / `#B0B0B0` / `#B8B8B8` | | |

Deciles (dark → light):

```
rock f34       #6A6565 #777174 #82797C #988581 #BBA093 #C4A99B #CBAFA3 #D7BBAA #E3C6B2 #F0D7C7
rock expl A    #6F696B #746E72 #80767C #A08D89 #BCA193 #C3A89B #C6AC9F #D8BBA6 #E1C4AF #EBD1C1
moss expl A    #627119 #7A8E12 #879C13 #A2AC17 #ABB616 #BEC11D #CCCB1F #D0CE20 #D8D41F #E1D922
leaf expl 2    #326401 #528901 #629604 #6DA204 #7FAC02 #8EBA05 #9EC408 #AECF08 #BDD30E #CBDD13
foliage f34    #243A05 #416804 #537905 #5F8306 #649104 #7B9E06 #90B106 #A6C306 #B5CE07 #D3DB0D
```

### 5.3 How the colour works

**Rock.**
- **One warm grey-pink stone, not mauve.** Every rock median on the sheet is **R > G > B**, hue 13–25°, sat 0.15–0.23:
  R − G 15–32, **G − B 5–17** (f34 `#C0A597`: 25 / 14; front `#C4A899`: 28 / 15; exploded A `#C0A598`: 27 / 13; rear G
  `#AB958F`: 22 / 6). The lit faces are peach (`#E2C6B4`–`#ECD4C4`, hue 21–28°). The shaded faces are cool lavender (hue
  300–350°, sat 0.04–0.06, B ≥ G by 1–3): that split is the warm sun and the cool sky fill, **light, not paint**. Never
  colour by facing, and never give a rock key B ≥ G.
- **Painted signal (gentle): "Rock Shadow (facets)".** Facet to facet the tone varies on the sheet (lit deciles
  `#D7BBAA` → `#F0D7C7`; exploded C's and the rear G's darker medians `#AC9793`, `#AB958F`, still hue 10–13°). Paint
  broad patches of whole facets: `rock_shadow` (from the Rock Shadow swatch, kept warm) at about 25–30 % coverage, mixed
  35–40 %; `rock_light` (exploded top thirds `#DFC4B0`, `#D4BAA9`, `#DBC2B4`) on the upper third at about 25 % coverage,
  mixed 25 %. The tops on the sheet are lighter than the bottoms in every exploded rock (by 30–60 levels), partly paint,
  partly light: keep the paint share small.
- **No dark painted foot band.** The bottom thirds (`#948481`, `#958582`) are the down-facing faces in shade; their lit
  quartiles stay within 20–30 of the mid third. At most a 15 % `rock_shadow` mix below 0.1 H where foliage presses in.
- **Moss smears:** olive moss (`#6F7637`, `#6B7331`) on A's upper left face (one patch about 0.5 × 0.8) and D's left
  foot; a genuinely different material: blend with `steps=2` over refined faces so the edge reads lobed.
- **Small rocks:** the same stone (`#C2A997`, `#B4998C`, `#BCA091`), per-rock tint ±0.06.

**Moss caps.**
- Lime-yellow moss: medians hue 61–64°, sat 0.85–0.95, value 0.73–0.75; lit tops near Leaf Highlight (`#DAD620`,
  swatch `#E1D85B`); deep green in the notches and the rim (`#748A13`). Per cap: **deep at the rim and notches → moss →
  sun-yellow on the top third**, by height within the cap (a position field).

**Foliage.**
- A greener, darker family than the moss: medians hue 72–76°, sat 0.95–0.98, value 0.58–0.71 (moss 0.73–0.75).
- **Tiered:** low outer leaves deeper (`#4E8302` mixed 40 %), middle leaves `leaf`, inner upright leaves and tips
  `leaf_young` (`#C0D50E`, close to Leaf Highlight). Stepped by tier like `K.clover(young_mat=…)`, not by facing.
- **Flowers:** pure white petals (`#FEFEFC`; shade quartile `#F6F4E6`), a yellow domed centre (`#E0D21F`, hue 55–56°,
  sat 0.86–0.92).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

The calibration targets are medians of **unshadowed** rendered regions (the exploded parts and close-ups), not
swatches. `K.sample` kinds: `"stone"` for the rock keys, `"green"` for the moss and leaf keys, `"vivid"` for the pollen.

| Key | Calibration target | Hue / sat / order targets | Where | Finish |
| --- | --- | --- | --- | --- |
| `m036_rock` | `#C0A598` (exploded A; B `#BFA598`; start from swatch Main Rock `#CFB9AE`) | hue 17–23°, sat 0.18–0.23, R > G > B, G − B 10–16 | every rock, the default | rough 0.9 |
| `m036_rock_shadow` | `#A99691` (swatch Rock Shadow; exploded C mid `#AC9793`) | hue 10–16°, sat 0.12–0.16, R > G > B, **G − B ≥ 5** | whole-facet patches at 25–30 %, mixed 35–40 % | rough 0.9 |
| `m036_rock_light` | `#D8BEAD` (exploded top thirds `#DFC4B0` / `#D4BAA9`) | hue 20–26°, sat 0.18–0.22 | upper-third patches at 25 % | rough 0.9 |
| `m036_moss_smear` | `#6F7637` (exploded A's smear; D `#6B7331`) | hue 64–70°, sat 0.5–0.6 | A's upper left face, D's foot | rough 0.95, low spec |
| `m036_moss` | `#B3BA1B` (exploded A cap; B `#AEB916`, C `#B7BE17`) | hue 60–66°, sat ≥ 0.85, value median ≥ 0.70 | caps, default | rough 0.9, low spec |
| `m036_moss_sun` | `#DAD620` (cap lit quartiles `#D6D31A`–`#DBD61E`; swatch Leaf Highlight `#E1D85B`) | hue 57–61° | top third of each cap | rough 0.9, low spec |
| `m036_moss_deep` | `#748A13` (cap shade quartiles `#64890B`–`#809111`) | hue 68–76° | rim band and notches | rough 0.9, low spec |
| `m036_leaf` | `#88B205` (exploded plain clusters `#8AB204` / `#86B505` / `#8BAE05`) | hue 72–78°, sat ≥ 0.93, value median ≤ 0.71 | clusters, default | rough 0.85, low spec |
| `m036_leaf_young` | `#C0D50E` (plain-cluster lit quartiles `#BAD307`–`#C7D508`) | hue 64–68° | inner upright leaves and tips | rough 0.85, low spec |
| `m036_leaf_deep` | `#4E8302` (plain-cluster shade quartiles) | hue 80–86° | outer low leaves at 40 % | rough 0.85, low spec |
| `m036_petal` | `#F6F4EC` (petal shade quartile; median `#FEFEFC`) | sat ≤ 0.06 | petals | rough 0.7 |
| `m036_pollen` | `#E0D21F` (exploded centre median; f34 `#DED217`) | hue 54–58°, sat ≥ 0.82 | flower centres | rough 0.7 |

**Calibration warnings:**
- **Rock warmth (the mauve failure, M031 and one earlier model):** calibrate `m036_rock` on the parts-shot RockA against
  `#C0A598`, then check **every** view's rock median: hue 15–25°, sat 0.17–0.24, **R > G > B with G − B ≥ 6** (front,
  f34, rear, r34, side, top and every part). Our studio's shaded faces will read neutral rather than lavender; don't push
  them by facing, and never let a key's B reach its G (M031's `#999296` failed exactly so).
- **Two greens apart:** moss hue 60–66°, sat ≥ 0.85, value median ≥ 0.70; foliage hue 72–78°, sat ≥ 0.93, value median
  ≤ 0.71. The hue gap must stay ≥ 6°.
- **Petals** clip easily: calibrate on the parts shot so the petal lit quartile is ≤ `#FFFFFE` and the median ≥
  `#F0F0EA`.
- **Lit quartiles** of our studio run 16–22 levels below the sheet's (M023, M035 verifiers): light, not paint.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Rocks** (on each rock's original facets, before any refine): `rock` base; `K.noise_field(scale≈0.2)` whole-facet
  patches → `rock_shadow` at 25–30 % coverage, mixed 35–40 %; upper-third patches → `rock_light` at 25 %; G and H get
  their own seeds so they don't repeat C's pattern. Then refine only A's upper-left face and D's foot and blend
  `moss_smear` there with steps 2.
- **Moss caps:** field t = (z − base) / h per cap: t < 0.25 → `moss_deep`; 0.25–0.65 → `moss`; > 0.65 → `moss_sun`;
  steps 2–3.
- **Foliage:** by tier (outer / inner) and leaf tip: `leaf_deep` 40 % → `leaf` → `leaf_young`; each cluster its own
  `tint_var` 0.04.
- **Hard edges only** where materials meet: rock | moss cap, petal | pollen.

### 5.6 Texture (Tint) and finish

- **Tint:** rock amp 0.04, scale 0.3, per original facet (a refined facet keeps one tone); moss amp 0.05, scale 0.8;
  leaves 0.04; petals none. Never per-triangle confetti ("no texture noise").
- **Finish:** rock rough 0.9, metal 0; moss and leaves `low_spec=True` (`K.FOLIAGE_SPEC` 0.06), rough 0.85–0.9; petals
  and pollen rough 0.7. No emission anywhere.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Rock:** f34_sheet median within 10 of `#C0A597`; front_sheet within 10 of `#C4A899`; parts-shot RockA within 8 of
  `#C0A598`; every view hue 15–25°, sat 0.17–0.24, R > G > B, G − B ≥ 6.
- **Moss:** f34_sheet caps within 12 of `#B2BB10` (mean of the f34 caps); parts-shot cap within 10 of `#B3BA1B`; hue
  60–66°, sat ≥ 0.85.
- **Foliage:** f34_sheet foliage within 12 of `#719606`; parts-shot cluster within 10 of `#88B205`; hue 72–78°, sat ≥
  0.93.
- **Petals** median ≥ `#F0F0EA`; **pollen** hue 54–58°, sat ≥ 0.82.
- **Shares** per §4 step 5.2–5.4.

## 6. Joins and contact

- **Rock to rock:** separate closed shells, touching or overlapping by 0–0.15 at flat contact faces ("simple contact
  surfaces (flat faces, no complex blend)"). No booleans between rocks, no fillets. A visible dark crease forms where
  they meet (§2.2 distinct forms).
- **Moss on rock:** conformed to the crown, sunk 0.03–0.06, a closed shell resting on the rock with no gap visible from
  any view; B's mat hangs 0.3–0.5 over the front-left edge.
- **Small rocks:** 0.04–0.06 below z 0, floor-cut flat; within 0.0–0.3 of a big rock or a cluster; none floating, none
  standing on a point.
- **Foliage:** roots on the ground (z 0–0.05) or conformed onto a rock (FL2, FL3, FL8); leaves press against rocks but cut
  no more than 0.05 into them; tall clusters lean on the flanks.
- **Ground:** the floor cut at z 0 (`m004.floor_cut`) gives every rock its flat bottom.

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** an ordinary sunlit rock group. No glow, light, sparkle, dust, pollen motes or particles in any
cell; the flowers are plain white and yellow paint, not emissive. WorldModeling §1.2 forbids "an ordinary asset recolored
neon with a glow halo".

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight:** nothing on the sheet glows.
- **Studio note (Requires Manual Validation):** check in Studio that the rocks stay warm grey-pink (not grey, not
  mauve, not orange) under the game's sun and sky, that the moss lime and the leaf green stay two distinct greens, and
  that the petals don't bloom to flat white.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`, `heat_glow`,
  `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`, `harvest_hit`,
  `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust` (as listed by M035's study).
- **Recommended: none.** The sheet shows no effect; W01's `RockCluster` and M035's `MossyBoulder` (the same family)
  shipped none. Record "Stage 6 skipped: sheet shows no VFX".
- **Not recommended:** `dust` or pollen motes (nothing floats on the sheet), `ore_glint` (plain stone), any light, or
  harvest sockets (not a resource node).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by searching the repo text and every sheet / wip `.blend` (zstd-decompressed) with
`blendall.py` / `names.py`:
- **W01** (`FlintbornWorldKit.blend`, `W01.blend`, every wip copy): `RockCluster`, `RockClusterA`, `RockClusterB`,
  `RockClusterC`, `RockClusterLinear`, `RockClusterCrescent`, `RockClusterTriangular`; keys `w01_*`.
- **M004:** `ObsidianRockCluster`. **M035:** `MossyBoulder*`, keys `m035_*`.
- **Elsewhere:** `JuniperFoliageCluster`, `LogAndStumpMossFoliage`, `SaplingLowerFoliage`, `SaplingTopFoliage`, many
  `*LeafCluster`, `WaterLilyFloweringCluster`, `CloverFlowerHead`, `CloverFloweringPatch` (V01), `Pebble*` (W01).
- `M.mk` would silently rename a clash to `<name>M036`, so avoid all of these.

**Proposed names.** None of `MossyRockCluster`, `m036_` occurs in the repo, the decompressed kit `.blend` or any sheet /
wip `.blend`. It keeps the sheet's "Rock Cluster" and follows M035's `MossyBoulder` precedent.

| Object | Part | Why |
| --- | --- | --- |
| `MossyRockCluster` | hero | W01 owns `RockCluster` |
| `MossyRockClusterRockA` | Rock A (tall, main) with its moss cap and smear | W01 owns `RockClusterA` |
| `MossyRockClusterRockB` | Rock B (medium) with its moss mat and sprig | W01 owns `RockClusterB` |
| `MossyRockClusterRockC` | Rock C (medium) with the exploded's tuft | W01 owns `RockClusterC` |
| `MossyRockClusterSmallRock` | Rock D (small) with its moss smear | `*RockSmall` belong to R01/R03 |
| `MossyRockClusterFoliage` | Foliage Cluster (reusable) | `*FoliageCluster` belongs to the juniper |
| `MossyRockClusterFlowerCluster` | Flower Cluster (reusable) | — |

- Palette keys `m036_*` (§5.4). Collection `Kit/M036 Rock Cluster`.
- Collision tags: hero and every rock part `"hull"`; Foliage and FlowerCluster `"none"`; SmallRock `"hull"`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **dressed 12.6 × 10.8 × 8.0, A's crown 7.3** (recommended: A a little over head height, a mid-size
   cluster between M035's boulder and W01's big cluster), or W01's class (A crown 10.5 → dressed about 18 × 15.5 ×
   11.5), or a compact 10.0 × 8.6 × 6.4 (A crown 5.8, about character height).
2. **Rock count** (§3.3, §3.7): **3 main meshes, C reused as two back domes G and H; 3 small-rock meshes reused at the
   back; a pebble** (recommended: the rear, r34, side and top all show the back domes), or only the front's A, B, C
   (the back views would then show A alone behind B).
3. **Rock A's proportion** (§3.5): **the hero's tall pillar, H/W 1.46** (recommended), not the exploded's egg (H/W
   about 1.05); the RockA part follows the hero.
4. **Moss** (§3.6): **caps on A and B only in the hero; the RockC part carries the exploded's tuft** (recommended).
5. **Cameras** (§3.1–§3.3): **`f34_sheet (0, 12)` (probe 8 / 12 / 16 once), `front_sheet (0, 8)`, `r34_sheet (208, 12)`
   (a back-left camera, not the kit rear34), `rear_sheet (180, 8)`, `side_sheet (90, 8)`, the kit top**; kit front34,
   rear34 and underside as self-consistency only; extras `junc_cu (15, 10)`, an underside shot of the RockB part (0,
   −35), a parts shot (−20, 22) and a scale shot with a 5.5-stud marker. Hide the floor in every `*_sheet` render (the
   sheet's ground shadow is background).
6. **Hero packaging:** **one hero object holding closed shells: each rock (A, B, C, G, H, the six small rocks and the
   pebble), each moss cap, and each leaf, petal and flower centre as its own closed solid** (recommended: the sheet says
   rocks meet with "simple contact surfaces … no complex blend" and "Separate foliage and flower meshes"; booleans
   between the rocks would blend them, and uniting about 100 leaves is slow and crash-prone). Every shell closed and
   manifold, 0 bowties, 0 self-intersections inside a shell; shells may touch or overlap by up to 0.15 but never share
   faces; `problems` reports any shell that isn't closed.
7. **"Hollow single shell"** (§3.8): **closed solid shells, no inner wall** (recommended).
8. **Exports:** **the hero plus 6 parts** (RockA, RockB, RockC, SmallRock, Foliage, FlowerCluster) (recommended: the
   exploded's labelled kinds; D and F share one small-rock part).
9. **Stage 5/6:** **no emission, light or VFX** (recommended: the sheet shows none).
10. **Colour:** **one warm stone (R > G > B, hue 15–25°) with whole-facet "Rock Shadow" and light patches, olive moss
    smears, three-band lime moss caps, three-tier leaves** (recommended); no dark painted foot band, nothing by facing.
11. **Names** as proposed.

## 9. Pitfalls to avoid

1. **An icosphere or soccer ball.** The domes (C, G, H) look geodesic at a glance, but their triangles differ a lot in
   size and the crowns are flat polygons. Build convex hulls of jittered, thinned point rings (not
   `primitive_ico_sphere`, not Fibonacci planes) and meet every §2.2 number: facets, largest facet, area and edge CV,
   valence spread, no regular rings.
2. **Upright slabs or a stack of eggs.** Only A is taller than wide (H/W 1.40–1.55). B is a block about as tall as wide,
   C, G and H are low domes, the small rocks are squat. M031 failed for "upright slabs, not squat boulders"; W01's open
   minor was "Rock C a little egg-like".
3. **A pile instead of a group.** Each rock keeps its own outline and crown; the creases between them show; B's crown is
   a separate flat top 2.6 below A's. Don't fuse rocks by booleans or bury them in foliage; keep the front centre open.
4. **A mauve or grey rock.** The rock is warm: hue 15–25°, sat 0.17–0.24, R > G > B with G − B ≥ 6 in every view and
   every key. The lavender shade is light. Rock Shadow `#A99691` has G − B of only 5: keep it at least that warm.
5. **Copying the exploded A.** It is drawn as a squat egg from above; the hero's A is a tall pillar (§3.5).
6. **Using the kit front34 or rear34 as the comparison.** The f34 is a front view (az 0); the r34 is a back-LEFT view
   (az ≈ 208). The kit cameras show different arrangements (§3.1–§3.2).
7. **Copying the top view.** It draws no A and no moss (§3.4).
8. **Modelling the cross-section's wall.** Closed solid shells only; an inner wall doubles tris and adds interior faces
   (§3.8).
9. **Moss on every rock.** Only A and B in the hero; C's tuft belongs to the RockC part (§3.6). The caps are lobed mats
   with real thickness, draping over the crown edge (W01's minor: "moss caps sit as small tufts rather than draping").
10. **Blade or spiky foliage.** The leaves are rounded spoon shapes (`shape="round"`), chunky and cupped, in two-tier
    rosettes; about 7 white five-petal flowers.
11. **One green.** Moss (hue 60–66°, lighter) and leaves (hue 72–78°, darker) are two families; the smears are a third,
    olive one.
12. **The ground shadow.** It is background in every share, profile and width (§3.11); hide the floor in `*_sheet`
    renders.
13. **Floating rocks or leaves.** Small rocks floor-cut flat at the ground; leaves rooted at z 0 or conformed onto rock.
14. **Budget.** Foliage is most of the count (about 1300–1900 of 2400–3200). Don't spend tris on hidden back leaves;
    never thin a rock below its §2.2 minimum.
15. **Name clashes** with W01 `RockCluster*`, M004 `ObsidianRockCluster`, `*FoliageCluster`, `*RockSmall` (§8). Only one
    agent drives a Blender session at a time; no commits, pushes or exports in stage agents.

## Decisions (main session, 2026-10-29)

All recommendations are accepted:
1. Size: dressed 12.6 W × 10.8 D × 8.0 H, with A's crown at 7.3.
2. Back domes G and H as reused copies of C.
3. Rock A uses the hero's tall pillar (height/width 1.46).
4. Moss caps on A and B only in the hero. The RockC part keeps its small tuft.
5. Comparison cameras:
   - the hero cell as a front view near 12° (probe 8°, 12° and 16° once);
   - the front cell at about 8°;
   - the rear three-quarter as an extra at azimuth about 208, not the kit rear34;
   - the rear at 180, and the side on the kit side camera;
   - the kit front34 and rear34 for self-consistency only.
6. Packaging (same rule as M035): one hero object made of closed shells. Each rock, moss cap, leaf cluster and flower is its own closed, manifold shell with 0 bowties and no self-intersections inside a shell. No booleans between rocks. `problems` must report any shell that isn't closed.
7. Closed solid shells, with no inner wall.
8. Hero plus the 6 parts.
9. No lighting or VFX; stages 5 and 6 are recorded as skipped.
10. Colour: one warm stone (red > green > blue, green − blue ≥ 6 in every key) with whole-facet light and shadow patches, olive moss smears, lime moss in three height bands and leaves in three tiers. Never coloured by facing.
11. Names: `MossyRockCluster*`, keys `m036_*`.

The §2.2 shape targets (tris per rock, facet regions, largest-facet share, area and edge spread, valence, height/width and wall limits, flat bottoms, B as its own region) are binding. No soccer-ball patterns, and no upright slabs except A.

## Stage 1 — Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m036.py` (`build()`), run in the background session on port 9882 against
`art/blender/assets/kit/wip/M036.blend`; the final numbers below come from a freshly restarted session.

- **Rocks.** Each rock is a convex hull of jittered point rings (`CLOUDS`) flattened by 1–5 cut planes into big
  deliberate facets (A: crown sloping 8° to the front-left, lit front shield, shaded left flank, back-right contact face;
  B: crown tilted to the front, near-vertical left flank, front, back-right contact; C: crown polygon, front-right,
  back-left contact, front-left, right), then yawed and scaled to its exact world size (`ROCKS`). Floor-ring points
  slide horizontally under a cut, so every rock keeps one flat floor at z 0 (10 corners on the main rocks, 4–6 on the
  small ones). No icosphere, Fibonacci or UV-sphere construction. G and H are C's point cloud yawed (150°, 70°) and
  scaled (decision 2); D2/E2/F2 reuse D/E/F; plus a pebble.
- **Layout** (`layout()`): A fixed at (1.4, 1.2) (the front cell puts A's centre at X ≈ +1.45); every other rock is
  pushed horizontally away from those placed before it until the overlap is within its limit. Final moves from the
  starting table: C 0.15, G 0.28, H 0.29, F2 0.24, the rest 0. **Overlap limits (deviation from §6's 0–0.15):** small
  rocks 0.15; main rocks 0.60; G 1.3 (G tucks in behind A's back-right flank, as the rear and r34 cells draw it).
  Measured deepest overlap 0.89 (G into A), hidden inside the joint. Rocks never share faces; no booleans.
- **Moss caps** (`CAPS`, `_rosette`, `_conform_rosette`, after m035): A's cap is a 9-lobe oak-leaf mat (r 1.08, 0.88
  thick at the centre) plus a 5-lobe mat; B's is an 8-lobe mat squashed (1.0, 0.7) on the crown's front-left plus a
  5-lobe mat. Each is conformed (sink 0.05, drape up to 0.7) so the lobes hang over the crown edge, and each mat is its
  own closed shell. The RockC part alone carries a 6-lobe tuft (decision 4).
- **Smears:** A's upper-left face (refined locally; an olive patch about 0.6 × 0.9) and D's left foot. The refine is a
  local `_refine`, because K.refine adds a face layer and that makes every live BMVert reference stale; rocks are found
  again by their `kit_part` face tags.
- **Clover clusters** (`CLUSTERS`, 13 instances, `_cluster`): a low cluster is a rosette of 6 splayed outer leaves
  (deep green) and 3–5 upright inner leaves (lime tips). A tall cluster (FL1, FL6, FL9, FL10, FL13) is a leafy column up
  a hidden leaning stem: golden-angle yaw, splayed at the foot, upright and younger at the top; leaves pointing straight
  into the rock it leans on are left out. Leaves are 14-tri closed spoon solids (`LEAF_OUT`: cupped, with a two-point
  midrib). A leaf more than 0.45 inside a rock is dropped; a shallower one is pushed out (`_Guard`). Flowers (7): five
  round white petals and a hexagonal yellow dome, tipped 0.8 rad away from the group's middle and toward the front (front
  half) or the back (back half), on rosette crowns or on a column's top and outer face. FL3 sits on the rocks in the
  B/C/A notch (ray from z 3.4), FL2 on B's crown, FL8 on G's crown.
- **Parts** (decision 8): RockA (A + cap + smear), RockB (B + mat + sprig), RockC (C + tuft), SmallRock (D + smear),
  Foliage (plain rosette), FlowerCluster (rosette + flower + bud). Each part is a set of closed shells.

## Stage 2 — Optimisation and cleanup

- Hero **3438 tris** (limit 4000): rocks 12 shells / 666 tris, moss 4 / 378, leaves 136 / 1904, petals 35 / 350, flower
  centres 7 / 140. Parts: RockA 338, RockB 346, RockC 150, SmallRock 64, Foliage 126, FlowerCluster 266 (limit 1000).
- `M.audit` on all 7 objects: non-manifold edges 0, non-manifold (bowtie) verts 0, boundary 0, wire 0, loose 0,
  zero-area 0, n-gons 0, duplicate verts 0, normals outward, transforms applied, no custom normals, origin at the bbox
  bottom centre. `shells_report`: every shell closed (volume > 0), with 0 self-intersections and 0 inverted faces inside
  any shell. The smallest corner on any face is 6.9° (none under 5°; `m012._force_slivers` opened 9). `K.check`: no
  problems.
- Sizes: hero **12.77 W × 10.80 D × 7.83 H** (target 12.6 ± 0.5 × 10.8 ± 0.6 × 8.0 ± 0.3: all in range; H, A's moss top,
  is 0.17 under the target). Rocks exact: A 5.0 × 5.4 × 7.3, B 4.8 × 4.4 × 4.7, C 4.5 × 4.8 × 3.2, G 4.2 × 4.2 × 3.35
  (lowered from 3.6, see the notes), H 4.7 × 3.8 × 2.8, D 1.0 × 0.9 × 0.8, E 1.7 × 1.4 × 1.0, F 1.4 × 1.3 × 1.2, pebble
  0.5 × 0.45 × 0.3.
- Rock-shape targets (§2.2), measured before the refine (`rock_metrics`):

| Rock | tris | H/W | area CV | edge CV | largest facet (front share / area / × median) | widest h | crown (faces, span, tilt) | wall share | floor span | valence min/max/mean/top share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | 70 | 1.46 | 0.58 | 0.38 | 0.193 / 6.0 / 4.4 | .35 | 6, 2.3 × 3.0, 14° | 0.63 | .85 × .81 | 3/10/5.7/.45 |
| B | 60 | 0.98 | 0.56 | 0.36 | 0.110 / 2.9 / 3.0 | .35 | 5, 3.6 × 2.8, 17° | 0.60 | .81 × .81 | 3/8/5.7/.35 |
| C | 58 | 0.71 | 0.42 | 0.29 | 0.137 / 2.7 / 3.4 | .25 | 6, 2.9 × 3.6, 5° | 0.33 | .83 × .86 | 3/8/5.7/.28 |
| G | 58 | 0.80 | 0.42 | 0.29 | 0.105 / 2.6 / 3.4 | .35 | 6 | 0.39 | .86 × .92 | 3/8/5.7/.36 |
| H | 58 | 0.60 | 0.43 | 0.30 | 0.161 / 2.3 / 3.5 | .25 | 7 | 0.32 | .90 × .86 | 3/8/5.7/.36 |
| D / E / F | 32 each | .80 / .59 / .86 | .40 / .30 / .34 | ~.27 | .14 / .15 / .21 | .35 | — | .37 / .27 / .39 | .77–.93 | 4/7/5.6 |

  Met: tris per rock, every rock's H/W, largest-facet share (A .19, B .11, C .14), one flat floor with 10 corners, floor
  span within .75–.90 on A, B and C (G .92, H .90 at the edge), regular-pattern verts (A 1, F 1, the rest 0), B its own
  rock. **Missed:** wall share (A .63, B .60, the domes .32–.39; limits .35/.30/.20). An egg 1.46 tall with a flat floor
  can't tilt 65 % of its area more than 15°, and the sheet's A and B have steep flanks too. Also missed: area CV on C/G/H
  (.42) and the small rocks (.29–.40), under 0.6; B widest at h .35 (target .45–.60); B's crown tilt 17° (target 10–15°).

## Stage 3 — UV

`M.smart_uv(angle 45, ANGLE_BASED, margin 0.008)` then `m012._uv_unfold` on every object: 0 overlapping triangle pairs,
0 flipped, min island gap 0.016, border 0.008, texel density min/median/max 1.0/1.0/1.0, conformal stretch p95 ≤ 1.041.
Islands: hero 1456 (many small closed shells), RockA 84, RockB 125, RockC 36, SmallRock 9, Foliage 50, FlowerCluster
125. The exporter writes its own palette UVs.

## Stage 4 — Materials, colour and texture

- **Pass 1** (`calibrate()`: `K.calibrate` on the kit test dome against §5.4's targets; rendered sRGB in brackets): rock
  #978783 (191,165,152), shadow #867B7D (169,150,145; **a mauve key, B > G: rejected**), light #A99B93 (214,190,172),
  smear #5E6737, moss #909A19 (178,185,25), sun #AEB020 (218,214,32), deep #637511 (118,137,18), leaf #719301 (136,176,6),
  young #99AE06 (190,212,10), leaf deep #457001 (79,131,6), petal #C1C7CA (245,245,238), pollen #B1AC01 (223,211,37).
- **Pass 2** (hero f34/front renders against the sheet cells, linear gains): the rock keys × 1.32 (the hero rock median
  was #A18C7F against #C0A597), rock and shadow kept warm with G − B ≥ 6; leaf and leaf deep × ~1.2, then × 1.07 on G;
  the petal a touch brighter. Final `PALETTE`: rock **#AC9B94**, rock_shadow **#9D8F87**, rock_light **#BFAEA5**,
  moss_smear #5E6737, moss #909A19, moss_sun #AEB020, moss_deep #637511, leaf **#84B001**, leaf_young #99AE06, leaf_deep
  **#508801**, petal **#C8CDCF**, pollen #B1AC01. Every rock key is R > G > B (G − B 7, 8, 9).
- **Blend, by position only:**
  - Rocks per flat facet (coplanar neighbours merged, never per triangle): noise patches → rock_shadow mixed 13/27/40 %;
    patches on each rock's upper 40 % → rock_light 17/33/50 %; the floor plain rock. Tint per facet (amp 0.05, scale
    0.35) and ±4 % per rock.
  - Smears: olive at 35–90 % with a lobed, noisy edge.
  - Moss mats by place on the mat: the centre 50 % sun; ridges and rim one of 0/25/50 % sun per lobe; notch valleys
    moss→deep 50 %. Tint amp 0.05.
  - Leaves by tier: outer leaves leaf→deep 40 %; column leaves stepping deep 40 → 20 % → leaf → leaf→young 50 % up the
    column; inner rosette leaves leaf→young 50 % with young tips (the outer 40 % of the top, by place along the leaf).
    Tint 0.04 per leaf, ±4 % per cluster. Petals and pollen flat.
- **Finish:** rock rough 0.9; moss and leaves low specular (0.06), rough 0.9 / 0.85; petal and pollen rough 0.7.
- `K.check` baked-shading correlation: 0.0 on all 7 objects. An early RockB part read 0.79 from a darker moss rim; the
  rim now takes its lobe's shade.
- **Re-measured** (final renders, the study's masks; the sheet in brackets):

| View | W:H | rock / green / flower % | rock median | green median | profile mean / max |
| --- | --- | --- | --- | --- | --- |
| f34_sheet (0, 12) | 1.382 (1.433) | 79.4 / 20.2 / 0.4 (74.9 / 24.5 / 0.7) | #B8A091 (#C0A597) | #7C980E (#7F9E08) | 0.063 / 0.16 |
| front_sheet (0, 8) | 1.445 (1.425) | 79.7 / 19.9 / 0.4 (73.3 / 25.7 / 1.0) | #B7A091 (#C4A899) | #728E0D (#829D08) | 0.042 / 0.12 |
| r34_sheet (208, 12) | 1.529 (1.409) | 81.7 / 18.3 / 0.0 (75.1 / 24.2 / 0.7) | #B4A097 (#BEA395) | #6E8F09 (#849E06) | 0.071 / 0.26 |
| rear_sheet (180, 8) | 1.486 (1.397) | 84.6 / 15.4 / 0.0 (71.4 / 27.1 / 1.4) | #B4A197 (#BFA496) | #749608 (#849F08) | 0.079 / 0.26 |
| side_sheet (90, 8) | 1.266 (1.234) | 82.3 / 17.6 / 0.1 (70.5 / 28.2 / 1.2) | #9D8B82 (#B09991) | #648608 (#7E9B08) | 0.170 / 0.56 |
| top_sheet (0, 89) | 1.188 (1.081) | 66.4 / 33.0 / 0.6 (70.6 / 28.8 / 0.6) | #C7B1A5 (#C8AB9D) | #94BD07 (#759307) | 0.080 / 0.53 |

  Parts shots (−20, 20) against the exploded view's medians: RockA rock #CAB2A2 (#C0A598), cap #AFB01E (#B3BA1B); RockB
  #D4B8A7 (#BFA598), mat #C4C71C (#AEB916); RockC #DCC1AF (#B09992); SmallRock #DEC1B0 (#B4998C); Foliage #86AF07
  (#88B205); FlowerCluster leaves #7FAB08 (#90B508), petals #FFFFFF (#FEFEFC). Every rock median is hue 18–24°, sat
  0.18–0.22, R > G > B, G − B ≥ 10: warm, not mauve. The hero rock is 8–13 levels under the sheet and the lit parts
  shots are 10–20 over it. Our studio puts more of the hero in self-shadow than the sheet's lighting does, so no single
  gain meets both; the key sits between them.

## Stage 5 — Lighting

Skipped, as decided (decision 9): nothing on the sheet glows. No emissive key, no light. Studio check (Requires Manual
Validation): the rocks stay warm grey-pink (not mauve or orange) under the game's sun and sky, the moss lime and the leaf
green stay two greens, and the petals don't bloom to flat white.

## Stage 6 — VFX

Skipped, as decided (decision 9): the sheet shows no glow, sparkle, dust or particles. No sockets; `build()` reports a
problem if the hero ever carries one.

## Modeller's notes for the verifier

- **Cameras:** compare `f34_sheet`, `front_sheet`, `r34_sheet` (az 208), `rear_sheet`, `side_sheet` and `top_sheet` (3×
  lens, floor hidden) with the sheet cells. The kit front34/rear34/front/side/rear/top/underside are for
  self-consistency. Extras:
  - `exploded` and `part_*`;
  - `under_cu`: the RockB part from below, showing the flat 10-corner floor;
  - `junc_cu`: A's flank meeting C's top in a plain V crease, with FL3's clover and flower in the joint;
  - `scale`: the 5.5-stud marker (A a little over head height).

  `m036.compare()` re-measures every cell and parts shot.
- **Known misses and open items:**
  1. The green share is 15–20 % against the sheet's 24–28 %: foliage mass is limited by the 4000 budget (136 leaves at
     14 tris). The flower share is 0–0.4 % against 0.7–1.4 %: the back views' flowers sit in shade (the studio light
     comes from the front) and read cream rather than white under the masks. The top view is greener than the sheet
     (33 %).
  2. Side cell: profile mean 0.17, max 0.56 at the back. G (3.35 tall, nearest the +X side camera) shows as a full
     dome, where the sheet draws the back low and hidden behind foliage. The sheet's side cell seems inconsistent with
     its rear cells (spec §3.3). G was lowered from 3.6 to 3.35 and tucked behind A to soften it.
  3. Rear and r34: our A reads narrower than the sheet draws it from behind (the sheet's rear A is about 6 studs wide;
     decision 3 keeps 5.0 × 5.4 with H/W 1.46). W:H is 1.49–1.53 against 1.40–1.41.
  4. The §2.2 misses listed under Stage 2: wall share on every rock, area CV on the domes and small rocks, and B's
     widest height and crown tilt.
  5. Rock overlaps exceed §6's 0.15 for main-rock pairs (up to 0.6) and for G into A (0.89). These joints are hidden,
     and the shells stay separate.
  6. The moss caps read as lobed rosettes; A's has a raised centre. Its top is 7.83 against the 8.0 target (inside the
     tolerance, 0.17 under). In the hero they are yellower-lime than the sheet's caps.
  7. The hero rock median is 8–13 levels darker than the sheet, and the parts shots are 10–20 lighter (see Stage 4).
- **Packaging:** the hero is one object of 194 closed shells (decision 6). Collision tags: the hero and the rock parts
  "hull"; Foliage and FlowerCluster "none". Names `MossyRockCluster*`, keys `m036_*`, collection `Kit/M036 Rock
  Cluster`.
- The builder imports only committed helpers (`m033`, `m012`, `m011`). The m035 leaf, flower and rosette code is
  copied, not imported, because m035 is still being modelled.

## Verification round 1 (verifier, 2026-10-29)

Fresh verifier; read-only background session on port 9882 against `wip/M036_verify.blend` (nothing built, edited or
saved). Every number below was re-measured through the MCP. Renders and close-ups went to the scratchpad
(`…/scratchpad/m036_verify/renders/`), made with `m036.render_views` and `m033.render_close` with `M.MODEL_RENDERS`
redirected in memory. The colour checks sampled both the sheet and the renders with the study's masks
(`m036.compare` plus my own cap and foliage boxes).

### Measured

| Object | Tris (limit) | Size W × D × H | Shells | Non-manifold edges / verts | Boundary, wire, loose | Zero-area, n-gons | Self-hits / inverted | Normals | Origin, transforms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `MossyRockCluster` | 3438 (4000) | 12.77 × 10.80 × 7.83 | 194 (12 rock, 4 moss, 136 leaf, 35 petal, 7 pollen) | 0 / 0 | 0, 0, 0 | 0, 0 | 0 / 0 | outward | bottom centre, applied |
| `…RockA` | 338 (1000) | 5.00 × 5.40 × 7.83 | 3 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 / 0 | outward | ok |
| `…RockB` | 346 (1000) | 4.80 × 4.40 × 4.70 | 10 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 / 0 | outward | ok |
| `…RockC` | 150 (1000) | 4.50 × 4.80 × 3.48 | 2 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 / 0 | outward | ok |
| `…SmallRock` | 64 (1000) | 1.00 × 0.90 × 0.80 | 1 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 / 0 | outward | ok |
| `…Foliage` | 126 (1000) | 1.63 × 1.57 × 0.78 | 9 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 / 0 | outward | ok |
| `…FlowerCluster` | 266 (1000) | 1.75 × 1.65 × 1.06 | 21 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 / 0 | outward | ok |

- **Other mesh results.**
  - Every shell is closed with positive volume. No duplicate verts, custom normals, modifiers, children or sockets.
  - The smallest face corner is 7.2°.
  - UVs on every object: 0 overlaps and 0 flipped, min gap 0.016, border 0.008, density 1.0, stretch p95 ≤ 1.041.
  - `K.check` reports nothing, and baked shading is 0.0 on all 7 objects.
  - Collision tags: the hero and the rock parts are `hull`; Foliage and FlowerCluster are `none`.
  - Collection: `M036 Rock Cluster`.
- **Floating shells (hero).** These are leaves or petals, measured to the nearest other shell, rock or ground, with
  edges and faces sampled too, not only verts:
  - 20 leaf shells are more than 0.03 from everything; 16 are more than 0.05, 3 more than 0.1 and 1 more than 0.2.
  - The worst gaps are 0.24 (FL6 leaf at (4.72, 0.82, 1.14), hero frame), 0.15 (FL6, (4.81, −0.84, 1.54)), 0.11
    (FL6) and 0.10 (FL1 and FL13).
  - **Contact chains.** Some shells have no chain of contact to the ground or a rock. At a 0.03 contact tolerance
    that is 59 shells (29 leaves, 25 petals, 5 pollen); at 0.05, 48; at 0.1, 15 (9 leaves and one whole flower).
  - **Five whole flowers** (petals and pollen, with no leaf under them within 0.03) hover above their clusters: the
    FL6 top flower (4.2, −0.2, 4.0), FL6's second flower, FL8 (3.1, 4.5, 4.0), FL9 (0.9, 4.0, 2.3) and FL10
    (−4.3, 0.3, 2.7).
  - The cause: the tall columns (FL1, FL6, FL10, FL13) are leaves on a "hidden stem" that isn't modelled.
- The parts have no floating shells.
- **Penetration.**
  - Rock into rock: A–G 1.28, A–C 0.59, A–H 0.58, G–F2 0.13 (convex plane depth).
  - Leaves into rock: 9 of 136 leaves cut deeper than 0.05, and 5 deeper than 0.15 (max 0.40). Moss sinks by up to
    0.077.
- **Rock shape on the hero.** These are measured now, so A and D are after their smear refine; the modeller's
  pre-refine numbers agree for B, C, G, H, E and F.

| Rock | tris | H/W | area CV | edge CV | largest front facet | widest h | crown faces / span / tilt | wall share | floor span, corners | regular verts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | 134 (refined) | 1.46 | 1.14 | 0.70 | .193 (6.0 sq) | .35 | 8 / 2.3 × 3.0 / 14° | .63 | .85 × .81, 10 | 10 (refine grid) |
| B | 58 | 0.98 | 0.53 | 0.36 | .110 (2.9) | .35 | 5 / 3.6 × 2.8 / 17° | .60 | .81 × .81, 10 | 0 |
| C | 58 | 0.71 | 0.42 | 0.29 | .137 (2.7) | .25 | 6 / 2.9 × 3.6 / 5° | .33 | .83 × .86, 10 | 0 |
| G | 58 | 0.80 | 0.42 | 0.29 | .105 | .35 | 6 / 6° | .39 | .86 × .92, 10 | 0 |
| H | 58 | 0.60 | 0.43 | 0.30 | .161 | .25 | 7 / 3° | .32 | .90 × .86, 10 | 0 |
| D / E / F | 58 (refined) / 32 / 32 | .80 / .59 / .86 | .77 / .30 / .34 | .44 / .29 / .27 | .14 / .15 / .21 | .35 | — | .37 / .27 / .39 | .77–.93, 6–8 | 7 / 0 / 1 |

- **Moss caps.**
  - A: 2.09 × 1.87, 126 tris, spanning z 6.51–7.83 (1.3 tall including the drape), plus a 0.85 mat.
  - B: 2.48 × 1.58, z 3.58–4.67, plus a 0.89 mat.
  - The caps sit only on A and B; RockC's part carries the tuft.
- **Sheet comparison** (`m036.compare`; the sheet's value in brackets):

| Shot vs cell | W : H | rock / green / flower | profile mean / max | rock median | green median |
| --- | --- | --- | --- | --- | --- |
| f34_sheet (0, 12) | 1.382 (1.433) | .794 / .202 / .004 (.749 / .245 / .007) | 0.063 / 0.16 | `#B8A091` (`#C0A597`) | `#7E9815` (`#7F9E08`) |
| front_sheet (0, 8) | 1.445 (1.425) | .797 / .199 / .004 (.733 / .257 / .010) | 0.042 / 0.12 | `#B7A091` (`#C4A899`) | `#728E13` (`#829D08`) |
| r34_sheet (208, 12) | 1.529 (1.409) | .817 / .183 / .000 (.751 / .242 / .007) | 0.071 / 0.26 | `#B4A097` (`#BEA395`) | `#6E900F` (`#849E06`) |
| rear_sheet (180, 8) | 1.486 (1.397) | .846 / .154 / .000 (.714 / .271 / .014) | 0.079 / 0.26 | `#B4A197` (`#BFA496`) | `#75970E` (`#849F08`) |
| side_sheet (90, 8) | 1.266 (1.234) | .824 / .176 / .001 (.706 / .282 / .012) | 0.170 / 0.56 | `#9D8B82` (`#B09991`) | `#65860E` (`#7E9B08`) |
| top_sheet (0, 89) | 1.188 (1.081) | .664 / .330 / .006 (.706 / .288 / .006) | 0.080 / 0.53 | `#C7B1A5` (`#C8AB9D`) | `#96BD10` (`#759307`) |

- **Caps by box, ours against the sheet.**
  - f34: A `#B4BC1E` (`#AFB90F`), hue 63° against 64°, sat .84 against .92. B `#C5C634` (`#B7BC12`), hue 60° against
    62°, sat .74 against .90.
  - front: A `#B8C022` (`#B2B90A`); B `#C5C725` (`#B6BB0D`).
  - rear and r34: A `#9BA31F` (`#BABD0C`), about 25 darker.
- **Foliage by box.** f34 `#719011` (`#729706`); front `#59790A` (`#789607`); side `#5F7F0B` (`#7B9906`). Hue 75–77°
  against 72–75°.
- **Parts shots.**

  | Part | Rock median (target) | Green median (target) | Flower median (target) |
  | --- | --- | --- | --- |
  | RockA | `#CAB2A2` (`#C0A598`) | `#AFB125` (`#B3BA1B`) | — |
  | RockB | `#D4B8A7` | `#C5C823` (`#AEB916`) | — |
  | RockC | `#DCC1AF` | — | — |
  | SmallRock | `#DEC1B0` | — | — |
  | Foliage | — | `#88AF0F` (`#88B205`) | — |
  | FlowerCluster | — | `#82AC10` | `#FFFFFF` |

- **Keys.**
  - Rock keys: `#AC9B94` (hue 17°, G − B 7); shadow mixes `#AA9992`–`#A6968F` (G − B 7–8); light mixes
    `#AF9E97`–`#B6A49C` (G − B 7–8). Every rock key is R > G > B, and the only olive mixes are the smears.
  - Petal `#C8CDCF` (hue 197°, B > R). No emission anywhere (strength 0 on all 23 materials).
- **Colour by facing.** I correlated key luminance against face normal z: rock 0.37, moss 0.09, leaves 0.01.
  - The rock value comes from the `rock_light` patches on each rock's upper 40 %, which is a position field.
  - Mean rock key luminance by fifth of height, bottom to top: 155.7, 155.6, 157.7, 159.8, 161.9. There is no dark
    foot band.
  - Tint is a per-corner layer, 0.916–1.076 (std 0.025).
- **Rock material area.** Plain rock 57 %, shadow mixes 23 %, light mixes 19 %, smears 0.1 %.

### Findings

1. **Blocker: floating and sparse foliage. The tall clover columns and flowers have no support, and the clover
   reads thin and spiky against the sheet's lush rounded clumps.**
   - **Floating.** 20 leaf shells sit more than 0.03 from everything (worst 0.24). 48 shells have no chain of
     contact at 0.05, including 5 whole flowers that hover above their rosettes.
     - In the close-ups, the FL6 right column is a ladder of separate leaves with gaps between the tiers.
     - The FL1, FL8, FL9 and FL10 flowers float in the air above the leaves.
     - In `side_sheet`, FL6 reads as a fern ladder across the middle of A.
     - This is the same failure as M035 round 1.
   - **Sparse.** The green share is 20 % against 24.5 % in the f34 and 20 % against 25.7 % in the front, just
     outside ±4. In the back views it is 18 % against 24 % (r34), 15 % against 27 % (rear) and 18 % against 28 %
     (side): 6–12 points under, outside the ±5 of §4.5.4.
     - The sheet's left tuft, the clumps round every foot and the back mounds are dense rounded masses. Ours are
       small, splayed rosettes.
   - **Shape.** The leaves are pointed kites (the `LEAF_OUT` outline ends in a point), not the sheet's rounded
     spoon (obovate) clover leaves. This shows clearly in `part_foliage` and `part_flowercluster` against the
     exploded clusters.
   - **Fix target.**
     - Rebuild the tall clusters (FL1, FL6, FL10, FL13) as 2–3 overlapping dense rosette mounds stacked so each
       mound's leaves touch the one below and press against the rock.
     - Seat every flower on, or touching, its rosette's inner leaves.
     - Re-measure until 0 leaf or petal shells are more than 0.03 from a neighbour, the rock or the ground, and
       every shell chains to the ground or a rock at 0.03.
     - Round the leaf outline: a blunt, rounded tip (two near-equal tip corners), `LEAF_W` about 1.0, a short
       stalk.
     - Spend the spare budget (3438 → about 3950, roughly 35 more leaves) on denser clumps at the left tuft, round
       the back and on G, to bring the green share to ≥ 21 % in the front cells and ≥ 22 % in the back cells.
2. **Minor: A's moss cap reads as a raised lime "crown" rather than a flat lobed mat.**
   - Its centre is 0.88 thick, against §1.4's 0.25–0.4. In `part_rocka` and `f34_sheet` it reads as a coronet
     sitting on the crown.
   - B's mat is closer to the sheet but paler and yellower: sat .74–.81 against .90–.93, hue 60–61° against 62°.
   - Fix target: A's cap thickness to 0.35–0.45, lobes lying on the crown faces; B's mat toward `#B7BC12`.
3. **Minor: back-view flowers are invisible.**
   - The flower share is 0.0 in the r34 and rear against 0.7–1.4 %. The petals face away and render grey, and they
     are tiny.
   - Fix target: tilt FL8, FL9 and FL10 toward +Y and seat them on their rosettes (finding 1). Make the petal key
     neutral or warm instead of blue-grey `#C8CDCF`.
4. **Minor: the side cell.**
   - Profile mean 0.17, max 0.56: G shows as a full dome at the back, where the sheet hides it.
   - I accept the modeller's reading that the side cell disagrees with the rear cells. G stays where the rear and
     r34 cells put it.
5. **Minor: A is narrow from behind.** The rear and r34 W : H is 1.49–1.53 against 1.40–1.41, and A spans about
   0.39 of the rear width against 0.48. This is decision 3's proportion; accept.
6. **Minor: §2.2 rock-shape misses.**
   - Wall share: A .63, B .60, domes .32–.39.
   - Area CV: C, G and H .42, E and F .30–.34. Edge CV: C, G and H .29.
   - B is widest at h .35 and its crown tilts 17°.
   - The smear refine grids add 10 regular verts on A and 7 on D, but they are hidden under the smear paint.
   - None of this reads in the renders: the rocks show big irregular flat facets, with no soccer-ball pattern and
     no egg-shaped domes. Accept.
7. **Minor: overlaps exceed §6.** A–G is 1.28 by plane depth (the modeller's note says 0.89), and A–C and A–H about
   0.6. Nine leaves cut more than 0.05 into rock (max 0.40). Every joint is hidden and the shells stay separate;
   accept.
8. **Minor: colour.**
   - The hero rock is 8–13 levels darker than the sheet in front and f34 (front R 13 under). The parts shots are 10–20
     lighter. This is lighting; the keys sit between the two.
   - The `rock_shadow` and `rock_light` patches barely show: the 40 % shadow mix is only 6 levels under the base key.
   - Side and rear foliage is 15–25 darker than the sheet.
   - None of this is a family error: the rock is warm in every view and key (hue 20–23°, G − B ≥ 6), never mauve.
9. **Minor: process.** The f34 elevation probe at 8°, 12° and 16° (decision 5) isn't recorded in the stage notes.
   The 12° shot itself matches well (profile mean 0.063).

**The modeller's listed misses, judged:**

| Miss | Verdict |
| --- | --- |
| Green share | Blocker, inside finding 1 |
| Flowers in shade | Minor 3 |
| Side G dome | Minor 4 |
| A narrow from behind | Minor 5 |
| Rock-shape targets | Minor 6 |
| Overlaps | Minor 7; bigger than noted |
| Moss slightly yellow | Minor 2; B's mat more than A's cap |
| Rock darker / parts lighter | Minor 8 |

**Lighting and VFX.** The sheet shows no glow, light or particles, and the model has none: no sockets and no
emission. Stages 5 and 6 were rightly skipped.

### Decisions check

| Decision | Result |
| --- | --- |
| 1, size | Followed: 12.77 × 10.80 × 7.83; A 5.0 × 5.4 × 7.3 |
| 2, G and H from C | Followed (C's cloud yawed 150° / 70° and scaled) |
| 3, A pillar | Followed: H/W 1.46 |
| 4, moss | Followed: caps on A and B only in the hero; tuft on the RockC part |
| 5, cameras | Followed (f34 at 12°; the probe isn't recorded) |
| 6, packaging | Mesh rules followed: one hero of 194 closed manifold shells, 0 bowties, 0 self-hits, no booleans, `problems` checks closure. But the dressing is not seated (finding 1) |
| 7, solid shells | Followed |
| 8, hero + 6 parts | Followed |
| 9, no lighting or VFX | Followed |
| 10, colour | Followed: warm stone in every key, whole-facet patches, olive smears, three-band moss, three-tier leaves, nothing by facing (`K.check` clean) |
| 11, names | Followed |

### Score and verdict

**6.5 / 10. FAIL (round 1) on one blocker: floating, sparse, spiky foliage (finding 1).**

Everything else holds:
- the mesh is clean, and every budget and size is met;
- the rocks read as the sheet's group of big-faceted warm stones in the f34, front, rear and r34 (profile mean
  0.04–0.08);
- the colour families, calibration and position blending are right.

Send finding 1 to a fresh modeller, with findings 2 and 3 if they are cheap, then run a fresh verifier.

## Fix round 1 (fix modeller, 2026-10-29)

A fresh fix modeller did this round in a background Blender on port 9877, on the work file `wip/M036.blend` (saved).
The final numbers below come from `build()` run in a freshly restarted session. `problems` is empty. Every change is
in `m036.py`. The foliage code follows m035's fix round 1 (`_mound`, `_core`, `_Contact`, `contact_report`). It is
copied in, not imported.

### Blocker: floating, sparse, pointed foliage (finding 1)

**Dome mounds (`_mound`).** Leaves are laid over a dome instead of splayed out from a stem.
- Each leaf's middle sits on the dome. Its face points out of the dome, tilted toward straight up (`LEAF_UP` 0.65).
  Its tip points up toward the top.
- The leaf positions follow an even-area golden spiral over 4–98° from the top.
- Colour goes by height on the dome, never by facing:
  - low leaves take `leaf_deep` mixes and top leaves take `leaf_young`;
  - the outer 40 % of each upper leaf has a lime tip.

**Core per mound (`_core`).** Every low or tall mound has a heart: a closed 12-tri hexagonal bipyramid at 0.70 of the
mound's radius. It is leaf×deep 60, with its upper cone leaf×deep 20. Seen through the gaps, it reads as the clump's
shaded inside.

**Tall clusters, with no hidden stems.** FL1, FL3, FL6, FL9, FL10 and FL13 are each 2–3 overlapping mounds.
- Mound sizes (`TALL_MOUNDS`): radius 1.0, 0.85 and 0.72 of `0.42 × w`, with 9, 8 and 6 leaves.
- The ground mound sits on the ground.
- Each upper mound sits 45 % of the way from straight above the mound below to resting on the flank of its rock
  (`UPPER_LEAN`). Where the rock bulges out past the column, the mound rests on the flank.
- Their leaves stay within 110° of straight out from the rock.
- FL3 now rises from the ground in the B/C notch up to the A-foot flower. Before, it was a cluster perched on the
  rocks.

**Low and small clusters.** Each is one mound:
- low: 9 leaves, radius `0.38 × w`, with a core;
- small: 6 leaves, radius `0.36 × w`, no core.

**Contact (`_Contact`).** Every core, leaf and whole flower is placed against what is already there: the ground, the
rocks, the moss caps and the pieces placed before it.
- A piece more than 0.03 from all of these slides toward its nearest point until it is 0.015 away.
- The rock guard then runs again, so nothing cuts more than 0.05 into a rock.
- In the final build, 62 pieces moved; the furthest moved 0.64.
- A leaf more than 0.45 inside a rock is still left out: 12 leaves in all.

**Flowers.**
- Each flower sits on its mound's shoulder, on the side it faces, 0.95 of the mound's radius up. It is then slid into
  contact with the leaves.
- Each petal's base sits inside the yellow centre, so a flower is one touching group.
- Facing: FL8 and FL9 face the back (+Y); FL10 faces the back left, toward the r34 camera; FL1, FL3 and FL6 face the
  front.

**Leaf shape.** The leaves are now round spoons:
- two stalk corners (`LEAF_STEM` 0.22 of the half-width);
- widest at 0.55 of the length;
- a broad, blunt tip edge between two equal corners at 0.92 of the length, 0.74 of the width, with no tip point.

`LEAF_W` went from 0.95 to 1.0. Each leaf has a cupped top with a two-point midrib and a flat underside fan (fold
0.16, camber 0.24, curl 0.10). That is **12 tris a leaf** (was 14). Petals use the same rounded form, with no tip
point, at 10 tris.

**Size and density.**
- Leaves are 0.78–0.94 long in the low and tall mounds and 0.56–0.68 in the small ones. They are fewer, bigger and
  rounder than the sheet's, so the 4000 budget still gives the sheet's green share.
- Cluster widths went up by about 20 % (`CLUSTERS`).
- Moves, which keep the width inside its tolerance:
  - FL1 to (−4.7, −1.5), in front of B's left foot;
  - FL6 to (4.85, −0.05);
  - FL7 to (5.45, −1.95);
  - FL13 to (5.15, 2.1).
- FL9 is now 3.0 wide and 3.4 tall.
- FL10 is now 4.4 tall, up B's back; the rear cell's right foliage reaches h .66.

**`contact_report(o)` (new).** For each shell, it checks triangle overlaps and vert-to-surface gaps against every
other shell and the ground. It counts:
- shells touching nothing within 0.03, and the worst such gap;
- the largest gap from any non-rock shell to its nearest neighbour;
- shells with no chain of contact to the ground or a rock shell, at 0.03 and at 0.1.

`build()` runs it on all 7 objects and reports any floating or unchained shell as a `problem`.

### Minors

**A's moss cap (finding 2).**
- The main mat is 0.45 high at its centre (was 0.88), and the small mat 0.36 (was 0.42).
- Both mats moved toward the crown's high back-right side: (0.28, 0.38) and (0.62, 0.78) from A's centre.
- `ROS_TIP_Z` went from 0.85 to 1.2, so the lobe corners sit nearer the notch tops and the mat reads flat and lobed.
- Measured above the rock under each mat's top vertex, the cap is **0.27 and 0.31** thick.
- A flat cap would put the dressed height under 8.0 ± 0.3, so **rock A is now 7.6 tall (was 7.3)**. That is inside
  A's ±0.3, with H/W 1.52, inside 1.40–1.55.
- A's crown cut is a little flatter, (−0.08, −0.08, 1) instead of −0.10, which tilts the crown 12.5°.

**B's mat (finding 2).**
- The moss keys lost their blue:
  - `m036_moss` `#909A19` → `#8E9C08`;
  - `m036_moss_sun` `#AEB020` → `#A9B208`;
  - `m036_moss_deep` `#637511` → `#627606`.
- B's mat takes half the sun mixes (`CAP_SUN`).

**Petals (finding 3).** `m036_petal` went from `#C8CDCF` to **`#D6D3CA`**, a warm neutral white (R ≥ G > B). The
flower-cluster part renders its petals `#FFFFFE`.

**Back-view flowers (finding 3).** FL8, FL9 and FL10 sit on their mounds facing the back cameras. Three flowers show
in both `rear_sheet` and `r34_sheet` (checked by eye).

**Rock patches (finding 8).**
- `m036_rock_shadow` went from `#9D8F87` to **`#99897F`**, mixed up to 50 % (was 40). Its patches are now −3, −6 and
  −10 levels from the base `#AC9B94`.
- `m036_rock_light` went from `#BFAEA5` to **`#CDBCB2`**. Its patches are +6, +11 and +16.
- Every rock key is still R > G > B, with G − B ≥ 7.
- Area: plain rock 56 %, shadow mixes 23 %, light mixes 21 %.
- Small rocks (under 2 studs) get no light patches. On a lump that small, "upper" means the same faces as "facing up".
  `K.check` read the SmallRock part's colours as baked shading (0.53, then 0.82) until the patches were dropped.

**Leaf keys.** The upturned mound leaves catch the key light, so the keys went down:
- `m036_leaf` `#84B001` → **`#709601`**;
- `m036_leaf_young` `#99AE06` → **`#879904`**;
- `m036_leaf_deep` `#508801` → **`#447401`**.

**Camera probe (decision 5).** `f34_sheet` was rendered at three elevations and compared with the hero cell (W : H
1.433):

| Elevation | W : H | Profile mean / max | Green |
| --- | --- | --- | --- |
| 8° | 1.472 | 0.067 / 0.24 | .260 |
| **12° (kept)** | 1.404 | 0.064 / 0.21 | .265 |
| 16° | 1.342 | 0.060 / 0.17 | .270 |

12° stays. Its W : H is closest to the sheet's, and its profile mean is within 0.004 of 16°'s. The probe renders are
`f34_e8_sheet.png`, `f34_e12_sheet.png` and `f34_e16_sheet.png`.

### Before → after (round-1 verifier's numbers → this build)

| Measure | Target | Before | After |
| --- | --- | --- | --- |
| Hero tris | < 4000 | 3438 | **3898** (rocks 642, moss 378, leaves and cores 199 shells / 2388, petals 350, pollen 140) |
| Hero size W × D × H | 12.6 ± 0.5 × 10.8 ± 0.6 × 8.0 ± 0.3 | 12.77 × 10.80 × 7.83 | **13.01 × 11.24 × 7.83** |
| Shells (rock / moss / leaf + core / petal / pollen) | — | 12 / 4 / 136 / 35 / 7 | 12 / 4 / 199 / 35 / 7 (257) |
| Shells more than 0.03 from everything | 0 | 20 (worst 0.24) | **0** (largest gap from any shell to its nearest neighbour: 0.026) |
| Shells with no contact chain at 0.03 / 0.1 | 0 | 59 / 15 | **0 / 0** (all 7 objects) |
| Hovering flowers | 0 | 5 | **0** |
| Mesh errors per object and per shell (non-manifold edges and verts, boundary, wire, loose, zero-area, n-gons, duplicate verts, self-hits, inverted, volume ≤ 0) | 0 | 0 | **0** (smallest corner 7.2°) |
| UV overlaps / flipped; min gap; border; conformal p95 | 0 / 0 | 0 / 0; 0.016; 0.008; ≤ 1.041 | **0 / 0; 0.016; 0.008; ≤ 1.036** |
| `K.check` / baked shading | nothing / 0 | nothing / 0.0 | **nothing / 0.0 on all 7** |
| Leaf outline | rounded spoon | pointed kite, 14 tris | **blunt two-corner tip, 12 tris** |
| f34 rock / green / flower | .749 / .245 / .007; green ≥ .21 | .794 / .202 / .004 | **.727 / .269 / .004** |
| Front | .733 / .257 / .010; green ≥ .21 | .797 / .199 / .004 | **.733 / .264 / .003** |
| r34 | .751 / .242 / .007; green ≥ .22 | .817 / .183 / .000 | **.729 / .269 / .002** |
| Rear | .714 / .271 / .014; green ≥ .22 | .846 / .154 / .000 | **.747 / .251 / .001** |
| Side | .706 / .282 / .012 | .824 / .176 / .001 | **.764 / .235 / .001** |
| Top | .706 / .288 / .006 | .664 / .330 / .006 | .643 / .349 / .008 |
| W : H f34 / front / r34 / rear / side / top | 1.433 / 1.425 / 1.409 / 1.397 / 1.234 / 1.081 | 1.382 / 1.445 / 1.529 / 1.486 / 1.266 / 1.188 | 1.395 / 1.462 / 1.544 / 1.522 / 1.277 / 1.161 |
| Profile mean / max, f34 / front / r34 / rear / side / top | — | .063 / .16, .042 / .12, .071 / .26, .079 / .26, .170 / .56, .080 / .53 | .064 / .21, .040 / .12, .068 / .27, .074 / .25, .176 / .56, .056 / .52 |
| A's cap thickness at its centre | 0.25–0.4 | 0.88 | **0.27 / 0.31** (main / small mat) |
| A's cap colour, f34 / front | `#AFB90F` / `#B3B90A` | `#B4BC1E` / `#B8C022` | **`#AEBA0F`** / `#B4BF10` (sat .92 / .92) |
| B's mat colour, f34 / front | `#B4B911` / `#ADB50C`, sat about .90 | `#C5C634` (sat .74) / `#C5C725` | **`#B7C311`** (sat .91) / `#B7C30E` (sat .93) |
| Foliage colour, f34 / front / rear / side | `#729506` / `#789607` / `#7E9C07` / `#7B9906` | `#719011` / `#59790A` / — / `#5F7F0B` | `#749E07` / `#729B07` / `#6B9106` / `#5F8305` (measured before the final leaf-tip change) |
| Rock median, f34 / front | `#C0A597` / `#C4A899` | `#B8A091` / `#B7A091` | `#B9A293` / `#B49E8E` |
| Petal key | warm or neutral white | `#C8CDCF` (B > R) | `#D6D3CA`; part petals render `#FFFFFE` |
| Rock patches, levels from the base key | about 10 | −6 / +9 at most | **−10 / +16 at most** |
| Flowers visible in rear / r34 | ≥ 1 | 0 by mask (grey petals) | **3 / 3** by eye; flower share 0.001–0.002 |
| Part tris: RockA / RockB / RockC / SmallRock / Foliage / FlowerCluster | < 1000 | 338 / 346 / 150 / 64 / 126 / 266 | 314 / 320 / 150 / 64 / 120 / 260 |
| RockA part's cap / RockB part's mat (parts shot) | `#B3BA1B` / `#AEB916` | `#AFB125` / `#C5C823` | `#ADB60F` / `#B7C30C` |
| Foliage part / FlowerCluster part leaves | `#88B205` / `#90B508` | `#88AF0F` / `#82AC10` | `#7BB207` / `#79AB07` |

### Looked at, against the sheet

- **f34 and front.**
  - The left tuft wraps B's left foot to about half B's height.
  - A leafy column fills the B/C notch up to the A-foot flower, and low clumps flank E.
  - The right column stands between C and A, with two flowers.
  - Every clump reads as a rounded leafy mass, with deep green showing between the leaves.
  - A's cap is a flat lobed mat on the crown, and B's mat is lime rather than pale yellow.
- **Rear and r34.** Clumps sit on and beside G, between G and H, and up B's back between H and B. Each has one flower
  facing the camera.
- **Side.** FL6 is a stack of touching mounds in front of A, no longer a ladder of separate leaves.
- **Parts.** Foliage and FlowerCluster read as chunky rosettes of round, blunt-tipped leaves. The bud sits at the
  FlowerCluster's foot, in contact.

### Left over

- **Leaves are bigger than the sheet's:** 0.78–0.94 long against 0.45–0.6. That was the only way to reach the sheet's
  green share inside 4000 tris. Close up, the parts show fewer, larger leaves than the exploded clusters.
- **Width.** The hero is 13.01 wide against 12.6 ± 0.5: inside, but near the edge. The rear and r34 W : H are
  1.52–1.54 against 1.40–1.41. A is narrow from behind (decision 3), and the wider foliage adds to it.
- **Flower share** is still 0.001–0.004 against the sheet's 0.007–0.014. The flowers are a few pixels in the
  480 × 400 shots, and the back ones render in shade.
- **Back and side greens, and A's cap from behind,** are 15–25 levels darker than the sheet (`#6B9106` against
  `#7E9C07` in the rear). As in round 1, that comes from the studio key light, which is in front.
- **Side cell** profile is 0.176 mean / 0.56 max, from G's full dome (minor 4, accepted).
- **Leaf cuts into rock.** The guard allows 0.05. Against the rocks, FL3's notch column dropped 8 leaves and FL9
  dropped 2.
- **Not re-measured this round:** the §2.2 rock-shape metrics for B–H and the small rocks. Their builders didn't
  change; only A's height and crown cut did. A: 66 tris, H/W 1.52, widest at h .35, largest front facet .193, crown
  tilt 12.5°.

## Verification round 2 (verifier, 2026-10-29)

A fresh verifier did this round, read-only, in a background session on port 9877 against `wip/M036_verify.blend`.
Nothing was built, edited or saved.
- The session's material hexes were checked equal to `PALETTE` before `palette()` re-registered the keys for the
  render helpers.
- Every number below was re-measured through the MCP: `M.audit`, my own bmesh shell, contact and penetration code, plus
  `m036.contact_report` and `K.check` for comparison.
- Renders went to `…/scratchpad/m036_verify2/renders/M036/` (`m036.render_views` with `M.MODEL_RENDERS` redirected in
  memory).
- Colours were sampled on both the sheet and the renders with the study's masks: `m036.compare`, plus my own boxes for
  the caps, B's mat, the foliage quartiles and the whites.

### Measured

| Object | Tris (limit) | Size W × D × H | Shells | Non-manifold edges / verts | Boundary, wire, loose | Zero-area, n-gons | Self-hits / volume ≤ 0 | Min corner | Normals, origin, transforms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `MossyRockCluster` | 3898 (4000) | 13.01 × 11.24 × 7.83 | 257 (12 rock, 4 moss, 199 leaf + core, 35 petal, 7 pollen) | 0 / 0 | 0, 0, 0 | 0, 0 | 0 / 0 | 7.2° | outward; bbox bottom centre (0, 0, 0); rot 0, scale 1 |
| `…RockA` | 314 (1000) | 5.00 × 5.40 × 7.83 | 3 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 / 0 | 7.6° | ok |
| `…RockB` | 320 (1000) | 4.80 × 4.40 × 4.70 | 9 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 / 0 | 7.4° | ok |
| `…RockC` | 150 (1000) | 4.50 × 4.80 × 3.48 | 2 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 / 0 | 7.6° | ok |
| `…SmallRock` | 64 (1000) | 1.00 × 0.90 × 0.80 | 1 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 / 0 | 7.4° | ok |
| `…Foliage` | 120 (1000) | 1.75 × 1.82 × 1.15 | 10 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 / 0 | 12.6° | ok |
| `…FlowerCluster` | 260 (1000) | 1.79 × 1.87 × 1.08 | 22 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 / 0 | 12.6° | ok |

- **Other mesh results.**
  - No duplicate verts, custom normals, modifiers, children or sockets.
  - UVs: 0 overlaps and 0 flipped on all 7 objects; min gap 0.016, border 0.008, conformal p95 ≤ 1.036.
  - `K.check` returns nothing, and baked shading is 0.0 on all 7 objects.
  - Collision tags: the hero and the rock parts `hull`, Foliage and FlowerCluster `none`.
- **Floating dressing (the round-1 blocker).** My own code built a BVH per shell. It sampled verts, edge quarter points,
  face centres and face-to-vert midpoints both ways for every pair within 0.12. It counted triangle overlap as 0 and used
  the ground at z 0.
  - Hero: **0 shells more than 0.03 from everything** (also 0 at 0.05 and 0.1). The largest gap from any dressing shell
    to its nearest neighbour is 0.026.
  - Gap histogram over the 245 dressing shells: 212 touching (0), 12 within 0.01, 19 within 0.02, 2 within 0.03.
  - **0 unchained shells** (no contact path to the ground or a rock) at 0.03, 0.05 and 0.1.
  - The parts have 0 floating and 0 unchained shells too.
  - `m036.contact_report` agrees on every object.
- **Hovering flowers: 0 of 7.** A flower here is a petal + pollen group. Each group's gap to its nearest leaf, core, rock
  or the ground:
  - 0.0, 0.0, 0.0, 0.015, 0.015, 0.015;
  - 0.026 for FL1 at (−5.7, −2.0, 2.5), the closest to the limit.
  - The FlowerCluster part's flower and bud: 0.002 and 0.012.
- **Rocks (hero; my bbox per shell).**
  - A 5.0 × 5.4 × **7.6** (H/W 1.52, 118 tris with the smear refine).
  - B 4.8 × 4.4 × 4.7 (H/W 0.98).
  - C 4.5 × 4.8 × 3.2 (0.71).
  - G 4.2 × 4.2 × 3.35 (0.80).
  - H 4.7 × 3.8 × 2.8 (0.60).
  - Small rocks: D 1.0 × 0.9 × 0.8, E 1.7 × 1.4 × 1.0, F 1.4 × 1.3 × 1.2, D2 the same as D, E2 1.4 × 1.2 × 0.8, F2
    1.1 × 1.0 × 0.9.
  - Pebble 0.5 × 0.45 × 0.3.
  - Every rock is inside §2.1 ± 0.3; A is at the top edge.
- **Moss mats.** Thickness here is the mat's top surface above the rock's top surface, on a 15 × 15 vertical-ray grid.
  - A main: 2.09 × 1.87, 126 tris, thickness median **0.22**, p90 0.33, max 0.39.
  - A small: 0.88 × 0.93, median 0.17, max 0.31.
  - B main: 2.48 × 1.58, median 0.24, p90 0.35, max 0.41.
  - B small: median 0.17, max 0.29.
  - Every mat touches its rock (gap 0.0). Moss sits only on A and B in the hero; the RockC part has its one tuft.
- **Leaves.** 199 leaf and core shells. Leaf length (the largest spread between two verts), p5 / p25 / median / p75 / p95:
  0.68 / 0.85 / 0.91 / 0.94 / 1.25. The sheet's are 0.45–0.6.
- **Penetration.**
  - Leaves and petals into rock (ray parity; depth to the nearest rock surface): 15 shells deeper than 0.05, 5 deeper
    than 0.15, max 0.47.
  - The fix note says nothing cuts more than 0.05 into a rock; that doesn't hold.
  - These leaves are hidden in joints, and it is no worse than round 1 (9 deeper than 0.05, max 0.40).
- **Sheet comparison** (`m036.compare`; the sheet's value in brackets). It reproduces the fix modeller's table exactly.

| Shot vs cell | W : H | rock / green / flower | profile mean / max | rock median | green median |
| --- | --- | --- | --- | --- | --- |
| f34_sheet (0, 12) | 1.395 (1.433) | .727 / **.269** / .004 (.749 / .245 / .007) | 0.064 / 0.21 | `#B9A293` (`#C0A597`) | `#7EA408` (`#7F9E08`) |
| front_sheet (0, 8) | 1.462 (1.425) | .733 / **.264** / .003 (.733 / .257 / .010) | 0.040 / 0.12 | `#B49E8E` (`#C4A899`) | `#7CA209` (`#829D08`) |
| r34_sheet (208, 12) | 1.544 (1.409) | .730 / **.269** / .002 (.751 / .242 / .007) | 0.068 / 0.27 | `#B39F95` (`#BEA395`) | `#6C9107` (`#849E06`) |
| rear_sheet (180, 8) | 1.522 (1.397) | .747 / **.251** / .001 (.714 / .271 / .014) | 0.074 / 0.25 | `#B4A198` (`#BFA496`) | `#6D9207` (`#849F08`) |
| side_sheet (90, 8) | 1.277 (1.234) | .764 / .235 / .001 (.706 / .282 / .012) | 0.176 / 0.56 | `#9F8C82` (`#B09991`) | `#648506` (`#7E9B08`) |
| top_sheet (0, 89) | 1.161 (1.081) | .643 / .349 / .008 (.706 / .288 / .006) | 0.056 / 0.52 | `#CAB5A8` (`#C8AB9D`) | `#81A208` (`#759307`) |

  The green share now meets the targets:
  - f34 and front, at least 21 %: 26.4–26.9 %;
  - r34 and rear, at least 22 %: 25.1–26.9 %;
  - side: 23.5 %.
- **Colour by region** (my boxes, medians; sheet → ours).
  - A's cap (top 15 % of the silhouette):
    - f34 `#B0BA0F` → `#AEBA0F` (hue 64° in both, sat .92 in both);
    - front `#B5BB0A` → `#ADB810`;
    - darker in the back views: r34 `#B9BE0E` → `#9DA90B`, rear `#BDBF0C` → `#99A70B`.
  - B's mat: f34 `#B7BC12` → `#B8C410` (sat .90 → .92).
  - Foliage below h .6: f34 `#729706` → `#7CA308`; front `#7A9807` → `#7AA208`; rear `#7E9C07` → `#6B9106`; side
    `#7B9906` → `#5E8306`. Hue 75–78° against the sheet's 72–75°.
  - Foliage lit quartile: about 20–40 levels below the sheet's in every view (f34 `#BED10B` → `#A4C20E`, rear `#C5CE13` →
    `#86A312`). The sheet's bright yellow-lime leaf tops are muted in ours.
  - Petals: warm white (hue 35–47°, sat .11; `#E6DFCD`–`#FFF9E4`), no longer blue-grey. The part shot reads `#FFFFFE`.
  - Rock: every view's median is R > G > B, hue 19–25°, sat .18–.21, G − B 9–15 (f34 hue 24°, front 25°, rear 19°, r34
    20°, side 21°, top 23°). Warm, never mauve.
- **Keys.**
  - Every rock key is R > G > B with G − B at least 7: rock `#AC9B94`; shadow mixes `#A99890` / `#A6958D` / `#A2928A`;
    light mixes `#B2A199` / `#B7A69E` / `#BCACA3`.
  - Moss `#8E9C08`, its sun mixes up to `#9CA708`, its deep mix `#788907`.
  - Leaf `#709601`, deep mixes `#678F01`–`#568201`, young `#879904`.
  - Petal `#D6D3CA`, pollen `#B1AC01`.
  - No `FB_m036_*` material has emission.
- **Colour against facing.**
  - Key luminance against normal z: rock 0.23, moss −0.02, leaf 0.23. Against height: rock 0.29, moss 0.09, leaf 0.49.
  - Both follow from position fields: the rock's light patches sit on each rock's upper 40 %, and the leaves are tiered
    by height on the dome.
  - `K.check` baked shading is 0.0 everywhere.
  - The Tint corner layer runs 0.916–1.076 (std 0.024): broad, not confetti.

### Findings

1. **Resolved (was the blocker): floating, sparse, pointed foliage.**
   - Floating: 0 shells more than 0.03 from everything (round 1: 20), 0 unchained (round 1: 59) and 0 hovering flowers
     (round 1: 5).
   - Sparse: the green share is 25–27 % in the four main cells (round 1: 15–20 %).
   - Pointed: the leaves end in a blunt two-corner edge, not a point.
   - In the junction close-up, FL3 is a continuous stack of touching leaves up the B/C notch, with its flower seated on
     top. The side view's FL6 is a stack of mounds, not a ladder.
2. **Minor (the main leftover): the clumps read as large-leaf ivy mounds, not the sheet's small upright clover
   rosettes.**
   - The sheet's clusters are compact rosettes of about 8–10 small convex spoon leaves with their tips up, a tall
     central leaf and bright yellow-lime tops.
   - Ours have fewer, bigger, flatter leaves (median 0.91 long against 0.45–0.6).
   - The leaf outline is a hexagonal plate (two stalk corners, two shoulders, two tip corners). It is no longer the
     round-1 kite, but it isn't a true rounded spoon either.
   - In the r34, the rear and the front's left tuft, many leaves splay out and hang down the column, so those clumps
     read like ivy curtains.
   - `part_foliage` shows 3–4 dominant leaves rather than a rosette, and the exploded shot's clusters read as low,
     splayed mounds.
   - The lit quartile is 20–40 levels duller than the sheet's.
   - They are still green, leafy mounds in the right places at the right share, so the group still reads as the sheet's
     mossy rock cluster. At 3898 of 4000 tris there is no room for smaller, more numerous leaves.
   - **Fix target** (only in a later polish pass):
     - leaves 0.55–0.7 long, tipped up (not splayed or hanging) on each mound's top half;
     - a raised central leaf per rosette;
     - the young lime tips toward `#BED10B` (the sheet's lit quartile);
     - pay for it by dropping hidden back and inner leaves.
3. **Minor: the leaf-size trade-off.** Accepted as the price of the green share inside 4000 tris (see 2).
4. **Minor: hero width 13.01** against 12.6 ± 0.5. That is inside the limit by 0.09; D 11.24 is inside its ±0.6 by
   0.16. Accept. A later foliage change must not push W past 13.1.
5. **Minor: rear and r34 W : H 1.52–1.54** against 1.40–1.41. The profiles still fit (mean 0.068 and 0.074). The cause
   is A's decision-3 width plus the wide side columns. Accept.
6. **Minor: rock A is 7.6 tall.**
   - That is at the top edge of 7.3 ± 0.3, with H/W 1.52 inside 1.40–1.55.
   - The dressed height of 7.83 is inside 8.0 ± 0.3.
   - On the scale shot A reads correctly as the tallest rock, a little over head height. Accept.
7. **Minor: low flower share.** The share is 0.1–0.4 % against 0.7–1.4 %, but 3–4 flowers show in every elevation view,
   in the sheet's places. The back-view flowers render cream in shade. Accept.
8. **Minor: A's moss cap has the right thickness but a modest read.**
   - The main mat is median 0.22, p90 0.33 and max 0.39 thick: a flat lobed mat inside the 0.25–0.4 target.
   - The sheet's cap is a brighter, deeper-lobed star that drapes further.
   - In the rear and r34, ours reads as a thin strip, 25 levels darker than the sheet's (`#99A70B` against `#BDBF0C`;
     the studio light is in front). Accept.
9. **Minor: A's olive smear** reads as one hard-edged, dark khaki facet on A's upper-left face in the f34 and front. The
   sheet's hero shows no visible smear there. **Fix target** (optional): halve its mix (35–55 %) so it reads as a tint,
   not a patch.
10. **Minor: leaves cut into rock deeper than the fix note claims.** 15 shells go deeper than 0.05 (max 0.47), all
    hidden inside joints. Accept, and correct the note.
11. **Minor, carried over and accepted in round 1:**
    - the side cell's profile, 0.176 / 0.56 (G's full dome);
    - the §2.2 wall-share and area-CV misses;
    - rock overlaps beyond §6 (hidden);
    - the hero rock median 7–16 levels under the sheet (lighting), and the parts 10–25 over it;
    - back-view greens 10–20 levels darker.

**The fix's claims, checked.** Every number in the fix's before → after table reproduces: tris, sizes, shells,
contact, shares, W : H, profiles, part tris, UV and `K.check`. The one exception is the leaf-into-rock limit
(finding 10).

### Decisions check

| Decision | Result |
| --- | --- |
| 1, size | Followed: 13.01 × 11.24 × 7.83 (inside ±0.5 / ±0.6 / ±0.3); A 5.0 × 5.4 × 7.6, inside ±0.3 |
| 2, G and H from C | Followed (G 4.2 × 4.2 × 3.35, H 4.7 × 3.8 × 2.8) |
| 3, A pillar | Followed: H/W 1.52 |
| 4, moss | Followed: mats on A and B only in the hero; tuft on the RockC part |
| 5, cameras | Followed. The 8 / 12 / 16° probe is now recorded, and 12° is kept |
| 6, packaging | Followed: one hero of 257 closed manifold shells, 0 bowties, 0 self-hits, no booleans. `problems` checks closure and contact |
| 7, solid shells | Followed |
| 8, hero + 6 parts | Followed |
| 9, no lighting or VFX | Followed: no sockets, no emission |
| 10, colour | Followed: warm stone in every key and view (G − B at least 7 in the keys), whole-facet patches, olive smears, three-band moss, tiered leaves. Nothing by facing (`K.check` clean, baked 0.0) |
| 11, names | Followed |

### Score and verdict

**7.5 / 10. PASS (round 2).**
- The round-1 blocker is fixed, by measurement: 0 floating shells, 0 unchained shells, 0 hovering flowers, and the
  green share at the sheet's level.
- The mesh is clean on all 7 objects, and every budget, size and decision is met.
- The rocks read as the sheet's group of big-faceted warm stones in every comparable view.

The leftovers are minors 2–11. The largest is the foliage style: big, ivy-like leaves instead of small, upright clover
rosettes. The main session should commit with these noted.

## Main session ruling (2026-10-29)
- **Result:** passed in round 2 (7.5/10) and committed. Round 1 failed (6.5/10) on floating, sparse, pointed foliage. The fix reused M035's contact-seated mound code.
- **Left for a later polish pass:**
  - Foliage reads as big-leaf ivy mounds, not small upright clover rosettes. Target: leaves 0.55–0.7 long and tipped up, a raised central leaf, young tips toward `#BED10B`. Pay for it by dropping hidden leaves.
  - Width is 13.01; don't let it pass 13.1.
  - Rock A is at 7.6, the edge of its tolerance.
  - A's olive smear reads as a hard khaki facet. Mix it at 35–55 %.
  - 15 leaves cut up to 0.47 into rock at hidden joints. The fix note claimed none went past 0.05; that claim is wrong.
  - Back greens are dark (studio light).
- **Export:** 7 assets, 7 solid pieces, 5126 tris, 0 VFX sockets, palette 25 colours, 0 problems.
