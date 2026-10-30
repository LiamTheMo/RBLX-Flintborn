# 049 Classic Pine — spec

Reference: `art/blender/assets/references/049.png` (1024 × 1536 px). The sheet's title is "CLASSIC PINE", subtitle
"STYLIZED LOW-POLY TREE", "PAGE 45 / 132", with "FLINTBORN / INDIVIDUAL MODEL STUDY" at the top left; the footer reads
"FLINTBORN — INDIVIDUAL MODEL STUDY". INDEX.md row 49 calls it "Classic Pine construction study".
Builder: `art/blender/kit/mcp/m049.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7). Trees: "a detailed skeleton plus foliage clumps; roots,
branches and every view matter" (memory `kit-tree-detail`). Here the skeleton is a thick planked trunk, seven buttress
roots blended into its foot, and the trunk's peg on which the canopy rings stack; the sheet draws no branches (§3.14).

**This is the fourth conifer in the kit.** 042 Young Fir (`TieredFir`, committed), 045 Pine Sapling (`PineSapling`,
being fixed) and 047 Old Pine (`GnarledPine`, being modelled) come first. **049's sheet silhouette is almost the same
as 042's** (§1.5), so this spec lists what makes 049 a different kit piece, and the verifier must check those points
(§1.5, §9).

Sheet text:
- **Hero cells:** "FRONT THREE-QUARTER (ASSEMBLED)", "REAR THREE-QUARTER (ASSEMBLED)". Both are only slightly turned
  (§3.1).
- **Orthographic cells:** "FRONT", "SIDE (RIGHT)", "REAR", "TOP". The first three are low views (e ≈ 7°); the top is a
  plan seen a little off-axis (§3.7).
- **"EXPLODED VIEW (PARTS & ASSEMBLY)":** labels "Canopy Tier 3" (the top cone), "Canopy Tier 2", "Canopy Tier 1"
  (its arrow points at the gap between the third and fourth canopy pieces), "Trunk", "Root Foot". A dashed line drops
  every canopy piece onto the trunk's peg. **Four canopy pieces are drawn under three labels** (§3.2).
- **"CANOPY LAYER (UNDERSIDE)":** a tier from below: a ring of broad blades round a bark-coloured hex **sleeve with a
  dark hole**, callout "Center Join (fits over trunk peg)".
- **"TRUNK TOP DETAIL":** the trunk's top: a thick octagonal **rim round a dished recess**, and an octagonal **peg**
  rising out of the recess, its top a lighter cut face with a dark pith dot. Callout "Trunk Peg (canopy layers stack
  and rotate)".
- **"ROOT FOOT DETAIL":** the trunk's planked foot flaring into roots; callouts "Trunk Roots (blended to base)",
  "Rocks (separate pieces)", "Ground Plants (simple leaf clusters)".
- **"MATERIAL PALETTE":** "Foliage Dark", "Foliage Mid", "Foliage Light", "Trunk Mid", "Trunk Dark", "Rock", "Ground /
  Soil", "Plant Leaves" (eight swatches, §5.1).
- **"MODEL NOTES"** (paraphrased): built from reusable parts (three canopy layers, one trunk, one root foot with rocks
  and plants); broad flat-shaded faces with clean, simple geometry; a silhouette that reads from a distance; consistent
  chunkiness with the Flintborn style; separate parts for easy variation (rotate the canopy, swap plants and rocks); no
  texture detail or noise, solid colours only (§3.12).
- **Game context and the old kit:**
  - **W04 Pines & Firs, row 1 `ClassicPine`** (`art/blender/scripts/kit/W04/classic_pine.py`, goals
    `art/blender/renders/kit/W04/classic_pine_goals.md`, manifest `art/roblox/kit/W04/manifest.json`) is the old kit's
    take on this subject, from a different reference row: about 24 tall in its goals (manifest size 12.8 × 14.5 ×
    14.8), a top tip plus three tiers of 8 drooping spade flaps, one `w04_needle` key, a fluted trunk with 5–6 buttress
    roots. `MODEL_PROGRESS.md` row 56: "3 fat tiers (ref 4); flat green, no lime tips; trunk hidden; variants
    identical"; its unmet goals R7-2 / V5-H2 (lit lime against dark teal contrast), R7-6 (crisp star from above) and
    R7-7 (exploded tiers read as steep tents, not flatter discs) apply here too. **W04 owns every `ClassicPine*` name**
    (§8).
  - Kit conifers: `TieredFir` (042, 16 tall), `PineSapling` (045, 10), `GnarledPine` (047, 20, squat); M032 / M037
    `pine` pieces.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Cell paper `#F5F0E4` (245,
240, 228), tolerance 14. Cell rules (measured grey lines): rows y 70 / 523 / 800 / 812 / 1052 (close-ups) / 1140
(palette | notes) / 1243 (close-ups) / 1483; columns x 11 / 268 / 469 (exploded | close-ups) / 511 / 755 / 802 (close-ups
| palette) / 1013.
- **Painted out (`TITLES` in `m.py`):** every cell title, the five exploded labels and the close-up callouts.
- **Masks** are `cls()` in `m.py`, the 045 / 047 classes (HSV, h in degrees; assigned in this order):
  - **X, cast shadow (not silhouette):** (s < 0.07, v ≥ 0.78) or (s < 0.08, v ≥ 0.70, B ≥ R − 3) or (h 200–245, s <
    0.14, v ≥ 0.70). The sheet draws a lavender ground shadow to the left of every side view and to the lower left of
    the top view.
  - **G, green:** h 50–180, s ≥ 0.25, v ≥ 0.10 (blades, bushes and leaf clumps; split by height, §1.2).
  - **S, sand:** h 30–52, s 0.22–0.47, v ≥ 0.80.
  - **T, trunk / bark:** h < 45, s ≥ 0.35, v ≥ 0.15.
  - **R, rock:** s < 0.30, v 0.25–0.95. (In the top cell R also takes the blue-grey shade of deep blade gaps.)
  - **O, other:** outlines, the darkest creases. Not a target.
- **Cells** (inside the rules; titles painted out): f34 (14,74,510,522); r34 (515,74,1012,522); front (14,527,267,799);
  side (272,527,510,799); rear (515,527,754,799); top (759,527,1012,799); exploded (14,845,468,1482); close-up 1, the
  underside (473,845,801,1051); close-up 2, the trunk top (473,1085,801,1242); close-up 3, the root foot
  (473,1276,801,1482).
- **Swatch inner boxes** 24 × 22 px at x 834–858, y 858 / 892 / 926 / 961 / 995 / 1030 / 1064 / 1099 (`m.SW`).

**Scratch study material** (no Blender) in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m049_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14, Pillow, numpy).
- **Helpers:** `m.py` (masks, boxes, `silhouette()`), `zoom.py` (`zoom.py x0 y0 x1 y1 scale out.png [grid]`),
  `comps.py` (connected components), `lines.py` / `lines2.py` (cell rules), `blendall.py` (name search in every
  `.blend`).
- **Measurements:** `measure2.py` (bbox, W : H, shares, profiles, fifths), `tiers.py` (hems, waists, trunk widths),
  `rows.py <view> [step]` (per-row G and T extents), `parts.py` (exploded components and profiles), `base.py` (rocks,
  plants, sand per view), `topang.py` (plan star points).
- **Colour:** `sw.py` (swatches), `samp.py` (every region per view, halves), `samp2.py` (per tier, bush vs leaf clump,
  rocks, sleeve, peg, exploded tiers, nearest-swatch splits).
- **Zooms:** `z_f34.png`, `z_f34low.png`, `z_f34base.png`, `z_r34.png`, `z_ortho.png`, `z_front.png`, `z_top.png`,
  `z_topcrown.png`, `z_expl.png`, `z_expl_t1b.png`, `z_cu.png`, `z_cu1.png`, `z_cu2.png`, `z_cu3.png`, `z_pal.png`;
  mask previews `cls_*.png`.
- **On our renders:** `measure_render.py <render.png> [paper_hex] [--flip]` (same masks). Self-test on the sheet's own
  cells (`cell_f34.png`, `cell_front.png`, paper `#F5F0E4`): f34 W : H 0.872 (no column filter), G 69.1 / T 15.5 / S
  4.4 / R 8.7; front W : H 0.846, G 72.0 / T 14.2 / S 3.2 / R 7.7. **Compare our renders with these self-test numbers,
  not with §1.2's W : H** (`measure2.py` drops columns of fewer than 6 px, which trims the soft patch edge).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a standalone tall pine with its own ground patch. Hero budget 4000 tris, each part
  under 1000. The plan in §4.3 lands at about 3100–3300.
- **Overall read (check this first).** A **tall, classic stepped pine on a thick, high, bare trunk**:
  - **Canopy:** a small pointed **five-ridge crown cone** with a hem of blades; a **middle tier (Tier 2)**; and a
    broad **lower skirt made of two stacked rings (Tier 1 upper and Tier 1 lower)**. Every ring is an **umbrella of
    long, broad, parallel-sided blades** with a shallow midrib and a **blunt, truncated chisel tip**, drooping, laid in
    two shingled rows, lapping over the ring below with a dark crease under each hem.
  - **Trunk:** a **chunky planked orange-brown trunk**, bare from the ground to about 0.29 H (z ≈ 6.8), **flaring into
    seven buttress roots that blend into its foot** and run out over a pale sand patch. Its top (hidden) is a hollow rim
    with a **peg** on which the canopy rings stack.
  - **Ground:** a pale sand patch with **chunky pale grey rocks** (two big ones at the front-left), **two faceted
    low-poly bush mounds** on the right, and **tall clusters of broad, blunt-tipped upright leaves** on the left and
    front.
  - It must read as **a crown, a middle tier and one broad double skirt on a tall bare trunk**: two clear waists, a
    sub-step inside the skirt in the three-quarter views, and a trunk that shows for nearly a third of the height.
  - Hero shares (f34): G 69.1 %, T 15.5 %, R 8.7 %, S 4.4 %.
- **Focal silhouettes, in order:**
  1. The stepped spire: apex, crown hem (0.35–0.41 of the canopy width), first waist (0.23–0.29), Tier 2 hem
     (0.66–0.70), second waist (0.44–0.49), then the skirt widening in one long slope to the Tier 1 lower hem (1.0).
  2. The ragged hem of long blunt blade tips on every ring; in the f34 and r34 the Tier 1 upper ring's tips show as a
     sub-step a little above the lower hem.
  3. The tall bare trunk and its buttress flare, warm orange lit side against dark brown shade side.
  4. The base: two big rocks front-left, the leaf clusters left and front, the bush mounds right, the sand patch.
