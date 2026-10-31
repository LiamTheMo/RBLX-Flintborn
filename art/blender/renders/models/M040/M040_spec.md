# 040 Cliff Wall — spec

Reference: `art/blender/assets/references/040.png` (1024 × 1536 px). The sheet's title is "01. CLIFF WALL" with the
subtitle "INDIVIDUAL ASSET PRODUCTION REFERENCE"; the top right reads "FLINTBORN ENVIRONMENT MODEL CATALOG / STYLIZED •
MODULAR • GAME-READY (BLENDER / ROBLOX)"; the footer reads "FLINTBORN — INDIVIDUAL MODEL STUDY" and "PAGE 41/132".
INDEX.md row 40 calls it "Flintborn Cliff Wall Construction Study".
Builder: `art/blender/kit/mcp/m040.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7).

Sheet text:
- **Cells:** "ASSEMBLED VIEW — FRONT THREE QUARTER", "ASSEMBLED VIEW — REAR THREE QUARTER", "ORTHOGRAPHIC VIEWS
  (CONSISTENT GEOMETRY)": "FRONT", "SIDE (RIGHT)", "REAR", "TOP (OVERHEAD)".
- **Exploded:** "EXPLODED CONSTRUCTION": "Grass Top Lip (Top Surface)", "Cliff Wall Body (Main Geometry)", "Flat Back
  Connector (Modular Join)". Dashed arrows drop the lip onto the body's top; three dashed arrows push the connector
  onto the body's **right-hand end**.
- **Parts breakdown (isolated):** "1. GRASS TOP LIP", "2. CLIFF WALL BODY", "3. FLAT BACK CONNECTOR".
- **Construction details:**
  - "TOP LIP UNDERSIDE": "Underside matches rock style (solid geometry)".
  - "TOP LIP TO BODY JUNCTION": "Simple flat joining surfaces".
  - "BACK CONNECTOR DETAIL": "Modular tabs for clean connections".
- **Material palette:** "Rock Light", "Rock Mid", "Rock Shadow", "Grass", "Foliage Dark", "Foliage Light", "Dirt / Earth".
- **Modeling notes** (paraphrased): a modular cliff chunk with clean connectors; broad flat-shaded faces and bold
  simple forms; keep the silhouette and proportions; simple solid geometry, no noise or micro detail; the grass top
  lip is a separate part for reuse and variation; the flat back connector lets the piece tile with other cliff
  modules; keep the rock face chunky and readable from a distance.
- **Game context:** a straight cliff-wall tile for building plateau edges (WorldModeling §12.2: "a terrain chunk with
  a flat rear/connector region, broad faceted front buttresses, a walkable top, and a separate grass lip"). The terrain
  kit uses a **32-stud grid**. The old kit sheet **W02 already has a Cliff Wall row** (`art/blender/kit/mcp/w02.py`,
  goals `art/blender/renders/kit/W02/cliff_wall_goals.md`, exported to `art/roblox/kit/W02/`): `CliffWall` (exported
  22.5 × 14.6 × 16.1, 5024 tris), `CliffWallBody`, `CliffWallGrassTop`, `CliffWallBackConnector` (1.0 × 11.8 × 18.2,
  a full-width plate on the back), `CliffWallStraight`, `CliffWallInnerCorner`, `CliffWallOuterCorner`. W02 is a
  different drawing (a 32 × 24 × 24 palisade with proud forward spikes and a back plate across the whole width). This
  sheet is a shallower 2 : 1 tile with an **end** plate (§3.2). Reuse W02's lessons, not its sizes or names (§8).

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Paper `#FEFCF6` (254, 252,
246), tolerance 10. Masks are `cls()` in `m.py` (HSV):
- **R, rock:** hue ≤ 45° or ≥ 190°, sat < 0.45, v ≥ 0.28, and not G/D/B/T. Lit faces warm peach (hue 20–25°), shaded
  faces cool blue-lavender (hue 220–300°); both are R (f34: 76 % warm, 24 % cool). Pebbles and lawn boulders are R.
- **G, green:** hue 45–150°, sat ≥ 0.28, v ≥ 0.12 (lawn, bushes, sprigs, drips). Split for colour work into lawn
  (hue < 80°, v ≥ 0.6) and bush (hue ≥ 80° or v < 0.6).
- **D, dirt:** hue 8–40°, sat ≥ 0.42, v ≥ 0.25 (bush trunks; < 1 % everywhere).
- **C, connector:** R or B pixels with sat < 0.10 inside the plate rectangles `CONN` (side (390,505,456,684), exploded
  (458,792,556,1048), parts (880,795,990,1056), close-up (829,1152,906,1329)). The plate's thin shaded edge falls in R.
- **B, ground shadow:** neutral or blue-tinted, sat < 0.07–0.12, v ≥ 0.82. **Background** in every silhouette and share.
  The ground shadows on this sheet are faint (< 1 % of a cell).
- **T, text and dark creases:** v < 0.30, sat < 0.30. In silhouettes, not in shares.
- **O, other:** outlines and anti-aliasing (1.5–3.3 % of the silhouettes).
- Cells (inner, below the labels): f34 (20,112,507,414); r34 (517,112,1004,414); front (20,478,289,686); side
  (290,478,500,686); rear (501,478,762,686); top (763,478,1004,686); exploded (20,724,596,1094); parts
  (597,724,1004,1094); close-ups underside (20,1152,356,1329), junction (358,1152,679,1329), connector
  (681,1152,906,1329). Swatches 66 × 68 px at x 34 / 107 / 180 / 254 / 327 / 401 / 474, y 1378–1446 (inner boxes in
  `m.SW`). The f34 bushes touch the header bar at y 112, so the f34 top may be clipped by 1–2 px.

**Scratch study material** (no Blender), in
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m040_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14, Pillow, numpy).
- **Helpers:** `m.py` (masks `cls()`/`cellcls()`, boxes `V`/`X`/`CONN`/`SW`, `label()`, `main_obj()`, `preview()`),
  `zoom.py`, `prev.py` (mask previews `cls_*.png`), `borders.py` (cell borders).
- **Measurements:** `measure.py` → `measure_out.txt`, `bb.json` (silhouettes, shares, top/bottom profiles, width per
  height, green per fifth, rock-top row); `lip.py` (face-top and lawn line per column); `crease.py` (column creases);
  `parts.py` → `parts.json` (exploded and parts boxes); `facets.py` → `facets_out.txt`, `facets.json`, `facets_*.png`.
- **Colour:** `samp.py` → `samp_out.txt` (per cell: rock median / lit / shade, warm and cool split, lawn, bush, C, D;
  body thirds; deciles); `bush.py` (per-bush and trunk samples); `sw.py`/`probe.py` (swatches and point probes).
- **Zooms:** `z_f34.png`, `z_r34.png`, `z_row2.png`, `z_front.png`, `z_side.png`, `z_top.png`, `z_expl.png`,
  `z_parts.png`, `z_cu.png`, `z_cu_conn.png`, `z_bushes.png`, `z_foot.png`, `z_pal.png`.
- **To run the scripts on our renders:** point `R` in `m.py` at the render, set `P` to its background, set the `V`/`X`
  boxes (and `CONN` for the side render) to the render cells, and re-run.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a modular terrain tile). Hero budget 4000 tris, each part under 1000. The plan in
  §4.3 lands at about 2400–3100.
- **Overall read (check this first).** A **long, straight cliff block about 1.6 times as wide as it is tall**, its front
  a **palisade of five tall flat-faced rock columns** separated by dark vertical creases, all reaching the same height,
  **capped by one flat lime lawn** that overhangs the column tops a little:
  - **the body:** five columns (each with a shaded left face and a lit front face), a flat back, and three **pointed
    shards** leaning against the lower face, plus a group of **flat-topped foot boulders** at the left;
  - **the grass top lip:** a flat lime lawn slab whose **rock rim** (blocky, same stone as the columns) sits on the
    column tops along a flat joint line; on the lawn, five round leafy **bushes** (two dark-green, three lime), two
    small boulders, pale pebbles and stepping patches;
  - **the flat back connector:** a grey plate with **three tabs on each long edge**, standing against the **right-hand
    end** of the wall, in its back half (side cell, exploded arrows, connector close-up);
  - **foot dressing:** a lime grass apron along the foot, two or three foot bushes, lime sprigs at both ends, pebbles.
  - Hero shares (f34): rock 75.5 %, green 24.2 % (lawn 67 % of it), dirt 0.3 %. Green by height fifths (bottom → top)
    16.1 / 13.6 / **0.0** / 28.7 / 41.7 %: **the middle of the face is bare rock**, the green is the lawn and its bushes
    on top and the apron and bushes at the foot.
- **Focal silhouettes, in order:**
  1. The flat lawn line and its bush bumps across the full width (top profile .84–.99 from f .10 to .90 in the f34;
     .84–.97 in the front cell).
  2. The column palisade: five vertical columns, all to the lip, with dark full-height creases between them.
  3. The pointed shards on the lower face (to about 0.5–0.55 of the screen height) and the stepped boulder group at the
     front-left foot.
  4. The grey end plate in the side view.
- **Target tile: 16.0 W × 8.0 D (body), turf top z 10.4.** Bounding box about 17.6 W (foliage overhang, §6) × 9.95 D
  (foot dressing in front, connector tabs behind) × 12.3 H (bush tops). Tolerances: W ±0.4, D ±0.5, H ±0.4; the seam
  pitch 16.0 and the turf 10.4 are exact. Decision §8.1.
  - **How it was derived.** The front cell is an elevated front view (§3.1). Its rock face spans 0.89 of the bbox width
    at mid-height (width per height .90 .89 .88 .87 at h .35–.75; the extra 0.97 at the foot is foot dressing at both
    ends), and the rock face meets the lawn at 0.745 of the bbox height (`lip.py`: .74–.78 across the face). So **face
    width / face height = 0.89 × 1.358 / 0.745 = 1.62**. The side cell is drawn at the front cell's scale (192 against
    190 px tall) and is 129 px deep: **depth / height 0.672**, of which the body is 106 px (7.4 studs at the scale
    below), the foot dressing 23 px (1.5) and the plate 52 px (3.6) of the body's back half.
  - **Why this size.** The terrain kit's 32-stud grid: a 16-stud tile is half a grid cell, so two tiles fill a cell
    and a 90° turn lands on the grid; 8 deep is a quarter cell. Turf at **10.4 = M032 Shoreline Corner's ridge grass
    level** (its tile contract, recorded for later cliff and shore sheets), so cliff walls and the shoreline corner
    meet at one plateau height. That gives face width / height 16 / 10.4 = 1.54 (sheet 1.62, −5 %). The lawn is 1.9
    characters above the ground: a real cliff a character can't jump, the columns 3.4–4.2 studs wide read as columns
    at a distance, the bushes 1.3–2.2 across are knee-to-chest high on the lawn.
- **Build frame:** front −Y, +X right, ground z 0. Tile seams at x = ±8.0, the back plane at y = +4.0, the column fronts
  at y ≈ −4. Stage 2 re-centres the hero on its bbox bottom centre; record where the seams and the back plane end up
  relative to the origin (§2.4).

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | Rock R | Green G | Connector C | O of silhouette | Columns visible |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (20,112,507,414) | 60–455 × 112–411 (396 × 300) | **1.320** | 75.5 % | 24.2 % | 0 | 1.6 % | 6 (5 + the left end chamfer) |
| Rear three-quarter (517,112,1004,414) | 556–979 × 112–403 (424 × 292) | 1.452 | 78.4 % | 21.3 % | 0 | 1.5 % | 6 + a stepped end |
| Front (20,478,289,686) | 23–280 × 482–671 (258 × 190) | **1.358** | 78.6 % | 21.3 % | 0 | 2.0 % | 5 |
| Side (290,478,500,686) | 323–451 × 483–674 (129 × 192) | **0.672** | 42.9 % | 16.9 % | **40.0 %** | 3.3 % | 2 in front of the plate |
| Rear (501,478,762,686) | 504–751 × 483–672 (248 × 190) | 1.305 | 78.0 % | 21.8 % | 0 | 1.7 % | 5 |
| Top (763,478,1004,686) | 779–992 × 492–672 (214 × 181) | 1.182 (W : D) | 29.0 % | 70.6 % | 0 | 1.9 % | — |

- Shares are of R + G + D + C (D is 0.2–0.5 % everywhere); the ground shadow is background. **Verifier tolerance:**
  shares ±4 points; W : H ±0.06; positions ±0.04 of W/H unless stated.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .14 | .31 | .76 | .81 | .87 | .84 | .90 | .86 | .91 | .90 | .93 | .97 | .97 | .94 | .99 | .99 | .93 | .95 | .87 | .32 | .21 |
| Front | .20 | .52 | .82 | .89 | .89 | .88 | .84 | .89 | .91 | .86 | .88 | .94 | .90 | .96 | .97 | .94 | .87 | .92 | .85 | .58 | .15 |
| r34 | .17 | .48 | .72 | .90 | .95 | .91 | .94 | .99 | .96 | .97 | .92 | .89 | .90 | .94 | .89 | .94 | .94 | .87 | .66 | .40 | .14 |
| Rear | .20 | .53 | .85 | .92 | .89 | .95 | .98 | .98 | .92 | .92 | .92 | .86 | .86 | .89 | .89 | .87 | .93 | .92 | .85 | .56 | .28 |
| Side | .11 | .30 | .44 | .60 | .69 | .71 | .84 | .88 | .90 | .89 | .92 | .96 | .98 | .99 | .97 | .92 | .92 | .90 | .92 | .90 | .69 |

- Reading: the ends (f .00–.05 and .95–1.0) are the foot dressing (bushes, sprigs, a boulder); from f .10 to .90 a flat
  lawn line at .84–.91 with bush bumps to .94–.99. The f34 rises to the right (its face-top line runs from about .70 at
  f .15 to .86 at f .85, below): a slight front-left camera with perspective (§3.1).

