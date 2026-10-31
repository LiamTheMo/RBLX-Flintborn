# 059 Grass Tuft — spec

Reference: `art/blender/assets/references/059.png` (1024 × 1536 px). INDEX.md row 59: "Flintborn grass tuft model
study". The sheet's own header reads **"PAGE 61/132"** (top left) and "FLINTBORN — INDIVIDUAL MODEL STUDY" (top right),
title **"GRASS TUFT"** (our number is INDEX's 059, §3.1).
Builder: `art/blender/kit/mcp/m059.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows no effect** (§7). This is a
**ground-foliage asset that will be repeated many times**, so it is budgeted as a small prop (§4.3, decision §8.14), and
the grass rules of WorldModeling §6.2 / §18 apply: broad, thick, pointed blades in a tall / medium / short hierarchy
spreading from one root, never a hedgehog of identical spikes.

Sheet text (paraphrased):
- **Title block (top left):** "GRASS TUFT"; subtitle: a broad-leaf grass clump with five solid blades. Description: a
  simple ground-foliage asset of five broad, angular leaves plus a few small stones, made for a clear silhouette and
  readable shapes in a stylised low-poly world.
- **"MATERIAL PALETTE"** (left, four swatches): Grass Dark, Grass Mid, Grass Light, Soil / Rock.
- **"ASSEMBLED VIEWS":** "FRONT THREE-QUARTER", "REAR THREE-QUARTER".
- **"ORTHOGRAPHIC VIEWS (CONSISTENT MODEL)":** "FRONT", "SIDE (RIGHT)", "REAR", "TOP".
- **"EXPLODED CONSTRUCTION (PARTS & ASSEMBLY)":** labels "Blade 1 (Center, Tallest)", "Blade 2 (Left Tall)", "Blade 3
  (Right Tall)", "Blade 4 (Left Short)", "Blade 5 (Right Short)", "Root Base (5-way join)", "Rock A (Large)", "Rock B
  (Medium)", "Rock C (Small)". Drawn: **six** blades (an unlabelled narrow dark blade between Blade 2 and Blade 1), each
  dashed to a face of a brown cross-shaped root base with an upright post; two grey rocks and two small tan pebbles
  (Rock C is the right-hand one; an unlabelled twin sits by Rock A).
- **"ASSEMBLED (EXPLODED PREVIEW)":** the same six blades lifted over the root base, plus **two short chunky leaves**
  (one over Rock A, one over Rock B) dashed down to the rocks; one tan pebble beside the root.
- **"CONSTRUCTION CLOSE-UPS":**
  1. "Base Detail (Underside)": the root base from below: chunky octagonal arms radiating from a hub with a hexagonal
     recess underneath; callouts say the ends are flat joining surfaces for the blades, and the geometry is simple and
     chunky.
  2. "Leaf Blade Detail": one blade tip: broad flat faces (a lime face and a darker face meeting at a ridge) and a
     consistent thickness.
  3. "Root and Rock Junction": the leaves meet at the central base (a brown block shows between them); rocks sit on the
     ground around the base, not attached to it.
- **"MODELING NOTES (GUIDELINES)":** five leaf blades around a small root base; broad angular leaves with clean flat-shaded
  faces; one large, one medium and one small rock round the base; geometry simple, chunky and readable; clean solid
  colours, no textures or noise; consistent silhouette and proportions across views.
- **"KEY PARTS (FOR REUSE)":** Blade 1 (Center), Blade 2 (Left Tall), Blade 3 (Right Tall), Blade 4 (Left Short), Blade 5
  (Right Short), Root Base, Rock A (Large), Rock B (Medium), Rock C (Small).
- **Game context and the old kit:**
  - **W07 row 1 `GrassTuft`** (`art/blender/scripts/kit/W07/grass_tuft.py`; manifest `art/roblox/kit/W07/manifest.json`)
    is the old kit's take on this sheet: about 6.5 × 6.9 footprint × 4.7 tall in the manifest, 312 tris, budget 800,
    collision `none` (CanCollide off), no VFX. Its notes: "eight wide faceted creased blades arching outward, small
    rocks"; its builder makes 5 main + 2 low blades from 6-sided ridged prisms on a 5-fin root stub plus 3 pebbles.
    `MODEL_PROGRESS.md` row 71 says: "few flat paddle blades (ref 5+ tall pointed)". Variants `GrassTuftDry`,
    `…RootBase`, `…ShortWide`, `…SingleBlade`, `…TallPointed`, `…ThreeBladeClump`. **W07 owns every `GrassTuft*`
    name** (§8).
  - **Related:** the lobby's `GrassTuftLarge` (3 × 2) and `GrassClumpSmall` (2 × 1.4) in `build_05_trees_plants.py`; the
    old meadow grasses V01 `BluegrassClump` (5.6 × 4.2 tall) and `FieldSedge` (4.4 × 4.0); the pointed lime dressing
    tufts of 047, 054 and 055; 058 Low Bush (4.5 tall). §1.5 keeps 059 apart from them.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Paper `#F9F6EC` (249, 246,
236), tolerance 12. Measured grey rules: page frame x 15 / 1008; assembled frame y 37 / 433; ortho header y 471 / 497,
frame bottom y 705, cell dividers x 269, 507, 758–759; exploded frame y 742–743 / 1145, divider x 631; close-ups y
1182–1183 / 1393, dividers x 329, 614; notes / key parts y 1406–1407 / 1521, divider x 554 | 562.
- **Cells** (`m.V`, `m.X` in the study folder): f34 (200,70,615,405); r34 (615,70,1008,405); front (16,498,268,704);
  side (270,498,506,704); rear (508,498,757,704); top (760,498,1007,704); exploded (16,744,630,1144); exploded preview
  "explA" (632,744,1007,1144); cu1 "base underside" (16,1184,328,1392); cu2 "leaf blade" (330,1184,613,1392); cu3 "root
  and rock" (615,1184,1007,1392); key parts row (563,1430,1007,1490).
- **Blanked text** before measuring: (15,37,335,150) title, (15,150,214,262) and (15,262,200,433) description and
  palette, (300,400,500,425) and (720,400,920,425) the assembled labels.
- **Swatches** (inner boxes, sd ≤ 4.1): GRASS DARK (35,307,56,327), GRASS MID (35,336,56,357), GRASS LIGHT
  (35,366,56,387), SOIL / ROCK (35,396,56,415).
- **Masks** are `cls9()` and `silhouette()` in `m.py` (HSV, h in degrees, assigned in this order):
  - **G**, green blades: h 50–180, s ≥ 0.25, v ≥ 0.08.
  - **T**, brown (root base, tan pebbles): h < 50, s ≥ 0.25, v ≥ 0.15.
  - **X**, cast shadow: s < 0.25 with v ≥ 0.88, or s < 0.055 with v ≥ 0.66 (the shadow is neutral grey, s ≈ 0.02).
  - **R**, grey rock: any other s < 0.25, v ≥ 0.25 (the rocks are warm grey, s 0.08–0.17).
  - **O**, other non-paper (outlines, near-black gaps). Silhouette = G ∪ T ∪ R ∪ (O not within 2 px of X).
  - **Limit.** In the top cell the contact shadow under the blades is darker (v 0.5–0.66, s 0.07–0.10) and falls into R,
    so the top's R share (14 %) overstates the rocks; count rocks there by blob (§1.2). Apply the same masks to our
    renders, floor hidden, so the comparison stays fair.
  - **Leaf tones:** light = h < 80 and v ≥ 0.55; dark = (h ≥ 93 or v < 0.45) and not light; mid = the rest.

**Scratch study material** (no Blender) in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m059_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Pillow + numpy).
- **Helpers:** `m.py` (boxes, `cls9`, `silhouette`, `hsv`), `zoom.py` (`zoom.py x0 y0 x1 y1 scale out.png [grid]`),
  `mont.py`, `probe.py` (`probe.py x,y …`), `comps.py` (`label()`).
- **Measurements:** `measure.py` → `measure_out.txt` (bbox, W : H, shares, fill, top profile, widths per height, fifths);
  `samp.py` → `samp_out.txt` (green tones per view and per band, rock and brown medians); `samp2.py` → `samp2_out.txt`
  (root base, pebbles and rocks per cell); `sw.py` (swatches); `comps.py` → `comps_out.txt` (rock / pebble blobs per
  view); `expl.py` → `expl_out.txt` (exploded and parts-row blades: length, width, L : W, width profile, tone);
  `tips.py` → `tips_out.txt` (outline runs per height).
- **Zooms:** `z_f34.png`, `z_r34.png`, `z_ortho1.png` (front, side), `z_ortho2.png` (rear, top), `z_front.png`,
  `z_side.png`, `z_rear.png`, `z_top.png` (4×), `z_expl.png`, `z_explA.png`, `z_cu.png`, `z_parts.png`, `z_pal.png`;
  class maps `cls_*.png`, `cls_mont1.png` (f34, r34), `cls_mont2.png` (front, side, rear, top).
- **On our renders:** copy 054's or 058's `meas.py` and point it at this folder's `m.py` (paper `#F9F6EC`, `cls9`,
  `silhouette`).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** small prop / repeated ground foliage, with its own dressing (root base, rocks). **Budget: hero
  ceiling 900 tris, plan about 550–700; every part under 1000** (decision §8.14; the old W07 `GrassTuft` had an 800
  budget and 312 tris; WorldModeling §16 puts a tuft at 40–160, but this sheet asks for six chunky closed blades, a root
  base and four rocks).
- **Overall read (check this first).** A **fan of six broad, pointed, faceted green blades** rising from one hidden
  root, leaning out at different angles, with **three short chunky leaves** low at the foot, **two warm-grey faceted
  rocks** (a large one front-left, a medium one right) and **two small tan pebbles** in front.
  - **Blade hierarchy (front, left → right):** Blade 4 long and low to the far left (dark), Blade 2 tall to the left
    (lime face), the narrow dark Blade 6 behind it, **Blade 1 the tallest, right of centre, leaning right** (lime / mid),
    Blade 3 to the right (dark-mid), Blade 5 long and lowest to the far right (lime).
  - **Blades are lanceolate solids:** a flat cut base, widening to the middle, then tapering to a pointed tip; each has
    a ridge down its face (a lime face and a darker face meet there) and visible thickness; one or two gentle bends.
    L : W 2.3–3.7 (exploded), so they are **broad leaves, not grass needles**.
  - It reads **green over a little stone**: in the front, green 90 %, grey rock 8 %, brown 1.3 % (pebbles only; the
    root base is hidden in every assembled view).
  - **About 1.26 × as wide as tall** in the front (f34 1.25, r34 1.25, rear 1.38), 1.06 from the side; **slightly oval in
    plan** (top W : D 1.14), and the plan reads as a **five-pointed star** of broad leaves round the centre.
- **Focal silhouettes, in order:**
  1. The fan: the tallest tip (Blade 1) at f .7 of the width (h 1.0), the second peak (Blade 6) at f .38 (h .89) and
     Blade 2 at f .23 (h .83); the outer blades step down to h .60–.67 and the far-right Blade 5 to h .39.
  2. The deep notches between blade tips (the outline drops to h .55–.63 between peaks): the blades separate in their
     upper half and **merge into one mass below h .5**.
  3. The foot: two pale warm-grey rocks and the lime base leaves, with tan pebbles in front.
- **Target size: 2.4 tall (Blade 1's tip), 3.0 wide (X) × 2.55 deep (Y)** (decision §8.1). Tolerances: height ±0.1,
  width ±0.2, depth ±0.2.
  - **How it was derived.** The front cell's silhouette is 216 × 172 px, so 71.7 px / stud at H 2.4. Side 178 × 168 →
    2.54 deep at 70 px / stud. Top 207 × 182 (W : D 1.14) → 2.88 × 2.53 at about the ortho scale. f34 371 × 298 →
    124 px / stud.
  - **Why 2.4.**
    - At 2.4 the sheet gives: Rock A 0.85 × 0.40 tall, Rock B 0.6–0.7 × 0.3, tan pebbles 0.25–0.38 (all "small stones",
      as the sheet says); blades 0.5–0.7 wide, which still read at gameplay distance.
    - 0.44 C against the 5.5-stud character: knee-to-thigh height. It is ground cover a player walks through, clearly
      smaller than 058 Low Bush (4.5) and close to the lobby's `GrassTuftLarge` (3 × 2).
    - The old W07 `GrassTuft` (4.7 tall) and V01 `BluegrassClump` / `FieldSedge` (4.0–4.2) are 0.75–0.85 C, chest high,
      far above WorldModeling §3.2's grass range (0.08–0.25 C); a broad-leaf tuft can sit above that range, but not at
      chest height.
    - At 1.8 the rocks shrink to pebbles (Rock A 0.64) and the blades to 0.4–0.5 wide; at 3.0 it reaches mid-thigh and
      crowds 058.
  - **Against the character (5.5):** 0.44 C tall, 0.55 C wide.
- **Build frame:** front −Y, +X right, ground z 0. The root base's post at (0, 0). The origin is the bbox bottom centre;
  the fan is not symmetric (Blade 1 leans right), so record the origin's offset from the post (expected ≤ 0.1).

### 1.2 Measured views (`measure.py`, `samp.py`, `comps.py`)

| View (box) | Silhouette bbox (px) | W : H | G | T | R | O | fill | leaf light / mid / dark |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (200,70,615,405) | 227–597 × 89–386 (371 × 298) | 1.245 | 92.6 % | 0.5 | 6.8 | 0.1 | 0.586 | 23 / 37 / 39 |
| Rear three-quarter (615,70,1008,405) | 629–986 × 100–386 (358 × 287) | 1.247 | 92.2 | 0.1 | 7.3 | 0.4 | 0.578 | 15 / 52 / 33 |
| **Front** (16,498,268,704) | 37–252 × 517–688 (216 × 172) | **1.256** | **90.4** | **1.3** | **8.3** | 0.0 | **0.590** | **25 / 32 / 43** |
| Side (270,498,506,704) | 301–478 × 517–684 (178 × 168) | 1.060 | 90.0 | 2.1 | 7.7 | 0.1 | 0.470 | 10 / 50 / 40 |
| Rear (508,498,757,704) | 523–743 × 526–685 (221 × 160) | 1.381 | 91.1 | 1.2 | 7.5 | 0.2 | 0.568 | 19 / 39 / 42 |
| Top (760,498,1007,704) | 787–993 × 509–690 (207 × 182) | 1.137 (W : D) | 81.9 | 3.9 | 14.0* | 0.2 | 0.498 | 14 / 58 / 27 |

- Shares are of the silhouette (X and paper excluded). **Fill** = silhouette / bbox area. *Top R includes contact shadow
  (mask limit); its true rock + pebble share by blob is about 9 %.
- **T is pebbles only** in every assembled view (the root base never shows); the side's 2.1 % is one tan pebble in front.
- **Verifier tolerance:** G ±4, R ±3, T ±1.5 points; W : H ±0.07; fill ±0.05; tip positions ±0.05 H.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.1 W): separate blade tips with deep notches.

