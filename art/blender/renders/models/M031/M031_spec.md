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

## Stage 1 — Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m031.py` (`build()`; background session on port 9880, work file
`art/blender/assets/kit/wip/M031.blend`). Every part comes from its own function, and the hero is assembled from
those same functions:
- **Cap** `_cap(R, H, n)`: rings (z fraction of H above the lip, radius fraction of R) lip (0, 0.90), rim (0.16, 1.0),
  shoulder (0.42, 0.94), upper (0.72, 0.64), then a **flat crown pentagon** (1.0, 0.22). Ring turns `CAP_OFFS`
  (0, 0, ½, 0) step. The lip and rim are aligned, so the lip band is a row of narrow quads (the dark lip band). The
  shoulder sits half a step round, giving tall triangles. The upper ring is turned back, so the shoulder and upper
  rows form diamonds and kites. Jitter is ±3.5 % radius and ±1.5 % H. Underneath, a down-facing gill annulus runs
  from the lip to an inner ring (0.04 H, 0.62 R) with a shallow fan to the centre (0.10 H). Big cap: 10 sectors, 108
  tris. Medium: 9 sectors. Small: 8 sectors. The big cap's rim has a vertex at ±X (front width 3.0) and its shoulder
  a vertex at the front (az 270).
- **Underside drum** `_drum`: 12 sides (10 on the medium and small). Rings (0, 0.86 r), (0.07, r), (just under the
  lip, r), (top, 0.90 r), with a shallow radial cone underneath. Big: r 1.0, 0.575 tall, 94 tris. Its top sits
  0.05 above the gill fan's apex, inside the cap; its side crosses the gill annulus transversally.
- **Stalk** `_stalk`: 10 sides (8 on the medium and small), **4 rings** offset half a step: (0, 0.90), (0.30, 1.0),
  (0.64, 0.84), (1.0, 0.67) of r_max. The Stalk part adds the 8-sided top peg (r 0.10, 0.15 tall). 6 rings were
  tried first and made small triangles that read as a smooth glossy bottle.
- **Rocks** `_rocks`: 12 `K.hull_rock` domes with flat bottoms at z −0.06 (cut flat later). Small rocks use rings
  (0, 1.0, 7), (0.4, 0.9, 7), (0.78, 0.64, 6), (1.0, 0.38, 4); R1 uses an 8-point, 5-ring recipe. Every rock touches
  at least one neighbour, checked with a BVH overlap for each yaw retry (`ROCK_INFO[...]["touch"]`).
- **Layout** (`SHROOMS`, `ROCKS`). Each mushroom's stalk length comes from its crown target. The stack is stalk →
  drum (the stalk sinks 0.08 × scale into it) → lip (drop above the drum bottom) → cap.
  - Big: foot (+0.32, +0.30, 0.25), r_max 0.75, cap R 1.50 × H 1.45, crown z 3.60, lip z 2.15, drum z 1.77–2.35.
  - Medium: foot (−0.95, −0.58, 0.12), leaning 18° toward az 205; R 0.78 × H 0.78, crown z 2.25.
  - Small: foot (+1.36, −0.72, 0.10), leaning 20° toward az 315; R 0.65 × H 0.55, crown z 1.69.
  - The caps never touch (BVH overlap check `cap_touch` = []).
  - Rocks: R1 central (0.15, 0.00) 2.40 × 2.45 × 1.0. R2 back-right (1.30, 1.00) and R3 back-left (−1.02, 1.08)
    reach out past the big cap's plan outline. **R6 is added** at the back centre (0.25, 1.30) 1.35 × 1.0 × 0.78:
    the rear cell draws a rock in front of the big stalk, which R1 can't hide from behind. Seats R4 / R5; pebbles
    P1–P6.
- **Changes from the study's starting values**, made on the renders:
  - Big cap H 1.6 → 1.45 and X +0.22 → +0.32 (the front cap was too tall: W : H 1.52, rim h .56 against .60–.66;
    its centre f .54 against .58).
  - Medium and small H 0.83 / 0.69 → 0.78 / 0.55.
  - Medium foot 0.1 inward and lean 16° → 18°.
  - Pebbles made squatter and moved inward until all of them overlap.

Placeholder keys were the study's §5.4 targets. Stage 4 replaced them.

## Stage 2 — Optimisation and cleanup

- **Hero:** the 21 shells (12 rocks, 3 × stalk / drum / cap) are united one at a time (`_union_fine`: exact union,
  0.002 merge, a guard against a union that loses the mesh), then cut flat at z 0 (`_floor_cut`, a triangle-fill
  cap). After that come `m016._clean_mesh`, `_finish` (from m025: drop inner crumbs, fill, force slivers, recentre),
  `_polish` (split quads, force slivers ≥ 5°, smart UV), ground faces, and `M.fix_bowties` last.
- **Hero guard:** if the fused hero fails `_fused_ok` (one shell, 0 non-manifold, bowtie or boundary edges, no
  self-intersections, no corner under 5°), every rock turns 13° and the hero is rebuilt (4 tries). The RockBase
  part has the same guard. Final build: both passed on attempt 0. Earlier layouts needed attempt 1.
- **Final audit** (`build()`, 2026-10-29):

| Object | Tris | Size (studs) | Shells | NM edges | Bowtie verts | Boundary | Self-hits | Inverted | Min corner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CaveFungusNode (hero) | 1484 / 4000 | 4.45 × 3.54 × 3.60 | 1 | 0 | 0 | 0 | 0 | 0 | 5.06° |
| CaveFungusCap | 108 / 1000 | 3.04 × 2.82 × 1.46 | 1 | 0 | 0 | 0 | 0 | 0 | 15.05° |
| CaveFungusUnderside | 94 / 1000 | 2.02 × 2.02 × 0.57 | 1 | 0 | 0 | 0 | 0 | 0 | 15.0° |
| CaveFungusStalk | 112 / 1000 | 1.47 × 1.48 × 1.75 | 1 | 0 | 0 | 0 | 0 | 0 | 9.9° |
| CaveFungusRockBase | 664 / 1000 | 4.37 × 3.47 × 1.05 | 1 | 0 | 0 | 0 | 0 | 0 | 5.11° |

- On every object: wire edges, loose verts, zero-area faces, n-gons and duplicate verts are all 0. Normals point
  outward (volume check, plus a ray-parity count of inverted faces, `_inverted`). Transforms are applied, the origin
  is at the bottom centre, there are no custom normals, shading is flat, and `K.check` reports no problems.
