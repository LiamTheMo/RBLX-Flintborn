# 032 Shoreline Corner — spec

Reference: `art/blender/assets/references/032.png`. The sheet's own title is "SHORELINE CORNER — INDIVIDUAL MODEL
STUDY", top right "FLINTBORN — WORLD MODELING CONCEPTS", top left "PAGE 33/132", footer "FLINTBORN — INDIVIDUAL MODEL
STUDY". INDEX.md row 32 calls it "Shoreline corner". The image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m032.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows water and foam** (§7); no glow, fire or particles.

Sheet text:
- **Header box:** "ENVIRONMENT ASSET — A riverbank shoreline corner with rocky cliffs, grass top and shallow water."
- **View labels:** "ASSEMBLED — FRONT THREE-QUARTER VIEW", "ASSEMBLED — REAR THREE-QUARTER VIEW", "ORTHOGRAPHIC VIEWS":
  "FRONT VIEW", "SIDE VIEW (RIGHT)", "REAR VIEW", "TOP VIEW". None of the "orthographic" cells is orthographic (§3).
- **Exploded labels:** "Grass Top (vegetation cluster)", "Dirt / Sand Strip (shore surface)", "Rock Slope (cliff
  pieces)", "Water Plane (+ Foam, separate)". Dashed drop lines and small dark pins mark the attach points.
- **Close-ups:** "1. CLIFF TO TOP JUNCTION" ("Flat joining surface between rock and top piece."; "Simple beveled edge, no
  noise."); "2. UNDERSIDE VIEW" ("Clean flat bottom surface."; "Simple blocky joining volumes."); "3. WATER PLANE DETAIL"
  ("Rocks sit on water plane."; "Foam is a separate flat mesh.").
- **Material palette:** Grass / Vegetation, Dirt / Sand, Rock (Cliff), Water Plane, Foam (Separate Mesh).
- **Modeling notes:**
  - "Style: chunky, low-poly, flat shaded, primitive forms."
  - "Keep broad, readable shapes and clean silhouettes."
  - "Use simple blocky cliff pieces that tile with other shoreline sections."
  - "Water plane and foam are separate meshes (do not bake foam into rocks)."
  - "Reusable parts: grass top, dirt/sand strip, rock slope pieces, water plane, foam."
  - "Maintain consistent geometry across all views."
  - "No photoreal textures or fine surface noise."
  - "Keep clean, solid colors and large flat faces in Flintborn style."
- **Game context and the old kit:**
  - **07 Terrain kit** (`build_07_terrain_kit.py`, `assets/07_terrain_kit.blend`, 32-stud grid, cliff and water sides
    face −Y): `CliffOuterCorner` 32×32×18, `CliffInnerCorner` 32×32×18, `Riverbank` 32×24×4, `RockyLakeshore`
    32×28×5. Water there is `water` / `water_deep` / `water_shallow` caps with a `foam` ribbon and foam tori round
    shore rocks, plus three `water_foam` sockets per water tile (`lib/vfx.py` lines 347–348).
  - **W03 Shorelines / Waterfalls / River** (`scripts/kit/W03/riverbank_chunk.py`, `shore_islet.py`,
    `streambed_patch.py`): `RiverbankChunk` with parts `RiverbankGrassTop`, `RiverbankSandStrip`,
    `RiverbankRockSlope`, `RiverbankWaterPlane` (wip export) or `RiverbankChunk*` (sheet export), and variants
    `…Straight`, `…InnerBend`, `…OuterBend`. The script's seam contract on a 32 × 32 tile: water z 1.0 over a riverbed
    at z 0.2, sand top 1.8 at the rock foot, grass top z 10.4 on a 0.8 soil band, shore at d = −7.5, grass rim at
    d = −0.4. **W03 revision 4 (user rework):** foam meshes were removed and replaced by `water_foam` sockets.
    `MODEL_PROGRESS.md` rows 52–55 flag W03 as "low flat cliff; sand thin; foam swirls" and "foam over-stylised". The
    exported `art/roblox/kit/W03/manifest.json` records a smaller `RiverbankChunk` (18.0 × 16.9 footprint, 12.1 high),
    so the kit file's W03 is not the 32-stud script build; which one is current is a main-session question (§8.4).
  - Later numbered sheets on the same subject: 041 "Shore Shelf", 161 "Shoreline wave and foam study". The contract
    recorded here (§6) is what they should join.

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The cell paper is
`#FDFAF2` (253, 250, 242), tolerance 14. The two hero cells have their titles painted out (`TITLES` in `m.py`). The
masks are `cls()` in `m.py` (HSV, h in degrees):
- **G, vegetation:** h 52–165, s ≥ 0.30, plus yellow flowers (h 40–52, s ≥ 0.55, v ≥ 0.75). Sub-masks in `samp4.py`:
  lawn h 60–100, bush leaves h 95–120, pine h 120–165.
- **S, sand / tan sides:** h 28–52, s 0.28–0.72, v ≥ 0.66 (beach, sand path, tan box and slab sides).
- **D, dark soil / bark:** h 10–45, s ≥ 0.30, v 0.18–0.66 (underside, trunks, crease dirt).
- **R, rock:** (s < 0.20, v 0.25–0.93) or (h 200–290, s < 0.45, v 0.20–0.86: the blue-violet shade faces) or (h < 28
  or ≥ 320, s < 0.30, v 0.25–0.93: the warm lit faces), not F.
- **W, water:** h 182–215, s ≥ 0.45, v ≥ 0.45.
- **F, foam:** h 165–225, s 0.03–0.45, v ≥ 0.86.
- **O, other:** outlines, deep crevices; not counted in the shares.
- Known leaks: white daisy petals fall into F or R (≤ 0.5 points); the darkest pine needles fall into O; the rock's
  shade faces stay R by design (the rock is one material lit warm/cool, §5.3).
- **The sheet draws no ground shadow** (the paper under every cell is clean `#FDFAF2`). Treat any render floor or
  shadow as background when measuring ours.

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m032_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Pillow + numpy).
- **Helpers:** `m.py` (masks `cls()`, view boxes `V`, exploded and close-up boxes `X`, `preview()`), `zoom.py` (crop +
  upscale), `grid.py` (10 % grids `g_*.png`, red = centre lines), `bb.json` (silhouette boxes).
- **Measurements:** `measure.py` → `measure_out.txt` (bbox, shares, top / bottom profiles, width per height);
  `cols.py` → `cols_out.txt` (per-column class extents); `topscan.py` → `topscan_out.txt` (top-view grass / sand / water
  extents per row, quadrant shares); `fit.py`, `fit2.py` (plan-proxy camera fits, `fit_*.png`).
- **Colour:** `samp.py` → `samp_out.txt` (swatches, view medians per class, exploded, close-ups); `samp2.py` →
  `samp2_out.txt` (hero regions: column faces, bevels, beach, path, lawn, pine, water, foam, box sides); `samp3.py`,
  `samp4.py` → `samp4_out.txt` (lawn / bush / pine split, flowers, part colours).
- **Names:** `blendall.py` → `blendall_out.txt` (every sheet, kit, checkpoint and wip `.blend`, zstd-decompressed).
- **Crops:** `f34.png`, `r34.png`, `views.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `cu.png`,
  `pal.png`, `z_f34_left.png`, `z_f34_right.png`; mask previews `cls_*.png`.
- **On our renders:** `measure_render.py <render.png> [paper_hex] [--flip]` prints the same bbox, shares, profiles and
  width per height with the study masks, so every number below can be checked on a render directly.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a modular terrain / shoreline piece with water. Hero budget 4000 tris (STAGES), each
  part under 1000. The plan in §4.3 lands at about 3300–3800; decision §8.7 asks whether a terrain hero may go to 6000
  (W03 heroes carried 8000).
- **Overall read (check this first).** A **raised grass-topped ridge** whose seaward side is a **row of big, fat,
  flat-faced grey cliff columns** with bevelled flat tops; the coast runs **straight along the front on the left, then
  turns about 45° and runs diagonally to the back-right** (the "corner"). At the cliff foot a **warm sand beach**
  widens in the middle and pinches out at both ends; in front of it **flat saturated cyan water** fills the front-right of
  the tile, edged by a **lumpy white foam ribbon**, with **faceted grey boulders** at the waterline and two standing in
  the water, each in a **foam ring**. On the ridge: lime lawn, a **sand path** along the cliff rim, three small
  **conifers**, fan-leaf **bushes**, white **daisies** and yellow flowers. At the left end, two **low blocky grass
  boxes** with tan sides sit at the cliff foot.
  - It must read as **one continuous ridge with separate columns**, not a rock pile, and the water as **one flat plane
    with a separate foam layer**, not foam painted on rocks.
  - Hero shares (f34): vegetation G 26.2 %, rock R 37.6 %, water W 19.6 %, sand S 8.6 %, foam F 2.2 %, soil D 1.6 %.
- **Focal silhouettes, in order:**
  1. The big front-left column C1 (f .26–.47, the nearest and widest, bevelled top at h .44–.49) and the column row
     stepping up to the back-right (tops h .48 → .58 → .75 → .80 → .82).
  2. The water's flat front edge and vertical right edge with the chamfered front-right corner; the big boulder in the
     water (f .58–.74) in its foam ring.
  3. The ridge's top outline: low at the left end (h .29–.46), rising along a diagonal back edge to h .86 at f .5, level
     to f .8, then down the right end (h .70 → .49); the pines break it at f .22–.32 and .46–.57.
- **Target size: tile 32 W × 26 D (bbox 32 ± 0.5 × 25 ± 1.5), ridge grass top z 10.4, pines to about z 17**
  (decision §8.1).
  - **How it was derived.** The kit terrain grid is 32 studs (WorldModeling §0, README sheet 07), and the W03 script
    tiles are 32 × 32 with the grass top at z 10.4. Inverting the hero at az 0 / e 32 with the sheet width as 32 studs
    (14.6 px/stud) gives: C1 column 6.7 wide and about 8.5 tall above the beach; the rim at the front-left C1 top and
    at C4 both at z ≈ 10.4 on one 45° line (two independent anchors agree, §2.2); pines 5.5–7 tall; the big water
    boulder 5.1 wide; the water's right edge reaching about 23 studs back from the front edge; the plateau's back edge
    about 20.7 back. The top view's aspect W : D = 1.253 gives D = 25.5. **D ≈ 26.**
  - **Against the character (5.5):** ridge top 10.4 = 1.9 C (an unclimbable cliff), cliff face 8.6 above the beach
    = 1.6 C, pines about 1–1.3 C (dressing pines, like W03's 6–7), C1 column 1.2 C wide, beach 3–5 wide (walkable),
    big water boulder about 0.9 C wide.
  - **Why this size.** It matches the W03 riverbank family's levels (water 1.0, bed 0.2, sand 1.8, grass 10.4), so the
    corner can join those straights (§6), and the old 07 shoreline tiles (32 × 24 and 32 × 28).
- **Build frame:** front −Y, +X right, ground z 0 = the underside of the land and the water slab's bed. Tile X −16 … +16,
  Y −13 … +13. Origin = the bbox bottom centre after stage 2 (the tile centre within ±0.5).

### 1.2 Measured views (`measure.py`)

| View (cell box) | Silhouette bbox (px) | W : H | G | R | W | S | F | D |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (16,142,508,480) | 32–498 × 150–470 | 1.455 | 26.2 % | 37.6 % | 19.6 % | 8.6 % | 2.2 % | 1.6 % |
| Rear three-quarter (517,142,1008,480) | 526–993 × 154–470 | 1.476 | 27.5 % | 47.2 % | 15.0 % | 1.8 % | 1.9 % | 1.5 % |
| Front (16,548,271,737) | 27–260 × 574–725 | 1.539 | 26.0 % | 40.1 % | 16.3 % | 5.3 % | 2.4 % | 2.1 % |
| Side (right) (275,548,495,737) | 288–484 × 562–725 | 1.201 | 16.6 % | 53.5 % | 16.5 % | 0.1 % | 2.3 % | 0.4 % |
| Rear (514,548,768,737) | 514–756 × 562–725 | 1.482 | 26.3 % | 57.5 % | 4.4 % | 2.3 % | 1.2 % | 1.8 % |
| Top (772,548,1008,737) | 785–997 × 556–725 | 1.253 (W : D) | 36.5 % | 9.4 % | 34.5 % | 10.3 % | 4.5 % | 1.2 % |

O (outlines, not counted) is 3.5–10.6 %. **Verifier tolerance:** shares ±4 points (S, F, D ±2); positions ±0.06 of
W / H unless stated.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .29 | .46 | .57 | .61 | .63 | .79 | .78 | .75 | .82 | .83 | .97 | .91 | .86 | .90 | .90 | .83 | .81 | .70 | .67 | .52 | .49 |
| r34 | .40 | .45 | .50 | .59 | .68 | .71 | .72 | .78 | .76 | .80 | .87 | .91 | .82 | .79 | .86 | 1.0 | .84 | .71 | .67 | .49 | .25 |
| Front | .29 | .51 | .61 | .69 | .68 | .83 | .94 | .95 | .77 | .87 | .86 | .83 | .89 | .96 | .95 | .89 | .83 | .83 | .76 | .60 | .40 |
| Side | .28 | .29 | .37 | .37 | .43 | .51 | .50 | .39 | .42 | .68 | .72 | .79 | .79 | .79 | .93 | .98 | .85 | .77 | .69 | .54 | .20 |
| Rear | .26 | .69 | .75 | .77 | .80 | .85 | .88 | 1.0 | .86 | .80 | .79 | .72 | .75 | .89 | .84 | .67 | .69 | .58 | .44 | .37 | .19 |

The peaks at f34 .50 (.97), .25 (.79), r34 .75 (1.0), rear .35 (1.0) and side .75 (.98) are pine tips. The ridge line
without pines is the f34 envelope .29 → .63 (f 0–.2), .75–.83 (f .3–.45), .86–.90 (f .55–.7), .83 → .49 (f .75–1.0).

**Bottom profiles** (lowest silhouette pixel):

```
f34    .22 .19 .17 .13 .10 .07 .04 .01 .00 .00 .00 .00 .00 .00 .00 .00 .00 .00 .02 .07 .11
r34    .17 .15 .11 .08 .05 .02 .00 .00 .00 .00 .00 .00 .00 .03 .06 .08 .12 .13 .16 .20 .22
front  .20 .15 .12 .09 .05 .02 .00 .00 .00 .00 .00 .00 .00 .00 .00 .00 .00 .02 .05 .07 .09
top    .02 .01 .01 .00 .00 .00 .00 .00 .00 .00 .00 .00 .00 .00 .00 .00 .00 .02 .07 .12 .18
```
- f34: flat (the water's front edge, screen-horizontal) from f .40 to .85; the front-right **chamfer** f .85–1.0
  (.02 → .11); the front-left **rises** to .22 at f 0 (the low boxes' front faces run diagonally back to the left: the
  front-left corner of the tile is empty).
- top: the same chamfer at the front-right (.02 → .18 over f .85–1.0); the front-left corner is full (sand, a rock and a
  sliver of water).

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .52@.39 .79@.24 .97@.06 .99@.04 .97@.06 .92@.10 .80@.15 .64@.24 .57@.29 .22@.51 .01@.55
r34    .33@.29 .68@.13 .95@.02 .98@.02 .97@.02 .87@.10 .77@.18 .68@.24 .36@.45 .24@.56 .01@.76
front  .55@.32 .88@.17 1.0@.05 1.0@.05 .97@.07 .93@.09 .86@.14 .75@.21 .64@.29 .47@.34 .01@.37
side   .87@.07 .99@.07 .99@.07 .91@.12 .76@.26 .72@.29 .49@.51 .43@.53 .28@.59 .09@.76 .01@.80
rear   .81@.00 1.0@.00 .99@.00 .95@.01 .91@.02 .86@.02 .79@.04 .67@.06 .50@.20 .36@.32 .01@.34
```

