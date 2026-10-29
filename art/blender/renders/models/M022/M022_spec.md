# 022 Fiber Shrub — spec

Reference: `art/blender/assets/references/022.png`. The sheet's own title is "FIBER SHRUB — SHRUB • RESOURCE • FOLIAGE",
"Individual Model Study", header "PAGE 19/132" (INDEX.md row 22 calls it "Flintborn Fiber Shrub Model Study"; the page
number on the sheet is not the index number). The image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m022.py` → `build()` (stages 1–6 below). Procedure: `art/blender/kit/mcp/STAGES.md`
(one modeller does stages 1–6 in a background Blender; the main session does stage 7).

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7).

Sheet text:
- **Header:** "A stylized shrub that provides fiber. Chunky, low-poly, hand-crafted look with broad flat-shaded faces
  and simple forms. Designed for clear silhouette and readability in the world."
- **Material palette:** Leaf Green, Leaf Dark, Wood Brown, Fiber Tan.
- **Views:** Front Three-Quarter (Hero), Rear Three-Quarter, Front, Side, Rear, Top.
- **Exploded Construction, "Reusable Modular Parts":** labels Fiber Tuft, Leaf, Stem Fork; five loose peg cylinders
  with dashed arrows into the fork's flat limb ends, the crotch and the limb sides.
- **Close-ups:**
  - "Part Close-Up — Fiber Tuft" (+ "Bottom View"): "Simple faceted planes. Attaches to stem fork peg."
  - "Part Close-Up — Leaf" (+ "Thickness View"): "Broad, flat facets. Slight thickness for volume."
  - "Part Close-Up — Stem Fork" (+ "Underside View"): "Main trunk element. Leaves and fiber tufts plug into flat join
    surfaces on top."
- **Modeling notes:** "Keep forms chunky and readable with broad, flat-shaded faces."; "Use simple, clean geometry
  with modular, reusable parts (leaf, fiber tuft, stem fork)."; "Maintain consistent silhouette, proportions and
  material palette with the Flintborn style."
- **Game context:** `src/shared/Resources/NodeCatalog.luau` has the node id **`FiberPlant`** (material Fiber, 2 hits,
  Hand 2 / Sickle 3, Farming); `ResourceService.luau` scatters 40 of them with a 2 × 3 × 2 green placeholder block.
  The old R05 kit sheet has `FiberShrub` (6.8 W × 5.9 D × 6.3 H, 1016 tris, `harvest_hit` + `harvest_deplete`) and
  owns the `FiberShrub*` names (§8). MODEL_PROGRESS row R05 marks it "partial: thin dark spiky leaves; small tucked
  fiber tufts".

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is about
`#F1EEE9`; each view's paper is the median of its box's top and bottom 4 rows. The masks are `cls()` in `m.py`
(HSV; background = within 16 of the paper):
- **L, leaves:** sat ≥ 0.28, hue 62–165°, g > 45.
- **T, fiber tufts:** hue 30–52°, sat 0.12–0.62, v ≥ 0.74. (Lit wood is hue 26–28°, so it stays out; hue 24–29 was
  tried first and pulled lit fork faces into T.)
- **W, wood:** sat ≥ 0.25 and hue < 30° (or ≥ 340°) with v < 0.86, or hue 30–45° with v < 0.62.
- **O, other:** ground shadow, the "UB" of the title inside the hero box, dark edges; not counted in the shares.

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m022_study\`.
Run with the scratch venv `...\scratchpad\venv22\Scripts\python.exe` (uv venv on python3.14 with Pillow + numpy; the
uv-managed interpreter itself refuses package installs).
- **Helpers:** `m.py` (masks, view boxes `V`, `stats`), `bb.json` (silhouette boxes).
- **Measurements:** `measure.py` → `measure_out.txt` (bboxes, shares, top profiles, width per height, region
  extents); `wood.py` → `wood_out.txt` (stem runs per height); `comps.py` → `comps_out.txt` (tuft components per view);
  `blobs.py` (close-up proportions by PCA).
- **Colour:** `samp.py` → `samp_out.txt` (swatches, views, parts, close-ups); `leafgrad.py` → `leafgrad_out.txt` (leaf
  base → tip, leaf and wood height bands); tuft and wood gradients are inline in this spec (§5.2).
- **Crops:** `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `cu_tuft.png`,
  `cu_leaf.png`, `cu_fork.png`, `pal.png`, `notes.png`; grids `g_*.png` (10 % grid on the silhouette bbox, red = centre
  lines); mask previews `cls_*.png`.
- **Zooms:** `z_f34_base.png` (stems and collars), `z_f34_tufts.png`, `z_expl_fork.png`, `z_expl_tuftTL.png`,
  `z_expl_pegs.png`, `z_expl_leafTL.png`, `z_expl_right.png`, `z_rear_base.png`, `z_r34_base.png`, `z_top_c.png`.