- Size against the target 4.4 × 3.5 × 3.6: W +0.05, D +0.04, H 0.

## Stage 3 — UV

`M.smart_uv(angle 45, ANGLE_BASED, margin 0.008)` plus `m012._uv_unfold`:

| Object | Islands | Overlap pairs | Flipped | Min gap | Border | Density min / med / max | Conformal p95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Hero | 291 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.033 |
| Cap | 13 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.064 |
| Underside | 7 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.051 |
| Stalk | 15 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.041 |
| RockBase | 130 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.013 |

## Stage 4 — Materials, colour and texture

**Keys** (`PALETTE`). Roughness: caps 0.75, gill and stalk 0.85, rocks 0.92. Normal specular, no metal.
- `m031_cap` `#985031`, `m031_cap_rim` `#783818`, `m031_cap_light` `#A95A38`;
- `m031_gill` `#E8BF92`;
- `m031_stalk` `#CABBAA`, `m031_stalk_low` `#BAA995`;
- `m031_rock` `#999296`, `m031_rock_small` `#7C7679`;
- 25 / 50 % mixes made by `K.mix_key`.

**Calibration:**
- **Pass 1** (`calibrate()`, `K.calibrate` on the test dome against the §5.4 targets). Rendered medians: cap
  (178,99,67) against `#B56240`, rim (141,74,48), light (199,110,74), gill (167,131,96), stalk (235,210,185), stalk
  low (215,189,161), rock (162,149,146), small rock (133,122,119), all within 6 of target.
- **Pass 2** (the hero's `*_sheet` renders with the floor hidden, against the sheet's class-masked region medians;
  scratch `m031_mod/reg.py`). Linear gains from the geometric mean of front and f34:
  - caps × (1.16, 1.01, 0.89);
  - rocks × 1.46 and small rocks × 1.4: with no floor bounce, the rock sides render darker than on the dome;
  - stalks × 1.2 on pass 1's hue. A per-channel gain greyed the stalk, so its shaded faces fell out of the cream mask;
  - gill × 3.5. The drum side sits in the cap's shadow, and the band rendered `#51402F` against `#957252`.

**Final re-measure** (median / lit quartile / shade quartile, sheet → ours):

