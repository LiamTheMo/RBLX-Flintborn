# 035 Boulder — spec

Reference: `art/blender/assets/references/035.png` (1024 × 1536 px). The sheet's own title is "BOULDER", with the
subtitle "Squat, large-facet rock with moss." and "PAGE 37/132" at the top right; the footer reads "FLINTBORN — INDIVIDUAL
MODEL STUDY". INDEX.md row 35 calls it "Flintborn boulder model study".
Builder: `art/blender/kit/mcp/m035.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7).

Sheet text:
- **Header:** "BOULDER"; "Squat, large-facet rock with moss."; "PAGE 37/132".
- **View labels:** "ASSEMBLED FRONT 3/4 VIEW", "ASSEMBLED REAR 3/4 VIEW", "FRONT VIEW", "SIDE VIEW", "REAR VIEW",
  "TOP VIEW".
- **Material palette:** Rock Light, Rock Mid, Rock Shadow, Moss Green, Foliage Light.
- **Parts (exploded view):** "Moss Cap (separate)", "Main Rock (mesh)", "Small Rock (mesh)", "Foliage Cluster (mesh)".
  Dashed arrows drop the cap onto the crown and pull five small rocks and six foliage clusters away from the foot.
- **Part list:** "1 × Moss Cap (separate)", "1 × Main Rock (mesh)", "3 × Small Rocks (mesh)" (two drawn),
  "4 × Foliage Clusters (mesh)" (one drawn, with a white flower).
- **Detail close-ups:**
  - "Moss Cap Underside": "Simple, low-thickness mesh. Attaches to top of main rock."
  - "Rock / Foliage Junction": "Separate meshes. Slight gaps OK. Interlocking composition."
  - "Small Rock Detail": "Thick, low-poly form. Broad flat faces, no fine detail."
- **Modeling notes:**
  - "Keep low-poly, chunky, and readable with broad flat-shaded faces."
  - "Moss cap, small rocks and foliage are separate meshes."
  - "Use simple, solid colors from palette. No texture noise or fine surface detail." (but see §3.9)
  - "Maintain the recognizable silhouette from the concept sheet."
  - "Clean topology with clear joins and logical pivots."
  - "Designed for modular reuse and easy variation (scale/rotation)."
- **Game context:** an environment prop. The name `Boulder` and its parts are taken: W01 (the earlier kit sheet, a
  near-identical mossy boulder, passed round 5 at 8/10) owns `Boulder`, `BoulderMainRock`, `BoulderMossCap`,
  `BoulderFlat`, `BoulderUpright` and `BoulderSplit`; sheet 06 owns `LowBoulder`, `TallBoulder`, `SplitBoulder` and
  `LongBoulder` (§8). W01's builder (`art/blender/kit/mcp/w01.py`) already has recipes for this subject:
  `moss_mounds` (leafy moss cap), `herb_bush` / `K.clover` (leaf clumps), `flower5` (white five-petal flower) and
  `crease`. Its goals file (`art/blender/renders/kit/W01/boulder_goals.md`) records five verifier rounds lost to a flat
  moss decal, a "melted" rock, blade-like herbs and soft facets: read it before modelling.

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is
`#FAF6EB` (250, 246, 235), tolerance 12. The masks are `cls()` in `m.py` (HSV):
- **R, rock:** hue ≤ 48° or ≥ 190°, sat 0.035–0.40, v 0.25–0.97, and not G/F/B. Lit rock faces are warm (hue 18–28°),
  shaded faces cool lavender (hue 250–340°), both in R.
- **G, green:** hue 48–140°, sat ≥ 0.30, v ≥ 0.15. Moss cap and foliage; split by position (the cap is the green
  above 0.55 H, `capshare.py`).
- **F, flower:** white petals (sat < 0.12, v ≥ 0.95) and yellow centres (hue 38–48°, sat ≥ 0.55). Under 1 %.
- **B, ground shadow:** neutral grey, sat < 0.035, v 0.45–0.95 (`#B1B1B1`). **Treated as background**: it is not in
  any silhouette, profile or share below.
- **O, other:** dark creases, outlines and anti-aliasing; in silhouettes but not in the shares (3.1–4.7 %).
- The palette title "MATERIAL PALETTE" pokes into the f34 box; `m.py` paints (160–186, 140–170) as paper.

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m035_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14 with Pillow and numpy; no scipy, so `m.py` has
its own `label()`).
- **Helpers:** `m.py` (masks `cls()`, view boxes `V` and `X`, `preview()`, `label()`), `zoom.py` (crop + upscale).
- **Measurements:** `measure.py` → `measure_out.txt` and `bb.json` (silhouettes, shares, top/bottom profiles, width
  per height, rock and green components); `mainrock.py` → `mainrock_out.txt`, `mainrock.json` and `main_*.png` (the
  main rock alone); `facets.py` → `facets_out.txt` and `facets_*.png` (flat-facet segmentation); `capshare.py` →
  `capshare_out.txt` (cap against foliage); `rockrun.py`, `rockbot.py`, `base.py` (rock runs, bottom outline);
  `expl.py` → `expl_out.txt` (exploded and part-list boxes); `flowers.py`.
- **Colour:** `samp.py` → `samp_out.txt` (swatches; medians, lit and shade quartiles and deciles per region).
- **Names:** `blendall.py`, `names.py` (every sheet and wip `.blend`, zstd-decompressed).
- **Crops:** `f34.png`, `r34.png`, `row2.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `cu.png`,
  `partlist.png`, `pal.png`, `pal_sw.png`; mask previews `cls_*.png`.
- **Zooms:** `z_f34_cleft.png` (the cleft and its moss), `z_f34_moss.png` (the cap rosettes), `z_f34_bot.png` and
  `z_r34_bot.png` (rocks, foliage and flowers at the foot), `z_expl_main.png` (the exploded main rock and its stain),
  `z_junc.png` (the junction close-up), `z_top_back.png` (the top view's back rim).
- **To run the scripts on our renders:** point `R` (in `m.py`) at the render, set `P` to its background colour, set
  the boxes in `V` to the render cells, delete the f34 title patch, and re-run `measure.py`, `mainrock.py`,
  `facets.py` and `capshare.py`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (an environment prop: landmark and cover rock). Hero budget 4000 tris, each part
  under 1000. The plan in §4.3 lands at about 2700–3200.
- **Overall read (check this first).** A **squat, broad-faceted, warm grey-pink boulder** with:
  - a **leafy lime moss cap** of 4–5 lobed rosette mounds on its crown, spilling down over the lower left shoulder;
  - a **deep vertical cleft on its front-left face**: a big front-right mass overlaps a smaller, lower left mass, and
    a tuft of moss sits in the foot of the cleft;
  - **chunky round-leaf foliage clusters** tucked round the left, back and right of the foot (low ones at the front,
    tall stacked ones against the flanks), three with a white five-petal flower;
  - **five small faceted rocks** and one pebble round the foot.
  - The front of the foot (f .45–.75 in the front views) stays open: bare rock meets the ground there.
  - Hero shares: rock 73.7 %, green 25.8 % (cap 10.9 %, foliage 14.9 %), flowers 0.5 %.
- **Focal silhouettes, in order:**
  1. The rock's barrel-dome outline: steep, slightly bulging sides, widest at about half height, a broad near-level
     crown with a rounded shoulder band. About 11–15 outline corners. Not a ball, not an icosphere.
  2. The cap's lobed, scalloped crown (f .35–.71 of the hero) rising 0.15–0.2 of the height above the rock.
  3. The cleft: a dark V running down the front-left face from about 0.7 of the rock's height to the ground.
  4. The foliage tufts at both ends of the silhouette (reaching h .41–.54) and the small rocks at the foot.
- **Target size: rock 9.0 W × 8.3 D × 6.4 H (crown); dressed 12.0 W × 11.1 D × 7.8 H studs** (cap peak 7.8 = 1.42 ×
  the 5.5-stud character; rock crown 1.16 ×). Tolerances: rock W ±0.3, D ±0.3; dressed W ±0.5, D ±0.6, H ±0.3.
  Decision §8.1.
  - **How it was derived.** The sheet has no character. Ratios are measured (§1.2): rock D/W 0.92 (side cell against
    front cell, which are drawn at the same scale: 20.5 and 20.4 px/stud for these sizes); rock crown 0.69–0.75 of W
    after removing the elevation (f34 0.69–0.72, front 0.745); dressed W/rock W 1.33 (front 1.33, f34 1.34); dressed
    D/W 0.92 (top view 219 × 202 px); cap peak 0.82–0.93 of rock W (f34 and front respectively).
  - **Why this size.** A rock a little taller than the character: good cover and a landmark, not a mountain. It sits
    between the old kit's boulders (sheet 06 `LowBoulder` 8 × 6 × 4, `TallBoulder` 6 × 5 × 8; W01 `Boulder` rock 11.6
    × 10.7 × 6.4, dressed 15.6 × 12.6 × 7.0), so it adds a mid size instead of repeating W01. At this size the
    flowers are 0.45 across, the foliage leaves 0.5–0.7 long and the small rocks 1.2–1.8 across, all reasonable
    against a 5.5-stud character.
- **Build frame:** front −Y, +X right, ground z 0, origin = the main rock's base centre on the ground. Stage 2
  re-centres the hero on its bbox bottom centre.

### 1.2 Measured views (`measure.py`, `mainrock.py`, `capshare.py`)

| View (box) | Silhouette bbox (px) | W : H | Rock R | Green G (cap / foliage) | Flower F | Main rock box (px) | Rock W : H | px/stud |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (165,112,598,427) | 170–583 × 126–406 | 1.473 | 73.7 % | 25.8 % (10.9 / 14.9) | 0.5 % | x 224–534 (row run), y 160–397 | 1.31 | 34.4 |
| Rear three-quarter (603,112,1009,427) | 626–985 × 130–398 | 1.338 | 70.8 % | 28.8 % (11.2 / 17.5) | 0.4 % | 667–936 × 164–385 | 1.216 | 30.6 |
| Front (14,462,276,695) | 22–265 × 487–665 | 1.363 | 74.7 % | 24.5 % (10.1 / 14.3) | 0.8 % | 51–234 × 515–661 | 1.252 | 20.4 |
| Side (280,462,518,695) | 287–511 × 487–666 | 1.250 | 74.1 % | 25.1 % (9.7 / 15.4) | 0.8 % | 317–486 × 516–659 | 1.181 | 20.5 (D 8.3) |
| Rear (522,462,763,695) | 529–757 × 487–666 | 1.272 | 71.5 % | 27.9 % (10.5 / 17.3) | 0.7 % | 554–743 × 510–661 | 1.250 | 21.1 |
| Top (767,462,1009,695) | 767–985 × 479–680 | 1.084 (W : D) | 67.0 % | 32.4 % (0 / 32.3) | 0.6 % | 802–956 × 500–659 | 0.969 | 17.2 |

- Shares are of R + G + F; the ground shadow (B) is background. **Verifier tolerance:** shares ±4 points (cap ±2,
  flowers ±0.5); positions ±0.06 of W/H unless stated.
- The f34's automatic main-rock box (187–537) merges the left small rock R1; the row run at h .40–.55 gives the rock
  alone (f .12–.88, 310 px).
- **Elevations.** The main rock's bottom outline rises only 6–10 px over its half-width in the front, rear and side
  cells (≈ 5–6°). The f34's bottom outline gives about 5–9°, but its small rocks' bottoms (R1 +17 px, R3 +47 px above
  the rock's front foot) need about 12–14° unless foliage hides their feet. Start at **f34 e 10°, front/rear e 6°,
  side e 5°**, and probe (§3.1).

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .24 | .42 | .48 | .55 | .70 | .75 | .79 | .85 | .90 | .93 | .97 | 1.0 | .98 | .94 | .90 | .85 | .81 | .72 | .55 | .44 | .26 |
| Front | .21 | .39 | .39 | .60 | .74 | .77 | .80 | .88 | .91 | .98 | 1.0 | .98 | .98 | .92 | .85 | .83 | .78 | .60 | .49 | .39 | .17 |
| r34 | .29 | .48 | .52 | .61 | .75 | .82 | .85 | .90 | .96 | .98 | 1.0 | .97 | .96 | .91 | .87 | .79 | .74 | .53 | .47 | .34 | .24 |
| Rear | .22 | .41 | .49 | .60 | .73 | .82 | .84 | .87 | .95 | .97 | 1.0 | .98 | .98 | .92 | .88 | .83 | .77 | .69 | .44 | .38 | .13 |
| Side | .22 | .31 | .43 | .51 | .65 | .77 | .80 | .88 | .92 | .97 | .99 | .98 | .96 | .94 | .89 | .82 | .77 | .61 | .42 | .30 | .13 |
| Top (h = back) | .48 | .54 | .59 | .69 | .87 | .88 | .87 | .87 | .93 | .99 | .99 | .96 | .93 | .93 | .91 | .92 | .90 | .81 | .82 | .79 | .48 |

- Front against f34: mean 0.040, max 0.12; rear against f34: 0.040 / 0.13; r34 against f34: 0.058 / 0.19
  (flipped 0.042 / 0.11, §3.2).
- The plateau at .90–1.0 over f .35–.70 is the cap; the steps at f .15–.25 (left) and .80–.90 (right) are the rock's
  shoulders meeting the foliage tufts.

**Bottom profiles** (lowest silhouette pixel; foliage and small rocks at the ends):

```
f34    .22 .12 .10 .06 .05 .02 .00 .01 .01 .04 .03 .03 .03 .05 .07 .06 .05 .06 .14 .14 .23
front  .17 .10 .07 .04 .02 .00 .02 .01 .02 .03 .02 .02 .02 .03 .05 .03 .02 .02 .04 .10 .16
r34    .27 .20 .08 .06 .03 .01 .01 .01 .03 .06 .06 .06 .06 .06 .09 .07 .05 .06 .08 .16 .21
rear   .19 .16 .04 .03 .01 .00 .01 .02 .02 .03 .03 .04 .03 .03 .05 .04 .03 .02 .03 .07 .12
side   .22 .07 .04 .03 .01 .00 .01 .02 .03 .03 .03 .04 .04 .04 .03 .03 .02 .02 .03 .09 .12
```

**Width per height, whole silhouette** (width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .05@.27 .81@.07 .97@.02 .97@.01 .94@.04 .81@.11 .71@.16 .65@.20 .50@.31 .31@.39 .02@.54
r34    .02@.31 .83@.08 .97@.03 .96@.00 .93@.02 .81@.06 .69@.15 .63@.18 .53@.22 .32@.35 .03@.48
front  .07@.22 .93@.03 .98@.00 .92@.03 .89@.05 .77@.12 .70@.15 .65@.18 .49@.29 .31@.36 .03@.50
side   .04@.24 .94@.05 .93@.03 .90@.04 .83@.08 .72@.15 .66@.19 .59@.23 .49@.28 .33@.36 .02@.51
rear   .06@.21 .92@.07 .97@.00 .93@.02 .90@.03 .76@.12 .72@.15 .66@.18 .53@.23 .32@.36 .03@.49
top    .07@.26 .49@.22 .74@.19 .80@.14 .99@.00 .97@.01 .84@.12 .77@.18 .75@.18 .43@.37 .03@.46
```