- **To run the scripts on our renders,** point `R` (in `m.py`) at the render, set the view box, and re-run
  `measure.py` (it rewrites `bb.json`).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (forage resource node, `FiberPlant`). Hero budget 4000 tris, each part under 1000.
  WorldModeling §16 suggests about 250–1,000 for a forage shrub; the plan in §4.3 lands at about 1300–1700 after the
  union (M017's bush was about 2200). Don't chase 1000 by thinning leaves or blades.
- **Overall read (check this first).** A chunky fan-shaped shrub, wider than tall (front W : H 1.31):
  - **a short faceted brown stem cluster** — one flared foot that splits low (z ≈ 0.6) into six limbs: two short low
    side stubs, two front stems carrying tufts, a thin back-right stem carrying a small tuft, and a back stem that holds
    the back leaves. The stems show plainly at the bottom centre of every elevation view (W 16–17 % of the silhouette);
  - **nine thick, lens-shaped leaves** radiating from the stems in a fan: two tall uprights at the back (they make the
    top of the silhouette and its centre V-notch), two splayed side leaves each side (one up at about 35°, one low at
    about 12°), one rounded leaf at the back centre and two low back diagonals. **The front centre stays open** so the
    stems show;
  - **three pale tan fiber tufts**, each a crown of pointed faceted blades sitting on a flared brown collar at the top of
    its stem: two big ones in front (left higher), one small one higher at the back right.
  - Hero shares: leaves 64 %, fiber 19 %, wood 17 %.
- **Focal silhouettes, in order:**
  1. The fan: two tall leaf points at the top with a V between them, broad pointed leaves splaying out and down to both
     sides (tips at h .71 and .27 left; .66 and .22 right).
  2. The three tan crowns of blades in front of the leaves, each on a visible brown collar.
  3. The stem cluster with see-through gaps between the stems at the bottom centre.
- **Target size: about 4.7 W × 3.9 D × 3.6 H studs** (H = 0.65 of the 5.5-stud character, the top of WorldModeling's
  0.25–0.65 C forage-shrub range; W : H 1.31 is inside its 0.9–1.6). Tolerances W ±0.25, D ±0.35, H ±0.2. Decision §8.1.
  - **How it was derived.** The sheet has no character and no part with an obvious real size. M017's decision fixed the
    forage-bush family at the design doc's ceiling: `BerryBushNode` is 4.3 × 3.5 × 3.6. Using the same height for the
    fiber shrub keeps the two forage nodes one family. The front cell (245 × 187 px) then gives **52 px per stud**;
    the hero (359 × 262 px) about **76 px per stud** horizontally.
  - **Depth:** side cell D : H 1.015 → 3.65; top W : D 1.14 → 4.1 (but the top is tilted, §3.5). 3.9 splits them.
  - **Alternatives:** R05's scale (about 6.3 tall, ×1.75, taller than the player) or the gameplay placeholder's 3 studs
    (0.55 C; × 0.83 → about 3.9 × 3.25 × 3.0).
  - Resulting part sizes: leaves L 2.0–2.5 × W 0.9–1.05; tufts Ø 1.3 / 1.15 / 0.7; stems Ø 0.3–0.5; foot Ø 1.35.
- **Build frame:** front −Y, +X right, ground z 0, origin = the stem foot's axis on the ground. The bbox centre then sits
  at about (0, +0.3); stage 2 re-centres to the bbox bottom centre.
- **Stud mappings used below:**
  - front cell X = (f − 0.50) × 4.7, z ≈ h × 3.6 (camera about 10° up, §3.1);
  - hero (f34) X = (f − 0.50) × 4.7, screen up = z cos e + Y sin e with e ≈ 12–14°;
  - rear cell X = (0.50 − f) × 4.7 (screen right = −X);
  - side cell Y = (f − 0.50) × 3.65, **screen right = +Y (the back)** for the kit side camera at az 90 (+X);
  - top cell: counts and spread only (§3.5).

### 1.2 Measured views (`measure.py`, `comps.py`)

| View (box) | Silhouette bbox (px) | W : H | Leaves L | Fiber T | Wood W | Tufts visible |
| --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (305,104,690,398) | 317–675 × 114–375 (359 × 262) | 1.370 | 63.9 % | 19.1 % | 17.0 % | 3 |
| Rear three-quarter (690,104,1010,398) | 694–1005 × 113–375 (312 × 263) | 1.186 | 76.4 % | 11.2 % | 12.4 % | 3 |
| Front (14,452,274,662) | 21–265 × 463–649 (245 × 187) | 1.310 | 63.9 % | 19.9 % | 16.1 % | 3 (T2 and T3 touch) |
| Side (278,452,500,662) | 292–488 × 457–650 (197 × 194) | 1.015 (D : H) | 64.5 % | 18.9 % | 16.5 % | 2 |
| Rear (504,452,760,662) | 513–751 × 463–650 (239 × 188) | 1.271 | 70.4 % | 12.2 % | 17.4 % | 2 |
| Top (764,452,1010,662) | 771–1003 × 456–659 (233 × 204) | 1.142 (W : D) | 77.8 % | 17.0 % | 5.2 % | 2 |

- **Reading:** the front and the hero are the same drawing (§3.1). From the back the leaves cover more (the back-centre
  leaf hides the front tuft T2 and part of the stems): fiber 11–12 % against 19–20 % from the front.
- **Verifier tolerance:** shares ±4 points (top ±6); profile values ±0.06 h; positions ±0.06 of W/H unless stated.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .74 | .73 | .70 | .68 | .64 | .70 | 1.0 | .93 | .86 | .78 | .54 | .83 | .89 | .95 | .85 | .69 | .75 | .61 | .63 | .66 | .69 |
| Front | .71 | .68 | .66 | .64 | .60 | .70 | .70 | .99 | .90 | .82 | .67 | .80 | .87 | .93 | .89 | .66 | .70 | .73 | .60 | .63 | .65 |
| Side | .22 | .48 | .69 | .66 | .64 | .73 | .69 | .66 | .87 | 1.0 | .95 | .88 | .81 | .70 | .75 | .79 | .84 | .88 | .53 | .51 | .49 |
| Rear | .26 | .65 | .62 | .74 | .71 | .76 | .73 | .96 | .95 | .85 | .69 | .84 | .91 | .99 | .78 | .69 | .73 | .63 | .66 | .69 | .71 |
| r34 | .37 | .66 | .74 | .72 | .75 | 1.0 | .94 | .89 | .83 | .69 | .81 | .86 | .92 | .95 | .65 | .69 | .73 | .63 | .66 | .68 | .32 |

- The **V-notch** between the two tall leaves: front h .67 at f .50 (f34 .54 at .50, rear .69 at .50).
- The side-leaf tips: front f 0.0 at h .71 (upper) and h .27 (lower); f 1.0 at h .65 (upper) and h .22 (lower).

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .09@.45 .59@.30 .92@.08 .91@.00 .77@.14 .86@.09 .92@.05 .82@.02 .42@.29 .40@.29 .01@.29
front  .20@.41 .74@.15 .95@.05 .88@.03 .78@.12 .87@.07 .95@.03 .84@.00 .40@.31 .37@.33 .01@.33
side   .11@.42 .66@.14 .79@.00 .82@.11 .90@.07 .83@.14 .70@.14 .63@.22 .48@.38 .13@.41 .02@.45
rear   .12@.44 .40@.29 .91@.04 .88@.07 .77@.10 .87@.06 .94@.03 .86@.14 .37@.32 .34@.34 .31@.36
```

So the fan is two-tiered: widest at h .2 (the low side leaves) and h .6 (the upper side leaves), pinched at h .4
(0.78 W) between them; above h .75 only the two tall leaves (0.37–0.42 W).

**Stem runs** (`wood.py`, W mask, front cell; width as a fraction of W, × 4.7 for studs):

```
h .00  .47-.56 (.09)                      ground contact point of the foot (elevated view)
h .02  .36-.64 (.29 = 1.36)               the foot at the ground
h .10  .29-.71 (.42 = 1.97)               foot + the two low side stubs, seen from above
h .15  .41-.60 (.20 = 0.94)               the trunk/foot above the stubs
h .20  .40-.63 (.23)
h .25  .38-.47 (.09 = 0.42)  .47-.53 (.05, back stem S4)  .55-.67 (.12 = 0.56, S2 leaning right)
h .30  .35-.45 (.10 = 0.47, S1)  .47-.52 (.05, S4)  .55-.58
h .35  .33-.39 / .40-.46 (S1 and its collar)
h .50  .70-.76 (.05 = 0.24, S3 under T3)
```

The f34 and rear agree within ±0.02. The rear shows more stem above h .4 (its left tuft's stem S3 at f .26–.34,
h .4–.6).

**Tuft components** (`comps.py`; centre (f, h); extents):

| View | Tufts |
| --- | --- |
| f34 | T1 (.340, .538), f .21–.48, h .36–.75, 97 × 103 px (1.27 × 1.35 studs); T2 (.627, .420), f .52–.75, h .27–.60, 83 × 87 (1.09 × 1.14); T3 (.766, .629), f .71–.84, h .53–.75, 48 × 59 (0.63 × 0.77) |
| front | T1 (.344, .532), f .21–.49, h .35–.74; T2 + T3 (.686, .475), f .54–.84, h .27–.73 (touching) |
| side | (.266, .571), f .09–.40, h .42–.76; (.585, .438), f .46–.72, h .29–.62 |
| rear | left (.230, .648), f .13–.31, h .51–.79 (small: T3 from behind); right (.705, .515), f .60–.81, h .34–.74 (big: T1) |
| r34 | (.215, .647) f .10–.29; (.504/.589, .51) f .46–.70 (one tuft split by a leaf edge); (.723, .627) f .66–.80 |
| top | (.423, .575) f .28–.55, h .42–.77; (.698, .415) f .58–.85, h .28–.59 |

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, governs; `g_f34.png`).** Like M020's, it is **not** a three-quarter view: the leaf fan
is left–right symmetric and the stems stand at the centre, so the camera is on the front axis (az ≈ 0) and a little
higher than the front cell (e ≈ 12–14°, §3.1).
- **Leaves (6 visible):** left upper (tip f .00, h .74, rising about 37° to the left, base hidden behind T1); left low
  (tip f .00, h .30, almost flat, its broad face turned up toward the camera, base near the stems at f .38, h .12);
  tall back-left (tip f .29, h 1.0); tall back-right (tip f .67, h .97); right upper (tip f .98, h .69); right low
  (tip f 1.0, h .21, face up). The tall pair is behind the tufts; the low side leaves are in front of the upper ones.
- **Tufts:** T1 big, left of centre and highest of the two front tufts; T2 right of centre, lower and leaning right;
  T3 small, higher, back right, partly behind the right upper leaf. Each crown shows 7–10 blade tips.
- **Stems (`z_f34_base.png`):** five stem pieces read at the foot: a low stub out to the left (to f .28, h .10), S1 up to
  T1's collar, a darker back stem S4 between S1 and S2, S2 up-right to T2's collar, a low stub out to the right. S3 shows
  above the right leaves only under T3 (f .68–.73, h .5). Each tuft sits on a **flared collar** at the stem top, about
  1.3–1.5 × the stem's width. Gaps between stems at h .25–.35 show the paper.
- **Facets:** leaves 0.3–0.6-stud flat triangles, a midrib ridge and a raised centre vertex on each face; stems 7–8-sided
  with irregular facets; tufts one or two big planes per blade side.

**Front (`g_front.png`).** The same composition at a lower elevation (≈ 10°). Same leaf tips (§1.2 top profile), T1 at
the same place, T2 and T3 touching. Use it for the orthographic profiles.

**Side (`g_side.png`; kit camera at +X has screen right = +Y, the back).** Narrower (D : H 1.015).
- **Tufts:** two, both in the **front half** (screen left): a high one leaning forward (f .09–.40, h .42–.76 → Y −1.5 …
  −0.37) and a lower one at the centre (f .46–.72, h .29–.62 → Y −0.15 … +0.8). By height these are T1 and T2; T3 (on
  the +X side, nearest this camera) is not seen (§3.3).
- **Leaves:** a tall one at the centre (tip f .47, h 1.0 → Y −0.1); one leaning back (tip f .87, h .88 → Y +1.35, z 3.2);
  a back one out to f 1.0 at h .48 (Y +1.8); a short low one at the back (f .56–.81, h .1–.25); front leaves to f .03
  at h .3–.48 and to f 0.0 at h .19 (Y −1.8, z 0.7).
- **Stems:** foot f .33–.65 at h .05 (1.17 stud); S1 leaning forward to the high tuft (f .26–.40 at h .40); S2 to the
  centre tuft.

**Rear (`g_rear.png`; screen right = −X).** The front's fan seen from behind, plus a **rounded leaf at the centre**
(f .33–.55, h .20–.61 → X +0.8 … −0.23, z 0.72–2.2) standing almost face-on to the camera and covering the stems' upper
part. Two tufts: small and high at screen left (T3, X +0.85 … +1.74) and big at screen right (T1, X −0.47 … −1.5). T2 is
hidden behind the centre leaf. Stems fan out at the base, five visible; S3 shows from h .4 to .6 at f .26–.34. This
agrees with the hero, so the rear is **not** a mirror.

**Rear three-quarter (`g_r34.png`).** The back with three tufts (small and high at the left, a big one at the centre,
a small one at the right) and three big leaves turned face-on toward the camera in front of the stems: the back-centre
leaf (f .24–.51, h .24–.57), a low back-left leaf (f .10–.38, h .05–.33) and a low back-right leaf (f .53–.85,
h .17–.40). These two low back leaves are the ones the front and rear cells don't show (LH, LI in §2.2). Compare with
the kit rear34 (152, 12) by counts (§3.4).

**Top (`g_top.png`; image top = back by kit convention, §3.5).** A star of **9 leaves** about 40° apart round the
centre, two tufts near the middle (left-of-centre and right), the brown stems showing between and below them, and one
darker leaf at the image bottom. The cell is drawn from about 60–70° up (blade and leaf undersides show), so its W : D
(1.14) and positions are not plan measurements.

**Close-ups (`cu_tuft.png`, `cu_leaf.png`, `cu_fork.png`).**
- **Fiber Tuft** (648,716,1002,950): a crown of about 11 pointed blades round a narrow waist; outer blades 35–50° up,
  inner ones nearly vertical; each blade a broad lance with a midrib fold and 2–3 facets a side; a short brown 8-sided
  **peg** under the waist (Ø about 0.2 of the crown width, as long). Crown W : H 1.06 including the peg (PCA, `blobs.py`).
  Bottom view: the peg with a dark socket hole (notation) and the blades radiating round it.
- **Leaf** (648,958,1002,1188): a **lens/kite pointed at both ends**, W : L 0.46, widest at 0.45–0.55 L (width profile
  0.10 0.22 0.34 0.42 0.45 0.44 0.40 0.32 0.22 0.09 along L); the front face rises to a midrib ridge and a raised centre
  vertex at about 0.55 L, with 8–10 broad facets. Thickness view: a spindle, W : L 0.27 seen slightly off edge, so the
  real thickness is about 0.15 L.
- **Stem Fork** (648,1197,1002,1425): a Y — a straight trunk about 1.4 × a limb's width, flared slightly at the foot,
  splitting at about 0.45 of its height into a near-vertical left limb and a right limb leaning 30–35°; 7–8-sided
  sections, flat **join surfaces** on top with a small dark socket dot (notation). Underside view: the trunk end (with a
  socket hole) and three limbs (the Y plus a side branch).

### 1.4 Parts (Exploded Construction (15,760,640,1300), `expl.png`)

Scale: the exploded parts are drawn about 1.05× the hero's scale (exploded tuft about 100 px across against the hero
T1's 97 px), so about 79 px per stud. Facet language for every part: broad flat-shaded facets, chunky, no noise.

#### Stem Fork (225,1040,470,1290), about 212 × 238 px (`z_expl_fork.png`)

- **Shape:** a faceted 8-sided trunk (Ø about 0.76 at mid height, a slight flare at the foot), splitting at about 0.45 of
  the height into **two upper limbs** (left nearly vertical, leaning 10° left; right leaning 30–35°), plus **one low
  side branch** going out to the left at about 60° from vertical. Limbs Ø 0.44–0.5, flat 8-sided end faces with a dark
  socket dot (notation only, decision §8.5), a small peg socket also marked on the right limb's side.
  Part size about **2.7 W × 1.0 D × 3.0 H** at 79 px/stud.
- **In the hero** the stems are shorter and more numerous (§3.2): the foot splits at about z 0.6 into six limbs.
- **Construction:** `_stem_fork(limbs, foot_r, split_z, seed)`:
  - a trunk loft (8 sides; rings at z −0.1, 0.25, split_z) with ±6 % radius and ±8° twist jitter per ring;
  - each limb a loft of 7–8 sides from inside the trunk (start 0.25 below split_z, on the axis) to its end, 3–4 rings,
    tapering 10 %, with a flat end cap; an optional **collar** (`collar=True`) flares the last 0.28 to 1.35 × Ø;
  - the exported part is the exploded call (trunk + 2 limbs + side branch); the hero the six-limb call (§2.1);
  - the limbs' bases overlap inside the trunk; one exact union, floor-cut at z 0.
- **Triangles:** trunk 8 × 3 × 2 = 48; limb 8 × 3 × 2 + cap 6 ≈ 54; collar 8 × 2 × 2 = 32 → part about 210, hero
  stems about 48 + 6 × 54 + 3 × 32 ≈ **470**.

#### Leaf ×5 in the exploded: (50,905,265,1030) 215 × 125 px, (330,800,450,975), (468,990,620,1095), (40,1075,230,1220), (455,1130,600,1240)

- **Shape (close-up governs):** a thick lens pointed at both ends, **W : L 0.46**, widest at 0.5 L, **thickness about
  0.15 L** (front 0.6 of it, back 0.4). The front has a midrib ridge from base to tip and a raised centre vertex at
  0.55 L; the back is a lower single ridge. Faces are broad facets (8–10 on the front). No serration, no spikes, no
  bend beyond a slight tip droop.
- **Size (hero governs):** L 2.0–2.5, W 0.9–1.05; the back-centre leaf rounder (L 1.75, W 1.0).
- **Construction:** `_leaf(L, W, seed)`:
  - outline 10 points (base, 4 per side at 0.15/0.35/0.6/0.82 L with half-widths 0.30/0.46/0.44/0.26 of W, tip),
    ±4 % jitter;
  - an inner ring of 6 points at 0.55 × the outline (about 0.2–0.85 L) raised to 0.45 × the front thickness, and a
    front apex at 0.55 L raised to the full front thickness; back: the outline fanned to one back apex at 0.5 L, 0.4
    of the thickness down;
  - front 10 + 12 + 6 = 28 tris, back 10 → **about 38 tris**. Use this, **not** `K.leaf` (a 16-tri shallow wedge) or
    `NS["leaf"]` (narrow, serrated).
  - A short hidden petiole wedge (0.2 long) at the base so the union bites into the stem.

#### Fiber Tuft ×2 in the exploded: (150,770,260,905), (455,870,580,1005); two more tufts peek out behind the low leaves

- **Shape:** about 10–11 blades round a narrow waist: an inner ring of 4 blades at 70–85° from horizontal and an outer
  ring of 6–7 at 35–55°, each yawed ±10°. Blade L 0.7–1.0 of the crown height, W about 0.25 L, thickness 0.08 L; a
  diamond section with a midrib (one fold), widest at 0.35 L, a sharp tip. The blades' bases meet in a waist (Ø about
  0.45 of the crown) that sits in the stem's collar. A short brown peg (Ø 0.26, 0.22 long) under the waist (part only;
  hidden in the hero).
- **Size (hero governs):** T1 crown Ø 1.3 × H 1.35 (waist to the highest tip), T2 Ø 1.15 × 1.2, T3 Ø 0.7 × 0.85.
- **Construction:** `_tuft(diam, height, n_inner, n_outer, seed)`:
  - each blade: 4 verts at the base (diamond), 4 at 0.35 L, 1 tip → 16 tris;
  - waist: a 6-sided short cone (12 tris) the blades sink into;
  - peg (part only) 8 sides, 16 tris;
  - 10 blades + waist ≈ **170 tris** (T3 with 7 blades ≈ 125).

#### Pegs ×5 (loose cylinders between the parts, `z_expl_pegs.png`)

- 8-sided cylinders about Ø 0.3 × 0.4 with a socket dot: joinery notation. **Not modelled in the hero** (every join is
  hidden inside a collar or a stem); the Tuft part keeps its own short peg as drawn in its close-up (decision §8.5).

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, origin = the foot axis). Azimuths are measured from +X
counter-clockwise (front = 270°, back = 90°); elevation = rise from horizontal.

### 2.1 Stems (`_stem_fork` hero call)

| Limb | From (inside the foot) | To (end) | Ø | Carries | Sheet evidence |
| --- | --- | --- | --- | --- | --- |
| Foot (trunk) | z −0.1 … 0.6 on the axis | — | 1.35 at z 0 → 0.95 at z 0.5 | everything | front h .02 run 1.36, h .15 run 0.94 |
| SL low-left stub | (−0.2, 0, 0.3) | (−0.95, −0.15, 0.5), flat end | 0.42 | leaf LB | f34/front left stub to f .28, h .10 |
| SR low-right stub | (+0.2, 0, 0.3) | (+0.95, −0.1, 0.48), flat end | 0.42 | leaf LF | right stub to f .70, h .08 |
| S1 left front | (−0.12, −0.1, 0.5) | (−0.5, −0.55, 1.32) + collar | 0.47 → 0.43 | T1, leaf LA | front run f .35–.45 at h .30 (X −0.7 … −0.24) |
| S2 right front | (+0.12, −0.1, 0.5) | (+0.3, −0.6, 1.0) + collar | 0.5 → 0.45 | T2 | front run f .55–.67 at h .25, leaning right |
| S3 back-right thin | (+0.15, +0.15, 0.6) | (+1.0, +0.35, 1.72) + collar | 0.3 | T3, leaf LE | f34 f .68–.73 at h .5; rear f .26–.34, h .4–.6 |
| S4 back | (0, +0.15, 0.5) | (0, +0.4, 1.2), flat end | 0.45 | LC, LD, LG, LH, LI | the dark run f .47–.52 at h .25–.30 |

- Collars: the stem's last 0.28 flares to 1.35 × Ø (S1 0.62, S2 0.65, S3 0.42), 8 sides, a flat top just under the
  tuft waist.
- Stems lean outward: S1 about 30° from vertical, S2 about 25°, S3 about 45°, S4 15° back. Keep see-through gaps between
  S1, S4 and S2 in the front view at h .25–.35.

### 2.2 Leaves (9 copies of `_leaf`, each with its own seed)

| Leaf | Base (on) | Azimuth | Elevation | L × W | Tip (expected) | Sheet evidence |
| --- | --- | --- | --- | --- | --- | --- |
| LA left upper | (−0.4, +0.05, 1.05), S1 side | 172° | 37° | 2.4 × 1.05 | (−2.30, +0.32, 2.49) | front tip f .00, h .71 (X −2.35, z 2.56) |
| LB left low | (−0.45, −0.25, 0.45), SL | 205° | 13° | 2.15 × 1.0 | (−2.35, −1.14, 0.93) | front tip f .00, h .27; face rolled up to the camera |
| LC tall back-left | (−0.12, +0.3, 1.15), S4 | 160° | 73° | 2.5 × 1.0 | (−0.80, +0.55, 3.55) | front tip f .33, h 1.0; rear tip f .66, h 1.0 |
| LD tall back-right | (+0.12, +0.3, 1.15), S4 | 20° | 72° | 2.45 × 1.0 | (+0.80, +0.55, 3.50) | front tip f .67, h .97; rear f .37, h 1.0 |
| LE right upper | (+0.55, +0.1, 1.1), S3 side | 8° | 35° | 2.15 × 1.0 | (+2.30, +0.35, 2.34) | front tip f .99, h .66 |
| LF right low | (+0.45, −0.25, 0.45), SR | 335° | 10° | 2.15 × 1.0 | (+2.35, −1.14, 0.82) | front tip f 1.0, h .22; face up |
| LG back centre | (+0.1, +0.5, 0.95), S4 | 82° | 50° | 1.75 × 1.0 | (+0.25, +1.55, 2.2) | rear centre leaf X +0.8 … −0.23, z 0.72–2.2, face-on |
| LH back-left low | (−0.2, +0.45, 0.6), S4 | 125° | 22° | 2.1 × 0.95 | (−1.32, +2.05, 1.39) | r34 low back-left face-on leaf; top count 9 |
| LI back-right low | (+0.2, +0.45, 0.6), S4 | 50° | 25° | 2.0 × 0.95 | (+1.36, +1.84, 1.45) | r34 low back-right face-on leaf; top count 9 |

- **Roll:** each leaf's broad face is turned toward the outside and up (the face normal about 30–50° above horizontal,
  pointing away from the stems), so the side leaves show their faces to the front and rear cameras (R05 build 4 had to
  fix edge-on side leaves). LG faces the back.
- **Tip droop:** 0.05 L on the side leaves, none on the tall pair.
- **Contact:** every leaf base (petiole) sinks 0.15 into its stem or collar side; leaves may overlap each other where
  they cross (LA behind T1, LB over LA's base, LE behind T3), never with coplanar faces.
- **Front gap:** no leaf between az 215° and 325° (the stems show in the hero and front cells).

### 2.3 Tufts (3 copies of `_tuft`)

| Tuft | Waist on (collar top) | Axis tilt | Crown Ø × H | Blades | Sheet evidence |
| --- | --- | --- | --- | --- | --- |
| T1 front-left | (−0.5, −0.55, 1.35), S1 | 20° toward az 200 (left, a little forward) | 1.3 × 1.35 | 4 + 7 | f34 f .21–.48, h .36–.75 (X −1.36 … −0.09); front f .21–.49, h .35–.74 (z 1.26–2.66) |
| T2 front-right | (+0.3, −0.6, 1.03), S2 | 25° toward az 345 (right) | 1.15 × 1.2 | 4 + 6 | f34 f .52–.75, h .27–.60 (X +0.09 … +1.18) |
| T3 back-right | (+1.0, +0.35, 1.75), S3 | 15° toward az 10 | 0.7 × 0.85 | 3 + 4 | f34 f .71–.84, h .53–.75; rear left tuft |

- **Expected hero:** X −2.37 … +2.35, Y about −1.55 … +2.35 (leaf half-widths included), z 0 … 3.6 →
  **4.7 × 3.9 × 3.6**.
- **f34_sheet (0, 14) checks:** W : H 1.30–1.42 (sheet 1.370); shares ±4 of 63.9 / 19.1 / 17.0; top profile ±0.07;
  V-notch at f .48–.56, h .50–.60; tuft components within ±0.06 of §1.2; 6 leaves and 3 tufts visible.
- **front_sheet (0, 10):** W : H 1.24–1.38 (sheet 1.310); width per height ±0.07 (the h .4 pinch at about 0.78 W).
- **rear_sheet (180, 10):** shares ±4 of 70.4 / 12.2 / 17.4; the centre leaf covers T2; 2 tufts visible, the small one
  at screen left.

## 3. View conflicts and resolutions

### 3.1 The "front three quarter (hero)" is an elevated front view

- **Evidence.** The leaf fan is symmetric about the stems, the side leaves' tips sit at f 0 and 1 at the same heights as
  the front cell's, the stems stand at the centre, and the tuft components sit at the same fractions as the front cell
  (T1 .340/.538 against .344/.532). Ground contact on the foot gives e ≈ 9–12° for the front cell; the hero looks down
  a little more.
- **Resolution.** Compare the hero with an extra **`f34_sheet (0, 14)`** and the front cell with
  **`front_sheet (0, 10)`**. The kit `front34 (−28, 12)` has no sheet counterpart: self-consistency only. The hero
  governs (WorldModeling §1.1).

### 3.2 Stem Fork (exploded) against the hero's stem cluster

- The exploded fork is a tall Y (trunk to 0.45 of 3.0 studs, two upper limbs, one side branch). Every assembled view
  shows a **short foot splitting at about z 0.6 into six stems** (two low stubs, S1–S4), none taller than 1.8.
- **Resolution** (M017's pattern): one builder `_stem_fork(limbs, …)`; the exported **`FiberPlantStemFork`** is the
  exploded call (Y + side branch, at the hero's limb thickness Ø 0.45–0.5); the hero is the six-limb call (§2.1). Same
  sections, facets, collars and keys.

### 3.3 Side cell: T3 missing, tall-leaf lean

- **Evidence.** The side cell shows two tufts in the front half, matching T1 and T2 by height; T3 (at +X, nearest a +X
  camera) isn't drawn. Its tall leaves lean one to the centre (Y −0.1) and one to the back (Y +1.35), but the rear cell
  shows both tall tips at h 1.0, which needs both at about the same depth.
- **Resolution.** The front and rear govern: tall pair symmetric at Y +0.55 (§2.2). The kit side camera is at az 90
  (screen right = back), which matches the sheet's forward tufts at screen left; T3 sits behind LE from that side and
  may show partly. Compare an extra **`side_sheet (90, 10)`** by shares (±5), tuft count 2–3 (both big tufts on the
  front half) and leaf count; record the misses.

### 3.4 Rear three-quarter

- **Evidence.** Three tufts and three face-on leaves in front of the stems (§1.3). With the kit `rear34 (152, 12)`
  (camera at the back right; screen right = (−0.88, +0.47) in plan) T3 lands at screen left, as drawn.
- **Resolution.** Compare by counts and shares (±5): 3 tufts, the back-centre leaf and the two low back leaves face-on,
  stems visible under them. W : H is not compared (the cell is drawn closer).

### 3.5 Top view: tilted, and one leaf the hero doesn't have

- **Evidence.** The top cell is drawn from about 60–70° up (leaf undersides and the tufts' collars show). It has 9 leaves
  about 40° apart **including one at the image top centre and one at the image bottom centre**, but the hero has no leaf
  at the front centre (the stems show there). Either orientation of the top cell puts one leaf where the hero has the gap.
- **Resolution.** The hero governs the front gap. Read the top cell with image top = back (kit convention): the darker
  bottom leaf is then the drawing's extra front leaf, and our LG fills the back centre. Judge the top only by: **8–10
  leaves radiating round the full circle**, 2–3 tufts near the middle, brown stems visible at the centre, W : D
  1.0–1.3. Compare the kit `top (0, 89)` and an extra `top_tilt (0, 65)`.

### 3.6 Exploded against the hero

- **Tufts:** the exploded shows two full tufts plus two more peeking from behind the low leaves; the hero shows three.
  Build 3 (decision §8.3).
- **Pegs and sockets:** construction notation; not modelled in the hero (§1.4, decision §8.5).
- **Leaf count:** the exploded draws 5 leaves; the hero needs 9 for the top cell's star (decision §8.2).

### 3.7 "Simple, clean geometry" and flat colours against the user's blended-colour rule

- The user's rule wins, and the sheet itself shows painted gradients (§5.3): leaves dark at the base and lime at the
  tip on every unshadowed exploded leaf; tuft blades orange-tan at the base and cream at the tip. Keep Tint low so the
  shrub still reads "clean".

### 3.8 Effects

- The sheet shows none (no glow, sparkle, floating fibres, dust). Stage 5/6 add nothing by default (§7).

## 4. Construction plan (modeller, stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `stem_fork()` → `FiberPlantStemFork`: the exploded Y + side branch (about 2.7 × 1.0 × 3.0), flat 8-sided end
     faces, no holes. Compare with `z_expl_fork.png` / `cu_fork.png`: split at 0.45 H, left limb near vertical, right
     30–35°, side branch low left.
   - `leaf()` → `FiberPlantLeaf`: L 2.3, W 1.05, thickness 0.35. Compare with the close-up: W : L 0.42–0.50, widest
     at 0.45–0.55 L, pointed both ends, raised centre vertex, a spindle edge-on (thickness 0.12–0.18 L).
   - `tuft()` → `FiberPlantTuft`: T1's size (Ø 1.3 × 1.35) with its peg. Compare with the close-up: 10–11 blades, crown
     W : H 0.95–1.1, waist and peg.
   - Render a parts shot (`extra`, about (−20, 15)) laid out as the exploded (fork low centre, leaf left, tuft upper
     left).
2. **Hero:**
   1. `_stem_fork` six-limb call (§2.1); `_paste` (m011 pattern) 9 leaves (§2.2) and 3 tufts (§2.3).
   2. Make each tuft one closed shell first (blades into the waist with `union_loose` + one exact union), then unite
      stems, leaves and tufts **one piece at a time**, saving the work file between risky steps; then `m004.floor_cut`
      at z 0.
   3. Origin at the bbox bottom centre; transforms applied. One closed shell (decision §8.6).
3. **Budget** (§4.3): hero about 1300–1700 (limit 4000), each part ≤ 250 (limit 1000). Spend spare tris on leaf facets
   (an extra inner ring) if the leaves read too plain against the hero; never on smoothing.
4. **Placeholder keys** (stage 1): `m022_leaf`, `m022_fiber`, `m022_wood`. Stage 4 adds the rest (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** a chunky fan, tall leaf pair at the top with a V between, side leaves in two tiers, three tan
      crowns on brown collars in front, stems and gaps at the bottom centre; nothing spiky or grassy.
   2. **f34_sheet (0, 14)** and **front_sheet (0, 10)** against their cells: §2.3's checks; 6 leaves, 3 tufts; stems at
      h .25–.35 split into 3 runs with gaps (§1.2 stem runs ±0.04).
   3. **rear_sheet (180, 10):** shares ±4; centre leaf covering T2; 2 tufts (small at screen left).
   4. **side_sheet (90, 10)** and **rear34 (152, 12):** shares ±5 and counts (§3.3, §3.4).
   5. **Top (0, 89) + top_tilt (0, 65):** 9 leaves round the full circle, 2–3 tufts near the middle (§3.5).
   6. **Kit views** (front34, front, side, rear, underside): self-consistency; the underside a flat foot with the stubs.
   7. **Parts against their cells** (§4.1).
   8. **Hero size** 4.7 × 3.9 × 3.6 (±0.25 / ±0.35 / ±0.2).
6. **Stage 2:**
   - zero non-manifold, boundary, wire and loose elements; no zero-area faces or n-gons; normals outward;
   - no faces under 5° where leaf petioles, blades, collars and limbs meet (m011 `_tidy` / `_desliver`);
   - don't decimate the leaves below their 10-point outline and raised centre, the blades below a diamond section, or
     the stems below 7 sides; keep the collars.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Stems (foot + 6 limbs + 3 collars) | 1 | 470 | 470 |
| Leaves (10-point lens, raised centre) | 9 | 38 (+4 petiole) | 380 |
| Tufts (blades 16 each + waist 12) | 3 | 170 / 150 / 125 | 445 |
| **Sum before union** | | | **about 1300** |
| **Hero after union** (seams, slivers, floor cut) | | | **about 1300–1700** (limit 4000) |
| Parts: StemFork / Leaf / Tuft | | | about 210 / 42 / 185 (limit 1000) |

## 5. Colour plan (modeller, stage 4)

### 5.1 Swatches (flat; medians of a 40 × 40 box inside each)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Leaf Green | (36,314,76,354) | `#6D9940` | 90°, 0.58, 0.60 |
| Leaf Dark | (104,314,146,354) | `#5D7237` | 81°, 0.52, 0.45 |
| Wood Brown | (174,314,216,354) | `#8D6241` | 26°, 0.54, 0.55 |
| Fiber Tan | (243,314,285,354) | `#EEBF7B` | 35°, 0.48, 0.93 |

- **Leaf Green** is close to the unshadowed exploded leaves (`#5D8333`–`#6A953C`) and a little lighter than the view
  medians (`#678A2E`–`#709530`).
- **Leaf Dark** is an olive (81°); the painted leaf bases are cooler and darker (`#3E603A`, 110°). Treat it as the dark
  end of the shaded half, not as the base key.
- **Wood Brown** matches the exploded fork (`#885E3D`) and the close-ups (`#865D3C`).
- **Fiber Tan** matches the close-up tuft (`#EEBC7B`) and the exploded tufts (`#F2C180`/`#F4C281`).

### 5.2 Rendered regions (`samp.py`, `leafgrad.py`; median / lit quartile / shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Leaves, f34 / front / side | V | L | `#6B8E2D` / `#688B2D` / `#6A8D2E` | `#96B93A` / `#92B538` / `#92B536` | `#3F5D25` / `#3D5A23` / `#3C5A22` |
| Leaves, rear / r34 / top | V | L | `#678A2E` / `#709530` / `#678C30` | `#8EB136` / `#97BB3A` / `#90B43A` | `#3E5B26` / `#436328` / `#395123` |
| Leaves, exploded (all) | (15,760,640,1300) | L | `#61893A` | `#8AB13F` | `#426533` |
| Leaves, exploded each | §1.4 boxes | L | `#59843F` / `#5E883E` / `#5D8333` / `#6A953C` / `#5F8732` | `#86B043`–`#8DB43D` | `#3A5C31`–`#476934` |
| Leaf close-up / thickness view | (655,990,860,1160) / (900,985,985,1115) | L | `#5E893F` / `#496C3A` | `#8AB14B` / `#5E833F` | `#42673B` / `#3C5B32` |
| Fiber, f34 / front / side / rear | V | T | `#F6C682` / `#F4C380` / `#F4C282` / `#F4C380` | `#FDE0AA` / `#FDDFAB` / `#FDDCA4` / `#FDDCA6` | `#D39E5D` / `#D49F5E` / `#D5A161` / `#D49F5D` |
| Fiber, r34 / top | V | T | `#F4C480` / `#EFBB76` | `#FDE1AE` / `#FDDB9F` | `#D6A25E` / `#D5A05E` |
| Fiber, exploded tufts / close-up / bottom view | (150,770,260,905), (455,870,580,1005) / (670,750,860,935) / (880,750,995,850) | T | `#F2C180`, `#F4C281` / `#EEBC7B` / `#F5C88A` | `#FEE0AC`, `#FDDFA8` / `#FDDDA4` / `#FEE0AB` | `#D8A667`, `#D9A465` / `#D19E60` / `#D9A96F` |
| Wood, f34 / front / side / rear | V | W | `#704D2F` / `#755132` / `#6E4C2F` / `#6D4C2F` | `#966841` / `#996B44` / `#8D623E` / `#91653F` | `#3D2B19` / `#402F1C` / `#47341F` / `#3D2E1B` |
| Wood, r34 / top | V | W | `#5E4228` / `#573D24` | `#7C5634` / `#7E5A34` | `#382918` / `#3A2C19` |
| Wood, exploded fork / fork close-up / underside | (225,1040,470,1290) / (655,1235,840,1420) / (870,1225,1000,1330) | W | `#885E3D` / `#865D3C` / `#8B6140` | `#A4734B` / `#B37F56` / `#B47F54` | `#63442C` / `#64462E` / `#69492F` |
| Pegs (exploded) | (215,945,470,1120) | W | `#916441` | `#C18B5F` | `#69492F` |
| Tuft peg (close-up / bottom view) | inside the tuft boxes | W | `#765436` / `#7F5938` | `#9D6E41` / `#C08B5D` | `#573C27` / `#593C25` |

**Gradients along a part** (medians in five equal steps):

```
leaf base -> tip
  close-up        #3E603A #49703F #5E8940 #87AC3F #8AB137
  expl top leaf   #3E6239 #4A713D #669240 #84AB3E #92B639
  expl right      #395A31 #486C31 #5F8534 #7DA137 #95B935
  expl right-low  #365531 #426532 #5F8732 #759F34 #8CB136
  f34 tall right  #3E5C21 #304A1E #55792C #799D2F #7DA333      (base in the stems' shade)
  f34 low right   #4B6C2A #53752B #70932A #799930 #97BB36
tuft base -> top
  close-up        #CF9C63 #E0AD70 #F6C17E #FCD191 #FADFA6
  expl TL / R     #DEAA6B #ECB777 #F5C887 #F6CE92 #FADDAE  /  #D1A165 #DEAD6E #F4C382 #FBD192 #FCDEA6
  f34 T1 / T2     #E9B16A #F9C780 #F8D18D #F7D093 #F3D5AD  /  -  #DAA465 #ECB371 #FAC981 #FBD18D
stem base -> top
  fork close-up   #8B603E #885E3C #80593A #795537 #B07C53      (top = the lit flat end face)
  expl fork       #8A603E #895F3D #835A3A #8F623F #966843
```

**Height bands** (median per 0.1 h, h 0 → 1):

```
front leaves  -  #55782B #79A032 #527228 #496A29 #63852D #70922F #789D30 #8DAE34 #94B337
rear leaves   -  #48692B #587B2B #55782F #668B30 #72942E #6C902E #779C2F #8BAA32 #92B235
front wood    #745033 #775233 #5C4028 #835C38 #856337 #906737           (h .2-.3 = under the tufts)
f34 wood      #765032 #734E30 #5A3F26 #734F2F #6F532F #7C5530
```

Deciles (dark → light), f34:

```
leaves #2C4717 #515B2C #547420 #5E7E28 #678A2C #6E9329 #799F2F #87AC31 #95B63D #A1C13B
fiber  #CA9357 #D4A265 #E3AA64 #EAB474 #F5BF7C #FEC981 #FAD28F #FED697 #FFDD9F #FFE7B3
wood   #2B2114 #412E18 #4D3622 #593C24 #68462D #755033 #805737 #8A5F3C #94653D #A16F46
```

### 5.3 How the colour works

**Leaves.**
- One yellow-green family: view medians hue 82–84°, sat 0.66–0.68. Lit faces lime (`#96B93A`), shade faces deep green
  (`#3F5D25`): that much is the sun on the facets; never paint by facing.
- **Painted base → tip gradient on every leaf** (unshadowed exploded and close-up): base dark, cool green (`#3E603A`,
  hue 110°, sat 0.35) → middle `#5E8940` (93°) → tip lime (`#8AB137`–`#95B935`, 80–82°). It shows in the hero too: the
  top bands (tall-leaf tips) are the palest (`#94B337`), the low bands darker.
- The leaf's two halves (either side of the midrib) differ only by light.

**Fiber.**
- Pale warm tan: hue 33–35°, sat 0.44–0.51. **Base → tip:** deeper orange-tan at the waist (`#CF9C63`–`#DEAA6B`) to
  cream at the tips (`#FADDAE`–`#FCDEA6`). The tufts render near the clip in the hero (median v 0.96).

**Wood.**
- Warm mid brown, hue 26–28°, sat 0.54–0.57 (unshadowed `#875D3C`). The hero's stems are darker (`#704D2F`) because the
  leaves and tufts shade them; the h .2–.3 band under the tufts is the darkest (`#5A3F26`–`#5C4028`). Flat end faces
  and collars render lighter only by light. Pegs a touch lighter (`#916441`), not needed in the hero.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered medians of **unshadowed** regions (exploded parts and close-ups), not swatches.
`K.sample` kinds: `"green"` for leaves; `"brown"` for wood; `"all"` on tight boxes for the fiber keys (cream fails the
brown filter's saturation test, as M020's cut wood did).

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m022_leaf` | `#62893C` (exploded leaf medians `#5D8333`–`#6A953C`; close-up `#5E893F`; swatch `#6D9940`) | leaf middles (t 0.3–0.7) | rough 0.8, `low_spec` |
| `m022_leaf_tip` | `#8CB238` (tip fifths `#87AC3F`–`#95B935`; hero tips `#85A63E`–`#97BB36`) | outer 30 % of each leaf | rough 0.8, `low_spec` |
| `m022_leaf_base` | `#42653A` (base fifths `#3E603A`, `#3E6239`, `#395A31`, `#365531`, second fifths `#49703F`–`#4A713D`) | inner 30 %, petiole, back ridge near the base | rough 0.8, `low_spec` |
| `m022_fiber` | `#F2C180` (exploded tufts `#F2C180`/`#F4C281`; close-up `#EEBC7B`; swatch `#EEBF7B`) | blade middles | rough 0.85 |
| `m022_fiber_base` | `#D9A567` (base fifths `#CF9C63`, `#DEAA6B`, `#D1A165`) | blade lower 30 %, waist | rough 0.85 |
| `m022_fiber_tip` | `#FADDA8` (top fifths `#FADFA6`, `#FADDAE`, `#FCDEA6`) | blade outer 30 % | rough 0.85 |
| `m022_wood` | `#875D3C` (exploded fork `#885E3D`; close-up `#865D3C`; swatch `#8D6241`) | stems, collars, the part's peg | rough 0.9 |
| `m022_wood_dark` | `#634530` (fork shade quartile `#63442C`–`#64462E`; hero under-tuft band `#5A3F26`–`#5C4028`) | stems between z 0.55 and 1.1 near the axis (under the tufts), crotches, ground contact | rough 0.9 |

**Calibration warnings:**
- **Fiber is near the clip in the hero** (`#F6C682`, lit `#FDE0AA`). Calibrate the three fiber keys on the close-up and
  exploded values; then check the f34_sheet fiber median within 10 of `#F6C682` and its base/tip spread ≥ 25 levels. If
  the tips wash out, lower the specular, not the contrast between keys.
- **Leaves:** greens calibrate darker than the painted sheet (kit memory); trust the render match. The hero leaf median
  must land within 12 of `#6B8E2D` with hue 80–86°; `leaf_tip` stays ≤ 84° hue, `leaf_base` ≥ 100° (cool).
- **Wood:** calibrate on the parts shot of the fork against `#885E3D`, then check the f34_sheet stem median within 12 of
  `#704D2F` (the studio's leaf shade should give most of the darkening; add `wood_dark` only where the bands still miss).

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Leaves** (field = each leaf's along-length t from its construction frame):
  - t < 0.3 `leaf_base`; 0.3–0.7 `leaf`; t > 0.7 `leaf_tip`; 3 steps, ±0.08 noise on t;
  - the tall pair LC/LD shift 0.1 toward the tip (their tips are the palest band in every view); the low leaves LB, LF,
    LH, LI shift 0.1 toward the base;
  - petiole faces `leaf_base`.
- **Fiber** (field = each blade's along-length t from the waist): t < 0.3 `fiber_base`; 0.3–0.7 `fiber`; > 0.7
  `fiber_tip`; 3 steps; waist `fiber_base`; T3 (in the back, small) +0.1 toward the base.
- **Wood:** `wood` base; faces with centre z 0.55–1.1 and within 0.35 of the foot axis → 50 % `wood_dark` (the shaded
  core under the tufts), fading over 0.3; z < 0.1 → 35 % `wood_dark`; broad patches (`K.patches` scale 0.6, level 0.3)
  between `wood` and a 30 % `wood_dark` mix; collars and flat ends plain `wood`.
- **Hard edges only** where materials meet: leaf | wood (petioles), fiber waist | collar, peg | fiber (part only).

### 5.6 Texture (Tint) and finish

- **Tint** (`tint_var` per piece about 0.04, so each leaf and tuft differs slightly):
  - leaves: `K.texture` amp 0.035, scale 0.5 (broad, per facet group);
  - fiber: amp 0.025;
  - wood: amp 0.05, scale 0.35 (along-stem mottling);
  - never per-triangle confetti.
- **Finish:**

| Material | Roughness | Specular | Metal | Notes |
| --- | --- | --- | --- | --- |
| Leaf keys | 0.8 | `FOLIAGE_SPEC` (`low_spec=True`) | 0 | matte faceted foliage |
| Fiber keys | 0.85 | normal (lower if the tips clip) | 0 | matte, dry |
| Wood keys | 0.9 | normal | 0 | matte bark |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Leaves:** f34_sheet median within 12 of `#6B8E2D`; base → tip order on the parts-shot leaf (dark cool base, lime
  tip); front height bands with h .9–1.0 the palest.
- **Fiber:** f34_sheet median within 10 of `#F6C682`; parts-shot tuft base → tip within 15 per step of the close-up row.
- **Wood:** parts-shot fork median within 8 of `#885E3D`; f34_sheet stems within 12 of `#704D2F`.
- **Shares** per §2.3 and §4 step 5.

## 6. Joins and contact (no cracks or seams on this sheet)

- **Limbs into the foot:** every limb starts on the axis 0.25 below the split, buried inside the foot; one exact union;
  the crotches are clean V's (fork close-up).
- **Tufts into collars:** the waist sinks 0.12 into the collar's flat top; the collar is 1.35 × the stem; no visible
  peg. The waist must not be coplanar with the collar top.
- **Leaves into stems:** each petiole sinks 0.15 into its limb, collar side or S4's end; the leaf base itself touches
  the stem (no floating leaves, no visible stalk).
- **Ground:** floor-cut at z 0 (`m004.floor_cut`); the foot and the two low stubs make the contact.
- Overlap everything; exact booleans (pitfall 10).

## 7. Lighting and VFX plan (modeller, stages 5 and 6)

**What the sheet shows:** an ordinary sunlit shrub. No glow, light, sparkle, floating fibres, dust or particles anywhere.
The pale tufts are diffuse (their shade quartile `#D39E5D` is still tan), not emission. WorldModeling §1.2 forbids "an
ordinary asset recolored neon with a glow halo"; §15: ordinary forage stays calm.

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight:** nothing glows. Emission ≥ 1.0 would export as flat Neon and erase the blades'
  base → tip gradient.
- **Studio note (Requires Manual Validation):** check in Studio that the tufts don't clip to flat cream under the game's
  sun and that the leaf base → tip gradient survives the palette export.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **Recommended: none.** The sheet shows no effect, and the other forage nodes (M017 `BerryBushNode`, M018
  `HerbShrubNode`) shipped none. Record "Stage 6 skipped: sheet shows no VFX".
- **Option** (decision §8.7): the R05 `FiberShrub` pair, if the main session wants hit feedback on fiber nodes:
  - `harvest_hit` at the tufts' front, (0, −1.4, 1.8), colour override `["#F2C180", "#6D9940"]` (fiber and leaf bits),
    scale about 0.5;
  - `harvest_deplete` at the foot, (0, 0, 0.4), same colours, `shape` about [3, 1, 3], scale about 0.3.
- **Not recommended:** `dust` (nothing floats on the sheet), `ore_glint` (reads as magic), any light.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by `git grep` of the repo and a search of every sheet .blend, zstd-decompressed
(`m020_study/blendall.py`):
- **R05 kit:** `FiberShrub` (48 hits in `FlintbornWorldKit.blend`, 49 in `R05.blend`), `FiberShrubLeaf`,
  `FiberShrubFiberTuft`, `FiberShrubStemFork`, `FiberShrubFiberBundle`, `FiberShrubDepleted`; keys `r05_fiber`
  (`#E2B878`), `r05_fiber_leaf` (`#2E7A24`), `r05_bark`.
- **`src`:** node id `FiberPlant` (NodeCatalog, ResourceService, BiomeCatalog) — a game id, not a kit object.
- **Other `*Leaf`/`*Fork` names:** M017 `BerryBushTrunkFork`, `BerryBushLeafClump`; M018 `HerbShrubLeaf`; W/V sheets'
  `*LeafClump`. None clash with the names below.
- `M.mk` would silently rename a clash to `<name>M022`, so avoid all of these.

**Proposed names.** `FiberPlantNode`, `FiberPlantStemFork`, `FiberPlantLeaf`, `FiberPlantTuft` and the `m022_` prefix
occur nowhere in the repo or any sheet .blend.

| Object | Part | Why |
| --- | --- | --- |
| `FiberPlantNode` | hero | matches the NodeCatalog id `FiberPlant`, as `BerryBushNode` / `HerbShrubNode` match theirs; R05 owns `FiberShrub*` |
| `FiberPlantStemFork` | Stem Fork (the exploded Y + side branch) | R05 owns `FiberShrubStemFork` |
| `FiberPlantLeaf` | Leaf | R05 owns `FiberShrubLeaf` |
| `FiberPlantTuft` | Fiber Tuft (with its peg) | R05 owns `FiberShrubFiberTuft` |

- Fallback if the main session prefers the sheet's word: `FiberShrubNode` (free), but then the parts need another
  stem than `FiberShrub*` (R05 owns those), so `FiberPlant*` keeps the set consistent.
- Palette keys `m022_*` (§5.4). Collection `Kit/M022 Fiber Shrub`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **4.7 × 3.9 × 3.6** (recommended: H 0.65 C like `BerryBushNode`, the design doc's ceiling for a forage
   shrub), or 3.9 × 3.25 × 3.0 (0.55 C, nearer the 3-stud gameplay placeholder), or R05's scale (about 6.8 × 5.9 × 6.3).
2. **Leaves:** **9** (recommended: the hero's 6 + the rear's centre leaf + two low back diagonals, matching the top
   cell's count), or 7 (only what the front and rear cells show; the top then reads sparse at the back).
3. **Tufts:** **3** (recommended: hero, r34 and rear agree), on collared stem tops.
4. **Stems:** **one `_stem_fork` builder; hero = foot + 6 limbs split at z 0.6; exported part = the exploded Y + side
   branch** (recommended, M017's pattern), or a hero built from the exact exploded fork (tall Y), which no assembled view
   shows.
5. **Pegs and sockets:** **not modelled in the hero; no socket holes anywhere; the Tuft part keeps its short peg**
   (recommended: hidden in every assembled view; holes add boolean risk), or loose peg parts exported too.
6. **Hero packaging:** **one closed shell** (recommended: STAGES default), tufts pre-united, pieces added one at a time.
7. **Stage 5/6:** **no emission, light or VFX** (recommended: the sheet shows none; matches M017/M018), or the R05-style
   `harvest_hit` / `harvest_deplete` pair in fiber and leaf colours (§7.2).
8. **Exports:** the hero plus 3 parts (`…StemFork`, `…Leaf`, `…Tuft`) (recommended). R05's `FiberBundle` drop and
   `Depleted` state are not on this sheet; not built unless asked.
9. **Comparison cameras** (§3): `f34_sheet (0, 14)` for the hero, `front_sheet (0, 10)`, `rear_sheet (180, 10)`,
   `side_sheet (90, 10)`, kit `rear34 (152, 12)` for the r34, kit top + `top_tilt (0, 65)`; kit front34 and underside as
   self-consistency; a parts shot `(−20, 15)`.
10. **Top-view front leaf** (§3.5): **hero governs, front stays open** (recommended), or add a short front leaf (loses
    the hero's stem gap).
11. **Names** as proposed.

## 9. Pitfalls to avoid

1. **Grass blades or spiky leaves.** R05 started grass-like and was marked "thin dark spiky leaves". These leaves are
   broad (W : L 0.46), **thick lenses** pointed at both ends with a raised centre — not `NS["leaf"]`, not `K.leaf`'s
   thin wedge, not cards.
2. **Edge-on side leaves.** Roll each leaf so its broad face shows to the front/rear cameras (§2.2); R05 build 4 had to
   fix this.
3. **Fur or fine fibres.** Each tuft is about 10 broad faceted blades on a waist (WorldModeling: "Do not add fine
   cotton fibers or fur"). Small tucked tufts were R05's other failure: T1 is 1.3 across, a third of the shrub's width.
4. **A green wall.** Keep the front centre open: the stems, their gaps and the collars must show at h .1–.35 in the hero
   and front.
5. **Floating tufts or leaves.** Every tuft sits in a visible flared collar; every leaf base touches a stem.
6. **One thick trunk or a tall Y.** The hero splits low into six stems (§3.2).
7. **Colour by facing.** Lime faces and dark faces on the same leaf are light; paint along each leaf's length only;
   `K.check` facing correlation < 0.5.
8. **Flat one-colour parts.** The leaf base → tip and the blade base → tip gradients are on the sheet (§5.3).
9. **Washed-out tufts.** They render near the clip; keep the base/tip spread.
10. **Exact booleans.** Overlap everything: limbs from inside the foot, petioles 0.15 into stems, waists 0.12 into
    collars, no coplanar faces (collar top vs waist bottom). Pre-unite each tuft; add pieces one at a time and save the
    work file between; remove slivers with m011's `_tidy` / `_desliver`.
11. **Comparing the wrong views.** The hero is an elevated front view; the top cell is tilted and has one leaf the hero
    lacks; the side cell hides T3 (§3).
12. **Side-view handedness.** The kit side camera at az 90 sits at +X, so screen right is the model's back; the sheet's
    side tufts at screen left are the front tufts.
13. **Naming clashes** with R05's `FiberShrub*` (§8). Don't edit shared helpers (`kit_models.py`, `kit_mcp.py`,
    `build_kit.py`, `lib/vfx.py`); put new helpers in `m022.py`. No commits, pushes or exports in the modeller's stages.

## Decisions (main session, 2026-10-28)

All recommendations are accepted:
1. Size: 4.7 W × 3.9 D × 3.6 H.
2. Nine leaves, including the rounded back-centre leaf and the two low back diagonals.
3. Three tufts, each on a flared brown collar.
4. One stem builder. The hero splits low, at about z 0.6, into six stems; the exported part is the exploded fork.
5. No pegs or socket holes, except the tuft part's own short peg.
6. One closed shell. Unite each tuft first, then add pieces one at a time.
7. No VFX.
8. Hero plus 3 parts; no depleted variant and no fiber bundle drop.
9. Comparison cameras: `f34_sheet (0,14)`, `front_sheet (0,10)`, `rear_sheet (180,10)`, `side_sheet (90,10)`, kit `rear34 (152,12)`, and the kit top plus `top_tilt (0,65)`.
10. The hero view governs the open front, over the top cell's extra leaf.
11. Names as proposed: `FiberPlantNode`, `FiberPlantStemFork`, `FiberPlantLeaf`, `FiberPlantTuft`.

Keep the tufts from washing out to white: calibrate them against the hero render, not only the swatch.

## Stage 1 — Modelling (modeller, 2026-10-28)

Builder `art/blender/kit/mcp/m022.py` (`build()` returns `audit`, `problems`, `log`, `uv`, `thin`, `self_hits`,
`inverted`, `views`). Background session port 9880, work file `art/blender/assets/kit/wip/M022.blend`. Helpers that live
in builders being edited in parallel (m017 / m018: `_union`, `_guarded`, `_polish`, `_seal`, `_tri_quads`) are copied
into the builder; m004 / m011 / m012 are imported.

**Parts, each its own function:**
- `leaf_mesh()` → `FiberPlantLeaf` (L 2.3, W 1.05): a 10-point outline pointed at both ends (`LEAF_OUT` half widths
  0.31 / 0.48 / 0.47 / 0.27 W at t 0.15 / 0.37 / 0.58 / 0.80); the front is a 6-point ring (midrib points at t 0.20 and
  0.86, side points at about half the half width) at 0.55 of the front thickness round a raised apex at t 0.53 (the
  close-up's centre vertex); the back a 4-point ring round a lower apex. Thickness 0.095 L front + 0.06 L back
  (0.155 L; the study's 0.15). Front and back are zipped by angle round the apex, so each leaf is star-shaped about its
  centre and can't fold through itself (inverted faces per leaf piece: 0 on all nine). 40 tris. Droop (t²) and the
  face direction are parameters. Not `K.leaf`, not `NS["leaf"]`.
- `blade_mesh()` / `tuft_mesh()` → `FiberPlantTuft`: a 6-sided waist cone and three rings of broad pointed lances
  (`TUFT_RINGS`: inner 74-84°, middle 58-68°, outer 44-54°; width 0.40 / 0.44 / 0.48 L; a diamond section with a
  midrib fold front and back, widest at 0.36 L, a third ring at 0.7 L, sharp tip; 22 tris a blade). Each blade is as
  long as both the crown height and diameter allow. The part has 11 blades and a short 8-sided brown peg (decision 5).
- `tube()` / `stems()` → the hero stem cluster; `fork_part()` → `FiberPlantStemFork` (the exploded Y: an 8-sided trunk
  r 0.40 → 0.36 to z 1.45 with a slight foot flare, left limb to z 3.0, right limb leaning ~33° to z 2.6, a low side
  branch out to the left; flat 8-sided ends; no socket holes, decision 5).

**Hero (`hero()`):** a low foot flare (r 0.56 → 0.36, z −0.15 … 0.30) and six limbs started inside it: low stubs SL /
SR, S1 / S2 in front (collared), S3 back right (collared), S4 at the back (thinner). Each collar is part of its limb
tube: the last 0.32 flares to 1.4 × the radius with a 0.08 rim (no separate boolean piece). Three tufts sit 0.12 into
the collar tops (T1 Ø 1.7 × H 1.55, T2 1.5 × 1.4, T3 1.0 × 1.0; blades 2 + 4 + 5, T3 2 + 3 + 4), pressed to 0.72 in
world Y about their foot (`TUFT_DEPTH`), with each blade's broad face turned 40 % toward the front (`FACE_TURN`), so
the crowns fan out to the sides like the sheet's instead of pointing blades at the camera (those read as foreshortened
dark needles). Nine leaves (`LEAVES`, decision 2) with their bases pulled within 0.6 × the host stem's radius of its
axis (no floating leaves, no visible stalk). The front stays open (decision 10).

Changes against the study's layout, each measured on the long-lens sheet renders:
- Foot: the study's r 0.70 trunk to z 0.62 read as a pot; the sheet's stems part at the ground (`z_f34_base`).
- Stem bases spread and S4 thinner (r 0.19 → 0.17), so the front's h .3 row shows separate runs with paper between:
  ours .34-.45 / .47-.54 / .54-.57 / .61-.65, sheet .36-.46 / .48-.53 / .55-.58 / .70-.71.
- S1 end x −0.55 and T1 tilted 18° toward az 195: T1 at f .18-.48 (sheet .21-.47).
- S3 end moved back to (0.95, 0.65, 1.75): at y 0.35 T3's blades grazed LE and left crossing faces after the union;
  the sheet draws T3 behind LE anyway.
- Leaves turned to face the front (side leaves `face` (0, −1, 0.8), low pair (0, −1, 0.55); the low pair first read
  edge-on); LA / LE longer and lower (2.45 / 2.3 at 34° / 32°) and the low pair shorter and higher (2.05 at 21° / 18°),
  so both tiers reach the silhouette's sides; the tall pair spread (az 166 / 14, el 68) for the V notch; LG's base
  lower (z 0.75; the rear's centre leaf spans h .20-.61); LH / LI longer and facing the back.

**Final measurements** (study masks, `m022.measure()`; sheet / ours):

| View | W : H | Leaves | Fiber | Wood |
| --- | --- | --- | --- | --- |
| f34_sheet (0, 14) | 1.369 / 1.352 | .638 / .626 | .192 / .176 | .170 / .199 |
| front_sheet (0, 10) | 1.321 / 1.360 | .639 / .619 | .200 / .175 | .161 / .206 |
| side_sheet (90, 10) | 1.016 / 1.041 | .645 / .611 | .190 / .190 | .165 / .199 |
| rear_sheet (180, 10) | 1.262 / 1.433 | .705 / .812 | .122 / .079 | .173 / .110 |
| r34_sheet (152, 12) | 1.188 / 1.317 | .763 / .769 | .113 / .088 | .124 / .143 |
| top_tilt_sheet (0, 65) | 1.139 / 1.495 | .778 / .699 | .170 / .182 | .052 / .119 |

- f34 top profile (f 0 … 1): ours .65 .64 .64 .63 .68 .75 1.0 .96 .89 .82 .70 .82 .88 .94 .99 .75 .71 .65 .66 .65 .66;
  sheet .74 .73 .70 .68 .64 .70 1.0 .93 .86 .78 .54 .83 .89 .95 .85 .69 .75 .61 .63 .66 .69. V notch h .70 (sheet .54
  f34, .67 front cell).
- f34 width per height (h 0 … 1): ours .01 .75 .91 .72 .76 .88 .97 .57 .44 .42 0; sheet .09 .59 .92 .91 .77 .86 .92
  .82 .42 .40 .01.
- Tuft components (a looser tan mask that includes shaded blades; f34): ours T1 f .18-.48 h .35-.79, T2 .53-.81 h
  .25-.66, T3 .70-.82 h .57-.81; sheet T1 .21-.47 h .36-.75, T2 + T3 .52-.85 h .26-.75. Rear: ours .16-.38 h .48-.80
  (T3) and .72-.82 h .58-.74 (T1's top); sheet .12-.31 / .60-.82.
- Size **4.91 W × 3.63 D × 3.45 H** (decision 4.7 ± 0.25 × 3.9 ± 0.35 × 3.6 ± 0.2: inside all three).

## Stage 2 — Optimisation and cleanup

- Union: `_union` (guarded exact booleans, one shell at a time, volume-checked, `view_layer.update()` before
  `split_loose` and before each boolean). Hero 50 shells, StemFork 4, Tuft 13: no retries, no failures. Then
  `m004.floor_cut` at z 0, the guarded sliver clean (`m011._clean`, max move 0.05 → 0.025; each step undone if it adds
  crossing faces or shells), `_finish`, `_polish` (quads split for the best angle, guarded `_force_slivers`, needle
  collapses, inverted-face removal + fan-fill reseal, guarded late collapses and `_flip_thin`).
- Fixes found in this stage: the tuft waist's bottom narrowed (0.30 → 0.18 of the crown diameter; at 0.30 the waist
  wall sat a hair inside the collar rim and left two inverted slivers and a crossing pair) and the blade bases moved
  inside the waist (base radii 0.03 / 0.07 / 0.11 of the diameter, at half the waist height); T2's tilt azimuth
  345 → 338 (345 / 342 left 1-2° union needles on a blade underside that no collapse or flip could fix).

| Object | Tris | Size (studs) | Shells | Non-manifold | Boundary | Wire / loose | Zero-area | n-gons | Dup verts | Normals | Min angle |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FiberPlantNode (hero) | 2066 / 4000 | 4.91 × 3.63 × 3.45 | 1 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | outward | 5.05° |
| FiberPlantStemFork | 278 / 1000 | 2.37 × 0.86 × 3.09 | 1 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | outward | 9.34° |
| FiberPlantLeaf | 40 / 1000 | 2.03 × 0.89 × 0.99 | 1 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | outward | 9.95° |
| FiberPlantTuft | 382 / 1000 | 1.56 × 1.65 × 2.02 | 1 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | outward | 6.02° |

- Hero before the union: 1602 tris (nine leaves × 40 = 360; T1 / T2 254 each, T3 210 (waist 12 + 22 a blade); stems
  about 524). Union seams and slivers bring it to 2066.
- Self-intersections (crossing face pairs without a shared vertex): 0 on every object. Inverted faces (ray parity
  along the normal, `inverted()`): 0 on every object. M017's 5-direction test at eps 2e-3 can flag one hero face in a
  < 2 mm crease between two T2 blades; at eps 2e-4 and 5e-5 it reports none (a crease, not an inside-out face).
- Origin at the bounding-box bottom centre on every object; transforms applied; no modifiers; no custom normals; flat
  shading. `K.check`: no problems.

## Stage 3 — UV

Smart UV (angle 45, ANGLE_BASED, margin 0.008) plus `m012._uv_unfold`:

| Object | Islands | Overlap pairs | Flipped | Min gap | Density (min / median / max) | Conformal stretch p95 |
| --- | --- | --- | --- | --- | --- | --- |
| FiberPlantNode | 398 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.009 |
| FiberPlantStemFork | 33 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.011 |
| FiberPlantLeaf | 3 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.024 |
| FiberPlantTuft | 59 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.019 |

## Stage 4 — Materials, colour and texture

**Keys and calibration** (`PALETTE`; targets are the spec 5.4 sheet medians of unshadowed regions):

| Key | Sheet target | Dome pass (K.calibrate, 6 iterations; dome median) | Final (hero pass) |
| --- | --- | --- | --- |
| m022_leaf | #62893C | #53733A (#61863C) | #608131 |
| m022_leaf_tip | #8CB238 | #729236 (#8AAF38) | #83A32E |
| m022_leaf_base | #42653A | #395838 (#41643A) | #406234 (kept cool, hue ~100°) |
| m022_fiber | #F2C180 | #BE9D6E (#F2C180) | #E9BB7C |
| m022_fiber_base | #D9A567 | #AA8758 (#D7A567) | #D2A063 |
| m022_fiber_tip | #FADDA8 | clipped on the dome (#F0B390, a pink cast): set by fiber's linear ratio, #C4B491 | #F1D5A3 |
| m022_wood | #875D3C | #6B4C31 (#865E3E) | #73492D |
| m022_wood_dark | #634530 | #4F3725 (#644734) | #553522 |

- Pass 2 (hero renders): each family corrected in linear light by the mean sheet / ours ratio over the f34, front and
  top: leaves ×(1.34, 1.27, 0.73), wood ×(1.16, 0.93, 0.85), fiber ×(1.28, 1.12, 0.93), then ×(1.07, 1.17, 1.21) and
  ×(1.17, 1.12, 1.15) as the crowns changed. The side and rear are lit by the studio's fill and read darker on every
  model: reported, not fitted (M017's rule).
- **Re-measured (sheet / ours):** f34 leaves #6B8E2D / #6B8F2D (lit #96B93A / #8EB234, shade #3F5D25 / #3B551D);
  front leaves #688B2D / #698E2C; top leaves #678C30 / #71962F; f34 fiber #F6C683 / #E7BB79 (lit #FDE1AB / #FFE19C,
  shade #D39E5D / #C99B5F); front fiber #F4C380 / #E6BA78; side fiber #F4C382 / #F3C785; f34 wood #704D2F / #6E452D
  (lit #966841 / #946E42); front wood #755132 / #6E452C. Side / rear / r34 leaves (studio fill): #6A8D2E / #4C6724,
  #678A2E / #547424, #709530 / #587926.
- Front leaf bands by height fifths (ground → top): sheet #54772B #709430 #5A7B2B #729530 #8EAF35, ours #547627
  #62842B #6C912E #7A9E30 #90B22F; the top band (tall-leaf tips) is the palest in both.

**Blending (positions only, never facing):**
- Leaves: along each leaf's own t, `leaf_base` → `leaf` across t 0.06-0.40 and `leaf` → `leaf_tip` across
  0.56-0.90, quarter steps (25 / 50 / 75 % mix keys), ±0.06 broad noise on t; tall pair +0.1 toward the tip, low leaves
  −0.1.
- Fiber: along each blade's t, `fiber_base` → `fiber` across t −0.1-0.24, `fiber` → `fiber_tip` across 0.46-0.84,
  quarter steps; waist `fiber_base`; T3 0.1 toward the base.
- Wood: `wood` with a 25 % `wood_dark` core under the tufts (z 0.55-1.1 within 0.35 of the axis, faded over 0.3) and
  broad noise patches up to 25 %; no darkening at the ground (the sheet's foot band isn't darker). Floor-cut faces
  plain `wood`.
- **Tint:** per-piece level ±0.04 (fiber ±0.024) and broad mottling: leaves amp 0.035 / scale 0.5, fiber 0.025 / 0.6,
  wood 0.05 / 0.35; jitter ≤ 0.005 (no per-triangle confetti).
- **Finish:** leaf keys roughness 0.8 with the foliage specular (`K.FOLIAGE_SPEC`, mix keys too via `_restyle`);
  fiber 0.85; wood 0.9; metal 0. The hero uses 20 material slots (8 keys + mix steps).

## Stage 5 — Lighting

Skipped (decision 7): the sheet shows an ordinary sunlit shrub; no emissive key, no light. Studio note (Requires
Manual Validation): check that the tufts don't clip to flat cream under the game's sun and that the leaf base → tip
gradient survives the palette export.

## Stage 6 — VFX

Skipped (decision 7): no glow, sparkle, floating fibres or dust on the sheet; no sockets (the hero has no children).
Renders were made with `vfx=True` (nothing to realise).

## Modeller's notes for the verifier

- Renders in `art/blender/renders/models/M022/`: the decision-9 long-lens cameras (`f34_sheet`, `front_sheet`,
  `rear_sheet`, `side_sheet`, `r34_sheet`, `top_sheet`, `top_tilt_sheet`; 3× lens as M018 / M020), the kit views,
  `exploded`, `part_stemfork`, `part_leaf`, `part_tuft`, and `M022_sheet_compare.png` (sheet cell left, ours right,
  each cropped to its silhouette). `m022.measure()` and `m022.compare()` re-run the study's masks.
- Known differences:
  1. **Tuft shading.** The sheet's tufts are bright on every face (shade quartile #D39E5D); in our studio the blades
     facing away from the sun go darker, so the fiber share reads .176 against .192 (f34) and the fiber median #E7BB79
     against #F6C683 (15 low in red; lit and shade quartiles within about 10). Raising the keys further clips the lit
     faces.
  2. **Tuft crowns** read a little rounder and fuller than the sheet's spikier flames in the f34 / front (the
     broad-face turn that cured the needle look softened the tips). The part tuft matches the close-up's open crown.
  3. **Rear:** the tufts show less (fiber .079 / .122): T1 sits behind LC / LA from the back. The sheet's rear shows
     more of both, which its own front cell's depths don't allow.
  4. **Top tilt** reads wider than deep (1.50 / 1.14) with more stem showing (.119 / .052): the sheet's top cell has a
     front leaf the hero doesn't (decision 10 keeps the front open).
  5. The V notch is shallower (h .70; sheet .54 f34, .67 front).
  6. Wood share a little high in the front views (.20 / .17): collars and stubs show; the stems are at the sheet's
     widths.
  7. The hero is 4.91 wide (limit 4.95) and 3.45 high (limit 3.4).
- Every union passed first try; nothing was left out.

## Stage 7 — Verification (round 1)

Independent verifier, 2026-10-28. Read-only background session on port 9882 with `wip/M022_verify.blend` (not saved,
`build()` not called). Fresh renders by `m022.render_views()` into the scratchpad
(`...\scratchpad\v022\renders\M022\`; the repo's render folder was untouched). Measured with `m022.measure()` (the
study's masks on both images) and with my own scripts: bmesh topology, BVH ray parity for interior faces, and
`v022\samp.py` for the colour gradients.

**Verdict: FAIL, 6/10.** The mesh is technically clean and the leaves, palette and blending are close. Three things
still read unlike the sheet: the tuft crowns, the fan's upper tier, and the rear.

### Technical checks (all re-measured; all pass)

| Object | Tris | Size (studs) | Shells | Non-manifold / boundary | Wire / loose | n-gons / zero-area | Dup verts | Self-hits | Inverted / interior | Min angle | Winding |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FiberPlantNode | 2066 / 4000 | 4.910 × 3.634 × 3.453 | 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 | 0 / 0 | 5.05° | consistent, volume +2.98 |
| FiberPlantStemFork | 278 / 1000 | 2.369 × 0.860 × 3.088 | 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 | 0 / 0 | 9.34° | consistent |
| FiberPlantLeaf | 40 / 1000 | 2.031 × 0.893 × 0.988 | 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 | 0 / 0 | 9.95° | consistent |
| FiberPlantTuft | 382 / 1000 | 1.564 × 1.647 × 2.016 | 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 | 0 / 0 | 6.02° | consistent |

- **Size against the decision** (4.7 ± 0.25 × 3.9 ± 0.35 × 3.6 ± 0.2): inside all three, but W 4.91 is 0.04 under its
  cap and H 3.45 is 0.05 over its floor. Any fix must keep W ≤ 4.95 and H ≥ 3.4.
- **Origin and transforms:** the local bbox is symmetric in X and Y with min z 0 (bottom centre) on all four objects;
  rotation 0, scale 1; no modifiers, no custom normals, no children, flat shading.
- **UV:** one `UVMap` each; 398 / 33 / 3 / 59 islands, 0 overlaps, 0 flipped, min gap 0.016, density 1.0, conformal
  stretch p95 ≤ 1.024.
- **Materials:** 20 slots on the hero (8 keys plus quarter-step mix keys), all used. Leaf roughness 0.8 with specular
  0.06; fiber 0.85; wood 0.9; metal 0; emission 0. There is a `Tint` corner layer (0.93–1.06, sd 0.021: broad, no
  confetti). `K.check` reports no problems.
- **No colouring by facing:** the correlation of key lightness with the face normal is |r| ≤ 0.16 per family (leaf
  nz 0.155, fiber −0.152, wood −0.126; ny and nx ≤ 0.06).
- **VFX:** none, as decided (decision 7).

### View comparison (sheet / ours, study masks)

| View | W : H | Leaves | Fiber | Wood | Notes |
| --- | --- | --- | --- | --- | --- |
| f34_sheet | 1.369 / 1.352 | .638 / .627 | .192 / .174 | .170 / .199 | shares OK (±4); profile misses: see B2 |
| front_sheet | 1.321 / 1.360 | .639 / .620 | .200 / .173 | .161 / .207 | wood +4.6, just over |
| side_sheet | 1.016 / 1.041 | .645 / .611 | .190 / .190 | .165 / .199 | shares OK (±5); back half low (profile .47 against .83–.88) |
| rear_sheet | 1.262 / 1.433 | .705 / **.812** | .122 / **.079** | .173 / **.110** | three shares out of ±4: see B3 |
| r34_sheet | 1.188 / 1.317 | .763 / .769 | .113 / .088 | .124 / .143 | OK (±5) |
| top_tilt_sheet | 1.139 / **1.495** | .778 / .701 | .170 / .180 | .052 / .119 | W : D over 1.0–1.3 |

- **f34 top profile** (f 0 → 1). Sheet: .75 .73 .70 .68 .63 .70 1.0 .93 .87 .78 **.54** .83 .89 .95 .87 .68 .75 .74
  .63 .66 .69. Ours: **.65 .64 .64 .63** .68 .75 1.0 .96 .89 .82 **.70** .82 .88 .94 .99 .75 .71 .65 .66 .65 .66.
- **f34 width per height** (h 0 → 1). Sheet: .07 .58 .91 .92 .77 .86 .92 .82 .42 .40. Ours: .01 .75 .91 **.72** .76
  .88 .97 **.57** .44 .42.
- **Stem runs at h .3, front.** Sheet .36–.46 / .48–.53 / .55–.58 / .70–.71; ours .35–.45 / .47–.54 / .54–.57 /
  .61–.65. Gaps show; the front is open.
- **Counts:**
  - nine leaves in the scene;
  - f34: 6 leaves and 3 tufts visible;
  - rear: 1 clear tuft plus the tip of T1;
  - top: nine leaves round the circle, two tufts near the middle.

### Colour (sampled on both images; Δ = ours − sheet, R/G/B levels)

| Region | Sheet | Ours | Δ |
| --- | --- | --- | --- |
| Hero leaves median / lit / shade (f34) | #6B8E2D / #96B93A / #3F5D25 | #6B8F2D / #8EB233 / #3B551D | 0,+1,0 / −8,−7,−7 / −4,−8,−8 |
| Hero leaf bands, bottom → top (f34) | #62842B #6A8F2F #62852D #799E30 #92B136 | #5A7C28 #61842A #6D922F #799D2F #92B72F | base −8,−8,−3; mid +11,+13,+2; tip 0,+6,−7 |
| Leaf base / mid / tip (close-up vs part_leaf) | #3F613B / #5E8940 / #8AB036 | #5C883A / #7AA337 / #98BE31 | **+29,+39,−1** / **+28,+26,−9** / +14,+14,−5 |
| Fiber base / mid / tip (close-up vs part_tuft) | #D09D64 / #F7C27F / #FADFA8 | #CF9655 / #E4B471 / #FFE2A0 | −1,−7,−15 / −19,−14,−14 / +5,+3,−8 |
| Fiber median (close-up vs part_tuft) | #EEBC7C | #F2C27B | +4,+6,−1 |
| Hero fiber median / lit / shade (f34) | #F6C683 / #FDE1AB / #D39E5D | #E6B877 / #FFDF9B / #C99B5F | **−16,−14,−12** / +2,−2,−16 / −10,−3,+2 |
| Wood (fork close-up vs part_stemfork) | #865D3C (hue 27°) | #865436 (hue 22°) | 0,−9,−6 |
| Hero wood median / lit / shade (f34) | #704D2F / #966841 / #3D2C19 | #6E452D / #946940 / #412719 | −2,−8,−2 / −2,+1,−1 / +4,−5,0 |

- **Blending:** the leaves go dark-cool to lime along each leaf, the blades orange-tan to cream, and the stems are
  mottled; there are no hard patches. The hero leaf gradient matches.
- **Misses:**
  - the hero fiber median is 16 low (the spec allows 10);
  - the part leaf has almost no dark base;
  - the wood is about 4–5° redder than the sheet.

### Findings

**Blockers** (each with a fix for a fresh modeller):

- **B1. The tuft crowns read as closed, shadowed balls, and as needle fans from the side.**
  - **Sheet:** each crown is an open flame of 7–10 distinct long pointed lances. The outer blades fan out to the sides
    at about 30–45° above horizontal, the inner ones stand upright, and every face is pale. Compare `z_ref_tufts.png`
    and `z_ours_tufts.png` in `...\scratchpad\v022\`.
  - **Ours:** T1 and T2 are compact balls. A front blade foreshortens toward the camera and leaves a grey-brown core
    (shade quartile #C99B5F against #D39E5D; hero fiber median #E6B877 against #F6C683, 16 low; the spec allows 10).
  - **From the side** (`side_sheet`), the crowns are thin spiky needle fans (pitfall 3), because the tufts are squashed
    to `TUFT_DEPTH` 0.72 and `FACE_TURN` 0.4 turns every blade face to the front.
  - **Fix in `TUFT_RINGS` / `tuft_mesh` / `TUFTS`:**
    - open the crown: outer ring 30–45° above horizontal, middle ring 50–60°, inner 75–85°;
    - use fewer, longer blades, for example (2, 3, 4) for T1 and T2 and (2, 2, 3) for T3, with blade length about the
      crown height;
    - make no blade lean toward −Y by more than about 30° from the tuft axis, so nothing points at the f34 camera;
    - raise `TUFT_DEPTH` to about 0.9–1.0 and lower `FACE_TURN` to about 0.2, so the crowns stay broad lances from the
      side and rear too.
  - **Acceptance:**
    - f34 fiber median within 10 of #F6C683, and the shade quartile at or above about #D09C5C;
    - f34 tuft components within ±0.06 of the study's §1.2;
    - `side_sheet` shows broad blades, not needles;
    - the part tuft's crown W : H is about 0.95–1.1, as in the close-up.
  - Keep the tris under budget, and keep the union clean: waist 0.12 into the collar, no coplanar faces.
- **B2. The fan's upper tier is too low and too narrow.**
  - **Upper side leaves (LA, LE):** the sheet's rise steeply to the top corners: tips at h .75 (f 0) and .69 (f 1) in
    the f34, .71 / .65 in the front cell. Ours point almost sideways: f 0–.15 at h .63–.65.
  - **The silhouette is narrow at two heights:**
    - h .7: width .57 against .82 (front .63 against .84);
    - h .3: width .72 against .92, where our pinch sits instead of at h .4.
  - **Fix in `LEAVES`:**
    - LA: elevation 34° → about 42°;
    - LE: elevation 32° → about 38°;
    - keep L, or lengthen by ≤ 0.1, so the X reach stays and W stays ≤ 4.95;
    - LB / LF: elevation 21 / 18° → about 25 / 22°, or W + 0.1, so their upper edge fills h .3.
  - **Acceptance (f34_sheet):**
    - top profile within ±0.07 at f 0–.2 and .8–1.0;
    - width per height within ±0.07 at h .3, .6 and .7.
- **B3. From the rear, the shrub is a green wall: stems and tufts are hidden.**
  - **Shares in rear_sheet** (sheet / ours): leaves .705 / .812, wood .173 / .110, fiber .122 / .079 (all over the
    spec's ±4); W : H 1.262 / 1.433.
  - **Sheet:** five stems fan visibly at h .1–.4 below a rounded centre leaf, and a tuft stands high on each shoulder.
    In ours, LG and the long low back diagonals LH / LI (L 2.45 / 2.4) cover the stems, and T1 shows only a tip behind
    LC / LA.
  - **Fix:**
    - shorten LH / LI to about 2.0–2.1 (the study's values) and lift their bases so they sit beside the stems, not in
      front of them, in the rear camera;
    - make LG rounder and a little smaller (L about 1.6), so S3 / S4 / SL / SR show under it;
    - B1's more open crowns, with T1 tilted less toward az 195 if needed, should bring T1 above LC's shoulder from the
      back.
  - **Acceptance (rear_sheet):** shares within ±4, two tufts visible (the small one at screen left), stems visible at
    h .1–.4.

**Minors** (fix if cheap; otherwise note them at commit):

- **m1. V notch.** f34 h .70 against the sheet's .54 (spec check .50–.60). The front cell matches (.70 / .69), so the
  sheet disagrees with itself. Spreading LC / LD by about 4° in azimuth would deepen it.
- **m2. Stems.**
  - S1 leans about 15° and S2 about 17° from vertical (spec 30° / 25°; sheet about 20°), so they read as near-parallel
    posts.
  - The foot pad and stubs make h .1 wider than the sheet (.75 against .58).
  - The collars read as ringed cups, a little heavier than the sheet's flare.
  - Leaning S1 / S2 out further from a narrower foot would match better.
- **m3. Wood hue.** About 4–5° redder than the sheet: key #73492D is 24°, the part renders 22° against 27°. Move
  `m022_wood` toward hue 27° (for example #74502F) and re-check the f34 stem median within 12 of #704D2F.
- **m4. Part leaf colour.** `FiberPlantLeaf` has no pure `leaf_base` faces (only 2 at 25 % mix). Its render is lighter
  and limier than the close-up (median #7AA238 against #5E893F; base +29 / +39). Give the part the hero's base band
  (shift −0.1) so its base reads dark and cool, near #3F613B.
- **m5. Side view.** The back half is low (top profile .47 against the sheet's .83–.88), and the view reads sparse and
  lopsided. The spec (§3.3) lets the front and rear govern, and B1 will improve the tufts here. Re-check the shares and
  counts after B1 and B3.
- **m6. top_tilt W : D.** 1.495 against 1.139 (spec 1.0–1.3); the plan ratio is 4.91 / 3.63 = 1.35. B2's steeper LA /
  LE will narrow it a little.
- **m7. Size near its limits** (W 4.91, H 3.45). Keep it in range after the fixes.
- **m8. Part tuft proportions.** The crown is taller and narrower than the close-up's (about 0.8 against 1.06 W : H).
  This is covered by B1.

**Passes:**
- topology, UVs, origin and transforms, and budget;
- nine thick, pointed lens leaves, with the hero leaf colour within 1 level;
- three tufts on brown collars;
- the open front with stem gaps;
- calm forage with no VFX;
- no colouring by facing;
- broad tint;
- base → tip gradients on leaves and blades;
- parts present with sensible shapes (fork Y plus side branch; leaf; tuft with peg).

## Round 2 fixes (modeller)

Fresh modeller, 2026-10-28. Background session on port 9882 with `wip/M022.blend` (saved after every good build).
Every change is in `m022.py`; `build()` runs in about 50–60 s with renders. Measured with `m022.measure()` (the study's
masks), plus scratch scripts in `...\scratchpad\r2_022\` (`tcomp.py` for tuft components, `parts.py` for part colours,
`chk.py` for the technical checks).

### What changed

- **B1, the tuft crowns** (`TUFT_RINGS`, `tuft_mesh`, `TUFTS`):
  - Rings at 75–85° / 50–60° / 30–45°, with fewer and longer blades: T1 and T2 (2, 3, 4), T3 (2, 2, 3). The blades
    are narrower lances (width 0.32 / 0.36 / 0.40 L).
  - Hero blades sit at set world azimuths (`WORLD_AZ`):
    - inner pair upright to the left and right;
    - middle ring to the front diagonals and the back;
    - outer ring straight out to both sides plus the back diagonals.
    - `FRONT_LEAN` 30°: any blade leaning toward −Y more than 30° from vertical is steepened in 3° steps.
    - The first try kept random azimuths with only the lean limit. It turned every front blade upright and read as a
      narrow bundle.
  - Each blade's width is rolled 70° (`BLADE_ROLL`) from tangential toward its radial plane. A blade splaying to either
    side of a view now shows its broad face instead of its edge. That edge was what made the round-1 crowns read as
    shadowed balls and needles.
  - `TUFT_DEPTH` 0.72 → 0.95; `FACE_TURN` 0.4 → 0.2.
  - T1 is now 1.5 × 1.45, tilted 14° toward az 205; T3 is 1.05 × 1.0 on S3, moved out to x 1.15.
  - **Part tuft** (`PART_TUFT`): 1.95 × 1.45 with 2 + 4 + 5 = 11 blades, as in the close-up. A part roll of 40° was
    tried: the blades read no broader and the base band went 16 dark, so `PART_ROLL` stays 70.
- **B2, the upper tier** (`LEAVES`):
  - LA el 43 (L 2.63, W 0.95, base on S1 at z 0.95, face (0, −0.8, 1));
  - LE el 35 (L 2.4, W 1.12);
  - LB / LF el 25 / 23, L 2.3, W 1.1, az 216 / 326, face (0, −1, 0.7).
  - LE stayed at 35° rather than 38°: at 37–38° both upper tips sat above h .7, and the f34 width at h .7 went to
    1.0 against the sheet's .82.
  - The low pair is longer than round 1. This keeps their upper edges at h .3 and the depth inside its tolerance.
- **B3, the rear:**
  - LG is rounder and smaller: 1.5 × 1.0, el 42.
  - LH / LI are L 2.15 and W 0.85, laid low and nearly flat (el 13, face mostly up), at az 112 / 68.
  - LC W is 0.84, and T1 sits on S1 at x −0.65, so T1 shows beside LC and above LA from the back.
  - LH / LI are 2.15 rather than the suggested 2.0–2.1, and point back rather than sideways. Shorter or more sideways
    leaves put the depth under 3.55. With LH / LI at az 135 / 45 and L 2.05, D was 2.96.
- **Minors:**
  - m2, stems: S1 and S2 lean about 26° and 33° from vertical (seen from the front 19° and 23°; round 1 was 15° and
    17°). The collars are less cup-like: `COLLAR` 0.32 / 1.4 / 0.08 → 0.30 / 1.3 / 0.06.
  - m3, wood hue: `m022_wood` is hue 27° and `m022_wood_dark` hue 26° (see the palette below).
  - m4, part leaf: `FiberPlantLeaf` is painted with shift −0.3. Its first two fifths are now the pure `leaf_base` key.
  - New shared check: `M.fix_bowties(o)` runs after `_polish` in `_make`. `nonmanifold_verts` is in the audit and in
    `problems`.

### Colour (two passes)

- **Pass 1** used the f34 / front medians, corrected in linear light:
  - leaves × (1.07, 1.04, 1.04);
  - fiber × (0.91, 0.92, 1.04): the open crowns read #FFCC7F, with red clipped;
  - wood moved to hue 27°, then × 1.08, so the part fork stays within 8 of #885E3D while the hero stems reach
    #704D2F. The full hero ratio (× 1.27) would have pushed the part fork about 20 too light.
- **Pass 2** re-measured every family within tolerance, so nothing more changed.

| Key | Round 1 | Round 2 |
| --- | --- | --- |
| m022_leaf | #608131 | #638332 |
| m022_leaf_tip | #83A32E | #87A62F |
| m022_leaf_base | #406234 | #426435 |
| m022_fiber | #E9BB7C | #E0B47E |
| m022_fiber_base | #D2A063 | #CA9A65 |
| m022_fiber_tip | #F1D5A3 | #E8CDA6 |
| m022_wood | #73492D | #785431 |
| m022_wood_dark | #553522 | #583B24 |

The blending is unchanged: position fields only, quarter steps, broad Tint. Facing correlation |r| ≤ 0.17 per family.

### Results against the round-1 targets (sheet / ours)

**B1, the crowns:**

| Check | Target | Sheet | Ours | Verdict |
| --- | --- | --- | --- | --- |
| f34 fiber median | within 10 | #F6C683 | #FEC685 (+8, 0, +2) | pass |
| f34 fiber shade | at or above #D09C5C | #D39E5D | #D6A46B | pass |
| f34 fiber share | ±4 | .192 | .204 | pass |
| T1 component | ±.06 | centre (.340, .538), f .21–.48, h .36–.75 | centre (.313, .541), f .16–.47, h .40–.76 | pass |
| T2 + T3 component | ±.06 | T2 f .52–.75, h .27–.60; T3 f .71–.84, h .53–.75 | f .51–.84, h .25–.82 | see note |
| Part tuft W : H | 0.95–1.1 | — | 1.91 / 1.91 = 1.00 | pass |
| Part tuft base → tip | within 15 per fifth | #CF9C63 #E0AD70 #F6C17E #FCD191 #FADFA6 | #D3995D #EDB77A #FFC883 #FFD191 #FFEAB3 | pass (≤ 13) |

- The T2 + T3 component merges into one, as in the sheet's own front cell. Its top is h .82, against T3's .75.
- **Side view:** the side_sheet crowns show more broad blade than in round 1, but the near-vertical blades still read
  spiky from +X. This is only partly fixed (below).

**B2, the f34 silhouette:**

| f | 0 | .05 | .10 | .15 | .20 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sheet top | .75 | .73 | .70 | .68 | .63 | .75 | .74 | .63 | .66 | .69 |
| Ours top | .73 | .71 | .68 | .65 | .63 | .79 | .66 | .67 | .68 | .68 |

- The worst miss is f .85 at −.08. Every other column is within .04.
- Width per height at h .3 / .6 / .7: ours .89 / .93 / .78; sheet .92 / .91 / .82. All within .04.
- f34 W : H 1.339 (sheet 1.369).
- Shares L / T / W: ours .627 / .204 / .170; sheet .638 / .192 / .170.

**B3, the rear (rear_sheet):**

- Shares L / T / W: ours .739 / .108 / .153; sheet .705 / .122 / .173. All within ±4 (+3.4 / −1.4 / −2.0).
- Two tuft groups show: T3 (with T2 behind it) at screen left, f .14–.43, and T1 at screen right, f .65–.82,
  h .46–.80.
- Stem runs (sheet / ours):
  - h .1: .30–.68 / .33–.41, .43–.62, .64–.72;
  - h .2: .31–.62 / .40–.65;
  - h .3: .33–.35, .58–.68 / .35–.40, .60–.67.
- The flat LH / LI show as a low leafy skirt at h .1–.2 that the sheet's rear doesn't draw.

**Other views** (sheet / ours):

| View | Leaves | Fiber | Wood | Other |
| --- | --- | --- | --- | --- |
| front | .639 / .618 | .200 / .206 | .161 / .176 | W : H 1.321 / 1.347 |
| side | .645 / .607 | .190 / .174 | .165 / .219 | leaves and wood about 5 out (m5) |
| r34 | .763 / .748 | .113 / .094 | .124 / .159 | |
| top_tilt | — | — | — | W : D 1.139 / 1.608 (m6, not fixed) |

- **Hero colour** (f34): leaves #6B8E2D / #6B8E2D; wood #704D2F / #6C4A2C.
- **Part fork:** #8C5F39 against #885E3D.
- **Part leaf**, base → tip fifths: #547E3D #537E3C #5B853B #679139 #789E34. The base is the cool `leaf_base` key
  (hue 99°), but it renders about 20 lighter than the close-up's #3E603A because the part shot lights the leaf face-up.

### Technical (all re-measured after the final build)

| Object | Tris | Size | Shells | Non-manifold edges / verts | Boundary | Inverted | Self-hits | Min angle | UV islands, overlaps, min gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FiberPlantNode | 1710 / 4000 | 4.89 × 3.64 × 3.48 | 1 | 0 / 0 | 0 | 0 | 0 | 5.06° | 356, 0, 0.016 |
| FiberPlantStemFork | 278 / 1000 | 2.37 × 0.86 × 3.09 | 1 | 0 / 0 | 0 | 0 | 0 | 9.34° | 33, 0, 0.016 |
| FiberPlantLeaf | 40 / 1000 | 2.03 × 0.89 × 0.99 | 1 | 0 / 0 | 0 | 0 | 0 | 9.95° | 3, 0, 0.016 |
| FiberPlantTuft | 376 / 1000 | 1.91 × 1.89 × 1.91 | 1 | 0 / 0 | 0 | 0 | 0 | 5.03° | 81, 0, 0.016 |

- **Size against the decision** (4.7 ± 0.25 × 3.9 ± 0.35 × 3.6 ± 0.2): W 4.89 ≤ 4.95, D 3.64 ≥ 3.55, H 3.48 ≥ 3.4.
- **Other checks:**
  - no wire or loose elements, no zero-area faces, no n-gons, no duplicate verts;
  - normals outward;
  - origin at the bottom centre; transforms applied; no modifiers;
  - UV density 1.0, stretch p95 ≤ 1.024;
  - `K.check` clean; `problems` empty; bowties fixed: 0.
- **Union inverted-face check:** the ray-parity check flagged one false positive on intermediate layouts. Along the
  normal the ray grazed an edge; 24 random rays said the face was outside. The final layout has 0.

### Left for the verifier / known misses

1. **Side view (m5).** It still reads sparse and lopsided from +X:
   - the back half is low (top profile .21–.31 at f .85–1.0, against the sheet's .49–.88);
   - the near-vertical crown blades look spiky there.
   - Turning the leaves' faces toward ±X (tried) didn't change the side shares, and it pushed the rear leaf share
     out of tolerance. Reverted.
2. **top_tilt W : D** is 1.61, against 1.14 (m6). The tall pair and the steeper upper tier read wide from 65°.
3. **The V notch** is h .73 in the f34, against .54 (m1). The front cell (.69) agrees with ours.
4. **The part leaf's base** is cool but lighter than the close-up (it is lit face-up).
5. **The flat back leaves LH / LI** show as a low skirt in the rear. They are needed for the decided depth.

## Stage 7 — Verification (round 2)

Independent verifier (not the round-1 verifier), 2026-10-28. Read-only background session on port 9882 with
`wip/M022_verify.blend`; not saved, `build()` not called, session stopped. Fresh renders by `m022.render_views()` with
`kit_models.MODEL_RENDERS` pointed at the scratchpad (`...\scratchpad\v2_022\renders\M022\`); the repo's render folder
is untouched. Measured with `m022.measure()` and my own scripts (`v2_022\tech.py`, `tech3.py`, `parts.py`, `crops.py`;
the side-by-side crops are `v2_022\cmp_*.png`).

**Verdict: FAIL, 7/10 (round 3 limited to four lines of `LEAVES`).** The front half now matches the sheet: open
flame crowns, the steep upper tier, and colours within a few levels. The back half still reads like a different plant.
From the side, r34 and rear, the leaves are edge-on blades that fan like grass (pitfalls 1 and 2), and the rear's
face-on centre leaf is missing. Both blockers are leaf-orientation numbers in `LEAVES`; nothing else needs touching.

### Technical (all re-measured; all pass)

| Object | Tris | Size (studs) | Shells | NM edges / bowtie verts | Boundary / wire / loose | n-gons / zero-area / dups | Self-hits | Inverted (ray parity) | Min angle | Volume |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FiberPlantNode | 1710 / 4000 | 4.889 × 3.636 × 3.485 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 | 5.06° | +2.77 |
| FiberPlantStemFork | 278 / 1000 | 2.369 × 0.860 × 3.088 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 | 9.34° | +1.29 |
| FiberPlantLeaf | 40 / 1000 | 2.031 × 0.893 × 0.988 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 | 9.95° | +0.20 |
| FiberPlantTuft | 376 / 1000 | 1.913 × 1.889 × 1.913 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 | 5.03° | +0.22 |

- **Size against the decision** (4.7 ± 0.25 × 3.9 ± 0.35 × 3.6 ± 0.2): W 4.889 ≤ 4.95, D 3.636 ≥ 3.55, H 3.485 ≥ 3.4. All
  are inside, and D and W are near their limits.
- **Origin and transforms:** the local bbox is symmetric in X and Y with min z 0.0000 on all four objects; rotation 0,
  scale 1. There are no modifiers, no children, no custom normals and 0 smooth faces (flat).
- **UV:** one `UVMap` each, in the range 0.008–0.992.
  - Islands 356 / 33 / 3 / 81; 0 overlaps; 0 flipped; min gap 0.016; density 1.0.
  - Conformal stretch p95 1.013 / 1.011 / 1.024 / 1.010; worst 1.081 (hero).
- **Materials:** the hero has 20 slots, all used. Roughness: leaf 0.8 (specular 0.06), fiber 0.85, wood 0.9. Metal 0,
  emission 0. `K.check` is empty. The KITSTAT lines are all `ok`.
- **Tint:** a corner layer. On the hero it runs 0.930–1.059 with sd 0.022; the within-face range p95 is 0.003, so the
  mottling is broad, with no confetti.
- **No colouring by facing:** the hero's key luminance against the face normal is |r| ≤ 0.17 for every family
  (leaf nz +0.12, fiber nz −0.17, wood nz −0.15).
  - The fork part shows wood nx −0.42. `paint_wood` uses only position noise (a `wood_dark` patch that happens to fall
    on one limb side), so this is not facing-based. It is noted only.
- **VFX / lighting:** none, as decided (decision 7).

### Round-1 blockers against their pass targets (sheet / ours, my measurements)

- **B1, the tuft crowns: PASS.**
  - f34 fiber median #F6C683 / #FEC685 (+8, 0, +2; target within 10).
  - Shade quartile #D39E5D / #D6A46B (target ≥ #D09C5C).
  - f34 fiber share .192 / .205.
  - Part tuft W : H .948 / .950 (target 0.95–1.1).
  - Part tuft base → tip fifths: sheet #D09D64 #E4B171 #F7C27F #FCD192 #FAE0A8; ours #D3995D #EDBA7A #FFC883
    #FFD697 #FFE3AC (≤ 9 per channel except the tip's blue at +4).
  - In `cmp_tufts_f34.png` the crowns are open flames of pale lances on collars, as on the sheet. They are a little
    sparser (T1 shows about 6 tips against 8–9).
  - The side crowns are still spiky (see S1).
- **B2, the upper tier: PASS.**
  - f34 top profile at f 0–.20: .73 .71 .68 .65 .63 against .75 .73 .70 .68 .63.
  - At f .80–1.0: .79 .71 .67 .68 .68 against .75 .74 .63 .66 .69. The worst miss is .04.
  - Width per height at h .3 / .6 / .7: .89 / .93 / .84 against .92 / .92 / .82.
  - W : H 1.339 / 1.369.
- **B3, the rear: numeric targets met, but it still reads unlike the sheet** (blocker S2).
  - Shares (sheet / ours): L .705 / .739 (+3.4), T .122 / .108, W .173 / .153.
  - Two tufts show, one on each shoulder.
  - Stems show at h .1–.4.

### View comparison (sheet / ours)

| View | W : H | Leaves | Fiber | Wood | Reads |
| --- | --- | --- | --- | --- | --- |
| f34_sheet | 1.369 / 1.339 | .638 / .626 | .192 / .205 | .170 / .168 | matches: fan, open front, stems with gaps, three tufts |
| front_sheet | 1.321 / 1.347 | .639 / .618 | .200 / .208 | .161 / .174 | matches |
| side_sheet | 1.016 / 1.046 | .645 / .606 | .190 / .174 | .165 / **.221** | **unlike**: grass-like blades fan to the back, and the back half is low |
| rear_sheet | 1.262 / **1.405** | .705 / .739 | .122 / .108 | .173 / .153 | **unlike**: an upside-down fan with a flat skirt; no face-on centre leaf |
| r34_sheet | 1.188 / **1.302** | .763 / .748 | .113 / .094 | .124 / .159 | **unlike**: sparse and lopsided; 1 clear tuft against 3; edge-on leaves |
| top_tilt | 1.139 / **1.608** | .778 / .704 | .170 / .149 | .052 / .147 | sparser than the sheet's 9-leaf star (sheet self-conflict §3.5; minor) |

- **Side top profile** (f 0 → 1). Sheet: .22 .48 .69 .67 .64 .73 .67 .66 .87 1.0 .95 .89 .82 .68 .75 .79 .83 .88 .53
  .51 .49. Ours: .23 .25 .48 .72 .66 .79 .63 .71 .78 .69 .92 1.0 .71 .59 .45 .48 .50 **.31 .31 .30 .21**.
- **Rear width per height** at h .1 / .2 / .3: sheet .38 / .90 / .89; ours .40 / **.53** / **.68**. The rear is
  narrow at the bottom and has no low tier.
- **Why**, from the leaf frames (|n · camera| for the broad face, from `LEAVES` through `leaf_frame`):
  - LH / LI (face mostly up, el 13): rear 0.09, r34 0.00–0.04, side 0.13–0.21. They are edge-on from every rear and
    side camera, so they read as the "skirt" and the side's grass blades.
  - LC / LD: side 0.02–0.06, edge-on from both sides, so they read as the side's thin tall blade.
  - LG's front-face normal is (−0.15, 0.67, **−0.73**). Its broad face points down and back, so from the rear it is a
    small, shadowed sliver rather than the sheet's big, bright, face-on centre leaf (f .33–.55, h .20–.61).

### Colour (Δ = ours − sheet, R/G/B levels)

| Region | Sheet | Ours | Δ |
| --- | --- | --- | --- |
| f34 leaves median / lit / shade | #6B8E2D / #96B93A / #3F5D25 | #6B8E2D / #8EB435 / #48631F | 0,0,0 / −8,−5,−5 / +9,+6,−6 |
| f34 leaf bands, ground → top | #53752A #719531 #5A7C2B #759A30 #8FB035 | #537A26 #63842B #6B8E2E #7CA12F #97B730 | 0,+5,−4 / −14,−17,−6 / +17,+18,+3 / +7,+7,−1 / +8,+7,−5 |
| f34 fiber median / lit / shade | #F6C683 / #FDE1AB / #D39E5D | #FEC685 / #FFE5A1 / #D6A46B | +8,0,+2 / +2,+4,−10 / +3,+6,+14 |
| f34 wood median / lit / shade | #704D2F / #966841 / #3D2C19 | #6C4A2C / #986A41 / #452E1B | −4,−3,−3 / +2,+2,0 / +8,+2,+2 |
| front leaves / fiber / wood | #688B2D / #F4C380 / #755132 | #6B8E2D / #FEC686 / #6C492B | +3,+3,0 / +10,+3,+6 / −9,−8,−7 |
| side leaves / fiber / wood | #6A8D2E / #F4C382 / #6E4C2F | #567526 / #F2C589 / #775436 | −20,−24,−8 / −2,+2,+7 / +9,+8,+7 |
| rear leaves / fiber / wood | #678A2E / #F4C381 / #6E4C2F | #547324 / #EAB97F / #6E4C2F | −19,−23,−10 / −10,−10,−2 / 0,0,0 |
| Part tuft median (close-up) | #EEBC7C | #FFCD8A | +17,+17,+14 (part shot lit brighter) |
| Part leaf base → tip fifths | #446841 #527A45 #5E8940 #719B3F #88AD35 | #537E3C #537E3C #5B853C #679139 #789E34 | +15,+22,−5 at the base; −16,−15,−1 at the tip |
| Part fork median | #865D3C (hue 27°) | #8C5F39 (hue 28°) | +6,+2,−3 |

- The front and f34 families are within 10 on every median.
- The side and rear leaves are about 20 dark. This is the studio fill on every model (M017's rule): reported, not
  fitted. The edge-on leaves make it worse, because their lit faces don't reach the camera.
- **Blending:** the leaves go cool-dark to lime along each leaf, and the blades orange-tan to cream. The stems are
  mottled with no hard patches. The blending is position-based, as the code shows.

### Deviations by the round-2 modeller

- **The tuft rebuild is accepted:** set world azimuths, `FRONT_LEAN` 30°, `BLADE_ROLL` 70°, `TUFT_DEPTH` 0.95,
  `FACE_TURN` 0.2. It met every B1 target.
- **LE el 35 instead of 38: accepted.** The measured h .7 width supports it.
- **LG 1.5 × 1.0 at el 42: rejected (S2).** At that elevation, with face (0, 1, 0.35), the broad face points down.
- **LH / LI laid flat (el 13, face up) to hold D: rejected (S1, S2).** It holds the depth but creates the skirt and the
  side's grass blades. Depth can be held with steeper, longer leaves instead (fix below).
- **Turning leaves toward ±X:** the modeller judged it by the side shares, which don't measure edge-on-ness. The
  check that matters is the broad-face dot product above.

### Findings

**Blockers** (round 3: edit `LEAVES` only; no tuft, stem, colour or union changes):

- **S1. Side and r34: the leaves read as edge-on grass blades, and the back half is low.**
  - **Fix:**
    - LH: `((-0.2, 0.4, 0.4), "S4", 125, 28, 2.6, 0.95, (-1, 0.4, 0.8), …)`.
    - LI: `((0.2, 0.4, 0.4), "S4", 55, 28, 2.6, 0.95, (1, 0.4, 0.8), …)`. This raises the broad-face dot for LH / LI
      to side about 0.55–0.68, r34 up to 0.80 and rear 0.61. Their tips land at about (∓1.5, 2.28, 1.6): y as now, so
      D stays about 3.6, and they give the side's back-half profile at h about .45.
    - LC face (0, −1, 0.25) → (−0.45, −1, 0.25); LD → (0.45, −1, 0.25). Side dot rises from 0.02–0.06 to 0.33; front
      dot 1.00 → 0.93, so the front barely changes.
  - **Acceptance:**
    - side_sheet top profile ≥ .40 at f .85–1.0;
    - no blade-thin leaf in side_sheet or r34_sheet;
    - r34 shows broad low back leaves.
- **S2. Rear: no face-on rounded centre leaf; the base is a flat skirt.**
  - **Fix:** LG `((0.05, 0.45, 0.75), "S4", 90, 75, 1.5, 1.05, (0, 1, 0), …)`. The face normal becomes (0, 0.97,
    −0.26): rear dot 0.91, r34 0.78. The tip is at z 2.2, so it spans h about .21–.63, as on the sheet (.20–.61). The
    skirt goes away with S1's LH / LI.
  - **Acceptance (rear_sheet):**
    - a bright face-on centre leaf at f about .33–.55;
    - width at h .3 ≥ .80;
    - shares within ±5 (L may rise);
    - two tufts and the stems at h .1–.4 still visible.
- **For both:**
  - re-run `measure()` and confirm that f34 / front are unchanged within ±.02 on shares and profile;
  - keep W ≤ 4.95, D ≥ 3.55 and H ≥ 3.4;
  - keep every union clean with 0 bowtie verts.
  - If D falls under 3.55, lengthen LH / LI by 0.1 rather than flattening them.

**Minors** (note at commit; don't block):

- **m1. V notch** f34 h .73 against .54. The sheet's front cell (.69) agrees with ours.
- **m2. Stems.**
  - The f34 width at h .1 is .70 against .58: the foot pad and the SL / SR stubs.
  - The stub ends show as flat sawn log ends from the rear34 and underside.
  - S4 reads as a dark, square-ended post between S1 and S2 (`cmp_stems_f34.png`).
- **m3. Crowns slightly sparse:** about 6 tips on T1 against 8–9. The shaded inner blades go brown-grey in the part
  shot (the part's wood share is .141 against .055, from dark blade backs). Small grainy speckle in the shaded blades
  is render noise, not the mesh.
- **m4. r34 tuft count** 1–2 against 3. LD / LE cover T2 / T3 from behind; S1 / S2 may partly help.
- **m5. top_tilt** W : D 1.61 against 1.14, and sparser than the 9-leaf star (§3.5 conflict). S1's steeper LH / LI
  help a little.
- **m6. Part leaf** base fifth #537E3C against #446841 (+15, +22): lit face-up, as the modeller noted.
- **m7. Part tuft** renders 17 lighter than the close-up (lighting of the part shot); the hero crowns are on target.
- **m8. Size** near the limits (W 4.889, D 3.636). Keep it in range after S1 / S2.

**Passes:**
- budget, topology, bowties, UVs, origin and transforms, and materials;
- no facing colour, and broad Tint;
- the hero / front silhouette, upper tier and open front;
- the open flame crowns on collars;
- the hero colour families within 10;
- the leaf and blade gradients;
- three parts (fork Y plus side branch, lens leaf, tuft with peg);
- no VFX, as decided.

## Main session after verification round 2 (2026-10-28)

Applied the verifier's S1/S2 LEAVES rows exactly (LC / LD faces (∓0.45, −1, 0.25); LG az 90 el 75 L 1.5 W 1.05 face (0, 1, 0); LH / LI az 125 / 55 el 28 L 2.6 W 0.95 faces (∓1, 0.4, 0.8)). The rebuild in the kit file gave a hero of 1708 tris, 4.889 × 3.574 × 3.485 (inside the decided limits), one shell, 0 non-manifold verts, `problems` empty. `measure()`: f34 and front unchanged (leaves #6B8E2D exact); side L/T/W .640/.159/.201 against .645/.190/.165; rear .799/.104/.097 against .705/.122/.173. The rear wood share fell because the face-on LG and the steeper back pair now hide the stems. Visually the side and rear read as broad leaves rather than grass, so this was committed with the rear shares recorded as a minor.
