# 056 Moss and Ivy — spec

Reference: `art/blender/assets/references/056.png` (1024 × 1536 px). INDEX.md row 56: "Moss and Ivy model study". The
sheet's own header reads **"60 — MOSS AND IVY"** and **"PAGE 60/132"**, "FLINTBORN — INDIVIDUAL MODEL STUDY" (our
number is INDEX's 056, §3.1). Builder: `art/blender/kit/mcp/m056.py` → `build()` (not written yet). Procedure:
`art/blender/kit/mcp/STAGES.md`. One modeller does stages 1–6 in a background Blender, then a fresh verifier does
stage 7. The main session puts the model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet. Colours "need to match the master reference and blend into
the colors nearby". Every model ships its colour, texture and VFX. **This sheet shows no effect** (§7).

Sheet text (paraphrased):
- **Description (top left):** low moss cushions and climbing ivy overlays for rocks, walls and ruins. It is chunky,
  layered ground and wall cover, built from simple modular parts with clean silhouettes.
- **Palette (top left, unlabelled):** five swatches: dark green, mid green, lime, stone, brown (§5.1).
- **"ASSEMBLED FRONT THREE-QUARTER"** and **"ASSEMBLED REAR THREE-QUARTER"**: the hero (§1.3). The two cameras are
  exactly 180° apart (§3.2).
- **FRONT / SIDE / REAR / TOP** (no "orthographic" claim). Front and rear are redraws of the two 3/4 views, not true
  orthos (§3.3).
- **"PARTS (EXPLODED)"**: left half, the hero pulled apart: 4 stone "double bricks", 2 moss cushions above with down
  arrows, a draping ivy curtain and a long tendril on the right with dashed arrows to the wall, base cushions, rocks and
  ivy sprays below. Right half: six labelled parts: **MOSS CUSHION (large)**, **MOSS CUSHION (small)**, **IVY CLUSTER
  (flat)**, **IVY TENDRIL (segment)**, **CORNER PIECE (angled)**, **SINGLE IVY LEAF**.
- **"CONSTRUCTION CLOSE-UPS"**: (1) "Moss cushion sits on top surface with simple flat join"; (2) "Ivy segment with
  attachment pad underside view"; (3) "Leaf cluster layering on corner junction".
- **"MATERIALS & MODELING NOTES"**: Stone: large, clean flat faces, a pale warm rock colour. Moss: low, rounded
  cushions, simple faceted shapes. Ivy leaves: flat, chunky leaf planes with a simple angular silhouette. Ivy tendril:
  simple low-poly branch segments with flat junctions.

**What this model is.** It is a **dressing kit**. The six overlay parts are the product: they are laid on other kit
pieces (rock tops, wall faces, ruin edges, ground). The hero is the sheet's demonstration piece: a **ruin stone block
(a short wall chunk) dressed with moss cushions on top, four ivy runs climbing its faces, and moss, rocks and ivy
sprays round its foot**.

**The old kit.** W06 row 4 `MossAndIvy` (`art/blender/scripts/kit/W06/moss_and_ivy.py`, goals
`art/blender/renders/kit/W06/moss_and_ivy_goals.md`) is the old take on a similar row. Its hero was a near-cube ruin
block (6.5 × 6 × 6.5, 3 courses). Its moss was clusters of open-bottomed domes, its ivy 3/5-lobed fans on 4-sided
tubes. `MODEL_PROGRESS.md` row 65 judged it "smooth blocks; neon moss; sparse ivy". W06 owns every `MossAndIvy*` name
and the WIP part names `MossCushion*`, `IvyClusterFlat`, `IvyTendril`, `IvyCornerPiece` and `IvyLeafSingle` (§8).

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Paper `#FAF6EC`, tolerance
12. Cell rules (measured grey lines):
- rows y 455–456, 726, 734, 1190, 1198–1199, 1469, 1496–1497;
- ortho dividers x 304–305, 491, 759–760;
- exploded | parts (dashed) x 548;
- close-ups | notes x 697; frame x 12 / 1011.

Cells (`m.V`):
- f34 (192,98,614,452); its left strip (192–222, 98–215) is blanked, because the description text runs into it;
- r34 (614,98,1010,452);
- front (14,490,303,724), side (306,490,490,724), rear (493,490,758,724), top (762,490,1010,724);
- exploded assembly (14,762,546,1188).

Part cells (object boxes):
- moss cushion large (571,831,700,921), small (730,839,824,906);
- ivy cluster (852,827,993,952), tendril (599,1005,654,1174);
- corner piece (722,1031,830,1158), single leaf (893,1035,970,1126).

Close-ups: CU1 (29,1237,239,1417), CU2 (254,1237,469,1417), CU3 (486,1237,681,1417). Notes icons x 722–795: stone
y 1235–1300, moss 1300–1350, leaf 1355–1420, tendril 1415–1495.

Swatches (`m.SW`, y 220–255): S1 (20–51), S2 (55–86), S3 (90–121), S4 (125–156), S5 (160–190).

**Masks** are `cls()` in `m.py` (HSV, h in degrees, assigned in this order):
- **Background:** the paper, plus the warm floor glow round every view (v ≥ 0.92, s < 0.42, h 20–60, flood-filled
  from the paper). The glow is `#FBF0DE`-ish and would otherwise count as stone.
- **X, cast shadow:** pale neutral (s < 0.10, v 0.62–0.92) touching the background, components ≥ 80 px.
- **G, green:** h 48–180, s ≥ 0.30, v ≥ 0.12 (moss and ivy).
- **T, stem:** h < 48, s ≥ 0.40, v 0.12–0.80 (brown tendrils).
- **R, stone and rocks:** v ≥ 0.22 and (s < 0.40, or warm and v ≥ 0.80).
- **O, other:** outlines and dark joints.
- **Known bias:** the brightest block tops (v ≥ 0.92) sometimes flood into the background, so R is about 1–2 points
  low on the sheet. Apply the same masks to our renders and the bias cancels.

