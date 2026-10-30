# 050 Timber Bridge — spec

Reference: `art/blender/assets/references/050.png` (1024 × 1536 px). The sheet's title is "49/132 | TIMBER BRIDGE" (the
printed 49 is the generator's number; INDEX.md row 50 calls it "Flintborn timber bridge model study"). The footer reads
"FLINTBORN — INDIVIDUAL MODEL STUDY".
Builder: `art/blender/kit/mcp/m050.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no water, glow or effect** (§7).

Sheet text:
- **Cells:** "1 ASSEMBLED VIEWS": "FRONT THREE QUARTER", "REAR THREE QUARTER"; "2 ORTHOGRAPHIC VIEWS": "FRONT VIEW",
  "SIDE VIEW", "REAR VIEW", "TOP VIEW". The front, side and rear cells are level (e ≈ 0: no plank tops show); the top
  view is a plan.
- **Exploded:** "3 EXPLODED CONSTRUCTION": labels "Rope Segment", "Post", "Stringer", "Brace", "Crossbeam". Also drawn,
  unlabelled: 7 posts with two rope coils each, one long rope strung over five of them, two deck groups (about 5 + 9
  boards), three stringers, two crossbeams, two corner "L" pieces (a leg with a beam end), two loose leg stubs, about
  eight small blocks with round peg heads, dashed drop arrows.
- **Key parts:** "PARTS (ISOLATED)": "Post" (square post, two coils near the top, peg dot on the cap, two dark slots
  near the foot), "Plank" (a long board with a faint line along its top), "Stringer", "Crossbeam", "Brace", "Rope
  Segment" (a short sagging twisted rope with round knob ends).
- **Close-ups:** "4 CONSTRUCTION CLOSE-UPS": "UNDERSIDE VIEW" — "Crossbeams and diagonal braces support the deck from
  below."; "POST JUNCTION" — "Rope tied around post. Planks sit on stringers and are fastened with wooden pegs.";
  "PLANK DETAIL (SECTION)" — "Plank thickness and joining surface. Simple blocky forms and clean edges for consistent
  low-poly style."
- **Material palette:** six unlabelled swatches, twice (header and §5): orange wood, tan, cream, grey, green, blue (§5.1).
- **Modeling notes:** "Modular construction using reusable parts." "Keep forms chunky and readable." "Broad
  flat-shaded faces, no small bevels." "Simple, clean geometry with straight cuts and consistent proportions."
  "Maintain the same silhouette and style as the Flintborn reference." "No additional details, props or text."
- **Game context:**
  - **W08 owns the old kit's footbridge** (`art/blender/scripts/kit/W08/footbridge.py`, goals
    `art/blender/renders/kit/W08/footbridge_goals.md`, manifest `art/roblox/kit/W08/manifest.json`): `Footbridge`,
    `FootbridgePost`, `FootbridgePlank`, `FootbridgeStringer`, `FootbridgeCrossbeam`, `FootbridgeBrace`,
    `FootbridgeRopeSegment`, `FootbridgeShortSpan`, `FootbridgeArched`, `FootbridgeBroken`; keys `w08_*`. It was built
    to an older drawing as a **low stream crossing** (deck top 2.0, posts 0.6, 10 × 5.3, 3 posts a side; its goals ask
    for "deck z ~1.6, walkable width ≥ 4"). `MODEL_PROGRESS.md` row 72 flags it "plank orientation; no X brace; flat
    orange; arched variant flat"; its goals record a rope that rendered "more golden-yellow than the reference's tan".
    Reuse its lessons, not its names or sizes (§8).
  - **M048 Dock** (being modelled now, `m048.py` untracked): the kit's first timber piece. W 8 post centres, posts 1.3,
    boards 1.82 × 0.85 (0.06 top chamfer), beams 3.45 → 4.75, **deck top 5.6**, posts to 8.3, rope coils + swags Ø
    0.42, brass bolt heads. Its colour family (§5) and rope look are this bridge's.
  - **Kit levels:** ground 0; water top 1.0 (M032 / M034 / M037 / M041; water 0.25/0.6 → 1.0 over a plate at z 0);
    M034 banks 1.6 with a 14-wide channel at its seams (X −7 … +7); M043 lower lawn 5.6, M040 / M043 upper lawn 10.4;
    M048's dock deck 5.6.
  - WorldModeling §13.1–13.2 (timber vocabulary): squared timbers with restrained bevels, posts stronger than rails,
    load-bearing parts first (posts, stringers, crossbeams, boards, then braces and rope), "Rope rails are thick
    low-resolution curves/tubes with restrained sag. Do not model individual rope fibers".

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Cell paper `#FEFDF9`
(the masks use M048's `#FEFCF7`, tolerance 10). Cell borders from the grey rule lines (`lines.py`): rows 63 / 393 /
401 / 651 / 659 / 1182 / 1190 / 1410 / 1492; columns 11 / 319 / 511 / 795 / 743 / 1012. Labels and callouts are painted
out (`TITLES` in `m.py`, found with `navy.py`). Masks are M048's `cls()` (HSV, h in degrees, in this order):
- **T** outlines / text: v < 0.16, or s < 0.25 and v < 0.35.
- **B** ground shadow: s < 0.12, v ≥ 0.70. Excluded from shares.
- **Y** rope and pegs: h 36–62, s ≥ 0.18, v ≥ 0.60; or h 33–36, s < 0.62, v ≥ 0.75.
- **W** lit wood: h < 40 (or > 345), s ≥ 0.35, v ≥ 0.62 (board tops, caps, lit ends).
- **K** dark wood: the rest of the wood hues, s ≥ 0.25, v ≥ 0.16 (post faces, stringers, legs, braces, shade).
- **O** other.
- W / K is a **lit / dark** split, not a material split (one orange timber family, §5).
- Cells: f34 (12,64,511,393); r34 (513,64,1011,393); front (12,402,318,651); side (320,402,510,651); rear
  (512,402,794,651); top (796,402,1011,651); exploded (12,660,742,1181); key parts (744,660,1011,1181); underside
  close-up (22,1236,290,1412); post junction (301,1236,500,1412); plank detail (512,1236,720,1412). Header swatches:
  inner boxes (736,19,762,43), (783,…), (830,…), (877,…), (924,…), (970,19,996,43) (`m.SW`); the §5 copies at x 752 /
  796 / 840 / 884 / 927 / 970, y 1250–1275.

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m050_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14, Pillow, numpy; no scipy).
- **Helpers:** `m.py` (masks, boxes `V` / `X` / `SW` / `TITLES`, `label`), `zoom.py` (crop with an optional sheet
  grid), `px.py`, `lines.py` (cell borders), `navy.py` (label boxes), `sampcore.py` (`reg()`: region median / lit /
  shade quartiles).
