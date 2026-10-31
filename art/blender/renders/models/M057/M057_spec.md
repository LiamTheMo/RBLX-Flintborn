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
