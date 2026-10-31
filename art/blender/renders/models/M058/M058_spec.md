# 058 Low Bush — spec

Reference: `art/blender/assets/references/058.png` (1024 × 1536 px). INDEX.md row 58: "Flintborn Low Bush Study". The
sheet's own header reads **"57 / 132"**, title **"LOW BUSH"**, footer "FLINTBORN — INDIVIDUAL MODEL STUDY" / "PAGE 57/132"
(our number is INDEX's 058, §3.1).
Builder: `art/blender/kit/mcp/m058.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows no effect** (§7). The tree rule
(memory `kit-tree-detail`) applies to this shrub: **build the skeleton first (a forked branch stem with flat cut tips),
then hang leaf clumps on the tips.** The stem must still read through the crown's lower window in the front, rear and
three-quarter views (the sheet shows 7–9 % wood in every side view, §1.2).

Sheet text (paraphrased):
- **Description (top centre):** thick, faceted, leafy bushes with big clumps and simple branch stems, used on the forest
  floor, along paths and in ruins.
- **"MATERIAL PALETTE"** (top right, five swatches): LEAF DARK, LEAF MID, LEAF LIGHT, ROCK, WOOD.
- **"ASSEMBLED VIEWS":** "FRONT THREE QUARTER" and "REAR THREE QUARTER".
- **"ORTHOGRAPHIC VIEWS":** "FRONT", "SIDE (RIGHT)", "REAR", "TOP".
- **"EXPLODED CONSTRUCTION":** labels "Leaf Clump (large)", "Leaf Clump (medium)", "Leaf Clump (small)", "Flower
  (optional)", "Branch Stem (base)", "Ground Leaves (optional)", "Rock (base)". Drawn: one forked branch stem with six
  flat-cut tips; four leaf clumps (large, medium, small and an unlabelled tiny one) and two flowers, each dashed to a
  tip; the stem's base among rocks, ground-leaf pads, two tan pebbles and a small leaf sprig on the pale ground.
- **"KEY CONSTRUCTION CLOSE UPS":**
  1. "Branch to Leaf Attachment": leaf clumps sit on branch tips; the pivot is at the base of the clump, for slight
     rotation and variation.
  2. "Leaf Clump Underside": a simple faceted volume with a flat underside; consistent thickness; clean low-poly shapes
     with broad faces.
  3. "Rock and Ground Detail": rocks sit on the ground; ground leaves overlap rocks and soil; clean intersections, no
     small gaps.
- **"REUSABLE PARTS (ISOLATED)":** Leaf Clump (large), Leaf Clump (medium), Leaf Clump (small), Branch Stem (base), Rock
  (base), Ground Leaves (optional), Flower (optional).
- **"MODELING NOTES":** chunky low-poly stylised forms; broad flat-shaded faces with no texture noise; simple clean
  silhouettes; reuse leaf clumps, rocks and ground leaves across variations; leaf clumps attach to branch tips at a
  pivot; rocks and ground leaves are separate pieces; flowers are optional, for variation; keep the proportions and style
  of the Flintborn foliage assets.
- **Game context and the old kit:**
  - **W06 row 1 `LowBush`** (`art/blender/scripts/kit/W06/low_bush.py`; manifest `art/roblox/kit/W06/manifest.json`) is
    the old kit's take on this sheet: about 6 × 6 × 4.5, 3223 tris, hull collision, a `harvest_hit` socket. Its parts
    and variants are `LowBushLeafClumpLarge`, `…Medium`, `…Small`, `LowBushBranchStem`, `LowBushBranchStemB`,
    `LowBushBerries`, `LowBushFlower`, `LowBushDome`, `LowBushHedge`, `LowBushOpenWoody`. `MODEL_PROGRESS.md` row 64
    says: "flat saturated blob; few flowers; variants off". **W06 owns every `LowBush*` name** (§8).
  - **Related models:** 054 Broadleaf Tree (`ShadeTree`, lobed leaf cards over dark cores); the rim bushes of 040, 043,
    044 and 046 (2–3-stud dome bushes); 017 Berry Bush (`BerryBushNode`, a 3.6-tall forage shrub). §1.5 keeps 058 apart
    from them.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Paper `#F8F4EC` (248, 244,
236), tolerance 12. Measured grey rules: assembled frame y 119–120 / 482–483; ortho frame y 493 / 750–751, cell dividers
x 277, 503, 767–768; exploded frame y 761 / 1262, x 10 / 638–639; parts frame y 1271–1272 / 1478–1479, x 10 / 715 |
725–726 (notes).
- **Cells** (`m.V`, `m.X` in the study folder): f34 (15,125,515,456); r34 (515,125,1008,456); front (12,531,276,722);
  side (278,531,502,722); rear (504,531,766,722); top (769,531,1010,722); exploded (11,790,637,1261); cu1 "branch to leaf"
  (651,800,859,945); cu2 "underside" (651,958,859,1100); cu3 "rock and ground" (651,1110,859,1250); parts row
  (11,1300,715,1425).
- **Swatches** (inner boxes of the rounded squares, sd ≤ 1.8): LEAF DARK (776,50,802,80), LEAF MID (821,50,850,80), LEAF
  LIGHT (867,50,896,80), ROCK (914,50,943,80), WOOD (961,50,990,80).
- **Masks** are `cls8()` and `sil8()` in `m.py` (HSV, h in degrees, assigned in this order):
  - **Y**, flower centre: h 38–58, s ≥ 0.55, v ≥ 0.80.
  - **R**, rock. Either lit warm facets (s 0.11–0.32, h < 48, v 0.55–0.935) or cool shade facets (s 0.04–0.30, h ≥ 195
    or < 12, v 0.25–0.80).
  - **X**, cast shadow, ground halo and soil: s < 0.07 with v ≥ 0.72; or s < 0.13 with v ≥ 0.90; or any other low-sat
    grey. The pale warm soil halo `#F5E8D8` falls here.
  - **G**, green: h 50–180, s ≥ 0.30, v ≥ 0.10.
  - **T**, wood: h < 50, s ≥ 0.30, v ≥ 0.10.
  - **O**, other: outlines, the near-black crown interior.
  - **W**, petals and enclosed sky gaps: near-white pixels (v ≥ 0.90, s < 0.12) enclosed by the silhouette above h .20.
  - **Limit.** The brightest rock tops (v ≥ .935) are lost to the soil halo, so R measures the mid and shade facets only.
    Apply the same masks to our renders, floor hidden, so the comparison stays fair.
  - **Canopy and ground green.** Canopy = G at h ≥ .15; ground green = G below h .15.

**Scratch study material** (no Blender) in
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m058_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe`.
- **Helpers:** `m.py` (masks, boxes, `cls8`, `sil8`, `fill_holes`), `zoom.py` (`zoom.py x0 y0 x1 y1 scale out.png [grid]`),
  `comps_053.py` (`label()`), `woodmap.py` (wood-only maps `w_*.png`), `tonemap.py` (leaf tones light / mid / dark at
  76° / 96°; `tonemap.py f34 2`), `mont.py`.
- **Measurements:** `measure.py` → `measure_out.txt` (bbox, W : H, shares, fill, profiles, fifths); `samp.py` →
  `samp_out.txt` (colours per region, tone shares and bands); `samp2.py` → `samp2_out.txt` (close-ups, parts, cut
  ends, soil, pebbles); `sw.py` (swatches); `comps.py` → `comps_out.txt` (flowers, rocks, ground pads per view);
  `trunk.py` (wood runs per height); `window.py` (canopy-run bottoms and the lower window); `scallops.py`; `expl.py`
  (exploded and parts blobs); `lines.py` (rules).
- **Zooms:** `z_f34.png`, `z_r34.png`, `z_f34crown.png`, `z_f34trunk.png`, `z_ortho1.png` (front, side),
  `z_ortho2.png` (rear, top), `z_expl.png`, `z_explclumps.png`, `z_explbase.png`, `z_stem.png`, `z_cu.png`,
  `z_cu1.png`–`z_cu3.png`, `z_parts.png`, `z_partsL.png`, `z_partsR.png`, `z_pal.png`. Also the masks `cls_*.png` /
  `cls_mont.png`, the wood maps `w_*.png` and the tone maps `t_f34.png` / `t_top.png`.
- **On our renders:** copy 054's `m054w/meas.py` and point it at this folder's `m.py` (paper `#F8F4EC`, `cls8`/`sil8`).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a free-standing shrub with its own base dressing (rocks, ground leaves, flowers; no
  soil patch, §3.8). Hero budget 4000 tris, each part under 1000. The plan in §4.3 lands at about 3600–3800 (tight: §4.3 gives the cut order).
- **Overall read (check this first).** A **low, wide, round-topped bush**: a **dome of faceted leaf rosettes** (each a
  pinwheel of 5–8 broad, blunt, faceted lobes round a raised centre), grouped in **clusters on the tips of a forked
  brown branch stem**.
  - The crown is lime-yellow on its lit top, mid green on the body, and dark green low down and inside.
  - At the sides it comes down to the ground. In the middle it lifts into an **arched lower window** (to h ≈ .45) where
    the **thick faceted trunk, its fork and two low side limbs** show against a near-black interior.
  - **Six white five-petal flowers with yellow centres** sit on the front half of the crown.
  - At the foot are **pale warm-grey faceted rocks** (two big ones at the front, two at the back and a flat stone in
    front), **lime ground-leaf pads** round the base and two or three small pebbles.
  - It reads **green over a little wood**. In every side view: canopy 70–73 % of the silhouette, ground green 5–10 %,
    wood 7–9 % (nearly all below h .5), rock 5–6 % (mid and shade facets; §1.2), flowers 1–5 %.
  - The bush is **about 1.45 × as wide as tall** in front and rear (front 1.425, rear 1.451), 1.21 from the side, and
    **slightly oval in plan** (top W : D 1.12).
- **Focal silhouettes, in order:**
  1. The crown's scalloped dome: the peak at f .4–.6 (h .96–.99), shoulders at h .67–.69 at f .1–.2 and .8–.9, the
     side clusters reaching the ground.
  2. The lower window: a dark arch from f ≈ .25 to .80 and up to h ≈ .45, with the brown trunk rising through it and
     forking at h .26–.34.
  3. The flowers: six white stars on the front, 0.12–0.14 H across.
  4. Two big pale rocks flanking the trunk foot, lime pads lapping over them.
