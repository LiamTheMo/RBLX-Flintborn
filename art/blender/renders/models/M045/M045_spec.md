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
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m045_study\`.
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

## Stage 1 — Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m045.py` (`build()`), work file `art/blender/assets/kit/wip/M045.blend`, background
session on port 9881. Patterns copied from m042 (not imported): cut tests, contact report, `_post`, the trunk union
through `m033._union_fine`. `m033._zip` was **not** reused: it skips a vertex of the inner ring that lies just before
the outer ring's first vertex (it left a triangle over the recess corner, a self-intersection), so m045 has its own
`_zip` that starts both rings from a common reference angle.

**Parts, each from its own function:**
- `plate()`: one closed 34-tri paddle slab, **0.20 thick everywhere** (straight side walls under the whole outline).
  Stations at 0 / 0.45 / 0.78 / 1.0 L with half-widths 0.08 / 0.50 / 0.425 / 0.09 W: a narrow buried root, widest at
  0.45 L, and a **chisel tip 0.18 W wide**. A midrib fold is raised 0.11 W on stations 1-3. The outer part bends down by
  `droop` in two steps (at 0.45 and 0.78 L), and the plate is rolled about its own axis. The chord is fitted so the tip
  anchor lands on the requested (r1, z1).
- `_core(kind)`: one closed shell per tier.
  - Lower / middle: an octagonal peg on a flat cap, a pleated frustum (corners at the row-A azimuths ±0.1), an underside
    down to a flat ring, and a **square recess turned 45°** (a diamond from the front). Its walls and ceiling are faces
    of the same shell.
  - Crown: the 4 + 4-ridge star cone (apex 10.0, rim z 8.6), its underside, the flat ring and the square recess.
  - Recess half-side = the entering piece's apothem + 0.045 (wall clearance 0.045-0.065).
