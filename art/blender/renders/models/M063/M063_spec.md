# 063 Hanging Vine — spec

Reference: `art/blender/assets/references/063.png` (1024 × 1536 px). INDEX.md row 63: "Flintborn hanging vine model
study". The sheet's own header reads **"PAGE 59/132"** (top left), title **"HANGING VINE"**, footer "FLINTBORN —
INDIVIDUAL MODEL STUDY" (our number is INDEX's 063, §3.1).
Builder: `art/blender/kit/mcp/m063.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows no effect** (§7). The subject is
**one wall-mounted hanging vine**: a chunky faceted **stone attachment pad** (the thing it hangs from) with a **thick
woody stub slotted into a socket** in the pad, from which **two woody strands twist round each other** and hang about
5.5 studs down, carrying **three-leaf clusters of chunky five-point (ivy / grape) leaves** that alternate round the vine,
a few **thin green curling tendrils**, and a **tip cluster** at the bottom. It is a placeable overlay (like 056's ivy
parts): it carries an **attach frame on the pad's flat back face**, which goes against a wall, cliff, ruin or trunk.
The two "ASSEMBLED" cells (vines over a stone block) are context, not part of the hero (§3.8).

Sheet text (paraphrased):
- **Title block (top left):** "PAGE 59/132", "HANGING VINE"; blurb: thick vines carrying simple leaf clusters, placed on
  cliffs, ruins, trees and structures; modular and buildable, with easy connections.
- **Header palette (under the blurb):** five unlabelled swatches: dark green, mid green, bright yellow-green, beige grey,
  brown (§5.1).
- **"ASSEMBLED":** "FRONT THREE QUARTER" and "REAR THREE QUARTER": a three-course pale stone block with two vines on the
  front (one wrapping the right corner) and one on the back, leaf clusters spilling over the top, grass and leaves at the
  foot.
- **"ORTHOGRAPHIC VIEWS (SAME MODEL)":** "FRONT", "SIDE", "REAR", "TOP".
- **"EXPLODED PARTS & ASSEMBLY":**
  - **"PARTS (REUSABLE)":** "Attachment Pad (wall/rock)" (a cracked chunky stone block), "Vine Segment (straight)" (a
    slightly bent faceted stick with cut ends), "Vine Fork (T-joint)" (a Y of three cut sticks), "Leaf Cluster (3
    leaves)" (three lobed leaves on a short green stalk).
  - **"EXPLODED VIEW":** top to bottom: the pad with its stub and a leaf cluster round the joint; a straight segment; a
    fork whose side arm points up-left; a segment; a lower segment carrying two clusters; a tip cluster. Blue dashed
    arrows pull four clusters off the stick; small blue rings mark the joints between segments.
  - **"CONSTRUCTION CLOSE-UPS":**
    1. "TOP JUNCTION": the segment fits into the pad; leaves gather round the joint to hide it.
    2. "LEAF ATTACHMENT": a cluster joins the segment at one simple pivot (a blue pivot ring on the stalk root); the
       leaves are set a little off-centre and angled so they look natural.
    3. "UNDERSIDE VIEW": the pad seen from below: a flat underside with a simple socket that takes the segment; clean
       low-poly broad faces.
- **"MATERIAL PALETTE (SOLID COLORS)":** six labelled swatches: Dark Foliage Green, Mid Foliage Green, Bright Leaf Green,
  Light Leaf Green, Rock Beige Gray, Vine Brown.
- **"MODELING NOTES":** chunky low-poly stylised forms with broad flat-shaded faces; the vine is built from modular
  straight and T-joint segments with reusable leaf clusters; the pad is a simple rock piece so the vine can go on walls,
  ruins or cliffs; leaves are clean angular Flintborn shapes with no thin geometry; simple readable forms in solid
  colours, no textures, no noise.
- **Game context and the old kit:**
  - **W06 row 3 `HangingVine`** (`art/blender/scripts/kit/W06/hanging_vine.py`; manifests `art/roblox/kit/W06/manifest.json`
    and `art/roblox/kit/wip/W06_hanging_vine/manifest.json`; goals `art/blender/renders/kit/W06/hanging_vine_goals.md`)
    is the old kit's take on this subject. Its hero was a ruined wall chunk with two braided vines (8.2 × 6.9 × 4.8,
    3284 tris); its variant **`StraightVine`** is this sheet's ortho subject: a stone pad on top and a two-strand braid
    hanging ~8 studs, **2.24 × 9.38 × 1.67, 1128 tris** (the later W06 manifest has `HangingVineStraight` 3.76 × 11.81
    × 1.43, 1250 tris). Its goals used strand r 0.17, leaves 0.9–1.1, clusters every ~0.8, one colour per material
    (`w06_bark #8D6237`, `w06_ivy #66A828`, `w06_stone #B1ADA9`). `MODEL_PROGRESS.md` row 67: **"thin vine, few large
    flat leaves; plain pad"**; `art/reference/kit/CHECKLIST.md`: HangingVine 7/10.
  - **Related:** 056 Moss and Ivy (`OvergrowthIvyTendril` 1.55 × 0.35 × 4.3: a square stem with a top pad and eight
    single leaves; `OvergrowthIvyCluster`, `…Corner`, `…Leaf`); WorldModeling §8.3 "Heartleaf creeper" / §18 "vine is
    tangled spaghetti"; siblings 059 Grass Tuft (2.4 tall), 060 Broadleaf Fern (3.0), 061 Meadow Herb (2.2), 062
    Ground Scatter (1.1). §1.5 keeps 063 apart from them.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The page is cream
(`#FAF6ED`, every panel too); each piece has a thin white sticker halo and a soft warm cast shadow to its lower left
(`#E4D3C2`, h 30°, s .15, v .89). Measured grey rules (`lines2.py`): assembled panel x 438–1008, y 13–336; ortho panel
y 346–752 (title bar to ≈ y 380, cell labels to ≈ y 405), dividers x 266, 511, 756; exploded panel y 765–1337, dividers
x 260 (parts | exploded) and 586 (exploded | close-ups); close-up boxes x 600–853 at y 829–986, 1000–1157, 1172–1325;
palette / notes panel y 1347–1491, divider x 484; footer rule y 1512.
- **Cells** (`m.V`, `m.X`): f34 (440,58,724,333); r34 (726,58,1008,333); front (15,408,265,745); side (268,408,510,745);
  rear (514,408,755,745); top (759,408,1008,745); exploded (262,825,586,1330); parts icons (15,840,135,1330); cu1 "top
  junction" (601,829,852,986); cu2 "leaf attachment" (601,1000,852,1157); cu3 "underside" (601,1172,852,1325).
- **Swatches** (inner boxes, sd ≤ 1.6): header H1 (32,243,76,287), H2 (95,243,139,287), H3 (158,243,203,287), H4
  (222,243,265,287), H5 (284,243,329,287); bottom P1 Dark Foliage (32,1386,79,1433), P2 Mid Foliage (105,1386,152,1433),
  P3 Bright Leaf (178,1386,226,1433), P4 Light Leaf (251,1386,299,1433), P5 Rock (325,1386,372,1433), P6 Vine Brown
  (398,1386,445,1433).
