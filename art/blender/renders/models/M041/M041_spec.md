# 041 Shore Shelf — spec

Reference: `art/blender/assets/references/041.png` (1024 × 1536 px). The sheet's title is "35 / 132 | SHORE SHELF"
with "INDIVIDUAL ASSET PRODUCTION REFERENCE / STYLIZED • LOW-POLY • FLAT-SHADED • GAME-READY LOOK" at the top right; the
footer reads "FLINTBORN — INDIVIDUAL MODEL STUDY". INDEX.md row 41 calls it "Flintborn Shore Shelf Model Study" (the
printed 35 is the generator's number, not the index's).
Builder: `art/blender/kit/mcp/m041.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows water and foam** (§7); no glow, fire, flow streaks or particles.

Sheet text:
- **Cells:** "ASSEMBLED / FRONT THREE-QUARTER VIEW", "ASSEMBLED / REAR THREE-QUARTER VIEW", "ORTHOGRAPHIC VIEWS": "FRONT
  VIEW", "SIDE VIEW (RIGHT)", "REAR VIEW", "TOP VIEW". The "orthographic" cells are low elevated views (e ≈ 4–10°); the
  top view is a true plan (§3).
- **Exploded:** "EXPLODED CONSTRUCTION": "Grass Cap", "Main Rock", "Side Rock (Large)", "Side Rock (Medium)", "Side Rock
  (Small)", "Sand Shelf", "Water Plane". Dashed arrows drop the cap onto the main rock's summit, the main rock and
  four small rocks onto the sand shelf, and the side rocks onto the water plane (small black pins mark their spots).
- **Close-ups:** "CONSTRUCTION CLOSE-UP A — ROCK / SAND JUNCTION": "Rocks sit directly on sand shelf". "CONSTRUCTION
  CLOSE-UP B — UNDERSIDE VIEW (WATER PLANE)": "Flat water plane with simple thickness".
- **Material palette:** "Grass / Foliage", "Sand", "Rock", "Shallow Water". **No foam swatch** (the foam is drawn in
  every water view).
- **Modeling notes** (paraphrased): (1) simple chunky low-poly shapes with broad flat-shaded faces; (2) reusable rock
  pieces, sand shelf and grass cap; (3) rocks sit directly on the sand shelf, no complex blending; (4) the water is a
  separate flat plane with simple thickness; (5) bold readable forms in Flintborn's primitive low-poly style; (6) clean
  topology, no small detail geometry or texture noise.
- **Game context and the old kit:**
  - **W03 Shorelines, row 3 `ShoreIslet`** (`art/blender/scripts/kit/W03/shore_islet.py`, goals
    `art/blender/renders/kit/W03/shore_islet_goals.md`, manifest `art/roblox/kit/W03/manifest.json`) is the old kit's
    take on the same subject: "a small rocky island standing in open cyan water … on an octagonal (clipped corner)
    water slab", 32 × 32, about 16 tall, water z 1.0 over a seabed z 0.2, sand collar 1.6; foam as `water_foam`
    sockets only, a `water_flow` drift beam and two `vapour` spray sockets. `MODEL_PROGRESS.md` row 54 flags it "stack
    plain; no foreground boulders; foam over-stylised; variants weak". Reuse its levels, not its names (§8).
  - **M032 Shoreline Corner** (accepted): water z 1.0 over a bed z 0.2, sand 1.0 → 1.8, ridge grass top 10.4, a foam
    mesh on a `*water*` key plus `water_foam` sockets. **M034 Streambed Section** (accepted): banks 1.6, water 1.0, bed
    0.7, channel X −7 … +7 at its seams. Both share the waterline; this tile joins it (§2.1).
  - Later sheets on the subject: 161 "Shoreline wave and foam study".

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Cell paper `#FEFBF1` (254,
251, 241), tolerance 14. The cell labels and the exploded callouts are painted out (`TITLES` in `m.py`). Masks are
`cls()` in `m.py` (HSV, h in degrees; assigned in this order):
- **W, water:** h 178–215, s ≥ 0.45, v ≥ 0.55 (both the light and the deep tone).
- **G, green:** h 55–170, s ≥ 0.30, v ≥ 0.15 (turf, lime leaves, dark ferns).
- **F, foam:** (h 160–240 or s < 0.06), s < 0.45, v ≥ 0.88. White daisy petals leak into F (≤ 0.4 points).
- **S, sand:** h 22–55, s 0.22–0.80, v ≥ 0.66. A few warm-lit rock faces leak into S (≤ 0.5 points).
- **D, brown:** h < 45, s ≥ 0.30, v 0.15–0.66 (pebbles, the cap's soil band, buds).
- **R, rock:** (s < 0.25, v 0.20–0.90) or (h 200–300, s < 0.55, v 0.15–0.92: the blue-violet shade faces) or (h < 22 or
  ≥ 300, s < 0.30, v 0.20–0.90: the warm lit faces).
- **O, other:** outlines, dark crevices, red/pink buds, yellow flower centres. Not a target.
- **The sheet draws no ground shadow.** Measure our renders with the studio floor hidden (M034 §2.6).
- Cells: f34 (18,70,510,415); r34 (515,70,1006,415); front (18,478,286,689); side (290,478,519,689); rear
  (522,478,769,689); top (772,478,1006,689); exploded (18,730,676,1239); close-up A (681,745,1007,964); close-up B
  (681,1012,1007,1239). Swatches 36 × 36 px at x 33–69, y 1288 / 1331 / 1374 / 1417 (inner boxes in `m.SW`).

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m041_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14, Pillow, numpy).
- **Helpers:** `m.py` (masks `cls()`, boxes `V`/`X`/`SW`, `label()`, `preview()`), `zoom.py`, `grid.py` (zoom with a
  10-px sheet grid: `g_f34.png`, `g_f34L.png`, `g_f34R.png`, `g_main.png`, `g_front.png`, `g_r34.png`, `g_top.png`),
  `prev.py` (mask previews `cls_*.png`), `col.py` (pixel column probe).
- **Measurements:** `measure.py` → `measure_out.txt`, `bb.json` (silhouettes, shares, profiles, width per height,
  height fifths); `outline.py` (water-plate hulls per view); `plan.py` → `plan_out.txt` (hero inversion into plan
  positions, §2); `sandpoly.py` → `sandpoly_out.txt` (sand shelf outline from the top view); `rocks.py` →
  `rocks_out.txt`; `parts.py` → `parts.json` (exploded parts); `facets.py` → `facets_out.txt`, `facets.json`,
  `facets_*.png`; `square.py` → `square_out.txt` (hero shares and profiles if the plate were square, §3.2).
- **Colour:** `samp.py` → `samp_out.txt` (per cell: every class, rock warm / cool / lit, water light / deep, lime /
  dark leaf); `samp2.py` → `samp2_out.txt` (part regions, cap plants, foot clump); `sw.py` (swatches).
- **Zooms:** `z_f34.png`, `z_f34full.png`, `z_r34.png`, `z_row2.png`, `z_top.png`, `z_expl.png`, `z_expl_main.png`,
  `z_expl_rocks.png`, `z_cu.png`, `z_pal.png`.
- **On our renders:** `measure_render.py <render.png> [paper_hex] [--flip]` prints bbox, W : H, shares (W F S G R D O),
  profiles, width per height and per-class colour medians with these masks. It reproduces the sheet on the sheet's own
  cell (`selftest_f34.png`: W : H 1.548, W 37.2 / R 42.7 / G 6.9 / S 6.3 / F 3.0).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a modular water tile with an islet. Hero budget 4000 tris, each part under 1000. The
  plan in §4.3 lands at about 2500–3400.
- **Overall read (check this first).** A **flat cyan water plate with clipped corners** (an octagon in both hero cells)
  holding a **pale sand shelf** (an irregular oval, about 18 × 19, a low step above the water) on which stands **one big
  sea stack** (the main rock: a cluster of three or four tall flat-faced columns with a pointed spire and low shoulder
  blocks at its foot) **crowned by a small flat lime grass cap** with ferns, lime leaves, white daisies and red buds.
  **Six chunky flat-crowned side rocks** stand round the shelf, in the water or straddling its edge, each ringed by
  **soft lobed white foam**; a foam ribbon with round bubble holes runs along the whole shelf waterline. Two small rocks
  and a few pebbles sit on the sand; a fern clump with a daisy and a pink bud grows at the stack's front-left foot.
  - It must read as **one tall rock on a sand shelf in shallow water, with separate boulders round it**, not a rock
    pile and not a sculpted island: the sand is a flat slab, the water a flat plate, the foam a separate layer.
  - Hero shares (f34): water W 37.1 %, rock R 42.6 %, green G 6.8 %, sand S 6.2 %, foam F 3.3 %, brown D 0.3 %.
- **Focal silhouettes, in order:**
  1. The main rock's tower (f .34–.71 in the f34) with the grass cap and its plants on top (the cell's top, h .77 →
     1.0), and the spire leaning on its right flank (f .65–.74, apex h .63).
  2. The big flat-crowned front-left boulder FL (f .21–.44, crown h .44) with its low lodged block in front, and the
     tall back-right boulder BR (f .71–.87, crown h .74).
  3. The octagonal water plate: horizontal front and back edges, short vertical end edges, four 45° chamfers.
  4. The white foam ribbon round the shelf and the foam collars round every rock in the water.
- **Target size: plate 32 W × 28 D, water top z 1.0, sand shelf top 1.6, main-rock summit 10.0, turf top 10.4, plant
  tips about 13.2** (decisions §8.1, §8.2). Tolerances: plate exact; turf ±0.1; bbox height 13.2 ± 0.6.
  - **How it was derived.** The f34 hero is an orthographic-looking **elevated front view** (az ≈ 0, e ≈ 28°): the
    plate's front and back edges are horizontal on screen, its end edges vertical, and its four 45° chamfers read Δy/Δx
    = 0.46, 0.47, 0.49 (sin e) → e ≈ 28°. With the plate 32 wide (478 px, k = 14.94 px/stud), the front-to-back screen
    span (196 px) gives **D = 28.0**. Every other cell agrees on the plate's proportion: front cell 251 px wide and side
    cell 217 px deep at the same scale (7.8 px/stud) → D/W 0.865; top cell 220 × 197 → 0.895; hero 0.875. Heights come
    from the hero (`plan.py`, z = 1 + (396 − y − (Y + 14)·7.01)/13.19): main-rock summit (cap underside) **10.0**, C1
    tip 10.8–11.1, cap plants to 13.3; the r34 gives a summit of about 10.6. The low "orthographic" cells draw every
    height 12–35 % taller (front cell summit ≈ 13, side cell plant tips ≈ 17.7): a known redraw (§3.3).
  - **Why this size.** The plate width is the 32-stud terrain grid (M032, M034, W03); the depth follows the sheet in all
    six cells, as M032's 32 × 26 did. The turf at 10.4 is within the hero's measurement (10.4–11.1) and equals M032's
    grass top, so the kit's shore pieces share one plateau height as well as one waterline.
  - **Against the character (5.5):** the stack stands 8.4 above the sand (1.5 C), 12 wide at its foot; the cap is out
    of reach (a landmark, not a walkway); the shelf is 18–20 across (a small beach to stand on, 0.6 above the water);
    FL and BR are 4.3–4.5 above the water (0.8 C, cover-sized); the water is 0.8 deep over the bed (wadeable).