| f | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .17 | .61 | .74 | .89 | .72 | .77 | .90 | .97 | .70 | .74 | .47 |
| r34 | .46 | .47 | .71 | .97 | .89 | .77 | .83 | .74 | .85 | .63 | .66 |
| Front | .16 | .60 | .55 | .77 | .84 | .63 | .84 | .94 | .63 | .66 | .40 |
| Side | .71 | .70 | .67 | .61 | .83 | .70 | .74 | .91 | .52 | .58 | .62 |
| Rear | .44 | .71 | .67 | .95 | .86 | .66 | .81 | .69 | .82 | .49 | .51 |

**Width per height** (silhouette width at h .02 → .98 in 11 steps, fraction of W):

```
f34    .32 .95 .92 .77 .83 .74 .84 .70 .42 .44 .04
r34    .42 .79 .89 .72 .83 .72 .80 .69 .55 .60 .03
front  .74 .96 .92 .76 .86 .78 .89 .46 .50 .39 .03
side   .49 .69 .52 .60 .69 .79 .91 .74 .36 .08 .02
rear   .62 .80 .73 .82 .93 .82 .66 .72 .57 .43 .05
```

- Reading (front): h .1–.2 the base leaves, rocks and the low outer blades across the full width; h .3–.6 the fan at
  .76–.89 of W (the low outer blades still reaching out); h .7–.9 only the tall blades (.39–.50 of W, in 2–3 separate
  runs); the top is Blade 1's tip.
- **Outline runs at h .70 (front, x from the bbox centre in H):** [−.32 … −.19] Blade 2, [−.17 … −.06] Blade 6, [+.03 …
  +.26] Blade 1. At h .85: [−.18 … −.14] Blade 6's tip, [+.14 … +.30] Blade 1. **The tall blades stand apart above h .65**
  (no merged crown).

**Height fifths** (bottom → top, % of each class):
- Green: front 21.4 / 30.3 / 28.9 / 15.1 / 4.2; f34 18.3 / 30.0 / 29.2 / 17.4 / 5.0; rear 16.8 / 31.2 / 27.7 / 18.3 /
  6.0; side 18.6 / 28.2 / 32.7 / 17.1 / 3.4.
- Rock and pebbles: 83–100 % in the lowest fifth in every side view.

**Blade tips** (read off the 4× zooms; x in px from the front bbox centre (x 143), h fraction of H; studs at H 2.4):

| Blade | Front tip (px), h | Rear tip (world x), h | Front studs (x, z) | Width at mid (front px) | Tone in the hero |
| --- | --- | --- | --- | --- | --- |
| **B1** Center, tallest | (204, 517), 1.00 | +0.96, .99 | (+0.85, 2.40) | 40 | lime upper half, mid lower |
| **B2** Left tall | (86, 545), .83 | −1.11, .84 | (−0.80, 2.00) | 30–35 | lime front face, mid body |
| **B6** back narrow (unlabelled) | (115, 534), .89 | −0.55, .91 | (−0.38, 2.14) | 18–22 | dark |
| **B4** Left short | (40, 585), .60 | −1.65, .51 | (−1.44, 1.44) | 40 (foreshortened) | dark, mid edge |
| **B3** Right tall | (243, 573), .67 | +1.36, .69 | (+1.39, 1.61) | 30–35 | dark-mid |
| **B5** Right short | (252, 621), .39 | +1.65, .44 | (+1.52, 0.94) | 30 | lime face, mid body |

- **Front and rear agree** (rear image right = world −X): the same six tips at the same heights (±0.09 H) and sides; the
  rear spreads 10 % wider on the −X side (W : H 1.38), §3.3.
- **Side** (image left = front, −Y): four tips at y −1.26 (h .71), −0.26 (h .83), **+0.68 (h 1.0, Blade 1 leans
  back)**, +1.26 (h .62). Two blades hide behind others.
- **Top** (centre (898, 602), image up = back): five broad leaves in a star, tips at (−0.06, +1.29) back, (−1.54,
  +0.26) left, (+1.32, +0.10) right, (−0.82, −1.21) front-left, (+0.54, −1.22) front-right; plan lengths 93–113 px
  (1.3–1.55 studs); leaves look broad from above (plan width about 0.5 of plan length), with a ridge down each.
- **Counts per view:** front 6 tall tips + 3 base leaves (+ 1–2 tiny sprouts); f34 6 + 3 (+ 2 tiny); rear 6; r34 6 + 2
  base leaves; side 4; top 5.

**Base leaves** (short chunky leaves at the foot; front px → studs):

| Leaf | Front box (px) | Studs (x range, z top) | f34 | Shape |
| --- | --- | --- | --- | --- |
| N1 left | (37–88, 640–670), behind Rock A | x −1.48 … −0.77, z 0.67 | (228–275, 297–345) | a short broad leaf lying out to the left, lime top, mid body |
| N2 front-centre | (128–163, 661–686) | x −0.21 … +0.28, z 0.38 | (385–455, 337–382), lime | a stubby faceted pyramid leaf, nearly as wide as tall |
| N3 right | (212–251, 647–677), behind Rock B | x +0.96 … +1.51, z 0.57 | (515–585, 302–355) | a short broad leaf pointing right, mid green |
| sprouts | (102–115, 669–677) green bump; (206–216, 655–665) a green bit above Rock B | 0.15–0.2 tall | (475–503, 370–388) lime; (330–360, 340–362) dark | tiny |

- explA draws the two base leaves alone: **L 66 px, W 44–47, L : W 1.4–1.5**, chunky gems with 6–8 broad facets, about
  0.33 of Blade 1's length there.

**Rocks and pebbles** (`comps.py`; studs at H 2.4; x from the post, front px / 71.7):

| Piece | Front | f34 | Side | Rear | Top | Adopted |
| --- | --- | --- | --- | --- | --- | --- |
| Rock A (large, grey) | (40–102, 659–686) 63 × 28 px = 0.88 × 0.39, x −0.96 | (231–334, 331–376) 0.84 × 0.37 | front grey (320–355) | right-hand grey pair (653–703) | UL grey (827–870, 540–579) 0.6 | centre (−0.95, −0.45), 0.85 × 0.65 × 0.40 |
| Rock B (medium, grey) | (186–226, 665–686) 41 × 22 px = 0.57 × 0.31, x +0.92 | (453–542, 339–372) 0.73 × 0.27 | back grey (429–455) y +0.56 … +0.94 | left-hand grey (543–602) | UR (924–952, 546–571) 0.4 | centre (+0.85, +0.35), 0.65 × 0.50 × 0.32 |
| Rock C (small, tan) | (91–117, 677–687) 0.38 × 0.15, x −0.50 | (312–352, 361–377) 0.33 × 0.14 | front tan (347–369) 0.33 × 0.23 | (590–606) | LL tan (822–839, 621–638) 0.25 | centre (−0.50, −0.80), 0.36 × 0.30 × 0.17 |
| Rock C2 (tan, unlabelled twin) | (180–196, 676–686) 0.24 × 0.15, x +0.67 | — | — | — | LR tan (939–956, 635–651) 0.25 | centre (+0.62, −0.75), 0.25 × 0.22 × 0.14 |

### 1.3 Silhouette and composition per view

**Front (`z_front.png`) — governs positions and heights.** A low view (rock tops just visible). Six blades fan from a
narrow base at x ≈ 143: B4 sweeps far left and low (its tip h .60), B2's lime face rises left (h .83), B6 shows as a
narrow dark spear between B2 and B1 (h .89), B1 rises right of centre to the top (h 1.0), B3 leans right (h .67), and B5
lies out to the far right (h .39). Their lower halves overlap into one green mass; above h .65 they separate. At the foot:
Rock A front-left in front of N1, a tan pebble, the lime pyramid N2 in front of the blade bases, a tan pebble, and Rock B
in front of N3. A soft neutral shadow falls to the left.

**Front three-quarter (`z_f34.png`) — governs the read.** Drawn **nearly frontal and from higher up**: the six tips sit at
the front's x fractions within ±0.04 H, all but the back blade B6 (B1 +.36 vs +.355, B2 −.37 vs −.33, B4 −.57 vs −.60, B3 +.56 vs +.58, B5 +.67 vs
+.63; only the back blade B6 shifts, −.25 vs −.16), the rocks' tops show more and the ground plane is deeper. Light from
the upper right: the lime falls on the upper-right faces of each blade, the dark on the left faces and low down.
- **Blades:** each shows two or three long facets: a broad lit face and a darker face meeting at a ridge, with one or two
  facet breaks along the length where the blade bends. Tips are pointed (about 25–35°), never rounded paddles or needles.
- **Base:** Rock A big and pale at the left (lit top `#C9BDB3`), the tan pebble right of it, N2's lime pyramid in front,
  a tiny lime sprout and Rock B at the right with N3 behind it, N1 behind Rock A at the left.

**Rear three-quarter (`z_r34.png`).** The same tuft from behind: B1's lime face dominates on the image left, the other
five fan out, two grey rocks on the near side at the image left, two base leaves on the right (a lime pyramid and a mid
leaf).

**Rear (`z_rear.png`).** A near mirror of the front: six tips at the mirrored x and the same heights; two grey rocks and a
tan pebble at the foot.

**Side (`z_side.png`).** A narrower fan (W : H 1.06): a broad lime blade reaching far forward (image left, h .71), the
narrow dark blade near the middle (h .83), B1 leaning back (image right, h 1.0) and a blade reaching back (h .62). Rocks:
a grey one in front with a tan pebble in front of it, a grey one at the back.

**Top (`z_top.png`).** A five-pointed star of broad leaves (each with a ridge; lime on the right-hand leaves, dark in the
creases near the centre), the centre a dark crease where they meet; two grey rocks at the back corners and two tan
pebbles at the front corners, just outside the star.

**Base detail, underside (close-up 1, `z_cu.png` left).** The root base seen from below at an angle: an octagonal hub
with **five chunky octagonal arms** (the four cross arms plus the upright post, foreshortened), each ending in a **flat
end face**; a **hexagonal recess** in the hub's underside (dark `#2A271D`). Root brown `#95643D`, lit `#CE9766`, shade
`#734D2F`.

**Leaf blade detail (close-up 2).** One blade's upper half: a broad lime face (`#ACDA30`) and a darker mid face
(`#62981E`) meeting at a ridge, a narrower edge band down the right side (the thickness), tapering to a sharp tip. L : W
of the shown part 2.26.

**Root and rock junction (close-up 3).** The blades' bases converge on a **brown block (the post top) visible between
them**, a big grey rock at the left (`#BAADA4`, shade `#726968`), a grey rock at the right and a tan pebble (`#9A7E58`)
in front, standing apart on the ground.

### 1.4 Parts (exploded `z_expl.png`, `z_explA.png`; key parts `z_parts.png`)

The exploded is a front view at a larger scale, blades lifted off their faces. **The hero governs every size, angle and
position (§3.5); the exploded and key parts govern each part's shape and proportions.**

`expl.py` (principal-axis length L, max width W, the width profile in tenths from tip to base):

