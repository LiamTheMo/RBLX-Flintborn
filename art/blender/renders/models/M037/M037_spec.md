# 037 Waterfall Module — spec

Reference: `art/blender/assets/references/037.png` (1024 × 1536 px). The sheet's own title is "34 / 132 WATERFALL
MODULE", top right "FLINTBORN — INDIVIDUAL MODEL STUDY", footer "FLINTBORN — INDIVIDUAL MODEL STUDY" and "PAGE 34 /
132". INDEX.md row 37 calls it "Flintborn Waterfall Module Study" (the printed 34 is the generator's number; the file
and the index say 037).
Builder: `art/blender/kit/mcp/m037.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows a falling water curtain, a top water plane, a pool, a foam ribbon, a splash disc
with white spray, and foam rings** (§7). No glow, fire or light.

Sheet text:
- **View labels:** "ASSEMBLED — FRONT THREE-QUARTER VIEW", "ASSEMBLED — REAR THREE-QUARTER VIEW", "FRONT VIEW", "SIDE
  VIEW (RIGHT)", "REAR VIEW", "TOP VIEW". **Three of the labels are wrong** (§3): the "rear three-quarter" is a
  front-left three-quarter, the "rear view" is a second front view, and the "side view (right)" puts the pool on the
  screen right, which is the view from −X.
- **Exploded labels ("EXPLODED PARTS & ASSEMBLY"):** "Top Water Plane", "Cliff Top (Grass & Foliage)", "Waterfall Mesh
  (Curtain)", "Cliff Wall Pieces", "Foam Ribbon", "Splash Disc", "Rock Pieces", "Water Plane (+ Foam)". Arrows and dashed
  drop lines show the top water plane sitting on the cliff top, the curtain hanging from it, and the foam ribbon and
  splash disc dropping onto the pool.
- **Close-ups:** "CLOSE-UP 1 — CLIFF TOP JUNCTION" ("Grass Top (sits on cliff walls)", "Rock Wall (join surface)");
  "CLOSE-UP 2 — UNDERNEATH VIEW" ("Top Water Plane (underside)", "Waterfall Mesh (attaches to top and behind rock
  walls)", "Cliff Wall (join surface)"); "CLOSE-UP 3 — WATER PLANE THICKNESS" ("Water Plane (thickness)").
- **Material palette (reference):** Grass / Foliage, Dirt / Soil, Rock, Water, Foam (Effect).
- **Modeling notes:**
  - "Use simple, chunky low-poly geometry."
  - "Broad, flat-shaded faces. No fine detail or noise."
  - "Keep parts modular and reusable."
  - "Clean joins between cliff walls, top, water mesh and planes."
  - "Water and foam are separate effect geometry (not baked)."
  - "Maintain consistent proportions across all views."
  - "Style: cartoony, primitive, Roblox-friendly, FLINTBORN."
- **Game context and the old kit:**
  - **W03 Shorelines / Waterfalls / River**, row 2 (`scripts/kit/W03/waterfall_module.py`, `renders/kit/W03/
    waterfall_module_goals.md`, kit `W03.blend`, exported `art/roblox/kit/W03/manifest.json`): `WaterfallModule`, a 32 ×
    32 cliff tile, **grass z 20.5 on a 0.5 soil band, channel water z 20.0 (8 wide at the back edge centre), a ~19-stud
    fall, a round pool z 1.0 over `w03_riverbed` z 0.2 in the front ~40 %, a 12-wide pool mouth at the front edge
    centre**. Parts `WaterfallTopWaterPlane`, `WaterfallCliffTop`, `WaterfallCliffWallA/B/C`; variants `WaterfallNarrow`,
    `WaterfallWide`, `WaterfallTwoStep`; sockets `VFX_WaterfallCurtain_N` (waterfall_curtain beams, x ±2, width 4.5,
    LEAN 1.0), `VFX_WaterfallSplash` (waterfall_mist), `WaterfallVapour`, `VFX_WaterfallFoamRibbon_N`, `WaterfallFlow`.
    The W03 rework (R7) made all falling water, foam and vapour VFX ("Only flat water surfaces are meshes").
    `MODEL_PROGRESS.md` row 52 flags it "cliff smooth/pale; thin curtain, little foam/splash; flat pool; two-step not
    tiered". The exported manifest records a smaller hero (22.2 × 14.9 plan, 18.2 tall), so the kit file's W03 is not the
    32-stud script build.
  - **07 terrain kit** (`build_07_terrain_kit.py` line 1884): `WaterfallCliff`, two cliff halves either side of a wide
    fall, cliff top z 20, a round `water_deep` pool z 1.8; its VFX row (`lib/vfx.py` line 349) is `waterfall_mist` at the
    pool plus two `water_foam`.
  - **M032 Shoreline Corner** and **M034 Streambed Section** (both accepted 2026-10-29): water z 1.0 over a bed (M032
    0.2, M034 0.7), a separate thin foam mesh on a `*water*` key plus `water_foam` sockets, one hero object with closed
    land / water / foam shells, `collision="precise"`. M034's seam contract: **channel X −7 … +7 at both seams, banks
    1.6, water 1.0, bed top 0.7**, flow +Y → −Y. M034's spec names 037 as a tile that should meet that contract.
  - Later sheets on the same subject: 159 "Waterfall flow and impact mist" (Event & VFX), 160 "River flow and foam VFX".

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The cell paper is `#FEFBF2`
(254, 251, 242), tolerance 14, **and warm: a paper pixel also needs r − b ≥ 3**, because the white spray, the foam and the
daisies are near-white but cool (b ≥ r) and would otherwise vanish into the paper. The two hero cells have their titles
painted out (`TITLES` in `m.py`). The masks are `cls()` in `m.py` (HSV, h in degrees), assigned in this order:
- **W, water:** h 182–215, s ≥ 0.45, v ≥ 0.45 (pool, top channel, the curtain's saturated stripes).
- **F, foam / spray / curtain highlights:** (h 165–230, s 0.03–0.45) or s < 0.03, v ≥ 0.86.
- **G, vegetation:** h 52–165, s ≥ 0.30, plus yellow flowers (h 40–52, s ≥ 0.55, v ≥ 0.75). Sub-masks in `samp.py`:
  lawn and lime bushes h 60–100, dark bushes h 95–125, pines h 125–165.
- **S, dirt (lit):** h 26–52, s 0.30–0.75, v ≥ 0.60.
- **D, soil / bark (dark):** h 0–45, s ≥ 0.30, v 0.12–0.66 (the low boxes' soil sides, pine trunks).
- **R, rock:** (s < 0.20, v 0.22–0.93) or (h 200–290, s < 0.45, v 0.18–0.88: the blue-violet shade faces) or (h < 28 or
  ≥ 300, s < 0.30, v 0.22–0.93: the warm lit faces).
- **O, other:** outlines, crevices, pink flowers; not a target.
- Known leaks: white daisies fall into F (≤ 1 point); the warmest lit rock faces (h 22–26, s .27–.34) fall into O;
  pink flowers are O.
- **The sheet draws no ground shadow** (the paper under every cell is clean). Treat any render floor or floor shadow as
  background: measure renders made with `FB_Ground.hide_render = True` (§2.6).

**Scratch study material** (no Blender), in
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m037_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Pillow + numpy).
- **Helpers:** `m.py` (masks `cls()`, view boxes `V`, exploded and close-up boxes `X`, `preview()`), `lab.py` (connected
  components), `zoom.py` (crop + upscale), `grid.py` → `g_*.png` (10 % grids over each view's silhouette, red = centre
  lines), `bb.json` (silhouette boxes), `px.py` (point samples).
- **Measurements:** `measure.py` → `measure_out.txt` (bbox, shares, top / bottom profiles, width per height);
  `rows.py <view>` → `rows_*.txt` (per-row class strips); `edges.py` → `edges_out.txt` (bottom-edge slopes);
  `curtain.py` → `curtain_out.txt` (curtain extents per height); `topscan.py` → `topscan_out.txt` (top-view rocks,
  channel, pool and grass runs); `creases.py` → `creases_out.txt`; `fit.py` (plan-proxy camera fit; not discriminating
  here, see §3.1).
- **Colour:** `sw2.py` → `swatch_out.txt`; `samp.py` → `samp_out.txt` (view medians per class, hero regions, exploded,
  close-ups, bushes, flowers, slab sides).
- **Names:** `blendall.py` → `blendall_out.txt` (every sheet, kit, checkpoint and wip `.blend`, zstd-decompressed).
- **Crops:** `f34.png`, `r34.png`, `views.png`, `side.png`, `top.png`, `expl.png`, `cu.png`, `pal.png`, `cell_*.png`,
  `z_f34_bottom.png`, `z_expl_top.png`, `z_expl_walls.png`, `z_expl_water.png`; mask previews `cls_*.png`.
- **On our renders:** `measure_render.py <render.png> [paper_hex] [--flip]` prints the same bbox, shares, profiles,
  width per height, class colour medians, lit-rock and lawn medians with the study masks (an alpha channel counts as
  background). On the sheet's own f34 cell (`cell_f34.png`) it reproduces the §1.2 numbers exactly
  (`selftest_f34.txt`).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a modular cliff / water terrain tile. Hero budget 4000 tris (STAGES), each part under
  1000. The plan in §4.3 lands at about 3700–3950 (decision §8.7).
- **Overall read (check this first).** A **square tile whose back 53 % is a tall block of fat, flat-faced grey rock
  columns** with a **lime grass top split in two by a cyan river channel**; the channel runs from the back edge,
  pinches between two rocks, widens into a small lip pool and **pours over a notch in the middle of the cliff face as a
  broad, three-band cyan curtain** that falls the full height into a **flat saturated cyan pool filling the front 47 % of
  the tile edge to edge**. At the foot: a **white splash disc with spiky spray** and a scalloped **foam ribbon**, foam
  patches across the pool, **two big faceted boulders standing in the pool** in foam rings, smaller boulders along the
  cliff foot. Two **stepped columns** stand proud of the face either side of the fall, each capped with a lime bush; a
  **low grass box with a pine** sits at each front corner of the cliff foot. On top: four pines, dark fern bushes,
  white / pink / yellow flowers, grey rocks lining the channel.
  - It must read as **a cliff of separate columns with flat tops under one grass cap**, a **flat curtain in a notch**
    and **a flat pool**, not a rock pile and not a sculpted mountain.
  - Hero shares (f34): rock R 36.1 %, water W 21.4 %, vegetation G 19.6 %, foam / spray F 12.2 %, soil D 1.5 %, dirt
    S 0.6 %.
- **Focal silhouettes, in order:**
  1. The curtain: in the front cell f .40–.61 from the lip (h .70) down into the spray (h .20–.27), in the f34
     f .46–.60, top h .70.
  2. The column block either side: front cell rim at h .68–.72 across f .03–.37 and f .61–.95; the stepped columns at
     f .13–.29 (top h .48–.50) and f .71–.84 (top h .45–.48) with bush caps.
  3. The pool: a flat cyan band across the whole bottom (front cell h 0–.09) with the two big boulders (f .14–.29 and
     .64–.78, h .08–.21).
  4. The pines over the rim (front cell tips h .94–.99 at f .13–.23, .30–.38, .70–.80).
- **Target size: tile 32 W × 32 D (bbox 32 ± 0.3 × 32 ± 0.3), grass top z 18.0, max z 25 ± 1 (pine tips)**; pool water
  z 1.0 over a bed at 0.2; top channel water z 17.4 over a bed at 17.1 (decision §8.1).
  - **How it was derived.**
    - The kit terrain grid, W03's `WaterfallModule`, M032 and M034 are all 32-stud tiles.
    - The front cell is az 0, e ≈ 10: its bbox is 257 px wide = 32 studs (8.03 px/stud) and 225 px = 28.0 studs tall.
      Its pool shows 20 px of depth for about 15 studs of plan (sin e = 0.17, e ≈ 10°). The grass rim at h .70 then
      puts the cliff top at z ≈ (19.6 − 15 · 0.17) / 0.985 ≈ **17.4**. The pine tips at h .97 put pines at about
      **6.3–7** tall.
    - The top cell is not orthographic but a high front view: three bands, pool .34, cliff face .28 and grass top
      .38 of its height (6.38 px/stud). With pool + top = 32 that solves to e ≈ 51°, **pool depth 15.3, cliff top depth
      16.7, cliff face 15.6 above the pool (top z ≈ 16.6)**.
    - The two agree within 5 %. **Grass top 18.0** is chosen so that the top channel's seam is exactly M034's seam
      raised by 16.4 (bank 1.6 → 18.0, water 1.0 → 17.4, bed 0.7 → 17.1; §6).
    - The curtain is 0.21 of the front cell's width = **6.7 studs mid-fall** (7–8.5 from lip to foot). The top view's
      channel is 13.8 wide at the back edge (X −6.4 … +7.4), 9 at Y ≈ 11, a 4-stud throat at Y ≈ 4 and an 8.6-wide lip
      pool.
  - **Against the character (5.5):**
    - The cliff stands 17 above the pool (3.1 C): unclimbable, a real landmark.
    - The fall is 16.4 tall and 7–8.5 wide (1.3–1.5 C wide), so a character can stand behind or in front of it.
    - The pool is 32 × 15 (5.8 × 2.7 C) and 0.8 deep (ankle-deep, wadeable). The top channel is 0.3 deep.
    - The two pool boulders are about 5 wide and 4.5–5 tall (0.9 C): cover-sized.
    - The stepped columns' tops are at z 11.5–12 (2.1 C) and the low corner boxes at z 2.4–4 (step-up height for the
      box, not the cliff). The pines are 6–7.2 tall (1.1–1.3 C), the foot pines about 5.
  - **Why this size.** It matches the terrain grid, W03's tile, the kit's one waterline (W03, M032, M034: pool water
    1.0), and lets an M034 streambed placed 16.4 studs up chain into the top channel. W03's 20.5 cliff would read
    about 15 % taller than the sheet.
- **Build frame:** front −Y, +X right, ground z 0 = the flat underside. The fall faces −Y. The river flows from the
  back edge (+Y) over the lip to the pool and out of the front (−Y). Tile X −16 … +16, Y −16 … +16. Origin = bbox
  bottom centre (the tile centre within ±0.1).

### 1.2 Measured views (`measure_out.txt`)

| View (cell box) | Silhouette bbox (sheet px) | W : H | G | R | W | F | S | D |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (22,64,544,467) | 33–537 × 76–464 | 1.298 | 19.6 % | 36.1 % | 21.4 % | 12.2 % | 0.6 % | 1.5 % |
| "Rear" three-quarter (550,64,1001,467) | 557–989 × 73–466 | 1.099 | 19.6 % | 42.9 % | 16.1 % | 11.1 % | 0.8 % | 1.4 % |
| Front (22,516,285,745) | 27–283 × 517–741 | 1.142 | 17.0 % | 40.0 % | 19.9 % | 13.1 % | 0.4 % | 0.9 % |
| Side "(right)" (292,516,507,745) | 302–497 × 526–735 | 0.933 | 17.5 % | 57.6 % | 6.8 % | 9.4 % | 0.5 % | 1.1 % |
| "Rear" (513,516,772,745) | 519–759 × 517–741 | 1.071 | 18.3 % | 42.6 % | 17.1 % | 13.1 % | 0.3 % | 0.6 % |
| Top (779,510,1001,745) | 787–990 × 516–741 | 0.903 (W : H) | 22.5 % | 21.6 % | 32.0 % | 14.4 % | 1.2 % | 0.5 % |

O (outlines, crevices, pink flowers) is 7.3–8.6 %. **Verifier tolerance:** shares ±4 points (F ±3, S and D ±1.5) unless
stated; positions ±0.06 of W / H unless stated.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .27 | .45 | .62 | .70 | .74 | .81 | .91 | .80 | .83 | .89 | .89 | .84 | .91 | .98 | .85 | .79 | .72 | .56 | .42 | .31 | .24 |
| r34 | .31 | .41 | .55 | .68 | .73 | .80 | .79 | .78 | .79 | .81 | .84 | .96 | .96 | .84 | .91 | .79 | .78 | .73 | .53 | .38 | .27 |
| Front | .32 | .74 | .78 | .94 | .94 | .83 | .94 | .96 | .83 | .85 | .90 | .85 | .81 | .79 | .83 | .97 | .96 | .83 | .75 | .39 | .17 |
| Side | .17 | .32 | .69 | .75 | .82 | .94 | 1.0 | .89 | .81 | .82 | .82 | .80 | .90 | .88 | .79 | .73 | .54 | .37 | .38 | .32 | .22 |
| "Rear" | .33 | .75 | .83 | .90 | 1.0 | .89 | .83 | .93 | .81 | .77 | .77 | .82 | .81 | .87 | .88 | .85 | .99 | .96 | .83 | .72 | .17 |

