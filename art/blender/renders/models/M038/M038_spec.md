# 038 Pebble Scatter — spec

Reference: `art/blender/assets/references/038.png` (1024 × 1536 px). The sheet's own title is "04 – PEBBLE SCATTER",
with the subtitle "Small stones and slabs (5 pieces). Use to detail ground." and "PAGE 40/132" at the bottom right; the
footer reads "FLINTBORN — INDIVIDUAL MODEL STUDY". INDEX.md row 38 calls it "Pebble scatter model study".
Builder: `art/blender/kit/mcp/m038.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows one optional effect: a soft contact shadow** (§7).

Sheet text:
- **Header:** "04 – PEBBLE SCATTER"; "Small stones and slabs (5 pieces). Use to detail ground."; "PAGE 40/132".
- **View labels:** "ASSEMBLED VIEW (FRONT 3/4)", "ASSEMBLED VIEW (REAR 3/4)", "ORTHOGRAPHIC VIEWS (SAME CONFIGURATION)":
  "FRONT VIEW", "SIDE VIEW (RIGHT)", "REAR VIEW", "TOP VIEW".
- **Material palette** (title misspelt "MATERIAD PALETTE"): "Rock A (main)", "Rock B (light)", "Rock C (shadow)",
  "Moss / Leaves 1", "Moss / Leaves 2".
- **Exploded view (parts & assembly):** "Rock A (tall rock)", "Rock B (medium rock)", "Rock C (flat slab)", "Rock D
  (wedge rock)", "Rock E (round rock)"; dashed drop lines and arrows put each rock on its ground shadow, and five loose
  leaf clusters, each with one white flower, drop between them.
- **Parts breakdown (individual meshes):** Rock A (tall rock) with leaf clumps at its foot; Rock B (medium rock) with a
  lime moss pad on top; Rock C (flat slab) with a lime moss pad on its left end and a green clump on its back edge;
  Rock D (wedge rock); Rock E (round rock). D and E are bare.
- **Close-ups:**
  - "Rock / Plant Junction": two big rock faces with a leaf cluster and one white flower in the gap, two small stones
    at its foot.
  - "Slab Thickness": "Uniform thickness (slab)", an arrow across the slab's side band.
  - "Underside": an elongated faceted stone seen from below: "Flat underside (no details)".
- **VFX overlay (optional):** the assembled scatter on a soft olive-grey ground disc: "Simple contact shadow (VFX - not
  geometry)".
- **Modeling notes:**
  - "Five separate meshes: 3 rock pieces (A, B, C) + 2 small stones (D, E)."
  - "Broad, low-poly, flat-shaded faces. Keep forms chunky and readable."
  - "Clean, simple solid colors. No texture noise. Match FLINTBORN style." (but see §3.9)
  - "Plants and flowers are geometry (separate from rocks). Keep forms simple."
  - "Flat underside for ground placement. Consistent thickness on slab."
  - "Parts can be reused and recombined for natural variation."
- **Game context:** a ground-detail prop. The old kit sheet **W01 already has a Pebble Scatter row** (the same
  subject, passed 8/10, exported to `art/roblox/kit/W01/`) and owns `PebbleScatter`, `PebbleFlatSlab`, `Pebble`,
  `PebbleWedgeRock`, `PebbleRoundRock`, `PebbleSmallStone` and `PebbleScatterSparse/Medium/Dense` (§8). Its sizes, from
  `art/roblox/kit/W01/manifest.json` (Roblox X × Z × Y, re-ordered here to W × D × H):

  | W01 piece | W × D × H (studs) | Tris |
  | --- | --- | --- |
  | `PebbleScatter` (hero) | 16.6 × 11.8 × 3.1 | 3656 |
  | `PebbleFlatSlab` | 7.4 × 4.2 × 1.8 | 210 |
  | `PebbleWedgeRock` | 3.2 × 2.8 × 2.6 | 182 |
  | `PebbleRoundRock` | 3.2 × 2.9 × 2.0 | 224 |
  | `Pebble` | 1.6 × 1.2 × 1.1 | 32 |
  | `PebbleSmallStone` | 1.1 × 0.9 × 0.7 | 32 |
  | tall rock (in the hero only) | 3.2 × 2.9 × 3.1 | — |

  W01's builder (`art/blender/kit/mcp/w01.py`, `scatter_piece`, `pebble_hero`) and goals file
  (`art/blender/renders/kit/W01/pebble_scatter_goals.md`) record two lost verifier rounds: a "smooth lozenge" slab, an
  egg-shaped round rock, heavy wedge moss, loose clumps and wrong piece counts. Read the goals file before modelling.

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is
`#FCF8F0` (252, 248, 240), tolerance 10. The masks are `cls()` in `m.py` (HSV):
- **R, rock:** hue ≤ 48° or ≥ 190°, sat 0.04–0.42, v 0.22–0.985, and not G/F/B. Lit faces are warm peach (hue 19–27°),
  shaded faces cool lavender-grey (hue 255–345°, B ≥ R > G); both are R.
- **G, green:** hue 48–150°, sat ≥ 0.28, v ≥ 0.15. Moss pads and leaf clusters; split by position with the moss boxes
  in `shares.py`.
- **F, flower:** white petals (sat < 0.10, v ≥ 0.96) and golden centres (hue 25–48°, sat ≥ 0.55, v ≥ 0.7).
- **B, ground shadow:** sat < 0.06, v 0.55–0.955: a cool neutral grey (`#B4B6BA`, B > G > R). **Treated as
  background**: it is not in any silhouette, profile or share below.
- **O, other:** dark leaf creases, outlines and anti-aliasing; in silhouettes, not in shares (2.6–4.1 %).

**Cell boxes** (from the frame lines, `lines.py`): f34 (14,160,518,452), r34 (521,162,1009,452), front (14,485,270,664),
side (272,485,510,664), rear (513,485,760,664), top (763,476,1009,664), exploded (14,734,728,1158), parts breakdown
(14,1180,728,1302), close-ups junction (731,734,1009,893), slab (731,918,1009,1066), underside (731,1100,1009,1340),
VFX overlay (566,1366,1009,1495). Swatch boxes 30 × 32 px at x 714 / 775 / 836 / 897 / 957, y 52–84.

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m038_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14 with Pillow and numpy; no scipy, so `m.py` has
its own `label()`).
- **Helpers:** `m.py` (masks `cls()`, cell boxes `V` / `X`, swatches `SW`, `label()`, `preview()`), `zoom.py` (crop +
  upscale), `lines.py` (frame lines).
- **Measurements:** `measure.py` → `measure_out.txt` and `bb.json` (silhouettes, shares, rock and green components,
  white blobs, top/bottom profiles); `rocks.py` → `rocks_out.txt` and `rocks.json` (per-rock boxes in every cell, w/h,
  outline corners, width per height, bottom rise); `facets.py` → `facets_out.txt`, `facets.json`, `facets_*.png`
  (flat-facet segmentation, M035 method); `shares.py` → `shares_out.txt` (per-rock and moss/leaf shares);
  `flowers.py`; `vfxdisc.py` (the contact-shadow disc).
- **Colour:** `samp.py` → `samp_out.txt` (swatches; median / lit / shade quartiles per rock, third, moss pad, leaf
  cluster, flower and shadow; deciles).
- **Crops:** `f34.png`, `r34.png`, `row2.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `parts.png`,
  `cu.png`, `vfx.png`, `pal.png`, `notes.png`; mask previews `cls_*.png`.
- **Zooms:** `z_eA.png`, `z_eB.png`, `z_eC.png`, `z_eDE.png` (exploded rocks), `z_parts1.png`, `z_parts2.png`,
  `z_junc.png`, `z_cuS.png` (slab edge), `z_cuU.png` (underside), `z_f34_back.png` (the big back cluster),
  `z_f34_right.png` (B, its moss pad, E, K4, K5), `z_f34_left.png` (C's left end, moss pad, L1/L2), `zfrontB.png`,
  `zE.png`.
- **To run the scripts on our renders:** point `R` (in `m.py`) at the render, set `P` to its background colour, set the
  boxes in `V` / `X` to the render cells and the per-rock boxes in `rocks.py` / `shares.py` to our rock positions, and
  re-run `measure.py`, `rocks.py`, `facets.py`, `shares.py` and `samp.py`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a ground-detail scatter set of five rocks with plants). Hero budget 4000 tris, each
  part under 1000. The plan in §4.3 lands at about 2100–2500.
- **Overall read (check this first).** A **loose ring of five warm grey-pink faceted rocks** round an open patch of
  ground, with chunky round-leaf plant clusters and white five-petal flowers tucked at their feet:
  - **C, a big low flat slab** front-left (the largest piece, 35 % of the hero silhouette): a near-flat broad top,
    a uniform side band, a protruding front corner, a **lime-yellow lobed moss pad on its back-left corner**;
  - **A, a tall blunt rock** behind, right of C's centre (the tallest; a blunt egg/bullet with its crown left of
    centre);
  - **B, a medium boxy rock** at the right, mid-depth, with a **lime star-shaped moss pad** draped over its top;
  - **D, a chunky wedge rock** at the front right, in front of the open patch;
  - **E, a tiny pebble** in the gap between A and B.
  - Seven leaf clusters (plus one small lime clump) and six flowers: a big two-flower mound between C's back edge
    and A, two clusters hugging C's left end, single-flower clusters in the open patch, at D's left and right, and
    between A and B.
  - Hero shares: rock 72.0 % (A 16.9, B 8.4, C 35.3, D 10.3, E 0.7), green 26.9 % (moss pads 5.5, leaves 21.3),
    flowers 1.1–1.4 %.
- **Focal silhouettes, in order:**
  1. A's blunt tower behind the slab: the only piece taller than wide-ish (screen W : H 0.98, the hero's top
     profile peak at f .50–.60).
  2. C's long low slab across the left 55 % of the hero, its flat top seen from above, its front corner pointing at
     the camera.
  3. The ring of separate pieces with ground showing between them: no piece touches another by more than a graze.
  4. The plant clusters and flowers at the feet, and the two lime moss pads on B and C.
- **Target size: 11.1 W × 8.9 D × 3.0 H studs** (A's crown 3.0 = 0.55 × the 5.5-stud character: hip height).
  Tolerances: W ±0.5, D ±0.6, H ±0.2. Decision §8.1.
  - **How it was derived.** The sheet has no character. The front three-quarter, front and top cells are one aligned
    composition (§3.1); with the f34 camera at e ≈ 30–33° the per-rock screen boxes, bottoms and tops agree within
    0.02–0.03 H (§2.1). A's crown height fixes the scale: **f34 40.2 px/stud, front cell 20.1, top cell 19.1**.
  - **Why this size.** A tall rock at hip height, a slab you can step onto (1.5 high), stones from knee height down
    to a 0.7 pebble: "use to detail ground", one size class below M035's boulder (rock 9.0 × 6.4) and with the same
    tall-rock height as W01's scatter (3.1). At this size the leaves are 0.4–0.65 long and the flowers 0.37–1.0
    across, readable against a 5.5-stud character. The scatter is tighter than W01's (16.6 × 11.8) because the sheet's
    pieces sit close.
- **Build frame:** front −Y, +X right, ground z 0, origin = the dressed footprint's centre on the ground. Stage 2
  re-centres the hero on its bbox bottom centre.

### 1.2 Measured views (`measure.py`, `rocks.py`, `shares.py`)

| View (box) | Silhouette bbox (px) | W : H | Rock R | Green G (moss / leaves) | Flower F | Rocks visible | Clusters | Flowers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (14,160,518,452) | 45–491 × 164–435 | **1.643** | 72.0 % | 26.9 % (5.5 / 21.3) | 1.1 % | 5 | 8 + 2 pads | 6 |
| Rear three-quarter (521,162,1009,452) | 558–982 × 183–430 | 1.714 | 74.4 % | 24.7 % | 0.9 % | 4 (5th hidden) | 5 | 3–4 |
| Front (14,485,270,664) | 35–256 × 527–655 | 1.721 | 71.7 % | 26.6 % (4.3 / 22.1) | 1.7 % | 5 | 8 + 2 pads | 6 |
| Side (272,485,510,664) | 297–493 × 537–641 | 1.876 | 78.0 % | 20.9 % | 1.1 % | 4 (C, A, two small) | 4 | 2 |
| Rear (513,485,760,664) | 523–741 × 527–643 | 1.872 | 70.6 % | 28.0 % | 1.3 % | 4 | 4 | 2–3 |
| Top (763,476,1009,664) | 777–990 × 482–659 | 1.202 | 69.0 % | 30.0 % (8.1 / 21.7) | 1.0 % | 5 | 8 + 2 pads | 6 |
| Exploded (14,734,728,1158) | 57–660 × 750–1130 | 1.585 | 77.4 % | 21.3 % | 1.3 % | 5 | 5 loose + attached | 5 |
| Parts breakdown (14,1180,728,1302) | 41–685 × 1189–1291 | — | 82.2 % | 16.9 % | 0.9 % | 5 | attached | 0 |

- Shares are of R + G + F; the ground shadow (B) is background. **Verifier tolerance:** shares ±4 points (moss ±2,
  flowers ±0.6, each rock ±2.5, C ±4); positions ±0.04 of W/H unless stated. Flower counts were made by eye on the
  zooms (the automatic `flowers.py` misses pale centres); cluster counts from the green components plus the zooms.

**Per-rock boxes** (fractions of each cell's silhouette: f across, h up; px are sheet px):

| Rock | f34 box (f, h) | f34 px | front box | top box (h = back) | Screen w/h f34 / parts / exploded |
| --- | --- | --- | --- | --- | --- |
| A tall | f .43–.70, h .53–1.00 | 125 × 128 | f .46–.75, h .47–.99 | f .44–.70, h .62–.99 | 0.98 / 0.74 / 0.83 |
| B medium | f .74–1.00, h .35–.63 | 115 × 77 | f .76–1.00, h .30–.54 | f .74–1.00, h .43–.71 | 1.51 / 1.15 / 1.11 |
| C slab | f .07–.61, h .07–.57 | 242 × 137 | f .09–.59, h .08–.53 | f .08–.61, h .08–.62 | 1.77 / 1.93 / 1.79 |
| D wedge | f .59–.83, h .00–.32 | 109 × 86 | f .60–.81, h .00–.31 | f .59–.81, h .01–.24 | 1.27 / 1.07 / 1.05 |
| E pebble | f .68–.74, h .44–.52 | 28 × 22 | f .68–.75, h .36–.46 | f .68–.74, h .56–.62 | 1.27 / 1.14 / 1.12 |

- Per-rock shares of the silhouette (`shares.py`): **f34** A 16.9, B 8.4, C 35.3, D 10.3, E 0.7; **front** 20.2 / 8.0 /
  32.0 / 9.8 / 0.9; **top** 14.8 / 7.4 / 38.2 / 7.5 / 0.6. Moss pads f34 5.5, front 4.3, top 8.1 %.
- The f34, front and top **X fractions agree within 0.03 for every rock**: one aligned composition (§3.1).

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .31 | .44 | .50 | .54 | .55 | .58 | .75 | .81 | .83 | .86 | .98 | .99 | .96 | .89 | .74 | .76 | .75 | .68 | .67 | .61 | .45 |
| Front | .28 | .41 | .46 | .50 | .50 | .52 | .54 | .79 | .76 | .80 | .90 | .98 | .98 | .95 | .86 | .67 | .71 | .70 | .62 | .57 | .41 |
| Top (h = back) | .43 | .54 | .56 | .64 | .66 | .66 | .81 | .87 | .88 | .90 | .97 | .99 | .97 | .92 | .84 | .85 | .83 | .72 | .71 | .67 | .58 |
| Side | .06 | .31 | .40 | .46 | .47 | .52 | .64 | .62 | .56 | .69 | .72 | .90 | .96 | .99 | .96 | .92 | .86 | .66 | .47 | .31 | .08 |
| Rear | .14 | .35 | .47 | .49 | .53 | .57 | .70 | .72 | .65 | .68 | .87 | .95 | .99 | .94 | .89 | .74 | .66 | .36 | .35 | .30 | .15 |
| r34 | .36 | .55 | .56 | .60 | .64 | .71 | .74 | .77 | .89 | .97 | .99 | .95 | .89 | .72 | .77 | .81 | .70 | .62 | .61 | .58 | .35 |

- f34 reading: f .05–.25 is C's top plus L1 and the lime pad (.44–.58); the step at f .30 is the back cluster K1
  (.75–.86); f .50–.60 is A's crown; f .70–.80 is K5 and B's moss pad (.74–.76); f .85–1.0 is B (.61–.68).

**Bottom profiles** (lowest silhouette pixel; ground contacts):

```
f34    .25 .16 .17 .15 .11 .09 .08 .08 .11 .14 .16 .05 .04 .01 .00 .01 .04 .36 .14 .14 .41
front  .26 .16 .15 .13 .10 .09 .08 .09 .10 .13 .15 .03 .04 .01 .01 .02 .08 .12 .12 .12 .35
top    .43 .25 .23 .20 .16 .12 .11 .08 .12 .15 .19 .05 .04 .03 .01 .02 .06 .16 .16 .22 .51
```

- The V at f .05–.50 is C's front corner (lowest at f .30–.35); f .55–.80 is K3 and D (the front-most piece, h 0); f
  .85 is the gap between D and K4 (.36 in the f34).

**Green components (f34)** (`measure.py`; f across, h up): L1 + L2 + moss pad MC f .00–.21, h .16–.55 (94 × 106 px);
K1 upper f .24–.45, h .55–.84 (95 × 79); K1b (lime) f .42–.56, h .47–.68; K3 f .54–.62, h .03–.15 (34 × 33); K2 f
.58–.68, h .31–.44 (42 × 36); K5 f .70–.81, h .62–.78 (50 × 44); MB (B's pad) f .80–.96, h .48–.68 (70 × 55); K4 f
.86–.99, h .13–.34 (61 × 58). The top view shows the same set (L strip along C's left end f .01–.15; K1 f .30–.56; K5 f
.69–.81; MB on B; K2 f .58–.67; K4 f .84–.94; K3 f .56–.63).

**Flowers** (white, five broad round-tipped petals, a golden domed centre): f34 6 (K1 ×2 at f .39 h .72 (back) and
f .43 h .63 (front); K5 f .75 h .71; K2 f .63 h .39; K3 f .58 h .11; K4 f .94 h .24). Diameters on the f34 zooms: K1 front 40 px (1.0
stud), K1 back 32 px (0.8), K4 24 px (0.6), K5 18 px (0.45), K2 17 px (0.42), K3 15 px (0.37). Front 6, top 6, side 2,
rear 2–3, r34 3–4, exploded 5 (one per loose cluster), parts 0.

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, governs; `f34.png`, `z_f34_*.png`).** An elevated **front** view (az 0, e ≈ 30–33°,
§3.1), not a rotated three-quarter.
- **C (flat slab):** 242 px across (6.0 studs of X extent), its top a quiet near-flat plane broken into broad
  shallow facets, lit pale (`#E1CABF`); the side band a row of big near-vertical faces, the left ones in lavender
  shade; the **front corner** at f .30 (0.43 of the slab from its left end) is the lowest point of the hero's left
  half. A thin top bevel and a lower chamfer tuck into the flat underside (`z_cuS.png`). The lime pad MC hangs over
  its back-left corner; L1 rises against its left end, L2 sits at its front-left foot.