- **Measurements:** `measure.py` → `bb.json` and `cls_*.png` (bbox, W : H, shares, top profile, width per height,
  fifths); `ortho.py` (row runs across the ortho cells: posts, deck band, legs, the top view's rows); `colp.py <cell>
  <x,x,…> <y0> <y1>` (class runs down columns: levels); `persp.py` / `persp_r34.py` (a pinhole camera fitted to the
  eight cap centres of each three-quarter: azimuth, elevation, bay / width); `proj050.py` (orthographic block model of
  the adopted layout at any camera, §2.7).
- **Colour:** `samp050.py` (swatches and every region in §5.2).
- **Zooms:** `n_f34.png`, `n_r34.png`, `n_fs.png` (front + side), `n_rt.png` (rear + top), `z_expl.png`,
  `z_expl_deck.png`, `z_keys.png`, `z_cu.png`, `z_cu2.png`; gridded details `g_front.png`, `g_side.png`, `z_f34a.png`,
  `z_f34b.png`, `z_f34under.png`, `z_f34under2.png`, `z_r34a.png`, `z_r34b.png`.
- **On our renders:** `measure_render.py <render.png> [paper_hex]` prints bbox, W : H, W / K / Y shares, profile,
  width per height, fifths and class medians with these masks. Self-test on the sheet's own f34 cell
  (`selftest_f34.png`) reproduces §1.2 exactly (W : H 1.670, W 41.7 / K 52.4 / Y 5.9).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a modular timber structure. Hero budget 4000 tris, each part under 1000. The plan in
  §4.3 lands at about 3450 (the rope is about 60 % of it).
- **Overall read (check this first).** A **long, level, straight timber trestle footbridge on eight square posts**
  (four a side, three equal bays), about three times as long as it is wide, **open at both ends**:
  - a **deck of chunky orange boards laid across the width**, four per bay, their ends forming a row of blocks along
    both long edges, the deck running on past the end posts at each end (front cell 11 px ≈ 1.3 studs past their
    outer faces; adopted 1.54, the end board);
  - **eight square posts** running from the ground up through the deck edge and standing a good third of their height
    above it, each with a softened square cap and a small dark peg dot;
  - **two tan rope wraps round each post** a little above the deck, and **thick twisted rope swags sagging low
    between the posts along both long sides** (three per side). **No rope across either end**;
  - under the deck, a **dark stringer** along each side (running a little past the end posts), a **crossbeam** at
    every post pair, and a **block with a round pale-gold peg head** on each post's outer face at stringer height
    (and on the end faces of the corner posts);
  - **legs** (the posts below the stringers), **knee braces** from each end leg inward to the stringer (end bays only)
    and an **X brace** between the two legs at each end, with a peg at the crossing.
  - Hero shares (f34): W 41.7 % (lit board tops, caps, plank ends), K 52.4 % (post faces, stringers, legs, braces),
    Y 5.9 % (rope and pegs).
- **Focal silhouettes, in order:**
  1. The long deck slab with its row of plank-end blocks, rising from the lower left (near −X end) to the upper right
     of the f34.
  2. The eight posts standing above it, each with its rope wraps, and the six low swags between them.
  3. The legs, the knee braces and the end X braces under the deck; the blocks and pegs on the post faces at the
     stringer line.
- **Target (post centres): W 8.0 across × 3 bays of 9.143 along (27.43 end post to end post), deck 32.0 long, deck top
  5.6, post top 8.85.** Overall about **32.0 L × 11.0 W (pegs) × 8.85 H**. Tolerances: post spacing exact; deck top
  5.6 ± 0.02 (a seam level, §2.1); H ± 0.3; W ± 0.4; L ± 0.4. Decision §8.1.
  - **How it was derived.**
    - **Height to width.** The side cell (level, the only cell drawn at one scale) gives post spacing 105 px across
      (posts 353–373 / 458–478) against post top → ground 471 → 591 = 121 px: **H / W 1.15**; the f34 fit (below),
      corrected for the near post's larger scale, gives 1.13. Adopted H / W 1.106 (W 8, H 8.85: the deck top lands on
      5.6, see levels).
    - **Bay to width.** Fitting a pinhole camera to the eight cap centres (`persp.py`, rms 5 px): **f34 bay / W 1.38,
      e 23°, the long axis 39° off the screen plane; r34 bay / W 1.35, rms 7 px.** Forced to a ratio, the fit error is
      8.8 px at 1.0, 5.9 at 1.2, 5.2 at 1.3–1.4. The **front and rear cells give 0.93** (bays 75.5 / 82.5 / 76 px
      against W ≈ 84 px at their height scale: the cells are drawn horizontally compressed, §3.1) and the **top cell
      1.0** (a two-bay drawing, §3.2). Adopted **1.143** (bay 9.143 = 4 boards of 2.286): between the three-quarters
      and the orthos, and it makes the deck exactly one 32-stud tile. The block model then gives the f34 W : H
      **1.677** at (−40, 23) against the sheet's **1.670**, and **1.587** at (140, 26) against the r34's 1.577
      (`proj050.py`).
    - **Levels** (front cell, H = 97 px from the post top y 486 to the ground y 582; side cell, H = 121 px, 471 → 591):

      | Item | Front (frac. of H) | Side | Adopted (z) |
      | --- | --- | --- | --- |
      | Post top | 1.000 | 1.000 | **8.85** |
      | Upper / lower rope wrap centre | .836 / .794 | .847 / .810 | **7.46 / 7.06** |
      | Swag at mid-bay (centre) | .699 (rope 512–516.5) | .715 | **6.20** |
      | Deck top | .634 (520.5) | .632 (514.5) | **5.60** (.633) |
      | Plank bottom | .551 (528.5) | .541 (525.5) | **4.75** |
      | Stringer / crossbeam bottom | .397 (543.5) | .393 (543.5) | **3.45** |
      | Peg centre on the block | .474 (536) | .479 | **4.12** |
      | Knee brace foot on the leg | .124 (570) | — | **1.10** |
      | X brace feet / tops | — | ≈ .05 / .37 | **0.45 / 3.30** |
    - **Sections:** post 17.5 px (front, 0.180 H), 20.5 px (side, 0.169 H), 17 px of 85 (top, 0.20 W) → **1.5**;
      board ends 8 px (front) and 11 px (side) thick → **0.85** (M048's); stringer 14.5 px → **1.30**; swag 5–7 px →
      **Ø 0.45**; the two wraps make a 0.66–0.73 band standing 0.27 proud of the post faces → **wrap tube Ø 0.40**.
  - **Why this size.**
    - **Against the character (5.5):** posts stand **3.25 above the deck** (hip height, 0.59 of the character); the
      wraps sit 1.5–1.9 above the deck (knee to thigh); the swags sag to **0.38 above the deck** (ankle height: a low
      rope edge, not a handrail, as on the dock); the walkway is **6.5 clear between the post lines** (9.5 of deck),
      room for three characters abreast; posts 1.5 square (chunky, as the notes ask); boards 2.19 wide, 0.85 thick.
    - **Against the kit:** the deck top **5.6 equals M048's dock deck and M043's lower lawn**; post centres 8 across
      equal the dock's, so a bridge end meets the dock's open end post line for post line (§2.1). The deck is **4.6
      above the water top 1.0** (legs on a water tile's plate at z 0, like the dock's).
- **Build frame (decision §8.2):** long axis **X** (the sheet's "FRONT VIEW" is a long side, and the kit's default
  `front` camera then shows it), +Y back, ground z 0, centred on x 0 / y 0. **Both ends open; the model is symmetric
  about x 0 and y 0.** Stage 2 puts the origin at the bbox bottom centre (it stays at 0, 0, 0; record any offset).
  This differs from M048 (long axis Y); placement rotates either as needed.

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | W (lit) | K (dark) | Y (rope + pegs) | O |
| --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (12,64,511,393) | 39–499 × 99–374 (461 × 276) | **1.670** | 41.7 % | 52.4 | 5.9 | 2.0 |
| Rear three-quarter (513,64,1011,393) | 519–988 × 81–378 (470 × 298) | 1.577 | 45.1 | 48.8 | 6.0 | 2.0 |
| Front (12,402,318,651) | 30–303 × 486–582 (274 × 97) | 2.825 | 44.4 | 49.1 | 6.4 | 2.3 |
| Side (320,402,510,651) | 341–489 × 471–592 (149 × 122) | **1.221** | 28.8 | 67.1 | 4.2 | 2.8 |
| Rear (512,402,794,651) | 522–786 × 486–582 (265 × 97) | 2.732 | 44.0 | 49.9 | 6.2 | 2.4 |
| Top (796,402,1011,651) | 833–947 × 424–614 (115 × 191) | 0.602 (W : L) | 68.9 | 30.9 | 0.1 | 0.7 |

- Shares are of W + K + Y; O and B are left out. **Verifier tolerance:** W / K ±6 points (they split on value, so the
  studio light moves them); Y ±1.5 (rope thickness and wrap size); W : H ±0.08 on f34, r34 and side; positions ±0.05.
- The f34's Y includes the pegs (its second fifth, 9.4 %). The top view's rope barely shows (0.1 %): the wraps are
  hidden under the caps' outlines and no swag is drawn there (§3.2).

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .38 | .61 | .55 | .57 | .61 | .66 | .79 | .73 | .74 | .76 | .80 | .92 | .85 | .84 | .86 | .89 | .99 | .79 | .79 | .89 | .71 |
| r34 | .36 | .57 | .51 | .55 | .61 | .74 | .67 | .68 | .71 | .75 | .80 | .91 | .84 | .84 | .86 | .89 | .99 | .80 | .78 | .88 | .69 |
| Front | .63 | .99 | .98 | .76 | .72 | .74 | .80 | .99 | .79 | .73 | .72 | .74 | .79 | .99 | .79 | .74 | .72 | .75 | .96 | .99 | .62 |
| Side | .61 | .63 | .99 | .99 | .98 | .81 | .79 | .77 | .75 | .74 | .74 | .74 | .75 | .76 | .79 | .82 | .96 | .99 | .99 | .86 | .61 |
| Rear | .63 | .99 | .98 | .77 | .74 | .75 | .81 | .99 | .80 | .74 | .72 | .73 | .79 | .99 | .86 | .74 | .73 | .76 | .96 | .99 | .63 |

- **f34:** eight peaks = the caps (f .05 far-left corner F1, .25–.30 F2, .55 F3, .80 F4; the near row N1–N4 at .15,
  .40, .65–.70, .95); the swags fill between (.55–.79). The deck rises steadily from .38 at the near-left end.
- **Front / rear:** four posts at the peaks (.99), swags dipping to .72–.74 between, the deck ends at .62–.63.
- **Side:** two posts (.99), one swag drawn between them (.74, §3.3), the deck end at .61.

**Width per height** (fraction of W at h .05 → .95):

```
f34    .07 .22 .46 .74 .93 .95 .76 .70 .45 .06
r34    .07 .31 .47 .74 .94 .94 .79 .53 .46 .06
front  .92 .92 .92 .92 .98 1.0 .92 .92 .94 .92
side   .85 .85 .85 .85 .97 .99 .85 .85 .89 .85
rear   .92 .92 .92 .92 .98 1.0 .92 .92 .94 .92
```

**Fifths** (bottom → top, % of each class): f34 W 2.1 / 19.5 / 37.3 / 35.6 / 5.6; K 8.3 / 26.8 / 35.4 / 22.0 / 7.5;
Y 0.2 / 9.4 / 33.2 / 38.3 / 18.9. r34 W 2.1 / 19.9 / 36.3 / 34.4 / 7.3; Y 0.6 / 13.2 / 30.2 / 39.3 / 16.7. Front W 6.1 /
12.8 / 39.3 / 28.4 / 13.4; K 16.4 / 17.6 / 48.3 / 12.6 / 5.1; Y 0 / 0 / 7.1 / 61.5 / 31.4.

**Level and size measurements** (sheet px; `ortho.py`, `colp.py`):

| Item | Front cell (long side) | Side cell (end) | Rear cell | Top cell | f34 / r34 |
| --- | --- | --- | --- | --- | --- |
| Post centres | 49.5 / 125 / 207.5 / 283.5 (bays 75.5, 82.5, 76) | 363 / 468 (105) | 540.5 / 613 / 695.5 / 767 (72.5, 82.5, 71.5) | x 847.5 / 932.5 (85); y ≈ 430 / 516 / 600 (3 a side) | caps F1 (65,213) F2 (180,161) F3 (296,126) F4 (410.5,105); N1 (138,246) N2 (246,194) N3 (364,160.5) N4 (474,134). r34 F (547.9,215) (635,166.4) (774.3,115.7) (897.7,88.6); N (623,249.3) (732.1,199.3) (853.7,152.3) (962,121.4) |
| Post width | 17.5 (41–58) | 20.5 | 16–17 | 17 (caps 839–856) | — |
| Post top → ground | 486 → 582 (97) | 471 → 591 (121) | 486 → 582 | — | N1 cap 246 → foot ≈ 372 |
| Rope wraps | Y 500–501, 504–505 (band 499–506); wraps stand 3 px proud each side (38–61 vs 41–58) | 488–489, 492–494 | same as front | — | two wraps on every post |
| Swag at mid-bay | 512–516.5 (Ø ≈ 5 px) | 500–507 | same | not drawn | three swags per long side |
| Deck top / plank bottom | 520.5 / 528.5 | 514.5 / 525.5 | 521 / 529 | — | |
| Stringer band | 529–543.5, x 33–300 (0.8 past the end posts) | 527–543 (crossbeam band, with the stringer ends) | 531–543 | edge strips under the board ends | dark band under the plank ends |
| Block / peg | blocks 529–543.5 at each post, peg centre y 536 (Ø 5–6) | blocks on both posts' end faces, pegs at 533 | same | ears 6 px outside the caps | block on the outer face below the deck, wider than the post |
| Deck ends | x 30 / 303: 11 px past the end posts' outer faces | x 341 / 489: 12 px past the posts' outer faces | 522 / 786 | y 436 → 604; edges x 841 / 939 = the posts' outer faces | the end boards past the end posts, the stringer end under them |
| Boards | plank-end gaps at 75, 98, 150/153, 180, 234, 257: **3 visible + 1 behind each post = 4 per bay** | one end board's side face, drawn as 3 blocks between the posts + 2 stubs outside | same | seams every 14.3 px (y 451 … 604): **6 per bay**, a seam at every post row | about 4 per bay along the near edge; exploded 5 + 9 |
| Braces | knee braces in the end bays only: foot on the end leg's inner face at y 570, top on the stringer underside ≈ 26 px in from the leg | X between the legs, feet ≈ 585, tops ≈ 546, peg at the crossing (403, 553) | same as front | — | dark diagonals between the near-end legs (f34 sheet ≈ (60–80, 300–330)) and under the far end |

### 1.3 Silhouette and composition per view

**Front three-quarter (`n_f34.png`, `z_f34a.png`, `z_f34b.png`, `z_f34under.png`, `z_f34under2.png`): governs.**
Camera at −X, −Y (**kit az ≈ −40, e ≈ 23**), clear perspective (the near end's across vector is 79 px, the far end's 70).
The −X end at the lower left, the near long side (−Y) running back to the upper right.
- **Deck:** boards run **across the width** (upper left to lower right). Their ends form a row of chunky blocks along
  the near edge, about 4 per bay, roughly flush with the posts' outer faces. Each board is a crisp box with lighter top
  edges; values vary a little board to board. A few boards seem to break near mid-width (the top view and the exploded
  draw full-width boards, §3.5). At the near-left end the deck runs on past the end posts and the stringer's end
  (with a peg dot) shows under it.
- **Posts:** eight caps above the deck. Each cap is a square with softened top edges and a small dark peg dot; faces
  show faint vertical split lines and darker streaks.
- **Rope:** two wraps round each post about 1.5–1.9 above the deck; swags sag low between the posts along both long
  sides (3 + 3). **None across either end.**
- **Under the deck:** the near stringer under the plank ends, a block with a big round pale-gold peg on every near
  post's outer face at stringer height (N2, N3, N4 clearly), the near legs (N1's reaches lowest at y ≈ 372), the far
  legs in shade, the end X braces between each end's legs.

**Rear three-quarter (`n_r34.png`, `z_r34a.png`, `z_r34b.png`).** The same composition from the other side (the
bridge is symmetric): camera at +X, +Y (**kit az ≈ 140, e ≈ 23–26**). The far-right post F4 rises highest (y 81).

**Front (`n_fs.png`, `g_front.png`).** A long side, level: four posts, three swags, the plank-end row (gaps between
3 visible ends per bay), the stringer band running the full length and **0.8 past each end post**, four blocks with
pegs (one per post, about the post's width), four legs, and **one knee brace in each end bay, from the end leg's
inner face (low) to the stringer underside, rising toward the middle at about 45° on the cell**. The middle legs have
none. The middle bay is drawn 10 % longer than the end bays.

**Side (`n_fs.png`, `g_side.png`).** An end, level: two posts, the end board's side face (drawn as 3 blocks between
the posts plus a stub outside each post), the crossbeam band with blocks and pegs on both posts' end faces, an **X
brace** between the legs with a peg at the crossing, and **a swag drawn across between the two posts** (§3.3).

**Rear (`n_rt.png`).** The other long side: identical to the front (same knee braces, no middle braces).

**Top (`n_rt.png`, the top cell).** A rectangle (W : L 0.602): boards across the width with seams at every post row,
**only three posts per side and two square bays** (§3.2), the deck edges flush with the posts' outer faces, small block
ears outside each post, a dark strip under each long edge (the stringers seen past the board ends), no swags drawn.

### 1.4 Parts (exploded (12,660,742,1181), `z_expl.png`, `z_expl_deck.png`; key parts (744,660,1011,1181), `z_keys.png`)

A near-isometric view from the front-left. **The hero governs every size**; the parts give shapes and boundaries.

| Part | Box (sheet px) | Notes |
| --- | --- | --- |
| Post (7 drawn) | e.g. (82,852,122,980); key (787,712,824,831) | A square post with **two rope wraps 0.2–0.35 of its length below the top**, cap with a dark peg dot, two dark slots near the foot (key). The exploded posts stop at the deck; separate leg stubs and "L" pieces below (§3.7) |
| Deck groups (about 5 + 9 boards) | (132,880,293,966), (293,798,597,916) | Full-width boards, chunky, a faint lengthwise line on some tops; lit tops `#E08644` |
| Plank (key) | (768,822,918,909) | One long board, top `#F2A858`, a faint line along the top (§3.8) |
| Stringer (3 drawn) | (193,948,540,1073) long; (520,886,624,963); key (768,890,918,978) | Long square beams, dark `#7C3715`, peg dots |
| Crossbeam (2 drawn) | (215,1016,329,1116) labelled; (347,913,479,973); key (790,975,887,1040) | Short beams, `#7E3C17` |
| Brace | (368,1034,468,1123) labelled; key (802,1031,893,1112) | A short square board, ends cut square on the key |
| Corner L pieces (2) | (79,1013,157,1105), (507,988,625,1088) | A leg with a short beam end on top: the leg + stringer end of a corner |
| Blocks with pegs (about 8) | e.g. (54,1009,72,1030), (468,905,511,945) | Small cubes with one round pale-gold peg head |
| Rope Segment | (132,695,540,848) strung over the posts; key (780,1121,887,1153) | A thick twisted rope, sagging, **round knob ends** on the key |

- **Underside close-up** (22,1236,290,1412): dark plank bottoms (`#6F371D` median), crossbeams and a stringer seen from
  below, a block with a peg, a leg with a diagonal brace.
- **Post junction** (301,1236,500,1412): the post rising past the deck edge; **two snug rope wraps** with the swag
  leaving from between them to the right; the plank ends butting the post on both sides; under the deck a **block on
  the post's outer face, wider than the post, with a faceted round peg head** (about 0.35 of the block's width).
