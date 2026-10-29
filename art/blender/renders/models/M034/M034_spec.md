# 034 Streambed Section — spec

Reference: `art/blender/assets/references/034.png` (1024 × 1536 px). The sheet's own title is "36 — STREAMBED SECTION",
top right "FLINTBORN — WORLD MODELING CONCEPTS", footer "FLINTBORN — INDIVIDUAL MODEL STUDY" and "PAGE 36/132".
INDEX.md row 34 calls it "Flintborn streambed model study" (the sheet's printed number 36 is the generator's, not the
index's; the file and the index say 034).
Builder: `art/blender/kit/mcp/m034.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows water, foam and a separate flow-strip VFX overlay** (§7); no glow, fire or
particles.

Sheet text:
- **View labels:** "ASSEMBLED — FRONT THREE-QUARTER VIEW", "ASSEMBLED — REAR THREE-QUARTER VIEW", "ORTHOGRAPHIC VIEWS
  (MATCHING GEOMETRY)": "FRONT", "SIDE (LEFT)", "REAR", "TOP". The three side cells are low-elevation views (e ≈ 5°),
  not true orthographics (§3).
- **Exploded Construction labels:** "Rock Pieces (Various Sizes)", "Sand / Bank Slab (Base)", "Stream Bed Slab
  (Sand/Rock)". Dashed drop lines and small pins mark where rocks sit; the water sheet is drawn under the slabs.
- **Parts Breakdown (Isolated):** "Rock Pieces (Various Sizes)" (one tall, one medium, one small rock), "Sand / Bank Slab
  (Base)", "Stream Bed Slab (Sand/Rock)", "Water Plane (Flow Mesh)".
- **Construction Details:** "1. UNDERSIDE VIEW" ("Flat bottoms for clean placement on terrain grid."); "2. JUNCTION
  CLOSE-UP" ("Rocks sit on bank and stream slab. Simple overlapping edges."); "3. THICKNESS / CROSS-SECTION" ("Thin,
  consistent slab thickness. Water plane slightly above stream bed."; side labels "Water Plane (Thin)", "Stream Bed
  Slab (Thicker)").
- **Material Palette (Reference):** Sand / Earth, Rock, Water (Plane), Water (Stream Bed).
- **VFX Overlay (Separate):** "Flow Strips (Simple Mesh)", "Rendered separately, not part of solid geometry."
- **Modeling Notes:** "Modular slab design with separate parts.", "Rocks are reusable pieces in various sizes.",
  "Clean, low-poly, flat shaded geometry.", "Consistent thickness and simple shapes.", "Water is a separate plane (no
  baked details).", "Keep silhouettes chunky and readable."
- **Game context and the old kit:**
  - **W03 Shorelines / Waterfalls / River**, row 4 (`scripts/kit/W03/streambed_patch.py`, `renders/kit/W03/
    streambed_patch_goals.md`, kit `W03.blend`, exported `art/roblox/kit/W03/manifest.json`): `StreambedPatch`, a
    32 × 32 shallow-stream tile, 4.5 high, stream along Y (front −Y to back +Y), **banks z 1.6, water z 1.0, riverbed
    z 0.2, a 12-wide channel at both seams (x −6 … 6 at the waterline)** on sloped Delaunay banks; parts
    `StreambedPatchBankRocks` (hull), `StreambedPatchBedSlab` (precise), `StreambedPatchSubmergedRocks` (hull),
    `StreambedPatchWaterPlane` (none); variants `…Straight`, `…Bend`, `…Fork`. Flow strips there are `water_flow`
    beam sockets (`VFX_StreambedFlowStrips_N`, z 1.03, downstream −Y), foam is `water_foam` sockets only (the user's
    W03 rework removed foam meshes). Its goals note: anchors ~5 wide with tops z ~4.4 were "still a little smaller
    relative to the tile than the reference's biggest boulders"; `MODEL_PROGRESS.md` row 55 flags "smooth uniform
    bank rocks; no flow strips; no pebbles".
  - **M032 Shoreline Corner** (accepted 2026-10-29): water z 1.0 over bed 0.2, sand 1.0 → 1.8, a separate foam mesh on
    a `*water*` key plus `water_foam` sockets, one hero object with closed land / water / foam shells.
  - Later sheets that may join this tile: 037 "Waterfall Module" (its pool spills off the tile front), 050 "timber
    bridge", 160 "River flow and foam VFX study". The contract in §6 is what they should meet.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The cell paper is
`#FEFBF3` (254, 251, 243), tolerance 14. The two hero cells have their titles painted out (`TITLES` in `m.py`). The
masks are `cls()` in `m.py` (HSV, h in degrees):
- **W, water:** h 178–213, s ≥ 0.45, v ≥ 0.60 (both the light and the deep tone of the water texture).
- **S, sand:** h 26–55, s 0.25–0.80, v ≥ 0.62 (bank tops and the lit bank sides).
- **D, dark pebbles / contact soil:** h < 45, s ≥ 0.30, v 0.15–0.62.
- **R, rock and earth:** (s < 0.25, v 0.18–0.88) or (h 200–290, s < 0.60, v 0.15–0.92: the blue-violet shade faces) or
  (h < 26 or ≥ 300, s < 0.30, v 0.18–0.88: warm lit faces), not F. **The grey-taupe bed-slab sides and the underside
  fall into R by design** (they measure `#A19897` / `#84776C`).
- **F, foam:** (h 160–240 or s < 0.08), s < 0.45, v ≥ 0.88.
- **O, other:** outlines, deep crevices, orange pebbles below h 26; not a target.
- Order of assignment: W, S, D, R, F. Known leaks: rock shade faces at h 200–212 with s ≥ 0.45 fall into W (< 1 % of
  rock pixels); the brightest rock tops (v ≥ 0.88, s < 0.08) fall into F (< 1 point).
- **The sheet draws no ground shadow** (the paper under every cell is clean). Treat any render floor or floor shadow
  as background: measure renders made with `FB_Ground.hide_render = True` (§2.6).

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m034_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Pillow + numpy).
- **Helpers:** `m.py` (masks `cls()`, view boxes `V`, exploded / parts / close-up boxes `X`, `preview()`), `lab.py`
  (connected components), `zoom.py` (crop + upscale), `grid.py` → `g_*.png` (10 % grids over each view's silhouette,
  red = centre lines), `bb.json` (silhouette boxes and profiles).
- **Measurements:** `measure.py` → `measure_out.txt`; `measure_cells.txt` (every cell through `measure_render.py`, the
  numbers quoted in §1.2); `topscan.py` → `topscan_out.txt` (top-view rocks); `rockring.py` → `rockring_out.txt` (each
  rock's surroundings: bank / waterline / in water); `shore.py` → `shore_out.txt` (waterlines per row); `seam.py` (the
  seam rows and the slab-side bands); `herorocks.py` → `herorocks_out.txt` (hero rock blobs); `fit.py`, `fit2.py`,
  `projrocks.py` (plan-proxy camera and rock-height fits).
- **Colour:** `samp.py` → `samp_out.txt` (swatches, view medians, regions); `samp2.py` → `samp2_out.txt` (rock lit /
  shade split, water light / deep tones).
- **Crops:** `f34.png`, `r34.png`, `views.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`,
  `parts.png`, `cu.png`, `cu1.png`, `cu2.png`, `cu3.png`, `pal.png`, `z_*.png`; mask previews `cls_*.png`.
- **On our renders:** `measure_render.py <render.png> [paper_hex] [--flip]` prints the same bbox, shares, profiles,
  width per height and per-class colour medians with the study masks (an alpha channel counts as background). It
  reproduces the sheet numbers exactly on the sheet's own cells (`selftest_f34.png`).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a modular terrain tile with water. Hero budget 4000 tris (STAGES), each part under
  1000. The plan in §4.3 lands at about 2700–3200.
- **Overall read (check this first).** A **square, thin, flat-bottomed slab tile** with a **shallow cyan stream
  running straight through it from the front edge to the back edge**, between **two flat warm-sand bank slabs**. The
  stream bed is a **separate, lower slab** under a **thin flat water plane**; the banks' inner edges are straight,
  jogged plank edges, softened by a **white foam ribbon** along the water. **Big chunky grey boulders with large flat
  facets and flat crowns** stand **on both waterlines** (about three per bank: two big, one mid), half on the bank and
  half in the stream, each ringed by foam; **mid and small rocks** dot both banks; **one rock stands in mid-stream**;
  small grey and brown pebbles are scattered on the sand and in the water.
  - It must read as **two clean sand slabs, a recessed stream slab and separate boulders**, not a rock pile and not a
    sculpted riverbank: the slab sides are straight and level, the boulders stand apart with sand between them.
  - Hero shares (f34): water W 40.1 %, rock R 36.2 %, sand S 15.6 %, foam F 4.7 %, pebbles D 1.1 %.
- **Focal silhouettes, in order:**
  1. The big boulders: in the hero the back one at f .45–.67 (h .74–1.0, the tallest point of the cell), the front
     pair at f .45–.74 (h .01–.41), the right-back pair f .77–1.0 (h .53–.76), the left-mid one f .27–.43 (h .43–.66).
  2. The slab: a thin parallelogram, the water running out through the lower-left edge with no visible thickness and
     the right bank showing a tan side face about 1.6 thick.
  3. The cyan channel with its foam edges, crossing the tile diagonally on screen.
