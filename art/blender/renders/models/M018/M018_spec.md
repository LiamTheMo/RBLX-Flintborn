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
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m018_study\`
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
