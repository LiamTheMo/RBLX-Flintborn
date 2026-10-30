# 048 Dock — spec

Reference: `art/blender/assets/references/048.png` (1024 × 1536 px). The sheet's title is "50/132 | DOCK" (the printed
50 is the generator's number; INDEX.md row 48 calls it "Flintborn dock model study"). The footer reads "FLINTBORN —
INDIVIDUAL MODEL STUDY".
Builder: `art/blender/kit/mcp/m048.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no water, foam, glow or effect** (§7).

Sheet text:
- **Cells:** "ASSEMBLED — FRONT THREE-QUARTER", "ASSEMBLED — REAR THREE-QUARTER", "ORTHOGRAPHIC VIEWS (CONSISTENT
  GEOMETRY)": "FRONT VIEW", "SIDE VIEW", "REAR VIEW", "TOP VIEW". The "orthographic" cells are near-level views (front
  e ≈ 2°, rear e ≈ 6°: the rear shows the plank tops); the top view is a plan.
- **Exploded:** "EXPLODED VIEW & PARTS": labels "Rope Segment", "Mooring Post", "Beam" (two), "Brace", "Crossbeam".
  Also drawn, unlabelled: 4 mooring posts with two rope coils each (dashed arrows drop them onto the deck / piles), 2 tall
  piles with a bolt block and bolt pin on one face, a dowel hole on top and two holes near the foot, a deck group of 9
  boards plus 1 loose board, 4 small bolt blocks with round bolt heads, the crossbeam with a short post stub at one end.
- **Close-ups:** "JUNCTION DETAIL" (a post rising through the deck edge, two rope coils, a swag leaving, a bolt block
  with a big round brass bolt head under the deck), "UNDERSIDE DETAIL" (dark plank bottoms, the side beam, a bolt block,
  a knee brace from the leg to the beam), "PLANK CROSS-SECTION": "Deck Plank (Top / Side / Bottom)" (a chunky board with
  softened top edges).
- **Key reusable parts (isolated):** "Mooring Post", "Deck Plank", "Beam", "Crossbeam", "Brace", "Rope Segment" (a
  sagging twisted rope with knob ends).
- **Material palette:** five unlabelled swatches: orange wood, tan, grey, green, blue (§5.1).
- **Modeling notes:** "Use chunky, low-poly, stylized forms with broad flat-shaded faces." "Keep proportions, silhouette
  and part shapes consistent with Flintborn style." "Timber uses simple solid color blocks, subtle value variation only
  (no wood grain texture, no noise)." "Rope is a separate mesh piece." "Parts are modular and reusable across docks."
  "Keep clean geometry with clear join points and flat surfaces." "No additional variants, props or environment
  elements on this page."
- **Game context:**
  - **W08 owns the old kit's dock** (`art/blender/scripts/kit/W08/dock.py`, goals `art/blender/renders/kit/W08/dock_goals.md`,
    manifest `art/roblox/kit/W08/manifest.json`): `Dock`, `DockStraight`, `DockTHead`, `DockLHead`, `DockPile`,
    `DockMooringPost`, `DockRopeTie`, `DockDeckPlank`, `DockBeam`, `DockBrace`; keys `w08_*`. It is a different drawing
    (6.5 × 8.5 × 5.2, deck top 3.2, octagonal post caps). `MODEL_PROGRESS.md` row 73 flags it "square posts (ref round
    with rope ties); flat orange; boxy heads"; its goals record "wood still renders slightly red". Reuse its lessons,
    not its names or sizes (§8).
  - **Water tiles** (M032 / M034 / M041 / M037): ground and bed bottom z 0, bed 0 → 0.2, **water 0.25 → 1.0**, foam
    1.03 → 1.07; keys containing "water" export see-through. **Shore tops:** M041 sand crest 1.6, M034 banks 1.6, M032
    sand 1.0 → 1.8. **M043 lower lawn 5.6**, upper 10.4; M044 ramp 0.35 → 10.4.
  - WorldModeling §13.1–13.2 (timber vocabulary; docks): squared timbers with restrained bevels (0.02–0.05 of the
    width), posts stronger than rails, "Build load-bearing components first: piles/posts, longitudinal beams,
    crossbeams, deck planks, then rails and rope. Inspect from underneath", "Rope rails are thick low-resolution
    curves/tubes with restrained sag. Do not model individual rope fibers", and the dock kit's later pieces: "short bay,
    straight span, corner/landing, ramp end, and damaged version".

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Cell paper `#FEFCF7` (254,
252, 247), tolerance 10. Cell borders from the grey rule lines (`lines.py`). Labels and callouts are painted out
(`TITLES` in `m.py`). Masks are `cls()` in `m.py` (HSV, h in degrees, in this order):
- **T** outlines / text: v < 0.16, or s < 0.25 and v < 0.35.
- **B** ground shadow: s < 0.12, v ≥ 0.70 (pale blue-grey `#B3B8C0`). Excluded from shares.
- **Y** rope and brass: h 36–62, s ≥ 0.18, v ≥ 0.60; or h 33–36, s < 0.62, v ≥ 0.75.
- **W** lit wood: h < 40 (or > 345), s ≥ 0.35, v ≥ 0.62 (plank tops, lit post caps, lit plank ends).
- **K** dark wood: the rest of the wood hues, s ≥ 0.25, v ≥ 0.16 (post and beam faces, legs, braces, shade).
- **O** other.
- W / K is a **lit / dark** split, not a material split: the sheet's wood is one orange family (§5).
- Cells: f34 (15,113,512,419); r34 (514,113,1009,419); front (15,492,296,730); side (297,492,560,730); rear
  (561,492,817,730); top (818,492,1009,730); exploded (15,739,717,1260); junction (727,739,1009,939); underside
  (727,949,1009,1123); plank cross-section (727,1133,1009,1260); key parts (15,1269,645,1484). Swatches: 32 × 32 inner
  boxes at y 22–52, x 714 / 776 / 838 / 900 / 962 (`m.SW`).

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m048_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14, Pillow, numpy).
- **Helpers:** `m.py` (masks, boxes `V` / `X` / `SW` / `TITLES`, `label`), `zoom.py` (crop with an optional sheet
  grid), `px.py` (pixel probe), `lines.py` (cell borders).
- **Measurements:** `measure.py` → `bb.json` and `cls_*.png` (bbox, W : H, shares, top profile, width per height,
  fifths); `prof.py` / `prof3.py` / `rowp.py` (class runs along columns and rows: levels, post edges, legs); `seams.py`
  (plank seams and plank-end gaps); `proj.py` (orthographic block model of the layout at the sheet cameras, §2.5).
- **Colour:** `samp.py`, `samp2.py` (swatches; per-region medians with lit / shade quartiles).
- **Zooms:** `n_f34.png`, `n_r34.png`, `n_fs.png` (front + side), `n_rt.png` (rear + top), `z_expl.png`, `z_cu.png`,
  `z_keys.png`, `z_pal.png`; gridded `g_front.png`, `g_side.png`, `g_rear.png`, `g_top.png`; details `z_deck.png`,
  `z_deck2.png`, `z_f34under.png`, `z_r34under.png`.
- **On our renders:** `measure_render.py <render.png> [paper_hex]` prints bbox, W : H, W / K / Y shares, profile,
  width per height, fifths and class medians with these masks. Self-test on the sheet's own f34 cell
  (`selftest_f34.png`) reproduces §1.2 exactly (W : H 1.575, W 35.9 / K 58.2 / Y 5.9).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a modular timber structure. Hero budget 4000 tris, each part under 1000. The plan in
  §4.3 lands at about 3550–3700 (the rope coils are half of it).
- **Overall read (check this first).** A **raised rectangular timber pier on six tall square legs**, roughly twice as
  long as wide:
  - a **deck of chunky orange boards laid across the width**, their ends showing as a row of blocks along both long
    edges;
  - **six square posts** (4 corners + 1 at the middle of each long side) running from the ground up through the deck
    edge and standing about a third of the height above it, each with a lightly chamfered cap;
  - **two fat tan rope coils** round each post a little above the deck, and **thick twisted rope swags sagging low
    between the posts on three sides**: both long sides and the far (+Y) end. **The near (−Y) end is open**, the
    walk-on end;
  - under the deck, a **side beam** along each long side and **crossbeams** at the ends and middle, with a **bolt
    block** on each post's outer face(s) carrying a **big round brass bolt head**;
  - **dark brown legs** below the beams, **knee braces** from the corner legs up to the beams, and an **X brace** on one
    face (§3.4).
  - Hero shares (f34): W 35.9 % (lit tops, caps, plank ends), K 58.2 % (vertical faces, beams, legs), Y 5.9 % (rope
    and bolts).
- **Focal silhouettes, in order:**
  1. The long deck slab with its row of plank-end blocks, rising from the front-left to the back-right of the f34.
  2. The six posts standing above it, each wrapped by the bright rope coils, and the five low swags between them.
  3. The dark legs, the longest (front corner) leg reaching lowest; the beam band and bolt blocks under the deck edge.
- **Target (post centres): W 8.0 across × L 16.0 along (two bays of 8), post top z 8.3, deck top z 5.6.** Overall
  about **10.6 W (bolt heads) × 19.2 L (planks) × 8.3 H**. Tolerances: post spacing exact; deck top 5.6 ± 0.05 (a seam
  level, §2.1); H ± 0.3; overall W, L ± 0.4. Decision §8.1.
  - **How it was derived.**
    - **Length : width (post centres).** Inverting the six post tops of each three-quarter view as an orthographic
      grid (the length axis and the width axis as screen vectors, sin²e = tan θ1 · tan θ2): **f34 az ≈ 46°, e 16.5°,
      L / W 2.19; r34 az ≈ 50°, e 17.1°, L / W 2.09** (two bays against one width). The **top cell** gives post
      spacing 173 px along × 93.5 across: **1.85**. The front and side cells give 210 / 165.5 = 1.27 (they are drawn
      at different horizontal scales, §3.1). Adopted **2.0** (W 8, L 16): between the top and the three-quarters, on
      the kit's 8-stud grid.
    - **Height.** From the same fits, post height / width spacing is **1.05 (f34) and 1.00 (r34)** → H 8.0–8.4 at W
      8. The front and side cells give 0.84, but they stretch the width (§3.1). Adopted **8.3**; the block model then
      gives the f34 W : H 1.586 at (47, 16.5) against the sheet's 1.575 (`proj.py`).
    - **Levels** (front cell, the cleanest vertical scale; H = 139 px from the post top y 540 to the ground y 679):
      post top 1.000; coil band 0.777–0.885 (two coils centred 0.856 / 0.813); rope at mid-bay 0.719–0.777; **deck top
      0.673**; plank bottom 0.554; beam 0.547 → 0.396; bolt block 0.561 → 0.446 (bolt centre 0.493); legs 0.396 → 0.
      The f34 coils sit at 0.78 and the r34 coils at 0.74 of the post (their top faces show, so the cap reads high);
      the f34 bolt block sits at 0.34–0.52. Adopted: deck top **5.6** (0.675 H), coils at 0.79 / 0.83 H.
    - **Overall / post spacing** (ratios inside one cell, so the cells' horizontal scales cancel): length front 262 /
      210 = 1.248, top 214.7 / 173 = 1.24 → **19.2–20 L**; width side 218 / 165.5 = 1.317, top 126.5 / 93.5 = 1.35 →
      **10.5–10.8 W**.
  - **Why this size.**
    - **Against the character (5.5):** posts stand **2.7 above the deck** (waist height); the coils sit at knee to
      thigh height (0.9–1.3 above the deck); the swags sag to **0.25–0.4 above the deck** (ankle height: a low rope
      edge, not a handrail); the walkway between the post lines is 6.7 clear, room for three characters abreast; the
      posts are 1.3 square (chunky, as the notes ask); the boards are 1.8 wide and 0.85 thick.
    - **Against the water (top 1.0):** the deck top is **4.6 above the water** (about 1.4 m at 0.3 m per stud): a
      fixed pier on tall legs, as drawn. The legs stand on z 0; in a water tile they rise through the bed (0 → 0.2)
      and the see-through water (0.25 → 1.0).
    - **Against the shore:** the deck top **5.6 equals M043's lower lawn**, so the open end can abut that terrace
      flush. From a beach (sand 1.6–1.8) the step is 3.8–4.0, which needs the dock kit's "ramp end" (WorldModeling
      §13.2), a later piece (decision §8.3). A low variant is a parameter change (§8.4).
