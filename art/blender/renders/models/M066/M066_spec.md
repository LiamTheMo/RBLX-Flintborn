# 066 Canvas Shelter — spec

Reference: `art/blender/assets/references/066.png` (1024 × 1536 px). INDEX.md row 66: "Canvas Shelter Model Study".
The sheet's own header reads **"PAGE 65/132"** (top right), title **"CANVAS SHELTER"**, subtitle "OPEN WOODEN SHELTER WITH
CANVAS CANOPY", header tag "FLINTBORN / ASSET PRODUCTION REFERENCE", footer "FLINTBORN — INDIVIDUAL MODEL STUDY" (our
number is INDEX's 066, §3.1).
Builder: `art/blender/kit/mcp/m066.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows an effect: a glowing hanging lantern
(its own "VFX (SEPARATE)" panel) plus two glowing candle jars on the table** (§7). The subject is **one open, walk-under
camp shelter with its furnishings**: **four chunky square timber posts on pale stone bases**, a **ridge pole** lashed
between the two tall right-hand posts, a **cream canvas canopy** tied at its four corners with **rope X-lashings** and
sagging deeply in the middle (one corner, at the ridge pole, higher than the others), short **crossbars** at the corner
lashings, **rope collars** at the post feet with **wooden pegs** bracing each base, a **red banner with a white diamond**
on an iron rod, a **hexagonal dark-metal lantern** with amber glass, and under the canopy a **plank table** with items, a
**long bench**, a **short bench** and a **stool**, plus **two open straw-filled crates**, a **hooped barrel** and **two
pale stone blocks**.

Sheet text (paraphrased):
- **Title block:** a simple outdoor camp shelter of timber posts and a stretched canvas canopy, with bench and table
  furnishings, a hanging lantern and a banner.
- **"FRONT THREE-QUARTER VIEW"** and **"REAR THREE-QUARTER VIEW"**: the assembled shelter with furniture and dressing.
  The second is not a rear view (§3.3).
- **"ORTHOGRAPHIC VIEWS"**: "FRONT VIEW", "SIDE VIEW", "REAR VIEW", "TOP VIEW". None of them draws the ridge pole, and
  the side view's back post disagrees with every other view (§3.2, §3.4).
- **"EXPLODED CONSTRUCTION / MAIN PARTS AND ASSEMBLY"**, labels: "Ridge Pole", "Canvas Canopy", "Wood Post (x4)",
  "Banner & Rod (x1)", "Peg (x4)". Unlabelled pieces: three lanterns, a long table, a long bench, a short bench, a
  stool, a barrel, two open crates, two stone cubes, small table items.
- **"KEY CLOSE-UPS"**:
  - **"RIDGE POLE JUNCTION"**: the canvas is looped over the ridge pole and tied to the posts with rope lashings. A
    square post with a square-cut top, a fat X-lashing (horizontal turns plus a diagonal cross) and a square beam end
    sticking out beside it; canvas enters the lashing from both sides.
  - **"POST BASE & PEG"**: the post stands on a grey stone base block; a gold rope collar at the post foot; a square
    wooden peg leans against the block, tied with rope; the canvas is tensioned to the ground with the peg (§3.10).
  - **"CANOPY UNDERSIDE"**: the canvas has simple low-poly thickness and clean folded planes. The ridge pole crosses
    overhead with a lashing; the canvas rim reads as a darker strip.
- **"MATERIAL PALETTE"**: six swatches — Timber (Primary), Canvas (Primary), Rope (Detail), Stone (Base), Banner
  (Accent), Lantern (Accent).
- **"MODEL NOTES"**: modular reusable parts (posts, ridge pole, canvas panel, furniture, crates, lanterns, banner);
  chunky readable forms with broad flat faces; simple clean shapes, limited detail; the canvas is one sheet with tied
  corners and a slight sag; posts sit on stone bases and are braced with ground pegs; primitive, hand-built, low-poly,
  solid colours, no texture noise; game-friendly resolution with clear part separation.
- **"VFX (SEPARATE)"**: "Lantern Light (VFX)": the glow is a separate effect, not part of the solid geometry; keep the
  lantern mesh simple and clean.
- **Game context and the old kit:**
  - **W10 row 1 `CampAwning`** (`art/blender/scripts/kit/W10/camp_awning.py`; manifest `art/roblox/kit/W10/manifest.json`;
    goals `art/blender/renders/kit/W10/camp_awning_goals.md`; compare `camp_awning_compare.png`) is the old kit's version
    of this same design (four posts, sagging canvas, two banners, a lantern at the front-right post, table and benches).
    The **exported** hero is **10.87 W × 8.18 H × 10.08 D, 1650 tris, `precise`**; parts `CampAwningCanvasCanopy` (8.6 ×
    1.88 × 7.6, 256 tris, `none`), `CampAwningWoodPost` (0.82 × 6.67, 68 tris, `box`), `CampAwningRidgePole` (10.07 long,
    20 tris, `box`), `CampAwningPeg` (0.28 × 0.8, 12 tris), `CampAwningTableSet` (3.6 × 1.74 × 4.4, 228 tris, `box`);
    variants `CampAwningSquareStall`, `…LongShelter`, `…LeanTo`, each with one `heat_glow`. Palette `w10_wood #8A4A22`,
    `w10_canvas #E3CFA0`, `w10_rope #C48A38`, `w10_stone #9A9498`, `w10_banner #B8191F`, `w10_iron #575B64`,
    `w10_lantern #FFB022`. Its goals asked for head clearance ≥ 7 under the canopy centre. `MODEL_PROGRESS.md` row 81:
    **"flat sheet (ref draped canvas on 4 posts); sparse clutter; no lantern glow"**; `art/reference/kit/CHECKLIST.md`:
    CampAwning 7/10. In its render the posts are thin round sticks, the canvas a flat slab and the canvas yellowish.
  - **Siblings:** M064 `CanvasTent` (spec `art/blender/renders/models/M064/M064_spec.md`) sets this family's timber,
    canvas, rope, crate, barrel and lantern rules (closed canvas slabs, twisted rope that touches what it ties, Neon
    glass with a `heat_glow` halo, walk-in collision). M051 / M052 are the nearest committed timber-and-rope builders.
    WorldModeling §13.1 (timber vocabulary), §13.3 (canvas: low-res grid, a few purposeful height moves, thin
    thickness; ties where the cloth really attaches), §13.8 (crate, barrel, table/bench, lantern, banner recipes).

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The page is near-white
(`#FAF8F4`); pieces cast a soft warm-grey shadow down and to the left (s < 0.13). Measured frame rules (`lines2.py`):
top 3/4 panel y 50–505 (no divider; the title text block sits top-left over the f34); ortho panel y 508–759 with cell
dividers x 294, 505, 772; exploded panel x 13–686 y 767–1274; close-up panel x 690–1011 (cells y 806–952, 968–1111,
1123–1270, art x 703–887); palette panel x 13–278 y 1281–1488; notes panel x 279–690; VFX panel x 690–1011; footer
rule y 1509.
- **Cells** (`m.V`, `m.X`): f34 (60,125,560,498); r34 (562,60,1011,478); front (14,528,293,725); side (297,528,504,725);
  rear (507,528,771,725); top (774,528,1010,725); exploded (14,820,685,1270); cu1 junction (703,806,887,952); cu2 base
  (703,968,887,1111); cu3 underside (703,1123,887,1270); VFX lantern (705,1318,848,1466).
- **Swatches** (inner boxes, sd ≤ 1.8): Timber (37,1319,62,1334); Canvas (37,1346,62,1361); Rope (37,1373,62,1389);
  Stone (37,1401,62,1416); Banner (37,1427,62,1443); Lantern (37,1454,62,1470).
- **Masks** (`cls()` in `m.py`, HSV, h in degrees; a 2 × 2 opening drops specks; background = (s < 0.13, v ≥ 0.75,
  h 25–75) or (s < 0.05, v ≥ 0.75), which removes the warm-grey cast shadow):
  - **C** canvas: h 25–62, s 0.13–0.40, v ≥ 0.78 (also catches the crate straw, the paper and the banner's white emblem
    edges: small).
  - **W** timber and every wood (posts, ridge, furniture, crates, barrel) plus deep warm shade: warm, s ≥ 0.40 (not R, Y,
    B), plus warm s ≥ 0.25 with v < 0.62.
  - **R** rope: h 30–50, s ≥ 0.40, v ≥ 0.62 (catches the brightest lit timber edges a little).
  - **Y** glow: h 36–60, s ≥ 0.80, v ≥ 0.90 (lantern glass and candle jars).
  - **B** banner red: h ≥ 345 or < 8, s ≥ 0.60, v ≥ 0.45. **K** metal / dark: v < 0.30, s < 0.45. **S** stone: s < 0.25,
    v 0.35–0.92, h < 26 or ≥ 200 (stone bases, loose stones, barrel hoops, the grey banner rod). **G** grass and the green
    bottle: h 62–160, s ≥ 0.25.
  - Apply the same code to our renders (studio floor hidden, plain background).