**Width per height, main rock only** (`mainrock.py`; width / the rock's own max width at the rock's h = 0.0 … 1.0;
below h .3 the elevation cells are cut by foliage and small rocks, so read the exploded and part-list rows for the
foot; the cap hides the crown's centre, so h .9–1.0 is shoulder to shoulder):

```
front  .20 .52 .71 .87 .97 .99 .98 .92 .87 .78 .04     widest at h .54
rear   .14 .65 .71 .85 .93 .94 .91 .85 .78 .66 .04     widest at h .47
side   .37 .51 .66 .79 .97 .99 .93 .87 .81 .74 .52     widest at h .48
expl   .05 .72 .78 .91 .97 .99 .95 .87 .79 .65 .13     widest at h .53 (no occlusion; seen from about 20° above)
plist  .12 .71 .91 .97 .98 .98 .88 .78 .64 .36 .04     widest at h .46 (drawn rounder and peakier)
```

So the rock is widest at h .45–.55, still 0.87–0.92 wide at h .7 and 0.78–0.87 at h .8 (a broad shoulder), and tucks
in to about 0.70–0.78 at h .1.

**Green components** (`measure.py`; extents in f across, h up; px = mask pixels):

| View | Cap | Foliage tufts |
| --- | --- | --- |
| f34 | f .35–.71, h .66–.99 (8147 px) | front-left group f .15–.43, h .00–.39 (two clusters plus the cleft moss); far-left f .00–.15, h .20–.49; right column f .83–.98, h .13–.54; front-right sprigs f .73–.82, h .08–.22 |
| Front | f .32–.69, h .69–.99 | left f .03–.40, h .01–.41; right column f .74–.99, h .09–.49 |
| r34 | f .35–.73, h .65–.99 | left tall f .00–.29, h .18–.53; front-left low f .20–.44, h .01–.20; right f .82–.99, h .16–.46 |
| Rear | f .36–.76, h .64–.99 (droops to the right) | left big f .01–.43, h .01–.48 (one flower at f .31, h .13); right f .86–.99, h .07–.43 |
| Side | f .34–.70, h .74–.99 | left f .04–.35, h .01–.43; right f .83–.99, h .09–.41; right low f .64–.84, h .04–.23 |
| Top | none drawn (§3.5) | one ring round the left, back and right (f .06–1.0); front-right f .53–.82, h .03–.26 |

**Small rocks** (read on the crops; centre f, extent; the f34's run splits them from the main rock):

| View | Rocks |
| --- | --- |
| f34 | R1 left foot f .04–.19, h .09–.25 (63 px = 0.20 rock W); R2 right-front f .75–.88, h .06–.19 (55 px = 0.18); R3 right-back f .87–.98, h .18–.34 (45 px = 0.15); pebble P1 (pinkish) f .18, h .12 |
| Front | R1 f .02–.17, h .06–.26 (0.20); R2 f .75–.90, h .03–.17 (0.20); R3 f .89–.98, h .16–.29 (0.13) |
| r34 | left near f .08–.24, h .06–.21; left far f .01–.08, h .21–.35; right f .73–.90, h .06–.22 (the largest, with a moss smear) |
| Rear | right f .76–.94, h .03–.18 (R5); a sliver at left f .16–.24, h .07–.17 (R4) |
| Side | left two: f .02–.12, h .02–.24 and f .08–.24, h .02–.16; right f .76–.93, h .03–.16 |
| Top (h = back) | top-left f .18–.30, h .74–.88; top-right f .83–.95, h .68–.82; right-lower f .80–.94, h .18–.33; bottom-centre f .57–.71, h .02–.16; bottom-left f .22–.37, h .01–.17; a sixth under the left foliage f .00–.04, h .39–.49. Two or three carry a moss patch on top. |

**Flowers** (white, five petals, yellow centre; on top of a foliage cluster): f34 2 (far-left f .09, h .32;
front-left f .34, h .10); front 2 (f .10, h .27; f .33, h .10); rear 1 (f .31, h .13); r34 none (one yellowish bud at
f .33, h .1); side none; top 2 on the right-hand ring; the part list's cluster and the junction close-up 1 each. Flower
Ø about 15 px in the f34 = 0.048 rock W ≈ 0.45 studs.

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, governs; `f34.png`, `z_f34_cleft.png`).** Not a real three-quarter: the same
drawing as the front cell at about the same, low elevation (§3.1).
- **Main rock:** a squat barrel dome, 310 px wide (f .12–.88), widest at mid height, its crown a broad near-level top
  hidden under the cap; the right shoulder shows at h .87, the left (lower) shoulder at h .71.
  - Big flat facets: 28 regions over 0.4 % of the rock's area, the largest 8.2 % (`facets.py`). Triangles of very
    different sizes; long sliver-like triangles run down the front, wide ones on the shoulder. Vertices join 5–7
    triangles. No even pentagon/hexagon pattern.
- **Cleft:** a V groove on the front-left face, from (f .34, h .70) down to (f .25, h .02). Left of it the left mass's
  lavender-shaded faces; right of it the front mass's left flank in shade, then its lit front. The front mass stands
  proud. A lobed moss tuft (`#4B6402` in shade) fills the cleft's foot from h .17 to .39.
- **Cap:** f .35–.71 (0.48 of the rock), 4–5 rosette mounds: a big one at the front-left, one behind and above it at
  the back, one on the right; the left lobes hang down onto the left shoulder (to h .66). Each rosette has a raised
  centre, 8–10 pointed, notched lobes and radial ridges: lime-yellow tops, deeper green in the notches.
- **Foliage:** far-left tuft with a flower (behind R1, to h .49); a low cluster in front of the cleft; a front-left
  cluster with a flower; a tall leafy column hugging the right flank (to h .54) behind R2/R3; a few sprigs between R2
  and the rock. Leaves are broad ovate, cupped, faceted solids with a pointed tip; outer leaves deeper green, inner
  upright ones lime-yellow.
- **Small rocks:** R1 at the left foot (in front of the far-left tuft), R2 at the right front, R3 at the right behind
  the foliage, P1 a tiny pinkish pebble left of the front-left cluster.
- **Ground shadow:** soft neutral grey to the left (light from the right); background.

**Front (`front.png`).** The f34 drawing again, a little taller (W : H 1.363 against 1.473): the cleft at f .30 →
.22, the cap at f .32–.69, the same three rocks and both flowers at the same fractions within 0.04.

**Rear three-quarter (`r34.png`, `z_r34_bot.png`).** A true back-right view (§3.2). The rock's broad faces are larger
here (17 regions, the largest 10.7 %); a crease runs down at f .71–.82 (the left mass's seam, seen from behind); the cap
droops to the right; tall foliage at the left, low foliage at the front-left, foliage at the right; two rocks at the
left, one large one at the right with a moss smear. No white flowers.

**Rear (`rear.png`).** A true rear view (az 180): the crease at the right (f .73–.84, the model's left), the cap
drooping to the right (the model's left, matching its droop to the left in the front), a big foliage mound at the left
(the model's back-right) with a flower, R5 at the right foot, R4 a sliver at the left.

**Side (`side.png`).** The kit side camera at +X (screen right = back, §3.4): a trapezoid barrel (W : H 1.181), steep
straight flanks, the cap centred (f .34–.70), two rocks at the front (left) and one at the back (right), foliage at
both feet. No cleft (it is on the far side). Its D is 0.92 of the front's W.

**Top (`top.png`, `z_top_back.png`; image top = back).** The rock as a roundish 11–13-sided polygon with one big
near-flat crown face (about 0.45 of the rock across, slightly right of centre), surrounded by a near-continuous ring
of foliage round the left, back and right, five small rocks round the rim (two with moss on top) and one under the
left foliage. A green moss stain shows on the lower left faces. **No moss cap is drawn on the crown** (§3.5).

**Close-ups.**
- **Moss Cap Underside** (24,1178,262,1384): the cap from below: a lobed, scalloped slab with a **flat brown
  underside** (`#725E45`, evenly lit) inside a thin lime rim band (about 0.08–0.12 of the cap's width thick). "Simple,
  low-thickness mesh."
- **Rock / Foliage Junction** (277,1178,512,1384): the front mass's left flank (big flat triangles) and, behind it
  across a gap, the left mass; a foliage cluster with a flower sits in the gap; a small rock (squat, eight-sided
  outline, broad faces) in front. Leaves touch the rock but don't cut into it. "Slight gaps OK."
- **Small Rock Detail** (528,1178,732,1384): a squat faceted pebble, W : H 1.18 on screen (h/w about 0.65–0.72), 14
  facet regions, the largest 23 % and the second 19 % of its area: few, broad faces.

### 1.4 Parts (Parts (Exploded View) (14,750,792,1131), `expl.png`; Part List (795,750,1009,1131))

Scale: the exploded parts are drawn larger against the main rock than in the hero (cap 0.63 of the rock's width
against 0.48; small rocks 0.16–0.30 against 0.13–0.21). **The hero governs every size**; the exploded gives shapes
and the part list.

#### Main Rock (272,823,569,1088), 298 × 266 px; Part List (808,827,898,919); `z_expl_main.png`

- **Shape:** a squat barrel dome, widest at h .5, a broad crown of 2–3 big near-level faces (a shadow marks where the
  cap sits), steep faceted sides, the foot tucked in a little to a flat bottom. Big irregular triangles (22 regions
  over 0.4 % of its visible area; vertex fans of 5–7). The exploded copy has **no cleft** (§3.6) and carries a green
  moss stain (two lobed patches, `#647430`) low on its left, shaded faces.
- **Hero size:** 9.0 × 8.3 × 6.4 (crown), as two masses (§2.1).
- **Construction:** `main_rock()` = the exact union of two `K.hull_rock(..., keep_bottom=True)` hulls (A, the
  front-right main mass; B, the lower left mass), not a vertex-pushed crease. Point sets for A, rings (height fraction,
  radius fraction, points): `(0.0, 0.82, 7), (0.14, 0.93, 7), (0.48, 1.0, 8), (0.74, 0.9, 7), (0.9, 0.62, 5),
  (1.0, 0.3, 3)` with radial jitter 0.10–0.12 and azimuth jitter ±0.35 of a step; B: `(0.0, 0.85, 6), (0.2, 0.95, 6),
  (0.55, 1.0, 6), (0.82, 0.78, 5), (1.0, 0.35, 3)`. Then **thin the rings** where a facet must be big: drop one point
  from the 0.48 and 0.74 rings of A on the front-right so that one or two facets reach the largest-facet target (§2.2).
  About 38 + 26 points → **about 70 + 45 tris before the union, 120–180 after**.

#### Moss Cap (333,724,521,811), 189 × 88 px; Part List (808,752,896,798); Moss Cap Underside close-up

- **Shape:** 4–5 overlapping lobed rosette mounds, about 2 : 1 long on screen from 20° above (true footprint about
  1.1 : 1). Each rosette: a raised centre, 8–10 pointed lobes with notches between, radial ridges from the centre to
  the lobe tips (so its top is a low faceted star cone), a thin vertical rim band, a flat underside. Rosettes overlap
  and the back one sits higher on the others. Lime-yellow tops, deeper green rims and notches, brown underside.
- **Hero size:** footprint 4.3 × 4.0 (0.48 of the rock's W and D), rim 0.15–0.25 thick, peaks 0.7–1.0 above their
  base; the stack's top 1.2–1.5 above the rock's crown.
- **Construction:** `moss_cap()`: per rosette `_rosette(r, h, lobes, seed)`: an outline of `lobes` tips at radius
  0.92–1.06 r and notches at 0.62–0.74 r, a top centre point at height h, one mid ring at 0.5 r and 0.55 h following the
  lobes (the ridges), the rim band 0.18 thick, and a flat underside fan. Conform the underside to the rock with
  `K.conform(verts, tree, sink=0.05)` so it hugs the crown and drapes over the left shoulder. W01's `moss_mounds` /
  `K.moss_slab` are the nearest recipes; this sheet's rosettes have more, sharper lobes (8–10, notched) than W01's
  oak-leaf mounds (5). **About 60–90 tris per rosette, 300–450 for the cap.**

#### Small Rock (×3 in the part list; 5 drawn in the exploded): (60,935,149,1012) 90 × 78, (161,1005,217,1052) 57 × 48, (214,1036,291,1101) 78 × 66, (308,1040,354,1088) 47 × 49, (455,1035,531,1086) 77 × 52 px; Small Rock Detail close-up

- **Shape:** squat faceted domes with flat bottoms; on screen W : H 1.15–1.48 (true h/w about 0.62–0.72), an outline of
  7–9 corners, 12–18 broad facets, a near-flat top facet; the same warm grey-pink as the main rock.
- **Three variants** (the part list's "3 ×"): **A 1.8, B 1.5, C 1.2** across; h = 0.66 w; plus a 0.5 pebble.
- **Construction:** `_small_rock(w, seed)` via `K.hull_rock` rings `(0.0, 0.9, 6), (0.35, 1.0, 7), (0.75, 0.75, 5),
  (1.0, 0.3, 3)`, `keep_bottom=True`, jitter 0.12: **about 30–36 tris** each.

#### Foliage Cluster (×4 in the part list; 6 drawn in the exploded): (167,837,241,909) 75 × 73, (90,888,169,979) 80 × 92, (607,905,668,959) 62 × 55, (661,943,739,1025) 79 × 83, (575,1025,659,1109) 85 × 85 px; Part List (816,1019,896,1088); junction close-up

- **Shape:** a rosette of broad ovate leaves (pointed tip, cupped, a raised midrib: K.leaf `shape="ovate"`, 12 tris)
  rising from one root point in 2–3 tiers: low outer leaves splayed out, inner leaves upright. 7–9 leaves in the
  exploded clusters, 10–14 in the part list and junction clusters. On screen W : H 0.87–1.16 (true h/w about
  0.75–0.95). One white five-petal flower with a domed yellow centre sits on top of the flowered variant.
- **Four variants** (the part list's "4 ×"): **low** (w 1.6–1.9, h 1.2–1.4, 10 leaves), **low + flower**, **tall**
  (w 1.6–2.2, h 2.4–3.2, 16–18 leaves in 3–4 tiers, leaning on the rock flank: the f34's right column and the rear's
  big mound), **small** (w 1.0, h 0.8, 6 leaves).
- **Construction:** `_cluster(kind, size, seed, flower=False)` from `K.clover` (tiers, `young_mat`) with
  `shape="ovate"` and W01's `flower5` for the flower (petals Ø 0.45, centre a 6-sided dome). Leaf length 0.5–0.75.
  **About 72 (small) / 120 (low) / 216 (tall) tris, + 84 per flower.**

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, origin = the main rock's base centre). The f34 is an aligned front
view, so screen x = plan X (34.4 px/stud in the f34, 20.4 in the front cell). Plan Y comes from the top view (scaled out
about 1.3× from the rock's centre: the top camera magnifies the tall rock against the ground pieces) and the side cell
(screen left = front, 20.5 px/stud).

### 2.1 Main rock, cleft and cap

| Piece | Base centre (x, y), base z | Size W × D × tall (top z) | Sheet evidence | Notes |
| --- | --- | --- | --- | --- |
| A, front-right main mass | (+0.6, −0.1), 0 | 7.6 × 8.1 × 6.4 (6.4) | f34 right edge f .88 (x +4.4), right shoulder h .87; crown under the cap | barrel dome; crown 2–3 big faces with normal z > 0.9 spanning ≥ 3.0 |
| B, left mass | (−2.3, +0.4), 0 | 4.6 × 6.6 × 5.2 (5.2) | f34 left edge f .12 (x −4.6), left shoulder h .71 (0.8 of A's crown); rear crease at the model's left | lean 0.06 toward A; its front face 0.8–1.2 behind A's front flank |
| Cleft (the A ∪ B seam) | front face from (−2.0, z 4.5) down to (−3.0, z 0) | groove depth 0.6–1.0 at mid height, opening 70–110° | f34 f .34 → .25; front f .30 → .22; rear crease f .73–.84 | real geometry from the union, not paint; fades out on the crown |
| Cap rosette M1 | (−0.8, −0.6) on A's crown | r 1.35, h 0.9 | f34 front-left rosette | the biggest |
| Cap rosette M2 | (+0.3, +1.2) | r 1.2, h 0.8 | the back rosette, higher | sits partly on M1 |
| Cap rosette M3 | (+1.3, +0.1) | r 1.15, h 0.75 | f34 right rosette | |
| Cap rosette M4 | (−1.8, +0.5), draped onto B's shoulder (z about 5.2–5.8) | r 1.0, h 0.6 | f34 cap's left lobes down to h .66; rear droop to the model's left | conformed down the slope |
| Cap rosette M5 (optional) | (0.0, +0.2) | r 0.9, h 0.7, on top of M1–M3 | the highest point, f .55 in the f34 | sets the cap peak at 7.8 |

- **Cap centre:** X 0 ± 0.35 (f34 +0.03 W, front +0.01 W, rear −0.05 W), Y +0.2 ± 0.4 (side +0.02 D).
- **Expected:** rock X −4.6 … +4.4, Y −4.15 … +4.15, crown 6.4; cap peak 7.8; with the dressing (§2.3) X −5.95 …
  +5.95, Y −5.3 … +5.6 → **12.0 × 11.1 × 7.8**.
  - **f34_sheet (0, 10):** W : H 1.42–1.53 (sheet 1.473); rock W : H 1.25–1.37 (sheet 1.31).
  - **front_sheet (0, 6):** W : H 1.31–1.42 (sheet 1.363); rock 1.20–1.31 (sheet 1.252).
  - **side (90, 5):** W : H 1.20–1.31 (sheet 1.250); rock 1.13–1.24 (sheet 1.181).

### 2.2 Rock-shape targets (measured on the sheet; check with `M.audit`, own bmesh code and `facets.py` on the renders)

These are binding (the M023 lobes failed first as "soccer-ball" facets, then passed as convex hulls with big
irregular triangles):

| Target | Value | Sheet evidence |
| --- | --- | --- |
| Main rock tris (after the union, before any refine) | 110–200 | 22–28 visible facet regions per view, about 45–60 facets in all |
| Distinct flat facets visible per elevation render (`facets.py`, threshold 7, regions ≥ 0.4 % of the rock's area) | 18–30 | f34 28, front 25, rear 17, side 18, r34 17, exploded 22 |
| Largest facet, as a share of the rock's projected area in the front render | 7–14 % | f34 8.2 %, front 8.9 %, r34 10.7 % |
| Largest facet, true area | 4–7 sq studs (≥ 4× the median facet) | front 8.9 % of about 46 sq studs |
| Facet size spread | triangle area CV ≥ 0.6; edge length CV ≥ 0.35 | big shoulder triangles next to long slivers |
| Vertex valence | 3–8, mean 5–6.5, no single valence on more than 45 % of the verts | fans of 5–7; an icosphere is all 5s and 6s |
| No regular pattern | no ring of 5–6 near-equal triangles round a vertex repeated over the surface; no pentagon/hexagon faces | — |
| Base flatness | flat bottom face spans 0.65–0.80 of the max width in X and Y; floor-face area 0.45–0.65 of the max horizontal section | flat contact line across f .4–.9 in the front/rear/side cells; exploded and part list tuck in to 0.70–0.78 at h .1 |
| Widest section | at h .45–.55; width at h .7 ≥ 0.87, at h .8 ≥ 0.78, at h .1 0.70–0.80 of max | `mainrock.py` rows |
| Crown | 2–3 faces with normal z > 0.9, together ≥ 3.0 across; A's crown z 6.2–6.6 | top view's big crown face (0.45 of the rock) |
| Silhouette corners | 11–15 from the front and side | front/expl outlines |
| Cleft | groove depth 0.6–1.0 (0.07–0.11 W) at mid height, measured from the rock's convex hull to the seam; ≥ 0.3 at z 0.5; opening 70–110°; runs from z 0 to about 0.7 of A's height | f34 / front / rear / junction close-up |

Small rocks: 12–18 facets each (14 regions visible in the close-up), largest facet 18–25 % of the rock's projected
area, h/w 0.62–0.72, flat bottoms.

### 2.3 Small rocks and foliage (instances)

| Piece | Centre (x, y), base z | Variant / size | Sheet evidence | Seat |
| --- | --- | --- | --- | --- |
| R1 left foot | (−4.6, −2.2), −0.08 | A 1.8 | f34 f .04–.19; front f .02–.17; top bottom-left | against B's foot, in front of F3 |
| R2 front-right | (+3.4, −3.6), −0.08 | A 1.7 (rot 40°) | f34 f .75–.88; front f .75–.90; side left (front); top bottom-centre | on the ground, 0.3 off A's foot |
| R3 right | (+5.0, −2.4), −0.06 | C 1.2 | f34 f .87–.98, h .18–.34; front f .89–.98; top right-lower | in front of F6 |
| R4 back-right | (+3.6, +3.6), −0.08 | B 1.5, moss on top | top top-right; side right; rear sliver at the left | beside F5b |
| R5 back-left | (−3.4, +3.8), −0.08 | B 1.5 (rot 110°), moss smear | top top-left; rear right f .76–.94; r34 right (the largest there) | |
| P1 pebble | (−3.3, −3.6), −0.04 | 0.5 | f34 f .18, h .12 (pinkish) | |
| F1 front-left, flower | (−1.8, −4.3), 0 | low + flower, w 1.9, h 1.3 | f34 f .28–.43 with the flower at f .34; front f .33 | the front's left cluster |
| F2 cleft foot | (−3.4, −3.0), 0 | low, w 1.6, h 1.4 | f34 f .15–.28 | leaves reach into the cleft |
| F3 far-left, flower | (−5.0, −0.6), 0 | tall + flower, w 1.9, h 2.4 | f34 f .00–.15, h .20–.49, flower at f .09, h .32; front f .10 | behind R1, leaning on B |
| F4 left-back | (−4.2, +2.6), 0 | tall, w 1.7, h 2.2 | rear right f .86–.99; r34 right | |
| F5a back, flower | (+1.8, +4.6), 0 | tall + flower, w 2.2, h 2.8 | rear left mound, flower at f .31 | |
| F5b back-right | (+4.2, +2.8), 0 | tall, w 1.8, h 3.0 | rear left f .01–.43, h to .48; r34 left tall | |
| F6 right column | (+5.0, +0.3), 0 | tall, w 1.7, h 3.2 | f34 f .83–.98, h .13–.54; front f .74–.99, h to .49 | stacked up A's right flank |
| F7 front-right sprigs | (+2.6, −3.7), 0 | small, w 1.0, h 0.8 | f34 f .73–.82, h .08–.22 | between R2 and A |
| F8 back-left | (−1.6, +4.6), 0 | low, w 1.6, h 1.4 | top view's back-centre ring | |

- **The front stays open** between F1 and F7 (x −0.8 … +2.0): bare rock meets the ground there in every front view.
- **Seats.** Small rocks: base 0.04–0.08 below z 0, then the floor cut gives each a flat bottom; none touch the main
  rock by more than a graze ("Slight gaps OK"). Foliage roots at z 0 to 0.05; leaves may touch the rock but never cut
  more than 0.05 into it; tall clusters lean 10–20° toward the rock.
- **From f34_sheet:** R1, R2, R3, P1 visible; F1, F2, F3, F6, F7 visible, 2 flowers. **From the rear:** R5 clear, R4 a
  sliver; F5a/F5b big at the left with 1 flower, F4 at the right.

## 3. View conflicts and resolutions

### 3.1 The "front three-quarter" is an elevated front view; the front cell is the same drawing

- **Evidence.** The cleft sits at the same X in both (f34 −0.22 … −0.34 W, front −0.26 … −0.37 W); the rocks at the
  same fractions within 0.04; the cap centre at X 0 ± 0.04 W in both; top profiles within mean 0.040.
- **Elevation is uncertain:** the main rock's bottom outline gives 5–9° in the f34 and about 6° in the front cell;
  the f34's small-rock feet suggest 12–14°.
- **Resolution.** Compare the f34 cell with an extra **`f34_sheet (0, 10)`** and the front cell with
  **`front_sheet (0, 6)`**. In stage 1, render f34_sheet at e 6, 10 and 14 once, keep the one with the smallest
  top-profile error and record it. The kit `front34 (−28, 12)` and `front (0, 4)` are self-consistency only.

### 3.2 The rear three-quarter is a true back-right view, not the f34 mirrored

- **Evidence.** Its silhouette alone is ambiguous (the flipped f34 fits slightly better: mean 0.042 against 0.058).
  But it shows no white flower (the f34 shows two on the left), its single right-hand rock is the largest
  (R5), and it shows the crease at f .71–.82, the cap drooping right and two rocks at the left: all as a camera at the
  back-right sees the layout of §2.
- **Resolution.** Compare it with the kit **`rear34 (152, 12)`** and an extra **`r34_sheet (150, 9)`**: shares ±4,
  profile ±0.08, 3 small rocks, no flower visible, crease at f .70–.85. The f34_sheet render flipped is a secondary
  silhouette check only.

### 3.3 The rear is a true rear view

- A camera at +Y (az 180) puts the model's left at screen right: the crease (B's seam) and the cap's droop both land
  at the right, R5 at the right foot, F5a/F5b as the big mound at the left. Compare with **`rear_sheet (180, 6)`**:
  shares ±5, 1–2 rocks, 1 flower, the crease at f .73–.84.

### 3.4 The side is from +X (the kit side)

- Two rocks at the screen left (R2 and R3, at the front) and one at the right (R4, at the back) match the top view's
  rock ring only with the camera at +X, screen right = back. The cleft is then on the far side, and the cell shows
  none. Compare directly with the kit **`side (90, 4)`** or an extra `side_sheet (90, 5)`: W : H ±0.06, rock D/W 0.92.

### 3.5 Top view: no cap on the crown; foliage drawn as a ring

- **Evidence.** Every elevation view and the exploded view put the cap on the crown (10–11 % of the silhouette); the
  top view draws a bare crown face and a heavy ring of foliage round the left, back and right (green 32 % of its
  silhouette against 25–29 % elsewhere). It also draws the rock larger against its rim rocks (perspective from above).
- **Resolution.** The hero governs: the cap is built. Judge the top by the rock outline (11–13 sides, one big crown
  face), the foliage covering the left, back and right and leaving the front open, and 5–6 rim rocks. Record "the top
  view draws no cap" as a known miss; the cap's share in our top render will be 8–12 % instead of 0.

### 3.6 The exploded main rock has no cleft

- **Evidence.** The exploded and part-list main rock is one rounded mass with a moss stain on its lower left; the f34,
  front, rear, r34 and the junction close-up all show the cleft and the second mass.
- **Resolution.** The hero governs: A ∪ B with a real cleft. The `MossyBoulderMainRock` part is the same mesh (one
  builder); the cleft is a known miss against the exploded cell. Keep the exploded's broad crown, barrel sides and the
  painted moss stain low on the left.

### 3.7 Counts: "3 × Small Rocks" and "4 × Foliage Clusters"

- The hero and top show 5 rocks plus a pebble, the exploded 5; 7–9 foliage clusters across the views, 6 in the
  exploded. **Resolution:** 3 rock variants placed 5 times plus a pebble; 4 cluster variants placed 9 times (§2.3), so
  each view's counts land within ±1.

### 3.8 Palette names against the renders

- "Rock Shadow" `#B99C8C` is the warmest and most saturated swatch, close to the rendered rock median (`#BFA194`);
  "Rock Mid" `#8C8182` is the cool lavender grey of the shaded faces; "Rock Light" `#C3B2AC` is a pale, less saturated
  warm grey. The warm-lit / cool-shade split on the renders is lighting (§5.3). Use the swatches as starting colours
  only; calibrate on the renders.

### 3.9 "Solid colors, no texture noise" against the user's blended-colour rule

- The user's rule wins, but keep it quiet: broad cool and light patches on the rock (whole facets), height bands on
  the cap and leaf tiers, low Tint. No per-triangle confetti.

### 3.10 Ground shadow

- A soft neutral grey (`#B1B1B1`) to the left of every view. It is lighting, not geometry: background in every
  measurement, and not modelled.

## 4. Construction plan (stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `main_rock_part()` → `MossyBoulderMainRock`: A ∪ B with the cleft (no cap, no dressing). Compare with the
     exploded main rock from about (−20, 20) and with §2.2: barrel sides, broad crown, big irregular triangles, the
     flat bottom.
   - `moss_cap_part()` → `MossyBoulderMossCap`: the 4–5 rosettes on a flat base (as built, before conforming). Compare
     with the exploded cap and the Moss Cap Underside close-up (render from below, about (0, −35)): flat brown
     underside, thin lime rim, scalloped lobes.
   - `small_rock_part()` → `MossyBoulderSmallRock`: variant A. Compare with the Small Rock Detail close-up.
   - `foliage_part()` → `MossyBoulderFoliage`: the low + flower variant. Compare with the part-list cluster.
   - Render a parts shot (`extra`, about (−20, 20)) laid out like the exploded.
2. **Hero:**
   1. Build A and B; one exact union (A first, then B; save before and after).
   2. Paint the rock (stage 4 needs the face lists; keep the original facets' ids before any refine).
   3. Build the cap rosettes, conform them to the rock (sink 0.05), and union them into the rock body one at a time
      (decision §8.6); or keep them as closed shells resting on it.
   4. Place the small rocks and the pebble (§2.3), floor-cut at z 0.
   5. Place the 9 foliage clusters and 3 flowers.
   6. `M.fix_bowties`, origin at the bbox bottom centre, transforms applied.
3. **Budget** (§4.3): hero about 2700–3200 (limit 4000); each part under 500 (limit 1000). If over, drop leaves from
   the tall clusters' hidden back sides first; never thin the main rock below 110 tris or the rosettes below 8 lobes.
4. **Placeholder keys** (stage 1): `m035_rock`, `m035_moss`, `m035_leaf`, `m035_petal`, `m035_pollen`. Stage 4 adds the
   rest (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** a squat faceted boulder with a leafy lime cap, a clear cleft on the front-left, foliage round
      the left, back and right, small rocks at the foot, the front of the foot open.
   2. **f34_sheet against the f34 cell:** W : H 1.42–1.53; shares within ±4 of 73.7 / 25.8 (cap 10.9 ± 2, foliage 14.9
      ± 3); top profile within ±0.07 (mean ≤ 0.04); cap at f .35–.71 ± 0.05, its lowest lobe at h .66 ± 0.06; cleft
      at f .34 → .25 ± 0.05; R1, R2, R3 at §1.2 ± 0.06; 2 flowers.
   3. **front_sheet against the front cell:** W : H 1.31–1.42, shares ±4, profile ±0.08.
   4. **Kit rear34 / r34_sheet against the r34 cell, rear_sheet against the rear cell, kit side against the side
      cell:** shares ±5, profiles ±0.1, the crease and the cap droop on the correct side (§3.2–§3.4), rock counts ±1.
   5. **Top (0, 89):** rock outline 11–13 sides with one big crown face; foliage on the left, back and right only;
      5–6 rim rocks; W : D 1.02–1.14 (sheet 1.084); the cap is the known miss.
   6. **Rock-shape targets** (§2.2), all of them, on the hero's main rock and on the MainRock part.
   7. **Parts against their cells** (§4.1); a **junction extra** `junc_cu (−35, 12)` framed on F2 and R1 against the
      Rock / Foliage Junction close-up; an **under-cap extra** of the MossCap part from below.
   8. **Hero size** 12.0 × 11.1 × 7.8 (±0.5 / ±0.6 / ±0.3); rock 9.0 × 8.3 × 6.4 (±0.3 / ±0.3 / ±0.2).
   9. **Scale shot:** the hero beside a 5.5-stud character marker (the kit-relative-scale rule).
6. **Stage 2:**
   - every shell closed and manifold: zero non-manifold edges and verts (`nonmanifold_verts` 0), boundary, wire and
     loose elements; no zero-area faces or n-gons; normals outward;
   - no faces under 5° where B meets A and where the cap meets the rock (m011 `_tidy` / `_desliver`);
   - no decimation of the main rock below 110 tris, rosettes below 8 lobes, small rocks below 12 facets.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density (leaves and petals included).

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Main rock A ∪ B (+ one refine where the stain is painted) | 1 | 150–450 | 150–450 |
| Cap rosettes | 4–5 | 60–90 | 300–450 |
| Small rocks A/B/C + pebble | 5 + 1 | 30–36 / 16 | 180 |
| Foliage low (10 leaves) | 3 (F1, F2, F8) | 120 | 360 |
| Foliage tall (16–18 leaves) | 5 (F3, F4, F5a, F5b, F6) | 200–216 | 1000–1080 |
| Foliage small (6 leaves) | 1 (F7) | 72 | 72 |
| Flowers (5 petals + centre) | 3 | 84 | 252 |
| **Hero** | | | **about 2300–2850; 2700–3200 after unions and cleanup** (limit 4000) |
| Parts: MainRock / MossCap / SmallRock / Foliage | | | about 150–450 / 300–450 / 34 / 204 (limit 1000) |

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 26 × 24 box inside each)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Rock Light | (32,178,58,202) | `#C3B2AC` | 16°, 0.12, 0.76 |
| Rock Mid | (32,220,58,244) | `#8C8182` | 355°, 0.08, 0.55 |
| Rock Shadow | (32,262,58,286) | `#B99C8C` | 21°, 0.24, 0.73 |
| Moss Green | (32,304,58,328) | `#94A822` | 69°, 0.80, 0.66 |
| Foliage Light | (32,346,58,370) | `#D6CF28` | 58°, 0.81, 0.84 |

There is no swatch for the cap's brown underside, the flower petals or the flower centres; they are sampled from
the renders below.

### 5.2 Rendered regions (`samp.py`; median / lit quartile / shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Rock, f34 / front / top | main-rock boxes | R | `#BFA194` / `#C0A394` / `#C4A89A` | `#E0C4B3` / `#E6C8B4` / `#E5C7B2` | `#7C6F6F` / `#786F70` / `#726A6A` |
| Rock, r34 / side / rear | main-rock boxes | R | `#AE988D` / `#B29A90` / `#B0988E` | `#ECCFB6` / `#E2C4AF` / `#E8CBB3` | `#6E6A72` / `#726E78` / `#776F73` |
| Rock, exploded main / part list (no cast shadow on them) | (272,823,569,1088) / (808,827,898,919) | R | `#BBA195` / `#AB948C` | `#DDBFA9` / `#DABCAC` | `#716C71` / `#706C71` |
| Rock thirds, exploded main (top / mid / bottom) | same | R | `#C9AEA0` / `#BEA497` / `#98837A` | `#E8CBB7` / `#CCB0A1` / `#C8AC9C` | `#767078` / `#6F6D76` / `#706867` |
| Rock thirds, front (top / mid / bottom) | (51,515,234,661) | R | `#D9BBA7` / `#CBAD99` / `#95837D` | `#EACDB9` / `#EBCEB6` / `#D5B49E` | `#89818B` / `#6F6B74` / `#7C6E62` |
| Small rocks: exploded L / exploded front / f34 R2 / f34 R3 / f34 R1 (in the cleft's shade) | samp boxes | R | `#BDA295` / `#BAA194` / `#C2A594` / `#CCAF9C` / `#877C7E` | `#DDBEAB` / `#DCC2B2` / `#E5C7B4` / `#E9CEBA` / `#C9B0A5` | `#746D70` / `#716D74` / `#817371` / `#7E6F6D` / `#615A58` |
| Small Rock Detail close-up | (528,1178,732,1384) | R | `#AA9792` | `#DABCAE` | `#666265` |
| Moss stain, exploded main rock | (290,960,330,1040) | G | `#647430` (74°, 0.59, 0.45) | `#697933` | `#5A652A` |
| Moss in the cleft, f34 / front | (228,300,275,360) / (60,600,100,640) | G | `#4B6402` / `#5C7A03` | | |
| Cap, f34 / front / rear / side / r34 | above 0.55 H | G | `#A1B809` / `#96B10C` / `#A2B808` / `#9DB30C` / `#A2B607` | `#D5D50B` / `#D1D70D` / `#D0D50C` / `#CBD20E` / `#CED309` | `#5E7E0C` / `#56780E` / `#627E0D` / `#557712` / `#627D0A` |
| Cap, exploded / part list / underside close-up rim (unshadowed) | (330,725,560,830) / (805,755,900,800) / (30,1185,255,1260) | G | `#98B11B` / `#93AD13` / `#9BAF1A` | `#C0CD1B` / `#C1CC10` / `#C0CF1E` | `#5D8016` / `#618016` / `#597A0C` |
| Cap underside (flat, evenly lit) | (60,1250,240,1335) | brown | `#725E45` (33°, 0.39, 0.45) | `#78634A` | `#6E5B41` |
| Foliage, f34 / front / rear / side / r34 | below 0.55 H | G | `#608904` / `#729405` / `#6E9004` / `#6C8F05` / `#668D04` | `#BFCB03` / `#C2CA04` / `#C0CB03` / `#C2CC04` / `#B6C903` | `#2F5104` / `#335005` / `#335304` / `#335106` / `#315204` |
| Foliage, exploded R-bottom / exploded L-top / part list / junction close-up | samp boxes | G | `#72A907` / `#629D14` / `#78AD07` / `#88B103` | `#AFCD06` / `#92C316` / `#BFD308` / `#BECD05` | `#3C7004` / `#3A720F` / `#3F7306` / `#3F6B02` |
| Top view green ring | V top | G | `#839C05` | `#C8CE04` | `#3E5807` |
| Petals, f34 / junction / part list | V / X | white | `#FDFDFA` | `#FFFFFD` | `#F5F5EE` |
| Flower centre, f34 / junction / part list | V / X | yellow | `#E0C411` / `#F0C709` / `#ECCB08` | `#EED823` / `#FAD30D` / `#FAD70B` | `#C6AC0A` / `#E2B20A` / `#D0AD13` |
| Ground shadow, f34 / exploded | V / X | B | `#B1B1B1` / `#B7B7B7` | | |

Deciles (dark → light), f34:

```
rock     #686261 #847675 #917E77 #97857F #AF9B92 #C5A795 #CFB19E #D9B9A4 #DDC1B0 #EFD4BC
cap      #47600A #66840B #7A9C0F #8CA80A #9BB30A #ACBC06 #BFC705 #CACE06 #D2D408 #DFDB16
foliage  #1E3C03 #355503 #3F6605 #4E7205 #578204 #659205 #86A804 #A2BC02 #B9C803 #D2D506
```

### 5.3 How the colour works

**Rock.**
- One warm grey-pink stone: medians hue 15–24°, sat 0.18–0.25. The lit faces are peach (`#E0C4B3`–`#ECCFB6`, hue
  23–28°), the shaded faces cool lavender (hue 250–340°, sat 0.04–0.10). That split is the warm sun and the cool sky
  fill: **light, not paint**. Never colour by facing.
- **Painted signal (gentle): broad cool and light patches.** Within the lit faces, tone still varies facet to facet
  (lit deciles `#D9B9A4` → `#EFD4BC`), and the top view's lit crown shows faint lavender facets. Give broad noise-field
  patches (whole facets): `rock_cool` (from Rock Mid) at about 30 % coverage, mixed 30–35 %; `rock_light` (from Rock
  Light) on the upper half at about 25 % coverage, mixed 25 %.
- **No dark foot band in paint.** The bottom thirds are darker (`#95837D`, `#98837A`), but their lit quartiles stay
  within 15–35 levels of the mid third, and the part list's bottom is the down-facing faces in shade. At most a 15 %
  `rock_cool` mix below 0.12 H where the foliage presses in (Roblox has no AO).
- **Moss stain:** an olive moss (`#647430` on the exploded rock; `#4B6402`–`#5C7A03` in the hero's cleft, in shade)
  on the faces in the cleft's foot (z < 0.4 of A's height) and two lobed patches low on B's front-left faces. A
  genuinely different material: blend with `steps=2` over refined faces, so the edge reads lobed, not a hard polygon.
- **Small rocks:** the same stone (`#BDA295`, `#BAA194`, `#C2A594`, `#CCAF9C`), per-rock tint ±0.06. R4 and R5 (and
  one front rock) carry a moss patch on their top 25–35 % (top view, r34).

**Cap.**
- Lime-yellow moss: medians hue 67–70°, sat 0.85–0.96; lit tops near Foliage Light (`#D5D50B`, `#D6CF28`), deep green
  in the notches and the rim (`#5E7E0C`). Per rosette: **deep at the rim and notches → moss → sun-yellow on the top
  third**, by height within the rosette (a position field). The flat underside is brown (`#725E45`): a hard material
  edge at the rim's bottom.

**Foliage.**
- A greener, darker family than the cap: medians hue 74–86°, sat 0.87–0.97, value 0.54–0.69 (cap 0.69–0.72).
- **Tiered:** low outer leaves deeper (`#3F7306` mixed 40 %), middle leaves `leaf`, inner upright leaves `leaf_young`
  (`#BFD308`, close to Foliage Light). Stepped by tier like `K.clover(young_mat=…)`, not by facing.
- **Flowers:** pure white petals (`#FDFDFA`; shade quartile `#F5F5EE`), a deep yellow domed centre (`#E0C411` –
  `#F0C709`).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

The calibration targets are medians of **unshadowed** rendered regions (the exploded parts, the part list and the
close-ups), not swatches. `K.sample` kinds: `"stone"` for the rock keys (sat 0.20 < 0.25), `"green"` for the moss and
leaf keys, `"brown"` for the cap underside, `"vivid"` for the pollen.

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m035_rock` | `#BCA195` (exploded small rocks `#BDA295` / `#BAA194`, exploded main `#BBA195`; start from swatch Rock Shadow `#B99C8C`) | main rock and small rocks, the default | rough 0.9 |
| `m035_rock_cool` | `#8C8182` (swatch Rock Mid; the shade faces' decile `#847675`) | broad noise patches at 30–35 % | rough 0.9 |
| `m035_rock_light` | `#C9AEA0` (exploded top-third median; swatch Rock Light `#C3B2AC`) | broad patches on the upper half at 25 % | rough 0.9 |
| `m035_moss_stain` | `#647430` (exploded stain) | the cleft's foot, B's low front-left faces, small-rock tops | rough 0.95, low spec |
| `m035_moss` | `#98B11B` (exploded cap; part list `#93AD13`; swatch Moss Green `#94A822`) | the cap, default | rough 0.9, low spec |
| `m035_moss_sun` | `#CED309` (cap lit quartiles `#CED309`–`#D5D50B`; swatch Foliage Light `#D6CF28`) | the rosettes' top third | rough 0.9, low spec |
| `m035_moss_deep` | `#5D8016` (exploded cap shade quartile; hero `#5E7E0C`) | rim band and notches | rough 0.9, low spec |
| `m035_moss_under` | `#725E45` (underside close-up) | the cap's flat underside (hard edge) | rough 0.95 |
| `m035_leaf` | `#72A907` (exploded cluster; part list `#78AD07`) | foliage, default | rough 0.85, low spec |
| `m035_leaf_young` | `#BFD308` (part-list lit quartile; hero lit `#BFCB03`) | inner upright leaves | rough 0.85, low spec |
| `m035_leaf_deep` | `#3F7306` (part-list shade quartile) | outer low leaves at 40 % | rough 0.85, low spec |
| `m035_petal` | `#F5F5EE` (petal shade quartile; median `#FDFDFA`) | petals | rough 0.7 |
| `m035_pollen` | `#E0C411` (f34 median; junction `#F0C709`) | flower centres | rough 0.7 |

**Calibration warnings:**
- **Rock:** calibrate `m035_rock` on the parts shot of the small rock against `#BCA195`, then check the f34_sheet rock
  median within 10 of `#BFA194`, hue 15–25°, sat 0.17–0.26. The rock must stay warm: a drift to the swatch's grey
  (Rock Light sat 0.12) reads wrong. Shade faces in our studio will read neutral, not lavender; don't push them by
  facing.
- **Two greens apart:** cap hue 64–72°, sat ≥ 0.85, value median ≥ 0.66; foliage hue 74–88°, sat ≥ 0.85, value median
  ≤ 0.66. The hue gap must stay ≥ 6°. W01's moss was flagged twice by the user for colour; measure, never eyeball.
- **Petals** clip easily: calibrate on the parts shot so the petal lit quartile is ≤ `#FFFFFD` and the median ≥
  `#F0F0EA`; no blue specular.
- **Lit quartiles** of our studio run 16–22 levels below the sheet's (023's verifiers): that is light, not paint.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Rock** (on A and B's original facets, before any refine): `rock` base; `K.noise_field(scale≈0.18)` patches →
  `rock_cool` at 30–35 %; upper-half patches → `rock_light` at 25 %; then refine only the cleft's lower faces and B's
  front-left lower faces and blend `moss_stain` there with steps 2 (field: distance to the cleft seam line, and z).
- **Cap:** per rosette, field t = (z − base) / h: t < 0.2 → `moss_deep`; 0.2–0.65 → `moss`; > 0.65 → `moss_sun`;
  steps 2–3. Underside faces `moss_under` (mode hard).
- **Foliage:** by tier (outer / middle / inner) `leaf_deep` 40 % → `leaf` → `leaf_young`; each cluster its own
  `tint_var` 0.04.
- **Small rocks:** `rock` with per-rock `tint_var` 0.06; `moss_stain` on the top 25–35 % of R4, R5 and R2 by z plus
  noise, steps 2.
- **Hard edges only** where materials meet: rock | moss stain edge (steps 2 is fine), cap underside | rim, petal |
  pollen.

### 5.6 Texture (Tint) and finish

- **Tint:** rock amp 0.04, scale 0.3, per original facet (so a refined facet keeps one tone, as W01's `rock()` does);
  cap amp 0.05, scale 0.8; leaves 0.04; petals none. Never per-triangle confetti ("No texture noise").
- **Finish:** rock rough 0.9, metal 0; moss and leaves `low_spec=True` (`K.FOLIAGE_SPEC` 0.06), rough 0.85–0.9; petals
  and pollen rough 0.7. No emission anywhere.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Rock:** f34_sheet median within 10 of `#BFA194`; parts-shot small rock within 8 of `#BCA195`; hue 15–25°, sat
  0.17–0.26.
- **Cap:** f34_sheet cap median within 12 of `#A1B809`; parts-shot cap within 10 of `#98B11B`; hue 64–72°, sat ≥ 0.85.
- **Foliage:** f34_sheet foliage median within 12 of `#608904`; parts-shot cluster within 10 of `#72A907`; hue
  74–88°, sat ≥ 0.85.
- **Cap underside** (under-cap extra) within 10 of `#725E45`. **Petals** median ≥ `#F0F0EA`; **pollen** hue 46–56°,
  sat ≥ 0.8.
- **Shares** per §4 step 5.2.

## 6. Joins and contact

- **A and B:** one exact union; B's lean and its 0.8–1.2 setback make the cleft a real V; no slivers under 5° along
  the seam (m011 `_tidy` / `_desliver`). Feed the boolean clean convex hulls with no coplanar faces (jitter B's base
  z by 0.02 before the floor cut).
- **Cap on the rock:** conformed, sunk 0.03–0.08; either united (one stone shell) or a closed shell resting on the
  crown with no gap visible from any view (decision §8.6). Its left rosette (M4) follows B's lower shoulder.
- **Small rocks:** 0.04–0.08 below z 0, floor-cut flat; within 0.0–0.3 of the rock foot or a cluster ("Slight gaps
  OK"); none floating, none standing on a point.
- **Foliage:** roots on the ground (z 0–0.05); leaves press against the rock but cut no more than 0.05 into it; F2's
  leaves reach into the cleft's mouth; tall clusters lean on the flanks.
- **Ground:** the floor cut at z 0 (`m004.floor_cut`) for the rock body and the small rocks gives flat undersides.

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** an ordinary sunlit mossy boulder. No glow, light, sparkle, dust, fireflies, pollen or
particles in any cell. The flowers are plain white and yellow paint, not emissive. WorldModeling §1.2 forbids
"an ordinary asset recolored neon with a glow halo".

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight:** nothing on the sheet glows.
- **Studio note (Requires Manual Validation):** check in Studio that the rock stays warm grey-pink (not grey or
  orange) under the game's sun, that the cap's lime and the foliage's green stay two distinct greens, and that the
  petals don't bloom to flat white.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust` (checked in the file; the
  entries after `dust` are particle textures, not kinds).
- **Recommended: none.** The sheet shows no effect, and W01's Boulder (the same subject) shipped with none. Record
  "Stage 6 skipped: sheet shows no VFX".
- **Not recommended:** `dust` or pollen motes (nothing floats on the sheet), `ore_glint` (plain stone), any light, or
  harvest sockets (a boulder is not a resource node here).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by searching the repo text and every sheet / wip `.blend` (zstd-decompressed) with
`blendall.py` / `names.py`:
- **W01** (in `FlintbornWorldKit.blend`, `W01.blend`, every wip copy): `Boulder`, `BoulderMainRock`, `BoulderMossCap`,
  `BoulderFlat`, `BoulderUpright`, `BoulderSplit`; keys `w01_rock`, `w01_moss`, `w01_leaf`, `w01_petal`, `w01_pollen`
  and the rest.
- **Sheet 06** (`06_rocks_runes_camp.blend`, the lobby): `LowBoulder`, `TallBoulder`, `SplitBoulder`, `LongBoulder`.
- **Elsewhere:** `JuniperFoliageCluster`, `LogAndStumpMossFoliage`, `SaplingLowerFoliage`, `SaplingTopFoliage`;
  `CopperNodeBaseRockSmall`, `FlintNodeBaseRockSmall`, `GoldRockSmall`; `StoneMainRock`, `StoneNodeMainRock`;
  `MeadowDaisy*` (W07), `Clover*` (V01), `Pebble*` (W01).
- `M.mk` would silently rename a clash to `<name>M035`, so avoid all of these.

**Proposed names.** None of `MossyBoulder`, `m035_` occurs in the repo, the decompressed kit `.blend` or any sheet /
wip `.blend`. "Mossy boulder" keeps the sheet's "Boulder" and its subtitle ("with moss").

| Object | Part | Why |
| --- | --- | --- |
| `MossyBoulder` | hero | W01 owns `Boulder` |
| `MossyBoulderMainRock` | Main Rock (A ∪ B with the cleft and the moss stain) | W01 owns `BoulderMainRock` |
| `MossyBoulderMossCap` | Moss Cap (4–5 rosettes, flat brown underside) | W01 owns `BoulderMossCap` |
| `MossyBoulderSmallRock` | Small Rock (variant A, 1.8) | `*RockSmall` belong to R01/R03 nodes |
| `MossyBoulderFoliage` | Foliage Cluster (low + flower) | `*FoliageCluster` belongs to the juniper |

- Palette keys `m035_*` (§5.4). Collection `Kit/M035 Boulder`.
- Collision tags: hero and MainRock `"hull"`; MossCap and Foliage `"none"`; SmallRock `"hull"`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **rock 9.0 × 8.3 × 6.4, dressed 12.0 × 11.1 × 7.8** (recommended: a mid-size boulder a little
   taller than the character, between sheet 06's boulders and W01's), or W01's class (rock 11.6 wide, dressed about
   15.5 × 14.3 × 10.1 at this sheet's proportions), or a chest-high 7.0-wide rock (dressed 9.3 × 8.6 × 6.1).
2. **Rock form** (§3.6): **two masses A ∪ B with a real cleft on the front-left** (recommended: the hero, front, rear,
   r34 and junction close-up all show it), or the exploded's single rounded mass (simpler; loses a defining feature of
   the hero).
3. **Cap** (§3.5): **4–5 lobed rosette mounds on the crown, the left one draping onto B** (recommended: every
   elevation and the exploded show it), not the top view's bare crown.
4. **Counts** (§3.7): **3 rock variants × 5 + a pebble; 4 cluster variants × 9; 3 flowers** (recommended: every view's
   counts within ±1), or the part list's literal 3 rocks and 4 clusters (the rear and top would then lack theirs).
5. **Elevations** (§3.1): **start f34_sheet at e 10 and probe 6 / 10 / 14 once; front and rear at 6; side at 5**.
6. **Hero packaging:** **one hero object holding closed shells: the stone body (A ∪ B with the cap united on it), each
   small rock, and each leaf, petal and flower centre as its own closed solid** (recommended: the sheet says "Moss cap,
   small rocks and foliage are separate meshes" and "Slight gaps OK"; uniting about 140 thin leaves by exact booleans
   is slow, crash-prone and welds the leaf necks; this follows M032's vegetation-shell exception). Every shell closed
   and manifold, 0 bowties, no shell cutting another by more than 0.05. Or **one closed shell** (the M029 precedent,
   which united 21 leaves; here about 7× as many unions).
7. **Exports:** **the hero plus 4 parts** (`MossyBoulderMainRock`, `…MossCap`, `…SmallRock`, `…Foliage`)
   (recommended: the part list's four kinds).
8. **Stage 5/6:** **no emission, light or VFX** (recommended: the sheet shows none; W01's Boulder shipped none).
9. **Comparison cameras** (recommended, §3): `f34_sheet (0, 10)` for the hero, `front_sheet (0, 6)` for the front
   cell, the kit `rear34 (152, 12)` plus `r34_sheet (150, 9)` for the r34, `rear_sheet (180, 6)` for the rear, the
   kit `side (90, 4)` for the side, the kit top for the top; kit front34, front, underside as self-consistency only;
   extras `junc_cu (−35, 12)`, an under-cap shot of the MossCap part from below, a parts shot (−20, 20) and a scale
   shot with a 5.5-stud marker. Hide the floor in every `*_sheet` render (the sheet's ground shadow is background).
10. **Colour:** **one warm stone with broad cool and light patches, an olive moss stain in the cleft, a three-band
    lime cap, three-tier foliage** (recommended); no dark painted foot band.
11. **Names** as proposed.

## 9. Pitfalls to avoid

1. **An icosphere or soccer ball.** The exploded rock looks geodesic at a glance, but its triangles differ a lot in
   size and its fans have 5–7 edges. Build convex hulls of jittered, thinned point rings (not `primitive_ico_sphere`,
   not a plane dual on Fibonacci normals) and meet every §2.2 number: facet counts, largest facet 7–14 % of the front
   area, area CV ≥ 0.6, valence spread.
2. **A melted or round rock.** Keep the barrel: steep sides widest at half height, a broad near-level crown, a flat
   base 0.65–0.80 wide. W01 lost a round to "melted rock" and soft facets: flat shading, no smoothing, no bevels.
3. **A painted or soft cleft.** The cleft is geometry: the A ∪ B seam with 0.6–1.0 depth at mid height. A vertex-pushed
   crease (W01's `crease()`) reads soft; a painted dark line reads flat.
4. **A flat moss decal.** The cap is 4–5 lobed rosette mounds with raised centres, notched lobes, a rim band and a
   flat brown underside, stacked 1.2–1.5 above the crown (W01's round-1 failure was "flat moss decal").
5. **Copying the top view.** It draws no cap and a heavier foliage ring (§3.5). The hero governs.
6. **Copying the exploded sizes.** The exploded draws the cap and rocks 1.3–1.5× too big for the main rock (§1.4).
7. **Blade or spiky foliage.** The sheet's leaves are broad ovate cupped solids with a pointed tip, in tiered rosettes
   (W01 lost rounds to "herb blades" and "herb language"). Tall clusters lean on the rock; the front of the foot stays
   open.
8. **Colour by facing.** The peach-lit / lavender-shade split is light. Cool and light patches go by a noise field over
   whole facets, the cap bands and leaf tiers by position; `K.check` facing correlation < 0.5.
9. **One green.** Cap (hue 64–72°, lighter) and foliage (hue 74–88°, darker) are two families; the moss stain is a
   third, olive one.
10. **A grey rock.** The rock is warm (hue 15–25°, sat 0.17–0.26); don't calibrate towards Rock Light's grey.
11. **Floating rocks or leaves.** Small rocks floor-cut flat at the ground; leaves rooted at z 0; nothing hovering
    under the cap.
12. **Exact booleans.** Clean convex inputs, no coplanar faces, A ∪ B first, then the cap rosettes one at a time; save
    between risky steps (STAGES.md crash note).
13. **Budget.** Foliage is most of the count (about 1650 of 2700–3200). Don't spend tris on hidden back leaves; never
    thin the rock or the rosettes to fit.
14. **Name clashes** with W01 `Boulder*`, sheet 06 `*Boulder`, `*FoliageCluster`, `*RockSmall`, `*MainRock` (§8). Only
    one agent drives a Blender session at a time; no commits, pushes or exports in stage agents.

## Decisions (main session, 2026-10-29)

All recommendations are accepted, with packaging (6) stated precisely:
1. Size: rock 9.0 W × 8.3 D × 6.4 H; dressed with moss and foliage, 12.0 × 11.1 × 7.8.
2. Two masses with a real cleft. The exploded view's single mass is a known miss.
3. The moss cap on the crown. The top view's missing cap is a known miss.
4. Counts: 3 rock variants placed 5 times plus a pebble; 4 foliage variants placed 9 times; 3 flowers.
5. Hero camera: start at 10° and try 6°, 10° and 14° once.
6. Packaging, in one hero object:
   - **The main rock with its moss cap fused is one closed shell.**
   - Each small rock and each foliage or flower cluster is its own closed shell. Fusing about 140 thin leaves is not required; the sheet calls them separate meshes.
   - Every shell is manifold, with 0 bowties and 0 self-intersections inside each shell. Shells may touch or interpenetrate slightly but must not share faces.
   - `problems` must report shells that aren't closed.
7. Hero plus the 4 parts.
8. No effects; stages 5 and 6 are recorded as skipped.
9. Comparison cameras:
   - front at 10° for the hero cell and 6° for the front cell;
   - the rear three-quarter against the kit rear34 (152°, 12°) or an extra at (150°, 9°);
   - the kit side camera for the side cell;
   - plus a junction close-up, a cap-from-below shot, a parts shot and a scale shot beside a 5.5-stud character.
10. Colour: one warm stone with broad cool and light patches (never by facing), an olive moss stain in the cleft, a cap in three bands from deep green to yellow, foliage in three tiers, and no dark painted band at the foot.
11. Names: `MossyBoulder*`, keys `m035_*`.

The rock-shape targets in §2.2 (facet counts, largest facet, area and edge spread, valence, base 0.65–0.80, cleft 0.6–1.0 deep) are binding. No soccer-ball or icosphere patterns.

## Stage 1: Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m035.py`, `build()` (background Blender on port 9877, work file `wip/M035.blend`). Every
part has its own function, and the hero is built from the same functions.
- **Main rock (`_rock`, `_mass`).** A and B are convex hulls of jittered point rings (`m033._ring_pts`/`_hull`).
  - A: rings 8/9/9/8/6/4 at h 0/.14/.46/.76/.91/1.0, radius .66/.85/1/.97/.82/.50. Size 7.6 × 9.2 × 6.45, centre
    (0.6, −0.1).
  - B: rings 7/8/8/6/3. Size 4.8 × 6.8 × 5.5, centre (−2.3, 0.2), crown leaning 0.14 toward A.
  - **The cleft is real geometry.** Each mass has one *cut plane* (`_cut`), which presses the points beyond it flat
    onto it.
    - A's plane forms its left flank: normal (−1, −0.12, 0.18), distance 3.0.
    - B's plane forms its front: normal (−0.15, −1, 0.12), distance 2.4.
    - The two walls meet in a V about 105° open at x ≈ −2.2. Without the cuts, two ellipsoid hulls gave a cleft only
      0.03–0.26 deep, because B's front lay flush with A's curve.
  - **Depth taper.** A's depth narrows toward the crown (`y_taper` 0.30), giving the side cell's trapezoid. Before
    the taper, the side profile error was 0.138 mean; after, 0.091.
  - **Union.** The two masses join in one merge-0 exact union at the origin (`m033._union_fine`), then
    `m033._floor_cut` at z 0.
- **Moss cap (`_rosette`, `_cap`, `_conform_rosette`).** Five rosettes, M1/M3/M4 on the rock, M2 on M1+M3, and M5 on
  M1+M2+M3.
  - Each rosette has 7–8 broad lobes, two corners per lobe (0.93–1.04 r) and a shallow notch (0.70–0.80 r).
  - Radial ridges run to a raised centre, with notch valleys, a 0.18 rim band and a flat underside fan.
  - The first version had one tip per lobe and read as a spiky star; it was changed to two corners.
  - **Fold-free conform.** Each rim corner's top and bottom verts drop by the same amount, and no vert drops more than
    1.1 below the seat under the rosette's centre.
    - Plain `K.conform` folded M1's rim over the steep front flank. The exact union of that self-intersecting shell
      returned an empty mesh, so the whole rock vanished; the stone then measured 5.4 × 3.8 × 2.8.
    - The hero now also rejects any stone narrower than 8.5 or lower than 7.0.
  - The rosettes are united into the stone one at a time (decision 6).
- **Small rocks (`_small_rock`).** Hulls with flat bottoms at z 0: rings 6/7/5/3, h = 0.66 w; the pebble uses rings
  5/5/3. Five rocks plus the pebble, kept clear of the stone by a push-out guard.
- **Foliage (`_leaf`, `_cluster`, `_flower`).**
  - **Leaf (`_leaf`).** An own 14-tri closed leaf: an ovate outline with a pointed tip, edges cupped (fold 0.16), a
    raised two-point midrib, one point underneath, and a random roll of up to 0.45 rad. `K.leaf` "ovate" read as
    flat slivers side-on, then as pyramids once thickened.
  - **Low and small clusters.** One mound of 14 (low) or 7 (small) leaves, with pitch rising from outer to inner.
  - **Tall clusters.** Stacks of leaf mounds every 0.55 stud up a stem that leans 12° toward the rock. Leaves
    pointing within 62° of straight into the rock are left out, being hidden.
    - The first versions read as fern or herring-bone columns.
  - **Placement.** Ten clusters: the nine in §2.3, plus F9, a small deep-green tuft in the cleft's foot, which is the
    sheet's cleft moss tuft. All are shifted −0.3 in Y (`DRESS_DY`), so the rock stands centred in its dressing in
    the side cell.
  - **Guard.** Every leaf is pushed out of the stone and the small rocks until it cuts in no more than 0.05, then
    lifted to z ≥ 0.004. On the final build it moved 42 leaves or rocks.
  - **Flowers.** Three flowers, on F1, F3 and F5a: five 14-tri petals, each based 0.03 out along its own direction,
    and a 6-sided pollen dome; the face tips 0.3 rad toward the front.
- **Elevation probe (spec 3.1).** All three runs used the f34 cell profile.

  | Elevation | Profile error, mean / max | W : H (sheet 1.473) |
  | --- | --- | --- |
  | 6° | 0.072 / 0.26 | 1.476 |
  | 10° | 0.060 / 0.23 | 1.426 |
  | 14° | 0.052 / 0.21 | 1.370 |

  Decision 9 fixes the hero camera at 10°, so `f34_sheet` stays at (0, 10). 14° fits the profile best, 6° the W : H.
  The probe renders are `f34_e6_sheet.png` and `f34_e14_sheet.png`.

## Stage 2: Optimisation and cleanup

**Tris.**

| Object | Tris | Limit | Size (studs) | Notes |
| --- | --- | --- | --- | --- |
| Hero `MossyBoulder` | 3770 | 4000 | 12.36 × 11.28 × 7.70 | target 12.0 ± 0.5 / 11.1 ± 0.6 / 7.8 ± 0.3 |
| `MossyBoulderMainRock` | 220 | 1000 | 9.0 × 8.22 × 6.4 | |
| `MossyBoulderMossCap` | 778 | 1000 | 5.47 × 4.69 × 2.73 | |
| `MossyBoulderSmallRock` | 38 | 1000 | 1.66 × 1.64 × 1.19 | |
| `MossyBoulderFoliage` | 286 | 1000 | 1.55 × 1.61 × 1.2 | 20 shells |

Hero tris by shell:

| Shell kind | Shells | Tris |
| --- | --- | --- |
| Stone (rock + cap) | 1 | 936 |
| Small rocks | 6 | 212 |
| Leaves | 168 | 2352 |
| Petals | 15 | 210 |
| Pollen | 3 | 60 |

**Mesh checks.**
- **Whole objects.** Every object has 0 non-manifold edges and verts (0 bowties), 0 boundary, wire or loose
  elements, 0 zero-area faces and 0 n-gons. Normals point outward, transforms are applied, and the origin is at the
  bbox bottom centre.
- **Per shell (`shells_report`).** Every shell is closed and manifold, with 0 self-intersecting face pairs and 0
  inverted faces.
  - The inverted test casts five rays, ignores hits on the face itself, and merges hits closer than 1e-4. With a
    single ray, a ray through an edge counted twice.
- **Corners.** No corner is under 5° (minimum 5.0° on the hero).
- **Tools.** m033's union, floor cut and `_finish`, then `m016._clean_mesh`, then `_polish` (m012). A last-resort
  `_kill_slivers` tries a rotate, a collapse or a dissolve on any sliver left, and keeps the result only if the mesh
  stays manifold.
- **MossCap part.** Its rosettes have no rock to sink into, so the ones seated on the rock are staggered 0.09 apart in
  depth (`PART_SINK_STEP`). Coplanar-close undersides had left a 1–3° sliver.
- **Retries.** The part retries up to 6 times with a nudged cap (it passed on attempt 2); the hero passed on attempt
  1.

**Rock-shape targets (§2.2), measured on the MainRock part.**

| Target | Measured | Spec |
| --- | --- | --- |
| Tris (no floor) | 198 | 110–200 |
| Area CV | 1.14 | ≥ 0.6 |
| Edge CV | 0.68 | ≥ 0.35 |
| Valence | 4–10, mean 5.92, top share 0.28 | — |
| Widest | h .45 | h .45–.55 |
| Width at h .05 | .85 | — |
| Width at h .65 | .90 | — |
| Width at h .75 | .85 | — |
| Width at h .85 | .65 | — |
| Base span X / Y | .79 / .75 | .65–.80 |
| Largest facet, front view | 7.5 % | 7–14 % |
| Cleft depth, mid height | 0.75 | 0.6–1.0 |
| Cleft depth, z 0.5 | 0.43 | ≥ 0.3 |
| Rear crease | 0.27 | — |

- **Borderline.** Width at h .8 is about 0.75 (target ≥ 0.78). Width at h .1 is about 0.88 (target 0.70–0.80):
  the foot is still a little wide, because B adds width low on the left.
- **Facets.** `facets_seen` 38 is a geometric count of every front-facing coplanar region with no occlusion, so it
  reads higher than the sheet's 18–30 visible regions.
- **Hero stone.** Its rock faces measure the same: cleft 0.75, largest facet 7.7 %.

## Stage 3: UV

`M.smart_uv` with angle 45, `ANGLE_BASED` and margin 0.008, then `m012._uv_unfold`.

| Object | Islands | Overlaps | Flipped | Min gap | Border | Density (min / med / max) | Conformal stretch p95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Hero | 1491 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.04 |
| MainRock | 23 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.05 |
| MossCap | 204 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.00 |
| SmallRock | 11 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.00 |
| Foliage | 121 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.02 |

An earlier hero build had 7–10 flipped triangles; the final build has 0.

## Stage 4: Materials, colour and texture

**Keys**, written into `PALETTE` with the pass notes:

| Key | Hex | Roughness | Low spec |
| --- | --- | --- | --- |
| `m035_rock` | `#A8928D` | 0.9 | no |
| `m035_rock_cool` | `#81767C` | 0.9 | no |
| `m035_rock_light` | `#B59D97` | 0.9 | no |
| `m035_moss_stain` | `#546330` | 0.95 | yes |
| `m035_moss` | `#7F980E` | 0.9 | yes |
| `m035_moss_sun` | `#ABB604` | 0.9 | yes |
| `m035_moss_deep` | `#51720B` | 0.9 | yes |
| `m035_moss_under` | `#6E5F49` | 0.95 | no |
| `m035_leaf` | `#60A802` | 0.85 | yes |
| `m035_leaf_young` | `#9DB702` | 0.85 | yes |
| `m035_leaf_deep` | `#387902` | 0.85 | yes |
| `m035_petal` | `#C1C7CA` | 0.7 | no |
| `m035_pollen` | `#B1A100` | 0.7 | no |

The warm rock key stays R > G > B: hue about 10° as a key, and it renders at hue 18–20°.

**Calibration passes.**
- **Pass 1.** `K.calibrate` on the dome against the §5.4 targets, 6 iterations. Rock keys use kind "all", because
  the stone filter drops sat > 0.18. Moss sun uses "vivid", because the green filter drops it.
- **Pass 2.** Linear gains so the hero's f34_sheet medians match the sheet's.
  - Rock ×(1.37, 1.27, 1.24).
  - Cap ×(1.09, 1.12, 0.5).
  - Leaf and leaf deep: green ×1.35 then ×1.15. Leaf young: green ×1.15.
- **Pass 3.** Moss under ×1.5.

**Blend, all by position, never by facing.**
- **Rock.** A noise field gives whole-facet `rock_cool` patches at up to 33 % mix (scale 0.20). Upper-half
  `rock_light` patches reach up to 25 %. Tint mottling uses amp 0.04, scale 0.3.
- **Stain.** The faces near the cleft-foot blob and B's two low front-left blobs are first cut into level bands at z
  0.55, 1.1 and 1.65 (`STAIN_BANDS`). Bands below 1.65 then take `rock_x_moss_stain` at 40 % or 80 %.
  - Whole facets painted, and K.refine'd ones, both read as tall green spikes.
- **Cap.** The raised centre is moss→sun at 67 %. Lobe ridges take one of three moss→sun shades per lobe, the sides
  half of that, the notch valleys deep→moss at 50 % and the rim band moss. The underside is `moss_under`, a hard
  edge.
  - Painting by height alone gave a facing correlation of 0.87, then 0.67. It is now 0.30 on the cap part and 0.0 on
    the hero.
- **Small rocks.** Each has its own tint (±0.06). R2, R4 and R5 carry a moss stain on their top facets.
- **Leaves.** Five tiers along each mound: deep 40 % → deep 20 % → leaf → young 50 % → young. Each cluster has its
  own tint (±0.04), and leaf mottling uses amp 0.04, scale 0.9.
- **Finish.** Moss and leaves use `K.FOLIAGE_SPEC`. There is no emission.

**Rendered colours against the sheet** (medians, the study's masks; foliage = green below 0.55 H).

| View | Rock (ours / sheet) | Cap (ours / sheet) | Foliage (ours / sheet) |
| --- | --- | --- | --- |
| f34_sheet | `#C8A89B` / `#BFA194` | `#A7BE0F` / `#A1B809` | `#5D7F09` / `#608904` |
| front_sheet | `#C3A497` / `#C0A394` | `#A6BC0F` / `#96B10C` | `#5A7E08` / `#729405` |
| rear_sheet | `#B19791` / `#B0988E` | `#87A00C` / `#A2B808` | `#569006` / `#6E9004` |
| r34_sheet | `#B09790` / `#AE988D` | `#88A10B` / `#A2B607` | `#579206` / `#668D04` |
| side_sheet | `#927E77` / `#B29A90` | `#879F0D` / `#9DB30C` | `#4A7605` / `#6C8F05` |

- The **rock** is within 10 everywhere but the side, which is darker in our side light.
- The **cap** is within 12 in the front views. It is about 20 darker in the rear and side, where the studio light is
  behind it.
- The **foliage** is within 12 in f34; elsewhere it is darker (shade).
- **Parts shots** (lit from above): small rock `#CCAEA3` against `#BCA195` (16 light), main rock `#D1AFA1`, cap
  `#B0C70E`, foliage cluster `#68B807` against `#72A907`.
- **Flowers.** Petals render 255/255/238 in the parts shot (clipped where they face the sun). Pollen renders
  (241, 213, 59): hue 51°, sat 0.76.

**Shares and silhouette against the sheet.**
- f34_sheet: rock 0.775 / green 0.224 (cap 0.087, foliage 0.137) / flower 0.001. The sheet is 0.737 / 0.258 (0.109,
  0.149) / 0.005.
- rear_sheet: 0.708 / 0.292 (0.108, 0.184). The sheet is 0.715 / 0.279 (0.105, 0.173).
- side_sheet: 0.745 / 0.255 (0.082, 0.172). The sheet is 0.741 / 0.251 (0.097, 0.154).
- r34_sheet: 0.728 / 0.272 (0.098, 0.174). The sheet is 0.708 / 0.288 (0.112, 0.175).
- W : H: f34 1.426 (sheet 1.473), r34 1.361 (1.338), rear 1.435 (1.272), side 1.319 (1.250).
- Top-profile error, mean / max: f34 0.060 / 0.23, front 0.055 / 0.15, r34 0.059 / 0.27, rear 0.062 / 0.23, side
  0.091 / 0.30.

## Stage 5: Lighting

Skipped: the sheet shows nothing that glows (decision 8). There are no emissive keys and no light sockets.

Studio check (Requires Manual Validation):
- the rock stays warm grey-pink under the game's sun;
- the cap's lime and the foliage's green stay two distinct greens;
- the petals don't bloom to flat white.

## Stage 6: VFX

Skipped: the sheet shows no glow, dust, sparkle or particles (decision 8). The hero has no `vfx_kind` children, and
`build()` reports it as a problem if any appear.

## Modeller's notes for the verifier

- **Cameras** (`SHEET_VIEWS`, 3× lens, floor hidden):

  | Shot | Azimuth, elevation | Against |
  | --- | --- | --- |
  | `f34_sheet` | 0, 10 | the hero cell |
  | `front_sheet` | 0, 6 | the front cell |
  | `r34_sheet` | 150, 9 | the r34 cell |
  | `rear_sheet` | 180, 6 | the rear cell |
  | `side_sheet` | 90, 5 | the side cell |
  | `top_sheet` | 0, 89 | the top cell |

- **Other renders.** The kit views, the four `part_*` shots (−20, 20), `exploded`, `cap_under` (the MossCap part from
  below), `scale` (beside a 5.5-stud stand-in) and `junc_cu` (the cleft foot from −35, 12). The probe renders are
  `f34_e6_sheet` and `f34_e14_sheet`.
- **`measure(path)`** in the builder applies the study's masks (R, G, F, B) to any render, and `rock_metrics(o)`
  computes the §2.2 numbers. `shells_report(o)` returns per-shell closed, manifold, self-hit and inverted results.
- **Known misses.**
  - **Decisions already accepted.** The top view draws no cap. The exploded rock has no cleft.
  - **Undersides.** In `cap_under`, from below with no fill light, the brown underside renders near-black (median
    (57, 47, 34) against the close-up's evenly lit `#725E45`).
  - **Leaves.** A few low outer leaves lie apart from their clump at the foot (rear34, front kit view). The tall
    clusters still read a little as stacked tiers rather than one bushy mass.
  - **Rock foot.** It is a little wide: h .1 width about 0.88 against 0.70–0.80, and base span X 0.79.
  - **Hero height.** It is 7.70, 0.1 under the 7.8 target, within the tolerance. A taller cap pushed the f34 W : H
    down to 1.38, so it was lowered.
  - **Cap colour.** The cap is about 20 darker than the sheet in the rear and side views.
  - **Parts-shot rock.** It reads lighter than the §5.7 target, since it is lit from above with no occluders. The hero
    rock medians match the sheet within 10.
  - **Small-rock part.** It is variant A only. The hero places A ×2, B ×2, C ×1 and the pebble.
- **Cap shapes.** The MossCap part's rosettes are staggered 0.09 in depth and nudged once by the retry, so the part
  differs very slightly from the hero's cap.

## Verification round 1 (verifier, 2026-10-29)

Fresh verifier, read-only, on `wip/M035_verify.blend` (port 9877). Everything was re-measured through the MCP with
`M.audit`, my own per-shell BVH self-intersection and volume code, `m035.shells_report`, `m035.rock_metrics`,
`M.uv_stats`, `K.check` and `m035.measure`. I rendered my own views at 960 × 800 into the scratchpad
(`m035_verify/`), with the same cameras as `SHEET_VIEWS`, and compared them side by side with the sheet cells
(`sbs_*.png`, `z_*.png`).

### Measured

| Object | Tris (limit) | Size W × D × H | Shells | Non-manifold E / V | Boundary, wire, loose | Zero-area, n-gons | Self-hits in shells | Normals | Origin, transforms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `MossyBoulder` | 3770 (4000) | 12.36 × 11.28 × 7.70 | 193: stone 1 (936), rocks 6 (212), leaves 168 (2352), petals 15 (210), pollen 3 (60) | 0 / 0 | 0, 0, 0 | 0, 0 | 0 | outward; every shell has positive volume; 0 inverted | bbox bottom centre (0, 0, 0); rot 0, scale 1 |
| `MossyBoulderMainRock` | 220 (1000) | 9.00 × 8.22 × 6.40 | 1 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 | outward | ok |
| `MossyBoulderMossCap` | 778 (1000) | 5.47 × 4.69 × 2.73 | 1 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 | outward | ok |
| `MossyBoulderSmallRock` | 38 (1000) | 1.66 × 1.64 × 1.19 | 1 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 | outward | ok |
| `MossyBoulderFoliage` | 286 (1000) | 1.55 × 1.61 × 1.20 | 20 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 | outward | ok |

- **Other mesh results.** No duplicate verts, no custom normals and no modifiers. The smallest corner is 5.0° on the
  hero. No shell cuts into the stone by more than 0.044 (target ≤ 0.05). UVs: 0 overlaps and 0 flipped on every
  object, min gap 0.016, border 0.008, density 1.0, conformal stretch p95 ≤ 1.05.
- **Rock shape (part / hero stone).**
  - Rock tris 198 / 319. Area CV 1.14 / 1.64; edge CV 0.68 / 0.97.
  - Valence 4–10, mean 5.92, top share 0.28.
  - Widest at h .45. Base span 0.79 / 0.75. Crown faces 11, spanning 6.5 × 6.0.
  - Largest front facet 7.5 % / 7.7 %. Cleft 0.75 at mid height, 0.43 at z 0.5. Rear crease 0.27.
  - Widths at h .05 … .95: .85 .94 .97 .99 1.0 .96 .90 .85 .65 .52.
- **Colour by facing.** `K.check` reports nothing. My own correlation of face normal z against key luminance is
  0.11 on the rock, 0.33 on the cap top (0.58 only when the brown underside is included, which is a hard material
  edge by position) and −0.02 on the leaves.
- **No painted foot band.** Rock key luminance is 147.7 below z 1 against 149.9 at mid height.
- **Tint.** A per-corner `Tint` layer, 0.933–1.076 (std 0.026).
- **Lighting and VFX.** The hero has no children and no sockets, and no material has emission > 0, which matches
  the sheet.

| Shot vs cell | W : H (sheet) | Rock / green (cap, foliage) / flower | Sheet | Profile err mean / max | Rock median (sheet) | Cap median (sheet) | Foliage median (sheet) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f34_sheet (0, 10) | 1.429 (1.473) | .773 / .225 (.087, .138) / .002 | .737 / .258 (.109, .149) / .005 | 0.060 / 0.24 | `#C8A89B` (`#BFA194`) | `#A8BF19` (`#A1B809`) | `#5C7E0C` (`#608904`) |
| front_sheet (0, 6) | 1.482 (1.363) | .782 / .217 (.081, .136) / .001 | .747 / .245 / .008 | 0.055 / 0.15 | `#C2A396` (`#C0A394`) | `#A8BE19` (`#96B10C`) | `#577C0C` (`#729405`) |
| r34_sheet (150, 9) | 1.363 (1.338) | .728 / .272 (.098, .174) / 0 | .708 / .288 / .004 | 0.060 / 0.26 | `#B09790` (`#AE988D`) | `#89A213` (`#A2B607`) | `#55920C` (`#668D04`) |
| rear_sheet (180, 6) | 1.439 (1.272) | .707 / .292 (.108, .184) / 0 | .715 / .279 / .007 | 0.064 / 0.23 | `#B19790` (`#B0988E`) | `#88A114` (`#A2B808`) | `#55900B` (`#6E9004`) |
| side_sheet (90, 5) | 1.320 (1.250) | .745 / .255 (.082, .172) / 0 | .741 / .251 / .008 | 0.091 / 0.30 | `#927E77` (`#B29A90`) | `#89A016` (`#9DB30C`) | `#497509` (`#6C8F05`) |
| top_sheet (0, 89) | W : D 1.114 (1.084) | .552 / .445 (cap known miss) | .670 / .324 | — | `#C8A99D` (`#C4A89A`) | — | — |

- **Colour families.** The rock is warm, R > G > B, in every key and mix (`#A8928D`; the cool mix `#9B8987` is
  still R > G > B, never mauve). It renders at hue about 17° with sat 0.22. The cap renders at hue 68° with sat 0.87,
  the foliage at hue 78° with sat 0.90, so the two greens are 10° apart.
- **Parts shots.** Small rock `#C2A59B` (target `#BCA195`). Cap part `#B3C718`. Foliage part `#64B912` (target
  `#72A907`). Cap underside from below `#483E30`, against the close-up's `#725E45` (key `#6E5F49`).
- **Detached shells** (hero; distance to the nearest other shell or the ground):
  - 25 leaf or petal shells sit more than 0.03 from everything, 13 more than 0.1, and 2 more than 0.2. The worst is
    0.23, a leaf of F3 at (−5.83, −1.36, 1.95) and a leaf of F5a at (1.95, 4.69, 1.77), in build coordinates.
  - At a 0.1 tolerance, 39 shells (33 leaves, 5 petals, 1 pollen) have no chain of contact to the ground or the
    stone. These are the upper tiers of the tall clusters, which have no stem.

### Findings

1. **Blocker: the tall foliage clusters read as sparse ladders of separate pointed leaves, not the sheet's dense,
   rounded clumps.** This is clearly visible in the rear, r34, side and top views.
   - **What the sheet shows.** The rear and r34 show a big compact mound of plump leaves at the left and tight
     clumps at the right. The side shows compact mounds at both feet, with the middle of the flank bare. The top
     shows a near-continuous ring hugging the base.
   - **What ours shows.** F3, F4, F5a, F5b and F6 are 0.55-stud tiers of narrow, diamond-shaped leaves that splay
     out sideways. They read as fern or herring-bone columns, with single leaves floating apart (see "Detached
     shells" above).
     - In the side view, F6 stands as a leaf ladder across the middle of the +X flank, where the sheet has bare rock.
     - In the top view, the clusters are separate tufts outside the rim instead of a ring.
     - In the rear view, F5a's flower faces away and shows only as a grey speck.
   - **Fix target.**
     - Rebuild each tall cluster as 2–3 overlapping dense mounds (the low-cluster rosette, stacked so that each
       mound's leaves overlap the one below and press against the rock).
     - Every leaf within 0.03 of a neighbour, the rock or the ground.
     - Leaves broader and rounder, like the part list's plump ovate leaves: `LEAF_W` towards 1.0, rounder outline
       corners and a short tip.
     - Move F6 forward to about y −1.5 … −2.5 (the front-right corner), so the side cell's mid-flank is bare and
       the f34's right column stays at f .83–.98.
     - Tighten the back and left clusters into a ring against the base, as seen from the top.
     - Tilt F5a's flower toward +Y.
     - Budget: the hero is at 3770 of 4000. Get the density from fewer, bigger, rounder leaves, not more leaves.
     - Re-measure: shares within ±4, side profile mean ≤ 0.07, and 0 leaves farther than 0.05 from a neighbour.
2. **Minor: the cap is spikier and taller-looking than the sheet's low scalloped mats.**
   - Its lobes end in pointed, drooping corners, so from the front it reads as green shards. The sheet's rosettes are
     broad and low, with rounded scalloped rims and a visible rim band.
   - Cap share in the f34 is .087 against .109 (just outside ±2).
   - Fix target: lower lobe-tip droop (`ROS_TIP_Z`), blunter corners and a slightly larger footprint.
3. **Minor: the cap is 20–26 levels darker than the sheet in the rear, r34 and side views** (for example rear
   `#88A114` against `#A2B808`). This comes from the studio's key light; it is not a facing paint error. Accept, or
   lift `m035_moss` by about 8 % overall.
4. **Minor: the cap underside renders near-black from below** (`#483E30`). This is lighting: the key `#6E5F49`
   matches the close-up. The underside is also stepped across rosettes rather than one flat slab. Accept.
5. **Minor: the rock reads boxy in the rear and side views.**
   - Its flanks are near-vertical and its crown broad.
   - Side profile: 0.091 mean, 0.30 max at f .80, where the back shoulder drops early.
   - The foot is wide: 0.85 at h .05 and 0.94 at h .15, against 0.70–0.80 at h .1. Width at h .8 is about 0.75
     (target ≥ 0.78).
   - Valence reaches 10 (target 3–8).
   - Fix target: pull the lowest ring of A and B in to about 0.75, and keep h .8 at ≥ 0.78.
6. **Minor: W : H runs wide in the front and rear cells.** Front_sheet is 1.482 against 1.363 (stage-1 range
   1.31–1.42); rear_sheet is 1.439 against 1.272. This is partly the decided 12.0 × 7.8 dressing, and partly the
   leaves splaying out at the ends. It should shrink with finding 1.
7. **Minor: the cleft is real geometry (0.75 deep), but it reads weaker than the sheet's dark V,** because both of its
   walls take similar light in our studio. Accept.
8. **Minor: colour details.**
   - The `rock_light` patches are barely visible: the 25 % mix is only 3 levels above the base key.
   - The petal key `#C1C7CA` is blue-grey (B > R). It renders white, but should be neutral or warm.
   - Pollen renders at sat 0.76 (target ≥ 0.8).
   - The side rock is `#927E77` against `#B29A90`, from the side light.
9. **Minor: counts.** There are 10 clusters, not decision 4's 9: F9 is the cleft-foot tuft, which matches the
   sheet's cleft moss. Accept.

### Decisions check

| Decision | Result |
| --- | --- |
| 1, size | Followed: rock 9.0 × 8.22 × 6.4; dressed 12.36 × 11.28 × 7.70 |
| 2, cleft | Followed: two masses with a real cleft |
| 3, cap | Followed |
| 4, counts | Followed: 5 rocks + pebble from 3 variants; 4 cluster kinds placed 10 times; 3 flowers |
| 5, camera | Followed: 10°, with the 6/10/14 probe |
| 6, packaging | Followed: one fused stone shell; every rock, leaf, petal and pollen dome a closed, manifold shell; 0 bowties, 0 self-hits, no shared faces; `problems` checks closure |
| 7, hero + 4 parts | Followed |
| 8, effects | Followed: none |
| 9, cameras | Followed |
| 10, colour | Followed: warm stone with noise patches, olive stain, cap shaded by lobe position, foliage in tiers, no foot band |
| 11, names | Followed |

### Score and verdict

**6.5 / 10. FAIL (round 1), on one blocker: the tall foliage clusters (finding 1).**

Everything else holds:
- the mesh is clean;
- every budget is met;
- the rock shape targets and the cleft are met;
- colour families, calibration and blending by position are correct.

The rest are minors (findings 2–9). Send finding 1, plus findings 2 and 5 if they are cheap, to a fresh modeller,
then run a fresh verifier.

## Fix round 1 (fix modeller, 2026-10-29)

Fresh fix modeller, background Blender on port 9877, work file `wip/M035.blend` (saved). The final numbers below come
from `build()` run in a freshly restarted session; `problems` is empty. Everything was changed in `m035.py`.

### Blocker: the tall foliage clusters (finding 1)

**What changed.**
- **Dome mounds (`_mound`).** The leaves are now laid over a dome, not splayed out from a stem.
  - Each leaf's middle sits on the dome. Its tip points up toward the dome's top, flaring out 0–0.25 rad. Its face
    points out of the dome, tilted 65 % of the way to straight up (`LEAF_UP`).
  - Points follow an even-area golden spiral over 4–98° from the top (`MOUND_TH`).
  - The clump therefore shows leaf faces from every side and from above, and reads as one rounded mass.
  - Colour still goes by height on the dome: low leaves `leaf_deep` mixes, top ones `leaf_young`. Nothing is coloured
    by facing.
- **Core per mound (`_core`).** Every low or tall mound has a hidden heart: a 12-tri closed hexagonal bipyramid at
  0.62 of the mound's radius, in `leaf×deep 60` with its upper cone `leaf×deep 20`. Through the gaps between leaves it
  reads as the clump's shaded inside, as on the sheet, instead of rock or sky.
- **Tall clusters (F3, F4, F5a, F5b, F6).** Each is 3 overlapping mounds (`TALL_MOUNDS`: radius 1.0 / 0.85 / 0.72 of
  `0.40 × w`; 9 / 8 / 7 leaves).
  - The ground mound has its centre at 0.4 of its radius above the ground. The top mound ends at the cluster's height.
  - Each upper mound sits 45 % of the way from straight above the ground mound to resting on the flank
    (`UPPER_LEAN`). Where the flank bulges past the column, it rests on the flank.
  - Mounds against the rock keep their leaves within 110° of straight out (`OPEN_ARC`).
- **Low and small clusters.** Each is one mound of 12 or 7 leaves, radius `0.36 × w` or `0.34 × w`.
- **Leaves (`_leaf`).**
  - `LEAF_W` 0.86 → **1.0**. The outline is widest at 0.66 of the length (was 0.60), so the tip is blunt, about 115°.
    Camber 0.22 → 0.24.
  - The underside is now a flat fan from the stem point: **12 tris a leaf** (was 14). Petals keep their 14-tri
    thickened form.
  - Leaf length 0.62–0.76 for low and tall clusters, 0.48–0.58 for small ones. That means fewer, bigger, rounder leaves
    than the sheet's.
- **Contact (`_Contact`).** Every leaf, core and whole flower is placed against what is already there: the ground, the
  stone, the small rocks and the leaves accepted before it.
  - A piece further than `CONTACT` (0.03) from all of that slides toward its nearest point until it is 0.015 away.
    The stone guard then runs again, so nothing cuts more than 0.05 into the stone.
  - So every shell has a chain of contact down to the ground or the stone.
  - In the final build, 75 pieces moved, the furthest by 0.63.
- **`contact_report(o)`.** This new check gives, per shell, the triangle overlaps and the vert-to-surface gaps against
  every other shell and the ground. It counts:
  - shells touching nothing within 0.03;
  - the worst gap;
  - shells with no chain to the ground or the stone, at 0.03 and at 0.1.

  `build()` now reports any floating or unchained shell on the hero or the Foliage part as a `problem`.
- **Layout (`CLUSTERS`, `SMALL_ROCKS`).**
  - **F6** moved from (5.2, 0.2) to **(5.0, −2.3)**; its seat is (5.00, −2.60) after `DRESS_DY`. It is the front-right
    column, still the f34's right end. The side view's mid-flank is now bare rock.
  - **R3** moved from (5.0, −2.4) to (5.2, −3.3), out of F6's seat.
  - **F5b** moved from (4.2, 2.8) to (4.0, 3.3), w 1.7, h 3.0. This fills the side cell's back clump.
  - **R4** moved from (3.6, 3.6) to (3.0, 4.2), out of F5b's seat.
  - **Ring seating (`hug`).** F3, F4, F5a, F5b, F6 and F8 are clamped so the ground mound's centre stands between
    0.3 and 1.0 × its radius outside the rock's widest outline along its azimuth (`HUG_MIN`, `HUG_MAX`). This puts the
    back and left clusters in a ring hugging the base. F3 and F6 keep their table places (`HUG_MAX_OF` 2.0), because
    the sheet's front silhouette ends in them.
  - Heights: F3 2.6, F4 2.3, F5a 2.8, F5b 3.0, F6 3.2.
- **Flowers.**
  - **F5a's flower faces the rear (+Y)** (`FLOWER_FACE`); F1's and F3's face the front.
  - Every flower now sits on its top mound's shoulder on the side it faces, at 0.95 of the mound's radius up, instead
    of sunk among the leaves. `FLOWER_TILT` 0.30 → 0.50.

### Minors

- **Cap (finding 2).** `ROS_TIP_Z` 0.85 → **1.45**, so the lobe corners are level with the notch tops and no longer
  droop. `ROS_CORNER` 0.20 → **0.28**, for blunter, broader lobe ends. Rosette radii × **1.06** (`ROS_SCALE`).
- **Rock (finding 5).**
  - The shoulder was let out: A's 0.91 ring 0.82 → **0.90**, B's 0.80 ring 0.84 → **0.93**. The width at h .8 is now
    0.79 (target ≥ 0.78).
  - The front depth now tapers more than the back: `y_taper` (front, back) **(0.36, 0.16)**, was 0.30 both. This keeps
    the side cell's back shoulder broad and gives a side profile of 0.055.
  - **Foot not narrowed: tried and reverted.**
    - At A 0.60/0.74 and B 0.66/0.82 the f34 rock read as a ball on a stalk, not the sheet's squat barrel.
    - A middle setting (0.62/0.79, 0.70/0.89) only brought h .15 to 0.90.
    - The foot rings are back at the round-1 values.
  - Valence was not changed (max 10 on the MainRock part).
- **Colour.**

  | Key | Change | Why |
  | --- | --- | --- |
  | `m035_moss` | `#7F980E` → **`#849E0F`** (×1.04) | At ×1.08 (`#89A40F`, tried), the f34 cap read 17 levels over the sheet (`#B2C70F` against `#A1B809`). The rear, r34 and side caps stayed about 20 under at either setting, because there the studio key light is behind the cap. ×1.04 keeps the f34 cap within 12. |
  | `m035_rock_light` | `#B59D97` → **`#C6AFA8`**, mix 0.25 → **0.35** | Its patches now reach about 10 levels over the base key (12 / 23 / 35 % mixes); before, they were 3. |
  | `m035_petal` | `#C1C7CA` → **`#D3D2CB`** | A warm-neutral white (R ≥ G > B), no longer blue-grey. |
  | `m035_pollen` | `#B1A100` → **`#CCAE00`**, low specular | It now renders at sat 0.94 (was 0.76). |
  | `m035_leaf`, `m035_leaf_young`, `m035_leaf_deep` | `#60A802` → `#5B8702`, `#9DB702` → `#95A102`, `#387902` → `#346002` | The new upward-facing leaves catch the key light. With the old keys the f34 foliage rendered `#6EB30A` against the sheet's `#608904`. Linear gains R ×0.9, G ×0.62 (young G ×0.75). |

### Before → after (round-1 verifier's numbers → this build)

| Measure | Target | Before | After |
| --- | --- | --- | --- |
| Hero tris | < 4000 | 3770 | **3844** (stone 1034, rocks 212, leaves and cores 194 shells / 2328, petals 210, pollen 60) |
| Hero size | 12.0 ± 0.5 × 11.1 ± 0.6 × 7.8 ± 0.3 | 12.36 × 11.28 × 7.70 | **12.11 × 10.91 × 7.87** |
| Leaf or petal shells > 0.03 from everything | 0 | 25 | **0** (largest gap of any shell to its nearest neighbour: 0.015) |
| Shells with no contact chain (0.03 / 0.1) | 0 | — / 39 | **0 / 0** |
| Mesh, per object and per shell (non-manifold E/V, boundary, wire, loose, zero-area, n-gons, self-hits, inverted, volume ≤ 0) | 0 | 0 | **0** (219 hero shells; smallest corner 5.03°) |
| UV overlaps / flipped; min gap; border; conformal p95 | 0 / 0 | 0 / 0; 0.016; 0.008; ≤ 1.05 | **0 / 0; 0.016; 0.008; ≤ 1.04** |
| Side profile, mean / max | ≤ 0.07 | 0.091 / 0.30 | **0.055 / 0.21** |
| f34 profile | — | 0.060 / 0.24 | 0.060 / 0.15 |
| Front profile | — | 0.055 / 0.15 | 0.062 / 0.24 |
| r34 profile | — | 0.060 / 0.26 | 0.067 / 0.22 |
| Rear profile | — | 0.064 / 0.23 | 0.073 / 0.34 |
| Front W : H | toward 1.363 | 1.482 | **1.432** |
| Rear W : H | toward 1.272 | 1.439 | **1.359** |
| f34 / r34 / side W : H | 1.473 / 1.338 / 1.250 | 1.429 / 1.363 / 1.320 | 1.368 / 1.404 / 1.247 |
| f34 rock / green (cap, foliage) | .737 / .258 (.109, .149) ± 4 (cap ± 2) | .773 / .225 (.087, .138) | **.756 / .242 (.098, .144)** |
| Front | .747 / .245 (.101, .143) | .782 / .217 (.081, .136) | **.765 / .234 (.092, .142)** |
| r34 | .708 / .288 (.112, .175) | .728 / .272 (.098, .174) | **.701 / .299 (.094, .206)** |
| Rear | .715 / .279 (.105, .173) | .707 / .292 (.108, .184) | **.691 / .309 (.103, .206)** |
| Side | .741 / .251 (.097, .154) | .745 / .255 (.082, .172) | **.738 / .262 (.086, .176)** |
| Top (cap is a known miss) | .670 / .324 | .552 / .445 | .516 / .481 (cap .209, foliage .272) |
| Rock median, f34 | within 10 of `#BFA194` | `#C8A89B` | `#C9AA9C` |
| Cap median, f34 / rear / side | `#A1B809` / `#A2B808` / `#9DB30C` | `#A8BF19` / `#88A114` / `#89A016` | `#ADC40F` / `#8AA50D` / `#8AA10D` |
| Foliage median, f34 / front / rear | `#608904` / `#729405` / `#6E9004` | `#5C7E0C` / `#577C0C` / `#55900B` | `#688E0A` / `#668B0A` / `#507C06` |
| Foliage part (parts shot) | `#72A907` | `#64B912` | `#629907` |
| Petals (parts shot): median / 75th percentile | ≥ `#F0F0EA`, ≤ `#FFFFFD` | 255/255/238 | `#FFFFFD` / `#FFFFFE`, R ≥ G > B |
| Pollen (parts shot): hue, sat | 46–56°, ≥ 0.8 | 51°, 0.76 | **51°, 0.94** |
| Cap part (parts shot) | `#98B11B` | `#B3C718` | `#B3C90F` |
| Cap underside, from below | lighting | `#483E30` | `#393022` (from below with no fill; key unchanged) |
| MainRock: tris, area CV, edge CV | 110–200, ≥ 0.6, ≥ 0.35 | 198, 1.14, 0.68 | 188, 1.14, 0.67 |
| MainRock: widths at h .05 / .15 / .75 / .85 | h .1 0.70–0.80; h .8 ≥ 0.78 | .85 / .94 / .85 / .65 | .85 / .94 / **.88 / .70** (h .8 ≈ 0.79) |
| MainRock: base span, largest front facet, cleft mid / z 0.5 | .65–.80, 7–14 %, 0.6–1.0 / ≥ 0.3 | .79/.75, 7.5 %, 0.75 / 0.43 | .79/.76, 8.3 %, 0.78 / 0.44 |
| MainRock valence | 3–8 | 4–10 | 3–10 (not changed) |
| `K.check` | nothing | nothing | nothing (`problems` empty) |

The flower share (0.000–0.002 against 0.004–0.008) can't be judged at the 480 × 400 preview size: a flower is a
handful of pixels there. All three flowers show in the f34, front, rear, top and junction renders.

### Looked at, against the sheet

- **Rear and r34.** The left and right foliage are compact leafy mounds of round, upturned leaves. F5a's flower faces
  the camera, and the middle of the foot has bare rock.
- **Side.** Clumps stand at both feet and the mid-flank is bare rock, as on the sheet.
- **Top.** The clusters ring the base round the left, back and right and leave the front open. The cap is the known
  miss.
- **Junction close-up.** F2 and the cleft tuft read like the sheet's Rock / Foliage Junction: plump leaves with a
  flower, against the rock across a small gap.
- **Foliage part.** It reads like the part-list cluster: round leaves round a mound with a white flower.

### Left over

- **f34 right column.** F6, seen from the front, still reads as three stacked tufts rather than one solid column. It is
  dense and touching, but a little stepped.
- **Rear profile** is 0.073 (was 0.064). The rock's model-left back shoulder sits lower than the sheet's (f .80–.90).
  The r34 profile is 0.067 (was 0.060).
- **Rock foot.** It is still 0.94 wide at h .15, against 0.70–0.80. Narrowing it read as a ball on a stalk (see
  above). Valence max is still 10.
- **Rear, r34 and side cap and foliage** are about 20 levels darker than the sheet. That is the studio's key light
  behind them; the front views are within tolerance.
- **f34 W : H** is 1.368 against 1.473, while the front is 1.432 against 1.363. The sheet's two front drawings disagree
  here; the front cell and the dressed size are favoured.

## Verification round 2 (verifier, 2026-10-29)

Fresh verifier, read-only, on `wip/M035_verify.blend` (background Blender, port 9880; nothing saved, no builder
edits). Everything was re-measured through the MCP: `M.audit`, `m035.shells_report`, `m035.rock_metrics`,
`M.uv_stats`, `K.check`, `m035.contact_report`, plus my own code for floating shells, contact chains, stone
penetration, facing correlation and per-cluster vertical gaps. My renders (960 × 800, the `SHEET_VIEWS` cameras with
m033's long lens, plus close-ups, two game-camera shots and the part shots) and side-by-sides with the sheet cells
(`sbs_*.png`) are in the scratchpad `m035_verify2/`. Sheet colours were sampled again with the study's masks.

### Measured

| Object | Tris (limit) | Size W × D × H | Shells | Non-manifold E / V | Boundary, wire, loose | Zero-area, n-gons | Self-hits in shells | Normals | Origin, transforms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `MossyBoulder` | 3844 (4000) | 12.11 × 10.91 × 7.87 | 219: stone 1 (1034), rocks 6 (212), leaves and cores 194 (2328), petals 15 (210), pollen 3 (60) | 0 / 0 | 0, 0, 0 | 0, 0 (18 quads) | 0 | outward; 0 inverted; every shell volume > 0 | bbox bottom centre; rot 0, scale 1 |
| `MossyBoulderMainRock` | 210 (1000) | 9.00 × 8.19 × 6.40 | 1 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 | outward | ok |
| `MossyBoulderMossCap` | 848 (1000) | 5.61 × 4.87 × 2.95 | 1 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 | outward | ok |
| `MossyBoulderSmallRock` | 38 (1000) | 1.66 × 1.64 × 1.19 | 1 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 | outward | ok |
| `MossyBoulderFoliage` | 246 (1000) | 1.71 × 1.74 × 0.99 | 19 | 0 / 0 | 0, 0, 0 | 0, 0 | 0 | outward | ok |

- **Other mesh results.** No duplicate verts, custom normals or modifiers. Smallest corner 5.03° (hero). UVs: 0
  overlaps and 0 flipped on every object, min gap 0.016, border 0.008, density 1.0, conformal p95 ≤ 1.04.
- **Floating dressing (my own code).** Per shell, the smallest vert-to-surface gap to any other shell (both ways),
  triangle overlaps, and the ground (z ≤ 0.03):
  - hero: **0 shells more than 0.03 from everything** (184 touching, 28 within 0.015, 6 within 0.03; worst 0.015);
    **0 shells with no contact chain to the ground or the stone**, at 0.03 and at 0.1;
  - Foliage part: 0 floating, 0 unchained;
  - deepest cut of any dressing vert into the stone 0.0496 (limit 0.05);
  - `m035.contact_report` agrees (0 / 0 / 0).
- **Tall clusters, vertical coverage** (leaf and core shells within 2.2 of each column's seat): F3, F4, F5a and F5b
  have no empty height band. **F6 has one: nothing spans z 1.96–2.20**, so its top mound is held only by 2 leaves
  touching the stone flank, 0.24 above the rest of the column.
- **Rock shape (part / hero stone).** Rock tris 188 / 302; area CV 1.14 / 1.63; edge CV 0.67 / 0.97; valence 3–10
  (mean 5.92, top share 0.36) / 3–15 (where the cap fuses on); widest at h .45; base span 0.79 / 0.76; largest front
  facet 8.3 % / 8.6 %; cleft 0.78 at mid height, 0.44 at z 0.5; rear crease 0.32. Widths at h .05 … .95: .85 .94 .97
  .99 1.0 .97 .93 .88 .70 .54 (h .8 ≈ 0.79).
- **Colour by facing.** `K.check` reports nothing. Correlation of face normal z with key luminance: hero rock 0.13,
  cap 0.22, leaves 0.13; MainRock 0.04; MossCap 0.25; Foliage 0.13. The SmallRock part is −0.76, but all its faces
  are `rock_x_cool_22` / `_33` (4 levels apart) from the position noise field, which on a 1.7-stud rock happens to
  fall on the top: position, not facing, and invisible in the render.
- **No painted foot band:** MainRock key luminance 147.2 below z 1 against 150.2 at z 2–4.5.
- **Tint:** a per-corner `Tint` layer, 0.932–1.078, sd 0.027.
- **Lighting and VFX:** no children, no sockets, emission 0 on all 26 materials.

| Shot vs cell | W : H (sheet) | Rock / green (cap, foliage) / flower | Sheet | Profile err mean / max | Rock median (sheet) | Cap median (sheet) | Foliage median (sheet) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f34_sheet (0, 10) | 1.369 (1.473) | .754 / .243 (.098, .145) / .002 | .737 / .258 (.109, .149) | 0.058 / 0.14 | `#C9AA9C` (`#BFA294`) | `#ADC50F` (`#9EB608`) | `#688E09` (`#608804`) |
| front_sheet (0, 6) | 1.429 (1.363) | .763 / .235 (.092, .144) / .002 | .747 / .245 (.101, .143) | 0.060 / 0.21 | `#C8A99C` (`#BFA294`) | `#ACC40F` (`#95B00C`) | `#668B09` (`#729405`) |
| r34_sheet (150, 9) | 1.401 (1.338) | .699 / .301 (.094, .208) / 0 | .708 / .288 (.112, .175) | 0.068 / 0.22 | `#AF968F` (`#AE988E`) | `#8AA50C` (`#A1B607`) | `#507D05` (`#668D04`) |
| rear_sheet (180, 6) | 1.356 (1.272) | .689 / .311 (.103, .207) / 0 | .715 / .279 (.105, .173) | 0.072 / 0.32 | `#AF968F` (`#B0988E`) | `#8AA50D` (`#A2B808`) | `#4F7C06` (`#6E9004`) |
| side_sheet (90, 5) | 1.244 (1.250) | .737 / .263 (.086, .177) / 0 | .741 / .251 (.097, .154) | 0.054 / 0.21 | `#968079` (`#B29A8F`) | `#8AA10D` (`#9CB20C`) | `#497006` (`#6C8F05`) |
| top_sheet (0, 89) | W : D 1.109 (1.084) | .514 / .483 (cap is the known miss) | .670 / .324 | — | `#C8A99E` (`#C4A89A`) | — | — |

- **Colour families.** Rock warm, R > G > B in every key and render (hue 13–19°, sat 0.18–0.22; never mauve). Cap hue
  68–71°, sat 0.92; foliage hue 77–83°, sat 0.94–0.96: two separate greens, 9–12° apart. Petals render warm white
  (`#FFFFF5`, key `#D3D2CB`, R ≥ G > B). Pollen renders hue 46°, sat 0.73–0.75 in the hero (10 px; the parts shot
  is higher). Every share is within ±4, and every cap share within ±2.
- **Sheet against ours, lit quartiles.** Foliage f34 `#7AA414` against `#A0BB0B`; rear `#5B8809` against `#9FBA0D`.
  The sheet's clumps have bright lime-yellow tops; ours stay a darker, bluer green.

### Findings

1. **Minor: the F6 right column still reads as three stacked tufts** (f34, front and game three-quarter). Its top
   mound sits 0.24 above the middle one, held only by two leaves on the stone, so from the front sky shows between the
   tiers. The sheet's right column is one continuous leafy column. It is attached, so this is not floating dressing.
   Fix target: lower F6's top mound by about 0.3 (or add 2–3 leaves bridging z 1.9–2.3) so the column has no empty
   height band; a vertical-coverage check like the one above should report no gap.
2. **Minor: the back tall clusters (F5a, F5b) read as narrow upright columns, not the sheet's broad rear-left mound**
   (rear, r34). They are dense and rounded now, a clear improvement on round 1's ladders, but each is about two leaves
   wide. The rear foliage share is .207 against .173, so the issue is shape, not amount. Fix target: widen their ground
   mound (`HUG_STRETCH` about 1.6 for F5a/F5b) and drop the top mound, so the back reads as one wide low mound reaching
   about h .45.
3. **Minor: the foliage is darker and less lime than the sheet.** Medians are close in the f34 (`#688E09` against
   `#608804`), but the lit quartile is 20–40 levels below the sheet's in every view, and the rear and side medians are
   about 20–30 under. Fix target: more `leaf_young` on the top third of each mound (now 120 faces against 720 at
   `leaf_x_deep_20`), aiming at the f34 lit quartile of about `#A0BB0B`.
4. **Minor: the rock reads boxy in the rear and side.** Its flanks are near vertical down to the ground and the foot is
   wide (0.85 at h .05, 0.94 at h .15, against the sheet's 0.70–0.80 at h .1). The sheet's rear and side read as a
   dome. The rear profile is the worst (0.072 mean, 0.32 at f .85, the model-left back shoulder). Valence max is 10
   (target 3–8). I agree with the fix modeller that pulling the foot in alone gave a ball on a stalk; it would need
   the lower ring pulled in together with a slightly lower widest ring. Accept for this model.
5. **Minor: the cap reads as faceted star cones rather than low scalloped mats.** It is less droopy than in round 1,
   and its height (1.47 above the crown) and share (f34 .098 against .109) are within tolerance. The sheet's rosettes
   have softer, serrated lobe edges. Accept.
6. **Minor: cap and foliage are about 20 levels dark in the rear, r34 and side** (cap `#8AA50D` against `#A2B808`).
   This is the studio key light behind the model; the front views are within about 15 (f34 cap 15 light). Accept.
7. **Minor: W : H.** f34 1.369 against 1.473 and front 1.429 against 1.363. The sheet's two front drawings disagree
   by the same amount, and the decided 12.0 × 7.8 size is met. Accept.
8. **Minor: top view.** The clusters stand round the left, back and right as separate tufts with gaps between them,
   not the sheet's continuous ring, and F1 and F2 add foliage at the front. The cap is the known miss. Accept.
9. **Minor: pollen** renders at sat 0.73–0.75 in the hero shots (target ≥ 0.8). It is only a few pixels. Accept.

The round-1 blocker is resolved: 0 floating shells and 0 unchained shells (measured independently), and every
cluster is now built from dense rounded mounds of broad round leaves with no splayed ladders. F6 is forward
(seat y ≈ −2.6), the side cell's mid-flank is bare rock with clumps at both feet, and the clusters surround the base
in the top view.

### Decisions check

| Decision | Result |
| --- | --- |
| 1, size | Followed: rock 9.00 × 8.19 × 6.40; dressed 12.11 × 10.91 × 7.87 (all within tolerance) |
| 2, cleft | Followed: two masses, cleft 0.78 deep at mid height |
| 3, cap | Followed |
| 4, counts | Followed: 5 rocks + pebble from 3 variants; 4 cluster kinds placed 10 times (F9 cleft tuft, accepted in round 1); 3 flowers |
| 5, camera | Followed: f34 at 10°, with the 6/10/14 probe on record |
| 6, packaging | Followed: one fused stone shell; every rock, leaf, core, petal and pollen dome a closed manifold shell; 0 bowties, 0 self-hits; `problems` checks closure and contact |
| 7, hero + 4 parts | Followed |
| 8, effects | Followed: none |
| 9, cameras | Followed |
| 10, colour | Followed: warm stone with position-noise cool and light patches, olive stain in the cleft, cap shaded by lobe position, foliage by height on each mound, no foot band |
| 11, names | Followed |

### Score and verdict

**7.5 / 10. PASS (round 2).**

There are no blockers:
- the mesh is clean and every budget is met (hero 3844 / 4000);
- no dressing floats, and every shell chains to the ground or the stone;
- the silhouette and the shares are within tolerance in every cell;
- the colour families are right, and colour is blended by position with Tint mottling;
- every decision is followed.

Findings 1–3 are worth a later polish pass if the main session wants one: F6's gap, a wider rear mound, and brighter
lime leaf tops. The rest should be committed as noted leftovers.

## Main session ruling (2026-10-29)
- **Result:** passed in round 2 (7.5/10) and committed. Round 1 failed (6.5/10) because the tall foliage clusters were sparse, floating ladders.
- **Left for a later polish pass:**
  - F6 reads as three stacked tufts: lower the top mound about 0.3, or bridge the gap.
  - F5a/F5b read as narrow upright columns: use a broader ground mound (`HUG_STRETCH` about 1.6).
  - Lit foliage is 20–40 levels darker and less lime than the sheet: use more `leaf_young` on the mound tops.
  - The rock reads boxy at the rear and side (wide foot, valence 10).
  - The cap reads as faceted star cones.
  - Pollen saturation is 0.74.
- **Export:** 5 assets, 5 solid pieces, 5186 tris, 0 VFX sockets, palette 26 colours, 0 problems.
