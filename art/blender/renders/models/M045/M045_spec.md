# 045 Pine Sapling — spec

Reference: `art/blender/assets/references/045.png` (1024 × 1536 px). The sheet's title is "PINE SAPLING", "PAGE
47/132"; the intro reads (paraphrased) "a young pine tree with simple, chunky forms, designed for readability and
reusable modular parts". The footer reads "FLINTBORN — INDIVIDUAL MODEL STUDY". INDEX.md row 45 calls it "Flintborn pine
sapling model study".
Builder: `art/blender/kit/mcp/m045.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7. The main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet. Colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7). Trees: "a detailed skeleton plus foliage clumps; roots,
branches and every view matter" (memory `kit-tree-detail`). Here the skeleton is the trunk and its root flares, and
the sheet draws no branches (§3.10).

**The sister sheet 042 Young Fir is being modelled now (`M042_spec.md`).** The two sheets have almost the same
silhouette proportions (§1.5). This spec therefore lists what makes 045 a different kit piece, and the verifier must
check those points (§1.5, §9).

Sheet text:
- **Hero cells:** "ASSEMBLED — FRONT THREE QUARTER" and "ASSEMBLED — REAR THREE QUARTER". Both are near-frontal (§3.1).
- **"ORTHOGRAPHIC VIEWS (ASSEMBLED)":** "FRONT", "SIDE", "REAR", "TOP". The first three are low views (e ≈ 5°); the top is
  a plan.
- **"EXPLODED CONSTRUCTION":** "TOP FOLIAGE TIER", "LOWER FOLIAGE TIER", "TRUNK", "GROUND FOLIAGE", "ROCK (MEDIUM)",
  "ROCK (SMALL)". Dashed arrows drop the top tier onto the lower tier, the lower tier onto the trunk, and plants onto
  small sand puddles. **Only two foliage tiers are drawn**, although every assembled view has three (§3.2).
- **"CONSTRUCTION CLOSE-UPS":**
  - "TRUNK TO FOLIAGE JOINING SURFACE": "Foliage tier has a recess. Trunk has a matching peg. Simple vertical
    assembly. Clean, chunky forms."
  - "FOLIAGE TIER DETAIL": "Broad, flat shaded faces. Simple angular planes. Consistent thickness. Clear silhouette
    from all sides."
  - "UNDERSIDE VIEW (ASSEMBLED)": "Trunk base with simple root flares. Rocks and foliage placed at ground level. Clean,
    readable geometry. No hidden detail complexity."
- **Material palette:** "FOLIAGE DARK", "FOLIAGE MID", "FOLIAGE LIGHT", "TRUNK", "ROCK", "GROUND FOLIAGE". The "ground
  foliage" swatch is a **tan** (`#C29E7E`), not a green. It is the ground/sand tone (§3.8). There is no separate sand
  swatch.
- **Model notes** (paraphrased): a simple, readable silhouette with three foliage tiers; modular, reusable parts
  (foliage tiers, trunk, ground pieces); broad flat-shaded faces with no fine detail or texture noise; clean, game-ready
  low-poly topology; chunky, clear forms.
- **Game context and the old kit:**
  - **W04 Pines & Firs owns every `Sapling*` name.** `art/roblox/kit/W04/manifest.json` has `Sapling` (4.5 × 5.7 × 4.5,
    1011 tris), `SaplingBushy`, `SaplingSeedling`, `SaplingSlender`, `SaplingTopFoliage`, `SaplingLowerFoliage`,
    `SaplingTrunk` and `SaplingRootsBase`. The last four mirror this sheet's exploded labels, so W04's sapling came
    from a sheet like this one. V02 owns `HazelShrubSapling` and V06 owns `BirchSapling` (§8).
  - **Kit pines already built:** M032 and M037 (`pine` pieces). §4.4 of `M042_spec.md` lists their weaknesses, and the
    same lessons apply here.
  - **Other sheets on the subject:** 042 Young Fir (16 tall, being modelled), 047 Old Pine, 049 Classic Pine and 094
    Snow Pine. The sapling must be the smallest of them (§1.1).

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, with the origin at the top left. The paper is
`#F9F6EA` (249, 246, 234), tolerance 14.
- **Painted out (`TITLES` in `m.py`):** the intro text block (20,60,212,178) and the exploded labels.
- **Masks** are `cls()` in `m.py`, the same classes as 042 with one extra shadow rule. HSV, h in degrees, assigned in
  this order:
  - **X, cast shadow:** (s < 0.07, v ≥ 0.78), or (s < 0.08, v ≥ 0.70, B ≥ R − 3), or (h 200–245, s < 0.14, v ≥ 0.70).
    The third rule is new: the lavender ground shadow left of every side view is darker here (`#B7BDC9`).
  - **G, green:** h 50–180, s ≥ 0.25, v ≥ 0.10.
  - **S, sand:** h 30–52, s 0.22–0.47, v ≥ 0.80.
  - **T, trunk:** h < 45, s ≥ 0.35, v ≥ 0.15.
  - **R, rock:** s < 0.30, v 0.25–0.95.
  - **O, other:** everything else.
  - Bounding boxes ignore columns with fewer than 6 silhouette pixels, which drops the grey contact shadows of the
    plants on the sand.
- **Cells** (inset from the borders): f34 (20,60,445,470); r34 (445,60,785,470); front (22,545,271,815); side
  (276,545,512,815); rear (517,545,758,815); top (763,568,1002,838); exploded (22,888,512,1478); close-up 1, the
  joining surface (533,896,809,1075); close-up 2, the tier detail (533,1089,809,1251); close-up 3, the underside
  (533,1266,809,1465).
- **Swatch inner boxes** are 33 × 22 px at x 808–841, y 85 / 119 / 155 / 189 / 225 / 260 (`m.SW`).

