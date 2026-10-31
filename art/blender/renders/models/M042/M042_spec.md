# 042 Young Fir — spec

Reference: `art/blender/assets/references/042.png` (1024 × 1536 px). The sheet's title is "YOUNG FIR", "PAGE 46/132",
with "STYLIZED LOW-POLY TREE ASSET / SIMPLE FORMS · BROAD FACES · CLEAN SILHOUETTE" at the top right; the footer reads
"FLINTBORN — INDIVIDUAL MODEL STUDY". INDEX.md row 42 calls it "Young Fir Model Study" (the printed 46 is the
generator's number, not the index's).
Builder: `art/blender/kit/mcp/m042.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7). Trees: "a detailed skeleton plus foliage clumps; roots,
branches and every view matter" (memory `kit-tree-detail`). Here the skeleton is the trunk and its roots; the sheet
draws no branches (§3.9).

Sheet text:
- **Cells:** "FRONT 3/4 VIEW", "REAR 3/4 VIEW", "MATERIAL PALETTE", "ORTHOGRAPHIC VIEWS (CONSISTENT GEOMETRY)": "FRONT",
  "SIDE", "REAR", "TOP". The orthographic cells are low elevated views (e ≈ 6–10°), the top a true plan (§3.1).
- **Exploded:** "EXPLODED PARTS & ASSEMBLY": "CROWN TIER", "MIDDLE TIER", "LOWER SKIRT", "TRUNK", "ROOT BASE". Dashed
  arrows drop the crown onto the middle tier, the middle onto the skirt, the skirt onto the trunk's flat top, the trunk
  onto the root base, and two loose plant clumps onto the base between three rocks.
- **Close-ups:** "FOLIAGE TIER (UNDERSIDE)" with inset "JOINING SURFACE DETAIL": "FLAT JOINING SURFACE FOR STACKING".
  "TRUNK TOP DETAIL" with inset "TRUNK CROSS-SECTION": "FLAT TOP SURFACE FOR FOLIAGE TIER". "ROOT BASE DETAIL" with an
  inset: "TRUNK TO ROOT JUNCTION / SIMPLE ANGLED FORMS".
- **Material palette:** "FOLIAGE DARK", "FOLIAGE MID", "FOLIAGE LIGHT", "TRUNK", "ROCK", "GROUND PLANTS". **No sand /
  ground swatch** (the sand patch is drawn in every side view and the root close-up).
- **Modeling notes** (paraphrased): three reusable foliage tiers (crown, middle, lower); one trunk piece; a separate
  root base with rocks and plants; broad flat-shaded faces; a clean silhouette with simple forms; no textures or noise,
  solid colours only (§3.10).
- **Game context and the old kit:**
  - **W04 Pines & Firs, row 2 `YoungFir`** (`art/blender/scripts/kit/W04/young_fir.py`, goals
    `art/blender/renders/kit/W04/young_fir_goals.md`, manifest `art/roblox/kit/W04/manifest.json`) is the old kit's take
    on the subject, from a different reference row: 11 × 11 × 17, three tier groups of pleated cones, a reddish trunk
    visible for the lower third, a leaning boulder, one `w04_needle` key. `MODEL_PROGRESS.md` row 57 flags it "fat dark
    tiers; trunk hidden; variants similar"; its goals record H11 (chunky overlapping flaps with darker undersides) and
    P2 (canopy dark and low contrast, not lime) as unmet. **W04 owns every `YoungFir*` name** (§8).
  - **Kit pines already built:** M032 (`m032.pine`, four 5-point star tiers, 5-sided trunk) and M037 (`m037.pine`, 3–4
    star tiers stacked by ray-cast contact, 4-sided trunk). §4.4 lists what to do better.
  - Later sheets on the subject: 045 "pine sapling", 047 "Old Pine", 049 "Classic Pine", 094 "Snow Pine". Keep the
    sizes in order (§1.1).

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Cell paper `#F7F3E9` (247,
243, 233), tolerance 14. Labels and callouts are painted out (`TITLES` in `m.py`). Masks are `cls()` in `m.py` (HSV, h
in degrees; assigned in this order):
- **X, cast shadow (not silhouette):** (s < 0.07, v ≥ 0.78) or (s < 0.08, v ≥ 0.70, B ≥ R − 3). The sheet draws a
  lavender ground shadow to the left of every side view and to the lower left of the top view; `silhouette()` also
  drops outline pixels within 3 px of it.
- **G, green:** h 50–180, s ≥ 0.25, v ≥ 0.10 (needles and ground plants).
- **S, sand:** h 30–52, s 0.22–0.47, v ≥ 0.80.
- **T, trunk / bark:** h < 45, s ≥ 0.35, v ≥ 0.15.
- **R, rock:** s < 0.30, v 0.25–0.95 (the warm lit faces and the blue-grey shade faces).
- **O, other:** outlines, the darkest creases. Not a target.
- Cells (inset 3 px from the borders): f34 (25,100,442,462); r34 (450,100,830,462); front (25,500,276,742); side
  (283,500,508,742); rear (515,500,741,742); top (748,500,999,742); exploded (25,785,524,1372); tier underside
  (528,782,1002,1028); trunk top (528,1035,1002,1233); root base (528,1240,1002,1497). Swatch inner boxes 26 × 28 px at
  x 856–882, y 143 / 194 / 245 / 296 / 347 / 398 (`m.SW`).

**Scratch study material** (no Blender), in
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m042_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14, Pillow, numpy).
- **Helpers:** `m.py` (masks `cls()`, `silhouette()`, boxes `V` / `X` / `SW`), `zoom.py` (crop with a 10-px sheet grid),
  `px.py` (pixel probe), `rows.py` (per-row class extents), `blendall.py` (name search in every `.blend`).
- **Measurements:** `measure.py` / `measure2.py` (bbox, W : H, shares, top profile, width per height, G / T fifths),
  `tiers.py` (hem and waist rows per view), `topang.py` (plan star points), `parts.py` (exploded parts), `hemtips.py`.
- **Colour:** `sw2.py` (swatches), `samp.py` (canopy per tier and per half), `samp2.py` / `samp3.py` (trunk, rock, sand,
  plants, hub, cut top; lit v > .7 and half medians).
- **Zooms:** `z_f34.png`, `z_r34.png`, `z_ortho.png`, `z_front.png`, `z_top.png`, `z_topcrown.png`, `z_expl.png`,
  `z_expl_low.png`, `z_cu.png`, `zb_f34.png`, `zb_r34.png`, `zb_front.png`, `zb_side.png`, `zb_rear.png`; mask
  previews `cls_*.png`.
- **On our renders:** `measure_render.py <render.png> [paper_hex] [--flip]` prints bbox, W : H, shares (G T S R O),
  profiles, width per height and per-class colour medians with these masks. It reproduces the sheet on the sheet's own
  cell (`selftest_f34.png`: W : H 0.817, G 72.6 / T 12.8 / R 8.7 / S 3.4).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a standalone conifer with its own ground patch. Hero budget 4000 tris, each part
  under 1000. The plan in §4.3 lands at about 2300–2900.
- **Overall read (check this first).** A **slim, stepped green spire of three stacked foliage tiers** — a pointed
  **crown** cone with a hem of flaps, a **middle tier** and a widest **lower skirt** — each tier a ring of **broad,
  pointed, drooping leaf flaps with a raised midrib**, two rows deep, lapping over the tier below with a dark shadow
  band under each hem. Below the skirt a **chunky, faceted, orange-brown trunk** (visible for the lower ~0.28 of the
  height) **flares into six angular roots** that run out over a **thin, irregular, pale sand patch**, dressed with
  **chunky pale grey rocks** and **clumps of upright lanceolate ground plants** (lime and green).
  - It must read as **three distinct tiers on a visible trunk**, not a smooth cone, not a pagoda of flat rings and not a
    blob: the outline steps in at two waists, every tier edge is a row of separate flap points.
  - Hero shares (f34): green G 72.5 %, trunk T 12.8 %, rock R 8.7 %, sand S 3.4 %.
- **Focal silhouettes, in order:**
  1. The spire outline: apex, the crown hem (0.48–0.50 of the canopy width), the first waist, the middle hem (0.71–0.75),
     the second waist, the lower hem (1.0).
  2. The ragged hem of flap points on each tier, the outermost drooping below the notches.
  3. The trunk and its root flare under the skirt; the warm orange lit side against the dark brown shade side.
  4. The base: two grey rocks in front, plant clumps left and right, the pale sand patch.
- **Target size: 16.0 tall (apex), canopy tip-to-tip 12.0 (silhouette 11.2–11.8), trunk Ø 2.0–2.1 under the skirt,
  ground patch about 13 × 11** (decision §8.1). Tolerances: height ±0.3, canopy silhouette W 11.5 ± 0.5.
  - **How it was derived.** Five side views agree on the proportions (`tiers.py`, fractions of the full height H,
    ground front edge to apex):

    | Feature | f34 | r34 | front | side | rear | adopted (z, studs) |
    | --- | --- | --- | --- | --- | --- | --- |
    | Crown hem (widest) h / width of canopy | .754 / .48 | .732 / .49 | .734 / .50 | .734 / .50 | .736 / .48 | z 11.6, plan tips r 2.9 |
    | Waist crown / middle h / width | .740 / .34 | .718 / .32 | .716 / .32 | .716 / .32 | .716 / .33 | z 11.2, visible r 1.8 |
    | Middle hem h / width | .612 / .71 | .585 / .68 | .574 / .73 | .576 / .73 | .583 / .75 | z 9.0, plan tips r 4.2 |
    | Waist middle / lower h / width | .567 / .47 | .538 / .48 | .537 / .46 | .528 / .48 | — | z 8.4, visible r 2.6 |
    | Lower hem h / width | .356 / 1.0 | .358 / 1.0 | .336 / 1.0 | .343 / 1.0 | .334 / 1.0 | z 5.0, plan tips r 6.0 |
    | Lowest canopy pixel h | .275 | .270 | .262 | .266 | .253 | front tips z ≈ 4.5 |
    | Canopy W / H | .656 | .666 | .696 | .643 | .678 | 11.5 / 16 = .72 (.70 on screen) |

    In the near-level front cell (e ≈ 8°, §3.1) the ground's front edge lies about 0.8 below the trunk foot, so
    13.8 px/stud; heights from it: crown hem 11.45, middle hem 8.8, lower hem 4.8 (side tips), apex 15.9. The f34
    (e ≈ 16°, 19.95 px/stud from the canopy width) gives 11.6 / 9.1 / 4.5–5.0. Adopted values are the means.
  - **Why 16.** The old kit's W04 YoungFir is 17 tall, its Sapling 6, its Classic Pine's lowest tier 15 wide; 16 keeps
    the young fir between the sapling (045) and the classic pine (049). The sheet's trunk is chunky (Ø 2.0 = 0.125 H),
    so a smaller tree would give a twig trunk under a character's shoulder, and a larger one a 3-stud trunk.
  - **Against the character (5.5):** the tree is 2.9 C tall; the lowest skirt tips hang at 4.5–5.0, about head height,
    so a character can stand at the trunk under the skirt's edge but brushes the flap tips; the trunk is about a
    character's shoulder width; rocks 1.0–1.6 tall (knee height); plant clumps 1.4–2.4 (waist to chest).
- **Build frame:** front −Y, +X right, ground z 0 = the sand patch's flat underside. Tree axis at (0, 0). Origin = bbox
  bottom centre (the patch's lobes are offset ≤ 0.4, so the origin lies within 0.4 of the axis: record it).

### 1.2 Measured views (`measure2.py`)

| View (box) | Silhouette bbox (px) | W : H | G | T | S | R | O |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (25,100,442,462) | 109–385 × 111–453 (277 × 343) | **0.808** | 72.5 % | 12.8 | 3.4 | 8.7 | 2.6 |
| Rear three-quarter (450,100,830,462) | 531–768 × 112–452 (238 × 341) | 0.698 | 76.4 | 13.1 | 3.3 | 4.4 | 2.7 |
| Front (25,500,276,742) | 70–235 × 508–737 (166 × 230) | 0.722 | 76.6 | 10.5 | 2.5 | 7.7 | 2.8 |
| Side (283,500,508,742) | 321–470 × 508–737 (150 × 230) | 0.652 | 78.6 | 10.5 | 2.4 | 6.0 | 2.5 |
| Rear (515,500,741,742) | 548–705 × 508–737 (158 × 230) | 0.687 | 78.5 | 11.5 | 2.0 | 5.9 | 2.1 |
| Top (748,500,999,742) | 785–967 × 528–712 (183 × 185) | 0.989 (W : D) | 97.2 | 0 | 0 | 2.5 | 0.3 |
| Exploded (25,785,524,1372) | parts, §1.4 | — | 65.7 | 18.2 | 0.5 | 14.5 | 1.4 |

- Shares are of the whole silhouette (O included, X excluded). **Verifier tolerance:** G ±5, T ±3, R ±3, S ±2 points;
  W : H ±0.05; positions ±0.04 of W / H unless stated. The f34 W : H is set mostly by the sand patch (canopy-only W : H
  0.656, §2.5).

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.1 f):

| f | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .08 | .41 | .63 | .77 | .89 | 1.0 | .87 | .69 | .49 | .37 | .08 |
| r34 | .06 | .42 | .59 | .76 | .86 | .98 | .92 | .78 | .63 | .42 | .06 |
| Front | .35 | .43 | .62 | .78 | .90 | 1.0 | .89 | .78 | .62 | .41 | .06 |
| Side | .35 | .44 | .61 | .77 | .89 | .99 | .92 | .79 | .64 | .41 | .34 |
| Rear | .35 | .44 | .63 | .77 | .89 | 1.0 | .91 | .78 | .64 | .45 | .34 |