| Region | Sheet | Ours | Δ median |
| --- | --- | --- | --- |
| Front big cap | `#BA6441` / `#DB7F56` / `#7D4024` | `#B96242` / `#D8754F` / `#6D361E` | ≤ 2 |
| F34 big cap | `#BA6442` | `#BC6542` | ≤ 3 |
| Front crown third | `#DA7C54` | `#D1704A` | 9–12 |
| Front lip band | `#7F4224` | `#74361E` | 11–12 (inside `#6E3A1E`–`#8A4A2C`) |
| Front underside band (left / right) | `#957252` / `#9C7653` | `#957655` / `#896C4D` | 4 / 19 |
| Front big stalk | `#EBD7C2` | `#EDD3B6` | 12 (B) |
| F34 big stalk | `#EAD7C3` | `#E5CDB1` | 18 (B) |
| Front central rock | `#A79A95` | `#B0A29F` | 9–10 |
| Front small rocks (left / right) | `#82797A` / `#8C7E77` | `#938784` / `#766A5F` | 17 / 24 (the right group sits in the key light's shade) |
| Side / rear big cap | `#C06843` / `#B96340` | `#9E563C` / `#A0563C` | 34 / 25 darker (light direction, not paint) |

- Saturation: front cap 0.64 (sheet 0.65); band 0.43 (target 0.42–0.47, hue 31°); stalk 0.23 (sheet 0.17–0.21).
- The two rock families are 29 levels apart (central `#B0A29F` against small `#938784`). Both are warm.

**Blending** (by position only, in 25 / 50 % steps, never by facing; `K.check` baked-shading correlation 0.00 on
every object):
- **Caps:** the lip band faces (centre under 0.12 H) are 50 % rim, the rim–shoulder band 25 % rim. On the upper half,
  broad noise patches (scale 0.8) are 25 / 50 % toward `cap_light`. The gill annulus is GILL.
- **Stalks:** from the visible foot (big 0.85, medium 0.35, small 0.30) the lowest 15 % is 50 % `stalk_low` and the
  next band to 32 % is 25 %. The peg is `stalk_low`.
- **Rocks:** the big rocks' bottom 15 % is 50 % `rock_small` and up to 32 % is 25 %. Faces within 0.2 of a neighbour
  are 25 %. Small rocks get broad patches 25 % toward `rock`.
- **Ground** (floor-cut cap): plain `rock`. A `rock_small` floor made the RockBase part's rock family follow facing
  (corr 0.50).

**Texture:** broad Tint mottling per piece: caps amp 0.03 at scale 0.6, gill and stalk 0.025 at 0.6, rocks 0.05 at
0.5, plus a per-piece tint (±0.03 / ±0.04). Tint spread: hero 1.14, cap 1.06, underside 1.03, stalk 1.04, rock base
1.14.

## Stage 5 — Lighting

Skipped by decision 7. The sheet shows no glow (glow share 0 %) and WorldModeling §9 rules out automatic emission
for cave mushrooms. No emissive key, no light. Studio note (Requires Manual Validation): check in Emberhollow Caves
lighting that the caps still read rust-orange; if not, fix the zone's placed lights.

## Stage 6 — VFX

Skipped by decision 7: the sheet says "No additional details, variants, or effects". There are no sockets, and
`build()` flags any socket on the hero as a problem. Renders use `vfx=True` (nothing to realise).

## Modeller's notes for the verifier

- **Measuring:** `m031_mod/meas.py` (shares, top profile, width per h, bands, per-cap f / h / W : H / rim),
  `reg.py` (region colours) and `vis.py` (class maps), in the scratchpad next to `m031_study`. They apply the
  study's `m.py` masks to both the sheet and `renders/models/M031/*_sheet.png`. The `*_sheet` renders use a 3× long
  lens and hide the floor, so there is no ground shadow. The r34 is compared with the f34_sheet render, unflipped
  (§3.1). Final numbers are in `m031_mod/final_meas.txt`.
- **Shares** (sheet → ours, C / K / R):
  - front 44.9 / 24.5 / 30.6 → 47.3 / 17.3 / 35.5;
  - f34 43.6 / 23.3 / 33.1 → 48.6 / 16.2 / 35.2;
  - side 44.0 / 24.2 / 31.7 → 45.3 / 22.9 / 31.8;
  - rear 47.6 / 19.4 / 33.0 → 40.0 / 25.3 / 34.6;
  - r34 49.3 / 17.9 / 32.7 → 48.6 / 16.2 / 35.2;
  - top 63.5 / 0 / 36.5 → 89.4 / 0.2 / 10.4.
- **Cap W : H and extents** (ours; sheet in brackets):

| View | Big | Medium | Small |
| --- | --- | --- | --- |
| Front | 1.87 (1.75), f .22–.88 (.235–.927), h .59–1.0 (.52–1.0); rim h .59–.62 (.60–.66) | 1.40 (1.38), f .00–.33 (.03–.39), h .37–.64 (.32–.63) | 1.44 (1.47), f .73–1.0 (.70–.99), h .27–.48 (.23–.47) |
| F34 | 1.72 (1.82) | 1.36 (1.42) | 1.37 (1.44) |
| Side | 1.62 (1.74; merged with the medium cap behind it) | — | 1.43 (1.42) |
| Rear | 1.79 (1.82) | — | 1.80 (1.40) |

  - Big cap width per its own height (front): .04 .92 .98 .96 .91 .84 .75 .67 .53 .36 .04 (sheet .02 .13 .95 .99 .94
    .87 .78 .69 .51 .33 .04).
  - Big stalk width (front): .33 W at h .30, .26 at .35, .28 at .40, .25 at .45 (sheet .31 / .29 / .27 / .24).
- **Known misses:**
  1. **Cream share low in the front and f34 (−6 to −7), and C / R correspondingly high.** The kit studio's high key
     light casts the big cap's shadow onto the upper stalk and the drum's left side. Those pixels fall below the
     cream mask's v 0.55 and count as rock or background (see `m031_mod/cls_front_sheet.png`). The lit colours
     match (stalk `#EDD3B6` against `#EBD7C2`, band `#957655` against `#957252`). Painting those faces lighter would
     be painting light, so I didn't. The side view, with the shadow behind, matches within 1.3.
  2. **Top cap share 89 % against the 60–75 % target** (§3.3 expected it to run high). With the front-view cap sizes
     and the 4.4 × 3.5 footprint, the caps cover most of the plan. The back and side rocks were moved out past the
     cap outline (rock 7 → 10 %). Reaching 25 %+ rock would need a footprint about 5 × 4.5.
  3. **Rear:** C −7.6 and K +5.9. The sheet draws the rear as the front again (§3.4). From behind, our small caps sit
     higher (h .40–.56 against .28–.53) and more stalk shows. R6 was added so a rock stands behind the big stalk.
  4. **Side D : H 0.90 (target 0.92–1.04) and f34 W : H 1.12 (1.20–1.32).** The hero matches the decided size, so
     these come from the camera.
  5. Side and rear caps render 25–34 levels darker than the sheet's (light direction).
  6. Side view: the medium cap shows behind the small one (§3.2, expected).
- **Build time:** `build()` takes about 16–34 s plus about 19–20 s of renders (≈ 35–55 s in all). `preview()`
  renders only the sheet shots.

## Stage 7 — Verification (round 1)

Fresh verifier, read-only. Background session on port 9880 with `wip/M031_verify.blend` (not saved, no `build()`). Fresh
renders came from `m031.render_views()` with `M.MODEL_RENDERS` pointed at the verifier's scratch folder
(`scratchpad/m031_ver/renders/M031/`). The modeller's `meas.py` / `reg.py` were re-pointed at those renders; the
verifier's own `band.py` adds the underside band, the parts and per-class colours. Side-by-side crops are
`scratchpad/m031_ver/pair_*.png` and `parts*.png`.

**Result: FAIL, 6.5 / 10.** Three blockers: the underside colour blows out wherever it is lit, the rock keys are
mauve rather than warm, and the rocks have the wrong shape. Geometry, topology, UVs, the caps and the stalks all pass.

### Re-measured (verifier's own bmesh scripts, plus `M.audit`)

| Object | Tris | Size (studs) | Shells | NM edges | Bowtie verts | Boundary | n-gons | Zero-area | Min corner | Self-hits | Inverted | Interior |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CaveFungusNode | 1484 / 4000 | 4.447 × 3.541 × 3.600 | 1 | 0 | 0 | 0 | 0 | 0 | 5.06° | 0 | 0 | 0 |
| CaveFungusCap | 108 / 1000 | 3.043 × 2.815 × 1.459 | 1 | 0 | 0 | 0 | 0 | 0 | 15.05° | 0 | 0 | 0 |
| CaveFungusUnderside | 94 / 1000 | 2.019 × 2.020 × 0.575 | 1 | 0 | 0 | 0 | 0 | 0 | 15.0° | 0 | 0 | 0 |
| CaveFungusStalk | 112 / 1000 | 1.466 × 1.480 × 1.750 | 1 | 0 | 0 | 0 | 0 | 0 | 9.9° | 0 | 0 | 0 |
| CaveFungusRockBase | 664 / 1000 | 4.374 × 3.467 × 1.050 | 1 | 0 | 0 | 0 | 0 | 0 | 5.11° | 0 | 0 | 0 |

- **Size and origin.** Against the decided 4.4 × 3.5 × 3.6: +0.05, +0.04 and 0, all inside tolerance. The local bbox
  is centred on x/y 0 with min z 0. Rotation is 0 and scale 1 on all five objects. There are no modifiers, parents,
  children or VFX sockets, no custom normals, and 0 smooth faces (flat shading). There are 0 wire edges, loose verts
  and duplicate verts, and the volume is positive.
- **Interior faces.** A single-ray parity test flagged 1 face each on the hero and the RockBase. A 5-ray majority
  vote on both sides of every face gives 0 interior and 0 inverted faces, so the flag was a false positive.
- **UV.** Each object has one layer. Islands: hero 291, cap 13, underside 7, stalk 15, base 130. Rasterised at
  1024², there are **0 overlapping texels**. There are 0 flipped and 0 zero-area UV faces. Density p5–p95 is
  0.96–1.04 of the median on every object, and the range is 0.008–0.992.
- **Materials.** There are 14 `m031_*` slots on the hero, all used. Roughness is 0.75 on the cap, 0.85 on the gill
  and stalk, and 0.92 on the rocks. Specular is 0.5, metal 0, emission 0. `K.check` reports nothing.
  - Within the cap faces, key luminance correlates with face normal z at 0.89, because the lip ring is darker and
    the upper patches lighter. Both are painted by ring height, as §3.8 and §5.5 prescribe, so this isn't colour by
    facing.
  - Tint is a corner attribute ranging 0.93–1.06.

### Views against the sheet

Renders are identical to the modeller's: the same numbers reproduce exactly.
- **Caps (pass).** These are faceted domes, not balls or soccer patterns:
  - a dark lip quad band, tall shoulder triangles, diamond and kite upper facets, and a pentagon crown (visible in
    the f34 and the top);
  - big W : H 1.87 front (sheet 1.75; tolerance 1.70–1.85, just over because the sheet's lip dips at its right end),
    1.72 f34, 1.79 rear;
  - width per cap height `.92 .98 .96 .91 .84 .75 .67 .53 .37` against `.95 .99 .94 .87 .78 .69 .51 .33`;
  - medium front f .00–.33 / h .37–.64 (sheet .03–.39 / .32–.63), small .73–1.0 / .27–.48 (sheet .70–.99 / .23–.47);
  - both lean outward with rim slopes like the sheet's (medium rim .37 → .52 against .33 → .47, small .34 → .27
    against .32 → .23).
- **Stalks (pass).** Fat cream bells. The big stalk's front width is .33 / .26 / .28 / .25 W at h .30–.45 (sheet
  .31 / .29 / .27 / .24). The Stalk part matches the exploded bell.