**Scratch study material** (no Blender) is in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m045_study\`.
Run it with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14, Pillow, numpy).
- **Helpers:** `m.py` (masks, boxes, `silhouette()`) and `zoom.py` (crop with a 10-px sheet grid:
  `zoom.py x0 y0 x1 y1 scale out.png [grid]`).
- **Measurements:**
  - `measure2.py`: bbox, W : H, shares, top profile, width per height, fifths.
  - `tiers.py`: hems, waists, trunk widths.
  - `low.py`: lowest canopy pixel and trunk foot.
  - `base.py`: sand, rock and plant extents.
  - `topang.py`: plan star points.
  - `parts.py`: exploded components.
  - `trunk.py`: exploded trunk profile.
- **Colour:** `sw.py` (swatches) and `samp.py` (every region per view, halves and tiers).
- **Zooms:** `z_f34.png`, `z_f34c.png`, `z_f34b.png`, `z_r34.png`, `z_r34b.png`, `z_ortho.png`, `z_front.png`,
  `z_frontc.png`, `z_top.png`, `z_top4.png`, `z_expl.png`, `z_expl_top.png`, `z_expl_lower.png`,
  `z_expl_ground.png`, `z_cu.png`, `z_cu1.png`, `z_cu2.png` and `z_cu3.png`. Mask previews are `cls_*.png`.
- **On our renders:** `measure_render.py <render.png> [paper_hex] [--flip]` uses these masks. Self-test on the sheet's
  own cells: front W : H 0.736, G 80.5 / T 10.1 / R 5.4 / S 2.0; f34 W : H 0.735, G 77.2 / T 10.8 / R 7.7 / S 3.1.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** a full asset: a standalone young pine with its own ground patch. The hero budget is 4000 tris and
  each part must stay under 1000. The plan in §4.3 lands at about 2400–2700.
- **Overall read (check this first).** A **small, chunky, three-tier pine on a tall visible trunk**:
  - **The canopy:**
    - a pointed four-ridge **crown cone** with two short rows of flaps at its foot;
    - a **middle tier**;
    - a widest **lower tier**.
    Each tier is a ring of **broad, thick, paddle-shaped leaf plates**. Each plate has a **constant thickness**, a midrib
    fold and a **blunt chisel tip**. The plates are two rows deep, lap over the tier below and leave a dark crease under
    each hem.
  - **The trunk:** under the canopy, a **smooth, tapered, eight-sided orange-brown trunk** shows for the lower ~27 % of
    the height. It **flares into six short, blunt root flares**.
  - **The ground:** the roots sit on a **thin pale sand patch**, dressed with **four pale grey faceted rocks** (one
    medium, three small) and **rosettes of broad, pointed-oval ground plants** (lime outside, green inside).
  - It must read as **three distinct tiers on a visible trunk**, not as a smooth cone or a stack of flat rings. The
    outline steps in at two waists, and every tier edge is a row of separate broad, blunt plate tips.
  - Hero shares (f34): G 77.2 %, T 10.8 %, R 7.7 %, S 3.1 %.
- **Focal silhouettes, in order:**
  1. The stepped spire outline: the apex, then the crown hem (0.48 of the canopy width), the first waist (0.29), the
     middle hem (0.81), the second waist (0.49), and the lower hem (1.0).
  2. The ragged hem of broad blunt plate tips on each tier, the front plate of each tier hanging lowest.
  3. The tapered trunk and its root flare under the lower tier, the orange lit side against the dark brown shade side.
  4. The base: two rocks in front, big plant rosettes left and right, the sand patch.
- **Target size: 10.0 tall (apex). Canopy tips at r 3.5 (silhouette 6.8–7.2 across). Trunk Ø 1.25 under the lower tier,
  2.1 at the flare. Ground patch about 7.8 × 6.8** (decision §8.1). Tolerances: height ±0.2; canopy silhouette W
  7.0 ± 0.3.
  - **How it was derived.** Five side views agree on the proportions (`tiers.py`, `low.py`). Fractions are of the full
    silhouette height H, from the patch's front edge to the apex:

    | Feature | f34 | r34 | front | side | rear | adopted (z, studs) |
    | --- | --- | --- | --- | --- | --- | --- |
    | Crown hem h / width of canopy | .760 / .50 | .730 / .43 | .749 / .48 | .746 / .48 | .746 / .45 | z 7.45, tips r 1.75 |
    | Waist crown / middle h / width | .731 / .33 | .720 / .34 | .722 / .29 | .723 / .28 | .727 / .29 | z 7.25, visible r 1.0 |
    | Middle hem h / width | .577 / .81 | .557 / .77 | .529 / .81 | .542 / .77 | .531 / .81 | z 5.35, tips r 2.8 |
    | Waist middle / lower h / width | .526 / .50 | .512 / .55 | .486 / .49 | .492 / .46 | .492 / .50 | z 4.9, visible r 1.75 |
    | Lower hem h / width | .379 / 1.0 | .370 / 1.0 | .309 / 1.0 | .304 / 1.0 | .310 / 1.0 | z 3.1, tips r 3.5 |
    | Lowest canopy pixel near the axis (front plate tip) h | .282 | .290 | .274 | .265 | .269 | z 2.7 |
    | Canopy W / H | .651 | .618 | .714 | .700 | .708 | 7.0 / 10 = .70 |

    The front cell is near level (e ≈ 5°, §3.1). Its scale is 25.7 px/stud for 10.0 (H 257 px), and its readings are
    adopted directly. The f34 (e ≈ 16°) puts the lower hem higher on screen, because the patch's front edge drops with
    elevation, and it draws the canopy about 7 % narrower (§3.3).
  - **Why 10.** The sapling must be clearly the smallest pine in the kit. 042 Young Fir is 16 on almost the same
    silhouette, and 047 Old Pine and 049 Classic Pine are larger. W04's old `Sapling` is only 5.7 tall, which is the
    character's height; at that size the sheet's rocks (0.11 H) and plants (0.14 H) would shrink to 0.6-stud pebbles and
    0.8-stud tufts. At 10:
    - the rocks are 0.75–1.3 tall, about knee height;
    - the plants are 1.1–1.5 tall;
    - the trunk is about an arm's width.
  - **Against the character (5.5):** the tree is 1.8 C tall. The lowest plate tips hang at 2.5–2.7, about hip height, so
    a character can't walk under the canopy. The middle hem (5.35) is at the character's head.
- **Build frame:** front −Y, +X right, ground z 0 = the sand patch's flat underside. The tree axis is at (0, 0). Origin
  = bbox bottom centre; the patch's lobes are offset ≤ 0.3, so the origin lies within 0.3 of the axis (record it).

### 1.2 Measured views (`measure2.py`)

| View (box) | Silhouette bbox (px) | W : H | G | T | S | R | O |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (20,60,445,470) | 130–413 × 79–469 (284 × 391) | **0.726** | 77.2 % | 10.8 | 3.1 | 7.7 | 1.2 |
| Rear three-quarter (445,60,785,470) | 491–761 × 69–469 (271 × 401) | 0.676 | 77.0 | 12.9 | 3.4 | 5.5 | 1.3 |
| Front (22,545,271,815) | 57–244 × 554–813 (188 × 260) | 0.723 | 80.4 | 10.1 | 2.0 | 5.4 | 2.0 |
| Side (276,545,512,815) | 304–486 × 554–814 (183 × 261) | 0.701 | 82.1 | 11.0 | 1.2 | 3.6 | 2.1 |
| Rear (517,545,758,815) | 544–732 × 554–814 (189 × 261) | 0.724 | 78.1 | 11.3 | 1.7 | 6.6 | 2.4 |
| Top (763,568,1002,838) | 814–969 × 619–776 (156 × 158) | 0.987 (W : D) | 85.1 | 0.5 | 0.1 | 13.3 | 0.9 |

- Shares are of the whole silhouette (O included, X excluded).
- **Verifier tolerance:** G ±5, T ±3, R ±3, S ±2 points; W : H ±0.05; positions ±0.04 of W / H unless stated.
- The f34 bbox is set left and right by the sand patch (x 137–414, 8.1 studs on screen). The canopy alone is 254 px.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.1 f):

| f | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .14 | .41 | .63 | .78 | .89 | 1.0 | .90 | .79 | .62 | .43 | .07 |
| r34 | .38 | .45 | .65 | .81 | .91 | 1.0 | .90 | .81 | .61 | .38 | .06 |
| Front | .31 | .54 | .61 | .79 | .91 | 1.0 | .90 | .79 | .60 | .53 | .04 |
| Side | .31 | .37 | .60 | .80 | .90 | 1.0 | .91 | .79 | .60 | .38 | .32 |
| Rear | .32 | .54 | .62 | .79 | .90 | 1.0 | .90 | .79 | .60 | .53 | .30 |

**Width per height** (silhouette width at h .0 → 1.0 as a fraction of W):

```
f34    .53 .87 .62 .73 .87 .54 .67 .38 .37 .19 .02
r34    .46 .91 .63 .61 .85 .55 .61 .38 .43 .20 .01
front  .50 .78 .20 .98 .73 .63 .62 .36 .38 .20 .02
side   .49 .70 .20 1.0 .74 .67 .62 .36 .38 .20 .03
rear   .48 .83 .20 .98 .74 .63 .62 .37 .39 .20 .02
```

- h .1 is the base dressing (the plant rosettes are as wide as the canopy).
- h .2 is the bare trunk. In the front cell that is 0.20 of W = 36 px = Ø 1.4 at z 2.0.
- h .3–.4 is the lower tier, h .5–.6 the middle hem and waist, and h .7–1.0 the crown.

**Height fifths** (bottom → top, % of each class's pixels):
- f34: G 15.5 / 21.7 / **31.8** / 21.9 / 9.1; T 61.4 / 38.6 / 0 / 0 / 0.
- Front: G 13.7 / 26.3 / 30.4 / 20.6 / 8.9; T 64 / 36.
- No bark shows above 0.4 H. The bottom fifth's green is the ground plants.

**Trunk widths** (`tiers.py`, front cell, as a fraction of the canopy W 185 px, with studs at 7.0 canopy):

| h | .25 | .22 | .20 | .15 | .12 | .10 | .07 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| front | .178 (1.25) | .189 | .195 (1.37) | .227 (1.59) | .254 | .303 (2.12) | .395 (2.77, roots) |
| side | .176 | .181 | .192 | .214 | .247 | .286 | .346 |
| rear | .185 | .190 | .201 | .228 | .261 | .315 | .397 |
| f34 | .213 | .228 | .240 | .307 | .311 | .315 | roots |

**Plan (top cell, `topang.py`, `z_top4.png`).**
- The canopy is about 150 px across, against 185 in the front cell (§3.3).
- **About 8 big outer points** (r 70–79 px from the centre at (885, 697)), with the second row's points between them.
- In the middle there is a **4-point crown star** (4 lit / shaded ridge pairs) with shorter ridges between.
- **Rocks and plants show beyond the canopy edge from above** (unlike 042):
  - a big pale rock at the back-right (dx +50, dy −40 px from the centre);
  - a small rock at the far left (dx −60, dy −20);
  - a plant rosette at the back-left (dx −35, dy −60);
  - a plant rosette at the right (dx +70, dy −15).
  - Up is the back (+Y). This orientation is checked against the rear cell's big rock at screen left (+X).
- Top shares: G 85.1 %, R 13.3 %.

### 1.3 Silhouette and composition per view

**Front three-quarter (`z_f34.png`, `z_f34c.png`, `z_f34b.png`) — governs.** An elevated view (e ≈ 16°, §3.1). The
canopy's front ridge faces the camera almost head-on, so the "three quarter" turn is small (we use az −15, §3.1).
- **Crown** (apex x 273, y 79): a straight-sided pointed cone. Its front ridge splits it into a lit right half and a dark
  left half. A short upper row of flaps (tips at y 140–150 at the sides) and the hem row (tips at y 165–185, x 212–338).
- **Middle tier** (y 184–264): broad plates in two staggered rows; the front plate's blunt tip at y ~262; side tips at
  x 165 and 371 (y 244).
- **Lower tier** (y 264–360): broad plates in two rows; side tips at x 144 and 397 (y 321); front plate tip at y 359.
  Each plate is a broad paddle 2.2–2.7 studs wide on screen, with a midrib (lit half and shaded half) and a chisel
  tip.
- **Trunk** (from y 336 between the tips down to the ground): Ø 54 px (1.55) at y 371, 61 at y 391, 78 at y 410 (z ≈
  1.3), then the flare. Bark: broad vertical facets, the lit right side orange (`#B06325` median, v > .7 `#E88733`), the
  left side dark brown (`#744323`).
- **Roots:** three show in front: left (to x 200, y 440), front centre (under the rocks), and a long right root
  sweeping to the lower right (to x 345, y 450). They are angular, four-sided, and taper to a blunt cut end.
- **Base dressing:**
  - **P1:** a big plant rosette at the left (x 150–245, top y 380; 10–12 broad leaves).
  - **P2:** a big rosette at the right (x 315–400, top y 385).
  - **R1:** a medium-small pale rock in front-left (x 200–265, top y 422).
  - **R2:** a small rock in front-right (x 280–315, top y 432).
  - **Sprigs:** a lime sprig between the rocks (x 255–285) and one at the right (x 325–345).
  - The sand patch spans x 137–414 (8.1 studs on screen, the widest thing in the cell).

**Rear three-quarter (`z_r34.png`, `z_r34b.png`).** The same tree from behind (az ≈ 165, e ≈ 16°). It has the same tiers
(h .730 / .557 / .370), the same lit-right light, and the same trunk with a long root to the lower right. One pale rock
sits left of the trunk (x 555–615, top y 418; the rear cell's big rock), with rosettes left (x 506–580) and right (x
660–745) and a lime sprig in front (x 600–640).

**Front, side and rear cells (`z_ortho.png`, `z_front.png`, `z_frontc.png`).** Near-level views (e ≈ 5°), all at one
scale (H 260 px); the tier rows sit at the same heights in all three (§1.1). Each tier shows one plate aimed at the
camera on the axis (the lit / dark split runs down its midrib).
- **Front:** a rock left of the axis (x 115–150, top y 775), a small rock right (x 167–177), and rosettes left (x 74–135)
  and right (x 165–229).
- **Rear:** a bigger rock at screen left (x 553–590, top y 765, i.e. world +X behind) and a small one right of the
  axis.
- **Side:** one small rock in front of the trunk.
- Judge the dressing for content (§3.5).

**Top (`z_top.png`, `z_top4.png`).** §1.2. The plates read as broad pointed kites with a midrib (one lit half, one
shaded half).

