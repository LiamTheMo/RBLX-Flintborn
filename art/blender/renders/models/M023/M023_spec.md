# 023 Clay Deposit — spec

Reference: `art/blender/assets/references/023.png`. The sheet's own title is "CLAY DEPOSIT", with "ENVIRONMENT ASSET —
STYLIZED LOW-POLY • MODULAR PARTS • GAME READY LOOK" at the top right and the footer "FLINTBORN — INDIVIDUAL MODEL STUDY,
PAGE 25/132". INDEX.md row 23 calls it "Flintborn Clay Deposit Model Study". The image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m023.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender; the main session does stage 7 (verification), then exports and
commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7).

Sheet text:
- **Header:** "CLAY DEPOSIT"; "ENVIRONMENT ASSET"; "STYLIZED LOW-POLY • MODULAR PARTS • GAME READY LOOK".
- **View labels:** "FRONT THREE-QUARTER" (printed "THREE-QUARTEЯR", a typo), "REAR THREE-QUARTER", "FRONT", "SIDE",
  "REAR", "TOP".
- **Modeling notes:**
  - "Built from simple, chunky low-poly shapes."
  - "Broad, flat-shaded faces. No texture noise." (but see §3.8)
  - "Separate parts: main clay lobe, additional clay lobes, rocks, and soil base."
  - "Rocks are embedded into soil base."
  - "Keep silhouettes readable from all angles."
  - "Consistent with FLINTBORN stylized aesthetic."
  - "Clean topology, solid colors, game-ready look."
- **Material palette:** Clay (Main), Clay (Secondary), Soil Base, Rocks.
- **Exploded labels:** Main Clay Lobe, Clay Lobe (×2 drawn, two different shapes), Rocks (x5), Soil Base. Dashed
  arrows drop every part onto the base; small dark pins on the base top mark the attach points.
- **Close-ups:** "Part Close-Up" ("Flat shaded faceted faces", the main lobe); "Base Underside" ("Flat underside for
  placement"); "Junction Detail" ("Clay overlaps soil base"; "Rock embedded into base").
- **Game context:** `src` and GDD.md have no clay node (GDD only uses "Clay" as a tribe colour). The old R07 kit sheet
  has `ClayDeposit` (built 9.5 × 8.1 × 5.0: 5 lobes, 8 pebbles, `harvest_hit` + `harvest_deplete`, plus
  `ClayDepositMainClayLobe`, `ClayDepositClayLobe`, `ClayDepositSoilBase`, `ClayLump` drop and `ClayDepositDepleted`),
  which owns the `ClayDeposit*` and `ClayLump` names (§8). `MODEL_PROGRESS.md` row R07 flags that build as "rounded
  blobs (ref flat-topped faceted lobes); smooth dome base".

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is
`#F1ECE6` (241, 236, 230), tolerance 14. The masks are `cls()` in `m.py` (HSV):
- **K, clay:** hue ≤ 30° or ≥ 345°, sat ≥ 0.56, v ≥ 0.35.
- **S, soil:** hue ≤ 40° or ≥ 345°, sat 0.24–0.70, v 0.18–0.80, and not K.
- **R, rock:** sat < 0.24, v 0.33–0.80.
- **O, other:** dark creases and edges; not counted in the shares.
- Known leaks: warm-shaded rock faces fall into S, and a few deep-shade soil pixels into R, so R is ±1.5 points. The
  rosy lump in the top view (§3.4) is S.

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m023_study\`.
Run with the scratch venv `..\venv\Scripts\python.exe` (uv venv of `C:/Users/Orang/.local/bin/python3.14.exe` with
Pillow 13 and numpy 2.5; the uv-managed interpreter itself refuses package installs).
- **Helpers:** `m.py` (masks `cls()`, view boxes `V`, `preview()`), `zoom.py` (crop + upscale), `bb.json` (silhouette
  boxes).
- **Measurements:** `measure.py` → `measure_out.txt` (shares, top/bottom profiles, clay-bottom line, width per
  height, rock components); `soilcol.py` (soil band under the clay per column); `expl.py` (exploded and close-up part
  boxes); `outline.py` (top-view outline radius by azimuth).
- **Colour:** `samp.py` (swatches, view medians, f34 deciles), `samp2.py` (exploded parts, close-ups, hero lobes,
  thirds), `samp3.py` (third lit quartiles, single rocks, soil bands, the rosy lump).
- **Names:** `blendall.py` (every sheet and wip `.blend`, zstd-decompressed).
- **Crops:** `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `cu_part.png`,
  `cu_under.png`, `cu_junc.png`, `pal.png`, `notes.png`; grids `g_*.png` (10 % grid on the silhouette bbox, red =
  centre lines); mask previews `cls_*.png`.
- **Zooms:** `z_top_right.png` (the rosy lump and right rocks), `z_f34_left.png` (left rocks and the pad skirt),
  `z_expl_base.png`, `z_expl_lobes.png`, `z_expl_rocks.png`.
- **To run the scripts on our renders,** point `R` (in `m.py`) at the render, set `P` to its background colour and
  re-run `measure.py` (it rewrites `bb.json`).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a resource node / environment prop). Hero budget 4000 tris, each part under 1000.
  The plan in §4.3 lands at about 1300–1800.
- **Overall read (check this first).** One low, round **soil pad** carrying a heap of **five chunky, broad-faceted
  orange clay lobes**, with **about ten small warm-grey rocks** embedded round the rim and in the notches:
  - the **main lobe** (the biggest and tallest) sits centre-back;
  - a **big squat lobe at the front-right** overlaps the main lobe's front;
  - a **small low lobe at the front-left**;
  - a **tall small lobe at the left** and a **small lobe at the back-right**, which show behind and beside the main
    lobe from the front.
  - The pad is a thick faceted slab with a sloped skirt and a flat underside; its brown top shows as a ring round the
    lobes. It must read as one clay outcrop on a soil bed, not five balls on a plate.
  - Hero shares: clay 70.5 %, soil 22.7 %, rock 6.7 %.
- **Focal silhouettes, in order:**
  1. The main lobe's broad crown (a flat-ish sloping top over steep sides), the highest point at f .52.
  2. The front-right lobe's wide squat dome (0.42 W) in front of it.
  3. The stepped outline down to the left (BL, FL) and right (BR), then the pad's flat skirt with rocks at both ends.
- **Target size: about 10.0 W × 9.6 D × 4.75 H studs** (H = 0.86 of the 5.5-stud character), pad 9.8 × 9.4, rocks
  0.95–1.35 across. Tolerances W ±0.4, D ±0.4, H ±0.2. Decision §8.1.
  - **How it was derived.** The sheet has no character. The anchor is the rocks: hero rocks measure 0.08–0.12 W
    (38–57 px of a 478 px hero), and the kit's pebble scale (R07 pebbles 1.0–1.4, W01 pebbles, M013 foot rocks) puts
    them at about 1.0–1.3 studs, so W ≈ 10. The height then follows from the hero and front cells (§3.1): main-lobe top
    z 4.68 (f34, e 14°) and 4.9 (front, e 9°).
  - **Why this size.** A waist-to-chest-high outcrop the character can stand beside and strike; the node footprint
    sits with the common nodes (M001 Stone 8.7 × 6.1 × 5.0, M006 Copper 8.6 × 8.0 × 5.9) and M020 (9.0 × 8.5 × 4.3).
    R07 `ClayDeposit` was 9.5 × 8.1 × 5.0, so the scale stays familiar.
  - **Depth compromise.** The cells disagree on depth: the top view is deeper than wide (W : D 0.925), the side cell
    is narrow (it implies D ≈ 8.1), and the hero's pad ellipse fits a round pad. D 9.6 (W : D 1.04) splits it
    (§3.5).
- **Build frame:** front −Y, +X right, ground z 0, origin = the pad centre on the ground. That is close to the bbox
  bottom centre already; stage 2 re-centres exactly.

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | Clay K | Soil S | Rock R | Scale (px/stud) |
| --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (15,115,540,435) | 46–524 × 126–409 | 1.689 | 70.5 % | 22.7 % | 6.7 % | 47.8 |
| Rear three-quarter (545,115,1010,435) | 561–995 × 147–409 | 1.656 | 71.1 % | 23.3 % | 5.7 % | 43.4 |
| Front (12,480,295,700) | 17–284 × 509–662 | 1.745 | 71.6 % | 22.3 % | 6.1 % | 26.7 |
| Side (296,480,523,700) | 307–512 × 520–659 | 1.475 | 65.9 % | 29.2 % | 4.9 % | 21.4 (D 9.6) |
| Rear (524,480,790,700) | 535–782 × 510–660 | 1.647 | 65.1 % | 27.9 % | 7.1 % | 24.7 |
| Top (796,478,1012,700) | 811–995 × 483–682 | 0.925 (W : D) | 55.0 % | 35.5 % | 9.5 % | 18.4 across, 20.7 down |

- **Verifier tolerance:** shares ±4 points (R ±2); positions ±0.06 of W/H unless stated.
- **Elevations** from the pad's bottom ellipse (ends of the bottom profile against its front point, for a near-round
  pad): **f34 ≈ 14°** (0.21 H = 59 px over a 239 px half-width), front ≈ 9°, side ≈ 10°, rear ≈ 9°, r34 ≈ 17°.
- **Rear box:** the cell's right divider sits at x 794, so the box stops at 790.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .24 | .36 | .51 | .63 | .67 | .69 | .79 | .89 | .93 | .95 | .99 | 1.0 | .98 | .93 | .81 | .75 | .75 | .66 | .53 | .39 | .25 |
| Front | .18 | .33 | .45 | .58 | .61 | .65 | .82 | .89 | .92 | .95 | .99 | .99 | .96 | .91 | .79 | .69 | .70 | .66 | .46 | .31 | .17 |
| Side | .19 | .32 | .35 | .65 | .78 | .90 | .95 | .98 | 1.0 | 1.0 | .99 | .96 | .89 | .78 | .66 | .68 | .65 | .61 | .48 | .29 | .17 |
| Rear | .17 | .37 | .51 | .59 | .62 | .64 | .79 | .91 | .95 | .99 | 1.0 | .97 | .93 | .90 | .87 | .71 | .65 | .62 | .51 | .35 | .18 |
| r34 | .27 | .43 | .48 | .64 | .77 | .81 | .79 | .86 | .95 | .98 | 1.0 | .98 | .96 | .93 | .90 | .77 | .65 | .66 | .59 | .41 | .27 |
| Top (h = back) | .64 | .71 | .78 | .83 | .85 | .88 | .90 | .93 | .97 | .98 | .99 | .99 | .98 | .94 | .94 | .92 | .88 | .83 | .78 | .75 | .48 |

