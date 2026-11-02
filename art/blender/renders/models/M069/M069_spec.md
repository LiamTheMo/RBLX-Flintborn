# 069 Palisade Wall — spec

Reference: `art/blender/assets/references/069.png` (1024 × 1536 px). INDEX.md row 69: "Flintborn palisade wall study".
The sheet's header reads **"PAGE 73/132"** (top right), title **"PALISADE WALL"**, subtitle "INDIVIDUAL ASSET PRODUCTION
REFERENCE", footer "FLINTBORN — INDIVIDUAL MODEL STUDY" (our number is INDEX's 069).
Builder: `art/blender/kit/mcp/m069.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows no glow, light or effect** (§7).
The subject is **one straight, modular, tileable section of a log palisade with its dressing**:
- a row of **ten sharpened palisade logs** of uneven height (octagonal, chamfered, faceted pale pointed tops, flat-cut
  feet), including two narrow filler poles;
- **two thick anchor posts** (the tallest pieces), each with **two chunky rope bands**;
- **horizontal rails** lashed across the logs: two full rails on the rear face, a stepped pair on the front face, each
  with short **end stubs** beyond the posts and **rope lashings** of three turns at chosen logs;
- a **red swallowtail banner with a white diamond emblem** on a rod in front of the right half ("optional and removable");
- **lavender-grey ground rocks** chocked against the feet and **lime-green leafy rosettes** along both faces.

Sheet text (paraphrased):
- **Title block:** "FLINTBORN", "PALISADE WALL", "INDIVIDUAL ASSET PRODUCTION REFERENCE", "PAGE 73/132".
- **"FRONT THREE-QUARTER VIEW"** and **"REAR THREE-QUARTER VIEW"** (what the r34 really shows: §3.2).
- **"ORTHOGRAPHIC VIEWS"**: "FRONT VIEW", "SIDE VIEW (RIGHT)", "REAR VIEW", "TOP VIEW".
- **"EXPLODED CONSTRUCTION"**, labels: "Palisade Log (uneven height)", "Horizontal Beam" (its sub-labels are garbled
  generator text: "(rexnct / (Beorusm) / (cwto)"), "Ground Rock (Stone)", "Foliage (Decorative)". Unlabelled: more logs
  (some with a rope band), a short flat-topped log stub with a band, two beams with rope bands near their ends, a short
  square block, a tall post split into a long upper piece and a banded lower piece, the banner, its rod, rocks and
  rosettes, dashed drop arrows.
- **Close-ups:** **"BEAM & LASHING DETAIL"** ("Palisade Log", "Horizontal Beam", "Lashing Rope"); **"POST TOP DETAIL"**
  ("Faceted Pointed Top (typical)"); **"BASE DETAIL (UNDERSIDE VIEW)"** ("Beam Underside", "Log Bottom (flat cut)",
  "Ground Rock").
- **"MATERIAL PALETTE (REFERENCE)"**: Wood (Main), Wood (Secondary), Rope, Banner, Rock, Foliage.
- **"MODELING NOTES"** (paraphrased): chunky, low-poly and legible; broad flat-shaded faces, no fine texture noise;
  uneven log heights for a hand-built look; horizontal beams on the rear, lashed with rope; the banner is optional and
  removable; simple rocks and foliage as separate pieces; consistent proportions across the views; reuse parts.
- **Game context and the old kit:**
  - **W12 row 1 `PalisadeWall`** (`art/blender/scripts/kit/W12/palisade_wall.py`; manifest `art/roblox/kit/W12/manifest.json`;
    goals `art/blender/renders/kit/W12/palisade_wall_goals.md`; compare `palisade_wall_compare.png`) is the old kit's
    palisade from a related row sheet. **Exported** hero `PalisadeWall` **10.62 W × 4.69 D × 11.57 H, 1904 tris,
    `precise`**; variants `…Intact`, `…LowBroken`, `…Tall`; parts `…Log` (1.2 × 10.4), `…Post` (1.26 × 6.6), `…Beam`
    (7.0 × 0.6 × 0.5), `…GroundCollar`, `…Banner` (1.75 × 4.4). Its goals: 9–12 logs 7.5–9.5 tall, posts to 10.5, tan
    cone tips ≈ 1/5 of the height, two rear beams at z ≈ 3 and 6. `MODEL_PROGRESS.md` row 90: **"uniform thin logs (ref
    uneven thick trunks); few lashings"**; `art/reference/kit/CHECKLIST.md`: PalisadeWall **6/10**. It does not tile
    (no seam contract).
  - **Siblings:** W12 `DoubleGate` (exported, **15.02 W × 9.83 H × 4.2 D**: fits one 16-stud slot, §2.9), `Barricade`,
    `WallWalk` (18.4 long: does not fit the pitch); M040 `StoneCliff` tile (**16-stud pitch, seams x ±8**, the tile
    contract this spec copies), M043 (20-stud pitch; its m3 / m4 pivot and seam-ring lessons); M064 `CanvasTent`
    (rope lashing lessons, its Rulings and minors), M068 `TimberCabin` (decided: plates 11.2, door 7.0; timber `#A95929`).
    WorldModeling §13.1 (timber vocabulary), §13.4 ("Palisade: repeat a few log shapes with controlled height
    differences, add rear horizontal rails, and keep a consistent wall thickness"), §12.2 (modular straight / corner /
    end pieces with a consistent connection area), §13.8 (banner: one readable white diamond emblem).
  - **Terrain grid:** 32 studs (WorldModeling, repository integration); M040's tile is half a cell.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is near-white
(`#F9F5EC`); pieces cast a soft warm-grey shadow down and to the left (s < 0.06, v 0.80–0.95), which the masks drop.
Frame (±5 px): header rule y ≈ 68; hero panels y ≈ 108–515 (titles to y ≈ 140), divider x ≈ 535; ortho title y ≈
525–550, cell labels y ≈ 560–582, cells to y ≈ 800, dividers x ≈ 336, 498, 766; exploded panel x 12–720, y ≈ 815–1315;
close-up column x 732–1012 (A y ≈ 815–1000, B ≈ 1010–1150, C ≈ 1160–1315); palette x 12–532, y ≈ 1330–1495; notes x
545–1012; footer rule y ≈ 1515.
- **Cells:** f34 (12,140,532,512); r34 (537,140,1014,512); front (12,585,334,800); side (338,585,496,800); rear
  (500,585,764,800); top (769,585,1013,800); exploded (12,840,720,1312); cuA (735,840,1012,1000); cuB
  (735,1035,1012,1150); cuC (735,1180,1012,1312). (Use y0 = 146 for f34 / r34 shares, below the title bars.)
- **Swatches** (inner boxes, y 1374–1432): Wood (Main) (27,1374,85,1432); Wood (Secondary) (109,…,167,…); Rope
  (192,…,250,…); Banner (275,…,333,…); Rock (358,…,416,…); Foliage (441,…,500,…).
- **Masks** (`m.py` `classes()`, HSV, h in degrees):
  - **W** timber: (h 8–48 or ≥ 345), s ≥ 0.40, v ≥ 0.12, not B / R; plus h 8–48, s 0.25–0.40, v < 0.66.
  - **R** pale timber + rope (the cut tips, rod knobs and rope share one hue band): h 30–50, s 0.25–0.62, v ≥ 0.66.
    Split by position when needed: tips above each log's shoulder, rope elsewhere.
  - **B** banner red: (h < 14 or > 340), s ≥ 0.55, v ≥ 0.35. **G** foliage: h 62–170, s ≥ 0.28, v ≥ 0.12.
  - **S** stone (cool lavender grey): s < 0.26, v 0.22–0.90, B ≥ R − 4, not G, and (s ≥ 0.06 or v < 0.80) (drops the
    paper and the cast shadow). **K** dark: v < 0.22, not W / B / G.
  - Wood value bands: **lit** v ≥ 0.80, **mid** 0.50–0.80, **shade** < 0.50.
  - Apply the same code to our renders (studio floor hidden, plain background).