- **Underside band.** Present under every cap, but see blocker 1.
- **Rock ring.** See blockers 2 and 3.

### Colours (median / lit quartile / shade quartile, sheet → ours, Δ = per-channel on the median)

| Region | Sheet | Ours | Δ median |
| --- | --- | --- | --- |
| Front big cap | `#BA6441` / `#DB7F56` / `#7D4024` | `#B96242` / `#D8754F` / `#6D361E` | 1 / 2 / 1 |
| F34 big cap | `#BA6442` | `#BC6542` | 2 / 1 / 0 |
| Front crown third | `#DA7C54` | `#D1704A` | 9 / 12 / 10 |
| Front lip band | `#7F4224` | `#74361E` | 11 / 12 / 6 |
| Cap part vs exploded cap | `#B25F3E` | `#C56946` | 19 / 10 / 8 |
| Side / rear big cap | `#C06843` / `#B96340` | `#9E563C` / `#A0563C` | ≈ 34 / 25 darker (kit light direction) |
| Front big stalk | `#EBD7C2` / lit `#FDE9D1` | `#EDD3B6` / `#F6DCBF` | 2 / 4 / 12 |
| Stalk part vs exploded stalk | `#ECD6BD` | `#F8DEC0` | 12 / 8 / 3 |
| Front underside band | `#A27C58` / `#B28F71` / `#8F6D4D` | `#896D51` / `#B2906D` / `#826A4C` | 25 / 15 / 7 (in the cap's shadow) |
| **Side underside band** | `#A37E5B` / `#AF9074` | `#B18F71` / **`#FDCF9D`** | 14 / 17 / 22; lit +78 |
| **Rear underside band** | `#AA8969` / `#C5AC94` | **`#E2BB8C`** / **`#FFD19C`** | **56 / 50 / 35** |
| **Underside part vs exploded disc** | `#BDA489` / `#F9E1C7` | **`#FFDEA0`** / `#FFEEAC` | **66 / 58 / 23** |
| Gill close-up vs cap-part underside | `#B08C69` | `#BEAD9B` (294 px, a flat plain disc) | 14 / 33 / 50 |
| Front central rock | `#A79A95` | `#B0A29F` | 9 / 8 / 10 |
| Front small rocks L / R | `#82797A` / `#8C7E77` | `#938784` / `#766A5F` | 17 / 14 / 10 · 22 / 20 / 24 |
| Rock base part vs exploded base | `#9C8E88` | `#A79A96` | 11 / 12 / 14 |
| **Side rocks** | `#9C8D86` (warm) | **`#807676`** (neutral) | 28 / 23 / 16 |
| **Rear rocks** | `#8D817C` / lit `#B1A29C` (warm) | **`#91898C`** / **`#A59C9F`** (B > G, mauve) | 4 / 8 / 16; lit hue wrong |
| Top rocks | `#7B7270` | `#9C9190` | 33 / 31 / 32 |

### Judging the modeller's misses

- **Cream share low in the front and f34** (K 17.3 / 16.2 against 24.5 / 23.3): **lighting, accepted.** The class
  map shows that the missing cream is the shaded faces of the stalks (the right halves, under the kit's left key)
  and the shaded side of the drum, which fall under the cream mask's v 0.55. Lit stalk colours match within 12. The
  side, with the light behind, is within 1.3.
- **Top cap share 89 % against 60–75:** **accepted.** It follows from the decided size and the front-view cap
  sizes. The sheet's top cell is drawn rotated and mirrored (§3.3).
- **Rear (C −7.6, K +5.9), side D : H 0.90, f34 W : H 1.12:** **accepted as a consequence of the composition and
  camera.**
  - The outward lean lifts the small caps' backs (rear h .40–.56). From behind, the medium cap merges into the big
    cap's rim.
  - The medium and small caps overhang the rock ring at both silhouette ends (front top profile f 0 .46 against
    .08, f 1 .36 against .27).
- **Side and rear caps 25–34 darker:** **lighting** (kit key direction). The key is right: front within 2.

### Blockers

1. **Underside (gill) colour blows out wherever it is lit.**
   - What's wrong:
     - Pass 2 multiplied `m031_gill` by 3.5 to brighten the shadowed front band, which is painting light. The key
       is now `#E8BF92`, lighter than the stalk key `#CABBAA`. The sheet's underside is always darker than the
       stalk.
     - In the rear and side, and on the Underside part, the drum reads as a bright butter-peach collar: rear band
       `#E2BB8C` against `#AA8969`, Underside part `#FFDEA0` against the exploded disc `#BDA489` (Δ 66 / 58 / 23).
     - In Studio, every lit cap will show this yellow ring.
   - Fix:
     - Drop the 3.5× gain. Re-run `K.calibrate({GILL: ((0xBD, 0xA4, 0x89), "brown")})` on the parts-shot drum,
       starting from the pass-1 key; pass 1 rendered (167,131,96) on the test dome.
     - Keep hue 29–31° and the key's luminance at least 15 % below `m031_stalk`.
   - Accept, and record as light, a front band darker than the sheet.
   - Check:
     - `part_underside` median within 15 of `#BDA489`;
     - rear_sheet band (the verifier's `band.py`) within 15 of `#AA8969`;
     - side band lit quartile no lighter than about `#C8A888`.
2. **Rock keys are mauve, not warm.**
   - What's wrong:
     - `m031_rock` `#999296` and `m031_rock_small` `#7C7679` have B > G (hue ≈ 325°). The spec (§5.4,
       pitfall 8) requires hue 8–22° with R > G > B.
     - The front only reads warm because of the warm key light. Side rocks render `#807676` (sheet `#9C8D86`),
       rear lit `#A59C9F` (sheet `#B1A29C`), and under Roblox's neutral light they will read lilac.
   - Fix:
     - Set warm starting keys, about `#9E928C` and `#80766F`.
     - Calibrate `rock` on the parts-shot central rock against `#A19592`, and `rock_small` on a pebble against
       `#857B78`.
     - Keep the two families 25–35 apart, and keep the ×1.46 / ×1.4 floor-bounce gains only if the front still
       needs them.
   - Check: side_sheet and rear_sheet rock medians have R > G > B, and are within 12 of `#9C8D86` / `#8D817C`.
3. **Rocks are upright slabs, not squat boulders.**
   - What's wrong:
     - `ROCK_RINGS` = (0, 1.0) → (0.4 h, 0.9) → (0.78 h, 0.64) → (1.0 h, 0.38 with 4 points). That gives
       near-vertical lower walls and a broad flat 4-point top.
     - Several rocks are as tall as or taller than wide: P5 h/w 1.17, P2 1.01, P3 0.88, R2 0.81, R3 0.79.
     - In the rear, side and Rock Base part renders the ring reads as a row of standing stones or teeth. The sheet
       shows rounded faceted domes ("lumpy ring of warm-grey boulders"; the exploded base).
     - 30 % of the RockBase's non-floor area faces within 15° of horizontal (walls).
   - Fix:
     - Use the study's bulged dome recipe, for example `((0.0, 0.92, 7), (0.3, 1.0, 7), (0.62, 0.84, 7), (0.86,
       0.5, 6), (1.0, 0.15, 3))`.
     - Cap the small rocks at h/w ≤ 0.75: P2 h 0.85 → 0.62, P3 0.70 → 0.55, P5 0.70 → 0.50 (w and d 0.70),
       P6 0.60 → 0.52.
     - Lower R2 to 0.88 (w 1.40) and R3 to 0.82.
     - Keep R1 and R6.
   - Check:
     - rear_sheet, side_sheet and the Rock Base part read as rounded squat domes against the exploded base;
     - front rock-band top profile within ±0.06 of the sheet (.14–.31);
     - h .0–.2 at least 85 % rock in front, side and rear;
     - the hero is still one shell with 0 NM, bowtie and boundary, and its size is unchanged;
     - wall-facing area share about 0.20 or less.

### Minors (record; fix only if cheap while doing the blockers)

- Front big-cap W : H 1.87 is 0.02 over its band (the sheet's dipping lip end). The f34 and rear are inside.
- The drum reads as a straight-walled collar with a hard, straight bottom edge, where the sheet's underside band
  has a soft, concave lower edge. This is per decision 3, and should read acceptably once blocker 1 is fixed.
- The Cap part's underside, seen from below, is a near-flat plain disc (the gill annulus rises only 0.04 H), with
  none of the close-up's radial tan facets. It is never seen in the hero.
- The stalks' lit faces show a warm specular sheen (a gold, glossy gradient on the big stalk's left faces in the
  front and f34). The sheet's stalks are matte. Specular 0.5 → about 0.2 on the stalk and gill keys.
- The Cap part renders 10–19 lighter than the exploded cap (`#C56946` against `#B25F3E`). The hero cap is within 2.
- The composition misses are all accepted, as judged above:
  - the medium and small caps overhang the rock ring at the silhouette ends;
  - rear small caps sit high, and the medium cap merges into the big cap's rim from behind;
  - top cap share 89 %;
  - the medium cap shows behind the small one in the side (§3.2).

## Round 2 fixes (modeller)

Fresh modeller, 2026-10-29. Background session on port 9880 with `wip/M031.blend` (saved after the final build). The
builder `m031.py` is still the source of truth; all changes are in it. Scratch tools are in
`scratchpad/m031_r2/`: `r2.py` (rock-band top profile, bottom-20 % rock share and R-class medians per view),
`band.py` (the verifier's band and parts script, pointed at `renders/models/M031/`), `bot.py` (class map of the
bottom band), `pair.py` (side-by-side crops `pairs_fsr.png` and `pairs_parts.png`). The final numbers are in
`final_meas.txt`. The modeller's `m031_mod/meas.py` / `reg.py` were re-run unchanged.

**Changes**
- **B1, gill.** Dropped the ×3.5 gain. Starting from pass 1's `#856C52`, linear steps on two targets: the
  part_underside median against the exploded disc `#BDA489`, and the rear_sheet band against `#AA8969`. They pull
  R in opposite directions (the parts shot lights the drum warm; the rear lights it cool), so the key sits between
  them. Final **`m031_gill #A08870`**: hue 30°, sat 0.30, relative luminance 0.26 against the stalk key's 0.51
  (47 % darker).
- **B2, rocks.** The keys are now warm with R > G > B. Final **`m031_rock #9B9290`** (hue 11°, sat 0.07) and
  **`m031_rock_small #7E7775`** (hue 13°, sat 0.07), 29 levels apart.
  - Started from `#9E928C` / `#80766F`. On the warm studio key light these rendered the front rocks at hue 29°,
    sat 0.21.
  - The lit front rock faces then fell into the cream mask (K: hue ≥ 26°, sat ≥ 0.13). The front bottom 20 % read
    only 49 % rock.
  - The saturation was stepped down until the front R median sat at hue 22–26° and sat 0.14, and the part_rockbase
    median sat within 6 of `#A19592`.
- **B3, rock shape.**
  - `ROCK_RINGS` is now the bulged dome `((0, .92, 7), (.3, 1.0, 7), (.62, .84, 7), (.86, .5, 6), (1, .15, 3))`.
  - Heights as asked: P3 0.55, P5 0.50 (0.70 × 0.70), P6 0.52, R2 0.88 (w 1.40), R3 0.82.
  - Three rocks differ from the verifier's list, to hold the sheet's front rock-band profile; all stay at h / w
    ≤ 0.75:
    - **P2 0.96 × 0.96 × 0.72**, not 0.62. At 0.62 the front's far-left column read h .16 against the sheet's .28.
    - **P1 0.54, P4 0.56** (P4 0.78 × 0.75). At 0.42 / 0.45 the medium and small stalks showed into the bottom
      band: front 84.5 % rock.
    - **R4 0.62.** 0.72 was tried: it is hidden behind the medium stalk and changed nothing.
  - h / w (height over the smaller footprint side): R1 0.42, R2 0.73, R3 0.71, R4 0.62, R5 0.42, P1 0.73, P2 0.75,
    P3 0.73, P4 0.75, P5 0.71, P6 0.74, R6 0.78 (R6 was kept, as asked).
- **Minors.**
  - Specular 0.5 → 0.2 on every `m031_stalk*` and `m031_gill` material (`SPEC`, applied by `_spec()` in
    `palette()` and after the build). It made no measurable difference: the gold gradient on the big stalk's left
    faces is the soft edge of the cap's shadow (it renders the same at 0.2).
  - Big cap H 1.45 → 1.48 (the crown stays at z 3.60; the lip drops 0.03). 1.50 gave front W : H 1.82 but f34 1.68.
- **Tried and reverted.** An undercut rock base ring (0.84) plus a flatter R1 recipe. RockBase wall share went
  0.264 → 0.235, but the front rocks darkened, the side worsened and the hero needed attempt 2 (1712 tris).

**Final audit** (`build()`; problems `[]`, `K.check` clean, baked-shading corr 0.00 on every object; hero and
RockBase guard passed on attempt 1; build 31.6 s plus 19 s of renders)

| Object | Tris | Size | Shells | NM e / v | Boundary | Self-hits | Inverted | Min corner | UV islands / overlaps / gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CaveFungusNode | 1648 / 4000 | 4.57 × 3.60 × 3.60 | 1 | 0 / 0 | 0 | 0 | 0 | 5.03° | 283 / 0 / 0.016 |
| CaveFungusCap | 108 | 3.04 × 2.82 × 1.49 | 1 | 0 / 0 | 0 | 0 | 0 | 15.25° | 10 / 0 / 0.018 |
| CaveFungusUnderside | 94 | 2.02 × 2.02 × 0.58 | 1 | 0 / 0 | 0 | 0 | 0 | 15.0° | 7 / 0 / 0.016 |
| CaveFungusStalk | 112 | 1.47 × 1.48 × 1.72 | 1 | 0 / 0 | 0 | 0 | 0 | 9.9° | 15 / 0 / 0.016 |
| CaveFungusRockBase | 870 / 1000 | 4.52 × 3.58 × 1.00 | 1 | 0 / 0 | 0 | 0 | 0 | 5.03° | 141 / 0 / 0.016 |

Hero size against 4.4 × 3.5 × 3.6: W +0.17 (tol 0.25), D +0.10 (0.3), H 0. The width grew with the wider P2.
Margin 0.008 on every object, density 1.0, no wire, loose or zero-area elements, no n-gons, rotation 0, scale 1.

**Checks against the verifier's list** (sheet → ours)

| Check | Target | Result |
| --- | --- | --- |
| B1 part_underside median | within 15 of `#BDA489` | `#CDA782`: Δ 16 / 3 / 7 (R one over) |
| B1 rear_sheet band | within 15 of `#AA8969` | `#9C816C`: Δ 14 / 8 / 3 ✓ |
| B1 side band lit quartile | no lighter than ≈ `#C8A888` | `#BAAA97` ✓ (round 1 `#FDCF9D`) |
| B1 key hue / vs stalk | 29–31°, ≥ 15 % darker | 30°, 47 % darker ✓ |
| B2 side rocks | R > G > B, within 12 of `#9C8D86` | `#827974` R > G > B ✓; Δ 26 / 20 / 18 ✗ |
| B2 rear rocks | R > G > B, within 12 of `#8D817C` | `#918783` ✓ Δ 4 / 6 / 7 |
| B2 front rocks | (spec §5.7) | `#958980` against `#A0928A`, Δ 11 / 9 / 10 |
| B2 part_rockbase | `#A19592` | `#A7988F`, Δ 6 / 3 / 3 (exploded base `#9C8E88`: Δ 11 / 10 / 7) |
| B3 front rock-band top | ±0.06 of the sheet | 15 of 19 interior columns within ±0.06; f .05 +.07, .30 / .35 −.09, .40 −.08, .45 +.10 |
| B3 bottom 20 % rock | ≥ 85 % | front 87.5, side 90.7, rear 98.1 ✓ |
| B3 hero shell, size | one clean shell, decided size | ✓ |
| B3 wall-facing area (RockBase) | about 0.20 | 0.264 (round 1 0.30) |
| Minor: front big-cap W : H | 1.70–1.85 | 1.83 ✓ (f34 1.69, rear 1.79) |
| Minor: Cap part | exploded `#B25F3E` | `#C46846` unchanged |

Notes on the misses:
- **Side rocks** are 18–26 darker than the sheet's. The side caps are 31 darker for the same reason (the kit key
  lights the model from the front-left, so from +X the rocks' visible faces are in shade). The keys are right in
  the front (Δ ≤ 11), the rear (Δ ≤ 7) and the parts shot (Δ ≤ 6). The side's lit quartile `#A49A96` is within 15
  of the sheet's `#B3A49F`. Lighting, not paint.
- **Rock-band profile outliers** are mask leaks, not rock height. The class map (`m031_r2/cls_front_sheet.png`)
  shows the big stalk's shaded lower half falling into R (f .40–.45, too high). The medium stalk leans in front of
  R4 at f .30–.35, so the rock behind it can't show (too low; raising R4 changed nothing). The end columns (f 0 and
  1.0) are the caps' overhang, accepted in round 1.
