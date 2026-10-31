# 062 Ground Scatter — spec

Reference: `art/blender/assets/references/062.png` (1024 × 1536 px). INDEX.md row 62: "Flintborn Ground Scatter Study".
The sheet's own header reads **"64 / 132"** (top left), title **"GROUND SCATTER"**, top right "FLINTBORN — INDIVIDUAL
MODEL STUDY" (our number is INDEX's 062, §3.1).
Builder: `art/blender/kit/mcp/m062.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows no effect** (§7). It is
**forest-floor dressing that will be repeated many times**, so it is budgeted as a light full asset (§4.3, decision
§8.14). It is not one plant but a **low pile of loose pieces**: two big green lobed leaves, orange / yellow / rust maple
leaves, small green leaves, two big square-section twigs crossed in an X with a small twig under them, one chunky
egg-shaped pinecone of shingled scales, two faceted warm-grey stones and a few wood chips. Every piece is a **closed
solid lying on the ground or on a neighbour** (close-up 1: "open underside, parts on the ground plane, nothing hidden"):
no ground plate, no soil disc, no floating and no buried pieces.

Sheet text (paraphrased):
- **Title block (top left):** "64 / 132", "GROUND SCATTER"; subtitle: fallen leaves, twigs, pinecones and stones.
- **"ASSEMBLED":** "FRONT 3/4" and "REAR 3/4".
- **Ortho row (no title bar text beyond the cell labels):** "FRONT", "SIDE (RIGHT)", "REAR", "TOP".
- **"EXPLODED CONSTRUCTION & PARTS":** labels "Leaf (large)", "Twig (large)" (on the crossed pair), "Twig (small)" (a
  loose short twig), "Ground Stone (large)", "Ground Stone (small)", "Pinecone"; dashed drop lines from the twig X down
  onto the assembly, dashed arrows pulling the loose leaves, chips and stones out from it.
- **"PART LIST (REUSABLE)":** Leaf (large) green, Leaf (medium) orange, Leaf (small) yellow, Leaf (variant) rust brown,
  Twig (large), Twig (small), Pinecone, Ground Stone (large), Ground Stone (small).
- **"CONSTRUCTION CLOSE-UPS":**
  1. "UNDERSIDE VIEW": a low view of a pile (three twigs, a pinecone, a stone, green / yellow / orange leaves); callout:
     the underside is open, the parts rest on the ground plane, there is no hidden geometry.
  2. "TWIG JUNCTION": two square-section sticks crossing, a dashed circle on the crossing; callout: the sticks simply
     intersect, with broad flat faces and no fancy joinery.
  3. "LEAF THICKNESS (CROSS-SECTION)": the tip of a green leaf from the side with a dimension arrow on its edge; callout:
     a thin but solid leaf slab with bevelled edges.
- **"MATERIAL PALETTE":** six unlabelled swatches in a 2 × 3 grid: green, muted yellow, orange, tan brown, an olive →
  ochre gradient, warm grey (§5.1). There are no header swatches on this sheet.
- **"MODELING NOTES":** chunky, low-poly cartoon style; broad flat-shaded faces; simple clean solid colours; reusable
  modular parts (leaves, twigs, pinecone, stones); no photoreal texture or noise; simple readable geometry; match the
  silhouette, proportions and style of the original reference.
- **Game context and the old kit:**
  - **W07 row 4 `GroundScatter`** (`art/blender/scripts/kit/W07/ground_scatter.py`; manifest `art/roblox/kit/W07/manifest.json`;
    goals `art/blender/renders/kit/W07/ground_scatter_goals.md`) is the old kit's take on this subject. Manifest hero
    **11.67 wide × 8.88 deep × 2.07 tall**, 1173 tris (budget 3500), collision `none`, no VFX; goals file says it was
    built as a ~5 × 4 × 1.3 pile with two green lobed leaves, 4–6 orange maples, 2–3 crossed twigs, one pinecone and two
    stones. `MODEL_PROGRESS.md` row 70: **"partial: twig planks dominate (ref leaves + pinecone); flat pinecone"**;
    `art/reference/kit/CHECKLIST.md` 7/10. Palette: one key per material, no shade variants (`w07_leaf #4E9A2C`,
    `w07_leaf_autumn #C0561E`, `w07_wood #7A4A2A`, `w07_stone #8E8E94`). Parts `GroundScatterLeaf`, `…LeafVariant`,
    `…Pinecone` (2.7 × 2.5 × 2.6, 240 tris), `…Stone` (hull collision), `…Twig`; variants `…LeafLitter`,
    `…TwigPatch`, `…MixedSparse`. **All `GroundScatter*` names are taken** (§8).
  - **Related:** 038 `StoneScatter*` (W01 owns `PebbleScatter*`); W05 `FallenSoftwoodLog*`; siblings 059 Grass Tuft
    (2.4 tall), 060 Broadleaf Fern (3.0), 061 Meadow Herb (2.2). §1.5 keeps 062 apart from them.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The page is pale paper
(`#F9F8F5`); each panel is cream (`#F7F4EC`); each piece has a thin white sticker halo and a soft warm-grey cast shadow
(`#DCD1C1`–`#E8DDD1`, h 30–40°, s .10–.12, v .86–.91). Measured grey rules (`lines2.py`): header rule y 94; assembled
panel y 94–455 (title bar to y 124), divider x 524; ortho title bar y 465–495, cells y 495–692, dividers x 261, 499, 756;
exploded x 11–755, y 703–1205 (title bar to y 732); part list x 761–1012, y 703–1205; close-ups x 11–751, y 1217–1521
(title bar to y 1248), dividers x 281 and ≈ 492; palette x 762–1012, y 1217–1337; notes y 1345–1521.
- **Cells** (`m.V`, `m.X`): f34 (13,140,523,454); r34 (526,140,1011,454); front (13,497,260,690); side (263,497,498,690);
  rear (501,497,755,690); top (758,497,1011,690); exploded (13,734,754,1203); parts column (763,734,900,1203); cu1
  "underside" (13,1272,280,1450); cu2 "twig junction" (283,1272,498,1450); cu3 "leaf thickness" (500,1272,750,1420).
  The assembled labels sit above y 140, so no text needs blanking.
- **Swatches** (inner boxes, sd ≤ 6 except P5): P1 (774,1257,802,1276), P2 (815,1257,843,1276), P3 (774,1283,802,1303),
  P4 (815,1283,843,1303), P5 (774,1310,802,1330, a gradient: sd 12), P6 (815,1310,843,1330).
- **Masks** (`cls()` in `m.py`, HSV, h in degrees; a 2 × 2 opening drops specks):
  - **G**, green leaves: h 60–170, s ≥ 0.30, v ≥ 0.10.
  - **Y**, yellow leaves: h 36–60, s ≥ 0.50, v ≥ 0.45.
  - **O**, orange leaves: warm (h < 36 or ≥ 345, s ≥ 0.35) with s ≥ 0.68 and v ≥ 0.70.
  - **B**, brown: the rest of warm (twigs, pinecone, chips, rust leaf, shaded orange-leaf edges) plus anything v < 0.20.
  - **S**, stone: (s < 0.13 with h < 28 or > 180, or s < 0.06) and 0.15 < v < 0.865. The cast shadow (warm, s ≥ 0.10,
    v ≥ 0.86) stays background; a few faint shadow slivers under leaves leak into S (≤ 1 point).
  - **Caveats:** the pinecone's lit scale tops (`#CD824D`, s .62) fall in B, not O; the shaded thickness bands of the
    orange leaves fall in B; the yellow leaf's amber shade sits on the Y / O border. Apply the same code to our renders
    (studio floor hidden, plain background).