**Scratch study material** (no Blender) in `<temp>\m069\` (the session scratchpad). No Pillow on this machine: the
scripts use Blender's bundled Python (`<blender dir>/5.2/python/bin/python.exe -I <script> < /dev/null`, numpy only)
with a small PNG reader / writer (`png.py`); `m.py` caches the sheet as `sheet.npy` and holds the masks.
- **Measurements:** `bbox.py` / `bbox2.py` (bbox, W : H, fill, shares, value bands), `sky.py` (skyline tip peaks per
  cell), `scan.py` (row seams, column profiles, per-column skyline), `comps.py` (connected parts per class: banner,
  rocks, foliage, rope).
- **Colour:** `sw2.py` (swatches), `samp.py`, `samp2.py` (class medians per cell and per named region; lit and shade
  quartiles).
- **Zooms:** `z_f34.png`, `z_r34.png`, `z_front.png`, `z_side.png`, `z_rear.png`, `z_top.png`, `z_ex_l.png`,
  `z_ex_r.png`, `z_cu.png`, `z_pal.png` (`zoom.py x0 y0 x1 y1 scale out.png [grid]`).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** a modular structure tile (a straight wall section) with dressing. **Hero under 4000 tris (STAGES),
  plan 3500–3850; every part under 1000; the plain tiling variant ≈ 2850** (§4.3, decision §8.2). It is not a
  "building" for the README's 8000 ceiling: it repeats along every fort perimeter, so it stays lean.
- **Overall read (check this first).** A **long, warm orange-brown fence of tall sharpened logs with an uneven,
  zig-zag skyline of pale pointed tips**, two taller banded posts, chunky golden rope, a red banner hanging on the right
  half of the front, grey-lavender rocks and bright lime rosettes along the foot:
  - **orange timber first** (f34 W 73 %), then the **pale tips and golden rope** (R 7.8), the **lime foliage** (G 8.8),
    the **red banner** (B 6.1), the **rocks** (S 3.4); wood lit / mid / shade 15 / 44 / 41.
- **Focal silhouettes, in order:**
  1. The skyline: twelve pointed tips at uneven heights (ten logs and the two posts; the +X post the tallest of all).
  2. The banded posts and the rails with their lashings across the logs (front: stepped; rear: two full rails).
  3. The banner with its rod; the chocked rocks and rosettes; the end stubs; the flat-cut feet.
- **Target size (decision §8.1):**
  - **Module pitch 16.00 (seams x = ±8.00), log row centred on y = 0. Tips 7.6–12.2 (main logs 8.0–11.5, posts 10.3
    and 12.2). Wall band ±0.875 (posts), rails out to ±1.43, their lashings to ±1.69, dressing to ±2.50.**
  - **Hero ≈ 16.0 W × 5.0 D × 12.2 H; plain module ≈ 16.0 × 3.38 × 12.2.**
  - Tolerances: pitch exact (seam planes ±0.005), tips ±0.3, post tips ±0.2, rail levels ±0.15, Ø ±0.05.
  - **How it was derived.** No piece carries a size. The front and rear cells are true elevations and agree: front
    logs span x 41–306 px (266 px) with the tallest tip 203 px above the ground (W : H **1.31**); rear 512–748 (237 px),
    181 px (**1.31**). The rear cell is drawn 0.88 × the front's size; the side cell 0.93 ×.
    - **The pitch sets the scale:** 16.0 studs across the log row = 0.060 stud / front px (0.068 / rear px). It is
      M040's tile pitch (half a 32-stud terrain cell), so two modules fill a cell and corners land on the grid.
    - That gives a typical log Ø 1.25–1.45 (front 20–23 px), posts 1.75 (28 px; rear 27 px ⇒ 1.84), end logs 1.47.
    - Heights (front px above ground y 789 × 0.060; rear in brackets): tallest post 12.2 (rear 12.3), other post 10.3
      (10.6), end logs 8.3 / 10.4 (9.0 / 10.6), the rest 7.6–11.5.
  - **Why this size.**
    - **Against the character (5.5; Roblox's default jump ≈ 7.2):** the shortest main log (8.0) is 1.45 C and clears a
      standing jump; the posts are 1.9 C and 2.2 C. The rails sit at 2.8 / 5.4–7.1 (knee, head, over head). The wall
      reads as a fortification, not a garden fence.
    - **Against the kit:** W12 `PalisadeWall` logs 7.4–9.1, posts 10.0; M068 hut plates 11.2; M040 cliff lawn 10.4; W12
      `DoubleGate` 9.83 tall and 15.02 wide (fits one 16 slot). A smaller pitch (12) makes the logs Ø 1.0, the "uniform
      thin logs" the old row failed on; a larger one (20, M043's) makes 15-stud tips that tower over the hut.
- **Build frame (decision §8.3):** front −Y (the outside, the banner face), +X right, ground z 0, the log axes on y = 0,
  the module centred on x = 0. The dressing is kept symmetric (front and rear reach |y| 2.50; nothing past |x| 7.95)
  so **the bbox bottom centre is the build origin** and no PivotOffset is needed (M040 / M043 pivot lesson).

### 1.2 Measured views (`bbox.py`, `bbox2.py`)

| View (box) | Object bbox (px) | W : H obj / timber + rope | fill | W / R / B / S / G / K % | wood lit / mid / shade % |
| --- | --- | --- | --- | --- | --- |
| **f34** (12,140,532,512) | 41–523 × 120–510 | **1.235 / 1.115** | 0.599 | 73.0 / 7.8 / 6.1 / 3.4 / 8.8 / 0.9 | **15 / 44 / 41** |
| r34 (537,140,1014,512) | 540–995 × 127–511 | 1.184 / 1.094 | 0.605 | 78.8 / 8.8 / 0.0 / 3.3 / 8.0 / 1.1 | 16 / 47 / 37 |
| **Front** (12,585,334,800) | 23–325 × 587–790 (logs 41–306) | **1.485 / 1.31** (logs) | 0.621 | 73.1 / 7.4 / 7.4 / 3.7 / 7.3 / 1.1 | 13 / 46 / 41 |
| **Side** (338,585,496,800) | 371–461 × 595–789 | **0.467 / 0.242** | 0.444 | 59.5 / 9.8 / 6.1 / 10.9 / 12.6 / 1.1 | 16 / 56 / 29 |
| **Rear** (500,585,764,800) | 503–760 × 609–789 (logs 512–748) | **1.425 / 1.309** | 0.642 | 80.0 / 8.2 / 0.0 / 4.7 / 6.0 / 1.2 | 12 / 51 / 37 |
| Top (769,585,1013,800) | 784–995 × 647–739 | 2.28 / 3.35 | 0.540 | 63.5 / 8.8 / 0.0 / 7.4 / 19.7 / 0.6 | 35 / 25 / 41 |

- **Front cell skyline** (`scan.py hrun`; tip px x : y, ground y 789): 54 : 651, **85 : 618 (post)**, 110 : 655,
  129 : 643, 152 : 640, 168 : 663 (narrow), 183 : 631, 207 : 598, 232 : 626, **257 : 586 (post)**, 275 : 633 (narrow),
  293 : 616. Log edges (px): 41 | 72 | 100 | 120 | 141 | 163 | 172 | 195 | 221 | 244 | 272 | 280 | 306.
- **Front cell levels** (z = px above ground × 0.060): front mid rail centre 5.4 (692–709 incl. lashing), front upper
  rail 7.1 (664–677, x 247–290), banner rod 8.5 (644–650, x 203–253), banner 8.7 → 1.9 (x 209–247), emblem centre 5.5
  (1.4 W × 3.1 H). −X post bands z 1.9–2.7 and 6.2–7.3; +X post bands 1.9–2.6 and 6.8–7.7.
- **Rear cell levels** (× 0.068, ground y 788): rails **2.8** (740–754) and **5.9** (694–708), each 0.95 tall; post bands
  2.3–3.3 / 7.1–8.4 (the +X post, left on screen) and 2.2–3.1 / 6.5–7.5 (the −X post); rail lashings at x px 590–603 and
  682–694 (build x ≈ +2.3 and −3.9); tips 532 : 632, **568 : 607 (post)**, 592 : 648, 622 : 640, 646 : 655, 666 : 669,
  686 : 660, **712 : 632 (post)**, 737 : 656.
- **Side cell:** one post square on with two bands (z ≈ 2.4 and 6.6), rail stubs projecting front and back at z ≈ 5.9
  (0.55 past the post faces: wood + rope depth 47 px = 2.96 studs), banner edges on **both** faces (§3.4), rocks and
  rosettes at the foot.
- **Verifier tolerance:**
  - front_sheet: timber + rope W : H **1.31 ± 0.05**; tip heights per §2.2 ± 0.3 (scored as the ordered skyline); rails
    and bands per §2.4 ± 0.25; shares W 73 ± 8, R 7.4 ± 3, B 7.4 ± 2.5, S 3.7 ± 2, G 7.3 ± 3.
  - rear_sheet: timber + rope W : H 1.31 ± 0.05; two full rails at 2.8 and 5.9 ± 0.2; shares W 80 ± 8, G 6 ± 3.
  - side_sheet: timber + rope W : H **0.277 ± 0.03** (ours by construction 3.38 / 12.2; the sheet's 0.242 = 2.96 studs
    shows no lashing outside the stubs: recorded, §2.4); object 0.467 ± 0.08.
  - f34_sheet: obj W : H 1.235 ± 0.08, timber + rope 1.115 ± 0.08; W 73 ± 8, R 7.8 ± 3, B 6.1 ± 2, G 8.8 ± 4; wood lit /
    mid / shade 15 / 44 / 41 ± 10.
  - **Recorded, not scored:** the r34 (§3.2), the top cell's tip count and rock spread (§3.5), the side cell's rear
    banner edge (§3.4), the exploded parts' pointed feet (§3.6).

### 1.3 Silhouette and composition per view

**f34 (`z_f34.png`) — governs the read, the front rails, the banner and the dressing.** From the front-left (≈ 25–35°
round from the front toward −X, ≈ 15° up, mild perspective), the wall recedes to the right:
- at the left (near) end the −X **end log** (short, its side face lit), then the **−X post** with a fat rope band above
  the front rail and another near its foot; a short **rail stub** pokes out on the end log, left of the post, at rail
  height;
- the **front mid rail** runs from the −X post across five logs, lashed with three vertical turns at two of them, and
  disappears behind the banner's left half;
- the **banner**: a red swallowtail cloth with two thin white edge stripes and a white diamond in a diamond, hanging
  from a round rod with pale knob ends, in front of the logs between the tall banner log and the +X post;
- the **front upper rail** comes out from the banner's right edge one rail-height higher, passes the **+X post** under
  its upper band and ends on the far end log with a lashing;
- the tallest piece is the +X post (12.2), the next the banner log (11.5); tips are 8-faceted pale pyramids;
- rocks: a big one and a small one at the near end, one mid-front, a small one under the banner, a big one at the far
  end; two more behind the far end; lime rosettes between them along the whole foot.

**r34 (`z_r34.png`).** The same layout as the f34 (−X end at the left and near, the tallest post at the right) with the
stepped front rails and no banner; not a rear view (§3.2).

**Front view (`z_front.png`) — governs the X layout and the tip heights.** Twelve upright pieces edge to edge from x 41 to
306 px (§1.2): end log, **−X post**, four logs (the fourth a narrow short filler), two logs, the tall **banner log**, a
log, the **+X post**, a narrow filler, the +X end log. The mid rail (z 5.4) from the −X post's stub to the banner's left
edge, with lashings on the third and fifth pieces; the upper rail (z 7.1) from the banner's right edge past the +X post
to the end; the rod across the top of the banner (z 8.5) from the banner log to the +X post. Rocks: six (1.0–1.7 tall),
rosettes between them.

**Side view (right) (`z_side.png`) — governs the depth.** The +X post square on (its two bands), the rail stubs either
side at z ≈ 5.9, the banner's edge on both sides (stylised, §3.4), rocks and rosettes at the foot.

**Rear view (`z_rear.png`) — governs the rear rails.** A true rear elevation (the tallest post at the left = +X): two
long rails at 2.8 and 5.9 from post to post, each lashed with two vertical turns ("II") at two logs (build x ≈ +2.3 and −3.9),
short stubs beyond both posts, both posts with two bands (the lower at the lower rail, the upper just above the upper
rail); three big rocks and rosettes. No banner.

**Top view (`z_top.png`).** Content only: a single row of round pale tops (the end pieces and one near the right
larger), rail blocks along the bottom edge (front) and a stub at the upper right (rear), rocks at both ends front and back
and one mid-back, rosettes round them (§3.5).

**Exploded (`z_ex_l.png`, `z_ex_r.png`).** Loose perspective near hero scale; it governs part shapes, not sizes:
- **Palisade Log (uneven height):** octagonal chamfered logs (four broad faces, four narrow chamfers) with 8-faceted pale
  pyramid tips; one with a three-turn band low on the shaft, one with a band at mid-height; their feet drawn pointed
  (§3.6);
- a **short flat-topped log stub** with a band (the post's banded lower piece) and a **tall post** whose lower piece is
  drawn apart from it with its band (§3.7);
- **Horizontal Beam** ×2: square chamfered beams with three-turn rope bands near an end, their end faces lighter;
- a short **square block** (a rail stub);
- the **banner** (swallowtail, two edge stripes, double diamond) and its **rod** (round, pale knobs at both ends),
  arrows into the tall post;
- **Ground Rock (Stone)** ×3 (faceted, flat-bottomed, lavender-grey), **Foliage (Decorative)** ×3–4 rosettes.

**Close-up A ("Beam & lashing detail", `z_cu.png`).** A squared, chamfered log with a flat top above; a horizontal beam
coming in from the left, its end hidden under **three fat rope turns** round the log (read as the rail ending against
the turns, §2.4);
each turn chunky (≈ 0.3 of the log's width), with flat twisted facets, golden with darker grooves.

**Close-up B ("Post top detail").** The shaft's chamfered octagon and a pale **pyramid tip of broad facets** with a narrow
facet between each pair, about 0.7 of the width tall, with a slight rim where it meets the brown shaft.

**Close-up C ("Base detail (underside view)").** From below: the beam's underside with a rope band, a log's **flat cut
bottom** and a **ground rock** beside / under it, rosettes (§3.6).

**Palette and notes.** Six flat swatches (§5.1); the notes as above.

### 1.4 Parts (exploded, close-ups)

| Part (label) | Tone (median, lit, shade) | Shape |
| --- | --- | --- |
| Palisade Log (uneven height) | shaft `#B2682B`, lit `#E79642`, shade `#613B1D` (close-up A) | octagonal chamfered prism, flat foot, pale 8-faceted pyramid tip ≈ 0.7 Ø |
| Post (tall, banded) | shaft `#AF6524` (close-up B), tip `#F8B15E` | as a log, Ø 1.75, two three-turn bands |
| Horizontal Beam | `#B16827`, lit `#D48B3C`, shade `#884E1E` | square chamfered beam 0.90 × 0.70, pale end faces, rope lashings |
| Rail stub / square block | as the beam | a short beam end |
| Lashing Rope | band-box median `#D49951`, lit `#FCDD81`, shade `#A06228` | fat twisted turns, three per band |
| Banner + rod | red `#FC231F`, hem `#D41610`, emblem `#FEF9F9`; rod `#91531F`, knobs lit `#E8A356` | swallowtail cloth, two edge stripes, double diamond; round rod, knob ends |
| Ground Rock (Stone) | `#87838E`, lit `#B5AFB7`, shade `#4E5261` (exploded) | faceted chunky stone, flat bottom |
| Foliage (Decorative) | `#81B010`, lit `#BFE30E`, shade `#336018` | a rosette of 5–8 broad rounded leaves round a dark centre |