**Scratch study material** (no Blender) in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m056_study\`.
Run the scripts with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14, Pillow, numpy).
- **Helpers:** `m.py` (masks, boxes, swatches, `cellcls()`, `silhouette()`, `preview()`) and `zoom.py` (`zoom.py x0 y0
  x1 y1 scale out.png [grid]`).
- **Measurements:**
  - `measure.py`: bbox, W : H, shares, fill, profiles, fifths → `measure_out.txt`;
  - `samp.py`, `samp2.py`: colour per region, the green classes, the stone lit / shade split → `samp_out.txt`,
    `samp2_out.txt`;
  - `parts.py`: the part cells; `split.py`: moss vs ivy and lit vs shade shares; `sw.py`, `sw2.py`: swatches;
    `lines.py`: cell rules.
- **Zooms** (gridded at 10 px):
  - `p_f34.png`, `p_r34.png`, `z_f34big.png`, `z_r34big.png`;
  - `p_ortho.png`, `z_front.png`, `z_side.png`, `z_rear.png`, `z_top.png`;
  - `p_expl.png`, `z_expl_stone.png`, `z_expl_ivy.png`, `z_parts.png`, `z_tendril_corner.png`;
  - `z_cu.png`, `z_cu2.png` (close-ups and notes).
- **Mask previews:** `cls_*.png`, `cls_mont.png`.
- **On our renders:** copy `measure_render.py` from `..\m047_study\` and point it at this folder's `m.py`, so the same
  masks and the same background glow rule apply. Render with the floor hidden.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (the hero) plus six small overlay parts. Hero budget 4000 tris; each part under 1000.
  The plan in §4.3 lands at about 3610–3720.
- **Overall read (check this first).** A **pale warm-stone ruin block**: a short, thick wall chunk of **three courses of
  big chamfered bricks** in running bond. It is about **twice as long as it is deep** and a bit shorter than a
  character. On top sit **a few low, lumpy lime moss cushions**. **Four ivy runs** climb it, each a brown square-section
  tendril with **flat, chunky, five-pointed leaves** in lime and two greens:
  - a wide curtain on the front face;
  - a full curtain on the right end;
  - a curtain on the back face;
  - a low patch on the left end.
  The runs lip over the top edges and spill onto the ground at their feet. **Moss cushions** and a few **pale faceted
  rocks** line the base.
  - It reads **green first, stone a close second**: G 52–53 % and R 43 % of every 3/4 silhouette, stems 1.4–2.1 %.
  - In the f34 the green is about half moss cushions, half ivy. In the r34 it is mostly ivy (§1.2).
- **Focal features, in order:**
  1. The ivy curtains: leafy runs of flat, pointed, overlapping leaves with brown stems showing between them,
     top to ground (every view).
  2. The block: big chamfered bricks with dark joints, warm lit faces, three courses.
  3. The moss cushions: low, faceted, lumpy lime domes on top and at the foot.
  4. The base: cushions, rocks and ivy sprays on the ground.
- **Target size (decision §8.1).**
  - **Stone core 7.8 (X, long) × 4.0 (Y, deep) × 4.8 (Z, three courses of 1.6).** The moss tops reach z ≈ 6.0.
  - **Overall about 11.0 × 7.9 × 6.05** with the base dressing (§2.7).
  - Tolerances: core ±0.3 per axis; overall ±0.5; top of moss ±0.3.
  - Ivy leaves 0.8–1.1 across; main stems Ø 0.26.
  - **How it was derived.** Both 3/4 views show the same layout: a narrow grey face on the left and a broad lit face on
    the right. Their top edges give the camera and the proportions (§3.2):
    - f34: left face 121 px, slope 13 / 121; broad face 225 px, slope 27.5 / 225 → azimuth **≈ 47°** off the broad
      face, elevation ≈ 7–12°.
    - r34: 117 px (slope 23 / 114) and 211 px (slope 46 / 211) → 46°, e ≈ 12°.
    - **Core W : D : H = 1 : 0.51 : 0.62.** r34: W 306 px, D 157, H 189 (near corner, top y 198 → ground y 387). f34:
      W 330, D 164.
    - **Bricks:** the end face shows 3 columns; the long face about 2.8 brick lengths per course; 3 courses. A brick is
      about L : D : H = 2 : 1 : 1.15, the exploded's "double brick" (§1.4).
  - **Why H 4.8.**
    - It is a ruin chunk just under head height (0.87 C). The moss crown (6.0) is at 1.09 C.
    - A player can **jump onto it** (Roblox's default jump height is 7.2) and **walk the top** between the cushions,
      but cannot step over it.
    - Leaves come out at 0.8–1.1 studs: big enough to read in-game.
    - At this scale the part sizes in §2.6 match the kit's other dressing: 035 moss caps, 039 rosettes about 0.9.
  - **Against the character (5.5):** a scale shot with one marker at the front face (X −2, Y −3.3) and one standing on
    the top at (X +2.4, Y 0) between the cushions and the ivy spill.
- **Build frame (decision §8.2):**
  - The **long faces are front (−Y) and back (+Y); the ends are left (−X) and right (+X)**.
  - Ground z 0, the core centred at x 0, y 0.
  - The **f34 camera is front-LEFT (az ≈ −47)**; the **r34 camera is rear-RIGHT (az ≈ +133)**. Kit azimuth convention
    as in 055: 0 = front, +90 = right (+X), 180 = rear.
  - Origin = bbox bottom centre. The dressing is near-symmetric in X, so the origin stays within 0.25 of the core
    centre (planned bbox centre ≈ (−0.03, −0.22)); record it.

### 1.2 Measured views (`measure.py`, `split.py`)

| View (box) | Silhouette bbox (px) | W : H | G | R | T | O | fill |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (192,98,614,452) | 196–613 × 110–435 (418 × 326) | **1.282** | **52.6 %** | **43.1** | 1.4 | 2.8 | 0.715 |
| Rear three-quarter (614,98,1010,452) | 614–990 × 105–414 (377 × 310) | 1.216 | 52.0 | 43.3 | 2.1 | 2.5 | 0.742 |
| Front (14,490,303,724) | 23–287 × 502–714 (265 × 213) | 1.244 | 51.9 | 43.6 | 1.6 | 2.9 | 0.792 |
| Side (306,490,490,724) | 326–475 × 503–712 (150 × 210) | 0.714 | 57.8 | 35.8 | 4.0 | 2.4 | 0.617 |
| Rear (493,490,758,724) | 504–746 × 509–712 (243 × 204) | 1.191 | 51.0 | 45.0 | 1.8 | 2.2 | 0.788 |
| Top (762,490,1010,724) | 778–992 × 526–702 (215 × 177) | 1.215 (W : D) | 74.3 | 22.9 | 0.4 | 2.4 | 0.784 |

- Shares are of the silhouette (O included, X excluded). **Verifier tolerance:** G ±4, R ±4, T 1–3 % in the 3/4 views;
  W : H ±0.08; fill ±0.05.
- **Green split** (hand boxes round the cushions; the boxes catch some ivy, so these are rough):
  - **f34:** moss ≈ 22–26 %, ivy ≈ 26–30 % of the silhouette.
  - **r34:** moss ≈ 9–11 %, ivy ≈ 41–43 %.
- **Stone lit / shade split** (v ≥ 0.66): f34 17.3 / 25.8 %, r34 20.5 / 22.8 %. The lit faces are the broad faces,
  the shade faces the ends; that is the light, not the material (§3.6).
- **Green classes** (within G):

  | Region | lime h < 72 | yellow-green 72–85 | green 85–100 | deep ≥ 100 |
  | --- | --- | --- | --- | --- |
  | f34 front curtain | 47 % | 18 | 17 | 18 |
  | r34 back curtain | 48 | 23 | 20 | 9 |
  | r34 right-end curtain (shade side) | 25 | 40 | 14 | 20 |
  | f34 moss on top | 62 | 31 | 6 | 1 |

  So moss is lime over a yellow-green (79°) lower band, never blue-green. Ivy is lime, mid green (91°) and dark
  blue-green (111–121°) leaves.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.1 W):

| f | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .28 | .80 | .84 | .94 | .97 | .99 | .97 | .89 | .86 | .83 | .34 |
| r34 | .28 | .79 | .88 | .94 | .99 | .98 | .91 | .90 | .89 | .27 | .16 |
| Front | .16 | .81 | .87 | .95 | .98 | .99 | .96 | .88 | .87 | .84 | .18 |
| Side | .07 | .33 | .84 | .91 | .93 | .99 | .98 | .93 | .27 | .19 | .09 |
| Rear | .09 | .83 | .89 | .87 | .94 | .96 | 1.0 | .98 | .86 | .84 | .14 |

**Width per height** (silhouette width at h .0 → 1.0 as a fraction of W):

```
f34    .16 .95 1.00 .97 .81 .81 .82 .82 .82 .41 .02
r34    .13 .98 .97 .88 .84 .84 .83 .85 .78 .52 .04
front  .58 .96 .96 .86 .85 .85 .87 .87 .87 .50 .03
side   .35 .96 .83 .68 .58 .58 .58 .58 .58 .41 .06
rear   .16 .95 .89 .85 .84 .85 .85 .85 .85 .60 .06
```

- Reading (f34): h .1–.3 is the base dressing at full width, wider than the block. h .4–.8 is the block (0.81–0.82
  W). h .9 is the moss crown (0.41), and the top 0.1 is the tallest cushion. The profile is a **flat-topped block with
  a domed moss crown left of centre**, the ivy lip at right a step lower (.83–.86).

**Height fifths** (bottom → top, % of each class):
- f34: G 25.1 / 26.3 / 13.5 / 14.6 / 20.4; R 18.4 / 20.7 / 28.9 / 29.7 / 2.4; T 10.5 / 29.0 / 40.2 / 19.1 / 1.1.
- r34: G 18.2 / 22.4 / 17.8 / 20.0 / 21.6; R 25.2 / 23.6 / 24.3 / 24.1 / 2.7.
- **Green is in all five fifths:** base cushions and sprays low, curtains through the middle, moss crown on top. Stone
  is absent from the top fifth (the crown hides the block's top). Stems are mid-height.

**x fifths, left → right** (f34): G 9.5 / 23.5 / 24.3 / 36.7 / 6.1; R 21.9 / 24.3 / 29.0 / 6.6 / 18.2. **The fourth
fifth is the front curtain** (G 37 %, R 7 %); the last fifth is bare stone at the front-right corner.

### 1.3 Silhouette and composition per view

**Front three-quarter (`z_f34big.png`) — governs with the front cell.** Front-left camera (§3.2), e ≈ 10–15°, light
perspective.
- **Left of the image: the left end (−X) in shade**, x 225–346. It shows three brick columns (about 40 px each) in
  three courses, with grey-mauve shade (`#746A6A`).
- **Right of the image: the front face (−Y), lit warm beige** (`#D3B595`), x 346–571. It has big chamfered bricks with
  dark joints and a clear running bond, and a broken corner on the top-right brick.
- **Main ivy curtain on the front face**, X ≈ −0.6 … +3.4 (image x 430–560, about 0.37–0.95 of the face):
  - from the top edge, where the leaves lip over onto the top at the front-right, down to the ground;
  - at its foot the leaves spread onto the ground round the front-right corner;
  - a thick brown stem shows in the middle (x 480–500), with leaves layered over it: lime in front and above, dark
    green under and between.
- **The far-right column of the front face** (X +3.4 … +3.9) is bare lit stone, top to bottom.
- **Left-end ivy patch:** a low run on the −X end from the ground to about z 2.4, across most of the end's width.
- **Top:**
  - three cushions on the left two-thirds of the top: a large one at the centre, one near the left end, one behind
    toward the back;
  - a small cushion right on the front edge;
  - lime moss specks along the top joints;
  - the curtain's leaves covering the right third of the top.
- **Base:**
  - a dark cushion against the left end;
  - two small cushions and one **big cushion** along the front face (the big one in front of the curtain's foot);
  - a blue-grey rock at the front-left corner, a beige rock pair at the front-right corner, pebbles.

**Rear three-quarter (`z_r34big.png`).** The same camera turned 180° (rear-right, az ≈ 133).
- **Left of the image: the right end (+X), in shade,** with a **full-width curtain** from the top (lipping onto the
  top) to the ground, wrapping the back-right corner.
- **Right of the image: the back face (+Y), lit,** with a **curtain** at X ≈ −3.2 … +0.9, its stem at X ≈ −1. Its foot
  spreads onto the ground toward the back-left corner, where a cushion sits.
- **Top:** the **largest cushion** (≈ 3.2 wide), centred about X −0.2.
- **Base:** a **big pale rock** behind the back face at X ≈ −0.3, with an ivy spray beside it, and a cushion at the
  far left beyond the right end.

**Front, rear (`z_front.png`, `z_rear.png`).** Redraws of the f34 and r34 at a slightly different angle (front:
narrow : broad 79 : 163 = 0.48, ≈ 44°; rear 88 : 135 = 0.65, ≈ 52°), at 0.63 and 0.64 of their scale. Same content.
They are compared at those angles (§2.7). Neither is a true front or rear ortho (§3.3).

**Side (`z_side.png`).** A view about 20° off the **+X end** toward the back: the end's full curtain (lime and green
leaves on a thick S-curving stem, top to ground, spreading at the foot), a sliver of the lit back face, a moss
cushion at the base on the back side, moss on top. The core is drawn narrow (93 px against 163 tall), narrower than
the 3/4 views allow. **Judged for content** (§3.3).