**Scratch study material** (no Blender) in
`<temp>\m062_study\`.
Run with `C:/Users/Orang/.local/bin/uv.exe run --no-project --with pillow --with numpy --with scipy python <script> < /dev/null`.
- **Helpers:** `m.py` (boxes, `cls`, `clsimg`, `hsv`), `zoom.py` (`zoom.py x0 y0 x1 y1 scale out.png [grid]`), `probe2.py`
  (`probe2.py x,y …` → hex and HSV), `lines2.py` (frame rules), `sw2.py` (swatches).
- **Measurements:** `measure.py` → `measure_out.txt` (bbox, W : H, fill, class shares and extents, top profile; writes
  `cls_views.png`); `comps.py` → `comps_out.txt` (per-class blobs per view: area, bbox, centroid); `expl.py` →
  `expl_out.txt` (exploded and parts blobs: principal L, W, tone); `twig.py` → `twig_out.txt` (twig widths across the
  axis); `samp.py` → `samp_out.txt` (class medians per view and per named piece); `cone.py` (pinecone and twig value
  bands); `bsplit.py` (brown split: pinecone vs the rest); `p5.py` (where the P4 and P5 swatch colours occur);
  `names.py` (manifest name search).
- **Zooms:** `z_f34.png`, `z_r34.png` (2×, gridded), `z_front.png`, `z_side.png`, `z_rear.png`, `z_top.png` (3×,
  gridded), `z_f34_mid.png`, `z_f34_left.png`, `z_cone_f34.png`, `z_cone_part.png`, `z_cone_expl.png`, `z_expl.png`,
  `z_parts.png`, `z_cu.png`, `z_cu1.png`, `z_cu2.png`, `z_cu3.png`, `z_pal.png`; class map `cls_views.png`.
- **On our renders:** copy 059's or 061's `meas.py`, point it at this folder's `m.py` and use `cls()`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** a repeated ground-dressing cluster of ~22 loose pieces: a light full asset (decision §8.14).
  **Budget: hero ceiling 2200 tris, plan about 1550–1850; every part under 1000 (pinecone part ≤ 600).** The old W07
  hero used 1173 of 3500 with flat one-key slabs and a flat pinecone; a shingled pinecone and bevelled leaves cost the
  difference.
- **Overall read (check this first).** A **low, broad pile about 4.4 wide, 3.6 deep and 1.1 tall** (seen from the front
  at the sheet's elevation it is 1.7–1.9 × as wide as tall):
  - **two big bright-green lobed leaves** (back-left and front-right), the biggest pieces in the pile;
  - **a big orange maple leaf at the front-left**, a smaller orange maple propped up at the back, a rust-brown maple
    under the twigs on the right, two small yellow maples tucked behind the stones, three small green leaves round the
    rim (one pale lime at the front centre);
  - **one long square-section twig** lying diagonally from back-left to front-right, and **a second twig crossing over
    it** in an X, its upper end lifted to be the highest point of the pile; a small twig lies under them;
  - **one chunky egg-shaped pinecone** standing at the front of the twig X (its scales lit tan-orange, dark gaps);
  - **a large faceted warm-grey stone at the back-right** and **a smaller one at the left**;
  - **four small wood chips and fragments** scattered at the front.
  - It reads **green / brown first, then orange and grey**: front G 38.8 %, B 38.6 (pinecone 11.2, twigs and the rest
    27.4), O 11.0, S 10.4, Y 1.3.
- **Focal silhouettes, in order:**
  1. The twig X: two chunky brown beams, one lifted, crossing above the pile (the top of every front view).
  2. The pinecone: a round scaly egg in front of the X (the pile's tallest solid lump after the lifted twig).
  3. The big lobed leaves: broad green stars lying flat, front-right and back-left; the orange maple front-left.
  4. The grey stones at back-right and left, the small leaves and chips round the rim.
- **Target size: 4.4 wide (X) × 3.6 deep (Y) × 1.1 tall** (the top of the lifted twig end) (decision §8.1). Tolerances:
  width ±0.25, depth ±0.25, height ±0.10. Pinecone **Ø 0.95, 0.98 tall**.
  - **How it was derived.** No piece has a known real size, so the plan was fixed on a readable pinecone (Ø 0.95: 0.17 C,
    shin height) and the rest scaled from the sheet's ratios:
    - pinecone width / pile width: f34 107 / 484 = 0.22, front 49 / 224 = 0.22, top 48 / 196 = 0.245 → pile 4.3–4.4 at
      Ø 0.95 (110 px / stud in the f34, 51 in the front, 44.5 in the top);
    - top cell W : D 1.21 (196 × 162 px, a high oblique; §3.2) → depth ≈ 3.6–3.7;
    - pile height from the twig geometry (§2.3): the lifted twig crosses the long one about a third of the way up its
      length and rises at 25–30°, putting its top at about 1.05–1.1.
  - **Why this size.**
    - Against the 5.5-stud character: **0.81 C wide, 0.20 C tall** — a knee-low litter patch the player walks through.
      The big leaves (1.85 across, 0.34 C) and the pinecone (0.17 C) stay readable at gameplay distance (WorldModeling §18
      "tiny details vanish").
    - It sits **under all the siblings**: 059 Grass Tuft 2.4, 060 Fern 3.0, 061 Meadow Herb 2.2 tall. A tuft or herb set
      beside it stands twice as tall; the herb's daisy heads (Ø 1.1) and our pinecone (Ø 0.95) are the same chunky order,
      so the kit keeps one scale language.
    - The old W07 goals asked ~5 × 4 × ≤ 1.4 with a 1.3-tall pinecone; its manifest exported 11.7 × 8.9 × 2.1, a giant
      pile. Ours is a little smaller than the goals and a third of the manifest.
    - At 3.6 wide the twigs drop to 0.20 thick and the small leaves to 0.5 (thin at distance); at 5.0 the pinecone (1.1)
      starts to rival the herb.
- **Build frame:** front −Y, +X right, ground z 0. Lay out in the frame of §2 (the pinecone base centre at (−0.25, −0.45)),
  then put the origin at the bbox bottom centre and record its offset from the frame origin (expected (−0.07, −0.05)).

### 1.2 Measured views (`measure.py`, `comps.py`, `bsplit.py`)

| View (box) | Silhouette bbox (px) | W : H | fill | G | Y | O | B | S |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Front three-quarter** (13,140,523,454) | 25–508 × 151–431 (484 × 281) | **1.722** | 0.593 | **37.0** | 2.0 | 11.2 | 38.2 | 11.6 |
| Rear three-quarter (526,140,1011,454) | 538–995 × 178–430 (458 × 253) | 1.810 | 0.570 | 19.0 | 3.4 | 16.7 | 42.9 | 17.9 |
| **Front** (13,497,260,690) | 25–248 × 542–660 (224 × 119) | **1.882** | **0.598** | **38.8** | **1.3** | **11.0** | **38.6** | **10.4** |
| Side (263,497,498,690) | 279–482 × 554–653 (204 × 100) | 2.040 | 0.505 | 15.3 | 6.1 | 8.1 | 53.6 | 16.9 |
| Rear (501,497,755,690) | 511–741 × 548–662 (231 × 115) | 2.009 | 0.554 | 21.4 | 3.7 | 15.3 | 42.2 | 17.4 |
| **Top** (758,497,1011,690) | 789–984 × 514–675 (196 × 162) | W : D 1.210 | 0.641 | 38.1 | 1.0 | 15.9 | 34.7 | 10.3 |

- Shares are % of the silhouette (background, halo and cast shadow excluded). **Fill** = silhouette / bbox area.
- **Brown split** (pinecone disc vs the rest): f34 10.4 + 27.8; front 11.2 + 27.4; top 8.6 + 26.1. The twigs are about
  20 % of the front, the chips, rust leaf, small twig and orange-leaf edges the other 7–8.
- **f34, front and top share one composition** (§1.3, §3.3); the rear, r34 and side are redrawn compositions (§3.4).
- **Verifier tolerance** (front, f34, top): G ±5, O ±4, B ±6, S ±3, Y ±1.5 points; fill ±0.05; W : H ±0.10 at the
  probed camera; piece centroids ±0.05 of W / H (table below).

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.1 W):

| f | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .32 | .61 | .76 | .75 | .85 | .85 | .81 | **.99** | .82 | .67 | .46 |
| **Front** | .32 | .58 | .73 | .73 | .81 | .86 | **.91** | .81 | .83 | .67 | .44 |
| Top | .40 | .90 | .88 | .98 | .92 | .99 | .90 | .97 | .86 | .80 | .45 |

- Reading (front): the low rim leaves at the ends (.32 / .44); L2 and the yellow leaf at f .1–.2; the pinecone and the
  back orange leaf at f .4–.5; **the lifted twig end at f .6–.7 is the top**; the big stone at f .8.

**Piece centroids** (fraction of the bbox: x from the left, h from the bottom; `comps.py`):

| Piece | f34 (x, h) | Front (x, h) | Top (x, h) | Plan (§2), studs |
| --- | --- | --- | --- | --- |
| Pinecone P | (.51, .45) | (.48, .45) | (.44, .48) | base (−0.25, −0.45) |
| L1 big green, front-right | (.78, .26) | (.78, .26) | (.73, .24) | (+1.00, −0.95) |
| L2 big green, back-left | (.32, .62) | (.29, .60) | (.22, .72) | (−1.20, +0.75) |
| O1 orange maple, front-left | (.27, .17) | (.28, .18) | (.21, .23) | (−1.25, −1.00) |
| O2 orange maple, back (propped) | (.55, .82) | (.49, .81) | (.51, .91) | base (0.00, +1.65) |
| S1 stone large, back-right | (.80, .72) | (.77, .73) | (.79, .75) | (+1.25, +0.85) |
| S2 stone small, left | (.22, .41) | (.21, .40) | (.14, .51) | (−1.60, −0.05) |
| G1 small pale leaf, front-centre | (.52, .10) | (.51, .09) | (.44, .10) | (−0.20, −1.50) |
| G2 small leaf, far-left | (.08, .34) | (.07, .32) | (.05, .43) | (−1.95, −0.30) |
| G3 small leaf, right | (.92, .62) | (.90, .61) | (.90, .60) | (+1.80, +0.35) |
| Y1 yellow, behind S2 | (.15, .55) | (.13, .55) | (.04, .58) | (−1.85, +0.40) |
| T2 lifted twig end (top) | (.74, 1.0) | (.66, 1.0) | (.70, .94) | (+0.92, +1.62), top z 1.08 |
| T1 front-right end | (.98, .41) | (.99, .40) | (.98, .40) | (+2.05, −0.30) |
| T1 back-left end | (.36, .88) | (.32, .84) | (.29, .99) | (−0.95, +1.62) |

- The three views agree within 0.03–0.08 on every piece: they are one composition at three elevations. The top is
  slightly narrower in x for the left-hand pieces (its x scale is 0.87 of the front's).

**Sizes** (studs at 110 px / stud f34, 51 front, 44.5 top; projected, so depth is foreshortened):

| Piece | f34 | Front | Top | Exploded / parts | Adopted |
| --- | --- | --- | --- | --- | --- |
| L1 leaf (large) | 202 × 135 px → 1.84 wide | 94 × 59 → 1.84 | 75 × 77 → 1.69 × 1.84 | exploded 193 × 113 (L : W 1.71, petiole incl.) | **1.85 across the lobes, 1.65 base → tip + petiole 0.40** |
| L2 leaf (large) | 128 × 104 (partly hidden) | 58 × 43 | 69 × 65 → 1.55 × 1.56 | | **0.88 × L1 (1.63 across)** |
| O1 leaf (medium) | 146 × 73 → 1.33 | 61 × 34 → 1.20 | 65 × 58 → 1.46 × 1.39 | exploded 130 × 84 (L : W 1.55) | **1.45 across + petiole 0.35** |
| O2 (medium, propped) | 67 × 47 (partly hidden) | 27 × 15 | 34 × 32 | | **0.72 × O1 (1.05 across)** |
| Y1 / Y2 leaf (small) | 52 × 38 (half hidden) | | | exploded 112 × 93 (L : W 1.20) | **0.80 across + petiole 0.22** |
| V1 leaf (variant) | ~95 × 50 under the twigs | | ~44 × 43 | parts L : W 1.54 | **1.20 across** |
| G1 / G2 / G3 small green | 73 × 48 / 75 × 41 / 55 × 40 | 33 × 19 / 33 × 17 / 28 × 18 | 31 × 29 / 19 × 16 / 25 × 22 | exploded 76 × 63 | **0.70 / 0.70 / 0.60 across** |
| Pinecone | 107 × 105 | 49 × 49 | 48 × 50 | exploded 100 × 90; parts ≈ 53 × 55 | **Ø 0.95 (at 0.6 H), 0.98 tall** |
| S1 stone (large) | 93 × 61 (foot hidden) | 49 × 30 | 48 × 37 → 1.08 × 0.89 | exploded 112 × 82 → H ≈ 0.69 W | **1.00 × 0.85 × 0.62** |
| S2 stone (small) | 89 × 67 | 42 × 27 | 35 × 26 → 0.79 × 0.62 | exploded 80 × 56 | **0.75 × 0.62 × 0.50** |
| Twig widths (`twig.py`) | T1 30–34 px (46 at a knot), T2 30–33 | T1 13–16 px | | exploded cross 28–29, loose small twig 17.5–21; parts large 15, small 10–11 | **T1 0.25, T2 0.23, T_s 0.17 square** |
| Chips | 37 × 25, 25 × 25, 25 × 25 px | | | exploded 49 × 24, 40 × 21, 43 × 26 | **0.28–0.36 × 0.15–0.17 × 0.11–0.12** |

- **Twig section.** A square beam seen from 30–40° shows its top and one side: projected width ≈ 1.39 × the side. f34
  30–33 px / 110 / 1.39 → 0.20–0.22; front 13–16 px / 51 / 1.39 → 0.19–0.23. The sheet's chunky read and the twig
  junction close-up favour the top of that range: **0.25 for the long twig, 0.23 for the crossing one**.
- **Twig length.** T1 spans X −0.95 → +2.05 (f34 305 px, front 151 px, top 142 px) and Y +1.62 → −0.30 in plan → **3.6
  long** (L : W 14). The cells show L : W 7–8 because the axis is foreshortened and the width carries the side face
  (§3.6).
- **Leaf thickness** (close-up 3 and the f34 edge bands of O1 / L1, 8–10 px at 110 px / stud seen at 30–40°): **0.08 for
  the large leaves, 0.07 medium, 0.06 small**, with a 0.02–0.025 chamfer on the top edge (the "bevelled edges").

### 1.3 Silhouette and composition per view

**Front three-quarter (`z_f34.png`) — governs the read.** A near-frontal view from about 30–40° up (§3.2), lit from the
upper left-front. Left to right:
- far left: a small lime leaf (G2) on the ground, a small amber-yellow maple (Y1) behind it, half hidden by the small
  stone S2 (a squat faceted warm-grey lump);
- behind them the big green lobed leaf L2, lying flat with its lobes toward the back-left, its back edge under the long
  twig's back end;
- front-left the big orange maple O1 (drawn redder here, `#C56138`, than in every other cell, §3.7), five pointed lobes
  with side teeth, a petiole pointing right toward the pinecone; a dark chip C1 at its back-left lobe;