- Reading: f .1 and .9 are the lower hem tips (h .34–.45), f .2–.8 the stepped flanks; f .0 / 1.0 are the sand patch
  (f34, r34) or the outermost plant (front, side, rear).

**Width per height** (silhouette width at h .0 → 1.0 as a fraction of W):

```
f34    .21 .87 .61 .52 .78 .57 .55 .39 .31 .17 .02
r34    .34 .86 .41 .60 .85 .58 .64 .36 .34 .18 .02
front  .42 .84 .20 .87 .87 .55 .67 .38 .34 .19 .03
side   .29 .75 .21 .71 .85 .57 .69 .39 .35 .19 .03
rear   .31 .77 .22 .81 .93 .61 .73 .41 .35 .20 .03
```

- h .1 is the base dressing (rocks and plants); h .2 the bare trunk (front .20 = 33 px of a 166-px-wide cell: Ø 2.4 at z
  3.2 including the root flare's top); h .3–.4 the lower skirt; h .5 the waist and h .6 the middle hem; h .7 the crown
  waist; h .8–1.0 the crown.

**Height fifths** (bottom → top, % of each class's pixels), f34: G 16.5 / 17.6 / **32.7** / 24.0 / 9.3 (the lower skirt
carries a third of the green; the bottom fifth's green is the ground plants); T 57.8 / 42.2 / 0 / 0 / 0 (no bark shows
above 0.4 H). Front: G 10.2 / 25.3 / 32.2 / 23.2 / 9.1; T 66 / 34.

**Plan (top cell, `topang.py`).** Outline W : D 0.989, 13 star points: **8 big points (r 87–92 px) at about 45° steps**
(math angles 350, 29, 87, 134, 178, 223, 267, 307; one points straight at the front, 267°) with **5 smaller points
(r 77–83) between them** (the second row; the other 3 are hidden). In the middle a **4-point crown star** (ridges N, E,
S, W in the plan, `z_topcrown.png`) with shorter ridges between. No trunk, sand, rock or plant shows from above
(R 2.5 % is shade on the flaps).

### 1.3 Silhouette and composition per view

**Front three-quarter (`z_f34.png`, `zb_f34.png`) — governs.** An elevated view (e ≈ 16°, §3.1) from the front-left
(we use az −35, §3.1).
- **Crown** (apex x 245, y 111): a straight-sided pointed cone, two facets per ridge (each ridge a lit right half and a
  dark left half), a slight step at y 166 (z ≈ 13.3, r 1.7) where the hem flaps start, hem tips at y 195 (r 2.7 on
  screen). A dark crease shadow under each hem notch (black in `cls_f34.png`).
- **Middle tier** (y 199–259): visible flaps in two staggered rows, the lower row's tips at y 238–256; the outermost
  tips at x 157 and 320.
- **Lower skirt** (y 259–355): two staggered rows of flaps; side tips at y 322 (left, x 129) and 335 (right, x 357);
  the front-facing flaps hang lowest (y 350–355). Each flap is a broad kite with a central ridge, 50–75 px long, 25–40
  px wide on screen.
- **Trunk** (from y 328 between the tips to the ground): Ø 48–50 px (2.4) just under the skirt (y 349–367), widening
  to 58 at y 384 (z ≈ 1.8) and flaring into the roots below y 395. Bark: vertical plank facets, a few dark slits, the lit
  right side orange (`#BE6F30` median), the left in dark brown shade (`#583624`).
- **Roots:** five visible: left (to x 190, y 420), front-left, a long front root (to x 300, y 442), front-right, right
  (to x 330, y 425). Angular, four- or five-sided, tapering to a blunt point on the sand, the longest about 4 studs
  from the axis.
- **Base dressing:** rock **R1** (x 145–192, top y 408), rock **R2** (x 220–262, top y 415) in front of the trunk, a
  dark plant clump **P1** behind R1 (x 130–205, top y 378, 7–9 upright dark leaves and a few lime ones), a big plant
  clump **P2** to the right (x 280–370, top y 375, lime and dark leaves) with a small grey rock **R3** behind it (x
  333–348), small lime sprigs **S1** (x 192–215), **S2** (x 265–290), **S3** (x 305–330). The pale sand patch spans x
  108–387 (the widest thing in the cell) with a soft edge.

**Rear three-quarter (`z_r34.png`, `zb_r34.png`).** The same tree from the back-right (az ≈ 145, e ≈ 16°): the same three
tiers and hems (h .732 / .585 / .358), the trunk, roots, a big clump at the screen left (the f34's P2 / R3 group from
behind), two pale back rocks **R4**, **R5**, a small lime clump **B1** and a clump **B2** at the screen right (the f34's
P1 from behind). It inverts consistently onto the f34's plan (§2.4).

**Front, side and rear cells (`z_ortho.png`, `z_front.png`, `zb_*.png`).** Low elevated views (e ≈ 8°) of the same tree,
drawn at one scale (230 px tall each), the tier rows at identical heights in all three (§1.1 table) — "consistent
geometry". Each shows one flap ridge pointing at the camera on the axis of every tier (the lit / dark split runs down the
middle). The base dressing differs a little between them (front: rocks at x 95–118 and 175–205, a small rock in front;
side and rear: their own arrangement); judge them loosely (§3.5).

**Top (`z_top.png`, `z_topcrown.png`).** §1.2. The flaps read as broad kites with a central ridge (one lit half, one
shaded half), pointed outward, the second row's points between the first row's.