**Top (`z_top.png`).** A large cushion left of centre (about 45 % of the width), two smaller ones below-left, ivy
leaves over the right half and the top edge, pale rocks at the corners. The block outline is barely visible and the
footprint reads 1.22 : 1, not 2 : 1. **Judged for content** (§3.3).

**Close-up 1 (moss on top).** Two cushions sit on a block's flat top. Their bases are flat and planar on the stone,
with no skirt and no gap. Ivy leaves in front lip over the edge, overlapping. Each cushion is a faceted lumpy dome,
lime on the lit upper facets and darker yellow-green at the lower ring.

**Close-up 2 (attachment pad, from below).**
- A block's underside, chamfered into four tiles.
- A **square flat pad** with a chamfered rim, about 2.2× the stem width and 0.4× as thick, flat against the stone.
- A **square-section brown stem** leaves the pad and runs down.
- A green leaf stalk joins the stem, with leaves below.
- **Flat junction:** the stem simply butts into the pad.

**Close-up 3 (corner junction).** Leaves layered round a vertical outside corner of the block. Each leaf lies nearly
flat on the stone, 0.0–0.1 off it, and overlaps the next by 30–50 %. They hang tip-down, lime on the outer layer and
green beneath, with the brown stem showing between. The bricks have big chamfers on every visible edge and a slight
facet crease across each face.

### 1.4 Parts (exploded, `p_expl.png`, `z_parts.png`)

**The hero governs every size and position** (§3.5). The exploded gives shapes, counts and joints.

| Part (label) | Box (px) | W × H px, W : H | Notes |
| --- | --- | --- | --- |
| Stone bricks (unlabelled) | (40–310, 845–1110), four pieces | each ≈ 2 : 1 : 1.28 (L : D : H) | four **"double bricks"**: a long face with a vertical seam groove at mid-length, a short end, big chamfers, a faint diagonal facet crease. Arrows show two side by side per course, two courses. The hero has more (§3.4) |
| MOSS CUSHION (large) | (571,831,700,921) | 130 × 91, 1.43 at ≈ 20° elevation | one low lumpy dome, **6–7 lumps** round the outline, flat base; lime upper facets, yellow-green lower ring; true H : W ≈ 0.42 |
| MOSS CUSHION (small) | (730,839,824,906) | 95 × 68, 1.40 | the same at 0.73 scale, **4–5 lumps** |
| IVY CLUSTER (flat) | (852,827,993,952) | 142 × 126, 1.13 | an **upright mat of about 22 leaves**, wide at the top (lime leaves fanning out and up), tapering down to a ragged hanging point of dark leaves; under-layer dark blue-green; no stem visible |
| IVY TENDRIL (segment) | (599,1005,654,1174) | 56 × 170, 0.33 | a **straight-ish brown stem** (Ø ≈ 1/3 of a leaf width), cut flat at the top, with **8 leaves** alternating left and right, tips down; yellow-green leaves |
| CORNER PIECE (angled) | (722,1031,830,1158) | 109 × 128, 0.85 | an **L-shaped spray**: an upper arm of lime leaves lying on a horizontal surface (receding to the upper right), and a hanging arm of darker leaves going down the vertical face; stem showing at the bottom. **About 18 leaves** |
| SINGLE IVY LEAF | (893,1035,970,1126) | 78 × 92 (blade ≈ 78 × 65) | **five points**: a long terminal lobe, two side lobes, two small basal lobes, two clear notches; a short green stalk; two-tone facets either side of a midrib crease. Colour `#5F9E33` (95°) |
| Draping curtain (unlabelled, hero piece) | (395–560, 820–1110) | | an S-curving brown stem with 2–3 branches, about 35 leaves, hooking over the top edge |
| Long tendril (unlabelled) | (570–715, 785–1080) | | a stem hooked over the top and hanging, about 20 leaves |

### 1.5 How 056 differs from W06 `MossAndIvy`, 035 and 036 (binding: the verifier checks these)

| | W06 `MossAndIvy` (old kit) | 035 Mossy Boulder / 036 Rock Cluster | **056 Moss and Ivy** |
| --- | --- | --- | --- |
| Base | a near-cube ruin block 6.5 × 6 × 6.5 of smooth blocks | rocks | **a 2 : 1 wall chunk 7.8 × 4.0 × 4.8: three courses of big chamfered bricks, running bond, dark joints, one broken corner** |
| Moss | clusters of **open-bottomed** puffy domes, "neon" | flat lobed mats / rosettes on rock | **low, closed, faceted, lumpy cushions** (H : W 0.40–0.45), lime over a 79° lower band, flat bases |
| Ivy | sparse fans on 4-sided tubes | none (clover rosettes) | **four dense runs** of flat 5-point leaves, about 110 leaves, three leaf tones, square-section stems with flat junctions and pads, lipping over edges and spilling onto the ground |
| Parts | MossCushionLarge / Small, IvyClusterFlat, IvyTendril, IvyCornerPiece, IvyLeafSingle | — | the same six overlays, rebuilt, with explicit attach frames (§2.6) |

## 2. Layout (starting values; tune on the renders)

Studs, build frame of §1.1 (long faces ±Y, ends ±X, ground z 0, core centred).

### 2.1 Stack (binding contact chain, bottom up; seat gap 0.015 unless stated)

| Piece | Sits on / against | Contact |
| --- | --- | --- |
| Bottom-course bricks | ground | sunk 0.02 |
| Upper-course bricks | the bricks below | bottom face 0.015 above the brick below; side faces 0.015 from neighbours |
| Top moss cushions | the top course's flat tops | flat base 0.02 into the top; never more than 0.05 into stone |
| Base moss cushions | ground, and may lean on the wall | base sunk 0.03; ≤ 0.05 into the wall |
| Rocks, pebbles | ground (may touch the wall) | sunk 0.08 / 0.04; ≤ 0.05 into the wall |
| Attachment pads | a stone face (top face, under a lip, or a wall face) | pad back 0.00–0.015 off the stone |
| Stems | pads and stone | segment backs within 0.03 of the stone along their length, or bridging between two contacts; segments overlap 0.05 at flat junctions; the stem end ≥ 0.05 into its pad |
| Leaves | the stem (at the stalk notch) and the stone or the leaf under them | stalk notch within 0.03 of the stem (≤ 0.05 into it); blade 0.01–0.05 off the stone or the leaf below; never inside the stone |
| Ground-spray leaves | a ground stem, and the ground | blade 0.01–0.03 above z 0, stalk on the ground stem |

### 2.2 Stone core

- **Courses:** z 0–1.6, 1.6–3.2, 3.2–4.8. **Rows across the depth:** three rows of 1.33 (front, middle, back).
- **Long-face bond** (along X, each row; the back row offset half a brick from the front so the r34 doesn't mirror the
  f34):

  | Course | Front row bricks (X lengths) | Back row |
  | --- | --- | --- |
  | 1 (bottom) | 2.6, 2.6, 2.6 | 1.3, 2.6, 2.6, 1.3 |
  | 2 | 1.3, 2.6, 2.6, 1.3 | 2.6, 2.6, 2.6 |
  | 3 (top) | 2.6, 2.6, 2.6 | 1.3, 2.6, 2.6, 1.3 |

- **Middle row:** courses 1–2 as one chamfered bar each, 7.8 long. Their ends show as the middle brick-end column on
  each end face, the f34's three end columns. Course 3 gets three real bricks (2.6), because its tops show between the
  cushions.
- **Brick shape:**
  - a box with a **0.16 chamfer on the four vertical edges and the four top edges**; bottom edges square, since they
    sit on the course below;
  - a **faint facet crease** on each long face: one diagonal edge, the far half pushed in 0.03. This is the sheet's
    "two-tone" face, lit by the sun;
  - ±0.03 jitter per brick in position and ±1° in yaw, so the joints read hand-laid. No brick more than 0.05 proud of
    the face plane.
- **Joints** read dark because the chamfers meet in a V. No extra joint geometry.
- **Damage:** the front row's top-right brick gets a **broken corner** (a 0.35 chip cut off its top-front-right corner,
  as in the f34). Give one back-row brick a 0.25 chip. No booleans: build the chip into the brick's ring.
- **Moss in the joints (optional, decision §8.9):** 4–6 thin lime strips (0.08 wide, 0.6–1.2 long) seated along top
  joints between the cushions. These are the f34's specks.

### 2.3 Moss cushions

**Shape (one closed shell each).**
- A flat base disc whose outline is **scalloped**: 12 verts, alternating radius ±10 %, so each lump shows in the
  outline.
