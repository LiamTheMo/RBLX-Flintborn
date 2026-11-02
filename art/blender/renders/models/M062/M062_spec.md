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
`<temp>\...\scratchpad\m062_study\`.
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

## Stage 1 — Modelling (modeller, 2026-10-31)

Builder `art/blender/kit/mcp/m062.py`, `build()`; built and rendered in a background session (port 9877) on
`art/blender/assets/kit/wip/M062.blend`. Imports only committed builders (`m012`, `m033`, `m047`); nothing from
`m057`–`m061`. Scratch scripts (measurement, comparison, camera probe) are in `<temp>\...\scratchpad\m062w\`.

**Parts, each from its own function** (spec 4.1):
- `leaf_shell(kind, …)`: one closed slab per leaf. The outline is star-shaped about the petiole hub: lobes are given as
  (angle, length, half-span, flank profile), and the sinus radii lie between them. Construction:
  - flat-ish bottom (one n-gon, triangulated);
  - a vertical side band;
  - a chamfer ring (`cham` > 0) up to an inset top ring;
  - a top made of a hub vert plus one raised vein vert per lobe. Each lobe fans from its vein vert, so it folds along
    its midrib.
  The lobe flanks droop (`droop`) and the tips rise (`cup`). A vein vert is pulled toward the hub until its fan has no
  folded triangle (`bad_fans` = 0 on every leaf).
  Kinds:
  - `large` (22 outline verts, a tooth on each side lobe);
  - `maple` (24, toothed);
  - `maple_small` (16);
  - `variant` (20, `curl` lifts two lobes 16–18°);
  - `ivy3` (10, no chamfer).
  Petioles: a 5-sided tapered prism, its own closed shell, starting inside the leaf base.
- `twig_shell`: a chamfered square section (8 verts) through station centres, with flat caps skewed 5–8°, a knot ring
  (×1.13) on T1, and a 6° lateral kink at the knot.
- `pinecone`: a dark 8-sided egg core plus 56 closed scales.
  - Five rings point down and out like shingles (7 / 8 / 9 / 9 / 8).
  - A crown ring of 9 runs up the egg's surface, lifted 12° off it.
  - A 6-scale cap lies nearly flat over the top.
  - Every scale root is 0.02 inside the core.
  - Scale shape: a flat pentagon (narrow root, widest at 0.48 L, a blunt two-vert tip) under a faceted pyramid whose
    apex is at 0.56 L, lifted T: 8 tris, a chunky faceted shingle like the sheet's.
- `stone`: hull of jittered rings (m033 `_ring_pts` / `_hull`): flat base sunk 0.02, broad top sloping down toward the
  front-left.
- `chip`: hull of a jittered box with one corner chamfered (C4: a flat hexagonal leaf fragment).

**Assembly by gravity** (`hero_all`, the order of spec 2.1):
- **Base pieces.** The pinecone and stones go on the ground first.
- **Leaves.** Ground leaves follow (Y1, Y2, L1, L2, O1, V1, G1–G3). Each lies on the ground (0.006 into it) and then
  **drapes** over any leaf already under it. The drape is a dilated support height field, h(p) = max z(q) − slope·|p − q|,
  applied to the whole outline column, hub, vein verts and petiole. The slope falls from 0.45 toward 0.15 until no
  support point is more than 0.025 inside the leaf. If a leaf cuts more than 0.035 into a stone or the pinecone, it
  moves 0.025 away from the solid it cuts and tries again.
- **Chips.** Rigid drop onto the ground or leaves.
- **Ts and T1.** Station heights come from a dense support profile along the beam: every 0.05 studs across 5 width
  samples, plus every support vert inside the beam's strip. The stations either side of any profile point above the
  chord are raised. An interior station sags at most 0.02, and an end bends down at most 4°. The twig then drops rigidly
  0.006 into what it rests on.
- **T2.** Its foot rests on the ground or leaf under it, and it is pitched about the foot until it first touches T1:
  binary search, then pressed in 0.7°.
- **O2.** Rear edge on the ground, tipped up about that edge until it first touches T1 or T2.
- **L1's petiole.** Re-aimed from the leaf base at the pinecone's right foot, ending 0.012 inside the first surface it
  meets.

**What changed from the plan, and why** (all measured on the renders):
- Leaves rest on the leaves under them by draping, not by a rigid drop. A rigid drop lifted a whole flat leaf 0.08–0.2
  onto a neighbour's lobe tip, leaving it hovering on its far side.
- V1 curls lobes 0 (front) and 4 (back-left basal). Curled side or main lobes under T1 and Ts lifted the twigs 0.08–0.2
  and pushed T2 to a 37–43° pitch.
- The pinecone scales are 8-tri faceted shingles, 56 of them (spec 36–40 lozenge plates at 12 tris).
  - 12-tri inset lozenges read as separate cubes with the dark core showing everywhere.
  - Broad pentagons with a raised apex overlap like the part cell's shingles, and the same tri count buys more scales.
  - A crown ring that hugs the surface plus a flat 6-scale cap closes the top (the first cap left a dark collar).

## Stage 2 — Optimisation and cleanup

Objects (final build, `build()` audit; tris after triangulation):

| Object | Tris | Size (studs) | Shells | Budget |
| --- | --- | --- | --- | --- |
| `ForestLitter` (hero) | **2102** | 4.57 × 3.79 × 1.13 | 82 | ≤ 2200 |
| `ForestLitterLeafLarge` (L1) | 168 | 2.15 × 2.17 × 0.16 | 2 (leaf + petiole) | < 1000 |
| `ForestLitterLeafMedium` (O1) | 168 | 1.62 × 1.65 × 0.14 | 2 | < 1000 |
| `ForestLitterLeafSmall` (Y1) | 120 | 0.86 × 0.85 × 0.11 | 2 | < 1000 |
| `ForestLitterLeafVariant` (V1) | 128 | 1.23 × 1.34 × 0.18 | 1 | < 1000 |
| `ForestLitterTwigLarge` (T1) | 108 | 3.46 × 1.39 × 0.27 | 1 | < 1000 |
| `ForestLitterTwigSmall` (Ts) | 76 | 1.06 × 0.53 × 0.17 | 1 | < 1000 |
| `ForestLitterPinecone` | **526** | 0.94 × 0.94 × 1.00 | 57 | ≤ 600 |
| `ForestLitterStoneLarge` (S1) | 42 | 1.04 × 0.90 × 0.67 | 1 | < 1000 |
| `ForestLitterStoneSmall` (S2) | 34 | 0.75 × 0.67 × 0.55 | 1 | < 1000 |

- Hero tris by kind:
  - leaves 1076 (10);
  - petioles 96 (6);
  - twigs 260 (3);
  - pinecone core 78 plus scales 448 (56);
  - stones 76;
  - chips 68 (4).
  The parts are the hero's pieces alone at hero size. The leaf parts point their tip at az 10°, and the twig parts lie
  along az 20° on the ground, so they compare with the part cells.
- On every object:
  - 0 non-manifold edges;
  - 0 bowtie verts (`fix_bowties` found 0);
  - 0 boundary, wire or loose elements;
  - 0 zero-area faces, 0 n-gons, 0 duplicate verts.
  Every shell is closed with positive volume and **0 winding errors** (`shells_report`); 0 self-intersections in any
  shell. The smallest corner is 3.13° (twig chamfer strips: T1 has 7 stations, chamfer 0.045, so no strip is longer than
  0.95).
- Normals are outward, flat shading, no custom normals, transforms applied, origin at the bbox bottom centre on every
  object. The hero's origin sits at (−0.167, +0.067, −0.02) in the build frame (`o["m062_offset"]`). Pieces sink at most
  0.02 (stones and the pinecone foot); leaves lie 0.004–0.006 into the ground.
- `o["m062_pieces"]` (JSON) records every piece's name, kind and build-frame centroid. The reports use it to name shells:
  - `shells_report`, `contact_report`, `bury_report`, `leaf_ground`, `vis_report`, `screen_report`.

**Contact and bury** (`contact_report`, `bury_report` on the hero):
- **Floating shells 0; unchained 0** (also 0 at a 0.1 chain tolerance). The named rests all overlap (gap 0.0):
  - T2 on T1;
  - O2 on a twig;
  - L1's petiole on the pinecone;
  - Ts on L1 and T1.
  Every one of the 56 scales touches the core or another scale.
- **Buried: 0 shells more than 0.05 inside another.** Deepest per kind:
  - scale in core 0.035 (the root seat);
  - V1 in S1 0.034;
  - G2 in S2 0.035;
  - Ts in T1 0.019;
  - L1's petiole in a scale 0.014;
  - stone or chip ≤ 0.009.
  The T2 seat in T1 is pressed about 0.01.

## Stage 3 — UV

`M.smart_uv` (angle-based, margin 0.008) plus `m012._uv_unfold` (cut 1 overlapping face free on the hero).
- Every object: 0 overlapping pairs, 0 flipped, minimum island gap 0.016, border 0.008, density 1.0 / 1.0 / 1.0.
- Hero conformal stretch p95 1.025, 613 islands (the exporter writes its own palette UVs; this layer is clean).

## Stage 4 — Materials, colour and texture

**Calibration.** `K.calibrate` (6 rounds, kit studio dome) to the spec 5.4 targets. Every key converged within 6 per
channel of its rendered target:

| Key | Target (rendered) | Calibrated hex in `PALETTE` | Rendered |
| --- | --- | --- | --- |
| `m062_leaf_green` | `#78AD32` | `#628E31` | (116, 170, 50) |
| `m062_leaf_deep` | `#5C922B` | `#4D792B` | (89, 142, 43) |
| `m062_leaf_lime` | `#8EB839` | `#739637` | (139, 180, 57) |
| `m062_leaf_pale` | `#B6C75C` | `#90A255` | (178, 196, 91) |
| `m062_leaf_olive` | `#876A1D` | `#6D5B1D` | (131, 104, 29) |
| `m062_leaf_yellow` | `#F0BE40` | `#BE9E3E` | (239, 191, 65) |
| `m062_leaf_amber` | `#D5921E` | `#AA7C1E` | (213, 146, 30) |
| `m062_leaf_orange` | `#E07630` | `#B1672F` | (222, 119, 48) |
| `m062_leaf_rust` | `#A1542A` | `#814A2A` | (158, 83, 42) |
| `m062_wood` | `#8E5A35` | `#734F34` | (139, 89, 53) |
| `m062_wood_light` | `#AC835F` | `#896E58` | (168, 128, 95) |
| `m062_wood_dark` | `#6C3E22` | `#5A3822` | (106, 61, 34) |
| `m062_cone_scale` | `#C8804A` | `#9E6C46` | (196, 125, 74) |
| `m062_cone_mid` | `#874D29` | `#6D4529` | (131, 77, 41) |
| `m062_cone_core` | `#4A250F` | `#40230E` | (73, 37, 15) |
| `m062_stone` | `#AEA6A2` | calibrated `#8A898C` → **`#837F7E`** | see below |
| `m062_stone_deep` | `#9F9490` | calibrated `#7F7B7E` → **`#777372`** | |