- **Target size: 22.0 tall (apex), canopy blade tips at r 8.3 (silhouette 16.0–16.8 across), trunk Ø 3.2 at z 4–7,
  root reach r 4.5–6.5, ground patch about 18.5 × 15** (decision §8.1). Tolerances: height ±0.4, canopy silhouette W
  16.4 ± 0.6.
  - **How it was derived.** Five side views agree on the proportions (`tiers.py`, `rows.py`; fractions of the full
    silhouette height H, ground front edge to apex):

    | Feature | f34 | r34 | front | side | rear | adopted (z, studs) |
    | --- | --- | --- | --- | --- | --- | --- |
    | Crown hem h / width of canopy | .819 / .38 | .800 / .36 | .800 / .35 | .769 / .39 | .780 / .41 | z 17.2, tips r 3.1 |
    | Waist crown / Tier 2 h / width | .800 / .26 | .793 / .32 | .780 / .23 | .749 / .26 | .759 / .29 | z 16.8, visible r 2.1 |
    | Tier 2 hem h / width | .644 / .67 | .616 / .66 | .608 / .66 | .587 / .70 | .604 / .68 | z 13.1, tips r 5.6 |
    | Waist Tier 2 / Tier 1 h / width | .612 / .49 | — | .571 / .44 | — | .571 / .48 | z 12.4, visible r 3.8 |
    | Tier 1 upper sub-hem h / width | .442 / 1.0 | .449 / .87 | .46 / .81 (shoulder) | — | — | z 9.4, tips r 7.1 |
    | Tier 1 lower hem h / width | .386 / 1.0 | .367 / 1.0 | .388 / 1.0 | .356 / 1.0 | .376 / .95 | z 7.7, tips r 8.3 |
    | Lowest canopy pixel near the axis h | .314 | .302 | .290 | .283 | .290 | front tips z ≈ 6.8 (screen 5.8 − e drop) |
    | Bare trunk Ø / canopy W (under the skirt) | .22 | .18 | .20 | .18 | .20 | Ø 3.2 (0.19) |
    | Canopy W / H | .679 | .723 | .735 | .668 | .669 | 16.4 / 22 = .745 (front) |

    The front cell is near level (e ≈ 7°: the patch is 19 px deep for about 15 studs at 10.75 px/stud). Its ground
    front edge lies about 0.85 below the trunk foot, so z = 22.85 h − 0.85. All five cells agree on every hem within
    0.03–0.05 H (the side cell sits lowest).
  - **Why 22.** "Classic" makes this the kit's standard tall pine: it must stand clearly above 042 Young Fir (16) on
    an almost identical silhouette (§1.5), above 045 (10), and at least as tall as 047 Old Pine (20, but squat and 20
    wide). At 22 the sheet's chunky trunk (0.145 H) is Ø 3.2, about two characters' shoulders, and the lowest skirt tips
    hang at 6.8–7.7, **above a 5.5 character's head**: players walk under this pine's skirt, where they brush 042's.
    20 (trunk 2.9, tips 6.2–7.0) is the alternative; 24 (W04's goal) makes the base dressing chest-high boulders.
  - **Against the character (5.5):** the tree is 4.0 C tall; the trunk is a bit more than half a character wide; the
    lowest tips at 1.25–1.4 C; rocks 1.6–2.3 tall (knee to thigh); leaf clusters 1.9–4.0 (waist to shoulder); bush
    mounds 3.4–4.2 (chest). The sheet draws its base dressing large (the bushes reach 0.25 H); §8 decision 9 keeps that.
- **Build frame:** front −Y, +X right, ground z 0 = the sand patch's flat underside. Tree axis at (0, 0). Origin = bbox
  bottom centre; the patch and the bushes push it about +0.3 X of the axis (record it).

### 1.2 Measured views (`measure2.py`)

| View (box) | Silhouette bbox (px) | W : H | G | T | S | R | O |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (14,74,510,522) | 103–469 × 80–510 (367 × 431) | **0.852** | 69.1 % | 15.5 | 4.4 | 8.7 | 2.4 |
| Rear three-quarter (515,74,1012,522) | 602–930 × 80–510 (329 × 431) | 0.763 | 75.3 | 12.3 | 3.7 | 6.1 | 2.6 |
| Front (14,527,267,799) | 45–239 × 545–790 (195 × 246) | 0.793 | 72.1 | 14.2 | 3.1 | 7.7 | 2.9 |
| Side (272,527,510,799) | 309–473 × 543–790 (165 × 248) | 0.665 | 75.4 | 13.8 | 2.1 | 5.9 | 2.8 |
| Rear (515,527,754,799) | 548–722 × 545–790 (175 × 246) | 0.711 | 76.2 | 12.1 | 2.4 | 6.3 | 3.0 |
| Top (759,527,1012,799) | 795–980 × 583–751 (186 × 169) | 1.101 (W : D) | 86.3 | 0 | 0 | 11.3 | 2.4 |
| Exploded (14,845,468,1482) | parts, §1.4 | — | — | — | — | — | — |

- Shares are of the whole silhouette (O included, X excluded). **Verifier tolerance:** G ±5, T ±3, R ±3, S ±2 points;
  W : H ±0.05; positions ±0.04 of W / H unless stated. The f34 bbox is set left and right by the sand patch (x 99–473,
  21 studs on screen at 17.5 px/stud); the canopy alone is 291 px.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.1 f):

| f | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .10 | .44 | .64 | .74 | .91 | .97 | .85 | .71 | .54 | .45 | .10 |
| r34 | .38 | .50 | .65 | .80 | .90 | .98 | .86 | .69 | .50 | .41 | .09 |
| Front | .07 | .47 | .64 | .72 | .90 | 1.0 | .86 | .70 | .51 | .43 | .08 |
| Side | .37 | .45 | .63 | .68 | .84 | .98 | .92 | .80 | .65 | .45 | .36 |
| Rear | .37 | .47 | .64 | .78 | .89 | 1.0 | .88 | .71 | .62 | .45 | .07 |

**Width per height** (silhouette width at h .0 → 1.0 as a fraction of W):

```
f34    .22 1.0 .78 .19 .78 .70 .42 .48 .27 .16 .01
r34    .15 .87 .67 .60 .89 .70 .57 .43 .35 .17 .02
front  .37 .93 .69 .47 .90 .67 .62 .43 .33 .16 .02
side   .39 .72 .22 .69 .91 .64 .70 .40 .35 .17 .10
rear   .39 .89 .59 .60 .93 .70 .65 .43 .35 .17 .03
```

- h .1 is the base dressing (as wide as the canopy: the bushes and clusters spread to the patch edge); h .2–.3 the bare
  trunk (f34 .19 at h .3) or the drooping front tips; h .4–.5 the skirt; h .6 the Tier 2 hem / waist; h .7–.8 Tier 2
  and the crown hem; h .9–1.0 the crown.