**Foliage tier underside (`z_cu.png`).** The middle tier seen from below (e ≈ −30°): **12 flaps** radiating round
(`cuTier` angular count), each a broad pointed leaf; at the centre an **octagonal bark-brown hub** (a short frustum, Ø
0.28 of the tier width, about 2.2 for the middle tier at this drawing's scale — §2.2 uses 1.8) with a **flat octagonal
bottom face and a small dark round hole in its middle** ("flat joining surface for stacking").

**Trunk top detail (`z_cu.png`).** The trunk's top: **an octagonal section**, near-vertical planked sides, a flat top
with an **inner octagon ring** (the inset: a raised outer rim and a flat inner face, `#C8793B`), a dark recess in the
3/4 drawing. The base flares into roots at the lower left.

**Root base detail (`z_cu.png`).** The trunk's lower part: broad flat bark planks, the flare splitting into **angular
roots (four visible in the front half), each a long faceted prism kinked once and tapering to the sand**; a pale grey
chunky rock against the trunk's foot (the inset "trunk to root junction"), lime and green plant clumps, the pale sand
patch with a soft edge, two small pebbles.

### 1.4 Parts (Exploded Parts & Assembly, `z_expl.png`, `z_expl_low.png`, `parts.py`)

The exploded is an elevated view from the front (e ≈ 25°) drawn about 1.2× the hero's scale. **Its crown is drawn
small** (crown / skirt width 0.32 against the hero's 0.48): §3.2. **The hero governs every size**; the parts give
shapes and counts.

| Part | Box (px) | Size px | Screen W : H | Notes |
| --- | --- | --- | --- | --- |
| Crown Tier | (269,815,356,880) | 88 × 66 | 1.33 | a pointed cone with a hem of 4 visible flap tips; widest at h .2 |
| Middle Tier | (225,893,396,971) | 172 × 79 | 2.18 | a low cone, near-pointed top (width .01 at the top, .76 at h .1 down: a broad gently sloping roof seen from above), 6 visible tips |
| Lower Skirt | (175,979,449,1083) | 275 × 105 | 2.62 | a broad frustum with a **flat top 0.21–0.29 of its width**, 7 visible tips in two rows |
| Trunk | (240,1107,387,1270) | 147 × 163 | — | octagonal, top Ø 48 px (0.17 of the skirt), near-straight to h .5, then flaring; **six roots** spanning 3.0 × the top Ø |
| Root Base | (150,1270,480,1372) | — | — | **3 rocks** (1.6 / 2.7 / 1.9 wide at hero scale), **4 plant clumps** on the ground + 2 dropping onto it, 2 small lime sprigs, no patch drawn (shadows only) |

Green split by nearest swatch (dark / mid / light): crown 42 / 19 / 39 %, middle 41 / 25 / 34 %, lower 42 / 28 / 30 %:
the crown is the lightest tier, the lower skirt the most mid-toned (§5.3).

#### Crown Tier — exploded, hero, top
- **Shape:** a straight-sided **star cone**: 4 main ridges (in the plan N / E / S / W) and 4 minor ridges between, each
  ridge with two broad facets; a **hem of 8 flaps** under its lower edge (4 long under the main ridges, 4 shorter), tips
  drooping; underneath, a small octagonal hub.
- **Hero size:** apex 16.0; cone rim r 1.7 at z 13.3 (the f34's step); hem tips r 2.9 (long) / 2.5 (short) at z
  11.6–11.9; hub Ø 1.0, bottom z 12.545. Part about 5.8 × 5.8 × 3.6 (W : H 1.6 standing alone; the exploded's 1.33 includes
  its 25° view of the cone).

#### Middle Tier — exploded, hero, underside close-up
- **Shape:** a low pleated cone (slope about 40–45°) with a small flat top; **12 flaps in two rows of 6** (row A long
  and low, row B shorter and higher, offset half a step), tips drooping; an octagonal hub under the centre.
- **Hero size:** top cap r 0.6 at z 12.53; row A tips r 4.2 at z 8.8–9.1; row B tips r 3.7 at z 9.9–10.3; hub Ø 1.8,
  bottom z 9.415. Part about 8.4 × 8.4 × 3.8 (W : H 2.2; exploded 2.18).

#### Lower Skirt — exploded, hero
- **Shape:** a broad pleated frustum with a **flat top** (Ø 2.8), **16 flaps in two rows of 8**, the longest flaps of
  the tree, tips drooping clearly below the notches; an octagonal hub under the centre.
- **Hero size:** top cap r 1.4 at z 9.41; row A tips r 6.0 at z 4.8–5.2 (front-facing tips droop to 4.5); row B tips
  r 5.3 at z 6.2–6.6; hub Ø 2.2, bottom z 6.615 (on the trunk top). Part about 12.0 × 12.0 × 4.9 (W : H 2.45; exploded
  2.62).

#### Trunk — exploded, close-ups, hero
- **Shape:** an **octagonal, planked trunk** (each side split once vertically, so 16 tall facets, slightly irregular),
  near-straight above z 2.5, then a **flare into six angular roots**; flat top with an inner octagon ring (§3.6); 2–3
  short dark vertical slits on the bark.
- **Hero size:** top Ø 2.0 at z 6.6; Ø 2.1 at z 4.0; Ø 2.3 at z 2.5; body Ø 3.2 at z 0.6 between the roots; roots
  reaching r 2.8–4.2 on the sand. Part about 8 × 7 × 6.6.

#### Root Base — exploded, root close-up, hero
- **Shape:** a thin irregular sand patch (hero; the exploded draws only shadows), 5 chunky rounded-angular rocks (10–16
  broad facets each), 3 pebbles, plant clumps of **5–10 upright lanceolate leaves** (each leaf folded on its midrib,
  pointed, 50–75° from horizontal, arching out), small lime sprigs of 4–5 leaves.
- **Hero size:** patch 13 × 11 (§2.4), top z 0.15; rocks 1.0–1.6 tall; clumps 1.2–2.4 tall.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, tree axis at (0, 0)).

### 2.1 Stack (binding contact chain, bottom up; every gap is VEG_GAP = 0.015)

| Piece | Bottom z | Top z | Sits on | Notes |
| --- | --- | --- | --- | --- |
| Sand patch | 0 | 0.15 (crest), edge bevelled to 0.03 | ground | flat underside |
| Trunk + roots (one closed shell) | 0.05 (sunk 0.10 into the patch) | **6.60 flat top** | patch | root tips sunk 0.05 into the patch top |
| Lower Skirt core + hub (one closed shell) | **6.615** (hub's flat bottom) | **9.40 flat top cap** (r 1.4) | trunk top | hub Ø 2.2 ≥ trunk top Ø 2.0, so the joint is hidden |
| Lower Skirt flaps ×16 | — | — | the core (roots) and row A (row B) | ≤ 0.03 contact, chain to the core |
| Middle Tier core + hub | **9.415** | **12.53 top cap** (r 0.6) | skirt top cap | hub Ø 1.8 ≤ cap Ø 2.8 |
| Middle flaps ×12 | — | — | core / row A | |
| Crown core + hub | **12.545** | **16.0 apex** | middle top cap | hub Ø 1.0 ≤ cap Ø 1.2 |
| Crown hem flaps ×8 | — | — | the crown core | |
| Rocks, pebbles | sunk 0.08 / 0.04 into the patch | §2.4 | patch | separate closed shells |
| Plant hubs | sunk 0.03 into the patch | | patch | leaves chain to their hub |

- **No coincident faces:** each hub bottom sits 0.015 above the cap below (never coplanar, never floating more than
  0.03). Read the gaps back through the MCP (BVH nearest distance per shell).
- The hidden caps and hubs are what makes each tier a stand-alone, re-stackable part ("3 reusable foliage tiers").

### 2.2 Tiers (plan radii r from the axis; z heights; angles are plan azimuths, 0 = +X, counter-clockwise, −Y = 270°)

| Tier | Core: top cap r @ z → rim r @ z | Row A flaps (count, azimuths, root r @ z → tip r @ z, length, max width) | Row B flaps | Hub Ø × height |
| --- | --- | --- | --- | --- |
| Crown | apex 16.0 → rim r 1.7 @ 13.3; 4 main ridges at 270 / 0 / 90 / 180°, 4 minor ridges between (r 0.74 of the main) | **8 hem flaps** emerging from under the cone's rim: 4 long at 270 / 0 / 90 / 180°, root r 0.9 @ 13.6 → tip r 2.9 @ 11.6; 4 short at 315 / 45 / 135 / 225°, tip r 2.5 @ 11.9; length 2.8 / 2.3, width 1.4 / 1.2 | — | 1.0 × 0.35 |
| Middle | cap r 0.6 @ 12.53 → rim r 2.0 @ 10.6 | **6** at 270 + k·60°; root r 1.2 @ 11.0 → tip r 4.2 @ 8.9 (front-facing droop to 8.7); length 3.6, width 1.8 | **6** at 300 + k·60°; root r 1.0 @ 11.7 → tip r 3.7 @ 10.0; length 3.1, width 1.6 | 1.8 × 0.4 |
| Lower | cap r 1.4 @ 9.40 → rim r 2.8 @ 7.6 | **8** at 270 + k·45°; root r 1.8 @ 7.9 → tip r 6.0 @ 5.0 (front-facing droop to 4.7); length 5.2, width 2.4 | **8** at 292.5 + k·45°; root r 1.6 @ 8.7 → tip r 5.3 @ 6.4; length 4.4, width 2.1 | 2.2 × 0.5 |

- **One flap points straight at the front camera on every tier** (row A at 270°; the crown's main ridge at 270°), as the
  front cell and the top view show; the f34 (az −35) then sees the tiers slightly turned, as drawn.
- **Jitter, not a pattern:** tip radius ±6 %, tip height ±0.15, azimuth ±5°, width ±8 %, per-flap roll ±6°; never two
  neighbours equal. Row B lies **on** row A (seat by ray cast down onto row A and the core, as `m037._touch_up`), its
  tips 0.9–1.4 above row A's.
- **Waists (visible checks):** under the crown hem the middle tier shows at r ≈ 1.8, z ≈ 11.1–11.2; under the middle
  hem the skirt shows at r ≈ 2.6, z ≈ 8.2–8.4; a dark crease band under each hem (geometry shadow, not paint).

### 2.3 Flap and core shapes

- **Flap (closed shell, 16 tris):** a root vertex (or a 3-vertex root, hidden), a widest section at 0.42 of the length
  (left edge, **raised ridge** 0.16 × width above the edges, right edge, **keel** 0.10 × width below), a second section
  at 0.75 of the length (width 0.62 of the max, ridge and keel halved, **bent down a further 12–18°**: the droop), and
  the tip. Faces: root fan 4, two section bands 8, tip fan 4. In plan the flap is a **broad kite** (widest at 0.42 of its
  length), not a needle and not a triangle; its two top facets are the sheet's lit / shaded leaf halves.
- **Pitch:** row A starts 38° (crown 50°) below horizontal at the root, then droops; row B 30–34°.
- **Core (one closed shell with its hub):** an 8-corner pleated frustum (corners at the row A azimuths pushed out 0.15,
  between them pulled in 0.15), a flat top cap, an underside sloping up from the rim to the hub, the hub an octagonal
  frustum (top Ø 0.85 of the bottom Ø) with a flat bottom face and a **small recessed octagon in its middle** (Ø 0.3,
  0.08 deep: the sheet's "hole"). Faces only where needed; under 60 tris per core with the hub.
- **Crown core:** the star cone from the apex to the rim at z 13.3 (4 main ridges at r 1.7, 4 minor at r 1.25, 16
  facets); the hem flaps tuck under its rim, giving the f34's small step; an underside from the rim down to the hub
  (top z 12.9).

### 2.4 Trunk, roots, base

Plan positions are the f34 hero inverted at az −35, e 16, checked against the r34 at az 145 and the front cell.

| Piece | Position (X, Y) / azimuth | Size | Notes / evidence |
| --- | --- | --- | --- |
| Trunk body | axis (0, 0) | octagon, sides turned 22.5° (a face, not a corner, toward −Y); Ø 3.2 @ 0.6, 2.3 @ 2.5, 2.1 @ 4.0, 2.0 @ 6.6; rings at 0.6, 2.5, 4.2, 5.6, 6.6 | f34 Ø 2.4 under the skirt, front 2.0 (§3.4) |
| Bark planks | | each side split once vertically (16 facets), split vertices pushed ±0.06 | close-ups |
| Bark slits | 3, on the front-left, right and back | 0.6–1.0 tall, 0.1 wide, recessed 0.08 (pulled-in vertex pairs) | f34, exploded |
| Top face | z 6.6 | inner octagon inset 0.22, recessed 0.06 | trunk cross-section |
| Root RF (front, long) | azimuth 285°, reach r 4.2 | 1.2 wide × 1.5 tall at the trunk, 3 segments, kink at 0.55, tip 0.25 | f34 long front root (x 300); front cell +4.3 |
| Root RL (left) | 175°, r 3.4 | 1.1 × 1.3, 2 segments | f34 x 190; front cell −3.2 |
| Root RFL (front-left) | 235°, r 3.0 | 1.0 × 1.2, 2 segments | f34; exploded front-left |
| Root RR (right) | 345°, r 3.8 | 1.1 × 1.3, 3 segments | f34 x 330 |
| Root RB1 / RB2 (back) | 60°, r 3.0; 120°, r 2.8 | 1.0 × 1.1, 2 segments | r34; exploded back roots |
| Roots, all | start on the trunk at z 2.0–2.8; 4–5-sided section, top ridge, flattened on the sand; tip sunk 0.05 | | "simple angled forms" |
| Sand patch | irregular lobed outline, 14 points, r 5.4–6.8 (mean 6.0), longest toward 325° and 145° (the f34 screen axis) | 13.2 × 11.0, crest 0.15, bevel 0.5 wide to 0.03 | f34 x 108–387 (13.9 on screen); front 12.0, side 10.9, r34 11.8 |
| Rock R1 | (−4.9, −0.2) | 2.3 × 1.9 × 1.5 tall | f34 f .13–.30, top h .13 |
| Rock R2 | (−2.7, −3.4) | 2.1 × 1.8 × 1.5 | f34 f .40–.55, top h .11; front cell's pale rock at x 108–118 |
| Rock R3 | (4.4, −1.9) | 1.6 × 1.4 × 1.2 | behind P2 in the f34; front cell's dark rock x 175–195 |
| Rock R4 | (3.9, 1.5) | 1.3 × 1.1 × 1.0 | r34 pale rock (x 590–615) |
| Rock R5 | (1.6, 4.4) | 1.5 × 1.3 × 1.1 | r34 pale rock (x 660–690) |
| Pebbles ×3 | (−1.0, −4.6), (2.4, −4.3), (−3.6, 2.9) | 0.35–0.5 | root close-up pebbles |
| Clump P1 (left, dark) | (−4.3, 1.4) | Ø 2.4, 2.2 tall, 9 leaves (6 dark, 3 lime) | f34 x 130–205, top h .22; r34 right clump |
| Clump P2 (right) | (2.4, −3.6) and a second hub at (3.5, −2.6) | Ø 3.0 together, 2.4 tall, 12 leaves (6 lime, 6 dark) | f34 x 280–370, top h .23 |
| Clump B1 (back) | (3.2, 3.5) | Ø 1.6, 1.3 tall, 6 leaves, lime | r34 centre clump |
| Clump B2 (back-left) | (−1.6, 4.2) | Ø 2.0, 1.6 tall, 8 leaves | r34 right clump |
| Sprigs S1, S2, S3 | (−4.0, −2.1), (−1.4, −4.9), (1.2, −4.7) | Ø 0.8–1.0, 0.7–0.9 tall, 4–5 lime leaves | f34 x 192–215, 265–290, 305–330 |

- **Keep clear:** no rock or clump within 0.1 of a root's top ridge or the trunk (contact allowed, overlap ≤ 0.05); P2
  and S2/S3 sit between the front roots; nothing under the skirt's front tips higher than 2.0 except P2's tallest leaf.
- **Spacing:** the dressing stays inside the patch outline by ≥ 0.3.

### 2.5 Expected extents and screen checks

- **Extents (build frame):** X about −6.8 … +6.8; Y about −6.4 … +6.4; Z 0 … 16.0. Bbox about 13.4 × 12.6 × 16.0 (the
  patch is the widest thing; the canopy's tips reach r 6.0 ± 0.36).
- **Self-consistency at `f34_sheet (−35, 16)`:** canopy W / H ≈ 0.66; hems at h .75 / .61 / .36; trunk T in the bottom
  two fifths only.
- **Checks on the renders** (floor hidden, `measure_render.py`):
  - **f34_sheet (−35, 16)** (probe az −25 / −35 / −45 × e 12 / 16 / 20, keep the best): W : H 0.76–0.86 (sheet 0.808);
    canopy-only W : H 0.62–0.70 (0.656); shares G 72.5 ± 5, T 12.8 ± 3, R 8.7 ± 3, S 3.4 ± 2; top profile within ±0.07
    for f .1–.9; width per height within ±0.08 at h .2–.9; hems (widest rows) at h .75 / .61 / .36 ± .03 with widths
    .48 / .71 / 1.0 ± .05 of the canopy; waists at h .74 / .57 ± .03 with widths .34 / .47 ± .06; G fifths within ±6;
    no T above 0.4 H; R1 / R2 / P1 / P2 at their §2.4 f ranges ± .05.
  - **front_sheet (0, 8), side_sheet (90, 8), rear_sheet (180, 8):** hems at h .734 / .576 / .336 ± .03, widths .50 /
    .73 / 1.0 ± .05, waists .32 / .47 ± .06; canopy W / H 0.64–0.72; shares loosely (G ±6); dressing judged for
    content only (§3.5).
  - **r34_sheet (145, 16):** loosely: W : H 0.65–0.75 (0.698), hems .732 / .585 / .358 ± .04, G 76.4 ± 6.
  - **top (0, 89):** W : D 0.95–1.03 (0.989); 8 big star points at about 45° steps with the second row between (≥ 4
    visible), a 4-point crown star in the middle; G ≥ 90 %, no sand or bark visible.

## 3. View conflicts and resolutions

### 3.1 Camera elevations: f34 / r34 (e ≈ 16°) vs the "orthographic" cells (e ≈ 6–10°) vs the top (90°)

- **Evidence.** f34: the lower skirt's side tips at y 322–335 and its front tips at y 355 (33 px = 1.65 studs at
  19.95 px/stud) and the sand patch's front edge 6 studs ahead of the trunk give sin e ≈ 0.27–0.29 → e ≈ 16°. Front
  cell: front tips 15 px below the side tips, the patch 12 px deep for 163 px wide → e ≈ 6–10°. All five side cells
  agree on every tier height within 0.02 H (§1.1).
- **Resolution (decision §8.10).** `f34_sheet (−35, 16)` governs (probe az ±10, e ±4); `r34_sheet (145, 16)`,
  `front_sheet (0, 8)`, `side_sheet (90, 8)`, `rear_sheet (180, 8)` and the kit `top`. Azimuth −35 is a choice (the tree
  is near-symmetric); §2.4's plan positions are this camera inverted, and they invert consistently onto the r34 at 145.

### 3.2 The exploded crown and trunk vs the hero

- **Evidence.** Exploded crown / skirt width 0.32 against 0.48–0.50 in all five side cells; exploded middle / skirt 0.63
  against 0.68–0.75; exploded trunk top / skirt 0.17 against 0.17–0.21.
- **Resolution.** The hero governs every size; the parts are the hero's own pieces (built by the same functions,
  moved to the origin), so the parts shot will show a bigger crown than the exploded. Record it.

### 3.3 Plan size: the top cell vs the side cells

- **Evidence.** The top cell's star tips reach r 90 px (12.6 studs across if drawn at the front cell's 14.3 px/stud);
  the side cells' canopy is 148–160 px wide (10.7–11.6).
- **Resolution.** Row A tips at r 6.0 (12.0 across), so the silhouette is 11.2–11.8 wide depending on the azimuth,
  inside the side cells' range; the top render will read a little smaller than the top cell if compared at one scale.

### 3.4 Trunk diameter: f34 / r34 vs the orthographic cells

- **Evidence.** Under the skirt the trunk is 48–50 px in the f34 (2.4) and 46 px in the r34 (2.3), but 27–30 px in the
  front, side and rear cells (2.0–2.2 at 13.8 px/stud).
- **Resolution.** Ø 2.0 at the top, 2.1 at z 4.0, 2.3 at z 2.5 (flare start). The f34 trunk will read about 10 % thinner
  than drawn: record it. Alternative: Ø 2.3 throughout (closer to the hero, the side cells' trunk then 10 % fat).

### 3.5 Base dressing between views

- **Evidence.** The f34 and r34 invert onto one plan (§2.4); the front cell puts a pale rock left of the trunk (R2's
  place, X −2.7), a dark rock and a pale rock right (R3, R4), a small rock in front; the side and rear cells draw their
  own small arrangements; the exploded root base shows only three rocks and six clumps.
- **Resolution.** The f34 + r34 plan governs (5 rocks, 4 clumps, 3 sprigs, 3 pebbles); the front / side / rear and the
  exploded are judged for content (rocks and plants both sides of the trunk, a pale sand patch) only.

### 3.6 The trunk top: hollow (3/4 close-up) vs flat with an inner ring (cross-section) vs "flat top for foliage tier"

- **Resolution.** A flat top with an inner octagon inset 0.22 and recessed 0.06 (reads as the rim of the cross-section;
  the 3/4 drawing's dark recess is that inset in shade). Hidden in the hero; it shows on the Trunk part and in
  `trunk_cu`.

### 3.7 The hub's hole

- **Resolution.** A small recessed octagon (Ø 0.3, 0.08 deep) in the middle of each hub's flat bottom, painted
  `m042_bark_deep`; **no through-hole** (each core stays one closed shell). The trunk's top face takes the lower skirt's
  hub, so the hole is never seen in the hero.

### 3.8 Two rows per tier vs the exploded's single-row look

- **Evidence.** Top view: 8 big outer points with smaller points between (§1.2); the front cell's lower skirt widens in
  two steps (h .38 and .336); the f34 middle and lower tiers show tips at two levels; the underside close-up counts 12
  flaps on the middle tier. The exploded parts, seen from 25° above, show one ragged hem.
- **Resolution.** Two staggered rows on the middle and lower tiers (12 and 16 flaps), one hem row on the crown (8).

### 3.9 Branches

- **Evidence.** The sheet draws no branch anywhere: the tiers stack on one another on hubs, the lowest on the trunk's flat
  top ("flat joining surface for stacking").
- **Resolution.** **No branches.** The user's tree rule is served by a detailed trunk (planks, slits, flare) and six
  multi-segment roots; record "no branches: none on the sheet" in the spec. Alternative: hidden branch stubs under each
  tier (invisible, wasted tris).

### 3.10 "No textures, no noise, solid colours only" against the user's blended-colour rule

- The user's rule wins, quietly: broad position-based blends (a lighter crown, deeper flap roots and inner surfaces,
  lighter flap tips), whole-facet Tint mottling at a low amplitude, never per-triangle confetti. The sheet's strong
  lit-right / dark-left split is the light (§3.11).

### 3.11 The palette against the renders: three foliage swatches are three lighting states

- **Evidence** (`samp.py`): on every tier the screen-left half is 62–93 % nearest the **dark** swatch and the right half
  54–80 % nearest the **light** swatch (f34 canopy left-half median `#286834`, 131°; right-half `#95BC32`, 77°); the
  shade-side edges are teal (`#156863`, rim light). Within one lit flap the colour barely changes along its length.
  Positional signals that remain: the crown is the lightest tier (light share 39.5 % against the skirt's 30.5 %) and
  the lower skirt the most mid-toned (mid 27 % against the crown's 9 %).
- **Resolution.** One base needle key that renders lime in light and deep green in shade, plus a light key and a deep
  key **blended by position and role** (§5.5); never by facing. Calibrate against the rendered regions, not the swatches.

### 3.12 Cast shadow

- The sheet draws a lavender ground shadow (`#CFD0D4`) to the left; the masks exclude it (X). Render every `*_sheet`
  view with the studio floor hidden (M034 §2.6), so our own floor shadow isn't classed as rock.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its exploded cell

1. `tier(kind)` with `kind` in `"crown" | "middle" | "lower"` → one closed **core + hub shell** (§2.3) plus its
   **flap shells** (row A, then row B seated on it), all in one object. Parts: `TieredFirCrownTier`,
   `TieredFirMiddleTier`, `TieredFirLowerSkirt`, each at the origin with its hub's bottom at z 0 (origin bottom centre:
   the drooping tips go below the hub, so the part's origin is at its lowest tip: decide in the builder and record).
   Compare each with its exploded cell (screen W : H ±0.15, visible tip count, the flat top cap visible on the middle
   and lower parts) and the underside close-up (`tier_under`, §4.2).
2. `flap(root, tip, width, pitch, droop, roll)` → one 16-tri closed shell (§2.3). Every flap in the model comes from
   it.
3. `trunk()` → `TieredFirTrunk`: the octagonal planked body (rings §2.4), the slits, the top inset, and the six roots
   (`root(azimuth, reach, w, h, segments, kink)`: 4–5-sided tapered prisms with a top ridge, kinked, their trunk end
   buried 0.3 in the body). **One closed shell:** union each root into the body one at a time at the origin
   (`m021._union_fine`, merge 0), save between unions; or build body and roots as one explicit mesh (the root's top
   ridge rising out of a body plank). Compare with the exploded trunk (top Ø 0.17 of the skirt width, roots spanning 3.0×
   the top Ø, flare from mid-height) and `trunk_cu` / `root_cu`.
4. `root_base()` → `TieredFirRootBase`: `patch()` (lobed CDT crest + bevel ring + flat underside), `rock(spec)` ×5
   (explicit ring stacks: base ring, a widest ring at 0.3 h, a shoulder ring at 0.7 h, a flat 4–6-corner crown; 10–16
   broad facets; no `K.hull_rock` jitter balls), `pebble()` ×3, `clump(spec)` ×4, `sprig(spec)` ×3 (each leaf a closed
   8-tri folded lanceolate shell, each clump a small closed hub pyramid on the sand). Compare with the exploded root base
   (rock silhouettes rounded-angular, W : H 1.3–1.6; clumps of upright pointed leaves) and `root_cu`.
5. **Hero `TieredFir`** = root base + trunk + lower + middle + crown, stacked by §2.1 (each tier moved up so its hub
   bottom sits VEG_GAP over the cap or trunk top below), joined into one object of closed shells. No booleans between
   pieces.
6. **Parts shot** (az −30, e 20) laid out like the exploded: crown above middle above skirt above trunk above the root
   base, gaps of 1.5–2.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a slim three-tier fir of broad drooping flaps on a chunky orange-brown trunk with six roots, on a
   pale sand patch with rocks and plant clumps.
2. **f34_sheet** against the hero (§2.5): hems, waists, profiles, shares, dressing positions.
3. **front_sheet / side_sheet / rear_sheet, r34_sheet, top** per §2.5.
4. **Tier extras:** `tier_under` (the middle tier part from below, e −35) against the underside close-up: 12 flaps round
   an octagonal brown hub with a flat face and a small dark recess. `trunk_cu (−30, 30)` on the Trunk part against the
   trunk-top detail: octagon, flat top with the inner ring, planks. `root_cu (−25, 15)` framed on the trunk foot against
   the root base detail: angular kinked roots on the sand, a rock against the foot, plants.
5. **Contact counts** (§6): floating shells 0; every flap ≤ 0.03 from its core or a neighbour flap and chained to the
   core; each hub 0.01–0.03 over its seat; every rock, pebble and plant hub on the patch.
6. **Hero size** per §2.5; **scale shot** beside a 5.5-stud character marker at the patch edge.
7. **Underside view** (kit `underside`): the skirt's flap undersides and hub over the trunk, the patch's flat bottom.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Lower skirt core + hub | 1 | 48–64 | 48–64 |
| Lower skirt flaps | 16 | 16 | 256 |
| Middle core + hub | 1 | 44–60 | 44–60 |
| Middle flaps | 12 | 16 | 192 |
| Crown star cone + hub | 1 | 40–56 | 40–56 |
| Crown hem flaps | 8 | 16 | 128 |
| Trunk body (16 facets × 4 bands, top inset, slits) | 1 | 170–230 | 170–230 |
| Roots | 6 | 24–40 | 150–240 |
| Sand patch | 1 | 70–110 | 70–110 |
| Rocks | 5 | 36–60 | 200–280 |
| Pebbles | 3 | 8–12 | 24–36 |
| Plant leaves (clumps 35 + sprigs 14) | 49 | 8 | 392 |
| Plant hubs | 8 | 6–8 | 48–64 |
| **Hero** | | | **about 1760–2150** (limit 4000) |
| Parts: CrownTier / MiddleTier / LowerSkirt / Trunk / RootBase | | | 170–185 / 236–252 / 304–320 / 320–470 / 730–880 (limit 1000) |

- **Spend the headroom on the read, not on density:** if the canopy looks thin, add a third, inner row of 4–6 short
  flaps on the lower skirt (+64–96) or split each flap's widest section into two (20 tris) before anything else. Stay
  under 3200 so the hero stays cheap for a tree that will be placed many times.

### 4.4 What to do better than the kit's pines (M032 `m032.pine`, M037 `m037.pine`)

| Kit pine | This fir |
| --- | --- |
| Tiers are flat 5-point star skins (`_star_tier`), one closed fan per tier, no thickness | Each tier: a closed core + 8–16 separate thick **kite flaps with a raised midrib and a keel**, two staggered rows |
| 5 points per tier, all tiers alike; `PINE_INNER` notches 0.66–0.76 | 8 / 12 / 16 flaps, row B between row A's points; crown star 4 + 4 ridges |
| Points barely droop (a fixed −0.3 r dip) | Each flap bent twice (pitch 30–50°, droop +12–18° at 0.75 L); front tips visibly below the notches |
| M032 tiers floated apart ("none touching another"); M037 fixed it with ray-cast contact | Stacked by flat caps and hubs (the sheet's own joining surfaces), every gap 0.015 and read back |
| 4–5-sided trunk, no roots, hidden in the canopy | Octagonal planked trunk with slits, a flare and six kinked roots, visible for 0.28 H |
| One tint per tier (±5 %), one `PINE` key | Base / light / deep keys blended by position and role, calibrated to the sheet's renders (§5) |

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 26 × 28 box inside each, sd ≤ 1.4)

| Swatch | Box | Hex | HSV | Channel order | Use |
| --- | --- | --- | --- | --- | --- |
| Foliage Dark | (856,143,882,171) | `#31533F` | 145°, 0.41, 0.33 | G > B > R | the shade-side tone; start for `needle_deep` |
| Foliage Mid | (856,194,882,222) | `#5C8D41` | 99°, 0.54, 0.55 | G > R > B | start for `needle` |
| Foliage Light | (856,245,882,273) | `#B6B638` | 60°, 0.69, 0.71 | R ≈ G > B | the lit tone; start for `needle_light` |
| Trunk | (856,296,882,324) | `#985E37` | 24°, 0.64, 0.60 | R > G > B | start for `bark` |
| Rock | (856,347,882,375) | `#C6B4A3` | 29°, 0.18, 0.78 | R > G > B | close to the lit rock; start for `rock` |
| Ground Plants | (856,398,882,426) | `#B2A837` | 55°, 0.69, 0.70 | R > G > B | the lit lime leaf; start for `plant` |

### 5.2 Rendered regions (`samp.py`, `samp2.py`, `samp3.py`; median / lit / shade quartiles)

| Region | Median | Lit (v > .7 median / lit quartile) | Shade | Halves (right = lit / left = shade) |
| --- | --- | --- | --- | --- |
| Canopy f34 / r34 / front / side / rear / top / exploded | `#4B8233` (102°, .61, .51) / `#448132` / `#488333` / `#508731` / `#4B8732` / `#3F7731` / `#629332` | `#A6C434` (72°, .73, .77) / `#AFC934` | `#174729` | R `#95BC32` (77°) / L `#286834` (131°) (f34); front R `#91B930` / L `#276A37` |
| Crown / middle / lower (f34, all) | `#3B7737` / `#4A8434` / `#548832` | `#B4CD37` / `#B9CE36` / `#9CC033` | `#1B502A` / `#17462B` / `#164528` | crown R `#9FC034`, L `#26683A` |
| Underside close-up (needles) | `#367031` (115°) | `#A4C434` | `#23522B` | |
| Trunk f34 / r34 / front / exploded / trunk close-up | `#864C29` (23°, .69, .53) / `#7D4D29` / `#724428` / `#9F5C30` / `#B06733` | `#DB883D` (28°, .72, .86) / `#E49244` | `#4D2F1F` | f34 R `#BE6F30` (27°, .75, .75) / L `#583624` |
| Trunk top face (cross-section inset) | `#C8793B` (26°, .71, .78) | `#E2934C` | `#AB7136` | |
| Hub (underside close-up, in shade) | `#714329` (22°, .64, .44) | `#9B5C32` | `#3F2315` | hole `#503727` |
| Rock f34 / exploded / root close-up | `#9D958E` / `#B0A59D` / `#9C9898` | `#D9C8B5` (32°, .17, .85) / `#D9CABA` / `#DDCDBD`; lit quartile `#E5D4C0` | `#60666C` (blue-grey: light) | |
| Sand f34 / root close-up | `#E7CC9C` (38°, .32, .91) / `#E9CD9E` | `#EBD3A7` | `#E1C490` | |
| Plants f34 / exploded / root close-up | `#4D7324` (89°) / `#628E28` / `#5E871F` | `#B8C534` (65°, .74, .77) / `#B7C62C` / `#B4C421` | `#1F401B` | lime (h < 80) 40–46 % `#9DB126`–`#A8BC29`; green (80–110) 38–50 % `#416B23`–`#508127`; dark (≥ 110) 4–20 % `#1D4721` |

### 5.3 How the colour works

- **Needles:** one mid green that renders lime in light and deep green in shade; the crown a step lighter, the lower
  skirt a step more mid-toned; flap roots and the tier cores (the recesses between flaps) deeper, toward teal; the
  outer third of each flap a touch lighter. The sheet's hard lit-right / dark-left split is the light: **never colour by
  facing**. Keep the needles (lit 70–80°, shade 125–140°) apart from the bark (22–28°) by hue; there is no shared key.
- **Bark:** one warm orange-brown (22–28°, sat 0.64–0.75, **R > G > B**); deeper in the slits, the lowest 0.4 near the
  sand and the hubs; lighter on the trunk's top face. The sheet's dark brown left side is the light.
- **Rock:** one warm pale grey-beige (28–33°, sat 0.13–0.18, R > G > B); crowns a step lighter, feet a step deeper.
  The blue-grey shade (`#60666C`) is the light.
- **Sand:** one pale warm sand (36–40°, sat 0.28–0.34); slightly deeper within 0.4 of the trunk, roots and rocks and on
  the bevel.
- **Ground plants:** two leaf tones chosen **per leaf by position** (outer and taller leaves lime, inner and lower leaves
  green) and per clump (P1 and B2 mostly green, sprigs all lime). They stay yellower than the needles (plant lime 65–69°
  against needle lit 72–77°).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are medians of **unshadowed rendered regions** (the lit-half or v > .7 medians), not swatches and not
shade quartiles. `K.sample` kinds: `"green"` for needles and plant leaves, `"brown"` for bark and sand, `"stone"` for
rock, `"vivid"` for the lime keys if `"green"` rejects them.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m042_needle` | f34 lit-half canopy median `#95BC32` ± 12 (start from the mid swatch `#5C8D41`) | 74–84° lit, G > R > B | every flap's top and keel by default | rough 0.85, `low_spec=True` |
| `m042_needle_light` | v > .7 canopy median `#A6C434`; lit quartile `#AFC934` (start `#B6B638`) | 68–76°, sat ≥ 0.7 | crown cone 45 %; crown flaps 30 %; middle row B 20 %; outer 35 % of every flap's length +20 % | rough 0.85, low spec |
| `m042_needle_deep` | the dark swatch `#31533F` rendered lit ± 12 (it then falls to about the sheet's shade `#174729`–`#286834` in shade) | 130–145°, sat 0.4–0.6 | tier cores (outside the hub) 70 %; flap undersides (the keel sheet, a construction role) 35 %; the root third of every flap 30 %; lower skirt row A 15 % overall | rough 0.9, low spec |
| `m042_bark` | f34 lit-half trunk median `#BE6F30` ± 12; v > .7 `#DB883D` (start from the swatch `#985E37`) | 22–28°, sat 0.64–0.75, **R > G > B** | trunk, roots, default | rough 0.9 |
| `m042_bark_light` | trunk top face `#C8793B` / lit `#E2934C` | 25–29° | the trunk's top face 70 %; root top ridges on their outer half 20 % | rough 0.9 |
| `m042_bark_deep` | exploded shade-half `#6F462C` (start); hub `#714329` | 20–25°, sat 0.55–0.65 | bark slits 100 %; the lowest 0.4 of trunk and roots 25 %; hubs 70 %; the hub recess 100 % | rough 0.95 |
| `m042_rock` | lit (v > .7) median `#D9C8B5` ± 10 (swatch `#C6B4A3`) | 28–33°, 0.13–0.18, R > G > B, R − B ≥ 25 | rocks, pebbles | rough 0.85, metal 0 |
| `m042_rock_light` | lit quartile `#E5D4C0` | 30–35°, 0.12–0.17 | top 30 % of each rock's height at 35 % | rough 0.85 |
| `m042_rock_deep` | a step below `rock` (`#B0A59D` exploded median) | 25–30°, 0.10–0.15 | lowest 0.25 at 25 % | rough 0.9 |
| `m042_sand` | `#E7CC9C` ± 8 (f34 and root close-up agree within 3) | 36–40°, 0.28–0.34 | patch | rough 0.95 |
| `m042_sand_deep` | shade quartile `#E1C490` | 36–40°, 0.34–0.38 | within 0.4 of trunk, roots, rocks, hubs at 25 %; bevel and edge at 30 % | rough 0.95 |
| `m042_plant` | plant v > .7 median `#B8C534`; lime leaves `#A8BC29` (swatch `#B2A837`) | 62–70°, sat ≥ 0.75 | lime leaves (outer / taller; all sprig leaves) | rough 0.85, low spec |
| `m042_plant_deep` | green leaves `#508127` (exploded) / `#48721E` | 88–98°, sat 0.65–0.75 | inner / lower leaves; most of P1 and B2 | rough 0.85, low spec |

**Calibration warnings:**
- **Needles (the W04 lesson, P2 unmet; M035 "lit foliage dark and less lime"; M038 "greens slightly grey").** Judge the
  f34_sheet canopy: lit (v > .7) median within 12 of `#A6C434` (hue 68–80°, sat ≥ 0.65), whole-canopy median within
  15 of `#4B8233`, and the left (shade) half's median hue ≥ 115°. If the lit faces read olive or grey, raise the base
  key's saturation; don't paint the lit side.
- **Bark:** f34 lit-half median within 12 of `#BE6F30`, R > G > B; the whole-trunk median recorded against `#864C29`
  (our shade is lighter than the sheet's: a known miss ≤ 20 levels).
- **Rock:** never blue; R > G > B on every rock median (the shade's blue is light).
- **Plants vs needles:** keep `m042_plant` ≥ 6° yellower than `m042_needle_light` after calibration.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles, never facing)

- **Flaps:** a field along each flap's own axis (0 at the root, 1 at the tip): `needle_deep` over 0–0.33 (30 %),
  `needle` 0.33–0.65, `needle_light` 0.65–1.0 (+20 %). Tier offsets: crown +30 % light, middle row B +20 % light, lower
  row A +15 % deep. The keel (underside) faces carry `needle_deep` at 35 % on top of that (a role: they are built as the
  flap's under-sheet). Per-flap tint ±0.04.
- **Cores:** `needle_deep` 70 %; their caps (hidden) any. Hubs `bark_deep` 70 % / `bark`.
- **Trunk and roots:** `bark` base; `bark_deep` by height (lowest 0.4: 25 %) and in the slits (hard); `bark_light` on the
  top face (hard: a cut face) and on the outer half of each root's top ridge (20 %). Per-plank tint ±0.04 (whole
  facets).
- **Rocks:** `rock` base; `rock_light` by height within each rock (top 30 %: 35 %); `rock_deep` lowest 0.25 (25 %).
- **Sand:** `sand` base; `sand_deep` by distance (within 0.4 of trunk, roots, rocks, hubs: 25 %) and on the bevel (30 %).
  Averaged with neighbours before quantising (M034: no triangle shards).
- **Plants:** per leaf by role (outer / taller → `plant`, inner / lower → `plant_deep`), ±0.04 tint per clump.
- **Hard edges only** where materials meet: needle | bark (hub, separate shells), bark | sand, rock | sand, leaf | sand.

### 5.6 Texture (Tint) and finish

- **Tint:** needles amp 0.04 per flap (one tone per flap facet pair, scale 0.6); bark 0.04 per plank; rock 0.04 per
  original facet (scale 0.4); sand 0.03 (scale 0.15, broad); plants 0.04 per leaf. Never per-triangle confetti.
- **Finish:** needles and plants `low_spec=True`, rough 0.85; bark 0.9; rock 0.85; sand 0.95. No emission.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Canopy:** f34_sheet lit (v > .7) median within 12 of `#A6C434`; whole canopy within 15 of `#4B8233`; shade half hue
  ≥ 115°. Front / side / rear canopy medians within 15 of `#488333`–`#508731`. Top canopy median within 15 of
  `#3F7731`, the crown star lighter than the outer flaps.
- **Trunk:** f34 lit half within 12 of `#BE6F30`.
- **Rock:** f34 v > .7 median within 10 of `#D9C8B5`, R > G > B.
- **Sand:** f34 S median within 8 of `#E7CC9C`.
- **Plants:** f34 plant (G below the skirt tips) v > .7 median within 12 of `#B8C534`.
- **Shares** per §2.5.

## 6. Joins and contact (no floating dressing)

- **Shells:** trunk + roots one closed shell; each tier core + hub one closed shell; each flap, rock, pebble, leaf and
  plant hub its own closed shell; the patch one closed shell. All in one hero object (decision §8.5).
- **Stack** (§2.1): trunk base sunk 0.10 into the patch; each hub's flat bottom 0.015 above its seat (the trunk top or
  the cap below), measured by BVH nearest distance: 0.005–0.03. Never coplanar, never overlapping.
- **Flaps:** each flap's root end is buried in its core (the §2.2 roots lie 0.2–0.6 inside the core's surface; keep the
  buried part short, it is hidden geometry) and the flap leaves the core through its surface with no gap; row B flaps
  rest on row A (seated by ray cast, gap 0.015) or on the core; neighbours may touch but cut no
  more than 0.05 into each other. Every flap chains by contact to its core, the core to the stack, the stack to the
  ground.
- **Base:** rocks sunk 0.08, pebbles 0.04, plant hubs 0.03 into the patch top; every leaf within 0.03 of its hub
  (`STAGES`: no hidden stems); leaves may touch a rock, root or the trunk but cut ≤ 0.05 into it.
- **Count floating shells before reporting** (STAGES: 035 and 036 failed round 1 on this): **0**. A shell "floats" if
  its nearest distance to every other shell and the ground is > 0.03 or if it doesn't chain to the ground.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0 (flap roots and leaf hubs are where 019–021 grew
  them).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no particles, no falling needles, no motes. The cast shadow is the
render's, not an effect.

- **Stage 5 (lighting): skip, and record why.** No emission, no PointLight. Studio notes (Requires Manual Validation):
  the canopy's lime-on-light / deep-in-shade read under the game's sun (the W04 fir rendered too dark and flat, P2); the
  bark stays orange-brown (not red); the rock stays warm pale grey.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** Not recommended: falling-needle or leaf particles,
  dust, pollen, any light. (A falling-leaf emitter would be the user's call later; the sheet doesn't draw one.)
- **Collision:** hero `precise` (a hull would wrap the patch and the skirt into one solid cone and stop a player 6
  studs from the trunk); Trunk `hull`; the three tier parts `hull`; RootBase `precise`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by searching `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json`, the
repo text (`git grep`) and every sheet / kit / wip `.blend` (zstd-decompressed) with `blendall.py`:
- **W04 (owns the subject's names):** `YoungFir`, `YoungFirCrownTier`, `YoungFirMiddleTier`, `YoungFirLowerSkirt`,
  `YoungFirTrunk`, `YoungFirRootBase`, `YoungFirSparse`, `YoungFirFull`, `YoungFirLeaning` (in `W04.blend`,
  `FlintbornWorldKit.blend`, the checkpoint and every wip copy); keys `w04_*`. Also `ClassicPine*`, `OldPine*`,
  `Sapling`, `GroundScatterPinecone`, and the strings `pine` (M032 / M037 `pine_*` pieces).
- **`TieredFir`, `TierFir`, `FirSpire`, `SpireFir`, `StackedFir`, `GreenFir`, `FirTree` and `m042` occur nowhere** in
  the repo text, the manifests or any `.blend`. `M.mk` would silently rename a clash to `<name>M042`; the names below
  don't clash.

| Object | Part | Why |
| --- | --- | --- |
| `TieredFir` | hero: base, trunk, three tiers | W04 owns `YoungFir`; "tiered" names the defining read |
| `TieredFirCrownTier` | "Crown Tier": star cone + hub + 8 hem flaps | |
| `TieredFirMiddleTier` | "Middle Tier": core + hub + 12 flaps | |
| `TieredFirLowerSkirt` | "Lower Skirt": core + hub + 16 flaps | |
| `TieredFirTrunk` | "Trunk": body + six roots | |
| `TieredFirRootBase` | "Root Base": sand patch, 5 rocks, 3 pebbles, 4 clumps, 3 sprigs | |

- Palette keys `m042_*` (§5.4). Collection `Kit/M042 Young Fir`. No sockets.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **16.0 tall, canopy tips r 6.0 (silhouette 11.2–11.8), trunk Ø 2.0–2.1, patch about 13 × 11**
   (recommended: between the old kit's 6-tall sapling and the classic pine; the sheet's chunky trunk stays plausible; the
   skirt tips hang at head height), or 17 (W04 parity), or 12 (a smaller "young" tree, trunk Ø 1.5).
2. **Name** (§8): **`TieredFir` and its five parts** (recommended), or `StackedFir`. Not `YoungFir*` (W04).
3. **Flap counts** (§2.2, §3.8): **crown 8 hem flaps on a 4 + 4-ridge star cone; middle 12 (two rows of 6); lower 16
   (two rows of 8); one flap aimed at −Y on every tier** (recommended: the top view's 8 + 5 visible points, the underside
   close-up's 12, the front cell's two-step skirt), or one row per tier (8 / 10 / 12; cheaper, flatter, the W04 look).
4. **Tier construction** (§2.3, §6): **a closed core + hub shell per tier with separate closed 16-tri kite flaps seated
   by contact** (recommended: no booleans, real overlap and shadow between flaps, every flap chained to its core), or
   one continuous pleated shell per tier (one shell, but no overlapping rows: the W04 H11 miss).
5. **Stacking** (§2.1): **flat caps and octagonal hubs as on the sheet, gaps 0.015** (recommended: the sheet's own
   "flat joining surface"; makes the tiers reusable parts), or the trunk running up through every tier as a hidden
   leader (simpler contact, but the hubs and caps go and the tiers aren't stand-alone).
6. **Packaging** (§6): **one hero object of closed shells (trunk + roots one unioned shell; cores; flaps; patch; rocks;
   pebbles; leaves; hubs); five parts as the exploded labels** (recommended), or a separate canopy object with
   `collision="none"` so only the trunk collides.
7. **Branches** (§3.9): **none** (recommended: the sheet draws none; the skeleton is the trunk and its six roots).
8. **Trunk diameter** (§3.4): **2.0 / 2.1 / 2.3 (top / z 4 / flare start)** (recommended), or 2.3 throughout (the hero
   cells' trunk).
9. **Dressing plan** (§2.4, §3.5): **the f34 + r34 plan (5 rocks, 4 clumps, 3 sprigs, 3 pebbles); front / side / rear
   and exploded judged for content** (recommended).
10. **Comparison cameras** (§3.1): **`f34_sheet (−35, 16)` governing** (probe az ±10, e ±4); `r34_sheet (145, 16)`,
    `front_sheet (0, 8)`, `side_sheet (90, 8)`, `rear_sheet (180, 8)`, kit `top`, `underside`; extras: parts shot
    (−30, 20), `tier_under` (e −35), `trunk_cu (−30, 30)`, `root_cu (−25, 15)`, a scale shot with a 5.5-stud marker.
    Hide the floor in every `*_sheet` render.
11. **Colour** (§5): **needle base / light / deep keys calibrated to the sheet's lit-half `#95BC32`, v > .7 `#A6C434`
    and the dark swatch; blended along each flap and by tier; flap undersides `needle_deep` 35 % as a construction role;
    orange bark `#BE6F30` lit; warm grey rock `#D9C8B5` lit; sand `#E7CC9C`; lime and green plant leaves per leaf**
    (recommended); never by facing.
12. **Stages 5 and 6:** **skip both, recorded** (recommended: nothing glows or moves on the sheet).
13. **Collision** (§7): **hero `precise`, Trunk and tiers `hull`, RootBase `precise`** (recommended), or hero `hull`
    (a solid 12-wide cone round the trunk).
14. **Budget** (§4.3): **4000 limit, planned about 1800–2200, ceiling 3200; parts under 1000** (recommended).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **Floating dressing (STAGES; 035 and 036 round 1).** Every flap, rock, pebble, leaf and hub within 0.03 of a
   neighbour, its core or the patch, chaining to the ground; count floating shells: **0**. Tiers touch by their hubs
   (0.005–0.03), never hover; the M032 pines stood apart until M037 seated them.
2. **Pagoda rings or a smooth cone (W04 H11 partly unmet).** Each tier is a ragged ring of separate broad kite flaps,
   two rows deep (crown one), tips drooping below the notches, a dark crease under every hem; the outline steps in at two
   waists (§2.5 hem and waist targets). Not stacked star skins, not a cone with a zig-zag edge.
3. **Canopy too dark, grey or olive (W04 P2; M035 "lit foliage dark and less lime"; M038 "greens slightly grey";
   M036 "back greens dark").** Calibrate to the rendered lit regions (§5.4): lit canopy within 12 of `#A6C434`, sat ≥
   0.65; a crown that reads lighter than the skirt.
4. **Colour by facing.** No light-right / dark-left paint, no "top faces light". Fields along each flap, by tier, by
   height, by role (the keel sheet, the slits, the cut top); `K.check` facing correlation < 0.5 per material.
5. **Hidden trunk (W04 "trunk hidden", H5).** Bark visible from the sand to the skirt's tips (0.28 H), Ø 2.0–2.3, with
   the root flare and six roots clear of the plants; T 12.8 ± 3 % of the f34.
6. **Plain skeleton (user's tree rule).** Octagonal planked trunk, 2–3 slits, a flare from z 2.5, six kinked
   multi-segment roots of different reach (2.8–4.2), checked in `root_cu`, front, side, rear and underside, not only the
   f34.
7. **Egg rocks (M034 round 1; M037 "rock parts egg-shaped").** Rocks are chunky rounded-angular blocks: a broad base, a
   flat 4–6-corner crown, 10–16 broad facets, W : H 1.3–1.6; no ico-spheres, no `hull_rock` jitter balls.
8. **Pointed-ladder or lettuce plants (STAGES; M036 "ivy mounds"; M038 "cupped lettuce heads").** Clumps of 5–10
   upright lanceolate leaves, each folded on its midrib, 50–75° from horizontal, arching out from a small hub; lime outer
   leaves, green inner ones.
9. **Over-wide patch or base clutter.** The patch is thin (0.15), about 13 × 11; the dressing stays at the trunk's foot
   (r ≤ 5.0) and below 2.4; G in the f34's bottom fifth ≤ 20 %.
10. **The top view.** 8 big points at 45° with the second row between them and a 4-point crown star; no bark, sand or
    rock visible from above.
11. **Bowties** at flap roots, leaf hubs and the hub recess: `M.fix_bowties` on every object, `nonmanifold_verts` 0.
12. **Exact booleans:** only for the roots into the trunk, at the origin, one root at a time, save between them
    (STAGES "Booleans"); nothing else is unioned.
13. **Names and scope.** No `YoungFir*` (W04) and no bare `pine`; only one agent drives a Blender session at a time; no
    commits, pushes or exports in stage agents; don't edit `lib/vfx.py` or the shared helpers (frozen).

## Decisions (main session, 2026-10-29)
The recommendations are accepted except where noted.
1. **Size:** 16 tall. The skirt reaches about 6 from the axis.
2. **Names:** `TieredFir` plus `TieredFirCrownTier`, `…MiddleTier`, `…LowerSkirt`, `…Trunk` and `…RootBase`, with keys `m042_*`. Never `YoungFir*`, which W04 owns.
3. **Flaps:** 8 / 12 / 16 in two staggered rows, with one flap aimed at the front on every tier.
4. **Tiers:** each tier is one closed core-and-hub shell plus separate flaps seated by contact. No booleans.
5. **Stacking:** flat caps and hubs, as drawn. The gaps are read back after the build, and **no floating dressing** is allowed (STAGES rule).
6. **Packaging:** one hero object made of closed shells. Only the roots are unioned into the trunk. Every shell is manifold, with 0 bowties.
7. **Branches:** none. The skeleton is the detailed trunk and roots, which must read in every view.
8. **Trunk diameter:** 2.0 at the top, 2.1 at z 4, 2.3 at the flare.
9. **Dressing:** use the plan from the front and rear three-quarter views.
10. **Cameras:** as listed. `f34_sheet (−35, 16)` governs.
11. **Colour.**
    - Base, light and deep needle keys, calibrated to the sheet's lit canopy and to the dark swatch.
    - Blend along each flap (root to tip) and by tier (the crown lightest).
    - **Not accepted: putting the deep key on flap undersides.** That is colouring by facing. Undersides keep the flap's position-based colour; the lighting makes them dark.
    - Bark lit target `#BE6F30`, rock `#D9C8B5`, sand `#E7CC9C`. Plant leaves are lime or green, per leaf.
    - Rock stays R > G > B.
12. **Lighting and VFX:** skip both and record that they were skipped.
13. **Collision:** hero precise.
14. **Budget:** a limit of 4000, with about 2000 planned.

The front three-quarter shares in §1 (green 72.5 %, trunk 12.8 %) are binding within ±4. The canopy must not read too dark or grey, which was W04's miss.

## Stage 1: Modelling (modeller, 2026-10-29)

The builder is `art/blender/kit/mcp/m042.py` → `build()`. It ran in a background Blender on port 9882, with the work
file `art/blender/assets/kit/wip/M042.blend`.

Every part comes from its own function, and the hero is built from the same functions:
- `tier("crown" | "middle" | "lower")`;
- `trunk_part` (`trunk_body` plus six `root` calls);
- `root_base_part` (`patch`, five `rock`, three `pebble`, ten `clump`).

The objects are `TieredFir` (the hero), `TieredFirCrownTier`, `TieredFirMiddleTier`, `TieredFirLowerSkirt`,
`TieredFirTrunk` and `TieredFirRootBase`, all in `Kit/M042 Young Fir`.

### Flaps

`flap()` makes a closed 16-tri kite:
- a root point, buried in the core;
- the widest section at 0.42 L, with a ridge of 0.11 w and a keel of 0.06 w;
- a second section at 0.75 L, 0.74 w wide, so the tip is broad and blunt rather than a spike;
- the tip.

The spine bends a little at 0.42 L and by `droop` at 0.75 L, so the hem hangs. The chord from root to tip is fixed, so
the tip lands where the table puts it.

How the flaps are kept from cutting each other:
- **Row A.** Every row A flap is rolled the same way about its spine (`ROLL` 7°), so neighbours shingle. A flap that
  would still cut a neighbour is rolled 3° more, then narrowed.
- **Row B.** Row B is laid over row A by `_drape`. Each section is lifted until no sample of its faces (corners, edge
  midpoints, centres) lies below row A's top surface plus a clearance.
- **What counts as a cut.** A crossing only counts when it lies outside the tier's core. `_hits` finds the exact
  points where triangles cross and tests them against the core by ray parity. So root overlaps hidden inside the core
  don't push row B up.

### Changes from the study's §2.2 table

These were made on the renders, measuring the front and f34 tier hems and waists with the study's masks (`tiers_r.py`
and `measure_render.py` in the study folder).

**Tier shape.** The study's chords of about 35° gave a fat, feathery cone with no waists. Row B flaps lifted more than
a stud off row A and stuck out. Now:
- the tiers are cones of flaps lying at 37–42° (the sheet's tier outlines are about 45°);
- row A is rooted low in a small core "plug";
- row B is rooted at the cap, parallel to row A and about 0.6 above it;
- both rows are long: row B reaches 0.85 of row A's radius, as on the sheet's hem, where tips from both rows show.

**Final rows.** Jitter on every flap: tip radius ±4 %, tip height ±0.1, azimuth ±5°, width ±8 %, roll ±3°.

| Tier, row | Flaps | Root r @ z | Tip r @ z (front-facing tip z) | Width | Droop |
| --- | --- | --- | --- | --- | --- |
| Crown, long | 4 | 1.2 @ 13.35 | 2.95 @ 11.6 | 2.1 | 16° |
| Crown, short | 4 | 1.0 @ 13.45 | 2.6 @ 11.9 | 1.85 | 16° |
| Middle A | 6 | 0.75 @ 11.55 | 4.25 @ 8.75 (8.55) | 3.0 | 24° |
| Middle B | 6 | 0.5 @ 12.35 | 3.8 @ 9.6 | 2.25 | 20° |
| Lower A | 8 | 1.1 @ 8.4 | 6.0 @ 4.65 (4.45) | 3.0 | 24° |
| Lower B | 8 | 1.0 @ 9.55 | 5.1 @ 5.85 | 2.7 | 20° |

After draping, each row B tip ended 0.1–0.5 above its design height (logged as `tip_lift`).

**Cores and hubs.** Each core is one closed shell with its hub:
- a pleated frustum with a flat cap. The crown's is the 4 + 4-ridge star cone: apex 16.0, rim radii 1.7, 1.25 and 0.95
  at z 13.3;
- an octagonal hub with a flat bottom and a recess (Ø 0.3, 0.08 deep).

The cores are smaller than the study's:
- lower: cap r 1.2 at z 9.60, rim r 1.9 at z 8.3;
- middle: cap r 0.6 at z 12.53, rim r 1.3 at z 11.3.

The hubs showed as a red band at every waist in the low side views. Two changes fixed that:
- the hub heights went from 0.35, 0.4 and 0.5 to 0.15, 0.15 and 0.3;
- the crown and middle cores carry a short wall down round their hubs (`skirt`, to z 12.57 and z 9.64), which hides
  them from the side.

The brown hub still shows from below (`tier_under`).

**Stack.** Every seat was read back at 0.015:
- the lower hub's bottom at 6.615 sits on the trunk top at 6.6;
- the lower cap was raised from 9.40 to 9.60, so row B's roots clear row A, and the middle hub's bottom is at 9.615;
- the middle cap is at 12.53 and the crown hub's bottom at 12.545.

### Trunk

The trunk is octagonal, with its corners at 22.5° + 45° k:
- **Planks.** Each side is split once and the split pushed in or out 0.07–0.12, giving 16 plank facets.
- **Rings.** The rings are at z 0.05, 0.6, 1.5, 2.5, 3.3, 4.2, 5.0, 5.8 and 6.6, with corner radii 1.9, 1.75, 1.45,
  1.17, 1.10, 1.06, 1.04, 1.02 and 1.0. The flare is stronger than the study's 1.78, 1.62 and 1.36, so the foot reads
  as it does on the sheet.
- **Slits.** Three slits pull the split vertices in 0.14 at two rings: front-left z 3.3–4.2, right z 1.5–2.5 and back
  z 4.2–5.0.
- **Top.** The top is flat, with an inner octagon inset 0.22 and recessed 0.06.

Six roots: each is a pentagon-section prism with an off-centre ridge, kinked once in plan. The ridge rises up the trunk
to z 2.2–2.8, and the blunt tip is sunk in the sand. Heights and widths are about 1.25 × the study's, so the roots stay
chunky to near the tip.

| Root | Azimuth | Reach | Segments |
| --- | --- | --- | --- |
| RF | 285° | 4.2 (1.4 wide × 1.9 tall) | 3 |
| RL | 175° | 3.4 | 2 |
| RFL | 235° | 3.0 | 2 |
| RR | 345° | 3.8 | 3 |
| RB1 | 60° | 3.0 | 2 |
| RB2 | 120° | 2.8 | 2 |

The roots were unioned into the body one at a time, at the world origin, with `m033._union_fine` (merge 0): 6 unions,
no retries. Then `m012._force_slivers` collapsed 17 sliver corners (under 2°, edges up to 0.12).

### Root base

**Sand patch.** A lobed ellipse, 7.2 × 2.8, along 325°/145° (the f34's screen axis).
- It is let out wherever a rock, clump, pebble or root tip needs 0.25 of sand beyond it.
- The crest is flat at 0.15 out to 0.5 inside the outline. A bevel runs down to a knife edge at the outline (a 0.03
  side strip gave 1° slivers). The underside is flat.

**Rocks.** Each rock is the hull of four jittered rings:
- a broad base sunk 0.08;
- the widest ring at 0.3 h;
- a shoulder at 0.72 h;
- a flat five-corner crown.

R1–R5 sit at their §2.4 places, except R1, moved in to (−4.6, −0.2), and R2, moved to (−2.75, −3.45). W : H is
1.3–1.6, so they read as chunky blocks, not eggs. The pebbles are at (−2.3, −4.35), (1.75, −4.15) and (−3.6, 2.9).

**Plant clumps.** Each clump has a closed five-sided hub pyramid sunk 0.03 into the sand. The leaves are 8-tri folded
lanceolate shells (a V channel on the midrib, a keel beneath), based inside the hub. Taller leaves stand at 64–76°,
outer ones at 42–56°.

| Clump | Leaves | Height |
| --- | --- | --- |
| P1 | 10 | 2.6 |
| P2a | 9 | 2.8 |
| P2b | 7 | 2.2 |
| B1 | 8 | 1.6 |
| B2 | 8 | 2.0 |
| Sprigs S1–S5 | 4–5 | 1.0–1.15 |

The clumps are 1.2 × the study's heights: at the study's sizes they read as small spikes beside the sheet's lush clumps.
S4 and S5 were added at the patch's long ends. S2, S3 and the front pebbles were pulled in so the front of the patch
isn't bare.

### Hero

The root base and the three tiers are built into one asset, and the unioned trunk is joined in: one object of 122
closed shells.

## Stage 2: Optimisation and cleanup

| Object | Tris | Size (studs) | Shells | Origin offset in the build frame |
| --- | --- | --- | --- | --- |
| TieredFir | 2714 / 4000 | 12.40 × 11.99 × 16.00 | 122 | (−0.017, −0.112, 0) |
| TieredFirCrownTier | 256 / 1000 | 5.74 × 6.02 × 4.49 | 9 | (0.015, 0.05, 11.506) |
| TieredFirMiddleTier | 316 / 1000 | 7.71 × 8.57 × 4.02 | 13 | (−0.091, −0.12, 8.508) |
| TieredFirLowerSkirt | 368 / 1000 | 11.62 × 11.99 × 5.20 | 17 | (−0.067, −0.112, 4.40) |
| TieredFirTrunk | 784 / 1000 | 7.28 × 6.94 × 6.55 | 1 | (0.117, −0.635, 0.05) |
| TieredFirRootBase | 990 / 1000 | 12.40 × 11.04 × 3.33 | 82 | (−0.017, 0.161, 0) |

**Hero by shell kind:**

| Kind | Shells | Tris |
| --- | --- | --- |
| Patch | 1 | 120 |
| Trunk and roots | 1 | 784 |
| Cores | 3 | 364 |
| Flaps | 36 | 576 |
| Rocks and pebbles | 8 | 286 |
| Leaves and plant hubs | 73 | 584 |

**Mesh checks.** Every object has 0 of each of these:
- non-manifold edges;
- non-manifold (bowtie) vertices (`M.fix_bowties` found none);
- boundary, wire and loose elements;
- zero-area faces;
- n-gons (all faces are triangles);
- duplicate vertices.

On every object the normals face outward, the transforms are applied and the origin is at the bbox bottom centre;
`K.check` reports no problems. Per shell (`shells_report`), every shell is closed and outward (volume > 0) with 0
self-intersections. The smallest corner angle is 2.01°, on the trunk where the roots meet the body after the union;
every other object is at 6° or more.

**No floating dressing** (`contact_report`, tolerance 0.03):
- hero: 0 floating shells and 0 unchained, also at 0.1;
- every flap root is buried in its core;
- hub seats 0.015, 0.015 and 0.015;
- 0 visible flap-flap cuts (crossings inside a core don't count);
- each part on its own: 0 floating, 0 unchained, 0 cuts.

The hero size target in `build()` is now 12.8 ± 0.8 × 12.4 ± 0.8 × 16.0 ± 0.3. The study's 13.4 × 12.6 was an
estimate; the patch is now shaped by the f34's screen axis and the dressing.

## Stage 3: UV

Each object was unwrapped with `M.smart_uv` (angle-based, angle 45, margin 0.008) and then `m012._uv_unfold`. Every
object has 0 overlapping pairs, 0 flipped faces, a minimum gap of 0.016, a border of 0.008 and even density.

| Object | Islands | Conformal stretch, p95 |
| --- | --- | --- |
| Hero | 783 | 1.027 |
| Crown | 89 | 1.041 |
| Middle | 74 | 1.031 |
| Lower | 89 | 1.033 |
| Trunk | 64 | 1.030 |
| Root base | 418 | 1.024 |

## Stage 4: Materials, colour and texture

### Calibration

- **Pass 1** (`m042.calibrate`, kit dome) used the §5.4 targets. The results are in the `PALETTE` comment.
- **Pass 2** used the f34_sheet render, with the floor hidden and the study's masks (`colr.py`). The kit studio lights
  the canopy's two halves almost alike: our left and right canopy medians are #508C2C and #55952C, against the
  sheet's #236735 and #95BC33. So a base calibrated to the sheet's lit half made the whole canopy lime (median
  #9CBE35). The fix:
  - the needle base went down to a mid green;
  - the light key became a yellower lime, used on the flap tips;
  - the deep key became a cooler teal.

**Final keys:**

| Key | Hex |
| --- | --- |
| needle | #437529 |
| needle light | #B0BC2A |
| needle deep | #1E5038 |
| bark | #965B24 |
| bark light | #AB6F39 |
| bark deep | #663F22 |
| rock | #9C9894 |
| rock light | #A9A49F |
| rock deep | #8A8889 |
| sand | #BAA784 |
| sand deep | #9E8B69 |
| plant | #93A134 |
| plant deep | #335A20 |

### Blends

Colour follows position and role only, never facing.

**Along each flap** (root fan, band, tip fan):

| Flaps | Root fan | Band | Tip fan |
| --- | --- | --- | --- |
| Lower A | deep 50 % | deep 25 % | light 50 % |
| Lower B | deep 50 % | needle | light 50 % |
| Middle A | deep 50 % | needle | light 50 % |
| Middle B | deep 25 % | light 25 % | light 75 % |
| Crown hem | deep 25 % | light 25 % | light 75 % |

- **Crown cone:** light 50 %, so the crown is the lightest tier.
- **Flap undersides** take the same key as the faces above them (decision 11).
- **Cores:** deep 75 % (cap 50 %). Hubs are bark deep 75 %; the recess is bark deep.
- **Trunk:**
  - bark deep 25 % on facets below z 1.0, on the roots below z 0.6 and round the slits;
  - bark light on the top face (the cut);
  - bark light 25 % on the outer half of each root's ridge, picked by the ridge vertices, not by normals.
- **Rocks:** light 50 % above 0.72 h, light 25 % above 0.55 h, deep 25 % below 0.22 h.
- **Sand:** deep 50 % on the bevelled rim, deep 25 % within 0.4 of the trunk, roots, rocks and hubs.
- **Plants:** chosen per leaf. The tallest 2–4 leaves per clump are lime (plant) and the rest green (plant deep). Each
  lime leaf's base is a quarter step deeper. Hubs are plant deep with bark deep 25 %.

### Texture and finish

**Tint:**

| Surface | Variation |
| --- | --- |
| Flaps | ±4 % per flap, plus broad noise (amplitude 0.03, scale 0.6) |
| Cores | noise 0.03 / 0.5 |
| Bark | ±4 % per plank column, plus 0.04 / 0.35 |
| Roots | 0.04 / 0.5 |
| Rocks | 0.04 / 0.4 |
| Sand | 0.03 / 0.15 |
| Leaves | ±4 % |

The kit's `baked_shading` is 0.00 on every object (0.01 on the root base), so no colour follows facing.

**Finish:**
- needles and plants: roughness 0.85, low specular;
- bark: 0.9 (deep 0.95);
- rock: 0.85;
- sand: 0.95.

### Re-measured

f34_sheet against the sheet's f34 cell:

| Region | Ours | Sheet | Note |
| --- | --- | --- | --- |
| Canopy median | #53922C | #508733 | within 12 |
| Canopy lit (v > .7) | #9BBE2C | #A6C434 | within 11 |
| Canopy shade quartile / left half | #2C511B / #508C2C (h 98) | #17472A / #236735 (h 136) | the studio's light; can't be painted (decision 11) |
| Trunk lit (right) half | #A9642F | #B3692F | within 10, R > G > B |
| Trunk median | #A5622E | #653D25 | the studio lights our shade side |
| Rock median / lit | #B9B19F / #DAD2BE | #A19D92 / #E8DAC3 | R > G > B, not mauve |
| Sand median | #E3C492 | #E7CC9C | within 8 |
| Plants median / lit | #6F8B2B / #A3C52F | #487427 / #AAC031 | ours a step lighter |

## Stage 5: Lighting

Skipped, because the sheet shows nothing that glows. There is no emission and there are no lights.

Studio-side checks (Requires Manual Validation), under Roblox's sun:
- the canopy reads lime on the lit side and deep green in shade, not dark and flat (W04's miss);
- the bark is orange-brown, not red;
- the rocks are warm pale grey.

## Stage 6: VFX

Skipped, because the sheet shows no effect. There are no sockets; `build()` checks that the hero has none.

## Renders and measurements (fresh session, final build)

The renders are in `art/blender/renders/models/M042/`:
- `M042_views.png` and the kit views: front34, rear34, front, side, rear, top, underside;
- the sheet views: `f34_sheet (−35, 16)`, `r34_sheet (145, 16)`, `front_sheet (0, 8)`, `side_sheet (90, 8)`,
  `rear_sheet (180, 8)` and `top_sheet`;
- the parts, each at (−30, 20): `part_*`;
- the close-ups:
  - `tier_under`: the middle part from below, e −35;
  - `trunk_cu`: the Trunk part at (−30, 30);
  - `root_cu`: the trunk's foot at (−25, 15);
- `exploded`;
- `scale`, with a 5.5-stud marker.

Class shares in percent; the sheet's values are in brackets.

| View | W : H | G | T | S | R |
| --- | --- | --- | --- | --- | --- |
| f34_sheet | 0.818 (0.808) | 68.6 (72.5) | 12.5 (12.8) | 7.6 (3.4) | 9.6 (8.7) |
| r34_sheet | 0.818 (0.698) | 69.0 (76.4) | 12.7 (13.1) | 3.7 (3.3) | 8.2 (4.4) |
| front_sheet | 0.727 (0.722) | 71.8 (76.6) | 11.8 (10.5) | 4.9 (2.5) | 10.4 (7.7) |
| side_sheet | 0.696 (0.652) | 72.4 (78.6) | 13.6 (10.5) | 2.1 (2.4) | 7.7 (6.0) |
| rear_sheet | 0.722 (0.687) | 71.0 (78.5) | 12.3 (11.5) | 2.6 (2.0) | 9.3 (5.9) |
| top_sheet | W : D 0.983 (0.989) | 92.9 (97.2) | 0.7 | 4.4 | 0.8 |

**Tier hems and waists.** Each pair is h / width, the width as a fraction of the canopy's widest row; the sheet's
values are in brackets.

| Feature | f34 | Front | Side |
| --- | --- | --- | --- |
| Canopy W : H | 0.662 (0.658) | | |
| Crown hem | | .757 / .50 (.734 / .50) | .756 / .50 |
| Crown–middle waist | .75 / .41 (.74 / .34) | .740 / .40 (.716 / .32) | .748 / .37 (.716 / .32) |
| Middle hem | .605 / .71 (.614 / .71) | .563 / .66 (.576 / .73) | .576 / .72 (.576 / .73) |
| Middle–lower waist | .593 / .48 (.567 / .47) | .557 / .52 (.537 / .46) | .570 / .46 (.528 / .48) |
| Lower hem | .40 / 1.0 (.38) | .346 / 1.0 (.336) | .347 (.345) |

## Modeller's notes for the verifier

**Judge colour against the lighting.** The kit studio lights the f34's left half nearly as brightly as the right. The
sheet's dark teal left half can't appear without painting by facing, which isn't allowed. The canopy median and the lit
median are within 12 of the sheet; the shade half's hue (98° against 136°) is the studio's light.

**Known misses:**
- In the f34, sand is 7.6 % against 3.4 ± 2. The patch is as wide as the sheet's (W : H 0.818), but plants cover less
  of it.
- In the f34, green is 68.6 %, right at the lower edge of the binding ± 4 band (68.5).
- In the r34, side and rear cells, green runs 4–7 points under the sheet and trunk 1–3 points over.
- The crown–middle waist is 0.37–0.41 wide against 0.32–0.34.
- The plant clumps render a step lighter than the sheet's.

**Changed from the study, and why:**
- The tier chords are steeper and the row B flaps long and parallel to row A: the study's numbers gave no waists.
- The core plugs are smaller, and the lower cap sits at 9.60.
- The hubs are shorter and the cores have skirts, because the hubs showed as a red band at every waist.
- The trunk flares more and the roots are chunkier.
- There are 65 leaves in 10 clumps; the study planned 49 in 7.
- The patch is a 7.2 × 2.8 ellipse along the f34's screen axis.

**Contact:**
- no shell floats, and every shell chains to the ground;
- the flap roots are buried in their cores;
- row B rests on row A with no visible cut;
- leaves may touch rocks and roots.

**Trunk union:** 6 exact unions at the origin, no retries, 17 sliver corners collapsed. The smallest corner is 2.01°.

No commits, pushes or exports were made. The work file `art/blender/assets/kit/wip/M042.blend` holds the final build.

## Verification round 1 (verifier, 2026-10-29)

A fresh verifier ran this round, read-only, on port 9882 with `wip/M042_verify.blend`. Nothing was built, edited or
saved. The renders went to the scratchpad (`…/scratchpad/m042_verify/M042/`), made with `m042.render_views` and
`M.MODEL_RENDERS` redirected there. Every number below was measured again, using the verifier's own per-shell and
contact code, `M.audit`, `K.check`, and the study masks (`measure_render.py`, `colr.py`) on both images.

### Measured

| Object | Tris / budget | Size (studs) | Shells | Bad shells* | Min corner | Floating / unchained | Origin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TieredFir | 2714 / 4000 | 12.40 × 11.99 × 16.00 | 122 | 0 | 2.01° (trunk) | 0 / 0 | bbox bottom centre (±6.2, ±5.995, z 0) |
| TieredFirCrownTier | 256 / 1000 | 5.74 × 6.02 × 4.49 | 9 | 0 | 9.99° | 0 / 0 | bottom centre |
| TieredFirMiddleTier | 316 / 1000 | 7.71 × 8.57 × 4.02 | 13 | 0 | 7.61° | 0 / 0 | bottom centre |
| TieredFirLowerSkirt | 368 / 1000 | 11.62 × 11.99 × 5.20 | 17 | 0 | 6.09° | 0 / 0 | bottom centre |
| TieredFirTrunk | 784 / 1000 | 7.28 × 6.94 × 6.55 | 1 | 0 | 2.01° | — | bottom centre |
| TieredFirRootBase | 990 / 1000 | 12.40 × 11.04 × 3.33 | 82 | 0 | 8.17° | 0 / 0 | bottom centre |

\* A bad shell has any of these: an edge without exactly 2 faces, a bowtie vertex, a self-intersection inside the
shell, a zero-area face, an n-gon, or volume ≤ 0. Every object, as a whole, has 0 non-manifold edges or vertices, 0
boundary, wire or loose elements, 0 zero-area faces, 0 n-gons and 0 duplicate vertices. Normals face outward,
transforms are applied (rotation 0, scale 1), there are no custom normals and no modifiers, and `K.check` reports
nothing.

- **Contact.** Over the whole hero, every non-ground shell overlaps or lies within 0.03 of another shell; the largest
  gap is 0.000. All 121 shells chain to the patch. `m042.contact_report` agrees: hub seats 0.015 / 0.015 / 0.015, 0
  flap–flap cuts, shells patch 1 / trunk 1 / cores 3 / flaps 36 / rocks + pebbles 8 / leaves + plant hubs 73.
- **Front three-quarter (`f34_sheet`) shares**, ours (sheet):
  - G 68.6 (72.5): **inside the binding ±4, 0.1 above the floor**;
  - T 12.5 (12.8): binding, met;
  - S 7.6 (3.4), outside the study's ±2;
  - R 9.6 (8.7);
  - W : H 0.818 (0.808).
- **Other views**, G / T / S, ours (sheet):

  | View | G | T | S |
  | --- | --- | --- | --- |
  | r34 | 69.0 (76.4) | 12.7 (13.1) | 3.7 (3.3) |
  | front | 71.7 (76.6) | 11.8 (10.5) | 4.9 (2.5) |
  | side | 72.4 (78.6) | 13.6 (10.5) | 2.1 (2.4) |
  | rear | 71.0 (78.5) | 12.3 (11.5) | 2.6 (2.0) |

  Top: G 92.9 (97.2), S 4.4 (0), W : D 0.983 (0.989).
- **Colour.** Ours against the sheet; both images measured with the same masks.

  | Region | Ours | Sheet | Δ / verdict |
  | --- | --- | --- | --- |
  | f34 canopy median | #53922F | #508733 | ≤ 11, ok |
  | f34 canopy v > .7 | #9CBE31 | #A6C434 | ≤ 10, ok |
  | f34 canopy saturation / value medians | .70 / .56 | .70 / .50 | not dark, not grey |
  | f34 left (shade) half | #508C2F (h 99) | #236735 (h 136) | studio light (see below) |
  | r34 canopy median | #3F7427 | #468233 | 7 / 14 / 12, at the edge |
  | r34 lit quartile | #7D9E2A | #A1C133 | darker |
  | front canopy median | #528A2E | #488433 | ok |
  | f34 trunk lit (right) half | #A9642F | #B3692F | ≤ 10, R > G > B |
  | f34 rock v > .7 | #CFC6B3 (h 42) | #DACDB8 | ≤ 11, R > G > B, not mauve |
  | f34 sand | #E3C492 | #E7CC9C | ≤ 10 |
  | f34 plants median / lit | #708D30 / #A4C534 | #487427 / #AAC031 | lighter and yellower |
  | front plants median / lit | #505D1E (h 72, v .36) | #53772B (h 88) | olive |

- **Colour by facing.**
  - Material luminance against the normal's z, per family: needle 0.02, plant 0.01.
  - Rock 0.89, but its keys sit in disjoint height bands within each rock (deep t < .22, base .28–.49, light 25
    .55–.68, light 50 > .79), so this is position. Every top face is in the top band because of the geometry, and the
    luminance step is only about 6 levels.
  - Bark 0.51: the cut top face (a role) and the ridge picked by vertex.
  - Sand 0.43: the bevelled rim (position).
  - `baked_shading` is 0.00–0.01 on every object.
  - **Flap undersides:** across all 36 flap shells, faces with nz > 0.2 and faces with nz < −0.2 differ in mean key
    luminance by **0.0**. Decision 11 is followed.
- **Tint.** One value per face (4 of 2714 faces vary across their corners), uncorrelated with facing (|r| < 0.08).
  Ranges: needle 0.93–1.06 (sd 0.026), bark 0.94–1.06, rock 0.97–1.03, sand 0.98–1.02, plants 0.96–1.04. Broad and
  subtle, no confetti.
- **Lighting and VFX.** 0 sockets, 0 lights and 0 emissive materials on the hero; collision `precise`. As decided.

### Findings

1. **Trunk sliver corners (minor, no action).**
   - **Finding.** 54 corners are under 5° (the smallest is 2.01°), all on the trunk where the roots were unioned.
   - **Why it doesn't matter.** No face is zero-area, the shell is closed and manifold, and the faces are flat shaded.
     These triangles render cleanly and import into Roblox without trouble.
   - **Optional fix.** If the trunk is touched again for any reason, collapse the corners under 3°.
2. **The canopy is sparser and spikier than the sheet (minor, the top priority for any round 2).**
   - **Finding.** On the sheet each tier is a dense, closed skirt of broad flaps: the outline is clean and stepped, the
     hems droop, and no interior shows. Ours reads more like a shingled cone. Gaps between flaps show the dark core,
     and the lower skirt's side flaps stick out flat as thin spikes in the front, side and rear views. The crown hem and
     the middle tier merge in the f34; the crown–middle waist measures 0.41 against 0.34.
   - **Effect on the numbers.** This is why green sits at 68.6 (the edge of the binding band) and runs 5–7 points under
     the sheet in the r34, side and rear views. Three tiers, two waists and drooping kite flaps do all read, so it is
     not a wrong silhouette.
   - **Fix targets.**
     - Widen the row A and row B flaps by about 10–15 % (or add 2 short inner flaps per tier) until they overlap with
       no core visible.
     - Bend the lower skirt's outer 0.25 L down a further 8–10°, so the side tips hang rather than spike.
     - Pull the crown hem tips in to r ≈ 2.6, so the crown–middle waist comes to ≤ 0.37.
     - Target: f34 G ≥ 71, and r34 / side / rear G ≥ 72.
3. **Lime tips on every flap (minor).**
   - **Finding.** The tip fans carry `needle_light` at 50–75 %, so every flap ends in a regular lime triangle: a
     scale pattern the sheet doesn't have. On the sheet, colour changes little along a flap. It is positional, not
     facing, so it is allowed.
   - **Fix target.** Tip fans at light 25 % on rows A, keep 50 % on the crown, and move the remaining difference to
     whole tiers (the crown lightest).
4. **Too much sand in the f34 (minor; sand is not binding).**
   - **Finding.** Sand is 7.6 % against 3.4 ± 2. The front lobe of the patch is a broad bare strip, and the sand shows
     past the canopy from above (top S 4.4 % against 0).
   - **Judgement on the patch-shape change.** The ellipse along the f34 screen axis is fine for the f34 width (W : H
     0.818). But the patch is deep toward the camera and too bare.
   - **Fix targets.**
     - Pull the front lobe in by about 0.6, or add one more front sprig or clump between R2 and P2.
     - Trim the two plan corners that stick out beyond the canopy.
     - Targets: f34 S ≤ 5.4, top S ≤ 2.
5. **Rear-lit canopy darker (minor).**
   - **Finding.** The r34 canopy median is 7 / 14 / 12 under the sheet. Only 425 px are at v > .7, against 6058 on the
     sheet. The cause is the studio key light, not the paint: the f34 and front medians are within 11.
   - **Requires manual validation in Studio** under the game sun (W04 P2). If the colour is changed at all, raise
     `m042_needle` value by about 5 %.
6. **Ground plants olive and spiky (minor).**
   - **Finding.** The front-cell plant median is #505D1E (h 72, v .36) against the sheet's #53772B (h 88). The f34 lime
     leaves are close (lit #A4C534 against #AAC031). The clumps are narrow, agave-like spikes, where the sheet draws
     broader, leafier lanceolate leaves.
   - **Fix targets.**
     - Move `m042_plant_deep` toward #3E7226 (h ≈ 95).
     - Widen the leaves by about 25 %.
7. **Shell and decision checks (pass).**
   - Flaps 8 / 12 / 16 (36 shells), with one row A flap at 270° on every tier.
   - Cores and hubs are closed shells; the seats are 0.015; no booleans except the trunk roots.
   - One hero object; trunk Ø 2.0 / 2.12 / 2.34 at z 6.6 / 4.2 / 2.5 (corner radii); no branches.
   - Dressing on the f34 + r34 plan: 5 rocks, 3 pebbles, clumps on both sides.
   - Keys `m042_*`, names `TieredFir*` (no `YoungFir*`).
   - The underside keys are not on undersides; no lighting or VFX; collision precise; 2714 tris.
   - The trunk's octagon, planks, slits, top inset and six chunky roots read in `part_trunk`, `trunk_cu` and
     `root_cu`. The root flare and roots read in the f34, r34, front and rear views, and as a flare in the side view.
   - The rocks are chunky, faceted, rounded-angular blocks, not eggs.
   - The tier parts match their exploded cells well: broad drooping kites round a cap. `tier_under` shows the brown
     octagonal hub with its dark recess.
8. **The modeller's changes, judged.**
   - **Steeper flaps (37–42°):** accepted. They make the waists, and the sheet's outlines are about 45°.
   - **Hidden hubs (shorter hubs plus core skirts):** accepted. There is no red band at the waists, and the hub still
     shows from below, as drawn.
   - **Chunkier base (65 leaves in 10 clumps, 1.2× heights):** accepted, with finding 6 on the leaf shape.
   - **Patch shape:** accepted, with finding 4.
   - **Hero size check changed to 12.8 ± 0.8 × 12.4 ± 0.8 × 16 ± 0.3:** accepted. Decision 1 fixes only the 16 height
     and a skirt reach of about 6. The skirt's Y extent of 11.99 gives r 6.0.

### Score and verdict

**7 / 10. PASS.** No blockers:
- the mesh is clean;
- the budgets are met;
- no dressing floats;
- the silhouette is a three-tier fir on a visible rooted trunk;
- the colour family is right, and nothing is coloured by facing;
- every decision was followed;
- the binding shares are met (G 68.6, only just; T 12.5).

If the main session spends the optional second round, finding 2 (fuller, less spiky tiers) comes first, then
findings 3 and 4.

## Main session ruling (2026-10-29)
Passed in round 1 (7/10) and committed. All five modeller changes are accepted.

**Left for a later polish pass:**
- The canopy is sparser and spikier than the sheet's, and the crown waist is wide (0.41 against 0.34). Targets: flaps 10–15 % wider, lower tips bent down a further 8–10°, crown hem at r ≈ 2.6, and f34 green ≥ 71.
- The lime tip on every flap reads as a scale pattern. Use a 25 % tip blend on row A.
- There's too much sand: f34 shows 7.6 % against 3.4 %.
- The ground plants are olive and spiky. Move `plant_deep` toward `#3E7226`, with leaves 25 % wider.
- The rear canopy looks dark because of studio light. Check it in Studio.

**Export:** 6 assets, 6 solid pieces, 5428 tris, 0 VFX sockets, palette 25 colours, 0 problems.