- **Target size: 4.5 tall (crown top), crown 6.4 wide (X) × 5.6 deep (Y), trunk Ø 0.55–0.6 at the base, forking at
  z 1.15–1.5** (decision §8.1). Tolerances: height ±0.15, width ±0.3, depth ±0.3.
  - **How it was derived.** The front cell's silhouette is 228 × 160 px, so 35.6 px / stud at H 4.5. The f34's 407 ×
    297 px gives 66 px / stud. The side is 193 × 160 (W : H 1.206 → 5.4 with the dressing). The top is 202 × 180 (W : D
    1.122 → 6.4 × 5.7).
  - **Why 4.5.**
    - The old kit's `LowBush` notes say "~6 × 6 × 4.5". It is "low": at 0.82 C, below a 5.5 character's eye line, so
      a player sees over it (the design doc's height table, §3.2 of WorldModeling).
    - It is not a forage shrub (forage shrubs are capped at 0.65 C, so 017 / 022 / 024 / 028 are 3.6 tall). The rim
      bushes of 040–046 are 1.6–2.5 tall, so 058 is clearly the big decorative bush of the set.
    - At 4.5 the sheet gives: rocks 1.8–1.9 wide and 0.75–0.95 tall; flowers 0.55–0.62 across (centres 0.17); trunk
      Ø 0.55–0.7 at the foot; rosettes 0.9–1.5 across; the lower window 2.0 high.
    - At 3.6 the flowers shrink to 0.45 and the window to 1.6. At 5.5 it is character height, not a low bush.
  - **Against the character (5.5):** 0.82 C tall, 1.16 C wide.
- **Build frame:** front −Y, +X right, ground z 0. Trunk axis at (0, 0), upright (the trunk run's centre moves less than
  ±0.03 H up to the fork in front and rear). The origin is the bbox bottom centre; the crown is near-symmetric in X, so
  the origin sits within 0.1 of the trunk axis (record it).

### 1.2 Measured views (`measure.py`, `samp.py`, `window.py`)

| View (box) | Silhouette bbox (px) | W : H | G | T | R | Y | W | O | fill | canopy G | ground G |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (15,125,515,456) | 81–487 × 145–441 (407 × 297) | **1.370** | **76.8 %** | **8.4** | 6.4 | 0.7 | 4.3 | 3.4 | 0.680 | 71.6 | 5.3 |
| Rear three-quarter (515,125,1008,456) | 531–953 × 157–435 (423 × 279) | 1.516 | 80.3 | 9.7 | 4.9 | 0.1 | 0.7 | 4.4 | 0.685 | 72.7 | 7.5 |
| Front (12,531,276,722) | 31–258 × 551–710 (228 × 160) | **1.425** | **77.4** | **7.6** | 6.1 | 0.7 | 4.2 | 4.0 | 0.682 | 70.3 | 7.1 |
| Side (278,531,502,722) | 294–486 × 550–709 (193 × 160) | 1.206 | 82.1 | 8.0 | 6.0 | 0.3 | 1.3 | 2.4 | 0.635 | 72.2 | 9.9 |
| Rear (504,531,766,722) | 520–754 × 549–710 (235 × 162) | 1.451 | 79.3 | 9.0 | 6.3 | 0.1 | 1.2 | 4.1 | 0.686 | 71.5 | 7.8 |
| Top (769,531,1010,722) | 789–990 × 531–710 (202 × 180) | 1.122 (W : D) | 88.0 | 2.1 | 3.1 | 0.8 | 3.2 | 2.7 | 0.695 | | |

- Shares are of the silhouette (O included; X, soil and paper excluded). **Fill** = silhouette / bbox area (0.64–0.70).
  W in the r34 / rear / side is mostly sky through gaps; in the front / f34 / top it is mostly petals.
- **Verifier tolerance:** G ±4, T ±3, R ±3 points; W : H ±0.07; fill ±0.05; positions ±0.04 H.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.1 W): one dome with a peak and shoulders,
scalloped by rosettes.

| f | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .16 | .69 | .67 | .91 | .94 | .95 | .95 | .91 | .67 | .63 | .44 |
| r34 | .35 | .64 | .69 | .86 | .99 | .95 | .96 | .80 | .74 | .59 | .13 |
| Front | .14 | .69 | .67 | .88 | .96 | .96 | .94 | .89 | .67 | .67 | .43 |
| Side | .13 | .63 | .70 | .79 | .92 | .98 | .92 | .81 | .73 | .55 | .14 |
| Rear | .45 | .61 | .76 | .76 | .91 | .99 | .89 | .86 | .72 | .58 | .12 |

**Width per height** (silhouette width at h .0 → 1.0 as a fraction of W):

```
f34    .06 .81 .93 .85 .97 .96 .87 .76 .54 .42 .02
r34    .24 .84 .90 .95 .95 .92 .86 .65 .49 .30 .02
front  .52 .94 .92 .90 .99 .94 .87 .77 .51 .39 .03
side   .27 .98 .90 .88 .94 .85 .74 .72 .37 .27 .03
rear   .29 1.00 .89 .94 .96 .91 .79 .74 .39 .32 .03
```

- Reading (front): h .1 the side clusters, rocks and ground pads across .94 of W. h .2–.5 the crown at full width. h .6–.7
  the dome narrowing (.87 / .77). h .8–.9 the top cluster (.51 / .39). There is no bare-trunk row: the crown comes down
  to the ground at the sides, and the trunk shows only in the lower window.

**Canopy-run bottom per column** (`window.py`: the bottom of the leaf run hanging from the top, fraction of H, at f .05 →
.95 every .05):

```
front  .30 .04 .09 .14 .14 .23 .21 .26 .41 .46 .40 .16 .38 .36 .17 .25 .09 .04 .34
f34    .32 .13 .11 .13 .78 .25 .67 .90 .46 .47 .49 .93 .40 .59 .20 .31 .28 .12 .38
rear   .56 .05 .06 .14 .30 .12 .37 .37 .27 .46 .37 .62 .38 .16 .22 .04 .02 .03 .10
```

- **This is the window.**
  - At the sides (f .10–.20 and .80–.90) the leaves reach h .02–.14: the low side clusters sit on the ground.
  - In the middle (f .40–.60) the crown's underside is at h .37–.46.
  - The f34's high values (.67–.93) are flower and sky gaps inside the crown, not the bottom.
- **Window (wood, dark interior and gaps above h .08):** f .24–.81 (p5–p95), up to h .45–.49 (p95), 9–13 % of the
  silhouette in every side view.

**Height fifths** (bottom → top, % of each class):
- Front: G 15.3 / 23.3 / 28.7 / 22.8 / 9.9; T 34.2 / 56.8 / 8.8 / 0.2 / 0.0; R 97.7 / 1.7 / 0.6 / 0 / 0.
- f34: G 12.9 / 23.3 / 29.6 / 22.8 / 11.4; T 25.4 / 62.4 / 12.0 / 0.2 / 0.0.
- Rear: G 14.8 / 22.5 / 31.1 / 22.7 / 8.9; T 36.2 / 57.2 / 6.5 / 0.1 / 0.0. Side: T 34.9 / 58.2 / 6.8 / 0 / 0.
- **Wood lives in the lower 60 %**: 54–63 % of it in fifth 2 (h .2–.4: the trunk and fork), 7–13 % in fifth 3 (the
  forked arms entering the clusters), none above h .6.
- **Wood bands** (% of the silhouette; h < .2 / .2–.4 / .4–.6 / > .6): front 2.6 / 4.3 / 0.7 / 0; f34 2.1 / 5.3 / 1.0 /
  0; rear 3.3 / 5.1 / 0.6 / 0.

**Wood runs per height** (`trunk.py`, fraction of H from the cell centre; front unless named):

| Feature | Evidence | Adopted (studs at H 4.5) |
| --- | --- | --- |
| Trunk foot | rear h .10–.14: w .148–.154 (flare); front h .06–.10: w .050–.069, partly hidden by the rock and pads | Ø 0.70 at z 0 (three short root flares), 0.58 at z 0.4 |
| Trunk | front h .14–.22: w .087–.125; f34 .077–.141; rear .154–.198 (the fork's base) | Ø 0.55 at z 0.8 |
| Fork | front h .26–.34: w .150–.169 (two leads side by side); r34 h .26 .301 | the fork at z 1.15–1.5 |
| Arms above the fork | front h .38: −.103…−.059 (w .05) and −.003…+.072 (w .08) and +.228…+.272 (w .05); h .42 w .069; h .46 w .05 | the lead Ø 0.32–0.36 → 0.24; the arms Ø 0.22–0.30 |
| Low side limbs | front h .14–.22: x −.33…−.20 (w .07–.11, oblique); x +.39…+.48 (w .03–.09). f34 the same pair (195–235, 360–400) and (385–410, 350–385) | LOW-L and LOW-R Ø 0.26 → 0.18, rising 25–35° out of the trunk at z 0.5–0.65 |

**Ground dressing blobs** (`comps.py`; x as a fraction of W from the cell centre, h fraction of H; studs at H 4.5, front
35.6 px / stud, f34 66 px / stud):

| View | Rocks | Ground leaves (green below h .13) |
| --- | --- | --- |
| Front | left −.43…−.16 (63 × 25 px = 1.8 × 0.7); front-centre flat stone −.06…+.15, h ≤ .05 (1.35 × 0.25); right +.09…+.38, h ≤ .175 (1.9 × 0.8, the tallest) | far left −.50…−.31; front-centre −.17…+.05 (1.4 wide, a foot rosette); right +.31…+.50 (1.25 wide) |
| f34 | left (124–246, 396–442) 1.86 × 0.71 with a pebble at its left; right (322–447, 383–436) 1.9 × 0.82; flat stone (293–330, 424–432); a pebble (273–287, 427–435) | far left (98–161); a big lime foot rosette (228–313, 402–440) in front of the trunk; right (440–463) |
| Side | big rock on its right half +.02…+.33 W, h ≤ .26 (1.65 × 1.15, §3.4); small rocks at the left −.49…−.23 | left −.50…−.28; middle −.29…+.11; right +.32…+.50 |
| Rear (mirrored: rear −x is world +X) | −.50…−.11 h ≤ .15 (world X +0.7…+3.2, 0.7 tall); −.11…+.34 h ≤ .18 (world X −2.2…+0.7, 0.8 tall) | −.50…−.30; −.22…+.03; +.25…+.50 |
| r34 | (652–700, 403–433) and a big group (738–900, 387–437) on the near side | five pads across |
| Top | grey rock edges at the front and the back rim (R fifths 47 % front, 33 % back) | |

**Flowers** (`comps.py`, yellow-centre blobs; studs from the trunk axis at H 4.5):

| Flower | Front (x frac W, h) | f34 (x frac W, h) | Front studs (X, z) | Sits on |
| --- | --- | --- | --- | --- |
| F1 | −.338, .43 | −.327, .45 | (−2.15, 1.95) | the low-left cluster's front |
| F2 | −.090, .525 | −.077, .545 | (−0.6, 2.35) | the front-left cluster's lower front |
| F3 | +.123, .77 | +.135, .78 | (+0.8, 3.45) | the crown top's front |
| F4 | +.226, .59 | +.235, .61 | (+1.45, 2.65) | the front-right cluster |
| F5 | +.237, .26 | +.251, .29 | (+1.5, 1.2) | a low rosette in the window, right of the trunk, above the right rock |
| F6 | +.393, .54 | +.396, .57 | (+2.5, 2.4) | the right cluster's front |

- Size: f34 blobs 34–38 px = 0.114–0.128 H; front 20–23 px = 0.125–0.144 H → **Ø 0.55–0.62** (F5 a little smaller, 0.45).
  Centre Ø 11–12 px in the f34 = 0.037 H → **0.17**.
- Rear and r34 show **no flowers**. The side shows two at its right (front) half. The top shows three: two in the upper
  half and one lower right (§3.5).

**Plan (top cell, `t_top.png`).**
- About **12 ± 3 rosettes** are visible from above, each 35–55 px (0.17–0.27 W = 1.1–1.7 studs face-on), lime centres
  with dark gaps between them.
- **The brown lead and fork show in a gap near the centre** (870–895, 640–690; T 2.1 %).
- The plan is round-oval: W : D 1.12; the outline has 23 scallops.
- Tones from above: light 33 %, mid 54 %, dark 13 %.

**Scallops** (`scallops.py`, outline peaks ≥ 2 px prominence over ±3°): front 20, f34 21, r34 17, side 18, rear 19,
top 23. That is **about one scallop per 0.16–0.17 H of dome outline** (0.75 studs at H 4.5): every rosette shows 2–3
lobes on the outline.

### 1.3 Silhouette and composition per view

**Front three-quarter (`z_f34.png`, `z_f34crown.png`, `z_f34trunk.png`, `w_f34.png`, `t_f34.png`) — governs the read
with the front cell.** It is drawn **nearly frontal and from higher up**: the six flowers sit at the front cell's x
fractions within ±0.015 W, and the rocks' tops and the ground band show more. It is about 4 % narrower in W : H (1.37
against 1.425), §3.2. Lit from the upper right: the lime falls on the upper right of every rosette, and the dark green
on the lower left.
- **Rosettes:** each is a raised centre with 5–8 broad lobes radiating as faceted planes. A lobe has a ridge from the
  centre to a **blunt rounded tip**, with two or three flat facets on each side. The outline of each rosette is a
  scalloped circle, not a star; the notches between lobes are shallow (about 0.2 R). Visible leaves (lobes) are 25–35 px
  = 0.38–0.53 studs; rosettes are 50–100 px = 0.75–1.5 studs.
