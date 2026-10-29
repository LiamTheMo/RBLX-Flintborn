# 031 Cave Mushroom — spec

Reference: `art/blender/assets/references/031.png`. The sheet's own title is "CAVE MUSHROOM", with "27 / 132" at the top
left and "FLINTBORN — INDIVIDUAL MODEL STUDY" at the top right and in the footer (INDEX.md row 31 calls it "Cave Mushroom
Construction Study"; the page number on the sheet is not the index number). The image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m031.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`
(one modeller does stages 1–6 in a background Blender; then a fresh verifier does stage 7).

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect and says so** ("No additional details, variants, or effects", §7).

Sheet text:
- **Header:** none beyond the title (no description sentence).
- **Views:** Front Three-Quarter, Rear Three-Quarter, Front, Side, Rear, Top.
- **Exploded Construction:** labels Mushroom Cap, Cap Underside, Mushroom Stalk, Rock Base. Two mushrooms are drawn
  exploded (the big one in the centre and a mid-size one at the right, each as cap → underside disc → stalk, with
  dashed arrows down into sockets in the base), and a third, small mushroom stands assembled on the base at the left.
  Each stalk has a short cylindrical peg on its top; each underside disc and each stalk bottom has a round hole.
- **Close-ups:**
  - "Cap Underside (close-up)": "Simple faceted underside with flat faces." (a ring of radial flat facets inside the
    orange rim, round the stalk top).
  - "Stalk & Rock Junction": "Stalk bottom with simple cylindrical peg." / "Matching socket in rock base." (a stalk
    foot with a hole over a rock with a round socket).
  - "Base Underside": "Flat, simplified underside with recessed sockets for stalks." (a flat trefoil/peanut-shaped bottom
    with three round recesses).
- **Material palette:** Cap (Top), Cap (Underside), Stalk, Rock (Main), Rock (Small) (§5.1).
- **Modeling notes:** "Keep chunky, low-poly, stylized forms."; "Match the original Flintborn palette and silhouette.";
  "Use broad, flat-shaded faces with no texture noise."; "Model cap, underside, stalk(s) and rock base as separate,
  reusable parts."; "Align pivot at the base center (on ground)."; "Ensure consistent geometry across all views.";
  "Keep topology simple and game-ready."; "No additional details, variants, or effects."
- **Game context:** `src/shared/Resources/NodeCatalog.luau` has the node **`CaveMushroomPatch`** (material
  `CaveMushroom`, health 4, `REGROW.Basic`, mastery Farming — the same stats as `ThornShrub` and `FrostShrub`);
  `BiomeCatalog.luau` spawns it in Cave and Forest habitats (Pinewood Wilds, Mosswick Forest, Emberhollow Caves). Its
  placeholder look is a 2 × 2 × 2 ball. WorldModeling §6.8 (mushroom recipe: lathed/ring cap with "a small top ring,
  wide shoulder ring, lower rim, and shallow underside inset", 6–10 sectors, short tapered stalk, "The cap needs an
  underside") and §9 table: "Cave moss / cave mushrooms: … Their visibility should come from shape and placed lighting,
  not automatic emission." The old **R07 kit sheet** has `CaveMushroom` (built 7.7 × 5.9 × 5.4: three cream-stalked
  rust-capped mushrooms on grey rocks, `harvest_hit` + `harvest_deplete`, plus parts and drops) and owns its names
  (§8). `MODEL_PROGRESS.md` row R07 marks it "mostly-done: no gill ring; slim stalks; pale flat base", and its goals
  file (`art/blender/renders/kit/R07/cave_mushroom_goals.md`) left open "caps read as ~12–16 large facets" (it used
  subdivided domes), "rock ring lumpy, not a flat pillow" and "top view: three separate caps with rocks round the rim".

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is
`#F2EDE8` (242, 237, 232); each view's paper is the median of its box's top and bottom 4 rows. The cell labels are
blanked to paper before measuring (`m.py`, `BLANK`). The masks are `cls()` in `m.py` (HSV; background = within 14 of
the paper):
- **C, cap (orange):** hue ≤ 24° or ≥ 345°, sat ≥ 0.38, v ≥ 0.22.
- **K, cream (stalks and the cap undersides):** hue 26–50°, sat ≥ 0.13, v ≥ 0.55, and not C.
- **R, rock:** anything else with sat < 0.26 and v < 0.84.
- **O, other:** the soft ground shadow (left of the hero in the f34/r34) and anti-aliased edge pixels; **treated as
  background, not counted in any share.**
- Known leaks: the deepest-shaded underside pixels near the rim (hue 19–20°, sat 0.74) fall into C; a few warm-shaded
  rock faces (hue 26–31°) fall into K (≤ 1.5 points in the bottom band). Use the same scripts on both images.

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m031_study\`.
Run with the scratch venv `...\scratchpad\venv22\Scripts\python.exe` (Pillow + numpy).
- **Helpers:** `m.py` (masks `cls()`, view boxes `V`, label blanking, `stats`), `lab.py` (connected components),
  `bb.json` (silhouette boxes), `crop.py`, `grid.py`.
- **Measurements:** `measure.py` → `measure_out.txt` (bboxes, shares, top and bottom profiles, width per height, shares
  per 0.1 h); `caps.py` → `caps_out.txt` (each cap: extents, W : H, share, width per cap height, rim line); `stalks.py`
  → `stalks_out.txt` (stalk and underside widths per height); `rocks.py` → `rocks_out.txt` (rock band top and stalk
  feet per column); `topsplit.py` → `topsplit_out.txt` (the top view's three caps split, outline radius by angle);
  `expl.py` → `expl_out.txt` (exploded parts).
- **Colour:** `samp.py` → `samp_out.txt` (views, caps and cap thirds, regions, parts, close-ups); `grad.py` →
  `grad_out.txt` (bottom → top along stalks, caps and rocks).
- **Names:** `blendall.py` (every sheet, kit and wip `.blend`, zstd-decompressed).
- **Crops:** `f34.png`, `r34.png`, `row2.png` (front, side, rear, top), `expl.png`, `cu.png` (the three close-ups),
  `pal.png` (palette and notes); grids `g_*.png` (10 % grid on the silhouette bbox, red = centre lines); mask previews
  `cls_*.png`, `cls_row2.png`, `cls_expl.png`, `top_split.png`.
- **Zooms:** `z_expl_top.png` (caps, discs and stalks), `z_expl_base.png` (the rock base and the assembled small
  mushroom).
- **To run the scripts on our renders,** point `R` (in `m.py`) at the render, set the view box in `V`, drop `BLANK`,
  and re-run `measure.py` (it rewrites `bb.json`), then `caps.py`, `stalks.py`, `rocks.py`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a common Farming resource node, `CaveMushroomPatch`). Hero budget 4000 tris, each
  part under 1000. The plan in §4.3 lands at about 1400–1900.
- **Overall read (check this first).** A cluster of **three chunky mushrooms** with broad faceted rust-orange domed
  caps on fat cream stalks, standing in a **lumpy ring of warm-grey boulders**. Front W : H 1.22.
  - **one big mushroom** at the back-centre: a tall faceted **dome cap** (cap Ø ≈ 0.70 W, cap visible W : H 1.75 —
    a dome, **not a flat disc, not a ball, not a cone**) with a dark lip band under its widest ring and a **tan
    underside band** showing below the rim; a fat cream stalk tapering upward, its foot hidden by the rocks;
  - **a medium mushroom at the front-left** (cap Ø 0.51 of the big cap's) and **a small one at the front-right** (cap
    Ø 0.43 of the big cap's), each **leaning outward** away from the big one (14–20°), their caps lower than the big
    cap's rim;
  - **eleven or so rocks**: one big low dome rock in front of (and under) the big stalk, two bigger rocks at the back,
    and small darker rocks round the rim and under the small mushrooms. The rocks make an unbroken band in the bottom
    20 % of every elevation view.
  - Hero shares (front): cap 44.9 %, cream 24.5 %, rock 30.6 %.
- **Focal silhouettes, in order:**
  1. The big dome cap: the top 30 % of every elevation view is cap only (≥ 97 % C at h .7–1.0).
  2. The three-cap stepped outline: medium cap top at h .625 on the left, small cap top at h .47 on the right, both
     tilted outward, both tucked under the big cap's rim line.
  3. The cream band (underside + big stalk) between h .25 and .65, with the stalks' feet hidden in the rock band.
- **Target size: about 4.4 W × 3.5 D × 3.6 H studs** (H = 0.65 C of the 5.5-stud character, the top of WorldModeling's
  0.25–0.65 C forage range; W : H 1.22). Tolerances W ±0.25, D ±0.3, H ±0.2. Decision §8.1.
  - **How it was derived.** The sheet has no character. `CaveMushroomPatch` is a Farming node with exactly the stats
    of `ThornShrub` and `FrostShrub`, so it joins the forage family set by M017 (`BerryBushNode` 4.3 × 3.5 × 3.6), M022
    (`FiberPlantNode` 4.7 × 3.9 × 3.6), M024 (`ThornBushNode` 4.8 × 4.0 × 3.6) and M028 (`FrostBushNode` 4.3 × 3.0 ×
    3.6). The same height puts the big cap's crown at the character's chest, its rim at the waist (z 2.0), the medium
    cap top at the hip, the small at the thigh. The front cell (234 × 192 px) then gives **53.3 px per stud**, the f34
    (430 × 341) **94.7 px per stud**.
  - **Depth:** the side cell D : H 0.970 → 3.49; the layout (§2) gives 3.45 (the front pebbles to the big cap's back
    edge).
  - **Alternatives:** 0.8 C (× 1.22 → 5.4 × 4.3 × 4.4: caps at shoulder height, a bigger "cave" patch), or R07's scale
    (7.7 × 5.9 × 5.4, as tall as the player).
  - Resulting part sizes: big cap Ø 3.0 × 1.6 tall (lip z 2.0 → crown z 3.6); big stalk Ø 1.0 (top) → 1.5 (widest,
    hidden) × 1.4 long; medium cap Ø 1.55, small cap Ø 1.3; big central rock Ø 2.0 × 1.0 tall; small rocks Ø 0.6–0.9.
- **Build frame:** front −Y, +X right, ground z 0, origin = the bbox bottom centre (the layout in §2 is already centred
  on it; stage 2 re-centres exactly).
- **Stud mappings used below** (H 3.6, W 4.4, D 3.5):
  - front cell X = (f − 0.50) × 4.4, z ≈ h × 3.6 (camera about 9° up, §3.1);
  - rear cell X = (0.50 − f) × 4.4 (screen right = −X);
  - side cell Y = (f − 0.50) × 3.5, **screen right = +Y (the back)** for the kit side camera at az 90 (+X);
  - top cell: counts, sizes and shares only (§3.3).

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | Cap C | Cream K | Rock R | Big / medium / small cap share |
| --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (20,74,518,453) | 51–480 × 94–434 (430 × 341) | 1.261 | 43.6 % | 23.3 % | 33.1 % | 26.3 / 10.4 / 6.9 % |
| Rear three-quarter (522,74,1004,453) | 546–962 × 94–433 (417 × 340) | 1.226 | 49.3 % | 17.9 % | 32.7 % | 34.8 / 8.8 / 5.7 % |
| Front (20,457,285,698) | 29–262 × 488–679 (234 × 192) | 1.219 | 44.9 % | 24.5 % | 30.6 % | 27.2 / 10.9 / 6.8 % |
| Side (289,457,518,698) | 300–493 × 481–680 (194 × 200) | 0.970 (D : H) | 44.0 % | 24.2 % | 31.7 % | 33.7 / 10.4 (one small cap) |
| Rear (522,457,771,698) | 531–760 × 485–680 (230 × 196) | 1.173 | 47.6 % | 19.4 % | 33.0 % | 32.4 / 7.8 / 7.4 % |
| Top (775,457,1004,698) | 792–987 × 474–681 (196 × 208) | 0.942 (W : D) | 63.5 % | 0.0 % | 36.5 % | 33.1 / 17.5 / 13.0 % |

- **Glow share: 0 % in every view.** No pixel is self-lit: the brightest cap facets are `#E88860`, the brightest stalk
  facets `#FEEBD5` (lit cream), and every part darkens on its shaded side.
- **Ground shadow:** the soft grey shadow (left of the hero in the f34 and r34, under the rocks elsewhere) is O, i.e.
  background (0.8–0.9 % of each box).
- **Elevations** from the bottom profiles (ends .05–.09 H above the front-centre rock's foot over about 1.3 studs of
  depth): front ≈ 9°, side ≈ 9°, rear ≈ 10°, f34 and r34 ≈ 14°.
- **Verifier tolerance:** shares ±4 points (top ±7); positions and profile values ±0.06 of W/H unless stated.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .12 | .41 | .55 | .60 | .62 | .70 | .81 | .87 | .92 | .95 | .98 | 1.0 | .99 | .96 | .93 | .90 | .85 | .77 | .67 | .43 | .12 |
| Front | .08 | .43 | .55 | .60 | .62 | .71 | .81 | .86 | .91 | .95 | .97 | .99 | .99 | .97 | .95 | .91 | .87 | .82 | .73 | .40 | .27 |
| Side | .07 | .35 | .45 | .49 | .72 | .80 | .86 | .89 | .92 | .95 | .97 | .99 | 1.0 | .98 | .96 | .94 | .91 | .89 | .82 | .77 | .70 |
| Rear | .08 | .39 | .48 | .53 | .75 | .83 | .88 | .91 | .95 | .97 | 1.0 | .99 | .96 | .94 | .90 | .87 | .78 | .69 | .50 | .45 | .13 |
| r34 | .11 | .35 | .48 | .53 | .65 | .77 | .84 | .89 | .93 | .96 | .98 | 1.0 | .98 | .95 | .92 | .88 | .81 | .73 | .45 | .34 | .15 |

- **Front reading:** f .05–.20 is the medium cap's tilted crown (.43 → .62, its top at f .17–.20); from f .25 the big
  cap's shoulder rises over .71 → .99 to its crown at f .55–.60; down the right shoulder to .73 at f .90, where the
  small cap's crown (h .47) is hidden under the big cap's right shoulder in the profile; f 1.0 is the small cap's
  outer edge (.27).
- **Side reading:** the small cap (left, front) .35–.49 at f .05–.15; the big cap from f .20 (.72) to its crown at
  f .60 (1.0); the big cap's back shoulder holds .70–.82 down to f 1.0 (the cap's back edge is the silhouette's back).
- **r34 against f34:** within 0.08 at 18 of 21 points (worst .07 at f .20, .09 at .90): the r34 is the f34 drawing
  again (§3.1).

**Bottom profiles** (lowest silhouette pixel per column above the bbox bottom, fraction of H): front .06 .05 .04 .03
.02 .02 .02 .02 .01 0 0 0 0 .01 .01 .02 .02 .02 .04 .04 .05; f34 .09 → 0 at f .50 → .09; side .06 → 0 at f .55 →
.03; rear .06 → 0 → .07; top (an outline) .42 at the ends.

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .10@.47 1.00@.00 .92@.05 .83@.15 .91@.05 .81@.08 .74@.15 .64@.25 .54@.30 .37@.38 .03@.55
r34    .19@.43 1.00@.00 .89@.09 .90@.05 .87@.06 .60@.12 .68@.21 .64@.22 .53@.27 .35@.36 .02@.53
front  .33@.40  .96@.03 .85@.07 .87@.11 .90@.05 .71@.07 .77@.15 .67@.24 .56@.29 .38@.38 .05@.55
side   .27@.43  .91@.07 .82@.12 .84@.04 .66@.07 .56@.16 .79@.21 .80@.19 .67@.25 .45@.38 .05@.57
rear   .27@.37  .98@.02 .91@.06 .94@.04 .90@.06 .78@.12 .68@.17 .66@.18 .56@.23 .37@.33 .04@.49
```

So: the rock band 0.85–0.98 W at h .1–.2; at h .3–.4 the medium and small caps spread the silhouette to 0.87–0.94 W;
at h .5 a pinch to 0.56–0.78 W (between the small caps' tops and the big cap's rim: the gap where only the big stalk
and underside show, plus the medium cap's crown in the front); h .6–.8 the big cap alone (0.67 W at .7, 0.56 at .8);
above .9 the crown (0.37 W).

**Shares per 0.1 h** (C / K / R in %, front; the f34, side and rear agree within ±10):

```
h  .0-.1  R99            .1-.2  K14 R85        .2-.3  C12 K41 R45     .3-.4  C48 K42 R8     .4-.5  C62 K36 R1
h  .5-.6  C43 K55        .6-.7  C73 K26        .7-.8  C99             .8-.9  C99            .9-1.0 C100
```

The rear: `.0 R99 | .1 K5 R94 | .2 C5 K43 R51 | .3 C52 K37 R9 | .4 C63 K35 | .5 C43 K55 | .6–.9 C99`. The side's
h .5–.6 is cream-heavy (C16 K81): from +X the underside band and big stalk fill the gap.

**Each cap** (`caps.py`; f across and h up as fractions of the view's silhouette bbox; cap-only pixels):

| View | Big cap f / h | Big W : H | Medium cap f / h | Medium W : H | Small cap f / h | Small W : H |
| --- | --- | --- | --- | --- | --- | --- |
| Front | .235–.927 / .521–1.0 | 1.75 | .034–.385 / .318–.625 | 1.38 | .701–.991 / .229–.469 | 1.47 |
| F34 | .244–.902 / .545–1.0 | 1.82 | .042–.379 / .326–.625 | 1.42 | .700–.981 / .270–.516 | 1.44 |
| Side | .175–.995 / .545–1.0 | 1.74 | — (hidden) | — | .041–.418 / .270–.525 | 1.42 |
| Rear | .157–.865 / .546–1.0 | 1.82 | right .687–.983 / .281–.531 | 1.38 | left .035–.335 / .281–.531 | 1.40 |
| R34 | .197–.890 / .521–1.0 | 1.77 | .043–.350 / .279–.544 | 1.42 | .686–.952 / .288–.497 | 1.56 |
| Top | Ø 0.59 W, centre (.37, .59) | — | Ø 0.42 W, centre (.80, .48) | — | Ø 0.36 W, centre (.51, .19) | — |

- **Big cap width per its own height** (front; from its lowest pixel to its crown, 0 … 1): `.02 .13 .95 .99 .94 .87
  .78 .69 .51 .33 .04`. The f34, side, rear and r34 agree within 0.05. So the cap is **widest in its lowest 0.2–0.3**
  (a rim band), then a **dome that narrows faster than a hemisphere** near the top (.69 at 0.7, .51 at 0.8, .33 at
  0.9; a hemisphere would give .71 / .60 / .44 above its rim band): a slightly ogival dome with a small crown.
- **Big cap rim line** (lowest cap pixel per 0.1 of the cap width, front): `.67 .60 .66 .66 .66 .66 .65 .63 .60 .53 .63`
  → level at h .60–.66 across, dipping to .53 at the screen-right end (f34 and side the same, rear level at .56–.59).
- **Medium cap** width per height `.11 .46 .77 .87 .90 .90 .84 .76 .60 .39 .05`; rim line from h .33 (left) to .47
  (right end): **tilted down to the left (outward) by about 13°** in the front, the same in the f34.
- **Small cap** width per height `.09 .38 .59 .75 .87 .90 .90 .77 .65 .49 .14`; rim line from .32 (left) to .23
  (right): **tilted down to the right (outward) by about 17°**; in the side its rim runs .27 (front end) → .35 (back
  end): **tilted forward by about 15°**.
- **Rear:** both small caps tilt outward (left one down to the left by about 16°, right one down to the right by about
  18°).
- **Size ratios** (cap Ø / big cap Ø): front medium 0.51, small 0.42; rear 0.42 / 0.42; side (small) 0.46; top 0.71 /
  0.61 (§3.3).

**Stalks and the underside band** (`stalks.py`; cream width / W at each h, front):

```
big stalk + underside   h .25 .316 | .30 .308 | .35 .291 | .40 .274 | .45 .239 | .50 .312 | .55 .449 | .60 .457 | .65 .124
medium stalk            h .15 .060 | .20 .124 | .25 .192 | .30 .188 | .35 .077          (f .15-.36; feet in the rocks)
small stalk             h .15 .064 | .20 .162 | .25 .124                                  (f .73-.89)
side big stalk          h .25 .356 | .30 .366 | .35 .325 | .40 .284 | .45 .278 | .50 .253 | .55 .531 | .60 .562
rear big stalk          h .30 .335 | .35 .313 | .40 .274 | .45 .261 | .50 .248 | .55 .513
```

- **Big stalk** (front, in studs): Ø 1.39 at z 0.9 (h .25, where it leaves the rock band), 1.35 at z 1.08, 1.28 at
  1.26, 1.20 at 1.44, 1.05 at 1.62. A steady taper upward; its foot is hidden by the central rock (rock top h .28–.32).
  The side shows it 0.9 × the front's width (faceting).
- **Underside band:** cream (tan, §5) from h .49 to the rim at h .60–.66, **0.45 W wide (≈ 2.0 studs = 0.65 of the
  big cap's Ø)** in the front, 0.53–0.56 of the side's width (1.9 studs), 0.51 W in the rear. It is a horizontal band
  under the dark lip, wider than the stalk top on both sides.
- **Medium stalk:** Ø 0.84 (0.19 W) visible from z 0.55 to 1.35; **small stalk:** Ø 0.70 (0.16 W) visible from z 0.4
  to 1.0. Stalk / cap Ø: big 0.35 at the top, 0.46 at the rock line; medium and small 0.54.

**Rock band top** (highest rock pixel connected to the ground, per 0.05 f, front): `.12 .14 .25 .28 .15 .15 .22 .23
.39 .26 .28 .30 .31 .29 .25 .17 .17 .14 .23 .18 .09`. The central rock tops out at h .31 (z 1.1) at f .55; the far-left
rock at .25–.28 (f .10–.15); the small front rocks at .14–.17; a back rock shows between the medium stalk and the big
stalk at f .40 (h .39). The side: `.10 .11 .17 .21 .16 .16 .16 .21 .29 .24 .26 .28 .29 .29 .27 .25 .34 .33 .27 .19`
(the back-right rock at f .80–.85, h .33–.34). The rear: central rock .26–.32, side rocks .16–.24, the back rocks at
f .30 and .70 (h .34–.35).

### 1.3 Silhouette and composition per view

**Front (`g_front.png`; governs the orthographic profiles).** Camera on the front axis, about 9° up.
- **Big mushroom:** cap f .235–.927 (centre .58), crown at f .55–.60. The cap shows about 5 big facets across its upper
  ring, a crown polygon, a ring of tall shoulder facets, and a **dark lip band** (h .60–.70) under the widest ring.
  Below the lip, the **tan underside band** f .31–.83 at h .50–.62; the stalk f .40–.71 at h .3 narrowing to f .43–.68
  at h .45, 2–3 facets across, one horizontal crease at h ≈ .42.
- **Medium (left):** cap f .03–.39 tilted down to the left, its crown at f .17–.20, h .625; its right part in front of
  the big cap's lower-left rim; stalk f .15–.36, visible h .15–.38, its foot behind two small rocks.
- **Small (right):** cap f .70–.99 tilted down to the right, crown h .47, tucked under the big cap's right rim; stalk
  f .73–.89, visible h .12–.28.
- **Rocks:** the big low central rock f .29–.73 (top h .31) in front of the big stalk; the far-left rock f .04–.17
  (top .25); a front-left small rock f .14–.30 (top .14); a front-right small rock f .73–.87 (top .15–.17); the
  far-right rock f .88–.99 (top .19); two dark back rocks peeking between the stalks (f .33–.40 h .28–.40 and f .68–.72
  h .28–.36). About 8 rocks visible, each with 6–12 broad triangular facets.

**Front three-quarter (`g_f34.png`; the hero).** Not a three-quarter: the front composition (caps at the same f within
0.01: big .58, medium .20, small .85) seen from higher (e ≈ 14°). The rocks show more of their tops; the far-left rock
is the biggest small one (f .00–.20, top .28). Shares within 1.5 of the front.

**Side (`g_side.png`; kit camera at +X: screen right = +Y, the back).** The big mushroom fills the right two thirds (cap
f .175–.995, crown f .60, stalk f .41–.70); **one** small mushroom at screen left (front), cap f .04–.42, h .27–.525,
tilted forward. The central rock covers the stalk foot (top .29), a taller back rock at the right (f .77–.92, top .34),
small rocks at the front-left. Read with the plan in §2: from +X the nearest small mushroom is the small one (front-
right); the medium (front-left) would show behind it (§3.2).

**Rear (`g_rear.png`; screen right = −X).** Drawn almost symmetric: big mushroom centred (cap f .157–.865, centre
.51), two equal small mushrooms (caps Ø 0.30 W) at f .04–.34 and .69–.98, both h .28–.53, both tilted outward. The
central rock in front of the big stalk (f .28–.72, top .30), dark back rocks beside the stalk at f .30 and .70, small
rocks at both ends.

**Rear three-quarter (`g_r34.png`).** The f34 drawing again (§3.1): medium cap at the left (Ø .309 W, larger), small at
the right (.269), big cap .197–.890.

**Top (`g_top.png`, `top_split.png`; image top = back by kit convention, §3.3).** Three caps seen from above as faceted
9–10-gons with a pentagon/hexagon crown facet: the big cap at the upper left (Ø 0.59 W, centre (.37, .59)), a mid cap
at the right (Ø 0.42, centre (.80, .48)) and a smaller cap at the bottom (Ø 0.36, centre (.51, .19)); the two smaller
caps 57° apart round the big one. A near-round rock cluster all round (outline radius 0.47–0.56 W at every 15°), with
two rocks at the back (upper middle and upper right) clear of the caps, rocks along the left and bottom-left edges.
Rock share 36.5 %.

**Exploded (`expl.png`, `z_expl_top.png`, `z_expl_base.png`) and close-ups (`cu.png`).** See §1.4.

### 1.4 Parts (Exploded Construction (20,702,619,1320), close-ups (623,702,1004,1320))

Facet language for every part: broad flat-shaded facets, chunky, crisp edges, no noise, no bevel chains.

#### Mushroom Cap — exploded big cap (186,726,447,866) 262 × 141 px; mid-size cap (431,872,581,963) 151 × 92 px

- **Shape:** a faceted **dome** with a broad rim band: widest a little above its lowest edge, then rounding to a
  small crown polygon (a pentagon or hexagon). About **9–10 sectors** and **4 rows** of big facets (lip band, shoulder,
  upper ring, crown ring), rows offset half a step so faces are triangles and kites; the facets on the big cap are
  about 0.6–1.0 stud across. Not an icosphere (R07's subdivided domes were flagged), not a soccer ball, not a smooth
  hemisphere, not a flat disc.
- **Proportions:** exploded big cap W : H 1.86 (orange outline), mid cap 1.64; width per height bottom → top (exploded
  big): `.01 .91 .99 .97 .92 .84 .76 .65 .50 .31 .00` — the same as the hero's (§1.2).
- **Inside the rim:** the exploded cap shows its **underside annulus** in cream-tan (`cream3` (214,837,419,873): 205 ×
  36 px, 0.78 of the cap width) set a little up inside the orange lip: the cap part is closed by its own underside
  (the "Cap Underside" close-up: radial flat facets from the lip in to the stalk).
- **Construction:** `_cap(R, H, n, seed)`: rings (z fraction of the cap height from the lip, radius fraction of R):
  lip (0.00, 0.90), rim (0.18, 1.00), shoulder (0.42, 0.95), upper (0.72, 0.70), crown (0.93, 0.34), apex (1.0, 0) or a
  flat crown polygon at 0.97 with r 0.22. Each ring rotated half a step from the one below; ±4 % radius and ±0.03 H
  jitter per vertex. The underside: from the lip ring a down-facing **gill annulus** of `n` radial facets rising 0.04 H
  inward to the drum's top ring (or to the stalk top on the Cap part). Big cap n = 10, about **100–120 tris**; medium
  n = 9, small n = 8, about 70–90 each.

#### Cap Underside — exploded disc (233,884,392,935) 160 × 52 px; mid disc (463,972,542,1007) 80 × 36 px

- **Shape:** a **thick 12-sided disc** with bevelled top and bottom edges and a central hole underneath. Exploded disc
  Ø 0.61 of the big cap's width, thickness about 0.12 of its own Ø. In the hero its side band is the **tan band seen
  under every cap** (§1.2: 0.65 of the cap Ø wide, about 0.1 H tall below the lip).
- **Construction:** `_underside(r, t, seed)` ("drum"): 12 sides; rings (z from its bottom, radius fraction): (0, 0.88),
  (0.25 t, 1.0), (0.85 t, 1.0), (t, 0.92); flat bottom fan. Big: r 1.0 (Ø 2.0), t 0.40 (z 1.62 → 2.02, its top hidden
  inside the cap above the lip); medium Ø 1.05, t 0.24; small Ø 0.88, t 0.20. **About 90 tris** each (3 bands × 24
  + two 12-gon caps); 10 sides is enough for the medium and small (about 76). Its top end sits
  inside the cap's gill annulus (overlap 0.04 or more), its bottom takes the stalk top.

#### Mushroom Stalk — exploded big (240,952,380,1105) 141 × 154 px (with peg); mid (460,1022,543,1120) 84 × 99 px

- **Shape:** a **bell / squat vase**: flat top (with a short cylindrical peg in the exploded) narrowing to 0.60 of the
  max width; widest at 0.30 of its height; a short taper to a flat bottom at 0.88–0.92 of the max. Width per height
  bottom → top (exploded big): `.21 .92 .96 1.00 .92 .84 .77 .71 .66 .60 .12` (the ends are the hole and the peg).
  About 10 sides with 4 rings offset half a step: kites and triangles, no vertical strips. W : H 0.92 (big), 0.85 (mid).
- **In the hero** only the upper half shows above the rocks; the visible part tapers from Ø 1.39 (z 0.9) to 1.05
  (z 1.62) (§1.2), so the hero stalk is a little less tapered than the exploded one (top / max 0.67 against 0.60).
- **Construction:** `_stalk(r_max, L, seed)`: 10 sides; rings (z fraction, radius fraction of r_max): (0, 0.88),
  (0.15, 0.96), (0.32, 1.0), (0.58, 0.88), (0.82, 0.77), (1.0, 0.67). Big: r_max 0.75 (Ø 1.5), L 1.45 (z 0.25 → 1.70);
  medium r_max 0.47, L 1.0; small r_max 0.40, L 0.8. **About 80–100 tris** (big), 60–70 (others).

#### Rock Base — exploded (95,1134,587,1302) 493 × 169 px; Stalk & Rock Junction (623,912,1004,1121); Base Underside (623,1124,1004,1320)

- **Shape:** a cluster of faceted low dome rocks: **one big central rock** (a wide low dome, W : H about 2, ~20 big
  triangular facets, the big stalk's socket on its crown), **a big rock behind it at the back-right**, a back-left
  rock, and a ring of **small rocks** round the front and sides (the small mushroom stands on one at the left of the
  exploded; the mid mushroom's socket sits among the right-hand rocks).
- **Base Underside:** a **flat** bottom whose outline is a lobed trefoil (three bulges and a notch), with three round
  recesses (sockets) — joinery notation (§8.5).
- **Rock shape language:** squat domes, height 0.45–0.9 of width, 6–8-sided footprints with 2 height rings and a small
  top cluster of faces, flat bottoms; the central rock flatter (h/w 0.5). Not icospheres, not pillows (R07's "main rock
  looks like a flat pillow").
- **Construction:** `_rock(w, d, h, seed)` via `K.hull_rock(..., keep_bottom=True)` or ring recipe `(0.0, 0.92, n),
  (0.4, 1.0, n), (0.78, 0.72, n−1), (1.0, 0.25, 3)` with jitter 0.10: **about 30–40 tris** each, the central rock about
  70–90 (n = 8, one more ring). The hero places 11 (§2.3).

#### Pegs and sockets (exploded and close-ups)

- The stalk-top pegs, the holes in the underside discs and stalk feet, the rock sockets and the underside recesses are
  joinery notation, hidden in every assembled view. **Not modelled in the hero**; the Stalk part keeps its short top
  peg (decision §8.5). No holes anywhere (they need booleans and show nothing).

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, origin = the bbox bottom centre). Azimuths are measured from +X
counter-clockwise (front = 270°, back = 90°).

### 2.1 Mushrooms

| Mushroom | Stalk foot (x, y, z) | Lean | Stalk r_max × L | Underside Ø × t | Cap R × H (lip z → crown z) | Cap centre (expected) | Sheet evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Big | (+0.22, +0.30, 0.25) | 0° | 0.75 × 1.45 (top Ø 1.0 at z 1.70) | 2.0 × 0.40 (z 1.62–2.02) | 1.50 × 1.60 (2.00 → 3.60) | (+0.22, +0.30) | front cap f .235–.927 (centre .58); rear .51; side cap centre .585 (Y +0.30) |
| Medium | (−1.05, −0.58, 0.30) | 16° toward az 215° | 0.47 × 1.00 | 1.05 × 0.24 | 0.78 × 0.83 (≈ 1.25 → 2.2) | (≈ −1.30, −0.76) | front cap f .034–.385 (X −2.05 … −0.51), crown h .625 (z 2.25), rim tilted 13° |
| Small | (+1.36, −0.72, 0.28) | 20° toward az 315° | 0.40 × 0.80 | 0.88 × 0.20 | 0.65 × 0.69 (≈ 0.95 → 1.7) | (≈ +1.55, −0.92) | front cap f .701–.991 (X +0.88 … +2.16), crown h .47 (z 1.69), rim tilted 17°; side cap f .04–.42 (Y −1.6 … −0.29), tilted 15° forward |

- **Big cap ring heights** (absolute): lip z 2.00 (r 1.35), rim 2.29 (r 1.50), shoulder 2.67 (r 1.43), upper 3.15
  (r 1.05), crown 3.49 (r 0.51), apex 3.60. One ring vertex points at the front camera (az 270) so the front shows a
  facet edge near the middle, as drawn. Expected front cap width per its height (from z 1.88, the lowest visible lip
  point at e 9°): .95 at 0.2, .94 at 0.4, .78 at 0.6, .51 at 0.8, .33 at 0.9 (±0.06).
- **Lean:** each small mushroom (stalk, underside, cap together) rotates about its stalk foot, so its cap tilts
  outward, as the front, side and rear all show. Expected rim slopes: medium 13° ±4 down to screen left in the front;
  small 17° ±4 down to screen right in the front and 15° ±4 down to screen left (front) in the side.
- **Contact:** each stalk's top sinks 0.06 into its underside drum; each drum's top sinks 0.04–0.08 into its cap's
  gill annulus; the big stalk's foot sinks 0.7 into the central rock (whose crown is at z 1.0), the small stalks' feet
  0.2–0.3 into their seat rocks.
- **Clearances:** the medium cap must not touch the big cap (min gap ≥ 0.05; the medium's crown at z 2.2 passes in
  front of and below the big cap's lip at z 2.0–2.3 only because it is 1.9 away in plan and leaning away). If it
  touches, move the medium foot 0.1 further toward −Y. The small cap tucks under the big cap's right lip (its crown z
  1.7 is below the lip z 2.0): overlap in plan is expected and fine, contact is not.

### 2.2 Silhouette checks per mushroom (front_sheet render against the front cell, ±0.05)

| Part | f extent | h extent | W : H |
| --- | --- | --- | --- |
| Big cap (orange only) | .235–.927 | .52–1.0 | 1.70–1.85 |
| Medium cap | .034–.385 | .32–.625 | 1.30–1.50 |
| Small cap | .701–.991 | .23–.47 | 1.35–1.60 |
| Underside band | .31–.83 | .49–.62 | — (0.40–0.50 W wide) |
| Big stalk (visible) | .40–.71 at h .30 | .25–.49 | width .31 W at h .30, .24 at h .45 |

### 2.3 Rocks (11)

| Rock | Centre (x, y) | w × d × h | Key | Sheet evidence | Seat |
| --- | --- | --- | --- | --- | --- |
| R1 central | (+0.10, +0.05) | 2.05 × 1.95 × 1.00 | `rock` | front f .29–.73, top h .31; rear f .28–.72, top .30; side central top .29 | the big stalk stands on its crown; low wide dome (h/w 0.5) |
| R2 back-right | (+0.95, +1.15) | 1.30 × 1.20 × 1.05 | `rock` | side f .77–.92 top .34; top view upper-right rock; front dark f .68–.72 | behind the big stalk, overlapping R1 by 0.3 |
| R3 back-left | (−0.80, +1.05) | 1.20 × 1.15 × 0.95 | `rock` | top view upper-middle rock; front dark f .33–.40 h .28–.40 | behind the big stalk's left |
| R4 medium's seat | (−1.00, −0.52) | 1.10 × 1.00 × 0.45 | `rock_small` | exploded: the small mushroom on a low rock | under the medium foot |
| R5 small's seat | (+1.30, −0.66) | 0.95 × 0.90 × 0.40 | `rock_small` | exploded: a socket among the right rocks | under the small foot |
| P1 front-left | (−1.20, −1.30) | 0.75 × 0.70 × 0.50 | `rock_small` | front f .14–.30, top .14 | on the ground, against R4 |
| P2 far-left | (−1.80, −0.35) | 0.80 × 0.80 × 0.85 | `rock_small` | front f .04–.17, top .25–.28; f34 far-left (the biggest small one) | on the ground |
| P3 left-back | (−1.70, +0.70) | 0.80 × 0.75 × 0.70 | `rock_small` | top view left edge; rear right end | on the ground |
| P4 front-right | (+1.30, −1.30) | 0.65 × 0.60 × 0.55 | `rock_small` | front f .73–.87, top .15–.17 | in front of the small stalk |
| P5 far-right | (+1.90, −0.40) | 0.60 × 0.60 × 0.70 | `rock_small` | front f .88–.99, top .19 | on the ground |
| P6 right-back | (+1.75, +0.60) | 0.75 × 0.70 × 0.60 | `rock_small` | top view right edge; rear left end | on the ground |

- **Embedding:** rocks overlap their neighbours by 0.1–0.3 (never coplanar), flat bottoms at z 0 (the floor cut
  makes them one flat underside), each rock yawed by its own seed.
- **Expected:** rocks X −2.2 … +2.2 (front rock band 0.96 W at h .1), Y −1.65 … +1.75, tops z 0.4–1.05; the rock
  band h .0–.2 ≥ 85 % rock in the front, side and rear.
- **Expected hero:** X −2.2 … +2.2 (P2, P5 and the small cap's outer edge), Y −1.65 … +1.80 (the front pebbles P1/P4,
  the big cap's back edge), z 0 … 3.6 → **4.4 × 3.45 × 3.6** (inside the 3.5 ±0.3 target).

### 2.4 Checks on the renders

- **front_sheet (0, 9):** W : H 1.15–1.29 (sheet 1.219); shares ±4 of 44.9 / 24.5 / 30.6; the cap table §2.2; top
  profile ±0.06; width per height ±0.07 (the h .5 pinch at 0.71 W); shares per 0.1 h ±12 per class; the underside band
  visible.
- **f34_sheet (0, 14):** shares ±4 of 43.6 / 23.3 / 33.1; caps per §1.2 ±0.05; W : H 1.20–1.32.
- **rear_sheet (180, 9):** shares ±4 of 47.6 / 19.4 / 33.0; the big cap f .157–.865 (±0.08, §3.4); both small caps
  tilted outward, tops h .45–.62.
- **side_sheet (90, 9):** D : H 0.92–1.04 (sheet 0.970); the big cap's crown at f .55–.65; the small cap at screen left
  tilted forward; shares ±5 (§3.2).
- **r34:** compare with the f34_sheet render (§3.1): shares ±5 of 49.3 / 17.9 / 32.7, profile ±0.08.
- **Top (0, 89):** three caps, rocks visible all round the rim, cap share 60–75 % (§3.3).

## 3. View conflicts and resolutions

### 3.1 Both three-quarter cells are the front composition from higher up

- **Evidence.** The f34's three caps sit at the front cell's f within 0.01 (big .58, medium .20, small .85), with a
  symmetric bottom ellipse (.09 / .09 at the ends): an aligned front view at e ≈ 14°. The r34 keeps the larger cap at
  the left (Ø .309 W against .269) and matches the f34's top profile within 0.08 at 18 of 21 points (mirrored it is
  worse); a real rear-three-quarter would put the medium (−X) at screen right.
- **Resolution.** Compare the f34 cell with an extra **`f34_sheet (0, 14)`** and the r34 cell with the **same render,
  unflipped**: shares ±5, profile ±0.08, the caps' f ±0.06. The kit front34 (−28, 12) and rear34 (152, 12) are
  self-consistency only (the rear34 is the check on the back rocks R2/R3).

### 3.2 Side: one small mushroom drawn, two in the plan

- **Evidence.** The front, f34, rear and r34 show both small mushrooms in front of the big one; the side (from +X,
  screen right = back: the big cap's back edge is the silhouette's right edge) shows one small cap at the front (f
  .04–.42, h .27–.525: Ø 1.33, the small's size; its crown at z 1.89 sits between the small's 1.69 and the medium's
  2.25). From +X the medium (front-left, crown z 2.2) stands
  behind the small one, and its crown would rise above the small cap at about f .15–.35, h .50–.61, where the sheet
  draws background.
- **Resolution.** The hero governs (four views against one): keep the medium where the front views put it. Our side
  render will show the medium's crown behind the small cap; record it, don't chase it. Judge the side by D : H, the big
  cap, the small cap's place and forward tilt, the rocks, and shares ±5.

### 3.3 Top: rotated, mirrored and drawn with larger small caps

- **Evidence.** The top cell's caps: big at the upper left, the mid-size one at the right, the small one at the bottom
  — both small caps on one side of the big, 57° apart. The front views need them at the front-left and front-right,
  about 100° apart round the big axis. No rotation of our plan puts the medium at the right and the small at the
  bottom without a mirror; a 45° turn explains the round outline (a 4.4 × 3.5 oval at 45° spans about 4.0 × 4.0 —
  the cell's outline radius is 0.47–0.56 W at every angle). The top also draws the small caps larger (0.71 and 0.61
  of the big cap against 0.51 and 0.42 in the front).
- **Resolution.** Read the kit top with image top = back. Judge it by counts and shares only: three faceted caps (9–10
  sides each, the big one 0.6–0.7 of the top's W), rocks showing round the rim, especially at the back (R2, R3) and
  the left (P2, P3); cap share 60–75 % (sheet 63.5; ours will run higher, because the front views fix the caps' size
  against a tighter rock footprint), rock 25–40 %. Record "top drawn rotated and mirrored" as a known miss.

### 3.4 Front against rear: the big mushroom's X

- **Evidence.** The front and f34 put the big cap's centre at f .58 (X +0.36); the rear draws it centred (f .51, X
  −0.05) with equal small mushrooms on both sides.
- **Resolution.** X +0.22 (the front's caps then land within 0.03 of the sheet's f, the rear's within 0.06). The front
  governs the small mushrooms' sizes (medium 0.51, small 0.42 of the big cap).

### 3.5 The underside band against an elevated camera

- **Evidence.** Every elevation cell shows a tan band 0.1–0.15 H tall below each cap's lip, curving like an underside
  seen from below. The sheet's renders use a perspective camera at about the caps' height; the kit sheet cameras are
  9–14° above the horizontal, from which a flat underside annulus can't be seen.
- **Resolution.** Build the underside as the exploded draws it: a **thick 12-sided drum** (the "Cap Underside" disc,
  Ø 0.65–0.68 of the cap) whose side band hangs 0.30–0.40 below the lip, plus the down-facing gill annulus from the
  drum to the lip (seen in the underside render and the Cap Underside close-up). Check on front_sheet: tan pixels
  under the big cap at h .47–.60, band width 0.40–0.50 W, band colour per §5.7. If the band reads thinner than 0.07 H,
  lower the drum's bottom by 0.08 (and shorten the stalk), never by flaring the lip.

### 3.6 Exploded against hero

- The exploded draws the mid-size mushroom at the right and the small one assembled at the left (mirror of the front),
  and every part about 1.4× larger relative to the base. Its stalk is a squat bell (W : H 0.92) whose widest part is
  hidden in the hero. **The hero governs** positions and sizes; the exploded gives the part list, the cap's dome, the
  disc and the bell.

### 3.7 "Cap (Underside)" swatch against the rendered underside

- **Evidence.** The swatch is a brown `#946244` (22°, 0.54, 0.58). The rendered undersides are tan: `#9B7654`–`#A37E5A`
  (29–30°, 0.44–0.46, 0.61–0.64) under the caps in the front, side and f34; `#A17E5B` inside the exploded cap; the Cap
  Underside close-up's gill ring `#A88563`–`#B4906C`. The exploded disc on its own reads lighter (median `#BDA589`, lit
  `#F9E1C7`, close to the stalk) because its top and side are lit.