| Part (label) | Exploded box (px) | L × W, L : W | Width profile (tip → base) | Tone (light / dark share) | Notes |
| --- | --- | --- | --- | --- | --- |
| Blade 1 (Center, Tallest) | (291–403, 760–975) | 230 × 72, **3.2** | 24 41 55 63 67 72 72 67 55 39 | 0.45 / 0.00 | widest at 0.35–0.45 L from the base; base 0.54 W; straight, the tip turned slightly right |
| (unlabelled, back) | (214–283, 775–922) | 160 × 43, **3.7** | 9 17 24 31 36 40 42 43 41 28 | 0.00 / 0.84 | the narrowest; dark; widest near the base third |
| Blade 2 (Left Tall) | (122–245, 810–974) | 203 × 62, **3.3** | 19 35 45 52 60 62 60 56 51 32 | 0.33 / 0.13 | lime edge face, mid body; curves out to the left |
| Blade 3 (Right Tall) | (376–509, 816–955) | 185 × 66, **2.8** | 16 31 43 53 58 63 66 61 51 37 | 0.00 / 0.86 | dark; leans right |
| Blade 4 (Left Short) | (107–199, 906–1001) | 131 × 57, **2.3** | 13 25 35 46 53 57 57 48 35 18 | 0.00 / 0.69 | dark; the stubbiest; its base tapers more (0.32 W) |
| Blade 5 (Right Short) | (415–528, 913–1002) | 137 × 55, **2.5** | 13 25 34 43 48 52 55 52 43 30 | 0.14 / 0.05 | mid with lime; lies out to the right |
| Base leaves (explA) | (670–738, 967–1018), (901–961, 987–1042) | 66 × 44–47, **1.4–1.5** | 37 40 44 43 42 39 37 35 30 18 | 0.03 / 0.27–0.38 | chunky faceted gems; dashed down onto Rocks A and B |
| Root Base (5-way join) | (258–363, 999–1071) | 106 × 73 | | brown `#9A683F` | a **cross of four octagonal arms plus an upright post**; flat end faces; parts row: the same cross + post |
| Rock A (Large) | (145–214, 1042–1093) 70 × 52 | W : H 1.35 | | `#B2A198` | 8–10 broad facets, flat base, sloping top |
| Rock B (Medium) | (419–464, 1053–1087) 46 × 35 | 1.31 | | `#9B8B82` | as Rock A, smaller |
| Rock C (Small) and its twin | (394–418, 1086–1110) 25 × 25; (211–239, 1082–1105) | ~1.1 | | tan `#AE7747` / `#AD7745` | a faceted nugget, 6–8 faces |

- **Key parts row** (each drawn alone, 43–46 px tall): Blade 1 L : W 2.56, Blade 2 2.27, Blade 3 2.31, Blade 4 1.95, Blade
  5 1.90 (lime / mid; Blade 3–5 dark 49–59 %); Root Base a cross + post (`#96653F`); Rock A `#AEA49E`, Rock B `#968985`,
  Rock C tan `#B37E4A`. The key-parts blades read stubbier than the exploded ones (thumbnail scale); **use the exploded
  L : W**.