**Scratch study material** (no Blender) in `<temp>\m066_study\` (the session scratchpad). Run with `uv run --no-project
--with pillow --with numpy --with scipy python <script> < /dev/null`.
- **Helpers:** `m.py` (boxes, `cls`, `clsimg`, `hsv`), `zoom.py` (`zoom.py x0 y0 x1 y1 scale out.png [grid]`),
  `probe2.py` (`probe2.py x,y …` → hex and HSV), `lines2.py` (frame rules), `sw2.py` (swatches), `emb.py` (banner
  white / red, straw, barrel top, hoops, lantern frame, bottle, jars), `man.py` (manifest names), `mani.py` (old
  CampAwning export sizes).
- **Measurements:** `measure.py` (bbox, W : H, fill, class shares, per-fifth shares, width profile; writes
  `cls_views.png`); `samp.py` → `samp_out.txt` (class medians per view and per named region, with lit and shade
  quartiles).
- **Zooms:** `z_fs.png` (front + side, 2×), `z_rt.png` (rear + top), `z_front.png` / `z_side.png` / `z_rear.png` (3.5×,
  grid 5, used for every ortho number below), `z_f34.png`, `z_f34_top.png` (ridge junctions, lantern ring, banner rod),
  `z_f34_bl.png`, `z_r34.png`, `z_r34_top.png`, `z_expl.png`, `z_ex_bl.png` (barrel, crate, peg), `z_peg.png`, `z_cu.png`,
  `z_pal.png`, `z_vfx.png`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** a walk-under camp structure with furniture and dressing: **full asset, hero budget 4000 tris, plan
  about 3300–3850; every part under 1000** (decision §8.16).
- **Overall read (check this first).** An **open square-ish shelter, wider than deep and about as tall as it is wide**:
  - **four thick square orange-brown posts**, the two on the right **taller** (12.0) than the two on the left (10.4), each
    standing on a **pale grey stone block** with a **gold rope collar** at its foot and a **peg** leaning on the block;
  - a **square ridge pole** lashed along the top of the two tall posts, its ends sticking out past them;
  - a **cream canvas sheet** tied by its four corners into **fat gold X-lashings** near the post tops, sagging deeply into
    a belly in the middle with an **X of soft creases** from the corners to the centre; the corner at the ridge pole is
    the **high point** (the canvas folds over the pole there);
  - short **crossbars** through the corner lashings, a **red swallowtail banner with a white diamond** hanging from an
    iron rod at the front-right post, a **hexagonal lantern with glowing amber glass** hanging from the front-right
    crossbar;
  - under the canopy a **plank table** (two glowing candle jars, a green bottle, a paper, a pot), a **long bench** behind
    it, a **short bench** in front, a **stool** at its right end; round the edges **two open crates full of straw**, a
    **barrel with blue-grey hoops**, **two pale stone cubes**.
  - It reads **orange-brown timber first (posts and furniture), then the cream canopy, then the red banner and the gold
    rope, then the lantern glow**: f34 W 52.8 %, C 26.4, B 7.7, R 6.0, S 4.6, Y 0.8.
- **Focal silhouettes, in order:**
  1. Four posts framing a deep cream hammock of canvas with one high corner; the ridge pole on the tall side.
  2. The red banner and the glowing lantern at the front-right post.
  3. The table and benches under the canopy; the lashings and collars; crates, barrel and stones round the base.
- **Target size: tall posts 12.0, short posts 10.4 (both measured from the ground, on 1.2 stone bases); post centres
  12.8 (X) × 9.2 (Y); canvas corners 9.0 / 9.0 / 9.2 / 10.6, canvas lowest point ≈ 7.05; hero with dressing about 17.3
  W × 12.3 D × 12.0 H** (decision §8.1). Tolerances: post tops ±0.3, post spacing ±0.4, canvas corners ±0.3, lowest point
  ≥ 6.9.
  - **How it was derived.** No piece carries a real size. The orthos are consistent in scale with each other and the
    **furniture** is drawn at realistic proportions, so the scale comes from the furniture and the kit's crate:
    - Front cell (`z_front.png`): ground y 711.4; left post x 46.4–62.1, top y 564.9 (**146.5 px**); right post x
      240.7–256.4, top y 540.9 (**170.5 px**); post width 15.7 px; post centres 54.2 / 248.5 (**194.3 px apart**);
      canvas ties y 587 (left) / 573 (right); canvas lowest y 627; table x 86–191 (105 px), top y 674 (37 px tall); bench
      seat y ≈ 690 (21 px); crate x 206–239, top y 677.7 (33 px square); foot collars y ≈ 690 (21 px up); banner x
      246–276 × y 571–660 (30 × 89 px), its rod y 568.6 from x 235 to 282; right lantern x 216–234 × y 578–633 (body
      ≈ 16 × 33 px plus its ring).
    - Side cell: post centres 335.5 / 466.7 (**131 px**); left post top y 540.9 (172 px), right post top y 598.6 (114 px);
      canvas ties y 560 / 607; lantern x 353–369 × y 579–633.
    - Rear cell: post centres 554 / 726.7 (**172.7 px**); left post top y 550.7 (163 px), right y 565.9 (148 px); canvas
      ties y 569 / 599; canvas lowest y 643.6.
    - **At 0.070 stud / px** (tall post 170.5 px = 12.0 → 0.0704; the crate 33 px = 064's 2.3 crate → 0.0697): tall post
      12.0, short post 10.3, post 1.10 wide, post spacing 13.6 (front) / 12.1 (rear) / 9.2 (side), table 7.35 long × 2.6
      tall, bench seat 1.5, crate 2.3, banner 2.1 × 6.2, lantern body 1.1 × 2.3, canvas ties 8.7 / 9.7, canvas lowest
      5.9 (front) / 4.9 (rear).
  - **Why this size.**
    - **Against the character (5.5):** the table is 0.47 C, the benches 0.27 C and the crate 0.42 C (real-world
      proportions for a 0.75 m table, a 0.45 m bench seat and a 0.75 m crate at 1.8 m per character). The tall posts are
      2.2 C. Characters **walk under the canopy** (lowest point 7.05, 1.5 above head height) and **sit on the benches**
      at the table.
    - **Against the kit:** crate 2.3 and barrel 2.8 match M064's 2.3 crate and 2.7 barrel; the shelter is the same class
      as M064's tent (13.7 × 11.7 × 11.0) and W10 `TimberHut` (13.0 × 10.7 × 12.5); W10 `CampAwning` (10.9 × 8.2 ×
      10.1) was too small for its own furniture (its posts 9.1).
    - **Smaller is worse:** at tall posts 10.0 the canvas belly drops to head height (≈ 5.9) and the table is a toy
      beside the character. **Larger** (posts 14) makes the crates and barrel read as toys.
- **Build frame (decision §8.2):** front −Y (the face the front cell shows: banner and lantern at its right post), +X
  right (the tall side with the ridge pole), ground z 0, the post rectangle centred on x 0, y 0. Stage 2 puts the origin
  at the bbox bottom centre (it lands at about (+0.70, −0.25, 0) of the build frame because of the banner rod and the
  front stone) and stores the offset (§2.12).

### 1.2 Measured views (`measure.py`)

| View (box) | Hero bbox (px) | W : H | fill | C | W | R | Y | B | K | S | G |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **f34** (60,125,560,498) | 73–542 × 140–483 (470 × 344) | **1.366** | 0.530 | **26.4** | **52.8** | 6.0 | 0.8 | **7.7** | 0.9 | 4.6 | 0.8 |
| r34 (562,60,1011,478) | 582–985 × 73–446 (404 × 374) | 1.080 | 0.537 | 31.4 | 51.7 | 9.0 | 0.5 | 3.2 | 0.8 | 2.7 | 0.7 |
| **Front** (14,528,293,725) | 36–282 × 540–712 (247 × 173) | **1.428** | 0.439 | 23.6 | 53.1 | 4.4 | 1.2 | 10.5 | 1.6 | 5.1 | 0.6 |
| Side (297,528,504,725) | 316–485 × 540–713 (170 × 174) | 0.977 | 0.366 | 18.0 | 67.3 | 8.0 | 0.8 | 0.0 | 1.7 | 3.1 | 1.1 |
| **Rear** (507,528,771,725) | 526–755 × 550–713 (230 × 164) | **1.402** | 0.541 | 30.6 | 59.5 | 4.5 | 0.4 | 1.3 | 1.7 | 1.2 | 0.7 |
| Top (774,528,1010,725) | 798–990 × 529–724 (193 × 196) | 0.985 | 0.632 | 64.5 | 30.3 | 2.3 | 0.1 | 0.0 | 0.8 | 1.0 | 1.0 |

- Shares are % of the silhouette (background and cast shadow excluded). The tall timber share in every view is the four
  posts plus the furniture; the canvas is pale and thin in the orthos (seen nearly edge-on).
- **Per fifth of height** (top → bottom, C / W / R / B): front 5/81/7/2, 56/20/6/16, 35/33/4/22, 0/75/5/11, 1/80/3/0 (post
  tops and lashings, then the canvas hammock and the banner, then furniture and post feet); side 17/67/14/0, 63/32/3/0,
  14/59/22/0, 1/92/3/0, 1/83/4/0; rear 26/64/8/0, 65/25/7/1, 52/37/5/3, 0/94/0/2, 0/88/3/0; f34 28/62/8/0, 68/19/4/7,
  23/51/8/15, 3/75/6/7, 3/67/6/1.
- **Width profile** (silhouette width per tenth of height, fraction of W, top → bottom): front .09 .96 .95 .96 .93 .94 .93
  .85 .91 .94 (one tall post tip, then the full width from the left post top down); rear .83 .92 .93 .93 .93 .91 .87 .90
  .96 1.00; f34 .30 .86 .95 .94 .92 .92 .96 .98 .95 .46.
- **Verifier tolerance:** front W : H 1.40 ± 0.08 (whole silhouette, rod knob to stone base); left / right post height
  ratio 0.87 ± 0.04 (sheet 0.859); post-centre span / tall post 1.07 ± 0.08 (sheet 1.14 front, 1.06 rear); canvas ties at
  0.75 / 0.77 H ± 0.04; table length 0.60 H ± 0.05; front C 24 ± 8, W 53 ± 8, B 10 ± 4; rear W : H 1.40 ± 0.08, left / right
  post ratio 0.87 ± 0.05; side post-centre span / tall post 0.77 ± 0.06 (the side cell's back-post height is not scored,
  §3.4); f34 W : H 1.37 ± 0.10, C 26 ± 8, W 53 ± 8, R 6 ± 3, B 4–8 (one banner, §3.8), Y 0.8 ± 0.6, S 4.6 ± 2.5; fifths ±
  12. The canvas lowest point is deliberately higher than the front and rear cells draw it (§3.6): the front lowest-point
  fraction (sheet 0.49 H) is recorded, not scored.

### 1.3 Silhouette and composition per view

**Front (`z_front.png`) — governs X, post heights, canvas tie heights, the banner and lantern placement.** A level view:
- two thick square posts framing the shelter, the **right one 1.16 × taller**; each with a gold **X-lashing** near its
  top (left y 575–600, right y 552–565) and a **collar** at its foot, grey stone pieces flanking the feet;
- the **canvas** as a cream hammock: tied just under the left post's lashing (y 587) and below the right post's top (y
  573), its belly at y 627; the near edge drawn as a pale band with a darker underside (the canvas seen edge-on with
  thickness);
- at the right post: a short **wooden crossbar stub** on the inner side and a **grey iron rod** sticking out to the right
  (y 568.6), the **red banner** hanging from it, swallowtail at the bottom (three tongues), a **white diamond emblem**
  (outline diamond, small inner diamond, side dots); the **lantern** hanging just inside the right post from a ring;
- a second lantern hanging just inside the left post (not in the f34, §3.7);
- under the canopy: the **table** (x 86–191) with jars, bottle and pot on top, a **bench** in front at seat height, a
  **crate** with a small sprout at x 206–239, a small **bucket / keg** (x 192–205) beside it.

**Side (`z_side.png`).** Tall post at the left (front), a **much shorter post at the right** (back, 114 px), the canvas
sloping from 560 to 607 with a belly near the right end, the lantern hanging inside the left post. Under it a crate, the
table end with a bottle, the stool, a barrel. The short back post conflicts with the front, rear and both three-quarter
views (§3.4); it governs only the depth (post-centre spacing 131 px → 9.2).

**Rear (`z_rear.png`).** Two posts, the left (seen from behind: the tall right-hand side) a little taller; a lantern
hanging from a stub on the left post's outer side; a thin red strip (the banner edge-on) at the right post; the canvas
belly lowest of all cells (y 643.6); along the bottom a row of four crates and a large chest. Content differs from the
front three-quarter (§3.3, §3.11); it is scored on post heights and W : H only.

**Top (`z_rt.png`).** A near-square cream sheet (≈ 110 × 110 px) with an **X of creases** from the corners to the centre,
**crossed timber stubs and lashings at all four corners**, crates and stones round the edges. No ridge pole drawn
(§3.2). Content only: corners tied at the posts, crease pattern, dressing at the edges.

**f34 (`z_f34.png`, `z_f34_top.png`, `z_f34_bl.png`) — governs the overall read, the construction and the dressing.**
From the front-left, above:
- four posts: **F** nearest (front-left, our FL) with a red banner on its left side (§3.8), **L** at the left (back-left,
  BL), **R** at the right (front-right, FR) — the tallest, with the banner on an iron rod and the lantern, **B** the far
  post (back-right, BR);
- the **ridge pole** from B's top to R's top and past R by about 1.2, lashed at both posts below their square-cut tips
  (tips about 1.1–1.4 above the pole);
- the **canvas**: highest at B (tied right under the ridge junction lashing), tied lower on R below the ridge on a short
  stub (y 245), at L's and F's top lashings; the front edge sags to about 7.0; creases run to the centre; a small rope tab
  at the middle of the sheet;
- at R: a second lashing below the ridge with a wooden stub to the left and the grey iron banner rod to the right; a
  ring hanging from the stub with the lantern on it, inside the post line;
- the table in the middle with two glowing candle jars, a green bottle and a paper; a long bench behind it; a short bench
  in front; another bench / box at the back right; a dark cabinet-like box behind the table at the back left; a barrel
  beside L; a crate stack at R's foot; stone cubes in front; grass tufts at the feet.
- Iso check (parallel-projection rule, B base = L + R − F on screen): post heights L 213, F 218, R 263, B ≈ 233 px; canvas
  corners 180 / 195 / 190 / 200 px above their bases. The corners are near-level with B a little higher; R is clearly
  the tallest post.

**r34 (`z_r34.png`, `z_r34_top.png`).** Labelled rear, but it shows the same arrangement as the f34 from the same kind of
corner: ridge pole from the far post to the right post, the canvas apex at the far post, a banner at the left post, the
lantern on the ridge pole's protruding end at the right post (§3.3). Iso check: heights L 238, F 222, R 260, B ≈ 241 px;
canvas corners 205–218 px above base. It confirms: one high corner at the ridge, one clearly tallest post, chunky
lashings with dangling tails, collars at the feet.

**Close-up 1, ridge pole junction (`z_cu.png`).** A square post with small chamfers and a flat square-cut top; a fat
gold X-lashing: two horizontal turns, a diagonal cross over the beam, rope about a quarter of the post width; a square
beam end (≈ 0.7 post width) sticking out to the right; canvas sweeping into the lashing from both sides.

**Close-up 2, post base & peg (`z_cu.png`).** The post (77 px) on a grey faceted block 110 px wide and ≈ 76 px tall (1.43 ×
the post width, about as tall as the post is wide), a gold rope collar of two turns right on the block's top, a square
peg (≈ 0.45 of the post width) leaning at ≈ 45° against the block's front-right, wrapped with rope; a grass tuft.

**Close-up 3, canopy underside (`z_cu.png`).** From below: broad canvas planes meeting at clean folds, the ridge pole
overhead with a lashing, a darker strip along a fold (the canvas edge seen in thickness). The canvas reads tan here
(`#DDB88D`): that is shade, not paint (§3.16).