- **Plank detail** (512,1236,720,1412): a chunky board (about 2.5 : 1 width to thickness, crisp edges, a lighter top
  `#F0974A`) resting on a dark stringer (`#763B17`) with a round peg head `#FCDE96` on its face.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (long axis X, ±Y long sides, ground z 0). Builder constants (decision §8.4): `W = 8.0` (post
centres across), `NB = 14` boards, `BOARD = 32 / 14 = 2.2857`, `BAY = 4 * BOARD = 9.1429`, `POST = 1.5`,
`DECK_TOP = 5.6`, `PLANK_T = 0.85`, `BEAM_D = 1.30`, `POST_TOP = 8.85`, `SINK = 0.02`.

### 2.1 The seam contract (binding; record it in the builder docstring and the export notes)

| Item | Value | Notes |
| --- | --- | --- |
| Ground / leg feet | **z 0**, flat leg bottoms | a water tile's plate; legs pass through the bed and the see-through water like the dock's |
| Deck top (walk surface) | **z 5.6**, flat, boards ± 0.02 | flush with M048's deck and M043's lower lawn; 4.6 above the water |
| Both ends | **x ±16.0**, the end boards' outer faces; no rope, no brace above the deck | walk-on seams: a 5.6 lawn, the dock's open end, or another bridge |
| Sides | boards to y ±4.75 (= the posts' outer faces); blocks to ±5.25; pegs to ±5.5 | nothing past ±5.6 |
| Post centres | y ±4.0; x ±4.571, ±13.714 | |
| Under the deck | stringers to x ±15.26 | nothing below the deck past x ±15.3 except the boards |

- **Walkability:** the walk surface is **level (0° slope)**, boards flat within ±0.02, gaps 0.10 (no step anywhere
  above 0.02). At both ends the deck is flush (≤ 0.02) with a 5.6 surface. **Steps the sheet does not solve:** from
  sand or M034's banks (1.6–1.8) the deck is 3.8–4.0 up, from the ground 5.6: those need a later stairs / ramp-end
  piece (the dock has the same need, M048 decision 3). Default Roblox jumps (JumpHeight 7.2) clear it, but it is not a
  walk.
- **With M048's dock:** turn the bridge 90° and butt one end (x −16) against the dock's open end (its end board face
  y −9.6): both decks at 5.6, both post lines at ±4.0 across, the dock's boards to ±5.1 and the bridge's to ±4.75.
- **With M043 (lower lawn 5.6):** an end against the lawn's front so the deck meets the turf flush; the end legs stand
  2.3 inside the deck end, clear of a terrace face at the seam.
- **With water tiles (M041 / M032 / M037):** legs on the plate (z 0) anywhere in open water; nothing touches the water
  mesh (the legs read through the see-through water).
- **With M034 (the stream tile) — does not fit as built.** The geometry fits the channel: along X over the tile, the
  deck is exactly the tile's 32, the end legs (x ±13.71) stand on the banks and the middle legs (±4.57) in the 14-wide
  channel. But M034's dressing leaves no clear 11-wide band across the tile: its waterline boulders B1–B4 (6.9–7.3
  wide, tops 5.6–7.4, at y 11.0 / 7.0 / −5.2 / −9.4), mid rocks M1, M2, S1 and bank rocks K1–K6 sit inside any bridge
  footprint (at y 0, K2 (−14.0, −2.4) stands under the −Y end posts and M2 (−6.8, −2.6) under the deck; B2's 5.6 top
  hits the stringers at y ≈ 4–7). A bridge over a stream needs a rock-free stream variant (a later piece) or open water
  (decision §8.1).