### 1.5 How 069 differs from the old kit (binding: the verifier checks these)

| | W12 `PalisadeWall` (old kit, exported) | **069** |
| --- | --- | --- |
| Size | 10.6 W × 4.7 D × 11.6 H; logs 7.4–9.1, posts 10.0 | **16.0 W (pitch) × 5.0 D × 12.2 H; logs 7.6–11.5, posts 10.3 / 12.2** |
| Logs | "uniform thin logs" r 0.55, round cones | **octagonal chamfered logs Ø 1.25–1.47 (fillers 0.70–0.80), 8-faceted pale tips 0.7 Ø** |
| Posts | flat-topped end posts | **pointed posts inset one log from each end, the tallest pieces, two three-turn bands each** |
| Rails | two rear beams | **two rear rails post to post + a stepped front pair, end stubs, seven lashings (2–3 turns)** |
| Tiling | none | **16-stud pitch, seams x ±8, identical end-log profiles, symmetric dressing, origin on the log line** |
| Colour | `w12_wood #8F5A2C`, one tan | **orange-brown timber `#AB6426` rendered, pale cut tips `#F8B15E`, golden rope, cool lavender-grey rock** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, log axes on y = 0). Kit camera azimuths: `front` az 0 (camera on
−Y), `side` az 90 (camera on +X, screen right = +Y), `rear` az 180; the f34 is about az −25 … −35, e 15 (camera at the
front-left, the −X end near).

### 2.1 The tile contract (binding; record it in the builder docstring and the export notes)

| Item | Value | Notes |
| --- | --- | --- |
| Pitch, seam planes | **16.00; x = −8.000 and x = +8.000** | half a 32-stud terrain cell (M040's pitch); nothing crosses a seam plane |
| Centre plane | **y = 0** (every log, filler and post axis; the two fillers set back to y +0.15) | the "consistent wall thickness" (§13.4) |
| Faces | **front −Y** = outside (banner, stepped front rails); **rear +Y** = inside (two full rails) | a run keeps one rotation |
| Ground | **z 0**: every log and post foot flat-cut on z 0; rocks flat-bottomed on z 0; rosette leaves rest on z 0 | no part below z 0 (decision §8.6) |
| End logs | **L1 and L11 identical in section: Ø 1.47 octagon, a broad face on the seam side, outer face at x = ∓7.995** | the same seam profile at both ends (M043 m4); a 0.01 slot between modules |
| End profile at the seams | only the end log's outer broad face comes within 0.3 of the seam plane: flat over y −0.55 … +0.55 (the chamfers beyond), z 0 → its shoulder (L1 7.27, L11 9.37), then the tip | any module meets any module (or a corner / gate) log to log |
| Rails and stubs | stop ≥ 0.70 inside the seams (outermost ends at x ≈ −7.20 / +7.30) | rails never bridge a joint |
| Rail levels (connector levels) | **rear RR1 z 2.80, RR2 z 5.90; front RF1 z 5.40, RF2 z 7.10**; section 0.90 H × 0.70 D; inner faces at \|y\| = 0.73 | corner and gate modules continue these levels |
| Dressing | rocks inside \|x\| ≤ 7.90, rosette leaf tips \|x\| ≤ 7.95; front reaches y −2.50, rear y +2.50 (±0.05) | symmetric, so the bbox centre is the log line |
| Origin | **bbox bottom centre = build (0, 0, 0)** (±0.02 in x, ±0.05 in y) | grid snapping and 90° turns need no PivotOffset (M040 / M043 lesson) |

- **How modules meet:** place modules every 16 studs along X with the same rotation. Module N's L11 (outer face
  +7.995) meets module N+1's L1 (outer face −7.995 of N+1) across a 0.01 slot: two Ø 1.47 logs side by side, like any
  two logs in the row. Across the joint the rhythm reads L11 (10.4) | L1 (8.3) between the +X post of N and the −X post
  of N+1, 5.42 apart (inside a module the posts are 10.58 apart): every joint becomes a short "post bay" without rails,
  the stubs stopping one log short of it. The dressing never collides (rocks 0.10 inside the seam).
- **Run ends:** a module's end log is a finished end, exactly as the sheet draws both ends: **no End variant** (decision
  §8.7). A Studio run may stop at either end.
- **Corner (contract for a later `StockadeCorner`; not on this sheet, decision §8.7):** it fills one 16 × 16 grid cell:
  a **corner post Ø 1.75 at the cell centre** (build (0, 0)), arm A of logs from the post to the seam x = −8 (log line
  y = 0), arm B to the seam y = +8 (log line x = 0); each seam shows the end-log profile above; rails on the inner side
  of the L (the quadrant between the arms) at the rear levels 2.80 / 5.90, butting the corner post under its bands. A
  straight module centred at (−16, 0) and one rotated +90° centred at (0, +16) then meet it exactly. One corner mesh
  serves every convex corner of a run that keeps its rear inside; a concave corner needs its own mesh (Roblox can't
  mirror a MeshPart).
- **Gate (contract):** a gate module fills one 16 slot with the end-log profile at both seams and the rear rails at
  2.80 / 5.90 butting its gate posts (Ø ≥ 1.75); clear opening ≥ 6.0 W × ≥ 8.0 H. **Interim:** the exported W12
  `DoubleGate` (15.02 wide) placed centred in a slot leaves 0.49 at each seam; record it, don't adapt it here.
- **Height variants** (W12 had Tall and LowBroken): same contract, change log heights only, never Ø or rail levels.

### 2.2 Timbers (front-cell order, −X → +X; every piece an 8-sided chamfered prism, axis vertical)

| Piece | Ø (across flats) | x range (centre) | Tip apex z | Shoulder z (tip 0.70 Ø) | Notes |
| --- | --- | --- | --- | --- | --- |
| L1 end log | 1.47 | −7.995 … −6.525 (−7.26) | **8.3** | 7.27 | seam log; carries the −X rail stubs |
| **P1 post** | **1.75** | −6.515 … −4.765 (−5.64) | **10.3** | 9.08 | bands z 2.10–3.10 and 6.40–7.50 |
| L3 | 1.25 | −4.755 … −3.505 (−4.13) | 8.0 | 7.13 | RF1 and rear lashings at its centre |
| L4 | 1.35 | −3.495 … −2.145 (−2.82) | 8.8 | 7.86 | |
| L5 | 1.25 | −2.135 … −0.885 (−1.51) | 8.9 | 8.03 | RF1 lashing |
| L6 filler | 0.80 | −0.875 … −0.075 (−0.475), **y +0.15** | 7.6 | 7.04 | a narrow short pole, recessed from the front |
| L7 | 1.35 | −0.065 … +1.285 (+0.61) | 9.5 | 8.56 | |
| **L8 banner log** | 1.45 | +1.295 … +2.745 (+2.02) | **11.5** | 10.49 | RF1 ends and RF2 starts on it; rear lashings at its centre; rod peg |
| L9 | 1.30 | +2.755 … +4.055 (+3.41) | 9.8 | 8.89 | behind the banner |
| **P2 post** | **1.75** | +4.065 … +5.815 (+4.94) | **12.2** | 10.98 | the tallest piece; bands z 2.10–3.10 and 6.60–7.70; rod peg |
| L10 filler | 0.70 | +5.825 … +6.525 (+6.18), **y +0.15** | 9.4 | 8.91 | narrow, recessed |
| L11 end log | 1.47 | +6.535 … +7.995 (+7.26) | **10.4** | 9.37 | seam log; RF2's outer piece and its lashing (x +6.95) |

- **Section:** an octagon of four broad faces (to ±X and ±Y) and four 45° chamfers, chamfer width **0.22 Ø** (the
  exploded logs' narrow facets; m064 `pole`'s section). Neighbours 0.01 apart (no coincident faces).