**Face-top line** (`lip.py`; where the rock run from the foot meets the green of the lip, per 0.05 f; foot-dressing
columns dropped): front .74 .75 .74 .76 .77 .77 .77 .77 .78 .78 .78; rear .77 .76 .73 .72 .71 .73 .74 .74 .71 .74;
f34 .68 .73 .78 .79 .81 .84 .85 .86 (rising to the right). **The lip line is level** in the governing front view: every
column reaches it; no column stands above the lawn and none stops short.

**Bottom profiles** (lowest silhouette pixel; ground contacts):

```
f34    .13 .10 .06 .03 .00 .01 .00 .01 .01 .03 .03 .05 .07 .08 .09 .11 .12 .12 .13 .14 .20
front  .18 .04 .02 .01 .01 .00 .00 .01 .01 .01 .01 .01 .01 .01 .02 .02 .02 .02 .02 .02 .05
```

- The front cell's foot is level (.00–.02): one straight front. The f34's rises to the right (perspective).

**Width per height** (silhouette width at h .05 → .95 as a fraction of W):

```
front  .97 .97 .95 .90 .90 .89 .88 .87 .78 .10
rear   .97 .96 .98 .91 .91 .89 .88 .86 .79 .13
f34    .42 .94 .95 .87 .86 .86 .85 .81 .74 .27
side   .94 .96 .95 .89 .84 .84 .79 .68 .64 .19
```

- Front: the face is 0.87–0.90 of W from h .35 to .75 (a slight batter, 3 % over 0.4 H); the foot band (h .05–.25)
  .95–.97 is the face plus the end bushes and the boulder group; .78 at h .85 is the lawn seen above the lip; .10 at
  h .95 the tallest bush.

**Green fifths** (bottom → top, % of all green): f34 16.1 / 13.6 / 0.0 / 28.7 / 41.7; front 24.9 / 8.5 / 0.0 / 23.3 /
43.4; rear 21.2 / 5.7 / 0.0 / 28.4 / 44.7; r34 22.2 / 9.1 / 4.0 / 15.5 / 49.2.

### 1.3 Silhouette and composition per view

**Front (`z_front.png`) — governs, with the f34.** An elevated front view (az 0, e ≈ 12°, §3.1). Screen positions
below as f (fraction of the bbox width) and studs (x = −8 + 16 × (column x − face left) / face width, face 65–870 in
the 3.5× zoom).
- **Columns** (tops at h .73–.78, all level under the lip): C1 x −8.0 … −4.8 (3.2 wide; a dark left face 1.1 wide
  — the left end chamfer); C2 −4.8 … −0.6 (4.2; two big lit faces split by a vertical ridge at about −2.6); C3 −0.6 …
  +2.4 (3.0; dark left face 0.9 wide); C4 +2.4 … +5.2 (2.8; dark left face 1.0); C5 +5.2 … +8.0 (2.8; dark left face
  1.0, lit right face to the end). Every column shows **a shaded left face and a lit front/right face** — each column is
  a prism with a front ridge, the left face turned toward −X. Dark full-height creases between the columns.
- **Shards** (pointed, leaning on the face): A x −1.4 … 0.0, apex h .51 (at the C2/C3 crease); B x +1.8 … +6.0 (a broad
  pointed slab with one big lit face), apex h .54 at x +4.2; C x +6.2 … +7.7, apex h .31.
- **Foot boulders** (left): big Bb x −6.0 … −2.3, flat tilted top at h .30, a lime bush on top; small Bs x −6.9 … −4.9
  behind its left, top h .28; a low block Bf x −7.9 … −6.4, top h .14.
- **Lawn** (h .76 → .88) with five bushes: two dark green round bushes with brown trunks (x −7.0 … −5.1, +2.0 … +4.0;
  tops h .94–1.0), three lime ones (x −5.1 … −4.2, +0.6 … +1.8, +5.7 … +7.1); a pointed small boulder (x −2.9 … −1.5)
  and a low block (+1.6 … +2.9) on the lawn; pale pebbles.
- **Foot:** a lime apron along the foot (x −1.5 … +5.5 and both ends), a round foot bush at x −0.7 … +0.9, lime sprigs
  at both ends (overhanging the face ends by up to 0.8–1.0), pebbles (x −0.9, +0.9, +4.6, +5.4, +6.9).
- **Ground shadow:** faint, background.

**Front three-quarter (`z_f34.png`) — governs, with the front.** The same drawing from a little to the front-left and
a little higher (§3.1): six columns (the front cell's C2 reads as two), the same level lip, the same lower-left boulder
group (f .20–.45, top h .30) with its bush, shards at f .44–.56 (apex h .55) and f .66–.80 (apex h .65), a low shard at
the right end (f .89–.97, h .30). The lawn shows deeper (lawn band 0.13–0.16 H against 0.12 in the front cell). Green
drips hang 0.3–0.7 stud over the lip at four or five column tops. No moss streak on the face.

**Side (right) (`z_side.png`).** The right-hand end (+X) from the side, a little elevated. Two columns' end faces
(screen left = the front) with a low foot boulder and lime sprigs; **the grey plate covers the back 49 % of the end**
(52 of the body's 106 px), from the ground to the lawn line, its front edge a dark thin strip (the plate's thickness);
**tabs** stick out of both long edges (front edge at about h .15 and .82, back edge at about h .29 and .76 of the
plate; a third front tab hidden by the plants); a small notch at the plate's front-top corner. Lawn and bushes on top.
C share 40.0 %.

**Rear (`z_row2.png`) and rear three-quarter (`z_r34.png`).** Both draw the back as a **second palisade face** (columns,
two big pointed shards, foot boulders and bushes) and the r34's left end as stepped boulders, **with no plate** (§3.2).
They contradict the side cell, the exploded and the connector close-up.

**Top (`z_top.png`; image top = the back).** A lime lawn, nearly square (W : D 1.18), framed by the lip's rock rim
(a thin band on the left, right and back, thick stepped rim blocks along the front, drawn as if seen a little from the
front); five dark-green bushes with brown trunks (left (−5.5, +1.0), back-centre (−2.2, +3.8), back-right (+5.0, +2.4),
front-left (−3.8, −2.9), front-right small (+6.1, −2.8)) and lime sprigs at two corners; a big boulder front-right and
a medium one right of centre; pale pebbles and flat pale stepping patches (`#EFD2BE`). R 29 %, G 71 %. The square plan is
a re-composition (§3.3).

**Close-ups (`z_cu.png`, `z_cu_conn.png`).**
- **Top lip underside** (36,1167,342,1300): the lip from below: **one big flat recessed underside face** (0.24–0.25 of the
  visible stone, `facets.py`) inside a **ring of blocky rim lobes** that hang below it, each lobe a few big rock facets;
  lime lawn and bush tops show over the rim. Screen w/h 2.29.
- **Top lip to body junction** (374,1152,665,1323): the lip's rim blocks (a row of chunky rock blocks 0.3 of the visible
  height, flat-topped under the turf) **sit on the columns' flat tops along a straight horizontal joint line**; the
  lawn overhangs the rim by a hair; bushes and a boulder on the lawn. No gap, no step between rim and columns.
- **Back connector detail** (696,1153,905,1323): the body's right-end column (lit front, shaded right face), then the
  plate standing just behind it at the end; **a chunky tab box (about 1.2 tall, 0.5 deep) sticks forward out of the
  plate's front edge at mid height**, beside the column; the plate's top runs level with the lawn edge.

### 1.4 Parts (Exploded Construction (20,724,596,1094) and Parts Breakdown (597,724,1004,1094); `z_expl.png`, `z_parts.png`)

Scale: the exploded and parts drawings are elevated three-quarter views from the front-left; their proportions are
consistent with the hero within perspective (body screen w/h 1.33 / 1.11; plate 0.41 / 0.40). **The front cell governs
every size**; the parts give shapes and facet character.

| Part (box, px) | Size px | Screen w/h | Width per height (h .05 → .95) | Shares | Facets (thr 5 / 7; largest; top-5 elongation h/w) |
| --- | --- | --- | --- | --- | --- |
| Grass Top Lip, exploded (147,724,437,827) | 291 × 104 | 2.80 | .08 .36 .52 .83 .91 .98 .97 .92 .80 .51 | R 37.6 / G 61.2 / D 1.2 | rim 18 / 22, largest 0.03–0.04 (blocky, h/w 0.3–1.8) |
| Grass Top Lip, parts (621,734,860,817) | 240 × 84 | 2.86 | .43 .84 .95 1.0 .98 .94 .86 .71 .62 .35 | R 31.0 / G 68.3 / D 0.7 | — |
| Cliff Wall Body, exploded (110,826,439,1074) | 330 × 249 | 1.33 | .56 .92 .95 .92 .87 .89 .86 .85 .83 .66 | R 99.5 | 32 / 31; 0.07; **h/w 3.1–4.2** |
| Cliff Wall Body, parts (607,845,845,1060) | 239 × 216 | 1.11 | .75 .95 .95 .97 .94 .93 .93 .91 .89 .61 | R 99.8 | 24 / 27; 0.03–0.07; **h/w 2.9–4.7** |
| Flat Back Connector, exploded (452,798,553,1045) | 102 × 248 | 0.41 | .81 .81 .76 .82 .82 .77 .77 .77 .89 .42 | C 90.1 | one flat face |
| Flat Back Connector, parts (882,797,986,1058) | 105 × 262 | 0.40 | .33 .85 .86 .90 .89 .90 .86 .85 1.0 .42 | C 91.6 | one flat face |
| Hero faces: f34 (100,190,440,370) / front (30,500,270,640) / rear (510,500,750,640) | — | — | — | — | 32 / 32, 0.04–0.07, h/w 2.2–3.7; 23–24 / 24–26, 0.03–0.05, h/w 1.6–4.7 |
| Underside close-up (36,1167,342,1300) | 307 × 134 | 2.29 | .12 .46 .69 .84 .98 .98 .95 .84 .79 .54 | R 85.8 / G 14.2 | 25 / 25; **one face 0.24–0.25**, the rest small rim facets |
| Junction close-up rock band (374,1240,665,1323) | — | — | — | — | 28 / 25; 0.05; h/w 0.4–3.0 |

#### Cliff Wall Body (Main Geometry) — `z_expl.png`, `z_parts.png`, `facets_eBody.png`, `facets_pBody.png`

- **Shape:** a block of **tall vertical rock columns** standing side by side with dark creases, their **tops flat and
  level** (the parts drawing shows the flat tops at one height with two hollow pockets in the top, §3.5), plus three
  **pointed shards** leaning on the lower front (the exploded's centre-left, centre-right and right shards, apex at 0.45–
  0.6 of the body height) and **two or three flat-topped boulder blocks** at the front-left foot. The body's left end
  shows column end faces; the right end (hidden in these views) takes the plate.
- **Facets:** **long vertical strips**: the five biggest facet regions are 2.9–4.7 times taller than wide; 24–32 regions
  over the visible body (4–6 per column), the largest 0.03–0.07 of the visible area. Never round, never a ring of small
  triangles. The shards have 2–3 big faces per side with a sharp apex.
- **Hero size: 16.0 W × 8.0 D × 9.2 H** (column tops at 9.2 under the lip); the foot boulders and shards stand in front
  to y ≈ −5.6.

#### Grass Top Lip (Top Surface) — exploded, parts, both close-ups

- **Shape:** a **flat slab**: a lime turf top (thin, its front edge scalloped by the column fronts) over a **rock rim** of
  chunky blocks around the edge, a flat recessed underside inside the rim ("Underside matches rock style"). In the
  exploded the rim shows 0.35–0.45 of the lip's front height and hangs lowest under the front corners. Lawn dressing:
  bushes, two small boulders, pebbles, sprigs.
- **Hero size: 16.0 × 8.3 (front edge 0.1–0.3 proud of the column fronts) × 1.2** (rim bottom 9.2, turf 10.1–10.4),
  plus the dressing to z ≈ 12.3.

#### Flat Back Connector (Modular Join) — exploded, parts, side cell, connector close-up

- **Shape:** a **flat rectangular plate** (screen w/h 0.40–0.41; the side cell gives 3.6 / 10.3 = 0.35), a dead-flat face
  on both sides, a thin edge (about 0.1 of its width), **three rectangular tabs on each long edge** (parts: left edge at
  about .09, .41, .83 of its height; right edge at about .17, .52, .91; side cell: .15 / .82 front, .29 / .76 back), each
  tab about 0.10 of the plate height tall and proud of the edge by about 0.1 of the plate's width, chunkier than the
  plate is thick; **a small rectangular notch at one top corner** (the front-top corner on the hero).
- **Hero size: 3.9 (Y) × 10.05 (Z) × 0.4 (X)**, tabs 1.0 tall × 0.35 proud × 0.5 thick.

#### Bushes, sprigs and small rocks (lawn and foot; `z_bushes.png`, `z_foot.png`, top cell)

- **Round leafy bush (dark green):** a dome of **broad diamond-to-oval leaves** (10–12, two tiers, pointed tips) round a
  short **brown trunk** that shows under the canopy; the top view reads as a rosette with a dark centre. Ø 2.0–2.2,
  1.7–1.9 tall (trunk 0.35–0.5). Leaves 0.8–1.0 long, 0.5–0.6 wide, folded.
- **Lime bush:** the same build, smaller and yellow-lime (Ø 1.2–1.4, 1.0–1.2 tall, 6–8 leaves, trunk hidden).
- **Sprig:** 3–5 lime and mid-green leaves from one root (Ø 0.6–0.9), at the foot ends and on the boulder top.
- **Lawn boulders:** a pointed 4–5-sided small rock (1.5 × 1.3 × 1.2) and a low flat block (1.6 × 1.3 × 1.1); **pebbles**
  0.25–0.6, low and flat-topped; **stepping patches** 0.6–0.9 flat pale slabs 0.08 proud of the lawn.
- **Foot boulders:** flat-topped chunky blocks like short columns (5–6 sides, near-vertical sides, a top facet tilted
  5–10° to the front); never eggs.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0). X from the front cell (face 16 wide, §1.3); Y from the side and top
cells; Z from the front cell's screen heights at e ≈ 12° (z ≈ (h × 13.7 − (y + 5.6) × 0.21) / 0.98).

### 2.1 The tile contract (binding; record it in the builder docstring and the export notes)