- **Build frame:** long axis **Y**, **the open (walk-on) end at −Y**, the roped end at +Y, +X right, ground z 0, centred
  on x 0 / y 0. Stage 2 puts the origin at the bbox bottom centre (it stays at 0, 0, 0 if the layout is symmetric;
  record any offset).

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | W (lit) | K (dark) | Y (rope + brass) | O |
| --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (15,113,512,419) | 44–492 × 124–408 (449 × 285) | **1.575** | 35.9 % | 58.2 | 5.9 | 1.7 |
| Rear three-quarter (514,113,1009,419) | 544–978 × 130–411 (435 × 282) | 1.543 | 30.7 | 63.2 | 6.1 | 1.6 |
| Front (15,492,296,730) | 27–288 × 540–679 (262 × 140) | 1.871 | 24.1 | 69.9 | 5.9 | 2.8 |
| Side (297,492,560,730) | 318–537 × 539–679 (220 × 141) | 1.560 | 22.2 | 72.2 | 5.6 | 2.6 |
| Rear (561,492,817,730) | 571–805 × 537–690 (235 × 154) | 1.526 | 16.3 | 79.6 | 4.1 | 2.2 |
| Top (818,492,1009,730) | 850–976 × 500–720 (127 × 221) | **0.575** (W : D) | 72.8 | 26.8 | 0.4 | 0.8 |

- Shares are of W + K + Y; O and B are left out. **Verifier tolerance:** W / K ±6 points (they split on value, so the
  studio light moves them); Y ±1.5 (rope thickness and coil size); W : H ±0.08 on f34, r34 and top; positions ±0.05.
- The top view's rope reads as W (the coils are seen edge-on from above: brown-gold C shapes round each cap).

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .46 | .73 | .74 | .66 | .67 | .69 | .72 | .76 | .90 | .89 | .82 | .84 | .92 | .99 | .86 | .82 | .80 | .79 | .87 | .87 | .66 |
| r34 | .67 | .89 | .89 | .77 | .77 | .78 | .82 | .92 | .99 | .85 | .81 | .81 | .90 | .81 | .72 | .69 | .67 | .65 | .74 | .73 | .48 |
| Front | .64 | .89 | .99 | .98 | .81 | .77 | .76 | .77 | .79 | .86 | .99 | .99 | .80 | .77 | .76 | .77 | .80 | .89 | .99 | .99 | .64 |
| Side | .62 | .88 | .99 | .99 | .91 | .82 | .79 | .77 | .76 | .75 | .74 | .74 | .75 | .77 | .79 | .81 | .87 | .99 | .99 | .87 | .64 |
| Rear | .68 | .90 | .99 | .99 | .97 | .84 | .82 | .82 | .84 | .89 | .97 | .97 | .84 | .82 | .82 | .84 | .90 | .99 | .99 | .90 | .68 |

- **f34:** six peaks = the six post caps (f .05–.10 far-left corner, .40 far-mid, .65 far-right, .15–.30 the near-front
  post under the deck line, .60 near-mid, .90–.95 near-right); between them the swags (.66–.80).
- **Front / side / rear:** posts at the peaks (.99), swags dipping to .74–.77 between, the deck ends at .64.

**Width per height** (fraction of W at h .05 → .95):

```
f34    .10 .30 .65 .93 .97 .94 .96 .64 .59 .08
r34    .10 .41 .69 .94 .97 .95 .97 .89 .61 .08
front  .90 .90 .90 .90 .96 1.0 .98 .90 .93 .90
side   .86 .86 .86 .86 .93 1.0 .98 .86 .91 .86
rear   .86 .87 .87 .87 .94 .94 1.0 .87 .94 .87
```

**Fifths** (bottom → top, % of each class): f34 W 0.2 / 14.0 / 43.6 / 35.5 / 6.7; K 8.4 / 29.6 / 34.1 / 20.0 / 7.8;
Y 0 / 5.4 / 25.8 / 50.9 / 17.9. Front W 0.1 / 0.8 / 33.7 / 43.8 / 21.6; Y 0 / 0 / 14.6 / 34.0 / 51.4.

**Level and size measurements** (sheet px; `prof.py`, `rowp.py`, `seams.py`):

| Item | Front cell (long side) | Side cell (end) | Rear cell (long side) | Top cell | f34 / r34 |
| --- | --- | --- | --- | --- | --- |
| Post centres | 52.5 / 158.5 / 262.5 (bays 106, 104) | 345.5 / 511 (165.5) | 600 / 688 / 777.5 (bays 88, 89.5) | x 867 / 960.5 (93.5); y 513 / 600 / 686 (87, 86) | see §1.1 |
| Post width | 23 (41–64, 147–170, 251–274 at the legs) | 23 | 24 | caps 22 | leg screen width 41–43 (√2 · post at 45°) → 1.25–1.35 |
| Post top → ground | 540 → 679 (139) | 540 → 679 | 540 → 688 (148; e ≈ 6°) | — | f34 front post 234 → 406 (172 incl. cap top); r34 235 → 409 |
| Rope coils | 559–562 and 565–568 (band 556–571) | 560–566 | 556–563 | C rings round each cap | f34 centre 0.78 H, r34 0.74 H |
| Rope at mid-bay | 571–579 (Ø 8 px); clear of the deck by 6.5 px | 574–580; clear by 3.5 px | 563–569 | — | |
| Deck top / plank bottom | 585.5 / 602 | 586 / 601 | plank tops 578–587 | — | |
| Beam (side or cross) | 603–624 | 604–624 | 587–622 (with the plank faces) | edge strips 16 px wide | |
| Bolt block / bolt | 601–617 / 608–613 (Ø 5–6) | 600–616 / 608–613 | 595–612 | ears 7–9 px outside the caps | |
| Deck ends | 27 / 288 (beam 34 / 279) | 319 / 537 (crossbeam 326 / 527) | 577 / 804 | 509 → 720 | |
| Planks | ends 27.5 px pitch (gaps at 91, 120, 147, 195, 224, 251) → about 9.5 over the deck | 5 ends between the posts (27 px) | 6 | **12 boards**, pitch 17.6, seam at the middle posts (y 597) | f34 about 10 along the near edge; exploded 9 + 1 |

### 1.3 Silhouette and composition per view

**Front three-quarter (`n_f34.png`, `z_deck.png`, `z_deck2.png`, `z_f34under.png`): governs.** Camera at +X, −Y
(**kit az ≈ 47°, e ≈ 16.5°**), strong perspective. The open −Y end at the left, the near long side (+X) running back to
the right.
- **Deck:** boards run **across the width** (far side to near side, upper-left to lower-right). Their ends form a row of
  chunky blocks along the near edge, about 4 per bay; the end board at the −Y end shows its long side face. Each board
  has softened, lighter top edges; values vary a little board to board. A few boards seem to break near mid-width; the
  top view and the exploded draw full-width boards (§3.3).
- **Posts:** six caps above the deck (far row: left corner, mid, right corner; near row: front corner, mid, right
  corner). Each cap is a lightly chamfered square with a small dark peg dot; each post shows a faint vertical split line.
- **Rope:** two fat coils round each post at about a third of the way up from the deck; swags sag low between: far
  side (both bays), the +Y end, near side (both bays). **None across the −Y end.**
- **Under the deck:** the near side beam with bolt blocks at the front corner and near-mid posts (big round bolt
  heads), the short-end beam with a block at the front corner, dark legs (the front-corner leg reaches lowest, y 406),
  more legs behind in shade. No brace reads clearly from this camera.

**Rear three-quarter (`n_r34.png`, `z_r34under.png`).** Camera at −X, −Y (**kit az ≈ −41°, e ≈ 17°**): the near long
side is −X, the open −Y end at the front-right, the roped +Y end at the back-left. The +Y swag carries **a knot at
mid-span** (sheet ≈ (643, 198)). Under the deck: the −X side's three legs, diagonals between the front-corner and
right legs on the −Y end (an **X brace**, z_r34under (790–920, 330–380)), bolt blocks on both outer faces of the
front-corner post. It does not show the +Y end's underside.

**Front (`n_fs.png`, `g_front.png`).** The +X long side, near level (e ≈ 2°): three posts, two swags, the plank-end row
(about 3 ends per bay between the posts), the beam band with three bolt blocks, three dark legs and **two knee braces
from the corner legs inward to the beam** (lower end at the leg's inner face, 0.12 H; upper end on the beam's underside
0.3 H in from the leg; about 42°). The middle leg has none. Beam and plank ends overhang the corner posts.

**Side (`n_fs.png`, `g_side.png`).** The +Y end (it carries the rope): two posts, one deep swag with a **knot loop at
the left post**, five plank ends (§3.3), the crossbeam band with two bolt blocks, two legs with **knee braces**.

**Rear (`n_rt.png`, `g_rear.png`).** A long side (three posts above the deck) with **one big X brace between the corner
legs and no middle leg**, a bolt at the crossing. It contradicts both three-quarters (§3.4).

**Top (`n_rt.png`, `g_top.png`).** A tall rectangle (W : D 0.575): **12 boards** across the width, six chamfered caps
on the long edges with rope C rings round them, bolt-block ears outside each cap, beam strips along both long edges
(§3.3).

### 1.4 Parts (Exploded (15,739,717,1260), `z_expl.png`; key parts (15,1269,645,1484), `z_keys.png`)

A near-isometric view from the front-left. **The hero governs every size**; the parts give shapes and boundaries.

| Part | Box (sheet px) | Notes |
| --- | --- | --- |
| Mooring Post (4 drawn) | leftmost (95,837,141,947); key (40,1300,95,1425) | A square post, **two rope coils at 0.25–0.4 from its top**, chamfered cap with a peg dot. Key part H / W ≈ 4.3, about the post from the beam bottom up (3.3–4.3) |
| Pile (2 drawn, unlabelled) | (88,967,145,1140), (601,960,648,1100) | A tall square post with a dowel hole on top, two holes near the foot, a **bolt block on one face near the top with a long bolt pin** |
| Deck planks (9 + 1) | (161,853,518,973) | Full-width boards, **L : W ≈ 3.4 on screen**, chunky, lit tops `#E69447`, sides `#8D4115` |
| Beam (2) | (198,930,518,1113) | Long square beams with dark peg dots; the two side beams |
| Brace | (411,1060,511,1167) | A short square board, ends cut at the joint angles |
| Crossbeam | (218,1120,345,1240) | A beam with a short post stub at one end and two bolt blocks |
| Bolt blocks (4 + pins) | (38,990,85,1040), (168,1010,221,1100), (645,1000,681,1040) | Small cubes, a round brass bolt head on one face, a pin behind |
| Rope Segment | (155,777,488,833); key (500,1340,620,1405) | A thick twisted rope, sagging, **round knob ends** |

- **Plank cross-section close-up:** a chunky board, about 2 : 1 width to thickness, softened top edges, a lighter top
  `#E49952` and darker side `#9A4F23`. The top looks split by a faint line along its length (two strips); see §3.3.
- **Junction close-up:** the post rises through the deck edge; boards butt against it on both sides; below the deck
  the bolt block sits on the post's outer face with a **large round brass bolt head** (about 0.4 of the block's width);
  two rope coils wrap the post, the swag leaves from between them.
- **Underside close-up:** plank bottoms (dark, `#673B21` in shade), the side beam along the edge, a bolt block, and a
  **knee brace** from the leg up to the beam.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (long axis Y, open end −Y, +X right, ground z 0). Builder constants (decision §8.4): `W = 8.0`
(post centres across), `BAY = 8.0` (two bays), `POST = 1.3`, `DECK_TOP = 5.6`, `PLANK_T = 0.85`, `BEAM_D = 1.3`,
`POST_TOP = 8.3`.

### 2.1 The seam contract (binding; record it in the builder docstring and the export notes)