- **Tip:** an **8-facet pyramid** from the shoulder octagon to a centred apex, length **0.70 Ø** (±0.08 per log, seeded:
  hand-cut), the apex ±0.04 off-centre; a 0.04 chamfer rim ring at the shoulder (close-up B's rim). Pale by role (§5.3).
- **Foot:** flat cut on z 0 (close-up C "Log Bottom (flat cut)"); one ring at z 0.9 for the foot blend.
- **Straight and vertical**, no lean (tiling); the uneven skyline comes from the heights and tip lengths only.
- **Check against the sheet:** ordered skyline from −X: 8.3, **10.3**, 8.0, 8.8, 8.9, 7.6, 9.5, **11.5**, 9.8, **12.2**,
  9.4, 10.4 (front cell, ±0.3).

### 2.3 Stack (binding contact chain; every seat ≤ 0.03 unless stated)

| Piece | Rests on / against | Contact |
| --- | --- | --- |
| Logs, fillers, posts | the ground | feet on z 0.000 (±0.005) |
| Rails (main spans) | the logs they cross; at each end the post's chamfer face, or the post's band where a band is at the rail's level | inner face touching L8 (the proudest log crossed) ≤ 0.01; an end in a chamfer runs in until its inner edge is 0.03 into the chamfer (≈ 0.10 past the post's broad-face plane); an end at a band stops 0.03 into the band's outer rope surface |
| Rail stubs | as the span ends, on the post's other side; the end log behind | as the span ends; the −X stubs also 0.005 into L1 |
| Post bands (3 turns) | the post only (`hull_loop` round the post section, offset 0.16) | sink ≤ 0.05 into the post; each turn touching the next (≤ 0.03); no turn passes through a rail |
| Rail lashings (2–3 turns) | the rail: each turn an **open C-run** over the rail's three exposed faces, both ends carried on to sink 0.04 into the log face behind | ≤ 0.05 into the rail; both ends touching (`rope_ends_report`) |
| Rod pegs | the front faces of L8 and P2 | sunk 0.05 into the log (a stated seat) |
| Banner rod | the two pegs' tops | resting ≤ 0.01 |
| Banner cloth | the rod (hem wrapped round it) | hem touching the rod ≤ 0.02 |
| Rocks | the ground; the log / post faces they chock | flat bottoms z 0; within 0.03 of a log, nowhere > 0.05 into one |
| Rosette leaves | the ground; a neighbouring leaf, rock or log | each leaf's base on z 0 (≤ 0.02); tips may rest on a rock (≤ 0.03) |

### 2.4 Rails, stubs, bands and lashings

