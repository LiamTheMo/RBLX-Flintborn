# 046 Natural Arch — spec

Reference: `art/blender/assets/references/046.png` (1024 × 1536 px). The sheet's title is "NATURAL ARCH", with
"FLINTBORN ENVIRONMENT MODEL CATALOG / STYLIZED • MODULAR • GAME-READY (BLENDER / ROBLOX)" at the top right. Its page
number reads "PAGE 44/132" (bottom right), two less than the file number; INDEX.md row 46 calls it "Flintborn Natural
Arch Model Study". The footer reads "FLINTBORN — INDIVIDUAL MODEL STUDY".
Builder: `art/blender/kit/mcp/m046.py` → `build()` (stages 1–6 done 2026-10-29). Procedure: `art/blender/kit/mcp/STAGES.md`. One
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
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m046_study\`.
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

## Stage 1: Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m046.py` (`build()`; quick loops `hero_only()`, `preview()`), built in a background Blender
(port 9882, `wip/M046.blend`). It imports M040's generic helpers (CDT, Steiner points, hull pieces, dome heart, prism,
`_touch`, `_Guard`, the shell / contact / rock-metric reports) and M043's rounded leaves (`_tleaf`, `_rleaf`). Nothing
in `m040.py`, `m043.py` or the shared helpers was edited. The final check ran in a freshly restarted session.