- **Masks** (`cls()` in `m.py`, HSV, h in degrees; a 2 × 2 opening drops specks):
  - **G**, leaves, petioles and tendrils: h 50–170, s ≥ 0.30, v ≥ 0.12 (yellow-green lit leaves at h 55–75 included).
  - **B**, vine wood (strands, stub, cut caps) and deep warm shade: h < 50 or ≥ 340, s ≥ 0.33, v ≥ 0.08, plus v < 0.15.
  - **P**, the pad (`shares.py`): inside the pad window only (front (116,408,186,492), side (380,408,428,488), rear
    (590,408,660,492), top (855,412,945,500)): non-background, s < 0.27, v > 0.30, not G, not saturated B. Outside the
    window, grey is cast shadow and stays background. (The plain `S` class of `m.py`, s < 0.13, misses the pad's warm lit
    faces and catches shadow: don't use it for the pad.)
  - **Green tones** (`gtone`): nearest of the four green swatches in (h, v): D (98°, .49), M (85°, .65), Br (68°, .80),
    L (65°, .84).
  - Apply the same code to our renders (studio floor hidden, plain background: no shadow, so P can be taken over the
    whole frame there as "stone").

**Scratch study material** (no Blender) in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m063_study\`.
Run with `C:/Users/Orang/.local/bin/uv.exe run --no-project --with pillow --with numpy --with scipy python <script> < /dev/null`.
- **Helpers:** `m.py` (boxes, `cls`, `gtone`, `clsimg`, `hsv`), `zoom.py` (`zoom.py x0 y0 x1 y1 scale out.png [grid]`),
  `probe2.py` (`probe2.py x,y …` → hex and HSV), `lines2.py` (frame rules), `sw.py` (swatches), `man.py` (manifest
  names; `man.py Cand1 Cand2 …` lists owned names containing each candidate).
- **Measurements:** `measure.py` → `measure_out.txt` (bbox, W : H, fill, G / B shares, green tones, per-tenth width and
  brown centre / width; writes `cls_views.png`); `shares.py` → `shares_out.txt` (G / B / P with the pad window, per
  quarter of height; writes `cls2_<view>.png`); `samp.py` → `samp_out.txt` (class medians per view and per named
  region, green value bands); `pad.py` (pad segmentation attempt; superseded by `shares.py`); `expl.py` → `expl_out.txt`
  (exploded and parts blobs: bbox, W : H, principal L : W; segment widths).
- **Zooms:** `z_fs.png` (front + side, 2×, grid 50), `z_rt.png` (rear + top), `z_assm.png` (assembled), `z_front_top.png`,
  `z_front_bot.png` (4×, grid 10), `z_side_top.png`, `z_rear_top.png`, `z_top_top.png` (pad junction, 4–5×), `zr_mid.png`,
  `zs_mid.png` (the strand twist, 5×), `zp_front.png`, `zp_top.png`, `zp_parts_pad.png`, `zp_expl_pad.png` (pad), `z_expl.png`,
  `z_parts.png`, `z_cu.png`, `z_pal.png`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** a wall-mounted foliage overlay, placed often on ruins and cliffs: a light full asset (decision
  §8.14). **Budget: hero ceiling 2500 tris, plan about 2050–2300; every part under 1000.**
- **Overall read (check this first).** A **tall narrow hanging column, about 3.3 × as tall as wide from the front** (W : H
  0.306) and 3.7 × as tall as deep from the side (0.269):
  - at the **top right-behind**, a chunky beige-grey **stone pad** (a cracked faceted block about 1.4 wide × 1.75 tall),
    its lower front half hidden behind a dense **junction cluster** of five or six big leaves;
  - a **thick brown stub** rising in front of the pad's left half, its **oblique cut end** (light tan) showing near the
    pad's top;
  - below the pad, **two brown strands twisted round each other** like a rope, crossing about every 1.1 studs, swaying
    gently left and right and tapering to a point at the bottom;
  - **leaf clusters every ~1 stud**, alternating sides down the vine: left / right in the front view and front / back in
    the side view; each cluster is two or three **five-point lobed leaves** (one main pointed lobe, two side lobes, two
    small basal lobes) with a midrib crease and lobe facets;
  - **thin green tendrils** curling out of the vine in loops (two or three per view), and green leaf stalks;
  - a **tip cluster** of two or three leaves hanging below the strand ends.
  - It reads **green first, then brown, then the grey pad**: front G 72.3 %, B 18.9, P 8.8.
- **Focal silhouettes, in order:**
  1. The column of alternating leaf clusters with the twisted brown rope showing between them (the vine is visible down
     its whole length in every view).
  2. The stone pad at the top right with the dense leaf cluster round the stub.
  3. The cut stub end and the tip cluster; the tendril loops.
- **Target size: 7.5 tall (pad top to the lowest leaf tip) × 2.3 wide (X) × 2.0 deep (Y)** (decision §8.1). Tolerances:
  height ±0.3, width ±0.2, depth ±0.2. Pad **1.40 W × 0.95 D × 1.75 H**. Strands **Ø 0.24** each (pair 0.42–0.48
  across where side by side); stub **Ø 0.39**; leaves **0.62–0.95** across (median ≈ 0.78); clusters 1.15–1.45 across.
  - **How it was derived.** No piece has a real size, so the scale was fixed on the leaves. Measured at the front cell
    (hero bbox 100 × 327 px, `shares.py`): single leaves 27–40 px, clusters 50–60 px, pad 58–67 × 76 px, stub 15–17 px,
    each strand 10–11 px (`zr_mid.png`, `zs_mid.png`), the pair 17–22 px where side by side (`measure.py` band maxima).
    At **43.5 px / stud** the leaves are 0.62–0.92 (in the range of 056's ivy, 1.07, and 062's small leaves, 0.6–0.7)
    and the column is 7.5 tall.
  - **Why this size.**
    - Against the 5.5-stud character: **1.36 C tall** — a vine hung near the top of a ~7–8-stud ruin wall reaches down to
      about knee height; a character standing beside it sees the pad above head height (pad bottom z 5.75).
    - The assembled cells show the vine running the full height of a three-course block whose height is about eight
      leaf widths: a 7.5-stud vine on a 7–8-stud wall matches that read.
    - It hangs above all the ground siblings (059 2.4, 060 3.0, 061 2.2, 062 1.1) but uses the same leaf language: its
      leaves (0.62–0.95) are a step under 056's ivy (1.07) and 062's big leaves (1.85), the same chunky order.
    - The old W06 `StraightVine` was 9.4 tall with 0.9-stud leaves; ours is a little shorter and much fuller (≈ 30
      leaves instead of its "few large flat leaves").
    - At 6.0 tall the leaves drop to 0.5–0.75 (thin at distance, WorldModeling §18 "tiny details vanish"); at 9.0 the
      pad grows to 2.1 tall and the strands to 0.29, heavy against 056's 0.26 stems.
- **Build frame (= the attach frame):** front −Y, +X right, **the wall plane y = 0** (the pad's flat back face), nothing
  at y > 0. The vine axis at x = 0, y = −0.95 (the pad's front-face plane). Build with z = 0 at the lowest leaf tip, so
  the pad top is at z ≈ 7.5. Then put the object origin at the bbox bottom centre (`K.check`) and store the attach point
  and the offset (§2.6, decision §8.10).

### 1.2 Measured views (`measure.py`, `shares.py`)

| View (box) | Hero bbox (px) | W : H | fill | G | B | P | Green tones D / M / Br / L |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Front** (15,408,265,745) | 88–187 × 415–741 (100 × 327) | **0.306** | 0.534 | **72.3** | **18.9** | **8.8** | 37 / 41 / 20 / 3 |
| **Side** (268,408,510,745) | 341–427 × 415–737 (87 × 323) | **0.269** | 0.477 | 67.5 | 19.8 | 12.7 | 53 / 28 / 13 / 5 |
| Rear (514,408,755,745) | 580–680 × 415–741 (101 × 327) | 0.309 | 0.473 | 70.1 | 19.5 | 10.4 | 33 / 43 / 19 / 5 |
| Top (759,408,1008,745) | 819–936 × 425–728 (118 × 304) | 0.388 | 0.465 | 72.0 | 16.2 | 11.9 | 44 / 37 / 15 / 4 |
| f34 (context: block + vines) | whole cell | 1.109 | — | 65.7 | 18.3 | — | 35 / 26 / 22 / 16 |
| r34 (context) | whole cell | 1.112 | — | 64.9 | 14.6 | — | 49 / 21 / 12 / 18 |

- Shares are % of the silhouette (background, halo and cast shadow excluded). **Fill** = silhouette / bbox area
  (`measure.py`, which counts the shadow sliver beside the pad; ±0.03).
- **Per quarter of height** (top → bottom, `shares.py`): front G / B / P 58 / 14 / 28, 77 / 23 / 0, 75 / 25 / 0, 88 / 12 / 0;
  side 49 / 14 / 38, 74 / 26 / 0, 74 / 26 / 0, 84 / 16 / 0. The pad fills the top quarter; brown peaks in the middle
  half (the twist shows between clusters) and drops at the leafy tip.
- **Width profile** (silhouette width per tenth of height, fraction of W, top → bottom):
  - front .80 .92 .89 .83 .83 .88 .68 .79 .66 .56 (W = 2.30);
  - side .69 .82 .84 .69 .76 .86 .63 .65 .69 .53 (W = 2.0).
  The column is nearly parallel-sided and narrows only in the bottom fifth.
- **Brown centre** (vine centreline, fraction of W from the left, per tenth): front .55 .63 .55 .48 .57 .59 .50 .56 .57
  .57; side .56 .61 .59 .48 .52 .56 .55 .56 .58 .62 → a gentle S-sway of about ±0.18 in X and ±0.15 in Y round the axis.
  Brown row width (px) median 5–17, max 14–22: wide where the strands lie side by side, narrow (5–7) at the crossings.
- **Verifier tolerance** (front, side): G ±6, B ±5, P ±4 points; W : H ±0.04; fill ±0.06; quarters ±10; width profile
  ±0.12 per tenth; the top quarter's P ≥ 18 (the pad must show).

**Cluster positions** (sheet px centre → z = (741 − y) / 43.5; side: left of the vine = front −Y, right = back +Y):

| Cluster | Front (x side, y) | Side (y side, y) | z | Plan quadrant | Leaves |
| --- | --- | --- | --- | --- | --- |
| J junction | both sides, 432–500 (left-heavy) | front-heavy, 433–505 | 5.55–7.1 (centre 6.3) | front, left and right of the stub | 5–6 big (two clusters) |
| C1 | right, 528 | back, 526 | 4.90 | back-right | 3 |
| C2 (small) | left, 536 (tight to the stem) | — | 4.70 | left | 2 small |
| C3 | left, 577 (big) | front, 572 (big) | 3.80 | front-left | 3 (on the fork spur, §3.6) |
| C4 | right, 628 | back, 628 | 2.60 | back-right | 3 |
| C5 | left, 667 | front, 667 | 1.70 | front-left | 2–3 |
| C6 | right, 708 | back, 705 | 0.80 | back-right | 3 |
| C7 tip | centre, 725 (to 741) | centre, 720 (to 737) | 0.0–0.75 | below the strand ends | 2–3 |

- Spacing is about 1.0 stud; the front and side cells agree on every cluster's height and quadrant (they are true
  orthos of one model). Plus 3–4 small single leaves (0.35–0.45) tight to the stem (front x 147–165 y 475–500; x 112–132
  y 522–550) and 3 tendril loops (front left y 560–600; front right y 660–700; side front y 590–650, a long hanging curl).

### 1.3 Silhouette and composition per view

**Front (`z_fs.png`, `z_front_top.png`, `z_front_bot.png`) — governs the read and X positions.** A near-level view
(the pad's top face just shows: e ≈ 5–10°), lit from the upper right:
- the pad at the top right: an irregular six-sided block whose top edge slopes up to the right, its right face lit
  beige, a crack line across its front with a yellow-olive lichen fleck; its lower left hidden by leaves;
- the stub rising in front of the pad's left half (x 133–150), ending at y ≈ 423 in an **oval cut face** (lit
  `#D8953B`), so the stub's top is cut obliquely, facing up and forward;
- the junction cluster: two big dark leaves to the left (≈ 40 px each), a bright lime leaf in the centre-right, two more
  half behind the pad's right edge;
- the twisted pair from y ≈ 490 down: two flat-faceted brown strands, lit orange on their right flanks, crossing every
  ~45–50 px; the pair sways a little right at y 510–530 and left at y 560–580;
- clusters alternating right / left down to the tip; green tendril loops at the left (y 560–600) and right (y 660–700)
  of the strands; the strands taper and end inside the tip cluster at y ≈ 735–741.
- **Leaves** are chunky flat-shaded slabs: each lobe folds along its vein into a lit and a shaded facet; the outer edge
  has a few small points between the lobes; a thin darker edge band shows the thickness. The left-hand leaves read dark
  and the right-hand ones lime: that is the light (upper right), not a painted side (§3.11).

**Side (`z_fs.png`, `z_side_top.png`, `zs_mid.png`) — governs Y positions.** The pad at the right (= the back, +Y,
the wall side), the stub rising at the pad's front face and overlapping its silhouette (so it sits in a socket in the
front face, §3.3), clusters alternating front / back, the back clusters filling the gap between the vine and the wall
plane (the side bbox's right edge, x 427, is the pad's back face). The front leaves reach 1.1 in front of the vine axis.

**Rear (`z_rt.png`, `z_rear_top.png`, `zr_mid.png`).** The pad at the left (+X, mirrored correctly), but the stub and
the junction cluster are drawn **in front of** the pad, which is impossible from behind (§3.2). The strand twist is the
clearest here: two strands, each 10–12 px, crossing at y ≈ 495, 545, 600 (every ~52 px = 1.2 studs). Use for the twist,
the shares and content only.