- centre: the pinecone, an upright egg widest in its upper half, with shingled lozenge scales (lit tan-orange tops,
  near-black gaps), in front of the twig X; an amber leaf fragment C4 under its left foot, a tan chip C2 and a dark chip
  C3 in front of it, the pale lime leaf G1 at the front;
- behind the pinecone the twig X: T1 from the back-left down to the front-right, its cut end square and slightly
  lighter, a knot / step near its back end; T2 rising from behind the pinecone over T1 to a lifted square end up at the
  back-right — the highest point; the bright orange maple O2 propped up behind the crossing; a rust-brown leaf (V1) and a
  short twig (T_s) half hidden under T1 to the right of the pinecone; yellow glints (Y2) behind the crossing;
- right: the big green leaf L1 lying flat in front of everything, its main lobe to the front-right, its green petiole
  running up-left into the pinecone's right foot; the big stone S1 behind T1 at the back-right, a small green leaf G3 at
  its foot on the right.
- **Leaves** are flat-shaded slabs: each lobe folds along its vein into a lit and a shaded facet, the midrib and lobe
  veins showing as crease lines; a thin darker thickness band runs round every edge. **Twigs** show flat lit tops and
  darker sides in long bands with a few grain facets. **Stones** have 10–16 broad facets, lit pale tops, dark lower faces.

**Front (`z_front.png`) — governs positions.** The same composition as the f34 from a little lower (W : H 1.88 vs 1.72):
every piece within 0.03–0.06 of its f34 position. The lifted twig end is the top at f .6–.7.

**Top (`z_top.png`) — governs the plan.** Not a plan view: a high oblique (about 60–75°, §3.2) of the same
composition. It sets the depth order: L2, O2, S1 and the twig X at the back; Y1 / S2 / G2 on the left; the pinecone at
the centre; O1, G1, L1 at the front. The long twig runs from the back-left corner to the right edge; the lifted twig end
points to the back-right.

**Rear three-quarter / rear (`z_r34.png`, `z_rear.png`).** Redrawn compositions (§3.4): a big stone at the front-right,
**two pinecones** side by side, a big orange maple at the front, a big green leaf left, a yellow maple at the right, the
twig X behind. Use for content only: from behind, the pile shows a stone, the pinecone, orange and yellow maples, green
leaves and the twigs crossing above.

**Side (`z_side.png`).** Also redrawn: the pinecone at the left, a grey stone in front, a second stone behind, an orange
maple at the left and a yellow-orange maple at the right, one twig running diagonally through the pile. Content only.

**Underside (close-up 1).** A low near-ground view of a pile: three twigs (two crossing, one low at the front-left), the
pinecone, a stone, green / yellow / orange / rust leaves. It shows every piece sitting on the ground or on another piece,
with nothing below the ground and no base plate.

**Twig junction (close-up 2).** Two square-section sticks (`#8E5935`, lit tops `#BA7B4B`, shade `#533018`) crossing at
about 90° in plan; the top stick sits **down onto** the lower one (it reads slightly let in, not floating); the edges
are softly chamfered; the cut ends are flat.

**Leaf thickness (close-up 3).** The tip of a green lobed leaf seen from the side: a solid slab whose thickness is about
8–10 % of the lobe width, a chamfered top edge (a lighter lit bevel above a darker side band), lobe facets on top.

### 1.4 Parts (exploded `z_expl.png`; part list `z_parts.png`)

The exploded is drawn at about 0.93 of the f34 scale (102 px / stud: its pinecone is 100 px vs 107). The parts column
draws every part as an icon in a same-size cell (not to scale). **The hero governs size, angle and position (§3.5); the
exploded and part list govern each part's shape and colour.**

| Part (label) | Exploded box (px) | Parts box (px) | Projected L : W | Tone (median, lit) | Shape |
| --- | --- | --- | --- | --- | --- |
| Leaf (large) | (64,806,259,915) | (787,744,872,785) | 1.71 / 2.00 | `#7AAF2F`, lit `#92C136` / `#7EB130`, lit `#9CC83D` | **five pointed lobes** (a long main lobe, two side lobes at ±55–65°, two small basal lobes at ±115–125°), a tooth on each side lobe's outer edge, a **petiole** curving off the base (0.4 long), vein creases from the base to each lobe tip |
| Leaf (medium) | (38,928,159,1012) | (794,793,869,836) | 1.55 / 1.78 | `#DF742D` / `#E07630` | **maple**: five pointed lobes with 1–2 teeth each, deep sinuses, a straight petiole |
| Leaf (small) | (53,1019,171,1110) | (796,844,866,883) | 1.20 / 1.79 | `#F1BD3F` / `#F0BE40` | the same maple, rounder lobes, fewer teeth, short petiole |
| Leaf (variant) | — | (794,888,867,936) | 1.54 | `#A1542A`, lit `#B36233`, shade `#733B1E` | maple, more jagged and slightly crumpled: two lobes curl up |
| small green leaves (unlabelled) | (153,1096,228,1169) | — | 1.21 | `#70A62F` | small three-lobed ivy-like leaves, no visible petiole |
| Twig (large) | the X (256,763,475,899): long arm 233 px, short arm 186 px | (779,937,887,990) | 8.3 / 7.1 | `#91582F` / `#8E5A35`, lit `#BB8052` | **square-section beam** with chamfered edges, flat cut ends, a slight kink / knot near one end |
| Twig (small) | (481,803,572,865) | (794,986,871,1025) | 5.1 / 6.8 | `#955B32` / `#925A35` | the same, shorter and thinner |
| Pinecone | (300,1007,400,1097) | (791,1027,869,1090) | W : H 1.1 / 0.97 | body `#6E3B1D`; scale tops `#CC844F`; gaps `#260E03` | **upright egg** widest at 0.55–0.65 H, a rounded top of small scales, tapering to a narrow foot; **5 rings of broad lozenge scales** pointing down and out like shingles (6 / 8 / 8 / 8 / 6) plus a 3–4-scale cap |
| Ground Stone (large) | (545,887,657,969) | (791,1090,869,1146) | 1.39 | `#B2A8A4`, lit `#C9BFBB`, shade `#706867` | squat faceted boulder, 12–16 broad facets, a flat base, a broad sloping top |
| Ground Stone (small) | (616,986,696,1042) | (807,1158,854,1192) | 1.44 | `#9F9491` / `#A19795` | the same family, rounder, 9–12 facets |
| Chips (unlabelled) | (529,1030,578,1058), (244,1070,277,1100), (569,1087,612,1115), more round the assembly | — | 1.6–2.0 | `#895731`, lit `#C9844A` | small faceted wood blocks with chamfered corners |
| Assembly (exploded centre) | (203,900,546,1136) | — | | | the twig X (dashed drop lines from the lifted pair), the pinecone in front, a stone at the back-right and the left, green / orange leaves round it |

