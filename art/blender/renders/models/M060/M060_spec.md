# 060 Broadleaf Fern — spec

Reference: `art/blender/assets/references/060.png` (1024 × 1536 px). INDEX.md row 60: "Broadleaf Fern Model Study". The
sheet's own header reads **"58 / 132"** (top left), title **"BROADLEAF FERN"**, footer "FLINTBORN — INDIVIDUAL MODEL
STUDY" (our number is INDEX's 060, §3.1).
Builder: `art/blender/kit/mcp/m060.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows no effect** (§7). The plant rules
of WorldModeling §1, §6.9 and §18 apply: **broad, thick, lobed fronds on a curved spine (about five lobe pairs per
frond), attached by stalks to one root crown**, never flat cards, never combs of thin leaflets, never a flat star.

Sheet text (paraphrased):
- **Title block (top left):** "58 / 132", "BROADLEAF FERN".
- **Description (top centre):** big stylised fronds and broad leaves; thick shapes that read clearly, made for forest
  undergrowth and jungle edges; chunky low-poly construction from simple, clean parts.
- **"MATERIAL PALETTE"** (top right): six unlabelled swatches (dark green, mid green, lime, pale sage, warm grey, brown;
  §5.1, §3.10).
- **"ASSEMBLED":** "FRONT THREE-QUARTER" and "REAR THREE-QUARTER".
- **"ORTHOGRAPHIC VIEWS (MATCHING GEOMETRY)":** "FRONT", "SIDE (RIGHT)", "REAR", "TOP" (the "top" is a high oblique,
  §3.3).
- **"EXPLODED CONSTRUCTION":** labels "Fern Frond (large)", "Fern Frond (medium)", "Fern Frond (small)", "Root Cluster
  (base)", "Broad Leaf (single)". Drawn: a large dark curved frond, a medium **pair** of fronds sharing one stalk, a small
  lime frond, each with an arrow down to the assembly; the assembly is a root crown with a short peg on top, its stalks
  rising into a ring of fronds, two pale rocks in front and a small lime ground sprig; the root cluster stands alone to
  the left (a stump with splayed legs) and a plain faceted kite leaf to the right, its arrow pointing at the assembly's
  lower right leaf.
- **"CLOSE-UPS":**
  1. "LEAF JUNCTION (SIDE VIEW)": the stalks meet a faceted orange-brown crown; dark brown stalks splay out of its top,
     a green stalk rises from its centre, stubby roots run down and out to the ground; rocks stand on either side.
  2. "UNDERSIDE VIEW": the crown from below: a star of about nine chunky faceted roots round a faceted hub, fronds
     spreading behind; a pale rock at the left.
  3. "LEAF THICKNESS (CROSS-SECTION)": one frond's upper part nearly edge-on: lobed edge, a raised midrib, a visible
     side band (the thickness) marked with a double arrow; the callout says the frond is thick, one-piece geometry for a
     clean silhouette.
- **"PARTS (INDIVIDUAL)":** Fern Frond (large), Fern Frond (medium), Fern Frond (small), Root Cluster (base), Broad Leaf
  (single), Rock (reusable), Ground Leaf (small, optional).
- **"MODELING NOTES":** chunky low-poly shapes with broad flat-shaded faces; fronds kept as separate reusable parts with
  simple joins; the root cluster and rocks are modular and reusable across foliage; a clear silhouette from every angle;
  simple shapes, solid colours, no texture noise; match the Flintborn reference's style, proportions and palette.
- **Game context and the old kit:**
  - **W06 row 2 `FernAndBroadleaf`** (`art/blender/scripts/kit/W06/fern_and_broadleaf.py`; manifest
    `art/roblox/kit/W06/manifest.json`) is the old kit's take on this subject (the same part names: large / medium /
    small frond, root cluster, broad leaf). Manifest: **10.2 wide × 6.8 tall × 9.6 deep**, 3549 tris (budget 4000),
    collision `none` (CanCollide off), no VFX. Notes: "dense rosette of broad-leaflet fronds, three upright cupped broad
    leaves, flared root stump in a ring of rocks". Its builder: 12 pinnate fronds with saw-tooth pinnae on a thin slab,
    three plain kite broad leaves, a dark soil mound, root nubs, grey boulders. `MODEL_PROGRESS.md` row 66: "rough: flat
    star of wide leaves (ref arching fronds)". Its palette comment records a verifier fail: the fern green read as a
    medium yellow-green with **weak contrast to the lime broad leaves**. Parts `FernAndBroadleafFrondLarge / …Medium /
    …Small / …RootCluster / …BroadLeaf`, variants `…Upright`, `…Spread`, `…BroadleafCluster`. A WIP copy
    (`art/roblox/kit/wip/W06_fern_and_broadleaf/`) owns `FernFrondLarge`, `FernFrondMedium`, `FernFrondSmall`,
    `FernRootCluster`, `SpreadFern`, `UprightFern`. **Those names are taken** (§8).
  - **Related:** the lobby's `FernLeafy` (4.2 wide × 2.4 tall, `build_05_trees_plants.py`: "thin rachis with discrete,
    forward-angled leaflets", the comb look to avoid); V03 `BrackenFern*` / `StrapFern*`; V10 `GiantCoilFern*`; 059 Grass
    Tuft (2.4 tall, rocks 0.85); 058 Low Bush (4.5 tall). §1.5 keeps 060 apart from them.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The cells have no flat paper:
the background is cream (`#FAF6EC`–`#FCF8EE`) with a warm floor glow under each plant (down to `#F5E5CC`) and a soft
neutral cast shadow to the left. Measured grey rules: page frame x 10–11 / 1012–1013; assembled frame y 109 / 457;
ortho frame y 466 / 725, cell dividers x 262, 512, 762; exploded frame x 11–716, y 734–735 / 1217–1218; close-ups x
723–1012; parts frame y 1226 / 1428–1429.
- **Cells** (`m.V`, `m.X` in the study folder): f34 (12,111,511,456); r34 (513,111,1011,456); front (12,519,261,724);
  side (263,519,511,724); rear (513,519,761,724); top (763,519,1011,724); exploded (12,770,715,1216); cu1 "leaf
  junction" (724,785,1011,910); cu2 "underside" (724,943,1011,1092); cu3 "thickness" (724,1110,1011,1216); parts row
  (12,1290,1011,1427).
- **Blanked text** before measuring: (12,111,172,153) and (513,111,668,153), the assembled labels.
- **Swatches** (inner boxes, sd ≤ 2.2): S1 (798,55,823,82), S2 (835,55,860,82), S3 (871,55,896,82), S4 (907,55,929,82),
  S5 (940,55,962,82), S6 (973,55,997,82).
- **Masks** are `background()` and `cls()` in `m.py` (HSV, h in degrees):
  - **Background:** flood-filled from the cell border through cream / floor glow (v ≥ 0.86, s < 0.30, h 15–65), near
    white (v ≥ 0.90, s < 0.10) and the neutral shadow (s < 0.07, v ≥ 0.62). Pale green-cream fringes and enclosed paper
    gaps (s < 0.25, v ≥ 0.80, h 40–140) are also background.
  - **G**, green: h 50–180, s ≥ 0.22, v ≥ 0.08.
  - **T**, brown (root crown, roots, stalks, deep shade on them): h < 50, s ≥ 0.28, v ≥ 0.12, except pale warm lit rock
    faces (v ≥ 0.75 with s < 0.42), which stay R.
  - **R**, rock: any other s < 0.28, v ≥ 0.22 (warm lit faces, cool blue-grey shade faces, the sage rocks).
  - **O**, other non-background (outlines, near-black gaps under the leaves).
  - **Leaf tones:** light = h < 82 and v ≥ 0.62; dark = (v < 0.45 or h ≥ 108) and not light; mid = the rest. The dark
    share includes the deep shade inside the plant; apply the same masks to our renders, floor hidden, so the comparison
    stays fair.
  - **Limits:** T includes very dark shade under the leaves (`#2D1D0C`) as well as lit root; R in the f34 includes the
    two sage rocks; a little rock creeps into O.

**Scratch study material** (no Blender) in
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m060_study\`.
Run with `C:/Users/Orang/.local/bin/uv.exe run --no-project --with pillow --with numpy python <script> < /dev/null` (the
plain `python3.14.exe` has no Pillow or numpy).
- **Helpers:** `m.py` (boxes, `background`, `cls`, `hsv`, `clsimg`), `zoom.py` (`zoom.py x0 y0 x1 y1 scale out.png
  [grid]`), `probe.py` (`probe.py x,y …`), `comps.py` (`label()`; importing it also prints its blob table).
- **Measurements:** `measure.py` → `measure_out.txt` (bbox, W : H, shares, fill, top profile, widths per height, fifths,
  tone bands); `runs.py` → `runs_out.txt` (outline runs at h .40–.95); `samp.py` → `samp_out.txt` (tones and regions per
  cell); `samp2.py` → `samp2_out.txt` (rocks, root, stalks, single leaves, parts); `sw.py` (swatches); `comps.py` →
  `comps_out.txt` (rock and brown blobs per view); `gl.py` → `gl_out.txt` (separate ground-level green blobs, the
  sprigs; its first lines repeat the `comps.py` table); `expl.py` → `expl_out.txt` (exploded and parts row: L, W, L : W,
  width profile, tone).
- **Zooms:** `z_f34.png`, `z_r34.png`, `z_f34g.png`, `z_r34g.png` (gridded), `z_ortho1.png`, `z_ortho2.png`,
  `z_front.png`, `z_side.png`, `z_rear.png`, `z_top.png` (4×, gridded), `z_front_r.png`, `z_f34_br.png` (the back-right
  rock), `z_expl.png`, `z_fronds.png`, `z_explbase.png`, `z_cu.png`, `z_cu1.png`, `z_cu2.png`, `z_cu3.png`,
  `z_parts.png`, `z_pal.png`, `z_notes.png`; class maps `cls_mont1.png` (f34, r34), `cls_mont2.png` (front, side, rear,
  top).
- **On our renders:** copy 058's or 059's `meas.py`, point it at this folder's `m.py` and use `cls()` (its background
  flood works on a plain studio background too).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a self-contained undergrowth plant with its own base dressing (root crown, rocks,
  ground leaves). **Budget: hero ceiling 3800 tris, plan about 2900–3300; every part under 1000** (decision §8.14; the
  old W06 `FernAndBroadleaf` used 3549 of 4000).
- **Overall read (check this first).** A **lush, rounded fern crown about 1.3 × as wide as tall**:
  - **two tall dark-to-mid fronds** rising in a V from the centre to the full height, tips arching outward and standing
    clearly apart at the top;
  - **two long lime fronds arching out sideways** at mid height (to the far left and right), with a darker forked
    partner behind each, and two smaller lime fronds pointing front and back;
  - a **skirt of big lobed broad leaves** drooping from the crown to the ground all round: lime ones in front, dark
    green ones at the sides and back;
  - a **chunky orange-brown root crown** with splayed stubby roots, seen between the leaf bases; **seven pale warm-grey
    faceted rocks** ringing the foot (two taller moss-stained ones behind) and **small lime ground sprigs**.
  - It reads **green over a little stone and wood**: front G 81.5 %, R 8.9 %, T 3.8 %, O 5.7 %.
  - **Every leaf is lobed**: deep rounded notches cut into each side, the lobes blunt and squarish, a raised midrib.
    Fronds are long (L : W 2.2–2.9); the skirt leaves are broad (L : W about 1.5).
- **Focal silhouettes, in order:**
  1. The two tall fronds standing apart above h .85 (front: runs at x −.26 … −.05 and +.17 … +.37 of H, §1.2), each
     tip curling outward.
  2. The arching lime fronds reaching to the far sides at h .55–.65 with lobed upper edges.
  3. The lobed skirt and the rock ring at the foot, brown roots showing between.
- **Target size: 3.0 tall (the tallest frond's apex), 3.85 wide (X) × 3.45 deep (Y)** (decision §8.1). Tolerances:
  height ±0.1, width ±0.2, depth ±0.2.
  - **How it was derived.** Front cell silhouette 229 × 183 px → **61 px / stud** at H 3.0 → W 3.75. Rear 227 × 171 →
    3.98 wide at 57 px / stud. Side 197 × 171 → **3.46 deep**. f34 428 × 328 (109 px / stud, includes some ground depth)
    → 3.92. Width taken as 3.85 (front and rear together).
  - **Why 3.0.**
    - 0.55 C against the 5.5-stud character: **hip height**, an undergrowth plant a player wades through. The sheet calls
      the fronds large and the plant "forest undergrowth and jungle edges".
    - At 3.0 the sheet gives: the big front rock **0.85 wide × 0.55 tall** (the same rock size as 059's Rock A, so the
      "reusable" rocks match across the foliage kit), medium rocks 0.55–0.65, frond widths 0.5–0.95, skirt leaves
      0.85–1.1 wide, lobes 0.2–0.35 wide: big enough to read at gameplay distance.
    - WorldModeling §3.2 puts ferns at 0.18–0.45 C (1.0–2.5) with spread 1.1–1.8 × height. Our spread (1.28) is inside
      that; the height sits a little above it, as the "large fronds" text asks. It stays above 059 Grass Tuft (2.4) and
      below 058 Low Bush (4.5).
    - The old W06 hero (6.8 tall, 1.24 C) is head-high: too big for undergrowth. The lobby `FernLeafy` (2.4) is
      a small fern.
    - At 2.5 the rocks shrink to 0.7 and the lobes to 0.17–0.28; at 3.6 the plant reaches the waist-to-chest line and
      the rocks reach 1.0.
  - **Against the character (5.5):** 0.55 C tall, 0.70 C wide.
- **Build frame:** front −Y, +X right, ground z 0. The root crown's axis at (0, 0). The origin is the bbox bottom centre;
  the fronds are not symmetric, so record the origin's offset from the crown axis (expected ≤ 0.15).

### 1.2 Measured views (`measure.py`, `samp.py`, `comps.py`)

| View (box) | Silhouette bbox (px) | W : H | G | T | R | O | fill | leaf light / mid / dark |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (12,111,511,456) | 75–502 × 120–447 (428 × 328) | 1.305 | 80.0 % | 4.6 | 10.7 | 4.8 | 0.621 | 33 / 29 / 38 |
| Rear three-quarter (513,111,1011,456) | 567–968 × 152–445 (402 × 294) | 1.367 | 82.2 | 5.8 | 8.3 | 3.7 | 0.638 | 37 / 26 / 37 |
| **Front** (12,519,261,724) | 28–256 × 533–715 (229 × 183) | **1.251** | **81.5** | **3.8** | **8.9** | 5.7 | **0.649** | **31 / 29 / 40** |
| Side (263,519,511,724) | 294–490 × 543–713 (197 × 171) | 1.152 | 84.6 | 4.8 | 6.4 | 4.3 | 0.575 | 38 / 34 / 28 |
| Rear (513,519,761,724) | 524–750 × 544–714 (227 × 171) | 1.327 | 82.3 | 4.1 | 8.5 | 5.1 | 0.642 | 28 / 28 / 44 |
| Top, high oblique (763,519,1011,724) | 784–992 × 531–714 (209 × 184) | 1.136 | 83.6 | 2.8 | 9.5 | 4.1 | 0.689 | 43 / 27 / 29 |

- Shares are of the silhouette (background excluded, O included). **Fill** = silhouette / bbox area.
- **Verifier tolerance:** G ±4, R ±3, T ±1.5 points; W : H ±0.07; fill ±0.05; tip positions ±0.06 H.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.1 W):

| f | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .20 | .63 | .72 | 1.00 | .97 | .90 | .77 | .88 | .91 | .67 | .20 |
| r34 | .23 | .66 | .95 | .94 | .95 | .95 | .73 | .90 | .97 | 1.00 | .67 |
| **Front** | .15 | .63 | .72 | .99 | .94 | .83 | .81 | .91 | .95 | .68 | .30 |
| Side | .50 | .65 | .68 | .98 | .94 | .84 | .65 | .80 | .84 | .88 | .58 |
| Rear | .68 | .73 | 1.00 | .98 | .91 | .74 | .80 | .94 | .99 | .99 | .62 |

**Width per height** (silhouette width at h .02 → .98 in 11 steps, fraction of W):

```
f34    .25 .88 .96 .95 .84 .71 .81 .47 .40 .51 .11
r34    .47 .89 .97 .89 .83 .53 .85 .75 .53 .61 .56
front  .28 .99 .97 .94 .86 .68 .78 .72 .43 .55 .11
side   .61 .78 .90 .79 .56 .84 .81 .46 .56 .14 .11
rear   .63 .86 .91 .93 .86 .62 .81 .74 .47 .54 .68
```

- Reading (front): h .1–.4 the skirt and the arching fronds across the full width (.86–.99 of W); h .5–.7 the arching
  fronds still reach out (.68–.78); h .8–.9 only the two tall fronds (.43–.55, two runs); the top is the tall fronds'
  curled tips. The foot is narrow (h .02: .28) because the rocks sit inside the leaf skirt.

**Outline runs** (`runs.py`; x from the bbox centre in fractions of H):

| View | h .70 | h .85 | h .95 |
| --- | --- | --- | --- |
| Front | [−.43 … +.06] [+.07 … +.25] [+.28 … +.32] | [−.26 … −.05] [+.17 … +.37] | [−.31 … −.15] [+.35 … +.45] |
| f34 | [−.43 … −.41] [−.35 … −.31] [−.28 … −.11] [−.09 … +.34] | [−.22 … −.02] [+.21 … +.42] | [−.26 … −.11] |
| Side | [−.20 … +.06] [+.15 … +.32] | [−.25 … −.07] [+.35 … +.44] | [−.27 … −.13] |
| Rear | [−.62 … −.31] [−.27 … +.01] [+.10 … +.35] | [−.33 … −.08] [+.15 … +.41] | [−.35 … −.19] [+.32 … +.49] |

- **The two tall fronds stand apart above h .80 in every side view** (a gap of 0.2–0.6 H between them), and the h .70
  row still breaks into 2–4 runs (lobes and frond tips).

**Height fifths** (bottom → top, % of each class):
- Green: front 13.0 / 30.5 / 25.2 / 21.1 / 10.1; f34 12.0 / 30.8 / 26.6 / 21.8 / 8.8; rear 12.9 / 29.3 / 24.1 / 22.2 /
  11.6; side 16.9 / 28.9 / 27.1 / 19.3 / 7.8.
- Brown: front 82 / 18 / 0 / 0 / 0; f34 62 / 34 / 4 / 0 / 0 (the golden stalk shows at mid height); side 89 / 6 / 5.
- Rock: 86–92 % in the lowest fifth in every side view (f34 10 % in the second: the two tall sage rocks).

**Frond tips** (read off the 4× zooms; studs at H 3.0; front x from the bbox centre (x 142), rear image left = world
+X, side image left = front −Y):

| Frond | Front tip (px) → (x, z) | Side tip → (y, z) | Rear tip → (world x, z) | Tone in the hero |
| --- | --- | --- | --- | --- |
| **F1** tall left (large) | (78, 534) → (−1.05, 2.97) | (337, 544) → (−0.96, 2.96), front | (729, 545) → (−1.61, 2.96) | dark body, lime-lit lobes |
| **F2** tall right (large) | (224, 541) → (+1.34, 2.85) | (473, 564) → (+1.42, 2.61), back | (570, 544) → (+1.18, 2.98) | mid → lime |
| **F3** arching left | (35, 614) → (−1.75, 1.66) | (490, 615) → (+1.72, 1.72), back | (751, 611) → (−2.00, 1.81) | lime |
| **F4** arching right | (253, 600) → (+1.82, 1.89) | (293, 630) → (−1.74, 1.46), front | (525, 600) → (+1.96, 2.00) | lime |
| **F3b** dark, behind F3 | (61, 586) → (−1.33, 2.11) | hidden | hidden | dark |

- The side's pairing (which arching frond is front or back) is not unique; §3.4 chooses a plan that gives two tall and
  two arching fronds in the front, rear **and** side views.
- **Skirt leaf tips, front** (studs): front-centre lime (180, 714) → (+0.62, **0.02**, on the ground); front-left lime
  (105, 675) → (−0.61, 0.66, drooping toward the camera); right lime (255, 697) → (+1.85, 0.29); left dark (36, 655) →
  (−1.74, 0.98); far-left dark (26, 689) → (−1.90, 0.43); left-low dark (74, 704) → (−1.11, 0.18); right dark behind
  → about (+1.70, 1.0).
- **Counts per view:** upper fronds front 5 + forks, f34 6, rear 4–5, side 4; skirt leaves front 7, f34 8–9, top 9–10;
  rocks front 5 (+ the back-right peak), f34 7, r34 6–7, top 7–8; ground sprigs front 3, side 4, rear 4, f34 6, r34 8
  (`comps.py` / `gl.py`).

**Rocks** (`comps.py`; studs at H 3.0, x from the crown axis):

| Rock | Front blob (px) → studs | f34 blob (px) → studs | Adopted centre (x, y), W × D × H |
| --- | --- | --- | --- |
| R1 large, front-left | (82–132, 677–712) → 0.82 wide, top 0.62, x −0.57 | (165–268, 376–436) → 0.95, x −0.66 | (−0.62, −1.05), 0.85 × 0.70 × 0.55 |
| R2 medium, front | (139–177, 689–715) → 0.64, top 0.43, x +0.26 | (284–358, 399–448) → 0.69, x +0.30 | (+0.30, −1.30), 0.62 × 0.52 × 0.42 |
| R3 medium, right | (206–240, 681–705) → 0.57, top 0.56, x +1.33 | (405–466, 381–426) → 0.57, x +1.35 | (+1.35, −0.85), 0.58 × 0.50 × 0.48 |
| R4 small, left | (41–66, 687–703) → 0.43, top 0.46, x −1.50 | (88–154, 387–416) → 0.61 × 0.28 | (−1.55, −0.60), 0.45 × 0.40 × 0.35 |
| R5 sage, back-left | (30–50, 655–690) behind leaves, top 0.98 | (98–157, 326–397), green-grey `#7C8D7F` | (−1.20, +0.85), 0.70 × 0.60 × 0.80 |
| R6 sage, back-right | peak (217–237, 621–640) behind leaves, top 1.54 | (425–475, 262–300), moss-green and pale | (+1.15, +0.95), 0.80 × 0.65 × 1.00 (§3.9) |
| R7 small, back | — | — (top: (827–852, 557–575)) | (−0.10, +1.35), 0.50 × 0.42 × 0.35 |