- **Target size: tile 32 W × 32 D (bbox 32 ± 0.3 × 32 ± 0.3), max z 8.0 ± 0.6 (big boulder tops)**, banks z 1.6, bed
  top z 0.7, water z 1.0, ground z 0 (decision §8.1).
  - **How it was derived.** The kit terrain grid and W03's `StreambedPatch` are 32 × 32; the top view is square (W : D
    1.005, 203 × 202 px → 6.3 px/stud). The front cell's slab is 226 px wide (7.06 px/stud): its bank side face is
    12 px = 1.7 studs (→ banks 1.6), the bed slab's grey side 8 px = 1.1, and the cell is 67 px = 9.5 studs high at
    e ≈ 5°, which puts the tallest boulder top at z ≈ 7.1–8.8 depending on which boulder it is (the drawing is not
    consistent). The plan-proxy fit (`fit.py`: the top view's rocks as domes on a 32 × 32 × 1.6 slab, height = k ×
    width) gives k ≈ 0.8 (front, rear), 1.0 (hero), 1.05 (side): **big boulders stand about 0.9 × their width above
    the bank (6.0–6.4 for 6.6–7.1 wide), tops z 7.6–8.0.** Hero scale: about 10.7 px/stud (477 px wide for the tile's
    44.6-stud projected width at az 35).
  - **Against the character (5.5):** big boulders 6.6–7.1 wide (1.2–1.3 C) and about 6.2 tall (1.1 C): cover-sized;
    mid rocks 4.5 wide, about 4 tall (0.7 C); channel 14 wide at the seams (2.5 C), 18–19 mid-tile; banks 7–9 wide;
    bank top 1.6 (0.3 C) and a 0.9 step down to the bed; water depth 0.3 (ankle-deep, wadeable).
  - **Why this size.** It matches the terrain grid, W03's tile and levels (bank 1.6, water 1.0) and M032's water
    level, so streams, shores and the 037 waterfall pool sit at one waterline; the boulders follow the sheet (bigger
    than W03's, which its own verifier called too small).
- **Build frame:** front −Y, +X right, ground z 0 = the flat underside. The stream runs along Y; downstream is −Y
  (W03 precedent; the sheet does not say). Tile X −16 … +16, Y −16 … +16. Origin = bbox bottom centre (the tile
  centre within ±0.1).

### 1.2 Measured views (`measure_cells.txt`)

| View (cell box) | Silhouette bbox (sheet px) | W : H | S | R | W | F | D |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (14,60,509,359) | 23–499 × 83–352 | 1.763 | 15.6 % | 36.2 % | 40.1 % | 4.7 % | 1.1 % |
| Rear three-quarter (514,60,1010,359) | 524–1000 × 88–357 | 1.767 | 16.2 % | 38.3 % | 36.3 % | 4.8 % | 1.7 % |
| Front (14,432,258,655) | 23–248 × 505–571 | 3.373 | 20.4 % | 57.7 % | 13.8 % | 3.6 % | 0.5 % |
| Side (left) (263,432,509,655) | 273–498 × 498–571 | 3.054 | 25.4 % | 52.7 % | 9.9 % | 4.6 % | 1.3 % |
| Rear (514,432,761,655) | 524–750 × 505–571 | 3.388 | 18.3 % | 58.2 % | 14.7 % | 4.0 % | 0.5 % |
| Top (766,432,1010,655) | 789–991 × 438–639 | 1.005 (W : D) | 31.8 % | 23.0 % | 35.3 % | 4.7 % | 1.4 % |

O (outlines, orange pebbles) is 2.3–6.2 %. **Verifier tolerance:** shares ±4 points (F, D ±2) unless stated;
positions ±0.06 of W / H unless stated.

- **The slab band in the side cells** (the bottom 17 % of H, 12–13 px): front S 63 % / R 31 % (the grey bed-slab side
  at f .35–.74), rear S 53 % / R 36 % (grey at f .50–.89), side S 83 % (all bank). Above the band R is 47–51 % in all
  three (the boulders).

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .35 | .47 | .53 | .58 | .63 | .69 | .71 | .77 | .81 | .85 | .96 | .96 | .97 | .99 | .90 | .87 | .83 | .80 | .75 | .77 | .65 |
| r34 | .53 | .60 | .62 | .66 | .74 | .72 | .75 | .81 | .83 | .90 | .97 | .93 | .96 | .99 | .90 | .85 | .80 | .76 | .73 | .72 | .60 |
| Front | .18 | .45 | .62 | .71 | .71 | .79 | .97 | .98 | .89 | .53 | .62 | .55 | .48 | .53 | .53 | .71 | .74 | .64 | .64 | .41 | .18 |
| Side | .16 | .41 | .53 | .66 | .77 | .75 | .48 | .53 | .44 | .44 | .55 | .55 | .88 | .97 | 1.0 | .97 | .90 | .51 | .48 | .29 | .16 |
| Rear | .18 | .44 | .52 | .71 | .76 | .71 | .53 | .58 | .48 | .50 | .64 | .59 | .77 | .97 | .98 | .89 | .67 | .62 | .52 | .42 | .18 |

The front, side and rear profiles are a **boulder skyline over a slab**: the flat slab band is h 0–.18, and every value
above .18 is a rock. Each shows a **dip to .44–.55 in the middle third (the channel)** with boulders both sides.

**Bottom profiles** (lowest silhouette pixel; the side cells are 0.00 everywhere: the slab's flat bottom edge):

```
f34    .30 .27 .24 .20 .17 .14 .10 .07 .04 .01 .00 .00 .01 .07 .13 .18 .23 .30 .39 .42 .48
r34    .47 .42 .36 .31 .25 .20 .14 .09 .04 .00 .05 .09 .13 .17 .21 .26 .30 .36 .39 .43 .48
```
- f34: the slab's two lower edges meet at f .50–.55 (the front-right corner; boulders hide the corner itself). The left
  edge (front edge of the tile) falls at slope .365 (screen), the right edge (the +X side) rises at .66.
- r34: the lowest point f .45 (the back-left corner, under a big boulder); slopes .61 and .48.

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .14@.46 .38@.30 .62@.15 .85@.00 .88@.03 .94@.06 .83@.17 .71@.28 .46@.39 .24@.47 .02@.62
r34    .02@.43 .23@.34 .45@.24 .65@.15 .85@.06 1.0@.00 .95@.05 .80@.17 .48@.33 .25@.45 .01@.63
front  1.0@.00 1.0@.00 1.0@.00 .95@.03 .91@.04 .85@.08 .81@.10 .72@.12 .16@.25 .13@.27 .04@.31
side   1.0@.00 1.0@.00 .97@.01 .94@.03 .87@.05 .82@.07 .69@.14 .66@.16 .60@.21 .19@.61 .08@.66
rear   1.0@.00 1.0@.00 1.0@.00 .95@.03 .92@.04 .87@.07 .74@.12 .64@.14 .15@.61 .13@.62 .04@.67
top    1.0@.00 at every height (a clean square: no notches in the tile outline)
```

**Top view rocks** (`topscan.py`, `rockring.py`; plan studs, X = −16 + 32u, Y = 16 − 32v; "wet" = the share of
water / foam round the rock):

| Rock | Plan (X, Y) | Size (studs) | Where |
| --- | --- | --- | --- |
| B1 | (−8.7, +11.0) | 6.8 × 7.3 | left waterline, back (wet .22, sand .53) |
| B2 | (+7.6, +6.4) | 6.6 × 7.1 | right waterline, back |
| B3 | (+10.9, −5.2) | 7.1 × 6.8 | right waterline, front-mid |
| B4 | (−8.3, −10.1) | 7.1 × 7.0 | left waterline, front |
| M1 | (+6.9, −9.8) | 4.6 × 4.6 | right waterline, front, mostly in the water (wet .45) |
| M2 | (−6.8, −3.0) | 4.6 × 4.4 | left waterline, mid, mostly in the water (wet .66) |
| S1 | (−3.8, +2.1) | 2.8 × 2.4 | **mid-stream** (wet .80) |
| bank rocks | (+13.6, −13.2) 3.5; (−12.5, −2.3) 3.2; (+13.3, +13.7) 2.8; (+13.7, +5.9) 2.7; (−13.8, −14.5) 2.7; (−14.0, +5.9) 2.7; (−14.1, −7.8) 2.7 × 1.6; (+14.3, −2.6) 2.4; (+8.6, +11.3) 2.4 | 2.4–3.5 | on the sand, mostly near the outer edges |
| small rocks | (+12.4, +1.8) 2.0; (+9.5, +0.8) 1.9 waterline; (+3.2, −11.8) 1.9 in water; (−13.0, +11.6) 1.9; (−7.8, +5.2) 1.7 waterline; (−10.1, +1.4) 1.6; (+6.6, −14.1) 1.6 waterline; (+5.7, +12.1) 1.3 in water; (−10.4, −5.5) 1.3; (−10.8, +6.6) 1.3; (+7.0, +14.8) 1.1 | 1.1–2.0 | |
| pebbles | about 15 grey and 8 brown / orange dots, 0.4–1.0 | | both banks, a few in the water |

Rock area in the top view: R 23.0 %, of which the six big and mid rocks are 15.4 points.

**Top view waterlines** (`shore.py`; the open water W only, and the outer edge of the wet zone where sand starts; X):

| v (0 = back) | .025 | .125 | .275 | .425 | .525 | .625 | .725 | .825 | .925 | .975 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open water | −6.4 … +6.1 | −4.8 … +6.4 | −7.7 … +3.8 | −7.0 … +9.0 | −5.8 … +8.6 | −3.8 … +7.7 | −5.8 … +8.3 | −5.4 … +3.2 | −8.6 … +5.8 | −7.7 … +5.8 |
| sand starts | −7.0 / +7.6 | −11.9 / +6.9 | −8.7 / +10.8 | −8.7 / +9.9 | −9.2 / +10.3 | −10.0 / +14.0 | −10.6 / +13.8 | −10.8 / +10.2 | −10.5 / +7.5 | −10.3 / +7.6 |

Where the open water narrows (v .125, .275, .625, .825) a big or mid boulder stands in it. **The seams:** the back edge
row (v = 0) has water + foam at X −6.5 … +6.7 (13.2 wide), the front edge row at X −7.4 … +7.7 (15.1 with foam); the
front cell's grey bed-slab side spans X −4.8 … +7.7 (12.5).

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, governs the read; `g_f34.png`).** A camera at the **front-right**: the tile's front
edge is the lower-left edge (the stream crosses it), the +X side is the lower-right edge (right bank with its tan side
face), the left bank runs along the upper-left. Fits: the edge slopes (.365 / .66) give az 38, e 28 with W : D 0.93; the
plan proxy (`fit.py`) scores best at **az 35, e 28** (az 30–40 within 0.01). Use **`f34_sheet (35, 28)`** (§3.1).
- **Slab:** thin; the lower-left (front) edge has no visible face where the water meets it, the right bank shows a tan
  face about 1.6 thick with two small steps in its top edge; the left bank's front end is cut square with a notch.
- **Boulders (sheet blobs, `herorocks_out.txt`; f, h):** left corner .05–.15, .37–.53; front-left in the water
  .22–.31, .27–.39; left-mid big .27–.43, .43–.66; back big .45–.67, .74–1.0; front pair at the front corner .45–.74,
  .01–.41; mid-stream .57–.65, .47–.57; right-back pair .77–1.0, .53–.76; smaller ones on the banks.
- **Water:** fills the lower-left half of the tile, with foam ribbons along both bank edges and rings round every
  rock in it; the texture shows light and deep cyan patches (§5.2).
- **Projection of the top-view plan into this camera** (`projrocks.py`, az 35 / e 28): B4 .14–.30, .36–.66; M2
  .29–.39, .48–.67; B1 .40–.56, .70–1.0; M1 .45–.55, .22–.41; B3 .56–.71, .22–.52; B2 .65–.80, .44–.74. The back
  boulder and the left-mid one land within about .05 of the sheet; the right-back pair lands about .1 left and the
  front pair about .15 higher than the sheet draws them (§3.2).

**Rear three-quarter (`g_r34.png`).** A camera at the **back-left** (az ≈ 225, e ≈ 32; the plan proxy scores .092
there). Its composition looks almost like the hero's because the top-view layout is roughly balanced under a 180°
turn (big boulders at the back-left and front-right ends of opposite banks). Water crosses the lower-left edge (the
tile's back edge, seen from behind); a big boulder sits at the bottom corner (B1 at the back-left).
- Compare with **`r34_sheet (225, 32)`**, not the kit rear34 (152, 12), which is a back-right camera.

**Front (`g_front.png`).** Camera az 0, e ≈ 5 (plan-proxy fit; the water's visible depth of about 20 px gives
32 × sin e × 7.06 ≈ 20 → e ≈ 5). A long thin slab (W : H 3.37): tan bank faces at both ends, the **grey-taupe
bed-slab face in the middle** (f .35–.74) with the cyan water just above it, a boulder skyline both sides of a central
dip (h .48–.62 at f .45–.70).

**Side (left) (`g_side.png`).** Labelled "SIDE (LEFT)": a camera at −X (az 270, screen right = front). The slab face is
**all sand** (the left bank's outer wall; the stream doesn't cross the side edges), boulders in front (the left bank's
B1 / B4) and the right bank's behind, water seen between them. W : H 3.05 (the tallest of the three side cells:
peak h 1.0 at f .70).

**Rear (`g_rear.png`).** az 180, e ≈ 5: like the front, with the grey bed face offset to f .50–.89 (from behind that
is X −12.5 … 0, against the top view's centred back seam: §3.4).

**Top (`g_top.png`; image top = back).** A square. The stream runs **straight from the top edge to the bottom edge**,
13–15 wide at the edges and up to about 19 mid-tile with a gentle bulge to the right at v .4–.75; sand banks left and
right with wavy foam-lined edges; the big boulders on the waterlines at the back-left, back-right, front-right and
front-left, two mid ones in the water, one rock mid-stream, mid and small rocks scattered on both banks, brown
pebbles. The outer edges are straight (width 1.00 at every row).

**Close-ups.**
- **1. Underside View** (14,1160,330,1290): the tile from below: **one flat taupe bottom** (`#84776C` in shade) inside a
  sand-coloured edge band; boulders peeking over the top edge.
- **2. Junction Close-Up** (335,1160,628,1290): a big boulder standing half on the sand and half in the water; its
  facets are large flat planes (several 1.5–2.5 studs across); a white foam band runs along the sand edge and round
  its foot; pale sand at the water's edge ("Rocks sit on bank and stream slab. Simple overlapping edges.").
- **3. Thickness / Cross-Section** (635,1160,1010,1290): a cut face of uniform thickness: under the bank a sand-coloured
  top layer fading into grey-taupe (`#BA9665` → `#A19897`), under the stream the same grey-taupe slab with a thin
  blue water band on top; the water top lies a little below the bank top; boulders and two small rocks on top.

### 1.4 Parts (Exploded Construction (14,666,700,1123), `expl.png`; Parts Breakdown (704,676,1012,1123), `parts.png`)

The exploded parts are drawn about 1.3–1.6× the hero's scale and laid out as a cleaner arrangement. **The hero and
top view govern sizes**; the exploded gives the part list, the slab language and the rock shapes.

#### Sand / Bank Slab (Base): exploded left (60,880,380,1000) and right (610,880,700,1000), parts (715,820,1000,900)

- **Shape:** a long flat **plank slab** of uniform thickness, straight long sides, **stepped / notched ends**
  (rectangular bites about 1.5–2 studs, L-shaped jogs), a flat sand top with lighter and darker broad patches, tan
  side faces; small rocks and pebbles sit on it (dashed lines mark their spots).
- **Hero part:** each bank: the outer wall flush with the tile side (X = ±16), the inner (water) edge a jogged straight
  line (§2.2), top z 1.6, bottom z 0.
- **Construction:** `_bank_slab(side)`: 2–3 overlapping plank blocks per bank (the "simple overlapping edges"), each a
  box from z 0 with its top at 1.6 (the middle plank may sit 0.15 higher or lower: the hero's right bank shows two
  small steps), the inner edge jogging 1–2 studs between planks with 45° chamfers; the top gridded at about 2 studs
  for colour patches (no z noise: "Clean, low-poly, flat shaded"); a 0.15 chamfer on the top outer edges only where a
  plank steps. **The outer tile wall and the seam faces stay straight and flat** (top view: no notches in the tile
  outline).

#### Stream Bed Slab (Sand/Rock): exploded (230,880,600,1010), parts (715,905,1000,1000)

- **Shape:** a long flat box of the same thickness class, drawn blue-topped with the water texture (the exploded draws
  its sides cyan; the front cell and the cross-section show its sides grey-taupe), a few small rocks with foam rings
  standing on it.
- **Hero part:** the channel floor between the banks: top z 0.7, bottom z 0, its side faces at the two seams (Y = ±16)
  grey-taupe earth; under the bank slabs it continues (or is unioned) so the land is one closed shell.
- **Construction:** `_bed_slab()`: the channel polygon (§2.2) extruded 0 → 0.7, the top gridded at 2 studs for the
  light / deep patches (§5.5); the small in-stream rocks belong to the hero layout, not to this part's geometry.

#### Water Plane (Flow Mesh): exploded (180,1035,560,1110), parts (735,1005,915,1090)

- **Shape:** a **thin flat sheet** of light cyan with three or four wavy white flow stripes ("Flow Mesh").
- **Hero part:** one flat water shell over the channel, top z 1.0, "slightly above stream bed".
- **Construction:** `_water_plane()`: the channel polygon grown 0.3 under the banks, extruded 0.6 → 1.0 (its bottom
  0.1 inside the bed slab, so no face is coplanar with the bed top), the seam faces inset 0.02 from Y = ±16 so they
  never coincide with the bed's seam faces. 12–40 tris. The flow stripes are not modelled into it: they are the VFX
  overlay (§7.2).

#### Rock Pieces (Various Sizes): exploded 12 flying pieces, parts 3 (`z_parts_rocks.png`)

- **Sizes (exploded px):** 130 (the big one), 81, 67, 54, 50, 49, 48, 40, 37, 35 wide: a ladder of about 1 : 0.62 :
  0.5 : 0.38 : 0.28, the same ladder as the top view (7.0 : 4.5 : 3.2 : 2.6 : 1.9).
- **Shapes:**
  - **Large** (the exploded big rock; parts' tall rock): a **broad base** (width at h .2–.4 = the maximum, the bottom
    ring at least 0.9 of it), steep sides of **big flat facets** (each 1.5–2.5 studs on a 7-stud rock), a **flat
    crown** about 0.45–0.55 of the width, height about 0.9 × width. Screen W : H 1.18 at the exploded view's ~30°
    elevation, width at h .5 / .7 / .9 = .91 / .76 / .57 of the max.
  - **Medium** (parts' left rock, exploded 67 px): a squat chunky dome with a flat top, height about 0.75 × width, a
    small rock lodged at its foot.
  - **Small** (parts' small rock, exploded 35–50 px): a flat-topped lump, height about 0.6 × width.
- **Construction:** `_rock(w, h, seed, crown)`: a convex hull of 3–4 jittered rings (bottom ring 0.95–1.0 R at z 0,
  widest ring 1.0 R at 0.2–0.3 h, shoulder ring 0.8 R at 0.7 h, a 4–5 point crown 0.45–0.55 R at h) with 7–9 points
  per ring and **irregular** angular jitter (±0.3 of the spacing), flat bottom. Large about 60–80 tris, medium 40–50,
  small 24–36, pebbles 8–14. `K.hull_rock` with explicit `rings` and `keep_bottom=True` is a fine base; no Fibonacci
  sphere, no ico-sphere, no vertex noise (M023 round 1).

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, stream along Y).

### 2.1 Levels (the tile contract)

| Level | z | Notes |
| --- | --- | --- |
| Ground / underside | 0 | one flat bottom for the whole tile ("Flat bottoms for clean placement on terrain grid") |
| Bed slab top | 0.7 | `m034_bed` (deep blue, §5), under the water |
| Water plane | top 1.0 (shell 0.6 → 1.0) | `m034_water`; W03 and M032 share this waterline |
| Foam | 1.03 → 1.06 | `m034_water_foam`, a thin closed shell, never within 0.02 of a water face |
| Bank top | 1.6 | sand; planks may step ±0.15 mid-bank, exactly 1.6 at the seams |
| Rock bases | 0.4 (waterline / in water), 1.3 (on the bank) | sunk 0.3 into the slab they sit on |
| Big boulder tops | 7.6–8.0 | the bbox top |
| Flow sockets / foam sockets | 1.03 / 1.05 | §7.2 |

### 2.2 Plan polylines (bank inner edges; straight segments with 45° jogs)

| Edge | Points (X, Y) | Sheet evidence |
| --- | --- | --- |
| Left bank inner edge | (−7.0, 16) → (−7.0, 12) → (−8.5, 10.5) → (−8.5, −3) → (−9.0, −4) → (−9.0, −11) → (−7.0, −13) → (−7.0, −16) | top-view sand edge −7.0 at the back seam, −8.7 … −10.6 mid-tile (with rocks); the open water at the front seam −7.7 |
| Right bank inner edge | (7.0, 16) → (7.0, 11) → (8.0, 10) → (8.0, 3) → (10.0, 1.5) → (10.0, −7) → (8.5, −8.5) → (8.5, −12) → (7.0, −13.5) → (7.0, −16) | top-view sand edge +7.6 at the back seam, +9.9 … +10.8 at v .3–.55, +13–14 round B3 (the boulder, not the bank), +7.5 at the front |
| Channel (bed slab, water plane) | between the two edges | 14 wide at both seams, 16.5 at Y +6, 19 at Y −5 |
| Foam ribbons | along both inner edges, on the water, 0.5–1.2 wide, wavy, with 3–5 round holes per 10 studs | hero and top: white bands 1–3 studs wide incl. the lighter water next to them |

- The channel's centre is X 0 at both seams (the sheet's water + foam centre is +0.1 at the back seam and +0.15 at the
  front seam; the open water alone −0.2 / −1.0), so the tile chains with itself along Y.
- The outer walls (X = ±16) are flat sand / earth faces from z 0 to 1.6; the seam faces (Y = ±16) are flat: banks
  0 → 1.6, bed 0 → 0.7, water 0.7 → 1.0 above it (inset 0.02).

### 2.3 Boulders and rocks (from the top view; heights from §1.1)

| Rock | Centre (X, Y) | Footprint w × d | Height (base → top z) | Base | Variant | Hero target f34 (f; h) |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | (−8.7, 11.0) | 6.8 × 7.3 | 0.4 → 7.8 | straddles the left edge | Large, yaw 15° | back big .45–.67; .74–1.0 |
| B2 | (8.0, 7.0) | 6.6 × 7.1 | 0.4 → 7.6 | straddles the right edge | Large, yaw −20° | right-back .77–1.0; .53–.76 (moved +0.4 / +0.6 from the top view toward the hero) |
| B3 | (10.9, −5.2) | 7.1 × 6.8 | 0.4 → 7.9 | straddles the right edge | Large ×1.0, yaw 40° | front pair .45–.74; .01–.41 (known high, §3.2) |
| B4 | (−8.3, −10.1) | 7.1 × 7.0 | 0.4 → 8.0 | straddles the left edge | Large, yaw −35° | left .14–.31; .27–.66 |
| M1 | (7.2, −10.3) | 4.8 × 4.6 | 0.4 → 4.6 | in the water at the right edge | Medium ×1.4 | front pair (with B3) |
| M2 | (−6.8, −3.0) | 4.6 × 4.4 | 0.4 → 4.4 | in the water at the left edge | Medium ×1.35 | left-mid .27–.43; .43–.66 |
| S1 | (−3.8, 2.1) | 2.8 × 2.4 | 0.4 → 2.6 | mid-stream | Small ×1.3 | mid-stream .57–.65; .47–.57 (the sheet's sits further right: §3.2) |
| Bank rocks ×9 | the "bank rocks" row in §1.2 | 2.4–3.5 | 1.3 → 1.3 + 0.7 w | on the sand | Medium / Small scaled 0.7–1.0 | — |
| Small rocks ×11 | the "small rocks" row in §1.2 | 1.1–2.0 | base 1.3 on sand, 0.4 in water; h 0.6 w | | Small scaled 0.5–0.8 | — |
| Pebbles ×20 | 12 on the banks, 4 in the water, 4 at the rock feet | 0.4–1.0 | h 0.3–0.5 | | 6–10 tri hulls; 7 brown / orange (`m034_pebble`), the rest rock | D share 1.1 % |

- Keep every rock at least 0.3 inside the tile outline (no rock crosses a seam or an outer wall).
- **The boulders stand apart:** at least 1.5 studs of sand or water between any two big / mid boulders (the junction
  close-up's pair is a big boulder with a small rock at its foot, not two big ones fused). Each big boulder may have
  one small rock (0.3–0.4 of its width) lodged at its foot, as in the parts breakdown.

### 2.4 Screen targets per view (renders measured with `measure_render.py`, floor hidden)

- **`f34_sheet (35, 28)`** against the hero: W : H 1.70–1.83 (sheet 1.763); shares S 15.6 (±5) / R 36.2 / W 40.1 (±6)
  / F 4.7 / D 1.1; top profile mean error ≤ 0.07 and every point within ±0.12; bottom profile within ±0.05; width per
  height within ±0.08 at every h; the four big boulders as four separate tall forms and M1 / M2 as two lower ones.
- **`r34_sheet (225, 32)`** against the rear three-quarter: W : H 1.70–1.83; shares within ±5 of S 16.2 / R 38.3 /
  W 36.3 / F 4.8; top profile mean ≤ 0.08; width per height ±0.08; a big boulder at the bottom corner.
- **`front_sheet (0, 5)`**: W : H 3.2–3.6 (sheet 3.373); shares ±4 of S 20.4 / R 57.7 / W 13.8 / F 3.6; the slab band
  (bottom 17 % of H) S 55–70 % with the grey bed face in the middle third; the top profile dips to ≤ .62 somewhere in
  f .45–.70 (the channel) with boulders over .70 on both sides.
- **`side_sheet (270, 5)`** (the sheet's "SIDE (LEFT)"): W : H 2.85–3.25 (sheet 3.054); shares ±5 of S 25.4 / R 52.7
  / W 9.9; the slab band ≥ 80 % S (no grey: the stream doesn't cross the side).
- **`rear_sheet (180, 5)`**: W : H 3.2–3.6 (sheet 3.388); shares ±4 of S 18.3 / R 58.2 / W 14.7 / F 4.0; grey bed
  face present (its position is a known miss: centred on ours, f .50–.89 on the sheet, §3.4).
- **kit `top (0, 89)`** against the top: W : D 1.00 ± 0.02; shares ±4 of S 31.8 / R 23.0 / W 35.3 / F 4.7; the open
  water per row within ±1.5 studs of §1.2's table where no boulder stands in it; the six big / mid boulders within
  ±1.5 studs of their plan positions.

### 2.5 Width-and-share sanity for the rear and side

The verifier failures on 021–023 came from views that were never measured. The rear and the side cells carry the
same weight as the hero here: **check W : H, shares, top profile and width per height in `rear_sheet`,
`side_sheet` and `r34_sheet` as well as in `f34_sheet` and `front_sheet`.**

### 2.6 How to measure our renders

- Render with the studio floor hidden: `bpy.data.objects["FB_Ground"].hide_render = True`, then `K.NS["KIT"]
  ["render_group"](objs, path, az, el)` for each extra camera; restore the floor afterwards. The sheet has no ground
  shadow; with the floor on, its shadow is classed R and inflates the rock share and the bbox.
- Run `measure_render.py <render> <background hex>` (or rely on the alpha channel if the render has one).

## 3. View conflicts and resolutions

### 3.1 The hero is a front-right camera, the kit front34 is front-left

- **Evidence.** The water crosses the hero's lower-left edge; in the front, side and rear cells the stream crosses the
  front and back edges only (grey bed face in the front and rear cells, all-sand face in the side cell), so the
  stream runs along Y and the lower-left edge is the front edge: the camera sits at +X of the front (az ≈ +35). The kit
  front34 is (−28, 12), from the front-left.
- **Resolution.** Compare the hero with **`f34_sheet (35, 28)`**. The kit front34 / rear34 / front / side / rear /
  underside are self-consistency only.

### 3.2 The hero and the top view place some rocks differently

- **Evidence.** Projected into the hero camera, the top view's plan lands the back boulder (B1) and the left-mid
  one (M2) within about .05 of the sheet, but the hero draws the front pair right at the front-right corner (h down to
  .01) where the top view has a 3.5-wide bank rock, the right-back pair about .1 further right, the mid-stream rock
  about .12 further right, and **water at the hero's left corner** (the front-left of the tile), where the top view
  has sand and two rocks. The rear three-quarter (from the back-left) agrees with the top view better (proxy score
  .092 against the hero's .130).
- **Resolution (decision §8.2).** **The top view governs the plan**: it is the only plan, and the tile must chain
  along the stream (the side walls must be bank, the seams must carry the same channel). Nudge only within the top
  view's own uncertainty toward the hero: B2 to (8.0, 7.0), M1 to (7.2, −10.3) and 4.8 wide. Record as known misses:
  the hero's front pair sits about .15 lower on the sheet than on ours; the hero's front-left corner shows water on the
  sheet and sand on ours (our f34 S share runs about +3–5 points, W about −3–6: the tolerances in §2.4 allow for it).

### 3.3 "SIDE (LEFT)" is a camera at −X

- The label and the all-sand slab face both fit a left camera (az 270, screen right = front). Compare **`side_sheet
  (270, 5)`** with the side cell; the kit side (90, 4) is self-consistency.

### 3.4 Front, rear and top disagree on where the channel meets the seams

- **Evidence.** Top view: centred at both seams (back −6.5 … +6.7, front −7.4 … +7.7 with foam). Front cell: grey bed
  face at X −4.8 … +7.7. Rear cell: X −12.5 … 0 (off-centre to the left).
- **Resolution.** The top view governs: a **centred 14-wide channel at both seams** (the tile contract, §6). Record the
  rear cell's off-centre bed face as a known miss.

### 3.5 Bed-slab sides: grey (front, rear, cross-section) or cyan (exploded)

- **Evidence.** The front and rear cells and the cross-section draw the bed slab's side as grey-taupe earth; the
  exploded and parts cells draw it as a cyan block (the water texture carried down the sides). The hero shows no face
  at all where the water meets the front edge.
- **Resolution.** **Grey-taupe earth sides** (`m034_earth`, three cells against one), with the thin water plane's own
  cyan side (0.3 tall above z 0.7) on top at the seams. The hero's missing front face is a drawing simplification.

### 3.6 Water level against the bank, and the W03 levels

- **Evidence.** The cross-section puts the water top a little below the bank top and the bed slab under it; the front
  cell's bed face is 1.1 studs against the bank's 1.7 (bed top ≈ 1.0, water ≈ 1.3 if read literally). W03 and M032
  use water z 1.0 with banks 1.6.
- **Resolution (decision §8.1).** Bank 1.6, **water 1.0**, bed top 0.7: the kit's one waterline, a 0.3-deep stream
  ("slightly above stream bed") and a 0.6 step from the water up to the bank (the sheet's 0.3–0.4 step reads the same
  at game scale). The front cell's grey face then reads 0.7 tall instead of 1.1 (3 px on the sheet's scale).

### 3.7 Bank outline: stepped planks (exploded, hero) against straight edges (top view)

- **Evidence.** The exploded and parts draw the bank slabs with notched, L-stepped ends and the hero's right bank shows
  two small steps; the top view's tile outline is a clean square at every row.
- **Resolution.** The outer walls and seams stay straight (tiling, top view); the "stepped plank" language goes on the
  **inner (water) edge** as 45° jogs between 2–3 overlapping planks (§2.2) and as small height steps (±0.15) between
  planks mid-bank.

### 3.8 Flow strips: mesh ("Simple Mesh") or VFX

- The sheet calls them a "VFX Overlay (Separate)", "Rendered separately, not part of solid geometry". In this kit a
  `water_flow` beam socket is exactly that: a flat scrolling streak on the water, previewed in the renders as a blended
  quad strip (`vfx.realize`). **Resolution (recommended):** `water_flow` beam sockets, not a mesh (§7.2, decision
  §8.6). The water plane itself stays one flat plane ("no baked details").

### 3.9 "Solid colors, flat shaded" against the user's blended-colour rule

- The sheet's surfaces are near-flat colours, but each carries broad patches: the sand has lighter and darker
  patches, the water a light / deep two-tone pattern, the rocks warm-lit / blue-violet shade faces (that one is
  lighting, never paint). Paint only broad position-based patches and bands (§5.5).

## 4. Construction plan (stages 1–3)

1. **Parts first,** each from its own function, checked against its exploded and parts cells:
   - `bank_slab()` → `StreambedSectionBankSlab`: the left bank as built in the hero (planks, jogged inner edge,
     sand top, tan / earth sides) with its pebbles and small rocks on it, as in the parts breakdown. Compare: a flat
     plank with straight sides and stepped ends, not a sculpted bank.
   - `bed_slab()` → `StreambedSectionBedSlab`: the channel slab (top 0.7, earth sides) with its in-water small rocks
     and pebbles.
   - `water_plane()` → `StreambedSectionWaterPlane`: the water shell alone, carrying the `water_flow` sockets.
   - `rock(size)` → `StreambedSectionRockLarge`, `StreambedSectionRockMedium`, `StreambedSectionRockSmall`: the three
     reusable rock pieces ("Rocks are reusable pieces in various sizes"), at the hero's B4 / M2 / small-rock scale.
   - Render a parts shot (`extra`, about (35, 28)) laid out like the parts breakdown (rocks above the bank slab, the
     bed slab, then the water plane).
2. **Hero** `StreambedSection`:
   1. **Land shell:** the two bank slabs and the bed slab, exact self-union one piece at a time, then the rocks and
      pebbles unioned in one at a time (largest first), `M.union_loose`, `M.fix_bowties`; save the work file between
      risky steps. Every rock sinks 0.3 into its slab so the unions are clean (no coplanar contact).
   2. **Water and foam:** joined into the same object as **separate closed shells**, never unioned with the land: the
      water shell (§1.4) and the foam shell (ribbons along both inner edges, a ring round each rock standing in the
      water: B1–B4, M1, M2, S1 and the 3 small in-water rocks, plus 6–10 loose blobs), 1.03 → 1.06.
   3. Origin at the bbox bottom centre; transforms applied.
3. **Budget** (§4.3): hero about 2700–3200 (limit 4000); each part under 1000. If over, drop pebbles and small-rock
   detail first, never the big boulders' facet count below 50 tris or their flat crowns.
4. **Placeholder keys** (stage 1): `m034_sand`, `m034_earth`, `m034_rock`, `m034_bed`, `m034_water`,
   `m034_water_foam`, `m034_pebble`.
5. **Stage 1 acceptance** (render, compare every view, measure with `measure_render.py` on floor-hidden renders):
   1. **Overall read:** two flat sand slabs, a recessed bed slab under a thin flat water plane, a straight stream from
      the front seam to the back seam, four big flat-faceted boulders on the waterlines plus two mid ones, one rock
      mid-stream, separate small rocks and pebbles on the sand, foam along both edges and round the rocks in the water.
   2. **`f34_sheet (35, 28)`** and **`r34_sheet (225, 32)`:** §2.4.
   3. **`front_sheet (0, 5)`, `side_sheet (270, 5)`, `rear_sheet (180, 5)`:** §2.4, including width per height and the
      slab-band shares.
   4. **kit `top (0, 89)`:** §2.4.
   5. **Kit views** (front34, rear34, front, side, rear, underside): self-consistency; the underside shows one flat
      bottom.
   6. **Parts against their cells;** extras **`junc_cu`** (about (20, 22), framed on B3 at the right waterline) against
      close-up 2 (the boulder half on sand, half in water, foam along the sand edge) and **`sect_cu`** (about (0, 12),
      framed on the front seam from X −16 to 0) against close-up 3 (sand over earth on the bank face, earth under the
      water, water top below the bank top).
   7. **Size:** bbox 32 ± 0.3 × 32 ± 0.3 × 8.0 ± 0.6; bank top 1.6 ± 0.05; water top 1.0 ± 0.02; bed top 0.7 ± 0.05.
6. **Stage 2:**
   - zero non-manifold edges and vertices (bowties: `M.fix_bowties`), boundary, wire and loose elements; no
     zero-area faces or n-gons; normals outward; no interior faces from the unions;
   - no faces under 5° where rocks meet the slabs;
   - the water and foam shells are closed and stay separate from the land shell; no foam face within 0.02 of a water
     face; the water's seam faces inset 0.02 from the bed's seam faces (no coincident faces at Y = ±16).
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even density. (The exporter writes palette UVs for solid faces
   and its own box-projected UVs for water pieces; the UV layer must still exist and be clean.)

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Bank slabs (2–3 planks, 2-stud top grid, sides) | 2 | 260 | 520 |
| Bed slab (2-stud top grid, sides) | 1 | 260 | 260 |
| Large boulders B1–B4 | 4 | 70 | 280 |
| Medium rocks M1, M2 | 2 | 46 | 92 |
| Bank rocks (2.4–3.5) | 9 | 36 | 324 |
| Small rocks (1.1–2.0) incl. S1 | 12 | 26 | 312 |
| Pebbles | 20 | 8 | 160 |
| Water plane shell | 1 | 40 | 40 |
| Foam shell (2 ribbons + 10 rings + blobs) | 1 | 450 | 450 |
| **Sum before union** | | | **about 2450** |
| **Hero after the land union** | | | **about 2700–3200** (limit 4000) |
| Parts: BankSlab / BedSlab / WaterPlane / RockLarge / RockMedium / RockSmall | | | about 450 / 330 / 40 / 70 / 46 / 26 (limit 1000) |

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 50 × 32 box inside each, y 1410–1442)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Sand / Earth | (42,1410,92,1442) | `#ECC07C` | 36°, 0.47, 0.93 |
| Rock | (141,1410,191,1442) | `#B4AEAF` | 350°, 0.03, 0.71 |
| Water (Plane) | (241,1410,291,1442) | `#22D5FE` | 191°, 0.87, 1.00 |
| Water (Stream Bed) | (340,1410,390,1442) | `#01B1EA` | 195°, 1.00, 0.92 |

- **Sand:** every rendered sand top is lighter and a touch more saturated than the swatch (`#FBCE81`); the lit sides
  are darker (`#C99C5E`) and the shaded sides darker still (`#A98353`): lighting.
- **Rock:** the swatch is a neutral grey; rendered rock is **warm in its lit faces** (h 0–20°, s .05–.13) and
  **blue-violet in its shade faces** (h 222–226°, s .28–.37), about half and half. Calibrate on the lit faces.
- **Water:** the plane swatch is the light tone, the stream-bed swatch the deep tone of the water's two-tone pattern;
  the rendered water median sits between (`#08D1FD`).
- **"Sand / Earth"** names one swatch for two things: the sand top and the grey-taupe earth of the slab sides and
  underside (cross-section `#A19897`, front cell `#AD9E8F`, underside `#84776C` in shade).

### 5.2 Rendered regions (`samp*.py`; median / lit quartile / shade quartile)

| Region | Box / mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- |
| Sand, exploded left bank top (unshadowed) | (110,905,300,950) S | `#FBCE81` | `#FEE8A8` | `#F3C171` |
| Sand, parts bank top (unshadowed) | (740,800,940,860) S | `#FCD085` | `#FDE198` | `#EBBA70` |
| Sand, hero open banks right / left | (400,230,480,290) / (90,170,210,230) S | `#FBCA7C` / `#FDD180` | `#FDDC94` / `#FEEBA8` | `#EAB565` / `#F8C570` |
| Sand, view medians f34 / r34 / top | V S | `#FCCF7F` / `#FCD384` / `#F7C375` | `#FDE59D` / `#FEE69F` / `#FCD692` | `#EAB566` / `#E5B065` / `#EBB362` |
| Sand, junction close-up (by the water) | (340,1240,420,1270) S | `#FCDE91` | `#FDE8A2` | `#C8A66D` |
| Bank side face, front cell (lit) / exploded (shaded) / parts (lit) | (25,562,90,570) / (90,955,200,985) / (725,870,830,895) | `#C99C5E` / `#A98353` / `#F6C574` | | |
| Bank cut face (cross-section, sand layer) | (650,1250,740,1275) | `#BA9665` | | |
| Earth: bed cut face / front-cell bed side / underside | (790,1250,880,1275) / (95,564,165,570) / (60,1215,230,1265) | `#A19897` / `#AD9E8F` / `#84776C` | underside `#BFADA1` | |
| Rock, exploded all rocks | (170,680,670,870) R | `#998E9A` | `#CEC3CA` | `#555A6D` |
| Rock, lit faces (v > .7) exploded / parts / f34 / top | R | `#C7BBB9` / `#C8BFBE` / `#C8BBBD` / `#C9BCBF` | `#D4CBCF` | |
| Rock, warm-lit faces / cool shade faces (f34) | R by hue | `#C1B0A8` (19°, .13) / `#57668B` (223°, .37) | | |
| Rock, junction close-up (big, near) | (380,1170,480,1240) R | `#A59698` | `#B4AAB1` | `#666674` |
| Rock, view medians f34 / r34 / front / side / rear / top | V R | `#978D97` / `#98909B` / `#9E9898` / `#938D97` / `#A49B99` / `#928D9E` | | |
| Water, view medians f34 / r34 / top / front | V W | `#08D1FD` / `#09D2FD` / `#04C9FD` / `#18D0FA` | `#4BE5FD` | `#01B7FB` |
| Water, light tone / deep tone (f34; about 1/3 of W each) | W s < .9 / s ≥ .97 | `#3FE1FD` / `#01C2FC` | | |
| Water, exploded bed slab top / parts bed slab top | W | `#07D1FD` / `#10D6FD` | | |
| Water plane part (flow mesh, over paper) exploded / parts | W | `#79ECFE` / `#4AE4FD` | | |
| Foam, f34 / top / parts / junction | F | `#C2F2FC` / `#C0F4FB` / `#C6F6FC` / `#C8EFFA` | `#E5FAFD` | `#94D9FB` |
| Pebbles, brown (D) f34 / exploded | D | `#846642` / `#916D43` | `#937354` | `#594431` |
| Pebbles, orange (h 8–28, s ≥ .45) f34 / top | | `#B5704D` / `#A16B44` | `#DC9664` | |

### 5.3 How the colour works

- **Sand:** one warm sand (h 36–40°, s .47–.52) with broad lighter patches (`#FEE8A8`-ish) and paler sand along the
  water's edge (junction `#FCDE91`); darker contact under rocks. The side faces are the same sand lit from the side,
  fading into the earth grey in their lower part (cross-section: sand layer over grey).
- **Earth:** one grey-taupe (h 6–30°, s .06–.17) for the bed slab's sides, the bank sides' lower band and the whole
  underside.
- **Rock:** one warm grey; lit faces warm, shade faces blue-violet (lighting). Per-rock Tint ±4 % so neighbours differ
  slightly. The crowns read lighter because they face the sun.
- **Water:** one saturated cyan plane over a **deep blue bed with broad light patches**: the patches under the
  see-through water give the sheet's light / deep two-tone texture (light `#3FE1FD`, deep `#01C2FC`, about one third
  of the water each).
- **Foam:** one pale cyan-white.
- **Pebbles:** grey ones are rock; 7 of the 20 are brown / orange.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are **unshadowed rendered regions** (the exploded and parts slabs, the lit rock faces, the open
water), not swatches and not shade quartiles.

| Key | Calibration target (kind) | Where | Finish |
| --- | --- | --- | --- |
| `m034_sand` | `#FBCE81` (brown; exploded bank top, unshadowed; parts `#FCD085`; hero open `#FBCA7C`; swatch `#ECC07C`) | bank tops, upper 60 % of bank sides | rough 0.95 |
| `m034_sand_light` | `#FEE5A0` (lit quartiles `#FEE8A8` / `#FDE59D`; junction `#FCDE91`) | broad patches and the water-edge band, at 35–40 % | rough 0.95 |
| `m034_earth` | `#A39A97` (stone; bed cut face `#A19897`, front-cell bed side `#AD9E8F`) | bed slab sides, underside, lower 40 % of bank sides | rough 0.95 |
| `m034_rock` | lit faces median `#C8BBBD` ± 10 (stone; v > .7 in f34, exploded `#C7BBB9`); whole-rock median `#998E9A` ± 12 (exploded); swatch `#B4AEAF` | every rock and the grey pebbles | rough 0.85 |
| `m034_bed` | `#01B1EA` start (swatch "Water (Stream Bed)"), tuned so the deep water tone renders `#01C2FC` ± 15 | bed slab top | rough 0.9 |
| `m034_bed_light` | `#3FE1FD` start (the light water tone; swatch "Water (Plane)" `#22D5FE`) | broad patches on the bed top, about 35 % of its area | rough 0.9 |
| `m034_water` | `#22D5FE` start (swatch); the rendered water median `#08D1FD` ± 12 with s ≥ .88 (f34) | water shell | rough 0.15, `kit_transparency` 0.3 (decision §8.6) |
| `m034_water_foam` | `#DDF8FC` start; the rendered foam median `#C2F2FC` ± 12, lit quartile ≈ `#E5FAFD` | foam shell | rough 0.6, `kit_transparency` 0.1 |
| `m034_pebble` | `#8E6B45` (brown; D medians `#846642` / `#916D43`; 2–3 of them toward the orange `#B5704D`) | brown / orange pebbles | rough 0.9 |

- The bed keys must **not** contain "water" (the exporter would make the bed a see-through, non-colliding piece). The
  foam key must (so the foam exports as its own see-through piece and never collides).

**Calibration warnings:**
- **Rock:** the lit faces must stay warm (h 0–25°, s .05–.15) and the shade faces blue-violet; a drift to the swatch's
  neutral `#B4AEAF` everywhere, or a calibration to the whole-rock median alone, loses the read. Check both targets.
- **Sand:** keep s ≥ .45 on the lit tops; the sides go darker by lighting, never by a darker key chosen by facing.
- **Water:** judge it by its render median after tuning the bed, not by the key (W03 found see-through water rendered
  paler than the sheet); in Roblox the exported water texture and `kit_transparency` decide it (Studio check, §7.1).
- Keep the families apart: sand s .45–.55, earth s ≤ .18, rock s ≤ .15 lit, water s ≥ .88, foam s ≤ .25.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Sand (bank tops):** `sand` base; broad patches (`K.patches(scale≈0.3, level≈0.15)`: `scale` is a frequency, so
  patches about 3 studs across, covering about 0.5 − level = 35 % of the top) → 35 % `sand_light`; within 1.0
  of the inner (water) edge → 40 % `sand_light` (the pale shore band); within 0.6 of a rock foot → 25 % `pebble`
  (contact).
- **Bank sides:** by height: z > 0.65 · 1.6 → `sand`; the band below blends in 3 steps to `earth` at z < 0.35 (the
  cross-section's sand-over-grey).
- **Bed top:** `bed` base; broad patches (`K.patches(scale≈0.3–0.4, level≈0.15)`, 2.5–3.5 studs across, about 35 %)
  → `bed_light`, blended in 3 steps (no hard
  confetti); within 0.6 of a rock foot → 30 % `earth`.
- **Rock:** `rock` with per-rock Tint ±0.04; faces below z 1.0 (under the water) → 30 % `earth` (wet base).
- **Hard edges only** where materials meet: sand | earth at the slab top edges where a plank steps, rock | sand, rock |
  bed, bed | earth (the bed top's rim), water | foam.

### 5.6 Texture (Tint) and finish

- **Tint:** sand amp 0.04 scale 0.6; earth amp 0.03 scale 0.8; rock amp 0.04 scale 0.5 (broad, per rock); bed amp
  0.03 scale 0.8; water and foam amp 0 (the exporter textures water). Never per-triangle confetti.
- **Finish:** roughness per §5.4; metal 0 everywhere; no emission.

### 5.7 Re-measure (final renders against the sheet, same masks)

- Sand: f34 S median within 10 of `#FCCF7F`; parts-shot bank slab top within 8 of `#FCD085`.
- Earth: `front_sheet` bed-face median within 12 of `#AD9E8F`; underside flat (no lighting judgement: `under_cu` may be
  dark, M023 lesson).
- Rock: f34 lit-face (v > .7) median within 10 of `#C8BBBD`, whole-rock median within 12 of `#978D97`; lit faces warm,
  shade faces blue-violet.
- Water: f34 W median within 12 of `#08D1FD`; light / deep tones present (each ≥ 20 % of W); foam median within 12
  of `#C2F2FC`.
- Shares per §2.4 in every compared view.

## 6. Joins, contact and the tile contract

- **Rocks on the slabs:** every rock sinks 0.3 into the slab it stands on (bank 1.6 → base 1.3; bed 0.7 → base 0.4);
  waterline boulders straddle the bank's inner edge with about half their footprint over the bed ("Rocks sit on bank
  and stream slab"); none perched on a point, no gaps under them.
- **Banks against the bed:** the bank planks overlap the bed slab by at least 0.3 under the inner edge so the union is
  clean; the inner edge's vertical face (1.6 − 0.7 = 0.9 tall) is sand above the water, earth-blended below z 1.0.
- **Ground:** one flat underside at z 0.
- **Water and foam:** closed shells, never unioned with the land; foam 1.03 → 1.06; the water's bottom 0.1 inside the
  bed slab and its long edges tucked 0.3 under the banks; seam faces inset 0.02.
- **Tile contract (record for 037, 050, 160 and any streambed variants):**
  - 32 × 32, ground z 0, bank tops 1.6 (exactly at the seams), water top 1.0, bed top 0.7;
  - **front and back seams (Y = ±16):** bed and water X −7 … +7 (centre 0), banks |X| 7 … 16; flat vertical faces;
  - **side walls (X = ±16):** solid bank faces 0 → 1.6 (the tile chains along the stream, and abuts terrain or a
    bank tile at its sides);
  - no rock crosses a seam or a side wall (≥ 0.3 inside).
  - **Against W03 `StreambedPatch`:** same tile size, bank 1.6 and waterline 1.0, but a 14-wide stepped channel
    (bed 0.7) against W03's 12-wide sloped one (bed 0.2): they don't join seamlessly. Chaining them needs a transition
    tile (decision §8.4).
- No coplanar faces between the bed top, the water bottom and the bank bottoms; rock bottoms jittered 0.02–0.05 off
  slab levels; exact booleans one piece at a time (STAGES "Booleans").

## 7. Water, lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** a flat saturated cyan water plane with a light / deep pattern, white foam along both bank
edges and round every rock in the water, and a **separate flow-strip overlay** ("VFX Overlay (Separate)": wavy white
streaks on a transparent sheet). No glow, light, sparkle, mist or particles. WorldModeling §12.3: separate land, sand,
water surface and foam; "a few broad strips or rings"; no z-fighting; "Record waterline and flow direction".

### 7.1 Water (export) and stage 5 (lighting)

- **How water exports** (`export_kit_roblox.py`): faces whose key `flintkit.is_water_key()` accepts (any key containing
  "water") become separate see-through pieces, one per key: SmoothPlastic, the key's 512 × 512 tileable texture (one
  tile per 16 studs, box-projected UVs from the asset origin so the pattern continues across tiles), `transparency`
  from `kit_transparency` (else 0.4), **no collision, no shadow**. Hence `m034_water` and `m034_water_foam`, and bed
  keys without "water".
- **Expected STATS for the hero:** solid 1 (or 2 if over the cut size), **water 2** (`m034_water`,
  `m034_water_foam`), glow 0.
- **Collision:** the hero and the slab parts **`collision="precise"`** (PreciseConvexDecomposition): the default hull
  would wrap the whole tile and its 8-stud boulders in one box. Rock parts `hull`. (W03 used precise for its bed slab.)
- **Waterline z 1.0; flow direction +Y → −Y (downstream = the front seam).**
- **Stage 5 (lighting): skip, and record why.** Nothing glows; no emission, no PointLight.
- **Studio notes (Requires Manual Validation):** the water's cyan and the light / deep pattern through the exported
  texture and transparency; the foam's opacity; that the 0.9 step from the bed (0.7) up to the bank (1.6) is walkable
  for the default character; the sand's warmth and the rock's warm / cool read under the game's sun.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`, `heat_glow`,
  `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **`water_flow` (the sheet's Flow Strips):** a beam kind; it needs `end=` and takes `width=`
  (`fx=[("water_flow", start, {"end": end, "width": w})]`):
  - centre: (0.5, 15.5, 1.03) → (0.5, −15.5, 1.03), width 6;
  - left: (−4.5, 14, 1.03) → (−4.5, −14, 1.03), width 3;
  - right: (5.0, 14, 1.03) → (5.5, −14, 1.03), width 3 (optional `curve0` to follow the right-hand bulge).
  - **3 sockets** on the hero and the same 3 on `StreambedSectionWaterPlane` (the parts breakdown's "Flow Mesh").
- **`water_foam`:** one per rock standing in or straddling the water, at z 1.05, scale by size: B1–B4 1.0, M1 / M2 0.8,
  S1 0.6, and the three small in-water rocks 0.4 (**10 sockets**); plus 2 per bank edge where no boulder stands
  (about (−8.5, 4), (−9, −7), (8, 13), (8.5, −11)) at scale 0.7 (**4 sockets**). **14 in all**; check the export STATS
  line reports 17 sockets on the hero (14 foam + 3 flow).
- **Not recommended:** `waterfall_mist`, `vapour`, `dust`, any light (nothing on the sheet).

## 8. Naming and decisions for the main session

**Names owned elsewhere** (repo text and every sheet / kit / checkpoint / wip `.blend`, zstd-decompressed, with
`blendall.py`):
- **W03** (`W03.blend`, `wip/W03_streambed_patch.blend`, manifest): `StreambedPatch`, `StreambedPatchBankRocks`,
  `StreambedPatchBedSlab`, `StreambedPatchSubmergedRocks`, `StreambedPatchWaterPlane`, `StreambedPatchStraight`,
  `StreambedPatchBend`, `StreambedPatchFork`; strings `StreambedBedSlab`, `StreambedWaterPlane`, `StreambedRock*`
  (84 hits), `StreambedFlowStrips` / `FlowStrips` (53 hits: socket names); keys `w03_*`.
  `FlintbornWorldKit.blend` and every M0xx wip blend carry `StreambedPatch` (166 hits: the W03 objects in the kit file).
- **07 terrain kit:** keys `water`, `water_deep`, `water_shallow`, `foam`, `sand`.
- **`StreambedSection` and `m034` occur nowhere** in the repo text or any `.blend`. `M.mk` would silently rename a clash
  to `<name>M034`; the names below don't clash. Avoid the bare `Streambed…` part names W03 owns (`StreambedBedSlab`,
  `StreambedWaterPlane`, `StreambedRock…`).

| Object | Part | Why |
| --- | --- | --- |
| `StreambedSection` | hero | the sheet's title; free |
| `StreambedSectionBankSlab` | Sand / Bank Slab (Base) | |
| `StreambedSectionBedSlab` | Stream Bed Slab (Sand/Rock) | `StreambedBedSlab` is W03's |
| `StreambedSectionWaterPlane` | Water Plane (Flow Mesh) | `StreambedWaterPlane` is W03's |
| `StreambedSectionRockLarge` / `…RockMedium` / `…RockSmall` | Rock Pieces (Various Sizes) | `StreambedRock…` strings are W03's |

- Palette keys `m034_*` (§5.4). Collection `Kit/M034 Streambed Section`. Socket names follow `K.socket`
  (`VFX_StreambedSection_water_flow_N`, `…_water_foam_N`).

**Decisions needed (a recommendation each):**
1. **Size and levels:** **tile 32 × 32, max z 8.0 ± 0.6; banks 1.6, water 1.0, bed top 0.7** (recommended: the
   terrain grid, the square top view, W03's bank and M032's waterline, a 0.3-deep stream), or the sheet's literal
   levels (water 1.3 over a bed at 1.0: a closer front cell, but a different waterline from W03, M032 and 037).
2. **Plan source:** **the top view governs the rocks and the channel; small nudges toward the hero (B2, M1)**
   (recommended: the only plan, and it keeps the tile chainable), or follow the hero (water at the front-left corner,
   the big pair at the front-right corner), which breaks the seam contract.
3. **Cameras for verification:** **`f34_sheet (35, 28)`, `r34_sheet (225, 32)`, `front_sheet (0, 5)`, `side_sheet
   (270, 5)`, `rear_sheet (180, 5)`, kit `top (0, 89)`**, all with the floor hidden for measuring; kit front34 /
   rear34 / front / side / rear / underside as self-consistency; extras `junc_cu (20, 22)`, `sect_cu (0, 12)` and a
   parts shot (35, 28) (recommended, §3).
4. **Tiling:** **record the §6 contract (14-wide channel centred at both seams, solid side walls) and leave chaining
   with W03's sloped `StreambedPatch` to a later transition piece** (recommended: the sheet's stepped slabs can't
   match W03's slopes), or force W03's 12-wide channel and bed 0.2 (the bed's grey seam face would then be 0.2 tall
   instead of the sheet's clear slab step).
5. **Parts:** **six: BankSlab, BedSlab, WaterPlane, RockLarge, RockMedium, RockSmall** (recommended: the sheet's
   parts breakdown and "Rocks are reusable pieces in various sizes"), or four with one `…Rocks` cluster part.
6. **Water, foam and flow:** **water shell `m034_water` (`kit_transparency` 0.3) over a deep-blue bed with light
   patches; a restrained foam mesh on `m034_water_foam` (`kit_transparency` 0.1); 3 `water_flow` beam sockets for the
   flow strips and 14 `water_foam` sockets** (recommended: matches M032's accepted foam decision and the sheet's "VFX
   overlay, rendered separately"), or sockets only for the foam too (the W03 rework; the foam bands, about 5 % of every
   view, would then be missing from still renders).
7. **Budget:** **4000 for the hero, planned at about 2700–3200** (recommended: STAGES).
8. **Stage 5:** **no emission or lights** (recommended: nothing glows).
9. **Hero packaging:** **one object: one closed land shell (banks, bed, every rock and pebble unioned), plus closed
   water and foam shells; `collision="precise"`** (recommended: no buried hidden faces, the exporter splits water by
   key, and a hull would box the stream in), or rocks kept as separate closed shells (cheaper booleans, but buried
   bottoms are hidden faces).
10. **Names** as proposed; keys `m034_*`.

## 9. Pitfalls to avoid (lessons from recent verifier failures written as targets)

1. **A rock pile instead of slabs and separate boulders** (021 round 1). The tile must read as **two flat sand slabs
   and a recessed bed slab**, with the boulders standing on them as **separate** forms. Targets: in `f34_sheet` the
   four big boulders and M1 / M2 are six distinct blobs (dark creases or sand / water between them); at least 1.5 studs
   between any two big / mid boulders in plan; rock covers 20–26 % of the top view (sheet 23.0 %), the six big / mid
   boulders 13–18 % of the top view (sheet 15.4 %); the bank side faces are straight and level along each whole tile side (front and side cells:
   slab band width 1.00 at h 0–.1).
2. **Lumpy or soccer-ball rocks** (023 round 1). "Clean, low-poly, flat shaded", "chunky": the big boulders have
   **big flat facets** (median facet area ≥ 1.2 sq studs on the four big ones; no facet under 0.15 sq studs except
   slivers at the base), **a flat crown** (faces with normal z > 0.9 cover ≥ 20 % of the rock's plan area, made of 3–5
   faces), **a broad base** (the bottom ring ≥ 0.9 of the max width, the widest point at 0.15–0.35 h), height
   0.85–0.95 × width; medium rocks 0.7–0.8, small 0.55–0.65. Irregular facets (vertex valence 3–9, not uniform
   pentagons); no `K.hull_rock` defaults, no vertex noise, no subdivision.
3. **Paint taken from shadowed areas.** Every calibration target in §5.4 is a median of an unshadowed region (the
   exploded and parts slab tops, the lit rock faces, the open water). Don't calibrate sand to the side faces, rock to
   the whole-rock median alone or to the swatch, or the water to the deep tone.
4. **Measuring wrong.** Measure floor-hidden renders with `measure_render.py`; treat any floor or floor shadow as
   background; check W : H, shares, the top profile and **width per height in every compared view, including
   `rear_sheet`, `side_sheet` and `r34_sheet`**, not only the hero.
5. **Comparing with the wrong camera** (§3): the hero is az 35 from the front-right (the kit front34 is front-left);
   the r34 is az 225 from the back-left (the kit rear34 is back-right); the side cell is from −X.
6. **A sloped W03-style riverbank.** The sheet is a stepped slab design: vertical slab faces, flat tops, a flat bed;
   no Delaunay slopes from the bank down to the bed, no lumpy sand.
7. **Foam baked into rocks or sand.** Foam is its own shell on `m034_water_foam`, 1.03 → 1.06, never on rock or sand
   faces; the export STATS shows 2 water pieces.
8. **Water that collides, z-fights or carries detail.** One flat water plane ("no baked details": no ripples, no
   stripes in the mesh); the flow strips are sockets; no face of the water coincides with the bed top or the bed's
   seam faces; the bed keys don't contain "water".
9. **Colour by facing.** Rock warm / cool and sand light / dark sides come from the light; paint only by position
   fields (§5.5); `K.check` facing correlation < 0.5.
10. **Breaking the tile:** a rock across a seam, a notch in the outer walls, the channel off-centre at a seam, or a
    bank top that isn't exactly 1.6 at the seams (§6).
11. **Hull collision on the hero** (§7.1): the tile would become a solid 8-stud box.
12. **Exact booleans:** union the slabs first, then rocks one at a time (largest first), keep water / foam out of the
    union, save between risky steps; `M.fix_bowties` after the unions.
13. **Naming clashes** (§8). Only one agent drives a Blender session at a time; no commits, pushes or exports in stage
    agents.

## Decisions (main session, 2026-10-29)

All recommendations are accepted:
1. A 32 × 32 tile, max height about 8.0 ± 0.6, with ground z 0, bed top 0.7, water top 1.0 and banks 1.6, sharing the waterline with W03, M032 and 037.
2. The top view governs the plan, with small nudges toward the hero. The study's known misses are recorded.
3. Cameras: `f34_sheet (35, 28)`, `r34_sheet (225, 32)`, `front_sheet (0, 5)`, `side_sheet (270, 5)`, `rear_sheet (180, 5)` and the kit top, plus `junc_cu`, `sect_cu` and a parts shot. The kit views are self-checks only.
4. Tiling: record the contract (bed and water X −7…+7 at both seams, solid bank side walls, no rock crossing an edge). Chaining with W03 waits for a transition piece.
5. Six parts as listed.
6. Foam: a thin foam mesh on `m034_water_foam`, plus 14 `water_foam` sockets and 3 `water_flow` sockets (+Y → −Y), as in M032.
7. Budget: 4000.
8. No emission or lights.
9. Packaging: one hero object with one closed land shell (rocks unioned in), plus closed water and foam shells, collision precise. This is the same water exception as M032. Every shell is manifold with 0 bowties, and the export shows 2 water pieces and 17 sockets.
10. Names: `StreambedSection*`, keys `m034_*`.