- The front and "rear" profiles are a **flat cliff rim at h .70–.75 with pine tips** at .94–1.0 (front f .15–.20,
  .30–.35, .75–.80; "rear" .20, .35, .80–.85) and the channel's rocks at .83–.90 in the middle. The far ends fall to
  .17–.33 (the corner pines and low boxes).
- f34: the rim rises from .62 (f .10) to .74–.81 (f .20–.25); the peaks .91 (f .30) and .98 (f .65) are pines; the right
  end falls .72 → .24 over f .80–1.0 (the right corner pine and boulder).
- Side: the cliff body at .80–.89 over f .15–.65 (pines .94–1.0 at f .25–.30), dropping to .37–.38 at f .85–.90 (the
  pool side, the curtain and a boulder).

**Bottom profiles** (lowest silhouette pixel):

```
f34    .22 .18 .15 .12 .08 .05 .01 .01 .01 .01 .00 .01 .01 .01 .01 .01 .04 .08 .13 .17 .22
r34    .24 .17 .14 .11 .08 .06 .04 .04 .03 .02 .01 .01 .02 .02 .03 .04 .05 .06 .06 .08 .20
front  .19 .03 .01 .01 .01 .00 .01 .01 .01 .01 .00 .01 .00 .01 .00 .01 .01 .02 .01 .03 .09
rear   .11 .08 .06 .00 .00 .00 .01 .01 .01 .01 .00 .01 .01 .00 .00 .00 .01 .01 .03 .07 .08
side   .11 .01 .01 .01 .02 .00 .02 .02 .00 .01 .02 .00 .00 .00 .00 .00 .00 .00 .00 .00 .03
```
- f34: the pool is drawn as a **hexagon**: a front-left edge falling at slope 0.50–0.58 (screen) over f 0–.30, a
  **screen-horizontal front edge from f .30 to .75**, and a right edge rising at 0.67–0.71 over f .75–1.0
  (`edges_out.txt`). A rectangle can't give that in an orthographic view (§3.1).
- r34: the lowest point is at f .45–.55; the front edge rises to the right at about 0.18 and the left side to the left
  at 0.38–1.1.
- front / rear / side: flat bottoms (slab bottoms), front-corner chamfers of 1–3 % at the ends.

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .46@.30 .70@.17 .98@.00 .93@.02 .89@.03 .80@.07 .72@.10 .67@.14 .49@.25 .39@.29 .01@.63
r34    .03@.51 .81@.17 .97@.03 .98@.00 .89@.05 .81@.09 .77@.11 .70@.17 .50@.24 .18@.52 .00@.57
front  .71@.13 .95@.05 .98@.00 .96@.01 .92@.02 .91@.02 .89@.03 .88@.03 .76@.11 .67@.15 .44@.33
side   .73@.24 .99@.01 .98@.02 .92@.05 .73@.08 .71@.09 .68@.10 .65@.11 .51@.17 .40@.24 .01@.29
rear   .73@.15 .99@.01 .98@.00 .96@.01 .95@.02 .94@.02 .92@.03 .90@.04 .84@.07 .71@.15 .63@.20
top    .95@.03 .99@.01 .98@.01 .98@.01 .99@.00 .98@.01 .99@.00 .97@.02 .97@.02 .97@.02 .95@.03
```
- Front / rear: **the cliff block is 0.88–0.96 of the width from h .1 to .7** (straight vertical sides; the side walls
  stand at the tile edges), then the grass top and pines.
- Side: **the cliff is 0.65–0.73 of the width from h .4 to .7** (screen left, f .08–.80), the pool and curtain take the
  remaining right part; the bottom row (h 0) starts at f .24 (the low boxes stand at f 0–.33 lower down).

**Curtain extents** (`curtain_out.txt`; the W / F run through the curtain at each h; f of the view's bbox):

| View | Top of the curtain (lip) | Mid-fall (h .45–.60) | Near the foot (h .25–.30) | Centre |
| --- | --- | --- | --- | --- |
| Front | h .70 | f .40–.61 (0.21 W = 6.7 studs) | .37–.66 (with spray) | .505 |
| "Rear" | h .70 | f .39–.63 (0.24 W) | .37–.70 | .51 |
| f34 | h .70 | f .46–.60 (0.14 W) | .45–.72 | .53 |
| r34 | h .70 | f .49–.66 (0.17 W) | .49–.76 | .575 |
| Side | h .65–.68 | f .73–.79 (edge-on, 1.5–2 studs), bowing out to f .77–.86 at h .30 | | |

The side cell shows the curtain **leaning out about 1.5 studs** from the lip to the foot (W03's LEAN 1.0).

**Top view** (`topscan_out.txt`; u = x fraction, X = −16 + 32u; v = row fraction from the back):

| Band | v | What | Plan (studs) |
| --- | --- | --- | --- |
| Grass top | 0 – .36 | left lawn u 0–.35, right lawn u .65–1.0, channel between | Y +16 … −0.7 (Y = 16 − 46.4 v) |
| Channel at the back edge | .02 | water u .30–.73 | X −6.4 … +7.4 (13.8 wide) |
| Channel | .10 | u .37–.66 | X −4.2 … +5.1 (9.3) at Y ≈ 11.4 |
| Throat | .26 | u .43–.56 between two rocks | X −2.2 … +1.9 (4.1) at Y ≈ 4 |
| Lip pool | .34 | u .36–.63 | X −4.5 … +4.2 (8.7) at Y ≈ 0 |
| Cliff face (drawn) | .36 – .66 | columns, curtain u .36–.64 | face line Y ≈ −0.7 |
| Pool | .66 – 1.0 | water u .01–1.0 by v .74 | Y −0.7 … −16 (15.3 deep), full width |

Rocks (top view blobs): on top T1 u .23–.36 v .01–.13 (4.4 wide, at the channel's left bank by the back edge), T2 u
.69–.79 v .03–.15 (3.5, right bank), T3 u .90–.98 v .15–.26 (2.8, right edge), T4 u .35–.43 v .20–.28 (2.7) and T5 u
.57–.67 v .21–.31 (3.1) at the throat; in the pool K1 u .13–.28 v .76–.89 (5.2, front-left), K2 u .78–.93 v .76–.90 (4.9,
front-right); at the cliff foot u .71–.78 v .62–.70 (2.7), u .01–.10 v .67–.72 (2.8), u .10–.17 v .70–.75 (2.2), u
.26–.31 v .62–.69 (1.6). Pine crowns at the top-left (u .1–.2, v .15–.30) and top-right (u .7–.8, v .2–.35); the
left low box's pine at u .05–.12, v .55–.62.

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, `g_f34.png`).** A camera at the **front-right** (the pool's right side rises to the
right; the low box's tan front face falls to the right on the lower left). The cliff and the curtain are drawn almost
frontally (the left rim slopes only 0.155 on screen, which gives az ≈ 19° at e 26°), the pool as a hexagon (its edges
fit az ≈ 40–45°). The curtain's width fraction 0.14 fits az 35 (8 · cos 35 / 44.6). Use **`f34_sheet (30, 26)`**
(§3.1).
- **Cliff, left block** f .10–.45: columns with flat bevelled tops under the grass, rim h .62 → .74 rising to the
  right; a stepped column f .25–.35 (top h .43–.45, bush cap); a narrow flank column left of the curtain f .41–.46 (top
  h .45); hanging lime bushes on the face at f .27–.31 h .55–.65.
- **Curtain** f .46–.60, lip h .70, flaring into white spray at h .25–.37.
- **Cliff, right block** f .59–.85: two to three tall columns (rim h .72–.80), a stepped column f .68–.78 (top h .53,
  bush cap), a small rock f .63–.68 at the foot.
- **Top:** left lawn f .15–.45 h .62–.85 with a pine (f .25–.35, tip h .91), dark ferns, white / pink / yellow flowers;
  right lawn f .58–.80 h .78–.90 with a pine (f .60–.70, tip h .98); the channel between with rocks (f .45–.52 h .85–.95
  at the back, f .55–.60 h .78–.83), foam patches, a tan dirt patch at f .40–.44 h .70–.73.
- **Foot:** low grass box at the front-left f .00–.13 (tan / brown soil sides h .13–.30, a pine f .02–.14 to h .50,
  bushes and daisies); boulders f .20–.30 h .15–.25, f .35–.45 h .22–.35; at the right a grass ledge with a pine (f
  .80–.88, h .40–.55) behind a boulder f .83–.93 h .30–.40.
- **Pool:** f .17–1.0 at the bottom; boulders in foam rings f .31–.45 h .03–.20 (big, front-left) and f .70–.81 h
  .12–.24 (big, front-right); foam patches and holes over the whole surface.

**"Rear three-quarter" (`g_r34.png`).** The fall faces the camera, the pool spills to the lower right, the cliff's left
side face is visible with two low boxes along it: a **front-left three-quarter** (az ≈ −25, e ≈ 24; §3.2). Curtain f
.49–.66 (lip h .70); left block f .08–.48 with a stepped column f .25–.40 (top h .58, bush cap); right block f .63–.92
with a stepped column f .73–.83 (top h .51); pines on top at f .22–.33, .52–.62, .65–.75, foot pines at f .16–.26 and
.85–.95; boulders f .19–.29, .29–.41, .38–.50 (left foot), .73–.83 (in the pool, foam ring), .74–.90 (right foot).

**Front (`g_front.png`).** az 0, e ≈ 10. Left to right (f; top h): leftmost corner column C1 .03–.10 (.70); C2 .10–.23
(.68); C3 .23–.37 (.68); a narrow recessed flank .37–.40 (to the pool); **curtain .40–.61**; C4 .61–.73 (.70); C5
.73–.88 (.70); C6 .88–.95 (.72, down to h .40). Stepped columns S_L f .13–.29 (h .17–.50, flat top with a lime bush)
and S_R f .71–.84 (h .17–.47, bush cap). Hanging lime bushes at f .20–.26 h .58–.67 and f .63–.67 h .62–.66. Boulders:
f .29–.39 h .18–.32 and f .06–.16 h .18–.26 (left foot), f .65–.70 h .20–.29 and f .89–.99 h .17–.26 (right foot);
pool boulders f .14–.29 h .08–.21 and f .64–.78 h .08–.20. Corner pines f .01–.13 (h .25–.45, on the low box B1, tan
side at f .00–.12 h .17–.27) and f .87–.96 (h .27–.44, on a grass ledge). Top: pines f .13–.23, .30–.38 (left) and
.70–.80 (right); rocks in the channel at f .40–.48 h .73–.80, .45–.53 h .80–.90, .56–.65 h .70–.80.

**"Rear" (`g_rear.png`).** **A second front view** (az ≈ 0, e ≈ 12; §3.3): the curtain f .40–.63 faces the camera, the
pool runs across the bottom, the same stepped columns (f .16–.31 top h .50, f .66–.79 top h .47), the same corner pines.
No back face is drawn anywhere on the sheet.

**Side "(right)" (`g_side.png`).** The pool and the curtain are at the **screen right**, the cliff body on the left: from
−X (az 270) the screen right is the front, which fits the front and top cells; from +X it would put the pool at the back
(§3.4). The cliff fills f .08–.72 with three column faces (f .10–.33 tall, .33–.60 a tall stepped column reaching
h .47 with a bush cap, .60–.72); the top's grass at h .70–.75 with two pines (f .22–.36 to h 1.0, f .58–.68 to h .88);
the curtain's edge at f .72–.80 bowing out to .86; the pool f .58–1.0 at h 0–.25 with three small boulders. **Two low
boxes stand at the bottom left** (f 0–.18 with a bush, f .18–.33 with a pine; tops h .18 and .15).

**Top (`g_top.png`; image top = back).** A high front view (e ≈ 50°, §3.5): grass halves left and right with pines,
ferns and flowers; the channel from the back edge (13.8 wide) down to the lip; the curtain drawn as a vertical band at
u .36–.64; the cliff face's columns u 0–.36 and .63–1.0 at v .36–.66; the left low box (grass, pine, flowers) at u 0–.22
v .54–.66; the pool across the whole front with white spray at the centre (v .62–.80) and the two big boulders near
the front corners in foam rings.

**Close-ups.**
- **1. Cliff Top Junction** (673,790,1003,961): a grass slab with a thin lime edge (no soil band visible) resting on
  **flat column tops**; the column under it has a few big flat facets (each 2–3 studs across at this scale); a lime fern
  hangs over the edge; daisies, pink and yellow flowers on the grass.
- **2. Underneath View** (673,1003,1003,1220): the top water plane from below (its underside a deeper cyan `#06B1F9`),
  the curtain's top tucked under the plane's front edge and its sides **behind** the two cliff walls, drawn as three
  rounded lobes with scalloped bottoms; the walls are big flat-faceted prisms ("join surface").
- **3. Water Plane Thickness** (673,1262,1003,1390): the pool slab's cut edge: a cyan top with lighter blobs and white
  foam, a **darker cyan side face** (`#01A8F4`) of uniform thickness (about 1 stud at this scale); a rock and the
  curtain's foot behind.

### 1.4 Parts (Exploded Parts & Assembly (20,790,663,1289), `expl.png`)

The exploded parts are drawn in an iso view at about 1.3–1.6× the hero's scale. **The hero and the front / top cells
govern sizes**; the exploded gives the part list, the shapes and the slab language.

#### Top Water Plane: (313,789,438,820), `z_expl_top.png`

- **Shape:** a thin flat rectangular **slab** of light cyan (`#41E2FD`, lighter blobs on it), side faces darker cyan,
  about 1 stud thick at the exploded scale. It sits on the cliff top over the channel; the curtain hangs from its front
  edge (close-up 2).
- **Hero part:** the top channel's water: one flat shell, top z 17.4, over the channel bed (z 17.1), from the back edge
  to the lip, following the channel polygon (§2.2) and tucked 0.3 under the grass banks.
- **Construction:** `_top_water()`: the channel polygon grown 0.3 under the banks, extruded 17.0 → 17.4 (its bottom 0.1
  inside the bed), the back seam face inset 0.02 from Y = 16; the front edge rounds over the lip into the curtain's top
  (the curtain shell starts 0.02 below it, never coplanar). 20–60 tris.

#### Cliff Top (Grass & Foliage): (150,780,520,960)

- **Shape:** a **rock-sided block** (the upper 3–4 studs of a row of columns, their front faces big flat facets) with a
  **lime grass slab** on top (thin lime edge overhanging slightly), two pines, dark fern bushes, white / pink / yellow
  flowers, a grey rock; a lime fern hangs over the front edge.
- **Hero part:** the cliff's top layer on each side of the channel: the grass slab z 17.4 → 18.0 over the column tops,
  with its dressing; the part shows the left half (the side with two pines).
- **Construction:** `_grass_top(side)`: a Delaunay / grid cap of the half's polygon (spacing about 2, no z jitter beyond
  0.05: "No fine detail or noise"), a 0.6 lime edge band, an overhang lip 0.15–0.3 beyond the column faces; the channel
  edge follows §2.2 with a 0.6 vertical bank down to the water. The part = this cap + the upper 3.5 studs of the columns
  under it + its dressing.

#### Cliff Wall Pieces: (131,920,420,1150), `z_expl_walls.png`

- **Shape:** **three tall columns in a row** and **one shorter column in front**, plus two loose rocks beside the curtain
  (a tall one and a small one). Every column is a chunky 7–9-sided prism with **big flat facets** (several per face,
  each 1.5–3 studs at hero scale), a slight taper, a once-chamfered rim and a **broad flat top**. Screen W : H (iso, top
  included): left .81, middle .62, right .54, front .81.