- **Resolution.** A separate darker underside key `m031_gill` (§5.4), calibrated to the rendered band (hue 29–30°, sat
  0.42–0.47), not to the swatch's redder brown; the stalk keeps the cream key. The underside is a different part and
  material on the sheet, so this is paint by part, not by facing.

### 3.8 The dark lip band

- The bottom 15 % of every cap is dark brown (`#71391D`–`#7E4225`, lit quartile only `#7E4123`–`#884A2D`), in every
  view including the r34 where the rest of the rim third is lit (`#D47B53`). Mostly geometry: the lip ring faces down
  and out. Build the lip band as a real inward-sloping ring (lip r 0.90 R, 0.29 below the widest ring) and add a gentle
  painted `m031_cap_rim` at 50 % on the lip faces only (§5.4).

### 3.9 Effects

- The sheet says "No additional details, variants, or effects" and shows none: no glow (glow share 0 %), no spores,
  no dust. WorldModeling §9: cave mushrooms get their visibility "from shape and placed lighting, not automatic
  emission". Stages 5 and 6 add nothing by default (§7).

## 4. Construction plan (modeller, stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `cap()` → `CaveFungusCap`: the big cap (R 1.5, H 1.6, n 10) closed by its gill annulus. Compare with the exploded
     cap (`z_expl_top.png`) from about (−10, 15) and from below (the Cap Underside close-up): dome width profile §1.2
     ±0.06, 4 rows of broad facets, a crown polygon, the dark lip ring, radial gill facets.
   - `underside()` → `CaveFungusUnderside`: the big drum (Ø 2.0 × 0.40, 12 sides, bevelled). Compare with the exploded
     disc: Ø : t about 5 : 1, bevelled edges.
   - `stalk()` → `CaveFungusStalk`: the big stalk (r_max 0.75, L 1.45) with a short 8-sided peg on top (Ø 0.18 × its top
     Ø, 0.15 tall). Compare with the exploded stalk: W : H 0.85–1.0 without the peg, widest at 0.25–0.35 of its height,
     top / max 0.60–0.70, 10 sides of kites.
   - `rock_base()` → `CaveFungusRockBase`: the 11 rocks (§2.3), united, floor-cut. Compare with `z_expl_base.png`: a
     wide low central dome with a few big facets, a big back-right rock, small rocks round it; a flat bottom.
   - Render a parts shot (`extra`, about (−20, 15)) laid out like the exploded.
