# 051 Rope Crossing — spec

Reference: `art/blender/assets/references/051.png` (1024 × 1536 px). The sheet's title is "PAGE 52/132 | ROPE CROSSING"
(the printed 52 is the generator's number; INDEX.md row 51 calls it "Flintborn rope crossing model study"). The footer
reads "FLINTBORN — INDIVIDUAL MODEL STUDY".
Builder: `art/blender/kit/mcp/m051.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no water, glow or effect** (§7).

Sheet text:
- **Cells:** "1 ASSEMBLED FRONT THREE-QUARTER VIEW", "2 ASSEMBLED REAR THREE-QUARTER VIEW"; "3 ORTHOGRAPHIC VIEWS":
  "FRONT VIEW", "SIDE VIEW", "REAR VIEW", "TOP VIEW". The front, side and rear cells are level (no plank tops show);
  the top view is a plan with the long axis horizontal (no rotation needed when comparing).
- **Exploded:** "4 EXPLODED CONSTRUCTION": labels "End Post", "Hanger Rope", "Main Rope", "Rope Tie (Wrap)", "Anchor
  Stone", "Plank". Also drawn, unlabelled: four posts (two drawn split into a cap-and-shaft piece above a lower piece),
  two stones at the −X end and one wide stone at the +X end, four loose cube "peg blocks" beside the post feet at the
  deck ends, about 8 planks linked along their ends by short rope pieces, one main rope with knot collars and 7
  hangers, the red cloth on two posts, dashed drop arrows.
- **Close-ups:** "5 CLOSE-UP: POST JUNCTION" (two posts; rope coils under the caps, red cloth under the coils, a
  backstay from each coil down to a knot on the stone top, the main rope leaving to the right, a hanger with knots);
  "6 CLOSE-UP: PLANK & HANGER" (chunky planks with a deeper block at each end, short rope links between the plank ends,
  hangers knotted onto the plank ends); "7 UNDERSIDE VIEW" (from below: four planks with end blocks, a stone at each
  side).
- **Key parts:** "8 PARTS (ISOLATED)": "End Post", "Brace", "Peg Block", "Plank", "Main Rope", "Hanger Rope",
  "Anchor Stone".
- **Material palette:** "9 MATERIAL PALETTE": six labelled swatches "Timber Dark", "Timber Light", "Rope", "Stone
  Light", "Stone Mid", "Cloth Wrap" (§5.1). The header carries five unlabelled swatches (orange wood, tan, grey,
  green, blue).
- **Model notes:** "Modular, reusable parts." "Planks are individual pieces hung by separate ropes." "Ropes are
  cylindrical, tied with simple knots." "Posts sit on faceted stone anchors." "Clean, chunky geometry with broad
  flat-shaded faces." "Keep forms simple and readable."
- **Game context:**
  - **W08 owns the old kit's rope crossing** (`art/blender/scripts/kit/W08/rope_crossing.py`, goals
    `art/blender/renders/kit/W08/rope_crossing_goals.md`, manifest `art/roblox/kit/W08/manifest.json`):
    `RopeCrossing`, `RopeCrossingAnchorStone`, `RopeCrossingEndPost`, `RopeCrossingHangerRope`,
    `RopeCrossingMainRope`, `RopeCrossingPlank`, `RopeCrossingSideRope`, `RopeCrossingNarrow`, `RopeCrossingWide`,
    `RopeCrossingDamaged`; keys `w08_*`. It was built to an older drawing at 16 × 8 × 7.8 with a 3.4 deck and 14
    planks. Its lessons: stones "too small" and "rope thin" failed a verifier; it added "wooden end walls" and a "swag
    rope between the collars" for its side cell; its rope rendered "more saturated yellow than the reference's beige".
    Reuse the lessons, not its names or sizes (§8).
  - **M048 Dock** (verified 8/10, committed): the kit's first timber piece. Timber and rope family, deck 5.6, twisted
    rope tubes (`m048._tube`), its ruling's polish list (coils read as faceted octagonal collars; f34 rope gold share
    +2.7; 5-sided swags accepted).
  - **M050 Timber Bridge** (being modelled now, `m050.py` untracked): deck 5.6, the same family, this spec's model for
    structure.
  - **Kit levels:** ground 0; water top 1.0; M043 lower lawn 5.6, M040 / M043 upper lawn 10.4; M048's dock deck and
    M050's bridge deck 5.6.
  - WorldModeling §13.1–13.2 (timber vocabulary): squared timbers, posts stronger than rails, load-bearing parts
    first, "Rope rails are thick low-resolution curves/tubes with restrained sag. Do not model individual rope fibers".

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Paper `#FEFCF7` (tolerance
10). Cell rules found with `lines.py`: rows 445/446 (ortho top), 479/480 (ortho label rule), 663/664, 672/673
(exploded), 1052/1053, 1058 (close-ups), 1283, 1292 (parts row), 1491; columns 17/18, 332, 504, 764, 1007; the
close-up columns 325 / 332, 674 / 683; the parts row 570 / 576, 777 / 784. Titles and callout labels are painted out
(`TITLES` in `m.py`). Masks are `m.cls()` (HSV, h in degrees, in this order):
- **T** outlines / text: v < 0.16; or s < 0.25 and v < 0.35; or h 200–250, s > 0.25, v < 0.45 (the navy ink).
- **R** red cloth: h < 12 or > 340, s ≥ 0.45, v ≥ 0.35.
- **Y** rope (golden): h 36–62, s ≥ 0.18, v ≥ 0.60; or h 33–36, s 0.18–0.62, v ≥ 0.75. (M050's second rule had no
  minimum saturation; here it picked up the warm stone tops, so s ≥ 0.18 was added.)
- **W** lit wood: h < 40 (or > 345), s ≥ 0.35, v ≥ 0.62 (plank tops, caps, lit faces; **also the rope's amber
  strands**, §5.2).
- **K** dark wood: the rest of the wood hues, s ≥ 0.25, v ≥ 0.16 (post faces in shade, plank sides, undersides).
- **B** ground shadow: grey (s < 0.09), v ≥ 0.78, blue above red by ≥ 6. Excluded from shares. It also catches a few
  pale bluish stone faces (v ≈ 0.79), so S below reads a little low.
- **S** stone: the remaining greys (s < 0.25, v ≥ 0.30).
- **O** other.
- W / K is a **lit / dark** split, not a material split (one timber family, §5).
- Cells: f34 (18,125,571,442); r34 (572,125,1008,442); front (19,481,331,663); side (334,481,503,663); rear
  (506,481,763,663); top (766,481,1006,663); exploded (19,674,1006,1051); junction close-up (19,1059,324,1282);
  plank close-up (333,1059,673,1282); underside (684,1059,1006,1282); key parts (19,1293,569,1490). Header swatches
  (718,15,760,54), (776,…,818), (836,…,878), (895,…,938), (954,…,997); the §9 palette swatches x 591–637 / 654–700 /
  718–764, rows y 1336–1382 and 1412–1449.

**Scratch study material** (no Blender), in
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m051_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Pillow, numpy) and `< /dev/null`.
- **Helpers:** `m.py` (masks, boxes `V` / `X` / `TITLES`, `label`, `pxs`), `zoom.py` (crop with an optional sheet
  grid), `lines.py` (cell rules), `sw.py` (swatch boxes and hexes).
- **Measurements:** `measure.py` → `bb.json` and `cls_*.png` (bbox, W : H, shares, top profile, width per height,
  fifths); `runs.py <cell> col|row <coords>` (class runs: levels and widths); `deck.py <cell> x0 x1 y0 y1 [step]`
  (deck top / bottom and rope rows per column); `caps.py` (cap tops in the three-quarters); `persp.py` (pinhole fit
  to the f34 posts, §3.1); `keys.py` (key-part boxes); `proj051.py` (orthographic block model of the adopted layout
  at any camera, §2.7).
- **Colour:** `samp.py` (every region in §5.2), `samp2.py` (rope strands, caps, stone faces).
- **Zooms:** `z_f34.png`, `z_r34.png`, `z_f34_l.png`, `z_f34_lposts.png`, `z_f34_rposts.png`, `z_f34_deck.png`,
  `z_front.png`, `z_front_l.png`, `z_side.png`, `z_rear.png`, `z_rear_deck.png`, `z_top.png`, `z_top_l.png`,
  `z_expl_l.png`, `z_expl_r.png`, `z_cu.png`, `z_cu5.png`, `z_cu6.png`, `z_cu7.png`, `z_keys.png`, `z_keys3.png`.
- **On our renders:** `measure_render.py <render.png> [paper_hex]` prints bbox, W : H, all-class and timber+rope
  shares, profile, width per height, fifths and class medians with these masks. Self-test on the sheet's own front
  cell (`selftest_front.png`, title cropped) reproduces §1.2 within 0.2 points (W 19.2 / K 19.6 / Y 4.5 / R 0.1 /
  S 56.6; W : H 2.407 against 2.431).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a modular rope-and-timber suspension footbridge. Hero budget 4000 tris, each part
  under 1000. The plan in §4.3 lands at about 3860 (rope is about 60 % of it).
- **Overall read (check this first).** A **short sagging plank walkway slung between two pairs of tall square timber
  posts, each post standing on its own big faceted grey anchor stone**:
  - **four anchor stones** (one per post, in pairs at each end), light warm-grey, tapered, flat-topped, chunky, with
    vertical facet breaks, crack lines and loose rock chunks at their feet; they fill the lower half of the height;
  - **four square orange posts** on the stones, each with a wider **base block** at its foot, a slightly wider
    **cap block** with softened top edges and a dark peg hole, **two fat golden rope coils** under the cap and a **red
    cloth wrap** below the coils with hanging tails;
  - **a main rope along each side**, from a coil at one end to the coil at the other, sagging to about mid-post
    height, with **knot collars** where the hangers hang;
  - **vertical hanger ropes** from the main-rope knots down to the plank ends, and a **diagonal from each post** down
    to the end plank;
  - **ten chunky planks across the width**, each with a deeper **end block (lug)** at both ends, gaps between them,
    tilted to follow a **gentle sag** from the stone tops at each end down to mid-span, linked along both edges by
    **short rope pieces**;
  - a **backstay** from each post's coil down and outward to a knot on its stone's top;
  - a low **brace** between the two posts at each end, and four **peg blocks** at the post feet anchoring the edge
    ropes.
  - Hero shares (f34, all classes): W 22.6 %, K 23.8, Y 2.8, R 1.7, **S 49.0** (stone is half the picture). Timber +
    rope only: W 44.4, K 46.7, Y 5.4, R 3.4.
- **Focal silhouettes, in order:**
  1. The two big stone pairs at the ends, the four posts standing above them.
  2. The sagging plank deck between them, its plank ends forming a row of blocks, the main rope swooping above it
     with the hanger "fence" between.
  3. The coils, red cloth and backstays at the posts; the rope links and lugs along the plank ends.
