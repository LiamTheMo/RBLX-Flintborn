# 018 Healing Herb — spec

Reference: `art/blender/assets/references/018.png` (HEALING HERB, "Individual Asset Production Reference", footer
"FLINTBORN — INDIVIDUAL MODEL STUDY", "PAGE 18/132"; INDEX.md row 18, "Flintborn healing herb study"; 1024 × 1536 px).
Builder: `art/blender/kit/mcp/m018.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them (this sheet shows none, §7).

Sheet text: "Low-poly stylized forest herb with closed flower buds. Chunky, cartoony forms, broad flat-shaded faces and
simple clean shapes. Designed for reusability." Modeling notes: "Keep forms chunky and low-poly"; "Broad, flat-shaded
faces"; "Clean, simple silhouette"; "Reusable modular parts"; "Maintain consistent geometry with orthographic views".
Palette: Bud, Leaf Light, Leaf Dark, Stem / Root Plug (one brown swatch, but every stem on the sheet is green: §3.7).
Close-up captions: "Leaf joins around root plug and stem base"; "Leaves angled upward from root plug"; "Faceted bud
with simple junction to stem". Parts: Flower Bud (x3), Stem (x3), Leaf (x6), Root Plug (x1).
The game's node is `HerbShrub` (`src/shared/Resources/NodeCatalog.luau`: material Herbs, 2 hits; the placeholder in
`src/server/Services/ResourceService.luau` is a 3 × 2 × 3 ball). WorldModeling §11: "healing herb" is an art label;
no medical or gameplay effect is implied, so nothing glows.

All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, top-left origin. Paper is `#F2ECE6` (242, 236, 230). Masks
(`m.py` `cls()`, HSV):
- **L, green** (leaves and stems): sat ≥ 0.22 and hue 60–140° and g > 50.
- **U, bud cream:** hue 30–60°, sat 0.10–0.45, v ≥ 0.74.
- **T, plug brown:** sat ≥ 0.18 and (hue ≤ 40° or ≥ 345°) and v < 0.74. A few bud-edge shade pixels fall in T
  (T spans reaching h 0.5–0.75 in f34 / rear); that is about 0.3 points. Use the same masks on our renders and it cancels.
- **O:** other non-paper (ground shadow, dark edges). Not counted in the shares.

Scratch study material (pure Python, no Blender), in the session scratchpad
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m018_study\`
(run with `C:/Users/Orang/.local/bin/python3.14.exe`):
- `png.py` (reader, `crop`); `m.py` (masks, view boxes `V`); `bb.json` (silhouette boxes, written by `measure.py`);
- `measure.py` (bboxes, shares, top / leaf-bottom profiles, width per height), `buds.py` (bud components),
  `stems.py` (green runs per height: stem widths), `polar.py` (top-view radius per azimuth, leaf tips), `expl.py`
  (parts, exploded and close-up components), `samp18.py` / `samp19.py` / `samp20.py` (swatches, region medians,
  quartiles, deciles, bud thirds, leaf radius bands, height bands, per-leaf, stem by height);
- crops: `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `parts.png`, `cu_junc.png`,
  `cu_under.png`, `cu_bud.png`, `pal.png`; grids `g_front.png`, `g_side.png`, `g_rear.png`, `g_top.png`, `g_f34.png`,
  `g_r34.png`; mask previews `cls_front.png`, `cls_rear.png`; zooms `z_parts_stem.png`, `z_parts_leaf.png`,
  `z_parts_plug.png`, `z_parts_bud.png`, `z_expl_core.png`, `z_expl_stems.png`, `z_expl_buds.png`, `z_f34_base.png`,
  `z_front_base.png`, `z_front_stems.png`, `z_side_stems.png`, `z_rear_stems.png`, `z_rear_buds.png`, `z_top_c.png`,
  `z_cu_bud.png`, `z_cu_plug.png`.
- To run them on our renders, point `R` (in `m.py`) at the render and set `P` to the render's background colour.

## 1. Study (2a)

### 1.1 Classification, size and scale

- **Classification:** full asset (forage resource node, `HerbShrub`). Hero budget 4000 tris, each part under 1000.
  WorldModeling §16 suggests 80–400 for an ordinary herb; the plan below lands at about 450–550 (§4.3).
- **What it is:** a low **rosette of seven big chunky faceted leaves** radiating from a squat faceted **brown root plug**,
  two smaller **upright inner leaves** around the stems, and **two straight green stems** carrying **cream faceted
  closed buds**: a tall one on the axis and a shorter one leaning to the front-right. The rosette is **higher at the back**
  (the back leaves rise to shoulders at about 0.6–0.65 of the height) and **low at the front** (the front leaves droop
  until their tips touch the ground). The plug shows only as a dark brown band at the ground between the leaf bases.
- **Target size: about 2.85 W × 2.65 D × 2.2 H studs** (H = 0.40 of the 5.5-stud character). Tolerances W ±0.15,
  D ±0.15, H ±0.1. Main bud 0.55 across.
  - Why: WorldModeling §3.2 "Flowering herb" is 0.15–0.40 C (0.8–2.2 studs), "bloom diameter 0.25–0.55 of overall
    height" (the main bud is 0.25 H: inside). The design doc wins over the sheet's implied scale (M017 decision 1).
    The node must still read as a harvestable at gameplay distance, so take the top of the range. That also matches
    the game's 3 × 2 × 3 placeholder.
  - The sheet's own proportions: front W : H 1.32 (226 × 171 px), side D : H 1.20 (205 × 171), rear W : H 1.28
    (218 × 170), top W : D 1.08 (200 × 185); front/side ratio 1.10 agrees with the top's 1.08, so the top cell is close to
    a true plan this time.
  - Repo neighbours: R05 `HealingHerb` 5.6 × 5.8 × 3.3 (WorldModeling-free kit row), lobby `BroadLeafHerb` 4 × 2.5.
    The size is a decision (§8).
- **Stud mappings used below** (build frame: front −Y, +X right, ground z 0; **plant axis** = the main stem):
  - front view: X = (f − 0.50) × 2.90; side view (**drawn from −X**, §3.1): Y = (0.50 − f) × 2.64 (screen right is the
    front); rear view: X = (0.50 − f) × 2.82 (screen right is −X); top view: X = (f − 0.50) × 2.85,
    Y = (h − 0.50) × 2.64 (image top = back); heights z = h × 2.2 (the orthographic cells look down about 6–10°, §3.5).
  - **77.7 px per stud** in the front, side and rear cells; 70 in the top cell.
  - The plant axis sits at **X +0.06** of the bbox centre (front stem f 0.525; rear stem f 0.477 → both +0.06) and
    Y 0.0 (side stem f 0.50). Coordinates below are relative to the axis.

### 1.2 Measured views (`measure.py`, `buds.py`)

| View (box) | Silhouette bbox (px) | W : H | Green L | Bud U | Plug T | Buds |
| --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (25,110,522,430) | 37–508 × 118–418 | 1.57 | 88.4 % | 10.1 % | 1.6 % | 2 |
| Rear three-quarter (530,110,1000,430) | 544–955 × 126–415 | 1.42 | 83.1 % | 14.3 % | 2.7 % | 2 |
| Front (22,495,268,692) | 30–256 × 508–679 | 1.32 | 87.2 % | 11.8 % | 1.0 % | 2 |
| Side (272,495,508,692) | 290–495 × 507–678 | 1.20 (D : H) | 83.7 % | 14.3 % | 1.9 % | 2 |
| Rear (513,495,768,692) | 531–749 × 508–678 | 1.28 | 88.3 % | 9.1 % | 2.6 % | 1 + 1 partly hidden |
| Top (772,495,1012,700) | 790–990 × 505–690 | 1.08 (W : D) | 92.8 % | 7.2 % | 0.0 % | 2 |

- Reading: the herb is nine-tenths green from every side; the buds take a tenth (a seventh from the side and r34,
  where they don't overlap); the plug shows only as 1–3 %.
- **Verifier check:** shares ±3 points (U ±2), profiles below ±0.06 h.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front | .16 | .32 | .58 | .63 | .66 | .68 | .67 | .66 | .64 | .95 | 1.0 | .96 | .89 | .79 | .74 | .61 | .61 | .62 | .59 | .54 | .11 |
| Side | .18 | .35 | .39 | .43 | .68 | .68 | .68 | .66 | .84 | .95 | 1.0 | .97 | .91 | .78 | .80 | .71 | .46 | .46 | .44 | .40 | .33 |
| Rear | .22 | .32 | .62 | .65 | .67 | .68 | .66 | .72 | .93 | .98 | .98 | .95 | .68 | .71 | .72 | .74 | .58 | .58 | .58 | .54 | .49 |
| f34 | .19 | .35 | .43 | .60 | .66 | .69 | .71 | .70 | .69 | .94 | 1.0 | .96 | .78 | .83 | .78 | .64 | .65 | .66 | .63 | .58 | .10 |
| r34 | .29 | .39 | .45 | .48 | .62 | .63 | .63 | .63 | .87 | .96 | .99 | .94 | .79 | .83 | .83 | .56 | .58 | .58 | .57 | .54 | .47 |

**Leaf bottom** (lowest green pixel per column): the rosette sits on the ground almost everywhere (front .13 .15 .17 .19
.19 .18 .13 .11 .18 .10 .05 .00 .02 .06 .15 .13 .13 .13 .12 .09 .06). There is no see-through gap under the leaves; the
negative space of this asset is the air around the two stems above the rosette.

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; the start f after the @):

```
front  .04@.54 .63@.36 .96@.02 .88@.05 .78@.11 .78@.18 .77@.11 .19@.53 .26@.41 .16@.42 .01@.50
side   .01@.13 .79@.12 .90@.01 .97@.03 .84@.11 .48@.22 .56@.19 .29@.46 .30@.40 .18@.42 .01@.50
rear   .01@.87 .87@.01 .97@.00 .89@.04 .79@.11 .83@.16 .65@.08 .39@.35 .19@.38 .17@.39 .01@.47
top    (radius per azimuth, §1.3 "Top")
```

So the rosette is widest at h 0.2–0.3 (z 0.45–0.65), keeps 0.77–0.83 of its width up to h 0.6 (the leaf shoulders),
then only the buds, stems and the inner leaves rise above h 0.7.

### 1.3 Silhouette and composition per view

**Front (`g_front.png`, `z_front_stems.png`, `z_front_base.png`):**
- A wide low fan with two buds above the centre: the tall bud on the axis (f 0.507, its top is the apex h 1.0), the
  short bud to the right (f 0.653, h 0.61). Left shoulder at h 0.63–0.68 (f 0.15–0.40), right shoulder h 0.59–0.62
  (f 0.75–0.90). Leaf tips touch the ground at the far left (f 0.0, h 0.16), the far right (f 1.0, h 0.08) and the front
  centre (f 0.53, h 0.0).
- **Leaves** (centre f, h): upper-left big leaf pointing left (f 0.07–0.47, h 0.47–0.66, tip at f 0.07, h 0.47);
  left big leaf drooping to the ground (f 0.0–0.48, h 0.16–0.42); the **front leaf** pointing at the camera, a
  diamond with a four-facet apex (f 0.42–0.66, top h 0.30, tip at the ground; `z_f34_base.png`); right low big leaf
  (f 0.62–1.0, h 0.05–0.42); right upper leaf (f 0.68–0.96, h 0.42–0.62); a **tall upright leaf behind the short bud**
  (f 0.55–0.72, up to h 0.80); a back-left upright leaf behind the main stem (f 0.33–0.48, up to h 0.66).
- **Stems:** main stem vertical, f 0.50–0.55 (0.070 H = 0.15 stud), visible from h 0.28 to the bud at h 0.70; short
  stem leaning right, f 0.575–0.624 at h 0.35, reaching the short bud's bottom (h 0.50) at f 0.65: about 25–30° from
  vertical in this view. Both show three facet tones (dark edge, lit broad face, mid face): a 6-sided prism (§3.6).
- **Plug:** dark brown at the ground, f 0.36–0.45 and 0.66–0.74, h 0.08–0.16, between the leaf bases (brown span
  1.1 studs).

**Side (drawn from −X: screen right = −Y, the front; `g_side.png`, `z_side_stems.png`):**
- Back (screen left) high: shoulder h 0.68 at f 0.20–0.35 (Y +0.4 to +0.8, z 1.5); the far back tip at f 0.0, h 0.18.
  Front (screen right) low: h 0.40–0.46 at f 0.80–0.95, the front tip at f 1.0, h 0.33. Two near leaves meet in a V
  at the bottom centre over the plug.
- **Buds:** main (0.500, 0.851; 0.24 × 0.31 H = 0.53 × 0.68 stud); short bud to screen right (0.661, 0.675;
  0.216 × 0.251 H), i.e. **in front of** the axis (Y −0.43).
- **Stems:** main f 0.473–0.527 (0.058–0.070 H), vertical; short stem from f 0.537–0.590 at h 0.35 to f 0.70 at h 0.55:
  about 35–39° from vertical in this view.
- A tall leaf rises behind the short bud on screen right (f 0.62–0.78, up to h 0.72).
- **Plug:** brown at f 0.36–0.67, h 0.05–0.12 (0.82 stud).

**Rear (camera at +Y, screen right = −X; `g_rear.png`, `z_rear_buds.png`, `z_rear_stems.png`):**
- Shoulders h 0.62–0.68 on the left (f 0.10–0.35, X +0.4 to +1.1) and 0.58 on the right (f 0.80–0.95, X −0.85 to
  −1.3); a V of two near leaves at the bottom centre, as in the side.
- **Buds:** main on the axis (f 0.46, top h 1.0); the short bud is **behind the main bud** (partly hidden by it) at
  screen left: it is at +X and farther from this camera, so at −Y. Its visible top is h 0.76.
- **Stems:** main f 0.450–0.505 (0.076 H) from h 0.35 up; a tall upright leaf at screen right (f 0.55–0.72, up to
  h 0.74: X −0.4).
- **Plug:** brown at f 0.32–0.65, h 0.05–0.13 (0.93 stud).

**Top (`g_top.png`, `z_top_c.png`, `polar.py`; image top = back):**
- A **seven-pointed star** of leaves. Radius per azimuth (azimuth from +X, counter-clockwise; studs):

  ```
  az   0    15   30   35*  45   60   75   85*  100  115  130  145* 160  175  190* 205  220  240* 255  270  285* 300  315  330  345* 355
  r  1.17 1.09 1.38 1.49 1.21 0.90 1.20 1.35 1.04 0.84 1.10 1.30 1.00 1.16 1.46 1.06 0.93 1.32 0.95 1.13 1.37 1.09 1.04 1.16 1.50 1.24
  ```

  Tips (*) at **35°, 85°, 145°, 190°, 240°, 285°, 345°** (spacing 45–60°, mean 51°), reach 1.30–1.50; notches
  between them at 0.82–0.95. A small leaf shows at about 310° (r 1.08) under the 345° leaf: an inner leaf (§2.2, I1).
- Two buds near the centre, both 31 × 32 px (0.44 stud), at (f 0.43, h 0.50) and (0.60, 0.58), with the short
  stem visible between them. Their placement does not match the front (§3.4).
- Leaf colour by radius: dark at the centre, light at the tips (§5.3).

**Three-quarters (`f34.png`, `r34.png`):** the f34 (the hero) shows the same layout as the front: two buds well apart
(short bud right and lower, offset 0.20 H), the front diamond leaf at the ground, both shoulders, the plug as brown
wedges between leaf bases. The r34 also has the short bud on the **right** (offset 0.23 H), which no rear-side camera
can show for a bud at +X: it is the mirror of a true rear three-quarter (§3.3).

**Close-ups (bottom row):**
- **Leaf Junction** (25,1195,280,1470), `cu_junc.png`: the plug is a big faceted ball (113 px = about 5 stem widths
  across) sitting on the ground; the stems rise from its flattened top; the leaf bases wrap round its upper sides.
- **Underside** (298,1195,540,1470), `cu_under.png`: from below, the plug (96 × 114 px) is a round faceted ball, and
  the leaves leave its upper rim at about 30–45° upward; their undersides are darker (§5.2).
- **Bud & Stem** (555,1195,785,1470), `cu_bud.png`, `z_cu_bud.png`: the bud (99 × 119 px, H : W 1.20) is a faceted
  ovoid: a five-facet apex fan on top, two bands of triangles round the middle, and a short cone below that sits
  directly on the stem's flat top ("simple junction"); no collar, no sepals. The stem is a green prism about 0.5 of
  the bud's width (51 px incl. two faces).

### 1.4 Parts (Exploded Construction (20,745,680,1160), crop `expl.png`; Parts column (690,745,1010,1160), `parts.png`)

Labels: "Flower Bud (x3)", "Stem (x3)", "Leaf (x6)", "Root Plug (x1)". Arrows: buds down onto the stem tops; stems
down into the centre of a brown **crown disc**; leaves inward to the disc rim (double arrows = placement/turn); the
plug **up** into the disc. The disc (70 × 35 px) carries an assembled core that is not labelled: a **tall upright
centre leaf** behind the middle stem and **two small curled leaves** at the rim (`z_expl_core.png`). The exploded
draws 3 buds, 3 stems, 5 big floating leaves plus the centre leaf (= the six), and the plug.
Scale: exploded buds 53–63 px wide; parts-column bud 59 px. Taking the bud as 0.55 stud: **about 107 px per stud**.

Facet language: broad flat-shaded facets, 3–4 across a leaf's face, 3–4 across a bud. No noise, no smooth shading.

#### Flower Bud: parts (752,749,810,826) 59 × 78 px; exploded (278,765,330,833), (356,725–802), (418,767,480,843); close-up (591,1223,689,1341)

- **Shape:** a faceted ovoid, **H : W 1.25** (parts 1.32, exploded 1.19–1.30, close-up 1.20, hero 1.15–1.21), widest at
  0.55 of its height, a blunt **five-facet apex** on top, a **short cone** below (lower 30 %) to the stem.
- **Size:** main 0.55 W × 0.68 H (hero front 43 × 52 px, side 41 × 53); short bud 0.45 × 0.52 (front 33 × 38, side
  37 × 43; 0.82 of the main). Exploded buds vary ±10 %.