| Item | Value | Notes |
| --- | --- | --- |
| Seam planes | **x = −8.0 and x = +8.0** (pitch 16.0) | nothing rock or plate crosses them; foliage may (§6) |
| Back plane | **y = +4.0**, flat (relief only inward, to y ≥ +3.6) | "flat rear/connector region" (WorldModeling §12.2); butts against terrain or a back module |
| Column fronts | y −3.8 … −4.3 (in/out per column) | the front is irregular, the seams are not |
| Ground | z 0, flat floor-cut bottom on every rock shell | |
| Column tops / lip bottom | **z 9.2** (flat) | every column top is under the lip |
| Lip recess (underside) | z 9.5 | flat, hidden in the assembly |
| Turf | **z 10.1 → 10.4** (lawn top 10.4, flat within ±0.03 for 1.0 stud of each seam) | the shared plateau level with M032 |
| Lip front edge at the seams | y −4.2 at x = ±8 exactly | so neighbouring lips line up |
| End profile at the seams | identical at x = −8 and x = +8 from y −2.6 to +4.0: the core's end face flat on the seam plane from z 0 to 9.2, the lip's end face flat from 9.2 to 10.4 | so any tile meets any tile |
| End chamfers | −X end: the front corner cut 1.0 × 1.0 (from (−8, −3.2) to (−7.0, −4.2)); +X end: 0.5 × 0.6 | in a run the seam reads as one more column crease (V about 1.5 wide, 0.8 deep) |
| Connector plate | **+X end only**: x 7.6 … 8.0, y +0.1 … +4.0, z 0 … 10.05; tabs project ±Y | the next tile's −X end meets the plate's outer face on the seam plane |
| Lip end over the plate | the turf runs to x = +7.98 over the plate (turf bottom 10.1 > plate top 10.05) | never coplanar with the plate's outer face (x 8.0) |
| Foot dressing | rocks and pebbles inside x −7.95 … +7.95; foliage overhang ≤ 0.8 past a seam, symmetric at both ends | |

- **How tiles meet:** place tiles every 16 studs along X with the same rotation. Tile N's plate (outer face on x = +8)
  touches tile N+1's flat core end (x = −8 of N+1) over the back half; in front of it, N's +X chamfer and N+1's −X
  chamfer make a V crease like the other column creases; the lips meet flush (same front y, same turf z, flat ends); the
  lawns join without a grey strip (decision §8.4). Front dressing doesn't collide (rocks stay 0.05 inside).
- **Run ends:** a tile at the right end of a run shows its plate (as the side cell does); a left end shows the flat core
  end and the columns' end faces. End-cap and corner modules are later sheets (WorldModeling §12.2; W02's
  inner/outer corners) and should reuse this contract.

### 2.2 Body pieces

| Piece | Plan / position (x, y), base z | Size W × D × H | Notes | Sheet evidence (front cell) |
| --- | --- | --- | --- | --- |
| Core | x −8 … +8 (+X stops at 7.6 over y +0.1 … +4), y −2.6 … +4.0, z 0 … 9.0 | 16 × 6.6 × 9.0 | flat back with 4–6 shallow vertical facets (relief ≤ 0.4, inward), flat ends on the seams; top hidden under the lip | side cell; WorldModeling §12.2 |
| C1 | x −8.0 … −4.8; front ridge at (−5.6, −4.2) | 3.2 × 3.4 × 9.2 | left face = the −X end chamfer (1.0 × 1.0), lit front face 2.4 | f .03–.24 top; dark left facet 1.1 |
| C2 | x −4.8 … −0.6; ridge at (−2.6, −4.3) | 4.2 × 3.4 × 9.2 | the widest; two big lit faces | f .24–.47 |
| C3 | x −0.6 … +2.4; ridge at (+1.0, −3.8) | 3.0 × 3.0 × 9.2 | set back 0.4; dark left face 0.9 | f .47–.64 |
| C4 | x +2.4 … +5.2; ridge at (+3.6, −4.1) | 2.8 × 3.2 × 9.2 | dark left face 1.0 | f .64–.79 |
| C5 | x +5.2 … +8.0; ridge at (+6.3, −3.9) | 2.8 × 3.1 × 9.2 | dark left face 1.0; +X chamfer 0.5 × 0.6; flush with the seam behind it | f .79–.97 |
| Shard A | base x −1.4 … 0.0, y −5.0 … −3.7; apex (−0.6, −4.0, 6.5) | 1.4 × 1.3 × 6.5 | 4-sided, leans back 10° into the C2/C3 crease | apex h .51 |
| Shard B | base x +1.8 … +6.0, y −5.3 … −3.8; apex (+4.2, −4.0, 7.0) | 4.2 × 1.5 × 7.0 | a broad pointed slab, one big lit front face, 5-sided | apex h .54 |
| Shard C | base x +6.2 … +7.7, y −4.9 … −3.8; apex (+7.0, −4.1, 4.0) | 1.5 × 1.1 × 4.0 | 4-sided | apex h .31 |
| Boulder Bb | centre (−4.1, −5.0) | 3.4 × 2.4 × 3.6 | flat top tilted 8° to the front; a lime bush on it | top h .30 |
| Boulder Bs | centre (−6.0, −4.5) | 2.0 × 1.8 × 3.2 | behind Bb's left | top h .28 |
| Boulder Bf | centre (−7.2, −5.0) | 1.5 × 1.4 × 1.7 | inside the seam (x ≥ −7.95) | top h .14 |

- Column faces: each column a 6–7-sided prism (back corners buried in the core) with a front ridge vertex; its left
  front face turned 35–50° toward −X, its right front face 10–20° toward +X; each long face split into 2 facets along its
  height (a vertex at 0.35–0.65 H pushed in or out by 0.1–0.2) so the facets are tall strips (h/w 3–4.5); top ring
  0.94–0.97 of the foot ring (a slight batter); creases between neighbours 0.3–0.6 deep.

### 2.3 Lip and dressing

| Piece | Position (x, y), z | Size | Notes | Sheet evidence |
| --- | --- | --- | --- | --- |
| Lip outline | x −8 … +8; back y +4.0; front edge following the column ridges 0.1–0.3 proud (y −4.0 … −4.5), y −4.2 at both seams | 16 × 8.3 | scalloped front, straight ends and back | front cell lip line .74–.78; junction close-up |
| Turf | z 10.1 → 10.4 | 0.3 thick | lawn top flat; 5 drips over the front rim at x −6.6, −3.3, +0.3, +3.6, +6.4, 0.3–0.7 down, 0.5–0.9 wide | f34 drips |
| Rim ring | z 9.2 → 10.1, 1.0–1.4 wide inside the outline | blocks 0.8–1.6 long | outer faces of the front broken into blocks (±0.12 in/out, a few hanging 0.1 lower over the column joints); ends and back flat | junction close-up, underside close-up |
| Recess | z 9.5 | inside the rim | one flat face | underside close-up (0.25 of the visible stone) |
| L1 dark bush | (−5.6, +1.0), 10.4 | Ø 2.1, 1.8 tall | brown trunk shows | front x −7.0 … −5.1; top cell left |
| L2 dark bush | (+3.6, +2.4), 10.4 | Ø 2.1, 1.8 tall | | front x +2.0 … +4.0; top back-right |
| L3 lime bush | (−3.9, −2.5), 10.4 | Ø 1.3, 1.1 tall | | front x −5.1 … −4.2; top front-left |
| L4 lime bush | (+0.9, +3.3), 10.4 | Ø 1.3, 1.1 tall | | front x +0.6 … +1.8 |
| L5 lime bush | (+6.3, −2.4), 10.4 | Ø 1.3, 1.1 tall | | front x +5.7 … +7.1; top front-right |
| Lawn sprigs | (−7.2, +3.2), (+7.0, +3.5) | Ø 0.8 | | top cell corners |
| Lawn boulders | R1 (−2.2, +2.4); R2 (+2.6, −0.6) | 1.5 × 1.3 × 1.2 pointed; 1.6 × 1.3 × 1.1 block | sunk 0.1 into the turf | front x −2.9 … −1.5 and +1.6 … +2.9 |
| Pebbles / patches | 8–10 pebbles 0.25–0.6; 3 flat patches 0.6–0.9 | | spread over the lawn, none within 0.4 of the front edge | top cell |
| Foot bush F1 | (0.1, −5.3), 0 | Ø 1.6, 1.4 tall | in front of shard A | front x −0.7 … +0.9 |
| Boulder-top bush | on Bb's top (−4.6, −5.0, ≈3.6) | Ø 1.4 lime | | front cell |
| Foot sprigs | (−7.9, −5.0), (−6.6, −5.7), (+5.8, −5.4), (+7.9, −4.9), (−2.4, −5.6) | Ø 0.7–1.0 | the end ones overhang the seams ≤ 0.8, symmetric | front cell ends |
| Foot pebbles | (−0.9, −5.6), (+0.9, −5.4), (+4.6, −5.4), (+5.4, −5.7), (−5.0, −6.0), (+6.9, −5.3), (−2.4, −5.9) | 0.4–0.9 | | front cell |
| Grass apron | x −1.5 … +5.5 and both ends, y −6.0 … −3.8 | 0.08–0.12 thick, jagged outline | flat lime patches on the ground, tucked 0.1 under the face | f34 / front foot strip |

### 2.4 Expected extents and screen checks

- **Extents (build frame):** X −8.8 … +8.8 (foliage overhang; rock −8.0 … +8.0); Y −6.0 … +4.35 (apron in front; back
  tabs 0.35 behind the back plane); Z 0 … 12.3 (L1/L2 tops). Bbox ≈ 17.6 × 10.35 × 12.3. After re-centring, record the
  seam planes (x = ±8.0 if the overhang is symmetric) and the back plane (y = +4.0 − y_centre) in the builder.