### 2.2 Posts, stringers, crossbeams, blocks

| Piece | Position | Size | Notes |
| --- | --- | --- | --- |
| Posts P1–P8 | centres (±4.571 / ±13.714, ±4.0) | 1.5 × 1.5, z 0 → 8.85 | cap chamfer 0.10 on the four top edges (the only bevel, §3.10); optional cap peg dot (§4.4) |
| Leg region | each post below z 3.45 | | colour only (§5); one shell per post (decision §8.5) |
| Stringers S±Y | y ±2.35 … ±3.25 (outer face sunk 0.02 into the posts' inner faces at ±3.25), x −15.26 … +15.26 | 0.9 wide × 1.32 deep, z 3.45 → 4.77 (top sunk 0.02 into the boards) | ends 0.8 past the end posts' outer faces (front cell); crisp |
| Crossbeams C1–C4 | x = each post row ± 0.45, y −2.35 … +2.35 between the stringers | 0.9 × 1.32, z 3.45 → 4.77 | end faces sunk 0.02 into the stringers |
| Blocks, outer faces (8) | each post's outer face: x = post ± 0.85, y ±4.73 → ±5.25 | 1.7 along × 1.25 tall × 0.5 proud, z 3.50 → 4.75 | sunk 0.02 into the post; open sky above (outside the board ends): the top view's ears |
| Blocks, end faces (4) | the corner posts' end faces: x ±14.444 → ±14.964, y ±3.25 … ±4.75 | 1.5 × 1.27 × 0.5, z 3.50 → 4.77 | top sunk 0.02 into the end board above; inner side touching the stringer's outer face |
| Pegs (12 + 2) | centre of each block's outer face, z 4.12; one on each X brace crossing | round, Ø 0.55, 0.25 proud incl. a 0.06 dome | 8 sides (the junction's head is faceted); sunk 0.03 into the block |

### 2.3 Deck

- **14 boards across the width**, pitch 2.2857 over x −16 … +16, each **2.186 wide** (0.10 gaps), **0.85 thick**
  (z 4.75 → 5.6), y −4.75 … +4.75 (9.5 long). **Seams on the four post rows** (x ±4.571, ±13.714), as the top view
  draws; 4 boards per bay; the end boards run 1.54 past the end posts' outer faces.
- **At the posts (decision §8.3):** the 8 boards that meet a post row (boards 1, 2, 5, 6, 9, 10, 13, 14 counted from
  −X) are **notched at both ends round the post**: an open L notch from the post's inner face (|y| 3.23) to the deck
  edge (4.75), 0.72 deep in x (to 0.02 clear of the post's face). The board is one closed prism of an 8-vertex plan
  polygon. The 6 others are plain boxes.
- **Each board** is a crisp box (no top chamfer: "no small bevels", §3.10) with a per-board height jitter of ±0.02 and
  yaw ±0.3° (no gap opening or closing past 0.06–0.14). No grain, no groove.
- **Underside:** boards rest on both stringers (sunk 0.02) and on the crossbeam under them, if any. The end boards
  overhang the stringer ends by 0.74 (supported over 1.55 of their width).

### 2.4 Braces

| Brace | From | To | Section | Sheet evidence |
| --- | --- | --- | --- | --- |
| Knee braces, both long sides (4) | the end leg's inner face (x ±12.964) at z 1.10 | the stringer underside (z 3.45) at x ±10.36 | 0.6 (in the brace's plane) × 0.45, centred in y on ±3.25 (straddling the leg / stringer line: ≥ 0.22 overlap with the leg face and with the stringer underside) | front and rear cells; ≈ 42° |
| X braces, both ends (2 × 2 boards) | each leg's inner face (y ±3.25) at z 0.45 | the opposite leg's inner face at z 3.30 (under the crossbeam's 3.45) | 0.6 × 0.35; board A x ±(13.764 … 14.114), board B ±(14.114 … 14.464) (stacked, touching at the crossing; B flush with the legs' outer end faces) | side cell; f34 near and far ends |

- Ends are cut to the faces they meet (vertical against a leg, horizontal against a stringer) and sunk 0.02. A peg on
  board B's outer face at the crossing (y 0, z 1.88). **No braces at the middle legs** (front and rear cells).

### 2.5 Rope

| Piece | Path | Size | Notes |
| --- | --- | --- | --- |
| Wraps (2 per post, 16) | rounded square round the post, centreline 0.93 from the post axis on the flats (an 8-segment ring: four flats, four 45° corners); centres **z 7.06 and 7.46** | tube Ø 0.40 | inner surface sunk 0.02 into the post faces; the two wraps touch |
| Swags (6) | both long sides, between neighbouring posts at y ±4.0 | Ø 0.45 | ends start inside the wraps (sunk ≥ 0.15) at z 7.26; **low point centre z 6.20** at mid-bay (rope bottom 5.98, 0.38 above the deck) |

- **Low-poly twisted rope (as M048):** 5–6-sided tube, a ring every ~0.6 along a swag; **turn each ring half a side**
  so the facets spiral like the sheet's twist; no fibres. Sag as a catenary sampled at the ring points.
- **Rope part (`TimberBridgeRope`):** one swag with the key part's **round knob ends** (Ø 0.6, 8 sides); in the hero the
  ends tuck into the wraps, so no knobs show.

### 2.6 Expected extents

- **Extents (build frame):** X −16.0 … +16.0 (boards); Y −5.5 … +5.5 (pegs; blocks ±5.25, boards ±4.75); Z 0 … 8.85.
  Bbox ≈ 32.0 × 11.0 × 8.85.

### 2.7 Screen checks (floor hidden; `measure_render.py`, the studio's paper colour as the second argument)

- **Self-consistency (`proj050.py`, orthographic block model):** f34 (−40, 23) W : H 1.677 (sheet 1.670; az −36 /
  −44 give 1.68 / 1.60 at e 26, e 20 / 28 give 1.78 / 1.53 at az −40); r34 (140, 26) 1.587 (1.577); side (90, 0)
  1.243 (1.221). The front cell's 2.825 against the model's **3.62** is the recorded ortho-cell miss (§3.1).
- **f34_sheet (−40, 23)** (probe az −35 / −40 / −45 × e 20 / 23 / 26, keep the best):
  - W : H 1.59–1.75 (1.670);
  - shares W 41.7 ± 6, K 52.4 ± 6, Y 5.9 ± 1.5;
  - Y fifths within ±8 of §1.2 (0.2 / 9.4 / 33.2 / 38.3 / 18.9);
  - top profile within ±0.08 (mean ≤ 0.05) of §1.2: eight cap peaks with the swags between, the deck rising from .38;
  - read: the −X end at the lower left, boards across the width with their ends as blocks along the near edge, three
    swags per side, both ends open, legs with the end X brace under the near end.
- **r34_sheet (140, 26)** (probe az 135 / 140 / 145 × e 23 / 26): W : H 1.50–1.66 (1.577); Y 6.0 ± 1.5.
- **front_sheet (0, 0)** (−Y side): four posts, three swags, 3 visible plank ends between posts, four blocks with pegs,
  two knee braces (end bays only), the stringer 0.8 past each end post; levels per §1.1; W : H ≈ 3.6 against 2.825
  (recorded).
