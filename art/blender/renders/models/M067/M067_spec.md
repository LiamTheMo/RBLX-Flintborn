# 067 Table and Seating — spec

Reference: `art/blender/assets/references/067.png` (1024 × 1536 px). INDEX.md row 67: "Flintborn Table and Seating Study".
The sheet's header reads **"PAGE 69/132"** (top right), title **"TABLE AND SEATING"**, subtitle "PRIMITIVE FURNITURE /
TABLE, BENCHES AND STOOL", footer "FLINTBORN — INDIVIDUAL MODEL STUDY" (our number is INDEX's 067, §3.1).
Builder: `art/blender/kit/mcp/m067.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows no glow, light or effect** (§7). The
subject is **one rugged plank table set**: a **thick four-plank table top** on **two A-frame trestles** (cleat, two
splayed legs, a low tie, a diagonal brace), a **crossbar** running under the top between the trestles with **through
tenons** that poke out past them, **two knee braces** from the crossbar down to the trestles, **two long two-plank
benches** either side of the table on splayed leg frames, and **one square three-plank stool** off the table's left end.
Everything is one warm orange timber with **dark square bolt heads**.

Sheet text (paraphrased):
- **Title block:** a rugged, hand-made wooden table set for settlements and camps; sturdy and functional, built from thick
  planks and simple joinery.
- **"FRONT THREE-QUARTER VIEW"** and **"REAR THREE-QUARTER VIEW"**: the assembled set. Unlike 066 and 052, the second is a
  genuine rear view (the same set turned 180°, §3.3).
- **"ORTHOGRAPHIC VIEWS (ASSEMBLED)"**: "FRONT", "SIDE (RIGHT)", "REAR", "TOP". The front and rear draw only the table and
  one bench; the side draws the table end and a stool-like piece where the far bench stands (§3.5); the top draws the
  stool at the other end of the table (§3.4).
- **"EXPLODED CONSTRUCTION"**, labels: "Table Top (Planks)", "Leg / Trestle", "Crossbar", "Stool", "Bench Seat
  (Planks)". Unlabelled: a second trestle, small square peg blocks flying out of the trestles (one with a red arrow), a
  small L-shaped block near the bench, a square post at the crossbar's right end, grey drop arrows.
- **"CONSTRUCTION CLOSE-UPS"**:
  - **"A LEG AND CROSSBAR JOIN"**: the crossbar's end with a tenon pin enters the trestle's head under a projecting cleat
    end that carries a dark square bolt; a square wooden peg drops out (red dashed arrow). Inset "SIDE VIEW (JOINT
    SECTION)": a tenon passing through an upright, locked by a peg.
  - **"B TABLE TOP PLANK DETAIL"**: three thick top planks with dark gaps and soft bevelled edges over a lower member whose
    end face carries a dark square bolt. Inset "PLANK THICKNESS (SECTION)": a plank section with small V notches on its top
    edges, stepping down onto a thicker member under one end.
  - **"C UNDERSIDE VIEW"**: from below, the top's planks (all along the length), a trestle at each end (cleat, legs), the
    crossbar between them with its tenons and square pegs poking out beyond both trestles.
- **"MATERIAL PALETTE (REFERENCE)"**: five unlabelled swatches (orange-brown, light orange, warm grey, red, cream) and a
  close-up render of a bevelled plank corner with a dark square bolt.
- **"MODELING NOTES"** (paraphrased): simple chunky planks with broad flat-shaded faces; separate planks on the top and
  the bench seats so the gaps stay clean; legs are simple A-frame trestles with a diagonal brace and a crossbar; square
  wooden pegs and bolts are separate parts; one plank thickness and one edge bevel on every piece; low poly, clean
  readable forms, no fine surface detail or texture noise; match the Flintborn proportions, colour range and silhouette.
- **Game context and the old kit:**
  - **W11 row 1 `TableAndSeating`** (`art/blender/scripts/kit/W11/table_seating.py`; manifest
    `art/roblox/kit/W11/manifest.json`; goals `art/blender/renders/kit/W11/table_seating_goals.md`; compare
    `art/blender/renders/kit/W11/table_seating_compare.png`) is the old kit's version of this set. Exported hero **7.0 W ×
    3.1 H × 7.7 D, 876 tris, `Box`**; parts `TableAndSeatingTableTop` (7.0 × 0.35 × 3.14, 176 tris),
    `…Trestle` (0.8 × 2.7 × 3.45, 168), `…Crossbar` (5.0 × 0.35 × 0.35, 12), `…BenchSeat` (6.0 × 1.68 × 1.71, 160);
    variants `…LongBench`, `…Stool` (2.07 cube, 136), `…Workbench`. Palette `w11_wood #A2622A`, `w11_iron #40444F`.
    `MODEL_PROGRESS.md` row 87: **"thin top, straight legs (ref trestle); thin benches"**; `art/reference/kit/CHECKLIST.md`:
    TableSeating **5.5/10**. Its goals log: the hero read "squat", the A-frame "only obliquely", nails "oversized".
  - **Siblings:** M066 `CanvasShelter` (spec `art/blender/renders/models/M066/M066_spec.md`, decided, not built) has its own
    table (top **2.60**), benches and stool (seat tops **1.50**, bench depth **1.20**): **067 uses the same heights** (§1.1).
    M052 `TimberBoardwalk` (passed 8/10) and M048 / M050 / M051 are the committed timber builders whose helpers this model
    should import (§4.1). WorldModeling §13.1 (timber vocabulary: restrained bevels 0.02–0.05, joints and overlaps shown,
    "do not leave decorative braces floating near posts"), §13.8 ("Table/bench: top planks, trestles or legs, crossbar,
    and visibly joined seat supports").

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is `#FBF8EE`; pieces
cast a soft neutral-grey shadow down and to the left (`#C8C6C5`, s < 0.05), which the masks drop. Frame rules (`lines.py`
and zooms): hero panel y 125–475; ortho panel y 485–741 with cell dividers at about x 261, 489, 716; exploded panel x
14–665, y 750–1240; close-up panel x 673–1010 (cells A y ≈ 783–975, B ≈ 985–1155, C ≈ 1163–1405); palette panel x
14–321, y 1250–1492; notes panel x 321–665; footer rule y 1513.
- **Cells** (`m.CELLS`): f34 (14,150,596,475); r34 (598,150,1011,475); front (14,540,261,740); side (262,540,489,740);
  rear (490,540,716,740); top (717,540,1010,740); exploded (14,780,665,1240); close-up A (685,800,895,970) and its
  section (895,800,1005,970); B (685,1000,895,1150) and its section; C (685,1185,1005,1400); palette render
  (105,1285,305,1478).
- **Swatches** (inner boxes, sd ≤ 1.2): S1 (35,1290,75,1317); S2 (35,1330,75,1357); S3 (35,1370,75,1397); S4
  (35,1410,75,1437); S5 (35,1450,75,1476).
- **Masks** (`m.py`, HSV, h in degrees):
  - **W** wood: (h < 45 or > 350), s ≥ 0.35, v ≥ 0.18. One timber family; light and shade are lighting, so the class is
    split by value, not by material: **lit** v ≥ 0.85, **mid** 0.55–0.85, **shade** < 0.55.
  - **K** dark: v < 0.30 and not W: bolt heads, plank-gap lines, outlines, deepest shade.
  - **Object** = W ∪ K ∪ (warm, s ≥ 0.25, v < 0.6). Background = everything else (paper, cast shadow).
  - Apply the same code to our renders (studio floor hidden, plain background).

**Scratch study material** (no Blender) in `<temp>\m067_study\` (the session scratchpad). There is no Pillow on this
machine: the scripts use Blender's bundled Python (`<blender dir>/5.2/python/bin/python.exe -I <script> < /dev/null`,
numpy only) with a small PNG reader / writer (`png.py`); `load.py` caches the sheet as `sheet.npy`.
- **Helpers:** `m.py` (masks, `CELLS`, `hexs`, `hsvs`), `zoom.py` (`zoom.py x0 y0 x1 y1 scale out.png [grid]`),
  `runs.py <cell> row|col <coords>` (object runs: levels, edges, gaps), `lines.py` (frame rules).
- **Measurements:** `measure.py` (bbox, W : H, fill, K share per cell), `vbands.py` (lit / mid / shade shares, wood hue
  and saturation per cell), `proj.py` (block model of the adopted layout, projected at any camera: §2.9).
- **Colour:** `sw4.py` (swatches), `samp.py` (class medians per cell and named regions), `samp2.py` (bolts, pegs, shadow).
- **Zooms:** `z_f34.png`, `z_f34_top.png` (top planks and joints), `z_f34_under.png` (left trestle, braces),
  `z_f34_back.png` (knee brace under the top), `z_f34_stool.png`, `z_r34.png`, `z_r34_top.png`, `z_r34_stool.png`,
  `z_fs.png` (front + side), `z_rt.png` (rear + top), `z_front.png` and `z_side.png` (5×, grid 5, used for every ortho
  number below), `z_top.png` (4×), `z_expl.png`, `z_expl_top.png`, `z_cu.png`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** furniture set with three kinds of piece: **full asset, hero budget 4000 tris, plan about
  1700–2300; every part under 1000** (decision §8.13).
- **Overall read (check this first).** A **long, low, chunky plank table flanked by two long benches, with a square
  stool off its left end**:
  - a **thick top of four lengthwise planks** with dark gaps, staggered butt joints and softly bevelled edges, overhanging
    the trestles by about 0.8 at each end;
  - under each end an **A-frame trestle**: a cleat under the top, two square legs splayed apart toward their feet, a low
    tie between them pegged through the front leg, and one diagonal brace;
  - a **crossbar** along the middle, just under the top, whose square tenon ends poke out beyond both trestles; **two knee
    braces** from the crossbar down to the trestles' low ties (the front view's "V" under the top);
  - **two benches** as long as the table, each a seat of two planks on a splayed leg frame at each end;
  - **one stool**: a square three-plank seat on four splayed legs with rails;
  - **dark square bolt heads** at the joints (top over the trestles, cleat ends, trestle faces, bench faces, stool seat).
  - It reads **warm orange timber in three values (lit tops, mid faces, dark undersides), with small dark dots**:
    f34 lit 39 % / mid 26 % / shade 35 %, K 2.4 %.
- **Focal silhouettes, in order:**
  1. The thick plank top over two A-frame trestles; the long benches either side.
  2. The braced undercarriage: crossbar, knee braces, the trestles' diagonals, the poking tenon ends.
  3. The stool; the bolt heads; the plank gaps and joints.
- **Target size: table top at z 2.60, 6.00 long × 2.82 wide, 0.44 thick; bench and stool seat tops at z 1.50; benches
  5.80 × 1.20; stool 1.40 × 1.40; hero about 8.8 W × 6.1 D × 2.64 H** (decision §8.1). Tolerances: seat and table tops
  ±0.02 (they are gameplay heights), lengths ±0.15, sections ±0.04.
  - **How it was derived.** No piece carries a real size. The **heights come from M066** (the instruction for this sheet:
    the furniture scale must match 066's; 066 decided table top 2.60 and seat tops 1.50 against the 5.5-stud character).
    The horizontal sizes come from the cells, scaled by the table height:
    - Front cell (`z_front.png`): ground y 699.5, top y 586 (**113.5 px = 2.60 → 0.0229 stud / px**); top 18 px thick
      (0.41); table 212 px long (**L / H 1.87**); bench seat y 642–661 (seat top **0.507 H**); trestle legs 23 px (0.53);
      bench legs 20 px (0.46).
    - Side cell (`z_side.png`): ground y 689.5, top y 588 (**101.5 px = 2.60 → 0.0256**); table 131 px wide (**W / H
      1.29**); top 16 px thick (0.41); the stool-like piece's seat top at **0.567 H** (§3.5).
    - Top cell (`z_top.png`): table 183 × 86 px (**L / W 2.13**); benches 168 px (0.92 L); bench-to-table gap 12–13 px
      (0.15 W).
    - f34 (corners of the top in `z_f34_top.png`, ortho fit): camera about 35° off the front, 20° up; **L : W : H ≈ 2.40 :
      0.99 : 1** (±10 %: the cell has mild perspective; the left end's plank ends are about 20 % thicker on screen than the
      right end's).
    - The orthos disagree with each other (front L / H 1.87, rear 1.69; side W / H 1.29; top L / W 2.13 → with the side,
      L / H 2.75). The **f34 (hero view) and the top agree on a long table: L 6.0 with W 2.82** (L / W 2.13, L / H 2.31).
      The front and rear cells draw it shorter; that is recorded, not scored (§3.2).
    - Plank thickness: top 0.41 (front, side, f34 end faces), bench seat 0.46 (front), stool seat 0.46 (side): **one
      thickness 0.44 for every plank** (model notes: "consistent plank thickness").
  - **Why this size.**
    - **Against the character (5.5):** the table top is 0.47 C, the seats 0.27 C, as in 066 (a real 0.75 m table and
      0.45 m seat at 1.8 m per character, about 1.1× for Roblox's chunky avatars). A seated R15 character's thighs rest
      at the seat and its forearms reach the top; the side cell's seat at 0.567 H supports 1.50 (§3.5).
    - **Against the kit:** the same heights as 066's table set, so the two sets can stand side by side or swap in Studio.
      A 5.80 bench seats two characters a side (seat points 2.4 apart, §2.8); W11's 7.0-wide hero with a 0.35 top read
      "thin"; this top is 0.44 on a shorter table and reads chunky.
    - **Smaller** (top 2.2) puts the seats under 1.3 and the table at waist height for a standing avatar's hands, a toy.
      **Larger** (top 3.0) puts the top at a seated avatar's chin.
- **Build frame (decision §8.2):** front −Y (the near bench in the f34; the stool at the front-left), +X right, ground z 0,
  the table centred on x 0, y 0. Stage 2 puts the origin at the bbox bottom centre (about build (−1.39, 0, 0), because the
  stool sits off the −X end) and stores the offset (§2.10).

### 1.2 Measured views (`measure.py`, `vbands.py`)

| View (box) | Object bbox (px) | W : H | fill | lit / mid / shade % | K % | wood hue / sat (median) |
| --- | --- | --- | --- | --- | --- | --- |
| **f34** (14,150,596,475) | 39–575 × 169–457 (537 × 289) | **1.858** | 0.502 | **39 / 26 / 35** | 2.4 | 28° / 0.76 |
| r34 (598,150,1011,475) | 608–993 × 189–443 (386 × 255) | 1.514 | 0.533 | 38 / 27 / 34 | 2.5 | 28° / 0.77 |
| **Front** (14,540,261,740) | 33–244 × 586–699 (212 × 114) | **1.860** | 0.589 | 13 / 55 / 32 | 3.9 | 28° / 0.83 |
| Side (262,540,489,740) | 279–467 × 586–690 (189 × 105) | 1.800 | 0.593 | 7 / 58 / 35 | 5.5 | 27° / 0.80 |
| Rear (490,540,716,740) | 506–697 × 586–699 (192 × 114) | 1.684 | 0.592 | 13 / 56 / 31 | 4.1 | 28° / 0.84 |
| Top (717,540,1010,740) | 749–994 × 552–714 (246 × 163) | 1.509 | 0.678 | 17 / 74 / 9 | 1.9 | 29° / 0.78 |
| Exploded (14,780,665,1240) | 35–629 × 780–1211 | 1.377 | 0.372 | 38 / 34 / 29 | 2.9 | 28° / 0.77 |

- **Front cell levels** (fractions of the table height H, ground 0): top 0.84–1.00 (thickness **0.158 H**); a band under
  the top 0.74–0.84 H across x 43–235 (§3.6); legs x 50–73 and 205–227 (centres at **±0.73 of the half-length**);
  braces from the band at **±0.16 L from the centre** down-outward at **≈ 42°** to the legs at 0.52 H, where the bench
  hides them; bench seat 0.33–0.51 H, 205 px long (**0.967 L**), legs x 43–63 / 214–234 (centres at **±0.83 of the
  bench's half-length**), feet splayed out about 5°; bolt heads on the band over each leg and on the bench's front face
  over each leg.
- **Side cell levels:** top 0.85–1.00 H, 131 px wide; cleat 0.73–0.84 H, 113 px (**0.86 W**), bolt heads over each leg;
  legs x 297–317 / 372–396 (centres at **∓0.30 W**), nearly vertical (the right foot 3 px out); a diagonal from the front
  (screen-left) leg at 0.30 H up to the centre under the cleat; a low tie 0.15–0.29 H from x 279 to 398 (it runs **through
  the front leg and pokes 0.44 out**, with a peg bump on top, x 279–296, y 652–670), bolt heads on the legs at the tie's
  height; to the right, a stool-like piece (§3.5): seat top **0.567 H**, 53 px wide, centred **+0.71 W** from the table's
  centre, three plank ends, a rail under the seat (0.29–0.39 H), a low stretcher (0.11–0.23 H), legs splayed out a little.
- **Top cell:** four plank rows (the two middle rows read narrower: drawing slop; the side cell's four plank ends are
  equal, 30–35 px); butt joints at **0.18 L** (back row) and **0.51 L** (front row); dark bolt dots on the back and front
  rows over the trestles (x 776 / 905 = 0.15 / 0.85 L); the **trestle feet** show as dark blocks past both long edges (x
  769–783 and 896–910, reaching the benches' inner edges, §3.7); benches 168 × 26 px with a centre seam and one dot at each
  end on the seam; the stool 47 × 47 px, three rows, right of the table (§3.4).
- **Verifier tolerance:** f34 W : H 1.80 ± 0.12 (block-model estimate 1.74 at (−35, 20), §2.9); f34 lit / mid / shade 39 /
  26 / 35 ± 10 each; K 1–4 %; front (table and benches, stool hidden or cropped) top thickness 0.17 ± 0.02 H, band
  0.72–0.83 H ± 0.03, leg centres ±0.73 ± 0.04 of the half-length, brace upper ends ±0.16 ± 0.03 L, brace angle 42 ± 6°,
  bench length 0.967 ± 0.03 L, bench-leg centres ±0.84 ± 0.04 of the bench's half-length; side cleat 0.86 ± 0.04 W, leg
  centres ∓0.30 ± 0.03 W at the top, tie 0.15–0.29 ± 0.03 H; top four rows, joints at 0.18 / 0.36 / 0.85 L ± 0.04 (§2.3),
  gap 0.15 ± 0.03 W. **Recorded, not scored:** front L / H (ours 2.31, sheet 1.87), rear L / H (1.69), side W / H (ours
  1.08, sheet 1.29), bench top / table top in the front (ours 0.577, sheet 0.507; §3.8), top-view bench depth (ours
  0.43 W, sheet 0.30 W).

### 1.3 Silhouette and composition per view

**Front (`z_front.png`) — governs the heights, the trestle and brace positions, the bench layout.** A level view from −Y:
- the **top** as a thick slab with a bevelled top edge and two small bolt heads over the trestles;
- under it a **darker band** (0.74–0.84 H) the length of the trestle span: the cleat ends plus the crossbar behind them
  (§3.6), with a dark square bolt over each leg;
- two **square legs** under the band (vertical in this view), and between them **two braces** forming a wide "V" opened
  downward, from the band near the middle out to the legs, disappearing behind the bench at its top;
- in front, the **bench**: a two-plank seat slab nearly as long as the table, a bolt on its face over each leg, and at each
  end two legs, the front one splayed outward, the back one showing behind it;
- the trestle legs' lower halves show behind the bench legs; no low crossbar between the legs (§3.6).

**Side (`z_side.png`) — governs the trestle.** From +X (screen right = +Y):
- the top end-on: **four equal plank ends** with gaps;
- the **cleat** under it, a little shorter than the top, with a bolt over each leg;
- **two legs**, nearly vertical here, set in from the cleat ends (§3.7);
- **one diagonal brace** from the front (screen-left) leg low down up to the centre under the cleat;
- a **low tie** between the legs that runs through the front leg and **pokes out with a square peg** on top (close-up A's
  joint), bolt heads on both legs at the tie's height;
- to the right, a **stool-like piece** at the far bench's position and height (§3.5); the near bench is outside the cell.

**Rear (`z_rt.png`).** The front cell mirrored, drawn 10 % shorter (L / H 1.69): top, band with bolts, legs, the V of
braces, the other bench in front. Scored with the front's ratios (§3.2).

**Top (`z_top.png`, 4×).** The top's four plank rows with dark gaps, two butt joints, four bolt dots over the trestles;
the trestle feet poking out past both long edges; a bench either side with a gap; the stool off the right end (§3.4).

**f34 (`z_f34.png`, `z_f34_top.png`, `z_f34_under.png`, `z_f34_back.png`, `z_f34_stool.png`) — governs the overall read,
the construction and the layout.** From the front-left, above:
- the **top** running up-right; its left end shows three plank ends stepping down toward the viewer; the back row starts
  with a **short piece** (joint near the left end), the front row has a **joint about a third along**, a middle row a
  **joint near the right end**; soft lit bevels on every plank edge;
- the **left trestle**: the cleat end under the plank ends; the front leg nearly upright, the back leg leaning back (an
  A-frame splayed toward the feet); the diagonal; the low tie from the back leg to the front leg with dark square bolt heads
  near the foot;
- under the top on the right a **beam descending to the right trestle's foot area** (the right knee brace), and inside
  the right trestle a **"V"** (its diagonal and the brace seen obliquely);
- the **near bench** along the front, poking out past the table's right end; the **far bench** behind, poking out past the
  left end (both partly projection, §2.9);
- the **stool** at the front-left, about 2.3 past the table's left end, square to the table: a seat of three pieces
  (narrow / wide / narrow on its front face) with a cross seam, dark bolt heads on its faces, four legs splayed out both
  ways, a rail under the seat.
- Ortho fit of the top's corners: camera ≈ 35° off the front, ≈ 20° up; stool centre ≈ (−5.3, −1.2) in the build frame.

**r34 (`z_r34.png`, `z_r34_top.png`, `z_r34_stool.png`).** The same set seen from the back-right: the stool now at the far
right behind the near bench, the f34's near bench now behind, poking out on the left. It confirms the f34 layout (§3.3), the
four plank rows with staggered joints (three plank ends at the left end plus a set-in back row), the trestle "V", and the
stool's rail and stretcher.

**Exploded (`z_expl.png`, `z_expl_top.png`).** In loose perspective near hero scale; it governs part shapes, not sizes:
- **Table Top (Planks):** four rows (three plank ends at the near end plus a set-in back row), staggered butt joints, the
  near row with a joint about a third along;
- **Leg / Trestle:** a tall A-frame: two legs meeting under the cleat, the cleat's ends projecting with square peg blocks
  and dark bolts, a diagonal, a low tie, bolts near the feet; a second trestle to the right;
- **Crossbar:** a long square beam with a pin at its left end and a groove line, ending at a square post (read as the
  second trestle's upright; not modelled as a separate post, §3.6); square peg blocks fly out of both trestles along its
  line;
- **Bench Seat (Planks):** a two-plank seat (one butt joint near the right end) on a splayed two-leg frame at each end with
  a stretcher between the legs;
- **Stool:** a square seat of two planks with a crack, four splayed legs, a rail.

**Close-up A (`z_cu.png`).** The trestle head: the cleat end projecting past the leg with a dark square bolt; a projecting
square block (tenon end) on the trestle's face; the crossbar's end with a pin going in; a square wooden peg dropping out.
The section: a tenon through an upright with a peg slot.

**Close-up B.** Three top planks, each about 0.44 thick, with V gaps between them and a soft lit bevel on every edge; below
the front plank's end, the cleat's end face with a dark square bolt (0.4 of the plank thickness across).

**Close-up C.** From below: four planks along the length; a trestle at each end (cleat across the width, legs); the
crossbar along the middle with its square ends and pegs poking out past both trestles.

**Palette render.** A bevelled plank corner: flat faces, a light bevel line on each edge, broad soft grain, a dark
blue-grey square bolt with a bevelled face.

### 1.4 Parts (exploded, close-ups)

| Part (label) | Exploded box (px) | Tone (median, lit, shade) | Shape |
| --- | --- | --- | --- |
| Table Top (Planks) | (195,785,600,895) | `#F19D44` top, lit `#FCAA4D`, side `#B16528` | four lengthwise thick planks, gaps, staggered butt joints, bevels |
| Leg / Trestle | (180,925,300,1135), (470,880,570,1050) | as the top; shade `#6D3A14` | A-frame: cleat, two splayed legs, diagonal, low tie, pegged tenon ends, bolts |
| Crossbar | (300,960,460,1015) | as the top | long square beam, tenon pin at the end, a groove line |
| Bench Seat (Planks) | (300,1055,630,1210) | top `#E9913F`, lit `#F69C42` | two-plank seat, one joint, splayed two-leg frames with a stretcher |
| Stool | (35,1025,140,1165) | as the bench | square seat (two planks in this cell; three in the top cell and the f34), four splayed legs, a rail |
| Pegs (unlabelled) | (155,1020,182,1048), (558,935,590,960) | wood `#A1571D` (close-up A) | square wooden blocks, about 0.4 of a leg's width |
| Bolts (unlabelled) | every cell | `#474E56` (213°, .16, .34), lit `#5A666E`, shade `#262829` | dark blue-grey square heads, slightly domed |

- **Plank:** 0.44 thick; widths 0.66 (top), 0.58 (bench), 0.44 / 0.48 / 0.44 (stool); a **0.04 chamfer on the four long
  edges** (8-sided section; the end faces flat, or with the same chamfer if the budget allows), every piece its own
  closed shell; gaps 0.06 between rows, 0.04 at butt joints.
- **Square member** (legs, cleats, ties, crossbar, braces, rails): chamfer 0.04 on the long edges of legs, cleats and the
  crossbar; ties, braces, rails and stretchers plain boxes or cut prisms.
- **Bolt head:** 0.18 square, 0.05 proud with a 0.02 low pyramid to a centre point, sunk 0.03 into its face; always on a
  wood face, never floating.
- **Peg block:** 0.20 cube; **tenon stub:** 0.26 × 0.24 (crossbar) / 0.30 × 0.30 (tie), protruding 0.25–0.30.

### 1.5 How 067 differs from the old kit and its sibling (binding: the verifier checks these)

| | W11 `TableAndSeating` (old kit, exported) | M066 table set (spec) | **067 Table and Seating** |
| --- | --- | --- | --- |
| Size | 7.0 W × 3.1 H × 7.7 D; top 0.35 thick | table 7.2 × 2.8 × 2.6, seats 1.5 | **table 6.0 × 2.82 × 2.60, seats 1.50, hero ≈ 8.8 × 6.1 × 2.64** |
| Top | thin planks, uneven ends | four 0.25 planks | **four 0.44 planks with gaps and three staggered butt joints, 0.04 bevels** |
| Legs | "straight legs (ref trestle)" | square legs + stretchers | **two A-frame trestles (10° splay), cleat, diagonal, low tie through the front leg with a peg; a crossbar under the top with poking tenons; two knee braces** |
| Seating | "thin benches", bench + stool variants | two-plank benches, stool | **two 5.80 two-plank benches on splayed leg frames with cleats and stretchers; a three-plank stool with rails** |
| Hardware | hex nail heads, oversized | — | **30 dark slate square bolt heads 0.18, peg blocks** |
| Colour | `#A2622A` one key | plank key by role | **one orange timber `#B8671F` with per-piece tint and positional bands; slate bolts `#474E56`** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0). Kit camera azimuths: `front` az 0 (camera on −Y), `side` az 90
(camera on +X, screen right = +Y), `rear` az 180, f34 about az −35 e 20, r34 az 145 e 20.

