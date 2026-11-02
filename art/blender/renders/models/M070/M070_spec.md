# 070 Ruined Lean-To — spec

Reference: `art/blender/assets/references/070.png` (1024 × 1536 px). INDEX.md row 70: "Ruined lean-to model study".
The sheet's header reads **"PAGE 68/132"** (top right), title **"RUINED LEAN-TO"**, subtitle "ENVIRONMENT PROP |
INDIVIDUAL ASSET STUDY", footer "FLINTBORN — INDIVIDUAL MODEL STUDY" (our number is INDEX's 070, §3.1).
Builder: `art/blender/kit/mcp/m070.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows no light or effect in any
assembled view** (its notes say "No baked lighting, effects or weathering textures"; one lantern appears only in the
exploded, §3.10). The subject is **a camp lean-to built into the corner of a ruined stone wall**:
- an **L of ruined masonry**: a long **back wall** of big chamfered pale stone blocks, **tallest left of centre** (eight
  courses) and **stepping down** to both ends, and a lower **left (−X) side wall** (five courses) ending at the front in
  a block column; broken corners, missing top blocks, dark joints, **ivy curtains** and **moss** on the blocks;
- **three square timber posts** (front-left, front-right, and one against the back wall) on stone footings, each with a
  **golden rope X-lashing** near its top, golden collars, and a **crossbeam** from the front-left post onto the side wall;
- a **cream canvas sheet** tied at three corners (front-left post, back post, front-right post) with its **fourth corner
  hanging low** at the front, right of centre, so the front edge reads as a **V**;
- a **red swallowtail banner with a white diamond emblem** on a crossarm at the front-right post, held by a dark pole;
- inside: a **brown leather bedroll** with golden end caps, a **golden sleeping mat** with blue-teal stripes, an
  **X-braced crate**, a small **open-frame side table**; a **hooped barrel** by the front-right post;
- **loose rubble blocks** round the front and grass and fern tufts at the wall feet.

Sheet text (paraphrased):
- **Title block:** "RUINED LEAN-TO", "ENVIRONMENT PROP | INDIVIDUAL ASSET STUDY", "PAGE 68/132", five header swatches
  (orange, cream, grey, green, **blue**; the blue is not in the palette panel, §5.1).
- **"FRONT THREE-QUARTER VIEW"** and **"REAR THREE-QUARTER VIEW"**. The first is a near-frontal high view (§3.2); the
  second is a true rear view from the back-right (§3.3).
- **"ORTHOGRAPHIC VIEWS"**: "FRONT VIEW", "SIDE VIEW (RIGHT)", "REAR VIEW", "TOP VIEW". The top view is mirrored (§3.4);
  the rear view draws two crates outside the back wall (§3.5).
- **"EXPLODED ASSEMBLY & PARTS"**, labels: "Ruin Wall Blocks (modular)", "Stone Rubble (assorted)", "Banner (cloth)",
  "Table / Bench", "Crate", "Canvas Canopy", "Upright Post (2x)", "Barrel". Several leaders point at the wrong piece
  (§3.9). Unlabelled: a crossbeam, a plank bench, a lantern on a bracket post, a bedroll, stone footings, grass.
- **"KEY CLOSE-UPS"**:
  - **"POST & CANOPY JUNCTION"**: a square post with a cracked top, a fat golden X-lashing (two crossing turns and
    horizontal wraps), a short square **toggle** lashed across the post; the canvas corner gathered and tied to the
    toggle; stone blocks behind.
  - **"UNDERSIDE VIEW"**: from below, a sloping timber with a square beam end crossing it, lashed with golden rope; the
    canvas corner gathered into a pale rope loop round the beam end.
  - **"WALL BLOCK DETAIL (CROSS-SECTION)"**: big near-cubic blocks with a clear **chamfer on every exposed edge**, dark
    joints between them, a light top face, chunky ivy leaves hanging from the top joint.
- **"MATERIAL PALETTE"**: Timber (Structure), Canvas (Cloth), Stone (Ruin), Foliage (Plants), Fabric (Banner).
- **"MODELING NOTES"** (paraphrased): chunky, low-poly, stylised geometry with broad flat-shaded faces; modular ruin
  blocks for reuse; simple planes for the canvas with clear thickness; consistent pole, rope and crate language; clean
  separation between structural parts; no baked lighting, effects or weathering textures; simple forms readable from
  mid distance.
- **Game context and the old kit:**
  - **W10 row 2 `RuinLeanTo`** (`art/blender/scripts/kit/W10/ruin_lean_to.py`; manifest `art/roblox/kit/W10/manifest.json`;
    goals `art/blender/renders/kit/W10/ruin_lean_to_goals.md`; compare `ruin_lean_to_compare.png`) is the old kit's
    version of a related sheet. **Exported** hero `RuinLeanTo` **13.72 × 8.02 × 10.02, 5822 tris, budget 8000,
    `precise`, one `heat_glow`**; parts `RuinLeanToWallBlocks`, `…CanvasCanopy`, `…UprightPost`, `…WallAnchor`, `…BedMat`,
    `…Peg`; variants `…SnowShelter`, `…TraderStall`, `…Abandoned`. `MODEL_PROGRESS.md` row 82: **"regular brick wall (ref
    broken ruin, moss/ivy); flat canvas"**; `art/reference/kit/CHECKLIST.md`: RuinLeanTo **6/10**. Its goals log: a
    verifier failed it for **thin flat walls, thin posts, a flat canopy and ivy as blobs**; it then got 3.2-deep walls,
    1.5-thick posts, a V-sagging canopy and hanging vine strands. Its stone was "lilac-grey" and its wood the shared
    `w10_wood #8A4A22`.
  - **Siblings:** M066 `CanvasShelter` (closest: canvas tied to posts with golden X-lashings, a banner on a rod, walk-under
    rulings), M064 `CanvasTent` (rulings: canvas blowing out under the key light, thin corners), M068 `TimberCabin`
    (layout model, banner and emblem recipe), M067 `TrestleTableSet` (furniture scale **table top 2.60, seats 1.50**),
    **M056 `OvergrowthRuinBlock`** (the ruin masonry, ivy and moss recipe this model reuses: §4.1). WorldModeling §13.1
    (timber), §13.3 (canvas: low-res grid, purposeful height moves, thin thickness; ties where the cloth attaches),
    §13.5 (ruins: broad pale blocks with simple joints, restrained wear; ruined variants remove selected stones; **ivy is
    a separate overlay and must not conceal the whole masonry**), §13.8 (crate, barrel, bed mat, banner recipes).
  - **Budget:** STAGES' full-asset ceiling **4000** (as 064 / 066); README's 8000 is for buildings. Open question 2.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is near-white
(`#F5F2EC`); pieces cast a soft **warm beige** shadow (h 26–38°, s 0.07–0.19, v 0.58–0.93), which the masks drop. Frame
rules (`lines.py`, ±2 px): header rule y 87; hero panels y 87–488, divider x 512; ortho panel y 488–785 (titles to
y ≈ 555; cell dividers x ≈ 281, 512, 764); exploded panel x 9–739, y 790–1287; close-up panel x 740–1014; palette panel
x 9–410, y 1288–1475; notes panel x 414–739; footer rule y ≈ 1505.
- **Cells** (`measure.CELLS`): f34 (12,122,510,486); r34 (514,122,1012,486); front (12,560,280,783); side
  (284,560,510,783); rear (514,560,762,783); top (766,560,1012,783); exploded (12,815,738,1285); cuA junction
  (755,845,1007,1007); cuB underside (755,1037,1007,1197); cuC wall block (755,1230,1007,1460).
- **Swatches** (inner boxes, sd ≤ 1.0): Timber (29,1338,91,1399); Canvas (103,1338,166,1399); Stone (178,1339,241,1399);
  Foliage (253,1338,316,1399); Fabric (328,1338,391,1399). Header row (sd ≤ 1.7): (764,40,800,75) … (971,40,1006,75).
- **Masks** (`cls.py`, HSV, h in degrees):
  - **BG** paper: s < 0.07, v > 0.93; **SH** cast shadow: h 26–38, s 0.07–0.19, v 0.58–0.94, not C. The silhouette is
    everything not flood-filled from the cell border through BG ∪ SH (so the floor shadow under the canopy is dropped,
    as our floor-hidden renders drop it). A few stone highlights near paper white stay in BG (≤ 4 %).
  - **W** timber and warm shade: (h < 48 or ≥ 345), s ≥ 0.45, v ≥ 0.15, not B / R; plus warm s ≥ 0.28 with v < 0.62.
  - **R** golden (rope, mat, bedroll caps, lit cut ends): h 32–55, s ≥ 0.42, v ≥ 0.62, not G.
  - **C** canvas: h 30–62, s 0.10–0.42, v ≥ 0.90. **B** banner red: (h ≥ 345 or < 10), s ≥ 0.60, v ≥ 0.35.
  - **G** foliage: h 55–170, s ≥ 0.30, v ≥ 0.15. **T** blue-teal (mat stripes): h 170–235, s ≥ 0.25.
  - **K** dark: v < 0.22, not W / B / G (outlines, joints, hoops, pole). **S** stone: everything else in the silhouette
    (warm pink-grey lit faces, lavender-grey shade).
  - Apply the same code to our renders (studio floor hidden, plain background).