- **Hero part:** the front column row C1–C6, the flanks, the stepped columns S_L / S_R, and the side-wall columns.
- **Construction:** `_column(w, d, h, seed, yaw)`: superellipse rings (7–9 points, exponent 2.4–3) at 3 heights (foot
  1.04 R, middle 1.0, shoulder 0.95), a chamfer ring 0.3 in and 0.4 down from a **flat top**, ring centres offset ≤ 0.2,
  radius jitter by broad sectors ±5 %; flat bottom; **50–70 tris** each. Copy M032's column recipe (`m032.py`), not
  `K.hull_rock`. Split each side face at most into 2–3 triangles with slightly different normals (facets), never into
  confetti.

#### Waterfall Mesh (Curtain): (419,850,506,1033), `z_expl_top.png`

- **Shape:** a broad vertical **sheet with three rounded lobes** (vertical flow bands) whose tops roll over the lip as
  three rounded caps, light cyan crests (`#6EEEFE`) and deep cyan valleys (`#03C0FC`), white streaks, the bottom
  breaking into white spray. "Attaches to top and behind rock walls."
- **Hero part:** the curtain from the lip (z 17.4, Y −1.0) to the pool (z 1.0, Y −2.5), 7.2 wide at the lip and 8.4 at
  the foot (X ±3.6 → ±4.2), its sides tucked 0.4 behind the flanking columns.
- **Construction:** `_curtain()`: a closed thin shell (0.25 thick) built from a cross-section of three shallow U-lobes
  (lobe depth 0.4, 4 points per lobe) swept down 5–6 rings with the lean (Y −1.0 → −2.5) and the widening; the top ring
  rolls forward over the lip by 0.5 (the rounded caps). 120–200 tris. WorldModeling §12.3: "a broad gently folded
  curtain with 2–4 large flow bands".

#### Foam Ribbon: (394,1033,519,1077), `z_expl_water.png`

- **Shape:** a flat **oval ring with a scalloped outer edge**, white with cyan blobs, the spray rising from it. In the
  hero it is the band round the curtain's foot.
- **Hero part:** a flat ring round the foot, outer 11 × 6, inner 8 × 3, centred (0, −3.0), z 1.03 → 1.07.
- **Construction:** part of the foam shell (§2.4); 12–16 scallops on the outer edge; 3–5 round holes.

#### Splash Disc: (394,1095,550,1158), `z_expl_water.png`

- **Shape:** a flat **ellipse** with a scalloped edge, white on cyan, carrying a crown of **white spiky splash cones**.
- **Hero part:** the disc in front of the curtain's foot, 15 × 8 (the top view's spray band u .28–.75), centred (0,
  −5.0), z 1.04 → 1.08, with **10–14 splash spikes** (3-sided pyramids 0.6–1.0 wide at the base, 1.2–3.5 tall, the
  tallest nearest the curtain) standing on it round the foot.
- **Construction:** part of the foam shell; the spikes are separate closed little pyramids in the same foam key.

#### Water Plane (+ Foam): (256,1120,588,1239), `z_expl_water.png`

- **Shape:** a **flat cyan slab of uniform thickness** with a lighter blob pattern, two boulders standing on it in white
  foam rings with holes; drawn with a stepped (notched) front-right corner.
- **Hero part:** the pool: water top z 1.0 from the cliff foot to the front edge and both side edges, side faces 0.2 →
  1.0 cyan at the tile edges ("thickness", close-up 3), over a bed z 0.2; foam rings round K1 and K2 and the foot
  boulders.
- **Construction:** `_pool()`: the pool polygon (§2.2) extruded 0.1 → 1.0 (bottom 0.1 inside the bed slab), the edge
  faces inset 0.02 from the tile edges; 20–40 tris. No ripples in the mesh (the light blobs are the exported water
  texture and the bed patches, §5).

#### Rock Pieces: (50,1077,300,1258)

- **Shape:** about **eleven faceted rocks** in a ladder of sizes (exploded 130 … 30 px wide: large, medium, small and
  pebbles); domed with a flat crown, flat bottoms, big flat facets, height about 0.75–0.9 × width.
- **Hero part:** the pool boulders K1, K2, the foot boulders, the channel rocks on top, pebbles.
- **Construction:** `_rock(w, h, seed)`: a convex hull of 3–4 jittered rings (bottom ring 0.95 R at z 0, widest 1.0 R
  at 0.25 h, shoulder 0.8 R at 0.7 h, a 4–5-point crown 0.5 R at h), 7–9 points per ring with irregular angular jitter
  (±0.3 of the spacing); large 60–80 tris, medium 40–50, small 24–36, pebbles 8–12. `K.hull_rock` with explicit rings
  and `keep_bottom=True` is a fine base; no ico-spheres, no vertex noise (M023 round 1).

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0). Screen ↔ plan for the front cell (az 0, e 10, 8.03 px/stud):
`X = −16 + 32 f`, `z ≈ (28.0 h − 0.174 (Y + 16)) / 0.985`. The sheet is a perspective drawing, so these are starting
values: **the screen targets in §2.5 govern.**

### 2.1 Levels (the tile contract)