2. **Hero:** `_paste` (m011 pattern) the rock base, the 3 stalks, the 3 drums and the 3 caps (§2.1); unite into one
   closed shell **one piece at a time**, saving the work file between risky steps (rocks first with `union_loose` then
   one exact union; then each mushroom bottom-up: stalk, drum, cap); `m004.floor_cut` at z 0. Origin at the bbox
   bottom centre; transforms applied. Decision §8.6.
3. **Budget** (§4.3): hero about 1300–1800 (limit 4000); parts ≤ 1000 each.
4. **Placeholder keys** (stage 1): `m031_cap`, `m031_gill`, `m031_stalk`, `m031_rock`. Stage 4 adds the rest (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** three chunky faceted rust domes on fat cream stalks in a lumpy grey rock ring; the big cap a
      dome with a dark lip and a tan band under it; the small two leaning outward; nothing round-smooth, nothing flat.
   2. **front_sheet (0, 9)** and **f34_sheet (0, 14)** against their cells: §2.2 and §2.4.
   3. **Cap shape** (parts shot and front): visible cap W : H 1.70–1.85 (big), width per cap height per §1.2 ±0.06 at
      0.4 / 0.6 / 0.8 / 0.9; **9–10 sectors and 4 facet rows**; on the front render the big cap shows 10–18 distinct
      faces, none smaller than about 0.25 stud across in its upper half; a crown polygon of 5–6 sides. **Not an
      icosphere, no soccer-ball pentagon/hexagon pattern** (023's round-1 failure); vertex valence on the dome 4–6.
   4. **Underside band:** visible under all three caps in the front, side, rear and f34 renders (§3.5); big band 0.40–
      0.50 W wide at h .47–.60.
   5. **Stalk shape:** the big stalk's visible width 0.29–0.34 W at h .30 and 0.21–0.27 W at h .45 (front); medium and
      small stalks 0.17–0.21 W and 0.14–0.18 W; parts shot per step 1.
   6. **Lean:** rim slopes per §2.1 ±4°.
   7. **rear_sheet (180, 9)**, **side_sheet (90, 9)**, the r34 check, the top: §2.4 and §3.
   8. **Rock band:** h .0–.2 at least 85 % rock in the front, side and rear; rock share 30–34 % in the elevation views;
      at least 7 rocks visible in the front, each with 6 or more broad facets.
   9. **Kit views** (front34, rear34, underside): self-consistency; the underside shows the flat floor cut, the drums
      and the gill annuli. **Hero size** 4.4 × 3.5 × 3.6 (±0.25 / ±0.3 / ±0.2).
6. **Stage 2:**
   - zero non-manifold, boundary, wire and loose elements; no zero-area faces or n-gons; normals outward; 0 bowtie
     vertices (`M.audit` `nonmanifold_verts`; the cap apex fans and the drum bottom fans are the risk);
   - no faces under 5° where stalks meet drums and rocks, and drums meet caps (m011 `_tidy` / `_desliver`);
   - don't decimate the caps below their 4 rows and 8 sectors, the stalks below 8 sides, the drums below 10 sides or
     the rocks below 5 sides.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Caps (dome + lip + gill annulus) | 3 | 110 / 85 / 75 | 270 |
| Underside drums (12 / 10 / 10 sides) | 3 | 90 / 76 / 76 | 240 |
| Stalks (10 sides, 6 rings) | 3 | 100 / 70 / 60 | 230 |
| Central rock | 1 | 80 | 80 |
| Back rocks | 2 | 50 | 100 |
| Seat rocks and pebbles | 8 | 30–40 | 280 |
| **Sum before union** | | | **about 1200** |
| **Hero after union** (seams, slivers, floor cut) | | | **about 1400–1900** (limit 4000) |
| Parts: Cap / Underside / Stalk / RockBase | | | about 125 / 90 / 110 / 550 (limit 1000) |

## 5. Colour plan (modeller, stage 4)

### 5.1 Swatches (flat; medians of a 30 × 16 box inside each)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Cap (Top) | (42,1362,72,1378) | `#BB623C` | 18°, 0.68, 0.73 |
| Cap (Underside) | (42,1394,72,1410) | `#946244` | 22°, 0.54, 0.58 |
| Stalk | (42,1426,72,1443) | `#E5C9AA` | 32°, 0.26, 0.90 |
| Rock (Main) | (42,1459,72,1475) | `#9B9191` | 0°, 0.06, 0.61 |
| Rock (Small) | (42,1491,72,1507) | `#7B726F` | 15°, 0.10, 0.48 |

- **Cap (Top)** matches the rendered cap medians (`#B5603D`–`#BC6844`) closely.
- **Cap (Underside)** is redder and darker than every rendered underside (§3.7).
- **Stalk** is a little darker and more saturated than the unshadowed rendered stalk (`#EBD2B9`–`#ECD7C2`).
- **Rock (Main)** is a neutral pink-grey; the rendered rocks are a touch warmer (hue 8–22°, sat 0.09–0.14). **Rock
  (Small)** matches the small rocks' medians (`#827A7A`–`#8D7F79`) and the top view's rocks (`#7B7270`).

### 5.2 Rendered regions (`samp.py`, `grad.py`; median / lit quartile / shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Caps, f34 / r34 / front / side / rear / top | V | C | `#B9633F` / `#B6623F` / `#B8633F` / `#BC6441` / `#B5603E` / `#B5603D` | `#DC7F57` / `#D87D55` / `#DB7D55` / `#D47850` / `#D57952` / `#D3764D` | `#7A3E21` / `#7E4225` / `#783E21` / `#783E23` / `#763D21` / `#8D4C2E` |
| Big cap crown third, front / f34 / rear | caps.py | C | `#DA7B53` / `#D97B54` / `#D37650` | `#E2855C` / `#E3845D` / `#E4855D` | `#BA6545` / `#B7664B` / `#C5714B` |
| Big cap middle third, front / f34 | caps.py | C | `#B86441` / `#BC6845` | `#DA7E55` / `#DC8058` | `#894A2D` / `#A25D3B` |
| Big cap lip band (bottom 15 %), front / f34 / r34 / rear | caps.py | C | `#71391D` / `#74391D` / `#7E4225` / `#753D21` | `#7E4123` / `#7E3F22` / `#884A2D` / `#82472A` | `#5E2D14` / `#632F16` / `#69341A` / `#6A351B` |
| Medium / small cap, front | caps.py | C | `#B45F3A` / `#C0643B` | `#CD714B` / `#DC7F54` | `#743B20` / `#67331A` |
| Exploded big / mid / small cap | (186,726,448,867) / (431,872,582,964) / (93,1067,232,1160) | C | `#B56240` / `#C06740` / `#B66240` | `#D67C55` / `#D2764F` / `#CD724B` | `#7E4327` / `#783E23` / `#86492C` |
| Underside band, front / side / f34 | (103,564,127,580)+(192,564,220,580) / (358,557,381,571)+(439,557,466,571) / (192,216,235,247)+(352,216,407,247) | K | `#9B7654` / `#A37E5A` / `#987554` | `#A6805A` / `#A98460` / `#A9815C` | `#916E4E` / `#977554` / `#906E4E` |
| Underside inside the exploded cap / mid cap | (214,837,419,873) / (431,872,582,964) | K | `#A17E5B` / `#A37E5A` | `#A88562` / `#A98561` | `#967352` / `#997653` |
| Cap Underside close-up (gill ring + stalk) | (623,730,1004,909) | K | `#B08C69` | `#EFD4BA` | `#A88460` |
| Exploded underside disc | (233,884,393,936) | K | `#BDA589` | `#F9E1C7` | `#AD8966` |
| Big stalk, front / f34 / rear | (136,589,181,618) / (231,264,321,322) / (623,583,673,618) | K | `#ECD7C2` / `#E9D5C1` / `#E4CFB9` | `#FDE9D2` / `#FDE9D3` / `#FBE6CE` | `#DDC7AF` / `#CBB59E` / `#C3AA93` |
| Medium / small stalk, front | (68,616,110,647) / (202,630,234,655) | K | `#E8D4BE` / `#D0B89D` | `#FAE3CA` / `#F6DEC3` | `#BCA895` / `#9A8068` |
| Exploded big / mid / small stalk | (240,960,381,1100) / (460,1022,544,1121) / (128,1141,223,1226) | K | `#EBD2B9` / `#E9CFB3` / `#DDC5AC` | `#FDE8CF` / `#FDE7CD` / `#F9E2C9` | `#C1AB95` / `#BBA18A` / `#A8927B` |
| Rocks, f34 / r34 / front / side / rear / top | V | R | `#9B8C85` / `#8D807E` / `#A0928A` / `#9C8D86` / `#8D817C` / `#7B7270` | `#B0A19C` / `#B2A39C` / `#B3A49F` / `#B3A49F` / `#B1A29C` / `#BAAFAB` | `#645D5A` / `#5F5652` / `#6B6461` / `#68605D` / `#605755` / `#4E4745` |
| Central rock, front / f34 | (103,630,192,676) / (180,339,360,428) | R | `#A79994` / `#A1938E` | `#B3A49F` / `#AF9F9B` | `#7A7373` / `#756E6D` |
| Central rock lit area, exploded | (300,1200,420,1290) | R | `#A19592` | `#AE9E9B` | `#9D8D87` |
| Small rocks, front left / right | (29,641,96,680) / (202,647,263,680) | R | `#827A7A` / `#8D7F79` | `#ADA09D` / `#B4A59E` | `#67605E` / `#6D6059` |
| Back rocks between the stalks, front | (107,607,122,628)+(188,610,197,628) | R | `#575253` | `#7C7779` | `#413C3D` |
| Exploded rock base / junction rock / base underside | (95,1134,588,1303) / (623,1040,870,1121) / (623,1150,880,1320) | R | `#9C8E88` / `#A69997` / `#7C726C` | `#AFA19D` / `#B3A5A0` / `#9A8F8D` | `#6E6664` / `#8A8282` / `#706865` |

**Gradients along a part** (medians in five equal steps, bottom → top; `grad.py`):

```
big stalk     exploded #DFC3A5 #EBD5BD #F0DBC4 #EFD9C2 #E9D0B6   front #D1BDAA #E9D6C2 #ECD9C4 #ECD6C1 #D9C1AB
mid stalk     exploded #B99F81 #E3CBB1 #F1DBC4 #EFD9C2 #EAD2B8
big cap       exploded #7A4126 #94533A #B56241 #D2764F #D47A55   front #C26439 #7F4224 #B46240 #D6784F #DB7C56
              lit q.   #84492D #CF7246 #D67C54 #DA7C54 #E88860
central rock  exploded #93837A #9F908A #A19592 #A89B96 #A09391   front #93857D #A79891 #AC9F9B #ADA19D #988476
```

Deciles (dark → light), front: central rock `#756E71 #7A7474 #92837B #A4958D #A69893 #A99B94 #AB9F9C #ADA19F #AEA3A1
#B5A9A7`; big stalk `#D0BAA5 #E0CBB6 #E7D4BF #E9D5C2 #EAD7C2 #ECD8C3 #EFDDCA #FCE6CE #FDE8D0 #FEEBD5`; underside band
`#906D4D #926F4F #96714D #957355 #987556 #9F7753 #9D7B5A #A57C55 #A67F59 #AB825A`; exploded big cap `#763F24 #7E452A
#95533B #AE5F3C #B4613F #C4673F #D0754E #D47851 #D67B55 #DA835B`.

### 5.3 How the colour works

**Caps.**
- One saturated rust-orange: hue 17–19°, sat 0.64–0.70 in every view and part. The unshadowed medians agree within 8
  levels (`#B5603D`–`#BC6844`; swatch `#BB623C`).
- The big spread (`#5E2D14` → `#E88860`) is light: up-facing crown facets lit (`#D97B54` crown third), the shoulders
  mid, the lip in shade. The r34's rim third reaches `#D47B53` in its lit quartile, so the rim third is not painted
  dark — **only the lip band** (bottom 15 %) stays dark in every view (§3.8).
- All three caps share one key; the small cap's slightly brighter median (`#C0643B`) is its tilt toward the light.
- No spots, no stripes, no texture noise.

**Underside.**
- One tan, hue 29–30°, sat 0.42–0.47, darker than the stalk by about 70 levels in the views (`#9B7654`–`#A37E5A`)
  and about 60 in the close-up (`#B08C69`). It is the same family as the stalk (same hue) but a separate, darker key
  (§3.7). The gill ring in the close-up is near-uniform (deciles `#A17F5F`–`#B4906C`).

**Stalks.**
- One warm cream, hue 30–31°, sat 0.17–0.21; unshadowed median `#EBD2B9`–`#ECD7C2`, lit `#FDE9D2`. Slightly darker at
  the foot (exploded bottom fifths `#DFC3A5`, mid stalk `#B99F81` — partly contact shade) and just under the cap
  (`#D9C1AB`, the cap's shadow: light, not paint).
- Painted signal: a gentle foot band only (the lowest 20 % of each stalk at 30 % toward `stalk_low`).

**Rocks.**
- Warm pink-grey, hue 8–22°, sat 0.08–0.14. Two painted families: the **big rocks** (central and back, `#A19592`–
  `#A79994` unshadowed) and the **small rocks** (`#827A7A`–`#8D7F79`, about 30 levels darker; swatch Rock (Small)
  `#7B726F`). The back rocks' `#575253` is shade.
- A darker ground band on the big rocks (bottom fifth `#93837A`–`#93857D` against `#A89B96` above): light plus a gentle
  painted band (lowest 20 % of each big rock at 35 % toward `rock_small`).
- No moss, no lichen, no orange spill.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered medians of **unshadowed** regions (the exploded parts, the top view, the crown
thirds), not swatches. `K.sample` kinds: `"vivid"` for the cap keys (sat 0.66 passes); `"brown"` for the gill key;
`"stone"` for the stalk (sat 0.19 < 0.25) and the rocks (check that the stone filter keeps the warm hue; if not, use
`M.sample(..., "stone")` as M015 did).

| Key | Calibration target | Saturation target | Where | Finish |
| --- | --- | --- | --- | --- |
| `m031_cap` | `#B9633F` (view medians `#B5603D`–`#BC6844`; exploded big cap `#B56240`; top view `#B5603D`; swatch `#BB623C`) | 0.64–0.70, hue 17–19° | every cap's dome | rough 0.75, specular low-normal |
| `m031_cap_rim` | `#8C4A2C` (lip band lit quartile `#7E4123`–`#884A2D`; toward the Cap (Underside) swatch `#946244`) | 0.65–0.72 | the lip ring faces only, at 50 % with `cap` | rough 0.75 |
| `m031_gill` | `#A8845F` (front / side / f34 underside band `#9B7654` / `#A37E5A` / `#987554`; exploded cap inside `#A17E5B`; close-up gill ring `#B08C69`) | 0.42–0.47, hue 29–31° | the drums and the gill annuli | rough 0.85 |
| `m031_stalk` | `#EBD3BA` (exploded big stalk `#EBD2B9`; front stalk `#ECD7C2`; swatch `#E5C9AA`) | 0.17–0.21, hue 30° | every stalk | rough 0.85 |
| `m031_stalk_low` | `#D8BDA0` (exploded bottom fifth `#DFC3A5`; mid stalk foot `#B99F81` as the dark end) | 0.25 | the lowest 20 % of each stalk at 30 % | rough 0.85 |
| `m031_rock` | `#A49693` (central rock front `#A79994`, f34 `#A1938E`, exploded lit area `#A19592`; swatch Rock (Main) `#9B9191`) | 0.08–0.12, hue 10–20° | R1, R2, R3 | rough 0.92 |
| `m031_rock_small` | `#867B78` (small rocks `#827A7A` / `#8D7F79`; swatch Rock (Small) `#7B726F`; top rocks `#7B7270`) | 0.08–0.12, hue 10–20° | R4, R5, P1–P6; the big rocks' ground band at 35 % | rough 0.92 |

**Calibration warnings:**
- **Cap:** calibrate on the parts-shot cap against `#B56240` (exploded median), then check the front_sheet cap median
  within 10 of `#B8633F`, its crown third within 12 of `#DA7B53` and its lip band no lighter than `#8A4A2C`; sat ≥ 0.64
  on the median. If the lit faces wash to salmon, lower the specular, not the colour.
- **Gill:** calibrate on the front_sheet underside band (the drum's side) against `#9B7654`–`#A37E5A` (±12), then check
  the underside render reads `#A08060`–`#B4906C` on the gill ring. The studio key lights the drum's side more than the
  sheet's shade does, so the key will land darker than the band target; don't let it drift toward the swatch's hue 22°.
- **Stalk:** calibrate on the parts-shot stalk against `#EBD2B9`; the front_sheet stalk median within 10 of `#ECD7C2`,
  sat 0.15–0.22. A stalk that whitens to `#F5F0E8` (sat < 0.10) reads as plaster, not cream.
- **Rock:** calibrate `rock` on the parts-shot central rock against `#A19592`–`#A79994` and `rock_small` on a pebble
  against `#827A7A`–`#8D7F79`; keep them 25–35 levels apart and both warm (hue 8–22°): a drift to the neutral or bluish
  grey reads wrong beside the sheet.
- The four families stay apart: cap sat ≥ 0.64, gill 0.42–0.47, stalk 0.15–0.22, rock ≤ 0.14.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Caps:** `cap` on the dome; the lip ring (the faces between the lip ring and the widest ring) → 50 % `cap_rim`,
  blending to 0 by the shoulder ring; broad patches (`K.patches` scale about 0.8, 2–4 facets each) of a 10 % lighter
  `cap` mix on the upper half, never single faces. Each cap its own `tint_var` 0.03.
- **Underside:** `gill` on the drum and the annulus, one flat tan (the close-up's gill ring is near-uniform); the edge
  where the stalk meets the drum stays hard (different parts and materials).
- **Stalks:** `stalk`; the lowest 20 % of each stalk by its own height → 30 % `stalk_low`, fading by 0.35; no top band
  (the cap's shadow does it).
- **Rocks:** big rocks `rock`; their lowest 20 % by height → 35 % `rock_small`, fading by 0.35; contact faces within
  0.2 of a neighbour → 25 % `rock_small`; small rocks `rock_small` with broad patches of 30 % `rock` (2–3 facets).
- **Hard edges only** where materials meet: cap | gill (at the lip), gill | stalk, stalk | rock. They are automatic
  (separate keys on separate faces).

### 5.6 Texture (Tint) and finish

- **Tint** (`tint_var` per piece about 0.03–0.04, so each cap, stalk and rock differs slightly):
  - caps: `K.texture` amp 0.03, scale 0.6 (broad);
  - stalks and gill: amp 0.025, scale 0.6;
  - rocks: amp 0.05, scale 0.5;
  - never per-triangle confetti ("no texture noise").
- **Finish:**

| Material | Roughness | Specular | Metal | Notes |
| --- | --- | --- | --- | --- |
| Cap keys | 0.75 | low-normal | 0 | the sheet's caps have soft highlights on lit facets |
| Gill, stalk keys | 0.85 | normal | 0 | matte |
| Rock keys | 0.92 | normal | 0 | matte stone |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Cap:** front_sheet median within 10 of `#B8633F`, sat 0.64–0.70; crown third within 12 of `#DA7B53`; lip band
  median `#6E3A1E`–`#8A4A2C`; parts-shot cap within 10 of `#B56240`.
- **Underside:** front_sheet band (pixels under the big cap outside the stalk) within 12 of `#9B7654`, sat 0.40–0.48;
  visible on all three caps.
- **Stalk:** front_sheet big stalk within 10 of `#ECD7C2`; parts-shot within 10 of `#EBD2B9`; foot darker than middle.
- **Rock:** front_sheet central rock within 10 of `#A79994`; small rocks within 10 of `#827A7A`–`#8D7F79`; the two
  families 25–35 apart.
- **Shares** per §2.4 and §4 step 5. **Glow share 0** (no pixel above the lit cap and stalk values).

## 6. Joins and contact

- **Big stalk into the central rock:** the stalk's lower 0.6–0.7 sinks into R1 (whose crown is at z 1.0), so the rock
  rim hides the foot from every elevation view, as drawn (the stalk leaves the rock line at h .25–.30).
- **Small stalks into their seat rocks:** feet 0.2–0.3 into R4 and R5; the front pebbles (P1, P4) stand in front of the
  feet so the stalks show from h .12–.15 up.
- **Stalk into drum, drum into cap:** overlaps of 0.04–0.08; the stalk top Ø (1.0 big) is smaller than the drum's
  bottom ring (Ø 1.76), so a tan ring of the drum's bottom shows round the stalk from below.
- **Rocks:** overlap neighbours 0.1–0.3, flat bottoms at z 0; floor-cut at z 0 (`m004.floor_cut`) gives one flat
  underside ("Flat, simplified underside").
- No coplanar faces: jitter rock bottoms by 0.02–0.05 above z 0 before the cut, never sit a drum ring exactly on a cap
  ring. Exact booleans: add pieces one at a time; save between (STAGES crash note).

## 7. Lighting and VFX plan (modeller, stages 5 and 6)

**What the sheet shows:** ordinary sunlit mushrooms on rocks. No glow (glow share 0 % in every view), no light, no
spores, no dust, no particles; the notes say "No additional details, variants, or effects". WorldModeling §9: cave
mushrooms' "visibility should come from shape and placed lighting, not automatic emission".

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight:** nothing on the sheet glows; Neon would flatten the faceted caps.
- **Studio note (Requires Manual Validation):** the node spawns in Emberhollow Caves as well as forests. Check in
  Studio that the caps still read as rust-orange (not brown-black) under the cave zone's lighting; if they don't, the
  fix is the zone's placed lights, per WorldModeling, not emission on the model.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **Recommended: none** (decision §8.7). The sheet rules effects out, and M023 and M025 (like the numbered
  models before them) decided against harvest sockets. Record "Stage 6 skipped: the sheet shows no VFX and says none".
- **Options** if the main session wants them:
  - the R07 pair: `harvest_hit` at the big cap's front edge, about (+0.22, −1.25, 2.4), colours `["#B9633F",
    "#EBD3BA"]` (cap and stalk crumbs), and `harvest_deplete` at about (0, 0, 0.6), colours `["#B9633F", "#A49693"]`;
  - spores: `dust` at about (+0.2, 0, 3.0) with colour `["#F0E2C8", "#E5C9AA"]`, rate about 0.4 — not on the sheet.
- **Not recommended:** any light, `crystal_glow`/`crystal_halo` (nothing glows), `ore_glint`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by `git grep` of the repo and a search of every sheet, kit and wip `.blend`,
zstd-decompressed (`m031_study/blendall.py`):
- **R07 kit** (in `FlintbornWorldKit.blend` (56 hits), `wip/R07_cave_mushroom.blend` and every M015–M029 wip copy):
  `CaveMushroom`, `CaveMushroomMushroomCap`, `CaveMushroomCapUnderside`, `CaveMushroomMushroomStalk`,
  `CaveMushroomRockBase`, `CaveMushroomCapDrop`, `CaveMushroomWhole`, `CaveMushroomDepleted`; keys `r07_cap`,
  `r07_stalk`, `r07_stone` (`art/blender/scripts/kit/R07/cave_mushroom.py`, `art/roblox/kit/R07/manifest.json`).
- **`src`:** the node id `CaveMushroomPatch` and the material `CaveMushroom` — game ids, not kit objects (0 hits in any
  `.blend`).
- `M.mk` would silently rename a clash to `<name>M031`, so avoid all of these.

**Proposed names.** `CaveFungusNode`, `CaveFungusCap`, `CaveFungusUnderside`, `CaveFungusStalk`,
`CaveFungusRockBase` and the `m031_` prefix occur nowhere in the repo or any `.blend` (`CaveFungus` 0 hits, `m031_` 0
hits; `Fungus` occurs only inside V05's longer names).

| Object | Part | Why |
| --- | --- | --- |
| `CaveFungusNode` | hero | `…Node` like `BerryBushNode` / `ThornBushNode` / `FrostBushNode`; a new stem as M024/M027/M028 did, since R07 owns `CaveMushroom*` |
| `CaveFungusCap` | Mushroom Cap (the big one, closed by its gill annulus) | R07 owns `CaveMushroomMushroomCap` |
| `CaveFungusUnderside` | Cap Underside (the big drum) | R07 owns `CaveMushroomCapUnderside` |
| `CaveFungusStalk` | Mushroom Stalk (the big one, with its top peg) | R07 owns `CaveMushroomMushroomStalk` |
| `CaveFungusRockBase` | Rock Base (the 11 rocks, flat bottom, no sockets) | R07 owns `CaveMushroomRockBase` |

- Fallback if the main session prefers the game's id: `CaveMushroomPatch` is free as an exact name (with parts
  `CaveMushroomPatchCap` etc., all 0 hits), but it shares R07's `CaveMushroom` prefix.
- Palette keys `m031_*` (§5.4). Collection `Kit/M031 Cave Mushroom`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **4.4 × 3.5 × 3.6** (recommended: the Farming forage family's height; the node's stats equal
   `ThornShrub` / `FrostShrub`; the big cap at chest height), or 0.8 C (5.4 × 4.3 × 4.4), or R07's 7.7 × 5.9 × 5.4.
2. **Mushroom count and layout:** **three — big at the back-centre (X +0.22), medium front-left, small front-right,
   both leaning outward 16–20°** (recommended: the front, f34, r34 and rear agree), against the top cell's rotated and
   mirrored arrangement (§3.3) and the side's single small mushroom (§3.2).
3. **Underside:** **a 12-sided tan drum (Ø 0.65–0.68 of each cap, hanging 0.3–0.4 below the lip) plus a down-facing
   gill annulus** (recommended: the exploded "Cap Underside" disc; it makes the tan band show from the sheet's
   elevated cameras, §3.5), or a flat underside annulus only (invisible from every elevation view).
4. **Underside colour:** **a separate tan key `m031_gill` calibrated to the rendered band** (`#9B7654`–`#A37E5A`,
   recommended, §3.7), or the swatch's redder brown `#946244`, or the stalk's cream.
5. **Pegs and sockets:** **none in the hero; no holes anywhere; the Stalk part keeps its short top peg; the RockBase
   part has a flat bottom without recesses** (recommended: hidden in every assembled view; holes need booleans; M025
   kept the same rule), or the underside close-up's three recesses on the RockBase part only.
6. **Hero packaging:** **one closed shell** (recommended: STAGES default), rocks first, then each mushroom stalk →
   drum → cap, one piece at a time.
7. **Stage 5/6:** **no emission, light or VFX** (recommended: the sheet says "No … effects"; WorldModeling: cave
   mushrooms get no automatic emission; consistent with M023), or the R07 harvest pair, or faint `dust` spores (§7.2).
8. **Exports:** **the hero plus 4 parts** (`…Cap`, `…Underside`, `…Stalk`, `…RockBase`) (recommended). R07's
   `CapDrop`, `Whole` drops and `Depleted` state are not on this sheet; not built unless asked.
9. **Comparison cameras** (§3): `front_sheet (0, 9)`, `f34_sheet (0, 14)` (for the f34 and, unflipped, the r34),
   `rear_sheet (180, 9)`, `side_sheet (90, 9)`, kit top; kit front34, rear34 and underside as self-consistency; a parts
   shot `(−20, 15)` and an underside shot of a cap (the Cap Underside close-up).
10. **Names** as proposed (`CaveFungus*`, hero `CaveFungusNode`).

## 9. Pitfalls to avoid

1. **Ball or soccer-ball caps.** The caps are domes with a broad rim band, 9–10 sectors and 4 facet rows, a crown
   polygon and a dark lip — not icospheres (R07's subdivided domes were flagged for 40 mid-size facets), not
   `hull_rock` of a Fibonacci sphere (023's first lobes failed as "pinched spheroids with even, soccer-ball facets").
   Measure the visible cap W : H (1.70–1.85 big) and the width per cap height (§1.2).
2. **Flat or mushroom-shelf caps.** The big cap is 1.6 tall on a 3.0 Ø (H/Ø 0.53, visible W : H 1.75); a cap under
   W : H 2.1 in the front is too flat.
3. **No underside band.** From the sheet cameras the tan band must show under every cap (§3.5). A flat annulus alone
   is invisible from above.
4. **Slim stalks.** R07's stalks were flagged slim. The big stalk is 0.31 W at the rock line and 0.24 W under the
   underside; the small stalks 0.54 of their caps.
5. **Upright small mushrooms.** Both lean outward (13–17° rim slopes in the front, 15° forward in the side).
6. **Pillow rocks or a flat base.** The central rock is a faceted low dome (h/w 0.5) with ~20 broad facets; small rocks
   are domes (h/w 0.6–0.9); the rock band is lumpy (top profile .14–.31 across the front). No base slab, no
   pale flat plate (R07's "pale flat base").
7. **Colour by facing.** The dark caps' lips and the light crowns are mostly light; paint the lip band by ring, the
   stalk feet and rock ground bands by height; `K.check` facing correlation < 0.5.
8. **One-grey rocks.** Two rock families (big `#A49693`, small `#867B78`), both warm; not neutral or bluish.
9. **White or grey stalks.** Cream, hue 30°, sat 0.17–0.21.
10. **Comparing the wrong views.** The f34 and r34 are both the front composition from about 14° up; the top is drawn
    rotated and mirrored; the side shows one small mushroom (§3).
11. **Side-view handedness.** The kit side camera at az 90 sits at +X, so screen right is the model's back; the
    sheet's side shows the big cap's back edge at the right and the small mushroom at the front-left of the frame.
12. **Exact booleans.** Overlap everything (§6); add the 20 pieces one at a time; remove slivers with m011's `_tidy` /
    `_desliver`; save between risky steps. Watch the cap apex fans and drum bottom fans for bowtie vertices.
13. **Adding effects.** No Neon, no light, no sockets unless decision 7 says otherwise.
14. **Naming clashes** with R07's `CaveMushroom*` (§8). Don't edit shared helpers (`kit_models.py`, `kit_mcp.py`,
    `build_kit.py`, `lib/vfx.py`); put new helpers in `m031.py`. No commits, pushes or exports in the modeller's
    stages.

## Decisions (main session, 2026-10-28)

All recommendations are accepted:
1. Size: 4.4 W × 3.5 D × 3.6 H.
2. Layout: the big mushroom at the back (X +0.22), the medium at the front-left and the small at the front-right, both leaning outward 16–20°. The top and side cells' disagreements are recorded known misses.
3. Underside: a tan drum about 0.65 of each cap's width, hanging 0.3–0.4 below the lip, plus a gill annulus.
4. Underside colour: a separate key `m031_gill`, calibrated to the rendered band, not the swatch.
5. No pegs or sockets in the hero and no holes anywhere. The Stalk part keeps its peg; the RockBase has a flat bottom.
6. One closed shell, built rocks first, then each mushroom stalk → drum → cap, one piece at a time.
7. No emission, light or VFX.
8. Hero plus 4 parts.
9. Comparison cameras:
   - front_sheet (0,9), rear_sheet (180,9) and side_sheet (90,9);
   - f34_sheet (0,14), with the r34 compared unflipped against it;
   - the kit top, judged by counts and shares only.
10. Names: `CaveFungusNode`, `CaveFungusCap`, `CaveFungusUnderside`, `CaveFungusStalk`, `CaveFungusRockBase`, keys `m031_*`.

The caps are faceted domes (10 sectors, 4 facet rows, a crown polygon), never balls or soccer-ball patterns. Meet each cap's W:H and visible h range per view.
