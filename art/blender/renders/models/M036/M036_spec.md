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