- **side_sheet (90, 0)** (+X end): two posts, the end board's side face, the crossbeam / stringer band with two end
  blocks and pegs, the X brace with its peg; W : H 1.17–1.30 (1.221); **no swag across** (§3.3).
- **rear_sheet (180, 0):** the mirror of the front.
- **top (0, 89.9):** the sheet draws the long axis vertical: rotate the image 90° to compare. W : L ≈ 0.34 against the
  top cell's 0.602 (its two-bay drawing, §3.2); boards across the width with seams at every post row; posts flush with
  the deck edges; block ears outside each post.

## 3. View conflicts and resolutions

### 3.1 Bay length: the three-quarters (bay / W 1.35–1.38) vs front and rear (0.93) vs top (1.0)

- **Evidence:** §1.1. Both three-quarters are consistent with each other; the front and rear cells draw the long side
  at 0.78 of the height's scale (their W : H 2.8 against the model's 3.6); the top cell draws a different, two-bay
  bridge.
- **Resolution (decision §8.1):** **bay 9.143 (1.143 W)**, 3 bays, deck 32.0. The f34 governs the read (block model
  1.677 against 1.670). The front and side cells are judged on content and level fractions (which agree), not on W :
  H. **Alternatives:** bay 8 (= W, the ortho cells; deck 28.6, f34 W : H 1.78) or bay 10.8 (the three-quarters
  literally; deck 37.1, longer than a tile).

### 3.2 Posts per side: top view 3 (two bays) vs every other view 4 (three bays)

- **Resolution:** **4 per side, 3 bays** (f34, r34, front, rear, exploded). The top view is judged for its plan
  content (boards across, seams at the post rows, posts flush with the edges, ears), not its post count.

### 3.3 A swag across the end (side cell) vs open ends (f34, r34)

- **Evidence:** the f34 and r34 show no rope between the two posts at either end (blank paper between F1–N1 and
  F4–N4); the top view draws no rope. Only the side cell draws a swag between its two posts.
- **Resolution:** **no end rope; both ends open** (a bridge is walked on at both ends). The side cell's swag is a
  drawing convention (the long-side swags seen end-on would be vertical lines at the posts). The side_sheet render
  shows no swag: a recorded miss.

### 3.4 Deck width: boards past the posts (side cell, 0.88) vs flush (top cell) vs nearly flush (f34)

- **Resolution:** **board ends flush with the posts' outer faces (y ±4.75)**; the blocks (0.5 proud) and pegs (to
  ±5.5) supply the side view's stubs outside the posts. **Alternative:** boards to ±5.2 with a 0.45 sliver of board
  outside each post (needs U notches; reads as a gap beside each post).

### 3.5 Board count and layout: top 6 per bay, front and f34 4 per bay, exploded about 14 in all

- **Resolution (decision §8.3):** **14 boards, 4 per bay, seams on the post rows, notched round the posts.** No butt
  joints (the f34's apparent mid-width breaks are not in the top view or the exploded).

### 3.6 Bracing

- **Evidence:** front and rear cells: one knee brace in each end bay from the end leg; none at the middle legs. Side
  cell: an X between the end legs with a peg at the crossing. f34: diagonals between the near-end legs and under the
  far end.
- **Resolution:** **4 knee braces (the end legs, both long sides) + an X brace at each end.** Symmetric, as the front
  and rear cells are identical.

### 3.7 Posts: one piece (every assembled view) vs post + leg stubs + corner L pieces (exploded)

- **Resolution (decision §8.5):** **one closed post per position**, ground → cap; the leg region is colour only. The
  exploded's split is a drawing of how the frame goes together, not hidden stacked faces.

### 3.8 Plank top line (key plank, plank close-up)

- **Resolution:** not modelled (a groove would read as 28 boards from above and the f34 board tops show none). Per-board
  tint carries the board-to-board variation.

### 3.9 Pegs: "wooden pegs" (junction text) vs pale gold rendering

- **Resolution (decision §8.9):** **wooden peg heads coloured pale gold** (`m050_peg`, rough 0.55, metal 0): the text
  says wood; the colour follows the render. **Alternative:** M048's brass (metal 0.5) for a dock-and-bridge match.

### 3.10 "Broad flat-shaded faces, no small bevels" vs softened caps and M048's chamfered boards

- **Resolution:** crisp boxes everywhere (boards, stringers, crossbeams, blocks, braces); **only the post caps get
  one 0.10 chamfer** (their corners read softened in the front, side and f34 cells). This differs from M048's 0.06
  board chamfer: the sheet's note governs (decision §8.3).

### 3.11 Leg colour: mildly darker (assembled) vs uniform (exploded and keys)

- **Evidence:** front cell middle posts: cap v .70, above the deck .65, leg .58–.61 (and 0.1 less saturated); f34 legs
  `#7E3911` / `#72320D` (v .45–.49) against the post above the deck `#8A3D0A` (.54): **0.87–0.92**. M048's legs were
  0.84 and much browner.
- **Resolution:** legs darken **by position** below the stringers, half as strongly as M048's (§5.5). Recorded.

### 3.12 Rear three-quarter

- The bridge is symmetric about both axes, so the "rear" three-quarter is the same composition from the other diagonal:
  camera (140, 26). Its slightly lower W : H (1.577) suggests a higher elevation than the f34's.

### 3.13 Cast shadow

- The sheet's ground shadows are pale blue-grey (B). Render every `*_sheet` view with the studio floor hidden.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

All pieces are explicit low-poly solids from vertex lists (boxes, plan-polygon prisms, cut-end braces, tubes). **No
booleans are needed**: every piece is its own closed shell, touching or sunk 0.02 into what carries it.

**Helper reuse (decision §8.10).** `m048.py` already has `_prism` (plan polygon → prism, optional top chamfer),
`_box`, `_brace_quad`, `_tube` (twisted rope with groove strand and pinch), `_knob`, `_bolt`, `_catenary`,
`coil_path` / `coil`, `swag_ends` / `swag` and a notched `board_outline`. If M048 is committed when M050 starts,
import those helpers from `m048` (models already import m012 / m033 / m040); if it is still in flight, copy them into
`m050.py`. Never import M048's constants, and never edit `m048.py`.

1. `post(i)` → each of the eight posts: a prism with a 0.10 cap chamfer, its block(s) and peg(s), its two wraps.
   **Part `TimberBridgePost`** = the −X / −Y corner post with both blocks, both pegs and its wraps (key "Post"),
   compared with the key part and the junction close-up.
2. `board(i)` / `deck()` → the 14 boards (§2.3). **Part `TimberBridgePlank`** = one plain board (key "Plank").
3. `stringer(side)` → **Part `TimberBridgeStringer`**.
4. `crossbeam(x)` → **Part `TimberBridgeCrossbeam`**.
5. `knee(sx, sy)`, `xbrace(sx)` → **Part `TimberBridgeBrace`** = one knee brace.
6. `wrap(post, z)`, `swag(p0, p1)` → **Part `TimberBridgeRope`** = one swag with knob ends (key "Rope Segment").
7. **Hero `TimberBridge`** = 8 posts (with 12 blocks, 12 pegs, 16 wraps) + 14 boards + 2 stringers + 4 crossbeams +
   4 knee braces + 2 X braces (4 boards, 2 pegs) + 6 swags.
   - Each piece a closed shell in one object; no unions.
   - `M.fix_bowties`; origin at the bbox bottom centre; transforms applied.
8. **Parts shot** (az −35, e 25), laid out like the exploded: boards above the stringers, posts at the corners, the
   crossbeam and brace in front, the rope above.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a long level trestle footbridge on eight square legs, chunky boards across the width, eight posts
   with snug double rope wraps and six low swags (both ends open), blocks with pale-gold pegs at the stringer line,
   end-bay knee braces and end X braces.
2. **f34_sheet, r34_sheet, front_sheet, side_sheet, rear_sheet, top** per §2.7.
3. **Level check (numbers):** leg feet z 0.00; stringers and crossbeams 3.45 → 4.77; deck top 5.60 ± 0.02 on every
   board; wraps 7.06 / 7.46; swag low points 6.20 ± 0.05; post tops 8.85.
4. **Underside extra** `under_cu (−35, −30)` against the underside close-up: board bottoms on the stringers and
   crossbeams, a knee brace meeting leg and stringer, the X brace, a block and peg; nothing floating.
5. **Junction extra** `junc_cu (−60, 15)` framed on the −X / −Y corner post: notched board ends against the post, the
   wraps snug, the swag leaving from between the wraps, the block and peg under the deck edge.
6. **Scale shot:** 5.5-stud character markers on the deck at x 0 and on the ground beside a leg.
7. **Kit shot** (if M048 / M043 are in the kit file): the bridge's −X end against the dock's open end and its +X end
   against an M043 lower lawn, from (45, 20): decks flush at 5.6.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Posts (prism + 0.10 cap chamfer; + cap peg dot) | 8 | 20 (28) | 160–224 |
| Blocks (crisp boxes) | 12 | 12 | 144 |
| Pegs (8-sided, domed) | 14 | 30 | 420 |
| Boards: plain / notched (8-vertex plan prism) | 6 / 8 | 12 / 28 | 296 |
| Stringers | 2 | 12 | 24 |
| Crossbeams | 4 | 12 | 48 |
| Knee braces | 4 | 12 | 48 |
| X brace boards | 4 | 12 | 48 |
| Wraps (5 sides × 8 segments) | 16 | 80 | 1280 |
| Swags (6 sides × 13 segments + caps) | 6 | 164 | 984 |
| **Hero** | | | **about 3450–3520** (limit 4000) |
| Parts: Post / Plank / Stringer / Crossbeam / Brace / Rope | | | ≈ 264 / 12 / 12 / 12 / 12 / 260 (limit 1000) |

- **The wraps are the cost.** If the hero is over 3900: swags to 5 sides (−160), then pegs to 6 sides (−110). Wraps at 6
  sides (+256) only if the budget allows. Never drop a wrap (two per post is a defining look), a swag, a peg or a board.

### 4.4 Shape targets (binding; check with `M.audit` and own bmesh code)

| Target | Posts | Boards | Stringers / crossbeams / braces | Rope | Pegs |
| --- | --- | --- | --- | --- | --- |
| Section | square 1.5; faces planar | 2.186 × 0.85; tops flat | square-ish boxes | round-ish 5–6 sides, spiral facets | round 8 sides |
| Edges | cap chamfer 0.08–0.12; sides sharp | crisp | crisp | — | dome ≤ 0.08 |
| Not | no rounded tops, no taper, no octagonal caps | no gaps > 0.14, no grain, no warping > 0.02 | no floating braces | **not thin**: swags Ø 0.43–0.47, wraps Ø 0.38–0.42; no fibres; no rope through a board or post | not flat discs, not cubes |

- **Chunky, not skinny:** board W : T 2.4–2.7; post W ≥ 0.16 of its height; rope Ø ≥ 0.05 of the post height.
- **Optional cap peg dot:** a 0.22 square inset 0.03 into each cap's top face (+8 tris per post), in `m050_wood_dark`;
  it reads in the f34 and the key part. Drop it first if the notes' "no additional details" is preferred.

### 4.5 Stages 2 and 3

- **Stage 2:** every shell closed and manifold; zero non-manifold edges and verts (`nonmanifold_verts` 0), boundary,
  wire and loose elements; no zero-area faces or n-gons (the notched boards' 8-gon tops and bottoms, the wrap rings and
  the peg domes are the places to check); normals outward; **0 winding errors** in `build()`'s problems list (STAGES
  "Consistent winding"; the notched boards are non-convex: triangulate the plan polygon with ear clipping, not a fan
  from vertex 0, and check each triangle's normal against the face's); no corners under 5° on visible faces; the deck
  top planar at 5.60 ± 0.02.
