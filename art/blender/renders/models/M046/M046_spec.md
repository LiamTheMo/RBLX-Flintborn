# 046 Natural Arch — spec

Reference: `art/blender/assets/references/046.png` (1024 × 1536 px). The sheet's title is "NATURAL ARCH", with
"FLINTBORN ENVIRONMENT MODEL CATALOG / STYLIZED • MODULAR • GAME-READY (BLENDER / ROBLOX)" at the top right. Its page
number reads "PAGE 44/132" (bottom right), two less than the file number; INDEX.md row 46 calls it "Flintborn Natural
Arch Model Study". The footer reads "FLINTBORN — INDIVIDUAL MODEL STUDY".
Builder: `art/blender/kit/mcp/m046.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7).

Sheet text:
- **Intro:** "Open rock hole through terrain. Large arch and cave entrance module. Walkable and modular."
- **Cells:** "FRONT THREE-QUARTER VIEW", "REAR THREE-QUARTER VIEW"; "TURNAROUND VIEWS": "FRONT", "SIDE", "REAR",
  "TOP (OVERHEAD)".
- **Exploded:** "EXPLODED CONSTRUCTION": "Top Span", "Left Rock Mass", "Right Rock Mass", "Ground Sill (Floor)". Dashed
  arrows drop the span onto the inner top corners of both masses and push the sill against the masses' inner faces.
  Each mass's inner face is drawn as a **flat vertical panel with 3–4 rectangular block tabs**; the sill has notched
  ends.
- **Close-ups:** "UNDERSIDE VIEW": "Joining surfaces (flat and clean)". "ROCK JUNCTION CLOSE-UP": "Top span sits on ledges
  of side rocks. Simple block connectors." "FLOOR DETAIL (THICKNESS)": "Consistent block thickness (across parts)".
- **Material palette:** "ROCK LIGHT (pale stone)", "ROCK SHADOW (cool gray)", "GRASS", "DIRT".
- **Modeling notes:** "Built from a small set of modular rock parts (Top Span, Left Rock Mass, Right Rock Mass, Ground
  Sill)." "Broad flat faces, low-poly, chunky, readable silhouette." "Walkable top surface with grass and simple
  foliage." "Clean blocky joining surfaces for modular reuse." "Keep geometry simple and game-ready. No high-frequency
  detail." "Use consistent rock, grass and dirt color palette from the Flintborn style."
- **Game context:**
  - **The plateau family:** M040 Cliff Wall (committed, lawn **10.4**), M043 Terraced Ledge (built, lawns 5.6 / 10.4),
    M044 Natural Ramp (study accepted; ground → 10.4, sand path `#F7BB7B`), M032 and M041 (10.4). The arch is a
    **free-standing** module: the sheet draws rounded, columned ends on both sides and no seam planes (§2.1, §3.2).
  - **The old kit's W02 row 4 `NaturalArch`** (`art/blender/scripts/kit/W02/natural_arch.py`, goals
    `art/blender/renders/kit/W02/natural_arch_goals.md`, manifest `art/roblox/kit/W02/manifest.json`) is a different
    drawing (32 × 24 × 22, a round 12 × 13 hole, a voussoir ring, an orange apron fanning 4–5 out). `MODEL_PROGRESS.md`
    row 51 flags it "narrow low opening, flat top slab; flat side; narrow pillars". **W02 owns every `NaturalArch*`
    name**, W16 owns `StoneArch*`, sheet 07 owns `RockArch` (§8). Reuse their lessons, not their sizes or names.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Cell paper `#FEFCF5` (254,
252, 245), tolerance 10. Cell borders were found from the grey rule lines (`lines.py`): the hero panel y 65–464, the
turnaround row y 474–751 with dividers at x 306 / 473 / 739, the exploded panel x 15–673 / y 761–1308, the right column
x 673–1008 with rules at y 977 / 986, 1166 / 1174, 1348. Text is painted out (`TITLES` in `m.py`). Masks are `cls()` in
`m.py` (the M044 classes, HSV, h in degrees):
- **P, floor sand:** not green, h 15–42, s ≥ 0.33, v ≥ 0.62 (the sunlit sill tiles and their darker edges). The shaded
  floor inside the tunnel (`#7B6968`) falls in R.
- **R, rock:** h ≤ 50 or ≥ 190, s < 0.40, v ≥ 0.25, not another class. Lit faces are warm peach-beige (h 18–24°);
  shaded faces are cool blue-lavender (h 223–260°). Both count as R. Boulders and pebbles are R.
- **L, lawn:** green (h 45–170, s ≥ 0.28, v ≥ 0.12) with h < 80 and v ≥ 0.62 (lime lawn, yellow flowers, lit fresh
  leaves).
- **F, foliage:** the rest of green (the bushes' emerald and mid leaves).
- **D, dirt / trunk:** h 0–40, s ≥ 0.40, v 0.15–0.62, not P (bush hearts and soil).
- **B, ground shadow**, **T** text / dark, **O** outlines.
- Cells (`V` / `X`): f34 (125,70,598,440); r34 (598,70,1006,440); front (17,500,305,722); side (308,500,472,722); rear
  (476,500,738,722); top (742,500,1006,722); exploded (17,800,672,1306); underside (675,795,1006,975); junction
  (680,1015,862,1166); floor (680,1205,860,1345). Swatch inner boxes 30 × 30 px at x 31–61, y 220 / 268 / 317 / 365
  (`m.SW`).

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m046_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14, Pillow, numpy).
- **Helpers:** `m.py` (masks, boxes `V` / `X` / `SW` / `TITLES`, `label`, `main_obj`), `zoom.py` (crop with sheet grid),
  `lines.py` (cell borders), `blendall.py` (name search in every `.blend`).
- **Measurements:** `measure.py` → `bb.json`, `measure_out.txt` (bbox, W : H, shares, top profile, width per height,
  fifths) and `cls_*.png` previews; `hole.py <views>` (the see-through opening: bbox, widths by height);
  `holeprof.py <view>` (the opening's outline row by row); `rows.py <view> [step]` (class extents per row, used for the
  rock-width and depth profiles in §1.2); `bushes.py` (bush clusters, yellow share).
- **Colour:** `samp.py` → `samp_out.txt` (swatches; per cell: rock all / warm / cool, floor, floor edges, lawn, yellow,
  foliage dark / fresh, trunk).
- **Zooms:** `zn_f34.png`, `zn_r34.png`, `zn_fs.png` (front + side), `zn_rt.png` (rear + top), `zn_expl.png`,
  `zn_cu.png` (three close-ups), `zn_pal.png`; detail `z_f34.png`, `z_r34.png`, `z_fs.png`, `z_rt.png`, `z_front.png`,
  `z_side.png`, `z_f34open.png` (the tunnel), `z_f34floor.png`, `z_r34floor.png`, `z_sill.png`.
- **On our renders:** point `R` in `m.py` at the render, set `P` (the studio paper) and the `V` box, and re-run
  `measure.py` / `hole.py` / `samp.py`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a modular terrain piece. Hero budget 4000 tris, each part under 1000. The plan in §4.3
  lands at about 3500–3800.
