# 024 Thorn Shrub — spec

Reference: `art/blender/assets/references/024.png`. The sheet's own title is "THORN SHRUB", top right "FLINTBORN —
INDIVIDUAL MODEL STUDY, PAGE 20/132" (INDEX.md row 24 calls it "Flintborn Thorn Shrub Study"; the page number on the
sheet is not the index number). The image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m024.py` → `build()` (stages 1–6 done, see below). Procedure: `art/blender/kit/mcp/STAGES.md`
(one modeller does stages 1–6 in a background Blender; then a fresh verifier does stage 7).

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7).

Sheet text:
- **Views:** "Front Three-Quarter (Assembled)", "Rear Three-Quarter (Assembled)", Front, Side, Rear, Top.
- **Exploded Construction:** labels "Leaf Cluster (x3)", "Thorn (x5)", "Branch Core (x1)". The drawing itself shows
  **5 clusters** (two of them with a thorn plugged into their side) and **4 thorns** (2 loose, 2 in clusters), with
  dashed arrows from the clusters and thorns to the core's limb ends.
- **Key Parts (Individual):** "Leaf Cluster (x3)" (4 lobes, a dashed arrow down to a socket dot on the core's centre
  limb), "Branch Core (x1)" (a trident), "Thorn (x5)".
- **Construction Detail 01 — "Branch to Leaf Junction":** a limb's flat 7–8-sided end ("Joining Surface", socket dot)
  and a single lobe with a dot on its back.
- **Construction Detail 02 — "Thorn Attachment":** a thorn's flat base ("Thorn Base", socket dot) plugging into a limb
  end among lobes.
- **Construction Detail 03 — "Underside View":** the assembled shrub from below: the trunk's flat octagonal foot (dot)
  and limbs radiating under the clusters.
- **Material palette (model colors):** five unnamed swatches: light green, cool mid green, olive, brown, pale tan.
- **Modeling notes:** "Use chunky, low-poly, flat shaded geometry."; "Keep broad, clear silhouette with readable leaf
  clusters and thorns."; "Reuse modular parts: leaf cluster, branch core, thorn."; "Clean topology with simple, solid
  forms (no small noisy details)."; "Maintain consistent proportions across all views."
- **Game context:** `src` has no thorn node (`NodeCatalog.luau` lists `FiberPlant`, `HerbShrub`, `BerryBush`; the only
  "Thorn" is a party-member name in `HudLayout.json`). WorldModeling §11 lists "thorn shrub" with the berry bush, herb
  and fiber shrub ("open shrub, rosette, and fan recipes… thorns are modules"). The old R05 kit sheet has `ThornShrub`
  (9.76 W × 7.51 D × 7.36 H, 1072 tris, `harvest_hit` + `harvest_deplete`, 15 icosphere clumps, 6 cones) and owns the
  `ThornShrub*` names (§8). MODEL_PROGRESS row R05: "mostly-done — dense foliage, few limbs; long thin thorns";
  `CHECKLIST.md` scores it 6/10. V07 owns `ThornScrub*` (a different plant: sheet 131).

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is about
`#F2ECE6` (242, 236, 230); each view's paper is the median of its box's top and bottom 4 rows. The masks are `cls()`
in `m.py` (HSV; background = within 18 of the paper):
- **L, leaves:** sat ≥ 0.25, hue 60–170°, g > 40.
- **T, thorns:** hue 22–55°, sat 0.12–0.43, v ≥ 0.66. (Bark is sat 0.45–0.60; the thorns' deepest shaded flanks,
  sat 0.43–0.47 and v 0.6–0.75, fall into W: about 1–2 points of share. Where a thorn-only number is needed the
  scripts add `W & sat < 0.47 & v > 0.55` near the thorn.)
- **W, wood:** sat ≥ 0.30, hue < 45° or ≥ 340°, v < 0.88, not L or T. Also catches the pale-brown cut ends.
- **O, other:** ground shadow, grey gaps and edges; not counted in the shares.

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m024_study\`.
Run with the scratch venv `...\scratchpad\venv22\Scripts\python.exe` (Pillow + numpy).
- **Helpers:** `m.py` (masks, view boxes `V`, `stats`), `bb.json` (silhouette boxes), `crops.py`, `gridcrop.py`.
- **Measurements:** `measure.py` → `measure_out.txt` (bboxes, shares, top profiles, width per height, region extents);
  `comps.py` → `comps_out.txt` (thorn components per view); `wood.py` → `wood_out.txt` (wood runs per height);
  `lobe.py` + `hull.py` (outline profiles and corner polygons of the isolated lobe, cluster, core and thorns);
  `expl.py` (exploded part boxes).
- **Colour:** `probe.py` (swatches), `samp.py` → `samp_out.txt` (views, parts, close-ups, deciles), `grad.py` →
  `grad_out.txt` (leaf hue by light, height bands, hero thorn base → tip), `thorngrad.py` (part thorns base → tip).
- **Crops:** `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `key.png`, `cu1.png`,
  `cu2.png`, `cu3.png`, `pal.png`, `notes.png`; grids `g_*.png` (10 % grid on the silhouette bbox, red = centre lines);
  mask previews `cls_*.png`, `mask_*.png`.
- **Zooms:** `z_f34_top.png` (crown lobes), `z_f34_base.png` (trunk and limbs), `z_f34_right.png` (right lobes and
  TD), `z_expl_core.png`, `z_expl_left.png`, `z_key_cluster.png`.
- **To run the scripts on our renders,** point `R` (in `m.py`) at the render, set the view boxes `V`, and re-run
  `measure.py` (it rewrites `bb.json`), then `comps.py`, `wood.py`, `samp.py`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a world shrub of the forage family). Hero budget 4000 tris, each part under 1000.
  WorldModeling suggests 250–1,000 for a forage shrub; the plan in §4.3 lands at about 1900–2400 after the unions
  because of the ~30 faceted lobes. Don't thin the lobes to chase 1000.
- **Overall read (check this first).** A dense, round, spiky shrub, wider than tall (hero W : H 1.35):
  - **a thick warm-brown branch skeleton** — a flared octagonal foot that splits low (z ≈ 0.6–1.0) into kinked,
    angular limbs. From the front, two big limbs cross in front of the foliage: a left one in an S up to the upper left,
    and a right one that rises and then sweeps almost level to the right edge. **Wood is 26 % of the hero** — the
    skeleton is a headline feature, not hidden;
  - **about 30 faceted leaf lobes in 9 clusters** at the limb ends. Each lobe is a **pointed gem**: a 6-sided spindle
    with a real apex, its axis pointing out from the shrub's centre. Seen end-on it is a hexagon with a centre vertex;
    seen side-on it is a diamond with a 85–110° tip. The clusters are flattened fans of 3–5 lobes, and the whole
    crown reads as a **star of points**, not a cloud of balls;
  - **five pale cream thorns** — fat 5-sided pyramids about 1.7 long — plugged into limb ends and pointing outward on
    the four diagonals (front-left, front-right low, back-left high, back-right high) plus a small one low at the back.
  - Hero shares: leaves 61 %, thorns 13 %, wood 26 %.
- **Focal silhouettes, in order:**
  1. The scalloped crown of lobe points with the two big upper thorns breaking it (TA upper right, TB left).
  2. The thick brown trunk and its two crossing front limbs, framed by lobes.
  3. The low thorn TD jutting down-right at the front, and the lobe points all round the rim.
- **Target size: about 4.8 W × 4.0 D × 3.6 H studs** (H = 0.65 of the 5.5-stud character, the top of WorldModeling's
  0.25–0.65 C forage-shrub range; W : H 1.33 is inside its 0.9–1.6). Tolerances W ±0.3, D ±0.4, H ±0.2. Decision §8.1.
  - **How it was derived.** The sheet has no character. The forage family was fixed by M017 (`BerryBushNode`
    4.3 × 3.5 × 3.6) and M022 (`FiberPlantNode` 4.7 × 3.9 × 3.6); the same height keeps the thorn shrub one of that
    family. The hero (444 × 328 px) then gives **92 px per stud** both ways; the front cell (232 × 184) **51 px per
    stud**.
  - **Depth:** side cell D : H 0.989 → 3.56; top W : D 1.124 → 4.27 (the top is drawn from about 70°, §3.5). The
    thorn and lobe tips placed from all views (§2) give Y −1.8 … +2.05, so **4.0** (±0.4).
  - **Alternatives:** × 1.25 (6.0 × 5.0 × 4.5, 0.82 C: a bigger "hazard" shrub at chest height), or R05's scale
    (9.8 × 7.5 × 7.4, taller than the player).
  - Resulting part sizes: trunk foot Ø 1.05 → 0.85; limbs Ø 0.4–0.6; lobes girdle Ø 0.65–1.2, length 0.85–1.6; thorns
    L 1.7 × base Ø 0.95 (T5 0.75 × 0.45).
- **Build frame:** front −Y, +X right, ground z 0, origin = the foot's axis on the ground. Stage 2 re-centres to the
  bbox bottom centre.
- **Stud mappings used below:**
  - hero (f34) and front cell: X = (f − 0.50) × 4.8, screen up = z cos e + Y sin e with e ≈ 13° (so z ≈ h × 3.6 + 0.22 Y);
  - rear and r34: X = (0.50 − f) × 4.8 (screen right = −X);
  - side: Y = (f − 0.50) × 4.0, **screen right = +Y (the back)** for the kit side camera at az 90 (+X); the side cell
    agrees with this (§3.3);
  - top (image top = back): X = (f − 0.5) × 4.8, Y = (h − 0.5) × 4.27.

### 1.2 Measured views (`measure.py`, `comps.py`)

| View (box) | Silhouette bbox (px) | W : H | Leaves L | Thorns T | Wood W | Thorns visible |
| --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (15,62,510,404) | 45–488 × 70–397 (444 × 328) | 1.354 | 60.9 % | 12.9 % | 26.2 % | 4 (TA, TB, TC small, TD) |
| Rear three-quarter (515,62,1010,404) | 541–987 × 71–397 (447 × 327) | 1.367 | 61.7 % | 15.1 % | 23.2 % | 3 (TA left, TC right, TD low left) |
| Front (20,454,272,656) | 31–262 × 462–645 (232 × 184) | 1.261 | 61.0 % | 13.3 % | 25.7 % | 4 |
| Side (278,454,500,656) | 295–480 × 458–645 (186 × 188) | 0.989 (D : H) | 61.2 % | 14.6 % | 24.2 % | 4 (TB, TA, TD, T5) |
| Rear (506,454,758,656) | 520–743 × 463–645 (224 × 183) | 1.224 | 60.2 % | 11.3 % | 28.5 % | 3 (TA, TC, T5) |
| Top (764,454,1006,656) | 780–988 × 458–643 (209 × 186) | 1.124 (W : D) | 76.1 % | 17.4 % | 6.4 % | 4 (all four diagonals) |

- **Reading:** every elevation is 60–62 % leaves and 23–28 % wood. The skeleton shows as much from the back as from the
  front (rear 28.5 %). From above the leaves cover the wood (6 %) and the thorns stick out on four diagonals (17 %).
- The front cell is the same drawing as the hero at a lower elevation (thorn components within ±0.02, §1.3); its
  narrower W : H (1.26) is the drawing, not the model. **The hero governs.**
- **Verifier tolerance:** shares ±4 points (top ±6); profile values ±0.07 h; positions ±0.06 of W/H unless stated.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .24 | .59 | .67 | .65 | .75 | .71 | .76 | .91 | .88 | .90 | .98 | .95 | .88 | .91 | .84 | .81 | .85 | .88 | .92 | .53 | .39 |
| Front | .55 | .58 | .66 | .82 | .79 | .78 | .73 | .89 | .88 | .92 | 1.0 | .93 | .89 | .91 | .82 | .82 | .85 | .89 | .92 | .52 | .38 |
| Side | .46 | .51 | .78 | .75 | .72 | .70 | .82 | .81 | .91 | .99 | .95 | .89 | .81 | .85 | .90 | .94 | .72 | .74 | .62 | .59 | .32 |
| Rear | .50 | .85 | .83 | .80 | .77 | .73 | .91 | .89 | .87 | .94 | 1.0 | .94 | .88 | .91 | .87 | .78 | .81 | .84 | .86 | .64 | .61 |
| r34 | .39 | .53 | .67 | .89 | .85 | .81 | .76 | .91 | .88 | .94 | 1.0 | .93 | .91 | .94 | .83 | .81 | .85 | .89 | .75 | .62 | .37 |
| Top (h = back) | .55 | .60 | .81 | .79 | .77 | .78 | .90 | .89 | .89 | .96 | 1.0 | .95 | .88 | .89 | .90 | .80 | .81 | .83 | .65 | .60 | .56 |