- **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box, sd ≤ 1.5)

| Swatch | Header box / §5 copy | Hex (header / §5) | HSV | Use |
| --- | --- | --- | --- | --- |
| 1 Orange wood | (736,19,762,43) | `#BF743D` / `#B76E3A` | 25°, 0.68, 0.75 | the framing's paint tone (between the rendered tops and the vertical faces) |
| 2 Tan | (783,19,809,43) | `#E6C18F` / `#E6BA80` | 34°, 0.38, 0.90 | hue reference for the rope (the rendered rope is brighter) |
| 3 Cream | (830,19,855,43) | `#DDD4C6` / `#DED1BE` | 36°, 0.10, 0.87 | **unused** (nothing on the sheet renders cream; nearest is a peg highlight) |
| 4 Grey | (877,19,902,43) | `#A2ABB1` / `#A6AFB4` | 204°, 0.08, 0.69 | **unused** (no metal or stone) |
| 5 Green | (924,19,949,43) | `#84A457` / `#85A655` | 85°, 0.47, 0.64 | **unused** (no moss or grass) |
| 6 Blue | (970,19,996,43) | `#36A3D0` / `#359FD1` | 198°, 0.74, 0.82 | **unused** (no water drawn) |

### 5.2 Rendered regions (`samp050.py`; median / lit quartile / shade quartile)

| Region | f34 / r34 | front / side | top | keys / exploded / close-ups |
| --- | --- | --- | --- | --- |
| Board tops | **`#DE833B`** (27°, .73, .87) / lit `#EF9747`; r34 `#DE843D` | | `#D47935` (26°, .75, .83); board-to-board value sd 0.012, range 0.043 | exploded `#E08644`; key plank `#F2A858`; plank detail `#F0974A` |
| Board ends (vertical) | | front **`#B25415`** (24°, .88, .70); side end face `#A25020` | | |
| Post faces above the deck | N3 `#8A3D0A` (24°, .93, .54) | front `#A64E13` (24°, .89, .65) | | key post `#8B3D12`; junction `#81360E` |
| Caps | N3 top **`#F4903E`** (27°, .75, .96) | front cap `#B4581A` (lit `#F79435`) | **`#F39641`** (29°, .73, .95), lighter than the boards beside them | |
| Stringers / crossbeams | | front stringer `#954B1F` (22°, .79, .58); side crossbeam `#7A462B` | | key stringer `#7C3715`; key crossbeam `#7E3C17`; exploded `#7D3B1D`; plank detail `#763B17` |
| Blocks | N3 `#A34707` | front `#B2520C` | | |
| Legs (below the stringers) | N1 **`#7E3911`** (22°, .87, .49); N4 `#72320D` | front `#9B5224` / `#A3511C` (v .58–.64); side `#8A4825` | | |
| Braces | | front knee `#9B4918`; side X `#803F22` (19°, .73, .50) | | key brace `#8C3F12` |
| Board bottoms (shade) | | | | underside close-up K `#6F371D` |
| All dark wood (K) | f34 `#78350F` / r34 `#783610` | | | |
| Rope | f34 **`#F8CD74`** (40°, .53, .97) / lit `#FDE997` / shade `#E8B155`; r34 `#F9CF78` | front swag `#F9D58D` (40°, .43, .98); wraps `#F5C954`; side `#F8D188` | | key `#FAD78C`; exploded `#F9D275`; junction `#FCD581` |
| Pegs | `#F2D088` (41°, .44, .95), `#F8D08B`, `#FAC674` | front `#E4C89C` (36°, .32, .90) | | junction `#FBDE92`; plank detail `#FCDE96` (42°, .40, .99) |

### 5.3 How the colour works

**Wood: one warm orange timber family, by role and position, never by facing — the same family as M048.** The sheet's
board tops (`#DE833B`) are within 13 of M048's (`#E19044`), its post faces (`#8A3D0A`) within 10 of M048's (`#8D4212`),
its rope (`#F8CD74`–`#F9D58D`) the same as M048's (`#F8D088`).
- The lit tops (27°, sat 0.73) against the vertical faces (24°, sat 0.88, value 0.54–0.70) is mostly the light: a
  **hue miss of 2–4° on the vertical faces is a known miss**, not a key error.
- **Role:** boards `m050_wood`; posts and blocks `m050_wood_deep`; stringers and crossbeams `wood_deep` with 35 %
  `wood_dark` (they read a step darker than the post faces in every cell: `#7C3715` against `#8B3D12` on the keys).
- **Position:**
  - **caps lighter:** the top 0.45 of each post blends toward `m050_wood_light` (rising to 60 % on the cap faces):
    the f34 cap `#F4903E` and the top view's caps `#F39641` against boards `#DE833B` / `#D47935`;
  - **legs darker, mildly:** below the stringer bottom (z 3.45) the posts blend toward `wood_dark` over 0.6 (3
    steps) to **50 %** at z 2.85 and below (value 0.87–0.92 of the post above, §3.11);
  - **braces** 60 % `wood_dark` (`#803F22`, `#8C3F12`);
  - **blocks** `wood_deep` with 15 % `wood` (front `#B2520C` a touch brighter than the post `#A64E13`).
- **Boards:** per-board tint ±0.03 (the sheet's boards differ by 0.012 sd in value); one broad lighter field (15 %
  `wood_light`) across the deck; two or three boards a step deeper (15 % `wood_deep`).
- **Not red:** keep the board key's hue at 26–29° and R − G ≤ 95; check the f34 board-top median hue ≥ 26° (W08's dock
  and footbridge both rendered "slightly red" / "flat orange").

**Rope.** One warm golden tan, brighter and more yellow than the tan swatch: `m050_rope` on the outer strands and
`m050_rope_dark` at 45 % on the groove strand, chosen **by the strand's index round the tube (its role in the twist),
never by the face's normal**. The rope reads clearly lighter than every wood face.

**Pegs.** Pale gold wooden peg heads `m050_peg`, a touch paler and less saturated than the rope; a lower roughness so
they catch a highlight like the sheet's.

