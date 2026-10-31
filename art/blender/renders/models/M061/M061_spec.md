# 061 Meadow Herb — spec

Reference: `art/blender/assets/references/061.png` (1024 × 1536 px). INDEX.md row 61: "Flintborn Meadow Herb Study".
The sheet's own header reads **"62/132"** (top left), title **"MEADOW HERB"**, subtitle "FLINTBORN — INDIVIDUAL MODEL
STUDY" (our number is INDEX's 061, §3.1).
Builder: `art/blender/kit/mcp/m061.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows no effect** (§7). It is a **common
meadow plant that will be repeated many times**, so it is budgeted near the small-prop class (§4.3, decision §8.14). The
plant rules of WorldModeling §1, §6 and §18 apply: **three chunky daisies on thick stems over a rosette of broad, thick,
faceted kite leaves**; the petals are broad blunt lozenges with real thickness (never thin pointed slivers, the old W07
failure), the leaves are closed solids (never flat cards), and **no part is turned toward a camera** (054 / 057: leaf
cards turned toward the front / rear cameras read as balls with spikes from the sides).

Sheet text (paraphrased):
- **Title block (top left):** "62/132", "MEADOW HERB".
- **Description (top centre):** a simple five-petal daisy with leaves; a common meadow plant.
- **Header palette (top right):** six unlabelled swatches: cream, yellow, lime, mid green, dark green, brown (§5.1).
- **"ASSEMBLED":** "FRONT 3/4" and "REAR 3/4".
- **"ORTHOGRAPHIC VIEWS (CONSISTENT GEOMETRY)":** "FRONT", "SIDE", "REAR", "TOP".
- **"EXPLODED CONSTRUCTION (PARTS & ASSEMBLY)":** labels "Petal (x5)", "Center (x1)", "Stem (x1)", "Leaves
  (xMultiple)". Drawn: five loose cream petal plates in a ring, a faceted yellow centre bead, one stem with a flat-topped
  cup and a crook below it, four loose kite leaves, each with arrows down into the assembly; the assembly is the three
  daisies on their stems rising from a low shared base, separate kite leaves lifted off round it, and a **leaf base** (a
  five-leaf fan) at the bottom receiving the stems.
- **"CONSTRUCTION CLOSE-UPS":**
  1. "FLOWER HEAD (UNDERSIDE)": a head from below: a simple faceted green cup under the petals, the stem entering the
     cup's bottom; callout: a simple faceted cup under the petals.
  2. "LEAF JUNCTION (DETAIL)": leaf bases crowding together at the centre; callout: the leaves meet at a central base
     with simple butt joins, no complex blending.
  3. "STEM INSERT (BASE VIEW)": an octagonal green collar with a hexagonal socket, and a hexagonal stem end with an arrow
     to it; callout: the stem plugs into the base; flat faces, no small details.
- **"PARTS (ISOLATED)":** Petal (x5), Center (x1), Stem (x1), Leaf (x1), Leaf Base (x1).
- **"MATERIAL PALETTE (MODEL COLORS)"** (bottom centre): the same six swatches, slightly darker (§5.1); bullets: solid
  flat colours without textures; broad clean facets; consistent with the Flintborn low-poly style; reusable parts; simple
  readable shapes.
- **"MODEL NOTES":** built from simple reusable parts (five petals, one centre, stems, leaves and a shared leaf base);
  keep the geometry chunky and clean; keep the silhouette clear at small scale; no fine detail or texture noise; match the
  Flintborn library's style and proportions.
- **Game context and the old kit:**
  - **W07 row 2 `MeadowDaisy`** (`art/blender/scripts/kit/W07/meadow_daisy.py`; manifest `art/roblox/kit/W07/manifest.json`;
    goals `art/blender/renders/kit/W07/meadow_daisy_goals.md`) is the old kit's take on this subject. Manifest: **6.01
    wide × 5.71 deep × 5.00 tall**, 852 tris (budget 2000), collision `none` (CanCollide / CanQuery / CanTouch off), no
    VFX; note "three big white 6-petal daisies on stems over a rosette of broad pointed leaves". `MODEL_PROGRESS.md` row 68:
    "mostly-done: thin pointed petals, tiny centre; flat leaves". Its palette: `w07_leaf #62B232`, `w07_petal_white
    #F2EAD2`, `w07_daisy_yellow #F5B800`. Its verifier history: dark leaf, a dense dark rosette, round petals, a sliver
    petal part, then petals fused into a pentagon disc. Parts `MeadowDaisyCenter / …Leaf / …Petal / …Stem`, variants
    `…SingleWhite`, `…WhiteClump`, `…YellowClump`. **Those names are taken** (§8).
  - **Related:** the lobby's `WildflowerWhite` (3.3 wide × 2.3–2.5 tall, `build_05_trees_plants.py` `daisy()`: flat
    head, broad rounded petals round a domed centre); W07 `Wildflowers*` (sheet 065 is a separate wildflower study);
    scatter daisies in 032 / 037 / 041 and `K.daisy` (flat six-petal stars for meadow dressing, not this hero's chunky
    head); 059 Grass Tuft (2.4 tall), 060 Broadleaf Fern (3.0 tall). §1.5 keeps 061 apart from them.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The page is pale paper
(`#F9F8F5`); each panel is cream (`#F5F0E7` at the top, `#F2EEE4` near the floor) with a soft warm-grey cast shadow
falling left of the plant. Measured grey rules: header rule y 93; assembled frame y 94–455, x 11–549 / 556–1013;
ortho title bar y 463–495, cells y 495–756, dividers x 275, 511, 760; exploded x 11–648, y 797–1343; close-ups x
656–1013 (dividers y 992–1001, 1160–1169); bottom panels y 1351–1526 (parts x 11–494, palette x 501–756, notes x
764–1013).
- **Cells** (`m.V`, `m.X` in the study folder): f34 (11,96,549,454); r34 (556,96,1013,454); front (11,520,275,756); side
  (276,520,511,756); rear (512,520,760,756); top (761,520,1013,756); exploded (11,797,648,1343); cu1 "flower head"
  (656,820,1013,992); cu2 "leaf junction" (656,1025,1013,1160); cu3 "stem insert" (656,1195,1013,1343); parts row
  (11,1375,494,1470).
- **Blanked text** before measuring: (15,100,125,145) and (560,100,670,145), the assembled labels.
- **Swatches** (inner boxes, sd ≤ 2.7): header H1 (749,26,780,58), H2 (793,26,825,58), H3 (837,26,869,58), H4
  (882,26,914,58), H5 (927,26,959,58), H6 (971,26,1004,58); palette panel P1 (519,1389,541,1416), P2 (556,…,583), P3
  (595,…,622), P4 (634,…,663), P5 (674,…,701), P6 (714,…,741).
- **Masks** (`cls()` in `m.py`, HSV, h in degrees):
  - **G**, green (leaves, stems, cups): h 60–170, s ≥ 0.25, v ≥ 0.06.
  - **Y**, yellow centre: h 30–60, s ≥ 0.55, v ≥ 0.55.
  - **W**, petal: anything else that differs from the panel's per-row paper colour by > 9 (or is near-white, v > 0.985
    and s < 0.07), above the lowest 30 % of the plant (so the floor shadow is excluded), closed 7 × 7 and hole-filled
    per head. **Caveat:** the petals' mid tone equals the paper (`#F4F0E5`), so W is the least exact class (±3 points);
    a few enclosed paper gaps between low leaves leak into W (≤ 0.5 %). On our renders use a plain studio background
    with the floor hidden and the same code.
  - **Green tones:** light v ≥ 0.70, dark v < 0.42, mid the rest. Dark includes the deep shade inside the rosette and on
    the shaded stems; apply the same masks to our renders.
  - **Top cell:** the cast shadow left of the plant joins the left head's petal mask (a block artefact); judge the top
    for content only (§3.3).

