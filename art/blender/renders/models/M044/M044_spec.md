# 044 Natural Ramp — spec

Reference: `art/blender/assets/references/044.png` (1024 × 1536 px). The sheet's title is "NATURAL RAMP / INDIVIDUAL
MODEL STUDY", with "FLINTBORN ENVIRONMENT MODEL CATALOG / STYLIZED • MODULAR • GAME-READY (BLENDER / ROBLOX)" at the top.
Its page number reads "43/132" (top left and bottom right), one less than the file number; INDEX.md row 44 calls it
"Flintborn Natural Ramp Study". The footer reads "FLINTBORN — INDIVIDUAL MODEL STUDY".
Builder: `art/blender/kit/mcp/m044.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7).

Sheet text:
- **Intro:** "Broad sloped path through terrain. Blend between levels. Walkable and modular."
- **Cells:** "ASSEMBLED FRONT THREE-QUARTER", "ASSEMBLED REAR THREE-QUARTER", "FRONT", "SIDE (RIGHT)", "REAR",
  "TOP (OVERHEAD)".
- **Exploded:** "PARTS (EXPLODED)": "Grass Border (Left)", "Left Cliff Rock Mass", "Top Landing Pad (Path)", "Ramp
  Wedge (Stone)", "Grass Border (Right)", "Right Cliff Rock Mass". Dashed arrows drop the path onto the wedge, the borders
  onto the cliff masses, and push the masses against the wedge's sides. A short unlabelled grass strip with a bush floats
  above the path's left end (§3.5).
- **Construction close-ups:** "1. PATH TO BORDER JUNCTION": "Simple overlapping edges. Clean connection, no gaps."
  "2. UNDERSIDE VIEW (RAMP WEDGE)": "Flat base for clean placement. Simple faceted geometry." "3. THICKNESS /
  CROSS-SECTION": "Path sits on stone wedge. Consistent thickness, clean faces."
- **Material palette:** "Path (Dirt) / Warm sand/brown", "Rock (Cliff / Stone) / Pale warm gray", "Grass / Bright
  green", "Foliage (Bushes) / Saturated green", "Rocks (Small) / Light gray/beige" (the swatch is brown: §3.8).
- **Modeling notes:** "Modular construction using simple reusable parts." "Broad, readable shapes with flat shaded
  faces." "Keep clean, low-poly and chunky silhouette." "Walkable top surface." "Consistent edge thickness and clean
  joins between parts." "No baked lighting, no texture noise, no decals." "Match Flintborn environment style and
  palette."
- **Game context:**
  - **M040 Cliff Wall** (committed): a 16 × 8 tile, lawn at **z 10.4**, seams x ±8, a flat back plane, lip front at
    back − 8.2. **M043 Terraced Ledge** (study accepted; builder in progress): lower lawn 5.6, upper lawn 10.4. **M032**
    and **M041** share the 10.4 plateau. This ramp is the walkable way from the ground up to that plateau (§2.1).
  - **The old kit's W02 row 3 `NaturalRamp`** (`art/blender/scripts/kit/W02/natural_ramp.py`, goals
    `art/blender/renders/kit/W02/natural_ramp_goals.md`, manifest `art/roblox/kit/W02/manifest.json`) is a different
    drawing: an 8-wide path climbing 9 over 22, plus Straight / Curved / Switchback variants. `MODEL_PROGRESS.md` row 50
    flags it "thin strip on thin slab (ref thick stepped wedge); flat side wall; dotted borders". **W02 owns every
    `NaturalRamp*` name** (§8). Reuse its lessons, not its sizes or names.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Cell paper `#FEFCF5` (254,
252, 245), tolerance 10. Cell borders were found from the grey rule lines (`lines.py`). Labels are painted out (`TITLES`
in `m.py`). Masks are `cls()` in `m.py` (HSV, h in degrees):
- **P, path:** not green, h 15–42, s ≥ 0.33, v ≥ 0.62 (the sand tiles and their darker edges).
- **R, rock:** h ≤ 50 or ≥ 190, s < 0.40, v ≥ 0.25, not another class. Lit faces are warm peach-beige (h 18–27°);
  shaded faces are cool blue-lavender (h 220–300°). Both count as R. Boulders and pebbles are R.
- **L, lawn:** green (h 45–170, s ≥ 0.28, v ≥ 0.12) with h < 80 and v ≥ 0.62. It also catches the yellow flowers and
  the lit tops of the light leaves.
- **F, foliage:** the rest of green (the bushes' dark emerald and mid leaves).
- **D, dirt / trunk:** h 0–40, s ≥ 0.40, v 0.15–0.62, not P (bush trunks).
- **B, ground shadow**, **T** text / dark, **O** outlines.
- Cells: f34 (18,131,510,465); r34 (514,131,1006,465); front (18,480,265,759); side (268,480,519,759); rear
  (522,480,772,759); top (776,480,1006,759); exploded (18,773,1006,1158); close-up 1 (28,1201,218,1383), close-up 2
  (235,1201,427,1383), close-up 3 (445,1201,633,1383). Swatch inner boxes 30 × 30 px at x 668–698, y 1207 / 1255 /
  1303 / 1351 / 1399 (`m.SW`).

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m044_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14, Pillow, numpy).
- **Helpers:** `m.py` (masks, boxes `V` / `X` / `SW` / `TITLES`, `label`, `main_obj`), `zoom.py` (crop with sheet grid),
  `px.py` (pixel probe), `blendall.py` (name search in every `.blend`), `lines.py` (cell borders).
- **Measurements:** `measure.py` → `bb.json` (bbox, W : H, shares, top profile, width per height, green / path / rock
  fifths) and `cls_*.png` previews; `rows.py <view>` (class extents per row); `side.py` (lawn line, rock steps, slope);
  `pathcorners.py` (path-mask corners); `explcomp.py` (exploded parts and path-slab corners); `bushes.py` (bush clusters,
  yellow share); `pebbles.py` (pebble and white-flower colours); `under.py` (close-up 2 flat share).
- **Layout fits:** `projfront.py` (front-cell perspective fit), `projf34.py` and `proj2.py` (orthographic block model at
  the f34 / side / top cameras; used to choose the size, §1.1, §3.1).
- **Colour:** `samp.py` → `samp_out.txt` (swatches; per cell: rock all / warm / cool, path, path edges, lawn, yellow,
  foliage dark / mid, trunk).
- **Zooms:** `zn_f34.png`, `zn_r34.png`, `zn_fs.png` (front + side), `zn_rt.png` (rear + top), `zn_expl.png`,
  `zn_cu.png`, `zn_pal.png`; detail `z_f34low.png`, `z_f34high.png`, `z_side.png`, `z_front.png`, `z_explpath.png`,
  `z_wedge.png`, `z_cu1.png`, `z_cu3.png`.
- **On our renders:** point `R` in `m.py` at the render, set `P` (the studio paper) and the `V` box, and re-run
  `measure.py` / `samp.py`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a modular terrain piece. Hero budget 4000 tris, each part under 1000. The plan in §4.3
  lands at about 3300–3700.
- **Overall read (check this first).** A **long straight ramp of warm sand flagstones climbing at about 30° between two
  lime grass borders, each border riding on a mass of pale warm columnar rock** that steps up with the slope:
  - the **path**: a broad strip of big flagstone tiles, **2 across and about 6 along the slope**, faint seams and tiny
    lips between rows, **pale pebbles** scattered on it, a short **flat landing** at the top;
  - under it a **stone wedge** (hidden in the hero except its flat base and back);
  - on each side a **grass border**: a lime turf strip raised a little above the path and overlapping its edge, carrying
    **round two-tone green bushes with brown trunks** (about 6 a side), pale boulders, **yellow five-petal flowers**,
    small white flowers and lime sprigs;
  - under each border a **cliff rock mass**: tall flat-faced columns whose tops step up with the ramp; their outer tops
    show as **pale peaked tips** beside the turf;
  - a thin lime **apron** along the foot of each cliff with sprigs and yellow flowers;
  - the low end runs out onto the ground (a thin path lip, a pale boulder and a bush at each corner).
  - Hero shares (f34): rock 36.4 %, path 30.6 %, green 32.4 % (lawn 20.6, foliage 11.8), trunk 0.7 %.
- **Focal silhouettes, in order:**
  1. The long sloped path band with its tile seams, rising from the lower-left to the upper-right of the f34.
  2. The two lime border lines running parallel to it, beaded with round dark bushes.
  3. The near cliff's palisade of tall columns stepping up under the right border (f34, side).
  4. The low end on the ground: the thin path lip, corner boulders, bushes.
