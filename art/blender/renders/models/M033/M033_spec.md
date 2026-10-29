# 033 Cave Moss — spec

Reference: `art/blender/assets/references/033.png`. The sheet's own title is "CAVE MOSS", with "28 / 132" at the top left,
"FLINTBORN — INDIVIDUAL MODEL STUDY" at the top right and the footer "FLINTBORN — INDIVIDUAL MODEL STUDY … PAGE
28/132" (INDEX.md row 33 calls it "Flintborn cave moss model study"; the page number is not the index number). The
image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m033.py` → `build()`. Procedure: `art/blender/kit/mcp/STAGES.md`
(one modeller does stages 1–6 in a background Blender; then a fresh verifier does stage 7).

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (no glow, no spores, no particles; §7).

Sheet text:
- **Header:** none beyond the title (no description sentence).
- **Views:** Front Three-Quarter, Rear Three-Quarter, Front, Side, Rear, Top.
- **Exploded Construction:** labels Sprout A, Sprout B, Sprout C (three sprouts in a row at the top, dashed arrows
  down to the clumps), Moss Clump Left, Moss Clump Center Right (printed "Moss Clump Center Ri̲ght", a garbled label
  whose leader ends on the right clump's top), Moss Clump Right, Rock Base, Side Rock (R). The centre clump has no
  label of its own. Below the clumps: one big Rock Base and six small rocks (two small ones high up at the left and
  right = back, two lower ones beside the base = front, and two "side rocks" at the far left and right with dashed
  double arrows pointing at the base).
- **Close-ups:**
  1. "Sprout Junction": "Leaf blades join at base." (a sprout's 4 blades rising from one point in the moss between a
     clump and the moss below it).
  2. "Rock to Moss Interface": "Moss clump sits on rock." / "Flat shaded facets throughout." (a clump resting on a big
     rock, two small rocks at its foot).
  3. "Underside View": "Flat base surface for placement." (the base from below: one broad flat face, outline of two
     lobes with a crease between them, moss peeking over the back rim).
- **Material palette:** Moss Dark, Moss Mid, Moss Light, Rock Light, Rock Mid (§5.1).
- **Modeling notes:** "Chunky, stylized low-poly forms."; "Broad, flat-shaded faces. No smooth shading."; "Simple,
  clean silhouette with clear clump shapes."; "Reusable parts: moss clumps, sprouts, rock base, side rocks."; "Keep
  clean topology and even, readable facets."; "Maintain consistent angles and proportions across all views."
- **Game context:** `src` has no cave-moss node or material (`git grep -i moss src` finds only the zone
  `MosswickForest`, the camp `MossfireCamp`, the creek `MossCreek` and a character colour). `BiomeCatalog.luau` /
  WorldModeling §17 put "sparse cave fungi and moss near damp surfaces" in Emberhollow Caves. WorldModeling §9 table:
  "Cave moss / cave mushrooms: Use subdued greens and warm neutral stalks. Their visibility should come from shape and
  placed lighting, not automatic emission." §10: "For a squat boulder, keep height around 0.5–0.9 of width … Use
  separate moss caps." The old **R07 kit sheet** has `CaveMoss` (built 8.2 × 6.8 × 5.9: a grey dome rock capped with
  three moss clumps, two lime sprouts, four flanking boulders, `harvest_hit` + `harvest_deplete`, plus parts, a
  `CaveMossChunk` drop and `CaveMossDepleted`) and owns its names (§8). `MODEL_PROGRESS.md` row R07 marks it "partial:
  pillowy saturated moss; flat slab base"; its goals file (`art/blender/renders/kit/R07/cave_moss_goals.md`) built the
  clumps from subdivided spheres ("subdiv 3 + dissolve … rounder than the ref's chunkier planes"). `CHECKLIST.md` scores
  it 6/10.

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is
`#F2EDE7` (242, 237, 231). Cell dividers: x 521 (top row); x 305, 528, 770 (second row); rows y 78–458 and 458–695.
The cell labels are blanked to paper before measuring (`m.py`, `BLANK`). View boxes `V`: f34 (16,80,519,456), r34
(524,80,1008,456), front (16,460,303,693), side (308,460,526,693), rear (530,460,768,693), top (772,460,1008,693). The
masks are `cls()` in `m.py` (HSV; background = within 14 of the paper):
- **G, green:** hue 55–140°, sat ≥ 0.30. Split into:
  - **L, lime (sprouts):** G and (hue ≤ 71.5° with v ≥ 0.30, or v ≥ 0.73, or sat ≥ 0.81 with hue ≤ 76°);
  - **M, moss (clumps):** the rest of G.
- **R, rock:** not G, sat < 0.22, v 0.20–0.86.
- **O, other:** the soft ground shadow (left of the hero in the f34 and r34, under the rocks elsewhere) and
  anti-aliased edges; **treated as background, not counted in any share** (2.1 % of the f34 box's object pixels, 1.8 %
  r34, 2.1–2.9 % in the small cells).