**Top (`z_rt.png`, `z_top_top.png`).** Not a plan: a redraw of the front at a slight elevation (the vine runs the full
cell height, which a view from above can't show, §3.4). The pad at the upper right (+X, +Y) confirms the pad sits
behind-right of the stub. Content only.

**Assembled f34 / r34 (`z_assm.png`).** Context: a pale three-course block 6–7 leaves tall with two vines running from
the top edge to the ground on the front (one at the right corner) and one on the back, leaf clusters spilling over the
top edge, grass, loose leaves and pebbles at the foot. No pad shows (they are hidden under the top leaves). They show the
intended use and the read: thick twisted brown rope, dense alternating three-leaf clusters, chunky lobed leaves.

**Top junction (close-up 1).** From the front-left, close: the stub (`#935A23`, lit `#C28242`) rising beside the pad's
left face; five big leaves fanned round it at the pad's lower edge, covering the joint.

**Leaf attachment (close-up 2).** A cluster's green stalk leaving the vine at a blue pivot ring; three leaves fanned from
the stalk end, the biggest hanging down-right, all tilted differently.

**Underside (close-up 3).** The pad from below: a broad flat underside (beige, lit `#E4CDB8`) with the stub
(`#664A2A`) entering it from below near its front edge, leaves round the stub's foot. The pad is chunky, 10–14 broad
facets, the underside one big flat face.

### 1.4 Parts (exploded `z_expl.png`; parts `z_parts.png`)

The parts icons are drawn at their own scales; the exploded draws every piece about 1.4–1.5 × larger than the hero's
(clusters 70–95 px vs 50–60 in the front cell; segments 22 px wide vs the pair's 15–20). **The hero governs size, angle
and position (§3.9); the cells govern each part's shape and colour.**

| Part (label) | Parts box (px) | Cell W : H / L : W | Tone (median, lit) | Shape |
| --- | --- | --- | --- | --- |
| Attachment Pad (wall/rock) | (40,854,120,923) | 1.16 / 1.2 | `#BBA394`, lit `#DAC8BB`, shade `#797375` | a **chunky irregular block**, nearly a cube in the icon: chamfered corners, a sloping faceted top, the front face broken into 4–5 facets by **crack creases** (two cracks, one running down the front, one across), tiny **yellow-olive lichen** in the cracks (`#B5A470`–`#DDD792`); a flat back (the leader line points at it) and a flat underside (close-up 3) |
| Vine Segment (straight) | (53,944,107,1057) | 0.48 / 4.1 (projected, with the bend) | `#945B2D`, lit `#B47234`, shade `#5C3D28` | a **6-sided flat-faceted stick** with one gentle bend at about 0.55 L (≈ 15°), slight taper, **flat cut ends** with a lighter end-grain cap; brown row width 19 px |
| Vine Fork (T-joint) | (35,1077,120,1172) | 0.90 / 1.2 | `#905A2C`, lit `#BA783A` | a **Y**: a leg down and two arms up-left and up-right at about ±50–60° from vertical, all cut flat at the ends, the same section as the segment, a broad faceted junction |
| Leaf Cluster (3 leaves) | (32,1194,119,1284) | **0.97** | leaves `#6AA821`, lit `#98C71D`, shade `#408822`; stalk `#95C61B` | a short **green stalk** rising from the top (the pivot end); at its foot **two side leaves** spreading out and a little up (≈ ±100–110° from straight down) and **one bigger centre leaf** hanging straight down; each leaf five-pointed with a midrib crease |
| Exploded top module | (380,830,460,902) | 1.11 | | the pad with the stub let into its front-left and a leaf cluster round the joint; the stub's flat bottom end below the pad |
| Exploded stick chain | (336,912,429,1184) | 0.34 | `#814F26`, lit `#BE7C39` | segment → fork (arm up-left, carrying the mid-left cluster by an arrow) → segment → lower segment; blue rings at the joints |
| Exploded clusters | (306,927,375,989), (451,942,545,1026), (433,1066,517,1148), (293,1095,364,1168) | 0.97–1.12 | `#62A923`, `#65A417`, `#559E2A` | four three-leaf clusters pulled off with arrows (two upper, two at the fork) |
| Exploded tip | (345,1183,460,1325) | 0.81 | | the lowest segment with two clusters and the tip cluster below its end |

- **Leaf construction (all leaves):** a closed slab 0.05–0.06 thick. Outline in the leaf's own frame (stalk at the
  origin, main tip along +X): **five points** — main tip at 1.0 L; two side lobe tips at ±50–60°, 0.80 R; two basal lobe
  tips at ±110–120°, 0.55 R — with **notches** between them at 0.50–0.55 R (side) and 0.40 R (basal), a shallow stalk
  notch, and one extra small point on each side lobe's outer edge only on the bigger leaves (≥ 0.85) = 10–12 outline
  verts. Tip angles 45–60° (pointed but broad; never needles). Top face: a hub vert at the stalk end + one vein vert per
  main / side lobe at 0.5 R raised 0.02, so each lobe folds into two facets (the sheet's creases); bottom face flat or a
  single fan; a side band joins the top and bottom outlines. A slight cup: lobe tips 0.03–0.05 above the hub plane.
  About **40–46 tris** per leaf.
- **Strand construction:** a **6-sided tube** along a chain of straight pieces (§4.1): mitred rings at each station,
  no smooth sweep; Ø 0.24 tapering to 0.12 over the last 1.2 studs; the tips pointed (a 3-vert cone end) inside the
  tip cluster.
- **Stub:** the same 6-sided section at Ø 0.39, 1.75 long; the top end cut obliquely (35° to the axis, the cut face
  facing up and forward, −Y); the bottom end flat.
- **Fork spur (hero):** a 6-sided stub Ø 0.18, 0.40 long, leaving one strand at about 60° from it, cut flat; it carries
  C3's stalk.
- **Petiole / stalk:** a 4-sided prism Ø 0.08 → 0.06, 0.25–0.40 long, its root seated in the strand, its end the
  cluster hub (the pivot).
- **Tendril:** a 4-sided tube Ø 0.08 → 0.05, 0.8–1.3 long, 6–8 straight pieces bending into one loose curl or loop
  (radius 0.12–0.18) at the free end; it leaves a strand and curls out and down.
- **Pad:** a hull of 18–24 verts (1.40 × 0.95 × 1.75): flat back (y = 0) and flat underside; the top two facets sloping
  down to the front-left; chamfered vertical edges; two crack creases on the front and right faces (a shallow V of 0.03
  made by splitting a face and pushing the crease verts in); **the socket**: a vertical groove in the front face at the
  stub's x (§2.2), open at the bottom, 0.43 wide, 0.21 deep, up to 0.85 H. Never smoothed, never `K.hull_rock` balls.

### 1.5 How 063 differs from its siblings and the old kit (binding: the verifier checks these)

| | W06 `StraightVine` (old kit) | 056 `OvergrowthIvyTendril` | 059–062 | **063 Hanging Vine** |
| --- | --- | --- | --- | --- |
| Size | 2.24 × 9.38 × 1.67 | 1.55 × 0.35 × 4.3 | 1.1–3.0 tall ground plants | **2.3 × 2.0 × 7.5, wall-mounted** |
| Stem | loose two-strand braid r 0.17, "thin vine" | one square stem Ø 0.26 | stems, twigs | **two 6-sided woody strands Ø 0.24 twisted every ~1.1 (pair 0.42–0.48 wide), a Ø 0.39 stub in the pad's socket, one fork spur** |
| Leaves | "few large flat leaves", one colour | 8 single lens leaves | blades, kites, maples | **≈ 30 chunky five-point slab leaves in three-leaf clusters every ~1 stud, alternating round the vine, plus a dense junction cluster and a tip cluster** |
| Pad | "plain pad" | a 0.55 square plate | — | **a 1.40 × 0.95 × 1.75 cracked faceted stone block, flat back and underside, a socket groove** |
| Extras | — | — | — | **3 green tendril curls, green stalks** |
| Attach | wall side +Y | top-centre of the back plane | ground | **the pad's back-face centre, wall plane y = 0, nothing behind it** |
| Colour | 3 keys, no shades | 3 ivy greens | | **four greens by leaf role and position along the leaf, vine brown with a tan cut end and deeper upper wood, green stalks, warm beige stone with a deeper foot, lichen in the cracks** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, wall plane y = 0, z = 0 at the lowest leaf tip). Plan azimuths: 0° = +X,
counter-clockwise, 90° = +Y (back, the wall), 270° = −Y (front). Camera azimuths follow the kit's renders: `front` at
az 0, `side` at az 90 = the camera on +X looking −X (screen right = +Y, so the pad shows at the right, as on the sheet),
`rear` at az 180.

### 2.1 Stack (binding contact chain, top down; every seat ≤ 0.03 unless stated)

| Piece | Hangs from / rests on | Contact |
| --- | --- | --- |
| Pad | the wall (attach frame) | back face planar at y = 0.000 (±0.002); nothing else at y > 0.005 |
| Stub | the pad's socket groove | the stub's surface within 0.00–0.02 of the groove's back and side walls along its whole groove length (a socket fit, not a boolean); the stub never more than 0.03 inside the pad's solid |
| Strands A, B | the stub's flat bottom cap | each strand's top ring seated 0.03–0.05 into the stub's bottom cap; the two strands touch each other along the twist (gap 0.00–0.02, overlap ≤ 0.03 at the crossings) |
| Fork spur | strand A at z 3.95 | root seated 0.02–0.04 into the strand |
| Petioles / stalks | a strand (or the spur, or the stub for J) | root seated 0.01–0.03 into the wood; the stalk end is the cluster hub |
| Leaves | their cluster hub | the leaf's stalk notch within 0.02 of the hub (or 0.01–0.03 into the stalk end); leaves of one cluster may overlap each other by stacking (≤ 0.02 apart), never pass through each other |
| Small single leaves | a strand, by a short stalk (0.12–0.18) | as above |
| Tendrils | a strand | root seated 0.01–0.03 into the strand; the free curl touches nothing (allowed: it is part of a chained shell) |

### 2.2 Pad, stub and vine axis

- **Pad:** x −0.45 … +0.95, y −0.95 … 0, z 5.75 … 7.50 (top facets slope from z 7.50 at the back-right down to ≈ 7.20 at
  the front-left; the front-left vertical edge chamfered 0.15, the others 0.08–0.12). Facet count 10–14 visible faces.
  Crack creases: one down the front face from the top at x ≈ +0.45 to the bottom-right; one across the right face at z
  ≈ 6.6. Lichen: the 2–4 thin faces along each crease (§5.3).
- **Socket groove:** in the front face, centred at x = 0, 0.43 wide (x −0.215 … +0.215), back wall at y = −0.74 (0.21
  deep), from the underside up to z 7.24, its top end closed by a sloping face. Seen from below (close-up 3) it reads as
  a notch in the flat underside holding the stub.
- **Stub:** axis x = 0, y = −0.95 + 0.005 (its centre on the pad's front plane, half in the groove), z 5.55 … 7.31 (top
  of the oblique cut), Ø 0.39 (6-sided, one flat facing −Y). The cut face tilts 35° toward −Y, so it shows in the front,
  side and top views as on the sheet; the lowest 0.20 hangs below the pad.
- **Vine axis** (the twist centre), stations (z: x, y): 5.55: 0.00, −0.95; 4.9: +0.15, −0.93; 4.3: +0.05, −1.00; 3.8:
  −0.15, −1.05; 3.2: +0.05, −0.98; 2.6: +0.10, −0.92; 2.0: −0.10, −0.97; 1.4: +0.03, −1.02; 0.8: +0.05, −0.95; 0.30:
  +0.03, −0.93 (strand tips). A gentle S-sway (§1.2), never a straight pole and never a zigzag.

### 2.3 Strands (2) and the twist

- Two strands A and B, Ø 0.24 (taper to 0.12 from z 1.5 down), each centred **0.11 off the vine axis** on opposite
  sides, rotating round it: a **right-handed twist, full turn every 2.2 studs** (so in any side view the strands cross
  every 1.1 → five crossings between z 5.5 and 0.3).
- Stations **every 60° of twist (≈ 0.37 apart)**, straight pieces between them with mitred rings: each strand is about
  14–15 pieces. Add a ±0.02 random radial jitter per station so it reads hand-shaped, not machined.
- Twist phase: at z 5.5 strand A at plan az 180° (left, −X), B at 0° (right), so both strand tops sit side by side
  across the stub's flat bottom (they fit inside its Ø 0.39 cap: 0.11 + 0.12 = 0.23 > 0.195, so seat each 0.03–0.05
  into the cap and let them splay 0.03 outward just below it — or widen the stub's bottom ring to Ø 0.46; pick the
  cleaner, report).