**Per-column class extents** (`cols.py`, f34; h from the bottom): water/foam spans h 0 → .16–.27 at f .50–.70 and
0 → .48–.52 at f .85–1.0 (the right edge); sand (beach) h .20–.29 → .69–.84 at f .50–.80; rock from the boulders' feet
up to the column tops (.64–.97 with the ridge's back cliff); vegetation from h .45–.65 up to the ridge line.

**Top view rows** (`topscan.py`; v = depth from the back, 0 → 1; fractions of W):

| v | .05 | .25 | .40 | .50 | .60 | .70 | .80 | .85 | .95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| grass to | .72 | .66 | .52 | .38 | .26 | .35 | .20 | .12 | — |
| sand | .73–.74 | .46–.68 | .40–.65 | .05–.61 | .21–.48 | .20–.35 | .19–.24 | .00–.22 | — |
| water from | .76 | .83 | .69 | .68 | .52 | .45 | .38 | .26 | .05 |

Quadrant shares: back-left G 89 % / S 7 %; back-right W 43 / G 22 / R 14 / S 10; front-left G 31 / S 23 / W 21 / R 11;
front-right W 77 / R 13. The shoreline is a diagonal from the back edge at x .76 to the front-left corner, with water
along the whole right edge and the whole front edge.

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, governs; `g_f34.png`).** Not a 45° iso view of an axis-aligned tile: the water slab's
front edge is screen-horizontal and its right edge screen-vertical with a chamfer between (`z_f34_right.png`), which only
a camera at **az ≈ 0** gives; the land is aligned to the 45° coast, so its blocks look isometric. The plan-proxy fit
(`fit2.py`) puts the camera at **az 0 … +5, e 24–44** (the score barely depends on e); the cliff-foot slope (screen
.59) with a 45° coast gives **e ≈ 32–36**; the chamfer slope gives 40–50. Use **e 32** (§3.1). The sheet is drawn with
some perspective (near columns larger: C1 .21 W against C4 .12 W).
- **Columns (front row), left to right:** C0 f .07–.27, top h .50–.52 (the left end, set back, face toward the
  front-left); a low boulder L1 in front of it f .12–.24, h .12–.28; **C1** f .26–.47, bevelled top h .44–.49, foot
  h .12–.18 (the biggest); C2 f .43–.56, top .58, foot .30; C3a f .53–.64, top .75, foot .45; C3b f .64–.70, top .73;
  C4 f .69–.82, top .78–.80, foot .55; C5 f .79–.85, top .82 (the right end). Dark vertical creases separate them; a
  tan sand-filled gully at f .24–.27, h .30–.48 between C0 and C1.
- **Ridge top:** lime lawn; a **sand path** on top along the rim from f .40 (h .58) to f .72 (h .78), about 0.08 W wide;
  pines P1 f .46–.57, h .78–1.0 (back), P2 f .20–.32, h .55–.84 (left, the tallest), P3 f .02–.11, h .27–.48 (on the
  left low box); bushes along the rim and at the right end (f .83–.92, h .55–.66); daisies (5–6 large white) and yellow
  flowers; three small pale rocks on the lawn (f .30, .70, .73 at h .55–.85).
- **Low boxes:** B1 f .00–.11, top h .30, front face h .16–.30 (tan sides, grass top, P3 on it); B2 f .20–.31, top h
  .17, front face h .05–.17 (a bush on it).
- **Beach:** sand from f .38 (h .10) to f .80 (h .74), widest at f .55–.70 (h .27–.75 including its slope up to the
  column feet); pebbles and two small rocks on it (f .53–.58 h .30–.36; f .57–.64 h .38–.48).
- **Water:** f .30–1.0, the right edge up to h .48–.52; the foam ribbon follows the shore 10–25 px wide with round
  holes; the front edge shows a thin slab side (about 4 px).
- **Boulders at / in the water:** W2 f .32–.40, h .02–.16; W3 f .43–.50, h .17–.27; **W1** (big, in the water) f
  .58–.74, h .03–.27; W4 f .74–.80, h .20–.27; W5 (tiny) f .78–.80, h .13–.16; W6 (big, waterline right) f .75–.86,
  h .40–.55; W7 f .81–.87, h .57–.63; W8 f .88–.93, h .58–.66. Each one in or touching the water sits in a foam ring.

**Front (`g_front.png`).** The hero again at a lower elevation (W : H 1.539 against 1.455): profile mean difference
.072 against the hero's (.102 mirrored), shares within 2.7 points, the same columns, boxes and boulders.

**Rear three-quarter (`g_r34.png`).** A camera **behind** (az ≈ 180, e ≈ 30): water along the left (screen left = +X,
the right-edge water), the ridge's **back cliff** facing the camera along its whole length (7–8 columns, tops h
.55–.75), a low box with a bush at the bottom right (B2-type, at the left end seen from behind), two pines on top. Its
profile is closer to the hero unmirrored (.061) than mirrored (.104): both are elevated views of a ridge rising to the
right of centre; the water side decides the camera (§3.2).

**Rear (`g_rear.png`).** The same back cliff at a lower elevation: 5 columns (f .00–.28, .27–.47, .43–.57, .58–.85,
.85–.90), tops h .52–.70, feet at h .00–.05 (the back cliff reaches the ground); water only at the lower left (f 0–.5,
h 0–.15, rock share 57.5 %, water 4.4 %); a low box with a pine at the right end (f .85–1.0, h .08–.38) = B1 + P3 seen
from behind; two pines on top.

**Side (right) (`g_side.png`).** The kit side camera at +X (az 90; screen left = front, screen right = back): water
with three boulders on the left (f 0–.45), the ridge's right end on the right (columns f .45–.90 up to h .79–.98 with
the pine), the cliff reaching the ground at the far right. W : H 1.20 (the tile's depth seen end-on, with the ridge's
height).

**Top (`g_top.png`; image top = back).** A rectangle W : D 1.253 with the front-right corner chamfered. Grass fills the
back-left; a diagonal sand band from the back edge (x .62–.74) to the front-left corner; water fills the right and
front, with the waterline from x .76 at the back to x .05 at the front; 6 grey boulders along the waterline, 2 in the
water (the big one at (.62, .75), one at (.78, .47)), each in a foam ring; a large pine crown at the top-left (.15, .25),
4 daisies. **The cliff columns don't show as columns**: only small grey tops at the grass edge (.55, .35), (.37, .55),
(.58, .12) (§3.4).

**Close-ups.**
- **1. Cliff to Top Junction** (655,812,868,958): two columns; the grass top sits as a slab on their **flat bevelled
  tops** ("Flat joining surface"), with a thin turf lip and daisies; the columns' faces are big flat facets, edges
  chamfered once ("Simple beveled edge, no noise"); a fan bush in the crease between them.
- **2. Underside View** (655,996,868,1116): a land slab from below: **flat brown bottom** (`#936631`) inside a tan side
  band (`#C69B51`), grass tufts poking over the top edge; a few shallow darker rectangles on the bottom ("Simple blocky
  joining volumes": the blocks that make up the slab).
- **3. Water Plane Detail** (655,1154,868,1270): one boulder standing on the water plane, its foot ringed by a flat
  **foam ring** with round holes, loose foam blobs around; "Rocks sit on water plane"; "Foam is a separate flat mesh".

### 1.4 Parts (Exploded Construction (14,745,638,1282), `expl.png`)

The exploded parts are drawn in the same isometric look as the hero, at a slightly larger scale. **The hero governs every
size**; the exploded gives the part list, the shapes and the slab language.

#### Grass Top (vegetation cluster): about (83,770,402,932)

- **Shape:** a long, stepped **slab** (wider at its left/back part, a step down in width toward the right) with straight
  cut ends and straight long edges; thickness about 0.8 (a green-sided slab with a brown soil line); on top: the lime
  lawn, a dirt patch where the sand path runs, one pine (left), fan bushes, daisies, yellow flowers, two small pale
  rocks.
- **Hero part:** the ridge's top: the ridge polygon (§2.2) at z 9.6–10.4 (turf over a 0.8 soil band), with all its
  dressing (P1, P2, bushes, flowers, lawn rocks). The cut ends at the tile edges are flat (joining faces).
- **Construction:** `_grass_top()`: a Delaunay cap of the ridge polygon (spacing about 2.0, z jitter ≤ 0.05), a soil
  band skirt 0.8 deep with a lumpy lip overhanging the rim 0.2–0.4, a sand path ribbon (2.4 wide) along the rim from
  (−1, −3) to (8, 6.5); dressing from the shared vegetation helpers.

#### Dirt / Sand Strip (shore surface): about (160,867,420,990)

- **Shape:** a long, flat sand **plank slab** in two stepped segments (tile-like crack lines, a few darker dents), tan
  sides; it is the beach.
- **Hero part:** the beach between the column feet and the waterline, z 1.8 at the cliff foot sloping to 1.0 at the
  water (and on under the water to the bed at 0.2, painted bed colour below z 1.0), 3–5 wide in the middle, pinching out
  at the left (f .38) and the right end (f .80).
- **Construction:** `_sand_strip()`: a cap between the cliff-foot and waterline polylines (§2.2), z by distance to the
  waterline; a short skirt where it meets the tile edge; 2–3 crack grooves are not modelled (no fine noise); 4–6
  pebbles.

#### Rock Slope (cliff pieces): about (40,925,465,1265)

- **Shape:** **five big columns** (four in a back row, tops level, one shorter in front), each an 8–10-sided prism with
  **big flat side faces**, a slight bulge, a once-chamfered rim and a **broad flat top** (the junction close-up); plus
  about **eleven small rocks** (squat faceted domes, flat bottoms, 0.8–2 wide) and two larger boulders.
  Column screen proportions: width : height about 0.8–0.9 with the top included.
- **Hero part:** the front column row C0–C5 (+ L1) and the back-cliff columns, and the shore boulders.
- **Construction:** `_column(w, d, h, seed, yaw)`: superellipse rings (8–10 points, exponent 2.6–3) at 3 heights (foot
  1.05 R, middle 1.0, shoulder 0.96), a chamfer ring 0.25–0.35 in and 0.35–0.5 down from a **flat top** (the bevel),
  ring centres offset ≤ 0.15, radius jitter by broad sectors ±4 %; flat bottom. About **60–90 tris** each. W03's
  `riverbank_chunk.py` column recipe ("hulls of 8-sided superellipse rings with a big, fairly flat top chamfer") is the
  model to copy; do not use `K.hull_rock` (it gives lumpy boulders, not columns).
  `_boulder(w, seed)`: `K.pebble`-style rings with `keep_bottom=True`: about 36 tris.

#### Water Plane (+ Foam, separate): about (190,1070,585,1250)

- **Shape:** a **flat rectangular slab** of saturated cyan (top `#06DBFE`), side faces about 0.6 tall, with two boulders
  standing on it, each in a white **foam ring** with round holes, a few loose foam blobs.
- **Hero part:** the water region (§2.2): the slab top at z 1.0 to the tile's front and right edges and the front-right
  chamfer, its sides down to the bed at z 0.2; under it a bed surface (z 0.2) that the beach slopes into.
- **Foam:** a separate flat mesh 0.04 above the water: the shore ribbon (0.8–1.5 wide, wavy, with 4–8 round holes per
  10 studs) and a ring round each boulder in the water (0.4–0.6 wide), plus 6–10 loose blobs (0.3–0.6). Never on the
  rocks.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0). Tile X −16 … 16, Y −13 … 13. Hero screen ↔ plan, used for the
values below: orthographic az 0, e 32, 14.6 px/stud, the water's front edge at Y −13, z 1.0 → h 0:
`Y = −13 + (22.0·h − 0.848·(z − 1)) / 0.530`, `X = −16 + 32·f`. The sheet is a perspective drawing, so these are
starting values: **the screen targets in §2.5 govern.**

### 2.1 Levels (the tile contract, from W03)

| Level | z | Notes |
| --- | --- | --- |
| Ground / underside | 0 | flat bottom of the land and of the water bed ("Clean flat bottom surface") |
| Bed under the water | 0.2 | bed key below the water |
| Water surface | 1.0 | `m032_water`; slab sides 0.2 → 1.0 |
| Foam | 1.04 | `m032_water_foam`, never coplanar with the water |
| Beach | 1.0 → 1.8 | waterline → cliff foot |
| Low boxes | top 2.4 | tan sides, grass top |
| Ridge grass top | 10.4 | turf over a soil band 9.6–10.4 |
| Column tops | 8.8–10.4 | bevelled flat tops, some a step below the turf (C0, C2, C3) |
| Pines | to about 17 | |

### 2.2 Plan polylines

| Line | Points (X, Y) | Sheet evidence |
| --- | --- | --- |
| Ridge front rim (cliff top, seaward) | (−16, −5) → (−8, −6) → (−4.2, −7.7) → (8.3, 4.8) → (10.5, 7) | C1 top h .49 at f .37 → (−4.2, −7.7); C4 top h .79 at f .76 → (8.3, 4.8): one 45° line `Y = X − 3.5`; the left part runs along the front |
| Ridge back edge | (−16, −2) → (−9.6, −1.5) → (−6.4, 2.3) → (−0.6, 7.7) → (9.3, 7.7) → (11, 8.5) | hero back edge h .62 at f .20, h .73 at f .30, h .86 level from f .48 to .79 |
| Column feet (seaward) | the rim pushed 1.5–2.5 seaward | foot h per column (§2.3) |
| Waterline (shore) | (−4, −13) → (−3, −9.7) → (2, −3.5) → (6, 2) → (9, 7.8) → (12, 10.5) → (12.5, 13) | sand/water boundary h .08 at f .40, h .50 at f .78; top view x .76 at the back |
| Water extent | waterline → the front edge (Y −13), the right edge (X 16), the chamfer (11, −13) → (16, −8) | top view chamfer f .85–1.0, .02 → .18; hero right edge to h .50 |
| Low ground / boxes front | (−16, −3) → (−6.5, −11) → (−4, −13) | hero bottom profile .22 at f 0 → .00 at f .40 |