### 5.4 Keys (start from M048's calibrated hexes; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are medians of unshadowed rendered regions, not swatches. `K.sample` kinds: `"brown"` for the
woods, `"vivid"` for rope and pegs. **Start values:** `m048.py`'s calibrated `PALETTE` (today: wood `#B8732F`,
wood_light `#C2803A`, wood_deep `#7E4314`, wood_dark `#5C391E`, rope `#EEC87C`, rope_dark `#99601A`, brass `#EBC772`)
— the same studio and light, so they should land within a few units; read them from the file at build time.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m050_wood` | **`#DE833B`** board tops (r34 `#DE843D`, exploded `#E08644`) | 26–29°, 0.68–0.76, R > G > B | boards; default | rough 0.85, metal 0, low spec |
| `m050_wood_light` | `#F2933F` (f34 cap top `#F4903E`, top-view caps `#F39641`) | 27–30°, 0.70–0.76 | caps and the top 0.45 of each post (to 60 %); the deck's lighter field at 15 % | rough 0.85 |
| `m050_wood_deep` | `#8B3D10` (f34 post `#8A3D0A`, key post `#8B3D12`, junction `#81360E`); check the front_sheet post faces near `#A64E13` and board ends near `#B25415` (± 18, light) | 22–26°, 0.80–0.90 | posts, blocks; stringers and crossbeams with 35 % dark; deeper boards at 15 % | rough 0.85 |
| `m050_wood_dark` | `#6F3518` (f34 legs `#72320D`–`#7E3911`, side X `#803F22`, underside `#6F371D`) | 19–24°, 0.72–0.85 | legs (to 50 %), braces (60 %), stringers (35 %), the cap peg dot | rough 0.9 |
| `m050_rope` | **`#F8D088`** (f34 `#F8CD74`, front `#F9D58D`, side `#F8D188`, key `#FAD78C`) | 38–42°, 0.43–0.53, value ≥ 0.92 | swags, wraps, knob ends | rough 0.95, low spec |
| `m050_rope_dark` | `#BE7019` (M048's groove target; the sheet's swag mid-tones `#E2A455`–`#ECAE5F`) | 32–36°, 0.70–0.85 | the groove strand at 45 % | rough 0.95, low spec |
| `m050_peg` | `#F6D48E` (f34 `#F2D088` / `#F8D08B`, junction `#FBDE92`, plank detail `#FCDE96`) | 38–43°, 0.36–0.46 | peg heads | rough 0.55, metal 0 (decision §8.9) |

**Calibration warnings:**
- **Board tops:** f34 W-class median within 12 of `#DE833B`, hue 26–29°, sat ≥ 0.66. Not red (hue < 25°), not brown
  (value < 0.8), not yellow-tan (hue > 31°).
- **Vertical faces:** front_sheet board ends within 18 of `#B25415`, post faces within 18 of `#A64E13`, stringer face
  within 18 of `#954B1F`; the value order **board ends > post faces > stringer ≥ legs** must hold.
- **Legs:** visibly but mildly darker than the posts above (value ratio 0.85–0.93), not M048's brown legs.
- **Caps:** clearly lighter than the board tops beside them in the top render.
- **Rope:** f34 Y median within 12 of `#F8CD74`, hue 38–42°, clearly lighter than any wood. Not white-cream, not
  orange.
- **Pegs:** pale gold, distinct from the rope by being paler and smoother; not grey (the grey swatch is unused), not
  wood-orange.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Boards:** `wood` base; per-board tint ±0.03; `wood_light` by a broad noise field (scale ≈ 0.08, one or two patches
  along the deck) at 15 %; 2–3 boards 15 % `wood_deep`. **Hard edges** only between boards (each board is its own
  shell).
- **Posts:** `wood_deep` base; `wood_light` by height over the top 0.45 of the post (rising to 60 % on the cap faces);
  `wood_dark` by height below z 3.45, 3 steps to 50 % at z 2.85.
- **Stringers, crossbeams:** `wood_deep` + 35 % `wood_dark`; per-member tint ±0.03.
- **Braces:** 60 % `wood_dark`. **Blocks:** `wood_deep` + 15 % `wood`.
- **Rope:** strand roles (§5.3); per-swag tint ±0.02.
- **Hard edges only** where materials meet: rope | post, peg | block, board | post.

### 5.6 Texture (Tint) and finish

- **Tint:** boards amp 0.03 per board (whole board) plus 0.02 at scale 0.3; framing 0.03 per member; legs 0.03; rope
  0.02 per piece; pegs none. **Never per-triangle confetti**, no grain stripes (the faint streaks on the sheet's posts
  are carried by the per-member tint).
- **Finish:** wood rough 0.85–0.9, metal 0, low spec; rope rough 0.95, low spec; pegs rough 0.55, metal 0. No emission
  anywhere.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Shares** per §2.7; **colours** per the §5.4 warnings, in f34_sheet, front_sheet and top. `K.check` facing
  correlation < 0.5 on every wood material (board tops and ends are one key; post faces one key).

## 6. Joins and contact (no floating dressing)

- **Posts:** feet flat on z 0 (each post one shell, ground → cap).
- **Stringers on posts:** each stringer's outer face sunk 0.02 into the four posts' inner faces; its top sunk 0.02 into
  the boards.
- **Crossbeams:** end faces sunk 0.02 into the stringers' inner faces; tops sunk 0.02 into the boards.
- **Boards on the frame:** every board's underside sunk 0.02 into both stringers (and the crossbeam under it, if any);
  notched boards clear the post faces by 0.02 (no coincident faces); board-to-board gaps 0.10 (no overlaps).
- **Blocks:** sunk 0.02 into the post faces; the end-face blocks also sunk 0.02 into the end board above and touching
  the stringer's outer face. **Pegs:** sunk 0.03 into the block (or X board B).
- **Braces:** each end face flush with (sunk 0.02 into) the leg face or stringer underside it meets; X boards touch each
  other at the crossing.
- **Rope:** wraps' inner surfaces sunk 0.02 into the post faces; the two wraps touch; swag ends sunk ≥ 0.15 into the
  wraps. **No rope passes through a board or a post** (the swags hang at y ±4.0, inside the deck edge, and their low
  points are 0.38 above the deck).
- **Chain to ground:** boards → stringers → posts → ground; crossbeams → stringers; wraps → posts; swags → wraps;
  blocks → posts; pegs → blocks; braces → legs and stringers.
- **Count floating shells before reporting** (STAGES; 035 and 036 failed round 1 on this): **0**. A shell floats if its
  nearest distance to every other shell and the ground is > 0.03, or if it doesn't chain to the ground.