- **Known leaks** (pixel colour alone can't separate them; use the same scripts on both images):
  - the deep-shaded sprout faces (hue ≈ 80°, sat 0.78, v 0.36, the same as shaded moss) fall into M: about 15–20 % of
    each sprout's pixels, so L reads low by about 2 points in the front;
  - a few lit moss pixels on the clump crowns next to sprout B (hue 72–73°, v 0.68–0.70) fall into L (< 0.3 points).

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m033_study\`.
Run with the scratch venv `...\scratchpad\venv22\Scripts\python.exe` (Pillow + numpy).
- **Helpers:** `m.py` (masks `cls()`, view boxes `V`, label blanking, `stats`), `comps.py` (connected components
  `label()`), `bb.json` (silhouette boxes), `crop.py`, `gridcrop.py` (crop with a sheet-pixel grid), `grid.py`.
- **Measurements:** `measure.py` → `measure_out.txt` (bboxes, shares, top / bottom / rock-top / green-bottom profiles,
  width per height, shares per 0.1 h and per third); `comps.py` → `comps_out.txt` (each sprout's extents, the
  ground-connected rock band top); `cmp.py` (top profiles of every view against the f34, direct and mirrored);
  `expl.py` → `expl_out.txt` and `shape.py` → `shape_out.txt` (exploded part boxes and width per height).
- **Colour:** `sw.py` (swatches), `samp.py` → `samp_out.txt` (views, regions, exploded parts, close-ups), `grad.py` →
  `grad_out.txt` (bottom → top along clumps, sprouts and rocks), `hist.py`, `probe.py`, `probe2.py` (mask tuning).
- **Names:** `blendall.py` (every sheet, kit and wip `.blend`, zstd-decompressed; run with
  `C:/Users/Orang/.local/bin/python3.14.exe`).
- **Crops:** `f34.png`, `r34.png`, `row2.png`, `expl.png`, `cu.png`, `pal.png`; grids `g_*.png` (10 % grid on the
  silhouette bbox, red = centre lines); mask previews `cls_*.png`, `cls_row2.png` (left the cell, right the mask: dark
  green M, yellow L, grey R, pink O).
- **Zooms:** `z_front.png`, `z_side.png`, `z_rear.png`, `z_top.png`, `z_f34_clumps.png` (facet language of ML and MC),
  `z_expl_clumps.png`, `z_expl_sprouts.png`, `z_expl_base.png` (the rock base and six small rocks, sheet-pixel grid).
- **To run the scripts on our renders,** point `R` (in `m.py`) at the render, set the view box in `V`, drop `BLANK`,
  pass the render's paper as `P`, and re-run `measure.py` (it rewrites `bb.json`), then `comps.py`, `cmp.py`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a harvestable cave resource node, the numbered successor of R07 `CaveMoss`). Hero
  budget 4000 tris, each part under 1000. The plan in §4.3 lands at about 1100–1600.
- **Overall read (check this first).** **One broad, low, faceted grey boulder** (the Rock Base) **capped at the back
  and both sides by three chunky faceted moss clumps**, with **two bright lime sprouts** and **six small rocks** round
  its foot:
  - the **centre clump (MC)** sits highest, on the base's back hump: a broad squat dome with a flat crown polygon;
  - the **left clump (ML)** and **right clump (MR)** drape down the base's left and right shoulders: tilted ovoid
    lumps whose outer ends hang over the side rocks;
  - the base's **front face stays bare grey**, with **sprout A** rising from a notch low on its front;
  - **sprout B** stands taller at the back-right, in the crease between MC and MR, and is the highest point;
  - small rocks: a side rock at each end (under ML and MR), a pebble at the front-left and front-right, and two small
    back rocks.
  - It must read as **one mossy boulder**, not a pile of rocks and not three green balls on a plate.
  - Hero shares (front): moss 39.9 %, sprout 11.3 %, rock 48.8 % (green 51.2 %).
- **Focal silhouettes, in order:**
  1. The three-clump moss crown: ML's rounded top at the left (h .74), MC's broad flat crown above the middle (h .92),
     MR's top at the right (h .69); the moss fills the upper half of every elevation view.
  2. Sprout B's spray of pointed blades at the upper right (the top of the bbox, h 1.0 at f .78).
  3. The bare grey front face with sprout A in its notch, and the low stepped rock skirt (pebbles and side rocks) at
     both ends.
- **Target size: about 6.4 W × 4.75 D × 3.9 H studs** (H = 0.71 C of the 5.5-stud character). Tolerances W ±0.3,
  D ±0.35, H ±0.2. Decision §8.1.
  - **How it was derived.** The sheet has no character. The anchor is the two front pebbles: 0.15–0.16 W in the front
    (f .08–.24 and .70–.87), and the kit's pebble scale (R07 pebbles 1.2–2.0, M023 rocks 0.75–1.35, M031 rocks
    0.6–0.9) puts them at about 1.0 stud, so **W ≈ 6.4**. The front cell (263 × 179 px) then gives **41.1 px per stud**
    (f34 74.1); its screen height 179 px = 4.36 screen studs, which at the cells' 12° elevation (§1.2) is a true height
    of 3.85–3.9 (the sprout B tip sits 2.7 behind the front edge, so 0.56 of the screen height is depth).
  - **Depth:** the side cell has the front cell's height in pixels (179) and is 195 px wide, so at the same scale
    **D ≈ 4.75** (D : W 0.74). The layout (§2) gives 4.65.
  - **Why this size.** The boulder's front hump at the character's hip (z 2.3), the moss crown at the waist (z 3.45),
    sprout B's tip at the chest (z 3.85); clumps 2.1–2.35 across, a hand-height harvest. It sits between M031 Cave
    Mushroom (4.4 × 3.5 × 3.6, its cave sibling) and M023 Clay Deposit (10.0 × 9.6 × 4.75), and well under R07's
    8.2 × 6.8 × 5.9, which was as tall as the player.
  - **Alternatives:** the R07 footprint (× 1.27 → 8.1 × 6.0 × 4.95, pebbles 1.3); the M031 height family (× 0.82 →
    5.25 × 3.9 × 3.2, pebbles 0.8).
  - Resulting part sizes: Rock Base 4.9 × 3.9, front hump z 2.3, back hump z 2.5; MC 2.35 × 2.0 × 1.5; ML 2.35 × 2.1 ×
    1.75 and MR 2.1 × 1.95 × 1.7 (along their tilted axes); sprouts 1.4–1.7 tall; side rocks 1.25–1.3 wide; pebbles
    0.8–1.1.
- **Build frame:** front −Y, +X right, ground z 0, origin = the bbox bottom centre (the layout in §2 is already centred
  on it; stage 2 re-centres exactly).
- **Stud mappings used below** (W 6.4, H_screen 4.36, e 12°, front edge y_f −2.2):
  - front cell X = (f − 0.50) × 6.4; true z = (h × 4.36 − (y + 2.2) × 0.208) / 0.978 for a point at depth y;
  - side cell Y = (f − 0.50) × 4.75 if it were a true +X side (screen right = +Y, the back); it is not (§3.3);
  - rear and top cells: counts, shares and widths only (§3.3, §3.4).

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | Moss M | Sprout L | Rock R | Green M+L | Scale (px/stud) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (16,80,519,456) | 33–506 × 112–429 (474 × 318) | 1.491 | 40.7 % | 10.2 % | 49.1 % | 50.9 % | 74.1 |
| Rear three-quarter (524,80,1008,456) | 538–986 × 130–423 (449 × 294) | 1.527 | 39.2 % | 13.9 % | 46.9 % | 53.1 % | 70.2 |
| Front (16,460,303,693) | 25–287 × 496–674 (263 × 179) | 1.469 | 39.9 % | 11.3 % | 48.8 % | 51.2 % | 41.1 |
| Side (308,460,526,693) | 315–509 × 496–674 (195 × 179) | 1.089 (D : H) | 35.1 % | 18.3 % | 46.5 % | 53.5 % | 41.1 (D 4.75) |
| Rear (530,460,768,693) | 538–751 × 496–674 (214 × 179) | 1.196 | 38.9 % | 15.6 % | 45.5 % | 54.5 % | 33.4 (W 6.4) |
| Top (772,460,1008,693) | 788–994 × 496–674 (207 × 179) | 1.156 | 39.0 % | 13.9 % | 47.2 % | 52.8 % | 32.3 (W 6.4) |

- **Glow share: 0 % in every view.** No pixel is self-lit: the brightest sprout facets are `#D4E15C` (v 0.88), the
  brightest moss `#92B131` (v 0.69), and every part darkens on its shaded side.
- **Ground shadow:** the soft grey shadow is O, i.e. background (1.8–2.9 % of the object pixels).
- **Elevations:** the bottom outline rises .03 H at f .15 and .07 at f .05 above the front point; for a 6.4 × 4.75
  footprint that is e ≈ 12° in the front and f34 (identical drawings, §3.1). The side and rear bottoms match within
  .02 (e ≈ 12°). The top cell is a steep elevated view (≈ 70–80°, image top = back; §3.4).
- **Verifier tolerance:** shares ±4 points (sprout ±3, top ±6); positions and profile values ±0.06 of W/H unless
  stated.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .14 | .36 | .59 | .66 | .71 | .73 | .75 | .86 | .90 | .92 | .92 | .89 | .84 | .90 | .87 | .98 | .93 | .80 | .57 | .47 | .17 |
| Front | .15 | .39 | .60 | .66 | .71 | .73 | .76 | .86 | .90 | .91 | .91 | .88 | .84 | .89 | .95 | 1.0 | .79 | .80 | .56 | .48 | .20 |
| Side | .14 | .43 | .58 | .68 | .75 | .79 | .83 | .84 | .85 | .92 | .91 | .88 | .81 | .92 | 1.0 | .94 | .82 | .82 | .50 | .39 | .28 |
| Rear | .16 | .39 | .53 | .60 | .64 | .74 | .79 | .84 | .85 | .86 | .87 | 1.0 | .99 | .96 | .87 | .81 | .83 | .84 | .55 | .44 | .16 |
| r34 | .16 | .33 | .48 | .71 | .93 | .91 | .83 | .97 | .93 | .85 | .87 | .89 | .91 | .86 | .81 | .73 | .71 | .67 | .62 | .42 | .18 |
| Top (h = back) | .55 | .65 | .74 | .80 | .84 | .87 | .93 | .96 | .97 | .98 | 1.0 | .98 | .96 | .93 | .91 | .91 | .93 | .78 | .73 | .64 | .41 |

- **Front reading:** f .00–.10 the left side rock rising into ML's outer flank (.15 → .60); ML's top .71–.76 at f
  .20–.30; MC's crown .86–.91 at f .35–.55 (flat across f .40–.50); a dip to .84 at f .60 (MC's right shoulder meeting
  MR and sprout B's left blade); sprout B .89–1.0 at f .65–.75; its right blade .79–.80 at f .80–.85; MR's right
  shoulder and the right side rock .56 → .20 at f .90–1.0.
- **Profiles against the f34** (`cmp.py`, 41 columns, mean / max |Δ|): front .014 / .14 (only the sprout tip), side
  .048 / .19, rear .060 / .21, r34 .088 / .28 direct but **.053 / .26 mirrored**, top .128 / .42.

**Bottom profiles** (lowest silhouette pixel per column above the bbox bottom, fraction of H): front .13 .07 .04 .03
.03 .03 .02 .01 .01 .01 .01 .01 .02 .03 .03 .02 .02 .03 .06 .08 .12; f34 the same within .01; side .12 → .01 at f
.40–.65 → .12; rear .12 → 0 at f .55 → .09; top (an outline) .18 → 0 → .34.

**Rock band top** (ground-connected rock per 0.05 f, `comps.py`): front `.20 .39 .32 .26 .32 .36 .42 .45 .40 .30 .35
.47 .56 .46 .41 .28 .25 .26 .34 .49 .21` — the left side rock (.39 at f .05), the base's front-left shoulder
(.42–.45 at f .30–.35), the notch round sprout A (.30–.35 at f .45–.50), the front hump right of the sprout (.56 at f
.60), the front-right pebble (.25–.28 at f .75–.85), the right side rock (.49 at f .95). The f34 is the same within
.02. Side `.18 .09 .25 .25 .27 .32 .36 .40 .45 .46 .35 .31 .31 .30 .32 .35 .47 .44 .26 .39 .28`; rear `.18 .40 .42
.24 .25 .20 .28 .36 .34 .31 .31 .32 .42 .53 .49 .45 .40 .23 .27 .39 .16`.

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .13@.42 .93@.05 .96@.04 .95@.04 .91@.06 .86@.08 .77@.11 .63@.18 .52@.32 .39@.40 .01@.78
front  .15@.40 .94@.04 .97@.03 .95@.04 .90@.06 .87@.07 .78@.10 .64@.17 .54@.32 .38@.40 .02@.75
r34    .26@.43 .94@.02 .96@.03 .90@.04 .87@.08 .82@.11 .71@.20 .67@.15 .50@.21 .42@.19 .01@.37
side   .17@.44 .95@.03 .94@.06 .93@.06 .88@.05 .84@.06 .71@.11 .69@.16 .62@.26 .31@.45 .02@.70
rear   .14@.47 .96@.04 .95@.03 .94@.03 .90@.06 .85@.08 .71@.15 .61@.23 .53@.31 .12@.56 .06@.53
top    .10@.46 .79@.11 .96@.00 .97@.02 1.00@.00 .98@.00 .95@.03 .84@.08 .67@.15 .55@.28 .04@.48
```

So: a near-full-width rock skirt at h .1–.3 (0.93–0.97 W); the clumps hold 0.86–0.90 W at h .4–.5 (ML and MR hang
over the side rocks); 0.77 at h .6; the crown narrows to 0.63 at .7 (MC plus sprout B), 0.52 at .8, 0.38 at .9 (MC's
crown and sprout B); the top 0.1 is sprout B alone.

**Shares per 0.1 h** (M / L / R in %):

```
front  .0 R100 | .1 R100 | .2 M8 R91 | .3 M36 L8 R54 | .4 M59 L19 R20 | .5 M71 L12 R15 | .6 M89 L9 R1 | .7 M68 L30 R1 | .8 M63 L35 | .9 M7 L92
f34    .0 R100 | .1 R100 | .2 M7 R91 | .3 M37 L6 R55 | .4 M59 L19 R21 | .5 M71 L11 R16 | .6 M91 L6 R1 | .7 M71 L26 R1 | .8 M68 L31 | .9 M16 L83
rear   .0 R100 | .1 R99  | .2 M17 R82 | .3 M43 L15 R41 | .4 M56 L19 R23 | .5 M70 L24 R4 | .6 M77 L21 | .7 M64 L34 | .8 M46 L51 R1 | .9 L98
side   .0 R100 | .1 R100 | .2 M8 R91 | .3 M32 L24 R42 | .4 M54 L19 R25 | .5 M75 L19 R4 | .6 M75 L23 | .7 M55 L43 | .8 M33 L65 | .9 L99
r34    .0 R100 | .1 M1 R98 | .2 M15 R84 | .3 M35 L16 R48 | .4 M62 L13 R24 | .5 M69 L15 R15 | .6 M80 L19 | .7 M70 L29 | .8 M44 L55 | .9 M3 L96
top    .0 R100 | .1 R100 | .2 M28 L12 R58 | .3 M55 L17 R26 | .4 M66 L19 R13 | .5 M82 L4 R12 | .6 M66 L8 R24 | .7 M17 L25 R57 | .8 M1 L35 R63 | .9 L21 R78
```

**Shares per third of the width** (M / L / R): front left 50 / 0 / 50, middle 34 / 15 / 51, right 38 / 16 / 45; f34
50 / 0 / 50, 35 / 13 / 51, 40 / 14 / 45; rear 56 / 0 / 44, 33 / 24 / 43, 33 / 17 / 51; side 60 / 0 / 40, 33 / 23 /
44, 15 / 29 / 56; r34 22 / 13 / 65, 58 / 8 / 34, 27 / 24 / 49.

**Each piece in the front** (read on `g_front.png` / `g_f34.png`; f across, h up, fractions of the silhouette bbox;
X and z from the §1.1 mappings):

| Piece | f extent | h extent | X (studs) | z (studs) | Notes |
| --- | --- | --- | --- | --- | --- |
| ML (left clump) | .07–.42 | .24–.74 | −2.75 … −0.51 | 0.80 … 2.85 | top at f .27; its long axis slopes down to the left over the left side rock; lower-right edge buried in the base's shoulder along (f .16, h .24) → (.33, .43) → (.42, .50) |
| MC (centre clump) | .30–.65 | .62–.92 (bottom hidden) | −1.28 … +0.96 | ≈ 2.2 … 3.44 | broad flat crown across f .40–.52; bottom hidden behind the front hump and sprout A |
| MR (right clump) | .60–.91 | .25–.69 | +0.64 … +2.62 | 0.84 … 2.62 | top at f .68–.75; its lowest point (f .82, h .25) hangs in front of the right side rock |
| Sprout A | .34–.56 (base f .47) | .30–.68 | −1.02 … +0.38 | 1.15 … 2.84 | four blades from one point in a notch low on the base's front face |
| Sprout B | .62–.88 (base f .72) | .70–1.0 | +0.77 … +2.43 | 2.55 … 3.85 | the tallest blade's tip at f .78; one long blade flares right to f .87, h .80 |
| Rock Base front face | .17–.86 | 0–.60 | −2.1 … +2.3 | 0 … 2.3 | front hump top h .60 at f .45–.55 (behind sprout A); front-left shoulder h .42–.45 at f .30–.35 |
| Side rock L | .00–.17 | .03–.40 | −3.2 … −2.1 | 0 … 1.3 | under ML's outer end |
| Side rock R | .82–1.0 | .05–.53 | +2.05 … +3.2 | 0 … 1.9 | under MR; taller than the left one |
| Pebble FL | .08–.24 | .01–.20 | −2.69 … −1.66 | 0 … 0.79 | separate, crease all round |
| Pebble FR | .70–.87 | .00–.24 | +1.28 … +2.37 | 0 … 0.97 | separate, crease all round |

- **Visible clump W : H** (front, screen): ML 1.10 (0.35 W × 0.50 H), MC ≥ 1.81 (bottom hidden), MR 1.02.
- **Sprouts** (`comps.py`, lime components): front A f .327–.563, h .285–.670 (W : H 0.90 in pixels); B tall part
  f .616–.776, h .687–1.0 plus the right blade f .726–.871, h .676–.804. The f34 the same within .01.

### 1.3 Silhouette and composition per view

**Front (`g_front.png`; governs, with the f34).** Camera on the front axis, about 12° up. A low, wide mound (W : H
1.47): a near-full-width grey skirt in the bottom 30 %, the three moss clumps above, sprout B on top at the right.
- **Rock Base:** one big faceted boulder whose front face fills f .17–.86 below h .45–.60: a front hump (top h .60 at
  f .45–.55), a lower front-left shoulder (h .42 at f .32), a notch at f .45–.50 (h .30) where sprout A roots, and its
  right side rising under MR. Its facets are irregular triangles about 0.4–0.8 stud across (12–20 across the front
  face), with crisp edges.
- **Clumps:** ML at the left (f .07–.42), MC above the middle (f .30–.65), MR at the right (f .60–.91). Each a chunky
  rounded lump of broad facets (§1.4); dark creases where they meet each other and the rock. ML and MR overhang the
  side rocks; MC sits behind and above, its bottom hidden.
- **Sprouts:** A in the front notch (f .34–.56), B at the upper right (f .62–.88, h .70–1.0).
- **Small rocks:** the side rocks at both ends, the front pebbles at f .08–.24 and .70–.87, each a squat faceted dome
  with its own crease against the base.

**Front three-quarter (`g_f34.png`; the hero).** **Not a three-quarter: the front drawing again** at 1.80 × the
scale (profile mean |Δ| .014, every piece's f within .01, the same bottom outline; §3.1). Shares within 1.1 points of
the front.

**Rear three-quarter (`g_r34.png`).** The f34 composition **mirrored** with the moss reshuffled (§3.2): sprout B's
spray at the upper left (f .15–.45, h .63–1.0), a big near clump in the middle-left (f .19–.60, h .18–.70), a clump
behind it at the top right (f .43–.73, h .60–.91), a clump at the far right (f .73–.95, h .32–.68), the second sprout
at the right in front of that clump (f .69–.90, h .30–.71); below, two big boulders (f .07–.40 and .50–.83, tops
h .42), a pebble at the front centre (f .37–.53, h 0–.16) and small rocks at both ends. Its rock band reads as
separate boulders more than the front's one face does.

**Side (`g_side.png`).** **Drawn as the front composition again, narrower** (W : H 1.089; profile against the f34
.048, mirrored .098): the base's front with sprout A on its crown at the centre (f .45–.64), two clumps stacked at the
left (f .05–.50), sprout B tall at the centre top (f .45–.88), a strip of MR at the right (f .70–.91), pebbles at both
ends. It is not a view from +X or −X (§3.3).

**Rear (`g_rear.png`).** **The front composition again** (profile against the f34 .060, mirrored .097; W : H 1.196):
the base's front with sprout A in front, ML at the left, MC at the top, MR at the right with sprout B over it. Not a
rear view (§3.3).

**Top (`g_top.png`, `z_top.png`; image top = back).** A steep elevated view (≈ 70–80°): a rounded outline whose
upper (back) half is a ring of grey rock; **two** clumps (a big one at the left, f .06–.55, h .20–.85; one at the
right, f .55–.95, h .20–.72), sprout B at the upper right (f .56–.85, h .67–.97), sprout A at the lower middle
(f .31–.61, h .22–.55) on the base's front hump, pebbles at the bottom corners. **No centre clump**: grey rock where MC
should be (§3.4).

**Exploded (`expl.png`, `z_expl_*.png`) and close-ups (`cu.png`).** See §1.4.

### 1.4 Parts (Exploded Construction (16,700,640,1235), close-ups (650,735,1008,1470))

Facet language for every part: broad flat-shaded facets, chunky, crisp edges, no noise, no bevel chains, no smooth
shading ("Broad, flat-shaded faces. No smooth shading."; "even, readable facets").

Scale: the exploded parts are drawn about 1.5–1.9 × larger relative to the base than in the hero (the centre clump is
0.69 of the base's width there, 0.40 in the front). **The hero governs every size**; the exploded gives shapes and the
part list.

#### Moss clumps — Left (100,912,231,1024) 128 × 111 px; centre (232,862,402,971) 168 × 107; Right (405,920,536,1031) 111 × 109 (`z_expl_clumps.png`, `z_f34_clumps.png`)

- **Centre clump (MC):** a **broad squat dome** (W : H 1.57) with a near-flat underside and a **flat crown polygon**
  (0.30 of its width at the top, 4–5 sides). Width per height bottom → top `.05 .57 .76 .89 .97 .98 .90 .82 .73 .51
  .30`: widest at 0.4–0.5, flat-ish bottom (0.57 at 0.1), shoulders rounding to the crown.
- **Side clumps (ML, MR):** **tilted ovoid lumps** (W : H 1.15 and 1.02 as drawn, tilted about 25–30° along the slope
  they lie on), pointed-round at both ends: `.03 .39 .61 .77 .84 .87 .88 .85 .72 .52 .02` (left) and `.03 .37 .57 .70
  .86 .90 .89 .87 .76 .54 .05` (right). The centre line drifts .21 → .61 (left) and .69 → .32 (right) bottom → top:
  each lump's upper end leans toward the middle and its lower end hangs outward — they drape over the shoulders.
  ML and MR are the same shape mirrored.
- **Facets:** each clump shows **12–18 broad polygonal facets** on its visible side in the f34 zoom (`z_f34_clumps.png`),
  several split into 2–3 triangles of slightly different tone; facet size 0.35–0.8 stud on a 2.3-stud clump. A crown
  polygon on MC (one big near-flat face). **Not a ball, not an icosphere, not a soccer-ball pattern** (no regular
  pentagon/hexagon tiling; R07's subdivided spheres were flagged as rounder than the ref).
- **Construction:** `_clump(size, seed, rings, tilt)` via `K.hull_rock(..., keep_bottom=True)`:
  - MC rings `(0.0, 0.55, 7), (0.22, 0.90, 8), (0.48, 1.0, 8), (0.74, 0.82, 7), (0.92, 0.52, 5), (1.0, 0.30, 4)`
    (the last ring all at h 1.0 makes the flat crown polygon), jitter 0.10: about 39 points → **about 70 tris**;
  - ML / MR rings `(0.0, 0.42, 6), (0.18, 0.84, 8), (0.45, 1.0, 8), (0.72, 0.88, 7), (0.90, 0.52, 5), (1.0, 0.18, 3)`,
    jitter 0.10, `tilt` about 25° about Y (ML's top toward +X, MR's toward −X), `lean` 0.1 toward the middle: about
    37 points → **about 66 tris**.
  - Then, if any face is larger than about 0.9 stud across, poke it with the centre raised 2 % of the radius (M019 /
    M023 within-face facets) — never more than 6 per clump.
  - Valence 4–7; if the hull comes out as even pentagons/hexagons, raise the angular jitter (the 023 round-1 fix).

#### Sprouts A, B, C — A (164,768,252,865) 71 × 95 px; B (283,730,370,824) 83 × 94; C (386,782,478,873) 67 × 90 (`z_expl_sprouts.png`; close-up 1)

- **Shape:** a fan of **3–5 pointed, chunky blades** from one point: one tall central blade, two side blades flaring
  30–60°, often a shorter back blade. Each blade is a **faceted lanceolate prism**: narrow at the base, widest at about
  0.55 of its length (width ≈ 0.28 of the length), a pointed tip, a **diamond cross-section with a midrib ridge** (two
  facets per side, thickness ≈ 0.4 × the width), slightly cupped. Not flat cards, not cones.
- Width per height bottom → top (exploded, whole sprout): A `.04 .46 .58 .70 .82 .93 .65 .68 .34 .21 .03`, B `.07 .41
  .52 .64 .78 .90 .60 .64 .27 .20 .07`, C `.01 .45 .57 .69 .82 .94 .76 .33 .30 .15 .01`: the fan is widest at 0.5 of
  its height, where the side blades end, and the central blade carries the top.
- **Close-up 1:** "Leaf blades join at base": the blades merge into one stub at the base, set into the moss.
- **Hero:** two sprouts. A: 4 blades (centre 1.65 tall, a long left blade to f .34 / h .55, a right blade to f .56 /
  h .50, a short back blade). B: 4–5 blades (the tall blade 1.4 leaning 15° right, a left blade to f .62 / h .92, a
  long right blade flaring about 65° to f .87 / h .80, a short back blade). The exploded's third sprout (C) is not in
  any assembled view (decision §8.3).
- **Construction:** `_blade(L, w, seed)`: 5 cross-sections along the blade (t 0, 0.2, 0.55, 0.85, tip) with 4 vertices
  each (the diamond: left edge, top ridge, right edge, under ridge), widths `0.35 0.8 1.0 0.55 0` × w, a slight
  forward curl; **about 24 tris** per blade, closed. `_sprout(blades, seed)` puts 4–5 blades round one base point,
  their bases overlapping 0.05 inside a small 6-sided stub (Ø 0.22 × 0.15) so the fan is one closed piece: **about
  100–130 tris**.

#### Rock Base — exploded (186,1037,432,1190) 246 × 153 px (`z_expl_base.png`); close-ups 2 and 3

- **Shape:** **one** broad, low, faceted boulder: a **higher back hump** (the exploded's top at y 1037, x 300–380), a
  **lower front lobe** (top about 0.68 of the hump's height) with a shallow notch near its middle, a front-left
  shoulder lower again, and a flat bottom. About 40–60 irregular triangular facets 0.4–0.9 stud across. It reads as
  **one form**, not a pile: the lobes are swells of one surface with shallow creases, not separate domes.
- **Hero:** 4.9 W × 3.9 D; the front hump top z 2.3, the front-left shoulder z 1.6, the back hump z 2.5 (under MC),
  the right flank z 1.9; h/w about 0.5.
- **Underside (close-up 3):** "Flat base surface for placement": one broad flat face; the outline is two lobes with a
  shallow crease between them; the rim is a short band of facets rising from the flat.
- **Rock to moss (close-up 2):** "Moss clump sits on rock": the clump rests directly on the rock, its lower edge
  tucked into the rock's facets with a dark crease, no gap and no lip; small rocks stand at the foot.
- **Construction:** `_base_rock(seed)`: **one non-convex ring mesh** (not a union of domes): 12 sectors × rings
  `(0.0, 0.94), (0.10, 1.0), (0.45, 0.93), (0.75, 0.70), (0.92, 0.38)` plus a 5-point crown, where each sector's
  radius and each ring's height are scaled by a lobe field: back hump (az 75–120°, height × 1.0), front lobe (az
  250–300°, × 0.92), front-left shoulder (az 200–245°, × 0.64), right flank (az 330–30°, × 0.76); the notch for sprout
  A is a 0.18-deep dent at az 268°, z 1.1–1.4. Beauty-triangulate, a few flipped diagonals by seed, ±5 % jitter. A flat
  bottom fan. **About 150–190 tris.**

#### Small rocks (×6) — side L (50,1090,128,1157) 78 × 63 px; Side Rock (R) (507,1095,578,1152) 69 × 54; front-left (133,1120,212,1184) 79 × 63; front-right (423,1104,497,1182) 74 × 76; back-left (150,1053,202,1094) 51 × 40; back-right (435,1055,485,1092) 48 × 35

- **Shape:** squat faceted domes, flat bottoms, screen W : H 1.0–1.37 (true h/w 0.65–0.9), 14–20 facets each, a small
  top cluster of faces. The "side rocks" carry dashed double arrows: they nest against the base's left and right
  flanks; the back pair sit high on the page (= further back) behind the base's shoulders.
- **Construction:** `_rock(w, d, h, seed)` via `K.hull_rock(..., keep_bottom=True)`, rings `(0.0, 0.92, 7), (0.4, 1.0,
  7), (0.78, 0.70, 6), (1.0, 0.25, 3)`, jitter 0.12: **about 40 tris** each.

#### Not modelled

- No pegs, sockets or holes anywhere (the exploded has none; the dashed arrows are layout notation).

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, origin = the bbox bottom centre). Azimuths are measured from +X
counter-clockwise (front = 270°, back = 90°). "Tilt" is a rotation about the Y axis (positive tips the top toward
+X).

### 2.1 Rock Base and small rocks

| Rock | Centre (x, y) | w × d × h | Sheet evidence | Seat |
| --- | --- | --- | --- | --- |
| RB base | (+0.05, +0.20) | 4.9 × 3.9 × 2.5 (front hump 2.3 at (0, −0.3); front-left shoulder 1.6 at (−1.2, −0.7); back hump 2.5 at (−0.1, +1.0); right flank 1.9 at (+1.4, +0.2)) | front face f .17–.86, hump h .60, shoulder h .42; exploded base | flat bottom on the ground |
| SL side left | (−2.60, +0.15) | 1.25 × 1.30 × 1.30 | front f .00–.17, top h .40 (z 1.3) | against RB's left flank, overlap 0.2 |
| SR side right | (+2.60, +0.25) | 1.30 × 1.30 × 1.85 | front f .82–1.0, top h .53 (z 1.9) | against RB's right flank, overlap 0.2 |
| PL front-left | (−2.15, −1.75) | 1.00 × 0.90 × 0.80 | front f .08–.24, top h .20 | in front of SL and RB, overlap 0.1 |
| PR front-right | (+1.80, −1.80) | 1.10 × 1.00 × 0.97 | front f .70–.87, top h .24 | in front of RB's right, overlap 0.1 |
| BL back-left | (−1.50, +2.00) | 0.85 × 0.80 × 0.70 | exploded back-left; top-view rock ring | behind RB's left, overlap 0.15 |
| BR back-right | (+1.40, +2.05) | 0.80 × 0.75 × 0.65 | exploded back-right; top-view rock ring | behind RB's right, overlap 0.15 |

- **Embedding:** small rocks overlap the base or a neighbour by 0.1–0.2 (never coplanar), flat bottoms at z 0.02–0.05
  before the floor cut, each yawed by its own seed. **Each small rock keeps a visible crease where it meets the base**
  (it is a separate rock, not a swell of the base).
- **Expected rocks:** X −3.23 … +3.25, Y −2.20 … +2.43.

### 2.2 Moss clumps

| Clump | Centre (x, y, z) | Size (along its axis × d × thickness) | Tilt | Sheet evidence |
| --- | --- | --- | --- | --- |
| ML | (−1.62, −0.15, 1.85) | 2.35 × 2.10 × 1.75 | +25° (top toward +X, lower end hanging out over SL) | front f .07–.42 (X −2.75 … −0.51), h .24–.74 (z 0.80–2.85) |
| MC | (−0.15, +0.95, 2.70) | 2.35 × 2.00 × 1.50 | 0°, yaw 10° | front f .30–.65 (X −1.28 … +0.96), crown h .92 (z 3.44); bottom sunk into the back hump (z ≈ 1.95) |
| MR | (+1.62, −0.20, 1.75) | 2.10 × 1.95 × 1.70 | −25° (top toward −X, lower end hanging out over SR) | front f .60–.91 (X +0.64 … +2.62), h .25–.69 (z 0.84–2.62) |

- **Contact:** each clump's underside sinks 0.15–0.30 into the rock below it (RB's shoulders and hump, SL / SR), so a
  dark crease, not a gap, shows at every moss–rock edge (close-up 2). ML and MR touch MC with a crease (overlap
  0.1–0.2).
- **Expected:** MC's crown polygon at z 3.40–3.48, normal within 15° of +Z; ML and MR crowns at z 2.8 and 2.6; the
  clumps' outer ends overhang SL and SR by 0.2–0.4 in the front view.

### 2.3 Sprouts

| Sprout | Base (x, y, z) | Blades (length, angle from vertical, toward) | Tip z | Sheet evidence |
| --- | --- | --- | --- | --- |
| A | (−0.19, −1.35, 1.15), in RB's front notch | centre 1.65 (5°, forward); left 1.35 (40°, az 200°); right 1.05 (35°, az 340°); back 1.1 (25°, az 100°) | 2.8 | front f .34–.56, base (f .47, h .30), tips (f .34, h .55), (f .48, h .68), (f .56, h .50) |
| B | (+1.40, +0.50, 2.50), in the crease between MC and MR | tall 1.40 (15°, az 0°); left 1.20 (32°, az 160°); right 1.10 (65°, az 345°); back 0.8 (30°, az 95°) | 3.85 | front f .62–.88, base (f .72, h .70), tips (f .78, h .99), (f .62, h .92), (f .87, h .80) |

- Each sprout's stub sinks 0.10–0.15 into the rock (A) or the moss (B); the blade bases overlap inside the stub.
- **Expected hero:** X −3.23 … +3.25 (SL, SR), Y −2.20 … +2.43 (PL / PR, BL / BR), z 0 … 3.85 (sprout B's tip) →
  **6.45 × 4.63 × 3.85** (inside 6.4 ±0.3 × 4.75 ±0.35 × 3.9 ±0.2).

### 2.4 Checks on the renders

- **front_sheet (0, 12)** against the front cell, and the same render against the f34 cell (§3.1):
  - W : H 1.40–1.54 (sheet 1.469 / 1.491);
  - shares ±4 of M 39.9 / L 11.3 / R 48.8 (f34 40.7 / 10.2 / 49.1); green 47–55 %;
  - the piece table in §1.2 ±0.05 per extent;
  - top profile mean |Δ| ≤ 0.05, max ≤ 0.12 (sprout tips may miss by 0.15 at one column);
  - width per height ±0.07 at every h;
  - shares per 0.1 h ±12 per class; h .0–.2 at least 90 % rock; h .6–.7 at least 85 % green;
  - rock band top (ground-connected) ±0.07 per column.
- **r34:** the front_sheet render **flipped left–right** against the r34 cell (§3.2): profile mean |Δ| ≤ 0.08, shares
  ±5 of 39.2 / 13.9 / 46.9.
- **side_sheet (90, 12), true +X side (screen right = +Y, the back):** D : H 1.05–1.25 (sheet 1.089 is a narrowed
  front redraw, §3.3; ours: D 4.63 over a screen height of about 3.77 + 1.46 × 0.208 = 4.07 → about 1.14); green 45–60 %, rock 40–55 %; MR
  nearest at the centre with SR in front of its foot, MC behind it at screen right, sprout B at the centre-right top,
  sprout A low at screen left. Judge it by these, not the sheet's piece positions.
- **rear_sheet (180, 12):** green 45–65 %, rock 35–55 %; MC nearest in the middle, ML at screen right, MR at screen
  left, sprout B at the upper left, BL / BR in front at the foot; the moss holds the upper half (h ≥ .5 at least 80 %
  green). The rear cell is a front redraw (§3.3); judge it by shares, W : H 1.40–1.65 (ours about 1.55: the sheet's 1.196
  is the narrowed redraw) and the width per height of the rock skirt (≥ 0.90 W at h .1–.3).
- **top_sheet (0, 75), image top = back:** green 45–62 %, rock 38–55 %; rock visible all round the rim, sprout B at
  the upper right, sprout A at the front centre; three clumps (the sheet draws two, §3.4).

## 3. View conflicts and resolutions

### 3.1 The front three-quarter is the front drawing

- **Evidence.** The f34's top profile matches the front's within mean .014 (max .14 at the sprout tip); every piece's
  f is the same within .01; the bottom outline is identical (.13 at both ends). A real front three-quarter would
  narrow the mound and move the clumps.
- **Resolution.** Compare **both** the front and the f34 cells with one **front_sheet (0, 12)** render. The kit
  front34 (−28, 12) is self-consistency only.

### 3.2 The rear three-quarter is the f34 mirrored

- **Evidence.** The r34's top profile matches the f34's **mirrored** within mean .053 (direct .088); its sprout spray
  is at the upper left where the mirrored f34 puts sprout B (f .12–.38), its far-right clump where the mirrored ML
  falls, its top-right clump where the mirrored MC falls. Shares within 3.7 points of the f34. A true rear camera on
  the front views' layout would put MC nearest and sprout A out of sight.
- **Resolution.** Compare the r34 cell with the **front_sheet render flipped** (profile ≤ 0.08, shares ±5). The kit
  rear34 (152, 12) is self-consistency: it must show MC's back, the base's back hump and BL / BR, and no bare holes.

### 3.3 Side and rear cells are front redraws

- **Evidence.** Both show the base's bare front face with sprout A facing the camera, ML at the left and MR at the
  right, sprout B at the top right — the front composition, not mirrored (profiles against the f34 .048 and .060,
  mirrored .098 and .097), only narrower (side W : H 1.089, rear 1.196). From +X the base's front would be at screen
  left and MR nearest; from the back, MC would be nearest and sprout A hidden.
- **Resolution.** Keep the layout the front views give. Take the **depth** from the side cell's width at the front's
  scale (D 4.75, §1.1). Judge side_sheet and rear_sheet by shares, widths and the expected arrangement in §2.4, not by
  the sheet's piece positions. Record "side and rear drawn as front views" as a known miss.

### 3.4 Top: a steep elevated view with only two clumps

- **Evidence.** The top cell shows the base's front hump and sprout A at the bottom (a camera ≈ 70–80° up, image top =
  back), a big clump at the left, a clump at the right, sprout B at the upper right, and **grey rock across the upper
  middle where MC should be**. The front, f34, side, rear and r34 all show three clumps with the centre one highest.
- **Resolution.** The hero governs: three clumps. Judge the kit top (and a `top_sheet (0, 75)`) by shares (green 45–62
  %, rock 38–55 %), rock round the back rim, and the two sprouts' places. Our top will show MC at the upper middle;
  record "top drawn without the centre clump" as a known miss.

### 3.5 Exploded against hero

- **Three sprouts against two.** The exploded draws Sprout A, B and C in a row above the three clumps; every assembled
  view (front, f34, side, rear, r34, top) shows two: one in the base's front notch and one at the back-right. **The
  hero governs** (decision §8.3): two sprouts; the Sprout part is one of the three shapes.
- **Sizes.** The exploded parts are 1.5–1.9 × larger relative to the base; the exploded base is W : H 1.58 seen from
  above, so its top shows; the hero base is h/w about 0.5. Hero sizes govern.
- **Six small rocks.** The exploded's six (side L and R, front L and R, back L and R) are the hero's SL, SR, PL, PR,
  BL, BR (§2.1).

### 3.6 Moss Light swatch is the sprout colour

- **Evidence.** "Moss Light" `#A5BC38` (70°, 0.70, 0.74) equals the rendered sprout medians (`#A3B92D`–`#AABF35`); no
  moss clump region reaches it (clump lit quartiles `#89A72A`–`#92AE2E`, crowns `#95B038`).
- **Resolution.** The sprouts take a `sprout` key calibrated to the rendered sprouts; the clumps take `moss` (Moss Mid)
  and `moss_dark` (Moss Dark). Never paint the clump tops with the sprout colour.

### 3.7 Rock swatches are lit and mid tones of one rock

- **Evidence.** "Rock Light" `#BCB0AA` matches the rendered rocks' lit quartile (`#B0A3A0`–`#B7ABA8`; the exploded
  base hump `#B3A7A6`), "Rock Mid" `#988E8C` the hero medians (`#877C7D`–`#928784`) and the exploded rocks (`#9B8D8A`–
  `#A39692`). The pebbles, side rocks and base read the same in the exploded (within 8 levels).