- **A (tall rock):** a blunt egg/bullet, widest at h .35–.55, crown left of centre (top profile peak f .50–.55 of the
  hero = 0.2–0.5 of A's own width), a long lit right flank of tall sliver facets, a shaded left flank. Its foot is
  hidden behind K1 and C.
- **B (medium rock):** a boxy rounded block, a large dark front-left face, a small sloping top mostly covered by the
  moss pad MB (a star of 7–9 pointed lobes, lime-yellow, draping over the right-front shoulder).
- **D (wedge rock):** a chunky faceted block, its apex over the back-left third, a big top facet sloping down to the
  front-right, steep shaded left face. No moss.
- **E (pebble):** a tiny squat stone at f .68–.74 in the A–B gap, its cast shadow to the left.
- **Plants:** K1 a big mound (≈ 16–20 leaves, 2 flowers) between C's back edge and A's left foot; K1b a small lime
  clump at A's front-left foot spilling onto C's back-right top; K5 behind the A–B gap (1 flower); K2 in the open
  patch right of C (1 flower); K3 at D's left (1 flower); K4 at D's right (1 flower); L1 and L2 at C's left end (no
  flower). Leaves are broad, round-tipped (spatulate), thick, cupped, two-tone along a midrib crease.
- **Spacing pattern:** the rocks form a loose ring round an open patch at about (1.4, −0.7) (K2 sits there): C–D gap
  0.2–0.5, C–B 1.6–2.2 (K2), B–D 2.0–2.6 (K4 beside it), A–B 0.3–0.6 (E and K5 in it), A–C 1.5–2.1 (K1 fills it). Ground
  shows between every pair of rocks in the f34.
- **Ground shadow:** soft cool grey to the left and behind (light from the front-right); background.

**Front (`front.png`).** The f34 drawing again at a slightly lower elevation (§3.1): every rock's X fraction within
0.03; B and E sit 0.05–0.08 H lower; W : H 1.721. Same 5 rocks, 8 clusters + 2 pads, 6 flowers.

**Top (`top.png`; image top = back).** Also the same composition, from high up (e ≈ 65–75°: A's front face and C's
front-left side band still show): C a big irregular hexagon (front vertex at its bottom, a straight back edge, the lime
pad at its back-left corner and the L leaf strip down its left end); A at the top centre-right; B at the right with MB
covering half its top; D at the bottom; E a speck left of B. The plants ring C's back and left and dot the open patch.

**Side (`side.png`).** Labelled "SIDE VIEW (RIGHT)", e ≈ 8°. Long low C at the left (front), tall A right of centre
(back), a cluster with a flower at A's front foot, E as a pebble, a low rock with a cluster at the far right, a small
moss tuft on A's left shoulder. **A compact re-composition** (§3.2): it does not show D or B where the plan puts them,
and its W : H (1.876) implies a scatter about half as deep as the front/top cells show.

**Rear (`rear.png`).** e ≈ 12°. A in the centre-right, a rounded rock with a big lime smear at the left (B's moss pad,
mirrored correctly), a low slab across the front centre, a small rock at the right, clusters at both ends. **A compact
re-composition** (§3.2): W : H 1.872 against our layout's ≈ 2.3.

**Rear three-quarter (`r34.png`).** e ≈ 25°. A at the back centre, a big plain rounded rock at the left, the long slab
at the right with clusters at its ends, a small rock at the front, a big flowered cluster in the A–slab gap. Matches a
camera at the **back-right** (az ≈ 150) with B and D merged into the left rock and E as the front rock, but the pieces
are drawn closer together (§3.2).

**Close-ups.**
- **Rock / Plant Junction** (731,734,1009,893): two big rock faces (big flat facets, a lit one and a shaded one) with a
  10–12-leaf cluster and one flower in the gap, and two small stones (≈ 0.4–0.6 studs) at its foot. Leaves touch the
  rocks but don't cut into them.
- **Slab Thickness** (731,918,1009,1066), `z_cuS.png`: the slab's end: a narrow top bevel (≈ 0.10 T, about 35°), one
  big near-vertical side face (≈ 0.70 T, leaning out 5–10°), a lower chamfer (≈ 0.20 T, 35–45° inward) to the flat
  underside. "Uniform thickness": the band height is the same all round.
- **Underside** (731,1100,1009,1340), `z_cuU.png`: an elongated faceted stone from below: one big flat bottom face
  (51 % of the visible stone, `facets.py`) inside a ring of 8–10 rim faces. "Flat underside (no details)".

### 1.4 Parts (Exploded View, Parts Breakdown, close-ups)

Scale: the exploded and parts rows draw D and especially E larger against the others than the hero does (E/D 0.69 in
the parts row and 0.74 in the exploded, 0.26 in the hero). **The hero governs every size** (§3.3); the exploded and
parts rows give shapes.

All five rocks: `K.hull_rock(..., keep_bottom=True)` from jittered point rings, flat bottom (floor-cut at z 0), flat
shading, no subdivision, no bevel modifier. WorldModeling §12.1: an uneven 5–8-sided footprint, 2–3 height rings, ring
centres offset, a few large side faces and a quieter top.

#### Rock A, tall rock — exploded (215,745,365,912) 130 × 156 px; parts (54,1189,128,1291) 75 × 102 px; `z_eA.png`

- **Shape:** a blunt egg/bullet: flat base about 0.78 of the max width, widest at h .35–.50, still 0.75–0.8 wide at h
  .7, 0.5–0.55 at h .85, a small blunt crown (2–4 small facets) over the left 0.3–0.45 of the width; the right flank
  a run of long vertical sliver facets, the left flank broader facets. 13 outline corners (parts and exploded).
- **Hero size: 3.1 W × 2.3 D × 3.0 H** (H/W 0.97 from the front, H/D 1.30 from the side: the parts row's narrow 0.74
  is the side-on shape).
- **Construction:** rings `(0.0, 0.80, 7), (0.18, 0.92, 7), (0.42, 1.0, 8), (0.66, 0.90, 7), (0.84, 0.62, 6),
  (1.0, 0.24, 3)`, jitter 0.10–0.12, crown `lean=(-0.30, 0.05)`; then thin one point from the 0.42 and 0.66 rings on
  the front-right so 2–3 long facets form there. **70–110 tris.**
- **Dressing in the part:** two small leaf clumps at its foot (left 8–10 leaves, right 4–6), no flower (parts row).

#### Rock B, medium rock — exploded (407,821,528,928) 120 × 108 px; parts (183,1194,260,1260) 77 × 67 px; `z_eB.png`

- **Shape:** a chunky rounded block: steep, slightly bulging sides, a broad near-flat top (one big top facet about
  0.4–0.5 of W across, sloping 5–10° to the front-right), base 0.85 of W. 12–14 outline corners.