**Close-up 1, trunk to foliage joining surface (`z_cu1.png`).** The lower tier is seen from below and the front.
- **In the tier:** in the middle of its underside there is a **flat, lighter green ring** (the core's underside,
  `#547727`). In that ring is a **recess drawn as a diamond** (a square turned 45°, 80 × 40 px on screen), dark brown
  inside (`#3B2117`).
- **The trunk:** a dashed arrow points down to its **top**, a faceted tapered frustum with the lit face orange and the
  shaded face brown. It is the "matching peg": the trunk's top end itself, with no separate stub.

**Close-up 2, foliage tier detail (`z_cu2.png`).** Three lower-tier plates seen from the side.
- **Shape:** each plate is a **flat slab of constant thickness**, with **straight side walls** and a top face folded
  once along the midrib. The plate is a broad paddle that ends in a **blunt chisel tip** (two angled edges and a short
  flat end).
- **Thickness:** the side wall is about 0.09–0.10 of the plate's width.
- **Colour:** the top face's long edge carries a thin lime highlight line (light catching the edge, §3.9). The side
  walls are dark green.

**Close-up 3, underside view (assembled) (`z_cu3.png`).** The tree from below.
- **Trunk bottom:** a **flat octagonal face** (Ø ≈ 0.4 of the root span, `#6D462D`).
- **Root flares: six** radiate from it. Each is a long four-sided block with a **blunt cut end**, one or two of them
  longer (lower left, bottom).
- **Around them:** three rocks (pale grey) and five plant rosettes. The lower tier's plates show at the rim.
- **No sand patch is drawn from below** (§3.6).

### 1.4 Parts (Exploded Construction, `z_expl*.png`, `parts.py`, `trunk.py`)

The exploded is an elevated view from the front (e ≈ 20°). Its scale differs from part to part:
- **the tiers and trunk** are drawn at about 31.6 px/stud if the lower tier is 7.0 wide;
- **the ground pieces** are drawn about 1.5× larger than that.

**The hero governs every size**; the parts give shapes and counts.

| Part | Box (px) | Size px | Screen W : H | Notes |
| --- | --- | --- | --- | --- |
| Top Foliage Tier | (265,888,381,972) | 117 × 85 | 1.38 | a 4-ridge cone; widest at h .15 (116 px at y 958); flaps at two heights (tips y ~922 and 958–970); a recess underneath (hidden) |
| Lower Foliage Tier | (213,991,433,1098) | 221 × 108 | 2.05 | a broad frustum with a **flat top Ø 46–60 px (0.21–0.27 of its width)**; 7 plate tips visible in front in two rows; plates run from the top rim down to the tips |
| Trunk | (272,1114,377,1236) | 106 × 123 | 0.86 | 8-sided, **flat top Ø 36 px (0.16 of the lower tier)**; Ø 40 / 45 / 52 / 64 / 90 px at y 1142 / 1160 / 1178 / 1190 / 1208 (straight taper, then a flare from y ~1185); **4 root flares in front** spanning 103 px (2.9 × the top Ø); two small dark knots at mid-height (y ~1150) |
| Ground Foliage | 5 rosettes: 113 × 69, 82 × 53, 71 × 47, 92 × 62, 37 × 17 (partial); 3 sprigs on sand puddles | | 1.5–1.6 | broad pointed-oval leaves, 8–12 per rosette (5–6 per sprig), folded on a midrib, 45–75° from horizontal, arching out; lime outer leaves, green inner |
| Rock (Medium) | (210,1307,298,1372) | 89 × 66 | 1.35 | a chunky faceted block: broad flat base, a sloping 4–5-corner top, 12–16 broad facets |
| Rock (Small) | (258,1386,330,1434) and one at (≈ 400–476, 1365–1431) | 73 × 49 / ~70 × 60 | 1.49 / 1.2 | the same build, rounder |

- **Green split:** the exploded G median is `#578C33`; lit (v > .7) `#A8C634`.
- **Plant hue split:** lime (h < 80) 39 %, green (80–110) 41 %, dark (≥ 110) 20 %.

#### Top (crown) tier — exploded, hero, top
- **Shape:** a straight-sided **4-ridge cone**: main ridges at 270 / 0 / 90 / 180°, and minor ridges between them at
  0.75 of the main radius, each with two broad facets.
- **Flaps:** a short **upper row of 4 plates** at the minor ridges, and a **hem row of 8 plates** (4 long under the main
  ridges, 4 shorter), with blunt tips drooping. A recess sits under the core.
- **Hero size:** apex 10.0; cone rim r 1.0 at z 8.5. Upper-row tips r 1.25 at z 8.1. Hem tips r 1.75 (long) / 1.5
  (short) at z 7.3–7.5, the front one at 7.2. Recess mouth z 7.315.
- **Part size:** about 3.5 × 3.5 × 2.8 (W : H 1.25; exploded 1.38).

#### Middle tier — hero only (the exploded draws no middle tier, §3.2)
- **Shape:** the lower tier's construction at 0.8 of its plan size: a core with a recess and a top peg, and **14 plates
  in two rows of 7**.
- **Hero size:** row A tips r 2.8 at z 5.3, the front plate's tip at 5.05; row B tips r 2.4 at z 5.8. Core cap z 7.3.
  Recess mouth z 5.715.
- **Part size:** about 5.6 × 5.6 × 2.6.

#### Lower tier — exploded, close-ups, hero
- **Shape:**
  - **The core:** a broad pleated frustum with a **flat top cap and a short top peg**, and a **recess** in its underside
    surrounded by a flat ring.
  - **The plates: 14 in two rows of 7**, the widest plates of the tree, with their tips drooping clearly below the
    notches.
- **Hero size:** row A tips r 3.5 at z 3.0–3.1, the front plate's tip at 2.7; row B tips r 3.0 at z 3.7. Cap z 5.7, peg
  top z 6.1. Recess mouth z 3.8, ceiling z 4.415.
- **Part size:** about 7.0 × 7.0 × 3.4 (W : H 2.06; exploded 2.05).

#### Trunk — exploded, close-ups 1 and 3, hero
- **Shape:** an **8-sided tapered trunk** with smooth broad facets and no planks or slits; **two small knots**. It runs
  near-straight above z 1.5, then **flares into six root flares**. The flat top is the peg, and the flat octagonal
  bottom shows from below.
- **Hero size:** Ø 1.1 at the top (z 4.4); 1.2 at z 3.5; 1.25 at z 2.5; 1.37 at z 2.0; 1.6 at z 1.5; 2.1 at z 1.0.
  Bottom octagon Ø 2.3 at z 0.04. Roots reach r 1.6–2.5.
- **Part size:** about 4.6 × 4.2 × 4.4.

#### Ground pieces — exploded, close-up 3, hero
- **Patch:** a thin, irregular sand patch (hero only).
- **Rocks:** 1 medium and 3 small (§2.4).
- **Plants:** 4 rosettes of 8–11 broad leaves and 3 sprigs of 5 leaves.

### 1.5 How 045 differs from 042 Young Fir (binding: the verifier checks these)

The two sheets' silhouettes are almost the same:

| | Canopy W / H | Hems h | Hem widths | Trunk shows below h | Shares |
| --- | --- | --- | --- | --- | --- |
| 045 front | .71 | .75 / .53 / .31 | .48 / .81 / 1.0 | .27 | |
| 042 front | .70 | .73 / .57 / .34 | .50 / .73 / 1.0 | .26 | |
| 045 f34 | | | | | G 77 / T 11 |
| 042 f34 | | | | | G 73 / T 13 |

So the difference has to come from the following, and the main session should keep these when it rules on §8:

| | 042 Young Fir (`TieredFir`) | 045 Pine Sapling |
| --- | --- | --- |
| Size | 16 tall, canopy 12, trunk Ø 2.0 | **10 tall, canopy 7.0, trunk Ø 1.1–1.25**; tips at hip height, not head height |
| Foliage elements | thin kites with a raised midrib and a keel, length : width ≈ 2.2 | **thick constant-thickness paddle slabs (0.2 thick), straight side walls, a midrib fold, a blunt chisel tip; length : width ≈ 1.5** (broader) |
| Tier plates | 8 / 12 / 16, the middle ring 0.73 of the lower | **12 (4 upper + 8 hem) / 14 / 14**; the middle is the lower tier's construction at 0.8, so its ring is 0.81 of the lower (§1.1) |
| Stacking | flat caps and octagonal hubs (hub on cap) | **peg and recess**: the trunk's top end enters the lower tier's recess, and each tier's top peg enters the recess of the tier above |
| Exploded parts | 3 tiers + trunk + root base | **2 foliage tiers (top, lower) + trunk + ground foliage + rock medium + rock small**; modular reuse is the point |
| Trunk | octagonal, **planked** (16 facets), 3 slits, an inner-ring top, **six long kinked roots** (r 2.8–4.2 = 1.4–2.1 × trunk Ø) | **smooth 8-sided tapered stump**, 2 knots, **six short blunt root flares** (r 1.6–2.5); the trunk widens 1.9× from top to flare (042: 1.6×) |
| Ground plants | upright lanceolate leaves, 5–10 per clump | **broad pointed-oval leaves in rosettes**, 8–11 per rosette, lime outside / green inside |
| Rocks | 5 warm beige rocks + 3 pebbles | **4 paler, more neutral grey rocks** (lit `#CEC0B4`–`#D1C3B4`), 1 medium + 3 small, no pebbles; rocks show beyond the canopy from above |
| Bark colour | lit `#BE6F30` | **more saturated orange: lit half `#B06325`, v > .7 `#E48230`–`#E88733`** |
| Ground patch | 13 × 11 | 7.8 × 6.8; the "ground foliage" swatch is tan |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, tree axis at (0, 0)).

### 2.1 Stack (binding contact chain, bottom up; every seat gap is VEG_GAP = 0.015)