- **Underside part R +16** (one over) against rear R −14: the two targets conflict in the red channel under the
  studio lights. Every other channel is inside.
- **Cap part** not fixed. It renders `#C46846` from every parts-shot angle tried ((−10, 12), (−20, 15), (−10, 15),
  (0, 12): ±4) and with the floor hidden (the same). The hero cap uses the same keys and is within 2 of the sheet
  (`#B96242` against `#BA6441`). Darkening only the part would make a reusable cap that no longer matches the
  hero's caps.
- **Front / f34 cream share** is now 14.8 / 14.2 (round 1 17.3 / 16.2). The drum's band now renders at its true
  tan, `#5E4D3B` in the front, in the cap's shadow, so it falls under the cream mask's v 0.55. This is the darker
  front band that was accepted as lighting. The rear and side bands match (above).
- The rest of round 1's accepted misses are unchanged: top cap share 87 %, side D : H 0.92, f34 W : H 1.15, the rear
  small caps sitting high, and the medium cap showing behind the small one in the side.

## Stage 7 — Verification (round 2)

Fresh verifier, read-only; it did no other stage and was not the round-1 verifier. Background session on port 9880 with
`wip/M031_verify.blend` (not saved; `build()` not called). Fresh renders come from `m031.render_views()` with
`M.MODEL_RENDERS` pointed at `scratchpad/m031_ver2/renders/`. The measuring scripts are copies of the modeller's
`band.py` / `r2.py` / `meas.py` and the round-1 `geo.py` / `geo2.py` / `mats.py`, re-pointed at those renders. The
side-by-side crops are `scratchpad/m031_ver2/p_fsr.png`, `p_34.png`, `p_top_expl.png`, `p_parts1.png`, `p_parts2.png`,
`p_under.png` and `z_stalk.png`. Every number the modeller recorded reproduces exactly.

