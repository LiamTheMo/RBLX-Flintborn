# 064 A-Frame Tent — spec

Reference: `art/blender/assets/references/064.png` (1024 × 1536 px). INDEX.md row 64: "Flintborn A-frame tent study".
The sheet's own header reads **"PAGE 66/132"** (top right), title **"A-FRAME TENT"**, subtitle "FLINTBORN — INDIVIDUAL
MODEL STUDY" (our number is INDEX's 064, §3.1).
Builder: `art/blender/kit/mcp/m064.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows an effect: two glowing lanterns**
(§7). The subject is **one walk-in A-frame canvas tent with its camp dressing**: two **A-frames of crossed square timber
poles** (one at each end) tied with **rope lashings** at the crossing, a **ridge pole** resting in the two crotches, a
**cream canvas** draped over the ridge in two sloped side panels with a **closed back** and an **open front doorway**
between two flaps, a **rolled door flap** tied across the top of the doorway, a **dark-metal lantern** hanging from the
front crossing, **corner knots** tying the canvas to the poles near their feet, **four pegs** with ropes, hem ties along
the long sides, a **teal sleeping mat and bedroll** inside, and outside a **storage crate**, **two barrels**, a **ground
lantern** and **two pale stones**.

Sheet text (paraphrased):
- **Title block:** "FLINTBORN / INDIVIDUAL MODEL STUDY", "A-FRAME TENT", "PAGE 66/132".
- **"FRONT THREE-QUARTER VIEW"** and **"REAR THREE-QUARTER VIEW"**: the assembled tent with its dressing, seen from the
  front-left and from the back-left.
- **"ORTHOGRAPHIC VIEWS (CONSISTENT MODEL)"**: "FRONT VIEW", "SIDE VIEW (RIGHT)", "REAR VIEW", "TOP VIEW" (what each
  cell really shows: §3.2–§3.4).
- **"EXPLODED CONSTRUCTION (ALL MAIN PARTS)"**, labels: "Canvas Panel (Left)", "Top Lashing", "Canvas Panel (Right)",
  "A-Frame Pole (Left)", "A-Frame Pole (Right)", "Tent Mat (Rolled + Flat)", "Storage Crate", "Stone (x2)", "Barrel"
  (its leader points at the second stone, §3.9), "Peg (x4)". The centre of the exploded view is the assembled front
  frame with the lantern(s), the closed back seen through the doorway and a dark box at the back of the floor (§3.10).
- **"MATERIAL PALETTE"**: seven swatches with short notes — Timber (Primary): warm, clean wood; Canvas Fabric: pale,
  slightly warm; Stone: pale faceted rock; Rope / Lashing: warm beige; Tent Mat (Fabric): muted green-blue; Metal
  (Lantern): dark, simple metal; Lantern Light (VFX): a separate effect, not baked in.
- **"MODELING NOTES"**: chunky readable forms; broad flat-shaded faces; clean simple silhouettes; reuse parts where
  possible (poles, lashings, pegs, crates); the canvas is simple low-poly planes with a slight sag and no
  high-frequency detail; the lantern glow is a separate VFX element and not part of the mesh; keep proportions
  consistent across the views.
- **"CONSTRUCTION CLOSE-UPS"**:
  - **"A. POLE JUNCTION (TOP)"**: two square, edge-chamfered poles crossing, their tips cut square; a chunky rope lashing
    of horizontal turns round both poles under the crossing plus diagonal turns forming a diamond below.
  - **"B. CANVAS ATTACHMENT & THICKNESS"**, callouts "Rope Lashing", "Canvas Thickness (simple plane)", "Canvas Wrap
    around Pole": the crossing seen close with a horizontal octagonal log (the ridge) bound in, the canvas draping from
    it in two slopes, the lantern hanging by a ring directly under the lashing.
  - **"C. UNDERSIDE VIEW"**: looking into the tent through the doorway: the front poles as big diagonals, the rolled door
    flap with two rope bands across the top, the lantern below it, the closed back wall, the bedroll on the flat mat,
    crates outside to left and right.
- **Game context and the old kit:**
  - **W10 row 2 `AFrameTent`** (`art/blender/scripts/kit/W10/a_frame_tent.py`; manifest `art/roblox/kit/W10/manifest.json`;
    goals `art/blender/renders/kit/W10/a_frame_tent_goals.md`) is the old kit's tent, from a different sheet (W10 had
    Closed / Rolled Doorway / Torn variants). The **exported** W10 hero is **11.10 W × 7.70 H × 10.55 D, 988 tris,
    `precise`, one `heat_glow`**; its parts `AFrameTentCanvasLeft` / `Right` (3.5 × 6.08 × 8.0, 100 tris, `none`),
    `AFrameTentFrameEnd` (88 tris, `box`), `AFrameTentMat`, `AFrameTentPeg` (0.28 × 0.8, 12 tris), `AFrameTentRidgePole`.
    The later script in the repo builds a narrower, taller tent (9.9 × 14.9 long × 8.7, hero 3116 tris, palette `w10_wood
    #8A4A22`, `w10_tentcanvas #EFE2C4`, `w10_rope #C48A38`, `w10_iron #575B64`, `w10_lantern #FFB022`, `w10_bedroll
    #2C6A52`); its verifier first failed it for **yellow canvas** (`#E3CFA0`), **merged panels** and a **wide footprint**.
    `MODEL_PROGRESS.md` row 80: **"thin poles, no lashing; flat canvas, no doorway; variants identical"**;
    `art/reference/kit/CHECKLIST.md`: AFrameTent 7/10.
  - **Related:** W10 `CampAwning` (10.9 × 8.2 × 10.1), `TimberHut` (13.0 × 10.7 × 12.5) are the same-class camp
    structures; M051 `RopeBridge` and M052 `TimberBoardwalk` are the nearest committed timber-and-rope builders (wood,
    rope and peg keys, twisted rope tubes, knots). WorldModeling §13.1 (timber vocabulary), §13.3 (canvas, camps: "build
    an A-frame from its two ends and ridgepole before fitting the canvas"), §13.8 (crate, barrel, lantern recipes).

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The page is near-white
(`#FDFCF9`); pieces cast a soft grey shadow to the lower right. Measured grey rules (`lines2.py`): header rule y 69;
three-quarter panel y 77–462 (title bars to y 103), divider x 515; ortho panel title y 471–496, cell labels to ≈ y 524,
cells to y 740, dividers ≈ x 277, 530, 780; exploded panel y 748–1235 (x 12–778), palette panel x 783–1012 y 748–1085,
notes panel y 1090–1265; close-up panel title y 1243–1265, cell labels to y 1294, cells to y 1486, dividers ≈ x 277,
672; footer rule y 1512.
- **Cells** (`m.V`, `m.X`): f34 (12,104,514,462); r34 (517,104,1012,462); front (12,526,275,740); side (280,526,528,740);
  rear (532,526,778,740); top (783,526,1012,740); exploded (12,778,778,1235); cuA (12,1296,275,1486); cuB
  (280,1296,670,1486); cuC (675,1296,1012,1486).
- **Swatches** (inner boxes, sd ≤ 2.2 except the glow gradient): Timber (804,785,833,808); Canvas (804,826,833,849); Stone
  (804,867,833,891); Rope (804,911,833,934); Tent Mat (804,954,833,978); Metal (804,998,833,1021); Lantern Light
  (804,1041,833,1065).
- **Masks** (`cls()` in `m.py`, HSV, h in degrees; a 2 × 2 opening drops specks; background = s < 0.10 and v ≥ 0.80,
  which also removes the grey cast shadow):
  - **C** canvas, lit and mid-shaded: warm (h < 60), s 0.08–0.42, v ≥ 0.74.
  - **W** timber **and** deep warm shade: warm, s ≥ 0.42 (not R, not Y), plus warm s ≥ 0.25 with v < 0.55. The sheet's
    shaded tent interior (`#7B4312`) falls in W with the poles, crate and barrels (§3.11).
  - **R** rope: h 27–60, s 0.40–0.72, v 0.55–0.92 (undercounts the brightest rope highlights, which go to Y).
  - **Y** lantern glow: h 33–60, s ≥ 0.72, v ≥ 0.80.
  - **M** mat teal: h 140–215, s ≥ 0.15. **K** metal / dark cool: h 215–260 with s ≥ 0.10 and v < 0.75, or v < 0.30 with
    s < 0.30. **S** stone: s < 0.25, v ≥ 0.40, h ≥ 250 or < 15. **G** grass: h 60–140, s ≥ 0.30.
  - Apply the same code to our renders (studio floor hidden, plain background).

**Scratch study material** (no Blender) in `<temp>\m064_study\` (the session scratchpad). Run with `uv run --no-project
--with pillow --with numpy --with scipy python <script> < /dev/null`.
- **Helpers:** `m.py` (boxes, `cls`, `clsimg`, `hsv`), `zoom.py` (`zoom.py x0 y0 x1 y1 scale out.png [grid]`),
  `probe2.py` (`probe2.py x,y …` → hex and HSV), `lines2.py` (frame rules), `sw.py` (swatches), `man.py` (manifest names;
  `man.py Cand1 Cand2 …`).
- **Measurements:** `measure.py` → `measure_out.txt` (bbox, W : H, fill, class shares, per-fifth shares, width profile;
  writes `cls_views.png`); `samp.py` → `samp_out.txt` (class medians per view and per named region, with lit and shade
  quartiles).
- **Zooms:** `z_fs.png` (front + side, 2×, grid 10), `z_rt.png` (rear + top), `z_rear3.png` (true side, 3×), `z_front4.png`
  (front 4×), `z_front_lf.png`, `z_front_r.png`, `z_front_lobj.png` (feet, pegs, knots), `z_f34.png`, `z_r34.png`,
  `z_f34_barrel.png`, `z_f34_r.png`, `z_side_l.png`, `z_peg.png`, `z_expl.png`, `z_expl_c.png`, `z_cu.png`, `z_cuA.png`,
  `z_cuB.png`, `z_cuC.png`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** a walk-in camp structure with dressing: **full asset, hero budget 4000 tris, plan about
  3300–3800; every part under 1000** (decision §8.16).
- **Overall read (check this first).** A **steep cream A-frame tent, a little wider than it is long**, standing on its
  pole feet:
  - at **each end an X of two square orange-brown poles** whose tips stick up 1.6 above a fat **rope lashing**; the X
    feet splay wide across the tent (front view: the frame is the whole silhouette, W : H 1.25);
  - the frames **lean outward at the ends** (the true side view is a trapezoid: ridge short, feet long);
  - a **cream canvas** in two broad sloped panels with soft diagonal sag creases, meeting at a straight ridge;
  - at the **front an open triangular doorway** between two cream flaps, the interior in deep warm shade, a **canvas
    roll** with two rope bands across the top of the doorway and a **lantern with amber glass** hanging from the front
    crossing just above it;
  - the **back closed** by a canvas triangle;
  - **chunky rope knots** where the canvas corners are tied to the poles low down, short ropes down to **square pegs**
    with pale caps, small rope ties along the hem;
  - inside, a **teal mat with tan bands** and a **rolled teal bedroll**;
  - outside, an **X-braced crate with iron corners** at the back-left, a **banded barrel with a ground lantern** at the
    front-left, a **second barrel** at the front-right, and **two pale faceted stones**.
  - It reads **cream canvas first, then the orange-brown X frames, then the lantern glow and the dark doorway**: true
    side cell C 67.1 %, W 28.6; f34 C 46.3, W 42.7, Y 1.5.
- **Focal silhouettes, in order:**
  1. The two X frames with tips above the ridge and the steep cream triangle between them.
  2. The open doorway with the roll and the glowing lantern over it; the dark interior with the teal mat.
  3. The rope lashings and corner knots; the crate, barrels and stones round the base.
- **Target size: pole tips 11.0; crossing (pole centrelines) 9.4; canvas ridge 10.1; pole feet ±6.4 across (X),
  frames leaning out to ±5.4 / ±4.6 along (Y); tent body 13.7 W × 11.7 L × 11.0 H; hero with dressing about 16.9 W ×
  13.2 D × 11.0 H** (decision §8.1). Tolerances: tips ±0.3, crossing ±0.25, foot spread ±0.25, door apex ±0.3.
  - **How it was derived.** No piece carries a real size. The scale is set by the **dressing** (the sheet draws the
    props at realistic proportions to the tent) and checked against **door clearance** for the 5.5-stud character:
    - Front cell (tent only): tips y 533, ground y 719 (**186 px**), crossing y 556 (163 px, 0.876 H), pole feet outer x
      30 / 262 (**232 px, W : H 1.247**), tips 37 px apart, pole width 12–13 px, door opening 96 px wide at the hem, its
      flap edges meeting at about y 573 (0.78 H), roll x 125–172 × y 603–617, hanging lantern glass 18 × 28 px, mat 90 px
      wide, bedroll 47 × 30 px, pegs 13 × 22 px.
    - True side cell (labelled "REAR VIEW", §3.3): tips y 540, ground y 718 (178 px); crossings x 600 / 700 (100 px =
      0.56 H); pole feet outer x 560 / 750 (190 px, **W : H 1.067**); canvas top edge x 612–690 (78 px = 0.44 H), canvas
      hem x 590–725 (135 px = 0.76 H); canvas end edges lean ≈ 9° from vertical, the poles ≈ 12°; corner knots at y
      680–705.
    - f34 (perspective): crate face 72 px and barrel 85 px against the tent's 340 px tip-to-foot height → **crate 0.21 T,
      barrel 0.25 T**.
    - **At T = 11.0** (0.0591 stud / px on the front, 0.0611 on the side): crate 2.3, barrel 2.75, peg 1.3 tall, pole
      0.75 thick, door opening 5.7 wide at the hem, mat 5.3 wide, bedroll 2.8 × 1.75, lantern glass 1.06 × 1.65.
  - **Why this size.**
    - **Against the character (5.5):** the crate is 0.42 C and the barrel 0.50 C, real-world proportions for a
      0.75 m crate and a 0.9 m barrel. The doorway (apex 8.4, 5.6 wide at the hem) is **1.9 wide at head height
      (5.5) and 2.7 wide at shoulder height (4.4)**: a character walks in upright, and it still reads as a snug tent;
      the roll's underside (6.0) and the lantern's bottom (6.9) clear the head. Inside, the canvas is **5.1 wide at
      head height** and 6.6 long: one or two players can stand. The tips are 2.0 C.
    - **Against the kit:** the same class as W10 `TimberHut` (13.0 × 10.7 × 12.5) and `CampAwning` (10.9 × 8.2); kit
      barrel staves are 3.1 long (W-kit `StorageBarrelStave`), so a 2.7 barrel sits in the family.
    - **Smaller is worse:** at T = 9.0 the door is 1.3 wide at head height and the lantern hangs at 5.6 (head height),
      and at the old W10 height (7.7) a character can't stand inside. **Larger** (T = 13) makes the crate and barrel
      read as toys beside it.
- **Build frame (decision §8.2):** front −Y (the doorway), +X right, ground z 0, the ridge along Y centred on x 0, y 0.
  The tent is symmetric about x 0 except the side-by-side pole order (§2.2) and the dressing. Stage 2 puts the origin at
  the bbox bottom centre (it lands at about (−0.33, 0, 0) of the build frame because of the dressing) and stores the
  offset (§2.11).

### 1.2 Measured views (`measure.py`)

| View (box) | Hero bbox (px) | W : H | fill | C | W | R | Y | M | K | S |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 (12,104,514,462) | 27–498 × 104–456 (472 × 353) | **1.337** | 0.521 | **46.3** | **42.7** | 2.9 | **1.5** | 1.5 | 2.6 | 1.8 |
| r34 (517,104,1012,462) | 548–997 × 118–450 (450 × 333) | 1.351 | 0.568 | 63.5 | 31.2 | 1.4 | 0.8 | 0.1 | 0.8 | 1.3 |
| **Front** (12,526,275,740) | 29–262 × 533–724 (234 × 192) | **1.219** (tent only 1.247) | 0.451 | 20.4 | 65.2 | 6.9 | 2.5 | 1.8 | 2.2 | 0.3 |
| "Side (right)" (280,526,528,740) | 293–522 × 534–724 (230 × 191) | 1.204 | 0.441 | 28.7 | 57.1 | 5.4 | 1.8 | 3.6 | 2.5 | 0.7 |
| **"Rear" = true side** (532,526,778,740) | 545–767 × 540–723 (223 × 184) | **1.212** (tent only 1.067) | 0.642 | **67.1** | **28.6** | 1.8 | 0.8 | 0.2 | 1.2 | 0.2 |
| Top (783,526,1012,740) | 809–976 × 532–733 (168 × 202) | 0.832 | 0.722 | 72.1 | 24.2 | 1.2 | 0.7 | 0.0 | 0.2 | 1.5 |

- Shares are % of the silhouette (background and cast shadow excluded). Grass G is under 1 % in every view.
- **Per fifth of height** (top → bottom, C / W / R / M): front 5/86/2/0, 4/74/19/0, 22/67/5/0, 26/67/3/0, 21/55/9/6 (the
  dark interior and the poles dominate; the rope peak in the second fifth is the lashing and upper ties); true side
  59/37/2/0, 81/19/0/0, 79/21/0/0, 75/22/1/0, 39/48/5/0 (canvas everywhere but the pole tips and the feet with their
  knots and dressing); f34 47/49/1/0, 71/26/1/0, 62/35/3/0, 31/53/5/3, 11/56/4/5.
- **Width profile** (silhouette width per tenth of height, fraction of W, top → bottom): front .16 .13 .27 .36 .48 .59
  .87 .90 .94 1.00 (the X tips, then a straight-sided triangle; the step at 0.6 H is the dressing behind the feet); true
  side .60 .60 .61 .66 .71 .76 .83 .93 .97 1.00 (a trapezoid).
- **Verifier tolerance:** front tent-only W : H 1.25 ± 0.05 (feet outer to tip height; the whole-silhouette front W : H
  is recorded, not scored: the dressing spreads wider than the sheet's front cell, §3.12); true side tent-only W : H
  1.06 ± 0.06, canvas top / hem lengths ± 0.4, C 67 ± 8, W 29 ± 7; f34 C 46 ± 8, W 43 ± 8, Y 1.5 ± 1.0, M 1.5 ± 1.0;
  fifths ± 12.

### 1.3 Silhouette and composition per view

**Front (`z_fs.png`, `z_front4.png`) — governs the frame across X, the doorway and the lantern height.** A near-level view
of the front end:
- the front X: two poles from the feet (outer x 30 / 262) to the crossing (y 556), tips 1.6 above it, the right-leaning
  pole drawn over the other at the crossing; a gold lashing at y 552–572;
- the canvas between the poles: two cream flaps from the poles in to the doorway edges, the flaps' inner edges turned
  back in a lighter strip near the hem; rope **upper ties** wrapping each pole and the canvas edge at y ≈ 590 (z 7.6);
- the **doorway** in deep warm shade (`#7B4312`) from the hem up to about z 8.4, the closed back triangle and a horizontal
  wooden edge at the back (y ≈ 665, §3.10), the teal **mat** with tan bands (x 100–190) and the **bedroll** (x 103–150)
  lying across at the back-left;
- the **roll** across the top of the doorway (z 6.0–6.8) and the **lantern** over it (the front cell draws the lantern
  lower, overlapping the roll: §3.6);
- **corner knots** on both poles at y 665–690 (z 1.7–3.1 on this cell), **pegs** with pale caps in front of the flaps
  (x 62–75, 220–232 → x ±4.7), the dressing partly hidden behind the feet (a barrel at the right, a crate corner at the
  left).

**"Side view (right)" (`z_fs.png`, `z_side_l.png`).** Not a side view: the doorway, the roll and the lantern all face the
camera and the −X panel shows as a sloped band to the left of the front X. It is the front end seen about 25–30° from
the front-left (§3.2). Content only: barrel A with the ground lantern at the far left, the mat and bedroll through the
door, pegs, a stone.

**"Rear view" (`z_rt.png`, `z_rear3.png`) — governs Y.** The true long-side elevation (§3.3): the side panel as a cream
trapezoid with soft diagonal creases from its top corners toward the middle of the hem; at each end the two poles of a
frame seen nearly edge-on, **slightly separated** (one behind the other: side-by-side poles, §2.2), leaning out ≈ 12°;
short horizontal stubs at the tips (the **ridge pole ends** sticking out past the crossings, §3.5); a lashing under each
crossing; **corner knots** (big figure-of-eight rope at y 680–705) where the canvas corners meet the poles; three small
rope **hem ties** along the bottom edge (x ≈ 602, 641, 690); the crate at the bottom-left.

**Top (`z_rt.png`).** Not a plan: a near-square cream canvas (136 × 140 px) with short crossed timbers at all four corners
(a real plan shows each frame as one line across the end), a faint centre seam, pegs and rope ties on the edges, the
crate below the bottom edge, a stone at the top right (§3.4). Content only.

**f34 (`z_f34.png`) — governs the dressing layout and the overall read.** From the front-left, above: the −X panel
broad and lit, the back X at the left, the front X at the right with the lantern hanging from its lashing, the roll
below the lantern, the doorway open with the teal mat and bedroll inside. Left to right along the base: a peg, the
**crate** (X braces, iron corner plates, studs) beside the back-left foot, a **stone** in front of it, **barrel A**
(squarish banded staves, iron bands top and bottom, a lid with a bung) with the **ground lantern** at its front-right
(its bail handle up), a second **stone** nearest the camera, the front-left foot with its knot and a peg, and at the far
right **barrel B** behind the front-right foot. Small grass sprigs at a few bases (§3.13).

**r34 (`z_r34.png`).** From the back-left: the closed back triangle at the left, the −X panel to the right, the crate at
the back-left corner, a stone and a peg in front of the panel, barrel A at the far right, four rope hem ties along the
panel's bottom edge, corner knots on all visible feet. It confirms the back is closed and the dressing sits on the −X
side.

**Close-up A, pole junction (`z_cuA.png`).** Square poles with clear chamfers on all four long edges (the chamfers lit
orange), tips cut square with a small chamfer rim, the poles crossing through each other's silhouette; the lashing:
two or three horizontal turns round both poles under the crossing and two diagonal turns making a diamond below, rope
about a quarter of the pole width, twisted.

**Close-up B, canvas attachment (`z_cuB.png`).** The crossing close with an octagonal log bound in horizontally (the
ridge), the canvas over it falling in two slopes, a second log end-on to the right (the other pole's tip), the lantern on
a ring right under the lashing. "Canvas thickness (simple plane)": the canvas edge shows a thin rim. "Canvas wrap
around pole": the canvas edge folds round the front pole.

**Close-up C, underside (`z_cuC.png`).** Inside the doorway looking in and up: the front poles' inner faces as big
diagonals, the roll (cream, two rope bands, spiral ends) and the lantern under it, the canvas ridge seam, the closed back
wall in warm shade, the bedroll on the mat, X-braced crates at the bottom corners outside.

### 1.4 Parts (exploded `z_expl.png`, `z_expl_c.png`)

The exploded cell draws the pieces at roughly hero scale but in loose perspective; the hero governs size and position,
the cells govern shape and colour (§3.9).

| Part (label) | Exploded box (px) | Cell W : H | Tone (median, lit) | Shape |
| --- | --- | --- | --- | --- |
| A-Frame Pole (Left / Right) | (55,855,205,1095) / (590,860,720,1095) | 0.63 / 0.55 (seen obliquely) | `#B25311`, lit `#DF7014`, shade `#7A3510` | an **X of two square chamfered poles**, tips cut square, a lashing under the crossing, a **rope band near each foot** (≈ 1/8 up) |
| Canvas Panel (Left / Right) | (230,880,355,1010) / (405,880,590,1000) | — | `#F9D9B0`, lit `#FEEEC6` | a broad sloped cream sheet hanging from the top; small rope ties at its corners; the left one carries the **door roll** at its lower front corner |
| Top Lashing | (355,820,400,850) | — | `#D89945`, lit `#E8AF55` | the crossing lashing (horizontal turns + diamond) |
| Centre assembly | (330,790,520,1085) | — | interior `#905725` | the front X with the lashing, the lantern(s) (drawn twice, §3.6), the roll, the closed back through the doorway, a **dark box at the back** of the floor (§3.10) |
| Tent Mat (Rolled + Flat) | (290,1040,580,1125) | — | teal `#476867`, lit `#7FA69D`; tan bands `#B67A3F` | a flat teal mat with a lighter teal grid and tan bands; a rolled bedroll, teal outside with a tan band and a tan-and-teal spiral end; L : Ø ≈ 2.2 |
| Storage Crate | (192,1085,296,1185) | 0.95 (front face) | `#7E4224`, lit `#B35F2E`, shade `#4A2414` | a **box with a plank frame** (corner posts, top and bottom rails), **X braces** on its faces, **dark iron corner plates** with studs, a plank lid |
| Barrel | (530,1040,615,1140) | 0.85 | staves `#7F4221`, lit `#B85F29`; hoops `#3F4146`, lit `#4F5B71` | an 8–10-stave bulged barrel, **two blue-grey iron hoops** (top and bottom), a plank lid; grass at its foot |
| Stone (x2) | (540,1135,615,1200), (645,1150,705,1195) | 1.25 / 1.35 | `#BAA1A0`, lit `#DEC6C5`, shade `#958387` | two chunky pale **faceted blocks**, near-cubes with broken corners, the second smaller |
| Peg (x4) | (130,1100,165,1170), (825,1145,860,1200) | 0.50 | `#A34C11`, top `#D57B31` | a **square stake** with a slightly wider **cap block** and a **rope band** below the cap |

- **Pole:** square 0.75 × 0.75 with 0.10 chamfers on the four long edges (8-sided, four broad and four narrow faces),
  tip cut square to the axis with a 0.06 chamfer rim, foot cut horizontal on the ground plane.
- **Lashing (crossing):** rope Ø 0.22: three horizontal turns round both poles just under the crossing (z 8.95–9.30),
  two diagonal turns over the crossing forming the diamond below (to z 8.6), and one turn over the ridge (close-up B);
  4–5-sided twisted tube (M051's `twist=True` idea), never flat collars.
- **Canvas:** a closed slab **0.10 thick** everywhere (outer face, inner face, rim band), never a single-sided plane
  (Roblox culls back faces). Low-poly grid with a slight sag (§2.4).
- **Lantern:** body 0.95 W × 0.95 D × 1.60 H: a square dark-metal base plate (0.95, 0.12 thick), four corner bars (0.09),
  a glass block 0.70 × 0.70 × 0.95 (emissive), a top band, a pyramid or hex-dome roof (1.0 → 0.35 wide, 0.35 tall), a
  ring (r 0.15, tube 0.05) on top.
- **Crate:** 2.30 × 2.30 × 2.20: body box inset 0.06 inside a frame of corner posts (0.26 square), top and bottom rails
  (0.26), one X brace (0.20 × 0.08 planks) on each of the four faces, iron corner plates (0.40 L-plates, 0.04 thick) at
  the eight corners, a plank lid with two plank seams.
- **Barrel:** 2.70 tall, Ø 2.00 at the ends, 2.20 at the bulge; 10 staves (one ring of 10 verts at z 0, 1.35, 2.70 with
  the middle ring at r 1.10); two iron hoops (0.22 tall, 0.05 proud) at z 0.30 and 2.25; a lid inset 0.06 with a
  round bung (Ø 0.35, 0.08 high).
- **Peg:** stake 0.55 square × 1.05 tall from z 0, cap block 0.75 × 0.75 × 0.30 on top (to z 1.35), a rope band
  (Ø 0.12 tube) round the stake at z 0.85.
- **Stones:** hull blocks 1.10 × 1.00 × 0.80 and 0.90 × 0.80 × 0.65, 10–14 verts each, flat bottoms, broken top corners
  (WorldModeling §12.1); never smooth eggs.
- **Mat:** flat 5.0 × 6.6 × 0.22 slab with two tan bands across (0.5 wide, 0.02 proud) and a tan border strip at the
  doorway end; **bedroll** Ø 1.50 × 3.00, 10-sided, its end faces as three concentric rings (the spiral read: teal /
  tan / teal), one tan strap (0.30 wide, 0.04 proud) round its middle.
- **Door roll:** Ø 0.80 × 2.80, 8-sided, its ends as two concentric rings (the rolled spiral), two rope bands (Ø 0.12) at
  0.25 and 0.75 of its length.

### 1.5 How 064 differs from the old kit and its neighbours (binding: the verifier checks these)

| | W10 `AFrameTent` (old kit, exported) | M051 / M052 | **064 A-Frame Tent** |
| --- | --- | --- | --- |
| Size | 11.1 W × 7.7 H × 10.6 D; a character can't stand inside | bridges / boardwalk | **tent 13.7 W × 11.7 L × 11.0 H; walk-in doorway 5.6 wide, apex 8.4** |
| Frame | "thin poles, no lashing" | square posts, rope coils | **two X frames of 0.75 chamfered poles, side by side, tips 1.6 above the crossing, frames leaning out 9.6°, a ridge pole in the crotches** |
| Canvas | "flat canvas, no doorway" | red cloth wraps | **0.10 slab, two sagging side panels with diagonal creases, a closed back, an open doorway with flaps, a roll across the top** |
| Rope | — | twisted tubes, knots | **crossing lashings (turns + diamond), corner knots, upper ties, peg ropes, hem ties; twisted, chunky** |
| Glow | one heat_glow | none | **two lanterns: emissive amber glass (Neon) + one `heat_glow` socket each, tuned to a steady lantern halo** |
| Dressing | crate, barrel, stones in the hero | — | **crate, two barrels, ground lantern, two stones, four pegs, mat and bedroll** |
| Colour | one key per material | wood family by role | **timber orange-brown on the frames, darker weathered wood on the crate and barrels, cream canvas with a deeper hem, beige rope with a deep strand, teal mat, cool dark metal, warm stone** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, ridge along Y). Plan azimuths: 0° = +X, counter-clockwise. Kit
camera azimuths: `front` az 0 (camera on −Y), `side` az 90 (camera on +X, screen right = +Y), `rear` az 180, f34 about
az −45, r34 about az 225.

### 2.1 Stack (binding contact chain; every seat ≤ 0.03 unless stated)

| Piece | Rests on / hangs from | Contact |
| --- | --- | --- |
| Poles (4) | the ground | foot cut flat on z 0.000 (±0.005); the two poles of a frame **touch at the crossing** (gap 0.00–0.02, side by side, §2.2) |
| Ridge pole | the two crotches | rests on the upper arms of both poles at each end (gap ≤ 0.02, sink ≤ 0.03) |
| Crossing lashings (2) | both poles and the ridge | turns hug the poles (inner surface 0.00–0.02 off the pole faces); sink ≤ 0.03 |
| Canvas shell | the ridge pole and the inner poles | inner face of the ridge fold on the ridge top (gap ≤ 0.02); each end panel's inner-pole edge touches its pole's inner face (gap ≤ 0.02) along its length; the outer-pole edge folds out to touch the outer pole (§2.4) |
| Corner knots (4) | a pole and the canvas corner | band hugs the pole; the knot's tail turns wrap the canvas edge (≤ 0.03 into the slab) |
| Upper ties (2, front) | the front poles and the canvas edge | as the corner knots |
| Door roll | the outside of the front flaps | its back touches both flaps (gap 0.00–0.02) either side of the doorway |
| Hanging lantern | the front lashing | its ring hooked through the lowest front turn of the lashing (ring and rope touching, ≤ 0.02) |
| Pegs (4) | the ground | stake bottom on z 0 |
| Peg ropes (4) | a corner knot and a peg band | ends sunk 0.03 into the knot and into the peg's rope band |
| Hem ties (6) | the canvas hem and the ground | the loop's top passes through the hem slab (≤ 0.05 inside it), its bottom touching the ground (z 0.00–0.02) |
| Mat, bedroll | the ground; the mat | mat bottom on z 0; bedroll resting on the mat top (gap ≤ 0.02) |
| Crate, barrels, stones, ground lantern | the ground | bottoms on z 0; each ≥ 0.05 from every other piece unless it touches (no overlap) |

### 2.2 Frames (two) and poles (four)

- **Crossing point** (where the two pole centrelines cross in the front view): (0, ±3.40, 9.40) — this is the frame's
  centre plane at the crossing.
- **Frame lean:** each frame's centre plane leans outward along Y: |y| = 3.40 + 0.17 (9.40 − z) (9.6° from vertical;
  the sheet's poles lean ≈ 12° and the canvas edges ≈ 9°, so this one lean serves both, §3.7).
- **Side by side, not lapped (decision §8.4):** at each end the two poles lie in **parallel planes 0.76 apart** (one
  pole width + 0.01), so they touch at the crossing without a boolean. At **both** ends the pole whose foot is at **+X is
  the outer one** (further from the tent centre): outer plane |y| = frame plane + 0.38, inner plane = frame plane − 0.38.
  - Front frame: outer pole from foot (+6.40, −5.38, 0) through (0, −3.78, 9.40) to its tip; inner pole from (−6.40,
    −4.62, 0) through (0, −3.02, 9.40).
  - Back frame: the mirror in Y: outer (+6.40, +5.38, 0) → (0, +3.78, 9.40); inner (−6.40, +4.62, 0) → (0, +3.02, 9.40).
  - From the front the X reads exactly as the sheet's; from the side the two poles show a sliver apart, as the true side
    cell draws them.
- **Tips:** each pole continues past the crossing to **z 11.0** (tips at x ≈ ±1.09, 2.2 apart, as the front cell's 37
  px), cut square to the axis. Pole length ≈ 13.0 (foot to tip).
- **Feet:** the foot cut horizontal at z 0 (an ellipse ≈ 0.90 along X × 0.76 along Y). Front view feet outer x ±6.85.
- **Pole section:** 0.75 square, 0.10 chamfers (§1.4), one long prism per pole (two rings + cut caps), no subdivisions;
  a ±0.02 random twist of the section along its length is allowed so they read hand-hewn, not machined.

### 2.3 Ridge pole

- 8-sided, Ø 0.55, axis (0, y, 9.75), **y −4.40 … +4.40** (its ends stick out ≈ 0.25 past the outer poles' outer faces,
  as the side cell's stubs; §3.5). It rests in both crotches (the V between the poles' upper arms above the crossing):
  set z so it touches the upper faces of both poles at each end (≈ 9.75; tune by measuring).
- Mostly hidden under the canvas; it shows at both ends between the tips and in close-up B.

### 2.4 Canvas (one shell for the slopes and ridge fold; one back piece; one front piece)

- **Side panels:** from the ridge fold (outer surface apex z 10.13, inner surface on the ridge top ≈ 10.03) down to the
  **hem at x ±5.80, z 0.10**; panel slope ≈ 59.6° (the poles are 55.8°: in the front view the panel edge stays behind
  the pole within its 0.45 half-width from z 1 to z 9, so the canvas doesn't poke out beside the poles).
- **End planes (the canvas ends):** |y| = 2.625 + 0.17 (9.40 − z), i.e. **parallel to the frames and touching the inner
  poles' inner faces** (0.02 gap). The ridge edge spans y ±2.46 (sheet ±2.4) and the hem y ±4.21 (sheet ±4.1).
- **Sag (the sheet's diagonal creases):** each side panel is a 5 × 3 vertex grid in its plane (top edge 3 verts along the
  ridge fold, a middle row at half the slope, the hem row); the middle row's three inner verts pushed **0.18 inward**
  (toward the tent axis) and the hem row's middle vert 0.06 inward; edges straight (they are tied). Flat shading then
  draws the X of creases from the top corners to the middle of the hem, as the true side cell shows. No cloth sim, no
  subdivision.
- **Back piece:** the closed triangle in the back end plane: apex at the ridge fold, base from (−5.80, 4.21, 0.10) to
  (+5.80, 4.21, 0.10); a centre vert pushed 0.10 inward for a gentle sag.
- **Front piece:** the same triangle **minus the doorway**: opening apex (0, ·, 8.40), opening base x ±2.80 at the hem
  → two flaps (each 3.0 wide at the hem) joined by the small closed triangle above the opening. Along each opening edge,
  from the hem to z 5.0, a **turned-back strip** 0.35 wide lying on the outside of the flap (its own 0.06 slab, touching
  the flap, ≤ 0.02 off), the sheet's lighter folded edge.
- **The outer-pole side ("canvas wrap around pole"):** the end piece touches the inner pole directly; on the other
  edge the outer pole stands 0.76 further out. Fold the end piece's last 0.45 along that edge outward (a hinged strip at
  ≈ 60° to the end plane) so its rim meets the outer pole's inner face (gap ≤ 0.02).
- **Joins between canvas shells:** each end piece's sloped edges tuck 0.02–0.03 inside the side panels' end rims (no
  coplanar faces, no gap of daylight). Thickness 0.10 on every piece; rims are real faces.

### 2.5 Doorway, roll and hanging lantern

- **Door opening:** apex z 8.40, base ±2.80 at the hem (z 0.10). Clear width: 4.3 at z 2.0, **2.7 at z 4.4, 1.9 at z
  5.5**, 0.5 at z 7.7.
- **Door roll:** axis along X at **(0, −3.47, 6.40)**, Ø 0.80, x −1.40 … +1.40; its back face touches the front flaps
  (the front end plane is at y −3.07 at z 6.4) on both sides of the opening (the opening is 1.33 wide there, the roll
  2.8 long). Two rope bands at x ±0.70. Its underside at 6.0.
- **Hanging lantern:** body centre **(0, −3.50, 7.70)**, z 6.90 … 8.50, ring to ≈ 8.80, hooked through the lowest front turn
  of the front lashing (at y ≈ −3.48, the front face of the lashing round the outer pole). Its back face is ≥ 0.25 off
  the canvas (front end plane at y −2.98 at z 6.9 and −2.71 at z 8.5). Its bottom clears the roll's top (6.80) by 0.10.
- **Upper ties:** a rope band round each front pole at **z 7.5** wrapping the canvas edge (the sheet's ties at y ≈ 590).

### 2.6 Rope: lashings, corner knots, peg ropes, hem ties

| Piece | Count | Where | Size | Sides × segments |
| --- | --- | --- | --- | --- |
| Crossing lashing | 2 | z 8.6–9.9 round both poles and the ridge (§1.4) | Ø 0.22 | 5 × 10 per turn, 4–5 turns |
| Corner knot | 4 | one per pole at **z 1.6**: a band of two turns round the pole plus a figure-of-eight tail of two loops wrapping the canvas end edge where it meets that pole | Ø 0.20; knot ≈ 1.2 across | 4 × 8 per turn |
| Upper tie | 2 | front poles, z 7.5 | Ø 0.16 | 4 × 8, 2 turns |
| Peg rope | 4 | from each corner knot's outer side down to its peg's band | Ø 0.16, 1.3–2.0 long, slight sag | 4 × 4 |
| Peg band | 4 | round each stake at z 0.85 | Ø 0.12 | 4 × 8 |
| Hem tie | 6 | three per long side at y −2.6, 0, +2.6: a loop through the hem down to the ground | r 0.20, tube Ø 0.14 | 4 × 8 |
| Roll band | 2 | round the door roll | Ø 0.12 | 4 × 8 |

- All rope is **twisted** (each ring rotated half a side per segment, M051's twist), chunky, never flat octagon collars
  or thin wire (M048 / M051 findings).
- **Pole positions at z 1.6:** front outer (+5.31, −5.11), front inner (−5.31, −4.35), back mirrored. The canvas end edge
  at z 1.6 is at x ±4.95 (inside the pole's 0.45 half-width: the knot's band touches pole and canvas).

### 2.7 Interior

- **Mat:** 5.0 (X) × 6.6 (Y) × 0.22, centred (0, +0.30), y −3.00 … +3.60 (inside the canvas ends ±4.21 at the hem); two tan
  bands across at y −1.4 and +1.6, a tan border strip at the doorway end.
- **Bedroll:** axis along X, centre (−0.90, +2.30, 0.97), Ø 1.50 × 3.00 (x −2.40 … +0.60), resting on the mat, one strap.
- Nothing else inside (§3.10). The floor between the doorway and the bedroll stays clear for walking in.

### 2.8 Dressing (positions from the f34 and r34, §3.12)

| Piece | Centre (x, y) | Size | Rot (z) | Notes |
| --- | --- | --- | --- | --- |
| Crate | (−7.40, +2.60) | 2.30 × 2.30 × 2.20 | 12° | beside the −X panel near the back-left foot; clear of the hem (x −5.8) and the back inner pole foot (−6.40, +4.62) by ≥ 0.05 |
| Barrel A | (−7.30, −0.90) | Ø 2.0 / 2.2 × 2.70 | 0° | in front of the −X panel, front half |
| Ground lantern | (−6.50, −2.60) | 0.95 × 0.95 × 1.60 + ring | 20° | on the ground at barrel A's front-right, bail handle up (§3.8) |
| Stone S1 | (−6.40, +0.90) | 1.10 × 1.00 × 0.80 | 25° | between the crate and barrel A |
| Stone S2 | (−7.60, −3.30) | 0.90 × 0.80 × 0.65 | 40° | in front of barrel A, left of the lantern |
| Barrel B | (+7.00, −3.40) | Ø 2.0 / 2.2 × 2.70 | 15° | beside the +X panel near the front, behind the front-right foot as seen from the front |
| Pegs P1–P4 | (±4.90, ±6.20) | 0.75 × 0.75 × 1.35 | 0–10° | just outside each end, each tied to its corner knot |

- **Clearances:** every dressing piece ≥ 0.05 from the canvas hem line (x ±5.80 for |y| ≤ 4.21), the pole feet
  footprints and each other, unless it deliberately touches; nothing intersects anything.

### 2.9 Walkability (binding)

- A 5.5-stud character proxy (a 2 × 1 × 5.5 box, head 1.1 wide above 4.4) **walks from y −8 in through the doorway to the
  mat without touching** canvas, pole, roll or lantern: door clear width ≥ 2.6 at z 4.4 and ≥ 1.8 at z 5.5; roll underside
  ≥ 5.95; lantern bottom ≥ 6.85.
- Inside: canvas clear width ≥ 5.0 at z 5.5; the mat top (0.22) is the only step on the way in.
- The pegs, peg ropes and hem ties are low obstacles round the outside (they collide in the `precise` hero; §7).

### 2.10 Expected extents

- **Tent body:** X −6.85 … +6.85 (feet), Y −5.83 … +5.83 (outer feet; ridge ±4.40), Z 0 … 11.0.
- **Hero with dressing:** X ≈ −8.76 (the crate's rotated corner) … +8.10 (barrel B), Y ≈ −6.58 … +6.58 (pegs), Z 0 … 11.0
  → **about 16.9 × 13.2 × 11.0**; bbox bottom centre ≈ (−0.33, 0, 0) in the build frame.

### 2.11 Origin, pivot and stored points

- Origin at the **bbox bottom centre** (`K.check`); transforms applied. Store `o["m064_offset"]` = build-frame origin →
  object origin, `o["m064_door"]` = the doorway threshold centre on the ground (build (0, −4.21, 0)), and
  `o["m064_inside"]` = the floor centre inside (build (0, 0, 0)) for spawn / NPC spots; re-check all three after the origin
  move.
- Parts: origin at their own bbox bottom centre; the Lantern part also stores `m064_hang` (its ring's top point).

### 2.12 Screen checks (floor hidden; `measure.py` masks; probe and keep the best)

- **front_sheet (0, 3)** (probe e 0–8) — governs: frame-only W : H (feet outer / tip height) 1.25 ± 0.05; tips 2.2 apart;
  crossing at 0.855 H ± 0.02; door apex at 0.76 H ± 0.03, door width at the hem 0.51 H ± 0.04; the roll at 0.58 H, the
  lantern glass centre at 0.70 H ± 0.03; pegs in front of both flaps; the mat and bedroll visible through the door.
- **side_sheet (90, 0)** — governs Y: tent-only W : H 1.06 ± 0.06; canvas ridge length 0.45 H ± 0.04, hem length 0.76 H ±
  0.05; the two poles of each frame a sliver apart; C 67 ± 8, W 29 ± 7; fifths ± 12 of §1.2; three hem ties; the ridge
  ends showing at the tips.
- **f34_sheet (−45, 20)** (probe az −35 … −55 × e 15 / 20 / 25; a longer lens is fine) — governs the overall read and the
  dressing: W : H 1.34 ± 0.10; C 46 ± 8, W 43 ± 8, Y 1.5 ± 1.0, M 1.5 ± 1.0, K 2.6 ± 1.5, S 1.8 ± 1.2; the crate, barrel
  A with the ground lantern, two stones, barrel B, pegs where the f34 has them.
- **r34_sheet (225, 20)**: the closed back, the crate at the back-left corner, hem ties on the −X panel; C 63 ± 8, W 31 ± 8.
- **top (0, 89.9)**: content only (§3.4): the ridge along Y, both X frames, the dressing round the edges.

## 3. View conflicts and resolutions

### 3.1 Sheet number
- **Evidence.** The header says "PAGE 66/132"; INDEX.md row 64 lists `064.png` as "Flintborn A-frame tent study".
- **Resolution.** Our number is 064 (file name, keys `m064_*`). Note the header in the export notes only.

### 3.2 "Side view (right)" is a front three-quarter
- **Evidence.** The cell shows the doorway, roll and lantern facing the camera and the −X panel as a band to the left of
  the front X; a true side view would show the long panel face-on and no doorway.
- **Resolution.** Content only (the dressing at the front-left, the mat through the door). Not scored on W : H.

### 3.3 "Rear view" is the true side elevation
- **Evidence.** It shows a long canvas trapezoid between two pairs of edge-on poles and no doorway and no back triangle;
  a rear view would show the closed back triangle with its X.
- **Resolution.** It governs Y (crossing spacing, lean, canvas lengths, the two-pole sliver, hem ties) and the side
  shares. The closed back is taken from the r34.

### 3.4 The "top" is a stylised square
- **Evidence.** A near-square canvas (136 × 140 px) with crossed stubs at all four corners; a real plan shows each frame
  as one line across its end and a canvas 1.38 × wider than long (front and side cells: hem 1.03 H across vs 0.76 H along).
- **Resolution.** Front and true side govern proportions; the top is content only (the ridge seam, both frames, pegs,
  dressing at the edges).

### 3.5 A ridge pole the parts list doesn't name
- **Evidence.** The exploded parts have no ridge pole. But close-up B binds a horizontal octagonal log into the crossing
  with the canvas draping from it; the side cell shows short horizontal stubs at both tips; the top cell has a centre seam;
  the f34 ridge line is ruler-straight between the frames (an unsupported canvas would sag).
- **Resolution (decision §8.5).** A ridge pole Ø 0.55 from y −4.40 to +4.40, resting in both crotches, mostly under the
  canvas. It is not exported as a part (it isn't labelled); it carries the canvas in the contact chain.

### 3.6 Lantern above the roll (f34, side cell, close-up B) vs over it (front cell, close-up C); two lanterns in the exploded
- **Evidence.** The f34 and the "side" cell hang the lantern directly under the lashing, above the roll; close-up B hangs
  it a short ring below the lashing. The front cell draws it lower, overlapping the roll; close-up C (from inside,
  looking up) puts it under the roll; the exploded centre stacks two lanterns.
- **Resolution.** One hanging lantern, **above the roll** (body z 6.9–8.5), hooked to the front lashing: it matches three
  views, and its bottom clears a 5.5 character's head (the front cell's height would put it at 4.7, in the doorway at head
  height). Close-up C's view from below is consistent with this (from low inside, a lantern 1 stud in front of the roll
  and above it projects below it). The second exploded lantern is the ground lantern.

### 3.7 Pole lean (≈ 12°) vs canvas edge lean (≈ 9°)
- **Evidence.** Side cell: the poles lean ≈ 12° from vertical, the canvas end edges ≈ 9°, with the canvas corners tied to
  the poles by big knots near the feet.
- **Resolution.** One lean, **9.6°**, for both: the canvas end edges then touch the inner poles all the way down (a
  clean contact chain, no 0.6–0.9 gap at the feet), the trapezoid keeps the sheet's ratios (ridge 0.45 H, hem 0.77 H),
  and the corner knots stay where the sheet draws them. Alternative: poles at 12° and canvas at 9°, the gap bridged only
  by the knots (closer to the sheet's angles, more floating risk).

### 3.8 The ground lantern stands raised beside barrel A
- **Evidence.** In the f34 and the "side" cell the ground lantern's base is about 0.4 of the barrel's height above the
  ground, with nothing visible under it.
- **Resolution.** It stands **on the ground** at barrel A's front-right (§2.8), bail handle up: a visible support would be
  invented and a hidden one floats. Alternative (open question): hook it by its bail over barrel A's top rim so it hangs
  against the staves at the drawn height (touching the rim).

### 3.9 Labels and scale in the exploded
- **Evidence.** The "Barrel" leader points at the second stone; the exploded A-frames are drawn obliquely (W : H 0.55–0.63
  against the front cell's 1.25); the exploded parts are near hero scale but in perspective.
- **Resolution.** Shapes and colours from the cells, sizes and angles from the hero (§1.1). Parts are exported at hero
  scale.

### 3.10 A dark box at the back of the floor
- **Evidence.** The exploded centre shows a dark wooden box across the back of the interior; the front cell shows a
  horizontal wooden edge at y ≈ 665 behind the bedroll; close-up C shows a dark horizontal bar low on the back wall. It is
  not in the parts list.
- **Resolution (open question).** Left out: the interior stays clear and the parts list matches. Alternative: a low box
  2.6 × 0.9 × 0.9 against the back canvas (+≈ 40 tris, `wood_dark`).

### 3.11 The interior's deep warm shade
- **Evidence.** The doorway reads `#7B4312` (front) / `#905725` (close-up C): the canvas's inside in shadow.
- **Resolution.** **Lighting, not paint.** The canvas has one key inside and out; the studio and Roblox shadows darken the
  interior. Never colour the inner faces darker by their facing (§5.3). The verifier judges the front's W share knowing the
  studio lights the interior more than the sheet.

### 3.12 Dressing spread vs the front cell
- **Evidence.** The front cell keeps everything inside the pole feet (W : H 1.22 with dressing, 1.25 tent only); the f34
  and r34 put the crate, barrel A and stones outside the −X panel and barrel B outside the +X panel. No two cells place
  the dressing alike (the true side cell shows the crate but no barrel A; close-up C shows crates at both door corners).
- **Resolution (decision §8.10).** The f34 (the most complete read) governs the dressing; the front governs the tent. The
  whole-silhouette front W : H (≈ 1.54) is recorded, not scored.

### 3.13 Grass sprigs
- **Evidence.** Small green sprigs at a few bases (f34, exploded barrel and stones); no green swatch.
- **Resolution.** Left out: ground dressing belongs to the terrain and the foliage models. Record it.

### 3.14 Peg caps: pale (f34, front, r34) vs orange (exploded)
- **Resolution.** Pale end-grain caps (`m064_end_grain`) as the three hero views draw them; the stake body is the darker
  wood.

### 3.15 "Canvas thickness (simple plane)" vs Roblox
- **Resolution.** The callout means a plain flat sheet, no folds or hems modelled in detail. Every canvas piece is a
  closed 0.10 slab: Roblox culls back faces, so a single-sided plane disappears from inside or behind (WorldModeling §5.2
  "leaf thickness is real geometry" applies to cloth too).

### 3.16 "Solid colours, broad flat faces" vs the user's colour rule
- **Resolution.** Keys by role, blended by position (§5.5); broad Tint mottling per piece; never per-triangle confetti.
  The sheet's lit tops, shaded sides, dark interior and blue-grey stone shade are its light.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

1. `pole(foot, through, tip_z)` → one chamfered square prism, square-cut tip, flat foot. Check against close-up A.
2. `frame(end)` → two poles side by side (§2.2) + the crossing lashing + two foot bands (the part has no canvas tails).
   Check against the exploded A-frame and close-up A (X, tips, lashing diamond).
3. `ridge()` → the 8-sided ridge pole (§2.3).
4. `canvas()` → the side-panel shell with the ridge fold, the back piece, the front piece with the doorway, the
   turned-back strips and the fold strips (§2.4). `panel_part()` → one side panel alone for export.
5. `rope_tube(path, r, sides, twist)` → every rope piece (lashing turns, knots, ties, peg ropes, hem ties, bands). Copy
   M051's twisted tube code (committed: import its geometry helpers, never its constants).
6. `lantern()` → the lantern (§1.4); glass on the glow key.
7. `roll()` → the door roll with its bands and spiral ends.
8. `crate()`, `barrel()`, `stone(size, seed)`, `peg()`, `mat()` (flat mat + bedroll).
9. **Hero `CanvasTent`** = 2 frames + ridge + canvas + 4 corner knots + 2 upper ties + roll + hanging lantern + 4 pegs + 4
   peg ropes + 6 hem ties + mat + bedroll + crate + 2 barrels + ground lantern + 2 stones, placed by §2, one object of
   closed shells. Then run the contact, bury, walk and winding reports (§6).
10. **Parts shot** (−20, 15) laid out like the exploded labels: Frame, Panel, Mat, Crate, Barrel, Stone, Peg, Lantern,
    gaps 0.8.
11. **Exploded shot:** from the parts as the sheet arranges them: a frame at each side, the two panels lifted above the
    centre, the assembled front frame with the lantern in the middle, the mat, crate, barrel, stones and pegs below.

Reusable code: M051 / M052 rope and timber helpers (committed: import, don't edit); `m047._Solids`, `shells_report`,
`contact_report`, `bury_report`, m038's `contacts()` (committed). Copy, don't import, from uncommitted builders.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a steep cream A-frame tent between two X frames with tips above the ridge, an open doorway with a
   roll and a glowing lantern, a closed back, knots and pegs at the corners, a teal mat inside, crate / barrels / stones
   round the base.
2. **front_sheet / side_sheet / f34_sheet / r34_sheet / top** per §2.12.
3. **Close-up renders:**
   - `junction_cu` close on the front crossing from the front-left, against close-up A: chamfered square poles, square
     tips, the lashing's horizontal turns and diamond, rope that reads twisted and chunky.
   - `canvas_cu` close on the front crossing from slightly above, against close-up B: the ridge bound in, the canvas
     falling from it with a visible 0.10 rim, the lantern on its ring under the lashing, the canvas fold meeting the
     outer pole.
   - `inside_cu` from (0, −4.6, 1.8) looking at (0, +2, 6.0), against close-up C: the poles' inner faces, the roll and
     lantern above the doorway, the closed back wall, the mat and bedroll; no see-through canvas from inside.
   - `knot_cu` on a corner knot and its peg rope: band on the pole, tail round the canvas edge, rope into the peg band.
   - `door_walk`: the 5.5 proxy (§2.9) standing in the doorway (y −4.2) and on the mat, front and side views; clearances
     printed.
   - `thumb`: the f34 at about 140 px tall: the X frames, the doorway, the lantern glow and the dressing still read.
   - `spin` contact sheet: az 0 / 45 / … / 315 at e 10: from every side the canvas reads solid (no missing back faces, no
     holes at the end joins), nothing floats.
4. **Contact counts** (§6): floating shells 0; buried 0 (stated seats excepted); winding errors 0.
5. **Scale shot:** the 5.5 marker beside the doorway and a second inside on the mat.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Poles (8-sided prism, cut tip with chamfer rim, flat foot) | 4 | 32–40 | 130–160 |
| Ridge pole (8-sided) | 1 | 28 | 28 |
| Canvas: side-panel shell (2 × 5 × 3 grid, ridge fold, rims) | 1 | 110–130 | 110–130 |
| Canvas: back piece / front piece (notch) / turned-back strips / fold strips | 1 / 1 / 2 / 2 | 24 / 50 / 12 / 12 | 122 |
| Crossing lashings (4–5 turns, 5 × 10) | 2 | 200–260 | 400–520 |
| Corner knots (band + figure-of-eight tail, 4 × 8) | 4 | 96–120 | 384–480 |
| Upper ties / roll bands / peg bands | 2 / 2 / 4 | 64 / 64 / 64 | 512 |
| Peg ropes (4 × 4) | 4 | 32 | 128 |
| Hem ties (4 × 8) | 6 | 32–64 | 192–384 |
| Door roll (8-sided, spiral ends) | 1 | 60 | 60 |
| Lanterns | 2 | 130–160 | 260–320 |
| Crate (frame, X braces, corner plates, lid) | 1 | 260–320 | 260–320 |
| Barrels (10 staves, 3 rings, 2 hoops, lid, bung) | 2 | 200–240 | 400–480 |
| Stones (hull, 10–14 verts) | 2 | 16–24 | 32–48 |
| Pegs (stake + cap) | 4 | 24 | 96 |
| Mat (slab + bands) + bedroll (10-sided, ring ends, strap) | 1 + 1 | 60 + 140 | 200 |
| **Hero** | | | **about 3300–3850; aim ≤ 3800; ceiling 4000** |
| Parts: Frame / Panel / Mat / Crate / Barrel / Stone / Peg / Lantern | | | 450–600 / 60 / 200 / 300 / 240 / 24 / 90 / 160 |

- **Over budget?** Cut in this order: hem ties 4 × 8 → 3 × 6 (or 6 → 4 ties); lashing turns 5 → 4 and sides 5 → 4; barrel
  staves 10 → 8; peg bands dropped in favour of the peg rope ending in a knot round the stake; the bedroll to 8 sides.
  **Never** drop a pole chamfer, a lashing, a corner knot, the doorway, the roll, a lantern, the canvas thickness or a peg.

### 4.4 Shape targets (binding; check with `M.audit` and own bmesh code)

- Poles 0.75 ± 0.04 square with visible chamfers; tips at z 11.0 ± 0.3, 2.2 ± 0.25 apart.
- Canvas every piece ≥ 0.09 thick at every rim; no single-sided face anywhere.
- Doorway: apex 8.40 ± 0.30, hem width 5.60 ± 0.40; roll underside ≥ 5.95; lantern bottom ≥ 6.85.
- Ridge canvas length (outer surface) 4.92 ± 0.4; hem length 8.42 ± 0.5.
- Crate 2.30 ± 0.15 square, barrels 2.70 ± 0.15 tall, pegs 1.35 ± 0.15 tall.

### 4.5 Stages 2 and 3

- **Stage 2:**
  - Every shell closed and manifold, **0 bowties** (likely at the knot loops, the turned-back and fold strips, the door
    notch corners, the crate's corner plates).
  - **0 winding errors per shell** (`bmesh.ops.recalc_face_normals` per shell, then `m047.shells_report`); the notched
    front piece and the hand-listed fold strips are where a reversed face slips in (044).
  - No zero-area faces; corners ≥ 3°; triangulate the canvas grid quads at build time (M051 left 104 non-planar quads).
  - Origin at the bbox bottom centre, transforms applied, `m064_offset` / `m064_door` / `m064_inside` re-checked.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box)

| Swatch | Hex (HSV) | Use |
| --- | --- | --- |
| Timber (Primary) | `#AD4B08` (24°, .95, .68) | poles, ridge (`timber`) |
| Canvas Fabric | `#FDE4BE` (36°, .25, .99) | all canvas, the roll (`canvas`) |
| Stone | `#AB988E` (21°, .17, .67) | stones (`stone`; the rendered stones are pinker, §5.2) |
| Rope / Lashing | `#C29A66` (34°, .47, .76) | all rope, mat bands, bedroll strap (`rope`) |
| Tent Mat (Fabric) | `#557E7E` (180°, .33, .49) | mat, bedroll (`mat`) |
| Metal (Lantern) | `#4E4D4F` (270°, .03, .31) | lantern frames, hoops, corner plates (`metal`) |
| Lantern Light (VFX) | radial: centre `#FBBF03` (45°, .99, .98), edge `#E48A05` (36°, .98, .89) | the glass (`glow`) and the VFX colour |

### 5.2 Rendered regions (`samp.py`; median / lit quartile / shade quartile)

| Region | Median | Lit Q | Shade Q |
| --- | --- | --- | --- |
| Canvas, all C: f34 / r34 / front / true side / top | `#FDE4BD` / `#FDE5BC` / `#FBDFB5` / `#FEE4BA` / `#FEE5BC` | `#FEECC5` / `#FEE9C0` / `#FEE7BD` / `#FEE6BC` / `#FEE7BE` | `#DEC1A3` / `#DAB898` / `#DCBD96` / `#FADAB1` / `#FADDB6` |
| Canvas side panel (true side) / f34 −X panel / r34 −X panel | `#FEE5BB` (38°, .26, 1.0) / `#FDE6BF` / `#FEE8C0` | `#FEE6BC` / `#FEEBC4` / `#FEE6BD` | `#FCDEB4` / `#E0C3A6` / `#FDE6BD` |
| Canvas back end (r34, in shade) | `#DAB999` (30°, .30, .85) | `#E5C7A7` | `#CFAE8F` |
| Door flaps (front) / door roll (cuC) | `#FDE1B7` / `#E0B991` | `#FEE5BC` / `#ECC9A1` | `#F4CFA1` / `#D5AD84` |
| Interior shade: front / cuC | `#7B4312` (28°, .85, .48) / `#905725` | `#8F4C11` / `#DFB990` | `#673913` / `#73441E` |
| Poles: exploded / cuA / cuB / front / true side | `#B25311` (25°, .90, .70) / `#A75420` / `#9D4918` / `#86441C` / `#834620` | `#DF7014` / `#D77C31` / `#F3801D` / `#A75526` / `#C3662A` | `#7A3510` / `#662B0D` / `#70310A` / `#4D2209` / `#411A09` |
| Crate (exploded / f34) / barrel staves | `#7E4224` (20°, .71, .49) / `#7F421F` / `#7F4221` | `#B35F2E` / `#B15F2A` / `#B85F29` | `#4A2414` / `#3E1F0F` / `#422114` |
| Peg stake (exploded) / peg cap (f34 lit, shade) | `#A34C11` / `#D1AF9B`, `#7E5849` | `#DF781B` | `#7E330B` |
| Rope: f34 / true side / cuA / cuB / exploded lashing | `#C08C57` (30°, .55, .75) / `#C79968` / `#D08C41` / `#B08952` / `#D89945` | `#E0A972` / `#DBA875` / `#DF9B4B` / `#E3A046` / `#E8AF55` | `#9F6832` / `#A27753` / `#BE7D3A` / `#9B6E4A` / `#AF7337` |
| Mat flat / bedroll / cuC | `#476867` (178°, .32, .41) / `#446661` / `#385A56` | `#7FA69D` / `#7CA196` / `#568079` | `#395856` / `#314D48` / `#2B4744` |
| Mat tan bands (exploded) | `#B67A3F` (30°, .65, .71) | `#DA974C` | `#9B6633` |
| Metal: lantern cuB / cuC / barrel hoops | `#362B2A` (5°, .22, .21) / `#3E3435` / `#3F4146` (223°, .10, .27) | `#493A38` / `#453C3B` / `#4F5B71` | `#251E1D` / `#342B2A` / `#282827` |
| Lantern glass: cuB / cuC / front | `#FBB708` (43°, .97, .98) / `#F9B707` / `#F7A610` | `#FFC108` / `#FED106` / `#FEB512` | `#F09703` / `#E89508` / `#DF880D` |
| Stones: exploded / f34 all S | `#BAA1A0` (2°, .14, .73) / `#887E89` | `#DEC6C5` / `#C3AFB0` | `#958387` / `#6F6166` |
| Cast shadow (not modelled) | `#E9D5D3`–`#F8F1E7` | | |

### 5.3 How the colour works

- **Frames:** `timber` on all four poles and the ridge; the **lowest 0.8 of each pole** (the ground end) blended one step
  toward `wood_dark` by height (weathered feet; the sheet's feet read deeper); tips and chamfers keep `timber` (their
  lit look is the light). Per-pole Tint 0.04 with a 0.02 lengthwise variation (grain).
- **Canvas:** `canvas` on every canvas face, **inside and outside alike**; the **hem band** (the lowest 0.35 of each
  piece, by height in the piece) blended three steps to `canvas_deep`; a 0.3 band round each knot and tie contact, by
  distance, one step to `canvas_deep` (rope rub); the turned-back strips stay `canvas` (their lighter look on the sheet is
  their angle to the light). The door roll `canvas` with its spiral end rings alternating `canvas` / `canvas_deep`
  by ring (position). Broad Tint 0.03 per panel facet region so the panels aren't one flat cream.
- **Rope:** `rope` body; one strand of every four (by strand index along the twist) `rope_deep`, so the twist reads; the
  knot tails' inner turns (those hidden between pole and canvas, by position) `rope_deep`. Tint 0.03 per piece.
- **Crate and barrels:** `wood_dark` body, per-plank / per-stave Tint 0.05 (the sheet's plank-by-plank value steps); the
  crate's frame and X braces one step toward `timber` (they are proud boards that the sheet draws a little warmer); iron
  plates and hoops `metal`; the barrel lid `wood_dark` one step toward `timber`.
- **Pegs:** stake `wood_dark`, cap `end_grain`, band `rope`.
- **Lanterns:** frame, plates, bars, roof, ring `metal`; glass `glow` (Neon).
- **Mat and bedroll:** `mat` body; bands, border strip and strap `rope`; the bedroll's end rings `mat` / `rope` / `mat`
  from the outside in.
- **Stones:** `stone` body, the lowest 25 % blended one step to `stone_deep` by height; Tint 0.05 broad.
- **Never by facing.** No face gets a colour because of which way it points: the interior's dark canvas, the shaded
  back end (`#DAB999`), the dark sides of the poles and the blue-grey stone shade are all the light.
- **Hues stay apart:** timber 22–27° (s 0.80–0.92); wood_dark 18–23° (v ≤ 0.55); canvas 34–40° (s 0.22–0.28, v ≥ 0.93
  rendered); canvas_deep 30–35°; rope 29–35° (s 0.45–0.62); rope_deep 27–31°; end_grain 20–30° (s 0.20–0.32); mat 170–185°;
  metal s ≤ 0.12, v 0.25–0.33; stone 10–25°, R > G > B; glow 38–45°.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians where the sheet gives them, swatches where it doesn't. `K.sample` kinds:
`"brown"` for timber, wood_dark, rope, rope_deep, end_grain; `"stone"` for canvas, canvas_deep, stone, stone_deep, metal;
`"vivid"` for glow; `"green"` for mat (check with `M.raw_sample` on the swatches too). Start the timber from M051's
calibrated `#894315` (its target `#9D4D18` is next to ours).

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m064_timber` | `#A3501A` ± 12 (poles: exploded `#B25311`, cuA `#A75420`, cuB `#9D4918`; swatch `#AD4B08`) | 22–27°, 0.80–0.92 | poles, ridge | rough 0.85 |
| `m064_wood_dark` | `#844526` ± 12 (crate `#7E4224` / `#7F421F`, barrel `#7F4221`) | 18–23°, 0.68–0.78, v ≤ 0.55 | crate, barrels, peg stakes, pole feet (blend) | rough 0.9 |
| `m064_end_grain` | `#C7A690` ± 15 (f34 peg caps, lit `#D1AF9B`) | 20–30°, 0.20–0.32 | peg caps | rough 0.9 |
| `m064_canvas` | side-panel median `#FDE4BC` ± 10 (true side `#FEE5BB`, f34 `#FDE6BF`; swatch `#FDE4BE`) | 34–40°, 0.22–0.28 | all canvas, roll | rough 0.95, low spec |
| `m064_canvas_deep` | `#E6C8A2` ± 12 (between the shade quartiles `#DEC1A3` / `#DAB898`) | 30–35°, 0.28–0.34 | hem band, rub bands, roll spiral (blend) | rough 0.95 |
| `m064_rope` | `#C8925A` ± 12 (f34 `#C08C57`, true side `#C79968`, cuA `#D08C41`; swatch `#C29A66`) | 29–35°, 0.45–0.62 | all rope, mat bands, strap | rough 0.95 |
| `m064_rope_deep` | `#A06C3A` ± 12 (rope shade quartiles `#9F6832` / `#A16C39`) | 27–31°, 0.60–0.70 | one strand in four, hidden knot turns | rough 0.95 |
| `m064_mat` | `#4F7674` ± 12 (flat `#476867`, bedroll `#446661`; swatch `#557E7E`) | 170–185°, 0.28–0.36 | mat, bedroll | rough 0.95 |
| `m064_metal` | `#48474B` ± 10 (swatch `#4E4D4F`; lantern `#362B2A`, hoops `#3F4146`) | s ≤ 0.12, v 0.25–0.33 | lantern frames, hoops, corner plates, bung | rough 0.55, metal 0.4 |
| `m064_glow` | `#F8B00A` (glass `#F9B707` / `#FBB708`; swatch centre `#FBBF03`), **emission 1.0** | 38–45°, ≥ 0.94 | lantern glass (Neon) | — |
| `m064_stone` | `#B4A199` ± 12 (between swatch `#AB988E` and render `#BAA1A0`) | 10–25°, 0.12–0.18, R > G > B | stones | rough 0.92 |
| `m064_stone_deep` | `#978884` ± 12 | 10–25°, 0.10–0.16 | stone feet (blend) | rough 0.92 |

**Calibration warnings:**
- **The canvas is cream, never yellow and never white** (the W10 verifier failed `#E3CFA0` as yellow). On the side render
  the panel median within 10 of `#FEE5BB`, saturation 0.22–0.30.
- **The timber is warm orange-brown, not red and not flat orange** (W08 "slightly red" / "flat orange"): hue ≥ 22°; the
  poles must read clearly lighter and more orange than the crate and barrels.
- **Rope is warm beige, not gold** (M048's gold excess): rope_deep on one strand in four, not more gold.
- **Metal is a cool dark grey, not black** (v ≥ 0.25 rendered); no rust colour.
- **Stone is warm pale grey, R > G > B, never lavender** (059 ruling; the sheet's purple `#887E89` is shade).
- **The interior stays the canvas key** (§3.11); if the studio render's doorway reads too pale, that is the studio light,
  not a reason to paint.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Canvas:** by height within each piece (hem band); by distance to each rope contact (rub band); the roll's end rings
  by radius.
- **Poles:** by height (feet → body), 3 steps over z 0–0.8.
- **Crate:** frame boards vs panels by part role; plates hard.
- **Stones:** by height in the stone.
- **Hard edges only** where materials meet: canvas | rope, rope | timber, metal | glass, metal | wood, mat | rope band.

### 5.6 Texture (Tint) and finish
- **Tint:** canvas 0.03 per facet region (broad, never per triangle); poles 0.04 per pole + 0.02 grain; crate planks and
  barrel staves 0.05 each; rope 0.03 per piece; mat 0.03; stones 0.05.
- **Finish:** everything matte (wood 0.85–0.9, canvas and rope 0.95), metal rough 0.55 / metal 0.4, glass emissive (no
  roughness concern); no emission anywhere but the glass.

### 5.7 Re-measure (final renders against the sheet, same masks)
- **Canvas:** side-render C median within 10 of `#FEE5BB`; f34 C median within 12 of `#FDE4BD`.
- **Timber:** f34 W median within 15 of `#834411` (shaded sheet median), parts-shot pole median within 12 of `#B25311`.
- **Glow:** Y share on the f34 1.5 ± 1.0; glass median within 12 of `#F9B707`.
- **Shares** per §2.12.

## 6. Joins and contact (no floating dressing, no buried dressing)

- **Shells:** each pole, the ridge, the canvas side-panel shell, back piece, front piece, each turned-back and fold strip,
  each lashing turn set, knot, tie, rope, peg (stake + cap), the roll, each lantern piece, crate parts, barrel parts,
  stones, mat, bedroll: closed shells, all in one hero object.
- **Chain to the ground:** poles → ground; ridge → poles; lashings → poles; canvas → ridge and inner poles (and outer
  poles by the fold strips); knots and ties → poles and canvas; roll → front flaps; hanging lantern → lashing; peg ropes →
  knots and pegs; pegs → ground; hem ties → hem and ground; mat → ground; bedroll → mat; crate, barrels, stones, ground
  lantern → ground; their bands, plates and lids → their bodies.
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**. A shell floats if its nearest distance
  to every other shell and the ground is > 0.03, or if it doesn't chain to the ground. The new risks: the canvas end edges
  on the outer-pole side (the fold strips must reach the pole), the roll (both ends on the flaps), the hanging lantern's
  ring, the turned-back strips.
- **Buried shells:** nothing more than 0.05 inside anything beyond its stated seat (lashing and knot turns ≤ 0.03 into the
  poles, hem tie loops ≤ 0.05 through the hem, rope ends 0.03 into knots and peg bands). Ray parity against the poles,
  ridge, crate and barrels as solids after the final placement step (`m047._Solids`).
- **No intersections between big pieces:** the canvas never passes through a pole (end planes 0.02 inside the inner
  poles); dressing never touches the canvas or a pole foot (≥ 0.05) unless it deliberately rests on it.
- **Walk report:** the §2.9 proxy path, minimum clearance printed (≥ 0.05 everywhere along it).
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.
- **Winding:** 0 errors per shell, checked with a parity ray test, not only the signed volume (044's wedge back face).
- **Parts:** each exported part self-contained (the Frame's lashing hugging its poles; the Lantern's pieces chained).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** two lanterns with bright amber-yellow glass (the hanging one at the door, the ground one by
barrel A) and a palette swatch for the lantern light, noted as a separate effect, not baked. No fire, smoke, dust or
sparkle. The cast shadows are the illustration's.

- **Stage 5 (lighting):**
  - The glass of both lanterns on `m064_glow` with **emission 1.0** (the exporter's Neon threshold; it exports as a Neon
    glow piece). Use m009's `_glow_mats` preview so the Blender render shows the glass as Roblox Neon will.
  - **No light painted on the canvas** (no glow patch round the lantern): the light comes from the sockets.
  - Studio notes (Requires Manual Validation): the canvas stays cream in daylight and warm-lit at night from the
    lantern; the interior reads dark from outside by shadow, not by paint; the timber reads orange-brown, the crate and
    barrels a step darker.
- **Stage 6 (VFX):** one **`heat_glow`** socket at each lantern's glass centre (no lantern kind exists in `lib/vfx.py`;
  W10 used `heat_glow` on its lanterns), with overrides so it reads as a steady lantern halo, not a furnace shimmer:
  - `emitters=[{"name": "Halo", "texture": "glow_soft", "color": ["#FFC23A", "#FF9A1E"], "size": [1.3, 1.5],
    "transparency": [0.65, 1.0], "lifetime": [1.0, 1.5], "rate": 2, "speed": [0, 0.05], "spread": 0,
    "light_emission": 1.0}]`;
  - `light={"color": "#FFB347", "brightness": 1.0, "range": 12, "flicker": True}` on the hanging lantern, range 8 on the
    ground lantern.
  - Sockets: hanging lantern (0, −3.50, 7.70), ground lantern (−6.50, −2.60, 0.75) in the build frame (passed through
    `M.mk`'s `fx=` list, which shifts them with the origin). Check the export STATS line reports **2 sockets** on the
    hero and 1 on the Lantern part.
- **Collision (decision §8.11):**
  - **Hero `precise`** (PreciseConvexDecomposition): the doorway and interior must stay open, the canvas and poles solid,
    the dressing solid. **Requires Manual Validation in Studio:** a default character walks in through the doorway and
    stands on the mat without snagging; if the decomposition fills the doorway, the fallback is hero `none` plus Studio
    colliders (two thin slope parts for the canvas, a back plate, the four poles as boxes, the crate and barrels as
    boxes).
  - Parts: `CanvasTentFrame` `precise` (a lone X shouldn't fill its triangle); `CanvasTentPanel` `hull`; `CanvasTentCrate`
    `box`; `CanvasTentBarrel` `hull`; `CanvasTentStone` `hull`; `CanvasTentPeg` `none`; `CanvasTentMat` `none` (flat; no
    snag at the doorway); `CanvasTentLantern` `none`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched all 2467 names in `art/roblox/kit/**/manifest.json` (`man.py`), the builders and the
repo text (`git grep`) for Tent, Canvas, Camp, Ridge, Lantern, Crate, Barrel, Peg, Bedroll, Mat, Lashing, Pole, Frame,
Shelter and the candidates:
- **W10:** `AFrameTent`, `AFrameTentCanvasLeft`, `AFrameTentCanvasRight`, `AFrameTentClosed`, `AFrameTentFrameEnd`,
  `AFrameTentMat`, `AFrameTentPeg`, `AFrameTentRidgePole`, `AFrameTentRolledDoorway`, `AFrameTentTornWorn` (and their
  `VFX_…heat_glow_1` sockets); `CampAwning*` (9 names incl. `CampAwningPeg`, `…RidgePole`, `…CanvasCanopy`);
  `RuinLeanTo*` (`…CanvasCanopy`, `…Peg`, `…BedMat`); `TimberHut*`. **Other:** `FortWorkshopCanvasRoof`,
  `GuardLodgeCanvasRoof`, `WatchtowerCanvasRoof`, `FireAndLightLanternPost`, `FortWorkshopLanternHook`,
  `StorageOpenCrate`, `StorageSquareCrate`, `StorageBarrelStave`, `DailyItemsRolledMat`, `RopeBridgePegBlock`.
- **`CanvasTent` (and every `CanvasTent…` part name below) and `m064` occur nowhere** in the manifests, builders or repo
  text (the only `m064` hits are random bytes inside two PNGs). No owned name is a substring of them; `AFrameTentCanvas…`
  contains "TentCanvas", not "CanvasTent". Also free: `LashedTent`, `RidgeTent`, `PoleTent`, `CampTent`.

| Object | Part | Why |
| --- | --- | --- |
| `CanvasTent` | hero: 2 frames, ridge, canvas, knots, ties, roll, 2 lanterns, pegs, ropes, hem ties, mat, bedroll, crate, 2 barrels, 2 stones | W10 owns `AFrameTent*` |
| `CanvasTentFrame` | "A-Frame Pole (Left / Right)": one X of two side-by-side poles with its crossing lashing ("Top Lashing") and foot bands; used twice | the labels; the lashing folded in (§8 decision 6) |
| `CanvasTentPanel` | "Canvas Panel (Left / Right)": one sloped side panel with its sag; the other side is the same mesh turned 180° about Z | the labels; the panels are symmetric front-to-back |
| `CanvasTentMat` | "Tent Mat (Rolled + Flat)" | the label |
| `CanvasTentCrate` | "Storage Crate" | the label |
| `CanvasTentBarrel` | "Barrel" | the label |
| `CanvasTentStone` | "Stone (x2)": the larger stone (the smaller is a scaled copy in Studio) | the label |
| `CanvasTentPeg` | "Peg (x4)": stake, cap, band | the label |
| `CanvasTentLantern` | the lantern (unlabelled but in the palette and every view), with its `heat_glow` socket | reused twice; useful on its own in camps |

- Palette keys `m064_*` (§5.4). Collection `Kit/M064 A-Frame Tent`. Sockets: 2 × `heat_glow` on the hero, 1 on the
  Lantern part. Stored points `m064_offset`, `m064_door`, `m064_inside` on the hero, `m064_hang` on the Lantern.

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **tips 11.0, crossing 9.4, canvas ridge 10.1, feet ±6.4 across; tent 13.7 × 11.7 × 11.0; hero with
   dressing ≈ 16.9 × 13.2 × 11.0** (recommended: the dressing's real-world proportions and an upright walk-in doorway).
   Alternatives: T 10.0 (door 1.5 wide at head height, lantern at 6.3: tight) or T 12.0 (the props read small).
2. **Build frame (§1.1):** **doorway at −Y, ridge along Y, symmetric about x 0 except the pole order and the dressing;
   origin at the bbox bottom centre with the offset stored** (recommended).
3. **What the hero includes (§3.12, §3.13):** **the tent plus the sheet's dressing (crate, two barrels, ground lantern,
   two stones, four pegs, mat, bedroll) placed as the f34; no grass, no back-wall box** (recommended). Alternative: a
   bare tent hero (frames, canvas, ropes, pegs, mat) with the dressing only as parts (front W : H then matches the sheet's
   1.22; the f34 loses its read).
4. **Frames (§2.2):** **two X frames of 0.75 chamfered square poles, the two poles of a frame side by side (0.76 apart,
   touching at the crossing, no boolean), the +X-foot pole outer at both ends; frames leaning out 9.6°; tips 1.6 above
   the crossing** (recommended: robust, and the side cell draws the two poles a sliver apart). Alternative: lapped poles
   in one plane, unioned per frame (close-up A's look; boolean risk).
5. **Ridge pole (§3.5):** **an 8-sided Ø 0.55 ridge from y −4.4 to +4.4 in both crotches, under the canvas; not a part**
   (recommended).
6. **Canvas (§2.4, §3.7, §3.15):** **closed 0.10 slabs everywhere; side panels on a 5 × 3 grid with the centre row sunk
   0.18 (the diagonal creases); end planes parallel to the frames touching the inner poles, the outer-pole edge folded
   to meet the outer pole; a closed back; the front with a doorway (apex 8.4, 5.6 wide) and turned-back strips; the
   crossing lashing folded into the Frame part** (recommended). Alternative: export a separate `CanvasTentLashing` part.
7. **Rope (§2.6):** **twisted tubes everywhere; crossing lashings of 4–5 turns with the diamond; a corner knot per pole at
   z 1.6 tying the canvas; upper ties on the front poles; peg ropes; six hem ties** (recommended).
8. **Doorway, roll, lantern (§2.5, §3.6):** **roll at z 6.4 across the doorway touching the flaps; the hanging lantern
   above it (6.9–8.5) on the front lashing** (recommended). Alternative: the front cell's lower lantern (blocks the head:
   not recommended).
9. **Ground lantern (§3.8):** **standing on the ground beside barrel A** (recommended). Alternative: hooked over barrel A's
   rim at the drawn height.
10. **Dressing layout (§2.8, §3.12):** **as the f34: crate back-left, barrel A + ground lantern + two stones on the −X side,
    barrel B front-right, pegs at the four corners; front whole-silhouette W : H recorded, not scored** (recommended).
11. **Collision (§7):** **hero `precise` with a Studio walk-in check (fallback `none` + Studio colliders); Frame `precise`,
    Panel `hull`, Crate `box`, Barrel `hull`, Stone `hull`, Peg / Mat / Lantern `none`** (recommended).
12. **Comparison cameras (§2.12):** **`front_sheet (0, 3)` and `side_sheet (90, 0)` govern the tent; `f34_sheet (−45, 20)`
    (probe az −35 … −55, e 15–25) governs the read and dressing; `r34_sheet (225, 20)`; `top` content only; close-ups
    `junction_cu`, `canvas_cu`, `inside_cu`, `knot_cu`, `door_walk`, `thumb`, `spin`; parts and exploded shots; scale shot.
    Floor hidden in every `*_sheet` render** (recommended).
13. **VFX (§7):** **emissive Neon glass on both lanterns and a `heat_glow` socket on each, overridden to a steady halo
    (rate 2, no drift) and a warm PointLight (range 12 / 8)** (recommended). Alternative: light only (emitters `[]`).
14. **Exports (§8 table):** **the hero plus eight parts: Frame, Panel, Mat, Crate, Barrel, Stone, Peg, Lantern** (recommended).
    Alternatives: separate `…PanelLeft` / `…PanelRight`, a `…Lashing` part, a `…StoneSmall`.
15. **Colour (§5):** **timber `#A3501A` on the frames, `#844526` on the crate, barrels and peg stakes, cream canvas
    `#FDE4BC` with a `#E6C8A2` hem band, rope `#C8925A` with a `#A06C3A` strand, teal mat `#4F7674`, cool metal `#48474B`,
    Neon glass `#F8B00A`, stone `#B4A199`, pale peg caps `#C7A690`; by role and position, never by facing; the interior
    is lighting** (recommended).
16. **Budget (§4.3):** **full asset: 4000 ceiling, plan 3300–3850; parts under 1000; cut hem ties, lashing turns and barrel
    staves first** (recommended).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **The old tent's failures (W10 / MODEL_PROGRESS row 80: "thin poles, no lashing; flat canvas, no doorway").** Poles
   0.75 with chamfers, fat lashings at both crossings, a sagging canvas with creases, a real walk-in doorway.
2. **Single-sided canvas (Roblox culls back faces).** Every canvas piece a closed 0.10 slab; `inside_cu` and the spin
   prove it from inside and behind.
3. **A doorway a character can't use.** Door ≥ 1.8 wide at z 5.5, roll ≥ 5.95, lantern ≥ 6.85; the `door_walk` proxy
   passes; the Studio walk-in check is recorded as Requires Manual Validation.
4. **Floating or buried pieces** (STAGES; 035 / 036 round 1; 046). The canvas touches the ridge and the poles, the roll
   touches the flaps, the lantern ring the lashing, the peg ropes their knots and pegs; nothing more than its stated seat
   inside anything. Count: floating 0, buried 0.
5. **Canvas through the poles, or dressing through the canvas.** End planes 0.02 inside the inner poles; every dressing
   piece ≥ 0.05 off the hem line and the pole feet.
6. **Rope that reads as flat collars or thin outlines** (M048 finding 1; M051 finding 1). Twisted tubes, Ø 0.20–0.22 on
   lashings and knots, the lashing's diamond turns visible in `junction_cu`.
7. **Rope too golden** (M048: f34 Y +2.7). Beige rope with one deep strand in four; Y on the f34 comes from the glass only.
8. **Yellow canvas** (W10 verifier: `#E3CFA0`). Cream `#FDE4BC` on the side render, s 0.22–0.30.
9. **Red or flat-orange wood** (W08). Timber hue ≥ 22°, poles clearly lighter than the crate and barrels; per-pole and
   per-plank Tint so nothing is one flat colour.
10. **Colour by facing** (042 ruling; 054 m9). The interior, the shaded back end, the dark pole sides and the blue-grey
    stone shade are light. `K.check` facing correlation < 0.5 per material.
11. **Hard colour bands** (M051 finding 5; M052 finding 3). The hem band, pole feet and stone feet blend over three
    steps; no stripe at a band edge.
12. **Blown-out highlights** (M052 finding 4). The canvas must not clip to white on the lit panel: calibrate so the side
    render's lit quartile stays ≤ v 1.0 with s ≥ 0.20.
13. **Egg stones** (M034 / M037). Faceted pale blocks with broken corners, flat bottoms.
14. **Winding and non-planar quads** (044; M051 finding 8). 0 winding errors per shell (the notched front piece, fold and
    turned-back strips, crate plates); triangulate the canvas grid at build time.
15. **Proportions from the stylised cells** (§3.2–§3.4). Front and true side set the tent; the "side (right)" and top
    cells are content only; the f34 sets the dressing.
16. **Names and scope.**
    - No `AFrameTent*`, `CampAwning*`, `RuinLeanTo*`, `TimberHut*`, `Storage*` names.
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit the frozen shared helpers (`kit_models.py`, `kit_mcp.py`, `build_kit.py`, `lib/vfx.py`) or other models'
      builders; import from the committed ones (`m047`, `m051`, `m052`, `m038`); don't touch other models' collections.

## Decisions (main session, 2026-10-31)
All 16 recommendations are accepted. The open questions are ruled as follows:
1. **Size.** The tent is 13.7 × 11.7 × 11.0, and about 16.9 × 13.2 × 11.0 with dressing. A character walks in upright through the doorway; the roll and the hanging lantern sit above head height.
2. **Build frame.** As recommended, storing `m064_offset`, `m064_door` and `m064_inside`.
3. **Hero.** The tent plus the sheet's dressing, placed as in the front three-quarter view. The front cell is scored on the tent alone. **No back-wall box.**
4. **Frames.** Chamfered square poles side by side, touching at the crossing, with no booleans.
   - **One shared lean of 9.6°** for the poles and the canvas, so the canvas sits on the poles and doesn't float off them.
5. **Ridge pole.** In the hero, resting in both crotches. Not a part.
6. **Canvas.**
   - **Closed slabs everywhere, never single-sided planes.**
   - The sag creases come from geometry, not paint.
   - The canvas touches its poles within 0.03, and none of it is buried more than 0.05 in a pole.
7. **Rope.** Twisted tubes. Every rope touches what it ties at both ends; peg ropes run from their peg to the canvas or pole.
8. **Doorway.** As recommended.
9. **Ground lantern.** On the ground beside barrel A.
10. **Dressing layout.** As in the front three-quarter view.
11. **Collision.** As recommended.
    - The hero walk-in is marked **Requires Manual Validation** in Studio, alongside 052's stairs.
    - If precise collision fills the doorway, use the fallback: `none` plus Studio colliders.
12. **Cameras.** As recommended, including `door_walk` and the eight-azimuth spin.
13. **VFX.** Emissive Neon glass (emission at least 1.0) on both lanterns, each with a `heat_glow` socket overridden to a steady warm halo.
14. **Exports.** Hero `CanvasTent` plus eight parts; keys `m064_*`. Never `AFrameTent*`.
15. **Colour.**
    - Use the colours as listed, by role and position, **never by facing**.
    - The dark interior comes from lighting, not paint.
    - Stone and canvas stay warm, never lavender or grey-blue.
16. **Budget.** Full asset: ceiling 4000 (plan 3300–3850), every part under 1000, with the cut order as listed.