- **Mass cores (`mass_core(sx)`, Left / Right Rock Mass): each ONE closed shell built directly, with no boolean.**
  - A chain of 31 column points runs round a base path: front jamb corner → front → a radius-3.2 corner → end → corner →
    back → back jamb corner → 3 jamb-face points.
  - There are 9 columns per mass: 3 on the front (including the jamb column), 3 round the end and 3 on the back. Each
    column has a crease (pushed in 0.64–0.84), a face and a ridge (pushed out 0.24–0.36).
  - Each chain point is a vertical column of verts, and neighbouring columns are zipped into quads and tris.
  - **Stacked blocks.** Each column has its own three levels, shared by all its points, so the facet breaks run across
    the column (the sheet's lumpy stacked columns):
    - a lower bulge at 1.9–3.1;
    - a block joint at 4.4–6.2, set back 0.12–0.22;
    - an upper bulge at 7.4–9.6.
  - Batter by height follows `S_FRONT` and `S_END` (the spec §2.3 table).
  - The column tops are solved onto the dome `zt(x, y)`: 13.4 over the middle, the shoulders falling over the ends and
    the rims rounding front and back. Creases and ridges take the top height of their un-pushed path point, so the top
    ring does not zigzag.
  - **The opening side.** The jamb face is vertical (x 3.5–3.75, relief only into the rock) from 0 to the spring at 5.4.
    The haunch then runs to the tip at x ±2.25 at 8.0 through (±3.2, 6.2), (±2.85, 7.0) and (±2.55, 7.6).
  - **Hidden joining surfaces:**
    - the flat ledge at z 8.0 (a CDT from the haunch tips out to x ±6.7);
    - the flat joining face at x ±6.7 (z 8.0 up to the dome);
    - the top under the lawn (a CDT with interior points on the dome);
    - the flat bottom.
  - The joint lines at x ±6.7 (front and back) are shared with the span's end rings.
- **Skirt blocks (8) and foot boulders (8)** are closed hulls.
  - Skirts are 2.6–3.2 along the face, 1.6–1.7 deep and 4.0–5.7 tall. Each has a 5-sided foot, its widest ring at 0.32 h,
    a 4-point shoulder at 0.68 h and a pitched ridge top (two points at ±0.28 w).
  - Three skirts (SK_L2, SK_L3, SK_R2) have a small flat crown (≤ 1.2) under a lime ledge pad.
  - Boulders are chunky gems: a 5-sided foot, widest at 0.42 h, a 3-point crown ring at 0.8 h (0.64 W) and an off-centre
    apex. H/W is 1.05–1.23, and each long axis runs along its face.
  - A piece whose hull would have a corner under 5° is rebuilt with the next seed.
- **Top span (`span()`): ONE closed shell.** It is a loft of 13 rings along X (±6.75, ±5.0, ±3.35, ±2.3, ±1.85, ±1.2, 0).
  - **Faces.** The front and back faces have rings at the bottom, 10.0, 11.8 and the top, with four lumps per face. The
    front peaks at ±5.0 and ±1.2 with creases at ±3.35 and 0; the back is staggered. The lumps bulge most at mid
    height.
  - **Bottom.** It is flat at the seat (z 7.98) for |x| ≥ 2.3, sunk 0.02 into the ledges. The soffit runs (2.3, 7.98) →
    (1.85, 8.3) → (1.2, 8.7) → (0, 9.44–9.49), with ±0.12 relief across the depth.
  - **Top.** A CDT on the dome.
  - **Ends.** The end rings sit 0.05 inside the masses (at x ±6.75, the joint line moved 0.03 in), so the span and mass
    joints overlap and cannot crack.
- **Lawn caps (`lawn_cap`), one per part.**
  - **Outline.** The rock top ring pushed out 0.18–0.28 (the lip foot), with the lawn's top edge 0.15 outside the rim.
  - **Lip.** It drops 0.38–0.62 below the rim, so the lawn caps every rock top and its underside dips below the rim all
    round.
  - **Top.** A CDT with an inner ring 0.95 inside the edge plus interior points; the lawn is 14.0 in the middle.
  - **Seams at x ±6.7.** Both caps use the same seam points (the corners, ±3.3 and 0) and overlap by 0.03. They can't
    share the points, because the kit merges coincident verts.
- **Sill (`sill()`, Ground Sill): 12 sand flagstones.**
  - The tiles are Voronoi cells of three convex pieces: the tunnel strip (x ±3.7, y ±4.8) and the two mouth flares (to
    x ±5.8 at y ±6.8).
  - Short and straight corners are cleaned off, and each cell is inset 0.025 (seams 0.05).
  - Each tile is a closed slab with its top at 0.40 ± 0.02, running 0.2 under each jamb foot.
- **Dressing:**
  - 8 rim dome bushes, 2.3–3.0 across and 2.0–2.5 tall (4 on the span, 2 per mass);
  - a jamb-foot dark bush, 7 small foot bushes and 3 pad bushes;
  - 4 sprigs (2 on the apron, 2 along the tunnel wall feet);
  - 10 pebbles (3 on the span, 1 per mass, 2 on the apron, 3 on the floor) and 8 five-point yellow flowers;
  - two lime aprons (bevelled strips 0.7–1.25 wide, tucked 0.45 under the rock) and two lime strips along the tunnel's
    wall feet.
- **How the bushes are built:**
  - a hidden faceted heart, its underside soil-dark;
  - broad rounded leaves laid tangent on the heart: dark bushes 3 crown + 4 skirt, small 2 + 3, pad 2 + 2;
  - each leaf is slid onto the heart, guarded out of the rock (≤ 0.05 in) and kept above the turf it sits on.
- **Hero `StoneGate`:** the four parts plus the hero-only foot dressing, as one object of 204 closed shells, with no
  booleans.
- **Cameras:**
  - **`f34_sheet`:** probed az −25 / −28 / −30 / −35 × e 14 / 18, with the long lens and with perspective, and kept
    **(−28, 18)**, which is in decision 9's probe set.
    - At (−28, 18) the W:H is 1.254, the shares are within ±4, and a sliver of paper shows through the tunnel.
    - At −35 the W:H is 1.208, under the 1.22 floor.
  - **`f34_see_sheet` (−22, 18), extra.** A 12-deep tunnel with a 7-wide mouth can only be seen through below about
    az −30, so this view shows the see-through (the hole is 0.09 × 0.19 of the frame, centred at 0.507).
  - **`front_sheet`** stays at (0, 8) as decided.
  - **`front_level_sheet` (0, 4), extra.** It is the level end of the study's e 4–12 fit, and carries the hole numbers.
  - **Others:** side (90, 8), rear (180, 8), r34 (145, 18), top (0, 60).
  - Every `*_sheet` view uses a 3× lens with the floor hidden.

## Stage 2: Optimisation and cleanup (modeller)

| Object | Tris (limit) | Size W × D × H | Shells |
| --- | --- | --- | --- |
| `StoneGate` (hero) | **3932** (4000) | 25.62 × 14.14 × 16.00 | 204 |
| `StoneGateSpan` | 862 (1000) | 13.50 × 11.76 × 8.02 | 39 |
| `StoneGateMassL` | 966 (1000) | 10.49 × 13.23 × 15.21 | 39 |
| `StoneGateMassR` | 900 (1000) | 10.51 × 13.34 × 15.37 | 33 |
| `StoneGateSill` | 184 (1000) | 11.48 × 13.55 × 0.50 | 15 |

- **Hero tris by kind:**

  | Kind | Shells | Tris | Breakdown |
  | --- | --- | --- | --- |
  | rock | 19 | 1400 | cores 338 / 340, span 294, skirts 28–32, boulders 24 |
  | lawn | 10 | 728 | caps 196 / 112 / 112, aprons, pads, strips |
  | tiles | 12 | 160 | |
  | leaves and petals | 153 | 1564 | |
  | pebbles | 10 | 80 | |

- **Every object** has:
  - 0 non-manifold edges and **0 non-manifold (bowtie) verts**;
  - 0 boundary or wire edges, 0 loose verts, 0 zero-area faces, 0 n-gons and 0 duplicate verts;
  - normals outward and transforms applied;
  - every shell closed with positive volume, with 0 self-intersecting pairs and 0 inverted faces (ray parity).
- **Winding (STAGES, the 044 lesson): 0 winding errors and 0 unpaired edges on every object.**
  - `winding_report` counts directed edges used twice or without a partner.
  - The span, cores and tiles are hand-built. Every shell's normals are recalculated and then checked this way.
  - `build()` lists any winding error as a problem.
- **No face has a corner under 5°** on any object. The smallest are 5.45° (hero), 7.88° (span) and 8.27° / 6.41°
  (masses). Getting there took four changes:
  - the span's top is a CDT, not long loft strips;
  - the tile top bevel ring was dropped: a 0.06 bevel along 2–4-stud edges can only be built from slivers, so the 0.4
    side carries the darker sand band instead;
  - the aprons and tunnel strips have bevelled edges;
  - the column levels are shared between the jamb-side columns and the joints.
- **Origins** are at the bottom centre. The offsets of the build frame (`m046_offset`):

  | Object | Offset | Note |
  | --- | --- | --- |
  | hero | (−0.011, −0.101, 0.0) | the y part is the dressing's front / back asymmetry |
  | span | (0, 0.015, 7.98) | |
  | MassL | (−7.495, 0.027, 0) | |
  | MassR | (7.504, −0.119, 0) | |
  | sill | (0, 0, 0) | |

- **Floating shells: 0** on every object (`contact_report`). For the hero: 204 shells, worst gap 0.0, max gap 0.003,
  and 0 unchained at both 0.03 and 0.1. The span chains through its seats to the masses.
- **Capping.**
  - Flat rock (n.z > 0.85) seen from straight above **above z 12: 0.0 studs²**.
  - Flat rock seen from above anywhere: 4.9 studs². This is:
    - thin strips of the hidden ledge at z 8.0, showing in front of and behind the span where a mass column stands proud
      of the span's foot;
    - boulder and skirt crown facets.
  - Everything seen from above inside the footprint, in studs²:

    | Lawn | Leaves | Rock (z ≤ 12) | Rock (z > 12) | Tiles |
    | --- | --- | --- | --- | --- |
    | 147.9 | 48.0 | 84.3 | 6.7 | 12.3 |

    The rock below z 12 is battered faces, skirts and boulders. The rock above z 12 is sloped battered faces just under
    the lip; none of it is flat.
  - Every rock top-ring point lies inside its cap's top edge, by ≥ 0.14 on the span and ≥ 0.051 on the masses.
  - The lip reaches ≥ 0.38 below the rim.
- **No light leaks.**
  - `crack_report` casts 972 rays at points 0.15 inside the solid, from the six sheet cameras plus three more.
  - The targets lie along the span / mass joint lines, the seat line, the cap seams and the floor / jamb joins.
  - Result: **0 leaks and 0 see-through.**
  - The only see-through is the opening. The enclosed background "specks" in the renders are gaps between bush leaves
    above the lawn (checked with a mask).
- **Walk test (rock only).**
  - **Clear width:**

    | z | 0.6 | 2.0 | 4.0 | 5.4 | 6.2 | 7.0 | 7.6 | 8.0 | 8.3 |
    | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
    | width | 7.08 | 7.14 | 7.11 | 7.05 | 6.43 | **5.72** | 5.11 | 4.54 | 3.61 |

  - **Clear height over the floor:**

    | x | 0 | ±1 | ±2 | ±3.2 | ±3.4 |
    | --- | --- | --- | --- | --- | --- |
    | height | **9.05** | 8.32 / 8.37 | 7.71 / 7.81 | 5.82 / 5.85 | 5.30 / 5.34 |

  - The apex is at 9.44–9.49, and the floor top at 0.386–0.419 (p5–p95).
  - The tallest dressing on the floor is 0.25 (strips and sprigs).
  - The lawn over the central 14 × 6, skipping bush footprints, is **13.60–14.00**, with a slope p95 of 22.9°.
- **Rock metrics** (`m040.rock_metrics`):
  - area CV 1.05 / 0.93 on the masses and 1.70 on the span;
  - 74 % of the masses' side faces within 20° of vertical (the shoulders and haunch round over);
  - the largest front facets are 1.6–2.2 wide by 3–6 tall.

## Stage 3: UV (modeller)

- Smart UV on every object (angle-based, 45°, margin 0.008), then `m012._uv_unfold` (0 faces cut).
- Result: 0 overlapping pairs and 0 flipped; minimum island gap 0.016; border 0.008; even density (1.0 / 1.0 / 1.0);
  conformal stretch p95 ≤ 1.02.
- The exporter writes its own palette UVs; this layer is clean.

## Stage 4: Materials, colour and texture (modeller)

**Calibration (`m046.calibrate()`: `K.calibrate` on the kit test dome against §5.4's targets):**

| Key | Hex | Dome render | Target |
| --- | --- | --- | --- |
| rock | `#A08B81` (19°, R − B 31) | (202,170,150) | `#C9AA9A` |
| rock_light | `#B6A498` (24°) | (231,201,178) | `#E6CBB7` |
| rock_deep | `#8E7A75` → **`#8F7A70`** | (179,148,136) | `#B39587` |
| floor | `#C39D75` | (246,189,130) | `#F6BC82` |
| floor_deep | `#A08470` | (199,156,124) | `#C69C7A` |
| grass | `#A3B20A` → **`#A3B300`** | (203,217,13) | `#CCD60A` |
| grass_light | `#AFBA0F` → **`#AFBA06`** | (219,227,16) | `#D9E30F` |
| grass_deep | `#8D9D04` → **`#8D9D00`** | (174,189,8) | `#ADBC09` |
| leaf | `#3A6815` | (66,120,22) | `#407616` |
| leaf_lit | `#6C9F32` | (130,192,51) | `#82C032` |
| leaf_deep | `#205D1F` | (36,106,31) | `#1F6A21` |
| flower | `#B5B21A` | (227,217,27) | `#E2DB1A` |
| pebble | `#AEAEA7` | (221,214,196) | `#DDD6C3` |
| trunk (soil) | `#381000` | (74,38,29) | `#4A2607` |

Three adjustments after calibration:
- **Mauve guard.** The calibrated rock_deep came out at hue 12°, R − B 25, so it was turned to hue 19° at the same
  value (`#8F7A70`, R − B 31). Every rock key is now R > G > B, hue 19–24°, R − B ≥ 30. The Rock Light and Rock Shadow
  swatches are never keys.
- **Grass.** In the scene the lawn rendered with B about 26 against the sheet's 9, so the blue channel of all three
  grass keys was taken to 0. The lawn now renders `#CEDD09` against `#CFD809`.
- **Leaves.** The dark bush tiers were shifted fresher, so the bush median lands in the sheet's 94° family instead of
  108°:
  - crown: leaf → lit at 80 %;
  - middle: leaf → lit at 20 %;
  - skirt: leaf → deep at 45 %.

**Blends** are by position or role, never by facing.
- **Rock:**
  - rock_light rises to 40 % over the upper 40 % of each column's own height, with a noise drift;
  - rock_deep adds 15 % patches below 1.5;
  - each column gets a Tint factor of 0.97–1.03, plus a facet mottle (amplitude 0.04, scale 0.3);
  - the span gets lighter toward its top (z 10.6 → 13); the soffit is plain stone with 10 % deep noise patches;
  - hidden caps are plain stone;
  - skirts and boulders are lighter at the crown and deeper at the foot.
- **Floor:**
  - sand tops with 10 % deep noise patches;
  - the 0.4 sides in floor_deep, a band set by its place in the tile;
  - hidden bottoms in plain sand;
  - a per-tile Tint of ±0.04 and a broad mottle.
- **Lawn:**
  - one noise field across every cap, so there is no colour step at the seams;
  - vertex noise values averaged per face, so the patches follow no triangle;
  - 10 / 20 % grass_light patches, and 10 / 25 % grass_deep within 0.8 of a bush root;
  - the aprons 30 % deeper where they tuck under the rock, the tunnel strips 25 % deep.
- **Bushes:**
  - two tones by role: crown fresh, skirt emerald;
  - a soil-dark heart underside;
  - sprigs in leaf_lit and a 30 % grass mix;
  - flowers and buds yellow; pebbles cream-grey.

**Kit check `baked_shading`:** hero 0.13, span 0.10, masses 0.19, sill 0.0 (limit 0.5). `K.check` reports no problems.

**Re-measure** of the final renders, using the study's masks.

*Shape and shares* (sheet values in brackets):

| View | W:H | R / P / L / F / G / D % |
| --- | --- | --- |
| f34 (−28, 18) | 1.254 (1.295) | **67.6 / 5.4 / 14.8 / 11.4 / 26.2 / 0.8** (64.5 / 6.6 / 15.2 / 13.3 / 28.5 / 0.4) |
| f34_see (−22, 18) | 1.301 | 66.8 / 5.6 / 14.5 / 11.6 / 26.1 / 1.5 |
| front (0, 8) | 1.489 (1.508) | 71.0 / 4.6 / 10.5 / 12.1 / 22.6 / 1.9 (68.1 / 4.7 / 14.8 / 12.1 / 26.9 / 0.3) |
| front_level (0, 4) | 1.533 | 74.4 / 3.7 / 8.8 / 11.9 / 20.7 / 1.2 |
| side (90, 8) | 0.762 (0.785) | 70.4 / 0.0 / 13.2 / 16.4 / 29.6 (74.7 / 1.2 / 11.8 / 11.9 / 23.7) |
| rear (180, 8) | 1.477 (1.450) | 72.8 / 3.6 / 10.1 / 10.9 / 21.0 (67.9 / 4.6 / 15.1 / 12.1 / 27.2) |
| r34 (145, 18) | 1.211 (1.262) | 69.4 / 1.0 / 13.6 / 12.2 / 25.8 (67.1 / 3.6 / 15.4 / 13.4 / 28.8) |
| top (0, 60) | 1.449 (1.356) | 38.8 / 8.8 / 35.1 / 16.4 / 51.5 (41.3 / 1.4 / 38.7 / 18.1 / 56.8) |

*Colour medians* (sheet values in brackets; the rock column is the lit half of the rock pixels):

| View | Rock lit half | Floor | Lawn | Bush |
| --- | --- | --- | --- | --- |
| f34 (−28, 18) | `#CCAC98` (`#C7A99A`) | `#F6BF86` (`#F6BA80`) | `#CEDD09` (`#CFD809`) | `#3F7822` (`#407616`) |
| f34_see (−22, 18) | `#CCAC97` | `#F5BF86` | `#CEDD0A` | `#3E7822` |
| front (0, 8) | `#CAAA96` (`#CCAC9B`) | `#C99D74` | `#CCDA0A` (`#C9D30A`) | `#3D7421` |
| front_level (0, 4) | `#CAAA96` | | `#CAD80A` | |
| side (90, 8) | `#A68F81` (in shade) | | `#A8B906` | |
| rear (180, 8) | `#AF968A` | | `#ADBE08` | |
| r34 (145, 18) | `#AE9689` | | `#AEC007` | |
| top (0, 60) | `#CDAD99` | `#F9C187` | `#CEDE06` | `#6B9128` |

- **Binding f34 shares (±4): all inside.** R 67.6 (+3.1), G 26.2 (−2.3), L 14.8, F 11.4, P 5.4.
- **Front-cell opening (binding).**

  | Camera | w / W | h / H | top | bottom |
  | --- | --- | --- | --- | --- |
  | sheet | 0.264 | 0.475 | 0.580 | 0.110 |
  | front (0, 8) | **0.260** | **0.408** | **0.580** | 0.173 |
  | front_level (0, 4) | **0.260** | **0.471** | **0.593** | 0.124 |

  - At (0, 8) the hole is centred at 0.496 and the jambs are vertical over its lower half: the row widths are 0.258,
    0.260 and 0.258 at 0.1, 0.3 and 0.5 of the hole's height. The h/H is 0.027 short of the ±0.04 tolerance, because at
    e 8 the far floor rises into the hole.
  - At (0, 4), the level end of the study's camera fit, every number is within tolerance.
  - In studs (ray-cast): 7.05–7.14 wide up to the 5.4 spring, the apex at 9.44–9.49, and 9.05 clear over the floor.
- Every rock median is R > G > B at hue 19–24° in every view, including the side, the rear and the tunnel: no mauve and
  no olive.

## Stage 5: Lighting (modeller)

Skipped (decision 11): the sheet shows no glow or light, so there are no emissive faces and no lights.

Studio checks needing manual validation (§7):
- the rock stays warm beige, not lilac, next to an M040 / M043 tile;
- the tunnel reads in shade but not black;
- the floor reads as warm sand, clearly apart from the rock;
- the column facets stay flat-shaded;
- a character walks through the tunnel (9.05 clear, 7.0 wide) without snagging, and reaches the lawn top (14.0) from a
  10.4 plateau with one jump;
- the lawn stays yellow-lime and the flowers yellow.

## Stage 6: VFX (modeller)

Skipped (decision 11): the sheet shows no effect. The hero has no sockets and no children, and `build()` treats any
socket as a problem.

Collision tags follow decision 12: the hero is `precise`, the span and both masses are `hull`, and the sill is `box`.

## Modeller's notes for the verifier

- **Renders** are in `art/blender/renders/models/M046/`:
  - `M046_views.png`, the contact sheet, and the default views;
  - the `*_sheet` views: f34 (−28, 18), front (0, 8), side, rear, r34 and top (0, 60), plus `f34_see_sheet` (−22, 18)
    and `front_level_sheet` (0, 4);
  - the part shots `part_span`, `part_massl`, `part_massr` and `part_sill`;
  - `span_underside` (e −30: the flat seats and the soffit);
  - `exploded`;
  - `scale`: 5.5-stud markers in the tunnel, on the apron and on the lawn;
  - `tunnel`: looking into the opening, with the marker;
  - `hole_cu`;
  - `junc_cu`: the span lifted 0.8 off the left mass's ledge;
  - `floor_cu`: the tile thickness.
- **`build()` returns** `audit`, `uv`, `materials`, `views`, `contact`, `capping` and `problems` (empty). It also
  returns `cover`, `opening`, `cracks`, `lawn`, `winding`, `shells`, `thin`, `rock_metrics`, `baked_shading`, `offsets`
  and `measure`.
- **Known misses and choices:**
  1. **The f34 camera is at (−28, 18), not (−35, 18).** It is within decision 9's probe set.
     - At −35 the W:H is 1.208 (under 1.22), and nothing shows through the tunnel.
     - The sheet's f34 shows paper through the hole at an angle that a 12-deep tunnel with a 7-wide mouth cannot give.
       `f34_see_sheet` (−22) shows the see-through.
  2. **Front hole h/H is 0.408 at e 8**, 0.027 outside the ±0.04 tolerance. At e 4 every opening number passes (see
     stage 4), and the 3D opening matches the spec: 7.0 wide, 9.05 clear, spring 5.4, apex 9.44.
  3. **Green fifths in the f34** are 8.8 / 5.6 / 1.0 / 42.6 / 42.0 against the sheet's 20.9 / 20.7 / 1.3 / 19.8 / 37.3.
     - The sheet carries far more foot greenery than the budget and the 13.8 depth limit allow.
     - The middle fifth is bare (1.0), as required.
     - The lawn's shoulder drapes and the rim bushes put more green in fifth 4.
  4. **Front and rear R is 71–73 % against 68 ± 4.** The front is just inside; the rear is 4.9 over. L is 10 % in both:
     the near-level views see little of the lawn top. G is within 5.
  5. **D is 1.9–3.8 % in the front, rear and r34** (sheet 0.3–0.5). The tile sides (floor_deep) fall in the dirt mask
     where they sit in the studio's shade. On the lit dome they render (199,156,124), the sheet's tile-side colour.
  6. **The tile top bevel was dropped,** since it would have made sub-5° slivers; the sides carry the darker band. There
     are no explicit notched sill ends: the tunnel tiles run 0.2 under each jamb foot, out of sight.
  7. **Rock seen from above is 84 + 6.7 studs²** against a target of ≤ 70. It is the battered faces, skirts and
     boulders; none of it is a flat top.
  8. **Hero at 3932 tris,** against a plan of about 3600. Leaves account for 1564 of them. MassL is at 966 of 1000.
  9. **Hero bbox is 25.62 × 14.14 × 16.00** against a target of 25.6 × 13.8 × 15.9. The foot bushes and leaves reach
     y ±7.2.
  10. **The f34 bush median is `#3F7822`** against the sheet's `#407616`: B is 12 higher, inside the 14 tolerance.
- **Not done here:** no commit, push or export. The work file `wip/M046.blend` is saved.

## Verification round 1 (verifier, 2026-10-29)

A fresh verifier, read-only, in a background Blender on port 9882 (`wip/M046_verify.blend`). Nothing was built, edited
or saved. Every number below comes from the verifier's own bmesh / BVH / ray-cast code and its own image masks, not from
`build()`'s reports. Renders and scripts are in the session scratchpad `m046_verify\`.

### Measured

**Mesh**

| Object | Tris (limit) | Size W × D × H | Shells | Open / non-manifold / boundary / wire / loose | Bowtie verts | Winding (dup / unpaired) | Zero-area / n-gons | Self-x in a shell | Neg-volume shells | Origin | Transforms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `StoneGate` | 3932 (4000) | 25.62 × 14.14 × 16.00 | 204 | 0 / 0 / 0 / 0 / 0 | 0 | 0 / 0 | 0 / 0 | 0 | 0 | bbox bottom centre (0, 0, 0) | applied |
| `StoneGateSpan` | 862 (1000) | 13.50 × 11.76 × 8.02 | 39 | 0 | 0 | 0 / 0 | 0 / 0 | 0 | 0 | bottom centre | applied |
| `StoneGateMassL` | 966 (1000) | 10.49 × 13.23 × 15.21 | 39 | 0 | 0 | 0 / 0 | 0 / 0 | 0 | 0 | bottom centre | applied |
| `StoneGateMassR` | 900 (1000) | 10.51 × 13.34 × 15.37 | 33 | 0 | 0 | 0 / 0 | 0 / 0 | 0 | 0 | bottom centre | applied |
| `StoneGateSill` | 184 (1000) | 11.48 × 13.55 × 0.50 | 15 | 0 | 0 | 0 / 0 | 0 / 0 | 0 | 0 | bottom centre | applied |

- Every shell is closed, consistently wound and of positive volume, so the normals point outward.
- **UV:** 0 overlapping pairs, 0 flipped, 0 zero-area, inside 0.008–0.992 on every object.
- **Rock footprint at the ground** (skirts and boulders included): x −12.61 … +12.74, y −6.46 … +6.64. Lawn top 14.01.

**Joints (ray-cast, rock + lawn + tiles only).**
- Points on the span/mass joint planes at x ±6.72 (z 8–13.6), the seat plane at z 7.98 (x ±2.3…±6.7) and the cap seams
  at x ±6.7: 128k samples, of which 110k are enclosed.
- Full lines were cast both ways through every enclosed point, along 18 directions: the 8 sheet cameras, −35 / −28 /
  −22 f34, grazing at e 0.3 from all four sides, straight down, (−45, 30), (−145, 18) and the underside at e −30.
- Result: **0 see-through**.
- Ground under the jamb feet (x ±3.3…±3.95): 0 of 2828 samples are visible from any camera.

**Floating dressing.**
- Hero: 204 shells, 48 on the ground, **0 floating**, 0 unchained. Every off-ground shell is ≤ 0.01 from a neighbour, or
  intersects one.
- Parts: span 0 / 0, MassL 0 / 0, MassR 0 / 0, sill 0 / 0.

**Capping.**
- Seen from straight above inside the footprint, in studs²: lawn 149.2, leaves 51.8, rock 96.0 (89.3 at z ≤ 12 and 6.7
  above it, all sloped faces), tiles 23.3.
- **Flat rock above z 12: 0.** Flat rock anywhere: 4.0 studs², all of it the hidden seat ledge at z 8.0.
  - These are slivers where a mass column stands proud of the span's foot: (±2.9, ∓4.4), (±5.6, ∓5.3), (±5.9, ±4.1).
  - 2.5–3.1 studs² of them are visible from each sheet camera.

**Opening (rock only, then everything).**

| Measure | Value |
| --- | --- |
| Clear width | 7.03 / 7.05 / 7.09 / 7.11 / 7.07 / 7.02 / 7.02 at z 0.6 / 1 / 2 / 3 / 4 / 5 / 5.4; 6.64 at z 5.9 (head height over the floor); 5.71 at 7.0; 4.54 at 8.0 |
| Rock apex | 9.43 |
| Clear height over the floor | **9.04** at x 0; 8.31 / 8.38 at ±1; 7.70 / 7.82 at ±2 |
| Floor top | p5 0.386, median 0.395 |
| Dressing in the tunnel | at most 0.33 above the floor (the strips and sprigs) |
| Walk test | a 2 × 1 × 5.5 character box sweeps through at x −2, −1, 0, +1 and +2 without touching anything |
| Lawn over the central 14 × 6 | 13.57–14.01, slope p95 22.7° |

**Dressing cut into rock (per-shell ray parity against each rock shell).**
- **Hero: 33 dressing shells more than 0.05 inside rock**: 28 more than 0.10 and 24 more than 0.20.
- **The worst is 0.81 deep, and several leaves lie entirely inside a mass core**: 7 of 7 verts in, at (8.11, −5.47,
  0.95), (−8.62, 5.89, 0.88) and (7.81, −5.39, 0.42).
- Axis rays confirm it. The leaf at (−8.31, 4.97, 0.42) has rock out to y 6.52, and the one at (8.11, −5.47) has rock
  out to y −5.83.
- All of these are hero-only foot bushes: J1, F2, F3, F4, F6 and F7.
- Parts: span, MassL and MassR all have 0.

**Shape and shares** (the verifier's own masks; sheet values in brackets):

| View | W:H | R / P / L / F / G / D % | Green fifths, bottom → top | Top profile |
| --- | --- | --- | --- | --- |
| f34 (−28, 18) | 1.253 (1.295) | 67.6 / 5.4 / 14.1 / 12.0 / 26.1 / 0.8 (64.5 / 6.6 / 15.2 / 13.3 / 28.5 / 0.4) | 8.6 / 5.5 / 0.9 / 41.8 / 43.2 (20.9 / 20.7 / 1.3 / 19.8 / 37.3) | f .05–.15 at .57 / .75 / .87 (.35 / .54 / .74); max dev 0.22, mean 0.06 |
| f34 (−35, 18) | 1.199 | 68.1 / 5.0 / 14.8 / 11.9 / 26.7 / 0.2 | 7.7 / 6.2 / 1.5 / 43.0 / 41.7 | similar |
| front (0, 8) | 1.488 (1.492) | 70.8 / 4.7 / 10.0 / 12.4 / 22.4 / 2.0 (67.7 / 4.8 / 15.0 / 12.2 / 27.2 / 0.3) | 11.4 / 4.4 / 1.3 / 21.1 / 61.8 (30.3 / 6.2 / 0.4 / 25.8 / 37.3) | f .05–.15 at .43 / .85 / .90 (.28 / .68 / .80); width at h .85 / .95 is .79 / .55 (.65 / .24) |
| front (0, 4) | 1.531 | 74.2 / 3.8 / 8.7 / 12.0 / 20.7 / 1.3 | | |
| side (90, 8) | 0.764 (0.785) | 70.5 / 0 / 14.0 / 15.5 / 29.5 (74.4 / 1.2 / 11.9 / 12.0 / 23.9) | | bottom-row width .98 (.77) |
| rear (180, 8) | 1.474 (1.450) | 72.4 / 3.8 / 10.1 / 10.9 / 21.0 (67.5 / 4.7 / 15.3 / 12.2 / 27.5) | | |
| r34 (145, 18) | 1.212 (1.262) | 69.1 / 1.2 / 13.4 / 12.4 / 25.8 (66.8 / 3.6 / 15.5 / 13.5 / 29.0) | | |
| top (0, 60) | 1.454 (1.356) | 38.8 / 8.9 / 34.2 / 17.2 / 51.4 (40.9 / 1.5 / 38.9 / 18.2 / 57.1) | | |

**Front-cell opening (binding).**

| Camera | w / W | h / H | top | bottom | centre |
| --- | --- | --- | --- | --- | --- |
| sheet | 0.264 | 0.470 | 0.574 | 0.109 | 0.48 |
| (0, 8) | 0.262 | **0.414** | 0.581 | 0.169 | 0.496 |
| (0, 4) | 0.262 | 0.476 | 0.594 | 0.120 | 0.496 |

**f34 see-through:** 0.04 × 0.13 at (−28, 18), top at 0.47; none at −35. The sheet shows 0.151 × 0.317.

**Colour.**
- **Rock keys:** all 7 are R > G > B at hue 19–21° and R − B 30–31. Base `#A08B81`. None is mauve or olive.
- **Rendered rock (lit half):** f34 `#CDAC98` against the sheet's `#CDADA0` (hue 22.6°, sat 0.26), front `#CAAA96`
  against `#CEAE9F`.
- **Other rendered colours:**

  | Material | Ours (f34) | Sheet |
  | --- | --- | --- |
  | Floor | `#F7BF86` | `#F6BA80` |
  | Lawn | `#CEDD15` | `#D0D809` |
  | Foliage | `#3B7622` | `#407616` |
  | Yellow | `#EBE01F` | `#E0DB1B` |

- **Facing correlation** (area-weighted, painted lightness against the normal):

  | Object | Rock n.z | Lawn | Floor | Leaves | Other axes |
  | --- | --- | --- | --- | --- | --- |
  | Hero | 0.14 | 0.01 | −0.01 | 0.11 | |
  | Span | 0.21 | | | | |
  | Masses | 0.12–0.13 | | | | |
  | All | | | | | n.x / n.y ≤ 0.12 |

- `K.check` reports no problems.
- **Builder:**
  - every paint choice uses position or role: column height, the noise field, the bush tier, the heart below its centre
    and the tile side by vertex z;
  - `normal` appears only in the geometry (leaf orientation, outlines) and in `capping_report`.
  - No paint is chosen by facing (unlike 044).
- **Tint:** per corner, 0.93–1.09, sd 0.025, per facet. No confetti on the renders.
- **Finish:** rock / floor 0.9, lawn and leaves 0.85, flower 0.8, metal 0. No emission, no sockets, no children.

### Findings

1. **Blocker: dressing buried in rock (decision 7, "Dressing cuts at most 0.05 into rock"; spec pitfall 13).**
   - 33 hero dressing shells cut more than 0.05 into rock: 24 more than 0.2, the worst 0.81, several entirely inside a
     mass core. They are the hero-only foot bushes J1, F2, F3, F4, F6 and F7.
   - Stage 1 states the opposite ("guarded out of the rock (≤ 0.05 in)"). The guard either doesn't see the core and skirt
     at these positions, or its push is undone by `_keep_up` or the `zmin` shift.
   - The buried leaves are also hidden faces: about 240 wasted tris in a 3932 / 4000 hero.
   - **Fix target:**
     - move each foot-bush centre outside the rock footprint by at least 0.7 R (onto the apron);
     - re-check every leaf after its final placement with a ray-parity test against the full hero rock;
     - report 0 shells more than 0.05 inside rock.
   - Spend the freed tris on visible foot greenery (finding 2).
2. **Minor: foot greenery much too sparse (§2.6 green fifths, ±7).**
   - The f34 bottom two fifths are 8.6 / 5.5 % green against 20.9 / 20.7; fifth 4 is +22.
   - The front's bottom fifth is 11.4 against 30.3.
   - The sheet's foot is a lush lime apron with many small bushes, sprigs and flowers; ours reads as bare rock to the
     ground.
   - **Target:**
     - widen the apron to 1.2–2.0 on the front and back faces;
     - add 4–6 small foot bushes and 4 sprigs (paid for by finding 1 and the leaf trims in finding 4);
     - f34 fifths 1–2 at ≥ 14 % each.
3. **Minor: the outline is boxier than the sheet's dome.**
   - The f34 top profile rises too fast at the left end: at f .05–.15 it is .57 / .75 / .87 against .35 / .54 / .74
     (max deviation 0.22, mean 0.06; the target is ±0.08 and mean ≤ 0.05).
   - The front is +0.15 at f .05–.10. Its top is too broad: width .79 / .55 at h .85 / .95 against .65 / .24.
   - The shoulder bushes L1, L2, R1 and R2 sit high on the rim edge, and pad bushes P1 / P2 stand on tall pointed end
     skirts (they read as potted plants on spikes in the front and rear).
   - **Target:**
     - move the shoulder bushes 0.8–1.5 down the drape, as §2.4 placed them (−10.0, −1.5) and (+10.0, +1.2);
     - lower or drop the pads on the end skirts;
     - get the front width at h .85 to ≤ .72 and the f34 top profile within ±0.08.
4. **Minor: the bushes are large flat-leaf "cabbage" domes, not the sheet's dense rounded clumps (decision 10).**
   - Each has 7 big pentagonal leaves with pointed tips. Some skirt leaves hang as edge-on flaps, and 18 % of the leaf
     area is within 12° of edge-on at the f34 (target ≤ 12 %).
   - Dark heart wedges show under several rim bushes.
   - **Target:**
     - 9–11 smaller rounded leaves (0.6–0.7 R) in 3 tiers;
     - no drooping edge-on skirt leaves;
     - the heart hidden from the f34 and front;
     - edge-on ≤ 12 %.
5. **Minor: the span's four lumps don't read.**
   - The front face above the hole reads as more columns. The sheet's span is 4 big bulging, rounded boulders (f34,
     exploded, underside), and our `part_span` reads as a box with a lawn.
   - The bulges are only 0.2–0.65.
   - **Target:**
     - lump bulge 0.8–1.2, with creases 0.6–0.8 between lumps;
     - rounded upper shoulders on each lump under the lip;
     - keep the apex V.
   - The pillar rock likewise reads as many narrow facets rather than "broad flat faces, chunky": merge the strip
     triangles into fewer, broader planes where the budget allows.
6. **Minor: the lawn reads as a thick overhanging slab in the side and top views.**
   - In the side view especially, the lip (0.38–0.62 drop plus the overhang) reads as a separate green cap.
   - **Target:** a lip drop of 0.25–0.35, the overhang ≤ 0.2, and the column tops rounding up to meet the lawn edge.
7. **Minor (accept and record): the front hole h/H is 0.414 at (0, 8)**, against 0.47 ± 0.04.
   - At (0, 4) all four numbers pass: 0.262 / 0.476 / 0.594 / 0.120. The sheet's hole bottom (0.109) matches e 4 (0.120),
     not e 8 (0.169), so the sheet's front camera is nearer e 4.
   - In 3D the opening is exact: 7.02–7.11 wide to the 5.4 spring, apex 9.43, 9.04 clear.
   - The main session should rule e 4 the front camera.
8. **Minor (accept): the f34 camera is at (−28, 18).**
   - It is in decision 9's probe set. At −35 the W:H is 1.199, under 1.22.
   - The binding f34 shares pass at both: R +3.1 / +3.6, G −2.4 / −1.8, P −1.2 / −1.6.
   - The sheet's big f34 see-through (0.15 × 0.32) can't be had through a 12-deep tunnel at this angle. That is a sheet
     perspective conflict, not a model fault.
9. **Minor: the hidden seat ledge shows** as flat slivers at z 8.0: 2.5–3.1 studs² visible from each sheet camera, at
   the haunch tips and in front of / behind the span feet. Close them with the span's lower front / back edge (or the
   lump overhang of §2.2), so the joint reads as a crease.
10. **Minor:**
    - Front and rear R are 70.8 / 72.4 against 67.7 / 67.5, and L is 10 against 15, at near-level cameras. Finding 6
      (a thinner lip that shows more lawn top) and finding 2 help.
    - Rock seen from above is 96 studs² against the study's ≤ 70. The top cell's R matches (38.8 against 40.9), so
      accept.
11. **Minor:**
    - **Sill:**
      - there is no tile bevel and no notched ends (recommendation 4 lists "notched sill ends"); this is invisible in
        the hero;
      - `kit_notes` still says "(bevelled tops)";
      - **target:** fix the note, and optionally add the two-step notch to the part's ends.
    - **Depth:**
      - the hero is 14.14 deep (inside 13.8 ± 0.7);
      - the side view's bottom row is .98 wide against .77, from foot bushes past the footprint;
      - the boulders reach x ±12.7 and y ±6.6 against the planned ±12.1 / ±6.0.
12. **Passes:**
    - the mesh on all five objects;
    - the budget;
    - no cracks;
    - no floating dressing;
    - capping (0 flat rock above z 12);
    - the opening and the walk test;
    - colour family and calibration;
    - no colour by facing;
    - no lighting or VFX;
    - collision tags, names and keys.
    - Decisions 1–6 and 8–14 are followed. Decision 4's notched sill ends are only partly done (finding 11), and decision
      9's camera choices are covered by findings 7 and 8.

### Score and verdict

**6.5 / 10. FAIL (round 1)**, on one blocker: finding 1, buried foot-bush dressing, a missed decision 7 and hidden faces.

- **Round 2:** fix finding 1, and use its freed budget for finding 2. Findings 3–5 are the main visual gaps against the
  sheet and are worth taking in the same round.
- **Sound as it stands:** the arch itself (opening, joints, capping, mesh, colour).

## Main session ruling after round 1 (2026-10-29)
- **Front camera:** `front_sheet` is now (0, 4). The sheet's hole bottom matches e 4, and every binding opening number passes there.
- **f34 camera:** (−28, 18) is accepted from the probe set.
- **Rock seen from above:** 96 studs² is accepted, because the top cell's rock share matches.
- **Fix round 1 scope:**
  - blocker 1, dressing buried in rock: 0 shells more than 0.05 into rock, re-checked after final placement;
  - the minors, using the tris freed by blocker 1:
    - 2, foot greenery;
    - 3, outline toward the dome;
    - 4, rounded clump bushes;
    - 5, span lumps;
    - 6, a thinner lawn lip;
    - 9, seat-ledge slivers;
    - 11, a `kit_notes` correction.

## Fix round 1 (fix modeller, 2026-10-29)

A fresh fix modeller in a background Blender (port 9882, `wip/M046.blend`). It edited only `m046.py`; no shared
helpers changed. The final check ran in a freshly restarted session: `build()` with parts, checks and renders gave
**problems: []**. The work file is saved. Nothing was committed, pushed or exported.

### Changes

1. **Blocker, dressing buried in rock.**
   - **Cause.** `m040._Guard` judges "inside" by the nearest face's normal. Where a skirt or boulder is sunk into a
     core, the nearest surface is the skirt's outside, so a leaf deep in the core read as "outside".
   - **New checks** in `m046.py`:
     - `_parity_in` / `_Rocks`: each closed rock shell (span, both cores, 8 skirts, 8 boulders: 19) is tested on its
       own, by ray parity in three skewed directions with a majority vote;
     - depth is the distance to that shell's surface.
   - **Placement.**
     - `_foot_spot` moves every hero foot plant's centre out from the rock until the rock is at least **0.7 R** away
       horizontally at 0.15 / 0.45 H / 0.85 H. Sprigs, pebbles and flowers use the same rule with a smaller clearance.
     - Pad bushes move off their core by at most 0.45 (so they stay on the pad).
     - Every leaf is placed first (slid onto the heart, `_keep_up`, the z-min shift), and only then tested against the
       full rock by parity. A leaf more than 0.05 in climbs the dome 10° at a time, and is dropped if it still cuts in.
     - A heart that cuts in is narrowed (×0.82, up to 5 times).
   - **Report.** `bury_report(o)` runs per object in `checks()`. Any dressing shell more than 0.05 inside rock is now
     a `build()` problem.
   - **Guard removed.** The old `_Guard` is no longer used for plants.
2. **Foot greenery.**
   - **Apron:** 1.2–1.5 wide from the base path (was 0.7–1.25). See "Left over" for why not 2.0.
   - **Foot plants** (hero-only):
     - **Bushes:** J1 (dark, about 1.5 across) plus 8 small bushes F1–F5 and F8–F10. They sit on the front and back
       faces, not past the ends, so they don't widen the front silhouette.
     - **Pad bushes:** P1, P2 and P3 on turfed corner and front skirts (the sheet's f34 ledge pads); P2 and P3 are new.
     - **Sprigs:** 7, of which SP3, SP4, SP7, SP8 and SP9 are new or moved to the ends.
   - **Reach limit.** A foot bush shrinks (to 0.62 R at least) to keep its leaves inside |x| 13.0 and |y| 7.4
     (`FOOT_REACH`).
3. **Outline toward the dome.**
   - **Shoulder bushes:**
     - L1 / R2 moved down the drape to x ±9.3 (on the cap's outer ridge points; the cap ends at x ±9.0–10.1), and made
       smaller (about 2.1 across, 1.55 tall);
     - L2 / R1 pulled in to x −7.0 / +7.3 and lowered (1.7 tall).
   - **Rim bushes:** the two centre bushes S2 / S3 are the tallest (2.16). S1 / S4 are lower (about 1.7).
   - **End skirts:** SK_L3 and SK_R2 are lower (5.0 / 4.8 → 3.5 / 3.4), pitched, with no pad and no pad bush. The
     corner skirt SK_R1 (4.4) and the front skirt SK_L1 (4.8) now carry the turfed pads instead.
4. **Bushes as dense rounded clumps** (`bush()`, `TIERS`, a new 8-tri leaf `_cleaf` with a flat underside fanned from
   the stem).
   - **Leaves:** 9–10 per rim bush, 6 per small bush, 0.62–0.74 R long.
     - A crown of 3–4 flat leaves fans out from the dome's top, half sunk in the heart.
     - A ring of 6 upright side leaves stands round the heart, tips curled in over it.
     - There are no hanging flaps.
   - **Why these two orientations.** At e 18, a leaf is within 12° of edge-on whenever its tilt is between about 6°
     and 60°. A uniform dome of leaves gives about 21 % edge-on, and the round-1 bushes measured 17.2 % with this
     metric (the verifier measured 18 %). Only near-flat and near-upright leaves stay clear.
   - **Hearts:** coloured as foliage by height (fresh above, emerald below), never the soil colour. Small bushes use a
     6-tri bipyramid heart.
   - **Size:** the clump's real width is about 1.5 R, so R was raised. Rim bushes are now 2.0–3.0 across.
5. **Span lumps.**
   - **Rings:** `SPAN_X` gains rings at ±4.15 and ±5.9, so the outer lumps have rounded flanks, not a tent.
   - **Bulges:** the peak bump is 0.80–0.88 × GZ 1.25, about **1.0–1.1 proud** at z 10. The creases are −0.50 to
     −0.55 × 1.25, about **0.63–0.69 in**. GZ is a little fuller at the top and bottom.
   - **Pillars:** each column face is now **two broad facets meeting at a mid ridge** (the third "face" strip is gone;
     spec 2.3). Cores went from 338 / 340 to 252 / 256 tris, and the front facets are 1.8–2.9 wide by 3–6 tall.
6. **Lawn lip** (`cap_outline`, `_seam`).
   - **Drop:** 0.25–0.35 below the rim (was 0.38–0.62).
   - **Overhang:** 0.15–0.19 (was 0.18–0.28).
   - **Miter offsets.** The offsets are now miters, so the outline's edges stay parallel to the rim's. This keeps every
     rim point inside on the sharper two-facet scallops: proud_min is 0.093 or more.
   - **Support points.** Two or three lawn support points at x ±7.0–7.1 keep the walkable lawn at 13.6 or more.
7. **Seat-ledge slivers.**
   - The span's bottom edge on each ring at |x| ≥ 2.3 now reaches past the ledge's outer edge (`_ledge_edge`,
     `_ledge_need`, +0.07). It covers the worst ledge point over the neighbouring ring interval.
8. **kit_notes.** `StoneGateSill` now reads "square-edged slabs, darker sand sides"; the module docstring was fixed too.

**Also changed:**
- **Front camera.** `front_sheet` is now (0, 4), per the ruling. The old (0, 8) view is kept as the extra
  `front_e8_sheet`; `front_level_sheet` is gone from the builder.
  - The file `front_level_sheet.png` in this folder is a **stale round-1 render**. It is no longer written; ignore it.
- **`edge_on_report`** is new in `checks()`. It reports area-weighted leaf faces within 12° of edge-on per camera, both
  all leaves and visible ones only.
- **`TARGET_SIZE` depth** went from 13.8 ± 0.7 to 15.0 ± 0.6 (see "Left over").

### Before → after (round-1 verifier numbers → fix round, fresh-session `build()` and own masks)

| Item | Target | Round 1 | Fix round 1 |
| --- | --- | --- | --- |
| Dressing shells > 0.05 in rock (hero, ray parity) | 0 | 33 (max 0.81) | **0** (max 0.041; parts 0 / 0.026 / 0) |
| Floating / unchained shells | 0 | 0 / 0 | **0 / 0** on all five objects |
| Winding errors / unpaired edges | 0 | 0 / 0 | **0 / 0** on all five |
| Non-manifold, bowtie, boundary, n-gons, zero-area, sub-5° corners, inverted shells | 0 | 0 | **0** |
| Hero tris (limit 4000) | < 4000 | 3932 | **3960** (rock 1312, lawn 716, tiles 160, leaves 1692, pebbles 80) |
| Parts tris (limit 1000) | < 1000 | 862 / 966 / 900 / 184 | **986 / 872 / 808 / 184** (span / L / R / sill) |
| Hero bbox W × D × H | | 25.62 × 14.14 × 16.00 | **26.12 × 15.21 × 16.10** |
| Joint leaks / see-through | 0 | 0 | **0 / 0** (936 rays) |
| Flat rock top above z 12 / anywhere | 0 | 0 / 4.0 | **0 / 0.0** |
| Seat ledge visible from each sheet camera (studs²) | 0 | 2.5–3.1 | **0.0** from all 6 |
| Lip drop / overhang | 0.25–0.35 / ≤ 0.2 | 0.38–0.62 / 0.18–0.28 | **0.25–0.35 / 0.15–0.19** |
| Span lump bulge / crease | 0.8–1.2 / 0.6–0.8 | 0.2–0.65 | **1.0–1.1 / 0.63–0.69** (design values) |
| Leaf edge-on at f34 (all leaves / visible) | ≤ 12 % | 18 % (17.2 own metric) | **11.5 / 11.5 %** |
| Opening width to 5.4 / clear over floor / apex | 7.0 / 9.0 / 9.4 | 7.02 / 9.04 / 9.43 | **7.05–7.14 / 9.02 / 9.43–9.52** |
| Lawn over the central 14 × 6 | ≥ 13.6, ≤ 25° | 13.57, p95 22.7° | **13.68, p95 19.3°** |
| f34 (−28, 18) W:H | 1.22–1.37 | 1.253 | **1.306** |
| f34 shares R / P / L / F / G / D | 64.5 / 6.6 / 15.2 / 13.3 / 28.5 / 0.4 (±4) | 67.6 / 5.4 / 14.1 / 12.0 / 26.1 / 0.8 | **68.4 / 5.3 / 16.1 / 9.6 / 25.7 / 0.7** |
| f34 green fifths, bottom → top | 1–2 ≥ 14 each; middle ≤ 4 | 8.6 / 5.5 / 0.9 / 41.8 / 43.2 | **11.4 / 6.7 / 1.5 / 39.1 / 41.3** |
| f34 top profile at f .05 / .10 / .15 | .35 / .54 / .74 | .57 / .75 / .87 | **.37 / .72 / .80** (whole profile: mean 0.051, max 0.18) |
| Front (0, 4) hole w / h / top / bottom | .264 / .475 / .58 / .11 (±.03 / ±.04 / ±.04) | .262 / .476 / .594 / .120 | **.255 / .471 / .590 / .122** |
| Front (0, 4) width at h .85 / .95 | .65 / .24 | .79 / .55 (at e 8) | **.58 / .64** (at e 8: .60 / .56) |
| Front (0, 4) bottom green fifth | toward 30 | 11.4 (e 8) | **16.1** (e 8: 15.6) |
| Front (0, 4) W:H / R / G | 1.508 ± .08 / 68 ± 4 / 27 ± 4 | 1.531 / 74.2 / 20.7 | **1.559 / 75.5 / 19.6** |
| Side (90, 8) W:H | 0.72–0.85 | 0.764 | **0.861** |
| Top (0, 60) R / L / F | 41 / 39 / 18 (±5 / ±5 / ±4) | 38.8 / 34.2 / 17.2 | **37.9 / 38.4 / 14.5** |
| Rock colour | R > G > B | keys hue 19–21° | **unchanged keys**; rendered lit rock f34 `#CCAC97`, front `#C9A995`, side `#AA9285` (all R > G > B) |
| `K.check` / baked shading (limit 0.5) | no problems / < 0.5 | none / 0.10–0.19 | **none / hero 0.01, span 0.27, masses 0.0, sill 0.0** |
| UV | no overlaps or flips | 0 / 0 | **0 / 0**, gap 0.016, p95 stretch ≤ 1.032 |

### Left over (for the verifier and the main session)

1. **f34 green fifths 1–2 are 11.4 / 6.7, against ≥ 14 each** (round 1: 8.6 / 5.5).
   - **What limits them:**
     - the 4000 budget, which leaves about 40 tris spare;
     - the depth: the foot bushes, kept 0.7 R clear of boulders that already stand at y ±6.7, reach y ±7.4;
     - the pad-bush "potted plant" read. A fourth pad bush on the left end skirt was tried and dropped, because the
       front view showed a row of potted plants.
   - **Shares.** F is 9.6 against 13.3 ± 3, 0.7 short. G (25.7) and R (68.4) are inside ±4. The smaller, denser clumps
     that round 1 asked for cost foliage area against the round-1 "cabbages".
2. **The outline at h .95 is still wide** (front .64 against .24).
   - Decision 8's walkable lawn (13.6 or more over the central 14 × 6) holds the lawn flat at 13.7–14.0 to x ±7.
   - Every rim bush therefore sits within 0.4 of the centre ones, and at about 1.6 tall (the sheet's 1.6–2.0) their
     tops all clear h .95.
   - The sheet's rounder lawn dome would mean lowering the walkable top.
   - The improvements are h .85 (.79 → .58) and the f34 profile at f .05 / .15.
   - The f34 profile at f .10 (.72 against .54) is the left end's column tops. The rock dome there matches the study's
     front-cell outline numbers (§1.2), so it was left alone.
3. **Depth 15.21** (13.8 ± 0.7 in the study; `TARGET_SIZE` was moved to 15.0 ± 0.6).
   - The rock alone is 13.4 deep. The extra is the foot bushes in front of the boulders and skirts (fix target 2 with
     the 0.7 R clearance).
   - **The apron stops at 1.5** (not 2.0) on the front and back for the same reason: 2.0 would add another 1.0 of
     depth and width.
   - The side W:H is 0.861 against 0.785 ± 0.08 (0.865 at most).
4. **Front and rear at near-level cameras** read R 74–76 and G about 20 (round 1 the same: 74.2 / 20.7).
   - At e 4 the lawn top is barely seen (L 8.5). The thinner lip that round 1 asked for shows less lime from the front.
5. **Front-view leaf edge-on is about 45 %.** At e 4 the flat crown leaves are edge-on by geometry. The binding target
   is the f34 (11.5 %).

- **Main session (2026-10-29):** TARGET_SIZE depth 15.0 ± 0.6 is accepted, so the foot bushes stay clear of the boulders.

## Verification round 2 (verifier, 2026-10-29)

A fresh verifier, read-only, in a background Blender on port 9882 (`wip/M046_verify.blend`, the fixed and integrated
model). Nothing was built, edited or saved. Every number below comes from the verifier's own bmesh / BVH / ray-parity
code and its own HSV masks (the study's class definitions, re-implemented). Only the shell-kind labels (`m046._kind`)
and the UV overlap count (`M.uv_stats`) were borrowed. Renders and scripts are in the session scratchpad
`m046_verify2\`. The sheet's own cells were re-measured with the same masks: the f34 came out at R 65.3 / P 6.5 / L 14.8
/ F 13.0, with green fifths 20.9 / 20.7 / 1.3 / 19.8 / 37.3, which confirms the study's numbers.

### Measured

**Mesh**

| Object | Tris (limit) | Size W × D × H | Shells | Non-manifold / boundary / wire / loose | Bowties | Winding (dup / unpaired) | Zero-area / n-gons / dup verts | Self-x in a shell | Neg-volume shells | Origin | Transforms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `StoneGate` | 3960 (4000) | 26.12 × 15.21 × 16.10 | 259 | 0 / 0 / 0 / 0 | 0 | 0 / 0 | 0 / 0 / 0 | 0 | 0 | bbox bottom centre (0, 0, 0) | applied |
| `StoneGateSpan` | 986 (1000) | 13.54 × 12.23 × 8.12 | 47 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | bottom centre | applied |
| `StoneGateMassL` | 872 (1000) | 10.49 × 13.56 × 15.40 | 48 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | bottom centre | applied |
| `StoneGateMassR` | 808 (1000) | 10.51 × 13.34 × 15.30 | 40 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | bottom centre | applied |
| `StoneGateSill` | 184 (1000) | 11.48 × 13.55 × 0.50 | 15 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | bottom centre | applied |

- **Normals.** Every shell is closed and consistently wound, with positive volume (the smallest is 0.0008), so the
  normals point outward.
- **Hero by kind:** rock 19 shells / 1312 tris; lawn 10 / 716; tiles 12 / 160; leaves and petals 208 / 1692; pebbles
  10 / 80.
- **UV:** 0 flipped, 0 zero-area, all inside 0.008–0.992; 0 overlapping pairs; minimum gap 0.016, on every object.
- **Sizes against the targets:** W 26.12 (25.6 ± 0.8), D 15.21 (15.0 ± 0.6, the ruled target) and H 16.10 (15.9 ±
  0.6) are all inside.
  - The mass cores are 24.4 × 12.4 (x ±12.19, y ±6.2), against 24 × 12.
  - The skirts and boulders reach x ±12.75 and y −6.79 … +6.64, against the planned ±12.1 / ±6.0.
  - The lawn top is 14.007.

**Dressing buried in rock (the round-1 blocker).** Each dressing shell was ray-tested against each of the 19 rock
shells on its own. The test runs on every vertex and face centre of the shell, with a majority vote over three skewed
directions. The depth is the distance to that rock shell's surface.

| Object | Dressing shells | > 0.03 | **> 0.05** | > 0.10 | Max |
| --- | --- | --- | --- | --- | --- |
| Hero | 218 (leaves, petals, pebbles) | 2 | **0** | 0 | **0.041** |
| Span / MassL / MassR / Sill | 45 / 36 / 29 / 3 | 0 | **0** | 0 | 0.0 / 0.026 / 0.0 / 0.0 |

- For information, the lawn and tiles sink into rock by design:
  - the caps' lip feet are 0.10–0.28 into the rim;
  - the aprons are tucked under the foot;
  - the tunnel tiles run 0.2 under each jamb foot;
  - one front-left ledge pad is up to 0.35 inside its skirt, at about (−7.9, −5.6, 4.8).

**Floating dressing (own contact graph).** Shells are in contact when they intersect (BVH overlap) or lie within 0.03
(vertex to surface, both ways). A shell chains when contact leads from it to the ground.

| Object | Shells | On ground | Floating | Unchained | Worst off-ground gap |
| --- | --- | --- | --- | --- | --- |
| Hero | 259 | 56 | **0** | **0** | 0.003 |
| Span / MassL / MassR / Sill | 47 / 48 / 40 / 15 | — | 0 | 0 | 0.0 |

**Joints and cracks (rock + lawn + tiles only, no dressing).**
- **Samples.** 14,784 sample points sit just off the joint planes: x ±6.69 / ±6.75 for z 7.8–14, y ±6.5, and z 7.95 /
  8.01 on the seat. 10,959 of them are enclosed.
- **Line test.** Full lines were cast from both sides through every enclosed point, with 3 jitters, in 19 directions:
  - the 8 sheet cameras;
  - −35 and −22 f34;
  - (−90, 8);
  - grazing at e 0.3 from all four sides;
  - straight down;
  - the underside at e −30;
  - (−45, 30), (−145, 18) and (35, 18).
- **Line-test result.** It flagged 2 points, and both were false alarms:
  - (−6.75, 5.11, 8.21) lies 0.005 from the rock surface with rock above it;
  - (−6.75, −1.89, 13.81) lies just above the lawn top (13.806).
  - Both were parity ties on a surface, not gaps.
- **Isolated-miss test.** A miss with at least 7 of 8 neighbours at 0.2 hitting was flagged in 5 places. A 0.025-grid
  scan of each showed it was the open edge of the opening or the silhouette, not a crack.
- **Result: 0 see-through cracks.**
- **Jamb feet.** 1876 ground points under the jamb feet (x ±3.30 … ±3.95) were tested. **0** are visible from any
  camera.

**Capping (straight down, 0.1 grid over x ±12.4, y ±6.2).**
- **Area seen from above (studs²):** lawn 161.0, rock 96.0, leaves 37.3, tiles 10.6, pebbles 0.3.
- **Flat rock (n.z > 0.85):** **0.0 above z 12**, and 0.0 anywhere.
- **Other rock above z 12:** 9.7 studs², all sloped faces under the lip. None above z 13.
- **The lawn caps every rock top.** A downward scan along both cap seams (x ±6.55 … ±6.85) finds rock only at |y| ≥ 4.4,
  on the sloped faces under the lip edge.
- **The seat ledge.** It is 18 flat faces (98.4 studs²) at z 8.0, and **0.00 studs² of it is visible** from the f34, f34
  (−22), front, side, rear, r34 and top cameras. The round-1 slivers are gone.

**Opening and walk (ray-cast along Y through the full depth).**

| Measure | Value |
| --- | --- |
| Clear width, rock | 7.02 / 7.04 / 7.08 / 7.09 / 7.05 / 7.00 / **6.98** at z 0.5 / 1 / 2 / 3 / 4 / 5 / 5.4; 6.62 at 5.9; 5.68 at 7.0; 4.52 at 8.0 |
| Clear width, everything | the same from z 1.0 up; 6.09 at 0.5 (the 0.08 tunnel strips and sprigs at the wall feet) |
| Rock apex / clear over the floor | apex 9.43–9.52; **9.02** at x 0; 8.37 / 8.43 at ±1; 7.75 at ±2; 5.76 / 5.81 at ±3.2; 5.20 / 5.26 at ±3.4 |
| Floor top | p5 0.386, median 0.393, p95 0.419 |
| Tallest dressing in the tunnel | 0.34 over the floor |
| Walk box 2 × 1 × 5.5 | clear against rock at x −2 … +2. Against everything, clear at −1 … +1, and at ±2 above 0.6, where it only touches the wall-foot strips |
| Lawn over the central 14 × 6 | 13.66–14.00 |

**Shape and shares (own masks).** Sheet values are in brackets; the f34 sheet values are the verifier's own
re-measure.

| View | W:H | R / P / L / F / G / D % | Green fifths, bottom → top | Top profile against §1.2 |
| --- | --- | --- | --- | --- |
| **f34 (−28, 18)** | 1.306 (1.295) | **68.3 / 5.3 / 15.9 / 9.8 / 25.7 / 0.7** (65.3 / 6.5 / 14.8 / 13.0 / 27.8 / 0.4) | **11.1 / 6.5** / 1.5 / 38.5 / 42.4 (20.9 / 20.7 / 1.3 / 19.8 / 37.3) | mean 0.050, max 0.18 at f .10 (.72 against .54) |
| f34 (−35, 18) | 1.282 | 68.6 / 4.9 / 16.5 / 9.9 / 26.4 / 0.1 | 9.7 / 8.1 / 1.9 / 39.4 / 40.9 | |
| f34 (−22, 18) | 1.314 | 67.6 / 5.6 / 15.5 / 10.0 / 25.5 / 1.3 | 12.1 / 5.5 / 0.9 / 38.7 / 42.8 | |
| **front (0, 4)** | 1.555 (1.508) | 75.3 / 3.8 / 8.4 / 11.4 / 19.8 / 1.1 (68.1 / 4.7 / 14.8 / 12.1 / 26.9 / 0.3) | 15.6 / 6.4 / 0.0 / 14.3 / 63.7 (30.3 / 6.2 / 0.3 / 23.3 / 39.9) | mean 0.047, max 0.09; **width at h .85 / .95: .58 / .64** (.65 / .24) |
| front (0, 8) | 1.489 | 71.7 / 4.7 / 10.3 / 11.4 / 21.7 / 1.9 | | |
| side (90, 8) | 0.860 (0.785) | 71.4 / 0.0 / 15.0 / 13.6 / 28.6 (74.7 / 1.2 / 11.8 / 11.9 / 23.7) | | mean 0.082, max 0.39 at f .90 |
| rear (180, 8) | 1.505 (1.450) | 73.6 / 3.9 / 10.7 / 9.3 / 20.0 / 2.5 (67.9 / 4.6 / 15.1 / 12.1 / 27.2) | | mean 0.034 |
| r34 (145, 18) | 1.266 (1.262) | 70.2 / 1.1 / 15.3 / 9.7 / 25.0 / 3.7 (67.1 / 3.6 / 15.4 / 13.4 / 28.8) | | |
| top (0, 60) | 1.336 (1.356) | 37.9 / 8.5 / 38.3 / 14.4 / 52.7 (41.3 / 1.4 / 38.7 / 18.1 / 56.8) | | mean 0.045 |

- **Yellow flowers** (h 46–60, s ≥ 0.6, v ≥ 0.85): 0.06 % of the f34 and 0.03 % of the front, against 0.61 / 0.96 %.

**Front-cell opening (binding, at the ruled (0, 4)).**

| | w / W | h / H | top | bottom | centre | Row widths at 0.1 / 0.3 / 0.5 of the hole |
| --- | --- | --- | --- | --- | --- | --- |
| Sheet | 0.264 | 0.475 | 0.580 | 0.110 | 0.48–0.50 | vertical jambs |
| **(0, 4)** | **0.257** ✓ | **0.472** ✓ | **0.591** ✓ | **0.120** ✓ | 0.500 | 0.254 / 0.257 / 0.254 (vertical) |

- **f34 see-through:** 0.039 × 0.136 at (−28, 18), 0.090 × 0.194 at (−22, 18), and none at (−35, 18). The sheet shows
  0.144 × 0.261 (the round-1 perspective conflict; ruled).

**Leaf edge-on** (own code: 176 leaf shells; area within 12° of edge-on):

| View | All leaves | Visible leaves |
| --- | --- | --- |
| **f34** | **11.5 %** | **11.5 %** (target ≤ 12) |
| front (0, 4) | 44.8 % | 41.0 % |
| top | 18.5 % | 20.2 % |
| side | 48.0 % | 48.5 % |

**Colour.**
- **Keys:**
  - all 7 rock keys are R > G > B at hue 19–21° and sat 0.18–0.20, base `#A08B81`;
  - floor `#C39D75` (31°) and `#A08470` (25°);
  - grass `#A3B300` (65°);
  - leaf mixes from 79° to 107°;
  - flower `#B5B21A` (59°) and pebble `#AEAEA7`.
- **Finish:** rough 0.9 / 0.85 / 0.8, metal 0, emission 0 on every material. No sockets and no children.
- **Rendered medians, ours against the sheet (own masks):**

  | Material | Ours, f34 | Sheet, f34 | Ours, front (0, 4) | Sheet, front |
  | --- | --- | --- | --- | --- |
  | Rock, warm (h ≤ 60) | `#C4A491` | `#C7A99A` | | |
  | Rock, lit half | `#CCAC97` | `#CFB0A2` | `#C9A995` | `#D0B0A1` |
  | Floor | `#F7BF86` | `#F6BA80` | | |
  | Lawn | `#CFDF15` | `#D0D809` | | |
  | Bush | `#3A721F` | `#407616` | | |

  - The rock in the side, rear and r34 views (`#AA9286`, `#AE9689`, `#AF9689`) stays R > G > B: no mauve and no olive.
- **Leaf hue split in the f34 (F pixels):**
  - p10 / p50 / p90 at 68° / 101° / 105°;
  - 18 % of them at ≤ 88° (the fresh tone);
  - **0 % at ≥ 115°** (no emerald).
- **Facing.** Area-weighted correlation of painted lightness (diffuse × Tint) against the normal:
  - **Rock:** n.z 0.10 on the hero, 0.17 on the span and 0.07–0.10 on the masses; n.x and n.y ≤ 0.12.
  - **Lawn:** n.z −0.07.
  - **Floor:** n.z −0.02. Its |n.z| correlation of 0.99 is the tile-side band, which `tile()` picks by vertex z (top /
    bottom / side by the role of each face in the slab), not by normal.
  - **Leaves:** n.z 0.21. Their |n.z| correlation of 0.76 comes from the tier roles (flat crown leaves fresh, upright
    side leaves deep), not from facing.
- **`K.check`:** no problems.
- **Builder grep.** `normal` occurs only in geometry (path normals, leaf orientation, outline offsets,
  `recalc_face_normals`) and in the reports. No paint is chosen by facing.

### Fix round 1 claims, checked

| Claim | Verified |
| --- | --- |
| 0 dressing shells > 0.05 in rock, max 0.041 | **yes**: 0, max 0.041 (hero); parts 0 / 0.026 / 0 |
| 0 floating / unchained | **yes** on all five objects |
| 0 winding / non-manifold / bowtie / n-gon / zero-area / inverted | **yes** |
| Hero 3960, parts 986 / 872 / 808 / 184 | **yes** |
| 0 joint leaks | **yes** (own line and isolated-miss tests) |
| Seat ledge visible 0.0 from every sheet camera | **yes** (0.00 from 7 cameras) |
| Leaf edge-on at the f34 11.5 % | **yes**, 11.5 % |
| Opening 7.05–7.14 / 9.02 / 9.43–9.52 | **yes**: 6.98–7.09 to 5.4, 9.02 clear, apex 9.43–9.52 |
| Lawn over the central 14 × 6 ≥ 13.68 | 13.66 (≥ 13.6, inside the target) |
| f34 shares 68.4 / 5.3 / 16.1 / 9.6 | **yes** within 0.3 (68.3 / 5.3 / 15.9 / 9.8) |
| f34 green fifths 11.4 / 6.7 | **yes** (11.1 / 6.5) |
| Front (0, 4) hole .255 / .471 / .590 / .122 | **yes** (.257 / .472 / .591 / .120) |
| Front width at h .85 / .95 .58 / .64 | **yes** (.58 / .64) |

### Findings

No blockers.

1. **Minor: foot greenery is still sparse** (round 1's finding 2, partly fixed).
   - The f34 green fifths 1–2 are 11.1 / 6.5, against ≥ 14 each and the sheet's 20.9 / 20.7.
   - F is 9.8, against 13.3 ± 3: 0.5 short.
   - The front's bottom fifth is 15.6 against 30.3.
   - The sheet's foot is a lush lime apron with many small bushes; ours is a thin lime band with a dozen small clumps.
   - G (25.7) and the binding f34 shares are inside ±4.
   - **Target, if the main session wants it:**
     - widen the apron on the front and back to 1.8–2.0, staying inside the ruled 15.0 ± 0.6 depth;
     - replace 2–3 lawn pebbles or rim-bush crown leaves with 3–4 low foot sprigs;
     - aim for f34 fifths 1–2 at ≥ 14.
2. **Minor: the yellow flowers are effectively invisible.**
   - The f34 shows 0.06 % yellow and the front 0.03 %, against the sheet's 0.61 / 0.96 %.
   - **Target:** 6–8 flowers 0.5–0.6 across on the apron and the lawn rim, so the f34 reaches ≥ 0.3 %.
3. **Minor: the bushes lack the sheet's emerald.**
   - The f34 F pixels run p10 / p50 / p90 at 68° / 101° / 105°, and 0 % of them reach hue 115° or more.
   - The deepest mix used is `leaf_x_deep_60` at 107°, and the pure `leaf_deep` key (`#205D1F`, about 118°) is never
     used.
   - Decision 10's two-tone `#82C032` / `#1F6A21` therefore reads as fresh plus mid-green, not fresh plus emerald. The
     bush median (`#3A721F` against `#407616`) is still inside 14.
   - **Target:** skirt / inner tier and lower hearts at `leaf_deep` ≥ 80 %, so that ≥ 15 % of the f34's F pixels sit at
     ≥ 115°.
4. **Minor: the bush form.**
   - The clumps read as dark faceted hearts with a few flat lime plates. In the front (e 4) and side views the crown
     plates stand out as horizontal blades: edge-on 45 % / 48 %.
   - The binding f34 is at 11.5 %, and there are no palm stars, cabbages or hanging flaps, so this is accepted.
   - **Optional target:** crown leaves tilted 8–15° up at the tips, so the e 4 silhouette is rounder.
5. **Minor: the ledge pads read as shelves.**
   - P1 and P3 on the front skirts (and the right corner pad) sit below the skirts' pitched peaks. In `cu_footl` and the
     front view they read as lime planks bolted onto the side of a spike, with a bush on top ("potted plant on a shelf").
   - One pad is up to 0.35 inside its skirt, which hides some faces.
   - **Target:** sit each pad on a flat skirt crown at the crown's height (the skirt's peak cut to the pad), or drop
     the pads and put the bushes at the skirt feet.
6. **Minor: the outline (round 1's finding 3, partly fixed).**
   - The front width at h .95 is .64 against .24, because the rim-bush tops form a level row over decision 8's walkable
     lawn.
   - The f34 profile at f .10 is .72 against .54 (max 0.18; mean 0.050 is on the limit).
   - The side profile falls one bin early at f .90 (.29 against .68; max 0.39), and the side W:H is 0.860 against
     0.785 ± 0.08. Both come from foot bushes past the footprint.
   - These are trade-offs against decision 8 and the ruled depth.
   - **Target, if revisited:** lower the four outer rim bushes by 0.3–0.4 down the lip drape, so the front width at
     h .95 is ≤ .45.
7. **Minor: the lawn edge in the top view has sawtooth points on both shoulders.**
   - Sharp lime triangles stand out where the cap drapes. The sheet's edge is softly scalloped.
   - **Target:** shoulder outline points spaced ≥ 0.8 apart with offsets alternating ≤ 0.15.
8. **Minor: the front and rear shares at near-level cameras.**
   - The front (0, 4) is R 75.3 / G 19.8 against 68 ± 4 / 27 ± 4, and the rear R 73.6 / G 20.0.
   - These views see little lawn top (L 8.4–10.7). This is not binding (§2.6), and findings 1 and 6 would help.
9. **Minor (known, accepted): the span lumps** read on `part_span` and over the hole in the f34. In the front and rear
   the span face still reads as more columns with a horizontal crease at z 8, rather than the sheet's 4 rounded
   boulders. Nothing more is asked this round.
10. **Minor (record): the boulders reach x ±12.75 and y −6.8.** The cores are 24.4 × 12.4. Accepted with the ruled depth.
11. **Passes:**
    - the mesh, winding and topology on all five objects;
    - the budget (3960 / 986 / 872 / 808 / 184);
    - 0 buried dressing (max 0.041);
    - 0 floating or unchained shells;
    - 0 see-through cracks and no ground showing at the jamb feet;
    - capping: 0 flat rock exposed, and the lawn over every top;
    - the seat-ledge slivers are hidden;
    - the opening: 7.0 wide, 9.02 clear, apex 9.43, vertical jambs to 5.4;
    - every front-cell number at (0, 4);
    - the walk test and the lawn ≥ 13.6;
    - the thinner lip;
    - the f34 W:H and the binding f34 shares (R +3.8, G −2.8, L +0.7, P −1.3; F 0.5 short of its own ±3);
    - edge-on 11.5 % at the f34;
    - the warm rock R > G > B in every view, and the floor, lawn and bush medians inside their tolerances;
    - no colour by facing (`K.check` clean, and the grep);
    - UV clean;
    - no lighting or VFX;
    - the collision tags, names and keys.
    - Decisions 1–14 as amended are followed. Decision 10's emerald tone is weak (finding 3), but the colour family and
      the two-tone split are present.

**Defining read.** In the front, rear, top and f34 the model reads as a squat, columned stone arch with a walk-through
tunnel, a sand floor, a lime lawn dome and bushes on top. The f34's opening is a narrow slit, against the sheet's clear
see-through. That is the ruled perspective conflict, and the tunnel and its floor are plainly visible.

### Score and verdict

**7.5 / 10. PASS (round 2).**
- The round-1 blocker is fixed and verified independently: 0 dressing shells more than 0.05 in rock.
- Nothing is broken.
- The remaining items (1–10) are visual gaps against the sheet's dressing density, flowers, emerald tone and outline.
  They are recorded for the commit notes.

## Main session ruling (2026-10-29)
- **Verdict:** passed in round 2 (7.5/10) and committed. Round 1 failed (6.5/10) because 33 foot-bush shells were buried in rock.
- **Left for a later polish pass:**
  - Foot greenery is sparse: f34 fifths 1–2 are 11.1 / 6.5 against a target of 14.
  - Yellow flowers are invisible.
  - The bushes have no emerald.
  - Crown leaves read as horizontal blades in the front view.
  - Ledge pads read as shelves.
  - The front width at h .95 is .64 (the rim bushes stand in a level row).
  - The lawn edge has sawtooth points.
  - The span lumps read as columns from the front.
  - The skirts reach x ±12.75.
- **Export:** 5 assets, 5 solid pieces, 6810 tris, 0 VFX sockets, palette 27 colours, 0 problems.