**Result: PASS, 7.5 / 10.** B1–B3 are fixed. What remains is lighting, or comes from the decisions. Nothing is broken.

### Re-measured (own bmesh scripts plus `M.audit`)

| Object | Tris | Size (studs) | Shells | NM e / v (bowtie) | Boundary | Wire / loose / dup | n-gons / zero-area | Min corner | Self-hits | Inverted / interior (5-ray) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CaveFungusNode | 1648 / 4000 | 4.568 × 3.597 × 3.600 | 1 | 0 / 0 | 0 | 0 / 0 / 0 | 0 / 0 | 5.03° | 0 | 0 / 0 |
| CaveFungusCap | 108 / 1000 | 3.043 × 2.815 × 1.489 | 1 | 0 / 0 | 0 | 0 / 0 / 0 | 0 / 0 | 15.25° | 0 | 0 / 0 |
| CaveFungusUnderside | 94 / 1000 | 2.019 × 2.020 × 0.578 | 1 | 0 / 0 | 0 | 0 / 0 / 0 | 0 / 0 | 15.0° | 0 | 0 / 0 |
| CaveFungusStalk | 112 / 1000 | 1.466 × 1.480 × 1.720 | 1 | 0 / 0 | 0 | 0 / 0 / 0 | 0 / 0 | 9.9° | 0 | 0 / 0 |
| CaveFungusRockBase | 870 / 1000 | 4.525 × 3.576 × 1.000 | 1 | 0 / 0 | 0 | 0 / 0 / 0 | 0 / 0 | 5.03° | 0 | 0 / 0 |