**Scratch study material** (no Blender) in
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m061_study\`.
Run with `C:/Users/Orang/.local/bin/uv.exe run --no-project --with pillow --with numpy --with scipy python <script> < /dev/null`.
- **Helpers:** `m.py` (boxes, `masks`, `petal_cand`, `cls`, `tones`, `clsimg`), `zoom.py` (`zoom.py x0 y0 x1 y1 scale
  out.png [grid]`), `probe2.py` (`probe2.py x,y …` → hex and HSV), `lines2.py` (frame rules), `sw.py` (swatches).
- **Measurements:** `measure.py` → `measure_out.txt` (bbox, W : H, shares, fill, tones, top profile, widths per height,
  fifths, head blobs); `runs.py` → `runs_out.txt` (class runs at h .30–.90, x from the bbox centre in fractions of H);
  `samp.py` → `samp_out.txt` (tones and named regions); `expl.py` → `expl_out.txt` (exploded and parts-row blobs: L, W,
  L : W, width profile, tone); `blobs.py` (yellow centres per view); `brown.py` (where the brown swatch colour appears).
- **Zooms:** `z_f34.png`, `z_r34.png` (2×, gridded), `z_front.png`, `z_side.png`, `z_rear.png`, `z_top.png` (3×,
  gridded), `z_f34_heads.png`, `z_top_heads.png`, `z_fr_mid.png`, `z_fr_left.png` (petal counts), `z_expl.png`,
  `z_cu.png`, `z_parts.png`, `z_pal.png`, `z_head.png`; class maps `cls_front_side_rear_top.png`, `cls_f34_r34_top.png`.
- **On our renders:** copy 058's or 059's `meas.py`, point it at this folder's `m.py` and use `cls()`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** a repeated meadow plant with three flower heads: small prop extended (decision §8.14). **Budget:
  hero ceiling 1400 tris, plan about 1100–1250; every part under 1000.** The old W07 hero used 852 of 2000 and failed on
  thin petals and flat leaves; thick petals and closed leaves cost the difference.
- **Overall read (check this first).** A **low, rounded clump about 1.17 × as wide as tall**:
  - **three white daisies** at three heights: the tallest **near the centre** facing front-up, a **lower one to the
    left** facing front-left, a **middle one to the right turned toward +X** (nearly side-on in the front);
  - each head is **five broad cream petals** in a ring round a **chunky faceted yellow bead**, with a **faceted green cup**
    under the petals;
  - **thick dark-green hexagonal stems**: the middle one nearly straight, the left one rising up-left with a kink below
    its head, the right one a smooth arc out to the right;
  - a **dense rosette of broad faceted kite leaves** filling the lower 55 % of the height and the full width: an upright
    centre fan, leaves spreading out flat to both sides, big lime leaves drooping toward the viewer front and back with
    their tips on the ground, and small dark leaves round the rim.
  - It reads **green under white**: front G 61.8 %, W (petals) 32.5 %, Y (centres) 5.7 %.
- **Focal silhouettes, in order:**
  1. Three white five-petal stars with yellow dots at three heights (front heads at h .85 / .76 / .65 of H).
  2. The thick stems carrying them out of the leaves (each 0.07 H wide).
  3. The rosette: a broad green mound with pointed leaf tips round its rim (leaf tips at h .37–.62) and drooping lime
     leaves at the foot.
- **Target size: 2.2 tall (the tallest petal tip), 2.55 wide (X) × 2.1 deep (Y)** (decision §8.1). Tolerances: height
  ±0.08, width ±0.15, depth ±0.15.
  - **How it was derived.** Front silhouette 231 × 198 px → **90 px / stud** at H 2.2 → W 2.57. Rear 210 × 194 → 2.38.
    Side 177 × 192 → **2.03 deep** (heads included). Top 221 × 188 (W : D 1.18, about the ortho scale, 88 px / stud) →
    2.51 × 2.14. f34 414 × 322 (146 px / stud; drawn from higher up, §3.2) → 2.83. Width taken as 2.55 (front and
    rear together), depth 2.1 (side and top together).
  - **Why 2.2.**
    - 0.40 C against the 5.5-stud character: **knee height**, the top of WorldModeling §3.2's flowering-herb range
      (0.15–0.40 C). The heads (Ø 1.1) are 0.50 of the height, inside §3.2's bloom range (0.25–0.55).
    - It sits **just under 059 Grass Tuft (2.4)** and well under 060 Fern (3.0), so in a meadow the daisy heads (centres
      at 1.4–1.9) stand above the tuft's merged mass (below 1.2) and among its tallest tips, where a player sees them.
    - At 2.2 the parts stay readable: petals 0.46 × 0.34, centres Ø 0.40, stems Ø 0.14, leaves 0.45–0.55 wide.
    - The old W07 hero (5.0 tall, 0.91 C) is waist-to-chest high: a giant daisy. The lobby `WildflowerWhite` (2.3–2.5)
      is the same order as ours.
    - At 1.8 the petals shrink to 0.38 and the stems to 0.11 (thin at gameplay distance); at 2.6 it crowds 059.
  - **Against the character (5.5):** 0.40 C tall, 0.46 C wide.
- **Build frame:** front −Y, +X right, ground z 0, the leaf-base hub axis at (0, 0). The origin is the bbox bottom
  centre; the heads are not symmetric, so record the origin's offset from the hub axis (expected ≤ 0.10).

### 1.2 Measured views (`measure.py`, `samp.py`)

| View (box) | Silhouette bbox (px) | W : H | G | W | Y | fill | green light / mid / dark |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (11,96,549,454) | 68–481 × 113–434 (414 × 322) | 1.286 | 65.6 % | 28.9 | 5.6 | 0.611 | 33 / 40 / 27 |
| Rear three-quarter (556,96,1013,454) | 628–968 × 129–432 (341 × 304) | 1.122 | 78.0 | 21.7 | 0.3 | 0.559 | 31 / 45 / 23 |
| **Front** (11,520,275,756) | 27–257 × 542–739 (231 × 198) | **1.167** | **61.8** | **32.5** | **5.7** | **0.650** | **31 / 40 / 29** |
| Side (276,520,511,756) | 311–487 × 544–735 (177 × 192) | 0.922 | 64.7 | 30.8 | 4.5 | 0.409 | 17 / 51 / 32 |
| Rear (512,520,760,756) | 531–740 × 542–735 (210 × 194) | 1.082 | 71.0 | 28.6 | 0.4 | 0.568 | 28 / 51 / 21 |
| Top (761,520,1013,756) | 776–996 × 549–736 (221 × 188) | W : D 1.176 | 52 | 41 | 7.4 | 0.625 | 35 / 42 / 23 |

- Shares are of the silhouette (background and floor shadow excluded). **Fill** = silhouette / bbox area. Top shares are
  rough (the shadow artefact above).
- **The rear and r34 show the heads from behind:** Y ≤ 0.4 % (only glints), the green cups visible at the head centres.
- **Verifier tolerance:** G ±5, W ±4, Y ±1.5 points; W : H ±0.07; fill ±0.05; head centres ±0.06 H; tones ±8.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.1 W):

| f | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .39 | .70 | .78 | .78 | .94 | .98 | .93 | .93 | .89 | .83 | .41 |
| r34 | .67 | .82 | .88 | .61 | .97 | 1.00 | .92 | .75 | .76 | .68 | .40 |
| **Front** | .55 | .74 | .82 | .79 | .94 | .99 | .93 | .93 | .89 | .84 | .69 |
| Side | .49 | .50 | .46 | .96 | .98 | .99 | .93 | .91 | .74 | .69 | .51 |
| Rear | .58 | .74 | .80 | .78 | .93 | .97 | .93 | .92 | .74 | .69 | .48 |

**Width per height** (silhouette width at h .02 → .98 in 11 steps, fraction of W):

```
f34    .53 .88 .78 .91 .93 .74 .89 .88 .70 .45 .09
r34    .69 .85 .78 .87 .98 .70 .82 .87 .56 .47 .18
front  .56 .84 .73 .92 .77 .76 .97 .96 .77 .49 .10
side   .15 .54 .44 .59 .60 .92 .61 .51 .46 .45 .14
rear   .66 .75 .80 .94 .49 .89 .96 .83 .50 .42 .06
```

- Reading (front): h .1–.4 the rosette across nearly the full width (.73–.92); a waist at h .4–.5 (.76–.77: the leaf tips
  end, only stems and the low heads' petals); h .6–.7 the three heads side by side (.96–.97); h .8–.9 the tall head and
  the upper petals of the right head (.49–.77); the top is H_M's upper petal.
- Side: narrow foot (.15 at h .02), the leaves rising to the sides (h .1–.4 .44–.60), the heads at h .5 (.92 with the
  low head's petals reaching out).

**Height fifths** (bottom → top, % of each class):
- Green: front 29.9 / 43.3 / 20.7 / 6.1 / 0.0; f34 30.4 / 43.4 / 21.1 / 5.0 / 0; rear 30.5 / 39.9 / 19.5 / 7.9 / 2.2;
  side 33.1 / 36.6 / 22.4 / 7.9 / 0.
- Petals: front 0 / 1.8 / 22.0 / 47.6 / 28.5; f34 0 / 1.2 / 21.3 / 48.6 / 29.0; rear 0 / 1.4 / 23.7 / 44.6 / 30.3; side
  0 / 2.7 / 14.1 / 41.1 / 42.1.
- **Green stays below h .6 except the stems and cups; petals live above h .4.**

**Outline runs** (`runs.py`; x from the bbox centre in fractions of H; G green, W petal, Y centre):

| View | h .50 | h .65 | h .80 |
| --- | --- | --- | --- |
| Front | W[−.58 … −.33] G[−.32 … −.24] G[−.18 … −.05] G[−.04 … +.13] G[+.17 … +.24] G[+.27 … +.31] | W[−.55 … −.21] (Y −.45 … −.31) G[−.03 … +.04] G[+.28 … +.45] W[+.46 … +.57] | W[−.38 … −.30] W[−.15 … +.38] (Y +.01 … +.11) Y/W[+.39 … +.47] |
| Side | G[−.39 … −.36] G[−.14 … −.08] G[+.13 … +.21] W[+.21 … +.45] | G[−.12 … −.05] G[+.20 … +.24] W[+.25 … +.37] | W[−.20 … +.21] (Y .00 … +.07) |
| Rear | W[−.43 … −.40] G[−.26 … −.18] G[−.02 … +.04] G[+.07 … +.17] G[+.26 … +.40] W[+.41 … +.53] | W[−.48 … −.39] G[−.37 … −.26] G[−.01 … +.05] W[+.23 … +.47] | W[−.33 … −.25] W[−.16 … −.08] G[−.07 … +.10] W[+.11 … +.19] |

- **Stem widths:** front middle stem at h .65 0.07 H (0.15 studs), right stem at h .60 0.07 H; side tall stem at h .55
  0.07 H; rear middle 0.06 H; r34 0.06 H. **Stems Ø ≈ 0.14.**
- **Cup widths:** rear tall cup at h .80 0.17 H (0.37), r34 0.14 H (0.31). **Cup Ø ≈ 0.33 at the top.**

**Heads** (yellow centre, or the cup on the rear / r34; studs at H 2.2; front x from the stems' meeting point x 142 ≈ the
bbox centre; rear image left = world +X):

| Head | Front centre (px) → (x, z) | f34 → (x, z) | r34 → z | Rear → (world x, z) | Side → (image x, z) | Top → (x, y) | Facing in the front |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **H_M** tall | (151, 570) → (+0.10, **1.88**) | (299, 160) → (+0.17, 1.87) | cup (809, 168) → 1.91 | (636, 568) → (0.00, 1.89), back | (400, 571) → (+0.11, 1.88), face-on | (914, 603) → (+0.32, **+0.44**) | front-up: ring ~100 × 67 px (ratio .67) |
| **H_R** right | (231, 589) → (+0.99, **1.67**) | (427, 193) → (+1.04, 1.65) | (680, 204) → 1.65 | (561, 607) → (+0.84, 1.45), back | hidden | not drawn | **turned toward +X**: ring ~40 × 70 px (ratio .5) |
| **H_L** left | (65, 611) → (−0.86, **1.42**) | (159, 227) → (−0.79, 1.41) | (907, 237) → 1.41 | (708, 616) → (−0.82, 1.35), back | (462, 610) → (+0.83, 1.43), side-on | (826, 652) → (−0.68, −0.11) | front-left: ring ~83 × 80 px (ratio ≈ 1) |

- **Heights are consistent across front, f34, r34 and side:** H_M 1.88, H_R 1.66, H_L 1.42 (centre of the yellow
  bead). The rear draws H_R lower (1.45); the front governs (§3.4).
- **Head size:** front H_M ring 100 px → **Ø 1.11**; top 109 px and 100 px → Ø 1.24 / 1.13; front H_L 83 px (0.92, a
  little oblique). **Ø 1.10 for all three** (H_M 1.15 allowed). Centre bead: front 36 px, top 37 / 32 px → **Ø 0.40**
  (0.36 of the head).
- **Petal count: five per head** in the top view (both heads, `z_top_heads.png`), the exploded, the parts row, the
  description and the notes; the front and f34 draw 6–7 overlapping petal shapes on the heads (§3.5).

**Leaves** (front, read off the 3× zoom; studs at H 2.2; x from x 142, z from y 739):

| Leaf (tier) | Front tip (px) → (x, z) | What it is |
| --- | --- | --- |
| Spread far-left | (28, 666) → (−1.27, 0.81) | a big leaf spreading flat to the left, mid / lime |
| Spread far-right | (256, 663) → (+1.27, 0.84) | the same to the right, lime |
| Inner right, rising | (214, 643) → (+0.80, 1.07) | rises to the right at about 40° |
| Inner left, rising | (103, 647) → (−0.43, 1.02) | behind the left stem |
| Upright left of centre | (114, 618) → (−0.31, **1.34**) | the centre fan's tallest, mid green |
| Upright right of centre | (163, 622) → (+0.23, 1.30) | lime-lit |
| Front-left big (drooping) | (91, 738) → (−0.57, **0.01**) | a big lime kite pointing down toward the viewer, tip on the ground |
| Front-right big (drooping) | (214, 737) → (+0.80, 0.02) | the same, right |
| Front centre small | (144, 735) → (+0.02, 0.04), its top at z 0.38 | a small upright diamond in front of the stems |
| Rim small dark left / right | (49, 728) → (−1.03, 0.12) / (243, 718) → (+1.12, 0.23) | small dark leaves lying nearly flat at the rim |

- **Leaf top:** the fan's tips reach **z 1.30–1.34 (h .60)**; green above h .6 is only stems and cups.
- **Counts per view:** leaves front 12–13, f34 13–14, rear 12, side 7–8 (the rosette is narrower from the side), top
  12–14 radiating round the centre.
- **Depth:** green in the side spans 1.75 (x 311–464); in the top 2.14 → the rosette is a little oval, **2.5 × 2.0**.

### 1.3 Silhouette and composition per view

**Front (`z_front.png`) — governs positions and heights.** A low view. H_M stands slightly right of centre on a straight
thick stem, its face toward the viewer and up (the petal ring an ellipse, the bead on top of it). H_L sits low at the far
left facing the viewer, its stem rising up and left from the centre with a kink just under the head. H_R sits at the right
turned toward +X: we see its petals edge-on-ish and the side of its bead, its cup and stem curving into it from below-left.
The rosette: an upright fan of mid / lime leaves between the stems (tips z 1.3), long leaves spreading flat to both sides
(tips at x ±1.27, z 0.8), a right leaf rising at 40°, two big lime kites in front drooping to the ground, a small diamond
leaf front-centre, small dark leaves at the rim; deep shade between them.

**Front three-quarter (`z_f34.png`) — governs the read.** Drawn **nearly frontal from higher up**: head x fractions .22 /
.56 / .87 against the front's .16 / .54 / .88, W : H 1.286 against 1.167; the rosette top and the drooping front leaves
show more. Lit from the upper right: lime on the upper faces of the leaves, dark in the creases and on the stems'
shaded sides; petals cream with warm-grey shade (`#C4B59E`) on their lower faces and edges; beads golden with an orange
lower band.
- **Petals** show their thickness as a grey side band (about 0.05 studs) and a faint centre crease; each is a broad
  lozenge, wider than half its length, with a blunt faceted end.