- **Clusters:** rosettes overlap 30–50 % into bigger mounds (2–3 studs) that read as one crown. The crown top is a big
  lime cluster at f .4–.6. Front-left and right clusters at h .55–.9 and two low side clusters reach the ground at f
  .05–.20 and .80–.95.
- **Skeleton visible** (`w_f34.png`):
  - The trunk rises from between the two front rocks (x 285–325, y 440 → 335): Ø 0.6 at the foot, faceted into plank
    strips (lit `#C5792B`, dark grooves `#331C04`).
  - At h .34 it forks: a lead continues up (285–300, to y 300 = h .48); an arm runs up-left (250–285, 305–330); an arm
    runs up-right (310–360, 355 → 320); and a short spur goes up-right (345–360, 290–275) with a cut end.
  - **Two low limbs** leave the trunk foot obliquely: left (195–235, 400 → 360) and right (385–410, 385 → 350). Each
    rises into a low side cluster.
  - The interior behind the skeleton is near-black (`#040C01`).
- **Base:** two big pale rocks flanking the trunk foot (left 1.86 × 0.71, right 1.9 × 0.82 with its lit top facing up
  right). A flat stone in front of the trunk, a pebble at the left rock. A big lime foot rosette in front of the trunk
  (1.3 wide) laps over the flat stone. Lime ground pads at both ends. A pale warm soil halo round everything (§3.8).
- **Flowers:** six, each five rounded white petals round a domed yellow centre, facing out and up from the rosette they
  sit on.

**Rear three-quarter (`z_r34.png`, `w_r34.png`).**
- The same bush from behind: no flowers.
- The trunk is wider here (rear h .10–.14 w .15–.17 H with the flare). It forks at h .30–.38 into a lead (up to h .50),
  a left arm and a right arm, with two low limbs to the side clusters (610–650, 380–410) and (820–850, 390–410).
- A group of rocks sits on the near (back) side: a small one at (652–700) and a big pair at (738–900). Five lime ground
  pads.

**Front, side and rear cells (`z_ortho1.png`, `z_ortho2.png`, `w_front.png`, `w_rear.png`, `w_side.png`).** These are
low views (ground band about 6 % of H) at one scale (160–162 px tall).
- **Front:** the same layout as the f34.
  - Trunk foot X −0.13…+0.3, fork at z 1.2–1.5.
  - Arms: left (X −0.5…−0.13, z 1.4–1.8); lead (X 0…+0.15, to z 2.0); right (X +0.4…+1.2, z 1.2–1.8, rising ~35°);
    a cut spur at (+0.8, 2.2).
  - Low limbs: left X −1.5…−1.1 at z 0.6–1.1; right X +1.6…+2.05 at z 0.6–1.35.
- **Rear:** mirrored. Trunk and fork; rocks at both sides of the trunk on the back.
- **Side:** a narrower dome (W : H 1.21) with the window and the trunk in the middle, the fork leaning toward its right.
  The big rock and two flowers are on its right half (§3.4).

**Top (`z_ortho2.png`, `t_top.png`).** About twelve rosettes, flowers at three spots, the brown lead visible in a
central gap, grey rock edges at the front and back rims.

**Branch to leaf attachment (close-up 1, `z_cu1.png`).**
- A branch fork: a thick limb (8-sided, plank facets, bark `#925323`, lit `#C77A31`) splits into a short upright and two
  side arms. Each ends in a **flat cut face**, outlined by a dashed line: that is where a clump sits.
- A pivot marker (a ring with a dot) sits at the fork; arrows show the clump's slight rotation about its base.
- **The joint is hidden by the clump's underside.** Dark green rosettes surround the fork.

**Leaf clump underside (close-up 2, `z_cu2.png`).**
- Seen from below, a cluster is **a solid volume with a flat, slightly lobed underside disc** (`#3A5A1B` in shade:
  rendered dark green, §5.3).
- Rosettes wrap the rim: their lobes hang just below the disc's edge and turn lime where the light reaches.
- No holes, no visible stems, consistent thickness.

**Rock and ground detail (close-up 3, `z_cu3.png`).**
- A pale rock (lit `#EBD7C3`, shade `#74747B`) of **10–14 broad flat facets with a flat base**, sitting on a pale soil
  floor beside the trunk foot.
- **Lime ground-leaf pads** (`#9CC606`, lit `#C3E112`) **lap over the rock's foot and the soil**: each pad is a low
  three- or four-lobed faceted rosette, flat underneath.

### 1.4 Parts (exploded `z_expl.png`, `z_explclumps.png`, `z_stem.png`, `z_explbase.png`; parts row `z_parts.png`, `z_partsL.png`, `z_partsR.png`)

The exploded is an elevated front view drawn bigger than the hero (the stem's trunk is 75 px against the large clump's
198). **The hero governs every size and height** (§3.6). The parts row gives each reusable module's own shape.

| Part (label) | Exploded box (px) | Parts-row box (px) | Notes |
| --- | --- | --- | --- |
| Leaf Clump (large) | (101–298, 810–979) 198 × 170, W : H 1.16 | (28–129, 1314–1418) 102 × 105, W : H 0.97 | exploded: a **cluster of about six rosettes** (a big centre one, others round it, the lower-left ones dark). Parts row: **one big two-tier rosette**, 6 upper lobes over 7–8 lower lobes round a raised centre, flat underside |
| Leaf Clump (medium) | (313–436, 839–946) 124 × 108, 1.15 | (145–232, 1331–1413) 88 × 83, 1.06 | one two-tier rosette, 7–8 lobes |
| Leaf Clump (small) | (435–534, 901–992) 100 × 92, 1.09 | (246–313, 1348–1411) 68 × 64, 1.06 | one single-tier rosette of 5–6 lobes ("clover") |
| (unlabelled tiny clump) | (259–336, 939–1007) 78 × 69, 1.13 | | a 5-lobe rosette dashed to the stem's front-centre tip |
| Branch Stem (base) | stem + rocks (225–467, 979–1183) 243 × 205 | (333–421, 1314–1418) 89 × 105, a Y | **six flat-cut tips** (§2.3). Faceted 6–8-sided limbs with plank facets. Cut ends pale (`#DD8C37`) or darker (`#8B5B36`). Bark median `#834C1D`, lit `#B97028` |
| Flower (optional) | two: (167–185, 1014–1031) and (511–529, 1031–1048) centres, dashed to the left and right-lower tips | (630–700, 1340–1405), centre (652–672, 1361–1381) | five broad rounded white petals, a domed yellow centre (`#FAD306`, base `#F3AE07`), a small green leaf under the petals (`#507805`) |
| Rock (base) | three: centre big (179–385, 1148–1231), back (366–422, 1124–1169), right (422–523, 1157–1222) | (432–504, 1349–1413) 73 × 65, W : H 1.12 | pale warm grey (`#CEBDB0`; lit `#F7F3EA`, shade `#787272`). 10–14 broad facets, flat base, a rounded crown |
| Ground Leaves (optional) | five pads (148–240, 1170–1233), (372–441, 1162–1232), (406–487, 1121–1157), (209–298, 1124–1171) | three pads (522–612, 1353–1411): 64 × 32, 42 × 25, 42 × 24 | low lobed lime pads (`#BAD509`, lit `#D8E810`), W : H 1.7–2.2, 3–5 rounded lobes, flat underneath |
| (unlabelled dressing) | two tan pebbles (192–224, 1196–1210) `#B79767` and (440–470, 1150–1168); a small leaf sprig on a stem behind the right rock (406–487, 1121–1157); two tiny red specks on the right rock (≈ 485, 1175) | | §3.7: the pebbles go in; the sprig and red specks stay out |

#### Branch stem — exploded, close-up 1, hero
- **Shape:** a faceted trunk (6–8 sides, plank strips, three short root flares at the foot) splits at the fork into a
  **left leader and a right leader** (the exploded's Y). They carry six limbs, each a straight run with one or two hard
  kinks, ending in a **flat cut face** (§2.3).
- **Hero size:** Ø 0.70 at z 0, 0.55 at z 0.8, fork at z 1.15–1.5; limbs Ø 0.18–0.36; tips at z 1.15–2.6. Part about 4.2
  × 3.6 × 2.7.

#### Leaf rosettes (large / medium / small) — parts row, exploded, close-ups 1–2, hero
- **Shape:** a closed faceted mound. A raised centre; one ring (small) or two offset rings (large, medium) of **broad
  blunt lobes**, each with a ridge from the centre to its rounded tip; shallow notches; the lower ring drooping; a
  **flat underside**. W : H about 1.0 as a part; in the hero each sits sunk into its cluster.
- **Hero sizes:** large Ø 1.5 (R 0.75, H 1.3); medium Ø 1.2 (R 0.6, H 1.05); small Ø 0.9 (R 0.45, H 0.8).

#### Leaf clusters (the hero's clumps) — exploded "large", close-ups 1–2
- **Shape:** a dark solid core with a flat underside (close-up 2) on its branch tip, clad in 4–5 overlapping rosettes.
  One scalloped outline, lime top, dark underside.

#### Rocks, ground leaves, flowers — exploded, close-up 3, parts row
- As in the table. Ground leaves are **the small rosette flattened** (H / R 0.5, 3–5 lobes): the sheet's "reuse leaf
  clumps" note. Flowers sit on rosettes in the hero, with the green leaf under the petals touching the rosette.

### 1.5 How 058 differs from its siblings and the old kit (binding: the verifier checks these)

| | W06 `LowBush` (old kit) | 054 `ShadeTree` | 044 / 046 rim `dome_bush` | 017 `BerryBushNode` | **058 Low Bush** |
| --- | --- | --- | --- | --- | --- |
| Size | ~6 × 6 × 4.5 | 20 tall | 2.0–3.0 across, 1.6–2.5 tall | 4.3 × 3.5 × 3.6 | **6.4 × 5.6 × 4.5, W : H 1.43** |
| Foliage | "flat saturated blob" of star clumps | 77 lobed bicone cards on 5 dark cores | 9–10 broad round-tipped leaves on a hidden heart | three-leaf clusters on canes | **about 31 faceted lobed rosettes (5–8 blunt lobes, 1–2 tiers) in seven clusters on branch tips; lime / mid / dark by height** |
| Skeleton | a trunk forking into 3 limbs in a front gap | a twisted 6-strand trunk with 4 plug-in modules | a short hidden trunk | canes | **a faceted trunk Ø 0.55–0.7 forking at z 1.15–1.5 into two leaders and seven flat-cut limbs, shown through an arched lower window (T 7–9 %, none above h .6)** |
| Flowers | ~7–9 white | none | yellow on some | berries | **six white 5-petal flowers (Ø 0.6), front half and crown top only** |
| Base | two front rocks, side rocks, moss, a soil patch | 7 rocks, tufts, moss pads | lawn | none | **two big front rocks, two back rocks, a flat stone, 2–3 pebbles, 8 lime ground-leaf pads; no soil patch** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, trunk axis at (0, 0)). Plan azimuths: 0° = +X, counter-clockwise,
90° = +Y (back), 270° = −Y (front).