| Item | Value | Notes |
| --- | --- | --- |
| Ground / leg feet | **z 0**, flat leg bottoms | the water tiles' bed bottom; the legs pass through the bed (0 → 0.2) and the water (0.25 → 1.0) |
| Deck top (walk surface) | **z 5.6**, flat, boards ± 0.02 | 4.6 above the water top 1.0; flush with M043's lower lawn |
| Open end | **y −9.6**, the end board's outer face; no rope, no brace above the deck | the walk-on seam: a terrace at 5.6, a later ramp end, or another dock bay |
| Roped end | y +9.6 | rope across, knee braces |
| Sides | boards to x ±5.1; bolt heads to x ±5.3 | nothing past ±5.4 |
| Post centres | x ±4.0; y −8, 0, +8 | |

- **With water tiles (M041 / M034 / M032):** stand the legs on the plate (z 0) anywhere in open water. Nothing of the
  dock touches the water mesh; the water tile's own foam stays where it is. The legs read through the see-through water
  as the sheet's dark legs.
- **With M043 (lower lawn 5.6):** put the open end's board face against M043's lower terrace front: the deck meets the
  lawn flush.
- **With a beach (sand 1.6–1.8):** the deck is 3.8–4.0 above the sand: a dock-kit ramp end / stairs piece is needed
  (decision §8.3). The open end's legs may stand on the sand (sunk to z 0 under it).

### 2.2 Posts, beams, crossbeams