### 2.1 Stack (binding contact chain; every seat ≤ 0.03 unless stated)

| Piece | Rests on / against | Contact |
| --- | --- | --- |
| Trestle legs (4), bench legs (8), stool legs (4) | the ground | flat horizontal feet on z 0.000 (±0.005) |
| Cleats (2) | the two legs of their trestle | cleat bottom z 1.86 on both leg tops |
| Top planks (7) | both cleats | plank bottoms z 2.16 on the cleat tops (±0.005) |
| Crossbar | the top's underside, between the cleats | top face on z 2.16; end faces against the cleats' inner faces (gap 0.00–0.02) |
| Crossbar tenon stubs (2) | the cleats' outer faces | inner face on the cleat face (0.00–0.02), top face against the plank underside |
| Low ties (2) | between their legs | end faces against the legs' inner faces (≤ 0.03 at the nearest point; the splay leaves a wedge ≤ 0.06) |
| Tie stubs (2) + peg blocks (2) | the front legs' outer faces; the stub tops | stub on the leg face (0.00–0.02); peg on the stub top |
| Trestle diagonals (2) | front leg inner face + tie top; cleat underside | both cut ends touching (≤ 0.02) |
| Knee braces (2) | the tie tops; the crossbar's underside | both ends cut horizontal, touching (≤ 0.02) |
| Bench seat cleats (4) | their two legs | cleat bottom z 0.80 on both leg tops |
| Bench seat planks (6) | the two cleats | bottoms z 1.06 |
| Bench stretchers (4), stool aprons (4), stool stretchers (2) | between their legs | ends against the legs' faces (≤ 0.03) |
| Stool seat planks (3) | the four leg tops and the aprons | bottoms z 1.06 |
| Bolt heads (30) | their faces | sunk 0.03, 0.05 proud + 0.02 dome |

