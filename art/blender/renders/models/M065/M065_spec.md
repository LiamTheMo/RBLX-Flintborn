# 065 Forest Wildflowers — spec

Reference: `art/blender/assets/references/065.png` (1024 × 1536 px). INDEX.md row 65: "Flintborn wildflowers model study".
The sheet's own header reads **"63"** (top left) and the footer **"PAGE 63/132"**, title **"WILDFLOWERS"**, subtitle "Forest
wildflowers in blue, purple and pink."; footer "FLINTBORN — INDIVIDUAL MODEL STUDY" (our number is INDEX's 065, §3.1).
Builder: `art/blender/kit/mcp/m065.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows no effect** (§7). It is a **common
forest-floor flower clump that will be repeated**, so it is budgeted as a small prop extended (§4.3, decision §8.14). The
plant rules of WorldModeling §1, §6 and §18 apply: **three different chunky flower heads (a hanging purple bell on a
crook, a tall blue five-petal star, a cupped pink bloom) on thick square stems over a rosette of broad, thick, faceted
leaves, with a few faceted stones at the foot**. Petals are broad blunt plates with real thickness, the bell and bloom are
closed solids with an inside, leaves are closed solids (never flat cards), and **no part is turned toward a camera**
(054 / 057 / 058: parts turned toward the front / rear cameras read as balls with flaps from the sides).

Sheet text (paraphrased):
- **Title block (top left):** "63", "WILDFLOWERS"; forest wildflowers in blue, purple and pink.
- **Style note (top centre):** a stylised nature asset: chunky low poly with broad flat shading, simple geometric shapes
  and clean silhouettes, in the Flintborn look.
- **"MATERIAL PALETTE" (top right):** seven labelled swatches: Flower Purple, Flower Blue, Flower Pink, Leaf Light, Leaf
  Dark, Stone (Pale Gray), Stone (Warm Brown) (§5.1). **There is no yellow swatch**, although both flower centres are
  yellow (§3.10).
- **Assembled:** "FRONT THREE-QUARTER (ASSEMBLED)", "REAR THREE-QUARTER (ASSEMBLED)".
- **"ORTHOGRAPHIC VIEWS (ASSEMBLED)":** "FRONT", "SIDE (RIGHT)", "REAR", "TOP".
- **"EXPLODED CONSTRUCTION (PARTS & ASSEMBLY)":** labels "Flower Head (Purple Bell)", "Flower Head (Blue Star)", "Flower
  Head (Pink Bloom)", "Stem (Purple)", "Stem (Blue)", "Stem (Pink)", "Leaf (Reusable)", "Root Stones (Decorative)", "Leaf
  Cluster Base (Junction)". Drawn: the bell head together with the bent top of its stem and a green cap; the star head
  with its calyx and a short neck; the bloom head with its calyx; three straight square stem pieces with arrows down into
  the cluster base; four loose leaves with short square petiole stubs (two either side, one raised and one low) with
  dashed arrows out from the base; five faceted stones (three or four grey, one brown); the cluster base is a fan of tall
  leaves over a ring of short chunky leaves round a small dark hub.
- **"CONSTRUCTION CLOSE-UPS":**
  1. "FLOWER CENTER DETAIL": the blue star from the front: five broad faceted petals round an octagonal pale-yellow
     centre; callout: simple faceted petals and centre, broad flat faces, nothing thin.
  2. "STEM TO BASE JUNCTION": a square stem standing in a low collar with angled faces on the cluster base, leaves round
     it and a grey stone in front; callout: the stem slots into the leaf cluster base; clean angled faces; no extras.
  3. "UNDERSIDE VIEW": from below: a flat hexagonal olive base with leaves round it and stones beside it; callout: a flat
     simple bottom; leaves and stems meet at the central base; stones sit round the base; nothing hidden.
- **"PARTS (ISOLATED)":** Purple Bell Head, Blue Star Head, Pink Bloom Head, Stem (Example), Leaf (Example), Rock (Gray),
  Rock (Brown).
- **"MODELING NOTES":** chunky low-poly forms with broad flat faces; simple shapes and clean silhouettes; petals,
  stems and leaves are separate modular parts; the leaf cluster base is one piece with clear joining faces for the stems
  and leaves; rocks are simple faceted stones and optional; keep proportions consistent across the views; no thin
  geometry, high-poly detail or textures; match the Flintborn primitive stylised look.
- **Game context and the old kit:**
  - **W07 row 3 `Wildflowers`** (`art/blender/scripts/kit/W07/wildflowers.py`; manifest `art/roblox/kit/W07/manifest.json`;
    goals `art/blender/renders/kit/W07/wildflowers_goals.md`) is the old kit's take on this subject, from a different
    row reference. Manifest: **5.92 wide × 5.20 deep × 5.41 tall**, 1740 tris (budget 2500), collision `none`, no VFX;
    note "purple hanging bells with calyx caps, a blue star flower, pink blooms over a leaf rosette, pebbles". Variants
    `WildflowersBlueStar`, `…PinkBloom`, `…PurpleBell`; parts `WildflowersFlowerHead`, `…Leaf`, `…Stem` (builder names
    `WildflowerFlowerHead`, `WildflowerLeaf`, `WildflowerStem`). `MODEL_PROGRESS.md` row 69: "mostly-done: flat pink
    star, dark bud; thin blue star; straight stems". Its goals log: the leaves formed a dark bowl, the pink cups were flat
    saucers, the stems were thin, the stones sat outside the mound, and (its worst habit) the leaves were finally
    **re-oriented by facing toward the camera**. **All `Wildflower*` names are taken** (§8).
  - **Related:** the lobby's `WildflowerWhite` (3.3 wide × 2.3–2.5 tall); V07 `HeatherBellFlower`; 061 Meadow Herb (2.2
    tall, the closest sibling: three heads on thick stems over a kite rosette); 059 Grass Tuft (2.4); 060 Broadleaf Fern
    (3.0). §1.5 keeps 065 apart from them.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The page is pale paper
(`#F9F6EC`); each panel is cream with a soft warm-grey cast shadow falling left of the plant. Measured grey rules: header
block to y ~95; assembled frame x 12–1013, y ~100–445 (no divider between f34 and r34; the palette panel starts at
x 822); ortho title bar y 457–489, cells y 490–739 with dividers x 300, 510, 771 and labels at y ~715–730; exploded x
12–638, y 783–1289; close-ups x 648–1013, y 783–1287; parts x 12–616, y 1300–1496; notes x 625–1013.
- **Cells** (`m.V`, `m.X` in the study folder): f34 (12,100,470,415); r34 (470,100,820,415); front (13,491,299,712); side
  (301,491,509,712); rear (512,491,770,712); top (772,491,1012,712); exploded (13,784,637,1288); cu1 "flower center"
  (658,792,875,948); cu2 "stem to base" (658,958,875,1118); cu3 "underside" (658,1130,875,1282); parts row (13,1340,616,1440).
  The cell boxes stop above the labels, so no text needs blanking.
- **Swatches** (inner boxes, sd ≤ 3.1): Flower Purple (843,42,871,68), Flower Blue (843,87,871,114), Flower Pink
  (843,126,871,157), Leaf Light (843,176,871,202), Leaf Dark (843,219,871,248), Stone Gray (843,264,871,291), Stone Brown
  (843,310,871,337).