- **Blade cross-section** (close-up 2, the exploded's facet lines): a broad front face split by a **ridge** into a lit
  half and a darker half, a narrow **edge / thickness band**, and a back. Not a flat card, not a cylinder: a shallow
  folded wedge (WorldModeling §6.1–6.2).
- **The blades are pointed lanceolates**, widest at 0.35–0.6 L from the base, the base end cut flat at 0.4–0.55 W (it sits
  on a joining face), the tip a sharp point with 2–3 facets converging.

### 1.5 How 059 differs from its siblings and the old kit (binding: the verifier checks these)

| | W07 `GrassTuft` (old kit) | 047 / 054 / 055 dressing tufts | V01 `BluegrassClump` / `FieldSedge` | 058 Low Bush | **059 Grass Tuft** |
| --- | --- | --- | --- | --- | --- |
| Size | ~6.5 × 6.9 × 4.7 tall | 1.5–3.2 tall, Ø 1.6–2.0 | 4.0–4.2 tall | 6.4 × 5.6 × 4.5 | **3.0 × 2.55 × 2.4 tall, W : H 1.26** |
| Blades | 5 main + 2 low creased "paddle" blades, few, rounded | 4–6 thin folded lanceolates (6 tris) on a hub | many thin blades | rosettes, not blades | **six broad pointed lanceolate solids (L : W 2.5–3.7, Ø 0.5–0.7) in a 1 tallest / 3 tall / 2 short hierarchy + three chunky base leaves (L : W 1.5) + two tiny sprouts** |
| Root | a 5-fin stub | a hidden hub | hidden | a trunk | **a brown cross + post root base (5-way join), hidden in the assembled views** |
| Stones | 3 pebbles | rocks around | none | big pale rocks | **two warm-grey faceted rocks (0.85, 0.65) + two tan pebbles (0.36, 0.25)** |
| Colour | one grass green | lime | green | lime / mid / dark rosettes | **three greens by blade role and height: front 25 / 32 / 43 light / mid / dark** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, the root base's post at (0, 0)). Plan azimuths: 0° = +X,
counter-clockwise, 90° = +Y (back), 270° = −Y (front).

### 2.1 Stack (binding contact chain, bottom up; every seat gap ≤ 0.03)

| Piece | Sits on / in | Contact |
| --- | --- | --- |
| Root base (post + four arms; closed shells) | ground | flat undersides at z 0 … −0.03 (decision §8.10) |
| Arms | the post | each arm's inner end buried ≥ 0.10 in the post; no boolean |
| Blades B1–B6 | their joining face on the root base (§2.3) | the blade's flat base face 0.03–0.06 inside the post / arm end; base centre within 0.05 of the face centre |
| Base leaves N1–N3 | ground (N2 may also touch the front arm) | root end at z 0 … −0.03 |
| Sprouts S1, S2 | ground | z 0 … −0.03 |
| Rocks A, B, pebbles C, C2 | ground | flat base sunk ≤ 0.03; **no attachment** to the root (close-up 3: ≥ 0.05 clear of the root base) |

### 2.2 Root base (5-way join)

- **Post:** 8-sided prism, Ø 0.36 (flats), from z −0.03 to **z 0.40**, its top a flat octagon (B1's joining face), the
  top ring chamfered 0.04 (the parts row's bevelled block). Its +X flank carries B3's base; its other flanks are hidden.
- **Arms (4):** 6- or 8-sided prisms, Ø 0.22, centreline at z 0.10, from the post to 0.50 out, each ending in a flat
  face square to its axis, rising 10° outward. Azimuths **166° (B4), 346° (B5), 76° (B6), 256° (B2)**: a cross turned
  so each arm points at its blade.
- **Hex recess (close-up 1):** optional; a 6-sided inset 0.04 deep on the post's underside. It faces the ground and is
  never seen in the game: **leave it out** unless the parts shot needs it (decision §8.4).
- **Visibility:** in the hero the arms and post are covered by the blade bases, the base leaves and the rocks. Front / f34
  T must stay ≤ 2 % (the sheet's T is pebbles only); the post top may show between the blade bases in a close-up
  (`root_cu`, close-up 3).
- Part about 1.0 × 1.0 × 0.43; the `…RootBase` part shows all six joining faces bare.

### 2.3 Blades (six)

Root = the centre of the blade's flat base face (on its joining face); tip = the tip point. L = straight root → tip.
"Bend" = the outward / downward turn at 0.55 L and again at 0.8 L (two kinks; each a facet break).

| Blade | Joining face | Root (x, y, z) | Tip (x, y, z) | L | W max (at) | L : W | Lean from vertical, azimuth | Bend (2 steps) | Roll (face toward) | Tone (§5) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **B1** Center, tallest | post top | (0.04, 0.04, 0.40) | **(+0.85, +0.55, 2.40)** | 2.22 | 0.70 (0.45 L) | 3.2 | 25°, az 33° | 4° + 4° (nearly straight; tip turns right) | front, 30° | mid → light |
| **B2** Left tall | arm 256° end | (−0.12, −0.48, 0.18) | **(−0.80, −1.20, 2.00)** | 2.08 | 0.63 (0.5 L) | 3.3 | 33°, az 227° | 6° + 8° out | front-left | dark base → mid → light upper |
| **B6** back narrow | arm 76° end | (+0.12, +0.48, 0.18) | **(−0.40, +1.15, 2.14)** | 2.09 | 0.55 (0.6 L) | 3.8 | 28°, az 128° | 5° + 5° | back, partly front | dark |
| **B3** Right tall | post +X flank | (+0.18, 0.00, 0.28) | **(+1.39, +0.15, 1.61)** | 1.81 | 0.64 (0.5 L) | 2.8 | 42°, az 7° | 8° + 10° out | front, 40° | dark → mid tip |
| **B4** Left short | arm 166° end | (−0.48, +0.12, 0.18) | **(−1.45, +0.55, 1.44)** | 1.66 | 0.66 (0.5 L) | 2.5 | 40°, az 156° | 10° + 12° out and down | front | deep base → dark |
| **B5** Right short | arm 346° end | (+0.48, −0.12, 0.18) | **(+1.52, −0.80, 0.94)** | 1.47 | 0.60 (0.5 L) | 2.5 | 57°, az 327° | 8° + 10° (the tip lifts slightly, as the front shows) | up-front | mid → light |

- **Hierarchy check:** lengths 2.22 / 2.09 / 2.08 / 1.81 / 1.66 / 1.47; leans 25–57°; no two blades within 10 % of each
  other in both length and lean. Tips at six distinct heights (2.40, 2.14, 2.00, 1.61, 1.44, 0.94).
- **Shape (each blade, its own frame, x along, y across):** stations at 0 (base), 0.30, 0.55 and 0.80 L, then the tip.
  - Half-widths (fraction of W / 2): base 0.48 (B4 0.36), 0.30 L 0.92, 0.55 L 1.0 (B1 at 0.45 L), 0.80 L 0.62, tip a
    point (or two verts 0.06 W apart if the tip fan makes bowties). Tip angle 25–35°.
  - **Section (6 verts):** left edge, front-left shoulder (−0.45, +0.75 r), front ridge (0, +r), front-right shoulder
    (+0.45, +0.75 r), right edge, back ridge (0, −0.55 r), with **r = 0.14 W** at the widest station, 0.10 W at the base
    and 0.8 L. Total thickness ≈ 0.10–0.13 studs on the big blades (close-up 2's "consistent thickness"). Tones blend
    across the shoulders, so each blade shows 2–3 broad facets per side, not a crease alone.
  - **Not a card and not a cylinder:** the side view of every blade shows its thickness; no round sections, no cone tips.
- **Roll:** each blade's broad face is turned between its lean plane and the nearer of the front / back cameras so it
  shows ≥ 50 % of its width in the front, rear and top views. In the front and f34, ≤ 10 % of blade area may lie within
  12° of edge-on.
- **Clearances:** every blade vertex past 0.15 L has z ≥ 0.05 (the lying blades B4 / B5 never touch the ground); blades
  pass ≥ 0.03 over rocks (or rest on them within 0.03, never inside); blades may overlap each other at the base (they are
  separate closed shells) but **no blade more than 30 % inside another**.

### 2.4 Base leaves (three) and sprouts (two)

| Leaf | Root (x, y, z) | Tip (x, y, z) | L | W | L : W | Thickness | Tone |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **N1** left, behind Rock A | (−0.65, +0.22, 0.02) | (−1.45, +0.30, 0.62) | 1.00 | 0.58 | 1.7 | 0.22 | mid → light tip |
| **N2** front-centre pyramid | (+0.12, −0.68, 0.02) | (+0.16, −0.96, 0.40) | 0.47 | 0.46 | 1.05 | 0.30 (a stubby gem) | light, mid base |
| **N3** right, behind Rock B | (+1.05, +0.85, 0.02) | (+1.55, +0.95, 0.57) | 0.75 | 0.50 | 1.5 | 0.22 | mid, dark base |
| S1 sprout, behind pebble C | (−0.45, −0.55, 0) | 0.18 tall | | 0.16 | | | mid |
| S2 sprout | (+0.40, −0.98, 0) | 0.15 tall | | 0.14 | | | light |

- **Placement notes (checked against §2.5 footprints):** N1 sits clear behind Rock A (rock y ≤ −0.13, N1 y ≥ −0.07) and
  0.4 under B4; N3 touches Rock B's back (rock y ≤ 0.60); N2 may lean against B2's base (separate shells, ≤ 30 %
  overlap) and touch the 256° arm; S1 hides behind pebble C (the front's green bump above the pebble).

- **Build:** a chunky leaf gem: a 4- or 5-sided section at three stations (base 0.6 W, 0.4 L 1.0 W, 0.75 L 0.55 W) and a
  tip point, the underside flat and resting on the ground; about 18–24 tris. N2 is the same with L ≈ W, standing up
  (explA's gems). Sprouts are a tiny 2-facet spear (8–10 tris) or two crossed ones.
- **Decision §8.3** keeps them: they are in the front, f34, r34 and explA, and they break the uniform-blade look at the
  foot. Without them the foot reads bare.

### 2.5 Rocks and pebbles

| Piece | Centre (x, y) | Size W × D × H | Yaw | Build |
| --- | --- | --- | --- | --- |
| Rock A (large, grey) | (−0.95, −0.45) | 0.85 × 0.65 × 0.40 | 20° | ring stack: 7-sided base ring (r ±10 %), widest ring at 0.35 h, a shoulder ring at 0.75 h pulled in 25 %, a sloping 5–6-sided top (lit top toward the upper right, as the sheet); 10–12 broad facets; flat base |
| Rock B (medium, grey) | (+0.85, +0.35) | 0.65 × 0.50 × 0.32 | −35° | as Rock A, 9–11 facets |
| Rock C (small, tan) | (−0.50, −0.80) | 0.36 × 0.30 × 0.17 | 10° | a faceted nugget: 6-sided base, one shoulder ring, a 3–4-sided top; 6–8 faces |
| Rock C2 (tan) | (+0.62, −0.75) | 0.25 × 0.22 × 0.14 | 50° | as C, smaller |

- Rocks are angular blocks (WorldModeling §12.1: H about 0.45–0.6 of W), **never `K.hull_rock` eggs**, never lavender.
  `m047._rock` / `m047.pebble` or `m053._rock` can serve; reshape them to these sizes.
- **Clearances:** ≥ 0.05 from the root base (no attachment); N1 behind Rock A and N3 behind Rock B may touch the rock's
  back (within 0.03) but never enter it more than 0.05; blades clear as in §2.3. Place every rock and leaf through the
  ray-parity guard (`m047._Solids`).

### 2.6 Expected extents and screen checks

- **Extents:** X −1.6 … +1.6 (B4's and B5's tips plus their widths), Y −1.3 … +1.25, Z 0 … 2.40. Bbox about 3.0–3.2 ×
  2.55 × 2.4.
- **Checks on the renders** (floor hidden; `meas.py` with this folder's `m.py`):
  - **front_sheet (0, 5)** — governs positions:
    - W : H 1.19–1.33 (sheet 1.256); G 90 ± 4, R 8 ± 3, T ≤ 2.5; fill 0.59 ± 0.05.
    - The top profile within ±0.08 for f .1–.9; the six tips at the §1.2 table's x and h ±0.05 H.
    - At h .70, three separate outline runs (B2, B6, B1); at h .85, two (B6, B1).
    - Leaf tones light / mid / dark 25 / 32 / 43 ± 8; the top band (h .75–1.0) ≥ 55 % light; the low band (h < .25)
      ≥ 38 % dark.
  - **f34_sheet (0, 15)** (probe az −20 … +20 × e 10 / 15 / 20; keep the best; §3.2): W : H 1.18–1.31 (sheet 1.245); G
    92.6 ± 4, R 6.8 ± 3; tones 23 / 37 / 39 ± 8.
  - **rear_sheet (180, 5), r34_sheet (180, 15)** (probe 160 … 200): W : H 1.20–1.40; six tips; two rocks and two base
    leaves visible (r34).
  - **side_sheet (90, 5):** content (§3.4): W : H 0.98–1.15 (sheet 1.06); a blade reaching far forward, Blade 1 leaning
    back; a grey rock in front with a tan pebble, a grey rock behind.
  - **top (0, 89):** W : D 1.05–1.25 (sheet 1.14); **five broad leaves read as a star** (B6 hidden under B1 / B4 or
    showing as a sixth narrow point); rocks at the corners outside the star.

## 3. View conflicts and resolutions

### 3.1 Sheet number
- **Evidence.** The header says "PAGE 61/132"; INDEX.md row 59 lists `059.png` as "Flintborn grass tuft model study".
- **Resolution.** Our number is 059 (file name, keys `m059_*`). Note the header in the export notes only.

### 3.2 The front three-quarter is near-frontal and drawn from higher up
- **Evidence.** The f34 tips sit at the front's x fractions within ±0.04 H except the back blade (§1.3); W : H 1.245 vs
  1.256; the rock tops and the ground show more.
- **Resolution (decision §8.9).** `front_sheet (0, 5)` governs positions; `f34_sheet (0, 15)` governs the read and the
  shares. Probe az −20 … +20 (e 10–20), keep the best and record the camera.

### 3.3 Five blades in the text, six in the drawings, plus base leaves
- **Evidence.** The subtitle and the notes say five blades and the key parts list Blade 1–5. But the exploded draws
  **six** blades (an unlabelled narrow dark one between Blade 2 and Blade 1), the front, f34, rear and r34 each show **six
  tall tips**, and the front, f34, r34 and explA show **two or three short chunky leaves** at the foot. The top shows
  five leaves (one hides).
- **Resolution (decision §8.3).** **Six blades** (B1–B5 as labelled, plus B6, the unlabelled back blade), **three base
  leaves** and **two tiny sprouts**. The drawings govern shape; the "five" names the labelled, reusable blades. The
  parts export keeps the five labelled blades (B6 is a narrower, darker B2 in the hero only).

### 3.4 Side and top disagree with the front in places
- **Evidence.**
  - Side: four tips; Blade 1 leans back (+0.68); one blade reaches far forward (−1.26, h .71) and one far back (+1.26,
    h .62).
  - Top: a clean five-point star, the back leaf at x ≈ 0 (the front puts Blade 1's tip at x +0.85), rocks at the four
    corners (grey at the back, tan at the front), while the front puts the grey rocks in front of the blade bases.
  - The rear is 10 % wider on the −X side (W : H 1.38 vs 1.26).
- **Resolution.** **Front governs X and Z for every blade, rock and leaf; the side and top set Y** (§2.3: B1 back, B2
  forward, B6 back, B4 slightly back, B5 forward), within a plan whose W : D is 1.14 and depth about 2.55. The side is
  judged for content (W : H, a forward blade, B1 leaning back, a rock front and back), the top for the plan (a star of
  broad leaves, W : D, rocks just outside the leaves). Rocks: A front-left and C / C2 in front (front, side and f34
  agree), B right and back (side, top). The rear's extra width is not chased.

### 3.5 Exploded scale vs the hero
- **Evidence.** The exploded draws each blade bigger and more upright than the hero (its Blade 1 is 230 px long against
  a root base 106 px wide; in the hero that blade is 2.2 studs against a 1.0-stud root), its blade length ratios differ
  from the hero's (Blade 4 0.57 of Blade 1 there, 0.75 in the hero), and the key parts are stubbier thumbnails (L : W
  1.9–2.6).
- **Resolution.** The hero governs size, lean and position; the exploded governs each blade's outline (L : W, where it
  is widest, a flat base, a pointed tip) and tone role; the key parts only confirm the set.

### 3.6 Palette "Soil / Rock" is tan, but the big rocks are grey
- **Evidence.** The SOIL / ROCK swatch is tan `#BD9868` (34°, .45). The root base (`#9E6B40`) and Rock C / its twin
  (`#A17447`–`#B37E4A`) are tan-brown, but Rocks A and B are warm grey in every cell (`#ABA196`, s 0.12–0.15).
- **Resolution.** Rocks A and B are **warm grey** (sampled), Rock C and C2 **tan** (the swatch, calibrated to the
  rendered pebbles), the root base **brown** (its own key). Never paint A / B tan.

### 3.7 Root base: cross + post or five radial arms
- **Evidence.** The exploded, explA and key parts show a cross of four arms plus an upright post; close-up 1 shows five
  arms from below, which is the same cross + post seen obliquely (the post foreshortened into a fifth arm), with a hex
  recess underneath.
- **Resolution.** Cross + post, the cross turned so each arm points at its blade (§2.2); the recess optional.

### 3.8 Ground: a shadow, no patch
- **Evidence.** Every cell shows a soft neutral cast shadow (s ≈ 0.02, v 0.66–0.88) to the left and no soil disc.
- **Resolution (decision §8.7).** **No soil patch.** The terrain is the ground. The masks exclude the shadow.

### 3.9 "No textures, no noise" vs the user's colour rule
- **Evidence.** The notes ask for clean solid colours, no textures or noise; the user wants rich, blended colour with
  broad Tint mottling (memory `lighting-not-paint`).
- **Resolution.** Three greens blended by blade role and height along each blade; broad Tint per blade, per rock facet
  (0.03–0.04), never per-triangle confetti.

### 3.10 Lighting
- The sheet is lit from the upper right (lime on the upper-right faces, dark on the left faces and low down). The
  lighting does that; never paint it by facing. Render every `*_sheet` view with the studio floor hidden. The cool tint
  on the rocks' shaded faces is light, not paint.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its exploded / key-parts cell

1. `blade(spec)` → one closed lanceolate solid (§2.3): stations, the 6-vert section, two bends, roll, a flat base face.
   Build it in bmesh in its own frame, then place it with its base face on the joining face. Check each against its
   exploded cell: L : W, widest station, base width, tip angle, a visible ridge. m049's `blade` / `_blade_local` and
   m055's `blade` are useful references (m049's has a pointed root; ours needs a flat base face).
2. `base_leaf(spec)` → the chunky gem (§2.4); `sprout(spec)`.
3. `root_base()` → post + four arms (§2.2), closed shells, arms buried ≥ 0.10 in the post (no booleans).
4. `rock(spec)` ×2, `pebble(spec)` ×2 (§2.5), all through the ray-parity guard (`m047._Solids`).
5. **Hero `BroadGrassClump`** = root base + six blades on their faces + three base leaves + two sprouts + four rocks,
   joined into one object of closed shells.
6. **Parts shot** (0, 15) laid out like the key-parts row: BladeCenter, BladeLeftTall, BladeRightTall, BladeLeftShort,
   BladeRightShort, RootBase, RockLarge, RockMedium, RockSmall, gaps 0.4.
7. **Exploded shot:** the root base in the middle, each blade lifted 0.6 off its face along its axis (the six of the
   exploded), the base leaves lifted over Rocks A and B (explA), rocks below.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a fan of six broad, thick, pointed blades of different lengths and leans, the tallest right of
   centre; three chunky base leaves; two grey rocks and two tan pebbles; no root showing.
2. **front_sheet / f34_sheet** per §2.6 (shares, fill, W : H, top profile, tip positions, separate runs at h .70 / .85).
3. **rear / r34 / side / top** per §2.6.
4. **Close-up renders:**
   - `blade_cu` (−30, 20) on B1's upper half against close-up 2: broad faces, a ridge, a visible thickness band.
   - `root_under` (0, −60) on the RootBase part against close-up 1: cross + post, flat end faces.
   - `root_cu` (−15, 15) on the hero's foot against close-up 3: blade bases converging on the post top, rocks apart.
   - `edge_side` (90, 0): every blade shows thickness (no blade thinner than 0.08 on screen in studs).
5. **Contact counts** (§6): floating shells 0; every blade on its joining face; every leaf, sprout and rock on the ground;
   buried 0.
6. **Hero size** per §2.6, plus a **scale shot** with a 5.5-stud marker beside the tuft (the top at 0.44 of the marker).

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Blades (6-vert section × 4 stations + tip fan + base cap) | 6 | 46–50 | 280–300 |
| Base leaves (4–5-sided, 3 stations + tip) | 3 | 18–24 | 55–70 |
| Sprouts | 2 | 8–10 | 16–20 |
| Root base: post (8-sided, chamfered top) + 4 arms (6-sided) | 1 + 4 | 36 + 14 | 90–100 |
| Rocks A, B (ring stacks) | 2 | 30–40 | 65–80 |
| Pebbles C, C2 | 2 | 10–16 | 22–30 |
| **Hero** | | | **about 530–600; aim ≤ 700; ceiling 900** |
| Parts: BladeCenter / LeftTall / RightTall / LeftShort / RightShort / RootBase / RockLarge / RockMedium / RockSmall | | | 50 / 50 / 50 / 50 / 50 / 100 / 40 / 32 / 16 |

- **Headroom:** spend it, if anything, on a fifth station near the tip of B1 / B2 (a smoother bend), or one more
  facet ring on Rock A. Never on more blades.
- **If a hidden face can go** (the arms under the base leaves), keep it anyway: closed shells beat a saving of 20 tris.

### 4.4 What to do better than W07's `GrassTuft` and the recent tufts

| Earlier | This one |
| --- | --- |
| W07: "few flat paddle blades", rounded tips, one green, 312 tris | six pointed lanceolates with a ridge, thickness and two bends; three greens by role; base leaves and rocks as the sheet |
| 047 r1: "spiky ground plants"; tufts like agave | broad blades (L : W ≤ 3.8, widest at mid), a directional fan with one tallest blade leaning right-back, not a symmetric rosette; leans 25–57° all different |
| 054 / 055: thin 6-tri folded spears | 46–50-tri closed solids with shoulders: broad faces that catch the light like the sheet's |
| 039 / 054: edge-on needle grass | every blade rolled to show ≥ 50 % of its width to the front / rear / top cameras |
| 035 / 036 / 046 / 047 r2: floating or buried dressing | blades seated on joining faces; leaves and rocks on the ground; ray-parity guard; counts reported |

### 4.5 Stages 2 and 3
- **Stage 2:**
  - Every shell closed and manifold, **0 bowties** (likely at blade tips: a single tip vertex over a 6-vert ring; and at
    the base-leaf tips; `M.fix_bowties`, or a two-vert tip).
  - **0 winding errors per shell** (hand-built blades flip easily: `bmesh.ops.recalc_face_normals` per shell, then check
    every shell with `m047.shells_report`).
  - No zero-area faces; corners ≥ 3°; no n-gons except the flat base caps and rock bases (triangulate if the audit asks).
  - Origin at the bottom centre, transforms applied.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box)

| Swatch | Box | Hex | HSV | Use |
| --- | --- | --- | --- | --- |
| GRASS DARK | (35,307,56,327) | `#56952E` | 97°, 0.69, 0.58 | start for `grass_dark` |
| GRASS MID | (35,336,56,357) | `#6AA420` | 86°, 0.80, 0.64 | start for `grass_mid` |
| GRASS LIGHT | (35,366,56,387) | `#A9D42E` | 76°, 0.78, 0.83 | start for `grass_light` |
| SOIL / ROCK | (35,396,56,415) | `#BD9868` | 34°, 0.45, 0.74 | start for `pebble` (tan); **not** the grey rocks (§3.6) |

### 5.2 Rendered regions (`samp.py`, `samp2.py`; median / lit quartile / shade quartile / v > .7)

| Region | Median | Lit Q | Shade Q | v > .7 |
| --- | --- | --- | --- | --- |
| All green: front / f34 / rear / side / top | `#58901E` (89°, .79, .56) / `#58921D` / `#568E1E` / `#5B951F` / `#67A21D` | `#A3D22E` / `#9BCD2A` | `#2E5F15` / `#2E6016` | `#9ACC2C` / `#95C828` |
| Light tone: front / f34 / rear / cu2 | `#A1D12B` (77°, .79, .82) / `#9DCF2A` / `#AFDC32` / `#ACDA30` | `#C2E843` / `#C3E844` | `#90C320` | |
| Mid tone: front / f34 / top / cu2 | `#609619` (86°, .83, .59) / `#5F9519` / `#6CAB1B` / `#62981E` | `#7AB82D` / `#80BA23` | `#487D15` / `#497D16` | |
| Dark tone: front / f34 / rear | `#386C19` (98°, .77, .42) / `#386C1A` / `#3B701D` | `#54952A` / `#549629` | `#214E13` / `#204E13` | |
| Tone shares (light / mid / dark %) | front 25 / 32 / 43; f34 23 / 37 / 39; rear 19 / 39 / 42; r34 15 / 52 / 33; side 10 / 50 / 40; top 14 / 58 / 27 | | | |
| Tone bands, front (h < .25 / .25–.5 / .5–.75 / > .75) | 15/37/48; 25/27/48; 26/36/39; **69/16/15** (f34 top band 58/26/16) | | | |
| Exploded blades (median) | B1 `#86BB21` (light .45); B6 `#397121` (dark .84); B2 `#53881A`; B3 `#4A8824` (dark .86); B4 `#579626` (dark .69); B5 `#659E1C`; base leaves `#78B023` / `#599220` | | | |
| Grey rock: front A / B; f34 A / B | `#ABA196` (31°, .12, .67) / `#AEA094` / `#AFA598` / `#A79A8C` | `#C8BBB3` / `#CBBDB1` | `#716965` / `#7A6E66` | `#C1B4AC` |
| Grey rock: cu3 left / explA A / parts A, B | `#BAADA4` (25°, .12, .73) / `#A29389` / `#AEA49E` / `#968985` | `#C9BBB4` | `#726968` | |
| Tan pebbles: f34 / front / side / rear / cu3 / expl / parts C | `#A17447` (30°, .56, .63) / `#A27F5B` and `#947655` / `#A17949` / `#AE8F64` / `#9A7E58` / `#AD7745` / `#B37E4A` | `#CA985E` (f34) | `#5B462B` | |
| Root base: explA / cu1 / cu3 / parts | `#9E6B40` (27°, .59, .62) / `#95643D` / `#9B693F` / `#96653F` | `#D8A26C` / `#CE9766` | `#7B5231` / `#734D2F` | `#D19B66` |
| Root hex recess (cu1) | `#2A271D` | | | |
| Cast shadow (not modelled) | `#D5D2D1`–`#DCDAD8` (s .02) | | | |

### 5.3 How the colour works

- **Blades: three greens by blade role and by position along the blade** (never facing):
  - **Role** (the exploded's tones): B1, B2, B5 are the light blades (mid body, light upper part); B3, B4, B6 are the dark
    blades (dark body, mid tip at most).
  - **Along the blade:** the lowest 0–0.2 L one step deeper than the body, the upper 0.55–1.0 L one step lighter on the
    light blades. B1: mid 0–0.3 L → blend → light 0.55–1.0 L. B2: dark 0–0.15 L → mid → light 0.6–1.0 L (60 %). B5:
    mid → light tip 0.7–1.0 L. B3: dark → mid tip (0.8–1.0 L, 40 %). B4: `grass_deep` 0–0.2 L → dark. B6: `grass_deep`
    0–0.2 L → dark → 25 % mid at the tip.
  - **A whole station band takes one blend step,** across all six section faces, so the lit face / shade face contrast
    comes only from the light (the sheet's lime and dark halves of one blade are lighting).
- **Base leaves:** N2 light with a mid base; N1 mid → light tip; N3 mid with a dark base; sprouts mid / light.
- **Root base:** `root` brown; `root_light` on the joining faces and the post's top ring (the cu1 lit ends); hard
  where blades meet it.
- **Rocks A, B:** warm grey `rock`; tops a step lighter (`rock_light`, the upper 30 % of each rock), feet a step deeper
  (`rock_deep`, the lowest 25 %), by height within each rock. R ≥ G ≥ B always; **never lavender or blue**.
- **Pebbles C, C2:** `pebble` tan, the lowest 30 % `root` brown (a warm shadow foot, by height).
- **Hues stay apart:** root 26–29°, pebble 30–34°, rock 25–33° at s ≤ 0.16, grass light 76–80°, grass mid 85–88°, grass
  dark 95–100°, grass deep 100–106°.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians where the sheet gives them, swatches where it doesn't. `K.sample` kinds:
`"vivid"` for the light key, `"green"` for mid / dark / deep, `"stone"` for rock, `"brown"` for root and pebble.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m059_grass_light` | front light-tone median `#A1D12B` ± 12 (lit `#C2E843`; start `#A9D42E`) | 76–80°, ≥ 0.75 | upper parts of B1 / B2 / B5, N2, N1's tip | rough 0.8, low spec |
| `m059_grass_mid` | mid-tone median `#609619` ± 12 (swatch `#6AA420`) | 85–88°, 0.78–0.86 | B1 / B2 / B5 bodies, base leaves, B3 / B6 tips | rough 0.85 |
| `m059_grass_dark` | dark-tone median `#386C19` ± 12 (swatch `#56952E` rendered) | 95–100°, 0.70–0.80 | B3 / B4 / B6 bodies, light blades' bases | rough 0.85 |
| `m059_grass_deep` | the dark shade quartile `#214E13` seen lit, about `#2E5A18` ± 12 | 100–106°, 0.70–0.80 | B4 / B6 lowest 0.2 L, N3 base | rough 0.9 |
| `m059_root` | root base median `#9E6B40` ± 12 | 26–29°, 0.55–0.62, **R > G > B** | post, arms, pebble feet | rough 0.9 |
| `m059_root_light` | root lit `#CE9766` ± 12 | 27–30°, 0.50–0.58 | joining faces, the post's top ring | rough 0.85 |
| `m059_pebble` | tan pebbles `#A17447`–`#A27F5B` together, target `#A07850` ± 12 (start `#BD9868`) | 30–34°, 0.45–0.56 | Rock C, C2 | rough 0.9 |
| `m059_rock` | front rock median `#ABA196` ± 10 | 25–33°, 0.10–0.15, R ≥ G ≥ B | Rocks A, B | rough 0.85, metal 0 |
| `m059_rock_light` | rock lit `#C8BBB3` ± 10 | 25–33°, 0.08–0.12 | upper 30 % of each rock | rough 0.85 |
| `m059_rock_deep` | rock shade `#716965` seen lit, about `#8E857C` ± 12 | 25–32°, 0.10–0.15 | lowest 25 % of each rock | rough 0.9 |

**Calibration warnings:**
- **The kit studio lights both halves** (042, 047, 054): calibrate the greens to the tone medians, not the lit quartile
  alone, and check the tone shares on the tuft's own renders (front 25 / 32 / 43 ± 8). Record the lit-shade bias.
- **Greens must not lean yellow or olive** (047's plants were flagged yellow): `grass_mid` ≥ 85°, `grass_dark` ≥ 95° on
  every median; only `grass_light` is lime (76–80°, never below 74°). The front all-green median within 15 of `#58901E`.
- **Rocks never lavender or tan:** A and B R ≥ G ≥ B, s ≤ 0.16; the cool shaded faces come from the light.
- **Pebbles stay tan, the root stays brown:** pebble hue 30–34° and s ≤ 0.56; root 26–29°, darker and more saturated.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Blades:** per station band (all six section faces of a band together), by fraction of L and the blade's role (§5.3).
  Bands blend across one band on each side; the tip fan takes the last band's key.
- **Base leaves:** base band → tip band as §5.3.
- **Root base:** hard `root_light` on the joining faces; `root` elsewhere.
- **Rocks / pebbles:** height bands within each rock.
- **Hard edges only** where materials meet: blade | root, root | ground, rock | anything.

### 5.6 Texture (Tint) and finish
- **Tint:** blades 0.04 per blade (whole blade, never per triangle) + 0.02 per station band; base leaves 0.04 each; root
  0.03 per member; rocks 0.04 per facet; pebbles 0.03.
- **Finish:** grass 0.8–0.9 rough, low spec; root 0.9; rocks 0.85–0.9; no metal, no emission.

### 5.7 Re-measure (final renders against the sheet, same masks)
- **Green:** front median within 15 of `#58901E`; v > .7 within 12 of `#9ACC2C`; tone shares 25 / 32 / 43 ± 8 (front)
  and 23 / 37 / 39 ± 8 (f34); top band ≥ 55 % light; low band ≥ 38 % dark.
- **Rock:** front median within 10 of `#ABA196`, lit within 10 of `#C8BBB3`, R ≥ G ≥ B.
- **Pebbles:** within 15 of `#A17447` (f34). **Root** (parts shot): within 12 of `#9E6B40`.
- **Shares** per §2.6.

## 6. Joins and contact (no floating dressing, no buried dressing)

- **Shells:** each blade, base leaf, sprout, root member, rock and pebble is its own closed shell, all in one hero object.
- **Blade chain:** blade → its joining face (base face 0.03–0.06 inside the post / arm; the base face's centre within
  0.05 of the joining face's centre) → root base → ground. **No blade floating**: report each blade's seat depth.
- **No blade buried:** ≤ 0.06 inside the root base at the base face; nothing inside a rock (ray parity); no blade more than
  30 % of its verts inside another blade.
- **Base leaves and sprouts:** root end at z 0 … −0.03; nothing else of them below z 0; never more than 0.05 inside a
  rock (N1 / N3 sit behind Rocks A / B and may touch them within 0.03).
- **Lying blades:** B4 and B5 never touch or dip into the ground past 0.15 L (z ≥ 0.05 there).
- **Rocks:** sunk ≤ 0.03; ≥ 0.05 clear of the root base (close-up 3: no attachment); never cutting a blade.
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**. A shell floats if its nearest distance
  to every other shell and the ground is > 0.03, or it doesn't chain to the ground. Chains: blade → root member → ground;
  leaf / sprout → ground; rock → ground.
- **Count buried shells** (STAGES; 046, 047 round 2): **0 dressing shells more than 0.05 inside a rock or the root
  base** (blade base faces excepted at ≤ 0.06). Use `m047._Solids` from the start (root base + every rock added as built;
  three skewed rays, two of three agree). A leaf or pebble that still cuts after its retries is moved outward along its
  azimuth.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.
- **Reports:** reuse `m047.shells_report`, `contact_report` and `bury_report` (committed; import, don't edit).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no particles, no pollen, no wind marks. The cast shadow is the
render's.

- **Stage 5 (lighting): skip, and record why.** No emission, no lights. Studio notes (Requires Manual Validation):
  - the blades keep lime tips and green bodies under the game sun (not olive, not yellow);
  - the dark blades stay green, not black;
  - the rocks stay warm grey and the pebbles tan.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** The old W07 `GrassTuft` had none either. A wind sway
  would be a Studio-side script, not a socket (a gameplay call, decision §8.11).
- **Collision:** **hero `none`** (CanCollide, CanQuery and CanTouch off): it is walk-through ground cover, as the old
  W07 `GrassTuft`, V01 `BluegrassClump` and `FieldSedge` are. The exporter supports it: `build_kit.COLLISIONS` includes
  `"none"`, and `export_kit_roblox.py` maps it to CanCollide false (058's spec said there was no such option; there is).
  Parts: the five blades and RootBase `none`; RockLarge and RockMedium `hull` (usable as scatter stones); RockSmall
  `none` (decision §8.8).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched every `art/roblox/kit/*/manifest.json` (1458 assets), the builders and the repo text
(`git grep`) for Grass, Tuft, Blade, Clump, Sedge and the candidates:
- **W07:** `GrassTuft`, `GrassTuftDry`, `GrassTuftRootBase`, `GrassTuftShortWide`, `GrassTuftSingleBlade`,
  `GrassTuftTallPointed`, `GrassTuftThreeBladeClump`. So **no `GrassTuft*` name** (a `GrassTuft` hero collides outright,
  and any `GrassTuft…` prefix would sit inside W07's namespace).
- **Lobby (build_05):** `GrassTuftLarge`, `GrassClumpSmall`. **V01:** `BluegrassClump` / `Bluegrass*`, `FieldSedge`,
  `Sedge*`. **Others:** `FiberPlantTuft`, `HeatherLeafTuft`, `SilkleafSeedTuft`, `DryTussock*`, `ReedClump*`,
  `ReedPatch*`, `Stormreed*`, the `…GrassTop` / `…GrassCap` / `…GrassLip` / `…GrassEdge` terrain pieces, and many
  `…LeafClump` parts.
- **`BroadGrassClump`, `BroadGrass*`, `BladeGrass*` and `m059` occur nowhere** (repo text, manifests, builders), and no
  owned name is a substring of `BroadGrassClump*`.

| Object | Part | Why |
| --- | --- | --- |
| `BroadGrassClump` | hero: root base, six blades, three base leaves, two sprouts, Rocks A / B, pebbles C / C2 | the sheet's own words ("broad leaf grass clump"); W07 owns `GrassTuft*` |
| `BroadGrassClumpBladeCenter` | "Blade 1 (Center)" | the label |
| `BroadGrassClumpBladeLeftTall` | "Blade 2 (Left Tall)" | the label |
| `BroadGrassClumpBladeRightTall` | "Blade 3 (Right Tall)" | the label |
| `BroadGrassClumpBladeLeftShort` | "Blade 4 (Left Short)" | the label |
| `BroadGrassClumpBladeRightShort` | "Blade 5 (Right Short)" | the label |
| `BroadGrassClumpRootBase` | "Root Base": post + four arms, joining faces bare | the label |
| `BroadGrassClumpRockLarge` | "Rock A (Large)" | the label |
| `BroadGrassClumpRockMedium` | "Rock B (Medium)" | the label |
| `BroadGrassClumpRockSmall` | "Rock C (Small)" (tan) | the label |

- Palette keys `m059_*` (§5.4). Collection `Kit/M059 Grass Tuft`. No sockets (§7).

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **2.4 tall, 3.0 × 2.55 footprint** (recommended: 0.44 C, knee-to-thigh ground cover; rocks 0.85 /
   0.65, pebbles 0.25–0.36; blades 0.5–0.7 wide). Alternatives: 1.8 (closer to WorldModeling's grass range and the
   lobby's `GrassClumpSmall`) or 3.0 (closer to the old meadow grasses, which are 4–4.7).
2. **Name (§8):** **`BroadGrassClump` and the nine parts above** (recommended). Not `GrassTuft*` (W07) or `GrassClump*`
   alone (lobby).
3. **Blade count (§3.3):** **six blades (B1–B5 + the unlabelled back blade B6) + three base leaves + two tiny sprouts**
   (recommended: what every assembled view and the exploded draw). Alternatives: the literal five blades (B6 dropped; the
   front loses its second-highest tip and the fan thins) or six blades without sprouts.
4. **Root base (§2.2, §3.7):** **cross + post, turned so each arm points at its blade; hidden in the hero; the hex
   recess left out** (recommended). Alternative: the recess as a 6-sided inset (+12 tris) for the parts shot.
5. **Rocks (§1.2, §2.5):** **four: Rock A (large grey), Rock B (medium grey), Rock C (small tan) and a smaller tan twin
   C2** (recommended: the front, top and exploded each show two tan pebbles). Alternative: the notes' literal three.
6. **Blade shape (§2.3):** **closed 6-vert lanceolate solids, 4 stations, a flat base face on the root, a pointed tip,
   two bends, L : W 2.5–3.8, thickness 0.10–0.13** (recommended), or a lighter 4-vert diamond section (about 30 tris per
   blade; fewer facets than the sheet shows).
7. **Ground (§3.8):** **no soil patch** (recommended), or a thin 0.04 soil disc (+20 tris, a new key).
8. **Collision (§7):** **hero `none`; blade parts and RootBase `none`; RockLarge / RockMedium `hull`; RockSmall `none`**
   (recommended), or everything `none`.
9. **Comparison cameras (§3.2):** **`front_sheet (0, 5)` governs positions, `f34_sheet (0, 15)` the read** (probe az −20 …
   +20, e 10–20); `rear_sheet (180, 5)`, `r34_sheet (180, 15)` (probe 160 … 200), `side_sheet (90, 5)`; kit `top`;
   extras: parts shot, exploded, `blade_cu`, `root_under`, `root_cu`, `edge_side`, scale shot. Floor hidden in every
   `*_sheet` render.
10. **Sinking (origin):** **root base, rocks, pebbles, leaves and sprouts sink at most 0.03**, so the origin sits within
    0.03 of the ground (recommended).
11. **VFX (§7):** **none; stages 5 and 6 skipped and recorded** (recommended). A wind sway is a Studio-side script if
    gameplay wants it.
12. **Exported parts (§8):** **the hero plus the nine key parts** (recommended: the sheet's "KEY PARTS (FOR REUSE)"
    row), or the hero plus the five blades and the root base only (the rocks duplicate kit stones).
13. **Colour (§5):** **blades by role and length to `#A1D12B` / `#609619` / `#386C19` (+ a deep base key), front all-green
    median `#58901E`, tone shares 25 / 32 / 43; rocks warm grey `#ABA196`; pebbles tan `#A07850`; root brown
    `#9E6B40`** (recommended).
14. **Budget (§4.3):** **hero ceiling 900, planned about 530–600; each part under 1000** (recommended: repeated ground
    cover; the old `GrassTuft` budget was 800). Alternative: the 4000 full-asset limit (it would not change the plan).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **Blades that read as spikes or needles (WorldModeling §18; 047 r1 "spiky", 054 / 055 thin spears).**
   - L : W 2.5–3.8 by the §2.3 table; widest at 0.45–0.6 L; a flat base 0.36–0.48 W wide; the tip 25–35° (never a
     cone or a sliver); never a cylinder or a round section.
   - The other way round is the W07 failure ("flat paddle blades"): tips must be **pointed**, not rounded.
2. **Flat cards with no volume (WorldModeling §17.2 "leaves have side-visible volume").**
   - Closed 6-vert sections, ridge 0.14 W, back ridge 0.08 W; every blade ≥ 0.08 thick on screen in `edge_side`.
   - No blade within 12° of edge-on over more than 10 % of blade area in the front / f34 (roll, §2.3).
   - Each blade shows 2–3 broad facets per side (the shoulders), as close-up 2.
3. **Too-uniform counts or a hedgehog / agave rosette (WorldModeling §6.2, §18).**
   - Six blades with six different lengths, leans (25–57°), bends and rolls; one tallest (B1) leaning right-back; three
     chunky base leaves of different sizes; two tiny sprouts. No radial symmetry, no equal spacing.
   - The tall blades separate above h .65 (three outline runs at h .70) and merge below h .5.
4. **Floating blades (STAGES; 035 / 036).** Every blade's base face seated 0.03–0.06 into its joining face; every leaf,
   sprout and rock on the ground (z 0 … −0.03); floating shells 0, counted and reported.
5. **Blades or leaves buried in rock (046; 047 r2).** Ray parity against the full hero rocks after the final placement:
   0 shells more than 0.05 inside a rock; N1 / N3 only touch the rocks' backs.
6. **Lying blades in the ground.** B4, B5 and the base leaves never dip below z 0 past their roots.
7. **Root plug showing (WorldModeling §18 "tree stump with leaves").** T ≤ 2.5 % in the front and f34 (pebbles only on the
   sheet); the root base stays under the blade bases.
8. **Yellow / olive grass (047 "plants too yellow"), or flat one-green (W07).** `grass_mid` ≥ 85°, `grass_dark` ≥ 95°;
   the front median within 15 of `#58901E`; tone shares ±8; the top band ≥ 55 % light.
9. **Colour by facing (042 ruling).** Tones by blade role and station band; rocks by height; `K.check` facing correlation
   < 0.5 per material.
10. **Lavender, blue or tan big rocks (M034, M037; §3.6).** Rocks A / B warm grey, R ≥ G ≥ B, s ≤ 0.16; angular blocks
    with 9–12 broad facets and flat bases, never eggs.
11. **Winding (044) and bowties.** 0 faces wound against their neighbours per shell, especially on hand-built blades and
    leaf gems; tip fans checked for bowties; corners ≥ 3°.
12. **Oversize.** 2.4 tall, not the old kit's 4–4.7; a scale shot with the 5.5-stud marker.
13. **Origin below the ground.** Sink nothing more than 0.03.
14. **Names and scope.**
    - No `GrassTuft*`, `GrassClump*`, `Bluegrass*` or other owned names.
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit the frozen shared helpers, `m047.py`, `m049.py`, `m054.py` or `lib/vfx.py`: import from the committed
      ones (`m047`, `m049`, `m053`, `m055`); copy from `m054` if it is still uncommitted.
    - Don't touch other models' collections.

## Decisions (main session, 2026-10-30)
All 14 recommendations are accepted. The open questions are ruled as follows:
1. **Size.** 2.4 tall with a 3.0 × 2.55 footprint. Ankle-to-knee height suits grass that repeats across the floor.
2. **Names.** Hero `BroadGrassClump` and the nine parts listed in §8; keys `m059_*`; collection `Kit/M059 Grass Tuft`. Never `GrassTuft*` or `GrassClumpSmall`.
3. **Blades.** Six tall blades (B1–B6) plus three base leaves and two sprouts, as drawn. The drawing governs over the text's "five".
4. **Root base.** A cross plus a post, hidden in the hero and never visible in an assembled view. No hex recess.
5. **Rocks.** Four, as drawn: large grey A, medium grey B, small tan C and C2.
6. **Blade shape.** Each blade is a closed solid with a ridged section and a blunt-enough point (not a needle), with real thickness from the side, and rolled to face the cameras. **No spikes, flat cards or hedgehog/agave fans.**
7. **Ground.** No soil patch.
8. **Collision.** As recommended: blades and root `none`; RockLarge and RockMedium `hull`; RockSmall `none`. **Hero:** `none`, so players walk through the clump.
9. **Cameras.** `front_sheet (0, 5)` governs positions and `f34_sheet (0, 15)` governs the read. The side and top set depth only.
10. **Sinking.** At most 0.03 for everything. Blades must sit on the root base or the ground, with **no floating and no buried pieces**.
11. **VFX.** None; stages 5 and 6 skipped and recorded.
12. **Exports.** The hero plus nine parts.
13. **Colour.**
    - Colour by blade role and position along the blade, **never by facing**.
    - Greens are not olive or yellow-brown.
    - Rocks are warm grey with R > G > B, never lavender.
14. **Budget.** Small-prop class: hero ceiling 900 (plan 530–600), every part under 1000.

## Stage 1 — Modelling (modeller, 2026-10-30)

Builder `art/blender/kit/mcp/m059.py` (`build()`, `hero_only()`, `preview()`), background Blender on port 9881, work file
`art/blender/assets/kit/wip/M059.blend`. Every exploded part has its own function and the hero is assembled strictly from
them: `post` + `arm` (→ `root_base`), `blade` (B1–B6 from the `BLADES` table), `leaf` / `_gem` (N1–N3), `sprout` (S1, S2),
`rock` (A, B, C, C2). The hero is one object of 20 separate closed shells (no booleans).

- **Blades.** Each blade is a polyline from its seat on its joining face to its tip with two bends (half the first bend at
  0.40 L and half at 0.62 L, the second at 0.82 L), fitted so it lands exactly on its tip. Five stations (0, .18, .40,
  .62, .82 L) of a **6-vert folded-plate section** (left edge front / midrib / right edge front / right edge back / back
  groove / left edge back) and a tip point: two broad front planes meet at a midrib raised 0.45 × the half-width (about 24°
  each side, so one plane catches the light and one falls in shade, as close-up 2), the back follows the fold one plate
  thickness behind (a V groove), and each edge is a narrow band of that thickness (close-up 2's "consistent thickness").
  Plate thickness 0.12 W (0.066–0.086 studs); fold depth seen side-on 0.13–0.17 studs. The base station is a thick convex
  sheath (0.31 W deep) whose face leans half-way toward its joining face, so it covers the arm end / post top.
  - **Roll** (`roll` 0–1): a blend between the natural face (up and in toward the centre; reads in the top view and on
    the diagonal blades B2, B6) and the front camera (B3 0.7 and B4 0.7 lean sideways and would be edge-on; B5 0.5, B1 0.35).
  - Width profiles per station from the exploded's width profiles (§1.4): base 0.50–0.68, widest 1.0 at 0.40 L, 0.82 L
    0.47–0.60 of the half-width; B6 the narrowest (W 0.55, L : W 4.2).
- **Root base.** 8-sided post Ø 0.36 across the flats, z −0.03 … 0.36 with a 0.045 chamfer; four 6-sided arms (azimuths
  166 / 346 / 76 / 256°, each pointing at its blade), centreline z 0.07 rising 10°, from 0.05 (0.13 buried in the post) to
  0.34 out, flat end faces. Joining faces: post top (B1), the post's +X flat at z 0.17 (B3), the four arm ends.
- **Base leaves** (N1–N3): 5-sided gems (flat underside, flanks, top ridge) at 0 / 0.4 / 0.75 L plus a tip, root on the
  ground. N1 and N3 lie lower and flatter than §2.4 (tips z 0.48 / 0.45) so they fill the front's full width at h .1–.2
  as the sheet does. N2 moved to x 0.04 (the sheet's front box −0.21 … +0.28) and W 0.50, so it hides the post foot.
- **Sprouts**: 4-sided two-stage spears, 0.18 / 0.15 tall, 14 tris.
- **Rocks / pebbles**: hulls of jittered ring stacks (`m033._ring_pts`), flat bases sunk 0.02, sloping tops; 38 / 38 / 22 / 22
  tris.
- **Placement guard**: `m047._Solids` holds the root members and rocks as they are built; every leaf and sprout is tested
  by ray parity and moved outward if more than 0.03 inside (none needed moving).

**Measured (front_sheet / sheet front):** W : H 1.203 / 1.256 (band 1.19–1.33 ✓); fill 0.589 / 0.590; G 88.0 / 90.4,
R 9.8 / 8.3, T 2.0 / 1.3 (≤ 2.5 ✓); top profile f .1–.9 `.62 .83 .73 .83 .64 .84 .96 .66 .69` vs `.60 .56 .77 .84 .64 .85
.95 .64 .67` (all within .08 except f .2, see notes); runs at h .70 **three** `[−.38 −.22] [−.20 −.05] [.04 .27]` vs
`[−.32 −.19] [−.17 −.06] [.03 .25]`; at h .85 B6 `[−.18 −.14]` and B1 `[.13 .29]` (sheet `[−.18 −.14] [.13 .30]`) plus a
one-pixel touch of B2's tip at −.39. f34_sheet W : H 1.197 (1.18–1.31 ✓). side_sheet W : H 0.997 (0.98–1.15 ✓). top_sheet
W : D 1.045 (1.05–1.25: at the edge). rear_sheet 1.241, r34_sheet 1.213 (1.20–1.40 ✓).

**Hero size 3.04 × 2.68 × 2.43** (targets 3.0 ± 0.2, 2.55 ± 0.2, 2.4 ± 0.1 ✓). Origin offset from the post (0.039, 0, −0.025).

| Blade | Seat | L | W | L : W | Lean / az | Seat depth | Fold / plate | Lowest z past 0.15 L | Max share inside another blade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | post top | 2.34 | 0.72 | 3.24 | 27° / 36° | 0.043 | 0.172 / 0.086 | 0.65 | 0.06 |
| B2 | arm 256° | 2.25 | 0.64 | 3.52 | 35° / 234° | 0.033 | 0.154 / 0.077 | 0.46 | 0 |
| B6 | arm 76° | 2.32 | 0.55 | 4.21 | 30° / 115° | 0.032 | 0.134 / 0.066 | 0.49 | 0 |
| B3 | post +X flat | 1.92 | 0.66 | 2.90 | 41° / 7° | 0.046 | 0.159 / 0.079 | 0.31 | 0.06 |
| B4 | arm 166° | 1.86 | 0.68 | 2.74 | 45° / 151° | 0.031 | 0.163 / 0.082 | 0.26 | 0 |
| B5 | arm 346° | 1.66 | 0.62 | 2.67 | 61° / 328° | 0.032 | 0.150 / 0.074 | 0.10 | 0 |

## Stage 2 — Optimisation and cleanup

`_post()` per object: triangulate, recalc normals per shell, flat shading, no custom normals, origin at the bbox bottom
centre (`o["m059_offset"]` = the origin in the build frame), `M.fix_bowties`, UVs.

| Object | Tris | Size (studs) | Shells | Collision |
| --- | --- | --- | --- | --- |
| BroadGrassClump (hero) | **704** / 900 | 3.04 × 2.68 × 2.43 | 20 (root 5, blades 6, leaves 3, sprouts 2, rocks 2, pebbles 2) | none |
| BroadGrassClumpBladeCenter | 58 | 1.06 × 0.81 × 2.11 | 1 | none |
| BroadGrassClumpBladeLeftTall | 58 | 0.93 × 1.15 × 1.93 | 1 | none |
| BroadGrassClumpBladeRightTall | 58 | 1.35 × 0.38 × 1.62 | 1 | none |
| BroadGrassClumpBladeLeftShort | 58 | 1.25 × 0.76 × 1.46 | 1 | none |
| BroadGrassClumpBladeRightShort | 58 | 1.28 × 0.94 × 0.96 | 1 | none |
| BroadGrassClumpRootBase | 124 | 0.71 × 0.71 × 0.39 | 5 | none |
| BroadGrassClumpRockLarge | 38 | 0.84 × 0.66 × 0.41 | 1 | hull |
| BroadGrassClumpRockMedium | 38 | 0.60 × 0.54 × 0.33 | 1 | hull |
| BroadGrassClumpRockSmall | 22 | 0.31 × 0.28 × 0.18 | 1 | none |

Hero tri split: blades 348, root 124, leaves 84, rocks 76, pebbles 44, sprouts 28. Every object: 0 non-manifold edges, 0
non-manifold (bowtie) verts, 0 boundary / wire / loose, 0 zero-area faces, 0 n-gons, 0 duplicate verts, normals outward,
transforms applied, origin offset (0, 0, 0); **0 winding errors** and 0 self-intersections in every shell; every shell
volume positive; smallest corner 7.4° (0 under 2°). `K.check` problems: none.

**Contact / float / bury** (`contact_report`, `bury_report`, `root_clearance`, `_blade_checks`): hero floating shells 0,
unchained 0 (blades chain through their root member; leaves, sprouts, rocks, pebbles and the root sit on the ground);
deepest sink −0.025 (decision 10: ≤ 0.03 ✓); dressing shells more than 0.05 inside a rock or the root: 0 (max 0.0); rocks
inside the root or each other: 0; rock / pebble clearance from the root base 0.37 / 0.39 / 0.44 / 0.56 (≥ 0.05 ✓); no
blade vertex in a rock; every blade seated 0.031–0.046 inside its member (0.03–0.06 ✓); no blade more than 6 % of its verts
inside another (≤ 30 % ✓); no blade vertex past 0.15 L below z 0.10 (≥ 0.05 ✓). The leaf guard moved nothing.

## Stage 3 — UV

`M.smart_uv(angle 45, ANGLE_BASED, margin 0.008)` + `m012._uv_unfold`: every object 0 overlaps, 0 flipped, min island gap
0.016, border 0.008, texel density min / median / max 1.0 / 1.0 / 1.0, conformal stretch p95 ≤ 1.043 (blades), 1.0 elsewhere.
Hero 199 islands. The exporter writes its own palette UVs.

## Stage 4 — Materials, colour and texture

**Calibration.** `m059.calibrate()` (`K.calibrate` on the faceted dome, 6 iterations) against the §5.4 targets gave
light `#80AD2A` (rendered 156,210,43), mid `#507C19` (93,146,25), dark `#325F19` (56,109,25), deep `#294F18` (45,89,24),
root `#7D5835` (157,107,66), root_light `#A67B58` (210,150,103), pebble `#7D6145` (157,118,82), rock `#888481`
(171,161,150), rock_light `#9F999A` (201,187,180), rock_deep `#716E6B` (142,133,123). Then corrected on the hero's own
renders (the dome is not the tuft: blades shade each other and the blades' green light bounces onto the rocks):

| Key | Final hex | Why changed from the dome value |
| --- | --- | --- |
| `m059_grass_light` | `#80AD2A` | unchanged (front light-tone median `#A6DE2F` vs sheet `#A1D12B`) |
| `m059_grass_mid` | `#5D8F1C` | the dome value rendered the hero's mid tone `#547F18` (sheet `#609619`); raised so the front all-green median sits within 15 |
| `m059_grass_dark` | `#325F19` | unchanged (front dark median `#426D18` vs `#386C19`) |
| `m059_grass_deep` | `#294F18` | unchanged (used only in the 75 % deep→dark mix at the B4 / B6 bases) |
| `m059_root` / `_light` | `#7D5835` / `#A67B58` | unchanged |
| `m059_pebble` | `#8E7050` | rendered `#806341` on the hero against `#A17447`–`#957858`; now `#9A7252` front, `#A07952` f34 |
| `m059_rock` | `#99908D` | the dome value rendered yellow-green on the hero (`#A8A191`, bounce from the blades) |
| `m059_rock_light` | `#A69D9A` | the dome's `#9F999A` had B > G (lavender rule); R > G > B now |
| `m059_rock_deep` | `#746C68` | kept R > G > B |

All rock keys R > G > B; greens: light 81°, mid 86°, dark 99°, deep 101° (no olive key).

**Colour by role and position along the blade (never by facing).** Each station band takes one tone from the blade's
ramp on the ladder deep 0 / dark 1 / mid 2 / light 3 (25 % mix steps): B1 mid → light from 0.35 L; B2 dark-mid base →
mid → 75 % light upper; B5 mid-light → light from 0.3 L; B3 dark → 75 % mid tip; B4 deep-dark base → dark → 50 % mid tip;
B6 deep-dark → dark → 75 % mid tip. Leaves: N1 mid → light tip, N2 light over a mid base, N3 dark base → mid. Root: root
with root_light joining faces (post top and chamfer, arm ends, 50 % on B3's flat). **Rocks and pebbles: broad noise
patches** (`K.noise_field`, a few facets across) of rock_light / rock / rock_deep (pebble / 50 % root), not height bands:
the first build used §5.3's height bands and `K.check` flagged both rock parts (corr 0.92–0.93, lighting painted in), since
on a squat block the top faces are the up-facing ones. **Tint:** per blade ±0.04 and per station band ±0.02, leaves
±0.04, root ±0.03 per member, rocks ±0.04 / pebbles ±0.03 per facet. Finish: grass rough 0.8–0.85 low-spec, root 0.85–0.9,
rocks 0.85–0.9, no metal, no emission. `kit_baked_shading` hero 0.04, blades 0.0–0.17, root base 0.38, rocks 0.0.

**Re-measured on the final renders (same masks):**

| | Sheet | Ours | Tolerance |
| --- | --- | --- | --- |
| front tones light / mid / dark | 25 / 32 / 43 | **22 / 36 / 42** | ± 8 ✓ |
| f34 tones | 23 / 37 / 39 | **26 / 37 / 38** | ± 8 ✓ |
| front top band light (h > .75) | 69 % | 60 % | ≥ 55 ✓ |
| front low band dark (h < .25) | 48 % | 48 % | ≥ 38 ✓ |
| front all-green median | `#58901E` | `#548219` | within 15 ✓ (G 14) |
| front green v > .7 | `#9ACC2C` | `#A4DB2E` | within 12: G 15 high (the lit lime planes are brighter) |
| front rock median / lit | `#ABA196` / `#C8BBB3` | `#A2968A` / `#CFC2B2` | median 9–12 darker (partly in blade shade); f34 `#A69E8D` vs `#ABA194` ✓ |
| pebbles (f34) | `#A17447` | `#A07952` | within 15 ✓ |

## Stage 5 — Lighting

Skipped: the sheet shows nothing glowing and no light (§7). No emission anywhere. Studio-side notes (Requires Manual
Validation): the blades keep lime tips and green bodies under the game sun (not olive); the dark blades stay green, not
black; rocks warm grey, pebbles tan. B2 leans toward the kit studio's key light and renders a dull mid there; under a sun
from the upper right, as on the sheet, its lit plane reads lime.

## Stage 6 — VFX

Skipped: the sheet shows no effect (§7); no sockets (checked in `build()`'s problems). A wind sway would be a Studio-side
script (decision 11).

## Modeller's notes for the verifier

- **Cameras.** `front_sheet (0, 5)` governs positions. `f34_sheet` is **(−8, 10)**, chosen by probing az −15 … +15 × e 6 /
  10 / 14 (score = top-profile + width-profile error + W : H error against the sheet's f34): (−8, 6) scored best (0.202) but
  is barely above the front; (−8, 10) scored 0.219 with W : H 1.195. The study's e 15 gave W : H 1.10 (our 2.68 depth shows
  too much ground plane). `r34_sheet (172, 10)`; `front34` / `rear34` the same. All `*_sheet` shots use the 3× lens with the
  floor hidden.
- **Rear / r34 / side tones** read 0 % light (rear 0 / 39 / 61 vs sheet 19 / 39 / 42): the kit studio's key comes from the
  front-left and the rear views get only the shadowless fill; painting the back faces lighter would be colour by facing.
- **Root visibility.** T (brown) front 2.0 %, f34 2.2, rear 2.0, r34 1.7, side 3.2, of which the two tan pebbles are
  about 1 % (the sheet's T is pebbles only: front 1.3, side 2.1). A sliver of root still shows: the post's foot between Rock
  B and the blade bases in the side view, and the back arm's underside under B6 in the rear. To hide most of it the arms are
  thinner (0.16 across the flats, spec 0.22), shorter (0.34 out, spec 0.50) and lower (centreline z 0.07, spec 0.10), the
  post top is 0.36 (spec 0.40) and B3's joining face sits at z 0.17 (spec 0.28). The RootBase part shot and `root_under`
  still show the cross + post with flat end faces.
- **Blade shape.** The folded plate (not §2.3's shouldered section) was chosen after the first renders: the shouldered
  convex section read as crystal shards and its facets barely changed tone under the studio light. With the fold, every
  blade shows a lit plane and a shade plane down its length (`blade_cu`), an edge band (`blade_edge`), and thickness side-on
  (`edge_side`). Tips close from the 0.82 L station (half-width 0.47–0.60) to a point: about 45–50° included angle, pointed
  but not a needle.
- **Depth (Y).** Tips pushed back / forward beyond §2.3 to reach the side's W : H and the depth target: B1 y +0.62 (spec
  +0.55; the side shows +0.68), B2 −1.34 (−1.20), B6 +1.34 (+1.15), B4 +0.72 (+0.55), B5 −0.85 (−0.80). Hero depth 2.68
  (2.55 ± 0.2 ✓).
- **Front top profile f .2** reads .83 against the sheet's .56: our B2 tip (x −0.82) lands in that sampling column, the
  sheet's just right of it. Moving B2's tip right to −0.74 merged the B2 and B6 runs at h .70 (two runs instead of three),
  so it stays at −0.82; the tip heights and runs match.
- **Top view.** A five-leaf star with B1 upright in the middle; N3 (behind Rock B) shows as a separate dark gem at the back
  right and Rock A sits front-left (the front governs rock placement, §3.4), so the sheet's "rocks at four corners" holds
  only for the front pebbles and Rock B.
- **Exploded shot** is a temp build (`EXPLODE["on"]`): blades drawn 0.9 off their joining faces along their axes, leaves
  lifted over the rocks, rocks and pebbles drawn out. Close-ups: `blade_cu` (−30, 20), `blade_edge` (B1 part edge-on),
  `edge_side` (90, 0), `root_under` (−20, −55, part), `root_cu` (−15, 15); `scale` (−20, 6) with a 5.5-stud marker (top at
  0.44 of it).
- **Blade parts** are built exactly as they sit in the hero (same lean, roll and colour); their origins are their own bbox
  bottom centres (offsets in `o["m059_offset"]`).
- Scratch: measuring scripts `meas.py`, `tonemap.py`, `pscore.py` and `final_meas.txt` in
  `C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m059w\`
  (run with `uv run --no-project --with pillow --with numpy python meas.py front_sheet sheet:front …`).

## Stage 7 verification (round 1)

Fresh verifier, read-only, background Blender on port 9881 on `wip/M059_verify.blend` (not saved). Renders in
`art/blender/renders/models/M059/verify/`: the `*_sheet` shots use the long lens with the floor hidden, plus the four
diagonals `az045/135/225/315_sheet`, `sideL_sheet`, `*_keyflip_sheet` and close-ups. Side-by-side montages:
`cmp_0..2.png`, `cmp_az8.png`, `cmp_cu.png`, `cmp_rear_keyflip.png`. My scripts are in the session scratchpad `m059v\`:
`a1.py` topology, `a2.py` shells / contact / ray-parity bury, `vis.py` 8-azimuth ray grid, `a3.py` / `a4.py` check, UV
and facing correlation, `meas.py` (the modeller's masks pointed at `verify/`).

**Verdict: PASS, 8 / 10.** No blockers. The front and f34 read like the sheet; the geometry is clean; nothing floats or
is buried; colour is by blade role and position, never by facing. The leftovers are below.

### Technical (re-measured)

| Check | Result |
| --- | --- |
| Tris | hero **704 / 900**; blades 58 each, RootBase 124, RockLarge / RockMedium 38, RockSmall 22 |
| Size | hero 3.038 × 2.680 × 2.425 (targets 3.0 ± 0.2, 2.55 ± 0.2, 2.4 ± 0.1 ✓); parts as in stage 2 |
| Origin / transforms | every object's bbox bottom centre at its origin (offset 0, 0, 0); rotation 0, scale 1; no modifiers; hero offset from the post (0.039, 0, −0.025) |
| Topology (all 10 objects) | 0 non-manifold edges, 0 bowtie verts, 0 boundary / wire / loose, 0 zero-area, 0 n-gons or quads, 0 duplicate verts, no custom normals, all flat |
| Shells (hero 20) | root 5, rocks 2, pebbles 2, blades 6, leaves 3, sprouts 2; **0 winding errors and 0 self-intersecting face pairs in every shell**; every volume positive |
| Floating | 0 (nearest gap of any non-ground shell 0.0); unchained 0. Blades touch their member: B1 post, B2 arm 256°, B6 arm 76°, B3 post (+ arm 346°), B4 arm 166°, B5 arm 346° |
| Buried | 0 leaves, sprouts, pebbles or rocks inside a rock or the root (all 0.000, ray parity, 3 rays); no blade in a rock; max blade share inside another blade 0.06. Deepest blade vertex in the root: B3 **0.080**, B1 0.062 (others 0.013–0.024); spec ≤ 0.06 at the base face; invisible |
| Sink | lowest point −0.025 (≤ 0.03 ✓); rocks / pebbles / leaves / sprouts −0.020; B3–B5 base rings −0.009 / −0.017 |
| Clearances | rocks and pebbles ≥ 0.067 from every other shell (root ≥ 0.05 ✓) |
| UV | 0 overlaps, 0 flipped, min gap 0.016, border 0.008, density 1.0, stretch p95 ≤ 1.043 |
| `K.check` | no problems (KITSTAT ok on all ten) |
| Collision tags | hero, blades, RootBase, RockSmall `none`; RockLarge / RockMedium `hull` (decision 8 ✓) |

**Blade shape (measured from the rings):** L / W max / L : W are B1 2.34 / 0.72 / 3.25, B2 2.25 / 0.64 / 3.52, B6
2.32 / 0.55 / **4.21**, B3 1.92 / 0.66 / 2.90, B4 1.86 / 0.68 / 2.74, B5 1.66 / 0.62 / 2.67 (exploded 3.2 / 3.3 / 3.7 /
2.8 / 2.3 / 2.5). Plate 0.066–0.086, section depth at mid 0.17–0.22, so each blade has real thickness side-on
(`blade_edge.png` shows a solid sliver, not a card). Tip included angle 43–52° (spec 25–35°): pointed, not needles, a
little blunter than the sheet.

### Eight azimuths (`vis.py`, ray grid on the hero)

| View | Blade px within 12° / 20° of edge-on | Root share of visible px | Narrowest blade (projected / true width) |
| --- | --- | --- | --- |
| front (0, 5) | 0.6 / 3.6 % | 0.4 % | B5 0.67 |
| az45 | 2.7 / 14.4 | 2.8 | B2 0.24, B1 0.33 |
| side 90 | 5.1 / 9.9 | 1.5 | B6 0.42 |
| az135 | 3.9 / 7.9 | 2.3 | B6 0.39 |
| rear (180, 5) | 0.6 / 1.7 | 1.8 | B5 0.54 |
| az225 | 1.8 / 6.3 | 3.0 | B1 0.14 (mostly hidden) |
| side 270 | 6.2 / 17.2 | 1.9 | B6 0.42 |
| az315 | 1.9 / 4.7 | 0.9 | B6 0.39 |
| top | 2.9 / 10.8 | 1.2 | all ≥ 0.81 |

Edge-on blade area is at most 6.2 % in every view (target ≤ 10 ✓). From every azimuth the blades read as broad, thick,
ridged lanceolates of different lengths and leans. There are no hedgehog or agave fans, needles or flat cards.

### Views against the sheet (same masks; sheet / ours)

| View | W : H | G / R / T | Tones light / mid / dark | Notes |
| --- | --- | --- | --- | --- |
| front (0, 5) | 1.256 / **1.203** ✓ | 90.4 / 88.0, 8.3 / 9.8, 1.3 / 2.0 ✓ | 25/32/43 / **22/36/42** ✓; top band light 69 / 60 ✓; low band dark 48 / 48 ✓ | three runs at h .70 ✓ (−.38…−.22, −.20…−.05, +.04…+.27); top profile within .08 except f .0 (.27 / .16) and **f .2 (.83 / .56)** |
| f34 (−8, 10) | 1.245 / **1.197** ✓ | 92.6 / 88.6 (edge of ±4), 6.8 / 9.3 ✓ | 23/37/39 / **26/37/38** ✓ | at the study's (0, 15): W : H 1.10 (out of band) |
| rear (180, 5) | 1.381 / 1.241 ✓ | 91.1 / 91.5 ✓ | 19/39/42 / **0/37/62** ✗ | |
| r34 (172, 10) | 1.247 / 1.213 ✓ | 92.2 / 92.9 ✓ | 15/52/33 / **0/38/62** ✗ | |
| side (90, 5) | 1.06 / **0.997** ✓ | T 2.1 / **3.2** | 10/50/40 / 0/49/51 | top profile f .4 **.33 / .83** (a notch where the sheet has its narrow mid blade), f 1.0 **.88 / .62** |
| top (0, 89) | 1.137 / **1.045** (band 1.05–1.25, 0.005 under) | | 14/58/27 / 24/42/34 | a rough, irregular five-leaf star |

**Colours** (rendered medians):
- **Greens.** Front green `#558420` vs `#58901E` (G 12 ✓ ≤ 15). Front v > .7 `#A4DB2F` vs `#9ACC2C` (**G +15**,
  tolerance 12). Light `#A6DE2F` vs `#A1D12B` (G +13). Mid `#5B8A1E` (86°, s .78) vs `#609619`. Dark `#446D1A` (**90°**,
  s .76) vs `#386C19` (98°): a little yellower than the sheet's dark, but still a saturated green, not olive.
- **Rocks.** Front `#A2978A` / f34 `#A89E8F` vs `#ABA194` (f34 ✓, front 9–14 darker); rock lit `#CABDAE` vs `#C9BDB4` ✓.
  Every rock key is R > G > B (`#99908D`, `#A69D9A`, `#746C68`, mixes `#A09694` / `#867E7A`): **never lavender**.
- **Pebbles.** Front `#9B7252` / f34 `#A07952` vs `#957858` / `#9D7045` ✓.
- **Keys.** Light `#80AD2A` 81°, mid `#5D8F1C` 86°, dark `#325F19` 99°, deep mixes 100°.

**Facing check (code and numbers).** The builder paints by position and role only; nothing reads a normal:
- blades per station band by `BLADES[...]["tone"]` (role and fraction of L);
- leaves per band;
- root by member (joining faces lighter);
- rocks and pebbles by `K.noise_field` of the face centre (position).

Correlation of painted luminance with normal z: hero grass 0.08; blade parts 0.10–0.31 (their luminance follows height
along the blade, 0.74–0.96, by design). Hero rocks −0.30, and −0.51 with the key light (RockMedium −0.70): the noise
patches happen to put the darker keys on the key-lit faces. That is chance, not facing paint, though it slightly flattens
Rock B's shading.

### The modeller's deviations and leftovers

| Item | Verdict | Visible against the sheet? |
| --- | --- | --- |
| Folded-plate section instead of §2.3's shouldered one | **Accept.** Each blade shows a lit plane and a shade plane meeting at a midrib, an edge band and real thickness (section depth 0.17–0.22): close-up 2's read | Numeric only (closer to the sheet than the spec) |
| Root base only mostly hidden (decision 4: never visible) | **Minor.** T (brown) is front 2.0, f34 2.2, rear 2.0, side 3.2 %. The root alone is 0.4 % of the front and 1.5–3.0 % of the side, diagonal and rear views. A brown post stub shows between the blade bases in side, az45, az135 (`az135_sheet`, `root_cu135`) and rear. The sheet's close-up 3 does show the post top, so this fits the sheet but not decision 4 | Visible in the non-governing views; not in front / f34 |
| Root arms shortened (0.34 out, 0.16 across) to hide them | **Minor.** The `BroadGrassClumpRootBase` part reads as a stump with stubby arms; the exploded / key-parts cell shows a cross whose arms reach well past the post. It is an exported reuse part | Visible on the part |
| Tip positions moved for depth (B1 +0.62, B2 −1.34, B6 +1.34, B4 +0.72, B5 −0.85) | **Accept with a note.** Front X / Z are unchanged; depth 2.68 ✓. On the side, B6's tip makes the far-back peak h .88 where the sheet's back blade is h .62. The sheet's mid blade at h .83 has no partner here (notch .33 at f .4) | Visible on the side only |
| N1 / N3 lower, N2 moved | **Minor.** N2 reads like the sheet's lime pyramid. In the front, N1 shows only as a thin lime sliver behind Rock A, and N3 hides behind Rock B; the sheet's front and f34 show three chunky gems at the foot. N3 is dark (dark → mid ramp) and shows as a separate dark lump in the side, az45, top and r34 | Visible at the foot |
| f34 camera (−8, 10) | **Accept.** It is inside the spec's probe range (az ±20, e 10–20, at the low edge); W : H 1.197 ✓. The sheet's f34 shows more ground and more of the rock tops | Camera choice; slight |
| Rear / r34 / side at 0 % light "because of the studio key light" | **Minor; the light is only part of the cause.** The key does come from the front-left (direction −0.49, −0.59, 0.64). But with the key turned 180° (`rear_keyflip_sheet`) the rear still reads 2 / 41 / 57 (r34 3 / 43 / 55). From behind, the dark blades B6 (19.6 % of the rear's pixels), B4 (18.4) and B3 (17.0) stand in front with B1 behind them; the sheet's rear has lime B1 in front and dominant. So the rear is darker because of the composition and the blade roles, not just the light | **Visible:** rear and r34 read darker than the sheet (dark 62 vs 42 %) |
| B2 dull mid green | **Accept.** B2's body renders `#567D19` (83°, s .80), a mid green, not olive; the sheet's B2 has a lime face | Slight |
| Top view: N3 a separate dark gem | **Minor** (as above). Top W : D is 1.045, 0.005 under its band | Visible on the top |
| Front top profile at f .2 (.83 vs .56) | **Accept.** B2's tip lands in that column; the tip heights and the three runs at h .70 match | Numeric only |
| Softer blade facet contrast | **Accept.** The value spread per height band matches (h .5–.75 v p10/50/90 .40/.52/.86 vs .43/.63/.87). The lit and shade planes inside one blade are less crisp than close-up 2's lime and mid faces | Slight |
| Lit greens G +15 | **Accept.** The v > .7 median is G +15 (tolerance 12) and the light median G +13: a slightly brighter lime | Numeric only |

### Minors to fix if a round 2 is run (none blocks)

1. **Rear tone (the most visible leftover).** Make the rear read like the sheet's, with lime B1 in front. Either give B6
   a mid tip and a narrower face toward the rear, or turn B1 / B6 so that from 180° B1 is not behind B6 and B3. Target
   under the kit studio: rear light ≥ 11 %, dark ≤ 50 %.
2. **Root stub.** 1.5–3 % brown shows in the side, diagonal and rear views (decision 4 says never). Bring B3's sheath or
   a base leaf over the post's back flank, or lower the post top behind B1.
3. **RootBase part.** Its arms are stubby against the exploded cross (0.34 out vs about 0.5).
4. **N1 / N3.** Make them visible chunky gems at the foot in the front and f34, and colour N3 mid green rather than dark.
5. **Numeric:**
   - B6 L : W 4.21 (exploded 3.7);
   - B3's deepest point 0.08 inside the post (≤ 0.06);
   - dark-tone hue 90° (≥ 95);
   - top W : D 1.045 (≥ 1.05).

### Main session ruling (2026-10-30)
Round 1 PASSED at 8/10, so the model is committed.
- **Deviations accepted:** the folded-plate blade section, the moved tips, and the f34 camera at (−8, 10).
- **Decision 4 amended:** a small root-post stub may show at the side, diagonal and rear (0.4 % front, 1.5–3 % elsewhere). The sheet's root close-up shows the post too.
- **Recorded for polish:** verifier minors 1–5, chiefly bringing lime B1 forward in the rear view, longer RootBase part arms, and chunkier N1/N3.

Export: 10 assets, 1216 tris, 0 problems.