### 2.1 Stack (binding contact chain, bottom up; every seat gap ≤ 0.03)

| Piece | Sits on / in | Contact |
| --- | --- | --- |
| Branch stem (trunk + limbs; one or more closed shells, decision §8.5) | ground | flat 8-sided foot at z 0 (the root flares' undersides at z 0 … −0.02) |
| Limbs | the trunk / the leaders | a ring-stack run continuing from the parent, or a closed shell buried ≥ 0.12 in it; no gap, no visible boolean seam |
| Twigs (4-sided, one per rosette that is off the tip) | their limb tip | buried ≥ 0.10 in the limb and 0.15–0.3 in the cluster core |
| Cluster core (dark solid, flat underside) | its limb tip | the tip's cut face 0.25–0.4 inside the core's underside (close-up 1: the joint is hidden) |
| Rosettes | the core and neighbours | each rosette's underside centre within 0.03 of the core (or a neighbour); ≤ 25 % of its verts inside the core; none more than 50 % inside a neighbour (§6) |
| Low-cluster rosettes at the ground | the core and the ground | the lowest lobes may touch z 0 (0 … −0.03), never sink further |
| Foot rosettes (FC, FB) | ground | flat underside at z 0 … −0.02 |
| Rocks, flat stone, pebbles | ground | flat base sunk 0.03 (decision §8.10) |
| Ground-leaf pads | ground and / or a rock's foot | underside within 0.03 of the ground or rock; ≤ 0.05 into a rock (ray parity, §6) |
| Flowers | a rosette | the green under-leaf and petal bases within 0.03 of the rosette surface; the centre dome on the petals; nothing inside the rosette deeper than 0.05 |

### 2.2 Branch stem: trunk and fork

| Ring z | 0 | 0.4 | 0.8 | 1.15 (fork base) | 1.5 (fork top) |
| --- | --- | --- | --- | --- | --- |
| Trunk Ø (plank crests) | 0.70 | 0.58 | 0.55 | 0.60 (widening into the two leaders) | |
| Centre X | 0 | 0 | 0 | 0.02 | |

- **Section:** 8-sided, with **plank strips** (alternate facets proud 0.02–0.04; the f34's lit strips and dark grooves).
  Two of the eight vertices are pulled in 0.04 for grooves. No twist is shown on this sheet.
- **Root flares (3):** short wedges at az 200°, 320°, 80°, from z 0.35 down to r 0.5 at z 0. Their 4-sided sections have
  a flat bottom, and the flares stay inside the rocks' clearance (§2.6).
- **Fork:** at z 1.15–1.5 the trunk splits into the **left leader** (Ø 0.36, toward −X / front) and the **right
  leader** (Ø 0.36, toward +X / back), as the exploded's Y. The front view shows the two leaders side by side, w .150–.169
  H (0.67–0.76 together) at h .26–.34.

### 2.3 Limbs (seven tips) and the clusters they feed

Waypoints are segment ends (straight segments; every waypoint a hard mitred kink). Ø per waypoint. Every tip ends in a
**flat cut face** (`bark_light`) buried in its cluster's core.

| Limb | From | Waypoints (x, y, z) → tip | Ø | Feeds | Evidence |
| --- | --- | --- | --- | --- | --- |
| **LEAD** | the right leader | (0.05, 0.05, 1.5) → (0.15, 0.15, 2.1) → **tip (0.2, 0.35, 2.55)** | 0.36 → 0.30 → 0.26 | CT (crown top) | front lead to z 2.0 (h .46), top-view gap at the centre; exploded top tip |
| **UP-L** | the left leader | (−0.15, −0.05, 1.35) → (−0.55, −0.45, 1.8) → **tip (−0.95, −0.9, 2.2)** | 0.32 → 0.26 → 0.22 | CFL (front-left) | front left arm X −0.5…−0.13, z 1.4–1.8; exploded centre-front short upright |
| **UP-R** | the right leader | (0.15, 0, 1.3) → (0.85, −0.3, 1.7) → **tip (1.4, −0.55, 2.15)** | 0.30 → 0.25 → 0.20 | CR (front-right) | front right arm X +0.4…+1.2, z 1.2–1.8 rising ~35°; exploded right-upper |
| **BACK-L** | the left leader | (−0.1, 0.1, 1.4) → (−0.5, 0.8, 1.95) → **tip (−0.9, 1.3, 2.3)** | 0.28 → 0.22 → 0.20 | CBL (back-left) | rear arm right in the image (world −X); exploded small up-left branch |
| **BACK-R** | the right leader | (0.15, 0.15, 1.45) → (0.6, 0.85, 1.95) → **tip (1.0, 1.35, 2.25)** | 0.28 → 0.22 → 0.20 | CBR (back-right) | rear arm left in the image (world +X); **not in the exploded: a mirrored BACK-L, decision §8.4** |
| **LOW-L** | trunk at z 0.55 | (−0.25, 0, 0.55) → (−1.0, −0.15, 0.85) → **tip (−1.75, −0.05, 1.15)** | 0.26 → 0.22 → 0.18 | CLL (low left) | front X −1.5…−1.1, z 0.6–1.1; f34 (195–235, 400 → 360); exploded left long limb |
| **LOW-R** | trunk at z 0.6 | (0.25, 0.05, 0.6) → (1.1, 0.15, 0.9) → **tip (1.95, 0.3, 1.3)** | 0.26 → 0.22 → 0.18 | CLR (low right) | front X +1.6…+2.05, z 0.6–1.35; f34 (385–410, 385 → 350); exploded right-lower |
| spur | UP-R at its kink | (0.85, −0.3, 1.7) → **(0.85, −0.55, 2.2)** | 0.14 | **bare, cut end visible** | front cut spur at (+0.8, 2.2); f34 (345–360, 290–275) |

- **Visible limb lengths (binding, §9.1):**
  - In the front, rear and f34 renders the trunk shows from the ground to the fork, and **LOW-L, LOW-R and two of the
    upper arms each show ≥ 0.5 studs** of bare limb inside the window.
  - The spur's cut end shows in the front and f34.
  - The top view shows the lead in a central gap (T 1–4 %).
- **Bark pits:** none drawn on this sheet. Skip them (the plank strips and cut ends carry the bark).
- **Cut ends:** the six cluster tips are hidden in their cores. Only the spur's end shows (pale `bark_light`). The parts
  stem shows all seven: about half pale, half `bark` (exploded: pale `#DD8C37`, darker `#8B5B36`).

### 2.4 Leaf clusters (seven) and foot rosettes (two)

| Cluster | Tip | Centre (x, y) | Core bottom z → crown top z | W × D | Rosettes L / M / S | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| **CT** crown top | LEAD | (0.15, 0.4) | 2.35 → **4.5** | 3.2 × 3.0 | 2 / 1 / 1 | front top f .4–.6 at h .96–.99; f34 big lime top cluster (250–330, 150–230); top-view centre |
| **CFL** front-left | UP-L | (−1.3, −1.2) | 1.95 → 3.95 | 2.8 × 2.4 | 1 / 3 / 1 | front f .3 top .88; canopy bottom at f .40–.50 h .41–.46; f34 left-centre mounds |
| **CR** front-right | UP-R | (1.6, −0.9) | 1.85 → 3.95 | 2.6 × 2.6 | 1 / 3 / 1 | front f .7 top .89; f34 right mounds with F4 / F6 |
| **CBL** back-left | BACK-L | (−1.1, 1.6) | 2.0 → 3.8 | 2.8 × 2.2 | 1 / 2 / 1 | rear f .6–.8 tops .86–.89 (image right = world −X) |
| **CBR** back-right | BACK-R | (1.1, 1.65) | 2.0 → 3.8 | 2.8 × 2.2 | 1 / 2 / 1 | rear f .2–.4 tops .76–.91 |
| **CLL** low left | LOW-L | (−2.35, 0.0) | **0.0** (lowest lobes on the ground) → 3.05 | 2.0 × 3.6 | 1 / 1 / 2 | front f .1–.2 tops .67–.69, bottoms .04–.09; rear the same |
| **CLR** low right | LOW-R | (2.4, 0.3) | **0.0** → 3.05 | 2.0 × 3.4 | 1 / 1 / 2 | front f .8–.9 tops .67, bottoms .04–.09 |
| **FC** foot rosette front | ground | (−0.55, −2.2) | 0 → 0.95 | 1.3 × 1.1 | 0 / 1 / 0 | f34 big lime foot rosette (228–313, 402–440); front centre ground green −.17…+.05 W |
| **FB** foot rosette back | ground | (0.5, 2.35) | 0 → 0.75 | 1.0 × 0.9 | 0 / 0 / 1 | rear centre ground green −.22…+.03 W |

- **Totals:** 7 + 14 + 10 = **31 rosettes** (large 7, medium 14, small 10). Within ±4 is fine if the views match.
- **Core (one per cluster):** a solid flattened dome (8-sided: a flat 8-gon underside, one band, a top ring and a top
  vertex; about 30 tris). Its size is 0.7 of the cluster's W and D and 0.55 of its height. **The underside is flat** and
  sits 0.1–0.2 above the lowest lobes, so from below it reads as close-up 2's disc ringed by lobes. CLL / CLR cores sit
  at z 0.5–0.9 with their skirt rosettes hanging to the ground; they are never buried in the ground.
- **Rosette (closed shell; §4.1 builds it):**
  - **Large:** n = 7 lobes, two tiers. Upper tier: 7 lobe tips at 0.62 R, z 0.78 h; notches at 0.45 R, z 0.84 h.
    Lower tier: 7 lobes offset by half a lobe, each a **blunt two-vertex tip** (±9° about the lobe axis) at R, z
    0.42 h; notches at 0.80 R, z 0.50 h. Rim ring at 0.72 R, z 0.08 h. Flat underside fan. About 84 tris.
  - **Medium:** n = 6, the same build, about 72 tris.
  - **Small:** n = 5, one tier: blunt tips at R, z 0.50 h; notches at 0.74 R; rim at 0.70 R, z 0.08 h; about 40 tris.
  - **Corners and joins.** Lobe tip corners ≥ 110° seen from above. Notch depth 0.18–0.25 R. Each lobe's ridge rises
    from tip to centre, so every lobe shows 2–3 broad facets.
- **Rosette placement** (per cluster, deterministic seed):
  - The large rosettes go on top and outward, the medium round the shoulders, the small low and inward.
  - Each sits on the core surface with its axis along the core normal tilted 15–25° toward up. It overlaps neighbours by
    30–50 % of its radius and has a random spin.
  - The underside centre is within 0.03 of the core; 1–2 rim verts may be inside the core (≤ 25 %).
  - **Clusters touch or overlap their neighbours** so the crown reads as one dome; each keeps its own scallops.
  - **Inner sides facing the trunk stay up**, so the window (f .25–.80, to h .45) stays open.
- **Read:** the crown must read as **one rounded, scalloped dome made of faceted rosettes**:
  - not a pile of separate balls (047 round 1);
  - not palm or agave stars (040, 044);
  - not big flat-leaf cabbages (046);
  - not a smooth blob (W06).
  Every rosette shows its centre and radiating lobes; neighbours overlap; the scallops come every ~0.75 studs.

### 2.5 Flowers (six)

| Flower | On | Approx. position (x, y, z) | Faces | Ø |
| --- | --- | --- | --- | --- |
| F1 | CLL front rosette | (−2.15, −1.6, 1.95) | out (−Y, −X) and up 25° | 0.6 |
| F2 | CFL lower front | (−0.6, −2.2, 2.35) | out (−Y) and up 20° | 0.6 |
| F3 | CT front | (0.8, −1.0, 3.45) | up 45° and out (−Y) | 0.6 |
| F4 | CR | (1.45, −2.0, 2.65) | out (−Y) and up 20° | 0.55 |
| F5 | a small low rosette of CLR, inside the window above RK1 | (1.5, −1.0, 1.2) | out (−Y) | 0.45 |
| F6 | CR right side | (2.5, −1.3, 2.4) | out (+X, −Y) and up 20° | 0.55 |

- Y values are where the crown surface lies on that line of sight; place each flower on the nearest outward rosette
  facet and record the actual position.
- **Build:**
  - **Five petals.** Each is a closed lens: a rounded spoon outline of 6 rim verts, broad at the tip (W : L 0.75),
    plus a top and a bottom vertex; about 12 tris. Petals overlap 20 % at their roots and are cupped up 12°.
  - **Centre dome:** 6-sided, two rings plus a top vertex, Ø 0.30 × 0.10 of the flower's Ø, raised 0.06 above the
    petals; about 18 tris.
  - **Leaf under the petals:** one small, closed, broad, round-tipped leaf (the parts row's green leaf), seated on the
    rosette.
  - About 85 tris per flower.
- **No floating:** the petal bases and the under-leaf sit within 0.03 of the rosette; the centre sits on the petals.
  Nothing more than 0.05 inside the rosette.

### 2.6 Base dressing

| Piece | Position (x, y) | Size W × D × H | Evidence |
| --- | --- | --- | --- |
| RK1 front-right (the tallest) | (1.45, −1.25) | 1.9 × 1.5 × 0.95, a rounded faceted crown, lit top toward the upper right | front +.09…+.38 W, h ≤ .175; f34 (322–447, 383–436); side big rock (§3.4) |
| RK2 front-left | (−1.9, −1.35) | 1.8 × 1.4 × 0.75, sloping top | front −.43…−.16 W, h ≤ .144; f34 (124–246, 396–442) |
| RK3 flat stone | (0.3, −1.95) | 1.3 × 0.9 × 0.25 | front −.06…+.15, h ≤ .05; f34 (293–330, 424–432) |
| RK4 back-right | (1.95, 1.3) | 2.0 × 1.4 × 0.8 | rear image −.50…−.11 W (world X +0.7…+3.2), h ≤ .15 |
| RK5 back-left | (−0.75, 1.55) | 1.8 × 1.3 × 0.7 | rear image −.11…+.34 W (world X −2.2…+0.7), h ≤ .18 |
| Pebbles ×3 | (−2.95, −1.2) grey; (0.95, −2.35) tan; (−2.7, 1.5) grey | 0.3–0.4 × 0.25–0.3 × 0.15–0.25 | f34 pebble at RK2's left; exploded tan pebbles `#B79767` |
| Ground-leaf pads ×8 | GL1 (−2.9, −1.9); GL2 (−0.2, −2.6) lapping over RK3; GL3 (2.75, −1.7); GL4 (2.6, −0.4) side; GL5 (2.6, 1.95); GL6 (−0.1, 2.75); GL7 (−2.4, 1.9); GL8 (−3.15, 0.3) side | 0.6–1.3 across, W : H 2–4 (0.2–0.35 tall), 3–5 lobes | front far left / right pads; rear three; side three; cu3 pads lapping a rock's foot; the parts row's three pads |

- **Clearances:** the rocks keep 0.15 clear of the trunk foot and root flares. LOW-R passes above RK1's back half (RK1's
  top 0.95 vs. the limb's underside at y ≈ 0 ≥ 0.6 above the rock's back edge: check). Pads may rest on a rock's foot
  (cu3) but never sink more than 0.05 into it. Foot rosettes keep 0.1 clear of rocks.
- **Rocks:** pale warm-grey angular blocks, flat base, 10–14 broad facets, ring stacks (base ring, widest ring at 0.3 h,
  shoulder ring at 0.7 h, a rounded faceted top). Never `K.hull_rock` eggs, never cool or lavender paint.

### 2.7 Expected extents and screen checks

- **Extents:** X −3.2 … +3.25 (CLL / CLR and the side pads), Y about −2.9 … +2.9, Z 0 … 4.5. Bbox about 6.4 × 5.8 × 4.5.
- **Checks on the renders** (floor hidden; `meas.py` with this folder's `m.py`):
  - **front_sheet (0, 5)** — governs positions:
    - W : H 1.36–1.49 (sheet 1.425); G 77 ± 4 (canopy 70, ground 7); T 7.6 ± 3; R 6 ± 3; fill 0.68 ± 0.05.
    - The top profile within ±0.07 for f .1–.9.
    - The canopy-run bottom (§1.2): the sides ≤ .15 at f .10–.20 and .80–.90; the middle .35–.50 at f .40–.60.
    - The window (non-leaf above h .08) 8–14 % of the silhouette, f .25–.80 to h .42–.50.
    - Six flowers at the §1.2 positions ±0.05 W / H.
  - **f34_sheet (0, 15)** (probe az −30 … +30 × e 10 / 15 / 20; keep the best; §3.2):
    - W : H 1.30–1.45 (sheet 1.370); G 77 ± 4, T 8.4 ± 3.
    - Light / mid / dark leaf shares 31 / 37 / 32 ± 8.
  - **rear_sheet (180, 5), r34_sheet (180, 15)** (probe 150 … 210): W : H 1.38–1.58; T 9 ± 3; no flowers; rocks and
    pads on the near side.
  - **side_sheet (90, 5):** content (§3.4): W : H 1.10–1.30 (sheet 1.206); the window with the trunk; clusters on both
    sides reaching the ground; the big rock and flowers on the front half.
  - **top (0, 89):** W : D 1.05–1.20 (sheet 1.122); 9–15 rosettes visible; T 1–4 % (the lead in a central gap);
    leaf light / mid / dark ≈ 33 / 54 / 13 ± 12.

## 3. View conflicts and resolutions

### 3.1 Sheet number
- **Evidence.** The header says "57 / 132"; INDEX.md row 58 lists `058.png` as "Flintborn Low Bush Study".
- **Resolution.** Our number is 058 (file name, keys `m058_*`). Note the header in the export notes only.

### 3.2 The front three-quarter is near-frontal and drawn from higher up
- **Evidence.** The six f34 flowers sit at the front cell's x fractions within ±0.015 W (−.327 / −.077 / +.135 / +.235 /
  +.251 / +.396 against −.338 / −.090 / +.123 / +.226 / +.237 / +.393). The rock tops and the soil show more. W : H is
  1.37 against 1.425.
- **Resolution (decision §8.9).** `front_sheet (0, 5)` governs positions; `f34_sheet (0, 15)` governs the read and the
  shares. Probe az −30 … +30 (e 10–20) and keep the best; record the camera.

### 3.3 Front and rear are near mirror images
- **Evidence.** The rear cell mirrors the front: the same window, the same fork, rocks at the same image x on both
  sides. The front has six flowers and the rear none.
- **Resolution.** **Build a real back:** two back clusters (CBL / CBR), two back rocks and back pads, placed by the rear
  cell (mirrored into world X). Front and rear both govern positions.

### 3.4 Which way the side and top cells face
- **Evidence.**
  - The "SIDE (RIGHT)" cell shows the flowers and the big rock on its right half, i.e. the bush's front is on the
    image's right. A camera on +X looking at −X would put the front on the left.
  - The top cell shows two flowers in its upper half and one lower right, and rock edges at both the top and bottom
    rims; the rear shows no flowers.
- **Resolution.** **The side cell is judged for content** (W : H, the window, low clusters both sides, the big rock and
  flowers on the front half), not mirror placement. **The top cell is judged for the plan** (W : D, rosette count, the
  central lead gap, rocks front and back). Flower positions come from the front and f34 (§3.5).

### 3.5 Where the flowers go
- **Evidence.** f34 / front: six on the front half. Rear / r34: none. Side: two on its front half. Top: three, two of
  them in the upper half.
- **Resolution (decision §8.6).** Six flowers on the front half and the crown top, placed from the front and f34 (§2.5).
  F3 sits high on CT so the top view shows it. **None on the back half.** The top cell's upper-half pair is not chased.

### 3.6 Exploded scale and module count vs the hero
- **Evidence.**
  - The exploded draws one stem with **six tips**, four clumps and two flowers dashed to tips. The large clump is drawn
    as a cluster of ~6 rosettes; the parts row's "large" is one two-tier rosette.
  - The hero shows a crown of about 30 rosettes, with clusters front, back and low at both sides, and flowers on
    rosettes, not on bare tips.
  - The exploded stem is drawn about 2.5× the hero's scale (its trunk is 75 px wide against the large clump's 198).
- **Resolution.**
  - **The hero governs sizes and placement; the parts row governs each part's shape.**
  - Rosettes come in large / medium / small (parts row); the hero's clusters are 4–5 rosettes on a core per tip (the
    exploded's "large").
  - The stem keeps the exploded's six tips plus BACK-R, the mirror of BACK-L, to fill the back (decision §8.4). It also
    keeps the visible cut spur.
  - Flowers sit on rosettes in the hero; the part shows one flower alone.

### 3.7 Small extras in the exploded base
- **Evidence.** The exploded base has two tan pebbles, a small two-leaf sprig on a stem behind the right rock and two tiny
  red specks on the right rock. None of these shows in any assembled view except one pebble.
- **Resolution.** Keep 2–3 pebbles (one tan). Leave out the sprig and the red specks (they read as berries, which W06
  owns as `LowBushBerries`, and the hero doesn't show them).

### 3.8 Ground: a soil halo, no patch
- **Evidence.** Close-up 3 says ground leaves overlap "rocks and soil". The assembled views show a pale warm halo
  (`#F5E8D8`, 33°, s 0.12, v 0.96) round the base, only just darker than the paper. No cell shows a soil disc edge,
  thickness or texture.
- **Resolution (decision §8.7).** **No soil patch** (as 054 §3.8). The game terrain is the soil. Rocks, pads, foot
  rosettes and the trunk foot sit on z 0. The halo is excluded by the masks.

### 3.9 "No texture noise" vs the user's colour rule
- **Evidence.** The notes ask for broad flat-shaded faces with no texture noise; the user wants rich, blended colour with
  broad Tint mottling (memory `lighting-not-paint`).
- **Resolution.** Several keys per material, blended by position and role; broad Tint per rosette, plank strip or rock
  facet (0.03–0.04), never per-triangle confetti.

### 3.10 Cast shadow and lighting
- The sheet is lit from the upper right (lime on the upper right of every rosette, dark lower left). The lighting does
  that; never paint it by facing. Render every `*_sheet` view with the studio floor hidden. The cool lavender of the
  rocks' shaded faces is light, not paint.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its parts-row cell

1. `tube(points, radii, sides, …)`. **Reuse `m054.tube`** (import, don't edit). It builds one closed tapering prism chain
   with mitred kinks and flat end caps. It builds the trunk, leaders, limbs, spur and twigs; **every waypoint is a hard
   kink**.
2. `branch_stem()` → the 8-sided planked trunk with three root flares (§2.2), the two leaders, the seven limbs and the
   spur (§2.3). Joins are ring-stack continuations or closed shells buried ≥ 0.12 (decision §8.5). Cut faces get
   `bark_light`. One function serves the hero and the `…BranchStem` part; the part shows all tips cut and bare.
3. `rosette(R, h, n, tiers, seed)` → one closed faceted lobed mound (§2.4). Build it by hand in bmesh, then check
   winding (§4.5). Large / medium / small are presets; the ground pads are `rosette(R, 0.5 R, n 3–5, 1)`. Check each
   preset against its parts-row cell before assembling: W : H, lobe count, blunt tips, flat underside.
4. `core(w, d, h)` → the dark flat-bottomed dome (§2.4).
5. `cluster(spec, seed)` → twigs from the tip + core + rosettes placed by §2.4's rules, in its own frame (the tip at the
   origin), so one function builds all seven clusters.
6. `flower(d, seed)` → petals, centre and under-leaf (§2.5), in its own frame.
7. `rock(spec)` ×5 (ring-stack hulls; `m054._rock` / `m054.pebble` or `m033._hull` can serve), `pebble()` ×3, `pad()` ×8, all through the
   ray-parity placement guard (`m047._Solids`, as 054 used it).
8. **Hero `GladeBush`** = stem + seven clusters on the tips + two foot rosettes + six flowers on rosettes + rocks,
   pebbles and pads, joined into one object of closed shells.
9. **Parts shot** (0, 15) laid out like the parts row: LeafClumpLarge, …Medium, …Small, BranchStem, Rock, GroundLeaves,
   Flower, gaps 1.0.
10. **Exploded shot:** the stem in the middle, the seven clusters lifted 1.5 off their tips with the tip joints shown,
    two flowers beside their tips, rocks and pads below.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:**
   - a low, wide, round-topped bush of faceted lime-topped rosettes;
   - an arched lower window with the planked trunk, its fork and two low limbs;
   - six white flowers on the front half;
   - two big pale rocks flanking the trunk foot, a flat stone, back rocks, lime ground pads.
2. **front_sheet / f34_sheet** per §2.7 (shares, fill, W : H, top profile, canopy-run bottoms, window, flower positions).
3. **rear / r34 / side / top** per §2.7.
4. **Close-up renders:**
   - `attach_cu` (−20, 25): the stem part's fork with one tip's cut face and its cluster lifted above it, against
     close-up 1.
   - `underside` (0, −89) on the LeafClumpLarge cluster and on the hero: a flat dark disc ringed by lobes, against
     close-up 2.
   - `rock_cu` (−30, 10) on RK2 with GL1 / a pad lapping its foot, against close-up 3.
   - `rosette_cu` (0, 35) on one large rosette: blunt lobes, ridges, broad facets.
5. **Contact counts** (§6): floating shells 0; every rosette chained to its core or the ground; every core to its tip;
   every flower to a rosette; buried 0.
6. **Hero size** per §2.7, plus a **scale shot** with a 5.5-stud marker beside the bush (the crown top at 0.82 of the
   marker).

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Trunk (8 sides × 4 bands, caps) + 3 root flares | 1 + 3 | 80 + 16 | 130 |
| Leaders and limbs (6-sided main runs, 5-sided arms, 2 kinks) | 9 | 36–48 | 330–400 |
| Twigs (4-sided, one per off-tip rosette) and the spur | ~14 | 10–12 | 150 |
| **Skeleton** | | | **≈ 610–680** |
| Cluster cores | 7 | 28–32 | 200–220 |
| Large rosettes (n 7, two tiers) | 7 | 80–84 | 560–590 |
| Medium rosettes (n 6, two tiers) | 14 | 68–72 | 950–1010 |
| Small rosettes (n 5, one tier) | 10 | 38–40 | 380–400 |
| **Foliage** | | | **≈ 2090–2220** |
| Flowers (5 petals, centre, under-leaf) | 6 | 80–90 | 480–540 |
| Rocks (ring-stack hulls) + flat stone | 5 | 26–36 | 150–170 |
| Pebbles | 3 | 10–14 | 30–40 |
| Ground pads (flattened rosettes, n 3–5) | 8 | 24–40 | 220–260 |
| **Dressing** | | | **≈ 880–1010** |
| **Hero** | | | **about 3580–3910 at the top of every range; aim 3600–3750** (limit 4000; **ceiling 3800**) |
| Parts: LeafClumpLarge / …Medium / …Small / BranchStem / Rock / GroundLeaves / Flower | | | 84 / 72 / 40 / 640 / 36 / 90 / 85 (each < 1000) |

- **This is tight.** If the hero passes 3800, cut in this order:
  1. medium rosettes to single-tip lower lobes (−12 each, −170);
  2. flowers to 4-vertex petal lenses (−20 each, −120);
  3. two medium rosettes from CT / CFL (−140);
  4. pads to 6 (−60).
  Never thin the trunk, never go below 28 rosettes, never subdivide.
- **Spend headroom** (if any) on an 8th lobe on the CT large rosettes (the crown's outline).

### 4.4 What to do better than W06's `LowBush` and the recent bushes

| Earlier | This one |
| --- | --- |
| W06: "flat saturated blob" of star clumps; few flowers | ~31 faceted blunt-lobed rosettes in seven clusters, scallops every ~0.75 studs, lime / mid / dark by height; six flowers at the sheet's spots |
| 040 m2: dark bushes read as palm or agave stars on visible trunks | lobes droop (lower tier tips at 0.42 h), blunt two-vertex tips, notches ≤ 0.25 R; no trunk visible under a rosette, only the stem in the window |
| 044 B2: spiky star bushes (kite / diamond leaves) | no kite outlines: every lobe tip ≥ 110°, rounded |
| 046 m4: "cabbage" domes of 7 big flat leaves, edge-on flaps, dark heart wedges showing | 5–8 small lobes per rosette, 31 rosettes; lobes tilted ≤ 60° (no edge-on flaps, ≤ 12 % of leaf area within 12° of edge-on in the f34); cores hidden from the f34 and front except through the window's dark interior |
| 047 r1: pads read as bunches of separate faceted balls | rosettes overlap 30–50 % on a core; clusters touch; one crown outline; tones by height across the cluster, not per ball |
| 036 / 047 r2 / 046: floating, hidden-stem or buried leaves | every rosette on its core (≤ 0.03) and chained through twig → tip → stem → ground; ray-parity guard for pads against rocks |

### 4.5 Stages 2 and 3
- **Stage 2:**
  - Every shell closed and manifold, with **0 bowties**. The likely spots are the rosette centres (apex fans), the
    blunt two-vertex tips, petal roots and limb kinks; use `M.fix_bowties`.
  - **0 winding errors per shell** (STAGES "Consistent winding"). Hand-built rosettes, petals and pads flip easily:
    `bmesh.ops.recalc_face_normals` per shell, then check every shell with `m054.shells_report`.
  - No zero-area faces; no n-gons except flat caps and the rosette undersides (triangulate those if the audit asks);
    corners ≥ 3°.
  - Origin at the bottom centre, transforms applied.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box, sd ≤ 1.8)

| Swatch | Box | Hex | HSV | Use |
| --- | --- | --- | --- | --- |
| LEAF DARK | (776,50,802,80) | `#417A32` | 108°, 0.59, 0.48 | start for `leaf_dark` |
| LEAF MID | (821,50,850,80) | `#669E25` | 88°, 0.77, 0.62 | start for `leaf_mid` |
| LEAF LIGHT | (867,50,896,80) | `#B8D117` | 68°, 0.89, 0.82 | start for `leaf_light` |
| ROCK | (914,50,943,80) | `#C2B7AD` | 29°, 0.11, 0.76 | start for `rock` |
| WOOD | (961,50,990,80) | `#966637` | 30°, 0.63, 0.59 | start for `bark` |

### 5.2 Rendered regions (`samp.py`, `samp2.py`; median / v > .7 / lit quartile / shade quartile)

| Region | Median | v > .7 | Lit Q | Shade Q |
| --- | --- | --- | --- | --- |
| Canopy f34 / front / rear / side / top | `#60A211` (87°, .90, .64) / `#66A40B` (84°, .93, .64) / `#4F920D` / `#65A409` / `#6DA805` | `#B4DE15` / `#B5DB0C` / `#AED80D` / `#ADD70A` / `#A6D306` | `#CCE918` / `#CBE70F` | `#1A500A` / `#1E5407` |
| Canopy by tone (front: light h < 76 / mid / dark h ≥ 96) | `#C0E20B` / `#5F9F06` / `#236414` | | | |
| Canopy tone shares (light / mid / dark %) | f34 31 / 37 / 32; r34 33 / 36 / 31; front 33 / 40 / 27; side 33 / 43 / 24; rear 27 / 37 / 36; top 33 / 54 / 13 | | | |
| Canopy bands (front, light / mid / dark %) | h .80–1.0: 66 / 28 / 6; .60–.80: 40 / 37 / 24; .40–.60: 28 / 47 / 25; .15–.40: 22 / 40 / 38 (rear .15–.40: 9 / 30 / 61) | | | |
| Cluster underside (cu2 disc) | `#3A5A1B` (90°, .70, .35), flat | | | |
| Crown interior (O) | `#040C01` near black | | | |
| Ground leaves: front (h < .13) / parts / cu3 | `#6E9304` (76°) / `#BAD509` (68°, .96, .84) / `#9CC606` (73°) | `#BCD304` | `#CDE007` / `#D8E810` / `#C3E112` | `#2C4104` / `#6B9107` / `#558306` |
| Wood f34 / front / rear | `#5F3611` (28°, .82, .37) / `#56320D` / `#542F0F` | `#C88332` / `#CE9A6E` / `#BF9B79` | `#B56E27` / `#BD7F36` / `#A26022` | `#331C04` / `#2B1803` / `#2D1A04` |
| Wood: f34 lit planks / cu1 bark / parts stem / exploded stem | `#C5792B` (30°, .78, .77) / `#925323` (26°, .76, .57) / `#7B471F` / `#834C1D` | | `#DD923A` / `#C77A31` / `#C27D36` / `#B97028` | `#A05F20` / `#512E11` / `#5C381D` / `#502E12` |
| Cut ends: pale / darker (exploded) | `#DD8C37` (31°, .75, .87) / `#8B5B36` (26°, .61, .55) | | | |
| Rock lit facets f34 / front / cu3 | `#DBC7AF` (33°, .20, .86) / `#DDC5AA` / `#EBD7C3` (30°, .17, .92) | | `#F4E3CF` (cu3) | |
| Rock shade facets f34 / cu3 | `#7F7B82` (270°, .05, .51) / `#74747B` — cool from the light | | | |
| Rock part (parts row) | `#CEBDB0` (26°, .15, .81) | | `#F7F3EA` | `#787272` |
| Flower petals / centre / under-leaf | `#F9F5ED`–`#FBFBF6` / `#FAD306` (50°, .98, .98) / `#507805` (81°, .96, .47) | | centre `#FCDD07` | centre `#F3AE07` |
| Tan pebble (exploded) | `#B79767` (36°, .44, .72) | | `#D0B07E` | `#826941` |
| Soil halo (not modelled) | `#F5E8D8` (33°, .12, .96) | | | |

### 5.3 How the colour works

- **Rosettes:** three keys **by height within each cluster and in the crown** (role and position, never facing).
  - **Light:** the upper 35 % of each cluster's rosettes, plus every rosette's upper-tier lobes above z 3.3.
  - **Mid:** the middle and lower-tier lobes.
  - **Dark:** the lowest rosettes and the lower tier of low-cluster rosettes.
  - CT carries the most light (the sheet's top band is 66 % light); CLL / CLR carry the most mid and dark (the low band
    is 22 / 40 / 38).
  - Blend with `K.blend(mode="blend", steps=3)` across lobe heights so a cluster goes lime → mid → dark without a hard
    band. Per-rosette Tint ±0.04.
  - **Light per lobe, not per face:** a whole lobe (its 2–3 facets) takes one blend step, so the radiating facets keep
    the lighting's contrast and the paint never follows facing.
- **Cores:** `leaf_under`, a deep green, hard against the rosettes. The flat underside shows from below as the sheet's
  `#3A5A1B`. The crown interior reads near-black in the window from occlusion, not paint.
- **Bark:** one warm brown (`bark`, 26–30°, R > G > B).
  - **`bark_light`** on cut faces and on every other plank strip's crest (35 %, the f34's lit strips, by strip index,
    not by facing).
  - **`bark_deep`** in the two grooves, at the fork crotch and the kink rings, and on the lowest 0.3 of the trunk and
    root flares.
  - Per-strip Tint ±0.04.
- **Ground pads:** `leaf_lime` (68–73°, yellower than `leaf_light`), with their lowest lobes 25 % `leaf_mid`.
- **Rock:** pale warm grey (`rock`). Tops a step lighter (`rock_light`, the top 30 % of each rock); feet a step deeper
  (`rock_deep`, the lowest 25 %), by height within each rock. R ≥ G ≥ B always; **never lavender or blue**, since the
  sheet's cool shade facets are light.
- **Flowers:** petals `petal` (warm white); centre `pollen` with its lowest ring 40 % `pollen_deep`; under-leaf
  `leaf_mid`.
- **Pebbles:** two `rock_deep`, one `pebble_tan`.
- **Hues stay apart:** bark 26–30°, cut wood 30–33°, pollen 48–52°, leaf lime 68–73°, leaf light 66–70°, leaf mid 84–90°,
  leaf dark 104–110°, leaf under 100–108°.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians where the sheet gives them, swatches where it doesn't. `K.sample` kinds:
`"brown"` for bark, `"stone"` for rock, `"vivid"` for the lime and yellow keys, `"green"` for leaf mid / dark.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m058_leaf_light` | canopy light-tone median `#C0E20B` ± 12 (lit `#CBE70F`; start `#B8D117`) | 66–70°, ≥ 0.88 | upper rosettes / upper lobes | rough 0.8, low spec |
| `m058_leaf_mid` | the LEAF MID swatch `#669E25` rendered lit ± 12 (mid-tone median `#5F9F06`) | 84–90°, 0.75–0.90 | middle lobes | rough 0.85 |
| `m058_leaf_dark` | the LEAF DARK swatch `#417A32` rendered lit ± 12 (dark-tone median `#236414`) | 104–110°, 0.58–0.75 | low rosettes, low lower-tier lobes | rough 0.9 |
| `m058_leaf_under` | cu2 disc `#3A5A1B` as rendered from below ± 12; start `#2E5A22` | 100–108° (**not** 90°: the sheet's 90° is warm light on dark green) | cluster cores | rough 0.95 |
| `m058_leaf_lime` | ground leaves: parts `#BAD509` ± 12 lit (front v > .7 `#BCD304`) | 68–73°, ≥ 0.9 | ground pads | rough 0.85, low spec |
| `m058_bark` | f34 / front whole-wood median `#5F3611` ± 15 together with lit planks `#C5792B` ± 15 (start `#966637`) | 26–30°, 0.70–0.85, **R > G > B** | trunk, limbs, twigs | rough 0.9 |
| `m058_bark_light` | cut ends `#DD8C37` ± 12 lit | 30–33°, 0.65–0.78 | cut faces, plank crests 35 % | rough 0.85 |
| `m058_bark_deep` | wood shade quartile seen lit, `#5A3416` ± 15 | 24–28°, 0.7–0.8 | grooves, crotch, kinks, foot | rough 0.95 |
| `m058_rock` | lit facets `#DBC7AF` ± 10 (start `#C2B7AD`) | 28–34°, 0.10–0.20, R ≥ G ≥ B | rocks, flat stone | rough 0.85, metal 0 |
| `m058_rock_light` | cu3 lit `#EBD7C3` ± 10 | 28–34°, 0.12–0.18 | top 30 % of each rock at 35 % | rough 0.85 |
| `m058_rock_deep` | the ROCK swatch `#C2B7AD` darkened to `#A89C92` | 24–30°, 0.10–0.15 | lowest 25 %, grey pebbles | rough 0.9 |
| `m058_pebble_tan` | `#B79767` ± 12 | 34–38°, 0.40–0.48 | one pebble | rough 0.9 |
| `m058_petal` | petals `#FBFBF6` ± 6 rendered; start `#F6F2EA` | 35–45°, ≤ 0.06, rendered v ≥ 0.93 | petals | rough 0.7 |
| `m058_pollen` | centre `#FAD306` ± 10 | 48–52°, ≥ 0.92 | centre domes | rough 0.6 |
| `m058_pollen_deep` | centre base `#F3AE07` ± 12 | 40–44°, ≥ 0.9 | centre lowest ring | rough 0.6 |

**Calibration warnings:**
- **The kit studio lights both halves** (042, 047, 054): calibrate `bark` to the whole-wood median and the lit planks
  together, and the leaves to the tone medians, not the lit quartile alone. Record the lit-shade bias. 054 had to lift
  its families in linear light after calibrating on the dome (bark ×1.4, leaf_mid ×1.5) because the crown shades
  itself. Expect the same here and re-measure on the bush's own renders.
- **Greens must not lean yellow or olive.** `leaf_mid` ≥ 84° and `leaf_dark` ≥ 104° on every median. Only
  `leaf_light` (66–70°) and `leaf_lime` (68–73°) are lime. Check the front canopy median within 15 of `#66A40B` and the
  tone shares.
- **Petals must stay white:** rendered petal median v ≥ 0.93, s ≤ 0.06 (not grey, not cream).
- **Bark must not go red or orange-flat:** R > G > B, hue ≥ 26°; the whole median stays dark (v ≤ 0.45 in the f34).
- **Rock never lavender:** R ≥ G ≥ B on every rock median; the cool shade comes from the light.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Rosettes:** per lobe by its height rank within the cluster (top light → middle mid → lowest dark), blended across 3
  steps. CT's ranks are shifted 0.15 lighter and CLL / CLR's 0.15 darker. Foot rosettes are mid with light tops. Cores
  are hard `leaf_under`. Hard edges where a lobe meets bark or a petal.
- **Stem:** `bark` base; `bark_light` 35 % on alternate plank crests (whole strip runs); `bark_deep` 40 % in the
  grooves, blended one facet out; a `bark_deep` ring (30 %) at the fork and at every kink; the foot's lowest 0.3 at 25 %
  `bark_deep`; hard `bark_light` on cut faces.
- **Rocks:** height bands within each rock. **Pads:** `leaf_lime` with the lowest lobes 25 % `leaf_mid`.
- **Hard edges only** where materials meet: cut face | bark, bark | leaf, petal | pollen, rock | pad.

### 5.6 Texture (Tint) and finish
- **Tint:** rosettes 0.04 per rosette (whole rosettes, never per triangle); bark 0.04 per plank strip + 0.03 broad; rock
  0.04 per facet; pads 0.03 per pad; petals 0.02.
- **Finish:** leaves 0.8–0.9, low spec; bark 0.9 (deep 0.95), cut 0.85; rock 0.85; petals 0.7, pollen 0.6. No emission.

### 5.7 Re-measure (final renders against the sheet, same masks)
- **Canopy:**
  - front median within 15 of `#66A40B`; v > .7 within 12 of `#B5DB0C`;
  - tone shares (light / mid / dark) 33 / 40 / 27 ± 8 in the front and 31 / 37 / 32 ± 8 in the f34;
  - the top band (h .8–1.0) ≥ 55 % light; the low band (.15–.4) ≥ 30 % dark.
- **Bark:** f34 whole median within 20 of `#5F3611`; lit planks within 15 of `#C5792B`; R > G > B.
- **Cut wood:** the spur's end within 15 of `#DD8C37`. **Rock:** lit facets within 10 of `#DBC7AF`, R ≥ G ≥ B.
- **Ground pads:** median within 15 of `#BAD509` lit (front ground-green median `#6E9304` in shade).
- **Flowers:** petals v ≥ 0.93, s ≤ 0.06; centre within 12 of `#FAD306`.
- **Shares** per §2.7.

## 6. Joins and contact (no floating dressing, no buried dressing)

- **Shells:** the stem is one or more closed shells (trunk + leaders as one ring-stack shell; limbs, twigs and the spur
  as closed shells buried ≥ 0.12, decision §8.5). Each core, rosette, petal, flower centre, under-leaf, rock, pebble and
  pad is its own closed shell. All are in one hero object.
- **Cluster chain:** rosette → core (or a neighbour rosette) within 0.03; core → limb tip (the tip's cut face 0.25–0.4
  inside the core); off-tip rosettes also get a 4-sided twig from the tip buried 0.15–0.3 in the core. **No rosette
  floating** off its core. A tilted rosette must still touch the core at its underside centre or rest on a neighbour.
- **No rosette buried:** its centre is outside the core, ≤ 25 % of its verts are inside the core, and none is more than
  50 % inside a neighbour. Count both per cluster and report them.
- **Low clusters and foot rosettes:** lowest lobes 0 … −0.03 below z 0. Their contact with the ground counts as a chain.
  CLL / CLR also chain through their cores to the limbs.
- **Flowers:** petal roots and the under-leaf within 0.03 of a rosette; no petal more than 0.05 inside a rosette; the
  centre dome within 0.03 of the petals. 036 had five whole flowers hovering: count flower shells chained.
- **Pads on rocks (cu3 "ground leaves overlap rocks"):** a pad may rest on a rock's foot, within 0.03 of it, but **no
  pad vertex more than 0.05 inside a rock** (ray parity against the full hero rocks after the final placement).
- **Rocks:** sunk 0.03; ≥ 0.15 clear of the trunk foot and root flares; never cutting a limb.
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**. A shell floats if its nearest distance
  to every other shell and the ground is > 0.03, or it doesn't chain to the ground. The chains are: petal → flower centre
  / under-leaf → rosette → core → twig / tip → limb → trunk → ground; pad → ground or rock → ground.
- **Count buried shells** (STAGES; 046, 047 round 2): **0 dressing shells more than 0.05 inside a rock, the trunk, a
  limb or a core.** Use 047 / 054's guard from the start (`_Solids`: stem + every rock + every core added as built; three
  skewed rays, two of three agree). Placement accepts ≤ 0.03. A pad or pebble that still cuts after its retries is moved
  outward along its azimuth, or dropped.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.
- **Reports:** reuse `m054.shells_report`, `contact_report` and `bury_report` (import, don't edit).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no particles, no pollen, no falling leaves, no fireflies. The cast
shadow and the soil halo are the render's.

- **Stage 5 (lighting): skip, and record why.** No emission, no lights. Studio notes (Requires Manual Validation):
  - the crown keeps lime tops and green bodies under the game sun (not olive, not pale);
  - the petals stay white, not grey;
  - the bark stays dark warm brown with pale cut ends;
  - the rocks stay pale warm grey;
  - the window's interior reads dark.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** The old W06 `LowBush` carried a `harvest_hit`
  socket because it was treated as harvestable. This sheet calls the bush decorative ("forest floor, paths and ruins")
  and shows no effect, so it gets no sockets unless the main session wants it harvestable (decision §8.11).
- **Collision:** hero `hull` (the old LowBush and 017 used hull; a player walks round a bush, and a hull over a
  6.4 × 5.8 × 4.5 dome is cheap). Parts: BranchStem `hull`, the three leaf clumps `hull`, Rock `hull`, GroundLeaves
  `box`, Flower `box` (decision §8.8). The exporter has no non-colliding option (`kit_nocollide` doesn't exist), so
  walk-through foliage would need a Studio-side `CanCollide = false`: note it in the export notes.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json` and the repo
text (`git grep`) for Bush, Shrub, Hedge, Scrub, Thicket, Bramble and the candidates:
- **W06:** `LowBush`, `LowBushLeafClumpLarge` / `…Medium` / `…Small`, `LowBushBranchStem`, `LowBushBranchStemB`,
  `LowBushBerries`, `LowBushFlower`, `LowBushDome`, `LowBushHedge`, `LowBushOpenWoody`. So **no `LowBush*` prefix** (a
  `LowBush` hero would collide outright, and `LowBushLeafClump*` exactly).
- **Other shrubs:** `BerryBushNode` / `BerryBush*` / `BerryShrub*` (017), `FiberShrub*` / `FiberPlantNode` (022),
  `ThornBush*` / `ThornShrub*` / `ThornScrub*` (024), `FrostBush*` / `FrostShrub*` (028), `HerbShrub*`, `HazelShrub*`,
  `ElderberryShrub*`, `RaspberryBush*`, `RosehipScrub*`, `SunpodShrub*`, `JuniperGroundShrub`, `HeartpodBramble`,
  `BloodberryThicket`, `SaplingBushy`, `HedgeBush`. Flowers: `MeadowDaisy*` and `Daisy*` exist, so no `Daisy` name.
- **`GladeBush`, `Glade*` and `m058` occur nowhere** (repo text, manifests, builders). `GladeBush*` contains no owned
  name as a substring.

| Object | Part | Why |
| --- | --- | --- |
| `GladeBush` | hero: branch stem, seven clusters, two foot rosettes, six flowers, five rocks, three pebbles, eight ground pads | a low leafy flowering bush of the forest floor, paths and ruins (the sheet's use); W06 owns `LowBush*` |
| `GladeBushLeafClumpLarge` | "Leaf Clump (large)": one large two-tier rosette (parts row) | the label |
| `GladeBushLeafClumpMedium` | "Leaf Clump (medium)" | the label |
| `GladeBushLeafClumpSmall` | "Leaf Clump (small)" | the label |
| `GladeBushBranchStem` | "Branch Stem (base)": trunk, leaders, seven limbs and the spur, all tips cut and bare | the label |
| `GladeBushRock` | "Rock (base)": RK1's shape | the label |
| `GladeBushGroundLeaves` | "Ground Leaves (optional)": three pads as in the parts row | the label |
| `GladeBushFlower` | "Flower (optional)": one flower with its under-leaf | the label |

- Palette keys `m058_*` (§5.4). Collection `Kit/M058 Low Bush`. No sockets (§7).

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **4.5 tall, crown 6.4 × 5.6** (recommended: the old LowBush's 4.5, under a character's eye line,
   flowers 0.6, rocks 1.8–1.9). Alternatives: 3.6 (the forage-shrub ceiling; flowers 0.45, window 1.6) or 5.0.
2. **Name (§8):** **`GladeBush` and the seven parts above** (recommended). Not `LowBush*` (W06), not `*Daisy*`.
3. **Crown plan (§2.4, §3.3):** **seven clusters (CT top, CFL / CR front, CBL / CBR back, CLL / CLR low at the sides
   reaching the ground) plus two foot rosettes, about 31 rosettes in all**, with front and rear governing positions and
   the side and top judged for content and plan (recommended). Alternative: copy the exploded's four clumps only (too
   sparse; the hero shows ~30 rosettes).
4. **Limbs (§2.3, §3.6):** **the exploded's six tips plus BACK-R, a mirrored BACK-L, so the back has two clusters; one
   bare cut spur visible** (recommended). Alternative: six tips with CB as one wide back cluster (the rear's two back
   shoulders then share one cluster).
5. **Stem shells (§6):** **trunk + leaders as one ring-stack shell; limbs, twigs and the spur as closed shells buried ≥
   0.12; no booleans** (recommended, as 054 decision 6), or weld per limb with ring junctions.
6. **Flowers (§2.5, §3.5):** **six on the front half and the crown top at the front / f34 positions; none on the back**
   (recommended), or seven with one more on the top-back to match the top cell.
7. **Ground (§3.8):** **no soil patch** (recommended, as 054), or a thin 0.05 soil disc (+40 tris, a new key).
8. **Collision (§7):** **hero `hull`; parts `hull`, GroundLeaves and Flower `box`** (recommended), or hero `precise`.
9. **Comparison cameras (§3.2):** **`front_sheet (0, 5)` governs positions, `f34_sheet (0, 15)` the read** (probe az −30 …
   +30, e 10–20); `rear_sheet (180, 5)`, `r34_sheet (180, 15)` (probe 150 … 210), `side_sheet (90, 5)`; kit `top`,
   `underside`; extras: parts shot, exploded, `attach_cu`, `rock_cu`, `rosette_cu`, scale shot. Floor hidden in every
   `*_sheet` render.
10. **Sinking (origin):** **rocks, pebbles and pads sink 0.03, never more**, so the bbox bottom stays within 0.03 of the
    ground and the origin is effectively at ground level (054 left its origin 0.1 below the trunk foot by sinking rocks
    0.1). Recommended.
11. **VFX (§7):** **none; stages 5 and 6 skipped and recorded** (recommended). Alternative: carry the old LowBush's
    `harvest_hit` socket if gameplay makes the bush harvestable (a gameplay call, not on the sheet).
12. **Exported parts (§8):** **the hero plus the seven labelled parts** (recommended: the sheet has a "REUSABLE PARTS"
    row), or the hero plus the three leaf clumps and the stem only.
13. **Colour (§5):** **rosettes by height role to `#C0E20B` / `#669E25` / `#417A32` (front canopy median `#66A40B`), cores
    `leaf_under` 100–108°, ground pads `#BAD509`, bark `#5F3611` with lit planks `#C5792B` and cut ends `#DD8C37`, rock
    `#DBC7AF`, petals white `#FBFBF6`, centres `#FAD306`** (recommended).
14. **Budget (§4.3):** **4000 limit, ceiling 3800, about 3600–3800 planned (skeleton ≈ 650, foliage ≈ 2150, dressing ≈
    950), every part under 1000; the §4.3 cut order if over** (recommended).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **Stem hidden in the foliage (the user's tree rule; 047 round 1 "stub limbs, hidden twigs").**
   - T 7.6 ± 3 % in the front, 8.4 ± 3 in the f34, 9 ± 3 in the rear, almost all below h .6.
   - The window open at f .25–.80 to h .42–.50: the middle canopy-run bottoms .35–.50.
   - The trunk visible from the ground to the fork in the front, rear and f34. LOW-L and LOW-R each ≥ 0.5 studs bare;
     the spur's cut end visible.
2. **Palm or agave stars (040 m2, 044 B2).** Rosette lobes droop (the lower tier at 0.42 h), tips blunt (two verts, ≥
   110°), notches ≤ 0.25 R. No flat radiating points; no bare trunk under a rosette.
3. **Cabbages (046 m4, 018).** No big flat leaves: 5–8 lobes per rosette, ~31 rosettes. No edge-on drooping flaps
   (≤ 12 % of leaf area within 12° of edge-on in the f34). Cores hidden from the f34 and front except as the window's
   dark interior.
4. **A pile of separate balls (047 round 1).** Rosettes overlap 30–50 % on their cores and clusters touch, giving one
   crown outline with scallops every ~0.75 studs (front 20 ± 6). Tone by height across the cluster, so each rosette is
   not its own lit ball.
5. **Spiky leaves (memory `kit-quality-bar`).** No kite or diamond lobes, no serrated edges, no strong V midrib folds.
   Ridges are gentle (the lobe's centre ridge rises ≤ 0.12 R above its flanks).
6. **Floating or buried dressing (STAGES; 035 / 036; 046; 047 round 2).**
   - 0 floating shells.
   - 0 rosettes with their centre inside the core or more than half inside a neighbour.
   - 0 pads, pebbles or flowers more than 0.05 inside a rock, the stem or a core (ray parity after the final placement).
   - 0 flowers hovering: every petal chained.
7. **Pale, olive or yellow canopy (W06 "flat saturated blob"; 047 plants yellow).** The front canopy median is within 15
   of `#66A40B`; `leaf_mid` ≥ 84°, `leaf_dark` ≥ 104°; the tone shares are within ±8. The core underside is dark green,
   not olive.
8. **Grey petals.** Rendered petals v ≥ 0.93, s ≤ 0.06.
9. **Colour by facing (042 ruling).** Tones by lobe height rank and cluster; `bark_light` by plank index and cut faces;
   rock bands by height. `K.check` facing correlation < 0.5 per material.
10. **Flat orange or red bark (W05, W06).** f34 whole median within 20 of `#5F3611`, hue 26–30°, R > G > B.
11. **Egg, mauve or blue rocks (M034, M037).** Angular blocks with 10–14 broad facets and flat bases; R ≥ G ≥ B.
12. **Winding (044) and bowties.** 0 faces wound against their neighbours per shell. Check every hand-built rosette, pad
    and petal, and every mitred kink ring. `M.fix_bowties`; corners ≥ 3°.
13. **Over budget from the rosettes.** Count tris per cluster as you go (CT ≤ 380, the others ≤ 330 including the core
    and twigs). Cut per §4.3 before thinning the stem.
14. **Origin below the ground (054 note).** Sink rocks and pads 0.03 at most, so the hero doesn't stand proud when it is
    placed on terrain.
15. **Names and scope.**
    - No `LowBush*`, `*Daisy*`, `BerryBush*` or other owned names.
    - Only one agent drives a Blender session at a time.
    - No commits, pushes or exports in stage agents.
    - Don't edit the frozen shared helpers, `m054.py`, `m047.py`, `m044.py` or `lib/vfx.py`: import from them.
    - Don't touch other models' collections.

## Decisions (main session, 2026-10-30)
All 14 recommendations are accepted.
1. **Size.** 4.5 tall, with a crown of 6.4 × 5.6.
2. **Names.** `GladeBush` plus the seven parts; keys `m058_*`. Never `LowBush*` or `Daisy*`.
3. **Crown plan.** Seven clusters of about 31 rosettes. The front and rear cells set positions; the side and top cells are judged for content and plan only.
4. **Limbs.** Seven, plus one visible bare spur. **The stem must show** in the arched window (the user's tree rule).
5. **Stem shells.**
   - Trunk and leaders: one ring-stack shell.
   - Limbs and twigs: closed shells, buried at least 0.12.
   - No booleans.
6. **Flowers.** Six, on the front half only, with white petals and yellow centres. They must sit on their rosettes and never hover.
7. **Ground.** No soil patch.
8. **Collision.** Hero and parts `hull`; ground leaves and flower `box`.
9. **Cameras.** `front_sheet (0, 5)` and `f34_sheet (0, 15)`.
10. **Sinking.** Rocks, pebbles and pads sink at most 0.03. The trunk foot sits at the bounding-box bottom, so the origin offset is 0.
11. **VFX.** None; stages 5 and 6 skipped and recorded.
12. **Exports.** The hero plus all seven parts.
13. **Colour.**
    - Use the colours as listed. Core undersides use dark green at 100–108° as a role (the core).
    - Blend by position and role, **never by facing**.
    - The canopy must not read olive or yellow.
    - Bark is warm brown, not red. Rocks are never lavender.
14. **Budget.** Limit 4000, ceiling 3800, every part under 1000.

**Rosettes.** Broad lobes with blunt tips (each tip at least about 110°), shingled into clusters. **No palm or agave stars, cabbages, balls or spikes** (M040, M044, M046, M047, M054 round 1).

**Packaging.** 0 winding errors and **no floating or buried dressing**.

**Helpers.** `m054.py` is not committed yet, so copy its helpers rather than importing them, unless it has been committed by the time you build. The committed `m047.py` and `m053.py` may be imported.

**Binding.** The front shares in §1 (green 77, wood 7.6, each ±4) and fill.