- **Build frame:** front −Y, +X right, ground z 0 = the flat underside. Plate X −16 … +16, Y −14 … +14. Origin = bbox
  bottom centre (the plate centre within ±0.1, because the plate is the widest thing in X and Y).

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | W | F | S | G | R | D | O |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (18,70,510,415) | 30–509 × 100–409 (480 × 310) | **1.548** | 37.1 % | 3.3 | 6.2 | 6.8 | 42.6 | 0.3 | 3.7 |
| Rear three-quarter (515,70,1006,415) | 528–1003 × 120–409 (476 × 290) | 1.641 | 31.4 | 2.8 | 8.1 | 8.4 | 45.1 | 0.3 | 3.8 |
| Front (18,478,286,689) | 28–280 × 516–669 (253 × 154) | 1.643 | 18.5 | 4.1 | 5.1 | 8.5 | 58.9 | 0.5 | 4.6 |
| Side, right (290,478,519,689) | 295–513 × 513–669 (219 × 157) | 1.395 | 17.1 | 3.5 | 3.7 | 10.2 | 61.1 | 0.3 | 4.2 |
| Rear (522,478,769,689) | 528–763 × 516–669 (236 × 154) | 1.532 | 16.8 | 3.2 | 7.6 | 10.2 | 57.6 | 0.2 | 4.5 |
| Top (772,478,1006,689) | 779–999 × 486–683 (221 × 198) | 1.116 (W : D) | 53.9 | 5.4 | 9.2 | 5.8 | 23.3 | 0.2 | 2.2 |
| Exploded (18,730,676,1239) | 37–660 × 730–1233 | — | 33.6 | 0.9 | 14.6 | 3.8 | 43.2 | 0.8 | 3.1 |
| Close-up A (681,745,1007,964) | full cell | — | 5.6 | 0.5 | 31.8 | 0 | 58.9 | 0.4 | 2.8 |
| Close-up B (681,1012,1007,1239) | 689–1000 × 1028–1187 | 1.950 | 56.6 | 0.6 | 13.4 | 1.8 | 24.6 | 1.3 | 1.7 |

- Shares are of the whole silhouette (O included). **Verifier tolerance:** W and R ±5, S and G ±2.5, F ±1.5 points;
  W : H ±0.06; positions ±0.04 of W / H unless stated.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .36 | .48 | .51 | .55 | .59 | .62 | .66 | .68 | .83 | .94 | .97 | .97 | .94 | .94 | .79 | .72 | .75 | .67 | .62 | .60 | .32 |
| r34 | .50 | .54 | .58 | .66 | .72 | .71 | .74 | .85 | .95 | 1.0 | .94 | .96 | .87 | .73 | .75 | .64 | .61 | .58 | .55 | .52 | .33 |
| Front | .16 | .33 | .44 | .43 | .35 | .43 | .70 | .84 | .92 | .96 | .96 | .92 | .93 | .80 | .57 | .53 | .61 | .62 | .50 | .31 | .28 |
| Side | .30 | .30 | .44 | .49 | .45 | .31 | .59 | .81 | .92 | .96 | .97 | .93 | .95 | .93 | .81 | .59 | .60 | .49 | .38 | .36 | .17 |
| Rear | .31 | .37 | .54 | .60 | .59 | .46 | .67 | .82 | .93 | .92 | .94 | .99 | .97 | .84 | .79 | .52 | .44 | .42 | .43 | .33 | .19 |

- Reading the f34: f .00–.35 is the plate's back-left chamfer and back edge (.36 → .66) with BL and L below it; f .40–.65
  the stack and its cap (.83 → .97, plant tips); f .70–.80 BR (.72–.79); f .85–1.0 the back-right corner (.67 → .32).

**Bottom profiles** (lowest silhouette pixel):

```
f34    .19 .16 .12 .09 .06 .02 .00 .00 .00 .00 .00 .00 .00 .00 .00 .00 .00 .02 .06 .10 .14
r34    .44 .20 .16 .12 .09 .05 .01 .00 .00 .00 .00 .00 .00 .00 .00 .04 .10 .15 .20 .26 .31
```

- The f34's flat bottom from f .30 to .80 is the plate's front edge; both ends rise along the front chamfers.

**Width per height** (silhouette width at h .05 → .95 as a fraction of W, @ left offset):

```
f34    .68@.20 .94@.06 1.0@.00 .99@.00 .97@.01 .83@.15 .58@.28 .42@.38 .27@.41 .16@.46
front  1.0@.00 .99@.00 .96@.04 .87@.06 .80@.11 .62@.27 .54@.29 .35@.32 .28@.36 .17@.42
side   1.0@.00 1.0@.00 .97@.00 .87@.08 .72@.11 .54@.30 .42@.32 .37@.34 .28@.38 .19@.43
rear   1.0@.00 1.0@.00 .97@.00 .89@.05 .81@.08 .63@.11 .43@.29 .39@.32 .30@.36 .22@.41
```

**Height fifths** (bottom → top, % of each class's pixels), f34: G 0 / 13.1 / 9.3 / 11.5 / **66.0** (the cap carries
two thirds of the green); R 5.2 / 28.3 / 37.8 / 27.6 / 1.1; S 0.3 / **85.4** / 13.3 / 0.3 / 0.8.

### 1.3 Silhouette and composition per view

**Front three-quarter (`g_f34.png`, `g_f34L.png`, `g_f34R.png`, `g_main.png`) — governs.** An elevated front view
(az 0, e ≈ 28°, §3.1). Positions below are the hero inverted into plan (`plan.py`): X = −16 + (x − 31)/14.94; the front
foot of each rock gives Y_front = (396 − y_foot − (z_foot − 1)·13.19)/7.01 − 14.
- **Water plate:** an octagon. Front edge y 409 (with the slab's side face) from x 160 to 420; back edge y ≈ 200 from
  x 190 to 440; end edges vertical at x 31 and 509; chamfer legs (studs) front-left 8.5, back-left 10.6, front-right
  6.1, back-right 3.7. The water is a flat two-tone cyan (deep `#01D7FD` 52 % of W, light `#40E8FD` 17 %), patches
  2–4 studs across.
- **Main rock** (f .34–.71): **three tall columns** — C1 at the left-back (x 190–262, a big shaded left face, its
  pointed bevelled tip at y ≈ 150–160, rising 0.4–0.7 above the turf at the cap's left), **C2 front-centre** (x 262–345,
  the biggest lit faces split by vertical creases at x ≈ 290 and 320, a flat top at the cap's front edge y 172), C3 at the
  right (x 325–365, tip y ≈ 160) — plus the **spire SP** (x 340–383, pointed apex y 215, foot on the sand y 297) leaning
  on C3's front, and lower stepped shoulder blocks at the right foot. Foot on the sand at y 312 (Y −3.2). Facets are
  tall strips (h/w 1.5–3.1); the largest single facet is 0.20 of the visible face (`facets.py` hMain).
- **Grass cap** (x 233–353, f .42–.67): a flat lime turf (top seen from y 127 to 172) with a thin darker green edge;
  dark fern rosettes at the back-left and front-centre, tall lime leaves at the back-centre and right, two white daisies
  with yellow centres, a red bud, a brown bud, small round teal leaves at the front-left. No brown soil band shows in the
  assembled views (it shows only in the exploded cap, §1.4).
- **Side rocks** (all chunky, flat or stepped crowns, 8–14 broad facets each, `facets.py`):
  - **FL**, front-left, the biggest: x 133–243, flat crown y 272 (h .44), straddling the shelf's front-left edge; a
    **low lodged block FLb** at its front foot (x 158–218, top y 336) standing in the water.
  - **L**, left: x 110–170, crown y 250, in the water at the shelf's left edge.
  - **BL**, back-left, small: x 157–190, top y 222, in open water.
  - **BR**, back-right, tall: x 373–448, flat crown y 180 (h .74), in the water just off the shelf's back-right edge.
  - **FR**, front-right: x 418–481, crown y 298, in the water, with a lower lodged step at its front-right.
  - **FS**, front-right small: x 377–412, top y 323, at the shelf's front-right corner.
- **Sand shelf:** pale cream sand (`#FEEFB7` open), visible in a broad band in front of the stack (y 300–352) and to its
  right (to x 420); its edge is a soft low step into the water, edged everywhere by foam. Two small rocks on it: **S1**
  (x 313–342, front) and **S2** (x 393–408, right); one pebble.
- **Foot plants:** a clump at the stack's front-left foot (x 197–262, y 250–310): broad lime leaves, dark leaves, a
  white daisy, yellow buds, a pink crystal-like bud; a thin green sprig in the C3/BR crease (x 362–375).
- **Foam:** a ribbon 0.8–1.6 wide along the whole shelf waterline with rows of round holes (bubbles), collars 0.6–1.4
  wide round FL/FLb, L, BL, BR, FR, FS, and small loose blobs. Soft lobed outlines, white `#C3F3FC` with a pale cyan
  edge. No blue gap between rock and foam.
- **Pebbles** (brown `#8B6136` or grey): in the water at (−9.5, −1.5), (−0.9, −9.2), (−0.8, −10.0), (11.6, 4.7), (10.8,
  −9.2), (11.2, −10.3); on the sand at (−0.8, −4.6).

**Rear three-quarter (`g_r34.png`).** The same island from behind (az ≈ 180, e ≈ 24–30°; the plate's chamfers read
inconsistently). The stack's back face shows two tall columns and a broad sand beach on its +X side (screen left), fern
clumps at the stack's back-left and back-right feet, a sprig by a front boulder, five side rocks and three sand rocks.
The rock arrangement does not invert cleanly onto the hero's plan (a rock at the screen's far left stands where the
hero puts FR): judge it loosely (§3.4).

**Front, side and rear cells (`z_row2.png`, `g_front.png`).** Low elevated views (front e ≈ 10°, side ≈ 4–5°) of the same
island. Each shows the stack with its cap and plants, two or three side rocks per side, the shelf's sand step and the
water band. **Every height is drawn taller than in the hero**: the stack's summit at z ≈ 13 (front cell) against 10.0,
BR's crown 8.4 against 5.5, L 6.2 against 3.6 (§3.3). The front cell shows a small teal flower in the foot clump.

**Top (`g_top.png`).** A true plan (no elevation shift; its front faces are painted on). The water plate is a rectangle
(W : D 1.116) with **one small chamfer at the front-right corner** (5 × 3 studs); the sand shelf is an oval ring round
the stack (X −8 … +10, Y −10 … +9, `sandpoly.py`); the stack with the cap in its middle (cap X −3.6 … +6.0, Y −2.1 …
+5.7); seven side rocks in foam: BR at the back-right, BL and L on the left, FL (with its lower block) at the
front-left, FR and FS at the front-right, a small one in front. Rock X positions agree with the hero within 0.5 for L,
FR, FS and FL; the stack is drawn 50 % wider, BR 3 studs further left and FS 4 studs further forward (§3.4).

**Close-up A — rock / sand junction (`z_cu.png`).** A side boulder and the stack's lower faces standing straight on
the flat sand; no skirt, no blending, no dark contact band; the shelf's top is flat with a few faint broad facets; its
edge is a soft low lip into the water, with a foam band on the water against it.

**Close-up B — underside (`z_cu.png`).** The island from below: the water plate's flat underside (blue `#029FD8` in
shade) with a straight bevelled edge; the sand shelf's flat octagonal bottom showing in the middle (`#BB9666` in shade);
the side rocks' bases dropping below the plate's underside; grass at the top. Read it as "flat bottoms, simple
thickness, separate plate".

### 1.4 Parts (Exploded Construction, `z_expl.png`, `z_expl_main.png`, `z_expl_rocks.png`, `parts.json`)

The exploded is an elevated view from the front-left; proportions agree with the hero (cap / stack width 0.67 against
0.62; shelf / stack 1.37 against 1.46). **The hero governs every size**; the parts give shapes and facet character.

