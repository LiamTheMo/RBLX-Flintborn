# 052 Boardwalk — spec

Reference: `art/blender/assets/references/052.png` (1024 × 1536 px). The sheet's title is "51 | BOARDWALK / INDIVIDUAL
ASSET PRODUCTION REFERENCE" and its footer "FLINTBORN — INDIVIDUAL MODEL STUDY … PAGE 51/132" (the printed 51 is the
generator's number; INDEX.md row 52 calls it "Flintborn Boardwalk model study").
Builder: `art/blender/kit/mcp/m052.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no water, glow or effect** (§7).

Sheet text:
- **Header:** "VISUAL STYLE & PALETTE": five unlabelled swatches (orange wood, tan, grey, green, blue) and the notes
  "Chunky, cartoony, primitive, low-poly aesthetic." "Broad flat-shaded faces, clean solid colors." "Warm timber, pale
  faceted rock (not used in this asset)."
- **Cells:** "1 ASSEMBLED MODEL (HERO VIEWS)": "FRONT THREE-QUARTER VIEW", "REAR THREE-QUARTER VIEW"; "2 ORTHOGRAPHIC
  VIEWS (CONSISTENT GEOMETRY)": "FRONT VIEW", "SIDE VIEW", "REAR VIEW", "TOP VIEW". The front, side and rear cells are
  level (no plank tops show); the top view is a plan with the long axis horizontal.
- **Exploded:** "3 EXPLODED CONSTRUCTION (REUSABLE PARTS)": labels "Rail Post", "Floor Plank", "Stairs", "Crossbeam",
  "Support Post". Also drawn, unlabelled: a rail post split into a cap block over a shaft; two post–rail–post frames
  (left: two posts with bolt blocks and a rail plank; upper right: the same); three loose rail planks; two floor-plank
  groups of 5 (one plank of the right group **notched** at its end); a long beam on two support posts with bolt blocks
  and a **knee brace** at the right post; 3 stair treads on a sloped stringer; red and blue dashed drop arrows.
- **Key parts:** "PARTS LIST (SAME AS REFERENCE)": "Rail Post / Support Post" (a square post, a hex bolt on one face
  near the top, a dark peg dot on top), "Rail Plank", "Floor Plank" (a faint line along the top), "Stairs" (**4 treads**
  on a sloped stringer with a vertical leg under the top tread), "Crossbeam", "Brace" (a short leg with a diagonal: an
  L knee brace).
- **Close-ups:** "4 CONSTRUCTION CLOSE-UPS": "A. STAIR JUNCTION" — "Stairs attach to side support post and crossbeam
  with simple plank join."; "B. UNDERSIDE VIEW" — "Crossbeams and braces support the floor planks. Simple, sturdy
  construction."; "C. POST / RAIL JUNCTION (CROSS-SECTION)" — "Rail planks join to post with flat faces. Simple
  overlapping geometry, clean edges." (labels "Rail Plank", "Joining Surface (flat face to flat face)", "Support Post").
- **Game context:**
  - **W08 owns the old kit's boardwalk** (`art/blender/scripts/kit/W08/boardwalk.py`, goals
    `art/blender/renders/kit/W08/boardwalk_goals.md`, manifest `art/roblox/kit/W08/manifest.json`): `Boardwalk`,
    `BoardwalkStraight`, `BoardwalkCornerL`, `BoardwalkRampEnd`, `BoardwalkStairs`, `BoardwalkRailPost`,
    `BoardwalkRail`, `BoardwalkFloorPlank`, `BoardwalkSupportPost`, `BoardwalkCrossbeam`; keys `w08_*`. It was built to
    an older drawing as a **low walkway** (deck top 1.9, 15 × 6.5 × 4.4, double rail on both sides, 0.4 planks, posts
    0.65). `MODEL_PROGRESS.md` row 74 flags it "plank-fence railing; ramp not stairs; corner not an L"; its goals record
    timber that "reads slightly redder than the reference". Reuse the lessons, not its names or sizes (§8).
  - **M048 Dock** (verified 8/10, committed; `m048.py` helpers importable): the kit's timber family, deck 5.6, posts
    1.3, boards 1.82 × 0.85, beams 3.45 → 4.75, brass bolt heads (`_bolt`), twisted rope tubes (`_tube`). Its ruling's
    polish list is §9 here (coils read as faceted collars; f34 rope gold +2.7; legs too dark in side light).
  - **M050 Timber Bridge** (being modelled, `m050.py` untracked): the nearest sibling. W 8 post centres, posts 1.5,
    deck 32 × 9.5 at **5.6**, crisp boards notched round the posts, stringers inside the post lines, blocks with pegs
    at z 3.50 → 4.75, knee and X braces. This sheet's timber sections and colours agree with it (§1.1, §5).
  - **M051 Rope Crossing** (being modelled, `m051.py` not written): stone tops and deck ends at 5.6; this spec's model
    for structure.
  - **Kit levels:** ground 0; water top 1.0 (M034 / M041; bed 0 → 0.2); sand 1.6; lawns 5.6 (M043 lower) and 10.4
    (M040 / M043 upper); decks 5.6 (M048, M050, M051).
  - WorldModeling §13.1–13.2 (timber vocabulary; "Bridges, docks, boardwalks, and fences"): squared timbers with
    restrained bevels, posts stronger than rails, "Build load-bearing components first: piles/posts, longitudinal
    beams, crossbeams, deck planks, then rails and rope. Inspect from underneath", "Keep route width consistent within
    one kit", and the kit's pieces "short bay, straight span, corner/landing, ramp end, and damaged version".

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Paper `#FEFCF7`
(tolerance 10). Cell rules (`lines.py` and paper scans): rows 150, 452 (section 1), 462, 665 (orthos), 675, 1161
(exploded), 1170, 1487 (close-ups); columns 8, 513, 1014; ortho dividers 300 / 490 / 748; exploded | parts list at
718; close-up columns 21–336, 354–669, 687–1001 (images y 1207–1407). Titles and cell labels are painted out
(`TITLES` in `m.py`). Masks are `m.cls()` (HSV, h in degrees, in this order):
- **T** outlines / text: v < 0.16; or s < 0.25 and v < 0.35; or h 200–250, s > 0.25, v < 0.45 (navy ink).
- **Y** brass and gold highlights: h 36–62, s ≥ 0.18, v ≥ 0.60; or h 33–36, s 0.18–0.62, v ≥ 0.75 (the bolt heads,
  the cap dots and a few pale plank-top highlights; **the rope does not class Y on this sheet**, §5.2).
- **W** lit wood: h < 40 (or > 345), s ≥ 0.35, v ≥ 0.62 (plank and tread tops, caps, lit faces).
- **K** dark wood: the rest of the wood hues, s ≥ 0.25, v ≥ 0.16 (post faces, beams, legs, braces, undersides).
- **B** ground shadow: the remaining low-saturation pixels (s < 0.25): the pale lilac-grey shadow. Excluded.
- **O** other.
- W / K is a **lit / dark** split, not a material split (one orange timber family, §5).
- Cells: f34 (9,151,512,451); r34 (514,151,1013,451); front (9,463,300,664); side (302,463,490,664); rear
  (492,463,748,664); top (750,463,1013,664); exploded (9,676,717,1160); key parts (719,684,1013,1160); close-ups A
  (21,1207,336,1407), B (354,1207,669,1407), C (687,1207,1001,1407). Header swatches (`sw.py`): (698,38,750,79),
  (761,…,813), (824,…,876), (887,…,939), (950,38,1002,79).

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m052_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Pillow, numpy) and `< /dev/null`.
- **Helpers:** `m.py` (masks, boxes `V` / `X` / `TITLES`, `label`, `pxs`, `reg`), `zoom.py` (crop with an optional
  sheet grid), `lines.py` (cell rules), `sw.py` (swatch boxes and hexes).
- **Measurements:** `measure.py` → `bb.json` and `cls_*.png` (bbox, W : H, shares, top profile, width per height,
  fifths, class medians); `runs.py <cell> row|col <coords>` (class runs: levels, post edges, plank gaps); `caps.py
  <cell>` (cap-top peaks in the three-quarters); `ortho_fit.py` (orthographic camera fit to the three-quarters' cap
  grid, §1.1); `ycount.py` (Y blobs per cell: bolts and cap dots); `proj052.py` (block model of candidate layouts) and
  `proj_adopt.py` (block model of the adopted layout at any camera, §2.8).
- **Colour:** `samp.py` (every region in §5.2), `rope.py` (rope strands).
- **Zooms:** `z_f34.png`, `z_f34_l.png`, `z_f34_r.png`, `z_f34_stairs.png`, `z_f34_rope.png`, `z_rope_f34.png`,
  `z_r34.png`, `z_r34_r.png`, `z_ortho_l.png` (front + side), `z_ortho_r.png` (rear + top), `z_front_l.png`,
  `z_side.png`, `z_top.png`, `z_expl.png`, `z_keys.png`, `z_cu.png`, `z_cuA.png`, `z_cuB.png`, `z_cuC.png`.
- **On our renders:** `measure_render.py <render.png> [paper_hex]` prints bbox, W : H, W / K / Y shares, profile,
  width per height, fifths and class medians with these masks. Self-test on the sheet's own cells reproduces §1.2
  exactly: `selftest_f34.png` (crop (9,176,512,420)) W : H 1.958, W 52.7 / K 45.2 / Y 2.1; `selftest_front.png` (crop
  (9,515,300,612)) W : H 3.288, W 40.9 / K 57.4 / Y 1.7.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a modular timber structure. Hero budget 4000 tris, each part under 1000. The plan in
  §4.3 lands at about 1750 (no rope-heavy parts; plenty of margin).
- **Overall read (check this first).** A **long, level, raised plank walkway on square timber posts, with a single
  chunky handrail along its back long side and across one end, open along its front long side, and a short flight of
  chunky plank stairs coming down from the other end**:
  - a **deck of chunky orange planks laid across the width**, their ends forming a row of blocks along both long
    edges, about five planks per bay;
  - **six full-height square rail posts**: four along the back (+Y) side and the two front corners, each standing
    about 3.4 above the deck with a softened cap and a pale peg dot on top;
  - **one rail plank per bay along the back side** (three) and **one across the railed (+X) end**, at thigh height,
    butted into the post faces; small rail-end stubs on the outer faces of the end posts;
  - two **short support posts** under the front edge at the middle (they stop under the planks);
  - under the deck: a **beam** along each side, **crossbeams** at every post row, a **block with a big pale-gold hex
    bolt** on the outer face of every post at beam height (and on the end faces of the corner posts), **knee braces**
    from the legs to the beams, an **X brace** under the deck;
  - **stairs** at the open (−X) end: chunky treads, each of two boards, on sloped stringers, dropping to the ground;
  - **a rope tie** on the front-right corner post at rail height, its tail lying on the deck.
  - Hero shares (f34): W 52.7 % (plank tops dominate), K 45.2 %, Y 2.1 % (bolts, cap dots, pale highlights).