- **Leaf construction (all leaves):** a closed slab. Outline in the leaf's own frame (base at the origin, tip along +X):
  large 22 verts, medium 24–26, small 16–18, variant 22 (two lobes lifted), small green 9. Top face: a hub vert at the
  base + one vein vert per lobe at 0.55 R raised 0.02–0.03, so each lobe folds into two facets (the sheet's creases);
  the top face inset 0.02–0.025 from the outline with a chamfer ring down to the side band; flat bottom. A gentle cup:
  lobe tips 0.03–0.06 above the base level. Petiole: a 5-sided tapered prism Ø 0.07–0.09 → 0.05.
- **Twig construction:** an 8-sided chamfered square (0.25 side, chamfer 0.035) along a 3-station spine with a 4–8° kink
  at 0.18 L; flat cut caps, slightly skewed (5–10°) so the ends don't look sawn; a knot = one ring bulged 0.03 at the
  kink. Twig (small) uses the same function.
- **Pinecone construction:** a dark egg core (8 sides × 6 rings, Ø 0.66 at 0.6 H) carrying **36–40 separate closed
  scale plates**. Each scale: a lozenge (narrow root under the ring above, widest at 0.6 L, a blunt two-vert tip), L
  0.24–0.30, W 0.20–0.26, thickness 0.05–0.06, tilted 30–40° off the core surface with its tip down and out; rings
  staggered by half a scale; the cap scales point up and meet at the top. The scales overlap their lower neighbours'
  roots so the gaps read dark (the core) between lit scale tops.
- **Stone construction:** `K.hull_rock` / `K.pebble` (or m038's `_rock`) with a flat base, 2–3 height rings, broad
  facets; never subdivided or smoothed.

### 1.5 How 062 differs from its siblings and the old kit (binding: the verifier checks these)

| | W07 `GroundScatter` (old kit) | 038 Stone Scatter | 059 / 061 | **062 Ground Scatter** |
| --- | --- | --- | --- | --- |
| Size | 11.7 × 8.9 × 2.1 (manifest) | rocks + clover pads | 2.4 / 2.2 tall plants | **4.4 × 3.6 × 1.1, a knee-low pile** |
| Leaves | one key per colour, flat slabs, spiky stars then 3-point lobes | clover pads | blades, kites | **~10 bevelled slabs: 2 big green lobed (1.85), orange maples (1.45, 1.05 propped), rust maple (1.2), 2 yellow maples (0.8), 3 small green (0.6–0.7); lobes fold along their veins** |
| Twigs | "twig planks dominate" | none | none | **two square beams crossed in an X (3.6 × 0.25 on the ground, 1.75 × 0.23 lifted to z 1.08) + a small twig 1.2 × 0.17; twigs ≈ 20 % of the front** |
| Pinecone | "flat pinecone", 1.3 tall | none | none | **an upright egg Ø 0.95 × 0.98 of 36–40 shingled lozenge scales on a dark core; 11 % of the front** |
| Stones | one grey key | the hero | small rocks | **two faceted warm-grey stones, 1.0 and 0.75, back-right and left** |
| Base | none | slab | hub / root base | **none: every piece on the ground or a neighbour, open underside** |
| Colour | 4 keys, no shading variants | | | **greens by role and position along the leaf, orange / rust / yellow / amber maples, two browns + tan for wood, dark core + tan scales, warm grey stones with a deeper foot band** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0). Plan azimuths: 0° = +X, counter-clockwise, 90° = +Y (back),
270° = −Y (front). "Tip az" is the direction from a leaf's base (petiole end) to its main lobe tip.

### 2.1 Stack (binding contact chain, bottom up; every seat gap ≤ 0.03)

| Piece | Rests on | Contact |
| --- | --- | --- |
| Leaves L1, L2, O1, V1, Y1, Y2, G1–G3 | the ground | flat bottom at z 0.000–0.010; a cupped leaf's lowest verts on z 0; never below −0.01 |
| Stones S1, S2 | the ground (S2's back foot on Y1's front lobe) | flat base sunk 0.02; S2 within 0.03 of Y1's top |
| Pinecone P | the ground | the foot ring sunk 0.02; L1's petiole tip touches its right flank |
| Chips C1–C3, fragment C4 | the ground or the leaf under them (C1 beside O1, C4 under P's left foot) | bottom within 0.03 of the ground / leaf top |
| Twig (small) T_s | the ground and V1 | its underside on V1 (z 0.07) and the ground; its front-right end touches T1's front face |
| Twig (large) T1 | the ground (front end) and L2's back lobe (back end) | bottom z 0.00 at the front end, 0.08 at the back end (L2's thickness); a 4° bow keeps its middle 0.00–0.04 above the ground / V1 |
| Twig (large) T2 | the ground behind P (lower end) and **T1's top** at the crossing | lower end sunk ≤ 0.02 and touching P's back; at the crossing T2's underside sits 0.00–0.03 into T1's top (close-up 2's "let in"), never above it |
| O2 (propped maple) | the ground (its base edge) and T1's back-top edge | base within 0.03 of z 0; its face rests on T1's back-top edge (≤ 0.03) |

### 2.2 Leaves (10)

Each leaf is placed by its **base point**, **tip az**, a **roll** of 0 (top face up; cupping and lobe folds give the
relief) and, for O2 only, a **lean**.

| Leaf | Part | Centre (x, y) | Span (across lobes) | Tip az | Pose | Tone (§5) |
| --- | --- | --- | --- | --- | --- | --- |
| **L1** front-right | Leaf (large) | (+1.00, −0.95) | 1.85 + petiole 0.40 | 320° | flat; petiole rises 10–15° up-left onto P's right foot (tip at (+0.08, −0.38, 0.12)) | green, lime tips, deep base |
| **L2** back-left | Leaf (large) × 0.88 | (−1.20, +0.75) | 1.63 + petiole 0.35 | 150° | flat; its back lobe carries T1's back end | green, lime tips, deep base |
| **O1** front-left | Leaf (medium) | (−1.25, −1.00) | 1.45 + petiole 0.35 | 225° | flat, a gentle cup; petiole toward P (az 30°) | orange, rust base band |
| **O2** back, propped | Leaf (medium) × 0.72 | base edge at (0.00, +1.65) | 1.05 | 270° (tip toward the front) | **leans forward 33–40° onto T1's back-top edge**; its tip ends about z 0.55 | orange |
| **V1** under the twigs | Leaf (variant) | (+0.75, +0.25) | 1.20 | 20° | flat; two lobes curled up 15–20°; T1 and T_s lie across it; ~45 % hidden from the front | rust |
| **Y1** left, behind S2 | Leaf (small) | (−1.85, +0.40) | 0.80 + petiole 0.22 | 160° | flat; S2's back foot on its front lobe | yellow, amber / olive base |
| **Y2** back, under T2 | Leaf (small) | (+0.55, +1.30) | 0.80 + petiole 0.22 | 70° | flat under T2's upper half, left of S1 (visible from the rear and top) | yellow, amber / olive base |
| **G1** front-centre | small green | (−0.20, −1.50) | 0.70 | 265° | flat | pale lime, olive base |
| **G2** far-left | small green | (−1.95, −0.30) | 0.70 | 190° | flat | lime |
| **G3** right | small green | (+1.80, +0.35) | 0.60 | 30° | flat, at S1's front-right foot | green, deep base |

- **Shapes:** lobes pointed (tip angles 40–55°, never needles), sinuses at 45–55 % R (large) / 38–45 % R (maples); the
  maples' lobes carry 1–2 teeth each; small greens are 3-lobed.
- **Clearances:** no leaf more than 0.03 inside another or inside a stone / the pinecone (overlaps are stacked, not
  merged: a leaf on top of another lies on it); twigs may press ≤ 0.02 into a leaf they lie on.

### 2.3 Twigs (3)

| Twig | Part | Axis (plan, ends) | Length | Section | Heights | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| **T1** long | Twig (large) | (−0.95, +1.62) → (+2.05, −0.30) | 3.6 | 0.25 square, chamfer 0.035 | bottom 0.08 at the back end (on L2) → 0.00 at the front end; 4° bow | a knot / 6° kink at 0.18 L from the back end; the front-right cut end square to the axis ±8° |
| **T2** lifted | Twig (large), L 1.75 | lower end (+0.10, +0.30) on the ground, just behind P → upper end (+0.92, +1.62) | 1.75 | 0.23 | crosses over T1 at about (+0.39, +0.76), 0.55 (plan) from its lower end, where T1's top is z 0.29; pitch 28°; **upper end top z ≈ 1.08** | the hero's highest point; the upper cut end skewed 8° |
| **T_s** small | Twig (small) | (+0.30, +0.15) → (+1.40, −0.15) | 1.20 | 0.17 | lies on V1 and the ground | its front-right end touches T1's front face; mostly in shadow under T1 from the front |

- **Checks:** T1 passes 0.15–0.25 in front of S1's front-left flank (no contact needed); T2 clears S1's top (0.62) by
  ≥ 0.08 and passes over Y2; T2's lower end is hidden behind P in the front and f34.

### 2.4 Pinecone, stones, chips

| Piece | Part | Position | Size | Pose |
| --- | --- | --- | --- | --- |
| **P** pinecone | Pinecone | base centre (−0.25, −0.45) | Ø 0.95 at z 0.58, Ø 0.55 at the foot (z 0.06), top z 0.98 | upright, a 5° lean toward the back-right; ring phase so no scale gap lines up with the front camera |
| **S1** large stone | Ground Stone (large) | (+1.25, +0.85) | 1.00 × 0.85 × 0.62 | yaw 15°; its broad top slopes down toward the front-left |
| **S2** small stone | Ground Stone (small) | (−1.60, −0.05) | 0.75 × 0.62 × 0.50 | yaw −20° |
| **C1** dark chip | chip | (−1.85, −0.70) | 0.34 × 0.17 × 0.12 | yaw 20°, beside O1's back-left lobe |
| **C2** tan chip | chip | (−0.45, −1.05) | 0.28 × 0.16 × 0.12 | yaw −30°, on O1's right lobe / the ground |
| **C3** dark chip | chip | (+0.25, −0.95) | 0.28 × 0.15 × 0.11 | yaw 70° |
| **C4** amber fragment | chip (a broken leaf piece) | (−0.78, −0.35) | 0.36 × 0.14 × 0.06 | under P's left foot (touching, not inside) |

### 2.5 Expected extents and screen checks

- **Extents:** X −2.30 (G2's tip) … +2.15 (T1's front end), Y −1.85 (G1) … +1.75 (T1's back end, O2's base, T2's
  tip), Z 0 … 1.08 (T2). Bbox about **4.45 × 3.6 × 1.1**; bbox centre about (−0.07, −0.05) in the build frame.
- **Checks on the renders** (floor hidden; `meas.py` with this folder's `m.py`):
  - **front_sheet (0, 30)** (probe az −10 … +10, e 20–35; keep the best; §3.2) — governs positions:
    - W : H 1.80–1.95 at the kept camera (sheet 1.882); fill 0.60 ± 0.05;
    - G 38.8 ± 5, B 38.6 ± 6 (pinecone ≈ 11, the rest ≈ 27), O 11.0 ± 4, S 10.4 ± 3, Y 1.3 ± 1.5;
    - the top profile within ±0.10 for f .1–.9, the top at f .6–.7 (the lifted twig); piece centroids per §1.2 ±0.05.
  - **f34_sheet (−5, 38)** (probe az −20 … +5, e 30–45): W : H 1.65–1.80 (sheet 1.722); G 37.0 ± 5, B 38.2 ± 6,
    O 11.2 ± 4, S 11.6 ± 3, Y 2.0 ± 1.5; piece centroids per §1.2 ±0.05.
  - **top_sheet (0, 68)** (probe e 60–75): W : D 1.15–1.28 (sheet 1.210); G 38.1 ± 5, B 34.7 ± 6, O 15.9 ± 4, S 10.3 ± 3;
    the depth order of §1.3.
  - **rear_sheet (180, 30), r34_sheet (180 ± 25, 35), side_sheet (90, 30)**: content only (§3.4): from every one, the
    twig X above the pile, the pinecone, at least one stone, green and orange leaves; no piece floating against the
    background; no underside showing.

## 3. View conflicts and resolutions

### 3.1 Sheet number
- **Evidence.** The header says "64 / 132"; INDEX.md row 62 lists `062.png` as "Flintborn Ground Scatter Study".
- **Resolution.** Our number is 062 (file name, keys `m062_*`). Note the header in the export notes only.

### 3.2 Every view is drawn from above; the "top" is a high oblique
- **Evidence.** The front cell and the f34 are the same composition (piece centroids within 0.03–0.06) at slightly
  different elevations (W : H 1.88 vs 1.72); the f34's back pieces sit 0.03–0.05 W further right than the front's, a
  camera about 5° to the front-left. The "top" shows every piece's side faces and the pinecone as an upright egg: a high
  oblique of the same composition, not a plan. Leaf aspect ratios (front .67 vs top 1.04 for L1) put the front at about
  25–35° and the top at about 60–75°.
- **Resolution (decision §8.9).** `front_sheet (0, 30)` governs positions, `f34_sheet (−5, 38)` the read, `top_sheet
  (0, 68)` the plan depth; probe the ranges in §2.5 and record the kept cameras. W : H depends strongly on the
  elevation, so it is checked at the kept camera, with the centroids and shares as the main tests.

### 3.3 Front, f34 and top agree; the twig heights are inferred
- **Evidence.** The three cells agree on every piece's place; none of them shows the twigs' heights directly. The f34
  shows T2 crossing T1 about a third of the way up T2's visible length and rising to the top of the pile; the front's
  pinecone top is at h .65 and S1's top at .73 of the bbox.
- **Resolution.** Twigs as §2.3: T1 on the ground, T2 resting on T1 at 28° with its top at z 1.08. That puts, at e 30,
  the pinecone top near h .62–.67 and S1's near .70–.75 of the front bbox. If the front W : H comes out under 1.75 at
  every probed camera, lower T2's pitch (move its lower end 0.1 closer to T1), not the pinecone.

### 3.4 Rear, r34 and side are redrawn, with two pinecones
- **Evidence.** The rear and r34 put the large stone at the front-right, two pinecones side by side, a big yellow maple
  at the right; the side puts the pinecone at the image left (world front) and a stone near the camera. None of these is
  a rotation of the front / f34 / top composition. The exploded, the part list ("Pinecone", one), the f34, front, top and
  side draw **one** pinecone; the subtitle says "pinecones".
- **Resolution (decision §8.3).** **One pinecone** in the hero; the front / f34 / top composition governs, and the rear,
  r34 and side are judged for content only (§2.5). Alternative: a second, 0.75-scale pinecone at the back-left behind L2
  (about +480 tris, over the plan); or keep a two-pinecone layout for a later variant.

### 3.5 Exploded and parts scale vs the hero
- **Resolution.** The hero governs every size and position; the exploded and part list govern each part's outline
  (lobe counts, teeth, petioles, the pinecone's egg and shingles, the stones' facets, the twig section and cut ends) and
  its colour role. The exported parts are the hero's pieces at hero size (§8).

### 3.6 Twig proportions: hero L : W 14, cells 7–8
- **Evidence.** The parts icons and exploded twigs measure L : W 5–8 projected; the hero's long twig is 3.6 × 0.25.
- **Resolution.** The cells' ratio is projected: the axis runs into the depth and the width carries the side face
  (×1.39). Unprojected, the exploded long arm is about 2.6 × 0.20 (L : W 13). Keep **3.6 × 0.25 for T1** and **1.2 × 0.17
  for T_s** (L : W 7, as the small twig cells). The verifier compares the part renders with the cells from the cells'
  camera (about (−20, 35)), not by raw L : W.

### 3.7 O1 is redder in the f34 than anywhere else
- **Evidence.** The f34's front-left maple renders `#C56138` (17°); the same leaf in the top is `#E17428` (25°), the
  front `#CC6F35`, the parts "Leaf (medium)" `#E07630`, the exploded `#DF742D`. The f34's whole orange class is redder
  (`#C86A36`) than every other view's (`#DA7F26`–`#E67C2E`).
- **Resolution (decision §8.13).** O1 is a **Leaf (medium)** with the consensus orange body and its **inner 0–0.30 L
  blended to rust** (by position), which gives the f34 its redder read without a separate colour. The rust Leaf (variant)
  is V1.

### 3.8 The P5 olive gradient and the P4 tan
- **Evidence.** P5 runs olive `#7E6D1B` (left) → ochre `#98681F` (right); `p5.py` finds it only in small transition
  zones: the yellow leaves' shaded bases, a dry leaf in the side cell and the underside close-up (`#83600A`). P4 `#AC835F`
  matches the twigs' lit tops (`#B17C56`–`#BB8458` in every cell).
- **Resolution.** P5 → `m062_leaf_olive`, the base band of the yellow leaves and of the pale leaf G1 (a dry transition,
  ≤ 1 % of any view). P4 → `m062_wood_light`, the twigs' cut-end caps and the knot rim, the tan chip C2. Twig tops are
  lit, not painted (§3.10).

### 3.9 Open underside, intersecting sticks
- **Evidence.** Close-up 1: no hidden geometry, parts on the ground plane. Close-up 2: the sticks simply intersect.
- **Resolution.** No base plate, no soil patch, no hidden interior pieces: each piece is a closed solid on the ground or a
  neighbour. At the X, T2 sits 0.00–0.03 into T1's top (a contact, not a boolean, not a notch cut); STAGES' buried
  limit (≤ 0.05) holds.

### 3.10 "Solid colours, no noise" vs the user's colour rule; lighting
- **Resolution.** Leaves blended by role and position along the leaf (base → body → lobe tips); twigs one body colour
  with lighter cut caps; pinecone scales blended root → tip; stones by height in their own frame; broad Tint per piece
  (0.02–0.04), never per-triangle confetti (memory `lighting-not-paint`). The sheet is lit from the upper left-front
  (lit leaf facets and twig tops, dark twig sides and stone undersides, near-black pinecone gaps): the lighting does
  that; never paint it by facing. Render every `*_sheet` view with the studio floor hidden.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its exploded / part-list cell

1. `leaf(spec)` → one closed bevelled leaf slab from an outline kind (`large`, `maple`, `maple_small`, `variant`,
   `ivy3`), span, thickness, cup, fold depth and petiole (§1.4). Check each kind against its cell: lobe count, teeth,
   petiole, L : W, a visible thickness and bevel in `leaf_edge`.
2. `twig(spec)` → a chamfered square beam along a 3-station spine with the kink, knot and skewed caps (§1.4). Check
   against close-up 2 and the parts cells.
3. `pinecone(spec)` → the core egg and 36–40 shingle scales (§1.4). Check against the parts cell and `z_cone_f34.png`:
   egg widest at 0.55–0.65 H, rounded top, dark gaps between lit lozenge tops, 4–5 scale tips across its front.
4. `stone(spec)` → a faceted boulder (§1.4) at the two sizes. Check facet count and H : W against the exploded stones.
5. `chip(spec)` → a small 8-vert block with 1–2 chamfered corners.
6. **Hero `ForestLitter`** = the 10 leaves + 3 twigs + pinecone + 2 stones + 4 chips placed by §2, one object of closed
   shells. Place pieces bottom-up in the §2.1 order and **settle** each onto what lies under it (m038's `settle()`
   approach: drop a loose group straight down until it is 0.01 above its support), then re-run the contact report.
7. **Parts shot** (−20, 35) laid out like the part list: LeafLarge, LeafMedium, LeafSmall, LeafVariant, TwigLarge,
   TwigSmall, Pinecone, StoneLarge, StoneSmall, gaps 0.3.
8. **Exploded shot:** the twig X lifted 0.8 (T1 and T2 together), the stones pulled 0.6 out along their azimuths, the
   loose leaves and chips pulled 0.4 out, the pinecone in place.

Reusable code: `K.hull_rock` / `K.pebble` (stones), m038's `_rock`, `settle()`, `contacts()` (committed: import, don't
edit), `m047._Solids`, `shells_report`, `contact_report`, `bury_report` (committed: import). Copy, don't import, from
uncommitted builders (m057, m058, m060). The 8-azimuth ray check: copy `vis.py` from the m054 scratch folders.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a low broad pile: two big green lobed leaves, an orange maple front-left, the pinecone in front of a
   twig X whose lifted end is the top, a big grey stone at the back-right and a small one left; ~1.8 × as wide as tall
   from the front.
2. **front_sheet / f34_sheet / top_sheet** per §2.5 (shares, fill, W : H at the kept camera, profile, centroids).
3. **rear / r34 / side** per §2.5 (content).
4. **Close-up renders:**
   - `underside_cu` (0, 5) low at the front, against close-up 1: every piece on the ground or a neighbour, nothing below
     z 0, no base plate.
   - `junction_cu` close and from above (−30, 50) on the twig crossing, against close-up 2: T2 sitting into T1's top,
     chamfered edges, no gap.
   - `leaf_edge` (0, 8) close on L1's main lobe tip, against close-up 3: the slab thickness, the chamfer.
   - `cone_cu` (0, 20) close on the pinecone against `z_cone_f34.png`.
   - `thumb`: the front at about 120 px tall: the twig X, the pinecone and both big green leaves still read.
   - **`spin` contact sheet: az 0 / 45 / 90 / 135 / 180 / 225 / 270 / 315 at e 25.** In every frame the pile reads as
     leaves + twig X + pinecone + stone; leaves read as lobed slabs (never a row of slivers); the pinecone's scales read
     (never a smooth ball). Leaves lying flat are not "cards turned to a camera"; at e 25 each shows ≥ 40 % of its face.
5. **Contact counts** (§6): floating shells 0; buried 0.
6. **Hero size** per §2.5, plus a **scale shot** with a 5.5-stud marker beside the pile (the top at 0.20 of the marker)
   and 059 / 061 beside it if they are in the kit file.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Leaf (large) L1 / L2 (22-vert outline, folds, bevel, petiole) | 2 | 130–150 | 260–300 |
| Leaf (medium) O1 / O2 (24–26 verts, bevel, petiole) | 2 | 110–130 | 220–260 |
| Leaf (variant) V1 | 1 | 100–120 | 100–120 |
| Leaf (small) Y1 / Y2 (16–18 verts, small bevel) | 2 | 55–70 | 110–140 |
| Small green G1–G3 (9 verts, fold, no bevel) | 3 | 36–44 | 110–130 |
| Twigs T1 / T2 / T_s (8-sided, 3 stations, caps, knot) | 3 | 40–72 | 150–180 |
| Pinecone (core 64 + 36–40 scales × 12) | 1 | 500–545 | 500–545 |
| Stones S1 / S2 | 2 | 40–72 | 90–120 |
| Chips C1–C4 | 4 | 12 | 48 |
| **Hero** | | | **about 1590–1840; aim ≤ 1850; ceiling 2200** |
| Parts: LeafLarge / LeafMedium / LeafSmall / LeafVariant / TwigLarge / TwigSmall / Pinecone / StoneLarge / StoneSmall | | | 150 / 130 / 70 / 120 / 72 / 48 / 545 / 72 / 48 |

- **Over budget?** First drop the large leaves' bevel to the main lobes only, then the pinecone to 32 scales (4 rings of
  8 + a 4-scale cap), then the stones to 40 / 32. **Never** flatten the leaves into cards, merge the pinecone's scales
  into bumps on a ball, or drop a twig to save triangles.
- **Lean alternative** (decision §8.14): about 1300 tris with 32 scales, no bevel on the small leaves and Y2 / G3
  dropped.

### 4.4 What to do better than W07's `GroundScatter` and recent foliage

| Earlier | This one |
| --- | --- |
| W07: "twig planks dominate" | twigs ≈ 20 % of the front (0.25 square, not wide planks); the leaves (G + O + Y ≈ 51 %) and the pinecone lead |
| W07: "flat pinecone" | an upright egg Ø 0.95 × 0.98 of 36–40 tilted lozenge scales with dark gaps |
| W07: one colour per material, no shade | greens / maples / wood / stones blended by role and position (§5) |
| W07: 11.7 × 8.9 manifest (a giant pile) | 4.4 × 3.6 × 1.1, a scale shot against the 5.5 marker |
| 056 / 058: parts that don't read like their cells | each part checked against its cell from the cell's camera (§3.6) |
| 058 r1: "ground pads are bright flat stars" | leaves are bevelled slabs with folded lobes, a gentle cup and blended colour, never flat single-colour stars |
| 035 / 036 / 046: floating or buried dressing | every piece settled on the ground or a neighbour; counts reported |
| 054 / 057: parts turned to the cameras | every piece placed by gravity and contact; the spin sheet at eight azimuths |

### 4.5 Stages 2 and 3
- **Stage 2:**
  - Every shell closed and manifold, **0 bowties** (likely at leaf lobe tips, petiole roots and scale tips).
  - **0 winding errors per shell** (`bmesh.ops.recalc_face_normals` per shell, then `m047.shells_report`).
  - No zero-area faces; corners ≥ 3°; triangulate the leaf top / bottom n-gons.
  - Origin at the bottom centre, transforms applied.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box)

