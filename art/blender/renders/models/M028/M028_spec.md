# 028 Frost Shrub — spec

Reference: `art/blender/assets/references/028.png`. The sheet's own title is "30 / 132 — FROST SHRUB", "Individual
Model Study", top right "FLINTBORN — STYLIZED ASSET REFERENCE", footer "PAGE 30/132" (INDEX.md row 28 calls it
"Flintborn frost shrub model study"; the page number on the sheet is not the index number). The image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m028.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`
(one modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7).

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no glow, sparkle, mist or particles** (§7).

Sheet text:
- **Views:** "Front Three-Quarter", "Rear Three-Quarter", Front, Side, Rear, Top.
- **Exploded View & Parts:** labels "Ice Nodule", "Forked Stem", "Leaf", "Base". The drawing shows the forked stem
  (trunk + tall up-left limb + short centre limb + up-right limb + a left branch ending in two stubs), a **separate short
  side branch** at the lower right (with its own small stub; a dashed line plugs its flat foot down into the base), **two
  dark-blue leaves** (dashed to the left branch's out-stub and the side branch's end), **two pale ice nodules** high
  (dashed to the left branch's up-stub and the up-right limb's end), **two smaller loose pale nodules** low left and low
  right (no dashes), and the base (rock ring, snow mound, two ice nodules on it; dashed lines from the trunk foot and the
  side branch's foot down into the snow).
- **Assembly Close-Up:** a limb's flat 8-sided end ("Joining Surface", a socket dot and a tiny peg) and a leaf with a
  dashed arrow to it ("Leaf").
- **Base Underside:** the base from below: rocks fused into one lumpy slab with a "Flat Underside (environment
  placement)"; snow shows over the rim.
- **Branch Thickness:** a limb's 8-sided cut end: "Consistent Low-Poly Thickness".
- **Material palette:** six unnamed swatches: pale ice blue, mid blue, deep blue, snow white-blue, warm brown,
  grey-brown.
- **Modeling notes:** "Chunky, readable low-poly forms"; "Broad, flat shaded faces (no textures)"; "Reusable modular
  parts (leaves, ice nodules, stem, base)"; "Clean join points and consistent thicknesses"; "Simple, solid colors
  matching FLINTBORN style".
- **Game context:** `src/shared/Resources/NodeCatalog.luau` has the node **`FrostShrub`** (material `Frostleaf`,
  health 4, `REGROW.Basic`, mastery Farming — the same stats as `ThornShrub`), placeholder look `P.Ball, M.Ice, SHRUB`
  (3 × 3 × 3); `BiomeCatalog.luau` spawns it in Frostpeak Ridge (share 10, habitat Highland). WorldModeling §11 lists
  "Emberbloom / Frost Shrub / Mooncap / Ancient Root: keep event inserts separate: … snow/ice nodules … Reuse the
  common plant grammar. Effects, if later requested, must not conceal the geometry during approval." The old **R08 kit
  sheet** has `FrostShrub` (10.6 W × 7.8 D × 8.7 H, a bare forked sapling with ico-1 "balloon" nodules and lozenge
  leaves on a 9-rock ring with a snow slab; sockets `vapour` + `harvest_hit`, depleted `harvest_deplete`) and owns its
  names (§8). MODEL_PROGRESS row R08: "mostly-done — short thick stem, few forks; big ice icosahedra".

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The panel rules are
at y 82–83, 539–540, 800–801, 1344 and x 17, 306–307, 519–520, 649–650, 783–784, 1006–1007 (`lines.py`). The paper is
about `#F2ECE6`; each view's paper is the median of its box's top and bottom 4 rows. The view labels are blanked to
paper before measuring (`m.py` `LABELS`). View boxes: f34 (19,85,518,538), r34 (522,85,1005,538), front
(19,542,305,799), side (309,542,518,799), rear (522,542,782,799), top (786,542,1005,799).

The masks are `cls3()` in `m.py` (HSV; background = within 14 of the paper). **The ground shadow is background:** it
is warm grey (b < r), and every blue class requires b − r ≥ 6, so the shadow falls into O and never enters a bbox,
share or profile:
- **blue** = cool (b − r ≥ 6), hue 185–245°, v ≥ 0.45.
- **L, leaves:** connected components of (blue, sat ≥ 0.40) whose **median** sat ≥ 0.555 and median v ≤ 0.80. Leaves
  measure sat 0.59–0.64 / v 0.71–0.78 per component; the ice nodules' shaded faces sat 0.45–0.52 / v 0.84–0.93, so the
  component rule separates them where a per-pixel threshold can't (a leaf's lit facets reach sat 0.48 and a nodule's
  shade facets sat 0.50).
- **I, ice:** the other blue with sat ≥ 0.20: the ice nodules (canopy and base) and the snow's shaded faces.
- **S, snow:** blue with sat < 0.20 and v ≥ 0.70: the snow's lit faces and the nodules' palest crown facets.
- **W, wood:** the largest connected brown component (hue < 48° or ≥ 330°, sat ≥ 0.14, v < 0.86, not blue): the stem.
  Wood is sat 0.41–0.45 per view.
- **R, rock:** every other brown component (the ring rocks; sat 0.28–0.35). The trunk never touches a rock in any view
  (snow and nodules separate them), so the split is clean.
- **O, other:** ground shadow, anti-aliased edges. Not counted.
- "Canopy" below means rows above h 0.45; "base" below it.

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m028_study\`.
Run with the scratch venv `...\scratchpad\venv22\Scripts\python.exe` (Pillow + numpy; no scipy, so `m.py` has its own
`label()`).
- **Helpers:** `m.py` (masks `cls`, `cls2`, `cls3`, view boxes `V`, `LABELS`, `stats`, `label`), `bb.json` (silhouette
  boxes), `crops.py`, `gridcrop.py`.
- **Measurements:** `measure.py` → `measure_out.txt` (bboxes, shares, top profiles, width per height, class extents,
  class shares per 0.1 h); `comps.py` → `comps_out.txt` (every leaf and canopy-nodule component: extents, PCA axis,
  length, width, ends); `wood.py` → `wood_out.txt` (wood runs per height); `base.py` (bottom profile, rock tops, base
  width per height); `prof.py` (outline width profiles and end angles of every leaf and nodule, sheet and parts);
  `expl.py` (exploded and close-up components).
- **Colour:** `probe.py` (swatches), `samp.py` → `samp_out.txt` (views, parts, close-ups), `samp2.py` (base nodules),
  `grad.py` → `grad_out.txt` (leaf and nodule base → tip, height bands per class, rock colour by column).
- **Crops:** `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `cu.png`, `pal.png`;
  grids `g_*.png` (10 % grid on the silhouette bbox, red = centre lines); mask previews `cls_*.png` (blue = L, sky = I,
  mint = S, brown = W, grey = R, magenta = O).
- **Zooms:** `z_expl_stem.png`, `z_f34_canopy.png`, `z_f34_bl.png` (front-left base nodule), `z_front_base.png`,
  `z_cuasm.png`, `z_cuthick.png`.