- **Buried shells:** no peg, wrap or block more than 0.05 inside a post or board (ray parity against the posts and
  boards after the final placement), as STAGES now asks (046 had leaves inside a core).
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0 (peg domes, wrap rings).
- **Winding:** 0 errors per shell (the notched boards' non-convex caps and the hand-listed box and brace builders are
  where a reversed face slips in; 044's wedge back face).

## 7. Water, lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** sunlit timber, tan rope and pale-gold pegs on white paper. **No water, foam, glow, light,
sparkle, dust, smoke or VFX callout** ("No additional details, props or text").

- **Water and foam: none in the model.** No `*water*` key, no foam mesh, no sockets.
- **Stage 5 (lighting): skip, and record why.** No emissive faces, no PointLight. Studio notes (Requires Manual
  Validation):
  - the boards read warm orange (not red, not brown) under the game's sun; caps lighter, legs a little darker;
  - the rope reads golden tan, the pegs pale gold;
  - **a character walks onto the deck from a 5.6 surface at either end, across it, and off the other end**; the low
    swags are an edge marker, not a guard rail (a 0.38–0.6 rope will not reliably stop a running character; if edge
    safety matters, Studio adds an invisible collider: not part of this model).
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".**
- **Collision:** hero `precise` (the deck walkable, the posts and rope solid, the space under the deck open);
  `TimberBridgePlank` `box`; `TimberBridgePost`, `Stringer`, `Crossbeam`, `Brace` `hull`; `TimberBridgeRope` `none`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json` and the repo
text (`git grep`) for Bridge, Plank, Timber, Rope, Span, Stringer, Trestle:
- **W08** owns `Footbridge`, `FootbridgePost`, `FootbridgePlank`, `FootbridgeStringer`, `FootbridgeCrossbeam`,
  `FootbridgeBrace`, `FootbridgeRopeSegment`, `FootbridgeShortSpan`, `FootbridgeArched`, `FootbridgeBroken` (this
  sheet's own labels under the old kit's prefix), `RopeCrossing*` (incl. `RopeCrossingPlank`), `Dock*`,
  `Boardwalk*`, `GantryRopeLift*`, `TimberHut*`, `TimberFence*`; keys `w08_*`.
- Other names: `MinecartBasePlank`, `LookoutPlatformFloorPlanks`, `WallWalkFloorPlank`, `WayfindingPostRopeTie`,
  `TableAndSeatingTrestle`, `NaturalArchTopSpan`, `StoneGateSpan`; M048's `TimberDock*` (keys `m048_*`).
- **`TimberBridge` and `m050_` occur nowhere** in the builders, the manifests or the repo text. (`.blend` contents were
  not decompressed for this study; `M.mk` renames a clash to `<name>M050`, so check the built names once.)

| Object | Part | Why |
| --- | --- | --- |
| `TimberBridge` | hero: posts, boards, stringers, crossbeams, braces, rope, blocks, pegs | W08 owns `Footbridge*`; parallels `TimberDock` |
| `TimberBridgePost` | "Post": the −X / −Y corner post (full height) with its blocks, pegs and wraps | |
| `TimberBridgePlank` | "Plank": one plain board | |
| `TimberBridgeStringer` | "Stringer" | |
| `TimberBridgeCrossbeam` | "Crossbeam" | |
| `TimberBridgeBrace` | "Brace" (a knee brace) | |
| `TimberBridgeRope` | "Rope Segment" (one swag with knob ends) | |

- Palette keys `m050_wood`, `m050_wood_light`, `m050_wood_deep`, `m050_wood_dark`, `m050_rope`, `m050_rope_dark`,
  `m050_peg` (§5.4). Collection `Kit/M050 Timber Bridge`. No sockets.

**Decisions needed (a recommendation each):**
1. **Size and crossing** (§1.1, §2.1, §3.1): **post centres 8 across × 3 bays of 9.143; deck 32.0 long, top 5.6; posts
   to 8.85; overall 32.0 × 11.0 × 8.85** (recommended: the f34's proportions between the ortho cells and the
   three-quarters; the deck is one 32-stud tile and level with the dock and M043's lower lawn, so it crosses **a gap
   between 5.6 surfaces — lawn to lawn, dock to lawn — over open water or low ground**, legs on z 0).
   - Or **bay 8** (deck 28.6; the ortho cells' squarer bays; f34 W : H 1.78 against 1.670).
   - **Not recommended: over M034 as built** (its boulders and rocks fill every bridge-wide band, §2.1), nor **a low
     bank-level crossing** (deck ≈ 1.9 needs a frame shallower than the sheet's 2.15 of boards + stringers; that is a
     different piece, like W08's old footbridge). A rock-free stream variant would be a later tile.
2. **Build frame:** **long axis X, symmetric about both axes, both ends open** (recommended: the sheet's front view is
   a long side, the kit's `front` camera then matches it, and the bridge lies across M034-style streams without
   turning). Or long axis Y like M048.
3. **Boards** (§2.3, §3.4, §3.5, §3.10): **14 full-width boards, 2.186 × 0.85, 4 per bay, seams on the post rows,
   ends flush with the posts' outer faces, the 8 boards at post rows L-notched round the posts, crisp edges (no
   chamfer)** (recommended). Or keep M048's 0.06 top chamfer for a closer dock match (against the sheet's "no small
   bevels").
4. **Builder parameters:** **write `m050.py` with `W`, `NB`, `BOARD`, `BAY`, `DECK_TOP`, `POST_TOP` constants; build
   only the drawn version now** (recommended), so a 10.4-level bridge (M040 plateaus) or a two-bay short span is a
   parameter change.
5. **Posts** (§3.7): **one closed post per position, ground → cap, 1.5 square, 0.10 cap chamfer; legs darkened by
   colour below the stringers** (recommended). Or post + leg as two stacked shells (the exploded's split).
6. **Framing and bracing** (§2.2, §2.4, §3.6): **stringers inside the post lines (0.9 × 1.32, 0.8 past the end
   posts), 4 crossbeams at the post rows, 12 blocks with pegs (8 outer faces + 4 corner end faces), 4 knee braces in
   the end bays, an X brace at each end with a crossing peg, nothing at the middle legs** (recommended: front, rear,
   side cells and the f34).
7. **Rope** (§2.5, §3.3): **two wraps per post (Ø 0.40 at z 7.06 / 7.46), six swags along the long sides only (Ø
   0.45, low point 6.20), none across the ends, twisted 5–6-sided tubes with spiral facets, no knot** (recommended).
   Or add end swags (the side cell's drawing; would close both walk-on ends).
8. **Colour** (§5): **M048's timber family by role and position: boards `#DE833B`, posts and blocks `#8B3D10`,
   stringers 35 % darker, caps toward `#F2933F`, legs 50 % toward `#6F3518`, braces 60 % dark; rope `#F8D088` with a
   45 % groove strand `#BE7019`; pegs `#F6D48E`; the cream, grey, green and blue swatches unused** (recommended). Never
   by facing.
9. **Pegs** (§3.9): **wooden (rough 0.55, metal 0), pale gold** (recommended: the junction text). Or M048's brass
   finish (metal 0.5).
10. **Helpers:** **import M048's geometry helpers if `m048.py` is committed, else copy them; never its constants**
    (recommended).
11. **Packaging:** **one hero object of closed shells (no booleans); six parts as the key labels: Post, Plank,
    Stringer, Crossbeam, Brace, Rope** (recommended).
12. **Comparison cameras** (§2.7): `f34_sheet (−40, 23)` governing (probe az −35 / −40 / −45 × e 20 / 23 / 26);
    `r34_sheet (140, 26)`; `front_sheet (0, 0)` (−Y side); `side_sheet (90, 0)` (+X end); `rear_sheet (180, 0)`;
    `top (0, 89.9)` (compare rotated 90°). Extras: parts shot (−35, 25), `under_cu (−35, −30)`, `junc_cu (−60, 15)`,
    the scale shot, the kit shot. Floor hidden in every `*_sheet` render.
13. **Stages 5 and 6:** **skip both, recorded; no water, foam or sockets** (recommended).
14. **Collision** as in §7 (recommended).
15. **Budget** (§4.3): **4000 limit, plan about 3450; cut swag sides, then peg sides** (recommended).
16. **Names** as proposed: `TimberBridge*`, keys `m050_*`.

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **A hovering plank carpet** (WorldModeling §13.2). Load-bearing first: legs on the ground, stringers on the posts,
   crossbeams between the stringers, boards on the frame, braces meeting real faces. The underside render must show
   every board resting on both stringers.
2. **Floating or buried dressing** (STAGES; 035 and 036 round 1; 046's leaves inside a core). Wraps hug the posts
   (sunk 0.02, never standing off), swag ends sit inside the wraps, pegs sit in the blocks, blocks on the posts.
   Count floating shells: **0**; buried (> 0.05 inside a post or board): **0**.
3. **Inward faces / broken winding** (044's wedge back face; STAGES "Consistent winding"). Every box, notched board,
   brace, peg and tube is hand-listed: 0 winding errors per shell, checked with a parity ray test, not only the signed
   volume. The notched boards' non-convex 8-gon caps are the new risk: ear-clip them and check every triangle.
4. **Thin rope that reads as an outline** (W08's rope; M034's foam outlines). Swags Ø 0.45, wraps Ø 0.40, golden and
   lit, sagging to just above the deck; two distinct fat wraps per post. Not a thin line, not a halo round the posts.
5. **Wood that reads red, brown or flat orange** (W08 dock "slightly red", W08 footbridge "flat orange"; 012's wood).
   Board tops hue 26–29°, sat 0.66–0.76, value ≥ 0.82; posts a step deeper; stringers deeper still; legs only
   mildly darker; per-board tint so the deck isn't one flat colour.
6. **Colour by facing.** The sheet's light tops and dark sides are the light. Role (board / framing / rope strand) and
   position (cap height, leg zone) only; `K.check` < 0.5 on every material.
7. **Egg or blob shapes where the sheet is square** (M034 / M037 "egg boulders"). Posts, boards, stringers, blocks and
   braces are crisp boxes; only the caps carry one chamfer; pegs round but flat-domed. No subdivision, no smooth
   shading.
8. **Proportions from the ortho cells.** The front and rear cells are drawn horizontally compressed and the top cell
   is a two-bay drawing; the f34 governs (bay 1.143 W, H 1.106 W).
9. **Ropes across the ends** (the side cell's convention). Both ends stay open: six swags, none across x ±16.
10. **Spiky foliage:** none on this sheet; add none (no moss, grass or props: "No additional details, props or text").
11. **Budget.** The wraps and swags are about 60 % of the count. Follow the cut order in §4.3; never drop a wrap, swag,
    peg or board.
12. **Names and scope.**
    - No `Footbridge*`, `RopeCrossing*`, `Dock*` or `Boardwalk*` (W08); no `TimberDock*` (M048).
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit other models' builders, `kit_models.py`, `kit_mcp.py`, `build_kit.py` or `lib/vfx.py` (frozen).

## Decisions (main session, 2026-10-29)
All the recommendations are accepted.
1. **Size and crossing.** Post centres are 8 across, with three bays of 9.143. The deck is 32.0 long (one tile). Deck top is at 5.6 and post tops at 8.85. The bridge crosses a gap between 5.6 surfaces, lawn to lawn or dock to lawn. It is not built to sit over M034 as that tile is now; record that as a known limit.
2. **Orientation.** The long axis runs along X, and the bridge is symmetric about both axes.
3. **Boards.** 14 boards, 2.186 × 0.85, with seams on the post rows and **crisp edges with no chamfer**, as the sheet's note says. Boards at post rows are L-notched around the posts.
4. **Posts.** One closed post per position, 1.5 square, with a 0.10 cap chamfer. Legs are darkened by position only, to about 50 % of `wood_dark`.
5. **Framing.** Stringers, 4 crossbeams, 12 peg blocks, 4 knee braces in the end bays, and 2 end X braces. Nothing at the middle legs.
6. **Rope.** Two wraps per post at Ø 0.40, and six swags along the long sides only at Ø 0.45 with a low point of 6.20. No rope across the ends. The rope must not read as a thin outline.
7. **Colour.** Use M048's timber family, calibrated to this sheet. Colour by role and position, **never by facing**, and the wood must not read red. Leave the cream, grey, green and blue swatches unused.
8. **Pegs.** Wooden, pale gold, roughness 0.55, metal 0.
9. **Helpers.** Import M048's geometry helpers if they are committed; never import its constants.
10. **Stages 5 and 6.** Skipped and recorded. Collision is precise on the hero, hull on the framing, box on the plank, and none on the rope.

Every piece is its own closed shell, with **no floating pieces** and **0 winding errors**. The hero stays under 4000 tris; if it runs over, cut the swag sides first, then the peg sides. The f34 shares (W 41.7, K 52.4, Y 5.9, each ±4) are binding.