| Member | Section | Position (x; y; z centre) |
| --- | --- | --- |
| **RR1** rear lower rail | 0.90 H × 0.70 D (the side cell's stubs stand 0.55 past the post faces), 0.06 chamfer on the long edges, square ends (pale) | x ≈ −4.68 … +3.98 (ends against the lower bands, §2.3); y +0.73 … +1.43; **z 2.80** |
| **RR2** rear upper rail | as RR1 | x ≈ −4.865 … +4.165 (ends in the posts' chamfers); y +0.73 … +1.43; **z 5.90** |
| **RF1** front mid rail | as RR1 | x ≈ −4.865 (in P1's chamfer) … **+2.60** (ends on L8, behind the banner); y −0.73 … −1.43; **z 5.40** |
| **RF2** front upper rail | as RR1 | x **+1.45** (on L8, behind the banner) … ≈ +3.98 (against P2's upper band); y −0.73 … −1.43; **z 7.10** |
| Stubs (6) | as the rails, 0.60 long (RF2's outer piece 1.40) | RR1: ≈ −7.20 … −6.60 and +5.90 … +6.50 (against the lower bands); RR2: ≈ −7.015 … −6.415 and +5.715 … +6.315 (in the chamfers); RF1: −7.015 … −6.415; RF2: +5.90 … **+7.30** (against P2's upper band, on L11) |
| **Post bands** (4 × 3 turns) | rope Ø **0.36**, 5-sided twisted, closed turns, 8 points (`hull_loop` round the post's octagon, offset 0.16; outer surface at 1.215 from the axis) | P1 z 2.10–3.10 (RR1's ends stop against it) and **6.40–7.50** (clear of RR2's top 6.35); P2 z 2.10–3.10 (RR1's ends stop against it) and 6.60–7.70 (RF2's ends stop against it); turns 0.36 apart |
| **Front lashings** (2 × 3 turns + 1 × 2 turns) | rope Ø **0.28**, 5-sided, open C-runs (offset 0.12 off the rail faces) of 5 points (§2.3), vertical (in a plane x = const), 0.30 apart | RF1 three turns at L3 (x −4.13) and at L5 (x −1.51); RF2 two turns at x +6.95 (on L11, inside the outer piece's end at 7.30; the sheet's lashing sits at x ≈ +6.2 over the recessed filler, recorded) |
| **Rear lashings** (4 × 2 turns) | as the front | RR1 and RR2 at L3 (x −4.13) and L8 (x +2.02) (the rear cell's two "II" lashings) |

- RF1 and RF2 overlap on L8 between x +1.45 and +2.60 at different heights (RF1 top 5.85, RF2 bottom 6.65): a 0.80 gap,
  hidden by the banner in the hero, visible in the plain module as a lapped splice.
- The rails pass **behind the post faces** as drawn: each span ends at the post (in its chamfer, or against its band)
  and a stub continues on the other side, so from the f34 and the rear cell the post stands in front of a rail that
  seems to run through it, its band showing between the rail ends (§3.3; the rear cell draws the rail ending at the
  band). No rail is ever inside a post or a band beyond its 0.03 seat.
- Side depth: bands reach ±1.215, rails and stubs ±1.43, the lashings ±1.69, so the timber + rope depth is 3.38 (side
  W : H 0.277; the sheet 0.242, whose side cell shows no rope outside the stubs). Bands that wrapped the rail ends too
  (close-up A's reading) would add another 0.35 a side: not used.
- Rope colour by strand (`_groove`: one strand in four `rope_deep`), never by facing.

### 2.5 Banner (front, hero only; "optional and removable")

| Piece | Where | Size / notes |
| --- | --- | --- |
| Pegs (2) | L8 front face at x +1.92, P2 front face at x +4.66; tops z 8.35 | square 0.30 × 0.30, from 0.05 inside the log face out to y −1.95 |
| Rod | x +1.62 … +4.96, centre y −1.80, z 8.50 | 8-sided Ø 0.30 resting on the pegs' tops; pale knob ends Ø 0.42 (6 × 4 balls) |
| Cloth | plane y −1.80, x +2.22 … +4.42 (2.20 wide) | a closed 0.08 slab: the top hem wrapped half round the rod (z 8.35 … 8.65), straight sides down to the **two swallowtail points at z 1.95**, the notch apex at **z 3.25**; interior rows at z 6.4 and 4.4 with a ±0.05 wave in y |
| Emblem (front face only) | centred x +3.32, z 5.50 | a white **outer diamond ring** 1.30 W × 2.90 H (line 0.14), a red gap, a white **inner diamond ring** 0.70 × 1.55 (line 0.12), a red centre: closed 0.02 shells, 0.01 proud of the cloth |
| Edge stripes | 0.10 wide, 0.12 in from each long edge, from z 8.20 down to each point | white closed 0.02 shells |

- Clearances: the cloth's back face (y −1.76) ≥ 0.20 in front of RF2 (front face −1.43) and of P2's band (−1.23); the
  points (z 1.95) ≥ 0.8 above rock F5; the cloth ≥ 0.05 off both pegs.

### 2.6 Rocks and rosettes (chock stones and ground cover)

| Piece | Centre (x, y) | W × D × H | Notes |
| --- | --- | --- | --- |
| F1 | (−7.00, −1.52) | 1.60 × 1.50 × 1.70 | big, chocking L1 / P1 (front cell 1.3 × 1.7; the f34's near-end big rock) |
| F3 | (−4.05, −1.25) | 1.00 × 1.00 × 0.85 | small, against L3 |
| F4 | (−0.60, −1.35) | 1.30 × 1.20 × 1.20 | mid-front |
| F5 | (+3.60, −1.25) | 1.10 × 1.00 × 0.80 | under the banner |
| F6 | (+5.90, −1.50) | 1.60 × 1.50 × 1.70 | big, chocking P2 / L10 |
| B1 | (+5.70, +1.55) | 1.80 × 1.60 × 1.95 | rear big (the rear cell's left rock) |
| B2 | (−2.90, +1.50) | 1.90 × 1.50 × 1.70 | rear mid |
| B3 | (−6.70, +1.50) | 1.70 × 1.50 × 1.80 | rear −X end |
| G1–G4 front rosettes | (−5.40, −1.75), (−2.40, −1.75), (+1.00, −1.75), (+7.25, −1.75) | Ø 1.40 / 1.50 / 1.50 / 1.20, 0.55–0.80 tall | between the rocks (≥ 0.05 off their footprints); G3 left of the banner |
| G5–G7 rear rosettes | (+7.20, +1.75), (+3.40, +1.75), (−4.70, +1.75) | Ø 1.20 / 1.50 / 1.50, 0.55–0.80 tall | |

- Rock centres are starting values: move each in y until its inner face is within 0.03 of the log it chocks (logs'
  faces lie at |y| 0.625–0.875). The outermost rosette leaf tips set the |y| 2.50 extents at both faces.

- **Rock shape:** a chunky faceted block (m064 `stone`'s box with two broken top corners, or m053 `_rock`'s low kind),
  flat bottom, top facets sloping; no egg shapes.
- **Rosette:** five broad leaves (outline W / L 0.60, length 0.65–0.80) radiating at 72° ± 10° round the clump centre,
  each pitched up 25–40°, **folded 25° along its midrib** (no flat cards: STAGES' edge-on rule), its base on the ground;
  the inner ends meet over the centre (dark green by role). Leaves turned radially outward, never toward the cameras.
- Every rock top stays ≥ 0.30 below the rail above it (RR1 bottom 2.35; RF1 bottom 4.95).

### 2.7 Expected extents

- **Hero:** X −7.995 … +7.995, Y −2.50 … +2.50, Z 0 … 12.20 → **15.99 × 5.00 × 12.20**; bbox bottom centre at build
  (0, 0, 0).
- **Plain module (`StockadeStraight`):** X ±7.995, Y −1.69 … +1.69 (lashings), Z 0 … 12.20 → **15.99 × 3.38 × 12.20**;
  bbox bottom centre at build (0, 0, 0) (the front and rear lashings reach the same |y|).

### 2.8 Screen checks (floor hidden; `m.py` masks; probe and keep the best)

- **front_sheet (0, 0)** — governs the X layout and the skyline: the §1.2 front tolerances; tips in order (§2.2); RF1 at
  5.4 lashed at L3 and L5, RF2 at 7.1, the stubs at the −X end, the banner between L8 and P2 with the rod at 8.5; rocks
  F1 / F3 / F4 / F5 / F6 and the rosettes.
- **rear_sheet (180, 0)** — governs the rear rails: two full rails at 2.8 / 5.9, two-turn lashings at x −4.13 and +2.02,
  stubs past both posts, both posts with two bands; the tallest post at screen left.
- **side_sheet (90, 0)** — governs the depth: timber + rope W : H 0.277 ± 0.03 (sheet 0.242, recorded), the stubs either side, the post's two
  bands.
- **f34_sheet (−30, 15)** (probe az −20 … −40 × e 10 / 15 / 20; the sheet has mild perspective) — governs the read:
  obj W : H 1.235 ± 0.08, shares and value bands per §1.2; content per §1.3.
- **r34_sheet:** compare the sheet's r34 with our **f34 render with the banner hidden** (§3.2); content only.
- **top (0, 89.9)** — content only: one row of octagonal tips, the rails' blocks along the front edge and the rear,
  rocks and rosettes at both ends and mid.
- **Tiling shots:** three modules in a row (`tiling_front`, `tiling_f34`, `tiling_top`) and a `seam_cu` at a joint: no
  gap wider than 0.01, no overlap, both end logs meeting square, the stubs one log short of the joint.

### 2.9 Origin, pivot and stored points

- Origin at the **bbox bottom centre** (`K.check`); transforms applied; it must equal the build origin (§2.1): print
  the residual.
- Store on the hero and the plain module: `o["m069_offset"]` (build frame = object + offset; expected (0, 0, 0)),
  `o["m069_seams"]` (−8.0, +8.0 along local X), `o["m069_rails"]` ({"RR1": 2.80, "RR2": 5.90, "RF1": 5.40, "RF2": 7.10},
  inner faces ±0.73), `o["m069_pitch"]` 16.0. The Banner part stores `m069_hang` (the pegs' wall-face points).
- Parts: origin at their own bbox bottom centre.

## 3. View conflicts and resolutions

### 3.1 Sheet number
- **Evidence.** The header says "PAGE 73/132"; INDEX.md row 69 lists `069.png` as "Flintborn palisade wall study".
- **Resolution.** Our number is 069 (file name, keys `m069_*`). Note the header in the export notes only.

### 3.2 The "rear three-quarter" repeats the front
- **Evidence.** The r34 puts the short −X end log and its post at the left and near, the tallest post at the right, and
  the stepped pair of rails (a mid rail on the left, a higher one past the tall post) exactly as the f34 does, with no
  banner. A camera behind the wall would show the −X end on the right, as the rear cell does (tallest post at screen
  left), and the rear's two full rails.
- **Resolution.** The r34 is the front face redrawn without the banner: compare it with our f34 render with the banner
  hidden, content only. The rear face is governed by the rear cell (§3.3).

### 3.3 Rails: "beams on rear" (notes) vs rails on both faces (every view); rails drawn behind the posts
- **Evidence.**
  - Notes: "Horizontal beams on rear, lashed with rope". Rear cell: two full rails at 2.8 and 5.9 with two-turn lashings.
  - f34, front cell, r34 and top: one rail at 5.4 on the front from the −X post to the banner and one at 7.1 from the
    banner past the +X post. Side cell: stubs on both faces at 5.9. Exploded: two beams.
  - In the f34 and the rear cell the thick posts stand **in front of** the rails, with a stub showing on the far side;
    close-up A hides the rail's end under the post's rope turns.
- **Resolution (decision §8.4).** **Rails on both faces as drawn:** RR1 / RR2 on the rear (the structural rails, §13.4)
  and the stepped RF1 / RF2 on the front (the hero view's most visible construction). Each rail span ends in the post's
  chamfer and a stub continues past it, so the post reads in front of a rail that runs through it, without hidden
  geometry. Alternative: rear rails only (the notes): the front then shows bare logs and the f34 / front cells lose their
  lashed rails.

### 3.4 Side cell: the banner on both faces
- **Evidence.** Red edges hang on both sides of the post in the side cell; no other view shows a banner on the rear.
- **Resolution.** One banner, on the front. The side cell's rear red edge is a recorded miss (side B share ours ≈ 3 %
  against the sheet's 6.1).

### 3.5 Top cell: seven round tops
- **Evidence.** The top view draws seven tops in a row (the end pieces larger) with rails on the front edge.
- **Resolution.** Content only (tip row, rails, rocks, rosettes). Twelve octagonal tips are built (the front and rear
  cells count twelve and eleven).

### 3.6 Feet: pointed (exploded) vs flat cut (close-up C), standing on a rock (close-up C)
- **Evidence.** The exploded logs end in pointed or wedge feet; close-up C labels a "Log Bottom (flat cut)" resting on
  a "Ground Rock"; every assembled view shows the logs standing on the ground with rocks in front of the feet.
- **Resolution (decision §8.6).** **Flat-cut feet on z 0**; rocks are chock stones beside the feet, never under a log
  (a log on a rock would lift the module off its seam profile). The pointed feet are a recorded miss. Alternative: a
  0.8 pointed stake below z 0 (hidden in terrain; +8 tris a log; the bbox bottom moves to −0.8 and every module would
  need a PivotOffset).

### 3.7 The exploded post in two pieces
- **Evidence.** The tall post is drawn as a long upper piece and a short banded lower piece; another short flat-topped
  banded stub stands among the logs.
- **Resolution.** Both posts are single timbers; the lower band is the "foot lashing" the exploded draws separately.
  The flat-topped stub is read as a rail stub's partner, not a piece of its own. Recorded.

### 3.8 Rail levels and band heights differ per cell
- **Evidence.** Front cell: RF1 5.4, RF2 7.1; rear: 2.8 and 5.9; side stubs 5.9; the bands sit at or just above the
  rails in some cells (§1.2).
- **Resolution.** The levels of the governing cell for each face: front RF1 5.40 / RF2 7.10 (front cell), rear 2.80 /
  5.90 (rear cell); bands per §2.4. The side cell's front stub at 5.9 (ours 5.4) is recorded.

### 3.9 Pitch against the drawn ends
- **Evidence.** Both ends of the sheet's wall finish with a plain log one piece outside a post; nothing shows how two
  sections join.
- **Resolution (decision §8.1).** The module's end logs are its seam pieces (§2.1): two modules joined read as two
  adjacent logs, and a run end looks exactly like the sheet's end.

### 3.10 Rope swatch vs rendered rope
- **Evidence.** The Rope swatch is `#D6AF76` (36°, 0.45); the drawn rope renders more saturated and golden: band-box
  median `#D49951` (32°, 0.63), lit `#FCDD81`, shade `#A06228`.
- **Resolution.** Calibrate the rope on the rendered bands (§5.4); the swatch is the flat reference.

### 3.11 "Broad, flat-shaded faces, no fine texture noise" vs the drawn grain
- **Resolution.** No modelled grain or cracks. Per-log Tint 0.05, chamfers and the pale tips carry the "hand-built" read;
  a foot blend band; rope strands by role.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

1. `log(d, tip_z, tip_k, seed)` → one octagonal chamfered prism with the flat foot, a foot ring (z 0.9), a ring 0.25
   under the shoulder, the shoulder rim and the 8-facet pyramid tip. Check against the exploded logs and close-up B.
2. `post(d, tip_z, seed)` → as `log` with Ø 1.75 and rings at the band edges.
3. `rail(x0, x1, z, side)` → the chamfered 0.90 × 0.70 beam with pale end faces and one mid ring; `stub(...)` → the same,
   0.60 long. Their ends cut into the posts' chamfers or stop against a band (§2.3).
4. `band(post, z0, z1)` → three closed twisted turns (`hull_loop` round the post's octagon). Check against close-up A
   (the rail running in under the turns) and the side cell (bands narrower than the stubs).
5. `lashing(rail, x, turns)` → open C-runs over the rail's three exposed faces, ends sunk into the log behind.
6. `banner()` → pegs, rod with knobs, cloth slab with the hem round the rod, emblem rings and edge stripes.
7. `rock(c, size, seed)`, `rosette(c, r, seed)`.
8. **Hero `Stockade`** = the twelve timbers + rails + stubs + bands + lashings + banner + rocks + rosettes, placed by §2,
   one object of closed shells. **Variant `StockadeStraight`** = the hero without banner, rocks and rosettes (the tiling
   module). Then the contact, bury, rope-ends, winding, seam and pivot reports (§6, §2.1).
9. **Parts shot** (−30, 15) laid out like the exploded; **exploded shot**: logs apart, rails pulled back off both faces,
   the banner forward, rocks and rosettes below.

**Helpers to reuse** (import functions from committed builders, never their module constants; `m064` is committed in
25de7ce, so it may be imported as M043 imported M040, or copied as M068 did):
- **`m064`:** `pole` / `pole_section` (the 8-sided chamfered pole with a cut tip: the log and post prism; change the cut
  tip to a pyramid), `_oct_ring`, `_prism_y` (an 8-sided log along Y: the rail and rod, rotated), `_shell`, `_box`,
  `rope` (twisted rope tube), `hull_loop` and `_mitre` (a rope loop round a section hull at an exact offset: the post
  bands), `lashing` (two wraps + a V sling: the pattern for open runs with sunk ends), `_band`, `_groove` (strand roles),
  `stone` (a chunky block with two broken top corners: the rocks), `_glow_mats` (not needed), `contact_report`,
  `bury_report`, `pierce_report` (the banner slab against the rod and pegs), `rope_ends_report` (every open C-run
  touches at both ends), `placement_report`, `render_close_ups`, `render_spin`, `_recentre`, `_tint`, `_paint`, `_mix`.
- **`m048`:** `_solid` (closed shell from points and faces, flipped by volume), `_prism` (vertical prism with a
  chamfered top), `_box`, `_rect`, `_inset`, `_plank2d`, `_tube` (twisted rope tube with strand numbering), `_knob` (the
  rod knobs), `coil_path` / `coil`, `_catenary`, `_tri_ngons`, `shells_report`, `contact_report`, `winding_report`,
  `levels_report` (adapt: tips, rail levels, band levels), `_recentre`, `_make_plain`. Its `_bolt` is unused here.
- **`m050`:** `_peg` (round peg head on a face), `_rope` (three-ply rope with aligned rings), `_ply_keys` /
  `_colour_rope` (golden rope by spiral band), `wrap_path` / `wrap` (an 8-point ring round a square post), `_inside`,
  `_groups`, `buried_report`, `levels_report`.
- **`m052`:** `_ext` (straight prism of a 2D region with consistent winding: the cloth outline, the emblem rings),
  `_earclip`, `_slab` (ear-clipped prism of any simple polygon: the swallowtail cloth, the diamond rings), `_cells`,
  `_plank2d`, `_plank2d_yz`, `_post_solid` (square post with a chamfered cap), `wrap_path`, `_resample`, `_rope_groove`,
  `rope_tie` (a twisted ring round a post with a tail: the band pattern), `buried_report`.
- **`m053`:** `_square`, `chain` (rings along a polyline with mitred kinks: the C-run lashings), `cap`, `_rock` (a
  chunky angular rock with a flat base and height bands: the alternative rock), `blade` (an 8-tri folded leaf: the
  rosette leaf, widened), `tuft`, `base_dressing` (rocks guarded off the timbers), `contact_report`, `bury_report`.
- Also `m061` (committed, 0c1ea60): `leaf` and `hub` (a rosette of broad thick kite leaves round a hidden hub: the
  rosette's model, at five leaves); `m047`: `_Solids` (ray-parity inside test); `m038`: `contacts()`; `m040`: `_tiles`
  (copies of the hero at ±16 for the tiling shots: the same pitch) and its `tiling_f34` / `tiling_top` shots.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a long row of sharpened orange logs with an uneven pale-tipped skyline, two taller banded posts,
   lashed rails, the red banner on the right half of the front, rocks and lime rosettes along the foot.
2. **front_sheet / rear_sheet / side_sheet / f34_sheet / r34 (banner hidden) / top** per §2.8.
3. **Close-up renders:**
   - `lash_cu` on P2's upper band from the front-right, against close-up A: three fat turns hugging the post and RF2's
     end, the rail running out to the left.
   - `tip_cu` on P2's tip, against close-up B: 8 broad facets, the rim, the pale-to-brown step.
   - `base_cu` from low under RR1 at L3, against close-up C: the rail's underside, the lashing, flat-cut feet, a rock.
   - `banner_cu`: rod, knobs, pegs, hem, emblem, stripes and the swallowtail; the cloth clear of RF2.
   - `seam_cu` at a joint of two modules; `tiling_front`, `tiling_f34`, `tiling_top` (three modules).
   - `thumb`: the f34 at ≈ 140 px tall: skyline, bands, rails, banner emblem still read.
   - `spin`: az 0 / 45 / … / 315 at e 10: nothing floats, no see-through cloth, rosettes never flat cards.
4. **Counts:** floating 0; buried 0 (stated seats excepted); rope-end failures 0; winding errors 0; seam violations 0
   (no vertex past |x| 7.995); pivot residual ≤ 0.02.
5. **Scale shot:** a 5.5 marker in front of L3 and beside the rails (the W12 `PalisadeWall` beside it, if its object is
   in the work file).
6. **Rosette sweep** (STAGES): 5° azimuth steps, whole leaves within 15° of edge-on ≤ 10 % of leaf area.

### 4.3 Budget (hero under 4000, plan 3500–3850; decision §8.2)

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Logs and fillers (8-sided, foot ring, under-shoulder ring, rim, pyramid, foot cap) | 10 | 62 | 620 |
| Posts (rings at the band edges) | 2 | 94 | 188 |
| Rails (8-sided chamfered, one mid ring, pale end caps) | 4 | 44 | 176 |
| Stubs | 6 | 28 | 168 |
| Post bands (3 closed turns, 5 sides × 8 points) | 4 | 240 | 960 |
| Front lashings (3 / 3 / 2 open C-runs, 5 sides × 5 points + caps, 46 a turn) | 3 | 92–138 | 368 |
| Rear lashings (2 open C-runs) | 4 | 92 | 368 |
| Banner (cloth slab 60, emblem rings 64, stripes 24, rod 32, knobs 48, pegs 24) | 1 | 252 | 252 |
| Rocks (box with broken corners, 10–12 verts) | 8 | 20 | 160 |
| Rosettes (5 folded 8-tri leaves) | 7 | 40 | 280 |
| **Hero `Stockade`** | | | **≈ 3540; plan 3500–3850; ceiling 4000** |
| **Variant `StockadeStraight`** (no banner, rocks, rosettes) | | | **≈ 2850** |
| Parts | | | Log ≈ 62, Post (with its two bands) ≈ 600, Rail (one rail + a 3-turn lashing + a stub) ≈ 210, Banner ≈ 252, Rock ≈ 20, Rosette ≈ 40 |

- **Cut order if over:** rosettes 7 → 5, rocks 8 → 6, the rod knobs to 4-sided, front lashings 3 → 2 turns.
- **Headroom use** (only after every check passes, ≈ 250): a fourth turn on the post bands where the sheet's bands look
  taller (rear cell), a second ring under each tip for a softer pale-to-brown step.
- **Never cut:** a tip, a post band (three turns), a rail or a stub, the banner's emblem, the end logs' profile, the
  rope's 5 sides (a 4-sided rope read as a paper collar, M064 stage 1).
- **Why not more:** the module repeats along every fort wall, so it is held to the full-asset 4000 (not the README's
  8000 building ceiling); the plain variant, the one that tiles by the dozen, is ≈ 2850.

### 4.4 Shape targets (binding; check with `M.audit` and own bmesh code)

- Seams: no vertex of any shell past |x| 7.995 (+0.001); end-log outer faces flat at ±7.995 over y −0.55 … +0.55 and
  identical at both ends (the same section rings); module pitch 16.000.
- Tips per §2.2 ± 0.3 (posts ± 0.2); tip length 0.62–0.78 Ø; Ø per §2.2 ± 0.05; feet on z 0 ± 0.005.
- Rails: levels 2.80 / 5.90 / 5.40 / 7.10 ± 0.15; section 0.90 × 0.70 ± 0.05; inner faces |y| 0.73 ± 0.02.
- Rope: Ø 0.36 (bands) / 0.28 (lashings) ± 0.03; three turns per band, 3 / 2 per lashing.
- Banner: 2.20 × 6.55 (top 8.50, points 1.95) ± 0.15; emblem 1.30 × 2.90 ± 0.15; cloth 0.06–0.10 thick.
- Hero bbox 15.99 × 5.00 × 12.20 ± (0.01, 0.10, 0.2); plain module 15.99 × 3.38 × 12.20.

### 4.5 Stages 2 and 3

- **Stage 2:**
  - Every shell closed and manifold, **0 bowties**, 0 boundary, wire or loose elements; no zero-area faces; n-gons
    triangulated (the octagon caps, the cloth outline, the diamond rings).
  - **0 winding errors per shell** (parity ray test): the pyramid tips, the rail end caps, the C-run caps and the
    ear-clipped cloth and emblem slabs are where a reversed face slips in (044's wedge).
  - **Thin corners:** long rails, stripes and rope runs triangulate to small angles. Report the count under 3°, fail
    only under 0.3° (the M064 ruling 2).
  - Origin at the bbox bottom centre = the build origin (§2.9); transforms applied; stored points re-checked.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box, `sw2.py`)

| Swatch | Hex (HSV) | Use |
| --- | --- | --- |
| Wood (Main) | `#A96931` (28°, .71, .66) | every log, post, rail, stub, rod (`m069_timber`) |
| Wood (Secondary) | `#D8954D` (31°, .64, .85) | the pale cut tips, rail and stub end faces, rod knobs (`m069_timber_end`) |
| Rope | `#D6AF76` (36°, .45, .84) | bands and lashings (`m069_rope`); renders more saturated (§3.10) |
| Banner | `#EE2D29` (1°, .83, .93) | the cloth (`m069_banner`) |
| Rock | `#878391` (257°, .10, .57) | the chock stones (`m069_rock`): a **cool lavender grey** (B > R) |
| Foliage | `#74A91E` (83°, .82, .66) | the rosettes (`m069_leaf`) |

### 5.2 Rendered regions (`samp.py`, `samp2.py`; median / lit quartile / shade quartile)

| Region | Median | Lit Q | Shade Q |
| --- | --- | --- | --- |
| Timber, whole cell: f34 / r34 / front / side / rear / exploded | `#975722` (27°, .77, .59) / `#A35E22` / `#985822` / `#A56024` / `#9A5A23` / `#A05F23` | `#D38234` / `#D28132` / `#CD7E31` / `#D18434` / `#C97A2E` / `#D28335` | `#553116` / `#563216` / `#4D2D15` / `#663B1A` / `#533117` / `#61381A` |
| Log shafts: rear above the rails / close-up A log / close-up B post | **`#AB6426` (28°, .78, .67)** / `#B2682B` / `#AF6524` | `#D68436` / `#E79642` / `#D88435` | `#673C1C` / `#613B1D` / `#60391C` |
| Log feet: rear y 760–780 / front y 720–740 | `#7A4A1D` (29°, .76, .48) / `#935322` | `#AB6325` / `#BF702A` | `#472B14` / `#472B15` |
| Rails: rear upper / rear lower / front / close-up A | `#AE6727` / `#AB6526` / `#B26826` / `#B16827` | `#C7893C` / `#C1752D` / `#D48B3B` / `#D48B3C` | `#985820` / `#91511B` / `#9C591F` / `#884E1E` |
| Pale tips: front / rear / close-up B pyramid | `#FBBF68` (36°, .59, .98) / `#FCBF64` / **`#F8B15E` (32°, .62, .97)** | `#FEDF8D` / `#FEDC8B` / `#FEDD88` | `#CD8747` / `#D08646` / `#BC7E44` |
| Rope, band boxes: front −X post / rear four / close-up A turns | **`#D49951` (33°, .62, .83)** / `#CE8F48` / `#CF9048` | `#FCD87D` / `#FCDD81` / `#FDD57B` | `#9E5E26` / `#A06228` / `#9B6838` |
| Rope, lit strands only (restricted class) | `#FAD075` (41°, .53, .98) / `#FBD678` / `#FCD178` | `#FEE088` | `#B68751` |
| Banner: front / f34 / exploded / top hem / side | `#FC231F` (1°, .88, .99) / `#FC2420` / `#FA1B1B` / `#D41610` / `#BD120F` | `#FD2320` | `#D91F14` / `#F2231D` / `#E51313` / `#930907` / `#75100C` |
| Emblem white: front / f34 | `#FEF9F9` / `#FEF8F8` | `#FFFFFF` | `#FEF4F2` |
| Banner rod (front) | `#91531F` | `#E8A356` (knobs) | `#5C3318` |
| Rock: exploded / rear / front / f34 big / close-up C | `#87838E` (262°, .08, .56) / `#857D89` / `#7D7888` / `#6B697D` / `#8D848E` | `#B5AFB7` / `#A99FAD` / `#AEA5AF` / `#9F97A7` / `#A6A2A7` | `#4E5261` / `#535866` / `#4E505F` / `#555767` / `#63646B` |
| Foliage: f34 / exploded / rear | `#81AF12` (78°, .90, .69) / `#81B010` / `#729711` | `#C3E40F` / `#BFE30E` / `#C0E30B` | `#2E5216` / `#336018` / `#2C4111` |
| Foliage split (f34): lime leaves (h < 82, v > .7) / dark (h ≥ 90) | `#B3D80D` (71°, .94, .85) / `#2A5A18` (104°, .73, .35) | `#CDEB12` / `#418317` | `#93BE0D` / `#1A3915` |

- f34 foliage: 63 % of G pixels are the lime hue (h < 80), the rest the deep green.

### 5.3 How the colour works

- **One timber** for every log, post, rail, stub, peg and the rod. The f34's spread (lit 15 / mid 44 / shade 41) is
  lighting; the side faces facing away and the rails' undersides are darker on the sheet because of the light. Never
  paint a face darker because of where it points.
- **Per-piece Tint 0.05** (every log, post, rail its own seed): the log-to-log steps the sheet shows.
- **Pale tips (`m069_timber_end`, hard edge at the shoulder rim):** every tip facet of every log and post, the rail and
  stub end faces, the rod knobs and the pegs' end faces. **By role** (listed in the builder per member), not by normal.
- **Positional bands (blend partners, 3 steps):** each log's and post's foot (z 0 → 0.9) one step toward
  `m069_timber_deep` (the rear feet `#7A4A1D`); the shaft just under the shoulder (0.25) one step toward
  `m069_timber_end` (close-up B's slight rim) — or leave it hard if the rim reads better.
- **Rope:** `m069_rope` with one strand in four `m069_rope_deep` (`_groove`), never by facing.
- **Banner:** `m069_banner`; the top hem (the 0.3 under the rod) one step toward `m069_banner_deep`; emblem and stripes
  `m069_cloth_white` (hard).
- **Rocks:** `m069_rock`; top 30 % one step toward `m069_rock_light`, bottom 25 % toward `m069_rock_dark` (m053 `_rock`'s
  height bands; position, never facing).
- **Rosettes:** leaves `m069_leaf_light` (lime) on the outer 60 % of each leaf, blended to `m069_leaf` mid-leaf and
  `m069_leaf_dark` at the inner ends over the clump centre (role and position: the f34's lime rims and dark hearts).
- **Hues stay together:** timber 26–30°, s 0.74–0.80 rendered; timber_end 31–37°, s 0.55–0.65; rope 32–42°, s 0.50–0.65;
  rock cool grey h 240–290°, s 0.06–0.14, B ≥ R; leaf 70–85° lime, deep 95–110°.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m069_timber` | rear-cell shaft median **`#AB6426` ± 12** (swatch `#A96931`); f34 W median `#975722` ± 15 | 26–30°, 0.74–0.80 | logs, posts, rails, stubs, pegs, rod | rough 0.85 |
| `m069_timber_end` | close-up B tip median **`#F8B15E` ± 15** (tips `#FBBF68`; swatch `#D8954D`) | 31–37°, 0.55–0.65, lighter than timber | tips, rail ends, knobs | rough 0.8 |
| `m069_timber_deep` | rear feet `#7A4A1D` ± 12 | 26–30°, 0.74–0.80, v ≤ 0.50 | foot blend partner | rough 0.9 |
| `m069_rope` | band-box median **`#D49951` ± 15**, lit strands `#FAD075` | 32–42°, 0.50–0.65 | bands, lashings | rough 0.95 |
| `m069_rope_deep` | `#A06228` ± 12 (band shade) | 28–32°, ≥ 0.70 | one strand in four | rough 0.95 |
| `m069_banner` | front cloth `#FC231F` ± 12 (swatch `#EE2D29`) | 358–3°, ≥ 0.83 | cloth | rough 0.9 |
| `m069_banner_deep` | top hem `#D41610` ± 12 | 0–4°, ≥ 0.88 | hem blend | rough 0.9 |
| `m069_cloth_white` | emblem `#FEF9F9` ± 8 (rendered; start the key at `#F4EEEC` so it doesn't clip) | s ≤ 0.05 | emblem rings, stripes | rough 0.9 |
| `m069_rock` | exploded rock `#87838E` ± 12 (swatch `#878391`) | 250–290°, 0.06–0.14, B ≥ R | rocks | rough 0.9 |
| `m069_rock_light` | lit `#B5AFB7` ± 12 | as rock, lighter | rock tops (blend) | rough 0.9 |
| `m069_rock_dark` | shade `#4E5261` ± 12 | as rock, v ≤ 0.40 | rock feet (blend) | rough 0.9 |
| `m069_leaf_light` | f34 lime `#B3D80D` ± 12 | 68–76°, ≥ 0.90 | leaf outer parts | rough 0.85 |
| `m069_leaf` | f34 G median `#81AF12` ± 12 (swatch `#74A91E`) | 76–84°, ≥ 0.82 | leaf middles | rough 0.85 |
| `m069_leaf_dark` | f34 dark `#2A5A18` ± 12 | 100–110°, ≥ 0.70 | leaf inner ends, centres | rough 0.85 |

**Calibration warnings:**
- **Orange-brown timber, not red and not grey-brown** (W12 `#8F5A2C` read brown; W08): hue 26–30°, s ≥ 0.74 on the rear
  render; lit faces and the tips must not clip (M052 finding 4).
- **Pale tips must be a real step** (M050 finding 6): `timber_end` ≥ 40 units lighter than `timber` in G, but the lit
  tip facets ≤ v 0.99 without clipping to white.
- **Rope golden-amber, not lemon and not the pale swatch:** hue 32–42°, s ≥ 0.50 rendered; it must stay distinct from
  the tips (rope s ≥ tips' s; the rope's grooves darker).
- **Cool lavender-grey rock, not warm and not purple** (this sheet's own stone; 066 / 068 used warm grey for theirs): B ≥
  R by 0–20, s ≤ 0.16 on every rendered rock median.
- **Lime foliage, not olive:** leaf_light hue ≤ 76°, s ≥ 0.90; leaf_dark clearly darker (v ≤ 0.40).
- **Banner pure red, not orange:** hue 358–3°.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- Logs and posts: by height above the foot (foot band 0.9). Rocks: by height (top 30 %, bottom 25 %). Rosette leaves:
  by distance from the clump centre. Banner: by distance below the rod (hem 0.3).
- **Hard edges only** where materials meet: timber_end | timber (tip facets and end faces are separate faces by role),
  rope | timber, banner | white, leaf | rock / ground.

### 5.6 Texture (Tint) and finish

- **Tint:** 0.05 per log, post and rail (broad, per piece, never per triangle), 0.04 per rock, 0.03 per rosette, 0.02
  on the banner.
- **Finish:** all matte: wood 0.85, rope 0.95, cloth 0.9, rock 0.9, leaf 0.85; no metal, no emission.

### 5.7 Re-measure (final renders against the sheet, same masks)

- **Timber:** rear_sheet shaft median within 12 of `#AB6426`; f34 W median within 15 of `#975722`; f34 lit within 15 of
  `#D38234`, shade within 15 of `#553116`.
- **Tips:** `tip_cu` tip median within 15 of `#F8B15E`. **Rope:** `lash_cu` band median within 15 of `#D49951`.
- **Banner:** front_sheet B median within 12 of `#FC231F`; emblem white s ≤ 0.05.
- **Rock:** front_sheet S median within 12 of `#7D7888`, B ≥ R. **Leaf:** f34 G median within 12 of `#81AF12`; lime share
  of G 63 ± 15 %.
- **Shares and value bands** per §1.2.

## 6. Joins and contact (no floating pieces, no buried pieces)

- **Shells:** every log, post, rail, stub, rope turn, peg, the rod, each knob, the cloth, each emblem ring and stripe,
  each rock and each leaf is its own closed shell, all in one hero object.
- **Chain to the ground:** logs, posts → ground; rails → logs and posts; stubs → posts; bands → posts; lashings → rails
  and logs; pegs → L8 / P2; rod → pegs; cloth → rod; emblem → cloth; rocks → ground; leaves → ground.
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**. A shell floats if its nearest distance
  to every other shell and the ground is > 0.03, or if it doesn't chain to the ground. The new risks: the rail ends in
  the posts' chamfers (they float by ≈ 0.07 if cut square at the broad-face plane, §2.3); the stubs; the C-run lashing
  ends where a thin log leaves a 0.10 gap behind the rail; the rod on its pegs; the emblem shells on a waved cloth.
- **Buried shells:** nothing more than 0.05 inside anything beyond its stated seat (the pegs' 0.05, the rope's
  ≤ 0.05). Ray parity against the logs, posts, rails and rocks as solids after the final placement (`m047._Solids`).
  Where a band sits at a rail's level, the rail ends stop against the band (§2.3), or the turns pass through them.
- **Thin slabs hide pass-throughs** (M064): run `pierce_report` on the 0.08 cloth (the rod, the pegs, RF2) and on the
  0.02 emblem shells. Target 0.
- **No intersections between big pieces:** neighbouring logs 0.01 apart; the fillers at y +0.15 clear their neighbours;
  rails touch L8 and seat in the posts only; rocks touch the logs ≤ 0.03.
- **Rope ends:** every open C-run touches at both ends (`rope_ends_report`, worst gap ≤ 0.02).
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.
- **Winding:** 0 errors per shell, checked with a parity ray test, not only the signed volume.
- **Parts:** each exported part self-contained (the Post with its bands, the Rail with its lashing and stub, the Banner
  chained pegs → rod → cloth) and **square to its axes** (M050 finding 7).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing emissive, no light, smoke, dust or sparkle; the cast shadows are the illustration's.

- **Stage 5 (lighting): skip, and record why.** No emissive part; no Neon. Studio notes (Requires Manual Validation): the
  timber reads orange-brown in daylight; the pale tips read against the sky; the rails' undersides are dark by shadow,
  not paint.
- **Stage 6 (VFX): skip, and record why.** The banner is drawn hanging still; a cloth flutter would need a skinned or
  scripted banner in Studio, which the sheet doesn't ask for. 0 sockets (the export STATS line must report 0).
- **Collision (decision §8.8):**
  - **Hero `precise`** (PreciseConvexDecomposition): logs, rails, rocks solid.
  - **`StockadeStraight` `box`**: the tiling module's box is 15.99 × 3.38 × 12.2, so the rails can't be used as steps,
    nothing can be jumped over, and boxes meet flush at the seams. **Requires Manual Validation in Studio:** with the
    hero's `precise`, check that a default character can't climb from a rock (1.7) to RF1 (top 5.85) to RF2 (top 7.55)
    and over the 8.0 tips; if it can and the fort must be closed, use `box` on the hero too.
  - Parts: `StockadeLog` `box`; `…Post` `box`; `…Rail` `box`; `…Banner` `none`; `…Rock` `hull`; `…Rosette` `none`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched all names in `art/roblox/kit/**/manifest.json` and the repo text (`git grep`) for
Palisade, Stockade, LogWall, StakeWall, Fence, Rampart, Barricade, Gate, Wall:
- **W12:** `PalisadeWall`, `PalisadeWallBanner`, `…Beam`, `…GroundCollar`, `…Intact`, `…Log`, `…LowBroken`, `…Post`,
  `…Tall`; `Barricade*` (incl. `BarricadeStake`), `DoubleGate*`, `WallWalk*`. **W-sheets:** `TimberFence*`,
  `BlockWall*`, `CliffWall*`, `StoneGate*`. **M040:** `StoneCliff*` (its notes use the word "palisade").
  **M068 (decided):** `TimberCabin*`.
- **`Stockade`** (and every `Stockade…` name below), `LogPalisade`, `TimberPalisade`, `StakeWall` and `LogWall` occur
  nowhere in the manifests or the repo text; `PalisadeSection` appears in 9 repo files (avoid). No owned name is a
  substring of `Stockade…`.

| Object | Part | Why |
| --- | --- | --- |
| `Stockade` | hero: 10 logs, 2 posts, 4 rails, 6 stubs, 4 bands, 7 lashings, banner, 8 rocks, 7 rosettes | W12 owns `PalisadeWall*` |
| `StockadeStraight` | variant: the hero without banner, rocks and rosettes (the tiling module) | WorldModeling §12.2 / §13.4 modules |
| `StockadeLog` | "Palisade Log (uneven height)": one log (Ø 1.35, tip 8.8) | the label |
| `StockadePost` | the thick post with its two three-turn bands (P2, 12.2) | exploded, close-up A |
| `StockadeRail` | "Horizontal Beam": one rail (RR length) with a three-turn lashing and a stub | the label |
| `StockadeBanner` | pegs, rod, cloth, emblem ("optional and removable") | the notes |
| `StockadeRock` | "Ground Rock (Stone)": F1 | the label |
| `StockadeRosette` | "Foliage (Decorative)": one rosette | the label |

- Palette keys `m069_*` (§5.4). Collection `Kit/M069 Palisade Wall`. No sockets. Stored points `m069_offset`,
  `m069_seams`, `m069_rails`, `m069_pitch` (hero and variant); `m069_hang` (Banner).

**Decisions needed (a recommendation each):**
1. **Size and pitch (§1.1, §2.1):** **16-stud pitch (seams x ±8, M040's), log row on y 0, tips 7.6–12.2, posts 10.3 /
   12.2** (recommended: the front and rear cells' 1.31 elevation at the kit's tile pitch; the shortest main log clears a
   jump). Alternatives: 12 (logs Ø 1.0, the old row's "thin logs") or 20 (M043's pitch; 15-stud tips).
2. **Budget (§4.3):** **hero under 4000 (plan 3500–3850), the plain module ≈ 2850, every part under 1000**
   (recommended). Alternative: the README's 8000 building ceiling (not needed; the module repeats).
3. **Build frame and origin (§1.1, §2.9):** **front −Y = outside / banner, rear +Y = rails; symmetric dressing so the
   origin is the log line at mid-module, no PivotOffset** (recommended).
4. **Rails (§3.3):** **both faces as drawn: rear RR1 / RR2 full, front RF1 / RF2 stepped; spans end in the posts with
   stubs beyond** (recommended). Alternative: rear only, per the notes.
5. **r34 (§3.2):** **treat it as the front redrawn without the banner** (recommended); score content only.
6. **Feet (§3.6):** **flat cut on z 0, rocks beside the feet** (recommended). Alternative: 0.8 pointed stakes below
   ground with a PivotOffset.
7. **Variants (§2.1):** **build the hero and `StockadeStraight` now; End = the module's own end log; Corner and Gate as
   contracts for later sheets (W12 `DoubleGate` fits a slot meanwhile)** (recommended). Alternative: build a
   `StockadeCorner` now from the contract (≈ 2600 tris, no sheet to judge it against).
8. **Collision (§7):** **hero `precise` with a Studio climb check; `StockadeStraight` `box`; parts as listed**
   (recommended).
9. **Cameras (§2.8):** **`front_sheet (0, 0)` governs layout and skyline, `rear_sheet (180, 0)` the rear rails,
   `side_sheet (90, 0)` the depth, `f34_sheet (−30, 15)` (probe −20 … −40, e 10–20) the read; r34 against the f34 with
   the banner hidden; top content; close-ups `lash_cu`, `tip_cu`, `base_cu`, `banner_cu`, `seam_cu`, three tiling shots,
   `thumb`, `spin`; parts, exploded and scale shots. Floor hidden in every `*_sheet` render** (recommended).
10. **Exports:** **hero, `StockadeStraight` and six parts** (recommended). Alternative: hero and variant only.
11. **Colour (§5):** **orange-brown timber `#AB6426` rendered with pale cut tips `#F8B15E`, golden rope `#D49951`, red
    banner with a white double diamond, cool lavender-grey rock, lime rosettes with deep centres; by role and position,
    never by facing** (recommended).
12. **Name:** **`Stockade`** (recommended; W12 owns `PalisadeWall*`). Alternative: `LogPalisade`.

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **The old palisade's failures** (W12 / MODEL_PROGRESS row 90: "uniform thin logs (ref uneven thick trunks); few
   lashings"; CHECKLIST 6/10; its goals log: "tips too spiky", "boxy"). Logs Ø 1.25–1.47 with two narrow fillers, posts
   1.75; the ordered skyline of §2.2; 8-facet tips 0.62–0.78 Ø; 4 bands and 7 lashings.
2. **Rope that reads as flat collars or thin outlines** (M064 minor 1: Ø 0.22 against a 0.75 pole read thin; M048
   finding 1; M051 finding 1). Bands Ø 0.36 on a 1.75 post (close-up A: each turn ≈ 0.3 of the log's width at the
   sheet's scale), lashings Ø 0.28, **5-sided twisted** (a 4-sided twist read as a paper collar), separate fat turns.
3. **Rope loops sinking into chamfered timbers** (M064 stage 1: radial loops cut the corners and sank 0.12). Use
   `hull_loop`'s mitred offset round the post's octagon; the lashings as open C-runs over the rail's three exposed
   faces with sunk ends (a closed loop can't pass between a rail and the log it touches).
4. **Rails buried in, floating off or crossed by the posts' bands.** Spans and stubs end 0.03 into the posts' chamfers,
   or 0.03 into the band where a band is at the rail's level (§2.3); a square cut at the broad-face plane floats 0.07.
   Nothing inside a post or a band beyond 0.05; no band turn through a rail.
5. **Floating or buried pieces** (STAGES; 035 / 036; 046; M051 findings 2–3). Stubs, C-run ends, pegs, rod, cloth,
   emblem shells, rocks, leaves: count floating 0, buried 0; report the worst sink per kind.
6. **Seams that don't tile** (M043 m4: the seam rings differed by 0.16; M040 / M043 m3: uneven overhang moved the
   pivot). Identical end-log sections at ±7.995; nothing past the seams; dressing symmetric so the origin is the build
   origin; `seam_cu` and three-module tiling shots show no gap, overlap or step.
7. **Single-sided or see-through cloth** (Roblox culls back faces; M064 pitfall 2). A closed 0.08 slab; the spin proves
   it from behind and at grazing angles.
8. **The banner clipping the wall** — the cloth ≥ 0.20 in front of RF2 and the P2 band, ≥ 0.05 off the pegs;
   `pierce_report` 0.
9. **Flat leaf cards and edge-on rosettes** (STAGES; 054 / 057 / 058 / 063). Leaves folded 25° on the midrib, turned
   radially; the 5° sweep: whole leaves within 15° of edge-on ≤ 10 % of leaf area at every step.
10. **Colour by facing** (042 ruling; 054 m9). Tips pale by role, feet and rock bands by position, rope by strand;
    `K.check` facing correlation < 0.5 per material.
11. **Hard colour bands and confetti** (M051 finding 5; M052 finding 3). Foot, hem and rock bands blend over three steps;
    Tint per piece, never per triangle.
12. **Warmed or purple stone.** This sheet's rock is cool lavender grey (`#87838E`, B > R, s ≈ 0.08–0.12); don't copy 068's
    warm grey, and don't push it to violet.
13. **Egg rocks** (M034 / M037). Faceted blocks with broken corners and flat bottoms.
14. **Winding and non-planar quads** (044; M051 finding 8). 0 winding errors per shell (pyramid tips, end caps, C-run
    caps, ear-clipped cloth and emblem).
15. **Thin faces** (M064 ruling 2). Report corners under 3°, fail only under 0.3°.
16. **Proportions from stylised cells** (§3.2–§3.5). The front cell governs the X layout and tips, the rear cell the
    rear rails, the side cell the depth; the r34 is the front again; the top is content only.
17. **Tiny details that vanish** (WorldModeling §18). `thumb`: tips, bands, rails and the emblem readable; the knobs and
    stripes may vanish.
18. **A climbable wall** (gameplay): the rocks and front rails form a stair to the tips under `precise`; the Studio
    climb check is Requires Manual Validation (§7).
19. **Names and scope.**
    - No `PalisadeWall*`, `PalisadeSection`, `Barricade*`, `TimberFence*` names.
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit the frozen shared helpers (`kit_models.py`, `kit_mcp.py`, `build_kit.py`, `lib/vfx.py`) or other models'
      builders; import from the committed ones (`m038`, `m040`, `m047`, `m048`, `m050`, `m052`, `m053`, `m061`, `m064`);
      don't touch other models' collections.

## Open questions for the main session

1. **Pitch and scale (§1.1, §2.1):** is a 16-stud module (seams x ±8, the same pitch as M040's cliff tile) with tips
   7.6–12.2 and posts 10.3 / 12.2 the right size? Recommended: yes; the sheet's elevations give exactly a 1.31 W : H at
   that pitch, logs come out Ø 1.25–1.47 (not the old row's thin logs), and the shortest main log clears a jump.
2. **Rails (§3.3):** both faces as drawn (rear two full rails, front stepped pair; recommended) or rear only, as the
   modelling notes say?
3. **Variants (§2.1):** build only the hero and the plain tiling module now, with Corner and Gate as written contracts
   (recommended), or also a `StockadeCorner` now without a sheet to judge it? Use W12 `DoubleGate` (15.02 wide) in a
   16 slot meanwhile?
4. **Feet (§3.6):** flat cut on z 0 (recommended) or pointed stakes below ground as the exploded draws (needs a
   PivotOffset on every module)?
5. **Collision (§7):** hero `precise` with a Studio climb check and the tiling module `box` (recommended), or `box` on
   both so no wall is climbable?
6. **Budget (§4.3):** keep the hero under 4000 (plan 3500–3850) and the plain module ≈ 2850 (recommended), given that it
   repeats along every wall?
7. **Name:** `Stockade` (recommended; W12 owns `PalisadeWall*`) or `LogPalisade`?

## Decisions (main session, 2026-11-02)

1. **Pitch 16.00** (M040's tile), tips 7.6–12.2, posts 10.3 and 12.2, logs Ø 1.25–1.47; hero about 16.0 × 5.0 × 12.2.
2. **Rails on both faces** as the sheet draws them (rear 2.80 / 5.90, front 5.40 / 7.10).
3. **Build the hero `Stockade` and the plain tiling module `StockadeStraight` now;** Corner and Gate stay written
   contracts (a corner fills one 16 × 16 cell around a centre post; W12 `DoubleGate` fits one slot for now).
4. **Flat-cut feet on z 0,** not the exploded view's pointed stakes (recorded miss).
5. **Collision:** `precise` on the hero, with a Studio check that players can't climb the chock rocks and front rails
   over the tips; `box` on `StockadeStraight`.
6. **Budget:** hero under 4000 (it repeats along every wall), `StockadeStraight` about 2850; every part under 1000.
7. **Name `Stockade`.**
8. **Tiling contract as §-written:** seams at x = ±8.000 with nothing crossing, identical end logs meeting log-to-log,
   rails stopping ≥ 0.70 inside the seams, dressing symmetric front/back so no PivotOffset is needed.
9. **Sheet conflicts as resolved in §3:** the "rear three-quarter" is the front redrawn without the banner; the side
   depth difference from the lashings is recorded, not scored.