| Part | Box (px) | Size px | Screen w/h | Shares | Facets (`facets.py`, ≥ 1 % regions) |
| --- | --- | --- | --- | --- | --- |
| Grass Cap | (265,730,419,798) | 155 × 69 | 2.25 | G 82, D 5.2 (soil sides), S 9.8 (flower centres) | — |
| Main Rock | (228,791,460,981) | 233 × 191 | 1.22 | R 98.6 | 12; largest 0.07; h/w 1.3–2.9 |
| Side Rock (Medium) | (121,846,216,953) | 96 × 108 | 0.89 | R 99.3 | 10; largest 0.17; width at h .7 / .9 = .72 / .33 |
| Side Rock (Large) | (480,854,585,934) | 106 × 81 | 1.31 | R 98.9 | 11; largest 0.16; width at h .7 / .9 = .72 / .22 |
| Side Rock (Small) and 5 more smalls | (37,1039,81,1085) …; 36–59 px | 45 × 47 | 0.96–1.08 | R 96–99 | 10; width at h .7 / .9 = .79 / .49 |
| Sand Shelf (with 4–5 small rocks) | (210,983,528,1098) | 319 × 116 | 2.75 | S 85.5, R 11.4 | — |
| Water Plane | (110,1070,660,1233) | 551 × 164 | 3.36 | W 97.9 | — |

#### Main Rock — exploded, hero, `g_main.png`
- **Shape:** **two or three tall flat-faced columns** standing side by side with a vertical crease between them, their
  tops at one flat level forming a **shallow summit tray** (lighter, the cap's seat) rimmed by the columns' bevelled top
  edges; **two small knobs** on the summit (hidden under the cap in the assembly: §3.6); **two low stepped shoulder
  blocks** at the foot (front-left and right front); in the hero, the spire on C3's front. Broad facets (12 regions
  over the visible body, the biggest 7 % of it), long vertical strips; never round.
- **Hero size: base 12.0 (X −5.5 … +6.5) × 11.0 (Y −3.5 … +7.5); summit z 10.0; tips C1 10.8, C3 10.6; spire apex
  7.2.**

#### Grass Cap — exploded, hero
- **Shape:** a **flat turf slab** with an irregular stepped (notched) outline, a lime top over **brown soil sides**
  (about 0.6 of the slab's side height is soil in the exploded), plants on top (2 dark fern rosettes, 2 tall lime-leaf
  rosettes, 2–3 daisies, a red bud, a brown bud, small round teal leaves).
- **Hero size: 8.1 (X −2.5 … +5.6) × 6.4 (Y +0.3 … +6.7) × 0.5** (underside 9.9, turf 10.4), plants to 13.2.

#### Side Rocks (Large / Medium / Small) — exploded, hero
- **Shape:** chunky boulders with **near-vertical lower sides, a broad base and a flat polygonal crown** (the Large one
  broad and squat, w/h 1.31; the Medium one taller with a small stepped knob on its crown, w/h 0.89; the Smalls rounded
  blocks w/h 1.0); 8–14 broad facets per visible side; the widest point low (h .3). **Not eggs.**
- **Hero:** FL (Large: 6.5 × 5.0 × 5.3), BR (Medium: 5.0 × 4.5 × 5.5), L, FR, FS, BL, FLb, FRb (Small family scaled
  0.5–1.0). Sizes in §2.3.

#### Sand Shelf — exploded, close-ups, top
- **Shape:** a **flat slab** with an irregular lobed / stepped outline (a notch at its right side in the exploded),
  straight vertical sides about 0.05 of its width tall, faint broad facets on the top; 4–5 small rocks sitting on it.
- **Hero size: about 18 × 19 (X −8 … +10, Y −10 … +9), top z 1.6**, its edge bevelled down to the water (§2.2).

#### Water Plane — exploded, close-up B
- **Shape:** a **flat plate with simple thickness** (a straight vertical side, about 0.03 of its length tall in the
  exploded), a two-tone cyan top (deep `#01CFFD` 67 %, light `#37E6FD` 18 %), no holes drawn, pins where rocks sit.
- **Hero:** the plate outline (§2.1) minus holes round the land; top z 1.0, bottom 0.25.

#### Plants (cap and foot) — `g_main.png`, `samp2_out.txt`
- **Dark fern rosette:** 6–8 narrow pointed leaves from one hub, arching out and up, dark green `#0B6A16`–`#126513` with
  lit tips `#21A157`. Ø 1.4–2.2, 1.0–2.0 tall.
- **Lime-leaf rosette:** 5–7 broad lanceolate lime leaves standing up (`#A0C908`, lit `#C8EA24`). Ø 1.6–2.0, 2.2–2.8 tall
  on the cap; Ø 2.5, 1.6 tall at the foot.
- **Daisy:** 6–8 white rounded petals (`#FBF8EE`) round a yellow disc (`#F5CD12`), Ø 0.8–1.1, on a short stem 0.3–0.5.
- **Buds:** red `#CF514B` (0.45 × 0.8 capsule), brown `#6D461D` (0.4), pink `#BC7CA3` crystal-like (0.5 × 1.0, foot
  clump), yellow `#E9BF03` drops (Ø 0.3, foot clump).
- **Sprig:** 3–5 upright thin leaves, Ø 0.8–1.2, 1.2–2.0 tall.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0). X and Y from the hero inversion (`plan.py`), heights from the hero
(§1.1), the sand outline from the top view checked against the hero.

### 2.1 The tile contract (binding; record it in the builder docstring and the export notes)

| Item | Value | Notes |
| --- | --- | --- |
| Plate outline | **X −16 … +16, Y −14 … +14, all four corners chamfered 7 × 7 at 45°**: (−9, −14) (9, −14) (16, −7) (16, 7) (9, 14) (−9, 14) (−16, 7) (−16, −7) | decision §8.2 |
| Seams | the straight edges: front and back **X −9 … +9**, ends **Y −7 … +7** | flat vertical faces |
| Ground / underside | **z 0**, one flat bottom for the whole tile | close-up B; M034 "flat bottoms" |
| Bed | **z 0 → 0.2** over the whole plate outline | `m041_bed` (no "water" in the key: solid, collides) |
| Water | **top z 1.0**, bottom 0.25, sides inset 0.02 from the plate outline | `m041_water`, see-through, no collision |
| Foam | **z 1.03 → 1.07** | `m041_water_foam` |
| Sand shelf top | **z 1.6** (flat crest), bevel to 1.15 at its edge, waterline where the bevel crosses 1.0 | |
| Main-rock summit / turf | **10.0 / 10.4** | M032's grass top |
| Rock bases | in water: on the bed (union, base z 0); on sand: sunk 0.3 (base 1.3) | |

- **The shared waterline.** At every seam the section is identical to M032's: bed 0 → 0.2, water 0.2 (0.25) → 1.0, flat.
  So this tile's straight edges meet M032's water edges (front X −4 … 16, right edge) and any open-water tile at one
  level. Against M034 (bed 0.7): the front or back seam's straight run (X −9 … +9) covers M034's whole channel (X −7 …
  +7), so a stream can run into the shelf tile; the bed steps 0.5 under the see-through water there (accepted; a later
  transition tile can hide it).
- **Corners.** The 7-stud chamfers leave a 14 × 14 diamond of open ground where four plates meet corner to corner. The
  shelf is an islet set into open water, so the main session decides whether that matters (§8.2: the square plate is
  the fully tileable alternative).
- **Nothing land crosses a seam:** every rock, pebble and the shelf stay ≥ 0.5 inside the plate outline (measured
  square to the nearest edge or chamfer); foam ≥ 0.3 inside.

### 2.2 Sand shelf, bed, water

| Piece | Outline / position | Levels | Sheet evidence |
| --- | --- | --- | --- |
| Sand shelf (waterline at z 1.0) | (−7.5, −1.5) (−6.5, −4.5) (−4.6, −6.3) (−2.6, −8.6) (0.5, −9.6) (4.0, −9.6) (6.6, −7.3) (8.5, −4.6) (10.0, −1.6) (10.0, 1.6) (8.2, 4.3) (5.5, 6.1) (3.1, 7.2) (0.5, 8.8) (−2.4, 8.0) (−5.0, 6.6) (−6.8, 4.2) (−7.5, 1.4) | crest 1.6, bevel band 0.6–1.0 wide down to 1.15 at the edge, side face 1.15 → 0 | top view `sandpoly.py`; hero front −8.9, right +10.0, front-left −7.9; close-up A lip |
| Bed | the plate outline | 0 → 0.2 | |
| Water | the plate outline inset 0.02, minus holes = the land's section at z 1.0 (shelf and every rock / pebble standing in water) offset 0.05, ≥ 12 corners per rock hole | 0.25 → 1.0 | close-up B; M034 lesson (§9.4) |

- Lobe the shelf outline a little between the points (±0.4, 2–3 studs per lobe) so it is not a smooth oval; keep the
  front-left edge under FL and the left edge under L (both straddle it).

### 2.3 Rocks (plan centre, footprint, base → top z; hero screen targets in f34 bbox fractions)