- **Target: 16.0 W × 20.0 L; path from z 0.35 at the toe to 10.4, slope 29.9°, flat landing 2.5 long at 10.4.** The
  bbox is about 17.2 W (foliage and apron overhang ≤ 0.6 per side) × 20.4 L (toe dressing) × 12.5 H (bush tops on the
  landing borders). Tolerances: W, L ±0.4 on the rock and path; the rise 10.4, the slope 29.5–30.5° and the seams are
  exact; bbox H ±0.4. Decision §8.1.
  - **How it was derived.**
    - **Slope and run (side cell, the most direct view):** the border's lower edge fits a line of dy/dx 0.581 over sheet
      x 300–470: **30.2°** (`side.py`). The side cell is near-level, so the apparent slope is the true slope within 1°.
      The rock and lawn run 228 px (x 280 → 508) and rise 127 px to the border's top edge at the high end (ground y
      697 → 570): **L / H = 1.80**. Over the last 16 px (x 490 → 508) the line flattens to dy/dx ≈ 0.3: a short landing,
      about 7 % of the run. At H 10.4 that gives a run of 18.7 plus foliage at the toe; adopted **20.0** (the 4-stud
      grid; the orthographic model's side W : H is 1.57 against the sheet's 1.61, `proj2.py`).
    - **Rise:** **10.4**, M040's plateau. That makes the ramp the walkable way from the ground to M040 / M043's upper
      lawn / M032 / M041. At 5.6 (M043's lower lawn) the same proportions would give a 3-wide path, not "broad".
    - **Width:** the cells disagree (§3.1). The top cell's bbox W : D 0.739 → 14.8; its mid-length widths → 12.4. The
      exploded path slab (a near-isometric parallelogram, front edge 115 px, back 107, long edges 283 / 292) gives slope
      length ÷ path width 2.6 → path 8.3, total 16.6. The f34 path front edge against its long edge (0.28 screen, about
      0.21 after the perspective correction) → about 16. The front cell's perspective fit is degenerate in W against
      elevation (W 11–16.5 all fit, `projfront.py`). Adopted **16.0**: M040's pitch (seams at x ±8, so a ramp stands in
      front of exactly one M040 tile), the exploded and f34, and a top-view W : D of 0.80 (sheet 0.739, +0.06).
    - **Path share of the width:** front cell near end 111 / 212 px = 0.52; top cell 0.45–0.49; top-view shares P 48 /
      G 34 / R 17 match an 8-wide path with 3.3-wide borders and a 1-wide rock strip each side (§2.5). Adopted **path 8.0
      (x ±4.0)**, each side 4.0.
  - **Why this size.**
    - The landing at 10.4 meets M040, M043's upper cap, M032 and M041 at one plateau.
    - 29.9° is well inside walkable: Roblox's `Humanoid.MaxSlopeAngle` defaults to 89°, and the comfortable walking feel
      is ≤ 40°. No step on the path is taller than 0.35 (the toe lip), far under the default jump (JumpHeight 7.2; it
      needs no jump at all).
    - 16 wide sits on M040's 16-stud pitch and the 32 grid.
  - **Against the character (5.5):** the path is 8 wide, room for three or four characters abreast; the rise is 1.9
    characters; each tile row climbs 1.7 (a third of a character) over 3.4 of slope; the borders are 0.3 above the path
    (ankle height); bushes are 1.8–2.1 tall (waist to chest).
- **Build frame:** low end (toe) at the front −Y, high end at the back +Y, +X right, ground z 0. Seams x = ±8.0, toe
  y = −10.0, back plane y = +10.0. Stage 2 re-centres the hero on its bbox bottom centre; record where the seams, the
  toe and the back plane end up relative to the origin, as M040 did (`m040_offset`).

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | R | P | L | F | G (L + F) | D | O |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (18,131,510,465) | 51–497 × 143–449 (447 × 307) | **1.456** | 36.4 % | 30.6 | 20.6 | 11.8 | **32.4** | 0.7 | 1.9 |
| Rear three-quarter (514,131,1006,465) | 534–995 × 152–459 (462 × 308) | 1.500 | 36.9 | 29.5 | 21.3 | 11.5 | 32.8 | 0.8 | 1.9 |
| Front (18,480,265,759) | 32–251 × 539–708 (220 × 170) | **1.294** | 21.1 | 46.0 | 19.8 | 12.5 | 32.3 | 0.5 | 2.4 |
| Side (268,480,519,759) | 274–510 × 551–697 (237 × 147) | **1.612** | 76.2 | 0.3 | 11.4 | 11.9 | 23.3 | 0.3 | 1.9 |
| Rear (522,480,772,759) | 540–765 × 540–708 (226 × 169) | 1.337 | 21.6 | 46.1 | 20.4 | 11.5 | 31.9 | 0.4 | 2.5 |
| Top (776,480,1006,759) | 804–979 × 512–749 (176 × 238) | 0.739 (W : D) | 17.4 | 48.2 | 22.5 | 11.5 | 34.0 | 0.5 | 3.0 |