- **Stems** are thick hexagonal prisms (flat faces catching the light in bands), **cups** faceted and flared under the
  heads.
- **Leaves** are faceted kites with a ridge: one half lit, one half shaded, widest at the middle, a pointed tip, a narrow
  base disappearing into the centre.

**Rear three-quarter (`z_r34.png`).** The heads from behind: three green faceted cups with the petals' undersides round
them (cream lit, warm-grey shade); the tall stem straight up the middle; the rosette the same as the front's (spreading
side leaves, big drooping leaves toward this camera, small centre diamond, upright fan).

**Rear (`z_rear.png`).** A near mirror of the front: H_M's cup on top of the tall straight stem, two lower heads from
behind left and right, the rosette as from the front.

**Side (`z_side.png`).** A narrower view (W : H 0.92): the tall stem at the centre bowing gently (curving out and back) to
H_M, seen face-on; a second, lower head at the right on a stem that arcs out to it, turned to the right (side-on); a big
upright-leaning leaf at the left, one at the right, small leaves at the foot and a small centre diamond. Only two heads
show (§3.4).

**Top (`z_top.png`).** Two heads seen face-on from above (five petals each, golden beads), over a star of 12–14 kite
leaves radiating from the centre, dark shade between them. The third head is not drawn (§3.3).

**Flower head underside (close-up 1).** A head from below: a **faceted green cup** (about 8 sides, flaring up to the
petals; `#3A6C11`, lit `#669E15`) under the ring of petals; the hex stem enters the cup's bottom at an angle; petal
undersides cream with warm-grey shade.

**Leaf junction (close-up 2).** The leaves' narrow bases crowd into the centre side by side with plain butt joins: each
leaf a faceted solid with a ridge, lime and mid faces (`#548913`, lit `#7CAF1E`).

**Stem insert (close-up 3).** The base seen from below or above: an **octagonal collar** (`#598E2E`) with a **hexagonal
socket** (dark inside, `#1F3D1A`) and the end of a hexagonal stem (`#437229`) aimed into it; flat faces only.

### 1.4 Parts (exploded `z_expl.png`; parts row `z_parts.png`)

The exploded is a front three-quarter at about the hero's scale, parts lifted off. **The hero governs every size, angle
and position (§3.9); the exploded and parts row govern each part's shape.**

`expl.py` (principal-axis length L, max width W, the width profile in tenths):

