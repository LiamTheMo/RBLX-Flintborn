# 025 Emberbloom — spec

Reference: `art/blender/assets/references/025.png`. The sheet's own title is "29 — EMBERBLOOM", "Individual Asset
Production Reference", footer "FLINTBORN — INDIVIDUAL MODEL STUDY", "PAGE 29/132" (INDEX.md row 25 calls it "Emberbloom
Flintborn Model Study"; the page number on the sheet is not the index number). The image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m025.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`
(one modeller does stages 1–6 in a background Blender; then a fresh verifier does stage 7).

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows a glowing seed and a separate VFX panel** (§7).

Sheet text:
- **Header:** "A crystal flower that grows from pale stone, with red leaves surrounding a glowing ember seed. Stylized,
  low-poly and modular for reuse."
- **Views:** Front Three-Quarter, Rear Three-Quarter, Front, Side, Rear, Top.
- **Exploded Construction:** labels Seedpod, Leaf (x6), Base (Rock Cluster); dashed arrows from each leaf's base and the
  seedpod's bottom point down into the base (the seed's arrow ends at a dot in the centre of the dirt floor).
- **Parts Breakdown:** Seedpod, Leaf, Base.
- **Construction close-ups:**
  - "Leaf Join": "Leaf plugs into base with a simple peg. Flat surfaces, clean angles." (a hexagonal peg under the
    leaf's base above a hexagonal socket in a rock).
  - "Base Underside": "Hollowed center. Simple geometry, flat faces. Used for placement on terrain."
  - "Seedpod Mount": "Seedpod sits on a central peg. Flat joining surfaces." (the seed's short bottom nub above a
    short 8-sided tube on the dirt floor).
- **Material palette:** Seedpod "Bright orange/yellow"; Leaf (Primary) "Saturated red"; Leaf (Shadow) "Dark red";
  Base Rock (Primary) "Warm brown gray"; Base Rock (Shadow) "Cool dark brown".
- **VFX Reference (separate from geometry):** "Ember Particles (Effect Only)": "Simple floating crystals/particles.
  Not part of the model geometry. Keep effects separate and modular." The panel shows the hero with a soft warm halo
  round the seed's upper half and 3–4 small yellow 4-point diamond crystals floating above and beside the tip.
- **Modeling notes:** "Keep geometry low-poly, with broad flat-shaded faces."; "Maintain chunky, readable silhouette.";
  "Use simple, clean shapes and solid colors."; "Model as separate reusable parts: seedpod, leaves, base."; "Keep
  pivots at center of each part."; "Flat joining surfaces for clean assembly."; "No baked glow, fire, or particles in
  geometry."; "Design to match Flintborn's stylized primitive aesthetic."
- **Game context:** `src/shared/Events/EventCatalog.luau` has the event node **`Emberbloom`** ("Emberbloom", Epic,
  spawn "Center"; drops AncientEmber 1, Herbs 10–14, Bloodroot 1–2). WorldModeling §11: "Emberbloom … Keep event
  inserts separate: seed/core … Reuse the common plant grammar. Effects, if later requested, must not conceal the
  geometry during approval." The old **R08 kit sheet** has `Emberbloom` (hero 8.4 W × 6.5 H; 5 outer + 4 inner thin
  lozenge petals round a 3.0 × 4.6 teardrop pod on a 10-boulder ring) and owns its names (§8). MODEL_PROGRESS row R08
  marks it "mostly-done: short smooth pod; no ember glow/sparks; thin petals".

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is about
`#F0EAE2`; each view's paper is the median of its box's top and bottom 4 rows. The labels "FRONT THREE-QUARTER" and
"REAR THREE-QUARTER" are blanked to paper before measuring (`m.py`). The masks are `cls()` in `m.py` (HSV;
background = within 18 of the paper):
- **S, seed:** hue 10–62°, sat ≥ 0.55, v ≥ 0.60.
- **L, leaves:** hue ≥ 330° or < 10°, sat ≥ 0.45 (and not S).
- **R, rock (and dirt):** anything else that is not background with v < 0.74.
- **O, other:** the pale ground shadow; not counted in the shares.
- The seed's deepest lower facets (hue < 10°, in the leaves' shade) fall into L, so the seed shares are a slight
  under-count. Use the same scripts on both images.

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m025_study\`.
Run with the scratch venv `...\scratchpad\venv22\Scripts\python.exe` (Pillow + numpy).
- **Helpers:** `m.py` (masks, view boxes `V`, `stats`), `bb.json` (silhouette boxes), `zoom.py`, `crops.py`,
  `grid.py`.
- **Measurements:** `measure.py` → `measure_out.txt` (bboxes, shares, top profiles, width per height, region extents,
  seed width profile); `bands.py` → `bands_out.txt` (bottom profiles, S/L/R share per 0.1 h, lowest leaf pixel per
  column); `parts.py` → `parts_out.txt` (exploded and breakdown parts by PCA); `seedprof.py` → `seedprof_out.txt`
  (seed width per height and colour bands); `polar.py` (top-view leaf and rock radius per 15°); `seedhue.py` →
  `seedhue_out.txt` (seed deep/mid/hot split, bright share).
- **Colour:** `samp.py` → `samp_out.txt` (swatches, views, parts, close-ups); `grad.py` → `grad_out.txt` (leaf base →
  tip, seed and rock height bands); `vfxs.py` (VFX panel particles and halo).
- **Crops:** `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `pb.png` (parts
  breakdown), `cu.png` (close-ups), `pal.png`, `vfx.png`, `notes.png`; grids `g_*.png` (10 % grid on the silhouette
  bbox, red = centre lines); mask previews `cls_*.png`.
- **Zooms:** `z_top.png`, `z_pb_leaf.png`, `z_expl_right.png` (three leaves), `z_expl_seed.png`, `z_expl_base.png`,
  `z_f34_base.png`, `z_cu.png` (the three close-ups), `z_vfx.png`.
- **To run the scripts on our renders,** point `R` (in `m.py`) at the render, set the view box, drop the label
  blanking, and re-run `measure.py` (it rewrites `bb.json`).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (Epic event resource node, `Emberbloom`). Hero budget 4000 tris, each part under
  1000. The plan in §4.3 lands at about 1500–2000 after the union.
- **Overall read (check this first).** A squat lotus of thick crystal leaves round a tall glowing gem, on a low ring of
  boulders. Wider than tall (front W : H 1.26):
  - **one tall faceted orange seed** in the centre: an elongated 8-sided gem with a long pointed top, widest a little
    above its middle, glowing (≥ 95 % of its pixels at v ≥ 0.9 in every elevation view); yellow on its upper facets,
    orange in the belt, red-orange at the bottom. It is the tallest thing and makes the top 30 % of the silhouette
    alone;
  - **six thick red crystal leaves**, each an elongated faceted diamond (a bicone shard) **pointed at both ends**,
    radiating from round the seed's foot: two splayed out sideways and low, two in front fairly low, two at the back
    standing more upright. Hero shares: leaves 55 %, seed 16 %, rock 29 %;
  - **a ring of about ten chunky brown-grey boulders** (plus 2–3 pebbles in front) round a low faceted dirt slab. The
    boulders make the bottom 20 % of every elevation view as an unbroken band under the leaves.
- **Focal silhouettes, in order:**
  1. The seed's long point rising alone above the leaves (h .70–1.0 is seed only in the front, side and rear).
  2. The leaf crown: two flat side points at h ≈ .5 out at f 0 and 1, and two back points at h ≈ .70 flanking the
     seed at f ≈ .25 and .80, all sharp.
  3. The rock band: a lumpy low band spanning 0.87 W, the leaves overhanging it a little at both ends.
- **Target size: about 7.0 W × 5.7 D × 5.5 H studs** (H = 1.0 C of the 5.5-stud character: the seed tip at the
  character's head). Tolerances W ±0.35, D ±0.4, H ±0.25. Decision §8.1.
  - **How it was derived.** The sheet has no character. The Emberbloom is an Epic event node that spawns alone at the
    map centre, so it should read at a distance like the other event nodes (M015 Ember Meteor 7.6 H, M014 Starstone
    7.8 H), but it is a plant on a rock ring, not a boulder. 1.0 C keeps the seed at eye height, the leaves at chest
    height and the boulders at knee height (1.0–1.4), which matches WorldModeling's boulder sizes. The front cell
    (225 × 178 px) then gives **32.4 px per stud**.
  - **Depth:** the side cell D : H 1.04 → 5.7. The hero layout (§2) gives 5.5–5.8.
  - **Alternatives:** R08's scale (6.5 H; × 1.18 → 8.3 × 6.7 × 6.5, taller than the player), or 0.8 C (4.4 H;
    × 0.8 → 5.6 × 4.6 × 4.4).
  - Resulting part sizes: seed Ø 2.25 × 4.55 tall; leaves L 3.4–3.6 × W 1.45 × T 0.7; boulders Ø 1.2–1.9 ×
    0.95–1.4 tall; dirt slab about 4.9 × 4.3 × 0.45.