| Piece | Bottom z | Top z | Sits on | Notes |
| --- | --- | --- | --- | --- |
| Sand patch | 0 | 0.12 (crest), edge bevelled to 0.03 | ground | flat underside |
| Trunk + roots (one closed shell) | 0.04 (sunk 0.08 into the patch) | **4.40 flat top (the peg)** | patch | root ends sunk 0.04 into the patch top |
| Lower tier core (one closed shell: recess, ring, frustum, cap, peg) | recess mouth 3.80 | cap 5.70, **peg top 6.10** | trunk top (recess ceiling 4.415) | the recess walls clear the trunk by 0.03–0.06 on every side |
| Lower tier plates ×14 | — | — | the core (row A), row A or the core (row B) | ≤ 0.03 contact, chained to the core |
| Middle tier core | recess mouth **5.715** (0.015 over the lower cap) | cap 7.30, peg top 7.65 | lower tier peg (ceiling 6.115) and cap | |
| Middle plates ×14 | — | — | core / row A | |
| Crown core (cone + recess) | recess mouth **7.315** | **apex 10.0** | middle peg (ceiling 7.665) and cap | |
| Crown plates ×12 | — | — | the cone | |
| Rocks | sunk 0.08 into the patch | §2.4 | patch | separate closed shells |
| Plant hubs | sunk 0.03 into the patch | | patch | leaves chain to their hub |