**Height fifths** (bottom → top, % of each class's pixels):
- f34: G 17.6 / 12.6 / **37.7** / 23.0 / 9.1; T 47.9 / 48.4 / 3.7 / 0 / 0.
- Front: G 20.0 / 15.7 / 33.8 / 21.9 / 8.5; T 52.7 / 47.3 / 0 / 0 / 0.
- **The trunk fills the whole second fifth** (042: T in fifths 1–2 at 58 / 42 but far fewer pixels): a tall bare trunk.

**Trunk widths** (`tiers.py`, `rows.py`; px and studs at the front cell's 10.75 px/stud):

| h (front) | .29 | .25 | .20 | .15 | .12 | .10 | .07 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| front px (studs) | 37 (3.4) | 36 (3.35) | 43 (4.0) | 60 (5.6) | 75 (7.0) | 85 (7.9) | 88 (8.2, roots) |
| side px | 30 | 30 | 30 | 38 | 49 | 64 | 67 |
| rear px | 33 | 33 | 36 | 47 | 63 | 55 | 33 |

- f34 trunk: 63–65 px (3.6–3.7) from y 355 to 395, widening to 88 at y 425, 149 at y 450 (roots), the long right root
  reaching x 400 (7.1 on screen from the axis).

**Plan (top cell, `topang.py`, `z_top.png`, `z_topcrown.png`).**
- Canopy G extents 797–976 × 582–751 (179 × 169 px); centre (apex) at (888, 659); **13 star points** round the
  outline, r 76–79 px to the upper right and 93–100 px to the lower left (the cell is a little oblique, §3.7).
- In the middle a **five-ridge crown star** (ridges N, E, SE, S, W in the cell; one points toward the front), bright
  lime, the ridges' halves split lit / shaded.
- **Rocks peek beyond the canopy**: a cluster at the upper left (dx −45 … −90, dy up to −54 px: world −X, +Y) and one
  at the right (dx +70 … +95: world +X, slightly +Y). Top shares G 86.3, R 11.3 (part of R is blue-grey shade in deep
  blade gaps).

### 1.3 Silhouette and composition per view

**Front three-quarter (`z_f34.png`, `z_f34low.png`, `z_f34base.png`) — governs.** A slightly turned, slightly elevated
view (az ≈ −15, e ≈ 12°, §3.1); 17.5 px/stud from the canopy width.
- **Crown** (apex x 276, y 80): a straight-sided pointed cone, each ridge a lit right and a shaded left facet; hem
  blades with tips at y 155–165 (x 219–331), a dark crease under the hem.
- **Tier 2** (y 165–245): two staggered rows of long blades; side tips at x 172 (y 240) and 376 (y 230).
- **Skirt** (y 245–375): **Tier 1 upper** blades with tips at y 290–320 (left x 154, right x 432), lapped over **Tier 1
  lower** blades with tips at y 340–350 (left x 126, right x 416); the front-facing blades hang lowest (y 365–375).
- **Blades** (`z_f34low.png`): long boards with **near-parallel sides**, 30–40 px wide (1.7–2.3 studs) and 90–100 px
  long on screen (about 5.4 visible, the roots hidden under the row above), a shallow central ridge (two top facets),
  a visible dark edge thickness, and a **truncated chisel tip** (two short bevels and a flat end about 0.35 of the
  width). Not kites (no widest point near the root), not paddles (not broad and short), not needles.
- **Trunk** (from y 325 under the skirt to the ground): Ø 63–65 px (3.6) from y 355 to 395, flaring below y 420.
  Bark: broad vertical planks with a few grooves; lit right side orange (`#C5712A` median), left in dark brown shade
  (`#613C21`).
- **Roots:** five visible: left (to x 205, y 470), front-left (x 230, y 490), front (under R2), front-right (x 345,
  y 495), a long right root (to x 400, y 478). They rise high on the trunk (to y 420–430, z ≈ 3.5–4.5) as broad
  buttress ribs and taper to blunt tips on the sand ("blended to base").
- **Base dressing:** rock **R1** front-left (x 145–210, top y 440), rock **R2** at the front (x 255–320, top y 455),
  a tall leaf cluster **C1** behind R1 (x 150–215, top y 401) with a lower cluster **C2** to its left (x 124–150),
  small clusters **C3** between the rocks (x 202–241) and **C4** in front right (x 318–351), two **faceted bush mounds**
  at the right, **BA** (x 330–395, top y 391) and **BB** (x 385–450, top y 415), a small sprig at x 244–263. The sand
  patch spans x 99–473 (the widest thing in the cell) with a soft edge.

**Rear three-quarter (`z_r34.png`).** The same tree, **lit from the right again**, and with **the same base layout as
the f34** (rocks at the left, bush mounds at the right), so it does not invert onto the f34 (§3.1). Tier hems .800 /
.616 / .449 / .367, the Tier 1 sub-step clearer than in the f34 (.87 against 1.0).

**Front, side and rear cells (`z_ortho.png`, `z_front.png`).** Low views (e ≈ 7°) at one scale (H 245–248 px); the hems
sit within 0.03–0.05 H of each other. Each tier shows one blade or ridge on the axis.
- **Front:** clusters left (x 55–109), R1 (x 68–99), R2 just left of the axis (x 125–163), the bush pair right (x
  164–235, top h .249), sprigs.
- **Side:** small clusters both sides and one small rock in front of the trunk; no bush.
- **Rear:** a rock left of the axis (x 584–621), clusters left, bushes right (x 659–716).
- Judge the dressing per view for content (§3.5).

**Top (`z_top.png`, `z_topcrown.png`).** §1.2. Blades read as long pointed boards with a central ridge, the second
row's tips between the first row's, five crown ridges in the middle.

**Canopy layer underside (`z_cu1.png`).** A ring seen from below (e ≈ −40°): about **10 broad blades** radiating round
(9 peaks found, one merged), each with a blunt tip; the upper ring's lime blades show past the rim. At the centre a
**hexagonal / octagonal bark sleeve** (x 578–635, 0.22 of the ring's width) with a **dark hole** about 0.5 of its
diameter (`#724525` sleeve in shade, hole near-black brown).

**Trunk top detail (`z_cu2.png`).** An octagonal trunk top: a **thick flat rim** (wall about 0.15 of the diameter)
round a **dished recess**, an **octagonal peg** (Ø ≈ 0.31 of the trunk top) rising from the recess floor about 0.6 of
the trunk top's Ø above the rim, leaning a few degrees, its top a flat lighter cut face (`#E59548`) with a small dark
pith dot. Planked sides below.

**Root foot detail (`z_cu3.png`).** The trunk's broad planks run down into **roots that are part of the trunk** (no
seam): buttress ribs leaving the trunk high and tapering out to the sand. A big pale grey chunky rock in front, a small
rock right, leaf clusters of **5–8 upright broad leaves with blunt-oval tips** (lime outside, green inside), the sand
patch with a soft edge.

### 1.4 Parts (Exploded View, `z_expl.png`, `z_expl_t1b.png`, `parts.py`)

The exploded is an elevated view from the front (e ≈ 20–25°). **The hero governs every size**; the parts give shapes,
counts and order.

| Part | Box (px) | Size px | Screen W : H | Notes |
| --- | --- | --- | --- | --- |
| Canopy Tier 3 | (169,851,253,924) | 85 × 74 | 1.15 | a pointed ridged cone, hem of about 8 visible blade tips, widest at the hem |
| Canopy Tier 2 | (128,925,289,1004) | 162 × 80 | 2.02 | an umbrella of blades from a central peak, tips drooping; 0.55 of Tier 1 lower |
| Canopy Tier 1 (upper piece) | (76,1006,329,1104) | 254 × 99 | 2.57 | the same build, 0.86 of the lower piece; 7–8 visible tips in two rows |
| Canopy Tier 1 (lower piece) | (65,1096,358,1218) | 294 × 123 | 2.39 | the widest; blades from a low central peak, two rows of tips; visible edge thickness |
| Trunk | (44,1226,372,1467) with the root foot | top Ø 52 px; peg 16 × 20 px | — | octagonal planked trunk, Ø 52–54 to y 1295, 61–67 at y 1303–1335, flaring from y 1340; **7 roots** spanning 228 px (4.4 × the top Ø); a short peg (Ø 0.31, height 0.38 of the top Ø); a dark knot slit at mid-height |
| Root Foot | (base of the same box) | — | — | **4 rocks** (two big at front-left, one at the right, small ones), **6 upright leaf clusters**, small sprigs; sand under each; **no bush mound drawn** (§3.9) |

- Canopy pieces as fractions of the lower piece: Tier 3 0.29, Tier 2 0.55, Tier 1 upper 0.86, Tier 1 lower 1.0 (the
  hero: 0.37, 0.67, 0.86, 1.0; §3.3).
- Green split by nearest swatch (dark / mid / light): T3 41 / 21 / 37 %, T2 46 / 21 / 33, T1 upper 44 / 25 / 31, T1
  lower 46 / 20 / 34. Exploded greens median `#4A8131`, lit (v > .7) `#A9C934`; peg `#9F572F`.

#### Canopy Tier 3 (crown) — exploded, hero, top
- **Shape:** a straight-sided **five-ridge star cone** (ridges at 270 + k·72°, one aimed at −Y), each ridge two broad
  facets; a **hem of 10 blades** emerging under the cone's rim (5 long under the ridges, 5 short between), tips
  drooping; a hex sleeve with a blind hole underneath.
- **Hero size:** apex 22.0; cone rim r 2.0 at z 18.6; long hem tips r 3.1 at z 17.2, short r 2.7 at z 17.5; sleeve
  bottom z 18.215. Part about 6.2 × 6.2 × 5.0 (W : H 1.24; exploded 1.15).

#### Canopy Tier 2 — exploded, hero
- **Shape:** a pleated core cone with a small cap and top peg, **16 blades in two rows of 8** (outer long, inner short,
  offset half a step), tips drooping; a hex sleeve under the core.
- **Hero size:** cap r 0.8 at z 18.2; outer tips r 5.6 at z 13.1 (front droop to 12.8); inner tips r 3.6 at z 15.0;
  sleeve bottom z 15.015. Part about 11.2 × 11.2 × 5.9 (W : H 1.9; exploded 2.02).

#### Canopy Tier 1 upper — exploded, hero
- **Shape:** as Tier 2, **18 blades in two rows of 9**.
- **Hero size:** cap r 0.85 at z 15.0; outer tips r 7.1 at z 9.4; inner tips r 4.4 at z 12.0; sleeve bottom z 14.515.
  Part about 14.2 × 14.2 × 6.3 (W : H 2.25; exploded 2.57).

#### Canopy Tier 1 lower — exploded, close-up 1, hero
- **Shape:** as Tier 2, the widest, **22 blades in two rows of 11**, the longest blades of the tree, tips drooping
  clearly below the notches.
- **Hero size:** cap r 0.9 at z 14.5; core rim r 3.4 at z 12.2; outer tips r 8.3 at z 7.7 (front-facing tips to 7.0);
  inner tips r 5.2 at z 10.9; sleeve bottom z 11.015, sleeve 1.3 tall, outer Ø 2.4, hole Ø 1.0. Part about 16.6 ×
  16.6 × 7.0 (W : H 2.4; exploded 2.39).

#### Trunk — exploded, close-ups 2 and 3, hero
- **Shape:** an **octagonal planked trunk** (each side split once: 16 slightly irregular plank facets, a few grooves,
  one dark knot slit), tapering gently to z 11.0, **seven buttress roots built into the trunk's foot** (no visible seam:
  their ribs rise out of plank pairs), a **thick rim with a dished recess** on top, and an **octagonal peg** rising out
  of the recess.
- **Hero size:** Ø 3.2 at z 4–7, 2.9 at z 9, 2.7 at the rim (z 11.0); flare from z 4.0 to 8 across the roots at the
  ground; roots reach r 4.5–6.5; recess Ø 1.9, 0.35 deep; peg Ø 0.85, top z 12.2. Part about 12.5 × 11 × 12.2.

#### Root Foot — exploded, close-up 3, hero
- **Shape:** a thin irregular sand patch, 5 chunky faceted rocks (two big), 3 pebbles, 2 faceted bush mounds, 6
  upright broad-leaf clusters, 2 sprigs.
- **Hero size:** §2.4.

### 1.5 How 049 differs from 042, 045 and 047 (binding: the verifier checks these)

The 049 and 042 sheets have nearly the same front silhouette:

| | Canopy W / H | Hems h (crown / mid / lower) | Hem widths | Lowest canopy h | Trunk Ø / canopy | f34 G / T |
| --- | --- | --- | --- | --- | --- | --- |
| 049 front | .735 | .80 / .61 / .39 | .35 / .66 / 1.0 | .29 | .20 | 69.1 / 15.5 |
| 042 front | .696 | .73 / .57 / .34 | .50 / .73 / 1.0 | .26 | .20 | 72.5 / 12.8 |

So the difference has to come from the following. The verifier renders 042, 045, 047 and 049 at their f34 cameras side
by side and checks each row:

| | 042 Young Fir (`TieredFir`) | 045 Pine Sapling (`PineSapling`) | 047 Old Pine (`GnarledPine`) | **049 Classic Pine** |
| --- | --- | --- | --- | --- |
| Size | 16 tall, canopy 12, trunk Ø 2.0 | 10, canopy 7, Ø 1.25 | 20, canopy 20.3 × 12, Ø 6.2 | **22 tall, canopy 16.4, trunk Ø 3.2** |
| Lowest skirt tips | z 4.5–5.0 (head height) | 2.5–2.7 (hip) | pads at 7.7–9 | **z 6.8–7.7: walk under the skirt** |
| Silhouette | three tiers, crown hem .50 wide | three tiers | squat, five pads, W : H ≈ 1 | **small crown (hem .35–.41 wide, at h .79); Tier 2; one long double skirt with a sub-step in the f34 / r34** |
| Canopy pieces | 3 tiers (8 / 12 / 16 kites) | 3 tiers (12 / 14 / 14 plates) | 5 pads | **4 rings: crown 10 + Tier 2 16 + Tier 1 upper 18 + Tier 1 lower 22 blades** |
| Foliage element | thin kite, widest at 0.42 L, pointed, L : W ≈ 2.2 | thick paddle slab, L : W ≈ 1.5 | lobe mounds | **long parallel-sided blade, L : W 2.6–3.0 (visible ≈ 2.5), shallow ridge, edge thickness ≈ 0.12 W, truncated chisel tip** |
| Crown from above | 4 + 4 ridge star | 4-ridge star | rosettes round a limb star | **5-ridge star** |
| Joint | flat cap + octagonal hub | peg + square recess | hexagonal limb sockets | **hollow trunk rim + peg; every ring a bark hex sleeve over a peg; rings "stack and rotate"** |
| Trunk | octagonal planked, 3 slits, 6 separate kinked roots r 2.8–4.2, bare to .26 H | smooth stump, 6 short flares | massive, leaning, forked | **thick (0.145 H) planked, bare to .29 H, 7 buttress roots blended into the foot (ribs rising to z 3.5–4.5), reach r 4.5–6.5** |
| f34 bark share | T 12.8 % | T 10.8 % | T 37.6 % | **T 15.5 %** |
| Ground plants | lanceolate clumps | broad-oval rosettes | dark broad-leaf bush + lime tufts | **two faceted low-poly bush mounds (right) + tall upright broad-leaf clusters (left, front)** |
| Rocks | 5 warm beige + 3 pebbles | 4 pale neutral grey | 6 warm light grey | **5 chunky pale warm grey, two big (2.2–2.3 tall) at the front-left, rocks peeking past the skirt from above** |

Also not W04's `ClassicPine` (one-key flat green canopy, top tip + three tiers of 8 spades, trunk hidden).

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, tree axis at (0, 0)). Plan azimuths: 0 = +X, counter-clockwise,
front −Y = 270°.

### 2.1 Stack (binding contact chain, bottom up; every seat gap is VEG_GAP = 0.015)