| Swatch | Box → hex (HSV) | Use |
| --- | --- | --- |
| P1 green | `#5C922B` (91°, .71, .57) | the big leaves' deep base / petioles (`leaf_deep`) |
| P2 muted yellow | `#ECC158` (43°, .63, .93) | yellow leaves (`leaf_yellow`; the rendered parts are more saturated, §5.2) |
| P3 orange | `#DC7810` (31°, .93, .86) | orange maples (`leaf_orange`) |
| P4 tan brown | `#AC835F` (28°, .45, .67) | twig cut caps, knot rim, tan chip (`wood_light`); also the twigs' lit tops (§3.8) |
| P5 olive → ochre | `#876A1D` (44°, .79, .53); left `#7E6D1B`, right `#98681F` | dry base bands (`leaf_olive`) |
| P6 warm grey | `#A19997` (12°, .06, .63) | stones (`stone`, `stone_deep`) |

### 5.2 Rendered regions (`samp.py`, `cone.py`; median / lit quartile / shade quartile)

| Region | Median | Lit Q | Shade Q |
| --- | --- | --- | --- |
| All green: f34 / front / top / r34 / rear / side | `#7BAF32` (85°, .71, .69) / `#7DB031` / `#7BAD2F` / `#75A82B` / `#6EA22B` / `#739829` | `#98C63D` / `#9BC83D` | `#45741A` / `#406817` |
| Big leaves L1 / L2 (f34) | `#78AD32` (86°, .71, .68) / `#7CB231` | `#96C53C` / `#92C335` | `#406D19` / `#3F6E18` |
| Small leaves G1 / G2 / G3 (f34) | `#B6C75C` (70°, .54, .78) / `#8EB839` (80°) / `#77A926` (83°) | `#C8D76C` / `#AFD14C` / `#8FBD2F` | `#728833` / `#597D21` / `#538613` |
| Leaf parts: large (parts / exploded) / small green (exploded) / cu3 | `#7EB130` / `#7AAF2F` / `#70A62F` / `#81B233` | `#9CC83D` / `#92C136` / `#92C138` / `#8EBE38` | `#4D7B1B` / `#5E8A20` |
| All orange: f34 / front / top / r34 / rear | `#C86A36` (21°) / `#CC6F35` / `#E07629` (25°) / `#E67C2E` / `#DF7A2B` | `#E68241` / `#F09031` | `#BB5A34` / `#C66A25` |
| O1 (f34 / top) / O2 (f34) / r34 front maple | `#C56138` (17°, .72, .77) / `#E17428` / `#DF7B23` (28°) / `#E87D2D` | `#E07943` / `#EF8D35` / `#EA882B` | `#BB5934` / `#DA6C24` |
| Leaf (medium) parts / exploded orange | `#E07630` (24°, .79, .88) / `#DF742D` | `#F18D39` / `#EC8633` | `#D66A27` / `#D36A2A` |
| Leaf (variant) parts / f34 rust under the twigs | `#A1542A` (21°, .74, .63) / `#613217` (shaded) | `#B36233` / `#A75A29` | `#733B1E` |
| Yellow: parts / exploded / r34 leaf / f34 Y1 (shaded, amber) | `#F0BE40` (43°, .73, .94) / `#F1BD3F` / `#F7C445` / `#D5921E` (38°, .86, .84) | `#F8CE57` / `#F8CA51` / `#FCD057` / `#E4A427` | `#C18A21` / `#CA891A` |
| Twigs: parts large / small / exploded small / cu2 / f34 T1 / f34 T2 | `#8E5A35` (25°, .63, .56) / `#925A35` / `#945A31` / `#8E5935` / `#7C4C2C` / `#996038` | `#BB8052` / `#C38653` / `#BA7B4B` / `#C98A56` | `#56321A` / `#533018` / `#3C220F` |
| Twig value bands (cu2): v < .4 / .4–.6 / .6–.75 / > .75 | `#56321A` 32 % / `#87542F` 24 % / `#A96D42` 33 % / `#CB8954` 11 % | | |
| Pinecone (f34 / parts / exploded) | `#603317` (23°, .76, .38) / `#703C1B` / `#6E3B1D` | `#D18852` / `#C17A45` / `#CC8450` | `#1F0B02` / `#2A1004` |
| Pinecone value bands (f34): v < .25 / .25–.45 / .45–.65 / > .65 | `#240E03` 21 % / `#552B13` 35 % / `#874D29` 13 % / `#CD824D` 31 % (parts: 21 / 28 / 25 / 26 %, top band `#C47B44`) | | |
| Chips: f34 C1 / C2 / C3; exploded | `#6C3E22` (23°, .69, .42) / `#CB7542` (22°, .68, .80) / `#5D371D` / `#895731` | `#AA6D42` / `#F2A05F` / `#A56B41` / `#C9844A` | |
| Stones: all f34 / front / top / r34; S1 / S2 (f34) | `#A89F9C` (15°, .07, .66) / `#B0A6A5` / `#B0A9A7` / `#A09794`; `#ACA6A5` (9°, .04, .67) / `#B5ABA8` | `#CBC5C3` / `#C5C0BF` / `#CEC9C6` | `#6C6565` / `#635F60` / `#666363` |
| Stone parts: large / small; exploded large / small | `#B1A6A1` (19°, .09, .69) / `#A19795`; `#B2A8A4` / `#9F9491` | `#CBC1BC` / `#C9BFBB` | `#6C6567` / `#706867` |
| Cast shadow (not modelled) | warm grey, h 30–40°, s .10–.12 | | |