- **Checks:** the strands touch at every station (gap ≤ 0.02); no strand face crosses into the other by more than 0.03;
  from the front and side the brown shows as a continuous rope between the clusters (B share 19 ± 5 %).

### 2.4 Clusters and leaves

Each cluster: a hub at the end of its stalk, which leaves the strand at the cluster's **plan azimuth**, pitched 20–40°
below horizontal; at the hub, two side leaves (tips spreading ±70–110° from straight down round the stalk) and one
bigger centre leaf hanging down (tip 15–30° off vertical, outward). **Leaf face normals point outward from the vine**
(along the cluster azimuth) with a 10–20° upward pitch; for clusters on the back half (plan az 10–170°) blend the normal
**35 % toward −Y** (away from the wall) so the leaves lie a little flatter against the wall plane and never face into it.
Never turn a leaf toward a camera (STAGES "Foliage reads from every azimuth").

| Cluster | Hub on | Hub z | Plan az | Stalk L | Leaves (span) | Tone role (§5.3) |
| --- | --- | --- | --- | --- | --- | --- |
| **J1** junction left | the stub, z 5.8 | 5.95 | 215° | 0.25 | 3: 0.95, 0.90, 0.85 (the two big dark leaves of the front cell + one below) | under-layer → dark bodies |
| **J2** junction right | the stub, z 6.0 | 6.25 | 320° | 0.25 | 3: 0.90 (lime, centre-right in the front), 0.85, 0.80 (half behind the pad's right edge, in front of its face: y ≤ −0.97) | outer → mid / bright, lime tips |
| **C1** | strand B | 4.90 | 50° | 0.35 | 3: 0.80, 0.75, 0.70 | back → mid body |
| **C2** small | strand A | 4.70 | 160° | 0.15 | 2: 0.45, 0.40 | small, tight to the stem → bright |
| **C3** (on the fork spur) | the spur's end | 3.80 | 215° | 0.30 | 3: 0.90, 0.85, 0.80 (the big left cluster) | outer → mid, bright tips |
| **C4** | strand B | 2.60 | 25° | 0.35 | 3: 0.80, 0.75, 0.70 | back → dark-mid |
| **C5** | strand A | 1.70 | 235° | 0.30 | 3: 0.75, 0.70, 0.65 | outer → mid |
| **C6** | strand B | 0.80 | 55° | 0.30 | 3: 0.70, 0.65, 0.65 | back → mid |
| **C7** tip | both strand tips | 0.55 | 280° (hanging) | 0.20 | 3: 0.65 (lowest tip reaches z 0), 0.60, 0.55 | young → bright, light tips |
| Singles S1–S4 | strands | 5.30, 4.20, 2.15, 1.20 | 345°, 135°, 300°, 120° | 0.15 | 1 each, 0.35–0.45 | bright |

- **Total ≈ 31 leaves** (27 in clusters + 4 singles). The azimuths follow the sheet's alternation (back-right / front-
  left, front and side cells agree) but rotate 20–40° between clusters so no two consecutive clusters line up along one
  diagonal (§3.12).
- **Clearances:** no leaf crosses y > −0.01 (the wall plane, minus a 0.01 margin); no leaf more than 0.03 inside the pad,
  the stub, a strand or another leaf; J2's right leaves lie in front of the pad face (y ≤ −0.97), not through it.
- **Shapes:** the centre leaf of each cluster is the biggest; leaves overlap their neighbours 15–30 % in the cluster's
  own view. Junction leaves cover the stub's foot and the groove's bottom from the front (close-up 1).

### 2.5 Tendrils (3) and the fork spur

| Piece | Root | Path | Length |
| --- | --- | --- | --- |
| **T1** | strand A at z 3.55 | out to −X and down, a loop of radius 0.15 at the end (front cell left, y 560–600) | 0.9 |
| **T2** | strand B at z 1.60 | out to +X and down, a curl (front cell right, y 660–700) | 0.8 |
| **T3** | strand A at z 2.40 | out to −Y (front) and down, a long hanging S ending in a curl (side cell, y 590–650) | 1.3 |
| **Fork spur** | strand A at z 3.95 | toward plan az 215°, 60° off the strand, 0.40 long, cut flat | C3's stalk leaves its end |

### 2.6 Attach frame, origin and expected extents

- **Attach point** `o["m063_attach"]` (object coordinates): the **centre of the pad's back face** (build (0.25, 0.00,
  6.62)); attach normal +Y (into the wall); up +Z. To place: put the attach point on the wall surface with the object's
  −Y facing out of the wall. Also store `o["m063_offset"]` = build-frame origin → object origin, and
  `o["m063_socket"]` = the stub's top-of-groove point (for chaining extra parts later). The object origin stays at the
  bbox bottom centre (`K.check`), as 056 did.
- **Extents:** X −1.20 (J1 / C3 leaf tips) … +1.05 (the pad's right face, C4 / C6 tips), Y −2.00 (C3 / C5 / T3 front
  tips) … 0.00 (the pad back), Z 0 … 7.50. Bbox about **2.25–2.35 × 2.0 × 7.5**; bbox bottom centre about (−0.08,
  −1.00, 0) in the build frame.
- **Checks on the renders** (floor hidden; `meas.py` copied from 061 / 062, pointed at this folder's `m.py` and
  `shares.py` masks):
  - **front_sheet (0, 6)** (probe e 0–12; keep the best) — governs: W : H 0.29–0.33 (sheet 0.306); G 72.3 ± 6, B 18.9 ±
    5, P 8.8 ± 4; quarters ±10 (top quarter P ≥ 18); width profile ±0.12 per tenth; cluster heights per §1.2 ±0.25; the
    pad at the upper right, the stub's cut end visible near the pad top; green tones D / M / Br / L within ±10 of
    37 / 41 / 20 / 3.
  - **side_sheet (90, 6)**: W : H 0.25–0.29 (0.269); G 67.5 ± 6, B 19.8 ± 5, P 12.7 ± 4; the pad at the right, clusters
    alternating front / back, nothing to the right of the pad's back face.
  - **rear_sheet (180, 6)**: content and shares (G 70.1 ± 8, B 19.5 ± 6); the twist with ≥ 4 crossings; the pad at the
    left (it hides the stub, unlike the sheet, §3.2).
  - **top_sheet (0, 89)**: content only (§3.4): the pad at the back-right, clusters round the vine, no bare sticks.
  - **context (−35, 15)**: two hero copies on a plain 6 × 3 × 7 box, attach points on its front face near the top
    (and one on the right face): compare the read with the f34 cell (thick rope, dense alternating clusters).

## 3. View conflicts and resolutions

### 3.1 Sheet number
- **Evidence.** The header says "PAGE 59/132"; INDEX.md row 63 lists `063.png` as "Flintborn hanging vine model study".
- **Resolution.** Our number is 063 (file name, keys `m063_*`). Note the header in the export notes only.

### 3.2 The rear draws the stub in front of the pad
- **Evidence.** Front, side and top agree: the pad sits **behind-right** of the stub (front: pad right of the stub; side:
  pad right = +Y; top: pad upper-right = +X +Y; the rear mirrors it to the left = +X). But the rear also draws the stub,
  its cut end and the junction leaves over the pad, which can only be true from the front.
- **Resolution.** Geometry from the front / side / top. From behind, the pad hides the stub's top half; the rear is
  checked for the twist, shares and content only.

### 3.3 "Slots into the pad" + "socket in the underside" + a cut end visible in every view
- **Evidence.** Close-up 1: the segment fits into the pad. Close-up 3: a flat underside with a socket taking the segment.
  The front, side, top and exploded all show the stub overlapping the pad's lower-left front and its oval cut end in the
  pad's upper half.
- **Resolution (decision §8.10).** A **socket groove** in the pad's front face, open at the underside (§2.2): the stub
  sits half in it, its oblique cut end at 0.9 of the pad's height facing up and forward. From below the stub enters a
  notch in the flat underside (close-up 3); from the front its cut end shows (close-up 1, the orthos). No boolean on the
  stub; the groove is part of the pad's hull. Fallback if the groove fights the hull: a plain front face and the stub
  pressed 0.03 into it (no deeper; the buried limit holds).

