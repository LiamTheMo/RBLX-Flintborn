# 043 Terraced Ledge — spec

Reference: `art/blender/assets/references/043.png` (1024 × 1536 px). The sheet's title is "TERRACED LEDGE", with
"FLINTBORN ENVIRONMENT MODEL CATALOG / STYLIZED • MODULAR • GAME-READY (BLENDER / ROBLOX)" at the top and "PAGE 42 / 132"
at the top and bottom right; the footer reads "FLINTBORN — INDIVIDUAL MODEL STUDY". INDEX.md row 43 calls it "Flintborn
terraced ledge model study".
Builder: `art/blender/kit/mcp/m043.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7).

Sheet text:
- **Intro:** "Two broad flat walkable levels. Useful as platforms and intermediate cliffs."
- **Cells:** "FRONT THREE-QUARTER VIEW", "REAR THREE-QUARTER VIEW", "ORTHOGRAPHIC VIEWS": "FRONT", "SIDE (RIGHT)", "REAR",
  "TOP (OVERHEAD)".
- **Exploded:** "EXPLODED CONSTRUCTION" ("Modular parts with simple clean connectors. Reusable across various
  layouts."): "Upper Ledge Cap", "Lower Ledge Shelf", "Main Cliff Base", "Corner Filler Rock", "Side Connector (Flat
  Back)". Dashed lines drop the cap onto the shelf and the shelf onto the base; a dashed double arrow pushes the connector
  against the assembly's end.
- **Close-ups (right column):** "JOINING SURFACES (UNDERSIDE)": "Upper Ledge Cap (Underside) / Flat joining surface for
  clean stacking." "THICKNESS & EDGE DETAIL": "Ledge thickness with clean, chunky forms. Simple bevels, no small
  details."
- **Construction close-ups:** "A. LEDGE JUNCTION (SIDE VIEW)": "Clean vertical stacking surfaces." "B. BOTTOM / GROUND
  SIDE": "Flat bottom surface (sits on ground). Simple, sturdy form." "C. SIDE CONNECTOR DETAIL": "Flat back connector
  for modular building." / "Clean rectangular slots and tabs."
- **Material palette:** "Rock (Main)", "Rock (Shadow)", "Grass / Foliage", "Dirt / Soil".
- **Game context:**
  - WorldModeling §12.2: "Build a terrain chunk with a flat rear/connector region, broad faceted front buttresses, a
    walkable top, and a separate grass lip … Split terraced ledges into an upper cap, lower shelf, and corner filler."
  - **M040 Cliff Wall** (built, not yet committed: `m040.py` is untracked) is the same generator's cliff tile, with the
    same stone, lawn, bushes and plate language: a 16 × 8 tile, lawn at **z 10.4**, seams x ±8, a flat back plane, a grey
    plate on the +X end (y back 3.9, z 0–10.05). **M032** and **M041** share the 10.4 plateau. This ledge is the
    two-step tile that leads up to that plateau (§2.1).
  - **The old kit's W02 row 2 `TerracedLedge`** (`art/blender/scripts/kit/W02/terraced_ledge.py`, goals
    `art/blender/renders/kit/W02/terraced_ledge_goals.md`, manifest `art/roblox/kit/W02/manifest.json`) is a different
    drawing: 32 × 32 × 24, decks at z 12 / 24, a full-width back plate, a notch with a filler, a dirt band under the turf.
    `MODEL_PROGRESS.md` row 49 flags it "rock hidden under flat lime slabs; low smooth cliffs". **W02 owns every
    `TerracedLedge*` name** (§8). Reuse its lessons, not its sizes or names.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Cell paper `#FEFBF5` (254,
251, 245), tolerance 10. Labels are painted out (`TITLES` in `m.py`). Masks are `cls()` in `m.py` (HSV, h in degrees):
- **R, rock:** h ≤ 50 or ≥ 190, s < 0.45, v ≥ 0.25, and not another class. Lit faces are warm peach (h 18–27°); shaded
  faces are cool blue-lavender (h 225–255°). Both count as R. Lawn boulders and pebbles are R.
- **L, lawn:** green (h 45–170, s ≥ 0.28, v ≥ 0.12) with h < 80 and v ≥ 0.62. It also catches the lit tops of the lime
  bushes and the yellow flowers.