- **Self-consistency at `front_sheet (0, 12)`:** face top (lip front at z 10.4, y −4.2) 10.4 / 13.7 = .76 (sheet .745);
  lawn back edge 12.2 / 13.7 = .89 (sheet .86–.90); shard tops A .51, B .55, C .31; Bb top .29; W : H 17.6 / 13.7 =
  1.28 (sheet 1.358, the foot overhang is shorter than the sheet's 1.0 per end: within −0.08, record).
- **Checks on the renders** (floor hidden):
  - **front_sheet (0, 12):** W : H 1.24–1.40; **face width / face-top height 1.50–1.66** (sheet 1.62); face-top line
    level at .72–.79 everywhere between f .10 and .90; top profile within ±0.07 (mean ≤ 0.04) of §1.2; width per height
    within ±0.07; 5 columns at the §1.3 x positions ±0.4; shares R 78.6 ± 4, G 21.3 ± 4; green fifths within ±7,
    middle fifth ≤ 3.
  - **f34_sheet (−10, 16):** W : H 1.26–1.38; shares R 75.5 ± 4, G 24.2 ± 4; green fifths 16.1 / 13.6 / 0 / 28.7 / 41.7
    ±7; the face-top line rising to the right as on the sheet (about .70 at f .15 → .86 at f .85, ±0.05).
  - **side (90, 10):** W : H 0.62–0.74 (sheet 0.672); C 34–46 % (sheet 40.0); the plate covering the back 45–52 % of the
    end, reaching the lawn line; tabs visible on both edges.

### 2.5 Rock-shape targets (binding; check with `M.audit`, own bmesh code and `facets.py` on the renders)

M032 failed round 1 on a turf slab that didn't cap the columns; M034 failed on egg-shaped boulders; M023 on soccer-ball
facets; W02 needed rounds to stop the columns reading as boulders. These are measurable:

| Target | Columns C1–C5 | Shards A–C | Foot boulders | Lawn boulders / pebbles | Lip rim |
| --- | --- | --- | --- | --- | --- |
| Mesh tris (before any refine) | 40–64 each | 16–30 | 24–40 | 12–24 / 8–12 | (in the lip, §4.3) |
| Sides | 6–7 (back corners in the core) | 4–5 + apex | 5–6 | 4–6 | blocks 0.8–1.6 long |
| Facets visible from the front | 3–6 per column | 2–3 per side | 6–10 | 4–6 | 1–2 per block |
| Facet shape | **tall strips h/w 3–4.5** (5 biggest) | long triangles to the apex | broad, h/w 0.8–2 | broad | blocky h/w 0.4–1.8 |
| Top | **flat at 9.2, entirely under the lip** | sharp apex | flat, tilted 5–10°, ≥ 35 % of the plan area | flat-ish | flat under the turf |
| Side faces within 20° of vertical | ≥ 85 % of side area | ≥ 60 % | **≥ 50 %** (no eggs) | — | ≥ 80 % |
| Narrowest face | ≥ 0.8 wide, ≥ 2.5 tall | — | ≥ 0.5 | — | — |

- **Irregular, not a pattern:** triangle area CV ≥ 0.6 on the body; no vertex ringed by 5–6 near-equal triangles; no
  pentagon/hexagon faces; never `primitive_ico_sphere`, Fibonacci planes, subdivision or displacement; not
  `K.hull_rock` with random ring jitter for the columns (explicit prisms, like `m032.column_pts`).
- **Capping (M032's lesson):** column faces with n.z > 0.5 above z 8.0 that are visible from above (not under the lip
  or the core): **0 studs²**; rock visible from straight above inside the tile = the rim's outer top bevel (≤ 0.3 wide)
  + lawn boulders + pebbles + foot boulder and shard tops, total ≤ 25 studs².

## 3. View conflicts and resolutions

### 3.1 Front three-quarter vs front cell: one drawing from two cameras

- **Evidence.** The same five columns, level lip, boulder group with its bush, the same two big shards and the low right
  shard, the same lawn bushes; W : H 1.32 against 1.358; shares 75.5 / 24.2 against 78.6 / 21.3. The f34's face-top line
  rises to the right (.70 → .86) and its foot too (.00 → .14): a camera a little to the front-left with perspective; the
  left end chamfer reads 0.03 of W wide, so the azimuth is small (5–15°). The lawn band is 0.12 H in the front cell and
  0.13–0.16 in the f34: e ≈ 12° and ≈ 16° for D = 8.
- **Resolution.** Compare the front cell with **`front_sheet (0, 12)`** (probe e 8 / 12 / 16) and the f34 with
  **`f34_sheet (−10, 16)`** (probe az −5 / −10 / −15 × e 12 / 16 / 22), keep the smallest top-profile error and
  record it. The kit `front34` is self-consistency only.

### 3.2 Flat back with an end plate (side, exploded, close-up) vs rock on the back (rear, r34)

- **Evidence.** The side cell shows the grey plate on the +X end covering the back half, with nothing behind it; the
  exploded's arrows push the plate onto the body's right end; the connector close-up shows it standing behind the
  right-end column; the sheet notes and WorldModeling §12.2 want a flat rear/connector region. The rear cell and the r34
  draw a second column face on the back (two big shards, boulders, bushes at the foot) and a stepped rock end where the
  plate should be.
- **Resolution (decision §8.2).** **A flat back** (the back plane y = +4.0, 4–6 shallow vertical facets ≤ 0.4 deep so it
  reads as rock, no dressing behind) and the **plate on the +X end**. Render `rear_sheet (180, 12)` and `r34_sheet
  (150, 16)` and judge them loosely: lawn and bushes on top, rock 70–85 %, green 12–26 %; record "back is a flat
  connector region, the sheet's rear cells redraw the front" as a known miss. The alternative, a double-faced ridge
  with columns on both long faces, would break the side cell, the plate and the tiling.

### 3.3 Top cell: near-square plan vs the 2 : 1 tile

- **Evidence.** The top cell is W : D 1.18 with a thick stepped rim drawn along the front (a perspective re-composition:
  a true top view can't see the front face). The side cell (drawn at the front's scale) gives a body depth of 7.4 studs
  and the plate covers half of it; the front cell's lawn band (0.12 H at e ≈ 12°) gives D ≈ 8.
- **Resolution.** D = 8.0. Render the kit top (0, 89) and judge it for what it agrees with: a lime lawn edged by the
  rim on all sides, five bushes in the §2.3 places (two dark, three lime), two lawn boulders, pebbles; **G 60–80 %**
  (sheet 70.6), R ≤ 32 % (sheet 29.0). Record W : D (ours ≈ 1.75) as a known miss.

### 3.4 The face batters slightly; the seams must be vertical

- **Evidence.** The front face narrows 3 % from h .35 to .75 (the end columns lean in a little).
- **Resolution.** Seams vertical at x = ±8 (tiling); the batter comes from the columns' top rings at 0.94–0.97 of the
  foot ring on the front and left/right faces that aren't on a seam, and from the end chamfers. No end column leans past
  the seam plane.

### 3.5 Pockets in the body's top (exploded, parts) vs "simple flat joining surfaces"

- **Evidence.** The exploded and parts bodies show two hollow square pockets in the body's top; the junction close-up
  says the lip sits on flat joining surfaces; in the assembly the top is never seen.
- **Resolution (decision §8.6).** **No pockets**: flat column tops at 9.2 and the core top at 9.0 (a 0.2 step that reads as
  a joint in the body part's renders). Record the pockets as a known miss on the body part. (Booleans for pockets would
  add crash risk for a feature hidden in every assembled view.)

### 3.6 Plate top: level with the lawn (close-up) vs a seamless lawn in a run

- **Evidence.** In the connector close-up the plate's top runs level with the lawn edge; in the side cell it reaches the
  lawn line.
- **Resolution (decision §8.4).** Plate top at **10.05**, just under the turf (10.1–10.4), and the turf runs over it to
  x = 7.98: from the side the plate reaches the lawn line (the turf edge sits on it), and a run of tiles shows one
  unbroken lawn. A plate flush with the lawn would put a 0.4-wide grey strip across the back half of every seam.

### 3.7 Exploded and close-ups against the hero

- The parts' proportions agree with the hero within perspective (§1.4). The underside close-up's lobes hang below a flat
  recess: our rim ring (9.2–10.1) and recess (9.5). The junction close-up's flat joint between the rim blocks and the
  column tops is the 9.2 plane (rim bottom on the column tops, no gap, no overlap beyond 0.03).

### 3.8 Palette names against the renders

- **"Rock Shadow" `#6E6F7D` (236°, B > G ≥ R)** equals the rendered shade faces (`#716F7C` f34, `#6C6F80` r34, `#696A7D`
  rear): the cool sky fill, **not paint**. Using it as a key gives blue or mauve rock.
- **"Rock Mid" `#AFA1A0` (4°, 0.09)** is a shaded mid tone and sits on the mauve edge (hue < 10°); never a key.
- **"Rock Light" `#CDB8AF` (18°, 0.15, 0.80)** is close to the stone; the rendered lit faces are warmer and stronger
  (`#E4C2AC`, 24°, 0.25).
- **"Grass" `#A5C624` (72°, 0.82)** is greener and darker than the rendered lawn (`#C2D512` top cell, `#D2DD14` f34).
- **"Foliage Dark" `#637C59` (103°, 0.28)** has the dark bushes' hue but a quarter of their saturation (rendered
  `#2D7E22`–`#357823`, 107–113°, 0.71–0.73). **"Foliage Light" `#B5C517` (66°)** matches the lime bushes (`#AAC602`–
  `#AEC807`).
- **"Dirt / Earth" `#9A6846` (24°, 0.55)** is the trunk family (rendered `#5E3813`–`#6A2E12`); there is no dirt band
  under the turf on this sheet (the lip's rim is rock).
- **The connector has no swatch**: it renders `#918A8E`–`#958D90` (326–343°, 0.05) in four cells.

### 3.9 "No noise, no micro detail" against the user's blended-colour rule

- The user's rule wins, quietly: broad lighter faces high on the columns and on the rim, slightly deeper ones at the
  foot, whole-facet mottling, lawn patches, leaf tiers. No per-triangle confetti, no moss streaks on the face (the
  middle fifth has 0 % green).

## 4. Construction plan (stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `body()` → `StoneCliffBody`: core, C1–C5 (`column(spec)`, explicit prisms as `m032.column_pts`), shards A–C
     (`shard(spec)`), foot boulders Bb/Bs/Bf (`block_rock(spec)`), no plants. Compare with the exploded and parts bodies
     (outline, width per height, facet strips, the flat level top).
   - `lip(dress=True)` → `StoneCliffGrassLip`: turf + rim ring + recess as one closed slab (`lip_slab()`: a 2D outline,
     `m032.cdt_region`/`m032.slab` style, rim blocks as offsets of the outline), plus the lawn dressing (`bush()`,
     `sprig()`, `small_rock()`, `pebble()`, `patch()`). Compare with the exploded and parts lips and with an
     **underside extra** (the lip from below, e −30) against the underside close-up (one flat recess ≥ 0.2 of the
     visible underside, rim lobes around).
   - `connector()` → `StoneCliffBackConnector`: plate + 6 tabs + the top notch, authored in place on the +X end (x
     7.6–8.0). Compare with the parts plate (w/h 0.39–0.42, tabs at the §1.4 heights).
   - Render a **parts shot** (az −20, e 22) laid out like the exploded (lip above, body below, plate to the right turned
     to the viewer).
2. **Hero:** body + lip (sunk 0.03 onto the column tops) + connector + foot dressing (apron, F1, boulder-top bush, sprigs,
   pebbles), each its own closed shell; `M.fix_bowties`; origin at the bbox bottom centre; transforms applied.
3. **Budget** (§4.3): hero about 2400–3100 (limit 4000); parts under 1000 (the lip part is the tight one: if over 950,
   tag one lime bush and the two lawn sprigs `on="hero"` as M032 did, never thin the slab or the columns).
4. **Placeholder keys** (stage 1): `m040_rock`, `m040_grass`, `m040_leaf`, `m040_trunk`, `m040_connector`. Stage 4 adds
   the rest (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** a long straight palisade of five flat-faced columns, all to one level, a flat lime lawn capping
      them, three pointed shards and a boulder group on the lower front, a grey plate on the right end in the side view.
   2. **front_sheet and f34_sheet** against their cells (§2.4).
   3. **side** (§2.4); **rear_sheet, r34_sheet, top** loosely (§3.2, §3.3).
   4. **Rock-shape targets** (§2.5), all of them, on the body part and the hero.
   5. **Capping:** the §2.5 capping numbers, and a **junction extra** `junc_cu (−20, 25)` framed on the C2/C3 lip front
      against the junction close-up (rim blocks on the column tops, one straight joint, no gap).
   6. **Connector extra** `conn_cu (35, 18)` on the +X end against the connector close-up (plate behind the end column,
      a front tab beside it, the plate top at the lawn line).
   7. **Tiling shot:** three hero copies at x −16 / 0 / +16 rendered from `front34` and from straight above: no gap, no
      overlap of rock, the lips flush and level, the seams reading as column creases, one unbroken lawn.
   8. **Hero size** per §1.1 and §2.4 extents; **scale shot** beside a 5.5-stud character marker.
6. **Stage 2:** every shell closed and manifold: zero non-manifold edges and verts (`nonmanifold_verts` 0), boundary,
   wire and loose elements; no zero-area faces or n-gons; normals outward; no corners under 5° on visible faces (the
   long column strips must stay above it: `m011._tidy` / `_desliver`); no decimation below §2.5. Check the seam faces are
   exactly planar (all verts at x = ±8.0 ± 0.001 on the core and lip ends).
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density (leaves and pebbles included).

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Core (flat back facets, ends) | 1 | 40–70 | 40–70 |
| Columns C1–C5 | 5 | 40–64 | 200–320 |
| Shards A–C | 3 | 16–30 | 48–90 |
| Foot boulders | 3 | 24–40 | 72–120 |
| Lip slab (turf CDT + rim ring + recess + drips) | 1 | 300–420 | 300–420 |
| Dark bushes L1, L2 (10–12 leaves × 12–16 + trunk 10) | 2 | 130–200 | 260–400 |
| Lime bushes L3–L5, boulder-top, F1 (6–8 leaves + trunk 8) | 5 | 80–130 | 400–650 |
| Sprigs (3–5 leaves) | 7 | 40–80 | 280–560 |
| Lawn boulders / pebbles / patches | 2 / 17 / 3 | 12–24 / 8–12 / 12 | 200–290 |
| Grass apron patches | 3 | 16–30 | 48–90 |
| Connector (plate 12 + 6 tabs × 12 + notch) | 1 | 84–100 | 84–100 |
| **Hero** | | | **about 2400–3100** (limit 4000) |
| Parts: Body / GrassLip / BackConnector | | | about 450–650 / 850–990 / 84–100 (limit 1000) |

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 50 × 52 box inside each, sd ≤ 1.4)

| Swatch | Box | Hex | HSV | Channel order | Use |
| --- | --- | --- | --- | --- | --- |
| Rock Light | (42,1386,91,1438) | `#CDB8AF` | 18°, 0.15, 0.80 | R > G > B | start for `rock_light` |
| Rock Mid | (115,1386,164,1438) | `#AFA1A0` | **4°**, 0.09, 0.69 | R > G ≥ B (near mauve) | **never a key** |
| Rock Shadow | (188,1386,237,1438) | `#6E6F7D` | **236°**, 0.12, 0.49 | **B > G ≥ R** | **never a key** (light) |
| Grass | (262,1386,311,1438) | `#A5C624` | 72°, 0.82, 0.78 | G > R > B | start for `grass` |
| Foliage Dark | (335,1386,384,1438) | `#637C59` | 103°, 0.28, 0.49 | G > R > B | hue for `leaf`; far too grey |
| Foliage Light | (409,1386,458,1438) | `#B5C517` | 66°, 0.88, 0.77 | G > R > B | start for `leaf_light` |
| Dirt / Earth | (482,1386,532,1438) | `#9A6846` | 24°, 0.55, 0.60 | R > G > B | start for `trunk` |

### 5.2 Rendered regions (`samp.py`, `bush.py`; median / lit quartile / shade quartile)

| Region | Median | Lit | Shade |
| --- | --- | --- | --- |
| Rock, whole f34 / front / r34 / rear | `#C3A598` / `#BEA59B` / `#C1A295` / `#B79C93` | `#E4C2AC` / `#E0C0AD` / `#E4C1AB` / `#DCBBA8` | `#716F7C` / `#716E7E` / `#6C6F80` / `#696A7D` |
| Rock warm faces only (hue ≤ 60 or ≥ 340): f34 / front / exploded body / parts body | `#D4B29D` / `#D2B4A1` / `#C9AB9B` / `#CEAF9F` | `#E8C7B1` / `#E4C5B2` / `#E3C3AF` / `#E5C7B3` | `#A38F84` / `#AB948B` / `#A08B85` / `#A3908E` |
| Rock cool faces (the shade light) f34 / exploded body | `#727285` / `#707083` (240°) | | |
| Warm share of rock: f34 / front / r34 / exploded / parts | 76.0 / 71.9 / 70.4 / 63.6 / 63.0 % | | |
| Body thirds, exploded (top / mid / bottom) | `#C1A39A` / `#AA9592` / `#A08D8C` | `#EECCB7` / `#D3B3A2` / `#D4B4A2` | |
| Body thirds, parts (top / mid / bottom) | `#C2A69B` / `#AC9894` / `#A18E8E` | `#F1CFB9` / `#D6B7A5` / `#D8B9A8` | |
| Lip rock (rim), exploded / parts | `#B59382` / `#8F7976` (rim mostly in shade) | `#DEC0A8` / `#D4B7A1` | |
| Junction close-up rock | `#C3A392` | `#F2D5BF` | `#5C657C` |
| Underside close-up rock (in shade) | `#766869` | `#E0C2B0` | `#615C64` |
| Lawn: top / f34 / front / exploded lip / parts lip | `#C2D512` / `#D2DD14` / `#CDD817` / `#CAD91B` / `#CDDC1D` | `#C8D819` / `#DFE524` / `#E1E33A` / `#D6E025` / `#D8E228` | `#B4C909` / `#ABC206` / `#A6BE08` / `#B4CA0C` / `#B9CC0B` |
| Dark bushes: f34 B1 / front B4 (boxes include some lawn) | `#357823` (107°, 0.71) / `#2D7E22` (113°, 0.73) | `#89D235` / `#86D23E` | `#102F09` / `#07400F` |
| Bush mask, all cells (h ≥ 80 or v < .6) | `#447714`–`#4B7A19` (88–93°, 0.79–0.83, 0.45–0.48) | `#78B82D`–`#7EBE39` | `#16430B`–`#1A460B` |
| Lime bushes: f34 B2 / front B6 / foot bush | `#AAC602` (69°, 0.99) / `#AEC807` (68°, 0.97) / `#8DB008` (72°) | `#EDF304` / `#DCEE14` / `#B6DE08` | `#436901` / `#2B5806` / `#254609` |
| Trunks (B1 / top) | `#5E3813` (29°, 0.80) / `#6A2E12` (19°, 0.83) | | |
| Connector: side / exploded / parts / close-up | `#958D90` / `#918A8E` / `#90898D` / `#958C8E` (320–347°, 0.04–0.06, v 0.55–0.58) | `#978F92` | `#8B8589` |
| Pale stepping patches (top) | `#EFD2BE` (24°, 0.21, 0.94) | | |

Deciles (dark → light):

```
rock  f34    #636572 #787281 #8D8187 #A8928E #BB9F96 #CAAB98 #D7B49D #DCB9A3 #E0BFA9 #F2D6BF
rock  front  #5D6374 #78727E #8D838C #A69491 #B79F98 #C7AA9C #D4B4A1 #D7B8A7 #DDBEAA #EDD1BB
green f34    #1A4B0D #407415 #709A0E #97BE13 #BCD20A #CDDA0F #D3DE14 #D4E11A #D7E320 #E4E839
green front  #1B440C #3D6B15 #658C12 #89B31D #AECA0D #C5D30F #CDD914 #CFDD1E #D5E023 #E4E462
```

### 5.3 How the colour works

**Rock.**
- **One pale warm peach-grey stone** for the columns, shards, boulders, the lip rim, lawn boulders and pebbles. Warm
  faces hue 20–25°, sat 0.22–0.26, **always R > G > B**. The sheet's shaded faces are blue-lavender (240°): the cool fill
  light. Our studio's shade is warm grey; that is light, not paint. **Never colour by facing.**
- **Gentle painted signal by height:** the upper third of the face renders lighter (lit `#EECCB7`–`#F1CFB9` against
  `#D3B3A2`–`#D8B9A8` lower down), the lip rim lightest, the lowest 1.5 studs a touch deeper. Whole facets, by height and
  a broad noise field. No dark foot band, no moss streaks, no green on the middle of the face.
- **Mauve guard (M031, M032 round 1):** every rock key R > G > B, hue 15–26°, R − B ≥ 30. `#AFA1A0` (Rock Mid, 4°) and
  `#6E6F7D` (Rock Shadow, 236°) are never keys, not even as a mix.

**Lawn.** A bright yellow-lime field (63–67°, sat ≥ 0.88): lighter patches (lit `#DFE524`) and slightly deeper lime
(`#ABC206`) near the bushes, the boulders and the drips. Stepping patches pale warm stone.

**Bushes.** Two plant types, chosen per plant (not per face): **dark-green round bushes** (107–113°, sat 0.71–0.80, value
0.47–0.49; lit leaves `#86D23E`, inner/lower leaves deep `#16430B`) and **lime bushes and sprigs** (66–72°, sat ≥ 0.95;
lit `#DCEE14`, shade `#2B5806`). Brown trunks under the dark bushes.

**Connector.** A flat neutral grey (`#918A8E`, sat ≤ 0.06), smoother than the rock, no mottling beyond a faint Tint.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

The calibration targets are medians of unshadowed rendered regions (the warm faces of the exploded and parts bodies,
the top-view lawn, the bush samples, the plate), not swatches. `K.sample` kinds: `"stone"` for rock and connector,
`"green"` for lawn and leaves, `"vivid"` for the lime bushes, `"brown"` for the trunk.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m040_rock` | `#CCAD9D` (warm faces: exploded body `#C9AB9B`, parts body `#CEAF9F`; f34 `#D4B29D`; start from swatch Rock Light `#CDB8AF`) | 18–24°, 0.18–0.26, R > G > B | all rock, default | rough 0.9, metal 0 |
| `m040_rock_light` | `#DDC1AE` (top-third lit `#EECCB7`/`#F1CFB9` against mid `#D3B3A2`: about +15 levels over `rock`) | 20–25°, 0.17–0.24, R > G > B | upper 30 % of the columns at 30–40 %; the lip rim at 45 %; pebbles and stepping patches | rough 0.9 |
| `m040_rock_deep` | `#BA9E8E` (a step below `rock`, hue kept warm) | 18–24°, 0.22–0.28, R > G > B | broad patches below 1.5 studs at 15 %, the shards' lower halves at 10 % | rough 0.9 |
| `m040_grass` | `#C4D614` (top-view lawn `#C2D512`; f34 `#D2DD14`; swatch Grass `#A5C624`) | 63–68°, ≥ 0.88, G > R > B | lawn, apron, drips, default | rough 0.85, low spec |
| `m040_grass_light` | `#DBE323` (lit quartiles `#DFE524`, `#DDE422`) | 60–64°, ≥ 0.82 | broad lawn patches at 25 % | rough 0.85, low spec |
| `m040_grass_deep` | `#AAC008` (shade quartiles `#ABC206`, `#A7BF07`) | 66–70°, ≥ 0.93 | within 0.8 of bush roots and lawn boulders, the drip tips, the apron's inner edge, at 30 % | rough 0.85, low spec |
| `m040_leaf` | `#3A7C22` (dark bushes `#357823`, `#2D7E22`; bush mask `#447714`–`#4B7A19`; hue from swatch Foliage Dark) | 95–112°, 0.70–0.82, value ≥ 0.46 | dark bushes, middle leaves | rough 0.85, low spec |
| `m040_leaf_lit` | `#7FC43A` (lit `#86D23E`, `#89D235`, `#78B82D`) | 88–95°, 0.70–0.78 | dark bushes' top tier at 40 % | rough 0.85, low spec |
| `m040_leaf_deep` | `#1E4F12` (shade `#16430B`–`#1A460B` lifted one step) | 105–115°, ≥ 0.75 | dark bushes' lower/inner leaves at 40 % | rough 0.85, low spec |
| `m040_leaf_light` | `#ACC705` (lime bushes `#AAC602`, `#AEC807`; swatch Foliage Light `#B5C517`) | 66–70°, ≥ 0.95, G > R > B | lime bushes and sprigs | rough 0.85, low spec |
| `m040_trunk` | `#653416` (trunks `#5E3813`, `#6A2E12`; swatch Dirt `#9A6846`) | 20–30°, 0.75–0.83 | trunks, soil specks at bush roots | rough 0.95 |
| `m040_connector` | `#938C8F` (plate `#918A8E`–`#958D90`) | sat ≤ 0.06, \|R − B\| ≤ 6, R ≥ G | plate and tabs | rough 0.7, metal 0 |

**Calibration warnings:**
- **Rock:** calibrate `m040_rock` on the parts shot's body (warm faces, i.e. the lit side) against `#CCAD9D`; then check
  the front_sheet rock median within 12 of `#BEA59B` and the f34_sheet within 12 of `#C3A598`, each with hue 15–25°, sat
  0.16–0.26, R > G > B. Our median will run warmer than the sheet's because our shade is warm grey, not blue (M032 round
  2 finding 3); a median within hue 15–25° that misses by ≤ 15 levels is a known miss, not a key error. Never push the
  shade faces blue by facing.