- **Build frame:** front −Y, +X right, ground z 0, origin = the seed's axis on the ground (the centre of the ring).
  Stage 2 re-centres to the bbox bottom centre (the bbox centre sits about 0.15 in front of the axis, §2.2).
- **Stud mappings used below** (H = 5.5, W = 7.0, D = 5.7):
  - front cell X = (f − 0.50) × 7.0, z ≈ h × 5.5 (camera about 8° up, §3.1);
  - rear cell X = (0.50 − f) × 7.0 (screen right = −X);
  - side cell Y = (f − 0.51) × 5.7, **screen right = +Y (the back)** for the kit side camera at az 90 (+X);
  - top cell: counts, spread and radii only (§3.4).
  - On an elevated view a point at depth Y shows at screen height z cos e + Y sin e (front camera; −Y for the rear).
    At e = 8° a point 2.3 behind the axis reads about 0.3 (0.06 h) higher than it is, one in front 0.3 lower.

### 1.2 Measured views (`measure.py`, `bands.py`, `seedhue.py`)

| View (box) | Silhouette bbox (px) | W : H | Seed S | Leaves L | Rock R | Seed px at v ≥ 0.9 |
| --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (14,92,520,420) | 58–507 × 100–409 (450 × 310) | 1.452 | 16.1 % | 54.7 % | 29.2 % | 97.3 % |
| Rear three-quarter (530,92,1010,420) | 574–962 × 109–411 (389 × 303) | 1.284 | 16.0 % | 53.6 % | 30.4 % | 96.9 % |
| Front (14,458,270,660) | 28–252 × 461–638 (225 × 178) | 1.264 | 22.0 % | 48.6 % | 29.4 % | 95.7 % |
| Side (275,458,505,660) | 297–482 × 463–641 (186 × 179) | 1.039 (D : H) | 20.4 % | 49.0 % | 30.6 % | 95.8 % |
| Rear (510,458,762,660) | 528–744 × 461–641 (217 × 181) | 1.199 | 17.9 % | 50.8 % | 31.3 % | 95.5 % |
| Top (768,462,1010,660) | 782–995 × 462–651 (214 × 190) | 1.126 (W : D) | 11.2 % | 59.5 % | 29.3 % | 87.1 % |