- The crown is a **scalloped dome of points**: local peaks every 0.1–0.15 f (f34 .20/.35/.50/.65/.90), never a smooth
  arc. Between neighbouring peaks the profile dips 0.03–0.10 h (the V's between lobe tips). **Stage 1 must reproduce
  at least 5 distinct peaks across f .15–.95 in the f34_sheet render.**
- The f34 right peak at f .90 (h .92) is thorn TA; left shoulder f .10 (h .67) is TB's tip.

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .08@.48 .79@.16 .91@.00 .95@.01 .93@.06 .95@.04 .85@.06 .69@.17 .56@.32 .59@.33 .01@.51
front  .12@.44 .78@.16 .91@.00 .96@.02 .95@.03 .98@.01 .85@.07 .72@.14 .76@.13 .61@.31 .01@.50
side   .27@.38 .80@.11 .82@.08 .99@.01 .92@.02 .90@.05 .80@.13 .74@.11 .49@.28 .38@.39 .01@.46
rear   .19@.36 .65@.19 .83@.08 .99@.00 .93@.04 .96@.00 .88@.12 .78@.08 .84@.05 .40@.29 .02@.49
r34    .25@.38 .94@.03 .87@.07 .92@.04 .97@.01 .93@.02 .89@.08 .74@.16 .72@.14 .77@.11 .01@.49
```

So the body is a broad, almost straight-sided mass from h .2 to .6 (0.91–0.95 W), tapering above h .65 to the crown;
at the ground only the trunk foot touches (h 0: 0.08 W at f .48), and the lowest lobes start at h .05–.1 (the gap
under the low clusters shows paper at h 0–.05 except at the foot).

**Wood runs** (`wood.py`, W mask; f ranges, width as a fraction of W, × 4.8 for studs):

```
f34  h .02  .43-.60 (.16 = 0.77)                         the foot at the ground
     h .06  .42-.68 (.26 = 1.25)                         foot flare + a low spur to the right (R-low limb root)
     h .15  .42-.61 (.19 = 0.91)                         trunk
     h .25  .29-.64 (.35)                                trunk + the F-L limb leaving to the left
     h .35  .25-.36 (.11) .38-.43 (.04) .47-.53 (.07) .56-.64 (.08)   F-L limb | back limb | C limb | F-R limb
     h .45  .26-.35 (.09 = 0.43)  .56-.82 (.26)          F-L limb rising | F-R limb sweeping right
     h .50  .30-.36 (.07)  .61-.86 (.24)
     h .60  .29-.36 (.08)  .83-.89 (.06)                 F-L limb top (under TB/TC) | F-R limb end
rear h .25  .32-.71 (.39); h .40 .16-.25 (.09) .48-.67 (.19); h .50 .14-.24 (.10) .55-.79 (.24)   Y to TA (left) and TC (right)
side h .02  .41-.66 (.25 = 1.0 D); h .40 .23-.61 (the forward limb to TB); h .50 .35-.45
```

- The trunk is about 0.85 studs wide above the flare (0.16–0.19 W), the limbs 0.4–0.6 (0.08–0.12 W).
- **Stage 1 target:** f34_sheet wood runs at h .35 must split into 3–4 runs with paper or leaf gaps between, and the
  h .45–.50 band must show the left limb (≈ f .26–.36) and the long right limb (≈ f .56–.86) **as two separate
  runs**. These are the "crossing limbs" that make the hero.

**Thorn components** (`comps.py`; centre (f, h), extents, tip):

| View | Thorns |
| --- | --- |
| f34 | TA (.81,.77) f .68–.92 h .62–.93 tip (.92,.93), 4726 px; TB (.22,.55) f .10–.31 h .41–.67 tip (.10,.67), 3609 px; TC (.31,.68) f .27–.36 h .60–.79 tip (.27,.79), 1313 px (mostly hidden); TD (.88,.15) f .81–.96 h .05–.28 tip (.96,.05), 2573 px |
| front | TA f .68–.92 h .61–.93; TB f .09–.29 h .41–.66; TC f .13–.33 h .60–.82; TD f .78–.95 h .05–.28 |
| r34 | TA (screen left) f .11–.35 h .61–.93 tip (.11,.93); TC (right) f .64–.87 h .54–.90 tip (.87,.90); TD (low left) f .02–.23 h .09–.35 tip (.02,.09) |
| rear | TA f .04–.30 h .54–.86 tip (.04,.86); TC f .67–.90 h .58–.86 tip (.90,.86); T5 f .60–.71 h .25–.31 (small, pointing screen right = −X) |
| side | TB (screen left = front) f .09–.38 h .45–.79 tip (.09,.78); TA (right = back) f .65–.77 h .68–.95 tip (.77,.95); TD f .10–.19 h .05–.19 tip (.10,.05); T5 f .72–.81 h .12–.21 |
| top | NW f .09–.31 h .56–.81 (TC); NE f .65–.87 h .58–.83 (TA); SW f .13–.37 h .16–.45 (TB); SE f .66–.86 h .04–.30 (TD) |

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, governs; `g_f34.png`).** Like M020/M022's, it is **not** a three-quarter view: the
trunk foot stands at the centre (f .43–.60), the cell is the front cell's drawing, and the r34 is its true opposite
(§3.1). Camera on the front axis (az ≈ 0), e ≈ 13°.
- **Skeleton (`z_f34_base.png`):** a flared foot (h 0–.15) leaning slightly right above h .2. The **F-L limb** leaves
  the trunk at h .2–.3 going left, kinks up at f .27 h .35 and rises in two straight kinked segments to f .30–.36,
  h .6, where TB's base sits on its outer side and TC behind its end. The **F-R limb** rises from the trunk at f .56,
  h .35 to f .62 h .48, then runs almost level to the right (h .45–.55) and ends at f .87–.90, h .6–.65 with a flat
  end under lobes. Between them a thinner **C limb** goes up behind the front-centre lobe (f .47–.53 at h .35), and a
  darker **back limb** shows at f .38–.43. A low spur to the right at h .06–.15 (f .63–.68) is the R-low limb under
  TD's cluster. Every limb is 7–8-sided, made of straight segments with visible knuckles at the kinks.
- **Lobes (about 16 visible):** crown points at f .20, .35, .50 (the top, h 1.0), .65; a big lobe facing the camera at
  the front centre (f .36–.58, h .38–.68, apex at the lower centre); a big one facing the camera low right (f .67–.88,
  h .17–.45); big lobes pointing left at the left edge (f 0–.28, h .2–.6); lobes pointing right at the right edge
  (f .85–1.0, h .35–.65); small low lobes at the front (f .38 h .1; f .72 h .1; f .9 h .12).
- **Thorns:** TA (upper right, pointing up-right and away, base hidden behind the F-R limb at f .70 h .66), TB (left,
  pointing left and a little up and toward the camera, base on the F-L limb at f .31 h .50), TC (small, upper left
  behind TB), TD (low right, pointing down-right toward the camera, base in the low-right cluster at f .80 h .27).
- **Facets:** lobe facets 0.2–0.4 stud triangles, 5–6 meeting at each apex; bark facets irregular 0.2–0.5 stud
  triangles; thorn sides 1–2 planes per side; no noise anywhere.

**Front (`g_front.png`).** The same drawing at e ≈ 10°. Use it for the orthographic profiles; compare with an extra
`front_sheet (0, 10)`.

**Side (`g_side.png`; kit camera at +X, screen right = +Y, the back).** Narrower (D : H 0.99), and it **agrees with
the kit convention**: TB (the front-left thorn, on the far side) pokes out at screen left, pointing forward and up
(tip Y −1.6, z 2.8); TA at screen right high (tip Y +1.1, z 3.4); TD low at the front (screen left, tip Y −1.5, z 0.2);
T5 small low at the back (f .72–.81, h .12–.21 → Y +0.9…+1.2, z 0.4–0.75). The trunk foot is at f .41–.66 (centre
Y +0.13) and the trunk leans forward toward the top (h .40 run .23–.61 is the forward limb to TB). The crown lobe is
tall and narrow here (f .37–.53, h .55–1.0): the crown lobes are **elongated spindles** (L : D about 1.5).

**Rear (`g_rear.png`; screen right = −X).** A Y of two thick limbs: screen left (+X) rising to TA's base (f .28, h .62),
screen right (−X) sweeping up to TC's base (f .68, h .62). A crown of lobe points like the front's (top profile peaks
at f .05, .30, .50, .65, .90). T5 shows small at f .60–.71, h .25–.31 pointing to screen right (−X), low on the back of
the trunk. TD (front right) is hidden behind the lobes. Wood 28.5 %: the back limbs must be as visible as the front
ones.

**Rear three-quarter (`g_r34.png`).** The true rear at a slightly higher elevation (trunk foot centred at f .42–.62):
TA at screen left (+X) high, TC at screen right (−X) high, TD at the far low left (+X front, its tip just past the
silhouette), a Y skeleton like the rear's. Compare with an extra `r34_sheet (180, 15)`.

**Top (`g_top.png`; image top = back by kit convention).** A **star**: a big central crown lobe seen apex-on (a
hexagon with a centre vertex, f .33–.65, h .37–.72), a ring of about 14–16 lobes radiating round it with their points
outward, and the four big thorns on the diagonals: TC NW (tip X −1.97, Y +1.3), TA NE (tip X +1.8, Y +1.4), TB SW
(tip X −1.8, Y −1.4), TD SE (tip X +1.75, Y −1.9). Brown shows only between the inner lobes (6 %). Drawn from about
70° up (lobe sides and thorn bases show), so compare with the kit `top (0, 89)` by counts and with an extra
`top_tilt (0, 70)` by shares.

**Close-ups.**
- **Detail 01 (22,1095,356,1340):** a limb end: 7–8-sided section, a **flat joining surface** cut square to the limb
  (light-brown end face, a socket dot), and a single lobe (clipped by the panel edge at x 343, so its outline isn't a
  full measurement): 7 outline corners at 112–158°, H : W ≥ 1.10, a pointed bottom where it meets the limb.
- **Detail 02 (360,1095,690,1340):** the thorn: a straight 5-sided pyramid (3 faces visible), **flat pentagonal base**
  ("Thorn Base", socket dot), outline corners: tip 39°, base corners 106–148°, L : base Ø about 1.5–1.7. The width
  falls linearly from base to tip (0.75 → 0.56 → 0.40 → 0.22 → 0.05): no bulge, no curve.
- **Detail 03 (694,1095,1005,1340):** the underside: the trunk's flat octagonal foot with a dot, five limbs radiating
  under the clusters, thorn bases visible from below, lobes pointing outward and down round the rim.

### 1.4 Parts (Exploded Construction (15,700,760,1085), Key Parts (765,700,1010,1085))

Scale: the exploded and key parts are drawn at about the hero's scale (exploded clusters 150–173 px across ≈ hero
clusters 1.6–1.9 studs at 92 px/stud). Facet language for every part: broad flat-shaded facets, chunky, no noise.

#### Branch Core (exploded (315,878,498,1040), 184 × 163 px; key (784,841,905,954), 122 × 114 px; `z_expl_core.png`)

- **Exploded shape:** a faceted **8-sided trunk** with a flared foot (the foot about 1.15 × the trunk's Ø), splitting at
  about **0.45 of its height** into:
  - an **upper-left limb** at about 40° from vertical (the longest, ≈ 0.55 of the core's width);
  - an **upper-right limb** at about 25° from vertical, a little shorter;
  - a **short centre stub** between them (≈ 0.15 of the height) with a **pale cut top** (`#C9AF99`, §5.1);
  - a **low left limb**, nearly horizontal, from about 0.3 of the height.
  Every limb Ø ≈ 0.45–0.5 × the trunk's, 7–8-sided, **flat square-cut ends** (the joining surfaces) with a socket dot
  (notation).
- **Key-part shape:** a **trident**: trunk, a tall vertical centre limb (flat top with the socket dot), a left limb at
  45° (longer) and a right limb at 45° (shorter); no low limb. Width profile from the bottom (fraction of its width):
  .30 .48 .48 .52 .68 .80 .91 .65 .66 .24.
- **Size (exploded, recommended for the part):** about **1.85 W × 0.9 D × 1.65 H** (trunk Ø 0.85, limbs Ø 0.40–0.45).
- **In the hero** the skeleton is bigger and has more limbs (§2.1, §3.2); same sections, kinks, facets and keys.
- **Construction:** `_branch_core(limbs, foot_r, split_z, seed)` (M022's `_stem_fork` pattern):
  - trunk loft, 8 sides, rings at z −0.1, 0.12 (flare), 0.45, split_z, with ±6 % radius and ±8° twist jitter per ring;
  - each limb a polyline of 2–4 **straight** segments (the kinks are the vertices), 7 sides, tapering 10–15 % to the
    end, starting 0.25 inside the trunk on its axis, with a **flat end cap square to the last segment**; a small knuckle
    swell (+8 % radius) at each kink ring;
  - one exact union of the limbs into the trunk, floor-cut at z 0.
- **Triangles:** trunk 8 × 3 × 2 = 48; a 3-segment limb 7 × 3 × 2 + cap 5 ≈ 47 → part (4 limbs) ≈ 240, hero (8 limbs)
  ≈ 48 + 8 × 47 ≈ **430**.

#### Leaf Cluster ×5 in the exploded: (346,720,518,856) 173 × 137, (162,759,323,896) 162 × 138, (504,787,652,909) 149 × 123, (180,916,292,1024) 113 × 109, (530,927,653,1027) 124 × 101; key (782,728,894,823) 113 × 96

- **Shape (key part governs, `z_key_cluster.png`):** **4 lobes** spread in a **flattened fan** (a flat star): two big
  front lobes pointing up-left and up-right, a taller one at the back pointing up, a smaller one behind at the left.
  The fan is about 1.2 × as wide as tall (H/W 0.85) and about **0.55 × its width deep**. Its top line has 3 separate
  points (h .77 at f .2, .99 at f .6, .82 at f .8, with V's between at .72 and .81): **real points, not a rounded
  top.** Bottom: the lobes' lower apexes converge on one hub (the socket).
- **The lobe (the unit; detail 01, the key cluster, the hero crown):** a **6-sided pointed gem**:
  - bottom apex at t 0 (buried in the hub or neighbours);
  - ring A, 6 vertices, at t 0.28, radius 0.42 D;
  - girdle ring B, 6 vertices rotated 30°, at t 0.50, radius 0.50 D;
  - crown ring C, 6 vertices rotated 30° again, at t 0.74, radius 0.36 D;
  - top apex at t 1.0, offset ±0.06 D sideways by seed;
  - L = 1.15–1.3 D for ordinary lobes, 1.5 D for the crown spindles; radius jitter ±8 %, ring twist ±10°.
  - That gives a **profile apex angle of about 94–98°** for L 1.2–1.3 D and about 85° for the crown spindles
    (half-angle atan(0.36 / (0.26 L/D))), and a 6–8-corner outline, as on the sheet. **36 tris.** Use this, **not** an icosphere (R05's balls), not `K.leaf` or `NS["leaf"]`.
- **Size (hero governs):** lobe girdle Ø 0.65–1.2, length 0.85–1.6; cluster span 1.4–2.1.
- **Construction:** `_cluster(n, span, fan_deg, seed)`: n lobes (3–5) on a hub, their axes spread across `fan_deg`
  (100–150°) in the cluster's main plane, each tilted ±20° out of it, yawed ±12°, D and L ±12 % by seed; the lobes'
  bottom apexes and a hidden 6-sided hub cone (12 tris) overlap at the hub; pre-unite the lobes of each cluster
  (`union_loose` + one exact union). **About 4 × 36 + 12 ≈ 155 tris** for the part.
- **Thorn in a cluster:** the two low exploded clusters carry a thorn whose base sinks into the cluster's side. In the
  hero this is TD (low right) and TB (left); see §2.3.

#### Thorn ×4 in the exploded: loose (58,873,138,946) and (646,816,719,895), in clusters (128,945,203,1003) and (630,948,721,1013); key (812,976,882,1064)

- **Shape:** a straight **5-sided pyramid** with a **flat pentagonal base** (detail 02), slightly irregular (base
  radius ±6 %, tip offset ±0.04 L), no ring in between: width falls linearly to a sharp tip (outline tip angle 38–39°).
  L : base Ø **1.6–1.8** (key part 1.6, detail 02 about 1.5 seen at an angle, hero TA 1.8).
- **Size:** **L 1.7 (1.55 showing + 0.15 sunk), base Ø 0.95**; T5 L 0.75, Ø 0.45.
- **Construction:** `_thorn(L, d, seed)`: 5 base verts + tip + base cap → 5 + 3 = **8 tris** (or 6 sides, 10 tris, if
  5 reads too crude). Base flat; sink 0.15 into the limb end or cluster side; never coplanar with a limb's end cap.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, origin = foot axis). Azimuths from +X counter-clockwise (front =
270°, back = 90°); elevation = rise from horizontal.

### 2.1 Skeleton (`_branch_core` hero call)

| Limb | Polyline (from inside the trunk → kinks → end) | Ø start → end | Carries | Sheet evidence |
| --- | --- | --- | --- | --- |
| Foot / trunk | axis (0.05, 0.05), z −0.1 → 0.95; leaning 10° toward +X above z 0.7 | 1.05 at z 0 → 0.95 at 0.12 → 0.85 at 0.95 | everything | f34 h .02 run 0.77 visible, h .15 0.91; side h .02 1.0 |
| F-L (front left, S) | (−0.05, −0.15, 0.6) → (−0.8, −0.35, 1.0) → (−1.05, −0.35, 1.4) → (−0.9, −0.3, 1.85) → (−0.95, −0.25, 2.1) flat end | 0.6 → 0.45 | TB (side), K3 | f34 h .25–.30 band to f .25; h .35–.60 run f .25–.36 |
| F-R (front right, sweep) | (0.2, −0.15, 0.75) → (0.55, −0.45, 1.5) → (1.15, −0.45, 1.75) → (1.65, −0.3, 1.85) → (1.95, −0.15, 2.05) flat end | 0.6 → 0.42 | K5 (end), K2 (root) | f34 h .35 f .56–.64; h .45–.50 f .56–.86; end f .87–.90 h .6–.65 |
| C (centre) | (0.05, 0.0, 0.9) → (0.0, 0.05, 1.6) → (0.0, 0.2, 2.4) flat end | 0.45 → 0.38 | K1 (crown), K2 | f34 h .35 f .47–.53 |
| B-R (back right) | (0.2, 0.2, 0.85) → (0.7, 0.45, 1.6) → (1.0, 0.55, 2.15) flat end | 0.55 → 0.42 | TA, K9 | rear screen-left arm f .14–.24 h .35–.55 |
| B-L (back left) | (−0.15, 0.2, 0.85) → (−0.6, 0.45, 1.55) → (−0.95, 0.55, 2.05) flat end | 0.55 → 0.42 | TC, K8 | rear screen-right arm f .48–.79 h .3–.55; f34 back limb f .38–.43 |
| L-low | (−0.15, 0.0, 0.5) → (−0.8, −0.15, 0.7) → (−1.35, −0.3, 0.85) flat end | 0.5 → 0.42 | K4 | exploded low left limb; f34 h .25 band |
| R-low | (0.2, −0.15, 0.45) → (0.75, −0.45, 0.65) → (1.15, −0.7, 0.9) flat end | 0.5 → 0.42 | K6, TD | f34 h .06–.15 spur f .63–.68, .79–.81 |
| K7 boss | a short stub (0.1, 0.45, 0.9) → (0.15, 0.85, 1.25) | 0.5 → 0.45 | K7, T5 | rear lobes low centre |

- Kinks are real angles (15–40° between segments), with a knuckle ring; **never a smooth curve or a pipe**.
- **See-through and crossing:** from the front the F-L and F-R limbs must pass **in front of** the lobes (K2's front lobe
  sits between them, K3/K5 behind their ends); the gap between the F-L limb and the trunk at h .3–.45 shows a dark
  interior (back limb, shaded lobes), not paper.

### 2.2 Leaf clusters (9 copies of `_cluster`; ~30 lobes)

| Cluster | Hub (on) | Lobes: axis az / el, girdle Ø × L | Sheet evidence |
| --- | --- | --- | --- |
| K1 crown | (0.0, 0.2, 2.45), C end | 5: up 90° el, 0.85 × 1.3 (spindle; apex z ≈ 3.6); 170°/50°, 1.0 × 1.2; 15°/50°, 0.9 × 1.15; 95°/45°, 0.95 × 1.15; 250°/55°, 0.9 × 1.1 | f34 crown peaks f .35/.50/.65 (X −0.7, +0.0, +0.7); top centre lobe apex-on |
| K2 front centre | (−0.1, −0.55, 1.75), C front / F-R root | 2: 265°/−15°, 1.15 × 1.3 (faces the camera; apex at f .52 h .38); 290°/40°, 1.0 × 1.15 | f34 f .36–.58 h .38–.68; f .55–.70 h .58–.82 |
| K3 upper left | (−1.25, −0.15, 2.05), F-L end | 3: 185°/15°, 1.0 × 1.2 (apex X −2.4); 160°/50°, 0.75 × 0.95; 215°/−10°, 0.9 × 1.1 | f34 f .03–.25 h .45–.65; small f .19–.30 h .62–.75 |
| K4 low left | (−1.35, −0.35, 0.85), L-low end | 4: 190°/5°, 1.2 × 1.35 (apex X −2.4, z 0.9); 225°/−15°, 1.0 × 1.15; 150°/10°, 1.0 × 1.1; 260°/0°, 0.65 × 0.85 (the small front lobe at f .38 h .1) | f34 f 0–.28 h .2–.47; f .17–.33 h .05–.2 |
| K5 right | (1.9, −0.15, 1.95), F-R end | 3: 0°/15°, 1.0 × 1.2 (apex X +2.4); 25°/50°, 0.8 × 1.0; 335°/−20°, 0.9 × 1.1 | f34 f .85–1.0 h .35–.65 |
| K6 low right | (1.15, −0.75, 0.9), R-low end | 3: 300°/15°, 1.15 × 1.3 (faces the camera); 320°/−25°, 0.8 × 1.0; 350°/−10°, 0.8 × 1.0 | f34 f .67–.88 h .17–.45; f .63–.78 h .02–.17; f .85–.95 h .1–.2 |
| K7 back | (0.15, 0.95, 1.3), K7 boss | 4: 90°/10°, 1.1 × 1.3; 60°/30°, 1.0 × 1.15; 125°/25°, 1.0 × 1.15; 95°/−20°, 0.9 × 1.05 | rear low centre lobes; top N lobes |
| K8 back left | (−1.05, 0.65, 2.0), B-L end | 3: 135°/30°, 1.0 × 1.2; 170°/15°, 0.9 × 1.1; 110°/55°, 0.85 × 1.1 | rear right lobes f .7–1.0; top W/NW ring |
| K9 back right | (1.1, 0.65, 2.05), B-R end | 3: 45°/30°, 1.0 × 1.2; 10°/15°, 0.9 × 1.1; 75°/55°, 0.85 × 1.1 | rear left lobes f 0–.3; top E/NE ring |

- **Each cluster is a flattened fan:** its lobes' axes lie within ±20° of one plane through the hub that faces outward
  from the shrub centre, so seen from outside a cluster reads as a flat star of points.
- **Lobe axes point away from the shrub centre** (no lobe pointing inward). The lobe facing a camera reads as a hexagon
  with a centre apex vertex (f34 K2, K6; top K1).
- **Contact:** lobe bottom apexes sink 0.15–0.25 into the hub; hubs sink 0.15 into their limb end (the limb's flat end
  stays visible on the BranchCore part only). Lobes of neighbouring clusters may intersect, never with coplanar faces.
- **Ground:** the lowest lobe points (K4, K6, K7) stop at z 0.05–0.15; only the foot touches the ground.

### 2.3 Thorns (5 copies of `_thorn`)

| Thorn | Base (on) | Tip (expected) | L × base Ø | Sheet evidence |
| --- | --- | --- | --- | --- |
| TA back right, high | (0.95, 0.5, 2.2), B-R end | (1.95, 1.2, 3.35) | 1.7 × 0.95 | f34 tip f .92 h .93; side tip Y +1.1 z 3.4; rear/r34 screen left high; top NE |
| TB front left | (−1.0, −0.35, 1.85), F-L outer side + K3 | (−1.9, −1.5, 2.45) | 1.7 × 0.95 | f34 tip f .10 h .67; side tip Y −1.6 z 2.8 (screen left); top SW |
| TC back left, high | (−0.95, 0.5, 2.1), B-L end | (−1.95, 1.25, 3.1) | 1.7 × 0.95 | rear tip f .90 h .86; r34 tip f .87 h .90; top NW; f34 shows only its upper half behind TB (§3.4) |
| TD front right, low | (1.2, −0.85, 0.95), R-low end + K6 | (2.15, −1.6, 0.3) | 1.6 × 0.9 | f34 tip f .96 h .05; side tip Y −1.5 z 0.2; r34 low left; top SE |
| T5 back, small | (−0.35, 0.75, 0.95), K7 boss side | (−0.95, 1.2, 0.8) | 0.75 × 0.45 | rear f .60–.71 h .25–.31 pointing −X; side f .72–.81 h .12–.21 |

- **Expected hero:** X −2.4 … +2.4 (lobe points; thorn tips ±1.95–2.15), Y about −1.85 … +2.05, z 0 … 3.6 →
  **4.8 × 3.9 × 3.6**.
- **f34_sheet (0, 13) checks:** W : H 1.30–1.40 (sheet 1.354); shares ±4 of 60.9 / 12.9 / 26.2; top profile ±0.07 with
  ≥ 5 peaks; thorn components within ±0.06 of §1.2 (4 visible: TA, TB, TD whole, TC partly); wood runs per §1.2.
- **front_sheet (0, 10):** width per height ±0.07 (§1.2).
- **rear_sheet (180, 10):** shares ±4 of 60.2 / 11.3 / 28.5; the Y skeleton to TA (screen left) and TC (screen right);
  T5 visible low at the centre right.
- **side_sheet (90, 10):** D : H 0.95–1.15; TB at screen left, TA at screen right high, TD low left, T5 low right.

## 3. View conflicts and resolutions

### 3.1 The "front three-quarter" is an elevated front view, and the "rear three-quarter" its true opposite

- **Evidence.** The f34 and front cells place every thorn within ±0.02 (§1.2), the foot at f .42–.60, and lobes at the
  same fractions: one drawing, the hero from a little higher. The r34 has its foot centred (f .42–.62) and shows TA at
  screen left, TC at screen right and TD at the far low left, which is exactly the hero seen from behind (+X on screen
  left). It is not a mirrored copy.
- **Resolution.** Compare the hero with **`f34_sheet (0, 13)`**, the front cell with **`front_sheet (0, 10)`**, the
  r34 with **`r34_sheet (180, 15)`**. The kit `front34 (−28, 12)` and `rear34 (152, 12)` have no sheet counterpart:
  self-consistency only. The hero governs (WorldModeling §1.1).

### 3.2 Branch Core (exploded / key part) against the hero skeleton

- The exploded core has 4 limbs (upper left, upper right, centre stub, low left) on a 1.85 × 1.65 trunk; the key part is
  a trident. Every assembled view shows a **bigger skeleton with 8 limbs** (two crossing front limbs, two back limbs, a
  centre limb, two low limbs, the back boss), reaching 2.1–2.4 high.
- **Resolution** (M017/M022 pattern): one builder `_branch_core(limbs, …)`; the exported **`ThornBushBranchCore`** is
  the exploded call (4 limbs, pale cut top on the centre stub); the hero is the 8-limb call (§2.1). Same sections, kinks,
  facets, end caps and keys.

### 3.3 Side cell agrees with the kit side camera

- **Evidence.** With the kit side camera at az 90 (+X), screen right is the back (+Y). The side cell shows TB (front
  left) pointing to screen left, TA (back right) at screen right, TD (front low) at screen left low and T5 (back low) at
  screen right low, which matches the layout built from the hero, rear and top. **Not mirrored.**
- **Resolution.** Compare an extra **`side_sheet (90, 10)`** directly: D : H, shares ±5, the four thorns' sides.

### 3.4 TC: small in the hero, big from behind

- **Evidence.** TC is 1313 px in the f34 (only its upper half shows, f .27–.36, between TB and the crown lobes) but
  4000–6000 px from the rear and r34, where it is the nearest thorn. Its tip X disagrees: f34 −1.1, rear/top −1.95.
- **Resolution.** TC is a full-size thorn at the back left (§2.3); the rear, r34 and top govern its tip. In the f34
  render it may show more than the sheet's sliver: accept up to 2500 px-equivalent (about 4 % share) and record it.

### 3.5 Top view: tilted

- **Evidence.** Lobe sides and thorn bases show; W : D 1.124 against D : H 0.989 from the side. Drawn from about 70°.
- **Resolution.** Judge the top by: a central crown lobe seen apex-on; **14–18 lobes radiating round it, points out**;
  4 thorns on the diagonals (NW, NE, SW, SE); wood ≤ 10 %. Compare the kit `top (0, 89)` and an extra
  `top_tilt (0, 70)` (shares ±6).

### 3.6 Exploded and key-part counts against the hero

- **Clusters:** labelled "x3", drawn 5 in the exploded; the hero needs about 9 to cover the round crown and the back
  (decision §8.3). One `_cluster` builder; the exported part is the key part's 4-lobe fan.
- **Thorns:** labelled "x5", drawn 4; the assembled views show 4 big ones plus the small T5 at the back (rear, side):
  5 in total (decision §8.2).
- **Pegs, dots and sockets:** joinery notation; not modelled (decision §8.5).

### 3.7 Rear cell versus TD

- The rear cell doesn't show TD (the front-right low thorn); from behind it sits behind K6/K5's lobes. Not a conflict.
  Expect TD hidden or showing at most a tip at the far screen left in `rear_sheet`.

### 3.8 "Simple, solid forms" and flat swatches against the user's blended-colour rule

- The user's rule wins, and the sheet shows painted variation (§5.3): lobes differ from each other (yellow-green,
  cool green, olive), crown lobes are lighter than low/inner ones, thorns go cream toward the tip. Keep Tint low so the
  shrub still reads "solid".

### 3.9 Effects

- The sheet shows none (no glow, sparkle, falling leaves, dust). Stages 5/6 add nothing by default (§7).

## 4. Construction plan (modeller, stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `branch_core()` → `ThornBushBranchCore`: the exploded 4-limb call (≈ 1.85 × 0.9 × 1.65), flat 7-sided end caps, no
     holes. Compare with `z_expl_core.png`: split at 0.45 H, left limb 40°, right 25°, short centre stub, low left limb.
   - `leaf_cluster()` → `ThornBushLeafCluster`: the key part's 4-lobe fan (≈ 1.9 W × 1.6 H × 1.05 D). Compare with
     `z_key_cluster.png`: H/W 0.80–0.90; 3 separate points on the top line with V's ≥ 0.05 H deep; each lobe's
     profile apex 85–110°.
   - `thorn()` → `ThornBushThorn`: L 1.7, base Ø 0.95, 5 sides, flat base. Compare with the key thorn and detail 02:
     linear taper, tip angle 35–45° in outline.
   - Render a parts shot (`extra`, about (−20, 15)) laid out like the key-parts column.
2. **Hero:**
   1. `_branch_core` 8-limb call (§2.1); `_paste` (m011 pattern) 9 clusters (§2.2) and 5 thorns (§2.3).
   2. Pre-unite each cluster (lobes + hub). Then unite skeleton, clusters and thorns **one piece at a time**, saving the
      work file between risky steps; then `m004.floor_cut` at z 0.
   3. Origin at the bbox bottom centre; transforms applied. One closed shell (decision §8.6).
3. **Budget** (§4.3): hero about 1900–2400 (limit 4000), each part ≤ 250 (limit 1000). Spend spare tris on lobe count or
   an extra limb kink; never on smoothing.
4. **Placeholder keys** (stage 1): `m024_leaf`, `m024_thorn`, `m024_wood`. Stage 4 adds the rest (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** a round spiky crown of **pointed** faceted lobes, a thick brown skeleton with two crossing front
      limbs clearly in front of the leaves, four big cream thorns on the diagonals; nothing ball-like or cloud-like.
   2. **Lobe shape on the renders:** at least 10 lobes in the f34_sheet render show a clear apex (outline corner
      ≤ 110°) on the silhouette or against a neighbour; no lobe reads as a sphere (outline corners all ≥ 140°).
   3. **f34_sheet (0, 13):** §2.3's checks; wood 22–30 %; wood runs at h .35 and h .45–.50 per §1.2.
   4. **rear_sheet (180, 10):** shares ±4; the Y skeleton; TA left, TC right, T5 low.
   5. **side_sheet (90, 10)** and **r34_sheet (180, 15):** shares ±5 and thorn positions (§3.3, §3.1).
   6. **Top (0, 89) + top_tilt (0, 70):** star, 14–18 outer lobes pointing out, 4 diagonal thorns (§3.5).
   7. **Kit views** (front34, rear34, underside): self-consistency; the underside shows the octagonal foot and the
      limbs radiating (detail 03).
   8. **Parts against their cells** (§4.1).
   9. **Hero size** 4.8 × 4.0 × 3.6 (±0.3 / ±0.4 / ±0.2).
6. **Stage 2:**
   - zero non-manifold, boundary, wire and loose elements; no zero-area faces or n-gons; normals outward;
   - no faces under 5° where lobes, hubs, limb ends and thorn bases meet (m011 `_tidy` / `_desliver`);
   - don't decimate a lobe below its 3 rings + 2 apexes, a thorn below 5 sides, or a limb below 7 sides; keep the kinks.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Skeleton (trunk + 8 limbs + caps) | 1 | 430 | 430 |
| Lobes (6-sided gem) | 30 | 36 | 1080 |
| Cluster hubs | 9 | 12 | 110 |
| Thorns (5-sided) | 5 | 8 | 40 |
| **Sum before union** | | | **about 1660** |
| **Hero after union** (seams, slivers, floor cut) | | | **about 1900–2400** (limit 4000) |
| Parts: BranchCore / LeafCluster / Thorn | | | about 240 / 155 / 8 (limit 1000) |

## 5. Colour plan (modeller, stage 4)

### 5.1 Swatches (flat; medians of the inner box of each, y 1405–1440)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| 1 light green | (22,1397,72,1447) | `#799941` | 82°, 0.58, 0.60 |
| 2 cool green | (78,1397,127,1447) | `#597B44` | 97°, 0.45, 0.48 |
| 3 olive | (134,1397,183,1447) | `#637539` | 78°, 0.51, 0.46 |
| 4 brown | (189,1397,239,1447) | `#815C41` | 25°, 0.50, 0.51 |
| 5 pale tan | (245,1397,294,1447) | `#E3CBAE` | 33°, 0.23, 0.89 |

- The three greens are **three lobe colours**, not light and shade: the exploded and key lobes range from `#607D33` to
  `#688A3B` (hue 84–90), the hero median is olive (`#62772E`, hue 77), and the detail-01 lobe is cooler (`#587839`,
  hue 90).
- **Brown** matches the parts' bark (`#8B6143`–`#946747`) a little darker.
- **Pale tan** is paler and greyer than every rendered thorn (`#E7C09A`–`#F2CCA1`, sat 0.33): calibrate on the renders.

### 5.2 Rendered regions (`samp.py`, `grad.py`, `thorngrad.py`; median / lit quartile / shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Leaves, f34 / front / side | V | L | `#62772E` / `#62772F` / `#60762C` | `#97A944` / `#91A647` / `#91A33C` | `#3C4F21` / `#3C4E21` / `#39491F` |
| Leaves, rear / r34 / top | V | L | `#64782E` / `#5D712C` / `#63772C` | `#91A43F` / `#91A23E` / `#94A43C` | `#3C4D21` / `#374920` / `#3F5022` |
| Leaves, exploded (all) / key cluster | (15,700,760,1085) / (775,720,905,830) | L | `#607D33` / `#688A3B` | `#89A741` / `#8AA943` | `#40572A` / `#456033` |
| Leaves, detail 01 lobe / detail 02 / detail 03 | (200,1105,346,1255) / (370,1140,520,1335) / (700,1130,1000,1320) | L | `#587839` / `#638031` / `#60742C` | `#719549` / `#87A33F` / `#85993B` | `#3D542F` / `#394F24` / `#35461F` |
| Thorns, f34 / front / side / rear | V | T | `#E7C09A` / `#E9C69D` / `#E5C198` / `#EBC397` | `#FDE0B7` / `#FCE1BA` / `#FDE0B8` / `#FDE0B8` | `#C49F76` / `#C9A378` / `#BD9A74` / `#CAA579` |
| Thorns, r34 / top | V | T | `#E6BE94` / `#DDB78D` | `#FDDFB6` / `#FCDDB3` | `#CDA87C` / `#B99570` |
| Thorns, exploded / key / detail 02 | as §1.4 | T | `#EAC39B` / `#F2CCA1` / `#E7C094` | `#FDDFB6` / `#FDDCB5` / `#FEE1BC` | `#BF9B75` / `#E8C195` / `#CDA67E` |
| Wood, f34 / front / side / rear | V | W | `#7A5538` / `#7B573B` / `#7F5B3D` / `#765439` | `#A67753` / `#A57754` / `#9F724F` / `#9A704E` | `#392B1C` / `#3C2D1E` / `#513C27` / `#433221` |
| Wood, r34 | V | W | `#865E3F` | `#AA7A55` | `#463423` |
| Wood, exploded core / key core / detail 01 / detail 03 | (320,850,520,1060) / (770,830,920,958) / (30,1150,215,1335) / (700,1130,1000,1320) | W | `#8E6445` / `#8B6143` / `#946747` / `#865F40` | `#A57754` / `#A0724F` / `#A47654` / `#A77855` | `#61452F` / `#6B4D35` / `#684932` / `#5F452E` |
| Cut ends (centre stub top, joining surfaces) | key core / exploded core / detail 01 | pale T inside W | `#C2AFA0` / `#C9AF99` / `#C7AD97` | `#E5D3C4` / `#E6D3C1` / `#DFD0C0` | `#B58C6A` / `#B7906E` / `#B09988` |

**Gradients** (medians in five equal steps):

```
thorn base -> tip (isolated parts; tip is creamier, about 10-15 levels lighter and less saturated)
  key thorn   #EBC89E #F2CCA3 #F2D0AA #F2CEA7 #F3D2AF
  detail 02   #B18D6A #E8C095 #E7BF95 #E7C9A6 #F6D7B5     (first fifth = the shaded base face)
  expl TR     #EBC499 #EBC296 #ECC396 #EECAA2 #EECDA6
  expl L      #BB9872 #DFBC97 #E5C19A #E5C39F #E6C8A1
thorn base -> tip (hero)
  TA          #EDC79C #E9C397 #E3BF99 #EFCFA9 #EFD3B0
  TC          #BD9972 #D0AC85 #E2C29F #E7C8AD #E1CBAB
```

**Height bands** (f34 median per 0.1 h, h 0 → 1):

```
leaves  #4E5D24 #4A5C28 #5C6D2D #718635 #5C702D #798B33 #677D2E #5E7631 #89A03F #94A748
wood    #7D5739 #765237 #714E35 #684931 #7C5639 #9E704D #97774D #5A432B   -       -
```

**Leaf hue by light** (terciles of value): f34 dark 83° / mid 77° / lit 71°; exploded 91° / 86° / 79°. The shade is
cooler and the light yellower in every view: lighting does part of it, but the exploded lobes (no foliage shadow) are
**cooler overall** (hue 86) than the hero (77).

Deciles (dark → light), f34:

```
leaves #2E3C16 #415325 #4D5F2D #576924 #5E712F #687C31 #788A32 #859638 #8EA745 #A3B246
thorns #B99570 #CBA175 #D2A87B #D6AE84 #E3B98B #DCD29D #FADBB0 #FEDDB0 #FDE0B5 #F6E2CE
wood   #2A1E14 #412E1F #543B27 #654730 #755035 #7D583B #885E40 #956946 #A47451 #B4825C
```

### 5.3 How the colour works

**Leaves.**
- One green family with **per-lobe variation** between the three swatch greens: some lobes yellow-green (`#799941`),
  some cool (`#597B44`), some olive (`#637539`). On the hero the overall median lands olive (hue 77, sat 0.61).
- **Height and depth:** the crown lobes are the lightest (h .9–1.0 `#94A748`), the low and inner lobes the darkest and
  coolest (h 0–.2 `#4A5C28`–`#4E5D24`). That is partly the light, partly paint: paint the low/inner lobes toward the
  cool swatch and the crown lobes toward the light swatch; never paint by facing.
- **Within a lobe:** the apex region is the lightest on the unshadowed parts (key cluster lit `#8AA943`); a mild
  base → apex lift (base toward cool, apex toward light) makes the points read.

**Thorns.**
- Warm cream-tan: hue 30–33°, sat 0.29–0.36, v 0.88–0.95. Base → tip a subtle lift to cream (`#EBC89E` → `#F3D2AF`).
  The hero thorns are near the clip on their lit faces (`#FDE0B7`).

**Wood.**
- Warm mid brown, hue 25–27°, sat 0.51–0.54. The parts render `#8B6143`–`#946747`; the hero's median is darker
  (`#7A5538`) where clusters shade it, and the h .3 band under the clusters is the darkest (`#684931`), while the
  sweeping F-R limb's top is the lightest (h .5–.6 `#9E704D`). The foot is not darkened at the ground (h 0 `#7D5739`).
- **Cut ends** (flat joining surfaces): pale warm grey-tan `#C9AF99`, on the BranchCore part's limb ends and centre
  stub. In the hero the ends are under hubs; any visible end face (F-R end, R-low end) gets the same key.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered medians of **unshadowed** regions (exploded parts, key parts, close-ups), then
checked against the hero. `K.sample` kinds: `"green"` for leaves; `"brown"` for wood; `"all"` on tight boxes for the
thorn and cut keys (cream fails the brown filter's saturation test, as M020's cut wood did).

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m024_leaf` | `#647F36` (exploded `#607D33`, key `#688A3B`, detail 02 `#638031`) | default lobe colour, mid clusters | rough 0.8, `low_spec` |
| `m024_leaf_light` | `#7A9A40` (swatch 1 `#799941`; key lit `#8AA943`; hero top band `#89A03F`–`#94A748`) | crown lobes (K1) and every lobe's apex third | rough 0.8, `low_spec` |
| `m024_leaf_cool` | `#567640` (swatch 2 `#597B44`; detail 01 lobe `#587839`; exploded dark tercile hue 91) | low/inner lobes (K4, K6 lower, K7) and every lobe's base third | rough 0.8, `low_spec` |
| `m024_leaf_olive` | `#64763A` (swatch 3 `#637539`; hero median `#62772E`) | whole lobes, about 1 in 3 by seed (not K1's spindle) | rough 0.8, `low_spec` |
| `m024_thorn` | `#EAC39B` (exploded `#EAC39B`; detail 02 `#E7C094`; hero `#E7C09A`) | thorn middles | rough 0.7 |
| `m024_thorn_tip` | `#F3D4B0` (top fifths `#F3D2AF`, `#F6D7B5`, `#EECDA6`, `#EFD3B0`) | outer 35 % of each thorn | rough 0.7 |
| `m024_thorn_base` | `#E2BA90` (base fifths `#EBC89E`, `#EBC499`; between them and the shaded `#DFBC97`) | inner 25 %, base cap | rough 0.7 |
| `m024_wood` | `#8C6344` (exploded `#8E6445`, key `#8B6143`, detail 01 `#946747`; swatch `#815C41`) | skeleton | rough 0.9 |
| `m024_wood_dark` | `#654832` (parts shade quartiles `#61452F`–`#6B4D35`; hero h .3 band `#684931`) | crotches, the inner sides of limbs within 0.4 of a hub, the trunk between z 0.7 and 1.1 | rough 0.9 |
| `m024_wood_cut` | `#C9AF99` (exploded `#C9AF99`, detail 01 `#C7AD97`, key `#C2AFA0`) | flat limb-end caps and the centre stub top | rough 0.85 |

**Calibration warnings:**
- **Leaves:** greens calibrate darker than the painted sheet (kit memory); trust the render match. The f34_sheet leaf
  median must land within 12 of `#62772E` with hue 74–82° and sat ≥ 0.52; height bands with h .9–1.0 the lightest
  (≥ `#86A040`-ish, within 15 of `#94A748`) and h 0–.2 the darkest. Lobes must differ visibly from each other (at least
  3 distinct lobe medians across the hero, ≥ 10 levels apart).
- **Thorns:** near the clip in the hero. Check the f34_sheet thorn median within 10 of `#E7C09A` and that the base → tip
  lift is visible (≥ 8 levels). If the lit faces wash out to white, lower the specular, not the key.
- **Wood — keep it warm and visible:** the f34_sheet wood median within 12 of `#7A5538`, hue 23–30°, sat ≥ 0.48; never
  grey-brown or black. `wood_dark` only in crotches and under hubs; the long F-R and F-L limbs stay mostly `wood`.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Lobes** (field = each lobe's along-axis t from its construction frame, 0 = hub end, 1 = apex):
  - each lobe's base key by cluster: K1 `leaf_light`; K2, K3, K5, K8, K9 `leaf` (or `leaf_olive` by seed, 1 in 3);
    K4, K6, K7 `leaf_cool` for the lower lobes and `leaf` for the upper;
  - within the lobe: t < 0.35 → 50 % toward `leaf_cool`; t > 0.7 → 45 % toward `leaf_light`; 3 steps; ±0.08 noise on t;
  - hubs `leaf_cool`.
- **Thorns** (field = along-axis t from the base): t < 0.25 `thorn_base`; 0.25–0.65 `thorn`; > 0.65 `thorn_tip`;
  3 steps; base cap `thorn_base`. T5 (small, low, at the back) +0.1 toward the base.
- **Wood:** `wood` base; faces within 0.4 of a limb's root crotch or a hub, and the trunk faces between z 0.7 and 1.1,
  → 50 % `wood_dark` fading over 0.3; broad patches (`K.patches` scale 0.6, level 0.3) between `wood` and a 25 %
  `wood_dark` mix; flat end caps `wood_cut` (hard).
- **Hard edges only** where materials meet: lobe | limb end (hub), thorn base | limb or lobe, cut cap | bark.

### 5.6 Texture (Tint) and finish

- **Tint** (`tint_var` per piece about 0.04, so lobes and thorns differ slightly):
  - lobes: `K.texture` amp 0.035, scale 0.5 (broad, per facet group);
  - thorns: amp 0.02;
  - wood: amp 0.05, scale 0.35 (along-limb mottling);
  - never per-triangle confetti.
- **Finish:**

| Material | Roughness | Specular | Metal | Notes |
| --- | --- | --- | --- | --- |
| Leaf keys | 0.8 | `FOLIAGE_SPEC` (`low_spec=True`) | 0 | matte faceted foliage |
| Thorn keys | 0.7 | normal (lower if the lit faces clip) | 0 | smooth, dry, a touch of sheen on the sheet's lit faces |
| Wood keys | 0.9 | normal | 0 | matte bark |
| `wood_cut` | 0.85 | normal | 0 | matte end grain |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Leaves:** f34_sheet median within 12 of `#62772E`; height bands light at the top; ≥ 3 distinct lobe colours.
- **Thorns:** f34_sheet median within 10 of `#E7C09A`; parts-shot thorn base → tip within 12 per step of the key thorn
  row.
- **Wood:** parts-shot core median within 8 of `#8E6445`; f34_sheet wood within 12 of `#7A5538`, hue 23–30°.
- **Shares** per §2.3 and §4 step 5.

## 6. Joins and contact (no cracks or seams on this sheet)

- **Limbs into the trunk:** every limb starts 0.25 inside the trunk on its axis; one exact union; crotches clean V's
  (exploded core).
- **Clusters onto limb ends:** each hub sinks 0.15 into the limb's end cap; lobe bottom apexes sink into the hub; no
  visible pegs.
- **Thorns:** base sinks 0.15 into the limb end or the cluster side; the base face must not be coplanar with an end cap.
- **Ground:** floor-cut at z 0 (`m004.floor_cut`); only the foot makes the contact.
- Overlap everything; exact booleans (pitfall 10).

## 7. Lighting and VFX plan (modeller, stages 5 and 6)

**What the sheet shows:** an ordinary sunlit shrub. No glow, light, sparkle, falling leaves, dust or particles in any
view. The pale thorns are diffuse (shade quartile `#C49F76` is still tan), not emission.

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight:** nothing glows. Emission ≥ 1.0 would export as flat Neon and erase the thorns'
  base → tip lift.
- **Studio note (Requires Manual Validation):** check in Studio that the thorns don't clip to flat white under the game
  sun and that the lobes' per-lobe colour variation survives the palette export.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **Recommended: none.** The sheet shows no effect, `src` has no thorn node to harvest, and the other forage shrubs
  (M017, M018, M022) shipped none. Record "Stage 6 skipped: sheet shows no VFX".
- **Option** (decision §8.7): the R05 `ThornShrub` pair, if the main session wants hit feedback:
  - `harvest_hit` at the front, (0, −2.0, 1.8), colour override `["#62772E", "#EAC39B"]` (leaf and thorn chips),
    scale about 0.5;
  - `harvest_deplete` at the foot, (0, 0, 0.4), colours `["#62772E", "#8C6344"]`, scale about 0.3.
- **Not recommended:** `dust`, `ore_glint` (reads as magic), any light.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by `git grep` of the repo and a search of every sheet .blend, zstd-decompressed
(`m024_study/blendall.py`):
- **R05 kit:** `ThornShrub` (49 hits in `FlintbornWorldKit.blend`, 50 in `R05.blend`), `ThornShrubLeafCluster`,
  `ThornShrubThorn`, `ThornShrubBranch`, `ThornShrubThorns`, `ThornShrubDepleted`; keys `r05_thorn_leaf` (`#6F7F28`),
  `r05_thorn` (`#DDBE96`), `r05_bark` (`#7A5030`).
- **V07 kit:** `ThornScrub`, `ThornScrubBranchSegment`, `ThornScrubLeaf`, `ThornScrubLowSprawl` … (56 hits in the kit
  file); key `v07_thorn`.
- **`LeafCluster`** appears as a suffix in the kit, R05 and W06 files (`ThornShrubLeafCluster`, W06 `*LeafCluster`);
  only the full names matter.
- `M.mk` would silently rename a clash to `<name>M024`, so avoid all of these.

**Proposed names.** `ThornBushNode`, `ThornBushBranchCore`, `ThornBushLeafCluster`, `ThornBushThorn` and the `m024_`
prefix occur nowhere in the repo or any sheet .blend (`ThornBush` 0 hits).

| Object | Part | Why |
| --- | --- | --- |
| `ThornBushNode` | hero | `…Node` like `BerryBushNode` / `HerbShrubNode` / `FiberPlantNode`; R05 owns `ThornShrub*`, V07 `ThornScrub*` |
| `ThornBushBranchCore` | Branch Core (the exploded 4-limb core) | the sheet's word; R05 owns `ThornShrubBranch` |
| `ThornBushLeafCluster` | Leaf Cluster (the key part's 4-lobe fan) | R05 owns `ThornShrubLeafCluster` |
| `ThornBushThorn` | Thorn | R05 owns `ThornShrubThorn` |

- Fallback if the main session prefers the sheet's word: `ThornShrubNode` is free as an exact name, but the parts
  would then need another stem (R05 owns `ThornShrub*` parts), so `ThornBush*` keeps the set consistent.
- Palette keys `m024_*` (§5.4). Collection `Kit/M024 Thorn Shrub`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **4.8 × 4.0 × 3.6** (recommended: H 0.65 C like the berry bush and fiber shrub, the design doc's
   ceiling for a forage shrub), or × 1.25 (6.0 × 5.0 × 4.5, a chest-high hazard shrub), or R05's scale (9.8 × 7.5 × 7.4).
2. **Thorns:** **5** — TA, TB, TC, TD on the four diagonals plus the small T5 low at the back (recommended: matches
   "x5", the top's four diagonals, and the rear/side cells' low back thorn), or 4 (drop T5; the rear loses its small
   thorn).
3. **Clusters:** **9 clusters, about 30 lobes** (recommended: the hero's 16 visible lobes, the top's star of 15–17 and a
   back the rear cell fills), or 6 clusters / about 22 lobes (sparser back; the rear and top read thinner).
4. **Skeleton:** **one `_branch_core` builder; hero = foot + 8 limbs with the two crossing front limbs; exported part =
   the exploded 4-limb core** (recommended, M017/M022 pattern), or export the key part's trident instead.
5. **Pegs, dots and sockets:** **not modelled; flat end caps in `wood_cut`; no holes** (recommended: notation only;
   holes add boolean risk).
6. **Hero packaging:** **one closed shell** (recommended: STAGES default), clusters pre-united, pieces added one at a
   time.
7. **Stage 5/6:** **no emission, light or VFX** (recommended: the sheet shows none; matches M017/M018/M022), or the
   R05-style `harvest_hit` / `harvest_deplete` pair (§7.2).
8. **Exports:** the hero plus 3 parts (`…BranchCore`, `…LeafCluster`, `…Thorn`) (recommended). R05's `Thorns` drop and
   `Depleted` state are not on this sheet; not built unless asked.
9. **Comparison cameras** (§3): `f34_sheet (0, 13)` for the hero, `front_sheet (0, 10)`, `r34_sheet (180, 15)`,
   `rear_sheet (180, 10)`, `side_sheet (90, 10)` (not mirrored), kit top + `top_tilt (0, 70)`; kit front34, rear34 and
   underside as self-consistency; a parts shot `(−20, 15)`.
10. **Lobe recipe:** **the 6-sided pointed gem (3 rings + 2 apexes, 36 tris), axis pointing out from the shrub
    centre, crown lobes elongated to L 1.5 D** (recommended: the sheet's points and the verifier lessons), or an
    icosahedron (20 tris; reads as a ball — R05's failure).
11. **TC in the hero view** (§3.4): **full-size at the back left, rear/top govern** (recommended), accepting that it
    shows a little more in the f34 than the sheet's sliver.
12. **Names** as proposed.

## 9. Pitfalls to avoid

1. **Balls, blobs or clouds.** Every lobe is a pointed gem with a real apex (profile 85–110°) and straight outline
   edges; the crown is a scalloped dome of points with ≥ 5 peaks in the hero. No icospheres, no subdivision, no
   smoothing, no tents (a 2-ring cone) and no tulips (a cup with 3 points).
2. **Lobes pointing anywhere.** Each lobe's axis points out from the shrub's centre; each cluster is a flattened fan
   (a flat star). A lobe facing the camera shows its apex as a centre vertex.
3. **Hidden skeleton.** Wood is 26 % of the hero and 28 % of the rear. The two crossing front limbs pass in front of the
   lobes; the back Y shows from behind. R05's "few limbs" was a failure.
4. **Pipes and smooth curves.** Limbs are straight 7-sided segments with kinks and knuckles, tapering 10–15 %, flat
   square-cut ends.
5. **Thin or spiky thorns.** Thorns are fat (L : base Ø 1.6–1.8, base Ø 0.95), straight 5-sided pyramids. R05's other
   failure was "long thin thorns".
6. **Thorns on the wrong diagonals.** TA back right high, TB front left, TC back left high, TD front right low, T5
   small low back (§2.3). The side cell confirms the handedness (§3.3).
7. **Colour by facing.** Lit/shade differences on lobes are light; paint by cluster, height and along-axis t only;
   `K.check` facing correlation < 0.5.
8. **Flat one-colour foliage.** The sheet's lobes differ (three swatch greens) and the crown is lighter than the low
   lobes (§5.3).
9. **Cold or dark wood.** Keep the bark warm (hue 23–30°, sat ≥ 0.48); `wood_dark` only in crotches.
10. **Exact booleans.** Overlap everything: limbs from inside the trunk, hubs 0.15 into end caps, thorn bases 0.15 into
    limbs, no coplanar faces (thorn base vs end cap, lobe faces of neighbouring clusters). Pre-unite each cluster; add
    pieces one at a time and save the work file between; remove slivers with m011's `_tidy` / `_desliver`.
11. **Comparing the wrong views.** The hero is an elevated front view, the r34 a true rear view; the top is tilted;
    TC is mostly hidden in the hero (§3).
12. **Side-view handedness.** The kit side camera at az 90 sits at +X, so screen right is the model's back; the sheet's
    side cell already agrees (TB at screen left, TA at screen right).
13. **Naming clashes** with R05's `ThornShrub*` and V07's `ThornScrub*` (§8). Don't edit shared helpers
    (`kit_models.py`, `kit_mcp.py`, `build_kit.py`, `lib/vfx.py`); put new helpers in `m024.py`. No commits, pushes or
    exports in the modeller's stages.

## Decisions (main session, 2026-10-28)

All recommendations are accepted:
1. Size: 4.8 W × 4.0 D × 3.6 H (tolerances W ±0.3, D ±0.4, H ±0.2).
2. Five thorns, including the small T5 low at the back.
3. Nine clusters with about 30 lobes. Each cluster is a flattened fan with its lobe axes pointing out from the shrub centre, so the crown reads as a star of points.
4. One skeleton builder. The hero gets 8 limbs; the exported part is the exploded 4-limb core.
5. No pegs or sockets. Flat end caps take `wood_cut`.
6. One closed shell. Unite each cluster first, then add pieces one at a time.
7. No emission, light or VFX.
8. Hero plus 3 parts; no drop and no depleted state.
9. Comparison cameras: `f34_sheet (0,13)`, `front_sheet (0,10)`, `r34_sheet (180,15)`, `rear_sheet (180,10)`, `side_sheet (90,10)`, and the kit top plus `top_tilt (0,70)`.
10. Lobe recipe: the 6-sided pointed gem, not an icosphere. Lobes must read as angular points, never balls.
11. TC at full size at the back left; the rear and top views govern it.
12. Names: `ThornBushNode`, `ThornBushBranchCore`, `ThornBushLeafCluster`, `ThornBushThorn`.

The wood must stay warm and visible: the two crossing front limbs show as separate runs, as the study's targets require.

## Stage 1 — Modelling (modeller, 2026-10-28)

Builder `art/blender/kit/mcp/m024.py` (`build()` returns a dict with `problems`; empty on the final build, 60–85 s
with renders). Work file `art/blender/assets/kit/wip/M024.blend`, background Blender on port 9877.

**Parts, each from its own function:**
- `lobe_mesh`, the unit: a 6-sided pointed gem (bottom apex, ring A, girdle B rotated 30°, crown ring C rotated 30°
  again, top apex offset ±0.06 D), 36 tris. **Deviation from §1.4:** the spec's ring spacing (A .28/.42 D, B .50/.50 D,
  C .74/.36 D) rendered as icosphere balls from every side (rounds 1–2). The crown ring now hugs the girdle
  (`GEM`: A .22/.40, B .45/.50, C .57/.44), so the top half is a long straight 6-faced pyramid, the long point the
  sheet's lobes show (`z_f34_top.png`). The girdle is clamped to at most L / 1.15 (`LOBE_LD`), so every lobe shows a
  point side-on.
- `apex_lobes` / `CLUSTERS`: **each lobe is placed by its apex**, read off the f34 for the front half, the rear cell
  for the back and the top for the ring. It runs from 0.1 out of its cluster's hub to that apex. The spec's az/el
  table with every bottom apex on the hub (round 1) gave nine separate balls with paper between them. 11 clusters,
  30 lobes: K1 crown (spindle + 4), K2 front centre (2), K3 upper left (4), K4 low left (3), K5 right (3), K6 low right
  (3), K7 low back left (2), K8 back left (3), K9 back right (2), K10 low front (1, on the trunk), K11 rear centre (1,
  off the C limb), K12 low back right (1, on the extra `BK` limb).
- `_hub`: a hidden 6-sided frustum from the host limb's nearest axis point to the hub, run on 0.22 past it so each
  lobe's bottom apex sits inside it. A hub ending on a limb's end cap left coplanar faces that the union didn't join.
- `tube` / `skeleton`: an 8-sided flared foot (z −0.12 … 1.2) and 7-sided kinked limbs (straight segments, knuckle
  ring +8 %, ±6 % radius, ±8° twist, flat caps). Hero limbs FL, FR, C, BR, BL, LL, RL, K7, BK (9).
  **Changes from §2.1:** the two front limbs come forward (y −0.6 … −0.95) and are thicker (Ø 0.66 → 0.48), so they
  pass in front of the side clusters (the round 2 f34 wood share was 0.18). FR rises from the trunk and runs nearly
  level to the right under K5. BR swings out to X 1.55, then crooks in to TA (the rear cell's +X arm at f .14–.24).
  A low back limb BK was added (the rear cell's wood spans f .27–.66 at h .15).
- `thorn_mesh`: a straight 5-sided pyramid with a flat pentagonal base sunk 0.15 and three coplanar colour rings on
  the flanks (the outline is unchanged; the rings carry the base → tip blend), 38 tris. The hero thorns have base
  Ø 1.0–1.15 and L 1.5–1.75: the spec's 0.95 × 1.7 measured T 0.086 in the f34 against the sheet's 0.129, so the
  sheet's thorns are fatter than the spec states.
- Parts: `core_part` (the exploded 4-limb core: UL, UR, the CS stub with a pale cut top, LO), `cluster_part` (the key
  part's 4-lobe fan through `apex_lobes`), `thorn_part` (L 1.9, base 1.1, the hero thorns' size).

**Comparison cameras** (decision 9): `f34_sheet (0,13)`, `front_sheet (0,10)`, `rear_sheet (180,10)`,
`side_sheet (90,10)`, `r34_sheet (180,15)`, `top_tilt_sheet (0,70)`, each with a ×3 long lens; the kit views;
`exploded (−12,12)`; `part_* (−20,15)`. `m024.measure()` runs the study's masks on the sheet and the render;
`m024.compare()` writes `M024_sheet_compare.png`.

**Final measurements** (`measure()`, study masks; sheet → ours):

| View | W : H | Leaves | Thorns | Wood |
| --- | --- | --- | --- | --- |
| f34 | 1.338 → 1.298 | .609 → .620 | .129 → .142 | .262 → .238 |
| front | 1.259 → 1.321 | .610 → .619 | .133 → .133 | .257 → .248 |
| rear | 1.217 → 1.251 | .602 → .611 | .113 → .141 | .285 → .245 |
| r34 | 1.346 → 1.240 | .617 → .629 | .151 → .144 | .232 → .224 |
| side | 0.984 → 1.107 | .612 → .598 | .146 → .139 | .242 → .263 |
| top (tilt 70) | 1.101 → 1.220 | .762 → .738 | .174 → .186 | .064 → .076 |

- f34 wood runs: h .35 `.23–.37 | .49–.68` (the sheet has 3 runs); h .45 `.20–.33 | .53–.76`; h .50
  `.16–.25 | .60–.82`. **The two crossing front limbs show as separate runs** (sheet h .45 `.25–.35 | .56–.81`).
- f34 top profile `.34 .69 .83 .82 .81 .79 .82 .91 .91 .97 .97 .90 .95 .91 .86 .88 .91 .94 .65 .36 .36`: scalloped,
  with peaks at f .10, .35, .45–.50, .60 and .85. The strict counter finds 4 inside f .15–.95; the sheet has 5.
- Hero size **4.74 W × 3.78 D × 3.60 H** (target 4.8 × 4.0 × 3.6; all inside tolerance).

## Stage 2 — Optimisation and cleanup

- Guarded union (copied from M022, then extended): shells are united one at a time with exact booleans. A result is
  kept only if the volume test passes **and the result is still one shell**, because a touching, non-overlapping
  piece passed the volume test and stayed loose. A failing shell is retried nudged, then once more after all the
  others (K5's right lobe needed that). Then the floor cut, the guarded `_clean_mesh`, `_finish` and `_polish`
  (M022's), then `M.fix_bowties` (the main session's check; 0–1 bowtie per build at lobe hubs, split).
- Final audit of all four objects: 0 non-manifold edges, 0 boundary edges, **0 non-manifold (bowtie) verts**, 0 wire
  edges, 0 loose elements, 0 zero-area faces, 0 n-gons, 0 duplicate verts, 1 shell, normals outward, 0 inverted faces
  (ray parity), 0 crossing face pairs, origin at the bottom centre, transforms applied, no modifiers, smallest corner
  angle ≥ 5.1°.
- Tris: **ThornBushNode 2640** (budget 4000), ThornBushBranchCore 232, ThornBushLeafCluster 228, ThornBushThorn 38.

## Stage 3 — UV

Smart UV through `M.smart_uv` (ANGLE_BASED, angle 45, margin 0.008) and M012's overlap unfold. Hero: 743 islands,
0 overlap pairs, 0 flipped, min gap 0.016, density (1.0, 1.0, 1.019), conformal stretch p95 1.0. Parts: 46 / 58 / 6
islands, 0 overlaps, stretch p95 ≤ 1.003.

## Stage 4 — Materials, colour and texture

- **Keys:** `m024_leaf`, `_leaf_light`, `_leaf_cool`, `_leaf_olive`, `_thorn`, `_thorn_tip`, `_thorn_base`, `_wood`,
  `_wood_dark`, `_wood_cut`. Finish: leaves roughness 0.8 with `FOLIAGE_SPEC`; thorns 0.7; wood 0.9; cut ends 0.85;
  no metal.
- **Calibration pass 1** (`m024.calibrate()`, test dome, 6 iterations): every key within 6 of its §5.4 target.
- **Pass 2** (hero): with the dome hexes, the f34 / front / rear / r34 medians read leaves `#546F31`, thorns
  `#CAAF8E` and wood `#6B4D35`, because the lobes shade each other and the wood. Each family was corrected in linear
  light by the mean sheet / ours ratio over those views: leaves ×(1.60, 1.31, 0.92), then ×(0.94, 0.955, 1.0) on the
  residual; thorns ×(1.46, 1.39, 1.29); wood ×(1.59, 1.47, 1.30).
- **Final palette:** leaf `#667732`, leaf_light `#798E3A`, leaf_cool `#59713A`, leaf_olive `#667135`, thorn `#DAB995`,
  thorn_tip `#E2C9A9`, thorn_base `#D3B28B`, wood `#896141`, wood_dark `#64462D`, wood_cut `#C2A993`.
- **Re-measured (f34 medians, sheet → ours):** leaves `#62772E` → `#687B2F` (max channel difference 6), thorns
  `#E7C09A` → `#EEC496` (7), wood `#7A5538` → `#835A3B` (9; hue 25°, sat 0.55, warm). Front: `#68782E` / `#EDC395` /
  `#83593A`. Rear: `#5A6F2D` / `#E1BC92` / `#735036`. Leaf height bands in the f34 (h 0 → 1): `#5C712E #687E2F
  #546223 #6F7F31 #809335`; the crown is lightest, as on the sheet.
- **Blends** (by position only, never by facing; `K.check` is clean):
  - each lobe along its own axis t: below 0.30, 50 % toward cool; below 0.42, 25 % toward cool; the middle in its
    key; above 0.70, 25 % toward light; above 0.78, 50 % toward light (±0.08 broad noise);
  - lobe keys by cluster: K1's spindle light, the low clusters' downward lobes cool, every third lobe olive;
  - thorns base → 50 % → mid → 75 % tip by ring; the base cap `thorn_base`; T5 shifted 0.1 toward the base;
  - wood: `wood`, with 50 % / 25 % `wood_dark` within 0.55 / 0.85 of the crotch (0.12, 0.06, 1.0) and within
    0.3 / 0.55 of a hub, and broad noise patches whose edges ramp 25 % → 12 % → 6 %; flat caps `wood_cut` (hard edge);
    no darkening at the foot.
  - 22 keys are used on the hero.
- **Tint:** per-face broad noise (leaves amp 0.035 at scale 0.5, thorns 0.02, wood 0.05 at scale 0.35) times a
  per-piece ±4 %.

## Stage 5 — Lighting

Skipped by decision 7: the sheet shows an ordinary sunlit shrub, so there is no emissive key and no light.
Requires Manual Validation in Studio: check that the thorns' lit faces don't clip to white and that the per-lobe
colour variation survives the palette export.

## Stage 6 — VFX

Skipped by decision 7: the sheet shows no glow, sparkle, falling leaves or dust, so there is no socket. The renders
use `vfx=True`, with nothing to realise.

## Modeller's notes for the verifier

- Compare with the `*_sheet` renders (long lens), not the kit `front34` / `rear34`, which have no sheet counterpart
  (§3.1). `m024.measure()` and `m024.compare()` reproduce the numbers above.
- **The lobe recipe deviates from §1.4's ring spacing on purpose** (see Stage 1). It is still 6 sides, 3 rings and
  2 apexes, 36 tris, with the axis pointing out from the centre.
- **The thorns are bigger than §1.4** (base Ø 1.0–1.15) to reach the sheet's thorn share; the part matches the hero.
- **Lobes are placed by their apexes**, so the "clusters" are hubs on limb ends with 1–5 lobes radiating. The
  exported `ThornBushLeafCluster` is the key part's 4-lobe fan, built by the same function.
- Known leftovers:
  - the side view is wider than the sheet's (W : H 1.11 against 0.98): the spec's 4.0 depth and the side cell
    disagree, and D stays at 3.78, inside tolerance;
  - rear wood is 0.245 against 0.285 (−4 points, at the tolerance edge);
  - TC's tip shows higher in the f34 than the sheet's sliver (decision 11: the rear governs);
  - the strict peak counter finds 4 crown peaks inside f .15–.95 (5 with the f .10 shoulder);
  - the low lobes read darker than the sheet's (leaf_cool plus the studio's ground shadow);
  - the lobes overall read slightly smaller and more separate than the sheet's dense mass, with some dark interior
    gaps between them.

## Stage 7 — Verification (round 1)

Fresh verifier, read-only, background Blender on port 9877 with `wip/M024_verify.blend` (not saved; `build()` not
called). Fresh renders went to the scratchpad (`.../scratchpad/v024/renders/`), never to this folder. Extra renders:
the six `*_sheet` cameras again **with the studio floor hidden** (`renders/ns/`), so the ground shadow can't enter
the silhouette box; 960 × 800 versions (`renders/hi/`); a `(−90, 10)` side as a handedness check. Colours and
silhouettes are re-measured with the study's own masks on both images. The bounding box uses L/T/W pixels only.

**Verdict: FAIL, 5.5 / 10.** The technical side is clean. The hero and rear read as a low splayed "nest" of limbs,
not the sheet's trunk column and Y.

### Technical (all re-measured; all pass)

| Check | ThornBushNode | BranchCore | LeafCluster | Thorn |
| --- | --- | --- | --- | --- |
| Tris (budget) | 2640 (4000) | 232 (1000) | 228 (1000) | 38 (1000) |
| Size (studs) | 4.742 × 3.784 × 3.600 (target 4.8 ± 0.3 × 4.0 ± 0.4 × 3.6 ± 0.2: in) | 1.89 × 0.97 × 1.67 | 1.92 × 1.28 × 1.60 | 1.05 × 1.06 × 1.90 |
| Shells / non-manifold edges / bowtie verts / boundary / wire / loose / zero-area / dup | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 | same | same | same |
| N-gons / min corner angle | 0 / 5.10° | 0 / 6.35° | 0 / 5.17° | 0 / 16.6° |
| Normals; faces pointing inward (my own ray-parity test from every face) | outward; 0 | outward; 0 | outward; 0 | outward; 0 |
| Self-intersections (BVH overlap of non-adjacent faces) | 0 | 0 | 0 | 0 |
| Origin (bbox bottom centre); rot/scale; modifiers | exact; 0 / 1; none | exact | exact | exact |
| UV: islands / overlaps / flipped / min gap / density / stretch p95 | 743 / 0 / 0 / 0.016 / 1.0–1.019 / 1.00 | 46 / 0 / 0 / 0.016 / 1.0 / 1.003 | 58 / 0 / 0 / 0.016 / 1.0 / 1.002 | 6 / 0 / 0 / 0.016 / 1.0 / 1.0 |
| Materials | 22 used, 0 unused slots; no emission, no metal | 4 | 9 | 4 |

- **Colour by facing:** none. The correlation of key luminance with normal z is leaf 0.07, thorn 0.05, wood 0.10.
  `K.check` is clean.
- **Interior faces:** none. No face lies inside the volume and there is one shell.
- **Stage 5/6:** no emissive key, light or socket, as decided (decision 7). Correct.
- **Keys:** leaf `#667732`, light `#798E3A`, cool `#59713A`, olive `#667135`, thorn `#DAB995`, base `#D3B28B`,
  tip mix `#E0C5A4`, wood `#896141`, dark mixes `#805A3C` / `#765437`, cut `#C2A993`. Every key is multiplied by
  a Tint corner attribute.

### Views against the sheet (floor hidden, sheet → ours)

| View | W : H | Leaves | Thorns | Wood | Peaks |
| --- | --- | --- | --- | --- | --- |
| f34 | 1.356 → **1.226** (spec check 1.30–1.40) | .609 → .620 | .129 → .142 | .262 → .238 | 5 → 5 |
| front | 1.269 → 1.242 | .610 → .619 | .133 → .133 | .257 → .248 | 5 → 5 |
| rear | 1.232 → 1.313 | .602 → .614 | .113 → .141 | .285 → .244 | 4 → 4 |
| r34 | 1.365 → 1.282 | .617 → .632 | .151 → .144 | .232 → .224 | 5 → 4 |
| side | 0.995 → 0.997 | .612 → .598 | .146 → .139 | .242 → .262 | 4 → 3 |
| top (tilt 70) | 1.114 → 1.236 | .762 → .738 | .174 → .186 | .064 → .075 | 4 → 3 |

- `m024.measure()` reports W : H 1.298 (f34), 1.107 (side) and 1.251 (rear). These are inflated or distorted
  because `stats()` counts class O (the grey ground shadow) as object. With the floor hidden, the f34 is 1.23.
- Every view is within ±4 points on the shares except the rear wood, at −4.1.

### Items

**B1 — BLOCKER: the skeleton reads as a low, splayed nest, not a trunk column with crossing limbs (front) and a Y
(rear).**

What the sheet shows:
- **f34.** A thick trunk column stands fully visible at f .43–.60 from the ground to h .35. The F-L limb rises from
  it as a long S to TB's base. The F-R limb rises to h .48, then sweeps right.
- **Rear.** The same column splits at h .35–.4 into two thick arms at about 45° to TA's base (screen left) and TC's
  base (screen right).

What ours shows:
- **The split is too low.** All nine limbs leave the trunk at z 0.45–0.9, so the crotch sits at h ≈ .12–.2. Four of
  them (`LL`, `RL`, `K7`, `BK`) run nearly level at z 0.45–0.85.
- **`BR` swings out level** to X 1.55 before turning up.
- **The trunk foot is hidden in the f34.** The single `K10` lobe (apex (−0.7, −1.65, 0.15)) sits in front of it,
  leaving only a stub at f .47–.58, h 0–.12.
- **The F-L limb is a short stub** that disappears behind TB within about 0.8 studs.
- **The rear reads as a solid wood band.** At h .35 the wood is one run f .28–.78. The sheet has two runs there:
  f .26–.30 (left arm) and f .43–.62 (trunk), with leaves between. The low back limbs read as horizontal spokes
  at h .2–.3.
- **The sheet's three-quarter shape is lost.** Seen in `hi/f34_sheet.png` and `hi/rear_sheet.png`, it reads as a
  bowl of limbs with lobes sitting on its rim.

Fix (in `m024.py`, `TRUNK` / `LIMBS` / `CLUSTERS`):
1. **Trunk.** Make it a visible column. Keep radius about 0.45 up to z 1.0–1.15 (about h .3), then split. Raise every
   main limb's root: FL and FR to z 0.8–1.0; C, BR and BL to z 1.0–1.15.
2. **FL.** Make it a steep rising S, for example (−0.05, −0.25, 0.8) → (−0.55, −0.62, 1.25) → (−0.9, −0.68, 1.7) →
   (−0.95, −0.6, 2.05). Keep it forward of K3/K4's lobes so it shows from h .25 to h .6 (f .25–.36).
3. **FR.** Rise first, then go level, for example (0.15, −0.25, 0.95) → (0.55, −0.85, 1.55) → (1.15, −0.9, 1.75) →
   (1.8, −0.5, 2.05).
4. **BR / BL (the rear Y).** Run them straight at about 45° from z ≈ 1.1 to the TA / TC bases, for example
   BR (0.15, 0.25, 1.05) → (0.75, 0.62, 1.6) → (1.2, 0.85, 2.2) and BL mirrored to (−1.05, 0.8, 2.15). Drop BR's
   outward swing to X 1.55.
5. **Low limbs.** Shorten `LL` and `RL` to a single 0.5–0.6 stud segment rising at least 25°, tucked behind their
   lobes. Delete the `BK` and `K7` limbs, and hang `K12` / `K7` (and T5) from short hubs off BR / BL at z about
   1.0–1.2, or off the trunk's back face. No limb may show as a level spoke in the rear.
6. **Trunk foot.** Remove `K10`, or move its hub and apex to X ≤ −0.9 behind FL, so the foot shows.
7. **Acceptance** (floor hidden, study masks):
   - f34 wood at h .06 and h .15 is one trunk run at about f .42–.62;
   - f34 h .35 wood has 3–4 runs;
   - rear wood at h .35 has at least 2 runs, with the trunk at about f .43–.62, and h .45 has two arms (sheet
     .15–.25 | .49–.76);
   - rear wood share is at least .25;
   - the rear visibly reads as a Y.

**B2 — BLOCKER: the hero silhouette is too narrow. The f34 W : H is 1.226, against the spec's own 1.30–1.40 check
(sheet 1.356).**

The body is pinched at mid-height. The width per height at h .2/.3/.4 is .83/.86/.80, against the sheet's
.91/.95/.93. The right edge is TA's tip at the top (f .95, h .96), because the right-hand lobes stop short. The sheet's
right edge is lobes at h .35–.65, with TA's tip inside at f .92. The left shoulder is high (f .10–.15 at h .75–.81,
against .65–.67).

Fix:
- **Right side.** Push K5 / K6 lobe apexes out to X +2.35 … +2.45 at z 1.2–2.2. For example, K5's (2.3, 0.1, 1.3)
  goes to (2.45, −0.3, 1.5), and a K6 lobe goes to about (2.4, −0.6, 1.1).
- **Left side.** Add or extend left-edge lobes at z 0.8–2.0 to X −2.4.
- **Upper left.** Lower the K3 / TC lobes so nothing at X < −1.5 rises above z 2.7.
- **Acceptance.** f34 W : H 1.30–1.40 with the floor hidden; width at h .2–.5 at least .90.

**Minors** (fix if cheap; otherwise record them):
1. **TA points almost due east in plan** (13° off +X), not NE. Move the tip to about (2.05, 1.6, 3.35). TC is low
   and flat in the rear (h .47–.71, against .58–.86): raise its tip to z about 3.1, per §2.3. TB in the f34 is
   nearly level: tip h about .6, against the sheet's .67.
2. **Side view.** TD dominates (share .081 at h 0–.39, against .011 at h .04–.19) and TB is hidden behind the near
   lobes. A `(−90, 10)` render matches worse, so the side camera is right. TD's tip just points too much toward +X:
   (2.3, −1.75) could become about (2.0, −2.0).
3. **T5 is too prominent in the rear** (.017 against .004). Shrink it to L 0.6.
4. **Leaf colour:**
   - `leaf_olive` (`#667135`) is within 3 of `leaf` (`#667732`), so there are effectively only 3 lobe colours. Move
     olive toward swatch 3 `#637539` with lower value, or toward a distinct hue.
   - The crown is too dull and the base too light. Leaf height bands in the f34, bottom → top: sheet `#4B5C26` …
     `#88A040`, ours `#5C712F` … `#7F9335`. That is Δ (+17, +21, +9) at the bottom and (−9, −13, −11) at the top.
   - The lit quartile is `#97A945` → `#879A3B` (Δ −16, −15, −10).
   - The parts are yellower than the sheet's: key cluster `#688A3B` (hue 86°) → `#7B8D33` (73°); exploded
     `#607D33` → `#718330`.
   - From behind the leaves are dull: rear lit `#91A43F` → `#6E8133` (Δ −35, −35, −12). That is mostly the studio's
     back-lighting.
5. **Thorns wash out from above.** In the top view the median is `#DDB78D` → `#FFD9A5` (Δ +34, +34, +24). In the part
   shot it is `#F2CCA1` → `#FFE8AD`. In the f34, the shade quartile `#C49F76` → `#D9B080` is too light, so there is
   less contrast. The f34 median is fine: `#E7C09A` → `#EEC496`.
   - Fix: lower the thorn specular from 0.5 to about 0.25 and take about 6 levels off `thorn_tip`.
6. **Wood:**
   - Medians are good: f34 `#7A5538` → `#82593A` (+8, +4, +2); exploded `#8E6445` → `#906745`; key core `#8B6143` →
     `#926442`.
   - About 73 % of the wood faces are `wood_dark` mixes (dark-25: 322, dark-50: 113, plain: 162), against "dark only
     in crotches".
   - The side wood is dark: `#7F5B3D` → `#674830`.
   - The two upper f34 wood bands read grey-tan (`#8E6D50`, `#947D64`; the cut caps and thorn bases bleed in).
   - Cut key: `#C2A993` against `#C9AF99` (Δ −7, −6, −6). OK.
7. **The `ThornBushLeafCluster` part's lobes look like flat ivy leaves** with long sharp tips. The key part's lobes
   are fat, rounded faceted gems with short points. The hero lobes are closer to the sheet.
8. **The low lobes look like round balls** seen end-on (K4, K6, K7, K12, K10), and they sit apart, with dark gaps
   between neighbours. The sheet's mass is denser.
9. **Top view.** The plan is a rectangle with wood showing in a channel on the right (the FR limb). The sheet's is a
   round star with a big central apex-on lobe and a ring of 14–16 outward lobes. W : D is 1.236 against 1.114, and
   D 3.78 sits at the low end of its tolerance. B1 / B2 plus about 0.3 more depth should improve this.
10. **Thorn part** L : D is 1.8, against the key part's 1.6: it reads slimmer. Acceptable.
11. **`m024.measure()` lets the ground shadow into the silhouette box** (class O in `stats()`). Measure with
    `FB_Ground.hide_render = True` or with a box on L/T/W pixels only, or the side/rear/top W : H are wrong.

**Passed items:**
- every technical requirement;
- size;
- shares within ±4 in every view except the rear wood (−4.1);
- crown peaks: 5 in the f34 and front, like the sheet;
- the two front limbs show as separate runs at h .45 / .50 (f .20–.33 | .53–.76; .16–.25 | .60–.82);
- five thorns on the right diagonals (TA back right, TB front left, TC back left, TD front right low, T5 back low);
- pointed gem lobes on the crown;
- f34 colour medians (leaves Δ ≤ 7, thorns Δ ≤ 7, wood Δ ≤ 8);
- the exploded core part matches its cell well;
- no VFX, as decided.

## Round 2 fixes (modeller)

Fresh modeller, background Blender on port 9877 with `wip/M024.blend` (saved after every good build). Every number
below is `m024.measure()` on the final build (the bbox now uses L/T/W pixels only, see minor 11); the f34, front,
rear, side and r34 were also re-rendered with the floor hidden and gave the same W : H, shares and wood runs
(f34 1.367, rear 1.350). Build time with all renders: 55–62 s (hero only about 45 s).

### B1 — skeleton (fixed, one criterion partly)

- **Trunk:** an 8-sided column, radius 0.58 at the flare, 0.49 → 0.47 → 0.42 up to z 1.22, leaning slightly to +X.
- **Main limbs leave the column at z 0.8–1.05:** FL (root z 0.82) runs left, then steeply up and back in (the S) to
  TB's base; FR rises from z 0.95 to (0.55, −0.85, 1.55), then runs nearly level to (1.85, −0.6, 2.15) under K5;
  C goes up the middle to K1; BL runs straight at about 45° to TC's base at (−1.05, 0.85, 2.3); BR rises at 26° to
  (1.15, 0.6, 1.45), then at 56° to TA's base at (1.55, 0.9, 2.25). BR keeps one kink because the sheet's rear
  needs the +X arm at f .15–.25 at h .45 (a straight 45° arm sits at f .35). Both arms are thick (r 0.45 → 0.33).
- **Low limbs:** LL and RL are single segments rising about 28° (about 0.75 long, half inside the trunk). The `K7`
  and old `BK` spokes are gone. Two short **back root stubs** (`BK` to +X, `BKL` to −X, rising 28–30°) carry the
  low back clusters K12 and K7. Hubs off the trunk showed as bare green bars from behind, and the rear needs the
  sheet's low root wood (h .15 run .26–.65; ours .28–.66).
- **K10 removed**, so the trunk foot shows in the hero.
- **Lobes moved so the arms show:** K11 moved up (rear f .30–.45, above BR's first segment); K2 moved up; a small
  K2 lobe now sits between the front limbs, and a small K12 lobe in the rear crotch, as the sheet's leaf gaps.

| Criterion (floor hidden) | Sheet | Ours | |
| --- | --- | --- | --- |
| f34 wood h .06 / h .15 one trunk run about f .42–.62 | .42–.69 / .43–.62 | .40–.60 / .41–.63 (+ TD base sliver .80) | pass |
| f34 wood h .35: 3–4 runs | 4 | **2** (.23–.42 \| leaf gap \| .53–.74) | **partly** |
| f34 h .45 / .50: two separate limb runs | .26–.36 \| .56–.82 | .28–.36 \| .57–.83; .30–.35 \| .60–.88 | pass |
| rear h .35: ≥ 2 runs, trunk about .43–.62 | .22–.30 \| .43–.62 | .17–.29 \| .35–.67 | pass (trunk run wider: BR root) |
| rear h .45: two arms | .15–.25 \| .48–.76 | .14–.28 \| .45–.71 | pass |
| rear wood share ≥ .25 | .285 | **.255** | pass |
| rear reads as a Y | — | yes: column, two arms to TA and TC, C limb between | pass |

The h .35 front row stays at 2 runs: at z ≈ 1.3 the thick BL root sits right behind FL's kink, so the two merge on
screen, and the C limb merges with the FR root. Separating them would mean splitting lower, which the round-1 finding
ruled out.

### B2 — silhouette width (fixed)

- The edge lobes go out to X ±2.42: K4 (−2.42, −0.5, 0.8), K3 (−2.4, −0.4, 1.75), K6 (2.42, −0.7, 0.85),
  K5 (2.42, −0.15, 1.35) and (2.38, −0.25, 1.95). K12 and K7 reach X ±2.2–2.3 at the back.
- **TA's tip** came down from z 3.35 to 3.2: it was the f34's highest point (top 1.00 at f .90; it is now .98).
- The crown spindle is now z 3.5. TD's tip and K6's low lobe were lifted so the screen height doesn't sag below the
  foot.

| Criterion | Sheet | Ours |
| --- | --- | --- |
| f34 W : H (floor hidden; spec 1.30–1.40) | 1.356 | **1.367** |
| f34 width at h .2 / .3 / .4 (≥ .90) | .91 / .95 / .93 | **.94 / .91 / .93** |
| Size (W 4.8 ± 0.3, D 4.0 ± 0.4, H 3.6 ± 0.2) | — | **4.84 × 3.73 × 3.50** |
| Upper left: nothing at X < −1.5 above z 2.7 | — | partly: TB tip z 2.75, TC tip z 3.0 (see minor 1) |

The f34 left shoulder is still high (top at f .10 / .15 = .74 / .80 against .67 / .65). Lowering K3's lobes and
TB's tip did not move it, and it broke one union, so I reverted that.

### Minors

1. **Thorn directions (fixed, with one conflict).** TA's tip is (2.15, 1.7, 3.2), 49° from +X in plan (NE). TB's tip
   is (−2.15, −1.5, 2.75), raised. TC's base moved up the arm to z 2.3 and its tip to (−1.6, 1.75, 3.0), which is
   steeper (rise 0.7 over 1.0). The rear wants it higher still, but the f34 wants the upper left lower, so I left
   it between. TD's tip is (2.05, −1.95, 0.45), more toward the front.
2. **Side view:** TD is still the biggest thorn from the side. It sits on the camera side (+X), so it reads large.
   Side D : H is 1.09 (spec 0.95–1.15).
3. **T5 (fixed):** base Ø 0.4, length about 0.65, now on the trunk's back face at z 1.2 (rear f .55–.62,
   h .27).
4. **Leaf colour (mostly fixed):**
   - Olive `#5C6831` is now distinct from leaf `#647A36` by (8, 18, 5).
   - f34 leaf height bands, bottom → top: `#546A2C #576E31 #556727 #647730 #8EAC45`, against the sheet's
     `#4B5C26 … #88A040`. The crown is now the lightest (+6, +12, +5), and the base went from +17 too light to
     (+9, +14, +6).
   - The part lobes come from a 50 % leaf / cool mix: the key cluster renders `#6D8436` against `#688A3B` (max Δ 6;
     hue 78° against 86°), and the exploded leaves `#647A32` against `#607D33`.
5. **Thorns (partly fixed):**
   - `THORN_SPEC` is 0.25 on every thorn key, mix keys included, and the tip is 6 levels lower.
   - f34 thorn median `#E3BB94` against `#E7C09A` (Δ −4, −5, −6), and the exploded thorns `#F2C99D` against
     `#EAC39B`.
   - Still washed out from directly above: top median `#FAD0A3` against `#DDB78D`, and the single-thorn part shot
     `#FFE3AE` against `#F2CCA1`. That light comes from the sun's diffuse on up-facing faces, not from specular.
6. **Wood (fixed):**
   - Dark mixes are now 138 of 505 bark faces on the hero (27 %, was 73 %): crotch radius 0.35 / 0.55 around
     (0.12, −0.03, 1.12), hubs 0.22 / 0.38, and broad patches only above noise level 0.42.
   - f34 wood `#735034` against `#7A5538` (Δ −7, −5, −4; hue 25°).
   - The core part is rendered unshaded and read about 20 levels light, so it paints a 25 % dark mix as its base
     (50 % in the crotch): exploded `#976C4A` against `#8E6445`.
   - Side wood is still dark (`#63442D` against `#7F5B3D`), in the shade of the side lighting.
7. **Leaf cluster part (fixed):** the lobes are fat faceted gems (`GEM_FAT`: rings 0.2/0.42, 0.42/0.5, 0.64/0.42;
   L/D about 1.0–1.2; apex about 88°), size 1.98 × 1.35 × 1.6, 214 tris. Its paint uses only 25 % mixes at the hub
   end and the tip. The full ramp tripped the `K.check` facing correlation (0.59) on the upright fan; it now passes.
8. **Low lobes as balls:** not changed. The K4 and K6 front lobes still read rounded end-on.
9. **Top:** W : D 1.089 (sheet 1.114). The FR limb still shows as a channel from above; top wood is .111, against
   the sheet's .064 and the "≤ 10 %" target.
10. **Thorn part:** unchanged (L : D 1.8).
11. **`measure()` (fixed):** `stats()` builds the silhouette box and profiles from L/T/W pixels only, so the grey
    ground shadow (class O) no longer counts.

### Final views (sheet → ours, `measure()`)

| View | W : H | Leaves | Thorns | Wood | Medians L / T / W (ours) |
| --- | --- | --- | --- | --- | --- |
| f34 | 1.356 → 1.367 | .609 → .593 | .129 → .158 | .262 → .249 | `#607531` / `#E3BB94` / `#735034` |
| front | 1.269 → 1.370 | .610 → .588 | .133 → .156 | .257 → .256 | `#5F7330` / `#E2BA90` / `#6F4D32` |
| side | 0.995 → 1.089 | .612 → .655 | .146 → .159 | .242 → .185 | `#54692D` / `#CBAC8B` / `#63442D` |
| rear | 1.232 → 1.346 | .602 → .621 | .113 → .124 | .285 → .255 | `#546B2E` / `#CBA884` / `#805A3D` |
| r34 | 1.365 → 1.364 | .617 → .639 | .151 → .127 | .232 → .234 | `#566D2F` / `#CBA885` / `#815B3F` |
| top (tilt 70) | 1.114 → 1.089 | .762 → .700 | .174 → .189 | .064 → .111 | `#708838` / `#FAD0A3` / `#865D3F` |

- f34 leaf median `#607531`: hue 79°, sat 0.59.
- f34 crown peaks: 5.
- Out of the ±4 tolerance: side wood −5.7 and side leaves +4.3; rear W : H +0.11, from the wider low back lobes.

### Calibration (two passes) and final palette

- **Pass 1** (`m024.calibrate()`, test dome, olive target darkened to `#5A6A32`):
  - leaf `#546C35`, light `#647F3D`, cool `#4A673F`, olive `#4C5C31`;
  - thorn `#B9A187`, tip `#C3AD98`, base `#B39A7E`;
  - wood `#6F5138`, dark `#503A26`, cut `#9D8E83`.
- **Pass 2** (a hero build with the dome hexes; linear sheet / ours medians over f34, front, rear and r34):
  - leaves ×(1.65, 1.29, 0.82), applied at 0.6 hue strength, ×(1.50, 1.29, 0.98);
  - leaf_light ×(1.68, 1.45, 1.10), cool ×(1.35, 1.16, 0.89), for the height bands;
  - thorns ×(1.39, 1.33, 1.30), tip ×(1.32, 1.26, 1.23);
  - wood ×(1.60, 1.52, 1.40);
  - then leaf and light were nudged 3–4° cooler for the parts.
- **Final:**
  - leaf `#647A36`, leaf_light `#7C9C44`, leaf_cool `#4F6433`, leaf_olive `#5C6831`;
  - thorn `#D6B798`, thorn_tip `#DDC0A7`, thorn_base `#CFAF8E`;
  - wood `#8A6343`, wood_dark `#64482E`, wood_cut `#C2AC99`.

### Checks (final build)

| | ThornBushNode | BranchCore | LeafCluster | Thorn |
| --- | --- | --- | --- | --- |
| Tris (budget) | 2596 (4000) | 232 (1000) | 214 (1000) | 38 (1000) |
| Size | 4.84 × 3.73 × 3.50 | 1.89 × 0.97 × 1.67 | 1.98 × 1.35 × 1.60 | 1.05 × 1.06 × 1.90 |
| Shells / non-manifold edges / bowtie verts / boundary | 1 / 0 / 0 / 0 | same | same | same |
| Inverted faces / self-intersections | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Min corner | 5.10° | 6.35° | 5.13° | 16.57° |
| UV islands / overlaps / flipped / min gap | 709 / 0 / 0 / 0.016 | 46 / 0 / 0 / 0.016 | 58 / 0 / 0 / 0.016 | 6 / 0 / 0 / 0.016 |

`K.check` is clean, `problems` is empty, and no union left out a shell (hero 33 lobes, 11 clusters, 9 limbs and
stubs, 5 thorns). The guarded unions and `M.fix_bowties` are unchanged.

**Union fragility:** two intermediate layouts dropped one shell in the guarded union: a back stub starting near the
trunk surface, and a K3 lobe after its hub moved. Both were fixed by moving geometry, not by changing the union.
Any further layout edit must re-check `union_failed`.

## Stage 7 — Verification (round 2)

Fresh verifier (not the round-1 verifier; no other stage), read-only. Background Blender on **port 9883** with
`wip/M024_verify.blend`, not saved, `build()` not called. Port 9880 was already serving the M027 session (PID 114816),
so my first launch there could not bind. That orphan process (PID 112824, `M024_verify.blend --port 9880`) is still
running and idle, because I wasn't allowed to stop it; the main session should end it. My launch also truncated
`art/blender/logs/bgmcp-9880.log`. Fresh renders went to `.../scratchpad/v024r2/renders/M024/` via
`kit_models.MODEL_RENDERS`; nothing in this folder was overwritten. I used the builder's `measure()` (L/T/W bbox)
and `compare()` there, plus my own Pillow side-by-sides (`sbs_*.png`), a hole count (enclosed paper inside the
silhouette) and three elevated "game camera" shots (`hi/game_angles.png`).

**Verdict: PASS, 7 / 10.** Both round-1 blockers meet their criteria, apart from one sub-criterion that is only
partly met. The technical side is clean. The hero, front and rear-three-quarter views read as the sheet's shrub:
- a trunk column with two limbs in front;
- a Y from behind;
- pointed gem lobes;
- five fat cream thorns on the diagonals.

What remains is secondary-view and finish work, listed below as minors.

### Technical (my own code; all pass)

| Check | ThornBushNode | BranchCore | LeafCluster | Thorn |
| --- | --- | --- | --- | --- |
| Tris (budget) | 2596 (4000) | 232 (1000) | 214 (1000) | 38 (1000) |
| Size W × D × H (studs) | 4.840 × 3.729 × 3.500 (4.8 ± 0.3 × 4.0 ± 0.4 × 3.6 ± 0.2: all in) | 1.891 × 0.966 × 1.670 | 1.982 × 1.354 × 1.604 | 1.049 × 1.058 × 1.900 |
| Shells / non-manifold edges / bowtie verts (my fan walk and `M.audit`) / boundary / wire / loose | 1 / 0 / 0, 0 / 0 / 0 / 0 | same | same | same |
| N-gons / zero-area / duplicate verts / min corner | 0 / 0 / 0 / 5.10° | 0 / 0 / 0 / 6.35° | 0 / 0 / 0 / 5.13° | 0 / 0 / 0 / 16.57° |
| Signed volume; inverted faces (my ray parity); self-intersections (BVH, non-adjacent) | +13.71; 0; 0 | +0.82; 0; 0 | +1.50; 0; 0 | +0.47; 0; 0 |
| Origin: bbox centre xy / min z; rotation / scale; modifiers; parent | (0, 0) / 0.000; 0 / 1; none; none | same | same | same |
| UV: islands / overlaps / flipped / min gap / density / stretch p95 | 709 / 0 / 0 / 0.016 / 1.0–1.045 / 1.00 | 46 / 0 / 0 / 0.016 / 1.0 / 1.003 | 58 / 0 / 0 / 0.016 / 1.0 / 1.00 | 6 / 0 / 0 / 0.016 / 1.0 / 1.00 |
| Materials used | 24 slots, all used; no emission, no metal | 3 | 5 | 4 |

- **Tint attribute** present on all four.
- `K.check` is clean; `m024.inverted` and `_self_hits` are 0 everywhere; `_thin` has 0 faces under the limit.
- **Colour by facing:** none. The correlation of key luminance with normal z, excluding the `wood_cut` caps and the
  `thorn_base` region (genuinely separate materials), is:
  - hero: wood −0.09, leaf 0.07, thorn −0.02;
  - parts: core −0.19, cluster −0.03, thorn 0.00.

  Including the caps, the hero wood is 0.31, which comes only from the flat cut ends being `wood_cut`. That is
  correct.
- **Wood paint:** dark mixes are 138 of 505 bark faces (27 %), confirmed.
- **Leaf paint:** `leaf_cool` is the single biggest key (736 of about 1750 leaf faces) plus 54 % of the mixes. This is
  why the low lobes read dark (see minor 4).
- **Stages 5 / 6:** no emissive key, light or socket, as decision 7 says. Correct.

### Round-1 blockers against their criteria (`measure()`, L/T/W bbox; sheet → ours)

| Criterion | Sheet | Ours | |
| --- | --- | --- | --- |
| B1 f34 wood h .06 / h .15: one trunk run at about f .42–.62 | .42–.69 / .43–.62 | .40–.60 / .41–.63 (+ TD sliver .80) | pass |
| B1 f34 h .35: 3–4 runs | 4 | 2 (.23–.42 \| .53–.74) | partly (accepted; see below) |
| B1 f34 h .45 / .50: two separate limb runs | .26–.36 \| .56–.82 | .28–.36 \| .57–.83; .30–.35 \| .60–.88 | pass |
| B1 rear h .35: ≥ 2 runs, trunk about .43–.62 | .22–.30 \| .43–.62 | .17–.30 \| .34–.68 | pass (trunk run wider) |
| B1 rear h .45: two arms | .15–.25 \| .48–.76 | .14–.28 \| .45–.70 | pass |
| B1 rear wood share ≥ .25 | .285 | .255 | pass |
| B1 rear reads as a Y | — | yes in rear and r34: column, left arm to TA, right arm to TC, C limb between; the two low root stubs widen it into a short fan at h .15–.3 | pass |
| B1 trunk foot visible in the f34 (K10 removed) | — | yes, h 0–.15 at f .40–.63 | pass |
| B2 f34 W : H 1.30–1.40 | 1.356 | 1.367 | pass |
| B2 f34 width at h .2 / .3 / .4 / .5 (≥ .90) | .91 / .95 / .93 / .95 | .94 / .91 / .93 / .97 | pass |

**Side by side (f34, front).** The sheet's trunk leans right and runs on as the F-R limb up to TA's base, and the
F-L limb leaves low and goes left as an S to TB.

Ours has:
- a short column;
- FR rising, then running level to the right (thick, clearly warm);
- FL rising up-left to TB.

The crossing reads, but FL is a straighter, less prominent diagonal than the sheet's S. The h .35 row merges FL
with BL behind it. This is a fair outcome given the "split higher" constraint, not a blocker.

**Rear / r34.** Round 1 saw a "bowl of limbs". From the sheet's elevations it is now a column with two thick
45° arms to the two rear thorns, which reads as the sheet's Y. The wood is a broader wedge than the sheet's
separate sinuous limbs, because the low stubs fan out at h .15–.3, but that is a style difference, not a misread.

### Deviations (modeller's), judged

- **BK / BKL root stubs: accepted.** The sheet's rear has low root wood (h .15 run .26–.65; ours .28–.66). The stubs
  carry K12 / K7 instead of bare hub bars. They add to the fan look in the rear, but stay inside the sheet's own
  low-wood band.
- **BR's kink: accepted.** It puts the +X rear arm at f .14–.28 at h .45 (sheet .15–.25). A straight 45° arm would
  land at f .35.
- **TC compromise (tip z 3.0): accepted.** In the rear and r34, TC rises to about h .8 against TA's .85; the sheet has
  both at about .85. In the f34 it stays a modest upper-left spike, as on the sheet. Raising it further would
  re-raise the f34's high left shoulder.

### Views, all (sheet → ours)

| View | W : H | Leaves | Thorns | Wood | Peaks | Enclosed holes |
| --- | --- | --- | --- | --- | --- | --- |
| f34 | 1.356 → 1.367 | .609 → .593 | .129 → .158 | .262 → .249 | 5 → 5 | .0002 → .0021 |
| front | 1.269 → 1.370 | .610 → .588 | .133 → .156 | .257 → .256 | 5 → 5 | .0003 → .0016 |
| side | 0.995 → 1.089 | .612 → .656 | .146 → .158 | .242 → .186 | 4 → 4 | 0 → 0 |
| rear | 1.232 → 1.346 | .602 → .621 | .113 → .124 | .285 → .255 | 4 → 4 | 0 → 0 |
| r34 | 1.365 → 1.364 | .617 → .639 | .151 → .127 | .232 → .234 | 5 → 3 | .0004 → .0002 |
| top (tilt 70) | 1.114 → 1.089 | .762 → .699 | .174 → .190 | .064 → .111 | 4 → 6 | 0 → **.0216** |

### Colours (median / lit quartile / shade quartile; sheet → ours, Δ RGB)

| View | Leaves | Thorns | Wood |
| --- | --- | --- | --- |
| f34 med | `#62772E` → `#607531` (−2, −2, +3) | `#E7C09A` → `#E3BB94` (−4, −5, −6) | `#7A5538` → `#735034` (−7, −5, −4) |
| f34 lit | `#97A945` → `#87A341` (−16, −6, −4) | `#FDE0B7` → `#FFE9B6` (+2, +9, −1) | `#A67753` → `#AA7950` (+4, +2, −3) |
| f34 shade | `#3C4F20` → `#354319` (−7, −12, −7) | `#C49F76` → `#C19F7B` (−3, 0, +5) | `#392B1C` → `#503623` (+23, +11, +7) |
| front med | `#62772F` → `#5F7330` (−3, −4, +1) | `#E9C69D` → `#E2BA90` (−7, −12, −13) | `#7B573B` → `#6F4D32` (−12, −10, −9) |
| rear med | `#64782E` → `#546B2E` (−16, −13, 0) | `#EBC397` → `#CBA884` (−32, −27, −19) | `#765439` → `#805A3D` (+10, +6, +4) |
| r34 med | `#5D712C` → `#566D2F` (−7, −4, +3) | `#E6BE94` → `#CBA885` (−27, −22, −15) | `#865E3F` → `#815B3F` (−5, −3, 0) |
| side med | `#60762C` → `#55692D` (−11, −13, +1) | `#E5C198` → `#CBAC8B` (−26, −21, −13) | `#7F5B3D` → `#63442D` (−28, −23, −16) |
| top med | `#63772C` → `#708838` (+13, +17, +12) | `#DDB78D` → `#FBD0A3` (+30, +25, +22) | `#7A6041` → `#865E3F` (+12, −2, −2) |

- **The hero (f34 / front) medians are within 13 on every family.** The rear / r34 / side thorn and leaf deficits
  and the top's excess come from the studio's light direction on the same keys: the sheet lights every cell from
  the front. They are not a palette fault.
- **f34 leaf height bands, bottom → top:** sheet `#4B5C26 #66792E #637730 #617830 #88A040`, ours `#546A2C #576E31
  #556727 #647730 #8EAC45`. The crown is the lightest, as on the sheet. The middle bands are 10–15 levels dull.
- **Palette keys as stored:** leaf `#647A36`, light `#7C9C44`, cool `#4F6433`, olive `#5C6831`; thorn `#D6B798`,
  tip `#DDC0A7`, base `#CFAF8E`; wood `#8A6343`, dark `#64482E`, cut `#C2AC99`.

### Items (none is a blocker)

1. **Minor — the top view reads as a ring, not the sheet's dense star.**
   - From the 70° top and from about 45° in front (`hi/game_angles.png`), you can see the brown limb interior and
     the ground through gaps between the crown and the outer ring. Enclosed holes are .022 against 0, and top wood
     is .111 against .064 (the target is ≤ .10).
   - The FR limb shows as a channel on the right.
   - This is the leftover of round 1's "bowl". It no longer shows at the sheet's 10–15° views.
   - Cheap fix, if the main session wants it before commit: add 2–3 upward lobes (36 tris each, about 1400 tris of
     headroom) between the crown and the ring:
     - one on FR's level run at about (1.0, −0.75, 2.2), pointing up and out;
     - one over the FL / BL crotch at about (−0.7, −0.2, 2.3);
     - one behind K1 at about (0.3, 0.6, 2.6).
   - Re-check `union_failed` and the f34 wood runs afterwards.
2. **Minor — the upper silhouette is boxier than the sheet's dome.**
   - f34 width at h .7 / .8 / .9 is .88 / .74 / .71, against .69 / .56 / .59.
   - The top profile is flat at .86–.97 across f .2–.9; the sheet peaks at the crown, at f .45–.5.
   - The left shoulder is high at f .15–.25 (.74–.93 against .65–.75), as round 2 already noted.
   - Leave it unless item 1's lobes are added; if they are, keep them inside z 2.6 at |X| > 1.2.
3. **Minor — the side view.**
   - W : H is 1.089 against 0.995. The width is pinched at h .4–.5 (.70–.72 against .92–.90).
   - TD reads as the big low-left spike, whereas the sheet's big spike is upper left.
   - Wood is .186 against .242 (−5.6) and leaves .656 against .612 (+4.4).
   - This was a known round-1 minor. Record it.
4. **Minor — the low lobes read dark and somewhat ball-like and separate.** `leaf_cool` dominates the hero, and the
   low K4 / K6 / K7 / K12 lobes read dark olive balls end-on. The sheet's low lobes are as bright as its mid lobes.
   Bottom band `#546A2C` against `#4B5C26` is fine on the median, but the lit quartile is −16 red. Record it.
5. **Minor — thorns wash out from directly above** (top median +30, +25, +22). This is diffuse light on up-facing
   faces; the f34 and front medians are within 13. Requires Manual Validation in Studio.
6. **Minor — rear W : H is 1.346 against 1.232.** The low back lobes reach the ground at both sides; width at h .1 is
   .89 against .65. Record it.
7. **Minor — the f34 h .35 row has 2 wood runs against the sheet's 4** (B1's partly-met sub-criterion). FL merges
   with BL behind it. The f34 still shows the trunk column plus two separate limbs at h .45 / .50. Record it.
8. **Minor — parts.**
   - Core part: matches the key part (trunk, low left limb, two upper limbs, cut centre stub).
   - Cluster part: fatter than in round 1, but its lobes have broad flat front facets (blockier than the sheet's
     faceted gems). Acceptable.
   - Thorn part: L : D 1.8, slimmer than the key thorn's about 1.6. Acceptable.

**Passed:**
- every technical requirement;
- size;
- both blockers' acceptance criteria (except item 7);
- f34 / front shares within ±3;
- crown peaks 5 / 5;
- five thorns on the right diagonals;
- pointed gem lobes on the crown;
- hero colour medians within 13;
- warm wood (hue 25°);
- no colour by facing;
- no VFX, as decided.

**For the main session:**
- Commit with items 1–8 recorded. Item 1 is the only one worth a quick optional pass.
- End the orphan PID 112824.