| Piece | Bottom z | Top z | Sits on | Notes |
| --- | --- | --- | --- | --- |
| Sand patch | 0 | 0.15 crest, bevel to the edge | ground | flat underside |
| Trunk + roots + rim + peg (one closed shell) | 0.05 (sunk 0.10 into the patch) | rim 11.0, peg top 12.2 | patch | root tips sunk 0.05 into the patch top; recess floor 10.65 |
| Tier 1 lower: core + sleeve (one closed shell) | **11.015** (sleeve's flat bottom on the rim) | cap 14.5, top peg to 15.1 | trunk rim | sleeve hole (blind) swallows the trunk peg with 0.05 radial clearance and 0.1 head room |
| Tier 1 lower blades ×22 | — | — | the core (outer row) and the outer row (inner row) | §6 |
| Tier 1 upper: core + sleeve | **14.515** | cap 15.0, peg to 15.6 | Tier 1 lower cap | its underside clears Tier 1 lower's inner blades by 0.02–0.1 (ray-cast) |
| Tier 1 upper blades ×18 | — | — | its core / its outer row / Tier 1 lower's blades | outer tips rest on Tier 1 lower's blades |
| Tier 2: core + sleeve | **15.015** | cap 18.2, peg to 18.8 | Tier 1 upper cap | |
| Tier 2 blades ×16 | — | — | its core / its outer row | |
| Tier 3: star cone + sleeve | **18.215** | apex 22.0 | Tier 2 cap | |
| Tier 3 hem blades ×10 | — | — | the cone (roots buried under its rim) | |
| Rocks, pebbles | sunk 0.08 / 0.04 | §2.4 | patch | |
| Bush mounds | base lobes sunk 0.05 | §2.4 | patch | each lobe touches a neighbour or the patch |
| Leaf-cluster hubs | sunk 0.03 | | patch | leaves chain to their hub |

- **Tiers 1 lower and upper nest like stacked umbrellas:** both cones slope about 42°, their surfaces 0.5–0.7 apart,
  and the upper ring's outer blades lie **on** the lower ring's blades (seated by ray cast, gap 0.015), as 042 seats
  row B on row A. Its outer tips end 1.3–1.7 above the lower ring's tips and 1.2 further in: the sub-step.
- **Waists:** the crown hem hangs 0.4 above Tier 2's surface at r 2.1 (z 16.8); the Tier 2 hem hangs about 2.3 above
  Tier 1 upper's surface at r 5.6 (z 10.8), leaving the second waist at r ≈ 3.8, z 12.4, with a dark crease band
  (geometry, not paint).
- **No coincident faces:** each sleeve bottom 0.015 above its seat; read every gap back through the MCP (BVH nearest
  distance per shell).

### 2.2 Rings (plan radii r; z heights)

| Ring | Core: cap r @ z → rim r @ z | Outer row (count, azimuths, root r @ z → tip r @ z, length, width) | Inner row | Sleeve (outer Ø × height, hole Ø × depth) |
| --- | --- | --- | --- | --- |
| Tier 3 crown | star cone apex 22.0 → ridges r 2.0 @ 18.6 (5 ridges at 270 + k·72°; valleys r 1.45) | **10 hem blades**: 5 long at the ridges, root r 0.9 @ 19.0 → tip r 3.1 @ 17.2, L 2.9, W 1.25; 5 short between, tip r 2.7 @ 17.5, L 2.4, W 1.1 | — | 1.6 × 0.4; hole 0.9 × 0.7 |
| Tier 2 | cap r 0.8 @ 18.2 → rim r 2.2 @ 16.7 | **8** at 270 + k·45°; root r 1.6 @ 16.9 → tip r 5.6 @ 13.1 (front droop 12.8); L 5.6, W 1.9 | **8** at 292.5 + k·45°; root r 0.7 @ 18.2 → tip r 3.6 @ 15.0; L 4.4, W 1.6 | 1.8 × 0.7; hole 1.0 × 0.7 |
| Tier 1 upper | cap r 0.85 @ 15.0 → rim r 2.6 @ 13.4 | **9** at 270 + k·40°; root r 2.0 @ 13.6 → tip r 7.1 @ 9.4; L 6.6, W 2.2 | **9** at 290 + k·40°; root r 0.7 @ 15.0 → tip r 4.4 @ 12.0; L 4.8, W 1.9 | 2.0 × 0.5; hole 1.0 × 0.7 |
| Tier 1 lower | cap r 0.9 @ 14.5 → rim r 3.4 @ 12.2 | **11** at 270 + k·32.7°; root r 2.8 @ 12.6 → tip r 8.3 @ 7.7 (front droop 7.0); L 7.2, W 2.5 | **11** at 286.4 + k·32.7°; root r 0.8 @ 14.5 → tip r 5.2 @ 10.9; L 5.6, W 2.1 | 2.4 × 1.3; hole 1.0 × 1.3 |

- **One outer blade aimed straight at the front (270°) on every ring** and one crown ridge at 270°, as in the front
  cell. Rotating rings (the sheet's variation note) is a later variant, not the hero.
- **Jitter, not a pattern:** tip radius ±5 %, tip height ±0.15, azimuth ±4°, width ±8 %, roll ±4°; never two
  neighbours equal.
- **Inner rows are visible:** their tips land at 0.6–0.65 of the outer row's radius, on top of the outer blades, so each
  ring shows two rows of tips (045's blocker was an inner row tucked under the outer one). The f34 must show tips at
  three heights in the skirt (inner rows and the Tier 1 upper sub-hem) above the Tier 1 lower hem.

### 2.3 Blade and core shapes

- **Blade (closed shell, 18 tris):** a root vertex (buried in the core); section A at 0.30 L (left edge, **ridge** 0.08
  W above the edges, right edge, **keel** 0.12 W below the centre: the edge thickness the sheet draws); section B at
  0.80 L, **the same width as A** (parallel sides; ridge and keel 0.8×), bent down a further 10–14° (the droop); a
  **truncated tip**: two tip vertices 0.35 W apart at L, on the mid-plane. Faces: root fan 4, band A→B 8, tip 6 (top 3,
  bottom 3). In plan the blade is a **long board with a short bevelled point**: not a kite, not a needle, not a
  paddle. Its two top facets are the sheet's lit / shaded halves.
- **Pitch:** outer rows start 36–40° below horizontal at the root and droop to 46–50° at the tip; inner rows 32–36°.
  The crown hem 38°.
- **Core (one closed shell with its sleeve):** a pleated cone frustum (corners at the outer-row azimuths pushed out
  0.12, between them pulled in 0.12), a small flat cap carrying a **short octagonal top peg** (Ø 0.85, 0.6 tall: the
  next ring's sleeve swallows it), an underside sloping in from the rim to the **hex sleeve** (flat bottom face with a
  **blind hole**, §3.6). Under 90 tris with sleeve and peg.
- **Crown core:** the five-ridge star cone (10 facets above the hem) from the apex to its rim at z 18.6, an underside
  from the rim down to the sleeve; the hem blades tuck under the rim.

### 2.4 Trunk, roots, base

Plan positions are the f34 (az −15) and front cell together; the r34, rear and side cells are judged for content
(§3.5).

| Piece | Position (X, Y) / azimuth | Size | Notes / evidence |
| --- | --- | --- | --- |
| Trunk body | axis (0, 0) | octagon, a face toward −Y; corner radii 3.0 @ 0.05 (between roots), 2.4 @ 1.0, 2.0 @ 2.0, 1.78 @ 3.2, 1.66 @ 4.5, 1.62 @ 6.0, 1.55 @ 7.5, 1.47 @ 9.0, 1.40 @ 11.0 | front Ø 3.35 at z 4.9, 4.0 at 3.7; f34 3.6 |
| Planks | | each side split once (16 facets), split pushed ±0.06–0.10; 3 shallow vertical grooves; 1 dark knot slit front-right at z 5.5–6.4 | close-ups, exploded |
| Rim + recess | top z 11.0 | flat octagonal rim, recess Ø 1.9 (inset 0.4), 0.35 deep, its floor flat | trunk-top detail |
| Peg | recess floor → z 12.2 | octagon Ø 0.85, leaning 4° toward +X, flat cut top (bark-light) with a 0.15 pith recess | trunk-top detail; exploded |
| Root RF (front) | 275°, reach r 5.0 | 1.6 wide × 2.6 tall at the trunk, rib rising to z 4.0, 3 segments | f34 under R2; front cell |
| Root RR (right, long) | 345°, r 6.5 | 1.7 × 2.8, rib to z 4.4, 3 segments, one kink | f34 long right root (x 400) |
| Root RFR (front-right) | 310°, r 5.2 | 1.5 × 2.4, rib to 3.8 | f34 x 345 |
| Root RFL (front-left) | 235°, r 4.6 | 1.4 × 2.2, rib to 3.6 | f34 x 230 |
| Root RL (left) | 190°, r 4.8 | 1.5 × 2.4, rib to 3.8 | f34 x 205 |
| Root RB1 / RB2 (back) | 70°, r 4.5; 125°, r 5.0 | 1.4 × 2.2 | exploded back roots; r34 |
| Roots, all | 4–5-sided section, a top rib that becomes a trunk plank ridge, flattened on the sand, blunt tip sunk 0.05 | | "blended to base"; no seam |
| Sand patch | lobed outline, 16 points, r 7.0–9.6, longest toward 0° / 180° | about 18.5 × 15, crest 0.15, bevel 0.6 wide to the edge | f34 21 on screen, front 18.2, r34 17.8 |
| Rock R1 | (−5.6, −1.2) | 3.2 × 2.6 × 2.2 tall | f34 x 145–210, front x 68–99; top-view left rock |
| Rock R2 | (−0.9, −4.9) | 3.4 × 2.8 × 2.3 | f34 x 255–320, front x 125–163; root-foot close-up's big rock |
| Rock R3 | (3.2, 4.4) | 2.4 × 2.0 × 1.6 | rear cell rock (x 584–621), r34 back rocks |
| Rock R4 | (7.6, 2.6) | 2.0 × 1.7 × 1.4 | top-view right rock beyond the skirt; exploded right rock |
| Rock R5 | (−6.6, 2.8) | 1.4 × 1.2 × 0.9 | top-view upper-left cluster; exploded small rocks |
| Pebbles ×3 | (−3.3, −5.6), (2.0, −5.8), (−7.6, 0.6) | 0.4–0.6 | exploded, root-foot close-up |
| Bush BA | (4.6, −1.4) | Ø 3.8 × 3.4, 4.2 tall, 6 lobes | f34 x 330–395 top y 391; front bush x 164–200 |
| Bush BB | (7.0, 0.4) | Ø 3.4 × 3.0, 3.4 tall, 5 lobes | f34 x 385–450; front x 200–235 |
| Cluster C1 | (−4.4, 0.8) | Ø 2.6, 4.0 tall, 8 leaves | f34 tall cluster behind R1 (top y 401) |
| Cluster C2 | (−7.2, −1.6) | Ø 2.0, 2.8 tall, 6 leaves | f34 x 124–150; front x 55–80 |
| Cluster C3 | (−3.0, −3.9) | Ø 1.6, 2.2 tall, 6 leaves | f34 between the rocks (x 202–241) |
| Cluster C4 | (2.0, −4.6) | Ø 1.6, 1.9 tall, 6 leaves | f34 x 318–351, front x 162–175 |
| Cluster C5 | (−1.6, 5.4) | Ø 2.0, 2.6 tall, 6 leaves | rear / r34 clusters |
| Cluster C6 | (5.4, 4.8) | Ø 1.8, 2.2 tall, 6 leaves | r34, exploded back-right |
| Sprigs S1, S2 | (0.6, −6.0), (−5.2, −4.6) | Ø 0.9, 1.2 tall, 4 leaves | f34 sprig x 244–263; front sprigs |

- **Keep clear:** no rock, bush or cluster within 0.1 of a root rib or the trunk (contact allowed, overlap ≤ 0.05);
  nothing under the skirt higher than 4.4 (BA's top stays below the Tier 1 lower tips at r 4.6: z ≈ 9.5).
- **Spacing:** the dressing stays inside the patch outline by ≥ 0.3.

### 2.5 Expected extents and screen checks

- **Extents (build frame):** X about −9.3 … +9.6; Y about −7.6 … +7.4; Z 0 … 22.0. Bbox about 18.9 × 15.0 × 22.0
  (the patch is the widest thing; the canopy's tips reach r 8.3 ± 0.4).
- **Checks on the renders** (floor hidden, `measure_render.py`, compared with the self-test numbers):
  - **f34_sheet (−15, 12)** (probe az −5 / −15 / −25 × e 8 / 12 / 16, keep the best): W : H 0.82–0.92 (self-test
    0.872); canopy W / H 0.64–0.72 (0.679); shares G 69.1 ± 4, **T 15.5 ± 3**, R 8.7 ± 3, S 4.4 ± 2; top profile within
    ±0.07 for f .1–.9; width per height within ±0.08 at h .2–.9; hems at h .82 / .64 / .44 / .39 ± .03 with widths .38
    / .67 / ≥ .95 / 1.0 ± .05; waists h .80 / .61 ± .03 at widths .26 / .49 ± .06; lowest canopy at h .31 ± .03; T
    fifths within ±8 (T in fifth 2 ≥ 40 %); R1 / R2 / BA / C1 at their §1.3 x ranges ± .05 W.
  - **front_sheet (0, 7), side_sheet (90, 7), rear_sheet (180, 7):** hems h .80 / .61 / .39 ± .03 (side ±.04), widths
    .35 / .66 / 1.0 ± .05; waists .78 / .57 at .23–.29 / .44–.48 ± .06; lowest canopy h .29 ± .03; bare trunk Ø
    0.18–0.21 of the canopy W; canopy W / H 0.66–0.75; shares loosely (G ±6, T 12–15 ± 3); dressing for content.
  - **r34_sheet (165, 12):** loosely: W : H 0.72–0.82, hems .80 / .62 / .45 / .37 ± .04 (the Tier 1 sub-step at .87 ±
    .06 of the width), G 75.3 ± 6.
  - **top (0, 89):** W : D 0.95–1.10; ≥ 11 outer star points, a 5-ridge crown star; rocks R1 / R4 / R5 peeking past the
    skirt (R ≥ 3 %); no bark or sand visible beyond a sliver (T ≤ 1 %, S ≤ 3 %).

## 3. View conflicts and resolutions

### 3.1 The "three-quarter" cells are barely turned, and the rear one repeats the front's base

- **Evidence.** The f34 base matches the front cell's (clusters and R1 left, R2 near the axis, bushes right), only
  shifted: f34 az about −10 … −20. The r34 shows the same layout (rocks left, bushes right) and the same lit-right
  light, so it can't be the f34 seen from behind. The rear ortho cell does the same (rock left of the axis, bushes
  right). The canopy is near-symmetric, so only the base reveals the turn.
- **Resolution (decision §8.10).** `f34_sheet (−15, 12)` governs (probe az ±10, e ±4); the plan (§2.4) is the f34 and
  front together. `r34_sheet (165, 12)` and `rear_sheet` are judged for the canopy numbers and for content in the base
  (rocks and clusters on one side, bushes on the other). Elevation: the f34 patch (49 px deep at 17.5 px/stud for
  about 15 studs) and the front-tip drop give e ≈ 11–12°; the ortho cells e ≈ 7°.

### 3.2 Four canopy pieces under three labels ("three canopy layers")

- **Evidence.** The exploded draws four canopy pieces (widths 85 / 162 / 254 / 294 px); the labels are Tier 3, Tier 2
  and Tier 1, the Tier 1 arrow pointing at the gap between the third and fourth pieces; the notes say "three canopy
  layers". The assembled f34 and r34 show four hem levels (h .82 / .64 / .44 / .39 and .80 / .62 / .45 / .37), the
  lowest two with no waist between them; the front cell shows the skirt as one long slope with a shoulder at h .46.
- **Resolution.** **Tier 1 is a double ring**: Tier 1 upper (0.86) nested on Tier 1 lower (1.0), the pair reading as
  one skirt with a sub-step. Four ring pieces in the hero; parts per decision §8.5.

### 3.3 Exploded scale vs the hero

- **Evidence.** Fractions of the lower ring: exploded Tier 3 0.29 / Tier 2 0.55 / Tier 1 upper 0.86; hero crown hem
  0.35–0.41 / Tier 2 0.66–0.70 / upper sub-hem 0.81–0.87. Exploded trunk top Ø 0.18 of the lower ring (hero 2.7 / 16.6
  = 0.16 at the rim).
- **Resolution.** The hero governs every size; the parts are the hero's pieces built by the same functions, so the
  parts shot shows a bigger crown and Tier 2 than the exploded. Record it.

### 3.4 Peg height: exploded vs the trunk-top close-up

- **Evidence.** Exploded peg 0.38 of the trunk top's Ø above the rim; the close-up's about 0.6.
- **Resolution.** Peg top 1.2 above the rim (0.44 Ø), from the recess floor 0.35 below the rim (1.55 long); the
  ring's sleeve hole swallows it. Hidden in the hero; it shows on the Trunk part and in `trunk_cu`.

### 3.5 Base dressing between views

- **Resolution.** The f34 + front plan governs (5 rocks, 2 bushes, 6 clusters, 2 sprigs, 3 pebbles); the side, rear,
  r34 and exploded are judged for content only: rocks and clusters on the left, bush mounds on the right, a pale sand
  patch, rocks peeking past the skirt from above.

### 3.6 The sleeve's hole: through-hole vs blind

- **Evidence.** The underside close-up draws a dark hole in the sleeve; "fits over trunk peg".
- **Resolution.** A **blind hole** (Ø 1.0, deep enough for the peg plus 0.1), painted bark-deep inside, so every ring
  core stays one closed genus-0 shell. From below it reads the same as the close-up. Alternative: a true through-hole
  (genus-1 shell; no visual gain, harder to keep clean).

### 3.7 The top cell is a little oblique

- **Evidence.** The outline reaches r 93–100 px to the lower left and 76–79 to the upper right of the crown apex; the
  shadow falls lower-left.
- **Resolution.** Build the plan round; judge the top render on point count (≥ 11), the 5-ridge crown star and the
  rocks peeking out, not on the outline's offset.

### 3.8 Trunk diameter between views

- **Evidence.** Bare trunk Ø / canopy: f34 .22, front .20, rear .20, side and r34 .18.
- **Resolution.** Ø 3.2 at z 4–7 (0.195 of 16.4). The f34 trunk will read about 10 % thinner than drawn: record it.

### 3.9 Bush mounds in the hero but not in the parts

- **Evidence.** The f34, r34, front and rear draw two faceted bush mounds at the right; the exploded root foot and the
  root-foot close-up draw only upright leaf clusters.
- **Resolution.** The hero governs: build both mounds into the root foot. They are 049's own dressing (none of
  042 / 045 / 047 has faceted bush mounds).

### 3.10 The rock swatch leans pink

- **Evidence.** Swatch `#B8ACA4` (24°, sat .11; R − G 12, G − B 8). The rendered lit rock is warmer and yellower,
  `#DCCBB6` (34°) in the f34 and `#DDC9B7` in the close-up; the shade is a near-neutral blue-grey `#69686A`.
- **Resolution.** Calibrate to the lit render, hue 30–38°, **R > G > B with G − B ≥ 12** (not mauve).

### 3.11 The "Foliage Light" swatch is yellow, the rendered lit canopy is lime

- **Evidence.** Swatch `#B3A733` (54°); f34 lit canopy (v > .7) `#B0CD34` (73°), lit half `#A3C531` (74°).
- **Resolution.** Calibrate the light key to the rendered lit canopy, not the swatch.

### 3.12 "No texture detail or noise, solid colours only" vs the user's blended-colour rule

- The user's rule wins, quietly: broad position-based blends (a lighter crown and Tier 2, a deeper lower skirt, deeper
  blade roots and cores), whole-facet Tint mottling at a low amplitude, never per-triangle confetti.

### 3.13 Lit right, dark left in every view

- **Evidence.** f34 canopy left half `#1C6834` (139°), right half `#A3C531` (74°); the r34 (from behind) is lit from
  the right too, and so is every ortho cell. The trunk splits the same way.
- **Resolution.** It is the light. **Never colour by facing.** Positional signals that remain (§5.2): the crown and
  Tier 2 are lighter (medians v .58–.60) than the lower skirt (.47), which is the most "dark"-swatch (50 % nearest).

### 3.14 Branches

- **Evidence.** None drawn anywhere: the rings stack on sleeves and pegs.
- **Resolution.** **No branches.** The user's tree rule is served by the thick planked trunk with its knot and grooves,
  the seven buttress roots blended into the foot, the hollow rim and the peg (checked in `trunk_cu`, `root_cu`, front,
  side, rear and underside). Record "no branches: none on the sheet".

### 3.15 Cast shadow

- The sheet draws a lavender ground shadow to the left; the masks exclude it (X). Render every `*_sheet` view with the
  studio floor hidden, so our floor shadow isn't classed as rock.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its exploded cell

1. `blade(root, tip, width, pitch, droop, roll)` → one 18-tri closed shell (§2.3). Every blade in the model comes from
   it. Check a single blade render (`blade_cu`): parallel sides, a truncated chisel tip, a visible edge.
2. `ring(kind)` with `kind` in `"t1_lower" | "t1_upper" | "t2"` → one closed **core + sleeve + top-peg shell** plus its
   blade shells (outer row, then the inner row seated on it), all in one object. `crown()` → the star cone + sleeve
   shell and its 10 hem blades. Compare each with its exploded cell (screen W : H ±0.2, visible tip count) and
   `ring_under` (the Tier 1 lower part from below, e −40) with close-up 1: about 11 blades round a hex bark sleeve with
   a dark hole.
3. `trunk()` → the octagonal planked body, grooves, knot slit, the rim and recess, the peg, and seven buttress roots
   (`root(azimuth, reach, w, h, rib_top, segments)`). **One closed shell.** Recommended: build body and roots as one
   explicit mesh, each root's top rib rising out of a plank-split vertex column so the root is part of the trunk ("blended
   to base", no seam). Fallback: union each root at the origin one at a time (`m033._union_fine`, merge 0), save between
   unions, collapse corners under 3° afterwards (042 finding 1). Compare with the exploded trunk and `trunk_cu (−30,
   30)` / `root_cu (−20, 12)`.
4. `root_foot()` → `patch()`, `rock(spec)` ×5 (explicit ring stacks: a broad base, a widest ring at 0.3 h, a shoulder
   at 0.7 h, a flat 4–6-corner crown, 10–16 broad facets; no `K.hull_rock` jitter balls), `pebble()` ×3,
   `bush(spec)` ×2 (5–6 faceted lobes each: §4.1a), `cluster(spec)` ×6 and `sprig(spec)` ×2 (each leaf a closed 8-tri
   folded broad leaf, each cluster a small closed hub pyramid on the sand).
   - **4.1a Bush lobes:** each lobe a chunky **faceted polyhedron with big flat facets** (an 8–10-vertex hull: a flat
     bottom ring, a widest ring, a 3–4-corner top; 14–20 tris), Ø 1.4–2.2, lobes overlapping 0.1–0.3 into each other so
     every lobe chains to the patch. Not smooth spheres, not cupped lettuce heads: gem-like mounds with sharp facet
     edges, as the f34 draws.
   - **4.1b Leaves:** broad, upright, blunt-oval tips (widest at 0.45–0.5 L, L : W 2.2–2.6), outer leaves pitched 60–70°,
     inner 75–85°: fans that stand up (045 blocker 3). Not needles, not agave stars, not edge-on to the f34 or front.
5. **Hero `TallPine`** = root foot + trunk + Tier 1 lower + Tier 1 upper + Tier 2 + crown, stacked by §2.1, joined into
   one object of closed shells. No booleans between pieces.
6. **Parts shot** (az −20, e 20), laid out like the exploded: crown above Tier 2 above Tier 1 upper above Tier 1 lower
   above the trunk above the root foot, gaps 1.5–2.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a tall classic pine of four blade rings (crown, Tier 2, a double skirt) on a thick, high bare
   orange-brown trunk with buttress roots, on a pale sand patch with big rocks, leaf clusters and two faceted bush
   mounds.
2. **f34_sheet** against the hero (§2.5): hems, sub-step, waists, profiles, shares, dressing positions.
3. **front_sheet / side_sheet / rear_sheet, r34_sheet, top** per §2.5.
4. **Extras:** `ring_under` vs close-up 1; `trunk_cu` on the Trunk part vs close-up 2 (rim, recess, peg with its cut
   top); `root_cu` on the trunk foot vs close-up 3 (roots part of the trunk, a big rock, clusters).
5. **Contact counts** (§6): floating shells 0; every blade ≤ 0.03 from its core or a neighbour blade and chained to its
   core; every sleeve 0.01–0.03 over its seat; every rock, pebble, lobe and hub on the patch.
6. **Hero size** per §2.5; **scale shot** beside a 5.5-stud character marker under the skirt's edge: the marker's head
   must clear the lowest tips.
7. **Underside view** (kit `underside`): the skirt's blade undersides and the Tier 1 lower sleeve over the trunk top;
   the patch's flat bottom.
8. **Side by side with 042, 045 and 047** (`cmp_conifers.png`, each at its own f34 camera, framed to height) for §1.5.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Blades (crown 10, Tier 2 16, Tier 1 upper 18, Tier 1 lower 22) | 66 | 18 | 1188 |
| Ring cores + sleeves + pegs | 3 | 70–90 | 210–270 |
| Crown star cone + sleeve | 1 | 40–60 | 40–60 |
| Trunk body (16 facets × 7–8 bands, grooves, knot, rim, recess, peg) | 1 | 300–380 | 300–380 |
| Roots | 7 | 36–56 | 250–390 |
| Sand patch | 1 | 90–120 | 90–120 |
| Rocks | 5 | 24–56 | 200–240 |
| Pebbles | 3 | 8 | 24 |
| Bush lobes | 11 | 14–20 | 160–220 |
| Cluster and sprig leaves (6 × 6–8 + 2 × 4) | 46 | 8 | 368 |
| Cluster hubs | 8 | 6 | 48 |
| **Hero** | | | **about 2900–3300** (limit 4000, ceiling 3600) |
| Parts: CanopyTier3 / CanopyTier2 / CanopyTier1Upper / CanopyTier1Lower / Trunk / RootFoot | | | 220–240 / 360–380 / 400–420 / 470–490 / 560–770 / 890–1030 (limit 1000: aim at the low end) |

- **RootFoot is the tight part.** If it passes 960, drop C6 to 5 leaves and R5 to a 16-tri block before touching the
  bushes; never thin the clusters to spikes.
- **Spend headroom on the read:** if the canopy looks thin or the core shows, widen blades 10 % or add 2 outer blades to
  Tier 1 lower (+36) before anything else.

### 4.4 What to do better than W04's `ClassicPine` and the kit's conifers

| Earlier | This pine |
| --- | --- |
| W04: one needle key, flat green; lit tops mid green, no lime (R7-2) | base / light / deep needle keys blended by ring and along each blade, calibrated to the rendered lit canopy |
| W04: tiers read as steep tents in the parts (R7-7) | rings are umbrellas whose parts shot shows W : H 1.9–2.4 |
| W04: trunk hidden | bare trunk 0.29 H, T 15.5 % in the f34 |
| 042: canopy sparse and spiky, core visible between flaps | broad blades (W 1.9–2.5) in two visible rows, inner tips on top of the outer blades; no core visible from the sides |
| 042: lime tip on every flap (a scale pattern) | colour by ring and a gentle along-blade blend, tips at most +25 % light |
| 045: inner row tucked under; tiers merged into one skirt | inner rows on top; two waists measured; the only merge is the deliberate Tier 1 pair, with its sub-step |
| 045: plates too long (L : W 2) for paddles | here long blades are the design (L : W 2.6–3.0), with parallel sides and truncated tips |

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 24 × 22 box inside each, sd ≤ 3.0)

| Swatch | Box | Hex | HSV | Channel order | Use |
| --- | --- | --- | --- | --- | --- |
| Foliage Dark | (834,858,858,880) | `#2B583B` | 141°, 0.51, 0.35 | G > B > R | the shade tone; start for `needle_deep` |
| Foliage Mid | (834,892,858,914) | `#578C38` | 98°, 0.60, 0.55 | G > R > B | start for `needle` |
| Foliage Light | (834,926,858,949) | `#B3A733` | 54°, 0.72, 0.70 | R > G > B | yellower than the lit render (§3.11) |
| Trunk Mid | (834,961,858,983) | `#AB6933` | 27°, 0.70, 0.67 | R > G > B | start for `bark` |
| Trunk Dark | (834,995,858,1017) | `#8B512E` | 23°, 0.67, 0.55 | R > G > B | start for `bark_deep` |
| Rock | (834,1030,858,1051) | `#B8ACA4` | 24°, 0.11, 0.72 | R > G > B (G − B 8) | leans pink (§3.10) |
| Ground / Soil | (834,1064,858,1086) | `#D9BE9B` | 34°, 0.29, 0.85 | R > G > B | start for `sand` (the render is paler, §5.2) |
| Plant Leaves | (834,1099,858,1121) | `#81B032` | 82°, 0.72, 0.69 | G > R > B | start for `plant` |

### 5.2 Rendered regions (`samp.py`, `samp2.py`; median / v > .7 / lit quartile / shade quartile)

| Region | Median | Lit (v > .7) / lit quartile | Shade quartile | Halves (right = lit / left = shade) |
| --- | --- | --- | --- | --- |
| Canopy f34 / r34 / front / side / rear / top / exploded | `#4C8232` (100°, .62, .51) / `#438333` / `#4B8630` / `#4C832F` / `#4F8B30` / `#487F2C` / `#4A8131` | `#B0CD34` (73°) / `#B6D135` | `#134725` | f34 R `#A3C531` (74°, .75, .77) / L `#1C6834` (139°, .73, .41) |
| Crown / Tier 2 / skirt (f34) | `#609836` (94°, v .60) / `#5E9432` (v .58) / `#417731` (106°, v .47) | `#B5CF35` / `#B5D033` / `#ABCC35` | `#195F3E` / `#144C27` / `#114424` | nearest dark / mid / light: 39 / 19 / 42; 45 / 13 / 42; 50 / 15 / 36 |
| Crown / Tier 2 / skirt (front) | `#538E36` / `#5B9430` / `#3C752F` | `#AACA33` / `#B0CC30` / `#A5C833` | | 36 / 19 / 45; 44 / 18 / 38; 51 / 16 / 34 |
| Underside close-up (blades) | `#37632B` (107°, v .39) | `#A4C737` | `#1A3F21` | |
| Trunk f34 / r34 / front / exploded / close-ups 2, 3 | `#744324` (23°, .69, .45) / `#6F4224` / `#714224` / `#AB622C` / `#AC6437` / `#AD622E` | `#E08835` (28°, .76, .88) / `#E68D38` | `#442614` | f34 R `#C5712A` (27°, .79, .77) / L `#613C21` |
| Peg cut top (close-up 2) | `#E59548` (30°, .69, .90) | `#E99A4E` | `#AE6840` | |
| Rim / recess band (close-up 2) | `#9F5931` (22°) | `#DB8942` | `#5A331E` | |
| Sleeve (close-up 1, in shade) | `#724525` (25°, .68, .45) | `#B7692D` | `#442715` | hole near-black brown |
| Rock f34 R1 / R2 / root close-up | `#A5A095` / `#B0A399` / `#AAA09A` | `#CFBEAF` / `#E0CDB8` / `#DDC9B7`; f34 all `#DCCBB6` (34°, .17, .86) | `#69686A` (blue-grey: light) | |
| Sand f34 / front / root close-up | `#EFD3A1` (38°, .33, .94) / `#EDD0A1` / `#F2D9AF` | `#F2D7A7` | `#EDD09B` | |
| Bush mounds f34 / r34 / front | `#678821` (79°, .76, .53) / `#618A22` / `#547F21` | `#B0C825` (67°) / `#B3CA26` | `#18411E` | nearest dark / mid / light 37 / 24 / 39 |
| Leaf clusters f34 / front / root close-up | `#557C16` (83°, .82, .49) / `#587719` / `#50781D` | `#ABC013` (67°) / `#AAC01E` | `#2B4818` | 36 / 38 / 27 |

### 5.3 How the colour works

- **Blades:** one mid green that renders lime in light and deep green in shade; the crown and Tier 2 a step lighter
  (medians v .58–.60), the skirt (both Tier 1 rings) a step deeper (v .47, half its pixels nearest the dark swatch);
  blade roots and cores deeper; the outer third of each blade at most a quarter-step lighter. The sheet's hard
  lit-right / dark-left split is the light (§3.13). Keep the blades (lit 72–76°, shade 135–140°) apart from the bark
  (22–28°) by hue.
- **Bark:** one warm orange-brown (23–28°, sat 0.68–0.79, R > G > B); deeper in the grooves, the knot, the lowest 0.5
  of the trunk and roots near the sand, the sleeves (they sit in the canopy's shade) and the recess; **lighter on cut
  faces** (the peg top `#E59548`, the rim).
- **Rock:** one warm pale grey (30–38°, sat 0.10–0.17, R > G > B, G − B ≥ 12); crowns a step lighter, feet a step
  deeper. The blue-grey shade is the light.
- **Sand:** one pale warm sand (37–39°, sat 0.30–0.34, v .93); slightly deeper within 0.4 of the trunk, roots, rocks
  and hubs and on the bevel.
- **Bushes:** lime-yellow green (lit 67°), chosen **per lobe by position**: the top and outer lobes lighter, the lower
  and inner lobes deeper; never per facet by facing.
- **Leaf clusters:** two tones **per leaf by position** (taller and outer leaves lime, inner and lower leaves green),
  more saturated than the blades (sat .8) and yellower (lit 67° against the blades' 73°).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are medians of **unshadowed rendered regions** (lit half or v > .7), not swatches and not shade
quartiles. M042 was calibrated in the same studio against near-identical sheet colours; its final keys (needle
`#437529`, light `#B0BC2A`, deep `#1E5038`, bark `#965B24`, rock `#9C9894`, sand `#BAA784`, plant `#93A134`, plant deep
`#335A20`) are good **starting points** for the first calibration pass, not answers. `K.sample` kinds: `"green"` for
blades, bushes and leaves, `"brown"` for bark and sand, `"stone"` for rock, `"vivid"` for the lime keys if `"green"`
rejects them.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m049_needle` | f34 canopy median `#4C8232` ± 12 and lit half `#A3C531` ± 12 (start `#578C38`) | 96–104° median, lit 72–78°, G > R > B | every blade by default | rough 0.85, `low_spec=True` |
| `m049_needle_light` | v > .7 canopy `#B0CD34` ± 12 | 70–76°, sat ≥ 0.7 | crown cone 40 %, crown blades 30 %, Tier 2 blades 25 %; outer third of every blade +15–25 % | rough 0.85, low spec |
| `m049_needle_deep` | the dark swatch `#2B583B` rendered lit ± 12 | 135–145°, sat 0.45–0.6 | ring cores 70 %; the root third of every blade 30 %; Tier 1 lower 20 % overall, Tier 1 upper 10 % | rough 0.9, low spec |
| `m049_bark` | f34 lit-half trunk `#C5712A` ± 12; v > .7 `#E08835` (start `#AB6933`) | 24–28°, sat 0.68–0.79, R > G > B | trunk, roots, default | rough 0.9 |
| `m049_bark_light` | peg top `#E59548`; lit rim `#DB8942` | 27–31° | peg top 100 % (a cut); rim top 60 %; root rib crests on their outer half 20 % | rough 0.9 |
| `m049_bark_deep` | trunk-dark swatch `#8B512E` rendered lit; sleeve `#724525` in shade | 21–25°, sat 0.62–0.70 | grooves and knot 100 %; recess and sleeve hole 100 %; sleeves 70 %; the lowest 0.5 of trunk and roots 25 % | rough 0.95 |
| `m049_rock` | f34 lit (v > .7) `#DCCBB6` ± 10 | 30–38°, 0.12–0.18, **R > G > B, G − B ≥ 12** | rocks, pebbles | rough 0.85, metal 0 |
| `m049_rock_light` | lit quartile `#E7D5C0` | 30–36° | top 30 % of each rock's height at 35 % | rough 0.85 |
| `m049_rock_deep` | rock median `#AAA097` | 28–40°, 0.08–0.13 | lowest 0.25 at 25 % | rough 0.9 |
| `m049_sand` | `#EFD3A1` ± 8 (f34, front and close-up agree within 6) | 37–39°, 0.30–0.34 | patch | rough 0.95 |
| `m049_sand_deep` | a step below: `#E3C48F` | 37–39°, 0.35–0.38 | within 0.4 of trunk, roots, rocks, hubs 25 %; bevel 30 % | rough 0.95 |
| `m049_bush` | bush v > .7 `#B0C825` ± 12 (median `#678821`) | 64–72° lit, sat ≥ 0.75 | top and outer bush lobes | rough 0.85, low spec |
| `m049_bush_deep` | bush median in shade-free lobes, about `#4E7A22` | 85–95°, sat 0.65–0.75 | lower and inner lobes; 40 % of the outer lobes' bottom ring (by height, not facing) | rough 0.85, low spec |
| `m049_plant` | cluster v > .7 `#ABC013` ± 12 (swatch `#81B032`) | 64–70°, sat ≥ 0.8 | outer / taller leaves, all sprig leaves | rough 0.85, low spec |
| `m049_plant_deep` | cluster median `#557C16` | 82–92°, sat 0.7–0.8 | inner / lower leaves | rough 0.85, low spec |

**Calibration warnings:**
- **Blades (W04 R7-2; M035, M038):** judge the f34_sheet canopy: lit (v > .7) within 12 of `#B0CD34` (hue 70–80°, sat
  ≥ 0.65); whole-canopy median within 15 of `#4C8232`; skirt band median darker than the crown band by ≥ 0.08 v.
- **Bark:** f34 lit-half median within 12 of `#C5712A`, R > G > B. The sheet's whole-trunk median `#744324` is mostly
  shade; ours will be lighter (a known studio miss ≤ 25 levels, as 042).
- **Rock:** never pink or mauve: R > G > B with G − B ≥ 12 on every rock median.
- **Plants vs blades:** `m049_plant` and `m049_bush` lit at least 4° yellower than `m049_needle_light`; plant medians
  more saturated than the canopy's (045 and 042 plants rendered dark olive: re-measure in the hero render, where the
  canopy shades them).

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles, never facing)

- **Blades:** a field along each blade's own axis (0 root → 1 tip): `needle_deep` 0–0.3 (30 %), `needle` 0.3–0.7,
  `needle_light` 0.7–1.0 (**+15 % on Tier 1 rows, +25 % on Tier 2 and the crown**; 042 finding 3: no lime scale on
  every tip). Ring offsets: crown +30 % light, Tier 2 +20 % light, Tier 1 upper +10 % deep, Tier 1 lower +20 % deep.
  Undersides (the keel faces) keep the blade's positional colour (042 ruling: no deep-on-undersides). Per-blade tint
  ±0.04.
- **Cores:** `needle_deep` 70 %. Sleeves `bark_deep` 70 % / `bark`; the hole `bark_deep` 100 % (a cavity role).
- **Trunk and roots:** `bark` base; `bark_deep` by height (lowest 0.5: 25 %) and in the grooves / knot (hard);
  `bark_light` on the peg's cut top and the rim (hard: cut faces) and on the outer half of each root rib (20 %, picked
  by the rib vertices). Per-plank tint ±0.04 (whole facets).