| Piece | Position | Size | Notes |
| --- | --- | --- | --- |
| Posts P1–P6 | centres (±4.0, −8 / 0 / +8) | 1.3 × 1.3, z 0 → 8.3 | cap chamfer 0.12 on the four top edges; optional shallow vertical V groove (0.05 deep) down the two outward faces (the sheet's split line) |
| Leg region | each post below z 3.45 | | colour only (§5); one shell per post (decision §8.5) |
| Side beams B±X | x ±2.45 … ±3.35 (outer face on the post inner faces), y −9.15 … +9.15 | 0.9 wide × 1.3 deep, z 3.45 → 4.75 | ends 0.5 past the corner posts' outer faces (front cell 7 px); 0.04 edge chamfer at most |
| Crossbeams C−Y, C0, C+Y | y −8 / 0 / +8 (± 0.45), x −2.45 … +2.45 between the side beams | 0.9 × 1.3, z 3.45 → 4.75 | end faces sunk 0.02 into the side beams |
| Bolt blocks | each post's outer long face (x ±4.65), and the end face (y ±8.65) of the four corner posts: 10 | 1.3 along the face × 1.0 tall × 0.35 proud, z 3.55 → 4.55 | sunk 0.02 into the post face |
| Bolt heads | centre of each block face, z 4.05; plus one at the X-brace crossing: 11 | round, Ø 0.55, 0.22 proud, a low dome (+0.06) | 8 sides (the sheet's heads are round, the junction close-up's is faceted); sunk 0.03 into the block |

### 2.3 Deck

- **10 boards** across the width (decision §8.2), pitch 1.92 over y −9.6 … +9.6, each **1.82 wide** (0.10 gaps), **0.85
  thick** (z 4.75 → 5.6), x −5.1 … +5.1. Seams at y 0, ±1.92, ±3.84, ±5.76, ±7.68 (a seam at the middle posts, as the
  top view draws).
- **At the posts:** the two boards on each side of a post row (the ones whose y range meets the post's ±0.65) end at
  the post's inner face (x ±3.33) on that side. Nothing of the board continues outside the post (the bolt block and the
  cap ears fill the edge in the top view). That is 2 boards × 3 rows shortened at both ends (the post rows have posts on
  both sides).
- **Each board** is a box with a **0.06 chamfer on its four top edges** (WorldModeling §13.1: restrained, one segment)
  and a per-board height jitter of ±0.02 and yaw ±0.4° (no gaps opening). No grain, no groove.
- **Underside:** boards sit on the side beams and crossbeams, sunk 0.02.

### 2.4 Braces

| Brace | From | To | Section | Sheet evidence |
| --- | --- | --- | --- | --- |
| Knee braces, +X and −X sides (4) | corner leg inner face (y ±7.35) at z 1.1 | side-beam underside (z 3.45) at y ±4.6 | 0.6 (in the brace's plane) × 0.45, centred in x on ±3.35 (straddling the leg / beam line, so the lower end meets the leg face and the upper end the beam underside, ≥ 0.2 of overlap each) | front cell (42°, lower end 0.13 H) |
| Knee braces, +Y end (2) | corner leg inner face (x ±3.35) at z 1.1 | C+Y underside at x ±0.9 | 0.6 × 0.45, y +7.6 … +8.05 | side cell |
| X brace, −Y end (2 boards) | each corner leg's inner face near its foot (z 0.6) | the opposite leg's inner face under C−Y (z 3.35) | 0.6 × 0.35; board A y −7.75 … −8.1, board B y −8.1 … −8.45 (stacked, touching at the crossing; both inside the legs' y range −7.35 … −8.65) | r34 −Y end; rear cell's X (§3.4) |

- Ends are cut to the faces they meet (vertical against a leg, horizontal against a beam) and sunk 0.02. A bolt head
  on board B's outer face at the crossing (x 0).

### 2.5 Rope

| Piece | Path | Size | Notes |
| --- | --- | --- | --- |
| Coils (2 per post, 12) | rounded square round the post, centreline 0.86 from the post axis, corner radius 0.3; centres **z 6.52 and 6.92** | tube Ø 0.42 | inner surface sunk 0.02 into the post faces; the two coils touch |
| Swags (5) | +X side y −8 → 0 and 0 → +8 at x +4.0; −X the same; +Y end x −4 → +4 at y +8 | Ø 0.42 | ends start inside the coils (sunk ≥ 0.15) at z 6.72; **low point z 6.15 on the long sides, 6.05 on the +Y end** (rope bottom 0.34 / 0.24 above the deck) |
| Knot (1) | on the +Y swag beside the +X corner post (the side cell's left post) | a lumpy loop Ø 0.8 × 0.5 | touches the swag and the coil |

- **Low-poly twisted rope:** 6-sided tube (5 if over budget), rings every 0.6 along a swag; **rotate each ring 30°
  (half a side)** so the flat facets spiral like the sheet's twist; no fibres (WorldModeling §13.2). Sag as a catenary
  sampled at the ring points.
- **Rope part (`TimberDockRope`):** one long-side swag with the key part's **round knob ends** (Ø 0.6, 8 sides); in the
  hero the ends tuck into the coils, so no knobs show.

### 2.6 Expected extents and screen checks

- **Extents (build frame):** X −5.3 … +5.3 (bolt heads; boards ±5.1); Y −9.6 … +9.6 (boards; the X brace's bolt at about −8.7); Z 0 …
  8.3. Bbox ≈ 10.6 × 19.2 × 8.3.
- **Self-consistency (`proj.py`, an orthographic block model):** f34 (47, 16.5) W : H 1.586 (sheet 1.575); top W : D
  0.552 (0.575). The long-side and end orthos give 2.31 and 1.23 (sheet 1.871 and 1.560): the sheet's ortho cells are
  drawn at their own scales (§3.1).
- **Checks on the renders** (floor hidden, `measure_render.py`, the studio's paper colour as the second argument):
  - **f34_sheet (47, 16.5)** (probe az 40 / 47 / 54 × e 12 / 16.5 / 21, keep the best):
    - W : H 1.50–1.65 (sheet 1.575);
    - shares W 35.9 ± 6, K 58.2 ± 6, Y 5.9 ± 1.5;
    - Y fifths within ±8 of §1.2 (the rope sits in the upper middle: 0 / 5.4 / 25.8 / 50.9 / 17.9);
    - top profile within ±0.08 (mean ≤ 0.05) of §1.2: six post peaks with the swags dipping between;
    - read: the open end at the left, boards across the width with their ends as blocks along the near edge, five
      swags (none across the near end), dark legs.
  - **r34_sheet (−41, 17)** (probe az −34 / −41 / −48): W : H 1.47–1.62 (1.543); Y 6.1 ± 1.5; the knot on the back
    (+Y) swag.
  - **front_sheet (90, 3)** (+X side): three posts, two swags, about 3 plank ends between posts, three bolt blocks, two
    knee braces from the corner legs; W : H **≈ 2.3** against the sheet's 1.871 is the recorded ortho-cell miss (§3.1).
  - **side_sheet (180, 3)** (+Y end): two posts, one swag with the knot at the +X post (on the left from +Y), two knee
    braces; W : H ≈ 1.23 against 1.560 (recorded).
  - **rear_sheet (−90, 6)** (−X side): judged against the front cell's layout, not the rear cell's X (§3.4).
  - **top (0, 89):** W : D 0.53–0.60 (0.575); W 72.8 ± 6; ten boards across the width, six caps with their coils, bolt
    ears outside.

## 3. View conflicts and resolutions

### 3.1 Proportions: the three-quarters (L / W 2.1–2.2) vs top (1.85) vs front and side (1.27)

- **Evidence:** §1.1. The front cell draws the length at 13.1 px per stud and the side cell the width at 20.7 px per
  stud (at W 8, L 16), with the same height (139 px) in both: each ortho cell was scaled to fill its box.
- **Resolution (decision §8.1):** the three-quarters and the top govern: **L / W 2.0** (W 8, L 16), H 8.3. The front
  and side cells are judged on content and level fractions (which agree), not on W : H. Record W : H misses of about
  +0.4 (front) and −0.33 (side).

### 3.2 The rear three-quarter shows the same open end as the front three-quarter

- **Evidence:** in both three-quarters the nearest short end has no rope and the far one has a swag; so the r34 is a
  camera at −X, −Y, not from behind.
- **Resolution:** open end −Y, roped end +Y; the r34 camera is (−41, 17). The roped end's underside is seen only in the
  side cell.

### 3.3 Plank count and layout: top 12, f34 / front / exploded about 10; boards that seem to break mid-width

- **Evidence:** top cell 12 seams-to-seams at 17.6 px (1.63 at its scale); front plank-end pitch 27.5 px (2.1 at its
  scale) → 9.5 over the deck; f34 about 4 per bay plus the overhangs → 10; exploded 9 + 1. The f34 shows a few boards
  apparently broken near mid-width; the top and the exploded draw full-width boards. The plank cross-section shows a
  faint line along the top. The side cell shows 5 plank ends on the end face, where a single board's side should show.
  The top cell draws the boards between two lengthwise strips (the beams seen beyond the board ends).
- **Resolution (decision §8.2):** **10 full-width boards, 1.82 wide, a seam at the middle posts**; no butt joints and
  no top groove (a groove would read as 20 boards from above). The side cell's plank ends and the top cell's beam strips
  are drawing conventions. **Alternative:** 12 boards at 1.6 (top cell; narrower ends along the edge than the f34 and
  front show).

### 3.4 Bracing: front (knee braces) vs rear (one X, no middle leg) vs the three-quarters (middle legs on both sides; an X on the −Y end in the r34)

- **Evidence:** front cell: knee braces from the corner legs, a middle leg. Rear cell: a single X between the corner
  legs, **no middle leg**, a bolt at the crossing. f34: a middle leg on the near (+X) side; r34: a middle leg on the near
  (−X) side and diagonals crossing on the −Y end. Side cell: knee braces.
- **Resolution (decision §8.6):** six legs (three per long side); **knee braces from the corner legs on both long sides
  and the +Y end; an X brace on the −Y end** (the r34 places it there; the rear cell's X with its crossing bolt is
  moved to it). The rear cell's missing middle leg is not followed. **Alternative:** the rear cell literally: an X on
  the −X side and no −X middle leg (contradicts the r34 and leaves the deck's middle unsupported on one side).

### 3.5 Mooring post and pile: two pieces (exploded) vs one continuous post (every assembled view)

- **Evidence:** the exploded drops a mooring post onto a separate pile; the assembled views show one straight post from
  the ground to the cap, darker below the beams.
- **Resolution (decision §8.5):** **one closed post per position**, ground → cap, with the leg darkening done by colour
  below z 3.45. No hidden stacked faces. **Alternative:** a pile (z 0 → 4.75) and a mooring post (4.75 → 8.3) as two
  shells meeting at the plank bottom.

### 3.6 Leg colour: dark legs (assembled) vs orange piles (exploded)

- **Evidence:** assembled legs `#764521` (front), `#62371C` (f34), `#683819` (r34) against post faces `#8D4212`; the
  exploded pile is `#984410`, the same orange as the mooring post `#883E12`.
- **Resolution:** the hero's legs are darker **by position** (below the beam bottom: weathered, wet, in the deck's
  shadow), blended over 0.6 under the beam (§5.5). The parts shot keeps the same paint as the hero (the pile region of
  the post part is dark too). Recorded.

### 3.7 Knot: mid-span (r34) vs at the post (side cell)

- **Resolution:** **at the +X corner post on the +Y swag** (the side cell; a knot by a post is where a rope would be
  tied). The r34's mid-span knot is recorded as a drawing difference.

### 3.8 "Simple solid color blocks, subtle value variation only (no wood grain texture, no noise)" against the user's blended-colour rule

- The user's rule wins quietly: per-board and per-member tint (±0.03, measured board-to-board value sd 0.014 on the top
  view), a broad lighter field over the deck, lighter post caps and darker legs by position. Whole faces only; no
  per-triangle confetti, no grain decals.

### 3.9 Palette swatches against the renders

- The wood swatch `#B56734` (24°, 0.71, 0.71) sits between the rendered tops (`#E19044`) and vertical faces
  (`#8D4212`–`#A95015`): it is the framing tone (§5.4).
- The tan swatch `#DEBF93` (35°, 0.34) is duller than the rendered rope `#F8D088` (39°, 0.45, 0.97): calibrate to the
  rope.
- **Grey `#AEB0B4`, green `#87A15A` and blue `#35A0C8` colour nothing on the sheet** (the bolts are drawn brass; there
  is no moss, grass or water). Unused (decision §8.8).

### 3.10 Cast shadow

- The sheet's ground shadows are pale blue-grey (B). Render every `*_sheet` view with the studio floor hidden.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

All pieces are explicit low-poly solids built from vertex lists (boxes, chamfered boxes, prisms, tubes). **No
booleans are needed**: every piece is its own closed shell, touching or sunk 0.02 into what carries it. Reuse M012's
board helpers only if they fit; don't edit other models' builders.

1. `post(i)` → each of the six posts: a chamfered-cap prism (optional V grooves), its bolt block(s) and bolt head(s), its
   two coils. **Part `TimberDockPost`** = the +X / −Y corner post with both blocks and bolts and its coils (key
   "Mooring Post"), compared with the key part and the junction close-up.
2. `deck()` → the ten boards (§2.3). **Part `TimberDockDeck`** (the exploded deck group), compared with the exploded
   deck and the plank cross-section.
3. `beam(side)` → a side beam. **Part `TimberDockBeam`** (exploded "Beam").
4. `crossbeam(y)` → a crossbeam. **Part `TimberDockCrossbeam`** (exploded "Crossbeam"; the part may carry one bolt block
   to echo the drawing, not the hero's).
5. `brace(a, b)` → a board between two contact faces with cut ends; `xbrace()` → the two stacked boards and the crossing
   bolt. **Part `TimberDockBrace`** = one knee brace.
6. `rope(path)` → a twisted tube along a sampled path; `coil(post)`; `knot()`. **Part `TimberDockRope`** = one long-side
   swag with knob ends (key "Rope Segment").
7. **Hero `TimberDock`** = 6 posts (with blocks, bolts, coils) + 10 boards + 2 side beams + 3 crossbeams + 6 knee
   braces + the X brace + 5 swags + the knot.
   - Each piece a closed shell in one object; no unions.
   - `M.fix_bowties`; origin at the bbox bottom centre; transforms applied.
8. **Parts shot** (az −35, e 25), laid out like the exploded: deck above the beams, posts at the corners, brace and
   crossbeam in front, rope above.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a raised timber pier on six dark square legs, chunky boards across the width, six posts with fat
   rope coils and five low swags (open near end), bolt blocks with brass bolts under the deck edge.
2. **f34_sheet, r34_sheet, front_sheet, side_sheet, top** per §2.6.
3. **Level check (numbers):** leg feet z 0.00; side beams and crossbeams 3.45 → 4.75; deck top 5.60 ± 0.02 on every
   board; coils 6.52 / 6.92; swag low points 6.15 / 6.05; post tops 8.30.
4. **Underside extra** `under_cu (35, −30)` against the underside close-up: board bottoms on the beams, the knee brace
   meeting leg and beam, the bolt block; nothing floating.
5. **Junction extra** `junc_cu (60, 20)` framed on the +X / −Y corner post: the board ends against the post, the coils
   snug, the swag leaving from between the coils, the bolt block and bolt under the deck edge.
6. **Scale shot:** 5.5-stud character markers on the deck at y 0 and on the ground beside a leg.
7. **Shore shot** (if M041 or M043 are in the kit file): the dock standing in M041's plate (legs through the water) and
   its open end against M043's 5.6 lawn, from (45, 20).

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Posts (prism + 0.12 cap chamfer; + V grooves) | 6 | 28 (44 with grooves) | 170–260 |
| Bolt blocks (box, 0.04 chamfer optional) | 10 | 12 (28) | 120–280 |
| Bolt heads (8-sided, domed) | 11 | 32 | 350 |
| Boards (chamfered top edges) | 10 | 20 | 200 |
| Side beams | 2 | 12–28 | 24–56 |
| Crossbeams | 3 | 12–28 | 36–84 |
| Knee braces | 6 | 12 | 72 |
| X brace boards | 2 | 12 | 24 |
| Coils (6 sides × 12 segments) | 12 | 144 | 1730 |
| Swags (6 sides × 14 rings) | 5 | 170 | 850 |
| Knot | 1 | 60 | 60 |
| **Hero** | | | **about 3540–3970**, plan ≈ 3600 (limit 4000) |
| Parts: Post / Deck / Beam / Crossbeam / Brace / Rope | | | ≈ 430 / 200 / 28 / 28–60 / 12 / 230 (limit 1000) |

- **The coils are the cost.** If the hero is over 3900: coils to 5 sides × 10 segments (100 tris, −530), then the swags
  to 5 sides (−140), then bolt heads to 6 sides (−90). Never drop a coil (two per post is a defining look), a swag, a
  bolt or a board.

### 4.4 Shape targets (binding; check with `M.audit` and own bmesh code)

| Target | Posts | Boards | Beams / braces | Rope | Bolts |
| --- | --- | --- | --- | --- | --- |
| Section | square 1.3; faces planar | 1.82 × 0.85 boxes; tops flat | square-ish boxes | round-ish 5–6 sides, spiral facets | round 8 sides |
| Edges | cap chamfer 0.10–0.14; sides sharp | top chamfer 0.05–0.07; bottoms sharp | ≤ 0.04 | — | dome ≤ 0.08 |
| Not | no rounded tops, no tapering, no octagonal caps (W08) | no gaps > 0.12, no grain, no warping > 0.02 | no floating braces | **not thin**: Ø 0.40–0.45; no fibres; no ropes through the deck | not flat discs |

- **Chunky, not skinny:** board W : T 2.0–2.3; post W ≥ 0.15 of its height; rope Ø ≥ 0.05 of the post height.

### 4.5 Stages 2 and 3

- **Stage 2:** every shell closed and manifold; zero non-manifold edges and verts (`nonmanifold_verts` 0), boundary,
  wire and loose elements; no zero-area faces or n-gons (the coils' rounded-square rings and the dome fans are the
  places to check); normals outward; **0 winding errors** in `build()`'s problems list (STAGES "Consistent winding",
  044's wedge back face); no corners under 5° on visible faces; the deck top planar at 5.60 ± 0.02.
- **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 32 × 32 box inside each, sd ≤ 1.4)

| Swatch | Box | Hex | HSV | Use |
| --- | --- | --- | --- | --- |
| 1 Orange wood | (714,22,746,52) | `#B56734` | 24°, 0.71, 0.71 | start for `m048_wood_deep` (framing) |
| 2 Tan | (776,22,808,52) | `#DEBF93` | 35°, 0.34, 0.87 | hue reference for rope (the rendered rope is brighter) |
| 3 Grey | (838,22,870,52) | `#AEB0B4` | 220°, 0.03, 0.71 | **unused** (§3.9) |
| 4 Green | (900,22,932,52) | `#87A15A` | 82°, 0.44, 0.63 | **unused** |
| 5 Blue | (962,22,994,52) | `#35A0C8` | 196°, 0.74, 0.78 | **unused** (no water drawn) |

### 5.2 Rendered regions (`samp.py`, `samp2.py`; median / lit quartile / shade quartile)

| Region | f34 / r34 | front / side / rear | top | exploded / keys / close-ups |
| --- | --- | --- | --- | --- |
| Board tops | **`#DF8C3E`** (29°, .72, .87) / `#EA9A4A`; back `#D67C35`; r34 `#E19145` | (rear tops show at 578–587) | `#CB7334` (25°, .74, .80); board-to-board value sd 0.014, range 0.04 | expl `#E69447`; key plank `#DD8F48`; junction `#E49346`; cross-section top `#E49952` |
| Board ends / sides (vertical) | | front **`#A95015`** (24°, .88, .66) / lit `#DC8740`; side `#A34F1B`; rear `#944617` | | expl sides `#8D4115`; cross-section side `#9A4F23` |
| Post faces above the deck | | front **`#8D4212`** (23°, .87, .55); middle post `#8A4113` | | junction `#8C4011`; expl post `#883E12`; key post `#7D3B14` |
| Post caps (above the coils) | f34 lit cap `#D07C4A` | front `#A1480F` (+20 over the face below the coils) | **`#E68D42`** (27°, .71, .90), lighter than the board tops beside them | |
| Beams / crossbeams (faces) | | front `#89451B` (23°, .80, .54); side `#84451F`; rear `#87461E` | edge strips `#B46329` | expl beam `#83411C`; crossbeam `#8C4014` |
| Bolt blocks | | front `#A14C14` | | |
| Legs (below the beams) | f34 **`#62371C`** (23°, .71, .38); r34 `#683819` | front **`#764521`** (25°, .72, .46); side `#744323`; rear `#7C4822` | | expl pile `#984410` (orange, §3.6) |
| Braces | | front knee `#7E3C17` (22°, .82, .49); rear X `#88431A` | | expl brace `#C87333` (lit) |
| Board bottoms (shade) | | | | underside `#673B21` |
| Rope | f34 swags **`#F8D07C`** (41°, .50, .97) / `#FDEB9D` / shade `#E6AF58` | front swag `#F8D088` (39°, .45, .97) / `#FCEAB2` / `#EEBA67`; coils `#F3CF82` / shade `#DDA24A`; side `#F9D484` | | expl `#F8D184`; key `#F8CF7F`; junction `#FBE199` |
| Brass bolt heads | f34 `#FAD584` (41°, .47, .98) | front `#F7E0A8` (43°, .32, .97) / shade `#F0C087` | | junction `#FADA96`; expl `#F8D38C` |

### 5.3 How the colour works

**Wood: one warm orange timber family, by role and position, never by facing.**
- The sheet's lit tops (29°, sat 0.70) against its vertical faces (23°, sat 0.87, value 0.55–0.66) is mostly the light.
  The studio's light will darken the vertical faces without reddening them: a **hue miss of 2–4° on the vertical faces
  is a known miss**, not a key error.
- **Role:** boards `m048_wood`; framing (posts, beams, crossbeams, bolt blocks) `m048_wood_deep`, about 0.83 of the
  boards' value (the front cell's post faces `#8D4212` and beams `#89451B` against its board ends `#A95015`, same
  facing).
- **Position:**
  - **post caps lighter:** the top 0.6 of each post blends toward `m048_wood_light` (the top view's caps `#E68D42`
    against the boards `#CB7334`; the front's cap `#A1480F` against `#8D4212` below the coils);
  - **legs darker:** below the beam bottom (z 3.45) the posts blend `wood_deep` → `m048_wood_dark` over 0.6 (3 steps),
    full dark below z 2.85 (front legs `#764521` against post `#8D4212`: 0.84 in value and 0.15 less saturated);
  - **braces** 60 % `wood_dark` (they sit in the leg zone: `#7E3C17` / `#88431A`).
- **Boards:** per-board tint ±0.03 (the sheet's boards differ by 0.014 sd in value); one broad lighter field across the
  deck (the f34's front-left boards and the r34's middle boards are lighter) at 15 % `wood_light`; two or three boards a
  step deeper (15 % `wood_deep`).
- **The old W08 dock rendered "slightly red"** (its goals): keep the board key's hue at 26–29° and R − G ≤ 95; check the
  f34 board-top median hue ≥ 26°.

**Rope.** One warm golden tan, brighter and more yellow than the swatch: `m048_rope` on the outer strands and
`m048_rope_dark` (the coils' shade `#DDA24A`) at 45 % on the groove strand, chosen **by the strand's index round the
tube (its role in the twist), never by the face's normal**. The rope reads clearly lighter than every wood face.

**Brass.** Pale gold bolt heads `m048_brass`, a touch paler and less saturated than the rope, with a metal finish so
they catch the light.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are medians of unshadowed rendered regions, not swatches. `K.sample` kinds: `"brown"` for the woods
(or `"vivid"` for the board tops if `"brown"` drops sat > 0.7), `"vivid"` for rope and brass.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m048_wood` | **`#E19044`** board tops (f34 `#DF8C3E`, r34 `#E19145`, junction `#E49346`, exploded `#E69447`, key `#DD8F48`) | 26–30°, 0.66–0.74, R > G > B | boards; default | rough 0.85, metal 0, low spec |
| `m048_wood_light` | `#EDA052` (lit tops `#EA9A4A`, `#EEA053`; top-view caps `#E68D42` +) | 27–31°, 0.62–0.70 | post caps and the top 0.6 of each post at 40–60 %; the deck's lighter field at 15 % | rough 0.85 |
| `m048_wood_deep` | `#B56734` (swatch 1); check the front_sheet post faces near `#8D4212` and beams near `#89451B` (± 15, light) | 22–26°, 0.70–0.80 | posts, beams, crossbeams, bolt blocks; deeper boards at 15 % | rough 0.85 |
| `m048_wood_dark` | `#946039` start; check the front_sheet legs near `#764521` and their value ≈ 0.84 of the post faces above | 23–27°, 0.58–0.68 | posts below z 3.45 (blended), braces at 60 % | rough 0.9 |
| `m048_rope` | **`#F8D088`** (front swag; f34 `#F8D07C`, exploded `#F8D184`, key `#F8CF7F`) | 38–42°, 0.42–0.52, value ≥ 0.92 | swags, coils, knot, knob ends | rough 0.95, low spec |
| `m048_rope_dark` | `#DDA24A` (coil shade; f34 shade `#E6AF58`) | 36–40°, 0.60–0.68 | the groove strand at 45 % | rough 0.95, low spec |
| `m048_brass` | `#F7D894` (front `#F7E0A8`, f34 `#FAD584`, junction `#FADA96`) | 40–44°, 0.35–0.47 | bolt heads | metal 0.5, rough 0.4 |

**Calibration warnings:**
- **Board tops:** f34 W-class median within 12 of `#DF8C3E`, hue 26–30°, sat ≥ 0.62. Not red (hue < 25°), not brown
  (value < 0.8), not yellow-tan (hue > 32°).
- **Vertical faces:** front_sheet board ends within 18 of `#A95015` and post faces within 18 of `#8D4212`; the order
  board ends > post faces > legs must hold in value.
- **Legs:** visibly darker than the posts above in every assembled view (the sheet's defining contrast); f34 leg median
  within 15 of `#62371C`–`#764521`.
- **Rope:** f34 Y median within 12 of `#F8D07C`, hue 38–42°, clearly lighter than any wood. Not white-cream, not
  orange.
- **Brass:** reads as gold, not grey (the grey swatch is unused), not the same flat colour as the rope (the metal finish
  separates them).

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Boards:** `wood` base; per-board tint ±0.03; `wood_light` by a broad noise field (scale ≈ 0.12, one or two patches
  across the deck) at 15 %; 2–3 boards 15 % `wood_deep`. **Hard edges** only between boards (each board is its own
  shell).
- **Posts:** `wood_deep` base; `wood_light` by height over the top 0.6 (rising to 60 % on the cap faces); `wood_dark` by
  height below z 3.45, 3 steps to full at z 2.85. The bolt block takes the post's colour at its height (`wood_deep`).
- **Beams, crossbeams:** `wood_deep`; per-member tint ±0.03.
- **Braces:** 60 % `wood_dark` mixed into `wood_deep`.
- **Rope:** strand roles (§5.3); per-swag tint ±0.02.
- **Hard edges only** where materials meet: rope | post, brass | block, board | post.

### 5.6 Texture (Tint) and finish

- **Tint:** boards amp 0.03 per board (whole board) plus 0.02 at scale 0.3; framing 0.03 per member; legs 0.03; rope
  0.02 per piece; brass none. **Never per-triangle confetti**, no grain stripes.
- **Finish:** wood rough 0.85–0.9, metal 0, low spec; rope rough 0.95, low spec; brass metal 0.5, rough 0.4. No
  emission anywhere.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Shares** per §2.6; **colours** per the §5.4 warnings, in f34_sheet, front_sheet and top. `K.check` facing
  correlation < 0.5 on every wood material (the boards' role split must not correlate with facing: their tops and ends
  are one key).

## 6. Joins and contact (no floating dressing)

- **Posts:** feet flat on z 0 (the leg region of each post is the same shell).
- **Beams on posts:** each side beam's outer face sunk 0.02 into the three posts' inner faces; its underside free.
- **Crossbeams on beams:** end faces sunk 0.02 into the side beams' inner faces; C−Y and C+Y also touch the corner
  posts' inner faces where they meet.
- **Boards on the frame:** every board's underside sunk 0.02 into the side beams (and the crossbeam under it, if any);
  boards meet posts at the post faces with ≤ 0.02 gap; board-to-board gaps 0.10 (no overlaps).
- **Braces:** each end face flush with (sunk 0.02 into) the leg face or beam underside it meets; X boards touch each
  other at the crossing; the crossing bolt sunk 0.03 into board B.
- **Bolt blocks and bolts:** blocks sunk 0.02 into the post faces; bolt heads sunk 0.03 into the blocks.
- **Rope:** coils' inner surfaces within 0.02 of the post faces (sunk 0.02); the two coils touch; swag ends sunk ≥ 0.15
  into the coils; the knot touches the swag and the coil. **No rope passes through a board or a post.**
- **Chain to ground:** boards → beams → posts → ground; coils → posts; swags → coils; blocks → posts; bolts → blocks;
  braces → legs and beams.
- **Count floating shells before reporting** (STAGES; 035 and 036 failed round 1 on this): **0**. A shell floats if its
  nearest distance to every other shell and the ground is > 0.03, or if it doesn't chain to the ground.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0 (dome fans, coil rings).
- **Winding:** 0 errors per shell (box builders are where a reversed face list slips in; 044's wedge back face).

## 7. Water, lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** sunlit timber, tan rope and brass bolts on white paper. **No water, foam, glow, light,
sparkle, dust, smoke or VFX callout** ("No additional variants, props or environment elements on this page").

- **Water and foam: none in the model.** The legs stand on z 0; placed in a water tile, the tile's water (0.25 → 1.0)
  surrounds them. No `*water*` key, no foam mesh, no `water_foam` sockets (not drawn). **Not recommended:** foam rings
  round the legs (M041's water tile already carries its own foam; a dock-specific ring would duplicate it).
- **Stage 5 (lighting): skip, and record why.** No emissive faces, no PointLight. Studio notes (Requires Manual
  Validation):
  - the boards read warm orange (not red, not brown) under the game's sun;
  - the legs read clearly darker than the posts;
  - the rope reads golden tan and the bolts brass;
  - **a character walks onto the deck from a 5.6 surface (or a ramp end later), along it, and is stopped by the rope
    swags at the sides**; the deck sits 4.6 above the water.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".**
- **Collision:** hero `precise` (the deck walkable, the rope and posts stop the character, the space under the deck
  open); `TimberDockDeck` `box`; `TimberDockPost`, `Beam`, `Crossbeam`, `Brace` `hull`; `TimberDockRope` `none` as a
  part (the hero's precise collision covers the hero's rope).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by searching `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json`,
the repo text (`git grep`) and every sheet / kit / wip `.blend` (zstd-decompressed) with the M044 study's
`blendall.py`:
- **W08** owns `Dock`, `DockStraight`, `DockTHead`, `DockLHead`, `DockPile`, `DockMooringPost`, `DockRopeTie`,
  `DockDeckPlank`, `DockBeam`, `DockBrace` and `Boardwalk*` (`BoardwalkFloorPlank`, `BoardwalkSupportPost`, …), plus
  `FootbridgePlank` and `RopeCrossingPlank`; they occur in `FlintbornWorldKit.blend`, `W08.blend` and every wip copy.
  Keys `w08_*`.
- Other plank names: `MinecartBasePlank` (W15), `LookoutPlatformFloorPlanks` (W13), `WallWalkFloorPlank` (W12);
  `StoneArchPierBlocks` (W16).
- **`TimberDock`, `Jetty`, `Wharf` and `m048_` occur nowhere** in the repo text, the manifests or any `.blend`. `M.mk`
  would silently rename a clash to `<name>M048`; the names below don't clash and none starts with `Dock`.

| Object | Part | Why |
| --- | --- | --- |
| `TimberDock` | hero: posts, deck, beams, crossbeams, braces, rope, blocks, bolts | W08 owns `Dock*`; parallels `StoneRamp`, `StoneCliff` |
| `TimberDockPost` | "Mooring Post": one corner post (full height) with its blocks, bolts and coils | |
| `TimberDockDeck` | the deck boards (exploded group; key "Deck Plank") | |
| `TimberDockBeam` | "Beam" (a side beam) | |
| `TimberDockCrossbeam` | "Crossbeam" | |
| `TimberDockBrace` | "Brace" (a knee brace) | |
| `TimberDockRope` | "Rope Segment" (one swag with knob ends) | |

- Palette keys `m048_*` (§5.4). Collection `Kit/M048 Dock`. No sockets.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1, §3.1): **post centres 8 across × 16 along (two bays of 8), post top 8.3, deck top 5.6; overall about
   10.6 × 19.2 × 8.3** (recommended: the three-quarters' and top's proportions on the 8-stud grid; posts waist-high on
   the 5.5 character).
   - Or **6 × 12, post top 6.2, deck top 4.2** (the same proportions 0.75×: a smaller pier, posts knee-to-thigh high,
     the deck 3.2 above the water).
2. **Boards** (§3.3): **10 full-width boards, 1.82 × 0.85, 0.06 top chamfer, a seam at the middle posts** (recommended:
   f34, front, exploded). Or 12 at 1.6 (top cell).
3. **Shore join** (§2.1): **build the 5.6 deck as drawn; the open end meets M043's 5.6 lawn flush, and a beach needs a
   later ramp-end / stairs piece** (recommended: WorldModeling §13.2 lists "ramp end" as its own dock-kit piece). Or
   lower the deck now (decision 4's low variant) and lose the sheet's tall legs.
4. **Builder parameters:** **write `m048.py` with `W`, `BAY`, `DECK_TOP`, `POST_TOP` constants; build only the drawn
   version now** (recommended), so a low variant (deck 2.6, 1.0 over sand 1.6) or a longer span is a parameter change.
5. **Posts** (§3.5): **one closed post per position, ground → cap, legs darkened by colour below the beams**
   (recommended). Or pile + mooring post as two stacked shells (the exploded's split).
6. **Bracing** (§3.4): **knee braces from the corner legs on both long sides and the +Y end; an X brace on the −Y end;
   six legs** (recommended: front, side, r34). Or the rear cell literally (X on the −X side, no −X middle leg).
7. **Rope** (§2.5): **two coils per post at 0.79 / 0.83 H, five swags (none across the open −Y end), Ø 0.42, 6-sided
   tubes with spiral (rotated-ring) facets, one knot at the +X post of the +Y swag** (recommended). Or 5-sided rope to
   save tris.
8. **Colour** (§5): **one orange timber family by role and position: boards `#E19044`, framing `#B56734`, caps toward
   `#EDA052`, legs blended to `#946039` (render near `#764521`), braces 60 % dark; rope `#F8D088` with a 45 % groove
   strand `#DDA24A`; brass bolts `#F7D894` with a metal finish; the grey, green and blue swatches unused** (recommended).
   Never by facing.
9. **Packaging:** **one hero object of closed shells (no booleans); six parts as the exploded and key labels**
   (recommended).
10. **Comparison cameras** (§2.6): `f34_sheet (47, 16.5)` governing (probe az 40 / 47 / 54 × e 12 / 16.5 / 21);
    `r34_sheet (−41, 17)`; `front_sheet (90, 3)` (+X side); `side_sheet (180, 3)` (+Y end); `rear_sheet (−90, 6)`;
    `top (0, 89)`. Extras: parts shot (−35, 25), `under_cu (35, −30)`, `junc_cu (60, 20)`, the scale shot, the shore
    shot. Floor hidden in every `*_sheet` render. The kit's default `front` (0, 4) looks at the open end; render it for
    the record only.
11. **Stages 5 and 6:** **skip both, recorded; no water, foam or sockets in the model** (recommended).
12. **Collision** as in §7 (recommended).
13. **Budget** (§4.3): **4000 limit, plan about 3600, the coils first in the cut order** (recommended).
14. **Names** as proposed: `TimberDock*`, keys `m048_*`.

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **A hovering plank carpet** (WorldModeling §13.2; W08 "low wide platform"). Load-bearing first: legs on the ground,
   beams on the posts, crossbeams between the beams, boards on the frame, braces meeting real faces. The underside
   render must show every board resting on a beam.
2. **Floating dressing** (STAGES; 035 and 036 round 1). Coils must hug the posts (≤ 0.02), swag ends must sit inside the
   coils, bolts must sit in the blocks, the knot must touch rope. Count floating shells: **0**. A coil standing off its
   post is the dock's version of M041's foam collars standing 0.24–0.40 off the rocks.
3. **Broken winding** (044's wedge back face; STAGES "Consistent winding"). Every box, chamfered box, dome and tube is
   hand-listed: 0 winding errors per shell, checked with a parity ray test, not only the signed volume.
4. **Thin rope or rope that reads as outlines** (W08 rev1 "thick rope" then too thin; M034's foam that read as hard
   outlines). The rope is Ø 0.40–0.45, golden and lit, sagging to just above the deck; coils are fat double bands.
   Not a thin line, not a halo round the posts.
5. **Egg or blob shapes where the sheet is square** (M034 / M037 "egg boulders"). Posts, boards, beams and blocks are
   crisp boxes with small chamfers; bolt heads are round but flat-domed. No subdivision, no smooth shading, no
   rounded-everything bevels (WorldModeling §13.1).
6. **Octagonal caps, round posts or boxy heads** (W08's dock). The posts are square, the caps square with a 0.12
   chamfer.
7. **Wood too red, too brown or flat orange** (W08 "flat orange", "wood still renders slightly red"; 012's wood
   remake). Board tops hue 26–30°, sat 0.62–0.74, value ≥ 0.82; framing a step deeper; legs clearly darker; per-board
   tint so the deck isn't one flat colour.
8. **Colour by facing.** The sheet's light tops and dark sides are the light. Role (board / framing / rope strand) and
   position (cap height, leg zone) only; `K.check` < 0.5 on every material.
9. **Water too pale / foam where none is drawn** (M034 / M041 water lessons). This sheet draws no water: none in the
   model. If a shore shot uses M041, its water is M041's, untouched.
10. **Proportions from the ortho cells.** The front and side cells are drawn at their own horizontal scales; the f34
    governs (L / W 2.0, H 8.3). A dock built to the front cell's 1.27 would be squat and square.
11. **The open end.** No rope or brace above the deck across −Y; five swags only.
12. **Budget.** Coils are about half the count. Follow the cut order in §4.3; never drop a coil, swag, bolt or board.
13. **Names and scope.**
    - No `Dock*` or `Boardwalk*` (W08).
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit other models' builders, `kit_models.py`, `kit_mcp.py`, `build_kit.py` or `lib/vfx.py` (frozen).

## Decisions (main session, 2026-10-29)
All 11 recommendations are accepted.
1. **Size.** Post centres 8 × 16 (two bays). Deck top at 5.6, flush with M043's lower lawn. Posts run to 8.3. Overall about 10.6 × 19.2 × 8.3.
2. **Boards.** 10 full-width boards, 1.82 × 0.85, with a small top chamfer and no groove.
3. **Shore join.** Build the deck as drawn. The ramp-end piece comes later.
4. **Builder constants.** Use `W`, `BAY`, `DECK_TOP` and `POST_TOP`. Build only the drawn version.
5. **Posts.** One continuous closed post per position. Darken the legs by colour below the beams, by position only.
6. **Bracing.** Six legs. Knee braces on both long sides and on the roped end, and an X brace on the open end.
7. **Rope.**
   - Two coils per post and five swags, about 0.42 thick.
   - Six-sided tubes with spiralled facets.
   - One knot, by the +X post.
   - Rope must not read as a thin outline.
8. **Colour.** One orange timber family, coloured by role and position, **never facing**.

   | Part | Colour |
   | --- | --- |
   | Boards | `#E19044` |
   | Framing | `#B56734` |
   | Post caps | toward `#EDA052` |
   | Legs | rendering near `#764521` |
   | Braces | 60 % dark |
   | Rope | `#F8D088`, groove strand `#DDA24A` |
   | Brass bolts | `#F7D894`, metal finish |

   The wood must not read red. The grey, green and blue swatches are not used.
9. **Lighting, VFX, water and foam.** None. Record each as skipped.
10. **Collision.** Precise on the hero, hull on the framing parts, none on the rope.
11. **Cameras.** As listed. The f34 at (47, 16.5) governs.

**Packaging.** No booleans. Every piece is its own closed shell, seated by contact or sunk 0.02. That means **no floating boards, coils or bolts**, and **0 winding errors**. The hero stays under 4000 tris; if it goes over, cut the rope coils first.

## Stage 1 — Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m048.py`, constants:
- `W` 8, `BAY` 8, `DECK_TOP` 5.6, `POST_TOP` 8.3;
- `POST` 1.3, `PLANK_T` 0.85, `BEAM_W` / `BEAM_D` 0.9 / 1.3.

`build()` builds the six parts and the hero, runs every check and renders. Every piece is its own closed shell built
from explicit vertex lists (`_prism`, `_box`, `_plank2d`, `_tube`, `_bolt`, `_knob`), and `_solid` checks each
shell's signed volume. There are no booleans and no unions.

- **Posts (6):**
  - 1.3 square, z 0 → 8.3, with a 0.12 cap chamfer.
  - Extra rings at 2.85 / 3.15 / 3.45 (the leg blend) and 7.2 / 7.75 (the cap blend) only carry colour bands.
  - One shell per post (decision 5).
- **Bolt blocks (10):** 1.3 × 1.0 × 0.35 proud, z 3.55–4.55, sunk 0.02 into the outer long face of every post and the
  end face of the four corner posts.
- **Bolts (11):** 8-sided heads, r 0.275, 0.22 proud with a 0.06 dome, sunk 0.03 into the blocks. The eleventh bolt
  sits at the X-brace crossing.
- **Deck (10 boards):**
  - 1.83 × 0.85 boards with 0.10 gaps over y −9.6 … +9.6 and x ±5.1, with a 0.06 top chamfer and a seam at y 0.
  - Board bottoms are sunk 0.02 into the beams (z 4.73).
  - Tops are jittered ±0.02 (measured 5.583–5.614), and the six un-notched boards are yawed ±0.4°.
  - **Deviation from §2.3:** the six boards that meet a post row are **notched** round the post (an open notch to the
    deck edge, 0.02 clear), instead of being cut back to x ±3.33 across their whole width. Cutting them back would
    leave holes in the deck edge beside every post. With the notch, the board ends continue on both sides of the post,
    as the junction close-up draws.
  - Each notch's inner corner is also joined straight across the board, so the top and bottom faces split into
    near-rectangles and no sliver triangles form.
- **Beams:**
  - 2 side beams: x ±2.45 … ±3.37 (sunk into the posts' inner faces), y ±9.15, z 3.45–4.75.
  - 3 crossbeams at y −8 / 0 / +8, with their ends sunk 0.02 into the side beams.
- **Braces:**
  - **4 long-side knee braces:** from the corner legs' inner faces at z 1.1 to the beam underside at y ±4.6. Centred
    on x ±3.35, 0.45 thick.
  - **2 knee braces on the +Y end:** from the corner legs (x ±3.35) to C+Y's underside at x ±0.9, y 7.6–8.05.
  - **X brace on the −Y end:** two boards (y −7.75…−8.11 and −8.09…−8.45), each running from z 0.45 on one leg to a
    3.40 top on the other. They cross at z 1.93, with a bolt at the crossing.
  - All brace ends are cut to the faces they meet and sunk 0.02.
- **Rope:**
  - **Coils (12):** 6-sided tubes along a 12-point rounded-square path, the centreline 0.845 off the post axis on the
    flats, at z 6.52 / 6.92. They are sunk into the post faces, and the two coils on each post touch.
  - **Swags (5):** 5-sided tubes on a catenary, 12 segments. Their ends sit inside the coils at z 6.72. Low points are
    6.15 on the long sides and 6.05 on the +Y end. There is no swag across the −Y end.
  - **Knot:** two fat 5-sided loops (tube r 0.15) round the +Y swag at x 2.78 / 2.46, beside the +X corner post's
    coil.
  - **Section:** circumradius 0.22, which reads 0.38–0.44 thick.
  - **How the rope got here:**
    - 6-sided antiprism with 8-point coils read as flat stacked plates.
    - A 4-sided twisted cord read as a ribbon.
    - 5-sided antiprism coils read as crumpled paper.
    - **Final:** the coils use aligned rings with the twist carried by colour strands (stage 4), and the swags keep
      the half-turn antiprism twist, which reads as twisted rope at sheet scale.
- **Parts:**
  - `TimberDockPost`: the +X/−Y corner post with both blocks and bolts and two coils.
  - `TimberDockDeck`: the 10 boards.
  - `TimberDockBeam`: the +X side beam.
  - `TimberDockCrossbeam`: a plain crossbeam.
  - `TimberDockBrace`: one long-side knee brace.
  - `TimberDockRope`: one long-side swag with two 8 × 4 ball knobs (r 0.3).
  - The exploded shot uses copies: 4 posts turned so their blocks face out, the deck lifted 5, the beams spread, the
    crossbeams below, the brace in front and the rope above.
- **Renders** (`renders/models/M048/`):
  - the kit's seven default views;
  - `f34_sheet (47, 16.5)`, `r34_sheet (−41, 17)`, `front_sheet (90, 3)`, `side_sheet (180, 3)`, `rear_sheet (−90, 6)`
    and `top_sheet (0, 89)`, all with the floor hidden;
  - six part shots at (−35, 25), `exploded` (−35, 25), and `scale` (5.5 markers on the deck at y 0 and on the ground
    beside a +X leg);
  - close-ups `junc_cu`, `rope_cu`, `bolt_cu`, `under_cu`, `knot_cu`, `xbrace_cu`;
  - everything together in `M048_views.png`.
- **Lens probe** (f34; lens 1 / 1.8 / 3× × az 47 / 54 × e 16.5 / 21): the sheet's three-quarters are near-orthographic.
  At 3× and (47, 16.5) the f34 gives W : H 1.559 (sheet 1.575) and a top-profile error of 0.035 mean / 0.13 max. So
  `LENS` is 3× for f34 / r34, and 8× for the level orthos (so the far post row hides behind the near one).

## Stage 2 — Optimisation and cleanup

Final build, run in a freshly restarted session:

| Object | Tris | Size (studs) | Shells |
| --- | --- | --- | --- |
| `TimberDock` | **3860 / 4000** | 10.56 × 19.20 × 8.30 | 69 |
| `TimberDockPost` | 432 | 2.30 × 2.30 × 8.30 | 7 |
| `TimberDockDeck` | 416 | 10.21 × 19.20 × 0.88 | 10 |
| `TimberDockBeam` | 12 | 0.92 × 18.30 × 1.30 | 1 |
| `TimberDockCrossbeam` | 12 | 4.94 × 0.90 × 1.30 | 1 |
| `TimberDockBrace` | 12 | 0.45 × 3.26 × 2.78 | 1 |
| `TimberDockRope` | 222 | 0.60 × 6.95 × 1.09 | 3 |

- **Hero tris by kind:**
  - wood: 39 shells, 1052 tris;
  - brass: 11 shells, 330 tris;
  - rope: 19 shells, 2478 tris (12 coils × 144, 5 swags × 130, 2 knot loops × 60).
- **Every object:**
  - zero non-manifold edges, bowtie verts, boundary, wire or loose elements, zero-area faces, n-gons and duplicate
    verts;
  - normals outward, transforms applied, origin at the bottom centre (hero offset 0, 0, 0);
  - per shell (`m040.shells_report`): 0 self-hits and 0 inverted faces;
  - smallest corner 17.5° (no face under 5°).
- **Winding:** 0 errors and 0 unpaired edges on every object (directed-edge check).
- **Contact:** 0 floating and 0 unchained shells at tol 0.03 and 0.1 (hero, post, deck and rope parts). The chains:
  - boards → beams → posts → ground;
  - coils → posts; swags → coils; knot → swag and coil;
  - blocks → posts; bolts → blocks; braces → legs and beams.
- **Levels:**

  | Item | Measured |
  | --- | --- |
  | Feet | z 0.00 |
  | Beams | 3.45–4.75 |
  | Board tops | 5.583–5.614 (all 10 within 5.60 ± 0.02) |
  | Coils | 6.52 / 6.92 |
  | Swag lows | 6.15 ×4, 6.05 |
  | Post tops | 8.30 |
  | X-brace crossing | 1.93 |

  No rope runs across the open −Y end.
- **Budget:** under 3900, so no cut was needed.

## Stage 3 — UV

`M.smart_uv` (angle 45, `ANGLE_BASED`, margin 0.008) followed by `m012._uv_unfold`.

| Object | Islands | Overlaps | Flipped | Min gap | Border | Density (min / med / max) | Conformal p95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `TimberDock` | 821 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.04 |
| `TimberDockRope` | 45 | 0 | 0 | 0.016 | 0.008 | 0.979 / 1.002 / 1.002 | 1.091 |
| Other parts | — | 0 | 0 | 0.016 | 0.008 | 1.0 | ≤ 1.015 |

## Stage 4 — Materials, colour and texture

**Calibration** (`m048.calibrate()`, `K.calibrate` dome):

| Key | Target | Calibrated hex | Rendered median |
| --- | --- | --- | --- |
| `wood` | `#E19044` | `#B27B41` | 223, 145, 68 |
| `wood_light` | `#EDA052` | `#BB874D` | 235, 160, 82 |
| `wood_deep` | `#8D4212` (the front cell's post faces, not the flat swatch) | `#753D11` | 141, 67, 18 |
| `wood_dark` | `#6C3D1E` (legs) | `#5C391E` | 108, 62, 30 |
| `rope` | `#F8D088` | `#CBAB7A` | 255, 208, 136 |
| `rope_dark` | `#BE7019` (the sheet's groove strands: front swag lower quartile; coil median `#C2761A`) | `#99601A` | 190, 110, 25 |
| `brass` | `#F7D894` | `#EFD9A0` | 247, 217, 148 |

**Adjusted afterwards on the hero renders** (the dome median doesn't match the model's lit areas):
- `wood` `#BB722E` and `wood_light` `#C97E37`: redder and more saturated, so the f34 board tops land on the sheet (the
  dome key rendered tan);
- `wood_deep` `#88491A` and `wood_dark` `#633D20`: a compromise between the f34, which matched, and the level orthos,
  which were too dark;
- `rope` `#F4CF80`: golden, not cream;
- `brass` `#EBC772`: the calibrated key rendered pale cream with metal 0.5; this one reads gold.

**Finish:**
- wood: roughness 0.85 (legs 0.9), metal 0, low specular;
- rope: roughness 0.95, low specular;
- brass: metal 0.5, roughness 0.4.

**Colour by role and position only, never facing.** `K.check` baked-shading correlation: hero 0.03, post part 0.11,
everything else 0.0.
- **Boards:** `wood`. Boards 2 and 7 at 15 % `wood_deep`, and boards inside a broad noise field at 15 % `wood_light`.
  - Per-board Tint ±0.03 plus K.texture 0.02.
  - One key per board, with hard edges only between boards.
- **Posts:** `wood_deep`, varied by height:
  - full `wood_dark` below 2.85, then 65 % / 35 % dark in the bands up to the beam bottom at 3.45;
  - 20 % / 40 % `wood_light` above the coils (7.2 / 7.75), and 60 % on the chamfer and top;
  - Tint ±0.03, texture 0.03.
- **Blocks, beams and crossbeams:** `wood_deep`, with Tint ±0.03 per member.
- **Braces:** 60 % `wood_dark`.
- **Bolts:** `brass`.
- **Rope:** strands are coloured by their place in the twist, never by facing.
  - **Coils:** (side − ring) mod 3 gives three plies, `rope_dark` / 45 % amber / golden `rope`, which spiral like a
    three-ply rope. (An even / odd split made a checkerboard.)
  - **Swags and knot:** strand 0 is `rope_dark`, strand 2 is 90 % amber, the rest are golden. About half the rope reads
    amber and half golden, as on the sheet.

**Re-measured** on the final renders against the sheet, with the study masks:

| View | W : H | W % | K % | Y % | W median | K median | Y median |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | 1.559 (1.575) | 39.2 (35.9) | 52.2 (58.2) | **8.6 (5.9)** | `#DD8334` (`#D77D34`) | `#703716` (`#6D3411`) | `#E2BA66` (`#F8CF7C`) |
| r34 | 1.472 (1.543) | 49.6 (30.7) | 41.9 (63.2) | 8.6 (6.1) | `#E18535` | `#6B3B19` (`#713714`) | — |
| front | 2.208 (1.871, recorded) | 21.6 (24.1) | 67.6 (69.9) | 10.8 (5.9) | `#AC6528` (`#B35C19`) | `#713613` (`#7C4219`) | — |
| side | 1.188 (1.560, recorded) | 30.7 (22.2) | 60.8 (72.2) | 8.5 (5.6) | — | `#854119` (`#7C411B`) | — |
| top | 0.551 (0.575) | 83.0 (72.8) | 8.9 (26.8) | 8.0 (0.4) | — | — | — |

Top profile error (mean / max):

| View | Mean | Max |
| --- | --- | --- |
| f34 | 0.035 | 0.13 |
| r34 | 0.026 | 0.08 |
| front | 0.030 | — |
| side | 0.046 | — |

Region samples (`region_report()`):

| Region | Ours | Sheet | Max channel diff |
| --- | --- | --- | --- |
| f34 board tops (24-point median) | `#D18738` (31°, 0.73, 0.82) | `#DF8C3E` | 14 |
| f34 cap top | `#E3843D` | `#D07C4A` | 19 |
| f34 legs | `#5C3419` | `#62371C` | 6 |
| front board ends | `#A15A22` | `#A95015` | 12 |
| front post face | `#70350F` | `#8D4212` | 28 |
| front beam | `#72360F` | `#89451B` | 22 |
| front legs | `#4E2B13` | `#764521` | 40 |

- The value order board ends > post faces > legs holds.
- The front cell's +X faces sit in the studio's darker side light. The f34, which governs, matches on legs and board
  tops.
- Wood hue is 23–31° everywhere: not red. The board tops' R − G is 74.

## Stage 5 — Lighting: skipped

The sheet shows no emissive part, glow or light (decision 9), so there are no emissive faces and no lights. To check in
Studio (Requires Manual Validation):
- the boards read warm orange, not red;
- the legs read clearly darker than the posts;
- the rope reads golden and the bolts brass;
- a character walks on from a 5.6 surface and is stopped by the swags at the sides.

## Stage 6 — VFX: skipped

The sheet shows no effect and no water or foam (decision 9). The hero has no sockets; `checks()` flags any.

## Modeller's notes for the verifier

- **Rebuild:**
  `import importlib, kit_models, m048; importlib.reload(kit_models); importlib.reload(m048); m048.build()`.
  - `m048.measure_views()` gives the W / K / Y shares; `build()` returns them under `measure`.
  - `m048.region_report()` gives the spec 5.4 region samples.
- **Known misses:**
  1. **Y share on the f34: 8.6 against 5.9** (tolerance ±1.5).
     - Bolts are 1.4 of that (a probe with the rope recoloured blue left Y at 1.4).
     - The sheet's rope falls into deep amber (W) on its shade side. Our studio light keeps more of the golden strands
       bright, even with half the strands amber.
     - Thinning the rope below Ø 0.38 would break decision 7 ("not thin"), so I didn't.
     - The Y median `#E2BA66` is darker than the sheet's `#F8CF7C`.
  2. **f34 K: 52.2 against 58.2**, right at the edge (the lighter boards push into W).
     - The r34 W / K 49.6 / 41.9 is well off the sheet's 30.7 / 63.2, because the studio key light lights the faces
       that camera sees.
     - The medians themselves match within 6–7.
  3. **Ortho cells:** the front, side and rear cells are drawn at their own horizontal scales, so their W : H (2.21 /
     1.19 against 1.87 / 1.56) is the recorded miss from §3.1.
     - At e 3 the side and front shots show the far post row's tops just above the near row.
     - The front_sheet framing is darker than the sheet (post face −28, legs −40) because of the light direction.
  4. **Not modelled:**
     - the cap peg dots and the faint vertical split line on the posts (a shallow V reads as nothing under flat
       shading);
     - the r34's mid-span knot (§3.7: the knot is at the post);
     - the rear cell's literal X brace and missing leg (§3.4).
  5. **Board notches** deviate from §2.3 (see Stage 1).
  6. **Hero budget:** 3860 tris, 2478 of them rope. More rope detail would need the §4.3 cut order.
- **Judge the rope by eye:** compare `rope_cu`, `junc_cu` and `knot_cu` with the junction close-up and the f34. The
  coils are round twisted rings with spiral plies; the swags are twisted 5-sided cords.

## Verification round 1 (verifier, 2026-10-29)

A fresh verifier, read-only. It used a background session on port 9877 with `wip/M048_verify.blend`. It ran no
`build()`, edited no code and saved nothing. Every number below was re-measured with the verifier's own bmesh, BVH
and numpy code; `M.audit`, `M.uv_stats` and `K.check` were used only as cross-checks. Renders went to the scratchpad
(`…/scratchpad/m048_verify/`), not to `renders/models/M048/`. The sheet cells were measured with the verifier's own
implementation of the §1.2 masks, which reproduces §1.2 on the f34 cell: W : H 1.568, W 35.9, K 58.2, Y 5.9.

### Mesh

| Object | Tris / budget | Size | Shells | Non-manifold, boundary, wire, loose, zero-area, n-gons, dup verts | Winding (dup directed / unpaired) | Bowtie verts | Self-hits per shell | Inward faces (triangulated, per-shell ray parity) | Min corner | Origin / transforms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `TimberDock` | **3860 / 4000** | 10.56 × 19.20 × 8.30 | 69 | all 0 | 0 / 0 | 0 | 0 | 0 | 17.5° | bbox x ±5.28, y ±9.6, z 0–8.3; rot 0, scale 1 |
| `TimberDockPost` | 432 / 1000 | 2.30 × 2.30 × 8.30 | 7 | all 0 | 0 / 0 | 0 | 0 | 0 | 17.5° | centred, z 0 |
| `TimberDockDeck` | 416 / 1000 | 10.21 × 19.20 × 0.88 | 10 | all 0 | 0 / 0 | 0 | 0 | 0 | 54.7° | centred, z 0 |
| `TimberDockBeam` | 12 | 0.92 × 18.30 × 1.30 | 1 | all 0 | 0 / 0 | 0 | 0 | 0 | 90° | centred, z 0 |
| `TimberDockCrossbeam` | 12 | 4.94 × 0.90 × 1.30 | 1 | all 0 | 0 / 0 | 0 | 0 | 0 | 90° | centred, z 0 |
| `TimberDockBrace` | 12 | 0.45 × 3.26 × 2.78 | 1 | all 0 | 0 / 0 | 0 | 0 | 0 | 40.5° | centred, z 0 |
| `TimberDockRope` | 222 / 1000 | 0.60 × 6.95 × 1.09 | 3 | all 0 | 0 / 0 | 0 | 0 | 0 | 25.5° | centred, z 0 |

- **Hero shells:** 69, as specified: 6 posts, 10 blocks, 11 bolts, 10 boards, 2 beams, 3 crossbeams, 8 brace boards, 12
  coils, 5 swags and 2 knot loops. Every shell has a positive signed volume, and no shell mixes materials.
- **Quads:** every hero quad is planar. In the rope part, 32 knob quads are non-planar by up to 0.035. Triangulated,
  their normals are still outward.
- **UV:** 0 overlaps and 0 flipped islands on every object; min gap 0.016, border 0.008, density 1.0. The rope part's
  conformal p95 is 1.09.
- **Other:** no modifiers or children; no emission anywhere; no `water` key. Collision is precise on the hero, hull on
  the post, beam, crossbeam and brace, box on the deck, and none on the rope.

### Contact and levels

- **Floating:** 0 shells floating at tol 0.03, and 0 without a chain to the ground (hero, post, deck and rope part).
  - **Boards:** every board sits on the beams (distance 0: bottoms 4.73 against beam tops 4.75). The six notched
    boards stand 0.020 clear of the posts. No two boards overlap.
  - **Coils:** all 12 touch their posts, sunk at most 0.016.
  - **Swags:** they end inside the coils, 0.10 short of the post faces, and come no closer to a board than 0.24 (the
    +Y swag) or 0.33 (the long sides).
- **Levels:**
  - leg feet z 0.00 and post tops 8.30;
  - board tops 5.583–5.614 (all within 5.60 ± 0.02);
  - beams and crossbeams 3.45–4.75;
  - coils z 6.30–7.14;
  - swag bottoms 5.93–5.95 on the long sides and 5.85 on the +Y end (centre lows about 6.15 and 6.05);
  - the X brace runs z 0.45–3.40, with its bolt at z 1.67–2.18.
- **Open −Y end:** the only rope past y −7.25 is the two −Y posts' own coils, and no brace reaches above z 3.4. No
  rope crosses the open end.
- **Walking:** the deck is flat to ±0.02 with 0.10 gaps. The posts leave 6.7 clear between their inner faces, and the
  coils, 0.7 above the deck, leave 5.96. A 5.5 character fits on the deck (the `deck_walk` and scale views agree).

### Views and shares (f34 at lens 3×; masks per §1.2; sheet values from the verifier's own re-measure)

| View | W : H ours (sheet) | W ours (sheet) | K | Y | Top-profile error mean / max | W median | K median | Y median |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **f34 (47, 16.5)** | 1.563 (1.568) | 39.2 (35.9) | **52.2 (58.2)** | **8.6 (5.9)** | 0.036 / 0.12 | `#DD8334` (`#D77D34`) | `#703716` (`#6D3411`) | `#E2BA66` (`#F8CF7C`) |
| f34 probe (40, 12) | 1.623 | 35.7 | 56.1 | 8.2 | 0.047 / 0.15 | | | |
| f34 probe (54, 12) | 1.788 | 32.2 | 59.3 | 8.6 | 0.058 / 0.17 | | | |
| f34 probe (40, 16.5) | 1.476 | 40.7 | 51.1 | 8.2 | 0.030 / 0.12 | | | |
| f34 probe (54, 16.5) | 1.629 | 37.9 | 53.2 | 8.9 | 0.046 / 0.15 | | | |
| r34 (−41, 17) | 1.470 (1.548) | 49.5 (30.7) | 41.9 (63.2) | 8.6 (6.1) | 0.022 / 0.07 | `#E18535` (`#DD8D40`) | `#6B3B19` (`#713714`) | `#FFD678` (`#F8CC7A`) |
| front (90, 3) | 2.221 (1.871, §3.1) | 21.6 (24.1) | 67.6 (69.9) | 10.8 (5.9) | 0.021 / 0.12 | `#AC6528` (`#B35C19`) | `#713613` (`#7C4219`) | |
| side (180, 3) | 1.188 (1.571, §3.1) | 30.7 (22.2) | 60.8 (72.2) | 8.5 (5.6) | 0.052 / 0.17 | | `#854119` (`#7C411B`) | |
| top (0, 89) | 0.548 (0.575) | 83.0 (72.8) | 8.9 (26.8) | 8.1 (0.4) | — | | | |

- **Where the gold comes from** (f34, probes with the rope or the brass temporarily recoloured blue, then restored;
  materials verified restored):
  - the rope makes 7.6–7.7 of the 8.6 Y points, and the bolts 1.0;
  - the rope covers 13.6 % of the silhouette, and about 56 % of its pixels class as Y (the amber plies fall into W/K);
  - the sheet's four visible bolts are about 0.5 (estimated).
  - So the +2.7 excess is mostly **rope (about +2.2)**, with the bolts about +0.5.
- **Region samples** (f34 (47, 16.5), 5 × 5 medians at build-frame points; front_sheet the same way):

  | Region | Ours | Sheet |
  | --- | --- | --- |
  | Board tops | `#D58637` (30°, 0.74, 0.83) | `#DF8C3E`, Δ10 |
  | Cap top | `#E3843E` | `#D07C4A` |
  | Post above deck | `#713711` (23°) | |
  | Board ends | `#A05A22` | `#A95015` |
  | Beam | `#723711` | |
  | Legs, +X face | `#4E2B14` (v 0.31) | f34 `#62371C` |
  | Legs, −Y face | `#683B1C` | |
  | Brace | `#5D3319` | |
  | front_sheet: board end / post face / leg | `#A15A22` / `#713610` / `#4D2B13` | `#A95015` / `#8D4212` / `#764521` |

  - Wood hue is 22–31° everywhere: **one orange family, not red**. The board tops' R − G is 90 (limit 95).
  - Rope 40–42°; brass is gold, metal 0.5, rough 0.4.
- **Colour by role and position, never facing:**
  - `K.check`: 0 problems; baked shading hero 0.03, post part 0.11, the others 0.
  - **Grep:** the builder's only `normal` uses are geometry (`_solid` winding, tube frames, bolt axes, block faces).
    No paint selection uses a normal. Posts use face-centre height (`_post_colour`), coils and swags use strand index
    (`_strands`), and boards use one key per board.
  - **Correlations:** wood lightness rank against normal z is 0.24 raw, but **−0.004 once height is regressed out**.
    Rope-dark share against normal z is −0.009. No post height band mixes materials.
  - **Legs:** `wood_dark` below 2.85, then 65 % and 35 % up to the beam bottom at 3.45. That is by height only.
- **Tint:** a corner float colour.
  - **Wood:** 0.955–1.057, sd 0.020. Board means differ from 0.986 to 1.029, and within a board the sd is about 0.007
    (gentle, no confetti). Its correlation with normal z is −0.003.
  - **Rope:** 0.981–1.018.

### Shape against the sheet (every cell compared at matching angles)

- **Matches:**
  - the f34 / r34 silhouette and layout (open end at the left of the f34 and the right of the r34, five swags, six
    square posts with chamfered caps, board ends as blocks along both long edges);
  - beams and crossbeams; bolt blocks with round brass heads;
  - legs darker below the beams; knee braces on the long sides (front cell) and the +Y end (side cell); the X brace
    with its crossing bolt on the −Y end (r34);
  - the top view's ten boards and caps;
  - the underside (boards on the beams, knee brace from leg to beam, nothing floating);
  - the six parts against the key parts and the exploded view.
- **Swags:** twisted, golden and amber, sagging to just above the deck. They read as rope, not outlines.
- **Coils:** fat double bands (0.84 tall, 0.37 proud of the post), not outlines. Close up (`junc_cu`, `coil_cu`) they
  read as **faceted octagonal collars with a stepped two-tone ply pattern** rather than the sheet's braided rope rings.
  At the sheet's scale they read as golden rope bands.

### Findings

1. **minor — coil read.** The coils use aligned rings, so the twist is carried only by the triangulation diagonals and
   the colour plies. Close up they look like brass-gold washers more than braided rope (junction close-up, key "Mooring
   Post").
   - **Fix target:** give the coils a geometric twist, either a ring rotation of half a side per ring (§2.5) or strand
     bumps that break the octagon silhouette, so the junction close-up reads as rope. Keep 6 sides and stay under 4000
     (§4.3 cut order).
2. **minor — decision 7, partly met.** Decision 7 asks for six-sided tubes with spiralled facets.
   - The swags and knot loops are **5-sided**.
   - The coils are 6-sided but have no spiralled facets (finding 1).
   - At 3860, 6-sided swags would land at about 3990, still under 4000, so the cut wasn't forced. It was a reorder of
     the §4.3 cut order (swags before coils), and the modeller didn't list it as a known miss.
   - The intent of the decision (thick, twisted, not an outline) is met.
   - **Fix target:** 6-sided swags, or the main session accepts 5 and records it.
3. **minor — f34 Y 8.6 against 5.9 (+2.7).** That is outside the spec's ±1.5 but inside the binding ±4.
   - About +2.2 of the excess is rope and about +0.5 is bolts.
   - **Fix target, if wanted:** raise the coils' amber-ply share (by strand index, never facing), or thin the coils'
     golden ply.
4. **minor — f34 K 52.2 against 58.2 (−6.0) at the governing camera.** That is outside the binding ±4 there, and at
   the spec's ±6 edge.
   - At the §2.6 probe (40, 12), all three shares are within ±4 (W 35.7, K 56.1, Y 8.2), and W : H 1.623 is within
     ±0.08.
   - The W and K medians match the sheet within 3–6 per channel, so this is the studio light's lit/dark split, not a
     key error.
   - **Fix target:** none needed. Record (40, 12) as the in-band probe.
5. **minor — r34 W / K 49.5 / 41.9 against 30.7 / 63.2.** The studio key lights the −X faces; the medians match (K
   `#6B3B19` against `#713714`). The top view's W 83 against 72.8 has the same cause. The r34 isn't binding. Accept.
6. **minor — board notches instead of the §2.3 cut-back.** Judged correct: the junction close-up draws the boards
   continuing on both sides of the post. They leave 0.02 of clearance and no holes in the deck edge. Accept.
7. **minor — legs a little too dark in side-lit views.** The front legs are `#4D2B13` against `#764521` (Δ41), and the
   f34 +X face Δ20. The leg / post value ratio is 0.70 against the sheet's 0.84.
   - **Fix target (optional):** lighten `wood_dark` about 10 %. Keep the legs clearly darker than the posts.
8. **minor — f34 rope Y median `#E2BA66` against `#F8CF7C` (Δ22, a touch dull).** In the r34 it is `#FFD678`, so this
   is light-dependent. Optional.
9. **minor — knot reads boxy.** It is two small wraps, not the side cell's lumpy loop at the post. Optional.
10. **minor — rope part's knob quads are non-planar (≤ 0.035).** Harmless once triangulated. Optional: build the
    knob bands as triangles.
11. **minor (recorded) — ortho cells.** The front, side and rear W : H misses come from §3.1. The side_sheet also
    shows the −Y X brace through the open legs, which is consistent in 3D; the side cell doesn't draw it.
12. **minor — bolt blocks barely read in the front view.** They are the beam's colour and only 0.35 proud, where the
    sheet's blocks read as distinct squares. Optional.

**Decisions:**
- 1 (size), 3, 4, 5, 6, 8, 9, 10, 11 and Packaging are followed exactly.
- 2: followed. The boards are 1.83 wide rather than 1.82, so ten boards with 0.10 gaps fill 19.2.
- 7: partly met (finding 2).

**No blockers.** The mesh and winding are clean, the model is under budget, nothing floats, the silhouette and parts
are right, the rope is thick, the colour is one orange family, and nothing is coloured by facing.

**Score: 8 / 10.** **Verdict: PASS.** Findings 1–2 (the coils' rope read and 6-sided swags) are the most worthwhile
polish if a round 2 is run.

## Main session ruling (2026-10-29)
- **Verdict:** passed in round 1 (8/10) and committed.
- **Decision 7:** 5-sided swags and knot loops are accepted. The rope still reads thick and twisted, which was the decision's intent. Recorded here as a known deviation.
- **Board notches** instead of the cut-back are accepted. They match the junction close-up.
- **Left for a later polish pass:**
  - Coils read as faceted octagonal collars. Give them a geometric twist.
  - The f34 gold share is +2.7, mostly rope. Use a larger amber-ply share on the coils.
  - The f34 dark wood is −6.0 at the governing camera, which is lighting; it passes at (40, 12).
  - The legs are a little dark in side light.
  - The rope median is slightly dull.
  - The knot is boxy.
  - The bolt blocks barely read from the front.
- **Export:** 7 assets, 7 solid pieces, 4966 tris, 0 VFX sockets, palette 16 colours, 0 problems.