- **Overall read (check this first).** **A broad, squat inverted-U of pale warm columnar rock with a tall pointed-round
  hole through its middle, a lime lawn dome on top beaded with round dark bushes, and a sand-flagstone floor running
  through the hole.**
  - two **rock masses** (the pillars), each a cluster of tall flat-faced columns, bottom-heavy: lower **skirt blocks**
    stand against the columns at a third to a half of the height, and **chunky foot boulders** sit at the base;
  - a **top span** of 4 big faceted lumps across the crown, its lumps meeting in a **peaked apex** over the hole;
  - an **opening** with near-vertical jambs to about 0.58 of its height and a pointed-round crown of 2–3 facets a side;
    it runs through the full depth as a **tunnel** (the f34 shows the far jamb's inner wall in shade);
  - a **lawn cap** over the whole top: flat-ish in the middle, draping down the rounded shoulders at both ends, a lime
    lip over the rim, **8 dark bushes** round it, pale pebbles and yellow flowers;
  - a **sand flagstone floor** (the sill) through the tunnel, flaring a little at both mouths, its edges a thin darker
    sand band above the lawn;
  - a thin lime **apron** round the whole foot with small fresh-green bushes, sprigs, yellow flowers, pebbles; lime strips
    along both wall feet inside the tunnel.
  - Hero shares (f34): rock 64.5 %, green 28.5 % (lawn 15.2, foliage 13.3), floor 6.6 %, trunk 0.4 %.
- **Focal silhouettes, in order:**
  1. The hole: a tall, narrow, peaked opening (w : h 0.71–0.77) through a thick rock body, the paper showing through.
  2. The inverted-U outline: a wide base, battered sides, rounded shoulders, a flat lawn top with bush bumps.
  3. The columned pillars with their skirt blocks and foot boulders (the bottom-heavy massing).
  4. The lime lawn dome and the bushes on its rim; the sand floor at the foot of the hole.
- **Target: rock 24.0 W × 12.0 D; lawn top 14.0 at the centre; the opening 7.0 wide between the jambs, apex 9.4 above
  the ground (9.0 clear over the floor at 0.4), springing at 5.4.** The bbox is about 25.4 W (foot plants and apron
  ≤ 0.6 per side past the 12.1 rock base) × 13.8 D × 15.9 H (bush tops); the sheet's front silhouette gives 25.0. Tolerances: W, D ±0.5 on the rock; the opening ±0.3 in width, ±0.4 in
  apex; bbox H ±0.5. Decision §8.1.
  - **How it was derived** (`rows.py`, `hole.py`, `holeprof.py`).
    - **The turnaround cells share one scale.** Front H 181 px, side 186, rear 180. The front cell is near level (our
      fit e 4–12), so its proportions are close to true.
    - **Front (width and opening):** rock at the base x 30–290 = **262 px**; ground at y 702, lawn top at y 548 (154 px);
      bush tops y 528 (174 px). Rock W / lawn H = **1.70**. The opening between the jambs is x 121–190 (**70 px**, 75 px
      on the face edges), its apex at y 602–603, the floor top at y ≈ 698–700: **98 px** tall from the floor. The
      jambs are vertical from the floor to y 643 (full width 70 px), so the **spring line is at 0.58** of the opening
      height.
    - **Side (depth):** rock at the base x 327–454 = **127 px**; 126 px at mid height; 107 px at z ≈ 12.3; the lawn top
      about 81–90 px deep. Rock D / lawn H = 0.82, so **D ≈ 0.49 W**.
    - **Scale:** W 24 → 0.0916 stud/px on the front cell: lawn H 14.1, opening 6.4–6.9 × 9.0, depth 11.7, bush tops
      15.9. Adopted **24 × 12, lawn 14.0, opening 7.0 × 9.0 clear**.
  - **Why this size.**
    - **"Large arch … walkable":** the opening must take a 5.5-stud character comfortably. At 24 W the clear apex is
      9.0 (1.64 characters); at head height (floor + 5.5) the opening is still ≈ 6.6 wide (two characters abreast);
      the jambs are vertical to 5.0 above the floor.
    - **24 W sits on the 4-stud grid** (¾ of the 32 grid; M043 is 20, M040 and M044 16).
    - **Against the plateaus:** the lawn top at 14.0 stands 3.6 above the 10.4 plateau, one default jump (JumpHeight
      7.2) from an M040 / M043 / M044 landing, so the walkable top can be reached in a run of plateau tiles; it is 8.4
      above M043's 5.6. Nothing on the sheet ties the arch to a plateau seam (§3.2).
    - **Rejected: lawn at 10.4** (the plateau). The sheet's proportions then give W 17.7, an opening **5.1 wide × 6.6
      apex** (the jambs only 3.8 tall, ≈ 2 wide at head height): a cramped doorway, not "Large arch". **Rejected: the
      32 grid** (opening 9.3 × 12, lawn 18.7): a cathedral, out of scale with the 10.4 plateaus.
  - **Against the character (5.5):** the arch is 2.5 characters tall to the lawn; the jambs reach 0.9 of a character;
    the foot boulders are waist to chest high (2–3.5); the skirt blocks shoulder to head high (4.5–6.5); the bushes are
    knee to waist high on the lawn.
- **Build frame:** the opening's axis along **Y** (front face −Y, back face +Y), the masses at −X (Left) and +X (Right),
  ground z 0, origin at the opening's centre on the ground. Stage 2 re-centres the hero on its bbox bottom centre;
  record the offset from the build frame (`m046_offset`, as M040 / M043 did).

### 1.2 Measured views (`measure.py`, `measure_out.txt`)

| View (box) | Silhouette bbox (px) | W : H | R | P | L | F | G (L + F) | D | O |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (125,70,598,440) | 132–588 × 81–433 (457 × 353) | **1.295** | **64.5 %** | 6.6 | 15.2 | 13.3 | **28.5** | 0.4 | 2.5 |
| Rear three-quarter (598,70,1006,440) | 600–1003 × 108–427 (404 × 320) | 1.262 | 67.1 | 3.6 | 15.4 | 13.4 | 28.8 | 0.5 | 2.1 |
| Front (17,500,305,722) | 24–296 × 528–708 (273 × 181) | **1.508** | 68.1 | 4.7 | 14.8 | 12.1 | 26.9 | 0.3 | 2.5 |
| Side (308,500,472,722) | 317–462 × 528–713 (146 × 186) | **0.785** | 74.7 | 1.2 | 11.8 | 11.9 | 23.7 | 0.5 | 3.0 |
| Rear (476,500,738,722) | 476–736 × 529–708 (261 × 180) | 1.450 | 67.9 | 4.6 | 15.1 | 12.1 | 27.2 | 0.3 | 2.6 |
| Top (overhead) (742,500,1006,722) | 751–994 × 530–709 (244 × 180) | 1.356 | 41.3 | 1.4 | 38.7 | 18.1 | 56.8 | 0.5 | 3.5 |
| Exploded (17,800,672,1306) | 33–641 × 811–1267 | 1.333 | 76.2 | 1.6 | 11.6 | 10.3 | 21.9 | 0.4 | 1.9 |

- Shares are of R + P + L + F + D; O and B are left out. **The rear and r34 repeat the front and f34** (shares within
  2.7 points; §3.3). **Verifier tolerance:** shares ±4 points; W : H ±0.08; positions ±0.05 of W / H unless stated.
- **Yellow flowers** (h 46–60, s ≥ 0.6, v ≥ 0.85): 0.60 % of the f34, 0.96 % of the front, 0.57 % of the side, 0.61 %
  of the top.
- **Pale pebbles on the lawn:** 10 blobs in the top cell, 6 in the f34 crop of the lawn, cream-grey `#DFD8C4` (44°, .12,
  .87); more show by eye (≈ 14–18 over the top).
- **The "TOP (OVERHEAD)" cell is not a plan.** It is a high oblique from the front (our estimate e 50–65): the lawn top
  fills the upper half, the front face and the hole the lower half (the hole opens to the cell's bottom edge: gaps
  826–924 px at its foot). Judge it at that camera (§2.6).

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .18 | .35 | .54 | .74 | .85 | .86 | .85 | .92 | .92 | .96 | .97 | .95 | 1.0 | .93 | .93 | .92 | .94 | .85 | .82 | .54 | .27 |
| Front | .09 | .28 | .69 | .81 | .89 | .87 | .91 | .91 | .97 | .92 | .99 | .97 | .97 | .92 | .89 | .90 | .88 | .78 | .70 | .39 | .09 |
| Side | .12 | .18 | .64 | .87 | .92 | .95 | .96 | .93 | .97 | .98 | .98 | .96 | .91 | .87 | .88 | .86 | .75 | .74 | .68 | .23 | .12 |
| Rear | .07 | .26 | .69 | .81 | .90 | .87 | .87 | .96 | .94 | .92 | .97 | .97 | .97 | .96 | .89 | .90 | .91 | .84 | .69 | .30 | .07 |
| Top | .16 | .71 | .84 | .87 | .89 | .95 | .96 | .92 | .91 | .92 | .93 | .97 | .98 | .91 | .92 | .88 | .92 | .89 | .82 | .72 | .23 |

- Reading:
  - **Front / rear:** a symmetric dome. The ends fall fast (f .00–.10: .09 → .69, the foot bushes and the battered end
    faces), the shoulders round over f .10–.20, and the lawn top runs nearly level from f .20 to .85 (.87–.99, the
    bumps are bushes).
  - **Side:** a flat-topped block with rounded top corners (f .10–.15 and .80–.95).
  - **f34:** a steady rise from the left end (.18) to the crown (1.0 at f .60), level to f .85, then the near right
    corner falling (.54 → .27).

**Width per height** (silhouette width at h .05 → .95, fraction of W):

```
f34    .36 .79 .95 .92 .86 .84 .82 .76 .68 .26
front  .97 .95 .94 .88 .87 .85 .80 .74 .65 .27
side   .77 .94 .87 .86 .82 .82 .78 .69 .60 .29
rear   .95 .95 .92 .88 .87 .84 .82 .73 .68 .30
top    .87 .97 .96 .95 .96 .92 .91 .89 .75 .38
```

- **The body narrows steadily upward** (front .97 → .65 at h .85): battered end faces, then rounded shoulders.

**Rock + lawn outline (front, `rows.py front`; ground y 702, 0.0916 stud/px):** full width 24.2 at z 1.5, 22.3 at z 3.1,
22.1 at z 5.3, 21.7 at z 7.5, 20.8 at z 9.2, 20.1 at z 10.3, 18.9 at z 11.4, 18.2 at z 11.9, ≈ 14–15 at z 13.0 (the
rim), the lawn top 14.2 wide at z 14.1. The lime lip shows on both shoulders from z 10 to 11.5 (L at x 58–64 and 261–273
px on y 572–596).

**Depth outline (side, `rows.py side`; ground y 708, 0.0945 stud/px):** 13.0 at z 1.5 (foot plants), 12.1 at z 3.2, 11.9
at z 5.5, 11.4 at z 7.2, 11.2 at z 8.9–10.0, 10.8 at z 11.2, 10.1 at z 12.3, ≈ 8 at z 13.4, the lawn top 8–8.5 deep.
The bottom row is narrower than z 1.5 (wph .77): **nothing sticks out at ground level in the side view** (the floor ends
inside the footprint, §2.3).

**Fifths** (bottom → top, % of each class):

| View | Green | Floor | Rock |
| --- | --- | --- | --- |
| f34 | 20.9 / 20.7 / **1.3** / 19.8 / 37.3 | 73.5 / 22.7 / 2.0 / 1.6 / 0.3 | 8.5 / 29.3 / 32.5 / 27.6 / 2.1 |
| Front | 30.3 / 6.2 / **0.3** / 23.3 / 39.9 | 79.2 / 11.4 / 6.4 / 2.6 / 0.4 | 19.0 / 25.2 / 30.6 / 24.2 / 1.0 |
| Side | 24.8 / 6.4 / **1.5** / 28.2 / 39.1 | 48.2 / 28.4 / 12.6 / 5.4 / 5.4 | 21.0 / 29.6 / 30.3 / 17.9 / 1.2 |
| Top | 8.0 / 4.2 / 22.4 / 42.4 / 23.0 | — | 17.9 / 40.7 / 35.5 / 5.1 / 0.7 |

- **The middle fifth is bare rock** in every elevation view (green ≤ 1.5 %): no moss on the column faces.

**The opening (`hole.py`, `holeprof.py`; the see-through region):**

| View | Hole bbox (px) | w × h | w / W | h / H | top at h | bottom at h |
| --- | --- | --- | --- | --- | --- | --- |
| Front | 120–191 × 603–688 | 72 × 86 | **0.264** | 0.475 | **0.580** | 0.110 (the far floor) |
| Rear | 569–637 × 609–688 | 69 × 80 | 0.264 | 0.444 | 0.550 | 0.111 |
| f34 | 329–397 × 214–325 (+ a sliver 403–455 beside the far jamb) | 69 × 112 | 0.151 | 0.317 | 0.620 | 0.306 |
| r34 | 770–844 × 238–335 (+ a sliver 729–763) | 75 × 98 | 0.186 | 0.306 | 0.591 | 0.287 |

- **Front-cell outline, row by row** (y → hole width px): 603 → 2 (apex), 607 → 24, 611 → 37, 615 → 46, 619 → 50,
  623 → 53, 631 → 61, 639 → 69, 643–679 → 70–71 (vertical jambs), 683–687 → 53–61 (grass tufts at the jamb feet).
  In studs above the ground (floor top 0.4): half-width **3.5 from 0.4 to 5.4**, 3.2 at 6.1, 2.65 at 7.2, 2.3 at 8.0,
  1.85 at 8.3, 1.2 at 8.7, **0 at 9.4**. A pointed-round crown: steep sides, a sharp apex where two span lumps meet.
- In the f34 / r34 the far jamb's inner wall cuts the see-through region in two (the sliver beside it): **a tunnel through
  the full depth**, its walls faceted and in shade.

### 1.3 Silhouette and composition per view

**Front three-quarter (`zn_f34.png`, `z_f34.png`, `z_f34open.png`, `z_f34floor.png`): governs.** An elevated view from
the front-left: the **front face** spans most of the image, the **left (−X) end** shows at the far left, and through the
hole the **right mass's inner wall** recedes in blue-grey shade. Our estimate: az −30 … −40, e 12–24 (the sheet camera
has stronger perspective than ours).
- **Hole:** centred at f 0.50, a tall peaked opening; through it the paper, the far jamb's faceted wall with a lime strip
  along its foot, and the shaded floor (`#7B6968`) inside.