- **Rocks:** `rock` base; `rock_light` top 30 % of height (35 %); `rock_deep` lowest 0.25 (25 %).
- **Sand:** `sand` base; `sand_deep` by distance (within 0.4 of trunk, roots, rocks, hubs: 25 %) and on the bevel
  (30 %); averaged with neighbours before quantising (no triangle shards).
- **Bushes:** per lobe by height in the mound (top lobes `bush`, bottom lobes `bush_deep`, middle 50 / 50); ±0.04 per
  lobe.
- **Clusters:** per leaf by role (outer / taller → `plant`, inner / lower → `plant_deep`), a quarter step deeper at each
  leaf's base; ±0.04 per cluster.
- **Hard edges only** where materials meet: blade | sleeve, bark | sand, rock | sand, leaf | sand, lobe | sand.

### 5.6 Texture (Tint) and finish

- **Tint:** blades amp 0.04 per blade (one tone per blade facet pair) plus broad noise 0.03 / scale 0.6; bark 0.04 per
  plank column plus 0.04 / 0.35; rock 0.04 per original facet (scale 0.4); sand 0.03 (scale 0.15, broad); bush 0.04 per
  lobe; leaves 0.04 per leaf. Never per-triangle confetti.
- **Finish:** blades, bushes and leaves `low_spec=True`, rough 0.85; bark 0.9 (deep 0.95); rock 0.85; sand 0.95. No
  emission.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Canopy:** f34_sheet lit (v > .7) within 12 of `#B0CD34`; whole canopy within 15 of `#4C8232`; crown band v ≥ skirt
  band v + 0.08. Front / side / rear canopy medians within 15 of `#4B8630`–`#4F8B30`.