- **Construction:** `_bud(radius, height, seed)`: rings of 5 verts, alternate rings turned 36°:
  bottom point (on the stem axis, z 0) → ring A (z 0.30 H, r 0.80 R) → ring B (z 0.56 H, r 1.00 R, turned) → ring C
  (z 0.80 H, r 0.80 R) → top point (z 1.0 H). Ring radii ±4 %, twist ±6° per ring by seed. **30 tris.** This reads as
  the sheet's "top fan, two bands, bottom cone". Not a smooth ico-2 (too round and fine), not a bare icosahedron
  (a 20-face jewel, WorldModeling §18).
- **Triangles:** 30 each.

#### Stem: parts (769,839,793,924) 25 × 86 px; exploded (301,862,334,937), (371,837,393,911), (416,876,444,947); close-up stem (594,1335,644,1442)

- **Shape:** a straight prism with a flat top, slight taper (1.0 → 0.88). Parts and exploded stems are **4-sided**;
  the hero stems and the close-up show **three faces at once** (6-sided). Resolution §3.6: 6 sides.
- **Size:** Ø 0.15 (hero: front 0.070 H, side 0.058–0.070, rear 0.076 → 0.13–0.17); parts-column stem 0.16 × 0.75;
  hero main stem 1.32 long (from z 0.30 inside the plug, past the plug top at z 0.42, to 0.08 into the bud whose bottom
  point is at z 1.54); short stem 1.0.
- **Construction:** `_stem(length, radius, sides=6, seed)`: 3 rings (base, middle, top), ±5 % radius and ±8° twist on
  the middle ring, flat cap. **About 24 tris.**

#### Leaf: parts (709,943,847,1034) 139 × 92 px (oblique); exploded big leaves 145 × 125, 148 × 116, 133 × 116, 125 × 171, 141 × 52 (edge-on)

- **Shape:** a chunky broad pointed leaf: narrow base (about 0.25 W), **widest at 0.55 L**, straight-ish sides to a
  pointed tip; **W : L ≈ 0.42** (top-view leaves 0.68 wide for about 1.6 long). The top is a low **pyramid**: the
  outline's facets meet at one apex at about 0.5 L (the f34 front leaf shows four big facets meeting at that point),
  with a ridge running on to the tip. The underside is a shallow keel. Thickness: apex 0.10–0.12 L above the outline,
  keel 0.04–0.05 L below. Chunky, but a folded wedge, not a pillow (WorldModeling §6.1, §18).
- **Size:** big leaves L 1.5–1.7 (exploded diagonals 176–210 px = 1.65–1.95 at 107 px/stud; hero top-view reach 1.30–1.50
  from the axis, starting at r 0.25 on an arching path), W 0.65–0.72; inner leaves L 1.25–1.35, W 0.45–0.5.
- **Construction:** `_leaf(L, W, pitch, curl, seed)`: an **8-point outline** (base; shoulders at 0.25 L / ±0.40 W;
  belly at 0.55 L / ±0.50 W; pre-tip at 0.82 L / ±0.28 W; tip), one top apex at 0.50 L (camber 0.11 L), one keel
  vertex below (0.05 L). This is `K.leaf` with a new outline `"kite": [(0.25, 0.40), (0.55, 0.50), (0.82, 0.28)]`
  (16 tris). If the f34 comparison shows too few facets, add a second ridge vertex at 0.80 L (camber 0.05 L): 20 tris.
  Bend: `pitch` = the base's rise, `curl` drops the tip (big outer leaves arch up then droop; inner leaves stay
  upright). Per-leaf ±8 % L, ±6 % W, ±5° roll by seed so no two neighbours are identical.
- **Triangles:** 16–20.

#### Root Plug: parts (735,1050,823,1129) 89 × 80 px; exploded plug (346,1082,422,1148) 77 × 67, crown disc (349,1029,418,1063) 70 × 35; close-ups (86,1296,198,1395), (362,1267,457,1380)

- **Shape:** a squat round faceted ball, **W : H 1.11** (parts), slightly flattened on top. Facets: a five-facet fan on
  top, broad triangles round the sides (parts and close-ups): an ico-2 sphere.
- **Size:** part 0.85 W × 0.77 H (parts column at 107 px/stud). In the hero its visible brown spans 0.82–1.1 at the
  ground: use **Ø 0.9**.
- **Crown disc** (exploded only, drawn as its own piece between the plug and the leaves; unlabelled): a flared 8-sided
  brown disc, 0.65 × 0.33 studs, darker and more saturated than the plug (§5.2). In the hero it is hidden by the leaf
  bases; in the junction close-up the plug's top is simply flattened with the stems rising from it.
- **Construction:** `_plug(w, h, seed)`: `primitive_ico_sphere_add(subdivisions=2)` (80 tris) scaled to W : H 1.11,
  the top cap vertices pressed to a plane at 0.85 of its height (the flattened top), two broad radius pulls (±5 %),
  no per-vertex noise. Optional `_crown(r, h)`: 8-sided flared frustum 0.75 → 0.65 wide × 0.12, sunk 0.05 into the
  plug top (decision §8). **About 80 + 32 tris.**

## 2. Layout (starting values; tune to §1.2–§1.3 on the sheet-elevation extras)

Build frame: front −Y, +X right, ground z 0, **origin of these coordinates = the plant axis** (bbox centre is about
0.06 to −X of it). Every piece is a transformed copy of a part-builder result (m011 `_paste` pattern).

### 2.1 Plug and stems

| Piece | Where | Size | Notes |
| --- | --- | --- | --- |
| Plug | centre (0, 0, 0.22), bottom at z −0.08 (floor-cut to z 0) | Ø 0.90 × 0.60 before the cut, flattened top at z 0.42 | sits on the ground like the junction close-up; its lower rim shows as the dark brown band at h 0.05–0.16 |
| Crown (optional) | on the flat top, (0, 0, 0.42) | 0.75 → 0.65 × 0.12, sunk 0.05 | under the leaf bases; colour `plug_crown` |
| Main stem | base (0, 0, 0.30), vertical | Ø 0.15, to z 1.62 (0.08 into the main bud) | front f 0.525, side f 0.50, rear f 0.477 |
| Short stem | base (+0.06, −0.06, 0.30), leaning **30°** toward azimuth **−45°** (front-right) | Ø 0.14, length 1.0, tip (+0.42, −0.42, 1.17) | front: right-leaning; side (from −X): leaning to screen right; rear: hidden behind the main stem/bud |
| Main bud | bottom point at (0, 0, 1.54), axis vertical | 0.55 W × 0.68 H, top z 2.22 | the apex; front f 0.507, side f 0.50 |
| Short bud | bottom point at the short stem's tip, axis along the stem (tilted 15°, not the full 30°) | 0.45 × 0.52, centre ≈ (+0.44, −0.43, 1.42) | front f 0.653, h 0.61; side f 0.661, h 0.675 |

### 2.2 Leaves (7 outer + 2 inner, one `_leaf` builder)

Azimuth from +X, counter-clockwise (front = 270°). Base = the leaf's root point on the plug's upper side at r 0.25,
z 0.36–0.40, sunk 0.06 into the plug. "Hump" = the highest point of the leaf's top edge; "tip" = the end point.

| Leaf | Az | L | W | Base pitch | Hump z | Tip (r, z) | Sheet evidence | Maturity (§5.5) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L1 back-right | 35° | 1.70 | 0.70 | 55° | 1.30 | (1.45, 1.10) | front right shoulder h .59–.62; rear left shoulder; top tip r 1.49 | young |
| L2 back | 85° | 1.60 | 0.68 | 40° | 1.00 | (1.35, 0.40) | side far-back tip f 0, h .18; top tip r 1.35 | young |
| L3 back-left | 145° | 1.65 | 0.70 | 55° | 1.40 | (1.30, 0.95) | front left shoulder h .63–.68, tip f .07 h .47; side shoulder h .68; rear right shoulder h .58 | mid |
| L4 left | 190° | 1.65 | 0.72 | 35° | 0.95 | (1.45, 0.30) | front far-left tip f 0.0, h .16 | mid |
| L5 front-left | 240° | 1.50 | 0.65 | 30° | 0.65 | (1.30, 0.08) | top tip r 1.32; the darkest leaf in the top view; mostly hidden in the front | old |
| L6 front | 285° | 1.55 | 0.70 | 30° | 0.66 | (1.35, 0.02) | the front diamond (f 0.42–0.66, top h 0.30, tip at the ground); side front tip | young |
| L7 right | 345° | 1.70 | 0.72 | 35° | 0.92 | (1.50, 0.18) | front right low big leaf (tip f 1.0, h .08); top tip r 1.50 | mid |
| I1 inner front-right | 325° | 1.35 | 0.48 | 68° | — | (0.60, 1.65) | the tall leaf behind the short bud (front f 0.55–0.72 to h .80; side to h .72); top small leaf at 310° | young |
| I2 inner back-left | 150° | 1.25 | 0.45 | 65° | — | (0.55, 1.55) | front leaf behind the main stem (f .33–.48 to h .66); rear upright at screen right (to h .74) | young |

- **Arch:** outer leaves rise at their base pitch for about 0.4 L, then `curl` drops the tip to the listed z. The
  front leaves (L5, L6, L7) touch or nearly touch the ground at the tip; the back leaves (L1, L3) stay high.