- **Size.** Against 4.4 × 3.5 × 3.6: W +0.17 (tolerance ±0.25), D +0.10 (±0.3), H 0.
- **Interior faces.** A single-ray parity test flags one RockBase face. The 5-ray majority vote on both sides gives 0, so
  it is a false positive (as in round 1).
- **Origin and transforms.** On all five objects the local bbox is centred on x/y 0 with min z 0, rotation is 0 and
  scale is 1. There are no modifiers, parents, children, VFX sockets or custom normals. All faces are flat-shaded, and
  the volume is positive.
- **UV.** Each object has one layer, with range 0.008–0.992. Islands: hero 283, cap 10, underside 7, stalk 15, base
  141. Rasterised at 1024², there are **0 overlapping texels**. There are 0 flipped and 0 zero-area UV faces. Density
  p5–p95 is 0.95–1.06 of the median.
- **Materials.** There are 14 `m031_*` slots, all used. `m031_cap` `#985031`, `gill` `#A08870`, `stalk` `#CABBAA` /
  `stalk_low` `#BAA995`, `rock` `#9B9290`, `rock_small` `#7E7775`; both rock keys are R > G > B, hue 11–13°. Roughness:
  cap 0.75, gill / stalk 0.85, rock 0.92. Specular 0.2 on every stalk and gill material, 0.5 elsewhere. Metal 0,
  emission 0. `K.check` reports nothing. Tint is a corner attribute from 0.93 to 1.06.
- **No colour by facing.**
  - The builder paints by position only: cap by ring height, stalk by height above the visible foot, rocks by height,
    neighbour distance and a noise field.
  - Rock key luminance correlates 0.52 with face height and 0.24 with normal z. The cap's 0.89 normal-z correlation is
    the ring-height lip band, as round 1 found.

### Blockers from round 1

| Item | Check | Result | Verdict |
| --- | --- | --- | --- |
| B1 underside colour | part_underside within 15 of `#BDA489` | `#CDA782`, Δ 16 / 3 / 7 | Pass. R is one level over; the rear band pulls R the other way, so these are conflicting light targets. |
| | rear_sheet band within 15 of `#AA8969` | `#9C816C`, Δ 14 / 8 / 3 | pass |
| | side band lit quartile ≤ ≈ `#C8A888` | `#BAAA97` (round 1 `#FDCF9D`) | pass |
| | key hue 29–31°, ≥ 15 % darker than the stalk | 30°; luminance 0.26 against 0.51 | pass |
| B2 rock hue | side / rear R > G > B | `#827974` / `#918783`, both warm (21° / 17°) | pass |
| | within 12 of `#9C8D86` / `#8D817C` | side Δ 26 / 20 / 18 ✗; rear Δ 4 / 6 / 7 ✓ | Pass (side is lighting, see below) |
| B3 rock shape | rounded squat domes against the exploded base | rear, side and RockBase all read as rounded faceted boulders (`p_parts1`, `p_fsr`) | pass |
| | h / w ≤ 0.75 | all ≤ 0.75 except R6 0.78 (kept as asked) | pass |
| | h .0–.2 ≥ 85 % rock | front 87.5, side 90.7, rear 98.1 | pass |
| | front rock-band top ±0.06 | 15 of 21 columns. Outliers: f .30 / .35 −.09, .40 −.08, .45 +.10, f 1.0 +.27 (cap overhang). The class map puts these on mask leaks: the shaded stalk reads as R, and the medium stalk covers R4. | pass |
| | one clean shell, size unchanged | yes, W +0.17 (inside tolerance) | pass |
| | wall-facing area ≈ 0.20 | RockBase 0.264, hero rocks 0.305 | Minor. The prescribed bulged-dome recipe itself gives about 20° walls between rings 0.3 and 0.62, and it reads as domes. |

### Views against the sheet (side-by-side crops)