### 5.3 How the colour works

- **Big green leaves (L1, L2):** body `leaf_green`; the base 0–0.20 R (round the petiole hub) and the petiole one step
  deeper (`leaf_deep`); the outer 0.75–1.0 R of each lobe one step lighter (`leaf_lime`). A whole radial band of the leaf
  (top facets, bevel and side band together) takes one blend step, so the lit-facet / shaded-facet contrast comes only
  from the light on the lobe folds.
- **Small green leaves:** G1 `leaf_pale` with an olive base band (0–0.25 R); G2 `leaf_lime` body with a `leaf_green`
  base; G3 `leaf_green` body with a `leaf_deep` base.
- **Orange maples (O1, O2):** body `leaf_orange`; O1's inner 0–0.30 L and its petiole blended to `leaf_rust` (§3.7); O2
  plain orange with a slightly deeper petiole (`leaf_rust`, one step).
- **Rust maple (V1):** `leaf_rust` body; the curled lobe tips one step toward `wood` (dry) by position.
- **Yellow maples (Y1, Y2):** body `leaf_yellow`; the inner 0.10–0.35 R `leaf_amber`; the petiole and base 0–0.10 R
  `leaf_olive` (P5).
- **Twigs:** `wood` along the whole beam; the cut-end caps and the knot ring `wood_light` (P4) by position (the end-grain
  role, not the facing); a 0.1 L band next to each cap blended one step. T_s the same.