- **Resolution.** One `rock` key calibrated to the exploded (unshadowed) rocks, plus a `rock_low` key for the ground
  band and the moss contact (paint by height and by distance to moss, never by facing). Not two rock families.

### 3.8 Effects

- No glow (glow share 0 %), no light, no spores, dust or sparkle, no VFX callout. WorldModeling §9: cave moss gets
  its visibility "from shape and placed lighting, not automatic emission". Stages 5 and 6 add nothing by default (§7).

## 4. Construction plan (modeller, stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `clump_centre()` → `MossBoulderClump`: MC on its own (§1.4). Compare with the exploded centre clump
     (`z_expl_clumps.png`) from about (0, 20): W : H 1.45–1.70, width per height ±0.08, a flat crown polygon (4–5
     sides, normal z > 0.95, area ≥ 0.25 sq studs), 12–18 broad faces visible.
   - `clump_side()` → `MossBoulderClumpSide`: ML's shape, untilted, flat-bottomed. Compare with the exploded left
     clump rotated by its tilt: width per height ±0.08.
   - `sprout()` → `MossBoulderSprout`: sprout B's fan (4–5 blades). Compare with the exploded Sprout B: W : H 0.8–0.95,
     width per height ±0.1, blades with a midrib ridge and a pointed tip.
   - `base()` → `MossBoulderBase`: RB alone, floor-cut. Compare with the exploded base from about (0, 25): the back
     hump higher than the front lobe, one continuous surface, 40–60 irregular facets, a flat bottom.
   - `side_rock()` → `MossBoulderSideRock`: SR's rock alone. Compare with the exploded Side Rock (R): W : H 1.15–1.4 as
     drawn, 14–20 facets.
   - Render a parts shot (`extra`, about (−20, 20)) laid out like the exploded.