- `tier(kind)`: the core, then row A, then row B.
  - Every plate is tested against the plates already placed, and against the plates of the tier below (`_below`, a
    probe build, so a part built alone equals the hero's tier).
  - The test is a **cut depth**: the deepest sample of either slab inside the other, ignoring samples hidden in the
    core.
  - A plate cutting more than 0.05 is rolled further. A lift / sink plate is first moved whole, then turned about its
    root. Narrowing (×0.96) is the last resort.
- `trunk_body()` + `root()` ×6:
  - **Body:** 8-sided and tapered, with a face toward −Y. Rings (z / width across flats): 0.04 / 2.30, 1.0 / 2.10,
    1.5 / 1.60, 2.0 / 1.37, 2.5 / 1.25, 3.1 / 1.19, 3.8 / 1.14, 4.4 / 1.10. Vertex jitter ±0.035, with the top two
    rings exact for the recess.
  - **2 knots:** a facet inset 0.11 and pulled in 0.05, front-right at z 2.8 and left-back at z 2.25.
  - A flat top (the peg) and a flat bottom.
  - **Six short blunt root flares:** pentagon-section blocks with an off-centre top ridge, flat cut ends 0.35 × 0.30,
    bottoms at z 0.08. RFR 315° r 2.5, RF 255° r 1.6, RL 200° r 1.9, RBL 145° r 1.8, RB 85° r 2.0, RR 355° r 1.8.
  - The roots are exact-unioned in one at a time at the world origin: one closed shell.
- `patch()`: a 12-point lobed outline (ellipse 3.45 × 2.95 with lobes, let out 0.2 beyond every item's footprint), a flat
  crest at z 0.12, a bevel 0.35 wide down to 0.03, a short side and a flat underside at z 0.
- `rock()` ×4: the hull of ring stacks, jitter 6 %.
  - Rings: base 0.90 / 6 points, widest 1.0 at 0.22 h / 7, shoulder 0.95 at 0.74 h / 6, flat crown 0.70 at h / 5. The
    crown slopes 10-14 % to one side.
  - Sizes: RM 1.9 × 1.6 × 1.15, RS1 1.5 × 1.2 × 0.95, RS2 1.1 × 0.95 × 0.72, RS3 1.0 × 0.9 × 0.62 (W : H 1.4-1.65).
  - Each is sunk 0.08 into the patch top under it (`_patch_z`).
- `rosette()` ×4 and `sprig()` ×3:
  - Five-sided hub pyramids sunk 0.03 into the patch.
  - Leaves are closed 12-tri broad pointed ovals (`_leaf12`): widest (W) at 0.4 L, L : W 1.55, a V fold of 16°, the tip
    arching out. The outer ring is pitched 46-58°, the inner ring 64-78°.
  - A leaf that would cut a rock, the trunk or a root is turned or shortened. P4 and S3 each dropped one leaf: 51
    leaves.

**Tiers as built.** These were tuned on the renders; the spec's §2.2 numbers were changed where the renders showed it.

| Tier | Row A (long, one at −Y) | Row B | Core: cap / peg / recess mouth |
| --- | --- | --- | --- |
| Lower | 7, root (0.75, 5.85) → tip (3.80, 2.75), front 2.45, W 2.0, droop 15 | 7 **sink**, (0.70, 5.50) → (2.90, 3.35), W 1.75 | cap r 0.85 @ 6.10, peg Ø 0.9 → 6.50, mouth 3.80 (ceiling 4.415) |
| Middle | 7, (0.60, 7.50) → (3.00, 5.15), front 4.85, W 1.65 | 7 **sink**, (0.55, 7.15) → (2.30, 5.40), W 1.4 | cap r 0.70 @ 7.90, peg Ø 0.75 → 8.25, mouth 6.115 (ceiling 6.515) |
| Crown | 4 long hem, (0.50, 8.75) → (1.75, 7.25), front 7.05, W 1.3 | 4 short hem **sink**, (0.45, 8.55) → (1.48, 7.38), W 1.1; 4 upper **lift**, (0.30, 9.05) → (1.22, 8.25), W 0.95 | star cone apex 10.0, rim 8.6, mouth 7.915 (ceiling 8.265) |

Why the changes (each was tried and measured):
1. **Row B sits under row A ("sink"), not on it.**
   - With row B resting on row A (the spec), the 0.20 slabs plus the rolled A edges at the seams (about 0.4 above the
     cone) forced row B 0.5-0.65 higher.
   - The tiers then became fat domes with no waists (front waist widths .66-.76 against the sheet's .49), or, with lifted
     tips, flat cabbage tops.
   - With row A as the outer cone through the sheet's waist (lower tier r 1.7 at z 4.9), and row B tucked about 0.3
     under it, every front / side / rear hem lands within 0.03 of the sheet (table below). The B plates show in the V
     gaps between the A roots and tips, a step higher than the A tips.
   - Trade-off: from the f34 (e 16) the upper ring of plates the sheet draws **on top** of each tier is not seen; the f34
     reads as long hem plates.
2. **Row A is 13 % narrower than the spec (2.0 / 1.65 instead of 2.3 / 1.9).** At 2.3, seven plates overlap 0.6 at
   their widest. The rolls that needed (up to 22°) lifted the edges and caused every row-B conflict. At 2.0 the rolls are
   6-12°.
3. **The cores are taller, so the stack seats moved** (lower cap 6.10, middle mouth 6.115, middle cap 7.90, crown mouth
   7.915): the 45° row-A roots sit higher than the spec's caps.
4. **The hem tips are lower and wider** (lower 2.75 at r 3.8, middle 5.15 at r 3.0, crown 7.25). Our widest row is the
   plates' 0.78 L corners, above the tips; with the tips moved, the measured hems match the sheet.
5. **Hero depth 7.7 (the spec's bbox said 6.8).** The canopy (tips r 3.8) is now the deepest thing, not the patch (the
   patch is 6.9 × 6.4). `TARGET_SIZE` is 7.9 ± 0.4 × 7.6 ± 0.4 × 10.0 ± 0.2.

**Hero `PineSapling`** = patch + rocks + plants + the lower, middle and crown tiers, with the unioned trunk joined in. It
is one object of 107 closed shells: patch 1, trunk 1, cores 3, plates 40, rocks 4, hubs 7, leaves 51.

**Parts:** `PineSaplingTopTier`, `…MiddleTier`, `…LowerTier`, `…Trunk`, `…GroundFoliage` (rosette P1 + hub),
`…RockMedium` (RM) and `…RockSmall` (RS2). Each sits at the origin (bottom centre); `o["m045_offset"]` is that origin in
the build frame.

**Measured on the renders** (`m045w/tiers_r.py`, the study's masks; floor hidden, 3× lens):

| View | Hems h / width (sheet) | Waists h / width (sheet) | Canopy W / H |
| --- | --- | --- | --- |
| front_sheet (0, 5) | .749 / .49 (.749 / .48); .551 / .82 (.529 / .81); .326 / 1.0 (.309) | .720 / .35 (.722 / .29); .509 / .58 (.486 / .49) | .720 (.714) |
| side_sheet (90, 5) | .749 / .47 (.746 / .48); .520 / .78 (.542 / .77); .303 (.304) | .491 / .65 (.492 / .46) | .731 (.700) |
| rear_sheet (180, 5) | .749 / .48 (.746 / .45); .546 / .81 (.531 / .81); .317 (.312) | .720 / .35 (.727 / .29); .514 / .54 (.492 / .50) | .737 (.708) |
| f34_sheet (−15, 16) | .766 / .48 (.762 / .50); .563 / .81 (.577 / .81); .340 / 1.0 (.379) | .729 / .42 (.731 / .33); .514 / .66 (.526 / .50) | W : H .693 (.726) |

- **Trunk widths** (front cell, as a fraction of the canopy W): h .25 .179 (.178), .20 .202 (.195), .15 .262 (.227),
  .10 .286 (.303).
- Bark shows from h 0 to .27-.33 in every side view (sheet .30-.34).

## Stage 2 — Optimisation and cleanup

- **Tris:** hero **2910** (plan 2400-2700, ceiling 3200, limit 4000).
  - By shell type: plates 1360 (40 × 34), leaves 612 (51 × 12), trunk 348 (body + 6 unioned roots), cores 262, rocks
    176, patch 96, hubs 56.
  - Parts: TopTier 470, MiddleTier 576, LowerTier 576, Trunk 348, GroundFoliage 140, RockMedium 44, RockSmall 44. All
    are under 1000.
- **`M.audit` on all 8 objects:** non-manifold edges 0, **bowtie / non-manifold verts 0**, boundary 0, wire 0, loose 0,
  zero-area 0, n-gons 0, duplicate verts 0, normals outward, transforms applied, origin at the bottom centre.
  - The hero's bbox centre is the origin; its build-frame offset is (0.095, −0.24, 0).
  - Per-shell report: every shell is closed and outward (volume > 0), with 0 self-intersections.
  - Trunk: 1 shell, 6 unions, 0 union retries, 22 slivers collapsed.
- **Thin triangles:** the parts have none under 2° (trunk minimum 2.04°). The hero has 24 faces under 2° (minimum
  0.9°), on the joined trunk copy after the hero's triangulate pass. Not an error; listed for the verifier.
- **Sizes:** hero 7.76 × 7.70 × 10.00; TopTier 3.73 × 3.78 × 3.09; MiddleTier 6.23 × 5.93 × 3.49; LowerTier 7.64 ×
  7.68 × 4.15; Trunk 3.64 × 3.97 × 4.36; GroundFoliage 2.21 × 2.54 × 1.37; RockMedium 1.83 × 1.55 × 1.27; RockSmall
  1.03 × 0.94 × 0.78.
- **Contact (no floating dressing):**
  - Hero: floating 0, unchained 0, max gap 0.000.
  - Core seats **0.015 / 0.015 / 0.015** (trunk top → lower recess ceiling, lower peg → middle, middle peg → crown), with
    0 core / trunk intersections: the pegs clear the recess walls.
  - 41 plate pairs touch and **0 cut more than 0.05** (deepest 0.048). 0 leaves cut a rock or the trunk.
  - Each tier part: floating 0, unchained 0, deepest cut 0.035 / 0.047 / 0.048.

## Stage 3 — UV

`M.smart_uv` (angle 45, ANGLE_BASED, margin 0.008), then `m012._uv_unfold`.
- Every object: 0 overlapping pairs, 0 flipped, minimum island gap 0.016, border 0.008, texel density min / median / max
  1.0 / 1.0 / 1.0, conformal stretch p95 1.00-1.03.
- Islands: hero 939, TopTier 179, MiddleTier 191, LowerTier 182, Trunk 52, GroundFoliage 44, rocks 11 / 8.

## Stage 4 — Materials, colour and texture

- **Calibration:** `K.calibrate` (6 iterations) against the spec's §5.4 targets gave:

  | Key | Calibrated | Rendered (target) |
  | --- | --- | --- |
  | needle | #80A233 | 156,196,52 (#9EC534) |
  | needle_light | #88A635 | |
  | needle_deep | #25663D | 41,118,63 (#28723F) |
  | bark | #8C5116 | 176,99,41 (#B06325) |
  | bark_light | #BB7428 | |
  | bark_deep | #5A3218 | |
  | rock | #A49C96 | 207,191,175 (#CEC0B4) |
  | rock_light | #B0A8A0 | |
  | rock_deep | #8C8A89 | |
  | sand | #BCAA88 | 238,208,157 (#EFD19D) |
  | sand_deep | #B6A381 | |
  | plant | #8FA41C | 176,198,28 (#AFC518) |
  | plant_deep | #436B25 | |
  | plant_dark | #1E4A26 | |
- **Pass 2 on the f34_sheet render.** As m042 found, the studio lights both halves of the canopy almost alike, so a
  needle base calibrated to the sheet's lit half made the whole canopy lime (median #88B736 against #519037). Final
  `PALETTE`:
  - needle **#4B8034**, needle_light **#B4C82C**, needle_deep **#1E5A3A**;
  - bark **#B06624**, bark_light #C47A2C, bark_deep #643A1C;
  - rock **#A49D99**, rock_light #B0A9A4, rock_deep #8C8A89;
  - sand #BCAA88, sand_deep #B6A381;
  - plant **#879C1A**, plant_deep #436B25, plant_dark **#2A5A2C**.
- **Blends** (position and role only, `_mix` in 25 % steps):
  - **Plates:** each plate has three bands along its own axis (root / middle / tip), on the deep ↔ light axis:
    - lower A (−.5, −.25, +.25), lower B (−.5, −.25, 0);
    - middle A (−.25, 0, +.5), middle B (−.25, 0, +.25);
    - crown long (+.25, +.5, +.75), crown short (0, +.25, +.5), crown upper (+.25, +.5, +.75).
    The crown is the lightest tier.
  - **Cores:** needle_deep 75 % (peg 50 %); the flat joining ring 25 % (the lighter ring of close-up 1); recess pockets
    bark_deep (hard: a socket). The crown cone is needle_light 75 %.
  - **Trunk:** bark; the lowest band (z < 1) and the bottom 25 % deep; knots bark_deep, with their inset walls 50 %.
    Root faces below z 0.5 are 25 % deep and the cut ends 50 % deep.
  - **Rocks:** the top 25 % of the height +50 % light, the next 15 % +25 % light, the lowest 25 % +25 % deep.
  - **Sand:** the bevel 50 % deep; within 0.35 of the trunk, roots, rocks and hubs 25 % deep.
  - **Plants (by role):** the outer ring alternates lime and green, the inner ring is mostly dark, and the sprigs are
    lime (one green). Each leaf's base faces are a step deeper. Hubs are plant_dark / bark_deep 25 %.
- **Nothing is coloured by facing.**
  - The trunk's flat top was bark_light and its bottom 75 % deep. K.check flagged that as baked lighting (corr 0.78), so
    both now keep the body's colour at their height. The root-ridge highlights were dropped for the same reason.
  - Final baked-shading correlations: hero 0.00, TopTier 0.21, Trunk 0.38 (limit 0.5), the others 0.00.
- **Tint:** per-plate tone ±0.04 plus broad mottling 0.03 (scale 0.6); cores 0.03; bark per facet column ±0.04 plus a
  0.04 mottle; roots 0.04; rocks 0.04 (scale 0.4); sand 0.03 (scale 0.15); leaves ±0.04 per leaf.
- **Finish:** plates and plants rough 0.85 with low specular; bark 0.9, bark deep 0.95; rock 0.85; sand 0.95; no metal,
  no emission.
- **Re-measured on f34_sheet** (`m045w/col.py`):

  | Region | Ours | Sheet | Check |
  | --- | --- | --- | --- |
  | Canopy median | #529535 | #519037 | within 15 ✓ |
  | Canopy v > .7 | #9FC835 (hue 77, sat .74) | #A5C935 | within 12 ✓ |
  | Crown right / lower right | #91BB30 / #498935 | | crown lighter ✓ |
  | Trunk lit half | #A55C27 | #B06325 | within 12 ✓, R > G > B |
  | Trunk v > .7 | #C66E2E | #E48230 | |
  | Rock v > .7 | #CCC2B0 (hue 39) | #CDC2B5 | R ≥ G ≥ B ✓ |
  | Sand | #F1D2A0 | #EFD19D | ✓ |
  | Plants v > .7 | #B2C91D | #AFC518 | ✓ |
  | Plant hue split lime / green / dark | 47 / 37 / 16 | 38 / 39 / 23 | within ±10 ✓ |

  Canopies in the other views (ours | sheet): side #447829 | #5B9635, rear #477F2E | #519237, r34 #467F2D | #5A9636.
  The near-level views read a little darker.
- **Shares on f34_sheet** (ours | sheet): G 76.8 | 77.2, T 8.6 | 10.8, S 5.1 | 3.1, R 7.7 | 7.7. All are within the
  binding ±4; S is at the edge of the spec's ±2.
  - Front (ours | sheet): G 79.5 | 80.4, T 7.7 | 10.1, S 3.3 | 2.0, R 8.3 | 5.4.
- **Known misses:**
  - The sheet's shade half is a deep teal (hue 139) because its light comes from the right. Our studio lights the left of
    the canopy, so our "shade half" reads hue ~101. Not painted (no colour by facing).
  - The thin lime rim on the plate edges (close-up 2) is light, not paint, and is not reproduced.

## Stage 5 — Lighting

Skipped: the sheet shows nothing glowing and no light (spec §7). No emission, no PointLight.

Studio notes (Requires Manual Validation): under the game's sun, check that the canopy reads lime in light and deep green
in shade, the bark a saturated orange (not red), and the rock a pale neutral grey.

## Stage 6 — VFX

Skipped: the sheet shows no effect (spec §7). The hero has no VFX sockets (checked by `build()`).

## Modeller's notes for the verifier

**Renders** are in `art/blender/renders/models/M045/`; the contact sheet is `M045_views.png`.
- Kit views: `front34`, `rear34`, `front`, `side`, `rear`, `top`, `underside`.
- Sheet views: `f34_sheet` (−15/16), `r34_sheet` (165/16), `front_sheet` / `side_sheet` / `rear_sheet` (e 5),
  `top_sheet`.
- Parts: `part_toptier` … `part_rocksmall` (−15/20), plus `exploded` and `scale` (with a 5.5-stud marker).
- Close-ups:
  - `join_cu`: the lower tier lifted 1.4 off its trunk, seen from below: the flat lighter ring and the dark diamond
    recess.
  - `plate_cu`: lower-tier plates from −60/15: slab thickness and chisel tips.
  - `underside_cu`: the hero without the patch, from below.
  - `root_cu`.

**Measuring scripts** (scratchpad `m045w/`):
- `tiers_r.py <png> [cell]`: hems, waists and trunk widths with the study's masks.
- `col.py <png> <cell>`: colour regions and shares.
- `sbs.py <cell> <png> <out>`: side by side.
- `cuts.py`: plate cut locations per tier.
- `m045_study/measure_render.py` also works on our renders.

**§1.5 differences from 042, as built:**
- Height 10.0 (042: 16). Canopy tips r 3.8 (silhouette 7.2-7.6).
- Trunk width 1.10 at the peg, 1.25 at z 2.5, 2.30 at the foot: ×2.1 from top to flare (042: ×1.6).
- **0.20-thick constant slabs** with straight walls, a midrib fold and a 0.18 W chisel end (042: thin kites with a keel).
- Plates 4 + 8 / 14 / 14 (042: 8 / 12 / 16).
- **A peg and square recess at every joint**, seats 0.015 (042: flat caps and hubs).
- **A smooth 8-sided trunk with 2 knots and 6 short blunt flares, r 1.6-2.5** (042: planked, with slits and long kinked
  roots).
- Rosettes of broad pointed-oval leaves, L : W 1.55 (042: lanceolate).
- 4 pale neutral rocks, lit #CCC2B0, and no pebbles.
- Bark lit half #A55C27, more saturated than 042's #BE6F30 target family.

**Plate length : width (a binding check, not fully met):**
- The visible length : width is about 1.4-1.5 on the crown and 1.75 on row B.
- On the lower and middle row A it is **1.95-2.1** (lower A chord 4.35, width 2.0; middle A 3.36 / 1.65).
- The sheet's 1.5 ratio with 0.20 slabs could not be kept together with the hem positions and the no-cut rule (Stage 1,
  changes 1-2). The plates still read clearly as thick blunt slabs, not 042's kites, but they are narrower than the
  sheet's.

**Other leftovers:**
- The f34 lower hem reads at h .340 (sheet .379); the front view matches.
- The lower waists are wider than the sheet's (front .58 vs .49, side .65 vs .46): the middle tier's diagonal tips hang
  into the waist band.
- The f34 does not show row B on top of each tier, because row B is tucked under row A (Stage 1, change 1).
- The top view shows only the canopy (G 97 %, R 2 %). With tips at r 3.8 the rocks at r 2.4-2.9 are covered, while the
  sheet's top cell draws a smaller canopy than its front cell (spec §3.3).
- The GroundFoliage part from −15/20 still reads somewhat spiky, because the outer leaves are seen edge-on.
- The trunk part is a bright orange in the open studio. The hero's trunk is shaded by the canopy and matches the sheet.

## Verification round 1 (verifier, 2026-10-29)

Fresh verifier, read-only, background Blender on port 9881 (`kit/wip/M045_verify.blend`, which also holds M042). Every
number below was re-measured with the verifier's own code (bmesh / BVH), not the builder's reports. Renders, side by
sides and scripts are in the scratchpad `m045_verify/`: `f34_sheet`, `r34_sheet`, `front_sheet`, `side_sheet`,
`rear_sheet`, `top_sheet`, `fir_*` (M042 at the same cameras), `cmp_*.png` (sheet cell | ours | 042), `cu_*.png`.

### Measured

| Object | Tris | Shells | Size (studs) | Boundary / non-manifold / wire / loose | Bowties | Zero-area / n-gons | Winding errors | Neg-volume shells | Self-isect (in shell) | Floating / unchained |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PineSapling (hero) | **2910** / 4000 (ceiling 3200) | 107 | 7.76 × 7.70 × 10.00 | 0 / 0 / 0 / 0 | 0 | 0 / 0 | **0** | 0 | 0 | **0 / 0** |
| TopTier | 470 | 13 | 3.73 × 3.78 × 3.09 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 / 0 |
| MiddleTier | 576 | 15 | 6.23 × 5.93 × 3.49 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 / 0 |
| LowerTier | 576 | 15 | 7.64 × 7.68 × 4.15 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 / 0 |
| Trunk | 348 | 1 | 3.64 × 3.97 × 4.36 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 / 0 |
| GroundFoliage | 140 | 12 | 2.21 × 2.54 × 1.37 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 / 0 |
| RockMedium | 44 | 1 | 1.83 × 1.55 × 1.27 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 / 0 |
| RockSmall | 44 | 1 | 1.03 × 0.94 × 0.78 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 / 0 |

- **Winding:** every manifold edge was checked for opposite traversal by its two faces: 0 errors on all 8 objects. Every
  shell has a positive signed volume.
- **Transforms and origin:** rotation 0, scale 1, no modifiers, no custom normals, and one clean `UVMap` on each. Each
  local bbox is symmetric in X and Y with z min 0, so the origin is at the bottom centre on all 8.
- **Contact** (the verifier's own BVH code, tolerance 0.03, chained from the ground): the hero has 107 shells, 0
  floating and 0 unchained; each part also has 0 / 0.
  - Peg seats: trunk top → lower core **0.015**, lower core → middle core **0.015**, middle core → crown core
    **0.015**.
  - No core intersects the trunk or another core, so the pegs clear the recess walls.
  - The trunk is sunk into the patch, and the rocks are sunk (they overlap it).
- **Thin triangles:** 24 under 2° (0.90–1.06°, area 0.028 each), **all on the sand patch** (shell 0). They sit on its
  0.03-high outer side wall at z 0.01–0.02 (12 segments × 2), not on the trunk as the modeller's notes say. Harmless.
- **No lighting or VFX:** no emission and no VFX children.
- **Collision:** hero `precise`; tiers, trunk and rocks `hull`; GroundFoliage `box`.
- **Plates:** the crown has 12 plates plus its core, the middle 14 and the lower 14. The slabs measure 0.27 through the
  fold centre (the 0.20 slab plus the midrib raise), so the thickness is constant (also seen in `plate_cu`).

**Shape** (the study's masks, `measure_render.py` / `tiers_r.py`, on the verifier's renders):

| View | W : H (sheet) | G / T / S / R (sheet) | Hems h / W (sheet) | Waists h / W (sheet) |
| --- | --- | --- | --- | --- |
| f34 (−15, 16) | .691 (.726) | **77.4 / 8.7 / 5.3 / 6.8** (77.2 / 10.8 / 3.1 / 7.7): all within the binding ±4 | .763/.48, .564/.81, **.342**/1.0 (.762/.50, .577/.81, .379/1.0) | .73/.42 (.73/.33); **.514/.66** (.526/.50) |
| front (0, 5) | .724 (.723) | 80.3 / 7.8 / 3.5 / 7.3 | .746/.49, .551/.82, .328/1.0 (.749/.48, .529/.81, .309) | .720/.36 (.722/.29); **.511/.57** (.486/.49) |
| side (90, 5) | .735 (.701) | 79.0 / 8.4 / 0.9 / 8.0 | .749/.47, .532/.77, .305/1.0 (.746/.48, .542/.77, .304) | .705/.39 (.723/.28); **.500/.64** (.492/.46) |
| rear (180, 5) | .744 (.724) | 74.6 / 11.8 / 1.3 / 8.6 | .748/.48, .547/.82, .318/1.0 (.746/.45, .531/.81, .312) | .720/.35 (.727/.29); .518/.53 (.492/.50) |
| r34 (165, 16) | .689 (.676) | 75.2 / 9.7 / 2.0 / 7.8 | crown hem **not found**, .571/.83, .357/1.0 (.782/.48, .560/.77, .372) | .728/.41; **.544/.72** (.512/.55) |
| top (0, 89) | 1.00 (.99) | G **97.5** / R **1.7** (85.1 / 13.3) | | |

**Colour** (medians of the same mask bands, f34, ours | sheet):

| Region | Ours | Sheet | |
| --- | --- | --- | --- |
| Crown band | #94C037 (v .75) | #5D9B3F (v .61) | lightest ✓, but much more lime than the sheet |
| Middle band | #569738 | #579335 | ✓ |
| Lower band | #4B8B3A | #508F39 | ✓ |
| Trunk right (lit) half / v > .7 | #A65C26 / #C66E2D | #B56525 / #E48230 | orange ✓, about 15 darker |
| Rock v > .7 / median | #CCBFAF / #BAAE9F | #CDC2B5 / #B0AFA7 | R ≥ G ≥ B ✓, not mauve; a little warmer than the sheet |
| Sand | #F1D3A0 | #EFD19D | ✓ |
| Plants (G below 0.2 H) | **#465913 (h 76, v .35)**; front #41530F (v .33) | #558021 (h 87, v .50); front #5C831F | dark olive against lime-green |
| Plant hue split lime / green / dark | 46 / 38 / 16 | 38 / 39 / 23 | ✓ within ±10 |

- **Colour by facing: none.**
  - Per material family, the verifier removed each shell's own position field (a plate's colour along its axis, a rock's
    by height). The residual colour then correlates with normal z at **0.09 for plates** and **−0.03 for rocks**.
  - Plate undersides are not darker than their tops: the mean top − bottom luminance is −0.06, and the axial bands
    explain it.
  - Raw correlations with height bands: rocks 0.91 (the spec's height bands, steps of about 4 %), sand 0.79 (the bevel
    role, about 1.5 %), trunk 0.39 (under 0.5).
  - `K.check` reports no problems. Stored baked-shading values: 0.00, TopTier 0.21, Trunk 0.38.
- **Tint mottling** is broad (per plate and per facet). No confetti shows in the renders.

### Findings

1. **Blocker: the three tiers don't read as three distinct tiers from the side, rear and r34.**
   - **The middle → lower waist is far too wide:** f34 .66 (sheet .50), side .64 (.46), r34 .72 (.55), front .57 (.49).
     All but the rear are outside the spec's ±.06.
   - **Why:** row B is tucked under row A, so each tier shows one ring of long plates running from the core to the hem.
     The sheet shows two visible rows per tier: an upper ring whose tips stop mid-tier over the hem row, and a dark crease
     under each hem.
   - **The result:** in `side_sheet`, `rear_sheet` and `r34_sheet` the middle and lower tiers merge into one drooping
     skirt. The tree reads as "crown + skirt", not the sheet's crisp three-step spire, and in the r34 the tier finder
     finds no crown hem at all. This is the model's defining silhouette (spec §1.1 "must read as three distinct tiers",
     pitfall 3).
   - **Fix target:**
     - Row B visible on top of each tier, its tips at about 0.5–0.6 of the tier's slope, with the row-A tips forming the
       hem below.
     - The lower tier's visible waist pulled in to W ≤ .56 in the f34, front and side views.
     - A crown hem that the tier finder detects in the r34.
     - The hems kept where they are now: they match within .02, except the f34 lower hem (finding 4).
   - **Possible routes.** Don't lift row B onto the rolled row-A edges: that made fat domes. Either:
     - shorten row A and root it further out (from r ≈ 1.3–1.5, under row B's mid-length), chained by contact to row B
       and the core; or
     - pitch row B steeper than row A, so it clears the row-A seams.
2. **Blocker (decision 4, §1.5): the plate proportions.**
   - **What:** row A on the lower and middle tiers is L : W 1.95–2.1, against the decided ≈ 1.5.
   - **How it reads:** at hero scale these plates read as long hanging blades and fingers, most clearly the side plates
     of both tiers in the f34. Close up (`plate_cu`) they are clearly thick, blunt, chisel-ended slabs. At no distance do
     they read as 042's thin pointed kites, so the §1.5 difference from 042 holds, but the decided paddle shape does not.
   - **Fix target:** a visible L : W ≤ 1.6 on every row. This follows from finding 1's two visible rows: each row covers
     about half the slope, so plates about 2.2–2.6 long and 1.6–2.0 wide.
3. **Blocker (§1.5 binding, pitfalls 4 and 9): the ground rosettes don't read as the sheet's broad-oval rosettes, and
   they look like 042's clumps.**
   - **Ours** (`cmp_base.png`, the `part_groundfoliage` render): low, splayed, dark-olive stars with pointed tips, an
     agave look. They read almost the same as 042's lanceolate clumps beside them.
   - **The sheet's:** upright fans of broad, round-tipped leaves, bright lime outside and green inside, standing taller
     than the rocks.
   - **Colour:** in the hero they are also darker than the sheet: median v .33–.35 against .50, hue 76 against 83–87.
   - **Fix target:**
     - Leaves with a rounded or blunt-oval tip, not a point, widest at 0.4–0.5 L, L : W ≈ 2.0–2.2.
     - The outer ring pitched 60–75° and the inner ring 75–85°, so the fan stands up.
     - P1 and P2 at least as tall as RS1 (≥ 1.3 visible).
     - Re-measure on `f34_sheet`: the plant median within 15 of `#558021` and the v > .7 median near `#AFC518`. The
       canopy shades the plants, so calibrate in the hero render, not the part.
4. **Minor: the f34 lower hem is at h .342,** against the sheet's .379 (outside ±.03). The near-level views match. It
   will likely move with finding 1. Target ±.03.
5. **Minor: the crown is too lime.** Its band median is #94C037 (v .75) against the sheet's #5D9B3F (v .61), so the crown
   reads as a separate yellow cap.
   - Target: lower the crown's offsets by one step (for example the long plates 0 / +.25 / +.5, and the upper plates the
     same).
   - Keep the crown lighter than the lower tier, with the crown band median within 20 of #5D9B3F.
6. **Minor: the bark is a little dark.** The lit half is #A65C26 against #B56525 (about 15 off; the spec allows 12), and
   the v > .7 median is #C66E2D against #E48230. The front view's trunk falls to #83471C under the canopy. Target: raise
   `m045_bark` about 6 % if the plates change the shading.
7. **Minor: the top view.** The canopy is a rounded rosette (G 97.5 %, R 1.7 %) with no 8-point star outline. No rocks or
   plants show beyond the canopy (sheet G 85 / R 13). The crown's 4-point star does read. A narrower, shorter row A
   (findings 1 and 2) should help. It isn't binding on its own (spec §3.3).
8. **Minor: the canopy tips reach r 3.8, against the decided r 3.5** (decision 1). The front W : H .72 is still in range,
   and the hero is 7.7 deep. Acceptable as recorded; re-check after finding 1.
9. **Minor: the rocks are a touch warm.** The median is #BAAE9F (hue 33°, sat .15) against the sheet's near-neutral
   #B0AFA7.
   - They meet the spec's lit target (#CCBFAF against #CEC0B4), are R ≥ G ≥ B and are never mauve.
   - RockMedium is a chunky faceted block with a flat base, not an egg.
   - No change required.
10. **Minor: the 24 thin triangles are on the patch's 0.03-high side wall,** not the trunk; the modeller's notes
    misattribute them. They are harmless at ground level. Optional fix: drop the side wall so the bevel runs straight to
    z 0.
11. **Passed:**
    - the budgets, every mesh-hygiene check and the winding;
    - floating dressing 0;
    - the peg-and-recess seats of 0.015 with a square, diamond-turned recess (`join_cu` matches close-up 1);
    - the constant 0.20 slab thickness with chisel ends (`plate_cu` matches close-up 2);
    - the smooth, tapered 8-sided trunk with its knots and 6 blunt flares, which read in the f34, front, side and r34
      and in `underside_cu`;
    - the f34 shares, within ±4;
    - the colour families (canopy, orange bark, R ≥ G ≥ B rock, sand), with nothing coloured by facing;
    - no lighting and no VFX.

    **Decisions:**
    - 1, 2, 3, 5, 6, 7, 8, 10, 12, 13, 14 and 15 were followed.
    - 4 was missed on L : W (finding 2).
    - 9 was missed on "broad-oval rosettes" (finding 3).
    - 11 was followed, but the crown is too lime (finding 5).
12. **§1.5 against M042, side by side** (`cmp_f34.png`, `cmp_side.png`):
    - **It differs on:** size (10 against 16); thick, blunt slabs against thin, pointed kites; the smooth trunk with
      blunt flares against planks and kinked roots; the peg joints; and the bark.
    - **It doesn't differ on the ground plants** (finding 3).
    - Both canopies also use the same construction, one ring of long plates per tier, which brings them closer together
      than the two sheets are. Finding 1 fixes that.

**Score: 6 / 10.** The mesh, contact and colour discipline are clean. The defining tier read and the rosettes do not yet
match the sheet.

**Verdict: FAIL.** Blockers 1–3 go back to a fresh modeller: the stage 1 tier construction and the rosette leaves, then
a stage 4 re-measure of the plants and the crown.

## Fix round 1 (fix modeller, 2026-10-29)

A fresh fix modeller worked in a background Blender on port 9881 (`kit/wip/M045.blend`, saved after the final build).
`m045.py` was edited. The final check ran in a freshly restarted session, and `build()`'s problems list is empty.
Scratch work and measuring scripts are in the scratchpad folder `m045fix/`:
- `it.py`: the tuning loop.
- `env.py`: silhouette envelopes.
- `meas.sh`: `tiers_r.py` on all five side views.
- `col.sh`: the verifier's `bands.py` plus `col.py`.
- `prof.py`: width profiles.
- `cmp_042.png`: the side-by-side with M042.

### What changed

1. **Two visible rings per tier (blocker 1).** Round 1 tucked row B under row A, so each tier was one ring of long
   plates, and the middle and lower tiers merged into one skirt. The lower and middle tiers are now built like this:
   - **Row B (the upper ring, 7 plates over the A seams) is built first and lies on top.**
     - Its roots are buried in the core. The core's pleated widest ring now reaches out to the waist: lower r 1.65 at
       z 4.6, middle r 0.98 at z 7.0.
     - The plates leave the core just under the hem above, at their narrow roots, so the waist stays narrow.
     - The tips stop at about 0.55 of the tier's slope: lower z 3.9, middle z 6.3.
     - The rows are steep: about 42° on the lower tier and 45° on the middle.
   - **Row A (the hem ring, 7 plates, one aimed at the front) is built second, as a sink row.**
     - It lies about 0.36 (normal) under row B's line and is rooted in the core's underside.
     - A plate that still cuts row B is first turned down (`tip_first`), then moved whole.
     - Its tips form the hem. The plate bends up 16-18° at 0.45 L, a slight flare, so the hem reaches the sheet's width
       without widening the waist. Its chisel tip droops 14° at 0.78 L.
   - **New plate mode.** `plate(..., length=L)` lays the unbent inner part from the root toward an aim point, L long,
     so both rows are parallel layers. `droop` may also be a pair: the bend at 0.45 L and the bend at 0.78 L.
   - **Rolls.** Row B rolls only 0-6°, because the rings barely overlap. Aim rows may roll up to +24° before any
     narrowing.
   - **Midrib fold.** `RIDGE` is now 0.08 W (spec 0.07; round 1 had 0.11), which leaves room for the stacking.
   - **Crown.** It keeps its round-1 construction: 4 long hem plates, 4 short and 4 upper on the star cone. The long hem
     plates are now 1.38 wide (was 1.3), and the front one's tip is at 7.15 (was 7.05).
   - **Hems held.** The lower row A aims at z 3.2 and the middle at 4.62. With the flare and droop, the hems land at
     front h .317 / .560.
2. **Plate proportions (blocker 2).** These follow from the two rings: every plate is about half the slope long.
   - Whole-slab L : W per plate, root to tip including the buried root, from the build log:

     | Row | L : W |
     | --- | --- |
     | Lower B | 1.34-1.50 |
     | Lower A | 1.48-1.58 |
     | Middle B | 1.32-1.49 |
     | Middle A | 1.36-1.58 |
     | Crown | 1.21-1.57 |

   - The visible part is shorter: the roots are buried 0.2-0.4 in the core, and row A's upper part is under row B.
   - The plates are still 0.20-thick constant slabs with chisel tips.
3. **Ground rosettes (blocker 3).**
   - **Leaf shape.** `_leaf12` is now a 14-tri **round-tipped oval**: widest (W) at 0.42 L, 0.84 W at 0.8 L, then a
     short blunt end 0.34 W wide, with no point. L : W is 2.0 (`LEAF_LW`), and the midrib fold is 22°.
   - **Pitch.**
     - The outer ring is pitched 60-72° and arches out at the tip (curl 0.26-0.34 L). The length is compensated, so the
       fan keeps its height.
     - The inner ring is pitched 75-85°.
     - P1 and P2 are 1.6 tall.
   - **Roles.** The outer ring is 2-3 lime leaves plus green ones, and the inner ring is dark and green. Each leaf's base
     is a step deeper.
   - **Colour.** The keys were recalibrated on the hero f34 render:
     - `m045_plant_deep` #62AA40 (was #436B25);
     - `m045_plant_dark` #2E7C48 (was #2A5A2C);
     - `m045_plant` #879C1A, unchanged.
   - **Leaf count.** 51 leaves; P4 and S3 still each drop one at a rock.
4. **Minors.**
   - **Crown colour.** The cone is `needle_light` 25 % (was 75 %), and the crown plate bands are one to two steps darker.
   - **Bark.** `m045_bark` is #BA6C26 (was #B06624).
   - **Dark crease under each hem.** Row B's root band is 75 % deep on the lower tier and 50 % on the middle. This is
     colour by position, not by facing.
   - **Hem tips.** Lower row A's tip band is +0.5 light (was +0.25).
   - **Winding check.** `shells_report` now counts winding errors per shell (a manifold edge walked the same way by both
     faces), and `check()` lists any in its problems.
   - **Target size.** `TARGET_SIZE` is 7.6 ± 0.4 × 7.3 ± 0.4 × 10.0 ± 0.2.

### Measured (final build, fresh session)

| Check | Round 1 | Fix round 1 | Target |
| --- | --- | --- | --- |
| Lower waist W: f34 / front / side / rear / r34 | .66 / .57 / .64 / .53 / .72 | **.55 / .49 / .47 / .42 / .50** | ≤ .56 in every view (sheet .50 / .49 / .46 / .50 / .55) |
| Crown hem in the r34 | not found | **h .754 / W .48** | found (sheet .782 / .48) |
| Front hems h (crown / middle / lower) | .749 / .551 / .326 | .746 / .560 / .317 | keep .749 / .551 / .326 (sheet .749 / .529 / .309) |
| Side, rear and r34 hems h (middle; lower) | .532; .305 / .547; .318 / .571; .357 | .570; .32 / .557; .32 / .580; .326 | sheet .542; .304 / .531; .312 / .560; .372 |
| f34 hems h (crown / middle / lower) | .763 / .564 / .342 | .763 / .560 / .323 | sheet .762 / .577 / .379 (minor) |
| Middle hem W: f34 / front / side / rear / r34 | .81 / .82 / .77 / .82 / .83 | .73 / .79 / .74 / .80 / .74 | sheet .81 / .81 / .77 / .81 / .77 |
| Crown waist W: front / side / rear | .36 / .39 / .35 | .37 / .41 / .37 | sheet .29 / .28 / .29 |
| Canopy W / H: front / side | .720 / .731 | .694 / .697 | 0.68-0.74 |
| Plate L : W (whole slab) | row A 1.95-2.1 | **1.21-1.58** | ≤ 1.6 on every row |
| Deepest plate cut (hero / parts) | 0.048 | 0.049 / ≤ 0.049 | ≤ 0.05 |
| Rosette leaf | pointed, L : W 1.55, pitch 46-58 / 64-78° | **round tip, L : W 2.0, pitch 60-72 / 75-85°** | round, 2.0-2.2, 60-85° |
| P1 / P2 top z against the rocks | 1.37 (part) | **1.59 / 1.58**, against RM 1.31 and RS1 1.06 | at least as tall as the rocks |
| f34 plants: median / v > .7 | #465913 / — | **#54751D** (Δ 1, 11, 4) / #A1C722 | median within 15 of #558021; v > .7 near #AFC518 |
| Plant split lime / green / dark | 46 / 38 / 16 | 42 / 44 / 14 | 38 / 39 / 23 ± 10 |
| f34 crown band | #94C037 | **#5B9937** | within 20 of #5D9B3F, and lighter than the lower band (#4C8836 ✓) |
| f34 middle / lower bands | #569738 / #4B8B3A | #589736 / #4C8836 | #579335 / #508F39 |
| f34 canopy: median / v > .7 | #529535 / #9FC835 | #599836 / #A0CB35 | #519037 ± 15 / #A5C935 ± 12 |
| f34 bark: lit half / v > .7 | #A65C26 / #C66E2D | #BD692C / #D0752F (`col.py`) | #B56525-#BF6926 / #E48230 |
| f34 rock v > .7 | #CCBFAF | #CDC5B0 | #CDC2B5, R ≥ G ≥ B |
| f34 shares G / T / S / R | 77.4 / 8.7 / 5.3 / 6.8 | 74.6 / 9.5 / 5.6 / 8.4 | 77.2 / 10.8 / 3.1 / 7.7 (binding ± 4) |
| Hero tris | 2910 | 3012 | ≤ 3200 ceiling |
| Hero size | 7.76 × 7.70 × 10.00 | 7.65 × 7.47 × 10.00 | canopy tips toward r 3.5 (now r 3.6-3.8) |

- **Tris.**
  - Hero 3012: plates 1360, leaves 714, trunk 348, cores 262, rocks 176, patch 96, hubs 56.
  - Parts: TopTier 470, MiddleTier 576, LowerTier 576, Trunk 348, GroundFoliage 162, RockMedium 44, RockSmall 44. All
    are under 1000.
- **Mesh checks, every object.**
  - Non-manifold edges, bowtie verts, boundary, wire, loose, zero-area, n-gons and duplicate verts are all 0.
  - Normals are outward and transforms applied. The origin is at the bbox bottom centre; the hero's offset is
    (0.14, −0.17, 0).
  - Per shell: every shell is closed with a positive volume, with 0 self-intersections and **0 winding errors** (the new
    check).
  - The hero still has 24 thin triangles (0.9°) on the sand patch's 0.03-high side wall. This is unchanged (verifier
    finding 10).
- **Contact.**
  - The hero has 107 shells: patch 1, trunk 1, cores 3, plates 40, rocks 4, hubs 7, leaves 51. Floating 0, unchained 0.
  - Core seats are 0.015 / 0.015 / 0.015, with 0 core or trunk intersections.
  - 0 plate pairs cut more than 0.05 (deepest 0.049), and 0 leaves cut a rock or the trunk.
  - Each tier part and GroundFoliage: floating 0, unchained 0.
- **UV, every object:** 0 overlapping pairs, 0 flipped, minimum island gap 0.016, border 0.008, conformal stretch p95
  1.00-1.03.
- **`K.check`:** no problems. Baked-shading correlations: hero 0.00, tiers 0.00, Trunk 0.38, GroundFoliage 0.02.
- **Lighting and VFX:** none (unchanged).

### Compared with the sheet and with M042

- **Front, side, rear and r34.** The tree shows three distinct steps: the crown hem, the middle hem and the lower hem.
  Each tier shows an upper ring whose tips lie over the hem ring, with a dark band under each hem. The hem plates flare
  a little and droop at the tip.
- **Against M042** (`cmp_042.png` in the scratchpad: sheet | 045 | M042 at the f34, side and top). They read as
  different kit pieces:
  - 045: broad, round-ended slabs in two rings per tier, on a smooth flared trunk, with upright broad-leaf fans.
  - 042: one ring of thin, pointed kites per tier, with spiky lanceolate clumps.
- **Top view.**
  - The outline has 7 points, because row A has 7 plates (the spec decided 7 + 7), with row B between them.
  - The 4-point crown star shows, with a ridge at −Y.
  - A corner of RM and a little of P4 show beyond the canopy.
  - Shares are G 96 / R 2 / S 1 (sheet 85 / 13); the sheet's top cell draws the canopy smaller (§3.3).

### Leftovers

- On the f34, the middle hem is .73 wide (sheet .81) and the lower hem sits at h .323 (sheet .379). The near-level
  views match better.
- In the front and side views, the middle hem is .03-.04 higher than the sheet's.
- The crown waist is .37-.41 (sheet .28-.29), as in round 1.
- The f34 G share is 74.6 (sheet 77.2), inside the binding ± 4. S is 5.6, above the spec's 5.1 maximum (± 2).
- The side and rear canopy medians read darker than the sheet (#437429 against #5B9635), as in round 1 (the studio
  light).
- From −15 / 20, the GroundFoliage part still shows one or two outer leaves edge-on. In the hero, the fans read as
  upright broad leaves.
- The top view shows 7 outer points, not 8, and the rocks and plants barely show beyond the canopy.

## Verification round 2 (verifier, 2026-10-29)

Fresh verifier, read-only, background Blender on port 9881 (`kit/wip/M045_verify.blend`, the fixed and integrated
model plus M042 `TieredFir` and M047). Nothing was built, edited or saved. Every number below comes from the verifier's
own scripts (bmesh / BVH / ray parity in Blender, and the study's `m.py` masks with the verifier's own profile and
colour code on the images). Renders, side-by-sides and scripts are in the scratchpad folder `m045_verify2/`:
- renders: `f34_sheet`, `r34_sheet`, `front_sheet`, `side_sheet`, `rear_sheet`, `top_sheet`, `fir_*` (M042 at the same
  cameras), `part_*`;
- side by sides: `cmp_f34`, `cmp_side`, `cmp_top` (sheet | 045 | 042), `cmp_r34`, `cmp_front_rear`, `cmp_parts`,
  `cmp_gf`, `cmp_base`, `cmp_cu`;
- scripts: `mesh.py`, `contact.py`, `plates2.py`, `roots.py`, `leaves.py`, `facing.py`, `prof.py`, `col.py`.

### Measured

**Mesh** (every object; a winding error is a manifold edge walked the same way by both faces):

| Object | Tris | Shells | Size | Bnd / NM / wire / loose | Bowties | Zero-area / n-gons | Winding | Neg-vol shells | Self-isect in shell | Floating / unchained |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PineSapling | **3012** / 4000 (ceiling 3200) | 107 | 7.65 × 7.47 × 10.00 | 0 / 0 / 0 / 0 | 0 | 0 / 0 | **0** | 0 | 0 | **0 / 0** |
| TopTier | 470 | 13 | 3.67 × 3.72 × 2.99 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 / 0 |
| MiddleTier | 576 | 15 | 5.77 × 5.45 × 3.39 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 / 0 |
| LowerTier | 576 | 15 | 7.55 × 7.46 × 4.11 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 / 0 |
| Trunk | 348 | 1 | 3.64 × 3.97 × 4.36 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | — |
| GroundFoliage | 162 | 12 | 2.19 × 2.64 × 1.50 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 / 0 |
| RockMedium | 44 | 1 | 1.83 × 1.55 × 1.27 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | — |
| RockSmall | 44 | 1 | 1.03 × 0.94 × 0.78 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | — |

- **Faces and transforms:**
  - All faces are triangles.
  - Rotation 0, scale 1, no modifiers, no custom normals, one `UVMap`.
  - The local bbox is centred in X / Y with z min 0 on all 8, so the origin is at the bottom centre.
  - Normals are outward: every shell has a positive volume and 0 winding errors.
- **Hero shells:** patch 1, trunk 1, cores 3, plates 40 (lower 7 + 7, middle 7 + 7, crown 4 upper + 4 short + 4 long),
  rocks 4, hubs 7 (4 rosettes + 3 sprigs), leaves 51.
- **Peg seats:** trunk top → lower core **0.015**, lower peg → middle core **0.015**, middle peg → crown core
  **0.015**, with no overlap between any of them.
- **Plate cuts:**
  - 44 plate pairs touch in the hero. The deepest cut is **0.049**; it is 0.053 only if samples hidden inside a core
    are counted.
  - 0 pairs cut more than 0.05. The parts' deepest cuts are 0.049 / 0.045 / 0.049.
  - No leaf cuts a rock or the trunk.
- **Plate roots:** every plate overlaps its core. Buried depth: lower 0.22–0.36, middle B 0.18–0.25, middle A
  0.115–0.14 (just under the spec's 0.15), crown 0.05–0.30.
- **Thin triangles:** 24 under 2°, all on the patch's 0.03-high side wall (unchanged from round 1).
- **Collision:** hero `precise`; tiers, trunk and rocks `hull`; GroundFoliage `box`. No emission, no VFX children.

**Plates** (per shell; L = root centroid to tip centroid, W = the widest point across):

| Row | L : W (whole slab) | L : W outside the core | Tip r / z | Through-slab thickness (median / p90) |
| --- | --- | --- | --- | --- |
| Lower A (hem) | 1.46–1.57 | 1.14–1.23 | 3.62–3.87 / 2.56–2.94 | 0.26 / 0.31 |
| Lower B (upper) | 1.34–1.49 | 1.04–1.16 | 2.50–2.63 / 3.77–3.88 | 0.25 / 0.28 |
| Middle A | 1.34–1.56 | 1.34–1.56 | 2.60–2.86 / 5.02–5.38 | 0.25 / 0.29 |
| Middle B | 1.28–1.48 | 1.08–1.19 | 1.91–2.02 / 6.19–6.42 | 0.24 / 0.27 |
| Crown (12) | 1.13–1.49 | 0.91–1.55 | 1.18–1.82 / 7.26–8.43 | 0.23–0.24 / 0.26–0.28 |

The walls are 0.20; the through-slab figure includes the midrib raise (0.08 W). Max L : W is **1.57** (target ≤ 1.6).

**Silhouette** (study masks, the verifier's own width profile; canopy rows above h .22):

| View | W : H canopy (sheet) | Crown hem h / W | Crown waist W | Middle hem h / W | **Lower waist W** | Lower hem h |
| --- | --- | --- | --- | --- | --- | --- |
| f34 | .667 (.651) | .763 / .48 (.762 / .50) | .41 (.33) | .569 / **.73** (.577 / .81) | **.53** (.50) | **.326** (.382) |
| r34 | .683 (.618) | **.756 / .48 found** (.785 / .48) | .38 (.34) | .585 / .74 (.560 / .77) | **.50** (.54) | .324 (.375) |
| front | .690 (.714) | .745 / .50 (.745 / .49) | .36 (.29) | .561 / .79 (.529 / .81) | **.49** (.48) | .316 (.313) |
| side | .692 (.700) | .747 / .50 (.746 / .48) | .42 (.28) | .572 / .74 (.542 / .77) | **.47** (.45) | .323 (.308) |
| rear | .695 (.708) | .747 / .50 (.746 / .45) | .36 (.28) | .561 / .79 (.535 / .81) | **.42** (.48) | .312 (.315) |

- **Two rings on each lower and middle tier.** Row B's tips sit over row A's hem tips:

  | Tier | Row B tips (r / z) | Row A hem tips (r / z) |
  | --- | --- | --- |
  | Lower | 2.5–2.6 / 3.8–3.9 | 3.6–3.9 / 2.6–2.9 |
  | Middle | 1.9–2.0 / 6.2–6.4 | 2.6–2.9 / 5.0–5.4 |

- **Trunk widths** (front view, as a fraction of the canopy W):

  | h | .25 | .20 | .15 | .10 |
  | --- | --- | --- | --- | --- |
  | Ours | .186 | .214 | .276 | .300 |
  | Sheet | .178 | .195 | .227 | .303 |

**Ground rosettes** (per leaf, the verifier's own mesh code):
- Leaf L : W **2.03–2.20**; blunt end 0.33–0.34 W wide (a round-tipped oval, no point).
- **Pitch of the inner part:**

  | Group | Outer ring | Inner ring |
  | --- | --- | --- |
  | P1 / P2 | 56–67° | 85–90° |
  | P3 / P4 | 56–65° | 85–89° |
  | Sprigs | 62–81° | |

- **Tops:** **P1 1.59, P2 1.58**, P3 1.25, P4 1.13, sprigs 0.75–0.99. Rocks: RM 1.31, RS1 1.06, RS2 0.82, RS3 0.70.

**Colour** (f34 unless named; ours | sheet):

| Region | Ours | Sheet | |
| --- | --- | --- | --- |
| Canopy median / v > .7 | #579836 / #A0CB35 | #529037 / #A5C935 | ✓ / ✓ |
| Crown band / middle / lower | **#5B9937** (v .60) / #589736 (v .59) / #4A8836 (v .53) | #5D9B3F / #579335 / #508F39 | crown within 6 of the sheet; lighter than the lower ✓ |
| Trunk lit (right) half / v > .7 | #BD692C (h 25) / #D1742F | #BF6926 / #E48230 | orange ✓; v > .7 a little dark |
| Rock v > .7 / median | #CCC1B0 (h 36, s .14) / #BBB1A0 | #CDC2B5 / #B0AFA7 | R ≥ G ≥ B ✓, not mauve; median a touch warm |
| Sand | #F1D3A0 | #EFD19D | ✓ |
| **Plants median** / v > .7 | **#52751D** (Δ 3, 11, 4) / #A7C81E | #558021 / #AFC618 | within 15 ✓ |
| Plants, front cell | #3F621B | #5C831F | darker (shaded by the canopy) |
| Plant split lime / green / dark | 41 / 43 / 15 | 38 / 39 / 23 | ✓ ±10 |
| **Shares G / T / S / R** | **75.1 / 9.6 / 5.7 / 7.6** | 77.2 / 10.8 / 3.1 / 7.7 | all within the binding ±4 |

- **Other views** (canopy median, ours | sheet):

  | View | Ours | Sheet | |
  | --- | --- | --- | --- |
  | Front | #529032 | #508F38 | ✓ |
  | Side | #427329 | #639A36 | darker |
  | Rear | #457A2C | #539337 | darker |
  | r34 | #437A2C | #5A9636 | darker |

  The studio light leaves the near-level and rear views darker, as in round 1.
- **Colour by facing: none.**
  - `K.check` returns no problems. Baked-shading values: hero 0.00, tiers 0.00, Trunk 0.38, GroundFoliage 0.02.
  - Over the hero, face key luminance correlates with normal z at −0.09.
  - Per plate, the up-facing faces are on average 0.065 *darker* than the down-facing ones, so there are no dark
    undersides. Rocks: +0.05, from the spec's height bands.
  - The builder has no `normal`-based paint selection. A `grep` finds only `recalc_face_normals` and leaf geometry.
  - Plate colour comes from `plate(..., tones=(root, middle, tip))` bands along the plate. Row B's darker root band
    (lower −0.75, middle −0.5) is therefore chosen by position.

### Findings

**Round-1 blockers, re-checked:**
1. **Distinct tiers: fixed.**
   - The lower waist is .42–.53 in every view (target ≤ .56).
   - The crown hem is found in the r34 (.756 / .48).
   - Each lower and middle tier shows two rings: row B on top, its tips over the row A hem.
   - The front, side, rear and r34 outlines step in three times.
   - The f34 interior reads as many rows of short scales, but its outline still steps at the crown, middle and lower
     hems.
2. **Plate proportions: fixed.** L : W is ≤ 1.57 on every plate (1.04–1.56 outside the core). The plates have 0.20
   walls, chisel ends and a midrib fold. `plate_cu` and `cmp_parts` show thick blunt slabs.
3. **Ground rosettes: fixed.**
   - The leaves are round-tipped ovals, L : W 2.03–2.2, standing up (inner rings 85–90°).
   - P1 and P2 are 1.58–1.59 tall, above every rock.
   - The f34 plant median is within 15 of `#558021`.
   - In `cmp_f34`, `cmp_side` and `cmp_base`, 045's upright broad-leaf fans read clearly unlike 042's spiky lanceolate
     stars.

**§1.5 against M042, side by side** (`cmp_f34`, `cmp_side`, `cmp_top`, `cmp_base`). They are different kit pieces on
every binding point:

| | 045 Pine Sapling | 042 Young Fir |
| --- | --- | --- |
| Height | 10 | 16 |
| Plates | 0.20 blunt slabs, two rings per tier | thin pointed kites |
| Joints | peg and recess | flat caps and hubs |
| Trunk | smooth, flared, 6 short flares | planked, long roots |
| Ground plants | broad-leaf fans | lanceolate clumps |
| Rocks | pale, neutral | warm beige |

Only the top views stay alike: both are a rounded rosette of plates round a 4 + 4 crown star.

**Remaining, all minor:**
1. **Minor: the f34 middle hem is .73 wide** (sheet .81, tolerance ±.05). The r34 and side read .74 (sheet .77), and
   the front and rear .79 (.81).
   - Fix target: an f34 middle hem of at least .77.
   - For example, make the middle row A's side plates 5–8 % longer, or flare them 3–4° more.
2. **Minor: the f34 and r34 lower hems sit at h .326 and .324** (sheet .382 and .375).
   - The front, side and rear match within .015 (.316 / .323 / .312).
   - The sheet's hero cells are perspective drawings, so no change is required.
3. **Minor: the crown waist is .36–.42** (sheet .28–.34), so the step from the crown to the middle tier is shallower
   than the sheet's.
   - Fix target: ≤ .34.
   - Either start the middle row B 0.1–0.15 lower, or root it 0.1 further in.
4. **Minor: the middle hem sits .025–.03 high** in the front, side, rear and r34 (front .561 against .529). The target
   is ±.03, and it is at the edge.
5. **Minor: the profile plates read as thin fingers.**
   - What: the middle and lower row A plates seen lengthwise, at the left and right edges of the f34 and side views,
     show as thin horizontal sticks.
   - Why: their flat tops are edge-on to the camera.
   - Fix target: roll those plates 10–15° more, or pitch the hem row 5° steeper, so their folded top shows in profile.
6. **Minor: every plate has a lime tip band,** so the f34 reads as six even rows of scales rather than three skirts.
   - Fix target (optional): give the lower tier's row B a tip band of +0.25 instead of +0.5, so the hem rows carry the
     light.
7. **Minor: sand is 5.7 %** of the f34 (sheet 3.1). That meets the binding ±4 but not the spec's ±2.
   - Optional: pull the patch outline in 0.15–0.2 at the front lobes.
8. **Minor: the top view.** It has 7 outer points against the study's "about 8"; row A has 7 plates, as decided.
   - Shares are G 96.7 / R 1.9 / S 1.1 against the sheet's 85 / 13.
   - Accepted under §3.3; no change.
9. **Minor: the GroundFoliage part** seen from −15 / 20 (`cmp_gf`) shows two outer leaves edge-on as spikes. In the
   hero, the fans read as broad upright leaves.
   - Optional: yaw the part's outer ring 15–20°, so no leaf is edge-on to the part camera.
10. **Minor: the front cell's plants** read darker than the sheet's (#3F621B against #5C831F), because the canopy shades
    them. The f34 meets the target.
11. **Minor: the trunk and rock colours are a little off.** No change is required.
    - The trunk's v > .7 median is #D1742F against #E48230; the lit half matches.
    - The rock median is a touch warm (#BBB1A0 against #B0AFA7).
12. **Minor, carried over:**
    - The row-A tips reach r 3.6–3.9, against the decided 3.5. The canopy W : H is still in range.
    - A few outer rosette leaves are pitched 56–59° (target 60–85°).
    - The middle row A roots are buried 0.115–0.14 (spec 0.15–0.3), but they chain.
    - 24 thin triangles remain on the patch side wall.

**Passed:**
- the budgets (3012 of 3200; every part ≤ 576);
- every mesh check, with **0 winding errors**;
- 0 floating or unchained shells;
- the three 0.015 peg seats;
- plate cuts ≤ 0.049;
- the f34 shares, within ±4;
- the colour families:
  - the canopy, with the crown lighter than the lower tier and within 6 of the sheet's crown;
  - orange bark;
  - R ≥ G ≥ B rock that is never mauve;
  - sand;
  - the plants;
- nothing coloured by facing;
- no lighting or VFX.

**Decisions:** 1–15 are all followed.
- Decision 1's tip radius (3.5) is exceeded by 0.1–0.4. This was recorded and accepted in round 1.
- Decision 4 is now met: L : W ≤ 1.57, plate counts 4 + 8 / 7 + 7 / 7 + 7, and one plate at the front on every tier.
- Decision 9's rosettes are now broad ovals.

**Score: 8 / 10.** The mesh, contact and colour discipline are clean. The three blockers are fixed, and the model
differs from 042. What is left:
- the tiers are less crisp in the f34 (the middle hem's width and the shallow crown waist);
- the profile plates read as thin fingers.

**Verdict: PASS.** Commit with the minors above noted.

## Main session ruling (2026-10-29)
- **Result:** passed in round 2 (8/10) and committed. Round 1 failed (6/10): the tiers merged, the plates were long blades, and the rosettes looked like 042's.
- **Left for a later polish pass:**
  - The f34 middle hem is .73 wide; target ≥ .77.
  - The crown waist is .36–.42; target ≤ .34.
  - Side-on plates read as thin sticks.
  - Every plate has a lime tip band that reads as rows of scales. Use +0.25 on the lower row B.
  - Sand is 5.7 %.
  - Two edge-on leaves on GroundFoliage.
  - The trunk highlight is slightly dark.
- **Export:** 8 assets, 8 solid pieces, 5232 tris, 0 VFX sockets, palette 23 colours, 0 problems.