- Shares are of R + P + L + F + D; O and B are left out. **The r34 and rear cells repeat the f34 and front** (same
  orientation, shares within 1.1 points, §3.2). **Verifier tolerance:** shares ±4 points; W : H ±0.08 (the sheet's
  cameras have stronger perspective than the studio's 50 mm, §3.1); positions ±0.05 of W / H unless stated.
- **Yellow flowers** (h 46–60, s ≥ 0.6, v ≥ 0.85): 1.3 % of the f34, 0.84 % of the front, 0.92 % of the top.
- **Pebbles on the path:** 15–17 blobs per view, 2.0–2.7 % of the path area.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .25 | .32 | .43 | .50 | .55 | .56 | .66 | .73 | .80 | .80 | .82 | .91 | .91 | .93 | .99 | .97 | .94 | .91 | .89 | .84 | .31 |
| Front | .08 | .32 | .56 | .86 | .91 | .98 | .96 | .91 | .90 | .89 | .89 | .89 | .89 | .91 | .96 | .99 | .96 | .91 | .65 | .39 | .09 |
| Side | .06 | .25 | .33 | .32 | .36 | .39 | .48 | .56 | .58 | .57 | .69 | .69 | .75 | .75 | .86 | .95 | .95 | .99 | .95 | .94 | .84 |
| Top | .16 | .37 | .63 | .88 | .98 | .99 | .99 | .98 | .98 | .98 | .98 | .98 | .98 | .99 | .98 | 1.0 | .99 | .97 | .86 | .66 | .28 |

- Reading:
  - **f34:** a steady climb from the toe (f .00, h .25) to the high back corner (f .70, h .99), then the near cliff's
    back top edge falling to the right (f .75–.95, h .97 → .84), and the near cliff's foot (f 1.0, h .31).
  - **Front:** the path's far end at h .89 across f .35–.65 between the two border bush lines (h .91–.99); the corners
    fall to the toe bushes (f .05 / .95, h .32 / .39).
  - **Side:** the stepped climb, in four blocks (h .32 → .58 → .75 → .95), bush bumps on top; the last 0.15 nearly level.

**Width per height** (silhouette width at h .05 → .95, fraction of W):

```
f34    .21 .55 .91 .91 .82 .78 .66 .57 .41 .14
front  .95 .94 .92 .89 .85 .81 .77 .74 .70 .58
side   1.0 .97 .95 .80 .70 .66 .51 .41 .30 .20
top    .97 1.0 .95 .91 .86 .86 .83 .77 .75 .68
```

- **Front and top taper toward the high end** (front: near end 212 px, far end 152, 0.72; top: path 91 px at the bottom
  end, 52 at the top end). Both cells are perspective views from the low end; the exploded path is a parallelogram of
  constant width (§3.3).

**Fifths** (bottom → top, % of each class):

| View | Green | Path | Rock |
| --- | --- | --- | --- |
| f34 | 14.3 / 22.9 / 24.0 / 25.0 / 13.8 | 8.7 / 31.9 / 25.2 / 21.4 / 12.7 | 13.6 / 36.4 / 31.5 / 16.3 / 2.3 |
| Front | 24.2 / 20.6 / 20.7 / 15.6 / 19.0 | 27.5 / 22.6 / 22.2 / 19.2 / 8.6 | 16.4 / 29.3 / 22.1 / 27.7 / 4.6 |
| Side | 8.0 / 19.6 / 23.1 / 24.8 / 24.5 | — | 36.8 / 30.2 / 21.2 / 10.9 / 0.9 |
| Top | 22.6 / 20.4 / 20.8 / 21.2 / 15.0 | 24.1 / 21.8 / 20.2 / 18.4 / 15.5 | 19.6 / 28.1 / 18.5 / 16.3 / 17.5 |

**Path corners** (`pathcorners.py`, sheet px): f34 toe-left (84,382), toe-right (183,425), top-left (391,157), top-right
(443,176): the toe edge runs 23.5° below horizontal, the far long edge climbs at 36°. Front: toe 85 → 201 at y 705, far
end 111 → 175 at y 556. Top: bottom end 846 → 937, top end 867 → 919, length 232.

**Side-cell rock blocks** (`side.py`, `z_side.png`; 12.2 px per stud with H 10.4 = 127 px, y measured from the toe):
a pale toe rock and foliage at y 0–1.6; block 1 y 1.6–4.8 (top ≈ 2.9); block 2 4.8–8.0 (top 3.7 → 4.7); block 3
8.0–13.9 (top 5.6 → 7.9, one internal facet ridge); block 4 13.9–18.7 (top 8.8 → 10.3, one internal ridge). Each block's
top slopes at about half the ramp's slope (dy/dx 0.33 on block 2), so the lawn line steps over the block tops, and the
border's green side shows as a band 0.3–1.2 thick between the straight lawn top and the stepped rock (§2.3).

### 1.3 Silhouette and composition per view

**Front three-quarter (`zn_f34.png`, `z_f34low.png`, `z_f34high.png`): governs.** An elevated view from the front-right
(the +X side): the toe at the lower left, the landing at the upper right, the **+X cliff face** filling the lower right.
Our estimate is az +55 … +65, e 12–19 (the sheet camera has stronger perspective than ours, §3.1).
- **Path:** the flagstones are big: **2 across**, with a seam down the middle that jogs between rows, and **about 6 rows
  up the slope** plus the landing row. Each row meets the next with a faint lip and a thin shadow line (`z_f34low.png`
  at sheet (175–245, 340–360), `z_f34high.png` at (330–400, 170–180)). The toe shows the slab's front edge as a thin
  darker band (about 0.35 stud). About 17 pale pebbles (some with a dark shaded side) are scattered over the path.
- **Near (+X) border:** a lime strip along the path's right edge, slightly raised, with **6 dark round bushes** at roughly
  even spacing (sheet (200,420), (256,359), (309,292), (363,240), (405,204), (452,184)), white and yellow flowers between,
  and the near cliff's **peaked column tips** showing along its outer edge.
- **Far (−X) border:** the same strip along the far edge, **5–6 bushes** ((68,367), (130,305), (214,237), two at
  (305,186)), a **pale boulder at the toe** ((115–175, 395–440)) and a **boulder at the top-back corner** ((340–380,
  150–175)); a few rock tips of the far cliff show beyond it.
- **Near cliff (+X face):** a palisade of tall pale columns stepping up from the toe to the back: a low pointed stump at
  the toe ((400–445, 375–425)), then columns at about (450–520), (520–560), (560–620), (620–680), (680–760) … to the back
  corner, each with lit front faces (warm peach) and shaded faces (blue-lavender), dark creases between. The tops are
  peaked facets just under or beside the border.
- **Foot:** a lime apron along the near cliff's whole foot, with small lime sprigs and yellow flowers at (238,431),
  (273,430), (359,390), (412,372).

**Rear three-quarter (`zn_r34.png`).** The same camera side and orientation as the f34 (toe lower left, +X face lower
right), with the dressing moved a little. It does not show the −X face or the high end's back (§3.2).

**Front (`zn_fs.png`, `z_front.png`).** Looking up the ramp from the toe, near level (our fit: e ≈ 0–10° with
perspective). The path fills the middle (46 % of the view), tapering from 111 px at the toe to 71 at the landing. The two
borders run up both sides with **3–4 dark bushes each** (left (60,693), (77,647), (91,604), (84,557); right (205,674),
(196,576) and above), pale boulders in the borders (left (65–100, 575–600) and (60–110, 660–690); right (195–220,
570–600), (205–235, 650–690)) and the cliffs' column faces (lavender shade, peach lit) outside them. The toe shows the
thin path lip across 86–200 at y 700–708; corner bushes sit on the ground at both toe corners.

**Side (right) (`zn_fs.png`, `z_side.png`).** The +X face, near level: the stepped column blocks (§1.2), the green border
band above them climbing at 30°, bushes on top (dark emerald with lighter leaves, brown trunks), a toe rock and bush at
the left. No path visible (0.3 %).

**Rear (`zn_rt.png`).** A repeat of the front cell (the toe lip at the bottom, the path receding up the ramp).

**Top (`zn_rt.png`).** A long strip (W : D 0.739), the path down the middle (48 %), the borders with their bushes either
side (34 % green), a strip of rock tips along each outer edge (17 % rock). It tapers toward the top of the cell by
perspective (§3.3).

### 1.4 Parts (Parts (Exploded) (18,773,1006,1158), `zn_expl.png`, `z_explpath.png`, `z_wedge.png`, `explcomp.py`)

A near-isometric view from the front-left (the width axis drawn 27° below horizontal, the length axis 29° above). **The
hero governs every size**; the parts give shapes, part boundaries and facet character.

| Part | Box (sheet px) | Notes |
| --- | --- | --- |
| Grass Border (Left) | (66,855,319,1007) | A long lime turf strip with **lime-green side faces**, an uneven outer edge, 4–5 round dark bushes with brown trunks, yellow and white flowers, a pale boulder at its lower end. Drawn flat; L 54 / F 28 % |
| Left Cliff Rock Mass | (133,939,330,1146) | A block of about 5 tall columns (lit right faces, lavender left faces), **lawn and bushes on its top**. R 79 % |
| Top Landing Pad (Path) | path slab (330,796,683,980) | A flat tiled slab: **2 tiles across, 5–6 along**, a visible tile thickness (about 0.05 of the width on screen) with a darker orange edge, pebbles, a pale boulder and grass tufts on its corners. Constant width (front edge 115 px, back 107) |
| (unlabelled) short grass strip | (338,795,500,870) | A short lime strip with a dark bush, sprigs and flowers, drawn above the path's left end (§3.5) |
| Ramp Wedge (Stone) | (340,860,700,1110) | A long pale stone block: a tall rectangular end face, long faces split into broad facets, a flat top. Drawn as a box (§3.4) |
| Grass Border (Right) | (727,833,987,970) | As the left, with 5 bushes and a boulder at its right end. L 39 / F 42 % |
| Right Cliff Rock Mass | (720,920,975,1120) | About 6 columns **stepping down toward its front end** (tall at the left / back, lower at the right / front), lawn and bushes on top |

#### Ramp Wedge (Stone)
- **Shape:** a long wedge: flat base (close-up 2: **one big flat bottom face**, 0.5–0.7 of the visible underside, darker
  `#76645E` in shade, ringed by a band of broad rim facets), long faces in 2–3 broad facets each, the sloped top under
  the path (close-up 3: "path sits on stone wedge").
- **Hero size:** x ±4.1 × y −9.56 … +10.0; top = the path's underside (§2.2), 0 at y −9.56 → 9.82 at the back.

#### Top Landing Pad (Path)
- **Shape:** flagstone tiles, each a chunky slab with a slightly bevelled top edge and **darker orange-brown sides**
  (close-up 3: tile front faces `#C88A5C` under a `#F9C180` top; the tiles read as bricks about 0.4 as tall as they are
  long). Read the label as the whole path slab including its flat top landing (§3.5).
- **Hero size:** 8.0 × 20.0, tiles 0.6 thick, on the slope plus the landing (§2.2).

#### Grass Border (Left / Right)
- **Shape:** a lime turf strip draped along the path edge: its inner edge overlaps the path ("simple overlapping
  edges", close-up 1), its top about 0.3 above the path, **lime side faces** (close-up 1 shows the border's green side
  under its lit top), its outer edge scalloped round the column tips.
- **Dressing:** dark round bushes, boulders, flowers and sprigs (§2.4).
- **Hero size:** about 3.3 wide (x ±3.7 → ±7.0) × 20 long, 0.3–1.2 thick (it drapes over the stepped columns).

#### Left / Right Cliff Rock Mass
- **Shape:** tall flat-faced columns, side by side along the ramp, with dark creases; **facets are tall strips**; tops
  are peaked (close-up 1: each column top is a two- or three-facet roof whose apex sits at the turf's outer edge); the
  heights step up with the slope (side cell, right mass in the exploded).
- **Hero size:** x ±4.0 → ±8.0, y −8.3 → +10.0, heights 2.9 at the toe column → 10.4 at the back.

#### Bushes, flowers, rocks (`z_cu1.png`, `z_f34low.png`)
- **Dark bush:** a round dome of **broad rounded leaves in two tones**: deep emerald (`#196B25`, 129°) inner and lower
  leaves and fresh lighter green (`#608316` → lit `#95D539`, 79°) upper leaves, 8–12 leaves in two or three tiers round a
  short **brown trunk** that shows only at the base. Ø 2.3–2.8, 1.8–2.1 tall. In the top cell they read as rosettes with
  a dark heart.
- **Yellow flower:** five broad rounded petals (`#EAE51B`, lit `#FAF731`) round a darker yellow-olive centre, Ø 0.5–0.7,
  lying almost flat on the turf in small groups of 2–3 (close-up 1).
- **White flower:** a small cream flower (`#F3EBD9`), Ø 0.3–0.4, single or in pairs.
- **Sprig:** 3–5 lime leaves from one root (`#A9BC02`–`#8CBC09`), Ø 0.7–1.0, sometimes with a yellow flower.
- **Border boulders:** pale, rounded-angular, a flat-ish crown with 4–6 broad facets, 1.3–2.0 across.
- **Pebbles:** 0.25–0.6, pale warm beige lit (`#E0C3AB`), grey shaded side (`#A59393`), on the path.
- **Apron:** a thin lime strip along each cliff foot, jagged edge.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (toe −Y, high end +Y, +X right, ground z 0).

### 2.1 The seam contract (binding; record it in the builder docstring and the export notes)

| Item | Value | Notes |
| --- | --- | --- |
| Side planes | **x = −8.0 and x = +8.0** | no rock vertex past them (column relief inward only, to ≥ ±7.4); foliage and apron overhang ≤ 0.6, symmetric |
| Back plane | **y = +10.0, flat**, z 0 → 10.4 (the wedge, both cliff backs, the landing tiles and border ends) | relief inward only, ≥ +9.6 |
| Toe | y = −10.0: the path toe lip, the border tongues and corner dressing reach it; toe dressing ≤ 0.4 in front of it | |
| Path top | **z(y) = 0.35 + 0.5743 (y + 10)** for y ≤ +7.5 (29.9°), **10.4** for y +7.5 … +10.0 (landing) | the walkable surface |
| Border top | z(y) + 0.30 up to y +8.5, then lowering to **10.45 at the back plane** | so the border lawn meets a 10.4 plateau flush |
| Landing | y +7.5 … +10.0, path top 10.4 flat, x ±4.0 | flush with M040's lip turf and M043's upper cap |

- **With M040 (16 × 8, lawn 10.4, seams x ±8, lip front at back − 8.2).** Same x: the ramp's sides line up with M040's
  seams. Put the ramp's back plane on M040's lip front (M040 frame y −4.2). Then the landing path (10.4) and the border
  ends (10.45) meet M040's lip turf flush; the ramp's back rock face touches the lip's rim and stands 0.1–0.3 in front of
  M040's column ridges (the gap is hidden behind the ramp). A run of M040 tiles with one ramp in front is the intended
  use.
- **With M043 (20 wide, upper cap at 10.4, lower lawn 5.6).** The landing matches the upper cap's 10.4, but M043's lower
  terrace stands in front of its upper face, so the ramp meets M043 only where an M040 tile or M043's planar end is
  reachable. A ground → 5.6 ramp (half the run) is a later variant (decision §8.10).
- **Run ends / stand-alone:** the back face is a flat columnar rock face (rear cells don't draw it; §3.2), the side faces
  are cliff faces.

### 2.2 Path and wedge

- **Tiles (`StoneRampPath`).** 2 columns × 7 rows = 14 tiles, each a closed slab 0.6 thick (vertical), its top edge
  bevelled 0.08 (so seams read as dark lines without gaps showing the wedge).
  - **Columns:** x −4.0 … 0 and 0 … +4.0; the middle seam jogs ±0.3 from row to row (sheet f34 / exploded).
  - **Rows on the slope:** 6 rows, each 2.92 of run (3.36 of slope, climbing 1.675); the cross seams of the left and right
    columns are offset by 0.6 so the path doesn't read as a grid. Row 7 is the landing, y +7.5 … +10.0, flat.
  - **Lips:** each row's downhill edge sits on the §2.1 line and its top is tilted 1.5–2° flatter than the slope, so its
    uphill edge sits 0.09–0.12 below the next row's downhill edge: the sheet's faint lips. The landing row meets row 6 with the same lip. Walkable without a jump.
  - **Toe:** row 1's front edge stands 0.35 high on the ground with a 45° chamfer on its top front edge; its bottom is
    flat on the ground for y −10.0 … −9.56 (the wedge starts there).
  - Seams 0.02 apart at most, tiles sunk 0.02 into the wedge; per-tile height jitter ±0.03 (no more).
- **Pebbles:** 20, Ø 0.25–0.6, 0.12–0.25 tall, sunk 0.03 into the tiles, spread over the whole path (more near the
  edges, a few along the seams), none taller than 0.25 (walkable). Two have a darker grey side by position (not facing),
  §5.
- **Wedge (`StoneRampWedge`).** x ±4.1 (0.1 under each cliff mass), y −9.56 … +10.0, base z 0, top = path top − 0.58
  (tiles sunk 0.02). Back face full height 0 → 9.82 on y +10.0 with two shallow column creases (inward ≤ 0.3). Long faces
  2–3 broad facets each (hidden in the hero, seen in the part shot). Underside: one flat face ≥ 0.5 of the visible
  underside at e −35, its outer ring bevelled up 0.2 over 0.3 (close-up 2).

### 2.3 Cliff masses

Two mirrored masses (`StoneRampCliffL`, `StoneRampCliffR`), not identical: change the column widths by ±0.2 and the
apex heights by ±0.15 between sides.

| Column | y range | Apex height at its downhill → uphill end | Crease after it | Sheet evidence |
| --- | --- | --- | --- | --- |
| T (toe rock) | −9.8 … −8.3 (a separate pointed rock, x ±5.6 … ±7.8) | 1.6 apex | — | f34 stump (400–445, 375–425); side toe rock |
| C1 | −8.3 … −4.9 | 1.80 → 2.85 | 0.5 deep | side block 1 (top ≈ 2.9) |
| C2 | −4.9 … −1.4 | 3.75 → 4.85 | 0.5 | side block 2 (3.7 → 4.7) |
| C3 | −1.4 … +1.8 | 5.75 → 6.70 | 0.3 | side block 3, front half (5.6 → …) |
| C4 | +1.8 … +4.9 | 7.60 → 8.45 | 0.5 | side block 3, back half (… → 7.9) |
| C5 | +4.9 … +7.5 | 9.35 → 9.95 | 0.3 | side block 4 (8.8 → …) |
| C6 | +7.5 … +10.0 | 10.30 → 10.40 (flat, under the landing border) | — (back plane) | side block 4 (… → 10.3), landing |

- The apexes come from the border top B(y) = 0.65 + 0.5743 (y + 10): **B + 0.15 at each column's downhill end, B − 0.75
  at its uphill end** (an 18° top, tan 0.33), so each crease steps up about 0.9. Check: B at y −8.3 / −4.9 / −1.4 /
  +1.8 / +4.9 / +7.5 = 1.63 / 3.58 / 5.59 / 7.43 / 9.21 / 10.70.

- **Columns:** x from ±4.0 (inner face, overlapping the wedge side by 0.1, hidden under the border) to the outer face at
  ±7.6 … ±8.0 (in / out per column, never past ±8.0). Each outer face is **2 tall facets** (a vertical ridge 0.1–0.2
  proud at 0.4–0.6 of the column's length), a 0.3 batter (top ring 0.3 inside the foot ring), creases as in the table.
  Front and back ends of each column are faceted too (visible across the creases).
- **Peaked tops:** each column top is a roof: from the apex line at x ±7.0 (under the turf's outer edge) down to the
  outer face's top edge 0.5–0.8 lower, in 2–3 facets (≥ 30° from horizontal, close-up 1). Inside x ±7.0 the column top
  is a plane at the apex line − 0.30, sloping at about 18° (tan 0.33): the turf drapes on it.
- **Apex against the turf:** at each column's downhill end the apex is 0.0–0.3 **above** the border top (the pale tips
  the f34 and close-up 1 show beside the lawn); at its uphill end it is 0.6–0.9 below, so the border's green side shows
  between (the side cell's sawtooth). Over C6 the apex follows the landing (10.0 → 10.4).
- **Back plane:** C6's back face and the wedge's back face lie on y +10.0, relief inward ≤ 0.4.
- **Foot:** flat bottom at z 0; the outer foot ring bevels in 0.2 over the lowest 0.3.

### 2.4 Borders and dressing

| Piece | Position (x, y), base z | Size | Notes | Sheet evidence |
| --- | --- | --- | --- | --- |
| Border turf L / R | inner edge x ±3.7 (0.3 over the path, lobed ±0.15), outer edge x ±7.0 scalloped ±0.3 round the column apexes; y −10.0 … +10.0 | top = §2.1 border top; underside = the column tops (thickness 0.3 at a column's downhill end, up to 1.2 at its uphill end) | one closed sloped slab per side; lime top **and lime sides**; at the toe it runs down onto the ground as a rounded tongue (top 0.65 at y −10) | close-up 1, side, exploded borders |
| Dark bushes R1–R6 | x +5.4 / +5.8 alternating; y −8.4, −5.2, −1.9, +1.5, +4.8, +8.3; on the border top | Ø 2.3–2.8, 1.8–2.1 tall | two-tone domes, trunk ≤ 0.2 showing | f34 near border (6); top right column |
| Dark bushes L1–L6 | x −5.8 / −5.4; y −7.8, −4.6, −1.3, +2.1, +5.4, +8.7 | as above | two at L5 / L6 may touch (f34 (305,186)) | f34 far border; front left |
| Toe boulder L | (−6.0, −9.3), on the ground, sunk 0.1, leaning into the border tongue | 1.9 × 1.6 × 1.5 | flat-ish crown | f34 (115–175, 395–440); front (60–110, 660–690) |
| Mid boulders | L (−6.2, +0.6), R (+6.2, −3.4), on the border, sunk 0.1 | 1.5 × 1.3 × 1.2 | | front left (65–100, 575–600), right (205–235, 650–690) |
| Top-corner boulders | L (−6.3, +9.0), R (+6.0, +9.3), on the landing border | 1.6 × 1.4 × 1.3 | | f34 (340–380, 150–175); front right (195–220, 570–600) |
| Yellow flowers | 5–6 per border, in groups of 2–3 at bush feet; 3 per apron | Ø 0.5–0.7 | petals lie on the turf (pitch ≤ 15°) | close-up 1; f34 |
| White flowers | 4–5 per border | Ø 0.3–0.4 | | f34, close-up 1 |
| Sprigs | 3 per border, 4 per apron | Ø 0.7–1.0 | | f34 foot (238,431), (273,430), (359,390), (412,372) |
| Apron L / R | x ±7.7 … ±8.6 (jagged), y −9.0 … +9.8 | 0.08–0.12 thick | tucked 0.1 under the cliff foot; overhang ≤ 0.6 | f34 near foot, top-cell edges |
| Toe corner bushes | (±5.8, −10.0 … −9.6) are R1 / L1 moved onto the tongue if the front cell's ground-level corner bushes need it | | | front (60,693), (205,674) |

- **Keep clear:** the path itself carries only pebbles (walkable); no bush within 0.3 of the border's inner edge; nothing
  behind y +10.0 (the back plane abuts terrain); nothing past x ±8.6.
- **Plant build:** reuse M040's `bush` (round dome, M040 m2 fix: a crown tier of 4–5 leaves pitched up and out, trunk
  ≤ 0.2 showing), `sprig`, `pebble`, `lawn_rock`, `apron`. A bush's leaves are blunt rounded ovals (tip ≥ 110°, camber
  ≤ 0.07 L), no leaf within 12° of edge-on at the f34 camera beyond 12 % of leaf area (M039 finding 1).

### 2.5 Expected extents and screen checks

- **Extents (build frame):** X −8.6 … +8.6 (aprons; rock −8.0 … +8.0); Y −10.4 … +10.0 (toe dressing; back plane);
  Z 0 … about 12.5 (L6 / R6 tops on the landing borders). Bbox ≈ 17.2 × 20.4 × 12.5.
- **Self-consistency (`proj2.py`, orthographic block model with bushes):** side (90, 0) W : H 1.57 (sheet 1.61); top
  W : D 0.80 (0.739); f34 W : H 1.40–1.47 at az 60–65, e 12–15 (1.456).
- **Checks on the renders** (floor hidden, `measure.py` masks; the studio's paper colour in `P`):
  - **f34_sheet (60, 15)** (probe az 50 / 60 / 68 × e 10 / 15 / 20, keep the best):
    - W : H 1.38–1.53 (sheet 1.456);
    - shares R 36.4 ± 4, P 30.6 ± 4, G 32.4 ± 4 (L 20.6 ± 4, F 11.8 ± 3), D ≤ 1.5;
    - green, path and rock fifths within ±7 of §1.2;
    - the toe at the lower left, the landing at the upper right, the +X palisade in the lower right; 2 tile columns and
      6–7 rows legible; 6 bushes along the near border;
    - top profile within ±0.08 (mean ≤ 0.05) of §1.2.
  - **front_sheet (0, 6)** (probe e 0 / 6 / 12): W : H 1.22–1.37 (1.294); P 46 ± 5, G 32 ± 4, R 21 ± 4; the toe lip
    across the bottom; the two border bush lines; the path's far end at h .85–.92.
  - **side (90, 4)** (probe e 0 / 4 / 8): W : H 1.53–1.69 (1.612); R 76 ± 5, G 23 ± 5; four stepped blocks under a 30°
    green band; slope of the band's lower edge 29–31°.
  - **top (0, 89):** W : D 0.70–0.82 (0.739, the size decision puts us at the upper edge); P 48 ± 5, G 34 ± 5, R 17 ± 5;
    the rock strip ≤ 1.1 wide along each outer edge.
  - **rear_sheet, r34_sheet:** judged as repeats of the front / f34 (§3.2). Render them at (180, 6) and (−120, 15) for the
    record only.

## 3. View conflicts and resolutions

### 3.1 Width: top cell (12.4–14.8) vs exploded and f34 (about 16) vs front (any)

- **Evidence:** §1.1. The cells were drawn with strong perspective, and the studio renders at 50 mm.
- **Resolution (decision §8.1):** **16.0 W**, path 8.0. Top-view W : D 0.80 against 0.739 is a recorded +0.06.
  **Alternative: 14.0 W**, path 7.0 (top W : D 0.70; off M040's pitch, a narrower path).

### 3.2 Rear and r34 cells repeat the front and f34

- **Evidence:** the r34 has the toe at the lower left and the +X face lower right, like the f34; the rear has the toe lip
  at the bottom, like the front. Shares match within 1.1 points.
- **Resolution:** the high end's back and the −X face are not drawn. The back is a flat columnar plane (§2.1) that abuts
  the plateau; the −X face mirrors the +X face with varied columns. Judge rear / r34 as repeats; record it.

### 3.3 Front and top taper toward the high end vs the exploded path's constant width

- **Evidence:** front far / near width 0.72, top 0.57 (path), f34 path back edge 55 px against 108 at the toe; the
  exploded slab is a parallelogram (115 / 107 px).
- **Resolution:** **constant width** (perspective, not geometry). A tapered ramp would not tile against a 16-wide cliff.
  Record the taper as a camera difference. **Alternative:** taper the path to 0.85 at the landing (not recommended).

### 3.4 The exploded wedge is a box with a tall low end vs the assembled ramp running to the ground

- **Evidence:** the exploded wedge's end face is tall; every assembled view puts the toe on the ground with a thin lip.
- **Resolution:** a true wedge (§2.2), its label wins. The exploded box shape is a drawing convention.

### 3.5 "Top Landing Pad (Path)" label and the unlabelled short grass strip

- **Evidence:** the label's leader runs toward the short grass strip drawn above the path's left end; the strip has a
  bush and flowers and no path on it. The path slab itself is the only tiled piece.
- **Resolution:** the label names the **path slab including its flat landing row** (`StoneRampPath`). The short strip
  is the landing segment of a grass border; build it as the last 2.5 of each border (y +7.5 … +10.0), not as a separate
  part. **Alternative:** a separate `StoneRampLandingBorder` part (adds a seam in the border).

### 3.6 Turf caps the rock (M032) vs the sheet's rock tips beside the turf

- **Evidence:** close-up 1 and the f34 show peaked pale column tops standing at the turf's outer edge; the top cell has
  17 % rock in a strip along each outer edge.
- **Resolution:** the turf covers every column top inside x ±7.0. Only the outer **roof facets** (≥ 30° slopes) show,
  ≤ 1.1 wide; there is **no flat exposed column top** and no rock between the path and the border (§6). This is the
  sheet's read, not M032's failure (a strip of turf between bare flat tops).

### 3.7 "No baked lighting, no texture noise, no decals" against the user's blended-colour rule

- The user's rule wins quietly: broad position-based blends (lighter column tops, deeper feet, path patches toward the
  edges, per-tile tint) and whole-facet Tint mottling at low amplitude, never per-triangle confetti. The sheet's
  peach-lit / lavender-shade split is the light (§5.3).

### 3.8 Palette names against the renders

- "Rocks (Small) — Light gray/beige" is a **brown** swatch `#9F7354` (25°, 0.47). The rendered pebbles and boulders are
  pale beige (`#E0C3AB` lit) with grey shade sides. **Pebbles and boulders use the rock family**; the swatch is used for
  nothing (at most a few soil specks at bush roots).
- "Rock (Cliff / Stone)" `#BDA8A1` (15°, 0.15, R − B 28) is paler and pinker than the rendered warm faces (`#D6B7A3`,
  24°, R − B 51). Calibrate to the rendered regions (§5.4).
- "Foliage (Bushes)" `#619145` (98°, 0.52) sits between the bushes' two tones (emerald 129° / fresh 79°).

### 3.9 Cast shadow

- The sheet's ground shadows are faint near-white (B, background). Render every `*_sheet` view with the studio floor
  hidden (M034 §2.6).

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

**Reuse M040** (committed): the palisade loft (`body_rings`, `palisade`), `_cdt`, `_cap`, the plants (`_leaf`, `bush`,
`sprig`, `pebble`, `lawn_rock`, `apron`), the shell / contact / capping reports and `measure()`. Import `m040` as
`m040` imports `m011` / `m012`; if `m043` is committed when this model starts, its sloped-free helpers may be imported
too. Don't edit `m040.py` or `m043.py`.

1. `path()` → **`StoneRampPath`** ("Top Landing Pad (Path)"): 14 tiles (§2.2), each an explicit bevelled slab (8 + 8
   bevel faces, 24–28 tris), plus the 20 pebbles. Compare with the exploded slab (2 across, 6–7 along, the darker tile
   sides, pebbles) and close-up 3 (chunky tiles on the wedge).
2. `wedge()` → **`StoneRampWedge`**: one closed shell, explicit verts (base ring, sloped top, faceted long faces, the
   back creases), 60–120 tris. **Underside extra** (e −35) against close-up 2.
3. `cliff(side)` → **`StoneRampCliffL` / `StoneRampCliffR`**: 6 explicit column prisms with roof tops (§2.3) and the
   toe rock, unioned per side with a merge-0 exact union **at the world origin** (STAGES "Booleans"; `m021._union_fine`),
   one column at a time, saving between; the toe rock stays its own shell. Compare with the exploded masses (tall
   strips, tops stepping toward the front).
4. `border(side)` → **`StoneRampBorderL` / `StoneRampBorderR`**: the draped turf slab (CDT top over the outline,
   resampled at ≤ 1.0 spacing so the patches blend; lime side walls down to the column tops) plus that side's bushes,
   boulders, flowers and sprigs. Compare with the exploded borders.
5. **Aprons and foot dressing** belong to the hero (tagged `on="hero"`), not a part.
6. **Hero `StoneRamp`** = wedge + path + both cliffs + both borders + aprons + all dressing.
   - Each piece is its own closed shell in one object; no booleans between pieces.
   - `M.fix_bowties`; origin at the bbox bottom centre; transforms applied.
7. **Parts shot** (az −35, e 25), laid out like the exploded: path above the wedge, borders above the cliffs, left
   group to the left, right group to the right.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a straight ramp of sand flagstones climbing at 30° between two lime borders of round two-tone
   bushes, on pale columnar rock that steps up with the slope; the toe on the ground, a flat landing at the top.
2. **f34_sheet, front_sheet, side, top** per §2.5.
3. **Walk test (numbers):** the rows' downhill edges at y −10.0 / −7.08 / −4.17 / −1.25 / +1.67 / +4.58 / +7.5 sit at
   z 0.35 / 2.03 / 3.70 / 5.37 / 7.05 / 8.72 / 10.40 ± 0.02, and the landing is flat at 10.40 to y +10; slope 29.9°; the
   largest step anywhere on the path ≤ 0.35 (the toe) and ≤ 0.12 between rows; pebbles ≤ 0.25 tall.
4. **Rock-shape targets** (§4.4) on the cliff parts and the hero.
5. **Capping and contact** (§6). Then a **junction extra** `junc_cu (40, 30)` framed on the +X border at y ≈ −3,
   against close-up 1: the turf overlapping the tile edges, its lime side, the peaked column tips at its outer edge, no
   gap. Then a **section extra** `sect_cu (0, 5)` with a clip plane at y −2 (or a part render of the path on the
   wedge), against close-up 3: tiles on the wedge, the border on the cliff, flat faces.
6. **Plateau shot:** the hero with its back plane on an M040 tile's lip front (if M040 is in the kit file), from (45,
   20) and from the front: the landing and borders flush with M040's lawn at 10.4, no gap, the sides on M040's seams.
7. **Scale shot:** 5.5-stud character markers on the ground at the toe, on the path at y 0 and on the landing.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Wedge | 1 | 60–120 | 60–120 |
| Path tiles | 14 | 24–28 | 340–390 |
| Pebbles | 20 | 6–10 | 120–200 |
| Cliff columns (per side, unioned) | 2 × 6 | 36–50 | 430–600 |
| Toe rocks | 2 | 18–30 | 36–60 |
| Border turf slabs | 2 | 140–200 | 280–400 |
| Dark bushes (8–10 leaves × 8 + trunk 8) | 12 | 70–90 | 840–1080 |
| Boulders | 6 | 16–26 | 100–150 |
| Yellow flowers (5 petals + centre) | 15 | 12–16 | 180–240 |
| White flowers | 10 | 6–8 | 60–80 |
| Sprigs | 14 | 20–30 | 280–420 |
| Aprons | 2 | 30–50 | 60–100 |
| **Hero** | | | **about 2800–3800**, plan ≈ 3400 (limit 4000) |
| Parts: Path / Wedge / CliffL / CliffR / BorderL / BorderR | | | 460–590 / 60–120 / 250–350 each / 760–960 each (limit 1000) |

- **The border parts are tight.** If a border is over 950, tag its sprigs and two white flowers `on="hero"` before
  thinning a bush or the turf.
- **If the hero is over 3900:** drop hidden back leaves, then pebbles (to 14), then apron sprigs (to 2 a side). Never
  drop a bush the f34 or front shows, and never thin a column below §4.4.

### 4.4 Rock-shape targets (binding; check with `M.audit`, own bmesh code and M040's `rock_metrics`)

| Target | Columns | Toe rocks | Boulders | Wedge | Pebbles |
| --- | --- | --- | --- | --- | --- |
| Sides | 5–7 | 4–5 + apex | 5–6 | 6 + facets | 4–6 |
| Facets visible from the side | 2–4 per column | 2–3 | 4–6 | 2–3 per long face | 2–3 |
| Facet shape | **tall strips h/w 2.5–4.5** on the outer faces (C1 / T may be squatter) | long triangles to the apex | broad, h/w 0.8–2 | broad | broad |
| Top | **roof facets ≥ 30° outside x ±7.0; draped plane under the turf inside** | apex | flat-ish crown ≥ 25 % of plan | under the tiles | flat-ish |
| Side faces within 20° of vertical | ≥ 85 % of outer-face area | ≥ 60 % | ≥ 40 % | ≥ 90 % | — |
| Narrowest face | ≥ 0.8 wide, ≥ 2.0 tall (C3–C6) | — | — | — | — |

- **Irregular, not a pattern:** triangle area CV ≥ 0.6 on each cliff. No vertex ringed by 5–6 near-equal triangles.
  Never `primitive_ico_sphere`, subdivision, displacement or `K.hull_rock` jitter balls (egg boulders, M034 / M037).

### 4.5 Stages 2 and 3

- **Stage 2:** every shell closed and manifold; zero non-manifold edges and verts (`nonmanifold_verts` 0), boundary,
  wire and loose elements; no zero-area faces or n-gons; normals outward; no corners under 5° on visible faces
  (`m011._tidy` / `_desliver`); the back-plane faces planar at y +10.0 ± 0.001; no rock vertex past x ±8.0.
- **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 30 × 30 box inside each, sd ≤ 1.4)

| Swatch | Box | Hex | HSV | Channel order | Use |
| --- | --- | --- | --- | --- | --- |
| Path (Dirt) | (668,1207,698,1237) | `#F4B676` | 30°, 0.52, 0.96 | R > G > B | start for `path` |
| Rock (Cliff / Stone) | (668,1255,698,1285) | `#BDA8A1` | 15°, 0.15, 0.74 | R > G > B, R − B 28 | hue reference only; too pale and pink for a key |
| Grass | (668,1303,698,1333) | `#B4C02D` | 65°, 0.77, 0.75 | G > R > B | hue reference; the rendered lawn is brighter and more saturated |
| Foliage (Bushes) | (668,1351,698,1381) | `#619145` | 98°, 0.52, 0.57 | G > R > B | between the bushes' two tones |
| Rocks (Small) | (668,1399,698,1429) | `#9F7354` | 25°, 0.47, 0.62 | R > G > B | **not used** (§3.8) |

### 5.2 Rendered regions (`samp.py`; median / lit quartile / shade quartile)

| Region | f34 | front | top | exploded | close-ups |
| --- | --- | --- | --- | --- | --- |
| Rock warm faces (h ≤ 60) | **`#D6B7A3`** (24°, .24, .84) / `#EFD7C0` / `#A59088` | `#D2B6A5` (23°, .21) / `#F3DAC2` | `#D7BCAA` | `#D4BDB3` (18°, .16) / `#E3D1CB` | cu1 `#D2B4A3`; cu3 `#D1B8A5` |
| Rock cool faces (the shade light) | `#867D87` (294°) | `#616A81` (223°) | `#616B83` | `#7C7A8B` (247°) | cu1 `#77788A` |
| Warm share of rock | 72.5 % | 60.5 | 63.7 | 55.3 | side 49.1 |
| Flat underside (close-up 2, in shade) | | | | | `#76645E` (15°, .20, .46), rim `#CFBAAE` |
| Path tops | **`#F8BB7B`** (31°, .50, .97) / `#FDC685` / `#EAAD73` | `#FCC180` | `#FABE7D` | `#FBBF7F` | cu1 `#FABD7A` |
| Path tile sides / toe lip (v < 0.85) | `#BC885B` (28°, .52) | `#CC8C5A` | `#C38C5B` | `#B87F5A` | cu3 front faces `#C88A5C` (25°, .54) |
| Lawn (lime, not yellow) | **`#C3CF06`** (64°, .97, .81) / `#DAE205` / `#AAB909` | `#BFCA06` | `#C0CB08` | `#CBD20C` | cu1 `#C1CC0A`; cu3 `#D1DB08` |
| Bush foliage (all F) | `#43791C` (95°, .77, .47) / `#83BE38` / `#1B4511` | `#41731C` | `#447118` | `#538522` | cu1 `#487E18` |
| Dark emerald leaves (h ≥ 95) | **`#196B25`** (129°, .77, .42) / `#329B38` | `#1A6222` | `#1E611C` | `#1C6C23` | cu1 `#1F6C2D` |
| Fresh leaves (h < 95) | **`#608316`** (79°, .83, .51) / `#95D539` | `#637F16` | `#5A7C14` | `#779121` | cu1 `#5A8410` |
| Yellow flowers | `#E5DD0D` (58°, .94, .90) / `#F6F109` | `#E5D92A` | `#E3D72C` | `#E2DA2C` | cu1 `#EAE51B` / lit `#FAF731` |
| White flowers | `#F3EBD9` (42°, .11, .95) | `#ECEBD2` | `#EFE3D6` | | |
| Pebbles | lit `#E0C3AB` (27°, .24), shade `#A59393` / `#A8A6AE` (probes, close-up 1) | | | | |
| Trunks (D) | `#6F371A` (21°, .77, .44) | `#6E3714` | | `#72371B` | |

### 5.3 How the colour works

**Rock.**
- **One pale warm peach-beige stone** for the columns, toe rocks, wedge, boulders and pebbles. Warm faces are hue
  18–26°, sat 0.16–0.26, **always R > G > B**.
- The sheet's shade faces are blue-lavender (223–300°): that is the fill light. Our studio's shade is warm grey; that is
  light, not paint. **Never colour by facing.**
- It is **the same stone family as M040 / M043** (their warm faces `#D4B29D` / `#D7B09C`; here `#D6B7A3`), a touch
  paler, so a ramp in front of an M040 tile reads as one rock.
- **Painted signals by position:** the upper third of each column a step lighter; the roof facets and boulder crowns
  lightest; the lowest 1.5 studs a touch deeper. Whole facets only, by height plus a broad noise field. **No moss, no
  green on the cliff faces** (the sheet's faces are bare).
- **Mauve guard (M031, M032 rounds 1–2, M040):** every rock key R > G > B, hue 15–26°, R − B ≥ 30. Rock (Cliff / Stone)
  `#BDA8A1` (R − B 28) is a hue reference only; the lavender shade is never a key, not even in a mix.

**Path.**
- One warm sand (30–32°, sat 0.48–0.52, value ≥ 0.92) on every tile top.
- **Per-tile tint ±0.04** so neighbouring tiles separate (the sheet's tiles differ slightly).
- Broad lighter / deeper patches across tiles by a noise field, and a slightly deeper tone in the 0.6 next to each
  border (by distance to the border, not by facing).
- **Tile sides and the toe lip:** a darker orange-brown, applied by **role** (the tile's bevel ring and side faces are
  the "worn edge" region) at a 50 % mix of `path_deep`. This is the exploded's and close-up 3's darker tile sides; it
  correlates with facing, so keep it to the bevel / side role and check `K.check` < 0.5 on the path material. If the
  check fails, drop the mix to 30 % and let the lighting do the rest.

**Lawn.** One bright yellow-lime (62–66°, sat ≥ 0.92) on both borders, their sides and the aprons. Lighter broad
patches; slightly deeper near bush roots and boulders.

**Bushes.** Two tones in every dark bush, by role, never per face: the **upper / outer leaves fresh green** (79–85°, lit
toward `#95D539`), the **inner / lower leaves deep emerald** (125–130°). Brown trunks. Keep the two tones ≥ 35° apart in
hue (the sheet's 79° / 129°); the bush median should land near `#43791C` (95°).

**Flowers.** Yellow petals 56–59° (yellow, not lime, not orange), a darker olive-yellow centre; white flowers cream
(sat ≤ 0.12).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are medians of unshadowed rendered regions (warm faces, lit lawns, bush medians), not swatches.
`K.sample` kinds: `"all"` for rock (M040's override: the stone filter drops sat > 0.18), `"brown"` for path and trunk,
`"green"` for lawn and leaves, `"vivid"` for lime / yellow. **Start from M040's calibrated hexes** where the family
matches (rock `#A3938B`, rock_light `#AD9E95`, rock_deep `#92837C`, grass `#9DAF06`, grass_light `#B0BA12`, grass_deep
`#879C02`, lime `#89A203`, trunk `#502401`), then re-calibrate to these targets.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m044_rock` | **`#D3B6A4`** (warm faces: f34 `#D6B7A3`, front `#D2B6A5`, cu1 `#D2B4A3`, exploded `#D4BDB3`) | 18–26°, 0.18–0.25, R > G > B, R − B ≥ 30 | columns, toe rocks, wedge, boulders, default | rough 0.9, metal 0 |
| `m044_rock_light` | `#E8D0BC` (lit `#EFD7C0`, exploded lit `#E3D1CB`; about +18 over `rock`) | 20–27°, 0.16–0.24 | upper 30 % of each column at 30–40 %; roof facets at 50 %; boulder crowns; pebbles at 60 % | rough 0.9 |
| `m044_rock_deep` | `#BFA192` (a step below `rock`, hue kept warm) | 18–24°, 0.20–0.26 | below 1.5 studs at 15 %; the wedge underside and back (hidden); pebble undersides by height | rough 0.9 |
| `m044_path` | **`#F7BB7B`** (f34 `#F8BB7B`, front `#FCC180`, top `#FABE7D`, swatch `#F4B676`) | 29–33°, 0.47–0.52, R > G > B | every tile top | rough 0.9, low spec |
| `m044_path_light` | `#FDC685` (lit) | 30–33°, 0.45–0.50 | broad patches at 20 % | rough 0.9, low spec |
| `m044_path_deep` | `#C68B5C` (tile sides f34 `#BC885B`, front `#CC8C5A`, cu3 `#C88A5C`) | 24–29°, 0.50–0.56 | tile bevels and sides at 50 % (role); within 0.6 of the borders at 15 % | rough 0.9 |
| `m044_grass` | **`#C2CD07`** (f34 `#C3CF06`, front `#BFCA06`, top `#C0CB08`, cu1 `#C1CC0A`) | 62–66°, ≥ 0.92, G > R > B | border tops and sides, aprons, default | rough 0.85, low spec |
| `m044_grass_light` | `#D8E106` (lit `#DAE205`) | 61–64°, ≥ 0.90 | broad patches at 20 % | rough 0.85, low spec |
| `m044_grass_deep` | `#A9B708` (shade `#AAB909`) | 64–68°, ≥ 0.90 | within 0.8 of bush roots and boulders; the apron's inner edge; at 25 % | rough 0.85, low spec |
| `m044_leaf` | `#43791C` (F medians `#41731C`–`#487E18`) | 90–98°, 0.75–0.82 | dark bushes' middle leaves | rough 0.85, low spec |
| `m044_leaf_lit` | `#7FB834` (fresh `#608316` → lit `#95D539`, lifted for our softer key light) | 78–86°, 0.70–0.83 | dark bushes' upper / outer tier at 60 % | rough 0.85, low spec |
| `m044_leaf_deep` | `#1B6A26` (h ≥ 95: `#196B25`, `#1A6222`, `#1F6C2D`) | 122–132°, ≥ 0.70 | dark bushes' inner / lower leaves at 60 % | rough 0.85, low spec |
| `m044_leaf_lime` | `#A6BC04` (sprig probes `#A9BC02`, `#8CBC09`) | 64–76°, ≥ 0.95 | sprigs, flower leaves | rough 0.85, low spec |
| `m044_flower` | **`#E8E018`** (f34 `#E5DD0D`, cu1 `#EAE51B`) | 56–59°, ≥ 0.85, R ≥ G ≫ B | yellow petals | rough 0.8, low spec |
| `m044_flower_heart` | `#ABA918` (cu1 centre probe, 59°, .86, .67) | 58–62° | flower centres | rough 0.8 |
| `m044_flower_white` | `#F3ECDA` (f34 `#F3EBD9`) | 35–50°, ≤ 0.12 | white flowers | rough 0.8, low spec |
| `m044_trunk` | `#6E3719` (trunks `#6F371A`, `#6E3714`, `#72371B`) | 19–25°, 0.75–0.85 | trunks, bush hearts | rough 0.95 |

**Calibration warnings:**
- **Rock:** calibrate `m044_rock` on the parts shot's cliff (warm faces) against `#D3B6A4`. Then check the f34_sheet
  warm-face median within 10 of `#D6B7A3` and the front_sheet within 10 of `#D2B6A5`; R > G > B, hue 15–26°. Whole-rock
  medians will run warmer than the sheet's (`#C6A898` f34) because our shade is warm, not lavender (M032 round 2, M040
  §5.4): a median within hue 15–26° that misses by ≤ 15 levels is a known miss, not a key error.
- **Path:** f34 path median within 12 of `#F8BB7B`, hue 29–33°, sat ≥ 0.45. It must read **warm sand**, clearly more
  saturated and orange than the rock (rock sat ≤ 0.26, path ≥ 0.45). Not brown, not pink.
- **Lawn:** f34 lawn within 14 of `#C3CF06`, hue 62–66°, sat ≥ 0.92. "Greens slightly grey" (M038) is the miss to avoid.
- **Leaves:** f34 bush F median within 14 of `#43791C`; the emerald tone at hue ≥ 120° and the fresh tone ≤ 88° both
  visible in the f34 crop ("lit foliage dark and less lime", M035; "back greens dark", M036).
- **Flowers:** within 14 of `#E5DD0D`, hue 56–59°.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Rock** (on the original facets, before any refine): `rock` base; `rock_light` by height within each column (faces
  with centre z above 0.65 of the column's apex, rising to 40 % at the top) and on the roof facets at 50 %; `rock_deep`
  by a noise field (scale ≈ 0.2) below 1.5 studs (15 %); per-column and per-boulder tint ±0.04.
- **Path:** `path` base; per-tile tint ±0.04; `path_light` by a noise field (scale ≈ 0.25) at 20 %; `path_deep` by role
  on the bevels and sides (50 %) and by distance to the border (< 0.6, 15 %).
- **Lawn:** `grass` base; `grass_light` by a noise field (scale ≈ 0.25) at 20 %; `grass_deep` by distance (to bush
  roots and boulders < 0.8) at 25 %. Average with neighbours before quantising (M034: no triangle shards).
- **Leaves:** by role in the bush: upper / outer tier `leaf_lit` 60 %, middle `leaf`, inner / lower `leaf_deep` 60 %.
- **Hard edges only** where materials meet: turf | tile (the overlap), turf | rock (the roof facets), leaf | trunk,
  petal | heart.

### 5.6 Texture (Tint) and finish

- **Tint:** rock amp 0.04, scale 0.3, per original facet; path 0.04 per tile plus 0.03 at scale 0.4; lawn 0.04, scale
  0.4; leaves 0.04 per leaf; petals 0.02; trunks none. Never per-triangle confetti.
- **Finish:** rock rough 0.9, metal 0; path rough 0.9, low spec; lawn and leaves `low_spec=True`, rough 0.85; petals 0.8;
  trunk 0.95. No emission anywhere.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Rock:** f34_sheet and front_sheet warm-face medians within 10 of `#D6B7A3` / `#D2B6A5`; parts-shot cliff warm median
  within 10 of `#D3B6A4`. All R > G > B, hue 15–26°, including the side view (mauve guard).
- **Path / lawn / leaves / flowers:** per the §5.4 warnings. **Shares** per §2.5.

## 6. Joins and contact (no floating dressing)

- **Tiles on the wedge:** every tile's underside sunk 0.02 into the wedge top (row 1's toe part on the ground at z 0);
  tiles touch their neighbours (gap ≤ 0.02). **No wedge visible** between tiles from any sheet camera.
- **Cliffs against the wedge:** each cliff's inner face at x ±4.0 overlaps the wedge's side (±4.1) by 0.1; the path
  edge tiles (x ±4.0) sit over the wedge, not over a crack.
- **Borders on path and cliffs:** the turf's inner 0.3 lies on the edge tiles (sunk 0.02, close-up 1's "simple
  overlapping edges"); its underside lies on the column tops (sunk 0.02); at the toe the tongue lies on the ground and
  the toe rock. **No crack** between turf and tiles, or between turf and column tops, from any camera.
- **Capping numbers (M032 round 1, the blocker; M040 §2.5).** From straight above, inside x ±8.0:
  - flat column top area (n.z > 0.85) not under turf: **0 studs²**;
  - visible rock: the roof-facet strips ≤ 1.1 wide per side (about 22 studs² a side), plus boulders, pebbles and the toe
    rocks; **total ≤ 60 studs²**;
  - wedge visible: **0**;
  - lawn visible ≥ 110 studs² (the two borders less the bushes); path visible ≥ 145 studs² (less pebbles and the turf
    overlap).
- **Back plane:** the wedge back, C6 backs, landing tiles' backs and border ends on y +10.0 within 0.001 (or relief
  inward); nothing behind it.
- **Plants:** roots on the turf (sink 0.03) or the ground; every leaf within 0.03 of its hub or trunk and chained by
  contact to the turf (STAGES: no hidden stems); every petal on its flower heart, every flower heart on the turf; leaves
  may touch rock but cut no more than 0.05 into it.
- **Count floating shells before reporting** (STAGES; 035 and 036 failed round 1 on this): **0**. A shell floats if its
  nearest distance to every other shell and the ground is > 0.03, or if it doesn't chain to the ground.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0 (bush hubs, petal centres, tile bevel corners).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** sunlit rock, sand tiles, lawns, bushes and flowers. No glow, light, sparkle, water, dust,
particles or VFX callout ("No baked lighting").
- **Stage 5 (lighting): skip, and record why.** No emissive faces, no PointLight. Studio notes (Requires Manual
  Validation):
  - the rock stays warm beige (not lilac) under the game's sun and matches an adjacent M040 tile;
  - the path reads warm sand, clearly separate from the rock;
  - the column facets read as separate planes (flat shading kept);
  - **a character walks from the ground to the landing and onto an M040 lawn without jumping or sliding**, with the
    game's default MaxSlopeAngle;
  - the borders stay yellow-lime, the flowers yellow.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** Not recommended: dust puffs on the path, pollen over
  the flowers.
- **Collision:** hero `precise` (the path walkable, the cliffs block); `StoneRampPath` `precise`; `StoneRampWedge`
  `hull` (a convex wedge); `StoneRampCliffL` / `R` `hull` (each mass is near-convex; the hull fills the roof tips by
  ≤ 0.9); `StoneRampBorderL` / `R` `none` (as W02's border: the bushes shouldn't snag, and the cliff and path below
  carry the walk surface within 0.3).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by searching `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json`, the
repo text (`git grep`) and every sheet / kit / wip `.blend` (zstd-decompressed) with `blendall.py`:
- **W02** owns `NaturalRamp`, `NaturalRampCurved`, `NaturalRampGrassBorder`, `NaturalRampGrassBorderRight`,
  `NaturalRampLandingPad`, `NaturalRampStraight`, `NaturalRampSwitchback`, `NaturalRampWedge` and
  `TerracedLedgeRampEnd`; they occur in `FlintbornWorldKit.blend`, `W02.blend` and every wip copy. Keys are `w02_*`.
- **W08** owns `BoardwalkRampEnd`.
- **M040** owns `StoneCliff*` (keys `m040_*`); **M043** plans `StoneTerrace*` (keys `m043_*`).
- **`StoneRamp` and `m044_` occur nowhere** in the repo text, the manifests or any `.blend`. (`RampWedge` occurs only
  inside W02's `NaturalRampWedge`.) `M.mk` would silently rename a clash to `<name>M044`; the names below don't clash.

| Object | Part | Why |
| --- | --- | --- |
| `StoneRamp` | hero: wedge + path + cliffs + borders + aprons + dressing | W02 owns `NaturalRamp`; parallels `StoneCliff`, `StoneTerrace`, `StoneSpire` |
| `StoneRampPath` | "Top Landing Pad (Path)": 14 tiles + pebbles | |
| `StoneRampWedge` | "Ramp Wedge (Stone)" | |
| `StoneRampCliffL` / `StoneRampCliffR` | "Left / Right Cliff Rock Mass" (+ toe rock) | |
| `StoneRampBorderL` / `StoneRampBorderR` | "Grass Border (Left / Right)" + their bushes, boulders, flowers, sprigs | |

- Palette keys `m044_*` (§5.4). Collection `Kit/M044 Natural Ramp`. No sockets.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1, §3.1): **16 W × 20 L, path 8 wide, from z 0.35 at the toe to 10.4, slope 29.9°, landing 2.5**
   (recommended: M040's pitch and plateau, the side cell's L / H 1.80 and 30.2°, the exploded / f34 width).
   - Or **14 W** (path 7): closer to the top cell, off the 16 pitch.
   - Or a **ground → 5.6** variant (M043's lower lawn): later, from the same builder with `RISE = 5.6` (decision 10).
2. **Constant width** (§3.3): **yes** (recommended; the taper is perspective). Or taper to 0.85 at the landing.
3. **Back and −X face** (§3.2): **a flat back plane on y +10 with shallow column relief; the −X cliff mirrors the +X
   with varied columns; rear / r34 judged as repeats** (recommended).
4. **Path tiles** (§2.2): **2 × 7 bevelled slab tiles, 0.6 thick, lips 0.08–0.12 between rows, toe lip 0.35**
   (recommended). Or one slab with grooves (cheaper, flatter; loses the sheet's chunky tiles).
5. **Borders** (§2.4, §3.5): **raised 0.3 over the path, overlapping its edge 0.3, lime sides, draped over the stepped
   columns; the landing segment is the last 2.5 of each border, lowering to 10.45 at the back plane** (recommended). Or
   a separate landing-border part.
6. **Column tops** (§2.3, §3.6): **peaked roof facets outside x ±7.0 (≤ 1.1 visible), stepping with apexes 0–0.3 above
   the turf at each column's downhill end; no flat exposed tops** (recommended). Or flat tops fully under the turf
   (M043's rule; loses the sheet's tips and the side cell's sawtooth).
7. **Packaging:** **one hero object of closed shells; six parts as the exploded labels; each cliff's columns unioned at
   the origin (merge-0), everything else separate shells** (recommended). Or the wedge and both cliffs as one unioned
   body (fewer hidden faces, but not the sheet's modular split).
8. **Seam contract** (§2.1): **sides on x ±8 (M040's seams), back plane y +10 placed on M040's lip front; landing and
   border ends at 10.4 / 10.45** (recommended).
9. **Comparison cameras** (§2.5): `f34_sheet (60, 15)` governing (probe az 50 / 60 / 68 × e 10 / 15 / 20);
   `front_sheet (0, 6)` (probe e 0 / 6 / 12); `side (90, 4)`; `top (0, 89)`; `rear_sheet (180, 6)` and
   `r34_sheet (−120, 15)` for the record. Extras: parts shot (−35, 25), wedge underside (e −35), `junc_cu (40, 30)`,
   `sect_cu`, the plateau shot with M040, the scale shot. Hide the floor in every `*_sheet` render.
10. **Builder parameter:** **write `m044.py` with `RISE`, `RUN`, `LANDING`, `W`, `PATH_W` constants**, build only 10.4
    now (recommended), so a 5.6 variant later is a parameter change, not a rebuild.
11. **Colour** (§5): **one warm beige stone `#D3B6A4` (R > G > B, never mauve), sand path `#F7BB7B` with role-darkened
    tile sides `#C68B5C`, lime lawn `#C2CD07`, two-tone bushes (`#7FB834` fresh / `#1B6A26` emerald, median
    `#43791C`), yellow flowers `#E8E018`, white `#F3ECDA`, trunks `#6E3719`; the brown "Rocks (Small)" swatch unused**
    (recommended). Blend by position, never by facing.
12. **Stages 5 and 6:** **skip both, recorded** (recommended).
13. **Collision** as in §7 (recommended).
14. **Budget** (§4.3): **4000 limit, plan about 3400, parts under 1000 with hero-only tags on the borders as needed**
    (recommended).
15. **Names** as proposed.

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **A thin strip on a thin slab (W02 `NaturalRamp`, `MODEL_PROGRESS` row 50).** The ramp is a **thick stepped stone
   mass**: the cliffs stand full height to the plateau at the back, the wedge fills under the path, and the side view
   shows four stepped blocks. Never a plank on stilts or a slab floating over the ground.
2. **The border as a table-top slab (M040 round 1, m1).** The border is not a uniform straight band: its green side
   varies 0.3–1.2 with the stepped columns, its outer edge scallops round the column tips, its inner edge is lobed
   ±0.15, and the bushes break its top line.
3. **Palm-star or spiky bushes (M040 m2; M039 round 1 blocker; M036 rounds 1–2).**
   - Dark bushes are round domes Ø 2.3–2.8 with a crown tier of 4–5 leaves pitched up and out; trunk ≤ 0.2 showing.
   - Leaves are broad rounded ovals: tip angle ≥ 110°, camber ≤ 0.07 L, no kite or diamond outlines.
   - **Edge-on leaves (M039 round 2, finding 1):** ≤ 12 % of leaf area within 12° of edge-on at the f34 camera, 0
     undersides showing; turn low leaves to the sides rather than toward the camera.
   - Petals are broad and rounded, lying on the turf.
4. **Floating dressing (STAGES; 035 and 036 round 1).** Every leaf, petal, flower heart, pebble and boulder within 0.03
   of a neighbour, its turf, a tile or the ground, chaining to the ground. Count floating shells: **0**. Pebbles sit in
   the tiles; flowers sit on the turf; bushes on the turf, not on the tiles' overlap edge.
5. **Turf that doesn't cap what it sits on (M032 round 1, the blocker).** No flat column top exposed; the turf covers
   every column top inside x ±7.0 and only roof facets ≤ 1.1 wide show outside; no wedge between tiles; no crack
   between turf and tiles (§6 numbers).
6. **Mauve or blue rock (M031, M032 rounds 1–2, M040 §5.3).** Every rock key R > G > B, hue 15–26°, R − B ≥ 30, in every
   view including the side. The lavender shade and Rock (Cliff / Stone) `#BDA8A1` are references only.
7. **Path reading as rock or as brown dirt.** The sand stays sat ≥ 0.45 (rock ≤ 0.26), hue 29–33°, value ≥ 0.9 on the
   lit tops.
8. **Colour by facing.** The peach-lit / lavender-shade split is the light. Height fields, noise patches, distances and
   roles only; `K.check` facing correlation < 0.5 per material (watch the tile-side role on the path).
9. **Egg boulders (M034 round 1; M037).** Boulders rounded-angular with a flat-ish crown and broad facets; toe rocks
   pointed; pebbles chunky. No ico-spheres, no `hull_rock` jitter balls.
10. **Lumpy columns or soccer-ball facets (M023, W02 "low smooth cliffs").** Columns are explicit prisms with tall strip
    facets (h/w 2.5–4.5), dark creases 0.3–0.5 deep and peaked roof tops. No subdivision, no smooth shading.
11. **An unwalkable or bumpy path.** Every row's downhill edge within ±0.02 of §2.1; slope 29.5–30.5°; row lips ≤ 0.12;
    toe lip ≤ 0.35; pebbles ≤ 0.25 tall. The landing exactly 10.4 and flat.
12. **Seams that don't fit the plateau.** Back-plane faces planar at y +10.0 ± 0.001; no rock past x ±8.0; landing 10.4
    and border ends 10.45 at the back plane; the plateau shot shows no gap or lawn step against M040.
13. **Lawns too dark, grey or olive (M035, M038).** f34 lawn within 14 of `#C3CF06`; the bushes keep both tones.
14. **Bowties** at bush hubs, petal centres, leaf roots and tile bevel corners: `M.fix_bowties` on every object,
    `nonmanifold_verts` 0.
15. **Exact booleans** (STAGES "Booleans"): only each cliff's columns, at the world origin, one at a time, saving between
    them. Nothing else is unioned.
16. **Budget.** Foliage and flowers are about half the count. The border parts are tight (≤ 1000): tag sprigs and
    white flowers hero-only before thinning a bush or the turf.
17. **Names and scope.**
    - No `NaturalRamp*` (W02), `StoneCliff*` (M040) or `StoneTerrace*` (M043).
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit `m040.py`, `m043.py`, `lib/vfx.py` or the shared helpers (frozen).

## Decisions (main session, 2026-10-29)
All 15 recommendations are accepted, with notes on 6 and 11.

1. **Size.** 16 W × 20 L. The path runs from z 0.35 to 10.4 at 29.9°, then a 2.5-stud landing at 10.4. The sides sit at x ±8.
2. **Width.** Constant along the ramp; the taper on the sheet is perspective.
3. **Back.** Flat, with shallow column relief. The far cliff mirrors the near one, with varied columns. Rear and r34 are judged as repeats.
4. **Path tiles.** 2 × 7 bevelled tiles, 0.6 thick, with row lips of 0.09–0.12 and a 0.35 lip at the toe.
5. **Borders.** Raised 0.3 above the path and overlapping it by 0.3, with lime sides, draped over the stepped columns.
6. **Column tops.** Peaked facets may show, but only in the outer strip, at most 1.1 wide, as the sheet draws them. **There must be no flat exposed column tops**, and the turf must cover everything inboard of that strip.
7. **Packaging.** One hero object made of closed shells, plus six parts. Only each cliff's columns are unioned, at the origin. Every shell is manifold with 0 bowties, and there is **no floating dressing**.
8. **Placement.** The back plane meets M040's lip front, and the landing meets the 10.4 plateau flush.
9. **Cameras.** As listed; `f34_sheet (60, 15)` governs.
10. **Builder.** `RISE` / `RUN` constants. Build only the 10.4 version for now.
11. **Colour.**
    - The tile sides `#C68B5C` are a geometric band: the faces below each tile's top bevel, picked by their place in the tile, never by normal direction. `K.check` must stay below 0.5.
    - Rock `#D3B6A4`: R > G > B, never mauve.
    - Path `#F7BB7B`.
    - Lawn `#C2CD07`.
    - Bushes are rounded two-tone domes, `#7FB834` / `#1B6A26`, with little trunk showing. Not palm stars, not spiky.
    - Flowers `#E8E018` / `#F3ECDA`. Trunks `#6E3719`.
12. **Lighting and VFX.** Both skipped, and recorded as skipped.
13. **Collision.** Precise on the hero and the path. Hull on the wedge and the cliffs. None on the borders.
14. **Budget.** 4000, with about 3400 planned.
15. **Names.** `StoneRamp*`, keys `m044_*`.

The f34 shares in §1 are binding within ±4.