**Bottom profiles** (lowest silhouette pixel; the pad's front ellipse):

```
f34    .20 .14 .09 .06 .04 .03 .02 .01 .01 .01 .00 .00 .02 .02 .02 .04 .05 .07 .08 .12 .22
front  .13 .10 .07 .04 .03 .02 .01 .01 .01 .00 .01 .01 .01 .01 .01 .02 .03 .04 .05 .08 .14
side   .13 .07 .06 .03 .02 .01 .01 .01 .00 .00 .00 .00 .00 .01 .00 .01 .01 .03 .04 .08 .13
rear   .13 .08 .05 .03 .02 .01 .01 .00 .00 .00 .01 .01 .01 .01 .01 .01 .02 .03 .05 .07 .13
r34    .25 .16 .09 .07 .06 .04 .03 .02 .00 .00 .00 .00 .00 .01 .02 .03 .04 .06 .08 .13 .24
```

**Clay bottom line** (lowest clay pixel per column, every 0.05 f; where the lobes meet the soil or a rock; `--` = no
clay):

```
f34    --  --  .39 .38 .47 .16 .15 .15 .01*.02*.17 .15 .13 .13 .13 .04*.06*.25  --  --  .23
front  --  --  .36 .43 .16 .16 .15 .15 .20 .15 .13 .12 .12 .11 .11 .13 .18 .23  --  .08* --
```
(* single stray pixels of the clay mask in shade; ignore.) So FL and FR sit on the pad top at h .13–.16, BL at h
.38–.47 behind the left rocks.

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .01@.53 .83@.09 .98@.00 .96@.02 .87@.07 .82@.10 .73@.13 .56@.27 .40@.30 .30@.36 .02@.54
r34    .21@.39 .83@.09 .94@.02 .98@.01 .93@.03 .81@.11 .75@.15 .60@.17 .50@.23 .33@.37 .02@.47
front  .04@.45 .90@.05 .98@.01 .93@.03 .85@.09 .77@.12 .69@.17 .54@.27 .39@.30 .30@.36 .01@.53
side   .30@.40 .95@.04 .98@.01 .90@.04 .78@.14 .74@.15 .72@.13 .51@.17 .42@.21 .34@.25 .09@.39
rear   .15@.32 .93@.04 .98@.01 .91@.05 .85@.06 .80@.10 .69@.17 .47@.27 .40@.31 .30@.35 .02@.47
top    .03@.56 .59@.19 .80@.10 .93@.03 .99@.01 .98@.01 .98@.00 .92@.05 .75@.12 .47@.30 .02@.52
```

**Soil band under the clay** (`soilcol.py`; lowest S/R pixel – where clay starts, as fractions of H; K = clay above):

```
f34    .03: .14-.33 | .06: .14-.37 | .10: .10-.39K | .20: .04-.47K | .30: .02-.15K | .50: .01-.17K | .60: .02-.13K | .70: .02-.13K | .90: .08-.53 | .94: .12-.40 | .97: .16-.34
front  .03: .12-.30 | .06: .09-.34 | .10: .07-.36K | .20: .03-.16K | .30: .01-.15K | .50: .01-.14K | .60: .01-.12K | .70: .01-.11K | .90: .06-.47 | .94: .08-.39 | .97: .12-.29
```
The visible pad (skirt plus top strip) is 0.11–0.15 H at the front centre and 0.17–0.19 H at the ends (front cell
0.63 and 0.97 screen studs), which fits a **rim about 0.8 high** plus a narrow top strip (§1.4).

**Lobe extents** (read on the grids `g_*.png`; f across, h up; the parts of a lobe hidden behind another are not
included):

| View | Main | Big near-right (FR) | Small near-left (FL) | Far-left (BL) | Far-right (BR) |
| --- | --- | --- | --- | --- | --- |
| f34 | f .26–.73, h ≥ .38–1.0 (crown f .34–.65 at h .89–1.0) | f .46–.88, h .13–.62 | f .23–.44, h .15–.42 | f .07–.27, h .37–.70 | f .71–.86, h .53–.75 |
| Front | f .24–.70, h ≥ .40–1.0 | f .40–.88, h .13–.60 | f .17–.40, h .17–.42 | f .07–.22, h .37–.63 | f .72–.87, h .45–.71 |
| r34 | f .32–.77, h ≥ .45–1.0 | big near-left f .14–.60, h .10–.56 | near-right f .60–.87, h .19–.54 | far-right f .78–.92, h .38–.65 | far-left f .15–.32, h .45–.80 |
| Rear | f .27–.73, h ≥ .30–1.0 | far-left f .06–.26, h .30–.65 | far-right f .74–.90, h .35–.63 | near-right f .62–.87, h .22–.55 | near-left f .19–.44, h .20–.43 |
| Side | f .13–.70, h ≥ .43–1.0 | hidden (behind FL) | right f .63–.92, h .25–.65 | near centre f .23–.70, h .17–.60 | hidden (behind main) |
| Top (h = back) | f .20–.79, h .40–.90; centre .49, .66 | f .40–.92, h .08–.56; centre .66, .32 | drawn as a **grey rock** f .16–.33, h .17–.35 | f .05–.27, h .33–.57; centre .16, .45 | drawn as a **rosy-brown lump** f .80–.94, h .64–.80; centre .88, .72 |

The r34, rear and side columns are mapped to the hero's lobe names by the camera analysis in §3.2–§3.4.

**Rock components** (`measure.py`; centre (f, h); extent; R-mask pixels):

| View | Rocks |
| --- | --- |
| f34 | far-left upper (.05, .26; f .02–.12, h .25–.40), far-left lower (.11, .09; h .09–.20), front-left on the skirt (.16, .18; f .12–.20, h .10–.25), left on the pad top between BL and FL (.20, .39; f .15–.27, h .30–.47), front centre at the rim (.52, .07; f .46–.58, h 0–.14), right upper (.89, .51; f .85–.92, h .47–.56), right lower (.92, .38; f .87–.95, h .30–.42): **7** |
| Front | the same 7 at the same fractions (front centre at f .42–.53) |
| r34 | left 3 (.04, .38), (.12, .47), (.13, .22); front 2 (.63, .22) on the pad top, (.67, .08) at the rim; right 2–3 (.90, .23), (.95, .36): **8** |
| Rear | left (.09, .17); front rim 2 (.42, .04), (.59, .05); centre on the pad top at the main lobe's foot (.54, .29; the biggest, 0.14 W); right 2 (.92, .21), (.93, .33): **7** |
| Side | left 3 (.05, .26), (.15, .14), (.16, .34); right 2 (.77, .29), (.92, .32): **5** |
| Top (h = back) | back rim (.55, .95), back-left (.24, .82), left (.14, .66), front-left (.24, .25; = FL, §3.4), right (.92, .54), right-back rosy (.88, .72; = BR, §3.4), front edge specks (.36, .05), (.12, .17): **6 grey + 2 lumps** |

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, governs; `g_f34.png`).** It is **not** a 3/4 view. It is an aligned, elevated front
view (az ≈ 0, e ≈ 14°): the pad's bottom ellipse is symmetric (.20 / .22 at the ends), and every lobe's screen x
matches its top-view X at az 0 (main f .50 ↔ top .49; FR .67 ↔ .66; BL .17 ↔ .16; §3.1).
- **Main lobe:** a big faceted boulder centred at f .50, its crown a broad sloping top (f .34–.65 at h .89–1.0) over
  steep facetted sides; about 11 outline corners; the facets are big (edges about 1.0–1.6 studs) and several are
  split into 2–4 triangles of slightly different tone.
- **FR lobe:** a wide squat dome (0.42 W, top h .62) right of centre, overlapping the main lobe's lower front; it sits
  on the pad top (bottom at h .13). Its crown is a broad near-flat face.
- **FL lobe:** a small low dome (0.21 W, top h .42) left of centre on the pad top, in front of the main lobe.
- **BL lobe:** at the far left, a tall small lobe (top h .70) behind the left rocks; its bottom is hidden at h .37.
- **BR lobe:** at the far right, a small lobe (top h .75) peeking behind FR and beside the main lobe.
- **Pad:** a brown band all round: the sloped skirt is a ring of irregular triangles (edges about 0.5–0.9 stud), the
  top shows only as a narrow strip at the left and right.
- **Rocks:** 7: two stacked at the far left on the ground, one on the front-left skirt, one on the pad top in the notch
  between BL and FL, one at the front rim (sunk into the skirt, bottom on the ground), two stacked at the right.
- **Crease lines:** the lobe joins read as dark creases (O mask) at f .30, .43–.50 (the FL/FR/main triple point) and
  .72.

**Front (`g_front.png`).** The same drawing as the f34 at a lower elevation (≈ 9°): lobe extents and rock fractions
match within 0.06 (§1.2), and its W : H is 1.745 against 1.689.

**Rear three-quarter (`g_r34.png`).** The f34 drawing **mirrored** (§3.2): top profile mostly within 0.08 of the
f34's reversed, shares within 1 point, the big squat lobe now left of centre and the small low lobe right of centre.

**Rear (`g_rear.png`).** Main in the centre with two lobes on each side (a low near one and a higher far one) and a
big rock on the pad top at the main lobe's back foot; two rocks on the back rim. A true rear camera (az 180) on the
§2 layout reproduces it (§3.3).

**Side (`g_side.png`).** Three lobes: the main at the left, a big low lobe at the centre front, a mid-height lobe at
the right; rocks at both ends. It fits a camera at **−X** (az 270, screen right = front), not the kit side at +X
(§3.3). It is drawn narrower than the other cells (W : H 1.475; §3.5).

**Top (`g_top.png`, `z_top_right.png`; image top = back).** A roundish 13–14-sided pad (outline radius 4.6–5.3 studs,
one flatter sector at the back-left, az 105–135° at 4.3–4.5; `outline.py`); the main lobe centre-back, the FR lobe
front-right, the BL lobe at the left; a grey rock where FL should be and a rosy-brown faceted lump where BR should be
(§3.4); grey rocks round the rim. The pad's front skirt shows as a darker band at the bottom (the camera is tilted a
little toward the front).

**Close-ups.**
- **Part Close-Up** (666,742,961,938), 295 × 196 px: the main lobe alone. A wide boulder with a flat underside, a
  broad sloping top made of 4–5 big faces, a ring of large triangles down the sides and a short lower band of facets
  that tucks in to the flat bottom. "Flat shaded faceted faces." Its colour bands are lighting only (§5.3).
- **Base Underside** (684,990,976,1131): the pad seen from below: a **flat bottom face** (lit evenly, `#947151`) inside
  a **chamfer band** that rises to the skirt; rocks at both ends overhang the rim and reach the ground. "Flat underside
  for placement."
- **Junction Detail** (655,1210,895,1472): a clay lobe comes straight down onto the soil top with no gap or lip ("Clay
  overlaps soil base"); a big rock sits in a hollow of the soil against the lobe's foot, its lower third buried; a
  smaller, browner rock behind it; the soil's skirt is a stack of broad irregular facets. A small dark speck marks the
  "Rock embedded into base" leader (the exploded attach pin).

### 1.4 Parts (Exploded Construction (15,745,640,1245), `expl.png`)

Scale: the exploded parts are drawn larger than the base relative to the hero (main lobe 0.75 of the base width
against 0.47 in the hero; rocks 0.13–0.27 against 0.10–0.13). **The hero governs every size**; the exploded gives
shapes and the part list.

#### Soil Base (191,1097,504,1228), 313 × 131 px (`z_expl_base.png`)

- **Shape:** a thick, low, irregular 12–14-sided slab: a flat bottom, a short chamfer at the bottom edge (the
  underside close-up's band), a **sloped skirt** of broad irregular triangles, and a gently domed top with a few broad
  low bumps. Its outline matches the top view's (§1.3).
- **Hero size:** 9.8 × 9.4; rim top **z 0.8**; the top rises to about z 1.05 under the lobes (hidden).
- **Construction:** `_soil_base(seed)`:
  - outline: 14 vertices, radius 4.7 (X) / 4.5 (Y) with ±4 % jitter by sector, a flatter back-left sector
    (az 105–135° at 0.93 R) and a slight bulge at the front-left (az 205–230° at 1.04 R), taken from `outline.py`;
  - rings (from the ground up): bottom z 0 at 0.95 R (the flat bottom), chamfer z 0.22 at 1.0 R, skirt middle z 0.5 at
    0.985 R (±0.06 radial jitter so the skirt breaks into irregular triangles), rim top z 0.8 at 0.95 R (±0.05 z),
    inner top z 0.95 at 0.65 R, crown z 1.05 at 0.3 R, centre fan;
  - beauty triangulation, a few flipped diagonals by seed (the sheet's irregular skirt triangles); flat bottom as one
    fan; no smoothing.
- **Triangles:** 14 × 5 bands × 2 = 140 + crown fan 14 + bottom 12 → **about 165**.

#### Main Clay Lobe (227,746,462,898), 235 × 152 px; Part Close-Up (666,742,961,938)

- **Shape:** a chunky boulder with a **flat bottom**, steep faceted sides and a **broad sloping crown** of 4–5 big
  faces; about 20–24 broad faces in all, with the largest faces split into 2–4 triangles that differ slightly in
  normal (the sheet's subtle within-face facets). Silhouette 10–12 corners from any side. Not a ball, not a jewel.
- **Hero size:** **4.7 W × 4.2 D × 4.0 tall** (base z 0.75, top z 4.75). The exploded and the close-up draw it much
  squatter (about 0.45 h/W); the hero needs 0.85 to reach its crown height (§3.6).
- **Construction:** `_lobe(size, seed, rings=MAIN_RINGS)` via `K.hull_rock(..., keep_bottom=True)`:
  - rings `(0.0, 0.86, 8), (0.18, 1.0, 9), (0.48, 0.97, 9), (0.76, 0.78, 8), (0.93, 0.48, 6), (1.0, 0.18, 3)`, jitter
    0.08, `lean` about (−0.08, 0.06) so the crown slopes down to the front-right as drawn;
  - then poke the 6–8 largest faces with the centre raised 2 % R (the within-face facets), like M019's lump recipe;
  - **about 100 tris**.

#### Clay Lobe (×2 drawn): left (150,895,289,991) 139 × 96 px, W/H 1.45; right (391,887,519,991) 128 × 104 px, W/H 1.23 (`z_expl_lobes.png`)

- **Left "Clay Lobe" = the squat type** (the hero's FR and FL): a wide low dome, flat bottom, a broad near-flat crown
  face, sides of big triangles.
- **Right "Clay Lobe" = the tall type** (the hero's BL and BR): taller, tilted, with a ridge running over the top (a
  rounded wedge).
- **Construction:** the same `_lobe()` with two ring sets:
  - `SQUAT_RINGS` `(0.0, 0.88, 8), (0.22, 1.0, 8), (0.55, 0.9, 8), (0.85, 0.6, 6), (1.0, 0.22, 3)`: about 30 points,
    poke 4–6 faces → **about 70 tris**;
  - `TALL_RINGS` `(0.0, 0.9, 7), (0.3, 1.0, 7), (0.62, 0.88, 7), (0.88, 0.55, 5), (1.0, 0.15, 2)`, `lean` 0.12 toward
    the main lobe: about 28 points → **about 60 tris**.

#### Rocks (x5): (248,986) 84 × 70, (466,1043) 74 × 65, (153,1050) 69 × 59, (359,1043) 57 × 43, (400,1014) 42 × 34 px (`z_expl_rocks.png`)

- **Shape:** squat faceted domes with flat bottoms (screen W/H 1.14–1.33, so true h/w about 0.75–0.85), 14–20 facets,
  a small top cluster of faces; warm grey.
- **Five variants** (widths in the exploded's ratio, scaled to the hero): **A 1.35, B 1.2, C 1.1, D 0.95, E 0.75**;
  h = 0.8 w.
- **Construction:** `_rock(w, seed)` via `K.pebble`-style rings `(0.0, 0.92, 6), (0.4, 1.0, 6), (0.8, 0.7, 5),
  (1.0, 0.25, 3)` with `keep_bottom=True`, jitter 0.12: **about 36 tris** each. The hero places 11 instances (§2.3),
  each a variant with its own seed and yaw.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, origin = pad centre). The f34 camera is aligned (az 0), so screen
x = plan X (47.8 px/stud) and screen up s = z cos 14° + (Y + 4.7) sin 14° (s in studs from the front-bottom point).
Plan Y comes from the top view, `Y = (h − 0.5) × 9.4`, pulled about 0.3 toward the centre for tall objects (the top
camera magnifies them, §3.4).

### 2.1 Pad and lobes

| Piece | Base centre (x, y), base z | Size W × D × tall (top z) | Yaw | Sheet evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| Soil base | (0, 0), 0 | 9.8 × 9.4 × 0.8 at the rim (1.05 crown) | — | f34 W, bottom ellipse; top outline | flat back-left sector at az 105–135° |
| Main | (−0.05, 1.1), 0.75 | 4.7 × 4.2 × 4.0 (4.75) | +15° | f34 f .26–.73, crown h 1.0 (z 4.68 at e 14°); top centre (.49, .66) | the tallest; crown slopes to the front-right |
| FR, front-right | (1.7, −1.7), 0.6 | 4.2 × 3.8 × 2.4 (3.0) | −20° | f34 f .46–.88, top h .62, bottom h .13 (front foot at y −3.6); top centre (.66, .32) | squat type; overlaps the main lobe's front by about 0.6 |
| FL, front-left | (−1.9, −2.4), 0.6 | 2.1 × 2.0 × 1.5 (2.1) | +30° | f34 f .23–.44, top h .42, bottom h .15; top grey rock at (.24, .25) | squat type; touches FR's left flank and the main lobe |
| BL, left | (−3.2, −0.3), 0.7 | 2.2 × 2.1 × 2.5 (3.2) | +70° | f34 left edge f .07 (x −4.3), top h .70; top centre (.16, .45) | tall type, leaning in toward the main lobe |
| BR, back-right | (2.7, 1.9), 0.7 | 2.0 × 2.0 × 2.3 (3.0) | −60° | f34 f .71–.86 (right edge x 3.6), top h .75; top rosy lump (.88, .72) | tall type; mostly hidden from the front |

- **Sinking:** each lobe's base is 0.25–0.35 below the local pad top (the "Clay overlaps soil base" join). Lobes that
  touch overlap 0.3–0.6 so the union gives clean creases.
- **Expected hero:** X −4.95 … +4.95 (pad and side rocks), Y −4.75 … +4.75, z 0 … 4.75 → **10.0 × 9.6 × 4.75**.
  - **f34_sheet (0, 14):** W : H 1.62–1.72 (sheet 1.689, predicted about 1.66).
  - **front_sheet (0, 9):** W : H 1.70–1.85 (sheet 1.745, predicted about 1.79).
  - **Top:** W : D 1.00–1.08 (sheet 0.925; known miss, §3.5).

### 2.2 Silhouette checks per lobe (f34_sheet render against the f34 cell, ±0.06)

| Lobe | f extent | top h | bottom h (visible) |
| --- | --- | --- | --- |
| Main | .26–.73 | 1.0 at f .52–.55 | hidden |
| FR | .46–.88 | .62 | .13 |
| FL | .23–.44 | .42 | .15 |
| BL | .07–.27 | .70 | .37 (behind the rocks) |
| BR | .71–.86 | .75 | hidden behind FR |

### 2.3 Rocks (11 instances of the 5 variants)

| Rock | Centre (x, y), base z | Variant (w) | Sheet evidence | Seat |
| --- | --- | --- | --- | --- |
| R1 far-left upper | (−4.45, 1.0), 0 | A 1.35 | f34 f .02–.12, h .25–.40; top left (.14, .66) | on the ground against the skirt, 0.3 into it |
| R2 far-left lower | (−4.5, −2.4), 0 | D 0.95 | f34 h .09–.20 | on the ground against the skirt |
| R3 front-left | (−3.4, −3.4), 0.3 | C 1.1 | f34 f .12–.20, h .10–.25; top speck (.12, .17) | on the skirt slope, a third buried |
| R4 left notch | (−3.0, −1.6), 0.85 | A 1.35 | f34 f .15–.27, h .30–.47 | on the pad top between BL and FL, touching both (the Junction Detail) |
| R5 front centre | (0.2, −4.5), 0 | B 1.2 | f34 f .46–.58, h 0–.14; front cell f .42–.53 | at the rim, half in the skirt |
| R6 right lower | (4.3, 0.2), 0.2 | D 0.95 | f34 f .87–.95, h .30–.42; top (.92, .54) | at the rim |
| R7 right upper | (3.9, 2.0), 0.55 | C 1.1 | f34 f .85–.92, h .47–.56 | on the pad top by the rim, against BR |
| R8 back rim right | (0.9, 4.4), 0 | C 1.1 | rear (.42, .04); top (.55, .95) | at the rim |
| R9 back rim left | (−0.8, 4.4), 0 | D 0.95 | rear (.59, .05) | at the rim |
| R10 back-left | (−2.7, 3.4), 0.3 | B 1.2 | top (.24, .82) only | on the skirt |
| R11 main's back foot | (−0.4, 3.3), 0.85 | A 1.35 | rear (.54, .29), the rear cell's biggest rock | on the pad top against the main lobe |

- **Embedding:** every rock is sunk 25–35 % of its height into the soil ("Rocks are embedded into soil base"); rocks on
  the ground at the rim also cut 0.2–0.4 into the skirt. None float, none stand only on a point.
- **From f34_sheet:** R1–R7 visible (7, as the sheet). R8–R11 hidden or nearly so.

## 3. View conflicts and resolutions

### 3.1 The "front three-quarter" is an elevated front view; the front cell is the same drawing

- **Evidence.** Every lobe's screen x in the f34 equals its top-view X at az 0 (main .50/.49, FR .67/.66, BL .17/.16);
  the bottom ellipse is symmetric. The front cell has the same lobes and rocks at the same fractions (±0.06) at a lower
  elevation (9° against 14°).
- **Resolution.** Compare the f34 cell with an extra **`f34_sheet (0, 14)`** and the front cell with
  **`front_sheet (0, 9)`**. The kit **front34 (−28, 12)** and **front (0, 4)** have no exact sheet counterpart:
  self-consistency only. The hero governs (WorldModeling §1.1).

### 3.2 The rear three-quarter is the f34 mirrored

- **Evidence.** Its top profile matches the f34's reversed within 0.08 at 19 of the 21 points (worst 0.11 at f .70;
  §1.2); shares within 1 point;
  the lobe extents mirror the f34's (big squat lobe f .14–.60 against FR mirrored .12–.54; far-right .78–.92 against
  BL mirrored .73–.93; far-left .15–.32 against BR mirrored .14–.29). A real back-right camera would hide FR and FL
  behind the main lobe.
- **Resolution.** Compare the r34 cell with the **f34_sheet render flipped left-right** (shares ±4, profile ±0.08,
  5 lobes, 7–8 rocks). The kit `rear34 (152, 12)` is self-consistency only (it is the main check on the back rocks and
  BR).

### 3.3 Rear and side: real cameras, but the side is from the left

- **Rear.** A camera at +Y (az 180, e 9) sees BR near-low at the left, BL near-low at the right, FR and FL high and far
  at the sides, the main lobe centred, and R11 at the main lobe's foot: the rear cell's layout. Compare with an extra
  **`rear_sheet (180, 9)`**: shares ±5, 5 lobes, profile ±0.1, R11 centred on the pad top.
- **Side.** The cell shows the main lobe at the **left**, a big low lobe in front at the centre, and a lobe at the right.
  With the main lobe at the back (y +1.1), only a camera at **−X** (az 270, screen right = front) puts it left; BL is
  then the near centre lobe and FL the right one, with FR and BR hidden. The kit `side (90, 4)` sits at +X (screen
  right = back) and shows the mirror arrangement with FR and BR. Compare with an extra **`side_sheet (−90, 10)`**:
  shares ±5, 3 lobes, rocks at both ends. Kit side: self-consistency.

### 3.4 Top view: FL drawn as a rock, BR as a rosy lump

- **Evidence.** The top shows orange only for the main lobe, FR and BL. At FL's place (.24, .25) it draws a **grey
  rock** 1.7 across; at BR's place (.88, .72) a **rosy-brown faceted lump** (`#BB7B5C`, sat 0.51, between clay and
  soil). Every elevation view shows five orange lobes. The top also draws everything about 1.2× larger relative to the
  pad than the hero (main 0.58 W against 0.47; FR 0.52 against 0.42), the usual magnification of a perspective camera
  above.
- **Resolution.** Five orange lobes (hero governs). Judge the top by the pad outline, the main/FR/BL lobe centres
  (±0.07), FL and BR positions (±0.12), and grey rocks round the rim; record "FL and BR are clay, the top draws a rock
  and a brown lump" as a known miss. Lobe sizes in the top: ±25 %.

### 3.5 Depth: top deeper than wide, side narrower

- **Evidence.** Top W : D 0.925 (D ≈ 10.8 for W 10, partly the visible front skirt); side W : H 1.475 implies D ≈ 8.1
  (with H 4.75); the hero's bottom ellipse at e 14° fits a round pad (D ≈ W).
- **Resolution.** D 9.6 over the rocks (pad 9.4). The side_sheet render will read about 1.74 against 1.475 (+18 %) and
  the top about 1.04 against 0.925 (+12 %); accept both and record them.

### 3.6 Exploded and close-up against hero: the main lobe's proportions

- **Evidence.** The exploded main lobe and the part close-up are wide and flat (screen W/H 1.55 and 1.51, true h/W about
  0.45); the hero's main lobe must rise from the pad (z 0.75) to the crown (z 4.68–4.9), h/W about 0.85. The exploded
  also draws every part 1.5–2× bigger relative to the base.
- **Resolution.** The hero governs: 4.7 × 4.2 × 4.0. Keep the close-up's character: a **flat bottom, a broad sloping
  crown of 4–5 big faces, and big side triangles**, so a parts shot reads like the close-up even though it is taller.

### 3.7 Rocks: "(x5)" against 7–11 in the views

- The exploded labels five rock parts (five sizes); the hero shows 7, the r34 8, the rear 7, the top 6 plus the two
  lumps. **Resolution:** five variants, 11 instances (§2.3), so every view's count lands within ±1.

### 3.8 "Solid colors, no texture noise" against the user's blended-colour rule

- The user's rule wins, but this sheet is almost flat: one clay hue (15–17°) everywhere; the lobes' top→bottom
  darkening is mostly light (its lit quartile still drops about 25 levels in the bottom third, and the palette has a
  darker **Clay (Secondary)**, so a light painted low band is justified, §5.3); the soil is one brown; the rocks one
  warm grey. Keep Tint low and blends gentle so it still reads "solid colors".

### 3.9 Effects

- The sheet shows none (no glow, sparkle, dust, crumbs or chips). Stages 5/6 add nothing by default (§7).

## 4. Construction plan (stage 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `soil_base()` → `RedClayDepositSoilBase`: the pad alone (no rocks; the exploded base has none). Compare with
     `z_expl_base.png`: 12–14 sides, chamfer, sloped faceted skirt, gently domed top, flat bottom.
   - `main_lobe()` → `RedClayDepositMainLobe`: compare with the part close-up from about (−10, 15): flat bottom, broad
     sloping crown, 10–12 outline corners, within-face facets.
   - `lobe()` → `RedClayDepositLobe`: the squat type at FR's size (4.2 × 3.8 × 2.4). Compare with the exploded left
     "Clay Lobe" (screen W/H 1.4–1.5).
   - `rock()` → `RedClayDepositRock`: variant A (1.35). Compare with the exploded rocks (dome, flat bottom, W/H
     1.15–1.3 on screen).
   - Render a parts shot (`extra`, about (−20, 15)) laid out like the exploded.
2. **Hero:**
   1. `_paste` (m011 pattern) the soil base, the 5 lobes (§2.1, each with its own seed, ring set and yaw) and the 11
      rocks (§2.3).
   2. One exact self-union (add pieces one at a time if the boolean struggles; save between risky steps), then
      `union_loose`, then `m004.floor_cut` at z 0.
   3. Origin at the bbox bottom centre; transforms applied. One closed shell (decision §8.6).
3. **Budget** (§4.3): hero about 1300–1800 (limit 4000), each part under 200 (limit 1000). Spend spare tris only on
   the pad skirt (16–18 sides) if its triangles read too big against the sheet.
4. **Placeholder keys** (stage 1): `m023_clay`, `m023_soil`, `m023_rock`. Stage 4 adds the rest (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** a clay heap on a soil bed; five lobes with clean creases where they meet; the pad's brown ring
      visible all round; rocks embedded, none floating.
   2. **f34_sheet (0, 14) against the f34 cell:** W : H 1.62–1.72; shares within ±4 (R ±2) of 70.5 / 22.7 / 6.7; top
      profile within ±0.07; lobe extents per §2.2 (±0.06); 7 rocks visible at §1.2 ±0.06.
   3. **front_sheet (0, 9) against the front cell:** shares ±4, W : H 1.70–1.85, same lobe fractions ±0.08.
   4. **f34_sheet flipped against the r34 cell:** shares ±4, profile ±0.08.
   5. **rear_sheet (180, 9) against the rear cell; side_sheet (−90, 10) against the side cell:** shares ±5, lobe and
      rock counts (rear 5 lobes, 6–8 rocks, R11 centred; side 3 lobes, 4–6 rocks).
   6. **Top (0, 89):** pad outline (flat back-left sector), main/FR/BL centres ±0.07, FL/BR ±0.12, rocks round the rim,
      W : D 1.00–1.08.
   7. **Kit views** (front34, rear34, front, side, rear, underside): self-consistency; the underside shows the flat
      bottom inside its chamfer band with rim rocks reaching the ground.
   8. **Parts against their cells** (§4.1); **junction extra** `junc_cu (−35, 12)` framed on R4 between BL and FL
      against the Junction Detail.
   9. **Hero size** 10.0 × 9.6 × 4.75 (±0.4 / ±0.4 / ±0.2).
6. **Stage 2:**
   - zero non-manifold, boundary, wire and loose elements; no zero-area faces or n-gons; normals outward;
   - no faces under 5° where lobes meet lobes, lobes meet the pad and rocks meet the soil (m011 `_tidy` /
     `_desliver`);
   - don't decimate the lobes below about 20 broad faces, the rocks below 14 facets or the pad skirt below 12 sides.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Soil base (14 sides, 5 bands, crown fan, flat bottom) | 1 | 165 | 165 |
| Main lobe (hull 43 pts + pokes) | 1 | 100 | 100 |
| Squat lobes FR, FL (hull 30 + pokes) | 2 | 70 | 140 |
| Tall lobes BL, BR (hull 28) | 2 | 60 | 120 |
| Rocks (pebble rings, 20 pts) | 11 | 36 | 396 |
| **Sum before union** | | | **about 920** |
| **Hero after union** (creases, contact rings, floor cut) | | | **about 1300–1800** (limit 4000) |
| Parts: SoilBase / MainLobe / Lobe / Rock | | | about 165 / 100 / 70 / 36 (limit 1000) |

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 48 × 22 box inside each)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Clay (Main) | (40,1299,88,1321) | `#CD6139` | 16°, 0.72, 0.80 |
| Clay (Secondary) | (40,1343,88,1365) | `#BF5C38` | 16°, 0.71, 0.75 |
| Soil Base | (40,1387,88,1409) | `#87634A` | 25°, 0.45, 0.53 |
| Rocks | (40,1431,88,1453) | `#968F90` | 351°, 0.05, 0.59 |

- **Clay (Main)** is a little darker than the unshadowed rendered clay (`#D0613C`–`#D4633B`), close to it in hue and
  sat.
- **Clay (Secondary)** is the same hue, 13 levels darker: it matches the lobes' lower thirds (`#BC5731`, part
  close-up) and the hero's shaded BL lobe (`#C15F39`). No lobe is painted in it as a whole (the exploded "Clay Lobe"
  medians `#DA673B` / `#D2643C` equal the main lobe's `#D0613C`).
- **Soil Base** equals the hero's rendered soil median (`#856248`); the unshadowed exploded base renders lighter
  (`#987054`).
- **Rocks:** the swatch is a neutral, slightly purple grey; **every rendered rock is warmer** (hue 7–21°, sat
  0.12–0.19, even the floating exploded rocks with no orange near them). Calibrate on the renders.

### 5.2 Rendered regions (`samp.py`, `samp2.py`, `samp3.py`; median / lit quartile / shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Clay, f34 / front / top | V | K | `#DA653A` / `#DA673E` / `#DA683F` | `#FC8355` / `#FA8255` / `#EF764A` | `#AE4D2A` / `#AB4E2C` / `#9E4A2B` |
| Clay, r34 / side / rear | V | K | `#D86239` / `#DC663C` / `#D36038` | `#F77C4E` / `#F67B4D` / `#F37A4D` | `#AA4B27` / `#A74A28` / `#9C4525` |
| Clay, exploded main / lobe L / lobe R | §1.4 boxes | K | `#D0613C` / `#DA673B` / `#D2643C` | `#F47D51` / `#EC764A` / `#F98152` | `#AA4D2A` / `#A04827` / `#9E4828` |
| Clay, part close-up | (666,742,961,938) | K | `#D4633B` | `#F07A4C` | `#A74F2E` |
| Clay, junction close-up | (656,1214,831,1364) | K | `#DC6638` | `#EB7245` | `#9F4624` |
| Clay, hero lobes main / FR / FL / BL / BR | (180,135,370,260) / (260,240,450,340) / (160,285,250,350) / (85,220,160,300) / (390,200,450,260) | K | `#E2693B` / `#E16A3D` / `#EC7245` / `#C15F39` / `#E56B3E` | `#FC8455` / `#FD8959` / `#F87D4F` / `#EE784E` / `#FD8A5A` | `#B65433` / `#C3582E` / `#C95C33` / `#974327` / `#AD4823` |
| Clay thirds, exploded main (top / mid / bottom) | (227,746,462,898) | K | `#F2794C` / `#DD693D` / `#B0512E` | `#F98256` / `#F47D51` / `#CD5E34` | `#EB7446` / `#B55532` / `#974525` |
| Clay thirds, part close-up | (666,742,961,938) | K | `#EF774A` / `#DA673E` / `#BC5731` | `#F67F52` / `#F07B4E` / `#D8653A` | `#E67144` / `#BF5A36` / `#984626` |
| Clay thirds, exploded lobe R | (391,887,519,991) | K | `#F57D4F` / `#D6673E` / `#A84C2A` | `#FD8859` / `#F37C4E` / `#D5673D` | |
| Clay thirds, hero FR | (260,240,450,350) | K | `#FA8051` / `#EB7042` / `#D15E36` | `#FD8A5B` / `#FC8B5C` / `#E56B3C` | |
| Soil, f34 / front / top | V | S | `#856248` / `#8B674D` / `#745642` | `#9F7556` / `#A27A5C` / `#9F7961` | `#664D3A` / `#674F3C` / `#543E2F` |
| Soil, r34 / side / rear | V | S | `#856148` / `#87644C` / `#8A664C` | `#9D7355` / `#A87C5D` / `#A37758` | `#664D3A` / `#6A523F` / `#6F533E` |
| Soil, exploded base (unshadowed) | (191,1097,504,1228) | S | `#987054` | `#AD7E5F` | `#7E5D45` |
| Soil, exploded base thirds (top / mid / skirt) | same | S | `#A6795A` / `#A07557` / `#89654C` | `#AF8060` / `#AE7F60` / `#976F53` | |
| Soil, f34 front skirt / f34 left top strip / r34 front skirt | (150,385,450,409) / (60,300,150,360) / (640,385,900,409) | S | `#7D5C43` / `#785B46` / `#7C5A42` | `#8F694C` / `#8A6B53` / `#8A654A` | `#6B4F38` / `#594535` / `#6B4F3A` |
| Soil, underside (all / flat bottom) | (684,990,976,1131) / (720,1060,930,1125) | S | `#947051` / `#947151` | `#AD7E5D` / `#977556` | `#74543C` / `#8F6B4A` |
| Soil, junction close-up | (655,1297,893,1470) | S | `#8C664B` | `#9C7254` | `#805E44` |
| Rocks, f34 / front / top / side / rear / r34 | V | R | `#92827C` / `#96837A` / `#9A8983` / `#81716A` / `#938178` / `#95817A` | `#B9A398` / `#BCA79B` / `#C0ADA3` / `#B39E90` / `#B49E93` / `#B7A197` | `#6C5E59` / `#6C605C` / `#776963` / `#665A57` / `#6B5D57` / `#71645F` |
| Rocks, exploded (5) | §1.4 boxes | R | `#8E7E7A` / `#8D7E7C` / `#92827F` / `#948581` / `#92807A` | `#A59894` … `#BAAAA5` | `#675E5E` … `#706867` |
| Rocks, single (f34 front / f34 notch / top front-left / top back / junction big / junction small) | samp3 boxes | R | `#98837B` / `#8E807B` / `#968783` / `#98867F` / `#93827C` / `#9E8270` (sat .29) | | |
| Rosy lump, top view (BR, §3.4) | (958,535,982,562) | all | `#BB7B5C` (20°, 0.51) | `#C99A87` | `#794F37` |
| Ground shadow, f34 | (60,410,520,425) | all | `#F2ECE6` (= paper: no cast shadow drawn) | | |

Deciles (dark → light), f34:

```
clay   #8C3D1F #B3512C #BE5732 #CA5B33 #D76337 #DE683B #E76D3D #F1784B #FB8153 #FD8A5B
soil   #533F30 #6A4F3C #785740 #7B5A43 #815F46 #8B6448 #8E674A #936A4D #9E7253 #A87D62
rock   #635853 #6E615C #756A67 #7D7270 #8D7E7A #97857F #A38F87 #AA988F #B49F96 #C2AC9F
```

### 5.3 How the colour works

**Clay.**
- One saturated red-orange: hue 15–17° everywhere, sat 0.68–0.75. The big spread (`#8C3D1F` → `#FD8A5B`) is the sun on
  the facets; never paint by facing.
- **Painted signal (light): a darker low band.** Every lobe's bottom third is darker than its middle even in its lit
  quartile (`#D8653A` against `#F07B4E` on the close-up; `#CD5E34` against `#F47D51` on the exploded main), sat rises
  0.69 → 0.74, and the palette carries Clay (Secondary) `#BF5C38`. Most of it is light (down-turned faces), so paint
  only a gentle band: the lowest 30 % of each lobe at about 40 %, fading by 0.45 of its height.
- **No light top band in paint.** The top thirds (`#F2794C`–`#FA8051`) are up-facing faces in the sun; their shade
  quartile is still bright because they all face up. That is light.
- **Within-face facets** (the split triangles with slightly different tone) are geometry (§1.4 pokes), not paint.
- **Lobes are all one clay.** BL's darker median (`#C15F39`) is the main lobe's shadow; satellites and main share keys.

**Soil.**
- One mid brown: hue 24–28°, sat 0.42–0.47. The skirt is darker than the top only by light (exploded skirt third
  `#89654C` against top `#A6795A`; the hero's front skirt `#7D5C43` ≈ its top strip `#785B46`).
- **Contact darkening:** the soil next to the lobes' feet and round the rocks reads darker in every view (shade
  quartiles `#664D3A`–`#6F533E`); mostly shadow, but Roblox has no AO, so paint a light touch (`soil_dark`, 35 %)
  within about 0.35 of each lobe and rock contact.
- The underside's flat bottom (`#947151`) is the same brown, evenly lit.

**Rocks.**
- One warm grey: hue 7–21°, sat 0.12–0.19, medians `#8D7E7C`–`#98867F`. The swatch's neutral `#968F90` is cooler than
  every render. Variety between rocks is small (±6 levels): per-rock tint only, no second key needed.
- The browner rock behind the big one in the Junction Detail (`#9E8270`, sat 0.29) is a rock sitting in warm soil
  shade; not a separate colour.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

The calibration targets are rendered medians of **unshadowed** regions (the exploded parts and the close-ups), not
swatches.
- **`K.sample` kinds:** `"vivid"` for the clay keys (sat 0.72 passes); `"brown"` for the soil keys; `"stone"` for the
  rock (sat 0.13 < 0.25 passes).

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m023_clay` | `#D4633B` (part close-up median; exploded main `#D0613C`, lobes `#DA673B` / `#D2643C`; swatch Clay (Main) `#CD6139`) | every lobe, the default | rough 0.8 |
| `m023_clay_low` | `#BC5731` (close-up bottom third; swatch Clay (Secondary) `#BF5C38`) | lowest 30 % of each lobe at 40 %, the crease faces where lobes meet at 25 % | rough 0.8 |
| `m023_clay_light` | `#DE6A3E` (hero main mid third `#DD6739`; FR mid `#EB7042`) | broad patches only (`K.patches` scale 1.0, level 0.3) on the upper halves, at 30 % | rough 0.8 |
| `m023_soil` | `#987054` (exploded base median, unshadowed; hero `#856248` = swatch `#87634A`) | the pad | rough 0.95 |
| `m023_soil_dark` | `#76573F` (f34 front skirt `#7D5C43`; junction soil shade `#805E44`; view shade quartiles `#664D3A`–`#6F533E`) | contact rings round lobe feet and rocks, the bottom chamfer band (z < 0.22) | rough 0.95 |
| `m023_rock` | `#917F7C` (exploded rock medians `#8D7E7C`–`#948581`; hero `#92827C`; swatch `#968F90`) | every rock | rough 0.9 |

**Calibration warnings:**
- **Clay is near the clip** in the lit quartile (R 252–253). Calibrate `m023_clay` on the parts shot of the main lobe
  against `#D4633B`, then check the f34_sheet clay median within 10 of `#DA653A`, hue 14–18°, sat ≥ 0.68. If the lit
  faces wash to pale salmon, lower the specular, not the colour. R07's `#D4572B` was a raw guess, not a calibrated key.
- **Soil:** calibrate on the parts shot of the soil base against `#987054`; then check the f34_sheet soil median within
  10 of `#856248` (most of the hero's soil is in the lobes' shade).
- **Rock:** check the hue stays warm (8–20°) and sat 0.10–0.20 in the render; a calibration that drifts to the
  swatch's purple-neutral reads wrong next to the sheet.
- The three families must stay far apart: clay sat ≥ 0.68, soil 0.40–0.50, rock ≤ 0.20.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Clay** (field = each lobe's local height fraction t = (z − base z) / lobe height, from its construction frame):
  - `clay` base;
  - t < 0.30 → 40 % `clay_low`, blending to 0 by t 0.45;
  - faces within 0.25 of another lobe's surface (the creases) → 25 % `clay_low`;
  - broad patches between `clay` and a 30 % `clay_light` mix on t > 0.5 (never single faces);
  - each lobe gets its own `tint_var` 0.03 so the five differ very slightly.
- **Soil** (fields = distance to the nearest lobe/rock surface; world z):
  - `soil` base;
  - within 0.35 of a lobe foot or rock → 35 % `soil_dark`, fading by 0.7;
  - the bottom chamfer band (z < 0.22) → `soil_dark` (unseen except in the underside);
  - broad patches (scale 1.2, level 0.3) between `soil` and a 15 % `soil_dark` mix on the skirt.
- **Rocks:** `rock` with per-rock `tint_var` 0.06 (two or three rocks a touch darker, as in the top view).
- **Hard edges only** where materials meet: clay | soil, clay | rock, rock | soil.

### 5.6 Texture (Tint) and finish

- **Tint:** clay amp 0.03, scale 0.6 (broad, clean); soil amp 0.05, scale 0.5 (the pad's faint facet-to-facet
  variation); rocks amp 0.04. Never per-triangle confetti ("No texture noise").
- **Finish:**

| Material | Roughness | Specular | Metal | Notes |
| --- | --- | --- | --- | --- |
| Clay keys | 0.8 | normal (lower if the lit faces clip) | 0 | damp-matte clay, soft highlights |
| Soil keys | 0.95 | normal | 0 | dry earth |
| Rock | 0.9 | normal | 0 | matte stone |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Clay:** f34_sheet median within 10 of `#DA653A`; parts-shot main lobe within 8 of `#D4633B`; bottom third darker
  than middle by 15–35 levels; hue 14–18°.
- **Soil:** f34_sheet median within 10 of `#856248`; parts-shot base within 8 of `#987054`.
- **Rock:** f34_sheet median within 10 of `#92827C`, sat 0.10–0.20.
- **Shares** per §4, step 5.2.

## 6. Joins and contact

- **Lobes into the pad:** each lobe's flat bottom sits 0.25–0.35 below the local pad top; the union leaves a clean
  crease ring ("Clay overlaps soil base"). No lip, no gap, no floating lobe.
- **Lobes into lobes:** overlap 0.3–0.6 (FR into the main lobe's front, FL against FR and the main lobe, BL and BR
  against the main lobe's flanks). The creases must read as dark lines in the f34 (§1.3).
- **Rocks:** 25–35 % of their height into the soil; rim rocks on the ground also cut into the skirt; R4 touches BL, FL
  and the pad (the Junction Detail); R11 touches the main lobe's back.
- **Ground:** floor-cut at z 0 (`m004.floor_cut`): one flat underside under the pad and the rim rocks ("Flat underside
  for placement").
- No coplanar faces: rock and lobe bottoms never sit exactly on a pad ring height; jitter them by 0.02–0.05. Exact
  booleans: add pieces one at a time if a union fails (2026-10-28 crash note in STAGES.md).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** an ordinary sunlit clay outcrop. No glow, light, sparkle, dust, crumbs or particles in any
cell; no ground shadow is even drawn. WorldModeling §1.2 forbids "an ordinary asset recolored neon with a glow halo".

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight:** nothing on the sheet glows; emission would export as flat Neon and erase the
  facets.
- **Studio note (Requires Manual Validation):** check in Studio that the clay's lit faces don't clip to flat salmon
  under the game's sun, and that clay, soil and rock stay three clearly different colours after the palette export.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **Recommended: none.** The sheet shows no effect, and M009 and M011–M020 decided against harvest sockets. Record
  "Stage 6 skipped: sheet shows no VFX".
- **Option** (decision §8.8): the R07 `ClayDeposit` pair, if the main session wants harvest feedback on nodes:
  - `harvest_hit` on FR's front face, about (1.7, −3.5, 1.6), colour override `["#D4633B", "#BC5731"]` (clay
    crumbs);
  - `harvest_deplete` at the pad centre, (0, 0, 0.6), colours `["#D4633B", "#987054"]`.
- **Not recommended:** `dust` (nothing floats on the sheet), `ore_glint` (clay doesn't sparkle), any light.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by searching the repo text and every sheet / wip `.blend` (zstd-decompressed) with
`blendall.py`:
- **R07 kit** (in `FlintbornWorldKit.blend`, its checkpoints and the M015–M017 wip copies, and
  `wip/R07_clay_deposit.blend`): `ClayDeposit`, `ClayDepositMainClayLobe`, `ClayDepositClayLobe`,
  `ClayDepositSoilBase`, `ClayDepositDepleted`, `ClayLump`; key `r07_clay` (and `r07_soil`, `r07_stone`).
- **Elsewhere:** `ClayStoragePot` (sheet 03 furnishings, lobby); `Pebble*` (W01 pebble scatter, 72 hits in the kit);
  the character colour `Clay`.
- `M.mk` would silently rename a clash to `<name>M023`, so avoid all of these.

**Proposed names.** None of `RedClayDeposit`, `RedClay`, `m023_` occurs in the repo, the decompressed kit `.blend` or
any sheet / wip `.blend`. "Red clay" is the plain name for this iron-red orange clay, and it keeps the sheet's
"Clay Deposit".

| Object | Part | Why |
| --- | --- | --- |
| `RedClayDeposit` | hero | R07 owns `ClayDeposit` |
| `RedClayDepositMainLobe` | Main Clay Lobe | R07 owns `ClayDepositMainClayLobe` |
| `RedClayDepositLobe` | Clay Lobe (the squat type, FR's size) | R07 owns `ClayDepositClayLobe` |
| `RedClayDepositRock` | Rocks (variant A, 1.35) | `Pebble*` belongs to W01 |
| `RedClayDepositSoilBase` | Soil Base (without rocks, as exploded) | R07 owns `ClayDepositSoilBase` |

- Palette keys `m023_*` (§5.4). Collection `Kit/M023 Clay Deposit`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **10.0 × 9.6 × 4.75, pad 9.8 × 9.4, rocks 0.75–1.35** (recommended: rock-anchored; chest-high
   outcrop; close to R07's 9.5 × 8.1 × 5.0 and the common nodes), or R07's footprint (9.5 × 8.1).
2. **Lobe count:** **five lobes** (recommended: the f34, front, r34 and rear all show five; the top's rock and rosy lump
   sit exactly where FL and BR go, §3.4), or three (top and exploded only).
3. **Main lobe proportions** (§3.6): **4.7 × 4.2 × 4.0 tall with a broad sloping crown** (recommended: the hero's
   crown height needs it), or the close-up's squat 0.45 h/W (the hero would then be about 3 tall, −35 %).
4. **Depth** (§3.5): **D 9.6** (recommended compromise), or 8.1 (side cell) or 10.8 (top view).
5. **Rocks:** **5 variants, 11 instances embedded 25–35 %** (recommended: every view's count within ±1), or 7 (the
   hero's visible set only; the rear and top would then lack theirs).
6. **Hero packaging:** **one closed shell** (recommended: STAGES default and the one-mesh-per-asset contract), or the
   lobes as separate objects (only if the game later swaps lobes when harvested).
7. **Exports:** **the hero plus 4 parts** (`...MainLobe`, `...Lobe`, `...Rock`, `...SoilBase`) (recommended). R07's
   `ClayLump` drop and `ClayDepositDepleted` state are not on this sheet and are not built unless asked.
8. **Stage 5/6:** **no emission, light or VFX** (recommended: the sheet shows none; consistent with M009–M020), or the
   R07-style `harvest_hit` / `harvest_deplete` pair with clay colours (§7.2).
9. **Comparison cameras** (recommended, §3): `f34_sheet (0, 14)` for the hero, `front_sheet (0, 9)` for the front
   cell, the f34_sheet render flipped for the r34, `rear_sheet (180, 9)` for the rear, `side_sheet (−90, 10)` for the
   side, kit top for the top; kit front34, rear34, front, side, rear, underside as self-consistency only; extras
   `junc_cu (−35, 12)` and a parts shot `(−20, 15)`.
10. **Clay keys:** **one clay family with a gentle painted low band** (`clay_low` from Clay (Secondary)) (recommended),
    or Clay (Secondary) as a whole-lobe colour for the four satellites (the sheet's renders don't show that).
11. **Names** as proposed.

## 9. Pitfalls to avoid

1. **Five balls on a plate.** Lobes must overlap each other and sink into the pad with clean creases; the pile reads as
   one outcrop (f34 creases at f .30, .43–.50, .72).
2. **Round or jewel lobes.** Broad faces (20–24 per big lobe, edges 1.0–1.6 studs on the main), flat bottoms, broad
   sloping crowns; not ico-2 balls (R07's "rounded blobs") and not bare icosahedra. Pokes give the within-face facets.
3. **A smooth dome pad.** The pad is a slab: flat bottom, chamfer, sloped skirt of irregular triangles, near-flat top
   (R07's "smooth dome base" was flagged). Rim about 0.8 high; the brown ring must show round the lobes in every view.
4. **Comparing with the wrong camera.** The f34 is an aligned front view at 14°; the r34 is the f34 mirrored; the side
   is from −X (§3.1–§3.3).
5. **Copying the top view's colours.** FL and BR are orange clay; the top's grey rock and rosy lump at their places
   are drawing slips (§3.4).
6. **Copying the exploded sizes.** The exploded parts are 1.5–2× too big for the base, and the main lobe there is too
   flat (§3.6). The hero governs.
7. **Floating or perched rocks.** Every rock sinks 25–35 % into soil; rim rocks touch the ground and cut into the
   skirt.
8. **Colour by facing.** The low clay band goes by height within each lobe and the soil darkening by distance to a
   contact, never by normal; `K.check` facing correlation < 0.5.
9. **Purple-grey rocks.** The swatch is cooler than every render; calibrate the rock on the renders (warm grey,
   hue 8–20°).
10. **Salmon clay.** The clay sits near the clip; keep sat ≥ 0.68 in the render (lower specular if it washes out).
11. **Exact booleans.** Overlap everything; no coplanar bottoms on pad rings; add the 16 pieces one at a time if the
    union struggles; remove slivers with m011's `_tidy` / `_desliver`; save between risky steps.
12. **Naming clashes** with R07 `ClayDeposit*`, `ClayLump`, W01 `Pebble*` (§8). Only one agent drives a Blender
    session at a time; no commits, pushes or exports in stage agents.

## Decisions (main session, 2026-10-28)

All recommendations are accepted:
1. Size: 10.0 W × 9.6 D × 4.75 H.
2. Five lobes, as in the hero view.
3. Main lobe 4.0 tall, with a broad sloping crown.
4. Depth 9.6, the compromise between the side and top cells.
5. Rocks: 11 instances of 5 variants, sunk 25–35 % into the soil.
6. One closed shell. Add pieces one at a time.
7. Hero plus 4 parts; no depleted state and no drop.
8. No VFX.
9. Comparison cameras: `f34_sheet (0,14)`, `front_sheet (0,9)`, the f34_sheet render flipped for the rear three-quarter, `rear_sheet (180,9)`, `side_sheet (-90,10)`, and extras `junc_cu (-35,12)` plus a parts shot at (-20,15).
10. One clay family with a painted low band; don't make whole lobes "Secondary".
11. Names as proposed: `RedClayDeposit` with `MainLobe`, `Lobe`, `Rock` and `SoilBase`.

Accepted misses: the side view reads about 18 % wider than the sheet, and the top view about 12 % wider, with the wrong colours at two lobes.


## Stage 1 — Modelling (modeller, 2026-10-28)

The builder is `art/blender/kit/mcp/m023.py`, `build()`. It takes about 8 s without renders and about 25 s with them.
It returns a dict with a `problems` list, which is empty on the final build. The background session ran on port 9880
with the work file `wip/M023.blend`, saved after each good build.

**Parts, each built by its own function:**

| Function | Object | Tris | What it is |
| --- | --- | --- | --- |
| `soil_base_part` | `RedClayDepositSoilBase` | 232 | the pad |
| `main_lobe_part` | `RedClayDepositMainLobe` | 124 | the main lobe |
| `lobe_part` | `RedClayDepositLobe` | 88 | FR's squat lobe |
| `rock_part` | `RedClayDepositRock` | 36 | rock variant A |

The hero `RedClayDeposit` is built from the same functions (`_soil_base`, `_lobe`, `rocks`).

**Lobes** (`_lobe`). Each lobe is the convex solid bounded by jittered tangent planes:
- the planes have Fibonacci normals (M019's polar-dual recipe; `_dual_hull` is copied in);
- a flat bottom plane closes it, plus one crown plane (main and squat lobes) or two ridge planes (tall lobes);
- the solid is fitted to its W × D box;
- the largest faces are then poked with a 2 % raise. This gives the sheet's split facets within each broad face.

Broad faces before triangulation: main 30, FR 23, FL 24, BL 20, BR 20.

**What changed on the renders, and why:**
1. **First pass.** I followed the spec's ring layout (Fibonacci normals down to z −0.42, the box fitted to 4.0 tall).
   The lobes came out as upright rounded boxes with vertical sides.
2. **Side planes tilted up only.** This gave frustum domes, which was better. But the f34 compare showed that the
   sheet's lobes are full round boulders. Each is widest at about two thirds of its visible height, and its lower part
   sinks into the pad.
3. **Final: a faceted spheroid cut flat low down.**
   - `LOBES` gives each lobe:
     - its top z, taken from the f34 cell with s = z cos 14° + (Y + 4.7) sin 14°;
     - its W × D;
     - its height from the equator to the top;
     - its cut b, the fraction of that height below the equator.

   | Lobe | Top z | W × D | Base z |
   | --- | --- | --- | --- |
   | Main | 4.75 | 4.7 × 4.4 | 0.81 |
   | FR | 3.0 | 4.3 × 3.9 | |
   | FL | 2.2 | 2.6 × 2.4 | |
   | BL | 3.0 | | |
   | BR | 2.75 | | |

   - Round 1b: the main lobe moved 0.25 forward, and FR and FL moved 0.3 toward the rim. In the sheet only the skirt
     shows in front of them.
   - Round 1c: BL and BR moved in against the main lobe. The top view had shown pad between them.
4. **Tried and rejected.**
   - Round 1e: BL 0.6 further back and BR lower, for the rear cell's "near" lobes. The rear barely changed, and the f34
     profile error grew from a maximum of 0.07 to 0.12.
   - Round 1c: rocks × 1.1. The rock share rose to 0.09 in f34 and 0.15 in the rear.

**Pad** (`_soil_base`). 14 sides. The rings run from the ground up:

| Ring | z | Radius |
| --- | --- | --- |
| bottom (below the floor cut) | −0.05 | |
| chamfer | 0.2 | 1.0 R |
| sloped skirt | 0.58 | 0.95 R |
| rim | 0.95 | 0.875 R |
| inner top | 1.1 | |
| crown | 1.2 | |
| centre point | 1.23 | |

Each quad is split on a seeded diagonal, so the skirt reads as irregular triangles. Round 1d raised the rim from 0.8
to 0.95 and sloped the skirt further out, which gives a thicker band in f34.

**Rocks** (`rocks`). 11 instances of 5 variants: A 1.24, B 1.1, C 1.01, D 0.87 and E 0.7. These are the spec's sizes
× 0.92, reduced after the pad got thicker. Each rock is placed by azimuth and a fraction of the pad's outline.
- **Ground rocks:** the base sits at z −0.15 and the floor cut flattens it; the rock cuts into the skirt.
- **Seated rocks:** the base sits 0.3 h below the soil under the rock's centre, and the bottom is turned half way
  toward the soil normal.

**Hero.**
- **Union and cleanup:**
  - One exact union of each shell in turn (`M.union_loose`, 16 shells).
  - `m004.floor_cut` at z 0.
  - Then `m016._clean_mesh`, `_finish` and `_polish` (M020's version, which includes the floor re-fan).
  - Finally `M.fix_bowties` as a guard. It found 0 bowties on every object.
- **Hero guard:** if the result is not one clean shell, every rock turns another 17° and the hero is rebuilt. This
  includes no self-intersections and no bowtie vertices. In round 1d a sliver pair showed up once at R4/FL; the current
  build passes on attempt 0.

**Measured against the sheet** (`m023.measure()`). It applies the study's masks to the sheet cells and to our long-lens
`*_sheet` renders. The rock mask also needs hue ≤ 30 or ≥ 300 and sat ≥ 0.06; without that, the studio floor's shadow
counts as rock.

| View | W : H sheet / ours | Clay K | Soil S | Rock R | top-profile error mean / max |
| --- | --- | --- | --- | --- | --- |
| f34 (`f34_sheet` 0, 14) | 1.689 / 1.583 | .709 / .697 | .228 / .234 | .063 / .070 | .025 / .07 |
| front (`front_sheet` 0, 9) | 1.739 / 1.733 | .719 / .694 | .224 / .239 | .058 / .067 | .031 / .12 |
| r34 (f34_sheet flipped) | 1.656 / 1.583 | .711 / .697 | .233 / .234 | .056 / .070 | .044 / .13 |
| rear (`rear_sheet` 180, 9) | 1.647 / 1.830 | .651 / .629 | .279 / .265 | .070 / .107 | .046 / .13 |
| side (`side_sheet` −90, 10) | 1.475 / 1.645 | .660 / .605 | .292 / .268 | .048 / .126 | .052 / .12 |
| top (`top_sheet` 0, 89) | 0.925 / 1.034 | .555 / .586 | .358 / .339 | .087 / .076 | .019 / .08 |

Hero size is 10.01 × 9.71 × 4.75 (target 10.0 × 9.6 × 4.75).

## Stage 2 — Optimisation and cleanup

| Object | Tris | Size (studs) | Shells | Non-manifold edges / verts | Boundary / wire / loose | Zero-area / n-gons / dup verts | Self-hits | Min corner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RedClayDeposit (hero) | 1386 / 4000 | 10.01 × 9.71 × 4.75 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 5.11° |
| RedClayDepositSoilBase | 232 / 1000 | 9.76 × 9.27 × 1.24 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 5.08° |
| RedClayDepositMainLobe | 124 / 1000 | 4.57 × 4.33 × 3.94 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 5.28° |
| RedClayDepositLobe | 88 / 1000 | 4.37 × 4.08 × 2.62 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 8.76° |
| RedClayDepositRock | 36 / 1000 | 1.18 × 1.08 × 0.99 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 24.5° |

- **Every object:** normals outward, no custom split normals, flat shading, transforms applied, origin at the bottom
  centre (offset 0, 0, 0).
- **Pre-union pieces:** pad 166 tris; lobes 116 / 92 / 94 / 72 / 64; rocks 36 each.
- **Hero floor:** one flat cap at z 0.
- **`K.check`:** reports nothing.

## Stage 3 — UV

`M.smart_uv` runs through `_finish` and `_polish`: angle 45, an ANGLE_BASED re-unwrap, margin 0.008.

| Object | Islands | Overlaps | Flipped | Min gap / border | Density min / med / max | Conformal stretch p95 / worst |
| --- | --- | --- | --- | --- | --- | --- |
| Hero | 233 | 0 | 0 | 0.016 / 0.008 | 1.0 / 1.0 / 1.0 | 1.003 / 1.091 |
| SoilBase | 15 | 0 | 0 | 0.016 / 0.008 | 1.0 / 1.0 / 1.0 | 1.027 / 1.039 |
| MainLobe | 9 | 0 | 0 | 0.016 / 0.008 | 1.0 / 1.0 / 1.0 | 1.089 / 1.116 |
| Lobe | 8 | 0 | 0 | 0.016 / 0.008 | 1.0 / 1.0 / 1.0 | 1.031 / 1.036 |
| Rock | 10 | 0 | 0 | 0.016 / 0.008 | 1.0 / 1.0 / 1.0 | 1.06 / 1.066 |

## Stage 4 — Materials, colour and texture

**Calibration, in two passes.**
1. `m023.calibrate()` runs `K.calibrate` on the dome.
2. The hero's `f34_sheet` render is measured against the f34 cell. Pass 2 changed only the clay keys, by
   × (1.076, 1.021, 0.825) in linear light. Soil and rock were already within 6.

| Key | Target (sheet render) | Dome pass 1 | Final hex | Roughness |
| --- | --- | --- | --- | --- |
| m023_clay | #D4633B | #A7502D (renders 211,99,61) | #AD5128 | 0.8 |
| m023_clay_low | #BC5731 | #964521 (189,87,52) | #9B461D | 0.8 |
| m023_clay_light | #DE6A3E | #AF5630 (221,106,63) | #B5572B | 0.8 |
| m023_soil | #987054 | #785D49 (150,112,85) | #785D49 | 0.95 |
| m023_soil_dark | #76573F | #5E4835 (117,88,64) | #5E4835 | 0.95 |
| m023_rock | #917F7C | #7C6D6E (150,128,123) | #7C6D6E | 0.9 |

**Final renders against the sheet:**

| Region | Ours | Sheet |
| --- | --- | --- |
| f34 clay, median / lit quartile / shade quartile | #DA653C / #E96F43 / #994327 | #DA653A / #FC8355 / #AE4D2A |
| f34 clay thirds, top / mid / bottom | #E46C40 / #DE693E / #C65933 | #EB6E42 / #D9643A / #CD5D34 |
| f34 soil | #87644B | #856248 |
| f34 rock | #98817C | #92827C / #95837D |
| front clay | #DA653D | #DA673E |
| front soil | #86644B | #8B674D |

**Blends.** All painted by position only, never by facing, in 25 % steps.
- **Clay**, a ladder from clay_low through clay to clay_light. Each lobe:
  - goes by its own height fraction t: full 50 % clay_low below t 0.22, fading out by t 0.5;
  - has broad noise patches toward clay_light, up to 50 %, above t 0.5–0.7;
  - takes at least 25 % clay_low on faces within 0.45 of another lobe's surface (the creases).
- **Soil**, a ladder from soil to soil_dark:
  - contact rings round the lobe feet and the rocks: 50 % within 0.35, 25 % within 0.8;
  - the chamfer band (z < 0.22) at 25 %;
  - broad noise patches at 25 % or 50 %.
- **Rocks:** the rock key, with a Tint of 0.95–1.04 per rock.
- **Floor cap:** plain soil, so the colour doesn't follow facing.
- **Hard edges:** only where two materials meet.

**Tint mottling.**

| Material | Amp | Scale | Extra |
| --- | --- | --- | --- |
| Clay | 0.03 | 0.6 | a factor of 0.98–1.02 per lobe |
| Soil | 0.05 | 0.5 | |
| Rock | 0.04 | 0.8 | |

The asset's tint_var is 0.03, and there is no per-triangle jitter.

**Hero materials (9):** soil, clay, rock, clay_low × clay at 50 % and 75 %, clay × light at 25 % and 50 %, and soil ×
dark at 25 % and 50 %.

## Stage 5 — Lighting

Skipped. The sheet shows an ordinary sunlit outcrop, so there is no emissive key and no light (decision 8).

**Studio check:** under the game's sun, the clay's lit faces must not clip to salmon, and clay, soil and rock must
still be three distinct colours after the palette export.

## Stage 6 — VFX

Skipped. The sheet shows no glow, sparkle, dust or crumbs, so there are no sockets (decision 8). The renders still ran
with vfx=True, which is `M.views`' default.

## Modeller's notes for the verifier

**Cameras.** Compare with the `*_sheet` renders, which use a 3× longer lens:

| Sheet cell | Our render |
| --- | --- |
| f34 | `f34_sheet (0, 14)` |
| front | `front_sheet (0, 9)` |
| r34 | `f34_sheet` flipped left to right |
| rear | `rear_sheet (180, 9)` |
| side | `side_sheet (−90, 10)` |
| top | `top_sheet` |

The kit views are for self-consistency only. `m023.measure()` reproduces the tables above. Other renders: `junc_cu` (the
Junction Detail at R4 between BL and FL), `under_cu`, `exploded`, and `part_*`.

**Known misses:**
- **Side and top are too wide:** W : H is 12 % over the sheet in both (accepted in the decisions). The side cell's
  wide, low centre lobe is narrower in ours; BL is 3.0 deep.
- **Rear cell.**
  - **Lobes:** the sheet shows two low near lobes and two higher far ones beside the main lobe. Ours shows one cluster
    per side, because FL hides behind the main lobe when seen from +Y.
  - **Rock share:** 0.107 against 0.070. R11 and R8–R10 read larger than the sheet's rocks.
  - **Clay colour:** ours is darker, #B35332 against #D36038. The sheet lights the rear cell from its own camera side;
    the studio light stays at the front.
- **Clay lit quartile:** 19 levels darker than the sheet (#E96F43 against #FC8355) at the same median. The sheet's sun
  is brighter on the facets. I left the colour alone so the median stays matched.
- **Main lobe part shot:** the part is the whole spheroid (4.57 × 4.33 × 3.94), so it reads rounder and taller than
  the sheet's squat Part Close-Up (decision 3: the hero governs).
- **Exploded shot:** it is at true hero scale, so the rocks look small next to the sheet's enlarged parts.

**What matches:** the f34 top profile is within 0.07 everywhere, and the f34 shares are within 1.2 points.

## Stage 7 — Verification (round 1)

Independent verifier, 2026-10-28. Read-only background session on port 9880 with `wip/M023_verify.blend`; nothing
was saved or rebuilt. Fresh renders went to the verifier's scratch folder (`render_views` with `M.MODEL_RENDERS`
redirected), not to this folder. `m023.measure()` on those renders reproduces the stage 1 table exactly.

**Verdict: FAIL, 6.5 / 10.** One blocker (lobe shape against the Part Close-Up and the exploded lobes); everything
technical passes.

### Re-measured (all five objects)

| Object | Tris | Size | Shells | NM edges / verts | Boundary / wire / loose | Zero-area / n-gons / dups | Self-hits | Interior faces | Min corner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RedClayDeposit | 1386 / 4000 | 10.01 × 9.71 × 4.75 (target 10.0 × 9.6 × 4.75: in tolerance) | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 | 5.11° |
| SoilBase | 232 | 9.76 × 9.27 × 1.24 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 | 5.08° |
| MainLobe | 124 | 4.57 × 4.33 × 3.94 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 | 5.28° |
| Lobe | 88 | 4.37 × 4.08 × 2.62 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 | 8.76° |
| Rock | 36 | 1.18 × 1.08 × 0.99 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 | 24.5° |

- Normals outward, no custom normals, flat shading, no modifiers, rotation 0 and scale 1, origin at the bottom centre
  (offset 0, 0, 0) on every object. Interior faces: odd-crossing ray test from each face centre, 0 everywhere.
- UV: hero 233 islands, parts 15 / 9 / 8 / 10; 0 overlaps, 0 flipped, min gap 0.016, border 0.008, density 1.0,
  conformal p95 ≤ 1.09.
- Materials: hero 9 (clay ×5 steps, soil ×3, rock); roughness clay 0.8, soil 0.95, rock 0.9; metal 0; emission 0;
  no VFX children (decision 8). `K.check` reports nothing (facing correlation under the limit).
- Area by key on the hero: the plain `m023_soil` key covers 67.4 of area, almost all of it the floor cap (mean normal
  z −0.99). The visible pad is entirely 25 % (19.0) and 50 % (27.0) soil_dark mixes.

### Colours, sheet against ours (study masks; Δ = ours − sheet per channel)

| Region | Sheet | Ours | Δ |
| --- | --- | --- | --- |
| f34 clay median | #DA653A | #DA653C | 0, 0, +2 |
| f34 clay light (lit quartile) | #FC8355 | #E96F43 | −19, −20, −18 |
| f34 clay low (shade quartile) | #AE4D2A | #994327 | −21, −10, −3 |
| f34 clay thirds top / mid / bottom | #EB6E42 / #D9643A / #CD5D34 | #E46C40 / #DE693E / #C65933 | −7,−2,−2 / +5,+5,+4 / −7,−4,−1 |
| f34 soil median / lit / shade | #856248 / #9F7556 / #664D3A | #87644B / #977256 / #553F2F | +2,+2,+3 / −8,−3,0 / −17,−14,−11 |
| f34 rock median / lit / shade | #95837D / #B8A298 / #6C5E58 | #98817C / #A78E89 / #6F5E5B | +3,−2,−1 / −17,−20,−15 / +3,0,+3 |
| front clay / soil / rock median | #DA673E / #8B674D / #99847B | #DA653D / #86644B / #98817C | 0,−2,−1 / −5,−3,−2 / −1,−3,+1 |
| top clay / soil / rock median | #DA683F / #745642 / #998882 | #D5623A / #7C5E48 / #887573 | −5,−6,−5 / +8,+8,+6 / −17,−19,−15 |
| side clay median | #DC663C | #C65C39 | −22, −10, −3 |
| rear clay / soil / rock median | #D36038 / #8A664C / #928178 | #B35332 / #6B5240 / #7E6E6D | −32,−13,−6 / −31,−20,−12 / −20,−19,−11 |

Medians match the sheet in the hero and front views. Hue and saturation stay in the three families. Our studio
render has more light contrast than the sheet: lit facets are about 19 levels duller and shade 10–20 darker. The rear
and side cells are darker because the studio key light stays at the front, which is lighting rather than paint.

### Views against the sheet (`f34_sheet`, `front_sheet`, f34 flipped, `rear_sheet`, `side_sheet`, `top_sheet`)

- **f34 / front:** W : H 1.583 / 1.733 (sheet 1.689 / 1.739). Shares K .697 / S .234 / R .070 (sheet .709 / .228 /
  .063). Top profile mean / max error .025 / .07 (front .031 / .12). Five lobes with clean creases, the pad's brown
  ring all round, 7 rocks visible. The overall read is right.
- **Soil band under the clay** (lowest object – lowest clay, fraction of H), f34 sheet / ours: f .30 .02–.15 /
  .04–.21; .50 .00–.17 / .00–.28 (R5 in front); .60 .02–.13 / .02–.22; .70 .02–.13 / .04–.16. The pad is not thin. FL's
  and FR's front feet sit about 0.06–0.09 H higher than the sheet's (FL's .21–.24 against .15; FR's .16–.22 against
  .13), which is at or just past the ±0.06 tolerance.
- **r34 (f34 flipped):** profile .044 / .13, shares within 1.4. **Rear:** W : H 1.83 against 1.647, rock .107
  against .070, one lobe cluster per side (known miss). **Side:** 1.645 against 1.475 (accepted miss). **Top:** W : D
  1.034 against 0.925 (accepted miss), lobe centres right; rim rocks read smaller and sit further out than the
  sheet's.
- **Junction close-up:** the lobe comes down onto the soil and R4 sits sunk in front of it, as on the sheet. FL's
  lower edge shows a small jagged notch where its undercut lower facets meet the domed pad top; the sheet's crease
  is clean.
- **Underside close-up:** the flat bottom is right, but the render is almost black (no light from below), so the
  chamfer band can't be judged. Compare the geometry only.

### Items

1. **BLOCKER: the lobes are pinched spheroids with even, soccer-ball facets, not the sheet's broad-based boulders.**
   - **Part Close-Up against `part_mainlobe`.** The sheet's main lobe is widest at its flat bottom. Its sides slope
     in to a broad sloping crown, and its facets are big irregular triangles.
   - Ours is a ball. The bottom is 3.4 × 3.6 against a maximum of 4.6 × 4.3, so the base is about 0.76 of the width,
     and the widest point is at about half height. The facets are near-uniform pentagons and hexagons, because the
     planes are on a Fibonacci sphere with only ±6 % jitter.
   - The same recipe shapes the hero's lobes: FR and FL show dark undercut flanks and a jagged lower edge where they
     meet the pad. This is pitfall 2 ("not bare icosahedra"). Decision 3 kept the height but asked to keep "a flat
     bottom, a broad sloping crown of 4–5 big faces, and big side triangles".
   - **Fix (builder `m023.py`, `KINDS` / `LOBES` / `_lobe`):**
     - **(a) Cut higher so the base is broad.** Main `b` 0.75 → about 0.35–0.4, and squat `b` 0.5/0.55 → about 0.3.
       Raise `Hup` so each lobe's top z and H stay the same: main Hup ≈ 3.94 / 1.38 ≈ 2.85. The flat bottom is then at
       least 0.9 of the max width. Sink each lobe 0.25–0.35 into the pad as the spec's §6 says.
     - **(b) Make the facets fewer and irregular.** Main planes 28 → 18–20, squat 22 → 14–16. Plane distance jitter
       0.06 → 0.12–0.15, and angle jitter `ang` 0.17 → 0.3. Then poke or triangulate the largest faces into 2–4 big
       triangles, as the close-up shows.
     - **(c) Make the crown one broad sloping face group.** Main crown plane distance 0.86 → about 0.72–0.78, plus a
       second crown plane next to it. The crown then makes 4–5 big faces, at least 1.5 studs across.
   - **Re-check:** `part_mainlobe` against the Part Close-Up (base widest, broad crown); f34_sheet profile still
     within ±0.07; FL and FR front feet at h .13–.15 (±0.06); no jagged lower edges in `junc_cu`.
2. **Minor: lit and shade contrast.** The clay lit quartile is 19 below the sheet's, and the soil and rock lit
   quartiles 8–20 below. This comes from the studio light and isn't paint. Don't fix it by facing. Optionally ease
   `CLAY_LOW_MIX` from 0.5 to about 0.4 (our bottom third is 7 darker than the sheet's).
3. **Minor: the soil key never shows.** Every visible pad face is a 25 % or 50 % soil_dark mix (the contact radius
   0.35 / 0.8 on the dense post-union mesh covers the whole top), so no contact ring reads. The median still matches
   (#87644B against #856248). Either narrow `SOIL_CONTACT` to about (0.2, 0.5), (0.45, 0.25) and recalibrate `m023_soil`
   so the median holds, or record that the pad is one darker blend.
4. **Minor: rocks.** The rim rocks read smaller and sit further out than the sheet's, in the top view especially. R6
   and R7 at the right are mostly hidden behind FR in the f34 (the sheet shows both clearly at f .85–.95). Optionally
   R7 rf 0.86 → 0.92 at az about 15°, and the ground rocks rf 0.93–0.98 → 0.88–0.92.
5. **Minor (known, accepted): rear cell layout and rock share, side and top widths, rear and side darkness from the
   lighting.**
6. **Minor: the `under_cu` render is unlit.** Add a fill light below or raise the elevation so the chamfer band can be
   judged. This is not a model fault.

## Round 2 fixes (modeller)

Fresh modeller, 2026-10-28. Background session on port 9880 with `wip/M023.blend` (saved after the final build). The
builder `m023.py` is the source of truth; `build()` takes about 27–35 s with renders and returns `problems: []`.
Scratch scripts (build, measure, clay bottom line, key areas, comparisons) are in the scratchpad folder `m023r2/`.

### 1. Blocker: lobe shape — fixed (pending the round-2 verifier)

**What changed.** The plane-dual spheroids are gone. I first tried the suggested parameter route (cut b 0.38 / 0.3,
19 / 15 planes, jitter 0.13, `ang` 0.3, a two-plane crown at 0.75 / 0.77, then triangulating and nudging vertices).
The lobes came out as angular crystal blocks with vertical sides, and the faces still had valence-3 corners. The sheet's
Part Close-Up and hero lobes have big triangles meeting at 5–6-edge vertices, which is what a convex hull of points
gives, not a plane dual. So `_lobe` is now the **convex hull of jittered point rings plus explicit crown points**
(`K.hull_rock`'s recipe, inline so it keeps the layout's yaw, lean and fitted box). `_dual_hull`, `_perp` and the
pokes are removed.
- `KINDS` (rings are (height fraction, radius fraction, points); radial / height jitter 0.07, azimuth jitter 0.3 of a
  step, crown jitter 0.05):
  - **main:** rings 0.0 / 0.96, 0.12 / 1.0, 0.38 / 0.97, 0.6 / 0.88, 0.8 / 0.7, then a 5-point crown at r 0.4–0.5,
    h 0.9–1.0, sloping to the front;
  - **squat** (FR, FL, the Lobe part): rings 0.0 / 0.96, 0.2 / 1.0, 0.42 / 0.97, 0.62 / 0.86, 0.8 / 0.66, then a
    5-point near-flat crown;
  - **tall** (BL, BR): rings 0.0 / 0.95, 0.2 / 1.0, 0.45 / 0.95, 0.66 / 0.84, 0.84 / 0.64, then a crown longer along
    local x.
- Every lobe is a dome now: a short lower band that tucks in a little, the widest ring just above the pad top, steep
  lower sides, a shoulder band at about 45°, and a broad crown. With only one shoulder ring (round 2a/2b) the lobes
  read as tall cubes with flat lids against the sheet's domes.
- **Sinking.** `LOBES` no longer carries Hup and b. Each hero lobe's base is `LOBE_SINK` 0.3 below the lowest pad top
  under its footprint (`_lobe_base`, ray-cast at 0, 0.4 and 0.7 of the half-extents; the outer edge isn't sampled
  because FR's and BR's edges reach over the rim). The top z stays as laid out, so H = top − base. The parts are built
  at `PART_H` (Main 3.94, FR 2.62: round 1's heights).
- **Layout changes** (all measured on the f34 cell):
  - **FR:** 0.25 forward (y −2.25), 0.15 left (x 1.6), top 3.05, and yaw −20° → 0°. With the broad base, the turned
    right end ran over the rim and down the skirt.
  - **FL:** 0.35 forward (y −2.85). Their broad feet now come down to the rim ("Clay overlaps soil base").
  - **BR:** 0.25 right and 0.2 wider (2.5). Its broad-based hull hid behind the main lobe (f34 profile at f .80 / .85
    read .64 / .52).

**Measured shape** (`meas.py`: hull slices, bottom face and crown faces; crown = faces with normal z > 0.75 in the top
20 %):

| Part | Size | Bottom face (fraction of max) | Widest at | Width at h .5 / .7 / .9 | Crown faces, span | Median edge |
| --- | --- | --- | --- | --- | --- | --- |
| MainLobe, round 1 | 4.57 × 4.33 × 3.94 | 3.4 × 3.6 (≈ 0.76) | ≈ 0.5 h | — | 1 broad face + pokes | — |
| MainLobe, round 2 | 4.74 × 4.52 × 3.94 | 4.34 × 4.14 (0.91 / 0.92) | 0.2 h (4.66) | 4.36 / 3.76 / 2.95 | 8, 2.81 × 2.97 | 1.46 (p90 2.16) |
| Lobe (FR), round 2 | 4.3 × 3.92 × 2.62 | 3.91 × 3.89 (0.91 / 0.99) | 0.4 h (4.21) | 3.97 / 3.17 / 2.15 | 7, 1.86 × 2.55 | 1.19 |

- **Hero lobes:**

  | Lobe | Base z | H | Faces |
  | --- | --- | --- | --- |
  | Main | 0.82 | 3.93 | 80 |
  | FR | 0.51 | 2.54 | 78 |
  | FL | 0.70 | 1.50 | 70 |
  | BL | 0.67 | 2.33 | 72 |
  | BR | 0.34 | 2.41 | 66 |

  Each base is 0.3 below the lowest pad top under its footprint. The base sits 0.41–0.75 below the pad top at the
  lobe's centre, because the pad top is domed.
- **The facets** are now big irregular triangles meeting at 5–6-edge vertices, with no soccer-ball pentagons. Split
  facets of slightly different tone appear where the jittered hull points lie nearly coplanar.

**Re-checks:**
- **`part_mainlobe` against the Part Close-Up** (scratch `cmp_part.png`). The base is now the widest part, the crown is
  a broad group of faces, and the sides are big triangles.
  - It is still taller than the close-up (h/W 0.83 against about 0.45). That is decision 3 (4.0 tall, the hero
    governs), so the part reads as a tall dome rather than the close-up's squat mound.
- **f34_sheet (0, 14):**
  - W : H 1.589 (sheet 1.689; round 1 1.583).
  - Shares K .718 / S .216 / R .066 (sheet .709 / .228 / .063).
  - Top profile mean .028, max .08. The max is the single extreme-left column (rock R2's flank: .16 against .24).
    Every other point is within .07. Moving R1 / R2 out flips that column to R1's top (.33), so neither setting fits
    it exactly.
- **front_sheet:** W : H 1.740 (1.739); shares .709 / .225 / .066; profile .033 / .09.
- **Clay bottom line** (lowest clay pixel per column, f34, sheet / ours):
  - **FL** (f .25–.35): .16 / .15 / .15 against .16 / .15 / .19.
  - **FR** (f .50–.85): .17 / .15 / .13 / .13 / .13 / .13 / .17 / .25 against .23 / .20 / .18 / .14 / .12 / .12 /
    .12 / .16.
  - So FL and FR's front feet sit at h .12–.19, against .21–.26 in round 1. FR's left end at f .50 is still .06 high:
    that is where R5 stands in front of it.
- **`junc_cu`.** The lobes come straight down onto the soil with clean creases. There is no jagged notch and no dark
  undercut flank, because the lower band now leans out instead of under. R4 sits sunk between BL and FL.
- **Kit views.** The main lobe's back crown points were raised (0.88 → 0.93) because the kit side view had read the
  crown as a peaked roof.

### 2. Minor: lit / shade contrast and the clay low band — partly

- `CLAY_LOW_MIX` 0.5 → 0.4.
- **f34 clay thirds,** top / mid / bottom: ours #DF693B / #DC673B / #D05F36 against the sheet's #EB6E42 / #D9643A /
  #CD5D34. The bottom third is now within 3 of the sheet's.
- **Parts shot, main lobe:** bottom third #C65931 against the mid's #DC6639, so 22 levels darker (target 15–35).
- **Lit quartile:** still about 16 below the sheet (#EC7244 against #FC8355). That is the studio light, not paint, and
  I left it alone.

### 3. Minor: the soil key never showed — fixed

- **Changes:** `SOIL_CONTACT` (0.35, 0.5), (0.8, 0.25) → (0.2, 0.5), (0.45, 0.25), and the `SOIL_PATCH` levels
  0.12 / 0.4 → 0.25 / 0.45.
- **Visible pad area by key** (faces with normal z > −0.5):

  | Key | Round 1 | Round 2 |
  | --- | --- | --- |
  | plain soil | 0 | 8.3 |
  | 25 % mix | 19.0 | 15.7 |
  | 50 % mix | 27.0 | 14.6 |

- **Result:** in the top view the plain soil reads on the open pad and a darker ring reads round the lobe feet and
  rocks. The floor cap stays plain soil.

### 4. Minor: rocks — partly

- **Moved in:** the front and back ground rocks R5 (0.95 → 0.92), R8 and R9 (0.95 / 0.96 → 0.9).
- **R7:** az 26 → 24 and 0.86 → 0.88. With FR unturned, it shows beside FR's right flank in the f34, as on the sheet.
  The suggested az 15 / 0.92 put it at f .95 instead of the sheet's .85–.92.
- **R1, R2 and R6 stay near the old radii.** They are the f34 silhouette's ends. Moving them in to 0.9 dropped the hero
  W to 9.83 and W : H to 1.556, and pushed the end profile error to 0.14.
- **Hero D is now 9.3,** within 9.6 ± 0.4. It was 9.71 while R8 and R9 stuck out at the back.
- **The top view** still draws its rocks larger (the top camera's magnification, §3.4).

### Calibration (two passes, after the reshape)

1. **Pass 1** (`m023.calibrate()` on the dome) gave the same keys as round 1: clay #A7502A, clay_low #95451D,
   clay_light #AF562D, soil #785D49, soil_dark #5E4835, rock #7C6D6E.
2. **Pass 2** (the new hero's f34_sheet against the f34 cell), factors in linear light:

   | Family | Measured | Sheet | Factor |
   | --- | --- | --- | --- |
   | Clay | #D76339 | #DA653A | × (1.032, 1.043, 1.034) |
   | Soil | #85634A | #856248 | × (1.0, 0.979, 0.946) |
   | Rock | #9A837D | #95837D | × (0.93, 1, 1) |

| Key | Final hex | Roughness |
| --- | --- | --- |
| m023_clay | #AF5329 | 0.8 |
| m023_clay_low | #9D471E | 0.8 |
| m023_clay_light | #B8592C | 0.8 |
| m023_soil | #785C47 | 0.95 |
| m023_soil_dark | #5E4733 | 0.95 |
| m023_rock | #786D6E | 0.9 |

**Final medians, ours / sheet:**

| Region | Ours | Sheet |
| --- | --- | --- |
| f34 clay | #DA663A | #DA653A |
| f34 soil | #866348 | #856248 |
| f34 rock | #95837D | #95837D |
| front clay | #DA663B | #DA673E |
| Parts shot, main lobe clay | #DA6538 | #D4633B (target within 8) |
| Parts shot, soil base | #9E7759 | #987054 (within 8) |
| Parts shot, rock | #8F7E79 | #917F7C |

- **Rear and side cells:** still darker than the sheet (rear clay #B55633 against #D36038). That is the studio key
  light at the front (known, round 1 item 5).

### Checks (final build)

| Object | Tris | Size | Shells | NM edges / verts | Boundary / wire / loose | Zero-area / n-gons / dups | Self-hits | Min corner | UV islands / overlaps / gap / border / p95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RedClayDeposit | 1200 / 4000 | 10.01 × 9.30 × 4.75 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 5.01° | 215 / 0 / 0.016 / 0.008 / 1.034 |
| SoilBase | 232 | 9.76 × 9.27 × 1.24 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 5.08° | 15 / 0 / 0.016 / 0.008 / 1.027 |
| MainLobe | 80 | 4.74 × 4.52 × 3.94 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 6.16° | 9 / 0 / 0.016 / 0.008 / 1.069 |
| Lobe | 80 | 4.30 × 3.92 × 2.62 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 8.61° | 11 / 0 / 0.016 / 0.008 / 1.05 |
| Rock | 36 | 1.18 × 1.08 × 0.99 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 24.5° | 10 / 0 / 0.016 / 0.008 / 1.06 |

- **Every object:** normals outward, rotation 0, scale 1, UV density 1.0.
- **Guards:** the hero guard passed on attempt 0, and `M.fix_bowties` found 0 bowties on every object.
- **Reports:** `K.check` reports nothing, and `problems` is empty.
- **Hero materials:** 9.
- **Stages 5 and 6:** unchanged (no emission, no VFX, decision 8).

### Left for the verifier

- **Main lobe part:** it is taller than the Part Close-Up (decision 3). Its character now matches the close-up: a
  broad base, a broad crown and big triangles.
- **f34 profile:** the one extreme-left column reads .08 (R2's flank).
- **FR's left foot** at f .50 is .06 high, behind R5.
- **Known misses as before:** the rear cell's lobe layout and rock share (.096 against .070), the side and top widths,
  and the rear and side darkness.

## Stage 7 — Verification (round 2)

Independent verifier (not the round-1 verifier), 2026-10-28. Read-only background session on port 9880 with
`wip/M023_verify.blend`; nothing was saved or rebuilt, and `build()` was not called. Fresh renders went to the
verifier's scratch folder (`v023r2/renders/M023/`, with `M.MODEL_RENDERS` redirected), and the side-by-side crops to
`v023r2/cmp_*.png`.

**Verdict: PASS, 7.5 / 10.** The round-1 blocker's re-checks are all met and everything technical passes. What is
left is minor: the main lobe reads as a rounded upright block in the side, rear and part views (item 2).

### Re-measured (own bmesh code plus `M.audit`, `m016._self_hits`, `m012._thin`, `M.uv_stats`, `K.check`)

| Object | Tris | Size | Shells | NM edges / verts | Boundary / wire / loose | Zero-area / n-gons / dups | Inverted faces | Self-hits (own BVH / m016) | Min corner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RedClayDeposit | 1200 / 4000 | 10.01 × 9.30 × 4.75 (target 10.0 ± 0.4, 9.6 ± 0.4, 4.75 ± 0.2) | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 / 0 | 5.01° |
| SoilBase | 232 | 9.76 × 9.27 × 1.24 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 / 0 | 5.08° |
| MainLobe | 80 | 4.74 × 4.52 × 3.94 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 / 0 | 6.16° |
| Lobe | 80 | 4.30 × 3.92 × 2.62 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 / 0 | 8.61° |
| Rock | 36 | 1.18 × 1.08 × 0.99 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 / 0 | 24.5° |

- **Inverted faces:** an odd-crossing ray from each face centre along its normal finds 0 on every object, and the
  signed volumes are positive.
- **Self-hits:** 0 BVH overlap pairs that share no vertex.
- **Min corner:** 5.01° is above the 5° polish limit.
- **Every object:**
  - origin at the bottom centre (local bbox centre 0, 0; z min 0), rotation 0, scale 1;
  - no modifiers, no custom normals, all faces flat shaded;
  - one `UVMap` plus the `Tint` attribute;
  - no children (no VFX, decision 8).
- **UV:** hero 215 islands, parts 15 / 9 / 11 / 10. 0 overlaps, 0 flipped, min gap 0.016, border 0.008, density 1.0,
  conformal p95 1.027–1.069.
- **Materials** (9 on the hero):
  - clay #AF5329; clay_low × clay 50 / 75 #A64D24 / #AA5026; clay × light 25 / 50 #B1542A / #B4562A;
  - soil #785C47; soil × dark 25 / 50 #725742 / #6B523D;
  - rock #786D6E.
  - Roughness clay 0.8, soil 0.95, rock 0.9; metal 0; emission 0.
  - The visible soil now shows the plain key. Areas: plain 74.9 (including the floor cap), 25 % 17.4, 50 % 16.5.
- **No colouring by facing.** `K.check` reports nothing. The builder paints by face-centre height (`_paint_lobe`'s
  low band and upper patch), a noise field and crease distance, never by normal. The clay keys span only 14 levels
  (#A64D24 – #B4562A). The per-face correlation of key luminance with normal z (0.75 on clay) comes from the height
  band on dome geometry, not from a facing rule.

### Round-1 blocker re-checks

| Re-check | Result |
| --- | --- |
| Broad flat base | MainLobe slice widths (X × Y) at h .02 / .2 / .5 / .7 / .9: 4.39×4.21 / 4.66×4.41 / 4.36×3.93 / 3.76×3.47 / 2.95×2.75. The bottom is 0.94 / 0.95 of the max, widest at 0.2 h. **Met.** |
| Big irregular triangles | 80 tris, vertex valence 3–9 (mostly 6–7), no soccer-ball pentagons. The facets read as broad irregular triangles in `part_mainlobe` and the hero. **Met.** |
| Broad crown | 4 faces with normal z > 0.9 (3.67 sq studs), 8 with z > 0.75. **Met.** |
| Front feet heights (f34 lowest clay, fraction of H; sheet / ours) | FL f .25 / .30 / .35: .16 .15 .15 / .16 .15 .19. FR f .50 / .55 / .60 / .65 / .70: .17 .15 .13 .13 .13 / .23 .20 .18 .14 .11. Within ±0.06, except f .50 (+.06, behind R5). **Met.** |
| f34 profile | Mean .028, max .08 (one extreme-left column, R2's flank). Shares K .718 / S .216 / R .066 against .709 / .228 / .063. W : H 1.589 against 1.689. **Met.** |
| Clean junction (`junc_cu`) | The lobes come straight down onto the soil with clean creases; no jagged notch, no undercut flank. R4 sits between BL and FL. **Met.** |

### Views against the sheet

Crops: `cmp_f34`, `cmp_r34`, `cmp_front`, `cmp_side`, `cmp_rear`, `cmp_top`, `cmp_part`, `cmp_expl`, `cmp_lobe`,
`cmp_base` and `cmp_junc`.

- **f34 and front:** five orange lobes on the brown pad, with grey rocks round the rim. The composition and
  proportions read as the sheet's. Front W : H 1.740 against 1.739, profile .033 / .09, shares within 1 point.
- **r34 (f34 flipped):** profile .049 / .11, shares within 1.7 points.
- **Side:** W : H 1.591 against 1.475 (accepted), profile .059 / .18 (the wider pad, accepted).
- **Rear:** W : H 1.83 against 1.647, rock share .096 against .070, one lobe cluster per side (accepted).
- **Top:** W : D 1.074 against 0.925 (accepted), profile .024 / .06. The dark speckle on BR in `top_sheet` is render
  noise in the main lobe's shadow, not paint.
- **Main lobe character.** In the side, rear, exploded and part views the main lobe reads as a rounded upright block,
  where the sheet's is a rounder dome. The height itself is decision 3.
  - Its lower flanks are near-vertical: 41 % of its area has |normal z| < 0.26.
  - Its shoulders are squared and its crown is a flat plateau. The f34 profile reads .97–.99 flat across f .40–.60,
    where the sheet peaks at .55 and falls to .93 at .40.
- **Lobe part** (`cmp_lobe`): squarer than the sheet's wide, low lobes (same recipe).
- **Soil base part** (`cmp_base`): flatter and smoother-skirted than the sheet's chunky, bumpy slab.
- **Exploded:** at true hero scale, so the parts look smaller than the sheet's enlarged ones (known).

### Colours, sheet against ours (`m023.measure()` masks; Δ = ours − sheet)

| Region | Sheet | Ours | Δ |
| --- | --- | --- | --- |
| f34 clay median / lit / shade | #DA653A / #FC8355 / #AE4D2A | #DA663A / #EC7244 / #9A4728 | 0,+1,0 / −16,−17,−17 / −20,−6,−2 |
| f34 clay thirds top / mid / bottom | #EB6E42 / #D9643A / #CD5D34 | #DF693B / #DC673B / #D05F36 | −12,−5,−7 / +3,+3,+1 / +3,+2,+2 |
| f34 soil median / lit / shade | #856248 / #9F7556 / #664D3A | #866348 / #9B7358 / #503B2A | +1,+1,0 / −4,−2,+2 / −22,−18,−16 |
| f34 rock median / lit / shade | #95837D / #B8A298 / #6C5E58 | #95837D / #A28F89 / #736662 | 0,0,0 / −22,−19,−15 / +7,+8,+10 |
| front clay / soil / rock | #DA673E / #8B674D / #99847B | #DA663B / #856348 / #95837D | 0,−1,−3 / −6,−4,−5 / −4,−1,+2 |
| side clay / soil / rock | #DC663C / #87644C / #81716A | #CC603B / #89664C / #8C7B76 | −16,−6,−1 / +2,+2,0 / +11,+10,+12 |
| rear clay / soil / rock | #D36038 / #8A664C / #928178 | #B55633 / #6F5440 / #7B6F6E | −30,−10,−5 / −27,−18,−12 / −23,−18,−10 |
| top clay / soil / rock | #DA683F / #745642 / #998882 | #D0613A / #826249 / #877875 | −10,−7,−5 / +14,+12,+7 / −18,−16,−13 |

- **Medians** in the hero and front views match within 6 levels.
- **Lit quartiles** are 16–22 levels duller, and the soil shade 16–22 darker. That is the studio light's contrast, not
  paint.
- **The rear and side** are darker because the key light stays at the front (known).

### Items

1. **Round-1 blocker (lobe shape): resolved.** Every re-check above is met.
2. **Minor: the main lobe reads as a rounded upright block** in the side, rear and part views; the sheet's is a rounder
   dome. Not required to pass. An optional cheap tweak in `KINDS["main"]` rounds the shoulders off and also brings
   the f34 profile at f .35–.45 down towards the sheet's .89 / .93 / .95:
   - pull the upper rings in: 0.38 / 0.97 → 0.93, 0.6 / 0.88 → 0.82, 0.8 / 0.7 → 0.62;
   - move the crown points in: r 0.4–0.5 → 0.32–0.4.
3. **Minor: the Lobe part and the squat hero lobes** are squarer than the sheet's wide, low lobes (same recipe as
   item 2).
4. **Minor: the soil base** is flatter and smoother than the sheet's chunky, irregular, bumpy slab. It is unchanged
   since round 1, and the hero hides most of it.
5. **Minor: lit and shade contrast** (the studio light). The f34 clay top third is 12 levels below the sheet's.
6. **Minor: FR's left foot** at f .50 is .06 high (behind R5), and the extreme-left f34 column reads .08 (R2).
7. **Minor (known, accepted):**
   - the side and top widths;
   - the rear lobe layout and rock share;
   - the rear and side darkness;
   - the unlit `under_cu` render;
   - the exploded shot at hero scale.

## Main session after verification round 2 (2026-10-28)

Applied the verifier's optional minor 2: the main lobe's upper rings went 0.97/0.88/0.7 → 0.93/0.82/0.62 and its crown points moved in (r 0.4–0.5 → 0.32–0.4), so it reads as a dome rather than an upright block. The rebuild in the kit file gave a hero of 1198 tris, one shell, 0 non-manifold verts, `problems` empty, `K.check` clean. Export: 0 problems.