- **To run the scripts on our renders,** point `R` (in `m.py`) at the render, set the view boxes `V`, set `LABELS = []`,
  and re-run `measure.py` (it rewrites `bb.json`), then `comps.py`, `wood.py`, `prof.py`, `samp.py`. Render with the
  studio floor hidden (`FB_Ground.hide_render = True`) or check that its shadow is neutral grey (b − r < 6), or the
  bbox picks it up (024's verifier lesson).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a forage resource node, `FrostShrub`). Hero budget 4000 tris, each part under 1000.
  WorldModeling suggests 250–1,000 for a forage shrub; the plan in §4.3 lands at about 2000–2600 after the unions
  because of the rock ring and the faceted nodules. Don't thin the facets to chase 1000.
- **Overall read (check this first).** A small bare **sapling on a snowy rock ring**, a little wider than tall (front
  W : H 1.19):
  - **a thick warm-brown trunk column** standing up out of a snow mound, clearly visible from the snow line (h .20)
    to the fork (h .60): one straight 8-sided column about 0.2 W wide, leaning a little to +X above h .45. At h .40–.45
    two low limbs leave it (left to the leaf pair, right to the right leaf); at h .60–.65 it forks into a **tall bare
    limb leaning up-left with a flat cut top** (the highest wood, h .96) and a **right branch rising at about 20° to a
    flat cut end** at the right (f .87), with a short centre limb hidden behind the right nodule. **Wood is 26 % of
    every elevation view** — the skeleton is a headline feature;
  - **three big dark-blue leaves**, each an elongated **faceted hexagonal shard** (a fat lozenge, L : W 1.9–2.05,
    pointed at the tip, blunt-pointed at the base): one pointing up-left (UL), a smaller one pointing straight left (LL),
    one pointing right and slightly up (R). Leaves are 27 % of the front;
  - **two pale ice nodules** high in the crown: NR on the right branch (the tallest thing, h 1.0, leaning right), and
    NB at the back left behind the UL leaf (hidden from the front, the big right-hand nodule in the rear view, §3.1).
    Each is a **faceted ice gem**, L : W 1.6, pointed at both ends, pale blue with near-white crown facets;
  - **the base:** a ring of about 11 chunky warm-brown and grey-brown rocks round a **lumpy faceted snow mound** that
    fills the ring, swallows the trunk foot and breaks through the ring to the ground at the front centre; **four
    mid-blue ice nodules** half-buried in the snow round the trunk (two front, two back). The base is the bottom 30 %
    of every elevation view.
  - Front shares: leaves 27 %, ice 22 %, snow 11 %, wood 26 %, rock 13 %.
- **Focal silhouettes, in order:**
  1. The Y of bare brown wood: the trunk column, the tall up-left limb with its flat cut top, the right branch with its
     cut end, framed by the big blue leaves on both sides.
  2. The pale gem NR on top right and the three blue shards splayed out left and right at mid-height (the widest band,
     h .45–.55, 0.93 W).
  3. The low wide base: a lumpy rock ring with white snow, a "waist" of bare trunk between base and canopy (h .25–.35
     only 0.54 W wide).
- **Target size: about 4.3 W × 3.0 D × 3.6 H studs** (H = 0.65 of the 5.5-stud character, the top of WorldModeling's
  0.25–0.65 C forage-shrub range; W : H 1.19 is inside its 0.9–1.6). Tolerances W ±0.25, D ±0.3, H ±0.2. Decision §8.1.
  - **How it was derived.** The sheet has no character. `FrostShrub` is a Farming node with `ThornShrub`'s stats, so it
    belongs to the forage family fixed by M017 (`BerryBushNode` 4.3 × 3.5 × 3.6), M022 (`FiberPlantNode` 4.7 × 3.9 ×
    3.6) and M024 (`ThornBushNode` 4.8 × 4.0 × 3.6). The same height keeps it one of that family. The front cell
    (246 × 207 px) then gives **about 57 px per stud**, the side cell (165 × 209) the same.
  - **Width:** front W : H 1.188 at e ≈ 12° (screen height 3.83 for H 3.6 with the ring's front at Y −1.48) → 4.55;
    the hero f34 cell is the same drawing 10 % narrower (W : H 1.069, §3.2) → 4.1. **4.3** sits between them and keeps
    both renders within ±0.06 of their W : H.
  - **Depth:** side D : H 0.789 → 2.95–3.0. The rock ring is wider than deep: front ring 0.82 W = 3.5 studs, side ring
    0.99 D = 2.95. So **3.0** (±0.3).
  - **Alternatives:** × 1.2 (5.2 × 3.6 × 4.3, 0.78 C: the rock ring at shin height and the crown at the shoulder, more
    like the Emberbloom event plant), or R08's scale (10.6 × 7.8 × 8.7, taller than the player).
  - Resulting part sizes at 3.6 H: trunk Ø 0.75–0.8 (foot flare 0.95); limbs Ø 0.36–0.45; leaves UL 1.65 × 0.85,
    R 1.7 × 0.85, LL 1.2 × 0.63 (thickness 0.7 × width); nodules NR 1.45 × 0.92, NB 1.4 × 0.88; base nodules
    0.8–0.95 × 0.75–0.85; rocks 0.55–0.85 wide × 0.38–0.6 tall; snow mound about 2.2 × 1.9 × 0.85.
- **Build frame:** front −Y, +X right, ground z 0, origin = the ring centre (the trunk foot's axis). Stage 2 re-centres
  to the bbox bottom centre.
- **Stud mappings used below** (cells drawn at e ≈ 12°, §3.3):
  - front and f34: X = (f − 0.50) × 4.3; z ≈ 3.9 h − 0.3 − 0.2 Y (screen up = z cos e + (Y + 1.48) sin e);
  - rear and r34: X = (0.50 − f) × 4.3 (screen right = −X); z as above with −Y;
  - side: Y = (f − 0.50) × 3.0, **screen right = +Y (the back)** for the kit side camera at az 90 (+X); the side cell
    agrees with this on NR, the R leaf and the centre limb's cut end (§3.4);
  - top (image top = back by kit convention): X = (f − 0.5) × 4.3, Y = (h − 0.5) × 3.0, but see §3.5.

### 1.2 Measured views (`measure.py`, `comps.py`)

| View (box) | Silhouette bbox (px) | W : H | Leaves L | Ice I | Snow S | Wood W | Rock R | Leaves / canopy nodules visible |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (19,85,518,538) | 51–482 × 116–519 (432 × 404) | 1.069 | 28.1 % | 21.5 % | 11.6 % | 26.2 % | 12.6 % | 3 (UL, LL, R) / 1 (NR) |
| Rear three-quarter (522,85,1005,538) | 547–972 × 115–519 (426 × 405) | 1.052 | 24.7 % | 25.1 % | 10.1 % | 26.5 % | 13.6 % | 3 / 2 (§3.1) |
| Front (19,542,305,799) | 40–285 × 575–781 (246 × 207) | 1.188 | 27.4 % | 22.4 % | 11.4 % | 26.1 % | 12.7 % | 3 (UL, LL, R) / 1 (NR) |
| Side (309,542,518,799) | 329–493 × 571–779 (165 × 209) | 0.789 (D : H) | 4.7 % | 32.5 % | 16.1 % | 25.4 % | 21.4 % | 1 / 2 |
| Rear (522,542,782,799) | 535–765 × 588–780 (231 × 193) | 1.197 | 16.5 % | 29.4 % | 11.9 % | 27.0 % | 15.2 % | 2 (R, LL) / 2 (NR, NB) |
| Top (786,542,1005,799) | 800–983 × 589–766 (184 × 178) | 1.034 (W : D, tilted) | 24.1 % | 30.9 % | 12.6 % | 26.3 % | 6.1 % | 3 / 1–2 |

- **Reading:** wood is 25–27 % of **every** view, the top included (the limbs spread wide). Leaves are 27–28 % of the
  front and f34 and 16.5 % of the rear (two leaves; NB covers the third). The side is base-heavy: rock 21 %, ice+snow
  49 %, one leaf.
- The f34 is the front cell's drawing (every part within ±0.02 of the same fractions, §3.2). The r34 is the rear's
  layout with the UL leaf visible as well (§3.1).
- I and S trade with lighting (a nodule's crown facets fall into S), so the verifier should judge **I + S together**
  (front 33.8 %, rear 41.3 %, side 48.6 %, f34 33.1 %, r34 35.2 %, top 43.4 %) and treat the I/S split as ±6.
- **Verifier tolerance:** shares ±4 points (I + S ±5; top ±6); profile values ±0.07 h; positions ±0.06 of W/H unless
  stated.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .46 | .52 | .56 | .90 | .87 | .85 | .82 | .74 | .96 | .93 | .82 | .71 | .88 | .96 | .99 | 1.0 | 1.0 | .79 | .61 | .60 | .59 |
| Front | .46 | .52 | .56 | .91 | .88 | .86 | .83 | .76 | .93 | .96 | .86 | .74 | .85 | .94 | .99 | 1.0 | 1.0 | .77 | .59 | .58 | .57 |
| Side | .11 | .14 | .55 | .56 | .70 | .75 | .73 | .71 | .90 | .96 | 1.0 | .97 | .92 | .82 | .71 | .32 | .30 | .27 | .21 | .19 | .12 |
| Rear | .59 | .60 | .61 | .62 | .92 | .91 | .90 | .86 | .77 | .98 | .90 | .99 | .50 | .85 | .94 | .96 | .97 | .98 | .61 | .59 | .56 |
| r34 | .55 | .56 | .57 | .58 | .78 | .91 | .90 | .88 | .82 | .72 | .84 | .83 | .96 | 1.0 | .94 | .70 | .73 | .76 | .78 | .43 | .39 |
| Top (h = back) | .54 | .59 | .63 | .65 | .79 | .79 | 1.0 | .99 | .98 | .96 | .89 | .94 | .95 | .87 | .86 | .80 | .79 | .75 | .78 | .78 | .77 |

- **Front:** three distinct crown masses with real dips between them: the UL leaf's tip (f .15, .91) sloping down its
  edge to .76 at f .35; the tall limb's cut top (f .40–.45, .93–.96); a dip to .74 at f .55 (the gap between the limb
  and NR); NR's dome peaking at 1.0 (f .70–.80); then a cliff to the R leaf (.59 at f .90, its tip .57 at f 1.0). On
  the left the LL leaf's tip sits at .46 (f 0).
- **Rear:** NR (screen left, .92 at f .20), the V of two bare prongs (.98 at f .45 and .99 at f .55, with .90 between),
  a deep notch to .50 at f .60, and NB's dome (.94–.98 at f .70–.85).
- **Side:** a lopsided crown: everything above h .32 lies in f .10–.72. NR on top (1.0 at f .50).
- **Stage 1 targets:** front_sheet ≥ 3 separate crown masses with dips ≥ 0.10 h between them (f .35 and f .55); the
  tall limb's flat top must be on the silhouette (.93–.96 at f .40–.45), not hidden by a leaf or nodule.

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .05@.33 .82@.09 .78@.09 .60@.18 .74@.10 .91@.04 .80@.17 .72@.12 .69@.11 .70@.12 .04@.76
front  .42@.28 .82@.08 .67@.16 .54@.21 .83@.07 .93@.03 .68@.17 .72@.13 .69@.13 .69@.14 .08@.74
side   .62@.22 .99@.00 .83@.07 .59@.20 .39@.18 .50@.09 .44@.21 .50@.20 .27@.38 .22@.39 .03@.48
rear   .38@.35 .81@.10 .72@.16 .54@.24 .57@.11 .93@.04 .88@.03 .68@.17 .68@.19 .68@.19 .03@.54
r34    .07@.41 .82@.12 .68@.22 .40@.31 .90@.09 .82@.02 .69@.22 .68@.23 .50@.20 .50@.21 .01@.65
```

- **Shape in elevation (front, rear):** a wide base band (0.82 W at h .1), a **waist** at h .3 (0.54 W: only the trunk,
  the base nodules' tops and the snow), the **widest band at h .45–.55** (0.93 W: leaf tips both sides), then about
  0.7 W from h .6 to .9 (UL leaf + tall limb + NR), and the NR tip alone at the top.
- **Side:** the base is the widest (0.99 D at h .1); the canopy is narrow (0.39–0.50 D at h .4–.7, 0.22–0.27 at h .8–.9).
  The canopy is only about 1.5 studs deep.
- **Stage 1 targets** (front_sheet, rear_sheet, ±0.07): the waist ≤ 0.62 W at h .3; ≥ 0.86 W at h .5; base 0.76–0.88 W
  at h .1.

**Class bands** (front; L / I / W / R, + S, % of each 0.1 h band, bottom → top):

```
h0-.1 0/18/0/73+S9   .1-.2 0/28/0/27+S44   .2-.3 0/59/26/1+S13   .3-.4 18/15/63/0+S5   .4-.5 62/1/36/0+S1
.5-.6 65/2/31/0+S2   .6-.7 42/4/54/0+S1   .7-.8 39/31/30/0+S1   .8-.9 26/50/20/0+S4   .9-1 0/29/18/0+S53
```

- The bottom band is rock (73 %), the next is snow (44 %) and ice; h .2–.3 is base nodules and the trunk; from h .4 the
  canopy is leaves and wood; the top two bands are NR (I + S) and the tall limb.

**Wood runs** (`wood.py`, W mask; f ranges, width as a fraction of W, × 4.3 for studs):

```
front h .20  .47-.51 (.05)                    the trunk in the snow's V (snow line)
      h .25  .40-.56 (.16 = 0.69)             trunk
      h .30  .38-.56 (.19 = 0.82)             trunk
      h .35  .37-.58 (.22)                    trunk, the low limbs' roots beginning
      h .40  .34-.65 (.32)                    trunk + left limb root + right low limb to the R leaf
      h .45  .29-.43 (.14) .45-.65 (.20)      left limb | trunk + right low limb
      h .50  .28-.39 (.11) .47-.59 (.13)      left limb end (under UL/LL) | trunk
      h .55  .49-.62 (.14)                    trunk, leaning right
      h .60  .50-.70 (.20)                    the fork
      h .65  .49-.79 (.30)                    fork: tall limb root + right branch
      h .70  .47-.57 (.10) .58-.62 (.04) .71-.85 (.15)   tall limb | centre limb sliver | right branch
      h .75  .46-.54 (.09) .59-.61 (.02) .79-.87 (.08)   tall limb | centre sliver | right branch cut end
      h .80  .43-.52 (.09) .59-.60 (.02)      tall limb leaning left
      h .85  .41-.50 (.09);  h .90 .39-.48 (.09);  h .95 .41-.46 (.04)   tall limb to its cut top
rear  h .25 .52-.61; h .30-.35 .45-.65 (.20); h .40 .36-.67; h .45 .35-.71 (low limbs leave)
      h .50 .43-.58 (.16) .60-.70 (.11)       trunk | the limb to LL (screen right = -X)
      h .55 .38-.56 (.19) .62-.71 (.10)
      h .60 .28-.54 (.27);  h .65 .19-.54 (.35)   the right branch toward NR (screen left = +X)
      h .70 .17-.24 .39-.41 .46-.54;  h .75-.80 .46-.54 (.08)   branch end | tall limb
      h .85 .44-.56 (.13);  h .90 .42-.49 .50-.57;  h .95 .41-.47 .52-.58   the V: two bare prongs
side  h .25-.45 .44-.61 → .32-.58 (.17-.26)   trunk (0.51-0.78 deep)
      h .50 .22-.40 (.19) .45-.59;  h .55 .18-.29 .47-.60   the limb forward (screen left) to the R leaf | trunk
      h .60-.65 .45-.68;  h .70 .44-.50 .54-.60 .62-.69;  h .80 .38-.39 .62-.64   fork; the centre limb's cut end at the back
```

- The trunk is about 0.8 studs wide (0.19 W) as a column from h .25 to .55; the limbs 0.35–0.45 (0.08–0.11 W).
- **Skeleton read (024's failure, made measurable).** The trunk is a **column**: one wood run from h .20 to h .55 in
  the front and rear, 0.16–0.22 W wide, centred at f .46–.55. It splits **twice**: low limbs at h .40–.45 and the main
  fork at h .60–.65. Above the fork the tall limb is a single run 0.08–0.10 W wide from h .70 to .95, moving left from
  f .52 to .43 (≈ 25° from vertical), and the right branch a separate run at h .70–.75 ending at f .85–.87.

**Leaf and canopy-nodule components** (`comps.py`; extents, PCA axis from +x counter-clockwise, length / width):

| View | Leaves | Canopy nodules |
| --- | --- | --- |
| front | UL f .13–.37 h .53–.90, axis 127°, ends (.33,.53) → (.14,.90), L/W 1.70; R f .64–1.0 h .36–.59, 18°, (.64,.43) → (1.0,.56), L/W 2.07; LL f 0–.27 h .40–.57, 4°, (.27,.49) → (0,.45), L/W 1.89 | NR f .60–.83 h .68–1.0, axis 57°, (.63,.68) → (.81,1.0), L/W 1.58 |
| f34 | UL f .11–.37 h .54–.90; R f .60–1.0 h .38–.62; LL f 0–.28 h .40–.56 (all within .02 of the front) | NR f .59–.81 h .70–1.0 |
| rear | R f 0–.34 h .37–.62, axis 161° (screen left = +X); LL f .71–.99 h .42–.61, axis 10° | NR f .19–.39 h .66–.92, axis 134°; NB f .61–.87 h .59–.98, axis 66° |
| r34 | R f 0–.36 h .34–.58; UL f .69–.91 h .46–.78, axis 58°; LL f .74–1.0 h .31–.46 | NR f .20–.44 h .60–.91; a second nodule f .55–.71 h .73–1.0 (NB, §3.1) |
| side | one leaf f .07–.30 h .40–.56 (screen left = front: the R leaf, §3.4) | NR f .39–.62 h .70–1.0 (top centre); one f .19–.41 h .52–.76 (§3.4) |
| top | f 0–.34 h .45–.65 (pointing −X); f .77–.99 h .55–.77; f .63–.97 h .01–.34 (pointing front-right) | f .27–.53 h .67–1.0 (back left: NB); f .59–.83 h .50–.80 (NR) |

**Base** (`base.py`): bottom profile ≈ 0 across f .15–.85, rising to .08 at f .10 (the ring's front curve). Rock tops
h .08–.24 (front), the highest at the right (.24, f .80). The base is 0.82 W wide at h .10, 0.67 at h .20, 0.54 at h .30.
No rock in front of the snow at f .45–.60: the snow mound reaches the ground there.

### 1.3 Silhouette and composition per view

**Front (`g_front.png`; governs proportions).** Camera on the front axis, e ≈ 12°.
- **Skeleton (`z_f34_canopy.png`, `z_expl_stem.png`):** the trunk rises out of the snow at f .47 (h .20), a straight
  column 0.19 W wide, leaning slightly right above h .45. The **left limb** leaves at h .40–.45 going left and a little
  up to f .28–.33, h .50, where the UL leaf (up-left) and LL leaf (left) attach to its end. The **right low limb** leaves
  at h .40 and runs a short way right to the R leaf's base (f .64, h .43). At h .60–.65 the **fork**: the **tall limb**
  rises up-left to a flat cut top at f .41–.46, h .96 (the cut face is pale orange-brown and slanted); the **right
  branch** rises right at ≈ 20° to a flat cut end at f .87, h .72–.75; NR sits on a short stub on its top, in the crotch
  between the branch and the tall limb. The thin sliver at f .58–.62, h .70–.80 is the **centre limb** behind NR.
- **Leaves:** UL is the biggest face-on shard (its broad face toward the camera, a ridge down its length, the lit upper
  right facets paler); LL is smaller and nearly level; R rises 18° to the right. All three are clearly pointed at the tip
  (outline tip 77–88°).
- **Nodules:** NR leans right (axis 57°), its crown facets near white, its lower facets mid blue; it is the highest
  point. Base nodules FL (f .10–.35, h .15–.38, mid blue) and FR (f .60–.83, h .17–.38, paler), each half-buried.
- **Base (`z_front_base.png`):** rocks left (two grey-brown, one far left darker), front-left (a small warm-brown one),
  the snow's front lumps breaking through at the front centre, front-right (a big warm-brown one), right (grey-brown),
  far right (grey-brown). The snow mound shows two big front lumps with a V between them under the trunk.

**Front three-quarter (`g_f34.png`, the hero).** **Not** a three-quarter view: the same drawing as the front cell, about
10 % narrower (W : H 1.069 against 1.188) with every part within ±0.02 of the same fractions and the same bottom sag
(the same elevation, §3.2). Compare with `f34_sheet (0, 12)`.

**Rear (`g_rear.png`; screen right = −X).** The true rear: R leaf at screen left (pointing +X), LL at screen right; NR
at screen left high (f .19–.39, leaning +X); **NB at screen right high** (f .61–.87, h .59–.98, axis 66°), exactly
where the front's UL leaf would show from behind, so NB hides UL (§3.1). The tall limb is vertical here and the top is
a **V of two bare prongs** (h .85–.98, f .41–.58): the tall limb (−X prong, screen right) and the centre limb (+X prong,
screen left). Base: two nodules at the back (f .2–.4 and .6–.8), the same rock ring.

**Rear three-quarter (`g_r34.png`).** The rear drawn larger and narrower (W : H 1.052), as the f34 is to the front. It
shows NR big at screen left (f .20–.44), a smaller nodule at the top centre (f .55–.71, h .73–1.0: NB seen past the tall
limb), the R leaf at screen left low, the **UL leaf at screen right high** (f .69–.91, h .46–.78) and LL at screen right
low. So the r34 shows all five canopy items: 3 leaves + 2 nodules. Compare with `r34_sheet (180, 12)` by counts and
shares.

**Side (`g_side.png`; kit camera at +X, screen right = +Y the back).** Narrow (D : H 0.79), base-heavy. NR on top centre
(f .39–.62); a leaf at screen left (front) at h .40–.56 (the R leaf, which points right and forward); a pale nodule at
screen left (f .19–.41, h .52–.76) on a limb going forward; the trunk at f .44–.61; the centre limb's flat cut end at
screen right (f .62–.69, h .70–.80). Nothing above h .32 behind f .72. See §3.4 for the one item that disagrees.

**Top (`g_top.png`; image top = back).** Drawn tilted and rotated (the ring reads as a diamond); see §3.5. Three dark
leaves radiating outward (left, back-right, front-right), a pale nodule at the back left (NB), a pale mass right of
centre (NR), the brown limbs crossing the centre (wood 26 %: the right branch's cut end at the far right, a limb to the
back), the snow mound's lumps filling the middle and a little rock at the rim (6 %).

**Close-ups.**
- **Assembly close-up (652,808,1005,1010; `z_cuasm.png`):** a limb (8-sided, broad flat facets) with a **flat cut
  end** square to the limb (a pale orange-brown end face `#BB8760`, a socket dot and a tiny peg: notation) and a leaf
  `#4B7BC3`: L : W 1.88, base end blunt-pointed (≈ 110°), tip pointed (≈ 81°), the belt parallel-sided.
- **Base underside (652,1013,1005,1213):** the rocks fuse into one lumpy slab with a **flat underside** (`#68544B`);
  rock lumps form the rim; snow shows over the top. One closed base, flat at z 0.
- **Branch thickness (652,1216,1005,1343; `z_cuthick.png`):** an **8-sided** cut end (`#A87551`), slightly irregular,
  the limb's section the same along its length ("consistent low-poly thickness").

### 1.4 Parts (Exploded View & Parts (19,803,648,1343), close-ups (652,803,1005,1343))

Scale: the exploded parts are drawn at varied scales (the base at about 107 px per stud, the stem at about 80). Use
the ratios and shapes from the exploded and the sizes from the hero. Facet language for every part: broad flat-shaded
facets, chunky, no noise.

#### Forked Stem — exploded (211,875,450,1132) 239 × 258 px plus the side branch (378,1042,466,1118); `z_expl_stem.png`

- **Exploded shape:** an **8-sided trunk** with a slightly flared, flat-cut foot (the foot about 1.15 × the trunk's
  Ø). At about 0.45 of its height the **left branch** leaves at about 45° and forks at its end into an **up-stub**
  (cut end, the nodule's joint) and an **out-stub** (cut end, the leaf's joint). The trunk continues to a fork at about
  0.6: the **tall limb** at about 30–35° from vertical to the left (the longest, a flat cut top), a **short centre
  limb** branching off the tall limb at about 0.75 of the height (cut end), and the **right limb** at about 35° from
  vertical to the right (cut end; the second nodule's joint).
- **Side branch (separate in the exploded):** a short limb (≈ 0.35 of the stem's height) rising at about 40° to the
  right with a small up-stub near its end and a flat foot that plugs into the base. In every hero view this limb joins
  the trunk's right side at h .40 (§3.6).
- Every limb is 8-sided, Ø ≈ 0.5 × the trunk's, **straight segments with visible knuckles** at the forks, tapering
  10–15 %, **flat square-cut ends** in the pale cut colour.
- **Size (recommended for the exported part):** about **2.4 W × 0.8 D × 3.2 H** (the hero skeleton without the leaves:
  trunk foot to the tall limb's top, side branch included).
- **Construction:** `_stem(limbs, foot_r, seed)` (M024's `_branch_core` pattern):
  - trunk loft, 8 sides, rings at z −0.1, 0.15 (flare), 0.6, 1.2, the fork z, with ±6 % radius and ±8° twist jitter
    per ring;
  - each limb a polyline of 1–3 **straight** segments (the kinks are the vertices), 8 sides, tapering 10–15 %,
    starting 0.25 inside its parent on the parent's axis, with a **flat end cap square to the last segment** and a
    knuckle swell (+8 % radius) at each kink ring;
  - one exact union of the limbs into the trunk; floor-cut the foot at z 0 for the exported part (in the hero the foot
    ends inside the snow mound).
- **Triangles:** trunk 8 × 4 × 2 = 64; a 2-segment limb 8 × 2 × 2 + cap 6 ≈ 38 → hero skeleton (5 limbs + 4 stubs)
  ≈ 64 + 5 × 38 + 4 × 22 ≈ **340**; after the union about 400.

#### Leaf ×2 in the exploded: left (45,963,185,1045) 140 × 82, right (489,977,604,1051) 115 × 74; close-up (846,847,984,938) 138 × 91

- **Shape: a faceted hexagonal shard (a fat lozenge), not a ball, tent or tulip.** Outline width / length along the
  axis (`prof.py`, base → tip, every 0.1):

```
cu_asm      .16 .30 .44 .51 .52 .52 .50 .42 .31 .19 .06     base 111°, tip 81°
expl left   .14 .28 .42 .52 .52 .52 .52 .44 .33 .20 .06     base 105°, tip 84°
expl right  .13 .27 .41 .49 .50 .49 .49 .41 .30 .18 .06     base 106°, tip 83°
front UL    .13 .29 .41 .52 .56 .56 .53 .47 .33 .20 .06     base 110°, tip 88°
front R     .10 .25 .40 .48 .48 .47 .46 .38 .28 .16 .05     base 101°, tip 77°
front LL    .03 .24 .43 .49 .49 .51 .52 .42 .31 .18 .06     base 100°, tip 79°
```

  - **Belt parallel-sided** from t .3 to t .6 (width ≈ 0.50–0.52 L); **tip taper longer and sharper** than the base
    (tip outline angle 77–88°, base 100–111°); L : W **1.85–2.05**.
  - **Section:** a flattened hexagon, thickness ≈ 0.7 × width, with a longitudinal ridge on the broad face (the sheet's
    lit and shaded halves meet along it), 3–4 facets across the visible width, 5–6 facets meeting at the tip.
- **Recipe (36–48 tris):** apex at t 0 (the base, sunk into its limb end); ring A at t 0.12 (6 vertices, 0.30 of the
  half-width); ring B at t 0.30 (6, 1.0); ring C at t 0.62 (6, 0.98, rotated 0–10°); ring D at t 0.82 (6, 0.60);
  tip apex at t 1.0 offset ±0.03 L by seed. Each ring is an ellipse 1.0 × 0.7 (width × thickness). Radius jitter
  ±5 %, ring twist ±6°. **6 + 3 × 12 + 6 = 48 tris.** Use this, not `K.leaf` / `NS["leaf"]` (spiky, serrated) and not an
  ico-1 squashed ellipsoid (R08's lozenge read as a balloon).
- **Size:** UL 1.65 × 0.85 × 0.6; R 1.7 × 0.85 × 0.6; LL 1.2 × 0.63 × 0.45. Exported part: the UL size.

#### Ice Nodule ×2 high in the exploded: (138,857,229,968) 91 × 111, (470,876,554,970) 84 × 94; ×2 low loose (110,1071,214,1144), (468,1097,548,1163)

- **Shape: a faceted ice gem** pointed at both ends, blunter than the leaf. Outline width / length:

```
expl UL     .12 .39 .55 .64 .67 .64 .62 .57 .41 .25 .06     ends 121° / 101°
expl UR     .10 .35 .50 .61 .65 .65 .63 .61 .47 .31 .10     ends 117° / 110°
front NR    .09 .27 .43 .56 .61 .63 .61 .59 .48 .28 .06     ends 106° / 106°
rear NB     .07 .29 .49 .58 .59 .60 .60 .56 .44 .27 .05     ends 100° / 103°
expl LL/LR  L/W 1.64 / 1.42 (squatter: the base nodules)
```

  - Widest at t .4–.6 (≈ 0.60–0.65 L), **L : W 1.5–1.7** (canopy), 1.4–1.6 (base); both ends 100–120°, a short crown
    of facets round each apex.
  - **Facets:** more and smaller than the leaf's: 8–12 visible per side, irregular triangles and kites, a few long ones
    along the belt. Big enough to read at a distance; no confetti.
- **Recipe (M014's crystal method):** convex hull of staggered 7–8-point rings — bottom apex (t 0), ring t 0.15 (0.45
  of the half-width), ring t 0.38 (0.95), ring t 0.62 (1.0, rotated half a step), ring t 0.85 (0.50), top apex (t 1.0)
  offset ±0.05 by seed; sector jitter ±6 % radius, ±3 % height (never per-vertex noise); then
  `bmesh.ops.dissolve_limit` at 3–4° and BEAUTY triangulation. Check 20–30 merged facets, 50–70 tris.
- **Size:** NR 1.45 × 0.92; NB 1.4 × 0.88; base nodules 0.8–0.95 long × 0.75–0.85 (L : W 1.25–1.4, squatter).
  Exported part: the NR size.

#### Base — exploded (146,1150,519,1300) about 373 × 150 px; underside close-up (679,1053,930,1182)

- **Rock ring:** about **11 chunky rocks** on an oval ring, outer 3.5 (X) × 2.95 (Y). Rocks 0.55–0.85 wide, 0.38–0.6
  tall, each a squat hull of 6–8 points with 2 height rings and a quiet top (WorldModeling §12.1), flat bottoms,
  overlapping their neighbours by 0.08–0.15. Two kinds: **warm brown** (front centre-left, front right, back) and
  **grey-brown** (left, right, back left), about 2 : 1 by area (§5). **The ring is open at the front centre** (f .45–.60):
  the snow fills that gap down to the ground.
- **Snow mound:** a **lumpy faceted mound** (3–5 broad hull lumps fused), about 2.2 × 1.9 inside the ring, top z 0.7–0.9
  round the trunk, its outer lumps overlapping the rocks' inner faces; the two front lumps (each ≈ 1.0 across) with a V
  between them under the trunk; facets 0.3–0.6 studs, flat-shaded, no noise. The trunk foot sinks into it: the snow
  meets the trunk in a collar at z 0.45–0.6.
- **Base nodules ×4** (two in the exploded base, two more seen in the rear and side): FL mid blue, FR pale, BL and BR
  pale, each sunk 30–40 % into the snow (or against a rock), long axes tilted 15–35° outward.
- **Underside:** one flat face at z 0 under the whole base (the rocks' and the snow's bottoms on one plane).
- **Size:** about **3.5 × 3.0 × 1.1** (base nodules included).
- **Construction:** `_rock(d, h, seed)` × 11, `_snow(lumps, seed)`, `_nodule(...)` × 4; union the base as its own
  piece first (rocks one at a time into the snow), floor-cut at z 0.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, origin = ring centre). Azimuths from +X counter-clockwise (front =
270°, back = 90°); elevation = rise from horizontal.

### 2.1 Skeleton (`_stem` hero call)

| Limb | Polyline (from inside the parent → kinks → end) | Ø start → end | Carries | Sheet evidence |
| --- | --- | --- | --- | --- |
| Trunk | (0, 0, −0.1) → (0.02, 0, 0.6) → (0.08, 0.02, 1.25) → (0.25, 0.05, 2.1) fork | 0.95 at z 0.15 → 0.8 at 0.6 → 0.75 at 1.25 → 0.7 | everything | front h .25–.55 run .16–.22 W at f .46–.55; rear the same |
| LB left branch | (0.0, −0.05, 1.3) → (−0.55, −0.2, 1.52) → (−0.92, −0.35, 1.72) flat end | 0.45 → 0.40 | LL leaf (end), UL leaf (front stub), NB (back up-stub) | front h .45 run .29–.43, h .50 .28–.39; side h .50 run .22–.40 (forward) |
| LB up-stub (back) | (−0.75, −0.25, 1.65) → (−0.82, 0.15, 2.0) flat end | 0.36 → 0.34 | NB | exploded left branch's up-stub; rear NB position |
| LB front stub | (−0.7, −0.3, 1.65) → (−0.8, −0.45, 1.88) flat end | 0.36 → 0.34 | UL | front UL base (.33, .53) |
| RB right low limb | (0.15, −0.05, 1.15) → (0.58, −0.3, 1.42) flat end, plus a 0.25 up-stub at its middle | 0.42 → 0.38 | R leaf | front h .40 run to f .65; exploded side branch |
| TL tall limb | (0.25, 0.05, 2.0) → (0.1, −0.05, 2.45) → (−0.3, −0.1, 3.42) flat top, cut slanted 15° | 0.44 → 0.38 | — (bare) | front h .70 f .52 → h .90 f .435 → top .41–.46 at h .96 |
| RBr right branch | (0.25, 0.05, 2.05) → (0.65, 0.0, 2.32) → (1.6, −0.05, 2.6) flat end | 0.42 → 0.36 | NR (stub at X 0.65) | front h .65 run to .79, end f .87 h .72–.75; rear h .60–.65 run to f .19 |
| NR stub | (0.62, 0.0, 2.25) → (0.66, 0.0, 2.48) | 0.34 | NR | z_f34_canopy: NR sits in the crotch on a stub |
| CS centre limb | (0.25, 0.08, 2.1) → (0.55, 0.3, 2.75) → (0.7, 0.45, 3.15) flat end | 0.36 → 0.32 | — (bare) | front sliver f .58–.62 h .70–.80; rear +X prong; side cut end f .62–.69 h .70–.80 |

- **Measurable skeleton targets** (front_sheet; floor hidden; the study's masks):
  - **trunk column:** visible from the snow line at z 0.5 (h .20) to the fork at z 2.05–2.1 (h .60): **1.55 studs of
    bare trunk**, one run 0.16–0.22 W wide from h .25 to h .55;
  - **split heights:** low limbs at z 1.15–1.35 (h .40–.45), main fork at z 2.05–2.1 (h .60–.62);
  - **limb angles:** LB 15–20° above horizontal toward −X (and 20° forward); RB 25–30° above horizontal toward +X,
    −Y; TL 20–30° from vertical leaning −X; RBr 15–22° above horizontal toward +X; CS 25–35° from vertical leaning
    back and +X;
  - wood runs at h .45–.50: **two** (LB and the trunk); at h .70–.75: TL and RBr **separate** (≥ 0.10 W of paper or
    leaf between them); at h .80–.95: TL alone, 0.08–0.10 W, its centre moving left from f .48 to .43;
  - rear_sheet: the V — two separate wood runs at h .90–.95 (sheet .41–.47 | .52–.58, ±0.06).
- Kinks are real angles (15–35° between segments) with a knuckle ring; **never a smooth curve or a pipe.**
- No limb runs level at the trunk's foot and none leaves below z 1.1: the trunk must read as a column first (024's
  "nest" failure).

### 2.2 Leaves (3 copies of `_leaf`)

| Leaf | Base (on) | Tip (expected) | L × W × T | Roll | Sheet evidence |
| --- | --- | --- | --- | --- | --- |
| UL up-left | (−0.8, −0.45, 1.88), LB front stub | (−1.55, −0.6, 3.3) | 1.65 × 0.85 × 0.6 | broad face toward −Y (the front camera), ridge facing front | front ends (.33,.53) → (.14,.90), axis 127°; r34 screen right high |
| LL left | (−0.92, −0.35, 1.72), LB end | (−2.15, −0.3, 1.52) | 1.2 × 0.63 × 0.45 | broad face toward −Y, tilted 20° up | front (.27,.49) → (0,.45), axis 4°; rear screen right; top left leaf |
| R right | (0.58, −0.3, 1.42), RB end | (2.15, −0.9, 2.05) | 1.7 × 0.85 × 0.6 | broad face toward −Y/+z (tilted 25° up), ridge up | front (.64,.43) → (1.0,.56), axis 18°; side leaf at screen left; top front-right leaf |

- Each leaf's base point sinks 0.12–0.18 into its flat limb end (the joining surface stays visible on the exported stem
  only). Leaves don't touch each other; UL and LL overlap only near their bases.
- **Expected front:** UL f .14–.37, h .53–.90; LL f 0–.27, h .40–.57; R f .64–1.0, h .36–.59 (±0.06).

### 2.3 Nodules (`_nodule`)

| Nodule | Bottom apex → top apex | L × W | Sheet evidence |
| --- | --- | --- | --- |
| NR right, high | (0.6, 0.0, 2.38) → (1.33, 0.05, 3.6) | 1.45 × 0.92 | front (.63,.68) → (.81,1.0), axis 57°; rear screen left f .19–.39; side top centre; top right of centre |
| NB back left, high | (−0.8, 0.12, 1.98) → (−1.32, 0.42, 3.22) | 1.4 × 0.88 | rear screen right f .61–.87 h .59–.98, axis 66°; r34 top centre; top back left; hidden behind UL from the front |
| FL base, front left | (−0.95, −0.5, 0.3) → (−1.2, −0.65, 1.15) | 0.95 × 0.8 (mid blue) | front f .10–.35 h .15–.38; f34 FL |
| FR base, front right | (0.95, −0.45, 0.3) → (1.15, −0.6, 1.12) | 0.9 × 0.78 (pale) | front f .60–.83 h .17–.38 |
| BL base, back left | (−0.85, 0.6, 0.35) → (−1.0, 0.8, 1.05) | 0.8 × 0.72 | rear f .6–.8; side back nodule |
| BR base, back right | (0.85, 0.55, 0.35) → (1.0, 0.75, 1.05) | 0.8 × 0.72 | rear f .2–.4 |

- NR's bottom apex and its stub sink 0.15 into the right branch's top; NB's into the up-stub's end. NB must stay **at
  or under the UL leaf's outline from the front** (top z ≤ 3.25; a peek of ≤ 0.04 W is fine) and **cover the UL leaf
  from the rear** (UL ≤ 0.05 of the rear silhouette).
- Base nodules sink 30–40 % into the snow; none touches the trunk.

### 2.4 Base

- **Rocks** (centre on the oval rx 1.45, ry 1.2; d × h; az from +X):

| # | az | d × h | Kind | Note |
| --- | --- | --- | --- | --- |
| K1 | 235° | 0.75 × 0.42 | warm | front left of the snow gap (front f .27–.40) |
| K2 | 305° | 0.85 × 0.55 | warm | front right, the biggest front rock (f .62–.80) |
| K3 | 205° | 0.6 × 0.45 | cool | left front |
| K4 | 180° | 0.65 × 0.5 | cool | left (the darkest) |
| K5 | 340° | 0.65 × 0.58 | cool | right (rock top h .24) |
| K6 | 10° | 0.6 × 0.5 | cool | right back |
| K7 | 40° | 0.6 × 0.45 | warm | back right |
| K8 | 75° | 0.55 × 0.42 | warm | back |
| K9 | 110° | 0.55 × 0.42 | warm | back |
| K10 | 145° | 0.6 × 0.45 | cool | back left |
| K11 | 255° | 0.45 × 0.3 | warm | small front-left pebble rock in front of K1 (f34's) |

- **Gap:** no rock between az 255° and 290°: the snow's front lumps reach the ground there.
- **Snow:** lumps (hull centres; radii): S1 (−0.45, −0.55, 0.25; 0.65), S2 (0.45, −0.6, 0.25; 0.65), S3 (0, 0.0, 0.35;
  0.75), S4 (−0.7, 0.45, 0.25; 0.55), S5 (0.7, 0.45, 0.25; 0.55); squash z to 0.85 top; floor-cut at z 0.
- **Expected base:** X ±1.75, Y ±1.48; rock tops z 0.38–0.6; snow top z 0.85; base nodule tops z 1.05–1.15.
- **Expected hero:** X −2.15 … +2.15 (LL and R tips), Y −1.48 … +1.48 (rocks; the R tip −0.9, NB +0.45), z 0 … 3.6 →
  **4.3 × 2.95 × 3.6**.

### 2.5 Checks on the renders

- **front_sheet (0, 12):** W : H 1.12–1.25; shares ±4 of 27.4 / 22.4 / 11.4 / 26.1 / 12.7 (I + S ±5 of 33.8); top
  profile ±0.07 with the three crown masses and the dips at f .35 and f .55; width per height ±0.07; the components of
  §1.2 within ±0.06; the wood runs of §2.1.
- **f34_sheet (0, 12):** the same drawing: shares ±4 of 28.1 / 21.5 / 11.6 / 26.2 / 12.6; components ±0.06 of the
  f34 row; W : H 1.05–1.20 (§3.2).
- **rear_sheet (180, 12):** shares ±4 of 16.5 / 29.4 / 11.9 / 27.0 / 15.2; R at screen left, LL at screen right, NR
  screen left high, NB screen right high, the V of two bare prongs; UL hidden.
- **r34_sheet (180, 14):** 3 leaves + 2 nodules visible; shares ±5 of 24.7 / 25.1 / 10.1 / 26.5 / 13.6.
- **side_sheet (90, 12):** D : H 0.72–0.86; NR on top centre; the R leaf at screen left; the CS cut end at screen right;
  base 0.95–1.0 D at h .1; canopy ≤ 0.55 D at h .4–.7. See §3.4 for what not to chase.
- **Top (0, 89) + top_tilt (0, 70):** three leaves pointing outward (the sheet draws them left, back-right and
  front-right; ours are UL and LL on the left and R front-right: judge the count, not the positions, §3.5), two pale
  nodules (NB back left, NR right), wood visible crossing the centre (≥ 15 %), a ring of rock at the rim; shares ±6.

## 3. View conflicts and resolutions

### 3.1 The UL slot: a leaf in the front, f34 and r34; a nodule in the rear, exploded and side

- **Evidence.** Mirrored into the front frame, the rear's screen-right nodule (f .61–.87 → .13–.39, h .59–.98) sits
  exactly where the front draws the UL leaf (f .13–.37, h .53–.90). Every other item agrees across the front and rear:
  NR (front .60–.83 ↔ rear mirrored .61–.81), R (.64–1.0 ↔ .66–1.0), LL (0–.27 ↔ .01–.29). The exploded's left branch
  carries a nodule (up-stub) and a leaf (out-stub); the side draws a nodule and a leaf on its forward limb. But the r34
  shows **both**: the UL leaf (screen right high) and a second nodule (top centre).
- **Resolution (recommended, decision §8.3):** **3 leaves + 2 canopy nodules.** Keep the hero's UL leaf in front
  (Y −0.45), and add **NB behind it** (Y +0.1 … +0.45) on the left branch's up-stub (the exploded's nodule joint). The
  front then shows UL and hides NB; the rear shows NB and hides UL; the r34 shows both. That satisfies the hero, front,
  rear, r34 and exploded together. Only the side keeps a conflict (§3.4).
- **Alternative:** the exploded's literal set, 2 leaves + 2 nodules (UL becomes a nodule). That matches the rear,
  exploded and side, but changes the hero and front (a nodule where they draw their biggest leaf) and the r34.

### 3.2 The "front three-quarter" is the front drawn narrower; the "rear three-quarter" the rear drawn narrower

- **Evidence.** f34 and front place every leaf and nodule within ±0.02 of the same fractions; their top profiles agree
  within ±0.03; the bottom sag at f .10 is the same in studs (0.32 against 0.29), so the elevation is the same. Only the
  W : H differs (1.069 against 1.188): the f34 is horizontally compressed about 10 %. No camera can produce both from one
  model (at 4.5 W the f34 would need a screen height above any elevation's maximum). The r34 is likewise the rear's
  layout at W : H 1.052 against 1.197.
- **Resolution.** Proportions come from the front cell (4.3 is the compromise width, §1.1). Compare the hero with
  `f34_sheet (0, 12)` by components, shares and profiles, and accept W : H 1.05–1.20. Compare the r34 with
  `r34_sheet (180, 14)` by counts and shares. The kit `front34 (−28, 12)` and `rear34 (152, 12)` have no sheet
  counterpart: self-consistency only. The hero governs layout (WorldModeling §1.1).

### 3.3 Camera elevation

- The front, side and rear bottom profiles sag 0.05–0.08 h at f .10 (0.18–0.29 studs), which for the ring's 3.5 × 2.95
  oval gives e ≈ 12–15°. Use **12°** for the `*_sheet` extras (14° for r34, which shows a little more ring).

### 3.4 Side cell: agrees with the kit side camera, except for one item

- **Evidence.** With the kit side camera at +X (screen right = +Y, the back), the side shows NR on top centre (Y ≈ 0 ✓),
  the R leaf at screen left (the front: the R leaf points right **and forward**, ✓ the top view's front-right leaf), the
  centre limb's flat cut end at screen right high (the back ✓, CS leans back), and the LL leaf hidden behind the trunk
  (it points −X, away) ✓. **The one conflict:** a pale nodule at screen left (front, f .19–.41, h .52–.76) on a forward
  limb. That is the UL slot drawn as a nodule again (§3.1); our UL leaf stands there instead, and NB will show at the
  back (screen right, f ≈ .55–.70, h .55–.9) where the side cell is empty above h .32 behind f .72.
- A camera at −X (mirrored) fits NB but puts the R leaf, the CS cut end and the front stub on the wrong sides: worse.
- **Resolution.** Compare an extra **`side_sheet (90, 12)`** (not mirrored): D : H, base width, NR on top, the R leaf at
  screen left, the cut end at screen right, shares ±6. Accept a blue leaf where the sheet draws the pale nodule and NB
  showing at the back; keep NB's Y ≤ +0.45 so it stays inside f .72. Don't move parts to chase the side.

### 3.5 Top view: tilted, rotated and partly inconsistent

- **Evidence.** The ring reads as a diamond (the cell is rotated about 30–45° and drawn from about 65–70°): lumps of
  the snow mound show their sides; W : D 1.034 against the front/side 4.3 : 3.0. It shows NB at the back left ✓, NR right
  of centre ✓, the LL leaf pointing −X ✓, the R leaf pointing front-right ✓, and **a third leaf pointing back-right**
  where no other view has one (UL, seen from above, should point up-left and foreshorten on the left).
- **Resolution.** Judge the top by counts and shares, not positions: 3 leaves pointing outward, 2 pale nodules, wood
  crossing the centre, rock at the rim (shares ±6). Compare the kit `top (0, 89)` and an extra `top_tilt (0, 70)`.

### 3.6 Exploded side branch against the hero

- The exploded draws the R leaf's limb as a separate short branch plugging into the base; every assembled view shows it
  joined to the trunk's right side at h .40. **Resolution:** in the hero, the RB limb starts 0.25 inside the trunk at
  z 1.15 and is united with it. In the exported Stem part it is attached the same way (one part). Its small up-stub is
  kept (≤ 0.25 long).

### 3.7 Rear V against the front's single tall limb

- The rear's top is a V of two bare prongs at h .85–.98; the front shows one tall limb and a sliver at f .58–.62 h
  .70–.80. **Resolution:** the second prong is CS, leaning back and +X **behind NR**: from the front only its sliver
  shows beside NR; from the rear it is the +X prong (CS top z ≈ 3.15, a little lower than the rear's .98: accept the
  rear's +X prong at h .85–.92).

### 3.8 Exploded counts against the hero

- **Leaves:** exploded 2, hero 3 (§3.1). **Canopy nodules:** exploded 2, hero 2 ✓. **Loose low nodules** (2, no dashes,
  squatter L : W 1.42–1.64): the base nodules' shape, shown loose. The hero base carries 4 (two front, two back: the
  front, rear and side cells each show two). **Pegs, dots and sockets:** joinery notation; not modelled (decision §8.5).

### 3.9 "Simple, solid colors" and "no textures" against the user's blended-colour rule

- The user's rule wins, and the sheet shows painted variation (§5.3): leaves darker at the base than the tip, nodules
  deep blue at the bottom and near-white at the crown, two rock colours, snow faintly blue in its creases. Keep Tint low
  (the notes say "broad, flat shaded faces").

### 3.10 Effects

- The sheet shows none: no glow (the nodules' shade facets are as dark relative to their lit facets as the leaves', so
  they are not self-lit, §7), no sparkle, no mist, no particles. Stages 5/6 add nothing by default (§7).

## 4. Construction plan (modeller, stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `stem()` → `FrostBushStem`: the hero skeleton without leaves (≈ 2.4 × 0.8 × 3.2), flat 8-sided end caps, no
     holes, foot floor-cut at z 0. Compare with `z_expl_stem.png`: trunk column; left branch at ~0.45 with two stubs;
     fork at ~0.6; tall limb, short centre limb, right limb; side branch.
   - `leaf()` → `FrostBushLeaf`: the UL leaf (1.65 × 0.85 × 0.6). Compare its outline profile with §1.4 (±0.05 per
     station), L : W 1.85–2.05, tip angle 75–90°, base 100–115°, a ridge and 3–4 facets across.
   - `nodule()` → `FrostBushIceNodule`: NR (1.45 × 0.92). Outline ±0.05 of §1.4, L : W 1.5–1.7, ends 100–120°, 20–30
     merged facets.
   - `base()` → `FrostBushBase`: rock ring + snow mound + 4 base nodules, flat underside (≈ 3.5 × 3.0 × 1.15).
   - Render a parts shot (`extra`, about (−20, 15)) laid out like the exploded.
2. **Hero:**
   1. Build the base (rocks united into the snow one at a time; save the work file between steps); then the stem
      (limbs into the trunk); then paste the leaves and nodules (M011 `_paste` pattern) per §2.
   2. Unite base, stem, leaves and nodules **one piece at a time**, saving between risky steps; floor-cut at z 0.
   3. Origin at the bbox bottom centre; transforms applied. One closed shell (decision §8.6).
3. **Budget** (§4.3): hero about 2000–2600 (limit 4000), each part ≤ 700 (limit 1000). Spend spare tris on rock and snow
   facets or a leaf ring; never on smoothing.
4. **Placeholder keys** (stage 1): `m028_leaf`, `m028_ice`, `m028_snow`, `m028_wood`, `m028_rock`. Stage 4 adds the
   rest (§5.4).
5. **Stage 1 acceptance** (render with the floor hidden, compare every view, measure with this folder's scripts):
   1. **Overall read:** a bare brown sapling with a clear trunk column and a Y of cut-ended limbs, three blue shards and
      two pale gems in the crown, a snowy rock ring at the foot. Nothing ball-like, nothing cloud-like.
   2. **Leaf shape on the renders:** every leaf's outline profile (`prof.py`) within ±0.06 of §1.4 at each station;
      tip angle ≤ 92°; belt parallel (t .3–.6 within ±0.04). **No leaf may read as a ball, tent (2-ring cone) or tulip.**
   3. **Nodule shape:** L : W 1.5–1.75 (canopy), both ends ≤ 120°, facets visible as distinct tones (≥ 4 distinct facet
      tones per nodule in the front render); not a smooth egg, not an icosahedron.
   4. **Skeleton:** the §2.1 targets: trunk column 1.5 ± 0.2 studs bare; low split at h .40–.45, fork at h .58–.65;
      the wood runs; the rear V.
   5. **front_sheet / f34_sheet / rear_sheet / r34_sheet / side_sheet / top:** §2.5.
   6. **Kit views** (front34, rear34, underside): self-consistency; the underside is flat with the rock lumps at the rim.
   7. **Parts against their cells** (§4.1).
   8. **Hero size** 4.3 × 3.0 × 3.6 (±0.25 / ±0.3 / ±0.2).
6. **Stage 2:**
   - zero non-manifold, boundary, wire and loose elements; zero bowtie vertices (`M.audit` `nonmanifold_verts`; check
     where leaf bases meet limb ends and where nodules meet the snow); no zero-area faces or n-gons; normals outward;
   - no faces under 5° where limbs, leaf bases, nodule apexes, rocks and snow lumps meet (m011 `_tidy` / `_desliver`);
   - don't decimate a leaf below its 4 rings + 2 apexes, a nodule below 20 merged facets, or a limb below 8 sides; keep
     the kinks and the flat end caps.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Stem (trunk + 5 limbs + 4 stubs + caps) | 1 | 400 | 400 |
| Leaves (6-sided shard, 4 rings) | 3 | 48 | 144 |
| Canopy nodules (hull, dissolved) | 2 | 60 | 120 |
| Base nodules | 4 | 50 | 200 |
| Rocks | 11 | 40 | 440 |
| Snow mound (5 lumps) | 1 | 260 | 260 |
| **Sum before union** | | | **about 1560** |
| **Hero after union** (seams, slivers, floor cut) | | | **about 2000–2600** (limit 4000) |
| Parts: Stem / Leaf / IceNodule / Base | | | about 400 / 48 / 60 / 950 (limit 1000; thin the base's snow before its rocks if it runs over) |

## 5. Colour plan (modeller, stage 4)

### 5.1 Swatches (flat; medians of the inner box of each, y 1395–1430, x inset 8)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| 1 pale ice | (29,1384,81,1438) | `#B5DBFD` | 208°, 0.28, 0.99 |
| 2 mid blue | (90,1384,142,1438) | `#5989CC` | 215°, 0.56, 0.80 |
| 3 deep blue | (151,1384,203,1438) | `#3D68A8` | 216°, 0.64, 0.66 |
| 4 snow | (212,1384,263,1438) | `#CBDCF3` | 214°, 0.16, 0.95 |
| 5 warm brown | (272,1384,325,1438) | `#88624C` | 22°, 0.44, 0.53 |
| 6 grey-brown | (333,1384,386,1438) | `#6A554F` | 13°, 0.25, 0.42 |

- **Leaves** span swatches 2 and 3: tips and lit facets near `#5989CC`, bases near `#3D68A8`.
- **Ice** is swatch 1; the nodules render `#A6CCFB` (median) from `#6995D9` (bottom facets) to `#DAEEFE` (crown).
- **Snow** is swatch 4; it renders `#D4E3F7`.
- **Swatch 5 is both the wood and the warm rock.** In the renders they differ: wood is darker and more saturated
  (`#72523F`, sat 0.45) than the warm rocks (`#81624E`, sat 0.40). Swatch 6 is the cool rock and the underside.

### 5.2 Rendered regions (`samp.py`, `samp2.py`, `grad.py`; median / lit quartile / shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Leaves, front / f34 / rear | V | L | `#4877C0` / `#4776BE` / `#4271B7` | `#6B99DC` / `#6593D8` / `#6492D7` | `#2F5592` / `#305492` / `#305694` |
| Leaves, r34 / side / top | V | L | `#4472B9` / `#3D65A4` / `#4C7ABE` | `#5F8ED6` / `#4D7CC4` / `#6996D9` | `#305695` / `#2C4F88` / `#3963A4` |
| Leaves, exploded L / R / close-up | §1.4 | L | `#4573BB` / `#4A7AC4` / `#4B7BC3` | `#6694DB` / `#6998DD` / `#6898DE` | `#345B9C` / `#325896` / `#325694` |
| Canopy nodules, front / f34 / rear / r34 | V, h > .45 | I + S | `#A9CFFB` / `#A6CCFB` / `#8EB7EE` / `#91B8EE` | `#D9EEFD` / `#DAEEFE` / `#D2EAFD` / `#CAE3FD` | `#6C97DA` / `#6995D9` / `#537ABB` / `#6995D6` |
| Nodules, exploded UL / UR / LL / LR | §1.4 | I + S | `#96C0F9` / `#AED1FC` / `#98C0F7` / `#9CBCEF` | `#D7EEFD` / `#D7ECFD` / `#C7E3FD` / `#CDE7FD` | `#6B97DD` / `#719DE1` / `#6D9ADD` / `#6B96DC` |
| Base nodules, f34 FL / FR | (114,382,194,450) / (304,380,391,450) | L+I+S | `#7DA2E1` / `#A6C9F6` | `#9DBDF2` / `#CFE4FD` | `#567ABB` / `#6D96D8` |
| Base nodules, exploded L / R | (160,1155,260,1225) / (355,1150,445,1215) | L+I+S | `#99BBEE` / `#C1DAFB` | `#A8C6F7` / `#DBECFD` | `#6C93D6` / `#90B4EB` |
| Snow, front / f34 / rear / side | V, h < .45 | S | `#D1E0F4` / `#D4E3F7` / `#D6E5F7` / `#DCEAF9` | `#EBF4FD` / `#EEF5FD` / `#EAF3FD` / `#E8F2FD` | `#BDCFE8` / `#C1D2E9` / `#BBCDE6` / `#BACCE5` |
| Snow mound, front box / exploded | (90,725,210,775) / (240,1170,470,1290) | I+S | `#BCCFEB` / `#C1D2ED` | `#E5F0FC` / `#E7F1FD` | `#81A1D1` / `#90B1D7` |
| Wood, front / f34 / rear / side / r34 | V | W | `#725342` / `#72523F` / `#765746` / `#755442` / `#775542` | `#9A735D` / `#996E56` / `#99745C` / `#99735C` / `#966E57` | `#503A2E` / `#4E382B` / `#4D372B` / `#513A2D` / `#4E372A` |
| Wood, exploded stem / close-up branch | (200,860,530,1140) / (665,842,818,1009) | brown | `#855D44` / `#8A6249` | `#A7795B` / `#A87B5D` | `#604230` / `#644630` |
| Cut ends: thickness close-up / joining surface | (805,1265,838,1325) / (796,905,815,945) | all | `#A87551` / `#BB8760` | `#B17D57` / `#C4936E` | `#A67350` / `#AB805A` |
| Cut ends, hero (top wood band) | front / f34 h .9–1.0 | W | `#BB8A69` / `#B37E5A` | | |
| Rock, front / f34 / rear / side | V | R | `#7E6354` / `#7D6254` / `#775F53` / `#7A5F51` | `#9D8174` / `#9F8071` / `#9C8175` / `#A18373` | `#544339` / `#564338` / `#54433A` / `#56443A` |
| Rock warm (hue ≥ 18°), front / f34 | V | R | `#806252` / `#81624E` | `#A38472` / `#A5836E` | `#584438` / `#584437` |
| Rock cool (hue < 18°), front / f34 | V | R | `#776560` / `#75635E` | `#997F76` / `#937A74` | `#4F3F3C` / `#51403B` |
| Rock, exploded base / underside | (140,1150,520,1300) / (679,1053,930,1182) | brown | `#7B6154` / `#68544B` | `#9E8071` / `#8B756F` | `#544238` / `#5C4B43` |

**Gradients** (medians in five equal steps along each part's axis):

```
leaf base -> tip
  front UL   #3A5D9C #4575BF #4A7AC2 #4978C0 #4878C0
  front R    #2D5290 #3760A0 #4B7BC4 #4D7CC2 #4E7DC1
  front LL   #335791 #4876BC #5585CB #5282C9 #5382C9
  rear R     #355B9B #375FA0 #4372B9 #4472B9 #4472B9
  r34 UL     #2D4F89 #3A65A9 #4A79C3 #598AD2 #5888D2
nodule bottom -> top
  front NR   #6995D9 #8FB7F2 #A4CBFA #BBD9FD #DAEEFD
  f34 NR     #6894D8 #9EC2F2 #A2CAFA #D0E6FD #D9EEFD
  rear NB    #496AA0 #6D98D8 #86AFEB #C4E0FD #D2EBFD
  r34 NR     #7BA8E7 #9DC4FA #ACD0FC #B3D6F7 #BAD5F4
```

**Height bands** (front, per 0.1 h, h 0 → 1; "-" = under 30 px):

```
wood   -       -       #6C5141 #6B4D3B #7D6051 #7A5B48 #674A3B #8A644D #7C593F #BB8A69(cut top)
rock   #775E4E #90766C #7D655C (rock only below h .3)
leaves -       -       -       #335992 #4877BE #4A7AC2 #4373BC #4A7AC2 #6E9BDD
```

**Rock colour by column** (front): f .1–.2 `#544645` (cool, dark), .2–.3 `#6F594F` (cool), .3–.5 `#906B54`–`#92705C`
(warm), .6–.7 `#67524A` (cool), .7–.8 `#806254` (mid), .8–.9 `#8E7166` (cool-light).

### 5.3 How the colour works

**Leaves.**
- One deep-blue family, hue 216–217° in every view, sat 0.60–0.64. Lit facets `#6593D8`–`#6B99DC`, shade
  `#2F5592`–`#305694` (lighting).
- **Base → tip:** the bottom fifth is clearly darker (`#2D5290`–`#3A5D9C`) than the outer three fifths
  (`#4878C0`–`#5382C9`). Part of it is the limb's shadow, but the exploded leaves (no shadow) show it too: paint a
  base-third darkening toward swatch 3 and a mild tip lift toward swatch 2.
- The LL leaf is a touch lighter (`#5585CB` tips) than UL and R: vary per leaf by ±6 levels.

**Ice nodules.**
- Hue 212–216°, sat 0.30–0.40 median, near-white crowns (`#D9EEFD`, sat 0.14). **Bottom → top a strong lift**
  (`#6995D9` → `#DAEEFD`): mostly light (the crown faces up), but the exploded nodules (lit from above too) keep a pale
  crown and a mid-blue lower third, so paint it: lower third toward `#7EA6E6`, crown toward `#CFE5FD`.
- Not self-lit: the shade/lit luminance ratio is 0.61, the leaves' 0.57 (M014's glowing crystal was 0.70 with no
  shade facets below mid). No emission (§7).
- Base nodules: FL is the deepest (`#7DA2E1`, close to the mid swatch), FR and the back pair pale (`#A6C9F6`). Paint
  FL as `ice_deep`, the others as `ice` with deep bottoms.

**Snow.**
- Very pale cool white `#D4E3F7` (hue 214°, sat 0.14); lit facets `#EEF5FD`; its creases and shaded lumps
  `#BCCFE8`–`#C1D2E9` (lighting) and the mound's lower faces against rocks and nodules bluer (`#BCCFEB` median of the
  front mound box, `#90B1D7` exploded shade). Paint a faint blue toward the contacts (position: distance from rocks,
  nodules and the trunk), never by facing.

**Wood.**
- Warm mid brown, hue 21–23°, sat 0.41–0.49. Parts render `#855D44`–`#8A6249`; the hero's median is darker (`#72523F`)
  where the leaves and nodules shade it. The trunk band at h .2–.4 is the darkest (`#6B4D3B`, the snow-collar shadow and
  the leaf shade); the limbs above h .7 lighter (`#8A644D`).
- **Cut ends** (flat joining surfaces, the tall limb's top, the right branch's end, CS's end): pale orange-brown
  `#A87551`–`#BB8760` (hero top band `#B37E5A`–`#BB8A69`).

**Rocks.**
- Two rock colours in about 2 : 1 by area: **warm** brown (`#81624E`, hue 21–24°, sat 0.36–0.40) at the front centre
  and the back; **cool** grey-brown (`#75635E`, hue 11–14°, sat 0.18–0.20) at the left and right. The underside is the
  darkest (`#68544B`).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered medians of **unshadowed** regions (exploded parts, close-ups), then checked against
the hero. `K.sample` kinds: `"vivid"` for the leaves (sat ≥ 0.35); `"brown"` for wood, cut ends and warm rock; `"all"`
on tight boxes for ice, snow and cool rock (the snow's lit faces clip the `"stone"` filter's `mx < 245`; the cool rock's
sat 0.20 fails `"stone"`'s 0.18).

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m028_leaf` | `#4877C0` (exploded `#4573BB` / `#4A7AC4`, close-up `#4B7BC3`; hero `#4776BE`) | leaf middles (t .3–.75) | rough 0.55, spec 0.35 |
| `m028_leaf_deep` | `#355A99` (base fifths `#335791`–`#3A5D9C`; swatch 3 `#3D68A8`) | leaf base third (t < .3) | rough 0.55, spec 0.35 |
| `m028_leaf_light` | `#5383C8` (LL tip fifths `#5585CB`; swatch 2 `#5989CC`) | leaf tip quarter (t > .75), more on LL | rough 0.55, spec 0.35 |
| `m028_ice` | `#A8CDFA` (front `#A9CFFB`, f34 `#A6CCFB`, exploded UR `#AED1FC`; swatch 1 `#B5DBFD`) | nodule belts; FR/BL/BR bodies | rough 0.3, spec 0.5 |
| `m028_ice_pale` | `#CFE5FD` (crown fifths `#D0E6FD`–`#DAEEFD`) | nodule crowns (top 25 %) | rough 0.3, spec 0.5 |
| `m028_ice_deep` | `#7EA6E6` (base nodule FL `#7DA2E1`; nodule bottom fifths `#6995D9`, exploded LL `#98C0F7`) | nodule bottom third; all of FL | rough 0.3, spec 0.5 |
| `m028_snow` | `#D3E2F6` (f34 `#D4E3F7`, front `#D1E0F4`; swatch 4 `#CBDCF3`) | snow body | rough 0.85, spec 0.3 |
| `m028_snow_blue` | `#BCCFEB` (front mound box `#BCCFEB`, exploded `#C1D2ED`) | snow within 0.25 of rocks, nodules and the trunk collar | rough 0.85 |
| `m028_wood` | `#87604A` (exploded `#855D44`, close-up `#8A6249`; swatch `#88624C`) | skeleton | rough 0.9 |
| `m028_wood_dark` | `#5E4433` (parts' shade quartiles `#604230`–`#644630`; hero h .2–.4 band `#6B4D3B`) | crotches, the trunk within 0.25 above the snow collar, limb undersides within 0.3 of a leaf base | rough 0.9 |
| `m028_wood_cut` | `#B07E58` (close-ups `#A87551` / `#BB8760`; hero top band `#B37E5A`) | flat limb-end caps | rough 0.85 |
| `m028_rock` | `#82634F` (hero warm `#81624E`, front `#806252`; exploded `#7B6154`) | warm rocks K1, K2, K7–K9, K11 | rough 0.92 |
| `m028_rock_cool` | `#74625C` (hero cool `#75635E` / `#776560`; swatch 6 `#6A554F`) | cool rocks K3–K6, K10 | rough 0.92 |
| `m028_rock_dark` | `#66524A` (underside `#68544B`; front far-left `#544645`) | rock ground-contact rows, crevices between rocks, the underside | rough 0.95 |

**Calibration warnings:**
- **Leaves:** the front_sheet leaf median must land within 10 of `#4877C0`, hue 214–219°, sat ≥ 0.56; the base fifth
  at least 15 levels darker than the tip fifth. Not navy, not sky blue.
- **Ice:** lit faces sit near the clip (`#DAEEFE`). If crowns wash to pure white, lower the specular, not the key. The
  front_sheet canopy-nodule median within 12 of `#A9CFFB`, and the bottom fifth at least 40 levels darker than the top.
- **Snow vs ice:** the snow must stay whiter and less saturated (sat ≤ 0.18) than the nodules (sat ≥ 0.28), or the base
  nodules melt into the mound.
- **Wood vs rock:** the hero wood median within 12 of `#72523F` (sat ≥ 0.40); warm rocks lighter and greyer
  (`#81624E`, sat ≈ 0.38). The rock band must keep both colours visible (≥ 25 % cool by area).

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Leaves** (field = along-axis t from the construction frame, 0 = base, 1 = tip): t < 0.3 → `leaf_deep` fading to
  `leaf` by t 0.4; t > 0.75 → 40 % toward `leaf_light` (LL 60 %); ±0.06 noise on t; per-leaf Tint offset ±0.03.
- **Nodules** (field = along-axis t, 0 = bottom): t < 0.3 → `ice_deep` fading to `ice` by t 0.45; t > 0.7 →
  `ice_pale`; FL entirely `ice_deep` with a 30 % `ice` crown. Neighbouring facets step one shade at a time (deep ↔ mid
  ↔ pale), never deep straight to pale (M014).
- **Snow:** `snow` body; faces within 0.25 of a rock, nodule or the trunk → 50 % `snow_blue`, within 0.12 → 75 %.
- **Wood:** `wood` base; crotches (within 0.3 of a fork), the trunk from the collar to 0.25 above it, and limb
  undersides within 0.3 of a leaf base → 50 % `wood_dark` fading over 0.25; broad patches (`K.patches` scale 0.6, level
  0.25) between `wood` and a 25 % `wood_dark` mix; flat end caps `wood_cut` (hard). Keep ≥ 60 % of the wood faces plain
  `wood` (024's verifier found 73 % dark mixes).
- **Rocks:** warm or cool per rock; the bottom 25 % of each rock and faces within 0.1 of a neighbour → 50 %
  `rock_dark`; the underside `rock_dark`.
- **Hard edges only** where materials meet: leaf | limb end, nodule | limb or snow, snow | rock, snow | trunk, cut cap |
  bark.

### 5.6 Texture (Tint) and finish

- **Tint** (`tint_var` per piece about 0.03):
  - leaves and nodules: `K.texture` amp 0.02 (the sheet: "no textures"), broad;
  - snow: amp 0.02, scale 0.5;
  - wood: amp 0.04, scale 0.35 (along-limb mottling);
  - rocks: amp 0.05, scale 0.45 (patches about 1 stud);
  - never per-triangle confetti.
- **Finish:**

| Material | Roughness | Specular | Metal | Notes |
| --- | --- | --- | --- | --- |
| Leaf keys | 0.55 | 0.35 | 0 | smooth, slightly waxy facets; the lit facets read paler, not glossy |
| Ice keys | 0.3 | 0.5 (lower if crowns clip) | 0 | icy, smooth; no transparency (Roblox palette export) |
| Snow keys | 0.85 | 0.3 | 0 | matte packed snow |
| Wood keys | 0.9 | normal | 0 | matte bark |
| `wood_cut` | 0.85 | normal | 0 | matte end grain |
| Rock keys | 0.92 | normal | 0 | matte |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Leaves:** front_sheet median within 10 of `#4877C0`; base → tip lift ≥ 15 levels; LL lighter than UL.
- **Nodules:** front_sheet canopy median within 12 of `#A9CFFB`; bottom → top lift ≥ 40 levels; rear NB within 15 of
  `#8EB7EE`.
- **Snow:** front_sheet S median within 8 of `#D1E0F4`, sat ≤ 0.18.
- **Wood:** parts-shot stem median within 8 of `#855D44`; front_sheet wood within 12 of `#725342`, hue 19–25°.
- **Rocks:** warm within 10 of `#806252`, cool within 10 of `#776560`, both present.
- **Shares** per §2.5.

## 6. Joins and contact (no cracks or seams on this sheet)

- **Limbs into the trunk:** every limb starts 0.25 inside its parent on the parent's axis; one exact union per limb;
  crotches clean V's with a knuckle ring.
- **Leaves and nodules onto limb ends:** each base apex sinks 0.12–0.18 into the flat end cap; no visible pegs. The
  leaf's base apex must not be coplanar with the cap: offset it 0.02 off the cap's centre and tilt 3–5°.
- **Trunk into the snow:** the trunk loft continues to z −0.1 inside the mound; the snow meets it in a collar at z
  0.45–0.6 (front h .20 snow V).
- **Base:** rocks overlap the snow lumps by 0.1–0.2 and each other by 0.08–0.15; base nodules sink 30–40 %; everything
  floor-cut at z 0 (`m004.floor_cut`) into one flat underside.
- Overlap everything; exact booleans (pitfall 10).

## 7. Lighting and VFX plan (modeller, stages 5 and 6)

**What the sheet shows:** a sunlit sapling on snow. No glow, light, sparkle, frost mist, falling snow or particles in
any view, and no VFX panel. The ice nodules are pale, not self-lit: their shade facets (`#6995D9`) keep the same
lit/shade ratio as the leaves' (0.61 against 0.57; M014's glowing crystal was 0.70). The notes ask for "simple, solid
colors".

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight:** nothing glows. Emission ≥ 1.0 would export the nodules as flat Neon and erase
  their deep-to-pale facet steps.
- **Studio note (Requires Manual Validation):** check in Studio that the nodule crowns and the snow don't clip to flat
  white under the game sun (Frostpeak's lighting may be brighter and cooler), and that the leaf base → tip step survives
  the palette export.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **Recommended: none.** The sheet shows no effect; WorldModeling §11 says Frost Shrub effects only "if later requested"
  and never concealing the geometry; the other forage shrubs (M017, M018, M022, M024) shipped none. Record "Stage 6
  skipped: sheet shows no VFX".
- **Options** (decision §8.7), if the main session wants frost to read in game:
  - `ore_glint` frost twinkle on the two canopy nodules: colour `["#F2F8FF", "#A8CDFA"]`, `spark_diamond`, rate 0.2,
    size 0 → 0.35 → 0, boxes tight round NR (1.0, 0.0, 3.0) and NB (−1.05, 0.3, 2.6);
  - R08's pair for hit feedback: `harvest_hit` at the front (0, −1.6, 1.8) with ice chips `["#CFE5FD", "#4877C0"]`,
    scale 0.5, and `harvest_deplete` at the foot (0, 0, 0.6).
- **Not recommended:** R08's `vapour` cold mist (it buried R08's trunk in white; it hides geometry), `dust`,
  `crystal_glow` (nothing glows).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by `git grep` of the repo and a search of every sheet .blend, zstd-decompressed
(`m024_study/blendall.py`, run with names `FrostShrub FrostBush FrostShrubNode FrostBushNode FrostBud IcyLeaf
IceNodule …`):
- **R08 kit** (`FlintbornWorldKit.blend`, `art/blender/scripts/kit/R08/frost_shrub.py`, `art/roblox/kit/R08/manifest.json`):
  `FrostShrub` (52 hits in the kit file), `FrostShrubForkedStem`, `FrostShrubIceNodule`, `FrostShrubLeaf`,
  `FrostShrubBase`, `FrostShrubDepleted`, `FrostBud`, `IcyLeaf`; keys `r08_ice` (`#9FC4EE`), `r08_frost_leaf`
  (`#3A66AE`), `r08_twig` (`#684738`), `r08_rock` (`#6A5A50`). (`IceNodule` occurs only inside `FrostShrubIceNodule`.)
- `M.mk` would silently rename a clash to `<name>M028`, so avoid all of these.

**Proposed names.** `FrostBushNode`, `FrostBushStem`, `FrostBushLeaf`, `FrostBushIceNodule`, `FrostBushBase` and the
`m028_` prefix occur nowhere in the repo or any sheet .blend (`FrostBush` 0 hits, `m028_` 0 hits).

| Object | Part | Why |
| --- | --- | --- |
| `FrostBushNode` | hero | `…Node` like `ThornBushNode` / `BerryBushNode` / `FiberPlantNode`; R08 owns `FrostShrub*` (the M024 `ThornBush*` pattern) |
| `FrostBushStem` | Forked Stem (the skeleton, side branch included) | the sheet's word "stem"; R08 owns `FrostShrubForkedStem` |
| `FrostBushLeaf` | Leaf (the UL size) | R08 owns `FrostShrubLeaf` |
| `FrostBushIceNodule` | Ice Nodule (the NR size) | R08 owns `FrostShrubIceNodule` |
| `FrostBushBase` | Base (rock ring, snow, 4 base nodules) | R08 owns `FrostShrubBase` |

- Fallback if the main session prefers the game's id: `FrostShrubNode` is free as an exact name, but the parts would
  need another stem anyway, so `FrostBush*` keeps the set consistent.
- Palette keys `m028_*` (§5.4). Collection `Kit/M028 Frost Shrub`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **4.3 × 3.0 × 3.6** (recommended: H 0.65 C like the berry, fiber and thorn shrubs — `FrostShrub`
   is a Farming node with `ThornShrub`'s stats), or × 1.2 (5.2 × 3.6 × 4.3, the rock ring at shin height, closer to
   the Emberbloom event plant), or R08's scale (10.6 × 7.8 × 8.7).
2. **Proportion source** (§3.2): **the front cell for W : H, the hero for layout; f34 W : H accepted at 1.05–1.20**
   (recommended), or follow the f34's narrower 1.07 (W 4.1; the front render then reads 8 % narrow).
3. **Canopy items** (§3.1): **3 leaves (UL, LL, R) + 2 nodules (NR on the right branch, NB at the back left behind UL)**
   (recommended: satisfies the hero, front, rear, r34 and exploded), or the exploded's literal 2 leaves + 2 nodules (UL
   becomes a nodule: matches the rear and side, changes the hero).
4. **Skeleton:** **one `_stem` builder; trunk column to a fork at z 2.05 with TL, RBr and CS above, LB and RB at
   z 1.15–1.35; the exploded side branch joined to the trunk in the hero and in the part** (recommended), or a
   separate side-branch part plugged into the base as drawn in the exploded.
5. **Pegs, dots and sockets:** **not modelled; flat end caps in `wood_cut`; no holes** (recommended: notation only).
6. **Hero packaging:** **one closed shell** (recommended: STAGES default): base first, then stem, then leaves and
   nodules one at a time.
7. **Stage 5/6:** **no emission, light or VFX** (recommended: the sheet shows none; matches the other forage shrubs), or
   the `ore_glint` frost twinkle, or R08's `harvest_hit` / `harvest_deplete` pair (§7.2).
8. **Exports:** the hero plus 4 parts (`…Stem`, `…Leaf`, `…IceNodule`, `…Base`) (recommended: the sheet's "reusable
   modular parts (leaves, ice nodules, stem, base)"). R08's `FrostBud` / `IcyLeaf` drops and `Depleted` state are not on
   this sheet; not built unless asked.
9. **Comparison cameras** (§2.5, §3): `front_sheet (0, 12)`, `f34_sheet (0, 12)`, `rear_sheet (180, 12)`,
   `r34_sheet (180, 14)`, `side_sheet (90, 12)` (not mirrored), kit top + `top_tilt (0, 70)`; kit front34, rear34 and
   underside as self-consistency; a parts shot `(−20, 15)`. All with the floor hidden for measuring.
10. **Leaf recipe:** **the 6-sided hexagonal shard (4 rings + 2 apexes, 48 tris), parallel belt, sharp tip, section
    0.7 × width** (recommended), or a 2-ring bicone (36 tris; loses the parallel belt and reads as a tent).
11. **Nodule recipe:** **M014's hull of staggered rings, dissolved to 20–30 broad facets** (recommended), or an ico-1
    (R08's "balloons").
12. **Base nodules:** **4 (FL, FR, BL, BR)** (recommended: the front, rear and side cells each show two), or 2 (the
    exploded base's visible pair).
13. **Names** as proposed.

## 9. Pitfalls to avoid

1. **Balls, tents or tulips.** Every leaf is a long hexagonal shard: parallel belt (t .3–.6), a sharp tip (77–88° in
   outline), a blunt-pointed base (100–111°), L : W 1.85–2.05, a ridge on its broad face. Every nodule is a faceted gem
   with points at both ends (100–120°), L : W 1.5–1.7. No icospheres, no subdivision, no smoothing.
2. **A low splayed nest.** The trunk is a **column**: 1.55 studs of bare trunk from the snow collar (z 0.5) to the fork
   (z 2.05). The low limbs leave at z 1.15–1.35, never at the foot. Above the fork: one tall limb at 20–30° from
   vertical, one right branch at 15–22° above horizontal, a centre limb behind NR. Check the wood runs (§2.1).
3. **Hidden skeleton.** Wood is 26 % of every view, the top included. The tall limb's flat top must be on the front
   silhouette (h .93–.96, f .40–.45); the right branch's cut end must stick out past NR (f .85–.87).
4. **Pipes and smooth curves.** Limbs are straight 8-sided segments with kinks and knuckles, tapering 10–15 %, with flat
   square-cut ends in the pale cut colour.
5. **NB showing from the front, or UL from the rear.** NB sits behind UL (Y +0.1 … +0.45) and no higher than z 3.25;
   UL ≤ 0.05 of the rear silhouette (§3.1).
6. **A closed rock wall.** The ring is open at the front centre where the snow reaches the ground; the waist at h .3 is
   ≤ 0.62 W; the rocks are small (0.38–0.6 tall), the snow mound shows above and between them.
7. **Snow and ice melting together.** Snow sat ≤ 0.18, ice ≥ 0.28; the base nodules stand out as blue gems on white.
8. **Colour by facing.** The nodules' pale crowns and deep bottoms are partly light: paint along each part's axis t and
   by position only; `K.check` facing correlation < 0.5.
9. **Wood too dark.** Keep the bark warm (hue 19–25°, sat ≥ 0.40); `wood_dark` only in crotches and at the collar;
   ≥ 60 % of wood faces plain `wood`.
10. **Exact booleans.** Overlap everything: limbs from inside their parent, leaf and nodule bases 0.12–0.18 into end
    caps (never coplanar), rocks into snow lumps; add pieces one at a time and save between; remove slivers with m011's
    `_tidy` / `_desliver`; run `M.audit` for bowtie vertices at leaf bases and snow/rock seams.
11. **Comparing the wrong views.** The f34 is the front drawn 10 % narrower; the r34 the rear likewise; the top is
    tilted and rotated (§3).
12. **Side-view handedness.** The kit side camera at az 90 sits at +X, so screen right is the model's back; the side
    cell agrees (R leaf at screen left, the CS cut end at screen right). Its forward pale nodule is the UL slot drawn as a
    nodule: don't move parts to fit it (§3.4).
13. **Measuring the ground shadow.** Hide the floor or use L/I/S/W/R pixels only; `cls3` treats the warm-grey shadow
    as background, a neutral studio shadow may not be (024's verifier lesson).
14. **Naming clashes** with R08's `FrostShrub*`, `FrostBud`, `IcyLeaf` (§8). Don't edit shared helpers (`kit_models.py`,
    `kit_mcp.py`, `build_kit.py`, `lib/vfx.py`); put new helpers in `m028.py`. No commits, pushes or exports in the
    modeller's stages.

## Decisions (main session, 2026-10-28)

All recommendations are accepted:
1. Size: 4.3 W × 3.0 D × 3.6 H (±0.25 / ±0.3 / ±0.2).
2. Canopy: 3 leaves plus 2 nodules. The second nodule sits behind the upper-left leaf, so the front hides the nodule, the rear hides the leaf, and the rear three-quarter shows both.
3. Proportions: W:H comes from the front cell and the layout from the hero view. The three-quarter render is accepted at W:H 1.05–1.20.
4. Side cell: don't move parts to fit its forward nodule.
5. Top cell: judged by counts and shares only.
6. Four base nodules.
7. No effects.
8. Hero plus the 4 parts; no drops and no depleted state.
9. Comparison cameras: front, three-quarter, rear and side at 12° elevation (rear three-quarter at 14°), all with the floor hidden.
10. Names as proposed (`FrostBush*`). For the spec's other decisions, follow its own recommendations.

The stem rises as a visible column (1.55 studs bare) before it splits, as the spec's wood-run and limb-angle targets require. 024 failed as a low splayed nest.

## Stage 1. Modelling (modeller, 2026-10-28)

Builder `art/blender/kit/mcp/m028.py` (`build()`). In the background session on port 9877 the build takes about 40 s,
or about 60 s with every render. Every part comes from its own function, and the hero is assembled from the same
functions.

**`skeleton()`** (hero and `FrostBushStem`):
- An 8-sided trunk column runs from z −0.1 to the fork at z 2.05, then makes a short taper into the crotch. Its radius
  is:
  - 0.47 at the flare;
  - 0.40 at z 0.6;
  - 0.375 at z 1.25;
  - 0.34 at the fork.
- The limbs are 8-sided and kinked (M024's `tube`), with knuckle rings and flat end caps:

| Limb | What it is | Where it goes |
| --- | --- | --- |
| LB | the left branch | leaves at z 1.3; carries two stubs, LBup (for NB) and LBfr (for UL) |
| RB | the right low limb | leaves at z 1.15; has a small up-stub, RBup |
| TL | the tall limb | goes up-left to its cut top at (−0.3, −0.1, 3.42) |
| RBr | the right branch | runs nearly level, then rises to its cut end at X 1.7, z 2.62 |
| NRs | NR's stub | — |
| CS | the centre limb | goes back, behind NR |

**`leaf_mesh()`** builds a 6-sided hexagonal shard:
- Section: width × 0.7 width, with a ridge vertex on each broad face and a flat side facet.
- Rings, at t (half-width fraction):
  - .10 (0.55);
  - .30 (1.0);
  - .46, a lerp ring for the colour ramp;
  - .62 (0.98);
  - .82 (0.60).
- The base and the tip are apexes, for 60 tris.
- Ring A is 0.55, wider than the spec's 0.30, so the outline at t .1 and .2 meets the measured profile (.29 / .40
  against .30 / .44).

**`nodule_mesh()`** is M014's hull of staggered rings:
- Rings at t .15, .38, .62 and .84, with radii .45, .95, 1.0 and .64, plus sector jitter.
- Dissolved at 12°, then BEAUTY-triangulated.
- Canopy gems have 6 points per ring: 36–38 merged facets, 42–46 tris.
- Base gems have 5 points per ring: 24–27 facets, 36–40 tris.
- The crown ring is 0.64, not 0.50, so NR's top is as broad as the sheet's (front profile at f .70–.80).

**Base:**
- Eleven rocks on an oval of rx 1.58, ry 1.28, open at the front. Each rock is a `_dome` hull of 16 points:
  - a flat bottom sunk 0.08;
  - a quiet four-point top;
  - an 8° dissolve.
- A flat snow pad plus five snow lumps, each a dome hull dissolved at 5°.
- Four base gems (FL, FR, BL, BR), half sunk.

**Union and cleanup:**
- The union is guarded and exact, one shell at a time, in this order: skeleton, leaves and nodules, snow, base gems,
  rocks.
- Every union passed with no retries and no failures: hero 36 shells, Stem 10, Base 21.
- Then, in order:
  - The floor cut uses `_floor_cut`, a scanfill cap. M004's `holes_fill` filled a cut loop nested inside another
    twice, which made 3–15 crossing floor faces and 5–14 inverted faces.
  - A guarded 4° limited dissolve, delimited by MATERIAL.
  - M024's clean, finish and polish.
  - `M.fix_bowties`.

**Hero size: 4.51 W × 2.99 D × 3.60 H.** W was raised from 4.3 to 4.5 (the LL and R tips at ±2.26), which is inside
the +0.25 tolerance. At 4.3 the front_sheet W : H was 1.117, under the 1.12–1.25 target. It now reads 1.171.

### Measured against the sheet (`m028.measure()`)

Measured on the long-lens `*_sheet` renders, with the floor hidden and the study's `cls3` masks on both images. Sheet
values are in brackets.

| View | W : H | L | I | S | I+S | W | R | leaves |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| front_sheet = f34_sheet (0, 12) | 1.171 (front 1.189 / f34 1.069) | .281 (.274) | .197 (.225) | .100 (.114) | .297 (.339) | .289 (.260) | .134 (.127) | 3 (3) |
| rear_sheet (180, 12) | 1.108 (1.198) | .194 (.165) | .332 (.295) | .061 (.118) | .393 (.413) | .277 (.270) | .137 (.152) | 3 (2) |
| r34_sheet (180, 14) | 1.103 (1.052) | .192 (.246) | .336 (.252) | .061 (.101) | .397 (.353) | .272 (.265) | .138 (.136) | 3 (3) |
| side_sheet (90, 12) | 0.757 (0.788) | .170 (.047) | .330 (.327) | .046 (.160) | .376 (.487) | .233 (.253) | .222 (.213) | 2 (1) |
| top_tilt_sheet (0, 70) | 1.524 (1.034) | .113 (.240) | .359 (.313) | .166 (.125) | .525 (.438) | .254 (.261) | .108 (.061) | 1 (3) |

**Front top profile**, f 0 to 1 in steps of 0.05:
- ours: .42 .50 .54 .90 .88 .87 .81 .73 .94 .97 .89 .77 .87 .95 .90 .93 .96 .78 .61 .59 .58
- sheet: .46 .51 .56 .91 .88 .86 .83 .76 .93 .96 .86 .74 .85 .94 .99 1.0 1.0 .77 .59 .58 .56
- The three crown masses are there, with dips at f .35 (.73) and f .55 (.77).
- The tall limb's flat top is on the silhouette, at .94–.97 for f .40–.45.
- NR's dome is the weak point: .90–.96 at f .70–.80 against the sheet's .99–1.0, at worst −0.09 at f .70.

**Front width per height:**
- h .1: 0.79 (target 0.76–0.88);
- h .3: 0.59 (the waist must stay ≤ 0.62);
- h .5: 0.91 (target ≥ 0.86).

**Front wood runs:**

| Height | Ours | Sheet |
| --- | --- | --- |
| h .2–.4 | one trunk run, .42–.58 (.16 W) | .41–.57 |
| h .50 | two runs, .29–.41 and .45–.60 | .28–.39 and .47–.60 |
| h .60 (the fork) | .47–.68 | .51–.69 |
| h .65 | .48–.77 | .50–.78 |
| h .75 | TL .45–.61 and RBr .77–.87, separate | .46–.54 and .80–.87 |
| h .80–.95 | TL alone, moving left from .43–.53 to .41–.47 | .44–.53 to .42–.46 |

That gives a trunk column of 1.55 studs of bare wood, a low split at h .45–.50 and the fork at h .60–.65.

**Rear:** the V of two prongs at h .90–.95 is weak. TL is a single run at .49–.59, and CS ends lower, at h .85
(f .34–.37). See the notes for the verifier.

## Stage 2. Optimisation and cleanup

| Object | Tris | Size (studs) | Shells | Non-manifold / boundary | Bowtie verts | Self-intersections | Inverted | Thin (< 5°) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FrostBushNode (hero) | 1644 / 4000 | 4.51 × 2.99 × 3.60 | 1 | 0 / 0 | 0 (2 fixed) | 0 | 0 | 6 (floor cap, 4.1–5.0°) |
| FrostBushStem | 404 / 1000 | 2.82 × 1.32 × 3.49 | 1 | 0 / 0 | 0 | 0 | 0 | 0 (min 5.8°) |
| FrostBushLeaf | 60 | 1.65 × 0.59 × 0.85 | 1 | 0 / 0 | 0 | 0 | 0 | 0 (min 14.9°) |
| FrostBushIceNodule | 46 | 0.87 × 0.87 × 1.45 | 1 | 0 / 0 | 0 | 0 | 0 | 0 (min 21.9°) |
| FrostBushBase | 944 / 1000 | 3.69 × 2.99 × 1.23 | 1 | 0 / 0 | 0 (2 fixed) | 0 | 0 | 6 (floor cap) |

**Tris before the union: 1348.**

| Piece | Tris |
| --- | --- |
| skeleton | 408 |
| leaves | 3 × 60 |
| canopy gems | 46 + 42 |
| snow | 38 + 5 × 34 |
| base gems | 40 + 40 + 40 + 36 |
| rocks | 11 × 28 |

**Every object** has:
- zero wire edges, loose verts, zero-area faces, n-gons and duplicate verts;
- outward normals;
- its origin at the bottom centre (0, 0, 0);
- transforms applied.

**The six thin faces are all in the flat underside cap at z 0.** They are scanfill fans from nearly collinear rim
verts. `_floor_needles` flips floor-floor edges, but none of these has a better diagonal. Merging their short rim edges
was tried and removed, because it folded a wall to 0.4°. The thin faces are invisible, they lie in one plane, and none
has zero area.

## Stage 3. UV

Smart UV (angle 45, margin 0.008), then M012's `_uv_unfold`. Every object has 0 overlap pairs, 0 flipped islands and a
minimum island gap of 0.016.

| Object | Islands | Density spread | Conformal stretch p95 |
| --- | --- | --- | --- |
| hero | 410 | 0.84–1.04 | 1.004 |
| Stem | 89 | 1.0 | 1.008 |
| Leaf | 15 | 1.0 | 1.0 |
| Nodule | 11 | 1.0 | 1.066 |
| Base | 218 | 1.0–1.03 | 1.004 |

The exporter writes its own palette UVs.

## Stage 4. Materials, colour and texture

### Keys

The keys came from three passes (the comments in `PALETTE` record each one):
1. `m028.calibrate()` on the dome against the spec's 5.4 targets.
2. Each family corrected in linear light by the sheet / ours ratio of the front_sheet medians (rear at half weight).
3. The snow-blue key made bluer.

| Key | Hex | Roughness | Specular |
| --- | --- | --- | --- |
| `m028_leaf` / `_deep` / `_light` | `#3D6DB6` / `#2A5393` / `#4678BE` | 0.55 | 0.35 |
| `m028_ice` / `_pale` / `_deep` | `#9DCDFF` / `#BADEFF` / `#769AD0` | 0.3 | 0.5 |
| `m028_snow` / `_blue` | `#A9B8CD` / `#99ADC9` | 0.85 | 0.3 |
| `m028_wood` / `_dark` / `_cut` | `#705647` / `#4F3D30` / `#906F54` | 0.9 / 0.9 / 0.85 | 0.3 |
| `m028_rock` / `_cool` / `_dark` | `#755A50` / `#6A5A5B` / `#5E4B4A` | 0.92 / 0.92 / 0.95 | 0.3 |

### Blending

Colour comes from position fields only. Mix keys are 25 / 50 / 75 % (`_mix` quantises to quarters), with ±0.05–0.06
noise on t.

- **Leaves** (t along the leaf's axis):
  - deep at the base, stepping 100 / 75 / 50 / 25 % over t < .42;
  - the plain key across the belt;
  - toward light over the tip, 25 then 50 % (LL 75 %).
- **Nodules:**
  - Canopy gems are deep below t .38, the key in the middle and pale above t .52.
  - The base gems FR, BL and BR are deep below t .5 with only a 25 % pale crown.
  - FL is deep with a 25 % ice crown.
  - The exported Nodule part has 25 % ends only. The full ramp on an upright gem gave a K.check correlation of 0.79.
- **Snow** (distance to the rocks, gems and trunk):
  - under 0.12: 75 % blue;
  - under 0.25: 50 %;
  - under 0.32: 25 %.
- **Wood:**
  - Forks and crotches are 50 % dark within 0.22 and 25 % within 0.38.
  - The hero only also darkens the snow collar (below z 0.95 / 1.12) and the leaf bases.
  - Broad noise patches add 25 %.
  - The bare ends (TL, RBr, CS, RBup) get pale cut caps. The join ends that carry leaves and gems are bark in the hero
    and cut on the Stem part.
- **Rocks:**
  - warm or cool per rock;
  - 50 / 25 % dark at the feet (by z) and in crevices within 0.06 / 0.14 of a neighbour.
- **Underside cap:** `m028_rock`, which keeps it out of the facing check.

### Tint and checks

- **Tint** is broad noise, never per face: amp 0.02 for leaf, ice and snow, 0.04 for wood, 0.05 for rock, with ±3–4 %
  per piece.
- **K.check facing correlation:** hero 0.00, Stem 0.34; Base, Leaf and Nodule 0.00. No `kit_shading_ok` override.

### Re-measured against the sheet (front_sheet; sheet in brackets)

- Leaves `#4778C4` (`#4877C0`) ✓
- Wood `#725341` (`#725342`) ✓
- Rock `#7E6255` (`#7E6354`) ✓
- Canopy ice, I+S `#A5D5FC` (`#A9CFFB`) ✓
- Snow `#D5E6FC` (`#D1E0F4`): +4 / +6 / +8, at the edge of tolerance.
- I class (base gems plus shaded snow) `#90B1D9` (`#95B5E5`): B −12, a little greyer.
- Parts shots: leaf `#4477C1` (exploded `#4573BB` / `#4A7AC4`) ✓; stem `#7D5B47` (`#855D44`), R −8.

**Rear and r34 are backlit by the kit studio sun.** The snow there reads `#B0C0D6` against the sheet's `#D6E5F7`, and S
drops to .06. The sheet lights every cell from the front, so this comes from lighting, not paint.

## Stage 5. Lighting

Skipped (decision 7): the sheet shows no glow, so there are no emissive keys and no light.

**Check in Studio:**
- the nodule crowns (`#BADEFF` key) and the snow don't clip to flat white under Frostpeak's sun;
- the leaf base-to-tip step survives the palette export.

## Stage 6. VFX

Skipped (decision 7): the sheet shows no glow, sparkle, mist or particles, so there are no sockets. Renders still use
`vfx=True`.

## Modeller's notes for the verifier

**Cameras.** Compare with the `*_sheet` renders (3× lens, floor hidden):
- `f34_sheet` and `front_sheet` are both (0, 12), per decision 3.
- `side_sheet` is (90, 12); screen right is the back.
- `top_tilt_sheet` is (0, 70).

`m028.measure()` gives the numbers above, and `m028.compare()` writes `M028_sheet_compare.png`.

**Known differences the decisions accept:**
- **Side:** our UL leaf stands where the sheet's side cell draws a pale nodule, so side L is .17 against .05
  (decision 4).
- **Top:** judged by counts and shares only (decision 5). The top_tilt camera doesn't match the sheet's rotated
  drawing, and our leaves merge into one mask component there.
- **Rear V:** CS ends behind NR at (0.64, 0.55, 2.98), so the rear's +X prong is low (h .85). Raising it to the
  sheet's h .95 at f .44 would put a second prong on the front silhouette at f .58, where the front draws a dip
  (spec 3.7).
- **Rear and r34 lighting:** they are backlit, so snow and rock read darker and S is low. That is lighting, not paint.

**Small leftovers:**
- NB's crown shows a sliver above the UL leaf in front_sheet (≤ 0.03 W).
- Front I+S is .297 against .339 (−4.2 points), and wood is .289 against .260 (+2.9).
- The front NR dome is 0.04–0.09 low at f .70–.80.
- Six needle triangles (4.1–5.0°) sit in the flat underside cap.
- The trunk is a straight column. The sheet's sways slightly and flares wider into the snow.

## Stage 7 — Verification (round 1)

Fresh verifier, read-only. Background session on port 9877 with `wip/M028_verify.blend`; nothing saved, `build()` not
called. Fresh renders went to a scratch folder (`M.MODEL_RENDERS` redirected), not to this folder. Every number below was
re-measured: topology with my own bmesh, BVH and ray-parity code, and colours and shares with the study's masks (`m028.classes`)
on both the sheet and my renders.

**Verdict: PASS, 7.5 / 10. No blockers.** The sheet's read is all there and the mesh is clean:
- a bare brown trunk column with a fork, a tall up-left limb and a right branch with cut ends;
- three blue hexagonal shards and two pale gems;
- a snowy rock ring that is open at the front, with four base gems.

What's left is colour hue on the rocks and some leftovers on the rear and top that the decisions accept.

### Technical (re-measured)

| Object | Tris | Size (studs) | Shells | NM edges / verts / boundary | Self-hits | Inverted (ray parity) | Faces under 5° | UV overlap / flipped / min gap | Density | Stretch p95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FrostBushNode | 1644 / 4000 | 4.51 × 2.99 × 3.60 | 1 | 0 / 0 / 0 | 0 | 0 | 6, all in the z 0 floor cap (4.09–4.96°); off the floor, min 5.07° | 0 / 0 / 0.016 | 0.84–1.04 | 1.004 |
| FrostBushStem | 404 / 1000 | 2.82 × 1.32 × 3.49 | 1 | 0 / 0 / 0 | 0 | 0 | 0 (min 5.84°) | 0 / 0 / 0.016 | 1.0 | 1.008 |
| FrostBushLeaf | 60 | 1.65 × 0.59 × 0.85 | 1 | 0 / 0 / 0 | 0 | 0 | 0 (min 14.9°) | 0 / 0 / 0.016 | 1.0 | 1.0 |
| FrostBushIceNodule | 46 | 0.87 × 0.87 × 1.45 | 1 | 0 / 0 / 0 | 0 | 0 | 0 (min 21.9°) | 0 / 0 / 0.016 | 1.0 | 1.066 |
| FrostBushBase | 944 / 1000 | 3.69 × 2.99 × 1.23 | 1 | 0 / 0 / 0 | 0 | 0 | 5, all in the floor cap (min **3.16°**) | 0 / 0 / 0.016 | 1.0–1.03 | 1.004 |

**Size.** The decided size is 4.3 × 3.0 × 3.6. The hero is W +0.21 (inside +0.25), D −0.01 and H 0.

**Other checks:**
- Every object has 0 n-gons, wire edges, loose verts and duplicate verts.
- No custom normals, no smooth faces, no modifiers, no parent or children.
- Transforms are applied and the origin is at the bbox bottom centre (bbox x and y centred on 0, z min 0).
- Volumes are positive (normals outward).
- No interior faces: one manifold shell, 0 crossing face pairs and 0 odd-parity faces.
- The hero underside is 110 coplanar faces, all pointing straight down, 7.72 stud².

**The floor needles.** They are flat, coplanar, non-zero area (min 0.00017 stud²) and point straight down, so they can't shade
or be seen. I judge them harmless.

**Materials:**
- 10 keys plus quarter mixes; every slot is used.
- No emission anywhere and no VFX sockets (decision 7).
- `K.check` reports no problems.
- Area-weighted facing correlation (key luminance against normal z), whole object: hero 0.19, Stem 0.35, Base 0.15,
  Leaf −0.03.

### View comparison (sheet → ours, front_sheet / rear_sheet / r34 / side / top at the decided cameras, floor hidden)

| View | W : H | L | I + S | W | R | Leaf components |
| --- | --- | --- | --- | --- | --- | --- |
| front | 1.189 → 1.174 | .274 → .281 | .339 → .297 | .260 → .289 | .127 → .134 | 3 → 3 |
| f34 | 1.069 → 1.174 (accepted 1.05–1.20) | .281 → .281 | .331 → .297 | .261 → .289 | .126 → .134 | 3 → 3 |
| rear | 1.198 → 1.108 | .165 → .194 | .413 → .392 | .270 → .277 | .152 → .137 | 2 → 3 |
| r34 | 1.052 → 1.103 | .246 → .192 | .353 → .397 | .265 → .272 | .136 → .138 | 3 → 3 |
| side | 0.788 → 0.757 | .047 → .170 (decision 4) | .487 → .376 | W + R .466 → .455 | | 1 → 2 |
| top_tilt (70) | 1.034 → 1.524 | .240 → .113 | .438 → .525 | .261 → .254 | .061 → .108 | 3 → 1 (merged) |
| top (89) | | .240 → .124 | .438 → .562 | .261 → .143 | .061 → .172 | 3 → 1 (merged) |

**Front.** All shares are within ±4, and I+S is −4.2, just inside its ±5.

**Front skeleton.** The trunk column, splits and limbs match the sheet:

| Height | Ours | Sheet |
| --- | --- | --- |
| h .25–.40 | one trunk run, .42–.59 | .38–.59 |
| h .50 | two runs, .29–.41 and .45–.61 | .28–.39 and .47–.60 |
| h .60 (fork) | .47–.68 | .51–.69 |
| h .75 | TL .45–.61 and RBr .77–.87, separate | .46–.54 and .80–.87 |
| h .80–.95 | TL alone, moving left, .43–.53 → .41–.47 | .44–.53 → .42–.46 |

- The tall limb's flat top is on the silhouette (.95–.97 at f .40–.45).
- The dips are at f .35 (.73 against .76) and f .55 (.77 against .74).
- The waist at h .3 is .59 (≤ .62 ✓), h .5 is .91 (≥ .86 ✓) and the base at h .1 is .79 ✓.

**Front components:**
- UL: f .13–.36, h .57–.90 (sheet .13–.37, .53–.90).
- LL: f 0–.29, h .37–.56 (sheet 0–.27, .39–.56).
- R: f .60–1.0, h .35–.61 (sheet .64–1.0, .35–.59).
- NR: f .61–.81, h .69–.94, share **.062 against the sheet's .103** (sheet .60–.83, .67–1.0).
- The ring is open at the front centre and the snow reaches the ground there ✓.

**Rear.**
- NR is at screen left and high, R at screen left, LL at screen right and NB at screen right and high ✓.
- The UL leaf shows round NB: its visible component is **3.4 %** of the silhouette, inside the spec's ≤ 5 %, but it reads
  as "gem on a blue leaf" where the sheet has one big pale gem.
- NB is .066 of the silhouette against the sheet's .133, with its top at h .86 against .98.
- **No V.** At h .90–.95 there is one TL run (.49–.59 / .51–.59) against the sheet's two (.43–.50 | .50–.57). The rear top
  profile has no notch at f .60 (.94 against the sheet's .50). CS ends as a cut stub at h .85, f .34–.37.

**Side.** The decision 4 conflict, accepted:
- The UL leaf stands up the front edge, so the top profile at f .25–.45 is .93–1.0 against .71–.96. The width at h .4 is
  .64 against .36.
- The R leaf, seen nearly end-on, reads as a squat hexagon.
- The wood mask's largest-component rule fails on our side render (trunk and rock merge into one shade), so I compared
  W + R together.

**Top.** By counts:
- 3 leaves are visible, but UL and LL merge into one component;
- 2 pale gems ✓;
- wood crosses the centre ✓;
- rock is at the rim ✓.

By shares:
- L is about half the sheet's (−12 points);
- I+S is +9 to +12 (outside ±6).

The UL and R leaves stand broad-face to the front, so from above they are seen edge-on.

### Colours (study masks, medians; sheet → ours, difference in R/G/B)

| Region (front_sheet unless noted) | Sheet | Ours | Δ | Result |
| --- | --- | --- | --- | --- |
| Leaves, all | `#4877C0` | `#4778C4` | −1 / +1 / +4 | ✓ (hue 216.2 → 216.8°, sat .62 → .64) |
| Leaf base → tip, UL | `#3A5D9C` → `#4878C0` | `#3965A8` → `#6996E1` | tip +33 / +30 / +33 | the tip fifth is too light (the lit tip plus 50 % light key) |
| Leaf base → tip, R / LL | `#2D5290` → `#4E7DC2` / `#335792` → `#5382C9` | `#3560A5` → `#4575BE` / `#2B4F8A` → `#4B7BC5` | ≤ ±21 | ✓ (base darker than tip on each) |
| Canopy ice (NR, I+S above h .45) | `#A9CFFB` | `#A5D5FC` | −4 / +6 / +1 | ✓ |
| NR bottom → top fifth | `#638FD2` → `#DAEFFD` | `#566F8B` → `#BBE1FE` | bottom −13 / −32 / −71 (shadowed by RBr, grey); crown −31 / −14 / +1 | crown a little cyan, not near-white |
| Rear NB (canopy ice) | `#8EB6EE` | `#9DCAFB` | +15 / +20 / +13 | just outside the spec's 15 (NB paler than the sheet's) |
| Base gem FL / FR area (I) | `#84A7DF` / `#9BBDED` | `#91ADD4` / `#8EB5DA` | +13 / +6 / −11 ; −13 / −8 / −19 | a bit greyer than the sheet; still read as blue on white |
| Snow (S, base) | `#D1E0F4` (sat .13) | `#D5E6FC` (sat .14) | +4 / +6 / +8 | ✓ (at the edge) |
| Wood | `#725342` (22°, .42) | `#725341` (23°, .43) | 0 / 0 / −1 | ✓ |
| Stem part against exploded stem | `#855D44` | `#7C5B47` | −9 / −2 / +3 | ✓ (just outside 8 on R) |
| Cut ends (wood, top 10 % band) | `#BB8966` | `#745644` | −71 / −51 / −34 | ✗: the TL cut top doesn't show pale from the front |
| Rock, all | `#7E6354` | `#7E6255` | 0 / −1 / +1 | ✓ |
| Rock, centre (warm) | `#81614C` (hue 23.6°) | `#876354` (hue 17.9°) | +6 / +2 / +8 | warm rock 6° too red |
| Rock warm share (hue ≥ 18°) | 63 % | 27 % (rear 6 %) | | the two-tone reads as one pinkish brown |
| Cool rock key | swatch `#6A554F` (13°) | key `#6A5A5B` (**356°, mauve**) | | renders `#6A5757` (6°) at the rear right |

The rear and r34 snow (`#AFC0D6` against `#D6E5F7`) and rear wood (`#664D3E` against `#765746`) are darker. The kit sun
backlights the rear cameras while the sheet lights every cell from the front, so this is lighting, not paint. The left/right
lightness of the front rocks is swapped against the sheet (ours lit from the left) for the same reason.

### Itemised findings (all minor; no blockers)

1. **Rock hues (minor, colour).**
   - The cool key `m028_rock_cool` `#6A5A5B` has a hue of 356° (mauve), against swatch 6 `#6A554F` / rendered cool
     `#75635E` at 12–13°.
   - The warm key `#755A50` (16°) renders at 18° against the sheet's 23.6°.
   - Together they melt the warm/grey-brown two-tone into one pinkish brown (warm share 27 % against 63 %).
   - Fix: set `ROCK_COOL` to about `#6B5953` (hue about 13°, the same luminance) and `ROCK` to about `#78594A` (hue about
     21°). Re-check that front rock C reads hue 21–24° and the warm share is ≥ 50 %.
2. **NR undersized in the front (minor).**
   - The front share is .062 against .103 and the top .91–.96 against 1.0 at f .70–.80.
   - On the sheet NR is the tallest thing; ours sits below TL's top.
   - Fix: scale NR about 1.15 along its axis and raise its top apex to about z 3.7 (H stays inside 3.6 + 0.2).
3. **Rear NB and UL (minor, inside the ≤ 5 % rule).**
   - The UL leaf shows round NB (3.4 %).
   - NB is half the sheet's rear area (.066 against .133) and lower (h .86 against .98).
   - Fix, if a round 2 is run: move NB about 0.1 to −X and +0.1 to +Y and grow it about 1.15, so it covers UL from the
     rear. Keep its front peek ≤ 0.03 W.
4. **Rear V (minor, spec 3.7 conflict).**
   - CS ends as a stub at h .85, f .34–.37, against a second prong at h .90–.95, f .41–.47.
   - Optional fix: end CS at about (0.35, 0.55, 3.2), behind NR's left edge from the front, and confirm that the front dip
     at f .55 stays ≤ .80.
5. **TL cut top not visible from the front (minor).** The front's top wood band is `#745644` against the sheet's pale cut
   face `#BB8966`. Tilt TL's end cap about 25° toward −Y, so the `wood_cut` face shows in front_sheet the way the sheet's
   slanted cut does.
6. **Top shares (minor, decision 5).** L is −12 and I+S is +9 to +12 on the top and top_tilt cells, because the UL and R
   leaves stand broad-face to the front. The sheet's top cell is internally inconsistent (spec 3.5). Accept, or tilt R's
   broad face about 15° more toward +z.
7. **Leaf UL tip too light (minor).** The tip fifth is `#6996E1` against `#4878C0`. Drop UL's tip mix from 50 % to 25 %
   `leaf_light`; keep LL at 75 %.
8. **NR crown cyan, not near-white (minor).** The top fifth is `#BBE1FE` against `#DAEFFD`. The `ice_pale` key `#BADEFF`
   could go toward `#C9E6FF`, but watch the clipping that the stage 5 Studio note mentions.
9. **Wood dark share (minor).** On the hero, plain `wood` is 51 % of the bark area (the spec asks for ≥ 60 %), but the
   rendered wood median matches the sheet exactly, so this is cosmetic.
10. **Floor needles (minor, accepted).**
    - The hero has 6 floor-cap faces at 4.1–5.0°.
    - The Base part has 5 at **3.16**–4.61°; the spec's stage 2 table lists 6 without the 3.2° minimum.
    - All are coplanar, point down and can't be seen.
11. **Within-family facing correlation (minor, noted).**
    - Rock 0.75 (dark feet by z) and ice 0.50 on the hero, and 0.76 on the exported Nodule (deep and pale ends along an
      upright axis).
    - These come from position fields (height, axis t) on upright pieces, not from normal-driven paint. The whole-object
      values pass `K.check`.
12. **Base gems paired (minor).** In the rear and side, each pair of base gems stacks into a two-gem cluster. The sheet's
    rear shows one per side. Acceptable under decision 6.
13. **NB crown sliver** above UL in front_sheet (≤ 0.03 W), as the modeller noted. Accepted.

**Requires manual validation (Studio):**
- the rock two-tone after the palette export;
- that the nodule crowns and snow don't clip under the Frostpeak sun;
- that the leaf base-to-tip step survives.

## Main session after verification round 1 (2026-10-29)

Applied minor 1: `ROCK` #755A50 → #78594A and `ROCK_COOL` #6A5A5B → #6B5953, so the rocks read as the sheet's warm and grey-brown pair instead of one pinkish brown. The rebuild in the kit file gave a hero of 1644 tris, one shell, 0 bowties, `K.check` clean. Export: 0 problems.