2. **Hero:** `_paste` (m011 pattern) RB, the 6 small rocks, the 3 clumps and the 2 sprouts (§2); unite into one closed
   shell **one piece at a time**, saving the work file between risky steps: RB first, then the small rocks
   (`union_loose` then one exact union), then MC, ML, MR, then sprout A, sprout B; `m004.floor_cut` at z 0. Origin at
   the bbox bottom centre; transforms applied. If an exact union with a sprout fails or leaves slivers that `_tidy` /
   `_desliver` can't clear, keep that sprout as a separate closed shell inside the same object (decision §8.6).
3. **Budget** (§4.3): hero about 1100–1600 (limit 4000); parts ≤ 1000 each.
4. **Placeholder keys** (stage 1): `m033_moss`, `m033_sprout`, `m033_rock`. Stage 4 adds the rest (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** one broad faceted grey boulder capped by three chunky moss clumps, the front face bare with a
      sprout in its notch, a taller sprout at the back-right, small rocks round the foot. Not a rock pile, not green
      balls on a plate.
   2. **front_sheet (0, 12)** against the front and f34 cells: §2.4, every line.
   3. **Clumps are faceted lumps, not balls:**
      - MC W : H (true) 1.50–1.65; ML / MR length : thickness 1.25–1.45 along their tilted axes;
      - each clump 55–95 tris, 12–18 distinct faces visible from the front, the largest ≥ 0.5 stud across; MC's crown
        polygon present;
      - vertex valence 4–7; **no soccer-ball pattern** (no region of near-equal pentagons and hexagons; 023's round-1
        failure);
      - the bottom ring 0.42–0.60 of the max width, sunk into the rock.
   4. **Base reads as one form with separate rocks:**
      - RB is one mesh with lobes (not a union of domes); on the front render it covers at least 70 % of the rock
        pixels, and its front face spans f .17–.86;
      - each of the 6 small rocks shows a crease all round where it meets RB or the ground, none wider than 0.2 W, none
        topping above h .53 in the front;
      - the rock band per column within ±0.07 of §1.2's.
   5. **Sprouts:** A rooted at h .27–.33 in the front with its tips at the §1.2 positions ±0.05; B's tall tip is the
      bbox top at f .75–.81; blades are closed diamond-section prisms (not flat cards), 3–5 per sprout.
   6. **Rear, side, top, r34:** §2.4 and §3.
   7. **Kit views** (front34, rear34, underside): self-consistency; the underside shows one flat floor-cut face
      (close-up 3). **Hero size** 6.4 × 4.75 × 3.9 (±0.3 / ±0.35 / ±0.2).
6. **Stage 2:**
   - zero non-manifold, boundary, wire and loose elements; no zero-area faces or n-gons; normals outward; 0 bowtie
     vertices (`M.audit` `nonmanifold_verts`; the sprout stubs and blade tips and MC's crown polygon are the risk);
   - no faces under 5° where clumps meet rock and sprouts meet their seats (m011 `_tidy` / `_desliver`);
   - don't decimate the clumps below 6 sectors and 5 rings, the blades below 4 cross-sections, RB below 10 sectors or
     the small rocks below 6 sides.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Rock Base (12 sectors, 5 rings, crown) | 1 | 170 | 170 |
| Small rocks | 6 | 40 | 240 |
| MC | 1 | 70 | 70 |
| ML, MR | 2 | 66 | 132 |
| Sprouts (4–5 blades × 24 + stub) | 2 | 110 | 220 |
| **Sum before union** | | | **about 830** |
| **Hero after union** (seams, slivers, floor cut) | | | **about 1100–1600** (limit 4000) |
| Parts: Clump / ClumpSide / Sprout / Base / SideRock | | | about 70 / 66 / 120 / 175 / 40 (limit 1000) |

## 5. Colour plan (modeller, stage 4)

### 5.1 Swatches (flat; medians of a 35 × 16 box inside each, x 45–80)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Moss Dark | (35,1281,86,1311) | `#5F7924` | 78°, 0.70, 0.47 |
| Moss Mid | (35,1317,86,1347) | `#718E27` | 77°, 0.73, 0.56 |
| Moss Light | (35,1353,86,1383) | `#A5BC38` | 70°, 0.70, 0.74 |
| Rock Light | (35,1390,86,1420) | `#BCB0AA` | 20°, 0.10, 0.74 |
| Rock Mid | (35,1426,86,1457) | `#988E8C` | 10°, 0.08, 0.60 |

- **Moss Mid** matches the rendered clump medians (`#6A8922`–`#73921F`) within 8 levels.
- **Moss Dark** matches the clumps' bottom fifths (`#526D1A`–`#5A7619`) and the shaded left clump (`#5C7C21`).
- **Moss Light** is the sprouts' colour (§3.6).
- **Rock Light / Rock Mid** are the rock's lit and mid tones (§3.7).

### 5.2 Rendered regions (`samp.py`, `grad.py`; median / lit quartile / shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Moss, f34 / r34 / front / side / rear / top | V | M | `#6A8922` / `#68891F` / `#6F8E22` / `#698820` / `#688822` / `#6D8D1F` | `#89A72A` / `#8CAA29` / `#8DAA2D` / `#81A125` / `#86A527` / `#89A727` | `#425A15` / `#496216` / `#435B17` / `#425A15` / `#425B15` / `#4A6217` |
| Sprouts, f34 / r34 / front / side / rear / top | V | L | `#A7BD34` / `#A6BD30` / `#A5BA38` / `#A3B731` / `#A9BE35` / `#A3B834` | `#CEDD55` / `#CDDA52` / `#CEDC57` / `#CBDA54` / `#CEDC59` / `#CCDC52` | `#738B15` / `#6E8914` / `#718915` / `#728B16` / `#758E15` / `#6F8518` |
| Rock, f34 / r34 / front / side / rear / top | V | R | `#877C7D` / `#908584` / `#8A7F7F` / `#887D7C` / `#8D817E` / `#928784` | `#B0A3A0` / `#AEA19F` / `#B2A6A2` / `#ADA09C` / `#B0A3A0` / `#B7ABA8` | `#6D6666` / `#6E6767` / `#706968` / `#6E6768` / `#6F696A` / `#696361` |
| ML / MC / MR, f34 | (70,200,215,340) / (180,125,330,200) / (330,225,465,350) | M | `#5C7C21` / `#7D9C28` / `#6F8E21` | `#809F27` / `#92AF2C` / `#92AE2E` | `#3E5615` / `#5C7B23` / `#465F16` |
| MC crown, f34 | (210,118,300,150) | M | `#95B038` | `#98B33E` | `#86A32F` |
| Exploded clump L / C / R | §1.4 boxes | G | `#6B8B20` / `#6E8E20` / `#73921F` | `#87A62A` / `#8DAB28` / `#96B12D` | `#53701A` / `#4B6719` / `#56721A` |
| Sprout A / B, f34 | (235,215,295,330) / (330,105,450,215) | L | `#A3B92D` / `#AABF35` | `#C3D34D` / `#CCDB55` | `#748A15` / `#6F8914` |
| Exploded sprout A / B / C | §1.4 boxes | G | `#9DB42E` / `#A1B732` / `#A2B92D` | `#C1D14A` / `#C7D754` / `#C6D64E` | `#789119` / `#7B951B` / `#77901A` |
| Base front lobe / base left, f34 | (260,290,380,400) / (120,300,240,400) | R | `#988A87` / `#7E7576` | `#B2A6A2` / `#9A8F90` | `#827772` / `#6A6465` |
| Pebble FL / FR, f34 | (50,370,130,425) / (345,345,445,425) | R | `#847C7E` / `#8C7F7D` | `#B1A7A6` / `#AFA2A0` | `#615B5D` / `#615B58` |
| Side rock R / L, f34 | (440,290,505,395) / (35,300,85,390) | R | `#988A85` / `#6F6A6E` | `#B6A8A4` / `#B7B1B1` | `#796E6A` / `#605B5D` |
| Exploded rock base / hump lit area | (200,1040,430,1188) / (300,1040,400,1090) | R | `#A19492` / `#B3A7A6` | `#B7ABAB` / `#C0B4B2` | `#807775` / `#A79B9A` |
| Exploded pebbles FL / FR, side L / R, back L / R | §1.4 boxes | R | `#A09493` / `#A39692`, `#9C8F8D` / `#9B8D8A`, `#857D7E` / `#948887` | `#BCB0AD` / `#BBAFAC`, `#B6AAA8` / `#B9ADAC`, `#AC9F9D` / `#BAADA9` | `#7C7475` / `#786F70`, `#77706E` / `#706969`, `#665F5E` / `#6A615E` |
| r34 near clump / big rock right / big rock left | (620,240,800,370) / (800,330,920,420) / (570,320,720,420) | M / R / R | `#5E7E1D` / `#9E908B` / `#867A7B` | `#82A324` / `#AC9E9C` / `#A49897` | `#405915` / `#857A76` / `#6D6666` |
| Close-up 1 sprout / moss | (760,760,1005,950) / (655,780,760,950) | L / M | `#A8BD31` / `#7F9E24` | `#C8D84E` / `#94B033` | `#708B15` / `#587518` |
| Close-up 2 moss / rock | (720,990,870,1100) / (655,990,880,1185) | M / R | `#66841C` / `#998B87` | `#86A322` / `#B5A8A7` | `#476014` / `#7B6F6B` |
| Close-up 3 flat underside / rim | (700,1300,900,1440) / (700,1250,1000,1300) | R | `#81746F` / `#A79B9A` | `#837771` / `#C4B8B4` | `#7E726C` / `#81756F` |

**Gradients along a part** (medians in five equal steps, bottom → top; `grad.py`):

```
clump L   exploded #526D1A #5A771A #6C8C1F #82A026 #8BA82F   lit q. #5A761F #61801B #81A123 #87A625 #92AE39
clump C   exploded #516C19 #5A7819 #739220 #7B9B26 #90AB33   lit q. #5A7819 #6C8A1C #8BAA26 #8EAC28 #9BB639
clump R   exploded #5A7619 #6B891D #76961F #7B9A22 #8AA82E   lit q. #627F1A #78981F #86A325 #98B42F #9AB432
ML        f34      #3C5415 #48631B #5B7A20 #799A26 #7D9D28
MR        f34      #455D15 #57731A #6F8D21 #769523 #8DAA2A
sprout A  exploded #7E9A1C #8FA724 #A1B730 #B4C73D #CDDA55   lit q. #96AF1F #ABBF2F #C1D147 #C7D550 #D2E05B
sprout B  exploded #829B20 #8DA626 #B3C539 #B6C83E #C7D957   lit q. #93AB22 #AEC138 #C9D854 #CFDE5B #D2E05D
rock base exploded #8D807C #928685 #ADA19E #B0A4A3 #B5A9A8   lit q. #958A89 #A79996 #B9ADAD #B7ABAA #C0B5B3
front lobe f34     #7C706C #857A79 #968985 #9C8F8C #B1A4A1
```

Deciles (dark → light), f34: moss `#324A10 #455F15 #506B16 #5C7A16 #68841C #6E8E21 #769624 #7D9D23 #85A52B #92B131`;
rock `#5A5659 #736968 #7C7271 #7F7677 #867874 #908382 #9A8B87 #9C9497 #ACA09D #B8ABA7`.

### 5.3 How the colour works

**Moss clumps.**
- One saturated moss green, hue 76–79°, sat 0.74–0.79 in every view and part. The unshadowed medians agree within 10
  levels (`#6A8922`–`#73921F`; swatch Moss Mid `#718E27`).
- **Darker at the bottom, lighter at the top.** Even the lit quartile runs `#5A761F` → `#92AE39` bottom → top on the
  isolated exploded clumps. Mostly light (top facets lit, undersides shaded), plus a painted **dark band**: the swatch
  "Moss Dark" and the bottom fifths (`#526D1A`–`#5A7619`) are the same colour. Paint the lowest 30 % of each clump (by
  its own height) toward `moss_dark`, blending out by 0.5; never by facing.
- The left clump's darker median (`#5C7C21`) and MC's lighter one (`#7D9C28`) are light (ML faces away from the key;
  MC's crown faces up). All three clumps share one key.
- No spots, no stripes, no lime patches on the clumps.

**Sprouts.**
- One bright lime, hue 69–70°, sat 0.72–0.76; medians `#A1B732`–`#AABF35` (swatch Moss Light `#A5BC38`); lit facets
  `#CEDD55`. Clearly yellower (7–9° of hue) and 40–60 levels brighter than the moss.
- **Darker at the blade bases** (bottom fifths `#7E9A1C`–`#829B20`, lit quartile `#93AB22`–`#96AF1F`): the bases sit in
  the other blades' shade, plus a gentle painted base band (lowest 25 % of each blade toward `sprout_base`).

**Rock.**
- One warm pink-grey family, hue 0–16° (a few faces 350–355°), sat 0.07–0.12; unshadowed exploded median `#A19492`,
  lit `#B3A7A6`–`#BCB0AD`, hero median `#877C7D`–`#928784` (the hero rocks sit under the moss and catch less light).
- A darker ground band (exploded base bottom fifths `#8D807C`–`#928685` against `#B0A4A3` above; swatch Rock Mid
  `#988E8C`): light plus a gentle painted band (lowest 20 % of each rock toward `rock_low`).
- A darker **moss contact** (the rock under ML, `#7E7576`; the side rock under ML `#6F6A6E`): mostly the clumps'
  shadow; paint only a light 25 % `rock_low` on faces within 0.25 of a clump.
- Pebbles and side rocks use the same key as the base (§3.7), each with its own tint.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered medians of **unshadowed** regions (the isolated exploded parts, the MC crown, the lit
front lobe), not swatches and not the shaded hero medians. `K.sample` kinds: `"green"` for the moss and sprout keys
(both pass `g > r + 8`, `g > b + 25`, sat > 0.3 — so sample them from separate boxes: the exploded clumps alone, the
exploded sprouts alone); `"stone"` for the rocks (sat < 0.18; check the filter keeps the warm hue).

| Key | Calibration target | Saturation target | Where | Finish |
| --- | --- | --- | --- | --- |
| `m033_moss` | `#6E8E20` (exploded clumps `#6B8B20` / `#6E8E20` / `#73921F`; front `#6F8E22`; swatch Moss Mid `#718E27`) | 0.74–0.79, hue 76–79° | every clump | rough 0.9, `low_spec=True` (`FOLIAGE_SPEC`) |
| `m033_moss_dark` | `#58741A` (exploded bottom fifths `#526D1A` / `#5A771A` / `#5A7619`; swatch Moss Dark `#5F7924`) | 0.72–0.78, hue 76–80° | the lowest 30 % of each clump at 55 %, blending out by 0.5 | rough 0.9, low_spec |
| `m033_sprout` | `#A1B732` (exploded sprouts `#9DB42E` / `#A1B732` / `#A2B92D`; f34 `#A3B92D` / `#AABF35`; swatch Moss Light `#A5BC38`) | 0.70–0.76, hue 68–71° | every blade | rough 0.75, low_spec |
| `m033_sprout_base` | `#809A1E` (exploded blade bottom fifths `#7E9A1C` / `#829B20`) | 0.75–0.82, hue 70–74° | the lowest 25 % of each blade and the stub, at 50 % | rough 0.75, low_spec |
| `m033_rock` | `#A19492` (exploded base `#A19492`, pebbles `#A09493` / `#A39692`, side rocks `#9C8F8D` / `#9B8D8A`; swatch Rock Mid `#988E8C`, Rock Light `#BCB0AA` as the lit target) | 0.07–0.11, hue 0–16° | every rock | rough 0.92 |
| `m033_rock_low` | `#8A7E7B` (exploded base bottom fifth `#8D807C`; f34 front lobe bottom `#7C706C`; swatch Rock Mid `#988E8C`) | 0.08–0.12, hue 5–16° | the lowest 20 % of each rock at 45 %; faces within 0.25 of moss at 25 % | rough 0.92 |

**Calibration warnings:**
- **Moss (flagged by the user twice on earlier sheets, `kit-colour-calibration`):** eyeballed moss renders pale and
  bluish under the studio sun. Calibrate on the parts-shot MC against `#6E8E20`, then check the front_sheet moss median
  within 10 of `#6F8E22`, sat ≥ 0.74, hue 76–79°; MC's crown third within 12 of `#95B038`. If lit faces wash toward
  `#A0B860`, lower the specular (`FOLIAGE_SPEC`), not the colour. The calibrated key will sit darker than the target.
- **Sprout:** calibrate on the parts-shot sprout against `#A1B732`; the front_sheet L median within 12 of `#A5BA38`,
  sat 0.70–0.78, hue 68–71°. It must not drift toward the moss hue (keep ≥ 6° and ≥ 35 levels apart) or whiten (sat <
  0.65 reads pastel).
- **Rock:** calibrate on the parts-shot base against `#A19492`; check the front_sheet rock median within 10 of
  `#8A7F7F` and the lit quartile within 15 of `#B2A6A2`; keep it warm (hue 0–16°, sat ≥ 0.07): a neutral or bluish
  grey reads wrong beside the sheet (R07's `#77737A` was purple-blue).
- The three families stay apart: moss sat ≥ 0.74 at hue 76–79°, sprout 0.70–0.76 at 68–71°, rock ≤ 0.12.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Clumps:** `moss`; the lowest 30 % of each clump by its own (tilted) height → 55 % `moss_dark`, fading by 0.5;
  broad patches (`K.patches` scale about 0.8, 2–4 facets each) of a 10 % lighter moss mix on the upper half, never
  single faces. Each clump its own `tint_var` 0.03.
- **Sprouts:** `sprout`; the lowest 25 % of each blade (by distance from the base point) → 50 % `sprout_base`, fading
  by 0.45; no tip band (the light does it).
- **Rocks:** `rock`; the lowest 20 % of each rock by height → 45 % `rock_low`, fading by 0.35; faces within 0.25 of a
  clump → 25 % `rock_low`; each small rock a slightly different tint (`tint_var` 0.04).
- **Hard edges only** where materials meet: moss | rock, sprout | rock (A), sprout | moss (B). They are automatic
  (separate keys on separate faces).

### 5.6 Texture (Tint) and finish

- **Tint** (per piece `tint_var` about 0.03–0.04):
  - clumps: `K.texture` amp 0.03, scale 0.6 (broad);
  - sprouts: amp 0.02, scale 0.6;
  - rocks: amp 0.05, scale 0.5;
  - never per-triangle confetti ("Broad, flat-shaded faces").
- **Finish:**

| Material | Roughness | Specular | Metal | Notes |
| --- | --- | --- | --- | --- |
| Moss keys | 0.9 | `FOLIAGE_SPEC` (low) | 0 | matte, soft |
| Sprout keys | 0.75 | `FOLIAGE_SPEC` (low) | 0 | the sheet's blades have soft highlights on lit facets |
| Rock keys | 0.92 | normal | 0 | matte stone |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Moss:** front_sheet M median within 10 of `#6F8E22`, sat 0.74–0.79; lit quartile within 15 of `#8DAA2D`; parts-shot
  clump within 10 of `#6E8E20`; each clump's bottom fifth darker than its top fifth by 40–70 levels (sheet 55–60).
- **Sprout:** front_sheet L median within 12 of `#A5BA38`; lit quartile within 15 of `#CEDC57`; blade bottom fifth
  darker than the top by 50–80 levels.
- **Rock:** front_sheet R median within 10 of `#8A7F7F`; lit quartile within 15 of `#B2A6A2`; parts-shot base within
  10 of `#A19492`.
- **Shares** per §2.4 and §4 step 5. **Glow share 0** (no pixel above v 0.90 in the moss or rock, none above the lit
  sprout values).

## 6. Joins and contact

- **Clumps on the rock:** each clump's underside sinks 0.15–0.30 into the rock (close-up 2: "Moss clump sits on rock");
  the joint is a dark crease, never a gap, a lip or a floating edge. ML and MR overhang SL and SR by 0.2–0.4 and touch
  them.
- **Clump to clump:** MC overlaps ML and MR by 0.1–0.2, leaving a crease between them (the sheet's dark seams at f .30
  and .60–.65 in the front).
- **Sprout A:** its stub sits in RB's front notch, sunk 0.10–0.15; the blades rise from one point ("Leaf blades join at
  base").
- **Sprout B:** its stub sinks 0.10–0.15 into the crease where MC and MR meet, touching both.
- **Small rocks:** overlap RB or a neighbour by 0.1–0.2, flat bottoms; floor-cut at z 0 (`m004.floor_cut`) gives one
  flat underside (close-up 3).
- No coplanar faces: jitter rock bottoms by 0.02–0.05 above z 0 before the cut; offset each blade base by its own
  small angle. Exact booleans: add pieces one at a time; save between (STAGES crash note).

## 7. Lighting and VFX plan (modeller, stages 5 and 6)

**What the sheet shows:** sunlit moss on grey rock. No glow (glow share 0 % in every view), no light, no spores, dust
or sparkle, no VFX callout. WorldModeling §9: cave moss's "visibility should come from shape and placed lighting, not
automatic emission".

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight:** nothing on the sheet glows; Neon would flatten the faceted clumps and the lime
  sprouts would read as glowing, which the sheet doesn't show.
- **Studio note (Requires Manual Validation):** cave moss belongs in Emberhollow Caves. Check in Studio that the moss
  still reads green (not black-olive) and the sprouts lime under the cave zone's lighting; if not, the fix is the
  zone's placed lights, per WorldModeling, not emission on the model.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **Recommended: none** (decision §8.7), as M023 and M031 decided for their harvest nodes. Record "Stage 6 skipped:
  the sheet shows no VFX".
- **Options** if the main session wants them:
  - the R07 pair: `harvest_hit` on MC's front at about (−0.15, −0.1, 3.0), colours `["#6E8E20", "#A1B732"]` (moss and
    sprout crumbs), and `harvest_deplete` at about (0, 0, 0.6), colours `["#6E8E20", "#A19492"]`;
  - faint spores: `dust` at about (0, +0.3, 3.6), colours `["#C8D88A", "#A5BC38"]`, rate about 0.3 — not on the
    sheet.
- **Not recommended:** any light, `crystal_glow` / `crystal_halo` (nothing glows), `ore_glint`, `vapour`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by `git grep` of the repo and a search of every sheet, kit and wip `.blend`,
zstd-decompressed (`m033_study/blendall.py`, 167 files):
- **R07 kit** (in `FlintbornWorldKit.blend` (56 hits), `wip/R07_cave_moss.blend` and every M015–M031 wip copy):
  `CaveMoss`, `CaveMossMossClump`, `CaveMossMossClumpSmall`, `CaveMossRockBase`, `CaveMossSprout`, `CaveMossChunk`,
  `CaveMossDepleted`; keys `r07_stone`, `r07_moss`, `r07_sprout` (`art/blender/scripts/kit/R07/cave_moss.py`,
  `art/roblox/kit/R07/manifest.json`). The substrings `MossClump`, `MossSprout` and `MossRock` hit only inside these.
- **W06 kit:** `MossCushionLarge`, `MossCushionSmall` (`W06.blend`, `W06_moss_and_ivy.blend`).
- `M.mk` would silently rename a clash to `<name>M033`, so avoid all of these.

**Proposed names.** `MossBoulder` and the `m033_` prefix occur nowhere in the repo or any `.blend` (0 hits each).

| Object | Part | Why |
| --- | --- | --- |
| `MossBoulderNode` | hero | `…Node` like `CaveFungusNode` / `BerryBushNode`; a new stem as M031 did, since R07 owns `CaveMoss*` |
| `MossBoulderClump` | Moss Clump (the centre clump, MC) | R07 owns `CaveMossMossClump` |
| `MossBoulderClumpSide` | Moss Clump Left / Right (ML's shape, untilted) | R07 owns `CaveMossMossClumpSmall` |
| `MossBoulderSprout` | Sprout (B's fan) | R07 owns `CaveMossSprout` |
| `MossBoulderBase` | Rock Base (RB alone, flat bottom) | R07 owns `CaveMossRockBase` |
| `MossBoulderSideRock` | Side Rock (R) | new |

- Fallback if the main session prefers the sheet's name: `CaveMossNode` is free as an exact name, but it shares R07's
  `CaveMoss` prefix (M031 avoided the same with `CaveFungus`).
- Palette keys `m033_*` (§5.4). Collection `Kit/M033 Cave Moss`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **6.4 × 4.75 × 3.9** (recommended: pebble-anchored at 1.0 stud; hump at the hip, moss crown at
   the waist, sprout tip at the chest; between M031 and M023), or the R07 footprint (8.1 × 6.0 × 4.95), or the M031
   height family (5.25 × 3.9 × 3.2).
2. **Layout:** **one Rock Base, three clumps (MC on the back hump highest, ML and MR draped over the shoulders), two
   sprouts (A in the front notch, B at the back-right), six small rocks (side L / R, front L / R, back L / R)**
   (recommended: the front and f34 agree, the r34 is them mirrored), against the top cell's two clumps (§3.4) and the
   side and rear cells' front redraws (§3.3) — recorded known misses.
3. **Sprout count:** **two in the hero** (recommended: every assembled view shows two), or three as the exploded
   draws (a third on ML's back-left, hidden in the front). The Sprout part is B's fan.
4. **Rock base:** **one non-convex lobed mesh (back hump, front lobe, front-left shoulder) plus six separate small
   rocks with creases** (recommended: "one form with separate rocks"), or a union of three hull domes (risks the
   rock-pile read).
5. **Colour keys:** **`moss` + `moss_dark` (bottom band), `sprout` + `sprout_base`, `rock` + `rock_low`, calibrated to
   the exploded parts** (recommended, §5.4); the Moss Light swatch is the sprout colour (§3.6) and the two rock swatches
   are one rock's lit and mid tones (§3.7).
6. **Hero packaging:** **one closed shell** (recommended: STAGES default), RB → small rocks → MC, ML, MR → sprouts, one
   piece at a time; fallback: a sprout that won't union cleanly stays a separate closed shell in the same object.
7. **Stage 5/6:** **no emission, light or VFX** (recommended: the sheet shows none; WorldModeling §9; as M023 and
   M031), or the R07 harvest pair, or faint `dust` spores (§7.2).
8. **Exports:** **the hero plus 5 parts** (`MossBoulderClump`, `MossBoulderClumpSide`, `MossBoulderSprout`,
   `MossBoulderBase`, `MossBoulderSideRock`) (recommended: the notes' "Reusable parts: moss clumps, sprouts, rock base,
   side rocks"), or 4 (drop `ClumpSide`). R07's `Chunk` drop and `Depleted` state are not on this sheet; not built
   unless asked.
9. **Comparison cameras** (§2.4, §3): `front_sheet (0, 12)` for the front and f34 cells, the same render flipped for
   the r34; `side_sheet (90, 12)`, `rear_sheet (180, 12)` and `top_sheet (0, 75)` judged by shares and widths; kit
   front34, rear34 and underside as self-consistency; a parts shot `(−20, 20)`.
10. **Names** as proposed (`MossBoulder*`, hero `MossBoulderNode`).

## 9. Pitfalls to avoid

1. **Green balls.** The clumps are faceted lumps with broad faces (12–18 visible, 0.35–0.8 stud), MC with a flat crown
   polygon and W : H 1.5–1.65, ML / MR tilted ovoids lying on the shoulders. Not icospheres, not subdivided spheres
   (R07), not `hull_rock` of a Fibonacci sphere (023's "pinched spheroids with even, soccer-ball facets").
2. **Pillow moss or a moss blanket.** R07 was flagged "pillowy saturated moss"; an earlier R07 pass became "a flat mat
   covering the rock". Three distinct clumps with creases; the base's front face stays bare.
3. **A rock pile.** The base is one lobed boulder that holds at least 70 % of the rock pixels in the front; the six
   small rocks are clearly smaller (≤ 0.2 W) and separated by creases. Not eleven equal domes, and not a flat slab
   (R07's "flat slab base").
4. **Flat-card sprouts.** Blades are closed diamond-section prisms with a midrib, pointed, chunky; 3–5 per sprout,
   joined at one base.
5. **Sprout A on top of the rock.** It roots low in a notch on the front face (h .27–.33 in the front), not on the
   hump's crown.
6. **Moss colour.** Measure and calibrate (§5.4); never eyeball (the user flagged moss twice). Moss hue 76–79°, sat ≥
   0.74; the sprouts are a different, yellower lime.
7. **Colour by facing.** The dark clump bottoms and light crowns are mostly light; paint the bottom band by height and
   the rock contact by distance; `K.check` facing correlation < 0.5.
8. **Cold grey rock.** Warm pink-grey (hue 0–16°, sat 0.07–0.12), one family; not R07's bluish `#77737A`.
9. **Comparing the wrong views.** The f34 is the front; the r34 is the f34 mirrored; the side and rear cells are
   front redraws; the top lacks the centre clump (§3).
10. **Side-view handedness.** The kit side camera at az 90 sits at +X, so screen right is the model's back; our side
    shows MR nearest, sprout A at the left and MC at the right, unlike the sheet's redraw.
11. **Shares with the shadow.** The ground shadow is background (O); measure shares on M + L + R only.
12. **Exact booleans.** Overlap everything (§6); add the 12 pieces one at a time; remove slivers with m011's `_tidy`
    / `_desliver`; save between risky steps. Watch the sprout stubs, blade tips and MC's crown polygon for bowtie
    vertices.
13. **Adding effects.** No Neon, no light, no sockets unless decision 7 says otherwise.
14. **Naming clashes** with R07's `CaveMoss*` and W06's `MossCushion*` (§8). Don't edit shared helpers
    (`kit_models.py`, `kit_mcp.py`, `build_kit.py`, `lib/vfx.py`); put new helpers in `m033.py`. No commits, pushes or
    exports in the modeller's stages.

## Decisions (main session, 2026-10-29)

The recommendations are accepted, with one change (6):
1. Size: 6.4 W × 4.75 D × 3.9 H.
2. Layout: three clumps, two sprouts and six small rocks, placed as the front views show.
3. Two sprouts in the hero.
4. Rock base: one non-convex lobed mesh holding at least 70 % of the rock pixels, with small rocks at most 0.2 W and creased all round.
5. Colour keys `m033_moss` / `moss_dark`, `sprout` / `sprout_base`, `rock` / `rock_low`, calibrated to the exploded parts.
6. **One closed shell, no exceptions.** Use a merge-0 union (`m021._union_fine`) for the sprouts. If one still won't fuse, move it until it does. A separate shell is not accepted.
7. No emission, light or VFX.
8. Hero plus 5 parts.
9. Comparison cameras: front (0, 12), also compared flipped for the rear three-quarter; side (90, 12), rear (180, 12) and top (0, 75), judged by shares.
10. Names: `MossBoulder*`, keys `m033_*`.

Clumps are broad-faceted lumps (12–18 broad faces visible, vertex valence 4–7), never balls or soccer-ball patterns.

## Stage 1 — Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m033.py` (`build()`; tuning helpers `hero_only()`, `preview()`, `calibrate()`). Built in
a background Blender (`bgmcp.py`, port 9881, `wip/M033.blend`). Every part has its own function; the hero is
assembled strictly from them.

- **Rock Base** (`_base_rock`): one non-convex ring mesh, 14 sectors; rings (radius, height fraction)
  `(0.93, 0) (1.0, 0.22) (0.97, 0.52) (0.86, 0.80) (0.64, 0.95)`, a 9-point top ring `(0.42, 0.99)` and a 5-point crown
  `(0.18, 1.0)`; half-step offset rings zipped into triangles; a low-order Fourier outline (±5/4/3 %) plus ±3 % jitter.
  Heights follow a lobe field read along each azimuth at ρ ≤ 0.42 (so each sector is a bulged dome profile; read at the
  outer rings it fell to a flat plate): back hump (−0.10, 1.00) 1.90, front lobe (0.00, −0.45) 2.50, front-left
  shoulder (−1.20, −0.70) 2.05, front-right (1.30, −0.40) 2.15, back flanks (∓1.4, 0.4) 1.60, floor 1.10, combined by a
  soft max (p 6) so the lobes are swells of one surface with shallow creases (a hard max gave thin streaky triangles
  along the crease lines). Centre (0.05, 0.25), radii 2.45 × 2.15. A 0.10-deep notch at (x −0.19, z 1.2) for sprout A.
- **Clumps** (`_clump_local`, `_clump`): convex hulls of jittered point rings (angular jitter ±0.28 step, radial ±10 %).
  MC rings `(0, .55, 6) (.24, .92, 7) (.52, 1, 7) (.80, .76, 6) (1, .36, 4)` (the last ring all at h 1 = the flat
  crown); side rings `(0, .40, 5) (.20, .86, 7) (.48, 1, 7) (.76, .84, 6) (1, .30, 4)`. 30 / 29 points (an earlier
  38-point hull read as a geodesic ball). MC (−0.15, 1.14, 2.52), 2.72 × 2.50 × 1.55, pitched 14° back (its back sinks
  down the back hump: more moss in the rear view), yaw 10°. ML (−1.72, −0.30, 1.82), 2.42 × 2.20 × 1.72; MR (1.74,
  −0.35, 1.74), 2.30 × 2.05 × 1.72; tilted ∓32° about Y so the inner end is up and the outer end hangs over the side
  rock, yawed ±14° (inner ends back toward MC), upper rings leaning 0.1 toward the middle.
  - **Spec deviation:** §2.2 says ML "tilt +25° (top toward +X)"; with this build's sign convention that lifts the
    *outer* end. The exploded and the front both show the inner end up and the outer end hanging, so ML is rotated
    −32° (its top normal toward −X, lying on the left shoulder) and MR +32°.
- **Sprouts** (`_blade`, `_stub`, `_sprout`): closed diamond-section blades (4 sections at t 0 / .2 / .55 / .85,
  widths .40 / .85 / 1.0 / .62 × 0.42 L, thickness 0.38 × width, a pointed tip, 7 % outward curl), each blade's face
  turned 55 % from its lean toward the front (the sheet draws every fan in the picture plane; faces along the lean
  showed the side blades edge-on). Blades rise from inside a 6-sided stub (Ø 0.30 → 0.22, 0.23 tall), bases nudged
  apart. A: 4 blades (1.65 / 6° forward, 1.45 / 41° az 195, 1.20 / 37° az 345, 1.10 / 25° back). B: 5 blades (1.64 /
  14° az 0, 1.30 / 30° az 160, 1.10 / 62° az 345, 0.80 / 30° az 95, 0.95 / 30° az 240). Seated by ray casts: A along
  +Y onto the base's front face at z 1.15 (seat (−0.19, −1.68, 1.15), sunk 0.12); B straight down onto MR's top-back
  at (1.31, 0.04) (seat z 2.40).
- **Small rocks** (`_small_rock`): squat bulged hull domes (m031 round-2 rings), each with its own bottom z (−0.03 …
  −0.09, no coplanar bottoms). SL (−2.58, 0.15) 1.40 × 1.35 × 1.45; SR (2.52, 0.15) 1.55 × 1.45 × 1.55; PL / PR /
  BL / BR are pushed out along their azimuth until they overlap the base's flank by 0.12–0.17 (`_seat_rock`, ray cast
  at z 0.25), so each touches the base whatever the jitter (two missed it by a hair in the first build and stayed
  separate shells). Sizes PL 1.0 × 0.9 × 0.72, PR 1.1 × 1.0 × 0.85, BL 0.78 × 0.72 × 0.60, BR 0.72 × 0.68 × 0.56.
- **Assembly / union:** base, rocks, clumps, stubs, blades in face order; `_union_fine` adds one shell at a time with
  merge 0 (m021 round 2) at the world origin (m030), with m031's guard against a union that drops the mesh;
  `_floor_cut` at z 0 (triangle-filled cap). Contacts (BVH): MC–RB, MC–ML, ML–SL/RB, MR–SR/RB, every small rock–RB.
  MR does not intersect MC (a visible crease between them; sprout B sits in it).

**Front_sheet (0, 12) against the front cell** (study masks, `scratchpad/m033_mod/meas.py`):

| | Sheet | Ours | Target |
| --- | --- | --- | --- |
| W : H | 1.469 | 1.439 | 1.40–1.54 ✓ |
| Moss / sprout / rock | 39.9 / 11.3 / 48.8 | 42.7 / 11.6 / 45.6 | ±4 ✓ |
| Top profile mean / max abs diff | — | 0.041 / 0.19 (the sprout-B column f .80) | ≤ .05 ✓ / ≤ .12 (tips .15): one column over |
| Width per height (h .1–.9) | `.94 .97 .95 .90 .87 .78 .64 .54 .38` | `.98 1.0 .97 .92 .86 .79 .70 .47 .36` | ±.07 ✓ (h .7 +.06, h .8 −.07) |
| Bands h .0 / .1 / .2 rock | 100 / 100 / 91 | 100 / 100 / 94 | ≥ 90 ✓ |
| Band h .6 green | 98 | 99 | ≥ 85 ✓ |

The r34 cell against the flipped front_sheet: profile .043 / .12 ✓, shares 42.7 / 11.6 / 45.6 against 39.2 / 13.9 /
46.9 ✓ (±5). Side_sheet: D : H 1.043 (1.05–1.25: a hair under), green 49.0 %, rock 51.0 % ✓. Rear_sheet: green
44.8 %, rock 55.2 % (spec 45–65 / 35–55: at the limit), h ≥ .5 at least 98 % green ✓, W : H 1.38 (spec 1.40–1.65: a hair
under). Top_sheet: green 60.1 %, rock 39.9 % ✓ (45–62 / 38–55); three clumps (the sheet's top draws two: known miss
§3.4).

**Size:** 6.35 W × 4.63 D × 3.95 H (target 6.4 ±0.3 × 4.75 ±0.35 × 3.9 ±0.2 ✓). Sprout B's tall tip is the top.

## Stage 2 — Optimisation and cleanup

| Object | Tris | Size (studs) | Shells | Non-manifold edges / verts | Boundary | Self-hits | Inverted | n-gons | Dup verts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MossBoulderNode (hero) | 1164 / 4000 | 6.35 × 4.63 × 3.95 | 1 | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| MossBoulderClump | 56 / 1000 | 2.59 × 2.26 × 1.55 | 1 | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| MossBoulderClumpSide | 54 / 1000 | 2.22 × 2.22 × 1.72 | 1 | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| MossBoulderSprout | 268 / 1000 | 1.68 × 1.01 × 1.71 | 1 | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| MossBoulderBase | 170 / 1000 | 5.10 × 4.23 × 2.30 | 1 | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| MossBoulderSideRock | 62 / 1000 | 1.38 × 1.53 × 1.55 | 1 | 0 / 0 | 0 | 0 | 0 | 0 | 0 |

- One closed shell (decision 6), no exceptions needed: both sprouts fuse with the merge-0 union. Every object: no
  wire edges, loose verts or zero-area faces; normals outward; no corner under 5° (`m012._thin`); `M.fix_bowties`
  last (0 bowties); origin at the bottom centre, transforms applied; flat shading, no custom normals.
- Fixed seeds: every part and the hero pass on attempt 0 (the retry loop exists but is not used). Sprout B's seat was
  moved 0.013 / −0.011 so that attempt 0 fuses (it had left one self-intersecting pair on MR). PR's overlap is 0.17
  (at 0.14 one face on PR's flank failed the inverted-face ray test).
- Topology: clump valence 4–8 (MC 4:3 5:11 6:12 7:3 8:1; side 4:3 5:13 6:7 7:5 8:1; the one valence-8 vertex sits in
  the flat bottom fan); MC's crown polygon is 2 coplanar tris, 0.40 sq studs, normal z > 0.95 on the part (pitched 14°
  in the hero). Largest clump face 0.49–0.51 sq studs, median 0.22–0.25. Clumps are 54–56 tris (the study's 55–95
  range at its floor: fewer, broader facets read less like a ball).

## Stage 3 — UV

Smart UV (angle 45°, ANGLE_BASED, margin 0.008) via `M.finish` / `_polish`, then `m012._uv_unfold`. All objects: 0
overlapping pairs, 0 flipped, min gap 0.016, border 0.008, density ratio 1.0 / 1.0 / 1.0. Islands / conformal stretch
p95: hero 217 / 1.028; Clump 9 / 1.070; ClumpSide 9 / 1.058; Sprout 52 / 1.020; Base 22 / 1.063; SideRock 11 / 1.015.

## Stage 4 — Materials, colour and texture

**Keys** (`PALETTE`): `m033_moss` `#648125` (rough 0.9, low spec), `m033_moss_dark` `#516A1D` (0.9, low spec),
`m033_sprout` `#ABC448` (0.75, Specular IOR 0.25), `m033_sprout_base` `#88A226` (0.75, low spec), `m033_rock`
`#857C7B` (0.92), `m033_rock_low` `#736B6A` (0.92). Mixes in use (25 / 50 / 75 % steps): moss→dark 25/50/75,
sprout→base 25/50/75, rock→low 25/50.

**Calibration:**
- Pass 1 (`K.calibrate`, test dome, against the study's exploded-part targets): moss `#5B7620` (rendered 107,138,32),
  moss_dark `#4B631A`, sprout `#819631`, sprout_base `#69801D`, rock `#7F797D` (rendered 159,147,144), rock_low
  `#6D676A`. The rock key came out B > G (mauve), so it was replaced by a warm key (R > G > B).
- Pass 2 (front_sheet, floor hidden, long lens, against the front cell's class medians; linear per-channel gains): the
  dome keys rendered everything too dark on the hero (moss `#617E1D`, sprout `#778923`, rock `#867A73`). Moss × ~1.3,
  then −6 % so the hero and the parts shot straddle their targets; sprout × ~1.75 (the blades stand in the clumps'
  shade) with Specular 0.25 for the sheet's pale lit facets; rock kept warm and slightly bluer.

**Final re-measure:**

| Region | Sheet | Ours | Δ / target |
| --- | --- | --- | --- |
| Front moss median / lit / shade | `#6F8E22` / `#8DAA2D` / `#435B17` | `#6A8921` / `#7EA128` / `#3F5413` | 5 ✓ / 15 (at the limit) / 6; sat 0.76, hue 77° ✓ |
| Front sprout median / lit | `#A5BA38` / `#CEDC57` | `#9FB536` / `#C5DD49` | 6 ✓ / 14 ✓; sat 0.73, hue 70° ✓ |
| Front rock median / lit | `#8A7F7F` / `#B2A6A2` | `#8A7D76` / `#AF9E95` | 9 ✓ / 13 ✓; hue 19°, R > G > B |
| Parts shot: Clump / ClumpSide | exploded `#6E8E20` | `#779825` / `#7C9F27` | 10 / 17 (parts shot lit with floor bounce) |
| Parts shot: Sprout | exploded `#A1B732` | `#A2B839` | 7 ✓ |
| Parts shot: Base / SideRock | exploded `#A19492` | `#A6978F` / `#A5948C` | 5 ✓ / 6 ✓ |
| Moss vs sprout | ≥ 6° and ≥ 35 levels apart | 77° vs 70°, 53 levels | ✓ |

**Blending (position only, never facing; `K.check` passes, so facing correlation < 0.5):**
- clumps: by the clump's own world height, the lowest 12 / 24 / 40 % → 75 / 50 / 25 % `moss_dark`. Bottom → top
  fifths on the parts shot: MC `#4A6115 → #7EA129` (45 levels; sheet 49), side `#57711A → #7FA229` (35; sheet 40–45).
  A 25 % lime crown was tried and dropped: `K.check` flagged it (colour following face direction, corr 0.92) and its
  lit faces fell into the sprout mask.
- blades: by distance along the blade, t < .2 / .4 / .6 → 75 / 50 / 25 % `sprout_base`; the stub 75 %. Parts-shot
  bottom → top 35 levels (sheet 61; the sheet's bright tips are light).
- rocks: by height, lowest 12 / 26 % → 50 / 25 % `rock_low`; faces within 0.25 of a clump → 25 %; the floor-cut cap
  plain `rock` (darkening it would follow facing).
- Hard edges only where materials meet (moss | rock, sprout | rock, sprout | moss).

**Texture (Tint):** broad noise mottling, clumps amp 0.035 scale 0.6, blades 0.02 / 0.6, rocks 0.05 / 0.5, plus each
small rock its own ±4 % tint and `tint_var` 0.03 per piece. No per-triangle confetti.

## Stage 5 — Lighting

Skipped (decision 7): the sheet shows nothing self-lit (glow share 0 %). No emission, no Neon, no light.
**Studio (Requires Manual Validation):** in Emberhollow Caves check that the moss still reads green and the sprouts
lime under the zone's lighting; fix with the zone's placed lights, not emission (WorldModeling §9).

## Stage 6 — VFX

Skipped (decision 7): no glow, spores, dust or sparkle on the sheet. The hero has no VFX sockets (checked in
`build()`); renders use vfx=True.

## Modeller's notes for the verifier

- **Build:** `m033.build()` ≈ 13–15 s build + 17–20 s renders; `problems` is empty. Renders in this folder:
  `front_sheet` (compare with both the front and the f34 cells, and flipped with the r34), `side_sheet`, `rear_sheet`,
  `top_sheet` (long lens, floor hidden), the kit views, `exploded`, `part_*`, close-ups `sprout_cu`, `rockmoss_cu`,
  `under_cu`. Measuring script: `scratchpad/m033_mod/meas.py` (the study's `m.py` masks on both images).
- **Known misses / near-limits:**
  - side and rear cells are front redraws (§3.3) and the top cell lacks MC (§3.4); our side shows the blades edge-on
    (sprout share 4 % against the redraw's 18 %);
  - rear_sheet rock 55.2 % / green 44.8 % sits on the 55 / 45 limit; rear and side W : H (1.38, 1.04) a hair under the
    study's estimates;
  - front lit moss 15 levels under the sheet (at the limit); parts-shot side clump 17 levels lighter than the exploded
    (the hero governs; the parts shot has floor bounce);
  - blade bottom → top contrast 35 levels against the study's 50–80 (the sheet's tips are brightly lit);
  - one top-profile column (sprout B's tip at f .80) off by 0.19;
  - clumps are 54–56 tris, at the floor of the study's 55–95; one valence-8 vertex per clump (bottom fan).
- **Spec deviations:** ML / MR tilt sign (see Stage 1); MC pitched 14° back and wider (2.72 × 2.50) than the study's
  2.35 × 2.0, to bring the rear share inside its band; SR 1.55 tall (study 1.85, which made an upright slab); side
  rocks and pebbles squatter than the study's table.

## Verification round 1 (verifier, 2026-10-29)

A fresh verifier, read-only, in a background Blender (port 9881) on `wip/M033_verify.blend`, with the model as the
main session integrated it (no `build()` run). Renders were made with `m033.render_views` (vfx=True), with
`M.MODEL_RENDERS` pointed at the scratchpad (`scratchpad/m033_verify/M033/`). The sheet and the renders were measured with
the study's masks (`m033_verify/meas_v.py`, a copy of `m033_mod/meas.py` reading those renders) and with
`M.sample` / `M.raw_sample`. My numbers reproduce the modeller's front figures exactly (W : H 1.439, shares 42.7 / 11.6
/ 45.6, top profile 0.041 / 0.19).

### Measured

| Object | Tris / budget | Size (studs) | Shells | NM edges / verts | Boundary / wire / loose | Zero-area / n-gons | Self-hits | Inverted | Corners < 5° | Normals | Origin offset | Transforms | UV (overlap / flip / gap / border / p95 conformal) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MossBoulderNode | 1164 / 4000 | 6.35 × 4.63 × 3.95 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | 0 | outward | (0, 0, 0) | applied | 0 / 0 / 0.016 / 0.008 / 1.028 (217 islands) |
| MossBoulderClump | 56 / 1000 | 2.59 × 2.26 × 1.55 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | 0 | outward | (0, 0, 0) | applied | 0 / 0 / 0.016 / 0.008 / 1.070 |
| MossBoulderClumpSide | 54 / 1000 | 2.22 × 2.22 × 1.72 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | 0 | outward | (0, 0, 0) | applied | 0 / 0 / 0.016 / 0.008 / 1.058 |
| MossBoulderSprout | 268 / 1000 | 1.68 × 1.01 × 1.71 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | 0 | outward | (0, 0, 0) | applied | 0 / 0 / 0.016 / 0.008 / 1.020 |
| MossBoulderBase | 170 / 1000 | 5.10 × 4.23 × 2.30 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | 0 | outward | (0, 0, 0) | applied | 0 / 0 / 0.016 / 0.008 / 1.063 |
| MossBoulderSideRock | 62 / 1000 | 1.38 × 1.53 × 1.55 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | 0 | outward | (0, 0, 0) | applied | 0 / 0 / 0.016 / 0.008 / 1.015 |

- Every object: 0 bowtie vertices, 0 duplicate vertices, flat shading (0 smooth faces), no custom normals, no
  modifiers, texel density ratio 1.0. `K.check`: no problems.
- Clump valence: MC 4–8 (one 8, in the bottom fan), side 4–8; the largest face is 0.49–0.51 sq studs, the median 0.23–0.26.
  MC has a 2-tri flat crown (0.40 sq studs, normal z > 0.95).
- Hero children: none (no VFX sockets, no lights). All 11 m033 materials have emission 0 and metal 0.

**Shape (front_sheet (0, 12) against the front / f34 cells; the r34 against the flipped render)**

| Check | Sheet | Ours | Verdict |
| --- | --- | --- | --- |
| W : H front / f34 / r34 | 1.469 / 1.491 / 1.527 | 1.439 | ✓ (1.40–1.54) |
| Moss / sprout / rock, front | 39.9 / 11.3 / 48.8 | 42.7 / 11.6 / 45.6 | ✓ ±4 |
| Moss / sprout / rock, r34 (flipped) | 39.2 / 13.9 / 46.9 | 42.7 / 11.6 / 45.6 | ✓ ±5 |
| Top profile mean / max, front / f34 / r34 | — | .041 / .19, .033 / .10, .043 / .12 | ✓; one front column (sprout B tip, f .80) is .19 off |
| Width per height, front (h .1–.9) | .94 .97 .95 .90 .87 .78 .64 .54 .38 | .98 1.0 .97 .92 .86 .79 .70 .47 .36 | ✓ ±.07 |
| Bands h .0–.2 rock / h .6 green | 100 100 91 / 98 | 100 100 94 / 99 | ✓ |
| Side_sheet D : H, green / rock | 1.05–1.25; 45–60 / 40–55 | 1.043; 49.0 / 51.0 | ✓ (D : H a hair under) |
| Rear_sheet W : H, green / rock, h ≥ .5 green | 1.40–1.65; 45–65 / 35–55; ≥ 80 | 1.384; 44.8 / 55.2; 99–100 | at the limits (the rear cell is a front redraw, §3.3) |
| Top_sheet green / rock | 45–62 / 38–55 | 60.1 / 39.9 | ✓ (three clumps; the sheet draws two, §3.4) |
| Base's share of the rock pixels in the front (ortho ray grid at (0, 12), hits on the Base part's surface) | sheet ≈ 67 % (hand-traced small-rock outlines on the f34) | **61 %** (60.5–62.9 % at a 0.01–0.1 tolerance) | decision 4 asks ≥ 70 % (see finding 1) |
| Small rocks, visible front width / top | SL .00–.17 h .40; PL .08–.24 h .20; PR .70–.87 h .24; SR .82–1.0 h .53 | SL .005–.156 (0.16 W) h .42; PL .13–.27 (0.14 W) h .18; PR .67–.82 (0.16 W) h .22; SR .86–1.0 (0.14 W) h .45 | ✓ every one ≤ 0.2 W visible and ±.05 of the sheet |
| Size | 6.4 ±0.3 × 4.75 ±0.35 × 3.9 ±0.2 | 6.35 × 4.63 × 3.95 | ✓ |

**Colour (median, lit quartile; true sRGB)**

| Region | Sheet | Ours | Δ / verdict |
| --- | --- | --- | --- |
| Front moss (study mask M) | `#6F8E22` / lit `#8DAA2D` | `#6A8923` / lit `#7EA128` | 5 ✓ / lit 15 darker (at the limit); hue 78°, sat 0.74 ✓ |
| Front moss (`M.sample` green, whole cell) | `#799723` (dark 72,98,23; light 158,183,54) | `#759625` (71,93,21; 152,173,53) | 4 ✓ / light 10 |
| Front sprout | `#A5BA38` / lit `#CEDC57` | `#9FB536` / lit `#C5DD49` | 6 ✓ / 14 ✓; hue 70°, sat 0.70 ✓ |
| Front rock (study mask R) | `#8A7F7F` / lit `#B2A6A2` | `#8A7D76` / lit `#AF9E95` | 9 (all in blue) / 13; **hue 21° vs the sheet's 0–15°, sat 0.15 vs 0.07** (finding 3) |
| Exploded clumps L / C / R vs parts shot Clump / ClumpSide | `#6C8B20` / `#6E8E20` / `#73921F`; range 75→150 | `#779825` / `#7C9F27`; range 88→129 | 9–12; flatter tonal range (finding 4) |
| Exploded sprout B vs part | `#A0B631` | `#A2B839` | 4 ✓ |
| Exploded base / side rock R vs parts | `#A19492` / `#9C8E8C` | `#A6978F` / `#A4948C` | 6 / 8 ✓; ours warmer (hue 21° vs 8°) |
| Swatches (raw) | Moss Dark `#5F7924`, Moss Mid `#728E27`, Moss Light `#A5BC39`, Rock Light `#BCB0AA`, Rock Mid `#998E8C` | keys `#648125` / `#516A1D` / `#ABC448` / `#88A226` / `#857C7B` / `#736B6A` | — |

- **Warm, not mauve:** every rock render R > G > B (front 138,125,118; parts 166,151,143). ✓
- **Blend by position:** `_paint_clump`, `_paint_rock` and the blade paint use height or distance only (read in the
  builder). Per-family correlation of key luminance with height: moss 0.71 (hero), sprout 0.82 (part), rock 0.08. The moss's
  correlation with normal z (0.78) follows from the bottom band on convex hulls, which the spec asks for (the sheet's
  dark bottom fifths). `K.check` passes. ✓
- **Tint:** a corner `Tint` attribute on every object; hero range 0.906–1.057 (std 0.029). The mean difference between
  neighbouring faces (0.009) is about a third of the difference between random face pairs (0.033), so the mottling is
  broad and visible, not confetti. ✓
- **Finish:** moss rough 0.9, low spec; sprout 0.75, spec 0.25; rock 0.92; no metal. ✓

**Lighting / VFX.** I checked the sheet again: there's no glow, halo, spores, dust, sparkle or VFX callout. The brightest
pixels are lit sprout facets that darken on their shaded sides. The skips of stages 5 and 6 are correct. The hero has
no sockets, no lights and no emission. ✓

**Decisions:** 1 size ✓; 2 layout (three clumps with MC highest, crown h .90; ML / MR on the shoulders; two sprouts,
A rooted at h ≈ .26–.28 in the front notch, B's tip the top at f .80; six small rocks, BL / BR visible in the rear) ✓;
3 two sprouts ✓; **4 one lobed non-convex base ✓, small rocks ≤ 0.2 W visible and creased ✓, but the base holds 61 % of
the front rock pixels, not ≥ 70 %** (finding 1); 5 keys `moss` / `moss_dark`, `sprout` / `sprout_base`, `rock` / `rock_low`
✓; 6 one closed shell, sprouts fused ✓; 7 no emission, light or VFX ✓; 8 hero plus 5 parts ✓; 9 cameras ✓;
10 names `MossBoulder*`, keys `m033_*` ✓.

### Findings

1. **Minor (decision 4's number; the main session's call).** The base holds **61 %** of the front rock pixels against
   decision 4's "at least 70 %". The study never measured this on the sheet. Hand-traced on the f34 cell, the sheet's own
   base holds about **67 %**, so the 70 % bar is above the reference, and ours is about 6 points under the sheet. The
   intent of the decision is met: one lobed form, and the small rocks' visible widths (0.14–0.16 W) and tops match their
   cells within ±.05. The deficit comes from the clumps covering a little more of the base (moss 42.7 against 39.9) and
   the side rocks' true footprints (SL 1.40 = 0.22 W, SR 1.55 = 0.24 W, against the study's 1.25–1.30). **Fix target if
   the main session holds 70 %:** SL to 1.25 × 1.30 × 1.30 and SR to 1.30 × 1.30 × 1.55 (study §2.1), pebbles PL / PR
   about 10 % lower. Re-measure with the ortho ray grid until the base reaches ≥ 0.67, while W stays ≥ 6.1 and the front
   bands stay ±.07.
2. **Minor (shape): the side clumps read as rounder balls than the sheet's sloping ovoids.** In the front, ML shows
   f .07–.34 × h .27–.74, which is narrower and more upright than the sheet's f .07–.42 × h .24–.74. In the top view ML
   and MR outline near-regular polygons. MC's squat crown matches. The silhouette metrics pass, so this is not a blocker.
   **Fix target:** stretch ClumpSide along its tilted axis (length : thickness 1.29 → about 1.4) and widen ML's
   inner end toward f .42.
3. **Minor (colour): the rock is slightly beige.** It renders at hue about 21° and sat 0.14–0.15, against the sheet's
   pink-grey (front 138,128,128, hue 0°, sat 0.07; exploded base hue 8°). Every channel is within 10, and R > G > B
   holds, so the colour family is right. **Fix target:** lift the rock keys' blue channel by about 6–8 (G ≈ B, never B > G)
   so the front rock median lands within 6 of `#8A7F7F` at hue ≤ 12°.
4. **Minor (colour): lit moss is about 10–15 levels dull, with a flatter tonal range per clump.** The parts-shot clump runs
   88 → 129 against the exploded clumps' 75 → 150. **Fix target:** within the existing position bands, a slightly lighter
   upper moss (for example a 10 % lighter moss mix by height on the top 25 %, not by facing), so the front lit quartile
   comes within 8 of `#8DAA2D`.
5. **Minor (cosmetic):** a long thin light fold runs across the base's back (visible in rear34 / rear between MC and
   ML). It is a crease of the lobe field; every corner is ≥ 5° and nothing is broken.
6. **Minor (finish consistency):** the base `m033_moss` has Specular 0.06 (`FOLIAGE_SPEC`), but its three dark mixes
   have 0.2. This can't be seen at roughness 0.9.
7. **Known misses (accepted in the spec):** the side and rear cells are front redraws, and the top cell has no MC; the
   sprouts are edge-on in our side view (sprout 4 % against the redraw's 18 %). Sprout B's tall tip sits about 0.05 W
   right of the sheet's (one top-profile column .19 off).

### Verdict

**PASS.** The mesh is clean (one closed shell, every topology and UV check at 0), every budget is met, the size is in
tolerance, the silhouette and shares match the front, f34 and flipped r34 within their tolerances, and the colour
families are right and blended by position. There is no glow or VFX, which is correct. Decisions 1–3 and 5–10 are
followed, and decision 4 is followed in form. Its 70 % base-pixel figure is missed (61 %), but that bar is above the
sheet's own ≈ 67 % (finding 1); the main session may hold it and send finding 1 back. The other findings are notes for
a later polish.

## Main session ruling (2026-10-29)
The model passes on round 1 and is committed with the minors left open.
- **Decision 4 (base share at least 70 %):** relaxed to the sheet's own figure. The verifier hand-traced about 67 % on the sheet; the model measures 61 %. The silhouette and share metrics pass, so this is recorded as a minor, not sent back.
- **Left for a later polish pass:**
  - the side clumps are rounder than the sheet's sloping ovoids (target length : thickness about 1.4);
  - the rock reads a little beige (raise blue 6–8, keep G ≥ B);
  - lit moss is 10–15 levels dull (lighter height band on the top 25 %);
  - a thin light fold across the base's back;
  - the specular mismatch inside the moss mixes.
- **Export:** 6 assets, 6 solid pieces, 1774 tris, 0 VFX sockets, palette 11 colours, 0 problems.
