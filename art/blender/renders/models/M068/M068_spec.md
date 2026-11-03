# 068 Timber Hut — spec

Reference: `art/blender/assets/references/068.png` (1024 × 1536 px). INDEX.md row 68: "Flintborn timber hut model study".
The sheet's header reads **"PAGE 67/132"** (top right), title **"TIMBER HUT"**, subtitle "INDIVIDUAL MODEL STUDY", footer
"FLINTBORN — INDIVIDUAL MODEL STUDY" (our number is INDEX's 068, §3.1).
Builder: `art/blender/kit/mcp/m068.py` → `build()` (stages 1–6 recorded at the end of this file). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows an effect: three glowing lanterns
with amber glass**, and a stone chimney that implies smoke (§7). The subject is **one small walk-in gable-roofed timber
hut with its dressing**:
- a **stone foundation course** of pale grey blocks with bigger **white corner blocks**;
- a **floor** of planks on it;
- **walls of thick horizontal planks** between **square corner posts**, a **barred window** in each long wall;
- the **door** in the front gable, under a **front gable frame**: two tall posts with golden foot caps, a lintel, a
  collar, and **crossed bargeboards** lashed at the apex;
- a **cream canvas roof**: two slopes on rafters and a **ridge beam** whose square end projects at each gable, with
  **golden rope ties** along both eaves and projecting **eave-beam ends** fixed with **iron bracket plates**;
- a **square stone chimney** with a dark flue;
- **two-step wooden stairs** to the door;
- **three lanterns**: one hanging from an iron eave bracket, two on wall brackets flanking the door;
- a **red banner with a white diamond** on a free-standing pole with a crossarm;
- **two hooped barrels**, an **X-braced crate**, loose white stones and grass tufts round the base.

Sheet text (paraphrased):
- **Title block:** "FLINTBORN / INDIVIDUAL MODEL STUDY", "TIMBER HUT", "PAGE 67/132".
- **"1. ASSEMBLED VIEW (FRONT 3/4)"** and **"2. ASSEMBLED VIEW (REAR 3/4)"**: the hut with its dressing from the
  front-left and from the back-left (§3.3).
- **"3. ORTHOGRAPHIC VIEWS (CONSISTENT GEOMETRY)"**: "FRONT VIEW", "SIDE VIEW (RIGHT)", "REAR VIEW", "TOP VIEW". What
  each cell really shows: §3.2–§3.5.
- **"4. EXPLODED CONSTRUCTION (MAIN PARTS)"**, labels:
  - "Roof Panel (Left)", "Ridge Beam", "Roof Panel (Right)", "Chimney", "Banner Pole + Banner", "Lantern (x2)";
  - "Wall Panel (Left)", "Wall Panel (Rear)", "Wall Panel (Right)" (written twice; one leader points at a small white
    stone), "Front Gable Frame", "Floor", "Stone Foundation (x4)", "Stairs".
  - Unlabelled: the doorframe with the door (two posts, a projecting lintel, a plank door with strap hinge and ring
    handle), a barrel, a crate, a small stone block with a square hole, grass tufts, dashed drop arrows.
- **"5. CONSTRUCTION CLOSE-UPS"**:
  - **"A. ROOF TO WALL JUNCTION"**: an eave beam's chamfered end projecting past the wall under a rafter, a dark iron
    plate with two rivets on its side, a golden wooden peg through the plate, the canvas on top.
  - **"B. FOUNDATION / WALL BASE"**: a big pale corner block under the corner post, grey blocks along the wall base,
    grass at the foot.
  - **"C. UNDERSIDE VIEW (ROOF)"**: from below, a grid of rafters and purlins with the canvas between them, the chimney
    passing through.
- **"6. MATERIAL PALETTE"**: Timber (Primary), Canvas (Roof), Stone (Foundation), Metal (Fittings), Banner (Cloth),
  Foliage (Accent).
- **"7. MODELING NOTES"** (paraphrased): chunky low-poly primitives (boxes, wedges, cylinders); a bold silhouette and
  clean flat-shaded faces; the roof is two canvas panels on a timber frame with a central ridge beam; walls are
  horizontal planks with vertical corner posts; the foundation is simple stone blocks; reuse modular parts (wall
  panels, roof panels, beams, doorframe, stairs, props); keep scale and proportions consistent across the views.
- **Game context and the old kit:**
  - **W10 row 3 `TimberHut`** (`art/blender/scripts/kit/W10/timber_hut.py`; manifest `art/roblox/kit/W10/manifest.json`;
    goals `art/blender/renders/kit/W10/timber_hut_goals.md`; compare `timber_hut_compare.png`) is the old kit's hut,
    from a different but related sheet. **Exported** hero `TimberHut` **12.97 × 10.68 × 12.47, 4398 tris, `precise`, 2 ×
    `heat_glow`**; parts `TimberHutCornerPost`, `…Doorframe`, `…Floor`, `…RidgeBeam`, `…Roof`, `…WallPanel`; variants
    `…Standard`, `…OpenWorkshop`, `…Weathered`. Its goals asked for a door ≥ 4 wide × 7 tall, floor z ≈ 1.2, interior
    clear ≥ 7, `chimney_smoke` at the chimney, "smoke thin and pale, no dark smear". `MODEL_PROGRESS.md` row 83: **"flat
    plank walls, no framing/window/door frame; plain roof"**; `art/reference/kit/CHECKLIST.md`: TimberHut **6.5/10**.
    Its goals log: wood rendered "more orange than the reference's brown" because it had to use the shared
    `w10_wood #8A4A22`.
  - **Siblings:** M064 `CanvasTent` (passed, exported: twisted rope, closed canvas slabs, Neon lanterns with a steady
    `heat_glow` halo, walk-in rulings, the canvas-clipping ruling), M066 `CanvasShelter` and M067 `TrestleTableSet`
    (decided; furniture scale **table top 2.60, seats 1.50**), M052 `TimberBoardwalk` (passed timber builder; stair
    risers 1.12). WorldModeling §13.1 (timber vocabulary), §13.3 ("Huts use a floor, corner posts, wall panels,
    doorframe, and roof panels … Do not model the outside as a solid cube with a doorway painted onto it"), §13.8
    (crate, barrel, lantern, banner recipes).
  - **Budget:** `art/blender/README.md` → "≤ 8,000 for buildings and large trees"; STAGES' generic 4000 is for props
    and furniture-scale assets (decision §8.2).

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is near-white
(`#FCFAF6`); pieces cast a soft neutral-grey shadow down and to the left (s < 0.05, v 0.85–0.93), which the masks drop.
Frame rules (from the zooms, ±3 px): header rule y ≈ 70; hero panels y ≈ 78–468 (title bars to y ≈ 100), divider x ≈
511; ortho panel title y ≈ 478–503, cell labels to y ≈ 530, cells to y ≈ 740, dividers x ≈ 273, 513, 762; exploded
panel x 14–755, y 750–1295; close-up panel x 760–1011 (cells A y ≈ 780–945, B ≈ 950–1115, C ≈ 1120–1295); palette
panel x 14–508, y 1305–1475; notes panel x 514–1011; footer rule y ≈ 1505.
- **Cells** (`bbox.CELLS2`): f34 (16,104,508,466); r34 (516,104,1010,466); front (16,532,272,738); side (276,532,510,738);
  rear (516,532,762,738); top (765,532,1010,738); exploded (14,770,755,1295); cuA (765,790,1008,945); cuB
  (765,960,1008,1110); cuC (765,1130,1008,1295).
- **Swatches** (inner boxes, sd ≤ 3.6): Timber (40,1352,88,1398); Canvas (117,1352,166,1398); Stone (195,1352,244,1398);
  Metal (275,1352,323,1398); Banner (353,1352,401,1398); Foliage (429,1352,478,1398).
- **Masks** (`cls.py`, HSV, h in degrees):
  - **W** timber and warm shade: (h 8–48 or ≥ 345), s ≥ 0.42, v ≥ 0.15, not B / Y; plus warm s 0.25–0.42 with v < 0.70.
  - **C** canvas: h 22–62, s 0.07–0.42, v ≥ 0.74. **R** rope ties: h 36–56, s ≥ 0.55, v ≥ 0.55, not Y.
  - **S** stone: s < 0.16, v 0.30–0.86, not C (drops the paper and the cast shadow). **K** dark: v < 0.30, not W / B
    (lantern frames, flue, window opening, outlines).
  - **B** banner red: (h < 12 or > 340), s ≥ 0.55, v ≥ 0.40. **Y** glow: h 33–62, s ≥ 0.70, v ≥ 0.88. **G** foliage: h
    62–170, s ≥ 0.28.
  - Wood value bands: **lit** v ≥ 0.85, **mid** 0.55–0.85, **shade** < 0.55.
  - Apply the same code to our renders (studio floor hidden, plain background).

**Scratch study material** (no Blender) in `<temp>\m068\` (the session scratchpad). No Pillow on this machine: the
scripts use Blender's bundled Python (`<blender dir>/5.2/python/bin/python.exe -I <script> < /dev/null`, numpy only)
with a small PNG reader / writer (`png.py`, from the 067 study); `load.py` caches the sheet as `sheet.npy`.
- **Helpers:** `m.py` (HSV, `hexs`, `hsvs`), `cls.py` (masks), `bbox.py` (cells, object boxes), `zoom.py` (`zoom.py x0
  y0 x1 y1 scale out.png [grid]`).
- **Measurements:** `bbox.py` (bbox, W : H, fill), `shares.py` (class shares and wood value bands per cell), `proj.py`
  (block model of the adopted layout, projected at any camera: §2.12).
- **Colour:** `sw3.py` (swatches), `samp.py` (class medians per cell and per named region, lit and shade quartiles).
- **Zooms:** `z_f34.png`, `z_r34.png` (2×), `z_f34_gable.png`, `z_f34_left.png`, `z_r34_gable.png` (3×, grid 10),
  `z_door.png`, `z_lwall.png` (5×), `z_fs.png`, `z_rt.png` (3×), `z_front.png`, `z_side.png`, `z_rear.png`, `z_top.png`
  (4×, grid 10: every ortho number below), `z_ex_tl.png`, `z_ex_tr.png`, `z_ex_bl.png`, `z_ex_br.png`, `z_ex_mid.png`,
  `z_cu.png`, `z_pal.png`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** a walk-in building with dressing: **building budget, hero ceiling 8000 tris (README), plan
  6200–7200; every part under 1000** (decision §8.2).
- **Overall read (check this first).** A **squat, warm-orange plank cabin on a pale stone plinth under a cream gable
  roof**, a little longer (along the ridge) than wide and about as tall to the chimney top as it is long:
  - **orange timber first** (walls, posts, gable frame, bargeboards, stairs, props), then the **cream roof**, then the
    **grey-white stone band** along the base, then the **red banner**, the **amber lantern glass** and the **dark
    lantern frames**: f34 W 58.9 %, C 18.3, S 11.2, K 3.5, B 3.4, G 2.9, Y 1.5, R 0.3; wood lit / mid / shade 16 / 37 / 48.
- **Focal silhouettes, in order:**
  1. The gable box: plank walls on the stone plinth, the cream roof with its crossed bargeboard tips and square
     ridge-beam ends, the chimney standing above the ridge.
  2. The front gable: tall door posts, lintel and collar, the plank door, the two lanterns, the stairs.
  3. The banner on its pole, the eave lantern, barrels, crate, stones; the eave ties, iron brackets, corner blocks.
- **Target size (decision §8.1):**
  - **Floor top z 2.60; door clear 3.60 W × 7.00 H (z 2.60–9.60); wall plates' top z 11.20; canvas ridge z 16.0;
    chimney top z 19.4.**
  - **Walls (corner posts' outer faces) 14.40 W (X) × 16.40 L (Y); roof 16.4 × 19.4 over the eaves and gables.**
  - **Hut alone ≈ 17.2 W × 21.2 L × 19.4 H (bargeboard feet, ridge-beam ends); hero with dressing ≈ 20.6 × 26.1 ×
    19.4** (§2.11).
  - Tolerances: floor ±0.03, door clear ≥ 3.5 × ≥ 6.9, plate top ±0.2, ridge ±0.3, chimney top ±0.4, footprint ±0.3.
  - **How it was derived.** No piece carries a real size, and the sheet's own proportions make the hut a doll's house:
    against the kit's barrel (2.7–2.8, M064 / M066) the side cell's barrel (52 px) gives 0.053 stud / px, a 3.0-tall
    door and a 5.4 eave. So the **door sets the scale** (the hut must be enterable), the **side and rear cells**
    (the only true elevations) set the heights and length, and the f34 sets the width:
    - Side cell (`z_side.png`): ground y 718.75, stone top 690, wall plate 618.75–630, roof band top (ridge) 573.75,
      chimney top 545, chimney x 439–464 (25 px); corner posts' outer faces x 321–471 (**150 px**), foundation 316–479
      (163), roof with bargeboards 307.5–482.5 (175); window frame 381–424 × 637.5–677.5, opening 391–415 × 644–670;
      four plank rows; four eave ties.
    - Rear cell (`z_rear.png`): the same heights to ±1 px; posts 157.5 px apart; window frame 612.5–656 × 636–677.5.
    - **In plate heights (ground → plate top = 100 px):** stone 0.29, ridge 1.44, chimney top 1.72, wall length 1.49,
      roof length 1.73, window opening bottom / top 0.48 / 0.74. **Ours (plate top 11.20):** stone 0.23 (decision
      §8.7), ridge 1.43, chimney 1.73, wall 1.46, roof 1.73 (bargeboard tips), window 0.49 / 0.78.
    - f34 (`z_f34_left.png`, `z_f34_gable.png`; post bases on the stone tops): the −X wall base runs (153, 47) px, the
      front gable base (180, −39) px → an ortho fit of **camera ≈ 40° off the front toward −X, ≈ 15° up**; then the
      long wall 238 px, the gable 235 px, wall height (stone top → plate top) 135 px: **L / H 1.76, W / H 1.74**.
      The f34 has mild perspective (its gable peak sits 40 px right of the base centre).
    - Top cell: roof 173 × 145 px (**along the ridge / across 1.19**; the side cell's roof is 175 px: same scale).
    - Door (f34 and front cell): clear width 0.36–0.55 H, clear height 0.80 H (f34) – 0.91 H (front cell).
    - Adopted: **H (floor → plate top) 8.60**; L 16.40 (L / H 1.91: between the side cell's 2.08 and the f34's
      1.76), W 14.40 (W / H 1.67, f34 1.74; L / W 1.14, top cell 1.17); door 7.00 = 0.81 H.
  - **Why this size.**
    - **Against the character (5.5):** the door is 1.27 C tall and 0.65 C wide (the 2 × 1 root part passes with 0.8 to
      spare each side); the interior is ≥ 7.8 clear under every member (1.4 C), 13.2 × 15.2 inside: room for four or
      five players and a 067 table set (2.60 top, 1.50 seats). The plinth puts the floor 0.47 C up, three 0.87 risers.
    - **Against the kit:** W10 `TimberHut` 13.0 × 10.7 × 12.5 with a 4.4 × 7.1 door; M064 tent 13.7 × 11.7 × 11.0;
      M066 shelter 17.3 × 12.3 × 12.0. This hut is the kit's largest camp structure, as a walled building should be.
    - **Smaller** (door 6.0) brushes a 5.5 avatar's hat and the eave lantern drops to head height. **Larger** (door
      8.0) makes the kit's barrels and crate (kept at kit size, §3.12) read as toys beside a 22-tall chimney.
- **Build frame (decision §8.3):** front −Y (the door gable), +X right, ground z 0, the walls' rectangle centred on x 0,
  y 0, ridge along Y. Stage 2 puts the origin at the bbox bottom centre (about build (0, +0.35, 0): the stairs at the
  front, the banner crossarm at the back) and stores the offset (§2.13).

### 1.2 Measured views (`bbox.py`, `shares.py`)

| View (box) | Object bbox (px) | W : H | fill | W / C / S / K / B / Y / G / R % | wood lit / mid / shade % |
| --- | --- | --- | --- | --- | --- |
| **f34** (16,104,508,466) | 31–492 × 104–450 (462 × 347) | **1.331** (≈ 1.245 without the far-left grass) | 0.710 | 58.9 / 18.3 / 11.2 / 3.5 / 3.4 / 1.5 / 2.9 / 0.3 | **16 / 37 / 48** |
| r34 (516,104,1010,466) | 535–986 × 116–448 | 1.357 | 0.686 | 56.2 / 19.7 / 13.5 / 3.1 / 2.7 / 1.0 / 3.7 / 0.3 | 11 / 52 / 37 |
| "Front" (16,532,272,738) | 24–264 × 540–722 | 1.317 | 0.694 | 61.8 / 14.0 / 9.6 / 3.6 / 5.9 / 1.9 / 2.7 / 0.4 | 12 / 39 / 49 |
| **Side** (276,532,510,738) | 286–499 × 544–720 | **1.209** | 0.703 | 52.6 / 20.2 / 14.7 / 6.4 / 0.1 / 0.9 / 4.8 / 0.3 | 12 / 54 / 34 |
| "Rear" (516,532,762,738) | 526–754 × 545–719 | 1.309 | 0.722 | 52.0 / 18.8 / 13.4 / 5.0 / 4.7 / 0.7 / 5.3 / 0.2 | 11 / 55 / 34 |
| Top (765,532,1010,738) | 773–998 × 544–730 | 1.209 | 0.792 | 31.9 / 52.3 / 8.3 / 3.0 / 1.7 / 0.6 / 1.9 / 0.2 | 17 / 43 / 40 |

- **Side cell levels** (fractions of the chimney-top height, ground 0): stone course 0–0.17; wall planks 0.17–0.51
  (four rows); wall plate 0.51–0.58; roof band 0.58–0.83; chimney 0.83–1.00 above the ridge, its centre at **0.87 of
  the wall length from the front** (§3.6); window centred (0.50 ± 0.02 of the wall), opening 0.28–0.43; four golden eave
  ties; bargeboards at both ends leaning out; the right-of-door lantern edge-on beyond the wall's left (front) end at
  0.32–0.60; a barrel at the right (back) end; grass tufts.
- **Verifier tolerance:**
  - side_sheet: plate / chimney top 0.58 ± 0.03, ridge / chimney top 0.83 ± 0.03, wall length / chimney top 0.85 ±
    0.05, roof length / chimney top 1.03 ± 0.05, window centred ± 0.04 of the wall, window opening bottom 5.4–5.7 and top
    8.3–8.9; shares W 53 ± 8, C 20 ± 6, S 15 ± 5, K 4–9, Y 0.5–1.5.
  - f34_sheet: W : H **1.25 ± 0.08** without grass (`proj.py` block model 1.21–1.27 over the probes); W 59 ± 8, S 11 ± 4,
    K 2–6, B 2–5, Y 0.8–2.4; wood lit / mid / shade 16 / 37 / 48 ± 10; C judged on the side view (§5.4, the M064
    canvas ruling).
  - **Recorded, not scored:** the stone band (ours 0.23 of the plate height, sheet 0.29; §3.9); the dressing positions
    in the side, rear, r34 and top cells (§3.6); the top cell's door side (§3.5); the "front" and "rear" cells' W : H.

### 1.3 Silhouette and composition per view

**f34 (`z_f34.png`, `z_f34_gable.png`, `z_f34_left.png`, `z_door.png`, `z_lwall.png`) — governs the read, the front
gable, the lanterns and the dressing.** From the front-left (≈ 40°), a little above (≈ 15°):
- the **−X long wall** at the left: about five rows of thick planks with dark seams and staggered butt joints, a
  corner post at each end, a **window** near its front end mostly hidden by the **eave lantern**, which hangs from a
  dark **iron L-bracket** under the eave beam beside the front-left corner post;
- the **front gable** at the right: plank walls either side of the **door**, which is set between **two tall door
  posts**; a heavy **lintel** across them, a **collar** above it at eave level, **vertical boards** in the gable triangle,
  two thick **bargeboards** meeting at the apex and crossing into an X of square tips with a golden block between, and
  the **ridge beam's square end** projecting below the crossing; a **lantern** on a wall bracket left of the door and
  one right of it, both with amber glass at about head height;
- the **door**: a dark-orange leaf of vertical planks with an iron strap hinge on the left and a ring handle on the right;
  in front of it a pale grey threshold, then **two-step wooden stairs** (two-plank treads on blocks); the left door post
  runs down to the ground beside the stairs;
- the **roof**: the cream −X slope in a grid of panels (seams up the slope and one along it at mid-slope), the
  **eave beam** under its edge with **golden U ties** at the seams, **projecting eave-beam ends** at the corners with
  iron plates (close-up A), the back gable's bargeboard tips at the upper left, small cleats on the bargeboards;
- the **chimney** just behind the ridge in the front third: a grey stone stack in two blocks with notched joints, a
  wider cap with a dark flue;
- the **stone plinth**: grey blocks of uneven length in two courses, a big **white block** at each corner;
- the dressing: the **banner pole** just beyond the back-left corner, its **crossarm** along Y with an X lashing and the
  **red swallowtail banner** hanging at its back end; a **barrel** at the back of the −X wall, the **crate** in front of
  it, a **white stone** in front of the crate; a second **barrel** beyond the front-right corner on the +X side; grass
  tufts at the corners and the stairs.

**r34 (`z_r34.png`, `z_r34_gable.png`).** A **true rear view from the back-left** (§3.3): the back gable at the left
(planks, a vertical frame post, the collar, crossed bargeboards with the ridge-beam end, a **lantern** on its left part,
no door, no stairs), the −X wall at the right with a **centred barred window**, four eave ties, the chimney above the
ridge near the back gable, and the banner pole, barrel and crate at the −X wall's **front** end. The dressing and
chimney are the f34's mirrored front-to-back (§3.6).

**"Front view" (`z_front.png`) — not an elevation.** A front-left three-quarter at a low camera (≈ 45°, ≈ 5° up):
the same content as the f34 (−X wall with the eave lantern on its bracket and a window shutter edge, the front gable
with the door right of centre, three lanterns, the stairs; banner pole at the far left with the knob above an X-lashed
crossarm; barrel and crate at the −X wall's back end; chimney near the front gable). Door clear height 0.91 of the wall
height; the gable's peak over the door.

**"Side view (right)" (`z_side.png`) — governs heights and length.** The +X long wall square on: four plank rows
between two corner posts on the two-course plinth with white corner blocks, a **centred window** (a frame of light
boards, a dark opening, two vertical bars), the eave beam with four golden ties, the cream roof band with seam lines and
stitch dots, the bargeboards at both ends, the chimney above the ridge at the back end, the right-of-door lantern
edge-on at the front end, a barrel at the back end.

**"Rear view" (`z_rear.png`) — actually the −X long wall.** The same elevation as the side cell, turned the other way
(chimney at the left = back, banner pole and banner at the right = front, a lantern sliver at the back gable).

**Top view (`z_top.png`).** The roof as a cream rectangle with a seam grid, both gables' bargeboard frames with cleats,
golden ties along one eave, the chimney (with its flue) near one end, barrels at two corners, the banner at the lower
left and the **stairs on a long (eave) side** (§3.5). Content only.

**Exploded (`z_ex_*.png`).** Loose perspective near hero scale; it governs part shapes, not sizes:
- **Roof Panel (Left / Right):** each drawn as a small tent of cream canvas with orange toggle pegs at its corners (each
  label points at one slope);
- **Ridge Beam:** a long square beam with a chamfered (octagonal) end and a golden band near it;
- **Chimney:** a square stone stack with notched joints and a hollow top;
- **Wall Panel (Left):** two plank panels each with an end post (plank ends lapped past the post);
- **Wall Panel with window** (leader "Wall Panel (Right)"): a long plank panel with a centred window frame and two
  vertical bars, end posts with square tops;
- **Doorframe** (unlabelled, leader "Wall Panel (Right)"): a plank panel with two big posts, a lintel projecting past
  them, a plank door with a strap hinge and a ring handle, golden caps at the post feet;
- **Front Gable Frame:** two rafters crossing at the apex with a golden lashing, a collar, two posts with golden foot
  caps;
- **Floor:** a deck of lengthwise planks on short dark feet;
- **Stone Foundation (x4):** runs of three pale grey bevelled blocks;
- **Stairs:** two treads of two planks each on blocks, the upper one set back;
- **Banner Pole + Banner:** a square pole with a block top, a round crossarm through it with an X lashing and iron
  bands, the red swallowtail banner with the white diamond, a golden band at the foot;
- **Lantern (x2):** dark frame, amber glass, a roof cap, hung by a ring from an orange peg;
- a hooped barrel, an X-braced crate with iron corners, a small stone block with a square hole, grass.

**Close-up A (`z_cu.png`, top).** The eave beam's end projects past the wall with a chamfered octagonal cut face; a
rafter rests across it; on the beam's side a dark iron plate (two rivets) holds a golden square peg; the cream canvas
over the top.

**Close-up B.** A white corner block (bevelled, broken corner) under the corner post's foot; grey blocks of two courses
along both wall bases, set a little back from the corner block's faces; grass.

**Close-up C.** From inside: rafters down the slope and purlins across them in a square grid, the canvas underside in
the cells (warm beige `#C5A37F` in shade), the chimney passing through near the ridge.

**Palette and notes.** Six flat swatches (§5.1); the notes as above.

### 1.4 Parts (exploded, close-ups)

| Part (label) | Exploded box (px) | Tone (median, lit, shade) | Shape |
| --- | --- | --- | --- |
| Roof Panel (Left / Right) | (195,830,370,920) / (360,820,560,920) | `#FEEDC6`, lit `#FEF0C9`, shade `#ECCCA3` | one canvas slope with seams and corner toggles |
| Ridge Beam | (300,785,470,820) | as the timber; lit end `#F79744` | long square beam, chamfered end, golden band |
| Chimney | (140,840,180,895) | `#887F84`, lit `#B5AAAF`; flue dark | square stone stack in two blocks, cap, hollow top |
| Wall Panel (Left) | (190,920,310,1100) | timber `#8F481D` | plank panels with end posts |
| Wall Panel (window) | (320,880,480,1010) | `#8F481D`, lit `#C56B26`, shade `#6E3517` | long plank panel, centred barred window |
| Doorframe + door | (440,980,560,1130) | posts lit `#F79744`; door `#89441A` | two posts, projecting lintel, plank door, strap hinge, ring |
| Front Gable Frame | (620,955,740,1120) | as the timber; caps `#F9A528` | crossed rafters with a lashing, collar, two posts with caps |
| Floor | (250,1090,460,1170) | `#D17C3F`, lit `#EE944B` | plank deck on dark feet |
| Stone Foundation (x4) | (140,1100,420,1270) | `#AEA2A2`, lit `#DED9D4`, shade `#7C777D` | runs of three bevelled blocks |
| Stairs | (525,1180,640,1260) | `#BA632B`, lit `#FBA754` | two two-plank treads on blocks |
| Banner Pole + Banner | (60,920,150,1135) | red `#D71A1E`; pole timber | pole, crossarm, X lashing, swallowtail banner, emblem |
| Lantern (x2) | (35,995,90,1100) | glass `#FAC606`; frame `#584E4D` | dark frame, amber glass, roof cap, ring, peg |
| Barrel / crate / stone | (565,1095,620,1170) / (635,1140,705,1195) | hoops `#776E72` | 8 staves and two hoops / X-braced box with iron corners |

### 1.5 How 068 differs from the old kit and its siblings (binding: the verifier checks these)

| | W10 `TimberHut` (old kit, exported) | **068 Timber Hut** |
| --- | --- | --- |
| Size | 13.0 × 10.7 × 12.5; door 4.4 × 7.1; floor 1.2 | **walls 14.4 × 16.4, floor 2.60, plates 11.2, ridge 16.0, chimney 19.4; door 3.6 × 7.0** |
| Walls | "flat plank walls, no framing/window/door frame" | **five rows of 0.40 planks with seams between 1.1 corner posts on corner blocks; a barred window in each long wall** |
| Front | door in a frame, lanterns either side | **front gable frame: tall door posts with golden caps, lintel, collar, crossed lashed bargeboards, ridge-beam end; three lanterns** |
| Roof | "plain roof", battens | **two closed canvas slabs on five-bay rafters and a purlin per slope, eave beams with golden U ties, iron bracket plates at the beam ends** |
| Base | stone course 1.55 | **two-course plinth of bevelled blocks to 2.30, white corner blocks to 2.60, three-riser stairs** |
| Colour | `w10_wood #8A4A22` (one shared key) | **orange timber `#A95929` with golden end caps; cream canvas; warm grey stone with white corner blocks** |
| Budget | hero 4398 | **plan 6200–7200, ceiling 8000** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0). Kit camera azimuths: `front` az 0 (camera on −Y), `side` az 90
(camera on +X, screen right = +Y), `rear` az 180; the f34 is about az −40 e 15 (camera at front-left).

### 2.1 Stack (binding contact chain; every seat ≤ 0.03 unless stated)

| Piece | Rests on / against | Contact |
| --- | --- | --- |
| Foundation blocks, corner blocks | the ground; the lower course | bottoms on z 0.000 (±0.005); upper course on the lower |
| Floor deck planks | the front and back foundation runs (inner 0.20) and a threshold beam | bottoms z 2.30 |
| Wall planks (bottom row) | the foundation course top | bottom z 2.30 |
| Corner posts (4) | the corner blocks | feet z 2.60 |
| Wall planks | the row below; their ends on the posts' inner faces | 0.06 seams, ends touching posts (≤ 0.02) |
| Wall plates (2) | the corner posts' tops and the top plank rows | bottoms z 10.40 |
| Door posts (2) / golden caps | the ground (caps 0–0.40, posts above) | feet z 0 |
| Lintel; front collar | the door posts' tops; lintel top + plate ends' inner faces | z 9.60; z 10.40 |
| Back frame posts, back collar | the back wall's outer face; the plates | touching |
| Rafters, bargeboards | the plates (birdsmouth: horizontal seat cut) | seats ≤ 0.02 |
| Ridge beam | both gables' bargeboard crotches | ≤ 0.02 |
| Purlins | the rafters' tops | ≤ 0.02 |
| Canvas slabs | rafters, purlins, ridge beam | underside on them ≤ 0.03, nowhere buried > 0.05 |
| Eave ties | canvas edge and plate | wrap both, ≤ 0.02 off |
| Chimney | a timber trimmer frame between two rafters under the canvas | flush, ≤ 0.02 |
| Lanterns | rings on bracket hooks; brackets on the plate / wall | touching |
| Stairs | the ground; the upper tread's back edge on the door posts' front faces | feet z 0 |
| Banner pole / rod / banner | ground; through-lashing; rod | touching |
| Barrels, crate, stones | the ground | flat bottoms z 0 |

### 2.2 Foundation

- **Course:** a ring of blocks under the walls, outer faces x ±7.40, y ±8.40, 1.00 deep (inner faces ±6.40 / ±7.40),
  **two courses** z 0–1.10 and 1.10–2.30, blocks 1.6–3.0 long (no two adjacent equal; joints of the two courses
  offset), 0.06 gaps, the outer top edge chamfered 0.10, two or three blocks per side with one broken top corner. About
  7 + 7 blocks along each long side and 6 + 6 along each end, between the corner blocks.
- **Corner blocks (4):** a grey block z 0–1.30 under a **white block** z 1.30–2.60, each 2.20 × 2.20, centred on the
  corner posts (±6.65, ±7.65): outer faces ±7.75 / ±8.75, proud of the course by 0.35 (close-up B). Bevel 0.12 on the
  white block's top edges, one broken corner each.
- At the door the front course runs behind the door posts (the posts stand in front of it, §2.5).

### 2.3 Floor

- **Deck:** 10 planks along Y, 1.26 wide with 0.06 gaps, z 2.30–2.60, x −6.60 … +6.60, y −7.60 … +7.60, resting on the
  front and back runs' inner 0.20 and on two hidden sleepers (1.0 × 0.6 on the ground, y ±3.5: no long free span).
- **Threshold:** the three middle planks continue through the doorway to y −9.50 on a threshold beam (0.8 × 0.6,
  x ±1.80, between the door posts, on the front course's outer face). The f34's pale threshold is these planks in shade.
- Floor top level at **2.60 ± 0.01** everywhere (characters walk on it).

### 2.4 Walls and posts

| Member | Section | Position |
| --- | --- | --- |
| Corner posts (4) | 1.10 square, 0.06 chamfer on the long edges, pale golden top and bottom faces | x ±6.10 … ±7.20, y ±7.10 … ±8.20, z 2.60–10.40 |
| Long-wall planks (±X) | 0.40 thick, 1.56 tall (+0.06 seams), outer top and bottom edges chamfered 0.06 | outer face x ±7.00, between the posts y −7.10 … +7.10; rows z 2.30 / 3.92 / 5.54 / 7.16 / 8.78 → 10.40 |
| End-wall planks (front, back) | as above | outer face y ±8.00, between the posts x −6.10 … +6.10 |
| Wall plates (2) | 0.90 (X) × 0.80, octagonal chamfered end faces (close-up A) | x ±6.30 … ±7.20, z 10.40–11.20, y −9.60 … +9.60 (1.40 past the end walls) |
| Iron bracket plates (4) + golden pegs | plate 0.10 × 0.90 × 0.70 with two rivets; peg 0.40 cube | on each plate's outer face 0.7 inside its end; the peg through the plate into the beam face (touching, not buried > 0.05) |

- **Plank joints:** one butt joint per row on the long walls, staggered (rows 1, 3, 5 at y −2.6; rows 2, 4 at +3.4),
  0.04 gap; front-wall rows split by the door; ±0.02 jitter in the plank outer faces (hand-made), never a step that
  opens a seam to see through.
- **Windows (both long walls, centred y 0):** opening y −1.50 … +1.50, z 5.54–8.78 (rows 3–4 removed); a frame of
  0.50-wide, 0.20-proud light boards (sill projecting 0.25 past the jambs and 0.30 out), two vertical iron bars 0.22
  square at y ±0.50; the opening is real (it looks into the interior, §3.10).
- **Back wall:** five rows; two **frame posts** 1.10 × 0.50 on its outer face at x ±2.35 (z 2.60–10.40), the r34's
  vertical post.

### 2.5 Front: doorway, door posts, lintel, collar, door

| Member | Section | Position |
| --- | --- | --- |
| Door opening | — | x −1.80 … +1.80, z 2.60–9.60 (clear **3.60 × 7.00**) |
| Door posts (2) | 1.10 square, 0.06 chamfer; golden foot caps 1.16 square × 0.40 | x ±1.80 … ±2.90, y −9.50 … −8.40, z 0–9.60 (caps 0–0.40) |
| Header plank | 0.40 thick | in the wall plane over the opening, z 9.60–10.40 |
| Lintel | 0.80 tall × 1.10 deep | on the door posts, x −3.30 … +3.30 (0.40 past each post), z 9.60–10.40 |
| Front collar | 0.80 × 1.10 | z 10.40–11.20, x −6.30 … +6.30 (butting into the plates' inner faces), y −9.50 … −8.40 |
| Door leaf | 3.56 × 6.96 × 0.30: four vertical planks with 0.04 seams, two inner battens, two iron strap hinges (0.10 proud, 1.8 long) on the hinge side, an iron ring handle (square-section ring Ø 0.6 on a 0.25 plate) | **hinged at x −1.80, open inward 95°** against the front wall's inner face: x −1.80 … −5.36, y −7.60 … −7.30, z 2.62–9.58 (decision §8.4) |

- The front wall planks run x −6.10 … −1.80 and +1.80 … +6.10; the gap between the wall's outer face (y −8.00) and the
  door posts' back faces (−8.40) is closed by the threshold below and the lintel above (the posts stand in front of the
  foundation; nothing floats: lintel → posts → ground).

### 2.6 Roof frame

| Member | Section | Position |
| --- | --- | --- |
| Rafters (4 interior pairs) | 0.50 wide × 0.70 deep | at y −5.82, −1.94, +1.94, +5.82 (five bays of 3.88 over the 19.4 roof), from the ridge beam down over the plates to the eave (x ±8.20); horizontal seat cut on the plate |
| Bargeboards (2 pairs) | 0.90 wide × 1.10 deep, 0.06 chamfer | the gable rafters at y ±9.20 … ±10.10, from the plate ends' tops up to the apex, **crossing**: tips at (±1.00, ±9.65, 17.20), a golden saddle block 0.8 × 0.9 × 0.6 between the tips |
| Bargeboard cleats (2 per board) | 0.40 × 0.30 × 1.40 | across each bargeboard and the canvas edge at 1/3 and 2/3 of its length (top cell, f34) |
| Apex lashing (2) | twisted rope Ø 0.24 | 3 turns round the crossing of each gable (exploded "Front Gable Frame") |
| Purlins (2) | 0.50 × 0.50 | one per slope at mid-slope (x ±4.10), on the rafters, y −9.70 … +9.70 |
| Ridge beam | 1.00 × 1.00, 0.08 chamfer, octagonal end faces | x ±0.50, top at the canvas underside (≈ z 15.88), y −10.60 … +10.60 (0.50 past the bargeboards' outer faces), golden end band (Ø 0.20 rope, 2 turns) 0.6 in from each end |
| Gable infill | vertical boards 0.40 thick, 0.9–1.1 wide | in each end-wall plane above the collar / back wall top, up to the rafters' undersides |

- Roof pitch **34°**: the canvas runs from the eave (x ±8.20, z 10.45) to the apex (0, 16.00).
- No tie beam or low member crosses the interior (interior clear §2.10).

### 2.7 Canvas (two closed slabs)

- Each slope one **closed 0.12 slab**: x 0 … ±8.20 (the two slabs meet at the apex fold: a 0.10 overlap, touching, or
  one slab folded over the ridge), y −9.70 … +9.70.
- Grid: **5 bays along Y × 2 rows down the slope** (the seams), each cell sagging **0.08** at its centre between the
  rafters and purlin (one interior vertex per cell, triangulated at build time). The seam lines lie on the rafters and
  the purlin: they read as soft ridges with the sag between, the f34's panel grid. No seam paint.
- **Eave edge:** the slab ends 0.10 past the eave beam's outer face; **golden U ties** (flat rope straps 0.24 wide ×
  0.08, wrapping the canvas edge and the plate) at each interior rafter: **4 per eave**.
- **Corner toggles** (exploded): 4 small golden pegs 0.30 cube at each slab's eave corners (optional, cut first).
- **Gable edges:** the slab's ends lie on the bargeboards' inner halves (touching), its edge 0.10 inside their outer
  faces.
- **Chimney hole:** the slab is cut round the chimney (no canvas inside the stone; ≥ 0.02 clear).

### 2.8 Chimney (f34 position, decision §8.5)

- **Body:** 2.60 × 2.60, centred (+2.20, −3.40), from the trimmer frame under the canvas (bottom z ≈ 13.6) to z 18.60,
  in two stone blocks (joint at z 16.6) with notched joints (a 0.15 step at each joint on two faces, the f34's notches).
- **Cap:** 3.00 × 3.00 × 0.80, z 18.60–19.40, bevel 0.08; **flue** 1.40 × 1.40 recess 0.60 deep (open top, closed
  floor).
- **Trimmer frame:** two short timbers (0.50 × 0.70) between the rafters at y −5.82 and −1.94, under the chimney's
  ±Y faces, flush with the rafter tops: the chimney's bottom sits on them (no floating stone, close-up C).
- VFX socket at the flue's centre, z 19.30 (§7).

### 2.9 Stairs, lanterns, banner, dressing

| Piece | Where | Size / notes |
| --- | --- | --- |
| Stairs | x −2.40 … +2.40; upper tread y −11.10 … −9.50, top **1.73**; lower tread y −12.70 … −11.10, top **0.87** | each tread two planks 0.78 wide × 0.30 with a 0.04 gap, 0.06 chamfer; the upper on two blocks (0.6 × 1.4) on the ground, the lower on two feet; three equal **0.87 risers** to the threshold |
| Lantern L1 (eave) | hangs at (−8.30, −6.60) from an iron L-bracket under the −X plate (arm 0.25 square, z 9.40–9.65, from x −7.00 out to −8.40) | body 1.40 × 1.40 × 2.60 at z 6.40–9.00 (frame bars 0.14, roof pyramid cap, finial, base plate), glass 1.00 × 1.00 × 1.60 Neon, ring z 9.00–9.40 |
| Lanterns L2, L3 (door) | (−4.40, −9.10) and (+4.40, −9.10) on wall brackets (arm 0.25 square from the front wall's outer face y −8.00 out to −9.25 at z 8.90) | as L1, body z 6.00–8.60; glass centre z 7.30 |
| Banner pole | (−9.40, +10.40) | 8-sided Ø 0.80, z 0–15.20, square block top 1.00 × 1.00 × 0.60 (15.20–15.80), golden foot band z 0.4–0.7 |
| Crossarm | along Y through the pole at z 14.20–14.60, y +9.60 … +13.40 | 8-sided Ø 0.40, end knobs, two iron bands; golden X lashing at the pole |
| Banner | plane x −9.40, hanging from the crossarm at y +10.90 … +13.10 | 2.20 wide, top hem wrapping the arm at z 14.20, three swallowtail points at z 6.40 (centre) / 6.80 (sides); a closed 0.08 slab; the white emblem (outer diamond ring, inner diamond, two side points) on **both** faces |
| Barrel A | (−9.20, +7.60) | the kit barrel (M064 `barrel`: 8 staves Ø 2.0 → 2.2, 2.80 tall, two iron hoops, a pale grey lid) |
| Crate | (−9.10, +3.40), yaw 8° | the kit crate (M064 `crate`: 2.30, X braces, iron corner plates) |
| Stone S1 / S2 | (−9.00, +1.40) / (+3.60, −11.60) | 1.10 × 1.00 × 0.90 / 0.90 × 0.80 × 0.70, white stone key, broken corners |
| Barrel B | (+9.20, −5.60) | as A, yaw 20° |
| Grass | — | none in the hero (decision §8.9) |

- Clearances: every dressing piece ≥ 0.10 off the foundation, corner blocks, stairs and each other; the banner pole
  ≥ 0.40 from the back-left bargeboard foot and the canvas corner.

### 2.10 Walk-in clearances (binding)

- **Path:** a 5.5 proxy (2 × 1 body to 4.4, a 1.1-wide head to 5.5) walks from (0, −15) up the stairs (0.87 risers),
  across the threshold, through the doorway, to (0, 0), and turns round (a 3.0-diameter circle) — touching nothing.
- **Door:** clear width ≥ 3.50 at every height up to 6.9 above the threshold; clear height ≥ 6.90 (lintel underside z
  9.60, the threshold z 2.60). The open leaf ≥ 0.10 off the path.
- **Interior:** x −6.60 … +6.60 × y −7.60 … +7.60 (13.2 × 15.2, minus the open leaf); every overhead member ≥ 7.8
  above the floor (plates 10.40, collars 10.40, rafters higher); the chimney stays above the canvas line.
- **Outside:** the eave lantern's bottom ≥ 6.3 (a character walking along the −X wall passes under it); the door
  lanterns' bottoms ≥ 6.0 and they stand 1.1 clear of the door posts (≥ 1.5 off the walk path).
- Print every minimum clearance (target ≥ 0.10) and the riser heights (0.87 ± 0.02, equal).

### 2.11 Expected extents

- **Hut:** X −8.60 (bargeboard feet) … +8.60, Y −10.60 (ridge-beam end) … +10.60, Z 0 … 19.40 (chimney cap).
- **Hero:** X ≈ −10.30 (barrel A) … +10.30 (barrel B), Y ≈ −12.70 (stairs) … +13.40 (crossarm), Z 0 … 19.40 → **about
  20.6 × 26.1 × 19.4**; bbox bottom centre ≈ (0, +0.35, 0) in the build frame.

### 2.12 Screen checks (floor hidden; `shares.py` masks; probe and keep the best)

- **side_sheet (90, 3)** — governs heights and length: the §1.2 side tolerances; the plinth band, four (ours five)
  plank rows, centred window with bars, four eave ties, chimney above the ridge (ours at the front third: recorded,
  §3.6), the right door lantern edge-on beyond the front end.
- **f34_sheet (−40, 15)** (probe az −35 … −50 × e 10 / 15 / 20; mild perspective on the sheet) — governs the read and
  dressing: W : H 1.25 ± 0.08 (`proj.py`: 1.21–1.27); shares and value bands per §1.2; content: the eave lantern on its
  bracket by the front-left corner, the door between its posts with the two lanterns, the crossed bargeboards and
  ridge-beam end at the front apex, the chimney behind the ridge in the front third, the banner at the back-left,
  barrel A and the crate along the −X wall, barrel B beyond the front-right corner, the stairs.
- **front3q_low (−45, 5)** — the sheet's "front view" cell: content as the f34; W : H recorded.
- **rear_sheet (−90, 3)** (camera on −X) — the sheet's "rear view" cell: the −X elevation (centred window, plinth,
  ties); the banner and chimney positions recorded (§3.6).
- **r34_sheet (−135, 15)** (camera back-left) — content: the back gable with its frame posts and ridge-beam end, the
  centred −X window; recorded: no back lantern (§3.7), the dressing mirrored (§3.6).
- **top (0, 89.9)** — content only: seam grid of 5 × 2 per slope, bargeboard cleats, the chimney with its flue, eave
  ties; the sheet's door side is not scored (§3.5).

### 2.13 Origin, pivot and stored points

- Origin at the **bbox bottom centre** (`K.check`); transforms applied. Store on the hero `o["m068_offset"]` (build
  frame = object + offset, M052's convention), `o["m068_centre"]` (the floor centre, build (0, 0, 2.60)),
  `o["m068_door"]` (threshold centre (0, −8.00, 2.60) and the outward facing −Y), `o["m068_hinge"]` (the leaf's hinge
  axis bottom (−1.80, −7.60, 2.60), closed yaw and open yaw), `o["m068_chimney"]` (flue centre); re-check all after the
  origin move.
- Parts: origin at their own bbox bottom centre; the DoorFrame part also stores its hinge; the Lantern part `m068_hang`
  (its ring top).

## 3. View conflicts and resolutions

### 3.1 Sheet number
- **Evidence.** The header says "PAGE 67/132"; INDEX.md row 68 lists `068.png` as "Flintborn timber hut model study".
- **Resolution.** Our number is 068 (file name, keys `m068_*`). Note the header in the export notes only.

### 3.2 The "front view" is a three-quarter view
- **Evidence.** The cell shows the −X long wall and the front gable together at a low camera (≈ 45°, ≈ 5° up), with
  the same content as the f34.
- **Resolution.** Score it as a low f34 (`front3q_low`), content only; its door height (0.91 H) is folded into §1.1.

### 3.3 The rear three-quarter is a true rear view
- **Evidence.** Its gable (left) has no door and no stairs, but a collar, a vertical frame post and a lantern; with the
  camera at the back-left that gable is the back one and the long wall is the −X wall.
- **Resolution.** The back gable gets the frame posts and the collar as drawn. Its lantern is §3.7; its dressing is
  §3.6.

### 3.4 The "rear view" is the −X side elevation
- **Evidence.** It draws a long wall with eave ties, not a gable; the chimney at its left and the banner at its right
  match a camera on −X.
- **Resolution.** Score it as the −X elevation (`rear_sheet` at −90); its heights agree with the side cell's to ±1 px.

### 3.5 The top view puts the door on a long side
- **Evidence.** Top cell: the ridge runs left–right, the bargeboard frames lie along the left and right edges, the
  eave ties along the bottom edge, and the stairs below the bottom edge (an eave side). Every other view puts the door in
  the gable.
- **Resolution.** Door in the front gable. The top cell is content only (seam grid, cleats, chimney, ties); its roof
  proportion (1.19) is used, its door side is not.

### 3.6 Dressing and chimney: the f34 and front cells against the side, rear, r34 and top cells
- **Evidence.**
  - f34 and the front cell: chimney behind the ridge at **0.78 of the way from the back to the front gable** (an ortho
    fit puts it at y ≈ −3.4 on the +X slope); banner pole at the **back-left** corner; barrel A and the crate along the
    −X wall's back half; barrel B beyond the front-right corner.
  - Side cell: chimney at **0.87 of the wall from the front** (back), barrel at the back-right. Rear cell (−X): chimney
    at the back, banner at the front-left. r34: chimney near the back gable, banner, barrel and crate at the −X wall's
    front end. Top: chimney near one gable, banner at the lower left.
  - The two groups are mirror images front-to-back; the walls, roof and windows agree.
- **Resolution (decision §8.5).** **The f34 governs the chimney and the dressing** (the hero view sets silhouette and
  character, WorldModeling §1.1; 067 followed the hero views the same way): chimney at (+2.20, −3.40), banner at the
  back-left, barrel A and crate on −X, barrel B front-right. The side, rear, r34 and top cells are scored on their
  walls, heights and windows; their chimney and dressing positions are recorded misses. Alternative: chimney at
  (+2.20, +6.00) and the banner at the front-left (four cells agree; the f34 and the front cell then miss, and the
  chimney leaves the hero view's gable silhouette).

### 3.7 How many lanterns
- **Evidence.** f34 and front cell: **three** (the eave lantern on its bracket near the front-left corner, two flanking
  the door). Side cell: the right door lantern edge-on. r34 and rear cell: one more on the **back gable**. Exploded:
  "Lantern (x2)".
- **Resolution (decision §8.6).** **Three**, as the hero view: L1 eave, L2 / L3 at the door. Alternatives: a fourth on
  the back gable (r34; +≈ 170 tris, +1 socket) or two (the exploded's label: drop the eave lantern).

### 3.8 The −X window: near the front (f34) or centred (rear cell, r34)
- **Evidence.** f34: a window frame near the −X wall's front end, mostly behind the eave lantern. Rear cell and r34
  (both the −X wall): a centred barred window. Side cell (+X): centred.
- **Resolution.** **Both windows centred** (three views agree; the exploded's window panel is centred too). The eave
  lantern stays by the front-left corner, as the f34; the f34's window-behind-the-lantern is a recorded miss.

### 3.9 Plinth height: the sheet's tall stone band against walkable risers
- **Evidence.** Side and rear cells: stone 29 px of a 100 px plate height (0.29); f34: 0.46 of the wall height; close-up
  B. The stairs have two treads, the upper about at threshold level.
- **Resolution (decision §8.7).** **Floor 2.60** (course 2.30, corner blocks 2.60): three equal 0.87 risers (two treads
  and the threshold), under 052's 1.12. The band reads 0.23 of the plate height (recorded). Alternative: floor 3.40
  (0.30, the sheet's band) with three 1.13 risers, or four 0.85 risers (three treads; the sheet draws two).

### 3.10 The window: real opening or dark inset
- **Evidence.** Every window is a dark opening (`#201717`) with two bars. The hut is walk-in; WorldModeling §13.3
  forbids painted openings.
- **Resolution.** A **real opening** through the wall with two iron bars; the dark comes from the interior's shade, not
  paint. No glow in the window (the sheet draws none).

### 3.11 The door: closed (every view) against walk-in
- **Evidence.** f34, front cell and the exploded draw the leaf closed, with a strap hinge and ring handle. The hut must be
  enterable.
- **Resolution (decision §8.4).** The hero's leaf **open inward 95°** against the inside of the front wall (hinge on the
  left jamb, the f34's strap side), so the doorway is clear with the hero's `precise` collision. The `DoorFrame` part
  carries the leaf closed with its hinge stored, for a scripted door in Studio. Alternative: the leaf closed as drawn
  in the hero (a sealed hut unless Studio removes it).

### 3.12 Props drawn at a doll's-house scale
- **Evidence.** On the sheet a barrel is 0.5 of the plate height (side cell), the lanterns 0.3 H, the banner 8.9 long.
  At the door-set scale a barrel would be 5.7 tall.
- **Resolution.** **Kit sizes for the props** (barrel 2.80, crate 2.30 as M064 / M066) so they match the rest of the
  kit; the **lanterns and banner stay at building scale** (lantern body 2.6, banner 2.2 × 7.8) because they belong to
  the hut and must read at its size. The props reading about half the sheet's relative size is recorded.

### 3.13 Wall plank rows: four (side, rear) or five to six (f34)
- **Evidence.** Side and rear cells: four rows. f34 −X wall and the exploded panels: five or six, with staggered butt
  joints.
- **Resolution.** **Five rows of 1.56** (one plank height for every wall; the window spans rows 3–4). Recorded against
  the side cell's four.

### 3.14 Roof bays: four (top, f34) or five (side)
- **Evidence.** Top: four columns (one short); side: five; f34: four or five; four eave ties in the side cell and the
  f34.
- **Resolution.** **Five bays, four interior rafters, four ties per eave** (ties at the interior rafters).

### 3.15 Grass and foliage
- **Evidence.** Tufts at every corner and by the stairs in every view; a Foliage swatch "(Accent)"; close-up B.
- **Resolution (decision §8.9).** **No grass in the hero** (WorldModeling §1.1: optional dressing; 064 and 066 left it
  out); place the kit's ground-scatter models round it in Studio. Alternative: six 3-blade tufts (≈ 40 tris each, `m068_leaf`).

### 3.16 The small stone block with a square hole (exploded)
- **Evidence.** Beside the crate in the exploded only; no assembled view shows it.
- **Resolution.** Left out (it reads as a miniature of the chimney cap). Recorded.

### 3.17 "Clean flat-shaded faces" against the drawn grain, cracks and canvas stitching
- **Resolution.** No modelled grain, cracks or stitches; plank seams and chamfers catch the light; the canvas seams come
  from the sag geometry; colour per §5.3.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

1. `block(lo, hi, bevel, broken, seed)` → one bevelled foundation block (chamfered outer top edge, optional broken
   corner). Check against close-up B and the exploded foundation run.
2. `foundation()` → the two courses, the four two-tier corner blocks.
3. `plank(...)` → one wall plank (6-sided section: outer top and bottom chamfered 0.06). `wall_long(sx)`,
   `wall_end(sy, door)` → the plank rows with joints, window opening, door opening, header; check against the exploded
   panels.
4. `post(lo, hi, caps)` → a chamfered square post with pale end faces (corner posts, door posts with golden caps, back
   frame posts).
5. `window(sx)` → frame boards, sill, two bars.
6. `door_leaf()` → planks, battens, hinge straps, ring handle; `doorframe()` → posts, caps, lintel, header, leaf.
7. `gable_frame(sy)` → collar, bargeboards crossing with the saddle block, apex lashing, cleats, gable infill boards.
8. `roof_frame()` → plates with chamfered ends, bracket plates and pegs, rafters, purlins, ridge beam with end bands,
   chimney trimmers.
9. `canvas(side)` → one closed slab with the sag grid and the chimney cut; `ties(side)` → the four U straps.
10. `chimney()` → body blocks with notches, cap, flue.
11. `floor()` → deck planks, threshold, sleepers. `stairs()` → treads, blocks, feet.
12. `lantern(base, bracket)` → frame, glass, cap, finial, ring, bracket (start from m064's `lantern`, scaled to §2.9).
13. `banner()` → pole, block top, foot band, crossarm with knobs and bands, X lashing, banner slab with emblem shells.
14. Props: `barrel`, `crate`, `stone` copied from m064 (§4.1 helpers).
15. **Hero `TimberCabin`** = foundation + floor + walls + posts + windows + doorframe (leaf open) + gable frames + roof
    frame + canvas + ties + chimney + stairs + lanterns + banner + props, placed by §2, one object of closed shells.
    Then the contact, bury, pierce, walk and winding reports (§6, §2.10).
16. **Parts shot** (−30, 15) laid out like the exploded; **exploded shot**: roof slabs and ridge lifted 4, walls apart,
    the gable frame forward, the floor and foundation below.

**Helpers to reuse (import the functions from committed builders, never their module constants):**
- `m048`: `_solid` (closed shell from points and faces, flipped by volume), `_prism` (vertical prism with a chamfered
  top), `_box`, `_rect`, `_inset`, `_plank2d` (a board from a 2D outline extruded along X or Y), `_brace_quad`, `_tube`,
  `_knob`, `coil_path`, `coil`, `knot`, `_tri_ngons`, `shells_report`, `contact_report`, `winding_report`,
  `levels_report`, `_recentre`, `_make_plain`. Its `_bolt` is round and sized by `BOLT_R`: don't use it.
- `m050`: `_peg`, `_rope`, `wrap_path`, `wrap`, `buried_report`, `_inside`, `_groups`, `levels_report`.
- `m051`: `_solid_rc` (the shell maker m064 uses), `_rope` (twisted rope tube with groove and phase).
- `m052`: `_ext` (straight prism of a 2D region with consistent winding), `_cells` (grid-cell prism, no slivers),
  `_earclip`, `_slab` (ear-clipped prism of any simple polygon: chamfered plank sections, gable boards, bargeboard
  ends), `_plank2d`, `_plank2d_yz`, `_post_solid` (square post with chamfered cap), `_brace`, `stringer_profile`,
  `treads`, `wrap_path`, `_resample`, `_rope_groove`, `rope_tie`, `walk_report` (adapt the path), `buried_report`.
- `m047`: `_Solids` (ray-parity inside test). `m038`: `contacts()`. `m009`: `_glow_mats` (Neon preview).
- `m064` (its working copy has uncommitted changes: **copy, don't import**): `_shell`, `_box`, `_slab2d` (closed canvas
  slab in a plane), `rope` and `_trim` (twisted rope, trimmed where it meets canvas), `hull_loop` (a rope loop hugging a
  hull at a fixed offset: the apex lashings, the banner X), `lashing`, `_band`, `lantern`, `crate`, `barrel`, `stone`,
  `pierce_report` (thin-slab pass-throughs), `bury_report`, `rope_ends_report`, `walk_report`, `placement_report`,
  `_glow_mats`, `_fx_spec`, `render_close_ups`, `render_spin`.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a plank cabin on a stone plinth under a cream gable roof, the front gable frame with crossed
   bargeboards over the door, three glowing lanterns, the chimney, the banner, barrels and crate.
2. **side_sheet / f34_sheet / front3q_low / rear_sheet / r34_sheet / top** per §2.12.
3. **Close-up renders:**
   - `junction_cu` on the front-left plate end, against close-up A: the chamfered beam end, the rafter on it, the iron
     plate with rivets and the golden peg, the canvas edge and a U tie.
   - `base_cu` on the front-left corner, against close-up B: the two-tier corner block proud of the course, the post on
     it, the courses' offset joints.
   - `underside_cu` from inside (0, 0, 4.5) looking up at the +X slope, against close-up C: rafters, purlin, ridge
     beam, the canvas underside in the cells, the chimney trimmers. **No see-through canvas.**
   - `apex_cu` on the front apex: crossed bargeboard tips, saddle block, lashing, ridge-beam end with its band.
   - `door_cu` from the stairs: posts, lintel, collar, the open leaf inside with hinge straps and ring, the two lanterns.
   - `door_walk`: the 5.5 proxy on the stairs, in the doorway and inside (front, side, three-quarter).
   - `inside_cu` from the doorway looking in: floor, windows from inside, the walls' inner faces, the roof underside.
   - `thumb`: the f34 at about 140 px tall: plinth band, plank rows, door, lantern glow, banner still read.
   - `spin` contact sheet az 0 / 45 / … / 315 at e 10: nothing floats, no see-through faces.
4. **Contact counts** (§6): floating 0; buried 0 (stated seats excepted); pierce 0; winding errors 0.
5. **Scale shot:** the 5.5 marker in the doorway and one beside a 067 table (2.60) inside.

### 4.3 Budget (ceiling 8000, plan 6200–7200; decision §8.2)

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Foundation blocks (bevelled; hidden end faces kept: each block a closed shell) | ≈ 52 | 16 | 830 |
| Corner blocks (two tiers, top bevelled, a broken corner) | 4 | 44 | 176 |
| Floor deck planks, threshold beam, sleepers | 10 + 3 | 12 | 156 |
| Wall planks (6-sided section) | ≈ 48 | 20 | 960 |
| Gable infill boards | ≈ 12 | 12 | 144 |
| Corner posts, door posts (chamfered), back frame posts, foot caps | 4 + 2 / 2 / 2 | 28 / 12 / 12 | 216 |
| Plates (octagonal ends), collars ×2, lintel, header | 2 / 3 / 1 | 44 / 28 / 12 | 184 |
| Bracket plates + rivets + pegs | 4 | 40 | 160 |
| Windows (frame boards, sill, bars) | 2 | 84 | 168 |
| Door leaf (planks, battens, straps, ring) | 1 | 130 | 130 |
| Rafters / bargeboards / purlins / ridge beam / cleats / saddles / trimmers | 8 / 4 / 2 / 1 / 8 / 2 / 2 | 12 / 28 / 12 / 36 / 12 / 12 / 12 | 452 |
| Rope: apex lashings, ridge end bands, eave ties, banner X | 2 / 2 / 8 / 1 | 96 / 48 / 36 / 96 | 672 |
| Canvas slabs (5 × 2 cells with sag vertices, closed, chimney cut) | 2 | 200 | 400 |
| Chimney (blocks, notches, cap, flue) | 1 | 130 | 130 |
| Stairs (4 tread planks, blocks, feet) | 1 | 150 | 150 |
| Lanterns with brackets | 3 | 170 | 510 |
| Banner (pole, top, foot band, crossarm, knobs, bands, slab, emblem both faces) | 1 | 280 | 280 |
| Barrels / crate / stones | 2 / 1 / 2 | 224 / 388 / 20 | 876 |
| **Hero** | | | **≈ 6600; plan 6200–7200; ceiling 8000** |
| Parts (§8) | | | RoofPanel ≈ 300, RidgeBeam ≈ 140, Chimney ≈ 130, Banner ≈ 280, Lantern ≈ 170, WallPanel ≈ 300, WindowWall ≈ 420, DoorFrame ≈ 520, GableFrame ≈ 330, Floor ≈ 160, Stairs ≈ 150, Foundation ≈ 260 |

- **Cut order if over:** corner toggles, bargeboard cleats, the crate's inner braces (use a 250-tri crate), foundation
  block count (longer blocks), rope sides (4 instead of 6). **Never cut:** the plinth's two courses and corner blocks, a
  window, the door or its frame, a lantern, the crossed bargeboards, the ridge-beam ends, the eave ties, the chimney cap
  and flue.
- **Headroom use** (only after every check passes): a back-gable lantern (§3.7), chamfers on the plank ends.

### 4.4 Shape targets (binding; check with `M.audit` and own bmesh code)

- Floor top 2.60 ± 0.01 (every deck plank); risers 0.87 ± 0.02, three, equal.
- Door clear ≥ 3.50 × ≥ 6.90; lintel underside 9.60 ± 0.05; the open leaf ≥ 0.10 off the walk path.
- Walls 14.40 ± 0.3 × 16.40 ± 0.3 (posts' outer faces); plate tops 11.20 ± 0.1; ridge (canvas top) 16.0 ± 0.3;
  chimney top 19.4 ± 0.4; pitch 34 ± 3°.
- Planks 0.40 ± 0.04 thick, 1.56 ± 0.1 tall, seams 0.06 ± 0.02; posts 1.10 ± 0.1; bargeboards 0.90 × 1.10.
- Canvas 0.10–0.14 thick everywhere, sag 0.06–0.12 per cell, never below a rafter or purlin top.
- Lantern glass 1.00 × 1.60 ± 0.1; glass centres z 7.6 (L1) and 7.3 (L2, L3) ± 0.3.
- Bargeboard tips cross ≥ 0.8 above the apex; ridge-beam ends ≥ 0.4 past the bargeboards.

### 4.5 Stages 2 and 3

- **Stage 2:**
  - Every shell closed and manifold, **0 bowties**, 0 boundary, wire or loose elements; no zero-area faces; n-gons
    triangulated.
  - **0 winding errors per shell** (`bmesh.ops.recalc_face_normals` per shell, then a parity ray test): the chamfered
    plates' octagonal ends, the cut rafters, the gable boards, the canvas sag grid and the emblem shells are where a
    reversed face slips in (044's wedge).
  - **Thin corners:** long boards and canvas rims triangulate to small angles. Report the count under 3° and fail only
    under 0.3° (the M064 ruling 2).
  - Origin at the bbox bottom centre, transforms applied, every stored point re-checked.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box, `sw3.py`)

| Swatch | Hex (HSV) | Use |
| --- | --- | --- |
| Timber | `#A95929` (22°, .76, .66) | every wooden piece's mid faces (`m068_timber`) |
| Canvas | `#F6E2BF` (38°, .22, .96) | the roof (`m068_canvas`); renders lighter, `#FEF0C9` |
| Stone | `#C2B6B7` (355°, .06, .76) | the foundation (warm grey, R > B) |
| Metal | `#6C6B70` (251°, .04, .44) | lantern frames, brackets, hoops, bars, hinges |
| Banner | `#CC2422` (0°, .83, .80) | the banner cloth |
| Foliage | `#709748` (89°, .52, .59) | grass (not in the hero, §3.15) |

### 5.2 Rendered regions (`samp.py`; median / lit quartile / shade quartile)

| Region | Median | Lit Q | Shade Q |
| --- | --- | --- | --- |
| Wood, whole cell: f34 / r34 / front / side / rear / top | `#90491F` (22°, .78, .56) / `#A25321` / `#8E471A` / `#A65927` / `#A95A25` / `#A95E26` | `#E48235` / `#D47733` / `#D8782C` / `#D77B32` / `#D27833` / `#DF8237` | `#552B14` / `#582C14` / `#512812` / `#512A18` / `#502715` / `#582C14` |
| Wall planks: side / rear / f34 −X wall / f34 front wall | **`#AB5C2A` (23°, .75, .67)** / `#AE5E2A` / `#88441C` / `#994E1D` | `#D88137` / `#DA8136` / `#AF5C23` / `#E67C21` | `#502B1A` / `#4F2918` / `#512812` / `#552F1C` |
| f34: door leaf / door posts and lintel / FL corner post / stairs / gable boards / roof timbers | `#733A19` / `#A15522` / `#784125` / `#BF682D` / `#924C23` / `#954C22` | `#804019` / `#F79744` / `#9F4C1C` / `#FCB15B` / `#E78531` / `#E2853C` | `#5B2F17` / `#522812` / `#5D3322` / `#552B13` / `#4D2818` / `#562B16` |
| f34: barrel A / crate / banner pole | `#8D4716` / `#824222` / `#6F3613` | `#C06622` / `#D07941` / `#9E501C` | `#4C2510` / `#502716` / `#411E0B` |
| Exploded: window wall / door / floor / stairs / post caps | `#8F481D` / `#89441A` / `#D17C3F` / `#BA632B` / `#F9A528` (35°, .84, .98) | `#C56B26` / `#A2561E` / `#EE944B` / `#FBA754` / `#FEB827` | `#6E3517` / `#603116` / `#89471D` / `#622F15` / `#D68219` |
| Close-up A: timber / cut end | `#994E23` / `#BB6625` | `#DE823D` / `#FBAA51` | `#502B1C` / `#824214` |
| Canvas: f34 slope / side / rear / top / exploded panel | `#FEF0CB` (43°, .20, 1.0) / `#FEF0C9` / `#FEF0C8` / `#FEEDC5` / `#FEEDC6` | `#FEF1CB` / `#FEF1C9` / … | `#FCECC6` / `#FBE9C2` / `#FBE7BE` / `#FAE2B9` / `#ECCCA3` |
| Canvas underside (close-up C, shade) | `#C5A37F` (30°, .36, .77) | `#C9A681` | `#C09D7A` |
| Stone course: f34 / side / exploded / close-up B grey | `#938A8E` (333°, .06, .58) / `#A6A1A5` / `#AEA2A2` / `#888286` | `#C9B9B6` / `#C7B7B9` / `#DED9D4` / `#BAB2B0` | `#625F65` / `#858083` / `#7C777D` / `#6C6A70` |
| White corner block: f34 / close-up B | `#AD9E9B` (10°, .10, .68) / `#A89EA3` | `#D0BEB9` / `#D9C4BF` | `#9D908E` / `#7F7C83` |
| Chimney: f34 stone / f34 dark parts / top | `#887F84` / `#584F50` / `#5B555A` | `#B5AAAF` / `#726B72` / `#747078` | `#574E50` / `#343035` / `#4E494F` |
| Metal: f34 lanterns / close-up A plate / exploded lantern / barrel hoops | `#53484A` (349°, .13, .33) / `#5A575C` / `#584E4D` / `#716C71` | `#786E71` / `#635E65` / `#706A68` / `#BCB4B8` | `#3F3637` / `#544F54` / `#403738` / `#413F42` |
| Glow: f34 / exploded | `#FBBD0A` (44°, .96, .98) / `#FAC606` | `#FED410` / `#FEDF09` | `#F09F03` / `#F1A403` |
| Rope ties: f34 / side / front | `#FBCA58` (41°, .65, .98) / `#F4BD51` / `#E1B14A` | `#FEDA56` / `#FFC45B` / `#FDE266` | `#F2BA5A` / `#C88C18` / `#AA8720` |
| Banner: f34 / rear / emblem | `#D71A1E` (358°, .88, .84) / `#CE1214` / `#FCF9F7` | `#E41E21` / `#E51D1E` / `#FEFCFC` | `#BE1215` / `#9E080A` / `#FAF6F5` |
| Window opening (side) | `#201717` | | |
| Foliage (f34) | `#5C7B13` | `#8FAC1B` | `#39500F` |

### 5.3 How the colour works

- **One timber** for every wooden piece (planks, posts, plates, collars, lintel, rafters, bargeboards, ridge beam,
  floor, stairs, door, window frames, banner pole, barrels, crate). The f34's value spread (lit 16 % / mid 37 % / shade
  48 %) is lighting: the −X wall, door recess and pole are darker in the f34 because they face away from the sheet's
  light; the side and rear elevations render the same planks `#AB5C2A`. Never paint a face darker because of where it
  points.
- **Per-piece Tint 0.05** (every plank, post and board its own seed): the plank-to-plank steps of the sheet.
- **Pale ends (`m068_timber_end`, hard edge):** the golden foot caps of the door posts and banner pole; the octagonal
  end faces of the plates and ridge beam, the bargeboard tips and the saddle blocks (the sheet's lit golden ends,
  close-up A `#BB6625` / lit `#FBAA51`; the README's "pale carved tips and cut ends"). End faces by **role**, not by
  normal: list them in the builder by member and end.
- **Positional bands (blend partners, 3 steps):** on each wall plank, 0.35 at one end (seeded coin) one step toward
  `m068_timber_deep`; post feet (lowest 0.4 above their base) one step deeper; door leaf one step deeper (the sheet's
  darker door, `#733A19` / `#89441A`) across the whole leaf by role.
- **Canvas:** `m068_canvas`; `m068_canvas_deep` blended over three steps along the eave edge (the hem) and round the
  chimney cut (soot), never across a whole slope.
- **Stone:** `m068_stone` on the course; **`m068_stone_light` on the corner blocks' upper tiers and the loose stones**
  (a role: the sheet's white blocks); the lower courses' bottom rows one step toward `m068_stone_dark` (ground grime);
  the chimney body `m068_stone`, its notched lower block one step toward `m068_stone_dark`, the cap `m068_stone_light`,
  the flue `m068_soot`.
- **Iron:** `m068_iron` hard against wood. **Rope:** `m068_rope` with one strand in four `m068_rope_deep`.
- **Banner:** `m068_banner`; emblem `m068_cloth_white` (hard). **Glass:** `m068_glow` (Neon).
- **Hues stay together:** timber 21–25°, s 0.74–0.82 rendered; timber_end 30–36°; canvas 38–45°, s 0.18–0.26; stone
  warm grey (R ≥ B, h 330–20°, s ≤ 0.08), never lavender or blue; iron h 330–360° / s ≤ 0.15 or neutral.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m068_timber` | side_sheet wall-plank median **`#AB5C2A` ± 12** (swatch `#A95929`); f34 W median `#90491F` ± 15 | 21–25°, 0.74–0.82 | every wooden piece | rough 0.85 |
| `m068_timber_end` | exploded caps `#F9A528` ± 15 (lit end faces `#F79744` / `#FBAA51`) | 30–36°, 0.78–0.86, lighter than timber | caps, cut ends, saddles | rough 0.8 |
| `m068_timber_deep` | `#7A3A16` ± 12 (between the mid faces and the shade quartiles) | 20–24°, 0.80–0.86, v ≤ 0.50 | plank-end and foot bands, door leaf (blend) | rough 0.9 |
| `m068_canvas` | side_sheet roof `#FEF0C9` ± 10 (swatch `#F6E2BF`); start from M064's calibrated `#FDE4BC` | 38–45°, 0.18–0.26 | both slabs | rough 0.95, low spec |
| `m068_canvas_deep` | `#E6C8A2` ± 12 (M064's; the exploded shade `#ECCCA3`) | 33–38° | hem and chimney blends | rough 0.95 |
| `m068_stone` | side_sheet course `#A6A1A5` ± 12; f34 `#938A8E` ± 15 (swatch `#C2B6B7`) | R ≥ B, s ≤ 0.08 | course, chimney body | rough 0.9 |
| `m068_stone_light` | f34 corner block `#AD9E9B` ± 12, lit `#D0BEB9` | warmer, lighter than stone | corner blocks' upper tier, loose stones, chimney cap | rough 0.9 |
| `m068_stone_dark` | `#6C6A70` ± 12 (close-up B shade) | as stone, v ≤ 0.45 | grime band, chimney notch block (blend) | rough 0.9 |
| `m068_soot` | `#2A2425` ± 10 | v ≤ 0.18 | flue | rough 1.0 |
| `m068_iron` | f34 lantern frames `#53484A` ± 12; close-up A plate `#5A575C` | s ≤ 0.15, v 0.30–0.40 | lantern frames, brackets, plates, rivets, bars, hinges, ring, hoops, crossarm bands | rough 0.55, metal 0.4 |
| `m068_glow` | glass `#FBBD0A` ± 12, emission 1.0 (Neon) | 42–48°, s ≥ 0.9 | lantern glass | Neon |
| `m068_rope` / `_deep` | side ties `#F4BD51` ± 15 / `#B8862E` | 38–44°, 0.60–0.72 | ties, lashings, end bands, banner X | rough 0.95 |
| `m068_banner` | f34 `#D71A1E` ± 12 (swatch `#CC2422`) | 355–3°, s ≥ 0.82 | banner | rough 0.9 |
| `m068_cloth_white` | `#F6F0EA` ± 8 | s ≤ 0.06 | emblem | rough 0.9 |

**Calibration warnings:**
- **Orange-brown timber, not red and not flat orange** (W08; W10 `#8A4A22` read brown): hue 21–25°, s ≥ 0.74 on the
  side render; the lit tops (stairs, floor, bargeboard tops) must not clip (M052 finding 4).
- **Canvas** (M064 ruling 1): the key-lit slope may clip in the kit studio; keep the hue-correct cream and judge the
  canvas on `side_sheet`; never shift the base salmon to save the f34. Not yellow (W10 verifier `#E3CFA0`).
- **Pale ends must be a real step** (M050 finding 6): `timber_end` ≥ 25 units lighter than `timber` in G; but caps
  must not blow out (M052 finding 4: cap tops ≤ v 0.98 rendered).
- **The undersides and door recess read as the same wood** (M048 finding 7): door one blend step deeper only.
- **Stone warm grey, not lavender** (066 decision 15): R ≥ B on every rendered stone median.
- **Rope golden, not lemon and not orange-brown**: hue 38–44° rendered; Y in the f34 comes from the glass only.
- **Iron dark warm grey, not black**: v 0.30–0.40 on `junction_cu`.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- Wall planks: by distance along the plank from the chosen end. Posts: by height above their base. Stone: by height
  (grime) on the lower course's lower 0.4. Canvas: by distance from the eave edge (hem 0.6) and from the chimney cut.
- **Hard edges only** where materials meet: iron | wood, rope | wood / canvas, glass | iron, banner | emblem,
  timber_end | timber (end faces are separate faces by role).

### 5.6 Texture (Tint) and finish

- **Tint:** 0.05 per wooden piece, 0.04 per stone block (broad, per piece, never per triangle), canvas `K.texture`
  mottling 0.03 per slab, iron 0.02.
- **Finish:** wood matte (rough 0.85), canvas 0.95, stone 0.9, iron rough 0.55 / metal 0.4, glass Neon.

### 5.7 Re-measure (final renders against the sheet, same masks)

- **Timber:** side_sheet wall-plank median within 12 of `#AB5C2A`; f34 W median within 15 of `#90491F`; f34 lit
  quartile within 15 of `#E48235`, shade within 15 of `#552B14`.
- **Canvas:** side_sheet C median within 10 of `#FEF0C9`, s ≥ 0.18.
- **Stone:** side_sheet S median within 12 of `#A6A1A5`; corner blocks lighter than the course.
- **Glass:** f34 Y median within 12 of `#FBBD0A`; **iron** on `junction_cu` within 12 of `#5A575C`.
- **Shares and value bands** per §1.2.

## 6. Joins and contact (no floating pieces, no buried pieces)

- **Shells:** every block, plank, post, cap, beam, rafter, board, bracket, peg, rope, canvas slab, lantern piece,
  banner piece and prop part is its own closed shell, all in one hero object.
- **Chain to the ground:** blocks → ground; corner blocks → ground; deck → course and sleepers; wall planks → course
  and rows below; posts → corner blocks; plates → posts; door posts → ground; lintel → door posts; collars → lintel /
  plates; rafters and bargeboards → plates; purlins → rafters; ridge beam → bargeboard crotches; canvas → rafters,
  purlins, ridge; ties → canvas and plates; lashings and bands → their timbers; chimney → trimmers → rafters; lanterns
  → rings → brackets → plate / wall; stairs → ground; banner → crossarm → pole → ground; props → ground.
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**. A shell floats if its nearest distance
  to every other shell and the ground is > 0.03, or if it doesn't chain to the ground. The new risks: the bracket
  plates and pegs on the chamfered plate ends; the saddle blocks between crossing bargeboards; the ridge beam in the
  crotches; the chimney on its trimmers; the eave ties over a sagging canvas edge; the threshold beam.
- **Buried shells:** nothing more than 0.05 inside anything beyond its stated seat. Ray parity against the posts,
  plates, rafters, ridge, blocks and props as solids after the final placement (`m047._Solids`).
- **Thin slabs hide pass-throughs** (M064): the 0.12 canvas is never more than 0.06 deep, so run **`pierce_report`**
  (edges of any non-canvas shell crossing a canvas surface twice): the ridge beam's top edge under the fold, the
  rafters' tops, the bargeboards, the chimney, the ties. Target 0.
- **No intersections between big pieces:** the crossing bargeboards touch at the crossing (no boolean, M064 decision
  4); the rafters meet the ridge beam's faces; the door leaf clears the wall's inner face by 0.0–0.02; the lanterns'
  frames clear the walls.
- **Walk report** (§2.10), minimum clearances printed.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.
- **Winding:** 0 errors per shell, checked with a parity ray test, not only the signed volume.
- **Parts:** each exported part self-contained (the DoorFrame with leaf, hinges and caps touching; the GableFrame with
  its lashing; the Banner chained; the Lantern with its bracket) and **square to its axes** (M050 finding 7).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** three lanterns with bright amber glass (and a fourth on the back gable in the r34, §3.7). The
window opening is dark, not lit. The chimney has a dark flue and no smoke is drawn; a stone chimney on a lived-in hut
implies smoke (W10's hut carried `chimney_smoke`). Cast shadows are the illustration's.

- **Stage 5 (lighting):**
  - The glass of all three lanterns on `m068_glow` with **emission 1.0** (exports as Neon). m009's / m064's
    `_glow_mats` preview so the Blender render shows the glass as Roblox Neon will.
  - **No light painted on the walls or ground** round the lanterns; no window glow.
  - Studio notes (Requires Manual Validation): the timber reads orange-brown in daylight; the interior reads dark from
    outside through the door and windows by shadow, not paint; at night the door lanterns light the stairs and the
    door, the eave lantern the −X wall.
- **Stage 6 (VFX):**
  - **Lanterns (3 sockets):** `heat_glow` at each glass centre, overridden to M064's steady halo:
    `emitters=[{"name": "Halo", "texture": "glow_soft", "color": ["#FFC23A", "#FF9A1E"], "size": [1.4, 1.7],
    "transparency": [0.65, 1.0], "lifetime": [1.0, 1.5], "rate": 2, "speed": [0, 0.05], "spread": 0,
    "light_emission": 1.0}]`; `light={"color": "#FFB347", "brightness": 1.0, "range": 12, "flicker": True}` on L2 and L3,
    range 10 on L1. Sockets (build frame, through `M.mk`'s `fx=` list): L1 (−8.30, −6.60, 7.60), L2 (−4.40, −9.10, 7.30),
    L3 (+4.40, −9.10, 7.30).
  - **Chimney (1 socket, decision §8.10):** `chimney_smoke` at the flue (+2.20, −3.40, 19.30), overridden **thin and
    pale** (W10's goal 28): `emitters=[{"name": "Smoke", "texture": "smoke_puff", "color": ["#BDB8B4", "#E4E0DC"],
    "size": [1.0, 3.5], "transparency": [0.6, 1.0], "lifetime": [3, 5], "rate": 2, "speed": [1.5, 2.5], "spread": 6,
    "light_emission": 0.0, "acceleration": [0.4, 0.3, 0], "drag": 0.3, "rotation": [0, 360], "rot_speed": [-15, 15]}]`,
    `light=None`.
  - Check the export STATS line reports **4 sockets** on the hero (3 `heat_glow`, 1 `chimney_smoke`), 1 on the Lantern
    part, 1 on the Chimney part.
- **Collision (decision §8.11):**
  - **Hero `precise`** (PreciseConvexDecomposition): walls, floor, stairs, plinth and props solid; the doorway, the
    interior and the windows must stay open. **Requires Manual Validation in Studio:** a default character climbs the
    0.87 risers without jumping, walks through the door, turns round inside and walks out; the decomposition fills
    neither the doorway nor the room. Fallback: hero `none` plus Studio colliders (four wall boxes split at the door,
    the floor box, two roof slabs, a stair wedge, plinth boxes, prop boxes).
  - Parts: `TimberCabinRoofPanel` `box`; `…RidgeBeam` `box`; `…Chimney` `box`; `…Banner` `none`; `…Lantern` `none`;
    `…WallPanel` `box`; `…WindowWall` `precise`; `…DoorFrame` `precise`; `…GableFrame` `hull`; `…Floor` `box`;
    `…Stairs` `precise`; `…Foundation` `box`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched all 2498 names in `art/roblox/kit/**/manifest.json` and the repo text (`git grep`)
for Hut, Cabin, Lodge, Shack, Cottage, Chimney, Lantern, Banner, Stair, Foundation, Gable, RoofPanel, WallPanel, Plank
and the candidates:
- **W10:** `TimberHut`, `TimberHutCornerPost`, `…Doorframe`, `…Floor`, `…OpenWorkshop`, `…RidgeBeam`, `…Roof`,
  `…Standard`, `…WallPanel`, `…Weathered`; `GuardLodge*` (incl. `GuardLodgeOpenGuardHut`, `…WallPanel`, `…Door`);
  `CanvasTentLantern` (M064), `FireAndLightLanternPost`, `FortWorkshopLanternHook`, `PalisadeWallBanner`, many
  `…Stairs` / `…Plank` names. **M066 / M067 (decided, not exported):** `CanvasShelter*`, `TrestleTableSet*`.
- **`TimberCabin` (and every `TimberCabin…` part name below), `PlankCabin` and `m068` occur nowhere** in the manifests
  or the repo text. No owned name is a substring of them.

| Object | Part | Why |
| --- | --- | --- |
| `TimberCabin` | hero: foundation, floor, walls, posts, windows, doorframe (leaf open), gable frames, roof frame, canvas, ties, chimney, stairs, 3 lanterns, banner, 2 barrels, crate, 2 stones | W10 owns `TimberHut*` |
| `TimberCabinRoofPanel` | "Roof Panel (Left / Right)": one canvas slab with its ties (the other side is the same mesh mirrored) | the labels |
| `TimberCabinRidgeBeam` | "Ridge Beam" with its end bands | the label |
| `TimberCabinChimney` | "Chimney" with cap, flue and its smoke socket | the label |
| `TimberCabinBanner` | "Banner Pole + Banner" | the label |
| `TimberCabinLantern` | "Lantern (x2)" with its wall bracket and `heat_glow` socket | the label |
| `TimberCabinWallPanel` | "Wall Panel (Left / Rear)": a plain five-row plank wall between two posts | the labels |
| `TimberCabinWindowWall` | the window wall panel (exploded) | modelling notes: "wall panels" |
| `TimberCabinDoorFrame` | door posts with caps, lintel, header, door leaf (closed, hinge stored) | modelling notes: "doorframe" |
| `TimberCabinGableFrame` | "Front Gable Frame": collar, crossed bargeboards, saddle, lashing, cleats | the label |
| `TimberCabinFloor` | "Floor": deck planks and threshold | the label |
| `TimberCabinStairs` | "Stairs" | the label |
| `TimberCabinFoundation` | "Stone Foundation (x4)": one side's two-course run with a corner block | the label |

- Props in Studio reuse M064's exported `CanvasTentBarrel` and `CanvasTentCrate` (no new prop parts).
- Palette keys `m068_*` (§5.4). Collection `Kit/M068 Timber Hut`. Sockets: 3 × `heat_glow` + 1 × `chimney_smoke` on
  the hero. Stored points `m068_offset`, `m068_centre`, `m068_door`, `m068_hinge`, `m068_chimney` (hero);
  `m068_hinge` (DoorFrame); `m068_hang` (Lantern).

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **floor 2.60, door clear 3.60 × 7.00, walls 14.40 × 16.40, plates 11.20, ridge 16.0, chimney 19.4;
   hero ≈ 20.6 × 26.1 × 19.4** (recommended: the door sets the scale for a walk-in hut; the side and rear elevations
   set the heights). Alternatives: door 6.5 (a hut ≈ 7 % smaller, tight for hats) or 8.0 (the kit props read as toys).
2. **Budget (§4.3):** **building ceiling 8000 (README), plan 6200–7200, every part under 1000** (recommended).
   Alternative: STAGES' 4000 (drops the second foundation course, the eave ties, two lanterns and the props).
3. **Build frame and origin (§1.1, §2.13):** **front −Y (the door gable), ridge along Y; origin at the bbox bottom
   centre with the offset, centre, door, hinge and chimney points stored** (recommended).
4. **Door (§3.11):** **hero leaf open inward 95° (hut enterable with `precise`); the DoorFrame part with the leaf closed
   and its hinge stored** (recommended). Alternative: closed as drawn.
5. **Chimney and dressing positions (§3.6):** **the f34's: chimney (+2.20, −3.40) in the front third, banner back-left,
   barrel A and crate on −X, barrel B front-right** (recommended). Alternative: the side / rear / r34 / top cells'
   back chimney and front-left banner.
6. **Lanterns (§3.7):** **three (eave + two at the door)** (recommended). Alternatives: four (+ back gable) or two.
7. **Plinth (§3.9):** **floor 2.60 with three equal 0.87 risers** (recommended). Alternative: floor 3.40 (the sheet's
   band) with 1.13 risers.
8. **Windows (§3.8, §3.10):** **both centred, real openings with two iron bars, no glow** (recommended).
9. **Grass (§3.15):** **none in the hero; kit ground scatter in Studio** (recommended). Alternative: six tufts.
10. **Chimney smoke (§7):** **a thin pale `chimney_smoke` socket at the flue** (recommended: implied, as W10's hut).
    Alternative: no smoke (the sheet draws none).
11. **Collision (§7):** **hero `precise` with a Studio walk-in check (fallback `none` + Studio colliders); parts as
    listed** (recommended).
12. **Comparison cameras (§2.12):** **`side_sheet (90, 3)` governs heights and length; `f34_sheet (−40, 15)` (probe az
    −35 … −50, e 10–20) governs the read and dressing; `front3q_low (−45, 5)`, `rear_sheet (−90, 3)`, `r34_sheet
    (−135, 15)` and `top` content; close-ups `junction_cu`, `base_cu`, `underside_cu`, `apex_cu`, `door_cu`,
    `door_walk`, `inside_cu`, `thumb`, `spin`; parts and exploded shots; scale shot. Floor hidden in every `*_sheet`
    render** (recommended).
13. **Exports (§8 table):** **the hero plus twelve parts** (recommended). Alternative: eight (fold WindowWall into
    WallPanel, drop Floor, Foundation and RidgeBeam).
14. **Colour (§5):** **timber `#AB5C2A` rendered with golden ends `#F9A528` and a deep blend partner; cream canvas
    `#FEF0C9` rendered; warm grey stone with white corner blocks; dark warm iron; golden rope; red banner with a white
    emblem; Neon glass; by role and position, never by facing** (recommended).
15. **Props (§3.12):** **kit sizes (barrel 2.80, crate 2.30); lanterns and banner at building scale** (recommended).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **The old hut's failures (W10 / MODEL_PROGRESS row 83: "flat plank walls, no framing/window/door frame; plain
   roof"; CHECKLIST 6.5/10).** Plank rows with dark seams and staggered joints, posts proud of the walls, barred
   windows with frames, a full door frame and gable frame, a canvas roof with a seam grid, ties and bargeboards.
2. **A hut a character can't enter** (the brief). Door ≥ 3.50 × ≥ 6.90, three equal 0.87 risers, interior ≥ 7.8 clear,
   the leaf out of the path; the walk report printed; the Studio walk-in recorded as Requires Manual Validation.
3. **A solid box with a painted door or window** (WorldModeling §13.3). Real openings; walls as closed 0.40 planks so
   the inside shows wood; `inside_cu` proves it.
4. **Single-sided or see-through canvas** (Roblox culls back faces; M064 pitfall 2). Closed 0.12 slabs; `underside_cu`
   and the spin prove it from inside and below.
5. **Floating or buried pieces** (STAGES; 035 / 036 round 1; 046; M051 findings 2–3). Brackets, pegs, saddles, ties,
   the ridge beam, the chimney and the threshold each touch what holds them. Count: floating 0, buried 0; report the
   worst sink per kind.
6. **Pass-throughs a bury report can't see** (M064 stage 1: the ridge poked 0.04 through the fold along its length).
   `pierce_report` = 0 on the canvas; the ridge beam's top 0.00–0.03 under the canvas.
7. **Rope that reads as flat collars or thin outlines** (M048 finding 1; M051 finding 1; M064's peg band). Twisted
   tubes Ø 0.20–0.24 on the lashings and bands; the eave ties are flat straps by design (the sheet's U ties) but must
   wrap both the canvas edge and the plate, not float on the canvas.
8. **Rope loops sinking into square timbers** (M064 stage 1: radial loops cut corners, sank 0.12). Use `hull_loop`
   (mitred offset of the timbers' hull) for the apex lashings, the banner X and the ridge bands.
9. **Canvas blown out or salmon** (M064 ruling 1; W10 yellow canvas). Hue-correct cream; judge C on `side_sheet`.
10. **Red, brown or flat-orange wood** (W08; W10 `#8A4A22`). Hue 21–25°, s ≥ 0.74; per-piece Tint so nothing is one flat
    colour; pale ends a real step but not clipped (M052 finding 4).
11. **Colour by facing** (042 ruling; 054 m9). The shaded −X wall, door recess, dark pole and canvas underside are
    light. `K.check` facing correlation < 0.5 per material; end faces coloured by member role.
12. **Hard colour bands** (M051 finding 5; M052 finding 3). Plank-end, post-foot, hem and grime bands blend over three
    steps.
13. **Egg stones and box plinths** (M034 / M037). Bevelled blocks with broken corners, two courses with offset joints,
    flat bottoms, corner blocks proud of the course.
14. **Winding and non-planar quads** (044; M051 finding 8). 0 winding errors per shell (octagonal beam ends, cut
    rafters, gable boards, canvas grid, emblem shells); triangulate the canvas grid at build time.
15. **Thin faces** (M064 ruling 2). Report corners under 3°, fail only under 0.3°.
16. **Proportions from the stylised cells** (§3.2–§3.6, §3.12). The side and rear elevations set heights and length,
    the f34 sets the width, read and dressing; the "front" and "rear" cells are a three-quarter and the −X elevation;
    the top is content only.
17. **Tiny details that vanish** (WorldModeling §18). Check `thumb`: plinth band, plank seams, door, lantern glow,
    banner emblem readable; rivets and toggles may vanish (they are first in the cut order).
18. **Names and scope.**
    - No `TimberHut*`, `GuardLodge*`, `CanvasTent*`, `CanvasShelter*` names.
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit the frozen shared helpers (`kit_models.py`, `kit_mcp.py`, `build_kit.py`, `lib/vfx.py`) or other models'
      builders; import from the committed ones (`m009`, `m038`, `m047`, `m048`, `m050`, `m051`, `m052`); copy from
      `m064`; don't touch other models' collections.

## Open questions for the main session

1. **Scale (§1.1):** is a door of 3.60 × 7.00 on a 2.60 floor (walls 14.4 × 16.4, chimney 19.4) the right hut size?
   The sheet's own proportions give a 3-stud door; the recommendation scales the hut to the door and keeps the props at
   kit size, so the barrels and crate read about half the sheet's relative size.
2. **Budget (§4.3):** use the README's building ceiling of 8000 (plan 6200–7200) instead of STAGES' 4000?
   Recommended: yes; 4000 would cost the second plinth course, the eave ties and two lanterns.
3. **Door (§3.11):** open inward in the hero so the hut is enterable (recommended), or closed as every view draws it?
4. **Chimney and dressing (§3.6):** the f34 and front cells put the chimney in the front third and the banner at the
   back-left; the side, rear, r34 and top cells mirror both. Recommended: the hero view's layout, with the other four
   cells' positions recorded as misses. Alternative: the back chimney and front-left banner.
5. **Lanterns (§3.7):** three (recommended: the f34), four (adds the r34's back-gable lantern) or two (the exploded's
   "x2")?
6. **Plinth height (§3.9):** floor 2.60 with 0.87 risers (recommended) or floor 3.40 with 1.13 risers (the sheet's tall
   stone band; needs the Studio stair check like 052)?
7. **Chimney smoke (§7):** add a thin pale `chimney_smoke` socket that the sheet doesn't draw (recommended), or none?
8. **Grass (§3.15):** leave it out of the hero (recommended) or add six small tufts?
9. **Parts (§8):** twelve parts (recommended) or eight? Should the props reuse M064's exported barrel and crate
   (recommended) rather than new `TimberCabin…` parts?
10. **Name:** `TimberCabin` (recommended; W10 owns `TimberHut*`) or `PlankCabin`?

## Decisions (main session, 2026-11-01)

1. **Scale is set by the door:** 3.60 × 7.00 clear on a 2.60 floor, walls 14.4 × 16.4, plate tops 11.2, ridge 16.0,
   chimney top 19.4. The 6.5 and 8.0 door alternatives are rejected; furniture scale stays shared with 064/066/067.
2. **Budget:** the building ceiling of 8000 tris applies (plan 6200–7200); every part stays under 1000.
3. **Door:** the hero's leaf stands open inward 95° so the cabin is enterable. A DoorFrame part carries the leaf closed,
   with its hinge stored.
4. **Chimney and dressing follow the f34:** chimney in the front third at (+2.2, −3.4), banner at the back-left. The
   side, rear, r34 and top cells' positions are recorded misses, not blockers.
5. **Three lanterns**, as the f34.
6. **Plinth:** floor 2.60 with three 0.87 risers; the taller band is a recorded miss.
7. **Chimney smoke:** add the thin pale `chimney_smoke` socket (implied by the chimney, kept subtle).
8. **No grass in the hero;** ground scatter is placed in Studio.
9. **Twelve parts.** Barrel and crate shapes are copied from `m064.py` into `m068.py` (no cross-module import) under
   this model's own names.
10. **Name `TimberCabin`.**
11. **Sheet mirroring:** the f34 governs; the front-to-back mirroring of the f34 and front cells against the other four is
    recorded, and verifiers compare mirrored cells with a mirrored render.

## Paused (2026-11-02)

Stopped on request before any build ran. State for the next modeller:
- **Done:** read the study, decisions and builders; stage 1 design worked out (below). `art/blender/kit/mcp/m068.py`
  holds the first half of the builder: palette and calibration targets, helpers copied from m064 / m066 (no mNNN
  imports), and part functions for every piece: foundation runs and corner blocks, floor and threshold, plank walls
  (6-sided V-seam planks, staggered joints, window and door cuts), window, posts, plates with bracket plates, rafters,
  purlins, trimmers, ridge beam with rope bands, crossed bargeboards (half-lap X built from three non-overlapping
  pieces plus a saddle), collars, back frame posts, gable infill, door frame and leaf (hinged at (-1.80, -7.59), open
  95 deg), two canvas slabs (5 x 2 sagging panels, chimney hole), U tie straps, chimney, stairs, lanterns with
  brackets, banner set, barrel, crate, stones.
- **Not done:** the second half (hero_all assembly, the 12 part wrappers, NOTES / COLLISION, _new / _post / UV,
  shell / contact / bury / pierce / rope-end / walk / placement reports, build(), renders and mirrored renders). It was
  written but the append failed (the command was too long), so it is not in the file. Nothing has been run or rendered:
  no numbers yet. Stages 2-6 all open.
- **Deviations from the spec (needed for consistency, to confirm):** pitch 32 deg, not 34 (at 34 the canvas line
  passes through the 11.20 plates); canvas eave at |x| 7.45 (0.25 past the plates, at plate-top height, so the U ties
  wrap the canvas edge and plate); bargeboards 0.90 x 0.92 at |y| 9.25-10.15, 0.80 proud of the canvas, heels seated on
  the plates; plates run to |y| 10.20; ridge beam ends at |y| 10.75; corner blocks 1.64 square (inner faces under the
  posts, so the wall and floor planks do not sink into them); chimney centre y -3.45 (clear of the rafter);
  banner pole (-9.55, 10.55) (0.5 clear of the bargeboard foot); door lanterns at x +-4.70; no apex rope lashing (it
  would pierce the canvas apex; the golden saddle stands in), recorded.
- **Next:** write the second half by porting m066's build / report / render section (rename the m066 keys to m068, a
  4-socket hero check, walk proxy over stairs and doorway). Run `build()` on port 9877 against
  `art/blender/assets/kit/wip/M068.blend`, then fix contact and bury issues, calibrate, render, and record stages 1-6
  here.

## Rulings on the paused deviations (main session, 2026-11-03)

All accepted, because each one keeps parts from piercing or sinking into each other:
1. **Pitch 32°.** The ridge stays at 16.0, so only the slope changes; the sheet's pitch is read by eye and 2° is within it.
2. **Canvas eave at |x| 7.45** at plate-top height, with the U ties wrapping canvas and plate.
3. **Bargeboards** 0.90 × 0.92 at |y| 9.25–10.15, 0.80 proud of the canvas, heels on the plates; plates to |y| 10.20;
   ridge beam ends at |y| 10.75.
4. **Corner blocks 1.64 square**, chimney centre y −3.45, banner pole (−9.55, 10.55), door lanterns at x ±4.70.
5. **No apex rope lashing:** the golden saddle block stands in. Record it as a miss against the sheet's apex wrap; a verifier
   should not fail the model on it alone.

## Stage 1 — Modelling (2026-11-03)

Built in a background Blender (port 9877, work file `art/blender/assets/kit/wip/M068.blend`, saved after the good
build). The builder's second half is written: `hero_all` (every part function placed by §2, leaf open 95°), the twelve
part wrappers, `NOTES` / `COLLISION`, `_new` / `_post` (stage 2–3 pass), the shell, ray-parity winding, contact, bury,
pierce, rope-end, walk and placement reports, `build()` / `report()`, and the renders (sheet views, mirrored views,
spin, close-ups, parts, exploded, scale, thumb).

**Changes to the first half, each found by a report or a render:**
1. **Chimney centre y −3.50** (was −3.45): its +Y face still overlapped the rafter at y −1.94 by 0.04; now 0.01 clear.
   Canvas cut y −4.83 … −2.17 (0.03 clear).
2. **Trimmers in the rafters' own band** (0.50 × 0.60, tops 0.015 under the canvas like the rafters) under the
   chimney's two long edges (x 0.90–1.40 and 3.00–3.50), and the **chimney's lower block cut to the 32° pitch** on
   them (foot z 15.28 uphill … 13.66 downhill). The old level trimmers at z 12.9–13.6 met the rafters only on the
   downhill side; the uphill one hung 0.8 under them, held only by the chimney. From inside (`underside_cu`) the stone
   foot sits flush between the rafters, as close-up C.
3. **Canvas:** the sagged grid node inside the chimney cut is dropped (it was a loose vertex).
4. **Ridge beam top edges** lowered by the first panel column's sag (−0.0295 at x ±0.50; 0.01 under the canvas at
   the apex): its top edges crossed the sagging canvas underside (pierce report 4). Chamfer 0.10 (0.08 left 0.30°
   slivers on the 21.5-long chamfer faces).
5. **Crossarm in two pieces** butting the pole's flat −Y / +Y faces (a knobbed stub and the long arm): the single arm
   was buried 0.255 through the pole. The X lashing still wraps pole and arm.
6. **Bracket plates z 10.53–11.07** (0.54 tall, spec 0.70): on the plate's flat outer face inside its 0.12 chamfers,
   so plate and bracket touch face to face (the taller plate met only the chamfers, 0.039 off).
7. **Floor part:** two short dark feet under every deck plank (the exploded's feet); six feet left the middle planks
   loose. The hero keeps its two hidden sleepers.
8. **RoofPanel part ties** are U clips round the canvas edge (the part has no plate to wrap); the hero's ties run on
   round the plate to the wall.
9. **`_earclip`** takes the valid ear with the largest smallest corner and refuses a diagonal through another vertex:
   the crossed bargeboards' lower piece had a 0.0° triangle.
10. **Bargeboard tips 1.60 out** (was 1.00): tips 1.64 above the apex, the sheet's big X (`apex_cu`).
11. **Plank chamfers 0.10** (was 0.07): the dark V seams between rows read in the f34, as on the sheet.

**Door leaf.** Decision 3's 95° is kept: hinged at (−1.80, −7.59) on the left jamb, the leaf stands almost square to
the front wall inside the room, x −1.80 … −2.11, y −7.59 … −4.04 (§2.5's x −1.80 … −5.36 describes a leaf swung flat
against the wall, about 180°). It is 0.8 clear of the walk proxy.

**Views against the sheet** (`f34_sheet`, `side_sheet`, `rear_sheet`, `r34_sheet`, `front3q_low_sheet`, `top_sheet`,
`M068_views.png`, `M068_spin.png`, `M068_mirror.png`, close-ups):
- The read matches: an orange plank cabin on a pale two-course plinth with white corner blocks, a cream gable roof
  with golden ties and crossed bargeboard tips, the door between tall posts under lintel and collar, two door lanterns
  and the eave lantern glowing, the grey chimney behind the ridge in the front third, the banner at the back-left,
  barrel A and the crate along −X, barrel B front-right, the stairs.
- Close-ups: `junction_cu` (octagonal golden plate end, iron plate with rivets and golden peg, rafter, canvas, U tie,
  close-up A), `base_cu` (two-tier corner block proud of the course, broken corner, post foot, offset joints,
  close-up B), `underside_cu` (rafter and purlin grid, canvas underside in the cells, the chimney foot between the
  trimmers, close-up C; no see-through canvas), `apex_cu` (crossed tips, golden saddle, ridge-beam end with its two
  rope bands), `door_cu`, `inside_cu` (floor, open leaf, barred window from inside, roof underside), `door_walk` (the
  proxy on the stairs, in the doorway, inside), `lantern_cu`, `chimney_cu`, `thumb_sheet` (plinth band, rows, door,
  glow and banner still read at 180 × 150).
- Spin (az 0 … 315, e 10): nothing floats, no see-through faces.
- **Mirrored renders (decision 11):** `side_mirror_sheet`, `rear_mirror_sheet`, `r34_mirror_sheet`,
  `top_mirror_sheet` (and `M068_mirror.png`) render the hero mirrored front-to-back (scale y −1), so the chimney sits
  at the back and the banner at the front-left as those cells draw them. The whole hero is mirrored, so in these
  renders the door gable is at the back too (the r34 mirror shows the door; the side mirror shows the door lanterns
  at the back end): compare only the chimney and dressing in them.
- **Recorded misses** (each ruled or decided): chimney and dressing mirrored against the side / rear / r34 / top cells
  (decision 4); the f34's −X window near the front end (§3.8, centred); five plank rows against the side cell's four
  (§3.13); the stone band 0.23 of the plate height against 0.29 (decision 6); props at kit size (§3.12); no apex rope
  lashing (ruling 5, the golden saddle stands in); the leaf drawn closed (decision 3); no grass (decision 8); no back
  gable lantern (decision 5).

## Stage 2 — Optimisation and cleanup (2026-11-03)

`build()` → `report()` problems list: **empty**.

| Object | Tris | Size (studs) | Shells |
| --- | --- | --- | --- |
| `TimberCabin` (hero) | **7612** (ceiling 8000; plan 6200–7200) | 20.75 × 26.50 × 19.40 | 340 |
| `TimberCabinRoofPanel` | 372 | 7.53 × 18.49 × 4.95 | 5 |
| `TimberCabinRidgeBeam` | 280 | 1.36 × 21.50 × 1.67 | 5 |
| `TimberCabinChimney` | 52 | 3.00 × 3.00 × 5.74 | 3 |
| `TimberCabinBanner` | 584 | 1.46 × 4.10 × 15.80 | 16 |
| `TimberCabinLantern` | 180 | 1.50 × 1.85 × 4.20 | 13 |
| `TimberCabinWallPanel` | 408 | 14.40 × 1.10 × 8.09 | 12 |
| `TimberCabinWindowWall` | 520 | 1.20 × 16.40 × 8.09 | 20 |
| `TimberCabinDoorFrame` | 288 | 6.60 × 2.25 × 10.40 | 16 |
| `TimberCabinGableFrame` | 152 | 17.38 × 1.80 × 7.24 | 7 |
| `TimberCabinFloor` | 408 | 13.14 × 17.09 × 0.90 | 34 |
| `TimberCabinStairs` | 96 | 4.80 × 3.20 × 1.73 | 8 |
| `TimberCabinFoundation` | 260 | 1.64 × 15.83 × 2.60 | 16 |

- Hero tris by kind: planks 2040 (100 shells), foundation blocks 832 (52), rope 800 (14: 8 ties, 4 ridge bands, 2 X
  loops), canvas 536 (2), beams 520, lantern iron 396, barrels 408, iron 324, posts 288, pole 240, boards 168, crate
  84 + corner plates 160, corner blocks 144, emblems 136, frames 96, banner 80, pegs 72, door 72, chimney 52, bars 48,
  bungs 40, stones 40, glass 36. Over the 7200 plan by 412, under the 8000 ceiling; nothing from the never-cut list was
  cut. If the main session wants the plan, the cut order (§4.3) starts with the rivets and the crate's inner braces.
- **Every object:** non-manifold edges 0, **bowties (non-manifold verts) 0**, boundary 0, wire 0, loose 0, zero-area
  0, n-gons 0 (triangulated), duplicate verts 0, normals outward, **winding errors 0** per shell (edge contiguity)
  and **0 inward faces by ray parity** per shell, self-intersections 0, every shell closed with positive volume.
- **Contact:** floating 0, unchained 0 in the hero and every part. Seats (hero, gap): post on corner block 0.003,
  plates on posts 0.003, collar on lintel 0.003, lintel on door posts 0.003, header to lintel 0.007, bargeboards on
  plates 0.003, saddle 0.003, ridge to bargeboard 0.025, rafter on plate 0.003, canvas on rafter 0.004, canvas on
  ridge 0.008, tie to canvas / plate 0.005, bracket plate 0.005, peg 0.005, trimmer to rafter 0.002, chimney on both
  trimmers 0.003, L1 hook / ring 0.010, L1 strap / plate 0.003, L2 strap / wall 0.029 (plank face jitter), crossarm /
  pole 0.003, sleeve 0.003, banner 0.000, threshold beam 0.015, deck on sleeper 0.006, open leaf over the deck 0.020,
  upper tread against the door posts 0.003.
- **Buried 0.** Worst sinks: banner > banner 0.034 (emblem into the cloth), rope > wood 0.027 (ridge bands), wood >
  wood 0.005, metal 0.005. **Pierce 0** (no edge crosses the canvas or banner twice). **Rope ends:** all touching.
- **Thin corners:** hero 544 faces under 3° (long planks, plates and chamfers), smallest 0.38° (floor 0.3).
- **Walk (§2.10):** the proxy walks from (0, −15) to (0, 0): surface profile ground → 0.87 (y −13.1) → 1.73 (−11.5) →
  2.60 (−9.9); **risers 0.87 / 0.86 / 0.87**; min clearance **0.40** (to the plinth under the threshold); turning at
  the centre 1.93. **Door clear 3.60 wide at every height, 7.00 tall** (lintel underside 9.60; header 9.603 in the
  wall plane). Interior's lowest overhead member the plates, **7.82 above the floor**. Lantern bottoms L1 6.40, L2 /
  L3 6.20.
- **Placement:** floor top 2.60; plate tops 11.20; canvas top 16.00 (pitch 32°); canvas eave |x| 7.45; chimney top
  19.40; walls 14.40 × 16.40; bargeboard tips z 17.64 (1.64 above the apex); ridge beam y ±10.75 (0.60 past the
  bargeboards); lantern glass centres L1 (−8.30, −6.60, 7.40), L2 / L3 (±4.70, −9.10, 7.20); banner 2.11 wide, top
  14.15, tip 6.40.
- **Origin and stored points:** every object's origin at its bbox bottom centre, transforms applied. Hero
  `m068_offset` (−0.074, 0.55, 0); `m068_centre` (0.074, −0.55, 2.60); `m068_door` threshold (0.074, −8.55, 2.60),
  facing −Y; `m068_hinge` axis bottom (−1.726, −8.14, 2.62), closed yaw 0, open yaw 95; `m068_chimney` (2.274,
  −4.05, 19.30) (all object-local). DoorFrame `m068_hinge` (−1.80, 0.817, 2.62); Lantern `m068_hang` (0, −0.174,
  3.11) and `m068_mount` (0, 0.924, 3.825); Chimney `m068_flue` (0, 0, 5.641); Banner `m068_top` (0, −1.20, 15.80).

## Stage 3 — UV (2026-11-03)

Angle-based unwrap (`M.smart_uv`, margin 0.008), overlapping faces cut free and unwrapped again. Hero: 2815 islands,
**0 overlaps, 0 flipped**, smallest island gap 0.016, density spread 0.999–1.001, conformal stretch p95 1.00. Every
part: 0 overlaps, 0 flipped, gaps ≥ 0.0159. The exporter writes its own palette UVs.

## Stage 4 — Materials, colour and texture (2026-11-03)

**How it was measured.** `K.calibrate` on the studio dome for every key (targets in `TARGETS`), then the hero
re-rendered at the sheet cameras with a transparent film (scratch renders in `<temp>\mr\`) so the alpha drops the
paper, and every render measured with the §1.2 masks against the same cells of the sheet.

**Calibrated palette** (written into `PALETTE`):

| Key | Hex | Dome render (target) | Note |
| --- | --- | --- | --- |
| `m068_timber` | `#9E5A2B` | — | kept: the lit long wall lands within 12 of `#AB5C2A` (below); the dome's `#8A512A` darkens it to about 20 off |
| `m068_timber_end` | `#C08024` | (`#F9A528`) | the dome's `#CA8B28` clipped R at 255; one step lower keeps cap tops under v 0.98 |
| `m068_timber_deep` | `#653516` | `#783916` (`#7A3A16`) | dome value |
| `m068_canvas` | `#EADEBF` | — | tuned on `side_sheet` (M064 ruling 1); the dome asked for a salmon `#FAC5AD`, rejected (§5.4 warning) |
| `m068_canvas_deep` | `#BAA58F` | `#EBC8A3` (`#E6C8A2`) | dome value |
| `m068_stone` | `#969295` | — | neutral-warm: the dome's `#858690` rendered B > R |
| `m068_stone_light` | `#A39A9A` | dome `#9B9599` → `#C1B3B0` (`#C4B6B2`) | the dome value made warmer and a step lighter (the white corner blocks) |
| `m068_stone_dark` | `#5E5C60` | (`#6C6A70`) | the dome's `#595A64` made warm |
| `m068_soot` | `#2A2425` | `#2E2524` (`#2A2425`) | |
| `m068_iron` | `#534E52` | dome `#524F56` → `#585255` (`#585255`) | the dome value with R ≥ B |
| `m068_glow` | `#EEB406` | Neon (`#FBBD0A`) | |
| `m068_rope` / `_deep` | `#F2C45E` / `#93712E` | (`#F4BD51`) / `#B6842E` (`#B8862E`) | rope raised from `#DDBB5A`: the f34 ties read 25 dark |
| `m068_banner` | `#C2191C` | `#D51A1E` (`#D71A1E`) | unchanged |
| `m068_cloth_white` | `#F0EAE4` | — | unchanged: the dome cannot reach white in its shaded half |

**Chimney tones (by role):** the sheet draws the whole stack a mid grey darker than the plinth (f34 `#887F84`): the
lower block half way to `stone_dark`, the upper block and the cap a quarter of the way (was `stone` / `stone_light`).

**Re-measured on the final renders** (ours / sheet):

| Region | Ours | Sheet | Δ (R, G, B) | Target |
| --- | --- | --- | --- | --- |
| Lit long-wall planks (`rear_sheet`, −X) | `#A35321` | side cell `#AB5C2A` | 8, 9, 9 | ± 12: **pass** |
| f34 wood, whole cell | `#A85623` | `#90491F` | 24, 13, 4 | ± 15: **miss (lighting)** |
| `side_sheet` canvas C | `#FEEBC3` | `#FEF0C9` | 0, 5, 6 | ± 10: **pass** |
| f34 stone S | `#978D8B` | `#93898B` | 4, 4, 0 | ± 15: **pass** |
| f34 glass Y | `#FFBE04` | `#FBBD0A` | 4, 1, 6 | ± 12: **pass** |
| f34 rope R | `#F7BC4E` | `#FCC459` | 5, 8, 11 | ± 15: **pass** |
| f34 banner B | `#CE1617` | `#D71A1E` | 9, 4, 7 | ± 12: **pass** |
| iron (dome render) | `#585255` | close-up A `#5A575C` | 2, 5, 7 | ± 12: **pass** |

- **Shares, f34:** W 61.5 (59 ± 8), C 19.1, S 13.5 (11 ± 4), K 1.8 (2–6, just under), B 1.8 (2–5, just under), Y 1.5
  (0.8–2.4), R 0.7; W : H **1.294** (1.25 ± 0.08). **Side:** W 54.7 (53 ± 8), C 23.8 (20 ± 6), S 16.2 (15 ± 5), K 1.0
  (4–9: under), Y 0.5 (0.5–1.5).
- **Recorded misses, all lighting, not colour:** the sheet lights its f34 from the front-right (its −X wall is in shade,
  `#88441C`, the front gable lit), the studio from the front-left, so our f34 wood median is lighter and the value
  bands are 1 / 79 / 20 against 16 / 37 / 48; the studio key leaves the +X wall of `side_sheet` in shade (`#84441B`;
  stone `#716D6F`), which is why the lit −X elevation (`rear_sheet`, the sheet's own "rear" cell draws the same planks
  `#AE5E2A`) carries the wall calibration. Colour is never chosen by facing. The key-lit canvas slope clips to
  `#FFFFE5` on the f34 / rear views (M064 ruling 1); judged on `side_sheet`. K is low because the sheet's K counts its
  ink outlines; our dark pieces are the flue, window bars, the room seen through the openings and the lantern frames.
- **Blends and texture:** per-piece Tint 0.025–0.05 on every plank, post, board and block (`_rt` seeds), `K.texture`
  mottling per piece; plank-end bands one step toward `timber_deep` on planks over 2.0 long (seeded end), post feet
  one step deeper, the door leaf one step deeper, the lower plinth course one step toward `stone_dark`, the canvas hem
  in three steps toward `canvas_deep` along the eave and round the chimney cut; pale golden ends by member role (plate
  and ridge end faces, bargeboard tips and feet, saddles, door-post caps, pole foot band, lintel ends). Hard edges only
  where materials meet. Finishes: wood rough 0.85–0.9, canvas 0.95, stone 0.9, iron 0.55 / metal 0.4, glass Neon.
- `K.check` (facing correlation and the kit checks) passes on every object.

## Stage 5 — Lighting (2026-11-03)

- The three lanterns' glass is `m068_glow` at **emission 1.0** (exports as Neon); `_glow_mats` previews it unshaded in
  Blender as Roblox shows Neon. No light painted on walls or ground; no window glow (the sheet draws the window dark).
- **Studio notes (Requires Manual Validation):** the timber should read orange-brown in daylight (not red, not flat
  orange); the interior reads dark from outside through the door and windows by shadow; at night the door lanterns'
  PointLights (range 12) light the stairs and door and the eave lantern's (range 10) the −X wall. The hero's `precise`
  collision must leave the doorway and room open: walk a default character up the 0.87 risers, through the door,
  turn round inside and walk out (fallback: collision `none` plus Studio colliders, §7).

## Stage 6 — VFX (2026-11-03)

- **Hero: 4 sockets** (export stats): 3 × `heat_glow` at the glass centres L1 (−8.30, −6.60, 7.40) range 10, L2 / L3
  (±4.70, −9.10, 7.20) range 12, overridden to M064's steady halo (`_fx_spec`); 1 × `chimney_smoke` at the flue
  (2.20, −3.50, 19.30), thin and pale (`SMOKE`, no light). Glow key on the hero: `m068_glow` only.
- **Parts:** `TimberCabinLantern` 1 × `heat_glow` (range 12) at its glass; `TimberCabinChimney` 1 × `chimney_smoke`
  at its flue. Every other part 0.
- The renders realise the sockets (halo and smoke puffs show in the views, spin and close-ups).

**Left for the verifier / main session:** the hero is 412 tris over the 7200 plan (under the 8000 ceiling); the f34
wood median and value bands, the side view's shaded +X wall and the low K share are lighting misses recorded above;
the mirrored renders mirror the door as well.

## Stage 7 verification (round 1)

Independent verifier, read-only, background Blender on a copy of the kit file taken after the main session built 068
into it (`build()` not called, nothing saved). Every number below was re-measured with the verifier's own bmesh / BVH /
ray-parity / raster code, and every view was rendered by the verifier into `<temp>\v068\r\` and set beside the matching
sheet cell (mirrored cells beside a front-to-back mirrored render, decision 11).

**Result: FAIL, 7/10.** One blocker: the walls and gable infill leak light through every plank joint, so the inside of
the walk-in hut shows bright slits. Everything else is clean or a recorded ruling.

### Technical (all objects)

| Object | Tris | Size (studs) | Shells | Floating / unchained | Deepest sink |
| --- | --- | --- | --- | --- | --- |
| `TimberCabin` | 7612 / 8000 | 20.750 × 26.500 × 19.400 | 340 | 0 / 0 | 0.041 (banner hem in its sleeve) |
| `…RoofPanel` | 372 | 7.534 × 18.494 × 4.949 | 5 | 0 / 0 | 0.000 |
| `…RidgeBeam` | 280 | 1.360 × 21.500 × 1.674 | 5 | 0 / 0 | 0.020 (rope bands) |
| `…Chimney` | 52 | 3.000 × 3.000 × 5.741 | 3 | 0 / 0 | 0.000 |
| `…Banner` | 584 | 1.456 × 4.100 × 15.800 | 16 | 0 / 0 | 0.041 (hem), X lashing 0.029 |
| `…Lantern` | 180 | 1.500 × 1.847 × 4.197 | 13 | 0 / 0 | 0.005 |
| `…WallPanel` | 408 | 14.400 × 1.100 × 8.094 | 12 | 0 / 0 | 0.000 |
| `…WindowWall` | 520 | 1.203 × 16.400 × 8.094 | 20 | 0 / 0 | 0.000 |
| `…DoorFrame` | 288 | 6.600 × 2.246 × 10.397 | 16 | 0 / 0 | 0.000 |
| `…GableFrame` | 152 | 17.375 × 1.800 × 7.238 | 7 | 0 / 0 | 0.000 |
| `…Floor` | 408 | 13.140 × 17.090 × 0.900 | 34 | 0 / 0 | 0.000 |
| `…Stairs` | 96 | 4.800 × 3.197 × 1.730 | 8 | 0 / 0 | 0.000 |
| `…Foundation` | 260 | 1.640 × 15.830 × 2.600 | 16 | 0 / 0 | 0.000 |

- Thirteen objects in `M068 Timber Hut`, names as §8. Every object: 0 non-manifold edges, 0 boundary, 0 wire, 0 loose
  verts, **0 bowtie verts**, 0 zero-area faces, 0 n-gons (all triangles), 0 duplicate verts, **0 winding errors** (edge
  direction test), 0 negative-volume shells, **0 faces failing the ray-parity test**. Smallest corner 0.377° (hero and
  ridge beam; 544 hero corners under 3°, ruling M064-2 fails only under 0.3°). Origin at the bbox bottom centre on every
  object (error 0.0000 on x, y and z), rotation 0, scale 1, no modifiers, no custom normals, no unused material slots.
- Contact (gap ≤ 0.03, chained to the ground): every shell of every object chains to the ground. Bury (sample points
  inside another shell by three-ray parity, depth to its surface): nothing over 0.05; the deepest are the stated seats
  (banner hem 0.041, X lashing 0.029, ridge bands 0.020, emblems, glass, rivets ≤ 0.005).
- Pierce (edges of one shell crossing another's surface twice): **0 through either canvas slab.** The 75 hero hits are
  all seats or coplanar touches; a 0.02-grid overlap volume on each pair gives at most 0.012 depth (lashing on the pole,
  banner in the sleeve) and 0.0006 for the open leaf against the front-wall plank ends.
- Canvas: 0.120 thick everywhere (2912 samples), sag 0.000–0.078 below the pitch plane, cut clear round the chimney.
- UV: one `UVMap` per object; 0 overlapping pixels (1024² raster), 0 flipped faces, all islands inside 0.008–0.992.
- Colour by role, not facing: per-material correlation of the Tint value with the face normal ≤ 0.035 on every big
  material (timber, canvas, stone, rope); the hero-wide luminance against x / y / z / |z| is 0.00 / 0.00 / 0.00 / 0.03.
- Sockets: hero 3 × `heat_glow` at L1 (−8.30, −6.60, 7.40) range 10 and L2 / L3 (±4.70, −9.10, 7.20) range 12 with the
  M064 halo, 1 × `chimney_smoke` at (2.20, −3.50, 19.30) thin and pale, no light; Lantern part 1 `heat_glow`; Chimney
  part 1 `chimney_smoke`; others 0. Glow key `m068_glow` only, spec emission 1.0 (Neon).
- Stored points (object space + `m068_offset` (−0.074, 0.55, 0)): centre (0, 0, 2.60); door threshold (0, −8.00, 2.60)
  facing −Y; hinge axis (−1.80, −7.59, 2.62), closed 0, open 95; chimney flue (2.20, −3.50, 19.30). All correct.

### Sizes and walkability (build frame)

- Floor: every deck and threshold plank top at 2.600. Walls 14.40 × 16.40 (posts' outer faces), plate tops 11.20,
  canvas ridge 16.00 (pitch 32°, ruling 1), canvas eave |x| 7.45, chimney top 19.40, bargeboard tips 17.64 (1.64 above
  the apex), ridge-beam ends |y| 10.75 (0.60 past the bargeboards). Planks 0.38–0.40 thick, rows 1.612 tall; posts
  1.10; bargeboards 0.90 wide. Lantern glass 1.00 × 1.61, centres L1 z 7.40, L2 / L3 z 7.20.
- Side fractions (chimney top 19.40): plate 0.577, ridge 0.825, wall length 0.845, roof with bargeboards 1.046, window
  opening z 5.54–8.78 centred at y 0. All in tolerance.
- **Walk** (own proxy, 2 × 1 body to 4.4 and 1.1 head to 5.5, stepping on the highest surface under its footprint):
  ground → 0.87 (y −13.15) → 1.73 (−11.55) → 2.60 (−9.95), **risers 0.87 / 0.86 / 0.87**. Above the 1.0 step band
  the proxy touches nothing from (0, −15) to (0, 0); 0 box intersections. **Door clear 3.60 at every height, 7.00
  tall** (lintel underside 9.60). Turning at the centre (24 yaws): no intersection, 0.10 clear. Interior lowest overhead
  member the plates / collars at 10.40 = **7.80 above the floor**. Lantern bottoms L1 6.40, L2 / L3 6.20; door
  lanterns 1.10 off the door posts. The open leaf stands at x −1.80 … −2.40, y −7.60 … −4.04, out of the path.
- Hero 20.75 × 26.50 × 19.40 against the builder's 20.7 ± 0.4 × 26.5 ± 0.5 × 19.4 (spec §2.11's 20.6 × 26.1 before
  the ruled pole move). Hero 7612 tris: under the 8000 ceiling, 412 over the 7200 plan.

### Views against the sheet (masks of §1.2; sheet → ours)

| View | W : H | Wood median | lit / mid / shade % | K % | S % |
| --- | --- | --- | --- | --- | --- |
| f34 (−40, 15) | 1.322 (1.245 without far grass) → **1.295** | `#90491F` → `#A85624` | 16/37/48 → 1/80/19 | 2.5 → 1.9 | 11.1 → 13.6 |
| side (90, 3) | 1.215 → 1.237 | `#A65927` → `#84441C` (+X in shade) | 12/55/33 → 0/18/82 | 4.2 → **1.1** | 14.9 → 16.1 |
| rear (−90, 3) | 1.301 → 1.352 | `#AA5A26` → `#A35322` | 11/56/33 → 0/77/23 | 3.2 → 1.4 | 13.5 → 12.1 |
| r34 (−135, 15) | 1.359 → 1.077 (content only) | `#A35421` → `#9E5324` | 11/53/36 → 0/81/19 | 2.1 → 0.7 | 13.5 → 15.1 |
| front3q_low (−45, 5) | 1.322 → 1.414 (recorded) | `#8E461A` → `#A55523` | 12/39/49 → 1/75/25 | 2.6 → 1.9 | 9.7 → 12.7 |
| top | 1.209 → 1.297 (turned 90°, content only) | `#A95E26` → `#C4672C` | — | 2.2 → 0.7 | 8.0 → 3.7 |

- Per material (camera rays mapped to faces, f34 unless stated; sheet in brackets): timber `#AB5824`, lit −X wall
  (`rear_sheet`) `#A45422` (side cell planks `#AB5C2A`, Δ 7, 8, 8: pass); canvas side `#FFF6CD` (`#FDF0C9`, pass;
  the key-lit slope clips to `#FFFFE5`, M064 ruling 1); course `#918886` / `#A69C99` (`#938A8E`), corner blocks
  `#B4A49D`, lit `#D1BFB7` (`#AD9E9B` / `#D0BEB9`: lighter than the course, pass); iron `#484141` (`#53484A`, pass);
  glass `#FFBE03` (`#FBBD0A`, pass); banner `#CE1616` (`#D71A1E`, pass); rope `#FFD75A` (`#FBCA58`, pass); pale ends
  `#D9861F`, lit `#F59925` (caps `#F9A528`, pass); emblem `#FFF5E4`. Hues stay orange (22–25°), stone R ≥ B.
- **f34:** the read matches: plank cabin on a pale two-course plinth with lighter corner blocks, cream gable roof with
  golden ties, crossed bargeboard tips with the golden ridge-beam end, door between tall posts under lintel and
  collar, the eave lantern by the front-left corner and the two door lanterns glowing, the chimney behind the ridge in
  the front third, banner back-left, barrel A and the crate along −X, barrel B front-right, the two-tread stairs. W : H
  in tolerance. The wood median, value bands and the lit / shade quartiles miss (studio key from the front-left, the
  sheet's from the front-right; recorded at stage 4).
- **side / rear:** heights, plinth, centred barred window with frame and sill, four ties per eave, bargeboards rising
  at both ends; chimney and dressing mirrored (decision 4; the mirrored renders put them where the cells draw them).
  The window reads white, not dark (minor 1).
- **r34 / front3q_low / top:** content as the cells, with the recorded misses (no back lantern, dressing mirrored, door
  on the gable, grass, five rows). The r34 sheet camera sits nearer the −X wall than (−135, 15), so its W : H is not
  comparable (content only).
- **Close-ups:** B: two-tier corner block proud of the two courses, broken corner, post foot (match). C: rafter and
  purlin grid, canvas in the cells, the chimney foot between the trimmers, no see-through canvas (match; the underside
  renders khaki-grey in the studio's shade against the sheet's warm `#C5A37F`). A: octagonal golden plate end, iron
  plate, rivets and peg are present but sit under the bargeboard heel (minor 3). Apex: crossed tips, saddle, pitched
  golden ridge-beam end with two rope turns.
- **Parts against the exploded cell:** roof slab with ties, ridge beam with pale ends and bands, chimney with cap and
  flue, banner set, lantern on its bracket, plank wall between posts, window wall, door frame with the closed leaf,
  strap hinges and ring, gable frame, floor on short feet with the threshold tongue, two-tread stairs, foundation run
  with its corner block: all read as drawn.
- Spin (eight azimuths, e 10): nothing floats, no see-through canvas. Thumb (180 × 150): plinth, rows, door, glow and
  banner read.

### Blockers

1. **Light leaks through every wall joint and the gable infill (shows from inside).** Horizontal rays from inside escape
   through all four walls at every row seam (170 / 174 / 193 / 98 escapes on R / L / B / F at the four seam heights),
   and `<temp>\v068\r\v_inside_wallL.png` / `v_inside_gable_B.png` show bright lines along the seams and joints. The gaps
   go straight through the 0.40 planks:
   - row seams 0.005 (rows end at z 3.915 / 5.535 / 7.155 / 8.775 and the next starts 0.005 higher);
   - butt joints 0.04 (long walls y −2.62 / −2.58 and 3.38 / 3.42; back wall x −2.02 / −1.98 and 2.58 / 2.62);
   - gable boards 0.010 at x ±0.50 and 0.030 at ±1.46, ±2.43, ±3.39, ±4.36, ±5.33 (434 escapes below the canvas line);
   - the outer gable boards' edges (|x| 6.28) to the plates' inner faces (6.30): 0.02, z 11.2 … 11.9.

   §2.4 says "never a step that opens a seam to see through", and pitfall 3 asks that "the inside shows wood". Fix:
   close every through-gap on the inner face and keep the seam read from the outer chamfers. Make each row's bottom
   meet the row below (0 gap; the 0.10 V-chamfers still draw the dark seam), and make butt-joint ends touch. Make the
   gable boards touch edge to edge, or back each joint with a hidden 0.20 batten inside the wall plane. Run the outer
   boards to the plate faces. Then re-run the inside escape scan (target 0 escapes except the door and the two windows)
   and the bury report (touching faces, no sinks).

### Minors

1. **Windows read as white holes in the side and rear elevations (shows).** Both windows are real openings at the same
   y and z, so square-on views look straight through the hut; the sheet draws them dark (`#201717`). Side K 1.1 against
   the §1.2 tolerance 4–9 (the window alone is about 2.6 % on the sheet); f34 K 1.9 and B 1.9 just under their 2–6 and
   2–5 floors. A ruling is needed if it should change: for example, a closed inner shutter or a dark board inside one
   window, or offset the two windows a little along Y so they don't line up.
2. **No bargeboard cleats (shows slightly).** §2.6 asks for two cleats per bargeboard, and the top cell and f34 draw
   them; the build has none, and the stage notes don't record the cut. The hero has 388 tris of headroom: about 96 tris
   for eight cleats, or record the cut.
3. **Close-up A's projecting beam end reads weakly (shows slightly).** The plate ends (|y| 10.20) stop only 0.05 past
   the bargeboards' outer faces (10.15). The heel sits over the end, so the golden octagon, iron plate and peg are
   tucked under it in the f34 and `junction_cu`. The sheet's eave-beam ends stand clear of the gable with the plate on
   their side. This follows ruling 3. If wanted, the plates could run to about |y| 10.8 with the bracket plate and peg
   moved out with them.
4. **f34 value spread (shows; recorded at stage 4).** Wood lit / mid / shade 1/80/19 against 16/37/48. The median is 24
   off in R and the quartiles 30–37 off: the studio lights the −X wall that the sheet leaves in shade. Colour is by
   role, not by facing.
5. **Canvas seam grid faint (shows on top and f34).** The 0.078 sag gives only soft shading. The top cell draws a clear
   5 × 2 seam grid per slope (§3.17 decided no seam paint). The key-lit slope clips (M064 ruling 1).
6. **Chimney notches barely read (shows slightly).** The 0.10 step at the joint is lost at sheet distance. The sheet's
   stack shows two blocks with a notched joint and a dark flue cap.
7. **Floor gaps (shows slightly from inside).** The 0.06 deck seams and a 0.03 slot between the threshold planks
   (y −7.62) and the deck (−7.59) across the doorway show the lit studio ground below in `inside_cu`. In Studio the
   space under the floor is enclosed by the plinth, so it should read dark. Check it during the walk-in validation.
8. **Hinge straps 0.05 into the door's clear width (does not show).** At x −1.748 inside the room, behind the wall
   plane; the doorway and walk path are unaffected.
9. **Budget (does not show).** 7612 is 412 over the 7200 plan and under the 8000 ceiling (decision 2).
10. **Recorded rulings, not scored:** chimney and dressing mirrored against the side / rear / r34 / top cells, the
    window centred, five rows, the 0.23 plinth band, kit-size props, no apex lashing, the leaf open, no grass, no back
    lantern, pitch 32°, chimney y −3.50 (ruling 4 said −3.45; moved 0.05 for rafter clearance at stage 1).

## Main session after round 1 (2026-11-03)

Round 1 failed on the see-through joints. The fix round covers:
1. **Blocker: close every joint.**
   - Plank rows meet with no gap, and butt-joint ends touch. The 0.10 chamfers still draw the dark seam outside.
   - Gable boards touch edge to edge, and the outer boards run to the plate faces.
   - After the fix, an inside escape scan may find openings only at the door and the two windows.
2. **Floor:** close the deck seams and the 0.03 threshold slot the same way, so no ground shows from inside.
3. **Windows read dark (minor 1):** a closed inner shutter of dark boards 0.30 behind the bars, on both windows. The sheet
   draws the openings dark, and the shutter keeps square-on views from seeing through the hut.
4. **Bargeboard cleats (minor 2):** add the two cleats per board that the spec asks for (about 96 tris; the hero stays
   under 8000).
5. **Eave-beam ends (minor 3):** run the plates out to about |y| 10.8, so the plate end, iron plate and peg project past
   the bargeboard heel as in close-up A, if that clears every other part. Otherwise record it.

Minors 4–10 stay recorded and are not part of the fix.

## Fixes after round 1

Fix modeller, background Blender (work file `art/blender/assets/kit/wip/M068.blend`, saved after the good build). Only
`m068.py` changed. Every change is in the builder and was checked by rebuilding with `build()`.

**1. Closed joints (blocker).** The shared overlap is `OVL` = 0.002. Neighbours sink that far into each other, so no
seam goes straight through and no vertices coincide (an exact touch would leave duplicate verts and coplanar end caps).
- Plank rows overlap 0.004 at the back (`row_z`). The 0.10 outer chamfers still draw the dark V seams. The top row runs
  0.002 into the plate (end walls: under the gable boards).
- Butt joints: the plank ends overlap 0.004 (long walls y −2.60 / +3.40, back wall x −2.00 / +2.60). The door header
  runs 0.002 into the top rows' ends at the jambs.
- Corner posts sink 0.002 into the corner blocks and the plates. This closes the 0.003 slits under the feet and over the
  tops.
- Gable infill (rewritten):
  - The boards overlap 0.004 edge to edge. Every other board is 0.01 thinner on both faces, so no faces are coplanar
    and the boards still read.
  - Board bottoms sit 0.004 into the top row and the posts. Board tops sit 0.002 into the canvas underside.
  - A board under the ridge beam runs into its chamfered underside.
  - A new apex block runs from the ridge's pitched top into the canvas, with its peak in the slabs' apex seam. Its fan
    is explicit, so no edge crosses a slab twice. It closes the slit over the ridge, which ran out past the gables.
  - The outer boards wrap the plate's inner chamfers and face, then run over the plate top onto the eave blocking.
- **End-bay sag 0.05 (`SAG_END`, was 0.08)** at the y ±7.535 nodes only. At 0.08 the sag over the gable plane would
  have sunk the boards' straight tops 0.055 into the canvas (over BURY). Now the deepest sink is 0.039.
- **Eave blocking (new, `eave_block`).** One timber on each plate top, x 6.85–7.08, between the gable planes, running
  0.002 into the plate and the canvas. It closes the slit between plate top and canvas: rays from the roof space left
  through it, and the inside scan found it. The rafter tails now stop against it at x 6.848, still seated on the
  plate.
- **Chimney.** The 0.03 ring between the canvas cut and the stack let light in. The cut is now 0.002 clear, under a
  flashing collar on the canvas: 0.12 past the stack, 0.10 tall, mortar grey, 0.002 into the canvas and the stack,
  32 tris. An exact-size cut was tried first and dropped: its rim faces were coplanar with the stack, and the pierce
  report flagged 7 edges.

**2. Floor.**
- The deck planks run 0.002 into the walls' inner faces and sit 0.002 into the underlay and courses.
- The two outer planks are notched round the corner posts and blocks (8-sided, corner at 6.112 / 7.112). They now cover
  the 0.8 × 0.5 corner holes, which looked down to the ground.
- New dark underlay board (`floor_under`) at x ±5.40, z 2.20–2.30, running 0.002 into the end courses. It shows in the
  0.06 deck seams as the dark gap and stops every ray. The sleepers sit under it; in the Floor part, the inner feet do.
- The threshold planks run 0.002 onto the deck (the 0.03 slot is gone).

**3. Inner shutters (minor 1).**
- Both windows have a closed shutter of two dark board leaves (`timber_deep` half way to soot) against the planks'
  inner face, 0.20 past the opening all round. The second leaf is set 0.01 back and is thicker.
- The windows now read dark in the side and rear views. Square-on views no longer see through the hut.
- WindowWall part: 544 tris.

**4. Bargeboard cleats (minor 2).**
- Two per board, eight in all: 0.40 along the board × 0.30 × 1.40, at 1/3 and 2/3 of the way from the foot to the
  apex, 96 tris.
- Each lies across the board's top face, 0.002 into it, and overhangs both faces by 0.25. The inner end crosses the
  canvas edge, as in the top cell.
- The cleats are 0.80 above the canvas, because the board is that proud of it (ruling 3), so they cannot rest on the
  canvas. Light timber.

**5. Eave-beam ends (minor 3).**
- The plates now run to |y| 10.80, with the iron bracket plates and pegs at |y| 10.10.
- The octagonal end, iron plate and peg project 0.65 past the bargeboard heel, as in close-up A (`junction_cu`).
- Nothing else is within reach: bargeboard feet over 0.1 off the peg, banner pole 1.9 away.

**Inside escape scan (`escape_report`, in `build()`'s report; problems if any ray leaves other than by the door).**
- Rays in 320 directions from 602 points inside the room and up into the roof space.
- Lower-hemisphere rays from 195 points 0.05 over the floor.
- Seam rays through each wall, both gables and the floor along every vertex coordinate in that plane ± 0.0007, square
  to the plane and slanted along the seam.
- Upper-hemisphere rays from a 0.04 grid just under the canvas round the chimney cut.
- Round-1 model, same scan: 35,424 rays out (walls 16,278, floor 8,702, windows 6,650, gables 3,603, eaves 191).
- **Now: 823,020 rays, 0 out except the door.**

**Numbers (`build()`, problems list empty).**

| Object | Tris | Shells |
| --- | --- | --- |
| `TimberCabin` | **7976** / 8000 | 358 |
| `…RoofPanel` | 372 | 5 |
| `…RidgeBeam` | 280 | 5 |
| `…Chimney` | 84 (collar) | 4 |
| `…Banner` | 584 | 16 |
| `…Lantern` | 180 | 13 |
| `…WallPanel` | 408 | 12 |
| `…WindowWall` | 544 | 22 |
| `…DoorFrame` | 288 | 16 |
| `…GableFrame` | 200 (cleats) | 11 |
| `…Floor` | 452 | 35 |
| `…Stairs` | 96 | 8 |
| `…Foundation` | 260 | 16 |

- **Every object:** 0 non-manifold edges, 0 bowties, 0 boundary edges, 0 duplicate verts, 0 winding errors, 0 ray-parity
  inward faces, normals outward. Floating 0, unchained 0, buried 0, pierce 0, rope ends all touching. UV: 0 overlaps,
  0 flipped, gaps ≥ 0.016.
- **Deepest sinks:** wood > canvas 0.039 (gable boards in the end-bay sag), banner 0.034, rope > wood 0.027, everything
  else ≤ 0.005.
- **Walk:**
  - risers 0.87 / 0.86 / 0.87;
  - walk clearance 0.40;
  - turning 1.95;
  - door 3.60 × 7.00;
  - overhead 7.82 above the floor.
- Hero 20.75 × 26.50 × 19.40.
- Sockets unchanged: hero 3 `heat_glow` + 1 `chimney_smoke`.
- The hero is 776 over the 7200 plan, 24 under the 8000 ceiling (decision 2). The next cut, if one is wanted, is the
  eight rivets (96).

**Renders (re-rendered by `build()`).**
- `inside_cu`: no bright seams in the walls, gable or floor; the floor seams read dark; the shutter is dark.
- `underside_cu`: the shutter and the chimney foot.
- `side_sheet` / `rear_sheet`: dark barred windows.
- `apex_cu`: the cleats on both boards.
- `junction_cu`: the projecting plate end with its iron plate and peg.
- `chimney_cu`: the collar.

## Main session after the fix round (2026-11-03)

The extra pieces the fix modeller added to close leaks are accepted: eave blocking on the plate tops, the mortar-grey
chimney collar, the end bays sagging 0.05, and two-leaf shutters. The hero at 7976 is under the 8000 ceiling (decision
2), so no rivets are cut. Round 2 goes to a fresh verifier.