| Rock | Centre (X, Y) | Footprint w × d | Base → top z | Kind | f34 target (f; top h) |
| --- | --- | --- | --- | --- | --- |
| Main rock | (0.5, 2.0) | 12.0 × 11.0 at the foot | 1.3 → 10.0 summit (C1 tip 10.8, C3 tip 10.6) | columns, §2.4 | f .34–.71; rim h .77 |
| Spire SP | (6.2, 0.4) | 2.9 × 2.5 | 1.3 → 7.2 | pointed shard leaning 8° into C3 | f .65–.74; apex .63 |
| FL (front-left, Large) | (−5.5, −4.9) | 6.5 × 5.0 | 0 → 5.3 | Large, flat crown ≥ 35 % of plan | f .21–.44; crown .44 |
| FLb (lodged at FL's foot) | (−5.5, −8.7) | 4.0 × 2.5 | 0 → 2.9 | Small ×1.3, low block | f .27–.39; .24 |
| L (left) | (−8.7, 1.9) | 4.0 × 3.5 | 0 → 3.6 | Small ×1.5 / Medium ×0.8 | f .17–.29; .51 |
| BL (back-left) | (−6.5, 8.6) | 2.2 × 2.2 | 0 → 2.2 | Small ×0.8 | f .26–.33; .61 |
| BR (back-right, Medium) | (9.4, 8.4) | 5.0 × 4.5 | 0 → 5.5 | Medium (tall, stepped crown) | f .71–.87; crown .74 |
| FR (front-right) | (12.0, −5.8) | 4.2 × 3.8 | 0 → 4.1 | Medium ×0.8 | f .81–.94; .36 |
| FRb (lodged at FR's front-right) | (12.8, −7.9) | 1.8 × 1.4 | 0 → 2.3 | Small ×0.7 | — |
| FS (front-right small) | (8.3, −7.0) | 2.3 × 2.3 | 0 → 2.8 | Small | f .72–.80; .28 |
| S1 (sand, front) | (3.8, −5.9) | 1.9 × 1.6 | 1.3 → 2.9 | Small ×0.7 | f .59–.65; .31 |
| S2 (sand, right) | (8.7, 1.1) | 1.0 × 1.0 | 1.3 → 2.1 | Small ×0.4 | — |
| Pebbles in water ×4 | (−9.5, −1.5), (−0.9, −9.6), (11.6, 4.7), (10.8, −9.6) | 0.6–0.9 | on the bed (0.15) → 1.25–1.4 (0.25–0.4 above water) | 6–10-tri chunks, 2 brown | — |
| Pebbles on sand ×3 | (−0.8, −4.6), (2.0, −8.0), (7.2, −3.5) | 0.4–0.6 | 1.55 → 1.85 | | — |

- **Spacing:** at least 1.0 of water or sand between any two side rocks except the lodged pairs (FL/FLb, FR/FRb), which
  touch. FL's back leans 0.2 into the stack's front-left shoulder block.
- **Hero-vs-top differences** are listed in §3.4; the hero governs.

### 2.4 Main rock pieces (explicit prisms, M040 `column` style; union into the land shell)

| Piece | Plan (X, Y) | Size | Top | Notes | Hero evidence |
| --- | --- | --- | --- | --- | --- |
| C2 front-centre column | X −0.5 … +5.0, front ridge at (1.3, −3.6), back to Y +3 | 5.5 × 6.5 at the foot | **10.0 flat** (summit, under the cap's front half) | the biggest lit faces; a dark left facet 1.5 wide; 2 vertical creases on the front | x 262–345 |
| C1 left-back column | X −5.5 … −0.5, Y −2.0 … +7.5 | 5.0 × 9.5 | **tip 10.8** at (−3.0, 2.8), just outside the cap's left edge, bevelled (top faces ≥ 35° slope); inside the cap outline its top stays ≤ 9.95 | big shaded left face turned −X | x 190–262 |
| C3 right column | X +3.7 … +6.5, Y −0.5 … +7.0 | 2.8 × 7.5 | **tip 10.6** at (6.0, 0.4), just outside the cap's front-right corner, bevelled; ≤ 9.95 inside the cap outline | | x 325–365 |
| C4 back mass | X −3.0 … +5.0, Y +3.0 … +7.5 | 8.0 × 4.5 | **10.0 flat** (summit, under the cap's back half) | hidden from the front; the r34's back columns | r34 |
| LB front-left shoulder block | X −5.5 … −3.5, Y −3.8 … −1.5 | 2.0 × 2.3 | 3.5 | stepped low block (exploded); mostly hidden by FL and F1 | exploded |
| RB right shoulder block | X +5.5 … +7.8, Y +1.5 … +5.0 | 2.3 × 3.5 | 4.5 | between SP and BR | exploded, hero right foot |
| SP spire | §2.3 | | 7.2 apex | 4–5 sides, a stepped front facet | x 340–383 |

- **Batter:** the front face leans back strongly (front foot Y −3.5, summit front edge Y ≈ +0.1: about 20° from
  vertical), the left side 2 studs over the height, the back and right sides 0.5–1. The summit plane is offset to the
  back-right of the foot centre, as the hero and top view show.
- **Columns:** 6–7 sides each, one or two vertical splits per long face (a vertex at 0.35–0.65 H pushed ±0.15) so
  facets are tall strips (h/w 2–3), creases 0.3–0.6 deep between columns. No `K.hull_rock` jitter, no subdivision.

### 2.5 Grass cap and plants

| Piece | Position (X, Y), base z | Size | Notes |
| --- | --- | --- | --- |
| Cap slab | outline (−2.5, 0.5) (0.5, 0.3) (1.2, 0.8) (3.5, 0.4) (5.6, 1.2) (5.4, 4.0) (5.0, 6.4) (2.0, 6.7) (−0.3, 6.2) (−2.4, 4.6) (−2.0, 2.6), with 2–3 notches 0.3–0.5 deep | 8.1 × 6.4; underside 9.9, soil 9.9 → 10.25, turf 10.25 → 10.4 | overhangs the summit edge 0.1–0.3 at the front; covers the whole flat summit (§2.6) |
| P1 dark fern | (−0.8, 4.8), 10.4 | Ø 2.2, 2.0 tall, 7 leaves | back-left |
| P2 lime tall-leaf rosette | (1.0, 5.6), 10.4 | Ø 2.0, 2.8 tall, 6 leaves | back-centre; the cell's highest point |
| P3 lime rosette | (3.9, 5.0), 10.4 | Ø 1.8, 2.2 tall, 5 leaves | back-right |
| P4 small dark fern | (2.2, 1.6), 10.4 | Ø 1.3, 1.0 tall, 5 leaves | front-centre |
| Teal round leaves | (−1.0, 2.0), 10.4 | Ø 1.0, 0.6 tall, 4 round leaves | front-left |
| Daisies D1, D2, D3 | (0.6, 2.4), (3.0, 4.0), (4.4, 2.2), 10.4 | Ø 1.0 / 0.8 / 0.7 | |
| Red bud, brown bud | (0.2, 5.0), (−0.5, 3.6), 10.4 | 0.45 × 0.8; 0.4 | on short stems |
| F1 foot clump | hub (−1.8, −2.9) on the sand between FL's back-right and C1 / C2, 1.6 | Ø 2.8, 2.0 tall (leaves may lie on FL, ≤ 0.05 into it): 5 lime broad leaves, 4 dark leaves, daisy Ø 1.1, 3 yellow drops, pink bud 0.5 × 1.0 | between FL and the stack; f .35–.48 |
| F2 sprig | (6.8, 3.2), 1.6 | Ø 1.2, 2.0 tall | the C3/BR crease |
| B1 back clump | (5.0, 7.0), 1.6 | Ø 1.8, 1.4 tall | r34 |
| B2 back clump | (−3.5, 7.8), 1.6 | Ø 1.4, 1.2 tall | r34 |
| BR sprig | (7.2, 7.6), 1.6 | Ø 0.8, 1.0 tall | r34 |

### 2.6 Expected extents and screen checks

- **Extents (build frame):** X −16 … +16; Y −14 … +14; Z 0 … 13.2 (P2). Bbox 32.0 × 28.0 × 13.2.
- **Self-consistency at `f34_sheet (0, 28)`:** plate W : H 478 / 309 = 1.55 (sheet 1.548); P2 tip at y ≈ 98 (sheet top
  100); summit rim at h .77; FL crown h .44; BR crown h .74.
- **Checks on the renders** (floor hidden, `measure_render.py`):
  - **f34_sheet (0, 28)** (probe az −5 / 0 / +5 × e 24 / 28 / 32, keep the best): W : H 1.49–1.61; shares W 37.1 ± 5
    (expect about +1.3 from the regular chamfers), R 42.6 ± 5, G 6.8 ± 2.5, S 6.2 ± 2.5, F 3.3 ± 1.5; top profile within
    ±0.08 for f .05–.95 (expect +.07 at f .10–.25 from the regular back-left chamfer; f .00 and 1.0 excluded); bottom
    profile within ±0.05; G fifths top fifth 66 ± 10; each rock at its §2.3 f range ±0.04 and top h ±0.05.
  - **top (0, 89):** W : D 1.143 (sheet 1.116, record); shares loosely: W 48 ± 6 (the chamfers remove about 6 points
    against the sheet's square plate), R 23 ± 6, S 9 ± 4, G 6 ± 3, F 5.5 ± 2; seven side rocks round the shelf in
    foam; the cap in the stack's middle.
  - **r34_sheet (180, 26)** (probe e 22 / 26 / 30): W : H 1.58–1.70; shares loosely ±6: W 31.4, R 45.1, S 8.1, G 8.4.
  - **front_sheet (0, 10), side_sheet (90, 5), rear_sheet (180, 10):** shares loosely (±7); W : H will read wider than
    the sheet (front ≈ 1.77 against 1.643, side ≈ 1.75 against 1.395, rear ≈ 1.7 against 1.532) because those cells
    draw heights 12–35 % taller (§3.3). Record, don't chase.

### 2.7 Rock-shape targets (binding; check with `M.audit`, own bmesh code and `facets.py` on the renders)

| Target | Main-rock columns | Spire | Side rocks (FL, BR, L, FR) | Small rocks (FLb, FRb, FS, BL, S1, S2) | Pebbles |
| --- | --- | --- | --- | --- | --- |
| Tris each (before refine) | 40–64 | 16–30 | 50–80 | 24–40 | 6–12 |
| Facets visible from one side | 3–6 per column | 2–3 per side | **8–14** | 5–8 | 3–5 |
| Facet shape | tall strips h/w 2–3 | long triangles to the apex | broad, h/w 0.8–2 | broad | — |
| Top | summit flat at 10.0 under the cap; C1 / C3 tips bevelled | sharp apex | **flat crown: faces with n.z > 0.9 cover ≥ 30 % of the plan, 3–6 faces** | flat-ish crown ≥ 20 % | flat-ish |
| Profile (3D, of max width) | batter as §2.4 | — | **width at 0.7 h ≥ 0.85, at 0.9 h ≥ 0.70; widest at 0.2–0.4 h; base ring ≥ 0.9** | width at 0.7 h ≥ 0.8 | — |
| H : W | — | — | FL 0.8 (5.3 / 6.5), BR 1.1 (5.5 / 5.0), L 0.9, FR 1.0 (all from the bed; above the water 0.65–0.9) | 0.5–1.2 | 0.3–0.7 above water |
| Side faces within 25° of vertical | ≥ 80 % of side area | ≥ 60 % | ≥ 50 % | ≥ 40 % | — |

- **Irregular, not a pattern:** triangle-area CV ≥ 0.6; no vertex ringed by 5–6 near-equal triangles; no ico-spheres,
  no Fibonacci or UV-sphere rings, no subdivision or displacement.
- **Not eggs (M034 round 1):** on the f34 render each side rock's screen W : H above the water ≥ 1.0 (FL ≥ 1.2, BR ≥ 0.9;
  sheet hFL 1.07, hBR 0.96, hFR 1.16, hL 1.22), its crown reading as a flat lit polygon.
- **Capping (M032's lesson, §2.5):** rock faces with n.z > 0.85 above z 9.0 that are visible from above (not under
  the cap): **≤ 1.5 studs²** in all (the bevels of C1 / C3 tips slope ≥ 35° and don't count). The cap covers the whole
  flat summit.

## 3. View conflicts and resolutions

### 3.1 The f34 is an elevated front view

- **Evidence.** The plate's front and back edges are horizontal on screen and its end edges vertical; the chamfers read
  sin e = 0.46–0.49 (e ≈ 28°); the depth then comes out 28.0 for a 32-wide plate, matching the side and top cells.
- **Resolution.** Compare the hero with **`f34_sheet (0, 28)`** (probe az −5 / 0 / +5 × e 24 / 28 / 32) with the floor
  hidden; the kit front34 (−28, 12) is self-consistency only. Positions in §2 are this camera inverted.

### 3.2 Plate outline: octagon (hero, r34) vs rectangle with one chamfer (top, exploded) vs mixed (front, rear)

- **Evidence.** Hero and r34: four 45° chamfers (hero legs 8.5 / 10.6 / 6.1 / 3.7; the r34's read inconsistently).
  Top view: a rectangle with only the front-right corner clipped (5 × 3). Exploded water plane: a rectangle with a kink
  near the front-right. Front cell: the back-left corner reads clipped; rear cell: the front-left. No two plan sources
  agree on which corners are cut; the two governing hero cells agree that all four are. W03's `ShoreIslet` (the old
  kit's version of this subject) used an octagonal clipped-corner slab.
- **Resolution (decision §8.2).** **A regular octagon: all four corners chamfered 7 × 7** (the mean of the hero's legs
  is 7.2). It keeps the hero's and r34's read (shares within about 1–2 points, end profiles within ±0.08 for f .05–.95)
  and gives four straight, symmetric seam runs (X −9 … +9, Y −7 … +7) that chain with any straight water edge and
  contain M034's channel. Record the top view's square corners as a known miss (top W share about −6).
  - **Alternative A, square plate** (fully tileable): f34 shares become W 48.7, R 34.7, S 5.1, G 5.6, F 2.7
    (`square_out.txt`: +11.6 / −7.9 against the sheet) and the f34 top profile at f .00–.30 rises to .68 (sheet
    .36–.66). The hero would read as "a square of sea", not the sheet's diorama plate.
  - **Alternative B, the hero's irregular chamfers exactly:** closest to the hero, but the four seam runs differ in
    length and position, so tiles don't line up.

### 3.3 Heights: the hero and r34 vs the low "orthographic" cells

- **Evidence.** Hero summit 10.0 (rim) and C1 tip 10.8–11.1; r34 summit ≈ 10.6 (rim y 187, back foot y 318). Front cell
  summit ≈ 13 (+30 %), BR 8.4 (+53 %), L 6.2 (+72 %); side cell plant tips ≈ 17.7 (+34 %). The front and side cells are
  drawn at one scale (7.8 px/stud) and their plate proportions agree with the hero, so only their heights are stretched.
- **Resolution (decision §8.1).** **The hero governs heights** (summit 10.0, turf 10.4, M032's level). The front, side
  and rear cells are judged for content and order (which rocks where, plants at both feet), loosely for shares, and
  their W : H misses are recorded (§2.6). Alternative: turf 12.0 (splits the difference: hero top profile about +.05,
  front cell about −.065).

### 3.4 Plan: the hero vs the top view

- **Evidence** (`plan_out.txt` against the top view's plan, `rocks_out.txt`):

  | Item | Hero (plan) | Top view | Difference |
  | --- | --- | --- | --- |
  | Main rock foot, front | Y −3.2 | Y −6.9 | 3.7 |
  | Main rock width | X −5.3 … +6.7 (12.0) | X −7.1 … +10.6 (17.7) | top 48 % wider |
  | Cap | X −2.5 … +5.6, Y +0.3 … +6.7 | X −3.6 … +6.0, Y −2.1 … +5.7 | ≤ 2.4 |
  | BR | X 6.9 … 11.9, Y front +6.1 | X 3.3 … 9.2, Y +6.9 | X 3.3 |
  | FS | Y front −8.2 | Y −11.9 | 3.7 |
  | L / BL | Y front +0.1 / +7.5 | −1.9 / +5.3 | 2.0 / 2.2 |
  | FL, FR | X −9.2 … −1.8, Y −7.4 / X 9.9 … 14.1, Y −7.7 | X −10.1 … −3.6, Y −10.2 (lower block) / X 9.7 … 13.5, Y −7.6 | ≤ 1 |
  | Sand shelf | front −8.9, right +10.0 | front −10.0, right +10.0, back +8.8, left −7.5 | ≤ 1.1 |

- **Resolution (decision §8.3).** **The hero governs positions and sizes** (the M034 lesson: the hero is the read a
  verifier compares first, and the top view is a re-composition with a stack 48 % too wide for the hero); the top view
  gives the sand outline (it agrees with the hero within 1.1) and the count and order of rocks round the shelf. Judge
  the kit top loosely (§2.6) and record the stack size, BR and FS positions as known misses.

### 3.5 The rear three-quarter

- **Evidence.** Its rock arrangement doesn't invert cleanly onto either plan (rock sizes and positions shift by 3–5
  studs); it adds back-side fern clumps and a broad sand beach on the stack's +X back side.
- **Resolution.** Take the clumps B1 / B2 and the sprig (§2.5) and the visible back sand from it; compare
  `r34_sheet (180, 26)` loosely (§2.6).

### 3.6 Summit knobs (exploded) and the cap

- **Evidence.** The exploded main rock shows two small knobs on its summit tray; the cap's arrow drops onto one of them.
  In the hero the cap hides the tray; only C1's and C3's bevelled tips show beside it.
- **Resolution.** **No knobs on the summit**; a flat tray at 10.0 under the cap (the knobs would poke through the turf or
  leave a gap under it). Record as a known miss on the MainRock part.

### 3.7 The cap's soil band (exploded) vs the hero

- **Evidence.** The exploded cap has brown soil sides (D 5.2 % of the part); the assembled views show no brown band
  (D 0.3 % in f34, almost all pebbles).
- **Resolution.** Soil sides 0.35 tall under a 0.15 turf rim, the cap seated so its soil band sits **0.1–0.2 behind the
  columns' rims** at the back and sides and only its front 0.15 of turf edge overhangs (as M040's lip): the band shows
  on the part and in the exploded-style parts shot, not in the hero. f34 D ≤ 1.0 %.

### 3.8 Underside (close-up B) vs a flat-bottomed tile

- **Evidence.** The sheet's underside shows rock bases dropping below the plate's underside.
- **Resolution.** One flat underside at z 0 for bed, shelf and rocks (terrain grid placement, M034 decision). Paint the
  underside by region: under the shelf outline `m041_sand`, elsewhere `m041_bed` (blue, as the sheet's water underside
  reads). Record "rock bases don't protrude below the plate" as a known miss on `under_cu`.

### 3.9 Palette names against the renders

- **"Rock" `#BCB3B4` (353°, 0.05, B > G)** is a neutral grey on the mauve side: **never a key as it is.** The rendered
  rock is warm in its lit faces (`#C3B1AA` 17°, 0.13; lit v > .7 `#C6B4AE` 15°) and blue-violet in its shade faces
  (`#66708B` 224°): the lighting, not paint (52–64 % of rock pixels warm).
- **"Sand" `#EBC48C` (35°, 0.40)** is darker and more orange than every rendered sand (`#FDE4AB` exploded, `#FDE7AE`
  close-up A, `#FEEFB7` hero open sand, 42–48°, 0.28–0.33).
- **"Grass / Foliage" `#9DC82B` (76°, 0.79)** sits between the turf (`#B7DF02` lit lime, 71°, 0.99) and the lime leaves
  (`#A0C908`); the dark ferns (`#126513`, 120°) have no swatch.
- **"Shallow Water" `#00C7FE` (193°, 1.0)** is the deep tone; the rendered water is `#06DFFD` (187°), deep `#01D7FD`,
  light `#40E8FD`.
- **Foam has no swatch:** it renders `#C3F3FC` (189°, 0.23) with a lit `#E8FCFE` and a cyan edge `#95D4FA`.

### 3.10 "No complex blending, no texture noise" against the user's blended-colour rule

- The user's rule wins, quietly: broad lighter crowns and column tops, slightly deeper feet, whole-facet mottling,
  broad sand patches, two-tone water from the bed; no per-triangle confetti, no contact skirts, no dark contact rings
  ("Rocks sit directly on sand shelf").

## 4. Construction plan (stages 1–3)

1. **Parts first,** each from its own function and checked against its exploded cell:
   - `main_rock()` → `ShoreShelfMainRock`: C1–C4, SP, LB, RB (`column(spec)`, explicit prisms as `m040`/`m032`
     `column_pts`), unioned at the origin, floor-cut flat at z 1.3 (part) / sunk into the sand (hero). Compare with the
     exploded main rock (outline w/h 1.22 ± 0.08, 10–14 facets, a flat summit tray, two low shoulder blocks).
   - `grass_cap(dress=True)` → `ShoreShelfGrassCap`: the slab (`m032.cdt_region`/`slab` style: turf top CDT, soil
     sides, flat underside) + cap plants (`fern()`, `lime_rosette()`, `daisy()`, `bud()`, `round_leaves()`). Compare with
     the exploded cap (w/h 2.25 ± 0.2 on the parts shot, G ≥ 75 %, soil sides visible).
   - `side_rock(kind, w, d, h, seed)` → `ShoreShelfRockLarge` (FL), `ShoreShelfRockMedium` (BR, with the stepped crown
     knob), `ShoreShelfRockSmall` (FS): explicit ring stacks with a flat crown, M034 fix-round rings (`BIG_R` (0, .95, 7)
     (.45, 1.0, 7) (.85, .92, 6) (1.0, .74, 5)) as the starting point, more facets on the Large (60–80 tris, the M034
     round-2 note on plain RockLarge). Compare each with its exploded cell (w/h ±0.1, width at h .7 / .9).
   - `sand_shelf()` → `ShoreShelfSand`: the lobed outline slab with its bevel band, S1, S2 and the sand pebbles (each
     sunk 0.3 / 0.05). Compare with the exploded shelf (w/h about 2.75 in the parts shot).
   - `water_plane()` → `ShoreShelfWaterPlane`: the octagon water shell with its holes (hero copy) — and the bed is in the
     land shell, not here.
   - Render a **parts shot** (az −30, e 25) laid out like the exploded (cap above the stack, rocks round, shelf below,
     plate at the bottom).
2. **Hero:** bed + shelf + main rock + side rocks + pebbles-in-water in **one closed land shell** (union one piece at a
   time, largest first, at the origin; `m021._union_fine` for small rocks); the cap its own closed shell sunk 0.1 onto the
   summit; plants, sand pebbles each their own closed shells; water one closed shell; foam closed shells. `M.fix_bowties`
   on everything; origin at the bbox bottom centre; transforms applied.
3. **Foam** (`foam()`): flat closed shells 1.03 → 1.07, never touching land or water:
   - **Shore ribbon:** 4–6 segments along the shelf waterline (inner edge = the shelf's section at z 1.05 offset +0.04;
     outer edge 0.8–1.6 out, lobed, ±30 % radial jitter, 10–12 corners per 6 studs), soft rounded segment ends, 2–4
     round holes (Ø 0.3–0.6) per segment in a row parallel to the shore (the sheet's bubble rows).
   - **Collars:** one per in-water rock (FL+FLb as one, L, BL, BR, FR+FRb as one, FS): inner edge = the rock's section at
     z 1.05 + 0.03, **≥ 12 corners**, so there is no blue ring; outer edge 0.6–1.4 out, lobed (10–12 corners, ±30 %), a
     slight wake bias toward the open water.
   - **Blobs:** 8–12 loose ovals 0.3–0.8, within 3 studs of the shore or a collar, ≥ 0.1 off pebbles.
   - Foam may overlap itself only by merging into one outline (no stacked coplanar foam).
4. **Budget** (§4.3): hero about 2500–3400 (limit 4000); parts under 1000. If the hero goes over 3800, trim foam blob
   count and the back clumps first, never the rocks' facets or the cap plants.
5. **Placeholder keys** (stage 1): `m041_rock`, `m041_sand`, `m041_grass`, `m041_soil`, `m041_leaf`, `m041_bed`,
   `m041_water`, `m041_water_foam`. Stage 4 adds the rest (§5.4).
6. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** one tall faceted sea stack with a lime cap on a pale sand shelf in an octagonal cyan plate; six
      chunky flat-crowned side rocks round it in soft foam.
   2. **f34_sheet** against the hero (§2.6), every rock at its f range and top h.
   3. **top, r34_sheet, front/side/rear_sheet** loosely (§2.6, §3).
   4. **Rock-shape targets** (§2.7), all of them, on the parts and the hero.
   5. **Capping** (§2.7) and a **summit extra** `cap_cu (−20, 35)` framed on the cap: turf covering the summit, C1 / C3
      tips beside it, no flat grey shelf round the turf, no gap under it.
   6. **Junction extra** `junc_cu (−25, 22)` framed on FL and the stack's front-left foot against close-up A: rocks
      straight on flat sand, the soft shelf lip, foam on the water against it.
   7. **Water extra** `water_cu (−20, 40)` on FR/FS: collars hugging the rocks (no blue ring), ribbon holes, blobs.
   8. **Underside extra** `under_cu (e −30)` against close-up B (flat bottom; sand-coloured under the shelf, blue
      elsewhere).
   9. **Hero size** per §2.6; **scale shot** beside a 5.5-stud character marker standing on the shelf.
7. **Stage 2:** every shell closed and manifold: zero non-manifold edges and verts (`nonmanifold_verts` 0), boundary,
   wire and loose elements; no zero-area faces or n-gons; normals outward; no corners under 5° on visible faces; no
   decimation below §2.7. Seam faces planar (all water / bed verts on a seam run within 0.001 of its plane).
8. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density (leaves and pebbles included).

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Main rock (C1–C4, SP, LB, RB, unioned) | 1 | 260–380 | 260–380 |
| Bed (octagon, through the land union) | 1 | 40–80 | 40–80 |
| Sand shelf (CDT crest + bevel band + sides) | 1 | 160–260 | 160–260 |
| Side rocks FL, BR | 2 | 56–80 | 112–160 |
| Side rocks L, FR | 2 | 44–60 | 88–120 |
| Small rocks FLb, FRb, FS, BL, S1, S2 | 6 | 20–36 | 120–216 |
| Pebbles | 7 | 6–12 | 42–84 |
| Grass cap slab (turf + soil sides) | 1 | 60–100 | 60–100 |
| Cap plants (P1–P4, teal leaves, 3 daisies, 2 buds) | 1 set | | 380–520 |
| Foot clump F1 | 1 | 140–200 | 140–200 |
| Sprigs and back clumps (F2, B1, B2, BR sprig) | 4 | 30–70 | 150–250 |
| Water shell (octagon + holes for the shelf, 8 rocks, 4 pebbles) | 1 | 220–340 | 220–340 |
| Foam (ribbon segments + 6 collars + 8–12 blobs) | | | 600–850 |
| **Hero** | | | **about 2400–3400** (limit 4000) |
| Parts: MainRock / GrassCap / RockLarge / RockMedium / RockSmall / Sand / WaterPlane | | | 260–380 / 440–620 / 60–80 / 56–76 / 24–40 / 220–380 / 220–340 (limit 1000) |

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 26 × 26 box inside each, sd ≤ 1.8)

| Swatch | Box | Hex | HSV | Channel order | Use |
| --- | --- | --- | --- | --- | --- |
| Grass / Foliage | (38,1293,64,1318) | `#9DC82B` | 76°, 0.79, 0.78 | G > R > B | between turf and lime leaves; start for `leaf_lime` |
| Sand | (38,1336,63,1361) | `#EBC48C` | 35°, 0.40, 0.92 | R > G > B | too dark / orange; rendered sand is paler |
| Rock | (38,1379,63,1404) | `#BCB3B4` | **353°**, 0.05, 0.74 | R > B > G (mauve side) | **never a key as is** |
| Shallow Water | (38,1422,64,1449) | `#00C7FE` | 193°, 1.00, 1.00 | B > G > R | the deep tone; start for `bed` |

### 5.2 Rendered regions (`samp.py`, `samp2.py`; median / lit quartile / shade quartile)

| Region | Median | Lit | Shade |
| --- | --- | --- | --- |
| Rock, whole f34 / r34 / front / top / exploded | `#A5979D` / `#9F949A` / `#AD9DA1` / `#9B9097` / `#AA9A98` | `#CFBEB9` / `#CCBBB5` / `#CBBAB4` / `#CFC4C1` / `#CCBEBD` | `#5B6379` / `#596477` / `#616981` / `#575F75` / `#586279` |
| Rock warm faces (h ≤ 60 or ≥ 330) f34 / front / exploded / close-up A | `#C3B1AA` / `#C1AFA8` / `#B8A6A0` / `#B5A59C` (13–22°, 0.12–0.14) | `#D6C8C5` / `#D3C2BD` / `#D6C8C5` / `#D7CAC7` | `#AB9994` / `#A99891` / `#A3938E` / `#877B7D` |
| Rock lit (v > .7) f34 / r34 / exploded | `#C6B4AE` (15°, 0.12) / `#C6B5AE` / `#C2B1AC` | `#D7CAC8` | `#B9A69F` |
| Rock cool (shade light) f34 / exploded | `#66708B` / `#5E6A85` (222–224°, 0.27–0.29) | | |
| Warm share of rock: f34 / r34 / front / exploded / close-up A | 52 / 53 / 56 / 55 / 64 % | | |
| Exploded main rock / small rocks | `#AD9B98` (9°) / `#A59594` (4°) | `#CABAB6` / `#CDC2C6` | `#5B6579` / `#565F7B` |
| Sand: hero open / exploded top / close-up A / f34 all | `#FEEFB7` (47°, 0.28) / `#FDE4AB` (42°, 0.32) / `#FDE7AE` (43°, 0.31) / `#FDEEB4` | `#FEF4C1` / `#FDECB6` / `#FEECB6` | `#FDE1A5` / `#F6D396` / `#F2CE95` / `#E0BE93` |
| Sand underside (close-up B, shade) | `#BB9666` | | |
| Water: f34 / r34 / top / exploded plane / hero open | `#06DFFD` (187°, 0.98) / `#06DEFD` / `#09DEFD` / `#02D8FD` / `#03D9FD` | `#31E8FD` | `#01CEFD` |
| Water deep (s ≥ .97) / light (s < .85), f34 | `#01D7FD` 52 % / `#40E8FD` 17 % (front 40 / 29, top 46 / 22, exploded 67 / 18) | | |
| Water underside (close-up B) | `#029FD8` (196°, 0.99, 0.84) | `#1DD7FC` | `#018FCE` |
| Foam: f34 / r34 / top / hero front strip | `#C3F3FC` / `#C2F4FC` / `#C1F4FC` / `#C2F5FD` (188–189°, 0.23) | `#E8FCFE` | `#95D4FA` |
| Turf (cap, lime, v > .7) / cap whole G | `#B7DF02` (71°, 0.99, 0.87) / `#96C604` | `#C7ED05` | `#9AC903` |
| Exploded cap turf / soil sides | `#84B30C` / `#8F6531` (33°, 0.66) | `#B6E30F` / `#A17638` | `#126208` / `#775421` |
| Lime leaves: f34 lime mask / foot clump | `#ACD603` (72°, 0.99) / `#67A202` (82°) | `#C5EA06` / `#95CD01` | `#6A9705` / `#396302` |
| Dark leaves: f34 / cap / foot clump | `#126513` (120°, 0.82, 0.40) / `#0B6A16` / `#0D4007` | `#20A157` / `#219E44` / `#1F6914` | `#073906` / `#033006` / `#042701` |
| Daisy petals / centre | `#FBF8EE`–`#FEFDF8` / `#F9D213` (50°, 0.92) | | |
| Buds: red / pink / brown / yellow drops | `#CF514B` / `#BC7CA3` / `#6D461D` / `#E9BF03` | | |
| Pebbles (D) f34 | `#8B6136` (30°, 0.61, 0.55) | `#A28A66` | `#583C19` |

Deciles are not needed here: the rock and sand split cleanly into lit and shade.

### 5.3 How the colour works

- **Rock:** one warm pale grey (lit faces hue 13–22°, sat 0.12–0.14, **always R > G > B**) for the stack, every side rock
  and the grey pebbles. The sheet's shade faces are blue-violet (224°): the cool fill light. Our studio's shade is warm
  grey; that is light, not paint. **Never colour by facing.** A gentle painted signal by position: the stack's upper
  third and every crown a step lighter, the lowest 1.0 above the sand or water a step deeper; faces below z 0.95 (under
  the water) mixed toward the bed.
- **Sand:** one pale cream sand (42–47°, sat 0.28–0.33), broad lighter patches (`#FEEFB7`) on the open crest, a slightly
  deeper band on the bevel down to the waterline and a faint ring within 0.4 of rock feet (20 %). No contact skirts.
- **Turf:** a bright yellow-lime (70–73°, sat ≥ 0.95) with lighter patches; soil sides brown.
- **Leaves:** two plant types chosen per plant (not per face): **dark ferns** (115–125°, sat ≥ 0.75, value 0.38–0.45; lit
  tips toward `#21A157`) and **lime leaves** (72–82°, sat ≥ 0.95). White daisies with yellow discs; red, pink, brown and
  yellow buds as single small accents.
- **Water:** a saturated cyan plate over a **deep-blue bed with broad light patches** (the M034 method): the patches seen
  through the 0.3-transparent water give the sheet's two-tone (deep ≈ half the water, light ≈ a fifth).
- **Foam:** one pale cyan-white, see-through 0.2.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are medians of **unshadowed rendered regions** (lit rock faces, the exploded and close-up sand tops,
the open water), not swatches and not shade quartiles. `K.sample` kinds: `"stone"` for rock, `"brown"` for sand, soil and
pebbles, `"green"` for turf and leaves, `"vivid"` for lime leaves, flowers and buds.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m041_rock` | lit faces (v > .7, f34) `#C6B4AE` ± 10; warm faces `#C3B1AA`; start about `#A99891` (16°, 0.14) | 12–22°, 0.10–0.16, **R > G > B, R − B ≥ 14** | all rock, default | rough 0.85, metal 0 |
| `m041_rock_light` | about +12 levels over `rock` (lit quartile `#D7CAC8`, crowns) | 14–22°, 0.08–0.14, R > G > B | stack's upper 30 % at 35 %; crown faces of side rocks (top 25 % of their height) at 30 %; C1 / C3 tips | rough 0.85 |
| `m041_rock_deep` | a step below `rock` (warm shade quartile `#A99891`–`#AB9994` lifted) | 14–22°, 0.13–0.18, R > G > B | lowest 1.0 above the sand / water at 20 %; column creases at 25 % | rough 0.9 |
| `m041_sand` | `#FDE6AD` (exploded top `#FDE4AB`, close-up A `#FDE7AE`; start from the swatch `#EBC48C` lifted) | 41–46°, 0.29–0.34, R > G > B | shelf crest and sides, sand pebbles' neighbourhood | rough 0.95 |
| `m041_sand_light` | `#FEEFB7` (hero open sand; lit `#FEF4C1`) | 45–50°, 0.25–0.30 | broad crest patches at 35 % | rough 0.95 |
| `m041_sand_deep` | `#F2CE95` (close-up A / exploded shade quartiles) | 36–42°, 0.36–0.42 | the bevel band to the waterline at 35 %; within 0.4 of rock feet at 20 %; the shelf's underwater side | rough 0.95 |
| `m041_grass` | turf lime `#B7DF02` (cap v > .7); f34 lime mask `#ACD603` | 70–74°, ≥ 0.95, G > R > B | turf, default | rough 0.85, low spec |
| `m041_grass_light` | `#C7ED05` (lit) | 68–72°, ≥ 0.95 | broad turf patches at 25 % | rough 0.85, low spec |
| `m041_soil` | `#8F6531` (exploded cap sides); brown bud `#6D461D` | 28–34°, 0.6–0.7 | cap sides, brown bud | rough 0.95 |
| `m041_leaf` | `#126513` (f34 dark leaves; cap `#0B6A16`) | 115–125°, 0.75–0.90, v 0.38–0.45 | ferns, foot-clump dark leaves | rough 0.85, low spec |
| `m041_leaf_lit` | `#21A157` (lit quartiles `#20A157`, `#219E44`) | 130–150°, 0.75–0.85 | fern tips and upper tier at 40 %; teal round leaves | rough 0.85, low spec |
| `m041_leaf_lime` | `#A0C908` (front lime mask; foot clump `#67A202`; swatch `#9DC82B`) | 72–82°, ≥ 0.95 | lime rosettes, foot-clump lime leaves, sprigs | rough 0.85, low spec |
| `m041_petal` | `#FBF8EE` | s ≤ 0.06 | daisy petals | rough 0.8 |
| `m041_flower` | `#F5CD12` (centre `#F9D213`, drops `#E9BF03`) | 48–52°, ≥ 0.9 | daisy discs, yellow drops | rough 0.8 |
| `m041_bud` | `#CF514B` (red); pink `#BC7CA3` as `m041_bud_pink` | | red bud; pink crystal bud | rough 0.7 |
| `m041_pebble` | `#8B6136` | 28–34°, 0.55–0.65 | brown pebbles (3 of 7) | rough 0.9 |
| `m041_bed` | start `#00A0EA` (M034's calibrated bed `#0090E8`, lifted because this sheet's water is lighter and greener), tuned so deep water renders `#01D7FD` ± 15 | 195–200°, 1.0 | bed top; underside outside the shelf | rough 0.9, Specular IOR Level 0 (preview, M034) |
| `m041_bed_light` | start `#3FE1FD`; tuned so the light tone renders `#40E8FD` ± 15 | 186–190° | broad bed patches (2.5–4 studs, about 25 % of its area) | rough 0.9 |
| `m041_water` | start `#00B4E2` (M034 `#00ACDC`); rendered water median `#06DFFD` ± 12, s ≥ .9 (f34) | 186–192° | water shell | rough 0.15, `kit_transparency` 0.3 |
| `m041_water_foam` | start `#AAD0E6` (M034's calibrated foam); rendered median `#C3F3FC` ± 12, lit ≈ `#E8FCFE` | | foam shells | rough 0.6, `kit_transparency` 0.2 |

- The bed keys must **not** contain "water" (the exporter would make the bed a see-through, non-colliding piece); the foam
  key must (so foam exports as its own see-through piece). Hence `m041_water` and `m041_water_foam` only.

**Calibration warnings:**
- **Rock:** calibrate `m041_rock` on the parts shot's lit faces against `#C6B4AE`; check the f34_sheet lit-face (v > .7)
  median within 10 and hue 12–22°, R > G > B. The whole-rock median will run warmer than the sheet's `#A5979D` (334°)
  because our shade is warm grey, not blue (M032 / M034 residuals): a whole-rock median within hue 10–25° that misses by
  ≤ 15 levels is a known miss, not a key error. Never push shade faces blue by facing; never use the `#BCB3B4` swatch.
- **Sand:** keep the lit crest at s ≤ 0.34 (M032 finding 4: sand too saturated); f34 S median within 10 of `#FDEEB4`.
- **Water:** judge by the render, after tuning the bed (M034: the bed's sky glint, not the key, lifted the water's red;
  Specular IOR Level 0 on the bed fixed it). Targets: f34 W median within 12 of `#06DFFD`; ≥ 40 % of W pixels at
  s ≥ .97 and ≥ 15 % at s < .85.
- **Turf vs leaves:** keep the lime turf (70–74°) and the dark ferns (115–125°) ≥ 40° apart; the lime leaves sit between
  but read as leaves by shape.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Rock** (on the original facets, before any refine): `rock` base; `rock_light` by height (stack faces with centre z
  above 0.7 of the summit at 35 %; side-rock faces in the top 25 % of each rock's height at 30 %); `rock_deep` by height
  (faces centred within 1.0 above the sand or water at 20 %) and in the column creases (faces within 0.3 of a crease
  line, 25 %); faces wholly below z 0.95 → 50 % `rock_deep` / `bed` mix (seen through the water). Per-rock tint ±0.04.
- **Sand:** `sand` base; `sand_light` by a broad noise field (scale ≈ 0.3, about 3 studs) at 35 % on the crest;
  `sand_deep` by distance to the waterline (the bevel band) at 35 % and within 0.4 of rock feet at 20 %; the underwater
  side 100 % `sand_deep`. Averaged with neighbours before quantising (M034 fix: no triangle shards).
- **Bed:** `bed` base; `bed_light` by a broad noise field (2.5–4 studs) at about 25 %; within 0.5 of every rock foot and
  under the foam ribbon `bed_light` (so the gap under a collar's inner edge never reads as a dark ring).
- **Turf:** `grass` base, `grass_light` patches at 25 %, slightly deeper `grass` within 0.5 of plant roots.
- **Leaves:** by role in the plant (top tier `leaf_lit` 40 %, inner / lower `leaf`), ±0.04 tint per plant.
- **Hard edges only** where materials meet: rock | sand, rock | turf, turf | soil, leaf | petal, water | foam (separate
  shells).

### 5.6 Texture (Tint) and finish

- **Tint:** rock amp 0.04, scale 0.4, per original facet (a refined facet keeps one tone); sand amp 0.03, scale 0.15
  (broad, M034); turf 0.04, scale 0.4; leaves 0.04; bed 0.03, scale 0.8; water and foam none (the exporter textures
  water). Never per-triangle confetti.
- **Finish:** rock rough 0.85, metal 0; sand 0.95; turf and leaves `low_spec=True`, rough 0.85; flowers 0.8; water 0.15;
  foam 0.6; bed 0.9 with Specular IOR Level 0 (preview only). No emission anywhere.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Rock:** f34_sheet lit-face (v > .7) median within 10 of `#C6B4AE`, hue 12–22°, R > G > B; whole-rock median recorded
  against `#A5979D` (known warm miss ≤ 15). Side, rear and top medians too (mauve guard: R > G > B everywhere).
- **Sand:** f34 S median within 10 of `#FDEEB4`; parts-shot crest within 8 of `#FDE6AD`.
- **Water / foam:** f34 W median within 12 of `#06DFFD`, deep ≥ 40 %, light ≥ 15 %; F median within 12 of `#C3F3FC`.
- **Turf / leaves:** cap lime median within 12 of `#B7DF02` (v > .7); dark leaves within 14 of `#126513`.
- **Shares** per §2.6.

## 6. Joins and contact (no floating dressing)

- **Land shell:** bed (0 → 0.2) + shelf (0 → 1.6) + main rock + side rocks + in-water pebbles unioned into one closed
  shell, floor-cut flat at z 0. In-water rocks rise from the bed through the water holes; FL and L straddle the shelf
  edge (their bases cut at z 0, unioned with both bed and shelf); the main rock sinks 0.3 into the shelf. No rock
  standing on a point, no gap under any rock, no coplanar faces between bed top, shelf faces and rock bottoms (jitter
  rock bottoms 0.02–0.05 off slab levels). Union at the origin, one piece at a time, save between risky steps (STAGES
  "Booleans").
- **Cap on the summit:** the cap's underside (9.9) sits 0.1 into the summit tray (10.0), never coplanar; its outline
  covers the whole flat summit; C1 and C3 tips rise beside it (their bevels touch the cap's edge, no gap > 0.03).
- **Plants:** every leaf, petal, bud and disc chains by contact (≤ 0.03) to its plant's hub, and the hub sits on the
  turf (10.4, sunk 0.03) or the sand (1.6, sunk 0.03). Leaves may touch rock but cut no more than 0.05 into it. Daisy
  petals touch the disc; the disc sits on a stem that reaches the turf. Count floating shells before reporting (STAGES:
  035 and 036 failed round 1 on this): **0**.
- **Pebbles:** sand pebbles sunk 0.05 into the sand (separate shells); in-water pebbles part of the land union (they
  stand on the bed through the water).
- **Water:** one closed shell, top 1.0, bottom 0.25 (0.05 above the bed), holes round the shelf and every in-water rock
  and pebble offset 0.05 from the land's z 1.0 section: **never touches the land** (BVH overlap 0, min distance
  0.04–0.08).
- **Foam:** closed shells 1.03 → 1.07: ≥ 0.03 off the water top and ≥ 0.03 off the land; the inner edges hug the rocks
  and the shelf (median plan gap ≤ 0.08, M034 round-2 target); never touching a pebble.
- **Seams:** water and bed faces planar on the straight seam runs; nothing land within 0.5 of the plate outline.

## 7. Water, lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** flat two-tone cyan water, a white foam ribbon round the shelf and foam collars round the
rocks, all static. No flow streaks, glow, light, sparkle, mist, spray or particles. WorldModeling §12.3: separate land,
sand, water surface and foam; "a few broad strips or rings"; no z-fighting; "Record waterline and flow direction".

### 7.1 Water (export) and stage 5 (lighting)

- **How water exports** (`export_kit_roblox.py`): faces whose key contains "water" become separate see-through pieces,
  one per key (SmoothPlastic, the key's 512 × 512 tileable texture box-projected from the asset origin, `kit_transparency`,
  no collision, no shadow). **Expected STATS for the hero:** solid 1 (or 2 if over the cut size), **water 2**
  (`m041_water`, `m041_water_foam`), glow 0.
- **Waterline z 1.0; no flow direction** (a still shore: no streaks on the sheet).
- **Collision:** hero `precise` (a hull would box the whole plate and the stack); MainRock, the three side rocks `hull`;
  GrassCap `hull`; Sand `precise`; WaterPlane `none`.
- **Stage 5 (lighting): skip, and record why.** Nothing glows; no emission, no PointLight.
- **Studio notes (Requires Manual Validation):** the water's cyan and two-tone through the exported texture and
  transparency (the bed's Specular 0 is preview only); the foam's opacity at 0.2; the rock stays warm pale grey (not
  lilac) under the game's sun; the sand stays pale cream; a character can stand on the shelf and wade the 0.8-deep water.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py` (frozen for modellers)

- **`water_foam`** (emitter 6 × 1.5 patch box, flat): **13 sockets** at z 1.05, each on open water ≥ 0.5 off every rock
  footprint (M032 round 2: three shore sockets sat inside boulders), yawed along the local shore if the exporter honours
  rotation:
  - **shore, scale 0.7:** (0.5, −10.6), (4.2, −10.8), (10.9, −1.8), (10.6, 2.6), (4.0, 9.6), (−2.6, 9.0), (−8.6, −1.6);
  - **rocks, on their seaward side:** FL+FLb (−6.0, −11.4) 1.0, L (−11.4, 1.9) 0.7, BL (−6.5, 10.4) 0.5, BR (9.4, 11.4)
    0.9, FR+FRb (12.2, −9.1) 0.8, FS (8.3, −9.0) 0.5.
  - Check the export STATS line reports 13 sockets.
- **Not recommended:** `water_flow` (no streaks or current on the sheet; W03's drift beam was its own invention),
  `vapour` spray (W03), `waterfall_mist`, `dust`, any light.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by searching `art/blender/kit/mcp/*.py`, `art/blender/scripts`, every
`art/roblox/kit/*/manifest.json`, and every sheet / kit / wip `.blend` (zstd-decompressed) with the M035 study's
`blendall.py`:
- **W03:** `ShoreIslet`, `ShoreIsletGrassCap`, `ShoreIsletRockPieces`, `ShoreIsletSandCollar`, `ShoreIsletSeaStack`,
  `ShoreIsletLowIsland`, `ShoreIsletSteppingRock`, `ShoreIsletFoamRing`, sockets `VFX_ShoreIslet*`; keys `w03_*`.
- **M032:** `ShorelineCorner*`. **M034:** `StreambedSection*`. **Others:** `BoulderMainRock`, `MossyBoulderMainRock`,
  `StoneMainRock`, `StoneNodeMainRock`, `RockShelfTwoLevels`, `AmberShelf*`; `MainRock` and `SeaStack` occur as
  strings in every kit and wip blend (W03 / R01 / W01 objects).
- **`ShoreShelf`, `m041`, `SandShelf` and `ShelfRock` occur nowhere** in the repo text, the manifests or any `.blend`.
  `M.mk` would silently rename a clash to `<name>M041`; the names below don't clash.

| Object | Part | Why |
| --- | --- | --- |
| `ShoreShelf` | hero: plate, bed, shelf, stack, cap, rocks, plants, water, foam | the sheet's title; W03 owns `ShoreIslet` |
| `ShoreShelfGrassCap` | "Grass Cap": slab + cap plants | |
| `ShoreShelfMainRock` | "Main Rock": C1–C4, SP, LB, RB | bare `MainRock` strings exist elsewhere; prefixed is free |
| `ShoreShelfRockLarge` | "Side Rock (Large)" (FL's shape) | |
| `ShoreShelfRockMedium` | "Side Rock (Medium)" (BR's shape, stepped crown) | |
| `ShoreShelfRockSmall` | "Side Rock (Small)" (FS's shape) | |
| `ShoreShelfSand` | "Sand Shelf": shelf slab + S1, S2, sand pebbles | avoids the doubled `ShoreShelfSandShelf` |
| `ShoreShelfWaterPlane` | "Water Plane": the hero's water shell | |

- Palette keys `m041_*` (§5.4). Collection `Kit/M041 Shore Shelf`. Sockets `VFX_ShoreShelf_water_foam_N`.

**Decisions needed (a recommendation each):**
1. **Size and heights** (§1.1, §3.3): **plate 32 × 28, water 1.0 over a bed 0.2, shelf 1.6, summit 10.0, turf 10.4
   (M032's grass top), plants to about 13.2; the hero governs heights** (recommended: all six cells agree on the 0.86–0.93
   proportion; the hero and r34 agree on the summit; 10.4 is inside the hero's range), or a 32 × 32 grid tile (side W : H
   +0.2, hero W : H −0.12), or turf 12.0 (between the hero and the stretched orthographic cells).
2. **Plate outline** (§3.2): **a regular octagon with 7 × 7 chamfers; straight seam runs X −9 … +9 and Y −7 … +7**
   (recommended: the hero and r34 read, W03 precedent, symmetric seams that chain with straight water edges and contain
   M034's channel), or a square plate (fully tileable; f34 W +11.6, R −7.9, ends of the top profile +0.32), or the hero's
   irregular chamfers exactly.
3. **Plan source** (§3.4): **the hero governs positions and sizes; the top view gives the sand outline and the rock order,
   judged loosely** (recommended: the M034 lesson; the top view's stack is 48 % wider than the hero's), or the top view
   governs (the hero's stack, BR and FS would move 3–4 studs).
4. **Water stack** (§2.1): **bed 0 → 0.2 (solid, `m041_bed`), water 0.25 → 1.0 (`m041_water`, transparency 0.3), foam
   1.03 → 1.07 (`m041_water_foam`, 0.2)** (recommended: M032 and W03 open-water levels, identical seam sections), or
   M034's bed at 0.7 (a shallower stream look; a 0.5 bed step against M032).
5. **Packaging:** **one hero object: one closed land shell (bed, shelf, stack, side rocks and in-water pebbles unioned),
   the cap its own shell, each leaf / petal / bud / sand pebble its own shell, one water shell, foam shells; collision
   precise** (recommended: M032 / M034 water exception; every shell manifold, 0 bowties, 0 floating shells, the export
   shows 2 water pieces), or rocks as separate closed shells sunk 0.3 (no booleans; buried bottoms are hidden faces).
6. **Parts:** **seven: GrassCap, MainRock, RockLarge, RockMedium, RockSmall, Sand, WaterPlane** (recommended: the
   exploded's seven labels; no foam part, the sheet lists none), or add `ShoreShelfFoam` as M032 did.
7. **Foam and VFX:** **a restrained lobed foam mesh (ribbon with bubble holes, collars, blobs) plus 13 `water_foam`
   sockets; no `water_flow`, no `vapour`** (recommended: the sheet draws foam but no streaks or spray; M032 / M034
   precedent), or sockets only (W03's rework; the foam, 3–5 % of every view, would be missing from still renders).
8. **Summit** (§3.6, §3.7): **a flat summit under the cap, no knobs; the cap's soil band tucked behind the column rims**
   (recommended).
9. **Underside** (§3.8): **one flat bottom at z 0, painted sand under the shelf and bed blue elsewhere** (recommended).
10. **Stage 5:** **no emission or lights** (recommended: nothing glows).
11. **Comparison cameras** (recommended, §2.6): `f34_sheet (0, 28)` governing (probe az −5 / 0 / +5 × e 24 / 28 / 32);
    kit `top (0, 89)`, `r34_sheet (180, 26)`, `front_sheet (0, 10)`, `side_sheet (90, 5)`, `rear_sheet (180, 10)` loosely;
    extras: the parts shot (−30, 25), `cap_cu (−20, 35)`, `junc_cu (−25, 22)`, `water_cu (−20, 40)`, `under_cu (e −30)`
    and a scale shot with a 5.5-stud marker. Hide the floor in every `*_sheet` render.
12. **Colour:** **one warm pale rock (R > G > B, hue 12–22°, lit `#C6B4AE`), pale cream sand `#FDE6AD`, lime turf
    `#B7DF02`, dark ferns and lime leaves as two plant types, a deep-blue bed with light patches under cyan water, pale
    foam** (recommended); never the Rock swatch as a key, nothing by facing.
13. **Budget:** **4000 for the hero, planned at about 2400–3400; parts under 1000** (recommended).
14. **Names** as proposed; keys `m041_*`.

## 9. Pitfalls to avoid (lessons from recent verifier failures written as targets)

1. **A cap that doesn't cap (M032 round 1, the blocker).** The cap covers the whole flat summit: exposed flat rock
   (n.z > 0.85, z > 9.0, visible from above) ≤ 1.5 studs²; only C1 / C3 bevelled tips show beside it. The cap is a broad
   turf slab (8.1 × 6.4), not a strip or a pill floating over the rock.
2. **Water reading low (M032 round 2).** f34 W ≥ 33 % (sheet 37.1), the plate's chamfers no bigger than 7 × 7, the
   shelf no bigger than §2.2; top-view W ≥ 42. Don't let the shelf or the foam eat the open water.
3. **Egg-shaped boulders (M034 round 1).** Side rocks have near-vertical lower sides, a broad base and a flat polygonal
   crown (§2.7): width at 0.7 h ≥ 0.85 and at 0.9 h ≥ 0.70 of the max; crown faces n.z > 0.9 ≥ 30 % of the plan; screen
   W : H above the water ≥ 1.0 (FL ≥ 1.2). Big flat facets (8–14 per side), not a ring of small triangles.
4. **Outline foam and blue rings (M034 rounds 1 and 2).** Foam is soft and lobed (±30 % radial jitter, 10–12 corners per
   collar, rounded ribbon ends, bubble holes), its inner edge hugging the rock or shelf (median plan gap ≤ 0.08, ≥ 12
   hole corners); bed under collars `bed_light`. Foam median `#C3F3FC` ± 12, F 3.3 ± 1.5 % in f34.
5. **Top view vs hero (M034).** Don't move the stack, BR or FS to the top view's places; the hero governs (§3.4). Don't
   copy the front / side / rear cells' stretched heights (§3.3).
6. **Mauve or blue rock.** `#BCB3B4` (353°) and the blue shade (224°) are not paint. Every rock key R > G > B, hue
   12–22°, R − B ≥ 14. Check the side, rear and top rock medians too.
7. **Colour by facing.** Height, distance and noise fields only; `K.check` facing correlation < 0.5 per material.
8. **Floating dressing (STAGES; 035 and 036 round 1).** Every leaf, petal, bud and pebble within 0.03 of its hub, the turf,
   the sand or a rock, chaining to the ground or a rock; count floating shells: 0. Leaves are rounded clumps, not
   pointed ladders.
9. **Water or foam touching land, z-fighting, or colliding.** Water 0.25 → 1.0 with holes 0.05 off the land; foam 1.03
   → 1.07, ≥ 0.03 off water and land; the bed key without "water", the water and foam keys with it; the export STATS
   shows 2 water pieces.
10. **A W03-style plain stack.** W03's islet was flagged "stack plain": the stack is three or four distinct columns with
    dark creases, a spire, two shoulder blocks and bevelled tips (§2.4), 10–14 broad facets on its front.
11. **Too much sand or dark contact.** "Rocks sit directly on sand shelf": no skirts, no dark rings; contact deepening
    20 % at most, within 0.4.
12. **Bowties.** Fern hubs and daisy discs are where 019–021 grew bowtie vertices: each leaf and petal its own closed
    shell, `M.fix_bowties` on every object, `nonmanifold_verts` 0.
13. **Socket placement (M032 round 2).** Every `water_foam` socket on open water, ≥ 0.5 off any rock footprint.
14. **Exact booleans:** union at the origin, one piece at a time (largest first), water / foam / plants out of the union,
    save between risky steps.
15. **Names and scope.** Avoid W03's `ShoreIslet*` and bare `MainRock`; only one agent drives a Blender session at a
    time; no commits, pushes or exports in stage agents; don't edit `lib/vfx.py` or the shared helpers (frozen).

## Decisions (main session, 2026-10-29)
All 12 recommendations are accepted.

1. **Size.** A 32 × 28 tile, turf at 10.4 (M032's level). Heights come from the hero view; the taller orthographic cells are a recorded known miss.
2. **Plate.** A regular octagon with 7 × 7 corner cuts and straight edges at X −9…+9 and Y −7…+7.
3. **Plan.** The hero cell governs positions and sizes. The top view is used for the sand outline and the rock order only, and is judged loosely.
4. **Water layers.**

   | Layer | Key | z range | Transparency |
   |---|---|---|---|
   | Bed | `m041_bed` (no "water" in the name) | 0 → 0.2 | solid |
   | Water | | 0.25 → 1.0 | 0.3 |
   | Foam | | 1.03 → 1.07 | 0.2 |

5. **Packaging.** One hero object, collision precise:
   - one land shell (bed, shelf, stack and side rocks unioned);
   - the cap as its own shell;
   - each leaf, petal and pebble as its own shell;
   - one water shell and the foam shells.

   Every shell must be manifold with 0 bowties. **No floating dressing** (STAGES rule). Water and foam never touch land, and there is no blue ring between the foam and the rocks.
6. **Parts.** The seven proposed (`ShoreShelfGrassCap`, `…MainRock`, `…RockLarge`, `…RockMedium`, `…RockSmall`, `…Sand`, `…WaterPlane`). No foam part.
7. **Foam and VFX.** A lobed foam mesh plus 13 `water_foam` sockets on open water, each ≥ 0.5 from rocks. No `water_flow` or vapour.
8. **Summit.** Flat under the cap, no knobs. **The cap must cover the whole flat summit** (M032's lesson).
9. **Underside.** One flat bottom at z 0.
10. **Lighting.** None.
11. **Cameras.** `f34_sheet (0, 28)` governs; the other cells are judged loosely. Include the listed extra shots.
12. **Colour.**
    - Rock: warm pale grey with R > G > B, lit faces `#C6B4AE`. Never the mauve swatch `#BCB3B4`, never B > G.
    - Sand `#FDE6AD`, turf `#B7DF02`.
    - Two separate plant types.
    - Water median `#06DFFD` with a two-tone bed, as in M034. Foam `#C3F3FC`.
    - Blend by position, never by facing.

**Binding targets.** The f34 shares in §1 hold within ±4. Water must stay ≥ 33 % of the f34 view. The side rocks must meet their flat-crown and wall-steepness targets, so they don't read as eggs.