- **Masks** (`cls()` in `m.py`, HSV, h in degrees):
  - **G**, green (leaves, stems, calyces, hub): h 60–170, s ≥ 0.25, v ≥ 0.06.
  - **U**, purple (bell): h 249–300, s ≥ 0.20, v ≥ 0.15. **B**, blue (star): h 205–249, s ≥ 0.25, v ≥ 0.15.
  - **P**, pink (bloom): h ≥ 300 or < 8, s ≥ 0.15, v ≥ 0.35.
  - **Y**, yellow centres: h 35–65 with s ≥ 0.20 and v ≥ 0.80 (the star's pale lemon), or h 35–60 with s ≥ 0.45, v ≥ 0.55,
    or h 27–35 with s ≥ 0.80, v ≥ 0.75 (the bloom bead's orange shade).
  - **N**, brown stone: h 8–35, s ≥ 0.30, 0.2 ≤ v < 0.85, not Y. **S**, grey stone: s < 0.25, 0.12 ≤ v < 0.84.
  - Specks under 60 px are dropped.
  - **Caveat on S:** on the sheet S also catches the dark contact shade on the ground under the leaves. The side cell has
    no stones yet reads S 3.5 %, so **sheet rock share ≈ N + (S − 3.5)**: front ≈ 2.5 %, rear ≈ 4 %, side ≈ 0. On our renders
    (floor hidden) S is the grey rocks only.
  - **Green tones:** light v ≥ 0.70, dark v < 0.42, mid the rest (the 061 convention).

**Scratch study material** (no Blender) in `<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m065_study\`.
Run with `C:/Users/Orang/.local/bin/uv.exe run --no-project --with pillow --with numpy --with scipy python <script> < /dev/null`.
- **Helpers:** `m.py` (boxes, `cls`, `tones`, `clsimg`, `hx`, `hsvs`), `zoom.py` (`zoom.py x0 y0 x1 y1 scale out.png [grid]`),
  `probe2.py` (`probe2.py x,y …` → hex and HSV), `lines2.py` (frame rules), `sw.py` (swatches).
- **Measurements:** `measure.py` → `measure_out.txt` (bbox, W : H, shares, fill, tones, top profile, widths per height,
  fifths and ranges per class) and `cls_views.png`; `blobs.py` → `blobs_out.txt` (each head and stone per view: box,
  centroid, height span); `nobud.py` (front / f34 shares without the bud, §3.3); `expl.py` → `expl_out.txt` (exploded and
  parts-row blobs: L, W, L : W, width profile, tone); `samp.py` → `samp_out.txt` (class and tone medians per view);
  `reg2.py` → `reg2_out.txt` (masked named regions: stems, calyces, leaves, rocks, centres); `leaves.py` → `leaves_out.txt`
  (individual leaf tones).
- **Zooms:** `z_f34.png`, `z_r34.png` (2×, gridded), `z_front.png`, `z_side.png`, `z_rear.png`, `z_top.png` (3×, gridded),
  `z_fr_stems.png` (5×: stems, crook, bud), `z_fr_rock.png`, `z_f34_ros.png` (rosette), `z_expl.png`, `z_expl_heads.png`,
  `z_expl_base.png` (cluster base), `z_cu.png`, `z_parts.png`, `z_parts_heads.png`, `z_pal.png`.
- **On our renders:** copy 061's `meas.py` (`<temp>\...\scratchpad\m061w\meas.py`), point it at this folder's `m.py` and
  use `cls()`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** a repeated forest-floor flower clump with three different heads and decorative stones: small prop
  extended (decision §8.14). **Budget: hero ceiling 1600 tris, plan about 1350–1500; every part under 1000.** Three
  different head types (a closed bell with an inside, a five-petal star, a two-ring cupped bloom), 17 closed leaves and
  five rocks cost more than 061's three identical daisies.
- **Overall read (check this first).** A **broad, low clump about 1.3 × as wide as tall**:
  - **three different flowers** at three heights: the **blue five-petal star tallest**, slightly right of centre and a
    little behind, facing front-up; the **purple bell** hanging mouth-down at the **far left** from a **shepherd's-crook
    stem** whose bend is the second-highest point; the **pink cupped bloom lowest**, at the **far right**, opening toward
    the front;
  - **thick square green stems**: the bell's rising up-left and hooking over, the star's nearly straight, the bloom's
    leaning out to the right;
  - a **rosette of broad faceted leaves** filling the lower 45–55 % of the height and the full width: an upright fan of
    mid-green leaves behind the stems (tips z 1.0–1.3), big leaves spreading out to both sides on petioles, big lime leaves
    drooping toward the viewer front and back with their tips on the ground, and short chunky leaves round the rim;
  - **five small faceted stones** tucked at the foot, partly under the leaf tips: a mauve-grey one front-left, a brown one
    front-right, and three at the back.
  - It reads **green with three colour accents**: front G ≈ 63 %, purple 9, blue 10, pink 10.5, yellow 1, stones 2.5
    (bud excluded, §3.3).
- **Focal silhouettes, in order:**
  1. The blue star at the top (centre bead h .84) and the purple bell hanging from its hook (h .48–.81).
  2. The pink bloom at the right (h .41–.74) and the crook's bend (h ≈ .87).
  3. The rosette: a broad green mound with pointed leaf tips on both sides (spreading tips at h .27–.35) and lime leaves
     drooping at the foot; stones peeping out at the front corners.
- **Target size: 2.4 tall (the star's top petal tip), 3.0 wide (X) × 2.3 deep (Y)** (decision §8.1). Tolerances: height
  ±0.08, width ±0.2, depth ±0.2.
  - **How it was derived.** Front silhouette 247 × 185 px → **77.1 px / stud** at H 2.4 → W 3.20. Rear 217 × 186 → 2.80.
    Side 146 × 185 → **1.89 deep** (no star drawn, §3.4). Top 199 × 183 (W : D 1.087); the heads there are drawn about
    0.96 × the front's size (star 81 px against 87, bloom 63 against 63, bell 60 against 63), so about 74 px / stud →
    2.69 × 2.47. Width taken as 3.0 (front, rear and top together; the front governs positions with x compressed × 0.97),
    depth 2.3 (side and top together).
  - **Why 2.4.**
    - The star's head is **Ø 1.13** at this size, the same as 061's daisy heads (Ø 1.1), so the two meadow flowers share
      one head scale. The bell is 0.86 long with a mouth of Ø 0.82, the bloom Ø 0.82; all inside WorldModeling §3.2's
      bloom range (0.25–0.55 of the height: star 0.47, bell and bloom 0.34).
    - 0.44 C against the 5.5-stud character: **just above knee height**, a touch over §3.2's flowering-herb band (0.15–0.40 C);
      forest wildflowers carry their heads on long stems above the leaves.
    - It equals 059 Grass Tuft (2.4) and stands 0.2 over 061 Meadow Herb (2.2), well under 060 Fern (3.0). In a mixed patch
      the star and the bell's crook (z 2.0–2.4) stand among the tuft's tallest tips and above the herb's daisies.
    - At 2.4 the parts stay readable: stems 0.13 square, star petals 0.50 × 0.32, leaves 0.45–0.6 wide, stones 0.26–0.48.
    - The old W07 hero (5.41 tall, 0.98 C) is chest-high: giant flowers. At 2.0 the stems fall to 0.11 and the star bead to
      0.21 (thin at gameplay distance).
  - **Against the character (5.5):** 0.44 C tall, 0.55 C wide.
- **Build frame:** front −Y, +X right, ground z 0, the cluster-base hub axis at (0, 0). The origin is the bbox bottom
  centre; the clump is not symmetric, so record the origin's offset from the hub axis (expected ≤ 0.10).

### 1.2 Measured views (`measure.py`, `blobs.py`, `nobud.py`)

| View (box) | Silhouette bbox (px) | W : H | G | U purple | B blue | P pink | Y | N + S | fill | green light / mid / dark |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (12,100,470,415) | 57–464 × 114–409 (408 × 296) | 1.378 | 59.6 % | 11.2 | 8.4 | 13.1 | 1.0 | 1.2 + 5.6 | 0.597 | 28 / 45 / 27 |
| Rear three-quarter (470,100,820,415) | 495–814 × 121–404 (320 × 284) | 1.127 | 68.7 | 7.6 | 7.8 | 9.3 | 0.0 | 1.2 + 5.4 | 0.599 | 30 / 45 / 25 |
| **Front** (13,491,299,712) | 33–279 × 519–703 (247 × 185) | **1.335** | **59.7** | **10.3** | **9.4** | **13.7** | **0.9** | **1.3 + 4.7** | **0.592** | **27 / 43 / 30** |
| Side (301,491,509,712) | 342–487 × 519–703 (146 × 185) | 0.789 | 65.3 | 13.4 | 0.2 | 17.4 | 0.1 | 0.1 + 3.5 | 0.559 | 22 / 45 / 34 |
| Rear (512,491,770,712) | 532–748 × 518–703 (217 × 186) | 1.167 | 62.7 | 9.1 | 9.5 | 11.0 | 0.2 | 2.9 + 4.7 | 0.564 | 23 / 47 / 30 |
| Top (772,491,1012,712) | 791–989 × 514–696 (199 × 183) | W : D 1.087 | 60.6 | 9.1 | 12.0 | 11.3 | 2.0 | 0.5 + 4.5 | 0.655 | 29 / 42 / 29 |

- Shares are of the silhouette (background and floor shadow excluded; S includes ground contact shade, see the caveat).
  **Fill** = silhouette / bbox area.
- **Without the front bud (§3.3, the recommended build):** front G 63.3, U 9.1, B 9.7, P 10.5, Y 1.0 (the bud is 5.8 % of
  the front silhouette); f34 G 63.0, U 9.9, B 8.7, P 10.2, Y 1.1 (bud 5.4 %).
- **The rear and r34 show the star and the bloom from behind:** Y ≤ 0.2 % (the star's calyx and the bloom's outer petals
  face the camera). The rear blue is deep (`#3B58E0`), the petals' backs in shade.
- **The side draws no star** (B 0.2 %, §3.4) and no stones (N 0.1).
- **Verifier tolerance:** G ±5, U / B / P ±2.5, Y ±0.8 points, rocks ±1.5; W : H ±0.08; fill ±0.05; head centres ±0.06 H;
  tones ±8.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.1 W):

| f | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .36 | .72 | .85 | .93 | .53 | .86 | .97 | .97 | .82 | .73 | .29 |
| r34 | .38 | .72 | .80 | .78 | .92 | .97 | .88 | .88 | .87 | .72 | .42 |
| **Front** | .34 | .73 | .86 | .87 | .69 | .87 | .96 | .98 | .83 | .72 | .55 |
| Side | .56 | .66 | .81 | .88 | .94 | .98 | .99 | .81 | .44 | .46 | .08 |
| Rear | .28 | .71 | .77 | .87 | .97 | .88 | .89 | .86 | .83 | .73 | .58 |

**Width per height** (silhouette width at h .02 → .98 in 11 steps, fraction of W):

```
f34    .43 .92 .81 .94 .70 .65 .92 .87 .66 .51 .20
r34    .57 .96 .83 .85 .95 .54 .83 .87 .69 .44 .04
front  .51 .91 .82 .95 .72 .83 .94 .84 .66 .49 .22
side   .46 .93 .66 .72 .54 .74 .62 .50 .53 .36 .12
rear   .49 .86 .78 .94 .45 .86 .96 .85 .54 .24 .03
```

- Reading (front): h .1–.3 the rosette across nearly the full width (.82–.95: the spreading leaves are the widest
  element, leaf width at h < .5 = the full 247 px); a waist at h .4 (.72: leaf tips end, only stems, the bell's lobes and
  the bloom's base); h .5–.7 the three heads side by side (.83–.94); h .8–.9 the star and the crook (.49–.66); the top
  is the star's upper petal. The dip at f .4 in the front / f34 top profile is the gap between the crook and the star.
- Side: the bell's crook is the top (h .99), the bloom at the left (front) at h .42–.74, the rosette .66–.93 wide low down.

**Height fifths and ranges** (bottom → top, % of each class; x as fractions of W from the bbox left):
- Green: front 34 / 46 / 13 / 4 / 2; f34 30 / 47 / 17 / 4 / 3; rear 30 / 45 / 15 / 8 / 2; side 39 / 34 / 17 / 4 / 6.
  **Green stays below h .5 except the stems, the crook and the calyces.**
- Purple (bell): front h .45–.81, x .02–.67 (bud included at x .46), centroid (.21, h .62); rear h .47–.76, x .71–.99;
  side h .62–.94 (drawn higher, §3.4); top x .00–.57.
- Blue (star): front h .45–.99 (petals .68–.99), x .15–.81, centroid (.63, h .84); rear h .48–.99, centroid (.42, .82).
- Pink: front h .41–.83 (bloom .41–.74; the bud .50–.71), centroid (.75, h .59); rear h .44–.77, x .01–.27; side h .42–.74,
  x .00–.42.

**Heads** (`blobs.py`; studs at 77.1 px / stud, front x from the plant axis x 152 compressed × 0.97, z from the ground
y 703; rear image left = world +X; top 74 px / stud, image up = +Y back):

| Head | Front blob (px) → (x, z) | f34 blob | r34 / Rear → (world x, z) | Side (image x → world y, z) | Top → (x, y) | Facing in the front |
| --- | --- | --- | --- | --- | --- | --- |
| **Star** (blue) | petals 147–233 × 519–578; bead (190, 548) → (**+0.48, 2.01**) | 252–387 × 114–209, bead (319, 160) | r34 588–700 × 121–207; rear bead area (623, 551) → (+0.19, 1.96) | not drawn | (893, 579) → (+0.04, **+0.35**) | front-up: ring 87 × 60 px (ratio .69); top ratio .89 |
| **Bell** (purple) | 38–100 × 554–614, centroid (73, 585) → (**−0.99, 1.53**); body z 1.15–1.94; cap (85, 550) → (−0.84, 1.98); crook apex (100, 537) → (−0.65, **2.12**) | 72–181 × 159–260 | rear 687–747 × 561–616 → (−0.97, 1.47) | (402, 557) → (y −0.23, z 1.90) | (824, 628) → (−0.89, **−0.31**) | hangs mouth-down, its axis about 15° off vertical toward the front-left |
| **Bloom** (pink) | 216–278 × 566–627, centre bead (242, 600) → (**+1.13, 1.34**) | 362–462 × 184–283, bead (403, 240) | rear 534–590 × 560–622 → (+0.98, 1.42) | (375, 597) → (y −0.58, z 1.38) | (958, 618) → (+0.92, **−0.18**) | opening toward the front, a little up and toward the centre (bead at .42 of the bloom's width) |
| Bud (pink + violet) | 127–168 × 571–625 → (−0.06, 1.47) | 222–287 × 195–273 | **absent** | absent | absent | a closed tulip bud on its own stem, front only (§3.3) |

- **Heights are consistent across front, f34, r34 and rear:** star bead z 1.96–2.01, bell body z 1.15–1.94 (centroid
  1.47–1.61), bloom bead z 1.34–1.42. The side draws the bell 0.35 higher; the front governs (§3.4).
- **Head sizes:** star Ø 87 px → **1.13** (top 81 px / 74 → 1.09); star bead front 20 × 13 px, top 19 × 18 → **Ø 0.26**. Bell
  66 px from cap to mouth → **0.86**, mouth Ø 63 px → **0.82** including the flared lobes, dome top Ø ≈ 0.38. Bloom Ø 63 px →
  **0.82**, about 0.5 deep; its bead front 12 px, top 16 × 17 → **Ø 0.20**. Bud 0.54 × 0.62.
- **Counts:** star **five petals** (every view, the close-up and the parts row); bell **six flared pointed lobes** (4–5 seen
  per side in the parts row); bloom **five outer + five inner petals** (parts row, f34, top).

**Stems** (front, 5× zoom `z_fr_stems.png`):
- Widths: bell stem 9 px at z 1.34, star stem 10 px at z 1.34, bloom stem 9–10 px, bud stem 7 px → **0.12–0.13**. They show
  two flat faces (one lit, one dark) in every view; close-up 2 and the parts row draw them **square**.
- Bell stem (front): x −0.36 at z 0.82 → −0.45 at z 1.34 → −0.57 at z 1.85 → the crook apex (−0.65, 2.12) → a short
  descending hook into the cap at (−0.84, 1.98). Side: the hook bends toward image left (the front). Top: the bell sits
  front-left. **The crook bends toward the front-left (az ≈ 215°).**
- Star stem: x +0.29 at z 0.82 → +0.35 at z 1.34 → the calyx (front y 573–592, z 1.44–1.69) behind the lower petals.
- Bloom stem: x +0.60 at z 0.82 → +0.78 at z 1.05 → the calyx at (+0.83, 0.95–1.2).

**Leaves** (front 3×, f34 2.4×; studs at H 2.4; x from the axis):

| Leaf (tier) | Front tip (px) → (x, z) | What it is | f34 tone (`leaves.py`) |
| --- | --- | --- | --- |
| Spread far-left, raised | (34, 645) → (−1.48, 0.75) | a big broad leaf spreading left on a petiole, rising then flattening | mid `#548D1B` (L 3 %) |
| Spread low-left | (42, 690) → (−1.39, 0.17) | a big leaf lying out left-front over the grey stone | mid |
| Spread far-right, raised | (279, 653) → (+1.60, 0.65) | the same to the right | light / mid `#83B71D` (L 52 %) |
| Spread low-right | (272, 690) → (+1.51, 0.17) | lying out right-front, over the brown stone | mid |
| Upright fan, right | (205, 605) → (+0.67, **1.27**) | the fan's tallest | mid with a lime tip |
| Upright fan, left / centre / right-low | (95, 622) / (125, 623) / (218, 622) → (−0.72, 1.05) / (−0.26, 1.04) / (+0.83, 1.05) | behind the stems | mid `#669F19` / `#7CAE1F` |
| Front-left big, drooping | (120, 703), top z 0.47 → (−0.40, 0.0) | a broad lime leaf pointing down toward the viewer, tip on the ground | **light** `#8EC022` (L 78 %) |
| Front-right big, drooping | (190, 703), top z 0.69 → (+0.48, 0.0) | the same, right | **light** `#92C420` (L 69 %) |
| Rim small, front-left / front-right | (80, 690) / (250, 690) | short chunky leaves at the stones | dark `#527A3A` / lime `#A0CD2E` |

- **Leaf top:** the fan's tips reach **z 1.0–1.3 (h .43–.54)**; green above h .55 is only stems, the crook and calyces.
- **Rear:** a big lime leaf at front-centre (world x ≈ +0.1, top z 0.6, `#8EBE20`), a smaller lime one at world x ≈ −0.3,
  mid-green spreading leaves both sides (`#65A41E`, `#629D20`), upright fan tips at z 1.07–1.30.
- **Counts per view:** leaves front 14–16, f34 15–17, rear 13–15, side 8–10, top 14–16 radiating round the centre.
- **Shapes:** broad ovate kites with a centre ridge (two facets a side), widest at 0.45–0.6 L, a pointed but not needle tip.
  The big front leaves are the broadest (L : W ≈ 1.5); the fan and spreading leaves 1.9–2.4; the rim leaves short and
  blunt (≈ 1.4).

**Stones** (front, rear and top; N = brown, S = grey):

| Stone | Front (px) → x, size | Rear / r34 → world x | Top | Notes |
| --- | --- | --- | --- | --- |
| Grey, front-left | 50–88 × 682–702 → x −1.25 … −0.80, 0.46 wide × 0.26 tall | — | edge at the front-left | mauve-grey `#867771`, lit `#C1AEA4` |
| Brown, front-right | 213–240 × 679–697 → x +0.77 … +1.09, 0.35 × 0.23 | — | (945, 667) → (+0.74, −0.84) | `#92582F`, lit `#D48E52` |
| Brown, back-right | — | rear 573–601 → +0.48 … +0.84; r34 at image left | hidden | `#906842` |
| Grey, back-left | — | rear 680–712 → −0.54 … −0.95; r34 right of centre | hidden | `#A9978C` |
| Small brown, back far-left | — | rear 712–735 → −0.95 … −1.25 | hidden | small chip |

### 1.3 Silhouette and composition per view

**Front (`z_front.png`) — governs positions and heights.** A low view. The star stands slightly right of centre on a
nearly straight stem, its face toward the viewer and up (the five-petal ring an ellipse with the pale bead on top). The
bell hangs at the far left from the crook: its stem rises from the rosette leaning left, bends sharply over at z 2.1 and
drops a short hook into a green faceted cap; the bell's six lobes flare out at the mouth. The bloom sits low at the
right, a deep pink cup opening toward the viewer, its golden bead and deep-rose throat visible, a dark calyx under it on
a stem leaning out from the centre. A small pink-and-violet closed bud stands between the bell stem and the star stem
(§3.3). The rosette: an upright fan of mid leaves behind the stems, big leaves spreading flat to both sides (tips at
x ±1.5), two big lime leaves drooping toward the viewer in front, chunky rim leaves, a grey stone front-left and a brown
stone front-right half under the leaves.

**Front three-quarter (`z_f34.png`) — governs the read.** Drawn **nearly frontal from higher up**: head x fractions .19 /
.48 / .64 / .86 (bell / bud / star / bloom) against the front's .16 / .46 / .63 / .86; W : H 1.378 against 1.335; the
rosette's upper faces and the drooping front leaves show more. Lit from the upper right: lime on the leaves' upper faces,
dark in the creases and on the stems' shaded faces; the bell lavender lit with deep violet shade on its lower lobes and
inside; the star's petals periwinkle with deeper blue facets; the bloom's outer petals light pink, its inner petals and
throat deep rose.
- **Petals** (star) are broad lozenges with a blunt point and a centre ridge; thickness shows as a darker side band
  (about 0.05 studs).
- **Stems** are square prisms (one lit face, one dark), the bell's crook made of straight segments with sharp bends.
- **Leaves** are faceted ovate kites with a ridge: one half lit, one half shaded, widest near the middle.

**Rear three-quarter (`z_r34.png`).** The star from behind (deep blue petal backs round a green calyx and its neck on the
straight stem), the bell at the right hanging from the crook (bending toward the right = world −X), the bloom at the
left showing its outer petals; the rosette as from the front (spreading leaves, a big lime leaf toward this camera, the
upright fan); a brown stone at the left and a grey one right of centre.

**Rear (`z_rear.png`).** A near mirror of the front: bloom left, star centre (calyx visible), bell right; a brown stone
at the left, a small dark pebble at the centre, a grey stone and a small brown chip at the right.

**Side, right (`z_side.png`).** A narrow view (W : H 0.79) from +X (image left = front −Y): the bell's stem rising up the
middle and hooking toward the front, the bell hanging under the hook (drawn higher than the front, h .62–.94); the bloom
at the front (image left), nearest the camera, opening toward the front; leaves rising to both sides. **No star and no
stones** (§3.4).

**Top (`z_top.png`).** The star face-up at the centre-back (five petals, pale bead), the bell at the front-left (seen from
above: its dome, cap and lobes), the bloom at the right a little in front of the axis, face-up (golden bead in a deep pink
cup), over a star of 14–16 leaves radiating from the centre; one stone peeps out at the front-right. No bud.

**Flower center detail (close-up 1).** Five broad periwinkle petals (`#8592FD`, shade `#334BD1`) with flat facets and a
blunt point, overlapping at the base round an **octagonal flat-topped pale-yellow bead** (`#FDE76F`, shade `#EAB44D`)
that is about half a petal's length across; nothing thin.

**Stem to base junction (close-up 2).** A square stem (lit face `#6FAB1A`, shade face `#4A821D`) standing in a low
light-green collar with angled faces (`#81B920`), leaf bases crowding round it, a grey stone in front.

**Underside view (close-up 3).** From below: a **flat hexagonal base** in olive (`#6D823F`), the leaves' undersides
radiating round it, two stones touching it.

### 1.4 Parts (exploded `z_expl.png`, `z_expl_heads.png`, `z_expl_base.png`; parts row `z_parts.png`, `z_parts_heads.png`)

The exploded is a front three-quarter at a larger scale than the hero (its star is 105 px against the hero's 87 at the
front's scale), parts lifted off. **The hero governs every size, angle and position (§3.8); the exploded and parts row
govern each part's shape.**

`expl.py` (principal-axis length L, max width W, the width profile in tenths):

| Part (label) | Box (px) | L × W, L : W | Width profile | Tone | Notes |
| --- | --- | --- | --- | --- | --- |
| Purple bell head (exploded) | bell (118,831,203,914) + crook / cap (170,802,243,875) | bell 82 × 89 (0.92) | 32 46 51 55 59 65 76 86 61 40 (narrow dome → wide mouth) | `#9A61F7`, lit `#B478FD`, shade `#4F2BB8` | a **six-sided faceted bell**: dome top, straight-ish flanks widening to a mouth of **six flared pointed lobes**; a **green six-sided cap** on top; the exploded keeps the **crook** (three straight square segments, a sharp over-the-top bend) with the head |
| Purple Bell Head (parts) | (28,1356,101,1427) | 73 × 76 (0.96) | 20 36 43 47 52 59 69 68 52 12 | `#AA70FA` | the bell alone; the lower lobes deep violet (the inside showing) |
| Blue star head (exploded) | (284,794,388,859) + calyx / neck (322,847,346,884) | 105 × 67 (seen tilted) | | `#7E8FFC`, shade `#2437C4` | **five petals**, each a broad lozenge with a blunt point (W : L ≈ 0.62) and a centre ridge; the octagonal pale bead; a **five-sided green calyx cone** and a short square neck |
| Blue Star Head (parts) | (120,1350,191,1409) + calyx (148,1403,165,1430) | 72 × 60 | | `#6F83FB`, calyx `#295518` | the same with the neck stub |
| Pink bloom head (exploded) | (454,845,542,925) | 93 × 81 (1.14) | 30 52 62 67 76 80 74 62 55 37 | `#FC6D9B`, lit `#FEBFD5`, shade `#E14D7F` | a **cupped bloom**: **five broad outer petals** flaring out and up, **five inner petals** standing up inside, blunt rounded ends with a crease; golden bead; a dark calyx with pointed sepals |
| Pink Bloom Head (parts) | (210,1351,285,1415) | 76 × 65 (W : H 1.17) | 28 44 51 58 64 64 57 52 46 30 | `#FC76A4`, calyx `#2C5810` | the same, seen from the front-up: a deep cup |
| Stems (Purple / Blue / Pink) | (232,896,268,1020) / (328,907,347,1020) / (432,954,467,1046) | 126 × 25 / 114 × 20 / 96 × 22 (L : W 5.1 / 5.6 / 4.3) | uniform (23 → 18) | `#72AB1D` / `#7FB61C` / `#588919` | **straight square prisms**, the top end cut square or slanted |
| Stem (Example) (parts) | (320,1344,345,1432) | 89 × 25 (3.6) | 15 22 20 18 18 18 17 17 17 16 | `#57941D`, lit `#7BB321`, shade `#336518` | a square prism with a slanted top cut |
| Leaf (Reusable) ×4 (exploded) | (133,1041,246,1125), (461,1044,588,1136), (101,1123,211,1171), (493,1131,612,1190) | 129 × 69 / 145 × 65 / 111 × 46 / 120 × 60 (**1.86 / 2.24 / 2.40 / 1.99**) | 21 33 51 62 67 64 55 45 35 14 | `#609D1D` / `#71A71E` / `#80B521` / `#518F23` | broad ovate kites, widest at 0.4–0.6 L, a centre ridge, pointed tip; **a short square petiole stub** at the base (the raised pair) |
| Leaf (Example) (parts) | (391,1344,446,1435) | 102 × 53, **1.91** | 10 26 40 46 51 51 46 36 25 11 | `#5A9728`, lit `#73B233`, shade `#3A731F` | the same kite, thick, pointed both ends |
| Leaf Cluster Base (exploded) | (252,1046,449,1217) | 204 × 171 | | `#69A417`, lit `#9DCC2A`, shade `#33640B` | **four tall upright leaves in a fan (two big centre ones, two leaning out), two leaning side leaves, and five short chunky leaves round the foot**, with a small dark hub socket under the centre |
| Root Stones (exploded) | grey (136,1193,207,1236), grey (204,1217,272,1258), small grey (447,1231,492,1259), brown (466,1204,531,1253) | 71 × 43 / 68 × 41 / 45 × 28 / 65 × 49 | | grey `#B6A295`, brown `#B1834E` | faceted nuggets, flat base, 8–12 broad facets |
| Rock (Gray) / Rock (Brown) (parts) | (471,1396,527,1430) / (551,1400,593,1430) | 59 × 37 (W : H 1.6) / 43 × 31 (1.4) | | `#A89388` / `#A8673E` | squat faceted gems; the grey one mauve-grey (R > G > B) |

- **Star petal construction:** a closed lozenge plate: outline of 6 verts (base point at r 0.07 under the bead, two base
  shoulders, two wide shoulders at 0.5 L, a blunt point or a short tip pair at 1.0 L), a shallow centre ridge on top, a
  flat underside, thickness 0.05 (0.065 at the ridge). Tip angle 80–100°. **Never a needle** (the W07 "thin blue star").
- **Star bead:** an octagonal flat-topped gem Ø 0.26, height 0.10, a bevel ring (close-up 1), its lower half among the petal
  bases.
- **Bell construction:** a lathed six-sided closed shell: cap seat ring Ø 0.16 → dome shoulder Ø 0.36 at 0.15 L → flank
  ring Ø 0.50 at 0.65 L → mouth ring Ø 0.66 at 0.92 L, with **six pointed lobes** (one per side, tip at Ø 0.82, flared 30–40°
  out and curling slightly up) between them; an **inner wall** 0.04–0.05 inside the outer (the mouth has a real rim and a
  shallow inside, WorldModeling §6.6), closed by an inner dome 0.30 L up. Never an open cone.
- **Bloom construction:** five outer petals (L 0.42 from r 0.06, W 0.36 at 0.6 L, cupped 45–55° up from the bloom plane,
  a blunt rounded end of 2–3 verts, a centre crease, thickness 0.05) and five inner petals (L 0.30, W 0.28, cupped 65–75°,
  turned 36° between the outer ones), all rising from a shared seat on the calyx; a golden bead Ø 0.20 at the bottom of
  the cup. Never a flat saucer (the W07 failure).
- **Calyces:** star — a five-sided cone Ø 0.10 → 0.26 over 0.16 with five short pointed sepal tips; bloom — a five-sided
  cup Ø 0.12 → 0.30 over 0.18 with five pointed sepals reaching 0.06 up the outer petals; bell — a six-sided collar
  Ø 0.18 × 0.10 (the cap), lighter green.
- **Leaf construction:** a closed kite: base point, two wide-shoulder verts at 0.5 L, tip; a raised centre ridge on top
  (+0.04) and a shallow keel below (+0.02); edges 0.06 thick; the halves meet at the ridge in a shallow V (15–25°) so one
  half catches the light. The reusable spreading leaves add a square petiole stub 0.10 × 0.10 × 0.15 at the base.

### 1.5 How 065 differs from its siblings and the old kit (binding: the verifier checks these)

| | W07 `Wildflowers` (old kit) | Lobby `WildflowerWhite` | 061 Meadow Herb | 059 Grass Tuft | **065 Forest Wildflowers** |
| --- | --- | --- | --- | --- | --- |
| Size | 5.92 × 5.20 × 5.41 tall | 3.3 × 2.3–2.5 | 2.55 × 2.1 × 2.2 | 3.0 × 2.55 × 2.4 | **3.0 × 2.3 × 2.4 tall, W : H 1.2–1.35** |
| Flowers | bells, a flat star with a white dot, flat pink saucers, a bud | flat white heads | three identical five-petal daisies | none | **three different heads: a six-lobed purple bell hanging from a crook (z 1.15–1.94), a blue five-petal star (bead z 1.98, the top), a cupped two-ring pink bloom (bead z 1.36)** |
| Stems | hexagonal, then thickened to 0.15 | thin | hex Ø 0.14 | none | **square 0.13; the bell's a shepherd's crook of straight segments** |
| Leaves | 10 pointed leaves re-oriented toward the camera | strap leaves | 17 kites | six tall blades | **17 closed broad kites: a 5-leaf upright fan, 4 spreading leaves on petioles, 4 big drooping lime leaves (front and back), 4 chunky rim leaves; placed by growth only** |
| Base | none | none | octagonal hub | hidden cross + post, rocks | **a hexagonal hub (flat olive underside), hidden by leaves** |
| Stones | a grey stone and an orange chip, outside the mound | none | none | grey rocks + tan pebbles | **five faceted stones (two mauve-grey, three warm brown) tucked under the leaf tips** |
| Colour | one leaf green, flat flower keys | | cream, gold, three greens | three greens | **lavender bell with a violet inside, periwinkle star with a pale-lemon bead, pink bloom with a deep-rose throat and a golden bead, lime / mid / dark leaves by role, mauve-grey and warm-brown stones** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, the hub axis at (0, 0)). Plan azimuths: 0° = +X,
counter-clockwise, 90° = +Y (back), 270° = −Y (front).

### 2.1 Stack (binding contact chain, bottom up; every seat gap ≤ 0.03)

| Piece | Sits on / in | Contact |
| --- | --- | --- |
| Hub (one closed hexagonal block) | ground | flat underside at z 0 … −0.03 |
| Fan leaves (5) and drooping leaves (4) | the hub's flank / top rim | each base point 0.04–0.08 inside the hub (a butt join, no boolean) |
| Spreading leaves (4) | the hub's flank | the petiole stub's end 0.04–0.08 inside the hub (the exploded's dashed arrows) |
| Rim leaves (4) | the ground beside the hub | base on the ground (keel z 0 … −0.02), touching the hub or a neighbour leaf |
| Stems (3) | the hub top | stem foot 0.06–0.08 inside the hub top (close-up 2's slot; no hole modelled in the hero, §3.6) |
| Bell cap | the end of the crook's hook | the hook's end 0.04–0.06 inside the cap's top |
| Bell | the cap | the bell's dome seat ring 0.03–0.05 inside the cap's bottom |
| Star / bloom calyx | the top of its stem | the stem's top 0.05–0.08 inside the calyx bottom |
| Star petals (5) / bloom petals (10) | the calyx top | each petal's base on / 0.02–0.04 into the calyx rim, under the bead; never floating above it |
| Beads (2) | the calyx top, among the petal bases | the lower 40–50 % among the petal bases; buried ≤ 0.06 |
| Stones (5) | the ground | flat base at z 0 … −0.02; touching a leaf above them or the hub (within 0.03) |

### 2.2 Hub (the "Leaf Cluster Base" hub; hidden in the hero)

- **6-sided block**, **Ø 0.50 at z 0, Ø 0.42 at the top z 0.18**, the top a flat hexagon with a low chamfer ring (close-up 2's
  angled faces), the bottom flat (close-up 3). Ring radii ±5 % per vertex.
- Hidden by the leaves in every assembled view (seen only from below). About 24 tris.

### 2.3 Stems and heads

| Head | Stem foot (x, y) on the hub top | Stem path (spine stations) | Head seat | Head centre | Facing / axis | Size |
| --- | --- | --- | --- | --- | --- | --- |
| **Star** (blue) | (+0.06, +0.08) | leaning right and back, nearly straight: (0.06, 0.08, 0.18) → (0.28, 0.24, 0.90) → (0.36, 0.40, 1.62) → a small bend to the calyx axis | calyx bottom at C − 0.22 n ≈ (0.32, 0.43, 1.80) | **C = (+0.40, +0.30, 1.96)** (petal plane centre; bead top 0.10 above) | **normal n: az 300°, tilt 45° from vertical** (front-right-up) | Ø 1.14 |
| **Bell** (purple) | (−0.08, +0.02) | rising up-left: (−0.08, 0.02, 0.18) → (−0.32, 0.02, 0.80) → (−0.46, 0.00, 1.35) → (−0.58, −0.05, 1.82) → **crook apex (−0.66, −0.10, 2.12)** → a short descending hook (az 215°, 40° below the horizontal) → its end at (−0.84, −0.22, 2.02) | cap Ø 0.18 × 0.10 on the hook's end, axis along the hook | bell top (seat) at (−0.87, −0.23, 1.93) | **axis down, tilted 15° toward az 215°** (front-left) | 0.80 long from the seat, mouth Ø 0.82 at its lobe tips; mouth centre ≈ (−1.03, −0.34, 1.20) |
| **Bloom** (pink) | (+0.08, −0.06) | leaning out right: (0.08, −0.06, 0.18) → (0.45, −0.10, 0.62) → (0.80, −0.14, 0.98) → the calyx | calyx bottom at C − 0.24 n ≈ (1.14, −0.12, 1.18) | **C = (+1.10, −0.28, 1.36)** (cup centre at the bead) | **normal n: az 255°, tilt 42°** (front, a little toward the centre, up) | rim Ø 0.82, cup depth 0.40 |

- **Stems:** **square prisms, side 0.13** (0.135 at the foot, 0.12 under the head), 3–5 straight segments, rings mitred at
  each bend so the bends are crisp (the sheet's crook is three straight segments, never a smooth arc); flat faces only; one
  face of each stem turned about 20° off the front so both faces read in the front and the sides.
- **Bell crook:** the rise leans 8–12° left; the apex is a sharp bend (about 125°) into the hook; the hook is 0.24 long.
  The crook's bend is the second-highest point (z 2.12 + half the stem, ≈ 2.19).
- **Why these facings (§3.4):** star front ratio .61 (sheet .69), top .71 (sheet .89), sides ±.35, rear sees its back and
  calyx; bloom front .65, top .74, from +X it shows its cup in profile opening to the front (the side cell), the rear sees
  its outer petals and calyx. **No head is turned toward a camera per view.**
- **Height check:** star top petal tip 1.96 + 0.57 × sin 45° + 0.03 ≈ **2.39–2.40** (the model's top); lowest star petal
  tip ≈ 1.56 (sheet 1.63); bell lobes z ≈ 1.12–1.30; bloom rim z ≈ 1.00–1.75 (sheet 0.98–1.78).
- **Bud:** not built (decision §8.3). If the main session wants it: a closed tulip bud 0.42 wide × 0.55 tall (three pink
  outer petals and two violet inner ones showing in front), on a fourth square stem (side 0.10) from the hub to
  (−0.06, −0.20, 1.20), bud centre z 1.47; about +90 tris.

### 2.4 Leaves (17)

Each leaf is a closed faceted kite (§1.4) placed by its **base point** (on the hub, or the ground for the rim leaves), its
**azimuth** and **pitch** (above the horizontal at the base; a gentle arch along the leaf adds 10–20° droop toward the
tip), and **roll** (rotation about its own axis: the top face stays up and outward; **never rolled toward a camera**).

| Leaf | Tier | Az | Base → tip (x, y, z) | L | W | Pitch → tip | Tone (§5) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **F1** fan left | cluster base | 172° | hub → (−0.72, +0.10, 1.05) | 1.15 | 0.46 | 60° | mid, light tip |
| **F2** fan back-left | cluster base | 120° | hub → (−0.26, +0.40, 1.28) | 1.20 | 0.48 | 72° | mid, light tip |
| **F3** fan back-centre | cluster base | 85° | hub → (+0.08, +0.45, 1.05) | 1.05 | 0.46 | 68° | mid |
| **F4** fan back-right (tallest) | cluster base | 40° | hub → (+0.62, +0.42, 1.28) | 1.25 | 0.50 | 62° | mid → light tip |
| **F5** fan right | cluster base | 345° | hub → (+0.82, −0.20, 1.05) | 1.15 | 0.46 | 55° | light, mid base |
| **S1** spread left, raised | reusable (petiole) | 178° | hub → (−1.48, +0.05, 0.72) | 1.30 (petiole 0.15) | 0.56 | 30° then flattening | mid |
| **S2** spread left-front, low | reusable (petiole) | 202° | hub → (−1.36, −0.48, 0.18) | 1.15 | 0.52 | 12° then drooping over R1 | mid, dark base |
| **S3** spread right, raised | reusable (petiole) | 4° | hub → (+1.52, +0.10, 0.66) | 1.30 | 0.56 | 28° then flattening | light / mid (light outer half) |
| **S4** spread right-front, low | reusable (petiole) | 335° | hub → (+1.40, −0.58, 0.18) | 1.15 | 0.52 | 12° then drooping over R2 | mid |
| **N1** front-left big, drooping | cluster base | 248° | hub → (−0.40, −1.05, 0.02): tip on the ground | 1.05 | 0.62 | rises to z 0.47 at 0.35 L, then droops | light |
| **N2** front-right big, drooping | cluster base | 290° | hub → (+0.48, −1.05, 0.02) | 1.10 | 0.66 | rises to z 0.65, then droops | light |
| **N3** back-centre big, drooping | cluster base | 82° | hub → (+0.15, +1.08, 0.02) | 1.05 | 0.62 | rises to z 0.60, then droops | light |
| **N4** back-left, drooping | cluster base | 122° | hub → (−0.55, +0.92, 0.03) | 0.90 | 0.54 | rises to z 0.45, then droops | light, mid base |
| **B1** rim front-left | rim (ground) | 228° | ground (−0.28, −0.25) → (−0.78, −0.62, 0.08) | 0.55 | 0.40 | 10–15°, a low arch (top z 0.22) | dark |
| **B2** rim front-right | rim (ground) | 318° | ground (+0.28, −0.25) → (+0.80, −0.60, 0.08) | 0.55 | 0.40 | 12° | mid → light tip |
| **B3** rim back-left | rim (ground) | 150° | ground (−0.30, +0.25) → (−0.85, +0.55, 0.08) | 0.52 | 0.38 | 10° | dark |
| **B4** rim back-right | rim (ground) | 28° | ground (+0.30, +0.25) → (+0.85, +0.55, 0.08) | 0.52 | 0.38 | 12° | dark → mid tip |

- **Shape:** kite, widest at 0.45–0.6 L, tip angle 50–70° (never a needle), base 0.25 W wide where it meets the hub (the
  petiole on S1–S4); L : W 1.5–1.7 for N1–N4, 2.0–2.5 for the fan and spreading leaves, 1.3–1.5 for the chunky rim
  leaves; thickness 0.06 at the edges, 0.12 at the ridge (0.10 edges on the rim leaves, so they never read as thin spikes —
  061's verifier minor 2).
- **Hierarchy check:** tips at z 1.05–1.28 (fan), 0.66–0.72 (raised spread), ≈ 0.2 (low spread), ≈ 0 (drooping and rim).
  Front leaf top at h .53, the rosette's widest at h .1–.3 (§1.2).
- **Keep the stems visible:** the bell stem must read clearly from z ≈ 0.6 up in the front and f34 (the sheet shows it
  rising out of the rosette from h .25); F1 / S1 must not cover it. The star stem shows from z ≈ 0.9 up, the bloom's from
  z ≈ 0.75 (061's verifier minor 3: a head that looks seated on the leaves).
- **Clearances:** no leaf more than 25 % inside another; every leaf vertex ≥ z −0.01 except the sunk rim bases; the
  drooping tips rest within 0.03 of the ground; no leaf cuts a stem by more than 0.03 outside the hub junction (move the
  leaf, not the stem); leaves over a stone touch it (≤ 0.03) but enter it ≤ 0.05.

### 2.5 Stones (5)

| Stone | Centre (x, y) | Size W × D × H | Yaw | Build |
| --- | --- | --- | --- | --- |
| **R1** grey, front-left | (−1.02, −0.56) | 0.48 × 0.40 × 0.28 | 20° | a faceted nugget: 6–7-sided base ring (r ±10 %), widest ring at 0.35 h, a shoulder ring at 0.75 h pulled in 25 %, a sloping 4–5-sided top; 10–12 broad facets; flat base (§12.1) |
| **R2** brown, front-right | (+0.93, −0.64) | 0.36 × 0.30 × 0.24 | −30° | as R1, 8–10 facets |
| **R3** brown, back-right | (+0.68, +0.66) | 0.36 × 0.30 × 0.22 | 45° | as R2 |
| **R4** grey, back-left | (−0.74, +0.64) | 0.44 × 0.36 × 0.27 | −15° | as R1 |
| **R5** brown chip, back far-left | (−1.16, +0.32) | 0.26 × 0.22 × 0.15 | 70° | a 5-sided nugget, 6–8 faces |

- Squat angular blocks (H 0.5–0.65 W, parts row W : H 1.4–1.6), **never `K.hull_rock` eggs, never lavender** (R > G > B on
  the grey). `m047._rock` / `m053._rock` or 059's rock builder can serve; reshape them.
- **Visibility:** about 2.5 % of the front silhouette and 4 % of the rear, ≈ 0 from the right side (tuck R2 / R3 under S3 /
  S4's droop) — 060's blocker 1 was rocks standing bare from the side and rear.

### 2.6 Expected extents and screen checks

- **Extents:** X −1.48 … +1.52 (S1 / S3 tips; the bell's lobes reach about −1.44, the bloom's rim about +1.51), Y −1.08 …
  +1.08 (N1 / N2 and N3 tips; rocks to −0.80 / +0.83; the star's back petals to about +0.75), Z 0 … 2.40 (the star's upper
  petal). Bbox about 3.0 × 2.2 × 2.4.
- **Checks on the renders** (floor hidden; `meas.py` with this folder's `m.py`):
  - **front_sheet (0, 5)** — governs positions:
    - W : H 1.20–1.38 (sheet 1.335); G 63.3 ± 5, U 9.1 ± 2.5, B 9.7 ± 2.5, P 10.5 ± 2.5, Y 1.0 ± 0.8 (bud-free
      targets), rocks 2.5 ± 1.5; fill 0.58 ± 0.05.
    - The top profile within ±0.08 for f .1–.9 (the dip at f .4 between the crook and the star must show); head centres
      at §1.2's (x, z) ±0.06 H; the star clearly the highest head, the bell hanging lower left, the bloom lowest right.
    - Green fifths within ±6 of 34 / 46 / 13 / 4 / 2; flower colours ≥ 90 % above h .4.
    - Green tones light / mid / dark 27 / 43 / 30 ± 8.
  - **f34_sheet (−10, 12)** (probe az −20 … 0 × e 10 / 15 / 20; keep the best; §3.2): W : H as close to 1.378 as a camera
    allows (061 reached only 1.04 against 1.286, so this is a soft check); G 63 ± 5, U / B / P per the bud-free f34 values;
    tones 28 / 45 / 27 ± 8; every head shows its shape (bell lobes, five star petals and bead, the bloom's cup and throat).
  - **rear_sheet (180, 5), r34_sheet (170, 12)** (probe 160 … 200): W : H 1.08–1.25; Y ≤ 0.6 % (the star from behind with
    its calyx, the bloom's outer petals); rocks 4 ± 1.5; G 63–69 ± 5.
  - **side_sheet** from +X (the sheet's "SIDE (RIGHT)": image left = front; the bloom nearest, at image left; render
    (90, 5) and (270, 5) and keep the one that matches): W : H 0.78–0.95; the bell's crook up the middle hooking toward the
    front; the bloom at the front; leaves rising to both sides; rocks ≤ 1.5 %. The star shows here although the sheet omits
    it (§3.4).
  - **top_sheet (0, 85)** (also (0, 60)): content only: the star face-up at the centre-back, the bell's dome front-left, the
    bloom's cup at the right, over a star of 14–17 radiating leaves.

## 3. View conflicts and resolutions

### 3.1 Sheet number
- **Evidence.** The header says "63" and the footer "PAGE 63/132"; INDEX.md row 65 lists `065.png` as "Flintborn
  wildflowers model study".
- **Resolution.** Our number is 065 (file name, keys `m065_*`). Note the header in the export notes only.

### 3.2 The three-quarter views are near-frontal and near-rear, drawn from higher up
- **Evidence.** f34 head x fractions .19 / .48 / .64 / .86 against the front's .16 / .46 / .63 / .86; W : H 1.378 against
  1.335; the rosette's upper faces show more. r34 against the rear: .16 / .46 / .80 vs .14 / .42 / .83.
- **Resolution (decision §8.9).** `front_sheet (0, 5)` governs positions; `f34_sheet` governs the read and the shares.
  Probe az −20 … 0 (e 10–20), keep the best and record the camera (061 settled on (−10, 12)); the same for r34 at 160 … 200.

### 3.3 A fourth flower (the pink-and-violet bud) appears only in the front and f34
- **Evidence.** The front and f34 draw a small closed tulip bud (pink outer petals, a violet petal in front, its own calyx
  and stem) between the bell stem and the star stem at z ≈ 1.47. The rear, r34, side and top don't draw it, though at
  that height it would show above the rosette from the rear. The exploded shows three heads and three stems, the parts row
  three heads, the subtitle names three colours.
- **Resolution (decision §8.3).** **Three heads** (exploded, parts row, rear, r34, side, top, text). The front and f34
  targets in §2.6 are the bud-free shares (`nobud.py`). Alternative: the bud as a fourth head (§2.3, +90 tris).

### 3.4 Head positions and facings differ per view (the generator redraws each cell)
- **Evidence.**
  - The star sits at x +0.48 in the front, +0.19 in the rear and +0.04 in the top; it faces the front (ratio .69), the top
    (.89) and is open from the rear too — no single flat head does all three.
  - **The side draws no star** and puts the bell 0.35 higher (h .62–.94 against the front's .48–.81).
  - The bloom's depth: y −0.18 (top) vs −0.58 (side).
- **Resolution (decision §8.3).** **One fixed, coherent orientation per head** (§2.3): star at (+0.40, +0.30) facing az 300°
  tilt 45°; bloom at (+1.10, −0.28) facing az 255° tilt 42°; the bell hanging from the crook at (−0.87, −0.23) tilted 15°
  toward the front-left. The front governs x and z, the top and side together give y. The side will show the star and a
  lower bell than the sheet; judge it for the crook, the bloom's profile and the leaf spread only. **Never turn a head,
  petal or leaf per camera** (054 / 057 / 058, and the old W07's facing-driven leaves).

### 3.5 Square stems (close-up 2, parts row) vs the hexagonal stems of the siblings
- **Evidence.** Close-up 2 shows a square stem with two faces; the parts-row stem is a square prism with a slanted cut;
  the assembled stems show one lit and one dark face. 061 and the W07 builder used hexagons.
- **Resolution.** **Square prisms (side 0.13)**, as the sheet. Turn each stem's faces about 20° off the front so the front
  and the sides both see two faces, never one flat board.

### 3.6 Stem slot: a socket in the cluster base
- **Evidence.** Close-up 2: the stem slots into a low collar on the cluster base; the exploded shows a dark socket under
  the fan; close-up 3 shows a flat hexagonal bottom. In every assembled view the base is hidden by leaves.
- **Resolution.** The hero's hub is a **closed block with no hole**; stems sink 0.06–0.08 into its top (a hidden butt
  join, as 061's hub). The `…LeafBase` part shows the hub; a square recess on its top is optional (decision §8.6;
  recommended: none — "no extra details").

### 3.7 The bell's crook belongs to the head in the exploded, to the stem in the hero
- **Evidence.** The exploded draws the bell head with the bent top of its stem attached; "Stem (Purple)" is straight. The
  parts row draws the bell alone.
- **Resolution.** In the hero the crook is part of the bell stem (one square tube from the hub through the bend to the cap).
  The `…PurpleBell` part is the bell with its cap (the parts row); the crook is not a separate part.

### 3.8 Exploded scale vs the hero
- **Resolution.** The hero governs size, lean and position; the exploded and the parts row govern each part's outline
  (bell lobes, star petal lozenge, bloom's two rings, calyx shapes, leaf L : W, the petiole stub, the cluster base's fan
  over chunky leaves, stone facets) and tone role. Exploded stones are drawn 1.5 × the hero's.

### 3.9 Stones are "optional" in the notes but drawn in every assembled view except the side
- **Evidence.** The notes call the rocks simple faceted stones, optional; the front, f34, rear, r34 and top all show them
  (two in front, three behind); the underside close-up has them touching the base; the side shows none.
- **Resolution (decision §8.7).** **Five stones in the hero** (they are part of the read: grey and brown corners at the
  foot), low and tucked under leaf tips; ≈ 0 from the right side. Alternative: no stones (−160 tris) if the clump is
  scattered over terrain that already has pebbles.

### 3.10 No yellow swatch, two yellows drawn
- **Evidence.** The palette lists no yellow, but the star's bead is pale lemon (`#FDE76F`, close-up 1; top `#FDF17C`) and
  the bloom's is deep golden (`#E2B30D`, top; lit `#F5D614`, shade `#C47B03`).
- **Resolution.** Two bead keys, `m065_star_bead` (pale) and `m065_bloom_bead` (golden), from the rendered areas.

### 3.11 The grey stone swatch is neutral, the drawn grey stones are mauve-grey
- **Evidence.** Swatch Stone (Pale Gray) `#9D9B9A` (s .02); the drawn grey stones are `#A89388` (parts), `#867771` (front),
  `#B6A295` (exploded): warm mauve-grey, h 17–24°, s .16–.19, R > G > B.
- **Resolution.** `m065_rock_grey` calibrated to the rendered stones (warm grey, R > G > B, s ≤ 0.20), never lavender
  (B > G) and never neutral blue-grey.

### 3.12 The hub's underside is olive in close-up 3
- **Evidence.** Close-up 3's hex base is `#6D823F` (79°, s .52), duller than any leaf; close-up 2's collar from above is
  light green `#81B920`.
- **Resolution.** The hub is hidden in every assembled view; give it `m065_leaf_dark` (recommended) or a dedicated olive
  `m065_hub` if the main session wants close-up 3 matched (decision §8.13).

### 3.13 "Solid colours, no textures" vs the user's colour rule
- **Resolution.** Leaves blended by role and position along the leaf; petals by position along the petal; the bloom by
  ring and position (deep throat → light outer tips); the bell by inside / outside region; stones by height; broad Tint per
  piece (0.02–0.04), never per-triangle confetti (memory `lighting-not-paint`).

### 3.14 Lighting
- The sheet is lit from the upper right (lime on the leaves' upper faces, dark creases, the stems' shaded faces dark in
  the front and lit in the rear, deep blue on the star's petal backs in the rear, deep violet under the bell's lobes). The
  lighting does that; never paint it by facing. Render every `*_sheet` view with the studio floor hidden.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its exploded / parts-row cell

1. `star_petal(spec)` → one closed lozenge plate (§1.4) in its own frame (base at the origin, along +X, top +Z). Check
   against close-up 1 and the parts row: W : L 0.60–0.66, widest at 0.5 L, blunt point, ridge, thickness.
2. `bead(spec)` → the octagonal flat-topped centre (star Ø 0.26 × 0.10; bloom Ø 0.20 × 0.10).
3. `calyx(spec)` → the star's five-sided cone, the bloom's five-sepal cup, the bell's six-sided cap.
4. `star_head(spec)` → calyx + bead + 5 petals, oriented by the head normal.
5. `bell(spec)` → the six-sided closed bell with six flared lobes and an inner wall (§1.4).
6. `bloom_petal(spec)` and `bloom_head(spec)` → calyx + 5 outer + 5 inner petals + bead.
7. `stem(spec)` → a square prism along a spine of straight segments (mitred bends), its top end in the calyx or cap.
8. `leaf(spec)` → one closed kite with ridge and keel, arched along its length; `petiole=True` adds the square stub (§2.4).
9. `hub()` → the hexagonal block (§2.2).
10. `rock(spec)` → a faceted nugget (§2.5).
11. `leaf_base()` → hub + F1–F5 + B1–B4 (the exploded's cluster base: tall fan over chunky leaves).
12. **Hero `ForestBlooms`** = leaf base + N1–N4 + S1–S4 + three stems + three heads + R1–R5, one object of closed shells.
13. **Parts shot** (0, 15) laid out like the parts row: PurpleBell, BlueStar, PinkBloom, Stem, Leaf, RockGrey, RockBrown,
    then LeafBase; gaps 0.3.
14. **Exploded shot:** the heads lifted 0.45 along their stems (the bell lifted with its cap), stems lifted 0.3, S1–S4
    pulled 0.35 out along their azimuths, the stones pulled 0.3 out.

Reusable code: 061's `petal`, `bead`, `cup`, `stem`, `leaf` and `hub` functions (`m061.py`, uncommitted: copy, don't
import); 059's rock builder; `m047._Solids`, `shells_report`, `contact_report`, `bury_report` (committed: import). Take
`vis.py` from `<temp>\...\scratchpad\m061w\`.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a purple bell hanging from a crook at the left, a blue five-petal star at the top, a pink cupped
   bloom low at the right, on thick square stems over a broad rosette of faceted leaves with stones at the foot; about
   1.3 × as wide as tall.
2. **front_sheet / f34_sheet** per §2.6 (shares, fill, W : H, top profile, head centres, fifths, tones).
3. **rear / r34 / side / top** per §2.6.
4. **Close-up renders:**
   - `star_cu` face-on to the star against close-up 1: five broad petals round the octagonal bead, petals overlapping at
     the base.
   - `bell_under` (from below and in front of the bell): the six lobes, the rim and the dark inside (a real opening, not a
     painted disc).
   - `bloom_cu` into the bloom: the two petal rings, the deep throat, the golden bead.
   - `junction_cu` low and close on the rosette centre against close-up 2: stems entering the hub top among the leaf bases.
   - `base_under` on the hero from below (0, −60) against close-up 3: the flat hex hub, leaves radiating, stones touching.
   - `edge_side` (90, 0) and (0, 0): every petal, lobe and leaf shows thickness (≥ 0.05 on screen in studs).
   - `thumb`: the front at about 120 px tall: the bell, the star and the bloom still read as three different flowers;
     the rosette shows separate pointed tips.
   - **`spin` contact sheet: az 0 / 45 / 90 / 135 / 180 / 225 / 270 / 315 at e 10.** In every frame the three heads read
     as flowers (no more than one head near edge-on at once; the bell reads from every side), the leaves as faceted kites
     (not spikes, not balls, not flaps).
5. **Contact counts** (§6): floating shells 0; buried 0.
6. **Hero size** per §2.6, plus a **scale shot** with a 5.5-stud marker beside the clump (the top at 0.44 of the marker)
   and 059 / 061 beside it if they are in the kit file.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Star petals (6-vert outline + ridge, closed) | 5 | 22–26 | 110–130 |
| Star bead + calyx (+ neck) | 1 | 24 + 30 | 54 |
| Bell (6 sides, 3 rings, 6 lobes, inner wall) + cap | 1 | 110–130 + 20 | 130–150 |
| Bloom outer petals / inner petals | 5 + 5 | 22 / 18 | 200 |
| Bloom bead + calyx | 1 | 20 + 30 | 50 |
| Stems (square, 3–6 segments, capped) | 3 | 28–52 | 110 |
| Fan leaves / drooping leaves (kite + ridge + keel, 2 stations) | 5 + 4 | 30–34 | 270–306 |
| Spreading leaves with petiole | 4 | 40–44 | 160–176 |
| Rim leaves (chunky kite) | 4 | 20–24 | 80–96 |
| Hub | 1 | 20–24 | 24 |
| Stones | 5 | 20–36 | 140–160 |
| **Hero** | | | **about 1330–1500; aim ≤ 1500; ceiling 1600** |
| Parts: PurpleBell / BlueStar / PinkBloom / Stem / Leaf / RockGrey / RockBrown / LeafBase | | | 150 / 190 / 250 / 12–20 / 44 / 36 / 30 / 290 |

- **Over budget?** First the stones to 20 tris each, then the rim leaves to 16, then the bloom's inner petals to 14, then one
  spine segment per straight stem. **Never** thin the petals, lobes or leaves into cards or slivers to save triangles.
- **Lean alternative** (decision §8.14): about 1150 tris with 14 leaves (drop B3, B4 and N4), four stones (drop R5) and
  20-tri star petals.

### 4.4 What to do better than W07's `Wildflowers` and recent foliage

| Earlier | This one |
| --- | --- |
| W07: a flat pink saucer, then tulip-like cups | a two-ring cupped bloom (outer petals 45–55° up, inner 65–75°) opening toward the front, with a deep throat and a golden bead |
| W07: a thin blue star with a white dot | five broad blunt lozenges (W : L 0.62) with thickness and a ridge round a pale-lemon octagonal bead Ø 0.26 |
| W07: straight stems, then hexagonal kinked stems | square prisms 0.13 with a crisp three-segment crook on the bell stem |
| W07: a dark leaf bowl, then leaves re-oriented toward the camera | 17 closed kites by tier and growth (fan, spreading on petioles, drooping lime, chunky rim); lime in front and on the spreading tips, dark only at the rim; the `spin` sheet at eight azimuths |
| W07: stones outside the mound, then hidden | five low stones tucked under the leaf tips, about 2.5 % of the front and 4 % of the rear |
| W07: 5.4 tall (giant flowers) | 2.4 tall, just above knee height |
| 058 / 054 / 057: cards turned toward the front / rear cameras | every leaf and head placed by growth (azimuth, pitch, normal), never per camera |
| 060: rocks bare from the side and rear | stones tucked under the spreading leaves; ≤ 1.5 % from the right side |
| 061: rim leaves read as thin dark spikes; the left stem hidden by its own head and leaves | chunky rim leaves (L : W 1.4, edges 0.10); the bell stem visible from z 0.6 up |
| 035 / 036 / 046: floating or buried dressing | every petal on its calyx, every head on its stem, every stem and leaf in the hub or on the ground, every stone on the ground; counts reported |

### 4.5 Stages 2 and 3
- **Stage 2:**
  - Every shell closed and manifold, **0 bowties** (likely at petal and lobe tips, kite tips, the crook's mitres and the hub
    top).
  - **0 winding errors per shell** (`bmesh.ops.recalc_face_normals` per shell, then `m047.shells_report`); the bell's inner
    wall faces into the bell's cavity (outward from the solid), so check it by eye in `bell_under` too.
  - No zero-area faces; corners ≥ 3°; no n-gons except the hub's flat top and bottom and the beads' flat tops (triangulate
    if the audit asks).
  - Origin at the bottom centre, transforms applied.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box, sd ≤ 3.1)

| Swatch (label) | Hex (HSV) | Use |
| --- | --- | --- |
| Flower Purple | `#A767FC` (266°, .59, .99) | bell (`bell`) |
| Flower Blue | `#6474FD` (234°, .60, .99) | star petals (`star`) |
| Flower Pink | `#FE97B5` (343°, .41, 1.00) | bloom petals (`pink`) |
| Leaf Light | `#6CA928` (88°, .76, .66) | light leaves (`leaf_light`; the rendered lime is lighter, §5.2) |
| Leaf Dark | `#498025` (96°, .71, .50) | rim leaves, calyces, hub (`leaf_dark`) |
| Stone (Pale Gray) | `#9D9B9A` (20°, .02, .62) | grey stones (`rock_grey`; the drawn stones are mauve-grey, §3.11) |
| Stone (Warm Brown) | `#A66A43` (24°, .60, .65) | brown stones (`rock_brown`) |

### 5.2 Rendered regions (`samp.py`, `reg2.py`, `leaves.py`; median / lit quartile / shade quartile)

| Region | Median | Lit Q | Shade Q |
| --- | --- | --- | --- |
| All green: front / f34 / rear / side / r34 / top | `#5D8F18` (85°, .83, .56) / `#578E1A` / `#548C1A` / `#4E8419` / `#56901A` / `#59911A` | `#99C929` / `#97C828` | `#26510C` / `#26530C` |
| Green light tone: front / f34 / rear | `#97C728` (78°, .80, .78) / `#95C627` / `#8EC229` | `#B1DA36` / `#B3DA38` | `#86B822` |
| Green mid tone: front / f34 / rear | `#5F9117` (85°, .84, .57) / `#578D19` / `#57901B` | `#73A91C` / `#6FA61D` | `#43750F` |
| Green dark tone: front / f34 / rear | `#29540C` (96°, .86, .33) / `#28550C` / `#26550B` | `#35660E` | `#163806` |
| Tone shares (light / mid / dark %) | front 27 / 43 / 30; f34 28 / 45 / 27; rear 23 / 47 / 30; r34 30 / 45 / 25; side 22 / 45 / 34; top 29 / 42 / 29 | | |
| Leaves (f34): N1 / N2 big front / S3 spread right / S1 spread left / fan centre / fan left / rim left / rim right | `#8EC022` (79°) / `#92C420` / `#83B71D` (80°) / `#548D1B` (90°) / `#669F19` (86°) / `#7CAE1F` / `#527A3A` (98°, .52) / `#A0CD2E` | `#B4DC38` / `#ADD834` / `#A1CD2D` / `#67991F` / `#85BB24` / `#9BCB31` / `#6E8843` / `#BADB4A` | |
| Leaves (rear): big front-centre / spreads | `#8EBE20` / `#65A41E`, `#629D20` | `#ABD730` | |
| Exploded leaves / leaf base / parts leaf | `#609D1D`–`#80B521` / `#69A417` / `#5A9728` (93°, .74, .59) | `#9DCC2A` / `#73B233` | `#33640B` / `#3A731F` |
| Stems: parts / exploded (purple, blue, pink) / front bell (shade face) / front star (lit face) / cu2 lit / cu2 shade | `#57941D` (91°, .80, .58) / `#72AB1D`, `#7FB61C`, `#588919` / `#30621A` / `#619617` / `#6FAB1A` / `#4A821D` | `#7BB321` | `#336518` |
| Calyces: front star / front bloom / r34 star / parts star / parts bloom | `#28540F` (98°) / `#29570E` / `#5C9818` / `#295518` / `#2C5810` | `#7EBC25` (r34) | |
| Bell cap: front / r34 | `#508A21` (93°, .76, .54) / `#4D8B1A` | `#70AD2A` | `#2F640E` |
| Hub: cu3 underside / cu2 collar | `#6D823F` (79°, .52, .51) / `#81B920` | | |
| Bell (purple): front / f34 / rear / top / parts / f34 lit area | `#9160F1` (260°, .60, .95) / `#9C65F7` / `#985FF3` / `#A062FA` / `#AA70FA` / `#AA6CFC` | `#BC7EFD` / `#BF81FD` | `#4A29B1` / `#512DBB` (inside and lobe undersides) |
| Star (blue): front / f34 / top / parts / cu1 | `#7C8EFC` (232°, .51, .99) / `#8795FD` / `#6E7FFA` / `#6F83FB` / `#7481FC` | `#8A98FD` / `#909DFE` | `#2D42D1` / `#2E45D8` |
| Star from behind: rear / r34 | `#3B58E0` (229°, .74, .88) / `#3A56E3` | `#798DF9` | `#1F40BB` |
| Star bead: cu1 / top / front | `#FDE76F` (51°, .56, .99) / `#FDF17C` (54°, .51) / `#FCD242` | `#FEE972` / `#FEF9A1` | `#EAB44D` |
| Bloom (pink): front / f34 / rear / top / parts | `#FB77A3` (340°, .53, .98) / `#FC72A1` / `#FB7EAA` / `#FC7DA6` / `#FC76A4` | `#FEBDD7` / `#FEC1D7` | `#DA4575` / `#DD4D80` |
| Bloom regions (front): outer petals / throat and inner bases | `#FDB0C8` (341°, .31, .99) / `#F64575` (344°, .72, .96) | `#FEC0D7` / `#FD6C99` | `#F25781` / `#E12F5A` |
| Bloom bead: top / f34 | `#E2B30D` (47°, .94, .88) / `#FDD544` | `#F5D614` | `#C47B03` |
| Grey stones: parts / front / rear / exploded | `#A89388` (21°, .19, .66) / `#867771` (17°, .16, .53) / `#A9978C` / `#B6A295` | `#C3B0A6` / `#C1AEA4` | `#6A605F` / `#776A65` |
| Brown stones: parts / front / rear / exploded | `#A8673E` (23°, .63, .66) / `#92582F` (25°, .68, .57) / `#906842` / `#B1834E` | `#CF8853` / `#D48E52` | `#74452A` / `#613A1C` |
| Cast shadow (not modelled) | warm grey, s < 0.07, v ≈ .91 | | |

### 5.3 How the colour works

- **Leaves: three greens by role and by position along the leaf** (never facing):
  - **Role:** the big drooping N1–N4 are **light** (lime); the right spreading S3, the right fan leaf F5 and the rim leaf B2
    are **light / mid** (light outer half); the fan F1–F4, the left spreads S1 / S2 and the right-low S4 are **mid** with
    light tips on F1, F2, F4; the rim leaves B1, B3, B4 are **dark**.
  - **Along the leaf:** the lowest 0–0.2 L (and the petiole) one step deeper (light → mid, mid → dark), the outer 0.6–1.0 L
    one step lighter on the fan leaves. A whole cross-band of the leaf takes one blend step, so the lit-half / shaded-half
    contrast comes only from the light (the ridge V).
- **Stems:** `stem` along the stem, the lowest 0.2 a step deeper (`leaf_dark`) where it enters the leaves.
- **Calyces:** star and bloom calyces `leaf_dark` with their upper rim 50 % `stem`, by position; the bell's cap `stem`.
- **Bell:** the outer shell `bell`; the **inner wall and the inside of the lobes `bell_deep`** (a region, not a facing: the
  sheet's deep violet under the lobes and in the mouth); the dome top band 25 % lighter toward the swatch by height in the
  bell's own frame.
- **Star:** petals `star`, the inner 0–0.25 L 50 % `star_deep` (by position along the petal); bead `star_bead`. The rear's deep
  blue on the petal backs is shade, not paint.
- **Bloom:** outer petals `pink`, their inner 0–0.35 L blending to `pink_deep`; inner petals `pink_deep` at the base →
  `pink` at the tips (by position along the petal); bead `bloom_bead`. Light pink tips (`#FDB0C8`) come from Tint and the
  light, not a third key.
- **Hub:** `leaf_dark` (hidden).
- **Stones:** `rock_grey` / `rock_brown` per stone; the lowest 0.25 of each 25 % deeper by height (contact), broad Tint per
  stone.
- **Hues stay apart:** bell 260–268°; star 228–236°; pink 338–346°; star bead 50–56° at s .45–.60; bloom bead 45–50° at
  s ≥ .90; leaf light 76–82°; leaf mid 85–90°; stem 88–94°; leaf dark 95–100°; rock grey 18–26° at s .12–.20 (R > G > B);
  rock brown 22–28° at s .58–.68.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians where the sheet gives them, swatches where it doesn't. `K.sample` kinds:
`"vivid"` for the flower, bead and light-leaf keys, `"green"` for mid / dark / stem, `"stone"` for the grey stone,
`"brown"` for the brown stone.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m065_bell` | bell median `#9160F1` ± 12, lit `#BC7EFD` (start swatch `#A767FC`) | 260–268°, .55–.65 | bell outer shell | rough 0.75, low spec |
| `m065_bell_deep` | inner / lobe shade `#5C3ECE` seen lit, about `#6A45D8` ± 15 | 255–262°, .62–.72 | bell inner wall, inner lobe faces | rough 0.8 |
| `m065_star` | star front median `#7C8EFC` ± 12, lit `#8A98FD` (start swatch `#6474FD`) | 228–236°, .45–.62 | star petals | rough 0.75 |
| `m065_star_deep` | about `#5D6CF4` ± 15 (between swatch and shade) | 230–236°, .60–.70 | inner 0–0.25 L of each petal | rough 0.75 |
| `m065_star_bead` | cu1 `#FDE76F` ± 12 (top `#FDF17C`) | 50–56°, .45–.60 | star bead | rough 0.6, a little spec |
| `m065_pink` | bloom front median `#FB77A3` ± 12, outer lit `#FDB0C8` (start swatch `#FE97B5`) | 338–345°, .40–.55 | outer petals, inner petal tips | rough 0.75 |
| `m065_pink_deep` | throat `#F64575` ± 12 | 340–348°, .68–.78 | inner petal bases, outer petals' inner band | rough 0.75 |
| `m065_bloom_bead` | top `#E2B30D` ± 12, lit `#F5D614` | 45–50°, ≥ .90 | bloom bead | rough 0.6 |
| `m065_leaf_light` | light-tone median `#97C728` ± 12 (start swatch `#6CA928`) | 76–82°, .75–.82 | light leaves; light tips | rough 0.8, low spec |
| `m065_leaf_mid` | mid-tone median `#5F9117` ± 12, toward the parts leaf `#5A9728` | 85–90°, .76–.84 | mid leaves; light leaves' bases; calyx rims | rough 0.85 |
| `m065_leaf_dark` | swatch `#498025` ± 12, rim leaf `#527A3A` | 95–100°, .60–.72 | rim leaves; mid leaves' bases; calyces; stem feet; hub | rough 0.85 |
| `m065_stem` | parts stem `#57941D` ± 12 | 88–94°, .75–.82 | stems, the bell cap | rough 0.85 |
| `m065_rock_grey` | parts grey stone `#A89388` ± 10 (front `#867771`) | 18–26°, .12–.20, R > G > B | grey stones R1, R4 | rough 0.9, metal 0 |
| `m065_rock_brown` | parts brown stone `#A8673E` ± 12 (swatch `#A66A43`) | 22–28°, .58–.68 | brown stones R2, R3, R5 | rough 0.9 |

**Calibration warnings:**
- **The kit studio lights both halves and keys from the front-left** (042, 047, 054, 061): calibrate to the medians, then
  check the tone shares on the clump's own renders (front 27 / 43 / 30 ± 8). Rear tones will read darker (061's verifier
  leftover 2: lighting, not composition). Record the bias.
- **Flower keys must not go dull from behind** (061's petal key was calibrated low and the petals read grey in the rear):
  check the rear pink median within 15 of `#FB7EAA`, the rear bell within 15 of `#985FF3`; if the undersides read grey or
  muddy, raise the key's value, not its saturation.
- **Purple and blue stay apart:** bell ≥ 258°, star ≤ 238° on the renders; the bell must not read blue, the star must not
  read violet.
- **Pink stays pink, not red or salmon:** hue 338–346° on the outer petals; the throat deeper but still pink-rose.
- **Greens must not lean yellow or olive** (047 "plants too yellow"): `leaf_mid` ≥ 85°, `stem` ≥ 88°; only `leaf_light` is
  lime (76–82°); the front all-green median within 15 of `#5D8F18`.
- **Contrast:** the lime leaves clearly lighter than the stems; the stems read dark against the lime front leaves.
- **Stones:** grey R > G > B (never lavender, never blue-grey), brown clearly warmer and more saturated than the grey.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Leaves:** per cross-band along the leaf (base → tip), by role (§5.3).
- **Petals:** base band → body by fraction of L (star); throat → tip (bloom).
- **Bell:** dome band → body by height in the bell's frame; inner wall one region (hard edge only at the rim).
- **Stems:** foot band → body by height. **Calyces:** body → rim by position. **Stones:** foot band → body by height.
- **Hard edges only** where materials meet: petal | bead, petal | calyx, bell | cap, bell outer | inner at the rim, stone |
  anything.

### 5.6 Texture (Tint) and finish
- **Tint:** leaves 0.03 per leaf + 0.02 per band; star petals 0.02 per petal; bloom petals 0.02 per petal; bell 0.02 per lobe
  band; beads 0.02; stems 0.02; stones 0.03 per stone + 0.02 per broad facet group. Broad, never per-triangle.
- **Finish:** greens 0.8–0.85 rough, low spec (`set_colour(low_spec=True)`); flowers 0.75; beads 0.6; stones 0.9; no metal,
  no emission.

### 5.7 Re-measure (final renders against the sheet, same masks)
- **Green:** front median within 15 of `#5D8F18`; light-tone median within 12 of `#97C728`; tone shares ± 8.
- **Flowers (front):** U median within 12 of `#9160F1`; B within 12 of `#7C8EFC`; P within 12 of `#FB77A3`; the bloom throat
  within 15 of `#F64575`.
- **Beads:** star bead within 15 of `#FDE76F`; bloom bead within 15 of `#E2B30D` (top view).
- **Stems:** the parts-shot stem within 12 of `#57941D`.
- **Stones:** grey within 12 of `#A89388` (parts shot), brown within 12 of `#A8673E`.
- **Shares** per §2.6.

## 6. Joins and contact (no floating dressing, no buried dressing)

- **Shells:** each petal, bead, calyx, cap, bell, stem, leaf, stone and the hub is its own closed shell, all in one hero
  object.
- **Flower chains:**
  - star petal → calyx rim / bead (each petal's base within 0.03 of the calyx rim and under the bead, ≤ 0.04 inside it) →
    calyx → stem (the stem's top 0.05–0.08 inside the calyx, axis within 0.02) → hub (foot 0.06–0.08 inside) → ground;
  - bloom petals (outer and inner) → calyx seat (≤ 0.04 inside) → calyx → stem → hub → ground; the bead seated among the
    inner petal bases;
  - bell → cap (seat ring 0.03–0.05 inside) → the hook's end (0.04–0.06 inside the cap) → the crook stem → hub → ground.
  - **No petal floating** off its head: report each petal's seat.
- **Leaf chains:** fan, drooping and spreading leaves → hub (base / petiole end 0.04–0.08 inside) → ground; rim leaves →
  ground (base sunk ≤ 0.02) and touching the hub or a neighbour leaf. Drooping leaf tips rest within 0.03 of the ground,
  never below z 0.
- **Stones:** on the ground (flat base sunk ≤ 0.02); each touches a leaf above it or the hub within 0.03 (close-up 3: stones
  sit round the base); no stone more than 0.05 inside a leaf, no leaf more than 0.05 inside a stone.
- **No buried dressing:** ≤ 0.08 of any stem inside a calyx or the hub; no petal more than 0.04 inside the bead or calyx
  beyond its seat; no leaf more than 25 % inside another; no leaf cutting a stem by more than 0.03 outside the hub junction
  (r < 0.30, z < 0.45).
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**. Chains: petal → calyx / bead → stem → hub →
  ground; bell → cap → stem → hub → ground; leaf → hub → ground; rim leaf → ground; stone → ground.
- **Count buried shells** (STAGES; 046, 047 round 2): **0 dressing shells more than 0.05 inside a neighbour** (seats excepted
  at their stated depths). Use `m047._Solids` (hub, stones, calyces, cap, bell added as built).
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.
- **Reports:** reuse `m047.shells_report`, `contact_report` and `bury_report` (committed; import, don't edit).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no pollen, no particles, no wind marks. The cast shadow is the
render's.

- **Stage 5 (lighting): skip, and record why.** No emission, no lights. Studio notes (Requires Manual Validation):
  - the bell stays lavender-purple and the star periwinkle-blue under the game sun (not merging into one blue-violet);
  - the pink stays pink (not salmon, not washed white), the beads yellow, the lime leaves lime and the stems green (not
    olive, not black); the grey stones warm grey, not lavender.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** The old W07 `Wildflowers` had none either. A pollen mote
  or wind sway would be a Studio-side choice, not a socket (decision §8.11).
- **Collision:** **hero `none`** (CanCollide, CanQuery and CanTouch off): walk-through cover, as the old W07 hero. Every part
  `none`, the rock parts included (they are pebble-sized) (decision §8.8).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched all 2155 names in `art/roblox/kit/*/manifest.json`, `art/roblox/kit/wip/*/manifest.json`
and `art/roblox/lobby/manifest.json`, the builders and the repo text (`git grep`) for Wildflower, Bloom, Bell, Star, Forest
and the candidates:
- **W07:** `Wildflowers`, `WildflowersBlueStar`, `…PinkBloom`, `…PurpleBell`, `…FlowerHead`, `…Leaf`, `…Stem`; builder names
  `WildflowerFlowerHead`, `WildflowerLeaf`, `WildflowerStem`; `MeadowDaisy*`, `GrassTuft*`, `GroundScatter*`.
- **Lobby:** `WildflowerWhite`. **V07:** `HeatherBellFlower`. **M025:** `Emberbloom*`. Others: `DandelionYellowBloom`,
  `MoonveilSingleBloom` / `…DoubleBloom`, `SunburstBloom` / `…FullBloom`, `MoonveilInnerBell`, `Starstone*`, `Starlight*`.
- **061 / 062:** `MeadowHerb*` (keys `m061_*`), `ForestLitter*` (keys `m062_*`).
- **`ForestBlooms`, `ForestBloomsPurpleBell`, `ForestBloomsBlueStar`, `ForestBloomsPinkBloom`, `ForestBloomsStem`,
  `ForestBloomsLeaf`, `ForestBloomsLeafBase`, `ForestBloomsRockGrey`, `ForestBloomsRockBrown` (and `…Bud`) and `m065_` occur
  nowhere** (repo text, manifests, builders, the working tree's untracked builders and specs); no owned name is a substring
  of them and none of them is a substring of an owned name. `ForestWildflowers` was rejected because it contains the owned
  `Wildflowers`.

| Object | Part | Why |
| --- | --- | --- |
| `ForestBlooms` | hero: hub, 17 leaves, 3 stems (one with the crook), bell + cap, star (5 petals, bead, calyx), bloom (10 petals, bead, calyx), 5 stones | the subtitle's "forest wildflowers" without the owned `Wildflower*` stem |
| `ForestBloomsPurpleBell` | "Purple Bell Head": the bell with its cap | the label |
| `ForestBloomsBlueStar` | "Blue Star Head": petals, bead, calyx and neck stub | the label |
| `ForestBloomsPinkBloom` | "Pink Bloom Head": both petal rings, bead, calyx and neck stub | the label |
| `ForestBloomsStem` | "Stem (Example)": a straight square prism 0.13 × 0.75 with a slanted top cut (the exploded "Stem (Blue)") | the label |
| `ForestBloomsLeaf` | "Leaf (Example)" / "Leaf (Reusable)": S1's shape with its petiole stub | the label |
| `ForestBloomsRockGrey` / `ForestBloomsRockBrown` | "Rock (Gray)" / "Rock (Brown)": R1 / R2 | the labels |
| `ForestBloomsLeafBase` | "Leaf Cluster Base (Junction)": hub + F1–F5 + B1–B4 | the exploded label and the notes' "single piece" |

- Palette keys `m065_*` (§5.4). Collection `Kit/M065 Forest Wildflowers`. No sockets (§7).

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **2.4 tall, 3.0 × 2.3 footprint** (recommended: 0.44 C; the star head Ø 1.13 matches 061's daisy heads;
   level with 059's 2.4). Alternative: 2.2 (0.40 C, exactly §3.2's top; star Ø 1.04, stems 0.12).
2. **Names (§8):** **`ForestBlooms` and the eight parts above** (recommended). Not `Wildflower*` / `Wildflowers*` (W07,
   lobby), not `ForestWildflowers` (contains the owned name). Alternative hero name `WoodlandBlooms` (also free).
3. **Heads (§2.3, §3.3, §3.4):** **three heads — the bell hanging from a crook at the left (body z 1.15–1.94), the star at
   the top (bead z 1.98, facing az 300° tilt 45°), the bloom low at the right (bead z 1.36, facing az 255° tilt 42°) —
   with fixed growth facings; no bud** (recommended). Alternative: add the front's pink-and-violet bud as a fourth head
   (+90 tris; it shows from the rear where the sheet's rear doesn't draw it).
4. **Leaves (§2.4):** **17 closed kites: a 5-leaf upright fan, 4 spreading leaves on petiole stubs, 4 big drooping lime
   leaves (front and back), 4 chunky rim leaves; placed by growth, never rolled toward a camera** (recommended).
5. **Stems (§2.3, §3.5, §3.7):** **square prisms, side 0.13, straight segments with mitred bends; the bell's a crook (apex
   z 2.12) bending toward the front-left; faces turned 20° off the front** (recommended). Alternative: hexagonal Ø 0.14 as
   061 (smoother, but unlike close-up 2).
6. **Base (§2.2, §3.6):** **a closed hexagonal hub, hidden in the hero; no socket hole, on the part as well** (recommended).
7. **Stones (§2.5, §3.9):** **five low faceted stones (R1 / R4 grey, R2 / R3 / R5 brown) tucked under the leaf tips, about
   2.5 % of the front, ≤ 1.5 % from the right side** (recommended). Alternative: none (−160 tris).
8. **Collision (§7):** **`none` on the hero and every part** (recommended).
9. **Comparison cameras (§3.2–§3.4):** **`front_sheet (0, 5)` governs positions, `f34_sheet` the read** (probe az −20 … 0, e
   10–20); `rear_sheet (180, 5)`, `r34_sheet (170, 12)` (probe 160 … 200); `side_sheet` from +X ("SIDE (RIGHT)": bloom
   nearest at image left; render 90 and 270, keep the one that matches); `top_sheet (0, 85)` content only; extras: parts
   shot, exploded, `star_cu`, `bell_under`, `bloom_cu`, `junction_cu`, `base_under`, `edge_side`, `thumb`, **`spin` (eight
   azimuths)**, scale shot. Floor hidden in every `*_sheet` render.
10. **Sinking (origin):** **hub, rim leaves and stones sink at most 0.03**; the origin within 0.03 of the ground; record the
    origin's offset from the hub axis (≤ 0.10) (recommended).
11. **VFX (§7):** **none; stages 5 and 6 skipped and recorded** (recommended).
12. **Exported parts (§8):** **the hero plus eight parts: the seven of the "PARTS (ISOLATED)" row and `LeafBase`**
    (recommended), or the hero plus the seven row parts only.
13. **Colour (§5):** **bell `#9160F1` with a `bell_deep` inside, star `#7C8EFC` with a deeper base band and a pale-lemon bead
    `#FDE76F`, bloom `#FB77A3` over a `#F64575` throat with a golden bead `#E2B30D`, leaves lime `#97C728` / mid `#5F9117` /
    dark `#498025` by role, stems `#57941D`, calyces dark, stones mauve-grey `#A89388` and warm brown `#A8673E`; front
    all-green median `#5D8F18`, tone shares 27 / 43 / 30; hub `leaf_dark`** (recommended). Alternative for the hub: an olive
    `m065_hub` `#6D823F` matching close-up 3 (hidden either way).
14. **Budget (§4.3):** **small prop extended: hero ceiling 1600, planned 1330–1500; each part under 1000** (recommended:
    three different heads, 17 closed leaves and five stones need it). Alternative: a lean 1150 (14 leaves, four stones,
    20-tri petals) if the clump is scattered very densely.

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **Parts turned toward the cameras (054 r2, 057 r1, 058 r1 blocker 1, and the old W07's leaves "reoriented by facing").**
   - Every head, petal and leaf placed by its growth (azimuth, pitch, normal); no per-camera roll.
   - The `spin` contact sheet at eight azimuths: at most one head near edge-on per frame, leaves read as kites from every
     side; `vis.py` edge-on flat area ≤ 10 % at 12° in every view, bare core (hub + stems) ≤ 15–30 % of the visible foliage.
2. **A flat saucer bloom (W07).** Two petal rings cupped 45–55° / 65–75°, a visible throat and bead; in `edge_side` the
   bloom reads as a cup.
3. **A thin or needle star (W07).** Five lozenges W : L 0.60–0.66, blunt points, thickness 0.05 visible in `edge_side`; the
   ring reads closed near the bead.
4. **An open-cone bell or a bell without an inside (WorldModeling §6.6, §18 "flower looks like disconnected triangles").**
   A closed six-sided shell with six flared pointed lobes, a rim and an inner wall; the inside reads dark violet from below.
5. **A soft or arched crook.** The bell stem's bend is crisp (three straight segments, a sharp apex), as the exploded draws
   it; the hook drops into a visible cap.
6. **Flat cards (WorldModeling §6.1, §17.2 "leaves have side-visible volume").** Every leaf a closed kite 0.06–0.12 thick with
   a ridge V; ≥ 0.05 on screen in `edge_side`.
7. **Spiky or hedgehog rosette (047 r1; WorldModeling §18).** Kite tips 50–70°, widest near the middle, a clear tier
   hierarchy (fan 1.05–1.28, raised spreads 0.7, low spreads 0.2, drooping and rim on the ground).
8. **Thin dark rim spikes (061 verifier minor 2).** Rim leaves chunky (L : W 1.3–1.5, edges 0.10), lying low.
9. **A dark, dense leaf bowl (W07).** Front light share 27 ± 8 %; the big front leaves lime; dark only at the rim and the
   leaf bases.
10. **Stems hidden or wiry (061 minor 3; WorldModeling §18 "tiny details vanish").** Square 0.13; the bell stem visible from
    z 0.6 up, the star's from 0.9, the bloom's from 0.75 in the front and f34.
11. **Rocks standing bare (060 r1 blocker 1) or hidden entirely (W07).** About 2.5 % of the front, 4 % of the rear, ≤ 1.5 %
    from the right side; squat faceted blocks, not eggs or obelisks.
12. **Floating petals, heads or stones (STAGES; 035 / 036).** Every petal on its calyx / under its bead, every head on its
    stem, every stem in the hub, every stone on the ground touching a leaf or the hub; floating shells 0, counted and
    reported.
13. **Buried parts (046; 047 r2).** Stem tops ≤ 0.08 in the calyx, beads ≤ 50 % sunk, no leaf more than 25 % inside another;
    ray parity after the final placement: 0 shells more than 0.05 inside.
14. **Leaves cutting the ground, stems or stones.** No vertex below z −0.01 except the sunk bases; drooping tips rest within
    0.03; no leaf cuts a stem by more than 0.03 outside the junction.
15. **Purple and blue merging, salmon pink, olive greens, lavender stones, grey flowers from behind.** Bell ≥ 258°, star
    ≤ 238°, pink 338–346°, `leaf_mid` ≥ 85°, `stem` ≥ 88°, grey stone R > G > B; rear flower medians within 15 of the sheet's.
16. **Colour by facing (042 ruling; 054 m9).** Tones by leaf role and position along the leaf, petals by position, the bell by
    region; `K.check` facing correlation < 0.5 per material. A band on a gem-like bead follows its facing (061 deviation 1):
    one key per bead.
17. **Winding (044) and bowties.** 0 faces wound against their neighbours per shell (the bell's inner wall especially);
    petal, lobe and kite tips checked for bowties; corners ≥ 3°.
18. **Oversize.** 2.4 tall, not the old kit's 5.4; a scale shot with the 5.5-stud marker.
19. **Origin below the ground.** Sink nothing more than 0.03.
20. **Names and scope.**
    - No `Wildflower*`, `Wildflowers*` or `ForestWildflowers` names.
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit the frozen shared helpers or other models' builders: import from the committed ones (`m047`, `m049`,
      `m053`, `m055`, `m056`); copy from `m059` / `m060` / `m061` if they are still uncommitted.
    - Don't touch other models' collections.

## Decisions (main session, 2026-10-31)
All 14 recommendations are accepted. The open questions are ruled as follows:
1. **Size.** 2.4 tall with a 3.0 × 2.3 footprint, level with 059. The star head matches 061's daisies.
2. **Names.** Hero `ForestBlooms` plus the eight parts in §8, keys `m065_*`. Never `Wildflower*`.
3. **Heads.** Three, with the fixed facings given.
   - **No bud:** only the front and f34 draw it, and the exploded view and parts row govern.
   - Heads must not vanish edge-on from the sides; check the spin sheet.
4. **Leaves.** Seventeen closed leaves with thickness, placed by growth and never turned toward a camera.
   - The rim leaves are **chunky flat kites, not thin dark spikes**, which was 061's main leftover.
5. **Stems.** **Square, as the sheet draws them**, side 0.13, with sharp bends.
   - Every head's stem stays visible where the sheet shows it, unlike 061's hidden left stem.
6. **Base.** A closed hexagonal hub with no socket. It uses `leaf_dark` (it is hidden), with no extra olive key.
7. **Stones.** All five, low and tucked under leaf tips.
   - The "mauve-grey" stones stay warm with R > G > B and must not read pink or lavender.
8. **Collision.** `none` everywhere.
9. **Cameras.** As recommended.
   - The side is judged for the crook, the bloom and the leaves only.
   - The top is judged for content only.
10. **Sinking.** At most 0.03, with **no floating and no buried pieces**: petals on their calyx or cup, heads on stems, stems on the hub.
11. **VFX.** None; stages 5 and 6 skipped and recorded.
12. **Exports.** The hero plus eight parts.
13. **Colour.**
    - Use the colours as listed, by role and position, **never by facing**.
    - Keep the three flower colours clearly distinct: violet bell, periwinkle star, pink bloom.
14. **Budget.** Small prop extended: hero ceiling 1600 (plan 1330–1500), every part under 1000.