**VFX panel (`z_vfx.png`).** The lantern alone: **six-sided**, a flared base, glass panels between corner bars, a band, a
domed roof with a cap and a **ring with a short hook** on top; warm dark metal; bright amber glass with a soft radial
glow round it.

### 1.4 Parts (exploded `z_expl.png`, `z_ex_bl.png`, `z_peg.png`)

The exploded cell draws the pieces in loose perspective near hero scale; the hero governs size and position, the cells
govern shape and colour (§3.11).

| Part (label) | Exploded box (px) | Tone (median, lit, shade) | Shape |
| --- | --- | --- | --- |
| Ridge Pole | (300,797,440,874) | `#873A0F`, lit `#DE741E`, shade `#5B230A` | a **square timber with small chamfers**, ends cut square, a rope band near each end, one end over a post top with the canvas apex |
| Canvas Canopy | (193,834,460,987) | `#FEF0C6`, shade `#FDE8C0` | a four-cornered sheet seen as a diamond, the **top corner high** at the ridge pole, an X of creases to a centre tab, small dark tie points at the corners |
| Wood Post (x4) | (160,910,188,1167), (468,887,494,1104) | `#A2480B` / `#923F0C`, lit `#D4630C` | tall **square chamfered posts**, flat tops, an X-lashing near the top, a rope band low down |
| Banner & Rod (x1) | (540,920,600,1077) | red `#B10C0F`, white `#F3F3EF`; rod `#40302B` | a **red banner, swallowtail with three tongues**, a white diamond emblem, hung from a dark rod with **knob ends** |
| Lanterns (three, unlabelled) | (120,994,150,1047), (226,970,253,1053), (503,960,533,1014) | glass `#FAB705`, metal dark | hexagonal lanterns on rings, two hanging from the canvas corners by dashed lines, one in the middle |
| Long table | (226,1020,400,1130) | `#C4662C` top, lit `#D87835`, shade `#5F2C13` | **four lengthwise planks** on square legs with a low stretcher; a small grey block under one leg |
| Long bench | (310,1077,490,1167) | `#A85A26`, lit `#DC7A36` | two-plank seat on four legs with stretchers |
| Short bench | (380,1127,490,1227) | `#A95A26` | the same design, shorter |
| Stool | (450,1183,493,1227) | as the benches | a two-plank square seat on four legs |
| Barrel | (112,1110,170,1194) | staves `#7B3B1B`, lit `#B95E28`; hoops `#878285`, lit `#BEB8B1`; top `#D3CAC1` | about 10 staves, slight bulge, **two blue-grey hoops** (near the top and bottom), an open top showing a pale grey surface |
| Crates (two) | (176,1147,253,1234), (513,1087,603,1177) | `#7D3E20` / `#743A1F`, lit `#CD7433`; plates `#433938`; straw `#F7D69A` | **open-topped** boxes: corner posts, top and bottom rails, **X braces** on the faces, dark corner plates, **heaped straw** inside |
| Stones (two cubes) | (256,1154,293,1188), (280,1187,323,1234) | `#AA9794`, lit `#DCCBC7`, shade `#6C5F66` | pale faceted near-cubes, one larger |
| Peg (x4) | (163,1195,190,1250) | `#813C15`, tip `#E0CCAD` | a short stake with a collar and a **pale pointed tip** (it reads like a candle; close-up 2's square peg governs, §3.10) |

- **Post:** 1.00 × 1.00 square, 0.08 chamfers on the four long edges (8-sided), top cut flat with a 0.05 chamfer rim,
  bottom flat on the stone base; a ±0.02 twist / taper along the length is allowed so it reads hand-hewn.
- **Stone base:** 1.60 × 1.60 × 1.20 faceted block (12–16 verts), flat bottom, **flat top under the post**, broken upper
  edges round the outside (WorldModeling §12.1); never a smooth box.
- **Ridge pole:** 0.80 × 0.80, 0.06 chamfers, 11.8 long, ends cut square.
- **Crossbar (stub):** 0.50 × 0.50 × 2.60 timber, 0.04 chamfers, ends cut square.
- **Canvas:** one closed slab **0.10 thick** (outer face, inner face, rim band), never a single-sided plane; a corner
  tab at each corner that wraps its post or the ridge pole.
- **Banner:** 2.00 W × 5.90 H × 0.08 slab, three swallowtail tongues (notches 0.9 deep), a top hem wrapping the rod;
  the emblem a white diamond outline (1.10 × 1.60, stroke 0.15), a small inner diamond (0.35 × 0.50) and two dots (Ø 0.18)
  either side, each a 0.015-proud inset on **both** faces.
- **Banner rod:** iron, 8-sided Ø 0.18, 3.1 long, a knob (Ø 0.30, 6-sided) on the outer end.
- **Lantern:** 6-sided. Base plate Ø 1.20 × 0.15 (flared), six corner bars Ø 0.10, glass core Ø 1.00 × 1.20 (emissive),
  a band Ø 1.15 × 0.12, a domed roof (two rings: Ø 1.15 → 0.70 → 0.30 over 0.45), a cap Ø 0.30 × 0.12, a ring (r 0.18,
  tube 0.06) on top. Body 2.04 tall, 2.40 with the ring.
- **Table:** 7.20 × 2.80 × 2.60: four planks 0.70 wide × 0.25 thick lengthwise with 0.02 gaps, two cleats under the top,
  four square legs 0.45, one stretcher along X at z 0.5 and one across each end.
- **Bench:** 6.00 × 1.20 × 1.50 (long) / 3.60 × 1.20 × 1.50 (short): two planks 0.60 × 0.22, four legs 0.35, one
  stretcher along X.
- **Stool:** 1.20 × 1.20 × 1.50: two planks, four legs 0.30.
- **Barrel:** 2.80 tall, Ø 2.00 at the ends, 2.20 at the bulge; 10 staves (rings of 10 verts at z 0, 1.40, 2.80 with the
  middle ring at r 1.10); two iron hoops 0.22 tall, 0.05 proud at z 0.35 and 2.30; an open top with the contents disc
  inset 0.15 below the rim.
- **Crate:** 2.30 × 2.30 × 2.10 open box: corner posts 0.26, top and bottom rails 0.26, an X brace (0.20 × 0.08 planks) on
  each face, dark corner plates (0.36 L-plates, 0.04 thick) at the eight corners; a **straw mound** (8–10-vert low dome,
  0.45 high above the rim) sitting on an inner floor 0.25 below the rim.
- **Peg:** square 0.40 × 0.40 × 1.60 stake, a pale cut top (end grain), a rope band 0.25 below the top.
- **Stones:** hull blocks 1.00 × 0.90 × 0.80 and 0.80 × 0.75 × 0.65, 10–14 verts, flat bottoms, broken top corners.
- **Table items:** two candle jars (6-sided Ø 0.45 × 0.60, emissive, a dark lid disc Ø 0.40 × 0.08), a green bottle
  (6-sided body Ø 0.40 × 0.70, neck Ø 0.16 × 0.30, a cork), a paper (1.40 × 1.00 × 0.04 slab), a pot (6-sided Ø 0.60 ×
  0.50, dark metal).

### 1.5 How 066 differs from the old kit and its siblings (binding: the verifier checks these)

| | W10 `CampAwning` (old kit, exported) | M064 `CanvasTent` | **066 Canvas Shelter** |
| --- | --- | --- | --- |
| Size | 10.9 W × 8.2 H × 10.1 D; posts 9.1 | tent 13.7 × 11.7 × 11.0 | **posts 12.0 / 10.4 on stone bases, spacing 12.8 × 9.2; hero ≈ 17.3 × 12.3 × 12.0; walk under, sit at the table** |
| Frame | thin round posts, a ridge log | two X frames of 0.75 chamfered poles | **four 1.0 chamfered square posts on 1.6 stone bases, a 0.8 square ridge pole on the tall side, crossbars at the corners, pegs at every base** |
| Canvas | "flat sheet", yellow `#E3CFA0` | 0.10 slabs, creases, doorway | **one 0.10 slab, deep sag (centre 2.4 below the corner mean), X creases to the centre, one high corner folded over the ridge pole, corner tabs wrapping the posts** |
| Rope | rings at the ties | lashings, knots, hem ties | **five fat X-lashings, four foot collars, four peg ropes, dangling tails; twisted, gold** |
| Glow | one heat_glow | two lanterns, Neon + heat_glow | **one hexagonal lantern (Neon glass + `heat_glow` halo + light) and two Neon candle jars** |
| Dressing | table set, crates, barrel, stones | crate, barrels, stones, mat | **table with items, long and short bench, stool, two open straw crates, barrel, two stones, banner** |
| Colour | one key per material | wood family by role | **saturated orange-brown posts, lighter plank furniture, darker crates and barrel, pale cream canvas with a deeper hem, gold rope, pale warm stone, red banner with an off-white emblem, warm dark lantern metal, cool grey hoops and rod** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0). Plan azimuths: 0° = +X, counter-clockwise. Kit camera azimuths:
`front` az 0 (camera on −Y), `side` az 90 (camera on +X, screen right = +Y), `rear` az 180, f34 about az −45, r34 az 135.
Post names: **FL** (−6.4, −4.6), **FR** (+6.4, −4.6), **BL** (−6.4, +4.6), **BR** (+6.4, +4.6).

### 2.1 Stack (binding contact chain; every seat ≤ 0.03 unless stated)

| Piece | Rests on / hangs from | Contact |
| --- | --- | --- |
| Stone bases (4) | the ground | flat bottom on z 0.000 (±0.005) |
| Posts (4) | their stone bases | bottom face on the base's flat top z 1.20 (±0.005), centred |
| Ridge pole | the inner (−X) faces of FR and BR | side face against both posts (gap 0.00–0.02); bound by two lashings |
| Crossbars (3: FL, BL, FR) | the post's outer Y face (FL / FR front face, BL back face) | side face against the post (gap 0.00–0.02); bound by the corner lashing |
| Corner lashings (5) | post + crossbar (FL, BL, FR lower), post + ridge (FR upper, BR) | turns hug the timber (inner surface 0.00–0.02 off the faces); sink ≤ 0.03 |
| Canvas | the four corner lashings and the ridge pole | each corner tab wraps its post's inner edge (or the ridge pole at BR) under the lashing, touching the timber (≤ 0.02) with the lashing turns over it (≤ 0.03 into the slab) |
| Banner rod | the FR crossbar's underside | top line touching the crossbar bottom (≤ 0.02); a rope band round both |
| Banner | the rod | top hem wraps the rod (inner surface ≤ 0.02 off it) |
| Lantern | the FR crossbar's inner end | ring hooked round the crossbar (ring and timber touching, ≤ 0.02) |
| Collars (4) | post foot | two turns on the base top, hugging the post |
| Pegs (4) | the ground and the base | stake foot on z 0, upper side touching the base's outer face (≤ 0.02) |
| Peg ropes (4) | peg band and collar | ends sunk 0.03 into the peg band and the collar |
| Table, benches, stool, barrel, crates, stones | the ground | bottoms on z 0; each ≥ 0.05 from every other piece unless it touches |
| Table items (5) | the table top (z 2.60) | bottoms on the top (gap ≤ 0.02) |
| Straw mounds | each crate's inner floor | sitting on it, rim clear of the walls by ≥ 0.03 or touching |

### 2.2 Posts and stone bases

| Post | Centre (x, y) | Base | Post z | Notes |
| --- | --- | --- | --- | --- |
| FL | (−6.4, −4.6) | 1.60 × 1.60 × 1.20 | 1.20 … **10.40** | crossbar on the front face, lashing L1 |
| BL | (−6.4, +4.6) | same | 1.20 … **10.40** | crossbar on the back face, lashing L2 |
| FR | (+6.4, −4.6) | same | 1.20 … **12.00** | crossbar + banner rod (L3), ridge (L4); lantern; banner |
| BR | (+6.4, +4.6) | same | 1.20 … **12.00** | ridge (L5); canvas apex |

- Post faces: FL / BL inner face x −5.90, FR / BR inner face x +5.90; front posts' inner (back) face y −4.10, back posts'
  inner face y +4.10.
- Bases are slightly irregular per post (seeded), rotated 0–6°, but every top stays flat and level under its post.

### 2.3 Ridge pole and crossbars