- **Lawn:** top-view lawn median within 12 of `#C2D512`; f34 lawn within 14 of `#D2DD14`; hue 62–68°, sat ≥ 0.88.
- **Leaves:** dark bushes' median within 14 of `#357823`, hue 100–115°; lime bushes within 14 of `#AAC602`, hue 66–72°.
  Keep the two types clearly apart (hue gap ≥ 30°).
- **Connector:** median within 8 of `#938C8F`, sat ≤ 0.07; it must read grey beside the warm rock, not lilac.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Rock** (on the original facets, before any refine): `rock` base; `rock_light` by height (faces with centre z above
  0.65 × 9.2 on the columns, rising to 40 % at the top) and on the lip rim (45 %); `rock_deep` by a noise field
  (scale ≈ 0.2) below 1.5 studs (15 %); per-column and per-boulder tint ±0.04 so neighbours separate.
- **Lawn:** `grass` base; `grass_light` by a noise field (scale ≈ 0.25) at 25 %; `grass_deep` by distance to bush roots
  and lawn boulders (< 0.8) and on the drip tips.
- **Leaves:** by role in the bush (top tier `leaf_lit` 40 %, middle `leaf`, lower/inner `leaf_deep` 40 %); lime bushes
  `leaf_light` with ±0.04 tint per plant.
- **Hard edges only** where materials meet: lawn | rim (the turf edge), leaf | trunk, rock | connector (separate shells).

### 5.6 Texture (Tint) and finish

- **Tint:** rock amp 0.04, scale 0.3, per original facet (a refined facet keeps one tone); lawn 0.04, scale 0.4; leaves
  0.04; connector 0.02; trunks none. Never per-triangle confetti.
- **Finish:** rock rough 0.9, metal 0; lawn and leaves `low_spec=True`, rough 0.85; connector rough 0.7; trunk 0.95. No
  emission anywhere.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Rock:** front_sheet median within 12 of `#BEA59B`, f34_sheet within 12 of `#C3A598`; parts-shot body warm median
  within 10 of `#CCAD9D`; all R > G > B, hue 15–25°. Side and rear medians too (mauve guard).
- **Lawn / bushes / connector** per §5.4 warnings. **Shares** per §2.4.

## 6. Joins and contact

- **Columns and core:** the columns' back corners sink 0.3–0.6 into the core; neighbouring columns touch along their
  creases (overlap ≤ 0.2); everything floor-cut flat at z 0. Each rock its own closed shell or the body unioned into one
  closed shell (decision §8.5); no exact booleans at the display slot (STAGES "Booleans").
- **Lip on the body:** the rim's bottom at 9.2 sits on the column tops (sink 0.03, never coplanar); the lip's outline
  covers every column top (§2.5 capping); the front rim 0.1–0.3 proud of the column fronts; no gap between rim and
  column at the joint line (the junction close-up).
- **Shards and foot boulders:** lean into the face, sinking 0.1–0.3 into the columns; floor-cut at z 0; no rock standing
  on a point or floating.
- **Connector:** its outer face exactly on x = 8.0, its inner face at 7.6; the core and C5 stop at x ≤ 7.6 in its span
  (or overlap it, hidden, never coplanar); front tabs may sink into C5's end; back tabs stand 0.35 behind the back plane.
- **Plants:** roots on the turf (z 10.4, sink 0.03) or the ground / a rock (`K.top_at`, `K.conform`); leaves may touch
  rock but cut no more than 0.05 into it; the boulder-top bush conformed onto Bb.
- **Seams:** every rock vertex within x −8.0 … +8.0; the core's and the lip's end faces planar on the seam planes
  (§2.1); foliage overhang symmetric.

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** sunlit rock, lawn and bushes; a grey plate. No glow, light, sparkle, water, dust, particles or
VFX callout.

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight.**
- **Studio notes (Requires Manual Validation):** the rock stays warm peach-grey (not lilac) under the game's sun; the
  column facets read as separate planes (flat shading kept); the lawn stays yellow-lime; the plate reads as neutral
  grey; a run of three tiles shows no seam gap or lawn step in Studio at the 16-stud pitch.

### 7.2 Stage 6 (VFX): skip, and record why

- Kinds in `art/blender/lib/vfx.py` (frozen for modellers) include `dust`, `water_foam`, `waterfall_mist`, etc.; **none is
  shown or implied**. Record "Stage 6 skipped: the sheet shows no effect".
- **Not recommended:** `dust` at the foot, pollen motes, falling-pebble sockets.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by searching `art/blender/kit/mcp/*.py`, `art/blender/scripts/*.py`, every
`art/roblox/kit/*/manifest.json`, and every sheet / kit / wip `.blend` (zstd-decompressed) with the M035 study's
`blendall.py`:
- **W02:** `CliffWall`, `CliffWallBody`, `CliffWallGrassTop`, `CliffWallBackConnector`, `CliffWallStraight`,
  `CliffWallInnerCorner`, `CliffWallOuterCorner`; `WaterfallCliff`, `WaterfallCliffTop`, `WaterfallCliffWallA/B/C`;
  `CliffSection`; keys `w02_*`.
- **07 terrain kit:** `CliffOuterCorner`, `CliffInnerCorner`.
- `M.mk` would silently rename a clash to `<name>M040`, so avoid all of these.

**Proposed names.** None of `StoneCliff`, `StoneCliffBody`, `StoneCliffGrassLip`, `StoneCliffBackConnector` or `m040_`
occurs in the repo text, the manifests or any `.blend` (also checked free: `CliffChunk`, `CliffModule`, `ColumnCliff`,
`PalisadeCliff`, `CliffPanel`, `CliffTile`, `ModularCliff`, `CliffBlock`). "Stone cliff" parallels M039's `StoneSpire` and
keeps W02's `CliffWall*` untouched.

| Object | Part | Why |
| --- | --- | --- |
| `StoneCliff` | hero: body + lip + connector + foot dressing | W02 owns `CliffWall` |
| `StoneCliffBody` | "2. Cliff Wall Body": core, columns, shards, foot boulders, no plants | W02 owns `CliffWallBody` |
| `StoneCliffGrassLip` | "1. Grass Top Lip": slab + rim + lawn dressing | the sheet's name; W02 owns `CliffWallGrassTop` |
| `StoneCliffBackConnector` | "3. Flat Back Connector": plate + 6 tabs | W02 owns `CliffWallBackConnector` |