- **Trunk:** f34 lit half within 12 of `#C5712A`. Peg top (Trunk part, `trunk_cu`) within 15 of `#E59548`.
- **Rock:** f34 v > .7 within 10 of `#DCCBB6`, R > G > B, G − B ≥ 12.
- **Sand:** f34 S median within 8 of `#EFD3A1`.
- **Bushes / clusters:** f34 bush v > .7 within 12 of `#B0C825`; cluster v > .7 within 12 of `#ABC013`; plant medians
  within 15 of `#678821` / `#557C16` (not olive: v ≥ .45).
- **Shares** per §2.5.

## 6. Joins and contact (no floating dressing)

- **Shells:** trunk + roots + rim + peg one closed shell; each ring core + sleeve + top peg one closed shell; the crown
  cone + sleeve one closed shell; each blade, rock, pebble, bush lobe, leaf and cluster hub its own closed shell; the
  patch one closed shell. All in one hero object (decision §8.6).
- **Stack** (§2.1): trunk base sunk 0.10 into the patch; each sleeve's flat bottom 0.015 above its seat (the trunk rim
  or the cap below), measured by BVH nearest distance: 0.005–0.03. Never coplanar, never overlapping. Each peg sits in
  its hole with 0.05 radial clearance and 0.1 head room: **pegs and hole walls must not touch** (no coincident faces).