- **F, foliage:** the rest of green (the bushes' mid and dark leaves, the shaded lime leaves).
- **D, dirt:** h 8–40, s ≥ 0.45, v ≥ 0.22, not green (bush trunks, flower centres; the exploded cap's soil sides).
- **C, connector:** R or B pixels with s < 0.12 inside the plate rectangles `CONN`. The side cell's rectangle over-counts
  shaded rock; the uniform plate alone is measured with `plate.py`.
- **B, ground shadow:** near-white with s < 0.06–0.10. **Background.** **T:** v < 0.25, s < 0.35. **O:** outlines.
- Cells: f34 (185,122,612,436) (the title "TERRACED LEDGE" ends at y 120; the intro text at x < 245, y < 200 is painted
  out); r34 (615,90,1006,436); front (17,520,299,750); side (303,520,514,750); rear (517,520,775,750); top
  (778,520,1007,750); exploded (17,790,737,1200); joining underside (740,800,1007,930); thickness (740,1005,1007,1152);
  close-up A (17,1266,349,1490), B (353,1266,685,1490), C (689,1266,1007,1490). Swatch inner boxes 28 × 26 px at x 29–57,
  y 266 / 307 / 349 / 390 (`m.SW`).

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m043_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14, Pillow, numpy).
- **Helpers:** `m.py` (masks, boxes `V` / `X` / `CONN` / `SW` / `TITLES`, `label`, `main_obj`), `zoom.py` (crop, optional
  sheet grid), `px.py` (pixel probe), `prev.py` (mask previews `cls_*.png`), `blendall.py` (name search in every `.blend`).
- **Measurements:** `measure.py` → `measure_out.txt`, `bb.json` (bbox, W : H, shares, top profile, width per height, G /
  L / R fifths); `bands.py` → `bands_out.txt` (lawn and rock bands per column); `rows.py <view>` (class extents per row);
  `parts.py` (exploded components); `under.py` (underside flat share, plate extents); `plate.py` (side plate share).
- **Layout fits:** `proj.py`, `proj2.py`–`proj5.py`: an orthographic model of the stepped block with its dressing,
  projected at the sheet cameras; used to choose the size (§1.1, §3.1).
- **Colour:** `samp.py` → `samp_out.txt` (per cell: rock all / warm / cool, lawn, foliage, dirt, connector; warm rock
  thirds), `samp2.py` → `samp2_out.txt` (dark / mid bush greens, lime leaves, yellow flowers, lawn by band).
- **Zooms:** `zn_f34.png`, `zn_r34.png`, `zn_ortho.png`, `zn_front.png`, `zn_side.png`, `zn_rear.png`, `zn_top.png`,
  `zn_expl.png`, `zn_cuR.png`, `zn_cuB.png`; gridded `z_f34.png`, `z_side.png`, `z_plate.png`, `z_expl.png`; detail
  `z_bushL.png`, `z_foot.png`.
- **On our renders:** `..\m041_study\measure_render.py` or M040's `measure()`; or point `R` in `m.py` at the render, set
  `P` and the `V` box, and re-run `measure.py` / `samp.py`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a modular terrain tile. Hero budget 4000 tris, each part under 1000. The plan in §4.3
  lands at about 3300–3700.
- **Overall read (check this first).** A **broad block of pale warm column rock that steps up in two flat lime
  terraces**:
  - a **lower step**: a palisade of about seven tall flat-faced columns across the full width, capped by a **lower
    lawn shelf** that runs the full width in front and **wraps a little round both ends** of the upper block;
  - an **upper block** set back about 6 studs, about 0.8 of the width at its front: a second palisade of about six
    columns, capped by an **upper lawn**;
  - a **full-height columnar back** (rear cells);
  - **round bushes** on both lawns: dark green with brown trunks, lime, and lime with **broad yellow flowers**; a pale
    boulder or two on each lawn;
  - at the foot, a **lime grass apron**, foot bushes, a pointed foot rock, pebbles;
  - on the **+X end, a flat grey connector plate** with slots and tabs (side cell, close-up C).
  - Hero shares (f34): rock 64.8 %, green 34.8 % (lawn 23.6, foliage 11.2), dirt 0.4 %.
  - Green by height fifths (bottom → top), f34: 13.8 / 8.4 / **43.3** / 14.3 / 20.2. Front: 18.2 / **0.8** / 42.8 /
    **3.1** / 35.1. **The two cliff bands are bare rock;** the green is the foot, the lower lawn (the middle fifth) and the
    upper lawn.
- **Focal silhouettes, in order:**
  1. The two level lawn lines, one above the other, the lower one wider. Front cell: lower lawn front edge at h .40–.42,
     its back edge (the upper face's foot) at h .53–.55, the upper lawn front edge at h .79–.80, its back at .89–.90.
  2. The two column palisades with dark full-height creases. Every column reaches its lawn line; none stands above it.
  3. The lower lawn showing at **both ends** of the upper block in the front and f34 (bush groups left and right).
  4. The foot dressing (apron, pointed foot rock, bushes).
  5. The grey plate in the side view.
- **Target tile: 20.0 W × 14.0 D; lower lawn top z 5.6, upper lawn top z 10.4** (M040's plateau). The bbox is about
  21.2 W (foliage overhang ≤ 0.6 per end) × 15.4 D (foot apron and dressing in front, back tabs) × 12.3 H (bush tops on
  the upper lawn). Tolerances: W, D ±0.4 on the rock; the seam pitch 20.0 and the lawns 5.6 / 10.4 are exact; bbox H
  ±0.4. Decision §8.1.
  - **How it was derived.**
    - **Plan depths:** the side cell, the most direct view of depth, gives a lower terrace 5.4 and an upper block 6.3
      deep for 157 px of upper-lawn height. The front cell's lawn bands (lower .40 → .55, upper .80 → .89) give a lower
      terrace about 1.4× the upper's screen depth. Adopted: **lower 6.0, upper 8.0** (8.0 = M040's tile depth, so the
      upper block and M040 line up front and back, §2.1). D / H = 14 / 10.4 = 1.35; the side cell's W : H is 0.995, and
      the model gives 1.02 (§2.5).
    - **Width:** the f34 (W : H 1.375) and front (1.359) need about 20 wide at a 10.4 lawn (`proj3.py`: 20 × 14 gives
      front 1.34–1.40, f34 1.29–1.39; 16 × 14 gives only 1.12–1.19, −0.2). The front cell's upper face spans 0.80 of the
      lower foot (R extents: 203 / 255 px at its foot, 189 at its top): **16.0 → 14.8 of 20**.
    - **Heights:** lower lawn / upper lawn = 0.50 (side), 0.56 (rear), 0.59 (front, elevation-corrected), 0.62 (f34).
      Mean 0.57 → 5.9; adopted **5.6** (0.54) as a compromise toward the side cell.
  - **Why this size.**
    - The upper lawn at 10.4 meets M040, M032 and M041 at one plateau.
    - The two rises are 5.6 and 4.8. Both are under a default Roblox jump (JumpHeight 7.2), so a player can climb from the
      ground to the plateau in two jumps: "two broad flat walkable levels … platforms and intermediate cliffs". A bare
      10.4 cliff (M040) can't be jumped.
    - 14 deep = M040's 8 plus a 6-deep lower terrace in front.
    - 20 wide is not a 16-stud pitch. The trade (§3.1, decision §8.1): 16 wide would miss the hero's W : H by about 15 %.
  - **Against the character (5.5):** the lower lawn is at about one character height (5.6); the upper lawn at 1.9
    characters. The lower terrace (6 deep) is just over a character's height in depth, room to stand and jump. The upper
    face columns are 2.6–2.8 wide; the bushes are 1.0–1.9 tall (knee to chest).
- **Build frame:** front −Y, +X right, ground z 0. Tile seams at x = ±10.0, back plane y = +7.0, lower column fronts
  y ≈ −7.0, upper face y ≈ −1.0. Stage 2 re-centres the hero on its bbox bottom centre; record where the seams and the
  back plane end up relative to the origin, as M040 did (`m040_offset`).

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | R | L | F | G (L + F) | D | C | O |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (185,122,612,436) | 187–604 × 125–428 (418 × 304) | **1.375** | 64.8 % | 23.6 | 11.2 | **34.8** | 0.4 | 0 | 1.6 |
| Rear three-quarter (615,90,1006,436) | 622–997 × 95–422 (376 × 328) | 1.146 | 74.4 | 15.7 | 9.6 | 25.3 | 0.3 | 0 | 1.4 |
| Front (17,520,299,750) | 27–287 × 539–730 (261 × 192) | **1.359** | 72.0 | 19.1 | 8.6 | 27.7 | 0.3 | 0 | 2.1 |
| Side (303,520,514,750) | 313–500 × 542–730 (188 × 189) | **0.995** | 45.9* | 6.0 | 6.8 | 12.8 | 0.1 | 41.3* | 1.7 |
| Rear (517,520,775,750) | 529–762 × 540–728 (234 × 189) | 1.238 | 84.0 | 10.1 | 5.7 | 15.8 | 0.2 | 0 | 1.8 |
| Top (778,520,1007,750) | 795–991 × 536–727 (197 × 192) | 1.026 (W : D) | 33.2 | 55.8 | 10.5 | 66.3 | 0.6 | 0 | 1.5 |
| Exploded (17,790,737,1200) | main group 234–594 × 790–1184 | — | 74.2 | 13.9 | 7.3 | 21.2 | 4.6 | — | 1.1 |

- *Side: the rectangle mask over-counts the plate. The uniform grey plate alone (`plate.py`) is **36.5 %** of the
  silhouette, and it spans x 425–498 of 313–500 (**0.36–0.43 of the depth**). Rock ≈ 50 %.
- Shares are of R + L + F + D + C; O and B are left out. **Verifier tolerance:** shares ±4 points (G ±5 in the back
  views); W : H ±0.06; positions ±0.04 of W / H unless stated.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .21 | .31 | .46 | .56 | .78 | .83 | .86 | .89 | .86 | .88 | .89 | .94 | .95 | .98 | .97 | .97 | .88 | .67 | .68 | .55 | .22 |
| Front | .12 | .43 | .60 | .83 | .90 | .91 | .96 | .89 | .92 | .90 | .90 | .91 | .96 | .96 | .99 | .92 | .96 | .86 | .58 | .51 | .14 |
| Side | .11 | .43 | .50 | .53 | .59 | .57 | .55 | .59 | .62 | .67 | .80 | .84 | .86 | .89 | .92 | .90 | .96 | .98 | .98 | .94 | .77 |
| Rear | .17 | .53 | .58 | .86 | .95 | .99 | .97 | .93 | .94 | .91 | .90 | .91 | .94 | .92 | .91 | .89 | .96 | .95 | .87 | .61 | .20 |
| r34 | .30 | .62 | .66 | .78 | .88 | .89 | .93 | .92 | .98 | .97 | .94 | .88 | .86 | .87 | .81 | .79 | .78 | .80 | .74 | .54 | .22 |

- Reading:
  - **Front:** f .05–.10 and .90–.95 are the lower lawn's ends (h .43–.60, bushes on them); f .15–.85 is the upper lawn
    (.83–.99 with bush bumps).
  - **f34:** the left shoulder (f .05–.15, h .31–.56) is the lower lawn and its bushes left of the upper block; the right
    shoulder (f .85–.95, .55–.68) is the lower lawn right of it.
  - **Side:** the step: f .05–.45 is the lower terrace (h .43–.67, bushes); from f .50 up it is the upper block and plate
    (.80–.98).
  - **Rear:** f .05–.10 is the low step at the +X back corner (h .53–.58, §3.4).

**Width per height** (silhouette width at h .05 → .95, fraction of W):

```
f34    .50 .91 .98 .91 .88 .80 .75 .64 .52 .18
front  .90 .98 .96 .93 .90 .84 .77 .74 .69 .51
side   .74 .98 .96 .96 .94 .82 .54 .52 .38 .13
rear   .93 .99 .98 .97 .94 .89 .82 .79 .76 .63
```

- **Rock-only widths, front cell** (`rows.py front`): lower face 255 px at its foot, 239 at its top (h .40); upper face
  203 at its foot (h .55), 200 at h .65, 189 at its top (h .80). In studs at 20 = 255 px: **lower 20.0 → 18.7, upper
  15.9 → 14.8**. The upper block is centred (left inset 24 px, right 28).

**Lawn bands** (`bands.py`, fraction of H, front cell): lower lawn .40 → .52–.55 at f .45–.85; upper lawn .79/.80 →
.86–.90 at f .30–.80; rock (lower face) .03/.06 → .39–.41, rock (upper face) .53–.56 → .78–.80. **f34:** lower lawn
.39–.43 → .55–.57 (f .50–.75); upper lawn .77–.80 → .87–.89 (f .45–.75).

**Green fifths** (bottom → top, % of all green): f34 13.8 / 8.4 / 43.3 / 14.3 / 20.2; front 18.2 / 0.8 / 42.8 / 3.1 /
35.1; side 5.2 / 0 / 52.6 / 3.0 / 39.2; rear 33.2 / 0 / 10.4 / 1.4 / 55.0; r34 21.1 / 9.9 / 3.3 / 39.6 / 26.2.
**Rock fifths**, f34: 21.8 / 38.3 / 14.1 / 23.2 / 2.6.

### 1.3 Silhouette and composition per view

**Front three-quarter (`zn_f34.png`, `z_f34.png`): governs.** An elevated view from a little to the front-left (we use
az −15, e 20, §3.1): the long lit front, the −X end as a narrow dark band at the left.
- **Lower step:** about seven to eight columns across the front (sheet x 222–600), each with a lit front face and a
  shaded left face, and dark full-height creases. The tops sit level under the lower lawn's front edge (h .39–.43). The
  lower-left end is a tall column (sheet x 222–250) with its dark end face.
- **Lower lawn:** a flat lime band (h .39 → .57) along the whole front.
  - It widens at both ends where the upper block stops: left, a pocket with a **dark bush LL1** and a **yellow-flowered
    lime bush LL2** (sheet x 240–320, y 255–285); right, a **lime bush LL5** at the far end (x 537–575, y 220–250).
  - Between them: a **pale boulder LB1** (x 365–402, y 280–310); a small dark bush **LL3** beside it; a **dark bush LL4**
    against the upper face's foot (x 445–485, y 225–258); yellow-flower sprigs; a small boulder **LB2** at the right
    (x 518–538); pebbles.
- **Upper block:** about six columns (x 255–535 at the top), set back. Its left end is a dark sloping face (x 255–272);
  its front edge rises gently to the right (perspective).
- **Upper lawn:** a flat lime top (h .77 → .89). It holds:
  - a **dark bush UL2** at the front-left corner (x 268–305) and a **dark bush** behind it (x 310–345);
  - a **pale boulder UB1** at the left-centre (x 355–385, y 160–190);
  - at the back right, sprigs, a **big dark bush UL3** (x 445–480, y 125–160) and a **lime bush UL4**;
  - pebbles.
- **Foot:**
  - a lime apron along the whole foot;
  - a **dark bush F1** at the −X front corner (x 197–235, y 330–370);
  - a **pointed foot rock FR1** at the front centre (x 389–428, y 385–430), about 2.3 tall;
  - small pale rocks and pebbles;
  - yellow-flowered sprigs at the left foot; bushes **F4–F6** spaced along the right foot.

**Front (`zn_front.png`).** An elevated front view (az 0, e ≈ 18°: the lower lawn's screen depth gives sin e ≈ 0.30–0.34).
The same two palisades: lower face 7 columns (x −10 … +10 in studs at 12.75 px/stud), upper face 6 columns (−8.0 …
+7.9 at its foot). Positions in studs (X = (sheet x − 157.5) / 12.75):
- **Upper lawn:** lime-dark bush −6.9 … −5.4; dark bush −5.2 … −3.2; boulder −3.0 … −1.2; lime sprig +1.0 … +2.5; dark
  bush +2.9 … +4.9; lime bush +5.1 … +6.9.
- **Lower lawn:** yellow-flowered lime group −7.0 … −4.9; boulder −3.6 … −1.9; yellow sprig −2.7 … −0.9; dark bush
  +1.6 … +3.5 against the upper face; sprigs at +1.0 and +4.5 … +5.2; small boulder +5.0 … +6.0; lime bush +7.2 … +9.1.
- **Foot:** yellow-flowered lime clump −7.5 … −4.8; small pale rock −6.6 … −5.7; pointed rock FR1 −3.8 … −1.4 (top h
  .18); bushes and sprigs at −0.9 … −0.2, +1.6 … +2.8, +4.5 … +5.7, +7.6 … +9.3; the apron along the whole foot.

**Side (right) (`zn_side.png`, `z_side.png`, `z_plate.png`).** The +X end, near-level.
- **Front ~0.4 of the depth:** the lower step's end in rock (columns, lit and shaded), its lawn at h .43–.50 with bushes
  on it (sheet x 313–390).
- **Behind it:** the upper block's end, also rock, from the lower lawn up to the upper lawn (h .80). It is a narrow strip
  in front of the plate, x 395–430.
- **Plate:** a **flat warm-grey plate** (`#9C908F`) over the back 0.36–0.43 of the depth (x 425–498), from the ground to
  the upper lawn line (y 566–568). Its features:
  - its front edge is notched: **dark rectangular slots** at y 660–675, 690–700 and 712–725 low down, and at y 600–610
    and 575–580 higher up;
  - **tabs** stand proud of its back edge at y 585–600, about 640–650 and 705–715;
  - small notches on its top edge (x 452–458, 470–478).
- **Upper lawn and bushes** on top (big dark bush at the back).

**Rear (`zn_rear.png`) and rear three-quarter (`zn_r34.png`).** Both draw the **back as one full-height columnar face**:
about six tall columns, two **big pointed leaning wedges** against it (rear x 590–640 and 650–705 in sheet px, the taller
to h .6), small foot rocks, and sprigs along the foot. Both draw a **low step with lawn and a bush at the +X back corner**
(rear left, r34 far left; top at h .47–.59). The r34 is seen **from the back-left**: the back face recedes to the left, and
the −X end is on the right, with a mid-height column ledge and a lime bush. Both show **no plate** (§3.4).

**Top (`zn_top.png`; image top = the back).** One near-square lime lawn (W : D 1.03) framed by a pale rock rim. It holds:
- dark bushes with brown trunks at the back-left, back-right and front-left; a lime bush at the front-right;
- boulders at the back-centre-right, front-right (big) and front-right (small); sprigs at the edges; pale pebbles;
- along the bottom edge, the stepped front column tops.

It shows **one level** only: no lower terrace, no step (§3.3).

**Joining surfaces (underside) (`zn_cuR.png`).** The upper cap from below: **one big flat face** (`#8E7F7C` in shade,
0.51 of the visible silhouette) inside a **ring of chunky rock rim lobes** that hang below it; a lime edge shows at the
left. Screen W : H 2.09.

**Thickness and edge detail (`zn_cuR.png`).** A lawn edge over the column tops. **Between the turf edge and each column's
face there is a pale lit bevel band** (`#FBD2AA` lit, about 0.3–0.4 stud), then the tall lit column faces with a crease
between them. Round bushes and a pale boulder sit on the lawn; a lime bush with yellow leaves stands at the right, and the
upper face rises behind.

**Close-up A, ledge junction (`zn_cuB.png`).** The lower lawn (left), with dark bushes, meets a **tall column face rising
from it, a clean vertical joint**. On the right, a column top steps down to a lower lawn with a dark bush and a boulder:
the step between levels.

**Close-up B, bottom.** The body from below: **one big flat bottom face** (0.48 of the visible silhouette) inside a ring of
column lobes that bevel up from it. Screen W : H 1.61.

**Close-up C, side connector.** A column end (lit) with lawn on top. **Right behind it, the grey plate**: a flat
rectangle with a small notch at its top-left corner, **one tab on its front-left edge at mid height** and slots on its
right edge.

### 1.4 Parts (Exploded Construction (17,790,737,1200), `zn_expl.png`, `z_expl.png`, `parts.py`)

An elevated three-quarter view from the front-left (e ≈ 25°). **The hero governs every size**; the parts give shapes,
part boundaries and facet character.

| Part | Box (sheet px) | Screen size | Notes |
| --- | --- | --- | --- |
| Upper Ledge Cap | (350,805,583,878) | 233 × 73 | A flat lawn slab with a pale boulder and dark / lime bushes at the back right. **Orange-brown soil sides** (`#D29766`, lit `#E2A66F`) broken into blocks, about 0.35 of its visible front height (§3.5) |
| Lower Ledge Shelf | slab (335,905,565,1010) | 230 × 105 | A lawn slab with **pale rock rim lobes** (not soil), bushes along it, a boulder |
| (unlabelled) left column with lawn top | (233,955,345,1165) | 112 × 210 | A tall end column (lit front, shaded left), lawn and bushes on top: the lower step's −X end |
| (unlabelled) tall back block | (520,872,590,1005) | 70 × 133 | A plain box column, flat top, no lawn: the upper block's end |
| Main Cliff Base | (350,985,588,1182) | 238 × 197 | A columnar block with a **big flat top face** and columns on its front: the lower step's body |
| Corner Filler Rock | (620,960,725,1103) | 105 × 143, w/h 0.73 | A **tall wedge**: a near-vertical front, a **sloping top** (high at the back-left), a notch step on its right flank, broad facets |
| Side Connector (Flat Back) | (130,895,207,1112) | 77 × 217, w/h 0.35 | A flat plate seen at an angle (dark thickness strip on its left), **a notch at the top-left**, **three tabs on its right edge** (y ≈ 935, 1010, 1085) and slots on its left |

The exploded pulls the body apart differently from the assembled views (§3.6). Its useful content:
- the **cap / shelf / base / filler / connector** split (WorldModeling §12.2);
- **flat joining faces** (the base's flat top, the cap's flat underside);
- the filler's wedge shape;
- the plate's slots and tabs.

#### Main Cliff Base (the stepped rock body)
- **Shape:** tall vertical rock columns, side by side, with dark creases. **Facets are long vertical strips**, many split
  into two or three triangles along the height (rear and f34). Tops are flat and level under each lawn, with a pale
  bevel band (thickness close-up). The bottom is flat (close-up B).
- **Hero size: 20.0 × 14.0**, lower columns to z 4.4, upper columns to z 9.2, back columns full height 0 → 9.2.

#### Lower Ledge Shelf
- **Shape:** a flat lawn slab over a pale rock rim of chunky blocks, with a flat recessed underside. Its front edge is
  scalloped by the column ridges. It wraps into the end pockets (§2.3).
- **Hero size:** about 20.0 × 6.3, plus the two pockets; rim bottom 4.37, turf 5.3 → **5.6**.

#### Upper Ledge Cap
- **Shape:** as the shelf, at the upper level. The underside is **one flat face inside rim lobes** (joining-surfaces
  close-up).
- **Hero size:** about 20.0 × 8.2 less the front pockets; rim bottom 9.17, turf 10.1 → **10.4**.

#### Corner Filler Rock
- **Shape:** a 5-sided wedge pillar: three broad side faces, a sloping top facet, a notch step half-way up one flank.
  Never an egg.
- **Hero size: 2.2 × 2.0 × 3.5**, standing in the −X end pocket on the lower lawn (§2.3).

#### Side Connector (Flat Back)
- **Shape:** a flat rectangular plate, dead flat on both faces, about 0.4 thick, with three slots in its front edge,
  three tabs on its back edge and a small notch at the front-top corner.
- **Hero size: 5.2 (Y) × 10.05 (Z) × 0.4 (X)** on the +X end (§2.1).

#### Bushes, flowers, rocks (`z_bushL.png`, `z_foot.png`)
- **Dark bush:** a round clump of **broad rounded leaves** (each a blunt-tipped oval, 4–5 per tier, two tiers) round a
  short **brown trunk** that shows at the base; the top view reads as a rosette with a dark centre. Ø 1.8–2.2, 1.6–1.9
  tall.
- **Lime bush:** the same build, smaller, yellow-lime leaves (`#A8B509`–`#B0D004`). Ø 1.4–1.8, 1.2–1.4 tall.
- **Yellow-flowered bush:** a lime bush with 3–5 **big broad rounded yellow petals / leaves** (`#E1D226`) on top and a
  dark centre (`z_bushL.png`: they read like large yellow blossoms). Ø 1.4–1.8.
- **Sprig:** 3–5 lime leaves from one root, sometimes with 1–3 small yellow buds. Ø 0.7–1.0.
- **Lawn boulders:** pale, rounded-angular, a flat-ish crown, 4–6 broad facets visible (1.2–1.8 across). **Foot rock**
  FR1: pointed, leaning into the face. **Pebbles:** 0.25–0.5, pale.
- **Apron:** a thin lime strip along the foot, jagged edge.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0).

### 2.1 The tile contract (binding; record it in the builder docstring and the export notes)

| Item | Value | Notes |
| --- | --- | --- |
| Seam planes | **x = −10.0 and x = +10.0** (pitch 20.0) | no rock or plate vertex past them; foliage may overhang ≤ 0.6, symmetric |
| Back plane | **y = +7.0**, flat (column relief inward only, to y ≥ +6.5) | "flat rear/connector region" (WorldModeling §12.2) |
| Lower column fronts | y −6.8 … −7.3 (in / out per column) | the front is irregular, the seams are not |
| Lower column tops | **z 4.4** (flat, all of them) | under the lower shelf |
| Lower shelf | rim bottom 4.37 (sunk 0.03), recess 4.7, turf **5.3 → 5.6** | lawn flat within ±0.03 for 1.0 stud of each seam |
| Upper face | columns y −0.8 … −1.3, standing from z 4.4 (feet under the lower shelf) to **z 9.2** | the shelf's back edge tucks 0.15 into them |
| Upper block front corners | chamfered: from (±(10 − c), −1.0) to (±10, +1.0), **c 2.0 at z 4.4 → 2.6 at z 9.2** (the chamfer face leans in) | the end pockets of lower lawn (§3.2) |
| Upper cap | rim bottom 9.17, recess 9.5, turf **10.1 → 10.4** | identical to M040's lip levels |
| End profile at the seams | identical at x = −10 and x = +10: the lower step's end planar from y −6.0 to +7.0, z 0 → 4.4; the shelf's end planar from y −6.0 to +1.0, z 4.37 → 5.6; the upper block's end planar from y +1.0 to +7.0, z 4.4 → 9.2; the cap's end planar from y +0.9 to +7.0, z 9.17 → 10.4 | so any tile meets any tile; at +X the plate covers y +1.8 … +7.0 (below) |
| Lower step front corners | chamfered from (±(10 − c), −7.0) to (±10, −6.0), **c 1.0 at z 0 → 1.4 at z 4.4** | front-cell taper (§3.2) |
| Connector plate | **+X end only**: x 9.6 … 10.0, **y +1.8 … +7.0, z 0 … 10.05**; 3 front slots, 3 back tabs (0.35 behind y +7.0), top notch | the next tile's −X end meets the plate's outer face on the seam plane |
| Core +X end behind the plate | steps in to x 9.62 behind y +1.6 (the plate overlaps it by 0.02); the groove y +1.6 … +1.8 is the dark edge strip | as M040 (`CORE_X`, `GROOVE_Y`) |
| Cap end over the plate | over y +1.8 … +7.0 the cap's +X end stops at x 9.98, overlapping the plate's top 0.88 (z 9.17 … 10.05) as M040's lip does | never coplanar with the plate's outer face (x 10.0) |

- **How tiles meet.** Place tiles every 20 studs along X with the same rotation. Tile N's plate touches tile N+1's flat
  −X end. The two lower shelves join flush at 5.6, the two upper caps at 10.4. The two end pockets meet as one V bay of
  lower lawn, 4.0–5.2 wide, in the upper face: in a run, the upper cliff reads as buttresses with bays, as the sheet's
  front and f34 show at each end.
- **With M040 (16 × 8, lawn 10.4, back plane at its y +4.0).** Align the back planes (M040's y +4.0 ↔ this y +7.0).
  Then:
  - the upper block and M040's body have the same depth (8);
  - the lawns meet at 10.4; M040's lip front at its seams (back − 8.2) ↔ this upper face (back − 8.0);
  - M040's flat −X core end covers back 7.2, which covers this plate (back 5.2);
  - M040's plate (back 3.9) meets this flat −X upper end.

  The pocket shows as a bay at the joint. Record it.
- **Run ends:** a +X run end shows the plate (as the side cell does); a −X run end shows the flat rock ends.

### 2.2 Body (one rock shell, decision §8.5)

Built as two lofted solids unioned at the origin (M040's palisade method), then floor-cut at z 0:
- **L, lower step:** outline x ±10, y −7.0 (column fronts) … +7.0, front corners chamfered, z 0 → 4.4. Its back part
  is inside U.
- **U, upper block:** outline x ±10, y −1.0 (column fronts) … +7.0, the leaning front-corner chamfers, z 0 → 9.2. Its
  lower front part (z < 4.4) is inside L. Its back face is full height.

| Face | Columns (x boundaries, studs) | Ridge / face y | Notes | Sheet evidence |
| --- | --- | --- | --- | --- |
| Lower front | **7**: −10.0 · −7.2 · −4.4 · −1.6 · +1.4 · +4.2 · +7.2 · +10.0 (the end columns' outer faces are the chamfers) | ridges y −7.1 … −7.3, faces −6.8 … −7.0 | each column a lit front / shaded left pair; creases 0.3–0.5 deep; top ring 0.4 behind the foot ring (batter) | front 7, f34 7–8 |
| Upper front | **6**: −8.0 · −5.4 · −2.7 · 0.0 · +2.7 · +5.4 · +8.0 at z 4.4 (→ ±7.4 at the top), plus the chamfer faces (each split into 2 tall facets) | ridges y −1.1 … −1.3, faces −0.8 … −1.0 | creases 0.3–0.5; batter 0.3 | front 6, f34 6 |
| Back | **7** shallow: −10.0 · −7.0 · −4.2 · −1.4 · +1.4 · +4.2 · +7.0 · +10.0 | y +7.0, creases inward ≤ 0.5 | **full height 0 → 9.2, no horizontal joint** | rear, r34 |
| Ends | planar on the seams (§2.1) | | rock behind the plate at +X | side cell |
| Bottom | flat at z 0; the outer ring bevels in 0.2 over the lowest 0.3 | | | close-up B |

- **Column faces:** each long face is split into 2–3 facets along its height (a vertex at 0.35–0.65 H pushed 0.1–0.2 in
  or out), so they are **tall strips (h / w 2.5–4.5)**. The tops are flat at 4.4 / 9.2 with a **0.3-wide pale bevel ring**
  (the thickness close-up's band: the top ring's front edge 0.3 lower and 0.25 back). Lower columns 40–56 tris each,
  upper 40–56, back 24–36.
- **Foot rocks** (separate closed shells, each sunk 0.1 into the ground):

| Rock | Centre (x, y) | Size W × D × H | Notes |
| --- | --- | --- | --- |
| FR1 pointed | (−2.6, −7.7) | 2.4 × 1.8 × 2.3 | leans 8–10° back into the C3 / C4 crease (sink 0.1–0.2 into the face); a sharp apex, 2–3 faces a side |
| FR2 small pale | (−5.9, −7.8) | 1.0 × 0.9 × 0.8 | flat-ish crown |
| FR3 small | (+1.2, −8.0) | 0.8 × 0.7 × 0.6 | |
| FR4 small | (+7.0, −7.9) | 0.7 × 0.7 × 0.6 | |

### 2.3 Shelf, cap, filler and dressing

| Piece | Position (x, y), base z | Size | Notes | Sheet evidence |
| --- | --- | --- | --- | --- |
| Lower shelf outline | front edge 0.1–0.3 proud of the lower ridges (y −7.2 … −7.6), y −6.1 at both seams; chamfer edges 0.15 proud; ends on x ±10 from y −6.1 to +1.0; back edge along the upper face foot (y −0.85, tucked 0.15) and the chamfer feet | 20 × 6.3 + two triangular pockets (2.0 × 2.0) | rim blocks 0.8–1.6 long along the front and chamfers; no rim at the back (hidden); recess 4.7 | front, f34, close-up A, thickness |
| Upper cap outline | front edge 0.1–0.3 proud of the upper ridges (y −1.2 … −1.6) between x ±7.4; chamfer edges 0.15 proud of the chamfer top line (±7.4, −1.0) → (±10, +1.0); ends on x ±10 from y +0.9 to +7.0; back on y +7.0 | 20 × 8.2 less the pockets | rim blocks along the front and chamfers, flat ends and back; recess 9.5 | front, f34, joining surfaces |
| **Corner filler** | in the **−X pocket**, centre (−9.0, 0.0); foot sunk 0.1 through the lower turf (z 5.5); leans 6–8° into the −X chamfer face (sink 0.1–0.3) | 2.2 × 2.0 × 3.5 (top facet sloping from 8.4 at the outer front to 9.0 at the inner back, under the cap edge 9.17) | 5-sided wedge, notch step on its front flank at about 7.2; x ≥ −9.95 | exploded "Corner Filler Rock"; front cell's dark sloping left end; WorldModeling §12.2 |
| UL1 dark bush | (−6.6, +5.0), 10.4 | Ø 1.9, 1.7 tall | brown trunk shows | top back-left |
| UL2 dark bush | (−4.4, +1.0), 10.4 | Ø 2.1, 1.8 tall | | front −5.2 … −3.2; top front-left; f34 front-left |
| UL3 dark bush | (+5.2, +5.4), 10.4 | Ø 2.2, 1.9 tall | the biggest | top back-right; f34 back-right; rear left |
| UL4 lime bush | (+6.8, +1.2), 10.4 | Ø 1.6, 1.3 tall | | front +5.1 … +6.9; top front-right |
| UL5 lime sprig | (+1.6, +5.8), 10.4 | Ø 1.1, 0.9 tall | | front +1.0 … +2.5; rear sprig |
| UL6 lime bush | (−6.4, +0.3), 10.4 | Ø 1.5, 1.2 tall | inside the chamfer line (x ≥ −8.7 at y 0) | front −6.9 … −5.4 |
| UB1 boulder | (−2.0, +1.6), 10.4 sunk 0.1 | 1.8 × 1.6 × 1.5 | rounded-angular, flat-ish crown | front −3.0 … −1.2; f34 |
| UB2 boulder | (+3.0, +5.6) | 1.5 × 1.3 × 1.2 | | top back-centre-right; rear +1.2 … +3.3 |
| UB3 small rock | (+4.6, +0.4) | 0.9 × 0.8 × 0.6 | | top front-right small |
| Upper pebbles | 8, 0.25–0.5 | | none within 0.4 of the front edge | top cell |
| LL1 dark bush | (−8.6, −3.0), 5.6 | Ø 1.9, 1.7 tall | | f34 lower-left |
| LL2 yellow-flowered bush | (−6.6, −2.2), 5.6 | Ø 1.6, 1.3 tall, 4 yellow petals | | f34; front −7.0 … −4.9 |
| LL3 small dark bush | (−0.6, −5.0), 5.6 | Ø 1.2, 1.0 tall | | f34 beside LB1 |
| LL4 dark bush | (+2.6, −1.9), 5.6 | Ø 2.0, 1.8 tall | touches the upper face | front +1.6 … +3.5 |
| LL5 lime bush | (+8.6, −0.4), 5.6 | Ø 1.8, 1.4 tall | in the +X pocket | front +7.2 … +9.1; f34 right |
| LS1–LS4 sprigs | (−2.0, −2.4) yellow; (+1.0, −4.2); (+4.8, −2.8); (−4.6, −5.6) yellow | Ø 0.8–1.0 | | front, f34 |
| LB1 boulder | (−2.9, −4.4), 5.6 sunk 0.1 | 1.8 × 1.5 × 1.4 | | front −3.6 … −1.9; f34 |
| LB2 small boulder | (+5.6, −4.6) | 1.2 × 1.0 × 0.9 | | front +5.0 … +6.0 |
| Lower pebbles | 6, 0.25–0.5 | | none within 0.4 of the front edge | |
| Apron | x −10.6 … −4.0, −2.0 … +3.0, +4.2 … +10.6; y −8.3 … −6.9 | 0.08–0.12 thick, jagged | tucked 0.1 under the face | f34, front foot |
| F1 dark bush | (−9.6, −7.6), 0 | Ø 1.8, 1.6 tall | overhang ≤ 0.6 | f34 left foot |
| F2 yellow-flowered clump | (−6.2, −7.7) | Ø 1.8, 1.0 tall | | front −7.5 … −4.8 |
| F3 sprig, F4, F5 bushes, F6 lime bush | (−0.5, −7.6) Ø 0.8; (+2.2, −7.7) Ø 1.2; (+5.1, −7.6) Ø 1.2; (+8.6, −7.6) Ø 1.5 | | | front foot |
| End sprigs | (−10.3, −3.0), (+10.3, −2.5) | Ø 0.7 | overhang ≤ 0.6, symmetric | front, side |
| Foot pebbles | 6 | 0.3–0.6 | | |

- **Keep clear:** nothing in the 1.0 strip behind the lower shelf's front edge taller than 1.0 except LL3 (the lawn line
  must read); no bush on the cap's chamfer edges; the dressing stays 0.3 inside each lawn's outline and inside x ±9.95
  (bush overhang aside).
- **Back:** nothing behind y +7.0 except the plate's back tabs (the back plane abuts terrain).

### 2.4 The connector plate

- **Plate:** x 9.6 … 10.0, y +1.8 … +7.0, z 0 … 10.05, both faces dead flat.
- **Front slots:** 3 rectangular slots cut 0.35 into the front edge at z 0.8–1.6, 3.0–3.8 and 6.4–7.2 (side cell's dark
  strips). Close-up C's single front tab is drawn as a slot here, so that the next tile's flat end isn't hit (§3.4).
- **Back tabs:** 3 tabs 0.35 proud behind y +7.0 at z 1.4–2.4, 4.8–5.8 and 8.0–9.0.
- **Top notch:** 0.4 (y) × 0.35 (z) at the front-top corner.
- Build it with M040's `plate_profile()` / `plate()` pattern (a CDT profile extruded in X), changing the slot direction.

### 2.5 Expected extents and screen checks

- **Extents (build frame):** X −10.6 … +10.6 (foliage; rock −10.0 … +10.0); Y −8.3 … +7.35 (apron in front; back tabs);
  Z 0 … 12.3 (UL3 top). Bbox ≈ 21.2 × 15.65 × 12.3.
- **Self-consistency (`proj5.py`, simplified block + dressing):**
  - `front_sheet (0, 16)`: W : H ≈ 1.37; lower lawn front edge h ≈ .37, upper face foot ≈ .47, upper front edge ≈ .77,
    upper back ≈ .91.
  - `f34_sheet (−15, 20)`: W : H ≈ 1.35; lawn rows .37 / .48 / .74 / .89.
  - `side (90, 8)`: W : H 1.02. `rear_sheet (180, 14)`: 1.61 (sheet 1.238, §3.4).
- **Checks on the renders** (floor hidden, `measure.py` masks):
  - **f34_sheet (−15, 20)** (probe az −8 / −15 / −22 × e 16 / 20 / 24, keep the best):
    - W : H 1.30–1.45 (sheet 1.375);
    - shares R 64.8 ± 4, G 34.8 ± 4 (L 23.6 ± 4, F 11.2 ± 3), D ≤ 1.5;
    - green fifths within ±7, the second fifth ≤ 12;
    - lower lawn front edge at h .36–.45 and upper at .72–.82 across f .45–.75;
    - lower lawn shows at **both ends** of the upper block (bush groups);
    - top profile within ±0.08 (mean ≤ 0.05) of §1.2.
  - **front_sheet (0, 16)** (probe e 12 / 16 / 20):
    - W : H 1.30–1.42 (sheet 1.359);
    - lower face foot full width, top 0.93–0.97 of it; upper face 0.78–0.82 of the lower foot at its foot, 0.72–0.76 at
      its top (sheet .80 / .74). The silhouette there stays full width (§3.2): record it;
    - lower lawn front edge h .37–.43, upper .76–.82;
    - shares R 72.0 ± 4, G 27.7 ± 4; green fifths within ±7, the second and fourth fifths ≤ 5;
    - 7 lower and 6 upper columns at the §2.2 x positions ±0.4.
  - **side (90, 8):** W : H 0.95–1.07 (sheet 0.995); plate 33–42 % of the silhouette over the back 0.36–0.40 of the
    depth, reaching the upper lawn line; the step profile (lower terrace in front, upper block behind); slots and tabs
    visible.
  - **rear_sheet (180, 14), r34_sheet (215, 20), top:** loosely (§3.3, §3.4): a full-height columnar back, the upper
    lawn and its bushes; top G ≥ 50 %.

## 3. View conflicts and resolutions

### 3.1 Proportions: front / f34 (wide) vs side (deep) vs rear / r34 (narrow) vs the 16-stud pitch

- **Evidence.**
  - At a 10.4 lawn, the front (1.359) and f34 (1.375) need about 20 wide (`proj3.py`: 20 × 14 → 1.34–1.44 and
    1.29–1.39; 16 × 14 → 1.12–1.17 and 1.15–1.19).
  - The side (0.995) needs D ≈ 14.
  - The rear (1.238) and r34 (1.146) are narrower: 16 × 14 gives 1.33 / 1.37 there; 20 gives 1.61 / 1.49.
  - The cells disagree with one another, as on 040 and 042.
- **Resolution (decision §8.1).** The hero f34 and the front cell govern: **20 × 14**. The rear and r34 are judged
  loosely (§3.4). **Alternative: 16 × 14** on M040's 16 pitch and the 32 grid. That would miss the governing W : H by
  0.17–0.22, the front-cell upper-face inset would become 1.6, and the lawns would read narrow.

### 3.2 The upper block narrower than the lower step (front, f34) vs a full-height plate on the +X end (side)

- **Evidence.**
  - Front cell: the upper face spans 0.80 of the lower foot at its foot and 0.74 at its top, centred. Lower lawn and
    bushes show at both ends.
  - f34: lower-lawn pockets at both ends.
  - Rear / r34: a low step at the +X back corner.
  - Side cell: the +X end's back 0.36–0.43 is a plate running from the ground to the upper lawn line, so the upper block
    reaches the +X end at the back.
- **Resolution (decision §8.2).** The upper block reaches the seams **only behind leaning front-corner chamfers** (c 2.0
  → 2.6, y −1.0 → +1.0). The chamfers make two lower-lawn **pockets** at the ends, which give the front cell's inset
  upper face and the f34's end bush groups. The planar ends behind them take the plate and tile cleanly.
  - **Known miss:** in a straight front view the upper block's back corners still fill the silhouette to ±10 at the
    upper heights. Width per height at h .65–.85 will be about 0.95–1.0 against the sheet's .74–.77. The face itself
    (between the creases) matches.
  - **Alternative:** the upper block inset 2.0 at both ends over its whole depth (a U-shaped lower lawn). That matches the
    front / f34 / rear silhouettes, but the plate then belongs to the lower step only (z ≤ 5.6, against the side cell),
    and the upper cliffs of a run stand apart with 4-stud gaps.
- **Taper of the ends** (front-cell silhouette .98 → .87 over the lower step): the seams must stay vertical, so the
  taper comes only from the leaning chamfers and a 0.3–0.4 batter on the column fronts. The silhouette stays full
  width: record the miss.

### 3.3 Top cell: one level, near-square (W : D 1.03)

- The top cell draws a single lawn over a front rim and no lower terrace. It is a re-composition (as on 040).
- **Resolution:** the plan is 20 × 14 with two levels. Use the top cell only for the upper lawn's dressing positions
  (fractions, §2.3) and the green share (≥ 50 % against 66 %). Its W : D and its missing step are known misses.

### 3.4 The back: rear / r34 (columns, two big leaning wedges, a low +X back step, no plate) vs side / exploded / close-up C (plate, flat back region)

- **Resolution (decision §8.3).**
  - **Flat back plane** at y +7.0 carrying seven full-height columns as **inward relief ≤ 0.5** (creases and strip
    facets), so the back still reads columnar. **No wedges** standing out behind the back plane, and no low step at the
    +X back corner: the plate is there.
  - The rear and r34 are judged loosely: a full-height columnar face, the upper lawn line, and bushes on top.
  - **Alternative:** the two wedges as shallow reliefs (≤ 0.5 proud of the creases, still inside y +7.0).
  - Close-up C's tab on the plate's front edge becomes a slot. A proud front tab would hit the neighbour's flat end
    (M040 put its front tabs into a groove for the same reason).

### 3.5 The Upper Ledge Cap's soil sides (exploded) vs rock rims (hero, thickness close-up, joining-surfaces close-up)

- **Evidence:** only the exploded cap shows orange-brown sides. Every assembled view shows pale rock (with a pale bevel
  band) under the lawn edge. The joining-surfaces close-up draws the cap's rim as rock lobes. D is 0.3–0.4 % of every
  hero view.
- **Resolution (decision §8.4):** **rock rims** on both shelf and cap (M040's lip). The Dirt / Soil swatch is used on
  trunks and soil specks only. Record the exploded cap's soil sides as a known miss (W02's brown line under the decks
  was the opposite reading). **Alternative:** a 0.15 soil line under the turf on the cap only (D +1–2 % in the f34).

### 3.6 The exploded body split vs the assembled body

- **Evidence:** the exploded draws a "Main Cliff Base" with a full-depth flat top, a separate tall left column with a
  lawn top, and a separate plain back block. Stacked as drawn they wouldn't make the assembled step.
- **Resolution:** the rock body is **one closed shell** (L ∪ U, §2.2), exported as `StoneTerraceBase`. The exploded's
  pieces are its columns. The shelf and cap are separate parts, as labelled. The flat joining faces (the lower body's
  flat tops under the shelf, the cap's flat underside) are kept.

### 3.7 Level heights: side 0.50 vs front 0.59 vs f34 0.62 (lower / upper)

- **Resolution:** lower lawn 5.6 (0.54). The front / f34 lower lawn line will sit about .02–.03 low on screen; record it.

### 3.8 "Simple bevels, no small details" against the user's blended-colour rule

- The user's rule wins quietly. Use broad position-based blends: lighter tops, the pale bevel band, a deeper foot,
  lawn patches. Use whole-facet Tint mottling at low amplitude, never per-triangle confetti. The sheet's peach-lit /
  blue-shade split is the light (§5.3).

### 3.9 Palette names against the renders

- "Rock (Shadow)" `#828779` is a **greenish** grey (81°, G > R > B). The rendered shade faces are blue-lavender (236°).
  Neither is paint.
- "Rock (Main)" `#C2B3AD` (17°, R − B 21) is paler and pinker than the rendered warm faces (`#D7B09C`, 20°, R − B 59).
- Calibrate to the rendered regions (§5.4).

### 3.10 Cast shadow

- The sheet's ground shadows are faint near-white (B, background). Render every `*_sheet` view with the studio floor
  hidden (M034 §2.6).

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

**Reuse M040.** `m040.py` (untracked at the time of writing) already has the palisade loft (`body_rings`, `palisade`),
the lip slab (`lip_outline`, `lip_slab`, `_cdt`, `_cap`), the plants (`_leaf`, `bush`, `sprig`, `pebble`, `lawn_rock`,
`apron`), the plate (`plate_profile`, `plate`), the seam snap (`_snap_seams`), the shell / contact / capping / seam reports
and `measure()`.
- If `m040` is committed when this model starts, import it, as `m040` imports `m011` / `m012` / `m016` / `m033`.
- If not, copy what you need into `m043.py`.
- Don't edit `m040.py`.

1. `body()` → **`StoneTerraceBase`** (Main Cliff Base):
   - L and U as explicit lofted column prisms (§2.2), unioned with a merge-0 exact union at the world origin (STAGES
     "Booleans"; `m021._union_fine`), then the foot rocks one at a time, floor-cut at z 0, `_snap_seams`.
   - One closed shell.
   - Compare with the exploded base and the left column: tall strip facets, flat level tops, the pale bevel ring.
   - Add a **bottom extra** (e −35) against close-up B: one flat bottom ≥ 0.4 of the visible underside, the lobes
     bevelling up.
2. `shelf(level)` with `level` in `"lower" | "upper"`:
   - one closed slab: turf, rim ring and recess, M040 `lip_slab` style, outline from §2.3;
   - plus that level's dressing (`lawn(level)`).
   - Parts **`StoneTerraceLowerShelf`** and **`StoneTerraceUpperCap`**.
   - Compare the cap with the exploded cap and with a **cap-underside extra** (the cap part from below, e −30) against the
     joining-surfaces close-up: one flat face ≥ 0.45 of the visible underside, rim lobes round it.
3. `filler()` → **`StoneTerraceCornerFiller`**:
   - a 5-sided wedge prism: an explicit base ring, a mid ring with the notch step, a sloping top facet;
   - 30–50 tris, broad faces.
   - Compare with the exploded filler: w/h 0.6–0.75, the sloping top, the notch.
4. `connector()` → **`StoneTerraceSideConnector`**: §2.4, authored in place on the +X end. Compare with the exploded plate
   and close-up C (slots, tabs, notch).
5. **Hero `StoneTerrace`** = body + lower shelf + upper cap + filler + plate + all dressing.
   - Each piece is its own closed shell in one object; no booleans between pieces.
   - `M.fix_bowties`; origin at the bbox bottom centre; transforms applied.
6. **Parts shot** (az −20, e 25), laid out like the exploded:
   - the cap above the shelf above the base;
   - the plate to the left, turned to the viewer;
   - the filler to the right.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a broad block of pale warm columns stepping up in two flat lime terraces; the lower lawn wraps the
   upper block's front corners; round dark / lime / yellow-flowered bushes on both lawns; a lime apron and a pointed foot
   rock; a grey plate on the right end in the side view.
2. **f34_sheet and front_sheet** per §2.5.
3. **side** per §2.5; **rear_sheet, r34_sheet, top** loosely.
4. **Rock-shape targets** (§4.4), on the Base part and the hero.
5. **Capping** (§6): the numbers below. Then a **junction extra** `junc_cu (−35, 12)`, framed on the lower lawn against
   the upper face at x ≈ −3, against close-up A: a clean vertical joint, the lawn running to the face, no gap. Then a
   **thickness extra** `thick_cu (−20, 22)` on the lower shelf's front edge at x ≈ +3: the lawn edge, the pale bevel band,
   the tall faces.
6. **Connector extra** `conn_cu (60, 15)` on the +X end against close-up C.
7. **Tiling shot:** three hero copies at x −20 / 0 / +20, from `front34` and from straight above:
   - no gap and no rock overlap;
   - the shelves and caps flush and level (5.6 / 10.4);
   - the end pockets meeting as V bays of lower lawn;
   - the plates hidden in the joints.
   - If M040 is in the kit file, add one M040 tile at the +X end with the back planes aligned (§2.1).
8. **Hero size** per §1.1 / §2.5; **scale shot** beside a 5.5-stud character marker on the ground, one on the lower lawn
   and one on the upper lawn.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Body: lower columns, upper columns, back relief, ends, chamfers, floor | 1 shell | — | 700–880 |
| Foot rocks FR1–FR4 | 4 | 16–36 | 80–110 |
| Lower shelf slab (turf CDT + rim + recess) | 1 | 260–340 | 260–340 |
| Upper cap slab | 1 | 300–380 | 300–380 |
| Corner filler | 1 | 30–50 | 30–50 |
| Connector (plate + 3 slots + 3 tabs + notch) | 1 | 80–110 | 80–110 |
| Lawn boulders UB1–UB3, LB1–LB2 | 5 | 16–30 | 100–140 |
| Dark bushes (8–10 leaves × 8–10 + trunk 8) | 7 (UL1–3, LL1, LL3, LL4, F1) | 70–110 | 500–700 |
| Lime / yellow-flowered bushes | 7 (UL4, UL6, LL2, LL5, F2, F6, F4) | 50–90 | 350–560 |
| Sprigs | 8 (UL5, LS1–4, F3, end ×2) | 24–40 | 190–320 |
| Pebbles | 20 | 6–10 | 120–200 |
| Apron patches | 3 | 16–30 | 50–90 |
| **Hero** | | | **about 2800–3900**, plan ≈ 3400 (limit 4000) |
| Parts: Base / LowerShelf / UpperCap / CornerFiller / SideConnector | | | 780–990 / 850–990 / 880–990 / 30–50 / 80–110 (limit 1000) |

- **The part limits are tight.** If a part is over 950, tag dressing `on="hero"`, as M040 did: on the shelf LS4 and two
  pebbles; on the cap UL5 and two pebbles. Never thin the slabs or the columns.
- **If the hero is over 3900:** drop hidden back leaves, then pebbles (to 14), then sprigs (to 6). Never thin a column
  below §4.4, and never drop a bush that the f34 or front shows.

### 4.4 Rock-shape targets (binding; check with `M.audit`, own bmesh code and M040's `rock_metrics`)

| Target | Lower / upper columns | Back relief | Foot rocks | Lawn boulders | Filler | Rims |
| --- | --- | --- | --- | --- | --- | --- |
| Sides | 6–7 (back corners in the core) | strips | 4–5 + apex (FR1) / 5–6 | 5–6 | 5 + sloping top | blocks 0.8–1.6 long |
| Facets visible from the front | 3–6 per column | 2–3 per column | 2–3 a side | 4–6 | 3–4 | 1–2 per block |
| Facet shape | **tall strips h/w 2.5–4.5** (5 biggest) | strips | long triangles to the apex | broad, h/w 0.8–2 | broad | blocky |
| Top | **flat at 4.4 / 9.2, entirely under the shelf / cap** (except the ≤ 0.3 bevel) | under the cap | apex / flat-ish | flat-ish crown ≥ 25 % of plan | sloping facet ≥ 30 % of plan | flat under the turf |
| Side faces within 20° of vertical | ≥ 85 % of side area | ≥ 90 % | ≥ 60 % | ≥ 40 % | ≥ 70 % | ≥ 80 % |
| Narrowest face | ≥ 0.8 wide, ≥ 2.0 tall | — | — | — | ≥ 0.6 | — |

- **Irregular, not a pattern:** triangle area CV ≥ 0.6 on the body. No vertex ringed by 5–6 near-equal triangles. Never
  `primitive_ico_sphere`, subdivision, displacement or `K.hull_rock` jitter balls (egg boulders, M034 / M037).

### 4.5 Stages 2 and 3

- **Stage 2:** every shell closed and manifold; zero non-manifold edges and verts (`nonmanifold_verts` 0), boundary,
  wire and loose elements; no zero-area faces or n-gons; normals outward; no corners under 5° on visible faces
  (`m011._tidy` / `_desliver`); seam faces exactly planar (all verts on x = ±10.0 ± 0.001 on the body ends, shelf ends
  and cap ends).
- **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 28 × 26 box inside each, sd ≤ 1.5)

| Swatch | Box | Hex | HSV | Channel order | Use |
| --- | --- | --- | --- | --- | --- |
| Rock (Main) | (29,266,57,292) | `#C2B3AD` | 17°, 0.11, 0.76 | R > G > B, R − B 21 (pink-grey) | hue reference only; too pale and pink for a key |
| Rock (Shadow) | (29,307,57,333) | `#828779` | **81°**, 0.10, 0.53 | **G > R > B** (greenish) | **never a key** (light) |
| Grass / Foliage | (29,349,57,374) | `#B8CD28` | 68°, 0.80, 0.80 | G > R > B | start for `grass` |
| Dirt / Soil | (29,390,57,415) | `#AC754C` | 26°, 0.56, 0.67 | R > G > B | start for `trunk` |

### 5.2 Rendered regions (`samp.py`, `samp2.py`; median / lit quartile / shade quartile)

| Region | Median | Lit | Shade |
| --- | --- | --- | --- |
| Rock, all: f34 / front / rear / r34 / side | `#C1A393` / `#BB9E92` / `#B09992` / `#837D89` / `#A18F8C` | `#EAC6AE` / `#ECC4A9` / `#E9C0A4` / `#E0BDA8` / `#BDA191` | `#73717E` / `#696D7B` / `#716E79` / `#6A6873` / `#636776` |
| Rock warm faces (h ≤ 60): f34 / front / rear / r34 / exploded / close-up A | **`#D7B09C`** (20°, .27, .84) / `#D4AE98` / `#D0AE9D` / `#D5B2A0` / **`#C7A89B`** (18°, .22, .78) / `#DFB59A` | `#F3D3B8` / `#EFCAAF` / `#EFC9AD` / `#EECEB6` / `#E4C4AB` / `#FBDABB` | `#AE9386` / `#AE9287` / `#AC948E` / `#B0958D` / `#9F8B86` / `#B89A8C` |
| Warm share of rock: f34 / front / rear / r34 / exploded | 67.7 / 67.0 / 59.9 / 41.5 / 59.8 % | | |
| Rock cool faces (the shade light): f34 / front | `#767785` (236°) / `#6D7181` (228°) | | |
| Warm rock thirds (bottom → middle → top): f34 / front / rear / r34 / top | `#CEAC9A` → `#DDB59B` → `#D6B09E`; `#D0AC9A` → `#D1AA93` → `#DDB8A0`; `#CBA997` → `#CFAE9D` → `#E4BDA3`; `#D1B09E` → `#D6B19F` → `#E8CBB2`; `#D0AE99` → `#E0BFA3` → `#E7C5AE` | | |
| Pale bevel band under the turf (thickness close-up lit) | `#FBD2AA` (30°, .32, .98) | | |
| Flat undersides (cap underside / body bottom, in shade) | `#8E7F7C` (10°, .13) / `#8C7D7A` | | |
| Lawn: f34 / front / rear / r34 / top / exploded / thickness | `#D7E10F` (63°, .93, .88) / `#D6DE0B` / `#D0DA0E` / `#CDDC11` / `#BCD11B` (67°) / `#C9D914` / `#D3DD05` | `#E0E916` / `#E6EA0A` / `#E3EA0A` / `#DCE60B` / `#C6D715` / `#D3E218` / `#DDE804` | `#B6C70B` / `#B0C010` / `#ADB817` / `#AFBF0B` / `#B4C614` / `#9BB30E` / `#AAC008` |
| Lawn by band (f34): upper / lower / foot | `#D3DF0F` / `#DBE413` / `#D2DA07` (one lawn colour on all three) | | |
| Bush foliage (F), all cells | `#4D7E19`–`#547F1A` (86–89°, .75–.83, .48–.51) | `#7DB831`–`#83B22D` | `#274C0B`–`#2C480C` |
| Dark-bush leaves (h ≥ 95) / mid (80–95) | `#257224` (119°, .68, .45) / `#5C9016` (86°, .85, .56) | | |
| Lime bush leaves (probes) | `#A8B509`–`#B0D004` (65–69°, .95–.98) | `#D0D205` | `#82B401` |
| Yellow flowers: f34 / front / rear / top | `#E1D226` (55°, .83, .88) / `#E2D32E` / `#DCC936` / `#D5C63F` (0.6–1.7 % of each view) | | |
| Trunks (D), f34 / r34 / top | `#6E330B` (24°, .90, .43) / `#662C0A` / `#72340F` | | |
| Exploded cap soil sides (D, exploded) | `#D29766` (27°, .51, .82) | `#E2A66F` | `#93704C` |
| Connector plate: side / close-up C | `#9C908F` (5°, .08, .61) / `#9B8F8E` | `#9F9391` | `#988D8D` |

### 5.3 How the colour works

**Rock.**
- **One pale warm peach stone** for the columns, chamfers, back, ends, rims, filler, boulders and pebbles. Warm faces
  are hue 18–24°, sat 0.22–0.28, **always R > G > B**.
- The sheet's shade faces are blue-lavender (228–250°): that is the fill light. Our studio's shade is warm grey; that is
  light, not paint. **Never colour by facing.**
- It is the **same stone as M040** (M040's warm faces `#D4B29D` f34 / `#C9AB9B` exploded; here `#D7B09C` / `#C7A89B`),
  so a run of 040 and 043 tiles must read as one rock.
- **Painted signals by position:**
  - the upper third of each face renders a step lighter (thirds above);
  - the **pale bevel band** at every column top under the turf is lightest (`#FBD2AA` lit);
  - the lowest 1.5 studs are a touch deeper;
  - the lower step's top ring just under the lower shelf is lighter, like the upper's.
- Whole facets only, by height plus a broad noise field. **No dark foot band, no moss streaks, no green on the cliff
  bands** (front second and fourth green fifths 0.8 / 3.1 %).
- **Mauve guard (M031, M032 rounds 1–2, M040):** every rock key R > G > B, hue 15–26°, R − B ≥ 30. Rock (Main)
  `#C2B3AD` (R − B 21) is a hue reference only; Rock (Shadow) `#828779` and the blue shade are never keys, not even in a
  mix.

**Lawn.**
- One bright yellow-lime (62–67°, sat ≥ 0.88) on both levels and the apron (the bands agree within 8 levels).
- Lighter broad patches. Slightly deeper lime near bush roots and boulders, and within 0.6 of the upper face's foot on
  the lower lawn (by position: the sheet shows that strip a step darker in the f34 and front).

**Bushes.** Three plant types, chosen per plant, never per face:
- **dark-green round bushes:** leaves 86–119° from lit to shade, median about 88°; lit leaves `#7DB831`, inner / lower
  leaves deep `#257224`; brown trunks;
- **lime bushes and sprigs:** 65–69°, sat ≥ 0.95;
- **yellow-flowered bushes:** lime leaves plus 3–5 broad yellow petals (55°).

Keep the dark bushes yellower than M040's (88° against 107–113°): measured, not copied.

**Connector.** A flat warm grey (`#9C908F`, sat ≤ 0.09, R ≥ G ≥ B), smoother than the rock, a faint Tint only.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are medians of unshadowed rendered regions (warm faces, lit lawns, bush medians), not swatches.
`K.sample` kinds: `"all"` for rock (M040's override: the stone filter drops sat > 0.18), `"green"` for lawn and leaves,
`"vivid"` for lime / yellow, `"brown"` for the trunk, `"stone"` for the connector. **Start from M040's calibrated
hexes** where the family matches (rock `#A3938B`, rock_light `#AD9E95`, rock_deep `#92837C`, grass `#9DAF06`,
grass_light `#B0BA12`, grass_deep `#879C02`, lime `#89A203`, trunk `#502401`), then re-calibrate to these targets.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m043_rock` | **`#CFAD9B`** (warm faces: exploded `#C7A89B`, f34 `#D7B09C`, front `#D4AE98`, rear `#D0AE9D`) | 18–24°, 0.20–0.27, R > G > B, R − B ≥ 30 | all rock, default | rough 0.9, metal 0 |
| `m043_rock_light` | `#E2C3AC` (exploded lit `#E4C4AB`; top thirds about +15 over `rock`) | 20–27°, 0.20–0.30 | upper 30 % of every column at 30–40 %; the **bevel band** at 60 %; rims at 45 %; filler crown; boulder crowns; pebbles | rough 0.9 |
| `m043_rock_deep` | `#BA9C8C` (a step below `rock`, hue kept warm; lower thirds) | 18–24°, 0.22–0.28 | below 1.5 studs at 15 %; the back face's lower half at 10 %; the flat bottom and the cap recess (hidden) | rough 0.9 |
| `m043_grass` | **`#CEDB12`** (f34 `#D7E10F`, front `#D6DE0B`, top `#BCD11B`, exploded `#C9D914`) | 62–67°, ≥ 0.88, G > R > B | both lawns, apron, default | rough 0.85, low spec |
| `m043_grass_light` | `#DEE718` (lit `#E0E916`, `#E3EA0A`) | 60–64°, ≥ 0.85 | broad lawn patches at 20 % | rough 0.85, low spec |
| `m043_grass_deep` | `#B0C10B` (shade `#B6C70B`, `#B0C010`) | 64–68°, ≥ 0.90 | within 0.8 of bush roots and boulders; within 0.6 of the upper face's foot; the apron's inner edge; at 25–30 % | rough 0.85, low spec |
| `m043_leaf` | `#4F801A` (bush F medians `#4D7E19`–`#547F1A`) | 85–92°, 0.75–0.85, value ≥ 0.47 | dark bushes, middle leaves | rough 0.85, low spec |
| `m043_leaf_lit` | `#7DB831` (lit `#7DB831`–`#83B22D`) | 82–88°, 0.70–0.78 | dark bushes' top tier at 40 % | rough 0.85, low spec |
| `m043_leaf_deep` | `#2A6A20` (h ≥ 95 `#257224`, lifted a step) | 105–120°, ≥ 0.68 | dark bushes' lower / inner leaves at 40 % | rough 0.85, low spec |
| `m043_leaf_lime` | `#AAC305` (lime leaves `#A8B509`–`#B0D004`) | 65–70°, ≥ 0.95 | lime bushes, sprigs, the yellow bushes' leaves | rough 0.85, low spec |
| `m043_flower` | `#E0CF2C` (`#E1D226`, `#E2D32E`, `#DCC936`) | 53–57°, ≥ 0.75, R > G ≫ B | yellow petals and buds | rough 0.8, low spec |
| `m043_trunk` | `#6A3210` (trunks `#6E330B`, `#662C0A`; swatch Dirt `#AC754C`) | 20–28°, 0.80–0.90 | trunks, bush hearts, soil specks at roots | rough 0.95 |
| `m043_connector` | `#9C908F` (side and close-up C) | 0–12°, sat ≤ 0.09, R ≥ G ≥ B | plate, slots, tabs | rough 0.7, metal 0 |

**Calibration warnings:**
- **Rock:** calibrate `m043_rock` on the parts shot's Base (warm faces) against `#CFAD9B`. Then check:
  - f34_sheet warm-face median within 10 of `#D7B09C`; front_sheet within 10 of `#D4AE98`; R > G > B, hue 15–25°;
  - the whole-rock medians against `#C1A393` (f34) / `#BB9E92` (front). Ours will run warmer because our shade is warm,
    not blue (M032 round 2, M040 §5.4). A median within hue 15–25° that misses by ≤ 15 levels is a known miss, not a key
    error. Never push the shade faces blue by facing.
- **Lawn:** f34 lawn within 14 of `#D7E10F`, top within 12 of `#BCD11B`; hue 62–67°, sat ≥ 0.88. "Greens slightly
  grey" (M038) is the miss to avoid: if the lawn reads olive, raise the saturation.
- **Leaves:** dark-bush F median within 14 of `#4D7E19`, hue 84–94°. Lime leaves within 14 of `#ABC306`, hue 64–70°. Keep
  the lime and dark types ≥ 18° apart. "Lit foliage dark and less lime" (M035) and "back greens dark" (M036) are the
  misses to avoid.
- **Flowers:** within 14 of `#E1D226`, hue 53–57°: yellow, not lime and not orange.
- **Connector:** within 8 of `#9C908F`, sat ≤ 0.09. It must read grey beside the warm rock, not lilac (R − B ≤ 16).

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Rock** (on the original facets, before any refine):
  - `rock` is the base;
  - `rock_light` by height within each face band (faces with centre z above 0.65 of their band's top, rising to 40 % at
    the top), and **on the bevel band at 60 %**, the rims at 45 %;
  - `rock_deep` by a noise field (scale ≈ 0.2) below 1.5 studs (15 %);
  - per-column and per-boulder tint ±0.04 so neighbours separate.
- **Lawn:**
  - `grass` is the base;
  - `grass_light` by a noise field (scale ≈ 0.25) at 20 %;
  - `grass_deep` by distance (to bush roots and boulders < 0.8; to the upper face's foot < 0.6) at 25–30 %.
  - Average with neighbours before quantising (M034: no triangle shards).
- **Leaves:**
  - dark bushes by role in the bush: top tier `leaf_lit` 40 %, middle `leaf`, lower / inner `leaf_deep` 40 %;
  - lime bushes `leaf_lime` with ±0.04 tint per plant;
  - petals `flower`.
- **Hard edges only** where materials meet: lawn | rim (the turf edge), leaf | trunk, petal | leaf, rock | connector
  (separate shells).

### 5.6 Texture (Tint) and finish

- **Tint:**
  - rock amp 0.04, scale 0.3, per original facet (a refined facet keeps one tone);
  - lawn 0.04, scale 0.4;
  - leaves 0.04 per leaf; petals 0.02;
  - connector 0.02; trunks none.
  - Never per-triangle confetti.
- **Finish:**
  - rock rough 0.9, metal 0;
  - lawn and leaves `low_spec=True`, rough 0.85; petals rough 0.8;
  - connector rough 0.7; trunk 0.95.
  - No emission anywhere.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Rock:** f34_sheet and front_sheet warm-face medians within 10 of `#D7B09C` / `#D4AE98`; whole-rock medians recorded
  against `#C1A393` / `#BB9E92`; parts-shot Base warm median within 10 of `#CFAD9B`. All R > G > B, hue 15–25°. Check the
  side and rear too (mauve guard).
- **Lawn / leaves / flowers / connector:** per the §5.4 warnings. **Shares** per §2.5. **No green** in the cliff bands
  (front second and fourth fifths ≤ 5 %).

## 6. Joins and contact (no floating dressing)

- **Body:** L ∪ U one closed shell. The foot rocks are separate closed shells, sunk 0.1 into the ground and leaning
  0.1–0.2 into the face; no rock stands on a point.
- **Shelf on the lower step:** the rim's bottom at 4.37 sits on the lower column tops (sink 0.03, never coplanar). The
  outline covers every lower column top from the front ridge line to the upper face. Its back edge tucks 0.15 into the
  upper face's columns, so there is **no crack between lawn and face** (close-up A).
- **Cap on the upper block:** the rim's bottom at 9.17 on the upper column tops; the outline covers every upper top. The
  front rim is 0.1–0.3 proud of the column ridges.
- **Capping numbers (M032 round 1, the blocker; M040 §2.5).** Column faces with n.z > 0.5 that are visible from above
  (not under a slab) must total **0 studs²**, apart from the bevel band, which is ≤ 0.3 wide and ≤ 0.3 below the turf
  edge. Rock visible from straight above inside the tile:

  | Source | Allowed area (studs²) |
  | --- | --- |
  | Bevel band strips | ≤ 0.3 wide |
  | Lawn boulders, pebbles, foot rocks, filler top | — |
  | **Total** | ≤ 30 |

  Lawn visible from straight above ≥ 220 studs² (lower about 135, upper about 150, less the bushes).
- **Filler:** its foot is 0.1 through the lower turf, into the shelf (contact with the shelf slab); it leans 0.1–0.3
  into the −X chamfer face; its top stays under the cap's edge (8.4–9.0 < 9.17).
- **Plate:** its outer face is exactly on x = 10.0 and its inner face at 9.6. The core steps in behind the groove (§2.1).
  Back tabs stand 0.35 behind the back plane; front slots are cut into the plate only.
- **Plants:**
  - roots on the turf (z 5.6 / 10.4, sink 0.03) or the ground;
  - every leaf within 0.03 of its hub or trunk and chained by contact to the turf (STAGES: no hidden stems);
  - every petal on its bush's top leaves;
  - leaves may touch rock but cut no more than 0.05 into it.
- **Count floating shells before reporting** (STAGES; 035 and 036 failed round 1 on this): **0**. A shell floats if its
  nearest distance to every other shell and the ground is > 0.03, or if it doesn't chain to the ground.
- **Seams:**
  - every rock and plate vertex within x −10.0 … +10.0;
  - body, shelf and cap end faces planar on the seam planes (§2.1);
  - foliage overhang symmetric, ≤ 0.6.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0 (bush hubs and petal centres).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** sunlit rock, lawns, bushes and flowers, and a grey plate. No glow, light, sparkle, water, dust,
particles or VFX callout.
- **Stage 5 (lighting): skip, and record why.** No emissive faces, no PointLight. Studio notes (Requires Manual
  Validation):
  - the rock stays warm peach (not lilac) under the game's sun and matches an adjacent M040 tile;
  - the column facets read as separate planes (flat shading kept);
  - both lawns stay yellow-lime;
  - the yellow flowers read yellow;
  - the plate reads neutral grey;
  - a run of three tiles shows no seam gap or lawn step at the 20-stud pitch;
  - **a character can jump ground → lower lawn → upper lawn** with the game's jump settings.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** Not recommended: dust at the foot, pollen or butterfly
  motes over the flowers, falling pebbles.
- **Collision:** hero `precise` (both lawns walkable, the faces block); `StoneTerraceBase` `precise` (a hull would fill
  the step); `StoneTerraceLowerShelf` and `StoneTerraceUpperCap` `precise`; `StoneTerraceCornerFiller` `hull`;
  `StoneTerraceSideConnector` `box`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by searching `art/blender/kit/mcp/*.py`, `art/blender/scripts`, every
`art/roblox/kit/*/manifest.json`, the repo text (`git grep`) and every sheet / kit / wip `.blend` (zstd-decompressed)
with `blendall.py`:
- **W02** owns `TerracedLedge`, `TerracedLedgeBase`, `TerracedLedgeCornerFiller`, `TerracedLedgeLowerShelf`,
  `TerracedLedgeUpperCap`, `TerracedLedgeRampEnd`, `TerracedLedgeShallow` and `TerracedLedgeWide`. It also owns
  `CliffWall*` (incl. `CliffWallBackConnector`), `WaterfallCliff*` and `CliffSection`. `TerracedLedge` occurs in
  `FlintbornWorldKit.blend` and every wip copy. Keys are `w02_*`.
- **The cave kit** owns `CaveLedge`, `CaveLedgeCornerFiller`, `CaveLedgePlatformSlab`, `CaveLedgeWall`,
  `CaveLedgeBackWallPanel` and others.
- **M040** owns `StoneCliff`, `StoneCliffBody`, `StoneCliffGrassLip` and `StoneCliffBackConnector`, with keys `m040_*`
  (in `M040.blend`).
- **`StoneTerrace`, `TerraceStep`, `StepLedge`, `TwinLedge` and `m043_` occur nowhere** in the repo text, the manifests
  or any `.blend`. (`m043` appears only as bytes inside `references/160.png`.) `M.mk` would silently rename a clash to
  `<name>M043`; the names below don't clash.

| Object | Part | Why |
| --- | --- | --- |
| `StoneTerrace` | hero: body + shelf + cap + filler + plate + dressing | W02 owns `TerracedLedge`; parallels M040's `StoneCliff` and M039's `StoneSpire` |
| `StoneTerraceBase` | "Main Cliff Base": the stepped rock body with the foot rocks | |
| `StoneTerraceLowerShelf` | "Lower Ledge Shelf": slab + rim + lower-lawn dressing | |
| `StoneTerraceUpperCap` | "Upper Ledge Cap": slab + rim + upper-lawn dressing | |
| `StoneTerraceCornerFiller` | "Corner Filler Rock" | |
| `StoneTerraceSideConnector` | "Side Connector (Flat Back)": plate + slots + tabs | |

- Palette keys `m043_*` (§5.4). Collection `Kit/M043 Terraced Ledge`. No sockets.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1, §3.1): **20 × 14, lower lawn 5.6, upper lawn 10.4** (recommended).
   - Why: it matches the governing f34 / front W : H and the side's depth; it meets the 10.4 plateau; both rises are
     jumpable; the upper block is M040's depth.
   - Or **16 × 14** at the same levels (M040's pitch and the 32 grid; −0.2 W : H against the hero, narrow lawns).
   - Or a 5.2 / 10.4 split (the side cell's 0.50; rises 5.2 / 5.2).
2. **Upper block plan** (§3.2): **reaches the seams behind leaning 2.0 → 2.6 front-corner chamfers, forming lower-lawn
   pockets at both ends** (recommended: front-cell inset, f34 end groups, the side cell's full-height plate, clean
   tiling). Or inset at both ends over its whole depth (better silhouettes; the plate drops to the lower step and runs
   break into buttresses).
3. **Back** (§3.4): **a flat back plane with seven full-height columns as relief ≤ 0.5, no wedges, no low back step;
   rear and r34 judged loosely** (recommended). Or the two wedges as shallow reliefs.
4. **Rims** (§3.5): **pale rock rims with a pale bevel band, no dirt band** (recommended). Or a 0.15 soil line under the
   cap's turf (the exploded).
5. **Packaging** (§6):
   - **one hero object of closed shells:** the body (L ∪ U plus the foot-rock unions, or the foot rocks as their own
     shells), the shelf, the cap, the filler, the plate, and each leaf, petal, trunk, boulder, pebble and apron patch;
   - **five parts as the exploded labels** (recommended).
   - Or the body as two shells (base + upper block, no union). That would put a joint line on the back.
6. **Corner filler** (§2.3): **one, in the −X end pocket on the lower lawn, leaning into the chamfer, top under the cap**
   (recommended: WorldModeling's "corner filler"; the front cell's sloping left end). Or a free-standing end-cap rock at
   the −X front foot.
7. **Connector** (§2.4): **+X end only, 5.2 deep (y +1.8 … +7.0), 0 → 10.05, 3 front slots, 3 back tabs, top notch**
   (recommended: the side cell's 0.36–0.43 of the depth; it fits inside M040's flat −X end). Or M040's exact plate (3.9
   deep, front tabs into a groove).
8. **Reuse of M040's code** (§4.1): **import `m040` if it is committed by then, else copy the helpers into `m043.py`**
   (recommended).
9. **Comparison cameras** (§2.5):
   - `f34_sheet (−15, 20)` governing (probe az −8 / −15 / −22 × e 16 / 20 / 24);
   - `front_sheet (0, 16)` (probe 12 / 16 / 20), `side (90, 8)`;
   - `rear_sheet (180, 14)`, `r34_sheet (215, 20)` (from the back-left; flip to 145 if the render shows the +X end on the
     right) and the kit top, all loosely;
   - extras: parts shot (−20, 25), cap underside (e −30), body bottom (e −35), `junc_cu (−35, 12)`, `thick_cu (−20, 22)`,
     `conn_cu (60, 15)`, the three-tile tiling shot (plus an M040 joint if available) and a scale shot with three 5.5-stud
     markers.
   - Hide the floor in every `*_sheet` render.
10. **Colour** (§5):
    - one warm peach stone `#CFAD9B` (R > G > B, hue 18–24°, the same family as M040), lighter high and on the bevel band,
      a touch deeper low;
    - one yellow-lime lawn `#CEDB12` with patches;
    - dark bushes `#4F801A`, lime `#AAC305`, yellow petals `#E0CF2C`, brown trunks `#6A3210`;
    - a warm-grey plate `#9C908F`
    (recommended). Never the Rock (Shadow) swatch, nothing by facing.
11. **Stages 5 and 6:** **skip both, recorded** (recommended).
12. **Collision** as in §7 (recommended).
13. **Budget** (§4.3): **4000 limit, plan about 3400, parts under 1000 with hero-only tags as needed** (recommended).
14. **Names** as proposed.

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **Turf that doesn't cap what it sits on (M032 round 1, the blocker).**
   - The lower shelf covers every lower column top from the front ridge line to the upper face, and tucks 0.15 into the
     upper face.
   - The cap covers every upper column top.
   - 0 studs² of exposed column top beyond the ≤ 0.3 bevel band (§6 numbers).
   - No lawn strip floating between bare column tops; no grey "necklace" from above.
2. **Floating dressing (STAGES; 035 and 036 round 1).** Every leaf, petal, pebble and boulder within 0.03 of a
   neighbour, its turf or the ground, chaining to the ground. Count floating shells: **0**. Petals sit on their leaves;
   the filler and boulders are sunk.
3. **Spiky or ladder foliage (M039 round 1 blocker; M036 rounds 1–2).**
   - Bush leaves are broad rounded ovals with blunt two-corner tips (tip angle ≥ 110°) and a camber ≤ 0.07 L, seated in
     round clumps by contact.
   - The yellow petals are broad and rounded.
   - No kite or diamond leaves, no pointed shards, no ivy curtains hanging down the faces.
4. **Mauve or blue rock (M031, M032 rounds 1–2, M040 §5.3).** Every rock key R > G > B, hue 15–26°, R − B ≥ 30, in every
   view including side and rear. Rock (Main) `#C2B3AD` (R − B 21) and Rock (Shadow) `#828779` are references only.
5. **Colour by facing.** The peach-lit / blue-shade split is the light. Height fields, noise patches, distances and roles
   only; `K.check` facing correlation < 0.5 per material.
6. **Egg boulders (M034 round 1; M037 "rock parts egg-shaped").** Lawn boulders and foot rocks are rounded-angular with
   a flat-ish crown and broad facets; FR1 is pointed; the filler is a wedge. No ico-spheres, no `hull_rock` jitter balls.
7. **Lumpy columns or soccer-ball facets (M023, W02 "low smooth cliffs").** Columns are explicit 6–7-sided prisms with
   tall strip facets (h/w 2.5–4.5), level flat tops and dark full-height creases. No subdivision, no smooth shading.
8. **Two stacked boxes.** The read is two palisades of columns:
   - creases 0.3–0.5 deep;
   - batter 0.3–0.4;
   - leaning end chamfers;
   - the bevel band;
   - an irregular front (ridges ±0.25).
   The levels must still be flat and level (lawn lines .40 / .80 in the front cell).
9. **A dirt band under the turf (W02; the exploded cap).** Rims are rock; brown only on trunks and a few root specks
   (D ≤ 1.5 % in the f34).
10. **Green on the cliff bands.** No moss streaks or vines on either face. Front green fifths 2 and 4 ≤ 5 %.
11. **Seams that don't tile.**
    - Seam faces planar at x = ±10.0 ± 0.001;
    - lawns at exactly 5.6 / 10.4 at both seams;
    - the plate on the +X end only;
    - no rock past a seam;
    - the three-tile shot shows no gap, overlap or lawn step.
12. **Lawns too dark, grey or olive (M035, M038).** f34 lawn within 14 of `#D7E10F`; dark bushes at hue 84–94° (not
    M040's 110°).
13. **Bowties** at bush hubs, petal centres and leaf roots: `M.fix_bowties` on every object, `nonmanifold_verts` 0.
14. **Exact booleans** (STAGES "Booleans"): only L ∪ U and the foot rocks, at the world origin, one piece at a time,
    saving between them. Nothing else is unioned.
15. **Budget.** Foliage is about a third of the count. The shelf and cap parts are tight (≤ 1000): tag dressing hero-only
    before thinning a slab or a column.
16. **Names and scope.**
    - No `TerracedLedge*` (W02), `CaveLedge*` or `StoneCliff*` (M040).
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit `m040.py`, `lib/vfx.py` or the shared helpers (frozen).

## Decisions (main session, 2026-10-29)
All 13 recommendations are accepted.
1. **Size:** 20 W × 14 D, with the lower lawn at 5.6 and the upper lawn at 10.4 (the same plateau as M040, M032 and M041). Seams are at x ±10 and the back plane at y +7.
2. **Upper block:** it reaches the seams behind front-corner cuts that widen from 2.0 to 2.6, leaving lower-lawn pockets at both ends.
3. **Back:** flat, with seven full-height columns cut in by no more than 0.5. The rear views are judged loosely.
4. **Rims:** pale rock with a bevel band under the turf, and no dirt band.
5. **Packaging:** one hero object made of closed shells.
   - The body is one union of the lower and upper blocks, done at the origin.
   - Every leaf, petal, rock and slab is its own shell, and every shell is manifold with 0 bowties.
   - **No floating dressing.**
   - **Turf caps every column top: 0 exposed column-top area** (M032's lesson).
6. **Corner filler:** one wedge, in the −X pocket.
7. **Connector:** +X end only, y +1.8 to +7.0, z 0 to 10.05.
8. **Code reuse:** M040 is now committed, so `m043.py` may import `m040` helpers.
9. **Cameras:** `f34_sheet (−15, 20)` governs, and `front_sheet (0, 16)` and `side (90, 8)` are strict. Include the three-tile tiling shot and the scale shot.
10. **Colour:**
    - rock `#CFAD9B` (always R > G > B, never mauve);
    - lawn `#CEDB12`;
    - bushes dark `#4F801A` and lime `#AAC305`;
    - flowers `#E0CF2C`;
    - trunks `#6A3210`;
    - plate `#9C908F`, warm grey with R ≥ B;
    - never use the Rock Shadow swatch as a key;
    - blend by position, never by facing.
11. **Lighting and VFX:** none; both are recorded as skipped.
12. **Collision:** precise on the hero, base, shelf and cap; hull on the filler; box on the connector.
13. **Budget:** 4000, with about 3400 planned.

Bushes are rounded leafy domes, not palm stars and not spiky (M040 m2, M039). The f34 shares in §1 are binding within ±4.