- Palette keys `m040_*` (§5.4). Collection `Kit/M040 Cliff Wall`.
- Collision tags (recommended, from W02's precedent): hero `"precise"` (the lawn is walkable, the face blocks);
  `StoneCliffBody` `"hull"`; `StoneCliffGrassLip` `"precise"`; `StoneCliffBackConnector` `"box"`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **a 16-stud tile (half the 32-stud grid), 8 deep, turf at 10.4 (M032's plateau level)**
   (recommended: grid-friendly, meets the shoreline corner at one height, face ratio within 5 % of the sheet), or a
   32-stud tile (32 × 16 × turf 20.8; a 3.8-character wall, columns 6–8 wide), or keep the sheet's ratio exactly with
   turf 9.9.
2. **Back** (§3.2): **a flat back plane (shallow facets ≤ 0.4) with the plate on the +X end; the rear and r34 cells judged
   loosely** (recommended: side cell, exploded, close-up, sheet notes and WorldModeling §12.2), or a double-faced ridge
   (columns on both long faces; breaks the plate and tiling).
3. **Plan depth** (§3.3): **8.0 (side and front cells)** (recommended), or the top cell's near-square plan (about 14
   deep; the side cell and the plate would then be off by 2×).
4. **Plate top** (§3.6): **10.05, under the turf, the lawn running over it** (recommended: an unbroken lawn in runs), or
   flush with the lawn as in the close-up (a grey strip at every seam).
5. **Body packaging:** **one hero object holding separate closed shells: the body's rocks (core, columns, shards,
   boulders) unioned into one closed rock shell, the lip one closed shell, the plate one, each leaf, trunk, pebble and
   patch its own** (recommended: the sheet's separate lip and plate, M032/M039 practice; a single body shell keeps the
   creases clean and the export light), or every rock its own shell (no booleans; more interpenetration).
6. **Body-top pockets** (§3.5): **none; flat tops** (recommended: hidden in every assembled view; booleans add crash
   risk), or two 0.6-deep pockets in the body part only.
7. **Foliage overhang at the seams** (§2.1): **≤ 0.8, symmetric** (recommended: matches the front cell's end sprigs and
   W : H; bushes merge harmlessly in runs), or everything inside the tile (bbox exactly 16 wide; W : H 1.19 against 1.358).
8. **Exports:** **the hero plus 3 parts** (`StoneCliffBody`, `StoneCliffGrassLip`, `StoneCliffBackConnector`)
   (recommended: the sheet's three numbered parts).
9. **Stage 5/6:** **no emission, light or VFX** (recommended: the sheet shows none).
10. **Comparison cameras** (recommended, §3): `front_sheet (0, 12)` (probe 8 / 12 / 16) and `f34_sheet (−10, 16)` (probe
    az −5 / −10 / −15 × e 12 / 16 / 22) governing; kit `side (90, 10)`; `rear_sheet (180, 12)`, `r34_sheet (150, 16)` and
    the kit top loosely; extras: the parts shot (−20, 22), the lip underside (e −30), `junc_cu (−20, 25)`, `conn_cu (35,
    18)`, the **three-tile tiling shot** and a scale shot with a 5.5-stud marker. Hide the floor in every `*_sheet` render.
11. **Colour:** **one warm peach-grey stone (R > G > B, hue 18–24°), lighter high and on the rim, a touch deeper low; a
    yellow-lime lawn with patches; dark-green and lime bushes as two plant types; brown trunks; a neutral grey plate**
    (recommended); never the Rock Mid or Rock Shadow swatches, nothing by facing.
12. **Collision** as listed above (recommended), or W02's exact set (GrassLip `"box"`, which would put the walkable top
    at the bush tops).
13. **Names** as proposed.

## 9. Pitfalls to avoid (lessons from recent verifier failures written as targets)

1. **A lip that doesn't cap the columns (M032 round 1, the blocker).** The lip's outline covers every column top; the
   rim sits on the tops at 9.2 with a straight joint; capping numbers in §2.5 (0 studs² of exposed column top; the rim
   0.1–0.3 proud). The lawn must not be a narrow strip or a pill shape floating over the columns; its front edge
   follows the column fronts.
2. **Rock dominating the share / too little green.** f34 R 75.5 / G 24.2 (±4), front 78.6 / 21.3; green in the top two
   fifths 70 % and the bottom two 30 %. Five lawn bushes plus the apron, the foot bush and the end sprigs carry it.
   Equally, **no green in the middle fifth** (0 % on the sheet): no moss streaks, no vines on the face.
3. **Mauve or blue rock.** `#AFA1A0` (4°) and `#6E6F7D` (236°) are shade and light, not paint. Every rock key R > G > B,
   hue 15–26°, R − B ≥ 30. Check the side and rear medians too.
4. **Colour by facing.** The peach-lit / blue-shade split is the light. Height fields, noise patches and distances only;
   `K.check` facing correlation < 0.5 per material.
5. **Lumpy columns or soccer-ball rocks (M023, W02).** Columns are explicit 6–7-sided prisms with tall strip facets
   (h/w 3–4.5), a level flat top under the lip and dark full-height creases; no `K.hull_rock` jitter on them, no
   subdivision, no smooth shading.
6. **Egg-shaped boulders (M034).** The foot boulders are flat-topped blocks with near-vertical sides (≥ 50 % of side area
   within 20° of vertical, a top facet ≥ 35 % of the plan); the lawn boulders are pointed or blocky, not round.
7. **A stepped crest.** The sheet's lip line is level (.74–.78 across the front cell): every column reaches 9.2; no column
   pokes above the lawn, none stops short of the rim.
8. **Seams that don't tile.** Seam faces planar at x = ±8.0 (± 0.001); no rock past a seam; the lip front at y −4.2 and
   the turf at 10.4 at both seams; the plate on the +X end only; the three-tile shot shows no gap, overlap or lawn step.
9. **Copying the rear, r34 or top cells as true views** (§3.2, §3.3): the back is flat and the plan is 2 : 1.
10. **Bowties.** Bush hubs (10–12 leaves round a trunk) and sprig roots are where 019–021 grew bowtie vertices: each leaf
    its own closed shell, `M.fix_bowties` on every object, `nonmanifold_verts` 0.
11. **A dirt band under the turf.** This lip's edge is rock (the rim), not soil (W02 and M032 had a brown band; this sheet
    doesn't). Brown only on trunks and a few root specks.