**Scratch study material** (no Blender) in `<temp>\m070\` (the session scratchpad). No Pillow on this machine: the
scripts use Blender's bundled Python (`<blender dir>/5.2/python/bin/python.exe -I <script> < /dev/null`, numpy only)
with the small PNG reader / writer `png.py` (from the 067 study); `load.py` caches the sheet as `sheet.npy`.
- **Helpers:** `m.py` (HSV, `hexs`, `hsvs`), `cls.py` (masks; `cls.py x0 y0 x1 y1 scale out.png` writes a class map),
  `zoom.py` (`zoom.py x0 y0 x1 y1 scale out.png [grid]`), `probe.py` (`name=x0,y0,x1,y1` → median hex and HSV ranges).
- **Measurements:** `measure.py` (bbox, W : H, fill, class shares), `prof.py` (top profile per column: object, wood,
  stone, canvas tops), `bb.py` (class boxes, ground-plant share of G), `lines.py` (frame rules).
- **Colour:** `sw.py` (swatches), `samp.py` (class medians per cell and per named region, lit and shade quartiles).
- **Zooms:** `z_f34.png`, `z_r34.png` (2×), `z_fs.png`, `z_rt.png` (3×, ortho pairs), `z_front.png`, `z_side.png` (4×,
  grid 10: the ortho numbers below), `z_f34_mid.png` (4×), `z_f34_right.png`, `z_ban.png` (3×), `z_f34_back.png`,
  `z_r34_lamp.png` (6×), `z_props.png` (4×), `z_ex_l.png`, `z_ex_r.png`, `z_cu.png` (2×); class maps `c_f34.png`,
  `c_fs.png`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** a walk-in camp structure with its masonry and dressing: **full asset, hero ceiling 4000 tris,
  plan 3800–3950; every part under 1000** (decision §8.2; open question 2).
- **Overall read (check this first).** A **pale pink-grey block ruin** in an L (a long, stepped back wall and a lower
  left side wall), with **orange timber posts and a cream canvas** leaning off it, a **red banner** at the right, and
  **lime ivy** spilling down the tallest part of the wall:
  - **stone first** (f34 S 40.5 %), then **timber** (W 25.1: posts, crate, barrel, bedroll, table), then the **cream
    canvas** (C 11.8), **foliage** (G 10.5, about 70 % ivy and moss on the walls, 30 % ground tufts), the **red banner**
    (B 4.3) and **golden rope and mat** (R 2.5).
- **Focal silhouettes, in order:**
  1. The stepped broken skyline of the back wall, tallest left of centre, with the ivy curtain falling from its top; the
     lower side wall ending in a block column at the front-left.
  2. The canvas: three high tied corners and the low hanging front corner; the three posts with their X-lashings.
  3. The banner at the right; the bedroll, mat, crate, table and barrel inside; rubble at the front.
- **Target size (decision §8.1), scale 0.0816 stud per front/side-cell pixel:**
  - **FR post top 12.0** (147 px); **FL post top 9.35** (114.5 px); **back post top 11.1** (136 px).
  - **Back wall** courses of **1.65**: **eight courses (13.2) at its tallest**, x −4.0 … +1.4 (164 px → 13.4); **−X side
    wall five courses (8.25)** (93–98 px → 7.6–8.0, top block chipped).
  - **Canvas ties:** FL **8.0** (97 px → 7.9), back post **9.9** (121 px), FR **9.2** (113 px); **hanging corner C4
    6.6** (sheet 62 px → 5.1; raised for the walk lane, decision §8.5).
  - **Banner** 2.1 wide (26 px), top 9.2, tails at 3.0 (76 px long).
  - **Footprint:** walls x −9.6 … +5.2, y −4.2 … +5.4; posts x −5.9 / −1.0 / +5.9; **hero ≈ 21.0 W × 13.1 D × 13.2 H**
    with banner and rubble (§2.11).
  - Tolerances: post tops ±0.2, wall course tops ±0.1, tallest course 13.2 ± 0.2, canvas ties ±0.2, banner ±0.2.
  - **How it was derived.** No piece carries a size; the front, side and rear cells are drawn at one scale (the tallest
    wall is 162–164 px in all three, the FR post 143–147 px in front and side), so they set the heights; the front cell
    sets X, the side cell sets Y.
    - Front cell (`z_front.png`, `prof.py front`): ground y 752 (post footings' bottoms). FR post x 216–229, top 606;
      FL post x 72–83, top 637.5; back post x 134–141, top 616. Canvas ties: FL y 655, back y 631, FR y 639; **the
      lowest canvas corner y 690 at x 166** (between the back post and FR). Stone tops by column: x 21–56 (−X wall seen
      end-on) 654–660; x 56–72 625–640; x 76–88 611–618; **x 92–164 585–590 (tallest)**; x 168–176 612–623; x 180–212
      631–640 (the back wall's +X end); x 216–229 the FR post. Banner x 236–262, y 639–715; crossarm y 630–634 to x 264;
      a dark pole x 232–240 from the banner's foot to the ground. Barrel x 194–215, top 711; side table x 145–172, top ≈
      712 (30 px tall); crate face x 82–115.
    - Side cell (`prof.py side`): ground 750; FR post x 328–344, top 607 (143 px); canvas from the FR lashing (y 640)
      falling to ≈ 655–680 toward the back; wall profile behind: x 396–420 top 640 (9.0), x 424–440 top 615 (11.0),
      **x 444–492 top 586 (13.4)**.
    - Rear cell (`prof.py rear`, camera on +Y, screen right = −X): tops 617 (x 544–574, the +X end), 639, 615,
      **588 (x 634–682, tallest)**, 615, 637, 667 (x 718–730, the −X end), rubble beyond: the front profile mirrored
      (tallest 70–118 px from the −X end in both).
    - **Scale:** the FR post set to **12.0**, M066's tall-post height (0.0816 stud / px). Then the side table is 2.45
      (kit table top **2.60**), a wall course 1.63–1.71 (M056's ruin course 1.6), the mat 5.7 long (top cell 70 px),
      the crate face 2.65 and the barrel 3.3+ tall (the sheet's props are about 20 % larger than the kit's: §3.8).
  - **Why this size.**
    - **Against the character (5.5):** the canvas ties are 1.45–1.8 C, the tallest wall 2.4 C, the side wall 1.5 C (a
      character cannot see over it); the mat (5.0 long) takes a lying character; the table top is 0.47 C as M067. A
      character **walks in under the canvas** on the lane left of the hanging corner (canvas underside ≥ 6.9) and from
      the open +X side (§2.10).
    - **Against the kit:** M066 shelter 17.3 × 12.3 × 12.0 (posts 12.0 / 10.4, ties 9.0–10.6); M064 tent 13.7 × 11.7 ×
      11.0; W10 `RuinLeanTo` 13.7 × 8.0 × 10.0 (its verifier asked for **thicker, massive walls**). The lean-to is the
      same class as the shelter, with the ruin rising above it as the sheet draws.
    - **Smaller** (FR post 10.0): the canvas ties drop to 6.6–8.3 and nothing is walkable. **Larger** (FR post 14.5,
      the scale at which the sheet's own hanging corner clears a head): wall courses 2.0, the wall 16 tall, the kit's
      crate and barrel read as toys.
- **Build frame (decision §8.3):** front −Y (the open side with the banner at its right), +X right (the second open side),
  ground z 0; x = (front px − 149.75) × 0.0816 (0 midway between the FL and FR posts); y = (side px − 336) × 0.0816 − 4.6
  (the FR post at y −4.6). Stage 2 puts the origin at the bbox bottom centre (about build (−0.9, −1.15, 0): the fallen
  block at −X, the banner knob at +X, rubble at the front, the back wall at +Y) and stores the offset (§2.13).

### 1.2 Measured views (`measure.py`)

| View (box) | Object bbox (px) | W : H | fill | S / W / C / G / B / R / K / T % |
| --- | --- | --- | --- | --- |
| **f34** (12,122,510,486) | 28–499 × 130–483 (472 × 354) | **1.333** | 0.673 | **40.5 / 25.1 / 11.8 / 10.5 / 4.3 / 2.5 / 1.7 / 0.1** |
| r34 (514,122,1012,486) | 533–999 × 134–483 (467 × 350) | 1.334 | 0.647 | 46.9 / 15.3 / 7.1 / 19.8 / 2.4 / 1.7 / 1.8 / 0.1 |
| **Front** (12,560,280,783) | 21–267 × 585–764 (247 × 180) | **1.372** | 0.736 | 39.3 / 27.1 / 10.4 / 11.6 / 4.6 / 3.1 / 1.3 / 0.0 |
| **Side** (284,560,510,783) | 298–496 × 585–756 (199 × 172) | **1.157** | 0.685 | 45.7 / 19.8 / 7.9 / 15.8 / 0.1 / 1.5 / 1.4 / 0.0 |
| **Rear** (514,560,762,783) | 524–752 × 587–755 (229 × 169) | **1.355** | 0.734 | **69.8** / 9.9 / 0.6 / 15.1 / 0.0 / 0.9 / 2.0 / 0.0 |
| Top (766,560,1012,783) | 779–991 × 561–767 (213 × 208) | 1.024 | 0.702 | 45.1 / 11.4 / 26.7 / 11.1 / 0.2 / 1.2 / 1.3 / 0.1 |

- Shares are % of the silhouette (paper and cast shadow excluded; the remaining 0.5–7 % is near-white stone highlight
  and shadow specks). **Ground plants** (G in the lowest 20 % of the bbox) are 29 % of G in the f34, 35 % front, 41 %
  side, 29 % rear, 21 % r34; with no grass in the hero (decision §8.10), expect G about 7 % in the f34 and 11 % in the
  rear.
- **Verifier tolerance:**
  - front_sheet: W : H **1.37 ± 0.08** (banner and rubble included); FL / FR post top 0.78 ± 0.03; back / FR post 0.93
    ± 0.03; tallest wall / FR post 1.10 ± 0.03; −X wall top / FR post 0.66–0.70; canvas ties / FR post: FL 0.67, back
    0.83, FR 0.77 (± 0.03); banner bottom / FR post 0.25 ± 0.03; shares S 39 ± 8, W 27 ± 8, B 3–6, R 1.5–4.5.
  - side_sheet: W : H 1.16 ± 0.08; FR post at the left, the tall band at the right; G judged by eye (grass omitted).
  - rear_sheet: W : H 1.36 ± 0.08; S ≥ 60; the stepped skyline with its peak 70–118 px (0.30–0.52 of the width) from the
    −X end.
  - f34_sheet: W : H **1.33 ± 0.10**; S 40 ± 8, W 25 ± 7, B 3–6, R 1.5–4, K ≤ 3, G 5–11; C judged on the front and side
    views (§5.4, the M064 canvas ruling).
  - **Recorded, not scored:** the hanging corner's height (ours 6.6, sheet 5.1: §3.6); the top cell's mirroring (§3.4);
    the rear cell's crates (§3.5); the side cell's stepped depth profile (§3.7); the props' size (§3.8).

### 1.3 Silhouette and composition per view

**f34 (`z_f34.png`, `z_f34_mid.png`, `z_f34_right.png`, `z_ban.png`, `z_props.png`) — governs the read and the
dressing.** A **near-frontal high view** (camera ≈ az −15, e ≈ 12°; §3.2): the X layout matches the front cell (post
fractions FL → back → FR 0 / 0.42 / 1 against the front cell's 0 / 0.41 / 1):
- at the left, the **−X side wall** receding up the picture from its **front-end column** (five courses, light faces to
  the left, lavender shade to the right, thin ivy strands and moss on it, a fern at its foot) to the corner;
- the **back wall** behind everything: stepped tops climbing to an **eight-course peak** left of centre (two blocks deep
  on top), a big **lime ivy curtain** falling from that peak down about four courses, then stepping down to the right to
  six courses at the FR post; dark joints, small moss patches and hanging strands on many blocks;
- the **FL post** right of the column: a square orange post with an X-lashing at the canvas corner and a **horizontal
  stub** (the crossbeam) running left onto the wall; a darker lower half with a jagged change of tone at mid-height
  (§3.12);
- the **back post** behind the canvas, its top above the canvas apex with an X-lashing; under the canvas it shows a
  golden band and stands on a **grey stone footing**;
- the **FR post** at the right, the tallest: a heavy X-lashing at the top with a **round crossarm** through it running
  right, a **dark iron sleeve** where a **dark pole** meets the crossarm, the **red banner** hanging from the crossarm
  by two loops (a white diamond emblem, two-point swallowtail foot), a golden collar at mid-height and one at the foot,
  the post standing on a grey block;
- the **canvas**: a cream sheet with soft diagonal creases, tied at FL (left), the back post (top) and FR (right), its
  **fourth corner hanging low at the front right of centre** with a short rope and toggle dangling from it;
- inside: the **bedroll** (brown leather, golden end caps, a tan strap) lying along the back at the left, the **mat**
  (golden tan, blue-teal stripes) in front of it, the **crate** (X-braced, open top, dark interior) at the front-left
  beside the FL post, the **side table** (open frame, lower shelf) at the back under the hanging corner, the **barrel**
  (two dark hoops, open top) left of the FR post; a small orange box behind the FR post (§3.13);
- **rubble**: five or six chamfered pale blocks across the front (a big one front-centre, a pair at the left, one at
  each post foot) with moss on some; grass tufts and ferns at both ends (§3.11).

**r34 (`z_r34.png`, `z_r34_lamp.png`) — a true rear view from the back-right** (§3.3): the **back wall's outer face** fills
the right half nearest the camera (a block grid five courses up to the peak behind, two heavy **ivy curtains** down its
face, ferns at its foot), the open +X side shows the interior (bedroll, mat, crate, table), the canvas from the back
post down to the hanging corner's golden toggle at the wall's edge, and the **banner post at the far left** with the
banner's back.

**"Front view" (`z_front.png`) — governs X and heights.** The −X wall end-on as a five-course column at the left, the
back wall's stepped skyline (peak left of centre), the three posts (FL short, back mid, FR tall) with their lashings, the
canvas's V (FL tie → low corner → FR tie), the banner right of FR on its crossarm with the dark pole under it, bedroll,
crate, mat, table and barrel along the foot, rubble in front.

**"Side view (right)" (`z_side.png`) — governs Y.** The FR post at the left (front) with its lashing and collars, the
canvas falling from it toward the back, the interior (crate, table, mat) under it, the wall stepping up to the back
(9.0, 11.0, then the 13.4 band of the tall section seen end-on), ivy on the end, a fern at its foot.

**"Rear view" (`z_rt.png`, left).** The back wall's outer face square on: a block grid of six to eight courses with dark
joints, the skyline peak right of centre (the front's peak mirrored), an ivy curtain from the peak down the middle and a
strand at the left (+X) end, the FR post's top showing over the wall at the left; **two crates and a block drawn outside
the wall** (§3.5).

**Top view (`z_rt.png`, right) — content only, mirrored** (§3.4): the walls along the top and the right edges with ivy
and moss on their tops and a thick corner pier, a broken stub and rubble on the open left side, the canvas as a square
with a golden tie at each corner and a seam X to its centre, the mat and bedroll along the walls, a stake at one open
corner, the banner at the other.

**Exploded (`z_ex_l.png`, `z_ex_r.png`).** Loose perspective, part shapes only:
- **Ruin Wall Blocks (modular):** a stepped wall chunk of chamfered blocks: a four-block pier, a five-course stepped
  stack, a small **opening** one block wide and two courses tall bridged by a top block, and a pier beyond, with an ivy
  run down the middle;
- **Stone Rubble (assorted):** single blocks and pairs, some broken;
- **Canvas Canopy:** a square sheet, slightly domed, with a **small square wooden toggle at each corner**;
- **posts:** a tall post with an X-lashing at the top and a collar near the foot; a **crossbeam** lashed at one end; a
  post with an X-lashing; a post with the banner on a short crossarm; a short post with collars; a post with a **lantern
  on a bracket arm** (§3.10); two stone footings, one with a post stub on it;
- a **plank bench** (two planks, splayed legs, a stretcher), a small **open box frame**, a **yellow bedroll** with two
  green straps (leader "Crate"), a **barrel** with two iron hoops and an open top, grass and fern tufts.

**Close-ups.** A: the FL / FR junction (toggle lashed across the post under the X-lashing, the canvas corner tied to the
toggle). B: the same junction from below. C: the block (chamfer about 0.10 of the block size on every exposed edge, dark
joints, a lighter top, ivy hanging from a top joint).

**Palette and notes.** Five flat swatches (§5.1); the notes as above.

### 1.4 Parts (exploded, close-ups)

| Part (label) | Box (px) | Tone (median, lit, shade) | Shape |
| --- | --- | --- | --- |
| Ruin Wall Blocks | (60,860,300,1110) | `#A48A80`, lit `#DCC7B7`, shade `#6F615D` | stepped chunk of chamfered near-cubic blocks, a 1 × 2 opening, ivy run |
| Stone Rubble | (40,1100,240,1230) | `#AEA4A7`, lit `#F5EDE1` | loose chamfered blocks, broken corners, moss |
| Canvas Canopy | (330,830,560,940) | `#FEEEC4`, lit `#FEEFC5` | square sheet, four corner toggles |
| Upright posts | (320,950,350,1180) | `#884316`, lit `#C66213`, shade `#5C2B14` | square posts, X-lashing, collars |
| Banner (cloth) | (510,1005,555,1125) | red as the hero | banner on a short crossarm |
| Crossbeam | (365,980,460,1030) | timber | square beam, lashed end |
| Bench / box frame | (340,1080,460,1160) / (315,1185,370,1230) | `#8D4819`, lit `#CA6D23` | two-plank bench; open frame |
| Bedroll ("Crate") | (365,1170,445,1220) | `#FBC34E` (exploded) / brown `#82421F` (hero) | roll with straps and caps |
| Barrel | (510,1130,580,1230) | `#884114`, lit `#D06C19` | eight staves, two dark hoops, open top |
| Lantern post | (600,960,640,1150) | glass `#F89C0C` | post, bracket arm, hanging lantern (§3.10) |
| Close-up A / B timber | (930,850,1000,1005) / (760,1050,960,1190) | `#AA571B` lit `#C7641C` / `#713C20` | post, toggle, beam end |
| Close-up C block | (760,1240,960,1440) | `#B5A29F`, lit `#DEC4BB`, shade `#6D666B` | chamfered block, dark joints, ivy |