- **Blades:** each outer blade's root end is buried 0.2–0.5 inside its core and leaves through the core's surface with
  no gap; inner blades rest on the outer row (ray cast, gap 0.015) or on the core; Tier 1 upper's outer blades rest on
  Tier 1 lower's blades. Neighbours may touch but cut no more than 0.05 into each other outside a core. Every blade
  chains by contact to its core, the core to the stack, the stack to the ground.
- **Base:** rocks sunk 0.08, pebbles 0.04, cluster hubs 0.03 into the patch top; every bush lobe touches a neighbour
  lobe or the patch and chains to the patch; every leaf within 0.03 of its hub (STAGES: no hidden stems); leaves may
  touch a rock, a root or the trunk but cut ≤ 0.05 into it.
- **Count floating shells before reporting** (STAGES: 035 and 036 failed round 1 on this): **0**. A shell "floats" if
  its nearest distance to every other shell and the ground is > 0.03, or if it doesn't chain to the ground.
- **Consistent winding (STAGES; 044's inward wedge face):** check every shell for faces wound against their
  neighbours; **0 winding errors**, reported in `build()`'s problems list. Blades and bush lobes are hand-built faces:
  check them especially.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0 (blade roots, leaf hubs and the peg / recess are
  where they grow).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no particles, no falling needles, no motes. The cast shadow is the
render's, not an effect.

- **Stage 5 (lighting): skip, and record why.** No emission, no PointLight. Studio notes (Requires Manual Validation):
  the canopy reads lime on the lit side and deep green in shade under the game sun (W04 R7-2's miss); the bark stays
  orange-brown, not red; the rocks stay warm pale grey, not pink.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** Not recommended: falling needles, pollen, dust, any
  light.
- **Collision:** hero `precise` (a hull would wrap the patch and the skirt into a 17-wide cone and stop players 8 studs
  from the trunk, though they should walk under the skirt); Trunk `hull`; the four canopy parts `hull`; RootFoot
  `precise`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json`, the repo text
(`git grep`) and every sheet / kit / wip `.blend` (zstd-decompressed, `blendall.py`):
- **W04 owns `ClassicPine`, `ClassicPineTrunk`, `ClassicPineTopTip`, `ClassicPineTallNarrow`, `ClassicPineShortWide`,
  `ClassicPineRootFoot`, `ClassicPineAsymmetric`** (in `W04.blend`, `FlintbornWorldKit.blend` and every wip copy: 80–86
  hits each), plus `YoungFir*`, `OldPine*`, `Sapling*`, `GroundScatterPinecone`; keys `w04_*`.
- **Kit conifers:** `TieredFir*` (042), `PineSapling*` (045), `GnarledPine*` (047), `pine_*` pieces (032 / 037).
- **`TallPine`, `StackedPine`, `TimberPine`, `LayeredPine` and `m049` occur nowhere** in the repo text, the manifests or
  any `.blend`. `TallPine` is not a substring of W04's `ClassicPineTallNarrow` (that reads "PineTall").

| Object | Part | Why |
| --- | --- | --- |
| `TallPine` | hero: root foot, trunk, four canopy rings | W04 owns `ClassicPine*`; "tall" names what sets it apart (the kit's tallest conifer, walk-under skirt) |
| `TallPineCanopyTier3` | "Canopy Tier 3": crown star cone + sleeve + 10 hem blades | the sheet's label |
| `TallPineCanopyTier2` | "Canopy Tier 2": core + sleeve + peg + 16 blades | |
| `TallPineCanopyTier1Upper` | "Canopy Tier 1", upper piece: core + sleeve + peg + 18 blades | §3.2 |
| `TallPineCanopyTier1Lower` | "Canopy Tier 1", lower piece: core + sleeve + peg + 22 blades | |
| `TallPineTrunk` | "Trunk": body, rim, recess, peg, 7 roots | |
| `TallPineRootFoot` | "Root Foot": patch, 5 rocks, 3 pebbles, 2 bush mounds, 6 clusters, 2 sprigs | the sheet's label |

- Palette keys `m049_*` (§5.4). Collection `Kit/M049 Classic Pine`. No sockets.

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **22.0 tall, canopy tips r 8.3 (silhouette about 16.4), trunk Ø 3.2, roots r 4.5–6.5, patch about
   18.5 × 15** (recommended: the kit's tallest conifer, 1.375 × 042 on a near-identical silhouette; the skirt tips at
   6.8–7.7 clear a character's head), or 20 (trunk 2.9, tips 6.2–7.0, the same height as 047), or 24 (W04's goal;
   chest-high dressing).
2. **Name (§8):** **`TallPine` and the six parts above** (recommended), or `StackedPine` (names the peg-and-sleeve
   construction, but reads close to 042's `TieredFir`). Not `ClassicPine*` (W04).
3. **Canopy rings (§2.2, §3.2):** **four rings: crown 10 hem blades on a 5-ridge cone; Tier 2 8 + 8; Tier 1 upper
   9 + 9; Tier 1 lower 11 + 11; inner rows visible on top; one blade aimed at −Y on every ring** (recommended: the
   exploded's four pieces, the f34 / r34 sub-step, the top view's 13 points), or three rings with a single skirt
   (cheaper, but loses the sub-step and the exploded's fourth piece).
4. **Blade shape (§2.3):** **long parallel-sided 18-tri blades, L : W 2.6–3.0, keel 0.12 W for edge thickness,
   truncated chisel tip 0.35 W** (recommended: the sheet's boards; neither 042's kites nor 045's paddles), or 042's
   16-tri kite (cheaper, but reads as 042).
5. **Exported parts (§8, §3.2):** **Tier 1 as two parts, `CanopyTier1Upper` and `CanopyTier1Lower`** (recommended: the
   exploded draws two pieces, each about 410–490 tris, and each ring can rotate on its own), or one `CanopyTier1`
   holding both rings (matches the single label and "three canopy layers", but about 900 tris, close to the 1000 part
   limit).
6. **Joints and packaging (§2.1, §3.6, §6):** **peg-and-sleeve at every ring (a hollow trunk rim with a peg; each ring
   a bark hex sleeve with a blind hole over the peg below; 0.015 seats; pegs clear their holes); one hero object of
   closed shells, trunk + roots + rim + peg one shell, no booleans between pieces** (recommended), or flat seats without
   pegs (simpler, but drops the sheet's "stack and rotate" construction).
7. **Roots (§2.4, §4.1):** **seven buttress roots built into the trunk mesh as explicit ribs (no union seam)**
   (recommended: "blended to base"), fallback the 042 one-at-a-time exact unions at the origin with sliver cleanup.
8. **Branches (§3.14):** **none** (recommended: none on the sheet; the skeleton is the trunk, roots, rim and peg).
9. **Dressing (§2.4, §3.5, §3.9):** **5 rocks (two big at the front-left), 3 pebbles, 2 faceted bush mounds at the right,
   6 broad-leaf clusters, 2 sprigs, at the sheet's proportions; f34 + front plan** (recommended), or the dressing scaled
   down 20 % (closer to 042's base, but the sheet's bushes and clusters are big).
10. **Comparison cameras (§3.1):** **`f34_sheet (−15, 12)` governing** (probe az ±10, e ±4); `r34_sheet (165, 12)`,
    `front_sheet (0, 7)`, `side_sheet (90, 7)`, `rear_sheet (180, 7)`, kit `top`, `underside`; extras: parts shot
    (−20, 20), `blade_cu`, `ring_under` (e −40), `trunk_cu (−30, 30)`, `root_cu (−20, 12)`, `cmp_conifers.png` (042 /
    045 / 047 / 049), a scale shot with a 5.5-stud marker. Floor hidden in every `*_sheet` render.
11. **Colour (§5):** **needle base / light / deep keys calibrated to the f34 canopy median `#4C8232`, lit half
    `#A3C531`, v > .7 `#B0CD34` and the dark swatch; crown and Tier 2 lighter, the skirt deeper; a gentle along-blade
    blend (tips +15–25 % light at most); bark lit `#C5712A`, cut faces `#E59548`; rock lit `#DCCBB6` (G − B ≥ 12); sand
    `#EFD3A1`; bushes `#B0C825` lit per lobe; clusters lime / green per leaf** (recommended); never by facing, no deep
    undersides.
12. **Stages 5 and 6:** **skip both, recorded** (recommended: nothing glows or moves on the sheet).
13. **Collision (§7):** **hero `precise`, Trunk and canopy parts `hull`, RootFoot `precise`** (recommended).
14. **Budget (§4.3):** **4000 limit, about 2900–3300 planned, ceiling 3600; parts under 1000, RootFoot ≤ 960**
    (recommended).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **Reading as 042 (the near-identical sheet).** The verifier's `cmp_conifers.png` must show, against 042: 22 against
   16 tall; a small crown (hem ≤ .41 of the canopy, at h .79); four rings with a skirt sub-step in the f34; long
   parallel blades with truncated tips, not kites; a thick trunk bare to 0.29 H (T 15.5 ± 3 % in the f34); buttress
   roots blended in; faceted bush mounds; a 5-ridge crown star from above.
2. **Tiers merging into one skirt (045 round 1 blocker).** Two waists measured in every side view (h .78 / .58 ± .03,
   widths ≤ .29 / ≤ .49); inner rows visible on top of each ring, their tips at 0.6–0.65 of the outer radius; a dark
   crease under the crown and Tier 2 hems. The only merge is the Tier 1 pair, and even it shows its sub-step in the f34
   and r34.
3. **A sparse, spiky canopy with the core showing (042 finding 2).** Blades broad (W 1.9–2.5) and overlapping; no core
   visible from the sides or above; outer blades bent down a further 10–14° at 0.8 L so the side tips hang rather than
   spike flat; f34 G ≥ 66 %.
4. **A lime scale pattern on every tip (042 finding 3).** Light by ring (crown and Tier 2) with tips at most +15–25 %;
   on the sheet colour barely changes along a blade.
5. **Colour by facing (042 ruling, STAGES).** No light-right / dark-left paint, no deep undersides, no "top faces light".
   Fields along each blade, by ring, by height, by role (grooves, cut faces, cavities); `K.check` facing correlation
   < 0.5 per material.
6. **Canopy too dark, grey or olive (W04 R7-2; M035; M038).** Lit canopy within 12 of `#B0CD34`, sat ≥ 0.65.
7. **Hidden or thin trunk (W04 "trunk hidden"; the user's tree rule).** Bark visible from the sand to z ≈ 6.8 in the
   front, side and rear (bare band h .20–.29 with no plant in front of the axis), Ø 3.2, with the buttress flare and
   seven roots of different reach, checked in `root_cu`, front, side, rear and underside, not only the f34.
8. **Floating dressing (STAGES; 035 and 036 round 1).** Every blade, lobe, rock, pebble, leaf and hub within 0.03 of a
   neighbour, its core or the patch, chaining to the ground: **0 floating shells**. New risks here: the nested Tier 1
   upper ring hovering over Tier 1 lower, a bush lobe touching only air, a peg touching its hole wall.
9. **Winding (STAGES; 044's inward wedge face).** 0 faces wound against their neighbours on every shell; check the
   hand-built blades, lobes, rim and recess especially.
10. **Egg or mauve rocks (M034 round 1; M037 "egg-shaped"; this sheet's pink swatch).** Chunky angular blocks with a
    broad base and a flat 4–6-corner crown, 10–16 broad facets, W : H 1.3–1.6; R > G > B with G − B ≥ 12.
11. **Spiky, edge-on or agave leaves; lettuce-ball bushes (039; 045 blocker 3; M036; M038).** Cluster leaves broad with
    blunt-oval tips, upright fans (outer 60–70°, inner 75–85°), lime outside / green inside, not edge-on to the f34 or
    front. Bush mounds are faceted gem-like lobes with big flat facets, not smooth balls or cups.
12. **Plants dark olive (042 finding 6; 045 finding 3).** Cluster and bush medians at v ≥ .45, hue 79–87°, measured in
    the hero render.
13. **Over-wide patch or base clutter (042 finding 4).** Patch about 18.5 × 15 and thin; f34 S ≤ 6.4 %; dressing below
    4.4 tall and inside the patch.
14. **The top view (W04 R7-6; 045 finding 7).** ≥ 11 outer star points with the second row between, a 5-ridge crown
    star, rocks peeking past the skirt; not a round rosette.
15. **Exact booleans:** only if the root fallback is used, at the origin, one at a time, saving between them (STAGES
    "Booleans"); nothing else is unioned. Collapse union corners under 3°.
16. **Names and scope.** No `ClassicPine*` (W04), no `TieredFir*` / `PineSapling*` / `GnarledPine*`; only one agent
    drives a Blender session at a time; no commits, pushes or exports in stage agents; don't edit `lib/vfx.py` or the
    frozen shared helpers; don't touch M045's or M047's objects (being worked on in parallel).

## Decisions (main session, 2026-10-29)
All 14 recommendations are accepted.
1. **Size.** 22 tall, canopy about 16.4 across, skirt tips at 6.8–7.7 (above head height).
2. **Names.** `TallPine`, plus `TallPineCanopyTier3`, `…CanopyTier2`, `…CanopyTier1Upper`, `…CanopyTier1Lower`, `…Trunk` and `…RootFoot`. Keys are `m049_*`. Never `ClassicPine*`, which W04 owns.
3. **Rings.** Four rings: crown 10, Tier 2 8 + 8, Tier 1 upper 9 + 9, Tier 1 lower 11 + 11. Each ring has one blade aimed at the front, and the inner row lies on top. **Tiers must not merge into one skirt**: two waists in every view, and the f34 sub-step must show (M045's round-1 failure).
4. **Blades.** 18-tri, parallel-sided, with cut-off tips, a visible edge thickness and a shallow ridge. Not kites, paddles or pads.
5. **Tier 1 export.** Two parts, upper and lower.
6. **Joints and packaging.** A peg and hex sleeve at every ring, with 0.015 seats and the pegs clear of their holes. One hero object built from closed shells, with no booleans between pieces. **No floating dressing**, **0 winding errors**, and no dressing more than 0.05 into rock.
7. **Roots.** Seven ribs built into the trunk mesh.
8. **Branches.** None.
9. **Dressing.** Keep the sheet's proportions. Bushes are faceted rounded mounds and the clusters are upright broad leaves. Nothing spiky, edge-on or olive.
10. **Cameras.** As listed. The front three-quarter at (−15, 12) governs.
11. **Colour.**
    - Canopy median `#4C8232`, lit half `#A3C531`; crown and Tier 2 lighter, the skirt deeper.
    - Blade tips at most +15–25 %, with no lime cap on every blade.
    - Bark lit half `#C5712A`, cut faces `#E59548`.
    - Rock `#DCCBB6` (G at least 12 above B; never pink or mauve), sand `#EFD3A1`, bushes `#B0C825`.
    - **Never colour by facing.** No deep undersides.
12. **Lighting and VFX.** Both skipped; record that.
13. **Collision.** Hero precise.
14. **Budget.** 4000 limit, 3600 ceiling, RootFoot ≤ 960.

**Binding.** The seven §1.5 differences from M042, M045 and M047, and the f34 shares (green 69.1, trunk 15.5, each ±4).