### 3.4 The "top" is a redraw of the front
- **Evidence.** The top cell shows the vine running the full cell height with its leaves seen face-on, exactly like the
  front; from above, a hanging vine would be a short blob under the pad.
- **Resolution.** Content only: the pad at the back-right and clusters all round. A true `top (0, 89)` render is made for
  the record, not scored on W : H.

### 3.5 Twisted pair (orthos) vs single sticks (exploded, parts)
- **Evidence.** Every ortho and both assembled cells show **two strands twisted together** (rear and side zooms: two
  10–12 px strands crossing every ~1.1). The exploded and parts draw **single** faceted sticks, 1.4–1.5 × the hero's
  scale, as wide as the whole pair (22 px exploded ≈ 15 px at hero scale ≈ the pair, 0.35–0.45).
- **Resolution (decision §8.4).** The **hero is the twisted pair**, built from short straight pieces (the "modular
  segments" idea, kinked, not a smooth helix). The **exported parts follow their cells**: `…Segment` and `…Fork` are
  single sticks at the stub's Ø 0.36–0.39, so a Studio builder can chain them into a simple vine of the same weight; the
  pad part has the same socket. The exploded shot is built from the parts (single-stick chain) as the sheet draws it.
  Alternative: export a `…TwistSegment` (one full turn of the pair, 2.2 long) as well (+≈ 150 tris; not on the sheet).

### 3.6 The fork doesn't show in the orthos
- **Evidence.** The exploded's fork has an arm up-left carrying the mid-left cluster; no ortho shows a side branch.
- **Resolution.** One short fork **spur** (§2.5) under C3, the big front-left cluster at z 3.8; its end hides under C3's
  leaves from the front, and shows a little from the left and below. The `…Fork` part is the full Y.

### 3.7 Leaves per cluster: "3 leaves" vs a dense junction
- **Evidence.** The part is a three-leaf cluster; the junction in every ortho shows five or six big leaves; the tip and
  C2 show two.
- **Resolution.** The junction is **two clusters** (J1, J2); C2 is a small two-leaf cluster; the tip a three-leaf
  cluster on the strand ends; 4 single small leaves on short stalks (the small leaves tight to the stem in the front
  cell). All leaves are from the one leaf function at different sizes.

### 3.8 The assembled cells show a stone block, several vines, grass and ground leaves
- **Resolution (decision §8.3).** Context only. The hero is **one vine on its pad**; no block, no grass, no ground
  litter. The `context` render puts copies on a plain box to compare the read. A vine draped over a wall top (the
  assembled heads) is a later variant, not this hero.

### 3.9 Exploded / parts scale vs the hero
- **Resolution.** The hero governs every size and position; the cells govern outline (five-point leaves and the three-
  leaf arrangement, the stick facets and cut ends, the Y, the pad's cracks and flat faces) and colour role. Parts are
  exported at hero scale: Pad 1.40 × 0.95 × 1.75; Segment Ø 0.36 × 1.8 long; Fork 1.5 W × 1.65 H; LeafCluster 1.50 W ×
  1.55 H (cell W : H 0.97).

### 3.10 Header vs labelled palette
- **Evidence.** The header shows five swatches; its third, `#C3D32A` (66°, .80, .83), lies between the labelled Bright
  Leaf `#ADC90F` and Light Leaf `#CBD738`. Its grey `#B6ADA5` and brown `#966533` match the labelled Rock `#B9B1A9` and
  Vine Brown `#956432` within 4.
- **Resolution.** Use the six labelled swatches (§5.1); the header's third swatch confirms the bright / light pair are
  close neighbours (light only on lobe tips, ≤ 5 %).

### 3.11 "Solid colours, no textures, no noise" vs the user's colour rule; lighting
- **Resolution.** Leaves blended by role (cluster position, layer) and by position along the leaf (stalk end → body →
  lobe tips); wood blended by position along the vine; stone by height in the pad's frame; broad Tint per piece
  (0.02–0.04), never per-triangle confetti (memory `lighting-not-paint`). The sheet is lit from the upper right (dark
  left leaves, lime right leaves, lit orange strand flanks, blue-grey pad shade): **the lighting does that; never paint
  by facing or by side**. Render every `*_sheet` view with the studio floor hidden.

### 3.12 The sheet's leaves alternate on one diagonal; the wall; "every azimuth"
- **Evidence.** Front and side agree: C1 / C4 / C6 are back-right, C3 / C5 front-left — all on the plan diagonal 45° /
  225°. Seen from front-left or back-right those would line up behind the vine. The hero is wall-mounted, so the back
  (+Y) hemisphere is never seen in game, but the sheet draws a rear view with leaves on both sides.
- **Resolution (decision §8.6).** Keep the sheet's quadrants, rotate each cluster 20–40° off the diagonal (§2.4), turn
  leaves outward (back-half leaves blended toward −Y). Run the eight-azimuth `vis.py` check: **binding in the five
  front-hemisphere views** (camera az 0, ±45, ±90): bare wood ≤ 30 % of the visible column, edge-on flat leaf area ≤ 10
  %, the rope visible between clusters; **content only in the three rear views** (az 135, 180, 225: the pad and the wall
  side; there, no view may read as a bare stick with flaps).

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

1. `leaf(size, cup, fold)` → one closed five-point slab (§1.4). Check against the cluster cell and close-up 2: five
   pointed lobes, the vein folds, visible thickness, ≈ 44 tris.
2. `cluster(spec)` → stalk + 2–3 leaves arranged as §2.4 (hub, side leaves, centre leaf). The part: check against its
   cell from the cell's camera (≈ (−15, 15)): W : H 0.97 ± 0.10, the stalk on top, the centre leaf largest.
3. `strand_chain(stations, r0, r1)` → a 6-sided tube through straight pieces with mitred rings (strands, stub, spur,
   segment, fork arms all use it). The twist: `twist_stations(axis_stations, offset 0.11, pitch 2.2, step 60°)`.
4. `stub()` → the Ø 0.39 piece with the oblique top cut and flat bottom.
5. `fork_part()` → the Y from three `strand_chain` arms meeting in a faceted junction (a small closed hull, the arms'
   ends seated 0.03 into it; or a merge-0 union at the origin, `m021._union_fine`). Check against the fork cell.
6. `segment_part()` → one stick Ø 0.36, 1.8 long, one 15° bend at 0.55 L, flat cut ends. Check against its cell.
7. `pad(socket=True)` → the cracked block with the groove (§1.4, §2.2). Check against the parts cell (near-cube read,
   cracks, lichen) and close-up 3 (flat underside, the socket notch).
8. `tendril(spec)` → the 4-sided curl (§2.5).
9. **Hero `TwistedVine`** = pad + stub + strands A / B + spur + 9 clusters + 4 singles + 3 tendrils, placed by §2, one
   object of closed shells. Then run the contact / wall-plane / bury reports (§6).
10. **Parts shot** (−15, 15) laid out like the parts column: Pad, Segment, Fork, LeafCluster, gaps 0.4.
11. **Exploded shot:** built from the parts as the sheet draws it: the pad with its stub and J cluster at the top; below
    it, with 0.35 gaps, Segment, Fork (arm up-left), Segment, Segment; four clusters pulled 0.6 out; the tip cluster at
    the bottom.

Reusable code: `m047._Solids`, `shells_report`, `contact_report`, `bury_report`, m038's `contacts()` (committed: import,
don't edit); 056's leaf placement push-out against solids and its attach-frame property pattern (`m056.py`, committed:
copy what you need). Copy, don't import, from uncommitted builders (m057, m060, m061). The 8-azimuth ray check: copy
`vis.py` from the scratchpad `m054_v3/` folder and make it mount-aware (the front-hemisphere / rear split of §3.12).

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a tall narrow column: the stone pad at the top right-behind, the thick stub with its cut end, a
   twisted brown rope hanging below it, three-leaf clusters alternating all the way down, curling tendrils, a tip
   cluster; ≈ 3.3 × as tall as wide from the front.
2. **front_sheet / side_sheet** per §2.6 (shares, quarters, W : H, width profile, cluster heights, green tones).
3. **rear_sheet / top_sheet / context** per §2.6 (content).
4. **Close-up renders:**
   - `junction_cu` (−35, 10), close on the stub and the pad's lower-left, against close-up 1: the stub in its socket,
     big leaves fanned round the joint.
   - `pivot_cu` close on C3's stalk root, against close-up 2: the stalk leaving the spur at one point, three leaves
     angled differently, no gap at the root.
   - `underside_cu` (0, −55) from below the pad, against close-up 3: a flat broad underside, the stub entering the
     socket notch, leaves round the stub's foot, nothing poking through the pad.
   - `twist_cu` (0, 5) close on z 2–4: two faceted strands crossing, touching, no gap of daylight between them except
     where the sheet shows it.
   - `leaf_edge` (90, 5) on a junction leaf: the slab thickness and fold.
   - `thumb`: the front at about 120 px tall: the pad, the rope and the alternating clusters still read.
   - **`spin` contact sheet: camera az 0 / 45 / 90 / 135 / 180 / 225 / 270 / 315 at e 10.** In every front-hemisphere
     frame the column reads as a leafy rope (never a bare stick with edge-on flaps); `vis.py` numbers per §3.12.
   - **`wall` check render** (90, 0) with a thin plane at y = 0: nothing crosses it.
5. **Contact counts** (§6): floating shells 0; buried 0; wall-plane crossings 0.
6. **Hero size** per §2.6, plus a **scale shot** with a 5.5-stud marker standing on the ground in front of a 7-stud
   plain wall box carrying the vine near its top (the pad bottom at z ≈ 5.75 above the marker's feet when the pad top is
   at the wall top − 0.2).

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Leaves, clusters (10–12-vert outline, folds, side band) | 27 | 40–46 | 1080–1240 |
| Single small leaves (10-vert, thinner band) | 4 | 30–36 | 120–145 |
| Strands A / B (6-sided, 14–15 pieces, pointed tips) | 2 | 175–190 | 350–380 |
| Stub (6-sided, 3 stations, oblique cap) | 1 | 36–44 | 36–44 |
| Fork spur | 1 | 18–24 | 18–24 |
| Stalks (4-sided, 2 stations) | 13 | 10–12 | 130–155 |
| Tendrils (4-sided, 6–8 pieces) | 3 | 48–64 | 145–190 |
| Pad (18–24-vert hull, groove, crack creases) | 1 | 90–120 | 90–120 |
| **Hero** | | | **about 1970–2300; aim ≤ 2300; ceiling 2500** |
| Parts: Pad / Segment / Fork / LeafCluster | | | 110 / 60–80 / 90–130 / 130–150 |

- **Over budget?** First drop the side-lobe extra points (12 → 10 outline verts), then the tendrils to 3-sided, then
  the strand stations to every 72°. **Never** flatten the leaves into cards, drop a strand (the twist is the defining
  feature), merge clusters into blobs, or thin the leaf count below 26.
- **Lean alternative** (decision §8.14): about 1650 tris: 10-vert leaves, 3-sided tendrils (2 of them), strand stations
  every 72°, singles dropped.

### 4.4 What to do better than W06 and recent foliage

| Earlier | This one |
| --- | --- |
| W06 `StraightVine`: "thin vine, few large flat leaves; plain pad" | Ø 0.24 strands (pair 0.45) — B ≈ 19 % of the front; ≈ 31 chunky slab leaves in clusters every ~1 stud; a cracked faceted pad with a socket |
| W06: one colour per material, no shade | four greens by role and position, vine brown with tan cut ends and deeper old wood, warm stone with a deeper foot and lichen (§5) |
| WorldModeling §18 "vine is tangled spaghetti" | two strands with a regular twist and a gentle sway; 3 tendrils only, each one curl |
| 056 r1: "leaves read as spiky stars", IvyLeaf "shallow notches" | five broad lobes, tips 45–60°, notches at 0.50–0.55 R; check the leaf against close-up 2 |
| 054 / 057 / 058: cards turned to the front / rear cameras, balls with flaps from the side | leaves turned outward from the vine by cluster azimuth (§2.4); `vis.py` over eight azimuths |
| 056 / 058: parts that don't read like their cells | each part rendered from its cell camera beside the cell (W : H, lobes, cut ends, the Y, cracks) |
| 035 / 036 / 046: floating or buried dressing | every leaf chained by stalk → wood → stub → pad; counts reported; nothing more than 0.03–0.05 inside anything |
| 054 m6: a proud trunk because the origin sat on other pieces | the attach frame on the pad back (y = 0 exactly), origin at the bbox bottom centre, offset stored |

### 4.5 Stages 2 and 3
- **Stage 2:**
  - Every shell closed and manifold, **0 bowties** (likely at leaf lobe tips, the pointed strand tips, stalk roots,
    the groove corners).
  - **0 winding errors per shell** (`bmesh.ops.recalc_face_normals` per shell, then `m047.shells_report`).
  - No zero-area faces; corners ≥ 3°; triangulate the leaf top / bottom fans and the pad's n-gons.
  - Origin at the bbox bottom centre, transforms applied, `m063_attach` / `m063_offset` / `m063_socket` re-checked after
    the origin move.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box)

| Swatch | Hex (HSV) | Use |
| --- | --- | --- |
| P1 Dark Foliage Green | `#4E7B33` (98°, .59, .48); header H1 `#4F7C34` | under-layer leaf bodies, leaf bases (`leaf_dark`) |
| P2 Mid Foliage Green | `#6EA522` (85°, .79, .65); header H2 `#70A524` | main leaf bodies (`leaf_mid`) |
| P3 Bright Leaf Green | `#ADC90F` (69°, .93, .79) | outer / young leaf bodies, lobe outer halves (`leaf_bright`) |
| P4 Light Leaf Green | `#CBD738` (65°, .74, .84); header H3 `#C3D32A` (66°, .80, .83) between P3 and P4 | lobe tips of sunny outer and tip leaves (`leaf_light`) |
| P5 Rock Beige Gray | `#B9B1A9` (30°, .09, .73); header H4 `#B6ADA5` | pad (`stone`; the rendered pad is warmer, §5.2) |
| P6 Vine Brown | `#956432` (30°, .66, .58); header H5 `#966533` | strands, stub, parts sticks (`vine`) |

### 5.2 Rendered regions (`samp.py`; median / lit quartile / shade quartile)

| Region | Median | Lit Q | Shade Q |
| --- | --- | --- | --- |
| All green: front / side / rear / top | `#67A416` (86°, .87, .64) / `#4F9116` / `#64A414` / `#5D9A14` | `#9AC812` (75°) / `#9AC610` / `#9EC912` / `#94C210` | `#2C6816` (104°, .79, .41) / `#296716` / `#376E0E` / `#2D650D` |
| Green value bands, front: v < .50 / .50–.65 / .65–.78 / ≥ .78 | `#2D6916` 26 % / `#559421` 25 % / `#79B514` 35 % / `#A4CF13` 14 % (side 30 / 41 / 16 / 12 %) | | |
| Leaf parts: cluster cell / exploded top-right / mid-left / top-left | `#6AA821` (88°, .80, .66) / `#62A923` / `#65A417` / `#559E2A` (98°) | `#98C71D` / `#9DCD21` / `#86BA15` / `#72B326` | `#408822` / `#469224` / `#387617` / `#29752C` |
| Close-up leaves cu1 / cu2 / cu3 | `#61A414` / `#7AB312` (81°) / `#446E04` (shaded) | `#A6CC13` / `#B2D11A` (70°) | `#1D500D` / `#23560B` |
| Brightest leaf accents (probes) | front tip-cluster leaf `#D6CB0E` (57°, .94, .84); junction lime `#9CC920` (76°); C1 lime `#9FD20D` (76°) | | |
| Stalk (parts cell) / tendrils (probes) | `#95C61B` (77°, .86, .78) / `#8CBE0E`, `#64AC2C` (94°) | `#A0CE1E` | `#8DC018` |
| All brown: front / side / rear / top | `#70491A` (33°, .77, .44) / `#6F481B` / `#724617` / `#6F4617` | `#C7832C` (34°, .78, .78) / `#CB812E` / `#CD842A` / `#BC7C23` | `#382308` / `#412808` / `#4C2F0B` / `#412807` |
| Vine mid: front / side / rear | `#6C4618` / `#6A431A` / `#764818` | `#C37E2A` / `#CD8232` / `#CD832A` | `#3A2308` / `#3E2608` / `#52320D` |
| Sticks: parts segment / fork / exploded / cu2 | `#945B2D` (27°, .70, .58) / `#905A2C` / `#814F26` / `#A26030` | `#B47234` / `#BA783A` / `#BE7C39` / `#C08040` | `#5C3D28` / `#58371C` / `#59391F` / `#583C27` |
| Stub: cu1 / cu3 | `#935A23` (29°, .76, .58) / `#664A2A` (from below) | `#C28242` / `#C48039` | `#422607` / `#382410` |
| Stub cut end: front / side / top | `#A66C29` (32°, .75, .65) / `#987322` / `#8A5825` | `#D8953B` (34°, .73, .85) / `#DC9B27` / `#C88627` | `#5F411E` / `#452D14` / `#6A4518` |
| Pad: front / side / rear / top | `#A4938A` (21°, .16, .64) / `#C8B09A` (29°, .23, .78) / `#B19B8C` / `#C3AFA1` (25°, .17, .76) | `#DFC7B0` / `#DDC3AC` / `#BFA895` / `#EBD6C2` | `#8D7C6D` / `#736B6A` / `#6A605A` / `#92837C` |
| Pad: parts / exploded / cu1 / cu3 underside | `#BBA394` (23°, .21, .73) / `#D3B8A1` / `#D0B59E` / `#DAC3AF` (28°, .20, .85) | `#DAC8BB` / `#DAC1AA` / `#DCC4AC` / `#E4CDB8` | `#797375` / `#AE998A` / `#94857B` / `#6D7484` (blue-grey: shade) |
| Lichen in the pad cracks (probes) | `#B5A470` (45°, .38, .71); lit `#DDD792` (55°, .34, .87) | | |
| Context wall (f34 / r34, not modelled) | `#98857E` / `#91878B` | `#EFD9C2` / `#E8D2BB` | `#69635F` / `#7B726B` |
| Cast shadow (not modelled) | `#E4D3C2` (30°, .15, .89) | | |

### 5.3 How the colour works

- **Leaves:** every leaf is blended along its own length (radial bands from the stalk notch, fraction of R), and its
  band set depends on its **role** (§2.4):
  - **under-layer** (J1, back-half clusters C1 / C4 / C6 — the leaves nearest the pad or the wall): base 0–0.25 R
    `leaf_dark`, body `leaf_dark` → `leaf_mid` blend over 0.25–0.70 R, lobe tips `leaf_mid`;
  - **outer** (J2, C3, C5): base `leaf_dark`, body `leaf_mid`, lobe outer 0.75–1.0 R `leaf_bright`;
  - **young / small** (C2, C7 tip, singles): base `leaf_mid`, body `leaf_bright`, tips `leaf_light`;
  - one leaf per cluster may step one tone lighter or darker than its role, so clusters don't look stamped.
  - A whole band (top facets, side band and underside together) takes one blend step; the lit / shaded facet contrast
    comes only from the light on the folds. Target shares on our front render (nearest-swatch, same `gtone`): D / M /
    Br / L within ±10 of 37 / 41 / 20 / 3.
- **Stalks and tendrils:** `stalk` along the whole piece; the tendril curl's last 0.2 one step toward `leaf_bright` (a
  young tip) by position; the stalk's root 0.04 next to the wood one step toward `leaf_dark`.