- **Peg and recess (the sheet's joint):**
  - The trunk's top 0.6 sits inside the lower tier's recess. The trunk's flat top face is 0.015 below the recess
    ceiling, and the walls are 0.03–0.06 clear.
  - Each tier's peg (an octagonal stub Ø 0.9 on the lower tier, 0.75 on the middle) sits inside the recess of the tier
    above in the same way.
  - The upper tier's recess-mouth ring also rests 0.015 above the cap below. Each tier therefore touches the piece
    below at two places, and none hovers.
  - Read the gaps back through the MCP (BVH nearest distance per shell, 0.005–0.03).
- **No coincident faces:** seats 0.015 apart, never coplanar, never more than 0.03.
- **The recess shape** is 4-sided as drawn (a square turned 45° to the trunk's octagon, side = the trunk top Ø + 0.1,
  0.6 deep) (§3.4).

### 2.2 Tiers

Plan radii r are from the axis, heights z. Angles are plan azimuths: 0 = +X, counter-clockwise, −Y = 270°.

| Tier | Core: cap r @ z → widest r @ z → underside ring | Row A plates (count, azimuths, root r @ z → tip r @ z, length, max width) | Row B plates | Peg / recess |
| --- | --- | --- | --- | --- |
| Crown | apex 10.0 → rim r 1.0 @ 8.5 (4 main ridges at 270 / 0 / 90 / 180°, 4 minor ridges at 0.75 r); underside from the rim to the recess mouth at z 7.315 (ring r 0.55) | **8 hem plates**: 4 long at 270 / 0 / 90 / 180°, root r 0.5 @ 8.8 → tip r 1.75 @ 7.4 (front one droops to 7.2); 4 short at 315 / 45 / 135 / 225°, tip r 1.5 @ 7.55; length 1.9 / 1.6; width 1.3 / 1.1 | **4 upper plates** at 315 / 45 / 135 / 225°, root r 0.35 @ 9.1 → tip r 1.25 @ 8.1; length 1.3; width 0.9 | recess Ø 0.85 (square), 0.35 deep; no peg |
| Middle | cap r 0.55 @ 7.30; widest r 0.95 @ 6.2; ring r 0.95 @ 5.715 | **7** at 270 + k·51.43°; root r 0.55 @ 7.0 → tip r 2.8 @ 5.3 (front-facing droop to 5.05); length 2.8; width 1.9 | **7** at 295.7 + k·51.43°; root r 0.5 @ 7.2 → tip r 2.4 @ 5.8; length 2.4; width 1.7 | peg Ø 0.75 to 7.65; recess Ø 1.0 (square), 0.4 deep |
| Lower | cap r 0.7 @ 5.70; widest r 1.15 @ 4.4; ring r 1.0 @ 3.80 | **7** at 270 + k·51.43°; root r 0.7 @ 5.3 → tip r 3.5 @ 3.05 (front-facing droop to 2.7); length 3.5; width 2.3 | **7** at 295.7 + k·51.43°; root r 0.6 @ 5.5 → tip r 3.0 @ 3.7; length 3.0; width 2.0 | peg Ø 0.9 to 6.10; recess Ø 1.2 (square), 0.6 deep |

- **One row-A plate points straight at the front camera on every tier (270°), and the crown's main ridge points there
  too**, as the front cell and the top view show. The f34 (az −15) then sees the tiers slightly turned.
- **Jitter, not a pattern:** tip radius ±5 %, tip height ±0.1, azimuth ±4°, width ±6 %, per-plate roll ±5°. Never make
  two neighbours equal.
- **Row B** lies **on** row A: seat it by ray cast down onto row A and the core (as `m037._touch_up` does), gap 0.015.
  Its tips sit 0.5–0.7 above row A's.
- **Waists (visible checks):**
  - under the crown hem, the middle tier shows at r ≈ 1.0, z ≈ 7.25;
  - under the middle hem, the lower tier shows at r ≈ 1.75, z ≈ 4.9;
  - a dark crease band runs under each hem (geometry shadow, not paint).
- **Pitch:** the visible outline from waist to hem runs at 45–48° (middle and lower) and 56° (crown). The plates leave
  the core at 30–35° below horizontal and bend down a further 12–18° at 0.6 of their length (the droop). The outline is
  the row B tops over the row A tips.

### 2.3 Plate and core shapes

- **Plate (one closed slab, about 28–32 tris).** Every plate in the model comes from `plate()`.
  - **Outline in plan:** a broad paddle: root width 0.45 W, widest W at 0.45 L, still 0.85 W at 0.78 L, then a **chisel
    tip**: two edges at about 40° to the axis meeting a **short flat end 0.18 W wide**. It is not a needle, a triangle
    or a narrow kite (039 was rejected for spiky, edge-on leaves).
  - **Top face:** folded once along the midrib (ridge raised 0.07 W above the edges), so there are two broad facets,
    which are the sheet's lit and shaded halves.
  - **Bottom face:** flat and parallel to the top's mean plane.
  - **Thickness 0.20 everywhere**, the same on every tier ("consistent thickness"): straight side walls round the whole
    outline, including the chisel end.
  - **The droop:** bend the outer 40 % down 12–18° at 0.6 L.
  - **Faces:** top 8–9, bottom 6–7, walls 14 (7 outline edges × 2).
- **Core (one closed shell with its recess and peg, under 70 tris):**
  - an 8-corner pleated frustum, with the corners at the row-A azimuths pushed out 0.1 and the corners between pulled in
    0.1;
  - a flat top cap carrying the octagonal peg;
  - an underside that slopes from the widest ring down and in to a **flat ring** (the close-up's lighter joining
    surface);
  - a **square recess** turned 45° through the flat ring.
  - The recess is a real pocket, and the shell stays closed: its walls and ceiling are faces of the same shell.
- **Crown core:** the 4 + 4-ridge star cone from the apex to the rim at z 8.5 (16 facets), then the underside to the
  recess. The plates tuck under the rim.

### 2.4 Trunk, roots, base

Plan positions come from the front and rear cells and the top cell (y up = +Y), checked against the f34 / r34 (§3.5).

| Piece | Position (X, Y) / azimuth | Size | Notes / evidence |
| --- | --- | --- | --- |
| Trunk body | axis (0, 0) | octagon, a face (not a corner) toward −Y; Ø 2.3 @ 0.04, 2.1 @ 1.0, 1.6 @ 1.5, 1.37 @ 2.0, 1.25 @ 2.5, 1.2 @ 3.5, 1.1 @ 4.4; rings at those heights | front cell widths (§1.2), exploded taper |
| Bark facets | | each side one broad face, vertices jittered ±0.04 (no planks) | exploded, close-up 1 |
| Knots | 2: front-right at z 2.9, left-back at z 2.3 | 0.25 × 0.35, recessed 0.05 (a pulled-in quad) | exploded y ~1150 |
| Top face | z 4.4 | flat octagon (the peg's top) | close-up 1; hidden in the hero |
| Bottom face | z 0.04 | flat octagon Ø 2.3, inside the patch | close-up 3 (underside) |
| Root RFR (front-right, long) | azimuth 315°, reach r 2.5 | 0.75 wide × 0.8 tall at the trunk, 2 segments, tip 0.35 × 0.3 with a flat cut end | f34 / r34 long right root |
| Root RF (front) | 255°, r 1.6 | 0.7 × 0.7, 1 segment | f34 front root under the rocks |
| Root RL (left) | 200°, r 1.9 | 0.7 × 0.75, 2 segments | f34 x 200 |
| Root RBL (back-left) | 145°, r 1.8 | 0.65 × 0.7 | underside, rear |
| Root RB (back) | 85°, r 2.0 | 0.7 × 0.7, 2 segments | underside: the long lower one |
| Root RR (right) | 355°, r 1.8 | 0.65 × 0.7 | underside, rear |
| Roots, all | start on the trunk at z 1.2–1.6; 4-sided section with a top ridge; flattened on the sand; a **blunt flat cut end** (not a point); end sunk 0.04 | | "simple root flares"; close-up 3 shows the cut ends |
| Sand patch | irregular lobed outline, 12 points, r 3.3–4.1 (mean 3.65), longest toward 0° / 180° | 7.8 × 6.8, crest 0.12, bevel 0.35 wide to 0.03 | f34 8.1 on screen, front 7.1, side 6.7, rear 7.3 |
| Rock RM (medium) | (2.2, 1.5) | 1.9 × 1.6 × 1.3 tall | top cell back-right; rear cell's big rock (screen left); r34 rock |
| Rock RS1 | (−1.3, −2.0) | 1.5 × 1.2 × 1.0 | f34 R1 (x 200–265); front cell rock left of the axis |
| Rock RS2 | (0.8, −2.2) | 1.1 × 0.95 × 0.75 | f34 R2 (x 280–315); front cell's small rock right of the axis |
| Rock RS3 | (−2.7, 0.9) | 1.0 × 0.9 × 0.7 | top cell's far-left rock, partly behind P1 |
| Rosette P1 (left) | (−2.5, −0.5) | Ø 2.4, 1.5 tall, 11 leaves | f34 left (x 150–245); front x 74–135 |
| Rosette P2 (right) | (2.5, −0.7) | Ø 2.4, 1.5 tall, 11 leaves | f34 right (x 315–400); front x 165–229 |
| Rosette P3 (back-left) | (−1.4, 2.7) | Ø 1.8, 1.2 tall, 8 leaves | top cell back-left |
| Rosette P4 (right-back) | (3.1, 0.6) | Ø 1.6, 1.1 tall, 8 leaves | top cell right, beside RM |
| Sprigs S1, S2, S3 | (0.0, −2.6), (1.8, −2.1), (−2.0, −2.3) | Ø 0.7–0.9, 0.6–0.8 tall, 5 leaves, lime | f34 sprigs at x 255–285 and 325–345; r34 front sprig |

- **Keep clear:** no rock or rosette may overlap a root's top ridge or the trunk by more than 0.05 (contact is allowed:
  RS1 leans on RF, RM touches RR's end). The dressing stays at least 0.25 inside the patch outline.
- **Plant leaves:** each a **broad pointed oval** (length : width ≈ 2.2), widest at 0.4 L, a rounded-pointed tip, folded
  on the midrib (V section, fold 25–35°), pitched 45–75° from horizontal and arching outward. Outer leaves are longer and
  lower; inner ones shorter and more upright. Each leaf is a thin closed shell (two folded sheets 0.04 apart, about 12
  tris), rooted inside a small hub pyramid on the sand.

### 2.5 Expected extents and screen checks

- **Extents (build frame):** X about −3.9 … +4.1; Y about −3.4 … +3.4; Z 0 … 10.0. The bbox is about 8.0 × 6.8 × 10.0
  (the patch is the widest thing; canopy tips reach r 3.5 ± 0.18).
- **Checks on the renders** (floor hidden, `measure_render.py`):
  - **f34_sheet (−15, 16)** (probe az 0 / −15 / −30 × e 12 / 16 / 20, keep the best):
    - W : H 0.69–0.77 (sheet 0.726);
    - shares G 77.2 ± 5, T 10.8 ± 3, R 7.7 ± 3, S 3.1 ± 2;
    - top profile within ±0.07 at f .1–.9; width per height within ±0.08 at h .2–.9;
    - hems at h .76 / .58 / .38 ± .03 with widths .50 / .81 / 1.0 ± .05 of the canopy;
    - waists at h .73 / .53 ± .03 with widths .33 / .50 ± .06;
    - G fifths within ±6; no T above 0.4 H.
  - **front_sheet (0, 5), side_sheet (90, 5), rear_sheet (180, 5):**
    - hems at h .75 / .535 / .31 ± .03 with widths .48 / .80 / 1.0 ± .05;
    - waists .725 / .49 ± .03 with widths .29 / .49 ± .06;
    - lowest canopy near the axis h .27 ± .03;
    - canopy W / H 0.68–0.74;
    - trunk width per §1.2 within ±0.03 of W at h .25 / .20 / .15 / .10;
    - shares within G ±6;
    - dressing judged for content only (§3.5).
  - **r34_sheet (165, 16):** loosely: W : H 0.63–0.72 (0.676), hems .73 / .56 / .37 ± .04, G 77 ± 6.
  - **top (0, 89):**
    - W : D 0.95–1.03;
    - about 8 big points with the second row between them, and the 4-point crown star with its ridge at −Y;
    - RM and RS3, the P3 and P4 rosettes and a little sand showing beyond the canopy;
    - G 85 ± 6, R 13 ± 4.

## 3. View conflicts and resolutions

### 3.1 "Three quarter" cells that are near-frontal; camera elevations

- **Evidence.**
  - The f34 and the front cell agree closely: the same front ridge on every tier aimed at the camera, the same lit-right
    split, and the dressing at the same screen offsets (f34 R1 −2.1 … −0.2 studs from the axis; front −1.3 … 0). So the
    f34 is turned at most 10–20°.
  - **Elevation:** the lower tier's front tip lies 9 px below its widest row in the front cell (0.35 stud) and 38 px
    (1.1 stud) in the f34. With the tip about 3.5 in front of the axis, that gives e ≈ 4–6° for the ortho cells and
    ≈ 16° for the f34 / r34.
- **Resolution (decision §8.10).**
  - `f34_sheet (−15, 16)` governs (probe az 0 … −30, e ±4).
  - `r34_sheet (165, 16)`.
  - `front_sheet (0, 5)`, `side_sheet (90, 5)`, `rear_sheet (180, 5)`.
  - The kit `top`.

### 3.2 Two foliage tiers in the exploded vs three in every assembled view and the notes

- **Evidence.** The exploded draws "TOP FOLIAGE TIER" and "LOWER FOLIAGE TIER" only. The front, side, rear, f34 and r34
  all show three hems (§1.1), and the notes say "three foliage tiers". The exploded lower tier (W : H 2.05, a flat top
  0.21–0.27 of its width, two rows of plates) matches the hero's lower tier.
- **Resolution (decision §8.3).**
  - Three tiers, all built by one `tier()` function from the same plate and core.
  - **The middle tier is the lower tier's construction at 0.8 of its plan size**, with its own heights from §2.2: "the
    lower foliage tier, reused". Plate thickness stays 0.20.
  - The modular story is the sheet's: one lower-tier design, used twice.
  - Export a `MiddleTier` part too, so level designers can restack it, and record that the exploded draws only two tiers.
  - **Alternative:** two tiers only, as in the exploded. That loses the hero silhouette and breaks every side view.

### 3.3 Canopy width: f34 / r34 (W / H .65 / .62) vs the ortho cells (.70–.71) vs the top cell (150 px vs 185)

- **Resolution.** Row A tips at r 3.5 (7.0 across). The ortho cells match. The f34 will read about 5–7 % wider than drawn
  (the sheet's f34 is a perspective drawing, a little taller); the top render reads larger than the top cell at the
  front cell's scale. Record both.

### 3.4 The recess: a diamond (square) pocket vs an octagonal trunk

- **Evidence.** Close-up 1 draws a 4-sided recess turned 45° on screen. The trunk is 8-sided (close-up 3's octagonal
  bottom, the exploded's round top).
- **Resolution.**
  - A **square recess** (as drawn) whose side is the trunk top's Ø + 0.1, so the octagonal peg fits with 0.05 clearance
    at the flats.
  - The pocket's ceiling and walls are faces of the core shell.
  - The interior takes `m045_bark_deep` (the close-up draws it dark brown, `#3B2117`). That is a position role: the
    pocket faces.
  - It shows in the parts shot and in `join_cu`, and is hidden in the hero.
  - **Alternative:** an octagonal recess that matches the trunk (tidier, less like the sheet).

### 3.5 Base dressing between views

- **Evidence.**
  - The front and f34 agree: rocks front-left and front-right, rosettes left and right.
  - The rear and r34 show a bigger rock at the back-right (+X, +Y).
  - The top shows that rock, a small rock at the far left, and rosettes back-left and right.
  - The exploded has 1 medium + 2–3 small rocks and 5 rosettes + 3 sprigs.
  - Close-up 3 shows 3 rocks and 5 rosettes.
- **Resolution.** The §2.4 plan (4 rocks, 4 rosettes, 3 sprigs) satisfies the f34, front, rear and top. The side cell, the
  exploded and close-up 3 are judged for content.

### 3.6 Close-up 3 (underside) draws no sand patch

- **Resolution.** Keep the thin patch in the hero: every side view draws it. Render `underside_cu` with the patch hidden
  (trunk, roots, rocks, plants and lower tier only) to compare with close-up 3. The kit `underside` keeps the patch.
  Record it. **Alternative:** sand puddles under each item, as the exploded draws, and no continuous patch. That is
  cheaper, but the hero cells all show one patch.

### 3.7 Exploded scale vs the hero

- **Evidence.**
  - Exploded top / lower tier width 0.53 (hero 0.48).
  - Trunk top / lower tier 0.16 (hero 0.16 at z 4.4 ✓).
  - The ground pieces are drawn about 1.5× (medium rock 89 px = 2.8 at the tiers' scale vs 1.9 in the hero).
- **Resolution.** The hero governs every size. The parts are the hero's own pieces, moved to the origin.

### 3.8 The "GROUND FOLIAGE" swatch is tan (`#C29E7E`), not green

- **Resolution.**
  - The swatch is the ground / sand tone: the nearest region on the sheet is the shaded sand.
  - The rendered sand is `#EFD19D`, so the swatch is a darker, redder version of it. Use the swatch as the start for
    `m045_sand_deep` and calibrate to the rendered shade quartile.
  - The ground plants take the foliage swatches' family, calibrated to their own rendered regions (§5.4).

### 3.9 "No texture noise, solid colours" and the lime rim on the plates vs the user's blended-colour rule

- **Resolution.**
  - The user's rule wins, quietly: broad position-based blends, and whole-facet Tint at a low amplitude, never confetti.
  - The thin lime line on each plate's top edge (close-up 2) is light catching the edge, so it **is not painted**: no
    rim key, no colour by facing. If it doesn't show in our render, record it as a known miss.

### 3.10 Branches

- **Resolution.** None: the sheet draws none, and the tiers stack on pegs. The user's tree rule is served by:
  - a detailed trunk (taper, knots, the flare);
  - six root flares of different reach, checked in the f34, the front, side and rear cells, `root_cu` and
    `underside_cu`.

### 3.11 Cast shadow

- **Resolution.** The sheet draws a lavender-grey ground shadow (`#B7BDC9`–`#D7D9DE`) to the left. The masks exclude it
  (X). Render every `*_sheet` view with the studio floor hidden.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its cell

1. **`plate(root, tip, width, thick=0.20, droop, roll)`:** one closed paddle slab (§2.3). Every canopy plate comes from
   it. Check one plate alone against close-up 2 (`plate_cu`, az −60, e 15): a constant-thickness slab, a midrib fold, a
   chisel end.
2. **`core(kind)` and `tier(kind)`:**
   - `kind` is `"crown" | "middle" | "lower"`.
   - `core(kind)` builds one closed core shell: frustum or star cone, flat underside ring, square recess, cap, peg.
   - `tier(kind)` adds the plate shells: row A, then row B seated on it.
   - Parts: `PineSaplingTopTier`, `PineSaplingMiddleTier` and `PineSaplingLowerTier`, each at the origin with its
     recess mouth at z 0 (the drooping tips hang below; record the origin).
   - Compare the top and lower parts with their exploded cells: screen W : H ±0.15, visible tip count, and the flat top
     with its peg on the lower part.
   - Compare the lower tier from below (`join_cu`, e −30) with close-up 1: a flat lighter ring and a dark square recess.
3. **`trunk()` → `PineSaplingTrunk`:**
   - the 8-sided tapered body (rings §2.4), the knots, the flat top and bottom;
   - the six roots: `root(azimuth, reach, w, h, segments)`, 4-sided tapered prisms with a top ridge and a flat cut end,
     their trunk end buried 0.25 in the body.
   - **It is one closed shell.** Either union each root into the body one at a time at the origin
     (`m021._union_fine`, merge 0) and save between unions, or build the body and roots as one explicit mesh, with each
     root's faces rising out of a body facet.
   - Compare with the exploded trunk: top Ø 0.16 of the lower tier's width; root span 2.9× the top Ø; a straight taper,
     then the flare. Compare `underside_cu` with close-up 3.
4. **The ground pieces:**
   - `patch()`: a lobed crest, a bevel ring and a flat underside.
   - `rock(spec)` ×4. These are explicit ring stacks:
     - a broad flat base ring;
     - a widest ring at 0.3 h;
     - a shoulder ring at 0.7 h;
     - a flat, sloping 4–5-corner top.
     That gives 12–16 broad facets and W : H 1.3–1.6, with no `K.hull_rock` jitter balls and no ico-spheres.
   - `rosette(spec)` ×4 and `sprig(spec)` ×3.
   - Parts:
     - `PineSaplingGroundFoliage` = rosette P1 alone;
     - `PineSaplingRockMedium` = RM;
     - `PineSaplingRockSmall` = RS2.
     None of them carries sand.
5. **Hero `PineSapling`** = patch + trunk + lower + middle + crown + rocks + plants, stacked by §2.1. Each tier is moved
   up so its recess ceiling sits VEG_GAP over the peg below. They are joined into one object of closed shells, with no
   booleans between pieces.
6. **Parts shot** (az −15, e 20), laid out like the exploded with gaps of 1.0–1.5:
   - the top tier above the middle;
   - the middle above the lower;
   - the lower above the trunk;
   - the ground pieces below.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a small, chunky, three-tier pine of broad blunt slab plates on a tapered orange trunk with root
   flares, on a sand patch with rocks and rosettes. It must not read as 042 scaled down (§1.5).
2. **f34_sheet** against the hero (§2.5).
3. **front_sheet / side_sheet / rear_sheet, r34_sheet, top** per §2.5.
4. **Close-up renders:**
   - `join_cu` (lower tier part from below, e −30, plus the trunk part under it) against close-up 1;
   - `plate_cu` against close-up 2;
   - `underside_cu` (hero, patch hidden, camera straight up) against close-up 3: an octagonal bottom face, six blunt
     flares, rocks and rosettes round them;
   - `root_cu (−20, 15)` on the trunk foot.
5. **Contact counts** (§6): floating shells 0. Every plate is within 0.03 of its core or a neighbour plate and chained to
   the core. Each seat is 0.005–0.03. Every rock and plant hub is on the patch.
6. **Hero size** per §2.5, plus a **scale shot** beside a 5.5-stud character marker at the patch edge: the lowest tips at
   about hip height, the middle hem at head height.
7. **Kit `underside`:** the plates' undersides, the lower tier's ring over the trunk, the patch's flat bottom.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Lower core (recess, ring, cap, peg) | 1 | 56–72 | 56–72 |
| Lower plates | 14 | 28–32 | 392–448 |
| Middle core | 1 | 56–72 | 56–72 |
| Middle plates | 14 | 28–32 | 392–448 |
| Crown star cone + recess | 1 | 40–56 | 40–56 |
| Crown plates | 12 | 26–30 | 312–360 |
| Trunk body (8 facets × 6 bands, top, bottom, knots) | 1 | 110–130 | 110–130 |
| Roots | 6 | 20–30 | 120–180 |
| Sand patch | 1 | 60–90 | 60–90 |
| Rocks | 4 | 28–56 | 150–190 |
| Plant leaves (rosettes 38 + sprigs 15) | 53 | 12 | 636 |
| Plant hubs | 7 | 6–8 | 42–56 |
| **Hero** | | | **about 2370–2740** (limit 4000) |
| Parts: TopTier / MiddleTier / LowerTier / Trunk / GroundFoliage / RockMedium / RockSmall | | | 350–420 / 450–520 / 450–520 / 230–310 / 140–150 / 40–56 / 28–40 (limit 1000) |

- **Spend headroom on the read, not on density.** If the plates look flat, split the top face's midrib into two
  sections (+4 tris per plate) before adding plates. Stay under 3200: this tree will be placed many times.
- **If the budget gets tight,** cut the leaves first (rosettes of 8 instead of 11), never the plate thickness.

### 4.4 Stages 2 and 3

- One object of closed shells (§6). Zero non-manifold, boundary, wire or loose elements; zero bowties
  (`M.fix_bowties`, especially at plate roots, leaf hubs and the recess corners); no n-gons; normals outward.
- Origin at the bottom centre, transforms applied.
- UV: Smart UV, margin ≥ 0.008, no overlaps.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 33 × 22 box inside each, sd ≤ 2.0)

| Swatch | Box | Hex | HSV | Channel order | Use |
| --- | --- | --- | --- | --- | --- |
| Foliage Dark | (808,85,841,107) | `#35624A` | 148°, 0.46, 0.38 | G > B > R | the shade-side tone; start for `needle_deep` |
| Foliage Mid | (808,119,841,142) | `#639845` | 98°, 0.55, 0.60 | G > R > B | start for `needle` |
| Foliage Light | (808,155,841,177) | `#BAAF39` | 55°, 0.69, 0.73 | R > G > B | the lit tone; start for `needle_light` (yellower than any rendered canopy: lit renders at 73–78°) |
| Trunk | (808,189,841,212) | `#986038` | 25°, 0.63, 0.60 | R > G > B | start for `bark` |
| Rock | (808,225,841,247) | `#BCADA0` | 28°, 0.15, 0.74 | R > G > B | start for `rock` |
| Ground Foliage | (808,260,841,282) | `#C29E7E` | 28°, 0.35, 0.76 | R > G > B | the ground tone: start for `sand_deep` (§3.8) |

### 5.2 Rendered regions (`samp.py`; median / v > .7 median / lit quartile / shade quartile)

| Region | Median | Lit (v > .7) / lit quartile | Shade quartile | Halves (right = lit / left = shade) |
| --- | --- | --- | --- | --- |
| Canopy f34 / r34 / front / side / rear | `#519037` (102°, .62, .56) / `#5A9636` / `#4C8C38` / `#5B9635` / `#519237` | `#A5C935` (76°, .74, .79) / `#AECE35` | `#174D30` | f34 R `#9EC534` (76°, .74, .77) / L `#28723F` (139°, .65, .45); front R `#9BC332` / L `#267342` |
| Crown / middle / lower (f34) | `#5B973C` / `#529134` / `#4F8E38` | `#B0CF35` / `#A4C82F` / `#A1C837` | `#1A5D3F` / `#144B30` / `#164B2F` | right halves `#AACB35` / `#A1C62F` / `#99C336`; left halves `#287445` / `#2A753C` / `#27703F` |
| Plate detail (close-up 2) | `#5B9737` | lit top `#A0C733`; v > .7 `#A4C935` | `#1A472B` | shaded plate top `#599646` |
| Tier underside (close-up 1) | `#2E612D` (119°) | flat joining ring `#547727` | `#1B4929` | recess interior `#3B2117` |
| Trunk f34 / r34 / front / exploded | `#854B24` (24°, .73, .52) / `#824B27` / `#814922` / `#A65E2D` | `#E48230` (28°, .79, .89) / lit quartile `#EC8C36` | `#552F1A` | f34 R `#B06325` (27°, .79, .69) / L `#744323` |
| Trunk bottom (close-up 3) | `#6D462D` (23°, .59, .43) | | | |
| Rock f34 / front / exploded | `#B1ACA7` / `#B3ACA8` / `#B1A99F` | `#CEC0B4` (28°, .13, .81) / `#D1C3B4` / `#D6CBBB`; lit quartile `#DCCBBD`–`#E1D2C1` | `#727376` (blue-grey: light) | |
| Sand f34 / front / exploded | `#EFD19D` (38°, .34, .94) / `#F1D29C` / `#F0D29F` | lit quartile `#F2D4A2` | `#E9CB98` / `#E3C48B` | |
| Plants f34 / front / exploded | `#547E21` (87°, .74, .49) / `#5C831F` / — | `#AFC518` (66°, .88, .77) / `#B8C612` | `#1E4D24` | lime (h < 80) 37–45 % `#91AF18`–`#A2BC19` (70–72°, .86); green (80–110) 31–41 % `#4A7823`–`#507F27` (92°, .70); dark (≥ 110) 20–24 % `#1D4F27` |

### 5.3 How the colour works

- **Plates.** The plates use one mid green that renders lime in light (lit 73–78°) and deep teal-green in shade
  (134–143°). Positional signals on the sheet:
  - the **crown is the lightest tier** (right-half `#AACB35` against the lower `#99C336`);
  - the plate roots and the cores (the recesses between plates) are deeper;
  - the outer part of each plate is a touch lighter.
  The hard lit-right / dark-left split is the light: **never colour by facing**. The undersides keep their plate's
  position colour (the main session's 042 ruling).
- **Bark.** One saturated orange-brown (24–28°, sat 0.70–0.80, **R > G > B**). It is deeper in the knots, in the
  lowest 0.3 of the trunk and roots, and in the recesses; lighter on the trunk's top face and the root ridges' outer
  half. The dark brown left side is the light.
- **Rock.** One pale, nearly neutral warm grey (26–32°, sat 0.10–0.15, R > G > B, never mauve, never blue). The tops
  are a step lighter and the feet a step deeper. The blue-grey shade is the light.
- **Sand.** One pale warm sand (37–39°, sat 0.33–0.36), slightly deeper within 0.35 of the trunk, roots, rocks and hubs,
  and on the bevel.
- **Ground plants.** Three tones chosen **per leaf by position**:
  - outer, taller leaves lime;
  - middle leaves green;
  - innermost and lowest leaves dark.
  The plants stay yellower than the plates (plant lime 66–72° against plate lit 73–78°).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are medians of **unshadowed rendered regions** (the lit half or the v > .7 median), not swatches and
not shade quartiles. `K.sample` kinds: `"green"` for plates and leaves, `"brown"` for bark and sand, `"stone"` for rock,
and `"vivid"` for the lime keys if `"green"` rejects them.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m045_needle` | f34 lit-half canopy `#9EC534` ± 12 (start from the mid swatch `#639845`) | 74–80° lit, G > R > B | every plate by default | rough 0.85, `low_spec=True` |
| `m045_needle_light` | crown right half `#AACB35`; v > .7 `#B0CF35` (start `#BAAF39`) | 70–76°, sat ≥ 0.72 | crown cone 45 %; crown plates 30 %; outer 35 % of every plate's length +20 % | rough 0.85, low spec |
| `m045_needle_deep` | the dark swatch `#35624A` rendered lit ± 12 (it then falls to about the sheet's shade `#28723F`–`#174D30`) | 135–150°, sat 0.45–0.6 | cores 70 % (the flat joining ring 40 %: it reads lighter, `#547727`); the root third of every plate 30 %; lower row A 10 % overall | rough 0.9, low spec |
| `m045_bark` | f34 lit-half trunk `#B06325` ± 12; v > .7 `#E48230`–`#E88733` (start from the swatch `#986038`) | 24–28°, sat 0.72–0.80, **R > G > B** | trunk, roots, default | rough 0.9 |
| `m045_bark_light` | lit quartile `#EC8C36`–`#F79A41` | 26–30° | the trunk's top face 70 %; root top ridges on their outer half 20 % | rough 0.9 |
| `m045_bark_deep` | close-up 3 bottom `#6D462D`; f34 left `#744323` rendered lit (start) | 22–25°, sat 0.6–0.7 | knots 100 % (hard); the lowest 0.3 of trunk and roots 25 %; the bottom face 70 %; recess pockets 100 % | rough 0.95 |
| `m045_rock` | lit (v > .7) `#CEC0B4`–`#D1C3B4` ± 10 (swatch `#BCADA0`) | 26–32°, 0.10–0.15, R > G > B, R − B ≥ 20 | rocks | rough 0.85, metal 0 |
| `m045_rock_light` | lit quartile `#DCCBBD` | 28–32°, 0.10–0.14 | top 30 % of each rock's height at 35 % | rough 0.85 |
| `m045_rock_deep` | the exploded median `#B1A99F` | 28–34°, 0.08–0.12 | lowest 0.25 at 25 % | rough 0.9 |
| `m045_sand` | `#EFD19D` ± 8 (f34, front and exploded agree within 4) | 37–39°, 0.33–0.36 | patch | rough 0.95 |
| `m045_sand_deep` | shade quartile `#E5C793` ± 10 (start from the "ground foliage" swatch `#C29E7E`) | 34–39°, 0.36–0.40 | within 0.35 of trunk, roots, rocks, hubs at 25 %; bevel and edge 30 % | rough 0.95 |
| `m045_plant` | plant v > .7 `#AFC518`–`#B8C612`; lime group `#91AF18`–`#A2BC19` | 64–72°, sat ≥ 0.82 | outer / taller leaves; all sprig leaves | rough 0.85, low spec |
| `m045_plant_deep` | green group `#4A7823`–`#507F27` | 88–96°, sat 0.65–0.75 | middle leaves | rough 0.85, low spec |
| `m045_plant_dark` | dark group `#1D4F27`–`#275A2B` rendered lit (start from the dark swatch) | 120–135°, 0.55–0.65 | innermost / lowest leaves, about 20 % | rough 0.85, low spec |

**Calibration warnings:**
- **Plates (W04 P2; M035 "lit foliage dark and less lime"; M038 "greens slightly grey").** On the f34_sheet canopy:
  - the lit (v > .7) median must be within 12 of `#A5C935` (hue 72–80°, sat ≥ 0.68);
  - the whole-canopy median within 15 of `#519037`;
  - the left (shade) half's median hue ≥ 125°;
  - the crown's right half lighter than the lower tier's.
  If the lit faces read olive or grey, raise the base key's saturation; don't paint the lit side.
- **Bark:** the f34 lit-half median within 12 of `#B06325`, R > G > B. Not red, not tan; more saturated than 042's.
- **Rock:** never blue or mauve; R > G > B on every rock median.
- **Plants vs plates:** keep `m045_plant` at least 5° yellower than `m045_needle_light` after calibration.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles, never facing)

- **Plates:** a field along each plate's own axis (0 at the root, 1 at the tip):
  - `needle_deep` over 0–0.3 (30 %);
  - `needle` over 0.3–0.65;
  - `needle_light` over 0.65–1.0 (+20 %).
  - Tier offsets: crown +30 % light, middle +10 % light, lower row A +10 % deep.
  - The whole plate (top, bottom and walls) takes its position's colour. **Nothing by facing.** Per-plate tint ±0.04.
- **Cores:** `needle_deep` 70 %; the flat joining ring `needle` 60 %. Recess pocket faces `bark_deep` (hard: a socket).
- **Trunk and roots:**
  - base `bark`;
  - `bark_deep` by height (lowest 0.3: 25 %) and in the knots (hard);
  - `bark_light` on the top face (hard: a cut face) and on the outer half of each root's top ridge (20 %);
  - the bottom face `bark_deep` 70 %;
  - per-facet tint ±0.04.
- **Rocks:** `rock` base; `rock_light` by height within each rock (top 30 %: 35 %); `rock_deep` on the lowest 0.25 (25 %).
- **Sand:** `sand` base; `sand_deep` by distance (within 0.35 of trunk, roots, rocks and hubs: 25 %) and on the bevel
  (30 %). Average with neighbours before quantising (M034: no triangle shards).
- **Plants:** per leaf by role (outer / taller → `plant`, middle → `plant_deep`, innermost → `plant_dark`), ±0.04 tint
  per rosette.
- **Hard edges only where materials meet:** plate | bark (the recess pocket), bark | sand, rock | sand, leaf | sand.

### 5.6 Texture (Tint) and finish

- **Tint:**
  - plates: amp 0.04 per plate (one tone per facet pair);
  - bark: 0.04 per facet;
  - rock: 0.04 per facet (scale 0.4);
  - sand: 0.03 (scale 0.15, broad);
  - plants: 0.04 per leaf.
  Never per-triangle confetti.
- **Finish:** plates and plants `low_spec=True`, rough 0.85; bark 0.9; rock 0.85; sand 0.95. No emission.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Canopy (f34_sheet):** lit (v > .7) within 12 of `#A5C935`; whole canopy within 15 of `#519037`; shade-half hue
  ≥ 125°; crown right half lighter than the lower's.
- **Canopy (front / side / rear):** medians within 15 of `#4C8C38`–`#5B9635`.
- **Trunk:** f34 lit half within 12 of `#B06325`.
- **Rock:** f34 v > .7 within 10 of `#CEC0B4`, R > G > B.
- **Sand:** f34 S within 8 of `#EFD19D`.
- **Plants:** f34 plant (G below y-equivalent 0.2 H) v > .7 within 12 of `#AFC518`; hue split lime / green / dark
  within ±10 points of 37 / 40 / 23.
- **Shares** per §2.5.

## 6. Joins and contact (no floating dressing)

- **Shells:**
  - the trunk + roots: one closed shell;
  - each tier core (with recess and peg): one closed shell;
  - each plate, rock, leaf and plant hub: its own closed shell;
  - the patch: one closed shell.
  All of them go in one hero object (decision §8.5).
- **Stack (§2.1):** the trunk base is sunk 0.08 into the patch. Each tier rests on the piece below at two places, the
  recess ceiling over the peg top and the mouth ring over the cap, each 0.015 measured by BVH nearest distance
  (0.005–0.03). Never coplanar, never overlapping, never hovering. The peg walls clear the recess walls (0.03–0.06): no
  intersection.
- **Plates:**
  - each plate's root end is buried 0.15–0.3 in its core and leaves the core through its surface with no gap (keep the
    buried part short: it is hidden geometry);
  - row B plates rest on row A (seated by ray cast, gap 0.015) or on the core;
  - neighbours may touch but cut no more than 0.05 into each other.
  Every plate chains by contact to its core, the core to the stack, the stack to the ground.
- **Base:** rocks are sunk 0.08 and plant hubs 0.03 into the patch top. Every leaf is within 0.03 of its hub (STAGES:
  no hidden stems). Leaves may touch a rock, root or the trunk but cut no more than 0.05 into it.
- **Count floating shells before reporting** (STAGES: 035 and 036 failed round 1 on this): **0**. A shell floats if its
  nearest distance to every other shell and the ground is > 0.03, or if it doesn't chain to the ground.
- **Bowties:** run `M.fix_bowties` on every object; `nonmanifold_verts` must be 0. Plate roots, leaf hubs and the
  recess corners are where they grow.

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no particles, no falling needles. The cast shadow is the render's,
not an effect.

- **Stage 5 (lighting): skip, and record why.** No emission, no PointLight.
  - Studio notes (Requires Manual Validation): the canopy's lime-in-light / deep-in-shade read under the game's sun
    (W04's firs rendered too dark and flat, P2); the bark stays a saturated orange, not red; the rock stays pale
    neutral grey.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** Not recommended: falling-needle particles, pollen,
  dust or any light.
- **Collision:** hero `precise`; a hull would wrap the patch and the canopy into a solid cone. The tiers and trunk parts
  `hull`; GroundFoliage `box`; rocks `hull`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by searching `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json`, the
repo text (`git grep`) and every sheet / kit / wip `.blend` (zstd-decompressed, `m042_study/blendall.py`):
- **W04:**
  - `Sapling`, `SaplingBushy`, `SaplingSeedling`, `SaplingSlender`, `SaplingTopFoliage`, `SaplingLowerFoliage`,
    `SaplingTrunk`, `SaplingRootsBase`;
  - `YoungFir*`, `ClassicPine*`, `OldPine*`;
  - keys `w04_*`.
- **V02 / V06:** `HazelShrubSapling`, `BirchSapling`.
- **M042:** `TieredFir*` (in `kit/wip/M042.blend`).
- **M032 / M037:** `pine_*` pieces and `m032_pine`.
- **`PineSapling`, `YoungPine`, `Pineling`, `SaplingPine` and `m045` occur nowhere** in the repo text, the manifests or
  any `.blend`.
- **Avoid `PineSaplingTopFoliage` / `…LowerFoliage`:** they contain W04's `SaplingTopFoliage` / `SaplingLowerFoliage`
  as substrings, which would confuse greps. The names below use `…Tier`.

| Object | Part | Why |
| --- | --- | --- |
| `PineSapling` | hero: patch, trunk, three tiers, rocks, plants | the sheet's title; W04 owns bare `Sapling` |
| `PineSaplingTopTier` | "Top Foliage Tier": star cone + recess + 12 plates | |
| `PineSaplingMiddleTier` | the lower tier at 0.8 (§3.2) | not drawn in the exploded |
| `PineSaplingLowerTier` | "Lower Foliage Tier": core + recess + peg + 14 plates | |
| `PineSaplingTrunk` | "Trunk": body + six root flares | |
| `PineSaplingGroundFoliage` | "Ground Foliage": rosette P1 with its hub | |
| `PineSaplingRockMedium` | "Rock (Medium)": RM | |
| `PineSaplingRockSmall` | "Rock (Small)": RS2 | |

- Palette keys `m045_*` (§5.4). Collection `Kit/M045 Pine Sapling`. No sockets.

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **10.0 tall, canopy tips r 3.5 (silhouette 6.8–7.2), trunk Ø 1.1 / 1.25 / 2.1 (peg / under the
   canopy / flare), patch about 7.8 × 6.8** (recommended: clearly the smallest pine, 0.63 × 042, with tips at hip height
   and the middle hem at head height). Alternatives: 8 (canopy 5.6, rocks 0.6–1.0), or 12 (closer to 042, weaker
   distinction).
2. **Name (§8):** **`PineSapling` and the seven parts above** (recommended), or `YoungPine`. Not `Sapling*` (W04).
3. **Tier count and reuse (§3.2):** **three tiers, the middle built as the lower tier's construction at 0.8 (same plate,
   thickness 0.20), exported as `MiddleTier` too** (recommended), or export only the exploded's two tier parts (the hero
   still has three).
4. **Plates (§2.2, §2.3):** **thick constant-thickness paddle slabs (0.20), midrib fold, chisel tip, length : width ≈
   1.5; crown 4 + 8, middle 7 + 7, lower 7 + 7; one plate aimed at −Y on every tier** (recommended), or thin kites as on
   042 (cheaper, but loses "consistent thickness" and makes the two trees alike).
5. **Stacking (§2.1, §3.4):** **peg and recess at every joint (the trunk top into the lower tier, each tier's peg into
   the tier above), a square recess as drawn, seats 0.015, the mouth ring also resting on the cap below** (recommended),
   or an octagonal recess.
6. **Packaging (§6):** **one hero object of closed shells (trunk + roots one unioned shell; cores; plates; patch; rocks;
   leaves; hubs)** (recommended), or a separate canopy object with `collision="none"`.
7. **Branches (§3.10):** **none** (recommended: the sheet draws none; the skeleton is the tapered trunk with knots and six
   root flares).
8. **Trunk (§2.4):** **smooth 8-sided taper, 2 knots, 6 short blunt root flares (r 1.6–2.5, the front-right one
   longest)** (recommended; no planks or slits, unlike 042), or 4 flares (exploded count in front only).
9. **Dressing (§2.4, §3.5):** **4 rocks (RM back-right, RS1 front-left, RS2 front-right, RS3 far left), 4 broad-leaf
   rosettes, 3 sprigs, no pebbles** (recommended).
10. **Comparison cameras (§3.1):** **`f34_sheet (−15, 16)` governing** (probe az 0 … −30, e ±4); `r34_sheet (165, 16)`;
    `front_sheet (0, 5)`, `side_sheet (90, 5)`, `rear_sheet (180, 5)`; kit `top` and `underside`. Extras: the parts shot
    (−15, 20), `join_cu` (e −30), `plate_cu (−60, 15)`, `underside_cu` (patch hidden), `root_cu (−20, 15)`, and a scale
    shot with a 5.5-stud marker. Hide the floor in every `*_sheet` render.
11. **Colour (§5):**
    - **plate keys base / light / deep calibrated to the f34 lit half `#9EC534`, v > .7 `#A5C935` and the dark swatch;
      blended along each plate and by tier (the crown lightest);**
    - **undersides keep their position colour (no facing);**
    - **bark lit half `#B06325`; rock lit `#CEC0B4`; sand `#EFD19D`, with `sand_deep` from the tan "ground foliage"
      swatch;**
    - **plant leaves lime / green / dark per leaf** (recommended).
12. **Underside close-up (§3.6):** **keep the continuous patch; compare close-up 3 with a patch-hidden render**
    (recommended), or replace the patch with sand puddles.
13. **Stages 5 and 6:** **skip both, recorded** (recommended).
14. **Collision (§7):** **hero `precise`, tiers / trunk / rocks `hull`, GroundFoliage `box`** (recommended).
15. **Budget (§4.3):** **4000 limit, about 2400–2700 planned, ceiling 3200; parts under 1000** (recommended).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **Reading as 042 scaled down.** The verifier compares the f34 renders of both trees side by side. 045 must show:
   - thick blunt slabs (visible side walls, chisel tips), not thin pointed kites;
   - a smooth tapered trunk with short blunt flares, not a planked trunk with long kinked roots;
   - broad-leaf rosettes, not lanceolate clumps;
   - paler neutral rocks;
   - a 10-stud height.
2. **Floating dressing (STAGES; 035 and 036 round 1).** Every plate, rock, leaf and hub is within 0.03 of a neighbour,
   its core or the patch, and chains to the ground. Count floating shells: **0**. Tiers rest on pegs and caps
   (0.005–0.03) and never hover; the M032 pines stood apart until M037 seated them.
3. **Pagoda rings or a smooth cone (W04 H11).** Each tier is a ragged ring of separate broad plates, two rows deep,
   with tips drooping below the notches and a dark crease under every hem. The outline steps in at two waists (§2.5
   targets).
4. **Spiky or edge-on leaves (039).** Plates are broad paddles (length : width ≈ 1.5) and plant leaves are broad ovals
   (≈ 2.2). No needles, no pointed ladders, no leaves seen only edge-on from the f34 or front.
5. **Colour by facing (the 042 ruling).** No light-right / dark-left paint, no dark undersides, no lime rim key. Use
   fields along each plate, by tier, by height, and by role (pocket, knot, cut top). `K.check` facing correlation must
   be < 0.5 per material.
6. **Canopy too dark, grey or olive (W04 P2; M035; M038; M036).** Calibrate to the rendered lit regions (§5.4): lit
   canopy within 12 of `#A5C935`, sat ≥ 0.68; a crown lighter than the lower tier.
7. **Hidden or twig trunk (W04 "trunk hidden").** Bark shows from the sand to the lowest tips (z 0–2.7), Ø 1.25–2.1
   with the flare, and T 10.8 ± 3 % of the f34. The flares stay clear of the plants in the front and side views.
8. **Egg rocks (M034 round 1; M037 "rock parts egg-shaped") and mauve rock.** Rocks are chunky rounded-angular blocks: a
   flat base, a flat sloping 4–5-corner top, 12–16 broad facets, W : H 1.3–1.6. Colour R > G > B with a hue of 26–32°,
   never pink or blue.
9. **Lettuce or ivy plants (M036 "ivy mounds"; M038 "cupped lettuce heads").** Rosettes of 8–11 separate broad leaves,
   each folded on its midrib and arching out from a small hub. They are not a closed cup or a mound.
10. **Over-wide patch or base clutter.** The patch is thin (0.12), about 7.8 × 6.8. The dressing stays inside it and
    below 1.5 tall.
11. **The top view.** About 8 big points with the second row between, a 4-point crown star with a ridge at −Y, and the
    back-right rock and two rosettes showing beyond the canopy.
12. **Bowties** at plate roots, leaf hubs and the recess corners: `M.fix_bowties` on every object, `nonmanifold_verts` 0.
13. **Exact booleans:** only for the roots into the trunk, at the origin, one root at a time, saving between them
    (STAGES "Booleans"). Nothing else is unioned; the recess is modelled as part of the core, not cut by a boolean.
14. **Names and scope:**
    - No `Sapling*` alone (W04) and no `TieredFir*` (042).
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit `lib/vfx.py` or the frozen shared helpers.
    - Don't touch M042's objects: it is being modelled in parallel.

## Decisions (main session, 2026-10-29)
All 15 recommendations are accepted.
1. **Size:** 10.0 tall, with canopy tips at r 3.5.
2. **Names:** hero `PineSapling`, parts `…TopTier`, `…MiddleTier`, `…LowerTier`, `…Trunk`, `…GroundFoliage`, `…RockMedium` and `…RockSmall`, keys `m045_*`.
3. **Tiers:** three. The middle tier is built as the lower tier at 0.8 scale and exported as `MiddleTier`.
4. **Plates:** thick paddle slabs, 0.20 thick, with chisel tips and length : width about 1.5. Counts: crown 4 + 8, middle 7 + 7, lower 7 + 7. One plate on each tier aims at the front.
5. **Joints:** a peg and square recess at every joint. Each mouth ring rests on the cap below with 0.015 seats. **No floating dressing.**
6. **Packaging:** one hero object of closed shells. Only the roots are unioned into the trunk. Every shell is manifold with 0 bowties.
7. **Branches:** none.
8. **Trunk:** a smooth, tapered 8-sided trunk with 2 knots and 6 blunt flares reaching r 1.6–2.5. It must read in every view.
9. **Dressing:** 4 rocks (chunky, not eggs), 4 broad-oval rosettes and 3 sprigs, all seated by contact.
10. **Cameras:** as listed. `f34_sheet (−15, 16)` governs.
11. **Colour:**
    - Plate keys are calibrated to the f34 lit canopy and the dark swatch, and blended along each plate, with the crown lightest.
    - **Nothing is coloured by facing.**
    - Bark lit `#B06325`, rock lit `#CEC0B4` (R ≥ G ≥ B), sand `#EFD19D`.
12. **Underside close-up:** compare it with the patch hidden.
13. **Lighting and VFX:** skip both, and record that.
14. **Collision:** hero precise.
15. **Budget:** about 2400–2700 tris, ceiling 3200.

**Binding checks.** The §1.5 checks that set it apart from M042 (scale, slab plates, peg joints, smooth trunk, broad rosettes, pale rocks) are binding. So are the f34 shares, within ±4.