12. **The plate as a full back wall (W02's reading).** The plate is 3.9 wide on the +X end's back half, not 16 wide on
    the back.
13. **Budget.** Foliage is about half the count; the lip part is tight (≤ 1000): move one lime bush and the lawn sprigs to
    the hero only before thinning the slab. Never thin a column below §2.5.
14. **Name clashes** with W02 `CliffWall*`, `WaterfallCliff*`, `CliffSection` and the terrain kit's `Cliff*Corner` (§8).
    Only one agent drives a Blender session at a time; no commits, pushes or exports in stage agents; don't edit
    `lib/vfx.py` or the shared helpers (frozen).

## Decisions (main session, 2026-10-29)
All recommendations are accepted.

1. **Size.** A 16 × 8 tile with the lawn top at z 10.4, the same level as M032's grass top. Tiling follows §2.1: seams at x = ±8.0, nothing rocky crossing them, a flat back plane at y = +4.0, the lip front at y −4.2 at both seams, end chamfers, and the plate on the +X end only.
2. **Back.** Flat back with shallow facets, plate at the +X end. The rear and rear three-quarter cells are judged loosely.
3. **Depth.** 8 studs.
4. **Plate top.** At 10.05, just under the turf.
5. **Packaging.** One hero object made of separate closed shells:
   - the body as one rock shell;
   - the lip and the plate as their own shells;
   - each leaf and each pebble as its own shell.

   Every shell must be manifold, with 0 bowties and no self-intersections inside a shell. **The lip must cap the columns: 0 exposed column-top area**, with the rim 0.1–0.3 in front of the column faces (M032's round-1 failure).
6. **Body tops.** Flat, with no pockets.
7. **Foliage overhang.** Up to 0.8 past the seams, the same at both ends.
8. **Exports.** Hero `StoneCliff` plus `StoneCliffBody`, `StoneCliffGrassLip` and `StoneCliffBackConnector`. If GrassLip goes over 1000 tris, one lime bush and the sprigs move to the hero only.
9. **Lighting and VFX.** None; stages 5 and 6 are recorded as skipped.
10. **Cameras.** As listed in the study. Front `(0, 12)` and front three-quarter `(−10, 16)` govern, and the three-tile tiling shot is required.
11. **Colour.**
    - Rock `#CCAD9D`: hue 18–24°, R > G > B, a little lighter high up.
    - Lawn `#C4D614`.
    - Two separate bush greens.
    - Never use the Rock Mid or Rock Shadow swatches as keys.
    - Blend by position, never by facing.
    - The middle fifth of the face stays bare rock.
12. **Collision.** Hero precise, Body hull, GrassLip precise, connector box.
13. **Names.** `StoneCliff*`, keys `m040_*`, collection `Kit/M040 Cliff Wall`.

The front three-quarter share targets in §1 are binding within ±4: rock 75.5 %, green 24.2 %.

## Stage 1 — Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m040.py`, `build()`. Background session on port 9877, work file
`art/blender/assets/kit/wip/M040.blend`. The final build ran in a freshly restarted session. Every part has its own
function:

- **`palisade()` (core and columns C1–C5).** One closed lofted solid over an explicit CCW plan outline (`FRONT` + `REST`).
  - Each column's front is an explicit prism front of 4–5 corners: a dark left face turned 35–50° toward −X, a ridge,
    a lit front face turned 10–20° toward +X, and a short face into the crease. The column's back corners are the core.
    Creases sit 0.7–1.3 behind the ridges.
  - Five rings: the foot (z −0.4); a ground ring (z 0, so the floor cut adds no cut points); two staggered mid rings
    (3.0 ± 0.75 and 6.2 ± 0.75, each vertex pushed in or out 0.14–0.3 along the outline normal, alternating sign between
    the rings; creases 0.08–0.16); the flat top at 9.2.
  - Batter: the top ring stands 0.2 behind the foot on the front, and the end chamfers lean in 0.12. −X chamfer
    (−8, −3.2) → (−7.0, −4.18); +X chamfer (7.45, −3.98) → (8, −3.35).
  - The +X end steps in to x 7.62 behind y −0.2, leaving the plate's groove.
  - Flat back y = +4.0 with 7 shallow facets (inward only; the mid rings go up to 0.3 in). No pockets (decision 6).
- **`shard()` A/B/C.** Convex hulls of a 5–6-point base (z −0.25), a mid ring bulged out 12–22 % at 38–50 % height, and
  a sharp apex leaning into the face. A's apex (−0.6, −3.65, 6.5) is in the C2/C3 crease; B is a broad 6-sided slab with
  apex (4.2, −3.95, 7.0); C's apex is (7.05, −3.95, 4.1). 18–22 tris each.
- **`block_rock()` Bb/Bs/Bf.** Hulls of a superellipse foot ring, a shoulder ring at 0.8 h (scale 0.95) and an inset top
  ring (0.68) on a plane tilted 6–9° down to the front: flat tops, near-vertical sides, never eggs. Bf is clamped inside
  x ≥ −7.93. 26–32 tris each.
- **`body_part()`.** The palisade plus Bs, Bb, Bf and A, B, C, joined by merge-0 exact unions at the world origin
  (`m033._union_fine`), then floor-cut at z 0. Result: **StoneCliffBody, one closed shell**.
- **`lip_slab()`.** One closed slab over `lip_outline()`.
  - Outline: front rim blocks (`BLOCK_X`, 1.1–1.55 long), each standing 0.13–0.22 in front of the most forward column
    point under it, with 0.28-long steps between blocks. The lip front is at y −4.2 on both seams. The +X end is on
    x 8.0 to y −0.65, then x 7.98 over the plate. Flat back y 4.0; −X end on x −8.
  - Lawn top at 10.4, flat (a CDT with a row of points 0.9 inside the front blocks).
  - Outer wall rings at 10.4, 10.1 (turf), the drip line (front only: 9.88, or 9.62 on the five drip blocks) and 9.17.
  - A flat rim bottom (an annulus 1.0–1.9 wide) at 9.17, sunk 0.03 onto the column tops, and an inner wall up to the flat
    recess at 9.5.
- **`plate()`.** The (y, z) profile extruded from x 7.6 to 8.0, top at 10.05 (decision 4).
  - The front edge has 3 tabs reaching y −0.22, at z 0.7–1.7, 4.1–5.1 and 7.8–8.8.
  - The back edge has 3 tabs reaching y 4.35, centred at 2.1, 5.2 and 8.6 (heights .21 / .52 / .86), each 1.0 tall.
  - The front-top notch is 0.32 × 0.33.
  - The tabs take the plate's 0.4 thickness; the sheet's 0.5 is not reproduced.
- **Dressing (`lawn()`, `hero_rest()`).**
  - `bush()`: a dome of broad pointed diamond leaves (8 tris each, closed), laid like shingles on a golden spiral over a
    low dome-shaped heart (20 tris, deep green). Each leaf points out and down along the dome. Dark bushes have 14
    leaves on a brown 5-sided trunk; lime bushes have 8 leaves.
  - `sprig()`: 4 steep leaves from one root.
  - Lawn: L1/L2 dark (Ø 1.7, 1.6 tall); L3, L4, L5 lime; R1 (pointed) and R2 (block) lawn boulders; 8 pebbles; 3 pale
    stepping patches; 2 corner sprigs.
  - Foot: F1 (lime, Ø 1.65); end clumps F_l (dark) and F_r (lime); bushes on the boulder tops (FB on Bb, FBs dark on
    Bs, FBf on Bf) and at the shards' feet (FA, FC, FBr); 4 sprigs; 7 pebbles; 3 jagged lime apron slabs (0.12 thick,
    tucked under the face).
- **Contact (no floating dressing).**
  - Every leaf is slid onto its bush's heart (`_touch`: the nearest vertex goes to 0.012 from the heart, then 0.03 into
    it).
  - A leaf that cuts more than 0.05 into rock is pushed out along the rock normal (never down), then slid back until it
    touches again (`_Guard.push`).
  - Hearts and trunks sit in the turf, on the ground, or 0.03 into the boulder tops. Pebbles, patches and lawn rocks sink
    0.03–0.1.
  - `contact_report()` (m035's, adapted) gives **0 floating and 0 unchained shells** on the hero and on the lip part. The
    largest gap of any shell is 0.01.
- **Camera probe (spec 3.1).** The f34 view was probed at lens ×1, ×2 and ×3 × azimuth −5, −10, −15, −20 × elevation 12,
  16, 22, scored on the top profile. Best: ×2 at (−5, 12), error 0.077; ×3 at (−5, 16), error 0.080. **`f34_sheet` is
  (−5, 16) with the 3× lens.** The other cameras: front_sheet (0, 12), side_sheet (90, 10), rear_sheet (180, 12),
  r34_sheet (150, 16), top (0, 89).

## Stage 2 — Optimisation and cleanup

| Object | Tris (limit) | Size W × D × H | Shells | Non-manifold edges / verts | Boundary / wire / loose | Zero-area / n-gons / duplicates | Normals | Smallest corner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| StoneCliff (hero) | **3202** (4000) | 17.40 × 10.55 × 11.99 | 204 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | outward | 5.04° |
| StoneCliffBody | 558 (1000) | 16.00 × 10.14 × 9.20 | **1** | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | outward | 5.04° |
| StoneCliffGrassLip | **984** (1000) | 16.00 × 8.50 × 2.82 | 64 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | outward | 5.86° |
| StoneCliffBackConnector | 116 (1000) | 0.40 × 4.57 × 10.05 | **1** | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | outward | 5.27° |

- **Hero shells.** Body rock 1 (786 tris including the unions), lip 1 (376), plate 1 (116), 20 small rocks / pebbles /
  patches, 174 leaves and hearts (1560), 4 trunks (64), 3 apron slabs (300).
- **Per-shell report (`shells_report`).** Every shell has 0 non-manifold edges and verts (**bowties 0**), 0 boundary
  edges, 0 self-intersecting face pairs and 0 inverted faces, and positive volume.
- **Body cleanup.** 6 shells merged, `_union_fine` attempt 0. Then `m016._clean_mesh`, `_force_slivers`, and the ground
  pass (`_ground_beautify`: cut points on straight underside runs dissolved, then Delaunay flips).
- **Transforms and origins.** Transforms applied; each object's origin is at its bbox bottom centre. `m040_offset` gives
  the build-frame position of the origin: hero (−0.027, −0.925, −0.001), body (0, −1.071, 0), lip (0, −0.252, 9.17),
  connector (7.8, 2.065, 0). Flat shading, no custom normals, no modifiers.
- **Lip-part budget.** It was 1112 before trimming. The slab went from 464 to 376 tris (11 blocks, coarser recess and
  annulus points), leaves are 8 tris, lawn pebbles are 3-sided prisms, and L4 plus the two lawn sprigs are hero-only
  (decision 8). It is 984 now.
- **Tile contract on the hero mesh (`seam_report`).**
  - 0 rock, lip or plate verts past x = ±8.
  - 31 verts on x = −8 and 48 on x = +8; the worst is 0.0000 off its plane.
  - Lip front at y −4.200 on both seams; turf at z 10.400 everywhere within 1 stud of each seam.
  - In the hero object the seams are at x = −7.973 and +8.027, and the back plane is at y = +4.925 (offset above).
  - The foliage overhangs both seams by 0.57–0.70.
- **Capping (`capping_report`, `proud_report`).**
  - 55 body faces have n.z > 0.5 above z 8; their **exposed area is 0.000 studs²**.
  - Every body top-ring vertex is inside the lip outline.
  - The rim stands **0.147–0.198** in front of each column's most forward front corner: C1 0.147, C2 0.166, C3 0.198,
    C4 0.198, C5 0.173.
  - Rock seen from straight above inside the tile is 10.45 studs² (≤ 25): shard and boulder tops 6.65, small rocks 3.80.
- **Rock metrics (body part).** Triangle area CV 1.15; 98.9 % of the side faces within 20° of vertical; 242 flat facets
  (merged at 3°). The five biggest front facets have h/w 3.85 / 4.30 / 4.58 / 5.78 / 6.63 (1.0–1.5 wide, 5.7–6.6 tall).

## Stage 3 — UV

`M.smart_uv` at 45°, ANGLE_BASED re-unwrap, margin 0.008, then `m012._uv_unfold`.

- All four objects: **0 overlapping pairs, 0 flipped**.
- Min island gap 0.016, border 0.008.
- Texel density min / median / max 1.0 / 1.0 / 1.0.
- Conformal stretch p95 1.000–1.026.
- Islands: hero 1071, body 68, lip 322, connector 32.

## Stage 4 — Materials, colour and texture

- **Keys** (`PALETTE`, calibrated with `K.calibrate` on the kit dome; rendered medians in brackets). Calibration renders
  are in the scratchpad `m040w/calib/`.
  - rock `#A3938B`. Calibrated `#A38C86` (206,171,156) came out at hue 12°; it was turned to 19° at the same value and
    saturation, then given 1 % less saturation in pass 2.
  - rock_light `#AD9E95` (219,194,174; 22°); rock_deep `#92837C` (19°).
  - grass `#9DAF06` (194,212,21); grass_light `#B0BA12` ("vivid" target, 218,226,35); grass_deep `#879C02` (166,188,10).
  - leaf `#336922` (57,121,34); leaf_lit `#68A038` (124,193,58); leaf_deep `#1A4611` (29,78,18); leaf_light (lime)
    `#89A203` (168,196,7).
  - trunk `#502401` (101,52,29); connector `#76737A` (145,140,142).
  - Every rock key is R > G > B with hue 19–23°. The Rock Mid and Rock Shadow swatches are not used.
- **Blending by position only.**
  - Columns (`_rock_key`): rock_light rises from z 5.98 to 40 % at the top, plus a ±0.08 noise drift; broad rock_deep
    (15 %) noise patches below z 1.5; plain rock on the hidden caps and the underside.
  - Shards: deep 10 % on their lower halves. Boulders: deep 15 % low, light 20 % on their tops.
  - Lip rim: 25–40 % toward rock_light by a noise field.
  - Lawn: grass, with 10–20 % grass_light noise patches and 20–35 % grass_deep within 0.6 of bush roots and lawn boulders.
    The turf band on the outer wall is grass; the five drip blocks are grass_deep.
  - Leaves by height on the dome: crown lit (or lime), skirt deep; hearts deep. The apron is deeper where it tucks under
    the face.
  - Hard edges only between materials: turf | rim, leaf | trunk, rock | plate.
- **Tint.** Rock 0.04 at scale 0.3 per column (column factors 0.97–1.03); shards and boulders 0.04 per piece; rim 0.04;
  lawn 0.04; leaves 0.04 per bush (± 0.04 per plant); connector 0.02. `K.check` baked shading: hero 0.27, parts 0.0
  (limit 0.5).
- **Finish.** Rock 0.9; grass and leaves 0.85, low-spec; trunk 0.95; connector 0.7. Metal 0, no emission.
- **Re-measured renders against the sheet** (`measure_views()`: the study's masks on our floor-hidden renders):

| View | W : H (sheet) | R / G / C % (sheet) | Green fifths, bottom → top (sheet) | Rock median (sheet) | Lawn median (sheet) |
| --- | --- | --- | --- | --- | --- |
| f34_sheet (−5, 16) | 1.256 (1.320) | **76.0 / 23.9** / 0 (75.5 / 24.2) | 20.3 / 7.2 / **0.0** / 22.0 / 50.5 (16.1 / 13.6 / 0 / 28.7 / 41.7) | `#BBA393` (`#C3A598`) | `#C5D71E` (`#D2DD14`) |
| front_sheet (0, 12) | 1.327 (1.358) | 79.7 / 20.3 / 0 (78.6 / 21.3) | 23.7 / 8.1 / **0.0** / 12.0 / 56.2 (24.9 / 8.5 / 0 / 23.3 / 43.4) | `#BAA292` (`#BEA59B`) | `#C1D321` (`#CDD817`) |
| side_sheet (90, 10) | 0.796 (0.672) | 44.9 / 18.2 / **36.8** (42.9 / 16.9 / 40.0) | — | `#8D7D74` | `#C7DA25` |
| rear_sheet (180, 12) | 1.338 (1.305) | 84.7 / 13.1 / 2.1 (78.0 / 21.8) | 0 / 0 / 0 / 0 / 100 | `#A8968C` (`#B79C93`) | — |
| r34_sheet (150, 16) | 1.309 (1.452) | 71.4 / 17.5 / 11.0 (78.4 / 21.3) | — | `#A8968C` (`#C1A295`) | — |
| top (0, 89) | 1.576 W : D (1.182) | 4.6 / 95.3 (29.0 / 70.6) | — | — | `#C7DA15` (`#C2D512`) |

- The dark/lime bush-mask median is `#496D16` (sheet bush mask `#447714`–`#4B7A19`).
- The front face-top line (where the rock run meets green) is .76–.79 across f .15–.85, and level (sheet .74–.78).
- Top-profile error: f34 mean 0.103, front 0.067.

## Stage 5 — Lighting: skipped

The sheet shows no glow or light (decision 9): no emissive faces, no PointLight.

Studio notes (Requires Manual Validation):
- the rock should stay warm peach-grey, not lilac, under the game sun;
- flat shading keeps the column facets as separate planes;
- the lawn stays yellow-lime and the plate neutral grey;
- a run of tiles at the 16-stud pitch shows no seam gap or lawn step.

## Stage 6 — VFX: skipped

The sheet shows no effect (decision 9). There are no sockets; `build()` checks for any.

## Modeller's notes for the verifier

- **Renders** are in `art/blender/renders/models/M040/`:
  - `M040_views.png`: the kit views, then the *_sheet shots, the parts, `part_connector_face`, `lip_underside`,
    `exploded`, `tiling_f34`, `tiling_top` and `scale`;
  - `junc_cu.png` and `conn_cu.png` (floor hidden).
- **`build()` returns** `audit`, `uv`, `materials`, `views`, `contact` and `problems` (empty in the final fresh-session
  build), plus `capping`, `proud`, `seams`, `rock_metrics` and `measure`.
- **Known misses (recorded; each comes from a decision or from the studio lighting):**
  1. **Light direction.** The kit studio's key light comes from the front-left; the sheet's comes from the front-right.
     So our columns' left faces render lit, and the +X end (the plate, the side view) is in shade: side rock `#8D7D74`,
     plate `#636065`, against the sheet's lit `#958D90`. The plate key renders `#918C8E` when lit on the dome. This is
     not painted in, because colour never follows facing.
  2. **W : H.** f34 1.256 (−0.064) and front 1.327 (−0.031). Causes: the 16 × 10.4 face (decision 1: 1.54 against the
     sheet's 1.62) and the 0.8 foliage-overhang cap (decision 7). The study predicted 1.28. The sheet's foot clumps
     stand 1.0+ past the ends and its lawn is narrower than the foot; ours keeps the full 16-wide lip for tiling.
  3. **f34 green fifths.** The second fifth is 7.2 (sheet 13.6, −6.4) and the top fifth 50.5 (41.7, +8.8): at elevation
     16 the lawn band sits wholly in the top fifth. The face-top line is level, not rising (.70 → .86) as in the sheet's
     perspective. The middle fifth is 0 % as required.
  4. **Side W : H** 0.796 against 0.672: the tile is 8 deep plus 2.2 of foot dressing and the back tabs (decision 3).
  5. **Rear, r34 and top.** Rear and r34 show the flat back plane with the plate's back tabs, not a second palisade
     (decision 2). Top W : D is 1.58 against the near-square cell (decision 3); G is 95 % because the rim sits under the
     turf and the plan is 2 : 1.
  6. **Front facets.** Of the five biggest, three are at h/w 3.85–4.58 and two at 5.8–6.6 (on 1.0-wide faces, two bands
     merge within 3°). The other facets are shorter strips.
  7. **Lip ends.** The +X lip end over the plate is at x 7.98, 0.02 inside the seam, so it is never coplanar with the
     plate. The lip's 0.03-thick bottom strip (9.17–9.2) is coplanar with the core end on both seam planes; it is the
     same stone and the next tile hides it.
  8. **Front tabs.** They sit inside the 0.3-wide groove in front of the plate (the side cell's dark edge strip). They
     read from the side, but in a run the next tile covers them.
- The lawn's broad colour patches follow its CDT triangles (1.7–2.5 studs). They are softened to 10–35 % mixes, but the
  top view still shows them faintly as large triangles.
- Nothing is committed, exported or pushed. The shared helpers are untouched, and only the collection
  `Kit/M040 Cliff Wall` in the work file was written.

## Verification round 1 (verifier, 2026-10-29)

Fresh verifier, read-only. Background Blender on port 9877 with `wip/M040_verify.blend`. Nothing was built or saved.
Every number below was re-measured with my own bmesh, BVH and ray-cast code, plus `M.audit`, `K.check` and
`m040.measure` run on my own renders. The renders and scripts are in the scratchpad `m040_verify/` (renders in
`m040_verify/r/M040/`, side-by-sides `sbs_*.png`).

### Measured

| Object | Tris (limit) | Size W × D × H | Shells | Non-manifold edges / bowtie verts / open shells | Boundary / wire / loose | Zero-area / n-gons | Self-intersecting pairs within a shell | Inverted shells | Origin | Transforms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| StoneCliff | 3202 (4000) | 17.402 × 10.549 × 11.993 | 204 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | bbox bottom centre (0, 0, 0) | applied, no modifiers, no custom normals, flat |
| StoneCliffBody | 558 (1000) | 16.000 × 10.142 × 9.200 | 1 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | ✓ | ✓ |
| StoneCliffGrassLip | 984 (1000) | 16.000 × 8.504 × 2.822 | 64 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | ✓ | ✓ |
| StoneCliffBackConnector | 116 (1000) | 0.400 × 4.570 × 10.050 | 1 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | ✓ | ✓ |

| Check | Measured | Target | OK |
| --- | --- | --- | --- |
| UV (1024 raster) | 0 overlapping px, 0 flipped, 0 zero-area, 0 outside 0–1 on all four objects | clean | ✓ |
| Floating dressing (hero, 204 shells, BVH overlap + nearest) | **0 shells > 0.03** from everything (197 touching, 5 < 0.01, 2 at 0.01–0.03); **0 unchained** (contact chain ≤ 0.03 to the ground or the body) | 0 / 0 | ✓ |
| Dressing cutting into rock (ray-parity inside test) | trunks 0.06–0.07; one leaf 0.07; bush hearts 0.14–0.31 into boulder tops (hidden under their leaves) | leaves ≤ 0.05 | ~ |
| Capping | 55 body faces with n.z > 0.5 above z 8 (121 studs²). Rays straight up: **0.000 exposed** (1650 samples). Rays toward 12 cameras (az −30 / 0 / +30 × el 12 / 16 / 25 / 40): 0.000 visible | 0 | ✓ |
| Rim proud of the column fronts (front ray at z 9.1 against z 9.3) | C1 0.150, C2 0.172, C3 0.187, C4 0.184, C5 0.165; 0 of 161 x-slices where a column is in front of the rim | 0.1–0.3 | ✓ |
| Column tops | every body vertex above z 8.5 is at z 9.200 | one level | ✓ |
| Seams (build frame) | body and lip x −8.0000 … +8.0000; **0 rock / lip / apron / pebble / plate vertices past ±8**; core −X end planar (12 verts, y −3.26 … 4.0, z 0 … 9.2), +X end planar (8 verts, y −3.45 … −0.2) | ±8, planar | ✓ |
| Lip at the seams | front y −4.2000 at both seams; lip ends z 9.17 … 10.4 on both; the turf is 10.400 everywhere within 1 stud of either seam; over the plate the lip stops at x 7.98 | −4.2, 10.4 | ✓ |
| Back | body and lip max y 4.000; facets inward to y 3.458 (0.54 deep at two mid-ring verts) | flat, ≥ 3.6 | ~ |
| Plate | one shell, x 7.6 … 8.0, y −0.22 … 4.35 (tabs), z 0 … 10.05; on +X only | +X only | ✓ |
| Foliage overhang | −X 0.728, +X 0.674 | ≤ 0.8, symmetric | ✓ |
| Rock metrics (body) | area CV 1.15; 98.9 % of side area within 20° of vertical; top-5 front facets h/w 3.85 / 4.30 / 4.58 / 5.78 / 6.63 (1.0–1.5 wide, 5.7–6.6 tall) | CV ≥ 0.6, ≥ 85 %, h/w 3–4.5 | ✓ (two facets long) |
| `K.check` | no problems. Baked shading: hero **0.27**, parts 0.0 (limit 0.5). My own area-weighted correlation of key value × Tint against the normal: rock n.z 0.03 / n.x 0.14 / n.y 0.03; grass −0.11 / −0.01 / 0.14; leaves 0.00 / 0.00 / 0.01. Leaves against height −0.41: the lime plants stand at the foot, the dark ones on the lawn, which is a per-plant choice | < 0.5, never by facing | ✓ |
| Tint | rock 0.93–1.07 (sd 0.023); grass 0.95–1.04 (sd 0.016); leaves 0.94–1.07 (sd 0.030); per facet, not per triangle | broad mottling | ✓ |
| Rock keys | every rock key R > G > B, hue 18–22°, sat 0.14–0.15. Rock Mid and Rock Shadow are not used | R > G > B, 18–24° | ✓ |
| Bush keys | dark leaf 99–108°; lime 69–75°; gap ≥ 30° | two greens kept apart | ✓ |
| Connector key | `#76737A` = (118, 115, 122): **B > R**, hue 266°, sat 0.06 | R ≥ G, \|R − B\| ≤ 6, not lilac | ~ (see m5) |
| Emission / sockets / lights | none; no children; metal 0; roughness 0.7 / 0.85 / 0.9 / 0.95 | none (decision 9) | ✓ |
| Collision tags | hero precise, Body hull, GrassLip precise, connector box | decision 12 | ✓ |
| Names / collection | `StoneCliff*`, keys `m040_*`, collection `M040 Cliff Wall` under `Kit` | decision 13 | ✓ |

**Renders** (my own, floor hidden on the `*_sheet` shots, measured with `m040.measure`; sheet values in brackets):

| View | W : H | R / G / C % | Green fifths, bottom → top | Rock median | Lawn median | Top-profile mean error |
| --- | --- | --- | --- | --- | --- | --- |
| f34_sheet (−5, 16) | 1.256 (1.320, **−0.064**) | **76.1 / 23.9** / 0 (75.5 / 24.2) ✓ | 20.3 / 7.1 / **0.0** / 22.0 / 50.5 (16.1 / 13.6 / 0 / 28.7 / 41.7) | `#BBA393` 24°, 0.21 (`#C3A598`) ✓ | `#C5D71E` (`#D2DD14`, Δ ≤ 13) ✓ | 0.103 |
| f34 at decision 10's (−10, 16) | 1.247 | 76.4 / 23.6 / 0 ✓ | 19.8 / 7.4 / 0.0 / 22.0 / 50.8 | `#BCA393` | `#C5D71E` | 0.128 |
| front_sheet (0, 12) | 1.327 (1.358) ✓ | 79.7 / 20.2 / 0 (78.6 / 21.3) ✓ | 23.7 / 8.1 / 0.0 / 12.0 / 56.2 | `#BAA292` (`#BEA59B`) ✓ | `#C1D321` (`#CDD817`) ✓ | 0.067 |
| side_sheet (90, 10) | 0.796 (0.672) | 44.9 / 18.2 / 36.9 (42.9 / 16.9 / 40.0) ✓ | — | `#8D7D74` (in shade) | `#C7DA26` | — |
| rear_sheet (180, 12) | 1.338 (1.305) | 84.7 / 13.1 / 2.1 (78.0 / 21.8) | 0 / 0 / 0 / 0 / 100 | `#A8968C` (`#B79C93`) | — | — |
| r34_sheet (150, 16) | 1.309 (1.452) | 71.4 / 17.5 / 11.0 (78.4 / 21.3) | — | `#A8968C` | — | — |
| top (0, 89) | 1.576 W : D (1.182) | 4.6 / 95.3 (29.0 / 70.6) | — | — | `#C7DA15` (`#C2D512`) ✓ | — |

Bush-mask median (f34) `#496F1C` (sheet `#447714`–`#4B7A19`) ✓. Every rock median keeps R > G > B, including the side and
rear views (no mauve).

### Seams and the `m040_offset` pivot

The hero's object frame puts the seams at x −7.973 / +8.027 and the back plane at y +4.925. The cause is that the
foliage overhang is uneven (0.728 against 0.674) and the bbox in Y runs from the foot dressing to the back tabs.

**This does not break tiling.** Copies placed 16 studs apart along X with the same rotation keep the same offset, so
their seams meet exactly. My three-tile shots (`tiling_f34`, `tiling_top`, `tiling_front`, and `seam_cu` at the +X
seam) show no gap, no overlapping rock, flush lips at one turf level and an unbroken lawn. Each seam reads as one more
column crease. The only remaining line is the planned 0.02 slot over the plate between x 7.98 and 8.0.

The offset only moves the pivot. That matters in three cases:
- snapping tiles to the 16/32-stud grid by position;
- rotating a tile about its pivot for 90° turns and corners;
- mixing the hero with the Body or Lip parts, whose bbox centres sit on the build-frame x = 0.

Roblox puts a MeshPart's origin at its bbox centre. The tile centre (build-frame origin, ground level) is therefore at
object-space **(+0.027, +0.925, −5.996) from the MeshPart centre** (Blender axes). The fix is metadata only: record
that PivotOffset in the export notes, converted to Roblox axes. Optionally, also make the foliage overhang exactly
symmetric so x = 0. No geometry change is needed.

### Findings

No blockers. Every mesh is clean, every budget is met, nothing floats, the columns are fully capped, the seam
contract holds exactly, the f34 shares are within ±4, the middle fifth is bare rock, the colour families are right,
nothing is coloured by facing, and every decision was followed.

Minor items, in priority order, each with a fix target:

- **m1 (minor, the most visible difference).** The lip reads as a separate table-top slab. A straight, uniform rock
  band about 0.9 tall (the rim at z 9.17–10.1) under a straight lime turf edge runs right across every governing view
  (`sbs_f34.png`, `sbs_front.png`). In the sheet's assembled views, the columns run up to a scalloped grass edge; the
  rim blocks show only in the junction close-up.
  - Fix target: break the band so the column creases carry on up through it. Step each rim block in or out with the
    column under it (±0.3–0.5, so the lip edge scallops like the sheet's lawn line), keeping 0.1–0.3 proud.
  - Turn the painted drip triangles into real drips: lime tongues 0.3–0.7 down over 4–5 column tops.
  - Re-run the capping and proud checks afterwards.
- **m2 (minor).** The dark bushes read as small palm or agave stars on visible trunks (`foot_left_cu.png`, the top
  of `f34_sheet`). The sheet's are round domes of broad leaves, with the trunk barely showing.
  - Fix target: add a crown tier of 4–5 leaves pitched up and out, so the outline is a dome Ø 1.9–2.1.
  - Show at most 0.2 of trunk.
  - Lime bushes are acceptable.
- **m3 (minor, part only).** The lip part's underside renders as one flat dark plane (`sbs_under.png`). The sheet shows
  blocky rim lobes ringing a recess.
  - Fix target: raise the recess to about z 9.8.
  - Facet the inner rim wall into 2–3 sloped faces, so the ring reads from e −30.
  - Do not lower anything below 9.17 over the columns.
- **m4 (minor).** The connector's front tabs sit inside the 0.3 groove and barely show (`sbs_conn.png`). The sheet's
  detail has a chunky tab standing forward of the plate edge beside the end column.
  - Fix target: bring the middle front tab out to about 0.5–0.6 in front of the plate edge, sunk into C5's end. The
    spec allows this.
- **m5 (minor).** The connector key `#76737A` is B > R (hue 266°). The stage 4 note says it was "nudged to R ≥ B", but
  it wasn't. It renders slightly violet `#636065` in the side view and `#625F63` in the r34.
  - Fix target: a key with R ≥ B ≥ G and sat ≤ 0.05, for example `#797476`.
  - The plate's dark value in the side view is the studio key light (front-left, so the +X end is in shade), not
    paint. Accepted.
- **m6 (minor).** The lawn's colour patches follow its CDT triangles (1.7–2.5 studs) and read as large triangles in the
  top view (`top_sheet.png`).
  - Fix target: either cut the patch contrast to ≤ 10 % mixes, or give the hero's lawn a finer CDT (spacing about 0.9)
    so the patches blend in 3 steps.
  - The lip part is at 984 tris, so do the finer CDT on the hero only.
- **m7 (minor).** Shard A (in the C2/C3 crease) is a thin sliver that barely separates from the column facets. All
  three shards are fused, flush-coloured rock, so they read weaker than the sheet's.
  - Fix target: widen A's base to the planned 1.4 and stand it 0.3 further proud.
  - Optionally give each shard its own per-piece tint of +0.03 (position or piece, never facing).
- **m8 (minor, accepted, decision-driven).** These come from decisions 1, 3 and 7 and from the sheet's perspective:
  - f34 W : H is 1.256, 0.064 under (just outside ±0.06).
  - f34 green fifth 5 is 50.5 (+8.8) and fifth 2 is 7.1 (−6.5).
  - Side W : H is 0.796 against 0.672. The spec's own §2.4 extents (Y 10.35 against H 12.3) predict about 0.84, so the
    §2.4 range 0.62–0.74 could never be met.
  - Top G is 95 % against 70.6, because the rim is under the turf on a 2 : 1 plan.
  - None needs a change.
- **m9 (minor, accepted).**
  - Two front facets have h/w 5.78 and 6.63 (target 3–4.5). They are still clean strips about 1 wide.
  - The back facets go 0.54 deep at two vertices (target ≤ 0.4).
  - One leaf sits 0.07 into rock (≤ 0.05).
  - All three are harmless.
- **m10 (minor).** "A little lighter high up" is very faint. rock_light is only 10 levels above rock, and at a 40 % mix
  that gives about +4. The upper-third lift barely shows.
  - Fix target, optional: make rock_light about +18 levels over rock (hue 20–22°, R > G > B), at the same 40 % by
    height.
- **m11 (export note).** Record the PivotOffset from the section above.

Modeller's listed leftovers, judged:
- f34 W : H −0.064: accepted (m8).
- Green by fifths: accepted. The middle fifth is 0.0 as required, the binding shares pass, and the top-fifth excess
  comes from the level lip at e 16.
- Side W : H: accepted (m8).
- Two facets over the h/w target: accepted (m9).
- Lawn triangles: real, but cosmetic (m6).
- The f34 camera at (−5, 16) instead of decision 10's (−10, 16): accepted. The decision kept the study's probe, and at
  (−10, 16) the shares are 76.4 / 23.6, still inside ±4.

### Score and verdict

**7 / 10. PASS.** The technical side is excellent: clean shells, 0 floating dressing, 0 exposed column top, an exact
seam contract and a seamless three-tile run. The governing shares and colour families match, and every decision was
followed.

The shape differs from the sheet in character, not in kind:
- the straight rim band and the straight lawn edge (m1);
- the palm-like dark bushes (m2);
- the flat lip underside (m3);
- the hidden front tabs (m4).

None is a blocker. m1 and m2 are worth a targeted pass if a second round is run.

## Main session ruling (2026-10-29)
- **Verdict:** passed in round 1 (7/10) and committed.
- **Main-session tweak (m5):** the connector key moved from `#76737A` (B > R) to `#797476`. I rebuilt in the GUI kit; tris and shells are unchanged.
- **Pivot:** the `m040_offset` pivot doesn't affect tiling at a 16-stud pitch. Record the PivotOffset in the export notes before the tiles are used for grid snapping or corner rotation.
- **Left for a later polish pass:**
  - The lip reads as a table-top slab. Target: step the rim blocks per column, and make the drips real geometry.
  - The dark bushes read as palm or agave stars on visible trunks. Target: add a crown tier, and show at most 0.2 of trunk.
  - The lip part's underside is flat.
  - The front tabs are hidden in the groove.
  - The lawn patches show as big triangles in the top view.
  - Shard A is a weak sliver.
  - The rock_light patches are faint.
- **Export:** 4 assets, 4 solid pieces, 4860 tris, 0 VFX sockets, palette 25 colours, 0 problems.