- **Front-left corner:** empty in front of the low-box line (the hero's bottom-left rises to h .22); the top view shows
  sand and a rock there (§3.4). **Back-left corner:** behind the ridge's back edge the tile is empty except the back
  cliff's feet and B1 (decision §8.2).
- **Ridge:** about 4–5 wide (perpendicular) at the left end, 10–11 in the middle (X −4 … 4), 3–4 at the right end;
  its back side is a second row of columns down to the ground (rear view), its left end steps down (C0, top about 9).

### 2.3 Columns (front row; yaw: the broad face faces the water normal, (+1, −1)/√2 for the diagonal part)

| Column | Centre (X, Y) | Footprint w × d | Top z | Yaw | Hero target (f; top h; foot h) |
| --- | --- | --- | --- | --- | --- |
| C0 (left end) | (−11, −5.5) | 5.5 × 4.5 | 9.0 | −15° | f .07–.27; .50–.52; hidden by L1 / B1 |
| L1 (foot boulder) | (−10.5, −8.5) | 3.6 × 3.2, h 3.0 | 4.0 | — | f .12–.24; .28; .12 |
| C1 (big, front-left) | (−4.5, −9) | 6.7 × 5.0 | 9.8 | −10° | f .26–.47; .44–.49; .12–.18 |
| C2 | (0, −4.8) | 4.5 × 4.0 | 9.6 | −40° | f .43–.56; .58; .30 |
| C3a | (3, −1.8) | 4.5 × 4.0 | 10.0 | −45° | f .53–.64; .75; .45 |
| C3b | (5.6, 1.2) | 3.5 × 3.5 | 9.8 | −45° | f .64–.70; .73; .45 |
| C4 | (8.2, 4.0) | 5.0 × 4.2 | 10.6 | −45° | f .69–.82; .78–.80; .55 |
| C5 (right end) | (10.6, 6.6) | 3.5 × 3.5 | 10.2 | −50° | f .79–.85; .82; hidden |
| Back row (5) | along the back edge line, 1.5 behind it | 4.5–6 × 4 | 9.8–10.4 | +135° | rear cell 5 columns, tops h .52–.70, feet at the ground |

- Columns overlap their neighbours 0.3–0.6 and sink 0.3 into the beach / ground; their tops sit flush with or a
  0.4–1.4 step below the turf (the junction close-up: the grass slab rests on the flat tops).
- **Creases:** each pair of columns leaves a dark V crease (O mask) running full height; the C0/C1 crease is filled with
  a tan sand gully (f .24–.27).

### 2.4 Low boxes, boulders, vegetation

| Item | Centre (X, Y), base z | Size | Hero target |
| --- | --- | --- | --- |
| B1 low box + P3 pine | (−14.3, −4.5), 0 | 3.4 × 3.4 × 2.4 | f .00–.11, top h .30, front face .16–.30 |
| B2 low box + bush | (−8, −9.5), 0 | 3.5 × 2.6 × 2.4 | f .20–.31, top h .17, front face .05–.17 |
| W1 big boulder in the water | (5, −9.5), 0.2 | 5.0 × 4.5 × 4.0 | f .58–.74, h .03–.27 |
| W2 waterline | (−4.5, −11.3), 0.2 | 2.6 | f .32–.40, h .02–.16 |
| W3 beach front | (−1.5, −7.5), 0.8 | 2.2 | f .43–.50, h .17–.27 |
| W4 in the water | (9, −5), 0.2 | 1.8 | f .74–.80, h .20–.27 |
| W5 in the water | (9.5, −8), 0.2 | 0.8 | f .78–.80, h .13–.16 |
| W6 big, waterline right | (10.8, 3), 0.2 | 3.6 × 3.4 × 3.2 | f .75–.86, h .40–.55 |
| W7, W8 right end | (12.4, 9), (14.2, 10.5), 0.2 | 1.8, 1.6 | f .81–.87 / .88–.93, h .57–.66 |
| Beach rocks | (1.5, −1.5), (3.5, 1.5), 1.4 | 1.3, 1.8 | f .53–.58 h .30–.36; f .57–.64 h .38–.48 |
| Pebbles | 4–6 on the beach | 0.4–0.7 | |
| P1 pine (back) | (1.5, 6.5) on the ridge | 5.5 tall, crown Ø 3 | f .46–.57, top h 1.0 |
| P2 pine (left, tallest) | (−8.5, −1.5) on the ridge | 6.8 tall, crown Ø 3.6 | f .20–.32, h .55–.84 |
| P3 pine (on B1) | on B1 | 5.0 tall | f .02–.11, h .27–.48 |
| Bushes | 8–10: along the rim, at the right end, on B2, in the C0/C1 crease | 1.2–2.2 | fan bushes of 6–9 broad leaves |
| Daisies / yellow flowers | 5–6 large daisies (Ø 0.8–1.0), 10–14 small yellow flowers | | |
| Lawn rocks | 3 small pale rocks on the ridge | 0.6–0.9 | f .30, .70, .73 at h .55–.85 |

- **Boulders sit on the water plane** ("Rocks sit on water plane"): the ones in the water stand on the bed at z 0.2
  and rise through the water surface; their part below z 1.0 is painted bed colour (W03's `submerge`). Each gets a foam
  ring.

### 2.5 Screen targets (`f34_sheet (0, 32)` render against the hero, `measure_render.py`)

- W : H 1.40–1.52 (sheet 1.455); shares within ±4 (S, F, D ±2) of G 26.2 / R 37.6 / W 19.6 / S 8.6 / F 2.2.
- Top profile within ±0.08 at every f (the pine tips ±0.1); bottom profile within ±0.05; width per height within ±0.08.
- Column targets per §2.3 (±0.05 f, ±0.06 h); 6 front columns plus C0 readable with dark creases between them.
- Water: f .30–1.0 at the bottom, the right edge to h .48–.55, the chamfer at f .85–1.0; boulders per §2.4 (±0.06).

## 3. View conflicts and resolutions

### 3.1 The "front three-quarter" is an elevated front view of a 45° coast

- **Evidence.** The water's outline (flat front edge, vertical right edge, chamfer) is the top view's outline seen from
  the front; the bottom profile is flat across f .40–.85. A 45° iso camera on an axis-aligned tile gives a 2.3 : 1 tile
  and a slanted water front, which the sheet doesn't show. The plan proxy (`fit2.py`) scores best at az 0 … +5.
- **Resolution.** Compare the hero with an extra **`f34_sheet (0, 32)`** and the front cell with **`front_sheet (0,
  26)`**. The kit front34 (−28, 12) and front (0, 4) are self-consistency only. The land blocks must be aligned to the
  45° coast so they read isometric from the front.

### 3.2 The rear three-quarter and rear cells are real views from behind

- **Evidence.** Both show the water on the left, which from behind is +X, where the top view puts the right-edge water;
  both show the ridge's back side as a full cliff row reaching the ground; the rear cell's pine box at the right end is
  B1 + P3 seen from behind.
- **Resolution.** Compare with **`r34_sheet (180, 30)`** (shares ±5, water on the left, back cliff columns 6–8) and
  **`rear_sheet (180, 18)`** (5 back columns, water only at the lower left, W share 3–7 %, the box with a pine at the
  right end). Don't flip the hero for the r34.

### 3.3 The side cell is the kit side camera

- From +X (az 90), screen left = front: water with boulders on the left, the ridge's right end on the right. Compare the
  kit **`side (90, 12)`** with the side cell: shares ±5, water on the left 40–50 % of the width, the cliff reaching the
  ground at the right. W : H may read up to +20 % (the cell is a perspective drawing).

### 3.4 Top view against the hero

- **Evidence.** The top view's land reaches the back-left corner, the grass edge runs 4–6 studs further seaward than
  the hero's rim, the columns show only as small grey tops, and its front-left corner is sand with a rock. The hero
  shows an empty back-left (behind the ridge) and an empty front-left (in front of the low boxes): at az 0 / e 32,
  land at z ≥ 1 in either corner would show above h .55 at f 0 or below h .22, and the sheet shows paper there.
- **Resolution.** **The hero governs the footprint** (decision §8.2). Compare the kit **`top (0, 89)`** with the top
  cell by: W : D 1.20–1.35, the front-right chamfer, the diagonal sand band from the back edge (x .60–.80) to the
  front-left, water along the right and front edges, 6–8 boulders in foam rings, and the pine crowns at the back-left.
  Record the empty back-left and front-left corners and the column tops as known misses.

### 3.5 Exploded and close-ups against the hero

- The exploded parts are drawn about 1.2–1.5× larger and in a cleaner arrangement (four columns in a row plus one in
  front). The hero governs sizes and placement; the exploded gives the slab language: **the grass top and the sand
  strip are thick flat slabs with straight cut edges**, the columns are prisms with flat tops, the water is a flat slab.
- The exploded water plane is a plain rectangle; the hero's water is the tile's front-right region. Build the hero's
  water to the region; the `…WaterPlane` part is the hero's water slab (decision §8.5).

### 3.6 Foam: mesh (sheet) against sockets (W03 precedent)

- The sheet says twice that foam is a **separate flat mesh**; the user replaced W03's foam meshes with `water_foam`
  sockets because they read over-stylised. **Resolution (recommended):** both. A restrained flat foam mesh (broad
  ribbon and rings, WorldModeling §12.3: "a few broad strips or rings rather than dense realistic particles") on its
  own water-type key, so it exports as a separate see-through, non-colliding piece, plus `water_foam` sockets for
  motion (§7.2, decision §8.6).

### 3.7 "Solid colors, large flat faces" against the user's blended-colour rule

- The sheet is close to flat: one lime, one sand, one warm grey, one cyan, one foam white. The rock's warm-lit / cool
  shade split (lit `#E4D6D2` h 11°, shade `#6A6E8A` h 232°) is lighting, never paint. Paint only gentle position-based
  blends (§5.5): contact darkening, a slightly paler dry beach band, broad lawn patches.

## 4. Construction plan (stages 1–3)

1. **Parts first,** each from its own function, checked against its exploded cell:
   - `grass_top()` → `ShorelineCornerGrassTop`: the ridge slab (turf, soil band, lip, sand path) with P1, P2, bushes,
     flowers, lawn rocks. Compare with the exploded Grass Top (stepped slab, straight cut edges, pine at the left).
   - `sand_strip()` → `ShorelineCornerSandStrip`: the beach slab. Compare: a flat plank-like strip, tan sides.
   - `rock_slope()` → `ShorelineCornerRockSlope`: the front column row C0–C5 + L1 and the shore boulders on it (as
     drawn in the exploded). Compare: separate fat flat-faced columns with flat bevelled tops.
   - `water_plane()` → `ShorelineCornerWaterPlane`: the water slab + bed (water and bed keys only).
   - `foam()` → `ShorelineCornerFoam`: the foam mesh alone.
   - Render a parts shot (`extra`, about (−20, 25)) laid out like the exploded.
2. **Hero** `ShorelineCorner`:
   1. Paste (m011 `_paste` pattern) the ridge core (a prism of the ridge polygon from z 0 to 9.6 hidden inside the
      columns), the front and back column rows, the grass top, B1, B2, the sand strip, the boulders and the vegetation.
   2. **Land shell:** exact self-union of the rock and land pieces only (add pieces one at a time; save between risky
      steps), then `union_loose`, then floor-cut at z 0. Vegetation may stay as separate closed shells in the same
      object (pines, bushes, flowers), as on previous models.
   3. **Water and foam:** joined into the same object as **separate closed shells**, never unioned with the land:
      water slab (top z 1.0, sides to 0.2) cut around the boulders and the beach slope (or simply under them: the
      beach and boulders rise through it), the foam shell 0.04 above the water.
   4. Origin at the bbox bottom centre; transforms applied.
3. **Budget** (§4.3): hero about 3300–3800 (limit 4000); each part under 1000. If over, drop flowers and bushes first,
   never column sides (≥ 8) or the bevel ring.
4. **Placeholder keys** (stage 1): `m032_grass`, `m032_soil`, `m032_sand`, `m032_rock`, `m032_water`,
   `m032_water_foam`, `m032_bed`, `m032_pine`, `m032_bark`, `m032_leaf`, `m032_petal`, `m032_pollen`.
5. **Stage 1 acceptance** (render, compare every view, measure with `measure_render.py`):
   1. **Overall read:** one continuous ridge with separate fat columns (creases, flat bevelled tops), the coast turning
      45° from the front-left to the back-right, a sand beach widening in the middle, a flat cyan water plane with a
      separate foam ribbon and rings, boulders standing in the water.
   2. **`f34_sheet (0, 32)`:** the §2.5 targets.
   3. **`front_sheet (0, 26)`:** W : H 1.48–1.60, shares ±4 of the front cell.
   4. **`r34_sheet (180, 30)`, `rear_sheet (180, 18)`, `side (90, 12)`:** §3.2–§3.3.
   5. **`top (0, 89)`:** §3.4.
   6. **Kit views** (front34, rear34, front, side, rear, underside): self-consistency; the underside shows one flat
      bottom (land) and the water slab's flat bed.
   7. **Parts against their cells;** the junction extra `junc_cu (−30, 15)` framed on C2/C3 against close-up 1 (flat
      tops under the grass slab), and `water_cu (−25, 35)` on W1 against close-up 3 (ring with holes, foam flat).
   8. **Size:** bbox 32 ± 0.5 × 25 ± 1.5, ridge top 10.4 ± 0.2, max z 16–18 (pines).
6. **Stage 2:**
   - zero non-manifold edges and vertices (bowties: `M.fix_bowties`), boundary, wire and loose elements; no zero-area
     faces or n-gons; normals outward; no interior faces from the unions (the hidden ridge core must be fully swallowed
     or removed);
   - no faces under 5° where columns meet columns, the turf, the beach and the ground;
   - the water and foam shells are closed and stay separate from the land shell; no foam face within 0.02 of a water
     face.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even density. (The exporter writes palette UVs for solid faces
   and its own box-projected UVs for water pieces; the UV layer must still exist and be clean.)

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Front columns C0–C5 (8–10 sides, 3 rings + bevel) | 7 | 80 | 560 |
| Back columns | 5 | 70 | 350 |
| Grass top (cap + soil band + lip + path ribbon) | 1 | 380 | 380 |
| Sand strip (cap + skirt) | 1 | 150 | 150 |
| Low boxes B1, B2 (bevelled boxes, grass top) | 2 | 40 | 80 |
| Boulders W1–W8, L1, beach rocks, lawn rocks | 14 | 36 | 504 |
| Pebbles | 5 | 12 | 60 |
| Water slab + bed | 1 | 120 | 120 |
| Foam ribbon + 4 rings + blobs | 1 | 320 | 320 |
| Pines P1–P3 (4-tier star cones + trunk) | 3 | 110 | 330 |
| Bushes (6–9 broad leaves) | 9 | 50 | 450 |
| Daisies + yellow flowers | 18 | 12 | 216 |
| **Sum before union** | | | **about 3500** |
| **Hero after the land union** | | | **about 3600–3900** (limit 4000) |
| Parts: GrassTop / SandStrip / RockSlope / WaterPlane / Foam | | | about 900 / 150 / 950 / 120 / 320 (limit 1000) |

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 36 × 18 box inside each, x 40–76)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Grass / Vegetation | (40,1322,76,1340) | `#9ECE2D` | 77°, 0.78, 0.81 |
| Dirt / Sand | (40,1355,76,1373) | `#E7B670` | 35°, 0.52, 0.91 |
| Rock (Cliff) | (40,1389,76,1407) | `#A09CA6` | 264°, 0.06, 0.65 |
| Water Plane | (40,1422,76,1440) | `#00C5FE` | 193°, 1.00, 1.00 |
| Foam (Separate Mesh) | (40,1456,76,1474) | `#D0FCFE` | 182°, 0.18, 1.00 |

- **Grass:** the lit lawn renders yellower and a little brighter (`#A7CE09`, h 71°, s .96) than the swatch.
- **Dirt / Sand** is one swatch for two things that render differently: the **beach / sand strip** (`#FBCF83`, much
  lighter) and the **tan slab sides** (`#B98745`); the slab **underside** is a darker brown (`#936631`).
- **Rock:** the swatch is a cool neutral grey; **every rendered rock is warmer** in its lit faces (h 5–15°, s .11–.14)
  and blue-violet in its shade faces. Calibrate on the renders.
- **Water / Foam:** the swatches match the renders within a few levels.

### 5.2 Rendered regions (`samp*.py`; median / lit quartile / shade quartile)

| Region | Box / mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- |
| Lawn, exploded grass top (unshadowed) | (83,770,402,932) G h 60–100 | `#A7CE09` | `#BAE11B` | `#417202` |
| Lawn, hero / top view | V G h 60–100; (838,615,872,640) | `#9FC904` / `#A3CC03` | `#BCE40C` | `#366502` |
| Pine, hero / exploded | G h 120–165 | `#07692D` / `#066A2A` | `#24B342` / `#25AB3F` | `#013112` |
| Bush leaves (dark side) | G h 95–120 | `#1B5A03` / `#196002` | `#368D0A` / `#349C14` | `#0B2F01` |
| Yellow flowers | hero h 40–58, s > .6 | `#E6CA2F` | `#F7DE1C` | `#DAAF3F` |
| Sand strip, exploded (unshadowed) | (160,867,420,990) S | `#FBCF83` | `#FDD994` | `#ECB25A` |
| Beach, hero (open, lit) | (288,341,340,373) S | `#FDE9A5` | `#FDEAAA` | `#FBE59F` |
| Sand path on the ridge | (265,232,321,258) S | `#F9CF7C` | `#FAD17F` | `#F8CC79` |
| Tan box / slab sides | hero S v < .85 | `#B98745` | `#C19A63` | `#AD7D44` |
| Underside flat bottom | (700,1060,830,1100) | `#936631` | `#966933` | `#7E5323` |
| Underside tan rim | (700,1012,760,1022) | `#C69B51` | | |
| Rock, exploded (all columns and rocks) | (40,925,465,1265) R | `#B19C9A` (5°, .13) | `#DBCAC6` | `#615C69` |
| Rock, C1 front face (lit) | (172,341,242,405) R | `#C2AEAD` | `#D5C1C1` | `#6B6D85` |
| Rock, C1 top bevel | (181,312,237,328) R | `#E6D7D2` | `#E9DBD7` | `#E2D0C5` |
| Rock, C3 front face | (288,264,349,309) R | `#D0BDB9` | `#E8DBD8` | `#727382` |
| Rock, W1 boulder | (312,389,372,453) R | `#B6A1A3` | `#DDCCC8` | `#565F81` |
| Rock, hero warm-lit / cool-shade faces | R by hue | `#CCB7B2` / `#6A6E8A` | | |
| Rock, view medians f34 / r34 / front / side / rear / top | V R | `#B6A1A3` / `#988D9A` / `#B7A5A6` / `#9F95A1` / `#8C849B` / `#B2A3A9` | | |
| Water, exploded plane / hero open / near shore | W | `#06DBFE` / `#01D4FE` / `#21E4FE` | `#3CEBFE` | `#01C8FC` |
| Water, view medians | V W | f34 `#05DBFE`, r34 `#09DBFE`, side `#06A2F5`, rear `#08C8FA`, top `#08D9FD` | | |
| Foam, exploded / hero ring round W1 | F | `#D5FCFD` / `#DFFAFD` | `#E7FEFE` | `#9FE9FB` |
| Soil / bark (D), views | V D | `#885E2F` … `#866029` | `#A47943` | `#492B06` |

### 5.3 How the colour works

- **Grass:** one vivid lime (h 70–90°, s ≥ .93). Lighter and darker patches on the lawn are broad (sun on tilted facets
  plus a few patches); bush and pine greens are separate keys (bush leaves darker and more saturated, pines a cool
  dark green h 143°).
- **Sand:** the beach and the strip are a pale warm sand (h 38–46°, s .35–.50); the hero beach is paler (`#FDE9A5`)
  than the exploded strip (`#FBCF83`) because it lies flat in the sun; the path on the ridge is the strip colour. Paint
  one sand key with a gentle paler band on the flat open beach (distance from the column feet > 1.5) and a gentle darker
  contact band at the column feet; not by facing.
- **Tan sides and underside:** slab sides (boxes, the grass top's soil band where it shows as tan, the sand strip's
  sides) one tan; the underside / soil one mid brown.
- **Rock:** one warm grey; lit faces warm, shade faces blue-violet (lighting). Per-column Tint ±4 % so neighbours
  differ slightly. The top bevels read lighter (`#E6D7D2`) because they face the sun.
- **Water:** one saturated cyan, flat (no shallow band: the sheet's water is uniform except near-shore highlights
  `#21E4FE`, which are the texture's caustic lines). Under it a darker bed so the see-through water reads saturated
  (W03 R5: the riverbed gives the deep cyan).
- **Foam:** one pale cyan-white.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are **unshadowed rendered regions** (the exploded parts and the open lit areas), not swatches.

| Key | Calibration target (kind) | Where | Finish |
| --- | --- | --- | --- |
| `m032_grass` | `#A7CE09` (green; exploded lawn; hero `#9FC904`; swatch `#9ECE2D`) | turf, lawn, box tops | rough 0.9, `low_spec` |
| `m032_leaf` | `#2F8A0C` start, calibrate the bush crowns' median to `#3A8E0C` ± 10 (green; lit `#349C14`, dark side `#196002`) | bushes | rough 0.9, `low_spec` |
| `m032_pine` | `#07692D` (green; hero and exploded pine medians) | pine tiers | rough 0.9, `low_spec` |
| `m032_bark` | `#6E440A` (brown; exploded grass-top D) | pine trunks | rough 0.9 |
| `m032_petal` / `m032_pollen` | `#F2F0E8` / `#E6CA2F` | daisies / centres, yellow flowers | rough 0.8 |
| `m032_sand` | `#FBCF83` (brown; exploded sand strip, unshadowed; path `#F9CF7C`) | beach, sand strip, path, gully | rough 0.95 |
| `m032_sand_light` | `#FCE29C` (hero open beach `#FDE9A5`) | flat open beach, at 40 % | rough 0.95 |
| `m032_soil` | `#B98745` (brown; hero tan sides; underside rim `#C69B51`) | box sides, slab sides, soil band lip | rough 0.95 |
| `m032_soil_dark` | `#936631` (brown; underside flat bottom) | the land's underside, crease dirt, column-foot contact at 30 % | rough 0.95 |
| `m032_rock` | `#B19C9A` (stone; exploded rocks; hero W1 `#B6A1A3`; swatch `#A09CA6`) | columns, boulders, rocks | rough 0.85 |
| `m032_water` | `#06DBFE` (exploded plane; hero open `#01D4FE`; swatch `#00C5FE`) | water slab top and sides | rough 0.15, `kit_transparency` 0.3 (decision §8.6) |
| `m032_bed` | `#0B6E8F` start (W03 `w03_riverbed`), tuned so the rendered water median lands on `#06DBFE` ± 12 | bed under the water, boulders and beach below z 1.0 | rough 0.9 |
| `m032_water_foam` | `#D5FCFD` (exploded foam; swatch `#D0FCFE`) | foam mesh | rough 0.6, `kit_transparency` 0.1 |

**Calibration warnings:**
- **Rock:** the calibrated render must stay warm in the lit faces (h 0–20°, s .08–.16) and its median within 10 of
  `#B19C9A`; a cool drift to the swatch's `#A09CA6` reads wrong next to the sheet.
- **Grass:** near the clip in G; keep h 70–78° and s ≥ .9 in the render (lower the specular, not the colour; foliage
  uses `K.FOLIAGE_SPEC` via `low_spec=True`).
- **Water:** W03 found the Blender preview of see-through water paler than the sheet (`#32BBDC` against `#05CDFD`).
  Judge the water by its render median (target `#06DBFE` ± 15, s ≥ .85) after tuning the bed, not by the key alone; in
  Roblox the exported water texture and the `kit_transparency` decide it (Studio check, §7.1).
- Keep the families apart: grass s ≥ .9 lime, sand s .35–.5 pale, tan s .55–.65, rock s ≤ .16, water s ≥ .85.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Grass:** `grass` base; broad patches (`K.patches` scale 1.2, level 0.3) toward a 20 % `grass`×`leaf` mix on the
  lawn; within 0.6 of a column top or the rim, 25 % `soil` (the trampled lip).
- **Sand:** `sand` base; distance from the column feet > 1.5 and above z 1.15 → 40 % `sand_light`; within 0.5 of a
  column foot or boulder → 30 % `soil_dark`; below z 1.0 → `bed` (hard edge at the waterline, hidden by the foam).
- **Rock:** `rock` with per-piece Tint ±0.04; below z 1.0 → `bed` (hard, submerged); column bases within 0.4 of the
  beach → 20 % `soil_dark`.
- **Hard edges only** where materials meet: rock | grass, rock | sand, grass | soil band, water | foam, sand | bed.

### 5.6 Texture (Tint) and finish

- **Tint:** grass amp 0.04 scale 0.5; sand amp 0.03 scale 0.6; rock amp 0.04 scale 0.5 (broad, per column); water and
  foam amp 0 (the exporter textures water). Never per-triangle confetti ("No photoreal textures or fine surface noise").
- **Finish:** roughness per §5.4; metal 0 everywhere; no emission.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- Lawn median within 10 of `#9FC904` on `f34_sheet`; parts-shot grass top within 8 of `#A7CE09`.
- Sand: f34 beach median within 12 of `#FCE59E`; parts-shot strip within 8 of `#FBCF83`.
- Rock: f34 R median within 10 of `#B6A1A3`; lit faces warm, shade faces blue-violet.
- Water: f34 W median within 15 of `#05DBFE`; foam within 10 of `#DEFAFD`.
- Shares per §2.5.

## 6. Joins, contact and the tile contract

- **Columns into the land:** columns overlap 0.3–0.6 and sink 0.3 into the beach / ground; the grass slab rests on the
  column tops with its soil band showing as a thin brown/tan lip (close-up 1). No gaps under columns, no floating tops.
- **Boulders:** sunk 0.3 into the beach or standing on the bed (z 0.2) through the water; none perched on a point.
- **Ground:** one flat underside at z 0 for the land and the bed ("Clean flat bottom surface").
- **Water and foam:** closed shells, never unioned with the land; foam 0.04 above the water; the water slab's side
  faces are the tile edges (front, right, chamfer).
- **Tile contract (record for the later shoreline sheets 041 / 161 and W03):** water z 1.0, bed 0.2, sand 1.0 → 1.8,
  grass 10.4; the water reaches the front edge from X −4 and runs along the whole right edge to the back (top view);
  the ridge stops at Y ≈ 8.5 with its back cliff and doesn't reach the back edge (decision §8.2). If the main session
  wants this corner to chain with W03 straights instead, the edge values to match are W03's (shore d = −7.5, rim
  d = −0.4), and the ridge must be extended to the left and back edges as flat joining faces.
- No coplanar faces between the beach, the bed and the water; jitter column bottoms 0.02–0.05 off ring heights; exact
  booleans one piece at a time (STAGES "Booleans").

## 7. Water, lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** flat saturated cyan water, a white foam ribbon along the waterline and foam rings round the
boulders, all static. No glow, light, sparkle, mist or particles. WorldModeling §12.3: "Separate land, bank slope,
sand strip, water surface … and foam", "Foam should be a few broad strips or rings", "The foam must not z-fight", "Record
waterline and flow direction".

### 7.1 Water (export) and stage 5 (lighting)

- **How water exports** (`export_kit_roblox.py`): faces whose key `flintkit.is_water_key()` accepts (any key containing
  "water") become separate see-through pieces, one per key: SmoothPlastic, the key's 512 × 512 tileable texture
  (`kitwater`, one tile per 16 studs, box-projected UVs from the asset origin so the pattern continues across assets on a
  16-stud grid), `transparency` from `kit_transparency` (else 0.4), **no collision, no shadow**. The STATS line counts
  them as "water" pieces. Hence `m032_water` and `m032_water_foam` (not `m032_foam`: a key without "water" would bake
  the foam into the solid land piece and make it walkable, against the sheet's "separate meshes").
- **Expected STATS for the hero:** solid 1 (or 2 if over the cut size), **water 2** (`m032_water`, `m032_water_foam`),
  glow 0.
- **Waterline z 1.0; no flow direction** (a still shore, no streaks on the sheet).
- **Stage 5 (lighting): skip, and record why.** Nothing glows; no emission, no PointLight.
- **Studio notes (Requires Manual Validation):** the water's cyan and the foam's opacity through the exported texture
  and transparency; that the bed under the water is not visible as a hard edge at the tile border; the lawn lime and
  the rock's warmth under the game's sun.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`, `heat_glow`,
  `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **Recommended:** `water_foam` sockets (the W03 precedent and the "every model ships its VFX" rule):
  - along the waterline every 5–6 studs at z 1.05, scale 0.6–0.8: about (−3.5, −11), (0.5, −6), (4, −1),
    (7.5, 4), (11, 9.5): **5 sockets**;
  - one ring socket per boulder standing in the water, scale by size 0.5–1.0: W1 (5, −9.5) 1.0, W4 (9, −5) 0.6,
    W6 (10.8, 3) 0.8: **3 sockets**.
  - Check the export STATS line reports 8 sockets.
- **Not recommended:** `water_flow` (no current or streaks on the sheet; a shore), `waterfall_mist`, `vapour`, `dust`,
  any light.

## 8. Naming and decisions for the main session

**Names owned elsewhere** (repo text and every sheet / kit / checkpoint / wip `.blend`, zstd-decompressed, with
`blendall.py`):
- **W03** (kit, `W03.blend`, wip blends, manifests): `RiverbankChunk`, `RiverbankChunkGrassTop`,
  `RiverbankChunkRockSlope`, `RiverbankChunkSandStrip`, `RiverbankChunkWaterPlane`, `RiverbankGrassTop`,
  `RiverbankSandStrip`, `RiverbankRockSlope`, `RiverbankWaterPlane`, `StreambedPatchWaterPlane`, `StreambedWaterPlane`,
  `WaterfallTopWaterPlane`, `ShoreIslet*`; the string `ShoreFoam` (19 hits in `W03.blend` and the streambed wip); keys
  `w03_*`.
- **W02:** `CliffWallGrassTop`. **07 terrain kit:** `CliffOuterCorner`, `CliffInnerCorner`, `Riverbank`,
  `RockyLakeshore`; keys `water`, `water_deep`, `water_shallow`, `foam`, `sand`.
- `Shoreline` occurs once per blend (a sheet title string), never as an object name. **`ShorelineCorner` and `m032`
  occur nowhere** in the repo text or any `.blend`.
- `M.mk` would silently rename a clash to `<name>M032`; the names below don't clash.

| Object | Part | Why |
| --- | --- | --- |
| `ShorelineCorner` | hero | the sheet's title; free |
| `ShorelineCornerGrassTop` | Grass Top (vegetation cluster) | `…GrassTop` is taken by W02 / W03 prefixes only |
| `ShorelineCornerSandStrip` | Dirt / Sand Strip (shore surface) | |
| `ShorelineCornerRockSlope` | Rock Slope (cliff pieces): the front column row + its foot rocks | |
| `ShorelineCornerWaterPlane` | Water Plane | |
| `ShorelineCornerFoam` | Foam (separate) | avoid `ShoreFoam` |

- Palette keys `m032_*` (§5.4). Collection `Kit/M032 Shoreline Corner`.

**Decisions needed (a recommendation each):**
1. **Size:** **tile 32 × 26 (bbox 32 ± 0.5 × 25 ± 1.5), ridge top 10.4, water 1.0, bed 0.2** (recommended: the
   terrain grid, W03's levels, the hero inversion and the top view's 1.253 agree), or a full 32 × 32 square (the back
   strip would show above the hero's top edge by about +0.13 H).
2. **Footprint:** **as the hero shows: the ridge as a 45° band with its back cliff, the back-left and front-left corners
   empty** (recommended: the hero, front, r34, rear and side cells all show it; at the hero camera anything in those
   corners would add silhouette where the sheet has paper), or filled to the left and back edges as flat joining faces
   (the top view; better for chaining with W03 straights, but the hero's top-left and bottom-left would read +0.2–0.3 H
   off).
3. **Hero camera for verification:** **`f34_sheet (0, 32)`, `front_sheet (0, 26)`, `r34_sheet (180, 30)`,
   `rear_sheet (180, 18)`, kit `side (90, 12)`, kit `top (0, 89)`**; kit front34 / rear34 / front / rear / underside
   as self-consistency; extras `junc_cu (−30, 15)`, `water_cu (−25, 35)` and a parts shot (−20, 25) (recommended, §3).
4. **Which shoreline straights this joins:** **record the §6 contract and leave chaining to the later shoreline sheets**
   (recommended: the kit's exported W03 is not the 32-stud script build, so there is no fixed partner yet), or force
   W03's 32-stud seam values now (needs decision 2's second option).
5. **Parts:** **five: GrassTop, SandStrip, RockSlope (front column row with its foot rocks), WaterPlane (slab + bed),
   Foam** (recommended: the sheet's "Reusable parts" list), or RockSlope as a single column.
6. **Water and foam:** **water slab `m032_water` (`kit_transparency` 0.3) over a bed `m032_bed`; a restrained foam mesh
   on `m032_water_foam` (`kit_transparency` 0.1) exported as its own see-through piece; plus 8 `water_foam` sockets**
   (recommended: the sheet says foam is a separate mesh twice; the sockets give motion like W03), or sockets only (the
   W03 user rework; the foam ribbon and rings would then be missing from every still render).
7. **Budget:** **4000 for the hero, planned at about 3600–3900** (recommended: STAGES), or allow 6000 for terrain
   heroes (W03 carried 8000) to keep more bushes and flowers.
8. **Stage 5:** **no emission or lights** (recommended: nothing glows).
9. **Hero packaging:** **one object: one closed land shell (columns, ridge, beach, boxes, boulders unioned), vegetation
   shells, a closed water shell and a closed foam shell** (recommended: STAGES allows separate shells where the sheet
   shows separate pieces, and the exporter splits water by key).
10. **Names** as proposed.

## 9. Pitfalls to avoid (lessons from recent verifier failures written as targets)

1. **A rock pile instead of one ridge with columns** (021 round 1). The ridge must read as **one continuous form**: a
   single grass slab along its whole length, the columns as **separate fat prisms** standing side by side with dark
   full-height creases. Target: in `f34_sheet`, 6 front columns plus C0 distinct at §2.3 (±0.05 f); no dark V-gaps
   wider than 0.6 stud except the column creases; no boulder heaps on the ridge (3 small lawn rocks only).
2. **Lumpy columns.** "Large flat faces", "Simple beveled edge, no noise": columns are 8–10-sided prisms whose side
   faces stay big (each ≥ 1.2 studs wide, ≥ 2.5 tall, split into at most 2–3 triangles of slightly different normal),
   one chamfer ring and a **flat top** (≥ 60 % of the top area within 10° of horizontal). Not `K.hull_rock`, not
   ico-spheres, no vertex noise.
3. **Paint taken from shadowed areas.** Every calibration target in §5.4 is a median of an unshadowed region (the
   exploded parts, the open beach, the open water). Don't calibrate rock to the shade quartile or the swatch.
4. **Measuring wrong.** Use `measure_render.py` with the render's background as paper and **any floor or ground shadow
   as background**; check width per height (§1.2) and shares in **every** compared view, including `rear_sheet` and
   `r34_sheet`, not only the hero.
5. **Comparing with the wrong camera** (§3): the hero is az 0 (not 45° iso); the r34 and rear are from behind (water on
   the left), not the hero mirrored; the side is the kit +X camera.
6. **Foam baked into rocks or the land.** Foam is its own shell on `m032_water_foam`, 0.04 above the water, never on
   rock faces; check the export STATS shows 2 water pieces.
7. **Water that collides or z-fights.** The water and foam keys contain "water" (no collision on export); foam never
   coplanar with water; the water slab's top is one flat plane (no shallow band, no ripple geometry).
8. **Colour by facing.** Rock warm/cool, lawn light/dark and beach pale/dark come from the light; paint only by
   position fields (§5.5); `K.check` facing correlation < 0.5.
9. **Copying the top view's footprint or the exploded sizes** (§3.4, §3.5).
10. **Thin W03-style cliffs.** W03 was flagged "low flat cliff; sand thin": the cliff stands 8.6 above the beach and the
    beach is 3–5 wide in the middle.
11. **Exact booleans:** union the land pieces one at a time, keep water / foam / vegetation out of the union, save
    between risky steps; `M.fix_bowties` after unions (leaf hubs and bush fans had bowties in 019–021).
12. **Naming clashes** (§8). Only one agent drives a Blender session at a time; no commits, pushes or exports in stage
    agents.

## Decisions (main session, 2026-10-29)

All recommendations are accepted:
1. Size: a 32 × 26 tile (bounding box 32 ± 0.5 × 25 ± 1.5), on W03's levels: water at z 1.0 over a bed at 0.2, sand rising 1.0–1.8, the ridge's grass top at 10.4, pines up to about 17.
2. Footprint follows the hero: a 45° band with a back cliff; the back-left and front-left corners stay empty.
3. Comparison cameras:
   - `f34_sheet (0,32)` and `front_sheet (0,26)`;
   - `r34_sheet (180,30)` and `rear_sheet (180,18)`;
   - the kit side (90,12) and kit top;
   - extras: a cliff-top junction close-up, a water close-up and a parts shot.
4. Tiling: record the contract in this spec; chaining waits for the later shoreline sheets 041 and 161.
5. Five parts: `ShorelineCornerGrassTop`, `ShorelineCornerSandStrip`, `ShorelineCornerRockSlope`, `ShorelineCornerWaterPlane` and `ShorelineCornerFoam`.
6. Foam: a separate thin foam mesh on a `*water*` key (so it exports as see-through water), plus 8 `water_foam` sockets.
7. Budget: 4000.
8. No emission or lights.
9. Packaging: one hero object, `ShorelineCorner`. It holds one closed land shell, separate vegetation shells, and closed water and foam shells. This is an exception to the kit's one-shell rule, because water and foam must export as their own see-through pieces. Every shell must be closed and manifold, with 0 bowties, and the export must show 2 water pieces.
10. Names as above; keys `m032_*`.

The cliff is one continuous ridge of distinct big flat-faced columns (each face at least 1.2 × 2.5 studs, at least 60 % flat tops), not a rock pile.

## Stage 1 — Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m032.py`, `build()` (fixed seeds; about 31 s without renders, 54 s with every render in a
fresh background Blender). Build frame as §1.1; final tile bbox **32.20 × 25.89 × 16.06** (ridge turf 10.4, pines to
about 16), origin at the bbox bottom centre.

**Parts** (each its own function, checked against its exploded cell; `part_*.png`, `exploded.png`):
- `grass_slab()` → GrassTop: a constrained-Delaunay slab over the `RIDGE` outline, top 10.4 (stepping to 9.7 at the left
  end, C0) with ±0.05 jitter, 1.05 thick; its side band is green turf (top 0.62) over a brown soil line; the sand path
  is a constraint region of the top. The pines, bushes, daisies and yellow flowers are added after the cleanup (below).
- `beach()` → SandStrip: a slab between the waterline and a line hidden inside the columns, z 1.0 at the waterline
  rising (smoothstep over 2.6 studs) to 1.8 at the cliff foot, its seaward wall straight down to below the ground.
- `column()` → RockSlope: fat flat-faced columns = the convex hull of a foot ring and a shoulder ring (8-sided
  superellipse, exponent 0.8; taper 1.04 → 0.96; the shoulder ring twisted up to ±7° and jittered ±0.35 in z, so each
  side is one big facet of two triangles with slightly different normals), then one chamfer (inset 0.38, or 0.095 × the
  smaller footprint side; down 0.42) to a flat top ring. 44 tris (front, 8 sides) / 38 tris (back, 7 sides).
  RockSlope = C0, C1, C1b, C2, C3a, C3b, C4, C5, C6 + L1, W2, W3, unioned.
- `bed()` + `water()` → WaterPlane; `foam()` → Foam (stage 6 and the water notes below).

**Hero** `ShorelineCorner` (decision 9): one land shell = bed (top 0.2) + beach + ridge core (the ridge outline inset
0.3, up into the slab) + 9 front and 8 back columns (C0–C6 with C1b; CL, BK1–BK4, BK6–BK8) + grass slab + 2 low boxes
(tan box, grass cap slab) + 11 boulders (convex hulls; W1 on 7/7/6/4 rings, the rest 6/6/5/3 or 5/5/4/2) + 3 pebbles +
3 lawn rocks: exact unions one shell at a time with merge 0 (m026 `_union_fine`), then a floor cut at z 0. Then, on the
finished land: 3 pines (trunk + three drooping 5-point star tiers stacked so that no piece touches another: the lower
tiers are frustums whose flat caps stop 0.1 under the next tier's skirt) and the bushes, daisies and yellow flowers as
separate closed shells set 0.05 above the land by ray casts. A BVH guard checks every piece against the land, the pines
and every plant already placed; a leaf that would touch is tried shorter and steeper, then dropped (4 of 79 dropped).
Then the water and foam shells.

**Layout against the sheet.** The study's §2 polylines were not self-consistent at e 32: the hero's column tops, feet,
waterline and beach heights cannot all be met by one orthographic plan with a 10.4 ridge. So the plan was refitted on
the `f34_sheet` render:
- the column tops by projecting each column's top corners into the render's silhouette frame (C1 h .48, C0 .52, C2 and
  C3 stepping up, C4 .78);
- the ridge's back edge to the top profile;
- the coast pushed back on the diagonal so the water reaches higher on screen;
- the ridge's right end stepped down (C5 9.4, C6 7.0);
- the water's right edge cut at Y 8.1 (the hero's right edge reads h .49–.52), so the back-right corner is empty like
  the back-left and front-left corners (decision 2).

| View | W : H sheet / ours | top profile error mean / max | bottom error mean / max |
| --- | --- | --- | --- |
| f34_sheet (0, 32) | 1.455 / 1.401 | .056 / .28 (the max is at f 1.0: the lens's perspective makes the front-right corner the right-most pixel) | .013 / .05 |
| front_sheet (0, 26) | 1.539 / 1.459 | .080 / .30 | .008 / .03 |
| r34_sheet (180, 30) | 1.476 / 1.391 | .085 / .28 | .065 / .28 |
| rear_sheet (180, 18) | 1.482 / 1.533 | .191 / .35 | .087 / .31 |
| side_sheet (90, 12) | 1.201 / 1.267 | .164 / .57 | .020 / .11 |
| top_sheet (0, 89) | 1.253 / 1.205 | n/a | n/a |

f34 top profile, sheet / ours, every .05 f: .29/.26 .46/.43 .57/.63 .61/.67 .63/.71 .79/.82 .78/.78 .75/.82 .82/.85
.83/.87 .97/.95 .91/.95 .86/.93 .90/.91 .90/.90 .83/.90 .81/.86 .70/.75 .67/.52 .52/.53 .49/.21.
f34 bottom profile, ours: .23 .14 .13 .09 .09 .05 0 … 0 .04 .08 .13 (sheet .22 .19 .17 .13 .10 .07 .04 .01 0 … .02 .07 .11).

Shares in %, G vegetation / D soil / S sand / R rock / W water / F foam:

| View | sheet | ours |
| --- | --- | --- |
| f34 | 26.2 / 1.6 / 8.6 / 37.6 / 19.6 / 2.2 | 20.2 / 3.8 / 6.7 / 47.7 / 15.1 / 1.5 |
| front | 26.0 / 2.1 / 5.3 / 40.1 / 16.3 / 2.4 | 19.3 / 3.8 / 6.4 / 50.3 / 14.0 / 1.4 |
| r34 | 27.5 / 1.5 / 1.8 / 47.2 / 15.0 / 1.9 | 23.3 / 3.9 / 1.8 / 62.0 / 6.7 / 0.8 |
| rear | 26.3 / 1.8 / 2.3 / 57.5 / 4.4 / 1.2 | 19.4 / 4.7 / 1.5 / 68.3 / 3.6 / 1.0 |
| side | 16.6 / 0.4 / 0.1 / 53.5 / 16.5 / 2.3 | 13.8 / 2.8 / 3.4 / 60.3 / 14.9 / 1.1 |
| top | 36.5 / 1.2 / 10.3 / 9.4 / 34.5 / 4.5 | 28.9 / 0.2 / 6.6 / 34.8 / 20.4 / 2.3 |

**Column faces** (before the union; the smallest foot / shoulder ring edge; the side faces are 4.8–9.3 tall above the
beach or ground): C0 1.59 / 1.46, C1 1.77 / 1.61, C2 1.36 / 1.35, C3a 1.43 / 1.22, C4 1.34 / 1.30, BK1–BK7 1.32–1.88.
The small columns the study sized 3.0–3.6 wide (C1b, C3b, C5, C6, CL, BK8) reach 0.96–1.17 with 8 sides.
**Flat tops** (area within 10° of horizontal over all up-facing area): 0.66–0.74 on every column.

## Stage 2 — Optimisation and cleanup

- **Tris:** hero **3886** (land 2438; vegetation 804 in 93 shells; water 296; foam 348 in 7 shells). Parts: GrassTop 750,
  SandStrip 194, RockSlope 714, WaterPlane 412, Foam 348 (all under 1000).
- **Shells (hero):** 1 land, 93 vegetation, 1 water, 7 foam (the ribbon's pieces between boulder holes, two boulder rings,
  blobs). Every shell has 0 non-manifold edges, 0 non-manifold (bowtie) verts and 0 boundary edges. The audit also
  shows 0 wire, 0 loose, 0 zero-area, 0 n-gons, 0 duplicate verts, normals outward and transforms applied.
- **Self-intersections:** 0 on the hero and every part.
  - The water's shore edge stands 0.09 off the beach's waterline wall, and its bottom 0.06 over the bed.
  - Every boulder is cut out of the water and foam by a 2D hole 0.09 outside its section below z 1.2.
  - The foam (z 1.03–1.11) is 0.03 over the water.
  - The vegetation guard (stage 1) keeps every plant shell clear.
- **Cleanup chain:** union → floor cut → weld → ears → pockets → m026's guarded desliver → a guarded needle collapse and
  cap flip (`_force_guarded`: each collapse is refused if it makes a face cross another, and the whole pass is undone
  if it still folds) → finish → polish. The plain m012 `_force_slivers` folded the surface in 1–5 places on this model,
  so it now runs only in guarded batches.
- **Faces under 5°:** 8 on the hero, all in one place (the core wall in the notch between C1b and C2, near (−4.2, −3.5):
  tall 9-stud strips where the column unions meet), and 3 on RockSlope; 0 on every other part. The water's and foam's
  2D triangulations are tidied (crowded points merged, straight boundary runs thinned, beauty fill, 2D bowties split
  before extrusion); their walls are planar quads.
- **Collision:** hero `precise` (a walkable terrain tile, not one hull); land parts `hull`; WaterPlane and Foam `none`
  (water pieces never collide anyway).

## Stage 3 — UV

Angle-based unwrap of Smart UV islands (`M.smart_uv`, margin 0.008), then m012 `_uv_unfold`:
- hero: 950 islands, 0 overlaps, 0 flipped, minimum gap 0.016, border 0.008, density 1.0 / 1.0 / 1.0, conformal stretch
  p95 1.011;
- every part: 0 overlaps, 0 flipped, p95 ≤ 1.016.

The exporter writes its own palette UVs, and box-projected UVs for the water.

## Stage 4 — Materials, colour, texture

**Pass 1** (K.calibrate on the dome; targets are the unshadowed rendered regions of §5.4). Key → rendered (target):
- grass `#88A900` → 167,205,5 (#A7CE09);
- leaf `#347909` → 58,142,11 (#3A8E0C);
- pine `#055D2D` → 10,106,45 (#07692D);
- bark `#573300`;
- pollen `#B5A51A` → 229,202,48 (#E6CA2F);
- petal `#C8C8C4`;
- soil `#936F39` → 185,134,68 (#B98745);
- soil_dark `#765424` → 147,102,49 (#936631);
- rock `#8C8085` → 176,156,155 (#B19C9A);
- sand `#DEA872`, sand_light `#E7B787`.

**Pass 2** (`f34_sheet` medians with the study masks):
- rock → `#A89AA1`: the hero's R median went from #988686 to **#B9A4A4** (sheet #B6A1A3). Lit faces are warm and shade
  faces cool, from the light.
- leaf → `#2C7A10`.
- soil → `#A8804A` (the shaded sides were reading as dark soil).
- sand → `#F0C47E`, sand_light `#F6D695`.
- water → `#00C8F4` over a bed `#054F6C`: the water median went from #26EBFF to **#25D8FF** (sheet #05DBFE).

Final f34 medians against the sheet:
- G #779E0F (sheet #58A70A, whose G includes far more dark bush and pine);
- S #D6AA6A (sheet #FAD58E): much of our visible sand is in the columns' shadow or seen at a grazing angle; the keys
  render #FFCE83 when lit;
- F #CCFFFF (#DEFAFD);
- D #6F5334 (#885E2F).

**Painting** (by position only, never facing; 25 / 50 / 75 % `mix_key` steps, `STEPS = 4`):
- **Lawn:** broad noise patches (scale 0.18) 25 % toward the bush green. The path is a hard sand region. The slab's side
  band is turf above `grass_z − 0.62` and soil below (two real materials, hard edge).
- **Beach:** within 1.2 of the cliff foot, 25 % toward dark soil (contact). The open beach is 0 / 25 / 50 % toward light
  sand by its distance from the waterline and the foot. The seaward wall takes the bed colour (submerged).
- **Columns:** a per-column Tint of ×0.95–1.05, plus broad mottling (amp 0.04, scale 0.5). The front columns' foot band
  (below z 2.2) is 25 % toward dark soil. The ridge core, seen only in the creases, is 50 % rock / dark soil.
- **Boulders standing in the water:** the bed colour below z 0.98 (hard edge, submerged), rock above, with a per-boulder
  Tint.
- **Underside (the floor-cut cap):** dark soil (`#936631`, close-up 2).
- **Tint mottling:** lawn 0.04, beach 0.03, and the rocks and boxes. None on water and foam (the exporter textures water).

**Shading check.** The kit groups sand, tan soil and dark soil as one family and flags the sand tops against the soil
sides and underside (corr 0.88 on the hero). These are the sheet's own material regions: the exploded sand strip, the
tan slab sides, and the brown underside close-up. So the hero, GrassTop and SandStrip carry `kit_shading_ok` with that
reason (`SHADING_OK`).

## Stage 5 — Lighting

Skipped by decision 8: nothing on the sheet glows, so there is no emissive key and no light.

The water (`m032_water`, `kit_transparency` 0.3) and foam (`m032_water_foam`, 0.1) are see-through water pieces:
SmoothPlastic, the kit water texture, no collision, no shadow.

**Studio checks:**
- the water's cyan and the foam's opacity through the exported texture;
- that the dark bed under the water reads as depth, not as a hard edge at the tile border;
- the rock's warmth and the lawn lime under the game sun.

## Stage 6 — VFX

8 `water_foam` sockets (`FX`):
- five along the waterline at z 1.05 (scale 0.65–0.75);
- one per boulder standing in the water (W1 1.0, W4 0.6, W6 0.8).

Export check on the wip file (`--sheet M032 --out <scratch>`, never into `art/roblox/kit/`): **STATS M032: 6 assets, 9
pieces (5 solid, 4 water, 0 glow), 8 vfx sockets, 0 problems**. The hero exports as 1 solid piece plus **2 water
pieces** (`m032_water` 0.3, `m032_water_foam` 0.1) and carries the 8 sockets.

## Modeller's notes for the verifier

- **Cameras:**
  - `f34_sheet (0,32)`, `front_sheet (0,26)`, `r34_sheet (180,30)`, `rear_sheet (180,18)`, `side_sheet (90,12)` and
    `top_sheet (0,89)`, all with a 3× lens and the studio floor hidden;
  - close-ups `junc_cu`, `water_cu` and `under_cu`, plus `exploded` and `part_*`.

  `m032.measure()` gives every number above with the study's masks.
- **Known misses, measured:**
  - In f34 and front, rock is about 10 points high and vegetation about 6 low. The 10.4 cliff at e 32 stands taller on
    screen than the sheet draws its middle columns, whose feet sit far up the beach; the sheet is not one consistent
    orthographic model.
  - Water is 15.1 against 19.6 in f34 (4.5 low).
  - The r34 and rear show more back-cliff rock and less water than the sheet.
  - The side cell shows the whole diagonal ridge. The sheet draws only its right end, which is inconsistent with C1
    standing at the front-left in the hero.
  - The top view shows the column tops and a narrower lawn (decision 2, §3.4).
  - The small columns (sized 3.0–3.6 by the study) have 8 faces 1.0–1.17 wide.
- **Needles:** 8 remain on the hero, all in one notch near (−4.2, −3.5) (core wall strips between C1b and C2), and 3 on
  RockSlope.
- **Vegetation** is separate shells (decision 9) standing 0.05 above the land. A guard keeps every shell clear of
  everything else, so 4 leaves are dropped where bushes crowd the pines.
- **Water preview:** the rebuild repaints the kit water preview texture when the water key changes
  (`_refresh_water_texture`).

## Verification round 1 (verifier, 2026-10-29)

Fresh verifier, read-only on `wip/M032_verify.blend` (port 9881). Every number below was re-measured through the MCP. The
renders went to the scratchpad (`m032_verify/r/M032/`, with `M.MODEL_RENDERS` redirected in the session). The same
`m032.render_views` cameras and `m032.measure()` masks were used. Nothing was saved, built or exported.

### Measured

| Check | Hero | GrassTop | SandStrip | RockSlope | WaterPlane | Foam |
| --- | --- | --- | --- | --- | --- | --- |
| Tris (budget) | 3886 (4000) | 750 (1000) | 194 | 714 | 412 | 348 |
| Size (studs) | 32.20 × 25.89 × 16.06 | 22.1 × 17.0 × 7.4 | 19.8 × 21.3 × 1.8 | 25.1 × 20.9 × 9.8 | 22.3 × 21.4 × 1.3 | 17.7 × 21.3 × 0.08 |
| Shells | 102 (land 1, veg 93, water 1, foam 7) | 57 | 1 | 2 | 2 | 7 |
| Non-manifold edges / verts (bowties), boundary, wire, loose, zero-area, n-gons, dup verts | 0 each | 0 | 0 | 0 | 0 | 0 |
| Self-intersections (BVH, non-adjacent face pairs) | 0 | 0 | 0 | 0 | 0 | 0 |
| Triangles with a corner < 5° | 8 land (all in the C1b/C2 notch at about (−4.1, −3.1), z 2–5.4, plus one on the floor cap at (−5.4, −3.7)) + 102 foam walls | 0 | 0 | 3 | 0 | 102 (foam walls) |
| Normals / origin / transforms | outward / bottom centre / applied | ok | ok | ok | ok | ok |
| UV | 950 islands, 0 overlaps, 0 flipped, gap 0.016, p95 stretch 1.011 | 0 overlaps | 0 | 0 | 0 | 0 |
| `K.check` | no problems | – | – | – | – | – |

- **Per-shell closure (`shells_report`):** land 2438 tris, veg 804, water 296, foam 348; 0 non-manifold, bowtie or
  boundary on every shell.
- **Separation:**
  - water to land: min 0.060, no BVH overlap;
  - foam to water: 0.030 (the foam is z 1.03–1.11 over water 0.26–1.00);
  - foam to land: min **0.019** at (12.6, 8.4), no overlap;
  - veg to land: 0.030, no overlap.
- **Levels:** turf 10.42 max, bed 0.2, water top 1.0, foam 1.03–1.11. The water top is 167 studs²; the foam top is
  37 studs² in 7 pieces (16.1 and 10.8 for the ribbon, 3.8 and 3.6 for the rings, then blobs).
- **Grass slab against column tops (plan, build frame):**
  - grass top (turf faces above z 8): **115 studs²**;
  - exposed rock tops (rock faces with n.z > 0.5 above z 6.5): **148 studs²**;
  - per column, exposed top against footprint: C0 14.4/16.5, C1 16.1/20.0, C2 10.7/14.5, C3a 11.4/14.5, C4 9.2/15.1,
    BK2 10.9/15.1, BK3 9.6/15.7, BK4 8.2/14.9, BK6 10.4/15.8. That is **60–90 % of every column top exposed**, beside
    the slab rather than under it.

**Screen shares and profiles** (`m032.measure()`; G / D / S / R / W / F %, sheet → ours; tolerance ±4, S/F/D ±2):

| View | W : H | G | D | S | R | W | F | top err mean / max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34_sheet | 1.455 / 1.401 | 26.2 / **20.2** | 1.6 / **3.8** | 8.6 / 6.7 | 37.6 / **47.7** | 19.6 / **15.1** | 2.2 / 1.5 | .056 / .28 |
| front_sheet | 1.539 / 1.459 | 26.0 / **19.3** | 2.1 / 3.8 | 5.3 / 6.4 | 40.1 / **50.3** | 16.3 / 14.0 | 2.4 / 1.4 | .080 / .30 |
| r34_sheet | 1.476 / 1.391 | 27.5 / **23.3** | 1.5 / **3.9** | 1.8 / 1.8 | 47.2 / **62.0** | 15.0 / **6.7** | 1.9 / 1.1 | .085 / .28 |
| rear_sheet | 1.482 / 1.533 | 26.3 / **19.4** | 1.8 / **4.7** | 2.3 / 1.5 | 57.5 / **68.3** | 4.4 / 3.6 | 1.2 / 1.0 | .191 / .35 |
| side_sheet | 1.201 / 1.267 | 16.6 / 13.8 | 0.4 / **2.8** | 0.1 / **3.4** | 53.4 / **60.3** | 16.5 / 14.9 | 2.3 / 1.1 | .164 / .57 |
| top_sheet | 1.253 / 1.205 | 36.5 / **28.9** | 1.2 / 0.2 | 10.3 / **6.6** | 9.4 / **34.8** | 34.5 / **20.4** | 4.5 / 2.3 | – |

**Where the extra rock sits** (f34, rock's highest screen row per 0.1 f band, sheet → ours):
- f .15: .51 → .69
- f .25: .43 → .77
- f .35: .51 → .83
- f .45: .53 → .86
- f .65: .72 → .91

C1's own bevelled top reads at h ≈ .48 (sheet .44–.49), so the **cliff height is right**. The extra rock is the exposed
octagonal tops of the front and back column rows, showing beside and behind a narrow grass strip.

**Colour** (medians with the study masks, sheet → ours):

| Region | f34 | Other views and parts |
| --- | --- | --- |
| Lawn | #9FC904 → #99BF0A | top #9EC803 → #A8CF05; parts shot #A7CE09 → #A4C909 |
| Bush leaves | #1B5A03 → #359013 (lighter) | – |
| Pine | #07692D → #096129 | share 4.1 → 1.4 % |
| Sand, all | #FAD58E → #D6AA6A | – |
| Sand, lit (v > .9) | #FCE59E → #FFD481 (s .37 → .49) | sand strip part #FBCF83 → #FFD17D |
| Rock median | #B6A1A3 → #B9A4A4 | – |
| Rock, lit faces | h 17°, s .09 → h 355°, s .11 | the key #A89AA1 is h 330° |
| Rock, cool shade (h 200–290) | 7.9 % → 0.1 % | – |
| Water | #05DBFE → #25D8FF | – |
| Foam | #DEFAFD → #CDFFFF | – |
| Dark soil D | #885E2F → #6F5334 | – |

**Shading by facing:** correlation of colour brightness with how much a face points up, per family on the hero:

| Family | Correlation | Area |
| --- | --- | --- |
| sand keys only | 0.05 | – |
| rock keys | 0.18 | – |
| grass keys | −0.01 | – |
| soil keys | 0.88 | `soil_dark` 578 studs², all n.z = −1 (the floor-cut cap); `soil` 79 studs², mean n.z −0.2 (side bands) |

The kit's 0.87 comes only from sand tops sitting against the tan soil band and the brown underside.

### Findings

1. **blocker: the grass top does not rest on the columns, so the cliff dominates every view.**
   - **What is wrong.** The sheet's defining read is a broad lime grass top that sits on the columns' flat tops. Close-up
     1 says "Flat joining surface between rock and top piece". The top view shows grass over the whole land, with rock
     only on the shore boulders (R 9.4 %). Ours is a narrow S-shaped turf strip (115 studs²) ringed on both sides by
     exposed grey octagonal column tops (148 studs²).
     - In `junc_cu`, the C2/C3a tops stand clear of the slab, a step below it and in front of it, with the brown core
       showing between them.
     - In `top_sheet`, the land reads as a necklace of octagons.
     - In f34, front, rear and r34, the column tops behind the strip add rock where the sheet shows lawn.
   - **How far off.** Rock is over tolerance in every view: +10.1 (f34), +10.2 (front), +14.8 (r34), +10.8 (rear) and
     +25.4 (top) points. Vegetation is under in every view: −6.0, −6.7, −4.2, −6.9 and −7.6.
   - **Verdict.** The cliff height itself matches (C1 top h .48 against .44–.49), so this is not a ridge-height problem.
     It is the slab's footprint and how the columns join it. The read now is "a column massif with a grass strip on
     top", not "a grassy riverbank corner over a cliff".
   - **Fix targets:**
     - **Widen the slab over the columns.** Make `RIDGE` the outer hull of the front and back column tops. The front rim
       runs about 0.6 inside each front column's seaward top edge, so only a bevel strip ≤ 1.0 stud of C0–C6 shows on
       the seaward side, like C1's grey bevel on the sheet. The back edge runs ≤ 0.6 inside each back column's outer top
       edge. Keep the 45° plan, the empty corners (decision 2) and the 10.4 turf (9.7 at C0).
     - **Seat the columns under the slab.** Put every column top inside the slab's soil band: top z between
       `grass_z − 1.05` and `grass_z − 0.62`, so the union swallows the top and the bevel under the turf and the turf
       lip overhangs 0.2–0.4. C0 goes to about 8.7–9.0. The back row goes to 9.4–9.7 under the 10.4 turf; BK2–BK7 are
       now 9.4–9.7 but sit outside the slab.
     - **Plan targets:**
       - grass top ≥ 200 studs² (now 115);
       - exposed rock tops (n.z > 0.5, z > 6.5) ≤ 50 studs² (now 148);
       - each column's exposed top ≤ 30 % of its footprint (now 60–90 %).
     - **Screen targets:**
       - f34: R ≤ 41.6, G ≥ 22.2;
       - front: R ≤ 44.1, G ≥ 22.0;
       - r34: R ≤ 51.2;
       - rear: R ≤ 61.5, G ≥ 22.3;
       - top: R ≤ 15, G ≥ 32;
       - f34 rock-top row at f .25 / .35 / .45 ≤ .55 / .57 / .59 (now .77 / .83 / .86).
     - **Budget (stays under 4000).** The swallowed top and bevel rings free about 15 tris per column, about 250 over 17
       columns. A larger slab cap at spacing 2.0 costs about +120. Spend the net of about +130 on vegetation:
       - pine crowns wider: P2 Ø 3.6, P1 Ø 3.0, a fourth tier on P1 and P2 (about +40);
       - 2–3 more fan bushes on the new rim and the back edge (about +90);
       - f34 pine share ≥ 2.5 % (now 1.4; sheet 4.1).
     - Hero ≤ 3950 tris.
2. **minor: water is a little low in the hero and r34.** f34 W 15.1 (sheet 19.6, −4.5); r34 6.7 (15.0). Target: f34 W
   ≥ 16. Move the waterline 0.5–1.0 stud landward between X 0 and 8, without narrowing the beach below 3 studs.
3. **minor: the beach sand is more orange and less pale than the sheet.**
   - The lit beach renders #FFD481 (s .49); the sheet's open beach is #FCE59E (s .37).
   - The low S median (#D6AA6A) is mostly the cliff's shadow on the beach. The strip part matches (#FFD17D against
     #FBCF83).
   - Target: open beach more than 1.5 from the foot at 50 % `sand_light` (now 25 %), with `sand_light` re-calibrated so
     the lit beach renders #FCE59E ± 12.
4. **minor: the rock is slightly pink.**
   - The key #A89AA1 is h 330°, so the lit faces render h 355°. The sheet's lit rock is h 15–20°, warm.
   - Target: a key hue of 10–20° (about #A89B96). Re-calibrate so the f34 R median stays #B6A1A3 ± 10 and the lit-face
     hue is ≥ 5°.
5. **minor: small columns break the 1.2-stud face rule (decision summary).**
   - C1b, C3b, C5, C6, CL and BK8 have 8 faces 0.96–1.17 wide.
   - Target: 6–7 sides for any column whose smaller footprint side is under 3.6, so every face is ≥ 1.2 wide.
6. **minor: slivers.**
   - 8 hero triangles under 5° (0.5–4.3°, 4–9 studs long) in the hidden C1b/C2 notch at about (−4.1, −3.1), plus 3 on
     RockSlope at (−3.7, −8.3), (2.4, 4.2) and (−3.4, −8.0).
   - They are manifold and don't show at any sheet camera. Re-check after fix 1, which rebuilds that notch.
   - The 102 thin foam-wall triangles come from the 0.08-thick sheet itself and are acceptable.
7. **minor: foam to land clearance.** It is 0.019 at the back-right waterline end (12.6, 8.4), against 0.09 intended
   (`WATER_GAP`). Target ≥ 0.05.
8. **minor: the brown ridge core shows.**
   - `rock_x_soil_dark_50` (#8F7762) reads as a brown vertical band between the back columns (rear, rear34) and in
     the front creases.
   - D is 3.8 against 1.6 in f34 and 4.7 against 1.8 in rear. The sheet's creases are dark grey-violet.
   - Target: core at 25 % `soil_dark` or rock-only, gaps between columns ≤ 0.6, D within +2 of the sheet.
9. **minor: bush leaves read light.** The f34 bush median is #359013 against the sheet's #1B5A03. Target: darken
   `m032_leaf` about 20 % (f34 bush median about #26700B ± 12).
10. **minor (Studio check): the water preview is paler.** The median is #25D8FF against #05DBFE, with R +32 against a
    ±15 target. This is the see-through preview; the exported texture and `kit_transparency` 0.3 decide it in Studio.

**Waiver ruling (`kit_shading_ok` on the hero, GrassTop and SandStrip): honest.**
- Within each material the facing correlation is low: sand 0.05, rock 0.18, grass about 0.
- The 0.87–0.88 comes only from three real regions:
  - the sand on top;
  - the tan soil band, chosen by height under the turf (`grass_z − TURF`, builder line 751) and on the box sides;
  - the dark-soil floor-cut cap. It is selected as the bottom cap at z_min (line 1436), and close-up 2 draws it as
    "Clean flat bottom surface" `#936631`.
- Every blend in the builder (beach contact and light bands, column foot band, lawn patches, submerged bed) is a
  position field.

**Tint mottling:** present (Tint CORNER, spread 1.2 on the hero), broad per column and per region, no confetti; none
on water and foam (correct).

**VFX:** 8 `water_foam` sockets at z 1.05: five along the waterline and one each at W1 (1.0), W4 (0.6) and W6 (0.8).
They suit the sheet's static foam ribbon and rings (the mesh gives the still read, the sockets the motion). No other
kind is implied. OK.

**Decisions:**

| Decision | Result |
| --- | --- |
| 1, size | 32.20 × 25.89, turf 10.42, water 1.0, bed 0.2, pines to 16.06: met |
| 2, footprint | 45° band, empty back-left and front-left: met |
| 3, cameras | met |
| 4, contract recorded | met |
| 5, five parts and their names | met |
| 6, foam mesh on a `*water*` key plus 8 sockets | met. The two water keys (`m032_water` 0.3, `m032_water_foam` 0.1) give 2 water pieces. I could not re-run the export, because verifiers don't export. |
| 7, budget | 3886: met |
| 8, no emission | all emission 0: met |
| 9, packaging, every shell closed | met |
| 10, names | met |
| Columns distinct, flat-faced, flat-topped | met |
| Faces ≥ 1.2 | missed on six small columns (minor 5) |

**Score: 6 / 10.** The mesh, budget, water and foam separation, UVs, VFX, decisions and the colour families are all
sound. The model fails on the one thing the sheet is about: the grass top over the cliff.

**Verdict: FAIL.** There is one blocker (finding 1). Fixes 2–9 are cheap to fold into the same pass.

## Fix round 1 (fix modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m032.py` (source of truth). The final numbers come from a freshly restarted background
session (port 9881, `wip/M032.blend`, saved). Nothing was committed, exported or pushed.

### Changes

**Blocker: the grass slab now caps the columns.**
- `RIDGE` is no longer hand-placed. `ridge_outline()` builds it as the outer hull of the column tops from three
  pieces:
  - every column's shoulder (top-edge) outline, inset by `RIM_IN` (front 0.6, back 0.45);
  - the hull of each neighbour pair round the ridge (`COL_RING`: C0 … C6, BK8 … BK1, CL), which bridges the creases;
  - the polygon through the column centres (the inside).

  The union is read off a constrained triangulation (`_union_outline`), simplified (RDP 0.08, no edge under 0.35) and
  resampled every 2.6 (`RIDGE_STEP`). Its area is 324 studs² (was about 140).
- Every column top follows the turf above it.
  - `column_pts()` puts each top-ring vertex at `grass_z(p) − SEAT` (`SEAT` 0.76, jitter ±0.03), with the shoulder
    `COL_BEVEL` drop below that.
  - The measured seats are 0.73–0.79 under the turf on all 17 columns. That is inside the soil band (0.62–1.05), so
    the union swallows each top.
  - What shows is a flat ledge about 0.2 wide at `grass_z − 0.76` beside the turf wall, then the 0.4 bevel: the
    sheet's "flat joining surface".
  - The per-column `top` field is gone. C0's top is now about 9.0, under the 9.7–10.2 turf. CL and C6, the old low
    end columns, sit under the slab too.
- The ridge core is the centre polygon offset 0.9 (`core_poly()`). At the two ends it is pulled back so it stays 0.5
  inside the rim. It is now 25 % `soil_dark` (was 50 %).
- Gaps between ring neighbours are ≤ 0.62; `col_gaps()` reports them. To get there:
  - C0 moved +0.3 in X and widened from 5.0 to 5.6;
  - BK4 moved 0.45 toward BK6 and widened from 5.0 to 5.6.
- `build()` resets `RIDGE`.

**Vegetation (paid for by the swallowed tops).**
- Pines have four tiers (`PINE_TIERS` 1.8 / 1.46 / 1.1 / 0.74 × scale). P1 is scale 1.1 (Ø 3.96) and P2 is scale 1.2
  (Ø 4.3). Their heights are 5.9 and 6.1 (bbox height 16.39).
- Three more fan bushes stand on the new rim and back edge (the C1 rim, BK2, BK6/BK7). They and two older bushes carry
  `on = "hero"`, which keeps the GrassTop part under 1000 tris.
- The sand path is widened 0.45 each side (`PATH_WIDEN`). Plants that stood on it were moved just off it: P1 to
  (−0.53, 5.63), bushes, a daisy, two yellow flowers and two lawn rocks.

**Minors.**
- **Waterline:** moved landward 0.4–0.5 at X 0–4 ((0.6, −7.2), (3.55, −3.95)).
  - From X 6 on, the original points stay. The beach at C4 is only 1.3–2.1 wide (waterline to column foot), and the
    move would have taken it under 1.
  - R2 and the pebble beside it moved 0.5 landward with the waterline.
- **Beach:**
  - The open beach (more than 1.5 from the foot and 0.5 from the waterline) is now 50 % `sand_light`. The 25 % step
    is only between it and the contact band.
  - `sand_light` was re-calibrated on the render to `#F7E8B4`.
- **Rock key:** `#A89AA1` (h 330°) → `#B0A4A1` (h 12°, R > G > B). Brighter keys (`#BCAFAD`, `#C4B6B6`) blew C1's lit
  face out to white without lifting the median (see "Left over").
- **Leaf key:** `#2C7A10` → `#215C0C` (× 0.75).
- **Small columns:** C1b, C6, CL and BK8 have 6 sides. C3b and C5 have 7, and so does C3a (`COL_SIDES_OF`).
- **Foam:**
  - The ribbon's shore edge is offset `WATER_GAP` + 0.08, because the tidy's merge moves points up to 0.1.
  - The ribbon now ends where it meets the water's back cut, instead of being clamped onto the beach there.
- **Slivers:**
  - A last guarded needle pass collapses edges up to 1.0 (`POLISH_LONG`).
  - RockSlope's columns now start below the ground like the hero's, so the floor cut makes their bottom. Their own
    8-gon bottoms were the floor needles.

### Before → after (round-1 verifier numbers → now)

| Check | Target | Before | After |
| --- | --- | --- | --- |
| Hero tris | ≤ 3950 | 3886 | **3614** (land 1970, veg 1008 in 116 shells, water 300, foam 336) |
| Parts tris | < 1000 each | 750 / 194 / 714 / 412 / 348 | GrassTop 942, SandStrip 196, RockSlope 550, WaterPlane 416, Foam 336 |
| Size | 32 ± 0.5 × 26 ± 1.5 × 17 ± 1.2 | 32.20 × 25.89 × 16.06 | 32.20 × 25.89 × 16.39 |
| Turf top (plan, grass keys, z > 8) | ≥ 200 studs² | 115 | **285** |
| Exposed rock tops (n.z > 0.5, z > 6.5) | ≤ 50 studs² | 148 | **15.1** |
| Exposed top per column | ≤ 30 % | 60–90 % | **0–22 %** (C6 22, C1 18, BK6 14, C0 12, CL 11, BK8 11, the rest ≤ 7) |
| Column top under turf | 0.62–1.05 | – | 0.73–0.79 on all 17 |
| Gaps between neighbours | ≤ 0.6 | up to 1.1 | ≤ 0.62 (BK4–BK3 0.62, C0–C1 0.55) |
| Smallest side face (foot / shoulder edge) | ≥ 1.2 | 0.96–1.17 on six columns | ≥ 1.20 on all 17 (CL 1.32 / 1.20) |
| f34 R / G | ≤ 41.6 / ≥ 22.2 | 47.7 / 20.2 | **36.2 / 34.6** (sheet 37.6 / 26.2) |
| front R | ≤ 44.1 | 50.3 | **40.5** (sheet 40.1); G 31.5 |
| r34 R | ≤ 51.2 | 62.0 | **48.9** (sheet 47.2); G 40.2 |
| rear R | ≤ 61.5 | 68.3 | **60.5** (sheet 57.5); G 29.9 |
| top R / G | ≤ 15 / ≥ 32 | 34.8 / 28.9 | **7.8 / 59.4** (sheet 9.4 / 36.5) |
| side R / G | – | 60.3 / 13.8 | 55.1 / 20.4 (sheet 53.4 / 16.6) |
| f34 rock-top row at f .25 / .35 / .45 | ≤ .55 / .57 / .59 | .77 / .83 / .86 | **.41 / .42 / .46** (sheet .43 / .51 / .53) |
| D (dark soil), f34 / rear | sheet + 2 | 3.8 / 4.7 | **1.5 / 2.5** (sheet 1.6 / 1.8) |
| f34 W | ≥ 16 | 15.1 | 14.9 (miss; see "Left over") |
| Pine share, f34 | ≥ 2.5 | 1.4 | 3.86 (sheet 5.72), measured on a different mask (see the notes below) |
| Lit open beach (f34 lower band, v > .9) | #FCE59E ± 12 | #FFD481 | **#FFE49E** |
| Bush median, f34 | #26700B ± 12 | #359013 | **#286D0E** |
| Rock key hue / lit-face hue | 10–20° / ≥ 5° | 330° / 355° | **12° / 24°** |
| Rock median, f34 | #B6A1A3 ± 10 | #B9A4A4 | #A6998E (miss; see "Left over"). Lit quartile #DAC7BA (sheet #E1D2CD) |
| Foam to land | ≥ 0.05 | 0.019 | **0.127**; water to land 0.051 |
| Faces under 5° | none | 8 hero + 3 RockSlope | **4 hero, 0 RockSlope** (listed in "Left over") |
| Self-intersections | 0 | 0 | 0 on the hero and every part |
| Non-manifold, bowtie, boundary, wire, loose, zero-area, n-gons, duplicate verts | 0 | 0 | 0 on every object and every hero shell (1 land, 116 veg, 1 water, 7 foam) |
| UV | 0 overlaps / flipped | 0 / 0 | 0 / 0 everywhere; hero 992 islands, gap 0.016, p95 1.013 |
| `K.check` | no problems | none | none |
| Sockets | 8 water_foam | 8 | 8 |
| f34 top profile error, mean / max | – | .056 / .28 | .066 / .29 |
| f34 W : H | sheet 1.455 | 1.401 | 1.356 |

Measurement notes:
- **Rock-top row:** the highest row where rock fills at least 30 % of the band. This reproduces the verifier's sheet
  values.
- **Pine share:** my mask is h 128–165, s ≥ .5. On it, ours is 3.86 against the sheet's 5.72, a ratio of .67. That is
  about 2.8 on the verifier's scale, where the sheet reads 4.1.

### Left over

- **Four seam needles (3.2–4.6°).** These are vertical strips where two column faces cross at a shallow angle. They
  are manifold, and none intersects another face:
  - (0.44, −2.83, 3.9) at C2/C3a;
  - (11.56, 5.42, 3.8) on C6's side;
  - (−7.73, 4.66, 8.7) on BK3, under the slab;
  - (−12.75, −6.21, 4.6) at CL/C0.

  Neither the guarded collapse (edges up to 1.6 tried) nor the flips removes them.
- **Rock median #A6998E against #B6A1A3.**
  - The bright flat column tops that lifted the round-1 median are now under the turf. What is left is vertical faces,
    whose shade is darker in the kit studio than on the sheet's flat-lit painting.
  - The lit quartile matches (#DAC7BA against #E1D2CD).
  - A brighter key only blows C1's sunlit face out to white (it leaves the rock class), and the median stays where it
    is.
  - A median with B ≥ G needs a cool key, which the 10–20° hue rule doesn't allow.
- **Vegetation share is now over the sheet:** f34 +8, front +5, r34 +13 and top +23 points.
  - The slab covers both column rows, so the plateau is deeper in plan than the sheet draws it. The top view is 59 %
    lawn against the sheet's 36 %.
  - Narrowing the plateau would mean moving the back row inward, which shrinks the bbox below 24.5 in Y. This is the
    main session's call.
- **Water in f34 is 14.9 (sheet 19.6).** The beach between the waterline and the column feet is only 0.8–2.5 wide, so
  the landward move was kept to X 0–4 (0.4–0.5). Moving the waterline further along would need the C3b–C5 columns
  moved back.
- **Water preview:** the median is unchanged (#25D8FF against #05DBFE). As in round 1, this is a Studio check.

## Verification round 2 (verifier, 2026-10-29)

I am a fresh verifier and did no other stage. I worked read-only on `wip/M032_verify.blend` (port 9881), which already
held the fixed model integrated by the main session. I re-measured every number below through the MCP. I rendered with
`m032.render_views` (`M.MODEL_RENDERS` redirected to the scratchpad `m032_verify2/r/`) and measured with
`m032.measure()` and the study masks. Side-by-side comparisons are in the scratchpad (`m032_verify2/cmp_*.png`).
Nothing was built, saved or exported.

### Measured

| Check | Hero | GrassTop | SandStrip | RockSlope | WaterPlane | Foam |
| --- | --- | --- | --- | --- | --- | --- |
| Tris (budget) | 3614 (4000) | 942 (1000) | 196 | 550 | 416 | 336 |
| Size (studs) | 32.20 × 25.89 × 16.39 | 24.7 × 22.1 × 7.7 | 19.8 × 21.3 × 1.8 | 24.9 × 20.5 × 9.7 | 22.3 × 21.4 × 1.3 | 18.1 × 21.3 × 0.08 |
| Shells | 125 (land 1 / veg 116 / water 1 / foam 7) | 60 | 1 | 1 | 2 | 7 |
| Non-manifold edges / bowtie verts / boundary / wire / loose / zero-area / n-gons / dup verts | 0 each | 0 | 0 | 0 | 0 | 0 |
| Self-intersections | 0 | 0 | 0 | 0 | 0 | 0 |
| Triangles with a corner < 5° | 4 (3.15–4.55°) | 0 | 0 | 0 | 0 | 0 |
| Normals / origin / transforms | outward / bbox bottom centre (exact) / applied | ok | ok | ok | ok | ok |
| UV overlaps / flipped / min gap / p95 stretch | 0 / 0 / 0.016 / 1.013 (992 islands) | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `K.check` | no problems | | | | | |

- **Per-shell closure (`shells_report`).** Land 1970 tris, vegetation 1008, water 300, foam 336. Every shell has 0
  non-manifold edges, 0 bowtie verts and 0 boundary edges.
- **Four needles.** All four are rock, in the land shell, on vertical faces (n.z 0.02–0.09):
  - (0.44, −2.83, 3.9), 6.6 long, in the C2/C3a crease;
  - (11.56, 5.42, 3.8), 7.9 long, on C6;
  - (−7.73, 4.66, 8.7), 2.3 long, on BK3 under the slab;
  - (−12.75, −6.21, 4.6), 6.2 long, in the CL/C0 crease.

  They are manifold and nearly coplanar with their neighbours, and they cross nothing. With flat shading they make no
  visible artefact, so they don't matter.
- **Separation (BVH).**

  | Pair | Min distance | Overlapping faces |
  | --- | --- | --- |
  | Water to land | 0.051, at the water's bottom edge by the beach wall (0.68, −7.24, 0.26) | 0 |
  | Foam to land | 0.127 | 0 |
  | Foam to water | 0.030 | 0 |
  | Vegetation to land | 0.025 | 0 |

- **Levels.** Land 0–10.76 (the turf is 10.4; the 10.76 is a lawn rock). Water 0.26–1.00. Foam 1.03–1.11. Water top
  169.9 studs², foam top 37.1 studs².
- **The round-1 blocker: the slab now caps the columns.**

  | Check | Target | Now |
  | --- | --- | --- |
  | Turf top (grass keys, z > 8, plan area) | ≥ 200 studs² | **284.8** |
  | Exposed rock tops (n.z > 0.5, z > 6.5) | ≤ 50 studs² | **15.1** |
  | Exposed top per column | ≤ 30 % | **0–26 %** (C6 25.7, C1 21.3, BK6 16.7 (most of it a lawn rock), BK8 16.6, C0 13.5, CL 12.7; the rest ≤ 9) |

  - **Seating.** Each column's highest rock vertex sits 0.68–0.77 under the turf above its centre (BK2 1.0). That is
    inside the soil band (0.62–1.05).
  - **Gaps** between ring neighbours are 0–0.62.
  - **Side faces.** Each column's narrowest side face, measured at the foot ring and at the shoulder ring:

    | Columns | Sides | Narrowest face (studs) |
    | --- | --- | --- |
    | C0, C1, C2, C4 | 8 | 1.26–1.77 |
    | C3a, C3b, C5 and the back row | 7 | 1.26–1.88 |
    | C1b, C6, CL, BK8 | 6 | 1.20–1.69 |

    Every face is at least 1.20 wide and 9.2–10.0 tall.

**Screen shares** (G / D / S / R / W / F in %; sheet → ours; tolerance ±4, and ±2 for S, F and D):

| View | W : H | G | D | S | R | W | F | Top profile error, mean / max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34_sheet | 1.455 / **1.356** | 26.2 / **34.6** | 1.6 / 1.5 | 8.6 / **5.5** | 37.6 / 36.2 | 19.6 / **14.9** | 2.2 / 1.5 | .066 / .29 |
| front_sheet | 1.539 / **1.415** | 26.0 / **31.5** | 2.1 / 1.7 | 5.3 / 5.5 | 40.1 / 40.5 | 16.3 / 13.7 | 2.4 / 1.4 | .080 / .31 |
| r34_sheet | 1.476 / 1.369 | 27.5 / **40.2** | 1.5 / 1.9 | 1.8 / 1.5 | 47.2 / 48.9 | 15.0 / **5.5** | 1.9 / 0.8 | .083 / .28 |
| rear_sheet | 1.482 / 1.500 | 26.3 / 29.9 | 1.8 / 2.5 | 2.3 / 1.3 | 57.5 / 60.5 | 4.4 / 3.5 | 1.2 / 1.0 | .175 / .34 |
| side_sheet | 1.201 / 1.238 | 16.6 / 20.4 | 0.4 / 1.7 | 0.1 / **3.0** | 53.4 / 55.1 | 16.5 / 14.5 | 2.3 / 1.1 | .165 / .57 |
| top_sheet | 1.253 / 1.198 | 36.5 / **59.4** | 1.2 / 0.0 | 10.3 / **2.5** | 9.4 / 7.8 | 34.5 / **20.6** | 4.5 / 2.2 | – |

- **Rock** is now within tolerance in **every** view; in round 1 it was 10–25 points over.
- **Vegetation** is over in f34 (+8.4), front (+5.5), r34 (+12.7) and top (+22.9). It is within 4 in rear and side.
- **f34 top profile** (sheet / ours, every 0.05 of the width f). The values outside ±0.08 are in bold:

  | f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | sheet | .29 | .46 | .57 | .61 | .63 | .79 | .78 | .75 | .82 | .83 | .97 | .91 | .86 | .90 | .90 | .83 | .81 | .70 | .67 | .52 | .49 |
  | ours | .25 | .41 | .63 | **.71** | **.75** | .80 | .79 | .83 | .86 | .89 | .98 | .91 | .91 | .91 | .89 | **.92** | .87 | **.82** | **.50** | .52 | **.20** |

  The low value at f 1.0 is the lens perspective at the front-right corner, as in round 1.
- **f34 bottom profile:** mean error .013, max .06.

**Colour.** Medians with the study masks, sheet → ours:

| Region | f34 | Other views and parts |
| --- | --- | --- |
| Lawn | #9FC904 → #99BF0B | top #9EC803 → #A7CF05; GrassTop part #A7CE09 → #AAD20B |
| Bush leaves | #1B5A03 → #266A0E | r34 #1A5B02 → #1F5B0C; top #226305 → #22610D |
| Pine | #07692D → #09642A | share 6.9 → 4.0 % (h 120–165) |
| Sand, lit (v > .9) | #FCE59E (s .37) → #FFD289 (s .44) | SandStrip part #FBCF83 → #FFD07A; top #FDDD8C → #FFD688 |
| Rock median | #B6A1A3 → #A6998E | r34 #988D9A → #AEA09C; top #B2A3A9 → #C2B4AD |
| Rock, lit quartile | #E0D1CC (h 15°, s .09) → #D7C3B7 (h 22°, s .15) | r34 h 12° → h 15° |
| Rock, shade quartile | #656273 (h 251°) → #665D58 (h 21°) | cool-shade share 34 % → 1 % |
| Water | #05DBFE → #25D8FF | |
| Foam | #DEFAFD → #CDFFFF | |

- **Facing correlation.** I correlated each material's key brightness (`flintkit_hex`) with face n.z, area-weighted,
  per family on the land shell:

  | Family | Correlation |
  | --- | --- |
  | Sand | −0.14 |
  | Rock | 0.07 |
  | Grass | −0.18 |
  | Soil | 0.80 |
  | Sand + soil | 0.96 |

  The Tint attribute against facing is within ±0.23 in every family.
- **Soil.** Every `soil_dark` face is the floor-cut cap: n.z = −1 at z 0, a position rule that matches close-up 2's
  "Clean flat bottom surface". The tan `soil` is the slab's side band below `grass_z − TURF`, a height rule. The
  `kit_shading_ok` waiver stays honest; nothing is coloured by facing.
- **Tint** is a per-corner `Tint` attribute: rock ×0.92–1.10 (per column), grass and sand ×0.96–1.04, spread 1.19. It
  is broad and per region, with no confetti. Water and foam carry none, which is correct.

**Water, foam and sockets.**
- Water and foam are separate closed shells that touch nothing (separation above). The foam reads in `water_cu` as a
  shore ribbon plus a ring round W1, which matches close-up 3 (the sheet's ring has round holes; ours is plain).
- **Sockets.** There are 8 `water_foam` sockets at z 1.05, unrotated. At their build positions:
  - **On the shore:** (−3.6, −12.4), (0.2, −9.4), (5.1, −2.8), (9.8, 2.5) and (12.4, 6.4).
  - **At the boulders:** W1 (5.0, −10.4) 1.0, W4 (8.8, −6.0) 0.6 and W6 (10.6, 2.6) 0.8.
  - Three of the shore sockets sit inside boulders: (0.2, −9.4) inside W3, (9.8, 2.5) inside W6, (12.4, 6.4) inside W7.
    The three ring sockets are at their boulders' centres by design.
  - The emitter is a flat 6 × 1.5 box of 2–3-stud patches (×0.6–1.0), so most patches still land on the water. See
    minor 6.

### Findings

1. **minor (the new risk): the plateau is deeper than the sheet's, and its rim is a smooth, even overhang.**
   - **How far off.** Vegetation is +8.4 (f34), +5.5 (front), +12.7 (r34) and +22.9 (top). f34 W : H is 1.356 against
     1.455 (target 1.40–1.52), and the top profile is high by .10–.12 at f .15–.20 and .09–.12 at f .75–.85.
   - **It doesn't break the defining read.** In every view the model reads as a grassy riverbank corner over a cliff of
     column prisms, with a beach and water:
     - rock is within tolerance everywhere;
     - the slab now sits on the column tops with its turf and soil lip, as close-up 1 draws it (`cmp_junc.png`);
     - the coast turns 45°;
     - the water and foam are separate.
   - **The most visible difference left.** The sheet shows grey bevelled column caps stepping along the rim (C1 at
     h .44–.49, C3 and C4 poking up). Ours hides every cap under a pill-shaped slab with an even lip. The f34 rock-top
     row at f .35 / .45 is .42 / .46 against the sheet's .51 / .53.
   - **The sand path** runs down the middle of the plateau; the sheet runs it along the front rim.
   - **Fix targets, for a later pass and not needed to commit:**
     - Pull the back row 1.5–2 studs inward between BK2 and BK6. This keeps the bbox Y ≥ 24.5, so the far-left and
       far-right back columns stay where they are.
     - Lift C1, C3a and C4 so 0.3–0.6 stud of grey cap shows in front of the turf lip.
     - Move the path toward the front rim.
     - Targets: f34 G ≤ 30, top G ≤ 45, f34 W : H ≥ 1.40.
2. **minor: f34 water is 14.9 against 19.6, and r34 water is 5.5 against 15.0.**
   - This comes from the narrow beach at C3b–C5 and the deep plateau, which hides the right-edge water from behind.
   - It stays recognisably a front-right water plane with a chamfered corner.
   - Fix target, together with finding 1: f34 W ≥ 17, by moving C3b–C5 about 1 stud landward and the waterline after
     them.
3. **minor: the rock median is #A6998E against #B6A1A3 (out of ±10), and the lit faces lean beige.**
   - Our lit quartile is h 22°, s .15; the sheet's is h 15°, s .09. The hue is warm, not pink, and the family is right.
   - The shade quartile is warm grey (h 21°), where the sheet's is blue-violet (h 251°). Spec §3.7 and §5.3 say that
     split comes from the sheet's lighting, not paint, so it is a Studio and lighting difference, not a key error.
   - Fix target: drop the key's saturation to about #B2A8A6 (h about 10°, s about .07), so the lit quartile renders
     about #DCCFCB and the median comes up toward #B0A0A0.
4. **minor: the beach sand is a little saturated.**
   - The lit S is #FFD289 (s .44) against #FCE59E (s .37). In f34 the lit S is now mostly the ridge path (`m032_sand`),
     and the sheet's path is #F9CF7C, so this is close.
   - The SandStrip part matches (#FFD07A against #FBCF83).
   - Fix target, optional: path and beach s ≤ .40.
5. **minor: the pine share is low.** It is 4.0 against 6.9 % on the h 120–165 mask (f34). Fix target, optional: the P1
   and P2 crowns about 15 % wider.
6. **minor: three shore foam sockets sit inside boulders, and every socket is unrotated.**
   - (0.2, −9.4) is inside W3, (9.8, 2.5) inside W6 and (12.4, 6.4) inside W7, so part of their emission is hidden in
     rock.
   - The 6-stud emitter box runs along X, not along the 45° shore.
   - Fix targets:
     - move the three sockets 0.5–1 stud seaward, off the boulders, onto open water;
     - yaw the five shore sockets to the local waterline direction, if the exporter honours socket rotation.
7. **minor: four needles of 3.2–4.6° remain in vertical column seams.** They are manifold, nearly coplanar and hidden
   in creases or under the slab, and they make no visible artefact. Accept them.
8. **minor (Studio check): the water preview is paler.** It renders #25D8FF against #05DBFE. The exported texture and
   `kit_transparency` 0.3 decide it in Studio, as recorded in rounds 1 and 2.
9. **Known misses, accepted as in the study (§3.3, §3.4):**
   - the side cell shows the whole diagonal ridge;
   - the top view shows empty back-left and front-left corners and only a thin beach (S 2.5 against 10.3).

**Fix-round claims checked.** These all reproduce exactly:
- tris 3614 / 942 / 196 / 550 / 416 / 336;
- shells 1 / 116 / 1 / 7;
- turf 285, rock tops 15.1;
- per column 0–26 % (the claimed C6 22 % is 25.7 % on my plan-projected measure, still under 30);
- seats 0.68–0.77;
- side faces ≥ 1.20;
- f34 R / G 36.2 / 34.6, W 14.9, W : H 1.356;
- rock median #A6998E;
- bush #266A0E (claimed #286D0E);
- foam to land 0.127, water to land 0.051;
- 4 needles.

The lit-beach #FFE49E claim depends on the region chosen. On the full S mask with v > .9, I get #FFD289, because the
path dominates.

**Decisions:**

| Decision | Result |
| --- | --- |
| 1, size | 32.20 × 25.89 × 16.39; turf 10.4, water 1.0, bed 0.2: met |
| 2, footprint | 45° band; empty back-left and front-left: met |
| 3, cameras | met |
| 4, contract recorded | met (§6) |
| 5, five parts and their names | met |
| 6, foam mesh on a `*water*` key plus 8 sockets | met: `m032_water` 0.3 and `m032_water_foam` 0.1 give 2 water pieces. Export not re-run (verifiers don't export). |
| 7, budget | 3614 / 4000; parts ≤ 942: met |
| 8, no emission | 0 emissive materials: met |
| 9, packaging, every shell closed | 1 land, 116 veg, 1 water, 7 foam; all closed, 0 bowties: met |
| 10, names and keys | `m032_*`, collection "M032 Shoreline Corner": met |
| Distinct flat-faced columns, faces ≥ 1.2 | met (all ≥ 1.20). The flat tops now sit under the slab by design (the round-1 fix target). |

**Score: 7 / 10.**
- **Sound:** the mesh, the budget, every shell closed, water and foam separate, UVs, colour families, no colour by
  facing, and every decision met.
- **Fixed:** the round-1 blocker. Rock is within tolerance in every view, and the slab rests on the columns.
- **Costs left:** a deeper, smoother plateau than the sheet's, with no grey caps at the rim, and less water on screen.

**Verdict: PASS.** Nothing is broken, nothing is over budget, and the defining read matches the sheet. Findings 1–8 are
minors to note at commit.

## Main session ruling (2026-10-29)
Passed in round 2 (7/10) and committed. Round 1 failed (6/10) because the turf slab did not cap the columns; fix round 1 resolved it.

**Left for a later polish pass:**
- The plateau is deeper and smoother than the sheet's. Vegetation is +8 in f34 and +23 in top, and the rim caps are hidden. Targets: pull BK2–BK6 in 1.5–2 studs, show 0.3–0.6 of cap on C1/C3a/C4, and move the path toward the front rim.
- Water is low on screen: 14.9 against 19.6 in f34. Move C3b–C5 about 1 stud landward.
- The rock median leans beige: try a key of about `#B2A8A6`.
- Lit sand is slightly saturated.
- Pine share is 4.0 % against 6.9 %.
- Three shore foam sockets sit inside boulders W3/W6/W7.
- 4 hidden needle triangles in the column seams.
- The water preview is paler than the sheet (Studio check).

**Export:** 6 assets, 9 pieces (5 solid, 4 water), 6054 tris, 8 VFX sockets, palette 18 colours, 0 problems.