- **Vine wood (strands, stub, spur):** `vine` body; the stub and the strands' upper 25 % (z > 4.3, the older wood
  nearest the pad) blended one step toward `vine_deep`; the strands' lower 1.2 (the young taper) one step toward
  `vine_light`; the stub's oblique cap and the spur's cut end `vine_cut` (the end-grain role, not the facing) with a
  0.05 band next to each cap blended one step. A narrow strip (≤ 0.04) where a strand touches the other may take one
  step of `vine_deep` by **distance to the other strand** (a position rule, not facing); skip it if it reads as stripes.
- **Pad:** `stone` body; the lowest 0–0.20 H band (in the pad's own frame) and the groove's inner faces (by position in
  the groove volume) blended to `stone_deep`; the 2–4 thin faces along each crack crease `moss` (lichen) with a
  one-step blend into `stone` on their neighbours; broad Tint mottling. Never darken the pad's left or lower faces by
  their facing: the blue-grey shade on the sheet is the light.
- **Parts:** the same keys and rules (Segment / Fork: `vine` body, `vine_cut` caps; LeafCluster: one under-layer side
  leaf, one outer side leaf, an outer centre leaf).
- **Hues stay apart:** leaf_dark 96–104°, leaf_mid 84–90°, stalk 76–80°, leaf_bright 68–74°, leaf_light 62–67°, moss
  45–55° (s ≤ 0.42), vine 27–31° (v ≤ 0.60), vine_deep 27–31° (v ≤ 0.46), vine_light 30–34°, vine_cut 31–35° (s ≥ 0.65,
  v ≥ 0.72), stone 22–30° (s 0.12–0.20), stone_deep 20–28°.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians where the sheet gives them, swatches where it doesn't. `K.sample` kinds:
`"green"` for the greens and the stalk, `"vivid"` for leaf_bright / leaf_light, `"brown"` for the wood keys, `"stone"`
for the stone keys and moss (check with `M.raw_sample` on the swatch too).

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m063_leaf_dark` | P1 `#4E7B33` ± 12 (render check: the front v < .50 band `#2D6916` comes from it plus shade) | 96–104°, 0.58–0.68 | under-layer bodies, bases | rough 0.85 |
| `m063_leaf_mid` | P2 `#6EA522` ± 12 (= cluster cell `#6AA821`, front all-green median `#67A416`) | 84–90°, 0.76–0.84 | main bodies | rough 0.8, low spec |
| `m063_leaf_bright` | P3 `#ADC90F` ± 12 (front lit quartile `#9AC812`) | 68–74°, 0.85–0.93 | outer lobe halves, young bodies | rough 0.8 |
| `m063_leaf_light` | P4 `#CBD738` ± 12 | 62–67°, 0.70–0.80 | lobe tips of young / tip leaves (≤ 5 % of greens) | rough 0.8 |
| `m063_stalk` | parts cell stalk `#95C61B` ± 12 | 76–80°, 0.80–0.88 | stalks, tendrils | rough 0.8 |
| `m063_vine` | P6 `#956432` ± 12 (= parts segment `#945B2D`, cu1 stub `#935A23`) | 27–31°, 0.62–0.72 | strands, stub, spur, part sticks | rough 0.9 |
| `m063_vine_deep` | `#6E4520` ± 12 (between the sheet's mid `#70491A` and the parts shade) | 27–31°, 0.68–0.76, v ≤ 0.46 | stub, upper strands (blend), twist contact strip | rough 0.9 |
| `m063_vine_light` | `#A8743C` ± 12 | 30–34°, 0.60–0.66 | the young lower taper (blend) | rough 0.9 |
| `m063_vine_cut` | stub cap `#C88A3A` ± 15 (front median `#A66C29`, lit `#D8953B`; side lit `#DC9B27`) | 31–35°, 0.68–0.78 | cut ends (stub cap, spur end, part caps) | rough 0.85 |
| `m063_stone` | rendered pad medians `#C4B0A0` ± 12 (top `#C3AFA1`, side `#C8B09A`, parts `#BBA394`; swatch P5 `#B9B1A9`) | 22–30°, 0.14–0.20, R > G > B | pad body | rough 0.9, low spec |
| `m063_stone_deep` | `#A39286` ± 12 (front pad median `#A4938A`) | 20–28°, 0.15–0.20 | pad foot band, groove | rough 0.9 |
| `m063_moss` | crack lichen `#C2B676` ± 15 (probes `#B5A470` / `#DDD792`) | 45–55°, 0.34–0.42 | crack faces | rough 0.9 |

**Calibration warnings:**
- **The kit studio lights both halves** (042, 047, 054): calibrate to the medians, then check the green tone shares on
  the hero's own front render (D 37 / M 41 / Br 20 / L 3 ± 10). If D comes out under 27 %, the under-layer roles need
  more leaves, not a darker leaf_mid.
- **Greens must not lean yellow or olive** (047 "plants too yellow"): leaf_mid ≥ 84°, leaf_dark ≥ 96°; only leaf_bright
  and leaf_light sit under 75°; the front all-green median within 15 of `#67A416`.
- **The vine is a warm mid brown, not orange and not near-black:** the sheet's orange flanks (`#C7832C`) are lit
  facets and its `#382308` is shade. The cut end is the only near-orange tan.
- **The stone is warm beige, R > G > B, never lavender or blue-grey** (059 ruling; 056 "never mauve"): the sheet's
  blue-grey (`#6D7484`, `#797375`) is shade.
- **Lichen stays muted** (s ≤ 0.42): it must not read as a bright green moss stripe.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Leaves:** radial bands from the stalk notch (fraction of R), band set by role (§5.3).
- **Wood:** by z along the vine (upper deep → body → young light), cap → 0.05 band → body at the cut ends.
- **Stalks / tendrils:** root → body → curl tip, by position along the piece.
- **Pad:** by height in the pad's frame; crack faces → neighbours.
- **Hard edges only** where materials meet: leaf | stalk, stalk | wood, wood | stone (stub in the groove), leaf | stone.

### 5.6 Texture (Tint) and finish
- **Tint:** leaves 0.03 per leaf + 0.02 per band (neighbouring leaves differ a little); strands 0.03 per strand with a
  0.02 lengthwise variation (grain); stalks 0.02; pad 0.04 broad mottling. Broad, never per-triangle.
- **Finish:** everything matte: leaves 0.8–0.85, wood 0.9, cut ends 0.85, stone 0.9; low spec; no metal, no emission.

### 5.7 Re-measure (final renders against the sheet, same masks)
- **Green:** front median within 15 of `#67A416`; tone shares per §5.3; parts-shot cluster median within 12 of `#6AA821`.
- **Brown:** front B median within 15 of `#70491A` (lit quartile within 20 of `#C7832C`); part sticks within 12 of
  `#945B2D`.
- **Stone:** front / top P median within 12 of `#A4938A` / `#C3AFA1`, R > G > B.
- **Shares** per §2.6.

## 6. Joins and contact (no floating dressing, no buried dressing)

- **Shells:** pad, stub, strand A, strand B, spur, each stalk, each leaf, each tendril: closed shells, all in one hero
  object.
- **Chain** (each piece must chain by contact ≤ 0.03 to the pad, and the pad to the wall plane):
  - pad → wall (back face at y = 0); stub → pad (in the socket groove, gaps ≤ 0.02);
  - strands A / B → stub (tops seated 0.03–0.05 into its bottom cap) and → each other (touching along the twist);
  - spur → strand A; stalks → strand / spur / stub; leaves → their stalk end (notch within 0.02); singles → strands
    by short stalks; tendrils → strands.
- **No floating:** no leaf more than 0.03 from its stalk end or a neighbouring leaf it rests on; no stalk more than 0.03
  from the wood. **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**.
- **No buried dressing:** no shell more than 0.05 inside another: strand tops in the stub ≤ 0.05; stalk roots ≤ 0.03;
  leaf notches ≤ 0.03; the stub's surface ≤ 0.03 inside the pad; **no leaf, stalk or tendril inside the pad** (ray
  parity against the pad, the stub and both strands as solids, `m047._Solids`, after the final placement step).
  **Buried shells: 0** (the strand-top seats excepted at their stated depth).
- **Wall plane:** no vertex of any shell at y > 0.005; the pad's back face planar at y = 0 (a wall-plane report:
  max y per shell). Leaves on the back-half clusters keep ≥ 0.01 off the plane.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.