| Part (label) | Box (px) | L × W, L : W | Width profile | Tone | Notes |
| --- | --- | --- | --- | --- | --- |
| Petal (x5), exploded | five loose plates (96–293, 821–916) | each 50–77 × 26–42 (lying, foreshortened) | | cream `#CFC0A7` (their shaded undersides) | broad chunky plates, faceted ends, visible thickness |
| Petal, parts row | (31–79, 1399–1464) | 67 × 46, **1.45** (W : L 0.69) | 13 31 39 42 44 44 42 38 39 32 | `#EBE1D0`, lit `#FEFDF4`, shade `#E3D9C4` | standing upright: a **lozenge**: narrow base, widest at 0.5–0.7 L, a blunt faceted top; a centre crease; thick |
| Center (x1) | exploded (168–223, 918–962) / parts (116–159, 1413–1456) | 56 × 45 / 44 × 43 | | `#F7BC06` / `#FBC508` (lit `#FED814`, shade `#B97702`) | a **faceted bead**: about 10 facets showing, squat in the exploded (W : H 1.25), round in the parts row |
| Stem (x1) | exploded (157–219, 992–1137) / parts (198–229, 1381–1465) | 148 × 58 / 86 × 30 | 58 54 45 23 22 23 25 26 27 25 (cup at the top) | `#497B1F` / `#477A1D` (93°), lit `#83B435` | a **hex prism** with a **flat-topped faceted cup** (≈ 2.4 × the stem's width) on a **crook** just under it (the cup tilts 25–35° off the stem axis); the lower stem straight |
| Leaves (xMultiple), exploded | four loose kites (123–378, 1070–1264), (516–629, 1117–1199) | 133–149 × 52–70, **2.1–2.6** | 20 37 53 58 62 63 60 51 35 20 | `#72A82B`–`#76AD28` (lime-mid), one `#588D2D` | **kites**: pointed both ends, widest at 0.45–0.6 L, a centre ridge, 2 facets a side |
| Leaf, parts row | (265–314, 1398–1464) | 80 × 42, **1.9** | 15 29 37 39 40 40 34 28 18 10 | `#7AAF2B`, lit `#9CCC3A`, shade `#60941D` | the same kite, thick |
| Leaf Base (x1) | exploded (285–574, 1182–1322) / parts (346–476, 1386–1464) | 289 × 139 / 131 × 79 | | `#6AA025` / `#7BAF21` | a **five-leaf fan**: a tall upright centre leaf, two upright-leaning leaves either side, two leaves spreading out flat left and right, all from one hidden hub |
| Assembly (exploded) | (351–596, 911–1171) | | | `#54881C` | the three stems rising from a low flat base, the heads as in the hero, three lifted leaves round the base |

- **Petal construction:** a closed lozenge plate: outline of 6 verts (base point, two base shoulders at 0.25 L, two
  wide shoulders at 0.65 L, a blunt tip pair or chamfered tip at 1.0 L), a shallow centre crease on top, thickness 0.05
  (0.06 at the crease line). **Never a pointed needle or a sliver** (W07's failures).
- **Bead construction:** a squat faceted gem: an 8-sided ring at the equator, a 5–6-sided top ring and a cap, the lower
  half sunk into the cup / petal ring.
- **Leaf construction:** a closed kite: two tips (base and apex), two wide-shoulder verts at 0.5 L, a raised centre ridge
  on top (+0.04) and a shallow keel below (+0.02), edges 0.06 thick; the halves meet at the ridge in a shallow V
  (dihedral 15–25°) so one half catches the light.

### 1.5 How 061 differs from its siblings and the old kit (binding: the verifier checks these)

| | W07 `MeadowDaisy` (old kit) | Lobby `WildflowerWhite` | 059 Grass Tuft | 060 Broadleaf Fern | **061 Meadow Herb** |
| --- | --- | --- | --- | --- | --- |
| Size | 6.0 × 5.7 × 5.0 tall | 3.3 × 2.3–2.5 | 3.0 × 2.55 × 2.4 | 3.85 × 3.45 × 3.0 | **2.55 × 2.1 × 2.2 tall, W : H 1.10–1.24** |
| Flowers | three daisies, thin pointed petals (6 in the manifest note), a tiny centre | flat heads, rounded petals | none | none | **three daisies at 1.88 / 1.66 / 1.42, five broad thick blunt lozenge petals (0.46 × 0.34), a chunky bead Ø 0.40, a faceted cup** |
| Stems | slender, bowed | thin | none | stalks into a crown | **thick hex prisms Ø 0.14 with a crook under each cup; middle straight, left kinked, right arched** |
| Leaves | ~9 pointed lozenge blades, flat; a rosette | strap leaves | six tall pointed blades | lobed fronds and a lobed skirt | **≈ 17 thick faceted kites: a 5-leaf upright fan (tips z 1.3), 4 spreading / rising leaves, 4 big drooping lime kites (front and back, tips on the ground), 2 small centre diamonds, 4 small dark rim leaves** |
| Base | none shown | none | hidden cross + post, rocks | root crown and rocks | **an octagonal hub, hidden by the leaves; no rocks, no soil** |
| Colour | one leaf green, cream, golden | | three greens by blade | four greens, ochre, brown | **cream petals with a warmer base, golden bead with an orange lower band, dark-green stems and cups, lime / mid / dark leaves by role** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, the hub axis at (0, 0)). Plan azimuths: 0° = +X,
counter-clockwise, 90° = +Y (back), 270° = −Y (front).

### 2.1 Stack (binding contact chain, bottom up; every seat gap ≤ 0.03)

| Piece | Sits on / in | Contact |
| --- | --- | --- |
| Hub (one closed octagonal collar) | ground | flat underside at z 0 … −0.03 |
| Leaf-base fan (5 leaves) and ring leaves (12) | the hub's flank / top rim, or the ground for the rim leaves | each leaf's base point 0.04–0.08 inside the hub (a butt join, no boolean); rim leaves' bases may sit on the ground beside the hub (z 0 … −0.02) touching a neighbour leaf |
| Stems (3) | the hub top | stem foot 0.06–0.08 inside the hub top; no socket hole modelled in the hero (§3.7) |
| Cups (3) | the top of their stem | the stem's top end 0.05–0.08 inside the cup's bottom |
| Petals (5 per head) | the cup's top rim | each petal's base 0.03–0.05 under the bead and on / in the cup rim; never floating above it |
| Beads (3) | the cup top, among the petal bases | lower 35–45 % of the bead inside the cup / petal ring; buried ≤ 0.12 |

### 2.2 Hub (the "Leaf Base" hub; hidden in the hero)

- **8-sided collar**, **Ø 0.42 at z 0, Ø 0.36 at the top z 0.18**, the top a flat octagon. Ring radii ±5 % per vertex.
- Hidden by the leaves in every assembled view (G only; no visible base). About 32 tris.

### 2.3 Stems, cups and heads

| Head | Stem foot (x, y) on the hub top | Stem path (spine stations) | Crook | Cup bottom → top | Head centre (bead top-centre) | Face normal (az, tilt from vertical) | Ø ring |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **H_M** tall | (+0.04, +0.05) | nearly straight up, leaning back to y +0.25 at the top with a gentle bow (0.06 sag toward −Y at mid height, the side cell's curve) | at 0.88 of the stem: the cup tilts 30° toward the face normal | z 1.62 → 1.80 | **(+0.10, +0.30, 1.88)** | **az 300°, 45°** (front-right-up) | 1.12 |
| **H_R** right | (+0.07, −0.03) | a smooth arc out to the right: (0.07, −0.03, 0.18) → (0.45, −0.10, 0.95) → (0.82, −0.18, 1.40) | at 0.85: the cup turns toward +X | z 1.45 → 1.60 | **(+0.99, −0.20, 1.67)** | **az 330°, 60°** (mostly +X, a little front) | 1.08 |
| **H_L** left | (−0.06, 0.00) | rising up-left: (−0.06, 0.0, 0.18) → (−0.55, −0.05, 0.95), then a **kink** (12–18°) at z 1.0 and on to the cup | at 0.82: the cup turns toward the front-left | z 1.20 → 1.36 | **(−0.86, −0.12, 1.42)** | **az 250°, 55°** (front-left-up) | 1.08 |

- **Stems:** **hexagonal prisms, Ø 0.14** (0.15 at the foot, 0.13 under the cup), 4–5 segments along the path, flat
  faces (the sheet's flat bands), the top end inside the cup.
- **Cups (calyx):** **8-sided, Ø 0.16 at the bottom (just over the stem), Ø 0.34 at the top rim**, height 0.16–0.20; a
  shallow flat top under the bead, the outer faces in two rings (close-up 1). Axis along the head's normal.
- **Beads (centres):** **Ø 0.40**, height 0.24, seated with their top 0.12–0.14 above the petal plane at the centre;
  8-sided equator, 5–6 facets on top (front: the bead stands clearly above the petals).
- **Petals (5 per head):** **L 0.46 (radial, from r 0.09 to r 0.55), W 0.34 at 0.65 L, thickness 0.05 (0.06 at the
  crease)**; base 0.10 wide tucked under the bead. Spaced 72° round the head normal, phase varied per head (H_M 10°,
  H_R 40°, H_L 25°) so no two heads repeat; each petal **lifts 10–15° out of the head plane** (a shallow cup, the f34's
  curving petals) and is turned ±5° on its own axis; adjacent petals overlap their neighbour by 0.02–0.05 near the base
  so the ring reads closed (as the front draws) with a clear notch between the tips.
- **Why these normals (§3.4):** front ring ratios H_M ≈ .67, H_L ≈ .82, H_R ≈ .47 (sheet .67 / ≈ 1 / .5); top ratios .71
  / .57 / .50 (all three faces visible from above); the rear and r34 see three cups from behind (the sheet's). **No head
  is turned toward a camera per view.**

### 2.4 Leaves (17)

Each leaf is a closed faceted kite (§1.4) placed by its **base point** on the hub (or the ground for the rim leaves), its
**azimuth** and **pitch** (above the horizontal at the base; a gentle arch along the leaf adds 10–20° droop toward the
tip), and **roll** (rotation about its own axis: the top face stays up and outward; **never rolled toward a camera**).

| Leaf | Tier | Az | Base → tip (x, y, z) | L | W | Pitch → tip | Tone (§5) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **F1** fan centre | leaf base | 95° | hub → (−0.02, +0.38, 1.32) | 1.36 | 0.52 | 75° | mid, light tip |
| **F2** fan left | leaf base | 160° | hub → (−0.31, +0.12, 1.34) | 1.36 | 0.52 | 72° | mid, light tip |
| **F3** fan right | leaf base | 30° | hub → (+0.23, +0.15, 1.30) | 1.32 | 0.50 | 72° | light, mid base |
| **F4** fan spread left | leaf base | 182° | hub → (−1.27, −0.05, 0.81) | 1.45 | 0.52 | 35° then flattening | mid, light tip |
| **F5** fan spread right | leaf base | 358° | hub → (+1.27, −0.05, 0.84) | 1.45 | 0.52 | 35° then flattening | light, mid base |
| **N1** front-left big, drooping | ring | 240° | hub → (−0.57, −0.95, 0.02): tip on the ground | 1.25 | 0.56 | rises to z 0.55 at 0.35 L, then droops | light |
| **N2** front-right big, drooping | ring | 300° | hub → (+0.80, −0.85, 0.02) | 1.25 | 0.56 | as N1 | light |
| **N3** back-left big, drooping | ring | 125° | hub → (−0.62, +0.85, 0.03) | 1.20 | 0.54 | as N1 | light, mid base |
| **N4** back-right big, drooping | ring | 55° | hub → (+0.70, +0.82, 0.03) | 1.20 | 0.54 | as N1 | mid → light |
| **N5** inner right, rising | ring | 10° | hub → (+0.80, +0.15, 1.07) | 1.20 | 0.46 | 45° | light |
| **N6** inner left, rising | ring | 165° | hub → (−0.55, +0.25, 1.02) | 1.15 | 0.46 | 50° | mid |
| **N7** front-centre small diamond | ring | 272° | hub → (+0.02, −0.62, 0.04); its top at z 0.38 | 0.75 | 0.40 | stands up then folds down: a squat kite (L : W 1.9) | light |
| **N8** back-centre small diamond | ring | 88° | hub → (0.00, +0.60, 0.05) | 0.72 | 0.38 | as N7 | light, mid base |
| **K1** rim dark, front-left | rim | 205° | ground (−0.45, −0.25) → (−1.03, −0.40, 0.12) | 0.65 | 0.32 | 10–15°, nearly flat | dark |
| **K2** rim dark, front-right | rim | 335° | ground (+0.50, −0.20) → (+1.12, −0.42, 0.23) | 0.65 | 0.32 | 15° | dark |
| **K3** rim dark, back-left | rim | 150° | ground (−0.45, +0.30) → (−0.98, +0.62, 0.12) | 0.60 | 0.30 | 10° | dark |
| **K4** rim dark, back-right | rim | 30° | ground (+0.45, +0.30) → (+1.00, +0.62, 0.15) | 0.60 | 0.30 | 12° | dark |

- **Shape:** kite, widest at 0.45–0.55 L, tip angle 45–60° (never a needle), base 0.25 W wide where it meets the hub;
  L : W 2.1–2.7 (big leaves 2.2, fan leaves 2.6; never slimmer than 2.8), thickness 0.06 at the edges, 0.12 at the
  ridge.
- **Hierarchy check:** tips at z 1.32 / 1.34 / 1.30 (fan), 1.07 / 1.02 (rising), 0.81 / 0.84 (spread), ≈ 0 (drooping and
  rim). Front leaf top at h .60, the rosette's widest at h .1–.4 (§1.2).
- **Clearances:** no leaf more than 25 % inside another; every leaf vertex ≥ z −0.01 except the sunk rim bases; the
  drooping leaves' tips rest within 0.03 of the ground; no leaf cuts a stem by more than 0.03 (move the leaf, not the
  stem).

### 2.5 Expected extents and screen checks

- **Extents:** X −1.30 … +1.28 (F4 / F5 tips plus half-widths; H_R's ring reaches about +1.30 side-on), Y −1.05 …
  +1.00 (N1 / N2 and N3 / N4 tips plus widths; H_M's ring back to about +0.75), Z 0 … 2.20 (H_M's upper petal). Bbox
  about 2.55 × 2.05–2.15 × 2.2.
- **Checks on the renders** (floor hidden; `meas.py` with this folder's `m.py`):
  - **front_sheet (0, 5)** — governs positions:
    - W : H 1.10–1.24 (sheet 1.167); G 61.8 ± 5, W 32.5 ± 4, Y 5.7 ± 1.5; fill 0.65 ± 0.05.
    - The top profile within ±0.08 for f .1–.9; head centres at §1.2's (x, z) ±0.06 H; the three heads at clearly
      different heights (1.88 / 1.66 / 1.42).
    - Green fifths within ±6 of 29.9 / 43.3 / 20.7 / 6.1 / 0; petal fifths with ≥ 70 % above h .6.
    - Green tones light / mid / dark 31 / 40 / 29 ± 8.
  - **f34_sheet (0, 20)** (probe az −25 … +5 × e 15 / 20 / 25; keep the best; §3.2): W : H 1.21–1.35 (sheet 1.286); G
    65.6 ± 5, W 28.9 ± 4, Y 5.6 ± 1.5; tones 33 / 40 / 27 ± 8; every head shows its five petals and bead.
  - **rear_sheet (180, 5), r34_sheet (180, 20)** (probe 160 … 200): W : H 1.02–1.18; Y ≤ 1.5 % (heads from behind, the
    three cups visible); G 71–78 ± 5.
  - **side_sheet (90, 5)** (also render (270, 5) and keep the closer; §3.4): W : H 0.85–1.00; the tall stem bowing up the
    centre to H_M; at least one lower head side-on; leaves rising to both sides; fill 0.41 ± 0.06.
  - **top_sheet (0, 85)** (a near plan; also (0, 60)): content only: face-up five-petal heads with golden beads over a
    star of 12–17 radiating kite leaves; all three heads visible is fine (§3.3).

## 3. View conflicts and resolutions

### 3.1 Sheet number
- **Evidence.** The header says "62/132"; INDEX.md row 61 lists `061.png` as "Flintborn Meadow Herb Study".
- **Resolution.** Our number is 061 (file name, keys `m061_*`). Note the header in the export notes only.

### 3.2 The three-quarter views are near-frontal and near-rear, drawn from higher up
- **Evidence.** The f34 head x fractions are .22 / .56 / .87 against the front's .16 / .54 / .88; W : H 1.286 vs 1.167;
  the rosette top shows more. The r34 matches the rear the same way.
- **Resolution (decision §8.9).** `front_sheet (0, 5)` governs positions; `f34_sheet (0, 20)` governs the read and the
  shares. Probe az −25 … +5 (e 15–25), keep the best and record the camera; the same for r34 at 160 … 200.

### 3.3 The top cell draws two heads
- **Evidence.** The top shows H_M (back-right, +0.32, +0.44) and H_L (left, −0.68, −0.11) face-on with five petals each;
  H_R is missing although every other view draws three heads; the leaves radiate in a star of 12–14.
- **Resolution.** Three heads (every other view). Use the top for **plan depth only**: H_M behind the axis (y +0.30), H_L
  a little in front of it (y −0.12). Judge the top for content (face-up five-petal heads over a leaf star), not head
  count.

### 3.4 Head facing differs per view (the generator turns every head toward every camera)
- **Evidence.** H_M is drawn open toward the front (ring ratio .67), open toward the side (.59) and nearly circular from
  the top (.94): no single flat head can do all three (the squares of the three ratios sum to 1.6, more than 1). The side
  draws only two heads (H_R hidden), and puts the lower head at image right side-on; the rear draws H_R lower (1.45)
  than the front (1.67).
- **Resolution (decision §8.3).** **One fixed, coherent orientation per head** from §2.3: H_M az 300° tilt 45°, H_R az
  330° tilt 60°, H_L az 250° tilt 55°. This gives the front its three reads (open / side-on-right / open-left), the top
  three visible faces, the rear and r34 three cups from behind. The side cannot match the sheet's two-head picture with a
  coherent plan; render `side_sheet` at both 90° and 270° and keep the closer; judge it for the stem bow, the head
  heights and the leaf spread only. **Never turn a head, petal or leaf per camera** (054 / 057 lesson).

### 3.5 Five petals (text, top, exploded, parts) vs 6–7 petal shapes (front, f34)
- **Evidence.** The description and notes say five petals; the exploded and parts row label "Petal (x5)"; the top view
  draws exactly five per head (`z_top_heads.png`). The front and f34 draw 6–7 overlapping petal shapes round each bead
  (`z_fr_mid.png`, `z_f34_heads.png`).
- **Resolution (decision §8.3).** **Five broad petals per head** (W : L 0.74), overlapping their neighbours near the base
  so the ring reads full from the front. The front's extra shapes are the overlaps and the thickness bands. Alternative:
  six petals per head (+2 × 26 tris per head), if the main session wants the front's count.

### 3.6 Petal shape: pointed lozenge (parts row) vs blunt rounded (top, hero)
- **Evidence.** The parts row stands a petal upright as a lozenge with a slightly pointed top; the top and front draw
  blunt, rounded-hexagonal petal ends; the old W07 failed on "thin pointed petals" and "round petals" in turn.
- **Resolution.** A **lozenge widest at 0.65 L with a blunt chamfered end** (two tip verts 0.10 apart, or a 100–120°
  tip): broad and chunky, clearly separate tips with notches between, never round discs, never needles.

### 3.7 Stem insert: a hex socket in the base
- **Evidence.** Close-up 3 shows an octagonal collar with a hex socket and a hex stem end; in every assembled view the
  base is hidden by leaves.
- **Resolution.** The hero's hub is a **closed collar with no hole**; stems sink 0.06–0.08 into its top (a hidden butt
  join, as 059's root base). The `…LeafBase` part (§8) shows the collar; a hex recess on its top is optional (decision
  §8.6; recommended: no recess, the close-up's "no small details").

### 3.8 One stem part, three stems in the hero
- **Evidence.** "Stem (x1)" with its cup and crook; the hero has three stems of different paths.
- **Resolution.** One `stem(spec)` function builds all three from their spine (§2.3); the exported `…Stem` part is H_M's
  stem with its cup (straight with the crook at the top, as the parts row).

### 3.9 Exploded scale vs the hero
- **Resolution.** The hero governs size, lean and position; the exploded and the parts row govern each part's outline
  (petal lozenge, bead facets, cup and crook, kite L : W, the five-leaf fan) and tone role.

### 3.10 The palette's brown swatch is used nowhere
- **Evidence.** H6 `#8C653D` / P6 `#876039` matches nothing in any drawing (`brown.py`: the only brownish pixels are the
  beads' deep orange shade `#A97417`–`#BB7C04`); no soil, root or base shows.
- **Resolution (decision §8.7).** **No brown region and no soil patch.** If the main session wants the swatch used, the
  hub's lowest 0.05 band (hidden) can take `m061_soil`; it changes nothing visible.

### 3.11 "Solid colours, no texture noise" vs the user's colour rule
- **Resolution.** Leaves blended by role and position along the leaf; petals by position along the petal; beads by
  height; broad Tint per piece (0.02–0.04), never per-triangle confetti (memory `lighting-not-paint`).

### 3.12 Lighting
- The sheet is lit from the upper right (lime on the leaves' upper faces, the stems dark on their shaded front faces in
  the front and lit in the rear, warm-grey petal undersides, an orange lower band on the beads). The lighting does that;
  never paint it by facing. Render every `*_sheet` view with the studio floor hidden.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its exploded / parts-row cell

1. `petal(spec)` → one closed lozenge plate (§1.4, §2.3) in its own frame (base at the origin, along +X, top +Z).
   Check against the parts row: W : L 0.69–0.75, widest at 0.65 L, blunt end, crease, thickness.
2. `bead(spec)` → the faceted centre (§2.3). Check against the parts row's centre (round, ~10 facets showing).
3. `cup(spec)` → the 8-sided calyx (§2.3, close-up 1).
4. `stem(spec)` → a hex prism along a spine with the crook, its top end inside the cup.
5. `head(spec)` → cup + bead + 5 petals, oriented by the head normal; then `flower(spec)` = stem + head.
6. `leaf(spec)` → one closed kite with ridge and keel, arched along its length (§2.4).
7. `hub()` → the octagonal collar (§2.2).
8. `leaf_base()` → hub + F1–F5 (the parts row's fan).
9. **Hero `MeadowHerb`** = leaf base + N1–N8 + K1–K4 + three flowers, one object of closed shells.
10. **Parts shot** (0, 15) laid out like the parts row: Petal, Center, Stem, Leaf, LeafBase, gaps 0.3.
11. **Exploded shot:** the heads lifted 0.5 along their normals with the petals spread 0.2 out, the stems lifted 0.3,
    the ring leaves pulled 0.3 out along their azimuths.

Reusable code: m059's blade builder (closed ridged blade, uncommitted: copy, don't import) and m060's leaf / sprig
functions for kite solids; `m047._Solids`, `shells_report`, `contact_report`, `bury_report` (committed: import).

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** three white five-petal daisies with golden beads at three heights on thick stems over a broad
   rosette of faceted kites; 1.17 × as wide as tall.
2. **front_sheet / f34_sheet** per §2.5 (shares, fill, W : H, top profile, head centres, fifths, tones).
3. **rear / r34 / side / top** per §2.5.
4. **Close-up renders:**
   - `head_under` (0, −35) below H_M against close-up 1: the faceted cup under the petal ring, the stem entering it.
   - `junction_cu` low and close on the rosette centre against close-up 2: leaf bases crowding in with plain joins.
   - `base_part` on the LeafBase part from below (0, −60) against close-up 3: the octagonal collar.
   - `edge_side` (90, 0) and (0, 0): every petal and leaf shows thickness (≥ 0.05 on screen in studs).
   - `thumb`: the front at about 120 px tall: each head still reads as a five-petal star with a yellow dot; the rosette
     shows separate pointed tips.
   - **`spin` contact sheet: az 0 / 45 / 90 / 135 / 180 / 225 / 270 / 315 at e 10.** In every frame the heads read as
     flowers (no petal ring reduced to a line in more than one head at once), the leaves as faceted kites (not spikes,
     not balls). This is the 054 / 057 lesson.
5. **Contact counts** (§6): floating shells 0; buried 0.
6. **Hero size** per §2.5, plus a **scale shot** with a 5.5-stud marker beside the herb (the top at 0.40 of the marker)
   and 059 / 060 beside it if they are in the kit file.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Petals (6-vert outline + crease, closed) | 15 | 22–28 | 330–420 |
| Beads (8-ring + 5-ring + cap + bottom) | 3 | 30–40 | 90–120 |
| Cups (8-sided, 2 rings, closed) | 3 | 28–32 | 84–96 |
| Stems (6-sided, 4–5 segments, capped) | 3 | 50–64 | 150–190 |
| Leaves, big / fan / rising (kite + ridge + keel, 2 stations) | 13 | 24–32 | 310–415 |
| Rim leaves (simpler kite) | 4 | 16–20 | 64–80 |
| Hub | 1 | 28–32 | 30 |
| **Hero** | | | **about 1060–1350; aim ≤ 1250; ceiling 1400** |
| Parts: Petal / Center / Stem / Leaf / LeafBase | | | 26 / 36 / 90 / 30 / 190 |

- **Over budget?** First the rim leaves to 12 tris, then the beads to 24, then one spine segment per stem. **Never** thin
  the petals or leaves into cards or slivers to save triangles.
- **Lean alternative** (decision §8.14): about 900 tris with 14 leaves (drop K3 / K4 and N8) and 20-tri petals.

### 4.4 What to do better than W07's `MeadowDaisy` and recent foliage

| Earlier | This one |
| --- | --- |
| W07: thin pointed petals, then round petals, then petals fused into a pentagon disc | five broad blunt lozenges (W : L 0.74) with thickness and a crease, overlapping near the base with clear notches at the tips |
| W07: tiny centre | a bead Ø 0.40 (0.36 of the head) standing 0.12 above the petals |
| W07: flat leaves; a dense dark rosette | closed kites 0.06–0.12 thick, lime in front and on top, dark only at the rim and the bases |
| W07: 5.0 tall (a giant daisy) | 2.2 tall, knee height |
| 054 / 057: cards turned toward the front / rear cameras read as balls with spikes from the sides | every leaf and head placed by growth (azimuth, pitch, normal), never per camera; a `spin` contact sheet at eight azimuths |
| 047 r1: spiky plants | kite tips 45–60°, petal tips blunt |
| 035 / 036 / 046: floating or buried dressing | every petal on its cup, every cup on its stem, every stem and leaf in the hub or on the ground; counts reported |

### 4.5 Stages 2 and 3
- **Stage 2:**
  - Every shell closed and manifold, **0 bowties** (likely at petal tips, kite tips and the hub top).
  - **0 winding errors per shell** (`bmesh.ops.recalc_face_normals` per shell, then `m047.shells_report`).
  - No zero-area faces; corners ≥ 3°; no n-gons except the hub's flat top and bottom (triangulate if the audit asks).
  - Origin at the bottom centre, transforms applied.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box)

| Swatch | Header box → hex (HSV) | Palette-panel hex (HSV) | Use |
| --- | --- | --- | --- |
| 1 cream | H1 `#F7F1E4` (41°, .08, .97) | P1 `#EFE5CF` (41°, .13, .94) | petals (`petal`; P1 → `petal_base`) |
| 2 yellow | H2 `#FDC815` (46°, .92, .99) | P2 `#FDC611` (46°, .93, .99) | beads (`centre`) |
| 3 lime | H3 `#9EC638` (77°, .72, .78) | P3 `#A1C637` (76°, .72, .78) | light leaves (`leaf_light`) |
| 4 mid green | H4 `#659A3F` (95°, .59, .60) | P4 `#5D933A` (96°, .61, .58) | leaf bodies (`leaf_mid`) |
| 5 dark green | H5 `#507932` (95°, .59, .47) | P5 `#49722C` (95°, .61, .45) | stems, cups, rim leaves (`stem`, `leaf_dark`) |
| 6 brown | H6 `#8C653D` (30°, .56, .55) | P6 `#876039` (30°, .58, .53) | unused (§3.10) |

### 5.2 Rendered regions (`samp.py`; median / lit quartile / shade quartile)

| Region | Median | Lit Q | Shade Q |
| --- | --- | --- | --- |
| All green: front / f34 / rear / side / r34 / top | `#598D1D` (88°, .79, .55) / `#5E921F` / `#64981C` / `#4D801B` / `#61961D` / `#74A81F` | `#A3CF37` / `#A5D037` | `#2A5312` / `#2B5511` |
| Green light tone: front / f34 / rear | `#9ECB34` (78°, .74, .80) / `#9ECB33` / `#97C62E` | `#B2D940` / `#B3DA41` | `#88BA28` |
| Green mid tone: front / f34 / rear | `#588B1B` (87°, .81, .55) / `#598E1C` / `#60931A` | `#72A51F` / `#71A61F` | `#417318` |
| Green dark tone: front / f34 / rear | `#2C5712` (97°, .79, .34) / `#2C5712` / `#2D580E` | `#376716` | `#1C3F0D` |
| Tone shares (light / mid / dark %) | front 31 / 40 / 29; f34 33 / 40 / 27; rear 28 / 51 / 21; r34 31 / 45 / 23; side 17 / 51 / 32; top 35 / 42 / 23 | | |
| f34 leaves: front-left big / front-right big / spread-left / spread-right / upright left / rim dark | `#8ABA2A` (80°) / `#6E9227` / `#54891E` (90°) / `#96C630` (79°) / `#5B911E` (88°) / `#4D832B` (97°) | `#B4DB41` / `#AAD338` / `#6FA327` / `#A1CD35` / `#7CAF24` / `#5E962F` | |
| Leaf part / leaf-base part / exploded leaf base / cu2 junction | `#7AAF2B` (84°, .76, .69) / `#7BAF21` / `#6AA025` / `#548913` | `#9CCC3A` / `#A4CF38` / `#94C52F` / `#7CAF1E` | `#60941D` / `#4A7C12` |
| Stems: parts / exploded / f34 mid / front mid (shaded side) / side / rear (lit side) | `#477A1D` (93°, .76, .48) / `#497B1F` / `#366518` / `#2E5A15` / `#73A51B` / `#78AC1E` | `#81B62D` / `#83B435` | `#386613` |
| Cups: cu1 / rear H_M / r34 H_M | `#3A6C11` (93°, .84, .42) / `#537B0D` (82°) / `#598807` | `#669E15` / `#6BA10E` / `#7EA007` | `#2A580F` |
| Collar / socket / plug (cu3) | `#598E2E` (93°, .68, .56) / `#1F3D1A` / `#437229` | `#7BAE4C` | `#2D571D` |
| Petals: front / f34 / side / top / cu1 / parts | `#F5EFDF` (44°, .09, .96) / `#F9F2E3` / `#F8F2E1` / `#F6ECDC` / `#F1EDE4` / `#F4F0E5` | `#FEFDF5` / `#FEFEF5` | `#C4B7A0` / `#C4B59E` (warm-grey shade) |
| Petals from behind: rear / r34 | `#CBBB9B` (40°, .24, .80) / `#C6B798` | `#F9F6EB` | `#B4A379` |
| Beads: front / f34 / side / top / f34 H_M | `#FCCE0B` (49°, .96, .99) / `#FDD30B` / `#FDDF18` / `#F3B906` / `#FDE010` | `#FEE319` | `#D59104` / `#DA9303` |
| Bead parts: exploded / parts | `#F7BC06` (45°, .98, .97) / `#FBC508` | `#FED814` / `#FED40D` | `#B97702` / `#C08002` |
| Cast shadow (not modelled) | warm grey, s < 0.07 | | |

### 5.3 How the colour works

- **Leaves: three greens by role and by position along the leaf** (never facing):
  - **Role:** the big drooping front / back kites N1–N4, the small diamonds N7 / N8, the rising right leaf N5, the right
    fan leaf F3 and the right spread F5 are **light** (lime); the fan F1 / F2, the left spread F4 and the left rising N6
    are **mid** with light tips; the rim leaves K1–K4 are **dark**.
  - **Along the leaf:** the lowest 0–0.2 L one step deeper (light → mid, mid → dark, dark → deep), the outer 0.6–1.0 L
    one step lighter on mid leaves. A whole cross-band of the leaf (both halves, ridge and edges) takes one blend step,
    so the lit-half / shaded-half contrast comes only from the light (the ridge V).
- **Stems and cups:** `stem` (dark-mid green) along the stem, the lowest 0.2 a step deeper (`leaf_dark`) where it enters
  the leaves; cups `stem` with their top rim one step lighter (`leaf_mid`, close-up 1's lit rim), by position.
- **Petals:** `petal` cream body; the inner 0–0.25 L blends to `petal_base` (P1, slightly warmer and deeper) by position
  along the petal. The warm-grey undersides on the sheet are shade, not paint.
- **Beads:** `centre` golden on the upper 60 % (by height in the bead's own frame); `centre_deep` (orange-gold) on the
  lower band (the exploded / parts beads and the sheet's shade band). Blend over one ring.
- **Hub:** `leaf_dark` (hidden).
- **Hues stay apart:** petal 40–48° at s ≤ 0.12; centre 45–52° at s ≥ 0.90; centre_deep 40–45°; leaf light 76–80°;
  leaf mid 86–92°; stem 90–96°; leaf dark 94–100°.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians where the sheet gives them, swatches where it doesn't. `K.sample` kinds:
`"vivid"` for the light leaf and the centre keys, `"green"` for mid / dark / stem, `"stone"` for the petals (pale,
low-saturation; check with `M.raw_sample` on the swatch too).

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m061_petal` | petal median `#F5EFDF` ± 10 (lit `#FEFDF5`; start H1 `#F7F1E4`) | 40–48°, ≤ 0.12, never pure white, never pink | petal bodies | rough 0.8, low spec |
| `m061_petal_base` | P1 `#EFE5CF` ± 10 | 38–44°, 0.12–0.16 | inner 0–0.25 L of each petal | rough 0.8 |
| `m061_centre` | bead median `#FCCE0B` ± 12 (start H2 `#FDC815`) | 47–52°, ≥ 0.90 | upper 60 % of each bead | rough 0.6, a little spec |
| `m061_centre_deep` | parts bead `#F7BC06` ± 12 | 42–46°, ≥ 0.95 | lower band of each bead | rough 0.6 |
| `m061_leaf_light` | light-tone median `#9ECB34` ± 12 (start H3 `#9EC638`) | 76–80°, 0.70–0.80 | light leaves; light tips | rough 0.8, low spec |
| `m061_leaf_mid` | mid-tone median `#598E1C` ± 12, toward the parts leaf `#7AAF2B` lit (start H4 `#659A3F`) | 86–92°, 0.70–0.82 | mid leaves; light leaves' bases; cup rims | rough 0.85 |
| `m061_leaf_dark` | rim leaf `#4D832B` ± 12 (start H5 `#507932`) | 94–100°, 0.60–0.72 | rim leaves; mid leaves' bases; stem feet; hub | rough 0.85 |
| `m061_stem` | parts / exploded stem `#487A1E` ± 12 | 90–96°, 0.72–0.80 | stems, cups | rough 0.85 |

**Calibration warnings:**
- **The kit studio lights both halves** (042, 047, 054): calibrate the greens to the tone medians and parts medians,
  then check the tone shares on the herb's own renders (front 31 / 40 / 29 ± 8). Record the lit-shade bias.
- **Greens must not lean yellow or olive** (047 "plants too yellow"): `leaf_mid` ≥ 86°, `stem` ≥ 90°; only
  `leaf_light` is lime (76–80°, never below 74°); the front all-green median within 15 of `#598D1D`.
- **Contrast:** the light leaves clearly lighter than the stems (W07 failed on a dark rosette); the stems read dark
  against the lime front leaves as in the front cell.
- **Petals cream, not white and not grey:** `#F5EFDF` median; R ≥ G ≥ B; the warm-grey shade comes from the light.
- **Beads golden, not orange or lemon:** 47–52° on the median; the orange only in the lower band.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Leaves:** per cross-band along the leaf (base → tip), by role (§5.3).
- **Petals:** base band → body, by fraction of L.
- **Stems:** foot band → body by height; cup body → rim by position.
- **Beads:** by height in the bead frame.
- **Hard edges only** where materials meet: petal | bead, petal | cup, cup | bead.

### 5.6 Texture (Tint) and finish
- **Tint:** leaves 0.03 per leaf + 0.02 per band; petals 0.02 per petal (so the five petals of a head differ a little);
  beads 0.02; stems 0.02. Broad, never per-triangle.
- **Finish:** greens 0.8–0.85 rough, low spec (`set_colour(low_spec=True)`); petals 0.8; beads 0.6; no metal, no
  emission.

### 5.7 Re-measure (final renders against the sheet, same masks)
- **Green:** front median within 15 of `#598D1D`; light-tone median within 12 of `#9ECB34`; tone shares ± 8.
- **Petals:** front W median within 10 of `#F5EFDF`, lit quartile within 10 of `#FEFDF5`.
- **Beads:** front Y median within 12 of `#FCCE0B`.
- **Stems:** the parts-shot stem within 12 of `#477A1D`.
- **Shares** per §2.5.

## 6. Joins and contact (no floating dressing, no buried dressing)

- **Shells:** each petal, bead, cup, stem, leaf and the hub is its own closed shell, all in one hero object.
- **Flower chain:** petal → cup rim / bead (each petal's base within 0.03 of the cup rim and under the bead, ≤ 0.05
  inside it) → cup → stem (the stem's top 0.05–0.08 inside the cup, axis within 0.02 of the cup axis) → hub (stem foot
  0.06–0.08 inside) → ground. **No petal floating** off its head: report each petal's seat.
- **Leaf chain:** leaf → hub (base point 0.04–0.08 inside) → ground; rim leaves → ground (base sunk ≤ 0.02) and touching
  a neighbour leaf. Drooping leaf tips rest within 0.03 of the ground, never below z 0.
- **No buried dressing:** ≤ 0.08 of any stem inside a cup; no petal more than 0.05 inside the bead or cup beyond its
  seat; no leaf more than 25 % inside another; no leaf cutting a stem by more than 0.03.
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**. Chains: petal → cup / bead → stem →
  hub → ground; leaf → hub → ground; rim leaf → ground.
- **Count buried shells** (STAGES; 046, 047 round 2): **0 dressing shells more than 0.05 inside a neighbour** (seats
  excepted at their stated depths). Use `m047._Solids` (hub, beads, cups added as built).
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.
- **Reports:** reuse `m047.shells_report`, `contact_report` and `bury_report` (committed; import, don't edit).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no pollen, no particles, no wind marks. The cast shadow is the
render's.

- **Stage 5 (lighting): skip, and record why.** No emission, no lights. Studio notes (Requires Manual Validation):
  - the petals stay cream under the game sun (not blown-out white, not grey);
  - the beads stay golden, the lime leaves lime and the stems dark green (not olive, not black).
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** The old W07 `MeadowDaisy` had none either. A pollen
  mote or wind sway would be a Studio-side choice, not a socket (decision §8.11).
- **Collision:** **hero `none`** (CanCollide, CanQuery and CanTouch off): walk-through meadow cover, as the old W07 hero.
  Every part `none` (decision §8.8).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched all 2431 names in `art/roblox/kit/*/manifest.json` and
`art/roblox/kit/wip/*/manifest.json`, the builders and the repo text (`git grep`) for Daisy, Herb, Meadow, Petal and the
candidates:
- **W07:** `MeadowDaisy`, `MeadowDaisyCenter`, `…Leaf`, `…Petal`, `…Stem`, `…SingleWhite`, `…WhiteClump`,
  `…YellowClump`; `Wildflowers*`; `GrassTuft*`; `GroundScatter*`.
- **R05:** `HealingHerb`, `HealingHerbBud`, `HealingHerbLeaf`, `HealingHerbRootPlug`, `HealingHerbSprig`. **M018:**
  `HerbShrub*`. **Lobby:** `BroadLeafHerb`, `WildflowerWhite`, `FernLeafy`.
- **`MeadowHerb`, `MeadowHerbPetal`, `MeadowHerbCenter`, `MeadowHerbStem`, `MeadowHerbLeaf`, `MeadowHerbLeafBase` and
  `m061` occur nowhere** (repo text, manifests, builders), no owned name is a substring of them and none of them is a
  substring of an owned name.

| Object | Part | Why |
| --- | --- | --- |
| `MeadowHerb` | hero: hub, 17 leaves, 3 stems, 3 cups, 3 beads, 15 petals | the sheet's title; free |
| `MeadowHerbPetal` | "Petal (x5)": one petal | the label |
| `MeadowHerbCenter` | "Center (x1)": one bead | the label (the sheet's spelling, as W07) |
| `MeadowHerbStem` | "Stem (x1)": H_M's stem with its cup and crook | the label |
| `MeadowHerbLeaf` | "Leaf (x1)": one big kite (N1's shape) | the label |
| `MeadowHerbLeafBase` | "Leaf Base (x1)": hub + F1–F5 | the label |

- Palette keys `m061_*` (§5.4). Collection `Kit/M061 Meadow Herb`. No sockets (§7).

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **2.2 tall, 2.55 × 2.1 footprint** (recommended: 0.40 C, knee height, just under 059's 2.4; heads Ø
   1.1). Alternatives: 1.8 (0.33 C; petals 0.38, stems 0.11) or 2.6 (crowds 059).
2. **Names (§8):** **`MeadowHerb` and the five parts above** (recommended). Not `MeadowDaisy*`, `HealingHerb*` or
   `HerbShrub*`.
3. **Heads (§2.3, §3.4, §3.5):** **three heads at 1.88 / 1.66 / 1.42 with fixed growth normals (H_M az 300° 45°, H_R
   330° 60°, H_L 250° 55°), five broad blunt petals each** (recommended). Alternative: six petals per head (the front's
   apparent count).
4. **Leaves (§2.4):** **17 closed kites: a 5-leaf fan, 4 big drooping lime kites (front and back), 2 rising, 2 small
   diamonds, 4 dark rim leaves; placed by growth, never rolled toward a camera** (recommended).
5. **Stems (§2.3, §3.8):** **thick hex prisms Ø 0.14 with a crook under a faceted 8-sided cup; middle straight with a
   bow, left kinked, right arched** (recommended).
6. **Base (§2.2, §3.7):** **a closed octagonal hub, hidden in the hero; no socket hole** (recommended), or a hex recess on
   the `LeafBase` part only.
7. **Ground and brown (§3.10):** **no soil patch, brown swatch unused** (recommended), or a hidden `m061_soil` band on
   the hub.
8. **Collision (§7):** **`none` on the hero and every part** (recommended).
9. **Comparison cameras (§3.2–§3.4):** **`front_sheet (0, 5)` governs positions, `f34_sheet (0, 20)` the read** (probe
   az −25 … +5, e 15–25); `rear_sheet (180, 5)`, `r34_sheet (180, 20)` (probe 160 … 200); `side_sheet` at 90 and 270
   (keep the closer); `top_sheet (0, 85)` content only; extras: parts shot, exploded, `head_under`, `junction_cu`,
   `base_part`, `edge_side`, `thumb`, **`spin` (eight azimuths)**, scale shot. Floor hidden in every `*_sheet` render.
10. **Sinking (origin):** **hub and rim leaves sink at most 0.03**; the origin within 0.03 of the ground; record the
    origin's offset from the hub axis (≤ 0.10) (recommended).
11. **VFX (§7):** **none; stages 5 and 6 skipped and recorded** (recommended).
12. **Exported parts (§8):** **the hero plus the five parts of the "PARTS (ISOLATED)" row** (recommended), or the hero
    plus Petal and LeafBase only.
13. **Colour (§5):** **petals `#F5EFDF` with a `#EFE5CF` base, beads `#FCCE0B` over `#F7BC06`, leaves lime `#9ECB34` /
    mid `#598E1C` / dark `#4D832B` by role, stems and cups `#487A1E`; front all-green median `#598D1D`, tone shares 31 /
    40 / 29** (recommended).
14. **Budget (§4.3):** **small prop extended: hero ceiling 1400, planned 1100–1250; each part under 1000** (recommended:
    three chunky heads and 17 closed kites need it; W07 used 852 with thin parts). Alternative: a lean 900 (14 leaves,
    20-tri petals) if the herb is scattered very densely.

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **Parts turned toward the cameras (054 r2 "balls with spikes" from the sides; 057 r1 "three balls on sticks").**
   - Every head, petal and leaf placed by its growth (azimuth, pitch, normal); no per-camera roll.
   - The `spin` contact sheet at eight azimuths: in each frame at most one head reads edge-on, leaves read as kites.
2. **Thin pointed petals, round discs or a fused pentagon (W07 builds 1–6).** Five lozenges W : L 0.69–0.75, blunt
   tips with notches between, thickness 0.05 visible in `edge_side`; the ring reads closed near the bead and starred
   at the tips.
3. **A tiny centre (W07).** Bead Ø 0.40, standing 0.12–0.14 above the petals; Y ≈ 5.7 % of the front.
4. **Flat cards (WorldModeling §6.1, §17.2 "leaves have side-visible volume").** Every leaf a closed kite 0.06–0.12
   thick with a ridge V; ≥ 0.05 on screen in `edge_side`.
5. **Spiky or hedgehog rosette (047 r1; WorldModeling §18 "grass resembles a hedgehog").** Kite tips 45–60°, widest at
   the middle, a clear tier hierarchy (fan 1.3, rising 1.05, spread 0.8, drooping and rim on the ground), not a radial
   ring of identical spikes.
6. **A dark, dense rosette (W07).** Front light share 31 ± 8 %; the big front leaves lime; dark only at the rim and the
   leaf bases.
7. **Thin or wiry stems (WorldModeling §18 "tiny details vanish").** Ø 0.14 hex prisms, 0.07 H on the front render.
8. **Floating petals or heads (STAGES; 035 / 036).** Every petal on its cup / under its bead, every cup on its stem,
   every stem in the hub; floating shells 0, counted and reported.
9. **Buried parts (046; 047 r2).** Stem tops ≤ 0.08 in the cup, beads ≤ 45 % sunk, no leaf more than 25 % inside
   another; ray parity after the final placement: 0 shells more than 0.05 inside.
10. **Leaves cutting the ground or stems.** No vertex below z −0.01 except the sunk bases; drooping tips rest within
    0.03; no leaf cuts a stem by more than 0.03.
11. **Yellow / olive greens (047), white-grey petals, orange beads.** `leaf_mid` ≥ 86°, `stem` ≥ 90°; petals cream
    `#F5EFDF`; beads 47–52°.
12. **Colour by facing (042 ruling; 054 m9).** Tones by leaf role and position along the leaf; `K.check` facing
    correlation < 0.5 per material.
13. **Winding (044) and bowties.** 0 faces wound against their neighbours per shell; petal and kite tips checked for
    bowties; corners ≥ 3°.
14. **Oversize.** 2.2 tall, not the old kit's 5.0; a scale shot with the 5.5-stud marker.
15. **Origin below the ground.** Sink nothing more than 0.03.
16. **Names and scope.**
    - No `MeadowDaisy*`, `HealingHerb*` or `HerbShrub*` names.
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit the frozen shared helpers or other models' builders: import from the committed ones (`m047`, `m049`,
      `m053`, `m055`, `m056`); copy from `m054` / `m057` / `m058` / `m059` / `m060` if they are still uncommitted.
    - Don't touch other models' collections.

## Decisions (main session, 2026-10-30)
All 14 recommendations are accepted. The open questions are ruled as follows:
1. **Size.** 2.2 tall with a 2.55 × 2.1 footprint, knee-high, just under 059.
2. **Names.** `MeadowHerb` plus the five parts, keys `m061_*`, collection `Kit/M061 Meadow Herb`. Never `MeadowDaisy*`.
3. **Heads.**
   - Three heads, each with **five** petals that overlap at the base. The text, top, exploded and parts row all govern.
   - Petals are broad, thick and blunt, never thin or pointed. The centre is chunky.
   - Fixed growth facings are confirmed. The heads must read well in the front and f34 views and must not vanish edge-on from the sides: check the eight-azimuth `spin` sheet.
4. **Leaves.** Seventeen kites placed by growth and never rolled toward a camera. They are closed solids with thickness. The rosette reads from all eight azimuths (STAGES "Foliage reads from every azimuth").
5. **Stems.** Hex prisms of Ø 0.14 with the crook and cup.
6. **Base.** A plain closed hub with **no hex socket**, on the part as well.
7. **Ground.** No soil patch; the brown swatch is unused.
8. **Collision.** `none` everywhere.
9. **Cameras.** As recommended, including the eight-azimuth `spin` sheet.
10. **Sinking.** At most 0.03. Nothing floats and nothing is buried: petals seat on the cup, the cup on the stem, and stems and leaves on the hub.
11. **VFX.** None; stages 5 and 6 skipped and recorded.
12. **Exports.** The hero plus five parts.
13. **Colour.**
    - Use the colours as listed, by role and by position along each piece, **never by facing**.
    - Petals are warm white, not grey or blue.
    - The rosette is not dark overall, which was W07's fault.
14. **Budget.** Small-prop extended: hero ceiling 1400 (plan 1100–1250), every part under 1000. Accepted because thick petals and 17 solid leaves need the tris.