### 1.5 How 070 differs from the old kit (binding: the verifier checks these)

| | W10 `RuinLeanTo` (old kit, exported) | **070 Ruined Lean-To** |
| --- | --- | --- |
| Size | 13.7 × 8.0 × 10.0 | **≈ 20.6 × 12.4 × 13.2; FR post 12.0; canvas ties 8.0 / 9.9 / 9.2** |
| Wall | "regular brick wall", lilac-grey | **an L of big chamfered blocks (2.4 deep, 1.65 courses) with a stepped broken skyline, peak 8 courses; broken corners, missing top blocks, a fallen block** |
| Overgrowth | vine strands, small caps | **three ivy curtains of chunky five-point leaves on square stems (M056 recipe), moss patches on block tops** |
| Canvas | V-sag between wall tie and posts | **one closed 0.10 sheet tied at three posts by toggles under X-lashings; the free front corner hanging to 6.6** |
| Posts | 1.5 round logs with collars | **three square chamfered posts on stone footings, golden X-lashings, collars, a crossbeam onto the side wall** |
| Banner | on an arm off the right post | **on a round crossarm through the FR post, held by a dark pole with an iron sleeve; emblem both faces** |
| Glow | one `heat_glow` | **none** (the sheet's notes; §7) |
| Colour | `w10_wood #8A4A22`, lilac stone | **orange timber `#964914`, warm pink-grey stone `#A6958F` (never lavender), lime ivy** |
| Budget | 5822 / 8000 | **plan 3800–3950, ceiling 4000** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0). Kit camera azimuths: `front` az 0 (camera on −Y), `side` az 90
(camera on +X, screen right = +Y), `rear` az 180; the f34 is about az −15 e 12 (camera at the front, a little left); the
r34 about az 140 e 15 (camera at the back-right).

### 2.1 Stack (binding contact chain; every seat ≤ 0.03 unless stated)

| Piece | Rests on / against | Contact |
| --- | --- | --- |
| Bottom-course blocks, rubble, fallen block | the ground | bottoms z 0.000 (±0.005); the fallen block on one edge, sunk ≤ 0.05 |
| Upper-course blocks | the blocks below | bottom 0.015 above the block below; side gaps 0.04–0.06 to neighbours (the joint) |
| Post footings (3) | the ground | flat bottoms z 0 |
| Posts (3) | their footings | foot on the footing's flat top z 0.60 (±0.005) |
| Crossbeam | the FL post's −X face and the side wall's front-end top | side face on the post (≤ 0.02); underside on the top block (≤ 0.02); bound by the FL lashing |
| X-lashings, collars, bands | their post (and the crossbeam / crossarm / toggle they bind) | turns hug the timber, inner surface 0.00–0.02 off; sink ≤ 0.03 |
| Corner toggles (C1–C3) | across the post's inner face under the lashing | touching the post (≤ 0.02) |
| Canvas | the three toggles | each corner tab wraps its toggle (≤ 0.02); nowhere buried > 0.05 |
| C4 tail and toggle | the canvas corner | rope end sunk 0.03 into the corner tab |
| Crossarm | through the FR lashing, resting on the dark pole's cap | touching both |
| Dark pole, sleeve | the ground; the crossarm | foot z 0; sleeve round both |
| Banner | the crossarm | two loops wrap the arm (inner surface ≤ 0.02 off) |
| Ivy stems and pads | block faces and tops | stem backs within 0.03 of the stone (M056 §2.1) |
| Ivy leaves | stem (stalk notch) and stone | notch within 0.03 of the stem; blade 0.01–0.05 off the stone; never inside it |
| Moss patches | block tops | flat base 0.02 into the top, never more than 0.05 |
| Bedroll, mat, crate, table, barrel | the ground (mat top 0.16) | bottoms z 0; each ≥ 0.05 from every other piece unless it touches |

### 2.2 Ruin walls (blocks; decision §8.4)

- **Block:** near-cubic, **2.4 deep (Y for the back wall, X for the side wall) × 1.65 tall × 1.6–2.6 long** (mostly 2.0–
  2.2), running bond (joints offset ≥ 0.6 between courses), **0.16 chamfer** on the top edges and on every exposed
  vertical edge (close-up C); bottom edges square (they sit on the course below). Joints are 0.05 gaps, so the chamfers
  meet in a dark V; no joint geometry. ±0.03 jitter per block in position and ±1° in yaw (never more than 0.05 proud of
  the face plane: §13.5 "do not randomly jitter every block").
- **Back wall:** x −9.6 … +5.2, **y +3.0 (inner face) … +5.4 (outer face)**. Course tops per span (the front cell's
  skyline):

  | x span | Courses | Top z | Front cell (px top → z) |
  | --- | --- | --- | --- |
  | −9.6 … −7.2 (corner, bonded with the side wall) | 5 | 8.25 | 654–660 → 7.5–8.0 |
  | −7.2 … −5.6 | 6 | 9.90 | 625–640 → 9.1–10.4 |
  | −5.6 … −4.0 | 7 | 11.55 | 611–618 → 10.9–11.5 |
  | **−4.0 … +1.4 (peak)** | **8** | **13.20** | 585–590 → 13.2–13.6 |
  | +1.4 … +2.6 | 7 | 11.55 | 612–623 → 10.5–11.2 |
  | +2.6 … +4.4 | 6 | 9.90 | 631–636 → 9.5–9.9 |
  | +4.4 … +5.2 (broken end) | 5 | 8.25 | 640 → 9.1 (recorded) |

- **Side wall (−X):** x −9.6 … −7.2, **y −4.2 (front end) … +3.0** (bonded into the corner), **five courses (8.25)**; its
  front-end column's top block chipped on the outer front corner (top reads ≈ 7.9, the front cell's 7.6–8.0).