- **Parts:** each exported part is self-contained (the LeafCluster's leaves chained to its stalk; the Fork's arms to its
  junction; the Pad one shell).
- **Reports:** reuse `m047.shells_report`, `contact_report`, `bury_report`, and m038's `contacts()` (committed; import,
  don't edit). Add a `wall_report()` in `m063.py`.

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no particles, no falling leaves, no drips. The cast shadows and
halos are the illustration's.

- **Stage 5 (lighting): skip, and record why.** No emission, no lights. Studio notes (Requires Manual Validation):
  - on a wall in the game sun the leaves stay bright mid-green with lime outer leaves (not olive, not uniformly dark on
    the shaded side of a wall);
  - the pad stays warm beige (not blue-grey under a cool sky) and close to the wall stone it is placed on (056's ruin
    stone lit `#D3B595` is a near neighbour);
  - the vine stays a warm mid brown with the twist readable at 20–30 studs.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** The old W06 vines had none either. Swaying in wind
  or a drifting leaf would be a Studio-side choice (a scripted sway on the MeshPart), not a socket (decision §8.11).
- **Collision:** **`none`** on the hero and every part (CanCollide, CanQuery and CanTouch off): the vine is dressing on
  a wall that has its own collision; the pad is too small to matter (decision §8.8).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched all 2454 names in `art/roblox/kit/**/manifest.json` (`man.py`), the builders and the
repo text (`git grep`) for Vine, Hanging, Creeper, Ivy, Tendril, Pad, Twist, Braid, Climb, Ruin and the candidates:
- **W06:** `HangingVine`, `HangingVineAttachmentPad`, `HangingVineBranched`, `HangingVineCurvedDraping`,
  `HangingVineFork`, `HangingVineLeafCluster`, `HangingVineSegment`, `HangingVineStraight`; wip `StraightVine`,
  `BranchedVine`, `VineAttachmentPad`, `VineFork`, `VineLeafCluster`, `VineSegmentStraight`; `MossAndIvy*`, `IvyTendril`,
  `IvyLeafSingle`, `IvyCornerPiece`, `IvyClusterFlat`. **M056:** `OvergrowthIvyCluster`, `…IvyTendril`, `…IvyCorner`,
  `…IvyLeaf`, `OvergrowthRuinBlock`. **V03-family:** `HeartleafCreeper`, `HeartleafVineSegment`, `HeartleafLeafAttachment`,
  `HeartleafHangingLoop`, `HeartleafWallClimb`, `TrumpetVine*`. **Other:** `TwistedSnag*` (8 names), `WillowHangingLeafClump`,
  `RuinLeanTo*`, `RopeBridgeHangerRope`, `RopeCrossingHangerRope`, the `…Pad` names `NaturalRamp…LandingPad`,
  `WaterLily…Pad…`.
- **`TwistedVine`, `TwistedVinePad`, `TwistedVineSegment`, `TwistedVineFork`, `TwistedVineLeafCluster` and `m063` occur
  nowhere** (repo text, manifests, builders). No owned name is a substring of them and none is a substring of an owned
  name (`TwistedSnag*` shares only the word "Twisted"). Also free: `BraidedVine`, `RuinVine`, `WallVine`, `ClimbingVine`.