- **Span crown:** 3–4 big faceted lumps above the hole ((250–330, 175–260), (330–470, 150–250)), lit warm on their front
  and top facets, lavender underneath; their lower facets form the crown.
- **Left mass (front face and left end):** 3 tall columns on the front ((175–250), (250–300), the jamb (300–330)), 2–3
  on the end ((132–200)); **two big skirt blocks** at the front ((180–260, 290–430), (150–200, 330–420)) standing about
  0.4–0.5 of the height; a **dark bush at the jamb foot** ((270–340, 360–420)); lime ledge pads with small bushes on the
  skirt tops ((155,369), (200,326)).
- **Right mass:** columns stepping round the front-right corner (490–590), **2–3 foot boulders** ((470–520, 330–370),
  (530–575, 310–360)), small fresh-green bushes at (512,356), (556,348), (562,299).
- **Lawn top:** a broad lime dome from (180, 190) to (560, 230); **6–7 dark bushes** round the rim ((237,160) large,
  (286,126), (343,105), (400,98), (444,115), (504,138) large, and one at the far right), pale pebbles and a few yellow
  flowers; the lime lip hangs over the rock rim.
- **Floor:** sunlit sand flagstones in front of the hole ((330–505, 340–435)), 5–6 large irregular tiles, a few pebbles,
  a thin darker sand edge along the front; the arch's shadow line crosses it. It flares a little wider than the hole.
- **Apron:** lime round the whole foot with sprigs, yellow flowers, pale pebbles.