- **Focal silhouettes, in order:**
  1. The long deck slab with its row of plank-end blocks, rising from the stairs at the lower left of the f34 to the
     railed end at the upper right.
  2. The back rail: four tall posts with the rail plank between them, and the end rail closing the right end.
  3. The stairs stepping down at the left; the posts and legs under the deck with their bolt blocks; the knee braces.
- **Target: post centres W 8.0 across × 3 bays of 9.412 along (28.24 end post to end post); deck 32.0 × 9.5, top
  5.6; post tops 9.0; rail 6.85 → 7.75; stairs 4 treads from the −X deck end down to the ground; overall about 37.84
  L × 11.06 W × 9.0 H** (stairs foot x −21.84 to deck end +16.0; bolt heads ±5.53). Tolerances: deck top 5.60 ± 0.02
  (a seam level, §2.1); post spacing exact; H ± 0.3; W ± 0.4; L ± 0.4. Decision §8.1.
  - **How it was derived.**
    - **Height and levels** (front cell, the cleanest scale: post top y 526 → ground 605, H = 79 px; side cell 521 →
      605, 84 px):

      | Item | Front (frac. of H) | Side | Adopted (z) |
      | --- | --- | --- | --- |
      | Post top | 1.000 | 1.000 | **9.00** |
      | Rail top / bottom | .861 / .759 (537 / 545) | .762 / .679 | **7.75 / 6.85** |
      | Deck top | **.620** (556) | .583 | **5.60** (.622) |
      | Plank bottom | .532 (563) | .500 | **4.75** |
      | Beam bottom | .380 (575) | .357 | **3.45** |
      | Bolt centre | .468 (568) | .452 | **4.12** |
      | Knee-brace foot on the leg | .19 (590) | .18 | **1.70** |

      With the deck at the kit's **5.6**, H = 9.0 and the sheet's sections land on the kit's timber: planks 7 px =
      **0.80** (M048 / M050 0.85), beam 12 px = **1.37** (1.30), posts 13–14 px = **1.5–1.6** (M050 1.5), rail 8 px =
      **0.91**, bolt Ø 4–5 px = **0.5**. All six rail posts are full height: in the f34 the near-left post runs y 275
      → 412 and the near-right 195 → 317, both with their bolt at 0.48–0.49 of the post (front cell 0.47).
    - **Along : across : height disagree between cells** (the generator draws each cell at its own scale, as on M050):

      | Source | Bay / H | W / bay | Notes |
      | --- | --- | --- | --- |
      | Front cell | 0.90 (bays 57.5 / 71.5 / 84 px, mean 71) | — | posts x 56 / 113.5 / 185 / 269 |
      | Rear cell | 0.84 (72 / 68.5 / 59.5) | — | posts x 521.5 / 593.5 / 662 / 721.5 |
      | Top cell | — | **1.01** (68.5 along, 69.5 across) | caps x 778.5 / 847 / 916.5 / 984; y 523.5 / ≈ 593 |
      | Side cell | — | 1.37 (with the front cell's bay/H) | post centres 344 / 447.5 (103.5 px): **W 1.23 H** |
      | f34 (orthographic fit to the cap grid, `ortho_fit.py`) | 1.10–1.23 | **0.61** | az −46.3, e 11.5; far caps (80,246) (182,223) (296,202) (393,181), near-right (461,194) |
      | r34 (same fit) | — | 0.71 | az −42.8, e 10.8 |

      Adopted **W 8.0** (the kit's route width: M048's and M050's post lines, so the pieces join post line for post
      line; WorldModeling §13.2 "Keep route width consistent") and **bay 9.412 = 5 planks of 1.882** (W / bay 0.85,
      bay / H 1.05: between the three-quarters and the orthos, as M050 did), which makes the deck **exactly one 32-stud
      tile** with the end planks one plank past the end post rows (top cell: deck 233 px over post span 205.5 = 1.134;
      ours 32 / 28.24 = 1.133).
    - **Planks:** the top cell counts **17** across the length (seams every 13.7 px, x 799 … 977: 5 per bay); the f34
      about the same; the exploded draws groups of 5. Adopted 17 × 1.78 wide (gaps 0.10), 0.85 thick.
    - **Stairs** (§3.4): the f34 draws **2 treads** under the deck end (screen risers 35 / 28 / 28 px, about 2.0 studs
      each at the near post's 15.2 px per stud), each tread two thick boards (close-up A agrees); the front cell 3, the
      top cell 3 (54 × 33 px: 7.4 wide × 4.5 deep), the exploded 3, the parts list **4**. Adopted 4 treads (risers
      1.12) so the stairs are walkable (decision §8.4).
  - **Why this size.**
    - **Against the character (5.5):** the deck stands **5.6 above the ground** (just over a character); the posts rise
      **3.4 above the deck** (0.62 C, hip height); the rail top is **2.15 above the deck** (thigh height: a low guard
      rail, chunky, not a fence); the walkway is **8.5 clear** from the open front edge to the rail (6.5 between the
      corner posts' inner faces at the ends); stair risers **1.12**, treads 1.46 deep, 8.0 wide.
    - **Against the kit:** the deck top **5.6 equals M043's lower lawn and the dock, bridge and crossing decks**; its
      stairs come down to the ground (z 0) — **the "ramp end / stairs" piece that M048 and M050 both flagged as
      missing**, here as part of the walkway. Over water the deck is 4.6 above the water top 1.0 (legs on the plate,
      like the dock's). On sand (1.6) the bottom tread (top 1.12) sinks under the sand and the next (2.24) is a 0.64
      step.
- **Build frame (decision §8.2):** long axis **X** (the sheet's "FRONT VIEW" is a long side, and the kit's `front`
  camera then shows it), the **rail side +Y**, the **railed end +X**, the **stairs at −X**, the **open long side −Y**
  (it faces the f34 camera, as on the sheet). Ground z 0; the deck centred on x 0 / y 0. **Not symmetric.** Stage 2
  puts the origin at the bbox bottom centre: the bbox runs x −21.84 … +16.0, so the deck centre ends at **x +2.92** in
  the object frame; record that offset in the builder docstring and the export notes (decision §8.2).

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | W | K | Y | O | W / K / Y medians |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (9,151,512,451) | 25–486 × 181–416 (462 × 236) | **1.958** | 52.7 % | 45.2 | 2.1 | 0.0 | `#D77F32` / `#7B3A14` / `#FAC77C` |
| Rear three-quarter (514,151,1013,451) | 546–997 × 180–407 (452 × 228) | 1.982 | 52.8 | 45.5 | 1.8 | 0.0 | `#C96823` / `#733511` / `#F9C77F` |
| Front (9,463,300,664) | 22–284 × 526–605 (263 × 80) | **3.288** | 40.9 | 57.4 | 1.7 | 0.0 | `#B05C20` / `#7C3D17` / `#F2C38B` |
| Side (302,463,490,664) | 329–463 × 521–605 (135 × 85) | **1.588** | 31.2 | 67.5 | 1.2 | 0.0 | `#AF5C20` / `#7A3B19` / `#F1C181` |
| Rear (492,463,748,664) | 506–734 × 526–605 (229 × 80) | 2.862 | 37.7 | 60.7 | 1.5 | 0.0 | `#AE5B1F` / `#713918` / `#F1C28A` |
| Top (750,463,1013,664) | 764–998 × 514–631 (235 × 118) | 1.992 (L : W incl. the stairs below) | 70.3 | 28.9 | 0.8 | 0.0 | `#D77D35` / `#783D18` / `#F6CB8F` |

- Shares are of W + K + Y; B (the lilac-grey ground shadow) and T are left out. **Verifier tolerance:** W / K ±6
  (they split on value, so the studio light moves them); Y ±1.5; W : H ±0.08 on the f34; positions ±0.05.
- **Y is bolts, cap dots and highlights only** (`ycount.py`): the front cell has 4 bolt blobs at y 566–567 plus cap
  and rail highlights; the top cell 8 cap dots (x 776 / 845 / 915 / 985 on both rows); the f34's 29 small blobs are
  the bolts plus pale plank-top highlights.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .20 | .32 | .71 | .65 | .67 | .69 | .71 | .81 | .75 | .78 | .80 | .82 | .91 | .86 | .89 | .91 | 1.0 | .92 | .89 | .94 | .72 |
| r34 | .50 | .77 | .70 | .72 | .74 | .83 | .78 | .80 | .82 | .84 | .93 | .88 | .89 | .91 | .99 | .93 | .89 | .93 | .72 | .62 | .54 |
| Front | .12 | .29 | .84 | .99 | .84 | .84 | .84 | .99 | .84 | .84 | .84 | .84 | .99 | .84 | .84 | .84 | .84 | .84 | .84 | .99 | .54 |
| Side | .58 | .84 | .99 | .99 | .89 | .79 | .79 | .79 | .79 | .79 | .79 | .79 | .79 | .79 | .79 | .79 | .89 | .99 | .99 | .85 | .58 |
| Rear | .54 | .99 | .84 | .84 | .84 | .84 | .84 | .84 | .99 | .84 | .84 | .84 | .84 | .92 | .99 | .84 | .84 | .84 | .84 | .99 | .55 |

- **f34:** the stairs at f 0–.05 (.20 / .32), the far-left post at .10 (.71), the rail rising behind the deck, posts
  at .35 (.81), .60 (.91), .80 (1.0) and the near-right corner post at .95 (.94), the deck end at 1.0 (.72).
- **Front / rear:** four post peaks (.99), the rail line (.84) between them, the stairs at the left end of the front
  (.12 / .29) and the deck end at the right (.54).
- **Side:** two posts (.99) with their rail stubs (.89), the end rail (.79) between them, the deck ends (.58).

**Width per height** (fraction of W at h .05 → .95):

```
f34    .23 .50 .45 .66 .92 .89 .91 .67 .42 .05
r34    .08 .27 .45 .67 .97 .96 .92 .87 .44 .06
front  .97 .96 .92 .87 .92 .91 .86 .87 .87 .86
side   .87 .87 .87 .87 .99 1.0 .87 .91 .90 .87
rear   .95 .93 .93 .93 1.0 .99 .93 .93 .93 .93
```

**Fifths** (bottom → top, % of each class): f34 W 7.1 / 15.4 / 35.5 / 33.3 / 8.7; K 15.0 / 25.5 / 29.7 / 20.8 / 9.0;
Y 6.9 / 25.8 / 33.9 / 23.3 / 10.1. Front W 14.0 / 11.5 / 29.3 / 23.3 / 21.9; K 16.7 / 21.6 / 37.7 / 15.7 / 8.4.

**Level and size measurements** (sheet px; `runs.py`, `caps.py`):

| Item | Front cell (−Y long side) | Side cell (+X end) | Rear cell | Top cell | f34 / r34 |
| --- | --- | --- | --- | --- | --- |
| Post centres | x 56 / 113.5 / 185 / 269 | x 344 / 447.5 (103.5) | x 521.5 / 593.5 / 662 / 721.5 | x 778.5 / 847 / 916.5 / 984; y 523.5 / ≈ 593 | f34 cap tops (80,246) (182,223) (296,202) (393,181); near-right (461,194); near-left cap ≈ (150,275) |
| Post width | 13–14 (50–63, 107–120, 179–191, 262–276) | 14–15 | 13–14 | caps 15–17 | — |
| Levels (y) | post top 526; rail 537–545; deck 556; plank bottom 563; beam band 563–575; bolts 568; brace foot 590; ground 605 | post top 521; rail 541–548; deck 556–563; beam 563–575; bolts 567; braces 575 → 590; ground 605 | as front | — | — |
| Rail | one rail through all 4 posts (the far rail, seen past the open near side) | the end rail between the two posts; rail-end stubs on both posts' outer faces (329–337, 455–463) | one rail through all 4 | a rail strip along the top edge (y 515–524) | far side only (4 posts) + across the right end; **no rail along the near side** |
| Deck | plank band 556–563, ends x ≈ 41 / 284 (15 px past the end posts) | 329–463 (1.30 × the post spacing) | — | x 765–998 (233; 13.75 px past each end post = 0.20 bay); y 521–598 | — |
| Planks | end gaps every 12–15 px (≈ 5 per bay) | end plank side face drawn as blocks | — | **17**, seams x 799, 812, 825, 839, 853, 867, 881, 894, 909, 923, 937, 950, 963, 977 | ≈ 17; some look broken at mid-width (§3.6) |
| Blocks / bolts | blocks 563–575, post-wide, bolt centres y 566–567 at all 4 posts | blocks on both posts' end faces, bolts at 567 | 4 | caps with pale dots (both rows) | a block + bolt on every near post (incl. the two support posts) |
| Braces | knee brace from **post 2 toward +X** (foot 120,590 → beam 138,573) and from **post 4 toward −X**; none at posts 1 / 3 | **V**: both legs up to the crossbeam (feet ≈ 590, tops 575 at x ≈ 368 / 420) | mirror of the front: post 1 (= +X end) inward, post 3 (= x −4.7) toward +X | — | under-deck braces in shade |
| Stairs | 3 treads x 22–85, tops ≈ 575 / 582 / 593, round post 1 | none drawn | a dark block x 685–740 between posts 3–4 | off the **bottom long side at the right end**: x 935–990, y 599–632, 3 treads | f34: **at the near-left (−X) end**, 2 treads; r34: at the far right beyond the railed end |

### 1.3 Silhouette and composition per view

**Front three-quarter (`z_f34.png`, `z_f34_l.png`, `z_f34_r.png`, `z_f34_stairs.png`): governs.** Camera at −X, −Y
(**kit az ≈ −46, e ≈ 12–14**), clear perspective. The −X end at the lower left, the near (−Y) long side running back to
the upper right.
- **Deck:** chunky planks laid across the width, upper left to lower right; their ends form a row of blocks along the
  near edge, over the near beam. Plank tops lighter at their edges, values varying plank to plank; some planks look
  broken at mid-width (§3.6).
- **Posts:** the far row's four posts with the rail plank between them, rising behind the deck; the near-left corner
  post at the stairs (full height, its cap at y 275) and the near-right corner post, joined to the far-right post by
  the **end rail**. The near side's two middle posts are **support posts** that stop under the plank ends, each with
  a bolt block at its top. A small rail-end block on the far-left post's −X face and on the near-right post's −Y face.
- **Stairs:** two chunky treads of two boards each, stepping down toward the lower left from under the deck end, with
  white slits between tread and deck (open risers), on stringers.
- **Rope:** a twisted orange-tan rope looped round a block on the near-right post at rail height, its tail running
  down onto the deck toward −X (`z_f34_rope.png`, `z_rope_f34.png`).
- **Under the deck:** the near beam with blocks and hex bolts at each near post, legs, braces in shade; a pale
  lilac-grey ground shadow (B, excluded).

**Rear three-quarter (`z_r34.png`, `z_r34_r.png`).** Not a true rear view: it repeats the f34's arrangement (rail on
the far side, near side open, the railed end at the right, the same rope on the near-right post) from nearly the same
camera, but puts **the stairs at the far right, beyond the railed end** (§3.3, §3.9). A V knee brace under the
near-left post.

**Front (`z_ortho_l.png`, `z_front_l.png`).** The −Y long side, level: four post peaks (the far row and the near
corners overlap), the rail through all four (the far rail seen past the open near side), the plank band, the beam band
with four blocks and bolts, knee braces at posts 2 and 4, the stairs as a stepped pile round post 1 at the left.

**Side (`z_side.png`).** The +X end, level: two posts with the end rail between them and a rail stub on each post's
outer face, the deck end as a row of blocks, the beam band with a block and bolt on each post's end face, a V of knee
braces from both legs to the crossbeam. No stairs drawn.

**Rear (`z_ortho_r.png`).** The +Y side: four posts, the rail, the beam band with bolts, knee braces mirroring the
front's, the stairs as a dark block at the right end.

**Top (`z_top.png`).** Plan, long axis horizontal: 17 planks across, 8 post caps with pale dots (four per long edge),
a rail strip along the top edge, the stairs as 3 treads below the bottom edge at the right end.

### 1.4 Parts (exploded (9,676,717,1160), `z_expl.png`; key parts (719,684,1013,1160), `z_keys.png`)

The hero governs every size; the parts give shapes and boundaries.

| Part | Box (sheet px) | Notes |
| --- | --- | --- |
| Rail Post / Support Post | key (743,728,777,840); exploded rail post (168,735,208,860), support post (270,1015,320,1130) | A square post (key W : H ≈ 1 : 3.3), a **hex bolt** on one face near the top, a dark peg dot on top. The exploded rail post is a cap block over a shaft; the support post carries a block with a bolt at its top |
| Rail Plank | key (830,740,987,818); exploded 3 loose (220,770,330,825), (420,705,520,760), (380,735,420,760) | A long square-ish board, section about 1 : 0.7 |
| Floor Plank | key (737,828,905,925); exploded groups of 5 (230,820,500,920), (420,760,600,855) | A long chunky board (L : W ≈ 4.5 on screen), faint line along the top; **one plank of the right group notched at its end** (≈ (500,845)) |
| Stairs | key (815,906,987,1053); exploded (30,945,200,1080) | Key: **4 treads** stepping down, a sloped stringer under them and a vertical leg under the top tread. Exploded: 3 treads (each with board lines) on a stringer |
| Crossbeam | key (740,1040,874,1128); exploded long beam (300,890,590,1000) | Key: a square beam about 0.8 of a floor plank's length. Exploded: the **long side beam** on two support posts with bolt blocks and a knee brace |
| Brace | key (887,1053,974,1143) | An **L**: a short vertical leg piece with a diagonal board rising from its foot |

- **A. Stair junction** (`z_cuA.png`): the corner post with a big block and **hex bolt** at beam height and a softened
  cap above the deck; deck planks on the beam; **two treads**, each of **two thick boards**, stepping down beside the
  post, open between treads.
- **B. Underside** (`z_cuB.png`): plank bottoms (`#69341A`), crossbeams, a post with a block and bolt, and an **X
  brace** of two crossing boards with a peg at the crossing.
- **C. Post / rail junction** (`z_cuC.png`): a square post; one rail plank's end butts flat against one face, another
  rail plank leaves from the adjacent face higher up ("Joining Surface (flat face to flat face)").

## 2. Layout (starting values; tune on the renders)

Studs, build frame (long axis X, rail side +Y, ground z 0, the deck centred on x 0 / y 0). Builder constants (decision
§8.3): `W = 8.0` (post centres across), `NP = 17` planks, `PITCH = 32 / 17 = 1.8824`, `BAY = 5 * PITCH = 9.4118`,
`POST = 1.5`, `DECK_TOP = 5.6`, `PLANK_T = 0.85`, `BEAM_D = 1.30`, `POST_TOP = 9.0`, `RAIL_Z = (6.85, 7.75)`,
`NT = 4` treads, `TREAD_D = 1.46`, `STAIR_W = 8.0`, `SINK = 0.02`. Flags for later variants (built only as drawn now):
`STAIRS = True`, `END_RAIL = True`, `RAIL_SIDES = ("+Y",)`.

### 2.1 The seam contract (binding; record it in the builder docstring and the export notes)

| Item | Value | Notes |
| --- | --- | --- |
| Ground / leg feet / stair foot | **z 0**, flat | a water tile's plate, ground or a beach (sunk under the sand) |
| Deck top (walk surface) | **z 5.6**, flat, planks ± 0.02 | flush with M043's lower lawn and the M048 / M050 / M051 decks |
| Open long side (−Y) | **y −4.75**, the plank ends' faces; nothing above the deck between the corner posts (x −13.37 … +13.37) except the rope tail lying on the planks at x 10.3 … 13.2 | a walk-on seam: a terrace front at 5.6, or the open end of a dock or bridge T-joined to it |
| Railed long side (+Y) | planks to y +4.75; rail on the post line y +4.0 | closed |
| Railed end (+X) | the end plank's outer face **x +16.0**; end rail on x +14.118 | closed (rail 1.25–2.15 above the deck) |
| Stairs end (−X) | the end plank's outer face **x −16.0**; stairs from x −16.0 to **−21.84**, y ±4.0 | the way up from z 0 |
| Sides | blocks to y ±5.25, bolt heads to ±5.53, rail stubs to ±5.10 | nothing past ±5.6 |
| Post centres | y ±4.0; x ±4.706, ±14.118 | the W 8 route width of M048 / M050 |

- **Walkability.**
  - **Deck:** level (0°), 17 planks, gaps 0.10, no step above 0.02. Clear width 8.5 from the open edge to the rail's
    inner face (y +3.70), 6.5 between the corner posts' inner faces at each end.
  - **Stairs:** 4 treads, **risers 1.12** (the top tread 1.12 below the deck), treads 1.46 deep (two 0.70 boards with
    a 0.06 gap), 8.0 wide; a 37° flight. Whether a default character walks up 1.12 risers without jumping must be
    checked in Studio (Requires Manual Validation; §8.4 has the 2- and 3-tread alternatives). The hero's precise
    collision follows the treads; a Studio-side invisible ramp wedge would make it smooth if wanted.
  - **Edges:** the open −Y side is a 5.6 drop, as drawn (no rail). The +X end rail blocks the end (a character can't
    pass under a rail 1.25 above the deck).
- **With M043 (lower lawn 5.6):** put the open −Y side against the lawn's terrace front: a walkway along the terrace,
  stairs down to the ground at −X.
- **With M050's bridge / M048's dock:** T-join an open bridge end (x ±16, 9.5 wide) or the dock's open end (10.2 wide)
  against the boardwalk's open −Y side anywhere in |x| ≤ 8.6 (clear of the corner posts): all decks at 5.6, flush.
  End-to-end joins need a variant with `END_RAIL = False` / `STAIRS = False` (the drawn hero is a terminal piece).
- **With water tiles (M041 / M034):** legs and stairs on the plate (z 0); the bottom tread's top (1.12) is 0.12 above
  the water top 1.0; nothing touches the water mesh. M034's bank rocks fill most bridge-sized footprints (M050 §2.1):
  not placed there as built.
- **With a beach (sand 1.6):** legs and stair foot stay at z 0 under the sand; the lowest tread disappears and the
  first step up is 0.64 (tread 2 at 2.24).

### 2.2 Posts

| Piece | Position | Size | Notes |
| --- | --- | --- | --- |
| Rail posts R1–R6 | far row (±4.706, +4.0), (±14.118, +4.0); near corners (±14.118, −4.0) | 1.5 × 1.5, z 0 → 9.0 | one closed prism per post; **cap chamfer 0.10** on the four top edges (the only bevel); a **pale peg dot** on top (0.30 square inset, 0.03 deep, `brass`) |
| Support posts S1–S2 | near middle (±4.706, −4.0) | 1.5 × 1.5, z 0 → 4.77 | top sunk 0.02 into the plank undersides; inner face sunk 0.02 into the near beam |
| Blocks (12) | each post's outer long face (y ±4.75 → ±5.25, x = post ± 0.75), and the four corner posts' end faces (x ±14.868 → ±15.368, y ±3.25 … ±4.75) | 0.5 proud, z 3.50 → 4.75 | sunk 0.02 into the post face; the end-face blocks touch the side beam's outer face |
| Bolt heads (12 + 2) | centre of each block's outer face at z 4.12; one at each X-brace crossing | **hex** (6 sides), Ø 0.55, 0.22 proud + a 0.06 dome | sunk 0.03 into the block (or brace board B); close-up A's hex head |

### 2.3 Framing: beams, crossbeams, headers

| Piece | Position | Size | Notes |
| --- | --- | --- | --- |
| Side beams B±Y | y ±2.35 … ±3.25 (outer face sunk 0.02 into the posts' inner faces), x −15.98 … +15.98 | 0.9 × 1.32, z 3.45 → 4.77 | top sunk 0.02 into the planks; the front cell's beam runs to the deck ends |
| Crossbeams C1–C4 | x = each post row ± 0.45 (−14.118, −4.706, +4.706, +14.118), y −2.35 … +2.35 | 0.9 × 1.32, z 3.45 → 4.77 | end faces sunk 0.02 into the side beams |
| End headers H±X | x ±15.10 … ±16.0, y −2.35 … +2.35 | 0.9 × 1.32, z 3.45 → 4.77 | carry the end plank's outer edge; the −X header takes the top tread and the stair stringers butt the side-beam ends beside it (close-up A "attach to … crossbeam") |

### 2.4 Deck

- **17 planks across the width**, pitch 1.8824 over x −16 … +16, **1.78 wide** (0.10 gaps; the two end planks 1.83 so
  their outer faces sit exactly at ±16.0), **0.85 thick** (z 4.75 → 5.6), y −4.75 … +4.75 (9.5 long). Seams fall on
  the post rows (x ±4.706, ±14.118), as M050.
- **Notches** (exploded: one notched plank): planks 0, 1, 15, 16 (end rows, rail posts at both ends) are notched at
  **both** ends; planks 5, 6, 10, 11 (middle rows) only at the **+Y** end (the −Y middle posts are support posts under
  the deck). Each notch is an open L from the post's inner face (|y| 3.23) to the deck edge, 0.72 deep in x (0.02 clear
  of the post face). One closed prism of a 6- or 8-vertex plan polygon; ear-clip the non-convex caps.
- **Each plank** a crisp box (decision §8.5: no chamfer, as M050; the alternative is a 0.05 top-edge chamfer), height
  jitter ±0.02 and yaw ±0.3° (gaps stay 0.06–0.14). No grain, no groove (§3.6).
- **Support:** every plank rests on both side beams (sunk 0.02) and on the crossbeam or header under it; the near
  middle planks also on the support posts.

### 2.5 Rails

| Piece | Position | Size | Notes |
| --- | --- | --- | --- |
| Back rail (3 planks) | y +3.70 … +4.30 (on the post line), from post face to post face: x −13.368 … −5.456, −3.956 … +3.956, +5.456 … +13.368 | 0.6 thick × 0.9 tall, **z 6.85 → 7.75** | end faces sunk 0.02 into the post faces (close-up C: flat face to flat face) |
| End rail (1 plank) | x +13.818 … +14.418, y −3.25 … +3.25 (from the near-right post's +Y face to the far-right post's −Y face) | 0.6 × 0.9, z 6.85 → 7.75 | the same butt joints |
| Rail-end stubs (4) | far-left post −X face (x −14.868 → −15.218, y 3.70 … 4.30); far-right post +X face (14.868 → 15.218); far-right post +Y face (y 4.75 → 5.10, x 13.818 … 14.418); near-right post −Y face (y −4.75 → −5.10) | 0.35 proud × 0.6 × 0.9, z 6.85 → 7.75 | the rail runs' overlap past their end posts (f34 far-left and near-right blocks; the side cell's stubs); sunk 0.02 |

### 2.6 Braces (the decision §8.6 set)

| Brace | From | To | Section | Sheet evidence |
| --- | --- | --- | --- | --- |
| End V braces (4) | each end leg's inner face (y ±3.25) at z 1.70, centred in x on the post row (x ±14.118, 0.45 thick) | the end crossbeam underside (z 3.45) at y ±1.15 | 0.6 × 0.45 | side cell (≈ 43°) |
| Long-side knee braces, end legs (4) | each end leg's inner face (x ±13.368) at z 1.70 | the side beam underside (z 3.45) at x ±11.27 | 0.6 × 0.45, centred in y on ±3.25 (straddling the leg / beam line: ≥ 0.2 overlap each) | front cell post 4, rear cell post 1, key "Brace" |
| Long-side knee braces, middle legs (4) | each middle leg's centre-side face (x ±3.956) at z 1.70 | the side beam underside at x ±1.856 | as above | front cell post 2, rear cell post 3 (both drawn on the −X middle legs; mirrored here, §3.5) |
| X braces, middle rows (2 × 2 boards) | each middle leg's inner face (y ±3.25) at z 0.45 | the opposite leg's inner face at z 3.30 | 0.6 × 0.35; board A x = row − 0.35 … row, board B row … row + 0.35 (stacked, touching at the crossing, inside the legs' x range) | close-up B; a bolt on board B at the crossing (y 0) |

- Ends cut to the faces they meet (vertical against a leg, horizontal against a beam) and sunk 0.02 (M048's
  `_brace_quad`).

### 2.7 Stairs (decision §8.4)

- **Treads T1–T4:** tops z 4.48, 3.36, 2.24, 1.12 (risers 1.12 = 5.6 / 5); each tread two boards **0.70 (x) × 8.0
  (y, ±4.0) × 0.55 (z)** with a 0.06 gap → 1.46 deep. T1 spans x −17.44 … −15.98 (its back face sunk 0.02 into the −X
  header), T_i steps out by 1.46 each; T4's front face at **x −21.84**.
- **Stringers (2):** cut (sawtooth) stringers, 0.5 wide at y ±2.60 … ±3.10, in the XZ plane: a seat under each tread
  (tread bottoms sunk 0.02 into the seats), the risers between, the bottom edge from the foot (x −21.84, z 0) up to the
  back; the back face vertical at x −15.98 butting the side beam's end (sunk 0.02). One closed prism of a ≈ 12-vertex
  non-convex profile: **ear-clip, check every triangle's winding** (the parts list draws a stringer and a vertical leg
  under the top tread: the stringer's back end is that leg).
- **Clearance:** the treads clear the corner posts (the posts are inside the deck end, |x| ≤ 14.87); the stairs touch
  only the header, the side-beam ends and the ground.
- **Stairs part:** the same treads and stringers, standing alone (origin at its bottom centre).

### 2.8 Rope tie

- **Wrap:** one twisted ring round the near-right post (14.118, −4.0) at **z 6.45** (just under the end rail), a
  rounded square, centreline 0.95 from the post axis, **Ø 0.30, 5 sides × 8 segments, `twist=True`** (M048 finding 1),
  inner surface sunk 0.02 into the shaft.
- **Tail:** from the wrap's −X side (13.20, −3.9, 6.40) curving down to the deck at (11.6, −3.7, 5.70) and lying on the
  planks to (10.3, −3.5, 5.71), Ø 0.30, 5 sides, ≈ 8 rings, sunk 0.03 into the plank tops where it lies (never more
  than 0.05; it crosses two plank gaps), ending in a knob (Ø 0.42, `_knob`, 6 × 3).
- It is the only rope on the sheet (both three-quarters; not in the parts list): dressing, kept low on the deck edge.

### 2.9 Expected extents and screen checks

- **Extents (build frame):** X −21.84 … +16.0 (stairs foot to the +X deck end); Y −5.53 … +5.53 (bolt heads; blocks
  ±5.25, planks ±4.75); Z 0 … 9.0. Bbox ≈ 37.84 × 11.06 × 9.0; centre x −2.92 (§1.1 build frame).
- **Self-consistency (`proj_adopt.py`, orthographic block model):** f34 (−46, 14) W : H **1.979** (sheet 1.958);
  (−46, 13) 2.041, (−46, 15) 1.920, (−43, 15) 2.016, (−49, 13) 1.942. Rear three-quarter (134, 15) 2.044 (sheet
  r34 1.982). Front (0, 0) **4.20** against the cell's 3.288, side (90, 0) **1.17** against 1.588: the ortho cells are
  drawn at their own horizontal scales (§3.1), recorded misses.
- **Checks on the renders** (floor hidden, `measure_render.py`, the studio's paper colour as the second argument):
  - **f34_sheet (−46, 14)** (probe az −40 / −46 / −52 × e 12 / 14 / 17; keep the best):
    - W : H 1.88–2.04 (1.958);
    - shares W 52.7 ± 6, K 45.2 ± 6, Y 2.1 ± 1.5;
    - read: the stairs at the lower left stepping down from the deck end, the long deck with its plank-end row rising
      to the upper right, the back rail with four posts behind it, the end rail closing the right end, the near side
      open with bolt blocks on its posts, the rope on the near-right post.
  - **r34_sheet (134, 15)**: the rail side and the railed end near, the stairs at the far right; W : H 1.95–2.10; not
    binding on composition (§3.9).
  - **front_sheet (0, 0)** (−Y side): four post peaks (the near corners in front of the far ones), the back rail
    seen past the open side, the plank band, four blocks with bolts, the stairs stepping down at the left.
  - **side_sheet (90, 0)** (+X end): two posts, the end rail between them with a stub on each outer face, the deck end,
    blocks with bolts on both posts' end faces, the V braces.
  - **rear_sheet (180, 0):** the rail side: four posts and the rail, bolts, braces, the stairs at the right end.
  - **top (0, 89.9):** long axis horizontal like the cell; 17 planks across, 8 post tops (6 caps with pale dots and the
    two support posts hidden under the planks), the back rail and the end rail; the stairs at the left end (the cell
    draws them off the bottom side, §3.3).

## 3. View conflicts and resolutions

### 3.1 Proportions: the three-quarters (W / bay 0.61–0.71) vs top (1.01) vs side + front (1.37); bay / H 0.84–0.90 (front, rear) vs 1.10–1.23 (f34)

- **Evidence:** §1.1 table. Each cell has its own horizontal scale (the M048 / M050 pattern).
- **Resolution (decision §8.1):** **W 8 (the kit route width), bay 9.412 (5 planks), H 9.0**: the f34's W : H lands
  on the sheet (1.979 against 1.958) and the deck is one 32-stud tile. The front and side cells' W : H are recorded
  misses. **Alternative:** bay 8 (deck 27.2; closer to the front and top cells; f34 W : H then needs e ≈ 12).

### 3.2 Which edges carry a rail: back side and one end (both three-quarters) vs eight caps in the top view

- **Evidence:** both three-quarters draw the rail along the far long side only, plus across the right end, and the
  near long side open (its middle posts stop under the deck with bolt blocks). The front and rear cells are consistent
  with that (the far rail shows through the open side). The top cell draws a cap at all eight post positions.
- **Resolution (decision §8.3):** **rail along +Y (4 posts, 3 rail planks) and across +X; six full-height rail posts
  (the far four and the near corners); the near middle posts are support posts under the deck.** The top cell's two
  near middle caps are a recorded miss. **Alternative:** rails on both long sides (closes the T-join side).

### 3.3 Stairs position: −X end (f34, close-up A, front, rear) vs off the long side at the right end (top) vs beyond the railed end (r34)

- **Evidence:** the f34 treads run across the width and step down toward −X below the end plank, beside the near-left
  corner post (close-up A agrees); the front cell draws them at its left end (−X seen from −Y), the rear cell at its
  right end (−X seen from +Y). The top cell puts 3 treads below the bottom edge at the right end; the r34 puts them
  beyond the railed end.
- **Resolution (decision §8.4):** **at the −X end, across the full stair width (8.0, y ±4.0), stepping down along −X.**
  The top cell's and the r34's placements are recorded misses.

### 3.4 Tread count: 2 (f34, close-up A) vs 3 (front, top, exploded) vs 4 (parts list)

- **Evidence and why it matters:** with the deck at 5.6, two treads make risers of **1.87**, three **1.40**, four
  **1.12**. A stair that needs a jump at every step is not a stair.
- **Resolution (decision §8.4):** **4 treads, risers 1.12, treads 1.46 (two boards each)**: the parts list's count
  and the most walkable; the f34's two-board treads and open risers are kept. **Alternatives:** 3 treads (risers 1.40,
  run 4.4: the top cell and exploded), or 2 as the hero (risers 1.87, jump-only).

### 3.5 Bracing: knee braces at front post 2 and post 4 (front cell) / their mirror (rear cell) vs a V at the end (side cell) vs an X under the deck (close-up B) vs the key's L brace

- **Evidence:** the front and rear cells agree on one 3D layout (a knee brace from the +X end leg inward and from the
  −X middle leg toward the centre, on both sides); the side cell draws a V between the end legs; close-up B an X with
  a peg; the key Brace an L (leg + diagonal).
- **Resolution (decision §8.6):** **a symmetric superset**: end V braces (4), knee braces from both end legs inward (4)
  and from both middle legs toward the centre (4), X braces at the two middle rows (4 boards, a bolt at each crossing).
  The −X end leg's long-side brace and the +X middle legs' braces are not drawn on the sheet (hidden by the stairs /
  not drawn). **Alternative:** only what the cells draw (asymmetric: end-leg brace at +X, middle-leg brace at −X).

### 3.6 Deck planks broken at mid-width (f34 tops) vs full-width (top cell, exploded, keys)

- **Resolution:** **full-width planks** (top view, exploded, key plank); the f34's mid-width seam is per-plank value
  variation (Tint), not geometry. The key plank's faint lengthwise top line is not modelled (a groove reads as twice
  the planks from above).

### 3.7 The near middle posts: support posts under the deck (f34, r34) vs caps in the top view's bottom row

- **Resolution:** **support posts ending under the planks** (both three-quarters; the exploded and the key name a
  "Support Post"). Recorded miss in the top cell.

### 3.8 Rail joints: butt (close-up C) vs passing behind the posts (f34, front cell)

- **Evidence:** in the f34 and front cell the posts sit in front of the rail; close-up C says the rail planks "join to
  post with flat faces" and shows a rail end butting a post face.
- **Resolution:** **rail planks butt into the post faces on the post line** (end faces sunk 0.02), plus **stubs** at
  the run ends (the f34's blocks on the far-left and near-right posts; the side cell's stubs). A rail on the posts'
  outer faces is the alternative (it would read as passing behind the posts in the f34, but leave the joint invisible).

### 3.9 The rear three-quarter is not a rear view

- **Evidence:** it repeats the f34's layout from almost the same camera (rail far, near side open, railed end right,
  the rope on the near-right post) but moves the stairs to the far right beyond the railed end. No camera on a
  consistent model reproduces both.
- **Resolution:** the f34 governs; `r34_sheet (134, 15)` is a true rear three-quarter, judged on W : H and content
  only.

### 3.10 Leg colour: dark legs (f34, under the deck) vs legs the colour of the posts (front, side, rear cells)

- **Evidence:** front legs `#A2511B` against the post faces above the deck `#9D4D19`; side `#9A4E1E` against
  `#984D1C`; the f34's dark legs (`#6B351B`) are in the deck's shadow (its lit near support leg is `#AE581E`).
- **Resolution:** **no leg darkening** (unlike M048's brown legs and M050's 50 %): the studio's own shadow under the
  deck darkens them (M048 finding 7: "legs a little too dark in side-lit views").

### 3.11 The rope tie: both three-quarters vs not in the parts list

- **Resolution:** **kept as hero dressing** (§2.8); no rope part.

### 3.12 "Broad flat-shaded faces" vs the soft lighter plank and tread edges (close-up A, f34)

- **Resolution (decision §8.5):** crisp planks and treads (the note; M050's decision), the caps' 0.10 chamfer the only
  bevel. **Alternative:** a 0.05 top-edge chamfer on planks and treads (M048's look; +≈ 400 tris, affordable).

### 3.13 Cast shadow

- The sheet's ground shadow is pale lilac-grey (B). Render every `*_sheet` view with the studio floor hidden.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

All pieces are explicit low-poly solids (prisms, boxes, tubes). **No booleans are needed**: every piece is its own
closed shell, touching or sunk 0.02 into what carries it.

**Helper reuse (decision §8.10).** `m048.py` is committed: import `_solid`, `_prism`, `_box`, `_rect`, `_brace_quad`,
`_tube`, `_knob`, `_bolt` (pass `sides=6` for the hex head), `_tri_ngons`, `winding_report`, `contact_report`,
`shells_report`, `measure` / `classify` if they fit. Never import M048's constants or palette; never edit `m048.py`;
import nothing from `m050.py` or `m051.py` (untracked / not written).

1. `rail_post(px, py, seed)` → post prism with cap chamfer, peg-dot inset, block, bolt. **Part
   `TimberBoardwalkRailPost`** (key "Rail Post / Support Post").
2. `support_post(px, seed)` → box, block, bolt. **Part `TimberBoardwalkSupportPost`**.
3. `side_beam(sy)`, `crossbeam(x)`, `header(sx)` → boxes. **Part `TimberBoardwalkCrossbeam`** = one crossbeam.
4. `plank(i, seed)` → plain or notched prism. **Part `TimberBoardwalkFloorPlank`** = one plain plank.
5. `rail(x0, x1)` / `end_rail()` / `stub(...)` → boxes. **Part `TimberBoardwalkRailPlank`** = one back-rail plank.
6. `brace(...)` (knee, V, X boards with `_brace_quad`), crossing bolts. **Part `TimberBoardwalkBrace`** = the key's
   L: a 2.4-tall leg piece (1.5 × 1.5 × 2.4) and one knee-brace board rising from low on its face, sunk 0.02 into it.
7. `stairs()` → treads + cut stringers. **Part `TimberBoardwalkStairs`**.
8. `rope_tie()` → wrap, tail, knob (hero only).
9. **Hero `TimberBoardwalk`** = 6 rail posts + 2 support posts + 12 blocks + 14 bolts + 6 peg dots (insets) + 2 side
   beams + 4 crossbeams + 2 headers + 17 planks + 4 rail planks + 4 stubs + 16 brace boards + 8 tread boards + 2
   stringers + the rope tie (wrap, tail, knob).
   - Each piece a closed shell in one object; no unions.
   - `M.fix_bowties`; origin at the bbox bottom centre (deck centre at x +2.92, recorded); transforms applied.
10. **Parts shot** (az −35, e 25), laid out like the key column: post, rail plank, floor plank, stairs, crossbeam,
    brace (+ the support post).

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a long level plank walkway on square posts; a chunky rail along the back and across one end;
   the front side open; stairs stepping down from the other end; bolt blocks at every post; braces underneath.
2. **f34_sheet, r34_sheet, front_sheet, side_sheet, rear_sheet, top** per §2.9.
3. **Level check (numbers):** deck top 5.60 ± 0.02 on every plank; post tops 9.00; rail 6.85 → 7.75; beams and
   crossbeams 3.45 → 4.77; bolts at 4.12; tread tops 4.48 / 3.36 / 2.24 / 1.12; stair foot x −21.84; support-post tops
   4.77.
4. **Walk check:** a 5.5 marker on the ground at the stair foot, on each tread, on the deck at the stairs end, at
   mid-deck by the open edge and by the rail; print the largest plank-to-plank step (≤ 0.02), the risers (1.12) and
   the clear widths (8.5 / 6.5).
5. **Stair extra** `stair_cu (−40, 18)` framed on the −X end against close-up A: two-board treads, open risers,
   stringers, the corner post with its block and hex bolt.
6. **Underside extra** `under_cu (−30, −35)` against close-up B: plank bottoms on the beams, crossbeams, the X brace
   with its bolt, a post with block and bolt.
7. **Rail extra** `rail_cu (−35, 20)` on the far-right post against close-up C: the back rail and the end rail butting
   its faces, the stubs.
8. **Scale and kit shots:** character markers; the boardwalk's open side against an M043 lower lawn and a bridge or
   dock T-joined to it, if they are in the kit file, from (45, 25).

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Rail posts (prism with cap chamfer, peg-dot inset) | 6 | ≈ 36 | 216 |
| Support posts | 2 | 12 | 24 |
| Blocks | 12 | 12 | 144 |
| Bolt heads (hex, domed) | 14 | ≈ 22 | 308 |
| Planks: plain / notched one end / notched both ends | 9 / 4 / 4 | 12 / ≈ 20 / ≈ 28 | 300 |
| Side beams, crossbeams, headers | 2 + 4 + 2 | 12 | 96 |
| Rail planks + stubs | 4 + 4 | 12 | 96 |
| Brace boards | 16 | 12 | 192 |
| Tread boards | 8 | 12 | 96 |
| Cut stringers (≈ 12-vertex profile) | 2 | ≈ 44 | 88 |
| Rope wrap (5 × 8, twisted) | 1 | 80 | 80 |
| Rope tail (5 sides × 8 rings) + knob | 1 | ≈ 70 + 36 | 106 |
| **Hero** | | | **about 1750** (limit 4000) |
| Parts: RailPost / SupportPost / RailPlank / FloorPlank / Stairs / Crossbeam / Brace | | | ≈ 80 / 46 / 12 / 12 / 184 / 12 / 24 (limit 1000) |

- **Headroom ≈ 2200.** If the main session wants more read, spend it in this order: plank / tread top chamfer 0.05
  (§3.12, ≈ +400); 8-sided bolt heads (+≈ 110); 6-sided rope (+≈ 40). If the hero ever passes 3900, undo those first,
  then drop the rail stubs (−48) and the X braces (−48 + 2 bolts). Never drop a post, plank, rail plank, tread,
  stringer, block or the end-face blocks.

### 4.4 Shape targets (binding; check with `M.audit` and own bmesh code)

| Target | Posts | Planks / treads | Rails | Beams / braces | Bolts | Rope |
| --- | --- | --- | --- | --- | --- | --- |
| Section | 1.5 square, chunky | 1.78 × 0.85; treads two 0.70 × 0.55 boards | 0.6 × 0.9 | beams 0.9 × 1.32; braces 0.6 × 0.45 | hex Ø 0.55, 0.22 proud | Ø 0.30, twisted |
| Edges | cap chamfer 0.10; others crisp | crisp (§3.12) | crisp | crisp | 6 facets + low dome | twisted facets |
| Not | no taper, no rounded caps, no subdivision | no warp > 0.02, no grain, no groove | **not thin** (≥ 0.55 thick, ≥ 0.85 tall), not a fence of two rails | no floating braces | not round, not grey | not a thin line, not golden |

- **Posts stronger than rails** (WorldModeling §13.1): post 1.5 against rail 0.6 × 0.9.

### 4.5 Stages 2 and 3

- **Stage 2:** every shell closed and manifold; zero non-manifold edges and verts (`nonmanifold_verts` 0), boundary,
  wire and loose elements; no zero-area faces or n-gons (the notched plank caps, the stringer profiles, the bolt domes
  and the post caps are the places to check); normals outward; **0 winding errors** in `build()`'s problems list
  (STAGES "Consistent winding": the stringers' sawtooth caps and the notched planks' caps are non-convex — ear-clip, not
  a fan from vertex 0 — and check each triangle against the face's normal); no corners under 5° on visible faces.
- **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box, sd ≤ 1.0)

| Swatch | Box | Hex | HSV | Use |
| --- | --- | --- | --- | --- |
| 1 Orange wood | (698,38,750,79) | `#B36E3F` | 24°, 0.65, 0.70 | the timber's flat paint (between the rendered tops and the vertical faces) |
| 2 Tan | (761,38,813,79) | `#E1CBAC` | 35°, 0.24, 0.88 | **unused** (the sheet's rope renders orange, §5.2) |
| 3 Grey | (824,38,876,79) | `#B6B8BA` | 210°, 0.02, 0.73 | **unused** ("pale faceted rock (not used in this asset)") |
| 4 Green | (887,38,939,79) | `#97AA7E` | 86°, 0.26, 0.67 | **unused** (no moss or grass) |
| 5 Blue | (950,38,1002,79) | `#36A8CD` | 195°, 0.74, 0.80 | **unused** (no water drawn) |

### 5.2 Rendered regions (`samp.py`, `rope.py`; median / lit quartile / shade quartile)

| Region | f34 / r34 | front / side / rear / top | keys / exploded / close-ups |
| --- | --- | --- | --- |
| Plank tops | **`#DB8133`** (28°, .77, .86) / lit `#ED9644`; mid-deck `#E58B3B`; end plank `#E38C3D`; r34 `#DE8335` | top **`#D87E37`** (26°, .75, .85) | key plank `#EB974F`; exploded `#E1863F` |
| Plank ends (vertical) | | front plank band `#C36726` (25°, .81, .76) | |
| Tread tops | upper `#E88F40`, lower `#EA9346` (28°, .70–.72, .91–.92) | | cu A `#E99144` |
| Tread / stair faces | K `#8B4317`; front faces `#94491B` | rear (shade) `#6A3419`; top stairs `#C37332` | key stairs `#88422D` |
| Post faces above the deck | NR `#9C4B16` (24°, .86, .61); F2 `#9A4913`; F3 `#894014`; NL `#A85016` | front **`#9D4D19`** (24°, .84, .62); side `#984D1C`; rear `#944B1A` | key post `#914619`; cu A `#8A4117`; cu C `#A7561D`; cu A cap `#9A4B15` |
| Cap tops | FL cap top **`#F59B48`** (29°, .71, .96) | top-view caps `#CA702A` (0.93 of the planks beside them) | |
| Legs (below the beams) | near support leg (lit) `#AE581E`; NL leg (shade) `#6B351B`; r34 `#8A3E0E` | front **`#A2511B`** (= the post faces); side `#9A4E1E` | cu B `#763C1E` (underside, shade) |
| Beams | near beam (lit) `#A14F19` | front **`#7D3D18`** (22°, .81, .49); side `#7E3E1A` | key crossbeam `#91481C` |
| Blocks | | front `#AF5D1D` (26°, .83, .69), a touch brighter than the posts; side `#A2561A` | |
| Rail | far rail `#B85B1C` (24°, .85, .72) | front **`#B25D20`** (25°, .82, .70); rear `#B25D21`; top strip `#D98337` | cu C `#BA6F3F`; key `#88421A` (shaded iso) |
| Braces | | front `#602F14` (21°, .79, .38); side `#693216` | cu B `#5C3119`; key `#753C1D` |
| Plank bottoms | | | cu B `#69341A` (20°, .75, .41) |
| All dark wood (K) | f34 `#7B3A14`; r34 `#733511` | rear `#713918` | exploded `#7F3E19` |
| Bolts | f34 **`#FAC77C`** (36°, .50, .98) / `#FDCD80` | front `#F2C38B` (33°, .43, .95); top cap dots `#F6CB8F` (35°, .42, .96) | cu A `#F4CF8F` (38°, .41, .96) |
| Rope | f34 median `#C36A22` / lit **`#E28A38`** (29°, .75, .89) / shade `#A44C19`; r34 median **`#DA8231`** (29°, .77, .85) / lit `#F09C42` | | |

### 5.3 How the colour works

**Wood: one warm orange timber family, by role and position, never by facing — M050's family, which the sheet
matches.** The plank tops (`#DB8133` / `#DE8335`) sit within 5 of M050's board tops (`#DE833B`); the post faces
(`#9C4B16`, front `#9D4D19`) between M050's f34 post (`#8A3D0A`) and its front post (`#A64E13`).
- The lit tops (28°, sat 0.75) against the vertical faces (24°, sat 0.84, value 0.60–0.62) is mostly the light: a
  **hue miss of 2–4° on the vertical faces is a known miss**, not a key error.
- **Role:**
  - planks and treads `m052_wood`;
  - posts `m052_wood_deep`;
  - **blocks** `wood_deep` + 25 % `wood` (front `#AF5D1D` against the post `#9D4D19`);
  - **rail planks and stubs** `wood_deep` + 50 % `wood` (front rail `#B25D20` sits between the post `#9D4D19` and the
    plank ends `#C36726` on the same facing);
  - **beams, crossbeams, headers, stair stringers** `wood_deep` + 35 % `wood_dark` (front beam `#7D3D18`: 0.79 of the
    post's value);
  - **braces** 60 % `wood_dark` (`#602F14` / `#693216` / `#5C3119`).
- **Position:**
  - **caps lighter:** the top 0.6 of each rail post (above the rail) blends toward `m052_wood_light`, 40 % on the
    faces rising to 60 % on the cap chamfer and top (f34 cap top `#F59B48`, the plank tops' lit quartile);
  - **legs: no darkening** (§3.10);
  - a broad lighter field across the deck at 15 % `wood_light`; two or three planks 15 % `wood_deep`.
- **Not red:** plank key hue 26–29° and R − G ≤ 95; check the f34 plank-top median hue ≥ 26° (W08's boardwalk "reads
  slightly redder than the reference").

**Rope: orange-amber, not golden.** The sheet's rope is the planks' colour with a twist (r34 median `#DA8231` against
the plank tops `#DE8335`; f34 lit `#E28A38`, shade `#A44C19`). One key `m052_rope`; one strand of the five (by its
index round the twist, never by the face's normal) blended 50 % toward `m052_wood_deep` for the groove. It reads as rope
by its twisted geometry and knob, not by a gold colour — the opposite of M048's gold excess. It adds **no Y**.

**Brass:** pale gold hex bolt heads and cap peg dots, `m052_brass`, metal finish so they catch the light (M048's
treatment; close-up A's head is a metal hex, not M050's wooden peg).

### 5.4 Keys (start from M050's calibrated hexes for wood, M048's for brass; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are medians of unshadowed rendered regions, not swatches. `K.sample` kinds: `"brown"` for the
woods and rope, `"vivid"` for brass. **Start values** (read them from the files at build time; don't import
constants): M050 `PALETTE` wood `#BB722E`, wood_light `#C57A35`, wood_deep `#80410F`, wood_dark `#65361A`; M048 brass
`#EBC772`.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m052_wood` | **`#DE8336`** plank tops (f34 `#DB8133`, r34 `#DE8335`, top `#D87E37`, exploded `#E1863F`) | 26–29°, 0.72–0.78, R > G > B | planks, treads; 50 % of the rails; 25 % of the blocks | rough 0.85, metal 0, low spec |
| `m052_wood_light` | `#F2963F` (f34 cap top `#F59B48`, the plank tops' lit quartile `#ED9644`) | 27–30°, 0.70–0.76 | caps (40–60 %), the deck's lighter field (15 %) | rough 0.85 |
| `m052_wood_deep` | **`#9A4A16`** (f34 NR `#9C4B16`, F2 `#9A4913`, front `#9D4D19`, side `#984D1C`); check the front_sheet post faces near `#9D4D19` and plank ends near `#C36726` (± 18, light) | 22–25°, 0.82–0.88 | posts; base of blocks, rails, beams, stringers | rough 0.85 |
| `m052_wood_dark` | `#65321A` (front braces `#602F14`, side `#693216`, cu B `#5C3119`, plank bottoms `#69341A`) | 19–22°, 0.73–0.80 | braces (60 %), beams / crossbeams / headers / stringers (35 %) | rough 0.9 |
| `m052_rope` | **`#DA8231`** (r34 median; f34 lit `#E28A38`) | 27–31°, 0.73–0.80 | the rope tie (4 strands; the fifth 50 % `wood_deep`) | rough 0.95, low spec |
| `m052_brass` | **`#F6C886`** (f34 `#FAC77C`, front `#F2C38B`, cu A `#F4CF8F`, top dots `#F6CB8F`) | 34–38°, 0.42–0.50, value ≥ 0.94 | bolt heads, cap peg dots | metal 0.5, rough 0.4 (M048's adjusted brass read gold where the calibrated one went cream) |

**Calibration warnings:**
- **Plank tops:** f34 W median within 12 of `#DB8133`, hue 26–29°, sat ≥ 0.70. Not red (< 25°), not brown (value <
  0.80), not yellow-tan (> 31°).
- **Vertical faces (front_sheet):** plank ends within 18 of `#C36726`, rail within 18 of `#B25D20`, post faces within
  18 of `#9D4D19`, beam within 18 of `#7D3D18`, braces within 18 of `#602F14`. Value order **plank ends > rail >
  blocks ≥ posts = legs > beams > braces**.
- **Legs:** within 0.95–1.05 of the post faces' value in front_sheet and side_sheet (no painted darkening).
- **Caps:** at least as light as the plank tops beside them in the f34; the top render's caps 0.90–1.0 of the planks.
- **Rope:** orange-amber like the sheet, a little lighter than the post behind it; **Y share from the rope ≈ 0** (a
  probe with the rope recoloured blue moves Y by < 0.3).
- **Brass:** reads pale gold, not cream, not grey (the grey swatch is unused), not the wood.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Planks:** `wood` base; per-plank tint ±0.03 (the sheet's planks vary, and the f34's mid-width "breaks" are value
  steps); `wood_light` by a broad noise field (scale ≈ 0.08, one or two patches along the deck) at 15 %; 2–3 planks 15 %
  `wood_deep`. **Hard edges** only between planks (each its own shell).
- **Treads:** `wood`; per-board tint ±0.03.
- **Rail posts:** `wood_deep`; `wood_light` by height over the top 0.6 of the post above the rail line (40 %), rising
  to 60 % on the cap chamfer and top; per-post tint ±0.03. **No dark band at the legs.**
- **Support posts:** `wood_deep`, tint ±0.03.
- **Blocks:** `wood_deep` + 25 % `wood`. **Rails and stubs:** `wood_deep` + 50 % `wood`, per-plank tint ±0.03.
- **Beams, crossbeams, headers, stringers:** `wood_deep` + 35 % `wood_dark`; per-member tint ±0.03.
- **Braces:** 60 % `wood_dark`.
- **Rope:** strand roles (§5.3); per-piece tint ±0.02.
- **Hard edges only** where materials meet: brass | block, brass | cap, rope | post, rope | plank.

### 5.6 Texture (Tint) and finish

- **Tint:** planks amp 0.03 per plank plus 0.02 at scale 0.3; framing 0.03 per member; rope 0.02; brass none.
  **Never per-triangle confetti**, no grain stripes (the sheet's faint post streaks are carried by the per-member
  tint).
- **Finish:** wood rough 0.85–0.9, metal 0, low spec; rope rough 0.95; brass metal 0.5, rough 0.4. No emission
  anywhere.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Shares** per §2.9; **colours** per the §5.4 warnings, in f34_sheet, front_sheet, side_sheet and top. `K.check`
  facing correlation < 0.5 on every wood material (plank tops and ends are one key; post faces one key).

## 6. Joins and contact (no floating dressing)

- **Posts:** feet flat on z 0 (each post one shell, ground → cap). Support posts' tops sunk 0.02 into the plank
  undersides.
- **Beams on posts:** each side beam's outer face sunk 0.02 into the posts' inner faces (rail posts and support
  posts); its top sunk 0.02 into the planks.
- **Crossbeams and headers:** end faces sunk 0.02 into the side beams' inner faces; tops sunk 0.02 into the planks.
- **Planks on the frame:** every plank's underside sunk 0.02 into both side beams (and the crossbeam / header / support
  post under it, if any); notched planks clear the post faces by 0.02 (no coincident faces); gaps 0.06–0.14 (no
  overlaps).
- **Blocks:** sunk 0.02 into the post faces; the end-face blocks also touching the side beam's outer face. **Bolts:**
  sunk 0.03 into the block (or X board B). **Peg dots:** insets in the cap top (not separate shells).
- **Rails:** end faces sunk 0.02 into the post faces; stubs sunk 0.02 into their post faces.
- **Braces:** each end face sunk 0.02 into the leg face or beam underside it meets; X boards touch at the crossing.
- **Stairs:** stringer feet flat on z 0, back faces sunk 0.02 into the side-beam ends; tread boards sunk 0.02 into the
  stringer seats; T1's back face sunk 0.02 into the −X header. No tread touches a post.
- **Rope:** the wrap's inner surface sunk 0.02 into the near-right post; the tail starts inside the wrap (≥ 0.10) and
  lies on the planks sunk 0.03 (never more than 0.05); the knob sunk 0.03 into a plank top.
- **Chain to ground:** posts → ground; beams → posts; crossbeams, headers → beams; planks → beams; blocks → posts;
  bolts → blocks; rails, stubs → posts; braces → legs and beams; stringers → ground and beams; treads → stringers;
  rope → post and planks.
- **Count floating shells before reporting** (STAGES; 035 and 036 failed round 1 on this): **0**. A shell floats if
  its nearest distance to every other shell and the ground is > 0.03, or if it doesn't chain to the ground.
- **Buried shells:** no bolt, block, stub, tread or rope piece more than 0.05 inside a post, plank, beam or stringer
  beyond its stated sink (ray parity after the final placement step, as STAGES asks; 046 had leaves inside a core).
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0 (bolt domes, the wrap ring, the knob, the stringer
  sawtooth corners).
- **Winding:** 0 errors per shell (the notched planks' caps, the stringers' sawtooth caps, the hex bolts and the
  hand-listed boxes and brace quads are where a reversed face slips in; 044's wedge back face).

## 7. Water, lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** sunlit orange timber, pale-gold bolt heads and an orange rope on white paper, a pale
lilac-grey ground shadow. **No water, foam, glow, light, sparkle, dust, smoke or VFX callout.** The blue swatch is
unused.

- **Water and foam: none in the model.** No `*water*` key, no foam mesh, no sockets.
- **Stage 5 (lighting): skip, and record why.** No emissive faces, no PointLight. Studio notes (Requires Manual
  Validation):
  - the planks read warm orange (not red, not brown), the posts a step deeper, the legs the posts' colour (only the
    deck's shadow darkens them), the braces darker;
  - the bolts read pale gold, the rope orange;
  - **a character walks from the ground up the four treads (risers 1.12) onto the deck without jumping**, along it,
    and onto a 5.6 surface across the open side; the back rail and the end rail stop it. Edge safety on the open side,
    if wanted, is a Studio-side invisible collider (not part of this model).
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".**
- **Collision:** hero `precise` (the deck and treads walkable, posts and rails solid, the space under the deck open);
  `TimberBoardwalkFloorPlank`, `TimberBoardwalkRailPlank`, `TimberBoardwalkCrossbeam` `box`;
  `TimberBoardwalkRailPost`, `TimberBoardwalkSupportPost`, `TimberBoardwalkBrace` `hull`; `TimberBoardwalkStairs`
  `hull` (a smooth ramp when used alone).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json` and the repo
text (`git grep`) for Boardwalk, Walkway, Plank, Pier, Deck:
- **W08** owns `Boardwalk`, `BoardwalkStraight`, `BoardwalkCornerL`, `BoardwalkRampEnd`, `BoardwalkStairs`,
  `BoardwalkRailPost`, `BoardwalkRail`, `BoardwalkFloorPlank`, `BoardwalkSupportPost`, `BoardwalkCrossbeam` (this
  sheet's own labels under the old kit's prefix), plus `Dock*` (incl. `DockDeckPlank`), `Footbridge*` (incl.
  `FootbridgePlank`), `RopeCrossing*` (incl. `RopeCrossingPlank`); keys `w08_*`.
- **M048** owns `TimberDock*` (incl. `TimberDockDeck`; keys `m048_*`); **M050** `TimberBridge*` (incl.
  `TimberBridgePlank`; keys `m050_*`); **M051** `RopeBridge*` (keys `m051_*`).
- Other names: `WatchtowerDeckFloor`, `WallWalkFloorPlank`, `MinecartBasePlank`, `LookoutPlatformFloorPlanks`,
  `StoneArchPierBlocks`; "Walkway" appears only as INDEX / MODEL_PROGRESS row 098 ("Root Arch Walkway"), no object.
- **`TimberBoardwalk` and `m052_` occur nowhere** in the builders, the manifests or the repo text. `M.mk` guards only
  exact-name clashes (`kit_models.mk`), and no `Boardwalk*` name equals a `TimberBoardwalk*` name. (`.blend` contents
  were not decompressed; check the built names once.)

| Object | Part | Why |
| --- | --- | --- |
| `TimberBoardwalk` | hero: posts, planks, framing, rails, braces, stairs, bolts, rope tie | W08 owns `Boardwalk*`; parallels `TimberDock` / `TimberBridge` |
| `TimberBoardwalkRailPost` | "Rail Post": one full-height post with its block, hex bolt, cap and peg dot | key "Rail Post / Support Post" |
| `TimberBoardwalkSupportPost` | "Support Post": the short post with its block and bolt | exploded label |
| `TimberBoardwalkRailPlank` | "Rail Plank": one back-rail plank | |
| `TimberBoardwalkFloorPlank` | "Floor Plank": one plain plank | |
| `TimberBoardwalkStairs` | "Stairs": four two-board treads on two cut stringers | |
| `TimberBoardwalkCrossbeam` | "Crossbeam": one crossbeam | |
| `TimberBoardwalkBrace` | "Brace": the key's L (a 2.4 leg piece + one knee-brace board) | |

- Palette keys `m052_wood`, `m052_wood_light`, `m052_wood_deep`, `m052_wood_dark`, `m052_rope`, `m052_brass` (§5.4).
  Collection `Kit/M052 Boardwalk`. No sockets.

**Decisions needed (a recommendation each):**
1. **Size and level** (§1.1, §2.1, §3.1): **deck top 5.6 (the kit's deck / lower-lawn level), post tops 9.0, rail
   6.85 → 7.75, post centres W 8 × 3 bays of 9.412, deck 32 × 9.5 (one tile), 17 planks; overall ≈ 37.84 × 11.06 ×
   9.0 with the stairs** (recommended: the sheet's sections land on the kit's timber at this level, the route width
   matches the dock and bridge, and the stairs give the 5.6 network the way up from the ground that M048 / M050 lacked).
   Or bay 8 (deck 27.2, closer to the front and top cells). A low marsh variant (deck ≈ 2, W08's idea) is a parameter
   change, not built now.
2. **Build frame and origin** (§1.1): **long axis X; rail side +Y, railed end +X, stairs −X, open side −Y; origin at
   the bbox bottom centre per STAGES, which puts the deck centre at x +2.92 (recorded in the docstring and export
   notes)** (recommended). Or keep the origin at the deck centre (easier tile placement, against the STAGES rule).
3. **Rails and posts** (§3.2, §3.7, §3.8): **back rail (3 planks) and the +X end rail, butt-jointed on the post line
   at 6.85 → 7.75, 0.6 × 0.9, with 4 run-end stubs; six full-height rail posts; two support posts under the open
   side** (recommended: both three-quarters, the front, rear and side cells, close-up C). Or rails on both long sides
   (the top cell's eight caps; closes the T-join side). Builder parameters `W`, `NP`, `PITCH`, `BAY`, `DECK_TOP`,
   `POST_TOP`, `RAIL_Z`, `NT` and the flags `STAIRS`, `END_RAIL`, `RAIL_SIDES`; build only the drawn version.
4. **Stairs** (§2.7, §3.3, §3.4): **at the −X end, 8.0 wide, 4 two-board treads, risers 1.12, treads 1.46, two cut
   stringers to the ground** (recommended: walkable; the parts list's count; the f34's placement and two-board treads).
   Or 3 treads (risers 1.40) or the hero's 2 (risers 1.87, jump-only). Whether 1.12 walks without a jump is a Studio
   check.
5. **Planks** (§2.4, §3.6, §3.12): **17 full-width crisp planks 1.78 × 0.85, seams on the post rows, 8 notched round
   the rail posts** (recommended: M050's convention). Or a 0.05 top-edge chamfer on planks and treads (close-up A's
   soft edges; +≈ 400 tris).
6. **Framing and bracing** (§2.3, §2.6, §3.5): **side beams full length, 4 crossbeams, 2 end headers, 12 blocks with
   hex bolts; braces: end V (4), end-leg knees (4), middle-leg knees toward the centre (4), middle-row X braces (4
   boards, a bolt at each crossing)** (recommended: a symmetric superset of every cell). Or only what the cells draw
   (asymmetric).
7. **Rope tie** (§2.8, §3.11): **one twisted wrap on the near-right post at 6.45 with a tail lying on the deck and a
   knob; 5 sides, `twist=True`** (recommended: both three-quarters). Or leave it out (not in the parts list).
8. **Colour** (§5): **M050's timber family by role and position: planks `#DE8336`, posts `#9A4A16`, blocks +25 % wood,
   rails 50 / 50, beams and stringers 35 % dark, braces 60 % dark, caps toward `#F2963F`, legs not darkened; rope
   orange `#DA8231`; brass `#F6C886` (metal 0.5); tan, grey, green and blue swatches unused** (recommended). Never by
   facing; not red.
9. **Bolts** (§2.2): **hex brass heads (6 sides, domed, metal 0.5)** (recommended: close-up A). Or M050's wooden pegs
   (rough 0.55, metal 0).
10. **Helpers:** **import M048's geometry helpers (committed); never its or M050's constants; nothing from `m050.py` /
    `m051.py`** (recommended).
11. **Packaging:** **one hero object of closed shells (no booleans); seven parts: RailPost, SupportPost, RailPlank,
    FloorPlank, Stairs, Crossbeam, Brace** (recommended). Or fold SupportPost into RailPost (the key's one "Rail Post /
    Support Post").
12. **Comparison cameras** (§2.9): `f34_sheet (−46, 14)` governing (probe az −40 / −46 / −52 × e 12 / 14 / 17);
    `r34_sheet (134, 15)` (not binding on composition); `front_sheet (0, 0)`; `side_sheet (90, 0)`; `rear_sheet (180,
    0)`; `top (0, 89.9)`. Extras: parts shot, `stair_cu`, `under_cu`, `rail_cu`, the walk and kit shots. Floor hidden in
    every `*_sheet` render.
13. **Stages 5 and 6:** **skip both, recorded; no water, foam or sockets** (recommended).
14. **Collision** as in §7 (recommended).
15. **Budget** (§4.3): **4000 limit, plan ≈ 1750; headroom for chamfers / 8-sided bolts if wanted** (recommended).
16. **Names** as proposed: `TimberBoardwalk*`, keys `m052_*`. Or `TimberWalk*` if the main session wants no
    "Boardwalk" substring at all.

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **A hovering plank carpet** (WorldModeling §13.2). Load-bearing first: legs on the ground, beams on the posts,
   crossbeams and headers between the beams, planks on the frame, stairs on stringers on the ground. The underside
   render must show every plank resting on both beams and every tread on both stringers.
2. **Floating or buried pieces** (STAGES; 035 and 036 round 1; 046's leaves inside a core). Blocks on the posts,
   bolts in the blocks, rails and stubs in the post faces, support-post tops under the planks, treads on the stringer
   seats, the rope tail lying on (not in) the planks. Count floating shells: **0**; buried beyond the stated sinks:
   **0**.
3. **Inward faces / broken winding** (044's wedge back face; STAGES "Consistent winding"). The stringers' sawtooth
   profiles and the notched planks' caps are non-convex: ear-clip them and check every triangle with a parity ray
   test, not only the signed volume. Hex bolts, brace quads and hand-listed boxes: 0 winding errors per shell.
4. **Legs too dark in side light** (M048 finding 7: front legs Δ41 against the sheet). Here the legs are the posts'
   colour on the sheet: no painted darkening; check legs / posts value 0.95–1.05 in front_sheet and side_sheet.
5. **Gold excess** (M048 finding 3: f34 Y +2.7, mostly rope; W08's "saturated yellow" rope). This sheet's rope is
   orange-amber and its Y is only bolts and cap dots: f34 Y 2.1 ± 1.5; the rope adds ≈ 0.
6. **Rope that reads as a faceted collar or a thin line** (M048 finding 1; W08; M034's foam outlines). The wrap is
   twisted (`twist=True`), Ø 0.30, sunk into the post; the tail has a twist and a knob.
7. **Wood that reads red, brown or flat orange** (W08's boardwalk "slightly redder"; W08 dock / footbridge "slightly
   red" / "flat orange"). Plank tops hue 26–29°, sat 0.72–0.78, value ≥ 0.82; posts a step deeper; rails between;
   per-plank tint so the deck isn't one flat colour.
8. **Colour by facing.** The sheet's light tops and dark sides (and the dark legs in the f34) are the light. Role
   (plank / post / rail / beam / brace / strand) and position (cap height, the deck field) only; `K.check` < 0.5 on
   every material.
9. **A thin fence instead of a chunky rail** (W08's "plank-fence railing", double rails). One rail plank per bay,
   0.6 × 0.9, on the back side and one end only; posts 1.5, clearly stronger.
10. **Stairs that don't work** (W08's "ramp not stairs"). Four treads, risers 1.12, two-board treads, open risers, on
    stringers that reach the ground; the top tread meets the header, not a post. The walk check (§4.2) prints them.
11. **Proportions from a single cell** (§3.1). The ortho cells are drawn at their own scales; W 8 × bay 9.412 × H 9
    governs, with the f34 W : H as the check.
12. **Egg or blob shapes where the sheet is square** (M034 / M037 "egg boulders"). Posts, planks, beams, blocks, rails
    and braces are crisp boxes; only the caps carry one chamfer; bolts hex with a low dome. No subdivision, no smooth
    shading.
13. **Names and scope.**
    - No `Boardwalk*`, `Dock*`, `Footbridge*`, `RopeCrossing*` (W08); no `TimberDock*` (M048), `TimberBridge*` (M050)
      or `RopeBridge*` (M051).
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit other models' builders, `kit_models.py`, `kit_mcp.py`, `build_kit.py` or `lib/vfx.py` (frozen).

## Decisions (main session, 2026-10-29)
All 12 recommendations are accepted.
1. **Proportions:** post centres 8 across × 3 bays of 9.412. The deck is 32 × 9.5 with its top at 5.6. Posts are 9.0 tall and the rail runs 6.85–7.75.
2. **Origin:** bottom centre of the bounding box (STAGES rule). Record the deck-centre offset (x +2.92) in the builder and in the export notes.
3. **Rails:** along the back (+Y) and across the +X end, with six full-height rail posts. The front (−Y) side is open.
4. **Stairs:** at the −X end, 4 treads with 1.12 risers, 8.0 wide. Studio must confirm a character can walk up them without jumping; until then, record this as Requires Manual Validation.
5. **Planks:** 17, with crisp edges. The 8 at the post rows are notched round the posts.
6. **Braces:** the symmetric set — end V braces, knee braces, and X braces under the middle rows.
7. **Rope tie:** kept on the front-right corner post, with its tail lying on the deck. Twisted geometry; orange-amber, with almost no gold.
8. **Bolts:** brass hex heads, metal finish.
9. **Helpers:** import M048's geometry helpers. No M048 constants, and nothing from `m050.py` or `m051.py`.
10. **Parts:** the seven proposed. Stages 5 and 6 are skipped and recorded.
11. **Names:** `TimberBoardwalk*`, keys `m052_*`, collection `Kit/M052 Boardwalk`.
12. **Cameras:** the f34 at (−46, 14) governs. The rear three-quarter is judged on content only.

**Colour:** M050's timber family, set by role and position, **never facing**, and never red. The legs are not painted darker than the posts. **Packaging:** every piece is its own closed shell, with **no floating pieces** and **0 winding errors**. Check winding carefully on the sawtooth stair stringers and the notched planks. **Binding targets:** the f34 shares in §1, within ±4, and the deck must be walkable.
