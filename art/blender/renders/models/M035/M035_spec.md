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