| Object | Part | Why |
| --- | --- | --- |
| `TwistedVine` | hero: pad + stub + twisted pair + spur + 9 clusters + 4 singles + 3 tendrils | the sheet's "Hanging Vine", whose defining read is the twisted rope; `HangingVine*` / `StraightVine` are W06's |
| `TwistedVinePad` | "Attachment Pad (wall/rock)" with its socket | the label |
| `TwistedVineSegment` | "Vine Segment (straight)" | the label |
| `TwistedVineFork` | "Vine Fork (T-joint)" | the label |
| `TwistedVineLeafCluster` | "Leaf Cluster (3 leaves)" | the label |

- Palette keys `m063_*` (§5.4). Collection `Kit/M063 Hanging Vine`. No sockets (§7). Attach properties `m063_attach`,
  `m063_offset`, `m063_socket` on the hero; `m063_attach` on every part (Pad: back-face centre; Segment: top end centre,
  axis −Z; Fork: top of the leg, axis −Z; LeafCluster: the stalk's top end = the pivot).

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **7.5 tall × 2.3 wide × 2.0 deep; pad 1.40 × 0.95 × 1.75; strands Ø 0.24 (pair ≈ 0.45); leaves
   0.62–0.95** (recommended: 1.36 C, a full-height vine on a 7–8-stud ruin wall; leaves in the kit's leaf scale).
   Alternatives: 6.0 tall (leaves 0.5–0.75, thin at distance) or 9.0 (the old `StraightVine`'s length; pad 2.1 tall).
2. **Names (§8):** **`TwistedVine` + `TwistedVinePad`, `…Segment`, `…Fork`, `…LeafCluster`** (recommended). Not
   `HangingVine*`, `StraightVine`, `Vine*` (W06) or `OvergrowthIvy*` (056). Alternative stem: `BraidedVine`.
3. **What the hero is (§3.8):** **one vine on its pad, no wall block, no grass or ground leaves** (recommended); the
   assembled cells are context and a `context` render.
4. **Stem (§2.3, §3.5):** **two 6-sided strands Ø 0.24 in a right-handed twist (full turn 2.2, crossings every 1.1),
   built from straight mitred pieces with a gentle S-sway, out of a Ø 0.39 stub** (recommended). Alternative (cheaper):
   one Ø 0.40 stick with spiral facet grooves (−≈ 200 tris; loses the defining twist).
5. **Pad and attachment (§2.2, §3.3):** **a cracked faceted block with a flat back (the wall) and flat underside, a
   socket groove in its front face open at the bottom; the stub sits half in it with its oblique cut end at 0.9 H
   facing up-forward** (recommended). Fallback: the stub pressed ≤ 0.03 into a plain front face.
6. **Leaves (§1.4, §2.4, §3.12):** **≈ 31 closed five-point slabs (0.05–0.06 thick) in 9 clusters (J1, J2, C1–C7) + 4
   singles; azimuths per §2.4 (sheet quadrants rotated 20–40°); normals outward, back-half leaves blended toward −Y;
   never turned to a camera** (recommended).
7. **Fork and tendrils (§2.5, §3.6):** **one short fork spur carrying C3; three green tendril curls** (recommended).
8. **Collision (§7):** **`none` on the hero and every part** (recommended).
9. **Comparison cameras (§2.6):** **`front_sheet (0, 6)` governs, `side_sheet (90, 6)` positions in depth; rear and top
   content (with shares on the rear); `context (−35, 15)` on a box; parts shot (−15, 15); exploded from the parts;
   `junction_cu`, `pivot_cu`, `underside_cu`, `twist_cu`, `leaf_edge`, `thumb`, `spin` (eight azimuths at e 10,
   binding in the front hemisphere), `wall` check, scale shot** (recommended). Floor hidden in every `*_sheet` render.
10. **Attach and origin (§2.6):** **wall plane y = 0 at the pad back, nothing behind it; `m063_attach` = the pad's
    back-face centre (normal +Y); origin at the bbox bottom centre; `m063_offset` and `m063_socket` stored**
    (recommended, as 056's overlay parts).
11. **VFX (§7):** **none; stages 5 and 6 skipped and recorded** (recommended).
12. **Exported parts (§3.5, §3.9):** **the hero plus the four labelled parts at hero scale: Pad (with socket), Segment
    (single stick Ø 0.36 × 1.8, one bend), Fork (Y, 1.5 W × 1.65 H), LeafCluster (W : H 0.97)** (recommended). Option:
    a fifth `TwistedVineTwistSegment` (one turn of the pair) for Studio chaining.
13. **Colour (§5):** **leaves `#4E7B33` / `#6EA522` / `#ADC90F` / `#CBD738` by role and along each leaf; stalks
    `#95C61B`; vine `#956432` with `#6E4520` older wood, `#A8743C` young taper and `#C88A3A` cut ends; stone `#C4B0A0`
    with a `#A39286` foot and groove; lichen `#C2B676` in the cracks** (recommended).
14. **Budget (§4.3):** **light full asset: hero ceiling 2500 (plan 1970–2300); each part under 1000** (recommended: 31
    slab leaves and two twisted strands need it). Lean alternative ≈ 1650 (§4.3).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **A thin vine and few flat leaves (W06 "thin vine, few large flat leaves; plain pad").** Two Ø 0.24 strands (the pair
   ≈ 0.45), B ≈ 19 % of the front; ≈ 31 slab leaves; a cracked faceted pad with a socket.
2. **A smooth helix or a straight pole.** Straight mitred pieces every 60° of twist, a gentle S-sway (±0.15–0.18), five
   crossings; never a perfect machined spiral, never a ruler-straight stick (WorldModeling §6.3).
3. **Spaghetti (WorldModeling §18).** Three tendrils, one curl each; no extra loose strands.
4. **Spiky star leaves (056 r1; WorldModeling §18 "foliage resembles crystals").** Five broad lobes, tips 45–60°, notches
   at 0.50–0.55 R, widest at mid-length; check against close-up 2.
5. **Flat cards (WorldModeling §6.1, §17.2; "no thin geometry" on the sheet).** Every leaf a closed slab 0.05–0.06 thick
   with lobe folds; `leaf_edge` shows it.
6. **Leaves turned toward the cameras (054 / 057 / 058).** Outward by cluster azimuth; `vis.py` at eight azimuths, binding
   in the front five: bare wood ≤ 30 %, edge-on ≤ 10 %.
7. **Leaves through the wall or the pad.** Wall-plane report: no vertex at y > 0.005; ray parity against the pad: 0 leaf
   verts inside.
8. **Floating leaves or stalks (STAGES; 035 / 036).** Every leaf chained by its notch to a stalk, every stalk seated in
   wood; floating shells 0, counted and reported.
9. **Buried pieces (046; 047 r2).** Seats at their stated depths; nothing else more than 0.05 inside; the stub in the
   groove, not sunk into the stone.
10. **Parts that don't read like their cells (056 / 058 blockers).** The LeafCluster at W : H 0.97 with the stalk on top
    and the centre leaf largest; the Fork a Y with cut ends; the Segment a faceted stick with one bend; the Pad a
    near-cube with cracks and a flat back and underside. Each rendered from its cell camera beside the cell.
11. **Colour by facing (042 ruling; 054 m9).** Leaves by role and position along the leaf; wood by z; stone by height;
    `K.check` facing correlation < 0.5 per material. The dark left / lime right of the sheet is its light.
12. **Olive greens (047), lavender stone (059 ruling), orange vine.** leaf_mid ≥ 84°; stone R > G > B; vine 27–31° and
    v ≤ 0.60 (only the cut end is tan-orange).
13. **Winding (044) and bowties.** 0 faces wound against their neighbours per shell; lobe tips, strand tips, stalk roots
    and the groove corners checked; corners ≥ 3°.
14. **Wrong attach or origin (054 m6).** The pad back exactly on y = 0; `m063_attach` re-checked after the origin move; a
    `context` render with the attach point on a box face shows the pad flush, no gap, no overlap.
15. **Names and scope.**
    - No `HangingVine*`, `StraightVine`, `BranchedVine`, `Vine*` or `OvergrowthIvy*` names.
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit the frozen shared helpers or other models' builders: import from the committed ones (`m038`, `m047`,
      `m056`); copy from `m057` / `m060` / `m061` if they are still uncommitted.
    - Don't touch other models' collections.

## Decisions (main session, 2026-10-31)
All 14 recommendations are accepted. The open questions are ruled as follows:
1. **Size.** 7.5 tall × 2.3 wide × 2.0 deep.
2. **Names.** Hero `TwistedVine`, parts `TwistedVinePad`, `…Segment`, `…Fork` and `…LeafCluster`, keys `m063_*`. Never `HangingVine*`, `StraightVine`, `Vine*` or `OvergrowthIvy*`.
3. **Hero.** One vine on its pad. The stone block is context for a comparison render only and is not exported.
4. **Stem.** The twisted pair of strands, which is the defining feature.
5. **Pad.** The socket groove, open at the bottom, with the stub seated in it.
6. **Leaves.**
   - Closed, chunky five-point slabs with thickness.
   - Turned outward from the vine and never toward a camera, with clusters rotated 20–40° off the sheet's diagonal.
   - **No flat cards and no stars.** Every leaf touches its stalk.
7. **Fork and tendrils.** One spur and three curls.
8. **Collision.** `none` everywhere.
9. **Cameras.** As recommended.
   - **Spin targets** are binding for the five front-half views, because the wall hides the back. The rear views must still show no flaps or floating pieces.
10. **Attach and origin.**
    - `m063_attach` is the centre of the pad's back face.
    - The origin is at the bbox bottom centre.
    - **Nothing behind the wall plane.**
11. **VFX.** None; stages 5 and 6 skipped and recorded.
12. **Exports.** The hero plus four parts.
    - Segment and Fork export as **single sticks of Ø 0.36**, as their cells draw them; the parts match their cells.
    - No fifth part and no drape-over variant; these are recorded as possible later additions.
13. **Colours.**
    - Use the colours as listed, by role and position, **never by facing**.
    - The vine bark is warm brown, not red.
    - The pad stone is warm beige, never lavender.
14. **Budget.** Light full asset: hero ceiling 2500 (plan 1970–2300), every part under 1000.