- Neighbouring outer leaves overlap 0.1–0.2 at their bases (no gaps at the plug), stay apart toward their tips (the
  top view's notches at r 0.82–0.95).
- Each leaf: own seed, ±5° roll, tip turned ±8° off its azimuth, so the star is not mechanical.
- The inner leaves stand round the stems' bases like a sheath (exploded core) and must not cover the stems above
  h 0.5 in the front view (stems visible from h 0.28 to the buds).

**Expected hero:** about 2.95 × 2.85 × 2.22 including the leaf tips; tune L / reach toward 2.85 × 2.65 (front / side
bbox). Tris (§4.3): 9 leaves × 16–20 = 144–180; 2 buds × 30 = 60; 2 stems × 24 = 48; plug 80 (+ crown 32) →
**330–400 before the union, about 400–550 after.**

## 3. View conflicts and resolutions

### 3.1 The side cell is drawn from the plant's left (−X)

- Evidence: (1) the short bud is in front of the axis (−Y): the rear shows it **behind** the main bud, and the f34
  separates the buds by 0.20 H (a bud at +Y would sit almost behind the main bud from front34); the side shows it at
  screen **right**. (2) The rosette is high at the back and low at the front (front, f34); the side is high at screen
  **left** (h 0.68) and low at screen right (0.40–0.46). Both say screen right = −Y = the front, i.e. a camera at −X.
- **Resolution:** compare the side cell with an **extra render at azimuth 270** (`side_left (270, 4)` and
  `side_left_sheet (270, 8)`), not the kit `side (90, 4)` (which shows the mirror image). Record it in the verifier
  brief. M016/M017's "screen right = +Y" note is about the kit camera at 90; it still holds for that camera.

### 3.2 Buds and stems: 2 in every hero view, 3 in the exploded

- Front, side, rear, top, f34, r34: exactly two buds on two stems. The exploded and parts label "(x3)".
- **Resolution:** **2 buds, 2 stems** on the hero (the hero views govern, WorldModeling §1.1). The exported parts are
  one bud and one stem. Alternative: a third bud would show in every view; not recommended (decision §8).

### 3.3 The r34 is a mirror image

- The r34 puts the short bud on screen right; any camera behind the plant puts a +X bud on screen left (the rear cell
  does). **Resolution:** compare the r34 cell with the kit `rear34 (152, 12)` **flipped left-right**. Judge it by
  shares, bud count, bud separation (0.23 H; ours about 0.26 H) and leaf count, not by left/right order.

### 3.4 The top view's bud positions do not fit

- Top: both buds the same size (0.44), at X −0.21 and +0.29, the right one further back. Front/side/rear: the main bud
  (0.55) on the axis, the short bud at (+0.44, −0.43). **Resolution:** the top governs only the leaf star (seven tips
  at 35/85/145/190/240/285/345°, reach 1.30–1.50, notches 0.82–0.95) and "two buds near the centre". Compare with the
  kit `top (0, 89)`.

### 3.5 Camera elevation and the asymmetric rosette

- The short bud's centre is at h 0.608 in the front (it is near that camera) and 0.675 in the side (far from it);
  its top 0.72 in the front and 0.76 in the rear. With the bud 0.43 off-axis, both give about **6–10°** of elevation.
- Each cell also draws the leaves nearest the camera low and the far ones high. Elevation explains only about 0.1 stud
  of that; the rest is the generated sheet. **Resolution:** build the rosette **high at the back, low at the front**
  (§2.2). That matches the front, f34 and side (from −X) and the rear's two shoulders; the rear's low centre "V" will
  come out higher in our render (its near leaf is L2, which rises to z 1.0). Tolerance on the rear profile at
  f 0.40–0.60 below h 0.4: ±0.12.
- Render extras `front_sheet (0, 8)`, `side_left_sheet (270, 8)`, `rear_sheet (180, 8)` and compare §1.2's profiles on
  those.

### 3.6 Stem sides: 4 (parts, exploded) against 6 (hero, close-up)

- The parts and exploded stems are square prisms; every hero cell and the bud close-up show three tones across the
  stem. **Resolution:** 6 sides everywhere (the hero governs; WorldModeling §6.3 asks 5–8 sides); the exported Stem part
  is the same builder at the parts cell's proportions. Alternative: 4 sides (matches the parts cell exactly). Decision §8.

### 3.7 "Stem / Root Plug" is one brown swatch, but every stem is green

- Swatch `#846347`; hero stems `#4C7823`–`#699122`, exploded stems `#66903C`, parts stem `#669044`, close-up stem
  `#5F853B`. **Resolution:** stems are green (`m018_stem`, §5.4); the brown swatch is the plug.

### 3.8 Leaf (x6) against nine leaves

- The exploded's six = 5 big floating leaves + the centre upright leaf; the top view shows seven outer tips, and the
  front shows two upright inner leaves. **Resolution:** 7 outer + 2 inner = 9 copies of one Leaf part (§2.2); the
  exported `Leaf` part is the parts-cell leaf (L 1.6, W 0.68). Alternative: 6 (label) leaves a 6-point star and loses
  a shoulder. Decision §8.

### 3.9 The three-quarter cells are drawn wider

- f34 W : H 1.57, r34 1.42, against the front's 1.32. A 2.85 × 2.65 rosette seen 28° off axis is not wider than its
  front. As in M017 §3.8: judge the 3/4 views by shares, bud count and separation, leaf count and the front diamond
  leaf, not by W : H. Record the miss.

### 3.10 "Simple clean shapes" against the user's blended-colour rule

- The user's rule wins, and the sheet itself shows the gradients: leaves dark at the base and lime at the tips (§5.3),
  buds pale at the top and warmer at the base, the plug's crown darker than its body. Keep Tint low so it stays clean.

## 4. Construction plan (Stage 1)

1. **Parts first**, each with its own function and checked against its cell:
   - `bud()` (`HerbShrubBud`: 0.55 × 0.68, 30 tris);
   - `stem()` (`HerbShrubStem`: Ø 0.16 × 0.75, 6 sides);
   - `leaf()` (`HerbShrubLeaf`: L 1.6, W 0.68, flat pitch 15°, light curl, as the parts cell);
   - `plug()` (`HerbShrubRootPlug`: 0.85 × 0.77, ico-2, flattened top; crown per decision §8).
   - Render a parts shot (`extra`, about (−20, 15)) laid out as the Parts column (bud, stem, leaf, plug top to
     bottom); compare proportions: bud H : W 1.25, stem L : Ø ≈ 4.7, leaf W : L 0.42, plug W : H 1.11.
2. **Hero:**
   1. `plug` at the centre; `_paste` the 2 stems, 2 buds, 9 leaves at §2 (each leaf with its own L, W, pitch, curl,
      seed).
   2. One exact self-union (m011 `_self_union`), then `union_loose`, then `m004.floor_cut` at z 0.
   3. Origin at the bbox bottom centre; transforms applied.
3. **Budget:** hero about 400–550 (limit 4000; WorldModeling's herb envelope 80–400 is a soft target, the sheet's
   chunky leaves need the extra); each part under 100 (limit 1000). Don't refine leaves or buds beyond §1.4: the sheet
   shows 3–4 facets across a face.
4. **Placeholder keys** (stage 1): `m018_leaf`, `m018_stem`, `m018_bud`, `m018_plug`. Stage 4 adds the others (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure):
   1. **Profiles** (top and width-per-height) within ±0.06 of §1.2 on the 8° extras (side: `side_left_sheet`).
   2. **Shares** (L / U / T, same masks) within ±3 points (U ±2): front 87 / 12 / 1, side 84 / 14 / 2, rear 88 / 9 / 3,
      top 93 / 7 / 0.
   3. **Buds:** main on the axis, top = the apex, 0.55 × 0.68; short bud 0.45 × 0.52 at front (f 0.65, h 0.61) ±0.04,
      side_left (f 0.66, h 0.675) ±0.04, hidden behind the main bud in the rear; H : W 1.2–1.3; five-facet apex.
   4. **Stems:** two, 6-sided, Ø 0.13–0.17; main vertical, visible from h 0.28 to the bud; short stem 25–35° in the
      front, 35–40° in the side_left.
   5. **Leaves:** 7 outer tips in the top at 35/85/145/190/240/285/345° ±10°, reach 1.30–1.50, notches 0.8–1.0; front
      diamond leaf tip at the ground; back shoulders at h 0.58–0.68; two upright inner leaves reaching h 0.72–0.80;
      each leaf a pyramid-topped wedge with a visible keel thickness from the side (WorldModeling §17.2).
   6. **Plug** visible only as a brown band at h 0.05–0.16 between the leaf bases, 0.8–1.1 wide.
   7. **Parts against their cells** (§4.1).
   8. **Hero size** 2.85 × 2.65 × 2.2 (±0.15 / ±0.15 / ±0.1).

## 5. Colour plan (Stage 4)

### 5.1 Swatches (flat; medians of a 24 × 15 box inside each, x 809–833)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Bud | (809,1207,833,1222) | `#F9DFAD` | 39°, 0.31, 0.98 |
| Leaf Light | (809,1235,833,1250) | `#99B841` | 76°, 0.65, 0.72 |
| Leaf Dark | (809,1263,833,1278) | `#608441` | 92°, 0.51, 0.52 |
| Stem / Root Plug | (809,1292,833,1307) | `#846347` | 28°, 0.46, 0.52 |

- Bud swatch ≈ the rendered bud middle (`#F4D7A5`–`#F6DAAC`): use the render.
- Leaf Light ≈ the rendered tip band (`#8BB448`) and lit quartiles (`#A3C550`); Leaf Dark ≈ between the rendered
  middle (`#6B9643`) and the base band (`#446F33`).
- Stem / Root Plug: matches the exploded/parts plug (`#81664F`–`#957962`), not the stems (§3.7).

### 5.2 Rendered regions (`samp18.py`–`samp20.py`; median, lit quartile, shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Green, front / side / rear | V | L | `#6B9643` / `#618C46` / `#699344` | `#A3C550` / `#A8C458` / `#9CC04E` | `#3C632E` / `#375C25` / `#3C6129` |
| Green, f34 / r34 / top | V | L | `#6D9944` / `#608A3F` / `#67933D` | `#A1C350` / `#9EC24C` / `#92B94E` | `#3E6630` / `#355725` / `#365B2B` |
| Leaves, exploded | (95,860,640,1120) | L | `#699341` | `#94B94A` | `#4A7238` |
| Leaf, parts | (705,940,850,1038) | L | `#6C9A4B` | `#98BD4D` | `#5C8949` |
| Leaves, junction / underside close-ups | cu boxes | L | `#638641` / `#507335` | `#88AE4F` / `#668B3E` | `#415D2F` / `#355329` |
| Main stem, front / side / rear | (146,572,152,615) / (389,565,396,622) / (631,560,638,598) | L | `#699122` / `#4C7823` / `#496E24` | `#77A125` / `#66932A` / `#6E9729` | `#517A1A` / `#375C1A` / `#39591E` |
| Stems, f34 main / short | (279,215,292,330) / (318,290,330,330) | L | `#517820` / `#53791A` | `#729A27` / `#638720` | `#355A0F` / `#33560F` |
| Stems, exploded / parts / close-up | | L | `#66903C` / `#669044` / `#5F853B` | `#8DB34A` / `#79A34A` / `#719639` | `#497136` / `#4E723E` / `#42632D` |
| Buds, front / side / rear / top | V | U | `#F6D9A5` / `#F6DAAC` / `#F1D4A5` / `#F0D6A4` | `#FEF0CB` / `#FEEECA` / `#FDEBC6` / `#FEF2D0` | `#D0B87F` / `#CEB781` / `#CDB583` / `#D0B87F` |
| Buds, f34 / r34 / exploded / parts / close-up | | U | `#F2D4AA` / `#F4DAAA` / `#F0D1A2` / `#F8DDAF` / `#F6D8A5` | `#FEEECA` / `#FEEEC9` / `#FEEBC4` / `#FEEFC9` / `#FEEEC8` | `#CBB37E` / `#CFB57F` / `#CCB185` / `#D5BA93` / `#D5B885` |
| Plug, parts / exploded / exploded crown disc | | T | `#957962` / `#81664F` / `#795B40` | `#B19076` / `#A07E61` / `#967252` | `#705B49` / `#695542` / `#5B4631` |
| Plug, junction / underside close-ups | | T | `#6B533D` / `#735A44` | `#947153` / `#A07D60` | `#4D3C2A` / `#67523D` |
| Plug in the hero (under the leaves), front / side / rear | V | T | `#352A1C` / `#3A2F1F` / `#3B2F20` | `#403525` / `#423626` / `#4A3C2A` | `#2F2417` / `#312618` / `#33291B` |
| Ground shadow, front | (60,676,230,690) | O | `#C4BEB4` | | |

Deciles (dark → light), front:

```
green  #2A4A20 #406833 #4C753A #56813E #638E44 #77A348 #85B14D #91BB52 #9FC34B #ABCB50
bud    #CCB477 #D2B97F #D8C192 #F1D498 #F4D7A3 #F8DBA5 #FBE0AD #FCE5B9 #FEEEC9 #FEF2D1
```

### 5.3 How the colour works

**Leaves.**
- One yellow-green family: tips and lit faces lime (77–83°, sat 0.60), the base and shade faces deep blue-green
  (100–106°, sat 0.55). Lit vs shade within a leaf is the sun (the pyramid top splits each leaf into a lit and a shaded
  half); never paint it.
- **Base → tip gradient** (top view, all leaves, by distance from the axis; the clearest painted signal):

  | r (studs) | 0.0–0.3 | 0.3–0.6 | 0.6–0.9 | 0.9–1.2 | 1.2–1.5 |
  | --- | --- | --- | --- | --- | --- |
  | Median | `#2A491A` | `#446F33` | `#5C893C` | `#7BA442` | `#8BB448` |
  | Lit | `#365A27` | `#679744` | `#80AC4D` | `#9BBE4E` | `#A2C451` |

  Even the lit quartile climbs from `#365A27` to `#A2C451`, so this is paint plus canopy shade at the centre.
- **Per leaf** (top view, r 0.75–1.25): young/bright L6 285° `#91B643`, L1 35° `#86B248`, L2 85° `#85AF48`; mid
  L7 345° `#78A94B`, L3 145° `#769F3E`, L4 190° `#6C943A`; old/dark L5 240° `#537C35`.
- **By height** (front, bands 0.0–0.8 h): `#779343 #5E863E #79A543 #7BAA47 #4D7637 #739E49 #8BB44E #84AF53`: no
  clean vertical trend (the base→tip field dominates).
- The leaf undersides (underside close-up) are darker: `#507335` against `#638641` on the junction close-up.

**Stems.** More saturated and yellower than the leaves (hue 82–93°, **sat 0.70–0.77**): `#5E8B27`–`#69962A` in the
sun, `#385F16` at the base among the leaves and `#3F671F` right under the bud (both shade). Paint one stem colour;
the studio's shade does the rest.

**Buds.** Warm cream (37–42°). **Top → base gradient** (bud thirds, front / f34 / r34):
top `#FDECC5` / `#FDECC8` / `#FDE5BF` (sat 0.21–0.25); middle `#F4D7A5` / `#F2D5A7` / `#F4D6AA` (0.30–0.32); bottom
`#D3BA7E` / `#CDB47E` / `#D2B781` (0.39–0.40). The bottom third's **lit** quartile is still more saturated
(`#F1D59B`, sat 0.36, against the top's `#FEF3D3`, 0.17), so the base is painted warmer/yellower, not only shaded.
No green at the bud base ("simple junction").

**Plug.** Greyish warm brown (27–29°): the parts/exploded plug `#81664F`–`#957962`; the crown disc darker and more
saturated `#795B40` (sat 0.47); in the hero it is in deep shade under the leaves (`#352A1C`).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered medians, not swatches. Kinds: `K.sample(..., "green")` for leaves and stems
(passes: g > r + 8, g > b + 25, sat > 0.3); **`"all"` on tight bud boxes** (cream fails both `"brown"` (sat 0.3 < the
filter) and `"vivid"`); `"brown"` for the plug (`#846347`: r − g 33, sat 0.46: passes).

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m018_leaf` | `#6E9A43` (view medians `#608A3F`–`#6D9944`; r 0.9–1.2 band `#7BA442`) | leaf middles | rough 0.85, `low_spec` |
| `m018_leaf_tip` | `#8EB548` (tip band `#8BB448`; young leaves `#85AF48`–`#91B643`; swatch Leaf Light `#99B841`) | outer 35 % of each leaf; young leaves | rough 0.85, `low_spec` |
| `m018_leaf_base` | `#4E7838` (r 0.3–0.6 band `#446F33`; old leaf `#537C35`; swatch Leaf Dark `#608441`) | inner 25 % of each leaf, keel/underside rows, old leaf L5 | rough 0.85, `low_spec` |
| `m018_stem` | `#62902A` (hero sun-side medians `#5E8B27`–`#699122`; exploded `#66903C`) | both stems | rough 0.8, `low_spec` |
| `m018_bud` | `#F5D8A8` (view medians `#F0D6A4`–`#F6DAAC`; swatch `#F9DFAD`) | bud middles | rough 0.7, spec 0.3 |
| `m018_bud_tip` | `#FCEAC6` (top thirds `#FDE5BF`–`#FDECC8`) | top 25 % of each bud | rough 0.7, spec 0.3 |
| `m018_bud_base` | `#E5C78C` (bottom-third lit `#EED19D`–`#F1D59B`; medians `#CDB47E`–`#D3BA7E` incl. shade) | bottom 30 % of each bud | rough 0.7, spec 0.3 |
| `m018_plug` | `#86684F` (exploded `#81664F`; parts `#957962`; swatch `#846347`) | plug body | rough 0.95 |
| `m018_plug_crown` | `#765940` (exploded crown `#795B40`; junction close-up `#6B533D`) | plug top / crown, ground contact | rough 0.95 |

- **Calibration warnings:**
  - Calibrate `bud_base` on the bottom third of an **unshadowed** bud (the parts-shot bud), then re-measure the hero's
    bud thirds: the stem/leaf shade adds the rest. Don't push `bud_base` toward `#D0B87F` (that's the shade quartile).
  - The cream bud sits near the white clip under the key light; lower its specular (0.3) rather than its colour if the
    top third blows out to `#FFFFFF`.
  - Kit memory: calibrated greens come out darker than the painted sheet; trust the render match. `leaf_tip` must
    stay under hue 85° (lime, not grass green).
  - `stem` is far more saturated than `leaf` (0.70 vs 0.55); calibrate it separately on the f34 main-stem box
    `(279,215,292,330)`, not together with leaves.
  - Calibrate the plug on the parts shot (unshadowed). In the hero it must come out very dark (`#352A1C`–`#3B2F20`)
    from the leaf shade; if it doesn't, darken only its upper half toward `plug_crown`, never the whole plug.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Leaves** (field = each leaf's own along-length parameter t = distance from its base / L, computed from the leaf's
  construction frame, so it follows the leaf, not world z):
  - t < 0.25 → `leaf_base`; 0.25–0.65 → `leaf`; t > 0.65 → `leaf_tip`, 3 steps across each boundary, broad noise
    ±0.08 on t so the bands don't read as stripes.
  - Maturity offset per leaf: young (L1, L2, L6, I1, I2) shift the bands 0.12 toward the base (more tip colour); old
    (L5) shift 0.2 toward the tip and mix 35 % `leaf_base` into its middle; mid (L3, L4, L7) as is.
  - Keel faces (the vertices below the outline plane, a construction-known set) → +0.25 toward `leaf_base`
    (the darker underside of the close-up).
  - Leaf bases within 0.12 of the plug → `leaf_base` (they meet the plug with a hard material edge).
- **Stems:** `stem` body; z < 0.6 → 35 % `leaf_base` (among the leaf bases); the top 0.06 under the bud stays `stem`
  (hard edge to the bud).
- **Buds** (field = height within each bud, 0 at its bottom point): < 0.30 → `bud_base`; 0.30–0.75 → `bud`; > 0.75 →
  `bud_tip`; 3 steps.
- **Plug:** `plug` body; top (z > 0.32) → `plug_crown`; z < 0.06 → 50 % `plug_crown` (ground contact); broad
  noise patches (scale 0.3, level 0.3) between `plug` and a 60 % `plug_crown` mix.
- **Hard edges only** where materials meet: bud against stem, stem against plug, leaf against plug.

### 5.6 Texture (Tint) and finish