**Rear three-quarter (`z_r34.png`, `z_r34floor.png`).** The mirror of the f34 (the right end and the back face, the floor
running to the lower left, the left mass's inner wall in the hole). Same massing, same dressing families. Judged as a
repeat with the back face as a varied mirror of the front (§3.3).

**Front (`z_front.png`).** Near level (e ≈ 4–12). The inverted U: battered ends with foot bushes, rounded shoulders with
lime lips, a nearly level lawn top with 4–5 bush bumps ((79,565), (158,541), (231,554), (253,584)). The hole in the
middle (x 121–190), the floor strip across its foot (front edge **138 px = 12.6 studs** wide, x 87–225: wider than the
hole), foot boulders and skirt blocks either side of it (left: a boulder at x 100–114 px beside the jamb, a tall skirt
at 57–82; right: a boulder at 210–239, y 657–695, and a second further out), small fresh-green bushes at
(46,681), (92,695), (202,692), (269,699). Each pillar's face: 3 columns plus skirt blocks.

**Side (`z_side.png`).** A slightly turned view of the +X end: a tall block of 4–5 columns (lit peach and lavender
strips), lower skirt blocks and foot boulders along the base, a lime ledge pad with a bush at z ≈ 5 on the front corner
((337–349, 638–662)), a bush cluster on the top at the front, the lawn draping down the back corner. Floor 1.2 %.

**Rear (`z_rt.png`).** A repeat of the front with the dressing moved.

**Top (overhead) (`z_rt.png`).** A high oblique from the front: the lawn dome (38.7 % L) with 7–8 dark bushes round it
((813,548), (885,547), (942,557), (951,593), (785,614) on the left shoulder, (966,624) on the right), pale pebbles, the
lawn edge scalloped over the front face; the front face's crown lumps and the hole below.

### 1.4 Parts (Exploded Construction (17,800,672,1306), `zn_expl.png`, `z_sill.png`)

A three-quarter view from the front, slightly above. **The hero governs every size**; the parts give shapes, part
boundaries and facet character.

| Part | Box (sheet px) | Notes |
| --- | --- | --- |
| Top Span | (143,805,517,980) | A long faceted beam of **4–5 big rock lumps** in a row (lavender undersides, warm tops), its whole top a lime lawn with 4 dark bushes and pebbles, a lime lip over its front edge. Width ≈ 0.6 of the assembled width; rock thickness ≈ 0.28 of its width. Its underside: lumps hanging below **flat seat faces** at both ends |
| Left Rock Mass | (40,960,235,1195) | A tall mass of columns and skirt blocks, **lawn and a bush on its outer top**, its **inner face a flat vertical panel with 3–4 rectangular block tabs**; foot boulders, a lime apron and small bushes at its base |
| Right Rock Mass | (437,975,640,1260) | The mirror: flat inner panel with tabs (left side), columns, a big foot boulder, a dark bush and lime apron at its base, lawn and bushes on top |
| Ground Sill (Floor) | (217,1147,420,1257) | A thick flat slab drawn in **pale stone** (`#DAC2B9` top, `#89818B` shaded side), cracked into 6–8 large tiles, **notched ends** (two steps at the right end) where it meets the masses. Thickness ≈ 0.09 of its length |

#### Top Span
- **Shape:** a beam of 4 lumps along X. Each lump a chunky faceted block (6–9 faces visible), the front and back lumps
  bulging 0.3–0.6 proud with creases 0.3–0.5 deep between them. The **underside** (underside cell): two flat seats at
  the ends ("Joining surfaces (flat and clean)"), the middle lumps hanging lower and forming the crown, a lime lip
  visible along the top edge from below.
- **Hero size:** x ±6.7 (13.4 wide), y −5.2 … +5.2 at the soffit (the crown faces lean back to ±4.2 at the lawn), seats
  at z 8.0, soffit apex 9.4, rock top 13.4 (§2.2).

#### Left / Right Rock Mass
- **Shape:** columns with tall strip facets, battered outer faces, rounded shoulders; skirt blocks and foot boulders at
  the base; the inner side a vertical **jamb** that leans in above the spring line (the haunch) to a flat **ledge** at
  z 8.0 (junction close-up: "Top span sits on ledges of side rocks"), then rises again as a flat joining face under the
  span's end.
- **Hero size:** x ±3.5 (jamb) … ±12.1 (base), y ±6.0 at the base, rock top 13.0–13.4 under the lawn.

#### Ground Sill (Floor)
- **Shape:** big irregular flagstones 0.4 thick on a flat base, a slightly bevelled top edge, darker sand sides; its
  ends notched round the jamb feet.
- **Hero size:** the tunnel strip x ±3.7 (0.2 under each jamb foot) for |y| ≤ 5.0, flaring to x ±5.6 at the mouths
  (y ±6.4); top z 0.4 (§2.3).

#### Junction close-up (680,1015,862,1166)
A span lump's dark faceted bottom hangs over a pale flat-topped block (the ledge) with a darker socket line; a down
arrow places the span on it. Lime turf and a bush on the outer part of the mass top. **Flat, clean seat faces** are the
point; the socket is the "simple block connector".

#### Floor detail (680,1205,860,1345)
A thick slab block with a top crack, a pebble, and a dimension arrow over its front edge: "Consistent block thickness
(across parts)". Top `#F0D1B8` (27°, .23, .94), lit side `#D2AD97`, shaded side `#9F8E8B`.

#### Bushes, flowers, rocks (`z_f34.png`, `z_front.png`)
- **Dark bush (lawn rim):** a round dome of broad rounded leaves in two tones: deep emerald inner and lower leaves
  (`#1F6C21`, 122°) and fresh green upper leaves (`#577E0F` → lit `#89CC35`, 81°); a dark soil heart (`#462304`) shows
  at the base. Ø 2.4–2.8, 1.6–2.0 tall over the lawn (front cell: 27–29 px wide, 20 px tall).
- **Foot bush:** the same two-tone family, smaller and fresher (foot greens: fresh `#85BE1B` 81°, deep `#276B20` 114°),
  Ø 1.4–2.2, 1.0–1.5 tall.
- **Sprig:** 3–5 lime-green leaves from one root, Ø 0.7–1.0, often with a yellow bud.
- **Yellow flower:** small five-petal flowers `#E0DB1B` (58°), lit `#EDE61C`, Ø 0.4–0.6, singles and pairs on the
  apron and the lawn.
- **Pebbles:** cream-grey `#DFD8C4`, 0.25–0.5, on the lawn top, the apron and the floor.
- **Foot boulders:** pale, faceted, 1.8–2.8 wide, 2.0–3.5 tall, a pitched 3–4-facet crown (front cell (210–239,
  657–695): 2.7 wide × 3.5 tall): chunky gems, not eggs.
- **Skirt blocks:** tall chunky blocks leaning on the columns, 2.5–4 wide, 4.5–6.5 tall, pitched tops; 2–3 carry a lime
  ledge pad with a sprig or small bush.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (opening axis Y, front −Y, back +Y, Left mass −X, Right mass +X, ground z 0).

### 2.1 Footprint and contract

| Item | Value | Notes |
| --- | --- | --- |
| Rock footprint at the ground | x −12.1 … +12.1, y −6.0 … +6.0 | the skirts and foot boulders reach the outline; columns sit 0.3–0.6 inside it |
| Opening | jambs x ±3.5 from the floor to z 5.4; crown to the apex (0, 9.4) per §1.2 | constant through the tunnel within ±0.3 (facet relief) |
| Tunnel length | y −5.2 … +5.2 at the soffit; the jambs y −5.6 … +5.6 at the floor | the mouths flare (§2.3) |
| Floor top | z 0.40, flat (±0.03 per tile) | walkable; the tile edge stands 0.25–0.3 over the apron |
| Lawn top | 14.0 at the centre; ≥ 13.6 over the central 14 × 6; the front / back rim at 13.3–13.5; the shoulders drape to z 10.5–11.0 at x ±10.5 | walkable: slope ≤ 25° over the central 14 × 6 |
| Ends | free-standing, rounded, columned | no seam planes (§3.2) |
| Outside the footprint | apron and foot plants to x ±12.7, y ±6.9 | nothing past ±0.8 outside the rock |

- **Placement:** the arch stands on the ground anywhere a path runs through. Its floor at 0.4 is flush with M044's toe lip
  (0.35) within 0.05 and uses the same sand, so a ramp path or a sand path can run up to either mouth.
- **Plateau run:** stood beside a 10.4 plateau tile, the arch's lawn is a +3.6 jump up; no seam contract applies.

### 2.2 Span and seats (the arch span must be sound)

- **Seats:** both masses carry a **flat ledge at z 8.0** from the haunch tip x ±2.3 out to x ±6.7, across the full depth
  (y ±5.2). The span's two **seat faces** lie on them (coplanar, hidden, touching; or the span sunk 0.02). The
  ledge's outer edge rises as a flat vertical joining face at x ±6.7 to the mass's top; the span's end faces lie on it
  (0.02–0.05 overlap).
- **Span body:** x ±6.7, rock top 13.4 at the centre (13.0–13.3 at the ends, under the lawn), front and back faces at
  y ±5.2 at z 8–11 leaning back to ±4.4 at 13.0. **Soffit:** from the seat edges (±2.3, 8.0) up through (±1.85, 8.3),
  (±1.2, 8.7) to the apex (0, 9.4); built as 2–3 facets a side meeting in a ridge along Y, with ±0.2 relief per lump
  so the vault isn't a perfect prism.
- **Lumps:** 4 across the front face (x centres ≈ −5.0, −1.7, +1.7, +5.0; 3.0–3.6 wide), 4 across the back (staggered
  0.5); each bulges 0.3–0.6 proud of the span face, creases 0.3–0.5 deep. The two central lumps' lower facets meet at
  the apex (the sheet's V). The outer lumps overhang the seat line by 0.1–0.3 with bevelled bottoms, so the span / mass
  joint on the faces reads as a rock crease, not a saw cut.
- **Thickness:** 5.4 at the seats (8.0 → 13.4), 4.0 over the apex. It's a thick lintel, not a slab.

### 2.3 Masses, skirts and the floor

**Mass core (each side; Left = mirror of Right with varied columns).**

| z | Outer end face x (Right) | Front / back faces y | Inner side | Notes |
| --- | --- | --- | --- | --- |
| 0 | 11.8 (columns; skirts and boulders to 12.1) | ±5.6 (skirts to ±6.0) | jamb x 3.5 | foot ring bevelled in 0.2 over the lowest 0.3 |
| 5.4 | 11.0 | ±5.5 | jamb x 3.5 (spring) | vertical jamb 0.4 → 5.4 |
| 8.0 | 10.6 | ±5.4 | haunch tip x 2.3, then the **ledge** out to 6.7 | haunch leans in through (3.2, 6.1), (2.65, 7.2) |
| 10.3 | 10.0 | ±5.3 | joining face x 6.7 | |
| 11.4 | 9.5 | ±5.1 | x 6.7 | shoulders begin |
| 12.4 | 8.6 | ±4.8 | x 6.7 | |
| 13.0–13.2 | 7.4 (the rim, under the lawn lip) | ±4.4 | x 6.7 | **no flat top exposed** (§6) |

- **Columns:** each mass has **3 columns across each front / back face** (outer, middle, the jamb column) and **4 across
  the end face**, each 2.0–3.5 wide; creases 0.4–0.6 deep; each column face in **2 tall facets** (a vertical ridge 0.1–0.2
  proud at 0.4–0.6 of its width); a facet break at 0.55–0.7 of the height on 2–3 columns (the sheet's stacked-block look).
  The column tops round over into the shoulders under the lawn.
- **Jamb and tunnel walls:** the inner face is 2–3 broad facets along Y (relief ±0.3), the haunch 2 facets; the walls
  read as rock, not as the exploded's flat tabbed panel (§3.4).
- **Skirt blocks** (separate closed shells, sunk 0.2–0.4 into the core): per mass, 2 on the front face (one at the jamb
  corner, 4.5–6.5 tall; one mid-face, 3.5–5), 1–2 on the back, 1 on the end face (the side cell's ledge block, top ≈
  5.0). Pitched 3–4-facet tops (≥ 30°) except where a ledge pad sits (a flat crown ≤ 1.2 across, fully turfed).
- **Foot boulders** (separate shells, sunk 0.1): 4 per mass, 1.8–2.8 wide, 2.0–3.5 tall, round the front, back and end
  feet; on the front both sides of the hole (front cell, hole centre at 155 px: x ≈ −4.4 beside the left jamb, +6.4
  and ≈ +9 on the right, at y ≈ −6.0; a tall skirt at x ≈ −8.0).

**Floor (`StoneGateSill`).**
- **Plan:** the tunnel strip x ±3.7 (under each jamb foot by 0.2) for y −5.0 … +5.0; at each mouth it **flares** to x ±5.6
  at y ±6.4 (a trapezoid each end), filling between the foot boulders. The front cell's floor front edge is 12.6 wide;
  the side cell shows nothing past the footprint at ground level.
- **Tiles:** 10–12 irregular flagstones (convex 4–6-sided outlines, 2.5–4 across), each a closed slab 0.4 tall (z 0 →
  0.4), top edge bevelled 0.06, seams ≤ 0.04, per-tile height jitter ±0.02. Two notched ends (steps 0.4 × 0.6) under the
  jamb feet, as the exploded draws.
- **Pebbles:** 6 on the floor, 0.2–0.4, ≤ 0.2 tall, sunk 0.03, near the walls and the mouths (walkable).
- **Inside the tunnel:** lime strips 0.4–0.7 wide on the floor's margin along both wall feet (x ±3.0 … ±3.6), 0.08 thick,
  with 2–3 sprigs a side (f34: the lime line along the far wall's foot).

### 2.4 Lawn cap

- **One cap per part** (span x −6.7 … +6.7; each mass x ±6.7 … rim), meeting at x ±6.7 with **coincident edge vertices
  at one height** (overlap ≤ 0.02 down), so the hero's lawn reads as one dome (§6).
- **Top surface:** a CDT over the outline, resampled at ≤ 1.0 spacing (M040 m6: no big flat triangles in the top view),
  dome 14.0 → 13.4 at the rim; ±0.15 lumps. **Thickness** 0.5–0.7 over the rock top.
- **Edge:** a lime lip overhanging the rock rim 0.2–0.4 and dropping 0.3–0.5 on the front / back (scalloped ±0.3 round
  the crown lumps); on the shoulders the cap drapes down to z 10.5–11.0 at x ±10.5 with a scalloped lower edge (front
  cell lime lip x 58–64 / 261–273 px, z 10–11.5).
- **Dressing on top:** **8 dark bushes** on the rim, inboard 0.6–1.2 of the lip: (−10.0, −1.5) on the left shoulder,
  (−6.8, +2.8), (−4.4, −3.4), (−0.6, +3.3), (+1.2, −3.6), (+5.4, +2.7), (+7.8, −2.8), (+10.0, +1.2) on the right
  shoulder; 14–18 pebbles; 4–6 yellow flowers; 2–3 sprigs. The middle of the lawn stays open (the sheet's open lime
  field, top cell).

### 2.5 Foot dressing and apron

| Piece | Where | Size | Sheet evidence |
| --- | --- | --- | --- |
| Apron | a jagged lime ring 0.8–2.0 wide round the whole rock foot, 0.08–0.12 thick, tucked 0.1 under the rock; not on the floor (it borders the floor tiles' sides) | to x ±12.7, y ±6.9 | every elevation view; f34 foot |
| Jamb-foot dark bush | front-left, (−5.2, −6.6) | Ø 2.4, 1.8 tall | f34 (270–340, 360–420) |
| Foot bushes (fresh) | 6–8: front (−10.5, −6.2), (+5.6, −6.6), (+11.0, −4.8); back (−9.0, +6.4), (+4.8, +6.6); ends (−12.2, +2.0), (+12.2, −1.5) | Ø 1.4–2.2, 1.0–1.5 tall | front (46,681), (92,695), (202,692), (269,699); f34 right foot |
| Ledge pads | on 3 skirt tops (left end, right end, front-left), lime 0.1–0.15 thick, each with a sprig or small bush | ≤ 1.2 across | f34 (155,369), (200,326); side (337–349, 638–662) |
| Sprigs | 6 on the apron, 2–3 a side inside the tunnel | Ø 0.7–1.0 | f34 foot |
| Yellow flowers | 8–10 on the apron in pairs | Ø 0.4–0.6 | f34, front (yellow 0.6–1.0 %) |
| Pebbles | 8 on the apron | 0.25–0.5 | f34, front foot |

- **Keep clear:** the floor carries only pebbles; no bush within 0.3 of the floor edge; nothing inside the opening above
  the floor except the wall-foot strips and sprigs (≤ 0.6 tall).

### 2.6 Expected extents and screen checks

- **Extents (build frame):** X −12.7 … +12.7; Y −6.9 … +6.9; Z 0 … ≈ 15.9 (bush tops on the lawn). Bbox ≈ 25.4 × 13.8 ×
  15.9.
- **Checks on the renders** (floor hidden, `measure.py` / `hole.py` masks; the studio's paper colour in `P`):
  - **f34_sheet (−35, 18)** (probe az −28 / −35 / −42 × e 12 / 18 / 24, keep the best):
    - W : H 1.22–1.37 (sheet 1.295);
    - shares R 64.5 ± 4, G 28.5 ± 4 (L 15.2 ± 4, F 13.3 ± 3), P 6.6 ± 2.5, D ≤ 1.5;
    - green fifths within ±7 of §1.2, **the middle fifth ≤ 4 %**;
    - the hole centred at f 0.50 ± 0.05, top at h 0.62 ± 0.05; the far jamb's wall visible through it;
    - top profile within ±0.08 (mean ≤ 0.05) of §1.2.
  - **front_sheet (0, 8)** (probe e 4 / 8 / 12): W : H 1.43–1.58 (1.508); R 68 ± 4, G 27 ± 4, P 4.7 ± 2; **the hole
    w / W 0.26 ± 0.03, h / H 0.47 ± 0.04, top at h 0.58 ± 0.04, jambs vertical over its lower 0.5**; the floor strip
    across the hole's foot, wider than the hole.
  - **side (90, 8)** (probe e 4 / 8 / 12): W : H 0.72–0.85 (0.785); R 75 ± 5, G 24 ± 5; nothing at ground level
    outside the footprint.
  - **top_sheet (0, 60)** (probe e 50 / 60 / 70): W : H 1.28–1.44 (1.356); L 39 ± 5, F 18 ± 4, R 41 ± 5; 7–8 bushes
    round the lawn.
  - **rear_sheet (180, 8), r34_sheet (145, 18):** judged as repeats of the front / f34 (§3.3); shares ±5.

## 3. View conflicts and resolutions

### 3.1 Size: plateau height vs a walkable "large arch"

- **Evidence:** §1.1. At the sheet's proportions the lawn height fixes the opening: lawn 10.4 → opening 5.1 × 6.6.
- **Resolution (decision §8.1):** **24 × 12, lawn 14.0, opening 7.0 × 9.0 clear.** **Alternatives:** lawn 10.4 (W 18,
  cramped opening); W 32 (opening 9.3 × 12).

### 3.2 "Modular" and "through terrain" vs rounded free-standing ends

- **Evidence:** the intro calls it "Open rock hole through terrain … modular"; every view draws rounded, columned end
  faces, a lawn draping over both shoulders and no flat seam plane; the only "clean blocky joining surfaces" are the
  internal seats, the inner faces and the sill ends (the exploded and the close-ups).
- **Resolution:** **modular = built from the four labelled parts with flat joining faces between them; the hero is
  free-standing** with rounded ends. No x seam planes. **Alternative:** flat seam ends at x ±12 so the arch can slot
  into a run of cliff tiles (not drawn; would change the front / rear silhouettes and the top profile).

### 3.3 Rear and r34 repeat the front and f34

- **Evidence:** shares within 2.7 points; the same hole (w / W 0.264 both); the same massing mirrored.
- **Resolution:** build the back face as a varied mirror of the front (columns, skirts and lumps moved ±0.3–0.8, the
  dressing re-placed); judge rear / r34 as repeats.

### 3.4 The exploded's flat tabbed inner panels vs the hero's faceted tunnel walls

- **Evidence:** the exploded masses' inner faces are flat panels with 3–4 rectangular tabs; the f34 / r34 tunnel walls
  are faceted rock in shade with a lime strip at the foot, no tabs.
- **Resolution (decision §8.4):** the hero governs the visible walls: **faceted rock jambs and haunch**. The joining
  surfaces are the **hidden** ones: the flat ledges at z 8.0, the flat joining faces at x ±6.7 above them, the span's
  flat seat faces, and the sill ends under the jamb feet. **No tabs** (they would show in the tunnel, or cost hidden
  tris). **Alternative:** 2 shallow tabs and matching sockets on each ledge / seat pair (hidden in the hero; +40 tris).

### 3.5 Floor colour: sand (hero cells) vs pale stone (exploded and floor close-up)

- **Evidence:** the hero cells' floor is sand: f34 `#F6BA80`, the front strip `#F7C086`, lit `#F8BE85` (30°, .46). The
  exploded sill is pale stone (`#DAC2B9`, 16°, .15) and the floor close-up's top is pale peach (`#F0D1B8`, 27°, .23). The
  palette's "DIRT" swatch is a brown `#B0744B` (24°, .57, .69).
- **Resolution (decision §8.5):** **sand flagstones** (the hero), in the part too; the same sand family as M044's path
  (`#F7BB7B`) so paths join. Tile sides darker sand by role. The swatch is the hue reference for the floor. **Alternative:**
  a pale-stone sill (exploded); it would read as rock and lose the f34's sand floor (P 6.6 %).

### 3.6 Exploded proportions

- **Evidence:** the exploded masses are drawn squat (≈ 195 px tall against a 374 px span: 0.52 of the span's width; the
  hero's masses stand ≈ 1.0 of it); the sill reads deeper than wide in some readings.
- **Resolution:** the turnaround cells govern all sizes; the exploded gives the part split, the seat ledges, the lumpy
  span and the notched sill only.

### 3.7 Sheet perspective

- The cells are perspective drawings; the studio renders at 50 mm. The front and rear cells are near level, so their hole
  and outline ratios are trusted to ±0.03; the f34 / r34 / top ratios to ±0.08.

### 3.8 "Broad flat faces … no high-frequency detail" against the user's blended-colour rule

- The user's rule wins quietly: broad position blends (lighter upper columns and crown lumps, deeper feet), per-column
  tint, whole-facet Tint mottling at low amplitude, never per-triangle confetti. The sheet's peach-lit / lavender-shade
  split is the light (§5.3).

### 3.9 Palette names against the renders

- **"ROCK LIGHT (pale stone)" `#CEBCB5`** (17°, .12, R − B 25) is paler and pinker than the rendered warm faces (`#C7A99A`,
  20°, .23, R − B 45). Hue reference only; calibrate to the rendered faces (§5.4).
- **"ROCK SHADOW (cool gray)" `#8D9383`** is a **green-grey** (82°, .11, G > R > B). The rendered shade faces are
  blue-lavender (223–260°). **Never a key**: it would read olive / mossy on the stone, and the lavender is light.
- **"GRASS" `#BED120`** (66°, .85) is a little duller than the rendered lawn (`#CFD809`, 63°, .96).
- **"DIRT" `#B0744B`**: §3.5.

### 3.10 Cast shadow

- The sheet's ground shadows are faint near-white (B). Render every `*_sheet` view with the studio floor hidden (M034
  §2.6), and keep the hole's see-through clean (no floor plane showing through it).

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

**Reuse M040** (committed): `_cdt`, `_cap`, `_steiner`, `_resample`, the plants (`_leaf`, `bush`, `sprig`, `pebble`,
`lawn_rock`, `apron`), `_touch`, `_dome_heart`, `_prism`, and the shell / contact / capping reports and `measure()`.
If `m043` is committed when this model starts, its `body()` (the L ∪ U surface built directly with shared vertices, no
boolean), `block_rock`, `pointed_rock`, `_tleaf`, `bush(…, tiers)` and `seam_report` / `capping_report` are the better
templates. Don't edit `m040.py`, `m043.py` or the shared helpers.

1. `span()` → **`StoneGateSpan`** ("Top Span"): **one closed shell built directly** (explicit vertex rings along X: the
   seat faces, the soffit ridge, the front / back lumps as ring offsets, the top under the lawn), no booleans, 260–360
   tris; plus its lawn cap, 3–4 of the rim bushes (those with |x| ≤ 6.0), its pebbles and flowers. Compare with the
   exploded span (4–5 lumps, lawn on top, lavender underside) and the underside cell (`under_cu`, e −30: flat seats at
   both ends, lumps between, the lime lip from below).
2. `mass(side)` → **`StoneGateMassL` / `StoneGateMassR`**: the core as **one closed shell** (columns, jamb, haunch, ledge,
   joining face, shoulders: build it directly as M043 did, or as a merge-0 exact union of 3–4 column prisms **at the
   world origin**, one at a time, saving between; STAGES "Booleans"); skirt blocks and foot boulders as their own closed
   shells; its lawn cap with its rim bushes (shoulder and outer-top ones), ledge pads, its jamb-foot bush. Compare with
   the exploded masses (columns, lawn on the outer top) and the junction close-up (`junc_cu`: the ledge under the span).
3. `sill()` → **`StoneGateSill`** ("Ground Sill (Floor)"): 10–12 flagstone slabs (8 + 8 bevel faces, 20–28 tris each),
   notched ends, its pebbles. Compare with the exploded sill (tiles, thickness, notches) and the floor close-up
   (`floor_cu`).
4. **Apron, foot plants, sprigs, foot pebbles, the tunnel wall-foot strips** belong to the hero (`on="hero"`), not a part.
5. **Hero `StoneGate`** = span + both masses + sill + hero-only dressing.
   - Each piece is its own closed shell in one object; no booleans between parts.
   - `M.fix_bowties`; origin at the bbox bottom centre; transforms applied.
6. **Parts shot** (az −30, e 25), laid out like the exploded: the span above, the masses apart left and right, the sill
   between them in front.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a squat columned rock arch with a tall peaked hole through it, a lime lawn dome with round dark
   bushes, a sand floor through the hole; bottom-heavy pillars with skirt blocks and foot boulders.
2. **f34_sheet, front_sheet, side, top_sheet** per §2.6, including the hole numbers.
3. **Walk test (numbers):** the floor top 0.40 ± 0.03 everywhere in the tunnel; clear height over the floor ≥ 9.0 at
   x 0, ≥ 5.6 at |x| ≤ 3.2, ≥ 4.6 at the jambs (x ±3.4); clear width ≥ 6.8 from the floor to z 5.4 and ≥ 5.6 at
   z 7.0; no pebble or sprig taller than 0.6 inside the tunnel. On top: lawn ≥ 13.6 over the central 14 × 6, slope
   ≤ 25°, no rock or bush blocking a 3-wide walk from end to end over the crown (bushes on the rim only).
4. **Rock-shape targets** (§4.4) on the masses, the span and the boulders.
5. **Capping and contact** (§6). A **junction extra** `junc_cu (−60, 15)` framed on the left seat with the span lifted
   0.8 (part render) against the junction close-up; an **underside extra** of the span part at e −30 against the
   underside cell.
6. **Scale shot:** 5.5-stud character markers on the floor in the middle of the tunnel, on the apron beside a pillar and
   on the lawn top.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Mass cores | 2 | 300–400 | 600–800 |
| Skirt blocks | 8–10 | 20–30 | 180–280 |
| Foot boulders | 8 | 16–24 | 130–190 |
| Span | 1 | 260–360 | 260–360 |
| Lawn caps (span + 2 masses) | 3 | 90–130 | 270–390 |
| Floor tiles | 10–12 | 20–28 | 220–320 |
| Pebbles (lawn 16, apron 8, floor 6) | 30 | 6–8 | 180–240 |
| Dark bushes (8 rim + 1 jamb foot) | 9 | 60–80 | 540–720 |
| Foot bushes | 6–8 | 35–50 | 230–380 |
| Sprigs | 10–12 | 15–25 | 160–280 |
| Yellow flowers | 12–16 | 10–14 | 130–210 |
| Apron, ledge pads, tunnel strips | 1 + 3 + 2 | 10–60 | 120–180 |
| **Hero** | | | **about 3000–4100**, plan ≈ 3600 (limit 4000) |
| Parts: Span / MassL / MassR / Sill | | | 700–900 / 800–980 each / 260–380 (limit 1000) |

- **The mass parts are tight.** If a mass is over 950, tag its ledge-pad sprigs, flowers and one foot boulder
  `on="hero"` before thinning a column or a rim bush.
- **If the hero is over 3900:** drop hidden back leaves, then lawn pebbles (to 10), then apron sprigs (to 3), then foot
  flowers (to 6). Never drop a rim bush the f34 or front shows, never thin a column below §4.4, never simplify the
  crown.

### 4.4 Rock-shape targets (binding; check with `M.audit`, own bmesh code and M040's `rock_metrics`)

| Target | Mass columns | Span lumps | Skirt blocks | Foot boulders | Pebbles |
| --- | --- | --- | --- | --- | --- |
| Sides | 3 per front / back face, 4 per end | 4 front + 4 back | 5–7 + pitched top | 5–7 | 4–6 |
| Facets visible per piece | 2–4 per column | 6–9 per lump | 3–5 | 5–8 | 2–3 |
| Facet shape | **tall strips h/w 2.5–4.5** on the outer faces | broad, h/w 0.6–1.5 | tall, h/w 1.5–3 | broad, h/w 0.8–2 | broad |
| Top | shoulders under the turf; no flat exposed top | under the turf | **pitched ≥ 30°**, or a turfed pad ≤ 1.2 | **pitched 3–4-facet crown**, crown ≥ 0.5 W at 0.8 H | flat-ish |
| Side faces within 20° of vertical | ≥ 80 % of outer-face area (the shoulders round over) | — | ≥ 60 % | ≥ 40 % | — |
| Profile | battered 0.3–0.6 | — | widest at 0.2–0.4 h | widest at 0.3–0.5 h, **H / W 0.8–1.3** | H / W ≤ 0.6 |

- **Irregular, not a pattern:** triangle area CV ≥ 0.6 on each mass and on the span; no vertex ringed by 5–6 near-equal
  triangles. Never `primitive_ico_sphere`, subdivision, displacement or `K.hull_rock` jitter balls (egg boulders, M034 /
  M037).
- **The opening outline is the arch's identity:** jambs planar within ±0.3 and vertical within 4° up to z 5.4; the
  crown 2–3 facets a side and a sharp apex (no flat lintel bottom, no round tube; W02's R1).

### 4.5 Stages 2 and 3

- **Stage 2:** every shell closed and manifold; zero non-manifold edges and verts (`nonmanifold_verts` 0), boundary,
  wire and loose elements; 0 self-intersecting pairs within a shell; no zero-area faces or n-gons; normals outward; no
  corners under 5° on visible faces (`m011._tidy` / `_desliver`); the seat faces planar at z 8.0 ± 0.001; the floor tops
  at 0.40 ± 0.03.
- **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 30 × 30 box inside each, sd ≤ 1.7)

| Swatch | Box | Hex | HSV | Channel order | Use |
| --- | --- | --- | --- | --- | --- |
| Rock Light (pale stone) | (31,220,61,250) | `#CEBCB5` | 17°, 0.12, 0.81 | R > G > B, R − B 25 | hue reference only; too pale and pink for a key |
| Rock Shadow (cool gray) | (31,268,61,298) | `#8D9383` | 82°, 0.11, 0.58 | **G > R > B** (green-grey) | **never used** (§3.9) |
| Grass | (31,317,61,347) | `#BED120` | 66°, 0.85, 0.82 | G > R > B | hue reference; the rendered lawn is brighter and more saturated |
| Dirt | (31,365,61,395) | `#B0744B` | 24°, 0.57, 0.69 | R > G > B | hue reference for the floor (§3.5) |

### 5.2 Rendered regions (`samp.py`, `samp_out.txt`; median / lit quartile / shade quartile)

| Region | f34 | front | side | top | exploded / close-ups |
| --- | --- | --- | --- | --- | --- |
| Rock warm faces (h ≤ 60) | **`#C7A99A`** (20°, .23, .78) / `#EBD0BC` / `#7D6A66` | `#CCAC9B` (21°, .24) / `#ECD1B9` | `#CDAE9D` (21°) | `#C6A798` | expl `#D4B29E` (22°, .25); junction `#E2C2AF` (ledge lit) |
| Rock cool faces (the shade light) | `#6B6E7E` (231°) | `#6E6E81` (240°) | `#676F84` (223°) | `#747382` | expl `#7A7584` (260°) |
| Warm share of rock | 58.4 % | 56.0 | 55.1 | 48.0 | expl 60.7; underside 38.2 |
| Rock all | `#9E8D8F` (353°) | `#A89392` (3°) | `#AC9593` (5°) | `#8A7F89` | — |
| Floor tops (P) | **`#F6BA80`** (29°, .48, .96) / `#F9BF86`; lit probe `#F8BE85` | `#E8B683`; strip probe `#F7C086` (31°, .46) | — | — | sill (pale stone) `#DAC2B9`; floor cu top `#F0D1B8` |
| Floor edges / tile sides (P, v < 0.85) | `#C09876` (28°, .39) | `#CB9F7E` (26°, .38) | | | floor cu lit side `#D2AD97` |
| Floor in the tunnel (shade, classed R) | probe `#7B6968` | | | | |
| Lawn (lime, not yellow) | **`#CFD809`** (63°, .96, .85) / `#D9E30F` / `#AFBE09` | `#C9D30A` | `#C6D20B` | `#CBD812` | expl `#CAD609`; junction `#D0D907` |
| Foot lawn (bottom zone, h < 70) | `#CAD006` | `#C6CC0C` | `#B7B823` | | |
| Bush foliage (all F) | `#407616` (94°, .81, .46) / `#83BE33` / `#24460D` | `#417518` | `#48741D` | `#4D7D1A` | expl `#417C1A` |
| Emerald leaves (h ≥ 95) | **`#1F6C21`** (122°, .71, .42) / `#338D30` | `#21661F` | `#246428` | `#227323` | expl `#1A6F21` |
| Fresh leaves (h < 95) | **`#577E0F`** (81°, .88, .49) / lit `#89CC35` | `#628011` | `#5F7F12` | `#5D8314` | expl `#648C13` / `#91D032` |
| Foot plants, fresh / deep | `#85BE1B` (81°) / `#276B20` (114°) | `#85AE25` / `#295620` | `#94C322` / `#275D2F` | | |
| Yellow flowers | `#E0DB1B` (58°, .88, .88) / `#EDE61C` | `#E4DB16` | `#E2D924` | `#DFD91F` | |
| Pebbles on the lawn | `#E8E3C9` (52°, .13) | | | `#DFD8C4` (44°, .12, .87) | |
| Trunks / soil hearts (D) | `#462304` (28°, .94, .27) | `#402005` | `#412405` | `#422307` | expl `#412105` |

### 5.3 How the colour works

**Rock.**
- **One pale warm peach-beige stone** for the masses, skirts, boulders and span. Warm faces are hue 18–24°, sat 0.20–0.26,
  **always R > G > B**.
- The sheet's shade faces are blue-lavender (223–260°): that is the fill light, and the tunnel's darkness is the light
  too. Our studio's shade is warm grey. **Never colour by facing**, and don't paint the tunnel walls darker by their
  normals.
- **The same stone family as M040 / M043 / M044** (their warm faces `#D4B29D` / `#D7B09C` / `#D6B7A3`; here `#C7A99A`,
  a step deeper), so an arch beside a cliff tile reads as one rock.
- **Painted signals by position:** the upper third of each column and the crown lumps' tops a step lighter; the lowest
  1.5 studs a touch deeper; optional `rock_deep` at ≤ 15 % on faces whose centre lies inside the tunnel volume (|x| < 3.6,
  |y| < 5.4, z < 9.5): a **position** test, checked with `K.check` < 0.5 (drop it if the check fails). Whole facets only,
  by height plus a broad noise field. **No moss on the column faces** (the middle fifth is bare).
- **Mauve guard (M031, M032 rounds 1–2, M037 m6, M040 m5):** every rock key R > G > B, hue 15–26°, R − B ≥ 30. The
  lavender shade, Rock Light `#CEBCB5` and Rock Shadow `#8D9383` are never keys, not even in a mix.

**Floor.** One warm sand (29–32°, sat 0.44–0.50, value ≥ 0.92) on every tile top; per-tile tint ±0.04; broad lighter /
deeper patches by a noise field; tile sides and bevels darker sand by **role** (a geometric band below each tile's top
bevel, never by normal direction), as M044 decision 11.

**Lawn.** One bright yellow-lime (62–65°, sat ≥ 0.92) on the cap, its lip, the ledge pads, the apron and the tunnel
strips. Lighter broad patches; slightly deeper within 0.8 of bush roots and at the apron's inner edge (by distance).

**Bushes.** Two tones in every bush, by role, never per face: upper / outer leaves fresh green (79–84°, lit toward
`#89CC35`), inner / lower leaves deep emerald (118–125°). Keep the two ≥ 35° apart in hue; the rim-bush median should land
near `#407616` (94°). Foot bushes carry more fresh green (≈ 60 / 40). A dark soil heart at the base.

**Flowers and pebbles.** Yellow petals 56–59° (yellow, not lime); pebbles cream-grey (40–50°, sat ≤ 0.14), lighter than
the rock.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are medians of unshadowed rendered regions (warm faces, lit lawns, bush medians), not swatches.
`K.sample` kinds: `"all"` for rock (M040's override: the stone filter drops sat > 0.18), `"brown"` for floor and trunk,
`"green"` for lawn and leaves, `"vivid"` for lime / yellow. **Start from M040's / M043's calibrated hexes** where the family
matches (M043: rock `#A48F85`, rock_light `#B29F93`, rock_deep `#978279`, grass `#A5B40C`, leaf `#456E19`, leaf_lit
`#67982C`, leaf_deep `#255D1F`, flower `#B1AA2A`, trunk `#552200`), then re-calibrate to these targets.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m046_rock` | **`#C9AA9A`** (warm faces: f34 `#C7A99A`, front `#CCAC9B`, side `#CDAE9D`, top `#C6A798`) | 18–24°, 0.20–0.26, R > G > B, R − B ≥ 30 | masses, skirts, span, boulders; default | rough 0.9, metal 0 |
| `m046_rock_light` | `#E6CBB7` (lit `#EBD0BC` / `#ECD1B9`; about +25 over `rock`) | 20–26°, 0.18–0.24 | upper 30 % of each column at 30–40 %; crown-lump tops at 40 %; boulder crowns at 30 % | rough 0.9 |
| `m046_rock_deep` | `#B39587` (a step below `rock`, hue kept warm) | 18–24°, 0.22–0.27, R − B ≥ 30 | below 1.5 studs at 15 %; hidden seats / joining faces; optional tunnel interior ≤ 15 % | rough 0.9 |
| `m046_floor` | **`#F6BC82`** (f34 `#F6BA80`, lit `#F8BE85`, front strip `#F7C086`; M044 path `#F7BB7B`) | 29–32°, 0.44–0.50, R > G > B | every tile top | rough 0.9, low spec |
| `m046_floor_deep` | `#C69C7A` (tile sides f34 `#C09876`, front `#CB9F7E`) | 25–29°, 0.36–0.42 | tile bevels and sides at 50 % (role) | rough 0.9 |
| `m046_grass` | **`#CCD60A`** (f34 `#CFD809`, front `#C9D30A`, rear `#CBD40B`, top `#CBD812`) | 62–65°, ≥ 0.92, G > R > B | cap, lip, pads, apron, tunnel strips; default | rough 0.85, low spec |
| `m046_grass_light` | `#D9E30F` (lit) | 62–64°, ≥ 0.90 | broad patches at 20 % | rough 0.85, low spec |
| `m046_grass_deep` | `#ADBC09` (shade `#AFBE09`) | 64–67°, ≥ 0.90 | within 0.8 of bush roots; the apron's inner edge; at 25 % | rough 0.85, low spec |
| `m046_leaf` | `#407616` (F medians `#407616`–`#4D7D1A`) | 90–96°, 0.75–0.82 | bushes' middle leaves | rough 0.85, low spec |
| `m046_leaf_lit` | `#82C032` (fresh `#577E0F` → lit `#89CC35`; foot `#85BE1B`) | 79–86°, 0.72–0.86 | bushes' upper / outer tier at 60 %; foot bushes' outer leaves; sprigs | rough 0.85, low spec |
| `m046_leaf_deep` | `#1F6A21` (h ≥ 95: `#1F6C21`, `#21661F`, `#246428`, `#1A6F21`) | 118–126°, ≥ 0.65 | bushes' inner / lower leaves at 60 % | rough 0.85, low spec |
| `m046_flower` | **`#E2DB1A`** (f34 `#E0DB1B`, front `#E4DB16`) | 56–59°, ≥ 0.84, R ≥ G ≫ B | petals | rough 0.8, low spec |
| `m046_pebble` | `#DDD6C3` (top `#DFD8C4`, f34 `#E8E3C9`) | 40–50°, 0.10–0.14, R ≥ G > B | pebbles on lawn, apron and floor | rough 0.9 |
| `m046_trunk` | `#4A2607` (D `#462304`, `#402005`, `#412405`) | 24–30°, 0.85–0.95 | bush hearts, trunks | rough 0.95 |

**Calibration warnings:**
- **Rock:** calibrate `m046_rock` on the parts shot's masses (warm faces) against `#C9AA9A`. Then check the f34_sheet
  warm-face median within 10 of `#C7A99A` and the front_sheet within 10 of `#CCAC9B`; R > G > B, hue 15–26°. Whole-rock
  medians run warmer than the sheet's (`#9E8D8F` f34, 353°) because our shade is warm, not lavender: a median at hue
  15–26° missing by ≤ 15 levels is a known miss, not a key error.
- **Floor:** f34 floor median within 12 of `#F6BA80`, hue 29–32°, sat ≥ 0.42: warm sand, clearly more saturated than the
  rock (rock ≤ 0.26). Not brown, not pink, not pale stone.
- **Lawn:** f34 lawn within 14 of `#CFD809`, hue 62–65°, sat ≥ 0.92. "Greens slightly grey" (M038) is the miss to avoid.
- **Leaves:** f34 F median within 14 of `#407616`; the emerald at hue ≥ 115° and the fresh tone ≤ 88° both visible in
  the f34 crop (M035 "lit foliage dark and less lime", M036 "back greens dark", M039 "shade halves olive").
- **Flowers:** within 14 of `#E0DB1B`, hue 56–59°.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Rock** (on the original facets, before any refine): `rock` base; `rock_light` by height within each column (faces
  with centre z above 0.65 of the column's top, rising to 40 %) and on the crown lumps' upper faces at 40 %; `rock_deep`
  by a noise field (scale ≈ 0.2) below 1.5 studs (15 %); per-column, per-lump and per-boulder tint ±0.04.
- **Floor:** `floor` base; per-tile tint ±0.04; `floor_deep` by role on the bevels and sides (50 %).
- **Lawn:** `grass` base; `grass_light` by a noise field (scale ≈ 0.25) at 20 %; `grass_deep` by distance (bush roots
  < 0.8) at 25 %. Average with neighbours before quantising (M034: no triangle shards); the three caps blend across the
  x ±6.7 seams with the same field (no colour step at a seam).
- **Leaves:** by role: upper / outer tier `leaf_lit` 60 %, middle `leaf`, inner / lower `leaf_deep` 60 %.
- **Hard edges only** where materials meet: lawn | rock (the lip), tile | lawn, leaf | heart, petal | centre.

### 5.6 Texture (Tint) and finish

- **Tint:** rock amp 0.04, scale 0.3, per original facet; floor 0.04 per tile plus 0.03 at scale 0.4; lawn 0.04, scale
  0.4; leaves 0.04 per leaf; petals 0.02; pebbles 0.03; trunks none. Never per-triangle confetti.
- **Finish:** rock rough 0.9, metal 0; floor rough 0.9, low spec; lawn and leaves `low_spec=True`, rough 0.85; petals 0.8;
  trunk 0.95. No emission anywhere.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Rock:** f34_sheet and front_sheet warm-face medians within 10 of `#C7A99A` / `#CCAC9B`; parts-shot warm median within
  10 of `#C9AA9A`. All R > G > B, hue 15–26°, in every view including the side, rear and the tunnel (mauve guard).
- **Floor / lawn / leaves / flowers:** per the §5.4 warnings. **Shares** per §2.6.

## 6. Joins and contact (no floating dressing)

- **The span on the seats:** both seat faces on the ledges at z 8.0 (coplanar touching, or sunk 0.02); the span's end
  faces on the masses' joining faces at x ±6.7 (overlap 0.02–0.05). **No gap anywhere a camera can see through:** rays
  from the 8 sheet cameras through the joints (the front / back creases at z 8 and x ±6.7, the lawn seams) hit rock or
  lawn, never the background. The crown's apex and the haunch tips meet the masses' corners within 0.02 (no step in the
  opening's outline at z 8.0 bigger than 0.1).
- **The sill:** its tiles sit on the ground (z 0), tops at 0.4; the tunnel strip runs 0.2 under each jamb foot (the
  notched ends); the flares butt the foot boulders and the apron (gap ≤ 0.02). No ground showing between the floor and
  the jambs from any camera.
- **The lawn caps:** each cap's underside on its rock (sunk 0.02); the three caps share edge vertices at x ±6.7 at one
  height; the lip overhangs the rim 0.2–0.4 and its drop reaches 0.1 below the rim edge, so **no crack** shows between
  lawn and rock.
- **Capping numbers (M032 round 1, the blocker; M040 §2.5; M043 decision 5).** From straight above, inside the rock
  footprint:
  - flat rock top area (n.z > 0.85) above z 12 not under lawn: **0 studs²** (masses and span);
  - turfed skirt pads: their flat crowns fully under the pad;
  - visible rock from above: battered faces, skirt and boulder crowns, pebbles; **≤ 70 studs²** (the battered faces and
    foot pieces are visible in the top cell's lower part, but no table top);
  - lawn visible ≥ 150 studs² (the cap less the bushes).
- **Plants:** roots on the turf (sink 0.03) or the ground; every leaf within 0.03 of its heart or trunk and chained by
  contact to the turf (STAGES: no hidden stems); every petal on its centre, every centre on the turf; leaves may touch
  rock but cut no more than 0.05 into it (M039 finding 3, M036 finding 10).
- **Count floating shells before reporting** (STAGES; 035 and 036 failed round 1 on this): **0**. A shell floats if its
  nearest distance to every other shell and the ground is > 0.03, or if it doesn't chain to the ground. The span chains
  through its seats to the masses; the masses and the sill stand on the ground.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0 (bush hubs, petal centres, tile bevel corners,
  the span's apex ridge).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** sunlit rock, lawns, bushes, flowers and a sand floor; the tunnel is in plain shade. No glow,
light, sparkle, water, dust, particles or VFX callout.
- **Stage 5 (lighting): skip, and record why.** No emissive faces, no PointLight. Studio notes (Requires Manual
  Validation):
  - the rock stays warm beige (not lilac) under the game's sun and matches an adjacent M040 / M043 tile;
  - the tunnel reads in shade but not black (Studio's ambient; no light needed);
  - the floor reads warm sand, clearly separate from the rock;
  - the column facets read as separate planes (flat shading kept);
  - **a character walks through the tunnel without crouching or snagging, and onto the lawn top from a 10.4 plateau with
    one jump**;
  - the lawn stays yellow-lime, the flowers yellow.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** Not recommended: dust motes in the tunnel, pollen over
  the lawn.
- **Collision (decision §8.12):** hero `precise` (the tunnel and the lawn top are both walk surfaces); `StoneGateSpan`
  `hull` (its hull's bottom is the seat plane at 8.0 across the opening: above head height); `StoneGateMassL` / `R`
  `hull` (each mass is near-convex; the hull fills the ledge notch, which the span covers anyway, and must not reach
  past the jamb: check the hull's inner face stays at x ±3.5 below z 5.4); `StoneGateSill` `box`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by searching `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json`, the repo
text (`git grep`) and every sheet / kit / wip `.blend` (zstd-decompressed) with `blendall.py`:
- **W02** owns `NaturalArch`, `NaturalArchBroken`, `NaturalArchGroundSill`, `NaturalArchLeftMass`, `NaturalArchNarrow`,
  `NaturalArchRightMass`, `NaturalArchTopSpan`, `NaturalArchWide`; they occur in `FlintbornWorldKit.blend`, `W02.blend`
  and every wip copy. Keys are `w02_*`.
- **W16** owns `StoneArch`, `StoneArchBaseStone`, `StoneArchHalfCollapsed`, `StoneArchKeystone`, `StoneArchPierBlocks`,
  `StoneArchPointed`, `StoneArchRound`, `StoneArchCollapsed`, `StoneArchWedge*` … (so **no `StoneArch*` name**, not even
  `StoneArchway`, which would share the prefix).
- **Sheet 07** owns `RockArch` (`build_07_terrain_kit.py`, the lobby); M021 owns `ArchedRootCluster*`; M029 owns
  `SapstoneRootArch*`.
- **M040** owns `StoneCliff*`, **M043** `StoneTerrace*`, **M044** `StoneRamp*`, **M039** `StoneSpire*`.
- **`StoneGate`, `CragArch` and `m046_` occur nowhere** in the repo text, the manifests or any `.blend`. `M.mk` would
  silently rename a clash to `<name>M046`; the names below don't clash.

| Object | Part | Why |
| --- | --- | --- |
| `StoneGate` | hero: span + masses + sill + lawn caps + dressing | W02 owns `NaturalArch`, W16 `StoneArch`; parallels `StoneCliff`, `StoneTerrace`, `StoneRamp`, `StoneSpire` |
| `StoneGateSpan` | "Top Span" + its lawn cap and rim dressing | |
| `StoneGateMassL` / `StoneGateMassR` | "Left / Right Rock Mass" + skirts, boulders, their caps and rim bushes | |
| `StoneGateSill` | "Ground Sill (Floor)": flagstones + floor pebbles | |

- Palette keys `m046_*` (§5.4). Collection `Kit/M046 Natural Arch`. No sockets.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1, §3.1): **rock 24 W × 12 D, lawn top 14.0, opening 7.0 wide × 9.0 clear (apex 9.4 above the ground,
   floor 0.4), spring line 5.4** (recommended: the sheet's proportions, a comfortable walk-through for the 5.5
   character, the 4-stud grid, a one-jump step from the 10.4 plateau).
   - Or **lawn at 10.4** (18 × 9; opening 5.1 × 6.6): on the plateau level, but a cramped doorway.
   - Or **32 W** (opening 9.3 × 12, lawn 18.7): oversized against the plateaus.
2. **Free-standing** (§3.2): **rounded columned ends, no seam planes; "modular" = the four parts with flat internal
   joining faces** (recommended). Or flat seam ends at x ±12 for cliff runs (not drawn).
3. **Back face and r34** (§3.3): **a varied mirror of the front; rear / r34 judged as repeats** (recommended).
4. **Joining faces** (§3.4): **flat ledges at z 8.0, flat joining faces at x ±6.7, flat span seats, notched sill ends; no
   block tabs; faceted tunnel walls** (recommended). Or 2 hidden tabs and sockets per seat (+40 tris).
5. **Floor** (§3.5): **sand flagstones (`#F6BC82`, M044's family), 10–12 tiles 0.4 thick, a tunnel strip x ±3.7 flaring to
   x ±5.6 at the mouths, inside the footprint** (recommended). Or a pale-stone sill (the exploded's colour).
6. **Span** (§2.2): **13.4 wide, one closed shell built directly, 4 lumps a face, seats on the ledges, soffit 2–3 facets a
   side to a sharp apex at 9.4** (recommended). Or the span as 4 separate lump shells overlapping (more shells, easier
   relief, but joints to check for see-through).
7. **Packaging:** **one hero object of closed shells built strictly from the four parts plus hero-only foot dressing; mass
   cores built directly (M043's approach) or a merge-0 union at the origin; nothing else unioned** (recommended).
8. **Lawn** (§2.4): **one cap per part, seams at x ±6.7 with coincident edges; a flat-ish dome 14.0 → 13.4, a lime lip
   over the rim, draping down the shoulders to z 10.5–11; 8 rim bushes; the middle open** (recommended). Or one
   continuous hero cap plus separate part caps (no seams in the hero, but the hero is then not built from its parts).
9. **Comparison cameras** (§2.6): `f34_sheet (−35, 18)` governing (probe az −28 / −35 / −42 × e 12 / 18 / 24);
   `front_sheet (0, 8)` strict, with the hole numbers (probe e 4 / 8 / 12); `side (90, 8)`; `top_sheet (0, 60)` (probe
   e 50 / 60 / 70: it's an oblique); `rear_sheet (180, 8)` and `r34_sheet (145, 18)` as repeats. Extras: parts shot
   (−30, 25), the span underside (e −30), `junc_cu`, `floor_cu`, the scale shot. Hide the floor in every `*_sheet` render.
10. **Colour** (§5): **one warm beige stone `#C9AA9A` (R > G > B, never mauve, Rock Shadow `#8D9383` never used), sand
    floor `#F6BC82` with role-darkened tile sides `#C69C7A`, lime lawn `#CCD60A`, two-tone bushes (`#82C032` fresh /
    `#1F6A21` emerald, median `#407616`), yellow flowers `#E2DB1A`, cream pebbles `#DDD6C3`, soil hearts `#4A2607`**
    (recommended). Blend by position, never by facing.
11. **Stages 5 and 6:** **skip both, recorded** (recommended).
12. **Collision** as in §7 (recommended).
13. **Budget** (§4.3): **4000 limit, plan about 3600, parts under 1000 with hero-only tags on the masses as needed**
    (recommended).
14. **Names** as proposed: `StoneGate*`, keys `m046_*` (recommended). Or `CragArch*` (also free).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **W02's arch failures (`MODEL_PROGRESS` row 51: "narrow low opening, flat top slab; flat side; narrow pillars"; its
   R1 "nothing hangs into the hole top").** The opening is **7.0 × 9.0 clear with a sharp peaked crown** (no flat lintel
   bottom, no hanging slab); the span is a thick lumpy lintel under a draped lawn, not a flat slab; the ends are
   columned and battered, not flat; each pillar is ≈ 8.5 wide at the base and bottom-heavy.
2. **A see-through crack at a joint.** Seats, end faces, lawn seams and the sill / jamb joins must be closed to every
   sheet camera (§6). The only see-through is the opening.
3. **The lawn as a table-top slab (M040 m1) or a cap that doesn't cap (M032 round 1, the blocker).** The lawn drapes over
   the shoulders with a scalloped lip, its edge broken by the crown lumps and the bushes; **0 studs² of flat rock top
   exposed**; turfed skirt pads cover their flat crowns.
4. **Palm-star or spiky bushes (M040 m2; M039 round 1 blocker; M036 rounds 1–2).**
   - Rim bushes are round domes Ø 2.4–2.8 with a crown tier of 4–5 leaves pitched up and out; the dark heart shows only
     at the base.
   - Leaves are broad rounded ovals: tip angle ≥ 110°, camber ≤ 0.07 L, no kite or diamond outlines.
   - **Edge-on leaves (M039 round 2, finding 1):** ≤ 12 % of leaf area within 12° of edge-on at the f34 camera, 0
     undersides showing; turn low leaves to the sides rather than toward the camera.
   - Petals are broad and rounded, lying on the turf.
5. **Floating dressing (STAGES; 035 and 036 round 1).** Every leaf, petal, flower centre, pebble and boulder within 0.03
   of a neighbour, its turf, a tile or the ground, chaining to the ground. Count floating shells: **0**. And the span
   itself must chain through its seats (it is not hovering if the seats touch).
6. **Egg boulders (M034 round 1 blocker; M037 m5 egg-shaped parts).** Foot boulders are faceted gems with pitched 3–4-facet
   crowns, H / W 0.8–1.3, widest low; skirt blocks tall with pitched tops; pebbles flat-ish. No ico-spheres, no
   `hull_rock` jitter balls, no smooth tapering ovoids.
7. **Column rock that reads as smooth prisms or soccer balls (M037 m4 "organ pipes", M023, W02 "low smooth cliffs").**
   Columns 2.0–3.5 wide with tall strip facets (h/w 2.5–4.5), creases 0.4–0.6 deep, a mid-ridge per face and a facet break
   on some columns; varied heights; no subdivision, no smooth shading.
8. **Mauve, blue or olive rock (M031, M032 rounds 1–2, M037 m6, M040 m5).** Every rock key R > G > B, hue 15–26°,
   R − B ≥ 30, in every view including the tunnel and the side. The lavender shade, Rock Light `#CEBCB5` and the
   green-grey Rock Shadow `#8D9383` are references only.
9. **Colour by facing.** The peach-lit / lavender-shade split and the dark tunnel are light. Height fields, noise patches,
   distances, roles and the tunnel-volume test only; `K.check` facing correlation < 0.5 per material (watch the floor's
   tile-side role and any tunnel tint).
10. **Lawns too dark, grey or olive (M035, M038); leaf shade halves olive (M039 m2).** f34 lawn within 14 of `#CFD809`;
    the emerald stays ≥ 115° and green, not olive.
11. **Big flat triangles in the lawn (M040 m6) and triangle shards (M034 m5).** CDT resampled at ≤ 1.0, blends averaged
    with neighbours, no colour step at the cap seams.
12. **An unwalkable opening or top.** Floor 0.40 ± 0.03; clear width ≥ 6.8 to z 5.4; apex ≥ 9.0 over the floor; nothing
    taller than 0.6 inside the tunnel; lawn top ≥ 13.6 and ≤ 25° over the central 14 × 6.
13. **Dressing cutting into rock (M039 m3, M036 m10: up to 0.47 claimed as ≤ 0.05).** Leaves and petals ≤ 0.05 into rock,
    measured with a ray-parity test, and reported honestly.
14. **Bowties** at bush hubs, petal centres, leaf roots, tile bevel corners and the span's apex ridge: `M.fix_bowties` on
    every object, `nonmanifold_verts` 0.
15. **Exact booleans** (STAGES "Booleans"): only inside a mass core if it isn't built directly, at the world origin, one
    piece at a time, saving between them, merge-0. Nothing between parts.
16. **Budget.** Foliage and flowers are about 40 % of the count. The mass parts are tight (≤ 1000): tag pad sprigs,
    flowers and a foot boulder hero-only before thinning a column or a rim bush.
17. **Names and scope.**
    - No `NaturalArch*` (W02), `StoneArch*` (W16), `RockArch` (07), `StoneCliff*` (M040), `StoneTerrace*` (M043) or
      `StoneRamp*` (M044).
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit `m040.py`, `m043.py`, `lib/vfx.py` or the shared helpers (frozen).

## Decisions (main session, 2026-10-29)
All 14 recommendations are accepted, with notes on 7 and 10.

1. **Size:** rock 24 W × 12 D, lawn top 14.0. Opening 7.0 wide, 9.0 clear over a 0.4 floor, springing at 5.4. A 5.5-stud character must pass with room.
2. **Ends:** free-standing, with rounded column ends and no seam planes.
3. **Back face:** a varied mirror of the front.
4. **Joints:** flat ledges and seats, faceted tunnel walls, no tabs. **No see-through cracks at joints.**
5. **Floor:** sand, the same family as M044's path.
6. **Span:** one closed shell, 4 lumps per face, sharp apex.
7. **Packaging:** the hero is built strictly from the parts.
   - Mass cores are built directly, or as a merge-0 union at the origin.
   - Every shell is manifold with 0 bowties.
   - **No floating dressing.**
   - Dressing cuts at most 0.05 into rock.
8. **Lawn:** one cap per part, with matching seams at x ±6.7. **The lawn caps every rock top; no flat exposed tops** (M032).
9. **Cameras:** `f34_sheet (−35, 18)` governs. `front_sheet (0, 8)` is strict on the hole numbers. Top is judged at about (0, 60).
10. **Colour:**
    - Rock `#C9AA9A` (R > G > B; never mauve or olive; never the Rock Shadow swatch).
    - Floor `#F6BC82`, with tile sides `#C69C7A` as a geometric band below each tile's top bevel, never by normal; `K.check` < 0.5.
    - Lawn `#CCD60A`.
    - Bushes are rounded two-tone domes `#82C032` / `#1F6A21`, not palm stars, spiky or edge-on.
    - Flowers `#E2DB1A`, pebbles `#DDD6C3`, soil `#4A2607`.
    - Blend by position, never by facing.
11. **Lighting and VFX:** none; both stages are recorded as skipped.
12. **Collision:** hero precise, span and masses hull, sill box.
13. **Budget:** 4000 tris, about 3600 planned. Tag dressing hero-only where the parts are tight.
14. **Names:** `StoneGate*`, keys `m046_*`.

**Binding targets:** the f34 shares in §1 (within ±4) and the front-cell opening numbers.