- **Hero size: 2.85 W × 2.4 D × 1.5 H** (h/w 0.53).
- **Moss pad MB:** a star pad of 7–9 lobes (pointed, maple-like, notched), 1.6 × 1.3 across (0.55 of B's width),
  0.10–0.15 thick, a raised centre 0.15–0.25, conformed over the top and draped 0.3–0.45 down the right-front shoulder;
  lime-yellow tops, deeper green in the notches. The exploded and parts copies also show a narrow green moss strip on
  B's shaded left flank (not in the hero; §3.6).
- **Construction:** rings `(0.0, 0.86, 7), (0.25, 0.98, 7), (0.6, 1.0, 7), (0.88, 0.82, 6), (1.0, 0.55, 4)` (the
  flat-ish top ring), jitter 0.08–0.10. **60–90 tris**; MB from `K.moss_slab(lobes=8, notch=0.3)` or `K.drape(lobes=8)`
  conformed with `K.conform(sink=0.03)`: **80–110 tris**.

#### Rock C, flat slab — exploded (81,936,329,1077) 252 × 141 px; parts (325,1191,473,1266) 145 × 75 px; slab and underside close-ups; `z_eC.png`, `z_cuS.png`, `z_cuU.png`

- **Shape:** a low slab of **uniform thickness**:
  - **plan:** an irregular hexagon / heptagon (from the top view): a straight back edge, the left and right ends
    chamfered, a **front vertex at 0.43 L from the left end** so the front is a shallow chevron; L 5.8, D 4.0;
  - **top:** 8–12 broad near-coplanar facets (neighbouring dihedrals 3–12°), the whole top tilted ≤ 4°, highest at the
    back-left; no dome, no lozenge;
  - **edge profile** (all round): top bevel ≈ 0.10 T at ~35°, side face ≈ 0.70 T leaning out 5–10°, lower chamfer ≈
    0.20 T tucking in 0.15–0.30 to the flat underside;
  - **underside:** one flat face (or coplanar triangles) spanning 0.80–0.90 of the top's footprint, no detail.
- **Hero size: 5.8 L × 4.0 D × 1.5 T** (T/L 0.26; screen X extent 6.0 with the yaw).
- **Construction:** not a hull of rings (that rounds it into W01's "smooth lozenge"). Build the plan polygon (7 vertices,
  ±0.15 jitter), and extrude it as four stacked rings: `z 0` at inset 0.22, `z 0.30` at inset 0, `z 1.35` at inset 0
  (+0.05 outward lean), `z 1.5` at inset 0.15; the top cap a fan / triangulation of 8–12 faces with each interior
  vertex lifted 0–0.06 (no dome). Flat bottom cap. **60–100 tris.**
- **Dressing in the part:** the lime pad MC on the back-left corner (1.5 × 1.1, 6–8 rounded lobes, 0.12 thick, draped
  0.3–0.5 over the left end); a 6-leaf green clump on the back edge (K1b-like); a leaf cluster at the left foot.

#### Rock D, wedge rock — exploded (498,962,584,1045) 87 × 83 px; parts (525,1194,585,1251) 61 × 57 px; `z_eDE.png`

- **Shape:** a chunky faceted block with a **tilted top**: apex over the back-left third, a big top facet falling
  20–25° to the front-right, steep left and back faces; 16–22 visible facets of similar size (no dominant face,
  largest region 8–12 %). 11–13 outline corners.
- **Hero size: 2.7 W × 2.3 D × 1.8 H** (h/w 0.67).
- **Construction:** rings `(0.0, 0.85, 6), (0.3, 1.0, 7), (0.65, 0.92, 6), (1.0, 0.45, 4)` with `lean=(-0.25, 0.20)`
  and the top ring's z scaled from 1.0 at the back-left to 0.75 at the front-right (or `tilt` 0.35 rad about the
  front-left/back-right axis before the floor cut), jitter 0.12. **40–64 tris.**

#### Rock E, round rock — exploded (552,1073,616,1130) 64 × 57 px; parts (627,1199,669,1236) 42 × 37 px; hero 28 × 22 px

- **Shape:** a squat pebble, h/w 0.6, one big top facet, 10–14 visible facets, 10–12 outline corners.
- **Hero size: 0.7 W × 0.6 D × 0.42 H.** The parts and exploded rows draw it about 1.8 across (§3.3).
- **Construction:** `K.pebble`/`K.PEBBLE` rings with `keep_bottom=True`, jitter 0.12. **20–32 tris.**

#### Plants (exploded loose clusters (323,1073,389,1130), (341,917,395,962), (353,1016,395,1054), (338,880,385,912); junction close-up)

- **Leaf:** broad, round-tipped spatulate leaves (`K.leaf(shape="round")` or `"disc"`, 16 tris), 0.40–0.65 long,
  width 0.70–0.85 × length, folded along a midrib (fold 0.2) so each shows a lit half and a shaded half, thick (0.04–
  0.05), tips curling down a little. Not pointed, not blades.
- **Cluster:** a rosette from one root in 2–3 tiers (`K.clover(shape="round", tiers=…, young_mat=…)`): low outer
  leaves splayed, inner leaves upright and lighter. Exploded loose clusters 5–7 leaves + 1 flower; K1 16–20 leaves.
- **Flower:** five broad round-tipped white petals (`K.daisy(petals=5)`, petal width 0.6 × length) round a domed
  golden centre (Ø 0.30–0.35 of the flower), sitting on top of the cluster, facing up and a little toward the camera.