- **Ridge pole:** 0.80 square, axis along Y at **x +5.50**, z **10.20 … 11.00**, **y −5.90 … +5.90** (0.80 past the posts'
  outer faces at ±5.10, as the f34's stub past R). Its outer face lies on the tall posts' inner faces (x 5.90). Post tips
  stand 1.00 above it.
- **Crossbars** (0.50 square × 2.60, along X, against the post's outer Y face):
  - FL: centre (−5.90, −5.35), z 8.40 … 8.90, x −7.20 … −4.60.
  - BL: centre (−5.90, +5.35), z 8.40 … 8.90.
  - FR: centre (+5.90, −5.35), z **9.35 … 9.85**, x +4.60 … +7.20 (inner end 1.30 inside the post line, outer end 0.30 out).
  - BR has none (the ridge pole does its job; the top cell's crossed stubs are content only).
- The crossbars sit outside the canvas (canvas y ±3.95) and below the canvas corners, so no crossbar passes through the
  canvas.

### 2.4 Canvas (one closed shell)

- **Corner anchors** (canvas mid-surface at the corner):
  - FL_c (−5.75, −3.95, **9.00**), BL_c (−5.75, +3.95, **9.00**), FR_c (+5.75, −3.95, **9.20**): each just inside its
    post's inner corner edge, the tab wrapping that edge under the lashing;
  - BR_c (+5.30, +3.95, **10.60**): the **apex**, the tab folded up over the ridge pole's top (to z 11.10) and down its
    inner face, captured by L5 (close-up 1: "loops over the ridge pole").
- **Grid:** 7 (along X) × 5 (along Y) vertices, bilinear in plan between the anchors (u along X 0 → 1, v along Y 0 → 1).
- **Sag:** z(u, v) = bilinear(corner z) − **1.20 · [4u(1−u) + 4v(1−v)]** (edges sag 1.2 at their middles, the centre 2.4).
  Expected: centre **≈ 7.05**; front edge middle 7.90, back 8.60, left 7.80, right 8.70. Keep **every canvas point ≥ 6.9**.
- **Creases:** triangulate each quad along the diagonal that points toward the grid centre, so flat shading draws the
  sheet's X of creases from each corner to the middle (top cell, f34, exploded). No subdivision, no cloth sim.
- **Thickness:** 0.10 offset downward along the vertex normals; rims are real faces; the corner tabs are part of the
  same closed shell (or touching closed slabs, ≤ 0.02).
- **Centre tab:** the f34 and the exploded show a small knot at the middle of the sheet: a 0.30 rope nub on the top face
  at the centre (optional, 12–16 tris).

### 2.5 Banner and rod (FR)

- **Rod:** along X at y −5.35, axis z **9.26** (its top touches the FR crossbar's bottom z 9.35), x **+6.20 … +9.30**, knob
  at x 9.30; a rope band (Ø 0.12, 2 turns) round rod and crossbar at x 6.80.
- **Banner:** plane y −5.35 facing −Y (front), x **+7.10 … +9.10**, top hem at z 9.20 wrapping the rod, bottom tongue
  tips at z **3.30**. It clears the post's outer face (x 6.90) by 0.20.

### 2.6 Lantern (one)

- Hangs from the FR crossbar's inner end: ring hooked round it at (4.85, −5.35), ring top touching the crossbar's bottom
  (z 9.35); body axis (4.85, −5.35), **body z 6.95 … 8.99**, ring to 9.35.
- It hangs **in front of the canopy's front edge** (canvas edge y −3.95), left of FR as the front cell draws it, clear
  of the post (post x ≥ 5.90; lantern radius 0.60 → x ≤ 5.45) and of the canvas (≥ 1.0).
- Glass centre (VFX socket): (4.85, −5.35, 7.85).

### 2.7 Rope

| Piece | Count | Where | Size | Sides × segments |
| --- | --- | --- | --- | --- |
| Corner X-lashing | 5 | L1 FL z 8.20–9.40, L2 BL z 8.20–9.40 (post + crossbar + canvas tab); L3 FR z 9.00–10.05 (post + crossbar + rod end + canvas tab); L4 FR z 10.05–11.15 (post + ridge); L5 BR z 10.05–11.25 (post + ridge + canvas apex tab) | Ø 0.24 | 4–5 × 10 per turn; 2 horizontal turns + 2 diagonal turns |
| Dangling tail | 2 | from L1 and L2, hanging 0.8–1.0 down the outside of the post (f34 L, r34) | Ø 0.20 | 4 × 4 |
| Foot collar | 4 | each post, z 1.22–1.66, two turns on the base top | Ø 0.22 | 4 × 8 per turn |
| Peg rope | 4 | from each peg band up to its collar | Ø 0.16, 1.0–1.4 long | 4 × 4 |
| Peg band | 4 | round each peg, 0.25 below its top | Ø 0.12 | 4 × 6 |
| Rod band | 1 | rod + FR crossbar at x 6.80 | Ø 0.12 | 4 × 6 |

- All rope is **twisted** (each ring rotated half a side per segment, M051's twist), chunky, never flat collars or thin
  wire. Lashings wrap **both** timbers they bind (close-up 1's diagonal cross over the beam end).

### 2.8 Pegs

- One per post, on the base's **outer X face** (−X for FL / BL, +X for FR / BR), at the post's y: foot at (±7.75, ±4.60,
  0), leaning toward the base 35° from vertical so its upper side touches the base's outer face (x ±7.20) at about z 0.9;
  its pale top faces up and out; its band's rope runs up to the collar (close-up 2).

### 2.9 Furniture, dressing and table items (f34 + exploded; §3.11)

| Piece | Centre (x, y) | Size (X × Y × Z) | Rot (z) | Notes |
| --- | --- | --- | --- | --- |
| Table | (−0.80, +0.40) | 7.20 × 2.80 × 2.60 | 0° | x −4.40 … +2.80, y −1.00 … +1.80 |
| Long bench | (−0.80, +2.70) | 6.00 × 1.20 × 1.50 | 0° | behind the table, 0.30 gap |
| Short bench | (+0.20, −1.90) | 3.60 × 1.20 × 1.50 | 0° | in front of the table, 0.30 gap |
| Stool | (+3.90, +0.40) | 1.20 × 1.20 × 1.50 | 8° | at the table's right end |
| Barrel | (−6.00, +2.00) | Ø 2.00 / 2.20 × 2.80 | 0° | straddling the left post line, as in the f34 beside L |
| Crate A | (+4.50, −2.50) | 2.30 × 2.30 × 2.10 | 0° | inside the front-right corner (front cell crate at x +5.0) |
| Crate B | (+4.40, +2.60) | 2.30 × 2.30 × 2.10 | 0° | inside the back-right corner |
| Stone S1 | (−4.60, −5.90) | 1.00 × 0.90 × 0.80 | 20° | outside the front edge, left (f34 stone by F) |
| Stone S2 | (+2.40, −5.50) | 0.80 × 0.75 × 0.65 | 35° | outside the front edge, right |
| Candle jars J1 / J2 | (+0.30, +0.70) / (+0.90, +0.50) | Ø 0.45 × 0.60 | — | on the table |
| Bottle | (−2.40, +0.90) | Ø 0.40 × 1.00 | — | on the table |
| Paper | (−0.90, +0.20) | 1.40 × 1.00 × 0.04 | 10° | on the table |
| Pot | (−3.60, +0.80) | Ø 0.60 × 0.50 | — | on the table |

- **Clearances:** every piece ≥ 0.05 from the stone bases, pegs and each other unless it touches; crate A and crate B
  each clear their corner's base by ≥ 0.05; nothing intersects anything.
- **Seat points** (stored, for Studio `Seat` parts): `m066_seat_back` (−0.80, +2.70, 1.50), `m066_seat_front` (+0.20,
  −1.90, 1.50), `m066_seat_stool` (+3.90, +0.40, 1.50).

### 2.10 Walkability (binding)

- A 5.5-stud character proxy (2 × 1 × 5.5 box) **walks in from the front** (from y −8, anywhere in x −5.6 … +3.3) to the
  short bench's front, and **from the back** (from y +8, x −4.9 … +3.2) to the long bench's back, touching nothing.
- **Head clearance:** the canvas underside ≥ 6.9 over every floor point inside the posts; the lantern hangs outside the
  canopy line, its bottom 6.95.
- The shelter is open on all four sides; the barrel, crates, pegs and stone bases are deliberate obstacles round the
  edges.

### 2.11 Expected extents

- **Posts and canvas:** X −7.20 … +7.20 (bases), Y −5.40 … +5.40, Z 0 … 12.0.
- **Hero:** X ≈ −7.95 (FL / BL pegs) … +9.36 (rod knob), Y ≈ −6.40 (stone S1) … +5.90 (ridge pole), Z 0 … 12.0 → **about
  17.3 × 12.3 × 12.0**; bbox bottom centre ≈ (+0.70, −0.25, 0) in the build frame.

### 2.12 Origin, pivot and stored points

- Origin at the **bbox bottom centre** (`K.check`); transforms applied. Store `o["m066_offset"]` = build-frame origin →
  object origin, `o["m066_centre"]` = the floor centre under the canopy (build (0, 0, 0)), the three seat points (§2.9)
  and `o["m066_lantern"]` = the glass centre; re-check all after the origin move.
- Parts: origin at their own bbox bottom centre; the Lantern part also stores `m066_hang` (its ring's top point), the
  Banner part `m066_hang` (the rod's inner end), the Post part `m066_top` (its top centre).

### 2.13 Screen checks (floor hidden; `measure.py` masks; probe and keep the best)

- **front_sheet (0, 3)** — governs X and heights: W : H 1.40 ± 0.08; left / right post 0.87 ± 0.04; post-centre span / tall
  post 1.07 ± 0.08; canvas ties at 0.75 / 0.77 H ± 0.04; banner 2.0 wide, bottom at 0.28 H ± 0.04; lantern left of FR,
  its glass at 0.65 H ± 0.04; table length 0.60 H ± 0.05, top at 0.22 H ± 0.02; crate A right of the table.
- **rear_sheet (180, 0)** — W : H 1.40 ± 0.08; left (FR / BR) taller than right (FL / BL), ratio 0.87 ± 0.05.
- **side_sheet (90, 0)** — governs Y: post-centre span / tall post 0.77 ± 0.06; the ridge pole along the top with 0.8
  stubs past both posts; the canvas rising to the BR apex. The sheet's short back post is not scored (§3.4).
- **f34_sheet (−45, 20)** (probe az −30 … −50 × e 15 / 20 / 25; the sheet's camera looks more at the front, so the front
  edge reads about twice the length of the left edge) — governs the overall read and dressing: W : H 1.37 ± 0.10; C 26 ±
  8, W 53 ± 8, R 6 ± 3, B 4–8, Y 0.8 ± 0.6, S 4.6 ± 2.5; the ridge pole from the far post to the right post; the canvas apex
  at the far post; the banner and lantern at the right post; table, benches, barrel, crates and stones where §2.9 puts
  them.
- **r34_sheet (135, 20)**: content only (§3.3): the back of the banner, the ridge side, the long bench, crate B, collars
  and pegs.
- **top (0, 89.9)**: content only: an X of creases to the centre, lashings at all four corners, the ridge pole along the
  right side, dressing at the edges.

## 3. View conflicts and resolutions

### 3.1 Sheet number
- **Evidence.** The header says "PAGE 65/132"; INDEX.md row 66 lists `066.png` as "Canvas Shelter Model Study".
- **Resolution.** Our number is 066 (file name, keys `m066_*`). Note the header in the export notes only.

### 3.2 The ridge pole is missing from the orthos and the top
- **Evidence.** The f34, r34, exploded (labelled "Ridge Pole") and close-ups 1 and 3 all show a square ridge pole lashed
  between two posts with the canvas looped over it at one end. The front, side, rear and top cells draw none: the top
  shows only crossed stubs at the corners.
- **Resolution (decision §8.4).** Build the ridge pole (it is a labelled part, two close-ups and the hero view). It runs
  along the tall right side, FR → BR, on the posts' inner faces. In the front and rear views it shows end-on at the tall
  post's top (the front cell's stubs at y 552–568 are read as that end and the FR crossbar).

### 3.3 "Rear three-quarter view" is another front three-quarter
- **Evidence.** It shows the ridge pole from the far post to the right post and the canvas apex at the far post, exactly
  the f34's arrangement; a real rear three-quarter would put the ridge pole on a near edge. Its props (banner left, lantern
  on the ridge stub, crates) are shuffled versions of the f34's.
- **Resolution.** Content only (lashings, collars, tails, the open sides). The f34 governs the construction and dressing.

### 3.4 Side view: a short back post
- **Evidence.** The side cell's back post is 114 px (8.0) against 172 px (12.0) at the front. The front and rear cells
  agree with each other (left column 146.5 / 148 px, right column 170.5 / 163 px: the right-hand pair tall, the left pair
  short), and the f34 and r34 both have the ridge pole carried level by two tall posts.
- **Resolution.** The right-hand pair (FR, BR) is 12.0 and carries the ridge pole level; the left pair (FL, BL) is 10.4.
  The side cell governs only the depth (post spacing 131 px → 9.2). Alternative: a sloping ridge pole with BR at 10.4
  (matches the side cell, breaks the f34's level ridge and needs an angled lashing).

### 3.5 Footprint: square top vs wide front
- **Evidence.** The top cell is a near-square sheet (≈ 110 × 110 px). The front and rear cells space the posts 194 / 173
  px against the side cell's 131 px (1.4 : 1), and the f34 / r34 draw the front edge about twice as long as the side edge.
- **Resolution.** Rectangle **12.8 (X) × 9.2 (Y)** post centres (front / rear mean and side cell at one scale). The top is
  content only, as 064's stylised top was.

### 3.6 Canvas sag: belly at head height in the front and rear cells
- **Evidence.** At 0.070 stud / px the front cell's canvas belly is at 5.9 and the rear cell's at 4.9; the f34's front edge
  middle is at about 7.0 and its belly clearly above the table and benches.
- **Resolution (decision §8.5).** Corners 9.0 / 9.0 / 9.2 / 10.6 with edge sag 1.2 and centre sag 2.4 → lowest point
  ≈ 7.05, so characters walk under (the old kit's goal was ≥ 7). The sag stays the dominant read (2.4 below the corner
  mean over a 7.9 short span); the front lowest-point fraction is recorded, not scored. Alternative: sag 1.6 (lowest
  6.25): closer to the front cell, but tall avatars clip the belly.

### 3.7 Lanterns: one, two or three, and how low
- **Evidence.** The f34, r34, side and rear cells each draw **one** lantern at a tall post; the front cell draws two (one
  inside each front post); the exploded draws three. The title says "hanging lantern" (singular); the VFX panel shows
  one. The drawn lanterns hang with their bottoms at 4.6–5.5 (head height).
- **Resolution (decision §8.8).** **One** lantern at FR, hung from the FR crossbar's inner end, in front of the canopy
  edge, body 6.95 … 8.99 (clear of every head). Alternative (open question): a second lantern at FL from the FL
  crossbar's inner end (front cell, exploded; +≈ 180 tris, one more socket).

### 3.8 Banners: one or two, and which way it faces
- **Evidence.** The parts list says "Banner & Rod (x1)"; the front, side, rear and r34 have one. The f34 has two: one on
  the rod at R, one hanging on F's left side. The front cell shows the rod's banner face-on; the rear cell draws a thin red
  strip (edge-on) at a post.
- **Resolution (decision §8.9).** **One** banner on the iron rod under the FR crossbar, its face toward the front (−Y),
  seen face-on in the front cell and the f34. The f34 B share is then expected at 4–8 instead of 7.7. Alternative (open
  question): a second banner hung from the FL crossbar's outer end, facing −X (the f34's F banner; +≈ 120 tris).

### 3.9 Post feet: stone bases vs posts in the grass
- **Evidence.** Close-up 2 and the model notes put every post on a stone base. The f34 and the orthos show the feet in
  grass tufts with grey stone pieces beside and behind them and a collar about 1.5 up.
- **Resolution.** A 1.6 × 1.6 × 1.2 faceted stone base under every post, the collar on its top (1.2–1.66: the orthos'
  collar height), no grass (§3.14). The grey pieces the orthos show beside the feet are the bases.

### 3.10 Pegs: braces at the bases or guy ropes for the canvas
- **Evidence.** The model notes say the posts are braced with ground pegs; close-up 2's caption says the canvas is
  tensioned to the ground with a peg, but its drawing ties the peg to the post's collar at the base. No assembled view
  draws a guy rope from a canvas corner to the ground. The exploded draws "Peg (x4)" as a short round stake with a pale
  tip that reads like a candle.
- **Resolution.** One square peg per post, leaning on the base's outer face, roped to the collar (close-up 2's drawing);
  a pale end-grain top (the exploded's pale tip). Alternative: guy ropes from the corner lashings to the pegs (invented in
  every assembled view; not recommended).

### 3.11 Furniture and dressing differ in every view
- **Evidence.** The f34: table, long bench behind, short bench in front, another bench / box at the back right, a dark
  cabinet behind the table at the back left, a barrel by L, crates at R's foot, stone cubes, table items. The exploded:
  table, long bench, short bench, stool, barrel, two open crates, two stone cubes. The front: table, bench, crate,
  bucket. The rear: four crates and a chest. The side: crate, table end, stool, barrel.
- **Resolution (decision §8.10).** The exploded's set (table, long bench, short bench, stool, barrel, two open crates,
  two stones) plus the f34's table items (two glowing jars, bottle, paper, pot), placed as the f34 and the front cell
  suggest (§2.9). No cabinet, chest or extra crates.

### 3.12 Rope: pale swatch vs gold render
- **Evidence.** The "Rope (Detail)" swatch is a pale beige `#D9C2A4` (34°, 0.24, 0.85); every rendered rope is gold:
  f34 `#DFA448`, front `#DC9E42`, close-up 1 `#DB9738`, close-up 2 `#E49738`, exploded `#E5A152` (32–37°, 0.64–0.75).
- **Resolution.** The rendered rope governs (the user's rule is to match the master reference's look); calibrate to
  `#DDA048`. Keep it a warm gold, not lemon or orange, with a deeper strand (§5.4). Alternative: the swatch's pale beige
  (it would read as M064's beige rope, unlike this sheet).

### 3.13 Two metals
- **Evidence.** No metal swatch. The lantern frame is a warm dark brown iron (`#5C4738`, shade `#413127`); the barrel
  hoops and the banner rod's lit parts are a cool grey (`#878285`, lit `#BEB8B1`); the crate corner plates are near-black
  warm (`#433938`).
- **Resolution.** Two keys: `m066_metal` (lantern, crate plates, pot, jar lids, rod knob) and `m066_iron` (barrel hoops,
  banner rod).

### 3.14 Grass tufts
- **Evidence.** Green tufts at most post feet and some props (G ≈ 0.6–1.1 %); no green swatch.
- **Resolution.** Left out: ground dressing belongs to the terrain and foliage models (as 064). Record it.

### 3.15 "Canvas is a single sheet" vs Roblox
- **Resolution.** One sheet in shape, but a closed 0.10 slab: Roblox culls back faces, so a single-sided plane vanishes
  from below, which is where players see it (close-up 3 itself says the canvas has low-poly thickness).

### 3.16 "Solid colours, no texture noise" vs the user's colour rule; the shaded underside
- **Resolution.** Keys by role, blended by position (§5.5); broad Tint mottling per piece; never per-triangle confetti.
  The canvas underside's tan (`#DDB88D` in close-up 3), the dark post sides and the lavender stone shade are the sheet's
  light, not paint.

### 3.17 Ridge-pole end bands vs junction lashings
- **Evidence.** The exploded ridge pole has a rope band near each end; the assembled views show those as the junction
  lashings at FR and BR.
- **Resolution.** The bands are the lashings L4 and L5 (in the hero). The `CanvasShelterRidgePole` part carries two rope
  bands where the lashings sit, so it reads like its cell on its own.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

1. `post(height)` → one chamfered square prism, flat cut top with a chamfer rim, flat bottom. Check against close-ups 1
   and 2.
2. `stone_base(seed)` → the faceted base with a flat top (§1.4). Check against close-up 2.
3. `ridge()` → the 0.80 square ridge pole; `crossbar()` → the 0.50 stub.
4. `canvas(corners)` → the 7 × 5 grid with the sag formula, centre-pointing diagonals, 0.10 offset, corner tabs (the BR
   tab over the ridge). Check against the exploded canopy and the top cell's creases.
5. `rope_tube(path, r, sides, twist)` → every rope piece (lashing turns, collars, tails, peg ropes, bands). Copy M051's
   twisted tube (committed: import its geometry helpers, never its constants). `x_lashing(timbers, z0, z1)` builds two
   horizontal turns and two diagonal turns round the listed timbers.
6. `lantern()` → the hexagonal lantern (§1.4); glass on the glow key. Check against the VFX panel.
7. `banner()` → slab with tongues, hem, emblem insets both faces; `rod()` with its knob.
8. `table()`, `bench(length)`, `stool()`, `barrel()`, `crate()` (with straw), `stone(size, seed)`, `peg()`, `items()`.
9. **Hero `CanvasShelter`** = 4 bases + 4 posts + ridge + 3 crossbars + canvas + 5 lashings + 2 tails + 4 collars + 4 pegs
   + 4 peg ropes + rod + rod band + banner + lantern + table + 2 benches + stool + barrel + 2 crates + 2 stones + 5 table
   items, placed by §2, one object of closed shells. Then run the contact, bury, walk and winding reports (§6).
10. **Parts shot** (−20, 15) laid out like the exploded: Post, RidgePole, Canopy, Banner, Lantern, Table, Bench, Stool,
    Crate, Barrel, Peg, gaps 0.8.
11. **Exploded shot:** the ridge pole lifted above the canopy, the canopy above the furniture, two posts either side, the
    lantern and banner to the right, crates, barrel, stones and a peg below.

Reusable code: M051 / M052 rope and timber helpers (committed: import, don't edit); `m047._Solids`, `shells_report`,
`contact_report`, `bury_report`, m038's `contacts()` (committed). Copy, don't import, from uncommitted builders (M064's
canvas and lantern code, if present, may be copied).

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** four thick posts on stone bases, the tall right pair carrying a ridge pole, a deep cream canvas
   hammock with X creases and one high corner, fat gold lashings, the red banner and glowing lantern at the front-right,
   table and benches underneath, crates, barrel and stones round the base.
2. **front_sheet / rear_sheet / side_sheet / f34_sheet / r34_sheet / top** per §2.13.
3. **Close-up renders:**
   - `junction_cu` on the BR junction from the front-left, against close-up 1: square-cut post top, the X-lashing over
     post and ridge, the canvas tab folded over the ridge.
   - `base_cu` on the FR base from the front-right, against close-up 2: faceted stone, collar on its top, the peg leaning
     on it with its rope to the collar.
   - `underside_cu` from (0, −1.5, 1.6) looking up at (0, +1, 8), against close-up 3: broad canvas planes, a visible 0.10
     rim, the ridge pole overhead; no see-through canvas from below.
   - `lantern_cu` against the VFX panel: six sides, flared base, bars, dome, ring on the crossbar.
   - `walk`: the 5.5 proxy at the short bench, on the back lane and under the canvas centre, front and side views; minimum
     clearances printed.
   - `thumb`: the f34 at about 140 px tall: posts, canopy belly, banner, lantern glow still read.
   - `spin` contact sheet: az 0 / 45 / … / 315 at e 10: the canvas reads solid from every side and from below, nothing
     floats.
4. **Contact counts** (§6): floating shells 0; buried 0 (stated seats excepted); winding errors 0.
5. **Scale shot:** the 5.5 marker standing under the canvas centre and one seated height marker at the long bench.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Posts (8-sided prism, chamfer-rim top) | 4 | 36–44 | 145–175 |
| Stone bases (faceted, flat top) | 4 | 20–28 | 80–112 |
| Ridge pole (8-sided) | 1 | 36 | 36 |
| Crossbars (8-sided) | 3 | 28 | 84 |
| Canvas shell (7 × 5 grid, both faces, rims, 4 tabs) | 1 | 190–230 | 190–230 |
| Corner X-lashings (4 turns, 4–5 × 10) | 5 | 120–150 | 600–750 |
| Collars / peg ropes / peg bands / tails / rod band | 4 / 4 / 4 / 2 / 1 | 48 / 24 / 32 / 16 / 32 | 448 |
| Pegs | 4 | 20 | 80 |
| Lantern (6-sided) | 1 | 160–190 | 160–190 |
| Banner (tongues, hem) + emblem insets ×2 + rod + knob | 1 | 60 + 64 + 32 + 20 | 176 |
| Table (planks, cleats, legs, stretchers) | 1 | 130–150 | 130–150 |
| Long bench / short bench / stool | 1 / 1 / 1 | 96 / 84 / 60 | 240 |
| Barrel (10 staves, 3 rings, 2 hoops, top disc) | 1 | 200–230 | 200–230 |
| Crates (frame, X braces, plates, floor, straw mound) | 2 | 250–290 | 500–580 |
| Stones (hull, 10–14 verts) | 2 | 16–24 | 32–48 |
| Table items (2 jars, bottle, paper, pot) | 5 | 12–40 | 150 |
| **Hero** | | | **about 3300–3700; aim ≤ 3800; ceiling 4000** |
| Parts: Post (post + base + collar) / RidgePole (+2 bands) / Canopy / Banner (+rod) / Lantern / Table / Bench / Stool / Crate / Barrel / Peg | | | 220 / 130 / 220 / 176 / 180 / 150 / 96 / 60 / 290 / 230 / 50 |

- **Over budget?** Cut in this order: the table items (pot, then paper); crate plates 8 → 4 per crate; lashing sides 5 → 4
  and diagonal turns 2 → 1 on L1 / L2; barrel staves 10 → 8; the stool. **Never** drop a post, a base, the ridge pole, a
  lashing, a collar, a peg, the canvas thickness, the banner, the lantern or a bench.

### 4.4 Shape targets (binding; check with `M.audit` and own bmesh code)

- Posts 1.00 ± 0.05 square with visible chamfers; tall tops 12.0 ± 0.3, short tops 10.4 ± 0.3; centres 12.8 ± 0.4 × 9.2 ±
  0.4 apart.
- Bases 1.6 ± 0.15 wide, 1.2 ± 0.1 tall, flat tops level under the posts.
- Canvas every rim ≥ 0.09 thick; no single-sided face; corners 9.0 / 9.0 / 9.2 / 10.6 ± 0.3; lowest point ≥ 6.9.
- Banner 2.0 ± 0.2 × 5.9 ± 0.4; lantern body 1.1–1.2 wide × 2.0 ± 0.2; table 7.2 × 2.8 × 2.6 ± 0.2; crates 2.3 ± 0.15; barrel 2.8
  ± 0.15 tall.

### 4.5 Stages 2 and 3

- **Stage 2:**
  - Every shell closed and manifold, **0 bowties** (likely at the lashing crossings, the canvas corner tabs, the banner
    tongues, the crate plates).
  - **0 winding errors per shell** (`bmesh.ops.recalc_face_normals` per shell, then `m047.shells_report`); the canvas
    offset shell and the BR tab fold are where a reversed face slips in (044).
  - No zero-area faces; corners ≥ 3°; the canvas grid triangulated at build time (non-planar quads otherwise; M051).
  - Origin at the bbox bottom centre, transforms applied, every stored point re-checked.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box)

| Swatch | Hex (HSV) | Use |
| --- | --- | --- |
| Timber (Primary) | `#B5551E` (22°, .83, .71) | posts, ridge, crossbars, pegs (`timber`) |
| Canvas (Primary) | `#FDE9C1` (40°, .24, .99) | the canvas (`canvas`) |
| Rope (Detail) | `#D9C2A4` (34°, .24, .85) | the rendered rope is gold, §3.12 |
| Stone (Base) | `#A29493` (4°, .09, .64) | stone bases, loose stones (`stone`) |
| Banner (Accent) | `#CA1619` (359°, .89, .79) | banner (`banner`) |
| Lantern (Accent) | `#EF9808` (37°, .97, .94) | lantern glass and candle jars (`glow`; the rendered glass is lighter, §5.2) |

### 5.2 Rendered regions (`samp.py`, `emb.py`; median / lit quartile / shade quartile)

| Region | Median | Lit Q | Shade Q |
| --- | --- | --- | --- |
| Canvas: f34 / r34 / front / rear / top / exploded | `#FEF2CB` (46°, .20, 1.0) / `#FEEDC2` (43°, .24, 1.0) / `#FDE7BA` / `#F6DEB7` / `#FDE9BE` / `#FEEFC5` | `#FEF4CD` / `#FEF0C6` / `#FEEBBE` / `#FEF0C8` / `#FEEDC3` / `#FEF1C8` | `#FCEBC4` / `#E4C8A4` / `#ECC79C` / `#E2BC90` / `#FCE0B4` / `#FAE2B5` |
| Canvas close-up 1 / close-up 3 (underside) | `#FCE0B3` / `#DEB88D` (32°, .36, .87) | `#FEEEC3` / `#FDE8BB` | `#E7C396` / `#D4AD82` |
| Posts: exploded L / R / front ortho / close-up 1 / close-up 2 / f34 L / f34 R | `#A2480B` (24°, .93, .64) / `#923F0C` / `#AD531A` / `#AD4E18` / `#874116` / `#813911` / `#8E3F10` | `#D4630C` / `#DA680D` / `#D96C1B` / `#CC662A` / `#B4531A` / `#AF5115` / `#BD5816` | `#763109` / `#632909` / `#612611` / `#722E0E` / `#703110` / `#5C270B` / `#5E2306` |
| Ridge pole: exploded / f34 / close-up 3 | `#873A0F` (22°, .89, .53) / `#8F3C0F` / `#702F0B` | `#DE741E` / `#E2721D` / `#BE6324` | `#5B230A` / `#77300C` / `#471903` |
| Furniture: table top (exploded) / long bench / short bench / f34 table / front table | `#C4662C` (23°, .78, .77) / `#A85A26` (24°, .77, .66) / `#A95A26` / `#8F4419` / `#793D19` | `#D87835` / `#DC7A36` / `#DA7A38` / `#E07725` / `#BC6025` | `#5F2C13` / `#562611` / `#4E220F` / `#401C0B` / `#35170B` |
| Crates (exploded L / R / front) / barrel staves (exploded / f34) | `#7D3E20` (19°, .74, .49) / `#743A1F` / `#874825` / `#7B3B1B` / `#713517` | `#CD7433` / `#CC7031` / `#B45F2D` / `#B95E28` / `#9E4C21` | `#462013` / `#401D11` / `#451F14` / `#3C1B0F` / `#38170A` |
| Crate straw (L / R) / barrel top | `#F7D69A` (39°, .38, .97) / `#F8D596` / `#D3CAC1` (29°, .09, .83) | `#FBDEA5` / `#FCE2AF` / `#E5DFD8` | `#EDC886` / `#E9BD79` / `#C2B8B3` |
| Peg: exploded / close-up 2; exploded tip | `#813C15` / `#994E12`; tip `#E0CCAD` | `#BE5915` / `#D56E25` | `#552713` / `#5E2908` |
| Rope: f34 / front / close-up 1 / close-up 2 collar / exploded | `#DFA448` (37°, .68, .87) / `#DC9E42` / `#DB9738` / `#E49738` / `#E5A152` | `#FAC558` / `#F5BE45` / `#FAC966` / `#FDD376` / `#F9BF65` | `#C27921` / `#BC7E32` / `#BD7120` / `#B46A1C` / `#C0813A` |
| Banner red: f34 / front / exploded | `#E01517` (359°, .91, .88) / `#DD1518` / `#B10C0F` | `#E71A1B` / `#E4191E` / `#BA1012` | `#CB0C0D` / `#CA090B` / `#9B0609` |
| Banner emblem white: f34 / front / exploded | `#FDF4F3` / `#FDEFEA` / `#F3F3EF` | | |
| Lantern glass: VFX panel / f34 / exploded; candle jars f34 | `#FCC005` (45°, .98, .99) / `#F7B705` / `#FAB705`; `#F4AA05` | `#FFCA08` / `#FDCA07` / `#FEC608`; `#FED529` | `#F6AE02` / `#EE9E05` / `#F2A503`; `#E48B01` |
| Lantern metal (VFX frame) / crate plates / barrel hoops | `#5C4738` (26°, .39, .36) / `#433938` / `#878285` (320°, .05, .53) | `#816854` / `#504448` / `#BEB8B1` | `#4E3B2D` / `#2B2425` / `#615D64` |
| Stones: exploded / f34 / f34 b / close-up 2 (base) | `#AA9794` (8°, .13, .67) / `#B39F9B` / `#9E8C88` / `#706365` | `#DCCBC7` / `#DFCFC6` / `#D8CAC1` / `#A99791` | `#6C5F66` / `#665A5D` / `#75676B` / `#6A5E5E` |
| Green bottle (f34) / paper (f34) | `#707B37` (71°, .55, .48) / `#FDEEAA` | `#989C4B` / `#FEF9BE` | `#5A622E` / `#FBE9A6` |
| Grass (not modelled) / cast shadow (not modelled) | `#697817` / `#F2E9DE`–`#C7C3BC` | | |

### 5.3 How the colour works

- **Posts, ridge, crossbars:** `timber`; the **lowest 1.0 of each post** (just above its collar) blended one step toward
  `wood_dark` by height (weathered feet); post tops and chamfers keep `timber` (their lit look is the light). Per-piece
  Tint 0.04 with a 0.02 lengthwise variation (grain lines the sheet draws on the posts).
- **Furniture (table, benches, stool):** `plank`, one step lighter and less saturated than the posts (the sheet's furniture
  reads lighter at the same lighting); per-plank Tint 0.05 (the plank-by-plank value steps); legs and stretchers one step
  toward `timber`.
- **Crates and barrel:** `wood_dark`, per-plank / per-stave Tint 0.05; crate frame boards and X braces one step toward
  `plank`; corner plates `metal`; straw `straw`, blended toward `straw_deep` by height (the mound's foot darker), 3 steps;
  barrel hoops `iron`; the barrel's contents disc `pale`.
- **Canvas:** `canvas` on every canvas face, **top and underside alike**; a **hem band** (faces within 0.35 of the sheet's
  outer edge, by distance in the sheet) blended three steps to `canvas_deep` (close-up 3's darker rim); a 0.3 band round
  each lashing contact, by distance, one step to `canvas_deep` (rope rub). Broad Tint 0.03 per crease facet region.
- **Rope:** `rope` body; one strand in four (by strand index along the twist) `rope_deep`; the lashing turns hidden
  between timbers and canvas (by position) `rope_deep`. Tint 0.03 per piece.
- **Stone:** bases and loose stones `stone`, the lowest 25 % blended one step to `stone_deep` by height; Tint 0.05 broad.
- **Pegs:** stake `timber` one step toward `wood_dark`, top face `end_grain`, band `rope`.
- **Banner:** `banner` body, the hem one step deeper (`banner` → 10 % darker by role), emblem insets `banner_white`; rod
  `iron`, knob `metal`.
- **Lantern:** base, bars, band, roof, cap, ring `metal`; glass `glow` (Neon).
- **Table items:** jars `glow` (Neon) with `metal` lids; bottle `bottle`; paper `canvas` one step toward `straw`; pot
  `metal`.
- **Never by facing.** No face gets a colour because of which way it points: the canvas underside's tan, the dark post
  sides, the lavender stone shade and the shaded furniture undersides are all the light.
- **Hues stay apart:** timber 21–25° (s 0.84–0.92); plank 22–26° (s 0.72–0.80, lighter than timber); wood_dark 18–22° (v ≤
  0.52); canvas 40–46° (s 0.20–0.26, v ≥ 0.95 rendered); canvas_deep 32–38°; rope 33–38° (s 0.62–0.74); rope_deep 30–35°;
  straw 37–41° (s 0.36–0.44); stone 6–14° (s 0.10–0.15, R > G > B); banner 357–2°; metal warm (h 20–30°, s 0.25–0.40, v
  0.25–0.36); iron cool grey (s ≤ 0.08); glow 40–45°.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians where the sheet gives them, swatches where it doesn't. `K.sample` kinds:
`"brown"` for timber, plank, wood_dark, end_grain, rope, rope_deep, straw, straw_deep; `"stone"` for canvas, canvas_deep,
stone, stone_deep, metal, iron, pale, banner_white; `"vivid"` for banner, glow; `"green"` for bottle (check with
`M.raw_sample` on the swatches too). Start the timber from M064's / M051's calibrated values (their targets `#A3501A` /
`#9D4D18` are next to ours).

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m066_timber` | `#A84D16` ± 12 (posts exploded `#A2480B` / `#923F0C`, front `#AD531A`, cu1 `#AD4E18`; swatch `#B5551E`) | 21–25°, 0.84–0.92 | posts, ridge, crossbars, peg stakes | rough 0.85 |
| `m066_plank` | `#A85A26` ± 12 (benches `#A85A26` / `#A95A26`; table lit `#D87835`) | 22–26°, 0.72–0.80, lighter than timber | table, benches, stool | rough 0.85 |
| `m066_wood_dark` | `#7C3E20` ± 12 (crates `#7D3E20` / `#743A1F` / `#874825`, staves `#7B3B1B`) | 18–22°, 0.72–0.80, v ≤ 0.52 | crates, barrel, post feet (blend) | rough 0.9 |
| `m066_end_grain` | `#D8BC98` ± 15 (peg tip `#E0CCAD`) | 28–36°, 0.20–0.32 | peg tops | rough 0.9 |
| `m066_canvas` | `#FEEDC2` ± 10 (r34 `#FEEDC2`, top `#FDE9BE`, exploded `#FEEFC5`, front `#FDE7BA`; swatch `#FDE9C1`) | 40–46°, 0.20–0.26 | canvas | rough 0.95, low spec |
| `m066_canvas_deep` | `#E6C49C` ± 12 (shade quartiles `#E4C8A4` / `#E2BC90` / `#E7C396`) | 32–38°, 0.28–0.36 | hem band, rope rub (blend) | rough 0.95 |
| `m066_rope` | `#DDA048` ± 12 (f34 `#DFA448`, front `#DC9E42`, cu1 `#DB9738`, exploded `#E5A152`) | 33–38°, 0.62–0.74 | all rope | rough 0.95 |
| `m066_rope_deep` | `#BC7A2C` ± 12 (shade quartiles `#C27921` / `#BC7E32` / `#BD7120`) | 30–35°, 0.74–0.82 | one strand in four, hidden turns | rough 0.95 |
| `m066_straw` | `#F7D598` ± 10 (crates `#F7D69A` / `#F8D596`) | 37–41°, 0.36–0.44 | crate straw | rough 0.95 |
| `m066_straw_deep` | `#EAC27F` ± 12 (shade `#EDC886` / `#E9BD79`) | 36–40°, 0.42–0.50 | straw mound foot (blend) | rough 0.95 |
| `m066_stone` | `#AE9C98` ± 12 (exploded `#AA9794`, f34 `#B39F9B`; swatch `#A29493`) | 6–14°, 0.10–0.15, R > G > B | bases, loose stones | rough 0.92 |
| `m066_stone_deep` | `#8C7E7C` ± 12 | 6–14°, 0.09–0.14 | stone feet (blend) | rough 0.92 |
| `m066_banner` | `#D51518` ± 12 (f34 `#E01517`, front `#DD1518`, exploded `#B10C0F`; swatch `#CA1619`) | 357–2°, 0.88–0.93 | banner | rough 0.9 |
| `m066_banner_white` | `#F8F0EC` ± 8 (f34 `#FDF4F3`, front `#FDEFEA`, exploded `#F3F3EF`) | s ≤ 0.06 | emblem insets | rough 0.9 |
| `m066_metal` | `#54423A` ± 10 (lantern frame `#5C4738`, shade `#413127`; plates `#433938`) | 20–30°, 0.25–0.40, v 0.25–0.36 | lantern frame, crate plates, jar lids, pot, rod knob | rough 0.55, metal 0.4 |
| `m066_iron` | `#827D80` ± 12 (hoops `#878285`, lit `#BEB8B1`) | s ≤ 0.08, v 0.45–0.55 | barrel hoops, banner rod | rough 0.5, metal 0.5 |
| `m066_glow` | `#F9B806` (glass `#FCC005` / `#F7B705` / `#FAB705`; swatch `#EF9808`), **emission 1.0** | 40–45°, ≥ 0.94 | lantern glass, candle jars (Neon) | — |
| `m066_pale` | `#D6CEC6` ± 10 (barrel top `#D3CAC1`) | s ≤ 0.10 | barrel contents | rough 0.6 |
| `m066_bottle` | `#727D3A` ± 12 (`#707B37`) | 68–75°, 0.50–0.60 | bottle | rough 0.4 |

**Calibration warnings:**
- **The canvas is pale cream, never yellow and never white** (W10's `#E3CFA0` read yellow): side and front renders within
  10 of `#FEEDC2`, saturation 0.20–0.28; the lit panel must not clip to white.
- **The posts are saturated orange-brown, not red and not flat orange:** hue ≥ 21°; the furniture reads a step lighter
  and softer, the crates and barrel clearly darker.
- **Rope is warm gold, not lemon and not orange-brown:** h 33–38°; the Y share on the f34 comes from the glass and jars
  only (≤ 1.4 %), not from the rope.
- **Stone is warm pale grey, R > G > B, never lavender** (059 ruling; the sheet's lavender is shade).
- **Banner red stays clean red** (h 357–2°), not orange-red; the emblem off-white, not pink.
- **Lantern metal is warm dark brown-grey, not black** (v ≥ 0.25 rendered); the hoops and rod a lighter cool grey.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Canvas:** by distance from the sheet's outer edge (hem band); by distance to each lashing contact (rub band).
- **Posts:** by height (feet → body), 3 steps over z 1.2–2.2.
- **Furniture:** legs and stretchers vs planks by part role (one step).
- **Crates:** frame boards vs panels by role; plates hard.
- **Straw:** by height in the mound.
- **Stones and bases:** by height in the stone.
- **Hard edges only** where materials meet: canvas | rope, rope | timber, metal | glass, metal | wood, banner | emblem,
  straw | crate, stone | post.

### 5.6 Texture (Tint) and finish
- **Tint:** canvas 0.03 per crease facet region (broad, never per triangle); posts 0.04 per post + 0.02 grain; planks and
  staves 0.05 each; rope 0.03 per piece; stones and bases 0.05; banner 0.02; straw 0.04.
- **Finish:** everything matte (wood 0.85–0.9, canvas, rope and straw 0.95, stone 0.92), metal rough 0.55 / metal 0.4, iron
  0.5 / 0.5, glass emissive; no emission anywhere but the lantern glass and the jars.

### 5.7 Re-measure (final renders against the sheet, same masks)
- **Canvas:** front-render C median within 10 of `#FDE7BA`; top-render C median within 10 of `#FDE9BE`.
- **Timber:** front-render post median within 12 of `#AD531A`; f34 W median within 15 of `#7A3912` (shaded sheet median).
- **Rope:** f34 R median within 12 of `#DFA448`.
- **Banner:** front-render B median within 12 of `#DD1518`.
- **Glow:** Y share on the f34 0.8 ± 0.6; glass median within 12 of `#F7B705`.
- **Shares** per §2.13.

## 6. Joins and contact (no floating dressing, no buried dressing)

- **Shells:** each base, post, the ridge, each crossbar, the canvas (with its tabs), each lashing, tail, collar, peg, peg
  rope, band, the rod, knob, banner (with its emblem insets touching it), each lantern piece, each furniture piece (planks,
  legs, stretchers as touching closed shells), crate parts, straw mounds, barrel parts, stones, table items: closed shells,
  all in one hero object.
- **Chain to the ground:** bases → ground; posts → bases; ridge and crossbars → posts; lashings → posts and the timbers
  they bind; canvas → lashings and the ridge (tabs); rod → FR crossbar; banner → rod; lantern ring → FR crossbar; collars
  → posts; pegs → ground and bases; peg ropes → pegs and collars; furniture, barrel, crates, stones → ground; items →
  table; straw → crate floors; hoops, plates, emblems, lids → their bodies.
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**. A shell floats if its nearest distance to
  every other shell and the ground is > 0.03, or if it doesn't chain to the ground. The new risks: the canvas tabs (each
  must touch its timber and sit under its lashing), the BR fold over the ridge, the banner rod (on the crossbar, not
  beside it), the lantern ring, the emblem insets, the table items, the straw.
- **Buried shells:** nothing more than 0.05 inside anything beyond its stated seat (lashing turns ≤ 0.03 into timber and
  canvas, rope ends 0.03 into bands and collars, the ridge and crossbars **touching** the posts, never through them). Ray
  parity against the posts, bases, ridge, table, crates and barrel as solids after the final placement step
  (`m047._Solids`).
- **No intersections between big pieces:** the canvas never passes through a post, crossbar or the ridge (the tabs wrap
  them); no furniture or dressing touches a base or a peg unless it rests on it.
- **Walk report:** the §2.10 proxy paths, minimum clearance printed (≥ 0.05 everywhere along them), plus the canvas
  minimum z over the floor inside the posts (≥ 6.9).
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.
- **Winding:** 0 errors per shell, checked with a parity ray test, not only the signed volume (044's wedge back face).
- **Parts:** each exported part self-contained (the Post with its base and collar touching; the Banner with its rod; the
  Lantern's pieces chained; the RidgePole's two bands hugging it; the Crate with its straw).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** one hanging lantern with bright amber glass and its own "VFX (SEPARATE)" panel (a soft warm
radial glow, explicitly a separate effect, not geometry), two glowing candle jars on the table, no fire, smoke, dust or
sparkle. The cast shadows are the illustration's.

- **Stage 5 (lighting):**
  - The lantern glass and both candle jars on `m066_glow` with **emission 1.0** (the exporter's Neon threshold; they
    export as Neon glow pieces). Use m009's `_glow_mats` preview so the Blender render shows them as Roblox Neon will.
  - **No light painted on the canvas or table** (no glow patch round the lantern): the light comes from the socket.
  - Studio notes (Requires Manual Validation): the canvas stays pale cream in daylight and warm-lit at night; the canopy's
    underside reads darker by shadow, not paint; the posts read saturated orange-brown, the furniture a step lighter, the
    crates and barrel darker.
- **Stage 6 (VFX):** one **`heat_glow`** socket at the lantern's glass centre (no lantern kind exists in `lib/vfx.py`; W10
  and M064 used `heat_glow` on lanterns), overridden to a steady lantern halo, not a furnace shimmer (M064's settings):
  - `emitters=[{"name": "Halo", "texture": "glow_soft", "color": ["#FFC23A", "#FF9A1E"], "size": [1.4, 1.7],
    "transparency": [0.65, 1.0], "lifetime": [1.0, 1.5], "rate": 2, "speed": [0, 0.05], "spread": 0,
    "light_emission": 1.0}]`;
  - `light={"color": "#FFB347", "brightness": 1.0, "range": 14, "flicker": True}` (range 14 reaches the table and both
    benches from the front-right corner).
  - Socket at (4.85, −5.35, 7.85) in the build frame, passed through `M.mk`'s `fx=` list (it shifts with the origin). The
    candle jars get **no socket** (Neon only). Check the export STATS line reports **1 socket** on the hero and 1 on the
    Lantern part.
- **Collision (decision §8.11):**
  - **Hero `precise`** (PreciseConvexDecomposition): posts, bases, furniture and dressing solid; the canvas above head
    height. **Requires Manual Validation in Studio:** a default character walks under the canopy from the front and the
    back and reaches both benches without snagging; nothing fills the space under the canvas. If the decomposition bridges
    the canvas down to the posts or furniture, the fallback is hero `none` plus Studio colliders (four post-and-base
    boxes, table, two bench and stool boxes, crate boxes, a barrel cylinder; the canopy left non-colliding).
  - Parts: `CanvasShelterPost` `hull`; `CanvasShelterRidgePole` `box`; `CanvasShelterCanopy` `none`; `CanvasShelterBanner`
    `none`; `CanvasShelterLantern` `none`; `CanvasShelterTable` `box`; `CanvasShelterBench` `box`; `CanvasShelterStool`
    `box`; `CanvasShelterCrate` `box`; `CanvasShelterBarrel` `hull`; `CanvasShelterPeg` `none`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched all 2467 names in `art/roblox/kit/**/manifest.json` (`man.py`) and the repo text
(`grep -r`, all files) for Shelter, Canopy, Awning, Camp, Banner, Bench, Table, Lantern, Stool, Post and the candidates:
- **W10:** `CampAwning`, `CampAwningCanvasCanopy`, `CampAwningLeanTo`, `CampAwningLongShelter`, `CampAwningPeg`,
  `CampAwningRidgePole`, `CampAwningSquareStall`, `CampAwningTableSet`, `CampAwningWoodPost` (and their
  `VFX_…heat_glow_1` sockets); `RuinLeanTo*` (incl. `RuinLeanToCanvasCanopy`, `RuinLeanToSnowShelter`,
  `RuinLeanToUprightPost`); `TimberHut*`; `AFrameTent*`. **Other:** `TableAndSeating*` (`…BenchSeat`, `…LongBench`,
  `…Stool`, `…TableTop`, `…Trestle`, `…Workbench`), `PalisadeWallBanner`, `FireAndLightLanternPost`,
  `FortWorkshopLanternHook`, `StorageCornerPost`, many `…Post` names. **M064 (spec, not yet exported):** `CanvasTent`,
  `CanvasTentFrame`, `…Panel`, `…Mat`, `…Crate`, `…Barrel`, `…Stone`, `…Peg`, `…Lantern`.
- **`CanvasShelter` and every `CanvasShelter…` part name below, and `m066`, occur nowhere** in the manifests or the repo
  text. No owned name is a substring of them (`CampAwningLongShelter` contains "Shelter", not "CanvasShelter";
  `CanvasTent…` shares only "Canvas").

| Object | Part | Why |
| --- | --- | --- |
| `CanvasShelter` | hero: 4 bases, 4 posts, ridge, 3 crossbars, canvas, lashings, collars, pegs, banner + rod, lantern, table + items, 2 benches, stool, barrel, 2 crates, 2 stones | W10 owns `CampAwning*`; the sheet's title |
| `CanvasShelterPost` | "Wood Post (x4)": a 12.0 post on its stone base with its collar (the short posts are the same mesh scaled in Studio, or cut) | the label; base folded in (close-up 2) |
| `CanvasShelterRidgePole` | "Ridge Pole", with its two end bands | the label |
| `CanvasShelterCanopy` | "Canvas Canopy": the sagging sheet with its tabs (BR tab unfolded flat for reuse) | the label |
| `CanvasShelterBanner` | "Banner & Rod (x1)": banner, emblem, rod, knob | the label |
| `CanvasShelterLantern` | the lantern (VFX panel), with its `heat_glow` socket | reused; useful in any camp |
| `CanvasShelterTable` | long table | furniture (model notes) |
| `CanvasShelterBench` | long bench (the short bench is a shorter build of the same function; not exported) | furniture |
| `CanvasShelterStool` | stool | furniture |
| `CanvasShelterCrate` | open crate with straw | dressing, reused |
| `CanvasShelterBarrel` | hooped open barrel | dressing, reused |
| `CanvasShelterPeg` | "Peg (x4)": stake, band, pale top | the label |

- Palette keys `m066_*` (§5.4). Collection `Kit/M066 Canvas Shelter`. Socket: 1 × `heat_glow` on the hero, 1 on the
  Lantern part. Stored points `m066_offset`, `m066_centre`, `m066_seat_back`, `m066_seat_front`, `m066_seat_stool`,
  `m066_lantern` on the hero; `m066_hang` on the Lantern and Banner parts; `m066_top` on the Post part.

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **tall posts 12.0 (FR, BR), short posts 10.4 (FL, BL), on 1.2 stone bases; post centres 12.8 × 9.2;
   canvas corners 9.0 / 9.0 / 9.2 / 10.6, lowest point ≈ 7.05; hero ≈ 17.3 × 12.3 × 12.0** (recommended: realistic
   furniture against the 5.5 character, the kit's crate size, walk under and sit at the table). Alternatives: tall posts
   11.0 (lowest canvas ≈ 6.2: tall avatars clip) or 13.0 (furniture reads small).
2. **Build frame and origin (§1.1, §2.12):** **front −Y (banner and lantern at the front-right), the tall side +X;
   origin at the bbox bottom centre with the offset, centre, seat and lantern points stored** (recommended).
3. **What the hero includes (§3.11, §3.14):** **the shelter plus the exploded's furniture and dressing (table with five
   items, long and short bench, stool, barrel, two open crates, two stones); no grass, cabinet or chest** (recommended).
   Alternative: a bare shelter hero (posts, ridge, canvas, rope, pegs, banner, lantern) with everything else only as
   parts.
4. **Frame (§2.2, §2.3, §3.2, §3.4):** **four 1.0 chamfered square posts on faceted stone bases; the 0.8 ridge pole along
   the tall right side on the posts' inner faces, level at z 10.2–11.0, 0.8 past both posts; 0.5 crossbars on the outer
   faces of FL, BL and FR; everything touching, no booleans** (recommended). Alternative: a sloping ridge with BR at 10.4
   (the side cell).
5. **Canvas (§2.4, §3.6, §3.15):** **one closed 0.10 slab on a 7 × 5 grid; corners 9.0 / 9.0 / 9.2 / 10.6 with the BR
   apex folded over the ridge pole; sag 1.2 per edge, 2.4 in the centre; centre-pointing diagonals for the X creases;
   corner tabs wrapping each post under its lashing** (recommended). Alternative: sag 1.6 (closer to the front cell,
   lowest 6.25).
6. **Rope (§2.7):** **twisted gold tubes: five X-lashings (FL, BL, FR lower, FR upper, BR), two dangling tails, four foot
   collars, four peg ropes and bands, a rod band; every rope touching what it ties** (recommended).
7. **Pegs (§2.8, §3.10):** **one square peg per post leaning on the base's outer face, roped to the collar; no guy
   ropes** (recommended).
8. **Lantern (§2.6, §3.7):** **one hexagonal lantern hung from the FR crossbar's inner end, in front of the canopy edge,
   body 6.95–8.99** (recommended). Alternative (open question): a second lantern at FL.
9. **Banner (§2.5, §3.8):** **one banner on an iron rod under the FR crossbar, facing front, 2.0 × 5.9, three tongues,
   emblem on both faces** (recommended). Alternative (open question): the f34's second banner at FL.
10. **Furniture and dressing layout (§2.9):** **table centred a little left and back, long bench behind, short bench in
    front, stool at the right end, barrel on the left post line, crates in the right-hand corners, stones outside the
    front edge; seat points stored** (recommended).
11. **Collision (§7):** **hero `precise` with a Studio walk-under check (fallback `none` + Studio colliders); Post `hull`,
    RidgePole `box`, Canopy / Banner / Lantern / Peg `none`, Table / Bench / Stool / Crate `box`, Barrel `hull`**
    (recommended).
12. **Comparison cameras (§2.13):** **`front_sheet (0, 3)`, `rear_sheet (180, 0)` and `side_sheet (90, 0)` govern the
    frame; `f34_sheet (−45, 20)` (probe az −30 … −50, e 15–25) governs the read and dressing; `r34_sheet (135, 20)` and
    `top` content only; close-ups `junction_cu`, `base_cu`, `underside_cu`, `lantern_cu`, `walk`, `thumb`, `spin`; parts
    and exploded shots; scale shot. Floor hidden in every `*_sheet` render** (recommended).
13. **VFX (§7):** **Neon glass on the lantern and both candle jars; one `heat_glow` socket at the lantern, overridden to a
    steady halo (rate 2, no drift) with a warm PointLight range 14; no socket on the jars** (recommended). Alternative: a
    small second socket at the jars (light range 6, brightness 0.5).
14. **Exports (§8 table):** **the hero plus eleven parts: Post, RidgePole, Canopy, Banner, Lantern, Table, Bench, Stool,
    Crate, Barrel, Peg** (recommended). Alternatives: drop Stool and Peg (nine parts), or reuse M064's `CanvasTentBarrel`
    instead of a new barrel (its lid differs from this open barrel: not recommended).
15. **Colour (§5):** **posts `#A84D16`, furniture `#A85A26`, crates and barrel `#7C3E20`, canvas `#FEEDC2` with a `#E6C49C`
    hem, gold rope `#DDA048` with a `#BC7A2C` strand, stone `#AE9C98`, banner `#D51518` with an `#F8F0EC` emblem, warm
    metal `#54423A`, cool iron `#827D80`, Neon glass `#F9B806`, straw `#F7D598`; by role and position, never by facing;
    the canopy's shaded underside is lighting** (recommended).
16. **Budget (§4.3):** **full asset: 4000 ceiling, plan 3300–3700; parts under 1000; cut table items, crate plates and
    lashing turns first** (recommended).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **The old awning's failures (W10 / MODEL_PROGRESS row 81: "flat sheet … sparse clutter; no lantern glow").** A
   deeply sagging canvas with X creases, the full furniture set, a Neon lantern with its halo; chunky 1.0 square posts,
   not thin round sticks.
2. **Single-sided canvas (Roblox culls back faces).** The canopy is seen mostly from below: a closed 0.10 slab, proved by
   `underside_cu` and the spin.
3. **A canopy you can't walk under.** Canvas ≥ 6.9 everywhere over the floor; the walk report and the Studio check
   recorded as Requires Manual Validation.
4. **Floating or buried pieces** (STAGES; 035 / 036 round 1; 046). The canvas tabs touch their timbers under the
   lashings, the ridge and crossbars touch the posts (never through them), the rod sits on the crossbar, the lantern ring
   on the crossbar, the items on the table, the straw on its floor. Count: floating 0, buried 0.
5. **Posts standing in the ground.** Every post sits on its stone base (close-up 2), the collar on the base top.
6. **Rope that reads as flat collars or thin outlines** (M048 finding 1; M051 finding 1). Twisted tubes Ø 0.22–0.24, the X
   of each lashing visible in `junction_cu`.
7. **Rope colour drift.** Gold `#DDA048`, not M064's beige and not lemon; one deep strand in four.
8. **Yellow or white canvas** (W10 verifier: `#E3CFA0`). Pale cream `#FEEDC2`, s 0.20–0.28, no clipped highlights.
9. **One wood colour everywhere.** Three wood keys by role: saturated posts, lighter planks, darker crates and barrel;
   per-plank Tint.
10. **Red or flat-orange wood** (W08). Timber hue ≥ 21°.
11. **Colour by facing** (042 ruling; 054 m9). The canvas underside, dark post sides, lavender stone shade and furniture
    undersides are light. `K.check` facing correlation < 0.5 per material.
12. **Hard colour bands** (M051 finding 5; M052 finding 3). The canvas hem, post feet, straw and stones blend over three
    steps.
13. **Egg stones and box bases** (M034 / M037). Faceted pale blocks with broken edges and flat bottoms; base tops flat
    under the posts.
14. **Winding and non-planar quads** (044; M051 finding 8). 0 winding errors per shell (canvas offset, BR fold, banner
    tongues, crate plates); triangulate the canvas grid at build time.
15. **Proportions from the stylised cells** (§3.2–§3.5). Front and rear set X and heights, the side sets only the depth,
    the f34 sets construction and dressing, the r34 and top are content only.
16. **Names and scope.**
    - No `CampAwning*`, `RuinLeanTo*`, `TimberHut*`, `TableAndSeating*`, `CanvasTent*` names.
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit the frozen shared helpers (`kit_models.py`, `kit_mcp.py`, `build_kit.py`, `lib/vfx.py`) or other models'
      builders; import from the committed ones (`m047`, `m051`, `m052`, `m038`); don't touch other models' collections.

## Decisions (main session, 2026-10-31)
All 16 recommendations are accepted. The open questions are ruled as follows:
1. **Size.** As recommended. The canvas's lowest point is about **7.05**, so characters walk under it and sit at the table. Walkability governs over the front and rear cells' deeper sag.
2. **Build frame and origin.** As recommended, storing `m066_offset`, `m066_centre`, the seat points and `m066_lantern`.
3. **Hero.** The shelter plus the exploded view's furniture set. No grass, cabinet or chest.
4. **Frame.** As recommended. The **ridge pole is level on two equal 12.0 posts**; the side view's short back post is a drawing slip. Pieces touch rather than overlap, with no booleans.
5. **Canvas.**
   - One closed slab: **no single-sided planes**.
   - The sag and the X creases come from geometry.
   - The corner tabs and the ridge fold touch their posts and pole within 0.03, and none of it is buried more than 0.05.
6. **Rope.** Twisted **gold** tubes as drawn; this differs from 064's beige rope, as the sheet does. Every rope touches what it ties at both ends.
7. **Pegs.** One per post, leaning on its stone base and roped to the post's foot collar.
8. **Lantern.** **One**, at the front-right post. No second lantern.
9. **Banner.** **One**, on the iron rod, with the emblem on both faces. No second banner.
10. **Furniture layout.** As §2.9. Every item stands on the ground or on the table, with none floating.
11. **Collision.** As recommended. The hero walk-under goes on the **Requires Manual Validation** Studio list alongside 052 and 064; the fallback is `none` plus Studio colliders.
12. **Cameras.** As recommended, including a walk-under shot with a 5.5-stud proxy and the eight-azimuth spin.
13. **VFX.** Emissive Neon glass (at least 1.0) on the lantern and both candle jars, plus one `heat_glow` socket on the lantern, tuned to a steady warm halo.
14. **Exports.** Hero `CanvasShelter` plus all **eleven** parts; keys `m066_*`. Never `CampAwning` or `CanvasTent*`.
15. **Colour.**
    - Use the colours as listed, by role and position, **never by facing**.
    - Canvas and stone stay warm, never lavender or grey-blue.
    - The banner red is saturated, not pink.
16. **Budget.** Full asset: ceiling 4000 (plan 3300–3700), every part under 1000, with the cut order as listed.