### 1.3 Silhouette and composition per view

**Front (`z_front.png`) — governs positions and heights.** A low view (rock tops just visible). Two tall fronds rise from
the centre: F1 to the upper left with lobes on both sides (a darker inner half and lime lit lobes on its outer edge), its
tip curling left at the very top; F2 to the upper right, mid and lime. Below them F3 arches far out to the left and F4
far out to the right (both lime, lobes on their upper edges), a darker forked frond F3b behind F3. The centre between
the tall fronds shows dark stalks and shaded lobes. The skirt: a big lime lobed leaf front-centre-left drooping toward the
camera, another lime leaf front-centre pointing straight down with its tip on the ground, a big lime-mid leaf at the
right, dark lobed leaves low at the left and right. At the foot: a big pale rock front-left (lit warm on its right faces,
cool grey in shade), smaller rocks in front and right, a small rock at the far left, brown roots showing between, small
lime sprigs on the ground, and a pale moss-stained rock peak behind the right-hand leaves.

**Front three-quarter (`z_f34g.png`) — governs the read.** Drawn **nearly frontal and from higher up**: every frond tip
sits at the front's x fraction within ±0.04 W (F1 .26 vs .22, F2 .85 vs .86, F3 .05 vs .03, F4 .98 vs .98), W : H 1.305
vs 1.251; the rock tops, the root crown and the ground show more. Lit from the upper right: lime on the upper faces of the
lobes, dark in the creases and on the inner halves of the fronds.
- **Fronds:** each shows a broad top face split by its raised midrib, 5–6 blunt lobes a side with deep rounded notches,
  and a darker side band (the thickness) along the lower edge. The tall right frond shows a bare **golden-ochre stalk**
  (`#8E670F`) between the leaves at mid height.
- **Base:** R1 big and pale front-centre-left, R2 front-right of centre, R3 right, R4 left; two **taller moss-stained
  rocks** behind the skirt at the left and right; brown roots between; lime ground sprigs at the front edge.

**Rear three-quarter (`z_r34g.png`).** The same plant from behind: the two tall fronds (one lime-lit, one dark) in a V,
arching fronds out to both sides, a lime skirt leaf front-centre pointing down, dark skirt leaves at the sides, the brown
root crown showing widely at the foot (r34 T 5.8 %), pale rocks round the front edge and many small lime sprigs.