- **Ruin damage (role, never random per block):**
  - **broken corners:** eight blocks get a chip (0.30–0.45 off one top corner, built into the block's ring, no
    booleans): the peak's two outer top blocks, the side wall's front-end top block, the +X end's top block, three
    mid-wall blocks on the inner face, one rubble block;
  - **missing blocks:** course 8 has one gap (x ≈ −1.0 … +0.6) and course 6 one at x ≈ +3.4; the side wall's top course
    one at y ≈ −0.8 (the f34's step);
  - **fallen block:** a broken half block (1.6 × 1.6 × 1.4, two chipped corners) lying tilted 12° on the ground outside
    the side wall at (−10.6, −0.8), 0.2 off its outer face (the f34's and top cell's rubble on that side).
- **Block counts:** back wall ≈ 47 (courses 1–5: six blocks each plus the corner; course 6: five; 7: four; 8: two),
  side wall ≈ 12, so ≈ 59 wall blocks; each a closed shell.
- The two-blocks-deep look of the peak's top (f34, r34) comes from the 2.4 depth plus a chamfered top; the side cell's
  3.9 band is recorded (§3.7).

### 2.3 Posts, footings, crossbeam

| Member | Section | Position |
| --- | --- | --- |
| Footings (3) | 1.40 × 1.40 × 0.60 pale chamfered blocks (stone key), broken corner on one; the back post's 1.20 × 1.20 so it clears the wall by 0.15 | under each post |
| **FL post** | 0.86 square, 0.05 chamfer, cracked split top (two 0.08 grooves) | centre (−5.90, −3.90), z 0.60 … **9.35** |
| **Back post** | 0.80 square | centre (−1.00, +2.25) (its back face 0.35 off the wall's inner face, clear of R1's leaves), z 0.60 … **11.10** |
| **FR post** | **1.10 square** (the sheet's heaviest) | centre (+5.90, −4.60), z 0.60 … **12.00** |
| Crossbeam | 0.60 × 0.60, square ends with pale cut faces | along X at y −3.90, z 8.25 … 8.85, from the FL post's −X face (x −6.33) to x −9.10, its far 1.9 resting on the side wall's front-end top block |

- No booleans: the crossbeam touches the post face; the lashing binds both.

### 2.4 Canvas (one closed shell; decision §8.5)

- **Corners** (mid-surface):
  - **C1** (−5.40, −3.40, **8.00**) at the FL post's inner corner, tab wrapping the C1 toggle;
  - **C2** (−0.55, +1.80, **9.90**) at the back post's front corner, tab on the C2 toggle;
  - **C3** (+5.30, −4.05, **9.20**) at the FR post's inner corner, tab on the C3 toggle;
  - **C4** (+1.40, −5.40, **6.60**), the free corner, gathered into a short tab with a 0.7 rope tail and a toggle
    dangling from it (lowest point of the tail ≈ 5.8, the f34's tassel).
- **Grid:** 6 × 6 vertices, bilinear in plan between C1 → C2 (u) and C1 → C4 (v).
- **Sag:** z = bilinear(corner z) − **0.20** at the front edges' middles (C1–C4, C4–C3), **0.45** at the back edges'
  (C1–C2, C2–C3), **0.60** at the centre (a parabola per edge, blended). Every point over the walk lane ≥ 6.9 underside
  (§2.10).
- **Creases:** triangulate each quad along the diagonal pointing to the sheet centre (M066's X of creases; the top cell's
  seam X and the f34's diagonal folds). No subdivision, no cloth sim.
- **Thickness:** 0.10 closed slab (offset down along vertex normals); rims are real faces.
- **Toggles (4):** 0.32 × 0.32 × 0.55 square wooden pegs (exploded corner blocks; close-up A), C1–C3 lashed across the
  post's inner face under the X-lashing, the canvas tab gathered round them.

### 2.5 Rope

| Piece | Count | Where | Size | Sides × segments |
| --- | --- | --- | --- | --- |
| X-lashing | 3 | FL z 7.60–8.95 (post + crossbeam + C1 toggle); back post z 9.40–10.40 (post + C2 toggle); FR z 9.20–10.60 (post + crossarm + C3 toggle) | Ø 0.22 (FR 0.26) | 4 × 8 per turn; 2 horizontal turns + 2 crossing diagonals |
| Collars | 3 | FR mid z 4.45–4.95 (front cell 4.5–5.0); FR foot z 0.62–1.00; FL foot z 0.62–0.95 | Ø 0.22 | 4 × 8, two turns |
| Back-post band | 1 | z 3.40–3.70 (f34 golden band under the canvas) | flat strap 0.30 × 0.06 | 4 sides |
| C4 tail | 1 | from the C4 tab down 0.7 | Ø 0.12 | 4 × 4 |
| Banner loops | 2 | round the crossarm | cloth, part of the banner | — |

- All rope **twisted** (M051 / M066 twist), chunky, golden; every turn touches what it binds (`hull_loop` round the
  square timbers, M066 / M064).

### 2.6 Banner, crossarm, dark pole

- **Crossarm:** round (8-sided) Ø 0.45, along X at z 9.60 (axis), through the FR lashing from x +5.10 to **+9.30**, an end
  knob Ø 0.60 at +9.30; pale cut face at the inner end.
- **Dark pole:** 8-sided Ø 0.50, at (+7.40, −4.30), z 0 … 9.37 (its cap under the crossarm), an **iron sleeve** (0.70 ×
  0.70 × 0.50, `m070_iron`) round the crossarm and the pole top.
- **Banner:** a closed 0.08 slab in the plane y −4.75 facing −Y, x **+7.15 … +9.25** (2.10), top hem z 9.20 wrapping the
  arm with two loops (0.35 wide) at x 7.4 and 9.0, **two-point swallowtail**: tips z **3.00**, centre notch up to 3.80;
  the white emblem (outer diamond ring, inner diamond ring, two side spikes) on **both** faces as thin shells 0.01 proud.
- The banner clears the pole by ≥ 0.15 and the FR post by ≥ 0.6.

### 2.7 Ivy and moss (M056 recipe, budget-limited; decision §8.6)

- **Leaf:** M056's lens leaf (`leaf_points`, `lens_polys`: an 8-vert five-point outline, raised midrib fan, 16 tris),
  **0.85–1.10 across**, tips down ± 35°, overlapping 30–50 %; tones by role (§5.3). Stems: M056's square-section
  `stem_shell` (main Ø 0.24, branch Ø 0.16), straight segments with flat junctions; pads (`pad_shell`) where a run lips
  over a top edge.

| Run | Face, span | Top → bottom | Leaves |
| --- | --- | --- | --- |
| **R1 peak curtain** | back wall inner face (y +3.0), x −4.0 … −1.8 (≥ 0.10 off the back post) | pad on the peak top (−2.6, +4.2, 13.2), lips over, down to z ≈ 7.0 (the f34 / front curtain, about four courses) | **14** (3 lipping on the top) |
| **R2 rear curtain** | back wall outer face (y +5.4), x −3.0 … −0.4 (the rear cell's middle curtain) | from the peak top down to z ≈ 4.0 | **8** |
| **R3 rear +X strand** | back wall outer face, x +3.4 … +4.6 | from the course-6 top to z ≈ 3.0 (rear cell's left strand, r34) | **4** |
| **R4 side-wall strands** | side wall outer face (x −9.6), y −3.6 … −1.0 | two thin strands from the top down 3–4 courses (f34) | **4** |
| **Moss** | block tops: peak (2), course 7 (1), course 6 (2), side wall (2), one rubble | flat lumpy lime patches 0.8–1.4 across, 0.15–0.25 tall (M056 `cushion_shell` flattened, H : W ≤ 0.2) | 8 patches |

- **Total ≈ 30 leaves.** Stems show between leaves. Every leaf faces outward from its wall face (never edge-on to the
  front or rear cameras); top leaves tilt up 25–40°.
- WorldModeling §13.5: the ivy covers at most ≈ 15 % of any wall face; the masonry stays readable.

### 2.8 Interior dressing and props (f34; kit sizes, §3.8)

| Piece | Centre (x, y) | Size (X × Y × Z) | Rot (z) | Notes |
| --- | --- | --- | --- | --- |
| Bedroll | (−4.20, +2.15) | 4.40 long × Ø 1.20 | along X | brown leather 8-sided roll, golden end caps 0.20, one tan strap at x −2.8; x −6.4 … −2.0, clear of the back post's footing |
| Mat | (−2.60, −0.80) | 2.20 × 5.00 × 0.16 | along Y | golden tan slab, y −3.3 … +1.7, its head end under the bedroll's curve (gap ≤ 0.05), two blue-teal stripes 0.25 wide at 0.6 from each end |
| Crate | (−5.60, −1.20) | 2.30 × 2.30 × 2.20 | 5° | X-braced, open top, dark interior floor |
| Side table | (+1.20, +2.00) | 2.80 × 1.60 × **2.60** | 0° | two-plank top, four legs, a lower shelf, rails (open frame) |
| Barrel | (+3.90, −3.00) (clear of the FR footing) | Ø 2.00 / 2.20 × 2.72 | 15° | eight staves, two dark hoops, open top with a dark rim |
| Rubble RB1–RB5 | (−8.60, −5.60), (−6.80, −6.20), (−1.60, −7.00), (+3.20, −6.60), (+8.40, −5.60) | 1.6×1.4×1.2, 1.2×1.2×1.0, 1.5×1.4×1.3, 1.2×1.1×0.9, 1.0×1.0×0.8 | 5–30° | chamfered, one or two broken corners each, flat bottoms |
| Fallen block | (−10.60, −0.80) | 1.6 × 1.6 × 1.4 | 12° tilt | §2.2 |

- **Clearances:** every piece ≥ 0.05 from the walls, footings and each other unless it touches; the mat's head tucks
  under the bedroll (touching, ≤ 0.02).
- **Seat / sleep points** (stored): `m070_sleep` (−2.60, −0.80, 0.16) along +Y.

### 2.9 Grass

- None in the hero (decision §8.10): ground scatter in Studio. Alternative: two fern clumps at the side wall's foot and
  the FR post foot (≈ 60 tris each).

### 2.10 Walk-in clearances (binding)

- **Front lane:** a 5.5 proxy (2 × 1 body to 4.4, a 1.1 head to 5.5) walks from (−3.2, −9) to (−3.2, 0) onto the mat
  between the FL post / crate and the hanging corner, touching nothing; **canvas underside ≥ 6.9 over x −4.4 … −2.0**.
- **Side lane:** from (+9, −0.5) to (0, −0.5) between the barrel and the table, under the C2–C3 side of the canvas
  (≥ 8.0).
- **C4:** its tail bottom (≈ 5.8) stays ≥ 0.6 off both lanes.
- Print every minimum clearance (target ≥ 0.10) and the canvas underside heights along both lanes.

### 2.11 Expected extents

- **Walls:** X −9.6 … +5.2, Y −4.2 … +5.4, Z 0 … 13.2.
- **Hero:** X ≈ −11.4 (fallen block) … +9.6 (crossarm knob), Y ≈ −7.7 (rubble RB3) … +5.4 (back wall), Z 0 … 13.2 →
  **about 21.0 × 13.1 × 13.2**; bbox bottom centre ≈ (−0.9, −1.15, 0) in the build frame.

### 2.12 Screen checks (floor hidden; `measure.py` masks; probe and keep the best)

- **front_sheet (0, 3)** — governs X and heights: the §1.2 front tolerances; the skyline steps of §2.2 (±0.3 per step),
  the canvas V, the banner right of FR with the dark pole under it.
- **side_sheet (90, 3)** — governs Y: FR post at the left, the canvas falling toward the back, the wall's tall band at the
  right (ours 2.4 deep: recorded, §3.7).
- **rear_sheet (180, 3)** — the outer face block grid, the skyline peak 0.30–0.52 of the width from the −X end, the R2
  curtain in the middle and R3 at the +X end, S ≥ 60.
- **f34_sheet (−15, 12)** (probe az −5 … −25 × e 8 / 12 / 16) — governs the read and dressing: W : H 1.33 ± 0.10, shares
  per §1.2; content per §1.3.
- **r34_sheet (140, 15)** (probe 130 … 150) — content: the outer face with R2 and R3, the interior through the +X side,
  the banner post at the far left.
- **top (0, 89.9)** — content only, compared with the sheet's top mirrored left–right (§3.4): the L of walls, the canvas
  kite with ties at its corners, mat and bedroll, rubble on the open sides.

### 2.13 Origin, pivot and stored points

- Origin at the **bbox bottom centre** (`K.check`); transforms applied. Store on the hero `o["m070_offset"]` (build frame
  = object + offset, M052's convention), `o["m070_centre"]` (the floor under the canvas, build (−1.0, −1.0, 0)),
  `o["m070_sleep"]`, `o["m070_corner"]` (the inside wall corner (−7.2, +3.0, 0)); re-check all after the origin move.
- Parts: origin at their own bbox bottom centre; the WallBlock part also stores `m070_course` (1.65); the Canopy part
  `m070_ties` (C1–C4 positions in part space); the Post part `m070_top`.

## 3. View conflicts and resolutions

### 3.1 Sheet number
- **Evidence.** The header says "PAGE 68/132"; INDEX.md row 70 lists `070.png` as "Ruined lean-to model study".
- **Resolution.** Our number is 070 (file, keys `m070_*`). The header goes in the export notes only.

### 3.2 The "front three-quarter" is a near-frontal high view
- **Evidence.** The posts' horizontal order and spacing match the front cell (0 / 0.42 / 1 against 0 / 0.41 / 1); the
  side wall recedes up the picture rather than across it; the block tops are visible (camera above).
- **Resolution.** Score it at az −15, e 12 (probe az −5 … −25, e 8–16).

### 3.3 The "rear three-quarter" is a true rear view from the back-right
- **Evidence.** The banner post is at the far left, the back wall's outer face (block grid, ivy curtains) fills the
  right half nearest the camera, and the interior shows through the open +X side.
- **Resolution.** `r34_sheet` at az 140, content only.

### 3.4 The top view is mirrored
- **Evidence.** It draws the walls along the top and **right** edges with the open sides at the left and bottom; every
  other view puts the side wall at the left (−X). Its banner (bottom right) sits by the end of a wall, not at the open
  corner; its canvas is an axis-aligned square with a stake at one corner.
- **Resolution.** Compare it mirrored left–right, content only (walls, canvas ties, mat and bedroll along the walls,
  rubble on the open sides). Its banner position and the stake are recorded misses.

### 3.5 The rear view draws crates outside the back wall
- **Evidence.** Two crates and a block stand on the ground in front of the outer face in the rear cell; the f34, front
  and r34 put the crate inside.
- **Resolution.** The crate stays inside (f34). Recorded.

### 3.6 The hanging corner: 5.1 (sheet) against a walkable lane
- **Evidence.** Front cell: the lowest canvas corner at 62 px (5.1 at our scale), right of centre at the front; f34: the
  same corner hanging with a rope tassel; side cell: the canvas falls from the FR lashing toward the back.
- **Resolution (decision §8.5).** **C4 at 6.6** with a 0.7 tail (to ≈ 5.8), front edges sagging 0.20, so the lane left
  of it keeps ≥ 6.9 underside. The V stays clear (C4 1.4 below C1, 2.6 below C3). Alternatives: the sheet's 5.1 (a
  head-height flap; the left lane drops to ≈ 6.3, tall avatars clip) or scale the model up to FR 14.5.

### 3.7 Wall depth: the side cell's 3.9 band against the f34's single row
- **Evidence.** Side cell: the tall section seen end-on is 48 px (3.9) with steps in front of it (11.0, 9.0); f34 and
  top: the side wall one block deep, the peak top two blocks; top cell walls 26–33 px (2.1–2.7).
- **Resolution.** **Every block 2.4 deep** (the W10 verifier's "thick, massive" walls and the top cell's 2.1–2.7). The
  side cell's band and steps are recorded. Alternative: a second 1.8 row behind the peak (+ ≈ 16 blocks, ≈ 380 tris).

### 3.8 Props drawn about 20 % larger than the kit
- **Evidence.** At the FR-post scale the crate face is 2.65 and the barrel 3.3+ tall, the side table 2.45.
- **Resolution.** **Kit sizes** (crate 2.30, barrel 2.72, table top 2.60) as 064 / 066 / 067 / 068, so the kit's
  furniture matches across models. Recorded.

### 3.9 Exploded labels pointing at the wrong pieces
- **Evidence.** "Crate" points at the yellow bedroll, "Table / Bench" at the small open box frame and a short post,
  "Banner (cloth)" at a stone with a pin, "Upright Post (2x)" at the lantern post.
- **Resolution.** Parts follow the drawn shapes and the hero (§8): the bedroll is a bedroll, the crate is the f34's
  X-braced crate, the table is the f34's side table.

### 3.10 The lantern (exploded only)
- **Evidence.** One lantern on a bracket post in the exploded; no assembled view shows it or any glow; the notes say
  "No baked lighting, effects".
- **Resolution (decision §8.9).** **No lantern, no glow, no VFX socket.** Alternative: a lantern on a bracket at the FL
  post (Neon glass, M064's steady `heat_glow`; +≈ 150 tris).

### 3.11 Grass and ferns
- **Evidence.** Tufts and ferns at both ends and the front in every view (29–41 % of G).
- **Resolution (decision §8.10).** None in the hero (WorldModeling §1.1: optional dressing; 064 / 066 / 068 left grass
  out); ivy and moss stay (they belong to the ruin).

### 3.12 The FL post's two tones
- **Evidence.** f34: the FL post's lower half darker with a jagged change of tone at mid-height; front cell: a notch.
- **Resolution.** One timber; the lower 40 % of each post blends one step toward `m070_timber_deep` (by height, §5.5).
  No modelled break.

### 3.13 Small items not in the parts list
- **Evidence.** f34: a small orange box with items behind the FR post; the exploded's plank bench and open box frame;
  stone footings with a post stub.
- **Resolution.** Left out of the hero (the bench is not in any assembled view); the footings are under the posts.
  Recorded.

### 3.14 Ruin wall part: the exploded's opening
- **Evidence.** The exploded wall chunk has a one-block, two-course opening under a bridging block; the hero walls have
  none.
- **Resolution.** The hero has no opening (every assembled view); the exported **WallSection** part has it (§8), so the
  modular kit gets the exploded's piece.

### 3.15 "No baked lighting, effects or weathering textures" against the user's colour rule
- **Resolution.** Colour per role and position with broad per-block Tint (§5.6); no painted light, shadow, cracks or
  grime textures; the grime band at the wall foot is a three-step blend of the same stone (as 056 / 068).

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

1. `block(lo, hi, chamfer, chip, seed)` → one wall block (top and exposed-vertical chamfers; optional broken corner).
   Check against close-up C.
2. `back_wall()`, `side_wall()` → courses per §2.2 with running bond, chips, missing blocks; `fallen_block()`.
3. `rubble(i)` → RB1–RB5 (chamfered, broken corners, flat bottoms).
4. `footing(c)`, `post(c, top, size)` (chamfered square, cracked top on FL), `crossbeam()`.
5. `toggle(post, z)`, `lashing(post, z0, z1, binds)` (two horizontal turns + the crossing diagonals), `collar(post, z)`,
   `band(post, z)`.
6. `canvas()` → one closed slab per §2.4 (corner tabs round the toggles, the C4 tab, the crease diagonals); `c4_tail()`.
7. `banner()` → crossarm, knob, dark pole, sleeve, banner slab with loops and swallowtail, emblem shells both faces.
8. `ivy(run)` → stems, pads, leaves per §2.7; `moss(i)`.
9. `bedroll()`, `mat()`, `crate()`, `side_table()`, `barrel()`.
10. **Hero `RuinedLeanTo`** = walls + rubble + footings + posts + crossbeam + lashings + collars + toggles + canvas +
    banner + ivy + moss + dressing, placed by §2, one object of closed shells. Then the contact, bury, pierce, walk,
    leaf-facing and winding reports (§6, §2.10).
11. **Parts shot** (−30, 15) laid out like the exploded; **exploded shot**: canvas lifted 4, posts apart, walls apart.

**Helpers to reuse (import functions from committed builders, never their module constants; copy if a module has
uncommitted changes at the time):**
- **`m056`** (ruin, ivy, moss): `brick_shell` (chamfered block with a chip in its ring: start here for `block`),
  `stone_core` (course / bond layout), `rock_shell` and `rocks` (rubble shapes), `cushion_shell`, `_cushion`,
  `lumpy_cushion`, `_lump_shell` (moss; flatten H : W to ≤ 0.2), `leaf_points`, `lens_polys`, `leaf`, `place_leaf`,
  `push_clear` (keeps leaves off the stone), `stem_shell`, `pad_shell`, `wall_points`, `_point_at_z`, `_run_geometry`,
  `_stations`, `ivy` (a run from a pad down a face), `part_cluster`, `part_tendril`, `part_corner`, `leaf_report`
  (edge-on / facing check), `contact_report`, `bury_report`, `shells_report`, `_paint_cushion` (height bands).
- **`m066`** (canvas on posts, X-lashings, banner): `_solid`, `_shell`, `_hull`, `_box`, `_prism`, `_ngon`, `_cyl`,
  `_tube`, `hull_loop`, `rope`, `_groove`, `rect_loop`, `post`, `stone_base` (footings), `collar`, `canvas_corners`,
  `canvas_top`, `_canvas_tris` (centre-pointing crease diagonals), `canvas_sheet`, `corner_tab`, `post_loop`,
  `x_diagonals`, `lashing_crossbar` (an X-lashing binding a post and a crossbar: the FL and FR lashings), `tail`, `rod`,
  `sleeve`, `_slab`, `banner`, `emblem`, `rod_band`, `table`, `crate`, `barrel` (open barrel with hoops), `stone`,
  `walk_report`, `pierce_report`, `rope_ends_report`, `placement_report`, `_min_angle`, `_thin`, `_uv_overlaps`,
  `_uv_unfold`, `export_stats`, `render_close`, `render_spin`, `render_cam`. (m066 is committed as work in progress:
  copy, don't import.)
- **`m064`**: `_slab2d` (closed canvas slab in a plane), `rope`, `_trim`, `rope_trim`, `hull_loop`, `lashing`, `_band`,
  `knot`, `crate` (X-braced: trim to ≈ 200 tris), `barrel`, `stone`, `bedroll` (start for the bedroll), `mat`, `bury_report`,
  `pierce_report`, `walk_report`, `render_spin`.
- **`m052`**: `_ext`, `_cells`, `_earclip`, `_slab` (ear-clipped prism: chipped block rings, swallowtail banner),
  `_plank2d`, `_post_solid` (square post with chamfered cap), `wrap_path`, `_resample`, `_rope_groove`, `rope_tie`,
  `walk_report`, `buried_report`, `levels_report`.
- `m047`: `_Solids` (ray-parity inside test). `m048`: `_solid`, `winding_report`, `_tri_ngons`. `m067`: `_plank`,
  `seat_report`, `thin_report`.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a pale block ruin in an L with a stepped broken skyline, ivy falling from its peak, three orange
   posts with golden lashings, a cream canvas with a low front corner, a red banner at the right, a camp inside.
2. **front_sheet / side_sheet / rear_sheet / f34_sheet / r34_sheet / top** per §2.12.
3. **Close-up renders:**
   - `junction_cu` at the FR post top, against close-up A: the toggle across the post, the X-lashing over it, the canvas
     tab round the toggle, the crossarm through the lashing.
   - `underside_cu` from below the FL corner, against close-up B: the crossbeam end, the lashing, the canvas tab; **no
     see-through canvas**.
   - `block_cu` at the peak's inner face, against close-up C: chamfers on every exposed edge, dark V joints, a lighter
     top, R1's leaves hanging from the top joint.
   - `ruin_cu`: a chipped block, a missing top block, the fallen block.
   - `walk`: the 5.5 proxy on both lanes (front, side, three-quarter); `inside_cu` from the front lane looking at the
     bedroll and mat.
   - `thumb`: the f34 at about 140 px tall: skyline, ivy, canvas V, banner still read.
   - `spin` contact sheet az 0 / 45 / … / 315 at e 10: nothing floats, no see-through faces, leaves never edge-on combs.
4. **Contact counts** (§6): floating 0; buried 0 (stated seats excepted); pierce 0; winding errors 0.
5. **Scale shot:** a 5.5 marker in the front lane and one lying on the mat.

### 4.3 Budget (ceiling 4000, plan 3800–3950; decision §8.2)

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Wall blocks (top-chamfered 20; blocks with exposed vertical edges 28–36) | ≈ 59 | ≈ 24 | 1420 |
| Broken-corner chips (extra ring faces) | 8 | 8 | 64 |
| Fallen block, rubble RB1–RB5 | 6 | 24 | 144 |
| Post footings | 3 | 20 | 60 |
| Posts (chamfered square; split top on FL) | 3 | 28 | 84 |
| Crossbeam | 1 | 20 | 20 |
| X-lashings | 3 | 80 | 240 |
| Collars, back-post band | 3 / 1 | 32 / 16 | 112 |
| Canvas (6 × 6 closed slab with tabs) | 1 | 150 | 150 |
| Toggles, C4 tail | 4 / 1 | 12 / 16 | 64 |
| Banner (slab 40, emblem both faces 48, crossarm 28, knob 12, pole 28, sleeve 12, loops 24) | 1 | 192 | 192 |
| Ivy leaves (lens) | 30 | 16 | 480 |
| Ivy stems and pads | ≈ 16 seg + 3 pads | 8 / 12 | 164 |
| Moss patches | 8 | 14 | 112 |
| Barrel (open, eight staves, two hoops) | 1 | 200 | 200 |
| Crate (X-braced, open top) | 1 | 200 | 200 |
| Side table | 1 | 120 | 120 |
| Bedroll (8-sided roll, caps, strap) | 1 | 80 | 80 |
| Mat + stripes | 1 | 36 | 36 |
| **Hero** | | | **≈ 3940; ceiling 4000** |
| Parts (§8) | | | WallBlock ≈ 36, WallSection ≈ 520, Rubble ≈ 60, Canopy ≈ 210, Post ≈ 200, Banner ≈ 192, Bedroll ≈ 116, Table ≈ 120, Crate ≈ 200, Barrel ≈ 200 |

- **Cut order if over:** moss patches (to 4), the C4 tail, the back-post band, ivy leaves (to 24, cutting R3 and R4
  first), the crate's inner braces, block chamfers on hidden vertical edges (12-tri plain boxes for buried bottom
  blocks), lashing sides (4 → 3). **Never cut:** the stepped skyline, the chamfers on exposed edges, the R1 curtain, an
  X-lashing, the canvas thickness, the hanging corner, the banner emblem, the crossbeam.
- **Headroom use** (only after every check passes): the second row behind the peak (§3.7), two ferns (§3.11).

### 4.4 Shape targets (binding; check with `M.audit` and own bmesh code)

- Course height 1.65 ± 0.03; skyline tops per §2.2 ± 0.1 (peak 13.2); blocks 2.4 ± 0.1 deep; chamfer 0.14–0.18; joints
  0.04–0.06.
- Post tops FL 9.35, back 11.1, FR 12.0 (± 0.1); posts 0.86 / 0.80 / 1.10 square ± 0.05; footings 0.60 tall.
- Canvas ties C1 8.0, C2 9.9, C3 9.2 (± 0.15); C4 6.6 ± 0.2; thickness 0.09–0.11; underside ≥ 6.9 over the front lane.
- Banner 2.10 ± 0.2 wide, tips z 3.0 ± 0.2, top 9.2; crossarm end x 9.3 ± 0.2.
- Ivy leaves 0.85–1.10 across; ≤ 10 % of the leaf area within 15° of edge-on at any 5° azimuth step (STAGES).
- Kit props: crate 2.30, barrel 2.72, table top 2.60, mat 0.16 thick.

### 4.5 Stages 2 and 3

- **Stage 2:**
  - Every shell closed and manifold, **0 bowties**, 0 boundary, wire or loose elements; no zero-area faces; n-gons
    triangulated.
  - **0 winding errors per shell** (`bmesh.ops.recalc_face_normals` per shell, then a parity ray test): the chipped
    block rings, the canvas tabs and grid, the swallowtail and emblem shells, the leaf lenses are where a reversed face
    slips in (044's wedge).
  - **Thin corners:** report the count under 3°, fail only under 0.3° (the M064 / M066 ruling).
  - Origin at the bbox bottom centre, transforms applied, every stored point re-checked.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box, `sw.py`)

| Swatch | Hex (HSV) | Use |
| --- | --- | --- |
| Timber (Structure) | `#9F5126` (21°, .76, .62) | posts, beam, crossarm, props (`m070_timber`) |
| Canvas (Cloth) | `#F6E0BE` (36°, .23, .96) | canvas; renders lighter, `#FEEEC3` |
| Stone (Ruin) | `#BBAFA5` (27°, .12, .73) | blocks, rubble, footings (warm grey, R > G > B) |
| Foliage (Plants) | `#5D9051` (108°, .44, .56) | swatch only: every rendered green is lime-olive 70–83° (§5.2) |
| Fabric (Banner) | `#C11F24` (358°, .84, .76) | banner |
| Header blue (no label) | `#418AC6` (207°, .67, .78) | the mat stripes (rendered `#3E5761`) |

### 5.2 Rendered regions (`samp.py`; median / lit quartile / shade quartile)

| Region | Median | Lit Q | Shade Q |
| --- | --- | --- | --- |
| Wood, whole cell: f34 / r34 / front / side / rear / top | `#7D421A` (24°, .79, .49) / `#7D461A` / `#7A4519` / `#703F17` / `#7B4416` / `#704A26` | `#BB661D` / `#B7601D` / `#B16119` / `#B45B1B` / `#C4641A` / `#9E6931` | `#3C1E10` / `#3E2110` / `#3C1F10` / `#3A1F0E` / `#34180A` / `#3E2515` |
| Posts: FR front / FR f34 / FL f34 / back f34 / exploded / close-up A | **`#964914` (24°, .87, .59)** / `#934816` / `#80421D` / `#824014` / `#884316` / `#AA571B` | `#CA6717` / `#C66317` / `#C55F19` / `#AD5816` / `#C66213` / `#C7641C` | `#502711` / `#5E290F` / `#46281F` / `#592612` / `#5C2B14` / `#5E2D12` |
| FR post top (cut end, f34) | `#E2871F` (32°, .86, .89) | | |
| Props (f34, under the canvas): crate / barrel / table / exploded barrel / bench | `#69371A` / `#75370E` / `#522B16` / `#884114` / `#8D4819` | `#B46727` / `#BA5F14` / `#8F4F1E` / `#D06C19` / `#CA6D23` | `#33170C` / `#361607` / `#28150D` / `#461F0D` / `#4E240F` |
| Close-up B beam (underside, shade) | `#713C20` | `#B06535` | `#5E331C` |
| Bedroll body / end caps / strap; exploded roll | `#82421F` / `#F09D1A` / `#72482E`; `#FBC34E` | | |
| Mat (f34 R) / stripe (f34 T) | `#CC8D38` (34°, .73, .80) / `#3E5761` (197°, .36, .38) | `#F4AA39` / `#58787A` | `#A8763C` / `#272D3A` |
| Rope: FR lashing / FL lashing / close-up A / FR collar | **`#F2AF4B` (35°, .69, .95)** / `#F0B656` / `#F3AE4C` / `#CA822C` | `#FBC75B` / `#FBE285` / `#FCC961` | `#CF7F22` / `#CA8B2E` / `#DB9439` |
| Canvas: f34 / front / side / exploded / top / close-up A | `#FEF0C8` (44°, .21, 1.0) / `#FEF0C7` / **`#FEEEC3`** / `#FEEEC4` / `#FDE4B8` / `#FDE6BB` | `#FEF2CA` / … | `#FDE8C0` / `#FAE5BD` / `#F5DAAC` / … |
| Canvas underside (close-up B) | `#E9C9A4` (32°, .30, .91) | | |
| Stone: f34 / front / side / **rear** / top / exploded / **close-up C** / rubble | `#958484` (0°, .11, .58) / `#958681` / `#A19190` / **`#A6958F` (15°, .12, .65)** / `#D1C2B9` / `#A48A80` / **`#B5A29F` (8°, .12, .71)** / `#AEA4A7` | `#DDC8C5` / `#D1B9AF` / `#C7B2AB` / `#C7AFA7` / `#EAD8D3` / `#DCC7B7` / `#DEC4BB` / `#F5EDE1` | `#645957` / `#665B55` / `#635950` / `#6D6465` / `#5E5950` / `#6F615D` / `#6D666B` / `#6C6A75` |
| Back-post footing (shade) | `#635E6B` | | |
| Ivy: f34 / r34 / close-up C | `#718A0F` (72°, .89, .54) / `#6E8B09` / `#64821B` | `#B8D505` / `#B9D604` / `#B1C81F` | `#3A4915` / `#2E410C` / `#4D6020` |
| Ground plants: grass / fern (f34) | `#5D7005` / `#497208` (83°) | `#A7B708` / `#6E9E0B` | `#263503` / `#264505` |
| Banner: f34 / front / emblem | `#D61B1F` (358°, .87, .84) / `#D1161C` / `#FCF0F0` | `#DF1E22` / `#E01C1F` | `#A31015` / `#990B11` |
| Dark pole / iron sleeve / dark crossarm segment | `#52362F` (11°, .43, .32) / `#6B534E` / `#715750` | | |
| Barrel hoops, outlines (K) | `#2E2626` | `#362E33` | `#150F12` |

### 5.3 How the colour works

- **One timber** (`m070_timber`) for posts, crossbeam, crossarm, toggles, table, crate and barrel staves. The props'
  darker f34 medians are the canvas's shade; the exploded barrel and bench render as the posts. **Per-piece Tint 0.05.**
- **Cut ends (`m070_timber_end`, by role):** the post tops, the crossbeam's and crossarm's end faces, the toggle ends (the
  f34's bright FR top `#E2871F`).
- **Positional bands:** each post's lowest 40 % one step toward `m070_timber_deep` (§3.12); the crate one step deeper
  overall (by role, M066's crate); table one step deeper.
- **Canvas:** `m070_canvas`; `m070_canvas_deep` over three steps along the hem (0.5) and on the corner tabs; the
  underside is lighting (close-up B), never paint.
- **Stone:** `m070_stone` on the blocks; **`m070_stone_light`** on chip faces, rubble tops and the footings' tops (role:
  broken and freshly exposed faces read pale); the bottom course's lowest 0.5 one step toward `m070_stone_dark` (ground
  grime); blocks Tint 0.05 per block so the wall reads as separate stones (the sheet's block-to-block variation).
- **Ivy (M056's roles, never by facing):** **lime** ≈ 40 % (outer layer, lip and top leaves, run tips), **green** ≈ 35 %
  (body), **dark** ≈ 25 % (under-layer next to the stone, the lowest third); stems `m070_stem`; moss patches banded by
  height (lime crown, green rim: M056 `_paint_cushion`).
- **Rope:** `m070_rope` with one strand in four `m070_rope_deep`. **Banner:** `m070_banner`, emblem `m070_cloth_white`
  (hard). **Dark pole:** `m070_pole`; sleeve and hoops `m070_iron`.
- **Bedroll:** `m070_leather` body, `m070_gold` caps, strap `m070_rope_deep`. **Mat:** `m070_mat`, stripes `m070_stripe`
  (hard).
- **Hues stay together:** timber 22–26°, s 0.80–0.88 rendered; rope 33–38°; canvas 38–45°, s 0.18–0.26; stone warm
  pink-grey (R ≥ G ≥ B, h 0–25°, s 0.08–0.16) — **never lavender**: the sheet's lavender shade quartiles are lighting;
  ivy 70–78°.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m070_timber` | front FR post **`#964914` ± 12** (swatch `#9F5126`) | 22–26°, 0.80–0.88 | posts, beam, crossarm, toggles, props | rough 0.85 |
| `m070_timber_end` | f34 FR top `#E2871F` ± 15 | 30–34°, lighter than timber by ≥ 25 G | cut ends | rough 0.8 |
| `m070_timber_deep` | `#5E2B12` ± 12 (shade quartiles) | 20–24°, v ≤ 0.40 | post feet (blend), crate / table step | rough 0.9 |
| `m070_canvas` | side_sheet `#FEEEC3` ± 10; start from M064's calibrated `#FDE4BC` | 38–45°, 0.18–0.26 | sheet | rough 0.95, low spec |
| `m070_canvas_deep` | `#E6C8A2` ± 12 (close-up B `#E9C9A4`) | 32–38° | hem, tabs | rough 0.95 |
| `m070_stone` | rear_sheet `#A6958F` ± 12; close-up C `#B5A29F` ± 12 (swatch `#BBAFA5`) | R ≥ G ≥ B, 5–25°, s 0.10–0.16 | blocks, footings' sides | rough 0.9 |
| `m070_stone_light` | close-up C lit `#DEC4BB` ± 12 | warmer, lighter | chips, rubble tops, footing tops | rough 0.9 |
| `m070_stone_dark` | `#6D6465` ± 12 (rear shade) | as stone, v ≤ 0.45 | grime band (blend) | rough 0.9 |
| `m070_ivy_lime` | `#B4D00A` ± 15 (lit quartiles) | 68–74°, s ≥ 0.85 | outer leaves, moss crowns | rough 0.8 |
| `m070_ivy` | f34 ivy `#718A0F` ± 12 | 70–76° | body leaves, moss rims | rough 0.8 |
| `m070_ivy_dark` | `#3A4915` ± 12 | 72–80°, v ≤ 0.32 | under-layer leaves | rough 0.85 |
| `m070_stem` | M056's calibrated `stem` (brown) | 20–30° | ivy stems, pads | rough 0.9 |
| `m070_rope` / `_deep` | f34 FR lashing **`#F2AF4B` ± 12** / `#CF8A2C` | 33–38°, 0.62–0.75 | lashings, collars, band, tail; deep strand, bedroll strap | rough 0.95 |
| `m070_banner` | f34 `#D61B1F` ± 12 (swatch `#C11F24`) | 355–3°, s ≥ 0.82 | banner | rough 0.9 |
| `m070_cloth_white` | `#F8F0EC` ± 8 | s ≤ 0.06 | emblem | rough 0.9 |
| `m070_pole` | `#52362F` ± 12 | 8–16°, s 0.35–0.50 | dark pole | rough 0.85 |
| `m070_iron` | `#4E3C37` ± 12 (sleeve `#6B534E` lit, hoops `#2E2626` shade) | s ≤ 0.30, v 0.25–0.40 | sleeve, cap, barrel hoops | rough 0.55, metal 0.4 |
| `m070_leather` | bedroll `#82421F` ± 12 | 20–24° | bedroll body | rough 0.8 |
| `m070_gold` | bedroll caps `#F09D1A` ± 15 | 34–38°, s ≥ 0.85 | caps | rough 0.8 |
| `m070_mat` | f34 mat `#CC8D38` ± 15 | 32–36°, 0.65–0.75 | mat | rough 0.95 |
| `m070_stripe` | `#47707A` ± 15 (rendered `#3E5761`, swatch `#418AC6`) | 190–205° | mat stripes | rough 0.95 |

**Calibration warnings:**
- **Stone warm pink-grey, not lavender and not tan** (066 decision 15; W10's lilac stone; M056's studio tan): R ≥ G ≥ B
  on every rendered stone median; the rear_sheet median within 12 of `#A6958F`.
- **Canvas** (M064 ruling 1 / M066 ruling 6): the key-lit canvas may clip in the kit studio; keep the hue-correct cream
  and judge C on front / side; never shift toward salmon or yellow.
- **Timber orange-brown, not red** (W08; W10 `#8A4A22`): hue ≥ 22°, s ≥ 0.80 on the front FR post; cut ends a real step
  but ≤ v 0.98.
- **Rope golden, not lemon** (`#F2AF4B`, 35°), distinct from the mat (34°, s 0.73, v 0.80: darker) and the bedroll caps
  (36°, s 0.89).
- **Ivy lime-olive, not the swatch's cool green** (§5.1): rendered medians 70–76°.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- Posts: by height above the footing (lowest 40 %). Stone: by height on the bottom course's lowest 0.5. Canvas: by
  distance from the hem (0.5) and on the tabs. Moss: by face-centre height within each patch (M056).
- **Hard edges only** where materials meet: rope | wood / canvas, iron | wood, banner | emblem, stripe | mat, cap |
  leather, timber_end | timber, leaf | stone.

### 5.6 Texture (Tint) and finish

- **Tint:** 0.05 per wooden piece, 0.05 per block (broad, per block, never per triangle), canvas `K.texture` mottling
  0.03, ivy 0.04 per leaf, iron 0.02.
- **Finish:** wood rough 0.85, canvas 0.95, stone 0.9, rope 0.95, ivy 0.8, iron rough 0.55 / metal 0.4. No emission.

### 5.7 Re-measure (final renders against the sheet, same masks)

- **Timber:** front FR post median within 12 of `#964914`; f34 W median within 15 of `#7D421A`.
- **Stone:** rear_sheet S median within 12 of `#A6958F`; front S within 15 of `#958681`; R ≥ G ≥ B.
- **Canvas:** side / front C median within 10 of `#FEEEC3`, s ≥ 0.18. **Rope:** f34 R lashings within 15 of `#F2AF4B`.
- **Ivy:** f34 G median hue 70–76°, lime share of G 35–50 %. **Banner:** within 12 of `#D61B1F`.
- **Shares** per §1.2.

## 6. Joins and contact (no floating pieces, no buried pieces)

- **Shells:** every block, chip-free rubble, footing, post, beam, toggle, rope run, the canvas, banner pieces, emblem
  shells, ivy stems, pads, leaves, moss patches and prop parts are closed shells, all in one hero object.
- **Chain to the ground:** blocks → courses → ground; rubble and the fallen block → ground; footings → ground; posts →
  footings; crossbeam → FL post and the side wall; lashings, collars, toggles → posts; canvas → toggles; C4 tail →
  canvas; crossarm → FR lashing and pole; pole → ground; banner → crossarm; ivy stems → stone; leaves → stems; moss →
  block tops; props → ground; mat ↔ bedroll.
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**. A shell floats if its nearest distance
  to every other shell and the ground is > 0.03, or it doesn't chain to the ground. New risks: upper-course blocks with
  jitter (keep the 0.015 seat), chips leaving a block corner hanging, the canvas tabs on the toggles, the C4 tail, leaves
  pushed off the stone by `push_clear`, moss on chamfered tops.
- **Buried shells:** nothing more than 0.05 inside anything beyond its stated seat. Ray parity against every block, post
  and prop as a solid after the final placement (`m047._Solids`, M056's `bury_report`): no leaf inside a block (046).
- **Thin slabs hide pass-throughs** (M064): run **`pierce_report`** on the canvas (posts, toggles, lashings, the back
  wall's top course near C2) and the banner (crossarm, pole). Target 0.
- **No intersections between big pieces:** posts clear the blocks (the back post's back face 0.35 off the wall); the
  crossbeam rests on the top block, not through it; the barrel clears the FR footing.
- **Walk report** (§2.10), minimum clearances printed.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0 (M019–021 had them at leaf hubs).
- **Winding:** 0 errors per shell, parity ray test, not only the signed volume.
- **Parts:** each exported part self-contained and square to its axes (M050 finding 7).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing emissive and no effect in any assembled view; the notes say "No baked lighting,
effects or weathering textures". The exploded's lantern is the only light source drawn (§3.10). Cast shadows are the
illustration's.

- **Stage 5 (lighting): skipped and recorded.** No emissive materials; no light painted on the stone or canvas.
  Studio notes (Requires Manual Validation): the stone reads warm pink-grey in daylight, not lavender; the canvas cream;
  the interior's shade comes from the canvas, not paint.
- **Stage 6 (VFX): skipped and recorded** (decision §8.9): no sockets on the hero or parts. Check the export STATS line
  reports **0 sockets**. Alternative: the lantern option of §3.10 with one steady `heat_glow`.
- **Collision (decision §8.11):**
  - **Hero `precise`** (PreciseConvexDecomposition): walls, rubble, posts and props solid; the lanes and the interior
    must stay open. **Requires Manual Validation in Studio:** a default character walks in on both lanes, lies on the
    mat, and the decomposition doesn't fill the space under the canvas. Fallback: hero `none` plus Studio colliders
    (wall boxes per skyline step, three post boxes, prop boxes, the canvas non-colliding).
  - Parts: `RuinedLeanToWallBlock` `box`; `…WallSection` `precise`; `…Rubble` `hull`; `…Canopy` `none`; `…Post` `hull`;
    `…Banner` `none`; `…Bedroll` `none`; `…Table` `box`; `…Crate` `box`; `…Barrel` `hull`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched all 2600 names in `art/roblox/kit/**/manifest.json` and the repo text (`git grep`) for
Ruin, LeanTo, Shelter, Refuge, Rubble, Wall, Block, Camp and the candidates:
- **W10:** `RuinLeanTo`, `RuinLeanToAbandoned`, `…BedMat`, `…CanvasCanopy`, `…Peg`, `…SnowShelter`, `…TraderStall`,
  `…UprightPost`, `…WallAnchor`, `…WallBlocks` (and `VFX_RuinLeanTo*_heat_glow_1`); `CampAwning*` (incl.
  `CampAwningLeanTo`, `CampAwningLongShelter`); `TimberHut*`. **W16:** `BlockWall*` (incl. `BlockWallBlockLarge / Medium
  / Small`, `…BrokenStepped`, `…CopingStone`, `…CornerBlockStacked`). **Other:** `OvergrowthRuinBlock` (M056),
  `MossAndIvyWallStrip`, `CourtyardFloorRubbleBlocks`, `…BrokenRubble`, `DoubleGateRuined`, `StoneStairRuined`.
  **Decided, not exported:** `CanvasShelter*` (M066), `TrestleTableSet*` (M067), `TimberCabin*` (M068).
- **`RuinedLeanTo` (and every `RuinedLeanTo…` part name below), `RuinShelter` and `m070` occur nowhere** in the manifests
  or the repo text. No owned name is a substring of them (`RuinLeanTo` is not a substring of `RuinedLeanTo`).

| Object | Part | Why |
| --- | --- | --- |
| `RuinedLeanTo` | hero: walls, rubble, footings, posts, crossbeam, lashings, collars, toggles, canvas, banner set, ivy, moss, bedroll, mat, crate, table, barrel | the sheet's title; W10 owns `RuinLeanTo*` |
| `RuinedLeanToWallBlock` | one chamfered block (2.0 × 2.4 × 1.65) with one broken corner | "Ruin Wall Blocks (modular)" |
| `RuinedLeanToWallSection` | the exploded's chunk: a stepped 3-block-wide, five-course section with a 1 × 2 opening under a bridging block and an ivy run | the exploded (§3.14) |
| `RuinedLeanToRubble` | a loose broken block with a moss patch | "Stone Rubble (assorted)" |
| `RuinedLeanToCanopy` | the canvas with its four toggles and the C4 tail | "Canvas Canopy" |
| `RuinedLeanToPost` | the FR post on its footing with lashing, toggle and collars | "Upright Post (2x)" |
| `RuinedLeanToBanner` | crossarm, knob, dark pole, sleeve, banner, emblem | "Banner (cloth)" |
| `RuinedLeanToBedroll` | bedroll on its mat | the exploded's roll; W10 owns `…BedMat` |
| `RuinedLeanToTable` | the open-frame side table | "Table / Bench" |
| `RuinedLeanToCrate` | X-braced open crate | "Crate" |
| `RuinedLeanToBarrel` | open barrel with two hoops | "Barrel" |

- Palette keys `m070_*` (§5.4). Collection `Kit/M070 Ruined Lean-To`. Sockets: none. Stored points `m070_offset`,
  `m070_centre`, `m070_sleep`, `m070_corner` (hero); `m070_course` (WallBlock), `m070_ties` (Canopy), `m070_top` (Post).

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **FR post 12.0 (0.0816 stud / px), wall courses 1.65, peak 13.2, side wall 8.25, ties 8.0 / 9.9 / 9.2;
   hero ≈ 21.0 × 13.1 × 13.2** (recommended: M066's post height, kit table height, M056's ruin course). Alternatives: FR
   14.5 (the sheet's hanging corner clears a head; the wall 16 tall, props toys) or 10.0 (no walk-in).
2. **Budget (§4.3):** **full asset: ceiling 4000, plan 3800–3950, every part under 1000, cut order as listed**
   (recommended). Alternative: 6000 (README's building class allows 8000) for a second wall row and 50 ivy leaves.
3. **Build frame and origin (§1.1, §2.13):** **front −Y (open, banner at the right), side wall −X, back wall +Y; origin at
   the bbox bottom centre with the offset, centre, sleep and corner points stored** (recommended).
4. **Walls (§2.2, §3.7):** **59 chamfered blocks 2.4 deep in running bond; the skyline of §2.2; eight chips, three
   missing blocks, one fallen block; no opening in the hero** (recommended). Alternative: a second row behind the peak.
5. **Canvas (§2.4, §3.6):** **one closed 0.10 sheet tied by toggles at FL 8.0, back 9.9, FR 9.2; the free corner C4 at
   6.6 with a 0.7 tail; crease diagonals to the centre** (recommended). Alternative: C4 at the sheet's 5.1.
6. **Ivy and moss (§2.7):** **four runs, ≈ 30 M056 lens leaves, eight flat moss patches** (recommended).
7. **Posts (§2.3, §2.5):** **three square posts on stone footings, golden X-lashings over toggles, three collars, a band,
   a crossbeam from FL onto the side wall** (recommended).
8. **Banner (§2.6):** **on a round crossarm through the FR lashing, a dark pole with an iron sleeve, 2.1 × 6.2, two-point
   swallowtail, emblem both faces** (recommended).
9. **Light and VFX (§3.10, §7):** **none: no lantern, no emissive, no socket** (recommended, the sheet's notes).
   Alternative: a lantern on the FL post with a steady `heat_glow`.
10. **Grass (§3.11):** **none in the hero; Studio scatter** (recommended). Alternative: two fern clumps.
11. **Collision (§7):** **hero `precise` with the Studio walk-in check (fallback `none` + colliders); parts as listed**
    (recommended).
12. **Comparison cameras (§2.12):** **`front_sheet (0, 3)` governs X and heights, `side_sheet (90, 3)` Y, `rear_sheet
    (180, 3)` the outer face; `f34_sheet (−15, 12)` (probe az −5 … −25, e 8–16) the read and dressing; `r34_sheet (140,
    15)` and `top` (mirrored) content only; close-ups `junction_cu`, `underside_cu`, `block_cu`, `ruin_cu`, `walk`,
    `inside_cu`, `thumb`, `spin`; parts and exploded shots; scale shot. Floor hidden in every `*_sheet` render**
    (recommended).
13. **Exports (§8 table):** **the hero plus ten parts** (recommended). Alternative: seven (drop Table, Crate, Barrel and
    reuse M064's `CanvasTentCrate` / `CanvasTentBarrel`).
14. **Colour (§5):** **orange timber `#964914` with cut ends `#E2871F`; golden rope `#F2AF4B`; cream canvas `#FEEEC3`;
    warm pink-grey stone `#A6958F` with pale chips and a grime band, never lavender; lime-olive ivy in three roles; red
    banner with a white emblem; dark pole `#52362F`; by role and position, never by facing** (recommended).
15. **Props (§3.8):** **kit sizes (crate 2.30, barrel 2.72, table top 2.60)** (recommended).
16. **Name:** **`RuinedLeanTo`** (recommended: the sheet's title, not owned) or `RuinShelter`.

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **The old lean-to's failures (W10 / MODEL_PROGRESS row 82: "regular brick wall (ref broken ruin, moss/ivy); flat
   canvas"; its verifier: thin flat walls, thin posts, flat canopy, ivy blobs; CHECKLIST 6/10).** A stepped broken
   skyline with chips, gaps and a fallen block; 2.4-deep chamfered blocks; chunky square posts; a creased, sagging
   canvas with a hanging corner; ivy as leaf runs on stems.
2. **A regular wall** (§13.5): running bond, block-to-block Tint, the skyline steps of §2.2, damage by role — never a
   grid of identical boxes, never random jitter on every block.
3. **Ivy that hides the masonry or reads as blobs** (§13.5; M056 round 1; 054 / 057 / 058): ≤ 15 % of any face; chunky
   five-point leaves facing out; the 5° azimuth sweep (STAGES) ≤ 10 % edge-on leaf area; stems visible.
4. **Moss as balls or gems** (M047; M056 blocker): flat lumpy patches, H : W ≤ 0.2, height-banded colour.
5. **Single-sided or see-through canvas** (M064 pitfall 2): a closed 0.10 slab; `underside_cu` and the spin prove it.
6. **A canopy you can't walk under** (M066 decision 1): underside ≥ 6.9 over the front lane; the walk report; the Studio
   check recorded as Requires Manual Validation.
7. **Floating or buried pieces** (STAGES; 035 / 036; 046): toggles, tabs, the C4 tail, leaves, moss, chips, the crossbeam
   on the wall. Count: floating 0, buried 0; report the worst sink per kind.
8. **Pass-throughs a bury report can't see** (M064 stage 1): `pierce_report` 0 on the canvas and banner.
9. **Rope as flat collars or thin outlines; loops sinking into square timbers** (M048 / M051 / M064 minor 1): twisted
   tubes Ø 0.22–0.26; `hull_loop` round the posts; the X of each lashing visible in `junction_cu`.
10. **Knot tails reading as nuts, faint ties, slab rolls** (M064 minors 4, 5, 8): the C4 tail is a short twisted rope with
    a square toggle, not a ring; the bedroll is an 8-sided roll with caps and a strap, not a flat slab.
11. **Canvas blown out or salmon** (M064 ruling 1, M066 ruling 6): hue-correct cream; judge C on front and side.
12. **Lavender, blue-grey or tan stone** (066 decision 15; W10's lilac; M056 minor 2): R ≥ G ≥ B; the rear_sheet median.
13. **Red or flat-orange wood** (W08; W10 `#8A4A22`): hue ≥ 22°, s ≥ 0.80; per-piece Tint.
14. **Colour by facing** (042 ruling; 054 m9): the lavender stone shade, the dark undersides and the canvas underside
    are lighting. `K.check` facing correlation < 0.5 per material (M056's moss waiver applies only to height-banded
    patches).
15. **Hard colour bands** (M051 finding 5; M052 finding 3): post feet, grime and hem blend over three steps.
16. **Egg rubble** (M034 / M037): chamfered blocks with broken corners and flat bottoms, never `K.hull_rock` balls.
17. **Winding and non-planar quads** (044; M051 finding 8): 0 per shell; triangulate the canvas grid at build time.
18. **Thin faces** (M064 / M066 rulings): report under 3°, fail only under 0.3°.
19. **Proportions from the stylised cells** (§3.2–§3.7): front and rear set X and heights, side sets Y, the f34 the read;
    the top is mirrored and content only.
20. **Tiny details that vanish** (WorldModeling §18): `thumb` must show the skyline, the ivy curtain, the canvas V and the
    banner emblem.
21. **Names and scope.**
    - No `RuinLeanTo*`, `CampAwning*`, `BlockWall*`, `OvergrowthRuinBlock`, `CanvasShelter*`, `TimberCabin*` names.
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit the frozen shared helpers (`kit_models.py`, `kit_mcp.py`, `build_kit.py`, `lib/vfx.py`) or other models'
      builders; import from committed ones (`m047`, `m048`, `m052`, `m056`, `m067`), copy from `m064` / `m066`; don't
      touch other models' collections.

## Open questions for the main session

1. **Scale (§1.1):** FR post 12.0 (0.0816 stud / px: M066's post height, the side table lands on the kit's 2.60, wall
   courses 1.65 like M056)? The sheet's own hanging corner then sits at 5.1, below head height. Recommended: yes, with
   the corner raised (question 4).
2. **Budget (§4.3):** STAGES' 4000 (plan ≈ 3940, ≈ 30 ivy leaves, single-row walls) or the building class (6000–8000)?
   Recommended: 4000 as briefed; the risk is M056's "ivy thinner than the sheet" minor. Alternative: 6000 for a second
   wall row behind the peak and ≈ 50 leaves.
3. **Layout reading (§3.2–§3.5):** the f34 is a near-frontal high view, the r34 a true rear view, the top cell mirrored,
   the rear cell's outside crates a slip. Recommended: as stated; the verifier compares the top cell mirrored.
4. **Hanging corner (§3.6):** C4 at 6.6 so a walk lane keeps ≥ 6.9 under the canvas (recommended), or the sheet's 5.1
   (a head-height flap; no clean front lane)?
5. **Wall depth (§3.7):** single 2.4-deep blocks (recommended) or a second row behind the peak (side cell's 3.9 band,
   +≈ 380 tris; needs question 2's alternative)?
6. **Lantern (§3.10):** none, as the assembled views and notes (recommended), or the exploded's lantern on the FL post
   with a steady `heat_glow`?
7. **Grass (§3.11):** none in the hero (recommended) or two fern clumps?
8. **Parts (§8):** ten parts including a WallSection with the exploded's opening (recommended), or seven reusing M064's
   crate and barrel?
9. **Name:** `RuinedLeanTo` (recommended: the sheet's title, unowned, not containing `RuinLeanTo`) or `RuinShelter` (no
   resemblance to the W10 name)?

## Decisions (main session, 2026-11-02)

1. **Scale:** the front-right post is 12.0 tall, as M066's tall posts (0.0816 stud per sheet pixel). Props keep kit sizes
   (crate 2.30, barrel 2.72); their 20 % shortfall against the sheet is a recorded miss.
2. **Budget:** ceiling 6000 tris (a structure about 21 × 13 × 13, between the 4000 props and 8000 buildings), plan about
   4800–5400. Spend the extra on the ivy and moss so it doesn't repeat M056's "ivy thinner than the sheet" minor, not
   on a second wall row. Every part stays under 1000.
3. **Sheet reading as the study gives it:** the f34 is a near-front high view (az about −15), the r34 a true back-right
   view, the top view is mirrored, and the crates drawn outside the wall in the rear view are a slip.
4. **Hanging corner at 6.6** (sheet 5.1) so one walk lane keeps at least 6.9 under the canvas; the front edge still
   reads as a V.
5. **Walls of single blocks 2.4 deep;** the side view's 3.9-deep band is a recorded miss.
6. **No lantern, glow or VFX socket** in the hero (the lantern appears only in the exploded view; the sheet notes say
   no effects).
7. **No grass in the hero;** ground scatter is placed in Studio.
8. **Hero plus ten parts,** including a wall section with the exploded view's opening.
9. **Name `RuinedLeanTo`.**
