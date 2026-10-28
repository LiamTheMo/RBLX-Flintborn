# 022 Fiber Shrub — spec

Reference: `art/blender/assets/references/022.png`. The sheet's own title is "FIBER SHRUB — SHRUB • RESOURCE • FOLIAGE",
"Individual Model Study", header "PAGE 19/132" (INDEX.md row 22 calls it "Flintborn Fiber Shrub Model Study"; the page
number on the sheet is not the index number). The image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m022.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`
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