- **Moss pads (MB, MC):** separate lobed lime pads, §1.4 B and C.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, origin = the dressed footprint's centre). Derived from the f34
(40.2 px/stud, e 30°: X from screen x, Y from each rock's bottom (front ground point) / sin e) cross-checked with the
top cell (19.1 px/stud); both agree within 0.1 in X and 0.3 in Y.

### 2.1 Rocks

| Piece | Centre (x, y), base z | Size W × D × H | Yaw | Sheet evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| C flat slab | (−1.73, −1.60), −0.04 | 5.8 × 4.0 × 1.5 | −8° (right end forward) | f34 f .07–.61, front corner f .30 h .07; top f .08–.61 | top 1.5; back edge at y ≈ +0.4 |
| A tall rock | (+0.72, +3.30), −0.05 | 3.1 × 2.3 × 3.0 | +5° | f34 f .43–.70, h .53–1.00; top f .44–.70 | crown at x ≈ +0.25 (left of centre) |
| B medium rock | (+4.12, +1.30), −0.05 | 2.85 × 2.4 × 1.5 | +15° | f34 f .74–1.00, h .35–.63; top f .74–1.00, h .43–.71 | MB on its top |
| D wedge rock | (+2.39, −3.30), −0.05 | 2.7 × 2.3 × 1.8 | −10° | f34 f .59–.83, h .00–.32 (the front-most piece) | apex over its back-left third |
| E round rock | (+2.25, +1.75), −0.03 | 0.7 × 0.6 × 0.42 | 30° | f34 f .68–.74, h .44–.52 | 0.1 off B's left and A's front-right foot |

- **Expected extents:** rocks X −4.65 … +5.55, Y −4.45 … +4.45; with L1/L2 X −5.55; dressed **11.1 × 8.9 × 3.0**.
- **Checks on the renders** (render frame = sheet frame, floor hidden):
  - **f34_sheet (0, 32):** W : H 1.58–1.71 (sheet 1.643); each rock's box at §1.2 ± 0.04; per-rock shares A 16.9 ±
    2.5, B 8.4 ± 2.5, C 35.3 ± 4, D 10.3 ± 2.5, E 0.7 ± 0.4; top profile within ±0.07 (mean ≤ 0.04); bottom profile
    with C's front corner the lowest point of f .20–.45 and D at h 0.
  - **front_sheet (0, 28):** W : H 1.65–1.79 (sheet 1.721); rock boxes at §1.2 ± 0.05; profile ±0.08.
  - **top_sheet (0, 72):** W : H 1.12–1.28 (sheet 1.202); rock boxes ± 0.05; C 38.2 ± 4 % of the silhouette.
- **Check of self-consistency** (how the numbers were derived; `rocks.json`): at e 30 these sizes and positions
  reproduce the f34's B bottom h .35 (pred .35), C top .57 (.55), D top .32 (.32), A bottom .53 (.51), E .44–.52
  (.45–.55), W : H 1.72 at e 30 and 1.65 at e 33.

### 2.2 Rock-shape targets (binding; check with `M.audit`, own bmesh code and `facets.py` on the parts shot)

The M023 lobes failed first as "soccer-ball" facets; W01's slab failed as a "smooth lozenge" and its round rock as an
egg. These are measurable:

| Target | A tall | B medium | C slab | D wedge | E pebble |
| --- | --- | --- | --- | --- | --- |
| Mesh tris (after floor cut, before refine) | 70–110 | 60–90 | 60–100 | 40–64 | 20–32 |
| Facets visible in one parts-shot view (eye) | 26–34 | 20–26 | 22–28 (top 8–12, band 8–12) | 16–22 | 10–14 |
| `facets.py` regions ≥ 0.4 % (thr 7) on the parts shot (sheet parts / exploded) | 11–16 (11 / 16) | 8–12 (12 / 11) | 9–13 (13 / 12) | 13–18 (14 / 16) | 8–14 (8 / 14) |
| Largest region, share of the rock's projected area (sheet parts / exploded) | 0.14–0.25 (.25 / .17) | 0.14–0.20 (.14 / .20) | 0.24–0.33 (.25 / .32) | 0.08–0.12 (.08 / .09) | 0.04–0.09 (.04 / .08) |
| Height / width (true) | 0.97 (X), 1.30 (Y) | 0.53 | T/L 0.26, T/D 0.37 | 0.67 | 0.60 |
| Flat base, share of max width in X and Y | 0.75–0.82 | 0.82–0.90 | 0.80–0.90 of the top footprint | 0.78–0.85 | 0.65–0.75 |
| Widest section | h .35–.50 | h .40–.65 | h .20–.90 (the band) | h .30–.50 | h .30–.45 |
| Outline corners from the parts camera | 12–14 | 11–14 | 12–14 | 11–13 | 10–12 |

- **Irregular triangles, not a pattern** (A, B, C, D): triangle area CV ≥ 0.6; edge length CV ≥ 0.35; vertex valence
  3–8, mean 5–6.5, no single valence on more than 45 % of the verts; at least 15 % of triangles with a smallest angle
  under 25° (the long sliver facets on A's right flank and C's band); no pentagon/hexagon faces and no ring of 5–6
  near-equal triangles round a vertex repeated more than twice. Never `primitive_ico_sphere`, never a Fibonacci-normal
  dual, never subdivision plus displacement. E is exempt from the CV and valence rules (too few faces).
- **C's top:** 8–12 faces with normal z > 0.97 covering ≥ 85 % of the top's area; no top face steeper than 12°
  except the bevel ring.
- **Width per height on the parts shot** (screen, rock only; h .05 → .95), to match within ±0.08:

```
A  .32 .53 .71 .88 .95 .88 .77 .69 .56 .27
B  .47 .73 .87 .95 .99 .88 .91 .87 .75 .10
C  .26 .57 .78 .87 .88 .96 .91 .80 .62 .49
D  .46 .67 .80 .95 .92 .89 .87 .74 .59 .43
E  .38 .81 .93 .98 1.0 .90 .88 .79 .62 .43
```

### 2.3 Plants and moss pads (instances)

| Piece | Centre (x, y), base z | Kind / size | Leaves | Flowers (Ø) | Sheet evidence | Seat |
| --- | --- | --- | --- | --- | --- | --- |
| MC lime pad | (−3.85, −0.40) on C's top | pad 1.5 × 1.1, 6–8 rounded lobes, 0.12 thick | — | — | f34 f .08–.21, h .45–.58; top left corner | conformed; drapes 0.3–0.5 over C's left end |
| MB lime pad | (+4.25, +1.45) on B's top | star pad 1.6 × 1.3, 7–9 pointed lobes, 0.12 thick | — | — | f34 f .80–.96, h .48–.68; top: half of B's top | conformed; drapes 0.3–0.45 down B's right-front shoulder |
| K1 back mound | (−1.60, +1.40), 0 | w 2.6 × 2.0, top 1.4 | 16–20 | 2 (1.0 front, 0.8 back) | f34 f .24–.45, h .55–.84; flowers f .43 h .63 / f .39 h .72 | behind C's back edge, against A's left foot; front leaves lie on C's back top |
| K1b lime clump | (+0.20, +1.90), 0 | w 1.1, top 0.8 | 5–6 (`leaf_young`) | — | f34 f .42–.56, h .47–.68 | A's front-left foot; leaves spill onto C's back-right top |
| K5 | (+2.85, +2.75), 0 | w 1.2, top 0.7 | 7–8 | 1 (0.45) | f34 f .70–.81, h .62–.78; top f .69–.81 | in the A–B gap behind E |
| K2 | (+1.40, −0.65), 0 | w 1.0, top 0.55 | 6 | 1 (0.42) | f34 f .58–.68, h .31–.44 | the open patch, right of C's right end |
| K3 | (+0.85, −3.70), 0 | w 0.85, top 0.5 | 5–6 | 1 (0.37) | f34 f .54–.62, h .03–.15 | at D's front-left corner |
| K4 | (+4.55, −2.30), 0 | w 1.5, top 0.8 | 8–10 | 1 (0.6) | f34 f .86–.99, h .13–.34; top f .84–.94 | right of D |
| L1 | (−4.75, −0.45), 0 | w 1.5, top 1.7 | 8–10 | — | f34 left group (sheet 61–96, 314–342) | against C's left end, rising above its top under MC |
| L2 | (−4.50, −1.95), 0 | w 1.7, top 0.8 | 10–12 | — | f34 left-front group (sheet 59–111, 349–392) | C's front-left foot |

- **Counts:** 8 leaf clusters (7 plus K1b) + 2 moss pads, about 72–86 leaves, 6 flowers. **f34_sheet must show** 5
  rocks, 8 ± 1 green groups (K1 and K1b may merge), 2 pads, 6 ± 1 flowers; the ground showing between every pair of
  rocks.
- **Seats:** roots at z 0–0.05; leaves may touch rocks but cut no more than 0.05 into them; pads conformed with sink
  0.02–0.04, never floating; tall clusters (K1, L1) lean 10–20° onto their rock.

## 3. View conflicts and resolutions

### 3.1 The front three-quarter, front and top cells are one aligned composition (front view, not 3/4)

- **Evidence.** Every rock's X fraction agrees within 0.03 across the three cells (§1.2 table); the same 8 clusters and
  6 flowers in each; the VFX overlay draws it a fourth time. With the sizes in §2.1 the f34's bottoms and tops are
  reproduced within 0.02–0.03 H at e 30.
- **Elevation is uncertain:** W : H gives e ≈ 33 for the f34 and 30 for the front; B's and E's bottoms give 30 and
  22–25. The top cell is from about 65–75° (A's front face and C's front side band show).
- **Resolution.** Compare the f34 cell with **`f34_sheet (0, 32)`** (probe 28 / 32 / 36 once, keep the smallest
  top-profile error and record it), the front cell with **`front_sheet (0, 28)`** (probe 24 / 28 / 32), the top cell with
  **`top_sheet (0, 72)`** (probe 64 / 72 / 80). The kit `front34`, `front` and top (0, 89) are self-consistency only.

### 3.2 Side, rear and rear three-quarter are compact re-compositions ("same configuration" notwithstanding)

- **Evidence.**
  - Side (from +X, screen right = back): the plan puts D (the front-most piece) at the far left in front of C and B
    (closest to the camera) in front of A; the cell draws neither there, only two small stones at A's foot. Its W : H
    1.876 against ≈ 2.2–2.6 for our layout.
  - Rear (from +Y, screen right = the model's left): B with its lime pad at the left is right, but the slab is drawn in
    the foreground (it is the front-most piece and should be farthest) and a small rock appears at the right. W : H
    1.872 against ≈ 2.3.
  - r34: fits a back-right camera (az ≈ 150) with B and D merged into one plain rock at the left and E in front, but
    pieces overlap more than the plan allows; B's pad is not drawn.
- **Resolution.** The f34 / front / top layout governs. Render **kit `side (90, 8)`**, **`rear_sheet (180, 12)`** and
  **kit `rear34 (152, 12)`** plus an extra **`r34_sheet (150, 25)`**, and judge them loosely: A the tallest and bluntest,
  C long and low with its lime pad, B with its pad, D and E present when not hidden, flowers present, shares ±6. Record
  W : H, positions and counts in these three as known misses.

### 3.3 Part sizes: exploded and parts rows against the hero

- **Evidence.** Width relative to C: hero A .52, B .48, D .45, E .12; parts row A .52, B .53, D .42, E .29; exploded A
  .52, B .48, D .35, E .25. A and B agree; E is drawn 2–2.5× larger in the rows than in the hero; D varies ±15 %.
- **Resolution.** The hero governs: E is a 0.7 pebble and the `StoneScatterRoundRock` part is that same mesh; D is 2.7.
  Record the parts row's larger E as a known miss (§8.4 offers the alternative).

### 3.4 Rock A's proportions: broad in the hero, narrow in the rows

- **Evidence.** Screen w/h: f34 0.98, front 0.94, top 0.85; parts 0.74, exploded 0.83; the side cell's A about 0.8.
- **Resolution.** One rock, wide in X (3.1) and narrow in Y (2.3): the hero sees its broad face, the side sees 0.77,
  and the parts row matches the side-on shape. Render the A part from the front and from the side in the parts shot.

### 3.5 Labels against the rocks' look

- "D (wedge rock)" is a chunky lumpy block in the rows; the hero's D shows the tilted top. Build the tilt (§1.4).
- "E (round rock)" is a squat faceted pebble, not a ball (h/w 0.6, flat top facet).
- "Five separate meshes" counts the rocks; plants are separate geometry too (§8.6).

### 3.6 Extras drawn in only one cell

- A moss tuft on A's left shoulder (side only), a lime smear on B's left flank (exploded, parts, rear), an olive smudge
  on D's shaded face (exploded), two small stones at the plant's foot (junction close-up only). The hero, front and top
  show none of them. **Resolution:** leave them out (the hero governs; "5 pieces"); record as known misses.

### 3.7 Palette names against the renders

- "Rock A (main)" `#9A98A3` is a **cool lavender grey with B > R > G** (251°, 0.07): it equals the rendered shade faces
  (`#6C656D`–`#776E72`, hue 290–340°), i.e. the cool sky fill, **not a paint colour**. Using it as the main key gives
  the mauve rocks that failed M031 round 1.
- "Rock C (shadow)" `#C0A799` (22°, 0.20) is closest to the rendered medians (`#C8AB9C`–`#CDAFA1`); "Rock B (light)"
  `#D1BAAE` (21°, 0.17) is the lit slab top / upper-face tone.
- "Moss / Leaves 1" `#8CA108` (68°, 0.95, 0.63) and "Moss / Leaves 2" `#ACC919` (70°, 0.88, 0.79) are the deeper and
  lighter ends of one lime-green family; the renders split it into yellower moss pads and greener leaves (§5.3).

### 3.8 The slab: hull versus extrusion

- A convex hull of rings rounds C's ends and domes its top (W01's "smooth lozenge"). The sheet's slab has a flat top,
  straight bands of uniform height and a front vertex. **Resolution:** build C by extruding its plan polygon (§1.4).

### 3.9 "Solid colors, no texture noise" against the user's blended-colour rule

- The user's rule wins, quietly: broad light patches on the rocks (whole facets), height bands on the pads, tiers on the
  leaves, low Tint. No per-triangle confetti.

### 3.10 Ground shadow

- A soft cool grey (`#B4B6BA`, B > G > R) to the left of and behind each piece in every view: lighting, background in
  every measurement, not modelled. The **VFX overlay's** olive-grey disc is a separate, optional effect (§7.2).

## 4. Construction plan (stages 1–3)

1. **Parts first,** each from its own function and checked against its cells:
   - `tall_rock()` → `StoneScatterTallRock`: A + its two foot clumps. Compare with the parts row (front and side) and
     the exploded A.
   - `medium_rock()` → `StoneScatterMediumRock`: B + MB. Compare with the parts row B and `z_eB.png`.
   - `flat_slab()` → `StoneScatterFlatSlab`: C + MC + the back-edge clump + the left-foot cluster. Compare with the
     parts row C, the slab-thickness close-up (a low end view) and the underside close-up (from below).
   - `wedge_rock()` → `StoneScatterWedgeRock`: D bare. Compare with the parts row D and the hero's D.
   - `round_rock()` → `StoneScatterRoundRock`: E bare (hero size).
   - `flower_clump()` → `StoneScatterFlowerClump`: a K2-type cluster (6 leaves, 1 flower). Compare with the exploded's
     loose clusters (§8.7).
   - Render a **parts shot** (az 0, e 27) laid out like the parts row (A, B, C, D, E left to right, same scale).
2. **Hero:**
   1. Build the five rocks at their §2.1 places; floor-cut each at z 0 (`m004.floor_cut`) for flat bottoms.
   2. Paint the rocks (stage 4 needs the face lists; keep the original facet ids before any refine).
   3. Build MB and MC, conform them to their rocks (sink 0.02–0.04): closed shells resting on the rock (decision §8.6).
   4. Place the 8 clusters and 6 flowers (§2.3).
   5. `M.fix_bowties`, origin at the bbox bottom centre, transforms applied.
3. **Budget** (§4.3): hero about 2100–2500 (limit 4000); each part under 500 (limit 1000). If over, drop hidden back
   leaves of K1 and L1 first; never thin a rock below its §2.2 minimum.
4. **Placeholder keys** (stage 1): `m038_rock`, `m038_moss`, `m038_leaf`, `m038_petal`, `m038_pollen`. Stage 4 adds the
   rest (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** five separate warm faceted rocks in a loose ring round an open patch: a big flat slab
      front-left, a tall blunt rock behind, a mossy block at the right, a wedge at the front right, a pebble in the A–B
      gap; round-leaf clusters and white flowers at their feet; two lime pads.
   2. **f34_sheet against the f34 cell:** §2.1 checks (W : H, per-rock boxes and shares, top profile, bottom profile);
      shares R 72.0 ± 4, G 26.9 ± 4 (moss 5.5 ± 2, leaves 21.3 ± 4), F 1.1–1.4 ± 0.6; counts 5 rocks, 8 ± 1 clusters, 2
      pads, 6 ± 1 flowers.
   3. **front_sheet against the front cell:** W : H 1.65–1.79, shares ±4 (R 71.7, G 26.6, F 1.7), per-rock shares A
      20.2, B 8.0, C 32.0, D 9.8, E 0.9 (±2.5, C ±4).
   4. **top_sheet against the top cell:** W : H 1.12–1.28; shares ±4 (R 69.0, G 30.0, moss 8.1); C a hexagon with a
      front vertex and a straight back; the plants on C's back and left, in the open patch and beside D.
   5. **Side, rear, r34:** loosely (§3.2).
   6. **Rock-shape targets** (§2.2), all of them, on each part and on the hero's rocks.
   7. **Parts against their cells** (§4.1); a **slab-end extra** `slab_cu (60, 6)` framed on C's right end against
      the Slab Thickness close-up; an **underside extra** of the FlatSlab part from below (e −35); a **junction extra**
      `junc_cu (−25, 10)` framed on K1 between C and A.
   8. **Hero size** 11.1 × 8.9 × 3.0 (±0.5 / ±0.6 / ±0.2); rocks at §2.1 sizes ±0.15.
   9. **Scale shot:** the hero beside a 5.5-stud character marker (the kit-relative-scale rule).
6. **Stage 2:** every shell closed and manifold: zero non-manifold edges and verts (`nonmanifold_verts` 0), boundary,
   wire and loose elements; no zero-area faces or n-gons; normals outward; no faces under 5° on the slab's bevel and
   chamfer rings (m011 `_tidy` / `_desliver`); no decimation below §2.2.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density (leaves, petals and pads included).

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| A / B / C / D / E | 1 each | 70–110 / 60–90 / 60–100 / 40–64 / 20–32 | 250–400 |
| Moss pads MB, MC | 2 | 80–110 | 160–220 |
| Leaves (round, 16 tris) | 72–86 | 16 | 1150–1380 |
| Flowers (5 petals × 12 + centre ≈ 24) | 6 | 84 | 504 |
| **Hero** | | | **about 2100–2500** (limit 4000) |
| Parts: TallRock / MediumRock / FlatSlab / WedgeRock / RoundRock / FlowerClump | | | about 330 / 200 / 420 / 60 / 30 / 180 (limit 1000) |

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 30 × 32 box inside each)

| Swatch | Box | Hex | HSV | Channel order |
| --- | --- | --- | --- | --- |
| Rock A (main) | (714,52,744,84) | `#9A98A3` | 251°, 0.07, 0.64 | **B > R > G (lavender)** |
| Rock B (light) | (775,52,805,84) | `#D1BAAE` | 21°, 0.17, 0.82 | R > G > B |
| Rock C (shadow) | (836,52,866,84) | `#C0A799` | 22°, 0.20, 0.75 | R > G > B |
| Moss / Leaves 1 | (897,52,927,84) | `#8CA108` | 68°, 0.95, 0.63 | G > R > B |
| Moss / Leaves 2 | (957,52,987,84) | `#ACC919` | 70°, 0.88, 0.79 | G > R > B |

No swatch for the petals or flower centres; they are sampled from the renders below.

### 5.2 Rendered regions (`samp.py`; median / lit quartile / shade quartile)

| Region | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- |
| Rock, whole f34 / front / top | R | `#CDAFA1` / `#CAAE9E` / `#D1B5AA` | `#E4CBBE` / `#E4CABC` / `#E6CDBF` | `#70676B` / `#6F676A` / `#726A70` |
| Rock, whole r34 / side / rear | R | `#CDAE9C` / `#CBAE9E` / `#CBAE9E` | `#E9CBBA` / `#E7CAB8` / `#E7CBBB` | `#75696E` / `#746C72` / `#706B72` |
| **Rock, exploded all / parts all (no cast shadow on them)** | R | **`#C8AB9C` / `#C9AC9C`** | `#E3C8BA` / `#E3C8B9` | `#6C656B` / `#6E666B` |
| Exploded A / B / C / D / E | R | `#C3A394` / `#978685` / `#D1B5A8` / `#B79D93` / `#AF948D` | `#E5C5B1` / `#E0C3B2` / `#E1C8BC` / `#DEC1B3` / `#E6CBB9` | `#6C656D` / `#675F62` / `#766F72` / `#685F62` / `#655E61` |
| Parts A / B / C / D / E | R | `#C3A493` / `#9C8783` / `#D6B9AC` / `#C7AA9D` / `#B9A196` | `#DFBFAC` / `#E0C2B0` / `#E1C7BB` / `#EDD0BF` / `#E7CAB9` | `#6C656E` / `#676060` / `#776E72` / `#6A6265` / `#625A5C` |
| Rock thirds, exploded A (top / mid / bottom) | R | `#DDBFAE` / `#C4A38F` / `#B69B87` | `#F4D8C1` / `#E3C2AA` / `#C7A99A` | |
| Rock thirds, exploded C (top / mid / bottom) | R | `#D6BFB4` / `#D2B3A6` / `#957E7B` | `#DEC6BC` / `#E3CBBE` / `#CFB3A6` | |
| Hero rocks f34 A / B / C / D | R | `#C0A89D` / `#927A73` / `#D5B9AC` / `#C3A698` | `#F4D9C3` / `#D3B7AA` / `#E1CABF` / `#E7CBBB` | `#686469` / `#6A5F5E` / `#756D73` / `#756B6E` |
| Moss pad B: f34 / exploded / parts / front / top | G | `#B6C508` / `#A5BE04` / `#B0C306` / `#BFC708` / `#B4BE07` | `#E0DA0E` / `#D4D206` / `#D8DA0C` / `#E2DC13` / `#DBD60B` | `#758C06` / `#708F05` / `#778F07` / `#93AC05` / `#809006` |
| Moss pad C: f34 / exploded / top | G | `#DCD207` / `#C7C606` / `#CCC307` | `#ECDE09` / `#D2D111` / `#DFCF10` | `#9EA306` / `#5F7F08` / `#869B08` |
| Leaf clusters, exploded loose (3) / junction close-up | G | `#A5BC04` / `#9ABB03` / `#95B505` / `#8FB202` | `#D6D607` / `#C9D70E` / `#CBD60E` / `#BDD005` | `#3C6302` / `#416A03` / `#446204` / `#355402` |
| Leaf clusters, f34 K1 / K4 / K5 / L (in shade) | G | `#81AA03` / `#A0AD04` / `#A3C904` / `#5D7C03` | `#D1D905` / `#E9DD0B` / `#C7DE06` / `#9AC004` | `#275102` / `#547202` / `#355602` / `#355A02` |
| Leaf clumps at A's foot, exploded / parts | G | `#608E03` / `#527806` | `#A7CC05` / `#AFC607` | `#235302` / `#345305` |
| Petals: f34 / exploded / junction | white | `#FEFEFC` / `#FEFEFC` / `#FEFDFC` | `#FFFFFF` | `#F9F2E3` / `#F8F4E4` / `#FBF9FB` |
| Flower centres: exploded / junction / f34 big flower | yellow | `#EEC60E` / `#FAC808` / `#EBAB08` | `#F6D735` / `#FCCD0C` / `#FDDA0C` | `#C49C0A` / `#DFAA07` / `#CA7600` |
| Ground shadow: f34 / exploded | B | `#B4B6BA` / `#C2C2C4` | | |
| VFX contact disc (inner / mid / outer) | — | `#C8C39C` / `#DAD1B1` / `#EEE4D5` | | |

Deciles (dark → light):

```
rock  f34   #655E61 #736A70 #927C76 #A99487 #C3A899 #D3B5A4 #D8BBAC #DBC2B8 #DFC8BD #F1D6C3
rock  expl  #635D5E #6F6870 #857677 #AA9186 #C3A597 #CEB1A2 #D5BAAA #D9C0B4 #E0C5B9 #E9D3C0
green f34   #234402 #3F6902 #597C03 #709204 #8CAC04 #A1BD03 #B8C805 #C9D306 #DCD908 #ECE010
green expl  #2B4903 #436903 #537804 #608505 #789E04 #95B503 #A9C303 #B9CB03 #CAD105 #DADA34
```

### 5.3 How the colour works

**Rocks.**
- **One warm grey-pink stone for all five rocks.** Medians hue 17–23°, sat 0.18–0.25, **always R > G > B** (R − B 35–
  45 levels). The lit faces are peach (`#E3C8B9`, hue 20–24°), the shaded faces cool lavender (`#6C656B`, hue 290–340°,
  B ≥ R > G). That split is the warm key and the cool sky fill: **light, not paint**. Never colour by facing.
- Per-rock medians differ only by how much of each rock is lit: B's (`#978685`) is mostly its shaded front-left face,
  C's (`#D1B5A8`–`#D6B9AC`) its upward top; their lit quartiles agree within 12. One key.
- **Gentle painted signal:** broad light patches on upper faces (the top thirds `#DDBFAE`, `#D6BFB4`; swatch Rock B
  `#D1BAAE`), and slightly deeper warm patches low on the rocks (the bottom thirds' lit quartiles `#C7A99A`,
  `#CFB3A6`), both by a noise field over whole facets. No dark painted foot band; no cool patches.
- **Mauve guard (M031 round 1 and one earlier model):** every rock key must be R > G > B with hue 12–26° and R − B ≥ 30.
  `#9A98A3` ("Rock A (main)") is never a key, not even as a mix.

**Moss pads (MB, MC).**
- **Lime-yellow**: medians hue 57–68°, sat 0.96–0.98, value 0.75–0.86; lit tops nearly pure yellow (`#D4D206`–
  `#E0DA0E`, R ≈ G), notches and the rim deeper (`#708F05`–`#778F07`, hue 70–73°). MC (on the slab, in more light) is
  yellower than MB.
- Per pad: **deep at the rim and notches → moss → sun-yellow on the raised centre and lobe ridges**, by height within
  the pad (a position field).

**Leaves.**
- **Greener and darker than the pads:** medians hue 68–80°, sat 0.95–0.99, value 0.47–0.79; the shade side of each
  leaf deep green (`#355402`–`#446204`, hue 80–86°), inner young leaves yellow-lime (`#C9D70E`, hue 63°). The two-tone
  look of each leaf is mostly its midrib fold in the light.
- **Tiered:** outer low leaves `leaf_deep` mixed 40 %, middle `leaf`, inner upright `leaf_young`. K1b and the clumps at
  A's foot use more `leaf_young` (they read lime in the f34).
- **Flowers:** pure white petals (`#FEFEFC`; shade quartile `#F8F4E4`), a golden domed centre (`#EEC60E`–`#FAC808`; the
  biggest flower's centre is more orange, `#EBAB08`).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

The calibration targets are medians of **unshadowed** rendered regions (the exploded parts, the parts row and the
close-ups), not swatches. `K.sample` kinds: `"stone"` for the rock keys, `"green"` for moss and leaf keys, `"vivid"` for
the pollen.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m038_rock` | `#C9AC9C` (parts all; exploded all `#C8AB9C`; D part `#C7AA9D`; start from swatch Rock C `#C0A799`) | 18–23°, 0.19–0.25, R > G > B | all five rocks, default | rough 0.9, metal 0 |
| `m038_rock_light` | `#D8BFB2` (exploded / parts top thirds `#DDBFAE`, `#D6BFB4`, `#D4B7A5`; swatch Rock B `#D1BAAE`) | 18–24°, 0.15–0.21, R > G > B | broad patches on the upper half at 25 %, C's top at 30 % | rough 0.9 |
| `m038_rock_deep` | `#B39A8C` (bottom thirds' lit quartiles `#C7A99A`, `#CFB3A6`, darkened toward `#B69B87`) | 18–24°, 0.20–0.26, R > G > B | broad patches below 0.35 H at 15–20 % | rough 0.9 |
| `m038_moss` | `#AAC005` (B pad exploded `#A5BE04` / parts `#B0C306`) | 62–68°, ≥ 0.93, G ≥ R > B, B ≤ 12 | both pads, default | rough 0.9, low spec |
| `m038_moss_sun` | `#D8D50A` (pad lit quartiles `#D4D206`–`#E0DA0E`; MC median `#C7C606`–`#DCD207`) | 57–61°, ≥ 0.93, \|R − G\| ≤ 10, B ≤ 20 | raised centres and lobe ridges; most of MC | rough 0.9, low spec |
| `m038_moss_deep` | `#739005` (pad shade quartiles `#708F05`–`#778F07`) | 68–74° | rims and notches | rough 0.9, low spec |
| `m038_leaf` | `#98B704` (exploded loose clusters `#A5BC04`, `#9ABB03`, `#95B505`; junction `#8FB202`) | 68–74°, ≥ 0.95, G > R > B | leaves, default | rough 0.85, low spec |
| `m038_leaf_young` | `#C9D60D` (cluster lit quartiles `#C9D70E`–`#CBD60E`; swatch Moss / Leaves 2 `#ACC919`) | 62–66° | inner upright leaves, K1b | rough 0.85, low spec |
| `m038_leaf_deep` | `#4A7A03` (cluster shade quartiles `#3C6302`–`#446204` lifted one step; swatch Moss / Leaves 1 `#8CA108` darkened) | 78–86° | outer low leaves at 40 % | rough 0.85, low spec |
| `m038_petal` | `#F6F2E8` (petal shade quartile `#F8F4E4`; median `#FEFEFC`) | warm white, never B > R | petals | rough 0.7 |
| `m038_pollen` | `#F0C20C` (exploded `#EEC60E`, junction `#FAC808`) | 44–50°, ≥ 0.9 | flower centres | rough 0.7 |

**Calibration warnings:**
- **Rock:** calibrate `m038_rock` on the parts shot (all five rocks) against `#C9AC9C`; then check the f34_sheet rock
  median within 10 of `#CDAFA1` with hue 17–23°, sat 0.18–0.25 and R > G > B. Shade faces in our studio read neutral or
  warm grey, not lavender: don't push them by facing, and don't let any key drift to B ≥ G.
- **Moss against leaves:** pad medians hue 57–68°, value ≥ 0.74; leaf medians hue 68–80°, value ≤ 0.74; the pads must
  read yellower than the leaves in the f34_sheet (pad median hue at least 4° below the leaf median).
- **Petals** clip easily: calibrate on the parts shot so the petal lit quartile is ≤ `#FFFFFD` and the median ≥
  `#F0EEE6`; no blue specular.
- **Lit quartiles** of our studio run 16–22 levels below the sheet's (023's verifiers): that is light, not paint.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Rocks** (on the original facets, before any refine): `rock` base; `K.noise_field(scale≈0.25)` patches →
  `rock_light` on the upper half at 25 % (C's top 30 %); low patches → `rock_deep` at 15–20 %. Per-rock tint ±0.04 so
  the five don't read as one block.
- **Pads:** per pad, field t = (z − base) / pad height: t < 0.25 → `moss_deep`; 0.25–0.6 → `moss`; > 0.6 → `moss_sun`;
  steps 2–3. MC shifted one step toward `moss_sun`.
- **Leaves:** by tier (outer / middle / inner) `leaf_deep` 40 % → `leaf` → `leaf_young`; each cluster its own
  `tint_var` 0.04. K1b and A's foot clumps start one tier lighter.
- **Hard edges only** where materials meet: rock | pad edge, petal | pollen.

### 5.6 Texture (Tint) and finish

- **Tint:** rock amp 0.04, scale 0.3, per original facet (a refined facet keeps one tone); pads amp 0.05, scale 0.8;
  leaves 0.04; petals none. Never per-triangle confetti ("No texture noise").
- **Finish:** rock rough 0.9, metal 0; pads and leaves `low_spec=True` (`K.FOLIAGE_SPEC` 0.06), rough 0.85–0.9; petals
  and pollen rough 0.7. No emission anywhere.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Rock:** f34_sheet median within 10 of `#CDAFA1`; parts-shot median within 8 of `#C9AC9C`; per-rock parts-shot
  medians within 12 of A `#C3A493`, C `#D6B9AC`, D `#C7AA9D`, E `#B9A196`; all R > G > B, hue 17–23°, sat 0.18–0.25.
- **Pads:** f34_sheet MB median within 12 of `#B6C508`, MC within 12 of `#DCD207`; parts-shot MB within 10 of
  `#B0C306`; hue 57–68°, sat ≥ 0.93.
- **Leaves:** parts-shot / FlowerClump median within 10 of `#9ABB03`; f34_sheet leaves (G outside the pad boxes) median
  within 14 of `#81AA03`–`#95B205`; hue 68–80°, sat ≥ 0.93.
- **Petals** median ≥ `#F0EEE6`; **pollen** hue 44–50°, sat ≥ 0.85.
- **Shares** per §4 step 5.

## 6. Joins and contact

- **Rocks:** each its own closed shell, floor-cut flat at z 0 (base 0.03–0.05 below before the cut). No rock touches
  another (gaps §1.3, E within 0.05–0.15 of B and A); none floating, none standing on a point.
- **Pads on rocks:** conformed (`K.conform(sink=0.03)`) with no visible gap from any view; MB drapes over B's
  right-front shoulder, MC over C's back-left corner and left end.
- **Leaves:** roots on the ground (z 0–0.05); leaves press against rocks but cut no more than 0.05 into them; K1's front
  leaves and K1b lie on C's back top; L1 leans on C's left end; K5 tucks into the A–B gap.
- **Flowers:** on top of their clusters, centres 0.05–0.15 above the highest leaf.

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** sunlit rocks and plants; no glow, light, sparkle or particles. The VFX overlay cell shows one
optional effect: a **soft contact shadow**, an olive-grey ground disc under the whole scatter (`#C8C39C` near the
rocks, `#DAD1B1` mid, fading to nothing about 0.5–1.0 stud beyond the footprint), labelled "VFX - not geometry".

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight:** nothing on the sheet glows. The flowers are plain paint.
- **Studio note (Requires Manual Validation):** check in Studio that the rocks stay warm grey-pink (not lilac or grey)
  under the game's sun, that the lime pads stay yellower than the leaves, and that the petals don't bloom.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. **None is a contact shadow**;
  `lib/vfx.py` is frozen for modellers (STAGES.md).
- **Recommended:** the main session adds a **`contact_shadow`** kind before stage 6: one flat Static Beam (like
  `water_flow`: `face_camera` false, normal up), texture `glow_soft`, colour `#6E6B52` (the disc's darkening, olive-grey),
  transparency 0.55 at the centre → 1.0 at the edge, `light_influence` 1, `light_emission` 0. The modeller then adds one
  socket at (0, 0, 0.03) with `end` across the long axis (−5.8, 0) → (+5.8, 0) and width 9.6, so the card covers the
  11.1 × 8.9 footprint plus 0.4–0.6 margin. Check the STATS line reports it.
- **If the main session declines** (the sheet says optional; Roblox's sun shadows already ground the pieces): record
  "Stage 6 skipped: optional contact shadow, no kind in vfx.py".
- **Not recommended:** `dust` or pollen motes, `ore_glint`, any light, harvest sockets.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by searching the repo text and every sheet / wip `.blend` (zstd-decompressed) with
the M035 study's `blendall.py`:
- **W01** (in `FlintbornWorldKit.blend`, `W01.blend`, every wip copy): `PebbleScatter`, `PebbleFlatSlab`, `Pebble`,
  `PebbleWedgeRock`, `PebbleRoundRock`, `PebbleSmallStone`, `PebbleScatterSparse`, `PebbleScatterMedium`,
  `PebbleScatterDense`; keys `w01_*`.
- **W07:** `GroundScatter`, `GroundScatterStone`, `GroundScatterLeaf*`, `GroundScatterPinecone`, `GroundScatterTwig`,
  `GroundScatterMixedSparse`. **W16:** `StoneArchWedgeStones`. **M035:** `MossyBoulder*`, `m035_*`.
- `M.mk` would silently rename a clash to `<name>M038`, so avoid all of these.

**Proposed names.** None of `StoneScatter`, `TallRock`, `MediumRock` or `m038_` occurs in the repo text, the kit
`.blend` or any sheet / wip `.blend`. "Stone scatter" keeps the sheet's subject ("small stones and slabs") without
W01's `Pebble*` prefix.

| Object | Part | Why |
| --- | --- | --- |
| `StoneScatter` | hero | W01 owns `PebbleScatter`, W07 `GroundScatter` |
| `StoneScatterTallRock` | Rock A + its foot clumps | the sheet's "tall rock" |
| `StoneScatterMediumRock` | Rock B + MB | "medium rock" |
| `StoneScatterFlatSlab` | Rock C + MC + its clumps | "flat slab"; W01 owns `PebbleFlatSlab` |
| `StoneScatterWedgeRock` | Rock D | "wedge rock"; W01 owns `PebbleWedgeRock` |
| `StoneScatterRoundRock` | Rock E | "round rock"; W01 owns `PebbleRoundRock` |
| `StoneScatterFlowerClump` | one loose cluster with a flower | the exploded's loose clusters (§8.7) |

- Palette keys `m038_*` (§5.4). Collection `Kit/M038 Pebble Scatter`.
- Collision tags: hero `"none"` (ground detail, as W01's scatter; a single hull would fill the gaps between the
  pieces); TallRock, MediumRock, FlatSlab, WedgeRock `"hull"`; RoundRock and FlowerClump `"none"`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **11.1 × 8.9 × 3.0, A 3.0 tall (hip height)** (recommended: W01's tall-rock height, one class below
   M035's boulder, readable leaves and flowers), or knee-high (A 2.2: dressed 8.1 × 6.5 × 2.2, leaves 0.3–0.5), or
   W01's spread (16.6 × 11.8, which the sheet's tight ring doesn't show).
2. **Layout** (§3.1, §3.2): **the f34 / front / top composition governs**; side, rear and r34 judged loosely (recommended:
   three aligned cells agree within 0.03; the other three are compact re-compositions).
3. **Slab construction** (§3.8): **an extruded plan polygon with a quiet faceted top and uniform bands** (recommended), not
   a ring hull.
4. **E's size** (§3.3): **the hero's 0.7 pebble, the part the same mesh** (recommended), or the rows' 1.8 round rock
   (crowds the A–B gap and changes the hero).
5. **Elevations** (§3.1): **f34_sheet e 32 (probe 28 / 32 / 36), front_sheet 28 (24 / 28 / 32), top_sheet 72 (64 / 72 /
   80)**; side 8, rear 12, r34_sheet (150, 25).
6. **Hero packaging:** **one hero object `StoneScatter` holding separate closed shells: each rock one shell, each moss pad
   its own thin closed shell conformed onto its rock, and each leaf, petal and flower centre its own closed solid**
   (recommended: the pieces stand apart on the ground, so one fused shell is impossible without bridging them; the sheet
   says "Five separate meshes" and "Plants and flowers are geometry (separate from rocks)"; this follows the M035 / M032
   vegetation-shell decision). Every shell closed and manifold, 0 bowties, 0 self-intersections inside each shell;
   shells may touch or interpenetrate by ≤ 0.05 but share no faces; `problems` must report shells that aren't closed.
   Alternative: fuse each pad into its rock by an exact union (one shell per rock, M035's cap precedent) if the
   verifier sees a seam.
7. **Exports:** **the hero plus 6 parts** (`…TallRock`, `…MediumRock`, `…FlatSlab`, `…WedgeRock`, `…RoundRock`,
   `…FlowerClump`) (recommended: the parts breakdown's five plus the exploded's loose cluster, "reused and recombined
   for natural variation"), or the five rocks only.
8. **Stage 5/6:** **no emission or light; a `contact_shadow` kind added by the main session and one socket** (recommended:
   the sheet's VFX overlay and the "VFX always" rule), or skip the optional overlay and record it.
9. **Comparison cameras** (recommended, §3): `f34_sheet (0, 32)`, `front_sheet (0, 28)`, `top_sheet (0, 72)` governing;
   kit `side (90, 8)`, `rear_sheet (180, 12)`, kit `rear34 (152, 12)` + `r34_sheet (150, 25)` loose; extras: the parts
   shot (0, 27), `slab_cu (60, 6)`, a FlatSlab-from-below shot (e −35), `junc_cu (−25, 10)` and a scale shot with a
   5.5-stud marker. Hide the floor in every `*_sheet` render (the sheet's ground shadow is background).
10. **Colour:** **one warm stone (R > G > B, hue 18–23°) with broad light and warm-deep patches, two lime pads in three
    height bands, three-tier leaves, white and gold flowers** (recommended); no cool patches, no dark foot band.
11. **Extras from single cells** (§3.6): **leave out** A's shoulder tuft, B's flank smear, D's smudge and the junction's two
    small stones (recommended: "5 pieces"; the hero, front and top show none).
12. **Names** as proposed.

## 9. Pitfalls to avoid

1. **Mauve rocks.** "Rock A (main)" `#9A98A3` is B > R > G: it is the shade light, not the stone. Every rock key R > G >
   B, hue 12–26°, R − B ≥ 30. M031 failed round 1 on exactly this; check the side and rear medians too.
2. **Soccer-ball or icosphere rocks.** Hull jittered, thinned point rings; big irregular flat facets with slivers next
   to broad faces; meet every §2.2 number (facet counts, largest facet, area and edge CV, valence spread, base
   flatness, h/w per rock). No subdivision, no bevel modifier, no smooth shading.
3. **A lozenge slab.** C has a flat quiet top, uniform bands, a front vertex and a flat underside (§1.4, §3.8). W01's
   slab lost a round as "smooth lozenge".
4. **An egg pebble or a ball.** E and B have flat-topped, squat shapes (h/w 0.6 and 0.53); A is a blunt bullet with a
   flat base, not an egg on a point.
5. **Touching or stacked pieces.** Ground shows between every pair of rocks in the f34; nothing floats or stands on a
   point; E sits in the A–B gap, not on either.
6. **Copying the rows' sizes.** The parts and exploded rows draw E 2–2.5× and D up to 15 % larger than the hero (§3.3).
7. **Copying the side, rear or r34 layout.** They are compact re-compositions (§3.2).
8. **One green.** Pads are lime-yellow (hue 57–68°, lighter), leaves green (68–80°, darker, deep shade side). Measure,
   never eyeball (W01's moss was flagged twice).
9. **Pointed or blade leaves.** The sheet's leaves are broad round-tipped spatulate solids with a midrib fold, in tiered
   rosettes; the flowers have five broad petals, not seven thin ones (`K.clover`'s default `daisy(petals=7)`: pass 5).
10. **A flat moss decal.** The pads are lobed slabs 0.10–0.15 thick with raised centres and rim bands, draped over an
    edge.
11. **Colour by facing.** The peach-lit / lavender-shade split is light. Patches by noise fields over whole facets, pad
    bands by height, leaf tiers by position; `K.check` facing correlation < 0.5.
12. **Budget.** Leaves and flowers are about 70 % of the count; don't spend tris on hidden back leaves of K1 and L1; never
    thin a rock below §2.2.
13. **Name clashes** with W01 `Pebble*`, W07 `GroundScatter*`, W16 `StoneArchWedgeStones` (§8). Only one agent drives a
    Blender session at a time; no commits, pushes or exports in stage agents; don't edit `lib/vfx.py` (frozen).

## Decisions (main session, 2026-10-29)

The recommendations are accepted, except the contact shadow (8):
1. Size: 11.1 W × 8.9 D × 3.0 H.
2. Layout: the front three-quarter, front and top cells govern. The side, rear and rear three-quarter are judged loosely.
3. Slab C is extruded from its plan outline, not built as a ring hull.
4. E is the hero's 0.7 pebble.
5. Cameras: f34 at 32° (try 28/32/36), the front cell at 28° (try 24/28/32), the top cell at 72° (try 64/72/80).
6. Packaging (same rule as M035/M036): one hero object of separate closed shells. Each rock is one shell, each moss pad its own thin shell conformed onto its rock, and each leaf, petal and flower centre its own solid. Every shell is manifold, with 0 bowties and no self-intersections inside a shell. `problems` must report any shell that isn't closed.
7. Hero plus the five rock parts and the flower clump.
8. **No contact-shadow VFX.** Don't add a new kind to `lib/vfx.py`; Roblox's own shadowing covers it. Stages 5 and 6 are recorded as skipped, with no emission or lights.
9. Collision: hero `none`; A, B, C and D `hull`; E and the clump `none`.
10. Colour: one warm stone (every rock key red > green > blue, hue 12–26°, red at least 30 above blue; never the lavender swatch `#9A98A3`), with broad light and warm-deep patches. Moss pads in three height bands, leaves in three tiers, and the two greens kept apart. No cool patches.
11. Details that appear in only one cell are left out.
12. Names: `StoneScatter*` (hero `StoneScatter`), keys `m038_*`.

The §2 facet targets per size class are binding: no soccer-ball patterns, and the slab must not read as a smooth lozenge.

## Stage 1: Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m038.py` (`build()`), built and saved in background Blender 9882 on
`art/blender/assets/kit/wip/M038.blend`; the final check was re-run in a freshly restarted session (same numbers).

- **Packaging (decision 6).** One hero `StoneScatter` of 162 separate closed shells: 5 rocks, 2 moss pads, 119 leaves,
  30 petals, 6 flower centres. No booleans. Parts `StoneScatterTallRock`, `…MediumRock`, `…FlatSlab`, `…WedgeRock`,
  `…RoundRock`, `…FlowerClump` (decision 7), each built by its own function from the same builders.
- **Rocks A, B, D, E** (`_cloud` / `_rock`): convex hulls of jittered point rings (m033 sampling), flattened by a few cut
  planes into big flat facets (m036 method), yawed and scaled to exact world size, flat floor ring at z 0.
  - A: 7 rings (46 points), crown lean −0.42 (crown left of centre); cuts for a broad lit front facet, a front-right
    facet, a broad left flank, the back and a small blunt crown.
  - B: 5 rings; a broad top facet sloping 8° to the front-right, a big front-left face, a steep right end.
  - D: 5 rings, lean (−0.25, 0.20), the top scaled from 1.0 at the back-left to ~0.5 at the front-right, plus a tilted
    top facet and a steep left face (the wedge).
  - E: the hero's 0.7 pebble (decision 4), one flat top facet.
- **Slab C** (`_slab`, decision 3): a 10-vertex plan polygon (straight back edge, chamfered ends, front vertex at 0.44 L)
  extruded as four rings: z 0 inset 0.28 (flat underside 0.87 × 0.83 of the footprint), z 0.30, z 1.33 leaning out 0.05,
  z 1.50 inset 0.16 (top bevel 37–44°). The top is a CDT of the top ring plus two interior verts lifted 0.13 / 0.17:
  12 broad facets, steepest 11.4°, tilt 1.2° (highest at the back-left). Not a ring hull; no dome.
- **Moss pads** (`_pad`): a lobed outline (MB 7 broad maple lobes with pointed tips; MC 7 rounded lobes), a mid ring and
  a centre, as a top and a bottom layer joined by a rim band (140 tris each). Each point is wrapped continuously onto
  its rock: it drops by its distance off the rock (at most `wrap`) and goes to the nearest rock surface, so lobes over
  the top lie on it and lobes past an edge drape down the side. Bottom 0.03 inside the surface; top the pad's thickness
  out (rim 0.08–0.09, centre 0.20–0.27).
- **Plants** (`_rosette`, `_cluster`, `CLUSTERS`): rounded spatulate leaves (closed solids, 18 tris: narrow at the stem,
  widest at 0.58 L, a blunt round tip, a raised midrib in two points, the tip curling down, one back point). A rosette
  is an outer splayed tier plus an inner upright tier, every stem within 0.05 of the hub, so the leaves cross and touch.
  Tall mounds (K1, L1) stack rosettes whose hub is seated (`"l"` seat) on the highest leaf surface under it (no hidden
  stems). Leaves more than 0.40 inside a rock are dropped (1, in L1); shallower ones are pushed out to touch the rock
  (33 pushes). Flowers: five round petals whose bases sit inside a domed centre, seated on the cluster at ≥ 0.85 of the
  leaf height round them, tipped 0.25 rad toward the front (K1's back flower and K5's toward the back, so the rear views
  show them).
- **Settle pass** (`settle`): any group of dressing shells not chained to the ground or a rock/pad at 0.03 is dropped
  straight down onto whatever is under it. Hero: 4 flower groups dropped in round 1, 0 left in round 2.
- **Layout (spec 2.1):** C (−1.73, −1.60) yaw −8°, A (0.72, 3.30) 5°, B (4.12, 1.30) 15°, D (2.39, −3.25) −10°, E (2.25,
  1.75) 30°. Rock clearances (minimum vertex-to-surface): AB 1.57, AC 1.98, AE 0.87, BE 0.36, CD 0.44, the rest ≥ 2.5.
  No rock touches another.
- **Clusters** (leaves / flowers / top z): K1 37 / 2 / 2.51 (3.2 × 2.1 across), K1b 10 / 0 / 0.97, K5 10 / 1 / 0.68, K2
  10 / 1 / 0.66, K3 9 / 1 / 0.58, K4 11 / 1 / 0.74, L1 14 / 0 / 1.42, L2 18 / 0 / 0.88. Six flowers, Ø 1.0, 0.8, 0.6, 0.45,
  0.42 and 0.37.
- **Deviations from the spec's starting values (tuned on the renders):**
  - D is 2.7 × 2.0 × 1.5 (spec 2.7 × 2.3 × 1.8): at 1.8 it stood 15 % too tall in the f34 (box h .00–.37 against .00–.32)
    and read as a ball.
  - K4 moved to x 4.40 and L1 / L2 0.15–0.25 inward: they were the extreme columns and pushed the f34 profile ends off.
  - K1's top is 2.5 (spec table 1.4): the mound has to show above the slab's back edge from the e 32 camera.
  - Cluster widths are 10–25 % over the table's: the sheet's clusters are denser and taller than the table's widths give,
    and the green share needed it (Stage 4).

**Measured against the sheet** (`compare()`, the study's masks; ours with the floor hidden and the 3× lens):

| View (camera) | W : H ours / sheet | Rock / green / flower, ours | Sheet | Top profile mean / max |
| --- | --- | --- | --- | --- |
| f34_sheet (0, 32) | 1.652 / 1.684 | .739 / .254 / .007 | .722 / .270 / .008 | 0.054 / 0.14 |
| front_sheet (0, 28) | 1.755 / 1.708 | .757 / .236 / .006 | .719 / .267 / .015 | 0.064 / 0.21 |
| top_sheet (0, 72) | 1.237 / 1.196 | .633 / .357 / .010 | .691 / .299 / .010 | 0.044 / 0.15 |
| side_sheet (90, 8), loose | 2.330 / 1.867 | .804 / .195 / .001 | .783 / .210 / .008 | 0.193 / 0.58 |
| rear_sheet (180, 12), loose | 3.254 / 1.872 | .751 / .247 / .001 | .709 / .281 / .010 | 0.207 / 0.47 |
| r34_sheet (150, 25), loose | 2.094 / 1.710 | .782 / .214 / .004 | .746 / .248 / .006 | 0.146 / 0.36 |

- Elevation probe (decision 5): the 28 / 36 and 24 / 32 alternatives were not rendered; 32 / 28 / 72 were used throughout.

## Stage 2: Optimisation and cleanup

- **Tris:** hero 3398 / 4000 (rocks 316, pads 280, leaves 2142, petals 540, centres 120). Parts: TallRock 330,
  MediumRock 206, FlatSlab 472, WedgeRock 56, RoundRock 36, FlowerClump 236 (all under 1000).
- **Per rock (spec 2.2):**

| Rock | Tris (target) | Area CV / edge CV | Valence min–max, mean, top share | Tris with a corner < 25° | Facets ≥ 0.4 % at 7° (parts camera) / largest | H/W | Floor span X / Y |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 74 (70–110) | .65 / .36 | 3–9, 5.68, .21 | .41 | 19 / .226 | .97 | .79 / .90 |
| B | 60 (60–90) | .57 / .35 | 3–8, 5.59, .30 | .32 | 20 / .283 | .53 | .85 / .86 |
| C | 72 (60–100) | .74 / .44 | 4–8, 5.81, .38 | .53 | 14 / .222 | T/L .29 | .87 / .83 |
| D | 51 (40–64) | .53 / .38 | 3–9, 5.65, .35 | .43 | 21 / .289 | .56 | .88 / .88 |
| E | 32 (20–32) | exempt | 4–7 | .03 | 18 / .103 | .60 | .82 / .81 |

  - C's top: 12 faces with normal z > 0.97, steepest 11.4°, bevel ring 37–44°. Their share of the top including the
    bevel ring is .77 (100 % without it). Regular-pattern verts: A 0, B 1, C 0, D 0, E 1.
  - Misses: B area CV .57 and D .53 (target ≥ .6); A and D valence max 9 (target ≤ 8); D's largest facet .29 (target
    .08–.12: the tilted top facet dominates). None reads as a pattern in the renders.
- **Mesh checks (every object):** 0 non-manifold edges, 0 non-manifold (bowtie) verts, 0 boundary, 0 wire, 0 loose, 0
  zero-area, 0 n-gons, 0 duplicate verts; normals outward; transforms applied; no custom normals; no modifiers. Per shell
  (`shells_report`): all 162 hero shells are closed and manifold, with 0 self-hits, 0 inverted faces and volume > 0.
  Smallest corner 5.25° (none under 5°; `m012._force_slivers` collapsed 2 slivers in the hero).
- **Floating dressing (STAGES):** `contact_report` on every object gives **0 floating shells** (largest gap of any
  dressing shell to its nearest neighbour 0.00) and **0 unchained** at 0.03 and at 0.05.
- **Origin and size:** bottom centre of each bbox, z min 0. Hero 11.17 × 8.85 × 3.00 (target 11.1 × 8.9 × 3.0 ± 0.5 / 0.6 /
  0.2). Rocks: A 3.1 × 2.3 × 3.0, B 2.85 × 2.4 × 1.5, C 5.83 × 4.38 × 1.67 (bbox with yaw and top lifts; plan 5.8 × 4.0 ×
  1.5), D 2.7 × 2.0 × 1.5, E 0.7 × 0.6 × 0.42.

## Stage 3: UV

- `M.smart_uv(angle 45, ANGLE_BASED, margin 0.008)`, then `m012._uv_unfold`. Every object: 0 overlapping triangle pairs,
  0 flipped, minimum island gap 0.016, border 0.008, texel density min / median / max 1.0 / 1.0 / 1.0, conformal stretch
  p95 1.01–1.06. Hero: 762 islands, 29 texels per stud at 1024.

## Stage 4: Materials, colour and texture

- **Calibration** (`m038.calibrate()`: `K.calibrate` on the kit dome, 6 iterations; targets from spec 5.4):

| Key | Target | Calibrated key | Rendered | Final key (PALETTE) |
| --- | --- | --- | --- | --- |
| m038_rock | `#C9AC9C` | `#9E8C85` (R − B 25: **rejected** by the warm guard) | (200,171,155) | `#A28F84` (R − B 30, hue 22°) |
| m038_rock_light | `#D8BFB2` | `#AA9B97` (R − B 19: rejected) | (215,190,176) | `#AC998E` (R − B 30, 22°) |
| m038_rock_deep | `#B39A8C` | `#8D7E78` (R − B 21: rejected) | (178,153,139) | `#917E73` (R − B 30, 22°) |
| m038_moss | `#AAC005` | `#899E03` | (168,191,7) | `#899E03` |
| m038_moss_sun | `#D8D50A` | `#ABAE07` | (214,212,10) | `#ABAE07` |
| m038_moss_deep | `#739005` | `#627E04` | (116,149,7) | `#627E04` |
| m038_leaf | `#98B704` | `#7B9602` | (149,180,7) | `#84A102` (lifted 7 %: the hero's leaves read dark) |
| m038_leaf_young | `#C9D60D` | `#A0AE0B` | (199,212,13) | `#A0AE0B` |
| m038_leaf_deep | `#4A7A03` | `#3F6C02` | (72,125,7) | `#3F6C02` |
| m038_petal | `#F6F2E8` | `#C2C5C5` (B > R: blue-grey) | (246,243,232) | `#C8C5BE` (warm white, R > G > B) |
| m038_pollen | `#F0C20C` | `#BE9F00` | (240,194,36) | `#BE9F00` |

  - The studio warms the stone, so the keys that render at the sheet's medians have R − B of only 19–25. Decision 10
    requires R − B ≥ 30 on every rock key, so each rock key was moved to the nearest key with R − B = 30 and hue 22°,
    using the calibration's per-channel linear gains (estimated render of `#A28F84`: (205,174,155)). All rock keys pass
    `warm_ok` (R > G > B, hue 12–26°, R − B ≥ 30), and `build()` reports any that don't. The lavender swatch is never
    used.
- **Blending (by position only):**
  - Rocks, per flat facet (2° regions): broad noise patches on the upper half go toward rock_light (mix up to 85 %),
    patches below 0.4 H toward rock_deep (up to 80 %), C's top at least 30 % light, the floor plain rock.
  - Pads, by place on the pad: the centre 90 % toward sun, lobe ridges 70 %, valleys moss or 25 %, the rim band deep
    (90 % mix); MC is shifted 0.34 toward sun.
  - Leaves, by tier: outer leaves leaf × deep 20 %, inner leaves leaf_young (K1b and A's foot clumps one tier lighter).
  - Petals and centres plain.
  - `K.check` baked-shading correlation: hero 0.01, parts ≤ 0.19 (limit 0.5).
- **Texture (Tint):** rock ±4.5 % per facet (scale 0.3) plus ±4 % per rock; pads 5 %; leaves 4 % plus ±4 % per cluster.
  No per-triangle confetti.
- **Finish:** rock roughness 0.9, metal 0; moss 0.9 and leaves 0.85, both with foliage specular 0.06; petal and pollen
  roughness 0.7. No emission.
- **Rendered colours against the sheet** (medians, same masks):
  - Rock: f34 `#CDB09B` vs `#CDAFA1` (R 0, G +1, B −6); front `#CBAE98` vs `#CAAE9E`; top `#CEB29E` vs `#D1B5AA`; parts
    row `#CDAF9A` vs `#C9AC9C`. Parts: A `#BCA08C` vs `#C3A493`, C `#CDB29F` vs `#D6B9AC`, D `#D2B6A0` vs `#C7AA9D`, E
    `#B9A290` vs `#B9A196`. All hue 20–26°, R > G > B. B runs 5–12 low, because the sheet's shade faces are lavender sky
    light, which our studio doesn't produce and decision 10 doesn't let us paint.
  - Green: f34 `#95B50D` vs `#95B205`; front `#95B50E` vs `#93AA07`; top `#95B508` vs `#91AB07`; MB pad (MediumRock part)
    `#B5C415` vs `#B0C306`; FlowerClump leaves `#8EB10C` vs `#9ABB03`.
  - Rear, side and r34 rock medians `#A99386`–`#AF998C` (the backs are in the studio's shade) vs `#CBAE9E`–`#CDAE9C`.

## Stage 5: Lighting

Skipped (decision 8): nothing on the sheet glows, so there is no emissive key and no light. Studio note (manual
validation): check in Studio that the rocks stay warm grey-pink under the game sun, the pads stay yellower than the
leaves, and the petals don't bloom.

## Stage 6: VFX

Skipped (decision 8): the sheet's only effect is the optional contact shadow, which Roblox's own shadowing covers. No kind
was added to `lib/vfx.py` and there are no sockets (`build()` reports any socket on the hero as a problem).

## Modeller's notes for the verifier

- **Run:** `import importlib, kit_models, m038; importlib.reload(kit_models); importlib.reload(m038); m038.build()`. It
  returns `audit`, `uv`, `materials`, `views`, `compare`, `contact` (the floating-shell report per object), `shells`,
  `rocks` (spec 2.2 metrics), `log` (layout clearances, settle moves, clusters, pads) and `problems` (empty).
  `m038.contact_report(o)`, `m038.shells_report(o)`, `m038.measure(path, box)` and `m038.compare()` also work alone.
- **Cameras** (`SHEET_VIEWS`, floor hidden, 3× lens): f34_sheet (0, 32), front_sheet (0, 28) and top_sheet (0, 72)
  govern. side_sheet (90, 8), rear_sheet (180, 12) and r34_sheet (150, 25) are judged loosely (spec 3.2: compact
  re-compositions; our W : H there is 2.1–3.3 against 1.7–1.9, as the spec predicted). Extras: `part_*` (0, 27),
  `part_tallrock_side` (90, 27), `parts_row`, `exploded`, `slab_under` (the FlatSlab part from below), `slab_cu` (the
  FlatSlab part at 70, 6), `junc_cu` (K1 between C and A), `scale` (beside a 5.5-stud stand-in) and the kit views.
- **Known misses:**
  - front_sheet green .236 vs .267 (inside ±4) and flower share .006 vs .015; top_sheet green .357 vs .299 (1.8 over ±4).
  - Back-view flowers are small (share .001–.004): four of the six face the front cameras.
  - D is 2.7 × 2.0 × 1.5, smaller than the spec's 2.7 × 2.3 × 1.8 (Stage 1), and its tilted top facet is its largest
    facet (.29 of the parts view; target .08–.12).
  - B and D triangle-area CV .57 / .53 (target ≥ .6); A and D valence max 9.
  - K1 rises to 2.5 (spec table 1.4); L1 to 1.42 (spec 1.7).
  - MB drapes only 0.19 below B's top at its lowest (spec 0.3–0.45): bigger drapes over B's steep shoulder folded into
    thin flaps, so `wrap` is 0.34 and the pad mostly lies on the top. A small lobe tip still hangs at the front edge of
    the MediumRock part. MC drapes 0.49 over C's left end.
  - The exploded and parts rows draw E about 2× larger; our RoundRock part is the hero's 0.7 pebble (decision 4).
  - Side, rear and r34 profiles miss, as expected for re-compositions (mean .15–.21).
  - The `parts_row` render is small: the five parts at one scale across about 24 studs in one 480-px cell.
  - Single-cell extras (A's shoulder tuft, B's flank smear, D's smudge, the junction's two pebbles) are left out
    (decision 11).

## Verification round 1 (verifier, 2026-10-29)

Fresh verifier; read-only on `art/blender/assets/kit/wip/M038_verify.blend` (background Blender, port 9882; nothing
built, edited or saved). Every number below is my own: my bmesh / BVH scripts and my own numpy comparison with the
study's masks (not `m038.compare()`). Renders and scripts are in the scratchpad `m038_verify\` folder (`r\*.png`,
`mesh_check.py`, `float_check.py`, `rock_check.py`, `colour_check.py`, `cmp.py`).

### Measured

| Object | Tris (limit) | Size W × D × H | Shells (kinds) | Open / NM edges / boundary / wire / loose / bowties / zero-area / n-gons / dup verts | Self-hits in a shell | Inverted (ray parity) | Origin (bbox cx, cy, zmin) | Rot / scale / mods / custom normals | Collision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| StoneScatter | 3398 (4000) | 11.17 × 8.85 × 3.00 | 162 (5 rock, 2 moss, 119 leaf, 30 petal, 6 pollen) | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 | 0 | 0 | 0, 0, 0 | 0 / 1 / none / no | none |
| TallRock | 330 (1000) | 4.10 × 2.30 × 3.00 | 15 (1 rock, 14 leaf) | all 0 | 0 | 0 | 0, 0, 0 | applied | hull |
| MediumRock | 206 (1000) | 2.85 × 2.40 × 1.57 | 2 (rock, moss) | all 0 | 0 | 0 | 0, 0, 0 | applied | hull |
| FlatSlab | 472 (1000) | 6.81 × 4.27 × 1.98 | 16 (rock, moss, 14 leaf) | all 0 | 0 | 0 | 0, 0, 0 | applied | hull |
| WedgeRock | 56 (1000) | 2.70 × 2.00 × 1.50 | 1 | all 0 | 0 | 0 | 0, 0, 0 | applied | hull |
| RoundRock | 36 (1000) | 0.70 × 0.60 × 0.42 | 1 | all 0 | 0 | 0 | 0, 0, 0 | applied | none |
| FlowerClump | 236 (1000) | 1.35 × 1.24 × 0.54 | 13 (7 leaf, 5 petal, 1 pollen) | all 0 | 0 | 0 | 0, 0, 0 | applied | none |

- Every shell closed (each edge exactly 2 faces), positive volume; smallest corner 5.25° (hero). UV: 0 overlaps, 0
  flipped, min gap 0.016, border 0.008, density 1.0 on every object.
- **Floating dressing (own code, verts + edge midpoints + face centres against every other shell, BVH overlap):** hero
  **0 floating** (every leaf / petal / centre shell is in contact, gap 0.00), **0 unchained** at 0.03; same on all six
  parts. Both pads touch their rock (gap 0). All rocks sit at z 0; no two rocks within 0.1 of each other.
- **Rocks in the hero (own metrics, floor faces excluded):**

| Rock | Tris (vis.) | Size | H/W | Area CV / edge CV | Valence (non-floor) min–max, mean | Slivers < 25° | Near-equal 5–6 fans | Floor span X / Y |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | 78 (72) | 3.10 × 2.30 × 3.00 | .97 | .62 / .35 | 3–8, 5.67 (floor fan 12) | .42 | 0 | .79 / .90 |
| B | 66 (60) | 2.85 × 2.40 × 1.50 | .53 | **.57** / .35 | 3–8, 5.59 | .36 | **4** | .85 / .86 |
| C | 80 (72) | 5.83 × 4.38 × 1.67 | T/L .29 | .74 / .44 | 4–8, 5.81 | .51 | 0 | .87 / .83 |
| D | 56 (51) | 2.70 × 2.00 × 1.50 | .56 | **.53** / .38 | 3–**9**, 5.65 | .46 | 1 | .88 / .88 |
| E | 36 (32) | 0.70 × 0.60 × 0.42 | .60 | exempt | 4–7 | .08 | (exempt) | .82 / .81 |

  - C's top: 12 faces with normal z > 0.97, steepest near-top face 11.4°, flat underside; .77 of the upward area
    including the bevel ring (target ≥ .85).
- **Renders against the sheet** (my `cmp.py`, sheet cells vs ours, floor hidden):

| View | W : H ours / sheet | Rock / green / flower ours | Sheet | Profile mean / max |
| --- | --- | --- | --- | --- |
| f34_sheet (0, 32) | 1.652 / 1.684 | .739 / .254 / .0068 | .722 / .270 / .0079 | .054 / .13 |
| f34 probe e 28 / 36 | 1.755 / 1.567 | — | — | .054 / .12; .054 / .14 |
| front_sheet (0, 28) | 1.755 / 1.708 | .758 / .236 / .0062 | .719 / .267 / .0146 | .065 / .21 |
| front probe e 24 / 32 | 1.872 / 1.652 | — | — | .070 / .25; .067 / .17 |
| top_sheet (0, 72) | 1.237 / 1.196 | **.633 / .357** / .0097 | .691 / .300 / .0096 | .043 / .15 |
| top probe e 64 / 80 | 1.270 / 1.255 | — | — | .046 / .15; .051 / .16 |
| side (90, 8), loose | 2.330 / 1.867 | .804 / .195 / .0013 | .783 / .209 / .0078 | .195 / .58 |
| rear (180, 12), loose | 3.254 / 1.872 | .751 / .247 / .0014 | .709 / .281 / .0098 | .207 / .47 |
| r34 (150, 25), loose | 2.094 / 1.710 | .782 / .214 / .0042 | .746 / .248 / .0059 | .145 / .36 |

  - The decision-5 probes are now rendered: e 32 ties 28 and 36 on the f34 (mean .054 each), e 28 is best for the
    front (.065), e 72 best for the top (.043). The chosen cameras stand.
- **Colour (rendered medians, same masks):**

| Region | Sheet | Ours | Note |
| --- | --- | --- | --- |
| Rock f34 / front / top | `#CDAFA1` / `#CAAE9E` / `#D1B5AA` (hue 19 / 22 / 17) | `#CDB09B` / `#CBAE98` / `#CEB29E` (hue 25 / 26 / 25) | R > G > B, within 10; a touch more orange |
| Rock pixels with B ≥ R | 11–15 % (lavender sky shade) | 0 % | never lavender or mauve |
| Rock parts A / C / D / E | `#C3A493` / `#D6B9AC` / `#C7AA9D` / `#B9A196` | `#BCA08C` / `#CDB29F` / `#D2B6A0` / `#B9A290` | within 12 except C's blue (13) |
| MB pad f34 | `#B6C508` (hue 64.8) | `#B7C516` (64.8) | match |
| MC pad f34 | `#DCD207` (57.2) | `#C2CC17` (63.3) | **less yellow than the sheet** |
| Leaves f34 (G outside the pad boxes) | `#87A804` (72.1, s .98) | `#93B514` (72.7, s .89) | lighter, a little grey |
| Petals | `#FEFFFE` | `#FFFAE8` | warm white |

  - Rock keys `#A28F84` … `#AA988C`: every one R > G > B, hue 22–24°, R − B = 30; the lavender swatch is not used.
  - Pads (hue 61–65) against leaves (72.7): the two greens are 8–9° apart (≥ 4 needed).
  - Facing: kit `baked_shading` hero 0.009, parts ≤ 0.19 (limit 0.5). My own correlation of rock-key lightness with
    face normal z is 0.37, driven by C's top lift (a position rule from spec 5.4), and under the limit. Tint is a
    CORNER colour attribute; broad per-facet mottling shows in the renders, with no confetti.
- **Lighting / VFX:** emission strength 0 on all 22 `FB_m038_*` materials, no emission nodes, no lights and no
  sockets in the collection (decision 8).

### Findings

No blockers.

1. **minor — leaf rosettes read as cupped lettuce heads.** From the top and f34 the clusters (K2, K3, K4, K5, the
   FlowerClump part) are closed domes of overlapping broad plates. The sheet shows splayed star rosettes of separate
   spatulate leaves with gaps between them. The FlowerClump part's inner upright leaves read as thin blades edge-on
   (pitfall 9). This is also why top_sheet green is .357 against .300 (+5.7, over ±4) and rock .633 against .691.
   **Fix:** lower `IN_PITCH` to about 0.55–0.75. Use fewer, narrower outer leaves (5–7 per small cluster) splayed
   with 15–25° gaps. Widen the inner leaves at the tip so they don't read as blades. Re-measure top_sheet green to ≤ .34.
2. **minor — MC pad not yellow enough.** f34 MC `#C2CC17` against `#DCD207` (R −26, hue 63 against 57). **Fix:**
   shift MC further toward `moss_sun` (0.34 → about 0.6), or make `moss_sun` yellower (the target render is R ≈ G).
   Check MC within 12 of `#DCD207`.
3. **minor — greens slightly grey and light.** Leaf and pad renders carry B 0x12–0x17 against the sheet's 0x04–0x08 (sat
   .89 against .97), and the f34 leaves are 12–16 lighter than `#87A804`. **Fix:** cut the green tint amplitude, or
   check that the Tint isn't pulling blue in, so the B channel stays ≤ 10. Darken `leaf` back toward the calibrated
   `#7B9602`.
4. **minor — f34 top profile mean .054, max .13** (target mean ≤ .04, max .07). The ends are too high: f .00 .40
   against .28 and f 1.0 .59 against .45. L1 / L2 at C's left and B / K4 at the right stand taller than the sheet's.
   **Fix:** lower L1's top and K4 by about 0.2.
5. **minor — front_sheet flower share .0062 against .0146** (outside ±.006); rear and side flowers barely show (.0013
   and .0014 against about .008–.010). The K1 front flower reads small. **Fix:** K1's front flower toward 1.1, and turn
   one of K1's and K5's flowers more upward so the rear cameras see them.
6. **minor — rock facet statistics.** B area CV .57 and D .53 (target ≥ .6). B has 4 vertices with 5–6 near-equal
   triangles round them (allowed: at most 2). D's non-floor valence reaches 9. D's tilted top / front-left facet
   dominates the parts view (modeller .29; target .08–.12). None reads as a soccer ball or an egg in any render. B and D
   look like chunky faceted stones. **Fix (optional):** one more jittered point on B's front-left face and on D's big
   facet.
7. **minor — D smaller than the spec** (2.7 × 2.0 × 1.5 against 2.7 × 2.3 × 1.8). Its f34 box (about f .61–.86, h
   .00–.33) still matches the sheet's (.59–.83, .00–.32), so I accept the modeller's tuning.
8. **minor — MB drape shallow.** The star pad mostly lies on B's top, with its right lobes reaching out past the edge.
   The sheet drapes it 0.3–0.45 down the right-front shoulder. It reads as a pad on top, not as a decal, so it isn't a
   blocker. **Fix:** a deeper `wrap` on the right-front lobes only.
9. **minor — slab top quiet, too few tones.** C is a correct extruded slab: flat top, uniform band, bevel and chamfer,
   flat underside, front vertex. It is not a lozenge. Its top reads as one plain plate, though, where the sheet shows
   broad facets of different tone. The top's share including the bevel ring is .77 (target ≥ .85). **Fix:** stronger
   per-facet rock_light / base alternation on C's top only.
10. **minor — part dressing light.** The TallRock's foot clumps and the FlatSlab's back-edge clump and left-foot cluster
    are small next to the parts row (sheet: an 8–10-leaf clump at A's left foot, a substantial clump on C's back edge).
11. **minor — rock hue 25° rendered** (spec 5.7: 17–23°). It is inside the decision's 12–26° key rule and R − B ≥ 30, a
    little more orange than the sheet's pink. Lowering the hue would break R − B ≥ 30 at this value, so leave it.

Checked and confirmed:
- The modeller's own notes: B / D CV, D size and facet, top green, back flowers, MB drape (all real, all minor as
  above).
- Elevation probes, now done (32 / 28 / 72 stand).
- Decisions 1–12: size, layout, extruded slab, 0.7 pebble, cameras, separate closed shells, hero + 6 parts, no VFX,
  collision tags, warm stone keys, single-cell extras left out, names.

### Score and verdict

**7.5 / 10. PASS.** The mesh is clean, the budget holds, nothing floats and the silhouette and layout are right.
- Clean mesh: every shell closed and manifold, 0 bowties, 0 self-intersections.
- Budget: 3398 / 4000, parts ≤ 472.
- Layout: the five-rock ring and every rock's role read correctly (tall blunt A, extruded slab C, boxy mossy B, wedge D,
  pebble E).
- Colour: the stone is warm and never lavender, two greens are kept apart, petals are warm white.
- No colour by facing. All decisions followed.

The leftovers are polish: rosette openness, MC yellow, green saturation, profile ends and flower size. Round 2 could
take items 1–5.

## Main session ruling (2026-10-29)
- **Result:** passed in round 1 (7.5/10) and committed. The optional round 2 is skipped (pace rule); its items are recorded for a later polish pass.
- **Polish items:**
  - Leaf clusters read as cupped lettuce heads, not open star rosettes, and the top view is too green (.357 against .300). Target: `IN_PITCH` about 0.55–0.75, top green at most .34.
  - Pad MC isn't yellow enough. Shift it toward `moss_sun`.
  - The greens are slightly grey and light. Darken `leaf` toward `#7B9602`.
  - The f34 top profile is off at the ends. Lower L1 and K4 by about 0.2.
  - Flowers are too small, and the rear views miss them.
  - The B and D facet statistics miss their targets.
  - The B pad drape is shallow.
  - The slab top reads as one tone.
- **Export:** 7 assets, 7 solid pieces, 4734 tris, 0 VFX sockets, palette 22 colours, 0 problems.