| Level | z | Notes |
| --- | --- | --- |
| Ground / underside | 0 | one flat bottom for the whole tile (cliff, boxes, pool bed) |
| Pool bed | 0.2 | `m037_bed`; the bed slab 0 → 0.2 under the whole pool |
| Pool water | 1.0 (shell 0.1 → 1.0) | `m037_water`; W03, M032 and M034 share this waterline |
| Foam (pool, ribbon, disc) | 1.03 → 1.08 | `m037_water_foam`, never within 0.02 of a water face |
| Low boxes B1 / B1b / B2 | tops 2.4 / 4.0 / 2.6 | soil sides, grass tops |
| Stepped columns S_L / S_R | tops 12.0 / 11.5 | flat tops with a lime bush |
| Main column tops | 17.2 – 17.6 | flat, bevelled, under the grass slab |
| Top channel bed | 17.1 | `m037_bed` (M034's 0.7 + 16.4) |
| Top channel water | 17.4 (shell 17.0 → 17.4) | `m037_water` (M034's 1.0 + 16.4) |
| Grass top | 18.0 (slab 17.4 → 18.0) | (M034's bank 1.6 + 16.4) |
| Curtain | 17.4 at the lip → 1.0 at the foot | `m037_water_fall` |
| Pines on top | to 24.2 – 25.2 | the bbox top |

### 2.2 Plan polylines

| Line | Points (X, Y) | Sheet evidence |
| --- | --- | --- |
| Cliff face (main columns' front faces) | (−16, −1.0) → (−4.4, −1.0); (+3.6, −1.2) → (+16, −0.8), ±0.5 per column | top view face base v .66 → Y −0.7; the front cell's flat rim |
| Curtain notch | X −3.6 … +3.6 at the lip, recessed wall behind at Y +0.4 | front cell curtain f .40–.61; W03 NOTCH 1.4 |
| Channel left bank | (−7.0, 16) → (−7.0, 13) → (−4.2, 11.4) → (−2.2, 5.0) → (−2.2, 3.0) → (−4.5, 0.6) → (−3.6, −1.0) | top view rows v .02 / .10 / .26 / .34 |
| Channel right bank | (+7.0, 16) → (+7.0, 13) → (+5.1, 11.4) → (+1.9, 5.0) → (+1.9, 3.0) → (+4.2, 0.6) → (+3.6, −1.2) | same |
| Pool | X −16 … +16, Y −16 … the cliff foot (−1.0), minus the low boxes and the stepped-column feet | top view v .66–1.0 full width; front cell water band across the whole bottom |
| Low box B1 (front-left, pine) | X −16 … −10.5, Y −6.5 … −1.5 | front cell f .00–.12; top view u 0–.22 v .54–.66 |
| Low box B1b (behind B1, bush) | X −16 … −13.0, Y −3.0 … −1.0, against the cliff | side cell's second box; r34's left boxes |
| Low ledge B2 (front-right, pine) | X +12.2 … +16, Y −5.0 … −1.0 | front cell f .87–1.0 h .25–.30; f34 right ledge |

- **The channel is 14 wide at the back seam (X −7 … +7, the M034 contract)**, narrows to about 9 at Y 11.4, pinches to a
  4-stud throat between rocks T4 / T5 at Y 3–5, opens into an 8.5-wide lip pool and pours over the 7.2-wide lip.
- **Back wall (Y = +16):** a flat rock joining face from z 0 to 17.4 with the channel's bed and water faces at the seam
  (WorldModeling §12.2: "a flat rear/connector region"; no sheet view shows the back, §3.3).
- **Side walls (X = ±16):** columns whose outer faces touch X = ±16 (±0.3) from Y −1 to +16, tops 17.2–17.6, the grass
  slab flush with the tile edge.

### 2.3 Columns (front row; yaw ±10°, broad face toward −Y)

| Column | Centre (X, Y) | Footprint w × d | Top z | Front-cell target (f; top h) |
| --- | --- | --- | --- | --- |
| C1 (left corner) | (−14.2, +1.2) | 3.6 × 4.5 | 17.4 | f .03–.10; .70 |
| C2 | (−10.7, +1.0) | 4.4 × 4.2 | 17.2 | f .10–.23; .68 |
| C3 | (−6.5, +1.0) | 4.4 × 4.0 | 17.6 | f .23–.37; .68 |
| F_L (left flank, recessed) | (−4.0, +0.2) | 1.6 × 2.4 | 10.5 | f .37–.40; to the pool (f34 f .41–.46, top h .45) |
| Notch wall behind the curtain | (0, +1.2) | 8.0 × 1.6 | 17.0 | hidden behind the curtain; `m037_bed`-blended |
| C4 | (+5.5, +1.0) | 4.0 × 4.2 | 17.4 | f .61–.73; .70 |
| C5 | (+9.8, +1.2) | 4.8 × 4.4 | 17.6 | f .73–.88; .70 |
| C6 (right corner) | (+14.0, +1.0) | 3.6 × 4.2 | 17.0 | f .88–.95; .72 |
| S_L (stepped, bush cap) | (−9.3, −3.3) | 5.0 × 4.2 | 12.0 | f .13–.29; .48–.50 |
| S_R (stepped, bush cap) | (+8.8, −3.3) | 4.2 × 4.0 | 11.5 | f .71–.84; .45–.48 |
| Side walls (3 per side) | X ±14.4, Y +5.5 / +9.5 / +13.5 | 3.4 × 4.2 | 17.2–17.6 | side cell f .10–.33, .33–.60 faces |
| Core block | X −14 … +14, Y +2.5 … +16 | | 17.2 | hidden; its back face is the joining face |

- Columns overlap their neighbours 0.3–0.6 and sink 0.3 below z 0.2 into the bed / ground; the grass slab rests on
  their flat tops (close-up 1). A dark V crease separates each pair full height.
- **Every main column face is a big flat facet:** each visible side ≥ 1.5 studs wide and ≥ 4 tall, split at most into
  2–3 triangles of slightly different normals.

### 2.4 Water, foam, rocks, vegetation

| Item | Centre (X, Y), base z | Size | Target |
| --- | --- | --- | --- |
| Curtain | lip (0, −1.0, 17.4) → foot (0, −2.5, 1.0) | 7.2 → 8.4 wide, 3 lobes, 0.25 thick | front f .40–.61, lip h .70 |
| Top water | channel polygon, 17.0 → 17.4 | 14 → 4 → 8.5 wide | top view rows |
| Pool water | pool polygon, 0.1 → 1.0 | 32 × 15 | front h 0–.09 band |
| Foam ribbon (curtain foot) | (0, −3.0), 1.03–1.07 | outer 11 × 6, inner 8 × 3 | spray band front f .28–.66 |
| Splash disc + 10–14 spikes | (0, −5.0), 1.04–1.08; spikes to 2.5–4.5 | 15 × 8 | top view spray u .28–.75, v .62–.80 |
| Pool foam rings | round K1, K2 (0.6 wide) and the foot boulders (0.4) | | top view rings |
| Pool foam patches | 8–12 broad blobs and a scalloped strip along the cliff foot | 0.6–2.0 | F share |
| Channel foam | 3–4 patches at the throat and the lip | 0.5–1.5 | f34 channel foam |
| K1 big pool boulder (front-left) | (−9.3, −10.5), 0.2 | 5.2 × 4.8, top z 5.0 | front f .14–.29 h .08–.21 |
| K2 big pool boulder (front-right) | (+11.2, −10.0), 0.2 | 4.9 × 4.6, top z 4.8 | front f .64–.78 h .08–.20 |
| K3 foot boulder left of the fall | (−5.2, −4.5), 0.2 | 3.2, top 4.2 | front f .29–.39 h .18–.32 |
| K4 foot rock right of the fall | (+5.6, −4.0), 0.2 | 1.8, top 2.8 | front f .65–.70 h .20–.29 |
| K5 right-corner boulder | (+14.2, −5.5), 0.2 | 3.2, top 3.4 | front f .89–.99 h .17–.26 |
| K6 left-corner boulder | (−12.6, −7.5), 0.2 | 2.8, top 3.0 | front f .06–.16 h .18–.26 |
| T1–T5 channel rocks on top | (−6.8, 13.0) 4.4; (+7.6, 12.5) 3.5; (+14.8, 6.7) 2.8; (−3.2, 4.6) 2.7; (+3.4, 4.2) 3.1; base 17.7 | height 0.6–0.8 × w | top view blobs |
| T6, T7 lip rocks | (−4.6, −0.2) 1.8; (+4.6, −0.4) 2.0; base 17.1 | | front f .40–.48 h .73–.80, .56–.65 h .70–.77 |
| Pebbles | 6 in the pool, 3 on the low boxes | 0.4–0.8 | |
| Top pines PL1, PL2, PR1, PR2 | (−11.5, 8.0), (−6.0, 11.0), (+8.5, 6.0), (+12.0, 11.5) on 18.0 | 7.2, 6.2, 7.0, 6.0 tall | front tips h .94–.99 |
| Foot pines PF1 (B1), PF2 (B2) | (−13.4, −4.0) on 2.4; (+14.0, −3.0) on 2.6 | 5.0, 4.8 | front f .01–.13 / .87–.96 |
| Dark fern bushes on top | 7–9, along the rims and the channel | 1.2–2.0 | `m037_leaf` |
| Lime bushes | S_L and S_R caps, B1b, 2–3 hanging on the face (front f .20–.26 h .58–.67, f .63–.67 h .62–.66) | 1.4–2.2 | `m037_leaf_lime` |
| Flowers | 8–10 white daisies, 4–6 pink, 6–8 yellow, on the tops and B1 | Ø 0.6–0.9 | |
| Dirt patches | 2 on top at the channel's left bank by the lip and at the back-left corner | 1.5–2.5 | `m037_dirt` |

- **Rocks sit on the water plane** (the sheet's exploded): pool boulders stand on the bed at z 0.2 and rise through the
  water; their part below z 1.0 is `m037_bed`-blended (wet). Each gets a foam ring. Channel rocks sink 0.3 into the
  grass or the channel bed.
- Keep every rock and bush at least 0.3 inside the tile outline.

### 2.5 Screen targets (renders measured with `measure_render.py`, floor hidden)

- **`front_sheet (0, 10)`** against the front cell **and** the "rear" cell:
  - W : H 1.05–1.20 (sheet 1.142 / 1.071);
  - shares ±4 of the front cell's G 17.0 / R 40.0 / W 19.9 / F 13.1 (±3) / S + D 1.3 (±1.5);
  - top profile mean error ≤ 0.06, every point within ±0.10 (pine tips ±0.12);
  - width per height within ±0.06 at h .1–.7 (the cliff 0.88–0.96 of W there);
  - curtain f .40–.61 (±0.03), lip h .70 (±0.04);
  - columns per §2.3 (±0.04 f), the stepped tops at h .45–.50, the pool band h 0–.09, both pool boulders at
    §2.4 (±0.05).
- **`f34_sheet (30, 26)`** against the hero:
  - W : H 1.15–1.35 (sheet 1.298);
  - shares within ±5 of R 36.1 / W 21.4 / G 19.6 / F 12.2 (±4);
  - top profile mean ≤ 0.08; the bottom profile within ±0.12 (the sheet's hexagonal pool is a known miss, §3.1);
  - width per height ±0.08;
  - curtain fraction 0.12–0.17 of W, centre f .47–.56, lip h .66–.74.
- **`r34_sheet (−25, 24)`** against the "rear three-quarter":
  - W : H 1.02–1.22 (sheet 1.099);
  - shares ±5 of R 42.9 / W 16.1 / G 19.6 / F 11.1;
  - top profile mean ≤ 0.08; width per height ±0.08;
  - curtain fraction 0.14–0.20, centre f .50–.60;
  - the left side face with its low boxes visible at the lower left.
- **`side_sheet (270, 12)`** against the side cell:
  - W : H 0.90–1.10 (sheet 0.933; ours runs wider because the sheet's side squeezes the 32-stud depth, §3.4);
  - shares ±5 of R 57.6 / G 17.5 / F 9.4, W 5–11;
  - the pool and the curtain on the screen right (f ≥ .55), the cliff 0.62–0.78 of W at h .4–.7, the curtain's edge
    bowing out at the right.
- **`top_sheet (0, 50)`** against the top cell:
  - W : H 0.85–0.95 (sheet 0.903);
  - the three bands (grass top ≈ .38, cliff face ≈ .28, pool ≈ .34 of H, each ±0.05);
  - the channel 13–15 wide at the back edge;
  - the pool full width at the front; K1 / K2 near the front corners;
  - shares ±5 of W 32.0 / G 22.5 / R 21.6 / F 14.4.
- **kit `top (0, 89)`:** plan check of §2.2 (channel widths ±1, the pool full width, the cliff face line Y −1 ± 0.6).

### 2.6 How to measure our renders

- Render with the studio floor hidden: `bpy.data.objects["FB_Ground"].hide_render = True`, then
  `K.NS["KIT"]["render_group"](objs, path, az, el)` for each extra camera; restore the floor afterwards. The sheet has
  no ground shadow; with the floor on, its shadow would be classed R and inflate the rock share and the bbox.
- Run `measure_render.py <render> <background hex>` (or rely on the alpha channel). **Render with `vfx=True`**: the
  sheet's curtain, spray and foam are part of every silhouette (the beam and mist previews add to W / F).
- **Check every compared view, including the "rear" cell, the side and the r34**, not only the hero: W : H, shares,
  top profile and width per height.

## 3. View conflicts and resolutions

### 3.1 The hero mixes a frontal cliff with an iso pool

- **Evidence.** The rim and the curtain are drawn nearly frontal (rim slope 0.155 → az ≈ 19°); the pool's outline is a
  hexagon whose two side edges (slopes 0.50–0.58 and 0.67–0.71) fit an az 40–45° iso view with a cut front corner; the
  curtain's width fraction (0.14) fits az 35. The top, front and "rear" cells all show a full rectangular pool with
  square corners. `fit.py` (a slab + cliff-block proxy) cannot separate the cameras (IoU 0.55 for many az / e), so the
  choice rests on these features.
- **Resolution.** Compare the hero with **`f34_sheet (30, 26)`** (between the rim and pool fits; the curtain fraction
  then lands at 0.15). Keep the pool rectangular (the top, front and rear cells, and tiling). Record as a known miss: the
  hero's flat bottom between f .30 and .75 (ours is a V with its lowest point near f .55–.60). The kit front34 (−28,
  12) is self-consistency only.

### 3.2 The "rear three-quarter" is a front-left three-quarter

- **Evidence.** The fall faces the camera and the pool lies in front of it; the cliff's left side face is visible with
  its low boxes; the front edge rises to the right at about 0.18 and the left side to the left at about 0.55, which
  gives az ≈ −30, e ≈ 18–24 (`edges_out.txt`); the curtain fraction 0.17 fits az −25.
- **Resolution.** Compare it with **`r34_sheet (−25, 24)`**. Don't flip the hero for it, and don't compare it with the
  kit rear34 (152, 12), which is a back camera.

### 3.3 The "rear" cell is a second front view; the back is never drawn

- **Evidence.** The "rear" cell shows the curtain facing the camera (f .40–.63), the pool across the bottom, the same
  stepped columns and corner pines as the front cell; its profile matches the front cell's (both rims h .70–.75, both
  cliffs 0.88–0.96 of W). No cell shows the tile's back.
- **Resolution.** Compare both the front and the "rear" cells with **`front_sheet (0, 10)`** (the targets in §2.5 cover
  both). Build the back as a **flat rock joining face** at Y = +16 with the channel's seam faces (WorldModeling §12.2),
  and treat the kit rear (180, 4) as self-consistency (it will show that flat wall: expected, not a miss).

### 3.4 The "side view (right)" is the view from −X, and its depth is squeezed

- **Evidence.** The pool and the curtain are on the screen right. The kit side camera at az 90 sits at +X, so its screen
  right is the model's back, and the front and top cells put the pool at the front. From −X (az 270) the screen right
  is the front, which fits. The cell is also narrower than the tile (W : H 0.933): at the front cell's height scale
  its width is about 24–26 studs of depth, against the top view's 32. Its two low boxes sit at the screen left (the
  back), while the front, r34 and top cells put the low boxes at the front-left corner.
- **Resolution.** Compare **`side_sheet (270, 12)`** with the cell; the kit side (90, 4) is self-consistency. The top
  view governs the depth (32): our side W : H will run about 0.95–1.05 (tolerance in §2.5). Place the low boxes at the
  front-left (B1 with the pine, B1b with the bush behind it against the cliff) and record the side cell's box position
  as a known miss.

### 3.5 The "top view" is a high front view

- **Evidence.** The cliff face, the curtain and the stepped columns are drawn as vertical faces (rows v .36–.66); a
  true top view would show the face as a line.
- **Resolution.** Compare **`top_sheet (0, 50)`** with the cell for bands and layout, and the kit top (0, 89) with the
  plan in §2.2 only.

### 3.6 Exploded and close-ups against the hero

- The exploded parts are drawn 1.3–1.6× larger and in a cleaner arrangement (three columns in a row plus one in front;
  a rectangular top water plane; a pool slab with a notched front-right corner). The hero governs sizes and placement;
  the exploded gives the slab language: **flat plates for every water surface, flat-topped prisms for the columns, a
  grass slab resting on them**.
- The exploded water plane's notched corner: not used (the top, front and "rear" cells show a plain rectangle).

### 3.7 Foam and falling water: meshes (sheet) against VFX (the W03 rework)

- The sheet draws the curtain, the foam ribbon and the splash disc as **separate meshes** ("Waterfall Mesh (Curtain)",
  "Foam Ribbon", "Splash Disc") and calls them "separate effect geometry (not baked)". The W03 rework made all of them VFX
  only, and its verifier then flagged "thin curtain, little foam / splash". M032 and M034 were accepted with **both** a
  thin foam mesh and sockets.
- **Resolution (recommended, decision §8.6):** both. Meshes on water keys (they export as see-through, non-colliding
  pieces): the curtain on `m037_water_fall`, the foam ribbon, splash disc, spikes and pool foam on `m037_water_foam`.
  Sockets for the motion: `waterfall_curtain` beams on the curtain, `waterfall_mist` at the foot, `water_foam` and
  `water_flow` (§7.2).

### 3.8 "Broad, flat-shaded faces" against the user's blended-colour rule

- The sheet's surfaces are near-flat colours with broad patches: the lawn has lighter and darker patches; the water a
  light / deep blob pattern; the curtain light crests and deep valleys; the rock warm-lit / blue-violet shade faces
  (that one is lighting, never paint). Paint only broad position-based patches and bands (§5.5).

## 4. Construction plan (stages 1–3)

1. **Parts first,** each from its own function, checked against its exploded cell:
   - `top_water()` → `CliffFallsTopWater`: the channel water shell with its bed under it. Compare: a thin flat cyan
     plate.
   - `cliff_top()` → `CliffFallsTop`: the left grass slab with the upper 3.5 studs of its columns, two pines, ferns,
     flowers, a rock, a hanging fern. Compare: a rock-sided block with a lime slab top.
   - `cliff_wall()` → `CliffFallsWall`: three tall columns in a row and a shorter one in front, plus a tall and a small
     loose rock. Compare: separate fat prisms with big facets and flat tops.
   - `curtain()` → `CliffFallsCurtain`: the curtain shell alone (3 lobes, rolled lip), carrying the curtain sockets.
   - `foam_ribbon()` → `CliffFallsFoamRibbon`, `splash_disc()` → `CliffFallsSplashDisc` (disc + spikes, carrying the
     mist socket).
   - `pool()` → `CliffFallsPool`: the pool shell, its bed, two boulders with foam rings (as drawn).
   - `rock(size)` → `CliffFallsRockLarge`, `CliffFallsRockMedium`, `CliffFallsRockSmall` (K1, K3, a foot pebble scale).
   - Render a parts shot (`extra`, about (35, 28)) laid out like the exploded (top water above the cliff top, the
     curtain to the right, the walls below, the ribbon and the disc stacked over the pool).
2. **Hero** `CliffFalls`:
   1. **Land shell:** the core block, the columns (one at a time, largest first), the stepped columns, the low boxes and
      the channel bed, exact self-union with the object at the origin; then the grass slabs (two halves) and the
      channel rocks, the pool boulders and foot boulders one at a time; `M.union_loose` (merge-0 union for the fine
      pieces, `m021._union_fine`), `M.fix_bowties`; save the work file between risky steps; floor-cut at z 0.
   2. **Vegetation** (pines, bushes, flowers): separate closed shells in the same object, as on M032.
   3. **Water and foam:** joined into the same object as **separate closed shells**, never unioned with the land: the
      pool shell, the top water shell, the curtain shell, the foam shell (ribbon, disc, spikes, rings, patches).
   4. Origin at the bbox bottom centre; transforms applied.
3. **Budget** (§4.3): hero about 3700–3950 (limit 4000); each part under 1000. If over, drop flowers, then bushes, then
   pebbles; never below 7 sides on a column, never the chamfer ring or the flat tops, never the curtain's 3 lobes.
4. **Placeholder keys** (stage 1): `m037_grass`, `m037_leaf`, `m037_leaf_lime`, `m037_pine`, `m037_bark`, `m037_petal`,
   `m037_pink`, `m037_pollen`, `m037_soil`, `m037_dirt`, `m037_rock`, `m037_bed`, `m037_water`, `m037_water_fall`,
   `m037_water_foam`.
5. **Stage 1 acceptance** (render, compare every view, measure with `measure_render.py` on floor-hidden, vfx renders):
   1. **Overall read:** a block of separate fat columns with flat tops under one grass cap split by a channel; a
      three-band curtain in a notch; stepped bush-capped columns either side; a flat full-width pool with two big
      boulders in foam rings; a white splash disc and spray at the foot; low pine boxes at the front corners.
   2. **`front_sheet (0, 10)`** against the front and "rear" cells; **`f34_sheet (30, 26)`**; **`r34_sheet (−25,
      24)`**; **`side_sheet (270, 12)`**; **`top_sheet (0, 50)`**: all of §2.5.
   3. **Kit views** (front34, rear34, front, side, rear, top, underside): self-consistency; the underside is one flat
      bottom; the rear shows the flat joining wall with the channel seam.
   4. **Parts against their cells;** extras **`junc_cu (−20, 20)`** framed on C2 / C3's tops against close-up 1 (grass
      slab on flat column tops, thin lime edge); **`lip_cu (15, −20)`** framed on the lip from below against close-up 2
      (the top water's underside, the curtain tucked behind the flank columns); **`pool_cu (−35, 25)`** framed on the
      pool's front-left edge against close-up 3 (the cyan side face 0.8–0.9 tall, foam on the top).
   5. **Size:** bbox 32 ± 0.3 × 32 ± 0.3 × 25 ± 1; grass top 18.0 ± 0.05 at the back seam; top water 17.4 ± 0.02;
      pool water 1.0 ± 0.02; pool bed 0.2 ± 0.05.
6. **Stage 2:**
   - zero non-manifold edges and vertices (bowties: `M.fix_bowties`), boundary, wire and loose elements; no zero-area
     faces or n-gons; normals outward; no interior faces from the unions (the core block fully swallowed);
   - no faces under 5° where columns meet columns, the grass slab, the boxes and the bed;
   - the water, curtain and foam shells are closed and stay separate from the land shell; no foam face within 0.02 of a
     water face; the curtain's top 0.02 below the top water's front edge; the water seam faces inset 0.02 from the tile
     edges.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even density. (The exporter writes palette UVs for solid faces and
   its own box-projected UVs for water pieces; the UV layer must still exist and be clean.)

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Main columns C1–C6 + side walls (7–8 sides, 3 rings + chamfer) | 12 | 56 | 672 |
| Stepped columns, flank, notch wall | 4 | 50 | 200 |
| Core block + back joining face | 1 | 40 | 40 |
| Grass slabs (two halves, 2-stud grid, edge band, channel banks) | 2 | 170 | 340 |
| Low boxes B1, B1b, B2 | 3 | 28 | 84 |
| Channel bed + top water shell | 1 | 70 | 70 |
| Curtain shell (3 lobes, 6 rings, rolled lip) | 1 | 170 | 170 |
| Pool shell + bed | 1 | 50 | 50 |
| Foam shell (ribbon, disc, 12 spikes, 7 rings, patches) | 1 | 420 | 420 |
| Boulders K1–K6, rocks T1–T7 | 13 | 40 | 520 |
| Pebbles | 9 | 10 | 90 |
| Pines (4 top, 2 foot; 4-tier star cones + trunk) | 6 | 80 | 480 |
| Bushes (dark ferns 8, lime 6) | 14 | 30 | 420 |
| Flowers | 20 | 8 | 160 |
| **Sum before union** | | | **about 3700** |
| **Hero after the land union** | | | **about 3700–3950** (limit 4000) |
| Parts: TopWater / Top / Wall / Curtain / FoamRibbon / SplashDisc / Pool / RockLarge / Medium / Small | | | about 70 / 750 / 330 / 170 / 120 / 200 / 300 / 70 / 45 / 26 (limit 1000) |

The budget is tight: if the land union goes over, ask the main session before cutting columns (decision §8.7).

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 36 × 40 box inside each, y 1345–1385; `swatch_out.txt`)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Grass / Foliage | (41,1345,77,1385) | `#98C22E` | 77°, 0.76, 0.76 |
| Dirt / Soil | (105,1345,141,1385) | `#DDAE75` | 33°, 0.47, 0.87 |
| Rock | (169,1345,205,1385) | `#AAA7B5` | 253°, 0.08, 0.71 |
| Water | (234,1345,270,1385) | `#00CCFE` | 192°, 1.00, 1.00 |
| Foam (Effect) | (298,1345,334,1385) | `#8AECFE` | 189°, 0.46, 1.00 |

- **Grass:** every rendered lawn is yellower and far more saturated (`#ABCE04`, h 70°, s .98) than the swatch.
- **Dirt / Soil** names two things: the lit dirt patches on top (`#D6AA76`, close to the swatch) and the low boxes'
  soil sides (`#906532`, darker and more saturated).
- **Rock:** the swatch is a cool neutral grey; every rendered rock is **warm in its lit faces** (h 8–20°, s .09–.14) and
  **blue-violet in its shade faces** (h 220–229°, s .20–.31), about half and half. Calibrate on the lit faces.
- **Water:** the swatch equals the pool's deep tone (`#02CFFD`); the rendered water has a light blob tone (`#43E6FD`)
  over it.
- **Foam (Effect)** is drawn cyan-tinted, but every rendered foam, spray and ribbon is **near-white** (`#F0FDFE` …
  `#F9FDFE`) with a pale-cyan shade quartile (`#A8F3FD`). Use the rendered value.

### 5.2 Rendered regions (`samp_out.txt`; median / lit quartile / shade quartile)

| Region | Box / mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- |
| Lawn, exploded cliff top (unshadowed) | (181,845,363,883) G h 60–100 | `#ABCE04` | `#C7E50B` | `#396A02` |
| Lawn, hero left top / right top | (102,185,237,225) / (325,145,420,190) | `#B9D902` / `#8AB603` | `#D0EF02` | `#446F02` |
| Lawn, view medians f34 / r34 / front / side / rear / top | V G h 60–100 | `#9CC303` / `#8CB604` / `#8EB406` / `#8CB606` / `#8FB605` / `#A9CC08` | `#D2ED04` | `#376202` |
| Lime bushes (hanging, ledge caps) | f34 (165,230,190,270) h 55–95; front (75,615,95,630) | `#7DB401` / `#A0B80A` | `#CAED01` | `#305005` |
| Dark fern bushes | V G h 95–125; exploded cliff top | `#125A04` / `#115704` | `#34AD33` / `#2D9312` | `#031C01` |
| Pines | V G h 125–165; exploded | `#046525` / `#056324` | `#1BA234` / `#19A035` | `#01220B` |
| Pine trunks | f34 D v < .5 | `#3C0F01` | `#6C4926` | |
| Flowers white / pink / yellow | f34 | `#FBFBFA` / `#EB7CAF` / `#F6D81A` | `#FEFEFE` / `#F7A3CF` / `#FAE249` | |
| Soil sides, low box (hero) | (37,360,90,395) D+S | `#906532` | `#9D703A` | `#571F01` |
| Dirt patches (lit S) | V S f34 / r34 / top | `#CBA875` / `#D6AA76` / `#DFC177` | `#F9D38E` | `#9C7039` |
| Rock, exploded cliff wall pieces | (131,933,394,1108) R | `#B1A2A4` (352°, .08) | `#D6C5C1` | `#5E637A` |
| **Rock, lit faces v > .7: exploded walls / rock pieces / f34 / front / top** | R | `#CBB6B1` / `#CBB7B3` / `#CCB8B5` / `#C7B6B7` / `#CFBCBA` | `#DFD0CB` | |
| Rock, warm-lit / cool-shade faces (exploded walls) | R by hue | `#C5B2AB` (16°, .13) / `#647391` (220°, .31) | | |
| Rock, close-up 1 lit (near, unshadowed) | (673,790,1003,961) R v > .7 | `#CDB8B3` | `#E3D3C9` | |
| Rock, pool boulders f34 front-left / front-right | (190,380,250,430) / (395,355,445,400) | `#C1A59F` / `#C0A59D` | `#E1CDC6` | `#63667B` |
| Rock, view medians f34 / r34 / front / side / rear / top | V R | `#9892A0` / `#9D8F9A` / `#A59AA4` / `#A1949E` / `#9E959F` / `#8A869A` | | |
| Pool water, exploded plane / hero open (front-right) | W | `#07D3FD` / `#09D9FD` | `#46E7FE` | `#02BCFA` |
| Pool water light tone / deep tone (exploded, about 1/3 and 2/3 of W) | W s < .85 / s ≥ .95 | `#43E6FD` / `#02CFFD` | | |
| Pool slab side face (close-up 3) | (680,1360,940,1385) | `#01A8F4` | | |
| Top water plane part (exploded) / underside (close-up 2) | W | `#41E2FD` / `#06B1F9` | `#53E7FD` | `#06B2FB` |
| Top channel water (hero) | (252,150,327,200) W | `#07C8FC` | `#25E6FD` | `#029CF8` |
| Curtain, exploded mesh W / light crests / deep valleys / F | (419,870,506,1033) | `#45DBFD` / `#6EEEFE` / `#03C0FC` / `#F0FDFE` | `#7AF6FE` | `#03B8FB` |
| Curtain, hero W / light / deep / F | (267,220,327,330) | `#11D3FD` / `#5CF1FE` / `#03C2FC` / `#BDFDFE` | `#6DF7FE` | `#02BAFC` |
| Foam ribbon / splash disc (exploded) | F | `#F7FDFE` / `#E5FCFE` | `#FEFEFE` | `#AAFBFE` / `#A4FAFE` |
| Splash at the foot (hero) / pool foam (hero) | F | `#FBFDFE` / `#F9FDFE` | `#FEFFFF` | `#A5F4FE` / `#CCF8FD` |

### 5.3 How the colour works

- **Hue order (unshadowed, low to high):** rock lit faces 8–20° < dirt / soil 33–43° < yellow flowers 52° < lawn
  69–75° < lime bushes 78° < dark fern bushes 110° < pines 138–141° < water and curtain 187–196° (foam the same hue at s
  ≤ .06) < rock shade faces 220–229° (lighting, not paint) < pink flowers 332°.
- **Grass:** one vivid lime (h 70–75°, s ≥ .95) with broad lighter / darker patches; the lime bushes slightly yellower
  and darker; the ferns a separate dark green; the pines a cool dark green.
- **Rock:** one warm grey; lit faces warm, shade faces blue-violet (lighting). Per-column Tint ±4 % so neighbours
  differ slightly; the flat tops read lighter because they face the sun.
- **Water:** one saturated cyan plane over a **deep teal bed with broad light patches**: the see-through water then
  reads saturated, and the patches give the sheet's light / deep blob pattern (light `#43E6FD` about 1/3, deep
  `#02CFFD` about 2/3). The top channel uses the same key, so it reads the same.
- **Curtain:** a lighter cyan than the pool (exploded median `#45DBFD`); the light crests and deep valleys come from the
  three lobes catching the light, plus the beam streaks.
- **Foam, spray, ribbon:** one near-white pale cyan.
- **Soil / dirt:** the low boxes' sides one mid soil brown; two bare dirt patches on top in the lighter dirt.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are **unshadowed rendered regions** (the exploded parts, the lit rock faces, the open water), not
swatches and not shade quartiles.

| Key | Calibration target (kind) | Where | Finish |
| --- | --- | --- | --- |
| `m037_grass` | `#ABCE04` (green; exploded cliff top lawn, unshadowed; hero left top `#B9D902`; swatch `#98C22E`) | grass slabs, box tops | rough 0.9, `low_spec` |
| `m037_leaf_lime` | `#86B80A` start; render median `#7DB401` ± 12 (green; lit `#CAED01`) | ledge caps, hanging bushes, B1b bush | rough 0.9, `low_spec` |
| `m037_leaf` | `#2A8A12` start; render crown median `#125A04` ± 12, lit quartile ≈ `#34AD33` (green) | dark ferns on top | rough 0.9, `low_spec` |
| `m037_pine` | `#056324` (green; exploded and view medians) | pine tiers | rough 0.9, `low_spec` |
| `m037_bark` | `#6A3E18` start; lit quartile ≈ `#6C4926` (brown) | pine trunks | rough 0.9 |
| `m037_petal` / `m037_pink` / `m037_pollen` | `#F4F4EE` / `#EB7CAF` / `#F6D81A` | daisies / pink flowers / centres and yellow flowers | rough 0.8 |
| `m037_soil` | `#906532` (brown; hero low-box side) | low-box sides, the grass slabs' thin underside lip | rough 0.95 |
| `m037_dirt` | `#D6AA76` (brown; r34 S median; swatch `#DDAE75`) | dirt patches on top | rough 0.95 |
| `m037_rock` | **lit faces median `#CBB6B1` ± 10** (stone; v > .7, exploded walls; f34 `#CCB8B5`); whole-rock median `#B1A2A4` ± 12 (exploded walls); swatch `#AAA7B5` | every column, boulder, rock and grey pebble | rough 0.85 |
| `m037_bed` | `#0B6E8F` start (W03 / M032), tuned so the pool renders `#07D3FD` ± 12 | pool bed, channel bed, the notch wall behind the curtain, rock below z 1.0 (blend) | rough 0.9 |
| `m037_water` | `#00CCFE` start (swatch); render median `#07D3FD` ± 12, s ≥ .88; light patches present | pool and top channel shells | rough 0.15, `kit_transparency` 0.3 |
| `m037_water_fall` | `#45DBFD` start (exploded curtain median); hero curtain W median `#11D3FD` ± 15, light crests (s < .85) ≥ 25 % of its W | curtain shell | rough 0.15, `kit_transparency` 0.2 |
| `m037_water_foam` | `#F2FCFE` start; render F median `#F7FDFE` ± 10, shade quartile ≈ `#A8F3FD` | ribbon, disc, spikes, rings, patches | rough 0.6, `kit_transparency` 0.1 |

- The bed key must **not** contain "water" (the exporter would make the bed a see-through, non-colliding piece). The
  three water keys must (each exports as its own see-through, non-colliding piece).

**Calibration warnings:**
- **Rock:** the lit faces must stay warm (h 5–20°, s .08–.15) and the shade faces blue-violet; a drift to the swatch's
  cool `#AAA7B5` everywhere, or a calibration to the whole-rock median alone, loses the read. Check both targets.
- **Grass:** near the clip in G; keep h 68–76° and s ≥ .93 in the render (lower the specular, not the colour).
- **Water:** judge it by its render median after tuning the bed (W03 found see-through water rendered paler than the
  sheet); in Roblox the exported water texture and `kit_transparency` decide it (Studio check, §7.1).
- **Curtain:** it hangs over the notch wall, so the wall must be the dark bed colour (as the pool's bed is) or the
  see-through curtain will read grey. Check the curtain's render median, not the key.
- Keep the families apart: grass s ≥ .93 lime, soil s .55–.70, dirt s .40–.50, rock s ≤ .15 lit, water s ≥ .88, foam
  s ≤ .10.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Grass slabs:** `grass` base; broad patches (`K.patches(scale≈0.3, level≈0.15)`, 3–4 studs across, about 30 %)
  toward a 25 % `grass`×`leaf_lime` mix; within 0.8 of the channel bank → 25 % `dirt` (trampled, as the sheet's tan bits
  by the lip).
- **Rock:** `rock` with per-column Tint ±0.04; faces below z 1.0 → `bed` (hard, submerged); column feet within 0.6 above
  the water → 25 % `bed` blend (wet band); the notch wall behind the curtain → `bed` (blend in 3 steps from its edges);
  channel rocks below z 17.4 → `bed`.
- **Low boxes:** sides `soil`; tops `grass` with a 0.3 `soil` lip.
- **Pool bed:** `bed` base; broad patches (`K.patches(scale≈0.3, level≈0.15)`, 3 studs, about 35 %) toward a lighter
  bed (`bed` × 1.6 brightness, or a `m037_bed_light` key if needed) so the water shows its light blobs; within 1.0 of a
  boulder → 30 % `rock`.
- **Hard edges only** where materials meet: rock | grass, rock | soil, grass | dirt patch edge, rock | bed at z 1.0,
  water | foam.

### 5.6 Texture (Tint) and finish

- **Tint:** grass amp 0.04 scale 0.5; rock amp 0.04 scale 0.5 (broad, per column); soil amp 0.03 scale 0.6; bed amp
  0.03 scale 0.8; water, curtain and foam amp 0 (the exporter textures water). Never per-triangle confetti ("No fine
  detail or noise").
- **Finish:** roughness per §5.4; metal 0 everywhere; no emission.

### 5.7 Re-measure (final renders against the sheet, same masks)

- Lawn (G h 60–100) median within 10 of `#9CC303` on `f34_sheet`; parts-shot grass top within 8 of `#ABCE04`.
- Rock: lit-face (v > .7) median within 10 of `#CCB8B5` on `f34_sheet` and of `#CBB6B1` on the parts shot; whole-rock
  median within 12 of `#9892A0` (f34); lit faces warm, shade faces blue-violet.
- Water: f34 W median within 12 of `#08D5FD`; light patches (s < .85) ≥ 20 % of the pool's W.
- Curtain: W median within 15 of `#11D3FD` with light crests present; foam / spray F median within 10 of `#F7FDFE`.
- Shares per §2.5 in every compared view.

## 6. Joins, contact and the tile contract

- **Columns into the land:** columns overlap 0.3–0.6 and stand on z 0 through the bed; the grass slab rests on their
  flat tops with its lime edge band (close-up 1); no gaps under columns, no floating tops.
- **Curtain:** its top 0.02 below the top water's front edge, rolled over the lip ("attaches to top"); its sides 0.4
  behind the flank columns F_L and C4's left face ("behind rock walls"); its foot 0.1 under the pool surface, hidden by
  the ribbon. Never coplanar with any rock face (≥ 0.1 gap to the notch wall).
- **Boulders:** pool boulders on the bed z 0.2, sunk 0.3; foot boulders overlap the column feet 0.3; channel rocks sunk
  0.3 into the grass slab or the channel bed.
- **Ground:** one flat underside at z 0.
- **Water and foam:** closed shells, never unioned with the land; foam 1.03–1.08; the water bottoms 0.1 inside their
  beds; the pool's edge faces and the top water's back face inset 0.02 from the tile edges.
- **Tile contract (record for 159, 160 and any waterfall variants):**
  - 32 × 32, ground z 0, grass top 18.0 exactly at the back seam and the side walls;
  - **back seam (Y = +16):** a flat rock joining face 0 → 17.4, grass 17.4 → 18.0 at |X| 7 … 16, channel bed 17.1 and
    water 17.4 at X −7 … +7. This is **M034's seam raised by 16.4**: an M034 `StreambedSection` placed at z +16.4
    behind the tile chains into the channel;
  - **front edge (Y = −16):** open pool water across the whole width (water 1.0, bed 0.2, the cyan slab side 0.2 → 1.0),
    as the sheet draws it. It joins M032-type open water at the same waterline. It does **not** match M034's front seam
    (banks |X| 7 … 16 at 1.6); a stream outlet needs a transition tile or a variant (decision §8.4);
  - **side edges (X = ±16):** cliff from Y −1 to +16 (column faces touching the edge, grass flush); pool water from Y
    −16 to the low boxes (left: Y −16 … −6.5; right: Y −16 … −5.0);
  - no rock, bush or pine crosses an edge (≥ 0.3 inside).
- No coplanar faces between the bed, the water bottoms and the column bottoms; rock bottoms jittered 0.02–0.05 off slab
  levels; exact booleans one piece at a time with the object at the origin (STAGES "Booleans").

## 7. Water, lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** a broad three-band cyan curtain, a flat cyan top water plane and pool with light / deep blobs,
a white foam ribbon and a splash disc with spiky white spray at the foot, foam rings round the boulders, foam patches on
the pool and the channel. No glow, light, fire or particles beyond the spray. WorldModeling §12.3: "Separate land,
bank slope, sand strip, water surface, waterfall curtain, and foam"; "broad gently folded curtain with 2–4 large flow
bands"; "The foam must not z-fight"; "Record waterline and flow direction".

### 7.1 Water (export) and stage 5 (lighting)

- **How water exports** (`export_kit_roblox.py` lines 80–90, 186–188, 541–592): faces whose key
  `flintkit.is_water_key()` accepts (any key containing "water", or `[a-z]\d+_water(_…)?`) become **separate see-through
  pieces, one per key**: SmoothPlastic (not Glass, so a Beam behind the pool stays visible), the key's 512 × 512
  tileable texture (`kitwater`, one tile per 16 studs, box-projected UVs in studs from the asset origin),
  `transparency` from the material's `kit_transparency` (else 0.4; 0.3 for "deep", 0.5 for "shallow"), **no collision,
  no shadow**. The asset's **first `water_flow` socket** gives every water piece of the asset a `flow` (direction and
  speed).
- **Expected STATS for the hero:** solid 1 (or 2 if over the cut size), **water 3** (`m037_water`, `m037_water_fall`,
  `m037_water_foam`), glow 0.
- **Collision:** the hero **`collision="precise"`** (PreciseConvexDecomposition), so the pool and the channel stay
  walkable and the hull doesn't box the tile in; `CliffFallsWall`, `CliffFallsTop` and the rock parts `hull`; the
  water parts `none`.
- **Waterline:** pool 1.0, channel 17.4. **Flow:** +Y → −Y (from the back seam to the lip, then from the foot to the
  front edge).
- **Stage 5 (lighting): skip, and record why.** Nothing glows; no emission, no PointLight. The beams' own
  `light_emission` (0.25–0.35) is enough.
- **Studio notes (Requires Manual Validation):**
  - the curtain's cyan and stripes through its texture, `kit_transparency` 0.2 and the beams;
  - that the asset-wide `flow` (−Y) doesn't make the curtain's texture crawl sideways (if it does, set the curtain
    piece's flow to none in Studio);
  - the mist's density at the foot;
  - the pool's and the foam's opacity;
  - that the 0.8-deep pool and the 0.3 channel are wadeable for the default character;
  - the lawn lime and the rock's warm / cool read under the game's sun.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`, `heat_glow`,
  `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`, `harvest_hit`,
  `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **`waterfall_curtain`** (beam kind: "socket on the top lip, end where the fall meets the pool"; beams Fall + Sheen,
  emitter Spray; needs `end=`, takes `width=`): **2 sockets** at (−1.8, −1.1, 17.3) → end (−2.0, −2.6, 1.2) and (+1.8,
  −1.1, 17.3) → end (+2.0, −2.6, 1.2), `width` 4.0 each (together the 7.2 → 8.4 curtain). On the hero and on
  `CliffFallsCurtain`.
- **`waterfall_mist`** ("where the fall hits the pool"; Mist + Splash emitters): **1 socket** at (0, −3.5, 1.4), scale
  1.2 (the spray band is about 15 wide). On the hero and on `CliffFallsSplashDisc`.
- **`water_foam`:** z 1.05, scale by size:
  - the curtain foot ribbon, 2 at (±3.0, −3.2) scale 1.0;
  - K1, K2 at 1.0; K3, K5, K6 at 0.6;
  - the pool's front edge, 2 at (−3, −14), (+5, −14) scale 0.7;
  - on the channel at z 17.45: the throat (0, 4.2) 0.6 and the lip pool (0, 0) 0.7.
  - **11 sockets** in all.
- **`water_flow`:** **the pool socket first** (the exporter reads the first): (0, −6, 1.03) → (0, −15.5, 1.03), width 12;
  then the channel (0.5, 15.5, 17.43) → (0, 1.0, 17.43), width 5 (`curve0` optional to follow the throat). **2
  sockets.** On `CliffFallsTopWater` the channel one; on `CliffFallsPool` the pool one.
- Check the export STATS line reports **16 sockets** on the hero (2 curtain + 1 mist + 11 foam + 2 flow).
- **Not recommended:** `vapour` (the sheet draws spray, not a haze; W03 added one, and the mist covers the spray),
  `dust`, any light.

## 8. Naming and decisions for the main session

**Names owned elsewhere** (repo text and every sheet / kit / checkpoint / wip `.blend`, zstd-decompressed, with
`blendall.py` → `blendall_out.txt`):
- **W03** (`W03.blend`, `wip/W03_waterfall_module.blend`, `FlintbornWorldKit.blend`, the checkpoint and every M0xx wip
  blend; manifest): **`WaterfallModule`** (the sheet's own title, 83 hits in the kit file), `WaterfallTopWaterPlane`,
  `WaterfallCliffTop`, `WaterfallCliffWallA/B/C`, `WaterfallNarrow`, `WaterfallWide`, `WaterfallTwoStep`; socket and
  string names `WaterfallCurtain`, `WaterfallSplash`, `WaterfallSplashPool`, `WaterfallFoamRibbon` / `WaterfallFoam`,
  `WaterfallVapour`, `WaterfallFlow`, `WaterfallDrop`; keys `w03_*`.
- **07 terrain kit:** `WaterfallCliff`; keys `water`, `water_deep`, `water_shallow`, `foam`.
- **Free:** `CliffFalls`, `WaterfallTile`, `WaterfallBasin`, `CliffWaterfall`, `FallsModule` and `m037` occur nowhere
  in the repo text or any `.blend`. `M.mk` would silently rename a clash to `<name>M037` (it would produce
  `WaterfallModuleM037`).

| Object | Part | Why |
| --- | --- | --- |
| `CliffFalls` | hero | the sheet's title `WaterfallModule` is W03's; a distinct prefix avoids W03's `Waterfall…` part and socket strings |
| `CliffFallsTopWater` | Top Water Plane | `WaterfallTopWaterPlane` is W03's |
| `CliffFallsTop` | Cliff Top (Grass & Foliage) | `WaterfallCliffTop` is W03's |
| `CliffFallsWall` | Cliff Wall Pieces | `WaterfallCliffWall…` is W03's |
| `CliffFallsCurtain` | Waterfall Mesh (Curtain) | `WaterfallCurtain` is a W03 socket name |
| `CliffFallsFoamRibbon` | Foam Ribbon | `WaterfallFoamRibbon` is W03's |
| `CliffFallsSplashDisc` | Splash Disc | `WaterfallSplash…` is W03's |
| `CliffFallsPool` | Water Plane (+ Foam) | |
| `CliffFallsRockLarge` / `…RockMedium` / `…RockSmall` | Rock Pieces | |

- Palette keys `m037_*` (§5.4). Collection `Kit/M037 Waterfall Module`. Socket names follow `K.socket`
  (`VFX_CliffFalls_waterfall_curtain_N`, `…_waterfall_mist_N`, `…_water_foam_N`, `…_water_flow_N`).

**Decisions needed (a recommendation each):**
1. **Size and levels:** **tile 32 × 32, grass top 18.0, max z 25 ± 1; pool water 1.0 over bed 0.2; channel water 17.4
   over bed 17.1** (recommended: the front and top cells give a cliff of 16.6–17.4, and 18.0 makes the back seam M034's
   seam raised by 16.4). The alternative is W03's levels (grass 20.5, channel 20.0), about 15 % taller than the sheet.
2. **Plan source:** **the front cell and the top view govern** (a full-width pool 15 deep, the cliff face at Y −1, the
   channel 14 → 4 → 8.5, the low boxes at the front corners) (recommended: the only consistent pair). The alternative,
   the hero's hexagonal pool with cut front corners, contradicts the top, front and "rear" cells.
3. **Cameras for verification:**
   - **`front_sheet (0, 10)`** against the front **and** the "rear" cells;
   - **`f34_sheet (30, 26)`** and **`r34_sheet (−25, 24)`** (the "rear three-quarter" is a front-left view);
   - **`side_sheet (270, 12)`** (the "side (right)" shows the pool on its right);
   - **`top_sheet (0, 50)`** and the kit top;
   - all with the floor hidden and `vfx=True`;
   - kit front34 / rear34 / front / side / rear / underside as self-consistency;
   - extras `junc_cu (−20, 20)`, `lip_cu (15, −20)`, `pool_cu (−35, 25)` and a parts shot (35, 28).
   (Recommended, §3.)
4. **Tiling:** **record the §6 contract: the back seam is M034's raised by 16.4; the front edge is open water across the
   width, as drawn** (recommended: it follows the sheet, and it joins open water at the kit's waterline). The
   alternative is M034's front seam (banks at |X| 7 … 16, 1.6 tall, a 14-wide outlet). That chains straight into a
   streambed but adds sand banks the sheet doesn't have. It could be a later `…Outlet` variant.
5. **Back of the tile:** **a flat rock joining face at Y = +16** (recommended: no view draws the back; WorldModeling
   §12.2 asks for a flat connector region). The alternative is a column-faced back, which adds about 300 tris for a face
   that abuts the upper terrain.
6. **Water, foam and curtain:** **meshes and sockets** (recommended: the sheet draws them all as separate meshes, and
   W03's VFX-only version was flagged "thin curtain, little foam / splash"). The meshes are:
   - a three-lobe curtain mesh on `m037_water_fall` (`kit_transparency` 0.2);
   - pool and channel shells on `m037_water` (0.3);
   - the foam ribbon, splash disc with spikes, rings and patches on `m037_water_foam` (0.1).

   The sockets are 2 `waterfall_curtain`, 1 `waterfall_mist`, 11 `water_foam` and 2 `water_flow`.

   The alternative is W03's VFX-only falling water and foam. The curtain would then exist only as beams, and the
   still renders would lose about 15–20 % of their W / F share.
7. **Budget:** **4000 for the hero, planned at about 3700–3950** (recommended: STAGES). The alternative is to allow
   6000 for this terrain hero (W03 carried 8000) and keep more bushes and flowers. Ask before cutting columns.
8. **Stage 5:** **no emission or lights** (recommended: nothing glows).
9. **Hero packaging:** **one object** (recommended: the same water exception as M032 / M034; the exporter splits water
   by key). It holds:
   - one closed land shell (core, columns, boxes, beds, grass slabs and rocks unioned);
   - separate closed vegetation shells;
   - closed pool / channel, curtain and foam shells;
   - `collision="precise"`.
10. **Parts:** **ten:** TopWater, Top, Wall, Curtain, FoamRibbon, SplashDisc, Pool, and RockLarge / Medium / Small
    (recommended: the sheet's exploded list, with rocks as reusable sizes as M034 did). The alternative is eight, with
    one `CliffFallsRocks` cluster part.
11. **Names:** **`CliffFalls*`, keys `m037_*`** (recommended: the sheet's `WaterfallModule` is W03's). The alternative is
    `WaterfallTile*`, also free.

## 9. Pitfalls to avoid (lessons from recent verifier failures written as targets)

1. **A rock pile instead of distinct columns** (021 round 1). The cliff must read as **separate fat prisms under one
   grass cap**. Targets:
   - in `front_sheet`, 7 front columns (C1–C6 + F_L) and the 2 stepped columns are distinct at §2.3 (±0.04 f), with dark
     full-height creases between them;
   - each column's flat top covers ≥ 60 % of its plan area within 10° of horizontal;
   - no boulder heaps against the face: the foot carries only K3–K6, the two low boxes and the stepped columns;
   - the cliff is 0.88–0.96 of the width at h .1–.7 in the front view.
2. **Small or lumpy facets** (023 round 1). "Broad, flat-shaded faces":
   - every visible column side ≥ 1.5 studs wide and ≥ 4 tall, split into at most 2–3 triangles;
   - big boulders K1 / K2: median facet area ≥ 1.2 sq studs, no facet under 0.15 sq studs except base slivers, a flat
     crown (normal z > 0.9 on ≥ 20 % of the plan area), height 0.85–1.0 × width;
   - no `K.hull_rock` defaults, no ico-spheres, no vertex noise, no subdivision.
3. **Paint taken from shadowed areas.** Every §5.4 target is an unshadowed median: the exploded lawn, the lit rock
   faces (v > .7), the open water, the exploded curtain. Don't calibrate rock to the swatch, the whole-rock median alone
   or the shade quartile; don't calibrate the grass to the view medians (they include shaded lawn). Check the hue order
   in §5.3 on the final renders.
4. **Measuring wrong.**
   - Measure floor-hidden, `vfx=True` renders with `measure_render.py`, and treat any floor or floor shadow as
     background.
   - Check W : H, shares, the top profile and **width per height in every compared view, including the "rear" cell
     (through `front_sheet`), `side_sheet` and `r34_sheet`**, not only the hero.
   - The "rear" cell's shares (R 42.6 / W 17.1 / F 13.1) and its width per height (0.90–0.96 at h .1–.7) are targets
     like the front's.
5. **Comparing with the wrong camera** (§3).
   - The hero is az +30 from the front-right; the "rear three-quarter" is az −25 from the front-left; the "rear" cell
     is a front view.
   - The "side (right)" is az 270; the "top" is e 50. The kit rear34 / rear / side cameras match none of the sheet's
     cells.
6. **A thin, flat or grey curtain** (W03's verdict).
   - The curtain is a 7–8.5-wide mesh with three lobes and a rolled lip, 0.21 of the front view's width.
   - Its render median is within 15 of `#11D3FD`, with light crests present.
   - The notch wall behind it is bed-dark, so the see-through curtain stays saturated.
7. **Too little foam and spray.** F is 12–14 % of every front / three-quarter view: the splash disc, ribbon, spikes,
   rings and patches must be modelled (and the mist and curtain previews rendered), not left to sockets alone.
8. **Foam baked into rocks or the land.** Foam is its own shell on `m037_water_foam` (1.03–1.08), never on rock or
   grass faces. The export STATS shows 3 water pieces.
9. **Water that collides, z-fights or carries detail.**
   - The pool and the channel are flat plates, with no ripples and no stripes in the mesh.
   - No water face coincides with a bed or a tile edge.
   - The bed key doesn't contain "water"; the three water keys do.
10. **Colour by facing.** Rock warm / cool and lawn light / dark come from the light; paint only by position fields
    (§5.5); `K.check` facing correlation < 0.5.
11. **Breaking the tile.**
    - No rock or plant across an edge.
    - The channel at the back seam must be X −7 … +7 with water 17.4, bed 17.1 and grass 18.0.
    - The pool edge faces and the channel's back face are inset 0.02.
    - Any change to the levels must update §6.
12. **Hull collision on the hero** (§7.1): the tile would become a solid 25-stud box with no pool.
13. **Exact booleans.**
    - Union the core and columns first (largest first, object at the origin), then the slabs and rocks one at a time.
    - Keep water, curtain, foam and vegetation out of the union.
    - Save between risky steps, and run `M.fix_bowties` after the unions (leaf hubs and fern fans had bowties in
      019–021).
14. **Naming clashes** (§8). Don't reuse any `Waterfall…` name W03 owns. Only one agent drives a Blender session at a
    time; stage agents make no commits, pushes or exports.

## Decisions (main session, 2026-10-29)

All recommendations are accepted, with the budget rule stated:
1. Size and levels:
   - a 32 × 32 tile, grass top at 18.0, overall height 25 ± 1 at the pine tips;
   - pool water at 1.0 over a bed at 0.2;
   - channel water at 17.4 over a bed at 17.1, 14 wide at the back edge.
2. Plan: the front cell and the top view govern; the hero's hexagonal pool edge is a known miss.
3. Comparison cameras:
   - the r34 cell at (−25, 24);
   - the "rear" cell against `front_sheet (0, 10)`;
   - the side at (270, 12), with a wider W:H tolerance;
   - the top at (0, 50);
   - the hero at (30, 26).
4. Tiling: the back seam is M034's raised by 16.4. The front edge is open water across the full width.
5. Back of the tile: a flat rock joining face at the back edge.
6. Water: meshes plus sockets.
   - Three water keys: `m037_water_fall` (curtain), `m037_water` (pool and channel) and `m037_water_foam`, giving 3 see-through pieces.
   - The bed key `m037_bed` must not contain "water".
   - 16 sockets: 2 `waterfall_curtain`, 1 `waterfall_mist`, 11 `water_foam` and 2 `water_flow`, with the pool's first.
7. **Budget: 4000 hard.** If it runs over, cut ferns, flowers and small rocks first, never the columns, curtain or boulders. Record what was cut.
8. No lighting.
9. Packaging: one hero object with closed land, vegetation, water, curtain and foam shells (the M032 / M034 water exception), collision "precise". Every shell is manifold with 0 bowties.
10. Ten parts.
11. Names: `CliffFalls*` (hero `CliffFalls`), keys `m037_*`.

The cliff is 7 front columns plus 2 stepped columns, with big flat faces (each visible face at least 1.5 × 4 studs, flat tops on at least 60 % of the area), not a rock pile.

## Stage 1 — Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m037.py` → `build()` (hero `CliffFalls` + ten parts, renders, report). Background session
port 9881 on `wip/M037.blend`; final check in a freshly restarted session reproduced every number below.

- **Cliff solid without booleans** (`cliff_solid`). The cap's three flat tops (left grass 18.0, channel bed 17.1, right
  grass 18.0; vertical bank walls between them along §2.2's banks) over the cap outline A (front Y −1.0, sides X ±15.65,
  back Y 16). The cap's underside at 16.9 turns in to a core outline B (front Y 0.2, sides ±14.6) that drops to the
  ground. A's back edge between X ±14.6 lies on B, so the back joining face is one flat wall from the ground to 18.0
  (rock below 17.4, the lime edge above, the channel slab's seam 16.9 → 17.1 bed-coloured). Back seam = M034's seam
  raised 16.4: channel X −7 … +7, bed 17.1, water 17.4, grass 18.0.
- **Columns** (`column`, m032's superellipse recipe): C1–C6 + the narrow flank FL in the front row, the stepped SL / SR in
  front (tops 12.0 / 11.5), three side columns per side (6 sides). 8-sided front columns with foot / mid / shoulder rings
  (the mid ring twisted ±0.16 rad, jittered 6 %, z ±1.1, so each big side facet breaks once) and a chamfered flat top.
  **The front row's bevelled shoulders stand 0.3 in front of the cap's edge** (`SHOULDER_OUT`), and the side columns'
  0.3 outside its sides, so the column tops show under the grass lip as on close-up 1 and no thin underside strip is
  left between the cap and the columns. Column tops 17.85 sit inside the cap. Side / corner columns have no foot flare
  and are clamped to |X| ≤ 15.97.
- **Low boxes** B1 (top 2.4, pine), B1b (4.0, bush) and B2 (2.6, pine): soil sides under a 0.42 grass band. They stand
  0.6 inside the tile edge, so the bed top beside them has no sliver.
- **Bed slab** 0 → 0.2 under the whole front, its back 0.45 into the core. **Rocks** (`rock`, m034's hull recipe with flat
  crowns): K1 / K2 (big, in the pool), K3–K6 at the foot, and the channel rocks T1, T2, T4–T7 standing on the channel
  bed through the water.
- **Water and foam, separate closed shells that touch nothing.**
  - Pool plate 0.26 → 1.0 over the full width, back edge Y −1.62 (just in front of the column feet). The channel plate
    17.16 → 17.4, 0.25 off the bank walls, 0.02 inside the back seam, 0.05 past the lip.
  - Both plates are cut by 2D holes. The holes are first taken from each land piece's section, then **re-measured on the
    finished land** (`refine_holes`).
  - Curtain (`curtain`): three U-lobes over 10 points, six rings from the lip (17.45, rolled forward 0.25 under the
    lip) to the pool (1.12), 7.1 → 8.3 wide, leaning out 1.3, 0.47 thick at the valleys; 164 tris.
  - Foam 1.03 → 1.08: the scalloped splash disc 16 × 8 with two round holes, rings round K1 / K2 (0.85 wide), four pool
    blobs, two channel blobs (17.43 → 17.48), the **splash veil** (a thin white spray wall in front of the foot whose top
    is a row of splash peaks up to 6.8) and 8 splash spikes.
- **Vegetation** (separate closed shells, `_Guard` keeps them off the land, the water and each other):
  - 6 pines, 3 tiers each: PL1 / PL2 / PR1 / PR2 on top, PF1 / PF2 on B1 / B2, 7.0 / 6.6 tall (the front cell's corner
    pines reach h .45).
  - 4 dark fern bushes; lime bushes: low wide caps on SL / SR, one on B1b, one on B2, and two hanging off the C2 / C4
    faces.
  - 2 white daisies, 2 pink, 3 yellow flowers.
  - **STAGES "no floating dressing":**
    - every leaf, flower, tier and trunk sits 0.015 (`VEG_GAP`) off its support;
    - pines are built top-down by ray casts: each tier's flat cap stops 0.015 under the tier above, and the trunk top
      stops 0.015 under the lowest tier;
    - face-bush leaves are based on a ray hit on the rock face;
    - leaves have a blunt 5-point outline with a low convex ridge (rounded, not pointed).
    - `floating(o)` counts **0 loose / 0 unchained of 77 vegetation shells** on the hero, and 0 / 0 of 24 on the cliff-top
      part.
- **Parts:**
  - `CliffFallsTopWater`: the channel plate.
  - `CliffFallsTop`: the left cap on C1–C3 and LW1–3 cut at 14.6, with PL1 / PL2, ferns and flowers.
  - `CliffFallsWall`: C1–C3 in a row, SL in front and K3.
  - `CliffFallsCurtain`.
  - `CliffFallsFoamRibbon`: the ring, outer 10.3 × 3.8.
  - `CliffFallsSplashDisc`: the disc, the veil and the spikes.
  - `CliffFallsPool`: the bed, the plate, K1 / K2 and their rings.
  - `CliffFallsRockLarge` / `RockMedium` / `RockSmall`: the K1, K3 and T6 shapes at the origin.

**Budget cuts (decision 7, flowers / ferns / small rocks first):**
- the T3 lawn rock and the P1 / P2 pebbles (P3 dresses the cliff-top part only);
- ferns 8 → 4;
- daisies 8–10 → 2 (+ 2 pink), yellow flowers 6–8 → 3;
- four-sided pine trunks; three tiers on every pine;
- no rings on K5 / K6; the ribbon is left out of the hero's foam union, because it lies wholly inside the splash disc
  (the part keeps it).

Columns, curtain and boulders are untouched.

## Stage 2 — Optimisation and cleanup

- **Land:** 35 exact merge-0 unions at the world origin, one shell at a time, with no coplanar inputs, then:
  - a floor cut at z 0;
  - `m016._clean_mesh` with the level planes locked (0, 0.2, 16.9, 17.1, 18.0, box and stepped tops);
  - finish, then polish (m012 needle force, m032's fold-guarded `_polish` and `_safe_force` to 2.5);
  - `fix_bowties`.
  - Self-hits after the union, after the cleanup and on the finished land: 0 / 0 / 0. There were 4 when the column tops
    were at 17.6–17.65; raising them to 17.85 fixed that. m026's guarded clean was tried and rejected: it slanted the
    bank walls into the channel.
- **Hero `CliffFalls`:**

  | Measure | Value |
  | --- | --- |
  | Tris | **3920** (limit 4000) |
  | Size | **32.00 × 32.00 × 25.22** |
  | Shells | 98: 1 land (2022 tris), 77 veg (986), 2 water (320), 1 curtain (164), 17 foam (428), every one closed |
  | Non-manifold edges / verts | 0 / 0 |
  | Boundary, wire, loose, zero-area, n-gons, duplicate verts | 0 |
  | Normals | outward |
  | Self-intersecting face pairs | **0** |
  | Faces under 5° | 3 rock union-seam slivers (min 1.1°) at the column creases behind SL / SR and on the RW1 / RW2 crease; the fold guard refuses to collapse them |
  | Inverted (ray parity) | 2 tiny land faces at a cap-underside corner |
  | Origin | bottom centre; transforms applied |

- **Parts:**
  - TopWater 120, Top 884, Wall 328, Curtain 164, Ribbon 84, Disc 220, Pool 546, RockLarge 46, RockMedium 38,
    RockSmall 22 (all under 1000).
  - Every one is closed, manifold, with 0 self-hits.
  - The Wall has 1 face under 5° (the same SL / C2 crease).
- **Holes against land:** water and foam keep ≥ 0.09 off every land piece (0.25 off the bank walls), and the foam
  0.03 over the water.

## Stage 3 — UV

`M.smart_uv` (ANGLE_BASED, angle 45, margin 0.008) + `m012._uv_unfold`. Results:
- hero 973 islands, 0 overlaps, 0 flipped, min gap 0.016, border 0.008, density 1.0 / 1.0 / 1.0, conformal p95 1.005;
- every part is the same: 0 overlaps, 0 flipped.

## Stage 4 — Materials, colour, texture

- **Calibrated** with `K.calibrate`; the rendered dome medians against the targets are:

  | Key | Rendered | Target |
  | --- | --- | --- |
  | grass | (170,206,5) | #ABCE04 |
  | leaf_lime | (124,180,5) | #7DB401 |
  | leaf | (17,87,9) | #125A04 |
  | pine | (9,97,31) | #056324 |
  | bark | (113,69,39) | #6C4926 |
  | petal | (254,254,241) | #F4F4EE |
  | pink | (234,124,175) | #EB7CAF |
  | pollen | (246,216,37) | #F6D81A |
  | soil | (143,101,51) | #906532 |
  | dirt | (213,169,117) | #D6AA76 |
  | rock | (175,160,163) | #B1A2A4 |

  Rock was then re-tuned on the hero renders to the **lit-face** target, giving `#ADA5AA`.
- **`palette()`:**

  | Key | Hex | Key | Hex | Key | Hex |
  | --- | --- | --- | --- | --- | --- |
  | grass | #8AAA00 | leaf_lime | #689600 | leaf | #0E4E06 |
  | pine | #04561F | bark | #5A3412 | petal | #C3C9C8 |
  | pink | #B96696 | pollen | #C2B001 | soil | #735326 |
  | dirt | #A88B66 | rock | #ADA5AA | bed | #0B6E8F |
  | bed_light | #3AC4EA | water | #00C2F2 (transparency 0.3) | water_fall | #10C0F2 (0.2) |
  | water_foam | #E6FCFE (0.1) | | | | |

  The bed key has no "water" in its name; the three water keys do. Water specular is 0 in the preview.
- **Blending (by position only):**
  - Lawn: broad noise patches up to a 50 % grass × lime mix, in 12 / 25 / 38 / 50 % steps.
  - Within 1.0 of the channel banks: 25 % dirt.
  - Two dirt patches with a 50 % ring round them.
  - Channel and pool beds: deep teal with broad light patches (25 / 50 / 75 %), and 25 % rock round the boulders' feet.
  - Cap outer walls: lime above 17.4, rock below (a hard edge between two materials).
  - Bank walls: grass above the water, bed colour under it.
  - The core wall behind the curtain is bed-dark, blending to rock over |x| 3.6 → 5.2.
  - Boulders are bed-coloured below their waterline (hard: submerged).
  - Box sides are soil under a grass band.
  - The floor is rock.
- **Tint:** grass 0.04 at scale 0.5, rock 0.04 per column (×0.95–1.05 per piece), bed 0.03 at scale 0.8. Water, curtain
  and foam have none (the exporter textures water).
- **Finish:** roughness per §5.4, metal 0, no emission. Every object carries `kit_shading_ok` (the sheet's own material
  regions, painted by position).
- **Final renders against the sheet** (study masks, `measure_render.py`):

  | Measure | Ours | Sheet |
  | --- | --- | --- |
  | f34 rock lit faces | `#C7B8B5` | `#CCB8B5` |
  | front rock lit faces | `#CABBB8` | `#C7B6B7` |
  | Cliff-top part rock lit | `#C2B4B1` | exploded `#CBB6B1` |
  | f34 lawn | `#9CC80E` | `#9CC303` |
  | Cliff-top part lawn | `#A4CB0B` | exploded `#ABCE04` |
  | f34 whole rock | `#999294` | `#9892A0` (B −12: the sheet's shade faces are blue-violet, the studio's are warm grey) |
  | Pool deep tone (s ≥ .95) | `#0BD2FF` | `#04C9FA` |
  | f34 W median | `#2BD8FF` | `#08D5FD` |
  | Light share of the pool's W | 0.72 | 0.23 |
  | Curtain W median | `#30D3FF` | `#17CEFE` |
  | Curtain light share | 0.56 | 0.46 |

  - The pool's light share runs high because the kit water preview texture lays light lines over the plate; darker
    water or bed keys only darkened both tones and left the share unchanged, so the keys were kept.
  - Foam renders `#FFFFFF`, shade `#BBF7FF`.

## Stage 5 — Lighting

Skipped (decision 8): nothing glows; no emissive key, no light. Studio notes are as in §7.1.

## Stage 6 — VFX

There are 16 sockets on the hero; the pool's `water_flow` is created first.
- `water_flow`: pool (0, −6, 1.03) → (0, −15.5), width 12; channel (0.5, 15.5, 17.43) → (0, 1.0), width 5.
- `waterfall_curtain` ×2: (±1.8, −1.15, 17.3) → (±2.0, −2.7, 1.2), width 4.
- `waterfall_mist`: (0, −3.6, 1.4), scale 1.2.
- `water_foam` ×11:
  - the ribbon at (±3, −3.2);
  - K1 and K2 at scale 1.0;
  - K3 (−6.0, −4.9), K5 and K6 (−12.3, −8.7) at 0.6;
  - the pool front (−3, −14) and (5, −14) at 0.7;
  - on the channel: the throat (0, 4.2, 17.45) and the lip (0, 0, 17.45).

The parts carry their own: TopWater the channel flow, Curtain the 2 curtain beams, SplashDisc the mist, Pool the pool
flow. Renders are made with `vfx=True`.

## Modeller's notes for the verifier

- **Cameras** (decision 3): f34_sheet (30, 26), r34_sheet (−25, 24), front_sheet (0, 10), also for the "rear" cell,
  side_sheet (270, 12), top_sheet (0, 50). The `*_sheet` shots use a 3× lens and hide the floor. Measure them with
  `m037_study/measure_render.py`; `m037_study/region.py` gives class medians inside a box (the curtain, the pool band).
  - The sheet's f34 rim rises to the right and its left end shows the cliff's left side with the low box. That reads like
    a front-left camera, and our r34_sheet (−25) resembles it closely. The decision camera (30, 26) gives the mirror
    layout.
  - The top-profile ends differ at (30, 26): ours .24 / .77 against the sheet's .27 / .24, because the sheet draws a
    hexagonal pool that sticks out past the cliff's back corners (known miss, §3.1).
- **Shares (ours against the sheet):**

  | View | G | R | W | F |
  | --- | --- | --- | --- | --- |
  | front | 14.7 / 17.0 | 51.4 / 40.0 | 22.9 / 19.9 | 9.1 / 13.1 |
  | f34 | 20.6 / 19.6 | 45.9 / 36.1 | 21.7 / 21.4 | 9.1 / 12.2 |
  | r34 | 20.0 / 19.6 | 45.6 / 42.9 | 22.2 / 16.1 | 9.5 / 11.1 |
  | top | 29.2 / 22.5 | 29.1 / 21.6 | 26.3 / 32.0 | 11.4 / 14.4 |
  | side | 18.0 / 17.5 | 68.2 / 57.6 | 6.8 / 6.8 | 3.3 / 9.4 |

  - The sheet's O (dark outlines) is 7–8.6 %; ours is 1–3 %. Most of the sheet's outline pixels sit on rock, so R + O is
    closer than R alone (front 52.9 against 48.5).
  - R is still high and F low. The sheet's curtain has white streak highlights (its F share is 25 % inside the curtain,
    ours 0.2 %) and denser pool foam. A curtain highlight would need another water key (a 4th water piece) or more foam
    tris; the hero is at 3920 of 4000.
- **Front view geometry:**
  - W : H 1.178 (sheet 1.142).
  - Top profile mean error about 0.07. The far right falls to .39 on the sheet because its cliff ends near X 14.4; ours
    stands at the tile edge per §6.
  - The cliff is 0.91–0.92 of the width at h .1–.7.
  - The curtain spans f ≈ .38–.62.
- **Side:** W : H 1.165 (sheet 0.933, squeezed depth: wider tolerance per decision 3). The low boxes sit at the
  front-left, not at the screen-left back as the sheet's side cell draws them (known miss, §3.4).
- **Deviations from the spec:**
  - The cap's grass edge stops 0.35 inside the side tile edges (X ±15.65), so the side columns' bevelled tops can show
    under it as at the front.
  - Low boxes stand 0.6 inside the tile edge.
  - The pool plate's back edge is at Y −1.62, so a thin strip of bed shows at the column feet.
  - The channel plate is 0.25 off the bank walls.
  - The corner pines are 7.0 / 6.6 tall, against the spec's 5.0 / 4.8, to reach the front cell's h .45.
  - K3 is at (−6.0, −4.9) and K6 at (−12.3, −8.7).
- **Known leftovers:**
  - 3 + 1 rock union-seam slivers under 5°.
  - 2 tiny inverted-parity land faces.
  - 6 leaves dropped by the guard, which tried shorter and steeper leaves first.
  - The exploded shot is small in its cell.
  - The rock reads warm-pink-grey: the sheet's blue-violet shade faces come from its lighting, and colouring by facing
    is not allowed.

## Verification round 1 (verifier, 2026-10-29)

A fresh verifier, read-only. It used port 9881 on `wip/M037_verify.blend`: no build, no save, and no edits to any
`.py`. Renders went to the scratchpad (`…/scratchpad/m037_verify/r/M037/`) through `m037.render_views` with
`M.MODEL_RENDERS` redirected. They were measured with `m037_study/measure_render.py` and `region.py`, plus my own scripts.
These were:
- `v3.py`: per-shell self-intersection, water/land distance, and a floating/chain check over **all** shells, including
  water and foam;
- `v4.py`: where the slivers and inverted faces are;
- `v6.py`: boulder proportions;
- `v7.py`: levels, seam, sockets and collision;
- `hue.py`: hue per region.

### Measured

| Object | Tris (limit) | Size (studs) | Shells | Non-man e / v | Bound / wire / loose / zero-area / n-gon / dup | Self-x (within a shell) | Normals | < 5° faces | Inverted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CliffFalls | **3920** (4000) | 32.00 × 32.00 × 25.22 | 98: land 1 (2022), veg 77 (986), water 2 (320), curtain 1 (164), foam 17 (428) | 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 | 0 | outward | 3 (min 1.09°) | 2 |
| CliffFallsTopWater | 120 | 13.33 × 17.03 × 0.24 | 1 | 0 / 0 | all 0 | 0 | outward | 0 | 0 |
| CliffFallsTop | 884 | 13.77 × 17.53 × 10.62 | 25 (1 land + 24 veg) | 0 / 0 | all 0 | 0 | outward | 0 | 0 |
| CliffFallsWall | 328 | 11.55 × 9.23 × 17.85 | 1 | 0 / 0 | all 0 | 0 | outward | 1 (3.5°) | 0 |
| CliffFallsCurtain | 164 | 8.30 × 2.25 × 16.33 | 1 | 0 / 0 | all 0 | 0 | outward | 0 | 0 |
| CliffFallsFoamRibbon | 84 | 10.28 × 3.80 × 0.05 | 1 | 0 / 0 | all 0 | 0 | outward | 0 | 0 |
| CliffFallsSplashDisc | 220 | 16.09 × 7.91 × 5.76 | 10 | 0 / 0 | all 0 | 0 | outward | 0 | 0 |
| CliffFallsPool | 546 | 32.00 × 16.45 × 4.90 | 4 (bed + rocks, water, 2 foam rings) | 0 / 0 | all 0 | 0 | outward | 0 | 0 |
| CliffFallsRockLarge / Medium / Small | 46 / 38 / 22 | 4.94 × 4.50 × 5.00 / 3.02 × 2.94 × 4.30 / 1.52 × 1.48 × 2.00 | 1 each | 0 / 0 | all 0 | 0 | outward | 0 | 0 |

- **Transforms and origin.** Every object has identity rotation and scale. In local space the hero's bbox is
  X −16 … 16, Y −16 … 16, z 0 … 25.215, so the origin is at the bottom centre. Every part's local bbox is centred,
  with min z 0.
- **Levels.** The flat-face areas sit at these heights:

  | Surface | z |
  | --- | --- |
  | Pool water | 1.000 |
  | Channel water | 17.400 |
  | Grass | 18.000 (the back seam's max is 18.000) |
  | Low-box tops | 2.4 / 2.6 |
  | Pool bed | 0.200 |
  | Channel bed | 17.100 |
  | Foam | 1.08 / 17.48 |

  - The pool water spans X ±15.98 and Y −15.98 … −1.62.
  - Channel water at the back seam spans X −6.48 … +6.75 (0.25 off the bank walls) and reaches Y 15.98.
- **Water against land.** Water, curtain and foam are separate closed shells.
  - The nearest land is 0.060 from the water (the pool bottom 0.26 over the bed at 0.2), 0.112 from the curtain and
    0.108 from the foam.
  - No water face overlaps a land face (BVH overlap 0).
  - The curtain's top is 0.07 from the channel water (17.45, rolled over the lip).
  - The water keys are exactly `m037_water`, `m037_water_fall` and `m037_water_foam`. `m037_bed` and its mixes contain no
    "water".
- **Floating** (my own check, every shell, contact 0.03):
  - Vegetation: 0 loose and 0 unchained of 77 on the hero, and 0 / 0 of 24 on the Top part.
  - Pool foam chains to the pool water. The 2 channel foam blobs sit exactly 0.030 over the channel water (17.43
    against 17.40), which is right at the contact limit.
  - The water plates and the curtain touch nothing, by design.
  - So no leaf, petal, flower, pebble or moss shell floats.
- **Facing.** `kit_baked_shading` is **0.00**, so no colour follows face direction. `kit_tint_spread` is 1.19. `K.check`
  reports nothing.
- **Sockets: 16.** There are 2 `water_flow` (`_1` is the pool's, (0, −6, 1.03), so it comes first), 2 `waterfall_curtain`
  (±1.8, −1.15, 17.3), 1 `waterfall_mist` (0, −3.6, 1.4) and 11 `water_foam` (the ribbon ×2, K1, K2, K3, K5, K6, the
  pool front ×2, the throat and the lip). Collision is `precise`.
  - They suit the sheet: a curtain from the lip to the pool, mist at the impact, foam at the ribbon, the boulders and the
    channel, and flow along the pool and the channel.

**Sheet comparison** (floor hidden, vfx on, study masks; the sheet's numbers are from the same script on `cell_*.png`):

| View | W:H ours / sheet | G | R | W | F | Top-profile mean error |
| --- | --- | --- | --- | --- | --- | --- |
| front_sheet vs front | 1.178 / 1.142 ✓ | 14.7 / 17.1 | **51.4 / 40.0** | 22.9 / 20.0 | **9.1 / 13.1** | ≈ 0.07 (both ends are the pool slab; f .95 is .74 against .39) |
| f34_sheet vs hero | 1.119 / 1.298 (the hexagonal pool, a decided known miss) | 20.6 / 19.6 | **45.9 / 36.1** | 21.7 / 21.4 | 9.1 / 12.2 | ≈ 0.16 (the right end .77 against .24, the decided known miss) |
| r34_sheet vs "rear 3/4" | 1.125 / 1.099 ✓ | 20.0 / 19.6 | 45.6 / 42.9 | 22.2 / 16.1 | 9.5 / 11.1 | |
| side_sheet vs side | 1.165 / 0.933 (squeezed depth, wider tolerance) | 17.9 / 17.5 | **68.2 / 57.6** | 6.9 / 6.8 | **3.3 / 9.4** | |
| top_sheet vs top | 0.884 / 0.903 ✓ | 29.2 / 22.5 | 29.1 / 21.6 | 26.3 / 32.0 | 11.4 / 14.4 | |

- The sheet's outline class O is 7.2–8.6 % and sits mostly on rock; ours is 1.1–2.9 %. Counting R + O, the front's
  rock excess is about +4 (52.9 against 48.4), and the rest of the gap is the missing foam.
- The front cliff is 0.91–0.92 of the width at h .1–.7 (target 0.88–0.96). The curtain spans f .38–.62 (target
  .40–.61).

| Colour (median) | Ours | Sheet | Verdict |
| --- | --- | --- | --- |
| Rock, lit faces (v > .7), f34 / front | `#C7B8B5` / `#CABBB8` (h 10°, s .09) | `#CCB8B5` / `#C7B6B7` | ✓ warm |
| Rock, shade (v < .5), f34 | `#696263` (h 351°, s .07) | `#5C5B6A` (h 244°, s .14) | lighting only (the sheet's blue-violet shade can't be painted) |
| Rock key `m037_rock` | `#ADA5AA` (b > g, h 322°, s .05) | | faintly mauve: see finding 6 |
| Lawn (G h 60–100), f34 / front | `#9EC912` / `#9CBE1D` | `#9CC303` / `#8EB406` | ✓ |
| Pines, f34 / front | `#074F18` / `#09601E` | `#046525` / `#056622` | ✓ (f34 a little dark) |
| Dark ferns, f34 | `#255C1A`, 550 px | `#125A04`, 4842 px | colour ✓; amount about 1/9 (budget cut) |
| Pool W, f34 / pool band | `#2BD8FF` / `#2DD7FC`, light share 0.72 | `#08D5FD` / `#09CFFC`, light share 0.23 | deep tone ✓ (`#0BD2FF` / `#04C9FA`); overall paler from the preview texture's light lines |
| Curtain, front box f .42–.58, h .35–.65 | W `#30D3FF`; F share 0.2 % | W `#1AD1FE`; F share 24.5 % | cyan ✓ (+22 R); **no white streaks** |
| Foam / spray | `#FFFFFF`, shade `#BBF7FF` | `#F7FDFE`, shade `#A6F2FD` | ✓ |
| Pool band F share (front, h 0–.08) | 13.8 % | 21.5 % | low |

### Findings

1. **minor: foam too sparse.** F is 9.1 against 13.1 in the front view, 9.1 against 12.2 in the f34 and 3.3 against
   9.4 in the side. The pool band is 13.8 % against 21.5 %. The sheet's pool is covered in scalloped white rings and blobs;
   ours has two angular hexagonal rings and four small blobs. Targets, budget-neutral (reshape existing foam, don't add
   shells):
   - grow the four pool blobs from r 1.0–1.4 to r 2.0–2.6, each with 6–8 scallops;
   - widen the K1 / K2 rings from 0.85 to 1.3–1.5 and make them 10–12-sided with scallops instead of hexagons;
   - extend the disc's back edge along the cliff foot as a scalloped strip about 1.2 deep.

   Goals: pool-band F ≥ 18 %, front F ≥ 11.5 % and f34 F ≥ 11 %.
2. **minor: the curtain has no white streaks.** Its F share is 0.2 % against the sheet's 24.5 %. This needs no new water
   key: add 3 thin closed crest streaks on the **existing** `m037_water_foam` key, 0.03–0.05 in front of each lobe crest
   from z 16.5 down to about 6. Allow ≤ 24 tris each (72 in all, inside the 80 left) and make them 0.5–0.8 wide. Goal: F
   ≥ 12 % inside the front curtain box (f .42–.58, h .35–.65). If tris are short, take them from the 8 splash spikes
   (8 → 5).
3. **minor: the rock share is high** (front +11, f34 +10, side +11). About 7 points of that is the sheet's outline class,
   and most of the rest closes with findings 1 and 2. No geometry cut is needed. Goal after 1 and 2: front R ≤ 47.
4. **minor: the columns look like smooth prisms.** The front and side columns read as clean, uniform, smooth octagonal
   basalt pillars ("organ pipes", clearest in the side and the kit side / rear34). The sheet's columns are chunkier, with
   visible triangular facet breaks and slightly different rim heights (front-cell rims at h .68–.72). Decision 9's target
   is met: 7 + 2 distinct columns, faces ≥ 1.5 × 4, flat stepped tops, not a rock pile. Optional, budget-neutral targets:
   - mid-ring twist ±0.16 → ±0.25 rad, so each visible side shows two distinct shades;
   - vary the shoulder tops of C1–C6 by ±0.3–0.5 (the cap still covers them).
5. **minor: the rock parts are egg-shaped.** H / W is 1.01 for `CliffFallsRockLarge`, **1.42 for `RockMedium`** and
   **1.31 for `RockSmall`**, and the medium and small ones taper to a point in the parts shot. The sheet's Rock Pieces
   are domed and flat-crowned, H about 0.75–0.9 × W. In the hero the visible boulders are fine: above the water, K1 / K2
   are 0.75 / 0.78 × W and the channel rocks 0.71–0.9. Targets (parts only):
   - build Medium and Small from T1 / T7 (or rescale them) to H / W 0.8–0.95;
   - crown ring 0.5 → 0.6 R, giving a flat crown ≥ 20 % of the plan (K1 / K2 now 0.17 / 0.18; Large 0.19, Medium 0.15,
     Small 0.10).
6. **minor: the rock key is faintly mauve.** `#ADA5AA` has b > g (h 322°, s .05). Under the studio's warm light the lit
   faces render warm (h 10°, matching the sheet), but in Studio's neutral light the key will lean faintly mauve-grey.
   Target: a key with g ≥ b at the same value, e.g. `#ADA6A4`. Re-check that the f34 lit-face median stays within 10 of
   `#CCB8B5` at h 5–20°.
7. **minor: thin vegetation on top.** The dark-fern pixels are about 1/9 of the sheet's, with 2 + 2 + 3 flowers. This
   follows decision 7's cut order and is recorded. If finding 2 frees no tris, leave it.
8. **minor: splash shape.** The 8 spikes plus the veil read as sharp ice-like shards. The sheet's spray is spiky but
   foamy. Optional: blunt the spike tips (apex 0.15 wide) and cap the tallest at 5.5. Merges with finding 2's tri swap.
9. **minor: mesh leftovers** (checked; none affect the render or import).
   - **Slivers.** 3 land faces under 5° (1.09°, 2.08°, 3.06°; areas 0.95–2.09 sq studs, 8–13 studs long) on column-crease
     union seams at (−15.66, −0.72, 14.25), (−8.46, −0.51, 3.39) and (15.38, 15.08, 12.89). The Wall part has 1 (3.5°).
     They are manifold, sit in the creases, and show no shading streak in any render.
   - **Inverted faces, hero.**
     - 0.044 sq studs at (−8.48, −0.52, 0.38): a ray-parity false positive (even parity from a second direction).
     - 0.061 sq studs at (15.14, 7.1, 16.9): a real tiny +Z fold in the RW1 / RW2 crease under the cap overhang. It is
       invisible and harmless.
10. **minor: seam.** The channel water at the back edge is X −6.48 … +6.75, 0.25 off the bank walls, against the
    contract's −7 … +7. A chained M034 will show a 0.25–0.5 strip of bed at the joint. Record it in §6, or bring the
    seam row of the plate to ±6.95 (the bank walls are vertical there).
11. **minor (known, decided):**
    - f34 W : H 1.119 and the right-end profile come from the sheet's hexagonal pool (decision 2).
    - The side's low boxes sit at the front-left (§3.4).
    - The rear is a flat joining wall (decision 5).
    - The exploded shot is small in its cell.

**Shape read.** The defining read holds in the front, f34, r34 and top views: a grassy, column-faced cliff split by a
channel, a three-lobe cyan curtain pouring from a notch, a white splash at the foot, and a flat full-width pool with two
chunky boulders in foam rings. Stepped bush-capped columns stand either side, and pine boxes sit at the front corners. The
close-ups match: a grass slab with a lime edge on flat column tops; the curtain tucked behind the flanks; the pool
slab's cyan side face. The pool is less foamy and the curtain plainer than the sheet's, but neither is a wrong
silhouette.

**Decisions.** I checked all 11 and found every one followed:

| # | Decision | Result |
| --- | --- | --- |
| 1 | Levels | 32 × 32 × 25.22; grass 18.0; pool 1.0 over 0.2; channel 17.4 over 17.1, bed opening 14 wide |
| 2 | Plan | front and top govern |
| 3 | Cameras | used |
| 4 | Tiling | back seam = M034's + 16.4; open-water front |
| 5 | Back | flat back wall |
| 6 | Water | 3 water keys; bed key without "water"; 16 sockets, pool flow first |
| 7 | Budget | 3920 ≤ 4000, cuts recorded, columns, curtain and boulders kept |
| 8 | Lighting | none |
| 9 | Packaging | one object; every shell closed with 0 bowties; collision precise |
| 10 | Parts | ten |
| 11 | Names | `CliffFalls*` / `m037_*` |

The cliff has 7 front columns + 2 stepped columns.

**Score: 7 / 10.** **Verdict: PASS.** There are no blockers:
- the mesh is clean and every shell is closed and manifold;
- it is under budget;
- nothing floats;
- the colour family is right (the rock's lit faces are warm) and no colour follows facing;
- every decision was followed.

Findings 1 and 2 (foam and curtain streaks) are the most visible gap to the sheet. They are worth a round 2 if the main
session wants the sheet's foamy look; otherwise commit with these notes.

## Main session ruling (2026-10-29)
Passed in round 1 (7/10) and committed.

**Main-session tweak (finding 6):** the rock key changed from `#ADA5AA` (B > G, faintly mauve) to `#ADA6A4` (G ≥ B). Rebuilt in the GUI kit; tris and shells are unchanged.

**Left for a later polish pass:**
- Foam is too sparse: front 9.1 % against the sheet's 13.1 %, pool band 13.8 % against 21.5 %. Targets: bigger scalloped pool blobs, 10–12-sided rings 1.3–1.5 wide, and a foam strip at the cliff foot.
- The curtain has no white streaks. Add 3 crest streaks on `m037_water_foam` (each ≤ 24 tris), taking tris from the splash spikes (8 → 5).
- Rock share is high (+10).
- The columns read as smooth octagonal pillars.
- The rock parts are egg-shaped (Medium H/W 1.42, Small 1.31).
- Splash spikes read as ice shards.
- Back-seam water sits at X −6.48…+6.75 against the −7…+7 contract. Record it, or widen to ±6.95.

**Export:** 11 assets, 16 pieces (7 solid, 9 water), 6372 tris, 21 VFX sockets, palette 27 colours, 0 problems.