### 2.2 Trestles (×2, centred on x = ±2.20; identical, not mirrored)

| Member | Section (X × Y × Z) | Position | Notes |
| --- | --- | --- | --- |
| Cleat | 0.45 × 2.43 × 0.30 | z 1.86–2.16, y −1.215 … +1.215 | 0.04 chamfer on its long edges; protrudes 0.125 past the leg tops |
| Legs (2) | 0.50 (X) × 0.46 (Y), horizontal section | tops: centres y ±0.86 at z 1.86; feet: centres y ±1.19 at z 0 (**10° splay**, feet's outer faces ±1.42, flush with the top's edges) | sheared prisms with **horizontal** end caps (planar), 0.04 chamfer on the four long edges |
| Low tie | 0.34 × (between legs) × 0.35 | z 0.40–0.75, y between the legs' inner faces (≈ ±0.86) | plain box |
| Tie stub + peg | stub 0.30 × 0.25 × 0.30 on the front leg's outer face (−Y), centred z 0.575; peg 0.20 cube on its top | stub y ≈ −1.32 … −1.57 | close-up A's pegged through-tenon, the side cell's block at screen left |
| Diagonal | 0.30 thick (X), 0.34 wide | lower end against the front leg's inner face on the tie top (y ≈ −0.83, z 0.75); upper end under the cleat at y ≈ 0 (z 1.86) | `m048._brace_quad` + `_plank2d` (low end vertical against the leg, high end horizontal against the cleat) |
| Bolts | — | cleat end faces (±Y), 1 each; the trestle's outer X face over each leg at cleat height and at tie height (4); the crossbar stub's end face (1) | 7 per trestle |

- The diagonal runs from the front leg low up to the centre, as the side cell draws it; both trestles use the same mesh, so
  from the f34 the left trestle shows it from its inner side.
- Trestle outer face x ±2.425 (cleat), legs x ±1.95 … ±2.45.

### 2.3 Top, crossbar and knee braces

- **Top:** x −3.00 … +3.00, y −1.41 … +1.41, z 2.16 … 2.60. Rows (y centres, back → front): R1 +1.08, R2 +0.36, R3 −0.36,
  R4 −1.08; width 0.66, gaps 0.06. **Butt joints** (0.04 gap, centred at): R1 x −1.92 (0.18 L, the short piece at the −X
  end: top cell, f34, r34, exploded), R3 x +2.10 (0.85 L: f34, r34, exploded), R4 x −0.84 (0.36 L: f34 and exploded; the
  top cell draws it at 0.51 L). R2 runs whole. Seven pieces. End offsets ±0.03 per piece and top jitter ±0.008 allowed
  (hand-made); **no step above 0.02 between rows**, so a cup or plate stands level.