- A bulged mid ring at 0.4 h (1.05 r).
- A lumpy upper ring of 8 at 0.78 h (0.62 r), each vert ±0.06 h.
- A 3–4-vert faceted crown at h.
- **H : W 0.40–0.45.** Lumps: 6–7 (large), 4–5 (small). Broad facets, no subdivision.
- **Never a ball or an egg** (M047's "pads read as balls"). The widest point stays in the lower half; the base is flat
  and the full width.

| Cushion | Where (x, y, base z) | W × D × H | Evidence |
| --- | --- | --- | --- |
| CT1 large (top) | (−0.4, +0.2, 4.8) | 3.0 × 2.5 × 1.25 | r34 centre, top cell's big cushion, f34 centre |
| CT2 (top) | (−2.6, −0.3, 4.8) | 2.2 × 1.9 × 0.95 | f34 left cushion; top cell left |
| CT3 (top) | (+1.3, +1.0, 4.8) | 1.9 × 1.6 × 0.9 | f34 behind-right cushion |
| CT4 small (top front edge) | (−1.4, −1.45, 4.8) | 1.5 × 1.2 × 0.75 | f34 small cushion on the front edge (lips 0.15 past the edge, its base still fully on the top) |
| CB1 big (front, at the curtain's foot) | (+1.0, −3.05, 0) | 2.8 × 2.2 × 1.2 | f34 big base cushion |
| CB2 (front) | (−1.9, −2.7, 0) | 1.6 × 1.4 × 0.8 | f34 mid cushions |
| CB3 (front-left) | (−3.3, −2.65, 0) | 1.5 × 1.3 × 0.75 | f34 |
| CB4 (left end) | (−4.7, −0.5, 0) | 1.6 (X) × 1.8 (Y) × 0.95 | f34 far-left dark cushion |
| CB5 (back-left corner) | (−3.5, +2.75, 0) | 1.7 × 1.5 × 0.85 | r34 far-right cushion |
| CB6 (right end, back side) | (+4.65, +1.3, 0) | 1.6 (X) × 1.4 (Y) × 0.8 | side cell base cushion; rear cell right |

- Positions put each base cushion's wall-side rim 0.03–0.05 into the wall face (front y −2.0, back y +2.0, ends
  x ±3.9). Re-seat after the cushion's lumps are built: the scalloped outline changes the rim.
- Yaw each cushion differently. Keep the top's right third (X > +2.0) free of cushions: the ivy spills there.

### 2.4 Ivy runs

**Leaf.** One closed **lens shell, 16 tris.**
- **Outline of 8 verts:** tip, right notch, right side-lobe tip, right basal-lobe tip, the stalk notch, left basal,
  left side, left notch.
- **Proportions:** width 1.0, length 0.95; side lobes at 0.55 L, ±0.48 W; basal lobes at 0.15 L, ±0.30 W; notches
  0.22 deep.
- **Top face:** a fan from a centre vert raised 0.05, offset toward the stalk, so a midrib crease shows.
- **Bottom face:** a fan from a centre vert 0.02 below.
- **Sizes:** 0.8–1.1 across, median 0.92.
- **No separate stalk on hero leaves** (decision §8.8). The blade's stalk notch is seated on the stem, within 0.03 or
  up to 0.05 into it; on the sheet the stalks are hidden under the overlapping blades. Only the IvyLeaf part (and
  optionally IvyTendril) gets a stalk: a 3-sided prism 0.3–0.35 long, Ø 0.06–0.07, 6 tris, as its own closed shell
  seated into the blade's notch.
- Blades lie **close to the stone**, tilted out 8–20° at the tip. **Tips point down or down-sideways** (hanging),
  ±35° from straight down. Overlap 30–50 % within a run.
- **Never edge-on to the governing cameras.** Every wall leaf's normal must be within 75° of the f34 or r34 view
  direction; check at az −47 and +133. Leaves on the top face tilt up 25–40° toward the nearest edge so they read from
  e ≈ 12°.

**Stem.**
- A **4-sided (square) section**, per close-up 2: main Ø 0.26, branches Ø 0.16.
- Straight segments 0.6–1.0 long with **flat junctions**: kinks of 10–30°, each next segment overlapping 0.05. No
  smooth sweeps.
- An S-wobble of ±0.3 across the run.
- Lips over the top edge as two segments: one along the top, 0.4–0.8 in from the edge, ending in a pad; one down the
  face.

**Pads.** A square plate, 0.55 × 0.55 × 0.10:
- one on the front face at about (−0.3, −2.0, 3.3), where R1's left branch is pinned to the wall: fully chamfered,
  20 tris. The block has no overhang, so close-up 2's "underside view" is read as this pad seen from below
  (decision §8.7);
- four on the top faces (one per run's top anchor), chamfer-top only, 12 tris.

| Run | Face, X / Y span | Top → bottom | Stem path | Leaves |
| --- | --- | --- | --- | --- |
| R1 front curtain | front (y −2.0), X −0.6 … +3.4 | pad on the top at (+1.5, −1.4); lips over; to the ground | main stem down X ≈ +1.0 … +1.4 with 2 branches out to X −0.3 and +3.0 at z 3.5 and 2.0 | **34**: 28 on the face, 4 lipping onto the top, plus the foot spray (R1g) |
| R1g front-right foot spray | ground, X +2.6 … +4.8, Y −2.2 … −3.4 | | a ground stem from R1's foot round the corner | 6 |
| R2 right-end curtain | +X end (x +3.9), Y −1.2 … +2.0, wraps 0.3 onto the back face | pad on the top at (+3.3, +0.6); to the ground | main stem down Y ≈ +0.3, one branch to Y −0.9 | **24** (4 lipping onto the top) |
| R3 back curtain | back (y +2.0), X −3.2 … +0.9 | pad on the top at (−1.0, +1.4); to the ground | main stem down X ≈ −1.0, branches to X −2.6 and +0.4 | **24** (3 lipping) |
| R3g back-left foot spray | ground, X −2.2 … −4.4, Y +2.2 … +3.3 | | ground stem | 5 |
| R4 left-end patch | −X end (x −3.9), Y −1.4 … +1.2, z 0 … 2.4 | from the ground up (no pad; it starts at CB4) | a short climbing stem, one branch | **10** |
| Top spill (part of R1 and R2) | top, X +2.0 … +3.9 | | the lip segments | counted above |
| Spare | | | | about 7, for gaps the renders show |

**Total ≈ 110 leaves.**
- **Leaf tones by role and position** (§5.3), never by facing:
  - **lime** (about 40 %): the outer layer, upper halves and run tips, the lip and top-spill leaves;
  - **green** (about 35 %): the body of each run;
  - **dark** (about 25 %): the under-layer leaves nearest the stone, the lower third and the foot sprays.
- Stems must **show between the leaves**: the f34 T share is 1.4 % and the side's 4 %.

### 2.5 Rocks

| Rock | (x, y) | W × D × H | Evidence |
| --- | --- | --- | --- |
| RK1 front-left corner | (−4.45, −2.6) | 1.3 × 1.1 × 0.8 | f34's blue-grey rock (shade) |
| RK2 front-right corner, pair | (+4.0, −2.8) and (+4.7, −2.3) | 1.4 × 1.2 × 0.9; 0.8 × 0.7 × 0.5 | f34 beige pair |
| RK3 back, big | (−0.3, +2.95) | 1.9 × 1.5 × 1.3 | r34 big rock |
| Pebbles ×3 | (−2.6, −3.4), (+3.4, +2.7), (−4.7, +1.2) | 0.4–0.55 | small pale stones in every view |

- Chunky faceted boulders: a flat base, 10–14 broad facets, a sloping top, W : H 1.3–1.6.
- The same pale warm stone as the block. **Never eggs, never `K.hull_rock` balls.**

### 2.6 The six overlay parts (exported; each with an attach frame)

| Part | Size W × D × H | Build | Attach frame (origin, axes) |
| --- | --- | --- | --- |
| **MossCushionLarge** | 3.0 × 2.5 × 1.25 | CT1's shell (§2.3), 6–7 lumps | origin at the base centre, base plane z 0. Drop it onto any up-facing surface: rock tops, wall tops, ground. Sink 0.02–0.05. Fits slopes ≤ 15° |
| **MossCushionSmall** | 1.8 × 1.5 × 0.8 | the same recipe, 4–5 lumps | as above |
| **IvyCluster** (flat) | 3.2 W × 0.45 D × 2.9 H | an upright mat of **22 leaves** on a hidden stem fan (3 stems from one top pad), wide at the top, tapering to a hanging point of dark leaves | origin at the top-centre of the **back plane y = 0**, facing −Y; every leaf and stem sits in y −0.45 … 0. Place it back-flat against any wall face, its top at or just below the wall top |
| **IvyTendril** (segment) | 1.1 W × 0.4 D × 4.4 H | one straight-ish square stem, cut flat at the bottom, a pad at the top; **8 leaves** alternating, tips down | origin at the pad centre on the back plane (y = 0, z = 0 at the top, the stem running down −Z). Stack segments: the next segment's pad hides the previous flat-cut end ("flat junctions") |
| **IvyCorner** (angled) | arms 2.4 (top) and 2.8 (hanging) × 1.4 wide | an L spray: a top arm of **8 lime leaves** lying on the horizontal plane (z 0, y > 0), a hanging arm of **10 darker leaves** on the vertical plane (y 0, z < 0); one stem bent 90° over the edge with a pad on the top | origin on the **edge line** (the X axis), top plane +Y, face plane −Z. It fits any 90° outside top edge: wall tops, block lips, rock ledges (decision §8.6) |
| **IvyLeaf** (single) | 1.0 × 0.12 × 1.25 (with stalk) | one leaf (§2.4) plus a 0.35 stalk (Ø 0.07) | origin at the stalk base; the blade in the XZ plane facing −Y, hanging down. Scatter it on the ground or hand-place it |

### 2.7 Expected extents and screen checks

- **Extents:** X −5.5 … +5.45, Y −4.15 … +3.7, Z 0 … 6.05 (bbox ≈ 11.0 × 7.9 × 6.05). Core 7.8 × 4.0 × 4.8.
- **Checks on the renders** (floor hidden, `measure_render.py` with this folder's `m.py`):
  - **`f34_sheet (−47, 12)`** (probe az −40 … −55 × e 8 / 12 / 16, keep the best; §3.2):
    - W : H 1.20–1.36 (sheet 1.282);
    - G 52.6 ± 4, R 43.1 ± 4, T 1–3 %; fill 0.715 ± 0.05; top profile ±0.08 at f .1–.9;
    - x-fifth 4 green-dominant (the front curtain), x-fifth 5 mostly stone;
    - the −X end at the left in shade, the front face lit on the right.
  - **`r34_sheet (133, 12)`** (probe 125 … 140): W : H 1.14–1.30 (1.216); G 52 ± 5, R 43 ± 5; the +X end's full
    curtain at the left, the back curtain right of centre, the big rock at the base.
  - **`front_sheet (−44, 8)`**, the f34 redraw: W : H 1.17–1.32 (1.244); G 51.9 ± 4.
  - **`rear_sheet (128, 8)`**, the r34 redraw: W : H 1.11–1.27 (1.191); G 51 ± 5.
  - **`side (111, 8)`:** judged for content: the +X end's curtain top to ground, moss on top, a base cushion on the
    back side.
  - **`top (0, 89)`:** judged for content: the large cushion left of centre, ivy over the right third, rocks at the
    corners. Green share ≥ 55 % (sheet 74 %; ours shows more block top).
  - **True orthos** (`front (0, 0)`, `rear (180, 0)`): content only. Front: the front face with R1 on its right half;
    rear: the back face with R3 on its −X half.

## 3. View conflicts and resolutions

### 3.1 Sheet number

The header says "60 — MOSS AND IVY", "PAGE 60/132". INDEX row 56 lists `056.png` as "Moss and Ivy model study". → Our
number is **056** (file name, keys `m056_*`). Note the header in the export notes only.

### 3.2 Block proportion and the 3/4 cameras

- **Evidence.**
  - Both 3/4 views put a narrow shaded face on the image left and a broad lit face on the right. Their top-edge slopes
    give azimuth 46–47° in both and the same W : D (1.9–2.0).
  - The block widths (W 306–330 px, D 157–164) and the course heights agree.
  - The exploded's bricks are 2 : 1 "double bricks". The side cell is narrow.
  - A near-cube (W06's reading, and what the r34 alone might suggest from the face widths) needs the faces at ≈ 25°.
    That contradicts both slope measurements.
- **Resolution (decisions §8.1, §8.2).**
  - A **2 : 1 wall chunk**.
  - The f34 is **front-LEFT (az −47)**, so the narrow face is the −X end. The r34 is **rear-RIGHT (az +133)**, exactly
    180° round, so the narrow face is the +X end.
  - Mirroring the model to put the f34 at az +47 (the kit's usual side) would mirror every comparison, so we don't.
  - Record the probed best cameras.

### 3.3 Front, rear, side and top cells

- **Front and rear** are redraws of the 3/4 views at 44° and 52° off the broad face, not orthos. → Compare them at
  `(−44, 8)` and `(128, 8)`. True orthos are rendered for content only.
- **Side** shows the core narrower than any consistent reading (W : H 0.57 against 0.83 from the 3/4 views). Its
  content matches the +X end (a full curtain and a back-side cushion). → **Judged for content.**
- **Top** shows a 1.22 : 1 footprint, a moss-dominated top and rocks at four corners. It can't show a 2 : 1 block. →
  **Judged for content** (cushion left of centre, ivy over the right, rocks at the corners).

### 3.4 Brick count: four double bricks (exploded) vs a three-course wall (hero)

- **Evidence.** The exploded shows 4 double bricks (2 per course, 2 courses). Every assembled view shows three courses,
  three columns on each end and 3–4 bricks per course on the long faces.
- **Resolution.** **The hero governs: 3 courses × 3 rows, running bond** (§2.2). The exploded's bricks give the brick
  shape: chamfers, the facet crease and the 2 : 1 proportion. The parts shot shows four bricks pulled apart, as drawn.

### 3.5 Exploded positions vs the hero

The exploded moves things around: the curtain on the right end, cushions over the left. **The hero governs positions**
(§2.3, §2.4); the exploded gives shapes, counts and joints.

### 3.6 Stone colour: lit beige vs shaded mauve-grey vs the swatch

- **Evidence.**
  - The lit long faces are `#D3B595` (30°, 0.30, 0.82); the shaded ends `#746A6A` (≈ 0°, 0.09, 0.45); the S4 swatch
    `#BEB2A7` (29°, 0.12, 0.75).
  - Every view shows the same split by which way the face points to the light.
  - The notes say "pale, warm rock colour".
- **Resolution.** **One stone key** (`stone`, warm, hue 28–32°). The light makes the lit / shade split.
  - Calibrate the lit long-face median to `#D3B595`.
  - The shade must stay **warm-neutral, never mauve** (B ≤ G on every median; M034 / M037 / M055 ruling).
  - **Never paint the ends darker** (colour by facing, the 042 ruling).

### 3.7 Two greens or three for the ivy

- **Evidence.** The leaves come in lime (66–68°), mid green (88–95°, the single-leaf part and S2) and a dark
  blue-green (108–121°, S1 and every curtain's under-layer). Each leaf is one tone (close-ups 1 and 3).
- **Resolution.** **Three ivy keys**, assigned per leaf by layer and position (§5.3).

### 3.8 Ground and cast shadow

No soil patch in any cell: the cushions, rocks and sprays sit on the paper, with a warm glow and a pale shadow to the
left. → No patch. Render every `*_sheet` view with the floor hidden; the masks drop the glow and the shadow.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

1. `brick(L, D, H, chip=None)`: a chamfered brick (§2.2) as one closed shell, about 32 tris (36 with a chip).
   `stone_core()` lays the courses (§2.2) with jitter. Check: the parts shot's four bricks against
   `z_expl_stone.png`; the core against the f34 block outline.
2. `moss_cushion(w, d, h, lumps, seed)`: one closed shell (§2.3), 50–75 tris. Check against the two cushion cells: the
   lumpy scalloped outline, H : W 0.40–0.45, flat base.
3. `ivy_leaf(size)`: the 16-tri lens (§2.4); `stalk()`. Check against the SINGLE IVY LEAF cell: five points, two clear
   notches, a midrib crease.
4. `stem(points, r)`: square-section segments with flat junctions; `pad(center, normal)`.
5. `ivy_run(spec, solids)` places a run:
   - Walk the stem path on the stone faces. Ray-cast to the stone from 0.5 out, then offset by r + 0.01.
   - Place leaves alternately along it: stalk to the stem, blade ray-cast to the stone or the leaf under it, lifted
     0.01–0.03, then tilted.
   - Run the placement guard (§6).
6. `rock(spec)` ×4 + `pebble()` ×3: explicit ring stacks (base ring, widest ring at 0.3 h, shoulder ring at 0.7 h, a
   faceted top).
7. **Hero `OvergrowthRuinBlock`** = core + top cushions + base cushions + rocks + runs R1–R4 + sprays, joined into one
   object of closed shells.
8. **The six parts** (§2.6) from the same functions, each with its own attach frame.
9. **Parts shot** at (−47, 18), laid out like the exploded: four bricks apart, two cushions above, the R1 curtain to
   the right. Then the six overlay parts in a row like the sheet's right half: cushions L and S, cluster; tendril,
   corner, leaf. Gaps 1.5–2.

### 4.2 Stage 1 acceptance

1. **Overall read:** a pale three-course chamfered-brick wall chunk, lumpy lime cushions on top, four leafy ivy runs
   with brown stems lipping over the edges, cushions, rocks and sprays at the foot.
2. **f34_sheet**, **r34_sheet**, **front_sheet**, **rear_sheet**, **side**, **top** per §2.7.
3. **Close-up renders:**
   - `moss_cu (−30, 20)` cropped on CT4 and the front-left top edge, against close-up 1 (flat join, leaves lipping);
   - `pad_cu`, looking up at the front-face pad (−0.3, −2.0, 3.3) from below and in front (az −10, e −35), against
     close-up 2 (square chamfered pad, square stem, a leaf below);
   - `corner_cu (−80, 10)` on the front-right corner, against close-up 3 (layered leaves round the corner, 30–50 %
     overlap, stem showing).
4. **Each part** against its cell: the parts shot plus a single render per part at the cell's angle (about (−20, 20)).
5. **Contact counts** (§6): floating shells 0; buried dressing 0.
6. **Size** per §1.1. A **scale shot** with a 5.5-stud marker at (−2, −3.3) and one standing on the top at (+2.4, 0).

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Bricks (chamfered, 2 chipped) | 25 (incl. 2 middle bars) | 32–36 | 800–830 |
| Moss joint strips (optional, §8.9) | 0–6 | 12 | 0–72 |
| Top cushions | 4 | 45–70 | 210–240 |
| Base cushions | 6 | 40–60 | 270–300 |
| Rocks + pebbles | 5 + 3 | 24–30 / 12 | 160–180 |
| Ivy leaves (no stalk, §2.4) | ≈ 110 | 16 | 1760 |
| Stems (4 runs + 2 ground stems, one ring-stack shell each, ≈ 40 segments) | 6 | 8 per segment + 4 caps | 330–350 |
| Pads (the close-up one chamfered, the rest plain chamfer-top) | 1 + 4 | 20 / 12 | 68 |
| **Hero** | | | **≈ 3610–3720** (limit 4000; ceiling 3850) |
| Parts: CushionLarge / CushionSmall / IvyCluster / IvyTendril / IvyCorner / IvyLeaf | | | 70 / 48 / 22 × 16 + 60 ≈ 410 / 8 × 16 + stem 48 + pad 20 (+ 48 if stalked) ≈ 196–244 / 18 × 16 + 60 ≈ 350 / 22 (limit 1000) |

- **Spend headroom on the read:** first more leaves in the curtains' upper halves (the lime outer layer); then the
  optional joint moss (+72). Never subdivide.
- **If over 3850:** drop hidden under-layer leaves first (those whose centres are more than 80 % covered from both
  3/4 cameras). Then plain chamfer-top bricks for the middle bars (−20 each). Thin visible leaves last.

### 4.4 What to do better than W06

| W06 | This one |
| --- | --- |
| "smooth blocks" | chamfered bricks with a facet crease, running bond, jitter, a broken corner; dark V joints |
| "neon moss"; open-bottomed domes | closed lumpy cushions, lime over a 79° lower band, calibrated |
| "sparse ivy" | about 110 leaves in four runs, three tones, overlapping 30–50 %, lipping over edges, spilling onto the ground; stems showing |
| a near-cube block | the measured 2 : 1 wall chunk at the measured cameras |

### 4.5 Stages 2 and 3

- **Stage 2:**
  - every shell closed and manifold; 0 bowties (leaf tips, notches, chips and pad corners are the likely spots:
    `M.fix_bowties`);
  - **0 winding errors per shell** (STAGES "Consistent winding"): the lens leaves' bottom fans flip easily, so check
    every leaf;
  - no zero-area faces (thin stalks: keep every edge ≥ 0.02); n-gons only on flat brick and pad faces;
  - corners ≥ 3°;
  - origin bottom centre, transforms applied.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density. The exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box, sd ≤ 1.4)

| Swatch | Box | Hex | HSV | Use |
| --- | --- | --- | --- | --- |
| S1 dark green | (20,220,51,255) | `#467033` | 101°, 0.54, 0.44 | start for `ivy_dark` |
| S2 mid green | (55,220,86,255) | `#5B8C29` | 90°, 0.71, 0.55 | start for `ivy_green` |
| S3 lime | (90,220,121,255) | `#B3CE1F` | 69°, 0.85, 0.81 | start for `moss` and `ivy_lime` |
| S4 stone | (125,220,156,255) | `#BEB2A7` | 29°, 0.12, 0.75 | start for `stone` |
| S5 brown | (160,220,190,255) | `#8C5E33` | 29°, 0.64, 0.55 | start for `stem` |

### 5.2 Rendered regions (`samp.py`, `samp2.py`; median / v > .7 / lit quartile / shade quartile)

| Region | Median | v > .7 | Lit Q | Shade Q |
| --- | --- | --- | --- | --- |
| Stone, f34 all / r34 / rear / front | `#786E6F` / `#898178` / `#C1A888` / `#7E7474` | `#D1B292` / `#D2B495` / `#D4B99C` / `#D0B496` | `#D6B899` / `#D4B798` / `#D9BEA2` / `#D4B99C` | `#696261` / `#66615C` / `#67645E` / `#6F6866` |
| Stone lit faces (v ≥ .66), f34 / r34 / exploded | `#D1B292` (30°, .30, .82) / `#D1B394` / `#CDAF91` | | | |
| Stone shade faces (v < .66), f34 / r34 / exploded | `#746A6A` (0°, .09, .45) / `#726968` (6°) / `#7A6F6D` (9°) | | | |
| Notes stone icon | `#BCA898` (28°, .19, .74) lit | | | `#7F7069` |
| Rocks, f34 base right / r34 big | `#D1B28A` / `#CAAC8A` | `#D3B58E` / `#E6CBAD` | `#E3CBA5` / `#F9E7C6` | `#AA9B75` / `#72655B` |
| Moss, f34 top / f34 big base / r34 top / top cell | `#ADCA06` (69°) / `#B4CD04` (67°) / `#A5C508` / `#9FC104` | `#CCE119` / `#C8DB05` / `#CEE012` / `#C2DB0C` | `#EBF039` / `#E9EF17` / `#E5EE2E` / `#E1EC1D` | `#4E7701` (81°) / `#476E03` / `#467002` / `#4A7502` |
| Moss, by class (f34 top): lime 62 % / yellow-green 31 % | `#CEE113` (66°, .92, .88) / `#5D8802` (79°, .99, .53) | | | |
| Moss parts large / small | `#9ABE04` / `#97BC05` | `#B9D613` / `#BDD711` | `#D2E324` / `#D5E621` | `#4F7A02` / `#4A7703` |
| Ivy lime leaves (curtains, cu1, cu3) | `#CAE10E` (67°, .94, .88) / `#C6DC0B` / `#CDE116` / `#C4DA08` | | | |
| Ivy green leaves (85–100°) | `#417710` (91°) / `#52911C` / `#5D9A21` / single leaf `#5F9E33` (95°, .68, .62) | | | |
| Ivy dark leaves (≥ 100°) | `#19541A` (121°, .70, .33) / `#1D4F14` (111°) / `#1A541B` / `#266121` | | | |
| Ivy all-green, f34 curtain / r34 back / ivy cluster part | `#8FBB11` (76°) / `#87B90E` (78°) / `#69A514` (85°) | `#C7DF10` / `#C0D90F` / `#B6D60F` | `#E1EC16` / `#D6E713` / `#CDE210` | `#1C4A0C` / `#294909` / `#1B5413` |
| Whole-view greens, f34 / r34 | `#77A30A` (77°, .94, .64) / `#74A10A` (78°) | | `#DCE91A` / `#D0E213` | `#265508` / `#2B5109` |
| Stem, f34 / r34 / tendril part / notes icon | `#4D3407` (39°, .91, .30) / `#523D08` / `#58390C` / `#895A29` (31°, .70, .54) | | `#B4935F` / `#B0925F` / `#BB8320` / `#AC7539` | `#261801` / `#2A1C03` |

### 5.3 How the colour works

- **Stone:**
  - one warm stone (`stone`) on every brick and rock;
  - **deeper** (`stone_deep`, 30–35 %) on the bottom 0.35 of the bottom course (ground contact) and on the rocks'
    lowest 25 %;
  - **lighter** (`stone_light`, 30 %) on the top course's upper 0.4 and the rocks' tops (sun-bleached).
  - All by height. Lit / shade comes from the light only (§3.6).
  - Per-brick Tint ±0.04 held across the whole brick, so each brick reads as its own stone; broad noise 0.02.
- **Moss cushions:** `moss` (lime) on the upper 65 %, blending to `moss_deep` (79–82°) over the lowest 35 % by height
  within each cushion (steps 3). Per-cushion Tint ±0.03.
- **Ivy leaves:** one key per leaf, by layer and position:
  - `ivy_lime` (about 40 %): outer layer, upper halves, run tips, lip and top-spill leaves;
  - `ivy_green` (about 35 %): run bodies;
  - `ivy_dark` (about 25 %): under-layer leaves nearest the stone, the lowest third, the foot sprays.
  - Per-leaf Tint ±0.04.
  - **Never by facing**: a leaf's tone follows its role, whatever its normal.
- **Stems, stalks and pads:** `stem`; the pads a step lighter (`stem` with Tint +0.05, as close-up 2's pad reads
  lighter than its stem).
- **Hues stay apart:**
  - stone 28–32° (sat ≤ 0.32);
  - stem 30–38°;
  - moss 64–68° over `moss_deep` 78–84°;
  - ivy lime 65–69°, green 88–95°, dark 108–118°.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians, not swatches. `K.sample` kinds: `"stone"` for the stone (lit faces
reach s 0.30, so use `M.sample(..., kind="all")` on a lit-face crop if `"stone"` drops them), `"brown"` for the stem,
`"vivid"` / `"green"` for the greens.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m056_stone` | lit long-face median `#D3B595` ± 12 (f34 front face, r34 back face); whole-view median within 20 of the sheet's (f34 `#786E6F`) (start `#BEB2A7`) | 28–32°, 0.24–0.32 lit; **B ≤ G on every median** (never mauve) | bricks, rocks, pebbles | rough 0.9, metal 0 |
| `m056_stone_deep` | the shade quartile `#6F6866` ± 12, warm | 20–32°, sat ≤ 0.15 | bottom band 30–35 %, rock bottoms 30 % | rough 0.95 |
| `m056_stone_light` | lit quartile `#D9BEA2` ± 10 | 28–32° | top-course upper band 30 %, rock tops 30 % | rough 0.9 |
| `m056_moss` | moss lime class `#CEE113` ± 12; whole-cushion median `#ADCA06`–`#B4CD04` ± 15 (start `#B3CE1F`) | **64–68°**, ≥ 0.88 | cushion upper 65 %, joint strips | rough 0.95, low spec |
| `m056_moss_deep` | moss yellow-green class `#5D8802` ± 12 | **78–84°**, ≥ 0.90 | cushion lower 35 % | rough 0.95, low spec |
| `m056_ivy_lime` | lime-leaf class `#C8DE0E` ± 12 (start `#B3CE1F`) | **65–69°**, ≥ 0.88 | outer, upper, tip, lip leaves | rough 0.8, low spec |
| `m056_ivy_green` | green-leaf class `#4F8C1A` ± 12 (`#417710`–`#5F9E33`; start `#5B8C29`) | **88–95°**, 0.70–0.88 | run bodies | rough 0.8 |
| `m056_ivy_dark` | dark-leaf class `#1D5218` ± 10 (start `#467033`) | **108–118°**, 0.65–0.80 | under-layer, lower third, sprays | rough 0.85 |
| `m056_stem` | notes icon / S5: `#8A5C2E` ± 12 lit-side; in-hero median `#4E3608` ± 15 is shade (start `#8C5E33`) | 30–38°, 0.64–0.75, **R > G > B** | stems, stalks, pads | rough 0.9 |

**Calibration warnings:**
- **The kit studio lights both halves** (042, 047, 055). Calibrate `stone` so the **lit long faces** hit `#D3B595`.
  The shaded ends will read lighter than the sheet's `#746A6A`; record it, and don't darken the ends.
- **Stone must not go pink or mauve** (M034, M037, M055). The sheet's shade has R > G = B; ours keeps B ≤ G on every
  median.
- **Greens must not lean yellow** (047's "plants leaning yellow", 039's olive shade halves):
  - the whole-view green median in the f34 at **76–79°** (sheet 77°);
  - `ivy_green` ≥ 88°, `ivy_dark` ≥ 108°, `moss_deep` ≥ 78°;
  - the shade quartile of the whole view **82–90°** (sheet `#265508`, ≈ 92°).
  - Lime may be lime (65–69°), but no more than about 45 % of the leaf area.
- **Lime is not neon** (W06): `moss` and `ivy_lime` value ≤ 0.90, sat ≤ 0.95 after calibration.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Bricks:** `stone` base; `stone_deep` bottom band and `stone_light` top band by height, steps 3; the chip's
  broken faces a touch lighter (`stone_light` 40 %, fresh break).
- **Cushions:** `moss` → `moss_deep` by height within each cushion.
- **Ivy:** whole leaves, one key each by role; no blend across a leaf.
- **Rocks:** height bands within each rock.
- **Hard edges only** where materials meet: leaf | stone, cushion | stone, stem | stone, rock | ground.

### 5.6 Texture (Tint) and finish

- **Tint:** stone 0.04 per brick, 0.02 broad; moss 0.03 per cushion plus 0.02 per lump facet group; leaves 0.04 per
  leaf; stems 0.03 per segment. Never per-triangle confetti.
- **Finish:** stone rough 0.9; moss 0.95; leaves 0.8 (a slight sheen, as the sheet's leaf highlights show); stem 0.9.
  No emission, no metal.

### 5.7 Re-measure (final renders against the sheet, same masks)

- **Stone:** f34 lit-face median within 12 of `#D1B292`; hue 28–32°; B ≤ G.
- **Moss:** f34 top-cushion lime class within 12 of `#CEE113`; the cushions' shade quartile 78–84°.
- **Ivy:** f34 curtain lime class within 12 of `#CAE10E`, green class within 15 of `#417710`–`#52911C`, dark class
  within 12 of `#19541A`–`#1D4F14`. Class shares within ±10 of §1.2 (curtain: lime 47 / yellow-green 18 / green 17 /
  deep 18).
- **Whole-view green:** f34 median hue 76–79°, shade quartile 82–92°.
- **Stem:** T share 1–3 % in the 3/4 views; lit stem pixels 30–40°.
- **Shares** per §2.7.

## 6. Joins and contact (no floating dressing, no buried dressing)

- **Shells:** each brick, cushion, rock, pebble, pad, stem segment (or each run's stem as one ring-stack shell) and
  leaf (no separate stalk in the hero, §8.8) is its own closed shell. All are in one hero object.
- **Seats** per §2.1.
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**.
  - A shell floats if its nearest distance to every other shell and the ground is > 0.03, or if it doesn't chain to
    the ground.
  - The chains:
    - leaf (stalk notch) → stem → pad / stone → brick → ground;
    - top-spill leaf → stem or top face;
    - foot-spray leaf → ground stem → ground;
    - cushion → top face or ground;
    - brick → brick below → ground;
    - rock → ground.
  - **No hidden stems:** every stem segment must touch the stone or the next segment.
- **Count buried shells** (STAGES; 046 and 047 round 2 blockers): **0 dressing shells more than 0.05 inside stone**,
  by ray parity against the full stone (every brick and rock) **after the final placement step**.
  - **Use 047's guard from the start:** `_Solids` holds the bricks and rocks as built; three skewed rays, two of three
    agree; placement accepts ≤ 0.03. A leaf that still cuts after its retries is **dropped**, never kept.
  - **Ray-cast every leaf's 8 outline points** to the stone. The joints are the trap: the chamfer V under a leaf is a
    dip, and the next brick's chamfer edge is a ridge.
  - Cushions on the top must not sink into a joint V, so their base sits on the flat tops. Base cushions against the
    wall must stay ≤ 0.05 in.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no particles, no falling leaves, no spores, no insects.

- **Stage 5 (lighting): skip, and record why.** No emission, no lights.
  - Studio notes (Requires Manual Validation): the stone reads pale warm beige on lit faces and warm grey in shade,
    never pink; the moss stays lime, not neon; the ivy's three tones stay distinct under the game sun; leaves read from
    both sides (they are closed shells).
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** Not recommended: drifting leaves or spores (not on
  the sheet).
- **Collision (decision §8.10):**
  - hero `hull`: players stand on the top and walk round; the hull over the base dressing is a gentle skirt;
  - **all six overlay parts `none`**: they dress other assets, which own the collision (as 035's MossCap and 036 /
    039's foliage).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json`,
`art/blender/scripts/kit/` and the repo (`git grep`) for Moss, Ivy, Vine, Creeper, Ruin, Overgrown, Overgrowth:
- **W06:**
  - `MossAndIvy` and every `MossAndIvy*` (`…CornerPiece`, `…CornerWrap`, `…CushionLarge`, `…CushionSmall`,
    `…IvyCluster`, `…RockCap`, `…SingleLeaf`, `…Tendril`, `…WallStrip`);
  - the WIP names `MossCushionLarge`, `MossCushionSmall`, `IvyClusterFlat`, `IvyTendril`, `IvyCornerPiece`,
    `IvyLeafSingle` (m033's header notes W06 owns `MossCushion*`);
  - `HangingVine*`.
- **Other kit rows:**
  - V03 `HeartleafCreeper*`, `TrumpetVine*`;
  - R07 `CaveMoss*`;
  - W01 `BoulderMossCap`, `MossBoulder*`;
  - W16 `ColumnIvyOverlay`, `CourtyardFloorIvy*`, `CourtyardFloorOvergrown`;
  - W10 `RuinLeanTo*`, `RuinColumn*`, `RuinColumnIvy`;
  - W09 `StoneStairRuined`, W12 `GateRuined` / `DoubleGateRuined`.
- **Numbered models:**
  - 033 (moss names), 035 `MossyBoulder*` (`…MossCap`), 036 `MossyRockCluster*`, 055 `MossyHollowLog*`.
  - **089 "Ruin block wall"** is still to come and will likely want `RuinBlock*` / `RuinWall*`, so avoid those
    prefixes here.
- **`Overgrowth*` and `m056` occur nowhere.** (`overgrowth` appears only as a word in a W10 note.) `M.mk` guards exact
  names only.

| Object | Part | Why |
| --- | --- | --- |
| `OvergrowthRuinBlock` | hero: stone core, cushions, ivy runs, rocks | W06 owns `MossAndIvy*`. The family name "Overgrowth" says what the overlays are; 089 keeps `RuinBlock*` |
| `OvergrowthMossCushionLarge` | MOSS CUSHION (large) | the label |
| `OvergrowthMossCushionSmall` | MOSS CUSHION (small) | the label |
| `OvergrowthIvyCluster` | IVY CLUSTER (flat) | the label |
| `OvergrowthIvyTendril` | IVY TENDRIL (segment) | the label |
| `OvergrowthIvyCorner` | CORNER PIECE (angled) | the label |
| `OvergrowthIvyLeaf` | SINGLE IVY LEAF | the label |

- Palette keys `m056_*` (§5.4). Collection `Kit/M056 Moss and Ivy`. No VFX sockets.

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **core 7.8 × 4.0 × 4.8 (three 1.6 courses), moss to 6.0, overall ≈ 11.0 × 7.9 × 6.05, leaves
   0.8–1.1** (recommended: a ruin chunk just under head height that players jump onto; leaves read in-game). Or a
   waist-high 5.9 × 3.0 × 3.6 (leaves 0.7; the dressing gets fiddly). Or W06's near-cube 6.5 × 6 × 6.5, which
   contradicts the measured 2 : 1 (§3.2).
2. **Frame and cameras (§3.2):** **long faces ±Y; f34 front-LEFT at az −47, r34 rear-RIGHT at az +133** (recommended:
   both measured from the drawing, exactly 180° apart). Or mirror the model to put the f34 at the kit's usual +47 side,
   which mirrors every comparison.
3. **Front / rear / side / top cells (§3.3):** **front and rear compared as 3/4 redraws at (−44, 8) and (128, 8); side
   and top judged for content** (recommended).
4. **Bricks (§2.2, §3.4):** **3 courses × 3 rows in running bond, about 25 chamfered bricks** (recommended: every
   assembled view). Or the exploded's 4 double bricks (a much blockier wall, unlike the hero).
5. **Moss form (§2.3):** **closed, lumpy, faceted cushions, H : W 0.40–0.45, flat bases; 4 on top, 6 at the base**
   (recommended). Or clusters of overlapping lumps (more tris; risks M047's "balls").
6. **Corner piece (§2.6):** **wraps a horizontal outside edge** (a top arm on the top face, a hanging arm down the face:
   the "lip" every hero run shows; recommended). Or wraps a vertical outside corner (close-up 3's subject; the part
   cell reads as a top arm plus a hanging arm, so less likely).
7. **Pads (§2.4):** **five pads: one per run on the top faces, plus one fully chamfered pad pinning R1's left branch
   to the front face, which is close-up 2's subject seen from below** (recommended). The block has no overhang, so
   the close-up's "underside" can't be taken literally. Or only the four top pads (close-up 2 then has no counterpart).
8. **Leaf geometry (§2.4, §4.3):** **a 16-tri lens (8-point outline), ≈ 110 leaves, no separate stalk on hero leaves
   (the stalk notch seats on the stem); stalks only on the IvyLeaf part** (recommended: hero ≈ 3650). Or stalks on
   every leaf (+660 tris: over the 4000 limit unless about 35 leaves go). Or 12-tri leaves without notches (loses the
   ivy silhouette).
9. **Joint moss (§2.2):** **include 4–6 thin lime strips in the top joints if the budget allows after the leaves**
   (recommended: the f34 shows them). Or skip.
10. **Collision (§7):** **hero `hull`; all six overlay parts `none`** (recommended).
11. **Exported parts:** **the hero plus the six labelled overlays** (recommended). Don't export a brick: 089 will own
    wall blocks.
12. **Colour (§5):**
    - **stone** lit `#D3B595`, never mauve;
    - **moss** `#CEE113` over `moss_deep` `#5D8802`;
    - **ivy** lime `#C8DE0E`, green `#4F8C1A`, dark `#1D5218` (about 40 / 35 / 25 % of leaves by role);
    - **stem** `#8A5C2E`;
    - blended by height and role, never by facing (recommended).
13. **Stages 5 and 6:** **skip both, recorded** (recommended).
14. **Budget (§4.3):** **4000 limit, about 3610–3720 planned, ceiling 3850; parts under 1000** (recommended). The
    budget is tight because of the leaf count: every leaf must earn its place in a governing view.

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **Moss that reads as balls or bunches of balls (047 round 1 blocker; M036 / M038).** Each cushion is one closed,
   flat-bottomed dome, H : W 0.40–0.45, widest in its lower half, 4–7 lumps showing as a scalloped outline and broad
   facets. Never a sphere, egg, or cluster of separate gems.
2. **Spiky or edge-on leaves (039 round 1 blocker and round 2 leftover; 047 minor 3; 055 pitfall 11).**
   - The ivy leaf has five points but chunky lobes: notches 0.22 deep, lobes at least 0.3 W wide, no needle tips.
   - Wall leaves are within 75° of the f34 / r34 view directions. Top-spill leaves tilt up 25–40°.
   - Target: ≤ 12 % of leaf area within 12° of edge-on at f34 (−47, 12); 0 undersides showing.
3. **Floating leaves (035 / 036 round 1).**
   - 0 shells more than 0.03 from a neighbour, the stone or the ground. Every leaf's stalk on a stem, every stem on a
     pad or the stone.
   - No "hidden stems" and no ladders of leaves with gaps between them (036's FL6).
4. **Buried leaves (046; 047 round 2 blocker).**
   - 0 dressing shells more than 0.05 inside a brick or rock, by ray parity after the final placement, every leaf's 8
     outline points checked.
   - Joints and chamfers are the trap. Cushions sit on flat tops, not in joint V's.
   - Drop a leaf that still cuts after retries; never keep it.
5. **Plants leaning yellow (047 note 3; 039 olive shade halves).**
   - Whole-view green median in the f34 76–79°, shade quartile 82–92°.
   - A real `ivy_dark` (108–118°) under-layer on every run.
   - `moss_deep` at 78–84° on every cushion's lower band.
   - Lime ≤ 45 % of the leaf area.
6. **Neon moss and smooth blocks (W06, `MODEL_PROGRESS.md` row 65).** Moss value ≤ 0.90 after calibration. Bricks
   chamfered 0.16 with a facet crease, jitter and a broken corner.
7. **Sparse ivy (W06).** About 110 leaves in four runs. In the f34 the front curtain covers X −0.6 … +3.4 from top to
   ground with 30–50 % overlap, and x-fifth 4 is green-dominant (sheet G 37 % / R 7 % in that fifth).
8. **Stems hidden or as smooth tubes.** Square-section stems with flat-junction kinks, T 1–3 % in the 3/4 views; the
   pad and stem read in `pad_cu`.
9. **Colour by facing (042 ruling).** The stone's lit / shade split is the light: ends are not painted darker. Leaf
   tone follows role, not normal. `K.check` facing correlation < 0.5 per material.
10. **Mauve or pink stone (M034, M037, M055).** B ≤ G on every stone median; lit hue 28–32°.
11. **A near-cube block (W06's reading).** The core is 7.8 × 4.0 × 4.8, 2 : 1, compared at az −47 / +133.
12. **Winding (044) and bowties.** 0 faces wound against their neighbours per shell, especially the leaf lenses' bottom
    fans and chipped bricks; `M.fix_bowties`; corners ≥ 3°.
13. **Booleans.** None planned: bricks, chips, cushions, stems and leaves are explicit shells. If one is truly needed,
    run it at the origin on clean manifold inputs and save first (STAGES "Booleans").
14. **Names and scope.**
    - No `MossAndIvy*`, `MossCushion*`, `IvyClusterFlat`, `IvyTendril`, `IvyCornerPiece` or `IvyLeafSingle` (W06).
    - No `RuinBlock*` (keep for 089), `RuinColumn*` or `ColumnIvyOverlay`.
    - One agent per Blender session; no commits, pushes or exports in stage agents.
    - Don't edit the frozen shared helpers or `lib/vfx.py`; don't touch other models' collections.

## Decisions (main session, 2026-10-30)
All 14 recommendations are accepted.
1. **Size.** Core 7.8 × 4.0 × 4.8 (three 1.6 courses), moss up to 6.0, overall about 11.0 × 7.9 × 6.05.
2. **Cameras.** The f34 sits front-left at az −47, the r34 at +133. The model is not mirrored.
3. **Other cells.** Front and rear are compared at (−44, 8) and (128, 8). Side and top are judged on content only.
4. **Bricks.** About 25 chamfered bricks in running bond, three rows deep, never a smooth block.
5. **Moss.** Closed, flat-based, lumpy cushions with height about 0.40–0.45 of width. **Never balls.**
6. **Corner piece.** Wraps a horizontal top edge.
7. **Pads.** Five: four on the top faces and one pinning a branch on the front face.
8. **Leaves.** About 110 flat 16-tri five-point leaves, with no stalks in the hero; only the single-leaf part has a stalk. **Never spiky or edge-on.**
9. **Joint moss strips.** Only if budget is left after the leaves.
10. **Collision.** Hero `hull`; the six overlay parts `none`.
11. **Exports.** The hero `OvergrowthRuinBlock` plus the six `Overgrowth*` parts. Keys `m056_*`.
12. **Colour.**

    | Region | Colour | Notes |
    | --- | --- | --- |
    | Stone, lit faces | `#D3B595` | never mauve |
    | Moss | `#CEE113` over `#5D8802` | |
    | Ivy | `#C8DE0E` / `#4F8C1A` / `#1D5218` | about 40/35/25 % by layer |
    | Stem | `#8A5C2E` | |

    Blend by height and role, **never by facing**. Greens must not lean yellow.
13. **Lighting and VFX.** Both skipped, and recorded.
14. **Budget.** Ceiling 3850. If it runs over, cut the joint strips first, then leaves at the back.

**Packaging.** Every shell is closed and manifold, with **0 winding errors**. **No floating leaves.** **No leaf, stem or cushion more than 0.05 inside the stone.** Watch the brick joints, and ray-check every leaf after final placement. Each overlay part carries its attach frame and origin as described.
