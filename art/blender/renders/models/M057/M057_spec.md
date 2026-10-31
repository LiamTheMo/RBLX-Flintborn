# 057 Ancient Tree — spec

Reference: `art/blender/assets/references/057.png` (1024 × 1536 px). INDEX.md row 57: "Flintborn Ancient Tree Model Study".
The sheet's own header reads **"54 / 132  FLINTBORN — INDIVIDUAL MODEL STUDY"**, title **"ANCIENT TREE"**, subtitle
**"MASSIVE TRUNK / BUTTRESS ROOTS / HIGH CROWN"** (our number is INDEX's 057, §3.1).
Builder: `art/blender/kit/mcp/m057.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows no effect** (§7). Trees (memory
`kit-tree-detail`): "take the dead tree and add leaves to it"; "pay more attention to the details: the branches, the
different views"; roots "snaking out over the ground". Scale (memory `kit-relative-scale`): the user asked for the
ancient tree to be **large**, clearly bigger than the other trees, judged against the 5.5-stud character. **This model
is 053's skeleton pattern grown into a giant: a hollow, buttressed, twisted trunk with a dark cleft and arch at its foot,
eight snaking buttress roots, four plug-in limb modules and seven leaf clumps (plus one small trunk sprout) with lime
moss strands hanging from them.** The limbs must read between and under the clumps in every view, and the trunk top
must show from above (047 round 1 failed on stub limbs and hidden twigs).

Sheet text (paraphrased):
- **"MATERIAL PALETTE (MAIN)"** (top right, four labelled swatches): Bark (Main), Bark (Light), Foliage, Rock.
- **Assembled views:** "ASSEMBLED — FRONT THREE QUARTER" and "ASSEMBLED — REAR THREE QUARTER".
- **Orthographic row:** "FRONT VIEW", "SIDE VIEW", "REAR VIEW", "TOP VIEW". Front, side and rear are near copies of one
  drawing (§3.3).
- **"EXPLODED CONSTRUCTION — MAIN REUSABLE PARTS":** labels "Crown Module", "Branch Module", "Trunk Core", "Root Module
  A", "Root Module B", "Root Module C". Drawn: five crown modules (each a leaf clump on a short faceted stub; the right
  one with three moss strands), four branch modules (two Y-shaped modules dashed to the trunk top, two side modules
  with a spur, double-arrowed to side bosses), the trunk core (a fluted, flared column with a pale cut top carrying two
  socket holes, two square side bosses, a flared foot), three root modules (A left, B right, C in front, each a thick
  faceted log with a hollow joining end and split toes), two slate rocks and a pebble, four pointed grass tufts.
- **"CONSTRUCTION DETAILS":**
  - "TRUNK TOP JUNCTION": the trunk core's pale cut top (about ten broad facets, dark radial cracks from the centre)
    with three limb logs plugging in: two from above, one from the side with a pale round peg; every log end is a flat
    pale ring round a dark bore.
  - "ROOT MODULE UNDERSIDE": "Joining Surface (flat, simple)" — a root log's end: an octagonal hollow tube with pale
    rim facets and a small peg inside the dark bore.
  - "TRUNK THICKNESS (CROSS-SECTION)": "Broad Faces Low Poly Style" / "Simple Hollow Form" — the trunk cut low: a thick
    faceted wall (pale cut rim, broad bark planks outside) round a dark brown hollow.
- **"KEY MODELING NOTES":** chunky, stylised low-poly forms with broad flat-shaded faces; trunk built from a modular core
  and branch modules, with separate root modules; foliage as simple clustered leaf clumps with hanging moss strands;
  a clean, readable silhouette, no photoreal detail; consistent wood, leaf and rock materials from the Flintborn style
  guide (§3.9).
- **Game context and the old kit:**
  - **W05 row 2 `AncientTree`** (`art/blender/scripts/kit/W05/ancient_tree.py`, goals
    `art/blender/renders/kit/W05/ancient_tree_goals.md`, `ancient_vs_oak_scale.png`) is the old kit's take on the same
    subject: 36.0 × 37.8 × 34.7, 7810 tris on an 8000 budget, seven buttress roots, a seven-clump crown with an open
    centre, twelve moss strands, and three variants (`HollowTrunk` with a walk-in cave, `ForkedGiant`, `ResinBearing`).
    `MODEL_PROGRESS.md` row 61: "squat cone trunk; flat pale crown, no vines; hollow variant not hollow". **W05 owns
    every `AncientTree*` name, R08 every `AncientRoot*`** (§8).
  - **Sister sheets:** 047 Old Pine (`GnarledPine`, 20 tall, committed), 053 Dead Tree (`TwistedSnag`, 18 tall,
    committed: the skeleton pattern), 054 Broadleaf Tree (`ShadeTree`, 20 tall, being modelled: the clump-on-limb
    pattern; its study left room for 057 to be the biggest). §1.5 keeps 057 apart.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Paper `#FBF8F0` (251, 248, 240),
tolerance 12. Measured grey rules: header y 21–22; frame x 8–9 / 1014–1015; assembled row bottom y 575–578; ortho row
y 578 / 837 with dividers x 265, 511, 761; lower frames y 842–843 / 1378–1379 / 1498, x 702 (exploded | details) and
712–713.
- **Cells** (`m.V`, `m.X`): f34 (12,122,509,540); r34 (514,122,1012,540); front (12,582,263,815); side (268,582,509,815);
  rear (514,582,759,815); top (764,582,1012,815); exploded (12,845,700,1376); cu1 "trunk top junction"
  (714,893,1012,1070); cu2 "root module underside" (714,1098,1012,1262); cu3 "trunk thickness" (714,1293,1012,1497).
- **Blanked text** (`m.TITLES`): the palette box (728,30,1012,150), which overlaps the r34 cell; the exploded title and
  labels; the close-up titles and call-outs.
- **Swatches** (squares about 42 × 43 at y 72–115): Bark (Main) x 748–790, Bark (Light) 815–857, Foliage 881–923, Rock
  947–989 (medians of the inner box, sd ≤ 1.4).
- **Masks** are `cls()` in `m.py` (054's, unchanged; HSV, h in degrees, in this order): **X** cast shadow; **G** green
  (h 50–180, s ≥ 0.30, v ≥ 0.12: leaves, strands, grass, moss); **T** wood (h < 50, s ≥ 0.30, v ≥ 0.12); **R** rock
  (s < 0.30, v 0.22–0.95); **O** other (outlines, the cleft and arch, the darkest creases). Canopy = G above h 0.28;
  ground green = G below h 0.20. The class previews (`cls_mont.png`) were checked by eye: rocks, the cleft, the strands
  and the moss band all land in their classes.

**Scratch study material** (no Blender) in
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m057_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe`.
- **Helpers:** `m.py` (masks, boxes, `silhouette()`), `zoom.py` (`zoom.py x0 y0 x1 y1 scale out.png [grid]`),
  `comps_053.py` (`label()`), `woodmap.py`, `tonemap.py` (054's, pointed at 057).
- **Measurements:** `measure.py` (bbox, W : H, shares, fill, profiles, fifths), `measure2.py` (canopy top / bottom per
  column, canopy vs ground green, wood above h .45), `trunk2.py` (outer wood extent per height), `strands.py` (hanging
  moss strands), `polar_top.py` (top outline radius per 3°, limb-arm histogram), `clumps_top.py` (seven clump sectors and
  centroids), `samp.py` / `samp3.py` (colour per region: canopy tones and bands, wood, rocks, strands, moss, cleft, cut
  faces), `sw.py` (swatches), `comps.py` (rock and plant blobs), `expl.py` (exploded and close-up blobs), `scallops.py`,
  `lines.py`.
- **Zooms:** `z_f34.png`, `z_r34.png`, `z_ortho.png`, `z_front.png`, `z_side.png`, `z_rear.png`, `z_top.png`,
  `z_expl.png`, `z_cu.png`, `z_pal.png`, `z_f34base.png`, `z_r34base.png`, `z_frontbase.png`, `z_sidebase.png`; wood maps
  `w_front.png`, `w_f34.png`, `w_r34.png`, `w_side.png`, `w_rear.png`; tone maps `t_front.png`, `t_top.png`; masks
  `cls_*.png`, `cls_mont.png`.
- **On our renders:** copy 054's `measure_render.py` (or 047's) and point it at this folder's `m.py` (paper `#FBF8F0`).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a standalone giant tree with its own base dressing (no ground patch, §3.8). Hero budget
  4000 tris, each part under 1000. The plan in §4.3 lands at about 3750–3850.
- **Overall read (check this first).** A **giant, round-crowned ancient tree**:
  - a **massive bell-shaped trunk** of twisted, plank-shingled strands (waist Ø ≈ 0.30 H across, 0.23–0.26 H deep)
    flaring through **eight snaking buttress roots** that start high on the trunk (h .35) and run out over the ground
    to split toes (reach 0.37–0.46 H);
  - **the trunk is hollow at its foot**: a tall **narrow dark cleft** on the front and a taller, wider **pointed dark
    arch** on the back open into a dark cavity, with slate rocks and a few plants inside;
  - at about half height **two thick low limbs** run out left and right under the side clumps, and the trunk ends at
    h ≈ .60 in a **cut top junction** from which **two Y-shaped modules** rise into the upper clumps;
  - **seven rounded leaf clumps** sit in a ring round an **open centre** (from above, the brown limb star and the trunk
    top show in the middle): three high (back-right, back-left, front-right), two low at the sides (left, right) and two
    lower ones tucked in (left-back, front-left), plus a **small sprout clump** on the trunk front-left;
  - **lime moss strands** hang from the clump undersides and limbs (about 12 round the crown);
  - **lime moss patches** on root tops and the trunk front; **slate-grey faceted rocks** (two tall slabs), **pointed lime
    grass tufts** and a **lime moss band** on the ground round the roots.
  - It reads **green over wood**: in every side view the canopy is 43–47 % of the silhouette, ground green 6.5–9 %,
    wood 37 % (of which 10.6–13.6 points are the limbs and upper trunk above h .45), rock 4–7 %, dark O 4–5 % (the
    cleft, arch and creases: O below h .35 is 1.6–2.4 % of the silhouette).
  - The crown is **about as wide as the tree is tall** (front W : H 1.023, rear 0.995), its lowest edge at h .33–.35
    under the side clumps, round in plan (top W : D 1.067) with **seven clefts round the outline**.
- **Focal silhouettes, in order:**
  1. The trunk's **bell**: a waist at h .40, a concave flare through h .30 / .20 / .10 (0.39 / 0.60 / 0.73 of H wide in
     the front) to the root toes at 0.85 H; the twisted strands and the dark cleft at its foot.
  2. The crown's outline: a scalloped dome — peak (back-right clump) at h 1.0, shoulders at h .89–.96, side clumps
     falling to h .55–.62 at the rims and hanging to h .33–.43 underneath, moss strands below them.
  3. The skeleton under the crown: the two low limbs under the side clumps, the trunk top junction and the Y modules in
     the gap under the high clumps (canopy bottom row gap at x .00–.05, h .65).
  4. Eight roots splaying to the ground with split toes; rocks and tall tufts between them; the dark arch at the back.
- **Target size: 32.0 tall (top of the back-right clump), crown 32.7 wide (X) × about 30 deep, trunk waist 9.4 × 8.0 at
  z 12.8, root reach r 11.5–14.5** (decision §8.1). Tolerances: height ±0.6, crown width 32.7 ± 1.2.
  - **How it was derived.** The front cell's silhouette is 227 × 222 px (H = 222, ground y 809), so **6.94 px / stud at
    H 32**; the f34's 445 × 408 px gives 12.75 px / stud; the top cell is 222 × 208 px at the front cell's scale
    (32.0 × 30.0). Outer wood extent per height (`trunk2.py`, the leftmost and rightmost T pixel, fraction of H from
    the trunk axis):

    | Height (z at 32) | front | side | rear | f34 | adopted (studs) |
    | --- | --- | --- | --- | --- | --- |
    | h .05 (1.6): root toes | −.387 … +.459 | −.350 … +.359 | −.341 … +.400 | | root reach r 11.5 (±Y) … 14.5 (±X) |
    | h .10 (3.2) | −.360 … +.374 | −.209 … +.295 | −.327 … +.345 | −.493 … +.493 | roots at r 11.7 (X), 9.5–10 (Y) |
    | h .15 (4.8) | −.320 … +.338 | −.277 … +.259 | −.295 … +.318 | | |
    | h .20 (6.4) | −.293 … +.311 (.604) | −.245 … +.236 (.481) | −.245 … +.282 (.527) | | root shoulders 19.3 across X, 15.4 across Y |
    | h .25 (8.0) | −.230 … +.266 (.496) | −.177 … +.177 (.354) | −.195 … +.205 (.400) | −.338 … +.360 | 15.9 X, 11.3 Y (roots on the flare) |
    | h .30 (9.6) | −.198 … +.194 (.392) | −.150 … +.145 (.295) | −.173 … +.173 (.346) | | 12.5 X, 9.4 Y |
    | h .35 (11.2) | .324 | .268 | .277 | | 10.4 X, 8.6 Y |
    | **h .40 (12.8): waist** | **.298** | **.232** | .264 | .362 | **9.4 X × 8.0 Y** |
    | h .45 (14.4) | .325 | .264 | .314 | .336 | 10.4 with the limb bases |
    | h .50 (16.0): low limbs | −.324 … +.288 | −.323 … +.236 | −.291 … +.355 | −.179 … +.191 | limb runs to ±10.4 |
    | h .55 (17.6) | −.248 … +.369 | −.159 … +.355 | −.277 … +.050 | −.326 … +.343 | limbs rise into L and R |
    | h .60 (19.2) | −.095 … +.270 | −.114 … +.127 | −.073 … +.118 | | trunk top junction Ø 6.6 at z 19.5 |
    | h .65 (20.8) | −.005 … +.113 | +.059 … +.136 | −.095 … +.205 | −.051 … +.284 | the Y modules' arms (leaders) |

  - **Why 32.** 054 Broadleaf and 047 Old Pine are 20, 053 Dead Tree 18; the user wanted the ancient tree clearly the
    biggest and earlier approved a 1.6× step for W05's ancient tree. 32 = 1.6 × 20, near W05's 34.7. At 32 the sheet's
    proportions give: the **lowest leaves at z 10.6–11.2** and the **strand tips at z 10–16** (4.5+ above a 5.5
    character's head), the low limbs at z 15–18, the trunk top at z 19.5, a **9.4-stud waist**, root shoulders at z 6–8
    and **19 across**, and the **back arch 10.5 tall × 3.8 wide at the ground** (a player can step into it, §3.6). At 28
    the arch is 9.2 × 3.3 and the strands hang to 8.8; at 36 the crown is 37 wide (a large footprint on the map).
  - **Against the character (5.5):** the tree is 5.8 C tall; the crown bottom at 2.0 C; the low limbs at 2.8–3.2 C;
    the waist 1.7 C wide; the roots reach 2.1–2.6 C from the axis; the arch 1.9 C tall.
- **Build frame:** front −Y, +X right, ground z 0. Trunk axis at (0, 0), **upright** (the trunk's wood centre moves less
  than ±0.01 H from h .25 to .45 in every view). The crown centre sits about +1.1 Y behind the axis (top cell: crown
  Y −13.8 … +16.0) and about 0.2 left of it (X −16.3 … +15.6): record the origin offset (bbox bottom centre).

### 1.2 Measured views (`measure.py`, `measure2.py`)

| View (box) | Silhouette bbox (px) | W : H | G | T | R | O | fill | canopy G | ground G | T above h .45 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (12,122,509,540) | 57–501 × 131–538 (445 × 408) | **1.091** | **51.5 %** | **36.6** | 7.0 | 5.0 | 0.652 | 42.7 | 8.8 | 10.6 |
| Rear three-quarter (514,122,1012,540) | 534–948 × 150–536 (415 × 387) | 1.072 | 52.2 | 36.8 | 5.9 | 5.1 | 0.655 | 45.7 | 6.5 | 11.6 |
| Front (12,582,263,815) | 26–252 × 588–809 (227 × 222) | **1.023** | **54.4** | **37.0** | 4.3 | 4.3 | 0.613 | 46.3 | 8.1 | 11.1 |
| Side (268,582,509,815) | 285–492 × 589–808 (208 × 220) | 0.945 | 52.7 | 37.6 | 5.2 | 4.5 | 0.572 | 45.2 | 7.5 | 13.6 |
| Rear (514,582,759,815) | 524–742 × 588–807 (219 × 220) | 0.995 | 54.3 | 37.1 | 4.3 | 4.2 | 0.591 | 46.6 | 7.7 | 10.6 |
| Top (764,582,1012,815) | 777–998 × 594–801 (222 × 208) | 1.067 (W : D) | 84.8 | 8.9 | 1.8 | 4.5 | 0.654 | | | |

- Shares are of the silhouette (O included, X excluded). **T above h .45** = limbs, the trunk top and the leaders
  showing through and under the crown: **10.6–13.6 % in every side view — the skeleton visibility target** (§9.1). T
  between h .28 and .45 (the bare trunk below the crown) is 8.2–9.4 %.
- **Verifier tolerance:** G ±4, T ±4, R ±3 points; W : H ±0.06; fill ±0.05; T above h .45 ≥ 9; positions ±0.04 H.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.1 W): one dome, peak right of centre.

| f | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .61 | .75 | .82 | .86 | .90 | .99 | .99 | .98 | .90 | .80 | .63 |
| r34 | .63 | .76 | .87 | .96 | .94 | .98 | .94 | .90 | .80 | .69 | .58 |
| Front | .54 | .70 | .82 | .92 | .89 | 1.00 | .95 | .96 | .85 | .76 | .60 |
| Side | .55 | .70 | .72 | .85 | .85 | .93 | .99 | .96 | .95 | .75 | .62 |
| Rear | .58 | .75 | .84 | .90 | .96 | 1.00 | .92 | .84 | .78 | .68 | .54 |

**Width per height** (silhouette width at h .0 → 1.0 as a fraction of W):

```
f34    .15 .97 .85 .57 .54 .92 .99 .90 .77 .42 .08
r34    .17 .87 .75 .44 .81 .99 .98 .85 .57 .49 .07
front  .02 .82 .65 .40 .71 .95 .97 .86 .61 .48 .03
side   .16 .76 .53 .34 .71 .94 .97 .86 .62 .39 .03
rear   .49 .80 .58 .36 .78 .95 .94 .74 .58 .39 .05
```

- Reading (front): h .1 roots, rocks and tufts across .82 of W; h .2 the root shoulders (.65); **h .3 the bare bell
  only (.40 of W: keep it; the strands start just above)**; h .4 the side clumps' undersides and strands appear (.71);
  h .5–.6 the crown at its widest (.95–.97); h .7–.9 the dome narrowing (.86 / .61 / .48); 1.0 the peak.

**Canopy outline per column** (front, x from the trunk axis as a fraction of H, every 0.05 from −0.50 to +0.50;
canopy = G above h .28, so the strands count):

```
x      -.50 -.45 -.40 -.35 -.30 -.25 -.20 -.15 -.10 -.05  .00  .05  .10  .15  .20  .25  .30  .35  .40  .45  .50
top     .55  .60  .69  .71  .81  .89  .91  .91  .91  .97 1.00  .98  .93  .95  .96  .88  .85  .76  .76  .72  .62
bottom  .52  .43  .42  .35  .43  .58  .46  .56  .44  .45  .65  .66  .42  .56  .39  .46  .48  .36  .45  .46  .55
```

- The **bottom row is the clump and strand layout**: the left clump L with its strands hangs to .35–.43 at x −.45…−.30;
  FL and the trunk sprout at .44–.58 (x −.25…−.05); **a gap at x .00–.05 where the bottom is .65–.66** — the trunk
  top and the Y modules show there under the back-right clump; R and its strands at .36–.48 (x +.20…+.45). Rear: gap
  .61–.65 at x −.05….00; side: gap .57–.63 at x −.10…+.05.

**Height fifths** (bottom → top, % of each class):
- Front: G 14.2 / 1.1 / 25.8 / 37.2 / 21.8; T 29.6 / 33.5 / 29.6 / 7.3 / 0.0; R 62.7 / 7.1 / 16.7 / 9.7 / 3.9.
- f34: G 16.1 / 2.1 / 18.7 / 41.6 / 21.5; T 26.6 / 37.7 / 25.8 / 9.8 / 0.2.
- Rear: G 13.6 / 1.2 / 27.2 / 39.0 / 18.9; T 31.4 / 32.8 / 28.7 / 7.0 / 0.0. Side: T 28.1 / 29.2 / 33.7 / 8.9 / 0.0.
- **Wood fifth 2 (h .2–.4) is the heaviest (29–38 %)**: the bell is the mass of this tree. **Wood fifth 3 (h .4–.6)
  holds 26–34 %** (the waist, the low limbs, the junction) and **fifth 4 (h .6–.8) 7–10 %** (the Y modules and the
  leaders inside the crown). A model whose limbs hide in the clumps drops fifth 4 under 5 % (047 round 1).
- R in fifths 3–4 of the orthos (≈ 1 point of the silhouette) is grey shade on the strands and bark, not rock.

**Scallops** (leaf-lobe peaks round the crown outline, 054's polar scan): front 34, side 33, rear 36, f34 43, r34 29,
top 44. At H 32 that is **one lobe about every 2.8 studs**: the visible leaf cards are **about 3–4 studs across**.

**Hanging moss strands** (`strands.py` plus a count by eye on the zooms; the automatic count misses strands whose tops
merge with a clump): **front 8** (X −13.1, −11.8, −8.9, −7.8 under L / FL; +5.2, +6.6, +8.6, +9.8 under R / FR),
**f34 9–10**, **r34 9**, **side 6**, **rear 7**. Visible length below the clump 0.05–0.13 H (**1.6–4.2 studs**), width
0.015–0.035 H (**0.5–1.1 studs**), lowest tips at h .32–.50 (**z 10–16**). Each strand is a lime drip, thick under the
clump, thinning, with a **rounded bulb tip** (the exploded's right crown module shows three).

**Ground dressing blobs** (`comps.py`; x as a fraction of H from the trunk axis, h fraction of H; studs at 32):

| View | Rocks | Plants |
| --- | --- | --- |
| Front | **tall slate slab** left −.365…−.29, h .06–.20 (2.4 wide × 4.5 tall, leaning on the left root); small −.37…−.30 h ≤ .07; −.23…−.20; front −.09…−.03 h ≤ .08 (1.9 wide); **inside the cleft** .00…+.07 h .11–.19; small +.07…+.10, +.14…+.17; right +.30…+.36 h .05–.10 (1.9 × 1.7) | far-left tuft −.46…−.34 (top h .14); left group −.33…−.10 (top .19); centre moss and sprigs −.16…+.16 (a continuous band); right group +.25…+.46 (top .14) |
| Rear (rear −x is world +X) | **tall slab** −.37…−.25 h .10–.20 (world X +8…+11.8); low −.37…−.27; small −.23…−.19, −.06…−.04; **in the arch** +.01…+.05 h .09–.15; small +.11…+.15; +.27…+.32 h ≤ .07 | −.43…−.33; −.32…−.09 (top .17); centre band −.14…+.22; +.23…+.44 |
| f34 (12.75 px / stud) | big low front-left (127–187, 502–534) 4.7 × 2.5; **big front-centre (218–274, 486–534) 4.4 × 3.8, the tallest front rock**; tall slate slab left (106–138, 428–467) on the left root's flank; **in the cleft** (291–319, 438–474); right (360–394, 503–525) 2.7 × 1.7; tall right (430–465, 438–472) 2.7 × 2.7; (432–461, 485–513); small far-left (64–72), (111–130, 495–520) | far-left (59–114, 455–524); the moss band (117–295, 437–537) with sprigs; left-front root moss (138–178, 403–436); (201–228, 444–458); front root moss and sprigs (253–296, 451–490); right group (299–369, 461–524); right-root moss (339–363, 403–418); far-right (404–488, 462–521) |

**Plan (top cell, `t_top.png`, `polar_top.py`, `clumps_top.py`).** The hub (trunk axis) at sheet ≈ (890, 705); sheet up =
+Y (back). The outline's polar radius dips at **seven clefts** (az 37°, 102°, 138°, 171°, 219°, 264°, 336°; az 0° = +X,
counter-clockwise), so **seven clumps** (studs at 6.94 px / stud):

| Clump | Sector (az) | Centroid (X, Y) | Outer reach | Lime share from above |
| --- | --- | --- | --- | --- |
| **BR** back-right (the biggest, highest) | 37–102° | (3.5, 10.2) | 15.6 | 67 % |
| **BL** back-left | 102–138° | (−5.1, 8.5) | 14.3 | 82 % (the top of the crown) |
| **LB** left-back | 138–171° | (−9.7, 4.7) | 15.3 | 13 % (low, tucked under) |
| **L** left (low) | 171–219° | (−10.4, −2.5) | 15.7 | 41 % |
| **FL** front-left | 219–264° | (−4.6, −8.5) | 13.5 | 8 % (low, tucked under) |
| **FR** front-right (high) | 264–336° | (4.5, −7.8) | 13.8 | 67 % |
| **R** right (low) | 336–37° | (10.2, 1.4) | 15.0 | 73 % |

- **The open centre:** between the clumps the brown **hub** shows (T 8.9 % of the top view) within r ≈ 4.3–6.5 of the
  axis: a pale cut top (the trunk top junction) and **limb arms** toward az ≈ 5–15° (R), 55–75° (BR), 100–140° (BL /
  LB, spread), 180–190° (L) and 230–240° (FL); nothing shows toward az 260–350° (covered by FR). Leaf tones from above:
  light 54 %, mid 41 %, dark 4 %. Seven white sky gaps show between the clumps and the hub (§9.2).

### 1.3 Silhouette and composition per view

**Front three-quarter (`z_f34.png`, `z_f34base.png`, `w_f34.png`) — governs the read with the front cell.** Drawn nearly
frontal from a higher camera (the ground band is h 0–.13 against .07 in the front cell) and about 7 % wider than the
front cell (W : H 1.091 against 1.023; crown x −.537…+.549 H against −.505…+.509): the same pattern as 054 (§3.2). Lit
from the upper right (wood lit `#F8B464`, shade `#563219`); cast shadow to the left.
- **Trunk:** a **bundle of three to four huge twisted strands** shingled with long faceted **bark plates** (lozenge
  plates 1.5–3 studs long with dark seams); the central strand climbs **lower-left → upper-right ("/")** and becomes the
  main leader (290, 330) → (320, 260) → (340, 205); the left strand dark (in shade), the right lit; outer buttresses
  lean in. Deep dark grooves between strands.
- **The front cleft** (`z_f34base.png`): between the central and right strands, a **dark slit** (`#0A0702`) from the
  ground to y ≈ 380 (h .39), 2.0 studs wide at the ground (x 288–312) narrowing to 0.5 at its top; a slate rock and
  sprigs inside it.
- **Skeleton visible** (`w_f34.png`): the **left low limb** leaves at (220, 310) running left to (160, 300) with a fork
  (180, 290) under the left clump; the **right low limb** (330, 310) → (400, 295) → (430, 290), long and thick (Ø 25 px
  = 2.0 studs at the tip zone), ending under R; the **upper-left limb** (dark, (240–265, 250–290)) into the upper-left
  clumps; the **central leader** to h .82.
- **Clumps:** lime-yellow lit tops (upper right of each), mid-green bodies, dark green lower-left rims and undersides;
  scalloped by lobed leaf cards about 3–4 studs across; small dark gaps between cards; **the small trunk sprout** clump
  on the trunk front-left at (219–289, 292–342), h .48–.61.
- **Strands:** 9–10 lime drips under L, the sprout, R and FR, longest under the side clumps.
- **Base:** eight roots arching from the bell to the ground, toes split; lime moss patches on four root tops and on the
  trunk front; pale-topped slate rocks (the two big front rocks the most visible, a tall slab at the left root); pointed
  lime tufts; a continuous lime moss band on the ground.

**Rear three-quarter (`z_r34.png`, `z_r34base.png`, `w_r34.png`).** The same tree from behind. The **back arch** is the
clearest: a **pointed (gothic) dark arch** from the ground to y ≈ 410 (h .33), 45 px (0.116 H = **3.7 studs**) wide at
the ground, closing to a point at the top, between two buttress strands; **three slate rocks, moss and sprigs inside**
on the cavity floor. Low limbs left and right, strands under both side clumps, lime moss tufts on two strand faces of
the trunk (h .35–.45).

**Front, side and rear cells (`z_front.png`, `z_side.png`, `z_rear.png`, `t_front.png`, `w_front.png`).** Low views at
one scale (220–222 px tall). They are **near copies** (§3.3): the same bell, the same two crossing strands with a dark
cleft at the centre foot (front: h ≤ .29, 1.4 studs wide; side: h ≤ .22; rear: h ≤ .20), the same two low limbs, the
same three-lobed top.
- **Front clumps (`t_front.png`, studs from the axis at 32):** L x 26–100 → X −16.3…−5.6, z 10.6–22.1 (strands to
  10.6); FL + BL (upper left) x 72–135 → X −9.7…−0.6, z 18.6–29.5; BR (top centre) x 115–180 → X −3.5…+5.9, z 20.8–32;
  FR (upper right) x 150–205 → X +1.6…+9.5, z 24.3–30.4; R x 172–250 → X +4.8…+16.0, z 13.4–24.3 (strands to 11.5); the
  **sprout** x 100–122, y 690–715 → X −5.6…−2.4, z 13.5–17.2.
- **Front skeleton (`w_front.png`):** two strands cross in an X up the bell (the left from the lower left to (145, 700),
  the right from the lower right to (130, 700)) above the cleft; **left low limb** x 65–110, y 685–705 → X −10.7…−4.2, z
  15.0–17.9, Ø 2.2 at the tip zone, 2.9 at the trunk; **right low limb** x 165–215, y 668–705 → X +3.7…+11.0, z 15.0–20.3,
  rising about 15° outward; **right leader** x 150–172, y 630–700 → X +1.6…+4.8, z 15.7–25.8, Ø 2.2–2.9 (the BM4 fork and
  up-arm); **left leader** x 100–125, y 650–690 → X −5.6…−2.0, z 17.1–22.9 (BM3).

**Top (`z_top.png`, `t_top.png`).** Seven rosette clumps round the brown hub (§1.2 plan table); lime centres, mid and dark
rims; the trunk top pale at the hub centre; five limb arms radiating between the clumps.

**Trunk top junction (close-up 1, `z_cu.png` top).** The core's top: a **flat pale cut face** (`#FAC172`, about 10 broad
facets round its rim, **dark radial cracks** from the centre); three limb logs: **8-sided prisms** with flat pale end
faces round a **dark round bore** (Ø ≈ 0.35 of the log, `#130904`); the side log carries a **round pale peg**. The bark
below the cut is broad planks with dark seams.

**Root module underside (close-up 2).** A root log's joining end: an **octagonal hollow tube** (dark interior), pale
rim facets, a small knob (peg) deep inside; the log's bark in long planks; a slate rock and a tuft beside it.

**Trunk thickness (close-up 3).** The trunk cut low: a **thick wall** (about 0.15–0.18 of the outer Ø), 10–12 broad
outer planks, a **pale cut rim** (`#F3AA5C`) round a **dark brown hollow** (`#56331D`, shade `#271910`). It is the
hollow the cleft and arch open into (§3.5).

### 1.4 Parts (exploded, `z_expl.png`)

The exploded is an elevated front view (about 6.5–7 px / stud by the crown modules against the hero). **The hero
governs every size and height** (§3.4); the parts give shapes, counts and joints.

| Part (label) | Box (px) | Notes |
| --- | --- | --- |
| Crown Module ×5 | TC (320–472, 852–953) 153 × 102; TL (labelled) (194–334, 903–1003) 141 × 101; TR (467–588, 897–996) 122 × 100; L (130–236, 996–1080) 107 × 85; R (536–647, 999–1121) 112 × 123 with strands | rounded domes W : H 1.2–1.5 of chunky lobed leaf cards, lime tops, dark undersides; each on a **short faceted stub** with a flat cut end (TC stub (376–408, 938–962); TR stub (491–538, 966–991)); **R carries three moss strands** with bulb tips (to y 1121) |
| Branch Module (labelled) = **BM1**, left side | (177–322, 1032–1115) 146 × 84 | a thick 8-sided log with a **socket end** (pale ring, dark bore) at the right, a knuckle with an **upward spur** (cut end, pale), then an arm rising up-left into the L crown module |
| BM2, right side | (450–559, 1034–1120) 110 × 87 (+ spur (558–600, 1055–1080)) | the mirror: socket end at the left, an up-right arm into R, a spur up with a cut end |
| BM3, Y top-left | (258–375, 966–1044) 118 × 79 | a short thick base with a **socket at its foot** (dashed down to the core top), a **Y fork**: an arm up-right (cut end) and an arm out-left into TL |
| BM4, Y top-right | (401–497, 969–1044) 97 × 76 | the mirror Y: an arm up-left, an arm out-right into TR |
| Trunk Core | (287–478, 1063–1290) (root C overlaps its foot) | a **tapered fluted column** of long planks, **flared foot**, a **pale cut top** with two socket holes (the Y modules), **two square side bosses** (490, 1185) and (735, 1185) double-arrowed to BM1 and BM2 |
| Root Module A | (142–279, 1185–1308) 138 × 124 | a thick tapering faceted log: a hollow joining end high at the trunk, one kink, a long low run, **two blunt split toes** |
| Root Module B | (490–630, 1184–1317) 141 × 134 | longer, steeper at the trunk end, a kink, a long low run, a split tip |
| Root Module C | (340–400, 1255–1353) | the front root, pointing at the viewer: a short steep log with a **dark bore at its top end** and split toes |
| Rocks, tufts | rocks (277–328, 1264–1302), (437–485, 1265–1303) slate, pale tops; pebble (533–565, 1291–1308); tufts (106–169, 1276–1323), (188–236, 1274–1308), (224–294, 1285–1337), (467–541, 1285–1336) | rocks 8–12 broad facets, blue-grey sides, pale lit tops; tufts of pointed lime blades |

#### Trunk core — exploded, close-ups 1 and 3, hero
- **Shape:** a twisted, plank-shingled bell of **eight strands** (one per root), oval in section (X : Y ≈ 1.18 at the
  waist), flared at the foot; a waist at z 12.8; a crotch swell at z 15–17 where two side bosses take BM1 and BM2; a pale
  cut top at z 19.5 with two sockets (BM3, BM4); **hollow at the foot** (a cavity under a ceiling at z ≈ 9.6, its wall
  0.16 of the Ø) opened by the **front slit** and the **back arch**; deep V grooves between strands; bark pits on
  strand crests.
- **Hero size:** body (strand crests, without the roots) 13.6 × 12.0 at z 0, 12.4 × 10.8 at z 4, 10.8 × 9.4 at z 8,
  **9.4 × 8.0 at z 12.8**, 10.2 × 8.6 at z 16 (the crotch swell with the bosses), 7.6 × 6.8 at z 17.6, **6.6 × 6.0 at the
  top (z 19.5)**. Part about 14 × 12 × 19.5 with the bosses.

#### Branch modules (four) — exploded, close-up 1, hero
- **Shape:** straight faceted prisms (main runs 8-sided like close-up 1's logs, arms 6, spurs and tines 4–5: chunky),
  **hard kinks** at waypoints, a flat 8-sided base face with a pale ring and dark bore (the joint, hidden in the hero),
  forks with a `bark_deep` crotch, flat-ended spurs (pale cut). **Each arm tapers to ≤ 0.5 of its base Ø** (053
  verifier: "pipe-like" limbs).

#### Crown modules (seven clumps from five shapes, plus the sprout) — exploded, hero
- **Shape:** a rounded mound (W : H 1.2–1.5) of **chunky lobed leaf cards** layered and overlapping over a **solid dark
  core**, fed from below by the module's arm tip through a short stub; scalloped outline with lobes ~2.8 studs apart;
  lime on top, mid on the body, dark underneath; moss strands hang from the underside rim (on L, R, LB, FR, FL, BR).

#### Root modules (A, B, C; eight in the hero) — exploded, close-up 2, hero
- **Shape:** thick tapering faceted logs (6-sided, plank facets, a top ridge) that **start high on the bell** (their top
  ridge leaves the body at z 10–12), arch down the flare in a concave buttress, kink where they meet the ground, then
  run low and **split into 2 (A, C) or 2–3 (B) blunt toes**. The joining end is a hollow octagon (close-up 2), modelled
  on the parts only.

### 1.5 How 057 differs from its siblings and W05 `AncientTree` (binding: the verifier checks these)

| | 047 Old Pine (`GnarledPine`) | 053 Dead Tree (`TwistedSnag`) | 054 Broadleaf (`ShadeTree`) | W05 `AncientTree` (old kit) | **057 Ancient Tree** |
| --- | --- | --- | --- | --- | --- |
| Size | 20 tall | 18 tall | 20 tall, crown 20.2 | 34.7 tall, 36 wide | **32 tall, crown 32.7 × 30, W : H 1.02: the biggest tree in the kit by 1.6×** |
| Silhouette | five flat pads with sky between | bare wood, T 78 % | one scalloped dome of five clumps, T 37 % | squat cone trunk, flat pale crown | **a bell trunk (h .30 row ≤ .42 of W) under a seven-clump dome; canopy G 43–47 %, T 37 % (10.6–13.6 above h .45); strands below the crown** |
| Trunk | Ø 6.2, planked, leaning | Ø 5.0 waist, six strands | Ø 4.7 waist, six strands, a knot | a cone | **9.4 × 8.0 waist, eight shingled strands crossing in an X, a concave bell to 19.3 across the root shoulders, hollow foot with a front slit and a back arch** |
| Limbs | five elbowed limbs | six bare modules | four modules, five clumps | thin limbs | **two side modules (each with a spur) + two Y modules on a pale cut top, seven clumps, an open hub from above** |
| Roots | seven buttress roots | six, split toes | six | seven wedges | **eight high-starting snaking buttress roots (3 module shapes), split toes, moss on four** |
| Foliage | domed pads | none | cards on dark cores | puff blobs | **cards on dark cores, 3–4-stud cards, seven clumps + a trunk sprout, twelve lime moss strands** |
| Top view | rosettes round a limb star | a nine-armed star | five clumps round a hub | seven-petal flower | **seven clumps with seven clefts round an open hub (T 8.9 %)** |
| Ground | sand patch | moss, tufts, rocks | moss band, pale rocks | grass patch | **no patch: a lime moss band, pointed lime tufts, slate rocks with pale tops (two tall slabs), rocks and plants inside the cavity** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, trunk axis at (0, 0)). Plan azimuths: 0° = +X, counter-clockwise,
90° = +Y (back), 270° = −Y (front).

### 2.1 Stack (binding contact chain, bottom up; every seat gap 0.015)

| Piece | Sits on / in | Contact |
| --- | --- | --- |
| Cavity walls (two thick C-arcs of the hollow foot, decision §8.6) | ground | flat bottoms at z 0 |
| Upper trunk (the solid body from the cavity ceiling up, bosses and top socket included) | the walls | its underside (the cavity ceiling) at z 9.6, overlapping the walls' tops by 0.3 (closed shells, buried) |
| Root modules (8) | the bell flare and the ground | the root's high end buried 0.3–0.5 in the flare (its joining face hidden inside the body); toes sunk 0.05 into z 0 |
| Branch modules (4) | their bosses / the top sockets | base face 0.015 off the boss / socket face, 0.02 wider all round (no peg in the hero, decision §8.5) |
| Arms, spurs, tines | their parent segment | part of the module's ring-stack shell, or closed shells buried ≥ 0.2 in the parent |
| Clump stub | its module's arm tip | stub base face 0.015 off the tip face; its top ≥ 0.4 inside the clump core |
| Clump core (dark solid dome) | the stub | the stub top buried 0.4–0.6 |
| Leaf cards | the core and neighbours | each card's underside centre within 0.03 of the core (or a neighbour card); ≤ 25 % of its verts inside the core |
| Moss strands | the clump core underside (or a limb underside) | the strand's top ring buried 0.3–0.5 in the core; never through a card's top, never through a limb |
| Rocks, pebbles, cavity rocks | ground | sunk 0.12 / 0.05 |
| Moss pads | ground | z 0 … 0.10–0.14, sunk 0.02 |
| Tufts | ground or a moss pad | hub sunk 0.03; every blade within 0.03 of its hub |

### 2.2 Trunk core

| Ring z | 0 | 2.0 | 4.0 | 6.4 | 8.0 | 9.6 | 11.2 | 12.8 | 14.4 | 16.0 | 17.6 | 19.5 (top) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Body X × Y (strand crests) | 13.6 × 12.0 | 13.0 × 11.4 | 12.4 × 10.8 | 11.5 × 10.0 | 10.8 × 9.4 | 10.2 × 8.8 | 9.7 × 8.3 | **9.4 × 8.0** | 9.6 × 8.2 | 10.2 × 8.6 | 7.6 × 6.8 | 6.6 × 6.0 |
| Twist (strand azimuth offset) | 0° | 4° | 8° | 13° | 16° | 19° | 23° | 26° | 29° | 32° | 35° | 38° |

- **Section:** **eight strands**, each three facets wide (24 sides); the vertex between two strands pulled in 0.5–0.7 (a
  deep V groove), the strand's middle facet proud 0.10–0.18, alternating strands 8–12 % thicker. Strand azimuths at
  z 0 are the root azimuths (§2.3): each root rides up its strand. Oval: scale the rings to the X × Y above.
- **Twist:** counter-clockwise seen from above, about 38° foot to top, so the front grooves climb lower-left →
  upper-right ("/"), as the f34 shows. Above the cleft, the front groove between the two central strands is the deepest
  (0.9) and runs up to z 12.5 (the f34's dark line above its slit).
- **Bark plates:** the sheet's bark is long lozenge plates with dark seams. Do it with geometry you already have: each
  strand facet run is split into **plates 1.6–2.6 long** (ring spacing), staggered half a plate between neighbouring
  facets where the ring stack allows, and **coloured per plate** (§5.5). No extra seams or inset geometry.
- **Hollow foot (decision §8.6):**
  - **Cavity:** inner wall 0.16 of the Ø thick (outer Ø 13.6 → inner about 9.2 × 7.8 at z 0, 7.6 × 6.4 at z 9), from z 0
    to the **ceiling at z 9.6**; 12-sided inner surface, flat-shaded.
  - **Front slit** at az 272°: 1.6 wide at z 0, 1.2 at z 5, 0.4 at its top **z 10.0** (the ceiling's front lip is
    notched up 0.4); jambs follow the strands (they lean with the twist).
  - **Back arch** at az 92°: **3.8 wide at z 0**, 3.4 at z 5, 2.0 at z 8, closing to a **point at z 10.6** (a gothic
    arch: the two jambs lean together above z 7; the ceiling's back lip is notched up 1.0 into the upper trunk to take
    the point).
  - The walls between the openings are two thick C-arcs (az 92°→272° through 180°, and back through 0°), each one closed
    ring-stack shell (outer strands, jambs, inner wall, top face under the upper trunk).
- **Top:** a flat cut face, a 10-sided cap Ø 6.6 × 6.0 (`bark_light`) with **dark radial cracks** (6 thin `hollow`
  wedges from the centre to the rim, 0.15 wide at the rim: colour regions on a fan of the cap, no extra cuts if the fan
  gives the lines) and **two sockets** for BM3 and BM4 (round holes Ø 1.4 × 0.4 deep on the part; in the hero the module
  bases cover them, §3.7). From above the cap shows as the pale hub between the arms.
- **Side bosses (2)** for BM1 / BM2, each an **8-sided collar** rising out of a strand pair with a **flat face**:

  | Boss | Face centre | Axis (az, rise above horizontal) | Collar Ø | Takes |
  | --- | --- | --- | --- | --- |
  | B_L | (−5.0, −0.4, 15.6) | 185°, 10° | 3.4 | BM1 (left, labelled) |
  | B_R | (5.0, 0.4, 16.0) | 5°, 12° | 3.2 | BM2 (right) |
  | S_TL | (−1.5, 0.7, 19.5) | 150°, tilted 22° from vertical | cap socket Ø 1.4 | BM3 (Y top-left) |
  | S_TR | (1.5, −0.4, 19.5) | 330°, tilted 18° from vertical | cap socket Ø 1.4 | BM4 (Y top-right) |

  Collars protrude 0.5–0.7 beyond the strand crest; with the module bases they make the crotch swell 10.2 across at z 16.
- **Sprout stub:** a short 5-sided stub (Ø 1.2, 1.4 long) from the trunk front-left at (−3.0, −3.4, 15.0) toward az 235°,
  rising 20°, for the SP clump (§2.5); built into the upper trunk shell or a closed shell buried 0.3.
- **Bark pits (8–10 on the core):** small dark square insets (0.35–0.5, flat `hollow` insets on strand crests, never in
  grooves), mostly between z 6 and 16 on the front and back faces. **No knot hole** (the sheet draws none; the slit and
  arch are this tree's holes).
- **Underside:** open to the cavity: the walls' bottom annuli at z 0 (hidden). No separate underside detail is drawn for
  the core; the root ends carry close-up 2's hollow (§3.7).

### 2.3 Roots (eight)

| Root | Module | Azimuth | Reach r (toe tips) | Section h × w at the bell → mid → toes | Toes | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| RT1 | A | 20° | 13.2 | 3.4 × 3.0 → 2.2 × 2.4 → 1.0 | 2 | rear far-left tips; rear tall slab beside it |
| RT2 | B | 60° | 12.0 | 3.2 × 2.8 → 2.0 × 2.2 → 0.9 | 3 | rear and r34 right of the arch |
| RT3 | C | 120° | 11.6 | 3.2 × 2.8 → 2.0 × 2.2 → 0.9 | 2 | rear and r34 left of the arch |
| RT4 | A | 160° | 14.0 | 3.6 × 3.2 → 2.4 × 2.6 → 1.1 | 2 | front far-left (−.39 H); f34 far-left root |
| RT5 | B | 200° | 14.5 | 3.6 × 3.2 → 2.4 × 2.6 → 1.1 | 3 | front left (tall slab on its flank) |
| RT6 | A | 240° | 12.4 | 3.4 × 3.0 → 2.2 × 2.4 → 1.0 | 2 | front centre-left; f34 big front-left root |
| RT7 | C | 300° | 12.4 | 3.4 × 3.0 → 2.2 × 2.4 → 1.0 | 2 | front centre-right; f34 front root to (420, 530) |
| RT8 | B | 340° | 14.2 | 3.6 × 3.2 → 2.4 × 2.6 → 1.1 | 3 | front far-right (+.46 H) |

- Gaps: the roots leave **60° gaps at az 90° (the back arch) and 270° (the front slit)**, 40° elsewhere.
- **Profile (top ridge, r from the axis → z):** (r 4.8 → z 11.5) leaving the strand, (6.4 → 9.6), (8.0 → 8.0), (9.6 →
  6.4) the concave buttress, (10.6 → 4.4), (11.6 → 2.6) **the kink**, then the low run (top 1.2–1.6 above the ground) to
  the toes. Section 6-sided: a top ridge, two upper flanks, two lower flanks splayed onto the ground, a flat bottom.
  Roots toward ±Y (60°, 120°, 240°, 300°) run 1.5–2.5 shorter than those toward ±X (the side cell is narrower, §1.1).
- **Snaking:** each root's plan path bends 10–20° once (at the kink) and the next root the other way; the toes splay
  20–30° apart, blunt, flat-ended (half pale cut, half dark).
- **Moss on roots:** four lime moss patches on root ridges (RT4 r 7–9, RT5 r 6–8, RT6 r 5–7, RT7 r 6–8.5) as a colour
  region on the root's ridge and upper-flank faces chosen by position (§5.5), not extra shells.
- Vary each repeated module's yaw ±5°, reach ±0.4 and section ±6 % so the repeats don't read.

### 2.4 Branch modules (four) and their limbs

Waypoints are segment ends (straight segments; every waypoint a hard mitred kink). Ø per waypoint. Spurs and tines are
4–5-sided, flat-ended. **Every arm tapers to ≤ 0.5 of its base Ø at its tip** (053 finding 2).

| Limb | Module | Socket | Waypoints (x, y, z) → | Ø | Arms, spurs (tip (x, y, z)) | Feeds |
| --- | --- | --- | --- | --- | --- | --- |
| **LOW-L** | BM1 (labelled "Branch Module") | B_L | P0 (−5.0, −0.4, 15.6) → knuckle K (−7.6, −0.8, 15.9) | 3.2 → 2.8 | **main arm** K → (−9.4, −1.4, 16.4) → J_L (−10.6, −2.0, 17.6), Ø 2.2 → 1.5; **bare fork** from (−9.9, −1.6, 16.6): tines to (−12.2, −2.6, 16.2) and (−11.8, −0.6, 15.6), Ø 0.8, poking out under L's outer underside; **spur** K → (−7.4, −3.4, 17.6) → J_FL (−5.6, −7.0, 18.8), Ø 1.9 → 1.2 | L (main), FL (spur) |
| **LOW-R** | BM2 | B_R | P0 (5.0, 0.4, 16.0) → elbow E (7.6, 0.6, 16.8) | 3.0 → 2.6 | **main arm** E → (9.6, 0.9, 18.0) → J_R (10.4, 1.2, 19.0), Ø 2.0 → 1.4; **bare fork** from (10.0, 1.0, 18.3): tines to (12.6, 0.0, 17.6) and (12.2, 2.0, 17.0), Ø 0.8; **cut spur** E → (8.2, 2.2, 19.2), Ø 1.3, pale end facing up-back (the exploded's spur) | R |
| **Y-TL** | BM3 | S_TL | (−1.5, 0.7, 19.5) → fork V (−2.6, 1.8, 22.0) | 3.2 → 2.8 | **up arm** V → (−3.6, 5.0, 24.4) → J_BL (−4.6, 7.6, 25.8), Ø 2.0 → 1.4; **out arm** V → (−5.6, 2.8, 21.6) → J_LB (−8.4, 4.2, 20.6), Ø 1.9 → 1.3 | BL (up), LB (out) |
| **Y-TR** | BM4 | S_TR | (1.5, −0.4, 19.5) → fork V (2.4, 0.4, 22.4) | 3.4 → 3.0 | **up arm (the main leader)** V → (3.0, 4.8, 25.2) → J_BR (3.4, 8.4, 26.6), Ø 2.4 → 1.6; **out arm** V → (3.8, −3.2, 23.6) → J_FR (4.4, −6.6, 24.0), Ø 2.0 → 1.4 | BR (up), FR (out) |

- **Branch-by-branch from the sheet** (front cell, studs from the axis, z above the ground):

  | Limb | Leaves the trunk | Segments seen | Ends seen |
  | --- | --- | --- | --- |
  | LOW-L | (−4.2, 15–17.9), Ø 2.9 | out-left nearly level, Ø 2.2 at X −7…−10.7 | a fork under L's outer edge at X −10…−11 |
  | LOW-R | (+3.7, 15–17), Ø 2.6 | rising ~15° right to (+11.0, 20.3) | the tip under R (f34: a long thick limb to x +.38 H) |
  | Y-TR | the trunk top (+1.6…+4.8, z 19.5–25.8) | the right leader, Ø 2.2–2.9, in the canopy gap at x .00–.05 | enters BR above z 26 |
  | Y-TL | (−5.6…−2.0, z 17–23) | the left leader into the upper-left clumps | enters BL / LB |

- **Visible limb lengths (binding, §9.1):** in the front, rear and f34 renders each of LOW-L and LOW-R must show **≥ 3.0
  studs of bare limb** not hidden by leaves or trunk, Y-TR's up arm **≥ 2.0** (the leader in the gap), and each bare
  fork its two tines against the sky or the clump underside. Y-TL must show ≥ 1.5 in the f34 or r34. From the top, the
  trunk cap and **at least four arms** show between the clumps.
- **Bark pits on modules (6–8):** at each knuckle, elbow and fork crotch first (dark square insets).
- **Cut ends:** every tine and spur end flat; about half pale (`bark_light`), half dark (`hollow`).

### 2.5 Leaf clumps (seven) and the sprout

| Clump | Module tip | Centre (x, y) | Bottom z (inner / outer droop) → top z | W × D × H | Cards | Strands | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **BR** back-right (crown) | J_BR (BM4 up) | (3.5, 10.2) | 23.2 / 20.8 → **32.0** | 12.5 × 11.0 × 10.0 | 12 | 1 | top sector 37–102°, outer 15.6; front top centre z 32 |
| **BL** back-left | J_BL (BM3 up) | (−5.1, 8.5) | 25.0 / 22.6 → 30.4 | 9.0 × 8.5 × 7.4 | 9 | 0 | top 102–138°, lime 82 %; front upper-left z 29.5 |
| **FR** front-right (high) | J_FR (BM4 out) | (4.5, −7.8) | 22.0 / 18.6 → 29.8 | 11.0 × 11.0 × 10.0 | 11 | 2 | top 264–336°; front upper right z 24.3–30.4 |
| **LB** left-back (low) | J_LB (BM3 out) | (−9.7, 4.7) | 18.4 / 14.4 → 25.6 | 8.5 × 8.5 × 9.0 | 8 | 2 | top 138–171°, lime 13 % |
| **R** right (low) | J_R (BM2) | (10.2, 1.4) | 17.6 / 12.8 → 24.3 | 11.5 × 11.0 × 10.0 | 11 | 3 | top 336–37°; front X +4.8…+16.0, bottom .40–.46 H |
| **L** left (low) | J_L (BM1 main) | (−10.4, −2.5) | 17.4 / 10.9 → 22.4 | 11.5 × 10.5 × 10.0 | 11 | 3 | top 171–219°; front X −16.3…−5.6, bottom .35–.43 H |
| **FL** front-left (low) | J_FL (BM1 spur) | (−4.6, −8.5) | 18.4 / 15.7 → 24.3 | 9.0 × 8.5 × 8.0 | 8 | 1 | top 219–264°, lime 8 % |
| **SP** trunk sprout | the sprout stub | (−4.0, −5.0) | 13.4 → 17.3 | 4.4 × 4.0 × 3.9 | 4 | 0 | front X −5.6…−2.4, z 13.5–17.2; f34 h .48–.61 |

- **Crown extents from this table:** X −16.2 … +16.0 (32.2), Y −13.3 … +15.7, Z 10.9 (L's droop; strands to 10) … 32.0.
- **Inner undersides stay up** (17–25) on the trunk side of every clump so the low limbs and the junction show; the
  outer side droops (10.9–22.6) as in the canopy bottom row (§1.2). **Keep the centre open:** no card within r 4.5 of
  the axis above z 19 (the top cell's hub).
- **Core (one per clump):** a solid flattened dome (7-sided, bottom ring + two bands + top vertex, ≈ 28–36 tris,
  `leaf_dark`), 0.75–0.8 of the clump's W and D and 0.7 of its H, its underside near-flat. Fills the clump so no sky
  shows through a clump's middle.
- **Stub (one per clump):** 5-sided Ø 1.2–1.6, from the module tip up into the core underside (a single segment; no Y
  inside the clump: the budget goes to the visible limbs).
- **Leaf card (closed, 16 tris):** 054's bicone plate: an **8-vertex rim of four broad rounded lobes** (radii alternating
  1.0 / 0.80, notch verts at ±18° from each lobe axis), a raised top centre (+0.22) and a lowered bottom centre (−0.15);
  no side walls, no zero-area faces, corners ≥ 8°. **Card Ø 3.0–4.4** (top cards largest), so the outline scallops come
  ~2.8 apart. If the budget allows, the ~24 most visible top and rim cards may use a 10-vertex 5-lobe rim (20 tris) —
  never pointed stars.
- **Card placement** (per clump, deterministic seed): Fibonacci spread over the upper 80 % of the core dome plus **one
  lower ring of 3–5 cards** hanging 0.4–1.0 below the core rim on the clump's outer side (the droop; the inner side stays
  up). Each card tangent to the dome, tilted outward 15–30°, random spin, overlapping neighbours by 30–50 % of its
  radius, underside centre seated within 0.03 of the core. Small dark gaps between cards are right (the sheet's dark
  tone 10–15 %), sky through a clump's middle is not.
- **Moss strands (12, closed shells):** a 5-sided tapered drip: top ring Ø 0.9–1.1 buried 0.3–0.5 in the core underside
  (or a limb's underside for the two under LOW-L and LOW-R), 2–3 rings down to Ø 0.45–0.6, a **bulb tip** (a ring
  swelling to Ø 0.7–0.9 then a point), total 3.0–5.5 long so 1.6–4.2 shows below the clump; slight sway (the lower half
  2–6° off vertical), never crossing a card or a limb. ≈ 16–20 tris each. Placement (studs): L at (−14.2, −3.6),
  (−12.4, −0.8), (−8.6, −5.0); R at (13.6, 0.6), (11.4, −2.4), (8.4, 3.8); LB (−12.6, 6.4), (−10.4, 8.4); FR (7.0,
  −10.2), (5.4, −12.4); FL (−7.4, −11.0); BR (9.4, 12.0). Tips at z 10–16 (L and R longest, lowest).
- **Read:** each clump **one rounded mound of overlapping leaves** — a scalloped outline, a lime top, a mid body, a dark
  underside — **not a cluster of separate balls** (047 round 1) and **not a smooth blob** (W05). The seven clumps touch
  or overlap in the front view, with **seven clefts round the outline from above**.

### 2.6 Base dressing (no ground patch)

Every piece sits between roots (≥ 15° from the nearest root azimuth at its radius, or ≥ 0.1 clear of the root surface)
or inside the cavity.

| Piece | Position (x, y) | Size W × D × H | Evidence |
| --- | --- | --- | --- |
| RK1 tall slab left | (−11.6, 0.2), az 179° | 2.6 × 2.2 × 4.6, a leaning slate slab, flat top sloping toward the trunk | front −.365…−.29, h .06–.20; f34 (106–138) on the left root's flank |
| RK2 big front-left | (−8.4, −8.0), az 224° | 4.6 × 3.6 × 2.6, low, a sloping faceted top | f34 (127–187, 502–534) |
| RK3 big front-centre | (−2.0, −12.2), az 261° | 4.4 × 3.8 × 3.6, the tallest front rock | f34 (218–274, 486–534); front −.09…−.03 |
| RK4 right tall | (9.6, −8.8), az 318° | 2.8 × 2.6 × 3.0 | f34 (430–465, 438–472) |
| RK5 right low | (12.8, −0.4), az 358° | 2.8 × 2.4 × 1.8 | front +.30…+.36 h .05–.10 |
| RK6 tall slab back-right | (9.6, 8.0), az 40° | 2.6 × 2.2 × 4.2 | rear tall slab −.37…−.25 (world X +8…+11.8) |
| RK7 back-left | (−9.2, 7.7), az 140° | 2.6 × 2.2 × 2.2 | rear +.27…+.32 |
| CR1, CR2 cavity rocks | (0.6, 1.6), (−1.0, 2.4) on the cavity floor | 1.6 × 1.4 × 2.2; 1.2 × 1.0 × 1.6 | r34 arch (three rocks), front cleft (139–154, 767–784), f34 cleft (291–319) |
| Pebbles ×4 | (−4.4, −12.8), (5.8, −11.4), (−13.0, 3.8), (3.8, 12.8) | 0.7–1.1 | small greys in every view |
| Moss band: pads ×5 | the slit mouth (az 270°, r 6–10), the arch mouth (az 90°, r 6–10), az 180° (r 8–11), az 0° (r 8–11), az 220° (r 6–9); outer lobes cut round the rocks (≥ 0.05 clear) | lobed, 4–6 across, 0.10–0.14 thick | the continuous lime ground band (ground G 6.5–9 %) |
| T1 far-left tuft | (−15.0, −2.0), az 188°, past the toes | Ø 3.0, 3.6 tall, 6 blades | front −.46…−.34; f34 far-left |
| T2 front-left group | (−4.8, −11.4), az 247° | Ø 2.6, 3.0 tall, 6 blades | front −.33…−.10 (top .19) |
| T3 slit-mouth sprigs | (0.4, −8.6), az 273° | Ø 1.8, 1.8 tall, 5 blades | front centre sprigs; f34 cleft |
| T4 right group | (11.6, −7.0), az 329° | Ø 2.8, 3.0 tall, 6 blades | front +.25…+.46; f34 (404–488) |
| T5 arch-mouth sprigs | (−0.6, 9.4), az 94° | Ø 1.8, 2.0 tall, 5 blades | r34 arch |
| CT1 cavity tuft | (−0.2, 0.6) inside | Ø 1.4, 1.6 tall, 4 blades | r34 plants inside the arch |

- **Blades:** pointed lanceolate, **broad at the base** (L : W ≈ 4), folded once along the midrib (closed, 6 tris), rising
  60–85° and arching out from a small hub; lime tips and a green heart. Never needles, never edge-on to the f34 or front
  camera (039).
- **Rocks:** angular blocks, flat base, 8–14 broad facets, ring stacks (054's `_rock`); RK1 and RK6 tall slabs (W : H
  0.55), the low ones W : H 1.2–1.8. Never `K.hull_rock` eggs.
- **Keep clear:** nothing more than 0.05 inside a root, toe, wall, the trunk or a rock (047 round 2 blocker); every tuft
  hub ≥ 0.3 outside root and wall surfaces; rocks may touch roots but cut ≤ 0.05. **Cavity pieces stay ≥ 0.2 inside the
  inner wall** and visible through the arch from `rear_sheet` and `r34_sheet`.

### 2.7 Expected extents and screen checks

- **Extents:** X −16.2 … +16.0 (L and R clumps; root RT5's toes −14.5, T1 −15.5), Y about −13.3 … +15.7 (RK3 front
  −14.1), Z 0 … 32.0. Bbox about 32.2 × 29.8 × 32.0.
- **Checks on the renders** (floor hidden, `measure_render.py` with this folder's `m.py`):
  - **front_sheet (0, 5)** — governs positions: W : H 0.96–1.08 (sheet 1.023); G 54.4 ± 4 (canopy 46.3, ground 8.1), T
    37.0 ± 4, R 4.3 ± 3; fill 0.61 ± 0.05; **T above h .45 ≥ 9 % (sheet 11.1)**; outer wood rows h .20 / .30 / .40 at
    .60 / .39 / .30 of H ± .05 (the bell); canopy bottom row (§1.2) ±0.06 per column with the **gap at x .00–.05
    (bottom ≥ .60)**; the slit dark from the ground to h .28–.31; the low-limb forks at (−.31…−.36 H, h .47–.53) and
    (+.33…+.38 H, h .53–.57).
  - **f34_sheet (0, 13)** (probe az −35 … +35 × e 9 / 13 / 16, keep the best; §3.2): W : H 1.02–1.10 (sheet 1.091);
    G 51.5 ± 4, T 36.6 ± 4; T above h .45 ≥ 9 (sheet 10.6); the slit visible; leaf light / mid / dark 58 / 27 / 15 ± 8.
  - **rear_sheet (180, 5), r34_sheet (180, 13)** (probe 145 … 215): W : H 0.94–1.08; T 37 ± 4; T above h .45 ≥ 9; **the
    arch: a dark pointed opening h ≤ .33, 0.10–0.13 H wide at the ground, with the cavity rocks visible**; O below h .35
    1.5–3 %.
  - **side_sheet (90, 5):** content (§3.3): W : H 0.88–1.02 (sheet 0.945); clumps both sides of the trunk; strands both
    sides; the bell visible from the ground to h .45.
  - **top (0, 89):** W : D 1.00–1.12 (sheet 1.067); seven clumps with seven clefts round the outline; **T 5–13 % (sheet
    8.9) with the pale cap and at least four arms in the hub**; leaf light / mid / dark ≈ 54 / 41 / 5 ± 10.

## 3. View conflicts and resolutions

### 3.1 Sheet number
- **Evidence.** The header says "54 / 132"; INDEX.md row 57 lists `057.png` as "Flintborn Ancient Tree Model Study".
- **Resolution.** Our number is 057 (file name, keys `m057_*`). Note the header in the export notes only.

### 3.2 The front three-quarter is near-frontal and drawn wider
- **Evidence.** The f34's crown is −.537 … +.549 H (front −.505 … +.509), its W : H 1.091 against 1.023, its ground band
  twice as deep; both sides grow alike, so it is a higher camera and a looser drawing, not a turn. The r34 (1.072 against
  the rear's 0.995) repeats it. Same as 054 §3.2.
- **Resolution (decision §8.10).** `front_sheet (0, 5)` governs positions; `f34_sheet (0, 13)` governs the read and the
  shares; probe az −35 … +35 (e 9–16) once and keep the best; record the camera. Don't widen the crown past 1.10.

### 3.3 Front, side and rear are the same drawing
- **Evidence.** The three ortho cells share one silhouette (W : H 1.02 / 0.95 / 1.00), one centred dark cleft at the
  foot, two low clumps at both sides with strands, a three-lobed top. The top cell's seven-clump ring can't show low
  clumps at both sides in views 90° apart, nor one cleft in the middle of three views.
- **Resolution.** **Front and rear govern positions; the top governs the plan; the side is judged for content** (as 053 /
  054). The plan (§2.5) puts the low clumps at the left and right and LB / FL tucked in, so the front and rear match;
  from the side the low clumps show as masses either side of the trunk. The side cell's cleft is read as the deep groove
  between the two roots facing +X (RT8 / RT1): a dark V-valley 0.8 deep, not an opening (§3.5).

### 3.4 Exploded scale and counts vs the hero
- **Evidence.** The exploded draws five crown modules, four branch modules, three root modules; the hero's top cell
  shows seven clumps and the front base eight root tips; the exploded trunk core's side bosses sit half way up the core,
  the hero's low limbs leave at h .47–.56.
- **Resolution.** **The hero governs sizes, heights and counts.** The exploded's parts are the **reusable shapes**: five
  crown module shapes → seven clumps (instanced with yaw ±25° and scale 0.8–1.15, plus the small SP), three root shapes
  → eight roots (A ×3, B ×3, C ×2), four branch modules as tabled. The parts shot uses the hero's own module meshes.

### 3.5 The hollow: close-up 3 vs close-up 1, and how many openings
- **Evidence.** Close-up 3 shows the trunk as a thick hollow tube; close-up 1 shows a solid pale cut top with radial
  cracks. The f34 shows a narrow front slit to h .39; the r34 a pointed arch to h .33 with rocks inside; the front, side
  and rear cells each show a dark cleft at the centre foot (h ≤ .29 / .22 / .20).
- **Resolution (decision §8.6).** **The trunk is hollow at its foot only**: a cavity from the ground to a ceiling at z
  9.6, its wall 0.16 of the Ø (close-up 3 is a low cut), solid above with the pale cut top of close-up 1. **Two
  openings:** the front slit (az 272°, to z 10) and the back arch (az 92°, to z 10.6); the side cell's cleft is a deep
  valley between roots. The f34's slit line above z 10 continues as the deepest strand groove to z 12.5.

### 3.6 Walk-in or not
- **Evidence.** At 32 tall the back arch is 3.8 wide × 10.6 tall; W05's `AncientTreeHollowTrunk` had a walk-in cave
  (≥ 4 × 6); the sheet shows rocks and plants on the cavity floor, so the floor is real.
- **Resolution (decision §8.7).** **Keep the sheet's size**; collision precise, so a player may step into the arch and
  see the dark cavity with its rocks. Don't widen it to a doorway (that is W05's variant, not this sheet).

### 3.7 Sockets, pegs and joint seams in the hero
- **Evidence.** Close-ups 1 and 2 and the exploded show bores, pegs, bosses and hollow root ends; the assembled views
  show no seams at the limb bases and no rings where the roots meet the bell.
- **Resolution (decision §8.5).** Bores, pegs and hollow ends are modelled on the parts only; in the hero each module's
  base face overhangs its boss by 0.02 all round (reads as a plank crease, never a pale ring) and each root's high end is
  buried in the flare. The top cap's two sockets are covered by BM3 / BM4.

### 3.8 Ground: no patch drawn
- **Evidence.** No soil disc in any cell: a lime moss band runs under the roots and tufts; paper shows past r ≈ 0.47 H.
- **Resolution.** No patch. Five broad, thin, lobed moss pads between the roots make the band; rocks, pebbles, tufts and
  root toes sit on z 0.

### 3.9 One foliage swatch vs three leaf tones; "consistent materials"
- **Evidence.** The palette shows one Foliage swatch (`#9CBC19`); the crown is clearly three-toned (lime tops, mid
  green, dark green undersides; shares 58 / 32 / 10). The notes ask for "consistent wood, leaf and rock materials from
  the Flintborn style guide"; the user wants rich, blended colour with broad Tint mottling (memory `lighting-not-paint`).
- **Resolution.** Three leaf keys calibrated to the rendered tone medians (the swatch is the mid / median target), two
  strand keys, bark / bark light / bark deep / hollow / cavity wall keys, rock / rock light / rock slate keys; blended by
  position and role; broad per-region Tint (0.03–0.04 per plate / card / facet), never per-triangle confetti.

### 3.10 Warm swatch rock vs slate rocks in the renders
- **Evidence.** The Rock swatch is a warm neutral grey `#A49F9C` (22°, 0.05); the rendered rocks have warm pale lit tops
  (`#D1C6C0`) and **cool slate-blue** shaded sides (`#58626E`, 212°, 0.20); the two tall slabs and the cavity rocks are
  slate overall (`#545B63`, `#6C6C72`).
- **Resolution.** `rock` calibrated to the lit and median values (warm); the cool look comes from the studio's shade, plus
  a **`rock_slate` key by role** for the tall slabs RK1 / RK6, the cavity rocks and each rock's lowest 30 % (position),
  never by facing.

### 3.11 Cast shadow
- The sheet's lavender shadow is excluded by the X mask. Render every `*_sheet` view with the studio floor hidden.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its exploded cell

**Reuse:** 054's `m054.py` already has `tube`, `prism`, `leaf_card`, `clump_core`, `_seat_card`, `_rock`, `pebble`,
`moss_pad`, `blade`, `tuft`, `contact_report`, `bury_report`, `limb_visibility`, `winding_total`; 053's `m053.py` has
`chain`, `cap`, `pit`, `branch_module`, `root_module`. 054 is still being modelled, so **copy what you need into
`m057.py`** (import from `m053`, which is committed, if it fits as is); don't edit either.

1. `seg_chain(points, radii, sides, twist)` → one closed tapering prism chain, a ring at each waypoint, mitred, flat end
   caps. **No smooth curves; every waypoint a hard kink.** Builds every limb, arm, spur, tine, stub, strand and root.
2. `trunk_walls()` → the two C-arc shells of the hollow foot (outer strands, jambs following the slit and arch, inner
   12-sided wall, flat bottoms, a top face under the ceiling).
3. `trunk_upper()` → the solid upper trunk from z 9.3 (overlapping the walls by 0.3; its underside is the cavity ceiling,
   notched at the slit and arch tops) to the cap at z 19.5, with the crotch swell, the cap with its radial-crack fan
   and two sockets, the sprout stub. **Bosses B_L / B_R grown into the ring stack** (053's "grown blocks" accepted by
   the main session) or unioned one at a time at the origin (`m021._union_fine`, merge 0; save between).
4. `trunk_core(part)` → walls + upper; on the part, the top sockets as holes and the bosses' faces with sockets.
5. `branch_module(kind)` for `side_l` (BM1), `side_r` (BM2), `y_tl` (BM3), `y_tr` (BM4), each in its own local frame
   (base face at the origin, axis +Z), so one function serves the hero and the part; `joints=True` adds the bore and peg
   (parts only).
6. `root_module(kind)` for `A` (2 toes), `B` (2–3 toes, longer, steeper), `C` (2 toes, short, steep), local frame at the
   high end; `joints=True` adds close-up 2's hollow octagon end.
7. `leaf_card`, `clump_core`, `crown_module(shape, scale, yaw, seed)` → stub + core + cards in its own local frame (stub
   base face at the origin), five shapes (TC, TL, TR, L, R from the exploded) placed as the seven clumps; `sprout()` for
   SP. `strand(top, length, sway, seed)`.
8. `base()` → `rock(spec)` ×9 (incl. CR1–2), `pebble()` ×4, `moss_pad()` ×5, `tuft(spec)` ×6 with the placement guard (§6).
9. **Hero `MonarchTree`** (decision §8.2) = trunk core + four branch modules + seven clumps and the sprout + 12 strands +
   eight roots + base, joined into one object of closed shells.
10. **Parts shot** (0, 22) laid out like the exploded: the trunk core in the middle, branch modules round its top and
    sides, the crown module above, the three root modules below; gaps 2–3.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a giant round-crowned tree on a massive twisted, shingled bell trunk with a dark slit at its foot;
   seven overlapping-leaf mounds, lime on top, with lime strands hanging; two low limbs with bare forks under the side
   clumps; the trunk top junction and leaders in the gap under the back clumps; eight snaking split-toed roots; slate
   rocks, tall lime tufts and a lime moss band at the foot; a pointed dark arch at the back with rocks inside.
2. **front_sheet / f34_sheet** per §2.7 (shares, fill, W : H, bell rows, canopy bottom row with the gap, T above h .45).
3. **rear / r34 / side / top** per §2.7.
4. **Close-up renders:** `junction_cu (−25, 35)` on the trunk core part's cap with BM3 / BM4 lifted off (radial cracks,
   bores, pale ends) against close-up 1; `root_end_cu (60, 10)` on Root Module A's joining end against close-up 2;
   `hollow_cu` — the trunk core part cut at z 4 (or rendered from (0, 60) with the upper trunk hidden) against close-up
   3 (thick wall, pale rim, dark hollow); `arch_cu (180, 6)` on the back arch (pointed, dark, rocks inside);
   `clump_cu` on one clump with its strands.
5. **Contact counts** (§6): floating shells 0; every card chained to its core, every strand to a core or limb, every core
   to its stub, every module to its boss; buried cards 0.
6. **Hero size** per §2.7; a **scale shot** with a 5.5-stud marker under L (its strands at z 10 clear the head by 4.5),
   one inside the back arch, and 054's `ShadeTree` (20) beside it if it is in the kit file.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Upper trunk (24 sides × 8 bands from z 9.3 to 19.5, crotch swell, cap fan with cracks, sockets hidden) | 1 | 470–520 | 470–520 |
| Cavity walls (two C-arcs: outer 8–9 facets × 4 bands, jambs, 12-sided inner wall, tops, bottoms) | 2 | 120–150 | 240–300 |
| Side bosses | 2 | 24–32 | 50–64 |
| Sprout stub | 1 | 10–12 | 10–12 |
| **Trunk core part** (+ sockets and boss holes on the part) | | | **780–900** |
| Branch modules (main 8 sides, arms 6, spurs and tines 4–5) | 4 | 90–110 | 360–440 |
| Clump stubs | 8 | 12–18 | 100–140 |
| Bark pits (flat insets) | 14–18 | 6 | 84–108 |
| Root modules (6-sided, 4 segments, 2–3 toes) | 8 | 46–56 | 370–450 |
| **Skeleton** | | | **≈ 1700–1850** |
| Clump cores | 8 | 28–36 | 230–280 |
| Leaf cards (16 tris; up to 24 at 20) | 74 | 16–20 | 1180–1280 |
| Moss strands | 12 | 16–20 | 190–240 |
| **Foliage** | | | **≈ 1600–1750** |
| Rocks (incl. 2 cavity rocks) | 9 | 22–30 | 200–250 |
| Pebbles | 4 | 8–10 | 32–40 |
| Moss pads | 5 | 14–18 | 70–90 |
| Tuft blades (6 tris) + hubs (8) | 32 + 6 | | 240–260 |
| **Base** | | | **≈ 540–640** |
| **Hero** | | | **about 3750–3900** (limit 4000; ceiling 3900) |
| Parts: TrunkCore / BranchModule (BM1) / CrownModule (TL shape) / RootModuleA / B / C | | | 800–900 / 120–150 / 250–300 / 70–90 each (limit 1000) |

- **Skeleton vs foliage split:** about 47 % skeleton, 41 % foliage, 13 % base (054: 46 / 39 / 15). The trunk is this
  model's subject, so the skeleton keeps its share; spend headroom on the bell's strand facets first (a fourth facet per
  strand on the front half: the shingles), then the 20-tri cards.
- **If the hero passes 3900:** drop the sprout (−50), then tuft blades to 5 (−32), then the strands to 10 (−36), then
  the cards to 68 (never below 7 per big clump), then RK7. Never subdivide; never thin the limbs or the bell.
- **The parts are far under 1000** (each root module is its own part), so no part-budget squeeze this time.

### 4.4 What to do better than W05's `AncientTree`, 047, 053 and 054

| Earlier | This one |
| --- | --- |
| W05: "squat cone trunk"; flutes as shallow lines | a concave bell of eight twisted strands with 0.5–0.9 V grooves, a waist 9.4 at z 12.8 above a 19-wide shoulder |
| W05: "flat pale crown, no vines" | seven card mounds, lime / mid / dark by height, twelve lime strands with bulb tips |
| W05: "hollow variant not hollow" | a real cavity with a slit and a pointed arch, rocks and a tuft inside |
| 047 round 1: stub limbs, hidden twigs | full limb runs with bare forks under L and R, the leader in the gap; T above h .45 ≥ 9 % |
| 047 round 1: pads read as balls | cards overlapping 30–50 % on a dome, one outline per clump |
| 047 round 2: plants buried in roots and rocks | the ray-parity guard from day one, walls included (§6) |
| 053: knot hidden at the f34; pipe-like limbs; moss olive in shade | the slit faces the f34 camera (check it); arms taper to ≤ 0.5 with forked ends; moss 58–61° with value ≥ 0.80 lit |

### 4.5 Stages 2 and 3
- **Stage 2:** every shell closed and manifold; 0 bowties (card centres, tine junctions, strand bulb tips, the jamb
  corners, toe forks are the likely spots: `M.fix_bowties`); **0 winding errors per shell** (STAGES "Consistent
  winding": the inner cavity wall faces must point **into the cavity** (outward of the wall solid) — the easiest place
  to flip a whole band; check the jambs and every hand-built card); no zero-area faces, no n-gons except flat caps;
  corners ≥ 3°. Origin bottom centre, transforms applied.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box, sd ≤ 1.4)

| Swatch | Box | Hex | HSV | Use |
| --- | --- | --- | --- | --- |
| Bark (Main) | (748,72,790,115) | `#B36F40` | 25°, 0.64, 0.70 | start for `bark` |
| Bark (Light) | (815,72,857,115) | `#E4B054` | 38°, 0.63, 0.89 | start for `bark_light` |
| Foliage | (881,72,923,115) | `#9CBC19` | 72°, 0.87, 0.74 | the canopy median target / start for `leaf_mid` |
| Rock | (947,72,989,115) | `#A49F9C` | 22°, 0.05, 0.64 | start for `rock` |

### 5.2 Rendered regions (`samp.py`, `samp3.py`; median / v > .7 / lit quartile / shade quartile)

| Region | Median | v > .7 | Lit Q | Shade Q |
| --- | --- | --- | --- | --- |
| Canopy f34 / front / rear / side / r34 / top | `#A5BA11` (67°, .91, .73) / `#98AD0A` (68°, .94, .68) / `#9EB511` / `#8DA710` / `#A8BC14` / `#90AC0E` | `#DBE411` / `#D5E007` / `#D4E011` / `#D2DF0E` / `#D7E316` / `#D3E00A` | `#E5EC1C` / `#DFE80A` | `#375D0C` / `#3A5909` |
| Canopy by tone (front: light h < 72 / mid / dark h ≥ 92) | `#D0DC07` / `#58800F` / `#2B5711` (rear dark `#3E7426`, side `#3C6E1F`, f34 `#346A23`) | | | |
| Canopy tone shares (light / mid / dark %) | f34 58 / 27 / 15; r34 59 / 30 / 11; front 58 / 32 / 10; side 55 / 34 / 11; rear 59 / 31 / 11; top 54 / 41 / 4 | | | |
| Canopy bands (front, light / mid / dark %) | h .85–1.0: 75 / 16 / 9; .70–.85: 61 / 27 / 12; .55–.70: 55 / 37 / 8; .40–.55: 44 / 45 / 11 | | | |
| Wood f34 / front / side / rear | `#A46839` (26°, .65, .64) / `#B06F35` (28°, .70, .69) / `#A16934` / `#8F5E38` | `#EC9E50` / `#EC9F49` / `#EA9F47` / `#EEA254` | `#F8B464` / `#F8B25C` | `#563219` / `#5B3719` |
| Wood by height (front): roots h < .2 / trunk .2–.45 / limbs > .45 | `#B77736` / `#C5793D` / `#9E6127` (f34 limbs `#895227`) | `#EEA74A` / `#F2A24D` / `#E49643` | | |
| Cut faces (cu1 trunk top, cu3 rim) | `#FAC172` (35°, .54, .98) / `#F3AA5C` (31°, .62, .95) | | | cu1 `#BD8148` |
| Holes: front slit (f34) / back arch (r34) / log bore (cu1) / cavity interior (cu3) | `#0A0702` (v .04) / `#0B0703` / `#130904` / `#56331D` (23°, .66, .34; shade `#271910`) | | | |
| Rocks: f34 front-centre / front-left / right tall | `#ADA598` (37°, .12, .68) / `#BDB1AA` / `#BCAFA0` | `#CEC2BB` (22°, .09, .81) / `#C5BBB7` / `#CEBFB5` | `#D1C6C0` / `#D9CFC8` / `#DDD0C9` | `#58626E` (212°, .20, .43) / `#626E7F` / `#646872` |
| Rocks slate: f34 tall slab / f34 in the cleft / r34 in the arch | `#545B63` (212°, .15, .39) / `#665F5E` / `#6C6C72` | | `#68798D` / `#756E71` / `#8E8A91` | `#393F44` / `#4E4D4F` / `#515256` |
| Moss strands f34 / r34 | `#747E07` (65°, .94, .50) / `#658106` (74°, .95, .51) | `#E9E008` (58°, .97, .91) / `#D0C014` | `#E5D706` (56°) | `#35570B` (87°) / `#325708` |
| Ground moss (G at h < .03) f34 / front / rear / side | `#B8BC09` (61°, .95, .74) / `#CECE17` (60°, .89, .81) / `#C3C211` / `#CCC81E` | `#CCD108` / `#DCD421` / `#D0CD13` / `#D3CF1B` | | |
| Grass blades (G at h .06–.22) f34 / front / rear | `#83980D` (69°, .91, .60) / `#829511` / `#889A0D` | `#CFD207` (61°) / `#D2CD0A` / `#CEC90B` | | `#354E10` (84°) / `#3A4F13` / `#314510` |

### 5.3 How the colour works

- **Leaves (cards and cores):** three keys ordered **by height within each clump and in the crown** (role and position,
  never facing): the **upper 40 %** of a clump's cards `leaf_light` (BR, BL, FR tops 75 % light), the **middle** cards
  `leaf_mid`, the **lowest ring and droop cards** `leaf_dark`; the core dome `leaf_dark`. LB and FL (tucked under, 8–13 %
  lime from above) carry mostly mid and dark; R and BL the most lime. `K.blend(mode="blend", steps=3)` across card
  heights so a clump goes lime → mid → dark without a hard band. Per-card Tint ±0.04.
- **Moss strands:** by position along the strand: the top 30 % (in the clump's shade) `strand_deep`, blending through
  `steps=3` to `strand` (lime) over the lower 70 % and the bulb; the two strands deepest under L and R 20 % deeper
  overall. Never by facing.
- **Bark:** one warm orange-brown (`bark`, 24–28°, R > G > B) everywhere; **per-plate colour** — every plate run (a
  facet run between two plate rings) picks one of `bark` (55 %), `bark` 30 % toward `bark_light` (30 %) or `bark` 25 %
  toward `bark_deep` (15 %), held whole along the plate (the sheet's shingles); **lighter** (`bark_light`) on cut faces
  (the cap, the cap rim, spur and tine ends, the jamb edges' first facet, the parts' bores rims and pegs); **deeper**
  (`bark_deep`) in the strand grooves (faces touching a pulled-in groove vertex), kink and fork crotches, under each
  boss, the valleys between roots where they meet the bell, the lowest 0.6 of roots and toes, and the limbs' undersides
  **by position under the crown** (limb faces below z 20 within the crown's footprint: 20 %, a shade region by place);
  **`hollow`** in the slit and arch jamb faces' inner halves, the cap's radial cracks, every pit, the dark tine and toe
  ends; **`cavity`** on the inner wall and ceiling. Roots a touch lighter (`bark` 15 % toward `bark_light`) on their
  top ridges by position on the section.
- **Moss on bark:** four root-ridge patches (§2.3) and two trunk patches (front above the slit z 13–16, back beside the
  arch z 11–13) in `moss`, hard at the edge, Tint ±0.03.
- **Rock:** warm pale grey `rock` (lit 20–35°, sat 0.08–0.14, R ≥ G ≥ B); `rock_light` on the top 30 % of each rock by
  height; `rock_slate` (212–222°, 0.12–0.18) on the lowest 30 % of every rock, the whole of the tall slabs RK1 / RK6 below
  their top 20 %, and the cavity rocks (by role and height, §3.10).
- **Moss pads:** `moss` (58–61°, very saturated, value ≥ 0.80 lit), edges 15 % `grass`.
- **Grass:** blades lime toward the tips and outer blades (`grass`), inner and lower blades `grass_deep` (78–85°).
- **Hues stay apart:** bark 24–28°, cut wood 31–38°, strand lime 56–60°, moss 58–61°, grass 60–66°, leaf light 62–66°,
  leaf mid 72–80°, grass deep 78–85°, strand deep 82–88°, leaf dark 95–105°, rock 20–35°, rock slate 212–222°.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians where the sheet gives them, swatches where it doesn't. `K.sample`
kinds: `"brown"` for bark, `"stone"` for rock, `"vivid"` for the lime keys, `"green"` for leaf mid / dark.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m057_leaf_light` | canopy light-tone median `#D0DC07` ± 12 (lit `#DFE80A`) | 62–66°, ≥ 0.92 | upper cards | rough 0.8, low spec |
| `m057_leaf_mid` | the Foliage swatch `#9CBC19` rendered lit ± 12 (mid-tone median `#58800F` in shade) | 72–80°, 0.80–0.90 | middle cards | rough 0.85 |
| `m057_leaf_dark` | dark-tone median of the lit views `#3A6E22` ± 12 | 95–105°, 0.65–0.75 | low / droop cards, cores | rough 0.9 |
| `m057_strand` | strand v > .7 `#E0D80A` ± 12 | 56–60°, ≥ 0.92 | strands' lower 70 % and bulbs | rough 0.9, low spec |
| `m057_strand_deep` | strand shade `#35570B` rendered lit → about `#4E7A0E` ± 12 | 82–88°, 0.82–0.90 | strands' top 30 % | rough 0.9 |
| `m057_bark` | front whole-wood median `#B06F35` ± 15 (f34 `#A46839`); v > .7 `#EC9F49` ± 12 (start `#B36F40`) | 24–28°, 0.64–0.72, **R > G > B** | trunk, limbs, roots | rough 0.9 |
| `m057_bark_light` | cut faces `#FAC172` ± 12 lit (start `#E4B054`) | 32–38°, 0.52–0.64 | the cap, cut ends, jamb edges, plate highlights (30 %) | rough 0.85 |
| `m057_bark_deep` | wood shade quartile seen lit, `#6E4022` ± 15 | 22–26°, 0.65–0.72 | grooves, crotches, root valleys, limb undersides (20 %), plates (15 %) | rough 0.95 |
| `m057_hollow` | slit / arch `#0A0702` → `#120A04` ± 8 (v ≤ 0.08) | 25–35°, 0.7–0.85 | jamb inner halves, cracks, pits, dark ends, the parts' bores | rough 1.0 |
| `m057_cavity` | cu3 interior `#56331D` seen in shade → `#3A2212` ± 12 (v ≤ 0.25) | 22–26°, 0.65–0.72 | the inner wall and ceiling | rough 1.0 |
| `m057_rock` | rock v > .7 `#CEC2BB` ± 10; median `#ADA598` ± 15 (start `#A49F9C`) | 20–35°, 0.08–0.14, R ≥ G ≥ B | rocks, pebbles | rough 0.85, metal 0 |
| `m057_rock_light` | lit quartile `#D9CFC8` | 22–30°, 0.06–0.10 | top 30 % of each rock at 35 % | rough 0.85 |
| `m057_rock_slate` | slab median `#545B63` → lit about `#6E7887` ± 12 | 212–222°, 0.12–0.18 | lowest 30 % of rocks, the tall slabs, cavity rocks | rough 0.9 |
| `m057_moss` | ground moss `#CECE17` ± 12 (v > .7 `#DCD421`) | 58–61°, ≥ 0.88 | moss pads, root and trunk patches | rough 0.95, low spec |
| `m057_grass` | blades v > .7 `#D2CD0A` ± 12; median `#829511` | 60–66°, ≥ 0.88 | outer and taller blades | rough 0.85, low spec |
| `m057_grass_deep` | blade shade `#3A4F13` rendered lit → about `#4E7414` ± 12 | 78–85°, 0.75–0.88 | inner and lower blades, hubs | rough 0.85, low spec |

**Calibration warnings:**
- **The kit studio lights both halves** (042, 047, 053): calibrate `bark` to the whole-wood median and v > .7 together;
  053's lit wood came out 21–24 levels low in R — check v > .7 against `#EC9F49` and add plate spread rather than
  pushing the base key orange.
- **Leaves must not go pale or olive:** W05 rev 6 failed "pale lime". The sheet's lime is genuinely 62–68° and very
  saturated: `leaf_light` 62–66°, s ≥ 0.92; `leaf_mid` and `leaf_dark` clearly green (≥ 72° and ≥ 95°). Check the
  canopy median within 15 of `#98AD0A` (front) and the tone shares.
- **Moss must not go olive-mustard in shade** (053 finding 4): `moss` value ≥ 0.80 lit, hue 58–61°; check the rear and
  top renders, not only the f34.
- **Bark must not go red:** R > G > B, hue ≥ 24° on every median. **Cut wood vs bark:** `bark_light` ≥ 45 levels lighter
  (V) than `bark` and ≥ 6° yellower, or the cap and cut ends won't read.
- **The slit and arch must read black at cell scale:** `hollow` v ≤ 0.08; the `cavity` key stays ≤ 0.25 so the hollow
  reads dark behind the opening, not brown.
- **Rocks never pink or mauve** (M034, M037): R ≥ G ≥ B on `rock`, and `rock_slate` blue-grey, not purple.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Clumps:** per card by its height rank within the clump (top light → middle mid → lowest dark), blended across 3 steps
  of rank; BR, BL, FR shifted 0.15 lighter, LB and FL 0.25 darker. Cores hard `leaf_dark`. Hard where card meets bark.
- **Strands:** by length fraction, `strand_deep` → `strand`, 3 steps.
- **Trunk and roots:** per-plate keys held whole (§5.3); `bark_deep` blended one facet out from each groove column and
  root valley; 25 % `bark_deep` on the lowest 0.6 of every root and toe; hard `hollow` / `cavity` in the openings; hard
  `bark_light` on cut faces; hard `moss` on the six moss patches. Per-plate Tint ±0.04 plus broad noise 0.03 at scale
  0.25.
- **Limbs:** `bark` base; a `bark_deep` ring at every kink and fork crotch (30 %); the under-crown shade region (20 %);
  pits hard `hollow`.
- **Rocks:** height bands within each rock (light top, base, slate foot). **Grass, moss:** per blade by role; pad edges
  15 % `grass`.
- **Hard edges only** where materials meet: cut face | bark, hole | rim, bark | leaf, strand | leaf, wood | ground
  dressing, rock | moss.

### 5.6 Texture (Tint) and finish
- **Tint:** bark 0.04 per plate + 0.03 broad; leaf cards 0.04 per card (whole cards); strands 0.03 per strand; rock 0.04
  per facet; moss 0.03 at scale 0.2; blades 0.04 per blade.
- **Finish:** bark 0.9 (deep 0.95), cut wood 0.85, hollow / cavity 1.0; leaves 0.8–0.9, low spec; rock 0.85–0.9; grass,
  moss, strands low spec. No emission.

### 5.7 Re-measure (final renders against the sheet, same masks)
- **Canopy:** front median within 15 of `#98AD0A`; v > .7 within 12 of `#D5E007`; tone shares 58 / 32 / 10 ± 8 (front),
  58 / 27 / 15 ± 8 (f34); the top band (h .85–1.0) ≥ 65 % light.
- **Bark:** front whole median within 20 of `#B06F35`; v > .7 within 12 of `#EC9F49`; R > G > B.
- **Cut wood:** the cap and cut ends within 15 of `#FAC172`. **Holes:** the slit and arch v ≤ 0.10 at cell scale.
- **Strands:** v > .7 within 12 of `#E0D80A`; median 60–78°.
- **Rock:** v > .7 within 10 of `#CEC2BB`, R ≥ G ≥ B; slabs read blue-grey (hue 200–230°). **Moss** within 12 of
  `#CECE17` in front **and** rear; **blades** v > .7 within 12 of `#D2CD0A`.
- **Shares** per §2.7.

## 6. Joins and contact (no floating dressing, no buried dressing)

- **Shells:** two cavity-wall shells and the upper trunk (closed, overlapping by 0.3; decision §8.6); each branch module
  one or more closed shells (main run a ring-stack shell; arms, spurs and tines welded at a ring junction or closed
  shells buried ≥ 0.2); each clump's stub, core and every card its own closed shell; each strand, root module, rock,
  pebble, moss pad, blade and hub its own closed shell. All in one hero object.
- **Module seats:** base face 0.015 off the boss / socket face, 0.02 wider all round; read the gaps back (BVH nearest per
  module: 0.005–0.03) and check **no module corner inside the trunk solid** by ray parity (047's `plug_report`), except
  the 0.3 buried root ends (record them).
- **Clump chain:** card → core (or a neighbour card) within 0.03; core → stub top buried 0.4–0.6; stub → module tip
  (0.015). **No card floating**, **no card buried** (centre outside the core, ≤ 25 % of its verts inside it, none more
  than 50 % inside a neighbour). Count both per clump and report them.
- **Strands:** top ring buried 0.3–0.5 in a core or limb underside; no strand vertex inside a card or a limb other than
  its anchor; the bulb ≥ 0.3 clear of every card and limb below it.
- **Limbs under clumps:** the bare forks (LOW-L, LOW-R) stay outside every card; module tips ≥ 0.4 inside their clump
  core.
- **Toes:** sunk 0.05 below z 0; root undersides 0–0.05 below z 0 along their low run.
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**. A shell floats if its nearest distance to
  every other shell and the ground is > 0.03 or it doesn't chain to the ground: card → core → stub → module → boss →
  upper trunk → walls → ground; strand → core or limb; blade → hub → pad or ground; rock → ground.
- **Count buried shells** (STAGES; 047 round 2 blocker): **0 dressing shells more than 0.05 inside a root, toe, a wall,
  the trunk or a rock**, by ray parity against the full hero after the final placement step. Use 047's guard from the
  start (`_Solids`: both walls, the upper trunk, every root and every rock added as built; three skewed rays, two of
  three agree; placement accepts ≤ 0.03; a blade that still cuts after its retries is **dropped**, never kept). The
  cavity pieces are tested against the walls too (inside the cavity is outside the wall solid).
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no particles, no falling leaves, no fireflies, no dust in the arch.
The strands are lime, not luminous (their lit tone is the render's light). The cast shadow is the render's.

- **Stage 5 (lighting): skip, and record why.** No emission, no lights. Studio notes (Requires Manual Validation): the
  canopy keeps its lime tops and green body under the game sun (not olive, not pale); the strands stay lime; the bark
  orange-brown, not red; the slit, arch and pits read near black; cut faces pale; rocks pale-topped slate; moss and grass
  lime. Check the arch interior isn't lit flat by Roblox ambient (the `cavity` key is dark for that reason).
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** W05's variants had dust and resin effects; this
  sheet has no variant cells (decision §8.14).
- **Collision:** hero `precise` (players walk under the clumps, between the roots and into the arch; a hull would wrap a
  32 × 30 × 32 block); trunk core `precise`; branch module, crown module and root modules `hull`. Strands, moss pads and
  tufts walk-through only if the exporter already supports `kit_nocollide` (it is written by W01 / W02 scripts but not
  split by the current exporter; decision §8.11).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json` and the repo text
(`git grep`, `.glb` excluded):
- **W05:** `AncientTree`, `AncientTreeTrunkCore`, `AncientTreeBranchModule`, `AncientTreeCrownModule`,
  `AncientTreeRootModuleA/B/C`, `AncientTreeHollowTrunk`, `AncientTreeForkedGiant`, `AncientTreeResinBearing`; also
  `OakTree*`, `DeadTree*`. **R08 / 029:** `AncientRoot`, `AncientRootBase`, `AncientRootDepleted`, `AncientRootHalfLeft`,
  `AncientRootHalfRight`, `AncientRootLeafClump`, `AncientRootMineralNodule`. Old: `GoldencrownAncientFork`,
  `GoldencrownHollowGiant`.
- **Elder\*:** `ElderberryShrub*`, `ElderberryLeafClump`, `ElderberryForkedStem`, `ElderberryBerryBunch`,
  `ElderberryLeafUnderside`; `build_lobby.py` places a prop named `EldersTotem_ElderTree`. So **no `Elder*` prefix**.
- **Old / Great / Giant:** `OldPine*` (W04), `GiantCoilFern*`; no `Great*` names. **Other trees:** `GnarledPine*` (047),
  `TwistedSnag*` (053), `ShadeTree*` (054), `BroadleafTree*` (lobby), `SilverbarkTree`, `GoldencrownTree`.
- **`Monarch`, `MonarchTree`, `Patriarch`, `Elderwood`, `Mossbeard`, `Greatroot` and `m057` occur nowhere** in the repo
  text, manifests or builders. `MonarchTree*` contains no owned name as a substring.

| Object | Part | Why |
| --- | --- | --- |
| `MonarchTree` | hero: trunk core (walls + upper), four branch modules, seven clumps + the sprout, twelve strands, eight roots, base dressing | a "monarch" is the forester's word for the oldest, largest tree in a stand; W05 owns `AncientTree*`, R08 `AncientRoot*` |
| `MonarchTreeTrunkCore` | "Trunk Core": walls, upper trunk, bosses, cap with sockets and cracks, sprout stub | the sheet's label |
| `MonarchTreeBranchModule` | "Branch Module": BM1, the left side module with its spur and bare fork, bore and peg on its base | the label points at BM1 |
| `MonarchTreeCrownModule` | "Crown Module": the TL shape with its stub (as BL in the hero) | the label points at the exploded's TL |
| `MonarchTreeRootModuleA` / `B` / `C` | "Root Module A / B / C" with close-up 2's hollow joining end | the labels |

- Palette keys `m057_*` (§5.4). Collection `Kit/M057 Ancient Tree`. No sockets (VFX).

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **32.0 tall, crown 32.7 × about 30, waist 9.4 × 8.0, root reach 11.5–14.5** (recommended: 1.6× the
   20-stud 054 / 047, near W05's 34.7; lowest leaves at 10.6–11.2 and strand tips at 10–16, so players walk under; the
   arch 3.8 × 10.6), or 28 (arch 3.3 × 9.2) or 36 (crown 37 wide).
2. **Name (§8):** **`MonarchTree` and the six parts above** (recommended), or `Mossbeard` (after the strands). Not
   `AncientTree*` (W05), `AncientRoot*` (R08) or `Elder*` (Elderberry, the lobby's `ElderTree`).
3. **Crown plan (§2.5, §3.3):** **seven clumps from the top cell's seven clefts — BR, BL, FR high; L and R low at the
   sides; LB and FL low, tucked under — plus the small trunk sprout SP; front / rear govern positions, the side is
   judged for content** (recommended), or five clumps as the exploded counts (the top cell clearly shows seven).
4. **Limb plan (§2.4):** **four modules: BM1 left side → L + spur → FL; BM2 right side → R + a cut spur; BM3 Y top-left →
   BL + LB; BM4 Y top-right → BR (the main leader) + FR; bare two-tine forks under L and R** (recommended), or a fifth
   module for FL off the trunk (+100 tris).
5. **Joints (§3.7):** **bosses and module overhangs in the hero, root ends buried in the flare; bores, pegs and hollow
   root ends only on the parts** (recommended), or pegs in the hero too (+120 hidden tris).
6. **Hollow foot (§2.2, §3.5):** **a real cavity to z 9.6 built as two closed C-arc wall shells plus a solid upper trunk
   overlapping them by 0.3 (no booleans), opened by a front slit (az 272°, 1.6 wide, to z 10) and a pointed back arch
   (az 92°, 3.8 wide, to z 10.6), with two slate rocks and a tuft inside** (recommended), or a shallow 1.5-deep dark
   recess behind each opening (cheaper by ~150 tris, but the r34's rocks inside the arch can't show).
7. **Walk-in (§3.6):** **keep the sheet's arch size; collision precise lets a player step in** (recommended), or close
   the cavity's collision.
8. **Roots (§2.3):** **eight high-starting buttress roots from three shapes (A ×3, B ×3, C ×2), 60° gaps at the slit and
   arch** (recommended; the front shows six to seven tips, W05 used seven), or seven.
9. **Leaf cards and strands (§2.5):** **74 lobed 16-tri cards (Ø 3.0–4.4) over dark cores; up to 24 five-lobe cards if
   the budget allows; twelve 5-sided strand drips with bulb tips** (recommended), or fewer, larger cards (reads coarser
   than the sheet's 2.8-stud scallops).
10. **Comparison cameras (§3.2):** **`front_sheet (0, 5)` governs positions, `f34_sheet (0, 13)` the read** (probe az
    −35 … +35, e 9–16 once); `rear_sheet (180, 5)`, `r34_sheet (180, 13)`, `side_sheet (90, 5)`; kit `top`; extras:
    parts shot (0, 22), `junction_cu`, `root_end_cu`, `hollow_cu`, `arch_cu`, `clump_cu`, scale shot. Floor hidden in
    every `*_sheet` render.
11. **Collision (§7):** **hero and trunk core `precise`; branch, crown and root modules `hull`** (recommended); strands,
    tufts and moss walk-through only if the exporter splits `kit_nocollide` (it doesn't today).
12. **Exported parts (§8):** **the hero plus the six labelled parts** (recommended), or also BM2–BM4 and the other crown
    shapes.
13. **Colour (§5):** **leaves by height role to `#D0DC07` / `#9CBC19` / `#3A6E22` (canopy median `#98AD0A`); strands
    `#E0D80A` / `#4E7A0E`; bark to `#B06F35` with v > .7 `#EC9F49`, per-plate shingle spread; cut wood `#FAC172`; holes
    `#120A04`, cavity `#3A2212`; rock lit `#CEC2BB` with a slate foot `#6E7887`; moss `#CECE17`; grass `#D2CD0A` /
    `#829511`** (recommended).
14. **Stages 5 and 6:** **skip both, recorded** (recommended); W05's dust / resin effects belong to its variants, not this
    sheet.
15. **Budget (§4.3):** **4000 limit, about 3750–3900 planned (skeleton ≈ 1780, foliage ≈ 1650, base ≈ 580), ceiling
    3900 for this one (the kit's largest tree), parts far under 1000** (recommended), or the usual 3800 ceiling (drop the
    sprout and two strands first).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **Limbs hidden in the clumps (047 round 1 "stub limbs, hidden twigs"; the user's tree rule).** T above h .45 ≥ 9 % in
   the front, rear and f34 (sheet 10.6–11.6); wood fifth 4 ≥ 6 %; LOW-L and LOW-R each ≥ 3.0 studs of bare limb and
   Y-TR's leader ≥ 2.0 in front, rear and f34; both bare forks visible under the side clumps; the canopy bottom gap at
   x .00–.05 (≥ .60 H); the inner undersides of L and R kept up.
2. **A closed crown from above.** The top view must show the pale cap and ≥ 4 limb arms in an open hub (T 5–13 %) and
   **seven clefts** round the outline (W05's "merged top ring" failed); no card within r 4.5 of the axis above z 19.
3. **Pipe-like limbs (053 finding 2).** Every arm tapers to ≤ 0.5 of its base Ø; forks end in two blunt tines; spurs
   flat-cut.
4. **A cone or a straight column for a trunk (W05 "squat cone"; 047 "straight column").** The bell: outer wood rows .60 /
   .39 / .30 of H at h .20 / .30 / .40 (± .05), concave between; eight strands with 0.5–0.9 V grooves, twisted ~38° CCW,
   the "/" on the front; the roots start high (z 10–12) on the bell.
5. **The hollow not reading (W05 "hollow variant not hollow"; 053 "knot hidden at the f34").** The slit dark and visible
   in `front_sheet` and `f34_sheet`; the arch pointed, dark, with rocks inside in `rear_sheet` and `r34_sheet`; O below h
   .35 within 1.5–3 % of the silhouette; check the slit at the chosen f34 camera before stage 4.
6. **Clumps as balls or blobs (047 round 1; W05 "gem-like puffs").** Each clump one mound with a scalloped outline (front
   scallops 34 ± 8), cards overlapping 30–50 %, tones ordered by height, no sky through a clump's middle.
7. **Spiky leaves and needle grass (memory `kit-quality-bar`; 039).** Cards with broad rounded lobes; tuft blades broad at
   the base (L : W ≈ 4), never edge-on to the f34 or front camera.
8. **Buried or floating dressing (STAGES; 035 / 036; 046; 047 round 2).** 0 floating shells; 0 cards buried; 0 strands
   floating or through a card or limb; 0 blades, hubs, pads or rocks more than 0.05 inside a root, toe, wall, the trunk
   or a rock, by ray parity after the final placement; hubs ≥ 0.3 clear of root and wall surfaces.
9. **Winding (044) and bowties.** 0 faces wound against their neighbours per shell — **the cavity's inner wall and
   ceiling are the new risk** (a whole inward band flipped would make Roblox cull the cavity into a see-through hole);
   check every jamb, every hand-built card and every strand bulb.
10. **Pale or olive canopy and moss (W05 rev 6 "pale lime"; 053 moss olive in shade; 047 plants yellow).** Canopy median
    within 15 of `#98AD0A`; leaf light 62–66° saturated; mid and dark clearly green; moss value ≥ 0.80 lit in the rear
    and top renders as well.
11. **Colour by facing (042 ruling).** `bark_deep` only in grooves, crotches, valleys and the under-crown region by
    position; plate keys by plate, not by normal; card tones by height rank; slate rock by role and height; `K.check`
    facing correlation < 0.5 per material.
12. **Flat orange or red bark (W05); lit wood low (053, 047).** Whole median within 20 of `#B06F35`, hue 24–28°, R > G >
    B; v > .7 within 12 of `#EC9F49`.
13. **Egg, mauve or purple rocks (M034, M037).** Angular blocks, 8–14 broad facets, flat bases; tall slabs as slabs.
14. **Size not reading (memory `kit-relative-scale`).** Report the bbox and a scale shot with the 5.5 marker and, if it is
    in the kit file, 054's 20-stud `ShadeTree`; 057 must read 1.6× bigger.
15. **Exact booleans:** none needed (walls + upper trunk as overlapping closed shells, bosses grown into the ring
    stack). If a union is used for the bosses, at the origin, one at a time, saving between them (STAGES "Booleans").
16. **Over budget from the leaves.** Count tris per clump as you go (≤ 260 for BR including core and stub, ≤ 230 for the
    other big clumps); cut the sprout, strands and cards before thinning the skeleton.
17. **Names and scope.** No `AncientTree*`, `AncientRoot*`, `Elder*`, `ShadeTree*`, `GnarledPine*`, `TwistedSnag*`;
    only one agent drives a Blender session at a time; no commits, pushes or exports in stage agents; don't edit the
    frozen shared helpers, `m053.py`, `m054.py` or `lib/vfx.py`; don't touch other models' collections.

## Decisions (main session, 2026-10-30)
All 15 recommendations are accepted.

1. **Size.** 32 tall, crown about 32.7 × 30. The trunk is a twisted bell, waist 9.4 × 8.0. Lowest leaves sit at z 10.6–11.2.
2. **Name.** `MonarchTree`, plus `…TrunkCore`, `…BranchModule`, `…CrownModule` and `…RootModuleA/B/C`. Keys `m057_*`. Never `AncientTree*`, `AncientRoot*` or `Elder*`.
3. **Crown plan.** Seven clumps plus the sprout, laid out from the top cell's seven clefts.
4. **Limb plan.** Four modules, with bare forks under L and R. **Every arm tapers to 0.5 or less of its base** (053's finding). Bare limb must read at least 1.5 studs in the front, rear and f34 views (the user's tree rule).
5. **Joints.** Pegs, bores and hollow root ends appear only on the parts. No pale ring may show at a joint.
6. **Hollow foot.** A real cavity built from two wall shells plus the upper trunk, with rocks and a tuft inside. **The cavity's inner walls and ceiling must be wound correctly (0 winding errors), never culled into see-through holes.**
7. **Walk-in.** Keep the sheet's arch size, so a player can step inside.
8. **Roots.** Eight, built from the three module shapes.
9. **Foliage.** 74 cards and 12 strands.
   - Cards are lobed and toned by height. No ball domes and nothing spiky.
   - Strands are seated by contact. **No floating or buried dressing.**
10. **Cameras.** `front_sheet (0, 5)` and `f34_sheet (0, 13)`; probe ±35° once.
11. **Collision.** Precise on the hero and trunk core; hull on the modules.
12. **Exports.** The hero plus six parts.
13. **Colour.**

    | Region | Colour |
    | --- | --- |
    | Leaves | `#D0DC07` / `#9CBC19` / `#3A6E22` |
    | Canopy median | `#98AD0A` |
    | Strands | `#E0D80A` / `#4E7A0E` |
    | Bark | `#B06F35` (lit `#EC9F49`) |
    | Cut wood | `#FAC172` |
    | Holes | `#120A04` |
    | Cavity | `#3A2212` |
    | Rock lit | `#CEC2BB` |
    | Rock slate foot | `#6E7887`, chosen by role and height only |
    | Moss | `#CECE17` |
    | Grass | `#D2CD0A` / `#829511` |

    Blend by position and role, **never by facing**. The canopy must not read pale or olive.
14. **Stages 5 and 6.** Skipped, and recorded as skipped.
15. **Budget.** Ceiling 3900, under the 4000 hard limit. Follow the spec's trim order if it runs over.

**Binding checks.** The front shares in §1 (canopy green 46.3, wood 37, each ±4); wood above h .45 at 10.6–13.6 % in every side view; and the §1.5 differences from M047, M053, M054 and W05.

## Stage 1 — Modelling (modeller, 2026-10-30)

Builder `art/blender/kit/mcp/m057.py` (`build()`). Background session port 9882 on `wip/M057.blend`; the final build was
run in a freshly restarted session and the file saved after it. It imports `m047` (tube frames, `_Solids` ray-parity
guard), `m033` (hulls, mottle, long lens, close-up framing) and `m012` (UV unfold, thin check, bottom centre); helpers
copied from `m054.py` (not imported) and adapted. Shared helpers untouched. Every exploded part has its own function and
the hero is assembled from exactly those functions (`hero_all`).

- **`trunk()`**: the whole trunk is **one closed shell, no booleans**.
  - An outer ring stack of 26 columns: eight strands at the root azimuths 20/60/120/160/200/240/300/340, each a groove
    vertex pulled in 0.75 and two crest verts at 37 / 63 % of the strand's span, alternate strands ±5 %.
  - Nine rings at z 0 / 2.2 / 4.4 / 6.6 / 8.6 / 10.4 / 12.8 / 15.6 / 19.5 (X × Y 13.6 × 12.0 → **9.4 × 8.0 at z 12.8** →
    6.6 × 6.0 at the top), twisting 0 → 38° CCW, so the front grooves climb "/".
  - The grooves at 90° and 270° are **split into two jamb columns**; the wall cells between them in rows 0–4 are left
    out. That gives the **back arch** (3.4 → 3.2 → 2.9 → 2.4 → 1.5 wide, closing to 0.5 at z 10.4: a pointed arch) and
    the **front slit** (1.6 → 0.6, 0.4 at z 10.4; the groove above it is pulled 0.95 deep to z 12.8).
  - Radial **jamb faces** join the jamb columns to a **cavity inner wall** (two 5-vertex arcs between the openings, 0.66
    of the crest ellipse: inner 9.0 × 7.9 at z 0), closed by a cone ceiling to z 12.0. A bottom annulus (each arc zipped
    to the outer ring by azimuth) closes the foot.
  - A flat pale cap with six dark radial crack wedges; four square bark pits (0.42, sunk 0.08) on crest plates.
  - `trunk(cut=2)` is the cavity walls only, with a pale cut rim (close-up 3).
- **`root()`** ×8 (RT1–RT8; module shapes A ×3, B ×3, C ×2; reach 11.6–13.8):
  - vertical sections along a snaking plan path; the stations follow the twisted strand (+14 / +8 / +3°, then half the
    kink bend);
  - section: a flat bottom, upright lower flanks, two shoulder facets and a broad crest (a log-like buttress, not a fin);
  - a concave crest line, for example A: (r 4.4, z 11.0, buried in the bell) → (6.0, 7.6) → (8.4, 4.2) → (reach − 2.2,
    2.0);
  - two blunt splayed triangular toes on z 0, their ends half pale and half hollow;
  - the part (`root_part`) has a square socket in its joining face and a pale peg.
- **`module()`** ×4 (table `BM`):
  - BM1 / BM2, the side modules: 8-sided main runs from inside the trunk (Ø 3.4 / 3.2); 6-sided arms (BM1's main arm into
    L and its spur arm into FL; BM2's main arm into R); 4-sided **bare two-tine forks** (tips 0.48 of the base Ø); BM2's
    5-sided cut spur with a pale end.
  - BM3 / BM4, the Y modules on the cap (Ø 3.2 / 3.4), fork into up arms (BL and BR: the leaders) and out arms (LB, FR).
  - **Every arm tapers to ≤ 0.5 of its base Ø**: 2.3 → 1.05, 1.9 → 0.9, 2.15 → 1.0, 2.1 → 1.0, 1.95 → 0.85, 2.4 → 1.0,
    2.0 → 0.85. Arms end inside their clump core.
  - A deep ring at each knuckle; pits only on near-square faces. `sprout_stub()` feeds SP.
  - The BM1 part has a bored base and a pale peg; `bosses_part()` adds the trunk part's two side bosses and two cap
    sockets.
- **`leaf_clump()`** ×7 plus SP:
  - a 5-sided core dome (bottom ring, widest ring, shoulder, top);
  - the whole mound **leans out from the trunk** (`tilt` 8–30°: outer side down, inner underside up so the limbs show);
  - Fibonacci cap cards over polar 0–100° (+12° on the outer side), each tilted 14–24°;
  - each card seated by `_seat_card` (1–2 of its 10 verts inside the core, its centre outside) and checked by
    `_card_ok` against the trunk, the limbs and every other clump's core;
  - a rejected card moves round the dome (5 tries); none was dropped;
  - all cores are built first, so no card hides in a neighbour's core.
- **`leaf_card()`**: a closed 16-tri card.
  - A 9-vertex rim of **three rounded lobes with two tip verts each** (±14°; radii 1.0 / 0.9 / 0.84 rc; notches 0.6).
  - A centre raised 0.34 rc above the rim, and a flat triangulated underside.
  - Smallest lobe-tip corner **112.5°** (`card_tip_angle()`; ≥ 110 asked).
  - Card radius 2.7 (Ø 5.4) on the big clumps, 1.27 on SP.
- **`strands()`** ×12: 3-sided lime drips (top r 0.55 buried 0.45 in the core underside, neck r 0.3, bulb r 0.46, point).
  Each is hung by a ray from below and moved toward the clump centre if it would cross a card or a limb. None was
  dropped.
- **Base:**
  - 7 slate rocks (two tall slabs, RK1 and RK6), 2 cave rocks (CR1 behind the arch, CR3 behind the slit) and 3 pebbles;
  - 4 lobed moss mounds (top 0.34);
  - 10 tufts (4–5 folded lanceolate blades on a 4-sided hub; one in the cavity);
  - 7 **leafy sprigs**: upright three-lobed cards on the ground, facing the cameras (the sheet's rounded-leaf plants).
  - Everything is placed through the `_Solids` guard: rocks step outward or sideways until ≤ 0.05 into wood, tuft hubs
    move out along their ray, blades turn, stand up or shorten, and pads move and shrink.
- **Nothing is below z 0.** Rocks and pads sit on z 0, as do toes and root bottoms, so the trunk foot is the bbox bottom:
  the hero's `m057_offset` and `origin_offset` are both (0, 0, 0).

**Iterations** (renders against the sheet cells with scratch `m057w/sbs.py`, measured with `m057w/meas2.py` and the
study masks):
1. Ball clumps on tall root fins, 4162 tris → no skirts, bigger cores, domed cards, log-section roots, budget trims.
2. "Umbrella" clumps with flat drooped undersides → the drooped core replaced by a tilted dome.
3. A gappy crown and a 21 % wooden hub from above → clumps enlarged and pulled in (W : D and top T).
4. Hidden limbs (LOW-L 0 in the f34, Y-TR 0) → the sprout lowered and shrunk, FL raised, FR moved right and up.
5. Height 30.9 → BR's top raised.
6. 29 cards with their centres inside a core → a centre test and the other-cores guard. Bowties at shared toe apexes →
   toes start apart. Sliver pits → pits only on faces with aspect ≤ 2.4, and wider opening tops.

**Deviations from the plan (for the main session):**
1. The trunk is one closed shell (outer stack, jambs, inner wall, ceiling, foot annulus), not two C-arc wall shells plus
   an overlapping upper trunk. This is cleaner: no hidden overlap. Both openings close at z 10.4 (slit asked 10.0, arch
   10.6). The ceiling is a cone to z 12.0, not flat at 9.6.
2. No bosses in the hero: the module main runs start 1.3 inside the trunk, and their swell is the crotch. Bosses with
   sockets are only on `MonarchTreeTrunkCore`. Root high ends are buried in the bell (decision 5).
3. Clumps: 5-sided cores and no skirt cards (the lean replaces the droop).
   - Clump sizes and centres changed from §2.5 to close the crown (final table `CLUMPS`), for example BR (3.15, 9.3)
     15.0 × 15.5, L (−10.9, −2.4) 15.0 × 11.5, FR (6.2, −7.2) 11.4 × 13.5.
   - Cards are Ø 5.4 (asked 3.0–4.4): 74 cards can't cover the bigger clumps at 3–4.
4. Budget cuts against the plan:
   - strands are 3-sided (asked 5);
   - toes are triangular, 2 per root (B asked 3);
   - 2 cave rocks + 1 tuft (asked 2 + 1); 3 pebbles (asked 4);
   - 4 moss pads (the 222° pad can't clear RT5 / RT6, so the guard drops it);
   - 10 tufts + 7 sprigs (the sprigs are an addition, for the ground green);
   - 4 trunk pits + 4 module pits (asked 8–10 + 6–8).
5. Moss on two root crests (RT5, RT7) and two trunk plates (asked four roots): the stripes read hard.

## Stage 2 — Optimisation and cleanup

| Object | Tris | Size (studs) | Shells |
| --- | --- | --- | --- |
| MonarchTree (hero) | **3878** (ceiling 3900) | 33.74 × 29.98 × 32.12 | 213 |
| MonarchTreeTrunkCore | 844 | 13.63 × 12.11 × 19.68 | 6 |
| MonarchTreeBranchModule | 160 | 10.12 × 9.12 × 5.97 | 6 |
| MonarchTreeCrownModule | 218 | 11.10 × 10.71 × 8.47 | 11 |
| MonarchTreeRootModuleA | 96 | 8.06 × 8.93 × 11.0 | 4 |
| MonarchTreeRootModuleB | 96 | 8.86 × 7.68 × 11.6 | 4 |
| MonarchTreeRootModuleC | 96 | 6.99 × 7.46 × 10.4 | 4 |

**Hero tris by shell kind** (skeleton 1516, foliage 1590, base 772):

| Kind | Shells | Tris |
| --- | --- | --- |
| trunk | 1 | 620 |
| limbs | 13 | 368 |
| tines, spurs and the sprout stub | 4 | 48 |
| cores | 8 | 214 |
| cards | 74 | 1184 |
| strands | 12 | 192 |
| roots | 8 | 352 |
| toes | 16 | 128 |
| rocks and pebbles | 12 | 272 |
| moss pads | 4 | 64 |
| blades | 44 | 264 |
| hubs | 10 | 60 |
| sprigs | 7 | 112 |

- **Every object:**
  - 0 non-manifold edges and **0 bowtie verts** (none needed fixing);
  - 0 boundary, wire, loose, zero-area, n-gon or duplicate verts;
  - normals outward, transforms applied;
  - origin at the bbox bottom centre (offset 0, 0, 0 on all seven);
  - smallest corner 4.3° (none under 3°).
- **Per shell, all seven objects:** **0 winding errors**, 0 self-intersections, every volume > 0. The winding count
  includes the cavity inner wall, ceiling and jambs, which are part of the one trunk shell. `K.check` is clean, and
  `build()["problems"]` is **empty**.
- **Contact:** 0 floating and 0 unchained shells in all seven objects (tol 0.03). The hero is anchored on its ground
  shells (sprigs included), the parts on their largest shell; pegs touch their bore floors.
- **Buried (ray parity, `bury_report`):**
  - 0 of 159 dressing shells (blades, hubs, pads, cards, cores, strands, sprigs) are more than 0.05 inside the trunk, a
    root, a toe or a rock (max 0.0);
  - rocks into wood: 0 (worst 0.029, RK4);
  - cards in their cores: 0 (max 2 of 10 verts, no centre inside; also checked against the other cores);
  - cards pierced by limbs: 0.

## Stage 3 — UV

`M.smart_uv` angle-based (45°, margin 0.008) plus `m012._uv_unfold`. All seven objects have 0 overlaps and 0 flipped,
min island gap 0.016, border 0.008, density 1.0 / 1.0 / 1.0 and conformal stretch p95 ≤ 1.013. Islands: hero 1310,
trunk 127, branch 48, crown 60, roots 29 / 31 / 29.

## Stage 4 — Materials, colour and texture

1. **`K.calibrate`** on the kit dome, to `TARGETS` (decision 13). Calibrated keys (rendered sRGB in brackets):

   | Key | Calibrated | Rendered |
   | --- | --- | --- |
   | leaf_light | `#A5B304` | 206, 218, 9 |
   | leaf_mid | `#839D18` | 160, 189, 24 |
   | leaf_dark | `#345F22` | 58, 109, 34 |
   | strand | `#B1B007` | 222, 214, 10 |
   | strand_deep | `#44690D` | |
   | bark | `#8B5B28` | 175, 111, 54 |
   | bark_light | `#DC9D62` | 255, 192, 114 |
   | bark_deep | `#583315` | |
   | hollow | `#000000` | 31, 29, 27 |
   | cavity | `#2A0E01` (red) | |
   | rock | `#A29EA0` | 205, 194, 188 |
   | rock_light | `#AAA8A9` | |
   | rock_slate | `#576374` | 110, 120, 134 |
   | moss | `#A3A817` | |
   | grass / grass_deep | `#A7A807` / `#446413` | |

2. **Re-measured on the tree renders.** The tree shades itself, so the dome values came out dark and red on the tree, as
   053 and 054 found. Final values are in `PALETTE`:
   - bark lifted in linear light (R ×1.39, G ×1.62, B ×1.46) to `#BC7B36`, so the front wood median and v > .7 land on
     the sheet; bark_light `#F0B868`, bark_deep `#7A4A24`;
   - leaf_mid moved greener and lighter to `#8AB51B` (the swatch-calibrated `#839D18` rendered at a "light" hue and
     flattened the tones); leaf_dark `#3A6A26`; leaf_light kept at `#B3C205`;
   - hollow `#0E0803`, cavity `#301A0C` (not red);
   - rock `#9C9590` / `#B2ABA5` (R ≥ G ≥ B), slate `#576374`;
   - moss `#C2C014`, grass `#B4B208`, grass_deep `#4A6E13`, strand `#B8B407`, strand_deep `#44690D`.
3. **Roles (never facing; no `normal` chooses paint anywhere):**
   - **Trunk**, per plate cell by role:
     - crest plates: bark 45 %, bark→light 25 % for 37 %, bark→deep 25 % for 18 %;
     - groove flanks: bark→deep 50 % for 50 %, bark→deep 25 % for 32 %, bark 18 %;
     - cells beside an opening deep 25–50 %, the foot band deeper;
     - per-plate Tint ±0.04 plus broad mottle 0.03;
     - jamb faces hollow; inner wall and ceiling cavity;
     - cap bark_light with six hollow crack wedges;
     - two mossy plates (front above the slit, back beside the arch).
   - **Roots**, by section edge: bottom deep 50 %; lower flanks deep 25 % or bark; shoulders bark, light 25 % or deep
     25 %; crest light 25 % or bark; per-plate Tint. Moss→bark 25 % crest plates on RT5 and RT7. Toes: ends half pale,
     half hollow; inner face deep.
   - **Limbs:** bark, with a deep 25 % ring at each knuckle (by position), pale cut ends, hollow pits.
   - **Cards**, by height rank in their clump (`TONE_STEPS`: light to 0.70, mid→light 75 / 50 %, mid, mid→dark 50 %,
     dark):
     - shifted per clump: BR / BL +0.15, FR +0.1, R +0.05, L −0.05, LB / FL −0.15;
     - shifted by broad position noise (`TONE_PATCH`);
     - per-card Tint ±0.04.
   - **Other dressing:**
     - cores by height in their own unturned frame;
     - strands by length (deep top → lime bulb, 4 steps);
     - rocks by height and role (pale top, warm body, slate foot; slabs and cave rocks slate below their top 20 %);
     - pads moss with grass-edged outer lobes;
     - blades: tall ones lime, short ones deep;
     - sprigs: leaf keys.
4. **Facing correlation** (`kit_baked_shading`): hero 0.26, trunk 0.26, parts ≤ 0.38 (limit 0.5).
5. **Finish:** leaves 0.8–0.9 with low spec; bark 0.9 (deep 0.95); cut 0.85; hollow and cavity 1.0; rock 0.85–0.9; moss,
   grass and strands low spec. No emission.

**Measured against the sheet** (`m057w/meas2.py`, study masks, ours / sheet; final renders, floor hidden, 3× lens):

| View | W : H | G | canopy G | ground G | T | T above h .45 | R | fill | tones L / M / D (ours vs sheet) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| front_sheet (0, 5) | **0.994** / 1.032 | 52.0 / 54.5 | **46.9 / 46.4** | 4.7 / 7.7 | **40.5 / 37.0** | **13.0** / 11.1 | 6.9 / 4.2 | 0.563 / 0.618 | 53 / 38 / 9 vs 58 / 32 / 10 |
| f34_sheet (0, 13) | 0.920 / 1.093 | 53.1 / 51.5 | 48.0 / 42.7 | 4.6 / 8.3 | 39.2 / 36.6 | **11.3** / 10.8 | 7.1 / 6.9 | 0.564 / 0.653 | 56 / 36 / 8 vs 58 / 27 / 15 |
| rear_sheet (180, 5) | 0.983 / 0.995 | 50.8 / 54.4 | 47.4 / 46.8 | 3.4 / 7.4 | 42.8 / 37.2 | **13.3** / 10.9 | 5.7 / 4.3 | 0.562 / 0.589 | 42 / 47 / 12 vs 59 / 31 / 11 |
| r34_sheet (180, 13) | 0.994 / 1.075 | 51.0 / 52.2 | 46.9 / 45.8 | 3.5 / 6.1 | 42.5 / 36.8 | **12.6** / 11.8 | 5.8 / 5.9 | 0.575 / 0.652 | 45 / 44 / 11 vs 59 / 30 / 11 |
| side_sheet (90, 5) | 0.872 / 0.950 | 56.0 / 52.8 | 54.1 / 45.3 | 1.7 / 6.6 | 37.2 / 37.7 | 3.9 / 13.6 | 6.7 / 5.2 | 0.545 / 0.573 | 38 / 50 / 12 vs 55 / 34 / 11 |
| top_sheet (0, 89) | W : D 1.097 / 1.067 | 84.6 / 84.9 | | | 13.5 / 8.9 | | 1.7 / 1.8 | 0.627 / 0.654 | 72 / 26 / 2 vs 60 / 35 / 5 |

**Colours** (ours / sheet):

| Region | Ours | Sheet |
| --- | --- | --- |
| Canopy median, front | `#82A20D` | `#98AD0A` |
| Canopy median, f34 | `#A1B80E` | `#A5BA11` |
| Canopy median, rear | `#8EB613` | `#9EB511` |
| Canopy v > .7, front | `#D7EA12` | `#D5E007` |
| Wood median, front | `#B16D32` | `#B06F35` |
| Wood median, f34 | `#B87033` | `#A46839` |
| Wood v > .7, front (R > G > B, hue 27°) | `#E79242` | `#EC9F49` |
| Rock v > .7, front (R ≥ G ≥ B) | `#CFC1AF` | `#D3D0B6` |
| Ground moss (h < .05), front, shaded under the crown | `#9CB110` | `#BEBF0F` |

- The arch interior's median is `#211F1D` (v .13 in the close-up; black at cell scale). Strands median in the close-up:
  `#91A00D`.

**Profiles, front** (ours against the sheet):

| Profile | Ours | Sheet |
| --- | --- | --- |
| Top (f .0–1.0) | .55 .71 .78 .93 .93 .97 1.00 .96 .87 .71 .59 | .54 .70 .82 .92 .89 1.00 .95 .96 .85 .75 .60 |
| Width per height | .13 .88 .53 .37 .85 .93 .97 .83 .59 .51 | .53 .82 .63 .39 .79 .95 .97 .86 .61 .48 |
| Canopy bottom (every 0.1 W) | .50 .44 .58 .42 .62 .75 .69 .48 .54 .50 | .42 .38 .51 .54 .45 .66 .56 .54 .36 .46 |

- Width per height: the bell row at h .3 is .37 against .39.
- Canopy bottom: the centre gap is at .75 / .69.

## Stage 5 — Lighting

Skipped: the sheet shows no emission or light (decision 14).

Studio notes (Requires Manual Validation). Under the game sun:
- the canopy should keep lime tops and green bodies (not pale, not olive);
- the bark should stay orange-brown, not red;
- the slit, arch, cracks and pits should read near black, and the cavity dark brown (check that Roblox ambient doesn't
  light it flat);
- cut faces pale; rocks pale-topped slate;
- moss, tufts, sprigs and strands lime.

## Stage 6 — VFX

Skipped: the sheet shows no effect (decision 14). No object has sockets (checked in `build()`).

## Renders

All in `art/blender/renders/models/M057/`:
- **Contact sheet and kit views:** `M057_views.png`; kit `front`, `side`, `rear`, `top`, `underside`; `front34`, `rear34`.
- **Sheet comparisons** (floor hidden, 3× lens): `f34_sheet`, `r34_sheet`, `front_sheet`, `side_sheet`, `rear_sheet`,
  `top_sheet`.
- **Parts:** `part_trunkcore`, `part_branchmodule`, `part_crownmodule`, `part_rootmodulea`, `part_rootmoduleb`,
  `part_rootmodulec`.
- **Exploded:** `exploded` (the trunk core lifted, the four modules drawn out round it, five crown modules with stubs
  above, the three root modules below).
- **Scale:** `scale` (5.5-stud markers in the back arch and under L, with 054's 20-stud `ShadeTree` beside it: 32.1
  against 20.0) and `scale_rear` (the marker standing in the arch).
- **Close-ups:**

  | Render | Shows |
  | --- | --- |
  | `arch_cu` | the pointed dark arch, a cave rock inside |
  | `slit_cu` | the front slit |
  | `hollow_cu` | the cavity walls cut at z 4.4: thick wall, pale rim, dark hollow (close-up 3) |
  | `junction_cu` | the trunk top with the Y modules |
  | `junction_part` | the part's pale cap, cracks, two sockets and the BM1 boss socket (close-up 1) |
  | `fork_cu` / `fork_r_cu` | the bare forks under L / R |
  | `clump_cu` | L with its strands |
  | `strand_cu` | the strands |
  | `root_cu` | RT6 |
  | `root_end_cu` | Root Module A's bored joining end and peg (close-up 2) |

## §1.5 differences, as measured

| | 057 as built |
| --- | --- |
| Size | 33.74 × 29.98 × 32.12 (1.6× the 20-stud ShadeTree in `scale`); front W : H 0.994 |
| Silhouette | a bell trunk (h .3 row .37 of W) under a seven-clump dome; canopy G 46.9, T 40.5 (13.0 above h .45); 12 strands below |
| Trunk | 9.4 × 8.0 waist, eight strands twisted 38° CCW with 0.75 grooves, 13.6 × 12.0 foot, a hollow foot with a front slit and a pointed back arch, cave rocks and a tuft inside |
| Limbs | two side modules (bare two-tine forks, a spur) and two Y modules on a pale cut top; seven clumps plus the sprout; the hub open from above (T 13.5) |
| Roots | eight log-section buttresses from three shapes, 16 toes, moss on two crests |
| Foliage | 74 rounded three-lobed cards (tips ≥ 112.5°) on eight leaning cores; twelve lime strands with bulb tips |
| Ground | no patch: lime moss mounds, ten lime tufts, seven leafy sprigs, slate rocks with pale tops (two tall slabs) |

## Modeller's notes for the verifier

- **Rebuild** in a fresh session: `import kit_mcp; kit_mcp.install(); import m057; m057.build()`. It takes about 50 s
  with the renders; `build(render=False)` takes 10 s.
- **Checks:**
  - `m057.shells_report(o)`: per-shell winding;
  - `contact_report`;
  - `bury_report`: dressing in wood or rock, and cards in any core and in limbs;
  - `limb_visibility(hero)`: studs of bare limb per polyline (BM1 = [main, main arm, spur arm, tine, tine]; BM2 = [main,
    main arm, tine, tine, spur]; BM3 / BM4 = [main, up arm, out arm]);
  - `card_tip_angle()`.
- **Measuring scripts:** scratch `m057w/meas2.py` (study masks) and `m057w/sbs.py` (sheet | ours).
- **Visible bare limb** (studs):

  | Limb | Front | Rear | f34 | r34 |
  | --- | --- | --- | --- | --- |
  | LOW-L (BM1 main + main arm) | 5.5 | 6.0 | 4.4 | 3.7 |
  | LOW-L tines | 1.3 + 1.2 | 1.5 + 1.6 | 1.5 + 2.2 | 0 + 0.5 |
  | LOW-L spur arm | 2.7 | 2.6 | 0.7 | 0.4 |
  | LOW-R (BM2 main + arm) | 5.3 | 4.4 | 4.3 | 3.6 |
  | LOW-R spur | 1.6 | 1.3 | 1.1 | 0.8 |
  | LOW-R tines | 0 | 0 | 0 | 0 |
  | Y-TL (BM3 main + up + out) | 1.5 | 2.3 | 5.8 ✓ | 1.0 |
  | Y-TR (BM4 main + up arm) | 3.1 + **2.0** | **0.6** | 3.1 + 1.2 | 0 |

  LOW-R's tines are hidden in every view by R's lower cards. Y-TL meets its ≥ 1.5 in the f34.
- **Known leftovers:**
  1. **Y-TR from the rear shows 0.6** (asked ≥ 2.0). BR covers it from behind, and lifting BR pushes the rear wood above
     h .45 past 13.6 (now 13.3). BM3's leader shows 2.3 from the rear instead.
  2. **Wood and ground from behind.** Rear and r34 wood T is 42.8 / 42.5 against 37.2 / 36.8 (±4): the bell and roots
     read heavier from behind. The front's 40.5 is just inside. Ground green is 3.4–4.7 against 6.1–8.3 (the sheet's
     lush plants; budget). Fill is 0.56 against 0.59–0.65.
  3. **Top and side.** Top T is 13.5 (asked 5–13), and the top tones 72 / 26 / 2 are lighter than 60 / 35 / 5. The side
     view's wood above h .45 is 3.9 against 13.6, and its W : H 0.872. The side is judged for content (§3.3): clumps on
     both sides, strands on both sides, the bell.
  4. **Front canopy colour.** The front canopy median is `#82A20D` against `#98AD0A` (R −22: shaded undersides at e 5).
     The f34 median and the front v > .7 match. Front tones are 53 / 38 / 9 against 58 / 32 / 10.
  5. **Crown texture.** The cards are Ø 5.4 three-lobed cushions on leaning cores. The crown reads as one lumpy dome with
     rounded lobes, coarser than the sheet's many small leaves, and the clefts between clumps are softer than the
     sheet's.
  6. **f34 width.** The f34 W : H is 0.920 against 1.093. The sheet's f34 is drawn wider (§3.2); not chased.
  7. **Root parts alone.** The Root Module parts read as tall buttress wedges when seen alone. Their inner end is the
     tall section that is buried in the bell in the hero.
  8. Deviations 1–5 under Stage 1.
- No commits, pushes or exports were made.

## Stage 7 verification (round 1)

A fresh verifier ran this stage read-only, in a background session on port 9882 on `wip/M057_verify.blend` (the kit
copy taken after the main session's `m057.build()`; not saved).
- **Scripts** (scratch `m057v/`): `a1.py` topology; `a2.py` contact, bury and self-intersection; `a3.py` piercing;
  `a5.py` facing correlation and exposed cut faces; `uv.py`; `meas.py` and `sbs.py` pointed at `verify/`; `scal.py`
  scallops at sheet-cell scale.
- **Renders:** `renders/models/M057/verify/`.

**Verdict: FAIL, 6/10.** The skeleton, the hollow foot, the topology and the contact are all clean. But the crown, about
half of every silhouette, doesn't read like the sheet's lobed leaf clumps:
- the crown module part reads as a cabbage ball;
- the side view reads as three separate balls.

### Re-measured (all seven objects)

| Check | Result |
| --- | --- |
| Tris | hero **3878** (ceiling 3900); TrunkCore 844, BranchModule 160, CrownModule 218, RootModuleA / B / C 96 each |
| Size | hero 33.74 × 29.98 × 32.12 (H 32 ± 0.6 ok; X 33.74 is inside 32.7 ± 1.2); parts as in Stage 2 |
| Origin / transforms | bbox bottom centre (0, 0, 0) on all seven; rot 0, scale 1, no modifiers, no custom normals, one UV layer |
| Topology | 0 non-manifold, 0 boundary, 0 wire, 0 loose, 0 zero-area (none under 1e-4 either), 0 n-gons (all tris), 0 duplicate verts, **0 bowties**; min corner 4.3° |
| Winding | 0 edges whose two faces disagree, in all 213 hero shells. The cavity wall, ceiling and jambs are part of the one trunk shell, whose volume is > 0. Every shell volume is > 0 on all objects |
| Self-intersections | 0 in every shell (BVH self-overlap, adjacent faces excluded) |
| Floating | 0 isolated, 0 unchained (tol 0.03; overlap or vertex-to-surface; chained from z ≤ 0.03) |
| Buried (ray parity, 3 skewed rays, 2 of 3) | 0 cards, strands, pads, blades, hubs or sprigs inside wood or rock (worst card 0.005). Three cores (BR, SP, FL) hold an arm end 0.20–0.49 deep: that is the designed arm-in-core seat, not buried dressing. Rocks into wood: worst 0.018 (RK4 against a toe) |
| Cards in cores | max 2 of 10 verts, 0 centres inside, 0 over 25 % |
| Pierced | **1 strand crosses a LOW-L tine** (intersection 0.66 long at (−12.1, −1.5, 15.6); not visible in any render). 1 SP card grazes the sprout stub (0.53 long, 0.005 deep; invisible) |
| UV | 0 overlaps, 0 flipped, every island in 0–1, island gaps ≥ 0.01, density p05 / p95 1.00 / 1.00 (hero 1310 islands) |
| Facing paint | **Pass.** No `normal` chooses paint anywhere in `m057.py`. Normal-z vs luminance: cards 0.02 (one key per card, by height rank), blades 0.02, limbs 0.19. Cores 0.74, rocks 0.57, roots 0.58 and sprigs 0.65 correlate only because they are painted by height or section role, as §5.3 planned. Object-level `kit_baked_shading` 0.26 (< 0.5) |
| Exposed cut faces | 7 pale `bark_light` caps of 0.35–0.47: main-run end caps showing past the arms at the Y-module forks ((−1.7…−3.1, 0, 22.2–22.5) and (3.5, −0.2, 22.0)) and at the LOW-L / LOW-R knuckles. Visible as pale patches in `junction_cu` (decision 5: no pale ring at a joint) |

### Views against the sheet (study masks; ours / sheet)

| View | W : H | canopy G | ground G | T | T above h .45 | fill | tones L / M / D (ours vs sheet) | scallops at sheet-cell scale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| front_sheet | 0.992 / 1.032 | 47.5 / 46.4 | **4.8 / 7.7** | 40.8 / 37.0 | 13.2 / 11.1 | **0.559 / 0.618** | 51 / 39 / 9 vs 58 / 32 / 10 | **24 / 34** |
| f34_sheet | 0.917 / 1.093 | 48.5 / 42.7 | **4.7 / 8.3** | 39.6 / 36.6 | 11.4 / 10.8 | 0.560 / 0.653 | 55 / 37 / 9 vs 58 / 27 / 15 | **18 / 43** |
| rear_sheet | 0.975 / 0.995 | 48.0 / 46.8 | **3.4 / 7.4** | **43.2 / 37.2** | 13.4 / 10.9 | 0.557 / 0.589 | 41 / 47 / 12 vs 59 / 31 / 11 | **17 / 36** |
| r34_sheet | 0.989 / 1.075 | 47.4 / 45.8 | **3.5 / 6.1** | **42.8 / 36.8** | 12.7 / 11.8 | 0.567 / 0.652 | 44 / 44 / 12 vs 59 / 30 / 11 | |
| side_sheet (90°) | **0.868 / 0.950** | **54.8 / 45.3** | 1.9 / 6.6 | 37.5 / 37.7 | **3.9 / 13.6** | 0.540 / 0.573 | 37 / 50 / 13 | **22 / 33** |
| side (270°), ours only | 0.866 | 54.8 | 2.3 | 36.8 | 4.8 | 0.547 | 47 / 40 / 13 | |
| top_sheet | W : D 1.090 / 1.067 | | | **13.4 / 8.9** | | 0.623 / 0.654 | **71 / 27 / 2 vs 60 / 35 / 5** | **22 / 44** |

**Profiles:**
- **Front top profile** matches: .54 .71 .78 .93 .93 .97 1.00 .96 .87 .71 .59 against .54 .70 .82 .92 .89 1.00 .95 .96
  .85 .75 .60.
- **Bell rows** at h .2 / .3: .53 / .37 against .63 / .39. The root shoulders are 0.10 narrow.
- **Canopy bottom at the centre:** .76 / .69 against .66 / .56. That window is **sky**; on the sheet the leader runs
  into foliage there.
- **Side top profile:** .11 .87 .90 .90 .79 **.76** .93 .98 .99 .96 .86, a notch at the centre. The sheet's side is one
  dome: .55 .70 .72 .85 .85 .93 .99 .96 .95 .75 .62.

**Colours (ours / sheet):**

| Region | Ours | Sheet | Reading |
| --- | --- | --- | --- |
| Bark, front wood median | `#B16C31` | `#B06F35` | hue 28°, R > G > B: warm brown, not red |
| Bark, v > .7 | `#E89142` | `#EC9F49` | G 14 low |
| Bark, rear lit wood | `#C37D3B` | `#EEA254` | the studio's shaded back |
| Canopy, front median | `#819E0E` | `#98AD0A` | ΔR −23; hue 72°, s .91: green, not olive |
| Canopy, f34 median | `#9EB70E` | `#A5BA11` | matches |
| Canopy, v > .7 | `#D8EB11` | `#D5E007` | matches |
| Canopy, top median | `#C4DB0B` | `#ADC20F` | too light |
| Low rocks | `#BDAEA1` (28°, .15) | `#AAA396`–`#BCB0A9` | warm |
| Tall slab | `#777C82` lit, `#383D42` shade (210–213°) | `#596368` (200°, .14) | the `#576374` slate key reads **blue-grey slate, not lavender** |
| Ground moss (h < .05) | `#9AB211` | `#BEBF0F` | greener (sprigs, shade) |

### Blockers

1. **The foliage doesn't read like the sheet** (the user's tree rule; decision 9).
   - The cards are Ø 5.4 three-lobed pyramids. Decision 9 accepted 74 cards at **Ø 3.0–4.4** and explicitly rejected
     "fewer, larger cards".
   - At sheet-cell scale the crown outline has **about half the sheet's lobes**: front 24 / 34 (outside 34 ± 8), f34
     18 / 43, rear 17 / 36, side 22 / 33, top 22 / 44.
   - Side by side (`m057v/crown_cmp.png`, `sbs1.png`, `sbs2.png`), the sheet's crown is many small rounded lobed leaves
     in distinct fluffy clusters. Ours is a dome of large angular faceted plates whose outline teeth read pointed.
   - A sky window shows through the crown centre between the two Y posts (canopy bottom .76 / .69 against .66 / .56).
   - **`MonarchTreeCrownModule` reads as a cabbage ball** (`verify/part_crownmodule.png`), where the exploded draws a
     domed lobed cluster, W : H 1.2–1.5.
   - **The side view reads as three separate balls on sticks**, at both 90° and 270°, with a V-notch at the top:
     - top profile .76 at the centre;
     - W : H 0.868 (§2.7 asks 0.88–1.02);
     - canopy G 54.8 against 45.3 ± 4;
     - wood above h .45 3.9 against 13.6.
   - **Fix direction:**
     - Smaller cards (Ø 3.4–4.0) with a lower centre (dome ≤ 0.2 rc) and a rounder outline, more of them per clump.
     - Pay for them from the base: the sprigs (112 tris) and some blades.
     - Shrink BR, L and FR back toward §2.5's sizes, so fewer cards cover them.
     - Pull the high clumps in over the hub until the side shows one dome and the top's hub wood falls to about 9. This
       also closes the f34 and front sky window.
     - If the budget truly can't do it, report a budget block with the lost detail, per the skill.

### Minors (each marked as visible against the sheet, or numeric only)

1. **Y-TR from the rear shows about 0.6** (asked ≥ 2.0). Visible: the sheet's rear shows the leader entering the crown;
   ours shows only a stub above the cap. `limb_visibility` needs the build-time `LIMB_INFO`, so this was judged from the
   renders. Rear wood above h .45 is 13.4, so the skeleton itself reads.
2. **Rear / r34 wood 43.2 / 42.8 against 37.2 / 36.8** (±4; out by 2). Mildly visible: from behind, the bell and two
   straight, near-level limb runs read heavy and pipe-like.
3. **Ground green 3.4–4.8 against 6.1–8.3; fill 0.557–0.567 against 0.589–0.653.** Visible: the sheet's base is a lush,
   continuous moss band with many plants and rocks; ours is sparse. The seven added sprigs render as small lime faceted
   cups, not the sheet's leafy plants.
4. **Top: wood 13.4 against 8.9** (asked 5–13); tones 71 / 27 / 2 against 60 / 35 / 5; median `#C4DB0B` against
   `#ADC20F`. Visible: the hub is a large jumble of orange blocks and pale cut faces, and the crown is lighter and yellower
   from above.
5. **Front canopy median R low** (`#819E0E` against `#98AD0A`). Mildly visible as a slightly deeper green at elevation 5;
   not olive. The f34 matches. Otherwise numeric only.
6. **Card size Ø 5.4.** Visible; this is blocker 1.
7. **LOW-R tines hidden in every view** (they show only in `forkR_under`). Visible as a missing fork under R. The sheet
   shows the limb ending under R, so the fork itself is minor.
8. **Spec deviations:**
   - **One-shell trunk:** numeric only, and cleaner (winding verified, cavity faces correct).
   - **Openings closing at z 10.4** (slit asked 10.0, arch 10.6): numeric only. The slit and the pointed dark arch with
     its cave rock both read (`slit_cu`, `arch_cu`).
   - **No bosses in the hero:** invisible, and correct under decision 5.
   - **Leaning cores:** they contribute to the side-view balls (blocker 1).
   - **Budget trims:** the 3-sided strands are fine at view scale; the 2 triangular toes per root are visible but small;
     3 pebbles and 4 pads are part of minor 3.
   - **Added sprigs:** visible; see minor 3.
9. **Root shoulders narrow** (width at h .2: .53 against .63). The roots read as straight sloping wedges, not the sheet's
   arching, snaking logs with long low runs; visible in the front and f34. The **Root Module parts read as tall fins**
   (`part_rootmodule*`), where the exploded draws low faceted logs.
10. **Exposed pale knuckle and fork caps** (7 faces, 0.35–0.47 each). Visible in `junction_cu` only.
11. **A strand crosses a LOW-L tine** (0.66). Numeric only.
12. **f34 W : H 0.917 against 1.093.** Numeric only: §3.2 says the sheet's f34 is drawn wider.
13. **Bark v > .7 G 14 low** (`#E89142` against `#EC9F49`). Numeric only.

### What passes
- **Trunk:** a twisted eight-strand bell with a "/" twist and a hollow foot: a dark front slit and a pointed dark back
  arch with a cave rock inside. The cavity is wound correctly.
- **Skeleton:** the low limbs show ≥ 3 studs bare in the front, rear and f34; a pale cut top; wood above h .45 is
  11.4–13.4 in the front, rear, f34 and r34.
- **Crown details and size:** twelve lime strands with bulb tips; the crown height and the front top profile match; the
  size reads right against the 5.5 character.
- **Colour:** warm bark; warm pale rocks with slate-blue slabs.
- **Technical:** no breakage, no floating or buried dressing, no facing paint, clean UVs.

## Fix round 1 (fix modeller, 2026-10-30)

**Outcome: BUDGET BLOCK on the crown.** At 3950 tris the crown cannot have both cards of Ø 3.4–4.0 and
cores covered all round. Most of the other targets moved toward the sheet. The crown still reads as faceted
green domes with leaf cards on them, not the sheet's dense lobed broadleaf clumps.

Background session port 9882 on `wip/M057.blend`; the final `m057.build()` was saved. Scratch scripts are in
`scratchpad/m057fix/`:
- `hero.py` (fast hero and preview);
- `full.py` (the full build, then save);
- `vis.py` / `visimg.py` (a ray grid over ten views: the share of foliage pixels that hit a bare core, and the
  share of card pixels seen edge-on);
- `ev.sh` (one tuning loop: build, `meas2.py`, `scal.py`, `sbs.py`);
- `m057_r1_orig.py` (the round-1 builder, for the baseline).

No commits or exports.

### What changed in `m057.py`

1. **Cards: smaller, rounder and placed by exposure.**
   - Cards are Ø 4.0 (`CARD_RC` 2.0), a three-lobe trefoil: tips at ±15°, notch 0.70, lobe radii 1.0 / 0.95 / 0.9.
   - The centre is low (`CARD_DOME` 0.18 rc, was 0.34), so the cards are leaves, not pyramids. The smallest tip
     corner is **119.4°** (was 112.5°).
   - Cards are no longer a fixed count per clump. `_candidates()` scores 260 points on each core by how many
     camera directions see them:
     - 12 at e 5, 8 at e 15, 6 at e 40, plus the top;
     - rays are tested against every core and the wood.
   - `select_cards()` spreads `N_CARDS` = 89 over the exposed points with a bisected minimum spacing (3.18). Spare
     candidates replace any card the guard rejects.
   - Each card leans `CARD_UP` 0.75 toward +Z from the core normal, with jitter 0.2 (leaves face the sky).
   - SP gets its own 4 cards (Ø 2.6).
2. **Clump layout.**
   - BR, FR and BL are flatter, wider domes pulled in over the hub:
     - BR (2.6, 8.6) 14.6 × 20 × 9.8, tilt −4;
     - FR (4.6, −6.0) 13.6 × 16.6;
     - BL moved to (−4.6, 2.8), so the side view's centre notch fills.
   - L, R and FL changed slightly to keep the low limbs visible. L (−10.8, −1.8) has D 11.8, R tilt 26, and FL is
     smaller and higher.
   - Cores are `CORE_PAD` 1.1 rc inside the envelope.
   - BM3's up arm now ends in BL's new core. All seven feeding-arm tips are checked to be inside their cores.
3. **Core colour.** The cores show between the cards, so they carry leaf tones by height. Top faces are
   lit / mid patches by position noise, flanks mid→light 25 %, then mid, and the underside mid→dark 75 %. There is
   noise on the height bands; nothing is chosen by facing. `TONE_STEPS` was retuned (light to rank 0.56).
4. **Crown part.** BL is rebuilt flatter (`PART_H` 6.8) and clad densely: 35 cards of Ø 3.4 at spacing 2.0, tone
   −0.1. The stub is built first and guards the cards. Result: 650 tris, 9.96 × 9.25 × 8.13, a covered leafy dome
   (`part_crownmodule.png`).
5. **Budget.**
   - The 7 sprigs are dropped (−112). Blades went from 44 to 33 (−66).
   - Moss pads are larger, which costs no tris (ground green 3.1–3.8).
   - `HERO_CEILING` is 3950. Hero total: **3940**.
6. **Minor 8 (decision 5).** Main-run knuckle end caps, arm root caps, and tine and spur root caps are now
   bark → deep 25 %, not pale `bark_light`. Only the true cut ends (tines, BM2's spur) and the trunk's cut top stay
   pale (`junction_cu.png`).
7. **Minor 1 (Y-TR from the rear).** BM4's main run now shows **2.42** from the rear (was 0.6). Its up arm is
   hidden in BR / BL in every view.
8. One L strand moved to (−13.4, 0.8), so it clears the tine and the cards. All 12 strands are hung.

### Before → after (`meas2.py` study masks, `scal.py` scallops at sheet-cell scale, `vis.py`)

| Check | Round 1 | Fix round 1 | Sheet / target |
| --- | --- | --- | --- |
| Card Ø (hero) | 5.4 | **4.0** (SP 2.6; part 3.4) | 3.4–4.0 |
| Card tip corner | 112.5° | **119.4°** | ≥ 110 |
| Card centre height | 0.34 rc | **0.18 rc** | ≤ 0.2 |
| Cards / card tris | 74 / 1184 | 89 / 1424 | |
| **Bare core, mean of 9 side views + top** | 37.9 % (side views 34–47, top 19) | **51.4 %** (side views 51–55, top 32) | ≤ 30 |
| Edge-on cards | 9–17 % | 15–20 % | ≤ 10 |
| Outline scallops: front / f34 / rear / side / top | 24 / 18 / 17 / 22 / 22 | **22 / 24 / 18 / 23 / 22** | 34 / 43 / 36 / 33 / 44 |
| Side W : H | 0.868 | **0.875** | 0.88–1.02 |
| Side top-profile dip at the centre | .76 | **.87** | one dome (.85–.99) |
| Side canopy G | 54.8 | 55.1 | 45.3 ± 4 |
| Top wood T | 13.4 | **9.4** | 8.9 (5–13) |
| Top W : D | 1.090 | 1.125 | 1.067 |
| Top tones L / M / D | 71 / 27 / 2 | 78 / 22 / 0 | 60 / 35 / 5 |
| Front canopy bottom, two centre columns | .76 / .69 | **.69 / .71** | .66 / .56 |
| Front W : H / canopy G / T / T above h .45 | 0.992 / 47.5 / 40.8 / 13.2 | 0.989 / 46.6 / 41.7 / 13.0 | 1.032 / 46.4 / 37.0 / 11.1 |
| f34 W : H / canopy G / T above h .45 | 0.917 / 48.5 / 11.4 | 0.926 / 47.5 / 11.2 | 1.093 / 42.7 / 10.8 |
| Rear canopy G / T / T above h .45 | 48.0 / 43.2 / 13.4 | 44.9 / 45.3 / 14.7 | 46.8 / 37.2 / 10.9 |
| Front / f34 tones | 51 / 39 / 9; 55 / 37 / 9 | 47 / 46 / 7; 52 / 43 / 6 | 58 / 32 / 10; 58 / 27 / 15 |
| Ground green (front / f34 / rear) | 4.8 / 4.7 / 3.4 | 3.4 / 3.8 / 3.1 | 7.7 / 8.3 / 7.4 |
| Y-TR, rear (studs) | 0.6 | **2.42** (main run) | ≥ 1.5 |
| Y-TR up arm, front | 2.0 | 0 (hidden by BL / BR) | ≥ 2.0 |
| LOW-L main + arm, front / rear / f34 | 5.5 / 6.0 / 4.4 | 5.1 / 5.1 / 5.1 | ≥ 3 |
| LOW-R main + arm, front / rear / f34 | 5.3 / 4.4 / 4.3 | 5.5 / 4.4 / 4.4 | ≥ 3 |
| Y-TL, f34 | 5.8 | 2.5 | ≥ 1.5 |
| Pale caps at joints | 7 | 0 by construction (`junction_cu`) | 0 |
| Crown part | 218 tris, a cabbage ball | **650 tris, 35 Ø 3.4 cards, flatter dome** (W : H 1.22) | exploded dome, W : H 1.2–1.5 |
| Hero tris | 3878 | **3940** | ≤ 3950 |

**Checks** (`build()["problems"]` is empty):
- All seven objects: 0 non-manifold edges or bowties, 0 boundary edges, 0 zero-area faces, 0 n-gons, normals
  outward, 0 winding errors, 0 self-intersections. Origin at the bbox bottom centre.
- 0 floating and 0 unchained shells.
- 0 dressing buried more than 0.05.
- 0 cards in a core (max 20 % of verts), 0 cards pierced by limbs, 0 rocks into wood.
- UVs: 0 overlaps, 0 flipped.
- Facing correlation: hero 0.26, parts ≤ 0.38.
- The hero's `m057_offset` is now **(0.06, 1.03, 0)**: the crown's bbox is no longer centred on the trunk axis.
  The main session needs this when placing the hero.

### The budget block (what is lost)

- **Card count, not placement, limits coverage.** With exposure-aware placement, 89 cards of Ø 4.0 cover about
  half of what the cameras see of the cores. Rebuilding the same layout with `N_CARDS` 160 (hero **5012 tris**)
  brought bare core to **27 %** (side views 24–32, top 13).
- **Covering the cores at Ø ≤ 4.0 needs about 150–160 cards.** That is about 900–1100 tris over the 4000 hard
  limit.
- **The non-crown budget has nothing left.** Trunk 620, limbs 416, roots 480, rocks 272, strands 192, cores 214,
  blades and hubs 258, pads 64. Only a few cards' worth more could come out without visible losses elsewhere.
- **What the hero loses at 3950:**
  - about half the visible core surface is bare, toned as leaf by height and patches;
  - the clumps read as faceted green domes with leaf cards on them, not dense lobed clusters;
  - outline scallops stay at about 22 against 33–44.
- **Larger or more cards don't add scallops.** The `N_CARDS` 160 test still gave about 20: cards lying on a core
  do not break its outline. Scallops would need cards that stand proud at every silhouette, which the edge-on
  limit argues against.
- **The crown part, with its own 1000-tri budget, shows the target look** at about 2.3× the hero's card density.
- **Options for the main session:**
  - (a) Accept bare core about 50 % at Ø 4.0.
  - (b) Allow Ø 5–5.4 cards again on the hidden-side and underside seats only (round 1 was 38 % bare core with
    74 Ø 5.4 cards).
  - (c) Split the foliage into its own MeshPart with its own budget (for example the crown as a second
    1500–2500-tri object). That would be a ruling on the "under 4000 per hero" rule.

### Leftovers

- **Blocker 1 is only partly addressed.**
  - Card size, lobe shape, centre height, the side dome, the top hub, the front window and the crown part all
    moved toward the sheet.
  - Bare core (51 %) and edge-on cards (15–20 %) moved away from it.
  - Outline scallops are unchanged at about 22.
- Side W : H 0.875 (just under 0.88). Side canopy G 55 against 45.
- Y-TR's up arm (the leader) no longer shows in the front view (main run 2.0 does).
- Rear and r34 wood 45 against 37. Ground green 3.1–3.8 against 6–8. Top tones too light (78 / 22 / 0).
- Unchanged minors from round 1: 2, 5, 7 (LOW-R tines hidden), 9 (root shoulders), 12, 13. Minor 11 (strand vs
  tine) was not re-measured with the verifier's triangle test.

### Main session ruling on the budget block (2026-10-30)
None of options (a), (b) or (c) is taken. The hero stays one piece under 4000. Instead, the **construction changes**.

**Why.** Seen beside the sheet (`scratchpad/m057fix/fin_a.png`), the sheet's crown is made of dense, cauliflower-like clusters of small rounded leaf lumps. Cards laid on a smooth faceted core can't give that: bare core shows between them, and they don't break the outline.

**New construction for each crown clump: the core is the foliage.**
- Build the clump as a cluster of overlapping low-poly rounded sub-domes (lumps), about 0.9–1.6 studs each and roughly 10–20 tris each.
- Use 8–16 lumps per clump, in leaf tones blended by height and position, with Tint per lump.
- The lumps make the outline scallops and leave no bare core. The 056 cushion parts (`m056.lumpy_cushion`, `_lump_shell`) are a working example of the lump approach.
- Lumps may be separate closed shells that overlap their neighbours, provided the dressing rules hold: no lump is floating, and none is buried, meaning nothing more than 0.05 inside wood and no lump wholly inside another.
- Cards become optional edge detail: a small number of rounded lobed cards on the outline and underside, turned radially outward.
- Undersides are dark by height, not by facing, and must not read as flat plates.

**Also in this round:** widen the root flare toward the sheet. The sheet's buttress roots splay out almost to the crown's width, with shoulders at h .2 of about .63 against our .53, and they read as snaking logs rather than wedges.

**Targets, at all eight azimuths:**
- the clump surface reads as lobed leaf clusters;
- outline lobes are at least 70 % of the sheet's count in each view;
- the side shows one dome.
- The hero ceiling stays **3950**.

The round-1 fix's other gains are kept: Y-TR from the rear, the bark-coloured caps, the dropped sprigs and the crown part.

## Fix round 2 (fix modeller, lump clusters, 2026-10-30)

Background session port 9882 on `wip/M057.blend`; the final `m057.build()` was saved and the session stopped.
`build()["problems"]` is empty. No commits or exports. Scratch in `scratchpad/m057fix2/`: `ev.sh` (hero, previews,
`meas2.py`, `scal.py`, `sbs.py`), `full.py`, `chk.py`, `part.py`, `az.py` / `azcount.py` (outline lobes at the four
extra azimuths), `m057_fix1.py` (the round-1-fix builder, for the baseline). The new comparison is
`scratchpad/m057fix2/fin_r2.png` (sheet left, ours right: f34, front, side, rear, top).

### What changed in `m057.py`

1. **Crown clumps: the core is the foliage** (main-session ruling). The cards, the card selection and the dark cores
   are gone. Each clump is built in two steps.
   - **Sub-domes.** `lump_specs()` places the clump's macro lumps: a hidden filler that holds the arm tip, a crown
     lump, and two staggered rings turned radially outward (up axis = the envelope normal + 0.55 Z). There are 11-14
     per clump (SP 5), 84 visible in all plus 8 fillers. Each is a two-half ellipsoid (r about 2.5-3.5) standing
     0.85 r proud of an envelope shrunk to 0.6 x W, D and 0.72 x H (`ENV_K`), so they read as distinct swells.
   - **Skin.** `clump_skin()` skins the union of the sub-domes as **one closed shell per clump**: a radial
     shrink-wrap from the clump centre.
     - It is faceted into small leaf domes: spherical Voronoi cells. Each cell's apex sits 0.38-0.62 above the union
       and is fanned (6 tris) to valley verts 0.5 below it.
     - The seeds are each sub-dome's peak plus 3 petals round it, so the cell borders fall on the creases. Petals
       are skipped on the inner side (facing the trunk), and a sparse relaxed fill covers the underside.
     - The hero has about 256 leaf domes, each about 3 studs across (the sheet's lobe pitch), for 1440 tris.
   - **Why one skin, not separate lump shells.** The first tries used separate closed lumps (`it1`-`it3`: 4-sided
     antiprisms, trefoil cushions, 4-lobe rosettes). They cost 16-20 tris each and hid about half of that inside
     their neighbours. At about 90 lumps the clumps read as a few big gem balls, with 14-22 outline lobes. The
     ruling allows separate shells; it doesn't require them. A test skin that used the seeds as verts (2 tris each)
     lost the creases and read as smooth balls (19 / 15 / 17 / 16 / 11 lobes), so it was dropped.
   - **Tones.** There is **one key per leaf dome**: its apex height in the clump and in its sub-dome, the crease depth
     round it, and position noise (`TONE_*`). Undersides are dark by height and creases dark by concavity, never by
     facing.
     - Tint is set per sub-dome (+-0.05, plus +-0.015 per dome), with broad mottling.
     - Per-face height tones gave a facing correlation of 0.58, which the kit check flags. Per-dome tones give
       **0.41**.
   - **Wood clearance.** `_clear_wood()` moves skin verts that land inside a limb or the trunk onto its surface plus
     0.06. The crown part's skin is cleared off its stub the same way.
   - **Layout.** The clump layout is retuned for size, an open hub and the side dome:
     - L and R are narrower and lower (W 13.4 / 13.6, z 15.4 / 15.8);
     - BR tilt 10 at z 23.2 -> 31.2, so Y-TR shows from the rear;
     - FR z 20.0 -> 29.8, tilt 10;
     - BL top 29.8, FL tilt 22 at z 18.8;
     - BM1's spur tip is raised to (-5.3, -7.8, 20.8), so it ends inside FL.
2. **`MonarchTreeCrownModule`** is the same construction, denser and flatter (`PART_CLUMP`: 117 domes, bump x 0.6,
   tones less height-led so a small dome doesn't track its normals). It has **736 tris** and measures 11.9 x 11.4 x
   8.2 (W : H 1.45), with a dark underside, a lumpy cluster outline and its bored stub. In `_shells` the stub now
   counts as a limb, not a root.
3. **Roots are wider.** `ROOT_KIND` has 5 stations: the crest runs (r 4.4, z 11) -> (6.6, 7.8) -> (9.0, 6.1) ->
   (reach - 2.6, 3.8) -> (reach - 1.6, 2.1), width 0.95-1.05 x.
   - The section is rounder (`sh = h - 0.55 w`, crest 0.44 w).
   - An S-bend runs through the kink (`ROOT_SNAKE`).
   - The stations are forced into order (min step 0.9). The short arch roots RT2 and RT3 had folded into
     self-intersections.
4. **Checks.** `bury_report` now tests the leaf skins:
   - against the wood and rocks (verts and face centres);
   - against the limbs (verts only: the arms end inside their clumps by design, as round 1's verifier accepted for
     the cores);
   - for no lump wholly inside another.
   - `_kind` calls every leaf shell a `lump`.
   - The unused sprig code and `_card_solids` are removed. Strands are guarded against the limbs only.

### Before -> after (`meas2.py` study masks, `scal.py` at sheet-cell scale)

| Check | Fix round 1 | Fix round 2 | Sheet / target |
| --- | --- | --- | --- |
| Crown construction | 89 Ø 4.0 cards on 8 faceted cores | 8 lump-cluster skins: 84 sub-domes + 8 fillers, about 256 leaf domes, 1440 tris | lobed leaf clusters |
| Bare core (`vis.py`) / edge-on cards | 51 % / 15-20 % | **0 / 0** (no core or cards; the skin is the foliage) | <= 30 / <= 10 |
| **Outline lobes front / f34 / rear / side / top** | 22 / 24 / 18 / 23 / 22 | **29 / 32 / 29 / 25 / 30** (run-to-run spread about +-3) | >= 24 / 31 / 26 / 24 / 31 (70 % of 34 / 43 / 36 / 33 / 44) |
| Outline lobes at az 45 / 135 / 225 / 270 / 315 (side scale) | not measured | 26 / 26 / 27 / 23 / 28 | >= 23 |
| Side W : H | 0.875 | **0.892** | 0.88-1.02 |
| Side top profile | dip .87 at the centre | .71 .88 .91 .92 .90 .95 .98 .98 .98 .95 .81 (one dome, no notch; the front / back edges stay high) | .55 .70 .72 .85 .85 .93 .99 .96 .95 .75 .62 |
| Side canopy G | 55.1 | 54.8 | 45.3 +- 4 |
| Front canopy bottom, centre columns | .69 / .71 | .71 / .69 (wood behind, the trunk top and leaders; no sky) | .66 / .56 |
| Bell width at h .2 / .3 | .53 / .37 | **.62 / .41** | .63 / .39 |
| Front W : H / canopy G / T / T above h .45 | 0.989 / 46.6 / 41.7 / 13.0 | 0.983 / 48.2 / 42.3 / 11.1 | 1.032 / 46.4 / 37.0 / 11.1 |
| f34 W : H / canopy G / T above h .45 | 0.926 / 47.5 / 11.2 | 0.915 / 50.0 / 8.7 | 1.093 / 42.7 / 10.8 |
| Rear / r34 canopy G / T | 44.9 / 45.3 | 43.7 / 47.7; 42.6 / 47.8 | 46.8 / 37.2; 45.8 / 36.8 |
| Top wood T / W : D | 9.4 / 1.125 | **6.8 / 1.048** | 8.9 / 1.067 |
| Tones L / M / D: front / f34 / rear / top | 47/46/7; 52/43/6; -; 78/22/0 | 55/40/6; 59/37/4; 58/31/11; 79/17/3 | 58/32/10; 58/27/15; 59/31/11; 60/35/5 |
| Canopy median front / f34 / v > .7 | - | `#83AA0F` / `#98BB10` / `#C6E212` | `#98AD0A` / `#A5BA11` / `#D5E007` |
| Bark median / v > .7 (front) | - | `#AE6E32` / `#E08E42` (warm brown) | `#B06F35` / `#EC9F49` |
| Low limbs bare: LOW-L / LOW-R front, rear, f34 | 5.1 / 5.5 | 3.5, 5.8, 3.8 / 6.4, 5.2, 5.5 | >= 3 |
| Y-TR from the rear (main + up arm) | 2.42 | **3.8** | >= 1.5 |
| Y-TL, r34 | - | 4.0 | >= 1.5 |
| Hero tris / size | 3940 / 33.7 x 30.0 x 32.1 | **3838** / 33.42 x 31.08 x 32.17 | <= 3950 / 32.4 +- 1.4 x 30 +- 2 x 32 +- 0.6 |
| Crown part | 650 tris, 35 cards, W : H 1.22 | **736 tris**, lump cluster, W : H 1.45 | < 1000, W : H 1.2-1.5 |
| Other parts | - | TrunkCore 844, BranchModule 160 (10.1 x 9.4 x 7.5, spur raised), RootModule A / B / C 108 each | < 1000 |
| Facing correlation (kit check) | 0.26 | hero **0.41**, crown part 0.44, others <= 0.42 | < 0.5 |

**Checks (all seven objects):**
- 0 non-manifold edges or bowties, 0 boundary edges, 0 winding errors, 0 self-intersections in every shell, 0
  zero-area faces or n-gons; normals outward.
- 0 floating and 0 unchained shells.
- 0 dressing more than 0.05 inside wood or rock; 0 lump verts inside limbs; 0 lumps wholly inside another.
- All 12 strands hung. All seven arm tips are inside their clump skins.
- The hero's `m057_offset` is (0.072, 0.945, 0).
- Bark stays warm brown and the low rocks warm; the slabs are slate.

### Leftovers

- **Outline lobes.** f34 32 and top 30 sit at about the 70 % line (top needs 31). The count moves +-3 between
  near-identical builds. Bigger dome bumps raise it, but the domes then read spiky (`it_5`); 0.38-0.62 is the
  compromise. Close up (`clump_cu`), the leaf domes are faceted pyramids, not rounded leaves. At sheet scale they
  read as crinkled leaf clusters. Fully rounded domes would cost about 3x the tris (about 83 domes in the budget),
  and that tested coarser.
- **Lump size vs the ruling.** The ruling's lumps are about 0.9-1.6 studs with 8-16 per clump. Eight to sixteen
  lumps can't fill a 12-15-stud clump at that size. Here the 11-14 sub-domes per clump are r 2.5-3.5, and the
  leaf-scale lobes (about 3 studs) come from the dome cells on them.
- **Wood share.** Front T is 42.3 and rear / r34 T about 47.8, against 37 +- 4. The wider roots (the ruling) and the
  bell trunk show more wood; rear was already 45 after fix round 1. Narrower root sections (0.9 x) changed T by only
  0.1, so the bell is the driver. Ground green is still 2.7-3.5 against 6-8.
- **Side view.** The front and back edges stay high (.71 / .81 against .55 / .62). The sheet's side cell is a copy of
  the front (§3.3), while our side shows FR / FL and BR at its edges. Side canopy G is 54.8 against 45 and side T
  above h .45 is 3.9 against 13.6, both as in earlier rounds.
- **Top tones** 79 / 17 / 3 against 60 / 35 / 5. Stronger crease darkening darkened the front more than the top, so
  it was left.
- **Root Module parts alone** still read as tall buttress wedges (their joining end is the tall section buried in the
  bell); round-1 minor 9 for the parts.
- Unchanged minors from round 1: 5 (front canopy median R low: `#83AA0F`), 7 (LOW-R tines hidden), 12 (f34 W : H),
  13 (bark v > .7 G low).

## Verification round 2 (verifier, 2026-10-31)

A fresh verifier ran this stage read-only, in a background session on port 9882 on `wip/M057_verify.blend` (the kit
copy taken after the main session's fixed `m057.build()`; not saved; session stopped).
- **Scripts** (scratch `m057v2/`): `a1.py` topology; `a2.py` contact, bury, self-intersection, lumps wholly inside
  lumps, strand piercing; `a3.py` crown-part stub seat; `a5.py` facing vs height correlation; `uv.py`; `meas2.py`,
  `scal.py`, `azc.py` (lobes at eight azimuths), `sharp.py` (lobe tip width), `rocks.py`, `sbs.py`, all pointed at
  `verify2/`.
- **Renders:** `renders/models/M057/verify2/` (sheet views at 900 × 820, five extra azimuths, close-ups, parts).
  `under.png` is blank (the camera went under the floor); ignore it.

**Verdict: PASS, 7/10.** The round-1 blocker is fixed: the crown no longer reads as large angular plates, a cabbage
or three balls. From every view it reads as clustered, crinkled broadleaf foliage, and the side view is one canopy.
It is still a different finish from the sheet: faceted crumpled domes with small pointed tips, where the sheet has
rounded clover lobes. The trunk reads as a smooth flared bell; the sheet has twisted strands and separate snaking
roots. Both are visible leftovers. Neither is a breakage, and neither makes the tree read as something else.

### Re-measured (all seven objects)

| Check | Result |
| --- | --- |
| Tris | hero **3838** (ceiling 3950); TrunkCore 844, BranchModule 160, CrownModule 736, RootModuleA / B / C 108 each |
| Hero tris by kind | lumps 1440 (8 skins), trunk 620, roots 448 + toes 128, limbs 416, rocks 272, blades 198, strands 192, pads 64, hubs 60 |
| Size | hero 33.42 × 31.08 × 32.17 (all within 32.4 ± 1.4 / 30 ± 2 / 32 ± 0.6); crown part 11.90 × 11.39 × 8.20 (W : H 1.45); branch 10.12 × 9.36 × 7.51; trunk 13.63 × 12.11 × 19.68; roots 8.06 × 8.98 × 11.0, 8.71 × 7.80 × 11.6, 6.95 × 7.50 × 10.4 |
| Origin / transforms | bbox bottom centre (0, 0, 0) on all seven; rot 0, scale 1, no modifiers, no custom normals, one UV layer |
| Topology | 0 non-manifold, 0 boundary, 0 wire, 0 loose, 0 zero-area (none under 1e-4), 0 n-gons (all tris), 0 duplicate verts, **0 bowties**; min corner 4.3° (hero), 5.2° (crown part) |
| Winding | 0 edges whose two faces run the same way, in all 121 hero shells and every part shell; every shell volume > 0. The leaf skins and the cavity (part of the one trunk shell) are wound correctly |
| Self-intersections | 0 in every shell (BVH self-overlap, adjacent faces excluded) |
| Floating | 0 isolated, 0 unchained (tol 0.03; overlap or vertex-to-surface; chained from z ≤ 0.03) |
| Buried (ray parity, 3 skewed rays, 2 of 3) | 0 lumps, strands, pads, blades or hubs inside trunk, roots, toes or rocks (none at any depth). 0 lump verts inside limbs (the arm tips end inside the skins by design). 0 lumps wholly inside another. Rocks into wood: worst 0.036 (a rock against a toe at (−8.6, −10.4)) |
| Crown part stub | 0 skin verts inside the stub; 3 skin faces at the stub's entry have their centres up to 0.30 inside it (the stub crosses the underside skin there). Numeric only |
| Pierced | 1 strand crosses a LOW-L limb at (−12.9, −4.3, 13.4): 4 triangle pairs, no strand vert inside. Round-1 minor 11, still present. Numeric only |
| UV | 0 overlaps, 0 flipped, all islands in 0–1, island gaps ≥ 0.01, density p05 / p95 1.00 / 1.00 (hero 1787 islands) |
| Facing paint | **Pass.** No normal chooses a colour anywhere in `m057.py` (the one `f.normal` is the bark-pit geometry in `_pit`). Leaf skins: one key per leaf dome, from the apex height in the clump and in its sub-dome, crease depth and noise. Normal-z vs luminance is 0.42 on the lumps, but only **0.08 once height is held fixed** (partial correlation; height vs luminance 0.58, normal-z vs height 0.64). So the kit's 0.41 comes from the height bands. Crown part: 0.43, and 0.07 with height held. Roots 0.66 and trunk 0.46 come from the section-role keys (crest / shoulder / flank / bottom plates; crest vs groove), which §5.3 planned and round 1 accepted. `kit_baked_shading`: hero 0.41, crown 0.44, root A 0.42, trunk 0.26 (all < 0.5) |

### Views against the sheet (study masks; ours / sheet)

| View | W : H | canopy G | ground G | T | T above h .45 | fill | tones L / M / D (ours vs sheet) | lobes (`scal.py`) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| front_sheet | 0.983 / 1.032 | 48.6 / 46.4 | **2.9 / 7.7** | **42.7 / 37.0** | 11.3 / 11.1 | 0.594 / 0.618 | 54 / 40 / 6 vs 58 / 32 / 10 | 30 / 34 (88 %) |
| f34_sheet | 0.914 / 1.093 | 50.5 / 42.7 | **3.4 / 8.3** | 40.3 / 36.6 | 8.8 / 10.8 | 0.592 / 0.653 | 59 / 36 / 5 vs 58 / 27 / 15 | 34 / 43 (79 %) |
| rear_sheet | 0.964 / 0.995 | 44.3 / 46.8 | **2.8 / 7.4** | **47.9 / 37.2** | 15.5 / 10.9 | 0.592 / 0.589 | 58 / 30 / 12 vs 59 / 31 / 11 | 26 / 36 (72 %) |
| r34_sheet | 0.967 / 1.075 | 43.1 / 45.8 | 3.5 / 6.1 | **48.1 / 36.8** | 15.4 / 11.8 | 0.599 / 0.652 | 64 / 27 / 8 vs 59 / 30 / 11 | |
| side_sheet (90°) | 0.889 / 0.950 | **55.4 / 45.3** | 1.3 / 6.6 | 38.3 / 37.7 | **4.0 / 13.6** | 0.560 / 0.573 | 64 / 27 / 9 vs 55 / 34 / 11 | 29 / 33 (88 %) |
| top_sheet | W : D 1.044 / 1.067 | | | 6.6 / 8.9 | | 0.592 / 0.654 | **79 / 17 / 3 vs 60 / 35 / 5** | **28 / 44 (64 %)** |

- **Lobes at eight azimuths, side-cell scale:** front 29, 45° 23, side 29, 135° 26, rear 30, 225° 29, 270° 23,
  315° 28. All are ≥ 23 (70 % of the side's 33).
- **Lobe counts depend on the sampler.** A finer radial step (`sharp.py`, 0.25 px) gives front 24 / 32, f34 28 / 43,
  rear 25 / 31, side 23 / 29, top 26 / 40. That is 75 / 65 / 81 / 79 / 65 %. **Top is under 70 % with both samplers;
  f34 is at the line.**
- **Lobe tip shape, at sheet-cell scale:** the median angular width 1.5 px below a peak is close to the sheet's
  (front 3.0 / 3.5°, f34 2.0 / 3.0, rear 3.5 / 3.5, side 4.0 / 3.0, top 2.5 / 3.5). At 3 px down, ours are wider
  (11.5 / 5.5, 4.2 / 4.0, 9.5 / 6.0, 10.5 / 7.5, 6.5 / 4.5). So our outline has small, slightly sharper tips on
  broader mounds: a crinkle, not long spikes.
- **Side top profile:** .69 .88 .91 .92 .89 .95 .98 .98 .97 .95 .81. One dome; the dip at the centre is 0.03 (round 1
  had .76). The edges stay high against the sheet's .55 / .62.
- **Front canopy bottom:** .52 .54 .46 .45 .64 .72 .69 .52 .57 .54 against .42 .38 .51 .54 .45 .66 .56 .54 .36 .46.
  No sky window: wood shows behind.

**Colours (ours / sheet):**

| Region | Ours | Sheet | Reading |
| --- | --- | --- | --- |
| Bark, front median | `#AE6C32` (28°, .71) | `#B06F35` (28°, .70) | warm brown; matches |
| Bark, v > .7 | `#E08E42` | `#EC9F49` | G 17 low (round-1 minor 13) |
| Canopy, front median | `#82A70F` (75°, .91) | `#98AD0A` (68°, .94) | slightly greener and deeper; saturated, **not olive** |
| Canopy, f34 median | `#95B90F` (73°) | `#A5BA11` (67°) | close |
| Canopy, top median | `#C2D80D` | `#ADC20F` | lighter and yellower from above (top tones 79 / 17 / 3) |
| Low rocks | key `#9C9590` (R > G > B), rendered warm pale grey | `#CEC4BC`–`#D8D1CC` | warm. Render sampling here is unreliable, because the floor shadow falls in the same band |
| Slate slabs | `#68727F`–`#6D727C` (hue 212–220°, s .12–.19) | `#6B7281`–`#79828B` (hue 212–220°, s .10–.17) | matches |

### Primary question: the crown

- **Read at sheet / game distance** (`f34_sheet`, `front_sheet`, `front34`, `az045`–`az315`, `scratchpad/m057v2/sbs_*.png`):
  - The clumps read as dense, crinkled leaf clusters, each made of several swells, with dark undersides and lit tops
    by height.
  - No plates, cabbage balls or flaps, and no bare core. The skin is the foliage.
  - The crinkle reads as leaf texture, not as spikes. On the outline, though, every dome apex makes a small pointed
    tooth, so the silhouette is serrated where the sheet's is scalloped.
- **Close up** (`clump_cu`, `junction_cu`): the leaf domes are clearly faceted pyramids, like crumpled paper or gems.
  A player standing under the tree sees this.
- **Side:** one broad canopy, no V-notch, W : H 0.889. It sits low on the trunk like a mushroom cap, because no limbs
  show from the side (T above h .45 is 4.0 against 13.6). The sheet's side shows the arms reaching out to the side
  clumps.
- **`MonarchTreeCrownModule`** (`part_crownmodule`, `part_crown_side`): a domed, crinkled leafy mound with a dark
  underside and its stub. W : H 1.45 is in the exploded's 1.2–1.5. It is no longer a cabbage ball, but it reads as one
  faceted bush dome rather than the exploded cell's distinct rounded leaf lobes.

### Blockers

None.

### Minors (each marked as visible against the sheet, or numeric only)

1. **SP (sprout) clump reads as a small spiky star**, visible in `front34`, `clump_cu`, `f34_sheet` and `front_sheet`,
   in front of the trunk under the L clump. It has 5 sub-domes with full-height dome bumps on a 4.8-wide clump, so
   its apexes stand out as points: the user's "no agave stars" rule. **Visible, and cheap to fix** (for example
   `bump_k` about 0.5 on SP, as the crown part uses 0.6, or a rounder single dome). This is the one change worth
   making before the commit if the main session wants it.
2. **Crown finish: faceted, serrated domes, not rounded clover lobes.** Visible side by side, but it reads as foliage.
   The fix modeller recorded the trade-off (rounded domes cost about 3× the tris).
3. **Top lobes 28 / 44 (64 %), under the ruling's 70 %;** f34 at the line with the finer sampler. Top tones are
   79 / 17 / 3 against 60 / 35 / 5, and the top median is `#C2D80D` against `#ADC20F`. Visible: the crown is
   lighter and more uniform from above.
4. **Trunk and roots.** The trunk reads as a smooth flared bell or skirt. The roots are ridges on it, with short toes,
   not the sheet's separate snaking logs with dark crevices between them and long low runs out to the crown's width
   (`trunk_cu`, `roots_rear`, front and f34). The bell width at h .2 now matches, but the separation between the
   roots doesn't. Wood share: front T 42.7 against 37.0, rear / r34 47.9 / 48.1 against 37.2 / 36.8 (±4, out by 2–11).
   **Visible.** It still reads as a massive buttressed trunk, so it is not a misread.
5. **Side view:** canopy G 55.4 against 45.3 ± 4; T above h .45 4.0 against 13.6 (no limbs visible from the side).
   Visible: the side reads more like a mushroom than the sheet's high crown on arms. Unchanged since round 1.
6. **Ground green 1.3–3.5 against 6.1–8.3**, fill about 0.59 against 0.62–0.65. Visible: the sheet's lush moss band
   and dense small plants and rocks are sparse here. The moss pads read as flat yellow patches.
7. **Root Module parts read as tall fins** (`part_rootmodulea/b/c`), where the exploded draws low faceted logs with a
   hollow end. Visible in the part renders only.
8. **Strand crosses a LOW-L limb** (4 triangle pairs, no vert inside). Numeric only.
9. **Crown-part stub crosses 3 underside skin faces** at its entry (face centres up to 0.30 inside). Numeric only;
   it is the joint.
10. Unchanged from round 1: f34 W : H 0.914 against 1.093 (§3.2 says the sheet's f34 is drawn wider); bark v > .7 G
    low; LOW-R tines hidden; front canopy median slightly green / deep (`#82A70F`).

### What passes

- **Round-1 blocker fixed.** The crown reads as leaf clusters from all eight azimuths. Bare core is 0 and the
  edge-on cards are gone. Lobes are ≥ 70 % of the sheet in front, f34, rear and side, and ≥ 23 at every extra
  azimuth. The side is one dome, and there is no sky window through the front.
- **Technical:** budget, sizes, origins, topology, winding, self-intersections, contact, bury and UVs are all clean.
  No colour is chosen by facing.
- **Colour:** warm bark that matches the sheet's median; warm low rocks; slate slabs that match; saturated leaf greens,
  not olive.
- **Skeleton:** the low limbs read bare in the front, rear and f34; the hollow foot keeps its front slit and back arch.

### Main session ruling (2026-10-31)
Round 2 PASSED at 7/10, so the model is committed.
- **Change before the commit:** verifier minor 1 (the sprout clump read as a small spiky star) was fixed in the main session. `CLUMPS["SP"]` got `bump_k=0.45`. After the GUI rebuild, `problems` was [] and 0 shells were floating, and front34 shows a small rounded clump.
- **Recorded for polish:** minors 2–10. The main ones:
  - a faceted, serrated crown instead of rounded clover lobes;
  - a bell trunk without separate snaking roots, so front and rear wood run high;
  - a mushroom-like side view;
  - top-view lobes at 64 %;
  - sparse ground;
  - Root Module parts reading as fins.

Export: 7 assets, 5902 tris, 0 problems.