**Seed colour split** (share of the seed's S pixels; median of each class):

| View | Deep (hue < 17°) | Mid (17–30°) | Hot (≥ 30°) |
| --- | --- | --- | --- |
| f34 | 25.6 % `#F74F1B` | 49.8 % `#FD7124` | 24.7 % `#FDC23D` |
| r34 | 33.2 % `#F34F1A` | 39.3 % `#FD6F23` | 27.5 % `#FDA634` |
| front / side / rear | 25.6 / 28.4 / 29.1 % `#F6521A`–`#F44C18` | 51.7 / 47.4 / 48.0 % `#FD7925`–`#FD7223` | 22.7 / 24.2 / 22.8 % `#FDA835`–`#FD9D2F` |
| top | 19.7 % `#DE4111` | 48.0 % `#FC7A27` | 32.3 % `#FDA336` |
| exploded / breakdown | 20.0 / 21.3 % | 56.5 / 53.9 % | 23.5 / 24.8 % |

- **Reading:** about a fifth of every elevation view is glowing seed, and almost all of it reads at full brightness
  (v ≥ 0.9; the darkest seed decile is still `#EE4818`). Leaves are about half, rock a steady 29–31 % everywhere,
  including the top.
- **Verifier tolerance:** shares ±4 points (top ±6); seed bright share ≥ 90 % (top ≥ 82 %); deep/mid/hot ±8 points;
  profile values ±0.06 h; positions ±0.06 of W/H unless stated.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .49 | .55 | .57 | .59 | .61 | .61 | .78 | .78 | .81 | .91 | 1.0 | .94 | .84 | .74 | .77 | .80 | .82 | .59 | .61 | .60 | .60 |
| Front | .52 | .54 | .55 | .55 | .54 | .71 | .71 | .78 | .87 | .96 | .99 | .93 | .84 | .70 | .65 | .69 | .71 | .53 | .52 | .50 | .46 |
| Side | .52 | .53 | .54 | .64 | .63 | .61 | .60 | .58 | .80 | .87 | .95 | 1.0 | .95 | .88 | .80 | .62 | .65 | .68 | .65 | .67 | .69 |
| Rear | .55 | .55 | .55 | .54 | .62 | .72 | .69 | .67 | .78 | .87 | .95 | 1.0 | .93 | .85 | .73 | .68 | .71 | .63 | .62 | .64 | .65 |
| r34 | .50 | .51 | .52 | .70 | .68 | .67 | .64 | .76 | .87 | .96 | .98 | .91 | .82 | .68 | .72 | .75 | .60 | .62 | .62 | .61 | .31 |

- **Leaf points in the front** (the targets for the crown): side tips at (f 0.0, h .52) and (1.0, .46); back-pair
  tips at (.26, .72) and (.80, .71); front-pair tips at about (.12, .45) and (.88, .47), partly in front of the side
  leaves. Between the back tips and the seed the profile dips to .65–.70 (the gap between leaf and seed).
- **Seed point:** f .50, h 1.0 in every elevation view; it is the only thing above h .73 (front), .70 (side), .74
  (rear).

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .12@.44 .80@.11 .82@.07 .78@.11 .78@.12 .94@.01 .82@.16 .53@.30 .54@.30 .12@.45 .01@.50
front  .24@.38 .87@.07 .82@.10 .67@.16 .84@.10 .95@.00 .57@.24 .57@.25 .26@.36 .14@.42 .02@.48
side   .31@.41 .94@.05 .85@.09 .68@.17 .81@.10 .96@.00 .86@.12 .35@.38 .30@.40 .17@.47 .03@.54
rear   .26@.35 .88@.06 .82@.09 .66@.17 .81@.10 .92@.03 .79@.19 .59@.24 .28@.41 .16@.47 .02@.53
```

So: the rock band 0.82–0.88 W wide at h .1–.2; a pinch at h .3 (0.66–0.68 W, the leaves' lower edges rising out of
the ring); the crown widest at h .5 (0.92–0.96 W, the side tips); at h .6–.7 the back leaves and seed (0.57 W
front); above h .8 the seed alone (0.26 W at h .8, 0.14 at .9).

**Height bands** (share of S / L / R per 0.1 h, front; the others agree within ±10):

```
h  .0-.1  R100        .1-.2  L8  R92       .2-.3  L76 R24      .3-.4  L99         .4-.5  S14 L86
h  .5-.6  S39 L61     .6-.7  S60 L40       .7-.8  S96 L4       .8-.9  S100        .9-1.0 S100
```

**Bottom profiles** (lowest pixel per column above the bbox bottom, fraction of H): front .045 at f .10, .011 at .30,
0 at .45–.55, .034 at .85; f34 .106 at .10, 0 at .50, .084 at .90. The ring's front curve gives the elevation: about
5–8° for the front, side and rear cells, about 11–14° for the three-quarters (§3.1).

**Seed width** (S width / W, per tenth of the visible seed height from its lowest visible pixel to the tip):

```
front  .00 .16 .28 .32 .32 .31 .28 .24 .16 .08 .01     visible from h .39; max 72 px = 0.32 W = 2.24 studs
side   .01 .31 .35 .38 .36 .33 .32 .24 .17 .09 .02     (side W is 0.82 of the front's: 70 px)
rear   .15 .29 .32 .33 .31 .30 .27 .20 .15 .08 .01
f34    .00 .22 .25 .27 .26 .25 .23 .19 .13 .07 .01
```

The seed's lower part is hidden behind the front leaves (their tips cross in front of it at h .4–.5). Its sides are
nearly parallel from h .45 to .60, then it tapers over the top 0.40 H to a sharp point. **Seed profile targets
(front, in studs):** half-width 1.12 at z 3.0–3.4, 1.07 at z 3.8, 0.72 at z 4.5, 0.57 at z 4.85, 0.29 at z 5.15, 0
at z 5.5.

### 1.3 Silhouette and composition per view

**Front (`g_front.png`; governs the orthographic profiles).** Camera on the front axis, about 8° up.
- **Seed:** centred (f .33–.65), visible from h .39 to 1.0; three facet rings show as diamond facets (about 4 across);
  hot yellow facets on the upper right, the belt orange, the lowest visible facets red-orange where the leaves shade.
- **Leaves (6 visible):** the two side leaves run from the centre at h ≈ .2 out to tips at f 0 (h .52) and f 1
  (h .46), their broad faces tilted up toward the camera; the two front leaves lie in front of them, lower, tips at
  f ≈ .12 and .88 (h ≈ .45), their bases crossing in a V just under the seed at f .47–.50, h .17–.20; the two back
  leaves stand behind the seed's flanks, tips at (.26, .72) and (.80, .71), partly covered by the seed.
- **Rocks:** a continuous band from f .07 to .93 at h .0–.2; the front-centre boulder is the biggest (about f .37–.64,
  1.9 studs wide); two pebbles at its lower right (f .62–.70, h .0–.05). Back boulders show above the front ones at
  the ends (f .10–.20 and .80–.90, tops at h .28–.34).
- **Facets:** leaves show 4–6 big flat facets each (a centre ridge and two facets a side); boulders 6–10 facets each.

**Front three-quarter (`g_f34.png`; the hero).** Not a true three-quarter: the composition is the front's, seen from
higher (e ≈ 14°) and turned about 20° so the right side is further away (the right side tip at h .60 against the
left's .49). The leaves are drawn more splayed (W : H 1.45 against the front's 1.26). Seed f .37–.64, h .45–1.0; the two
front leaves big and low (h .25–.55) in front of the seed's foot; the back pair tips at (.31, .78) and (.80, .82); the
side tips (0, .49) and (1.0, .60). Rocks: about 9 boulders and 2 pebbles visible, the front-centre one biggest.

**Side (`g_side.png`; kit camera at +X: screen right = +Y, the back).** The crown is asymmetric front to back: at
screen left (the front) a low leaf tip at (f 0.0, h .52) and a second at (.13, .62); at screen right (the back) two
tall tips at (.88, .68) and (1.0, .69). This is the hero's layout seen from the side (front pair low, back pair high,
§2.2). Seed f .36–.73, the centre-right big leaf in front of it (the right side leaf, nearest the camera). Rock band
f .05–.95 at h .0–.2, three boulders across the front of it.

**Rear (`g_rear.png`; screen right = −X).** The two back leaves are nearest: big, face-on, tips at (.20, .62) and
(.82, .62); behind them the two front leaves show as uprights flanking the seed at (.25, .72) and (.80, .71); the side
tips at (0, .55) and (1.0, .65). The front-pair uprights are drawn higher here than the front view allows (§3.2). Rock
band as the front, its centre boulder the biggest.

**Rear three-quarter (`g_r34.png`).** The rear composition from higher (e ≈ 14°), turned so screen right (−X) is
nearer: the screen-right side tip falls to h .31 and the screen-left one stays at .50 (§3.1). Seed f .33–.63.

**Top (`z_top.png`; image top = back by kit convention, §3.4).** A star of **5 leaves** about 72° apart (tips at
about 5°, 85°, 165°, 228° and 305° round the seed, screen angles CCW from screen right; tip radius 0.43–0.51 W), the
seed seen end-on as a faceted octagon (Ø 0.30 W) at the centre, and the boulder ring all round it outside and between
the leaves (ring outer radius 0.40–0.50 W, inner about 0.30 W). The cell is a little tilted (boulder fronts and the
ground shadow show at the bottom).

**Exploded (`expl.png`, `z_expl_*.png`) and close-ups (`z_cu.png`).** See §1.4.

### 1.4 Parts (Exploded Construction (14,700,650,1190), Parts Breakdown (664,705,1010,935), close-ups (664,965,1010,1312))

Facet language for every part: broad flat-shaded facets, chunky, crisp edges, no noise, no bevels.

#### Seedpod — exploded (277,697,392,884) 116 × 188 px; breakdown (721,723,796,832) 76 × 110 px

- **Shape:** an elongated faceted gem: about 8 sides, rings offset by half a step so the faces are **diamonds and
  kites**, not vertical strips (the exploded shows 4 facets across, a 5–6-facet pointed crown, and a shorter lower
  cone ending in a small blunt point). The upper facets yellow-orange, the lower red-orange (§5.3).
- **Proportions:** exploded W : H 0.62, breakdown 0.69; widest at 0.50–0.58 of the height; width/H per 0.05 up from
  the bottom (exploded): `.01 .03 .28 .36 .42 .47 .54 .55 .56 .59 .60 .61 .58 .53 .47 .41 .35 .27 .18 .10 .01`.
- **In the hero** the seed is the same width (Ø 2.25) but its point is longer (the top cone is 1.0 × the width against
  0.73 × in the exploded) and its lower half is hidden in the leaves, so the hero seed is about 4.55 tall (W : H
  0.49). Decision §8.3: the hero profile governs (§1.2 seed targets).
- **Seedpod Mount close-up:** the seed's bottom ends in a short 8-sided nub (Ø about 0.2 of the seed's width) that sits
  on a short 8-sided **tube** on the dirt floor (Ø about 0.25 of the seed width, as tall as wide, a hole in its top).
- **Construction:** `_seed(d, z0, z1, seed)`: 8 sides, rings at (z fraction of the seed height from its bottom,
  radius fraction): (0, 0.11 nub), (0.03, 0.11), (0.08, 0.40), (0.20, 0.75), (0.35, 0.96), (0.48, 1.0), (0.62, 0.95),
  (0.77, 0.64), (0.86, 0.50), (0.93, 0.26), tip (1.0, 0). Each ring is rotated half a step from the one below, ±4 %
  radius jitter per vertex, flat nub cap. **About 150 tris.**

#### Leaf ×6 — exploded six (the far-left two merge in the mask): upper-right (388,772,530,894), lower-right (414,852,627,1018); breakdown (853,735,967,824)

- **Shape:** a thick faceted diamond shard — a **bicone pointed at both ends** like a crystal, not a flat leaf, a
  tent, a ball or a tulip cup.
  - Outline: widest at 0.45–0.55 L, **W : L 0.40–0.43** (exploded 0.40, breakdown 0.43). Full width / L per tenth of
    the length, base → tip (mean of the two clean leaves): `.12 .22 .30 .36 .41 .41 .37 .31 .24 .12`. **Both ends
    come to real points**: the tip angle in plan is 40–50°, the base narrows to 0.10–0.15 L where the peg sits.
  - Section: a flattened hexagon at the widest — a top ridge along the length, a raised top apex vertex at about
    0.45 L, the two outline edges, and a lower keel. The top shows 4–6 broad facets (two long ones from the apex to the
    tip, two to three from the apex to the base), the underside 2–4.
  - **Thickness about 0.20 L** (top 0.12 L above the outline plane, keel 0.08 L below): the breakdown leaf shows a
    thick dark underside band, the exploded lower-right leaf a deep side face.
  - No bend, no curl, no serration, no midrib groove.
- **Leaf Join close-up:** a short **hexagonal peg** under the leaf's base (Ø about 0.12 L, as long), plugging into a
  hexagonal socket.
- **Size (hero governs):** L 3.4–3.6, W 1.45, T 0.7.
- **Construction:** `_leaf(L, W, T, seed)`:
  - outline 8 points (base point, 3 per side at 0.2 / 0.5 / 0.8 L with half-widths 0.27 / 0.50 / 0.30 of W, tip);
  - top: the apex at 0.45 L raised T × 0.6 and a ridge point at 0.2 L raised T × 0.35, fanned to the outline;
  - bottom: a keel apex at 0.5 L lowered T × 0.4, fanned to the outline;
  - ±4 % jitter on the outline and the apex, no two leaves identical (seed per copy);
  - top 10 + bottom 8 ≈ **18–24 tris**; spend up to about 36 if the leaves read too plain (one more outline pair at
    0.35 L), never on smoothing;
  - the exported part adds its hexagonal peg (12 tris); in the hero the base end and its peg sink into the slab.

#### Base (Rock Cluster) — exploded (142,966,507,1152) 366 × 187 px; breakdown (754,843,955,921) 202 × 79 px

- **Shape:** a low faceted **dirt slab** (a thick disc with a slightly raised, cracked, faceted top and short sloped
  sides; its visible side is about 0.4 of a front boulder's height) carrying a **ring of about ten dome boulders**
  round its rim — big ones at the front and sides partly outside the slab's edge, smaller ones at the back on the slab's
  rim — and 2–3 pebbles. The seed's mount peg stands at the slab's centre; the leaves' arrows end at the slab's inner
  ring, round the peg.
- **Boulders:** squat domes, height 0.65–0.75 of width, 5–7-sided footprints with 2 height rings and a quiet top
  (WorldModeling §12.1), flat bottoms. In the hero the front-centre one is the biggest (Ø 1.9 × 1.35 tall).
- **Base Underside close-up:** a **hollowed centre**: a broad shallow faceted bowl under the slab, ringed by the
  boulders' flat bottoms. Decision §8.6.
- **Construction:** `_slab(rx, ry, h, seed)` (14 sides, top ring raised 0.05 at r 0.55, an underside recess, no
  booleans) + `_boulder(d, h, seed)` × 10 + `_pebble(d)` × 3 + `_peg()`; the boulders overlap the slab by 0.2–0.4 and
  each other by 0.1–0.2. Part size about **6.1 × 5.3 × 1.4**.

#### Pegs and sockets (close-ups)

- Leaf pegs (hexagonal) and the seed's mount tube (8-sided): joinery notation, hidden in every assembled view.
  **Not modelled in the hero**; the Petal part keeps its peg and the RockBase part its mount tube (decision §8.5). No
  socket holes anywhere.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, origin = the ring centre). Azimuths are measured from +X
counter-clockwise (front = 270°, back = 90°); elevation = rise from horizontal.

### 2.1 Seed

- Axis at (0, 0); bottom nub at z 0.95 (on the hidden mount, inside the leaf cluster), widest Ø 2.25 at z 3.0–3.4,
  tip at z 5.5. Rings from §1.4 scaled to z 0.95–5.5. One ring vertex points at the front camera (az 270) so the front
  shows a facet edge down the middle, as drawn.
- Expected front width (2r / W): .32 at z 3.2, .31 at z 3.8, .21 at z 4.5, .16 at z 4.85, .08 at z 5.15.

### 2.2 Leaves (6 copies of `_leaf`, each with its own seed)

| Leaf | Azimuth | Base (sinks into the slab) | Elevation | L × W × T | Tip (expected) | Sheet evidence |
| --- | --- | --- | --- | --- | --- | --- |
| P1 right side | 0° | (+0.7, 0, 0.6) | 34° | 3.4 × 1.45 × 0.7 | (+3.52, 0, 2.50) | front tip f 1.0, h .46 (z 2.5) |
| P2 left side | 180° | (−0.7, 0, 0.6) | 36° | 3.4 × 1.45 × 0.7 | (−3.45, 0, 2.60) | front tip f 0.0, h .52 (z 2.85, f34 .49) |
| P3 front right | 312° | (+0.47, −0.52, 0.6) | 37° | 3.5 × 1.45 × 0.7 | (+2.34, −2.60, 2.71) | front tip f .88, h .47; side tip f 0, h .52 |
| P4 front left | 228° | (−0.47, −0.52, 0.6) | 37° | 3.5 × 1.45 × 0.7 | (−2.34, −2.60, 2.71) | front tip f .12, h .45 |
| P5 back right | 48° | (+0.47, +0.52, 0.6) | 52° | 3.6 × 1.45 × 0.7 | (+1.95, +2.17, 3.44) | front tip f .80, h .71; rear near tip f .20, h .62; side f .88–1.0, h .68 |
| P6 back left | 132° | (−0.47, +0.52, 0.6) | 52° | 3.6 × 1.45 × 0.7 | (−1.95, +2.17, 3.44) | front tip f .26, h .72; rear near tip f .82, h .62 |

- **Roll:** each leaf's width is tangential (perpendicular to its azimuth) and its top ridge faces up and inward, so
  the broad top facets face the seed and the sky, like a lotus. The back pair's top faces show to the rear camera
  (they are the rear view's big face-on leaves); the side and front leaves show their top faces to the elevated front
  cameras. Roll ±8° per leaf so the facet light varies.
- **Contact:** every leaf's base point and its first 0.3 L sink into the slab and the seed's foot region (z 0.45–1.0);
  neighbouring leaves overlap near their bases (never coplanar); the seed's lower cone sits inside the ring of leaf
  bases, the leaves touching it from z 1.0 to about 1.6 (the front pair cross in front of it).
- **Expected front view** (e 8°): side tips h .46/.47; front-pair tips (2.71 − 0.36) / 5.5 = h .43 at f .17/.83; back
  tips (3.42 + 0.30) / 5.5 = h .68 at f .22/.78; widest at h ≈ .47 (full W). Back-tip f is 0.04 inside the sheet's
  .26/.80 — widen P5/P6 to az 44°/136° if the front's back tips land inside .22/.78.
- **Expected side view** (+X camera): front-pair tips at screen left (f ≈ .05, h ≈ .45), back-pair tips at screen right
  (f ≈ .92, h ≈ .66).

### 2.3 Base

- **Slab:** an oval 14-gon, rx 2.45, ry 2.15, z 0 → 0.45 (top ring at 0.55 r raised to 0.50), sides sloped 25°,
  centred on the axis. Underside recess Ø about 3.0 × 2.6, 0.3 deep (§8.6).
- **Boulders** (centre on the oval ring rx 2.55, ry 2.2; height h; footprint Ø d; `az` as above):

| # | az | d × h | Note |
| --- | --- | --- | --- |
| B1 | 270° | 1.9 × 1.35 | front centre, the biggest; front f .37–.64 |
| B2 | 305° | 1.6 × 1.15 | front right |
| B3 | 235° | 1.5 × 1.1 | front left |
| B4 | 340° | 1.7 × 1.25 | right |
| B5 | 200° | 1.7 × 1.2 | left |
| B6 | 20° | 1.4 × 1.1 | back right |
| B7 | 160° | 1.5 × 1.15 | back left |
| B8 | 60° | 1.3 × 1.0 | back |
| B9 | 120° | 1.3 × 0.95 | back |
| B10 | 90° | 1.2 × 1.0 | back centre |

- **Pebbles:** P-a Ø 0.55 × 0.35 at (+1.1, −2.75), P-b Ø 0.4 × 0.28 at (+1.5, −2.6) (the front's two pebbles right of
  B1), P-c Ø 0.5 × 0.32 at (−1.4, −2.75) (f34's front-left pebbles).
- **Expected:** ring outer X ±3.05 (0.87 W, front h .1 width .87), Y −2.85 … +2.6; boulder tops z 0.95–1.35 (front
  rock band h .0–.20, back boulders reading h .28–.34 at the ends).
- **Expected hero:** X −3.45 … +3.52, Y −2.9 … +2.75 (leaf half-widths included), z 0 … 5.5 → **7.0 × 5.65 × 5.5**.

### 2.4 Checks on the renders

- **front_sheet (0, 8):** W : H 1.20–1.32 (sheet 1.264); shares ±4 of 22.0 / 48.6 / 29.4; top profile ±0.06 at the
  leaf points of §1.2; width per height ±0.07 (the h .3 pinch at 0.67 W, h .5 at 0.95); 6 leaves; seed alone above
  h .73.
- **f34_sheet (−20, 14):** shares ±4 of 16.1 / 54.7 / 29.2; side tips lower on the left (h ≈ .49) than the right
  (≈ .60); W : H 1.25–1.45 (the sheet's 1.45 is drawn wide; report the value).
- **rear_sheet (180, 8):** shares ±4 of 17.9 / 50.8 / 31.3; the two back leaves big and face-on in front of the seed's
  foot.
- **side_sheet (90, 8):** D : H 0.98–1.10; low tips at screen left (front), tall at screen right (back).
- **r34_sheet (200, 14)** and **top (0, 89) + top_tilt (0, 70):** by counts and shares (§3.1, §3.4).

## 3. View conflicts and resolutions

### 3.1 The three-quarter cells are near-front and near-rear views

- **Evidence.** The f34 is the front composition (seed centred, the same leaves) seen from about 14° up; its side tips
  differ in height by 0.11 H (left lower), which a turn of about 20° at e 14° explains. The r34 is the rear
  composition, its screen-right tip the lower one. The f34 is also drawn about 15 % wider than the front cell.
- **Resolution.** Compare the hero with an extra **`f34_sheet (−20, 14)`** (the kit's front34 is −28: camera front-left,
  so the left side is nearer, as drawn) and the r34 with **`r34_sheet (200, 14)`** (camera back-left, screen right =
  −X nearer; the kit's rear34 at 152 is the other side). **Probe the handedness with one render before using either.**
  Judge the f34 by shares, the seed's place and the leaf points, not by W : H. The front cell governs the orthographic
  profiles; the hero governs the overall read.

### 3.2 Leaf heights: front and side against the rear

- **Evidence.** The front, f34 and side all show the front leaves low (tips h .45–.52) and the back leaves high (h
  .68–.72). The rear agrees for the back pair (near, tips h .62 → z ≈ 3.7) but draws the front pair, behind the seed,
  at h .70–.72, which needs their tips at z ≈ 3.5 — the front view puts them at z ≈ 2.7.
- **Resolution.** The front, f34 and side govern (three views against one): front pair 37°, back pair 52° (§2.2). Our
  rear will show the front-pair tips about 0.1 h lower than drawn (h ≈ .60); record it, don't chase it.

### 3.3 Leaf count: 6 against the top cell's 5

- **Evidence.** The exploded labels "Leaf (x6)" and draws six; the front, rear and side each show six tips. The top
  cell draws five leaves about 72° apart.
- **Resolution.** Build **6** (decision §8.2). Judge the top by: 5–6 leaves round the full circle with sharp tips at
  radius 0.43–0.51 W, the seed's octagon at the centre (Ø 0.28–0.32 W), boulders showing all round outside and between
  the leaves (rock share 29 ± 6 %).

### 3.4 Top view orientation and tilt

- Read the top with image top = back (kit convention). Our layout has a gap at the front centre (between P3 and P4,
  84°) and at the back centre (between P5 and P6, 84°); the sheet's star has a leaf at the image top. Compare the kit
  `top (0, 89)` and an extra `top_tilt (0, 70)` by counts and shares only.

### 3.5 Exploded seed against the hero seed

- Same width, but the exploded seed is stubbier (W : H 0.62, top cone 0.73 × the width) than the hero's (top cone
  about 1.0 × the width, total about 4.55 tall to reach the mount). Decision §8.3: one builder at the hero profile; the
  exported `EmberbloomPod` is that same seed.

### 3.6 Ring shape

- The rock band is 0.87 W wide in the front (6.1 studs) but 0.85 of the narrower side cell (4.85 studs); the top cell
  gives W : D 1.10 for the ring. Build a slightly oval ring (6.1 × 5.45 outside the boulders, §2.3); the leaves set the
  hero's depth.

### 3.7 "No baked glow … in geometry" and "solid colors" against the glowing seed and the blended-colour rule

- The modelling note forbids glow halos, flames or particle shapes as mesh; it does not forbid an emissive material.
  The header calls it "a glowing ember seed", the seed stays at v ≥ 0.9 even on its shade facets, and the VFX panel
  adds a halo. So the seed's keys are Neon (§7.1) and the halo and floating crystals are VFX sockets, never geometry.
- The user's blended-colour rule wins over "solid colors", and the sheet itself shows painted gradients: the seed
  deep → orange → yellow from bottom to top, the leaves darker at the base and brighter toward the tip (§5.3). Keep
  Tint low so the asset still reads "clean".

## 4. Construction plan (modeller, stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `pod()` → `EmberbloomPod`: the hero seed (Ø 2.25 × 4.55) with its nub. Compare with `z_expl_seed.png` and
     `pb.png`: 8 sides of diamond facets, a long sharp top point, a short lower cone, widest a little above the middle.
   - `petal()` → `EmberbloomPetal`: L 3.5, W 1.45, T 0.7 with its hexagonal peg. Compare with `z_pb_leaf.png`: W : L
     0.40–0.44, widest at 0.45–0.55 L, **sharp points at both ends**, thickness 0.18–0.22 L, 4–6 top facets.
   - `rock_base()` → `EmberbloomRockBase`: slab + 10 boulders + 3 pebbles + the mount tube (§2.3). Compare with
     `z_expl_base.png` / `pb.png`: boulders domed and chunky, the slab's dirt top visible inside the ring and lower than
     the boulder tops, underside recess.
   - Render a parts shot (`extra`, about (−20, 25)) laid out like the exploded (seed above the base, leaves round it).
2. **Hero:** `_paste` (m011 pattern) the base, 6 petals (§2.2) and the pod (§2.1); unite into one closed shell **one
   piece at a time**, saving the work file between risky steps (base first: slab + boulders with `union_loose` then
   one exact union; then leaves; the seed last); `m004.floor_cut` at z 0. Origin at the bbox bottom centre; transforms
   applied. Decision §8.7.
3. **Budget** (§4.3): hero about 1500–2000 (limit 4000); parts ≤ 1000 each.
4. **Placeholder keys** (stage 1): `m025_seed`, `m025_leaf`, `m025_rock`. Stage 4 adds the rest (§5.4). Keep the seed's
   faces separable (the Neon keys must land on whole seed facets only).
5. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** a tall pointed glowing gem above a crown of six thick pointed red shards, on a lumpy boulder
      ring; nothing round, nothing flat-leaved, nothing cupped shut round the seed.
   2. **front_sheet (0, 8)** and **f34_sheet (−20, 14)** against their cells: §2.4's checks; 6 leaf tips; seed alone
      above h .73.
   3. **Leaf shape** (on the parts shot and in the top view): each leaf's outline W : L 0.38–0.46, both ends sharp
      (the last 0.1 L narrower than 0.15 L), tip angle 40–55°; top facets distinct (at least 4 lit/shade steps along
      a leaf).
   4. **Seed shape:** front width per §2.1 ±0.03 W; top cone ≥ 2.0 tall; 8 ± 1 facets round; diamond facets.
   5. **rear_sheet (180, 8)**, **side_sheet (90, 8)**, **r34_sheet (200, 14)**: shares ±5 and leaf counts (§3.1, §3.2).
   6. **Top (0, 89) + top_tilt (0, 70):** §3.3's checks.
   7. **Rock band:** h .0–.2 at least 90 % rock in the front, side and rear; rock share 29 ± 4 % in every view; the
      boulders show between the leaf tips in the top view.
   8. **Kit views** (front34, rear34, underside): self-consistency; the underside shows the boulders' flat bottoms and
      the slab's recess.
   9. **Parts against their cells** (step 1). **Hero size** 7.0 × 5.7 × 5.5 (±0.35 / ±0.4 / ±0.25).
6. **Stage 2:**
   - zero non-manifold, boundary, wire and loose elements; no zero-area faces or n-gons; normals outward;
   - no faces under 5° where leaf bases, the seed foot, the slab and boulders meet (m011 `_tidy` / `_desliver`);
   - don't decimate the leaves below their 8-point outline with top apex and keel, the seed below 8 sides and its
     offset rings, or the boulders below 5 sides; keep the seed's facet rows (they carry the colour bands).
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Seed (8 sides, 10 rings, nub) | 1 | 150 | 150 |
| Leaves (8-point bicone shard) | 6 | 24–36 | 150–220 |
| Boulders (5–7-sided, 2 rings, domed top) | 10 | 50–70 | 600 |
| Pebbles | 3 | 20–28 | 75 |
| Slab (oval 14-gon, raised top ring, recess) | 1 | 110 | 110 |
| **Sum before union** | | | **about 1100–1150** |
| **Hero after union** (seams, slivers, floor cut) | | | **about 1400–2000** (limit 4000) |
| Parts: Pod / Petal / RockBase | | | about 150 / 40 / 850 (limit 1000) |

## 5. Colour plan (modeller, stage 4)

### 5.1 Swatches (flat; medians of a 28 × 24 box inside each)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Seedpod | (40,1249,68,1273) | `#FE7C2C` | 23°, 0.83, 1.00 |
| Leaf (Primary) | (40,1298,68,1322) | `#C0242D` | 357°, 0.81, 0.75 |
| Leaf (Shadow) | (40,1347,68,1371) | `#8C1D23` | 357°, 0.79, 0.55 |
| Base Rock (Primary) | (40,1396,68,1420) | `#795D54` | 15°, 0.31, 0.47 |
| Base Rock (Shadow) | (40,1445,68,1469) | `#5B4C48` | 13°, 0.21, 0.36 |

- **Seedpod** is the seed's mid (belt) colour; the sheet also paints a hot yellow and a deep red-orange (§5.3).
- **Leaf (Primary)** matches the unshadowed exploded and breakdown leaves (`#BC2830`–`#C02931`).
- **Leaf (Shadow)** is the shade side and the bases (`#8A1A1F` in the Leaf Join close-up).
- **Base Rock (Primary)** sits between the view medians (`#70594E`–`#775E52`) and the exploded base (`#7C5E51`).
- **Base Rock (Shadow)** is a little lighter and greyer than the rendered shade quartiles (`#4B3932`–`#4F3C34`).

### 5.2 Rendered regions (`samp.py`, `grad.py`; median / lit quartile / shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Seed, f34 / r34 | V | S | `#FC7024` / `#FC6E25` | `#FDC23D` / `#FDA735` | `#F64F1B` / `#F04718` |
| Seed, front / side / rear / top | V | S | `#FC7926` / `#FC7025` / `#FD7325` / `#FC7D29` | `#FDA735` / `#FD9C32` / `#FD9C30` / `#FDAB3E` | `#F65118` / `#F44A17` / `#F24816` / `#E44913` |
| Seed, exploded / breakdown | (255,690,420,895) / (700,715,820,838) | S | `#FC7C27` / `#FD762A` | `#FDAD36` / `#FEA736` | `#F04B16` / `#EC4B16` |
| Seed, mount close-up (bottom cone) | (700,1208,860,1260) | S | `#E64714` | `#FC6D1E` | `#CC3310` |
| Leaves, f34 / r34 | V | L | `#B6262B` / `#81191E` | `#F83D44` / `#E2353D` | `#5A1013` / `#550E11` |
| Leaves, front / side / rear / top | V | L | `#85191D` / `#8B1A1E` / `#7F1A1F` / `#C5252C` | `#E9353F` / `#DA323A` / `#D42F37` / `#F1343C` | `#500E10` / `#570E11` / `#510D10` / `#6A1115` |
| Leaves, exploded all / upper-right | (20,750,650,1030) / (388,770,532,896) | L | `#C02931` / `#BC2830` | `#F03A43` / `#E33841` | `#73181D` / `#921B21` |
| Leaf, breakdown / Leaf Join | (845,735,980,835) / (678,972,865,1040) | L | `#BC2930` / `#8A1A1F` | `#E9373F` / `#B6232A` | `#72191E` / `#691519` |
| Rock, f34 / r34 | V | R | `#674F46` / `#715A50` | `#99776A` / `#A88372` | `#382B26` / `#4B3932` |
| Rock, front / side / rear / top | V | R | `#70594E` / `#765C52` / `#775E52` / `#645049` | `#9F7B6B` / `#A78375` / `#A98574` / `#A78778` | `#4C3A34` / `#493832` / `#4D3C35` / `#392A26` |
| Rock, exploded base / breakdown | (130,950,530,1165) / (748,835,975,925) | R | `#7C5E51` / `#84655A` | `#9F8278` / `#9A796D` | `#4F3C34` / `#56423A` |
| Dirt floor, exploded / breakdown | (250,1010,420,1080) / (800,850,900,885) | R | `#634B41` / `#634A41` | `#A1857A` / `#76574C` | `#3D2E28` / `#4D3A36` |
| Base underside / mount close-up rock | (678,1092,865,1198) / (678,1240,865,1308) | R | `#533D34` / `#5B453D` | `#786158` / `#9F7E71` | `#32241F` / `#40312B` |
| VFX panel: seed / leaves / rocks | (380,1290,540,1450) / (283,1290,650,1460) / (283,1400,650,1495) | S/L/R | `#FD8010` / `#AF2120` / `#674F46` | `#FED11D` / `#F83D41` / `#9C7767` | `#F64E0F` / `#570E11` / `#372924` |

**Gradients along a part** (medians in five equal steps):

```
seed bottom -> top
  front        #F24513 #FC641F #FD7C29 #FDA234 #FD9933
  side / rear  #EE3E15 #FC621F #FD792C #FD9730 #FD9B32  /  #F24415 #FC691E #FD7E2B #FD982E #FD9D34
  f34 / r34    #F74C1A #FC6520 #FD822C #FD9432 #FD963C  /  #F34016 #FC6120 #FD772D #FD9D33 #FDA738
  exploded     #E04113 #FA641B #FD8528 #FD8F31 #FD9E31
  breakdown    #CB3613 #FA641E #FD8A31 #FD8E34 #FDA93A
leaf base -> tip
  breakdown    #A9262F #B1272F #BE2930 #E7353E #D7333C
  expl UR      #A32229 #B3242B #BF2831 #D93239 #EA373F
  expl R-low   #75191E #C8333E #C02830 #DA2E39 #EE373F      (base in the leaf's own shade)
rock bottom band (lowest 20 %): f34 #684F45, front #6F574C, rear #715B4F, exploded #664F45
```

Deciles (dark → light), front:

```
seed   #ED3D0D #F75421 #FE5B1B #FC6428 #FC751E #FD7B24 #FC892B #FE9131 #FEA534 #FEAD39
leaves #340A0B #541214 #661519 #75161C #84161C #93181D #B72026 #D72F14 #EB3238 #FC3B45
rock   #362A28 #513D34 #5C4942 #665045 #6A564E #7B5B4C #886354 #946C5B #9A7868 #B0846F
```

### 5.3 How the colour works

**Seed.**
- Self-lit: the shade quartile stays at `#F04718`–`#F65118` (v ≥ 0.94) in every view, so the facets do not darken with
  the light; the facet variety is painted.
- **Bottom → top gradient** on every drawing: red-orange `#F04A16` at the bottom fifth → orange `#FC6420` → `#FD7C2A`
  → amber `#FD9832` at the top two fifths, plus a scatter of hot yellow facets (`#FDC23D` in the f34, `#FDA735`–
  `#FDAB3E` elsewhere) on the upper half, more on the upper right (the drawing's light side). The split is about
  25 % deep, 50 % mid, 25 % hot in every view (§1.2).
- No dark seed pixels anywhere: the darkest decile is `#ED3D0D`.

**Leaves.**
- One saturated red family, hue 357–0°, sat 0.78–0.82. Unshadowed median `#BE2930`. The elevation views are much
  darker (`#7F1A1F`–`#8B1A1E`) because they look at the leaves' undersides and shaded inner faces; the top view
  (`#C5252C`) and the f34 (`#B6262B`) see more top faces. That difference is light, not paint.
- **Painted base → tip gradient** on the unshadowed leaves: base `#A32229`–`#A9262F` → middle `#BE2930` → tip
  `#D9323A`–`#EA373F`. The bases are also darkened by the seed's and the neighbours' occlusion (`#75191E`).
- The lit facets reach `#F03A43`–`#F83D44`: light on the facets, never painted by facing.

**Rock.**
- Warm brown-grey, hue 15–19°, sat 0.27–0.35. Unshadowed median `#7C5E51` (exploded); view medians `#70594E`–`#775E52`
  (the leaves shade the ring's top). The ground band (lowest 20 % of each boulder) is darker, `#664F45`–`#715B4F`.
- The **dirt floor** inside the ring is darker and a touch redder than the boulders (`#634B41`), as is the underside
  (`#533D34`). Treat it as the shaded dirt key.
- No orange wash from the seed on the leaves or the rocks: the sheet shows none (the leaves near the seed are their
  darkest, not warmest).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered medians of **unshadowed** regions (exploded parts and breakdown), not swatches.
`K.sample` kinds: `"vivid"` for the seed and the leaves; `"brown"` for rock and dirt (check that the brown filter keeps
the lit rock pixels at sat 0.27–0.35; if not, use `M.sample(..., "stone")` as M015 did).

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m025_seed_hot` | `#FDA835` (hot medians `#FD9D2F`–`#FDA835`; breakdown `#FEA735`; exploded `#FDAE36`; f34 lit `#FDC23D`) | about 25 % of the seed's facets: the top fifth plus upper-half facets biased to +X/−Y (§5.5) | **emission ≥ 1.0 → Neon** |
| `m025_seed` | `#FC7425` (mid medians `#FD7124`–`#FD7925`; swatch `#FE7C2C`) | about 50 %: the belt and the rest of the upper half | **emission ≥ 1.0 → Neon** |
| `m025_seed_deep` | `#F24C18` (deep medians `#F44C18`–`#F74F1B`; bottom fifths `#EE3E15`–`#F74C1A`; mount close-up `#E64714`) | about 25 %: the lower cone and the nub | **emission ≥ 1.0 → Neon** (§7.1) |
| `m025_leaf` | `#BE2930` (breakdown `#BC2930`; exploded UR `#BC2830`; swatch `#C0242D`) | leaf middles (t 0.3–0.7) | rough 0.65, metal 0 |
| `m025_leaf_tip` | `#DC333B` (tip fifths `#D7333C`–`#EA373F`) | outer 30 % of each leaf | rough 0.65 |
| `m025_leaf_dark` | `#A02229` (base fifths `#A32229`–`#A9262F`; Leaf Shadow swatch `#8C1D23` as the dark end) | inner 30 %, the keel near the base, the faces within 0.4 of the seed | rough 0.7 |
| `m025_rock` | `#7A5D51` (exploded base `#7C5E51`; swatch `#795D54`; views `#70594E`–`#775E52`) | boulder bodies | rough 0.92 |
| `m025_rock_light` | `#957465` (deciles 8–9 `#946C5B`–`#9A7868`; breakdown lit `#9A796D`) | broad patches, about 25 % of the boulders, 2–4 facets each | rough 0.92 |
| `m025_rock_dark` | `#5E4A42` (ground bands `#664F45`–`#715B4F`; Rock Shadow swatch `#5B4C48`) | the lowest 20–25 % of each boulder by height; faces within 0.25 of a neighbour; pebbles | rough 0.92 |
| `m025_dirt` | `#634B41` (exploded and breakdown floor `#634B41`/`#634A41`; underside `#533D34`) | slab top and sides, the underside recess, the mount tube | rough 0.95 |

**Calibration warnings:**
- **Neon keys** render flat at their colour in Blender (emission ≥ 1.0) and in Roblox (Neon is unlit, one flat colour
  per piece, with bloom). Calibrate them by the parts-shot seed against `#FC7C27` (exploded median) and the f34_sheet
  seed median within 12 of `#FC7024`; the three keys must stay at least 30 levels apart in G (`#F24C18` / `#FC7425` /
  `#FDA835`) so the bands survive. If the hot key washes toward white, lower its value, never raise emission.
- **Leaves:** reds clip easily in R. Calibrate on the parts-shot leaf against `#BE2930`, then check the front_sheet leaf
  median within 15 of `#85191D` and the top median within 15 of `#C5252C` (the studio light should give most of the
  difference); add `leaf_dark` only where the front still reads too light.
- **Rock:** calibrate on the parts-shot base against `#7C5E51`; front_sheet rock median within 10 of `#70594E`.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Seed** (all Neon, so boundaries are whole facets; blend means a mixed facet band, not a gradient inside a face):
  field u = (z − z_bottom) / height + 0.20 × lateral toward (+X, −Y) / r + 0.12 × a per-facet noise:
  - u < 0.30 → `seed_deep`; 0.30–0.68 → `seed`; > 0.68 → `seed_hot`;
  - across each boundary, alternate facets of the adjacent ring between the two keys (a one-ring checker band), so the
    change reads as scattered facets like the sheet, not a horizontal stripe;
  - the nub → `seed_deep`;
  - shares to land: deep 20–33 %, mid 40–56 %, hot 22–32 % of the seed's pixels per view (§1.2). The facing correlation
    must stay below 0.5 (`K.check`): the lateral and noise terms matter (M012's height-only bands scored 0.65).
- **Leaves** (field = each leaf's along-length t from its construction frame): t < 0.3 `leaf_dark`; 0.3–0.7 `leaf`;
  > 0.7 `leaf_tip`; 3 steps, ±0.08 noise on t; faces within 0.4 of the seed's surface → +30 % `leaf_dark`
  (occlusion); the back pair shift 0.05 toward the tip (their tips are the crown's brightest in the rear view).
- **Rock:** body `rock`; broad noise patches (`K.patches` scale about 0.5, 2–4 facets each) → `rock_light` at level
  0.3; ground band (height above ground < 0.25 × the boulder's height) → 50 % `rock_dark`; contact faces within 0.25
  of a neighbour or the slab → 35 % `rock_dark`; crowns (top 30 %) 0 % dark. Pebbles `rock_dark` with 30 % `rock`.
- **Dirt:** slab and tube `dirt`; 20 % `rock_dark` patches near the boulders.
- **Hard edges only** where materials meet: seed | leaf, leaf | dirt, boulder | dirt. They are automatic (separate
  keys on separate faces).

### 5.6 Texture (Tint) and finish

- **Tint** (`tint_var` per piece about 0.04, so each leaf and boulder differs slightly):
  - leaves: `K.texture` amp 0.03, scale 0.5 (broad, per facet group);
  - rock and dirt: amp 0.06, scale 0.45;
  - seed: none (Neon keys ignore Tint in the export);
  - never per-triangle confetti.
- **Finish:**

| Material | Roughness | Specular | Metal | Notes |
| --- | --- | --- | --- | --- |
| Seed keys | 0.5 | low | 0 | Neon (emission ≥ 1.0) |
| Leaf keys | 0.65–0.7 | normal | 0 | crisp lit facets (the sheet's leaves have a slight sheen on the lit planes) |
| Rock, dirt keys | 0.92–0.95 | normal | 0 | matte |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Seed:** f34_sheet median within 12 of `#FC7024`; deep/mid/hot split per §5.5; **bright share ≥ 90 %** of seed
  pixels at v ≥ 0.9 in the front, side, rear and f34 (sheet 95–97 %), with VFX on and off.
- **Leaves:** parts-shot median within 12 of `#BE2930`; base → tip order on the parts-shot leaf (darker base, brighter
  tip); front_sheet median within 15 of `#85191D`.
- **Rock:** parts-shot base within 10 of `#7C5E51`; front_sheet within 10 of `#70594E`; ground band darker than crowns.
- **Shares** per §2.4 and §4 step 5.

## 6. Joins and contact

- **Leaves into the slab:** each leaf's base point and its first 0.3 L sink into the slab and the seed's foot region;
  no visible peg; neighbouring leaf bases overlap (no coplanar faces).
- **Seed into the leaf cluster:** the nub sits at z 0.95 inside the leaf bases (the mount tube is not in the hero); the
  lower cone touches or overlaps the leaf bases from z 1.0 to about 1.6; it must not float (the sheet's leaves hug its
  foot).
- **Boulders on the slab and the ground:** flat bottoms at z 0; overlap the slab by 0.2–0.4 and each other by
  0.1–0.2; floor-cut at z 0.
- Overlap everything; exact booleans (pitfall 10).

## 7. Lighting and VFX plan (modeller, stages 5 and 6)

**What the sheet shows:**
- The seed is self-lit in every view (§5.3): bright, saturated, no dark facets.
- The leaves and rocks show no orange spill.
- The separate "VFX Reference" panel adds (`z_vfx.png`, `vfxs.py`):
  - a **soft warm halo** round the seed's upper half: peak `#FECB97`–`#FEC382` just above the tip, fading to the paper
    (`#F0E9E1`) about 100 px out (about 0.6 H ≈ 3.3 studs at the model's scale), centred about 0.1 H above the tip;
  - **3–4 small yellow 4-point diamond crystals** floating above and beside the tip: one about 0.2 H above it, two at
    the tip's height about 0.14 W either side, one small dot lower left; each about 0.15 H tall × 0.08 W wide (about
    0.8 × 0.45 studs), colour `#FEE10E`–`#FED731` (lit `#FFE343`–`#FFDC5D`).
- No fire, smoke, sparks or dust.

### 7.1 Stage 5 (lighting)

- **Emissive (Neon) keys: `m025_seed_hot`, `m025_seed`, `m025_seed_deep`** at emission ≥ 1.0 (start at 1.2). Each exports
  as a Neon glow piece, one per key, with no collision. Check the export STATS line (3 glow pieces).
  - Why all three: the sheet's darkest seed facets are still at v ≥ 0.9 (`#EE4818`), so a lit, solid deep key would read
    as a dull lower half in Roblox's shade. M015 kept its `core_deep` solid because that core's lower facets went to
    `#9C2509` under the shells; this seed has no such shade.
  - Emission between 0 and 1 does nothing in Roblox except drop the Tint. Don't use it.
  - Leaves, rocks and dirt: emission 0.
- **Light:** one warm PointLight in the open, carried by the socket below (decision §8.8): colour `#FF8A2A`, brightness
  about 0.6, range 9, shadows true, no flicker or a slow one. Place it at about (0, −1.2, 6.0): above the seed's tip and
  a little in front, at least 0.6 from every surface (check by BVH). It must not tint the leaves orange: the
  front_sheet leaf and rock medians with VFX on stay within 10 of the VFX-off values.
- **Studio note (Requires Manual Validation):** the halo leans on the place's default Bloom. With Bloom off, the Neon
  seed still reads and the halo emitter carries the glow. Check that the three seed bands stay distinct under Neon's
  bloom.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **Recommended (decision §8.8):**
  1. **`crystal_halo` × 1** — the panel's halo. Socket inside the seed behind its upper centre, about (0, +0.3, 4.4),
     so the mesh hides the billboard's middle and the glow shows round the silhouette. Scale about 0.45 (size about
     5.5–6.3, a halo about 3 studs out). Colour override `["#FFD9A8", "#FF9A3C"]` through
     `emitters=[dict(KINDS["crystal_halo"]["emitters"][0], color=[...])]`.
  2. **`crystal_glow` × 1** — the light only (§7.1), at about (0, −1.2, 6.0), with
     `light={"color": "#FF8A2A", "brightness": 0.6, "range": 9, "flicker": False, "shadows": True}`.
  3. **`embers` × 1 with the `spark_diamond` texture** — the panel's "floating crystals". Socket in the open above
     the tip, about (0, 0, 6.1). Override the emitter: texture `spark_diamond`, colour `["#FFE34A", "#FECE16"]`, size
     `[0.8, 0.3]`, transparency `[0.1, 1.0]`, rate 1.5, lifetime `[1.8, 3.0]`, speed `[0.3, 0.8]`, spread 40, drag 0.6,
     acceleration `[0, 0.3, 0]`, shape about `[2.0, 0.6, 2.0]` (Roblox XYZ), light_emission 1.0. About 3–5 crystals
     alive at a time, drifting up beside and above the tip, as drawn.
- **Not added:** fire, smoke, dust, `heat_glow` (its flickering puffs and light read as fire; the sheet says "no
  fire"), `ore_glint` on the seed (the seed glows; it doesn't glint).
- **Harvest sockets** (`harvest_hit` / `harvest_deplete`): R08's Emberbloom had them; M015 and the later numbered
  models do not. Recommended none for now (decision §8.9).
- All sockets go on the hero only (the Pod part may carry a copy of the halo; decision §8.8). Render with `vfx=True`.
  If the preview stand-ins veil the model, render the compare set with them hidden plus one shot with them, and record
  that. The export STATS line must report 3 sockets and 3 glow pieces.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by `git grep -w` of the repo and a search of every sheet .blend, zstd-decompressed
(`m020_study/blendall.py`):
- **R08 kit:** `Emberbloom` (45 hits in `FlintbornWorldKit.blend`), `EmberbloomSeedpod`, `EmberbloomLeaf`,
  `EmberbloomBase`, `EmberbloomDepleted`, `EmberSeed`, `RedPetal`; keys `r08_ember`, `r08_petal_red`, `r08_rock`
  (`art/blender/scripts/kit/R08/emberbloom.py`, `art/roblox/kit/R08/manifest.json`).
- `EmberbloomSeed` occurs in the kit .blend only as a substring of `EmberbloomSeedpod`; avoid it anyway.
- **`src`:** the event node id `Emberbloom` (EventCatalog) — a game id, not a kit object.
- `M.mk` would silently rename a clash to `<name>M025`, so avoid all of these.

**Proposed names.** `EmberbloomNode`, `EmberbloomPod`, `EmberbloomPetal`, `EmberbloomRockBase` and the `m025_` prefix
occur nowhere in the repo or any sheet .blend.

| Object | Part | Why |
| --- | --- | --- |
| `EmberbloomNode` | hero | matches the event node id `Emberbloom`, as `BerryBushNode` / `FiberPlantNode` match theirs; R08 owns `Emberbloom` |
| `EmberbloomPod` | Seedpod (with its nub) | R08 owns `EmberbloomSeedpod` |
| `EmberbloomPetal` | Leaf (with its hexagonal peg) | R08 owns `EmberbloomLeaf` |
| `EmberbloomRockBase` | Base (slab, boulders, pebbles, mount tube) | R08 owns `EmberbloomBase` |

- Palette keys `m025_*` (§5.4). Collection `Kit/M025 Emberbloom`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **7.0 × 5.7 × 5.5** (recommended: 1.0 C, the seed at head height, knee-high boulders; an Epic
   event node that must read at a distance), or R08's 6.5 H (8.3 × 6.7 × 6.5), or 0.8 C (5.6 × 4.6 × 4.4).
2. **Leaves:** **6** (recommended: the exploded's "x6" and the front, side and rear views), or 5 (the top cell only).
3. **Seed profile:** **the hero's** (recommended: Ø 2.25 × 4.55, long pointed top, sitting down in the leaves), or the
   exploded's stubbier gem (W : H 0.62, about 3.7 tall), which would leave the seed's foot floating 0.8 above the
   slab or need a tall hidden post.
4. **Leaf layout:** **front pair low (37°), back pair upright (52°), sides 34–36°** (recommended: the front, f34 and
   side agree), or a symmetric 40° ring (matches the rear's far leaves, misses the front's leaf points by 0.1 h).
5. **Pegs and sockets:** **not modelled in the hero; no socket holes anywhere; the Petal part keeps its hexagonal peg
   and the RockBase part its mount tube** (recommended: hidden in every assembled view; holes add boolean risk), or no
   pegs at all.
6. **Underside:** **a shallow recess in the slab's bottom** (recommended: the sheet's "Base Underside" calls it out
   for terrain placement; built into the slab mesh, no boolean), or a flat bottom.
7. **Hero packaging:** **one closed shell** (recommended: STAGES default), base first, then leaves, then the seed, one
   piece at a time.
8. **Stage 5/6:** **three Neon seed keys + `crystal_halo` + `crystal_glow` (light) + `embers` with the spark_diamond
   texture** (recommended, §7), or the R08-style `heat_glow` + `embers` (reads as fire, which the sheet rules out).
   Halo on the Pod part too: recommended no (parts stay plain, as M015's).
9. **Harvest sockets:** **none for now** (recommended: consistent with M015's decision; gameplay sockets later in one
   pass), or R08's `harvest_hit` in red and orange.
10. **Exports:** the hero plus 3 parts (`…Pod`, `…Petal`, `…RockBase`) (recommended). R08's `EmberSeed` / `RedPetal`
    drops and `Depleted` state are not on this sheet; not built unless asked.
11. **Comparison cameras** (§3): `front_sheet (0, 8)`, `side_sheet (90, 8)`, `rear_sheet (180, 8)`, `f34_sheet (−20, 14)`,
    `r34_sheet (200, 14)` (probe the handedness of both first), kit top + `top_tilt (0, 70)`; kit front34, rear34 and
    underside as self-consistency; a parts shot `(−20, 25)`.
12. **Names** as proposed.

## 9. Pitfalls to avoid

1. **Soft or flat leaves.** The leaves are **thick crystal shards** (T ≈ 0.2 L) with sharp points at both ends and 4–6
   big facets on top — not flat cards, not balls, not tents, not tulip cups closed round the seed, not R08's thin
   lozenges. Measure W : L (0.38–0.46) and both end widths (< 0.15 L over the last 0.1 L) on the parts shot.
2. **A round or short seed.** The seed is an 8-sided diamond-faceted gem with a long point (top cone ≥ 2.0 tall, front
   width .16 W at z 4.85); not an icosphere, not an egg, not R08's "short smooth pod".
3. **A dull seed.** It must read as bright as the sheet: ≥ 90 % of its pixels at v ≥ 0.9, and its share of the
   silhouette within ±4 of §1.2. All three seed keys Neon; no solid lower half.
4. **One-colour seed.** The deep → mid → hot bands and the scattered hot facets are on the sheet (§5.3); keep each key
   distinct and the split near 25/50/25.
5. **Hidden boulders.** R08's last build hid the ring under its petals. The rock band must be ≥ 90 % of the front,
   side and rear at h .0–.2, rock about 29 % of every view including the top, the boulders visible between the leaf
   tips from above.
6. **Leaves cupped shut.** The crown is open: the seed shows from h .39 up in the front, with clear sky between the
   back leaves and the seed's flanks (the front profile dips to .65–.70 there).
7. **Colour by facing.** Lit and shade leaf facets and rock faces are light; paint along each leaf's length, by boulder
   height and by broad patches only; `K.check` facing correlation < 0.5. The seed's hot facets follow position plus
   noise, not normals.
8. **Orange spill.** The sheet shows none on the leaves or the rocks; keep the light small, above the tip, and check
   the medians with VFX on.
9. **Glow as geometry.** The halo and the floating crystals are VFX sockets, never mesh ("No baked glow, fire, or
   particles in geometry").
10. **Exact booleans.** Overlap everything: leaf bases 0.3 L into the slab, boulders 0.2–0.4 into the slab, no coplanar
    faces (boulder bottoms and the slab bottom both at z 0 — let the floor cut make them coplanar, never the union).
    Pre-unite the base; add pieces one at a time and save the work file between; remove slivers with m011's
    `_tidy` / `_desliver`.
11. **Comparing the wrong views.** The f34 and r34 are near-front and near-rear views from higher up; the top cell
    shows 5 leaves where the sheet builds 6; the rear draws the front leaves higher than the other views (§3).
12. **Side-view handedness.** The kit side camera at az 90 sits at +X, so screen right is the model's back; the
    sheet's tall side-view leaves at screen right are the back pair.
13. **Naming clashes** with R08's `Emberbloom*` (§8). Don't edit shared helpers (`kit_models.py`, `kit_mcp.py`,
    `build_kit.py`, `lib/vfx.py`); put new helpers in `m025.py`. No commits, pushes or exports in the modeller's stages.

## Decisions (main session, 2026-10-28)

All recommendations are accepted:
1. Size: 7.0 W × 5.7 D × 5.5 H.
2. Six leaves.
3. Seed shape: follow the hero's taller seed, sitting down in the leaves.
4. Leaf layout: front low, back upright.
5. No pegs or socket holes in the hero. The leaf part keeps its peg, and the base part keeps its seed mount.
6. Underside: a shallow recess built into the slab mesh, not a boolean.
7. One closed shell, built base first, then the leaves, then the seed. Add pieces one at a time.
8. Glow and effects:
   - Neon keys `m025_seed_deep` `#F24C18`, `m025_seed` `#FC7425` and `m025_seed_hot` `#FDA835`, each at emission ≥ 1.0 and one flat colour.
   - Sockets: `crystal_halo` inside the upper seed, `crystal_glow` (light only, `#FF8A2A`) above the tip, and `embers` with the `spark_diamond` texture in yellow.
   - No `heat_glow`, and no halo on the seed part.
9. No harvest sockets.
10. Hero plus 3 parts; no drops and no depleted state.
11. Comparison cameras: front (0,8), side (90,8), rear (180,8), f34 (−20,14), r34 (200,14), and the kit top plus `top_tilt (0,70)`. Check the left-right orientation of both three-quarter cameras with one test render first.
12. Names as proposed: `EmberbloomNode`, `EmberbloomPod`, `EmberbloomPetal`, `EmberbloomRockBase`.

Leaves are crystal shards with real points at both ends, never balls or tents. The boulder ring stays readable: the bottom 20 % of the front, side and rear views is at least 90 % rock.