**Rear (`z_rear.png`).** A near mirror of the front: two tall fronds at the full height, two arching fronds to the far
sides (a little higher than the front's), a lime skirt leaf front-centre pointing down, dark skirt leaves at the sides,
four low pale rocks, brown between.

**Side (`z_side.png`).** A narrower fan (W : H 1.15): a tall frond toward the front (image left, the tallest), a tall
frond toward the back (slightly lower), arching lime fronds to the front and back, a bare **golden stalk** at the centre
(z 1.1–1.6), lime skirt leaves pointing down at the centre, dark skirt leaves at both ends, low rocks only.

**Top, high oblique (`z_top.png`).** About 9–10 leaves radiating from a **small brown crown nub** at the centre: tall
fronds toward the back, lime fronds to the left and right, two big lime lobed skirt leaves toward the camera (front-left
and front), dark leaves at the sides; rocks ring the foot just outside the leaves (grey-blue in shade), seven or eight of
them. Not a true plan (§3.3).

**Leaf junction (close-up 1, `z_cu1.png`).** The crown: a wide, faceted, **orange-brown octagonal hub** (`#7E460D`, lit
`#B46B1E`) with flat-faceted sides; several **dark brown square-ish stalks** splay up and out of its top rim, one
**green stalk** rises from its centre into a frond; **stubby roots** leave the hub's lower flanks and run out and down
to the ground; a big pale rock each side, standing on the ground beside the roots.

**Underside (close-up 2, `z_cu2.png`).** From below: a **star of about nine chunky faceted roots** (`#684125`, lit
`#A56A3A`) round a faceted hub, each root a 5–6-sided prism with a flat cut end; the fronds spread above and behind it
(dark undersides `#274317`); a pale rock (`#A69E9D`) at the lower left.

**Leaf thickness (close-up 3, `z_cu3.png`).** One frond's upper part, nearly edge-on: a lime top face, **a raised
midrib** running along it (a darker green ridge), the lobes cut by rounded notches, and a **darker side band about 0.12
of the frond's width deep** (the thickness) along the lower edge; the double arrow marks it at the tip. The frond bends
gently along its length. Mid `#609C1E`, lit `#84BD2C`, shade `#417A1B`.

### 1.4 Parts (exploded `z_expl.png`, `z_fronds.png`, `z_explbase.png`; parts row `z_parts.png`)

The exploded is a front three-quarter at a larger scale, the fronds lifted off the crown. **The hero governs every size,
angle and position (§3.11); the exploded and parts row govern each part's shape and proportions.**

`expl.py` (principal-axis length L, max width W, the width profile in tenths from tip to base):

| Part (label) | Exploded box (px) | L × W, L : W | Width profile (tip → base) | Tone (light / mid / dark %) | Notes |
| --- | --- | --- | --- | --- | --- |
| Fern Frond (large) | (110–291, 782–972) | 246 × 112, **2.2** | 35 49 70 88 101 108 112 96 69 35 | 1 / 41 / 57 | dark `#3C7E2C`; a thick square-ish **rachis curving in one arc**; **5 big blunt lobes on the outer side**, 3–4 smaller ones on the inner side near the tip; a short bare stalk below the blade; widest at 0.3–0.4 L from the base |
| Fern Frond (medium) | (342–511, 795–959) | pair 186 × 161 (1.15) | — | 23 / 63 / 15 | mid `#6FAF22`; **two blades on one stalk**: a main blade (≈ 150 px, 6 lobes a side) and a smaller one (≈ 110 px, 5 a side) forking from its base at about 35° |
| Fern Frond (small) | (523–626, 860–975) | 150 × 60, **2.5** | 16 28 42 49 56 56 60 54 38 19 | 77 / 22 / 2 | lime `#8ABB05`; 6 lobes a side, both sides; a short stalk; widest at 0.35–0.45 L from the base |
| Root Cluster (base) | (75–229, 1015–1125) | 154 × 110 | | brown `#744928` (lit `#C18145`) | an **octagonal stump** (Ø ≈ 0.30 of the span, a flat top with a small pith mark) with **4–5 splayed square-section legs** ending in flat cut faces |
| Broad Leaf (single) | (556–652, 1028–1129) | 129 × 65, **2.0** | 17 29 43 65 55 59 60 55 46 32 | 18 / 70 / 12 | `#8FCD37`; a **plain faceted kite** (no notches): a centre ridge, 4–5 facets a side, a blunt base and a pointed tip, visible thickness |
| Assembly | (255–548, 968–1196) | | | G `#5D961C` | the crown with a **short peg on its top**, about 7 fronds and skirt leaves on stalks, two pale rocks (`#A39B93`), one lime sprig |

- **Parts row** (each drawn alone, 60–120 px): large L : W 2.0 (dark 65 %), medium pair 1.28 (mid 64 %), small 2.3
  (lime 74 %), root cluster 159 × 100 (`#744A29`), broad leaf 1.85 (`#85C636`, mid 91 %), **rock** 88 × 63 px, W : H 1.4
  (`#8C8C8F` median, lit `#BFA997`: warm lit, cool shade), **ground leaf** 73 × 39 px: **three small rounded leaves in a
  low clump** (`#8EC62A`).
- **Frond construction (z_fronds, close-up 3):** a **thick rachis** (a darker beam, about 0.06 of the frond length thick
  at the base, tapering) carries a **thick lobed blade**: lobes broad and blunt (squarish ends with chamfered corners),
  swept 20–30° toward the tip, **notches rounded and deep (0.45–0.6 of the half-width)**, the last lobes merging into a
  pointed tip. The blade's two halves meet at the rachis at a shallow V, so one half catches the light and the other
  shades (the sheet's lit / dark halves are lighting).
- **Lobe counts:** large 5 (outer) + 3–4 (inner); medium 6 and 5; small 6; skirt leaves in the hero 4 a side (top view
  front-right leaf: 4 notches a side).

### 1.5 How 060 differs from its siblings and the old kit (binding: the verifier checks these)

| | W06 `FernAndBroadleaf` (old kit) | Lobby `FernLeafy` | 059 Grass Tuft | 058 Low Bush | **060 Broadleaf Fern** |
| --- | --- | --- | --- | --- | --- |
| Size | 10.2 × 9.6 × 6.8 tall | 4.2 × 2.4 tall | 3.0 × 2.55 × 2.4 | 6.4 × 5.6 × 4.5 | **3.85 × 3.45 × 3.0 tall, W : H 1.25–1.30** |
| Foliage | 12 thin-slab pinnate fronds with saw-tooth pinnae, a flat star; 3 plain kite leaves | thin rachis with discrete leaflets (a comb) | six pointed lanceolate blades | rosettes of rounded leaves on a branched stem | **8 thick lobed frond blades on stalks (2 tall, 2 arching + 2 forks, 2 small; 5 blunt lobes a side, deep rounded notches, raised rachis) + a skirt of 8 big lobed broad leaves (4 lobes a side, L : W ≈ 1.5) drooping to the ground** |
| Base | soil mound, root nubs, grey boulders | none | hidden cross + post, 4 rocks | trunk on rocks | **a visible orange-brown faceted root crown with 7 splayed roots (front T ≈ 4 %), 7 rocks (2 tall sage ones behind), 6 lime ground sprigs** |
| Colour | one fern green + lime broad leaves (weak contrast) | one green | three greens by blade | lime / mid / dark rosettes | **dark large fronds, lime arching and small fronds, lime skirt in front and dark skirt behind; ochre stalks; brown crown; warm-grey and sage rocks** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, the crown axis at (0, 0)). Plan azimuths: 0° = +X,
counter-clockwise, 90° = +Y (back), 270° = −Y (front).

### 2.1 Stack (binding contact chain, bottom up; every seat gap ≤ 0.03)

| Piece | Sits on / in | Contact |
| --- | --- | --- |
| Root crown hub (one closed ring-stack shell) | ground | flat underside at z 0 … −0.03 |
| Roots (7 closed prisms) | the hub's lower flank | inner end buried ≥ 0.10 in the hub; outer cut end on the ground (z 0 … −0.03) |
| Peg (short post on the hub top) | the hub top | buried ≥ 0.05 |
| Frond stalks (6) and skirt-leaf petioles (8) | the hub's top rim | stalk foot 0.04–0.08 inside the hub top; no boolean |
| Frond blades (8; F3b / F4b fork off their partner's stalk) | the top of their stalk | the stalk's top end runs 0.06–0.12 into the blade's rachis (inside the blade solid), so blade and stalk share one continuous line |
| Skirt leaves (8) | their petiole | as the blades; the leaf tip rests on the ground or a rock within 0.03 where the sheet puts it there (N1), never below z 0 |
| Rocks (7) | ground | flat base sunk ≤ 0.03; may touch a root or a skirt leaf within 0.03, never cut one by more than 0.05 |
| Ground sprigs (6) | ground | base at z 0 … −0.03; ≥ 0.05 clear of rocks |

### 2.2 Root crown (hub + roots + peg)

- **Hub:** 8-sided ring stack, **Ø 0.70 at z 0** (a slight flare), Ø 0.60 at z 0.18, **Ø 0.50 at the top z 0.45**, the
  top a flat octagon with its outer ring chamfered 0.04 (close-up 1's faceted crown). Ring centres offset ≤ 0.03 and radii
  ±6 % per vertex so it reads hand-cut, not lathed.
- **Peg:** 6-sided post Ø 0.14 from the hub top to z 0.58 (the exploded's peg); hidden among the stalk feet in the hero,
  bare on the part.
- **Roots (7):** 5- or 6-sided prisms, Ø 0.20 at the hub tapering to 0.14, leaving the hub's flank at z 0.18–0.28 and
  running out and down in two segments (a knee at 60 % of the run) to a **flat cut end square to the axis** on the ground
  at r 0.80–1.00. Azimuths about **15°, 65°, 120°, 170°, 215°, 268°, 320°** (±8°, uneven lengths r 0.80 / 0.95 / 0.85 /
  1.0 / 0.82 / 0.9 / 0.95). Close-up 2 shows about nine; seven carry the read at this size (decision §8.6).
- **Visibility:** the roots and the hub's lower half show **between the skirt leaves and the rocks** in the front, f34,
  rear and r34 (T 3.8–5.8 %, 60–90 % of it in the lowest fifth). Not hidden like 059's root base; not a big stump either
  (WorldModeling §18 "tree stump with leaves": T ≤ 6 % in every side view).
- Part about 2.0 × 2.0 × 0.58.

### 2.3 Upper fronds (6 stalks, 8 blades)

Root = the stalk foot on the hub top rim (r 0.15–0.20 at the frond's azimuth, z 0.42); blade base = where the lobed blade
starts on the stalk; tip = the blade's tip point. L = blade length along its curved rachis. "Apex" = the blade's highest
point (the tall fronds curl over, so the apex is below the tip in plan but at about the tip's height).

| Frond (part) | Az | Stalk: foot → blade base | Blade base (x, y, z) | Tip (x, y, z) | Apex z | L | W max (at, from base) | Lobes a side | Curve | Tone (§5) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F1** tall (large) | 222° | 0.80, Ø 0.13 → 0.11 | (−0.28, −0.26, 1.15) | **(−1.05, −0.95, 2.90)** | **3.00** (at 0.8 L) | 2.25 | 0.92 (0.35 L) | 5 outer + 4 inner | rises steep, the last 25 % curls outward | deep base → dark → mid outer lobes |
| **F2** tall (large) | 45° | 0.75, Ø 0.13 → 0.11 | (+0.25, +0.26, 1.10) | **(+1.32, +1.38, 2.78)** | 2.86 | 2.15 | 0.88 (0.35 L) | 5 + 4 | as F1 | dark base → mid → light tip |
| **F3** arching left (medium, main) | 165° | 0.55, Ø 0.11 → 0.09 | (−0.42, +0.12, 0.90) | **(−1.80, +0.45, 1.66)** | 1.95 (at 0.45 L) | 1.80 | 0.62 (0.4 L) | 5 + 5 | rises to 0.45 L, then droops outward | mid base → light |
| **F3b** fork of F3 (medium, minor) | 132° | forks off F3's stalk at 0.6 of its length | (−0.30, +0.30, 0.95) | **(−1.25, +1.10, 2.10)** | 2.12 | 1.40 | 0.50 (0.4 L) | 5 + 5 | gentle arc | dark → mid tip |
| **F4** arching right (medium, main) | 345° | 0.55, Ø 0.11 → 0.09 | (+0.42, −0.12, 0.90) | **(+1.85, −0.50, 1.88)** | 2.05 | 1.85 | 0.62 (0.4 L) | 5 + 5 | as F3 | mid base → light |
| **F4b** fork of F4 (medium, minor) | 18° | forks off F4's stalk | (+0.32, +0.10, 0.95) | **(+1.45, +0.55, 1.40)** | 1.70 | 1.35 | 0.50 | 5 + 5 | arcs out and down | dark → mid tip |
| **F5** small, front | 258° | 0.40, Ø 0.09 | (−0.10, −0.40, 0.80) | **(−0.45, −1.60, 1.25)** | 1.45 | 1.35 | 0.52 (0.4 L) | 5 + 5 | arches toward the camera and droops | mid base → light |
| **F6** small, back | 95° | 0.45, Ø 0.09 | (−0.03, +0.40, 0.85) | **(−0.15, +1.72, 1.70)** | 1.80 | 1.40 | 0.52 | 5 + 5 | arches back | mid base → light |

- **Hierarchy check:** apexes 3.00 / 2.86 / 2.12 / 2.05 / 1.95 / 1.80 / 1.70 / 1.45; no two blades within 10 % of each
  other in both length and azimuth spacing; the two tall fronds 177° apart in plan and leaning 25–35° from vertical.
- **Views this plan gives:** front: F1 left and F2 right tall, F3 far left and F4 far right arching, F3b dark behind F3
  (the sheet's five); side: F1 front and F2 back tall, F5 front and F6 back arching (the sheet's four); rear: the front
  mirrored. Check against §1.2's tip table (±0.06 H).
- **Blade shape (each blade in its own frame, u along the rachis, v across):**
  - **Rachis spine:** a smooth arc of 7–8 stations from the blade base to the tip (curvature as the Curve column),
    continuing the stalk's line.
  - **Outline:** half-width envelope (fraction of W / 2) base 0.35, 0.2 L 0.85, 0.35 L 1.0, 0.6 L 0.85, 0.85 L 0.45, tip a
    point. Along each side, **5 lobes**: each lobe a blunt squarish tongue (three outline verts: front corner, outer end,
    back corner; the outer end chamfered), swept 20–30° toward the tip; between lobes a **rounded notch** (one or two verts)
    reaching **0.45–0.6 of the local half-width** toward the rachis. Lobe widths 0.18–0.35 studs (never thinner than
    0.15). The tip is the last lobe pair merging into a point (tip angle 35–50°, not a needle).
  - **Large-frond asymmetry (§3.7):** F1 / F2 outer-side lobes reach the full envelope; inner-side lobes 0.75 of it.
  - **Thickness (close-up 3):** blade **0.07** thick at the edges; the rachis a raised ridge **+0.04 above and +0.03
    below** the blade surfaces (so 0.14 at the rachis), tapering to 0.06 at the tip. The two halves meet at the rachis in
    a **shallow upward V (dihedral 15–25°)**, so the halves light differently. Total thickness reads in the side view
    (`edge_side`).
  - **Topology:** a strip built from the spine: each lobe is a fan from 2–3 spine verts to its outline verts, top and
    bottom, plus side walls round the outline. Closed, manifold, no n-gons, no bowties at the lobe corners or the tip.
- **Roll:** each blade's top face turned toward the sky and outward (the sheet shows the tops of the fronds in every
  view); F5 and F6 rolled so their faces show in the side view. In the front and f34, ≤ 15 % of blade area within 12° of
  edge-on.
- **Clearances:** blades may overlap each other near the crown (separate shells) but **no blade more than 25 % inside
  another**; every blade vertex past 0.3 L at z ≥ 0.25; nothing inside a rock (ray parity).

### 2.4 Skirt: lobed broad leaves (8)

Each is a **broad lobed leaf** (the kite of the "Broad Leaf (single)" part with **4 rounded notches a side**, §3.5) on a
short petiole from the hub top rim (z 0.40, r 0.22, Ø 0.09, 0.30–0.40 long, rising 30–40° then turning out), the blade
arching out and drooping so the tip lands where the table says.

| Leaf | Az | Tip (x, y, z) | L | W | L : W | Lobes a side | Tone |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **N1** front, points down | 290° | (+0.60, −1.70, **0.02**: rests on the ground) | 1.55 | 1.00 | 1.55 | 4 | light, mid base |
| **N2** front-left, droops toward the camera | 245° | (−0.75, −1.55, 0.55) | 1.50 | 1.05 | 1.45 | 4 | light, mid base |
| **N3** right | 335° | (+1.85, −0.80, 0.30) | 1.75 | 1.10 | 1.6 | 4 | mid → light |
| **N4** far left, low | 185° | (−1.92, −0.25, 0.43) | 1.65 | 0.95 | 1.75 | 4 | dark |
| **N5** left-low | 212° | (−1.40, −1.05, 0.18) | 1.35 | 0.85 | 1.6 | 4 | mid, dark base |
| **N6** back-left | 145° | (−1.60, +0.95, 0.90) | 1.60 | 0.95 | 1.7 | 4 | dark |
| **N7** back | 90° | (+0.10, +1.80, 0.40) | 1.70 | 1.00 | 1.7 | 4 | dark |
| **N8** back-right | 30° | (+1.65, +1.00, 0.95) | 1.55 | 0.95 | 1.65 | 4 | dark → mid tip |

- **Shape:** a kite outline (widest at 0.4 L from the base, the base blunt at 0.45 W, a pointed tip of 45–60°) with 4
  lobes a side cut by rounded notches 0.40–0.50 of the local half-width deep, a raised midrib, the halves in a shallow V
  (dihedral 15–20°), thickness 0.07 (0.12 at the midrib). About 110 tris each (§4.3).
- **Placement checks:** N1's tip on the ground beside R2 (≥ 0.03 clear of it); N2 drapes over R1's back top (within 0.03,
  never inside); N3 passes over R3; N4 / N5 over R4; the sage rocks R5 / R6 sit behind N6 / N8 and peek above them by
  0.10–0.25 in the front and f34 (§3.9).

### 2.5 Rocks (7) and ground sprigs (6)

| Piece | Centre (x, y) | Size W × D × H | Yaw | Build |
| --- | --- | --- | --- | --- |
| R1 large, front-left | (−0.62, −1.05) | 0.85 × 0.70 × 0.55 | 20° | ring stack: 7-sided base ring (r ±10 %), widest ring at 0.35 h, a shoulder ring at 0.75 h pulled in 25 %, a sloping 5–6-sided top; 10–12 broad facets; flat base |
| R2 medium, front | (+0.30, −1.30) | 0.62 × 0.52 × 0.42 | −30° | as R1, 9–11 facets |
| R3 medium, right | (+1.35, −0.85) | 0.58 × 0.50 × 0.48 | 55° | as R1 |
| R4 small, left | (−1.55, −0.60) | 0.45 × 0.40 × 0.35 | 10° | 7–9 facets |
| R5 sage, back-left | (−1.20, +0.85) | 0.70 × 0.60 × 0.80 | −15° | an upright faceted block with a pointed 4–5-sided top (f34's pyramid peak); moss-stained upper half (§5) |
| R6 sage, back-right | (+1.15, +0.95) | 0.80 × 0.65 × 1.00 | 35° | as R5, taller (the front's pale peak; §3.9) |
| R7 small, back | (−0.10, +1.35) | 0.50 × 0.42 × 0.35 | 40° | 7–9 facets |

- Rocks are angular blocks (WorldModeling §12.1), **never `K.hull_rock` eggs**, never lavender. `m047._rock` /
  `m055._rock` (committed) can serve; reshape them to these sizes. 059's rock builder is the same family (the sheet's
  "reusable" rock).
- **Ground sprigs (the "Ground Leaf (small, optional)" part):** 2–3 small rounded leaf blades in a low clump, 0.30–0.40
  across, 0.12–0.18 tall, each leaf a thick 4–5-sided gem (about 10 tris), at about (−0.10, −1.95), (+1.05, −1.45),
  (−1.25, −1.55), (+2.00, −0.30), (−2.05, +0.35), (+0.55, +1.90); nudge each outward until it is ≥ 0.05 clear of rocks
  and leaves and on the ground.

### 2.6 Expected extents and screen checks

- **Extents:** X −2.05 … +1.95 (N4 / F3 and F4 / N3 tips plus widths), Y −2.0 … +1.95, Z 0 … 3.00. Bbox about 3.85–4.0 ×
  3.45–3.9 × 3.0 (if the depth runs past 3.65, pull the front / back skirt tips in).
- **Checks on the renders** (floor hidden; `meas.py` with this folder's `m.py`):
  - **front_sheet (0, 5)** — governs positions:
    - W : H 1.18–1.32 (sheet 1.251); G 81.5 ± 4, R 8.9 ± 3, T 3.8 ± 1.5; fill 0.65 ± 0.05.
    - The top profile within ±0.08 for f .1–.9; the five frond tips at §1.2's (x, z) ±0.06 H; N1's tip on the ground.
    - At h .85 and .95 two separate runs (the tall fronds) with a gap ≥ 0.15 H.
    - Leaf tones light / mid / dark 31 / 29 / 40 ± 8.
  - **f34_sheet (0, 20)** (probe az −20 … +20 × e 15 / 20 / 25; keep the best; §3.2): W : H 1.24–1.37 (sheet 1.305); G 80
    ± 4, R 10.7 ± 3, T 4.6 ± 1.5; tones 33 / 29 / 38 ± 8; the stalk of F2 shows between the leaves.
  - **rear_sheet (180, 5), r34_sheet (180, 20)** (probe 160 … 200): W : H 1.26–1.40; two tall fronds apart above h .85;
    T 4–6 %.
  - **side_sheet (90, 5):** W : H 1.08–1.22 (sheet 1.152); a tall frond front and back, arching fronds front and back,
    a bare stalk at the centre (z 1.1–1.6), low rocks.
  - **top_sheet (0, 60)** (probe e 50–70): content only (§3.3): 9–10 radiating leaves round a visible brown crown nub,
    rocks ringing the foot outside the leaves.

## 3. View conflicts and resolutions

### 3.1 Sheet number
- **Evidence.** The header says "58 / 132"; INDEX.md row 60 lists `060.png` as "Broadleaf Fern Model Study".
- **Resolution.** Our number is 060 (file name, keys `m060_*`). Note the header in the export notes only.

### 3.2 The three-quarter views are near-frontal and near-rear, drawn from higher up
- **Evidence.** The f34 frond tips sit at the front's x fractions within ±0.04 W (§1.3); W : H 1.305 vs 1.251; the rock
  tops, root crown and ground show more. The r34 matches the rear the same way (W : H 1.367 vs 1.327).
- **Resolution (decision §8.9).** `front_sheet (0, 5)` governs positions; `f34_sheet (0, 20)` governs the read and the
  shares. Probe az −20 … +20 (e 15–25), keep the best and record the camera; the same for r34 at 160 … 200.

### 3.3 The "top" cell is a high oblique, not a plan
- **Evidence.** The "top" shows the tall fronds rising toward the image top and the leaf undersides and rock sides; its
  W : H (1.136) mixes depth and height.
- **Resolution.** Render it at (0, 60) (probe e 50–70) and judge it for content only (radiating leaves, the crown nub,
  the rock ring). Depth comes from the side cell (3.46).

### 3.4 Every ortho view draws the same fan
- **Evidence.** Front, rear and side each show two tall fronds in a V and two arching fronds to the far sides (§1.2). A
  plant whose tall fronds lean only left and right would show them overlapping in the side view.
- **Resolution.** Put the two tall fronds on one diagonal (F1 front-left, F2 back-right) and the arching fronds and small
  fronds round the other directions (F3 left, F4 right, F5 front, F6 back), so every ortho view shows two tall and two
  arching fronds (§2.3). Front governs X and Z; side governs Y. The side's tall back frond is drawn 0.2 lower than the
  front's F2: F2's apex is set between (2.86).

### 3.5 "Broad Leaf (single)" is a plain kite, but every assembled leaf is lobed
- **Evidence.** The exploded and parts row draw the broad leaf as a plain faceted kite with no notches, and the
  exploded's arrow points it at the assembly's lower right leaf; but that leaf, and every skirt leaf in the f34, r34,
  front, rear, side and top, has 3–4 deep rounded notches a side.
- **Resolution (decision §8.5).** **The hero's skirt leaves are lobed** (the drawings of the assembled plant govern);
  they keep the kite's construction (centre ridge, a blunt base, the widest point at 0.4 L, a pointed tip) with 4 notches
  a side cut in. The exported `…BroadLeaf` part is one hero skirt leaf (lobed), so a reused leaf matches the hero. The
  alternative is the parts row's plain kite as the part.

### 3.6 Root cluster: a tall stump with legs, or a low hub with a root star
- **Evidence.** The exploded and parts row draw a **tall octagonal stump with 4–5 long legs** (height ≈ 0.65 of its
  span); close-ups 1 and 2 show a **low faceted hub with about nine short roots**; the assembled views show only a low
  brown crown between the leaves.
- **Resolution (decision §8.6).** A **low hub (0.45 tall, Ø 0.5–0.7) with 7 splayed roots** (§2.2): the close-ups and the
  hero govern; the parts row's flat cut ends and square-ish legs give the root shape. The exported `…RootCrown` part is the
  hero's crown (hub, roots, peg).

### 3.7 Large frond: lobes on one side (parts) or both (hero)
- **Evidence.** The exploded / parts row large frond has 5 big lobes on its outer side and small ones on the inner side;
  in the hero F1 and F2 show lobes on both sides.
- **Resolution.** Both sides lobed, the inner side's lobes 0.75 of the outer's (§2.3). The part is the hero's F1.

### 3.8 Medium frond = a forked pair
- **Evidence.** The exploded and the parts row both draw "Fern Frond (medium)" as two blades sharing one stalk (a main
  blade and a smaller fork at its base).
- **Resolution.** F3 + F3b and F4 + F4b are the two medium pairs (§2.3); the part exports F3 with F3b on one stalk.

### 3.9 Tall moss-stained rocks show only in the front and f34
- **Evidence.** The front shows a pale faceted peak behind the right-hand leaves at z 1.2–1.5 and a rock at the far left
  reaching about 1.0; the f34 shows two tall green-grey pyramid rocks behind the skirt (back-left `#7C8D7F` and
  back-right, half moss-green, half pale). The side and rear show only low rocks.
- **Resolution (decision §8.5).** Two **sage-stained back rocks, R5 0.80 and R6 1.00 tall**, mostly behind the back
  skirt leaves, peeking 0.10–0.25 above them in the front and f34; not the full 1.5 (the side and rear would then show
  them).

### 3.10 The palette's six swatches are unlabelled
- **Evidence.** S1 `#32692F` dark green, S2 `#4E8A25` mid green, S3 `#AFCC15` lime, **S4 `#B8BA9B` pale sage**, S5
  `#B8AEA4` warm grey, S6 `#8F5928` brown. S4 matches nothing green in the plant; it matches the sage-stained rocks (f34
  `#7C8D7F` / `#849782` in shade).
- **Resolution.** S1–S3 are the frond greens, **S4 the moss stain on the rocks** (`m060_rock_sage`), S5 the rocks, S6
  the root crown (§5.1).

### 3.11 Exploded scale vs the hero
- **Evidence.** The exploded draws each frond larger and more upright than the hero and its root cluster taller; the
  parts row are thumbnails.
- **Resolution.** The hero governs size, lean and position; the exploded governs each part's outline (L : W, lobe count,
  a thick rachis, a bare stalk, the pair) and tone role.

### 3.12 "Solid colours, no texture noise" vs the user's colour rule
- **Evidence.** The notes ask for simple shapes and solid colours; the user wants rich, blended colour with broad Tint
  mottling (memory `lighting-not-paint`).
- **Resolution.** Frond greens blended by frond role and position along the frond; broad Tint per blade and per lobe band
  (0.03–0.04), never per-triangle confetti.

### 3.13 Ground: no soil patch
- **Evidence.** Every cell shows the floor glow and a soft neutral shadow, no soil disc; the dark brown between the
  leaves is shade on the roots and the crown.
- **Resolution (decision §8.7).** **No soil patch.** The terrain is the ground.

### 3.14 Lighting
- The sheet is lit from the upper right (lime on the upper faces of the lobes, dark in the creases and on the inner halves
  of the fronds; rocks warm on the lit faces, blue-grey in shade). The lighting does that; never paint it by facing.
  Render every `*_sheet` view with the studio floor hidden.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its exploded / parts-row cell

1. `blade(spec)` → one closed lobed frond blade (§2.3): spine arc, envelope, lobes and notches, rachis ridge, V-fold,
   thickness. Build it in bmesh in its own frame. Check against `z_fronds.png`: L : W, lobe count, notch depth, blunt
   lobes, a pointed tip, the ridge and the side band. m049's `_blade_local` / `blade` and m055's `blade` (committed)
   are references for a ridged closed blade on a drooping spine; m055's `leaf(lobes=…)` for notch geometry (it is flat;
   ours needs the spine strip).
2. `stalk(spec)` → a 5-sided tapered prism along a gentle curve (2–3 segments) from the hub rim to the blade base,
   running 0.06–0.12 into the blade's rachis.
3. `frond(spec)` → stalk + blade (+ the fork for F3 / F4: the minor blade's stalk leaves the main stalk at 0.6 of its
   length, 0.05 inside it).
4. `skirt_leaf(spec)` → petiole + lobed kite blade (§2.4).
5. `root_crown()` → hub, peg, 7 roots (§2.2), closed shells, roots buried ≥ 0.10 in the hub (no booleans).
6. `rock(spec)` ×7, `sprig(spec)` ×6 (§2.5), all through the ray-parity guard (`m047._Solids`, committed).
7. **Hero `BroadleafFern`** = root crown + 6 fronds (8 blades) + 8 skirt leaves + 7 rocks + 6 sprigs, one object of
   closed shells.
8. **Parts shot** (0, 15) laid out like the parts row: LargeFrond, MediumFrond, SmallFrond, RootCrown, BroadLeaf, Rock,
   GroundLeaf, gaps 0.4.
9. **Exploded shot:** the crown in the middle, each frond lifted 0.8 along its stalk axis, the skirt leaves lifted 0.4,
   rocks in place.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a lush fern about 1.3 × as wide as tall; two tall fronds apart at the top; lime fronds arching to
   the sides; a lobed skirt to the ground; brown crown and roots between; a rock ring with two taller sage rocks behind.
2. **front_sheet / f34_sheet** per §2.6 (shares, fill, W : H, top profile, tip positions, separate runs at h .85 / .95).
3. **rear / r34 / side / top** per §2.6.
4. **Close-up renders:**
   - `junction_cu` (−20, 10) on the crown against close-up 1: a faceted hub, stalks splaying from its top rim, roots
     running down to the ground, rocks beside.
   - `underside` (0, −60) on the RootCrown part (or the hero with the floor hidden) against close-up 2: a root star with
     flat cut ends.
   - `thickness_cu` near edge-on on F1's upper half against close-up 3: the lobed edge, the raised rachis, the side band.
   - `edge_side` (90, 0): every blade shows thickness (≥ 0.06 on screen in studs).
   - `thumb`: the front at about 120 px tall: each upper frond still shows ≥ 3 notches a side, the skirt leaves ≥ 2.
5. **Contact counts** (§6): floating shells 0; every blade on its stalk, every stalk in the hub, every root in the hub
   and on the ground; buried 0.
6. **Hero size** per §2.6, plus a **scale shot** with a 5.5-stud marker beside the fern (the top at 0.55 of the marker).

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Large blades F1, F2 (8 spine stations, 5 + 4 lobes, top + bottom + walls) | 2 | 160–190 | 320–380 |
| Medium blades F3, F4 / forks F3b, F4b (5 + 5 lobes) | 4 | 130–160 | 520–640 |
| Small blades F5, F6 | 2 | 120–150 | 240–300 |
| Frond stalks (5-sided, 2–3 segments) | 6 + 2 fork stalks | 20–30 | 160–240 |
| Skirt leaves (4 + 4 lobes) + petioles | 8 | 100–120 + 16 | 930–1100 |
| Root crown: hub (8-sided, 4 rings) + peg + 7 roots (6-sided, 2 segments, cut end) | 1 | 60 + 16 + 7 × 36 | 330 |
| Rocks (ring stacks) | 7 | 24–40 | 200–240 |
| Ground sprigs (2–3 gems) | 6 | 20–30 | 120–180 |
| **Hero** | | | **about 2850–3400; aim ≤ 3300; ceiling 3800** |
| Parts: LargeFrond / MediumFrond / SmallFrond / RootCrown / BroadLeaf / Rock / GroundLeaf | | | 210 / 330 / 170 / 330 / 130 / 40 / 30 |

- **Over budget?** First drop the inner-side lobes of the large fronds to 3, then the skirt leaves to 3 lobes a side on
  N4–N8 (behind), then one spine station per blade. **Never** thin the blades into cards or the lobes into slivers to
  save triangles.
- **Lean alternative** (decision §8.14): about 2000 tris with 4 lobes a side, 6 skirt leaves and 5 rocks, if the main
  session wants a lighter repeated asset.

### 4.4 What to do better than W06's `FernAndBroadleaf`, the lobby `FernLeafy` and recent foliage

| Earlier | This one |
| --- | --- |
| W06: "flat star of wide leaves (ref arching fronds)"; thin slabs; 12 even fronds; one fern green, weak contrast to the lime leaves | 8 blades in a clear hierarchy (two tall, two arching, two forks, two small) that **arch**; 0.07 blades with a 0.14 rachis; dark large fronds against lime arching fronds and skirt |
| Lobby `FernLeafy`: thin rachis with discrete leaflets (a comb) | one solid lobed blade per frond: lobes joined to the blade, notches only 0.45–0.6 deep, lobes 0.18–0.35 wide |
| 049 r1: "shields and pads", merged tiers | long lobed fronds (L : W 2.2–2.9) standing apart above h .80; the skirt is a separate lower layer |
| 054 r1: leaves read as pointed diamond shards | blunt squarish lobes with rounded notches; only the leaf tip is pointed |
| 047 r1: spiky plants, flat pad undersides | thick blades with closed, faceted undersides and a ridge below the rachis |
| 035 / 036 / 046 / 047 r2: floating or buried dressing | every blade on a stalk in the hub, every root in the hub and on the ground; ray-parity guard; counts reported |

### 4.5 Stages 2 and 3
- **Stage 2:**
  - Every shell closed and manifold, **0 bowties** (likely at lobe corners, notch verts and blade tips; `M.fix_bowties`,
    or a two-vert tip).
  - **0 winding errors per shell** (hand-built strips flip easily: `bmesh.ops.recalc_face_normals` per shell, then check
    every shell with `m047.shells_report`).
  - No zero-area faces; corners ≥ 3°; no n-gons except the hub top and rock bases (triangulate if the audit asks).
  - Origin at the bottom centre, transforms applied.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box)

| Swatch | Box | Hex | HSV | Use |
| --- | --- | --- | --- | --- |
| S1 dark green | (798,55,823,82) | `#32692F` | 117°, 0.55, 0.41 | start for `frond_dark` |
| S2 mid green | (835,55,860,82) | `#4E8A25` | 96°, 0.73, 0.54 | start for `frond_mid` |
| S3 lime | (871,55,896,82) | `#AFCC15` | 70°, 0.90, 0.80 | start for `frond_light` |
| S4 pale sage | (907,55,929,82) | `#B8BA9B` | 64°, 0.17, 0.73 | start for `rock_sage` (§3.10) |
| S5 warm grey | (940,55,962,82) | `#B8AEA4` | 30°, 0.11, 0.72 | start for `rock` |
| S6 brown | (973,55,997,82) | `#8F5928` | 29°, 0.72, 0.56 | start for `root` |

### 5.2 Rendered regions (`samp.py`, `samp2.py`; median / lit quartile / shade quartile / v > .7)

| Region | Median | Lit Q | Shade Q | v > .7 |
| --- | --- | --- | --- | --- |
| All green: front / f34 / rear / side / r34 | `#5D961C` (88°, .81, .59) / `#61991C` / `#498216` / `#6A9F0F` / `#619D15` | `#AEDB28` / `#AFD926` | `#134111` / `#174511` | `#A1D224` / `#9FCF24` |
| Light tone: front / f34 / rear / side | `#A8D722` (76°, .84, .84) / `#A9D51F` / `#A1D01A` / `#9CCA14` | `#C9EA33` / `#C2E52A` | `#8ABC13` | |
| Mid tone: front / f34 / rear / cu3 | `#69A520` (87°, .81, .65) / `#68A120` / `#5A951B` / `#5C971E` | `#89C82E` / `#87C433` | `#498116` | |
| Dark tone: front / f34 / rear | `#1B5116` (115°, .73, .32) / `#1E5416` / `#1C5011` | `#306E24` / `#326F2A` | `#0A2A07` | |
| Tone shares (light / mid / dark %) | front 31 / 29 / 40; f34 33 / 29 / 38; rear 28 / 28 / 44; r34 37 / 26 / 37; side 38 / 34 / 28 | | | |
| Tone bands, front (h < .25 / .25–.5 / .5–.75 / > .75) | 37/21/41; 26/35/37; 32/23/43; 29/35/34 (f34 43/22/34; 28/31/39; 33/27/38; 26/34/38) | | | |
| Fronds in the hero: f34 tall large F1 / tall F2 / arching F3 / arching F4 | `#3C741C` (98°, .76, .45) / `#619F17` / `#8CBF20` (79°) / `#8BB618` | `#AAD71E` / `#A3D31A` / `#B0DB1B` / `#BADF18` | `#1C5513` | |
| Parts / exploded fronds: large / medium / small | `#33782D` (115°) – `#3C7E2C` (108°) / `#67AB21` – `#6FAF22` (87–90°) / `#88B703` – `#8ABB05` (76°) | `#73AF35` / `#9CD12F` / `#AED306` | | |
| Skirt leaves: front N1 / f34 front leaves / f34 down leaf / f34 right leaf / f34 left dark leaves | `#9CD124` (78°, .83, .82) / `#89C318` / `#88C426` / `#8DC531` / `#54892E` (95°) | `#CBEB3F` / `#C7E825` / `#C1E43D` / `#B4DE3F` / `#78B628` | | |
| Broad leaf part / exploded | `#85C636` (87°, .73, .78) / `#8FCD37` | `#91CE39` / `#A5D841` | `#599F26` | |
| Ground sprig part | `#8EC62A` (82°, .79, .78) | `#A0D22F` | `#5D9528` | |
| Stalks: f34 / side | `#8E670F` (42°, .89, .56) / `#967B09` (49°) | `#9A6E19` / `#A7880F` | `#5E5006` | |
| Root: parts / exploded / cu2 / cu1 crown | `#744A29` (26°, .65, .45) / `#744928` / `#684125` / `#7E460D` (30°, .90) | `#BF8047` / `#C18145` / `#A56A3A` / `#B46B1E` | `#4A2D17` / `#482C17` / `#4A2E17` / `#3E2002` | `#C28349` / `#CA8546` |
| Root in the hero (T, v ≥ .25): front / f34 / r34 / rear | `#684324` (27°, .65, .41) / `#6E4B17` / `#734A28` / `#7E5C35` | `#AB895D` / `#BB9B6D` | `#462C0E` | |
| Rock: front cells (front / rear / top / big front rock) | `#7F7C76` (40°, .07, .50) / `#817D7B` / `#858483` / `#827D77` | `#C0BEA8` / `#C7C4AD` / `#DFC2AB` | `#4D4F4D` / `#515554` | `#D3C5AD` / `#C2C0AA` / `#EACEB1` |
| Rock: parts / cu2 / cu1 right | `#8C8C8F` / `#A69E9D` / `#848286` | `#BFA997` / `#DAC9BA` / `#C4AB96` | `#757378` / `#91887F` | `#BEA997` / `#D6C6B4` |
| Sage rocks (f34, shade) | `#7C8D7F` / `#849782` (back-left); back-right half moss-green, half pale pink-grey | `#899992` | `#3A3E39` | `#BDB4A1` |
| Cast shadow (not modelled) | neutral grey, s < 0.07 | | | |

### 5.3 How the colour works

- **Fronds: four greens by frond role and by position along the frond** (never facing):
  - **Role:** the large fronds F1 / F2 are the dark fronds (dark body, mid outer lobes on F2, as the hero); the arching
    fronds F3 / F4 and small fronds F5 / F6 are lime; the forks F3b / F4b are dark with a mid tip.
  - **Along the frond:** the lowest 0–0.15 L one step deeper than the body (`green_deep` at the stalk junction), the
    upper 0.6–1.0 L one step lighter on the lime and mid roles. F1: deep 0–0.15 → dark 0.15–0.75 → 35 % mid 0.75–1.0.
    F2: deep → dark 0.15–0.45 → mid 0.45–0.8 → 40 % light tip. F3 / F4 / F5 / F6: mid 0–0.25 → light 0.4–1.0. F3b / F4b:
    deep → dark → mid tip.
  - **A whole spine-station band takes one blend step,** across both halves and the edges, so the lit-half / shaded-half
    contrast comes only from the light (the V-fold).
  - **Rachis ridge:** the ridge faces of the lime fronds take one step darker (mid on a light band) along the whole
    length: the sheet's darker midrib line on lime leaves (a region, not facing).
- **Skirt leaves (`leaf_fresh` family):** N1 / N2 light with a mid base; N3 mid → light; N5 / N8 mid with a dark base;
  N4 / N6 / N7 dark (`frond_dark`) with a deep base. The front three must read lime against the darker fronds behind
  (W06's weak-contrast failure).
- **Stalks:** `root` brown at the foot (0–0.25 of the stalk), blending to `stalk` ochre (0.25–0.7), then to the blade's
  base key at the blade.
- **Root crown:** `root` body; `root_light` on the roots' cut ends, the hub top ring and the peg top (close-up 1's lit
  facets as regions); `root_deep` on the lowest 0.08 band of the hub and roots (a damp foot, by height).
- **Rocks:** warm grey `rock`; the lowest 25 % a step deeper (`rock_deep`), by height within each rock. **R5 / R6: the
  upper 50 %** `rock_sage`, and its −X half above 0.3 h on R6 (the moss side the f34 shows; by position on the rock, not
  facing). R1 / R7 may take a 20 % sage band at the top back. R ≥ G ≥ B on the plain rock; never lavender or blue.
- **Ground sprigs:** `leaf_fresh` and `frond_light`, alternating by sprig.
- **Hues stay apart:** root 25–30°, stalk 42–50°, rock 25–35° at s ≤ 0.14, sage 60–90° at s 0.12–0.20, frond light
  74–78°, leaf fresh 80–86°, frond mid 86–92°, frond dark 105–116°, green deep 108–118°.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians where the sheet gives them, swatches where it doesn't. `K.sample` kinds:
`"vivid"` for the light keys, `"green"` for mid / dark / deep, `"stone"` for the rocks, `"brown"` for root and stalk.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m060_frond_light` | front light-tone median `#A8D722` ± 12 (lit `#C9EA33`; start S3 `#AFCC15`) | 74–78°, ≥ 0.80 | upper F3–F6, F2's tip, N1 / N2 light bands, sprigs | rough 0.8, low spec |
| `m060_leaf_fresh` | skirt-leaf / broad-leaf median `#8CC82E` ± 12 (`#9CD124`, `#88C426`, `#85C636`) | 80–86°, 0.72–0.85 | skirt leaf bodies N1–N3, N5's tip, sprigs | rough 0.8 |
| `m060_frond_mid` | mid-tone median `#69A520` ± 12 (parts medium `#67AB21`; start S2 `#4E8A25`) | 86–92°, 0.75–0.85 | bases of the lime fronds, F2's body, fork tips, ridges on lime bands | rough 0.85 |
| `m060_frond_dark` | large-frond median `#3A7A2C` ± 12 (exploded `#3C7E2C`, parts `#33782D`; start S1 `#32692F`) | 105–116°, 0.60–0.72 | F1 / F2 bodies, forks, back skirt leaves N4 / N6 / N7 | rough 0.85 |
| `m060_green_deep` | the dark shade quartile `#174511` seen lit, about `#28561E` ± 12 | 108–118°, 0.60–0.72 | the lowest 0.15 L of every frond, dark leaves' bases | rough 0.9 |
| `m060_stalk` | stalk median `#8E670F`–`#967B09`, target `#906F12` ± 12 | 42–50°, 0.80–0.92 | frond stalks 0.25–0.7, petioles' middle | rough 0.85 |
| `m060_root` | parts / exploded root median `#744A28` ± 12 (start S6 `#8F5928`) | 25–30°, 0.60–0.70, **R > G > B** | hub, roots, stalk feet | rough 0.9 |
| `m060_root_light` | root lit `#BF8047` ± 12 | 26–30°, 0.58–0.66 | cut ends, hub top ring, peg top | rough 0.85 |
| `m060_root_deep` | root shade `#4A2D17` seen lit, about `#5A3820` ± 12 | 24–28°, 0.60–0.70 | the lowest 0.08 of hub and roots | rough 0.95 |
| `m060_rock` | rendered rock median `#827D77` ± 12 and v > .7 `#CDC0AC` ± 12 (start S5 `#B8AEA4`) | 25–35°, 0.06–0.14, R ≥ G ≥ B | rock bodies | rough 0.85, metal 0 |
| `m060_rock_deep` | rock shade `#4D4F4D` seen lit, about `#77716B` ± 12 | 25–35°, 0.08–0.14 | the lowest 25 % of each rock | rough 0.9 |
| `m060_rock_sage` | S4 `#B8BA9B` swatch, rendered toward `#9AA486` ± 12 (sheet shade `#7C8D7F`) | 60–90°, 0.12–0.22 | R5 / R6 upper halves, R6's −X side, a top band on R1 / R7 | rough 0.9 |

**Calibration warnings:**
- **The kit studio lights both halves** (042, 047, 054): calibrate the greens to the tone medians and the parts medians,
  not the lit quartile alone, and check the tone shares on the fern's own renders (front 31 / 29 / 40 ± 8). Record the
  lit-shade bias.
- **Greens must not lean yellow or olive** (047's plants flagged yellow): `frond_mid` ≥ 86°, `frond_dark` ≥ 105° on every
  median; only `frond_light` is lime (74–78°, never below 72°); the front all-green median within 15 of `#5D961C`.
- **Contrast:** the dark large fronds must read clearly darker than the lime arching fronds and the front skirt (f34
  `#3C741C` vs `#8CBF20`); W06 failed on this.
- **Rocks never lavender:** R ≥ G ≥ B on the plain rock, s ≤ 0.14; the cool shade comes from the light; the sage keys stay
  green-grey, not mint.
- **Stalks stay ochre, the root stays orange-brown:** stalk 42–50°, root 25–30°.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Blades:** per spine-station band (both halves and the edges of a band together), by fraction of L and the frond's
  role (§5.3); bands blend across one band on each side; the tip takes the last band's key.
- **Skirt leaves:** base band → tip band as §5.3.
- **Stalks:** root → stalk → blade base, by fraction of the stalk.
- **Root crown:** by height (deep band) and by member (cut-end faces `root_light`, hard).
- **Rocks:** height bands within each rock; sage by height and by position on R6.
- **Hard edges only** where materials meet: stalk foot | hub, root | ground, rock | anything.

### 5.6 Texture (Tint) and finish
- **Tint:** blades 0.04 per blade + 0.02 per lobe band; skirt leaves 0.04 each; stalks 0.03; root 0.03 per member; rocks
  0.04 per facet; sprigs 0.03.
- **Finish:** greens 0.8–0.9 rough, low spec (`set_colour(low_spec=True)`); root 0.9; rocks 0.85–0.9; no metal, no
  emission.

### 5.7 Re-measure (final renders against the sheet, same masks)
- **Green:** front median within 15 of `#5D961C`; v > .7 within 12 of `#A1D224`; tone shares 31 / 29 / 40 ± 8 (front)
  and 33 / 29 / 38 ± 8 (f34).
- **Rock:** front median within 12 of `#7F7C76`, v > .7 within 12 of `#D3C5AD`, R ≥ G ≥ B on the plain rocks.
- **Root** (front / f34 T with v ≥ .25): within 15 of `#684324` / `#6E4B17`; parts shot within 12 of `#744A29`.
- **Stalk** (f34 / side): within 15 of `#8E670F`.
- **Shares** per §2.6.

## 6. Joins and contact (no floating dressing, no buried dressing)

- **Shells:** each blade, stalk, petiole, skirt leaf, root, the hub, the peg, each rock and each sprig is its own closed
  shell, all in one hero object.
- **Frond chain:** blade → its stalk (the stalk's top end 0.06–0.12 inside the blade's rachis, the stalk axis within 0.03
  of the rachis line) → hub top (stalk foot 0.04–0.08 inside) → hub → ground. Forks: the minor stalk 0.04–0.06 inside the
  main stalk. **No frond floating**: report each blade's seat.
- **Skirt chain:** leaf → petiole (as above) → hub. Where a skirt leaf's tip rests on the ground (N1) or a rock (N2 on
  R1), it is within 0.03 and never below z 0 or more than 0.05 inside the rock.
- **No blade or leaf buried:** ≤ 0.12 of stalk inside a blade; no blade inside the hub beyond its stalk; nothing inside
  a rock (ray parity); no blade more than 25 % of its verts inside another blade.
- **Roots:** inner end ≥ 0.10 in the hub; cut end on the ground (z 0 … −0.03); no root more than 0.05 inside a rock.
- **Rocks:** sunk ≤ 0.03; may touch a root or a leaf (within 0.03), never cut one by more than 0.05.
- **Sprigs:** base at z 0 … −0.03, ≥ 0.05 clear of rocks.
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**. A shell floats if its nearest distance
  to every other shell and the ground is > 0.03, or it doesn't chain to the ground. Chains: blade → stalk → hub → ground;
  skirt leaf → petiole → hub; root → hub / ground; rock → ground; sprig → ground.
- **Count buried shells** (STAGES; 046, 047 round 2): **0 dressing shells more than 0.05 inside a rock or the hub**
  (stalk feet and root ends excepted at their stated depths). Use `m047._Solids` from the start (hub + every rock added as
  built; three skewed rays, two of three agree). A leaf or sprig that still cuts after its retries is moved outward along
  its azimuth.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.
- **Reports:** reuse `m047.shells_report`, `contact_report` and `bury_report` (committed; import, don't edit).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no particles, no spores, no wind marks. The cast shadow is the
render's.

- **Stage 5 (lighting): skip, and record why.** No emission, no lights. Studio notes (Requires Manual Validation):
  - the lime fronds and front skirt stay lime and the large fronds dark green under the game sun (not olive, not black);
  - the stalks stay ochre, the root orange-brown;
  - the rocks stay warm grey (sage on R5 / R6), never lavender.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** The old W06 `FernAndBroadleaf` had none either. A
  wind sway would be a Studio-side script, not a socket (decision §8.11).
- **Collision:** **hero `none`** (CanCollide, CanQuery and CanTouch off): walk-through undergrowth, as the old W06 hero.
  Parts: fronds, broad leaf and ground leaf `none`; RootCrown `hull`; Rock `hull` (usable as a scatter stone) (decision
  §8.8).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched every `art/roblox/kit/*/manifest.json` and `art/roblox/kit/wip/*/manifest.json`, the
builders and the repo text (`git grep`) for Fern, Frond, Broadleaf, RootCluster and the candidates:
- **W06:** `FernAndBroadleaf`, `…BroadLeaf`, `…BroadleafCluster`, `…FrondLarge`, `…FrondMedium`, `…FrondSmall`,
  `…RootCluster`, `…Spread`, `…Upright`. **W06 WIP:** `FernFrondLarge`, `FernFrondMedium`, `FernFrondSmall`,
  `FernRootCluster`, `SpreadFern`, `UprightFern`.
- **V03:** `BrackenFern`, `BrackenFernFrond`, `BrackenFullFern`, `StrapFern*`. **V10:** `GiantCoilFern*`. **Lobby:**
  `FernLeafy`, `BroadLeafHerb`, `BroadleafTree*`.
- So **no `Fern…` prefix** and **no part name containing `FernFrond…` or `FernRootCluster`** (a name like
  `BroadleafFernFrondLarge` would contain W06 WIP's `FernFrondLarge`; `BroadleafFernRootCluster` would contain
  `FernRootCluster`).
- **`BroadleafFern`, `LargeFrond`, `MediumFrond`, `SmallFrond`, `RootCrown`, `GroundLeaf`, `BroadleafFernBroadLeaf`,
  `FernRock` and `m060` occur nowhere** (repo text, manifests, builders; `m060` / `M060` match only binary blobs), and no
  owned name is a substring of the names below.

| Object | Part | Why |
| --- | --- | --- |
| `BroadleafFern` | hero: root crown, 6 fronds (8 blades), 8 skirt leaves, 7 rocks, 6 sprigs | the sheet's title; free |
| `BroadleafFernLargeFrond` | "Fern Frond (large)": F1 with its stalk | the label, reordered to avoid `FernFrondLarge` |
| `BroadleafFernMediumFrond` | "Fern Frond (medium)": F3 + F3b on one stalk | the label, reordered |
| `BroadleafFernSmallFrond` | "Fern Frond (small)": F5 with its stalk | the label, reordered |
| `BroadleafFernRootCrown` | "Root Cluster (base)": hub, peg, 7 roots | avoids `FernRootCluster`; the close-ups' crown |
| `BroadleafFernBroadLeaf` | "Broad Leaf (single)": one skirt leaf with its petiole (lobed, §3.5) | the label |
| `BroadleafFernRock` | "Rock (reusable)": R1 | the label |
| `BroadleafFernGroundLeaf` | "Ground Leaf (small, optional)": one sprig | the label |

- Palette keys `m060_*` (§5.4). Collection `Kit/M060 Broadleaf Fern`. No sockets (§7).

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **3.0 tall, 3.85 × 3.45 footprint** (recommended: 0.55 C, hip-high undergrowth; rocks 0.85 like
   059's, lobes 0.2–0.35 wide). Alternatives: 2.5 (WorldModeling's fern ceiling, 0.45 C) or 3.6 (waist-to-chest, rocks
   1.0).
2. **Names (§8):** **`BroadleafFern` and the seven parts above** (recommended). Not `FernAndBroadleaf*`, `Fern…`
   prefixes, `…FernFrond…` or `…FernRootCluster`.
3. **Frond counts (§2.3, §3.4, §3.8):** **6 stalks carrying 8 blades: 2 large tall (F1, F2), 2 medium pairs (F3 + F3b,
   F4 + F4b), 2 small (F5, F6); 5 lobes a side** (the large fronds' inner side 4) (recommended: every ortho view then
   shows two tall and two arching fronds, and the parts' pair is honoured). Alternative: 6 single blades without forks
   (the front loses the dark F3b).
4. **Skirt (§2.4):** **8 lobed broad leaves, 4 lobes a side, lime in front and dark behind, N1's tip on the ground**
   (recommended).
5. **Broad leaf and rocks (§3.5, §3.9):** **the skirt leaves lobed and the `…BroadLeaf` part one lobed skirt leaf**
   (recommended; alternative: the parts row's plain kite as the part). **Seven rocks: R1 large, R2 / R3 medium, R4 / R7
   small, R5 / R6 sage back rocks 0.8 / 1.0 tall** (recommended; alternative: all seven low, ≤ 0.55, as the side and rear
   draw).
6. **Root crown (§2.2, §3.6):** **a low faceted hub (0.45 tall, Ø 0.5–0.7) with a peg and 7 splayed roots with flat cut
   ends, visible between leaves and rocks (front T ≈ 4 %)** (recommended). Alternative: the parts row's tall stump with
   4–5 long legs.
7. **Ground (§3.13):** **no soil patch** (recommended), or a thin soil mound under the crown (+30 tris, a new key).
8. **Collision (§7):** **hero `none`; frond, broad-leaf and ground-leaf parts `none`; RootCrown and Rock `hull`**
   (recommended), or everything `none`.
9. **Comparison cameras (§3.2, §3.3):** **`front_sheet (0, 5)` governs positions, `f34_sheet (0, 20)` the read** (probe
   az −20 … +20, e 15–25); `rear_sheet (180, 5)`, `r34_sheet (180, 20)` (probe 160 … 200), `side_sheet (90, 5)`;
   `top_sheet (0, 60)` content only; extras: parts shot, exploded, `junction_cu`, `underside`, `thickness_cu`,
   `edge_side`, `thumb`, scale shot. Floor hidden in every `*_sheet` render.
10. **Sinking (origin):** **hub, roots, rocks and sprigs sink at most 0.03**, so the origin sits within 0.03 of the
    ground; record the origin's offset from the crown axis (≤ 0.15) (recommended).
11. **VFX (§7):** **none; stages 5 and 6 skipped and recorded** (recommended). A wind sway is a Studio-side script if
    gameplay wants it.
12. **Exported parts (§8):** **the hero plus the seven parts of the sheet's "PARTS (INDIVIDUAL)" row** (recommended), or
    the hero plus the three fronds and the root crown only (the rock duplicates kit stones).
13. **Colour (§5):** **large fronds dark `#3A7A2C`, arching / small fronds lime `#A8D722` over mid `#69A520`, skirt
    `#8CC82E` in front and dark behind, a deep base key; stalks ochre `#906F12`; root `#744A28`; rocks warm grey
    (median `#827D77`) with sage `#B8BA9B` stains on R5 / R6; front all-green median `#5D961C`, tone shares 31 / 29 / 40**
    (recommended).
14. **Budget (§4.3):** **full-asset class: hero ceiling 3800, planned about 2900–3300; each part under 1000**
    (recommended: the sheet's lobed fronds and skirt need it; the old W06 hero used 3549). Alternative: a lean 2000 (4
    lobes a side, 6 skirt leaves, 5 rocks) if the fern is to be scattered densely.

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **Flat cards (WorldModeling §6.1, §17.2 "leaves have side-visible volume"; close-up 3).**
   - Every blade a closed solid: 0.07 at the edges, a 0.14 rachis ridge, a 15–25° V-fold; ≥ 0.06 on screen in
     `edge_side`.
   - No blade within 12° of edge-on over more than 15 % of blade area in the front / f34 (roll, §2.3).
2. **Comb-like or spiky fronds (lobby `FernLeafy`; 047 r1 "spiky"; 054 r1 "pointed diamond shards").**
   - One solid lobed blade per frond: lobes **joined** to the blade, notches only 0.45–0.6 of the half-width deep, lobes
     0.18–0.35 wide with **blunt squarish ends**; only the frond tip is pointed (35–50°).
   - Never separate leaflet cards on a thin stick; never needle-thin lobes.
3. **Leaflets that vanish at game distance (WorldModeling §18 "tiny details vanish").** 5 lobes a side, not 8–12; in the
   `thumb` render (front ≈ 120 px tall) each upper frond still shows ≥ 3 notches a side.
4. **A flat star or an even rosette (W06's failure; WorldModeling §6.2, §18).** Two tall fronds standing apart above h .80
   (two runs at h .85 and .95), arching fronds reaching the far sides, a drooping skirt: a rounded crown 1.25–1.30 × as
   wide as tall, not a flat disc; uneven azimuths and lengths.
5. **Shields and pads (049 r1).** Fronds L : W 2.2–2.9 (large ≈ 2.4); the skirt leaves are the only broad ones (≈ 1.5).
6. **Floating fronds (STAGES; 035 / 036).** Every blade on its stalk, every stalk in the hub, every fork in its main stalk,
   every skirt leaf on its petiole, every root in the hub and on the ground; floating shells 0, counted and reported.
7. **Fronds buried in the crown or in rock (046; 047 r2).** Stalk feet 0.04–0.08 in the hub, stalk tops ≤ 0.12 in the
   blade; ray parity against the hub and rocks after the final placement: 0 shells more than 0.05 inside.
8. **Skirt leaves cutting into the ground.** No vertex below z −0.01 except the sunk bases; N1's tip rests within 0.03.
9. **A stump with leaves, or no root at all (WorldModeling §18; 059).** T 3–6 % in every side view, 60–90 % of it in the
   lowest fifth; the hub ≤ 0.45 tall; roots visible between leaves and rocks.
10. **Yellow / olive fronds (047 "plants too yellow"), weak contrast (W06), or one flat green.** `frond_mid` ≥ 86°,
    `frond_dark` ≥ 105°; the dark large fronds clearly darker than the lime fronds and front skirt; the front median
    within 15 of `#5D961C`; tone shares ±8.
11. **Colour by facing (042 ruling; 054 m9).** Tones by frond role and spine band; rocks by height and position; `K.check`
    facing correlation < 0.5 per material. The lit / shaded halves come from the V-fold and the light.
12. **Lavender, blue or tan rocks (M034, M037).** Plain rocks R ≥ G ≥ B, s ≤ 0.14; sage only on the stained regions;
    angular blocks with 9–12 broad facets and flat bases, never eggs.
13. **Winding (044) and bowties.** 0 faces wound against their neighbours per shell, especially on the hand-built lobe
    strips; lobe corners, notches and tips checked for bowties; corners ≥ 3°.
14. **Oversize.** 3.0 tall, not the old kit's 6.8; a scale shot with the 5.5-stud marker.
15. **Origin below the ground.** Sink nothing more than 0.03.
16. **Names and scope.**
    - No `FernAndBroadleaf*`, `Fern…`-prefixed, `…FernFrond…` or `…FernRootCluster` names.
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit the frozen shared helpers or other models' builders: import from the committed ones (`m047`, `m049`,
      `m053`, `m055`); copy from `m054` / `m056` / `m057` / `m058` / `m059` if they are still uncommitted.
    - Don't touch other models' collections.

## Decisions (main session, 2026-10-30)
All 14 recommendations are accepted. The open questions are ruled as follows:
1. **Size.** 3.0 tall with a 3.85 × 3.45 footprint (hip-high).
2. **Names.** As in §8: hero `BroadleafFern`, parts `BroadleafFernLargeFrond`, `…MediumFrond`, `…SmallFrond`, `…RootCrown`, `…BroadLeaf`, `…Rock` and `…GroundLeaf`, with keys `m060_*` and collection `Kit/M060 Broadleaf Fern`. Never `FernFrond*`, `FernRoot*` or `FernLeafy`.
3. **Fronds.** Six stalks and eight blades, as recommended.
   - Blades are blunt-lobed with real thickness, a rachis ridge and a V-fold.
   - **No comb or spike look, no flat star of wide leaves, no flat cards.**
   - Each frond must read from every view, not just the front.
4. **Skirt.** Eight lobed broad leaves.
5. **Broad leaf part.** Lobed, to match the assembled leaves; the kite in the parts row is a simplification. Seven rocks, with the back pair 0.8 and 1.0 tall and stained sage.
6. **Root crown.** A low hub with seven roots with cut ends, as the close-ups draw it; the close-ups govern over the parts row.
7. **Ground.** No soil patch.
8. **Collision.** As recommended: hero `none`, fronds, leaves and sprigs `none`, RootCrown and Rock `hull`.
9. **Cameras.** As recommended; the top is judged for content only.
10. **Sinking.** At most 0.03. **No floating or buried pieces:** every frond and leaf attaches to the root crown or the ground.
11. **VFX.** None; stages 5 and 6 skipped and recorded.
12. **Exports.** The hero plus seven parts.
13. **Colour.**
    - Colour by frond role and position along the frond, **never by facing**.
    - Keep strong contrast between the dark fern green and the lime, which W06 lacked.
    - Rocks are warm grey, never lavender; the sage is a stain on the back rocks only.
14. **Budget.** Full-asset class: ceiling 3800, plan 2900–3300, every part under 1000.

## Stage 1 — Modelling (modeller, 2026-10-31)
Builder `art/blender/kit/mcp/m060.py` → `build()`, built in the background Blender on port 9881 (`wip/M060.blend`, saved).
- **Construction.** Each frond and skirt leaf is **two closed shells**:
  1. A lobed blade: a 2D outline (u along the spine, v across, in studs), triangulated as fans from the rachis stations
     (one per lobe hub), mapped onto an arched cubic spine with roll, a V-fold and thickness, with rim walls all round.
  2. A 4-sided diamond tube. It is the stalk below the blade and continues **inside the blade as the raised rachis**: it
     pokes out 0.036 → 0.018 above and 0.03 → 0.012 below the blade surfaces and ends in a point at 0.93 L. The tube's
     joint ring bisects the kink between stalk and blade.
- **Lobes.** Blunt tongues with two outer corners (the leading one chamfered to 0.94), leaning toward the tip (30° on
  fronds, 26° on leaves).
  - **U-slots with two verts** separate them (bottom 0.28 of the lobe pitch).
  - Notches reach 0.62–0.66 of the half-width on fronds and 0.57–0.59 on leaves.
  - Single-vertex notches were tried first and always read as a sawtooth (one vertical side, one slanted). The spec
    allows "one or two verts", so two were used.
- **Fronds (6 stalks, 8 blades).** F1 / F2 tall (5 outer + 4 inner lobes, inner side 0.8 wide), F3 / F4 arching lime,
  F3b / F4b dark forks seated 0.6 up their parent stalk, F5 / F6 small lime.
  - Foot, base, tip and apex come from §2.3. An apex search fits the spine to apex − 0.10, so the blade top lands on
    the table.
  - Measured: L 1.45–2.36, L : W 2.1–3.1, tip angle 56–80°.
  - Apexes: F1 2.93, F2 2.80, F3b 2.15, F4 2.10, F3 2.04, F6 1.81, F4b 1.77, F5 1.54. Tips land exactly on the table.
- **Skirt (9 lobed broad leaves).** A petiole leaves the hub rim (r 0.18, z 0.38) rising 62° for 0.58. The blade leaves
  it already heading 38° down and droops to 62° at the tip. The result is a dome, so the leaves hang outward and face
  every view, as in the sheet's front, side and rear.
  - L 1.18–1.58, L : W 1.18–1.21, 4 lobes a side.
  - **N9 (az 0°) was added** to fill the right side of the skirt (see deviations).
  - Tips were pulled in from §2.4 to r 1.5 (front and back) and 1.85 (sides), so the leaves hang steeply instead of
    lying flat.
- **Root crown.** An 8-sided hub (Ø 0.70 → 0.44, top 0.45, chamfered top ring) and a 6-sided peg to 0.58.
  - 7 five-sided roots, two segments each with a knee at 60 % and a flat cut end on the ground.
  - Roots at 15 / 65 / 120 / 170 / 215 / 268 / 320°, reaching r 0.70–0.85.
- **Rocks (7).** Ring-stack hulls (`m033._ring_pts` / `_hull`), 30–34 tris each.
  - R1–R4 and R7 are low (0.31–0.48 tall).
  - R5 / R6 are tall and pointed, 0.80 / 1.00 (decision 5).
- **Sprigs (6).** 2–3 thick gem leaves of 10 tris each, on the ground.
- **Parts.** Each is built by the same functions as the hero: LargeFrond = F1, MediumFrond = F3 + F3b, SmallFrond = F5,
  RootCrown, BroadLeaf = N1, Rock = R1, GroundLeaf = S1 (3 gems).
- **Reading from all eight azimuths.**
  - Rolls were set by a greedy search over the ray-grid measure (`vis_bm`), with a V-fold of 12.5° a half and a 6°
    lobe wave (alternate tongues lifted or dropped).
  - Spin sheet `M060_spin.png`: two tall fronds stand apart and the blades show their lobes from every azimuth. No view
    reads as a ball with flaps.

## Stage 2 — Optimisation and cleanup
- **Budget.** Hero **3764 tris** (ceiling 3800): 17 blade shells 2660, 17 tubes of about 30 each (502), crown 262,
  rocks 210, sprigs 130. Parts 30–428.
  - The two-vert slots and N9 were paid for by trimming tube stations (frond blade stations 3 → 2, leaf stations to 1)
    and cutting sprigs to 2 gems (S1 keeps 3).
- **Topology.** Every shell is closed. All 8 objects have 0 non-manifold edges and verts (bowties), and 0 boundary,
  wire or loose elements, zero-area faces, n-gons and duplicate verts.
  - **0 winding errors** in every shell, and normals point outward.
  - 0 self-intersections per shell. A sweep cap and a fan-validity clamp in `_side_outline` stopped the leaves' fans
    folding over a slot.
  - Smallest corner 3.2°.
- **Origin.** At the bbox bottom centre, with transforms applied. The hero's origin is offset (0.009, 0.057) from the
  crown axis; sink −0.02.

## Stage 3 — UV
`M.smart_uv(angle 45, ANGLE_BASED, margin 0.008)` followed by `m012._uv_unfold`:
- 0 overlaps, 0 flipped faces, minimum gap 0.016, border 0.008.
- Density 1.0 / 1.0 / 1.0; conformal stretch p95 1.008 on the hero (≤ 1.038 on the parts).
- 1337 islands on the hero, one per flat facet group. The exporter writes its own palette UVs.

## Stage 4 — Materials, colour, texture
- **Calibration.** `m060.calibrate()` ran on the kit dome for 6 iterations against the §5.4 targets, with three
  changed targets:
  - FRESH aimed at `#92CC28` (81°), so the lime skirt reads as the sheet's light tone.
  - DARK `#33702A` and DEEP `#244E1B`.
  - ROCK `#928E89`.
- **Adjustments after calibration.**
  - The dome renders brighter than the self-shaded fern (the warning in §5.4), so the greens were moved ⅔ of the way
    back toward the uncalibrated keys until the hero's own front render matched the sheet.
  - ROCK calibrated to `#737375` (B > R), so it was replaced by the warm `#888582`.
  - SAGE did not converge with the stone mask, so it was set by hand.
- **Final palette.** Greens: rough 0.8–0.9, low spec. Root and rock: rough 0.85–0.95.

| Key | Hex |
| --- | --- |
| frond_light | `#9ECA22` |
| leaf_fresh | `#84BB2B` |
| frond_mid | `#5E9221` |
| frond_dark | `#346D2B` |
| green_deep | `#244C1C` |
| stalk | `#735B00` |
| root | `#7A4D27` |
| root_light | `#96693C` |
| root_deep | `#472A10` |
| rock | `#888582` |
| rock_deep | `#6E6B68` |
| rock_sage | `#858C74` |

- **Painting (never by facing).**
  - Blades are painted per lobe band along their length, from a ramp on the ladder deep → dark → mid → fresh → light:

    | Blade | Ramp |
    | --- | --- |
    | F1 | deep → dark → 1.5 |
    | F2 | deep → dark → mid → 2.75 |
    | Lime fronds | mid → light |
    | Forks | deep → dark → mid tip |
    | Front skirt N1 / N2 | mid → light |
    | N3 | mid → fresh-light |
    | N4 / N6 | dark |
    | N5 / N8 / N9 | dark → mid or fresh |
    | N7 | lime, as the sheet's rear centre leaf |

  - Each rachis tube is one step darker than its band. Stalks run root → ochre → blade base.
  - The crown is painted by member: the top ring, peg top and cut ends take root_light; the lowest band takes a
    root_deep mix.
  - Rocks get deep stone in noise patches. R5 / R6 are sage on the upper half and on R6's −X side; R1 / R7 have a sage
    band at the top back.
  - Tint: ±0.04 per blade plus ±0.02 per band, ±0.03 on tubes and crown, ±0.04 per rock facet.
  - `K.check` baked shading is 0.27 on the hero. A height foot band on the rocks gave 0.56, so it was replaced by noise
    patches.
- **Re-measured** (final renders against the sheet, same masks):

| View | W : H | fill | G / T / R % | tones l / m / d | green median | light | mid | rock median / lit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| front sheet | 1.283 | .626 | 81.5 / 3.8 / 8.9 | 31 / 29 / 40 | `#5D961C` | `#A8D722` | `#69A520` | `#7F7C76` / `#C0BDA8` |
| front ours | 1.185 | .527 | 82.6 / 3.4 / 14.0 | 23 / 36 / 41 | `#5B891E` | `#A9DE23` | `#6C9B24` | `#7D786F` / `#B9B0A3` |
| f34 sheet | 1.353 | .588 | 80.0 / 4.6 / 10.7 | 33 / 29 / 38 | `#61991C` | `#A9D51F` | `#68A120` | |
| f34 ours (0, 20) | 1.040 | .487 | 85.8 / 2.4 / 11.8 | 26 / 39 / 35 | `#659920` | `#AADF23` | `#6CA026` | `#938D80` |
| side sheet | 1.163 | .563 | 84.6 / 4.8 / 6.4 | 38 / 34 / 28 | `#6A9F0F` | | | |
| side ours | 1.040 | .526 | 79.3 / 4.6 / 16.2 | 25 / 38 / 37 | `#59871C` | | | |
| rear sheet | 1.327 | .642 | 82.3 / 4.1 / 8.5 | 28 / 28 / 44 | | | | |
| rear ours | 1.170 | .534 | 75.3 / 5.6 / 19.1 | 14 / 40 / 47 | | | | |

- **Front details.**
  - The tall fronds give two separate runs at h .85 and .95.
  - Dark median `#2D5F16` vs `#1B5116`: the sheet's dark tone is mostly cast shade.
  - Root median in shade `#49341C` vs `#684324`: darker, because the hub sits under the skirt.

## Stage 5 — Lighting
Skipped: the sheet shows no emission or light. Studio notes (Requires Manual Validation):
- The lime fronds and front skirt must stay lime, and F1 / F2 dark green, under the game sun.
- The stalks stay ochre and the root orange-brown.
- The rocks stay warm grey, with sage only on R5 / R6 and the tops of R1 / R7.

## Stage 6 — VFX
Skipped: the sheet shows no effect (decision 11), and no object has sockets. Collision: hero, fronds, leaf and ground
leaf `none`; RootCrown and Rock `hull`.

## Modeller's notes for the verifier
- **Checks (the `build()` result).**
  - Contact: 62 shells, **0 floating, 0 unchained**.
  - Bury: 0 shells over 0.05. The maximum is 0.029, where N8 lies over R6 and N6 over R5; the guard lifted N8's tip
    0.30 and N6's 0.06.
  - No rock goes into the crown or another rock.
  - Tube feet sit 0.049–0.066 in the hub; the forks seat in their parent tube.
  - No blade has more than 11 % of its verts inside another (the N9 / N3 overlap at the right).
  - The problems list holds only the two eight-azimuth items below.
- **Eight azimuths.** Ray grid 0.025, facet normals. Each cell is the % of visible foliage within 20° / 12° of edge-on:

  | Azimuth | 0° | 45° | 90° | 135° | 180° | 225° | 270° | 315° |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | el 5 | 8.5 / 3.3 | 9.7 / 2.4 | 9.6 / 3.3 | **10.9** / 4.4 | 8.6 / 3.0 | **10.4** / 3.3 | 9.2 / 3.2 | 8.8 / 3.2 |

  - At el 20 every azimuth is 8.1–13.9 / 2.3–3.7.
  - Bare core (tubes + crown): 7.6–13.3 % of foliage + core.
- **Deviations from the Decisions and spec, with reasons.**
  1. **9 skirt leaves, not 8** (N9 at 0°). The right side of the front view was open; the leaf was paid for by the tube
     and sprig trims.
  2. **Skirt leaves L : W ≈ 1.2** (spec 1.5), with tips at r 1.5–1.85 (spec up to 2.0). The sheet's front, side and rear
     leaves are broad and hang steeply. With the spec's tips they lay flat and read as shelves and edge-on cards.
     - Leaf tip angle is 82° (spec 45–60°); frond tip angles are 56–80° (spec 35–50°).
  3. **Notches 0.57–0.66 deep** (spec 0.40–0.60), with two-vert U-slots. Shallower notches vanished in the renders.
  4. **The rachis is the stalk tube continued through the blade.** The spec asks for a ridge in the blade mesh and a
     stalk ending 0.06–0.12 inside it. The tube is cheaper and gives the ridge, keel and stalk one continuous line.
  5. **N7 is painted lime** (spec: dark). The sheet's rear view has a lime leaf front-centre, pointing down.
  6. **Rocks.**
     - No height foot band: it gave a facing correlation of 0.56.
     - R5 / R6 footprints narrowed to 0.56 × 0.50 / 0.62 × 0.54. Their heights stay 0.80 / 1.00; they sit at
       (−1.15, 0.78) / (1.08, 0.88).
     - The low rocks are about 8 % smaller and pulled in.
  7. **Sprigs** sit at 0.85 × the spec radii. S2–S6 have two gems; S1 has three.
- **Leftovers.**
  - Front fill 0.53 vs 0.63.
  - Front W : H 1.185 is inside the 1.18–1.32 band, at its low end; side W : H 1.04 vs 1.15.
  - The rock share is too high outside the front: the tall R5 / R6 stand clear of the skirt from the rear and sides
    (the conflict in spec §3.9; the decision keeps their heights).

    | View | Ours | Sheet |
    | --- | --- | --- |
    | Front | 14.0 % | 8.9 % |
    | Side | 16.2 % | 6.4 % |
    | Rear | 19.1 % | 8.5 % |

  - Edge-on at el 5 is just over 10 % at 135° (10.9) and 225° (10.4).
  - f34 tones are 26 / 39 / 35, with mid 10 points above the sheet's 29.
  - `thickness_cu` is a near edge-on view of the LargeFrond part.
  - `junction_cu` mostly shows leaf bases and rocks, because the hub sits under the skirt.

## Stage 7 verification (round 1)
Fresh verifier, 2026-10-31. Read-only, in a background Blender on port 9881 on `wip/M060_verify.blend` (not saved). My
renders and side-by-side comparisons are in `renders/models/M060/verify/`: `cmp_0..2.png` (sheet cell next to ours),
`spin_row0/1.png`, and `big_*.png` at 900 × 700. The scripts are in the scratchpad `m060_verify/`: `audit.py`,
`contact.py`, `uvov.py`, `vis.py`, `meas.py`; `meas.py` uses the study's `measure.py` masks.

**Verdict: FAIL, 5/10.** The model is technically clean and the front reads as a lobed fern. From the back half,
though, it does not read like the sheet.

### Technical re-measure (all pass)
- **Tris.** Hero 3764 (ceiling 3800). Parts: Large 210, Medium 428, Small 214, RootCrown 262, BroadLeaf 162, Rock 30,
  GroundLeaf 30.
- **Size.** Hero 3.711 × 3.356 × 2.946, inside 3.85 ± 0.2 / 3.45 ± 0.2 / 3.0 ± 0.1.
- **Origin and transforms.** On all 8 objects the origin is at the bbox bottom centre (0, 0, 0). Rotation 0, scale 1,
  delta transforms identity, no modifiers. No custom normals, all faces flat. The hero is offset (0.009, 0.048) from
  the crown axis (limit 0.15); it sinks 0.02.
- **Topology.** On every object, 0 for each of:
  - non-manifold, boundary and wire edges;
  - loose verts and duplicate verts;
  - zero-area faces and n-gons (everything is triangulated);
  - bowtie verts and winding errors;
  - shells with negative volume;
  - self-intersections within a shell.
  - The hero has 63 shells: 17 blades, 17 tubes, 9 crown pieces, 7 rocks and 13 sprig gems.
  - The smallest corner is 2.92° on the hero (spec ≥ 3°; the builder's thin check uses 2°). Numeric only.
- **Contact.** My own BVH pass, tolerance 0.03, chained to the ground:
  - 0 floating and 0 unchained shells. Every blade touches its own tube, and every tube touches the hub; the forks
    F3b / F4b seat in their parent tubes.
  - Tube feet sit 0.052–0.078 inside the hub.
  - Buried: only N8 in R6, 0.029 deep (limit 0.05). Nothing is below z −0.025.
- **UV.** Rasterised at 1024²: 0 overlapping cells and 0 flipped faces. Texel density p5 / p95 is within ±1.4 % on
  every object; the islands sit inside 0.008–0.992.
- **Colour assignment (code read).**
  - Blades are painted per lobe band along u, by role.
  - Tubes are painted per segment, rocks by noise field plus height and position, and the crown by member and height
    band. The hub top ring and the root cut ends take root_light, as §5.3 asks.
  - Nothing is chosen by face normal. `kit_baked_shading` is 0.27 on the hero and 0.31 on RootCrown (under 0.5).
- **Eight azimuths.** My ray grid (0.025, facet normals) shows edge-on (within 20°) at el 5:

  | Azimuth | 0° | 45° | 90° | 135° | 180° | 225° | 270° | 315° |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | Edge-on % | 8.5 | 9.7 | 9.7 | 11.0 | 8.6 | 10.5 | 9.1 | 8.8 |

  - At el 20 the range is 8.2–13.8 %, with az0 the highest.
  - By eye at 900 px:
    - az135: N7 / N8 show partly edge-on.
    - az225: several lobe tongues of F3 / F3b show as thin fins, and N6 / N4 as stacked shelves.
    - These are sliver tongues, not whole flat-card flaps. **Minor; acceptable.**

### Blockers
1. **The tall rocks are the reverse of §3.9.** The spec has R5 / R6 mostly behind the back skirt, peeking 0.10–0.25
   above it in the front and f34. Instead:
   - **In the front and f34 they do not show.** No sage peak is visible; the f34 has none of the sheet's two tall sage
     rocks.
   - **From the right side, the rear and the back diagonals they stand fully bare.** They read as two grey obelisks
     beside the plant. The narrowed footprints (0.56 × 0.50 and 0.62 × 0.54 for 0.8 / 1.0 tall) make them spires, not
     the sheet's broad pyramid blocks.
   - Ray-grid hits on R5 / R6 are 138 / 252 at az0 and **461 / 692 at az180**.
   - Rock share of the silhouette:

     | View | Ours | Sheet (tolerance ±3) |
     | --- | --- | --- |
     | Front | 14.6 % | 8.9 % |
     | Side | 16.6 % | 6.4 % |
     | Rear | 20.6 % | 8.5 % |
     | r34 | 17.8 % | 8.3 % |
     | az135 | 24.0 % | — |
     | az225 | 22.3 % | — |

   - The rock share is out of tolerance in every view, the front included.
2. **The rear half has a bare root star and a thin back skirt.** In the rear, r34, az135 and az225 the seven roots
   splay over open ground like the parts-row stump (`big_rear.png`). The back skirt leaves hang steeply beside the
   crown and don't cover the base. The sheet's rear and r34 show a full skirt of big lobed leaves down to the ground,
   with the brown crown seen under them and only low rocks.
   - Silhouette, ours against the sheet:

     | View | Fill | W : H | Sheet fill | Sheet W : H |
     | --- | --- | --- | --- | --- |
     | Front | 0.552 | 1.172 | 0.649 | 1.251 |
     | f34 (0, 20) | 0.507 | 1.019 | 0.621 | 1.305 |
     | Rear | 0.557 | 1.152 | 0.642 | 1.327 |
     | r34 (180, 20) | 0.506 | 1.010 | 0.638 | 1.367 |

   - Every fill is outside ±0.05. Every W : H is outside its band (front 1.18–1.32, f34 1.24–1.37, rear and r34
     1.26–1.40).
   - The plant reads as a sparse fan on rocks, not the sheet's lush rounded mound.

### Minors (visible unless marked numeric)
- **Lobe shape.** Lobes are straight-cut rectangular tongues swept toward the tip with square U-slots, so the tall
  fronds read as a stepped ratchet or staircase edge. The sheet's lobes are rounded scallops with rounded notches.
  - They still read as one solid lobed blade with thickness, a rachis ridge and a V-fold (`cmp_0`, `big_front`), not
    a comb or spikes.
  - Fix: round the tongue ends (chamfer both outer corners, or add a mid vertex), and use less sweep.
- **Leaf tones.** Light / mid / dark shares (sheet in brackets; tolerance ±8):

  | View | Ours | Sheet |
  | --- | --- | --- |
  | Front | 23 / 37 / 39 | 31 / 29 / 40 |
  | f34 | 27 / 40 / 33 | 33 / 29 / 38 |
  | Rear | 14 / 41 / 45 | 28 / 28 / 44 |

  - The front sits on the edge of tolerance. The f34 mid (+11) and the rear light (−14) and mid (+13) are out.
- **Root in the front reads near black** (T, v ≥ .25): front `#4A341C`, f34 `#523A1C`, sheet `#684324` / `#6E4B17`.
  The rear is right (`#6D4529`).
- **Greens are in range, not olive.**
  - Front all-green `#608D21` vs `#5D961C`; v > .7 `#A3D62C` vs `#A1D224`.
  - Light `#AADC27` (76°), mid `#6D9C28` (84°, 2° under the §5.4 floor of 86°), dark `#2E5F1A` (103°, floor 105°).
    Numeric only.
  - The dark-vs-lime contrast is strong: F1 is dark, the arching fronds and front skirt are lime.
- **Rocks are warm grey, never lavender.**
  - Front median `#878076` vs `#7F7C76`; rear v > .7 `#D3CBBB`; R ≥ G ≥ B everywhere.
  - The sage `#858C74` sits on the R5 / R6 upper halves and reads only faintly.
- **Parts against their cells.**
  - RootCrown matches the parts-row stump with splayed legs. Large frond, BroadLeaf (lobed, decision 5) and Rock
    (W : H 1.35 vs 1.4) are fine.
  - MediumFrond: lime main blade with a dark fork; the sheet's pair is all mid green. It follows the hero roles;
    minor.
  - The SmallFrond part shot at (0, 15) sees F5 end-on and reads as a flat folded panel. That is presentation, not the
    mesh.
  - GroundLeaf is three pointed gem pyramids; the sheet draws three small rounded leaves. Tiny, minor.

### The modeller's deviations
1. **9 skirt leaves, not 8.** Numeric only; accepted.
2. **Broader, steeper skirt leaves with blunter tips.** Visible. They look fine in the front, but the steep hang is
   part of Blocker 2 (base uncovered, narrow silhouette at the back). Spread the back leaves outward and lower.
3. **Deeper two-vertex notches (0.57–0.66).** The depth is close to the sheet's. The square slot and straight tongue
   give the ratchet look; minor, visible.
4. **Rachis as the stalk tube.** The ridge and keel read correctly; numeric deviation only. Accepted.
5. **Lime N7.** Visible and correct: it matches the sheet's rear front-centre lime leaf. Accepted.
6. **Rock changes.**
   - No foot band: invisible, accepted.
   - R5 / R6 narrowed: visible, part of Blocker 1.
   - Smaller low rocks: fine.
7. **Sprigs pulled in.** Numeric; fine.
8. **Front fill 0.53 (I measure 0.552) vs 0.63–0.65.** Visible, out of tolerance; Blocker 2.
9. **Side W : H 1.04 vs 1.15.** Out of the 1.08–1.22 band; mostly numeric, and it follows from Blocker 2.
10. **Too much rock outside the front.** Visible; Blocker 1. The front is also out (14.6 vs 8.9).
11. **f34 mid tone high.** Out of tolerance (+11), and the rear more so; minor, visible as a less lime-lit read.
12. **Dark root in front.** Visible minor (above).

### For the fix modeller (targeted)
- **Tall rocks.** Pull R5 / R6 in under the back skirt, or widen the back skirt leaves and lay them flatter so they
  drape over the rocks. Restore broader footprints (about 0.70 × 0.60 / 0.80 × 0.65) so they read as pyramid blocks.
  Aim for rock ≤ 12 % in the side and rear, and for the peaks to show 0.1–0.25 above the skirt in the front and f34.
- **Back skirt and roots.** Give the back and side skirt leaves (N4–N9) more outward spread and lower tips so they
  cover the root arms. Fill the rear at h < 0.4 so that rear and r34 fill reach ≥ 0.60 and W : H ≥ 1.25.
- **Lobe ends.** Round the lobe ends (secondary).
- **Re-check after the fix.** Bury (N8 / N6 over R5 / R6), rock share and the eight azimuths.

## Fix round 1 (fix modeller, 2026-10-31)
A fresh modeller, in the background Blender on port 9881 (`wip/M060.blend`, saved). It edited only `m060.py`; the
shared helpers are untouched. The scripts are in the scratchpad `m060_fix/`: `meas.py` uses the study's masks and the
verifier's cameras; `search*.py` / `rolls*.py` are parameter searches over the ray grid. Renders of this round:
`renders/models/M060/fix1/` (`cmp_all.png` puts each sheet cell beside ours; `big_*.png` at 900 × 700). `build()`
rewrote the usual `M060/` renders.

### What changed
1. **Back and side skirt as a lush mound (blocker 2).**
   - Leaves now spread around the crown more evenly: N9 18°, N8 52°, N7 95°, N6 128°, N4 176° (front N5 214°, N2 245°,
     N1 288°, N3 332°). Before, the back half had only three leaves.
   - **N4 and N6–N9 are "curtain" leaves.** Each is W 1.40, with a longer and steeper petiole (N6 0.64 / 66°, N8 0.70 /
     68°, N4 / N9 0.72 / 68°). The blade leaves it nearly level (lean 4–12°), arches out and drops (droop 70°, fuller
     Bezier handles 0.48 / 0.34) to a tip on the ground at r 1.7–2.0.
   - `CURTAIN_ENV` keeps them broad down to the ground: 0.92 at 0.66 L and 0.58 at 0.82 L, so no triangular gaps open
     between neighbouring tips.
   - **Curtain leaves have 3 bigger lobes a side** (depth 0.30) instead of 4. On these big leaves the 4 small scallops
     vanished against the same-coloured leaves behind. This saves 180 tris.
   - The front leaves (N1, N3, N5) also reach lower and further out, with tips at z 0.04–0.06.
   - New per-leaf keys in `LEAVES`: `pet`, `rise`, `lean`, `droop`, `hk`, `curtain`.
   - The root arms now sit under the skirt. One long back root (80°, r 1.30) and R7 at the skirt edge (0.45, 1.46),
     0.60 × 0.50 × 0.38, show at the rear foot, as the sheet's rear does.
2. **Tall rocks (blocker 1).**
   - R5 is 0.70 × 0.60 × 0.80 and R6 0.80 × 0.65 × 1.00 (decision heights). They are broad pyramid blocks.
   - They sit at az 130° / 50°, r 0.90, i.e. (−0.58, 0.69) / (0.58, 0.69), right under the raised arches of N6 / N8.
     No leaf is lifted and nothing is buried.
   - The curtains of N9 / N8 / N7 / N6 / N4 cover them from the side, rear and diagonals. Roots were re-routed out of
     their sectors: 0 / 80 / 170 / 208 / 248 / 288 / 326°.
   - A search over position (az 35–75°, r 0.7–1.35), height (×0.8–1.25), leaf azimuths and widths picked this layout:
     its worst R5 + R6 share over the seven non-front views is the lowest.
3. **Scalloped lobes (ruling).**
   - Each lobe is now two shoulder verts (±0.35 of the pitch, at 0.84 of the envelope) plus a crown vert on the
     envelope, and one V-notch vert sits between lobes.
   - Before, each lobe was a two-vert U-slot plus a straight two-corner tongue: the square ratchet.
   - The first lobe rises from the base vert, so the vert and tri counts per blade are unchanged.
   - Sweep is lower: 16° on fronds, 14° on leaves (was 30 / 26). Notch depth: fronds 0.64, leaves 0.66, curtain leaves
     0.70 of the half-width.
4. **Front root colour (ruling).** In the hero only, the root arms (root_light, then a 75 % mix) and the hub's two
   lower bands (a 50 % root / root_light mix, then root_light) are one step lighter. This is by member and height band,
   never by facing. The RootCrown part keeps the parts-row brown.
5. **GroundLeaf: rounded leaves (ruling).** `_pad`: a domed hexagonal pad, cupped at the side corners, lying 16–21° off
   the ground. It is 12 tris (was a 10-tri pointed gem). The hero's 13 pads cost +26 tris.
6. **MediumFrond part coloured as its cell (ruling).** `MEDIUM_PART_TONE` (mid green, fresh tips) on both blades of the
   part only. The hero's F3 / F3b keep their roles.
7. **Rear tones.** N7 now runs to light at its tip (the sheet's lime rear centre leaf). N8, N9 and N3 tips are one step
   lighter.
8. **Eight azimuths.** Two greedy roll passes on the ray grid set these rolls:

   | Blade | Roll |
   | --- | --- |
   | N3 | −56 |
   | N4 | 10 |
   | N5 | 13 |
   | N6 | 10 |
   | N8 | −7 |
   | N9 | 33 |
   | F1 | (33, 18) |
   | F3 | 27 |
   | F4b | −33 |
   | F5 | −58 |

   F3 / F4 tips moved to (−1.96, 0.45, 1.80) / (1.99, −0.50, 1.95), and the F2 apex to 2.86 (spec 2.86), to widen the
   rear.

### Before → after
Before = stage-7 round 1 (verifier). After = this build, measured the same way: verifier cameras, study masks, floor
hidden.

| Check | Before | After | Target |
| --- | --- | --- | --- |
| Rock share, front | 14.6 % | **10.9** | 8.9 ± 3 |
| Rock, side (right) | 16.6 | **8.2** | 6.4 ± 3 |
| Rock, rear | 20.6 | **9.0** | 8.5 ± 3 |
| Rock, r34 | 17.8 | **5.8** | 8.3 ± 3 |
| Rock, az135 / az225 | 24.0 / 22.3 | **9.8 / 8.0** | ≤ ~12 |
| Rock, side (left) / az045 / az315 | 15.9 / — / — | 10.3 / 12.3 / 13.7 | (no sheet cell) |
| R5 + R6 ray-grid share, az0 / 90 / 135 / 180 / 225 / 270 | — | 1.5 / 2.2 / 4.7 / 5.1 / 2.1 / 5.0 % | |
| Fill, front / f34 | 0.552 / 0.507 | **0.577 / 0.520** | 0.649 / 0.621 (toward) |
| Fill, rear / r34 | 0.557 / 0.506 | **0.584 / 0.564** | ≥ 0.60 |
| W : H, front / f34 | 1.172 / 1.019 | **1.276 / 1.096** | 1.18–1.32 / toward 1.305 |
| W : H, rear / r34 | 1.152 / 1.010 | **1.256 / 1.062** | ≥ 1.25 |
| W : H, side | 1.038 | **1.096** | 1.08–1.22 |
| Rear root (T) / r34 T | 5.4 / 4.4 (bare star) | 0.9 / 0.4 | 4.1 / 5.8 |
| Front T | 3.3 | 3.1 | 3.8 ± 1.5 |
| Root colour, front T (v ≥ .25) | `#4A341C` | `#52371D` | `#684324` |
| Tones front / f34 / rear / r34 (l / m / d) | 23/37/39, 27/40/33, 14/41/45, 15/40/45 | **27/36/37, 29/41/30, 22/36/42, 24/34/42** | 31/29/40, 33/29/38, 28/28/44, 37/26/37 |
| Front green / light / mid | `#608D21` / `#AADC27` / `#6D9C28` | `#63941E` / `#A5D422` / `#6D9D20` | `#5D961C` / `#A8D722` / `#69A520` |
| Front rock median | `#878076` | `#7F7B70` | `#7F7C76` |
| Edge-on (20°) at el 5, az 0 … 315 | 8.5 / 9.7 / 9.7 / 11.0 / 8.6 / 10.5 / 9.1 / 8.8 | **8.5 / 8.8 / 7.8 / 9.8 / 5.2 / 8.5 / 8.3 / 8.5** | ≤ 10 |
| Edge-on (20°) at el 20 | 8.2–13.8 | 6.5–11.9 | |
| Bare core (tubes + crown) | 7.6–13.3 % | 4.9–10.7 % | ≤ 15–30 |
| Hero tris | 3764 | **3610** | ≤ 3800 |
| Parts (Large / Medium / Small / Root / BroadLeaf / Rock / GroundLeaf) | 210 / 428 / 214 / 262 / 162 / 30 / 30 | 210 / 428 / 214 / 262 / 162 / 30 / **36** | < 1000 |
| Hero size | 3.71 × 3.36 × 2.95 | **4.04 × 3.58 × 2.94** | 3.85 ± 0.2 × 3.45 ± 0.2 × 3.0 ± 0.1 |
| Floating / unchained shells | 0 / 0 | 0 / 0 (all 8 objects) | 0 |
| Buried > 0.05 | 0 (max 0.029) | 0 (max 0.020; rocks into root1 0.021) | 0 |
| Leaves lifted by the rock guard | N8 0.30, N6 0.06 | none | |
| Blade verts inside another blade | ≤ 0.11 | ≤ 0.07 | ≤ 0.25 |
| Non-manifold / bowtie / winding / self-intersections | 0 | 0 on every object and shell | 0 |
| Smallest corner | 2.92° | 2.75° (builder's thin check: 2°) | ≥ 3° (numeric) |
| UV | 0 overlaps / flips | 0 / 0, gap 0.016, border 0.008, p95 1.012 | |
| Origin | bbox bottom centre, offset (0.009, 0.048) | bottom centre, offset (−0.015, 0.150), sink −0.02 | ≤ 0.15 |
| `kit_baked_shading` hero / RootCrown | 0.27 / 0.31 | 0.00 / 0.29 | < 0.5 |

### Leftovers and deviations
- **Tall-rock peaks in the front and f34: not met.**
  - R5 + R6 are 1.5 % of the front ray grid and 0.6 % at el 20. They read as small grey bits between leaves, not as
    the sheet's peaks.
  - The skirt that now hides them from the side and rear also hides them from the front, because they sit under the
    back arches. This is the §3.9 conflict: the sheet's front / f34 show tall peaks, its side / rear show only low
    rocks.
  - **Tried and dropped:**
    - Raising them to 0.92 / 1.15 and 1.0 / 1.25 under raised N6 / N8: the front stayed at 1.6 %, N7 / N8 were lifted
      0.18–0.42 and the rear rose to 10.6–12.9 %.
    - Moving them to the back corners (az 40° / 140°, r 1.1): 3.2 % in the front, but still no readable peak, and the
      front rock share rose to 12.6.
    - Lowering the front petioles (0.58 → 0.38): no gain.
- **Rear / r34 fill 0.584 / 0.564** (target ≥ 0.60), up from 0.557 / 0.506.
  - What is left is the open band at h 0.4–0.6, between the skirt top and the arching fronds, and the open top corners
    beside the tall fronds.
  - The rear width profile is .35 1.00 .98 .88 .64 .50 .62 .89 .45 .52 .61; the sheet's is .63 .86 .91 .93 .86 .62 .81
    .74 .47 .54 .68.
- **r34 / f34 W : H 1.06 / 1.10** (sheet 1.367 / 1.305). At el 20 the depth adds to the height. With the decided
  footprint (4.04 wide, at the tolerance limit; 3.58 deep) a W : H of 1.3 would need about 4.6 wide. The sheet's
  three-quarters are not consistent with its orthos (§3.2).
- **Rear and r34 root share fell to 0.9 / 0.4 %** (sheet 4.1 / 5.8). The skirt that was asked to cover the root star
  now covers the crown too. Only the long back root and the R7 gap show some brown.
- **Front root** `#52371D`, toward `#684324` but not there. The hub sits in the front skirt's cast shade, and its band
  is already root_light.
- **Skirt leaves.**
  - They are broad and fewer (9) than the sheet's layered mound, so at a distance the back reads as big lobed leaves.
  - Curtain leaf tips are 88–99° and leaf L : W is 1.15–1.45. The spec asks for 45–60° and 1.5; round 1's accepted
    deviation was 82°.
- **f34 mid tone 41 %** (sheet 29). Mid includes `leaf_fresh` (hue 87°, which the study's mask counts as mid); still
  out by 12.
- **Rock share without a sheet target:** left side 10.3, az045 12.3, az315 13.7. These come from the front-left rock
  cluster (R1, R4) plus R5 through the N4 / N6 gap.
- **The SmallFrond part shot** still sees F5 end-on (presentation, unchanged).
- No commits or exports.

### Main session ruling after fix round 1 (2026-10-31)
- **Tall-rock peaks hidden in the front and f34: accepted.** This is the sheet's own §3.9 conflict: its front draws tall peaks, while its side and rear draw only low rocks. Keeping the rocks hidden from the side and rear was the blocker, and that matters more than a peek in front.
- **Accepted as minors:**
  - rear and r34 fill at 0.584 / 0.564;
  - f34 and r34 W : H limited by the width cap.
- **Next:** a fresh round-2 verifier.

## Verification round 2 (verifier, 2026-10-31)
A fresh verifier, read-only, in a background Blender on port 9881 on `wip/M060_verify.blend` (the main session's build
of the fixed `m060.py`; not saved). Renders and comparisons: `renders/models/M060/verify2/` (`cmp_0..2.png` and
`big_cmp_*.png` put each sheet cell beside ours, `spin_row0/1.png` the eight azimuths, `big_*.png` at 900 × 700,
`cmp_parts.png` the parts row). Scripts: `<temp>\...\scratchpad\m060_verify2\` (`audit.py`, `contact.py`, `bur2.py`,
`uvov.py`, `vis.py`, `vis_rock2.py`, `notch.py`, `col.py`); shares use the study's masks through the fix round's
`meas.py`. My renders measure the same as `fix1/` to within 0.2 points, so the kit-file build matches the fix build.

**Verdict: PASS, 7/10.** Both round-1 blockers are fixed. Nothing is broken, and from every side the model reads as the
sheet's fern: two tall lobed fronds in a V, lime fronds arching out, a skirt mound to the ground, rocks and roots at the
foot. The main leftover is visible but not a blocker: the big back "curtain" leaves have lost most of their visible
lobing.

### Round-1 blockers
1. **Tall rocks: fixed.** R5 / R6 are now broad blocks (0.70 × 0.60 × 0.80 and 0.80 × 0.65 × 1.00) under the back arches.
   They read as no more than grey bases peeking under the curtain leaves, never as bare obelisks.

   | View | Rock share, ours | Sheet (±3) |
   | --- | --- | --- |
   | Front | 10.8 % | 8.9 |
   | Side (right) | 8.2 | 6.4 |
   | Rear | 9.0 | 8.5 |
   | r34 | 5.8 | 8.3 |
   | az045 / az135 / az225 / az315 | 12.1 / 9.8 / 7.9 / **13.7** | ≤ ~12 |
   | Left side | 10.1 | no cell |

   - The ray grid at el 5 shows where the diagonal excess comes from. At az315 (front-left) it is R1 346, R2 223, R4 139
     and **R5 510 hits through the N4 / N6 gap**; R5 shows there only up to about the skirt line. At az045 it is R1 340,
     R6 361 and R3 242.
   - Minor, numeric.
2. **Rear mound and root star: fixed.** In the rear, r34, az135 and az225 the curtain leaves N4 / N6–N9 drop to the
   ground all round and cover the root arms. Only the long back root and a stub show.
   - Rear T is 0.9 % and r34 T 0.4 % (sheet 4.1 / 5.8). The rear is now over-covered (see minor 2).
   - It reads as a lush mound. It is less lobed than the sheet's (minor 1).

### Extras from the ruling: all done
- **Lobe ends.** Frond lobes are polygonal scallops, a shoulder, crown and shoulder with a V notch
  (`big_az135.png`, `big_rear.png`). There is no square ratchet edge any more; from a glancing angle a slight step
  remains.
- **Front root.** In the hero, the arms are root_light then a 75 % mix, and the hub's lower bands a 50 % mix then
  root_light. This is by member and height band.
  - The front T (v ≥ .25) still renders `#52371D` against the sheet's `#684324`, because of the shade under the front
    skirt. The rear is right at `#7B5432`.
- **GroundLeaf.** Three domed, cupped hexagonal pads, 36 tris; they match the parts cell's rounded clump.
- **MediumFrond part.** Mid green with fresh tips on both blades, as its cell. The hero's F3 / F3b keep their roles.
- **Eight azimuths.** Every view shows lobed fronds; I found no flat-card flaps or fins at 900 px. Ray grid 0.025
  (facet normals), % of visible foliage within 20° of edge-on:

  | Azimuth | 0 | 45 | 90 | 135 | 180 | 225 | 270 | 315 |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | el 5 | 8.6 | 8.8 | 7.7 | 9.8 | 5.2 | 8.5 | 8.3 | 8.5 |

  - At el 20 the range is 6.4–11.9.
  - Bare core (tubes + crown) is 3.1–10.7 %.

### Technical re-measure (all pass unless marked)
- **Tris.** Hero 3610 (ceiling 3800). Parts: Large 210, Medium 428, Small 214, RootCrown 262, BroadLeaf 162, Rock 30,
  GroundLeaf 36.
- **Size.** Hero 4.037 × 3.580 × 2.942.
  - Height: 3.0 ± 0.1. Depth: 3.45 ± 0.2.
  - **Width is inside decision 1's 3.85 ± 0.2 by only 0.013** (limit 4.05).
- **Origin and transforms.** All 8 objects have the origin at the bbox bottom centre, rotation 0, scale 1, identity
  deltas, no modifiers, no custom normals and flat shading.
  - The hero sits (−0.015, 0.150) from the crown axis, exactly at the 0.15 limit, and sinks 0.02.
- **Topology.** All 8 objects have 0 of each of these:
  - non-manifold, boundary and wire edges;
  - loose and duplicate verts;
  - zero-area faces and n-gons (fully triangulated);
  - bowtie verts and winding errors;
  - negative-volume shells and self-intersections within a shell.
  - The hero has 63 shells: 17 blades, 17 tubes, 9 crown pieces, 7 rocks and 13 sprig pads. No rock overlaps another
    rock or the hub.
  - The smallest corner is 2.75° on the hero (spec ≥ 3°). Numeric.
- **Floating.** Tolerance 0.03, chained to the ground: 0 floating and 0 unchained shells. Every blade touches its own
  tube; every tube sits 0.050–0.078 inside the hub; F3b / F4b seat in their parent tubes. Nothing is below z −0.025.
- **Buried.** No blade, tube or sprig is inside any rock or the hub (ray parity, 3 rays).
  - **root4 (az 248°) runs 0.079 into R1.** All 5 verts of its end ring are inside, so its cut-end face is hidden in
    the rock. The spec allows 0.05.
  - root1 goes 0.040 into R7 and 0.031 into R6, both inside the limit.
  - The builder's bury report doesn't test roots against rocks. Visually it reads as a root running under the rock.
    Numeric minor.
- **UV.** Rasterised at 1024²: 0 overlapping cells and 0 flipped faces on every object. Density p5 / p95 is within
  0.997–1.005, and the islands sit inside 0.008–0.992.
- **Colour code (read).** Nothing is chosen by face normal:
  - blades by lobe band along u and role (`blade`, `_ramp` / `_tone`);
  - tubes by segment;
  - the crown by member and height band;
  - rocks by noise field, height fraction and position (`q.x < c.x`, top-back dot);
  - sprigs alternate by pad.

  `kit_baked_shading` is 0.32 on the hero in this build (the fix round reported 0.00) and 0.29 on RootCrown, both under
  0.5.
- **Colours on the renders** (sheet in brackets):

  | Region | Ours | Sheet |
  | --- | --- | --- |
  | Front all-green | `#63941E` (85°) | `#5D961C` |
  | Green, v > .7 | `#A1D225` | `#A1D224` |
  | Light | `#A5D522` (76°) | `#A8D722` |
  | Mid | `#6D9D20` (**83°**; §5.4 floor 86°, numeric) | `#69A520` |
  | Dark | `#2A5D17` (**104°**; floor 105°, numeric) | |
  | Rear all-green | `#437A21` | `#498216` |

  - Not olive. The dark-vs-lime contrast is strong: F1 / F2 and the back curtains dark, the arching fronds and front
    skirt lime.
  - **Rocks.** Front median `#807C71` against `#7F7C76`: warm, R ≥ G ≥ B, never lavender. The lit rock
    `#BEBBA8` (52°) is a little less warm than the sheet's `#D3C5AD`.

### Minors (none blocking)
1. **Curtain leaves read nearly unlobed** (visible).
   - N4 / N6–N9 are 5 of the 9 skirt leaves and fill the side, left, rear and back-diagonal views. There they read as
     big plain heart or arrowhead leaves (`big_cmp_side.png`, `big_cmp_rear.png`, `big_sideL.png`). The sheet draws
     every skirt leaf with open, rounded lobes.
   - `notch.py` on `_side_outline`:

     | Outline | Notch depth (of the half-width) | Notch opening |
     | --- | --- | --- |
     | Curtain leaves | 0.70 | **about 10°**, mouth 0.066 |
     | Other leaves | 0.66 | **9–13°**, mouth 0.044 |
     | Fronds | 0.64 | 17–26° |

   - The slits close up visually on the drooping blades.
   - Cheap fix if wanted: open the leaf notches (shoulders at about ±0.22 of the pitch instead of ±0.35, or relax the
     fan clamp on shoulder 2) so they show as rounded V scallops. It costs no extra tris.
2. **The rear is over-covered.**
   - Rear T is 0.9 % and r34 T 0.4 % (sheet 4.1 / 5.8).
   - The sheet's low rock ring and brown roots don't show along the rear foot. One grey block shows under the centre
     instead.
   - The top view (e 60) also hides most of the rock ring.
3. **root4 0.079 inside R1** (above). Shorten it (R 0.80 → about 0.68) or move it a few degrees.
4. **The front root is still dark:** `#52371D` against `#684324`.
5. **Tone shares out of ±8.**

   | View | Ours (light / mid / dark) | Sheet |
   | --- | --- | --- |
   | f34 | 29 / **41** / 30 | 33 / 29 / 38 |
   | Side | 29 / **45** / 25 | 38 / 34 / 28 |
   | r34 | **24** / 34 / 42 | 37 / 26 / 37 |
   | Front | 27 / 36 / 37 (in) | 31 / 29 / 40 |
   | Rear | 22 / 36 / 42 (in) | 28 / 28 / 44 |

6. **Silhouette** (accepted in the ruling).
   - Fill: front 0.577 (sheet 0.649), f34 0.520 (0.621), rear 0.584, r34 0.564.
   - W : H: f34 1.096 and r34 1.062, held down by the width cap.
   - W : H in band: front 1.276, rear 1.256, side 1.096.
7. **At the limit:** width 4.037 (limit 4.05), origin offset 0.150, smallest corner 2.75°.
8. **az045 shows the bare hub and root arms** between N1 and N3 (T 5.1 %, inside the sheet's T range). The SmallFrond
   default part shot is end-on; at (−60, 20) it reads as a lobed lime frond.

**Ready for export and commit, with the leftovers above.** Minor 1 is the only one worth a quick optional touch.

### Main session ruling (2026-10-31)
Round 2 PASSED at 7/10, so the model is committed.
- **Change before the commit:** verifier minor 3 (root 4 ran 0.079 into R1, past the 0.05 burial limit) was fixed in the main session. `ROOTS[4]` was shortened from 0.80 to 0.68. After the GUI rebuild, a ray-parity check found the deepest root vertex inside any rock at 0.040.
- **Recorded for polish:** the other minors, chiefly:
  - the curtain leaves reading nearly unlobed, because their notches are too narrow;
  - the rear over-covered, with almost no roots or rock ring showing;
  - tone shares in the f34, side and r34 views;
  - width and origin offset at their limits.

Export: 8 assets, 4952 tris, 0 problems.
