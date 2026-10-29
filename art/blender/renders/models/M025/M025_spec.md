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

## Stage 1 - Modelling (modeller, 2026-10-28)

Builder `art/blender/kit/mcp/m025.py` → `build()` (about 36 s with renders, 25 s without; fixed seeds, the same
result every run). Background session port 9880, work file `art/blender/assets/kit/wip/M025.blend`.

Camera handedness: `build_kit.frame_box` puts the camera at (sin az cos el, -cos az cos el, sin el), so the f34 camera
at az -20 sits front-left (the left side nearer, as the sheet's f34 draws it) and the r34 at az 200 sits back-left
(screen right = -X nearer). The side camera at az 90 sits at +X (screen right = the back).

**Parts, each from its own function:**
- `EmberbloomPod` (`_seed`): 8 sides and 9 rings, each turned half a step. Each ring edge is shared by one up and one
  down triangle, which together form one **diamond facet**: about five rows, four across.
  - Rings (height fraction, radius fraction): (0, .11) and (.03, .11) for the nub, then (.10, .45), (.25, .82),
    (.43, 1.0), (.60, .96), (.74, .78), (.86, .47), (.95, .18), and the tip.
  - Radius 1.0 (Ø 2.0). The study's Ø 2.25 put the seed share 5–7 points over the sheet in every view.
  - It runs from z 0.95 to 5.5. 144 tris.
  - The hero seed uses the same rings, but its lower cone runs on down into the slab (a ring at z 0.40, r 0.6), which
    hides the leaf hub.
- `EmberbloomPetal` (`_leaf`): the convex hull of these points:
  - a pointed outline: half-width / L of .062, .155, .21, .18 and .088 at .12, .30, .48, .65 and .84 of the length;
  - each outline point split into an upper and a lower edge (a side band of ±0.24 T), so the section is a flattened
    hexagon with a deep side face, like the exploded leaves;
  - a top ridge at .18, .45 and .68 L, raised .38, .6 and .4 T;
  - a keel at .25, .5 and .72 L, lowered .28, .4 and .26 T. T = 0.34 L.

  **Both ends are real points** (about 58° at the base and 55° at the tip, in plan). W : L is 0.42–0.45. The part
  adds its hexagonal peg along -X under the base. 100 tris.
- `EmberbloomRockBase` (`_slab`, `_boulders`, `_mount`). 866 tris.
  - A 14-sided slab: rx 2.45, ry 2.15, sloped sides, a raised faceted top up to z 0.52.
  - A **shallow faceted recess in the slab's underside**: rim at 0.62 R, apex 0.3 up. It is built into the slab mesh;
    no boolean.
  - Ten squat dome boulders (hull rocks with 4 rings, d 1.5–2.1, h 0.92–1.15) on an oval ring (rx 2.55, ry 2.2).
  - Three pebbles in front, and the seed's 8-sided mount post.

**Hero (`EmberbloomNode`):** 1438 tris, **6.97 W × 5.69 D × 5.50 H**. Built in this order:
1. Base, then the six leaves, then the seed, united one shell at a time by `_union_fine`: exact booleans, a 0.002
   post-merge, and a guard that undoes and retries (with a 0.004 nudge) any union that loses most of the mesh.
2. Floor cut at z 0 by `_floor_cut`: a triangle fill of all the cut loops together, so the recess stays open.
3. The m016 cleanup, the m023-style finish and polish, then `M.fix_bowties`.

**Leaf layout.** Each leaf: tip, roll and cross. The bases sit at r 0.35, z 0.42 (inside the slab), shifted `cross`
sideways.
- P1, right: tip (3.52, 0, 2.62), roll 38.
- P2, left: tip (-3.45, 0, 2.85), roll -38.
- P3, front right: tip (2.55, -2.9, 2.75), roll -48, cross -0.5. P4, front left, mirrors it.
- P5, back right: tip (2.0, 2.62, 3.65), roll 48, cross 0.5. P6, back left, mirrors it.

Decisions taken while matching the views:
- **Crossed, rolled leaves.** The study's flat tangential leaves read as needles in every elevation view (front leaves
  32–36 % against the sheet's 49 %). The sheet's front and rear cells show the front and back pairs **crossing in a V**
  in front of and behind the seed's foot, with their inner edges raised, cupping its lower half; the side leaves show
  broad faces. So:
  - the front and back pairs cross (±0.5) and roll 48°;
  - the side pair roll 38°;
  - the leaves are thicker (T 0.34 L).
- **Root points.** Each hero leaf's hull also takes one hidden root point inside the seed's foot (z 0.6, 0.12 out along
  its azimuth), so every leaf overlaps the seed and the union is one shell. Each root is its own: a root point shared
  by two leaves made the exact union drop the whole base.
- **Seed foot cone.** The seed's foot cone (r 0.6 at z 0.4) swallows the hub where the leaf roots meet the slab. With a
  thin post there, the union left 23 crossing sliver pairs at the hub.
- **Boulders.** Squatter and wider than the study (h/d 0.55–0.6), so the ring reads as one continuous low band.

**Measured against the sheet** with `m025.measure()`, using the study's masks on both images.
- Sheet cameras: front (0, 8), side (90, 8), rear (180, 8), f34 (-20, 14), r34 (200, 14), top (0, 89), top_tilt (0, 70).
- 3× lens; VFX off.

| View | Seed S (sheet / ours) | Leaves L | Rock R | Bottom 20 % rock | Top-profile error mean / max |
| --- | --- | --- | --- | --- | --- |
| Front | 22.0 / 22.9 | 48.6 / 46.6 | 29.4 / 30.5 | 96.6 % | 0.037 / 0.20 |
| F34 | 16.1 / 20.9 | 54.7 / 48.6 | 29.2 / 30.5 | 98.2 % | 0.088 / 0.27 |
| Side | 20.4 / 24.5 | 49.0 / 43.7 | 30.6 / 31.8 | 97.1 % | 0.063 / 0.30 |
| Rear | 17.9 / 16.9 | 50.8 / 53.3 | 31.3 / 29.8 | 93.6 % | 0.078 / 0.25 |
| R34 | 16.0 / 16.9 | 53.6 / 51.0 | 30.4 / 32.1 | 97.8 % | 0.064 / 0.22 |
| Top | 11.2 / 11.7 | 59.5 / 66.3 | 29.3 / 22.0 | - | 0.066 / 0.14 |
| Top tilt (70) | 11.2 / 13.1 | 59.5 / 63.4 | 29.3 / 23.5 | - | 0.102 / 0.22 |

- **Front, rear, r34:** within ±4 on every share.
- **Side and f34:** seed +4.1 and leaves -5.3 on the side; seed +4.8 and leaves -6.1 on the f34.
  - The sheet draws its f34 about 15 % wider (W : H 1.45 against our 1.10). Spec 3.1 says to judge the f34 by shares
    and leaf points.
  - The sheet's side view draws its near leaf broader than one lotus geometry can be from both the front and the side.
- **Top:** the sheet's top cell draws 5 leaves; we build 6 (decision 2). So the leaf share is 7 over and the rock 7–8
  under (tolerance ±6). The boulders show between every pair of leaf tips.
- **Front W : H:** 1.16 against the sheet's 1.27. The sheet's object is wider than 7.0 × 5.5 allows; the size decision
  governs.

## Stage 2 - Optimisation and cleanup

| Object | Tris | Size (studs) | Shells | Non-manifold edges / verts (bowties) | Boundary | Self-intersecting pairs | Smallest corner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EmberbloomNode (hero) | 1438 / 4000 | 6.97 × 5.69 × 5.50 | 1 | 0 / 0 | 0 | 0 | 5.01° |
| EmberbloomPod | 144 / 1000 | 2.04 × 2.02 × 4.57 | 1 | 0 / 0 | 0 | 0 | 8.65° |
| EmberbloomPetal | 100 / 1000 | 4.67 × 1.75 × 1.46 | 1 | 0 / 0 | 0 | 0 | 5.40° |
| EmberbloomRockBase | 866 / 1000 | 6.41 × 5.69 × 1.15 | 1 | 0 / 0 | 0 | 0 | 5.02° |

All four objects also pass these checks:
- no wire edges, loose verts, zero-area faces, n-gons or duplicate verts;
- normals outward; no inverted faces (volume positive, normals recalculated);
- origin at the bottom centre (offset 0, 0, 0); transforms applied;
- no modifiers, no custom normals, flat shading.

`build()` puts every one of these checks into its `problems` list, and the list is empty.

## Stage 3 - UV

`M.smart_uv` (angle 45, ANGLE_BASED re-unwrap, margin 0.008), then m012's overlap unfold:

| Object | Islands | Overlap pairs | Flipped | Min gap | Border | Density min / med / max | Conformal stretch p95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Hero | 246 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.022 |
| Pod | 25 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.029 |
| Petal | 24 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.049 |
| RockBase | 148 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.024 |

## Stage 4 - Materials, colour and texture

**Keys** (`PALETTE`, calibrated hexes; the targets are in `TARGETS`):

| Key | Hex | Target (sheet) | Finish |
| --- | --- | --- | --- |
| m025_seed_deep | #F24C18 | deep medians #F44C18–#F74F1B | Neon, emission 1.0, rough 0.5 |
| m025_seed | #FC7425 | mid medians #FD7124–#FD7925 | Neon, emission 1.0 |
| m025_seed_hot | #FDA835 | hot medians #FD9D2F–#FDA835 | Neon, emission 1.0 |
| m025_leaf | #8F0E18 | #BE2930 (unshadowed), #85191D (front) | rough 0.65 |
| m025_leaf_tip | #A31722 | #DC333B | rough 0.65 |
| m025_leaf_dark | #78020B | #A02229 | rough 0.7 |
| m025_rock | #69524B | #7C5E51 / front #70594E | rough 0.92 |
| m025_rock_light | #7E675E | #957465 | rough 0.92 |
| m025_rock_dark | #4F403C | #5E4A42 | rough 0.92 |
| m025_dirt | #55413B | #634B41 | rough 0.95 |

**Pass 1** (`calibrate()`, on the kit's test dome):

| Key | Result | Dome render against target |
| --- | --- | --- |
| leaf | #981520 | 191,46,51 against #BE2930 |
| leaf_tip | #AE202C | |
| leaf_dark | #800310 | |
| rock | #624D46 | 123,94,82 against #7C5E51 |
| rock_light | #766058 | |
| dirt | #4F3D37 | |
| rock_dark | #4A3C38 | its last dome sample fell out of the brown mask; the rock key's own gain gives the same value |

**Pass 2** (the hero's seven sheet views against the sheet's medians, using linear-light geometric-mean gains):
- leaves × (0.87, 0.60, 0.62): the elevation views were 15–25 levels light and less saturated, and the f34 and top
  11–13 dark;
- rock and dirt × 1.15.

**Re-measured** (VFX off; sheet / ours):

| View | Leaves | Rock |
| --- | --- | --- |
| Front | #85191D / #941D21 | #70594E / #72594F |
| Side | #8B1A1E / #7E1F20 | #765C52 / #5C4842 |
| Rear | #7F1A1F / #8D1F23 | #775E52 / #67514A |
| R34 | #81191E / #912226 | – |
| F34 | #B6262B / #9F2226 | #674F46 / #7A5F53 |
| Top | #C5252C / #AE2D32 | #645049 / #6D564D |

- Seed, f34: #FC7024 / #FF741E, within 12.
- The leaf medians straddle the sheet's by ±13–21. The sheet lights its leaf tops harder and shades them harder than
  the studio: its lit quartile is #E9353F–#F83D44, against our #D83B3E. Paint can't copy that, because colour may never
  follow facing.

**Blending, by position only:**
- **Seed.** Each whole diamond takes one Neon key from u = height fraction + 0.04 × lateral toward (+X, -Y) + 0.10 ×
  broad noise ± 0.18 at random per diamond. Deep below 0.53, hot above 0.77. There are no mixes between Neon keys (a mix
  would not be Neon).

  Seed bands per view (deep / mid / hot; the sheet is about 26 / 50 / 24):

  | Front | F34 | Side | Rear | R34 |
  | --- | --- | --- | --- | --- |
  | 32 / 51 / 17 | 22 / 58 / 20 | 35 / 37 / 29 | 15 / 58 / 27 | 19 / 55 / 26 |

- **Leaves.** Along each leaf's own length t: dark base → leaf → bright tip, over 9 keys (25 / 50 / 75 % mixes), with
  ±0.08 noise.
  - Faces within 0.45 of the seed are two steps darker (occlusion).
  - The back pair shift 0.05 toward the tip.
- **Rock.**
  - Broad noise patches go up to 75 % toward rock_light.
  - The ground band (under half of each boulder's height, ramped) goes up to 50 % toward rock_dark.
  - Faces within 0.25 of a neighbouring rock are at least 35 % dark.
  - Pebbles are 50–75 % dark.
- **Dirt.** Plain, with 25 % toward rock_dark on noise patches near the boulders. The floor-cut cap is plain rock.

**Tint:**
- per piece ±3 %;
- broad mottling: leaves amp 0.03, scale 0.5; rock and dirt amp 0.06, scale 0.45;
- seed faces exactly Tint 1.0 (checked 1.0–1.0 on the hero and the Pod).

**`K.check`:** baked shading 0.24 on the hero (limit 0.5) and 0 on the parts. The plain dirt cap first gave 0.54 for the
dirt family, so the cap is now the rock key.

## Stage 5 - Lighting

- **Neon seed.** The three seed keys are Neon: emission 1.0, `flintkit_spec` [0.5, 0, 1.0]. In Blender, `_glow_mats`
  previews them unlit, as Roblox shows Neon. The export should give 3 glow pieces.
- **Seed bright share** (v ≥ 0.9): 99.5–99.9 % in every view. The sheet's is 95–97 % (87 % on the top).
- **Glow share** (the seed's share of the silhouette):

  | | Front | F34 | Side | Rear | R34 | Top |
  | --- | --- | --- | --- | --- | --- | --- |
  | Sheet | 22.0 | 16.1 | 20.4 | 17.9 | 16.0 | 11.2 |
  | Ours | 22.9 | 20.9 | 24.5 | 16.9 | 16.9 | 11.7 |

- **Light.** `crystal_glow` at build (0, -1.2, 6.0), 1.26 clear of the mesh: #FF8A2A, brightness 0.6, range 9, shadows
  on, no flicker. With the light on, the front leaf median moves from #941D21 to #961D21 and the rock doesn't move: no
  orange spill.
- **Studio (Requires Manual Validation):** the halo leans on the place's default Bloom. Check that the three seed bands
  stay distinct under Neon bloom.

## Stage 6 - VFX

| Socket | Kind and settings | Build point | Roblox XYZ (hero-local) | Clearance | Inside the mesh | Spawn points inside |
| --- | --- | --- | --- | --- | --- | --- |
| VFX_EmberbloomNode_crystal_glow_1 | crystal_glow, light only | (0, -1.2, 6.0) | (-0.03, 6.0, 1.01) | 1.26 | no | – |
| VFX_EmberbloomNode_crystal_halo_1 | crystal_halo, scale 0.45, #FFD9A8 → #FF9A3C | (0, 0.3, 4.4) | (-0.03, 4.4, -0.49) | 0.34 | yes, by design | – |
| VFX_EmberbloomNode_embers_1 | embers with `spark_diamond`, #FFE34A → #FECE16, size 0.8 → 0.3, rate 1.5, shape 2.0 × 0.6 × 2.0 | (0, 0, 6.2) | (-0.03, 6.2, -0.19) | 0.70 | no | 0 of 125 |

- `fx_check()` (m015's ray-parity test) checks these inside `build()`.
- Renders use `vfx=True`. The halo's preview stand-in shows only in `vfx_halo.png` (m014's practice): its blobs veil
  the model, where a Roblox billboard inside the seed would not.
- No fire, smoke, dust, heat_glow or harvest sockets (decisions 8 and 9).

## Modeller's notes for the verifier

- **Renders** are in `art/blender/renders/models/M025/`:
  - the contact sheet `M025_views.png`;
  - the sheet shots `*_sheet.png` and `top_tilt.png`;
  - `vfx_halo.png`, `exploded.png`, and `part_pod.png`, `part_petal.png`, `part_rockbase.png`.
- **Re-measure** with `m025.measure()` after `m025.preview(vfx=False)`. For the side-by-side crops I compared the sheet
  cell's bounding box against our render's.
- **Known differences, judged and left:**
  - f34 and side leaf shares 5–6 points under: the sheet draws its f34 wider and its near side leaf broader;
  - top rock share 7 under: 6 leaves against the top cell's 5;
  - seed Ø 2.0, not the study's 2.25, to keep the seed shares in line;
  - the Petal part is 3.85 long to its base point, plus the peg. The hero leaves run 3.7–3.95, their inner ends buried;
  - leaf medians straddle the sheet by ±13–21 (lighting contrast);
  - rear view seed deep share 15 % against 29 %: the back leaves cup the seed's lower, deep facets.
- **Hidden parts.** The leaf hub, the seed foot and the leaf roots are hidden inside the seed's foot cone and the slab.
  The underside shows the recess and the boulders' flat bottoms (`underside.png`).
- **Clean build.** `build()` returns an empty `problems` list and an empty `log.union_retries` (the union guard did not
  fire).

## Stage 7 — Verification (round 1)

Independent verifier, 2026-10-28. Read-only: background session on port 9881 with
`art/blender/assets/kit/wip/M025_verify.blend` (not saved; `build()` not called). Fresh renders went to a scratch
folder (`M.MODEL_RENDERS` redirected), so `art/blender/renders/models/M025/` was not touched. Everything below was
re-measured; nothing was taken from the stage sections.

**Verdict: FAIL, 6.5 / 10.** The technical side is clean. Two things read clearly unlike the sheet: the seed's visible
shape (a slim flame tongue instead of a plump gem cupped by the leaves), and the leaf red (dull crimson instead of the
sheet's saturated red).

### Technical checks (all pass)

| Object | Tris | Size (studs) | Shells | NM edges / verts | Boundary / wire / loose | Zero-area / n-gons | Self-intersecting pairs (BVH, m016) | Inverted faces (ray parity) | Min corner | Volume |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EmberbloomNode | 1438 / 4000 | 6.973 × 5.687 × 5.500 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 / 0 | 0 | 5.01° | +44.29 |
| EmberbloomPod | 144 / 1000 | 2.038 × 2.018 × 4.570 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 / 0 | 0 | 8.65° | +7.09 |
| EmberbloomPetal | 100 / 1000 | 4.674 × 1.751 × 1.456 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 / 0 | 0 | 5.40° | +3.52 |
| EmberbloomRockBase | 866 / 1000 | 6.406 × 5.687 × 1.150 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 / 0 | 0 | 5.02° | +16.35 |

- **Size:** 6.97 × 5.69 × 5.50 against the decided 7.0 × 5.7 × 5.5 (±0.35 / ±0.4 / ±0.25). Pass.
- **Other checks:** no duplicate verts and no interior faces (every face's outward ray hits an even number of
  surfaces). Origin at the bbox bottom centre (offset 0, 0, 0). Rotation 0, scale 1, no modifiers, no custom normals,
  all faces flat. `K.check` returns no problems.
- **UV:** one `UVMap` each, with 0 overlaps, 0 flipped, min gap 0.016, border 0.008 and density 1.0 / 1.0 / 1.0.
  Conformal stretch p95 is 1.022 (hero), 1.029 (pod), 1.049 (petal) and 1.024 (base).
- **Neon:** `FB_m025_seed_deep` `#F24C18`, `FB_m025_seed` `#FC7425` and `FB_m025_seed_hot` `#FDA835`. Each has
  `flintkit_spec` emission 1.0 and an unshaded node set (BSDF and output only, no Tint mix). Each is one flat colour.
  The seed's Tint is exactly 1.0 on every corner of the hero and the pod.
- **Solid keys:** emission 0, and Tint 0.909–1.057 on the other faces (a broad range).
- **Paint fields:** leaves follow t along each leaf, and rocks follow boulder height and patches. Nothing is
  coloured by facing (`K.check` baked shading is under its limit).
- **Sockets** (`fx_check`, run by me): 3 in all, the kinds and places that decision 8 set.

  | Socket | Build point | Clearance | Inside | Spawn points inside |
  | --- | --- | --- | --- | --- |
  | `crystal_glow` (light only: `#FF8A2A`, 0.6, range 9, shadows, no flicker) | (0, −1.2, 6.0) | 1.26 | no | – |
  | `crystal_halo` (vfx_scale 0.45, `#FFD9A8` → `#FF9A3C`) | (0, 0.3, 4.4) | 0.34 | yes (by design) | – |
  | `embers` (`spark_diamond`, `#FFE34A` → `#FECE16`, 2.0 × 0.6 × 2.0 box) | (0, 0, 6.2) | 0.70 | no | 0 / 125 |

  The parts carry no sockets.
- **No light spill.** With VFX on against off, the leaf median moves by at most 2 levels in any elevation view and the
  rock median does not move.

### Views against the sheet (VFX off, sheet cameras, the study's masks on both images)

| View | Seed S (sheet / ours) | Leaves L | Rock R | Seed bright ≥ 0.9 | Bottom 20 % rock | Seed deep / mid / hot (sheet → ours) | Top-profile error mean / max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front | 22.0 / 22.9 | 48.6 / 46.6 | 29.4 / 30.5 | 95.7 / 99.8 | 95.8 / 96.6 | 26/52/23 → 32/51/17 | 0.037 / 0.20 |
| F34 | 16.1 / **20.9** | 54.7 / **48.6** | 29.2 / 30.5 | 97.4 / 99.5 | 97.4 / 98.2 | 26/50/25 → 22/58/20 | 0.088 / 0.27 |
| Side | 20.4 / **24.5** | 49.0 / **43.7** | 30.6 / 31.8 | 95.9 / 99.9 | 96.7 / 97.1 | 28/48/24 → 35/**37**/29 | 0.065 / 0.30 |
| Rear | 17.9 / 16.9 | 50.8 / 53.3 | 31.3 / 29.8 | 95.5 / 99.7 | 98.8 / 93.6 | 29/48/23 → **15**/58/27 | 0.078 / 0.25 |
| R34 | 16.0 / 16.9 | 53.6 / 51.0 | 30.4 / 32.1 | 96.9 / 99.6 | 99.3 / 97.8 | 33/39/27 → **19**/**55**/26 | 0.064 / 0.22 |
| Top | 11.2 / 11.7 | 59.5 / **66.3** | 29.3 / **22.0** | 87.2 / 98.7 | – | 20/48/32 → **6**/44/**50** | 0.066 / 0.14 |

- Bold marks values outside the spec's tolerance: shares ±4 (top ±6), seed bands ±8.
- W : H is 1.16 against 1.27 (front), 1.10 against 1.45 (f34), 0.97 against 1.04 (side) and 1.17 against 1.20 (rear).
- Six leaves show in every view. The seed is the only thing above h .73 in the front, side and rear.
- The boulder ring reads as an unbroken low band in every elevation view, and boulders show between all six leaf tips
  from the top.

**Seed visible shape** (seed mask; widths as a fraction of the silhouette W):

| View | Seed visible from h (sheet / ours) | Visible seed W : H | Max width | Seed px in the bottom 25 % |
| --- | --- | --- | --- | --- |
| Front | .39 / .23 | 0.66 / 0.42 | .32 / .28 | 0 / 47 |
| F34 | .48 / .31 | 0.80 / 0.46 | .27 / .29 | 0 / 0 |
| Side | .48 / .17 | 0.74 / 0.37 | .37 / .32 | 0 / 125 |
| Rear | .50 / .16 | 0.79 / 0.37 | .33 / .27 | 0 / 54 |
| R34 | .52 / .18 | 0.81 / 0.38 | .29 / .29 | 0 / 98 |

Above the widest point, the profiles agree within 0.03 (front, from the widest point to the tip: sheet .30 .29 .25
.17 .10 .01; ours .28 .27 .23 .18 .10 .01). The difference is below it:
- **On the sheet,** the leaves hide everything below the seed's widest ring, so the visible seed is a plump gem sitting
  in the leaf cup.
- **In our model,** the front and back pairs leave a V open down to the rock band, so the seed's long lower cone shows
  as a tapering flame tongue.
- **Orange specks at ground level.** The hero has 71 seed faces with centres below z 1.6, down to z 0.51 at r 0.54.
  Most are slivers of 0.002–0.06 stud² between the leaf bases and the slab, left by the seed foot cone (`SEED_POST_R`
  0.6 at z 0.40). They show as orange specks just above the boulders in the side, rear and r34 views. The sheet has
  none.

### Colour (sheet → ours, with the per-channel difference)

| Region | Sheet | Ours | Δ R, G, B |
| --- | --- | --- | --- |
| Seed deep (front shade quartile) | `#F65117` | `#FF4711` | +9, −10, −6 |
| Seed mid (front median) | `#FC7926` | `#FF741E` | +3, −5, −8 |
| Seed hot (front lit quartile) | `#FDA736` | `#FFB02E` | +2, +9, −8 |
| Seed f34 median / lit / shade | `#FC7024` / `#FDC23D` / `#F64F1A` | `#FF741E` / `#FFB02E` / `#FF4711` | +3,+4,−6 / +2,−18,−15 / +9,−8,−9 |
| Seed, exploded median | `#FC7C27` | `#FF731D` | +3, −9, −10 |
| Leaf, parts shot / breakdown median | `#BC2930` | `#AA2F30` | **−18**, +6, 0 |
| Leaf, exploded median / lit | `#C02931` / `#F03A43` | `#A32E2F` / `#CC3C3F` | **−29**, +5, −2 / **−36**, +2, −4 |
| Leaf, front median / lit | `#85191D` / `#E9353F` | `#941D21` / `#D53B3E` | +15, +4, +4 / −20, +6, −1 |
| Leaf, f34 median / lit | `#B6262B` / `#F83D44` | `#9F2226` / `#D73F41` | **−23**, −4, −5 / **−33**, +2, −3 |
| Leaf, side lit | `#DB323A` | `#AE3A3E` | **−45**, +8, +4 |
| Leaf, rear lit / r34 lit | `#D42F37` / `#E2353D` | `#A72E32` / `#B03337` | **−45**, −1, −5 / **−50**, −2, −6 |
| Leaf, top median / lit | `#C5252C` / `#F1343C` | `#AE2D32` / `#D34044` | **−23**, +8, +6 / **−30**, +12, +8 |
| Rock, front median | `#70594E` | `#72594F` | +2, 0, +1 |
| Rock, exploded / parts shot | `#7C5E51` | `#785E53` / `#7B6054` | −4, 0, +2 / −1, +2, +3 |
| Rock, side / rear median | `#765C52` / `#775E52` | `#5C4842` / `#67514A` | −26, −20, −16 / −16, −13, −8 |
| Rock, f34 / top median | `#674F46` / `#645049` | `#7A5F53` / `#6D564D` | +19, +16, +13 / +9, +6, +4 |
| Rock lit quartile (front / rear) | `#9F7B6C` / `#A98574` | `#8B6C5E` / `#7C6359` | −20, −15, −14 / −45, −34, −27 |
| Dirt floor (exploded, lit floor) | `#7C5C4F`–`#815E50` | `#725A51`–`#745C52` | about −9, −3, +2 |

- **Seed:** within about 10 of the sheet on every band (the f34's hottest facets are 18 less yellow). The three keys
  stay distinct.
- **Rock and dirt:** match where they are unshadowed (front, exploded, parts). The side and rear medians are the studio
  shade.
- **Leaves:** the medians straddle the sheet, but the lit faces are 20–50 levels darker in R and less saturated
  (sat 0.67–0.72 against 0.76–0.78) in every view. The unshadowed parts-shot median misses the spec's own target
  (within 12 of `#BE2930`) by 18. The leaves read as dull crimson; the sheet's are a bright, saturated red ("Leaf
  (Primary): Saturated red").

### Findings

**Blockers**

1. **B1. The seed reads as a slim flame tongue, not the sheet's plump gem in a leaf cup.**
   - **Evidence.** The visible seed's W : H is 0.37–0.46 against the sheet's 0.66–0.81, and it shows from h .16–.31
     against .39–.52. Its max width is 0.27–0.32 W against 0.32–0.37. Orange seed-foot slivers show at ground level
     in four views (47–125 px in the bottom 25 %; sheet 0).
   - **Knock-on effects.** The seed is over in the f34 and side (+4.8 and +4.1), and the leaves are under (−6.1 and
     −5.3).
   - **Fix,** in `m025.py`:
     - **(a) Seed body.** Widen to `SEED["r"]` 1.1 (Ø 2.2) and make the shoulders rounder below the widest ring,
       for example `SEED_RINGS` (0.25, 0.90) and (0.43, 1.0), so the part reads as the sheet's gem (aim for pod W : H
       0.50 or more).
     - **(b) Leaf cup.** Close the leaf cup over the seed's lower half: the front pair (P3/P4) and back pair (P5/P6)
       should cross in front of and behind the seed at h ≈ .38–.42, not open a V to the rocks. Reduce their `cross`
       (±0.5 → about ±0.2) and/or raise their inner edges (more roll, or root points higher on the seed). Check on
       front_sheet that the seed's lowest visible pixel is at h .36–.44, and that its visible W : H is 0.60 or more in
       the front, side and rear.
     - **(c) Seed foot.** Shrink the foot cone so no seed face is exposed near the ground: `SEED_POST_R` 0.6 → 0.3 or
       less, or keep the post wholly inside the slab and leaf hub. Accept when no seed-material face has its centre
       below z 1.4 outside the leaf bases, and every view has 0 seed pixels in its bottom 25 %.
     - **Check:** re-measure the seed share against §1.2 (±4); the wider seed and the closed cup roughly cancel.
2. **B2. The leaf red is dull crimson where the sheet's is a bright, saturated red.**
   - **Evidence.** The parts-shot median is `#AA2F30` against `#BC2930` (−18; the spec allows 12). The exploded median
     is `#A32E2F` against `#C02931` (−29). The lit quartile is 20–50 under in R in every view, with saturation 0.67–0.72
     against 0.76–0.78.
   - **Cause.** Pass 2's leaf gain × (0.87, 0.60, 0.62), plus the white specular sheen on the lit facets.
   - **Fix:**
     - Set the leaf keys from the pass 1 dome calibration again (`#981520` / `#AE202C` / `#800310`), or nudge from
       there.
     - Turn the leaf keys' specular down (`low_spec=True` in `PALETTE`) so the lit facets stay saturated.
     - Recheck the parts-shot leaf median within 12 of `#BE2930`, its lit quartile at `#E0353D` or above, and
       saturation 0.75 or more.
     - Accept the elevation medians running up to about 20 lighter than the sheet's. That is the sheet's harder
       shade, and the plan's own rule says lighting is not paint.
     - Keep the base → tip ramp (dark → leaf → tip).

**Minors** (fix if cheap; otherwise record)

3. **Seed band split.** These views fall outside ±8:
   - side mid 37 against 48;
   - rear deep 15 against 29;
   - r34 deep 19 against 33, and mid 55 against 39;
   - top: hot 50 against 32, and deep 6 against 20 (the whole tip cone is hot from above).

   The f34's hot facets sit centre-left; the sheet puts them upper right. Fix in `SEED_COL`: lower `hot` toward 0.80
   on the tip ring only, with mid facets mixed in, so the top view is mostly mid with hot on one side. Raise `lat` (0.04
   → about 0.12) so hot leans to +X / −Y and deep shows round the back's lower belt. B1(b) will also change the rear and
   side splits.
4. **Top view rock share** 22.0 against 29.3 (tolerance ±6) and leaves 66 against 60. This was expected from 6 leaves
   against the top cell's 5 (decision 2). Narrowing the leaves a little (`LEAF_W` 0.95) would help, but it is optional.
5. **Front W : H** 1.16 against 1.27, and f34 1.10 against 1.45. The size decision governs; record it.
6. **Rock contrast.** The lit quartiles are 20–45 under the sheet's (`rock_light` patches are subtle), and the side
   and rear medians sit in the studio shade (−16 to −26). The unshadowed medians match. Optionally, lift `rock_light`
   about 8 % and let its patches reach the crowns more often.
7. **Seed slivers.** The seed foot is split into many tiny faces (71 faces below z 1.6, most under 0.02 stud²). They
   waste tris but break no check. B1(c) removes most of them.
8. **Petal part length.** The part is 4.67 long including the peg (the study planned L 3.5 plus the peg); the modeller
   recorded this. Its W : L and both points are fine.
9. **Pod part.** W : H 0.45 against the exploded 0.62 and breakdown 0.69. This follows decision 3 (the hero's taller
   seed), but at Ø 2.0 it is narrower than the decided Ø 2.25. B1(a) brings it closer.

**Passes worth keeping as they are:**
- the six thick shard leaves, pointed at both ends, in a lotus layout (front pair low, back pair upright);
- the boulder ring (bottom 20 %: 94–98 % rock);
- the underside recess;
- the three Neon keys at their decided hexes, with the seed at 99.5 % or more bright;
- the three sockets, correctly placed, with no light spill;
- clean topology, UVs, origin and transforms.

## Round 2 fixes (modeller)

Fresh modeller, 2026-10-28. Background session on port 9881 with `art/blender/assets/kit/wip/M025.blend` (saved after
the final build). All changes are in `art/blender/kit/mcp/m025.py`; no shared helper was touched. `build()` takes about
40 s with renders (fixed seeds), and returns an empty `problems` list and an empty `union_retries` list.

### B1. Seed shape: fixed

- **(a) Seed body.** `SEED["r"]` 1.0 → **1.15** (Ø 2.3), with rings (0.25, **0.90**) and (0.43, 1.0). The verifier's
  r 1.1 gave a visible W : H of 0.58–0.59, under the 0.60 target, so I went one step further. The Pod part is now
  2.34 × 2.32 × 4.57 (**W : H 0.51**, was 0.45).
- **(b) Leaf cup.** I first tried reducing the front pair's `cross` to ±0.2. That made the V *lower*: in the front
  view the seed showed from h .23, with 175 px in the bottom 25 %. The V's bottom is where the two leaves' raised
  inner edges cross, so a *larger* cross lifts it. I swept cross ±0.9 / ±1.3 / ±1.6, roll 48–62, and raised bases.
  - **P3 / P4 cross ±1.6** (roll ±48 kept). Each base sits past the mid-line, in front of the seed's foot, and the
    inner edges meet at h .43.
  - **P1, the near leaf in the side view:** tip (3.52, 0, 3.25) (was z 2.62), roll 20 (was 38), width ×1.15
    (`LEAF_WS`). It now covers the seed's foot in the side view, the way the sheet's side cell draws its near leaves.
  - **Not kept:**
    - Raising every leaf base to z 0.9–1.3 bared the seed's lower cone between the boulders (270–800 px in the
      bottom 25 %).
    - `LEAF_W` 0.9, for the top cell's rock share, cost 2–4 points of leaf in every elevation view, made 4
      self-intersecting pairs, and gained only 3 points on the top.
  - The back pair are unchanged (±0.5). With the wider seed they already close the rear and r34 cups.
- **(c) Seed foot.** `SEED_POST_R` 0.6 → **0.3**.
  - The hero seed's diamonds centred below z 1.5 (`SEED_FOOT_Z`) take the **dirt** key. There are 16 of them, all
    hidden in the cup. The sheet's Seedpod Mount close-up shows the seed sitting on a dirt-coloured peg. At z 1.2, one
    orange speck still showed under P1 in the side view.
  - The Pod part stays all Neon.
  - The hero has **0 seed-key faces with a centre below z 1.4**; the lowest is at 1.73. Round 1 had 71 faces, down to
    z 0.51.
- **Petal part.** It now has its own length, `PETAL_L` 3.9, because the crossed hero P3 runs 4.5 to its buried base.
  With its peg the part is 4.33 × 1.61 × 1.34 (was 4.67; minor 8).

**Seed visible shape.** VFX off, sheet cameras, measured the verifier's way:
- "visible from": the lowest row with at least 3 seed px;
- W : H: the widest seed row over the visible height;
- the seed px in the bottom 25 %.

| View | Seed visible from h (sheet / round 1 / now) | Visible W : H (sheet / r1 / now) | Max width (sheet / r1 / now) | Bottom 25 % seed px (sheet / r1 / now) |
| --- | --- | --- | --- | --- |
| Front | .39 / .23 / **.433** | 0.66 / 0.42 / **0.65** | .32 / .28 / .32 | 0 / 47 / **0** |
| F34 | .48 / .31 / **.433** | 0.80 / 0.46 / **0.64** | .27 / .29 / .33 | 0 / 0 / **0** |
| Side | .48 / .17 / **.431** | 0.74 / 0.37 / **0.64** | .37 / .32 / .37 | 0 / 125 / **0** |
| Rear | .50 / .16 / **.403** | 0.79 / 0.37 / **0.63** | .33 / .27 / .32 | 0 / 54 / **0** |
| R34 | .52 / .18 / **.457** | 0.81 / 0.38 / **0.70** | .29 / .29 / .36 | 0 / 98 / **0** |

### Shares, bands and checks per view (sheet / ours; VFX off)

| View | Seed S | Leaves L | Rock R | Bottom 20 % rock | Seed deep / mid / hot (sheet → ours) | W : H | Top-profile error mean / max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front | 22.0 / 21.6 | 48.6 / 49.8 | 29.4 / 28.6 | 92.9 % | 25/51/22 → 24/50/24 | 1.27 / 1.16 | 0.039 / 0.17 |
| F34 | 16.1 / **21.7** | 54.7 / 50.8 | 29.2 / 27.4 | 95.3 % | 25/49/24 → 20/49/30 | 1.45 / 1.09 | 0.076 / 0.19 |
| Side | 20.4 / 21.9 | 49.0 / 48.0 | 30.6 / 30.1 | 97.5 % | 28/47/24 → **48/30/21** | 1.04 / 0.97 | 0.057 / 0.18 |
| Rear | 17.9 / 18.4 | 50.8 / 51.5 | 31.3 / 30.1 | 94.4 % | 29/48/22 → 24/54/20 | 1.20 / 1.17 | 0.071 / 0.12 |
| R34 | 16.0 / 18.7 | 53.6 / 49.9 | 30.4 / 31.4 | 98.2 % | 33/39/27 → 27/48/24 | 1.29 / 1.05 | 0.069 / 0.22 |
| Top | 11.2 / 15.0 | 59.5 / **66.2** | 29.3 / **18.7** | – | 19/48/32 → 18/37/43 | 1.13 / 1.24 | 0.064 / 0.12 |
| Top tilt | 11.2 / 16.4 | 59.5 / 62.9 | 29.3 / 20.7 | – | 19/48/32 → 19/41/38 | 1.13 / 1.11 | 0.094 / 0.22 |

- **Seed share:**
  - Within ±4 in the front, side, rear and r34; the side went from +4.1 to +1.5. The top is +3.8 (tolerance ±6).
  - **F34 is +5.6** (round 1 +4.8). The sheet draws its f34 33 % wider (W : H 1.45 against 1.09), which shrinks every
    share except the leaves'.
- **Top rock share: 18.7 against 29.3** (round 1 22.0).
  - Causes: six leaves against the top cell's five (decision 2), the broader P1, and the crossed front pair. From
    straight above, that crossing reads as an X.
  - Narrowing the leaves did not pay (see B1b).
- The seed is the only thing above h .73 in the front, side and rear. Six leaves show in every view, and the boulder
  ring stays an unbroken low band.

### B2. Leaf red: partly fixed

- Pass 2's leaf gain is dropped, and the three leaf keys are `low_spec=True` (Specular IOR level 0.06 on the keys and
  all their mixes).
- With low specular, the first-pass hexes (`#981520` / `#AE202C` / `#800310`) rendered dark and over-saturated: part
  shot `#AC1018`, saturation 0.91.
- So I re-ran the dome calibration with low_spec: leaf `#9A252F`, tip `#B02F3A`, dark `#831C28`. The dome renders
  were 191,40,48 / 221,51,60 / 160,31,41 against the targets.
- Then leaf ×1.03 and tip ×1.05. **Final: leaf `#9F2731`, leaf_tip `#B8323D`, leaf_dark `#831C28`.**
- Also tried: ×1.07 / ×1.15 with a darker base. That pushed the front median to +53 and read pink.

| Region | Sheet | Round 1 | Now | Target |
| --- | --- | --- | --- | --- |
| Parts shot (Leaf cell) median | `#BC2931` | `#AA2F30` | **`#B0252E`** (−12, −4, −3) | within 12 of `#BE2930`: met (just) |
| Parts shot lit quartile | `#E9373F` | – | `#C62B33` | ≥ `#E0353D`: **not met** |
| Parts shot saturation (median / lit) | 0.78 / 0.76 | 0.72 | **0.79 / 0.78** | ≥ 0.75: met |
| Exploded median / lit | `#C02931` / `#F03A43` | `#A32E2F` / `#CC3C3F` | `#AF252E` / **`#E0363F`** | lit met |
| Front median / lit | `#85191D` / `#E9353F` | `#941D21` / `#D53B3E` | `#AB232B` / **`#ED3942`** | median +38 |
| F34 median / lit | `#B6262B` / `#F83D44` | `#9F2226` / `#D73F41` | **`#BD2B32`** / `#EE3943` | |
| Side median / lit | `#8B1A1E` / `#DB323A` | `#7E1F20` / `#AE3A3E` | `#8E1F25` / `#BB2F38` | |
| Rear median / lit | `#7F1A1F` / `#D42F37` | `#8D1F23` / `#A72E32` | `#9F232B` / `#C12E38` | median +32 |
| R34 median / lit | `#81191E` / `#E2353D` | `#912226` / `#B03337` | `#9F212A` / `#C32E38` | median +30 |
| Top median / lit | `#C5252C` / `#F1343C` | `#AE2D32` / `#D34044` | **`#C22F38`** / **`#ED3943`** | |

- **What improved.** The red is now saturated (0.76–0.79; the sheet's is 0.76–0.78). The lit quartiles are within
  4–10 of the sheet in the front, f34, top and exploded views; in round 1 they were 20–36 under.
- **The trade-off.** The part shot (the leaf lying flat, softly lit) wants brighter keys. But the front, rear and r34
  medians are already 30–38 lighter than the sheet's, whose leaves sit in hard shade there. That is past the
  verifier's ~20 allowance, and brighter keys would push them further.
- **Why the part shot's lit quartile stays under target.** The flat part has no strongly lit facets in the studio
  light. Paint can't add that contrast without colouring by facing.
- The base → tip ramp (dark → leaf → tip) is kept.

### Minors

- **3. Seed bands: partly fixed.**
  - **Tip cap.** For diamonds above h .72, the height term is flattened (× 0.3) and the colour leans by direction
    (`lat_top` 0.25). From above the tip is now mixed, not one hot disc: top hot 50 → 43, deep 6 → 18.
  - **Thresholds.** With the cup closed, the deep belt is hidden, so `deep` 0.53 → 0.58 and `hot` 0.77 → 0.78.
  - **Lateral lean.** The verifier's `lat` 0.12 toward (+X, −Y) made the rear and r34 44–47 % deep with 10 % hot.
    Final: `lat` 0.03 toward (−X, −0.3 Y).
  - **What I swept:** `lat` 0–0.12, four directions, deep 0.53–0.62, hot 0.76–0.81, chk 0.14–0.18 and five noise
    seeds.
  - **Result.** Five views land within ±9; the front, f34 and rear are within ±6.
  - **Still out:** the side stays deep-heavy (48/30/21) in every variant, because a few big diamonds face that
    camera. The top is hot +11 and mid −11.
- **4. Top rock share:** recorded above (−10.6).
- **5. W : H:** front 1.16 against 1.27, f34 1.09 against 1.45. The size decision governs. The hero is
  6.96 × 5.69 × 5.50.
- **6. Rock contrast: tried, little effect.**
  - Change: `rock_light` `#7E675E` → `#886F66` (+8 %).
  - The rock medians are unchanged within 2.
  - The lit quartiles are still 10–25 under the sheet's (front `#8B6C5E` against `#9F7B6C`), because the patches mix
    toward `rock_light` by 75 % at most.
- **7. Seed slivers: fixed** by B1(c); no seed face sits below z 1.73.
- **8. Petal length: fixed** (4.33 with the peg).
- **9. Pod W : H:** 0.51, was 0.45. The exploded seed is 0.62 and the breakdown 0.69; the hero's seed is taller per
  decision 3.

### Checks (all re-measured after the final build)

| Object | Tris | Size (studs) | Shells | NM edges / verts | Boundary | Self-intersecting pairs | Min corner | Volume |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EmberbloomNode | 1470 / 4000 | 6.96 × 5.69 × 5.50 | 1 | 0 / 0 | 0 | 0 | 5.02° | +49.08 |
| EmberbloomPod | 144 / 1000 | 2.34 × 2.32 × 4.57 | 1 | 0 / 0 | 0 | 0 | 9.40° | +9.75 |
| EmberbloomPetal | 100 / 1000 | 4.33 × 1.61 × 1.34 | 1 | 0 / 0 | 0 | 0 | 5.40° | +2.75 |
| EmberbloomRockBase | 866 / 1000 | 6.41 × 5.69 × 1.15 | 1 | 0 / 0 | 0 | 0 | 5.02° | +16.35 |

- **Topology, all four objects:** no wire edges, loose verts, zero-area faces, n-gons or duplicate verts. Normals
  point outward, and the origin is at the bottom centre (offset 0, 0, 0).
- **Build path:** the union guard, the merge-0.002 union and `M.fix_bowties` are kept. No bowties needed fixing, and
  the guard made no union retries.
- **UV** (margin 0.008): 0 overlaps, 0 flipped, min gap 0.016, border 0.008, density 1.0 everywhere. Conformal stretch
  p95 is 1.026 (hero, 279 islands), 1.046 (pod), 1.049 (petal) and 1.024 (base).
- **`K.check`:** no problems.
- **Neon:** `m025_seed_deep` `#F24C18`, `m025_seed` `#FC7425` and `m025_seed_hot` `#FDA835`. Each has emission 1.0 and
  one flat colour, with Tint exactly 1.0 on every seed corner (hero and Pod).
- **`fx_check`** (re-run after the seed changes):

  | Socket | Build point | Clearance | Inside | Spawn points inside |
  | --- | --- | --- | --- | --- |
  | crystal_glow | (0, −1.2, 6.0) | 1.24 | no | – |
  | crystal_halo | (0, 0.3, 4.4) | 0.43 | yes (by design) | – |
  | embers | (0, 0, 6.2) | 0.70 | no | 0 / 125 |

### Kept as they were

- The six thick double-pointed shard leaves in a lotus (front pair low, back pair upright).
- The boulder ring and the underside recess.
- The Neon set-up and the three sockets.

### Renders

- **Where:** `art/blender/renders/models/M025/`.
- **From `build()`, VFX on:** `M025_views.png`, the `*_sheet.png` shots and `top_tilt.png`.
- **Also:** `exploded.png`, the `part_*.png` shots, `underside.png` and `vfx_halo.png`.
- **To re-measure:** run `m025.preview(vfx=False)`, then `m025.measure()`.

## Stage 7 — Verification (round 2)

Independent verifier (not the round 1 verifier), 2026-10-28. Read-only: a background session on port 9881 with
`art/blender/assets/kit/wip/M025_verify.blend` (the main session's rebuild). The file was not saved and `build()` was
not called. All renders went to a scratch folder (`M.MODEL_RENDERS` redirected), so `art/blender/renders/models/M025/`
was not touched. Every number below is my own re-measurement.

**Verdict: PASS, 7.5 / 10.**
- Both blockers are met against their stated targets.
- The technical side is clean.
- What is left are minors, and each has a cheap fix if the main session wants one.

### Technical checks

| Object | Tris | Size (studs) | Shells | NM edges / verts | Boundary / wire / loose | Zero-area / n-gons / dup | Self-hit pairs | Min corner | Volume | UV islands / overlap / flipped / gap / border / density / stretch p95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EmberbloomNode | 1470 / 4000 | 6.96 × 5.69 × 5.50 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 5.02° | +49.08 | 264 / 0 / 0 / 0.016 / 0.008 / 1.0 / 1.024 |
| EmberbloomPod | 144 / 1000 | 2.34 × 2.32 × 4.57 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 9.40° | +9.75 | 29 / 0 / 0 / 0.016 / 0.008 / 1.0 / 1.046 |
| EmberbloomPetal | 100 / 1000 | 4.33 × 1.61 × 1.34 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 5.40° | +2.75 | 23 / 0 / 0 / 0.016 / 0.008 / 1.0 / 1.049 |
| EmberbloomRockBase | 866 / 1000 | 6.41 × 5.69 × 1.15 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 5.02° | +16.35 | 148 / 0 / 0 / 0.016 / 0.008 / 1.0 / 1.024 |

- **Size:** within the decided 7.0 × 5.7 × 5.5 (±0.35 / ±0.4 / ±0.25).
- **Origin and transforms:** the origin is at the bbox bottom centre (offset 0, 0, 0.0000). Rotation 0 and scale 1 on
  all four objects. No modifiers, no custom normals and 0 smooth faces. One `UVMap` each. `M.audit` reports normals
  outward, and `K.check` returns `[]`.
- **Inverted faces.** Ray parity, one ray per face along its normal, re-tested with 7 jittered rays.
  - The parts have 0.
  - The hero has **1**: face 896, a 0.007 stud² dirt sliver at (−0.28, −1.13, 0.47), folded back-to-back under P4's
    base where the leaf meets the slab.
  - The hero also has **12 back-to-back edge pairs** (zero-angle creases), and the RockBase has 1.
    - 11 of the hero's pairs are at the leaf-base / slab seam at z 0.46–0.49. Ray tests find all of them invisible
      from every direction.
    - One is where back leaf P6 touches the seed at (−0.4, 1.04, 2.1), a crevice.
  - The bowtie, self-hit and manifold checks miss these by design. They are harmless in Roblox. Minor m6.
- **Neon.** `FB_m025_seed_deep` `#F24C18`, `FB_m025_seed` `#FC7425` and `FB_m025_seed_hot` `#FDA835` each have
  `flintkit_spec` [0.5, 0, **1.0**], Emission Strength 1.0, emission colour equal to the base colour, and nodes BSDF +
  Output only (no Tint mix), so each is one flat colour. Tint is exactly 1.000–1.000 on every seed corner of the hero
  and the Pod.
- **Solid keys:** emission 0. Tint runs 0.909–1.057 (rock and dirt) and 0.962–1.051 (leaf). The leaf keys have Specular
  IOR level 0.06 (`low_spec`).
- **No colour by facing.** Within each family, the key luminance does not correlate with normal z (r = 0 for leaf, rock
  and seed). `K.check` baked shading is within its limit.
- **Seed foot (B1c):** 104 seed-key faces, the lowest centre at **z 1.733**; 0 below z 1.4. 37 dirt-keyed foot faces sit
  above z 0.9 (z up to 1.68).
- **Sockets** (`fx_check`, run by me):

  | Socket | Settings | Build point | Clearance | Inside | Spawn points inside |
  | --- | --- | --- | --- | --- | --- |
  | `crystal_glow` | light only, `#FF8A2A`, 0.6, range 9, shadows, no flicker | (0, −1.2, 6.0) | 1.24 | no | – |
  | `crystal_halo` | `glow_soft`, `#FFD9A8` → `#FF9A3C` | (0, 0.3, 4.4) | 0.43 | yes (by design) | – |
  | `embers` | "Crystals", `spark_diamond`, `#FFE34A` → `#FECE16`, box 2.0 × 0.6 × 2.0 | (0, 0, 6.2) | 0.70 | no | 0 / 125 |

  This is exactly decision 8: no `heat_glow` and no harvest sockets, and the parts carry no sockets.

### B1 and B2 against their targets

**B1. Seed shape: met.**

Measured with VFX off, the sheet cameras, and the study's masks on both images.

| View | Seed visible from h (sheet / ours) | Visible W : H | Max width / W | Seed px in the bottom 25 % |
| --- | --- | --- | --- | --- |
| Front | .395 / **.433** | 0.67 / **0.65** | .32 / .32 | 0 / **0** |
| F34 | .45 / .433 | 0.71 / 0.64 | .27 / .33 | 0 / 0 |
| Side | .489 / .431 | 0.76 / **0.64** | .37 / .37 | 0 / **0** |
| Rear | .50 / .403 | 0.79 / **0.62** | .33 / .32 | 0 / **0** |
| R34 | .503 / .457 | 0.76 / 0.70 | .29 / .36 | 0 / 0 |

- **Targets.**
  - The front's lowest visible seed is at h .36–.44: met (.433).
  - Visible W : H is 0.60 or more in the front, side and rear: met (0.65 / 0.64 / 0.62).
  - Every view has 0 seed px in its bottom 25 %: met.
  - No seed face centre is below z 1.4: met (lowest 1.733).
  - The seed share is within ±4 of §1.2 in the front, side, rear and r34: met (−0.4, +1.5, +0.5, +2.7).
- **Front width profile** (seed width / visible height, from the bottom of the visible seed to the tip):
  - sheet .03 .36 .61 .67 .66 .64 .59 .50 .34 .21 .03;
  - ours .04 .55 .64 .65 .65 .62 .55 .46 .34 .19 .02.

  This is a near match: a plump gem in the leaf cup, no longer a flame tongue.
- **Side:** the same shape, about 15 % slimmer (max .63 against .75).
- **Rear and r34:** the bottom 20 % of the visible seed is still a narrow wedge in the V between the back pair (rear .08
  / .22 against the sheet's .70 / .77). The rest matches. Minor m2.

**B2. Leaf red: resolved in substance; the part-shot lit target is not met.**

| Region | Sheet | Ours | Δ R, G, B | Target |
| --- | --- | --- | --- | --- |
| Parts shot, Leaf cell: median | `#BC2931` | `#B0252E` | −12, −4, −3 | within 12 of `#BE2930`: **met (at the edge)** |
| Parts shot: lit quartile | `#E9373F` | `#C62B33` | −35, −12, −12 | ≥ `#E0353D`: **not met** |
| Parts shot: saturation, median / lit | 0.78 / 0.76 | 0.80 / 0.78 | | ≥ 0.75: **met** |
| Exploded: median / lit | `#C02931` / `#F03A43` | `#AF252E` / `#E0363F` | −17,−4,−3 / −16,−4,−4 | |
| Front: median / lit | `#85191D` / `#E9353F` | `#AB232B` / `#ED3942` | +38,+10,+14 / +4,+4,+3 | |
| F34: median / lit | `#B6262B` / `#F83D44` | `#BD2B32` / `#EE3943` | +7,+5,+7 / −10,−4,−1 | |
| Side: median / lit | `#8B1A1E` / `#DB323A` | `#8E1F25` / `#BB2F38` | +3,+5,+7 / −32,−3,−2 | |
| Rear: median / lit | `#7F1A1F` / `#D42F37` | `#9F232B` / `#C12E38` | +32,+9,+12 / −19,−1,+1 | |
| R34: median / lit | `#81191E` / `#E2353D` | `#9F212A` / `#C32E38` | +30,+8,+12 / −31,−7,−5 | |
| Top: median / lit | `#C5252C` / `#F1343C` | `#C22F38` / `#ED3943` | −3,+10,+12 / −4,+5,+7 | |

- **Judgement: the trade-off is accepted.**
  - Hue and saturation now match the sheet's "saturated red" in every view: 0.76–0.80 against 0.76–0.78.
  - The lit quartile matches where the studio light falls squarely: front, f34, top and exploded, all within 16.
  - The misses are lightness only, and they go both ways:
    - The front, rear and r34 medians are 30–38 *lighter* than the sheet's, whose leaves sit in harder shade.
    - The side, r34 and part-shot lit quartiles are 19–35 *darker*, because no facet faces the studio key.
  - Paint can't serve both without colouring by facing. Side by side, the leaves now read as the same red.

### Views against the sheet

Side-by-side crops of the sheet cell's bbox against our render's bbox, for all six sheet views, top_tilt, the parts,
the exploded view, the underside and the VFX panel. Shares are with VFX off; bold marks values out of tolerance.

| View | Seed S (sheet / ours) | Leaves L | Rock R | Bottom 20 % rock | Seed deep / mid / hot (sheet → ours) | W : H | Top-profile error mean / max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front | 22.0 / 21.6 | 48.6 / 49.8 | 29.4 / 28.6 | 95.8 / 92.9 | 26/52/23 → 25/50/25 | 1.27 / 1.16 | 0.039 / 0.17 |
| F34 | 16.1 / **21.7** | 54.7 / 50.8 | 29.2 / 27.4 | 97.4 / 95.3 | 26/50/25 → 20/50/30 | 1.45 / 1.09 | 0.076 / 0.19 |
| Side | 20.4 / 21.9 | 49.0 / 48.0 | 30.6 / 30.1 | 96.7 / 97.5 | 28/48/24 → **48/30/22** | 1.04 / 0.97 | 0.057 / 0.18 |
| Rear | 17.9 / 18.4 | 50.8 / 51.5 | 31.3 / 30.1 | 98.8 / 94.4 | 29/48/23 → 25/55/21 | 1.20 / 1.17 | 0.071 / 0.12 |
| R34 | 16.0 / 18.7 | 53.6 / 49.9 | 30.4 / 31.4 | 99.3 / 98.2 | 33/39/27 → 27/48/24 | 1.29 / 1.05 | 0.069 / 0.22 |
| Top | 11.2 / 15.0 | 59.5 / **66.2** | 29.3 / **18.7** | – | 20/48/32 → 19/38/44 | 1.13 / 1.24 | 0.064 / 0.12 |
| Top tilt | 11.2 / 16.4 | 59.5 / 62.9 | 29.3 / **20.7** | – | 20/48/32 → 19/42/39 | 1.13 / 1.11 | 0.094 / 0.22 |

- **Front, rear and r34:** a lotus of thick double-pointed shards round a plump faceted gem, with the boulder band below.
  - Silhouette error is 0.04–0.07 mean.
  - The front pair (cross ±1.6) meets in a V at the centre, like the sheet's front cell.
  - The silhouette is narrower (size decision 1).
- **F34:** reads as the front from slightly left. The sheet's f34 is drawn 33 % wider, so its seed share is +5.6 (as
  recorded; the size decision governs).
- **Side:** the broadened, raised P1 covers the seed's foot as the sheet's near leaf does. The silhouette is a little
  lopsided (the back pair stand taller on the right), but the profile error is only 0.057.
- **Top:** six leaves against the sheet's five (decision 2). The crossed front pair reads as two near-parallel leaves
  pointing to the front, so boulders show only at the sides and back. Minor m1.
- **Parts.**
  - Pod: W : H 0.51 against 0.62–0.69 (decision 3).
  - Petal: double-pointed, with its hex peg; its base end is fuller than the sheet's long base point.
  - RockBase: boulder ring, dirt floor and mount post. The sheet draws a raised slab rim as well.
  - The exploded and underside views read like the sheet. The VFX halo and the diamond crystals match the VFX panel.

### Colour (sheet → ours, Δ R, G, B)

| Region | Sheet | Ours | Δ |
| --- | --- | --- | --- |
| Seed mid (front median) | `#FC7926` | `#FF741E` | +3, −5, −8 |
| Seed hot (front lit) | `#FDA736` | `#FFB02E` | +2, +9, −8 |
| Seed deep (front shade) | `#F65117` | `#FF4711` | +9, −10, −6 |
| Seed f34 lit | `#FDC23D` | `#FFB02E` | +2, −18, −15 |
| Pod part median | `#FD7628` | `#FF731D` | +2, −3, −11 |
| Exploded seed median | `#FC7C27` | `#FF4B13` | +3, **−49**, −20 (deep-heavy, m3) |
| Rock front median / lit | `#70594E` / `#9F7B6C` | `#70574D` / `#8B6C5E` | 0,−2,−1 / −20,−15,−14 |
| Rock exploded median | `#795C50` | `#785E53` | −1, +2, +3 |
| Rock base part median | `#836459` | `#7B6054` | −8, −4, −5 |
| Rock side / rear median | `#765C52` / `#775E52` | `#5B4841` / `#69534B` | −27,−20,−17 / −14,−11,−7 (studio shade) |
| Rock f34 / top median | `#674F46` / `#645049` | `#795E52` / `#6C554E` | +18,+15,+12 / +8,+5,+5 |
| Leaves | see the B2 table | | |

### Modeller's deviations: rulings

- **Leaf-cup crossing (P3 / P4 cross ±1.6): accepted.**
  - It is what closes the front cup: the seed is visible from h .433, with 0 px low.
  - It costs the top view its even five-point star (m1).
  - It leaves the cup open at the diagonals (m2).
- **Dirt-keyed seed foot (16 diamonds below z 1.5): accepted.**
  - It matches the sheet's Seedpod Mount (the seed on a dirt peg).
  - The Pod part stays all Neon.
  - Ray tests show 30 of the 37 dirt foot faces visible from some direction (az 45–60° and 285–315°, el 8–45°)
    *through the gaps between the leaves*. In renders at those angles they read as a dark wedge of ground under the
    seed. That is far better than round 1's orange specks.
- **Leaf-red trade-off: accepted** (see B2).

### Findings

**Blockers: none.**

**Minors** (record, or fix cheaply in `m025.py`):

1. **m1. Top rock share 18.7 against 29.3** (top_tilt 20.7). Six leaves (decision 2) plus the crossed front pair cover
   the ring from above.
   - Cheap fix if wanted: shorten the leaf tips' reach about 5 % (`LEAVES` tip radii × 0.95) for the four side and back
     leaves only.
   - Check that the front, side and rear leaf shares stay within ±4.
2. **m2. The seed's lower cone shows between leaves at diagonal angles.**
   - In the rear and r34, the lowest 20 % of the visible seed is a narrow wedge in the back pair's V.
   - At az 45° and 300° (not sheet views), the seed tapers down to the dark foot: a hint of the round 1 flame tongue.
   - Cheap fix: fill the lower cone, e.g. `SEED_RINGS` (0.10, 0.45) → (0.10, 0.60), so what shows between the leaves
     is gem, not taper. This also widens the Pod part's bottom toward the sheet's.
3. **m3. The Pod part (and the exploded seed) is deep-heavy:** 46 / 27 / 27 against the sheet's 22 / 55 / 23. The
   hero's `deep` 0.58 is tuned for a seed whose lower half is hidden, but the part shows its whole height, so half of
   it is red-orange.
   - Cheap fix: give `_paint_seed` a threshold override for `pod_part` (e.g. `deep` 0.35, `hot` 0.72).
   - Target: the part's bands within ±8 of the sheet's.
4. **m4. Side-view seed bands** 48 / 30 / 22 against 28 / 48 / 24 (as the modeller recorded: a few big diamonds face
   that camera). The top is hot +12, mid −10. Leave it.
5. **m5. Rock contrast:** the lit quartiles are 15–25 under (front `#8B6C5E` against `#9F7B6C`), and the side and rear
   medians sit in studio shade. The unshadowed medians match within 8. Leave it.
6. **m6. Degenerate creases.** One folded dirt sliver (0.007 stud², odd ray parity) and 11 back-to-back face pairs at
   the leaf-base / slab seam (z 0.46–0.49), all invisible from every direction; one crease where P6 touches the seed.
   The RockBase has one between two boulders. No check fails and nothing shows.
   - Optional: dissolve faces under 0.01 stud² at that seam in `_finish`.
7. **m7. W : H** 1.16 / 1.09 against the sheet's 1.27 / 1.45 (front / f34): size decision 1. Record.
8. **m8. Part shapes.** The Pod's W : H is 0.51 (decision 3). The Petal's base end is fuller than the sheet's long base
   point. The RockBase has no raised slab rim. Record.

**Kept as they are:**
- the six thick double-pointed shard leaves;
- the plump seed cupped at h ≈ .43;
- the boulder band (bottom 20 % at 93–98 % rock);
- the underside recess;
- the three Neon keys at their decided hexes (99.8 % or more bright);
- the three sockets;
- clean topology, UVs, origin and transforms.

## Main session after verification round 2 (2026-10-28)

Applied m3: `POD_PART_BANDS` (deep 0.2, hot 0.74) for the Pod part only. Face keys went from 60/52/32 at deep 0.35 to 46/72/26 (deep / mid / hot), against the sheet's mostly-mid part. The hero is unchanged: 1470 tris, one shell, 0 bowties, `problems` empty. Export: 0 problems. m1, m2 and m4–m8 are recorded in MODEL_PROGRESS.md.