**Stones.** The calibrated stone hexes have B > G (`#8A898C`), so they would read lavender in Roblox's neutral light.
Decision 13 requires R > G > B, so the palette uses red-warm greys: `#837F7E` / `#777372`, R − G 4, G − B 1.
- The kit studio light is warm. A neutral grey renders at h 31°, which falls outside the study's S mask (h < 28°).
- This hex renders at h ≈ 26°, s ≈ 0.12: inside the mask, but darker than the sheet (front S median `#968C85` vs
  `#B0A6A5`).
- Brighter versions put the lit facets over the mask's v 0.865 limit (counted as background).

**Colour by role and position, never by facing** (`K.check` baked-shading correlation 0.00 on all ten objects):
- **Leaves**, radial bands from the petiole hub. Each outline segment's top fan triangle, chamfer quad and side quad
  take one key from that segment's mean radius as a fraction of its lobe's length; hub triangles are the base band;
  bottom triangles go by centroid.
  - Big greens: deep base (< 0.30), deep→green 50 %, green body, green→lime 50 % (0.70–0.80), lime tips.
  - O1: rust 75 % at the hub, rust 50 % (< 0.30), rust 25 % (< 0.42), then orange (spec 3.7's redder f34 read).
  - O2: orange with a 25 % rust hub.
  - V1: rust, the curled lobe tips 50 % toward wood.
  - Yellows: amber–olive base, amber inner band, amber→yellow 50 %, yellow body.
  - G1: pale with an olive base. G2: lime with a green base. G3: green with a deep base.
  - Petioles: deep green, olive, or rust-mixed per leaf.
- **Twigs:** wood body; the cut caps wood_light; the end bands and the bands either side of the knot 25 % toward
  wood_light.
- **Pinecone:** core `cone_core`. For each scale, the two root facets are `cone_mid`, the two flank facets cone_mid→scale
  50 %, and the tip facet and base `cone_scale`. The crown and cap scales are 25 % toward wood_light with body-coloured
  flanks. This is position along the scale (root → flank → tip), which gives the sheet's dark scale body under a lit tip
  (lit band B_lit `#B17143` vs the sheet's `#BF7F4E`).
- **Stones:** broad noise patches across facets (stone, stone→deep 50 %, deep). No height or foot band: the planned
  0–0.25 H foot band follows face direction on a squat block, the lighting-not-paint rule.
- **Chips:** C1 / C3 wood_dark, C2 wood_light, C4 amber.
- **Tint:** 0.03 per leaf and per twig, 0.02 per band, 0.04 per scale, 0.04 per stone facet, 0.03 per chip. All broad,
  never per-triangle. Finish: matte everywhere (roughness 0.75–0.9, low specular), no metal, no emission.

**Re-measured on the final renders** (study `cls()` masks, `<temp>\...\scratchpad\m062w\meas.py`; sheet in brackets):

| View | W : H | fill | G | Y | O | B | S |
| --- | --- | --- | --- | --- | --- | --- | --- |
| front_sheet (0, 30) | 1.80 (1.88) | 0.52 (0.60) | 34.6 (38.8) | 2.7 (1.3) | 9.0 (11.0) | 45.5 (38.6) | 8.2 (10.4) |
| f34_sheet (−5, 38) | 1.56 (1.72) | 0.52 (0.59) | 37.6 (37.0) | 3.3 (2.0) | 9.5 (11.2) | 41.7 (38.2) | 7.9 (11.6) |
| top_sheet (0, 68) | 1.31 (1.21) | 0.56 (0.64) | 41.9 (38.1) | 4.6 (1.0) | 10.7 (15.9) | 35.1 (34.7) | 7.8 (10.3) |

- Medians (front): G `#6F9C33` (sheet `#7DB031`), O `#DC7732` (`#CC6F35`), B `#8B5732` (`#77401F`), S `#968C85`
  (`#B0A6A5`).
- Camera probe (front az −10…10 × e 20–35; f34 az −20…5 × e 30–45; top e 60–75): fill stays 0.49–0.53 at every camera,
  and the best-scoring cameras are within 5° of the decided ones, so the decided cameras are kept.
- Rear, r34 and side (content only): the twig X, the pinecone, both stones, and green and orange leaves show in each.
  Shares: rear G 31.6 / O 10.8 / B 36.4 / S 16.4; side G 37.5 / B 41.6 / S 12.2.

## Stage 5 — Lighting

Skipped: the sheet shows no glow, light or emission (spec 7). No emissive parts; no lights.
Studio notes (Requires Manual Validation):
- the big leaves stay bright green and the maples orange / yellow under the game sun;
- the stones stay warm grey: their hex is R > G > B, so not blue under a cool sky;
- the pinecone scales stay tan-orange over the dark core.

## Stage 6 — VFX

Skipped: "the sheet shows no effect" (spec 7). No sockets (`build()` checks there are none). Collision:
- hero `none`;
- parts `none`, except `ForestLitterStoneLarge` `hull` (decision 8).

## Modeller's notes for the verifier

**Renders** (`art/blender/renders/models/M062/`):
- `M062_views.png`: the sheet views, nine part shots at (−20, 35), the exploded view, and the scale shot with two
  5.5-stud markers.
- `M062_spin.png`: eight azimuths at e 25 (`spin_000` … `spin_315`).
- Close-ups:
  - `cone_cu` (0, 20);
  - `junction_cu` (−30, 50) and `twig_x`;
  - `leaf_edge` (L1's lobe tip, e 6) and `leaf_edge_part` (the large-leaf part edge-on);
  - `underside_cu` (0, 5);
  - `thumb`.
- `compare_sheet.png`: the sheet cell beside our render for front, f34, top and rear, cropped and scaled to one height.

**Eight azimuths** (`vis_report`, ray grid at e 25; share of hits):

| az | leaf | twig | cone (core + scales) | stone | chip | leaf edge-on | leaf slab faces | leaves seen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 49.8 | 20.8 | 13.3 | 11.8 | 3.2 | 20.6 | 77.2 | 8 |
| 45 | 47.2 | 19.1 | 14.0 | 15.7 | 3.1 | 24.6 | 78.6 | 9 |
| 90 | 48.5 | 19.8 | 15.2 | 13.5 | 2.7 | 21.3 | 78.3 | 9 |
| 135 | 48.0 | 16.8 | 14.4 | 18.2 | 1.7 | 16.3 | 73.7 | 9 |
| 180 | 50.9 | 13.7 | 14.1 | 18.5 | 1.7 | 18.2 | 74.1 | 9 |
| 225 | 51.7 | 14.7 | 15.3 | 14.4 | 2.7 | 17.2 | 72.4 | 9 |
| 270 | 49.2 | 22.3 | 14.5 | 10.4 | 2.6 | 19.5 | 73.0 | 9 |
| 315 | 49.4 | 21.2 | 14.1 | 11.2 | 3.1 | 24.5 | 75.0 | 8 |

- The leaves lie flat by gravity, so they read the same from every side. "Leaf edge-on" (16–25 %) counts hits on faces
  within 70° of the view axis. These are the bevel and side bands of thick slabs, not flat cards: 72–79 % of leaf hits
  land on the top and bottom slab faces.

**Projected piece centroids at front_sheet** (x from the left, h from the bottom; the spec 1.2 sheet value in brackets):
- within 0.05:
  - P (0.49, 0.42) [0.48, 0.45]
  - L2 (0.26, 0.55) [0.29, 0.60]
  - O1 (0.30, 0.17) [0.28, 0.18]
  - S2 (0.18, 0.38) [0.21, 0.40]
  - G1 (0.49, 0.08) [0.51, 0.09]
  - G2 (0.07, 0.27) [0.07, 0.32]
  - O2 (0.53, 0.80) [0.49, 0.81]
- off:
  - L1 (0.75, 0.20) [0.78, 0.26]
  - Y1 (0.12, 0.47) [0.13, 0.55]
  - G3 (0.91, 0.44) [0.90, 0.61]
  - S1 (0.81, 0.60) [0.77, 0.73]
- These are 3D centroids projected near-orthographically. The sheet's values are centroids of the visible pixels, so
  back pieces whose lower half hides behind the twigs or stones (S1, G3, Y1) read 0.08–0.17 higher on the sheet.

**Deviations from the Decisions and the plan (with reasons):**
1. **Piece sizes are 6–20 % over the spec 2 table**, to get the pile's coverage and green share toward the sheet:
   - L1 2.20 across (spec 1.85);
   - L2 1.96 (1.63);
   - O1 1.68 (1.45);
   - O2 1.15 (1.05);
   - V1 1.36 (1.20);
   - Y1 / Y2 0.86 (0.80);
   - G 0.80 / 0.78 / 0.70 (0.70 / 0.70 / 0.60);
   - S1 1.05 × 0.89 × 0.64;
   - S2 0.80 × 0.66 × 0.54.
   At the spec sizes the front fill was 0.43 and G 32 %. The hero stays inside decision 1's tolerances: 4.57 × 3.79 ×
   1.13 (D 3.79 is near the 3.85 limit). The pinecone is Ø 0.94 × 1.00.
2. **Positions moved** for gaps, nudges out of the stones, and the sheet's composition. Plan points used:
   - L1 (0.93, −0.86), L2 (−1.25, 0.95) az 140, O1 (−1.12, −0.94), O2 rear edge (−0.32, 1.76) az 280, V1 (0.64, 0.44);
   - Y1 (−1.92, 0.62) (behind S2, under L2's lobe), Y2 (0.48, 1.36), G1 (−0.20, −1.48), G2 (−1.93, −0.32);
   - G3 (1.74, 0.42) az 350, S2 (−1.64, −0.18), Ts (0.42, 0.30) → (1.40, −0.10).
   Leaves that cut a stone are pushed out in 0.025 steps. Final centroids are in `leaves[*].centre` of `build()`.
3. **Twig X.** Section and placement:
   - T1 is 0.24 square and T2 0.22 (spec 0.25 / 0.23), so the twigs stay near 20 % of the front.
   - T2 is 1.82 long (1.75), with its foot at (−0.02, 0.10) right behind the pinecone (spec (0.10, 0.30)).
   - T2 rests on T1 at a **27.0° pitch, top z 1.107** (spec 28°, 1.08).
   - T1 lies on L2, V1 and L1's side-lobe tip at bottom z 0.12–0.21. Its front end rests on L1's tip 0.12 above the
     ground, not on the ground.
4. **O2 propped at 46.5° with its tip at z 0.87** (spec 33–40°, 0.55). The larger maple touches T1 first at that angle,
   so a lower prop would cut T1.
5. **L1's petiole** runs 0.435 long and rises 6.6° onto the pinecone's foot (spec 0.40, 10–15°).
6. **Pinecone:** 56 faceted shingles at 8 tris each (spec 36–40 at 12) plus a crown ring and cap (see stage 1);
   526 tris, within the 600 cap.
7. **Stone colour:** the hex is not the calibrated value (stage 4) and there is no foot band (lighting-not-paint).

**Leftovers and known misses:**
- **Fill** 0.52 front / 0.52 f34 / 0.56 top vs the sheet's 0.60 / 0.59 / 0.64 (tolerance ±0.05). The painted sheet packs
  broad, overlapping leaves; ours keep their sinuses and settle without merging. The camera probe can't close this.
- **Shares slightly outside tolerance:**
  - front B 45.5 (≤ 44.6);
  - f34 S 7.9 (≥ 8.6);
  - top O 10.7 (≥ 11.9) and Y 4.6 (≤ 2.5);
  - f34 W : H 1.56 (1.65–1.80, a soft check);
  - top W : D 1.31 (1.15–1.28).
  Front G 34.6, O 9.0, S 8.2, Y 2.7 and W : H 1.80 are within tolerance.
- **Stones render darker** than the sheet's (S median 26 below in each channel). This trades against keeping their lit
  facets inside the S mask under the warm studio with an R > G > B hex.
- **The pinecone part** seen from above (−20, 35) shows the crown cap as a slightly lifted lid with a thin dark line
  under it. From the hero cameras it reads as a scaly egg (`cone_cu`).
- Petioles read as thin sticks in places (spin 180 / 225: O2's petiole stub under the propped leaf).
- The rear, r34 and side cells are the sheet's redrawn compositions (two pinecones). They are judged for content only.

**Re-running:** `import importlib, kit_models, m062; importlib.reload(kit_models); importlib.reload(m062); m062.build()`
builds the hero and parts, renders, and returns the audit, UV, materials, contact, bury, leaf_ground, winding, vis,
screen and `problems` (an empty list in the final build). `m062.hero_only()` and `m062.preview()` are the fast loops.

## Stage 7 verification (round 1)

Fresh verifier, read-only. Background session on port 9877, on `art/blender/assets/kit/wip/M062_verify.blend` (not
saved). Every number below is my own measurement, made with my own scripts in `<temp>\...\scratchpad\m062v\` (topology,
contact, hover, bury, sizes, visible centroids, eight-azimuth ray grid, and image masks that reuse the study's `cls()`).
Renders are in `art/blender/renders/models/M062/verify/`:
- sheet views `*_sheet.png`;
- `v_spin.png` (eight azimuths at e 25);
- `v_parts.png` (parts at (−20, 35) plus the cone side view);
- `v_misc.png` (the cone from above and from the side, leaf and stone edges, a low view);
- `v_cu.png` (close-ups of the chips, petioles, O2 from both sides, the T1 end, the junction, the underside and a leaf tip).

**Verdict: FAIL, 6/10.** The pile reads like the sheet, and the topology, budget, contact chain and bury checks are all
clean. Two things fail: four petioles are cut off from their leaves (broken construction, also in two exported parts),
and the pinecone's crown reads as a lid.

### Re-measured: passes

- **Tris.** Hero 2102 (ceiling 2200): leaves 1076, petioles 96, twigs 260, cone core 78 + 56 scales × 8 = 448, stones 76,
  chips 68. Parts: LeafLarge 168, LeafMedium 168, LeafSmall 120, LeafVariant 128, TwigLarge 108, TwigSmall 76,
  **Pinecone 526** (≤ 600), StoneLarge 42, StoneSmall 34.
- **Hero size.** 4.566 × 3.795 × 1.127, inside decision 1's tolerances. The depth is 0.055 under its 3.85 limit.
  - Pinecone 0.94 × 0.94 × 1.04, including the 5° lean and the 0.02 sunk foot.
  - T1 is 3.59 long with a 0.254 section (0.30 at the knot). T2 is 1.85 long, 0.22 square, pitched 27.0°, top z 1.107.
  - Ts is 1.10 long, 0.17 square.
- **Every object** (hero and 9 parts):
  - 0 non-manifold edges, bowtie verts, boundary, wire or loose elements, zero-area faces and n-gons;
  - 0 winding errors and 0 self-intersections in any shell, every shell with positive volume;
  - smallest corner 3.13°;
  - transforms applied (rot 0, scale 1), origin at the bbox bottom centre (offset 0, 0, 0), no modifiers, no custom
    normals, flat shading;
  - collision none, except StoneLarge hull.
  - Build-frame offset (−0.167, +0.067, −0.020).
- **UV.** One layer per object, 0 overlapping pairs, 0 flipped, minimum gap 0.016, border 0.008, density 1/1/1. Hero
  conformal stretch p95 1.026, 661 islands.
- **Contact** (82 shells; a contact is a triangle overlap or a vertex within 0.03; ground at build z ≤ 0.03):
  - floating 0, unchained 0;
  - all 56 scales touch the core (worst gap 0.0);
  - T2–T1 0.0 (T1 is 0.009 inside T2), O2–T1 0.0, Ts–T1 0.0, T1–L2 0.0, T1–L1 0.0.
- **Bury** (ray parity, three directions, vertex depth): 0 shells more than 0.05 inside another. Deepest:
  - scale in core 0.035;
  - V1 in S1 0.034;
  - Y petiole in its leaf 0.033;
  - O1 in S2 0.032;
  - G2 in S2 0.028;
  - Y1 in L2 0.022;
  - Ts in T1 0.020.
  Lowest vertex z −0.020 (stones and the cone foot); leaves sit at −0.006.
- **Colour code.** The builder chooses no colour by face normal:
  - leaves take radial bands from the hub per outline segment;
  - twigs take the caps, end bands and knot bands by station index;
  - scales take the root facets `fan[0]` / `fan[4]` by vertex order;
  - stones take a 3-D noise field;
  - chips take one key each.
- **Colours.**
  - Stones render `#958C85` (front S median), R > G > B, h 26°, s 0.11: warm grey, never lavender.
  - Greens are not olive: front G `#709D34`, h 87° (sheet `#7DB031`, 87°); large-leaf part `#73A435`.
  - Orange, rust and yellow stay apart: medium part `#DC7834`, variant `#9E5730`, small `#CEA339`.
- **Eight azimuths** (ray grid at e 25): leaves 47–52 %, twigs 14–22 %, cone 13–15 %, stones 10–19 %.
  - 9–10 leaves are seen from every side.
  - Leaf hits on side or bevel bands (more than 70° off the view) are 16–24 %; the rest land on the slab tops. Those
    bands belong to 0.06–0.08 slabs, not cards.
  - Every frame reads as leaves + twig X + pinecone + stone.
  - The twig X reads from every side, with T2 resting on T1.
- **Content of the rear, r34 and side views.** Each shows the twig X, the pinecone, both stones, and green and orange
  leaves. No underside shows.

### Blockers

1. **Four petioles are cut off from their leaves** (true breakage; spec §6 says "petiole (welded to its leaf)").
   - Leaf-to-petiole gap in the hero: **L1 0.108, L2 0.098, O1 0.061, O2 0.033**. Y1 and Y2 overlap (0.0).
   - The same gap is in the exported parts: **ForestLitterLeafLarge 0.122, ForestLitterLeafMedium 0.061**. Each is a
     second shell lying loose beside the leaf.
   - Each loose stem lies on the ground, so the floating count misses it. On the renders the stems read as loose green
     or orange sticks:
     - L2's stem lies alone between L2 and the cone (`v_cu.png`, petiole close-ups);
     - the large-leaf part shows its stem detached at the left (`v_parts.png`);
     - O2's stem hangs under the propped leaf like a stake (spin 180 / 225).
   - **Cause.** `place_leaf` and `prop_leaf` start the stem at `rear_x + 0.10`. `rear_x` is the outline's minimum x, which
     for the `large` and `maple` kinds is the basal-lobe tips (±124° / ±114°), not the base sinus (−0.08 R). So the stem
     starts in the open notch between the basal lobes. `maple_small` happens to reach.
   - **Fix.** Start every stem inside the leaf base, at about the hub (`KINDS[kind]["hub"] * R`) or at the base sinus
     x + 0.05, and lengthen it by the difference. Re-aim L1's stem from that start. Then require a leaf-to-petiole gap
     of 0 in `contact_report`.
2. **The pinecone's crown reads as a lid** (the second focal silhouette; visible against the sheet).
   - In the part shot (−20, 35) and from above (0, 60), the crown reads as a lidded pot: the crown ring of 9 scales
     lifted 12° plus the near-flat 6-scale cap form a rosette with a central hole over a dark collar.
   - At e 25 in all eight azimuths, and at front_sheet, it reads as a jagged crown above a dark band.
   - The sheet (`z_cone_part.png`, `z_cone_f34.png`) shows an egg whose rounded top carries the same shingles, getting
     smaller.
   - **Fix.** Close the top with the downward shingle pattern continued (a sixth, smaller ring plus a 3–4-scale cap lying
     on the core, no lifted ring), so no dark collar shows.
   - The body passes: it reads as shingled scales, not cubes or a ball.

### Minors (measured; each says whether it shows against the sheet)

- **Chips perch on leaf edges** (visible in close-up; a minor read at the sheet cameras).
  - C1 bottom z 0.157, C2 0.108, C3 0.118. All three sit rigidly on a lobe edge.
  - 38–62 % of their undersides hang more than 0.10 above what lies below them.
  - The 0.03 contact rule passes, but they read as balanced on the edge (`v_cu.png`, C2).
  - Fix: tilt each chip onto its support (two-point settle) or move it onto bare ground.
- **T1 never touches the ground** (visible from the low side azimuths).
  - Its lowest point is z 0.111; the gap under its underside has a median of 0.13 and a maximum of 0.25.
  - It is carried on lobe tips of L1, L2 and V1 (spec: bottom 0.00 at the front end).
  - Numeric only at the sheet cameras.
- **O2 propped at 46.5°, tilt 47°** (visible).
  - From front_sheet and f34 its face is near edge-on: a thin orange strip lying on T1 in place of the sheet's orange
    maple face behind the crossing. At az 45 / 315, 50–53 % of its hits are edge-on.
  - From the rear its stem reads as a stake (blocker 1).
- **Visible piece centroids** (ray-cast per piece; x from the left, h from the bottom; within 0.05 of §1.2):
  - front 9 / 14, f34 7 / 14, top 7 / 14;
  - P, L1, O1, O2, S2 and G1 are within 0.05 in front and f34.
  - Misses:
    - T1's back-left end h −0.08 (front), −0.13 (f34), −0.07 (top): it doesn't reach as high or as far back as on the
      sheet;
    - T2's top end x −0.08 in the f34 (0.66 vs 0.74);
    - L2 x −0.085 (f34);
    - S1 h −0.09 (front);
    - L1 h −0.07 (front);
    - Y1 −0.04 to −0.07;
    - O1 x +0.08 (top).
  - Mildly visible: the X sits a little left and low in the f34.
  - **G3 is 0.2 % visible from the front** (0.7 % in the f34), hidden by S1 and T1, where the sheet shows a distinct small
    green leaf at the right edge. Visible.
- **Fill** (visible: a looser pile with gaps between the leaves).
  - Front 0.519, f34 0.519, top 0.556, against the sheet's 0.598 / 0.593 / 0.641 (±0.05): misses by 0.03 / 0.02 / 0.04.
  - With every non-background pixel counted, the fill is 0.546 / 0.549 / 0.589 against the sheet's 0.663 / 0.645 / 0.717.
- **Shares outside tolerance** (numeric only, except top Y, which is mildly visible):
  - front B 45.5 (≤ 44.6);
  - f34 S 7.8 (≥ 8.6);
  - top O 10.9 (≥ 11.9);
  - top Y 4.6 (≤ 2.5): the olive and amber bases and the olive stems also fall in the Y mask.
  - In tolerance: front G 34.6, Y 2.7, O 9.1, S 8.1; f34 G 37.6, Y 3.3, O 9.7, B 41.5; top G 41.9, B 34.9, S 7.8.
- **W : H** (soft, numeric).
  - Front 1.80 (OK), f34 1.56 (1.65–1.80), top W : D 1.31 (1.15–1.28).
  - Top profile: front f .7 0.99 vs 0.81 (the lifted end sits one column right); f34 f .7 0.70 vs 0.99, f .1 0.71 vs 0.61.
- **Colour against the sheet** (front medians, sheet in brackets):
  - G `#709D34` (`#7DB031`): 19 dark in G. Numeric; it reads a touch darker.
  - B `#8B5834` (`#77401F`): 20–24 light. Mild.
  - S `#958C85` (`#B0A6A5`): 26–32 dark and warmer (h 26° vs 5°). Visible but mild.
  - **The yellow part renders `#CEA339`** against the cell's `#F0BE40` (target ±12): the amber/olive centre covers about
    half the leaf. Visible: a mustard centre.
  - **Pinecone contrast is low.** Shade quartile `#55321A` against the cell's `#2A1004`, body `#8E5530` against `#703C1B`.
    Visible: no near-black gaps between the scales.
- **56 eight-tri scales** in place of 36–40 lozenge plates.
  - The budget holds (526).
  - Visible: the scales read as pointed pyramids, not the sheet's flat lozenge plates, which adds to the low contrast above.
- **Pieces 6–20 % larger** (numeric). L1 spans 1.94 in plan against the pinecone's 0.94 (ratio 2.06; the sheet's f34
  ratio is 1.89). The hero is inside tolerance.
- **Twig sections 0.24 / 0.22** against 0.25 / 0.23 (numeric).
- **L1's petiole** is 0.435 long and rises 6.6° (numeric; see blocker 1).

### For the fix round

- Blocker 1: stem starts.
- Blocker 2: close the cone top.
- Then, cheaply:
  - settle C1–C3 onto bare ground or tilt them onto their support;
  - lower O2's prop or swing it so its face shows from the front;
  - reveal G3;
  - pull the yellow amber band in to under 0.30;
  - darken the cone's root facets (or `cone_core`) toward the sheet's gaps.
- Keep everything that passes: topology, contact, bury and colour-by-role.

## Fix round 1 (modeller, 2026-11-01)

Fresh fix modeller, background session on port 9877, `art/blender/assets/kit/wip/M062.blend` (saved after the final
build). A fix round had been half done in `m062.py` before a pause; this round re-ran it, kept what worked and finished
the list. Scratch scripts (cone loop, O2 pose search, visible-piece shares, colour masks) are in `<temp>\...\m062f\`.

### Blocker 1: petioles cut off from their leaves (fixed)
- Every stem now starts inside its own leaf base: `place_leaf` starts it `PET_SEAT` (0.04) behind the base notch
  (`notch_x`), not at `rear_x` (the basal-lobe tips), and runs it back between the basal lobes. L1's stem is re-aimed
  from that start onto the pinecone foot (`_aim_petiole`; now 0.66 long, rising 5.5°).
- O2 has no petiole (spec 2.2 lists none); its old stub was the "stake" seen from the rear.
- New check `petiole_report` in `build()`: every stem's gap to its own leaf must be 0 (triangles intersect), in the hero
  by piece name and in each leaf part that has a stem. Result: **Y1, Y2, L1, L2, O1 0.0; the LeafLarge, LeafMedium and
  LeafSmall stems 0.0** (round 1: L1 0.108, L2 0.098, O1 0.061, O2 0.033; LeafLarge 0.122, LeafMedium 0.061). L1's
  stem also touches the cone (0.0).

### Blocker 2: the pinecone's top read as a lid (fixed; cone rebuilt)
- **Core:** a rounded egg with 8 sides. Profile r 0.12 / 0.30 / 0.425 / 0.435 / 0.35 / 0.18 at z −0.02 / 0.14 / 0.36 /
  0.58 / 0.76 / 0.88, apex 0.93: widest at 0.4–0.6 H with a broad domed top. The old core ended in a near-flat cone
  under a lifted crown ring and a flat cap; that was the lid and the dark collar.
- **Scales:** 58 faceted lozenge scales lying **on** the egg (`scale_gem`), tiled in rings like the sheet's
  (`z_cone_f34`, the part cell):
  - a 4-scale cap whose roots meet over the apex, then rings of 8, 8, 8, 8, 8, 8 and 6;
  - each ring's roots sit at the side corners of the ring above, half a scale round, so the rings interlock with no
    holes;
  - each scale is its tile shrunk to 0.93, so the dark core shows only as thin diamond lines (the sheet's near-black
    gaps);
  - two crest verts across each scale fold it into a lit upper facet and a lower facet turning down to the tip; the tip
    is lifted 0.008–0.026 off the egg (a shadow line under each); 6 verts, 8 tris per scale.
- Tried and dropped on the way: flat shingle plates (the paused round: tiles standing off the egg, a flat top), blunt
  10-tri pads (a geodesic ball), wide-root pointed shingles (dark wedge holes).
- **Result.** The part shot (−20, 35), the view from above and every spin frame read as a round scaled pinecone with a
  domed top of small scales and no lid or collar.
  - Pinecone part **558 tris** (cap 600), Ø 0.90 × 0.96 tall.
  - Rendered part: lit quartile `#CD844F` (cell `#C47B44`–`#CD824D`), shade quartile `#30150A` (cell `#2A1004`), median
    `#AC6B3E`.
  - Root facets take `cone_mid→scale 50 %` and the underside `cone_mid`, by position on the scale. `K.check`
    baked-shading correlation 0.17 (limit 0.5). `CONE_C` is `#2A1206` (was `#40230E`), so the gaps read near-black.

### Minors
- **Chips (fixed).** Each chip now lies flat on bare ground near its plan point (the nearest spot with no leaf under its
  footprint and no cut into a stone or the cone), then settles. New `chip_report`: C1–C4 hang **0.0** over what is
  below them (round 1: 38–62 % of their undersides more than 0.10 up).
- **T1 on the ground (fixed).** L1 is turned 12° and moved 0.06, so its side lobe no longer holds T1's front end up.
  T1's front stations are now at z 0.0 (round 1: lowest point 0.111). Its middle still rides on V1 (0.23 at 0.44 L).
- **O2 (fixed).** Propped on the back of T1 it could only face the back, so it was edge-on from the front.
  - New `tilt_leaf`: O2 (span 1.02, the spec's 1.05) is tilted 26° with its face toward az 320 and dropped onto what is
    under it. It rests on **T1 (gap 0.004) and Y2 (0.011)**, caught behind the crossing with its face to the front; tip
    z 0.60.
  - The pose came from a search over plan point, tip az, tilt az and tilt that kept two supports and the hero depth
    inside 3.85.
  - Visible share of O2: front 3.6 %, f34 3.9 % (round 1: a thin strip).
- **G3 (fixed).** Moved out to (1.85, 0.60), span 0.64, from behind S1 and T1. Front visible share 1.0 → 1.5 % (the
  sheet's ~1.9 %); centroid (0.94, 0.49) in the front view.
- **Yellow (fixed).** Amber hub at half a step, amber only inside 0.18 L, amber→yellow to 0.30, then yellow. The yellow
  part renders median `#EDB33B`, lit `#FFCD46` (cell `#F0BE40`; round 1 `#CEA339`).
- **Stones.** Lighter red-warm greys `#9A9493` / `#8C8685` (R > G > B). Front S median `#B4A79E` (sheet `#AEA5A4`;
  round 1 `#958C85`).
- **Height.** T2 shortened 1.82 → 1.72: it pitches 33° now that T1 lies lower, and its top had reached 1.18. Top z
  1.123, hero H 1.14.
- **V1** keeps its curl on lobes 0 / 4 (16° / 18°); it is not what lifts T1 (tested 0–18°, no change).

### Measured (final `build()`)
- `problems: []`.
- **Tris.** Hero **2118** (ceiling 2200): leaves 1076, petioles 80 (5), twigs 260, cone core 94 + 58 scales × 8 = 464,
  stones 76, chips 68. Parts: LeafLarge 168, LeafMedium 168, LeafSmall 120, LeafVariant 128, TwigLarge 108,
  TwigSmall 76, **Pinecone 558**, StoneLarge 42, StoneSmall 34.
- **Hero size 4.57 × 3.75 × 1.14** (decision 1: 4.4 ± 0.25, 3.6 ± 0.25, 1.1 ± 0.10). Build-frame offset
  (−0.165, +0.039, −0.020).
- **Every object:**
  - 0 non-manifold edges and verts (bowties), 0 boundary, wire, loose, zero-area faces and n-gons; normals outward;
  - **0 winding errors and 0 self-intersections in every shell**; smallest corner 3.13° (pinecone 18.2°);
  - origin at the bbox bottom centre;
  - UV: 0 overlaps, 0 flipped, minimum gap 0.016, hero stretch p95 1.028.
- **Contact:** 83 shells, **floating 0, unchained 0** (also 0 at the 0.1 chain tolerance). T2 on T1 0.0, O2 on T1 0.0,
  L1's stem on the cone 0.0, Ts on L1 / T1 / V1. Every scale touches the core or a scale. Lowest vertex −0.020.
- **Bury:** 0 shells more than 0.05 inside another. Deepest: a scale in the core 0.033, O1 in S2 0.032, chip C3 in C2
  0.030, L1's stem in a scale 0.025, Ts in T1 0.021.
- **Eight azimuths** (ray grid, e 25): leaves 47.5–51.5 %, twigs 15.5–21.9, cone 11.4–13.7, stones 11.5–19.2. 9–10
  leaves seen in every view; 77–81 % of leaf hits on the slab tops.
- **5° azimuth sweep** (new `sweep_report`; e 25; whole leaves within 15° of edge-on by their mean top normal): worst
  **5.8 %** of the leaf area (az 165, O2 seen from behind). Only O2 ever turns edge-on; every other leaf lies within
  0.9–7.6° of flat.
- **Sheet views.** The study's masks, re-implemented in `<temp>\...\m062f\meas.py`, give the sheet front G 37.3 / Y 1.2
  / O 10.6 / B 40.3 / S 10.6 (the spec's 38.8 / 1.3 / 11.0 / 38.6 / 10.4). Sheet values in brackets:

| View | W : H | fill | G | Y | O | B | S |
| --- | --- | --- | --- | --- | --- | --- | --- |
| front_sheet | 1.84 (1.88) | 0.57 (0.61) | 34.3 | 2.4 | 11.0 | 41.1 | 11.3 |
| f34_sheet | 1.60 (1.72) | 0.57 (0.60) | 36.6 | 2.9 | 11.6 | 38.2 | 10.6 |
| top_sheet | 1.26 (1.20) | 0.57 (0.67) | 40.1 | 3.5 | 12.1 | 34.6 | 9.8 |

- Medians (front): G `#729D33` (sheet `#7DB031`), O `#DA7732` (`#CC6F35`), B `#905C37` (`#7A4522`), S `#B4A79E`
  (`#AEA5A4`).

### Renders
`art/blender/renders/models/M062/`: `M062_views.png`, `M062_spin.png`, `*_sheet.png`, `part_*.png`, `cone_cu.png`,
`junction_cu.png`, `twig_x.png`, `leaf_edge*.png`, `underside_cu.png`, `thumb.png`, `scale.png`, `exploded.png` and
`compare_sheet.png` (regenerated: the sheet cell beside our render for front, f34, top and rear). The `fix1/` folder
holds the paused round's intermediate renders (the flat-plate cone); they are superseded.

### Left for the verifier
- **Top Y 3.5 %** (spec 1.0 ± 1.5): Y1, Y2 and their olive stems read from above more than on the sheet.
- **Fill** 0.57 in every view: the front is within 0.05, the top 0.10 under the sheet's. The painted pile overlaps its
  leaves more densely.
- **f34 W : H 1.60** (soft check, 1.65–1.80); front 1.84 and top 1.26 are in range.
- **Front B median** about 20 lighter than the sheet's (the twigs' lit tops).
- O2 shows its underside or edge from the rear (az 135–200), within the sweep target.
- The pinecone is near-round (0.90 × 0.96) where the cell's egg is slightly taller. Its scales are diamonds with a
  cross crest, crisper than the sheet's soft painted lozenges.

## Stage 7 verification (round 2)

Fresh verifier, read-only. Background session on port 9877 on `art/blender/assets/kit/wip/M062v.blend` (the kit copy
taken after the main session built 062; not saved, `build()` not run). Every number below is my own measurement with my
own scripts and renders in `<temp>\...\v2\` (topology, shell contact / chain / ray-parity bury, petiole and scale
gaps, a 5° azimuth sweep, an eight-azimuth ray grid, the study's HSV masks re-implemented on the sheet cells and on my
renders at the decided cameras, part shots at (−20, 35) beside the part-list and exploded cells, close-ups of every
stem joint and of the pinecone from nine directions).

**Verdict: PASS, 8/10.** Both round-1 blockers are fixed, and every technical, contact and foliage check passes. What
is left are visible-but-mild style differences (pinecone scale pattern, rounder stones, a looser pile), listed below.

### Round-1 blockers, re-checked
1. **Petioles join their leaves: fixed.**
   - Hero: Y1, Y2, L1, L2 and O1 stems each intersect their own leaf (gap 0.0; 2–3 of each stem's 10 verts lie inside
     the leaf slab). O2 has no stem now, so the rear "stake" is gone.
   - Parts: the LeafLarge, LeafMedium and LeafSmall stems each intersect their leaf (gap 0.0).
   - Close-ups of each part from above (0, 80) and low (200, 12) show the stem running into the base notch, under the
     slab. In the hero front / f34, L1's stem runs from the leaf to the cone foot (gap 0.009 to the core, 0.0 to a
     scale), and L2's and O1's stems run from their leaf bases toward the cone.
2. **Pinecone lid: fixed.**
   - Hero close-ups at (0 / 90 / 180 / 270, 20), (45, 60) and (0, 85), and the part at (−20, 35), (0, 0) and (0, 70):
     a closed scaly dome from every side, with no lifted ring, no collar and no dark band under the top.
   - Profile (part): Ø 0.67 at 0.1 H, 0.84 at 0.3, 0.94 at 0.5, 0.95 at 0.7, 0.80 at 0.85 and 0.55 at 0.95 H.
     Projected W : H at the cell camera 0.99 (cells 1.00 / 1.11).
   - 58 scales, all 58 touching the core (gap 0.0) in the hero and in the part.

### Re-measured: passes
- **Tris.** Hero 2118 (ceiling 2200). Parts: LeafLarge 168, LeafMedium 168, LeafSmall 120, LeafVariant 128,
  TwigLarge 108, TwigSmall 76, Pinecone 558 (≤ 600), StoneLarge 42, StoneSmall 34.
- **Sizes.** Hero 4.571 × 3.746 × 1.143 (4.4 ± 0.25, 3.6 ± 0.25, 1.1 ± 0.10). Pinecone part 0.90 × 0.90 × 0.96;
  T2 top z 1.123.
- **Every object** (hero and 9 parts):
  - triangulated; 0 non-manifold edges, 0 bowtie verts, 0 boundary, wire or loose elements, 0 zero-area faces, 0 n-gons,
    0 duplicate verts;
  - 0 winding errors, every shell with positive volume; smallest corner 3.13° (pinecone 18.2°);
  - origin at the bbox bottom centre (0, 0, 0), rotation 0, scale 1, no modifiers, no custom normals, flat shading;
  - one UV layer, 0 overlapping pairs, 0 flipped, minimum gap 0.016, border 0.008; hero stretch p95 1.028;
  - only `FB_m062_*` materials; collision `none` everywhere except `ForestLitterStoneLarge` `hull`.
- **Contact** (83 shells, my own BVH pairwise gaps): floating 0, unchained 0. T2–T1 0.0, O2–T1 0.0 and O2–Y2 0.011,
  Ts–T1 0.0. Lowest vertex −0.020 (stones, cone foot); leaves −0.006 to 0.0.
- **Bury** (ray parity in three directions, vertex depth): nothing over 0.05. Deepest: O1 in S2 0.032, V1 in S1 0.028,
  G2 in S2 0.028, C2 in C3 0.026, L1's stem in a scale 0.025, G3 in S1 0.023, Y1 in L2 0.022, scale in scale 0.021,
  Ts in T1 0.021.
- **Foliage.**
  - 5° sweep over 72 azimuths at e 25: worst 6.5 % of leaf area in whole leaves within 15° of edge-on (az 165, O2 only;
    target about 10 %). At e 35 also 6.5 %. Every other leaf lies 0.9–7.6° from flat.
  - Eight azimuths at e 25 (ray grid, step 0.02): leaves 47.5–51.4 %, twigs 15.4–22.3, cone 11.5–13.7, stones
    11.3–19.2; 9–10 leaves seen in every view. Slab-top facets within 15° of edge-on 4.7–9.9 % of leaf hits; slab
    rims 11–14 %. Every spin frame reads as leaves + twig X + pinecone + stones.
- **Sheet views** (study masks on the sheet cell and on my render, same code; sheet in brackets):

| View | W : H | fill | G | Y | O | B | S |
| --- | --- | --- | --- | --- | --- | --- | --- |
| front_sheet (0, 30) | 1.84 (1.89) | 0.57 (0.65) | 34.1 (35.7) | 2.4 (1.2) | 11.1 (10.1) | 38.4 (35.6) | 11.3 (10.1) |
| f34_sheet (−5, 38) | 1.60 (1.72) | 0.58 (0.63) | 36.4 (34.9) | 2.9 (1.9) | 11.7 (10.5) | 35.6 (36.1) | 10.6 (11.3) |
| top_sheet (0, 68) | 1.26 (1.20) | 0.58 (0.70) | 39.8 (34.6) | 3.5 (0.9) | 12.1 (14.4) | 32.1 (31.5) | 9.8 (9.9) |

  - Front medians: G `#729C33` (`#7DB031`), O `#DA7732` (`#CC6F35`), S `#B6A9A0` (`#AEA5A4`), B `#8F5C35`
    (`#77401F`).
  - Parts at (−20, 35), medians against the cell: large leaf `#70A132` (`#80B131`), medium `#D27131` (`#DD742F`),
    small `#EDB338` (`#F0BE42`), variant `#9D552E` (`#A2562B`), twig `#8D5D39` (`#94623C`), stones `#B4A69F` /
    `#BBADA4` (`#B1A6A1` / `#A19795`). Pinecone lit quartile `#CC834E` (`#D0955B`), shade quartile `#2F150A`
    (`#2F1205`): the near-black gaps now match.
  - The front, f34 and top compositions match the sheet piece for piece: the twig X with its lifted end the top, the
    pinecone in front of it, L1 front-right, L2 back-left, O1 front-left, O2 behind the crossing, S1 back-right, S2
    left, G1 front-centre.

### Blockers
None.

### Minors (measured; each says whether it shows against the sheet)
1. **Pinecone scale style** (visible, mild). The cone reads as a scaled pinecone from every view, but as a round ball
   covered in about 7 small pointed diamond scales across the front, with a criss-cross lattice of dark gaps. The sheet
   (part cell, exploded, f34) shows about 4–5 broad, rounded lozenge shingles across the front in down-pointing rows on
   a slightly tapered egg. Fix if touched again: fewer, broader scales (about 6 rings of 6–7), rounded or blunt tips,
   and a slightly narrower foot.
2. **Stones rounder and lighter than the cells** (visible, mild). At the cell camera, StoneLarge projects W : H 1.17
   and StoneSmall 1.21 (cells 1.39 / 1.43): domed boulders, where the sheet has squat stones with broad sloping tops.
   Shade quartiles are `#988D85` / `#8B807A` (cells `#6C6667` / `#6D6768`).
3. **Looser pile** (visible). Fill is 0.57 front, 0.58 f34 and 0.58 top, against 0.65 / 0.63 / 0.70 measured the same
   way on the sheet. Floor shows between the leaves, most of all from the top.
4. **Yellow share from above** (mildly visible). Top Y is 3.5 % (sheet 0.9; tolerance ≤ 2.5): Y1 / Y2 and their
   olive stems show more than on the sheet.
5. **Wood lighter and flatter** (mild). Front B median `#8F5C35` against `#77401F` (24–28 per channel; target 15). The
   TwigLarge part's lit quartile is `#976844` against the cell's `#BE8556`: less lit-top / dark-side contrast. There are
   no knot or grain facets like the cell's.
6. **Green a touch dark** (numeric). Front G median `#729C33` against `#7DB031` (G channel 20 lower); the hue is right
   (not olive).
7. **f34 W : H 1.60** (soft check 1.65–1.80; numeric). The lifted twig end peaks at about f 0.6 of the width, against
   the sheet's 0.7.
8. **Rear, r34** (content only; visible in those redrawn cells). T2 points toward the back-right, so from 155–180° it is
   foreshortened to a stub, and the X reads weakly. O2 shows its underside from behind.
9. **Ts parallel under T1** (mild, visible in the front and f34). The small twig reads as a second beam beside T1, right
   of the cone, where the sheet shows the rust leaf V1. V1 is mostly hidden.
10. **G1 reads cupped** (mild). The pale front leaf, draped over L1's edge and a chip (top z 0.207), shows an olive
    centre in a lighter rim, so it reads a little like a small bowl. The sheet's G1 is a flat pale ivy leaf.
11. **Facet-level edge-on** (numeric). 30 % of the leaf top-facet area is within 15° of edge-on at az 350, e 25 (the
    folded lobe facets). The STAGES whole-leaf measure passes at 6.5 %.

### For the main session
Ready to commit with minors 1–11 noted. None is broken construction, and the defining pieces (the twig X, the
pinecone, the big lobed leaves) read like the sheet.