- **Tint:** per piece `tint_var` about 0.04 (each leaf and each bud differs slightly).
  - Leaves: `K.texture` amp 0.035, scale 0.5 (broad, per facet group, never confetti).
  - Stems: amp 0.03.
  - Buds: amp 0.02 (the sheet's buds are clean).
  - Plug: amp 0.05, scale 0.3 (soil mottling).
- **Finish:**

  | Material | Roughness | Specular | Metal | Notes |
  | --- | --- | --- | --- | --- |
  | Leaf keys | 0.85 | `FOLIAGE_SPEC` (`set_colour(low_spec=True)`) | 0 | matte faceted foliage |
  | Stem | 0.8 | `FOLIAGE_SPEC` | 0 | matte |
  | Bud keys | 0.7 | 0.3 | 0 | satin: the sheet's bud tops reach `#FEF3D3`; opaque, no emission |
  | Plug keys | 0.95 | normal | 0 | matte soil |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- Green median within about 10 levels of `#6B9643` (front) / `#618C46` (side_left) / `#699344` (rear); the top
  view's radius bands in §5.3 within about 12 levels and in order (centre darkest, tips lightest); the per-leaf groups
  in order (young > mid > old).
- Bud median within 8 levels of `#F5D8A8`; thirds in order (top palest, base warmest), each within 12 levels.
- Main stem (sun side) within 12 of `#62902A`, sat ≥ 0.65.
- Plug in the hero within 15 of `#3A2E1F`; plug in the parts shot within 12 of `#86684F`.
- Shares per §4, step 5.2.

## 6. Joins and contact (this sheet has no cracks, pits or seams)

- **Leaves into the plug:** each leaf base sunk 0.06 into the plug's upper side, bases overlapping their neighbours
  0.1–0.2 (no slots of daylight at the centre from the top view: its centre is `#2A491A` leaf, not plug).
- **Stems into the plug and buds:** stems start 0.1 inside the plug and run 0.08 into the bud's bottom cone; the bud's
  bottom point is buried in the stem (the "simple junction": no collar, no sepals).
- **Plug on the ground:** flat cut base at z 0 (m004 `floor_cut`), the plug's rounded lower rim visible above it.
- No floating pieces, no coplanar contact (exact booleans, pitfall 12).

## 7. Lighting and VFX plan (Stages 5 and 6)

**What the sheet shows:** an ordinary lit herb. No glow, light, sparkle, particles or haze anywhere; the pale bud
tops are diffuse highlights (their shade facets go to `#CBB37E`), not emission. WorldModeling §1.2 (no ordinary asset
"recolored neon with a glow halo") and §11 ("healing herb" is an art label; no effect implied).

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces** (the exporter turns emission ≥ 1.0 into flat Neon parts, which would erase the buds' facets),
  no PointLight: nothing on the sheet glows.
- **Studio note (Requires Manual Validation):** check in Studio that the cream buds don't clip to white under the
  game's sun and that the leaf tip/base gradient survives the palette export.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`,
  `vapour`, `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `dust`. No new kind is proposed.
- **Recommended: none.** The sheet shows no effect; m009 and m011–m017 decided against harvest sockets. Record
  "skipped: sheet shows no VFX".
- **Option** (decision §8): `harvest_hit` at the front (0, −1.4, 0.9) and `harvest_deplete` at the plug (0, 0, 0.4)
  with colour overrides `["#8EB548", "#F5D8A8"]` (leaf and bud chips), as R05 `HealingHerb` shipped. Only if the main
  session wants hit feedback on gather nodes.
- Not recommended: `crystal_glow` / `ore_glint` / `rune_glow` on the buds ("healing" is a label; it would read as magic).

## 8. Naming and decisions for the main session

Names owned elsewhere (`git grep` of the repo; `FlintbornWorldKit.blend` is zstd-compressed, so it was decompressed
with Python 3.14's `compression.zstd` and searched: `HealingHerb` occurs 48 times there, `HerbShrub` and `m018_` 0):
- R05 kit: `HealingHerb`, `HealingHerbBud`, `HealingHerbLeaf`, `HealingHerbRootPlug`, `HealingHerbSprig`,
  `HealingHerbDepleted`, keys `r05_herb_leaf`, `r05_herb_stem`, `r05_bud`, `r05_root`;
- lobby / build_05: `BroadLeafHerb`;
- `src`: NodeCatalog / BiomeCatalog / ResourceService node id `HerbShrub` (an id, not a mesh: the M017 precedent
  `BerryBushNode` takes the node id plus `Node`); EventCatalog `WildHerbPatch`.
- `M.mk` would silently rename a clash to `<name>M018`, so avoid them all.

**Proposed names** (none found in the repo or the decompressed kit .blend; `m018_` is unused too):

| Object | Part | Why |
| --- | --- | --- |
| `HerbShrubNode` | hero | the NodeCatalog id + `Node`, like M017 `BerryBushNode`; R05 owns `HealingHerb` |
| `HerbShrubBud` | Flower Bud (x3) | R05 owns `HealingHerbBud` |
| `HerbShrubStem` | Stem (x3) | |
| `HerbShrubLeaf` | Leaf (x6) | R05 owns `HealingHerbLeaf` |
| `HerbShrubRootPlug` | Root Plug (x1) | R05 owns `HealingHerbRootPlug` |

- Fallback set if the main session prefers the sheet's name: `HealingHerbNode`, `HealingHerbStem` are free, but the
  `HealingHerbBud/Leaf/RootPlug` part names are R05's, so the parts would need `HealingHerbBudM018`-style names. Not
  recommended.
- Palette keys `m018_*` (§5.4). Collection `Kit/M018 Healing Herb`.

**Decisions needed:**
1. **Size** (§1.1): 2.85 × 2.65 × 2.2 (recommended: 0.40 C, the top of WorldModeling's flowering-herb range; matches the
   game's 3 × 2 × 3 placeholder), or mid-range 0.30 C (2.15 × 2.0 × 1.65).
2. **Bud and stem count** (§3.2): 2 + 2 as every hero view shows (recommended) or 3 + 3 (the label).
3. **Leaf count** (§3.8): 7 outer + 2 inner upright = 9 (recommended) or 6 (the label).
4. **Stem sides** (§3.6): 6 (recommended: hero views, close-up, WorldModeling §6.3) or 4 (parts cell).
5. **Crown disc** (§1.4): include it as a low flared 8-sided disc on the plug top, mostly hidden (recommended: it is the
   exploded's joinery and gives the leaf bases something to sit on; +32 tris), or omit it.
6. **Exports:** hero plus `HerbShrubBud`, `HerbShrubStem`, `HerbShrubLeaf`, `HerbShrubRootPlug` (5 objects,
   recommended). A harvested/budless variant is not on the sheet; not built unless asked (WorldModeling §6.7 would make
   it the hero minus buds and stems).
7. **Stage 5/6:** no Neon, no light, no VFX (recommended); or the R05-style `harvest_hit` / `harvest_deplete` pair.
8. **Side comparison camera** (§3.1): compare the sheet's side cell with an extra render at azimuth 270 (recommended),
   and the r34 with the kit rear34 flipped (§3.3).
9. **Names** as proposed.

## 9. Pitfalls to avoid

1. **Flat card leaves or spikes.** Each leaf is a closed chunky wedge with a pyramid top (apex 0.11 L) and a keel;
   it must show thickness from the side. Not `NS["leaf"]` narrow serrated leaves, not cones (WorldModeling §6.1, §18).
2. **Pillow leaves.** Chunky is not puffy: one apex and one keel vertex, straight facets; no smooth shading, no
   subdivision.
3. **A symmetric rosette.** The sheet's rosette is high at the back and low at the front (§2.2, §3.5); a radially
   identical star misses both shoulders and the front diamond leaf.
4. **Comparing the side with the kit side (90).** The sheet's side is drawn from −X (§3.1); the kit side is its mirror.
   Use `side_left (270, …)`. The r34 is a mirror too (§3.3).
5. **The short bud behind the main bud.** It is in front-right (+X, −Y): separated in the front and f34, hidden behind
   the main bud only from the rear.
6. **Jewel or ball buds.** A bare icosahedron is a gem; an ico-2 is a smooth ball. Use the 5-ring ovoid (§1.4):
   apex fan, two bands, bottom cone, H : W 1.25.
7. **A collar or sepals under the buds.** The sheet's junction is the bud's cone sitting straight on the stem.
8. **Brown stems.** The "Stem / Root Plug" swatch is brown, but every stem on the sheet is a saturated green (§3.7).
9. **A visible tree stump.** The plug shows only as a dark band at the ground (WorldModeling §18 "tree stump with
   leaves"); keep it Ø 0.9 and covered by the leaf bases above z 0.35.
10. **Colour by facing.** The lit/shaded halves of each leaf are the sun. Paint base → tip, per leaf maturity and the
    keel set only; `K.check` facing correlation < 0.5.
11. **Leaves too blue or too yellow.** Median hue about 91°; tips 77–85°; base 95–105°. Stems hue 82–90°, sat ≥ 0.65.
12. **Exact booleans.** Overlap everything: leaf bases 0.06 into the plug and 0.1–0.2 into each other, stems 0.1 into
    the plug and 0.08 into the buds, plug below z 0 before the floor cut. No coplanar contact; remove slivers with
    m011's `_tidy` / `_desliver`, keep triangles above 5° where nine leaf bases meet the plug.
13. **Stage 2 over-cleaning.** Don't decimate the leaves below their 8-point outline or the buds below 5 sectors; keep
    each leaf's apex and keel (they are its silhouette and its colour bands).
14. **Naming clashes** with R05's `HealingHerb*` and the lobby's `BroadLeafHerb` (§8). Only one agent drives Blender at
    a time. No commits, pushes or exports in stage agents.

## Decisions (main session, 2026-10-28)

All recommendations are accepted:
1. Size 2.85 × 2.65 × 2.2.
2. Buds and stems: 2 + 2.
3. Leaves: 9 (7 outer, 2 inner upright).
4. Six-sided stems.
5. Include the crown disc.
6. Export the herb plus four parts.
7. No effects; skip stages 5 and 6 and record why.
8. Compare the side view against an extra render at az 270, and the rear three-quarter flipped.
9. Names as proposed: `HerbShrubNode`, `HerbShrubBud`, `HerbShrubStem`, `HerbShrubLeaf`, `HerbShrubRootPlug`.

## Stage 1 (modelling), modeller 2026-10-28

Builder `art/blender/kit/mcp/m018.py` (`build()`), work file `art/blender/assets/kit/wip/M018.blend` (background
session on port 9879). Collection `Kit/M018 Healing Herb`; objects `HerbShrubNode` (hero), `HerbShrubBud`,
`HerbShrubStem`, `HerbShrubLeaf`, `HerbShrubRootPlug` (decision 9).

**Part builders.** Each has its own function, and the hero is assembled only from them.
- `bud_mesh`: the 5-ring ovoid exactly as in 1.4 (bottom point; ring A at 0.30 H, 0.8 R; ring B at 0.56 H, 1.0 R,
  turned 36°; ring C at 0.80 H, 0.8 R; apex). 30 tris. Part 0.51 × 0.52 × 0.68 (H : W 1.32, as the parts cell).
- `stem_mesh`: a 6-sided prism with 3 rings, taper 1.0 → 0.88 and flat caps (decision 4). 32 tris. Part Ø 0.15 × 0.75.
- `leaf_mesh` with `leaf_path`:
  - the midline is a cubic Bézier set by the base pitch and the tip slope; the handle scale is solved so the
    midline's highest point reaches a given z;
  - a 12-point ovate outline (half-widths 0.32, 0.46, 0.50, 0.47 and 0.36 W at t 0.12 … 0.89);
  - the edges droop 0.42 × their distance from the midrib, giving the sheet's tent-shaped leaves. The droop is half
    along the leaf normal and half straight down, so a hard-arched leaf never folds through itself;
  - three ridge points on top (t 0.30, 0.50, 0.72; camber 0.07, 0.08, 0.045 L) and three keel points below, with the
    same topology.
  - 32 tris.
- `plug_mesh`: an ico-2 sphere (80 tris) with two broad ±5 % pulls and its top pressed flat. Part 0.84 × 0.86 × 0.77
  (W : H 1.11).
- `crown_mesh`: an 8-sided flared disc (decision 5), hero only.

**Hero layout** (plant axis at the origin, front −Y):
- Plug: Ø 0.9, centre z −0.04, top pressed to 0.16, cut flat at the ground. Crown 0.48 → 0.56 Ø × 0.10 at z 0.10.
- Main stem: from z 0.06, 1.56 long, Ø 0.15. Main bud: bottom 1.52, top 2.20.
- Short stem: leans 23° toward azimuth −50°, 1.25 long. Short bud: 0.45 × 0.52, tilted 15°; bottom (0.35, −0.40, 1.12),
  top (0.44, −0.51, 1.62).
- Leaves (azimuth, W, midline peak z, tip (r, z)):

  | Leaf | Azimuth | W | Peak z | Tip (r, z) |
  | --- | --- | --- | --- | --- |
  | L1 | 22° | 1.08 | 1.32 | (1.52, 1.05) |
  | L2 | 88° | 1.06 | 0.58 | (1.38, 0.04) |
  | L3 | 148° | 1.08 | 1.30 | (1.50, 1.00) |
  | L4 | 200° | 1.08 | 0.80 | (1.50, 0.25) |
  | L5 | 244° | 1.00 | 0.55 | (1.30, 0.04) |
  | L6 | 285° | 1.06 | 0.55 | (1.35, 0.00) |
  | L7 | 338° | 1.08 | 0.80 | (1.55, 0.15) |
  | I1 | 325° | 0.66 | upright | (0.62, 1.75) |
  | I2 | 150° | 0.64 | upright | (0.58, 1.62) |

- The leaf roots start at r 0.06, inside the plug and the stems.

**Changes from the study's layout, and why** (each found by rendering every view against the sheet):
- **Leaf roots and width.** The study's §2.2 numbers (roots at r 0.25 on the plug's upper side, a quadratic arch)
  gave narrow, claw-like leaves that hooked down, and left a fully exposed brown ball. The sheet's leaves are broad
  (W ≈ 0.6 L) and tent-shaped with a strong midrib, and they rise from the plug's centre; the plug shows only as a
  dark band. Changes:
  - roots inside the plug, at r 0.06;
  - a lower plug that shows less (top 0.16; Ø 0.9 kept);
  - wider leaves (W 1.0–1.08, against the study's 0.65–0.72);
  - the drooping flanks.
- **L2 (88°) is low**: peak 0.58, tip on the ground, against the study's 1.0. The sheet's rear cell has a low centre
  "V" between two shoulders. That is a leaf pointing at the rear camera, drawn as a diamond like L6 at the front. The
  side cell's high back shoulder comes from L3 (148°).
- **L1 moved from 35° to 22°**, so the front view's right shoulder reaches f 0.90 (h 0.58, against the sheet's 0.59).
- **Stems are 1.56 and 1.25 long** because the plug is lower. The buds sit exactly where §2.1 puts them.
- **The leaf grew from the study's 16–20 tris to 32.** One keel point fanned to the whole outline cut through the top
  of a hard-arched leaf, and an exact union with that leaf then deleted the whole hero (volume 0). Three ridge points
  and three keel points follow the bend.

**Renders for comparison.**
- `M.views` writes the kit views plus these extras: `front_sheet (0, 8)`, `side_left (270, 4)`,
  `side_left_sheet (270, 8)`, `rear_sheet (180, 8)`, `f34_sheet (−28, 12)`, `r34_sheet (152, 12)`, `top_sheet (0, 89)`,
  `exploded` and `part_*`.
- **The `*_sheet` extras use a 3× longer lens** (`SHEET_LENS`; the camera backs off to keep the same fill). The
  sheet's cells are almost orthographic, while the kit camera (about 3 × the radius away) blows the near leaves up.
  Measure on these.
- `M018_sheet_compare.png`: the sheet cell beside our long-lens render, per view (ours flipped for the r34, §3.3).
- `m018.measure()` runs the study's masks on both.

**Stage 1 acceptance** (sheet → ours, long-lens renders):

| View | W : H | L / U / T shares (%) | Notes |
| --- | --- | --- | --- |
| Front | 1.32 → 1.21 | 87 / 12 / 1 → 89 / 7.5 / 3.4 | top profile within ±0.06 at 15 of 21 columns |
| Side (270) | 1.20 → 1.13 | 84 / 14 / 2 → 85 / 7 / 8 | back high, front low, as the sheet |
| Rear | 1.28 → 1.09 | 88 / 9 / 3 → 92 / 7.5 / 0.7 | centre V (L2) and both shoulders |
| Top | 1.08 → 1.11 | 93 / 7 / 0 → 93 / 6 / 0.4 | seven tips at 22, 88, 148, 200, 244, 285 and 338° |

- **U is low and T is high in every view, for one reason.** The studio shades the buds' undersides much harder than
  the sheet does, so their shaded faces fall into the plug mask (T). The plug itself measures `#3D3227` (r34) and
  `#1E1711` (side, shade quartile), against the sheet's `#352A1C`–`#3C2F1F`.
- **The f34 and r34 W : H** (1.19 and 1.12) stay below the sheet's 1.57 and 1.42 (§3.9: those cells are drawn wider).
- **Leaf tip angles** against the study's 35, 85, 145, 190, 240, 285 and 345°: all within 10° except L1 (22°, moved
  for the front's right shoulder; 13° off).

## Stage 2 (optimisation and cleanup)

**Union**
- The 15 shells (plug, crown, 2 stems, 2 buds, 9 leaves) are joined one at a time with exact booleans (`_union`).
  Each result is checked against the volumes going in, and stray verts are dropped before each union.
- All 15 joined on the first try; none failed.

**Self-intersections** are checked after every step (`_self_hits`):
- the union output is clean;
- the merge after the union uses 0.0005 (`UNION_MERGE`); 0.004 pinched thin leaf flanks into crossing faces;
- the sliver pass moves a vert at most 0.06 (`CLEAN_MOVE`); m011's 0.18 folded flanks through each other;
- every later sliver collapse runs through `_guarded`, which undoes it if the number of crossings rises.

**Floor:** cut at z 0 (`m004.floor_cut`). The floor faces are painted plug shade near the plug and leaf base under
the leaves, with Tint 0.95.

**Hero `HerbShrubNode`**
- **826 tris** (budget 4000), 406 verts.
- Size **2.94 × 2.69 × 2.20**. Target 2.85 × 2.65 × 2.2 (tolerance ±0.15 / ±0.15 / ±0.1): inside.
- 1 shell. 0 non-manifold, 0 boundary and 0 wire edges; 0 loose verts, 0 zero-area faces, 0 duplicate verts, 0 n-gons.
- Normals outward; **0 self-intersections**.
- Origin at the bottom centre, transforms applied, no modifiers.
- Two slivers under 5° remain (smallest corner 3.94°, area at least 0.001 sq stud). Both are at r < 0.15, hidden
  inside the leaf-root cluster. Collapsing them created crossings, so the guard kept them.

**Parts:** Bud 30, Stem 32, Leaf 32 and RootPlug 80 tris. Each is 1 shell, all checks 0, no self-intersections.

**Against the study's estimate:** the study expected 400–550 tris. The 32-tri leaf (stage 1) and the union seams make
826. WorldModeling's 80–400 envelope for an ordinary herb is a soft target; the sheet's chunky tent leaves need the
facets.

## Stage 3 (UV)

`M.smart_uv` (Smart UV islands re-unwrapped ANGLE_BASED, margin 0.008), then `m012._uv_unfold`.

| Object | Islands | Overlaps | Flipped | Min gap | Border | Density min / med / max | Conformal p95 / worst | Worst angle change |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HerbShrubNode | 188 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.016 / 1.077 | 2.98° |
| HerbShrubBud | 13 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.0 / 1.0 | 0° |
| HerbShrubStem | 8 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.0 / 1.0 | 0° |
| HerbShrubLeaf | 3 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.017 / 1.017 | 0.75° |
| HerbShrubRootPlug | 9 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.081 / 1.088 | 4.44° |

The hero has 115 texels per stud at 1024². The exporter writes its own palette UVs; this layer is clean for FBX/OBJ.

## Stage 4 (materials, colour, texture)

**Pass 1, dome** (`K.calibrate` with the §5.4 targets; the rendered median against the target in brackets):

| Key | Calibrated hex | Rendered median (target) |
| --- | --- | --- |
| `m018_leaf` | `#5B8040` | 107, 151, 67 (`#6E9A43`) |
| `m018_leaf_tip` | `#739444` | 139, 177, 71 (`#8EB548`) |
| `m018_leaf_base` | `#436636` | 77, 118, 55 (`#4E7838`) |
| `m018_stem` | `#537829` | 97, 141, 41 (`#62902A`) |
| `m018_plug` | `#6A5644` | 132, 104, 79 (`#86684F`) |
| `m018_plug_crown` | `#5E4936` | 117, 89, 65 (`#765940`) |

The bud keys could not be calibrated on the dome. The cream clips on the lit faces, and the solver pushed `bud_tip`
pink (`#F3BEAA`). The bud keys were set by hand at hue 36–42° and fixed in pass 2.

**Pass 2, hero renders** (long-lens views, study masks; sheet → ours):

| Region | Front | Side | Rear | f34 | r34 | Top |
| --- | --- | --- | --- | --- | --- | --- |
| Green median | #6A9643 → #68913E | #618C46 → #6F9845 | #699343 → #5A813A | #6D9844 → #689444 | #5F8A3F → #60843C | #67933D → #6A943F |
| Bud median | #F6D9A5 → #EFD3A8 | #F6DAAC → #EED1AA | #F1D4A5 → #D1BB90 | #F2D4AA → #F0D3A8 | #F4DAAA → #C9B491 | #F0D6A4 → #EED3B1 |

- **Green lit / shade quartiles:** front `#A3C551` / `#3C632B` → `#96C252` / `#375622`; f34 `#A0C352` / `#3E652F` →
  `#9FC852` / `#3B5C26`.
- **Bud thirds (top / middle / base):**
  - front: `#FBE1B5` / `#D5BC8C` / `#E7D49B` → `#FFE0BB` / `#F0D3A5` / `#A08D6A`;
  - f34: `#FDECC8` / `#F2D5A8` / `#CCB47B` → `#FFE9BE` / `#F1D3A5` / `#B29C76`.
- **Plug in the hero:** sheet `#352A1C` (front), `#3A2F1F` (side), `#3C2F1F` (r34); ours `#1E1711` (side, shade
  quartile), `#3D3227` (r34).
- **Top-view radius bands** (r 0–0.3 … 1.2–1.5): sheet `#2B491B #467033 #5D8B3C #7DA543 #8DB548`; ours
  `#416330 #4D7234 #628D3E #759D45 #94B952`. In order: centre darkest, tips lightest.

**Changes in pass 2:**
- `leaf_tip` → `#7A9C48`: the lit quartile was low at first, then the tip band ran high.
- `leaf` → `#5A8044` and `leaf_tip` slightly bluer: ours ran 6° too yellow.
- `leaf_base` → `#3A5A2E`, plus a **rosette-heart field**: leaf faces within 0.95 of the axis move up to one full
  step toward `leaf_base`, by horizontal distance (the sheet's dark top-view centre). The inner leaves changed from
  `young` to `mid`.
- Buds `#C0AE90`, tip `#C7B49E`, base `#E1CD9B`: the tip had clipped to white and gone yellow.
- New key **`m018_plug_shade #2F2519`** for the hero's plug and crown: soil deep under the leaves. The studio lit the
  plug `#8A765A`, where the sheet draws it `#352A1C`. The part plug keeps `plug` and `plug_crown`.

**Final palette** (`PALETTE` in the builder):

| Key | Hex | Finish |
| --- | --- | --- |
| `m018_leaf` | `#5A8044` | rough 0.85, foliage specular |
| `m018_leaf_tip` | `#7A9C48` | rough 0.85, foliage specular |
| `m018_leaf_base` | `#3A5A2E` | rough 0.85, foliage specular |
| `m018_stem` | `#537829` | rough 0.8, foliage specular |
| `m018_bud` | `#C0AE90` | rough 0.7, specular 0.3 (satin) |
| `m018_bud_tip` | `#C7B49E` | rough 0.7, specular 0.3 |
| `m018_bud_base` | `#E1CD9B` | rough 0.7, specular 0.3 |
| `m018_plug` | `#6A5644` | rough 0.95 |
| `m018_plug_crown` | `#5E4936` | rough 0.95 |
| `m018_plug_shade` | `#2F2519` | rough 0.95 |

The hero has 19 material slots: the base keys plus the `K.mix_key` steps.

**Blending** (by position only, never by facing):
- **Leaves:**
  - along each leaf's own construction parameter t, a base → tip ladder: −1 at t 0.12, 0 from 0.36 to 0.58, +1 at 0.88,
    in quarter steps;
  - broad noise of ±0.08 on t;
  - a maturity shift: young +0.12; old −0.2 with 35 % base in the middle (L5);
  - keel faces −0.25 (darker undersides);
  - the rosette-heart field.
- **Buds:** by height in the bud, base → body → tip at 0.20 / 0.42–0.62 / 0.86.
- **Stems:** `stem` → 35 % `leaf_base` below z 0.8 (among the leaf bases), in 3 steps.
- **Plug:**
  - hero: `plug_crown` → `plug_shade` by height, with broad noise patches;
  - part: body, crown on top, half-way at the ground contact.
- **Hard edges** only where materials meet: bud and stem, stem and plug, leaf and plug.

**Tint**
- Per piece: ±4 % for leaves, ±2 % for buds.
- Broad mottling: amp 0.035 at scale 0.5 for leaves, 0.03 for stems, 0.02 for buds, 0.05 at scale 0.3 for the plug.
  Visible, not confetti.

**Left over**
- The bud's rear and r34 medians (`#D1BB90`, `#C9B491`) stay darker than the sheet's (`#F1D4A5`, `#F4DAAA`), and its
  bottom third (`#A08D6A`) darker than `#E7D49B`. The studio's key light is one-sided; the sheet's buds are lit evenly
  from every side.
- Brightening `bud_base` to `#F2DEAE` moved the bottom third by only 4 levels, so that change was reverted.

## Stage 5 (lighting): skipped

The sheet shows no glow, light or emissive surface (§7.1, decision 7), so there is no Neon and no PointLight.

Studio note (Requires Manual Validation):
- check that the cream buds don't clip to white under the game's sun;
- check that the leaf base → tip gradient survives the palette export.

## Stage 6 (VFX): skipped

The sheet shows no effect (§7.2, decision 7), so there are no sockets. The export STATS line should report none.

## Stage 7 — Verification (round 1)

Fresh verifier, read-only. Background session on port 9880 with `wip/M018_verify.blend` (not saved, `build()` not
called). Fresh renders went to the verifier's scratchpad (`M.MODEL_RENDERS` redirected) through `m018.render_views`,
so the long-lens `*_sheet` cameras are the ones used. Every number below was re-measured: own bmesh and BVH checks,
plus `M.audit`, `K.check` and `m018.measure()`.

**Verdict: FAIL, 5/10.** The technical side is clean. The rosette's leaf shape and arch, and the bud colour, are
clearly unlike the sheet.

### Technical (all re-measured)

| Check | HerbShrubNode | Bud | Stem | Leaf | RootPlug |
| --- | --- | --- | --- | --- | --- |
| Tris (budget) | 826 (4000) | 30 (1000) | 32 | 32 | 80 |
| Size (studs) | 2.938 × 2.693 × 2.200 (target 2.85 × 2.65 × 2.2: inside) | 0.507 × 0.522 × 0.680 (H : W 1.32) | 0.147 × 0.159 × 0.75 | 1.552 × 0.757 × 0.33 (W : L 0.49) | 0.838 × 0.855 × 0.77 (W : H 1.10) |
| Shells, non-manifold, boundary, wire, loose, zero-area, duplicates, n-gons | 1, 0, 0, 0, 0, 0, 0, 0 | same | same | same | same |
| Winding / volume | consistent, +0.848 (outward) | outward | outward | outward | outward |
| Self-intersections (BVH, triangulated) | 0 | 0 | 0 | 0 | 0 |
| Interior faces (ray parity) | 0 | 0 | 0 | 0 | 0 |
| Corners under 5° | 2 (3.94°, 4.14°) | 0 (min 43°) | 0 (min 10.7°) | 0 (min 27°) | 0 (min 54°) |
| UV (`UVMap`): overlaps at 1024² / flips / bounds | 0 / 0 / 0.008–0.992 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Origin at bottom centre, transforms, modifiers | offset (0, 0, 0), rot 0, scale 1, none | same | same | same | same |

- Shading: flat, no custom normals.
- Materials: 19 slots on the hero, all of them used. No emission. Roughness and specular as in the spec (leaves and
  stem 0.85 and 0.8 with foliage specular 0.06, buds 0.7 with 0.3, plug 0.95).
- `Tint` corner attribute present. `K.check`: no problems. No VFX sockets and no children (decision 7: correct).
- **The two slivers are acceptable.** They are at local (−0.06, 0.01, 0.32) and (−0.11, −0.01, 0.24), area 0.001
  sq stud, at r ≤ 0.11 inside the leaf-root cluster under the leaf bases and stems. No camera can see them.
- Facing check (per-face paint luminance against the face normal):
  - leaf nz +0.11, stem 0.00: fine;
  - plug −0.74: the position-based crown/shade field on a ball's top; accepted;
  - **bud −0.63**: `bud_base` `#E1CD9B` is painted brighter than `bud` `#C0AE90` and `bud_tip` `#C7B49E`, so the
    downward faces are the brightest paint. This inverts the sheet's ladder (top palest, base warmer) to offset studio
    shade (see B3).

### Silhouette and detail (long-lens extras against the sheet cells; the side against `side_left_sheet`, the r34 flipped)

| View | W : H sheet → ours | L / U / T sheet → ours (%) |
| --- | --- | --- |
| Front | 1.32 → 1.21 | 87 / 12 / 1 → 89 / 7.5 / 3.4 |
| Side (270) | 1.20 → 1.13 | 84 / 14 / 2 → 85 / 7.3 / 7.7 |
| Rear | 1.28 → 1.09 | 88 / 9 / 3 → 92 / 7.5 / 0.7 |
| f34 | 1.57 → 1.19 | 88 / 10 / 1.5 → 90 / 8 / 2.4 |
| r34 | 1.42 → 1.22 | 83 / 14 / 2.6 → 88 / 9 / 2.8 |
| Top | 1.08 → 1.11 | 93 / 7 / 0 → 93 / 6.4 / 0.4 |

- **Matches:** two buds on two six-sided green stems; the main bud is the apex on the axis and the short bud is
  front-right (separated in the front and f34, behind the main bud from the rear); buds are five-ring ovoids with a
  five-facet apex and no collar; the plug is a dark band at the ground; the parts match their cells.
- **Top profile, outside ±0.06:**
  - side back end (f 0.05–0.15): ours .17 / .24 / .46, sheet .35 / .39 / .43;
  - side front end (f 0.85–1.0): ours .30 / .24 / .16 / .08, sheet .46 / .44 / .40 / .33;
  - rear, f34 and r34 far-left column: ours .52 in all three, sheet .22 / .19 / .29;
  - f34 right end (f 0.85–0.95): ours .42 / .36 / .29, sheet .66 / .63 / .58.
- **Width per height, rear at h 0.1 and 0.2:** ours .32 and .39, sheet .87 and .97. Ours has open air under the side
  leaves; the sheet's leaves sweep down to the ground on both sides.

### Colour (sheet → ours, medians, same masks and boxes; Δ = ours − sheet in R, G, B)

| Region | Front | Side | Rear | f34 | r34 |
| --- | --- | --- | --- | --- | --- |
| Green median | #6A9643 → #68923E (−2,−4,−5) | #618C46 → #6F9945 (+14,+13,−1) | #699343 → #5A7F3A (−15,−20,−9) | #6D9844 → #689444 (−5,−4,0) | #5F8A3F → #5E853B (−1,−5,−4) |
| Green lit quartile | #A3C550 → #96C252 | #A8C458 → #9FC953 | #9CC04E → #7DA445 (−31,−28,−9) | #A0C350 → #9FC952 | #9EC24C → #7DA444 (−33,−30,−8) |
| Green shade quartile | #3C632D → #375524 | #375C25 → #2F471D | #3B6129 → #2E4A20 | #3E6530 → #3B5B26 | #345725 → #2E4C22 |
| Main bud median | #F3D5A0 → #E1CAA1 | #F5D8AA → #BBA37E (−58,−53,−44) | #F2D4A4 → #C5B08E (−45,−36,−22) | #F0D3A1 → #ECCFA1 | #F3D5A8 → #C4B08D (−47,−37,−27) |
| Bud shade quartile | #CEB476 → #8B7A5A (−67,−58,−28) | #CDB37D → #9E8B62 | #CAB07D → #8F7F5F | #C8B077 → #8F7F61 | #D0B682 → #C2AD7F |
| Bud thirds top / mid / base | #FDECC6 / #F5D8A6 / #D3B97D → #F4DAB8 / #A79473 / #8C7C56 | #FCE6C1 / #F7DAAF / #D1B986 → #F6DCB9 / #BAA37E / #A18E63 | — | #FDECC8 / #F2D5A8 / #CBB37A → #FFE1BB / #ECCFA2 / #A18D69 | — |
| Main stem | #669142 → #547B22 (−18,−22,−32) | | | | |
| Plug, low band | #352A1C → (hidden) | #3A2F1F → #201B15 (−26,−20,−10) | | #352A1C → #29251E | #3C2F1F → #362D25 (−6,−2,+6) |

- **Top view, base → tip radius bands** (0–0.2 … 0.8–1.0 of the max radius):
  - sheet `#2A481B #456F33 #5D8A3C #7CA443 #8CB548`;
  - ours `#426432 #4C6F35 #6A9240 #7EA547 #9FC952`;
  - Δ centre (+24,+28,+23), tips (+19,+20,+10);
  - the order is right (centre darkest, tips lightest).
- **Parts** (parts-column cells → `part_*` renders):
  - bud `#F7DCAE` → `#EACDA0` (−13,−15,−14);
  - stem `#669044` → `#5C8727` (−10,−9,−29);
  - leaf `#6C9A4B` → `#74A34B` (+8,+9,0);
  - plug `#967A63` → `#80644D` (−22,−22,−22).
- **Leaves:** blended base → tip with broad mottling. Neighbours blend the way the sheet's do, with no confetti.

### Findings

**B1, blocker: the leaves read as tents and umbrellas, and the top is a cabbage, not a star.**
- Cause: the hero's outer leaves are W 1.00–1.08, about 0.65–0.70 L, against the study's 0.42–0.5 and the exported
  `HerbShrubLeaf` part's 0.72 / 0.49. `FOLD` 0.42 then drops each flank 0.2 or more.
- Effects in every view:
  - Any leaf pointing at a camera becomes a parasol with a dark hollow under it.
  - `side_left_sheet`: two umbrella leaves (L4, L5) fill the view and hide the short stem and most of the main stem.
    The sheet's side shows both stems and a fan of leaves seen side-on.
  - Front: L5/L6 are rounded pentagon lumps with flat bottoms, not the sheet's front diamond leaf (pointed tip on the
    ground, widest at mid-height, about h 0.30).
  - Rear: L2 is a tent in the centre, where the sheet has the V of two leaves.
  - Top: the leaves overlap into a rounded mass. The seven points and the notches at r 0.82–0.95 can't be read.
- Fix:
  - outer leaves W 0.72–0.80 (W : L 0.45–0.5, the same as the exported part); inner leaves about 0.5;
  - `FOLD` 0.15–0.20;
  - keep the ridge camber at 0.08–0.10 L, so each leaf is a low pyramid-topped board, not a tent.
- Accept when:
  - `top_sheet` shows seven separate pointed tips with notches;
  - `side_left_sheet` shows both stems from h 0.3 up;
  - the front leaf is a diamond with its tip on the ground;
  - side top profile within ±0.06 of the sheet (f 0.05–0.15: .35 / .39 / .43; f 0.85–0.95: .46 / .44 / .40).

**B2, blocker: the side leaves float as wings instead of sweeping to the ground.**
- L1 (tip z 1.05) and L3 (tip z 1.00) end in the air at h ≈ 0.47, with slope −20°. Under them, and under L4/L7 in the
  rear and three-quarters, there is open space.
- The sheet's leaves rise to the shoulder (h 0.62–0.68), then droop, and their extreme tips land at h 0.1–0.3. Rear
  width at h 0.1/0.2 is .87/.97 on the sheet against our .32/.39; the far-left top in rear, f34 and r34 is
  .22/.19/.29 against our .52.
- Fix: keep the humps (peak z 1.30–1.45 for L1 and L3), but drop their tips to z 0.35–0.5 with slope −45 to −55°.
  Give L4/L7 tips z 0.10–0.25 at r 1.45–1.55. Each outer leaf should be a broad arch, high at the shoulder and low at
  the tip.
- Accept when: rear width per height at h 0.1–0.3 is ≥ 0.8; the far-left top in rear, f34 and r34 is ≤ 0.32; the
  f34 right end (f 0.85–0.95) is within ±0.08 of .66 / .63 / .58.

**B3, blocker: the buds render grey-tan, not cream, and their ladder is inverted.**
- Paint: `bud` `#C0AE90` (sat 0.25, v 0.75) and `bud_tip` `#C7B49E`, against the swatch `#F9DFAD` and the sheet's
  medians `#F0D6A4`–`#F6DAAC`. `bud_base` `#E1CD9B` is the brightest key.
- Rendered:
  - shade quartile `#8B7A5A`–`#9E8B62`, against the sheet's `#CAB07D`–`#CEB476` (−50 to −67);
  - rear and r34 medians −45/−36/−22 and −47/−37/−27;
  - front bud middle and base thirds `#A79473` / `#8C7C56`, against `#F5D8A6` / `#D3B97D`.
- The sheet's buds are pale cream from every side with soft shading. Ours show dark taupe facets.
- Fix:
  - lift the bud keys toward the swatch and keep hue 38–42°: `bud` about `#EBD3A2`, `bud_tip` about `#F6E7C6`
    (palest), `bud_base` about `#DDBE85` (warmer, more saturated, not brighter than the body);
  - control clipping with the finish, not the paint: specular 0.1, roughness 0.85;
  - re-measure the main bud: rows from the apex down 0.30 H, columns ±0.09 W round it, every non-green pixel.
- Accept when: shade quartile ≥ `#B8A070`; lit quartile not pure `#FFFFFF`; median within 15 of the sheet in front,
  side and rear; thirds in order (top palest, base warmest).

**Minor (fix if convenient, otherwise note):**
1. **Short stem too upright in projection:** 23° lean on a 1.25 stem from z 0.06. It projects to about 15° in the
   front (sheet 25–30°) and 18° in the side (sheet 35–39°). Try a lean of 32–35° on a shorter stem (about 1.0, base
   raised to z 0.3), with the short bud kept at about (0.42, −0.45, 1.40).
2. **Inner leaves I1/I2 read as dark, narrow, upright spikes** in the front and rear, because the heart field pulls
   them to `leaf_base`. On the sheet, the inner leaf behind the short bud is a mid-green broad leaf. Let them keep the
   `leaf` key above z 0.8.
3. **Stem colour:** the main stem in the front is `#547B22`, against `#669142` (−18,−22,−32); the part stem is
   `#5C8727`, against `#669044` (blue −29). It is slightly too saturated: about `#5B8433` → render `#66903C`.
4. **Plug:** the part renders `#80644D` against `#967A63` (−22 each), outside the spec's ±12. The hero plug in the
   side is `#201B15` against `#3A2F1F`. Lift `plug` by about 20 levels.
5. **Top radius bands:** the heart is too light (+24..28) and the tips too light (+19/20). That partly follows from
   B1 (wide leaves cover the dark heart).
6. **Green medians** are within 5 levels in front, f34 and r34; the side is +14, and the rear −15/−20 (lit quartile
   −31). These should settle with B1/B2.
7. **U share** is 6.4–8.8 % against 7–14 %, because bud shade falls into T. It follows B3.
8. **f34/r34 W : H** 1.19/1.22 against 1.57/1.42: accepted per §3.9.
9. **`studs` metadata:** the custom property on `HerbShrubNode` reads "2.9 x 2.7 x 2.5"; the measured size is
   2.94 × 2.69 × 2.20. It is stale; refresh it after the floor cut.
10. **Two corners under 5°** (3.94°, 4.14°): hidden in the root cluster, accepted.

**Studio (Requires Manual Validation):** the bud brightness under the game's sun after B3, and whether the leaf
base → tip ladder survives the palette export.

## Round 2 fixes (modeller)

Fresh modeller, background session on port 9878 with `wip/M018.blend` (saved after the final build). Every change is
in the builder `art/blender/kit/mcp/m018.py`; `build()` reproduces it. Measurements: `m018.measure()` (study masks,
long-lens `*_sheet` renders, side against `side_left_sheet`, r34 flipped) plus a scratch colour script using the
verifier's main-bud box (apex rows down 0.30 H, columns ±0.09 W, every non-green pixel).

### Final technical state (all re-measured after the last `build()`)

| Check | HerbShrubNode | Bud | Stem | Leaf | RootPlug |
| --- | --- | --- | --- | --- | --- |
| Tris (budget) | 618 (4000) | 30 | 32 | 32 | 80 |
| Size | 2.94 × 2.69 × 2.20 (inside ±0.15 / ±0.15 / ±0.1) | 0.51 × 0.52 × 0.68 | 0.15 × 0.16 × 0.75 | 1.55 × 0.76 × 0.28 | 0.84 × 0.86 × 0.77 |
| Shells / non-manifold / boundary / n-gons / dup verts | 1 / 0 / 0 / 0 / 0 | same | same | same | same |
| Self-intersections (BVH) | 0 | 0 | 0 | 0 | 0 |
| Inverted faces (ray parity) | 0 | 0 | 0 | 0 | 0 |
| Min corner | 5.06° (no slivers left) | 43° | 10.7° | 31° | 54° |

- Union: 15 shells in, none retried, none failed or dropped; the hero comes out as 1 shell.
- UV: bounds 0.008–0.992, 0 overlapping texels at 1024², margin 0.008 (unchanged `UV` settings).
- `K.check`: no problems. Origin at bottom centre, rotation 0, scale 1, no modifiers, 19 material slots, no emission, no
  VFX sockets (decision 7).
- `studs` is now refreshed from the final mesh at the end of `build()` (minor 9): "2.9 x 2.7 x 2.2"; `tris` 618.

### Leaf recipe: the edge never dips below the keel (coordinator note from M019)

- `KEEL` is now 0.045 / 0.05 / 0.035 L (the study's 0.04–0.05 L keel; round 1 had 0.025–0.03), and `KEEL_GUARD = 0.7`
  caps each edge's droop (measured along the leaf normal) at 0.7 × the keel line's depth at that t. The keel line runs
  from 0 at the base through the keel points to 0 at the tip.
- `leaf_mesh` reports per leaf: edge verts below the keel line, top or underside faces facing the wrong way, and
  ray-parity inverted faces. All 9 hero leaves and the part: **0 / 0 / 0** (`build()` returns them as `leaf_inverted`).
  The round-1 recipe (FOLD 0.42, shallow keel) had **all 10 edge verts below the keel line** on every leaf tested (L1,
  L4, L6); FOLD 0.18 without the guard still had 4–5.
- `_union` now calls `view_layer.update()` before `split_loose` and after each retry nudge (the stale `matrix_world`
  pitfall from M019).

### B1, leaf shape: partly fixed

- `FOLD` 0.42 → **0.18**; ridge camber 0.08 / **0.09** / 0.06 L (0.08–0.10 asked).
- Outline: the outer half now tapers to a point (half-widths 0.30, 0.45, 0.50, 0.42, 0.24 W at t 0.12 … 0.88). Round
  1's 0.47 / 0.36 at t 0.70 / 0.89 made blunt spoon ends that merged into the cabbage.
- Widths: outer **0.80–0.88** (round 1 1.0–1.08), inner I1 0.52, I2 0.50. The verifier asked for 0.72–0.80 at "W : L
  0.45–0.5". The arched back and side leaves are 1.8–2.2 long along the midline (they rise to the shoulder and come
  back down), so 0.80 gave W : L 0.36 and read as spikes; 0.84–0.88 keeps W : L at 0.39–0.46. No tents: the
  cross-section is a low pyramid-topped board.
- `top_sheet`: seven separate pointed tips with notches between them (study 35/85/145/190/240/285/345 → ours
  28/88/148/200/248/285/340, all within 10°). The heart is still a busy cluster round the buds.
- Front: L6 is the sheet's diamond, tip on the ground, widest at mid-height.
- `side_left_sheet`: the main stem shows from about h 0.45, the short stem from about h 0.4 (I1 moved from 325° to 335°
  so it no longer stands in front of the short stem). Not yet "from h 0.3": L3's base and L4's hump still cover the
  lowest part.
- Side top profile ends: f 0.05–0.15 ours .35 / .42 / .47 (sheet .35 / .39 / .43, within ±0.06); f 0.85–0.95 ours
  .43 / .38 / .34 (sheet .44 / .40 / .33 at f .90–1.0, and .47 / .46 at f .80–.85). **Pass.**

### B2, side leaves as wings: partly fixed

- L1 / L3: humps kept (midline peak 1.22 / 1.24; the silhouette top with the ridge is about 1.4). Tips dropped from
  z 1.05 / 1.00 at −20° to **z 0.62 / 0.58 at −38°**. That is not the asked 0.35–0.5 at −45…−55°: see "Profile
  trade-off" below.
- L4 / L7 tips at **z 0.03**, r 1.52 (asked 0.10–0.25; lower, so they land on the ground and fill the rear's bottom rows).
- L2 back leaf raised (peak 0.58 → 0.92, tip z 0.04 → 0.42): the side's back end now matches (above).
- Acceptance numbers (sheet → ours):
  - rear width per height at h 0.1 / 0.2 / 0.3: .87 / .97 / .89 → **.29 / .92 / .94**. h 0.1 fails: the lowest
    silhouette row is the plug's near edge, which the 8° camera puts below the leaf tips;
  - far-left top column: rear .22 → **.14** (pass), f34 .19 → **.35**, r34 .29 → **.34** (both fail by 0.03–0.05, from
    L3's tip);
  - f34 right end at f .85 / .90 / .95: .66 / .63 / .58 → **.43 / .35 / .26** (fail).

**Profile trade-off (why B2 is only partly applied).** The sheet's cells disagree with each other at the leaf ends.
- The front wants the right shoulder high out to x ≈ 1.25 (f .85–.95: .62 / .59 / .54), and so does the f34 right end.
- The rear wants the same +X edge low (f .05: .32), and the f34 / r34 far-left column wants L3's tip low.
- A top profile seen from the front and from the rear of one rigid object can differ only by the camera-elevation
  shift (about 0.05 h here).

I tried the literal B2 numbers: L1 / L3 tips at z 0.45 and −50…−60°, humps pushed out to r 1.0 with long Bézier
handles, L4 / L7 hooking to the ground. Some profile columns improved by 0.05–0.15, but every outer leaf became a hooked
"spider leg" (steep rise, knee, steep drop). That looks less like the sheet's broad, gently drooping leaves than round 1
did. The final values are the gentlest arches that still drop the tips well below the shoulders and put L4 / L7 on the
ground.

Other profile numbers outside ±0.06 (dTop = ours − sheet):
- front f .05–.15: −.14 / −.17 / −.14; f .85–.95: −.11 / −.18 / −.30;
- rear f .10–.20: −.20 / −.13 / −.08; f .90–1.0: −.15 / −.19 / −.35;
- r34 f .85–1.0: −.30 / −.37 / −.39.

The centre columns (buds, stems) are within ±0.03 everywhere. W : H: front 1.32 → 1.20, side 1.20 → 1.06, rear
1.28 → 1.17.

### B3, bud colour: partly fixed

- The ladder now runs top palest → base warmest, by height in the bud (position only):
  - `bud_tip` #E6D3B4 (saturation 0.22, the palest);
  - `bud` #EED3A0;
  - `bud_base` #EED29A (warmer and more saturated, luminance just under the body).
- Finish: specular 0.1 and roughness 0.85 on all bud keys (was 0.3 / 0.7).
- Pass 1 (`K.calibrate` on the dome, kind "all"): the cream clips on the dome's lit side, and the solver again returned
  grey-pink hexes (#C8B192 / #E2BEAA / #B8A47C), the round-1 trap. Not used.
- Pass 2, on the hero renders: the verifier's suggested #EBD3A2 / #F6E7C6 / #DDBE85 clipped the lit facets to #FFFFCD.
  So the tip was lowered, and the base brought up to the body's value.
- Main bud (sheet → ours: median, then lit quartile / shade quartile):
  - rear #F5DBA8 → **#F7D89D** (#FFE8C1 / #A68F64); r34 #F3D5A9 → **#F7D89E** (#FFE8BE / #D2B780): within 10;
  - front #F4D7A3 → #B3986A (#FFFFD4 / #957F56); f34 #F0D3A1 → #C4A773 (#FFFFD5 / #957F55);
  - side_left #F9E0B0 → #FFFDBE (the lit side, clipped).
  - Thirds are in order (top palest, base warmest) in front, rear, f34 and r34: front #FFFEC5 / #B2986A / #957E54,
    rear #FFE7B8 / #F6D79D / #99855B.
- What is left: the kit studio has a strong world-fixed key light, from −X and above.
  - The same paint reads right from the rear and r34, clips from the side, and the front / f34 see the shaded lower band
    (−40…−65).
  - No position-based paint satisfies all views. Making the base brighter than the body (round 1's fix) is what the
    verifier rejected.
  - The shade quartile ≥ #B8A070 passes in r34 and side only. The lit quartile is never pure #FFFFFF.
  - The part bud renders #FFFAB1 (sheet #F7DCAE).
  - The bud under the game's sun still needs a Studio check (Requires Manual Validation).

### Minors

1. **Short stem lean: fixed.**
   - It now starts behind the axis low in the heart (0, 0.10, 0.20), crosses the main stem inside the leaf roots and
     leans 43° toward az −51; length 1.25.
   - It projects **30.4° in the front and 35.9° in the side** (sheet 25–30 / 35–39).
   - Short bud bottom (0.49, −0.51, 1.04), top (0.58, −0.61, 1.54).
2. **Inner leaves: fixed.** The heart field fades out on I1 / I2 between z 0.7 and 1.3, so their upper halves keep the
   `leaf` key; they read mid-green in the front and rear.
3. **Stem: fixed.** `stem` #537829 → **#57793B** (dome calibration renders 102, 142, 61 against #66903C).
   - The part stem renders #62893A (sheet #669044: Δ −4 / −7 / −10; the blue is no longer −29).
   - The f34 hero main stem renders #679345.
4. **Plug part: fixed.**
   - `plug` #6A5644 → **#806A58**, `plug_crown` → #715B47: the part renders **#9A7B61** (sheet #957962, +5).
   - Hero `plug_shade` #2F2519 → #3A2D1F: the hero plug renders #3C3128 / #3B3026 in the rear / r34 (sheet #3B2F20 /
     #3C2F1F).
5. **Top-view gradient: improved.** The outer leaves also get a Tint field by distance from the axis (0.72 at the axis,
   1.0 at r 0.7; position only).

   | Band (r 0–0.2 … 0.8–1.0 of max) | 1 | 2 | 3 | 4 | 5 |
   | --- | --- | --- | --- | --- | --- |
   | Sheet | #2A481A | #456F33 | #5D8A3C | #7CA443 | #8CB548 |
   | Round 1 | #426432 | #4C6F35 | #6A9240 | #7EA547 | #9FC952 |
   | Round 2 | **#476932** | **#517836** | **#59813B** | **#739943** | **#8CB04D** |

   - The tips now match (0, −4, +5).
   - The heart is still +29: the buds and inner leaves sit there, and the sheet's heart is in occlusion shadow that the
     studio doesn't render.
6. Green medians (sheet → ours): front #6A9643 → #60873C, side #618C46 → #719D45, rear #699343 → #5D843D, f34
   #6D9844 → #679241, r34 #5F8A3F → #60893C. The leaf keys are unchanged from round 1 (#5A8044 / #7A9C48 / #3A5A2E).
7. L / U / T shares (sheet → ours): front 87/12/1 → 83/10/8, side 84/14/2 → 79/12/8, rear 88/9/3 → 80/11/9, top 93/7/0
   → 91/9/0.
   - T is inflated by the shaded bud band (hue ~40°, v < 0.74 falls in the plug mask) and by the visible plug band.
   - The plug is Ø 0.9 as decided, and it shows as a dark disc at the ground in the side and rear.
8. f34 / r34 W : H: accepted per §3.9, unchanged.
9. **`studs`: fixed** (above).
10. **Slivers: none left** (min corner 5.06°).

### Cleanup changes (needed by the new leaves)

- `_clean_mesh`'s sliver pass and `_force_slivers` now run through `_guarded`. When a step raises the crossing count,
  the sliver pass retries with half and then a quarter of `CLEAN_MOVE` (the final build used 0.03).
- `_guarded` also undoes a step that raises the shell count (a needle collapse had split L3's blade off the hero).
- `_collapse_needles` (guarded) collapses the short edge (< 0.05) of any needle under 5°.
- `_tri_quads` is m018's own copy of m012's. It skips a quad that an earlier edge rotation already turned into a
  triangle (m012's version crashed on it).
- I2 moved from 150° to 125°. At 150° it shared L3's vertical plane, and the union left L3 hanging on a 0.005-stud pinch.

### Final palette (`PALETTE`)

| Key | Hex | Finish |
| --- | --- | --- |
| `m018_leaf` | `#5A8044` | rough 0.85, foliage specular |
| `m018_leaf_tip` | `#7A9C48` | rough 0.85, foliage specular |
| `m018_leaf_base` | `#3A5A2E` | rough 0.85, foliage specular |
| `m018_stem` | `#57793B` | rough 0.8, foliage specular |
| `m018_bud` | `#EED3A0` | rough 0.85, specular 0.1 |
| `m018_bud_tip` | `#E6D3B4` | rough 0.85, specular 0.1 |
| `m018_bud_base` | `#EED29A` | rough 0.85, specular 0.1 |
| `m018_plug` | `#806A58` | rough 0.95 |
| `m018_plug_crown` | `#715B47` | rough 0.95 |
| `m018_plug_shade` | `#3A2D1F` | rough 0.95 |

### Honest assessment

Technically, it is clean and sturdier than round 1: no slivers, guarded cleanup, and a leaf recipe that can't turn
inside-out. The leaves are no longer tents or umbrellas, the top is a seven-point star, and the front diamond is right.
The buds are cream with the right ladder, and the stems, plug and inner leaves are fixed.

Still unlike the sheet:
- the leaves are long and narrower than the sheet's fat leaves, so the rosette reads more open and spiky (the sheet's is
  denser);
- the plug shows as a dark disc in the side and rear;
- the side view hides the lowest part of the stems;
- the f34 right end, the rear h 0.1 width and the f34 / r34 far-left column miss the B2 numbers;
- the bud brightness depends on the studio key light's direction.

I would expect round 2 to score about 6–7/10.

## Stage 7 — Verification (round 2)

Fresh verifier (did no other stage, not the round-1 verifier), read-only. Background session on port 9880 with
`wip/M018_verify.blend` (the kit copy after the main session's rebuild); not saved, `build()` not called. Fresh renders
through `m018.render_views` (long-lens `*_sheet` cameras) with `M.MODEL_RENDERS` redirected to the verifier's
scratchpad (`…/scratchpad/v18r2/renders/M018/`, with `cmp_0..5.png`: sheet cell | our render for front, side_left,
rear, top, f34, r34 flipped). Every number below was re-measured: `M.audit`, own BVH self-intersection and ray-parity
checks, own UV rasteriser at 1024², `K.check`, `m018.measure()` and an own colour script (same masks on both images).

**Verdict: FAIL, 6/10.** The technical side is clean and most round-1 minors are fixed. The buds, stems, diamond front
leaf and seven-point star read correctly. But the rosette still looks clearly unlike the sheet's: the leaves are narrow,
peaked and spiky, and the plug shows as a dark pedestal.

### Technical (all re-measured)

| Check | HerbShrubNode | Bud | Stem | Leaf | RootPlug |
| --- | --- | --- | --- | --- | --- |
| Tris (budget) | 618 (4000) | 30 (1000) | 32 | 32 | 80 |
| Size (studs) | 2.943 × 2.693 × 2.200 (target 2.85 × 2.65 × 2.2 ±0.15/±0.15/±0.1: inside) | 0.507 × 0.522 × 0.680 | 0.147 × 0.159 × 0.750 | 1.552 × 0.757 × 0.278 | 0.838 × 0.855 × 0.770 |
| Shells / non-manifold / boundary / wire / loose / zero-area / dup verts / n-gons | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 | same | same | same | same |
| Normals (signed volume) / odd-parity (inverted or interior) faces | outward / 0 | outward / 0 | outward / 0 | outward / 0 | outward / 0 |
| Self-intersections (BVH, triangulated) | 0 | 0 | 0 | 0 | 0 |
| Min corner angle | 5.06° (no slivers) | 43.0° | 10.7° | 31.4° | 53.8° |
| UV: overlapping texels at 1024² / flipped / bounds / density spread p5–p95 | 0 / 0 / 0.008–0.992 / ±0.1 % | same | same | same | same (±2.5 %) |
| Origin / rotation / scale / modifiers | bottom centre (offset 0,0,0) / 0 / 1 / none | same | same | same | same |

- Flat shading (0 smooth faces), no custom normals. `Tint` corner attribute present (0.78–1.05).
- `K.check`: no problems. `studs` "2.9 x 2.7 x 2.2" and `tris` 618 now match the mesh (round-1 minor 9: fixed).
- Materials: 19 slots on the hero, all used, no emission, metal 0. Leaves and stem rough 0.85/0.8 with foliage
  specular 0.06; buds rough 0.85 spec 0.1; plug rough 0.95. No VFX sockets and no children (decision 7: correct).
- **Facing check** (paint luminance against the face normal): leaf nz +0.10, stem −0.07: no colouring by facing.
  The bud's +0.63 is only its height ladder: its three keys differ by less than 2 luminance levels (#E6D3B4 / #EED3A0 /
  #EED29A), so the round-1 inversion is gone. The plug's −0.76 is the accepted crown→shade height field.

### Round-1 items

| Item | Status |
| --- | --- |
| B1 tents/umbrellas, cabbage top | **Partly fixed.** No tents (FOLD 0.18), seven tips in the top, the front diamond leaf is right. But the leaves are now narrow peaked blades (see N1). |
| B2 side leaves as wings | **Partly fixed, overshot.** L1/L3 tips dropped to z 0.6. The leaf ends are now too low in most views (dTop at the outer columns: front f .85–.95 −.11/−.18/−.30; f34 −.23/−.28/−.32; r34 f .85–1.0 −.21/−.30/−.37/−.39; rear f .90–1.0 −.15/−.19/−.35). Rear width at h 0.1 is .29 (sheet .87). |
| B3 bud colour | **Mostly fixed.** Cream with the ladder in order. The lit side still clips toward lemon (see minor 1). |
| m1 short-stem lean | Fixed (30° front, 36° side). |
| m2 inner leaves dark spikes | Fixed for colour; still narrow upright spikes (W : L 0.32–0.34). |
| m3 stem colour | Fixed: part #62893A against sheet #689245 (−6, −9, −11). |
| m4 plug colour | Fixed: part #9B7D64 against #997E69 (+2, −1, −5); hero rear #3A3027 against #3B2F20. |
| m5 top bands | Improved (tips match; heart still light). |
| m9 `studs` / m10 slivers | Fixed. |

### Shape against the sheet (long-lens extras; side = `side_left_sheet`, r34 flipped)

| View | W : H sheet → ours | L / U / T % sheet → ours | Plug pixels / green pixels, sheet → ours |
| --- | --- | --- | --- |
| Front | 1.32 → 1.20 | 87 / 12 / 1 → 83 / 10 / 8 | 1.4 % → 3.7 % |
| Side (270) | 1.20 → 1.06 | 84 / 14 / 2 → 79 / 12 / 8 | 2.6 % → 5.6 % |
| Rear | 1.28 → 1.17 | 88 / 9 / 3 → 80 / 11 / 9 | 3.2 % → 9.5 % |
| f34 | 1.57 → 1.17 | 88 / 10 / 2 → 80 / 11 / 9 | 1.7 % → 8.3 % |
| r34 | 1.42 → 1.22 | 83 / 14 / 3 → 76 / 15 / 9 | 3.4 % → 10.6 % |
| Top | 1.08 → 1.12 | 93 / 7 / 0 → 91 / 9 / 0 | — |

- **Right:** two buds on two six-sided green stems, graded by height (main top z 2.20 on the axis, short bud top 1.54,
  front-right). Buds are 5-ring ovoids with a five-facet apex and no collar. The front diamond leaf has its tip on the
  ground. The top reads as a seven-point star (tips 28/88/148/200/248/285/340°). The centre columns (buds, stems) are
  within ±0.03 of the sheet in every view. The parts match their cells.
- **Leaf geometry** (midlines computed from `LEAVES`): outer leaves are 1.64–2.23 long with W 0.80–0.88, so W : L is
  0.39–0.49. The outline tapers to 0.24 W at t 0.88. Every outer midline rises steeply from r 0.06 (L1 reaches z 0.94 by
  t 0.25) to a peak at t 0.43–0.63, then drops, so each blade is an inverted "^". The sheet's leaves are broad
  (W : L ≈ 0.5–0.55 as drawn) with fuller tips. They leave the plug low, and their visible blades run out as nearly
  straight, gently inclined boards in two tiers: high back leaves over low leaves lying on the ground.

### Colour (sheet → ours; Δ = ours − sheet in R, G, B)

| Region | Front | Side | Rear | f34 | r34 |
| --- | --- | --- | --- | --- | --- |
| Green median | #6A9643 → #60873C (−10,−15,−7) | #618C46 → #719C45 (+16,+16,−1) | #699343 → #5D853D (−12,−14,−6) | #6D9844 → #679241 (−6,−6,−3) | #5F8A3F → #60893C (+1,−1,−3) |
| Green lit / shade | #A3C550 / #3C632D → #8CB851 / #344C1E | #A8C458 / #375C25 → #95BE50 / #395928 | #9CC04E / #3B6129 → #7DA444 / #2F4920 | #A0C350 / #3E6530 → #96C050 / #385326 | #9EC24C / #345725 → #7DA444 / #2B4720 |
| Main bud median | #F3D5A0 → #FAE7B3 (+7,+18,+19) | #F5D9AD → #F3D8A2 (−2,−1,−11) | #F1D4A4 → #F7D89E (+6,+4,−6) | #F0D3A2 → #FFFDB4 (+15,+42,+18) | #F5DBAC → #F7D89E (+2,−3,−14) |
| Main bud lit / shade | #FEEFCA / #CAB174 → #FFFFD4 / #A68E62 | #FEEFCB / #CCB27D → #FFFFD9 / #AC9264 | #FDECC6 / #C7AF7C → #FFECC2 / #AB976A | #FEEEC9 / #C8B077 → #FFFFD5 / #AC9264 | #FEF0CB / #D0B681 → #FFEBC2 / #D0B680 |
| Main bud thirds top / mid / base | #FDEBC4 / #F4D7A5 / #D2B87B → #FFFFC2 / #C3A773 / #957F55 | #FCE6C1 / #F6D9AD / #DDC799 → #FFFFCF / #E9C78C / #B6A676 | #FCE4C2 / #F3D6AA / #CFB686 → #FFE8B9 / #F6D79D / #D0B47D | #FDEBC8 / #F2D5A7 / #CBB37A → #FFFFD4 / #FFECB2 / #AC9261 | #FDE5BE / #F8DEAD / #F1D2A1 → #FFE8B9 / #F6D79D / #D7C894 |
| Hero plug | #362E1F → #534333 (+29,+21,+20) | #3A2F1F → #2B2119 (−15,−14,−6) | #3B2F20 → #3A3027 (−1,+1,+7) | #352A1C → #2D261F (−8,−4,+3) | #3C2F1F → #3A2F26 (−2,0,+7) |

- **Parts:** bud #F0D5B0 → #FFF9B1 (+15, +36, +1, lit side clipped lemon); stem #689245 → #62893A; leaf #759F4D →
  #72A14B (−3, +2, −2); plug #997E69 → #9B7D64.
- **Top-view gradient:** in order (centre darkest, tips lightest); the leaves blend base → tip with broad mottling, no
  confetti.

### Findings

**N1, blocker: the rosette reads as narrow, spiky, peaked blades, not the sheet's broad low leaves** (cmp_0, cmp_1,
cmp_2, cmp_4, cmp_5).
- Every outer leaf rises steeply from the centre to a mid-length peak and falls away ("^"). With W : L 0.39–0.49 and a
  0.24 W tip, the front, rear, f34 and r34 show a sparse fan of horn-like blades with dark hollows between them. The
  sheet shows a dense mound of broad, overlapping, gently inclined boards. This is the model's defining feature.
- The profile numbers agree: the outer columns are 0.11–0.39 h too low in front, rear, f34 and r34 (the sheet carries
  its upper leaves out to the edge, then drops only the tip).
- **Cheap fix (parameters only, `LEAVES` / `OUTLINE` / `HANDLES`):**
  - widen the outer leaves to W 0.95–1.05 (W : L ≥ 0.5) and fill the outline's outer half to
    `(0.72, 0.46), (0.88, 0.32)`. Keep `FOLD` 0.18 so they stay boards, not tents;
  - move each outer arch's peak inward (t 0.25–0.35: shorter base handle, about `(0.30, 0.30)`), so the visible blade
    beyond it is a straight board falling 15–30°, not a "^";
  - upper tier L1/L3 (and L2): tips at z 0.85–1.0, r 1.4–1.5. Lower tier L4/L7/L5/L6: keep their tips on the ground,
    broad, under the upper tier.
- **Accept when:** in `cmp_*`, the leaves read as broad overlapping boards; outer-column dTop is within ±0.10 in
  front and f34 (f .85–.95); rear width at h 0.2–0.3 is ≥ 0.85; the top still shows seven tips with notches.

**N2, blocker: the plug shows as a dark pedestal/pot under the rosette** (f34, rear, r34, side).
- Plug pixels are 2.5–5× the sheet's share (rear 9.5 % against 3.2 %, f34 8.3 % against 1.7 %, r34 10.6 % against
  3.4 %). The leaves leave from r 0.06 at 38–55°, so nothing covers the plug's 0.45-radius rim. The sheet's leaf
  bases come down over it and leave only dark wedges between them (pitfall 9).
- **Cheap fix:** the N1 changes (lower, broader leaves) cover most of it. In addition, shrink `PLUG_H` rx 0.45 → 0.36,
  or start the outer leaf roots at r 0.20–0.25 (z 0.10–0.14, still inside the plug) with base pitch 25–35°, so their
  lower edges skirt the plug.
- **Accept when:** plug pixels / green pixels ≤ 4.5 % in rear, f34 and r34.

**Minor (note if not fixed):**
1. **Bud lit side clips to lemon** in front, side, f34 and the part: lit quartile #FFFFD4–#FFFFD9 (hue about 60°,
   against the sheet's #FEEFCA, 40°); f34 median +15/+42/+18. The shade quartile is −28…−36 in front/f34 (#A68E62
   against #CAB174). This depends on the studio's one-sided key light; rear and r34 are within 7. If touched, lower
   all three bud keys about 6 % in value at the same hue. Otherwise leave it for the Studio check.
2. **Short bud sits far out:** top at r ≈ 0.84 (study plan 0.62). In the top view it sits at the rosette edge, where the
   sheet has both buds near the centre (§3.4 accepted the mismatch; the 43° lean pushed it further out).
3. **Green lit quartile low** in rear, r34 and top (−31…−22 in R and G), and the shade is darker in front (−8, −23,
   −15): the open spiky structure shows deep interior. Expect it to settle with N1.
4. **Inner leaves I1/I2** are W : L 0.32–0.34 upright spikes; the sheet's inner leaf behind the short bud is broader.
   Widen to about 0.62 with N1.
5. f34/r34 W : H 1.17/1.22 against 1.57/1.42: accepted per §3.9.

**Studio (Requires Manual Validation):** bud clipping under the game's sun; the leaf base → tip ladder through the
palette export.

## Round 3 fixes (modeller)

Fresh modeller, background session on port 9879 with `wip/M018.blend` (saved after the final build). This was a
targeted round: N1 (the leaf rosette), N2 (plug exposure), and minors 1, 2 and 4. Every change is in
`art/blender/kit/mcp/m018.py`; `build()` reproduces it.

Measured with:
- `m018.measure()`: long-lens `*_sheet` cameras, the side against `side_left_sheet`, the r34 flipped;
- a sheet-against-ours composite of all six cells;
- a top-view polar tip counter;
- the verifier's main-bud box.

### Final technical state (all re-measured after the last `build()`)

| Check | HerbShrubNode | Bud | Stem | Leaf | RootPlug |
| --- | --- | --- | --- | --- | --- |
| Tris (budget) | 840 (4000) | 30 | 32 | 32 | 80 |
| Size | 2.95 × 2.61 × 2.20 (inside 2.85 × 2.65 × 2.2 ± 0.15 / 0.15 / 0.1) | 0.51 × 0.52 × 0.68 | 0.15 × 0.16 × 0.75 | 1.55 × 0.76 × 0.28 | 0.84 × 0.86 × 0.77 |
| Shells / non-manifold / boundary / n-gons / dup verts | 1 / 0 / 0 / 0 / 0 | same | same | same | same |
| Self-intersections (BVH) | 0 | 0 | 0 | 0 | 0 |
| Inverted faces (ray parity) | 0 | 0 | 0 | 0 | 0 |
| Min corner | 5.13° | 43° | 10.7° | 31° | 54° |
| UV overlap texels at 1024² / flipped / bounds | 0 / 0 / 0.008–0.992 | same | same | same | same |

- Union: 15 shells in, none retried, none failed; the hero comes out as 1 shell.
- `K.check`: no problems. Origin at bottom centre, no modifiers, no emission, no VFX sockets (decision 7).
- The leaf keel guard is unchanged. Every leaf (9 hero leaves and the part) has, before the union:
  - 0 edge verts below the keel line;
  - 0 flipped top or underside faces;
  - 0 ray-parity inverted faces;
  - 0 self-crossings.
- The `view_layer.update()` calls and the `_guarded` cleanup steps are untouched.
- `studs` is "3.0 x 2.6 x 2.2" (rounded); KITSTAT reports "ok" for all five objects.

### N1, leaf shape: rebuilt

**Why the literal brief didn't work.** A single cubic from the crown (z 0.12) can't peak at t 0.25–0.35 and also end
at a tip at z 0.85–1.0: a scratch search over handles found no set that does both. The first try used a steep first
segment up to z 1.2, and that rise showed as a wide vertical green wall round the stems.

**The new midline.** Each outer leaf's midline is now two cubics:
- **`Path2` / `arch_path`** (new):
  - a short straight **stalk** from the crown rim (r 0.21, z 0.10–0.12) up to a joint at r 0.27–0.31;
  - then the **board**, which leaves along the stalk and turns over to the tip.
- Leaf t is now the **arc-length** fraction (the old Bezier t bunched the outline near the ends), so outline positions
  mean what they say.

**`arch_layout` (outline, ridge and keel).**
- The stalk is narrow (half width 0.11 W) and has its own ridge and keel points that follow the bend. Without them the
  ridge chord cut through the keel: 2 crossings per leaf.
- The board carries the outline, ridge and keel. `BOARD_OUTLINE` (u, half width / W) is
  (0, 0.26), (0.24, 0.45), (0.50, 0.50), (0.72, 0.40), (0.88, 0.18).
- I tried the brief's (0.72, 0.46), (0.88, 0.32). In arc-length terms it gave blunt 120° tips, and the top view became
  a cabbage of round discs. (0.40, 0.18) gives the sheet's ~90° tips.
- `OUTLINE` itself (inner leaves and the part) takes the brief's values (0.72, 0.46), (0.88, 0.32).
- `FOLD` stays 0.18.

**Two tiers.**
- Upper tier, L1 / L3 (az 354 / 148): boards carried out at z 1.0–1.07, with only the tip dropping (tip z 1.00 /
  0.98, slope −14°).
- Lower tier, L2 / L4 / L5 / L6 / L7: boards that peak early (z 0.73–0.87 at r ≈ 0.45, joint at t 0.23–0.29), then
  fall as straight boards at 25–35° to tips on or near the ground (L7's tip is at z 0.18).
- L2 is lower tier, not upper as briefed. The side cell's back end is at h 0.18–0.35, and the rear needs L2 to cover
  the plug.

**Widths.**
- Outer W is 0.82–0.96 (L5 0.70). That is W : L 0.45–0.52 over the whole leaf, and the visible board is broad
  (W : L ≈ 0.65).
- W 0.95–1.05 on every leaf turned the shorter lower leaves into round discs.

**Roll** (a new per-leaf option).
- L1 / L7 are rolled +15° and L3 / L4 −15°, so the side leaves turn their faces toward the front, as every sheet cell
  draws them. Edge-on, they read as the round-2 horns.
- L6 has a kite outline (`KITE`) for the front diamond.

**Inner leaves (minor 4).**
- W 0.52 / 0.50 → 0.70 / 0.68 (W : L 0.43–0.47). I read the verifier's "about 0.62" as a width: 0.62 × L would be
  1.0 stud and would hide both stems.
- Rolled 75° / −25° (`INNER_ROLL`) so they face the front, broad.

**Azimuths.** L1 is at 354° and L7 at 28°; they swapped sides of the x axis from round 2's 28° / 340°. Two
constraints drove this:
- the f34's right end must be the *high* leaf (sheet f .95 = .58);
- the top view needs L1 and L7 at least 30° apart.

With L1 at 4° and L7 at 352°, the top view merged them into one tip. With L7 at 322°, the f34 failed again.

**Pass criteria** (sheet → ours; dTop = ours − sheet):

| Criterion | Result |
| --- | --- |
| Front outer columns f .85 / .90 / .95 within ±0.10 | −0.04 / −0.03 / −0.01 **pass** (round 2: −0.11 / −0.18 / −0.30) |
| f34 outer columns f .85 / .90 / .95 within ±0.10 | −0.05 / −0.03 / 0.00 **pass** (round 2: −0.23 / −0.28 / −0.32) |
| Rear width at h 0.2 / 0.3 ≥ 0.85 | 0.97 / 0.86 **pass** (sheet 0.97 / 0.89) |
| Top shows seven tips | **Pass.** Polar tips at 21 / 81 / 159 / 192 / 249 / 273 / 345° (sheet 36 / 84 / 144 / 189 / 240 / 285 / 345), plus one shallow inner bump at 117° (I2, at 0.88 of the maximum radius). |
| Hero reads as a dense, low, overlapping mound | In the front, f34, rear and r34: broad overlapping boards, no hollows, and stems rising out of the leaf mass. See "Honest assessment". |

**Other profile columns:**
- Front f .05–.35: within −0.12…−0.04.
- Front f 1.0: +0.39. Our right extreme is L1's high tip; the sheet's is L7's tip on the ground. That is the price of
  the f34 fix.
- f34 f 0–.10: +0.32 / +0.19 (our left extreme is high).
- Rear f 0 / .05: +0.33 / +0.26; rear f 1.0: −0.31.

**W : H** (sheet → ours), §3.9:

| View | Sheet | Ours |
| --- | --- | --- |
| Front | 1.32 | 1.22 |
| Side | 1.20 | 1.03 |
| Rear | 1.28 | 1.12 |
| f34 | 1.57 | 1.14 |
| r34 | 1.42 | 1.17 |

### N2, plug exposure: fixed

- `PLUG_H`: rx 0.45 → **0.36**, centre z −0.04 → −0.08, top 0.16 → **0.13**.
- `CROWN_H`: z0 0.10 → 0.07 (top at 0.17).
- The outer leaf roots start at r **0.21**, z 0.10–0.12 (`ARCH_BASE_R`), inside the crown.
- L2, the leaf nearest the rear camera, comes down over the plug to the ground, with a broad base (`SKIRT`: half width
  0.24 W on its stalk).
- Broad stalks on the other lower leaves made crossing slivers in the heart, so they were dropped.

| Plug pixels / green pixels | Sheet | Round 2 | Round 3 |
| --- | --- | --- | --- |
| Rear | 2.9 % | 9.5 % | **3.5 %** pass |
| f34 | 1.7 % | 8.3 % | **3.4 %** pass |
| r34 | 3.1 % | 10.6 % | **2.6 %** pass |
| Front / side (not in the criteria) | 1.1 / 2.3 % | 3.7 / 5.6 % | 5.5 / 5.1 % |

The front and side figures are inflated by shaded bud pixels: hue ~40° with v < 0.74 lands in the plug mask. The
darker bud keys add more of these.

### Minors

1. **Bud keys −6 % in value, at the same hue and saturation.**
   - Keys: `bud` #EED3A0 → **#E0C696**, `bud_tip` #E6D3B4 → **#D8C6A9**, `bud_base` #EED29A → **#E0C591**.
   - Main bud, verifier box (sheet → ours):

     | View | Lit quartile | Median |
     | --- | --- | --- |
     | Front | #FEEFCA → #FFF6C7 (round 2 #FFFFD4) | #F2D59E → #F0D8A6 |
     | f34 | #FEEEC9 → #FFFFC7 (round 2 #FFFFD5) | #F0D3A1 → #FFECA7 |
     | Side | #FEECC4 → #FFFFC7 | #F4D8A8 → #DEBC84 |
     | Rear | #FEECC6 → #F7DCB4 | #F1D3A3 → #E7C993 |
     | r34 | #FEEBC2 → #F7DCB4 | #F3D5A7 → #E8CA93 |

   - The part bud renders #FFE9A5 (sheet #F0D5B0).
   - The lit side now clips less in the front and f34. The rear and r34 medians are now 10–20 darker than the sheet
     (in round 2 they were within 7).
   - The studio's one-sided key light still decides this, so it stays a Studio check.
2. **Short bud nearer the axis: fixed.**
   - The short stem's base moved to (−0.12, 0.25, 0.20). The lean is unchanged (43° toward az −51), so the projected
     angles are unchanged (30° in the front, 36° in the side), and the stem still crosses the main stem inside the
     heart.
   - Bud bottom (0.374, −0.360, 1.04), top (0.458, −0.464, 1.54): top at r **0.65** (round 2 0.84, plan 0.62).
3. Inner leaves: see N1.

### Colour (sheet → ours, green medians)

The leaf keys are unchanged (#5A8044 / #7A9C48 / #3A5A2E).

| View | Sheet | Round 2 | Round 3 |
| --- | --- | --- | --- |
| Front | #6A9643 | #60873C | **#699546** |
| Side | #618C46 | #719C45 | #77A347 |
| Rear | #699343 | #5D853D | #517335 |
| f34 | #6D9844 | #679241 | **#72A24A** |
| r34 | #5F8A3F | #60893C | #557D3B |
| Top | #67933D | — | **#689341** |

- The front, f34 and top are within 5–9.
- The rear is darker (−24…−32), because the rolled side leaves show their keel sides to it.
- The side is lighter, because L4 shows its full lit face.
- Colour is still by position only: the base → tip ladder along the leaf's own (arc-length) t, keel faces a step
  darker, and a heart field by distance from the axis. There is no facing term, and the Tint mottling is unchanged.

### Honest assessment

The rosette now reads like the sheet's in the front, f34 and r34. It is a dense mound of broad, overlapping, faceted
boards:
- the upper leaves are carried out level and drop only at the tip;
- the lower leaves fall to the ground;
- the front diamond is in front;
- the buds rise on stems out of the leaf mass;
- the plug shows only as dark wedges at the ground.

Every N1 / N2 number passes, and the technical side is clean.

Still unlike the sheet:
- The sheet's three-quarter cells are drawn lower and wider (W : H 1.57 against our 1.14; §3.9).
- The rear is darker than the sheet.
- The side shows a large face-on L4 with spiky ends.
- The top view's leaves are rounder than the sheet's sharp diamonds, and I2 adds an eighth bump.
- The front's far-right column is L1's high tip, where the sheet has L7 on the ground.
- The bud's lit side still runs pale yellow under the studio key light (a Studio check).

I would expect round 3 to score about 7–8/10.

## Stage 7 — Verification (round 3)

Fresh verifier (did no other stage and was neither earlier verifier), read-only. Background session on port 9881 with
`wip/M018_verify.blend` (the kit copy saved after the main session's round-3 rebuild). The file was not saved, `build()`
was not called, and the session is stopped. Fresh renders came from `m018.render_views` (long-lens `*_sheet` cameras)
with `M.MODEL_RENDERS` redirected to the verifier's scratchpad (`…/scratchpad/v18r3/renders/M018/`). The scratchpad
also holds `cmp_<view>.png` (sheet cell | ours, cropped to the object at the same height; r34 flipped) and
`cmpp_f34/r34.png` (sheet hero | our perspective hero). The repo renders were not touched.

Every number was re-measured with:
- `M.audit`;
- my own BVH self-intersection and ray-parity scans;
- my own UV rasteriser at 1024² over Blender's loop triangles;
- a facing/colour regression over the `flintkit_hex` keys;
- `K.check` and `m018.measure()`;
- my own fill, width and colour scripts, using the same masks on both images.

**Verdict: FAIL, 6/10.** The technical side is clean. N2 passes. Every numeric acceptance line written for N1 passes,
and the leaves are now broad, which fixes the round-2 horns. But beside the sheet's hero crops, the rosette still
doesn't read as the sheet's low, wide, dense mound:
- It reads as an upright **cone/tent**: short stalks rise to a joint at r 0.3, z 0.55–0.70, then straight boards fall
  to the ground, leaving open space between and under them.
- The front diamond stands too tall.
- The top view, a pointed seven-point star in round 2, has turned into a cabbage of blunt, round boards.
- In the r34 hero the short bud is hidden.

### Technical (all re-measured)

| Check | HerbShrubNode | Bud | Stem | Leaf | RootPlug |
| --- | --- | --- | --- | --- | --- |
| Tris (budget) | 840 (4000) | 30 (1000) | 32 | 32 | 80 |
| Size (studs) | 2.953 × 2.611 × 2.200 (decision 2.85 × 2.65 × 2.2 ±0.15/±0.15/±0.1: inside) | 0.507 × 0.522 × 0.680 | 0.147 × 0.159 × 0.750 | 1.552 × 0.757 × 0.278 | 0.838 × 0.855 × 0.770 |
| Shells / non-manifold / boundary / wire / loose / zero-area / dup verts / n-gons | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 | same | same | same | same |
| Normals (signed volume) / odd-parity (inverted or interior) faces | outward / 0 | outward / 0 | outward / 0 | outward / 0 | outward / 0 |
| Self-intersections (BVH, triangulated, non-adjacent pairs) | 0 | 0 | 0 | 0 | 0 |
| Min corner angle | 5.13° | 43.0° | 10.7° | 31.4° | 53.8° |
| UV: overlapping texels at 1024² (strict interior) / flipped / bounds / density p5–p95 | 0 / 1 degenerate* / 0.008–0.992 / ±0.1 % | 0 / 0 / in / ±0 % | same | same | 0 / 0 / in / −3…+2 % |
| Origin / rotation / scale / modifiers / custom normals | bottom centre (0,0,0) / 0 / 1 / none / none | same | same | same | same |

\* Hero polygon 810, the only quad left, is non-convex in UV. One of its loop triangles has a signed UV area of
−1.9e-7: three nearly collinear UVs, effectively zero area. It covers no texels (overlap 0). This is trivial and isn't
a finding. (A naive fan triangulation of that quad double-counted 238 boundary texels, which is a measuring artefact.)

- Flat shading (0 smooth faces). `Tint` corner attribute on the hero is 0.76–1.05.
- `K.check`: no problems. `studs` "3.0 x 2.6 x 2.2"; the `tris` property (840) matches the mesh.
- 19 materials on the hero, all used. No emission, metal 0, leaf/stem specular 0.06, rough 0.80–0.95. No VFX sockets
  and no children (decision 7: correct).
- **Facing check** (key luminance against face nz, with height regressed out):
  - leaf: partial r +0.01 (raw +0.07);
  - stem: −0.13.
  - None of the leaf or stem colour comes from facing. The bud's +0.52 is meaningless: its five keys
    (#E0C591 / #E0C695 / #E0C696 / #DCC6A0 / #D8C6A9) are within about 1 % luminance.
  - The plug's −0.58 is the crown/shade position field accepted in rounds 1–2: the dark crown disc sits on top.

### N1 / N2 against the round-2 pass criteria (my numbers)

| Criterion | Sheet | Ours | Result |
| --- | --- | --- | --- |
| Front outer columns f .85/.90/.95, dTop within ±0.10 | .62/.59/.54 | .58/.56/.53 (−.04/−.03/−.01) | pass |
| f34 outer columns f .85/.90/.95 | .66/.63/.58 | .61/.60/.58 (−.05/−.03/.00) | pass |
| Rear width at h 0.2 / 0.3 ≥ 0.85 | .97 / .89 | .97 / .86 | pass |
| Top shows seven tips with notches | pointed star | seven lobes, but blunt and round (see B2) | numerically pass, visually weak |
| Plug / green pixels ≤ 4.5 % (rear, f34, r34) | 2.9 / 1.8 / 3.2 % | 3.5 / 3.4 / 2.6 % | **N2 pass** |
| Leaves read as broad overlapping boards (cmp_*) | — | broad: yes. Overlapping into a mound: no | **fail** (B1–B3) |

On the plug:
- The front and side "plug" shares (5.5 / 5.2 %) come from shaded bud pixels caught by the T mask: the T median there
  is tan, #97825C / #89744F.
- With a dark-only plug mask (max < 115), the front plug is 135 px, against the sheet's 192 at a smaller scale.
- Visually, the plug is now a dark rim at the ground. The pot is gone.

**Measurements the round-2 criteria missed** (sheet → ours):

| View | Mound width at h .3 / .4 / .5 / .6 | Lower-half fill (object share of bbox, bottom 50 %) | Green median height p50 | W : H |
| --- | --- | --- | --- | --- |
| Front | .88/.78/.78/.77 → .79/.66/.89†/.47 | .65 → .50 | .36 → .40 | 1.32 → 1.22 |
| Side | .97/.84/.48/.56 → .82/.66/.56/.36 | .69 → .50 | .32 → .35 | 1.20 → 1.03 |
| Rear | .89/.79/.83/.65 → .86/.72/.68/.57 | .72 → .41 (bottom 15 %: .40 → .08) | .36 → .45 | 1.28 → 1.12 |
| f34 | .91/.80/.77/.77 → .70/.57/.94†/.58 | .62 → .58 | .39 → .40 | 1.57 → 1.14 (§3.9) |
| r34 | .95/.86/.76/.51 → .67/.54/.94†/.44 | .70 → .48 | .34 → .41 | 1.42 → 1.17 (§3.9) |

† The single row where L1/L3's level tips sit. Every other row of the mound is 0.1–0.3 narrower than the sheet's.

The sheet's leaf mass is a dome: wide at h 0.3–0.6 and filled down to the ground. Ours is a cone: narrow at mid-height,
with one spike row at L1/L3's level, and open underneath (rear bottom-15 % fill 0.08 against 0.40).

### Shape against the sheet hero crops (`cmpp_f34`, `cmpp_r34`, `cmp_*`)

- **Right:**
  - two cream buds on six-sided green stems, graded in height;
  - the leaves are broad and faceted, with no horns or "^" blades;
  - L1/L3 carry out level and drop at the tip;
  - the plug shows only as a dark rim;
  - the seven outer leaves sit at sensible azimuths;
  - the parts match their cells.
- **Unlike the sheet:**
  - **f34 hero.** The sheet is a wide, low clump. Big boards fan out almost horizontally on both sides, the left one
    drooping to the ground (f0 h .19), and the stems stand clear above a mound top at h ~.65.
  - Ours is a compact, upright bush. The lower-tier boards hang from z ~0.7 down to the ground like kites. The left
    extreme is high (f0 h .51). The inner leaves stand as a green wall round the stems up to h ~.7.
  - **r34 hero.** The sheet shows both buds and both stems clearly above the leaves. In ours the short bud is a sliver
    behind a dark inner/upper leaf (bud share U .098 against .142).
  - **Front diamond (L6, KITE).** The sheet's is a compact pyramid with its top at h ≈ 0.27. Ours is a large kite to
    h ≈ 0.43 that covers the lower centre, with another leaf showing below it.
  - **Top.** The sheet's top is a crisp star of pointed diamond leaves. Ours is broad blunt boards (visible board
    W : L ≈ 0.65 by the modeller's own figure), and only the front kite reads as pointed.

### Departures by the modeller

| Departure | Ruling |
| --- | --- |
| Two-cubic `arch_path` (stalk + board), arc-length t | **Accept.** Sound and clean: 0 crossings, 0 inverted. The problem is where the joint and board sit, not the method. |
| `BOARD_OUTLINE` instead of the brief's (0.72, 0.46), (0.88, 0.32) | **Accept the reasoning** (the brief's values give blunt tips). But the result is still too broad for the short boards (B2). |
| L2 lower tier, not upper | **Accept** (the side and rear need it). |
| Outer W 0.82–0.96 instead of 0.95–1.05 | **Accept for the whole leaf.** But the stalk eats about 25–30 % of L, so the visible board is W : L ≈ 0.65, broader than the sheet's ~0.5 (B2). |
| Roll ±15° on L1/L3/L4/L7 | **Accept.** It is the main cause of the darker rear (minor 1). |
| L1/L7 azimuth swap (354° / 28°) | **Accept.** It costs front f1.0 (+.39) and f34 f0–.10 (+.32/+.19) (minor 3). |
| Inner I1/I2 widened to W 0.70/0.68 and rolled 75°/−25° | **Partly reject.** Together with L3's high board, they make the green wall round the stems and hide the short bud in r34 (B3). |
| `KITE` front diamond at joint z 0.70 | **Reject the height** (B1). The kite shape is fine. |
| `PLUG_H` rx 0.36, crown lowered, roots at r 0.21, L2 skirt | **Accept.** N2 is fixed. |
| Bud keys −6 % | **Accept.** The front and f34 clip less. Rear and r34 are now 8–22 darker (minor 2, Studio). |

### Colour (sheet → ours; Δ = ours − sheet in R, G, B)

| Region | Front | Side | Rear | f34 | r34 | Top |
| --- | --- | --- | --- | --- | --- | --- |
| Green median | #6A9643 → #699546 (−1,−1,+3) | #618C46 → #77A347 (+22,+23,+1) | #699343 → #517335 (−24,−32,−14) | #6D9844 → #72A24A (+5,+10,+6) | #5F8A3F → #557D3B (−10,−13,−4) | #67933D → #689341 (+1,0,+4) |
| Green lit / shade | #A3C551 / #3C632B → #96C151 / #47632C | #A8C45B / #375C23 → #96C052 / #486933 | #9CC04F / #3C6128 → #7AA043 / #344E21 | #A0C352 / #3E652F → #9AC351 / #517735 | #9DC24D / #345724 → #7BA143 / #3C5C28 | #92B94E / #365C2B → #90BA51 / #44652E |
| Bud median | #F6D9A5 → #FFECAD (+9,+19,+8) | #F6DAAC → #FFDB9F (+9,+1,−13) | #F1D4A5 → #E9CB95 (−8,−9,−16) | #F2D4AA → #FFECAA (+13,+24,0) | #F4DAAA → #E8CB94 (−12,−15,−22) | #F0D6A4 → #FBE3B5 (+11,+13,+17) |
| Plug (dark mask) | #352A1C → #221A12 (−19,−16,−10) | #3A2F1F → #352C24 (−5,−3,+5) | #3B2F20 → #352B22 (−6,−4,+2) | #362A1C → #27201A (−15,−10,−2) | #3C2F1F → #3A3026 (−2,+1,+7) | — |

Parts (sheet cell → our part render, median):
- bud #F8DDAF → #FFE9A5 (+7, +12, −10), with the lit quartile #FEEFCA → #FFFFD1, still clipping toward lemon;
- stem #669044 → #61883A (−5, −8, −10);
- leaf #6C9A4B → #72A34B (+6, +9, 0);
- plug #967A63 → #9A7B61 (+4, +1, −2).

Colour is good in the front, f34, top and the parts. The rear and r34 are darker, because the rolled leaves show their
keel sides. The side is lighter, because of the face-on L4. Both effects are geometry, not keys, and B1 changes them.
The blending is by position (base → tip ladder, heart field) with broad mottling and no confetti.

### Findings

**B1, blocker: the rosette is a cone, not the sheet's dome-shaped mound** (cmpp_f34, cmpp_r34, cmp_front/side/rear).
- Lower-tier L2/L4/L6/L7 rise only to a joint at r 0.27–0.31, z 0.55–0.70, then fall in a straight line at 28–40° to
  the ground.
- The result is narrow at mid-height (width at h .3–.6 is 0.44–0.72, against the sheet's 0.76–0.97) and open
  underneath (lower-half fill .41–.58 against .62–.72).
- The front diamond is too tall.
- **Cheap fix (`ARCH` / `ARCH_KW` only):** give L2/L4/L7 the L1/L3 shape, with their tips kept on or near the ground:
  - joint r 0.30 → **0.40–0.45**, z ≈ 0.70;
  - `handles` (0.45, 0.30) → **(0.30, 0.55)**;
  - tip slope −28…−40 → **−50…−55**.
  - The board then holds z 0.7–0.85 out to r ≈ 0.9 and drops only its outer third, so it curtains down to the ground.
- L5: joint z 0.30 → 0.50.
- L6 (front diamond): joint (0.27, 0.70) → **(0.30, 0.42)**, tip (1.30, 0.00), slope −30, so its top sits at h ≈ 0.25–0.3.
- **Accept when:** mound width at h 0.3–0.6 is ≥ 0.75 in the front, rear, f34 and r34, outside the L1/L3 row; lower-half
  fill is ≥ 0.60 in the front, side, rear and r34; and the front diamond's top is at h ≤ 0.32. Keep the round-2/3
  criteria (outer dTop, rear width, plug ≤ 4.5 %).

**B2, blocker: top view regressed from a pointed star to blunt, round boards** (cmp_top; round 2's top was right).
- The stalk takes 25–30 % of each leaf. The remaining board has W : L ≈ 0.65 and keeps half-width 0.40 W at u 0.72.
- **Cheap fix:**
  - `BOARD_OUTLINE` → (0, 0.24), (0.30, 0.46), (0.50, 0.44), (0.72, 0.30), (0.88, 0.12);
  - outer W: L2/L4/L7 0.96/0.82 → **0.82/0.75**, L1/L3 0.90 → 0.84;
  - leave L5/L6.
- Visible-board W : L should come out at about 0.5–0.55, the sheet's.
- **Accept when:** `top_sheet` reads as seven pointed diamond tips like the sheet's top cell (the polar tip counter still
  finds 7, and no outer leaf reads as a disc).

**B3, blocker: the short bud is hidden in the r34 hero** (cmpp_r34; sheet U .142, ours .098).
- The sheet shows both buds and both stems standing clear of the leaves in the rear three-quarter.
- **Cheap fix:**
  - I2: tip z 1.62 → **1.30** and `INNER_ROLL` −25° → **0°** (it may also move to az 105°);
  - I1: tip z 1.75 → 1.45;
  - if L3's level board (148°, z ≈ 1.05) still crosses the r34 sightline, lower its joint to z 0.62.
- **Accept when:** the short bud is ≥ 70 % visible in `r34_sheet` (and in `rear34`), and the bud share is ≥ 0.12.

**Minor (note if not fixed):**
1. **Rear and r34 green** are 10–32 darker than the sheet's (rolled leaves show their keels). Re-check after B1;
   don't touch the keys.
2. **Bud:** the front, f34 and part lit sides still clip toward lemon (#FFFFD1 against #FEEFCA). The rear and r34
   medians are now 8–22 darker. This is a Studio check under the game's sun; don't re-key.
3. **High extremes:** front f1.0 (+.39) and f34 f0 (+.32), both from the L1/L7 swap. Accepted.
4. **W : H is narrower than the sheet's** in the front (1.22/1.32), side (1.03/1.20) and rear (1.12/1.28). This is
   bounded by decision 1's footprint. B1 widens mid-height but not the bbox. Accepted.
5. **UV:** hero polygon 810, the last quad, is UV-degenerate (one loop triangle of area 2e-7). If the modeller is in the
   builder anyway, triangulating it removes the note; otherwise ignore it.

**Studio (Requires Manual Validation):** bud clipping under the game's sun; the leaf base → tip ladder through the
palette export.

**For the main session:** every numeric acceptance line written for round 3 passes, and N2 is fixed. The FAIL rests on
the visual criterion the round-2 verifier also set ("leaves read as broad overlapping boards" forming the sheet's
mound), now backed by the mid-height width and lower-half fill numbers above. If the 2-round cap rules out a fourth
round, I'd rank the remaining work as B1 > B3 > B2. B1 is parameters only (`ARCH`, `ARCH_KW`) and is likely to improve
the r34 bud sightline and the top view as well.

## Main session decision after round 3 (2026-10-28)

Committed at round 3 (verifier 6/10). Every numeric target from round 2 passes, the leaves are broad, the plug is hidden, and both buds read. The remaining difference is proportion: a cone against the sheet's low, wide mound. It is recorded for a polish pass, in the verifier's order: B1 (lower-tier arch shape and L5/L6 joints), then B3 (inner leaves lower so the short bud shows in r34), then B2 (narrower `BOARD_OUTLINE`). Hero 840 tris, one shell, `problems` empty. Export: 5 assets, 0 problems.