- **Pinecone:** core egg `cone_core`; each scale `cone_scale` on its outer 0.45–1.0 L, blended to `cone_mid` over its
  root 0–0.45 L (where it tucks under the ring above), so the gaps read dark as on the sheet; the cap scales one step
  lighter.
- **Stones:** `stone` body; the lowest 0–0.25 H band (in each stone's own frame) blended to `stone_deep`; broad Tint
  mottling. Never colour the stone's lower faces by their facing; the shade comes from the light.
- **Chips:** C1 / C3 `wood_dark`; C2 `wood_light`; C4 `leaf_amber` (a leaf fragment).
- **Hues stay apart:** leaf_deep 88–94°, leaf_green 84–88°, leaf_lime 78–82°, leaf_pale 68–72° (s ≤ 0.58), leaf_olive
  42–50°, leaf_yellow 41–45°, leaf_amber 36–40°, leaf_orange 22–27°, leaf_rust 18–22° (v ≤ 0.66), wood 23–27° (v ≤
  0.58), wood_light 26–30° (s ≤ 0.50), wood_dark 22–25° (v ≤ 0.44), cone_scale 24–27°, cone_core 18–22° (v ≤ 0.30),
  stone 8–20° (s 0.04–0.09).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians where the sheet gives them, swatches where it doesn't. `K.sample`
kinds: `"green"` for the greens, `"vivid"` for yellow / amber / orange, `"brown"` for rust, wood and the pinecone,
`"stone"` for the stones and leaf_pale (check with `M.raw_sample` on the swatch too).

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m062_leaf_green` | big-leaf median `#78AD32` ± 12 (lit `#96C53C`) | 84–88°, 0.68–0.76 | big leaf bodies, G3 | rough 0.8, low spec |
| `m062_leaf_deep` | P1 `#5C922B` ± 12 | 88–94°, 0.68–0.75 | leaf bases, petioles | rough 0.85 |
| `m062_leaf_lime` | G2 `#8EB839` ± 12 | 78–82°, 0.66–0.74 | lobe tips, G2 | rough 0.8 |
| `m062_leaf_pale` | G1 `#B6C75C` ± 12 | 68–72°, 0.50–0.58 | G1 | rough 0.8 |
| `m062_leaf_olive` | P5 `#876A1D` ± 12 | 42–50°, 0.75–0.82 | yellow / pale leaf base bands | rough 0.85 |
| `m062_leaf_yellow` | parts small leaf `#F0BE40` ± 12 (swatch P2 `#ECC158`) | 41–45°, 0.70–0.78 | yellow bodies | rough 0.8 |
| `m062_leaf_amber` | f34 Y1 `#D5921E` ± 12 | 36–40°, 0.82–0.88 | yellow inner bands, C4 | rough 0.8 |
| `m062_leaf_orange` | parts / top / exploded `#E07630` ± 12 (swatch P3 `#DC7810`) | 22–27°, 0.76–0.84 | orange bodies | rough 0.8 |
| `m062_leaf_rust` | parts variant `#A1542A` ± 12 | 18–22°, 0.70–0.78 | V1, O1's inner band, orange petioles | rough 0.85 |
| `m062_wood` | twig parts / cu2 `#8E5A35` ± 12 | 23–27°, 0.60–0.67 | twigs | rough 0.9 |
| `m062_wood_light` | P4 `#AC835F` ± 12 | 26–30°, 0.42–0.50 | cut caps, knot ring, C2 | rough 0.9 |
| `m062_wood_dark` | f34 chip C1 `#6C3E22` ± 12 | 22–25°, 0.66–0.72 | C1, C3 | rough 0.9 |
| `m062_cone_scale` | cone top band `#C8804A` ± 15 (f34 `#CD824D`, parts `#C47B44`) | 24–27°, 0.60–0.66 | scale outer halves, cap | rough 0.75 |
| `m062_cone_mid` | cone mid band `#874D29` ± 12 | 22–25°, 0.68–0.74 | scale roots | rough 0.8 |
| `m062_cone_core` | `#4A250F` ± 12 (the dark band `#552B13`; never black) | 18–22°, 0.75–0.82 | core egg | rough 0.9 |
| `m062_stone` | S1 / parts large `#ACA6A5`–`#B1A6A1` ± 10 (swatch P6 `#A19997`) | 8–20°, 0.04–0.09, R > G ≥ B | stone bodies | rough 0.9, low spec |
| `m062_stone_deep` | exploded small stone `#9F9491` ± 10 | 10–18°, 0.07–0.10 | stone foot bands | rough 0.9 |

**Calibration warnings:**
- **The kit studio lights both halves** (042, 047, 054): calibrate to the medians, then check the shares and the
  medians on the pile's own renders. Record the lit-shade bias.
- **Greens must not lean yellow or olive** (047 "plants too yellow"): leaf_green ≥ 84°, leaf_deep ≥ 88°; only leaf_pale
  sits under 75°; the front all-green median within 15 of `#7DB031`.
- **Orange vs rust vs wood stay apart:** the orange maples bright (v ≥ 0.82), rust darker (v ≤ 0.66), the twigs browner
  and duller (s ≤ 0.67, v ≤ 0.58). The pinecone scales are tan-orange (s ≈ 0.62), never as saturated as the leaves.
- **Stones warm grey, R > G ≥ B, never lavender or blue** (059 ruling); not as dark as W07's `#8E8E94`.
- **The pinecone core dark brown, not black:** the near-black on the sheet is shadow between the scales.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Leaves:** radial bands from the petiole hub (fraction of R), by role (§5.3).
- **Twigs:** cap → 0.1 L band → body, by position along the beam.
- **Pinecone scales:** root → tip along each scale; the core one key.
- **Stones:** by height in the stone's frame.
- **Hard edges only** where materials meet: leaf | twig, scale | core, petiole | pinecone, chip | leaf.

### 5.6 Texture (Tint) and finish
- **Tint:** leaves 0.03 per leaf + 0.02 per band (so the two big greens and the two yellows differ a little); twigs
  0.03 per twig with a 0.02 lengthwise band variation (grain); pinecone scales 0.03 per scale; stones 0.04 broad
  mottling; chips 0.03. Broad, never per-triangle.
- **Finish:** everything matte: leaves 0.8–0.85, wood and core 0.9, scales 0.75, stones 0.9; low spec; no metal, no
  emission.

### 5.7 Re-measure (final renders against the sheet, same masks)
- **Green:** front median within 15 of `#7DB031`; big-leaf median within 12 of `#78AD32`.
- **Orange:** top / front O median within 15 of `#E07629` / `#CC6F35` (f34 `#C86A36`).
- **Brown:** front B median within 15 of `#77401F`; the pinecone disc's v > .65 median within 15 of `#CD824D`.
- **Stone:** front S median within 10 of `#B0A6A5`.
- **Yellow:** parts-shot small leaf within 12 of `#F0BE40`.
- **Shares** per §2.5.

## 6. Joins and contact (no floating dressing, no buried dressing)

- **Shells:** every leaf, petiole (welded to its leaf), twig, pinecone scale, the pinecone core, stone and chip is its
  own closed shell, all in one hero object.
- **Chains** (each piece must chain by contact ≤ 0.03 to the ground):
  - leaves → ground; S2 → ground (+ Y1); P core → ground; P scales → P core (each scale root 0.01–0.03 into the core,
    and the bottom-ring scales may touch the ground);
  - T1 → ground (front end) + L2 (back end); T2 → ground (lower end) + T1 (crossing); T_s → V1 + ground; O2 → ground +
    T1; chips → ground or the leaf under them; L1's petiole → L1 (welded) and P's foot (touch).
- **No floating:** no leaf, chip or scale more than 0.03 above whatever is under it; the propped O2 touches T1 along its
  face; the lifted T2 touches T1 at the crossing (the only support besides its lower end). **Count floating shells before
  reporting** (STAGES; 035 / 036 round 1): **0**.
- **No buried dressing:** no shell more than 0.05 inside a neighbour: T2 into T1 ≤ 0.03, twigs into leaves ≤ 0.02,
  scale roots into the core ≤ 0.03 beyond the seat, S2 onto Y1 ≤ 0.02, stones and the pinecone foot ≤ 0.02 below z 0.
  Use `m047._Solids` with the core, the stones and the twigs as solids, ray parity after the final settle. **Buried
  shells: 0** (scale roots and the T2 seat excepted at their stated depths).
- **Ground:** no vertex below z −0.03 (sunk feet); leaves' bottoms at z 0.000–0.010.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.
- **Reports:** reuse `m047.shells_report`, `contact_report`, `bury_report`, and m038's `contacts()` / `settle()`
  (committed; import, don't edit).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no particles, no falling leaves, no dust. The cast shadows and halos
are the illustration's.

- **Stage 5 (lighting): skip, and record why.** No emission, no lights. Studio notes (Requires Manual Validation):
  - the big leaves stay bright green and the maples orange / yellow under the game sun (not olive, not brown);
  - the stones stay warm grey (not blue-grey under a cool sky), the pinecone's scales tan-orange over a dark core.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** The old W07 hero had none either. A drifting leaf or
  dust mote would be a Studio-side ambient choice, not a socket (decision §8.11).
- **Collision:** **hero `none`** (CanCollide, CanQuery and CanTouch off): walk-through floor litter, as the old W07
  hero. Parts `none`, except **`ForestLitterStoneLarge` `hull`** if it is placed alone as an obstacle (059 precedent:
  RockLarge hull) (decision §8.8).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched all 1555 names in `art/roblox/kit/*/manifest.json` and
`art/roblox/kit/wip/*/manifest.json` (`names.py`), the builders and the repo text (`git grep`) for Scatter, Litter,
Debris, Forest, Floor, Twig, Pine, Cone, Leaf, Stone, Fallen and the candidates:
- **W07:** `GroundScatter`, `GroundScatterLeaf`, `…LeafLitter`, `…LeafVariant`, `…MixedSparse`, `…Pinecone`, `…Stone`,
  `…Twig`, `…TwigPatch`. **W01:** `PebbleScatter*`. **M038:** `StoneScatter*`. **W05:** `FallenSoftwoodLog*`,
  `FallenHollowLog`, `SoftwoodLogBranchStick`. **Other:** `GoldencrownSeedCone`, `ClassicPine*`, `OldPine*`, the
  `…Floor…` structure pieces, 110 `…Leaf…` parts.
- **`ForestLitter`, `ForestLitterLeafLarge`, `…LeafMedium`, `…LeafSmall`, `…LeafVariant`, `…TwigLarge`, `…TwigSmall`,
  `…Pinecone`, `…StoneLarge`, `…StoneSmall` and `m062` occur nowhere** (repo text, manifests, builders); no owned name is
  a substring of them and none of them is a substring of an owned name (`GroundScatterLeafLitter` contains "Litter" but
  not "ForestLitter").

| Object | Part | Why |
| --- | --- | --- |
| `ForestLitter` | hero: 10 leaves, 3 twigs, pinecone, 2 stones, 4 chips | the sheet's subject ("fallen leaves, twigs, pinecones and stones"); `GroundScatter` is W07's |
| `ForestLitterLeafLarge` | "Leaf (large)": L1 | the label |
| `ForestLitterLeafMedium` | "Leaf (medium)": O1 | the label |
| `ForestLitterLeafSmall` | "Leaf (small)": Y1 | the label |
| `ForestLitterLeafVariant` | "Leaf (variant)": V1 | the label |
| `ForestLitterTwigLarge` | "Twig (large)": T1 | the label |
| `ForestLitterTwigSmall` | "Twig (small)": T_s | the label |
| `ForestLitterPinecone` | "Pinecone": P | the label |
| `ForestLitterStoneLarge` | "Ground Stone (large)": S1 | the label (shortened: "Ground" is implied) |
| `ForestLitterStoneSmall` | "Ground Stone (small)": S2 | the label |

- Palette keys `m062_*` (§5.4). Collection `Kit/M062 Ground Scatter`. No sockets (§7).

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **4.4 × 3.6 footprint, 1.1 tall (the lifted twig), pinecone Ø 0.95** (recommended: 0.81 C × 0.20 C,
   under every sibling; big leaves 1.85, twigs 0.25 thick). Alternatives: 3.6 wide (pinecone 0.78, twigs 0.20) or 5.0
   (the old W07 goals).
2. **Names (§8):** **`ForestLitter` and the nine parts above** (recommended). Not `GroundScatter*`, `PebbleScatter*` or
   `StoneScatter*`.
3. **Pieces and counts (§2, §3.4):** **10 leaves (2 large green, 2 orange maples with one propped, 1 rust, 2 yellow, 3
   small green), 3 twigs (T1 long, T2 lifted across it, T_s small), 1 pinecone, 2 stones, 4 chips** (recommended).
   Alternative: a second pinecone at the back-left as the rear / r34 draw.
4. **Twig X (§2.3, §3.3, §3.9):** **T1 on the ground, T2 resting on T1 at 28° with its top at z 1.08, seated 0.00–0.03
   into T1's top; chamfered square sections, a knot on T1** (recommended).
5. **Pinecone (§1.4):** **an upright egg, 36–40 separate shingled lozenge scales on a dark core** (recommended), or 32
   scales if the budget needs it.
6. **Leaves (§1.4, §2.2):** **closed bevelled slabs, lobes folded along their veins, a gentle cup, petioles on the large
   / medium / small kinds; placed flat by gravity (O2 propped on T1), never turned to a camera** (recommended).
7. **Ground and base (§3.9):** **no base plate, no soil patch; open underside** (recommended).
8. **Collision (§7):** **`none` on the hero and every part except `ForestLitterStoneLarge` `hull`** (recommended), or
   `none` everywhere.
9. **Comparison cameras (§3.2):** **`front_sheet (0, 30)` positions, `f34_sheet (−5, 38)` the read, `top_sheet (0, 68)`
   the plan** (probe ranges in §2.5); rear / r34 / side content only; extras: parts shot (−20, 35), exploded,
   `underside_cu`, `junction_cu`, `leaf_edge`, `cone_cu`, `thumb`, **`spin` (eight azimuths at e 25)**, scale shot. Floor
   hidden in every `*_sheet` render.
10. **Sinking (origin):** **stones, the pinecone foot and twig ends sink at most 0.02; leaves sit at z 0.000–0.010; the
    origin at the bbox bottom centre, its offset from the build frame recorded (≈ (−0.07, −0.05))** (recommended).
11. **VFX (§7):** **none; stages 5 and 6 skipped and recorded** (recommended).
12. **Exported parts (§8):** **the hero plus the nine parts of the "PART LIST (REUSABLE)"** (recommended), each at hero
    size; no chip part and no variants (the sheet shows none).
13. **Colour (§5):** **big leaves `#78AD32` with `#5C922B` bases and `#8EB839` tips; orange `#E07630` (O1's inner band
    rust `#A1542A`); yellow `#F0BE40` with amber `#D5921E` and olive `#876A1D` bases; twigs `#8E5A35` with tan `#AC835F`
    caps; pinecone scales `#C8804A` over `#874D29` roots on a `#4A250F` core; stones `#ACA6A5` with a `#9F9491` foot**
    (recommended).
14. **Budget (§4.3):** **light full asset: hero ceiling 2200, planned 1590–1850; each part under 1000 (pinecone ≤ 600)**
    (recommended: the shingled pinecone and bevelled leaves need it). Alternative: a lean 1300 (32 scales, Y2 / G3
    dropped, no small-leaf bevel) if the litter is scattered very densely.

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **Twigs dominating (W07 "twig planks dominate").** Square 0.25 beams, not wide planks; twigs ≈ 20 % of the front, the
   leaves ≈ 50 %.
2. **A flat or smooth pinecone (W07 "flat pinecone"; WorldModeling §18 "berry bunch looks like jewels").** An upright egg
   0.98 tall; 36–40 separate scale plates with dark gaps; `cone_cu` against `z_cone_f34.png`.
3. **Flat cards or bright flat stars (WorldModeling §6.1, §17.2; 058 r1 "ground pads are bright flat stars").** Every leaf
   a closed bevelled slab 0.06–0.08 thick with lobe folds, a cup and blended colour; `leaf_edge` shows the thickness.
4. **Spiky leaves (047 r1; §18 "foliage resembles crystals or spikes").** Lobe tips 40–55°, broad lobes, sinuses at
   40–55 % R.
5. **Parts that don't read like their cells (056 / 058 blockers).** Each exported part rendered from the cell camera
   (−20, 35) beside its cell: the large leaf's five lobes and petiole, the maples' teeth, the twig's chamfered square
   and cut ends, the pinecone's egg and shingles, the stones' facet count.
6. **Floating pieces (STAGES; 035 / 036).** Settle every piece; T2 touches T1 at the crossing; O2 touches T1; chips sit on
   the ground or a leaf; floating shells 0, counted and reported.
7. **Buried pieces (046; 047 r2).** T2 into T1 ≤ 0.03; scale roots ≤ 0.03 into the core; ray parity after the final
   settle: 0 shells more than 0.05 inside.
8. **A base plate or soil disc** (close-up 1). None; nothing below z −0.03.
9. **Pieces turned toward the cameras (054 / 057).** Placed by gravity and contact; the `spin` sheet at eight azimuths.
10. **Colour by facing (042 ruling; 054 m9).** Tones by role and position; `K.check` facing correlation < 0.5 per
    material. Twig tops lit by the light, not painted.
11. **Olive or yellow greens (047), lavender stones (059 ruling), black pinecone.** leaf_green ≥ 84°; stones R > G ≥ B;
    the core `#4A250F`, not black.
12. **Orange, rust and wood merging into one brown.** Keep v and s apart per §5.4: orange v ≥ 0.82, rust v ≤ 0.66, wood
    s ≤ 0.67 and v ≤ 0.58.
13. **Winding (044) and bowties.** 0 faces wound against their neighbours per shell; lobe tips, petiole roots and scale
    tips checked for bowties; corners ≥ 3°.
14. **Oversize.** 4.4 × 3.6 × 1.1, not the old manifest's 11.7 × 8.9; a scale shot with the 5.5-stud marker.
15. **Names and scope.**
    - No `GroundScatter*`, `PebbleScatter*` or `StoneScatter*` names.
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit the frozen shared helpers or other models' builders: import from the committed ones (`m038`, `m047`,
      `m059`); copy from `m057` / `m058` / `m060` if they are still uncommitted.
    - Don't touch other models' collections.

## Decisions (main session, 2026-10-31)
All 14 recommendations are accepted. The open questions are ruled as follows:
1. **Size.** A 4.4 × 3.6 footprint, 1.1 tall, with a pinecone of Ø 0.95.
2. **Names.** Hero `ForestLitter` plus the nine parts in §8, keys `m062_*`, collection `Kit/M062 Ground Scatter`. Never `GroundScatter*`, `PebbleScatter*` or `StoneScatter*`.
3. **Counts.** 10 leaves, 3 twigs, **one pinecone**, 2 stones and 4 chips. The front, f34, top and parts row govern; the rear cells are redraws.
4. **Twig X.** As recommended. If the front W : H stays under 1.75 at every probed camera, lower the lifted twig's pitch rather than the pinecone.
5. **Pinecone.** 36–40 separate shingle scales on a dark core. Every scale touches the core or the scale above it, so **none float**.
6. **Leaves.**
   - They lie flat by gravity, with one propped on the twig, and are never turned toward a camera.
   - They are bevelled solids with thickness and folded lobes, not flat cards.
   - Each leaf touches the ground or the piece it rests on, within 0.03, and none is buried more than 0.05.
7. **Base.** No base plate and no soil patch.
8. **Collision.** `none` everywhere except `hull` on `ForestLitterStoneLarge`.
9. **Cameras.** As recommended, plus the eight-azimuth spin. Centroids and colour shares are the main tests; W : H is a soft check.
10. **Sinking.** Leaves at most 0.02 into the ground. Origin at the bbox bottom centre.
11. **VFX.** None; stages 5 and 6 skipped and recorded.
12. **Exports.** The hero plus nine parts.
13. **Colours.**
    - Use the colours as listed, by role and position, **never by facing**.
    - The front orange leaf is the standard orange with a rust inner band; the rust leaf under the twigs is the variant.
    - Stones are warm grey with R > G > B, never lavender.
14. **Budget.** Light full asset: hero ceiling 2200 (plan 1590–1850), every part under 1000, pinecone at most 600.