- **Target: post centres 18.0 along (x ±9.0) × 6.0 across (y ±3.0); stone tops 5.6; post tops 11.0; deck top 5.6 at
  the ends, 4.5 at mid-span; overall about 26.0 L × 11.2 W × 11.0 H** (stone spurs to about 27.2 × 12.0).
  Tolerances: stone tops and the end planks' top outer edges 5.60 ± 0.02 (a seam level, §2.1); H ± 0.3; W ± 0.4;
  L ± 0.6. Decision §8.1.
  - **How it was derived.**
    - **The three-quarters can't set proportions.** A pinhole camera fitted to the four cap-top centres and four feet
      in the f34 (`persp.py`, rms 4.1 px) puts the posts 7.5 post-spacings apart along the span: the f34 draws each
      end's two posts almost side by side (across vector (47, 4) px) while its planks run steeply down-right (a plank
      is (69, 31) px long). Forced to L / W 3.0 the fit error rises to 10 px. The three-quarters are judged on content,
      composition and W : H (§2.7), not proportion.
    - **Height.** Front cell (H 122 px, post top y 523 → ground 645, scale 11 / 122 = 0.090 per px): stone top y 582
      (z **5.68**, fraction 0.516), base block 570–582 (1.1 tall), shaft, coil band 536–545 (z 9.02–9.83), cap 523–535
      (z 9.92–11.0). The stone top is set to the kit's **5.6** (lawn / dock / bridge deck) and the post top to **11.0**
      (0.98 of the 5.5 character above the ground, the posts 5.4 above the stone). The side cell gives stone 0.45 /
      post 0.55 (the side cell draws the post bases taller, §3.4).
    - **Along.** Front cell post centres x 69.5 / 280 → 210.5 px = **1.73 H → 19.0**; top cell post centres x 797 /
      973.5 → 176.5 px against across 60 px → **L / W 2.94**; front + side at one height scale → 3.37. Adopted **L 18.0,
      W 6.0 (L / W 3.0)**.
    - **Across.** Side cell post centres x 386 / 451 → 65 px against H 127 → **0.51 H → 5.6**; top cell plank length
      62 px against post centres 60 px. Adopted **W 6.0**, planks 6.2 long (y ±3.1).
    - **Sections:** post shaft 23.5 px front (0.19 H → 2.1), 19.5 px side (0.154 H → 1.7), 16 px of 60 across in the
      top (0.27 W → 1.6) → **1.6**; cap 25 px front → **1.7**; base block 24–25 px front, 1.3 × the shaft in the
      junction close-up → **2.0**; main rope 5 px → **Ø 0.45**; hangers 3 px → **Ø 0.26**; coils, two in a 9 px band
      → **Ø 0.42**; plank 13 px of 60 in the top → **1.15 wide**; plank-end blocks 14 × 11–13 px front → lugs 1.15 deep.
    - **Deck:** front cell deck top y 583 at the stone edges, **595 at mid-span** (bottom 607–608); rear cell 576–577
      / 596 / 607. Sag of the deck top **12.5 px = 1.1**: z 5.6 → **4.5**. Main rope centre at mid-span y 569 (front,
      rear 567) → **z 6.86**; at the posts it leaves the coil band at z ≈ 9.4.
    - **Stones:** front: top x 36–87 (51 px → 4.4 along), base x 26–100 (74 px → 6.3), post centre 5 px (0.4)
      inward of the stone centre; inner top edge x 87–96. Side: per stone top 36 px (3.3), base 45 px (4.2), gap 38 px
      at the top and 28 px at the ground (§3.2). Top: the pair's outline 58 × 103 px (5.8 × 10.3), merged, with a notch
      in the outer face.
  - **Why this size.**
    - **Against the character (5.5):** posts stand **5.4 above the stone tops** (head height); the walkway is **4.0
      clear between the base blocks**, 4.4 between the shafts and about 5.0 between the hangers (one character with
      room to pass); the main rope sits **2.1–2.4 above the deck at mid-span** (hip height: a real hand-line, unlike
      M050's ankle swags); planks 1.15 wide with 0.25 gaps; the sag is 1.1 over a 13.75 deck (max slope 17°, §2.1).
    - **Against the kit:** the stone tops and the deck ends are **5.6**: M043's lower lawn, M048's dock and M050's
      bridge deck. The crossing spans a **14.5-stud clear gap** between the anchor stones' inner faces (|x| 7.26),
      over ground or water at z 0 (stones on the plate, like the dock's legs), joining two 5.6 surfaces end to end.
- **Build frame (decision §8.2):** long axis **X** (the sheet's "FRONT VIEW" is the long side, and the kit's
  `front` camera then shows it), +Y back, ground z 0, centred on x 0 / y 0. **Symmetric about x 0 and y 0** except the
  cloth (§2.6). Stage 2 puts the origin at the bbox bottom centre (it stays at 0, 0, 0; record any offset).

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | W | K | Y | R | S | O |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (18,125,571,442) | 20–553 × 150–431 (534 × 282) | **1.894** | 22.6 % | 23.8 | 2.8 | 1.7 | 49.0 | 1.2 |
| Rear three-quarter (572,125,1008,442) | 560*–1001 × 151–424 (442 × 274) | 1.61* | 21.8 | 23.4 | 2.9 | 1.6 | 50.3 | 1.2 |
| Front (19,481,331,663) | 24–322 × 523–645 (299 × 123) | **2.431** | 19.0 | 19.4 | 4.4 | 0.1 | 57.2 | 0.1 |
| Side (334,481,503,663) | 351–479 × 521–647 (129 × 127) | **1.016** | 26.3 | 21.0 | 1.8 | 0.0 | 50.9 | 0.0 |
| Rear (506,481,763,663) | 512–755 × 523–645 (244 × 123) | 1.984 | 19.8 | 15.6 | 3.7 | 3.6 | 57.4 | 0.0 |
| Top (766,481,1006,663) | 777–994 × 532–635 (218 × 104) | 2.096 (L : W) | 41.5 | 20.7 | 0.7 | 0.0 | 37.2 | 0.2 |

\* The r34's left stone spills over the cell rule to x ≈ 560; `measure.py` stops at 572 (W : H 1.569 there).

- **Timber + rope only** (no stone): f34 W 44.4 / K 46.7 / Y 5.4 / R 3.4; r34 43.8 / 47.1 / 5.9 / 3.3; front 44.3 /
  45.3 / 10.3 / 0.1; side 53.5 / 42.8 / 3.7 / 0; rear 46.4 / 36.7 / 8.6 / 8.3; top 66.1 / 32.9 / 1.1 / 0.
- **The rope is mostly amber, not golden** (§5.2): on the sheet's isolated ropes only 20–31 % of the rope pixels
  class Y; 45–57 % class W and 16–35 % K. So the f34's Y (2.8 % of everything) is only the rope's golden highlights.
- **Verifier tolerance:** W / K ±6 (they split on value, so the studio light moves them); Y ±1.5; R ±1.0; S ±6 (the
  B / S split is approximate); W : H ±0.08 on f34, front and side; positions ±0.05.
- **Red:** none in the front and side cells, 3.6 % in the rear, 1.6–1.7 % in both three-quarters (§2.6, §3.6).

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .19 | .52 | .63 | .86 | .77 | .85 | .71 | .68 | .67 | .65 | .66 | .67 | .70 | .72 | .75 | .80 | .98 | .99 | .99 | .76 | .47 |
| r34 | .15 | .52 | .62 | .84 | .77 | .81 | .74 | .69 | .68 | .67 | .67 | .69 | .72 | .76 | .80 | .86 | .99 | .89 | .97 | .72 | .44 |
| Front | .05 | .52 | .64 | .99 | .93 | .77 | .72 | .69 | .65 | .65 | .63 | .65 | .65 | .69 | .71 | .77 | .81 | .99 | .98 | .53 | .04 |
| Side | .06 | .08 | .41 | .45 | .98 | .99 | .99 | .98 | .80 | .78 | .77 | .77 | .78 | .83 | .88 | .99 | .99 | .98 | .45 | .43 | .05 |
| Rear | .05 | .53 | .98 | .99 | .81 | .77 | .72 | .69 | .66 | .65 | .63 | .63 | .64 | .67 | .70 | .74 | .80 | .98 | .99 | .57 | .04 |

- **f34:** the near-left stone at f 0–.05 (low), the left posts at .15 and .25 (.86 / .85), the main rope dipping to
  .65 at mid-span, the right posts at .80–.90 (.98–.99), the right stone at .95–1.0.
- **Front / rear:** stones at both ends (.52–.64), the posts at .99, the main rope sagging to .63 at the middle.
- **Side:** two stones (.41–.45 at the outer quarters), two posts (.98–.99), the rope sag between them (.77, §3.5).

**Width per height** (fraction of W at h .05 → .95):

```
f34    .26 .49 .69 .97 .97 .93 .90 .84 .80 .13
r34    .27 .42 .63 .97 .99 .93 .89 .82 .18 .15
front  .99 .96 .95 .94 .93 .86 .81 .78 .80 .79
side   .98 .91 .89 .86 .77 .69 .65 .65 .69 .66
rear   .97 .96 .96 .95 .95 .89 .84 .82 .83 .82
```

**Fifths** (bottom → top, % of each class): f34 W 0 / 2.8 / 51.7 / 33.3 / 12.3; K 0 / 8.9 / 41.9 / 35.7 / 13.5; Y 0 /
0.6 / 28.8 / 56.5 / 14.2; R 0 / 0 / 0.8 / 58.9 / 40.3; S 24.5 / 39.3 / 28.3 / 7.1 / 0.7. Front W 0 / 13.1 / 32.0 / 36.4
/ 18.5; Y 0 / 1.3 / 24.1 / 60.4 / 14.2; S 39.1 / 36.3 / 20.1 / 3.4 / 1.1. Side Y 0 / 0 / 5.6 / 64.0 / 30.3.

**Level and size measurements** (sheet px; `runs.py`, `deck.py`, `caps.py`):

| Item | Front cell (long side) | Side cell (end) | Rear cell | Top cell | f34 |
| --- | --- | --- | --- | --- | --- |
| Post centres | x 69.5 / 280 (210.5) | x 386 / 451 (65) | — | x 797 / 973.5; y 553 / 613 (60) | cap tops FL (102, 194), NL (149, 197), FR (461, 155), NR (498, 156); feet FL (102, 285), NL (147, 314), FR (461, 237), NR (496, 245) |
| Post width | shaft 59–81 (23.5); cap 57–82; base block 59–83 | 19–20 (377–395 / 442–460) | — | caps 16 (791–807) | NL shaft 33 px, FL 33 px at +6 |
| Levels (y) | post top 523, cap bottom 535, coils 536–545, base block 570–582, stone top 582, ground 645 | post top 521, base blocks 563–591, stone top ≈ 590, ground 647 | same as front | — | — |
| Stones | top 36–87 (51), base 26–100 (74) / 250–317 at y 620; inner top edge 87–96 | 359–404 / 433–477 at y 630 (45 each, gap 28); 363–399 / 437–473 at y 595 (36, gap 38) | same | pair outline x 777–835, y 532–635; outer notch y 570–595, 10 px deep | near-left stone (40–260, 300–431) |
| Deck | top 583 (ends) → 595 (mid), bottom 607–608 (mid) | plank stack 592–612 between the stones | top 576 → 596, bottom 607 | 10 planks: x 811–819 (dark), 822–835, 840–853, 857–869, 872–884, 887–900, 904–916, 920–933, 937–950, 954–965 (dark); planks y 552–614 | about 10 planks, near-end lugs with pale peg dots |
| Deck ends | big blocks 14 × 11–13 px at x 112, 143, 172, 204, 234; small nodes at 127, 157, 187, 219 and 96 / 252 at the stone edges | — | big 585, 610, 636, 664, 687; nodes 570, 597, 621, 649, 675, 700 | rope with knots along both plank-end rows | — |
| Main rope | mid y 567–571 (Ø 5 px); knots at x 101, 128, 157 (and mirror) | sag drawn between the two coils, low y ≈ 550 | knots 574, 596, 622, 649, 674, 697 | over the plank-end rows | one per side, 7 hangers visible on the near side |
| Hangers / diagonals | 6 hangers (x 100, 127, 157, 187, 219, 250), Ø 3 px; a diagonal from each coil down-inward to (97, 582); a backstay down-outward to a knot at (50, 577) | — | 6 hangers | — | 7 near-side hangers; backstays to knots on the stone tops |
| Cloth | **none** | **none** | band + tails on both posts | none | on all four posts, below the coils |

### 1.3 Silhouette and composition per view

**Front three-quarter (`z_f34.png`, `z_f34_l.png`, `z_f34_lposts.png`, `z_f34_rposts.png`, `z_f34_deck.png`):
governs the read.** Camera at −X, −Y with strong perspective (the near-left post is 117 px tall against 91 px for the
far-left one). The −X end at the lower left, the deck rising to the +X end at the upper right.
- **Stones:** two at each end. The near-left one is huge in frame (to y 431), with a flat warm-lit top, cool shaded
  faces, vertical facet breaks and loose chunks at its foot; the far-left one sits behind it. At the +X end the pair
  reads as one broad block.
- **Posts:** four, each with a base block wider than the shaft sitting on the stone, a cap block with a peg hole, two
  fat coils right under the cap, red cloth below the coils with tails hanging part way down the shaft.
- **Rope:** the near main rope swoops from the left posts' coils down to mid-span and up to the right posts, with
  round knot collars at 7 hangers; each hanger drops to a plank end. A backstay from each coil runs down and outward to
  a knot on the stone top. A rope also runs between the two posts of each end at coil height (§3.5).
- **Deck:** ten planks laid across, upper left to lower right, each a chunky beam with a deeper end block (lug)
  carrying a pale peg dot; short rope links between the lugs; the deck rises from mid-span to the stone tops at each
  end. A pale blue-grey ground shadow under it (B, excluded).

**Rear three-quarter (`z_r34.png`).** The same composition from the other diagonal (the model is symmetric):
camera at +X, +Y. Both main ropes and both hanger rows show; red cloth on three posts.

**Front (`z_front.png`, `z_front_l.png`).** Level. Two stones with the posts on them, the coils, the main rope with
6 hangers and knot collars, the deck as a curved row of blocks (5 big plank-end blocks with small knot nodes between,
§3.3), a diagonal from each post to the deck end, a backstay to a knot on each stone top, **no red**.

**Side (`z_side.png`).** End-on: two separate stones with a gap between them down to the ground, two posts, a band
of timber between the posts at their base blocks (§3.4), the lower planks stacked below it between the stones, ropes
sagging between the coils (§3.5), **no red**.

**Rear (`z_rear.png`, `z_rear_deck.png`).** The mirror of the front, with red cloth bands and tails on both posts.

**Top (`z_top.png`, `z_top_l.png`).** Plan, long axis horizontal: ten planks across with gaps (the end two darker),
rope with knots along both plank-end rows, square caps with a peg dot, a timber with rope across between each end's
two posts at the post line, the stone pair as one outline per end with a notch in the outer face.

### 1.4 Parts (exploded (19,674,1006,1051), `z_expl_l.png`, `z_expl_r.png`; key parts (19,1293,569,1490), `z_keys3.png`)

The hero governs every size; the parts give shapes and boundaries. Key-part boxes from `keys.py`.

| Part | Box (sheet px) | Notes |
| --- | --- | --- |
| End Post | key (32,1337,77,1447) | A plain square post (W : H 46 : 111 in the iso), a dark **peg hole on top**, a small **peg on one face near the top**, a faint ring line near the foot; no coils or cloth on the key. Exploded posts are drawn as a cap + shaft piece over a lower piece, with coils and cloth |
| Brace | key (93,1369,158,1438) | A short **square-section beam** (about 2.2 × its section) with peg dots on top and on a face |
| Peg Block | key (168,1391,211,1430) | A **cube** with a peg hole on top and small pegs on two faces. Exploded: four loose cubes at the post feet, on the foot-rope line |
| Plank | key (223,1369,318,1443) | A long beam, section about 1 : 0.7, a faint lengthwise line on top, a peg dot near one end |
| Main Rope | key (321,1364,406,1423) | A thick twisted rope with a **knot collar near each end and round knob ends** |
| Hanger Rope | key (423,1328,446,1443) | A thinner twisted vertical rope with **knot nodes** at the top, a third of the way down and at the bottom |
| Anchor Stone | key (466,1350,558,1443) | A **tapered faceted block**, flat top with a dark **socket hole** at the centre, vertical facet planes, a loose chunk at its foot |

- **Junction close-up** (19,1059,324,1282): two posts; the shaft carries a **cap block** at the top and a **wider base
  block** at the foot; **two fat twisted coils** under the cap; a **red cloth** wrap knotted below the coils with two
  long tails; a backstay from each coil to a **knot on the stone top**; the main rope leaving at coil height; a hanger
  with knots.
- **Plank close-up** (333,1059,673,1282): chunky planks (top `#D77E36`, sides `#743817`), each with a **deeper end
  block flush with its end**, gaps about a third of a plank width; **short rope links with collars between the plank
  ends**; hangers knotted onto the plank ends.
- **Underside** (684,1059,1006,1282): four planks from below (`#783C1A`), each with an end block at both ends; a
  stone face at each side.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (long axis X, ±Y long sides, ground z 0). Builder constants (decision §8.4): `L = 18.0` (post
centres along), `W = 6.0` (across), `STONE_TOP = 5.6`, `POST_TOP = 11.0`, `NP = 10` planks, `PITCH = 1.40`,
`PLANK_W = 1.15`, `PLANK_T = 0.80`, `LUG_T = 1.15`, `SAG = 1.10`, `ROPE_LOW = 6.86`, `SINK = 0.02`.

### 2.1 The seam contract (binding; record it in the builder docstring and the export notes)

| Item | Value | Notes |
| --- | --- | --- |
| Ground | **z 0**, stone bases and spurs flat | a water tile's plate or ground |
| Walk surface at the ends | **stone tops z 5.6**, x ±7.26 … ±12.0, \|y\| 0.05 … 4.9 (the pair 0.10 apart at y 0) | flush with M043's lower lawn, M048's and M050's decks |
| Deck ends | the end planks' top outer edges z **5.58–5.60** at \|x\| 6.85 | 0.41 horizontal gap to the stone's inner face |
| Outer ends | stone outer faces x ±12.0 (top) → ±13.0 (base) | a 5.6 surface meets the outer top edge; the stone base and spurs may tuck into a terrace face below it |
| Sides | stones to y ±5.6 at the base | nothing past ±6.0 (spurs) |
| Post centres | (±9.0, ±3.0) | |

- **Walkability.**
  - **Deck:** ten separate planks, each tilted to the curve `z_top(x) = 4.50 + 1.10 (x / 6.875)²`. The steepest
    (end) planks lie at **16.3°**; the deck's end slope is 17.7°. **Seam steps ≤ 0.08** (end plank inner top edge
    5.263 against plank 2's outer top edge 5.186) across 0.25–0.29 gaps. Under the 0.35 limit everywhere.
  - **Ends:** stone top 5.60 → end plank top edge 5.585 (0.015 step) across a 0.41 gap. The **brace sill** at the
    post line is the one step up: **0.35** (§2.3, decision §8.5).
  - **Clear width:** 4.0 between the base blocks, 4.4 between the shafts, about 5.0 between the hangers' knots; the
    main rope 2.1–2.4 above the mid deck (hip height), 3.8 above the stone tops at the posts. Open above.
  - **What blocks a walk:** a rope across the end between the two posts (the side and top cells, §3.5) would hang at
    chest height above the walk. It is **left out** unless the main session decides otherwise (decision §8.6).
  - **Getting on from lower ground** (sand, banks 1.6–1.8, ground 0) needs a stairs / ramp piece, as for the dock and
    the bridge.
- **With M043 (lower lawn 5.6):** set the stone tops' outer edge (x ±12.0) against the lawn's front edge; the stones
  stand in front of the terrace face on the ground. Lawn to lawn across a 14.5 gap.
- **With M048 / M050:** turn the crossing so a stone pair's outer edge meets the dock's open end or the bridge's end
  board face; all at 5.6. The posts (y ±3.0) sit inside the dock's and bridge's post lines (±4.0).
- **With water tiles:** stones on the plate (z 0) in open water; nothing touches the water mesh.
- **With M034 (the stream tile):** its bank rocks and boulders fill any 26 × 11 footprint (M050 §2.1); not placed
  there as built.

### 2.2 Anchor stones and spurs

| Piece | Position | Size | Notes |
| --- | --- | --- | --- |
| Anchor stones S1–S4 | one under each post, centred about (±9.9, ±2.85) | **top** (z 5.6, flat): x \|7.26 … 12.0\|, y \|0.05 … 4.9\|; **base** (z 0): x \|6.8 … 13.0\|, y \|1.3 … 5.6\| | a convex faceted hull (`K.hull_rock`-style point rings, or own hull): ground ring, z 1.2, z 3.8, z 5.35 and the top ring. The **deck-side face stays vertical at \|x\| 7.26 from 5.6 down to 3.8** (clear of the end plank's lug, §2.4), then flares to 6.8 at the ground. The **cleft face** leans from \|y\| 0.05 (top) to 1.3 (ground): the pair nearly meets at the top (a 0.10 seam) and opens into a V gap below (the side cell's gap, §3.2). 2–3 vertical facet breaks per face (points jittered ±0.12). **Chamfer 0.25 on the outer top edges only** (outer x and outer y); the cleft and deck-side top edges stay sharp so the walk seams stay tight |
| Spurs | 2–3 per stone, on the ground against the outer and long faces | faceted chunks 0.9–1.8 wide, 0.8–1.6 tall | each touching its stone (overlap ≤ 0.05) and the ground; the f34's near-left stone shows the biggest cluster. Mirror-varied (different seeds) so the four stones are not identical |
| Socket | not modelled (hidden under the post) | | the key's top hole; record |

### 2.3 Posts, brace, peg blocks

| Piece | Position | Size | Notes |
| --- | --- | --- | --- |
| Base blocks (4) | centred on the posts | 2.0 × 2.0, z 5.58 → 6.70 | crisp box sunk 0.02 into the stone top |
| Shaft + cap (4) | (±9.0, ±3.0) | shaft 1.6 × 1.6, z 6.68 → 9.92; **cap 1.7 × 1.7, z 9.92 → 11.0**, 0.10 chamfer on the cap's top edges | one stepped prism shell per post (`_prism` levels), sunk 0.02 into the base block. A **dark peg-hole inset** (0.30 square, 0.03 deep) on the cap top. A **small square peg** (0.22 square, 0.10 proud) on the outer y face at z 10.4 (the key) — optional, cut order §4.3 |
| Brace sills (2) | the post line x ±(8.5 … 9.5), y −2.0 … +2.0 | 1.0 (X) × 4.0 (Y) × 0.37 (Z): **z 5.58 → 5.95** | ends sunk 0.02 into the base blocks' inner faces; bottom sunk 0.02 into both stone tops (spans the 0.10 seam). Two peg dots on top as inset squares (`peg`). The **0.35 step** onto the walk (decision §8.5) |
| Peg blocks (4) | x ±(7.31 … 8.02), y ±(2.30 … 3.20) | 0.71 × 0.90 × 0.80, z 5.58 → 6.38 | on the stone top beside the base block (outer face sunk 0.02 into it); a square peg (0.28 square, 0.10 proud, `peg`) centred on the span-facing face at z 6.10. Anchors the end ties |

### 2.4 Deck

- **Ten planks across the width**, centres x ±0.70, ±2.10, ±3.50, ±4.90, ±6.30 (pitch 1.40), **1.15 wide** (gaps
  0.25), **6.2 long** (y ±3.10), body **0.80 thick**, with a **lug at each end** (\|y\| 2.20 … 3.10) reaching **1.15**
  below the top: one closed prism of the 8-vertex U profile in the YZ plane, extruded along the plank's width. Ear-clip
  the non-convex caps (M050's notched-board rule).
- **Tilt:** each plank's top centre on `z_top(x)`, rotated about Y to the curve's slope at its centre (16.3°, 12.8°,
  9.3°, 5.6°, 1.9° from the ends in). Per-plank jitter: yaw ±1.0°, roll ±0.8°, height ±0.02 (the sheet's planks hang a
  little irregularly; keep the seam steps ≤ 0.10).
- **End plank clearance:** its outer bottom lug corner reaches \|x\| 7.175 at z 4.48; the stone's deck-side face at
  7.26 → **0.085 clear**. Check every plank and lug ≥ 0.05 clear of the stones (distance test).
- **Peg dots:** an inset square (0.26, 0.03 deep) on each lug's outer end face at mid-lug height, `peg` colour (the
  f34's pale dots). +8 tris per lug. No grain; the key's lengthwise top line is not modelled (§3.7).

### 2.5 Rope

All rope is twisted low-poly tube (`m048._tube`). **Use `twist=True` (each ring turned half a side, antiprism strips)
on the coils** (M048's ruling: aligned coil rings read as faceted octagonal collars), and on the main ropes and
hangers too.

| Piece | Path | Size | Notes |
| --- | --- | --- | --- |
| Coils (2 per post, 8) | rounded square round the shaft, centreline 0.99 from the post axis; centres **z 9.22 and 9.62** | Ø 0.42, 5 sides × 8 segments, twisted | inner surface sunk 0.02 into the shaft; the two touch; the upper coil's top (9.83) just under the cap (9.92) |
| Main ropes (2) | plane y ±2.75; ends at (±8.0, ±2.75, 9.42), sunk ≥ 0.15 into the coils on each post's span side; a catenary through **z 6.86 at x 0** | **Ø 0.45**, 6 sides, about 10 path rings | **knot collars** at each hanger: one fat ring Ø 0.70 in the same tube (no extra shell); a second ring per knot only if the budget allows |
| Hangers (16) | at x ±0.70, ±2.10, ±3.50, ±4.90 (planks 2–9), y ±2.75, vertical | Ø 0.26, 4 sides, twisted, 2.3–2.8 long | top end sunk 0.10 into the knot collar; bottom ends in a **knot bulge** (one ring Ø 0.42) seated on the lug top (sunk 0.03). One hanger per plank: "planks are individual pieces hung by separate ropes" (decision §8.7) |
| Diagonals (4) | from each coil's span side (±8.0, ±2.9, 9.1) down to the end plank's lug top (±6.3, ±2.75, 5.43) | Ø 0.30, 5 sides | bottom knot bulge on the lug (front cell: coil (82, 545) → (97, 582)) |
| Backstays (4) | from each coil's outer corner (±9.7, ±3.7, 9.2) down to a **knot knob** on the stone top at (±10.7, ±4.3) | Ø 0.36, 5 sides; knob Ø 0.6 (6 × 3, `_knob`) | knob sunk 0.03 into the stone top; the rope clears the base block (x > 10.0 at z 6.7) |
| Foot-rope links (18) | between neighbouring planks' lugs on each side at \|y\| 2.65, from lug face to lug face at mid-lug height | Ø 0.26, 4 sides, 1 segment | each end sunk 0.08 into its lug; length ≈ gap + 0.16 |
| End ties (4) | from the end plank's lug top (\|y\| 2.65, sunk 0.03) to the peg block's span-facing face at z 5.75 | Ø 0.26, 4 sides | clears the stone's top corner by ≥ 0.02 (never through stone) |

- **Rope parts:** `RopeBridgeMainRope` = one main rope (as the hero's, rebuilt between two points 8 apart) with the
  key's **knot collar near each end and round knob ends** (Ø 0.6). `RopeBridgeHangerRope` = one hanger, 3.0 long, with
  the key's three knot nodes.

### 2.6 Cloth

- **Where:** every post, **wrapped round its −X and +Y faces** (an L-shaped wrap round that corner) at **z 8.55 →
  9.00**, just under the lower coil, with **two tails** hanging from the corner to z ≈ 7.0 and a small knot lump. This
  is the only reading that matches every view (§3.6): the f34 sees red on all four posts (their −X faces), the rear and
  r34 see it on the +Y faces, the front (−Y faces) and side (+X faces) cells show none.
- **Geometry:** the wrap is a closed slab 0.08 thick, its inner face sunk 0.01 into the shaft; tails are tapered slabs
  0.45 wide × 0.08 thick with a notched (swallowtail) foot, hanging 0.02 off the shaft and touching the wrap; the knot
  a 0.40 × 0.25 × 0.35 lump. All closed shells, all chained to the post.

### 2.7 Expected extents and screen checks

- **Extents (build frame):** X −13.0 … +13.0 (stones; spurs to about ±13.6); Y −5.6 … +5.6 (spurs ±6.0); Z 0 … 11.0.
- **Self-consistency (`proj051.py`, orthographic block model):** front (0, 0) W : H **2.47** (sheet 2.431); side (90,
  0) **1.09** (1.016); top **2.27** (2.096). Three-quarters: (−20, 15) 1.89, (−15, 20) 1.81, (−25, 15) 1.84, (−25, 25)
  1.60.
- **Checks on the renders** (floor hidden, `measure_render.py`, the studio's paper colour as the second argument):
  - **f34_sheet (−20, 15)** (probe az −15 / −20 / −25 / −30 × e 12 / 15 / 20; a longer lens than usual is fine, keep
    the best):
    - W : H 1.81–1.97 (1.894);
    - shares W 22.6 ± 6, K 23.8 ± 6, Y 2.8 ± 1.5, R 1.7 ± 1.0, S 49.0 ± 6;
    - Y fifths within ±10 of §1.2 (0 / 0.6 / 28.8 / 56.5 / 14.2);
    - read: the −X stones big at the lower left, four posts with coils and red cloth, the main rope swooping low with
      hangers, ten tilted planks with lugs, backstays to the stones.
  - **r34_sheet (160, 18)** (probe az 155 / 160 / 165 × e 15 / 20 / 25): W : H 1.53–1.69 (≈ 1.61); R 1.6 ± 1.0.
  - **front_sheet (0, 0)** (−Y side): W : H 2.43 ± 0.1; two stones with the posts on them; the main rope low point at
    0.62–0.65 H; the deck top at 0.41 H at mid-span and 0.51 at the ends; **no red** (the −Y faces carry none).
  - **side_sheet (90, 0)** (+X end): W : H 1.02–1.15; two stones with the V gap below, two posts, the brace and the
    stacked planks between the stones; **no red**.
  - **rear_sheet (180, 0):** the front's mirror with red cloth on both posts.
  - **top (0, 89.9):** long axis horizontal like the cell; ten planks with the end two in shade, rope along both
    plank-end rows, caps with peg holes, the stone pairs with their outer notch. W : L about 0.43 against the cell's
    0.48.

## 3. View conflicts and resolutions

### 3.1 Proportions: the f34 (posts 7.5 spacings apart) vs the orthos (L / W 2.9–3.4)

- **Evidence:** §1.1. The f34's perspective is strong and its posts at each end are drawn nearly side by side; no
  camera fits them at a bridge-like ratio (rms 10 px at L / W 3.0 against 4 px free).
- **Resolution (decision §8.1):** **L 18 × W 6 from the front, side and top cells.** The three-quarters are judged on
  content, composition and W : H.

### 3.2 Stone pairs: separate with a gap to the ground (side cell, exploded −X end, key "Anchor Stone") vs one merged block per end (top cell, exploded +X end, f34 +X end)

- **Evidence:** the side cell's stones are 45 px each with a 28 px gap at the ground and 38 px at the top; the top
  cell's pair is one outline with only a notch in the outer face; the f34's +X pair and the exploded +X stone read as
  one block.
- **Why it matters:** the walkway between the posts (\|y\| < 2.0) runs straight over the gap between the stones. With
  the side cell's literal 3.4-wide slot at the top, nothing can be walked onto from the outer end.
- **Resolution (decision §8.3):** **four stones, paired so their tops nearly meet (a 0.10 seam at y 0) and their cleft
  faces lean apart below** (\|y\| 0.05 at the top → 1.3 at the ground), so the side view still shows two stones with a
  V gap and the top view a merged outline with an outer notch. **Alternative:** the literal slot (3.4 at the top;
  needs an extra landing piece to be walkable).

### 3.3 Deck count: 10 planks (top cell, f34) vs 5 plank ends + 6 knot nodes (front and rear cells) vs about 8 (exploded)

- **Evidence:** the top cell counts 10 planks with gaps; the f34 about 10; the front and rear cells draw an
  alternating row of 5 big blocks and 6 smaller nodes where the hangers land; the exploded about 8.
- **Resolution (decision §8.7):** **10 planks**, each with end lugs (the front's big blocks) and rope links between
  lugs (the smaller nodes read as the links and hanger knots). One hanger per inner plank (16) and a diagonal to each
  end plank. **Alternative:** 6 hangers per side at x ±1.3, ±3.9, ±6.4 (the front and rear cells), landing on the
  links between planks.

### 3.4 The end brace: a tall timber band between the posts (side cell, 2.3 tall) vs a member at the post line (top cell) vs the key's square beam

- **Evidence:** the side cell draws a band of timber y 563–592 between the posts at their base blocks (2.3 studs at
  the side cell's scale; W08 read it as an "end wall"); the top cell shows a timber with rope across between the posts
  at the post line; the key Brace is a square-section beam.
- **Why it matters:** the brace lies across the walkway at the entrance. A 0.8 square beam on the stone top is a 0.8
  lip; an end wall closes the crossing.
- **Resolution (decision §8.5):** **a low sill brace, 1.0 wide × 0.37 tall (a 0.35 step)**, at the post line, ends
  in the base blocks. The side cell's tall band and the key's square section are recorded misses. **Alternative:** the
  key's 0.8 × 0.8 beam (an 0.8 lip that must be jumped).

### 3.5 Rope across the ends (side cell sag between the coils; top cell rope at the post line; f34 rope between each end's posts) vs a walkable entrance

- **Evidence:** the side cell draws a rope sagging between the two coils to y ≈ 550 (z ≈ 8.4); the top cell a rope
  across at the post line; the f34 a rope from each far post's coil to the near post's coil at both ends.
- **Why it matters:** at z 8.4–9.4 it hangs 2.8–3.8 above the walk: chest height on a 5.5 character. Roblox collision
  on the hero (precise) would stop anyone walking on.
- **Resolution (decision §8.6):** **left out; both ends open.** Recorded as a visible miss in the f34, side and top.
  **Alternatives:** keep it as on the sheet (the crossing is then entered only by jumping), or keep it as a separate
  non-colliding rope object if the exporter supports that (main session's call).

### 3.6 Red cloth: all four posts (f34), both visible posts (rear, r34) vs none (front, side)

- **Resolution:** **an L-wrap on each post's −X and +Y faces with tails at that corner** (§2.6): it satisfies all six
  views. **Alternative:** a full band round every post (simpler and symmetric; red then shows in the front and side
  renders against the sheet's none).

### 3.7 Plank top line (key plank) and post split lines (exploded)

- **Resolution:** not modelled (a groove would read as twice the planks from above, and "broad flat-shaded faces").
  Per-plank tint carries the variation. The exploded post split (cap piece over a lower piece) is the cap block step
  and the base block, not a cut through the shaft.

### 3.8 End Post part: bare (key) vs with coils and cloth (exploded)

- **Resolution (decision §8.10):** the part is the **bare timber post** (base block, shaft, cap, peg hole, side peg)
  as the key draws it; the coils and cloth stay in the hero (the key lists "Rope Tie (Wrap)" separately in the
  exploded). **Alternative:** the post with its coils and cloth (M050's choice for its Post part).

### 3.9 Cast shadow

- The sheet's ground shadows are pale blue-grey (B). Render every `*_sheet` view with the studio floor hidden.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

All pieces are explicit low-poly solids (hulls, boxes, prisms, tubes). **No booleans are needed**: every piece is its
own closed shell, touching or sunk 0.02 into what carries it.

**Helper reuse (decision §8.11).** `m048.py` is committed: import `_solid`, `_prism`, `_box`, `_rect`, `_tube`,
`_knob`, `_catenary`, `_tri_ngons`, `winding_report` (and `contact_report` / `shells_report` if they fit) from `m048`,
as M050 does. Never import M048's or M050's constants; never edit `m048.py`; don't import from `m050.py` (untracked,
in flight). Stones: `K.hull_rock` takes ellipse rings; the anchor stone's straight faces want an own hull of explicit
points (bmesh `convex_hull`) — use whichever gives the vertical deck-side face and the leaning cleft face.

1. `stone(sx, sy, seed)` → one anchor stone (hull) + its 2–3 spurs. **Part `RopeBridgeAnchorStone`** = the −X / −Y
   stone with its spurs, compared with the key part (and the socket hole as a dark inset on top, the part only).
2. `post(sx, sy, seed)` → base block, shaft + cap prism, peg hole, side peg. **Part `RopeBridgeEndPost`** (bare,
   §3.8).
3. `coils(sx, sy)`, `cloth(sx, sy, seed)` → hero only.
4. `brace(sx)` → **Part `RopeBridgeBrace`**.
5. `peg_block(sx, sy)` → **Part `RopeBridgePegBlock`** (the key's cube with its peg).
6. `plank(i, seed)` → the U prism with peg-dot insets, placed on the curve. **Part `RopeBridgePlank`** = one level
   plank.
7. `main_rope(sy)`, `hanger(i, sy)`, `diagonal(sx, sy)`, `backstay(sx, sy)`, `link(i, sy)`, `end_tie(sx, sy)`.
   **Parts `RopeBridgeMainRope`, `RopeBridgeHangerRope`** (§2.5).
8. **Hero `RopeBridge`** = 4 stones (+ spurs) + 4 posts (base blocks, prisms) + 8 coils + 4 cloths + 2 braces + 4 peg
   blocks + 10 planks + 2 main ropes + 16 hangers + 4 diagonals + 4 backstays (+ knobs) + 18 links + 4 end ties.
   - Each piece a closed shell in one object; no unions.
   - `M.fix_bowties`; origin at the bbox bottom centre; transforms applied.
9. **Parts shot** (az −35, e 25), laid out like the key row: post, brace, peg block, plank, main rope, hanger, stone.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a sagging plank footbridge between two pairs of big grey anchor stones; four posts with fat
   coils and red cloth; two main ropes swooping to hip height with knots and hangers; ten tilted planks with lugs and
   rope links; backstays to the stones; open ends.
2. **f34_sheet, r34_sheet, front_sheet, side_sheet, rear_sheet, top** per §2.7.
3. **Level check (numbers):** stone tops 5.60; base blocks 5.58 → 6.70; post tops 11.00; coils 9.22 / 9.62; main-rope
   low point 6.86 ± 0.05; deck top 4.50 ± 0.03 at mid-span; end planks' top outer edges 5.58–5.60; brace top 5.95.
4. **Walk check:** a 5.5 marker on the stone top at each end, on the brace, on the end plank and at mid-span; the
   largest seam step and the end gaps printed (≤ 0.35 / ≤ 0.45).
5. **Junction extra** `junc_cu (−35, 18)` framed on the −X / −Y post against the junction close-up: base block on the
   stone, twisted coils, cloth, backstay to its knob, main rope and diagonal leaving the coils.
6. **Plank extra** `plank_cu (−30, 35)` on planks 2–5 at the −Y edge against the plank close-up: lugs, links, hanger
   knots on the lugs, peg dots.
7. **Underside extra** `under_cu (0, −60)` against the underside close-up.
8. **Scale and kit shots:** character markers; the crossing between two M043 lower lawns if they are in the kit file,
   from (45, 20).

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Anchor stones (hull, ~40 points) | 4 | ≈ 70 | 280 |
| Spurs | 10 | ≈ 14 | 140 |
| Base blocks | 4 | 12 | 48 |
| Shaft + cap prism (chamfer, peg-hole inset) | 4 | ≈ 40 | 160 |
| Side pegs on posts | 4 | 12 | 48 |
| Coils (5 sides × 8, twisted) | 8 | 80 | 640 |
| Cloth (wrap 32, tails 2 × 16, knot 12) | 4 | ≈ 76 | 304 |
| Brace sills (+ 2 peg insets) | 2 | 28 | 56 |
| Peg blocks + pegs | 4 | 24 | 96 |
| Planks (U prism 28 + 2 peg insets 16) | 10 | 44 | 440 |
| Main ropes (6 sides, 18 rings: ≈ 10 path rings + one fat knot ring per hanger) | 2 | ≈ 212 | 424 |
| Hangers (4 sides, 4 rings incl. bulge) | 16 | 28 | 448 |
| Diagonals (5 sides × 4) | 4 | 46 | 184 |
| Backstays (5 sides × 4) + knobs | 4 | 46 + 36 | 328 |
| Foot-rope links + end ties (4 sides × 1) | 22 | 12 | 264 |
| **Hero** | | | **about 3860** (limit 4000) |
| Parts: EndPost / Brace / PegBlock / Plank / MainRope / HangerRope / AnchorStone | | | ≈ 100 / 28 / 24 / 44 / 260 / 60 / 110 (limit 1000) |

- **The rope is the cost (about 2300, 60 %).** The margin is only about 140, so expect to use the first cuts. If the
  hero is over 3900, cut in this order:
  1. main ropes to 5 sides (−70);
  2. the post side pegs (−48) and the cloth knot lumps (−48);
  3. one spur fewer per stone (−56);
  4. the plank peg-dot insets (−160);
  5. hangers' rings 4 → 3 (−128).

  Never drop a coil (two per post), a hanger, a plank, a main rope, a backstay or a link; never take the coils below 5
  sides or untwist them.

### 4.4 Shape targets (binding; check with `M.audit` and own bmesh code)

| Target | Stones | Posts | Planks | Rope | Cloth |
| --- | --- | --- | --- | --- | --- |
| Section | tapered, flat top, big facets | shaft 1.6 square, cap 1.7, base 2.0 | 1.15 × 0.80, lugs 1.15 deep | round-ish, twisted facets | thin slabs (0.08) |
| Edges | 0.25 chamfer on outer top edges only | cap chamfer 0.08–0.12; others crisp | crisp | knots as fat rings | crisp |
| Not | no egg / blob boulders (M034 / M037), no rounded tops, no confetti facets | no taper, no rounded caps | no warp > 0.02, no grain, no groove | **not thin**: main Ø 0.43–0.47, coils 0.40–0.44, hangers ≥ 0.24; no fibres; no rope through a stone, plank or post | not floating off the post; not covering the coils |

- **Chunky, not skinny:** posts ≥ 0.29 of the post spacing across; planks W : T 1.4–1.6; stones ≥ 0.5 of the total
  height; main rope Ø ≥ 0.08 of the post height above the stone.

### 4.5 Stages 2 and 3

- **Stage 2:** every shell closed and manifold; zero non-manifold edges and verts (`nonmanifold_verts` 0), boundary,
  wire and loose elements; no zero-area faces or n-gons (the plank U caps, the stone hull faces and the knot rings are
  the places to check); normals outward; **0 winding errors** in `build()`'s problems list (STAGES "Consistent
  winding"; the plank caps are non-convex: ear-clip, not a fan from vertex 0, and check each triangle against the
  face's normal); no corners under 5° on visible faces; stone tops planar at 5.60 ± 0.01.
- **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box, sd ≤ 1.3)

| Swatch | Box | Hex | HSV | Use |
| --- | --- | --- | --- | --- |
| Timber Dark | (591,1336,637,1382) | `#A8602E` | 25°, 0.73, 0.66 | flat paint of the posts, brace and peg blocks (renders as `#9D4D18` faces) |
| Timber Light | (654,1336,700,1382) | `#CE7A39` | 26°, 0.72, 0.81 | flat paint of the planks (renders as `#D87E34` tops) |
| Rope | (718,1336,764,1382) | `#E1C192` | 36°, 0.35, 0.88 | hue reference only; the rendered rope is golden and amber (§5.2) |
| Stone Light | (591,1412,637,1449) | `#BFBDBC` | 20°, 0.02, 0.75 | the stones' base key |
| Stone Mid | (654,1412,700,1449) | `#939398` | 240°, 0.03, 0.60 | the stones' lower band, spurs, cleft |
| Cloth Wrap | (718,1412,764,1449) | `#BF3E34` | 4°, 0.73, 0.75 | flat paint of the cloth (renders deeper and more saturated) |
| Header 1–5 | (718,15,760,54) … | `#B96F3C`, `#E1C194`, `#B0B2B6`, `#86A059`, `#2FA4CE` | | wood, rope, grey; **green and blue unused** (no moss, grass or water drawn) |

### 5.2 Rendered regions (`samp.py`, `samp2.py`; median / lit quartile / shade quartile)

| Region | f34 / r34 | front / side / top | keys / exploded / close-ups |
| --- | --- | --- | --- |
| Plank tops | **`#DA7E31`** (27°, .78, .85) / lit `#E88E3A` | top `#C8702C` (26°, .78, .78) | plank cu `#D77E36`; key plank `#CC7531` |
| Plank sides, lugs, undersides | K `#6B3413` (22°, .82, .42) | front plank-end blocks `#9D4B1B` | plank cu sides `#743817`; underside `#783C1A`; key peg block `#833E16` |
| Post faces | NL shaft **`#9D4A16`** (23°, .86, .62); FL (shade side) `#7C3B15` | front shaft `#9D4D17`, cap `#A9521A`, base `#9F501A` | junction `#9F5019`; key post `#9C4E1A`; key brace `#9C5525` |
| Cap tops | NL cap top `#A6521C` (lit `#B55D24`) | top-view caps `#BD6325` (0.94 of the plank tops beside them) | junction cap tops **`#DF813A`**, `#E1823E` |
| Rope, golden (Y) | f34 **`#F4C26A`** (38°, .57, .96) / lit `#FDDC7D` / shade `#DCA963`; coils `#F2C060` | | junction `#FAC562`; plank cu `#F8C05E`; key main `#F8C871`; key hanger `#F7BE64` |
| Rope, amber strands (W in rope) | | front main rope band `#D08F36` | junction hanger `#BC6D19`, backstay `#D5842A`, coils `#B25A1D`; key main rope `#D27D2D` |
| Rope class split | | | junction backstay Y 31 / W 54 / K 16 %; key main rope 20 / 45 / 35; junction hanger 19 / 57 / 24 |
| Cloth | f34 **`#98200F`** (7°, .90, .60) / lit `#C82E14`; right posts `#951E0E` | rear `#B2200F` / lit `#DF2710` | junction `#971D0F` / lit `#DC2E17` |
| Stone, lit tops | far-left top lit `#F3E8DB` | | junction stone top `#D6CAC0` (27°, .10, .84) / lit `#F2E8DC`; key lit `#E7DCD1` |
| Stone, faces | near-left faces `#C1B7AF`; r34 right stones `#A59F9F` | front **`#B9B1AC`** (23°, .07, .73); top `#BFB8B3` | exploded `#B1AAA8`; underside `#A09EA2` |
| Stone, shade | near-left `#8E8E98` (240°, .07, .60) / shade `#7A7F8E` | front shade `#9D9B9E` | key `#91919B`; underside shade `#858894` |

### 5.3 How the colour works

**Wood: one warm orange timber family, by role, never by facing — the M048 / M050 family, which the sheet agrees
with.** This sheet's plank tops (`#DA7E31`) are within 10 of M050's board tops (`#DE833B`); its post faces
(`#9D4A16`) sit between M050's f34 post (`#8A3D0A`) and front post (`#A64E13`).
- **Role:** planks `m051_wood` (Timber Light); posts, base blocks, brace and peg blocks `m051_wood_deep` (Timber Dark).
  The posts read **only a small step deeper** than the planks on the same facing (top-view caps 0.94 of the planks;
  the junction's cap tops equal the planks), much less than M050's step. The vertical faces of planks and posts
  render alike (`#9D4B1B` / `#9D4D17`); that is the light.
- **Position:**
  - **plank lugs** (the 0.9 at each end) blend 35 % toward `m051_wood_dark` (the f34's darker plank ends);
  - **base blocks** 15 % `wood_dark` (they sit in the stones' shade on the sheet);
  - **peg-hole insets** 100 % `wood_dark`.
- **Planks:** per-plank tint ±0.03; two or three planks 15 % `wood_deep`; one broad lighter field. No grain.
- **Not red:** plank key hue 26–29°, R − G ≤ 95; check the f34 plank-top median hue ≥ 26°.

**Rope: golden highlights over amber, by strand role.** On the sheet only a fifth to a third of the rope pixels are
golden (Y); the rest is amber and its shade. So `m051_rope` (golden) takes **2 strands of 5–6** and `m051_rope_dark`
(amber) the rest, with one strand blended 50 % between them — chosen **by the strand's index round the twist, never by
the face's normal**. That is a much larger amber share than M048's (half / half), which rendered +2.7 Y too golden.
Calibrate the split on the f34 Y share (2.8 % of all, 5.4 % of timber + rope).

**Cloth:** one deep vivid red, `m051_cloth`; the folds and tails' shade come from the light.

**Stone: warm light grey with a cooler mid grey low down, by position.** The sheet's lit faces are warm (`#C1B7AF`,
tops `#D6CAC0`), its shaded faces cool (`#7A7F8E`–`#8E8E98`): that split is the light. The key is the warm light grey;
`m051_stone_mid` blends in **by height** (40 % below z 1.2, 3 steps up to z 2.2), on the **spurs** (50 %) and in the
**cleft region** (\|y\| < 1.0, 30 %). Broad tint mottling; no confetti.

**Pegs:** pale gold `m051_peg` (the f34's lug dots and the key's pegs), paler and smoother than the rope.

### 5.4 Keys (start from M048's calibrated hexes for wood and rope; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are medians of unshadowed rendered regions, not swatches. `K.sample` kinds: `"brown"` for woods,
`"vivid"` for rope, pegs and cloth, `"stone"` for stones. **Start values:** `m048.PALETTE` (wood `#BB722E`, wood_deep
`#88491A`, wood_dark `#633D20`, rope `#F4CF80`, rope_dark `#99601A`; read them from the file at build time).

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m051_wood` | **`#D87E34`** plank tops (f34 `#DA7E31`, plank cu `#D77E36`) | 26–28°, 0.74–0.79, R > G > B | planks | rough 0.85, metal 0, low spec |
| `m051_wood_deep` | **`#9D4D18`** post faces (f34 NL `#9D4A16`, front `#9D4D17`, junction `#9F5019`); check cap tops near `#DF813A` / top view `#BD6325` | 22–25°, 0.82–0.87 | posts, base blocks, brace, peg blocks | rough 0.85 |
| `m051_wood_dark` | `#6E3514` (f34 plank sides `#6B3413`, plank cu `#743817`, underside `#783C1A`) | 20–23°, 0.78–0.84 | lugs 35 %, base blocks 15 %, peg holes | rough 0.9 |
| `m051_rope` | **`#F8C46A`** (f34 `#F4C26A`, junction `#FAC562`, key main `#F8C871`) | 37–40°, 0.54–0.62, value ≥ 0.94 | 2 strands per tube | rough 0.95, low spec |
| `m051_rope_dark` | **`#C8761F`** (junction hanger `#BC6D19`, backstay `#D5842A`, key main `#D27D2D`, coils `#B25A1D`) | 26–32°, 0.78–0.87 | the other strands (one at 50 %) | rough 0.95, low spec |
| `m051_peg` | `#F2CC80` (start from M050's peg `#F6D48E`; sample the f34 lug dots) | 38–43°, 0.40–0.50 | peg dots, pegs | rough 0.55, metal 0 |
| `m051_cloth` | **`#B42411`** (f34 `#98200F` / lit `#C82E14`, rear `#B2200F` / lit `#DF2710`) | 5–8°, ≥ 0.85 | cloth wrap, tails, knot | rough 0.9, low spec |
| `m051_stone` | **`#BCB5B0`** (front faces `#B9B1AC`, top `#BFB8B3`, near faces `#C1B7AF`); tops should land near `#D6CAC0` | 20–28°, 0.05–0.10 (warm light grey) | stones | rough 0.92, low spec |
| `m051_stone_mid` | `#939398` (swatch; the f34 shade `#8E8E98`, key `#91919B`) | 230–245°, 0.03–0.08 (cool) | lower band, spurs, cleft (§5.3) | rough 0.92 |

**Calibration warnings:**
- **Plank tops:** f34 W median within 12 of `#DA7E31`, hue 26–29°, sat ≥ 0.72. Not red (< 25°), not brown (value <
  0.78), not yellow-tan (> 31°).
- **Posts:** a small step deeper than the planks on the same facing (top render: caps 0.90–0.97 of the plank tops),
  not M050's big step.
- **Rope:** f34 Y share 2.8 ± 1.5 and Y median within 12 of `#F4C26A`; the amber strands read orange-gold, not brown,
  and the rope as a whole reads clearly lighter and yellower than the posts. Not cream (the swatch), not uniformly
  yellow (W08's miss).
- **Cloth:** reads deep red in the f34 (R share 1.7 ± 1.0), hue ≤ 8°, not orange, not pink.
- **Stone:** light warm grey on lit faces, cool mid grey in shade; the S share 49 ± 6 in the f34. Not blue-grey all
  over, not brown, not white.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Planks:** `wood` base; per-plank tint ±0.03; lugs 35 % `wood_dark` by position (the outer 0.9 at each end); 2–3
  planks 15 % `wood_deep`. Hard edges only between planks (each its own shell).
- **Posts:** `wood_deep`; per-post tint ±0.03; base blocks 15 % `wood_dark`; peg holes `wood_dark`.
- **Stones:** `stone` base; `stone_mid` by height (40 % below z 1.2, 3 steps to 0 % at z 2.2); spurs 50 %; the cleft
  region (\|y\| < 1.0) 30 %; per-stone tint ±0.03 and a broad noise field (scale ≈ 0.15) at 0.03.
- **Rope:** strand roles (§5.3); per-piece tint ±0.02.
- **Hard edges only** where materials meet: rope | post, cloth | post, peg | wood, post | stone, rope knob | stone.

### 5.6 Texture (Tint) and finish

- **Tint:** planks 0.03 per plank plus 0.02 at scale 0.3; posts 0.03; stones 0.03 per stone plus the noise field;
  rope 0.02 per piece; cloth 0.02; pegs none. **Never per-triangle confetti.**
- **Finish:** wood rough 0.85–0.9, metal 0, low spec; rope rough 0.95; pegs rough 0.55; cloth rough 0.9; stone rough
  0.92. No emission anywhere.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Shares** per §2.7; **colours** per the §5.4 warnings, in f34_sheet, front_sheet and top. `K.check` facing
  correlation < 0.5 on every material.

## 6. Joins and contact (no floating dressing)

- **Stones:** bases flat on z 0; spurs on the ground, each touching its stone (overlap ≤ 0.05); the two stones of a
  pair 0.10 apart at the top (no coincident faces, no overlap).
- **Posts:** base blocks sunk 0.02 into the stone top; shaft + cap prism sunk 0.02 into the base block; side pegs sunk
  0.03.
- **Brace:** ends sunk 0.02 into the base blocks' inner faces; bottom sunk 0.02 into both stone tops.
- **Peg blocks:** bottom sunk 0.02 into the stone top, outer face sunk 0.02 into the base block; pegs sunk 0.03.
- **Planks:** carried by their hangers (or diagonals) and links; **no plank touches a stone** (≥ 0.05 clear, §2.4);
  plank-to-plank gaps 0.25–0.29, no overlap.
- **Rope:** coils sunk 0.02 into the shafts and touching each other; main-rope ends sunk ≥ 0.15 into the coils; hanger
  tops sunk 0.10 into the knot collars and bottom bulges sunk 0.03 into the lug tops; diagonals the same; backstays
  sunk into the coils and ending in knobs sunk 0.03 into the stone top; links sunk 0.08 into both lugs; end ties sunk
  0.03 into the end plank's lug top and 0.08 into the peg block. **No rope passes through a stone, plank, brace or post.**
- **Cloth:** wrap sunk 0.01 into the shaft; tails touching the wrap; knot touching the wrap.
- **Chain to ground:** stones → ground; posts → stones; coils, cloth → posts; main ropes → coils; hangers → main ropes;
  planks → hangers, diagonals, links; end ties → peg blocks → base blocks; backstays → coils and stones.
- **Count floating shells before reporting** (STAGES; 035 and 036 failed round 1 on this): **0**. A shell floats if its
  nearest distance to every other shell and the ground is > 0.03, or if it doesn't chain to the ground. The planks are
  the new risk: each must touch its hanger or diagonal bulge **and** both neighbouring links.
- **Buried shells:** no knob, peg, link end, coil or cloth more than 0.05 inside a stone, post, plank or block beyond
  its stated sink (ray parity after the final placement, as STAGES asks; 046 had leaves inside a core). Spurs ≤ 0.05
  into their stone.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0 (hull vertices, knot rings, knobs).
- **Winding:** 0 errors per shell (the plank U caps, the stone hulls if built by hand, the cloth slabs and hand-listed
  boxes are where a reversed face slips in; 044's wedge back face).

## 7. Water, lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** sunlit timber, golden and amber rope, red cloth and light grey stone on white paper. **No
water, foam, glow, light, sparkle, dust, smoke or VFX callout.**

- **Water and foam: none in the model.** No `*water*` key, no foam mesh, no sockets.
- **Stage 5 (lighting): skip, and record why.** No emissive faces, no PointLight. Studio notes (Requires Manual
  Validation):
  - the planks read warm orange (not red), the posts a touch deeper, the stones light grey with cool shade;
  - the rope reads golden over amber, the cloth deep red;
  - **a character walks from a 5.6 surface onto a stone top, over the brace sill, down the sagging deck and up the
    other side** without jumping; the main ropes are hip-height hand-lines, not a guard (edge safety, if wanted, is a
    Studio-side invisible collider).
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** (The cloth could sway in a later Studio script; the
  sheet doesn't show it.)
- **Collision:** hero `precise` (the deck and stones walkable, the posts and rope solid); `RopeBridgePlank`,
  `RopeBridgeBrace`, `RopeBridgePegBlock` `box`; `RopeBridgeEndPost`, `RopeBridgeAnchorStone` `hull`;
  `RopeBridgeMainRope`, `RopeBridgeHangerRope` `none`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json` and the repo
text (`git grep`) for Rope, Crossing, Bridge, Plank, Suspension, Anchor, Brace, Peg:
- **W08** owns `RopeCrossing`, `RopeCrossingAnchorStone`, `RopeCrossingEndPost`, `RopeCrossingHangerRope`,
  `RopeCrossingMainRope`, `RopeCrossingPlank`, `RopeCrossingSideRope`, `RopeCrossingNarrow`, `RopeCrossingWide`,
  `RopeCrossingDamaged` (this sheet's own labels under the old kit's prefix), plus `Footbridge*`, `Dock*`,
  `GantryRopeLift*`, `RopeLift*`; keys `w08_*`.
- **M048** owns `TimberDock*` (keys `m048_*`); **M050** `TimberBridge*` (keys `m050_*`).
- Other names: `RuinLeanToWallAnchor`, `*Peg` (W10), `*Brace` (W11–W15), `*Plank` (W08, W12, W13, minecart).
- **`RopeBridge` and `m051_` occur nowhere** in the builders, the manifests or the repo text. (`.blend` contents were
  not decompressed; `M.mk` renames a clash to `<name>M051`, so check the built names once.)

| Object | Part | Why |
| --- | --- | --- |
| `RopeBridge` | hero: stones, posts, coils, cloth, braces, peg blocks, planks, ropes | W08 owns `RopeCrossing*`; parallels `TimberDock` / `TimberBridge` |
| `RopeBridgeEndPost` | "End Post": bare timber post (base block, shaft, cap, peg hole, side peg) | §3.8 |
| `RopeBridgeBrace` | "Brace": the end sill | §3.4 |
| `RopeBridgePegBlock` | "Peg Block": the cube with its peg | |
| `RopeBridgePlank` | "Plank": one level plank with its lugs | |
| `RopeBridgeMainRope` | "Main Rope": one rope with knot collars and knob ends | |
| `RopeBridgeHangerRope` | "Hanger Rope": one hanger with three knots | |
| `RopeBridgeAnchorStone` | "Anchor Stone": one stone with its spurs and socket | |

- Palette keys `m051_wood`, `m051_wood_deep`, `m051_wood_dark`, `m051_rope`, `m051_rope_dark`, `m051_peg`,
  `m051_cloth`, `m051_stone`, `m051_stone_mid` (§5.4). Collection `Kit/M051 Rope Crossing`. No sockets.

**Decisions needed (a recommendation each):**
1. **Size and crossing** (§1.1, §2.1, §3.1): **post centres 18 × 6; stone tops 5.6; posts to 11.0; deck sagging from
   5.6 at the ends to 4.5 at mid-span; overall about 26 × 11.2 × 11** (recommended: the front, side and top cells;
   the stone tops and deck ends meet M043's lower lawn, M048's dock and M050's bridge at 5.6, across a 14.5 clear gap
   over ground or water at z 0). Or post top 11.6 (the side cell's taller posts). A 10.4-level version is a parameter
   change (stones 10.4 tall), not built now.
2. **Build frame:** **long axis X, symmetric about both axes except the cloth** (recommended: the sheet's front view
   is the long side). Or long axis Y like M048.
3. **Anchor stones** (§2.2, §3.2): **four stones, paired with tops 0.10 apart and a V gap opening below; deck-side
   faces vertical to z 3.8; 2–3 spurs each** (recommended: walkable ends, still two stones in the side view). Or the
   side cell's literal 3.4 slot (not walkable without a landing piece).
4. **Builder parameters:** **`L`, `W`, `STONE_TOP`, `POST_TOP`, `NP`, `PITCH`, `SAG`, `ROPE_LOW` constants; build only
   the drawn version** (recommended).
5. **End brace** (§3.4): **a low sill, 1.0 × 0.37, top 5.95 (a 0.35 step)** (recommended: walkable). Or the key's 0.8
   square beam (an 0.8 lip).
6. **Rope across the ends** (§3.5): **left out; both ends open** (recommended: the crossing must be walked; a rope at
   chest height blocks the entrance). Or keep it as drawn (jump-only), or as a separate non-colliding rope if the
   exporter can mark one.
7. **Deck and hangers** (§2.4, §3.3): **10 planks (1.15 × 0.80, lugs 1.15 deep) tilted to the curve; one hanger per
   inner plank (8 a side), a diagonal from each post to the end plank, rope links between all lugs** (recommended: the
   top cell, the f34 and "planks are individual pieces hung by separate ropes"). Or 6 hangers a side as the front
   and rear cells draw.
8. **Rope construction** (§2.5): **twisted tubes everywhere (`twist=True`), coils 5 sides × 8, main ropes Ø 0.45 at 6
   sides with knot collars built into the tube, hangers Ø 0.26 at 4 sides** (recommended: answers M048's "faceted
   collar" finding). Or aligned rings with strand colouring (M048 as committed).
9. **Cloth** (§2.6, §3.6): **an L-wrap on each post's −X and +Y faces with two tails** (recommended: matches all six
   views). Or a full band round every post.
10. **End Post part** (§3.8): **bare timber post as the key** (recommended). Or with coils and cloth (M050's way).
11. **Helpers:** **import M048's geometry helpers (committed); never its or M050's constants; nothing from `m050.py`**
    (recommended).
12. **Colour** (§5): **M048 / M050 timber family by role: planks `#D87E34`, posts a small step deeper `#9D4D18`, lugs
    35 % dark; rope golden `#F8C46A` on 2 strands over amber `#C8761F`; cloth `#B42411`; stone warm light grey
    `#BCB5B0` with cool `#939398` low down; header green and blue unused** (recommended). Never by facing.
13. **Packaging:** **one hero object of closed shells (no booleans); seven parts as the key labels** (recommended).
14. **Comparison cameras** (§2.7): `f34_sheet (−20, 15)` governing (probe az −15 … −30 × e 12 / 15 / 20); `r34_sheet
    (160, 18)`; `front_sheet (0, 0)`; `side_sheet (90, 0)`; `rear_sheet (180, 0)`; `top (0, 89.9)`. Extras: parts
    shot, `junc_cu`, `plank_cu`, `under_cu`, the walk and kit shots. Floor hidden in every `*_sheet` render.
15. **Stages 5 and 6:** **skip both, recorded; no water, foam or sockets** (recommended).
16. **Collision** as in §7 (recommended).
17. **Budget** (§4.3): **4000 limit, plan about 3860; cut main-rope sides, small pegs and knots, a spur, the peg-dot
    insets, then hanger rings** (recommended).
18. **Names** as proposed: `RopeBridge*`, keys `m051_*`.

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **Floating or buried pieces** (STAGES; 035 and 036 round 1; 046's leaves inside a core). The planks are hung, so
   each one must touch its hanger or diagonal bulge and both links; no plank may rest on or cut into a stone. Coils
   hug the shafts, knobs sit on the stone tops, links enter the lugs, cloth hugs the shaft. Count floating shells:
   **0**; buried beyond the stated sinks: **0**.
2. **Inward faces / broken winding** (044's wedge back face; STAGES "Consistent winding"). The plank U caps are
   non-convex: ear-clip them and check every triangle. The stone hulls, cloth slabs, pegs and hand-listed boxes: 0
   winding errors per shell, checked with a parity ray test, not only the signed volume.
3. **Rope that reads as thin outlines** (W08's rope; M034's foam outlines). Main ropes Ø 0.45, hangers ≥ 0.24; knots
   as fat collars; the hanger "fence" must read as rope, not wire.
4. **Coils that read as faceted collars or washers** (M048's finding 1). Twist the coil rings (half a side per ring),
   5–6 sides, fat (0.42), two distinct wraps; compare `junc_cu` with the junction close-up.
5. **Rope too golden** (M048: f34 Y +2.7; W08 "saturated yellow"). The sheet's rope is mostly amber with golden
   highlights: 2 golden strands of 5–6, calibrate on the f34 Y share 2.8.
6. **Wood that reads red, brown or flat orange** (W08 "slightly red" / "flat orange"; 012's wood). Plank tops hue
   26–29°, sat 0.72–0.79, value ≥ 0.78; posts only a small step deeper; per-plank tint so the deck isn't one flat
   colour.
7. **Colour by facing.** The sheet's light tops and dark sides (and warm lit / cool shaded stone) are the light. Role
   (plank / post / strand) and position (lugs, base band, cleft) only; `K.check` < 0.5 on every material.
8. **Egg or blob stones** (M034 / M037 "egg boulders"). Anchor stones are tapered, flat-topped, big-faceted blocks
   with vertical facet breaks and crisp edges, not rounded boulders; spurs chunky, not pebbles.
9. **Proportions from the f34** (§3.1): its posts are drawn nearly side by side. The orthos set L / W 3.0.
10. **A closed entrance** (W08's "end wall"; the side cell's end swag). The brace is a 0.35 sill and no rope crosses
    an end, unless the main session decides otherwise; the walk check (§4.2) must pass.
11. **Budget.** The rope is about 60 % of the count and the margin is about 140. Follow the cut order in §4.3; never drop a coil, hanger,
    plank, main rope, backstay or link.
12. **Names and scope.**
    - No `RopeCrossing*`, `Footbridge*`, `Dock*`, `RopeLift*` (W08); no `TimberDock*` (M048) or `TimberBridge*` (M050).
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit other models' builders, `kit_models.py`, `kit_mcp.py`, `build_kit.py` or `lib/vfx.py` (frozen).

## Decisions (main session, 2026-10-29)
All 12 recommendations are accepted.
1. **Size.** Post centres 18 along × 6 across. Stone tops at 5.6, post tops at 11.0. The deck sags from 5.6 to 4.5 at mid-span. The main rope's low point is at about z 6.86. The bridge crosses a 14.5-stud gap between 5.6 surfaces.
2. **Orientation.** Long axis on X, symmetric except the cloth.
3. **Stones.** Four stones, with paired tops 0.10 apart over a V gap, so the ends stay walkable. Stones are faceted, light warm grey, and never eggs.
4. **Builder constants.** Build the drawn version only, with sizes as parameters.
5. **End brace.** A low sill, 1.0 × 0.37, giving a 0.35 step.
6. **No rope across the ends.** Both ends are open, so a character can walk on. This is a deliberate known miss against the f34, side and top cells; record it.
7. **Deck.** 10 planks with end blocks, 8 hangers a side, a diagonal from each post to its end plank, and rope links between all plank ends.
8. **Rope.** Twisted tubes everywhere, never under 5 sides on a coil. Gold goes on only 2 of every 5–6 strands, chosen by strand index, to avoid M048's gold excess. Rope must not read as thin outlines or faceted collars.
9. **Cloth.** An L-shaped wrap on each post's −X and +Y faces, red near `#B42411`.
10. **End Post part.** A bare timber post.
11. **Helpers.** Import M048's geometry helpers, never its constants. Import nothing from the uncommitted `m050.py`.
12. **Everything else** follows the spec:
    - Colour: the M048/M050 timber family, coloured by role and position, **never facing**, and not red. The stone's cool tone is blended by height and position only.
    - Packaging: every piece is its own closed shell, with **no floating pieces**, **0 winding errors** and no dressing buried in stone.
    - Cameras: the f34 (−20, 15) governs.
    - Collision, stages 5 and 6 skipped, the budget cut order, and the names `RopeBridge*` with keys `m051_*`.

**Walkability is binding.** Plank tilt is at most 17°. Steps between planks are at most 0.08. The only raised step is the 0.35 sill.

## Stage 1 — Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m051.py`. `build()` builds the seven parts and the hero, runs every check, renders and
measures. It returns `audit`, `uv`, `materials`, `views`, `measure`, `contact`, `bury`, `winding`, `walk`, `levels` and
`problems`. Constants are as in §2 (`L` 18, `W` 6, `STONE_TOP` 5.6, `POST_TOP` 11.0, `NP` 10, `PITCH` 1.40, `SAG` 1.10,
`ROPE_LOW` 6.86). From M048 it imports only the geometry helpers `_box`, `_knob`, `_solid`, `_tri_ngons`, `_tube` and
`winding_report`; no constants. Nothing comes from `m050.py`. Every piece is its own closed shell from explicit vertex
lists, with no booleans and no unions.

- **Anchor stones (4):** lofted rings, not convex hulls.
  - Each stone has 9 points per ring, at z 0, 1.3, 3.8 and 5.35, plus the flat top at 5.6. The sides are quads between
    the rings, and the top and bottom caps are centroid fans.
  - A first version used convex hulls of jittered points. Collinear hull points gave zero-area faces and 2–3° slivers,
    which dissolving and beautifying didn't remove. The loft has none (smallest corner 10.2° on the stone part).
  - Shape as §2.2:
    - the deck-side face is the vertical plane |x| 7.26 from 3.8 up, flaring to 6.8 at the ground;
    - the cleft face is the leaning plane |y| 0.05 (top) → 1.3 (ground), so each pair has a 0.10 seam at the top and
      the V gap below;
    - the outer x face runs 12.0 → 12.85, and the outer y face 4.9 → 5.35;
    - the outer top edges have a 0.25 chamfer, and the outer corner a 0.4–0.6 chamfer.
  - **Facets:** two facet columns per outer face, each pushed out (+0.15–0.32) or in (−0.12–0.28) by one amount from
    the ground to 3.8, and by 0.45× above. They give vertical ridges and grooves (the sheet's vertical facet breaks)
    with broad flat faces between.
  - **Deviation:** the outer base is 12.85 / 5.35 instead of 13.0 / 5.6. This leaves room for the spurs inside the
    §1.1 extents of 27.2 × 12.0.
- **Spurs (8, 2 per stone):** chunky 12-point hull blocks, 1.4–1.7 along the face, 1.0–1.3 tall and 0.78 deep, on the
  ground against the outer x or outer y face. Each is pushed out by bisection until the two hulls overlap by exactly
  0.03. The overlap is measured both ways on vertices, edge midpoints and face centres, because a stone corner can poke
  into a spur face between its vertices. The first version measured spur vertices only and buried spur faces 0.09–0.13.
- **Posts (4):** a 2.0 base block from z 5.58 to 6.70; a 1.6 shaft (sunk 0.02) stepping out to a 1.7 cap from 9.92 to
  11.0 with a 0.10 chamfer; a flush dark 0.30 peg-hole square on the cap top. One shaft-and-cap shell of 44 tris.
- **Coils (8):** two per post, centres at z 9.22 and 9.62, on a 16-point rounded square round the shaft (0.99 off the
  axis on the flats, corners at 0.93 / 0.93). The section is a twisted **3-sided** tube (r 0.265, reading 0.40–0.46
  thick), turned half a side per ring, with alternate rings 8 % thinner.
  - How the coil got here, tried in renders of one post:
    - the 5-sided 8-segment antiprism read as stacked flat plates;
    - a 6-vertex three-ply star section turned one side per ring (8 segments) still read as plates, because the
      segments were too long for the radius;
    - 16 short segments: 3-sided read as a twisted wrapped rope, 4-sided as a twisted cord, 5-sided as a smooth ring.
  - The final coil has the geometric twist the M048 ruling asked for, at 96 tris (the plan had 80).
- **Cloth (4):** an L-shaped slab (0.08 thick, inner face sunk 0.01) round each post's −X and +Y faces, z 8.20–9.00.
  Its caps are two quads each, so there are no sliver triangles. A knot lump sits on the −X face near the corner. Two
  tapered tails with pointed feet hang to about z 6.9 and 7.25 (one on each face, 0.02 off the shaft).
  - The band is taller than §2.6's 8.55–9.00, to bring the f34 red share up.
  - The swallowtail foot became a point: the notch's concave cap gave 4.7° slivers.
- **Brace sills (2):** x ±(8.5…9.5), y ±2.02 (sunk into the base blocks), z 5.58 → 5.95.
- **Peg blocks (4):** x ±(7.31…8.02), y ±(2.30…3.20), z 5.58 → 6.38, with a 0.28 peg 0.10 proud at z 6.15 on the
  span-facing face.
- **Planks (10):** the U prism of §2.4 (1.15 wide, 0.80 body, 1.15 lugs, 6.2 long).
  - The caps are ear-clipped into 6 triangles each (smallest corner 8.6°).
  - A flush pale peg-dot square (0.26) sits in a frame on each lug's end face.
  - Each plank's top centre sits on `z_top(x)`, pitched to the slope, with yaw ±0.4° and roll ±0.1°.
  - **The end planks are pitched 0.55° steeper about their outer top edge.** That edge stays at 5.585, and the step
    down to plank 2 drops from 0.083 to 0.068. With §2.4's ±1° / ±0.8° jitter the step was 0.083, over the binding
    0.08.
- **Main ropes (2):** y ±2.75, from (±8.0, 9.42) between the two coils, on the catenary through 6.87 at x 0.
  - 5-sided twisted antiprism, Ø 0.45.
  - 28 rings: the ends, two mid rings at ±6.45, and a knot collar at each hanger (rings ±0.2 at Ø 0.45 round a Ø 0.70
    ring).
- **Hangers (16):** at planks 2–9, y ±2.75, vertical from the lug top (knot bulge sunk 0.03) to 0.15 inside the
  collar.
  - Twisted 3-sided (r 0.16, reading 0.24–0.28 thick), 5 rings, lengths 2.21–2.54.
  - **Deviation from §2.5's 4 sides:** the 4-sided twisted hanger's long segment made 4.8° sliver triangles. The 3-ply
    hanger with a mid ring has none, is cheaper (26 tris against 28 / 36), and matches the coils.
- **Diagonals (4):** from (±8.0, ±2.9, 9.1) in the lower coil down to the end plank's lug top, with a knot bulge. The
  neck is at 0.45: at 0.36 it gave 4.9° slivers.
- **Backstays (4):** from the lower coil's outer corner (±9.93, ±3.93, 9.22) to a 6 × 3 knob (r 0.30) sunk 0.03 into
  the stone top at (±10.7, ±4.3). They clear the base blocks.
- **Links (18) and end ties (4):** 3-sided, r 0.15, one segment.
  - The links run lug face to lug face at |y| 2.65, mid-lug height, each end sunk 0.08.
  - The end ties run from the end plank's lug top to the peg block's face at z 5.85. They clear the stone's top corner
    by 0.064.
- **Not built, as decided:**
  - the rope across each end (decision 6; the check `rope_across_open_end` is 0);
  - the stone socket hole (hidden under the post);
  - the side peg in the hero (cut order 2; it is on the End Post part).
- **Parts:**
  - `RopeBridgeEndPost`: bare, with base block, shaft and cap, peg hole and side peg.
  - `RopeBridgeBrace`.
  - `RopeBridgePegBlock` (block and peg).
  - `RopeBridgePlank`: one level plank.
  - `RopeBridgeMainRope`: 8 long, with a collar near each end and Ø 0.6 knob ends.
  - `RopeBridgeHangerRope`: 3.0 long, with three knots.
  - `RopeBridgeAnchorStone`: the −X / −Y stone and its 2 spurs.
- **Renders:**
  - the seven default views;
  - `f34_sheet (−20, 15)`, `r34_sheet (160, 22)`, `front_sheet (0, 0)`, `side_sheet (90, 0)`, `rear_sheet (180, 0)`
    and `top_sheet (0, 89.9)`, all with the floor hidden;
  - seven part shots;
  - `exploded`: per end, two stones pulled apart, the posts lifted, the brace and peg block, the planks in a row, and a
    main rope with hangers above;
  - `scale`: 5.5 markers at mid-span, on the +X end plank, on the −X stone top between the brace and the deck, and on
    the ground;
  - close-ups `junc_cu`, `plank_cu`, `under_cu`, `rope_cu`, `knot_cu`, `cloth_cu`, `stone_cu` and `end_cu` (the open
    walk-on end);
  - all of them together in `M051_views.png`.
- **Lens probe:**
  - **f34**, lens 1.8 / 3 / 6× by az −20 / −25 by e 12 / 15 / 20. At (−20, 15) and 6× the W : H is 1.855 (sheet
    1.894), so `LENS` is 6× for both three-quarters.
  - **r34**, az 155 / 160 / 165 by e 18 / 22 / 25. At (160, 18) the W : H was 1.76, outside the spec's 1.53–1.69 band,
    so the r34 moved to **(160, 22)**: W : H 1.68.
  - The level orthos use 8×.

## Stage 2 — Optimisation and cleanup

Final build, run in a freshly restarted session (port 9880):

| Object | Tris | Size (studs) | Shells |
| --- | --- | --- | --- |
| `RopeBridge` | **3896 / 4000** | 27.41 × 12.33 × 11.00 | 116 |
| `RopeBridgeEndPost` | 68 | 2.00 × 2.00 × 5.42 | 3 |
| `RopeBridgeBrace` | 12 | 1.00 × 4.04 × 0.37 | 1 |
| `RopeBridgePegBlock` | 24 | 0.81 × 0.90 × 0.80 | 2 |
| `RopeBridgePlank` | 44 | 1.15 × 6.20 × 1.15 | 1 |
| `RopeBridgeMainRope` | 154 | 8.52 × 0.64 × 1.12 | 3 |
| `RopeBridgeHangerRope` | 68 | 0.41 × 0.40 × 3.00 | 1 |
| `RopeBridgeAnchorStone` | 130 | 6.80 × 6.11 × 5.60 | 3 |

- **Hero tris by kind:**
  - stone: 12 shells, 520 tris (4 stones × 90, 8 spurs × 20);
  - wood: 24 shells, 736 tris (4 × 56 posts, 2 × 12 braces, 4 × 12 peg blocks, 10 × 44 planks);
  - peg: 4 shells, 48 tris;
  - cloth: 16 shells, 256 tris;
  - rope: 60 shells, 2336 tris (coils 768, main ropes 552, hangers 416, backstays and knobs 240, diagonals 184, links
    144, ties 32).
- **Budget:** the first full build was 4032. Two changes brought it down:
  - the hangers went to the plan's ring count, then to 3-ply;
  - the links and ties went to 3-ply.

  It is now under 3900, so no cut-order item was needed. The side peg stays off the hero and on the part (cut 2).
- **Every object:**
  - zero non-manifold edges, bowtie verts, boundary, wire or loose elements, zero-area faces, n-gons and duplicate
    verts;
  - normals outward, transforms applied, 0 bowties fixed;
  - hero origin at the bbox bottom centre (offset −0.002, 0.005, 0);
  - smallest corner 5.03° on the hero (no face under 5°).
- **Winding:** 0 errors and 0 unpaired edges on every object (directed-edge check). Per shell (`m040.shells_report`):
  0 self-hits, 0 inverted faces, all volumes positive, no mixed-material shell.
- **Contact (tol 0.03):** 0 floating and 0 unchained shells on the hero, post, peg block, main rope and stone parts.
  The chains:
  - stones → ground; spurs → stones; base blocks → stones; shafts → base blocks;
  - coils and cloth → shafts; main ropes → coils; hangers → collars and lugs;
  - planks → hangers, diagonals and links; ties → peg blocks → base blocks;
  - backstays → coils and knobs → stones.
- **Buried (`bury_report`, ray parity per shell, against stated sink + 0.05):** 0 over the limit and 0 fully hidden.
  Worst depths:

  | Pair | Depth | What it is |
  | --- | --- | --- |
  | spur in stone | 0.03 | the spur seat |
  | rope in wood | 0.131 | the coils at the shaft corners |
  | rope in rope | 0.15 | rope ends inside the coils and collars |
  | rope in stone | 0.03 | the knobs |
  | cloth in wood | 0.01 | the wrap |
  | peg in wood | 0.03 | the pegs |
  | wood in stone | 0.02 | the base blocks, braces and peg blocks |

- **Levels:**

  | Item | Measured |
  | --- | --- |
  | Stone tops | 5.600 ×4 |
  | Post tops | 11.00 ×4 |
  | Base blocks | 5.58–6.70 |
  | Coils | 9.22 / 9.62 |
  | Main-rope low | 6.869 (target 6.86 ± 0.05) |
  | Deck mid top | 4.511 (4.50 ± 0.03) |
  | End planks' top outer edges | 5.585 |
  | Brace top | 5.95 |
  | Hanger lengths | 2.21–2.54 |

- **Walk (binding):**

  | Item | Measured |
  | --- | --- |
  | Plank tilt | 16.89 / 12.85 / 9.25 / 5.58 / 1.87° (max **16.89 ≤ 17**) |
  | Steps between planks | 0.068 / 0.061 / 0.039 / 0.021 / 0.006 / 0.023 / 0.040 / 0.057 / 0.066 (max **0.068 ≤ 0.08**) |
  | Gaps | 0.234–0.288 |
  | End step from the stone top | 0.013–0.016, across 0.40–0.42 gaps |
  | Sill | **0.35** |
  | Clear width | 4.0 between the base blocks, 4.4 between the shafts |
  | Rope across an end | none |

- **Extents:** 27.41 × 12.33 against §1.1's 27.2 × 12.0 with spurs (tolerance ±0.4).

## Stage 3 — UV

`M.smart_uv` (angle 45, `ANGLE_BASED`, margin 0.008) then `m012._uv_unfold` (2 faces cut free on the hero).

| Object | Islands | Overlaps | Flipped | Min gap | Border | Density | Conformal p95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `RopeBridge` | 2066 | 0 | 0 | 0.016 | 0.008 | 0.999 / 1.0 / 1.0 | 1.00 |
| Parts | 6–67 | 0 | 0 | 0.016 | 0.008 | 1.0 | ≤ 1.027 |

## Stage 4 — Materials, colour and texture

**Calibration** (`m051.calibrate()`, the `K.calibrate` dome, 6 iterations, starting from M048's palette):

| Key | Target | Dome-calibrated | Final in `PALETTE` | Why changed |
| --- | --- | --- | --- | --- |
| `wood` | `#D87E34` | `#AC6C33` | **`#B66D2A`** | f34 plank tops were under-saturated (`#CD7C3B`); linear-ratio correction |
| `wood_deep` | `#9D4D18` | `#804518` | **`#894315`** | front posts were 16 dark, f34 posts too yellow; averaged |
| `wood_dark` | `#6E3514` | `#5C3014` | `#5C3014` | |
| `rope` | `#F8C46A` | `#CEA261` | `#CEA261` | |
| `rope_dark` | `#C8761F` | `#A16720` | `#A16720` | |
| `peg` | `#F2CC80` | `#C0A870` | `#C0A870` | |
| `cloth` | `#B42411` | `#8F2210` | `#8F2210` | |
| `stone` | `#BCB5B0` | `#9B9A9D` | **`#ABA5A2`** | faces 12–20 dark and too neutral against the sheet's warm grey |
| `stone_mid` | `#939398` | `#767A85` | `#767A85` | |

**Finish:**
- wood: rough 0.85 (dark 0.9), metal 0, low specular;
- rope: rough 0.95, low specular;
- peg: rough 0.55;
- cloth: rough 0.9, low specular;
- stone: rough 0.92, low specular.

**Colour is by role and position, never by facing.** The builder selects no paint by a face normal (normals are used
only for winding and tube frames). `K.check` baked-shading correlation: hero 0.07, plank part 0.22, main rope part
0.25, the others 0.
- **Planks:** `wood`.
  - Planks 3 and 8 are 15 % `wood_deep`; planks inside a broad noise field along x are 10 % toward `peg` (a lighter
    field).
  - **Lug faces** (lug bottoms, inner walls, cap lug triangles and end-face frames) are 50 % `wood_dark`, by position.
    That is up from §5.5's 35 %, because the f34 lug sides were 38 lighter than the sheet's.
  - The peg dots are `peg`.
  - Per-plank Tint ±0.03, plus `K.texture` 0.02.
- **Posts:** `wood_deep`. The base blocks are 15 % `wood_dark`, the peg holes `wood_dark`, the brace 10 % `wood_dark`
  and the peg blocks `wood_deep`. Tint ±0.03, texture 0.03.
- **Stones:** `stone`, with `stone_mid` by height:
  - 40 % on the ground band (faces centred below 1.2), 15 % on the 1.3–3.8 band, none above;
  - 30 % in the cleft (|y| < 1.0);
  - spurs 50 %;
  - Tint ±0.03 per stone, plus a broad noise field at 0.03 (scale 0.15).
- **Rope strands are chosen by index round the twist (decision 8):**
  - the main ropes, diagonals and backstays (5 strands) have gold `rope` on 1, a blend on 1 (60 % toward amber) and
    `rope_dark` on 3;
  - the coils (3 strands) have gold 1, blend 1 and amber 1;
  - the hangers, links and ties are blend and amber only.
  - **Why:** a probe recoloured each rope family.
    - With gold on the thin ropes too, the f34 gold share was 4.3; without it, 2.6. Coil gold is worth 1.0 and
      main-rope gold 1.4.
    - With 2 of 5 golden on the main ropes it was 5.7, and before calibration 9.7.
    - The blend strand stays amber-side (hue < 36°, class W), as the sheet's amber strands do.
- **Cloth:** `cloth`, Tint 0.95–0.97 on the tails and knot.

**Re-measured** on the final renders against the sheet (study masks, floor hidden):

| View | W : H ours (sheet) | W | K | Y | R | S | Top-profile error mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **f34 (−20, 15)** | **1.839 (1.894)** | 23.7 (22.6) | 25.3 (23.8) | **2.8 (2.8)** | 1.0 (1.7) | 47.2 (49.0) | 0.079 |
| r34 (160, 22) | 1.683 (1.61) | 23.1 (21.8) | 25.3 (23.4) | 2.5 (2.9) | 2.1 (1.6) | 47.0 (50.3) | 0.058 |
| front (0, 0) | 2.459 (2.431) | 13.2 (19.0) | 28.7 (19.4) | 2.6 (4.4) | 0.3 (0.1) | 55.1 (57.2) | 0.059 |
| side (90, 0) | 1.102 (1.016) | 3.3 (26.3) | 28.7 (21.0) | 0.4 (1.8) | 0.4 (0.0) | 67.2 (50.9) | 0.126 |
| rear (180, 0) | 2.453 (1.984) | 11.7 (19.8) | 28.0 (15.6) | 2.6 (3.7) | 2.7 (3.6) | 55.0 (57.4) | 0.085 |
| top | 2.226 (2.096) | 46.7 (41.5) | 6.9 (20.7) | 1.9 (0.7) | 0.0 (0.0) | 44.5 (37.2) | — |

- **f34 medians** (ours against the sheet's regions):
  - W `#CA7E32` against plank tops `#DA7E31`;
  - K `#954214` against post faces `#9D4A16`;
  - Y `#F5B765` against `#F4C26A`;
  - R `#922011` against `#98200F`;
  - S `#BCB1A8` against faces `#C1B7AF`.
- **f34 Y fifths:** 0 / 5.1 / 21.4 / 61.9 / 11.5 (sheet 0 / 0.6 / 28.8 / 56.5 / 14.2; each within ±10).
- **Region samples** (`region_report()`, 5 × 5 medians at build-frame points):

  | Region | Ours | Sheet | Max channel diff |
  | --- | --- | --- | --- |
  | f34 plank tops (24 points) | `#D67F32` (28°, 0.77, 0.84) | `#DA7E31` | **4** |
  | f34 cap top | `#AF5224` | `#A6521C` | 9 |
  | f34 post faces | `#AB6627` | `#9D4A16` | 27 (lit side brighter) |
  | front post face | `#984212` | `#9D4D17` | 11 |
  | front lug ends | `#974F20` | `#9D4B1B` | 6 |
  | f34 stone faces | `#B9AEA5` | `#C1B7AF` | 10 |
  | front stone faces | `#BAAFA6` | `#B9B1AC` | 6 |
  | f34 stone tops | `#D7CABF` | `#F3E8DB` | 29 (the sheet's lit tops are near white) |
  | f34 lug sides | `#934D1E` | `#6B3413` | 39 (the sheet's −X lug sides are in shade) |

  The `cloth` region sample lands on the post at that angle. Use the R median instead.
- **Hue checks:** wood 20–28° everywhere (not red, not tan; plank-top R − G is 87); rope 33–40°; cloth 4–8°; stone
  hue 28°, sat 0.11 (warm light grey) with cool `stone_mid` low down.

## Stage 5 — Lighting: skipped

The sheet shows no emissive part, glow or light, so there are no emissive faces and no lights. To check in Studio
(Requires Manual Validation):
- the planks read warm orange (not red), the posts a little deeper, the stones light warm grey with cool shade;
- the rope reads golden over amber, and the cloth deep red;
- a character walks from a 5.6 surface onto a stone top, over the 0.35 sill, down the sagging deck and up the other
  side without jumping (precise collision on the hero). The main ropes are hip-height hand-lines, not a guard.

## Stage 6 — VFX: skipped

The sheet shows no effect, water or foam. The hero has no sockets, and `checks()` flags any.

## Modeller's notes for the verifier

- **Rebuild:**
  `import importlib, kit_models, m051; importlib.reload(kit_models); importlib.reload(m051); m051.build()`.
  - `m051.measure_views()` gives the study-mask shares, and `m051.region_report()` the region samples.
  - `m051.walk_report()`, `m051.bury_report(o)` and `m051.levels_report(h)` cover the binding checks. Run them after a
    `build()`: they read `PLANK_INFO` and `GEO`.
- **Decisions followed:** 1–12 as written. Known deviations:
  1. **Stone bases** are 12.85 / 5.35 instead of 13.0 / 5.6, so the chunky spurs stay near §1.1's 27.2 × 12.0. The hero
     is 27.41 × 12.33 (tolerance ±0.4).
  2. **The end planks are pitched 0.55° steeper** (16.89°) about their outer top edge, and the jitter is ±0.4° yaw
     and ±0.1° roll. This keeps the binding step limit: 0.068 against 0.083 with §2.4's jitter.
  3. **Rope geometry:**
     - the coils are 16-segment twisted **3-sided** tubes (spec: 5 sides × 8, twisted). The 5-sided and 6-ply 8-segment
       versions read as stacked plates (see Stage 1). The coils are 96 tris each.
     - the hangers, links and ties are 3-sided (spec: 4). The 4-sided hanger made slivers, and the coils, hangers and
       links now share one twisted 3-ply look.
  4. **Gold is 1 of 5 strands** on the main ropes and backstays, 1 of 3 on the coils, and 0 on the thin ropes
     (decision: "only 2 of 5–6"). This was set by the f34 gold-share probe: f34 Y 2.8 against 2.8.
  5. **Lugs** are 50 % `wood_dark` instead of 35 %. **Cloth** is z 8.20–9.00 instead of 8.55–9.00. The **swallowtail
     tails** have a pointed foot.
  6. **The r34 camera** is (160, 22) instead of (160, 18), to bring W : H inside the spec band.
  7. **Not modelled:** the rope across the ends (decision 6, a deliberate miss in the f34, side and top cells), the
     stone socket hole, the hero side pegs (cut order 2), plank grain lines, and the post split line (§3.7).
- **Known misses (lighting, not paint):**
  - **front / side / rear W and K:** the studio lights the −Y, +X and +Y faces less than the sheet does. For example,
    the side cell is W 3.3 against 26.3, but the K median `#71310C` is still in the wood family.
  - **top S 44.5 against 37.2:** the stone tops are broad in plan, and the sheet's top cell crops its pale tops into B.
  - **f34 R 1.0 against 1.7:** inside ±1.0. The L-wrap's −X faces are seen at a grazing angle from (−20, 15), and the
    sheet's f34 draws the cloth round the far faces too. This follows decision 9.
  - **f34 top-profile error 0.079 mean:** the sheet's f34 perspective draws the left posts lower (§3.1). W : H and
    every share are in band.
- **Judge the rope by eye** in `junc_cu`, `cloth_cu`, `rope_cu` and `plank_cu`: the coils are twisted rope rings, not
  faceted collars; the main ropes are twisted 5-sided tubes with fat knot collars; the hangers are twisted 3-ply with
  knot bulges seated on the lugs.

## Verification round 1 (verifier, 2026-10-29)

A fresh verifier ran this round read-only on `wip/M051_verify.blend` (port 9880). It ran no `build()`, edited no builder and saved
nothing. Every number below comes from the verifier's own bmesh/BVH code, not from the builder's reports. Renders and
scripts are in the scratchpad `m051_verify/`. Each render was compared with the matching sheet cell and measured with the
study's `measure_render.py` (paper `#F2E8D9`).

### Measured

| Object | Tris | Size | Shells | Non-manifold / boundary / wire / loose | Bowties | Winding (dup. directed / unpaired) | Zero-area / n-gons | Self-hits in shell | Inward faces (tri parity) | Min corner | Origin offset |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `RopeBridge` | **3896 / 4000** | 27.41 × 12.33 × 11.00 | 116 | 0 / 0 / 0 / 0 | 0 | 0 / 0 | 0 / 0 | 0 | 0 | 5.03° | 0, 0, 0 |
| `RopeBridgeEndPost` | 68 | 2.00 × 2.00 × 5.42 | 3 | 0 | 0 | 0 / 0 | 0 / 0 | 0 | 0 | 45° | 0 |
| `RopeBridgeBrace` | 12 | 1.00 × 4.04 × 0.37 | 1 | 0 | 0 | 0 / 0 | 0 / 0 | 0 | 0 | 90° | 0 |
| `RopeBridgePegBlock` | 24 | 0.81 × 0.90 × 0.80 | 2 | 0 | 0 | 0 / 0 | 0 / 0 | 0 | 0 | 90° | 0 |
| `RopeBridgePlank` | 44 | 1.15 × 6.20 × 1.15 | 1 | 0 | 0 | 0 / 0 | 0 / 0 | 0 | 0 | 8.6° | 0 |
| `RopeBridgeMainRope` | 154 | 8.52 × 0.64 × 1.12 | 3 | 0 | 0 | 0 / 0 | 0 / 0 | 0 | 0 | 9.3° | 0 |
| `RopeBridgeHangerRope` | 68 | 0.41 × 0.40 × 3.00 | 1 | 0 | 0 | 0 / 0 | 0 / 0 | 0 | 0 | 23.8° | 0 |
| `RopeBridgeAnchorStone` | 130 | 6.80 × 6.11 × 5.60 | 3 | 0 | 0 | 0 / 0 | 0 / 0 | 0 | 0 | 10.2° | 0 |

Every shell has positive volume, and transforms are applied on every object. There are no modifiers or custom normals,
each object has one `UVMap` and a CORNER `Tint` attribute. A parity test on the untriangulated quads first flagged 48
"inward" faces. They come from 104 non-planar quads (worst deviation 0.079, on the stones). On the triangulated mesh
there are **0** inward faces.

Hero shell census: stone 12 (4 stones and 8 spurs); wood 24 (4 base blocks, 4 shafts, 2 braces, 4 peg blocks and 10 planks);
peg 4; cloth 16; rope 60 (8 coils, 2 main ropes, 16 hangers, 4 diagonals, 4 backstays, 4 knobs, 18 links and 4 ties).

**Contact** (tolerance 0.03, with BVH overlap or proximity, chained from the ground): **floating 0, unchained 0** on the
hero, post, peg block, main rope and stone parts. No shell is fully hidden.

**Buried** depth was measured by nearest-normal plus 7-ray parity, as the deepest point of each shell inside another:

| Pair | Measured | Stated sink | Limit (sink + 0.05) |
| --- | --- | --- | --- |
| Spur in stone | 0.025 | 0.03 | 0.08 |
| Base block, brace or peg block in stone | 0.02 | 0.02 | 0.07 |
| Knob in stone | 0.03 | 0.03 | 0.08 |
| Peg in wood | 0.03 | 0.03 | 0.08 |
| Cloth in wood | 0.01 | 0.01 | 0.06 |
| Links in lugs | 0.082–0.089 | 0.08 | 0.13 |
| Hanger tops in collars | 0.125–0.137 | 0.10 (0.15 in builder) | 0.15 |
| End ties in peg blocks | 0.108–0.119 | 0.08 | 0.13 |
| Backstays in coils | 0.137–0.148 | "sunk" | — |
| Backstay ends in knobs | 0.205 | (end inside knob) | — |
| **Lower coil in shaft** | **0.075** | 0.02 | 0.07 (+0.005) |
| **Upper coil in shaft** | **0.106** | 0.02 | 0.07 (+0.036) |
| **Diagonal foot in end-plank lug** | **0.128–0.131** | 0.03 | 0.08 (+0.05) |

**Levels:**

| Item | Measured |
| --- | --- |
| Stone tops | 5.600 ×4 |
| Post centres | (±9.0, ±3.0) |
| Shafts and caps | 6.68 → 11.00 |
| Braces | x ±(8.5…9.5), y −2.03…2.01, z 5.58 → 5.95 |
| Peg blocks | x ±(7.31…8.02), 5.58 → 6.38 |
| Main-rope centre at x 0 | 6.875 (bottom 6.653, Ø 0.45; collars Ø 0.70) |
| Deck top at mid-span | 4.512 |
| End planks' outer top edges | 5.583–5.585 at \|x\| 6.86 |
| Plank to stone clearance | 0.065 |

**Walkability** (binding), measured on the mesh:
- Plank tilts: 16.89 / 12.85 / 9.25 / 5.58 / 1.87° (max **16.89 ≤ 17**).
- Steps between plank top edges across \|y\| ≤ 2: max **0.052 ≤ 0.08**.
- Gaps: 0.219–0.271.
- End step from the stone top: 0.015.
- No geometry above z 6.0 over the end walk (\|y\| ≤ 1.6, \|x\| 7.3–12.2), so **no rope crosses either end**.

**Character walk:** a 2.0 (y) × 1.0 (x) × 5.5 box was stepped 0.1 at a time from x −11.5 to +11.5 in lanes y −0.7, 0
and +0.7 (box out to \|y\| 1.7). The floor was found by downward rays.
- The largest step up or down is **0.35**, at the sill only. The floor runs 5.60 → 5.95 → 5.56 … 4.51 … 5.56 → 5.95 → 5.60.
- **0 collisions** in the box above floor + 0.36 in any lane.
- Clear width: 4.0 between the base blocks and 3.49 between the coils at head height. Both ends are open.

**Shares** (study masks; sheet in brackets):

| View | W : H | W | K | Y | R | S |
| --- | --- | --- | --- | --- | --- | --- |
| **f34 (−20, 15), 6×** | **1.840** (1.894) | 22.6 (22.6) | 26.4 (23.8) | 3.1 (2.8) | 1.0 (1.7) | 46.8 (49.0) |
| r34 (160, 22) | 1.681 (1.61; band 1.53–1.69) | 22.4 | 26.0 | 2.8 (2.9) | 2.3 (1.6) | 46.5 |
| r34 (160, 18) | 1.766 | 21.0 | 26.8 | 2.6 | 2.3 | 47.2 |
| front | 2.457 (2.431) | 12.1 | 30.6 | 3.0 (4.4) | 0.4 (0.0) | 54.0 (57.2) |
| side | **1.104** (1.016 ± 0.08) | 3.5 | 28.5 | 0.4 | 0.5 | 67.1 |
| rear | 2.457 (1.984) | 11.7 | 28.7 | 2.8 | 3.0 (3.6) | 53.8 |
| top | 2.222 (2.096) | 47.5 | 6.7 | 2.2 | 0.0 | 43.6 |

- Every f34 share is within the binding ±4. The largest gap is K +2.6.
- f34 Y fifths: 0 / 5.7 / 21.8 / 60.8 / 11.7. The sheet's are 0 / 0.6 / 28.8 / 56.5 / 14.2, so each is within ±10.

**Colour** (f34 medians against the sheet):

| Class | Ours | Sheet | Note |
| --- | --- | --- | --- |
| W | `#CC8033` (30°) | plank tops `#DA7E31` | |
| K | `#944117` (20°) | posts `#9D4A16` (23°) | |
| Y | `#F7B966` | `#F4C26A` | |
| R | `#921F11` (6.5°) | `#98200F` | |
| S | `#BBAFA8` (warm, sat 0.10) | `#C1B7AF` | |

- Wood is in the M048/M050 family: `wood #B66D2A` / `deep #894315` against M048's `#BB722E` / `#88491A`. It is never red.
- The rope's Y share is 3.1 against 2.8, so there is no gold excess. The amber strands carry most of the rope.
- `K.check` reports no problems, and `kit_baked_shading` is 0.07.
- **Facing correlation** (own code, normal z against material × Tint luminance): hero all faces 0.07; wood 0.10; rope −0.04;
  plank part 0.22; main rope part 0.23; post part −0.02.
  - Stone is 0.47 (bottoms excluded), and 0.56 in the 1.4–5.5 band. The cause is position, not facing: the spec's cleft rule
    (\|y\| < 1.0, 30 % `stone_mid`) lands on the leaning cleft faces, which point downward.
  - A grep of the builder finds **no paint selected by a normal**. `_stone_colour` uses the face centre's z and \|y\|. The
    normals are used only in winding, tube frames, spur placement and `walk_report`.
- **No lighting, VFX or water:** no emissive materials, no lights, no children or sockets, no water or foam keys.

### Shape against the sheet

| Area | What the renders show | Result |
| --- | --- | --- |
| Overall | Front, rear and top match their cells' composition. The f34 and r34 read as the sheet's: two stone pairs, four posts with coils, the swooping main ropes with the hanger fence, ten tilted lug planks and backstays. | Good |
| Anchor stones | Four faceted, tapered, flat-topped blocks with vertical facet columns and chamfered outer top edges. Not eggs. The side view shows the V gap with a 0.10 seam at the top. | Good |
| Posts | A wider base block, a cap block a step wider with a dark peg hole, and a visible cap line in the close-ups. | Good |
| Coils | Two twisted 3-ply wraps per post: twisted and two distinct wraps, not smooth octagon collars. | Minor 1 |
| Cloth wraps | An L-wrap with tails on −X / +Y. Red shows in the rear and r34 (R 3.0 / 2.3) and on all four posts' far faces in the f34. Front 0.4, side 0.5. | Good |
| Backstays | Run to knobs on the stone tops. | Good |
| Main ropes | Sag to 6.875 between the coils, with fat collars at each hanger. | Good |
| Hangers | 16, twisted, with bulges seated on the lugs. | Good |
| Diagonals | 4, to the end planks. | Good |
| Links | 18 between the lugs. | Good |
| Planks | 10 tilted planks with deep end lugs and pale peg dots. They read like the plank close-up. | Good |
| Sill and peg blocks | The sill and the four peg blocks are present. | Good |
| Underside | Matches cell 7 in content. | Good |

### Findings

1. **minor** (the claimed deviation, judged acceptable): **the coils read as jagged diamond-faceted bands** in the f34, `c_junc` and
   `c_coil`, where the sheet draws two round, fat rope wraps with strand grooves. They are clearly twisted rope rings,
   not flat octagon collars, so this is not the M048 failure. The 3-sided choice is accepted.
   - **Fix target (polish):** soften the facets. Raise the coil `pinch` or ring count, or try 4 sides × 20 segments
     (≤ 100 tris each), so each wrap reads rounder.
2. **minor:** **the upper coils sit 0.106 into the shaft and the lower ones 0.075**, against the stated 0.02 sink (limit
   0.07). Most of each coil is visible, so nothing is hidden.
   - **Fix target:** move `COIL_D` / `COIL_C` out by about 0.04 at the upper ring (or both rings). Otherwise, record the
     coil sink as 0.10 in §6.
3. **minor:** **the diagonal feet sink 0.13 into the end-plank lugs** (stated 0.03). The knot bulge still shows.
   - **Fix target:** end the diagonal path 0.08 higher (`diagonal()` contact point), or record the sink.
4. **minor: the stone spurs are small pointed shards.** The sheet's f34, exploded view and key draw chunky, cube-like
   loose blocks at the stone feet (up to about a quarter of the stone height). In the top view the spurs also read as
   detached pebbles.
   - **Fix target:** make the spurs blockier (fewer, flatter-topped hull points) and taller, 1.4–1.8. Check the overlap
     again afterwards.
5. **minor: the stones' cool lower tone sits in hard horizontal bands.** It is 40 % below z 1.2 and 15 % to 3.0,
   visible as stripes in `c_stone`. Spec §5.5 asked for a 3-step blend to z 2.2.
   - **Fix target:** use `K.blend` steps across 1.2–2.2.
6. **minor: the side view W : H is 1.104**, against 1.016 ± 0.08 (0.008 over). The side view's W / K split (3.5 / 28.5
   against 26.3 / 21.0) is the studio lighting on the +X faces, as the notes say. The K hue is still in the wood family.
7. **minor: the `RopeBridgePegBlock` part** has one peg and no top peg hole. The key draws a hole on top and pegs on two
   faces.
   - **Fix target:** add the top inset, and optionally a second peg (+20 tris).
8. **minor: 104 non-planar quads** on the hero (worst 0.079, on the stone loft rings). They are not a defect in Blender.
   The exporter or Roblox's triangulation may pick the other diagonal, which changes the facet shading a little.
   - **Fix target (optional):** triangulate the stone sides at build time.
9. **noted, not a finding:**
   - The r34 at e 22 is accepted. It puts W : H inside the spec's band; e 18 gives 1.766.
   - Gold on 1 of 5 strands on the main ropes, diagonals and backstays and 1 of 3 on the coils is accepted. The decision
     said 2 of 5–6, but the f34 Y share of 3.1 against 2.8 shows the change avoided a gold excess.
   - The end planks 0.55° steeper is accepted. Tilt is 16.89 ≤ 17, and the step limit holds.
   - The smaller stone bases (12.85 / 5.35) are accepted. The extents are 27.41 × 12.33, within ±0.4 of 27.2 × 12.0.

### Decisions check

1. Size and levels: followed.
2. Long axis X, symmetric except the cloth: followed.
3. Four stones with a 0.10 seam and the V gap: followed.
4. Builder constants: followed.
5. Sill 1.0 × 0.37, a 0.35 step: followed.
6. **No rope across the ends:** followed; 0 hits over the end walk. This is a known miss against the f34, side and top
   cells, and it is recorded.
7. 10 planks, 8 hangers a side, 4 diagonals and 18 links: followed.
8. Twisted rope everywhere; coils not under 5 sides: the coils are **3-sided**. This is the modeller's justified deviation,
   and it is judged acceptable (finding 1). Gold by strand index: followed.
9. L-wrap cloth `#8F2210`, rendering `#921F11`: followed.
10. Bare End Post: followed.
11. Only M048 geometry helpers imported, nothing from `m050`: followed.
12. Colour by role and position, closed shells, 0 floating, 0 winding errors, names `RopeBridge*` / `m051_*`, collision
    precise / hull / box / none, stages 5 and 6 skipped: followed.

### Score and verdict

**8 / 10. PASS.**
- Mesh, winding, budget, contact, walkability and colour family are all clean. The f34 shares are within ±4, and every
  decision is followed or justified.
- The leftovers are polish: rounder coils, chunkier spurs, a blended stone band, small sink overruns at the coils and
  diagonal feet, and the peg-block part details. None of them blocks a commit.

## Main session ruling (2026-10-29)
- **Result:** passed in round 1 (8/10) and committed. All five modeller deviations are accepted. The missing end rope stays the recorded known miss.
- **Left for a later polish pass:**
  - Coils read as jagged faceted bands. Use 4 sides × 20 segments, or a softer pinch.
  - Coils sink 0.075 / 0.106 against 0.07. Move them out about 0.04.
  - Diagonal feet sink 0.13. Raise them about 0.08.
  - Loose foot rocks are small shards. Make them blockier, 1.4–1.8 tall.
  - The stones' cool band is hard-edged. Use a 3-step blend.
  - The PegBlock part lacks its peg hole and second peg.
  - Triangulate the stone sides at build time; 104 non-planar quads.
- **Export:** 8 assets, 8 solid pieces, 4396 tris, 0 VFX sockets, palette 19 colours, 0 problems.