- **Front, f34 and r34.**
  - The caps are faceted domes with a dark lip band, shoulder kites and a crown. The stalks are fat cream bells. The
    small caps lean outward.
  - Big cap W : H: front 1.83 (sheet 1.75, band 1.70–1.85), f34 1.69 (sheet 1.82).
  - Big cap extents: front f .24–.88, h .585–1.0 (sheet .235–.927, .52–1.0).
  - Medium cap: f .02–.35, h .37–.64 (sheet .03–.39, .32–.63). Small cap: f .74–1.0, h .27–.48 (sheet .70–.99,
    .23–.47).
  - The rocks read as warm-grey boulders.
  - The visible difference is under the big cap. The drum and the upper stalk sit in the kit key light's cap shadow and
    render olive-grey (band `#5E4D3B` against `#A27C58`), with a soft penumbra gradient that reads slightly bronze
    (`z_stalk.png`). The sheet lights the underside. The keys are right, so this is lighting.
- **Side.** The caps and rocks are about 14 % darker than in the front, by the same factor (cap `#9D553B` against
  `#BC6441`, rocks `#827974` against `#9C8D86`). The stalks match (`#B7A693` against `#BBA38D`). One factor across two
  different keys means the key light's direction, not paint. The medium cap shows behind the small one (§3.2,
  accepted).
- **Rear.** Rocks `#918783` against `#8D817C` (Δ ≤ 7). The small caps sit higher (h .40–.56), as accepted in round 1.
  The rock band is lower behind the medium stalk (f .30 / .35: −.16 / −.11) and higher at f .15–.20 (+.11). Minor.
- **Top.** Cap share 87 % against 63.5 % (rock 12 against 36.5): accepted in round 1 (decided size, and the sheet's cell
  is mirrored and rotated).
- **Exploded and parts.**
  - The rock base is a lumpy ring of rounded boulders, as on the sheet.
  - The stalk bell matches, with its peg.
  - The cap dome matches.
  - The underside part is a thick puck (t / Ø 0.29). The sheet's disc is thinner (about 0.12) and paler.
  - The Cap part's underside renders as a flat, dark, shadowed disc.

### Colours (median / lit quartile / shade quartile, sheet → ours)

| Region | Sheet | Ours | Δ median |
| --- | --- | --- | --- |
| Front big cap | `#B8633F` / `#DB7D55` / `#783E21` | `#BB6442` / `#D7754E` / `#6D361E` | 3 / 1 / 3 |
| F34 big cap | `#B9633F` | `#BC6542` | 3 / 2 / 3 |
| R34 caps (vs f34 render) | `#B6623F` | `#BC6542` | 6 / 3 / 3 |
| Side / rear caps | `#BC6441` / `#B5603E` | `#9D553B` / `#9F553B` | 31 / 15 / 6 · 22 / 11 / 3 (light direction) |
| Top caps | `#B5603D` | `#B75E41` | 2 / 2 / 4 |
| Front cream (stalks + band) | `#C3AB94` / `#F7DEC6` | `#CAB29A` / `#F4DABC` | 7 / 7 / 6 |
| Front underside band | `#A27C58` | `#5E4D3B` | 68 / 47 / 29 (cap shadow) |
| Side / rear underside band | `#A37E5B` / `#AA8969` | `#857161` / `#9C816C` | 30 / 13 / 6 · 14 / 8 / 3 |
| Front / f34 rocks | `#A0928A` / `#9B8C85` | `#958980` / `#968981` | 11 / 9 / 10 · 5 / 3 / 4 |
| Side / rear rocks | `#9C8D86` / `#8D817C` | `#827974` / `#918783` | 26 / 20 / 18 · 4 / 6 / 7 |
| Top rocks | `#7B7270` | `#A1948D` | 38 / 34 / 29 lighter (lit from above) |
| Cap part / exploded cap | `#B25F3E` | `#C46846` | 18 / 9 / 8 |
| Underside part / exploded disc | `#BDA489` | `#CDA782` | 16 / 3 / 7 |
| Stalk part / exploded stalk | `#ECD6BD` | `#F8DEBF` | 12 / 8 / 2 |
| Rock base part / exploded base | `#9C8E88` | `#A7988F` | 11 / 10 / 7 |

### Judging the remaining misses

- **Side rocks 18–26 darker: lighting.**
  - In the same render the caps are 31 darker, by the same factor of about 0.86.
  - In the front, f34, rear and parts shot the same rock keys are within 11.
  - Repainting would break those views.
- **Underside part R +16: lighting / conflicting targets.**
  - The parts shot lights the drum warm; the rear band wants more red, not less.
  - The key's hue and luminance are right.
- **Cream share 14.8 / 14.2 against 24.5 / 23.3 (front / f34): lighting.**
  - The class map shows the missing cream is the big stalk's upper and right faces and the drum, inside the cap's cast
    shadow. Those pixels fall under the cream mask's v 0.55.
  - The lit cream matches within 7. The side (K 20.3 against 24.2) and rear (25.3 against 19.4) are not short.
  - Brightening the keys would be painting light.
  - The other share misses (front R +5.5, C +4.2; f34 C +6.5; rear C −5.7) are the same pixels moving class, plus the
    accepted composition.
- **Front band 68 darker: lighting**, accepted in round 1 (it sits in the cap's shadow). The rear and side bands match.

### Blockers

None.

### Minors (record; none needs another round)

1. The Underside part is a thick puck (t / Ø 0.29) where the sheet's exploded disc is about 0.12 and paler. This
   follows decision 3 / §3.5 (the drum hangs 0.3–0.4 below the lip). If it is ever revisited, the cheap fix is
   to keep the hero drum and build the part with a thinner `side_top` / `t`.
2. Wall-facing rock area: 0.264 on the RockBase against about 0.20. The rocks read as domes.
3. The Cap part's underside (gill annulus) renders as a flat, dark, shadowed disc, unlike the close-up's light radial
   facets. It is never seen in the hero from normal angles. This is unchanged from round 1.
4. The Cap part renders 18 / 9 / 8 lighter than the exploded cap. The hero caps are within 3.
5. In the front and f34, the underside drum and the upper big stalk look olive / bronze in the cap's shadow (studio
   key). Check this in Studio under Emberhollow Caves lighting together with the existing stage-5 note.
6. Rear rock band −.16 / −.11 at f .30–.35 (behind the medium stalk).
7. R6's h / w is 0.78.
8. Round 1's composition misses are still accepted:
   - top cap share 87 %;
   - f34 W : H 1.15 and side D : H 0.92;
   - the rear small caps sit high;
   - the medium cap shows behind the small one in the side;
   - the small caps overhang the rock ring at the silhouette ends.

**Requires Manual Validation (Studio):** cap rust-orange, cream stalks and the tan underside under the zone's
lighting (minor 5). Export size 4.57 × 3.60 × 3.60 studs.