- **Bolts on the top:** R1 and R4 at x ±2.20 (over the trestles), 4 heads.
- **Crossbar:** 0.36 (Y) × 0.30 (Z), y −0.18 … +0.18, z 1.86–2.16, x −1.975 … +1.975 (between the cleats' inner faces);
  0.04 chamfer on its two lower long edges. **Tenon stubs** 0.26 × 0.24 at y 0, z 1.89–2.13, on the cleats' outer faces,
  x ±2.425 … ±2.725 (they poke out past the trestles and stay under the top's 0.575 overhang); a bolt head on each
  stub's end face. Built as body + stubs that **touch** the cleats, never one bar through them (no buried tenon).
- **Knee braces (2):** in the plane y = 0 (0.30 wide in Y, 0.30 thick), upper end cut horizontal under the crossbar at x
  ±0.95 (z 1.86), lower end cut horizontal on the tie's top at x ±2.03 … ±2.33 (z 0.75): **≈ 42°**, as the front cell
  draws them. They miss the trestle diagonal (which is at z ≥ 1.6 near y 0) by ≥ 0.1.

### 2.4 Benches (×2, at y = ±2.40; identical, the back one turned 180°)

| Member | Size | Position (bench-local: x along the bench, y across, bench centre at 0) |
| --- | --- | --- |
| Seat planks | 2 rows 0.58 wide, gap 0.04 → 1.20 deep; 0.44 thick; 5.80 long | z 1.06–1.50; the inner row (toward the table) has a butt joint at x −2.03 (0.15 L from −X; f34 near bench, exploded); three pieces |
| Seat cleats (2) | 0.34 (X) × 1.10 (Y) × 0.26 | z 0.80–1.06, centred x ±2.45 |
| Legs (4) | 0.42 square (horizontal section) | tops centred (±2.45, ±0.36) at z 0.80; **splayed 5° outward along X and 4° outward along Y** (feet centred ≈ (±2.52, ±0.42)) |
| Stretchers (2) | 0.20 (X) × (between legs) × 0.24 | z 0.30–0.54, between each frame's two legs |
| Bolts (4) | — | seat top on the centre seam at x ±2.45 (2: top cell); the outer long face (away from the table) over each frame (2: front and rear cells) |

- Bench centres: front (0, −2.40), back (0, +2.40). Seat inner edges y ±1.80 (**0.39 gap** to the top's edges ±1.41, top
  cell 0.15 W ≈ 0.42); outer edges ±3.00.
- Bench legs at x ±2.45 overlap the trestle legs and the tie stubs in X; they are separated in Y (bench legs' inner faces
  ±1.83 at the top, ±1.77 at the feet; trestle feet ≤ ±1.42; tie stub ≤ −1.57): clearance ≥ 0.20.

### 2.5 Stool (one, at (−4.95, −1.30))

| Member | Size | Position (stool-local) |
| --- | --- | --- |
| Seat planks (3) | 0.44 / 0.48 / 0.44 wide, gaps 0.02 → 1.40; 0.44 thick; 1.40 long (along X) | z 1.06–1.50; a cross seam (0.03 groove or a butt joint) across the middle plank (f34) is optional |
| Legs (4) | 0.38 square | tops centred (±0.47, ±0.47) at z 1.06; **splayed 7° outward both ways** (feet ≈ (±0.60, ±0.60)) |
| Aprons (4) | 0.14 thick × 0.22 tall | z 0.84–1.06 between the legs on all four sides, set 0.04 in from the legs' outer faces |
| Stretchers (2) | 0.14 × 0.20 | z 0.30–0.50, between the legs on the ±X sides |
| Bolts (4) | — | centre of each seat side face |

- The stool stands square to the table (yaw 0°), its +X edge 1.25 clear of the table's −X end and its −Y edge level with
  the near bench's inner half. Clearances to the near bench ≥ 1.2 in X.

### 2.6 Bolts (all square heads, `m067_iron`)

| Where | Count |
| --- | --- |
| Top (R1, R4 over the trestles) | 4 |
| Cleat end faces (±Y) | 4 |
| Trestle outer faces (over each leg at cleat height and tie height) | 8 |
| Crossbar stub end faces | 2 |
| Benches (2 seat top + 2 outer face, each) | 8 |
| Stool seat side faces | 4 |
| **Total** | **30** |

### 2.7 Expected extents

- **Table:** X −3.00 … +3.00, Y −1.57 (tie stub) … +1.42, Z 0 … 2.64 (top bolts).
- **Hero:** X ≈ −5.75 (stool foot) … +3.00, Y ≈ −3.03 … +3.03 (bench feet), Z 0 … 2.64 → **about 8.75 × 6.06 × 2.64**;
  bbox bottom centre ≈ (−1.38, 0, 0) in the build frame.

### 2.8 Seating and walkability (binding)

- **Seat tops level at z 1.50 ± 0.01** (benches and stool), every seat plank's top within 0.01 of its neighbours (no
  step a Seat part would rock on).
- **Seat points** (stored on the hero, for Studio `Seat` parts, one character each): `m067_seat_f1` (−1.20, −2.40, 1.50) and
  `m067_seat_f2` (+1.20, −2.40, 1.50), facing +Y; `m067_seat_b1` (−1.20, +2.40, 1.50) and `m067_seat_b2` (+1.20, +2.40,
  1.50), facing −Y; `m067_seat_stool` (−4.95, −1.30, 1.50), facing +X. Each point's facing stored as a unit vector.
- **Knee room:** for each bench seat point, a seated-legs proxy (1.2 W × 1.2 D box from the seat's front edge toward the
  table, z 0.0–1.75) touches nothing of the table: the trestles (x ±1.95 … ±2.45), the crossbar and knee braces (y ±0.18)
  stay clear. Print the minimum clearance (target ≥ 0.10).
- **Walk around:** a 5.5-stud proxy (2 × 1 × 5.5) walks round the whole set at 0.3 from its outline without passing
  through anything; no pocket 1.0–2.0 wide where a character could wedge (the bench gaps are 0.39, too narrow to enter).
- The top is a surface characters can jump onto (flat within 0.02).

### 2.9 Screen checks (floor hidden; `measure.py` masks; probe and keep the best)

- **front_sheet (0, 0)** — governs heights and the undercarriage. **Hide the stool** (or crop to the table's X range: the
  sheet's front cell has none, §3.4). Top thickness 0.17 ± 0.02 H; band 0.72–0.83 H; leg centres ±0.73 ± 0.04 of the
  half-length; brace upper ends ±0.16 ± 0.03 L, angle 42 ± 6°, lower ends hidden behind the bench; bench length 0.967 ±
  0.03 L; bench-leg centres ±0.84 ± 0.04; bench top 0.577 H (decided, §3.8); bolts on the band over each leg and on the
  bench face over each leg; W : H recorded (ours ≈ 2.27, sheet 1.86).
- **rear_sheet (180, 0)** — the same checks mirrored, stool hidden.
- **side_sheet (90, 0)** — governs the trestle: cleat 0.86 ± 0.04 W; leg centres ∓0.30 ± 0.03 W at the top; feet splayed
  (≤ 0.05 W past the top's edges); the diagonal from the front (screen-left) leg low to the centre under the cleat; the
  tie at 0.15–0.29 H with its stub and peg poking out at screen left; the crossbar stub end-on at the centre under the top;
  the back bench end-on at screen right, centred +0.85 W from the table centre, seat top 0.577 H (sheet 0.567 ✓); the
  stool beyond the table at screen left-back. W / H recorded (ours 1.08, sheet 1.29).
- **f34_sheet (−35, 20)** (probe az −30 … −45 × e 15 / 20 / 25; the cell has mild perspective) — governs the overall read
  and layout: W : H 1.80 ± 0.12 (`proj.py` block model: 1.74 at (−35, 20), 1.81 at (−30, 20)); lit / mid / shade 39 / 26 /
  35 ± 10; K 1–4 %; the stool at the left, about 1.25 clear of the table's left end and square to it; the far bench
  poking out at the left behind the table, the near bench poking out at the right; three plank ends on the top's left end
  with the back row's short piece; both trestles' A-frames and the right knee brace descending under the top.
- **r34_sheet (145, 20)** — content: the stool at the far right, the A-frame of the +X trestle with its diagonal, the
  crossbar stub, the far bench poking out at the left.
- **top (0, 89.9)** — four rows with the joints at 0.18 / 0.36 / 0.85 L ± 0.04 (R1 / R4 / R3); bolt dots on R1 and R4 over
  the trestles; gap 0.15 ± 0.03 W; benches with a centre seam and an end dot each; trestle feet at the top's edges; the
  stool off the −X end (sheet: off the +X end, §3.4).

### 2.10 Origin, pivot and stored points

- Origin at the **bbox bottom centre** (`K.check`); transforms applied. Store `o["m067_offset"]` (build frame = object +
  offset, M052's convention; expected ≈ (−1.38, 0, 0)), `o["m067_centre"]` = the table's floor centre (build (0, 0, 0)),
  the five seat points and facings (§2.8); re-check all after the origin move.
- Parts: origin at their own bbox bottom centre; the Table part also stores its seat points (relative to itself: the bench
  points at ±2.40) so a Studio script can seat characters at a table placed alone; the Bench part stores its two seat
  points; the Stool part its one.

## 3. View conflicts and resolutions

### 3.1 Sheet number
- **Evidence.** The header says "PAGE 69/132"; INDEX.md row 67 lists `067.png` as "Flintborn Table and Seating Study".
- **Resolution.** Our number is 067 (file name, keys `m067_*`). Note the header in the export notes only.

### 3.2 Table length: the orthos disagree
- **Evidence.** Front L / H 1.87, rear 1.69; side W / H 1.29; top L / W 2.13; f34 L : W : H ≈ 2.40 : 0.99 : 1 (ortho fit,
  ±10 %). The front and side together give L / W 1.45; the top and side give L / H 2.75.
- **Resolution (decision §8.1).** **L 6.00, W 2.82, H 2.60** (L / H 2.31, L / W 2.13, W / H 1.08): the f34 (hero view) and
  the top (plan) agree on a long table; the front and rear draw it about 20 % shorter. Front and rear are scored on their
  levels and fractions, not on W : H. Alternative: L 5.0 (front cell; the f34 then reads stubby, and the benches seat two
  a side only tightly).

### 3.3 "Rear three-quarter view" is a true rear view
- **Evidence.** The r34 shows the stool at the far right behind the near bench, and a bench poking out on the left behind
  the table: exactly the f34's layout turned 180° (the f34's stool at the front-left lands at the back-right; its near
  bench becomes the far one).
- **Resolution.** The r34 confirms the f34's layout; both govern it (unlike 052 and 066, whose "rear" views were redraws).

### 3.4 Where the stool stands
- **Evidence.** f34 and r34: off the table's −X end, at the front (ortho fit ≈ (−5.3, −1.2)). Top cell: off the +X end, on
  the centre line (≈ (+4.3, −0.1)). Front and rear cells: no stool. Side cell: a stool-like piece at the far bench's
  place (§3.5).
- **Resolution (decision §8.4).** **(−4.95, −1.30), square to the table**, as the two hero views (which agree with each
  other) place it, pulled 0.35 toward the table so it reads as part of the set. The ortho renders hide it for scoring.
  Alternative: the top cell's (+4.3, 0) (the f34 and r34 then show it in the wrong place).

### 3.5 The side cell's "stool" is the far bench end-on
- **Evidence.** The piece right of the table in the side cell sits at **Y +2.39** (centre +0.71 W at the side scale, our
  bench centre 2.40), its seat top at **0.567 H** (our bench 0.577 H), about 1.36 wide (bench depth 1.20); its legs splay
  sideways with a rail under the seat and a low stretcher, which is a bench end frame seen end-on. It draws three plank ends
  where the bench has two. The near bench, at screen left, is cut off by the cell edge.
- **Resolution.** Read it as the back bench end-on: it confirms the bench's position and the 1.50 seat height. The bench
  keeps two seat planks (front, rear, top, exploded, f34).

### 3.6 The crossbar: under the top, not low; and the front cell's band
- **Evidence.**
  - The exploded labels a "Crossbar" running between the trestles with a pin at its end; close-up A's crossbar enters the
    **trestle's head**, just below the projecting cleat; close-up C draws it along the middle with square ends and pegs
    poking out past both trestles.
  - The front and rear cells draw a **band under the top** (0.74–0.84 H) along the trestle span, with bolts over the legs,
    and two braces from it down to the legs. Below the bench seat nothing runs between the legs: **there is no low
    crossbar** (it would show between the bench legs).
  - The f34 shows no front apron: under the near top edge the underside is open to the shadow, with the right knee brace
    descending from under the top to the right trestle's low tie.
  - The exploded's square post at the crossbar's right end matches no assembled view.
- **Resolution (decision §8.5).** One **crossbar at y 0 directly under the top** (z 1.86–2.16) between the cleats, its
  tenon stubs poking out past both trestles; **two knee braces** from it down to the low ties at 42°; no front or back
  apron; no post. The front band is the crossbar behind the cleat ends (same height); the front cell's bolts over the legs
  are the cleat-end bolts (close-up B). Alternative: front and back aprons bolted to the legs (closer to the front cell's
  band; contradicts the f34's open underside and close-up C).

### 3.7 Trestle legs: A-frame or vertical
- **Evidence.** The exploded and close-up A draw a strong A (legs meeting under the cleat); the f34 shows the back leg
  leaning back; the top cell shows the feet poking past both long edges of the top (to the bench edges, ≈ 0.42 out); the
  side cell (the one view that sees the trestle square-on) draws the legs nearly vertical, feet 0.3 W in from the top's
  edges. The model notes say "A-frame trestles".
- **Resolution (decision §8.6).** **10° splay**: feet's outer faces flush with the top's long edges (±1.42), tops 0.33
  inside the cleat ends. The A reads in the f34, r34 and side, the feet show at the edges in the top view, and the benches
  keep ≥ 0.25 clearance. Alternatives: 4° (the side cell; the A is lost: W11's "straight legs" failure) or 16° (the top
  cell's feet to the bench edges; the feet then clash with the bench legs).

### 3.8 Seat height: 066's 1.50 vs the front cell's 0.507 H
- **Evidence.** Front and rear cells: bench seat top 0.507 H (1.32 at H 2.60). Side cell (the back bench end-on): 0.567 H
  (1.47). M066 (decided): seats 1.50 with its table at 2.60. The instruction for this sheet: match 066's furniture scale.
- **Resolution (decision §8.3).** **Seats 1.50** (0.577 H): one kit seat height, the side cell's value, 066's value.
  Recorded in the front check. Alternative: 1.32 (the front cell; then 066 and 067 seat heights differ by 0.18 and Studio
  seat offsets need two values).

### 3.9 Plank count on the top: four
- **Evidence.** Side cell: four equal plank ends. Top cell: four rows. Exploded and r34: three plank ends at one end plus a
  set-in back row (four rows). f34's left end and close-up B show three plank ends (the back row's short piece starts
  further in, or the crop shows three).
- **Resolution.** **Four rows**; the back row's butt joint near the −X end gives the f34's and exploded's staggered look.

### 3.10 Butt joints differ per view
- **Evidence.** Back row: 0.18 L (top cell), near the left end (f34, r34, exploded). Front row: 0.51 L (top), ≈ 0.34 L
  (f34), 0.32 L (exploded), 0.25 L (r34). A middle row: near the right end (f34 0.85, exploded 0.85, r34), none in the
  top cell.
- **Resolution.** R1 0.18 L, R3 0.85 L, R4 0.36 L (§2.3): the hero views govern where they agree with each other.

### 3.11 Stool seat: two or three planks
- **Evidence.** Exploded: two planks with a crack. f34: three pieces on its front face (narrow / wide / narrow) and a cross
  seam on top. Top cell: three rows. r34: a 2 × 2 look (two planks and a cross seam).
- **Resolution.** **Three planks** (0.44 / 0.48 / 0.44) along X with an optional cross groove on the middle plank: the f34
  and top agree. Alternative: two 0.69 planks (exploded).

### 3.12 Bench legs: splay direction
- **Evidence.** Front cell: the bench legs splay outward along X about 5°. Side cell (bench end-on) and exploded: the two
  legs of a frame splay apart in Y with a stretcher. f34: both.
- **Resolution.** **5° along X and 4° along Y**; stretchers between each frame's legs (§2.4).

### 3.13 Palette swatches that match nothing rendered
- **Evidence.** S1 `#B56420` matches the rendered wood's mid faces, S2 `#E59241` its lit tops. S3 `#B09584` (warm grey),
  S4 `#D14137` (red) and S5 `#FAE4BD` (cream) match no surface: the bolts render dark slate `#474E56` (close-up B, palette
  render), the only red on the sheet is the exploded's dashed arrows and close-up A's section outline, and the cream is
  the paper.
- **Resolution.** Wood from S1 / S2 and the rendered regions; bolts from the rendered heads (`#474E56`); S3–S5 unused
  (recorded). Alternative: bolts in S3's warm grey (they would read as pale pewter, unlike every drawn head).

### 3.14 "No fine surface detail or texture noise" vs the drawn grain and cracks; light and shade
- **Evidence.** Every plank carries painted grain streaks, small crack notches at its edges and a light bevel line. The
  model notes forbid fine surface detail and texture noise; the user's rule wants colour that blends.
- **Resolution.** No modelled cracks or grain; the bevel lines come from the 0.04 chamfers catching the light. Colour:
  one wood key with per-piece Tint and broad positional bands (§5.3). The dark undersides, end faces and shaded legs
  (f34 shade 35 %) are lighting, not paint.

### 3.15 Cast shadow and ground
- **Evidence.** A soft grey cast shadow under every view; no grass, rug or ground patch.
- **Resolution.** Nothing under the set; feet on z 0.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

1. `plank(x0, x1, y0, y1, z0, z1, ch, seed)` → one 8-sided chamfered plank (0.04 on the four long edges). Check against
   close-up B and the palette render.
2. `top()` → the seven pieces of §2.3 + 4 bolts. Check against the exploded top and the top cell.
3. `trestle(sx)` → cleat, two splayed legs (`leg(top_xy, foot_xy, z0, z1, w, d)`: a sheared prism with horizontal caps),
   tie, tie stub, peg block, diagonal, 7 bolts. Check against the exploded trestle, close-up A and the side cell.
4. `crossbar()` → body + two stubs (+ the stub bolts if the part should carry them). Check against the exploded crossbar
   and close-up C.
5. `knee_brace(sx)` → the 42° brace with both ends cut horizontal. Check against the front cell.
6. `bench(sy)` → 3 seat pieces, 2 cleats, 4 splayed legs, 2 stretchers, 4 bolts. Check against the exploded bench and the
   side cell's end-on frame.
7. `stool()` → 3 seat planks, 4 splayed legs, 4 aprons, 2 stretchers, 4 bolts. Check against `z_f34_stool.png`,
   `z_r34_stool.png` and the exploded stool.
8. `bolt(c, n)` → a square head (own constants: half-size 0.09, proud 0.05, dome 0.02, sink 0.03), built with
   `m048._solid`.
9. **Hero `TrestleTableSet`** = top + 2 trestles + crossbar + 2 knee braces + 2 benches + stool, placed by §2, one object
   of closed shells. Then run the contact, bury, knee-room, walk and winding reports (§6, §2.8).
10. **Parts shot** (−20, 15) laid out like the exploded: Top, Trestle, Crossbar, Bench, Stool, gaps 0.8; plus the Table.
11. **Exploded shot:** the top lifted 1.5, the trestles apart, the crossbar between them, a bench and the stool below.

**Timber helpers to reuse (all committed; import the functions, never the module constants):**
- `m048`: `_solid` (closed shell from points and faces, flips by volume), `_prism` (vertical prism with a chamfered top),
  `_box`, `_rect`, `_inset`, `_plank2d` (a board from a 2D outline extruded along X or Y), `_brace_quad` (brace outline
  cut vertical at a leg face and horizontal at a beam underside: the trestle diagonal), `_tri_ngons`,
  `winding_report`, `shells_report`, `contact_report`, `_recentre`, `_make_plain`. Its `_bolt` is round and sized by
  m048's `BOLT_R 0.275`: don't use it.
- `m052`: `_ext` (straight prism of a 2D region with consistent winding), `_cells` (grid-cell prism, no slivers),
  `_earclip`, `_slab` (ear-clipped prism of any simple polygon: chamfered plank sections, cut braces), `_plank2d`,
  `_plank2d_yz`, `_brace`, `_post_solid` (square post with chamfered cap). Its `_bolt(sides=…)` would give a square head
  with `sides=4`, but it is sized by m052's `BOLT_R 0.36` (twice this sheet's head): write `m067._bolt` instead.
- `m050`: `_peg` (round peg head; not this sheet's square peg), `buried_report`, `_inside`, `_groups`, `levels_report`.
- `m047`: `_Solids` (ray-parity inside test for the bury report), `shells_report`. `m038`: `contacts()`, `contact_report`.
- Copy, don't import, from anything uncommitted (`m064`, `m065` if their helpers are wanted).

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a thick four-plank table on two A-frame trestles, a crossbar under the top with poking tenons and two
   knee braces, two long two-plank benches either side, a three-plank stool off the left end, dark square bolts.
2. **front_sheet / rear_sheet / side_sheet / f34_sheet / r34_sheet / top** per §2.9.
3. **Close-up renders:**
   - `join_cu` on the +X trestle head from the front-right, against close-up A: cleat end projecting with its bolt, the
     crossbar stub poking out with its bolt, the diagonal meeting the cleat.
   - `tie_cu` on the −X trestle's front leg from the front-left: the tie stub through the leg with its peg block (the side
     cell's block).
   - `plank_cu` on the top's front-right corner, against close-up B and the palette render: three plank ends with V gaps
     and lit bevels, the cleat end face with its bolt below.
   - `under_cu` from (0, −1.0, 0.4) looking up at (0, 0, 2.2), against close-up C: four planks, both cleats, the crossbar
     with its stubs past the trestles, the knee braces.
   - `stool_cu` against `z_f34_stool.png`: three planks, bolts on the side faces, splayed legs, aprons.
   - `seat`: a 5.5 proxy seated at each seat point (a sitting pose box: hips on the seat, thighs forward, lower legs down)
     from the front and the side; knee room printed (§2.8).
   - `thumb`: the f34 at about 140 px tall: top, trestles, benches and stool still read; plank gaps visible.
   - `spin` contact sheet: az 0 / 45 / … / 315 at e 10: nothing floats, every leg reaches the ground.
4. **Contact counts** (§6): floating shells 0; buried 0 (stated seats excepted); winding errors 0.
5. **Scale shot:** the 5.5 marker standing beside the table and one seated at `m067_seat_f1`.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Top plank pieces (8-sided, chamfered long edges) | 7 | 28 | 196 |
| Cleats (chamfered) | 2 | 28 | 56 |
| Trestle legs (sheared, chamfered) | 4 | 28 | 112 |
| Ties, tie stubs, peg blocks, diagonals | 2 each | 12 | 96 |
| Crossbar (chamfered) + 2 stubs | 1 | 28 + 24 | 52 |
| Knee braces | 2 | 12 | 24 |
| Bench seat pieces (3 per bench) | 6 | 28 | 168 |
| Bench legs (chamfered) / cleats / stretchers | 8 / 4 / 4 | 28 / 12 / 12 | 320 |
| Stool seat planks / legs / aprons / stretchers | 3 / 4 / 4 / 2 | 28 / 28 / 12 / 12 | 268 |
| Bolt heads (4 sides + domed top + base) | 30 | 14 | 420 |
| **Hero** | | | **about 1710; plan 1700–2300 (end chamfers on the planks add ≈ 16 × 16); ceiling 4000** |
| Parts: Table (top + trestles + crossbar + braces + its 18 bolts) / Top / Trestle / Crossbar / Bench / Stool | | | ≈ 790 / 252 / 230 / 80 / 300 / 324 |

- Far under the ceiling: **don't spend the headroom on noise** (cracks, grain ridges, rounded corners). Allowed uses, in
  order: chamfer the plank end edges too (+≈ 256); give the bolts 0.02 bevels (+≈ 240). Never drop a bolt group, a peg, a
  stub, a brace, a stretcher or a plank joint.

### 4.4 Shape targets (binding; check with `M.audit` and own bmesh code)

- Table top 6.00 ± 0.15 × 2.82 ± 0.08, top face at 2.60 ± 0.02, four rows, gaps 0.06 ± 0.02, joints at §2.3 ± 0.25.
- Planks 0.44 ± 0.03 thick everywhere (top, benches, stool); chamfers 0.03–0.05 on every plank's long edges.
- Trestle legs 0.50 ± 0.05; splay 10 ± 2°; feet within the top's footprint ± 0.05; cleat 2.43 ± 0.1.
- Crossbar under the top at y 0 ± 0.05, stubs protruding 0.25–0.35 past the cleats; knee braces 42 ± 6°.
- Seat tops 1.50 ± 0.01; benches 5.80 ± 0.15 × 1.20 ± 0.06 at y ±2.40 ± 0.08; stool 1.40 ± 0.08 square.
- Bolt heads 0.16–0.20 square, 0.04–0.07 proud.

### 4.5 Stages 2 and 3

- **Stage 2:**
  - Every shell closed and manifold, **0 bowties** (none expected: no shell shares a vertex with another).
  - **0 winding errors per shell** (`bmesh.ops.recalc_face_normals` per shell, then `m048.winding_report` or
    `m047.shells_report`, plus a parity ray test): the sheared legs, cut braces and chamfered prisms are where a reversed
    face slips in (044's wedge).
  - No zero-area faces; corners ≥ 3° measured on quads (long thin boxes triangulate to small angles, recorded as M052's
    finding 10, not a defect); every leg cap and brace end planar (sheared prisms keep horizontal caps planar).
  - Origin at the bbox bottom centre, transforms applied, every stored point re-checked.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box)

| Swatch | Hex (HSV) | Use |
| --- | --- | --- |
| S1 | `#B56420` (27°, .82, .71) | the wood's mid faces (`m067_wood`) |
| S2 | `#E59241` (29°, .72, .90) | the wood's lit tops (lighting of `m067_wood`; the `m067_wood_light` blend partner) |
| S3 | `#B09584` (23°, .25, .69) | matches nothing rendered (§3.13) |
| S4 | `#D14137` (3°, .74, .82) | the sheet's arrows; unused |
| S5 | `#FAE4BD` (38°, .24, .98) | the paper; unused |

### 5.2 Rendered regions (`samp.py`, `samp2.py`; median / lit quartile / shade quartile)

| Region | Median | Lit Q | Shade Q |
| --- | --- | --- | --- |
| Wood, whole cell: f34 / r34 / front / side / rear / top / exploded | `#BE6D29` (27°, .78, .75) / `#B96927` / `#B4641E` (28°, .83, .71) / `#A45D20` / `#B5641D` / `#CB7A2D` (29°, .78, .80) / `#BB6A29` | `#F9A748` / `#F8A446` / `#DB8C34` / `#C3722A` / `#DB8A34` / `#DC8530` / `#F9A447` | `#643412` / `#633411` / `#5E2F0D` / `#51290F` / `#61310D` / `#B66B28` / `#6D3A14` |
| f34: top surface / near plank side face / left end faces | `#ED9A42` (30°, .72, .93) / `#C56E27` / `#6B3D22` | `#F8A242` / `#F1A43A` / `#724124` | `#D5883A` / `#B26627` / `#5E351D` |
| f34: front-left leg (lit) / back-left leg (shade) | `#F09228` / `#804D2B` | `#F99B30` / `#88532E` | `#804313` / `#562A12` |
| f34: near bench top / bench front face / stool top / stool leg | `#F9A648` (31°, .71, .98) / `#B16629` / `#E49848` / `#864F28` | `#FCAA4D` / `#B6692B` / `#F6B056` / `#D68337` | `#F09D46` / `#AA5E26` / `#C07C3C` / `#724220` |
| Front cell: top face / band / trestle leg / brace / bench face / bench leg | `#BE6D22` / `#70380E` / `#683714` / `#5F310E` / `#BB6A21` / `#B8671E` | `#CE7A29` / `#884612` / `#93511E` / `#723C12` / `#EEA953` / `#C26C20` | `#B2621F` / `#54290A` / `#421E07` / `#48260B` / `#AE5E1C` / `#753A0E` |
| Side cell: cleat / leg | `#5F3010` / `#A55E23` | `#804417` / `#B76A25` | `#44220C` / `#5D2F13` |
| Top cell: table / bench | `#CC7B2D` / `#CF7D2D` | `#DC842E` / `#D78531` | `#BD702B` / `#BF7029` |
| Exploded: top / bench top; close-up B: plank top / plank front | `#F19D44` / `#E9913F`; `#E99545` / `#884A21` | `#FCAA4D` / `#F69C42`; `#F39F46` / `#E28B34` | `#B16528` / `#D28134`; `#D88A43` / `#693817` |
| Peg block (close-up A, wood) | `#A1571D` (26°, .82, .63) | `#EF953A` | `#7B4218` |
| Bolt heads: close-up B / close-up A / palette render | `#474E56` (212°, .17, .34) / `#4E5354` / `#474D55` | `#5A666E` / `#5E5C5E` / `#606770` | `#262829` / `#292120` / `#25282E` |
| Bolts at hero size (mixed with wood): f34 / front | `#605049` / `#53483F` | | |
| Cast shadow (not modelled) / paper | `#C8C6C5` / `#FBF8EE` | | |

### 5.3 How the colour works

- **One timber:** every wooden piece (planks, cleats, legs, ties, braces, crossbar, stubs, pegs, bench and stool parts) on
  `m067_wood`. The sheet's three values (lit tops 39 %, mid faces 26 %, shade 35 % in the f34) are **lighting**: the dark
  undersides, end faces, shaded legs and the front cell's dark band and braces are never painted darker.
- **Per-piece Tint 0.05** (every plank piece, leg, cleat its own seed): the sheet's plank-to-plank value steps (f34 table
  top `#ED9A42` vs bench top `#F9A648` vs stool top `#E49848`).
- **Positional bands (blend partners, 3 steps):** on each top and seat plank, the last 0.35 at one end (chosen by a seeded
  coin per plank, by position along the plank) blended one step (≈ 20 %) toward `m067_wood_deep` (the sheet's darker
  plank ends and streaks); on one plank in three, a 0.6-wide band near mid-length blended one step toward
  `m067_wood_light` (the lighter streaks). Legs: the lowest 0.25 blended one step toward `m067_wood_deep` by height
  (ground grime), **never more**: the legs must not read darker than the planks at the same lighting (M048 finding 7).
- **Pegs and stubs:** `m067_wood` (close-up A's peg is the same wood, `#A1571D` in shade).
- **Bolts:** `m067_iron`, hard edge against the wood.
- **Never by facing.** No face gets a colour because of which way it points (`K.check` facing correlation < 0.5).
- **Hues stay together:** wood 26–31°, s 0.70–0.84 rendered; wood_deep 23–27°; wood_light 29–32°; iron cool blue-grey
  (h 200–220°, s 0.10–0.20).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians; `K.sample` kind `"brown"` for the wood keys, `"stone"` for `iron` (check
with `M.raw_sample` on the swatches too). Start the wood from M052's calibrated `m052_wood #B26C2B` (hue 29°: next to
ours).

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m067_wood` | front_sheet face median `#B8671F` ± 12 (front top face `#BE6D22`, bench face `#BB6A21`, bench leg `#B8671E`; swatch S1 `#B56420`); top-render median `#CC7B2D` ± 12; f34 top surface `#ED9A42` ± 15 | 26–31°, 0.72–0.84 | every wooden piece | rough 0.8, low spec |
| `m067_wood_light` | `#E59241` ± 12 (S2; lit tops are lighting, so this is only a blend partner) | 28–32°, 0.68–0.76, lighter than wood | light streak bands | rough 0.8 |
| `m067_wood_deep` | `#8E4A18` ± 12 (between the mid faces and the shade quartiles) | 23–27°, 0.78–0.86, v ≤ 0.58 | plank-end bands, leg feet (blend only) | rough 0.85 |
| `m067_iron` | `#474E56` ± 10 (close-up B, palette render) | h 200–220°, s 0.10–0.20, v 0.30–0.38 | bolt heads | rough 0.45, metal 0.5 |

**Calibration warnings:**
- **Orange timber, not red and not brown-grey** (W08 "slightly red" / "flat orange"; W11's `#A2622A` read browner than
  this sheet): hue 26–31°, saturation ≥ 0.70 on the front render.
- **Lit tops must not blow out** (M052 finding 4): the f34 top median ≤ v 0.96, R not clipped; target `#ED9A42`.
- **The legs and undercarriage read as the same wood** (M048 finding 7): front_sheet bench-leg median within 15 of the
  bench-face median.
- **Bolts dark slate, cool, not black and not warm grey:** v 0.30–0.38 rendered on `plank_cu`; at hero size they mix to
  the f34's `#605049`.
- **The blend partners must be a real step** (M050 finding 6: a 1-unit "lighter field" was invisible): wood_light and
  wood_deep each ≥ 25 units from wood in at least one channel, bands visible in the top render.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Planks:** by distance along the plank from the chosen end (deep band) or from the band centre (light band).
- **Legs:** by height (feet → body), 3 steps over z 0–0.25.
- **Hard edges only** where materials meet: iron | wood.

### 5.6 Texture (Tint) and finish

- **Tint:** 0.05 per wooden piece (broad, per piece, never per triangle); bolts 0.02.
- **Finish:** wood matte (rough 0.8: the sheet's soft bevel highlights), iron rough 0.45 / metal 0.5; no emission.

### 5.7 Re-measure (final renders against the sheet, same masks)

- **Wood:** front_sheet W median within 12 of `#B4641E`; top-render W median within 12 of `#CB7A2D`; f34 W median within
  15 of `#BE6D29`; f34 lit quartile within 15 of `#F9A748`, shade quartile within 15 of `#643412`.
- **Value shares** per §2.9 (f34 lit / mid / shade 39 / 26 / 35 ± 10).
- **Iron:** `plank_cu` bolt median within 12 of `#474E56`.

## 6. Joins and contact (no floating pieces, no buried pieces)

- **Shells:** every plank piece, leg, cleat, tie, stub, peg, diagonal, crossbar, knee brace, bench cleat, stretcher,
  apron and bolt head is its own closed shell, all in one hero object.
- **Chain to the ground:** legs → ground; cleats → legs; top planks → cleats; crossbar → top underside and cleat faces;
  crossbar stubs → cleat outer faces; ties → legs; tie stubs → front legs; pegs → stubs; diagonals → legs, ties and
  cleats; knee braces → ties and crossbar; bench cleats → bench legs; bench planks → bench cleats; stretchers and aprons
  → legs; stool planks → stool legs and aprons; bolts → their faces.
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**. A shell floats if its nearest distance
  to every other shell and the ground is > 0.03, or if it doesn't chain to the ground. The new risks: the stubs and pegs
  (they sit on faces, they don't pass through), the knee braces' cut ends, the ties between splayed legs (the wedge gap
  must close to ≤ 0.03 at the nearest point), bolts on chamfered edges.
- **Buried shells:** nothing more than 0.05 inside anything beyond its stated seat (bolts 0.03, everything else touching).
  **No through-tenons modelled as one bar through a member** (close-up A's joint is body + stub on the face). Ray parity
  against the planks, legs, cleats and crossbar as solids after the final placement step (`m047._Solids`,
  `m050.buried_report`).
- **No intersections between pieces** (bench legs vs trestle feet ≥ 0.25 apart; knee braces vs diagonals ≥ 0.1).
- **Knee-room and walk reports:** §2.8, minimum clearances printed.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.
- **Winding:** 0 errors per shell, checked with a parity ray test, not only the signed volume (044's wedge back face).
- **Parts:** each exported part self-contained (the Trestle with its stub, peg and bolts touching; the Crossbar with its
  stubs; the Bench and Stool complete) and **square to its axes** (M050 finding 7: no inherited yaw or jitter on a part
  with box collision).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing emissive, no light, fire, smoke, dust or sparkle. The cast shadows and the bevel
highlights are the illustration's lighting.

- **Stage 5 (lighting): skipped**, recorded. No emissive faces. Studio notes (Requires Manual Validation): the top and seats
  read light orange in daylight with darker undersides from shadow, not paint; the bolts read as dark dots at gameplay
  distance.
- **Stage 6 (VFX): skipped**, recorded. 0 sockets; the export STATS line must report 0.
- **Collision (decision §8.11):**
  - **Hero `precise`** (PreciseConvexDecomposition): the top, benches and stool are solid and standable; the 0.39 bench
    gaps stay closed or open, either is harmless. **Requires Manual Validation in Studio:** a default character can sit at
    each seat point (Studio `Seat` parts placed from the stored points), its legs don't snag on the trestles or the
    crossbar, and it can jump onto the top. Fallback: hero `none` plus Studio boxes (top, two bench boxes, stool box,
    two trestle boxes).
  - Parts: `TrestleTableSetTable` `box`; `…Top` `box`; `…Trestle` `hull`; `…Crossbar` `box`; `…Bench` `box`; `…Stool`
    `box`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched every `"name"` in `art/roblox/kit/**/manifest.json` and the repo text for Table, Bench,
Stool, Trestle, Seat, Picnic, Furniture, Plank and the candidates:
- **W11:** `TableAndSeating`, `TableAndSeatingBenchSeat`, `…Crossbar`, `…LongBench`, `…Stool`, `…TableTop`, `…Trestle`,
  `…Workbench` (this sheet's old version). **W10:** `CampAwningTableSet`. **Other:** `FortWorkshopWorkTable`,
  `DailyItemsToolStand`, many `…Plank` names (`BoardwalkFloorPlank`, `TimberBoardwalkFloorPlank`, `DockDeckPlank`, …).
  **M066 (spec, not yet exported):** `CanvasShelterTable`, `…Bench`, `…Stool`.
- **`TrestleTableSet` and every `TrestleTableSet…` part name below, and `m067`, occur nowhere** in the manifests or the
  repo text. `CampAwningTableSet` contains "TableSet" but no owned name is a prefix or substring of `TrestleTableSet`.

| Object | Part | Why |
| --- | --- | --- |
| `TrestleTableSet` | hero: top, 2 trestles, crossbar, 2 knee braces, 2 benches, stool, 30 bolts | W11 owns `TableAndSeating*`; the sheet's construction |
| `TrestleTableSetTable` | the assembled table without seating (top, trestles, crossbar, braces, its bolts) | the set's main reusable piece |
| `TrestleTableSetTop` | "Table Top (Planks)": seven pieces + 4 bolts | the label |
| `TrestleTableSetTrestle` | "Leg / Trestle": cleat, legs, tie, stub, peg, diagonal, 7 bolts | the label |
| `TrestleTableSetCrossbar` | "Crossbar": body + stubs | the label |
| `TrestleTableSetBench` | "Bench Seat (Planks)": the whole bench (the label points at it) | the label |
| `TrestleTableSetStool` | "Stool" | the label |

- Palette keys `m067_*` (§5.4). Collection `Kit/M067 Table and Seating`. Sockets: none. Stored points `m067_offset`,
  `m067_centre`, `m067_seat_f1`, `m067_seat_f2`, `m067_seat_b1`, `m067_seat_b2`, `m067_seat_stool` (+ facings) on the
  hero; seat points on the Table, Bench and Stool parts.
- Bench seat points sit at x ±1.20 (2.40 apart) so the seated-legs proxy clears the trestle legs (§2.8).

**Decisions needed (a recommendation each):**
1. **Size (§1.1, §3.2):** **table top at 2.60, 6.00 × 2.82, planks 0.44; seats at 1.50; benches 5.80 × 1.20; stool 1.40;
   hero ≈ 8.75 × 6.06 × 2.64** (recommended: 066's heights, the f34 and top cell's length). Alternative: L 5.0 (front
   cell).
2. **Build frame and origin (§1.1, §2.10):** **front −Y (the near bench), stool at −X front; origin at the bbox bottom
   centre with the offset, centre and seat points stored** (recommended).
3. **Seat height (§3.8):** **1.50, the kit's seat height (066, side cell)** (recommended). Alternative: 1.32 (front cell).
4. **Stool position (§3.4):** **(−4.95, −1.30), square to the table** (f34 and r34) (recommended). Alternative: the top
   cell's +X end.
5. **Undercarriage (§3.6):** **crossbar under the top at y 0 with tenon stubs past both trestles; two 42° knee braces to
   the low ties; no aprons, no low crossbar, no post** (recommended). Alternative: front and back aprons.
6. **Trestle splay (§3.7):** **10°, feet flush with the top's edges** (recommended). Alternatives: 4° or 16°.
7. **Top planks (§2.3, §3.9, §3.10):** **four rows, three butt joints (R1 0.18 L, R3 0.85 L, R4 0.36 L), gaps 0.06,
   chamfers 0.04** (recommended).
8. **Benches (§2.4, §3.5, §3.12):** **two planks with one joint, cleats, legs splayed 5° (X) and 4° (Y), stretchers; at
   y ±2.40** (recommended).
9. **Stool (§2.5, §3.11):** **three planks, four 7°-splayed legs, aprons on four sides, stretchers on two** (recommended).
   Alternative: two planks (exploded).
10. **Bolts and pegs (§2.6, §3.13):** **30 dark slate square heads; two peg blocks on the tie stubs; the crossbar stubs as
    the "square pegs" of the exploded and close-up C** (recommended).
11. **Collision (§7):** **hero `precise` with a Studio seating check (fallback `none` + Studio boxes); Table / Top /
    Crossbar / Bench / Stool `box`, Trestle `hull`** (recommended).
12. **Comparison cameras (§2.9):** **`front_sheet (0, 0)`, `rear_sheet (180, 0)` (stool hidden) and `side_sheet (90, 0)`
    govern the levels; `f34_sheet (−35, 20)` (probe az −30 … −45, e 15–25) governs the read and layout; `r34_sheet (145,
    20)` and `top` content; close-ups `join_cu`, `tie_cu`, `plank_cu`, `under_cu`, `stool_cu`, `seat`, `thumb`, `spin`;
    parts and exploded shots; scale shot. Floor hidden in every `*_sheet` render** (recommended).
13. **Budget (§4.3):** **full asset: ceiling 4000, plan 1700–2300; every part under 1000; headroom only for end chamfers
    and bolt bevels** (recommended).
14. **Exports (§8 table):** **the hero plus six parts: Table, Top, Trestle, Crossbar, Bench, Stool** (recommended).
    Alternative: drop Top and Crossbar (four parts).
15. **Colour (§5):** **one timber `#B8671F` with per-piece Tint 0.05 and positional deep / light bands; slate bolts
    `#474E56`; by role and position, never by facing; S3–S5 unused** (recommended).
16. **Stages 5 and 6:** **skipped and recorded; 0 sockets** (recommended).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **The old set's failures (W11 / MODEL_PROGRESS row 87: "thin top, straight legs (ref trestle); thin benches";
   CHECKLIST 5.5/10; goals: "hero squat", A-frame "only obliquely", nails "oversized").** Top 0.44 thick, seats 0.44;
   A-frame splay 10° that reads in the f34 and side; braces visible in the front view; bolt heads 0.18.
2. **Floating or buried pieces** (STAGES; 035 / 036 round 1; 046; M051 findings 2–3: sinks beyond the stated value). Stubs
   and pegs sit on faces, never through members; braces' cut ends touch; ties close their wedge gap; bolts sunk 0.03.
   Count: floating 0, buried 0, and report the worst sink per kind.
3. **Winding and non-planar faces** (044; M051 finding 8; M052's stringers). Sheared legs keep horizontal caps; brace ends
   planar; 0 winding errors per shell by parity.
4. **A plank top that reads as one slab** (M050 finding 2; M052 finding 1). Four separate rows with 0.06 gaps and 0.04
   chamfers so a dark V shows between them in the top and f34 renders at sheet scale; the joints visible.
5. **Legs or undercarriage painted dark** (M048 finding 7). The sheet's dark undercarriage is shade; same key, the feet
   at most one step deeper.
6. **Red, brown or flat-orange wood** (W08; W11 `#A2622A`). Hue 26–31°, s ≥ 0.70; the lit tops orange `#ED9A42`, not
   cream and not clipped (M052 finding 4).
7. **Colour by facing** (042 ruling; 054 m9). Lit tops, dark sides and end faces are light. `K.check` facing correlation
   < 0.5.
8. **Invisible or hard colour bands** (M050 finding 6; M051 finding 5; M052 finding 3). Blend partners ≥ 25 units away,
   blended over three steps by position.
9. **Egg or blob shapes where the sheet is square** (M034 / M037). Crisp boxes with 0.04 chamfers on the long edges only
   (WorldModeling §13.1: 0.02–0.05); no smooth shading, no subdivision.
10. **Seats that don't work** (gameplay). Seat tops level at 1.50 ± 0.01, the seat points stored with facings, the knee
    room printed; collision validated in Studio.
11. **Parts that don't read like their cells or carry the hero's jitter** (056 / 058 blockers; M050 finding 7). Each part
    rendered beside its exploded cell; parts square to their axes.
12. **Proportions from a single stylised cell** (§3.2–§3.8). The f34 and top set the length, the side sets the trestle, the
    front sets the levels and fractions; front / rear W : H and side W / H recorded, not scored.
13. **Noise for detail** (model notes; WorldModeling §18 "tiny details vanish"). No modelled cracks or grain; check the
    `thumb` render: plank gaps, trestles, bolts as dots.
14. **Names and scope.**
    - No `TableAndSeating*`, `CampAwning*`, `CanvasShelter*` names.
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit the frozen shared helpers (`kit_models.py`, `kit_mcp.py`, `build_kit.py`, `lib/vfx.py`) or other models'
      builders; import from the committed ones (`m047`, `m048`, `m050`, `m052`, `m038`); don't touch other models'
      collections.

## Open questions for the main session

1. **Table length (§3.2):** 6.00 (f34 and top cell) or 5.0 (front cell)? The orthos disagree by up to 50 %; the
   recommendation keeps the front and rear cells' W : H as recorded misses.
2. **Seat height (§3.8):** keep the kit's 1.50 (066, the side cell) against the front cell's 1.32?
3. **Stool position (§3.4):** the hero views' front-left (recommended) or the top cell's +X end? The front and rear cells
   draw no stool at all.
4. **Undercarriage (§3.6):** is the recommended reading (crossbar under the top, knee braces to the low ties, no aprons)
   acceptable, or should the front cell's band be a pair of aprons? The exploded's square post at the crossbar's end is
   left out.
5. **Trestle splay (§3.7):** 10° (recommended), 4° (side cell) or 16° (top cell)?
6. **Stool seat (§3.11):** three planks (f34, top) or two (exploded)?
7. **Swatches S3 `#B09584`, S4 red `#D14137`, S5 cream `#FAE4BD` (§3.13):** confirm they are unused. If S3 is meant as the
   bolt colour, the bolts would turn pale warm grey, unlike every drawn bolt.
8. **Parts list (§8):** six parts, or four (drop Top and Crossbar)? Should the 066 shelter later reuse
   `TrestleTableSetTable` / `…Bench` / `…Stool` in place of its own furniture (the heights already match)?

## Decisions (main session, 2026-11-01)

1. **Table length 6.00.** The f34 and the top cell agree; they are the views the hero is judged on. The front and rear
   cells' W : H stays a recorded miss, not a blocker.
2. **Seat tops 1.50, table top 2.60**, matching 066 so the kit's furniture shares one scale. The front cell's 1.32 is a
   recorded miss.
3. **Stool front-left** at (−4.95, −1.30), as both three-quarter views show it. The top cell's +X end is a sheet
   inconsistency.
4. **Undercarriage as recommended:** crossbar under the top with square ends past both trestles, knee braces at 42° to
   the low ties, no aprons. Leave out the exploded view's square post at the crossbar end.
5. **Trestle splay 10°.**
6. **Stool seat of three planks** (f34 and top agree; the exploded cell is the outlier).
7. **Swatches S3, S4 and S5 are unused.** Bolt heads stay dark slate `#474E56`, as every drawn bolt.
8. **Six parts** (Table, Top, Trestle, Crossbar, Bench, Stool). 066 keeps its own furniture for now; reusing this set's
   parts there is a later option, not part of this model.

## Paused (2026-11-01)

Paused by the main session (user request) before the first build.
- **Done:** read the spec, the decisions, STAGES, the skill and the sheet. The first full draft of
  `art/blender/kit/mcp/m067.py` is written: every piece builder (plank, leg, trestle, crossbar, knee brace, bench, stool,
  `_bolt`), the hero and six parts, the stage 2–3 pass, the contact, bury, winding, seat-level, knee-room and walk reports,
  the render set and the `measure()` masks.
- **Half done:** the builder has **never been run**, so it is untested. No geometry is in the wip file, there are no
  renders, no audit numbers and no calibration. The `PALETTE` hexes are starting values, not calibrated. Stage 1–6
  sections are not yet recorded in this spec.
- **Next:** start the session on port 9879 with the wip file and run `m067.build(render=False)`. Fix the errors and
  then `problems`; check the tris (plan about 2300–2600 with the colour-band rings). Save the wip, then run
  `calibrate()`, render, and compare each view and part with the sheet using `measure()`. Record stages 1–6 here and
  add "Modeller's notes for the verifier".
- **Resumed 2026-11-02** by a new modeller (background Blender, port 9879, `art/blender/assets/kit/wip/M067.blend`).
  Stages 1–6 are recorded below.

## Stage 1 — Modelling

The draft builder ran first time with four problems, all fixed in `m067.py`:
1. **Table part 1204 tris (over 1000).** The colour-band rings were the cost: every band edge is a full 8-sided ring
   (16 tris), and the top's seven pieces carried 352 tris of rings. Stage 4 below settles the bands; the Table part is
   now 980.
2. **Crossbar part: the stubs were unchained.** In the hero the stubs sit on the cleats' outer faces; alone, the cleat
   gap left them floating. `crossbar(alone=True)` (the part only) runs each tenon stub from the body's end face out to
   its bolt, the exploded cell's "pin at its end". The hero keeps body + stubs on the cleat faces (no bar through a
   cleat).
3. **Hero H 2.67 against the target 2.64.** The top bolts are 0.05 proud with a 0.02 dome, as §1.4 sets them, so the
   bbox top is 2.67. The target in `TARGET_SIZE` is now 2.67 ± 0.02; the table top stays 2.60.
4. **Stool turned a quarter.** The draft ran the stool's planks along X, so the f34 showed three plank ends on the −X
   face and one long plank side on the front. The f34 (`z_f34_stool.png`, the "narrow / wide / narrow" front face) and
   §3.11 show the plank ends on the front face: `stool()` now builds `_stool()` inside a 90° frame. The stool is
   square, so its size, legs, aprons, bolts and seat point are unchanged; the cross seam now runs left to right across
   the middle plank, as on the f34.

Also: the f34 comparison camera is **(−30, 20)**, probed over az −25 … −40 × e 15 / 20 (§2.9): W : H 1.79 there
(sheet 1.86, target 1.80 ± 0.12); (−35, 20) gave 1.68, at the edge. The trestle part's shot looks from **(60, 15)**: from
the shared (−20, 15) the A-frame (in the YZ plane) is edge-on.

**Built (build frame; every piece its own closed shell; 92 shells in the hero):** the top's seven pieces (four rows, joints
R1 x −1.92 / R3 +2.10 / R4 −0.84), two A-frame trestles (cleat, two 10.06° legs, tie, tie stub + peg on the front leg,
diagonal at 46°), the crossbar with its two stubs, two knee braces at 42.8°, two benches (three seat pieces, two cleats,
four legs splayed 5° / 4°, two stretchers each), the stool (four seat pieces, four 7° legs, four aprons, two stretchers),
30 bolts.

**Against the sheet (front / side fractions are by construction, checked on the renders):**

| Check | Target | Ours |
| --- | --- | --- |
| Top | 6.00 × 2.82, top face 2.60, planks 0.44 | 6.00 × 2.82 (bbox 6.05 with the ±0.03 end jitter), 2.600, 0.44 |
| Front: top thickness / band / leg centres | 0.17 H / 0.72–0.83 H / ±0.73 | 0.169 / 0.715–0.831 / ±0.733 |
| Front: brace upper ends / angle | ±0.16 L / 42 ± 6° | ±0.167 L / 42.8° |
| Front: bench length / bench-leg centres | 0.967 L / ±0.84 | 0.967 / ±0.845 |
| Side: cleat / leg centres / tie | 0.86 W / ∓0.30 W / 0.15–0.29 H | 0.862 / ∓0.305 / 0.154–0.288 |
| Top: joints / bench gap | 0.18 / 0.36 / 0.85 L; 0.15 W | 0.18 / 0.36 / 0.85; 0.39 = 0.138 W |
| Splay: trestle / bench / stool | 10° / 5°, 4° / 7° | 10.06° / 5°, 4° / 7° |
| Seat tops (benches, stool) / table top | 1.50 ± 0.01 / 2.60 | 1.500–1.500 / 2.600–2.600 |
| Stool | (−4.95, −1.30), 1.40 square | (−4.95, −1.30), 1.40 (bbox 1.58 with the splayed feet) |
| f34 W : H | 1.80 ± 0.12 (sheet 1.86) | 1.79 at (−30, 20) |
| Recorded, not scored: front / rear W : H, r34 W : H | sheet 1.86 / 1.68 / 1.51 | 2.28 / 2.29 / 1.65 |

**View by view** (renders in `art/blender/renders/models/M067/`, all in `M067_views.png`):
- **f34_sheet:** the long four-plank top over the left trestle's A, the right knee brace under the top, the near bench
  poking out right, the far bench out left, the stool front-left square to the table with three plank ends on its front
  face. Matches the cell's layout; the sheet's top looks a little deeper on screen (its mild perspective).
- **r34_sheet:** the stool at the far right behind the near bench, the +X trestle's A and diagonal, the far bench out
  left: the same layout as the cell.
- **front_sheet / rear_sheet** (stool hidden): top, cleat-end band with bolts, legs, the V of the knee braces from near
  the middle down to the legs, the bench in front with bolts over each frame. Our table is longer for its height (the
  decided L 6.0, §3.2).
- **side_sheet:** four equal plank ends, the cleat with three bolts, the splayed legs, the diagonal from the front
  (screen-left) leg low up to the centre, the tie, the tie stub and peg past the front leg, both benches end-on. The
  sheet's legs are nearly vertical (10° splay decided, §3.7), and our knee braces show end-on as a vertical bar at the
  centre, which the sheet's side cell doesn't draw (they are the front cell's V; §3.6 decision).
- **top_sheet:** four rows with the three joints, bolt dots on R1 and R4 over the trestles, the benches with a seam and
  an end dot each, the stool off the −X end (the sheet's top cell puts it off the +X end, §3.4).
- **Parts against their exploded cells:** `part_top` (four rows, staggered joints), `part_trestle` (A-frame, cleat with
  bolts, diagonal, tie with the pegged stub, bolts near the feet), `part_crossbar` (long square beam with a tenon and
  bolt at each end), `part_bench` (two-plank seat with one joint, splayed frames, stretchers), `part_stool` (three-plank
  seat, splayed legs, aprons, stretchers), `part_table`, and `exploded.png` laid out like the cell.
- **Close-ups:** `join_cu` (cleat end and bolt, crossbar stub with its bolt; close-up A), `tie_cu` (the pegged tie stub and the leg bolt, from a fixed camera in the gap past the near bench's −X end: the
  bench hides the stub from every orbit angle),
  `plank_cu` (plank ends with V gaps and chamfers over the cleat end face and bolt; close-up B), `under_cu` (from below,
  dark: the studio has no light from below), `stool_cu`, `seat` (seated proxies at all five points, front and side),
  `thumb_sheet` (the f34 at 140 px: top, trestles, benches, stool and the plank gaps still read), `M067_spin.png` (eight
  azimuths at e 10: nothing floats, every leg reaches the ground), `scale.png`.

## Stage 2 — Optimisation and cleanup

| Object | Tris | Size (studs) | Shells |
| --- | --- | --- | --- |
| `TrestleTableSet` (hero) | **2540** / 4000 | 8.77 × 6.14 × 2.67 | 92 |
| `TrestleTableSetTable` | 980 | 6.05 × 2.99 × 2.67 | 44 |
| `TrestleTableSetTop` | 380 | 6.05 × 2.82 × 0.51 | 11 |
| `TrestleTableSetTrestle` | 248 | 0.57 × 2.99 × 2.16 | 13 |
| `TrestleTableSetCrossbar` | 80 | 5.59 × 0.36 × 0.30 | 5 |
| `TrestleTableSetBench` | 524 | 5.80 × 1.30 × 1.57 | 15 |
| `TrestleTableSetStool` | 512 | 1.58 × 1.58 × 1.50 | 18 |

- Hero tris by kind: planks 1020 (17 pieces, the band rings included), legs 704, bolts 420, the rest 396. The headroom
  is unspent (no noise, §4.3).
- Every object: 0 non-manifold edges and verts (bowties), 0 boundary, wire or loose elements, 0 zero-area faces, 0
  n-gons, 0 duplicate verts, normals outward, transforms applied, origin at the bbox bottom centre. Per shell: 0 winding
  errors, 0 faces failing the parity test (a point 0.002 out along each normal must be outside by ray parity), 0
  self-intersections, positive volume. 0 non-planar quads; the smallest corner on any face 33.7°.
- **Contact** (`contact_report`, tolerance 0.03): 0 floating, 0 unchained, worst gap 0.000 in every object; hero feet at
  z 0.000.
- **Bury** (`bury_report`, ray parity, limit 0.05): 0 buried, 0 hidden in every object; the deepest sink of any kind is
  the bolts' stated 0.03.
- **Clearances:** knee braces to the trestle diagonals 0.50; bench legs to the trestle (nearest: the tie stub) 0.235;
  benches to the top 0.81 (3D) / 0.39 (plan); stool to the near bench 1.35, to the table end 1.25.
- **Seats** (`seat_report`): bench and stool plank tops 1.500–1.500, table top 2.600–2.600; **knee clearance 0.15** at
  all four bench points (target ≥ 0.10); walk loop clearance 0.304.
- **Stored points** (hero; build frame = object + `m067_offset` (−1.357, 0, 0)): `m067_seat_f1` (−1.20, −2.40, 1.50) and
  `_f2` (+1.20, −2.40, 1.50) facing (0, 1, 0); `_b1` / `_b2` at y +2.40 facing (0, −1, 0); `m067_seat_stool` (−4.95,
  −1.30, 1.50) facing (1, 0, 0); `m067_centre` (1.357, 0, 0) in object space. Re-checked after the origin move. The
  Table part stores the four bench points, the Bench part two, the Stool part one (relative to each part's origin).

## Stage 3 — UV

`M.smart_uv` (angle-based, angle 45°, margin 0.008) plus the overlap pass (`_uv_unfold`, 0 faces needed cutting). Every
object: 0 overlapping pairs, 0 flipped, smallest island gap 0.016, border 0.008, texel density ratio 1.0, conformal
stretch p95 ≤ 1.024. Hero 652 islands. The exporter writes its own palette UVs.

## Stage 4 — Materials, colour and texture

**Calibration.** `m067.calibrate()` (the `K.calibrate` dome, targets §5.4) gave wood `#92591E` (rendered 180, 101, 30),
light `#B97C3E`, deep `#734218`, iron `#49525F` (71, 78, 86). On the hero those woods rendered a step too dark (f34
median `#A25B1B` against the sheet's `#BE6D29`, front `#9E5819` against `#B4641E`): the dome is lit more fully than the
table's faces. As for M052, the final wood hexes were then set from the hero renders: the three wood keys scaled in
linear light by the measured render / sheet ratio (R 1.33, G 1.4, B 1.7), and the light and deep keys nudged back into
their hue / saturation bands. Iron keeps the dome value's finish: on `plank_cu` the bolt heads render `#474C55` (71, 76,
85) against the target `#474E56` (rough 0.45, metal 0.5; rough 0.6 / metal 0.2 rendered too pale, (80, 85, 92)).

| Key | Final hex in `PALETTE` | Hue / sat | Finish |
| --- | --- | --- | --- |
| `m067_wood` | **`#A66829`** | 30°, 0.75 | rough 0.8, low spec |
| `m067_wood_light` | **`#D48F44`** | 31°, 0.68 | rough 0.8, low spec |
| `m067_wood_deep` | **`#844A1A`** | 27°, 0.80 | rough 0.85, low spec |
| `m067_iron` | **`#49525F`** | 215°, 0.23 | rough 0.45, metal 0.5 |

Blend keys in use (`K.mix_key`): `wood_x_deep_24` / `_44` (plank-end band, two steps), `wood_x_deep_30` (leg feet),
`wood_x_light_18` / `_36` (bench streak, two steps).

**Re-measured** (`m067.measure()`, the §1.2 masks, final renders):

| View | Sheet wood median / lit Q / shade Q | Ours | Value shares lit / mid / shade (sheet → ours) |
| --- | --- | --- | --- |
| f34_sheet | `#BE6D29` / `#F9A74A` / `#643411` | `#BC6D26` / `#D57F34` / `#9B581F` | 40 / 27 / 33 → 3 / 86 / 11 |
| r34_sheet | `#B96927` / `#F8A547` / `#643411` | `#AB6423` / `#D68138` / `#8C511B` | 39 / 28 / 33 → 4 / 82 / 13 |
| front_sheet | `#B4641E` / `#DA8B35` / `#5F2F0D` | `#B66823` / `#C16F26` / `#5A310D` | 14 / 57 / 29 → 1 / 64 / 35 |
| rear_sheet | `#B5641D` | `#A96322` | 13 / 59 / 28 → 0 / 89 / 11 |
| side_sheet | `#A45D20` | `#8D521B` | 7 / 62 / 31 → 0 / 57 / 43 |
| top_sheet | `#CB7A2D` | `#D37B2B` | 17 / 76 / 7 → 5 / 87 / 8 |

- Medians: f34 within 3, front within 5, top within 8 (targets 15 / 12 / 12). Hue 28–29°, saturation 0.79–0.81 in
  every view (sheet 27–29°, 0.76–0.83): orange, not red or brown.
- **Not met: the value spread.** The sheet's lit quartile is 36 units brighter and its shade quartile 55 darker than ours
  in the f34 (lit share 40 % against 3 %). That is the illustration's hard key light against the kit studio's soft
  light; the only way to reach it here would be painting tops lighter and sides darker, which is colour by facing
  (forbidden). Recorded, as in M052. The side view's median (`#8D521B` against `#A45D20`) is the same effect: its faces
  look at +X, away from the studio key.
- K share (dark pixels) 0.7–1.4 % against the sheet's 1.9–5.5 %: our bolt heads render v ≈ 0.30–0.33, just over the
  K threshold (the sheet's own bolt median `#474E56` is v 0.34 too); the sheet's K also counts its ink outlines.

**Colour by role and position only, never by facing.** No paint choice reads a normal. Measured on the hero's 1060 wood
faces: the correlation between each face's key luminance and its normal is x 0.00, y 0.00, z 0.12 (|n| components
−0.06 … 0.02), far under 0.5.
- Every wooden piece is `m067_wood` with a **per-piece Tint ±0.05** (seeded by the piece's name): the plank-to-plank
  value steps of the sheet.
- **Plank-end bands:** on each plank piece with a band, the last 0.35 at one end (seeded coin) in two steps toward
  `wood_deep` (44 % within 0.15 of the end, 24 % to 0.35), by distance along the plank. Top: R1b, R2a, R3a, R4b (the
  four pieces longer than 2.5); benches: all three seat pieces; stool: all four seat pieces.
- **Light streak:** a 1.3-long streak near mid-length on each bench's outer plank, two steps toward `wood_light` (36 %
  within 0.35 of its centre, 18 % to 0.65). **None on the top** (deviation from §5.3): a two-step streak costs 64 tris
  per plank, and the Table part (top + trestles + crossbar + braces) must stay under 1000 (it is 980). A one-step streak
  (32 tris) rendered as a hard light rectangle, so it was dropped rather than kept hard.
- **Leg feet:** the lowest 0.25 of every leg 30 % toward `wood_deep`, by height (one step; the legs still read as the
  same wood as the planks).
- **Bolts:** `m067_iron`, Tint ±0.02, hard edge against the wood (two materials).
- The first band strengths (t 0.12–0.24) moved a band only 4–8 units with the calibrated partners: invisible (M050
  finding 6). The final 0.24–0.44 moves it 8–15 units: visible on `top_sheet` and `plank_cu`, still soft.
- Finish: wood matte (rough 0.8 / 0.85, low specular), iron rough 0.45 / metal 0.5, no emission.

## Stage 5 — Lighting

**Skipped.** The sheet shows nothing emissive and no light source; its highlights and cast shadows are the
illustration's lighting. 0 glow keys (export stats). Studio notes (Requires Manual Validation): in daylight the top and
seats should read light orange with darker undersides from shadow, not paint; the bolts read as dark dots at gameplay
distance; a default character can sit at each stored seat point (Studio `Seat` parts) and jump onto the top.

## Stage 6 — VFX

**Skipped.** No smoke, dust, sparkle or glow on the sheet. 0 sockets on every object (`export_stats`: `vfx_sockets` 0,
`glow_keys` []).

## Modeller's notes for the verifier

- **Rebuild:** `import importlib, kit_models, m067; importlib.reload(kit_models); importlib.reload(m067); r =
  m067.build()` returns `problems: []` plus `audit`, `contact`, `bury`, `seats` (seat levels, knee room), `walk`,
  `winding`, `bowties`, `thin`, `uv`, `placement`, `export_stats`. `m067.preview()` renders only the sheet views;
  `m067.measure(path, box)` applies the §1.2 masks to a sheet cell or a render; `m067.calibrate()` re-runs the dome.
- **Comparison cameras:** `f34_sheet` is (−30, 20), not the spec's (−35, 20) (probed, Stage 1). `front_sheet` and
  `rear_sheet` hide the stool (the sheet's cells have none).
- **Deliberate differences from the sheet** (all decided or recorded): table L / H longer than the front and rear cells
  (decision 1); seats 1.50 not the front cell's 1.32 (decision 2); stool front-left, not the top cell's +X end (decision
  3); knee braces show end-on in the side view (decision 4); 10° splay where the side cell draws near-vertical legs
  (decision 5); the f34 value spread and K share (studio lighting, Stage 4).
- **Budget-driven colour choice:** no light streak on the table top and no end band on its three short pieces (R1a,
  R3b, R4a), so the Table part stays at 980 / 1000. The hero alone has room for both (2540 / 4000) but would then differ
  from its parts.
- **The Crossbar part differs from the hero's crossbar on purpose:** alone, its tenon stubs run from the body's end
  faces (through where the cleats would be), so the part is one chained piece; in the hero the stubs sit on the cleats'
  outer faces.
- **Stool orientation:** the stool is built turned 90° (planks front to back); its seat point still faces +X (toward the
  table end).
- `under_cu` is dark because the studio has no light from below; it shows the plank undersides, both cleats, the
  crossbar and the knee braces, but reads poorly against close-up C.
- Scratch files: `<temp>\build.json` (the last `build()` report), `<temp>\calib\` (dome renders).

## Rulings (main session, 2026-11-02)

1. **Table top bands:** keep it as built. The Table part stays under 1000 with no light streak and no end band on the
   three short pieces; the hero carries the same top, so hero and part match. Per-piece tint separates the planks.
2. **Value spread** (f34 lit / mid / shade 3 / 86 / 11 against 40 / 27 / 33) comes from the studio's soft light; fixing
   it would mean colouring faces by facing, which STAGES.md forbids. Accepted; the verifier judges hue and the medians.
3. **Dark-pixel share and the dark `under_cu`:** studio and ink-outline effects, accepted.
4. **f34 camera at (−30, 20)**, trestle part shot at (60, 15) and the fixed `tie_cu` camera: accepted.

## Stage 7 verification (round 1)

Independent verifier, read-only, background Blender on a copy of the kit file taken after the main session built 067
into it (`build()` not called). Every number below was re-measured with the verifier's own bmesh / BVH / raster code,
and every view was rendered by the verifier into `<temp>\v067\r\` and set beside the matching sheet cell.

**Result: PASS, 8/10.** No blockers.

### Technical (all objects)

| Object | Tris | Size (studs) | Shells | Floating / unchained | Worst gap | Deepest sink |
| --- | --- | --- | --- | --- | --- | --- |
| `TrestleTableSet` | 2540 / 4000 | 8.767 × 6.140 × 2.670 | 92 | 0 / 0 | 0.002 | 0.030 (bolts only) |
| `…Table` | 980 / 1000 | 6.054 × 2.988 × 2.670 | 44 | 0 / 0 | 0.002 | 0.030 (bolts) |
| `…Top` | 380 | 6.054 × 2.820 × 0.510 | 11 | 0 / 0 | 0.002 | 0.030 (bolts) |
| `…Trestle` | 248 | 0.570 × 2.988 × 2.160 | 13 | 0 / 0 | 0.002 | 0.030 (bolts) |
| `…Crossbar` | 80 | 5.590 × 0.360 × 0.300 | 5 | 0 / 0 | 0.002 | 0.030 (bolts) |
| `…Bench` | 524 | 5.800 × 1.296 × 1.570 | 15 | 0 / 0 | 0.002 | 0.030 (bolts) |
| `…Stool` | 512 | 1.580 × 1.580 × 1.500 | 18 | 0 / 0 | 0.002 | 0.030 (bolts) |

- Every object: 0 non-manifold edges, 0 boundary, 0 wire, 0 loose verts, 0 bowtie verts, 0 zero-area faces, 0 n-gons,
  0 duplicate verts, 0 winding errors (edge direction test), 0 negative-volume shells, 0 faces failing the parity test,
  0 non-planar quads, smallest corner 33.7°. Origin at the bbox bottom centre (error 0.0000 on x, y and z), rotation 0,
  scale 1, no modifiers, no custom normals, no unused material slots.
- Bury, by ray parity on every touching pair: the only sinks are the bolt heads' stated 0.03 (and the plank / cleat face
  points under them). No leg, cleat, tie, stub, peg, brace or plank passes into another piece. No shell's centre lies
  inside another shell.
- UV: one `UVMap`. Hero 652 islands; every object has 0 overlapping pixels (2048² raster), 0 flipped faces, smallest
  island gap 0.016, border 0.008 (meets ≥ 0.008), texel density ratio 1.00 (p5 and p95).
- Materials: `m067_wood` `#A66829` (rough 0.8, spec 0.06), blend keys `wood_x_deep_24 / _44 / _30`, `wood_x_light_18 /
  _36`, `m067_iron` `#49525F` (rough 0.45, metal 0.5), all no emission; Tint 0.954–1.047. Correlation between face colour
  and normal: x 0.00, y 0.00, z 0.12, |z| 0.01, so no colour comes from facing.

### Sizes, joinery, furniture use (build frame)

- **Top:** 6.00 (bbox 6.054 with end jitter) × 2.82, every plank top at 2.600 (flat to 0.000), underside 2.16. Every
  plank is 0.44 thick. Joints at R1 −1.92 (0.18 L), R3 +2.10 (0.85 L), R4 −0.84 (0.36 L). Four bolts on R1 and R4 over
  the trestles.
- **Trestles:** legs 0.50 × 0.46 with a 10.06° splay. Tops at y ±0.86 (z 1.86), feet at ±1.19, outer faces ±1.42 (top
  edge ±1.41). Cleat 2.43 × 0.45 × 0.30. Tie z 0.40–0.75. Tie stub y −1.29 … −1.57 with a peg on top. The diagonal runs
  from the front leg on the tie top up to y 0 under the cleat (53°). Six bolts per trestle.
- **Crossbar:** y ±0.18, z 1.86–2.16, between the cleat faces; stubs protrude 0.30, each with a bolt.
- **Knee braces:** 42.8° from (±1.0, 1.86) to the tie top at x ±2.2.
- **Benches:** 5.80 × 1.20 at y ±2.40, seat tops 1.500. Legs splay 5° (X) and 4° (Y). Plan gap to the top 0.39 (0.36 to
  the splayed feet).
- **Stool:** 1.40 square at (−4.95, −1.30), seat top 1.500, legs 7° both ways. It stands 1.25 off the top's end and 1.26
  off the near bench.
- **Bolts:** 30 heads, each 0.18 × 0.18 × 0.10 (0.03 sunk, 0.05 proud, 0.02 dome), all `m067_iron`.
- **Front fractions:** top 0.169 H, band 0.715–0.831 H, leg centres ±0.733, brace upper ends ±0.167 L, bench 0.967 L,
  bench legs ±0.845.
- **Side fractions:** cleat 0.862 W, legs ∓0.305 W, tie 0.154–0.288 H.
- **Top view:** bench gap 0.138 W. Every value is in tolerance.
- **Seat points:** the five stored points (hero object space + `m067_offset` (−1.357, 0, 0)) land at f1 / f2
  (∓1.20, −2.40, 1.50) facing +Y, b1 / b2 (∓1.20, +2.40, 1.50) facing −Y, and the stool point (−4.95, −1.30, 1.50) facing
  +X. The Table, Bench and Stool parts carry their own points, which resolve to the same build positions.
- **Knee room:** box 1.2 × 1.2 × 1.75 from each bench's inner edge toward the table; minimum clearance 0.15 at all four
  points (the trestle leg foot; target ≥ 0.10).
- **Walk-around:** a plan occupancy grid at 0.05, dilated by 0.5 and by 0.8, leaves one connected free region. There is
  no enclosed pocket. The bench gaps (0.39) are closed to a character.
- Hero size: 8.77 × 6.14 × 2.67, matching the spec's 8.75 ± 0.15 × 6.10 ± 0.12 × 2.67 ± 0.02.

### Views against the sheet (masks of §1.2; sheet → ours)

| View | W : H | Wood median | Hue / sat | lit / mid / shade % | K % |
| --- | --- | --- | --- | --- | --- |
| f34 (−30, 20) | 1.858 → **1.787** | `#BE6D29` → `#BB6C25` | 28.2° / .76 → 28.2° / .80 | 40/27/33 → 3/86/11 | 2.4 → 0.9 |
| r34 (145, 20) | 1.514 → 1.653 (155: 1.76) | `#B96927` → `#AB6423` | 28.3 / .77 → 28.4 / .79 | 39/28/33 → 4/82/14 | 2.5 → 1.1 |
| front (stool hidden) | 1.860 → 2.286 | `#B4641E` → `#B66823` | 27.7 / .83 → 28.4 / .81 | 14/57/29 → 1/64/35 | 3.9 → 0.9 |
| rear (stool hidden) | 1.684 → 2.286 | `#B5641D` → `#A96322` | 27.9 / .83 → 28.9 / .80 | 13/59/28 → 0/88/12 | 4.1 → 0.6 |
| side | 1.800 → 2.309 | `#A45D20` → `#8D521B` | 27.0 / .80 → 28.7 / .81 | 7/62/31 → 0/58/42 | 5.5 → 1.6 |
| top | 1.509 → 1.455 | `#CB7A2D` → `#D37B2B` | 29.0 / .78 → 28.6 / .80 | 17/76/7 → 5/87/8 | 1.9 → 0.1 |

- Within tolerance: the f34 W : H (1.80 ± 0.12) and the wood medians (f34 within 4, front within 5, top within 8). Hue
  and saturation are orange in every view.
- Bolt colour: the side-facing heads render `#3B4148`–`#40464E` against the sheet's `#454C54` (palette render) and
  `#464D55` (close-up B).
- The value spread, K share, dark `under_cu` and front / rear W : H are the settled rulings and decisions.
- **f34:** the layout matches:
  - the stool front-left, square to the table;
  - the far bench poking out left, the near bench poking out right;
  - three plank ends with the back row's short piece;
  - the left trestle's A with its diagonal and the right knee brace under the top.
- **r34:** the same layout turned 180°, with the +X trestle's A and diagonal.
- **front / rear:** the top, the cleat-end band with bolts over the legs, the knee-brace V and the bench with face bolts.
- **side:** four equal plank ends, the cleat with bolts, the A legs, the diagonal from the front leg to the centre, the
  tie, leg bolts at tie height, and the benches end-on.
- **top:** four rows, three joints, bolt dots on R1 and R4, the bench seams with end dots, trestle feet at the edges.
- **Parts against their exploded cells:**
  - Top: four rows, staggered joints.
  - Trestle: cleat, legs, diagonal, tie with the pegged stub, bolts near the feet.
  - Crossbar: beam with tenon ends.
  - Bench: two planks with a joint, splayed frames, stretchers.
  - Stool: three planks with a seam, splayed legs, aprons, stretchers.
- **Close-ups:**
  - A: cleat end and bolt, crossbar stub with bolt.
  - Tie: stub through the front leg, peg block on top, leg bolt.
  - B: chamfered plank ends with gaps over the cleat end and its bolt.
  - C: dark from below (ruling 3).
- Spin (eight azimuths at e 10): every leg on the ground, nothing floats. Thumb (170 × 140): the table, trestles, benches
  and stool read.

### Blockers

None.

### Minors

1. **Upward-facing bolt heads glint pale (shows).** The four table-top bolts and the bench seat-seam bolts render
   `#DBE0E7`–`#FFFFFF` in the r34 and `#5D646E`–`#858D99` in the f34. Every drawn bolt on the sheet is dark slate
   (`#454C54` / `#464D55`). The cause is the iron's rough 0.45 / metal 0.5 picking up the studio's sky. Fix if wanted:
   iron rough about 0.7 and metal about 0.2–0.3, with the side-facing heads re-checked against `#474E56` on `plank_cu`.
2. **Trestle part reads as a wide trapezoid (shows on the part).** The exploded cell draws a tall, narrow A whose legs
   nearly meet under the cleat. This follows from decision 5 (10° splay) and the decided 2.82 width. Recorded.
3. **Crossbar part reads slender (shows on the part).** It is 5.59 long with a 0.36 × 0.30 section; the exploded cell
   draws a short, chunky beam about as thick as a leg. The section follows §2.3 and the front band (0.26 H), and the length
   follows the decided table. Recorded.
4. **Side view (shows):**
   - The knee braces appear end-on as a vertical bar at the centre (decision 4, already recorded).
   - The tie stub and peg have little contrast, because the benches end-on behind them are the same wood. The sheet
     cell has no near bench there.
5. **r34 camera (shows, slightly).** At (145, 20) the stool overlaps the table's far end. The sheet shows it standing
   clear to the right. At (155, 20) it separates, but W : H goes from 1.65 to 1.76 against the sheet's 1.51. Content
   check only, so no change is needed.
6. **Bench plank-end bands (shows, slightly).** On `top_sheet` the back bench's inner plank carries the table's cast
   shadow (studio lighting, not paint). The light streak on the outer plank reads as a soft lighter rectangle. Both are
   acceptable.
7. **Seat points sit over seams (does not show).** All five stored seat points lie over a 0.04 seam: the bench centre
   seam at y ±2.40 and the stool's cross seam. A vertical ray at the point hits nothing. A Studio `Seat` part placed at
   z 1.50 is unaffected, so this needs no fix. It is noted for anyone who ray-casts down to the seat.
8. **Stool corridor (does not show).** The stool sits 1.13–1.25 off the table's −X end and 1.26 off the near bench's
   end. This is a corridor open at both ends, not a dead-end pocket; the 0.5- and 0.8-radius walk tests pass. Studio
   validation (Requires Manual Validation) should confirm that a character walks through it without snagging.
9. **Hero Y 6.14 against §2.7's 6.06 (does not show).** The bench outer-face bolts add 0.04 a side. This is within
   the 6.10 ± 0.12 target.

## Main session after round 1 (2026-11-02)

Minor 1 fixed: the iron finish goes from rough 0.45 / metal 0.5 to rough 0.7 / metal 0.25, so the up-facing bolt heads
no longer glint pale; in the regenerated r34 and f34 they read dark slate like the sheet. Base colour unchanged.
