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

## Stage 1 — Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m049.py` (`build()`), work file `art/blender/assets/kit/wip/M049.blend` (saved after the
final build), background session on port 9881. The final check ran in a freshly restarted session; `build()`'s problems
list is empty. Cut tests, the contact report, `_post` and the leaf / hub / rock patterns are copied (not imported) from
m045. **No booleans anywhere:** every piece is a closed shell built explicitly. Scratch scripts and side-by-sides are in
the scratchpad folder `m049w/` (`prof.py` width profiles, `tiers_r.py` hems / waists, `col.py` colours, `sbs.py`,
`cus.py`).

**Parts, each from its own function:**
- `blade()`: one closed **18-tri** shell (spec §2.3): a root point; section A (left, ridge 0.08 W, right, keel 0.12 W);
  section B at 0.75 L with the **same width** (ridge and keel 0.8×); two tip points 0.26 W apart (a short chisel point).
  Root fan 4, band A→B 8, tip 6. The outer part bends down `droop` in two steps, and the blade is rolled about its own
  axis. The chord is fitted so the tip lands on the requested (r, z). Per row the taper length can change (`sa`): the
  inner rows put A at 0.50 L, so their roots are narrow where they converge near the cap (outer rows 0.30 L).
- `_core(kind)`: one closed shell per ring:
  - an octagonal top peg on a flat cap;
  - a pleated cone to the rim (corners at the outer-row azimuths ±0.12);
  - an underside in to a **hex sleeve**, then the sleeve's flat bottom and a **blind octagonal hole** (walls and ceiling
    in the same shell).
  - Crown: a **five-ridge star cone** (ridges r 2.0, valleys 1.45 at z 18.6, apex 22.0, one ridge at −Y) with the same
    sleeve and hole.
- `ring(kind)`: the core, the outer row, then the inner row on top.
  - Every blade is tested against the blades placed before it, against the ring below (`_below`, a probe build, so a part
    equals the hero's ring) and against the core below.
  - A blade cutting more than 0.05 outside a core has its tip turned up about its buried root, then it is rolled, then
    narrowed. **Roots never move**, so no blade can float.
- `trunk()`: **one closed lofted shell** (decision 7: the roots are part of the trunk mesh, with no union).
  - Six root-region rings (z 0.05 / 0.95 / 1.65 / 2.5 / 3.4 / 4.4) carry, per root, flank / crest / crest / flank
    vertices, plus valley points in each gap (one per ~30°). Each root is a log 0.95 high near its blunt tip (0.36 w
    wide), rising as a buttress rib into the trunk. Flanks are capped at 0.4 of the gap to a neighbour (an early build
    self-intersected where two roots were 30° apart).
  - Then a 16-vertex planked octagon at z 5.4 / 7.0 / 8.8 / 11.0: each side split, the split pushed out 0.06–0.10; three
    splits pushed in 0.10 are the grooves (0°, 135°, 225°).
  - A knot slit: a half-facet inset 0.16 and pressed in 0.08, front-right, z 5.4–7.0.
  - The flat rim (z 11.0), a dished recess (corner r 1.0, floor 10.65), the octagonal peg (apothem 0.425, top 12.2,
    leaning +0.05 X) and its cut top with an inset pith octagon.
- `patch()`, `rock()` ×5, `pebble()` ×3, `bush()` ×2, `cluster()` ×6 and `sprig()` ×2:
  - Bush lobes (`lobe()`): hulls of a bottom ring of 4, a widest ring of 5 at 0.42 h and a top of 3 at 0.88 h, 20 tris
    each: gem-like faceted mounds.
  - Leaves: closed 10-tri broad leaves with a blunt end 0.24 W wide, L : W 1.75, an 18° V fold. The outer ring is
    pitched 60–70° and arches out; the inner ring 75–85°. They stand on 4-sided hub pyramids.
  - A leaf that would cross a rock or the trunk is turned or shortened: **all 39 leaves were placed, none dropped**.

**Stack as built.** The spec's §2.1 heights did not work: Tier 1 upper's cap at 15.0 sat below its own hole ceiling. The
heights were re-derived so each blind hole swallows the peg below with 0.1 head room and 0.125 radial clearance at the
flats (hole apothem 0.55, peg apothem 0.425).

| Piece | Seat (sleeve bottom) | On | Hole ceiling | Cap | Top peg |
| --- | --- | --- | --- | --- | --- |
| Trunk | z 0.05 (sunk 0.10) | patch | — | rim 11.0, recess floor 10.65 | 12.2 |
| Tier 1 lower | 11.015 | trunk rim | 12.30 | 14.50 | 14.95 |
| Tier 1 upper | 14.515 | T1L cap | 15.05 | 15.40 | 15.85 |
| Tier 2 | 15.415 | T1U cap | 15.95 | 18.20 | 18.65 |
| Crown | 18.215 | T2 cap | 18.75 | apex 22.0 | — |

**Rings as built** (tuned on the renders; root (r, z) → tip (r, z)):

| Ring | Outer row | Inner row (on top) |
| --- | --- | --- |
| Crown | 5 long blades along the ridges, (0.25, 21.45) → (3.10, 17.45), front 17.30, W 2.0, droop −12 (the tips flare: a concave spire) | 5 short blades in the valleys, sunk under the long ones, (0.55, 20.10) → (2.75, 17.60), W 1.25 |
| Tier 2 | 8, (1.75, 16.90) → (5.60, 13.10), front 12.85, W 3.0, roll 8 | 8, (0.80, 17.90) → (2.90, 16.15), W 2.3, roll 18, A at 0.5 L |
| Tier 1 upper | 9, (1.90, 14.30) → (7.45, 9.30), front 9.00, W 3.2, roll 5 | 9, (0.85, 15.10) → (3.40, 13.55), W 2.6, roll 18 |
| Tier 1 lower | 11, (2.60, 12.30) → (8.30, 7.70), front 7.20, W 3.8, roll 8 | 11, (0.90, 13.95) → (3.95, 11.55), W 2.6, roll 18 |

Why the changes from §2.2:
1. **Wider blades** (T1L outer 2.5 → 3.8, T1U 2.2 → 3.2, T2 1.9 → 3.0, crown 1.25 → 2.0). At the spec widths the rings
   read as separate hanging "legs" with gaps between them; the sheet's tiers are closed fans of overlapping boards.
2. **Shorter, lower inner rows** (tips at 0.39–0.48 of the outer radius; spec 0.6–0.65). At the spec's lengths the cut
   test lifted each inner row up to 0.9 (it rests on the rolled outer row). That made every tier fat at the top and lost
   both waists (front waist .64 at h .58 against the sheet's .48). Tier 1 lower's inner row is hidden under Tier 1 upper
   in the hero anyway; it shows on the part.
3. **The crown is a cone of blades.** Five long blades lie along the cone's ridges from just under the apex to the hem
   (the sheet draws the crown's faces as blades), with five short ones tucked between. The first build (hem blades only,
   under the rim) showed a bare lime pyramid.
4. **Trunk Ø ≈ 3.7 at z 5–7** (corner radii 1.93 / 1.85 / 1.74 / 1.58 at z 5.4 / 7.0 / 8.8 / 11.0: 3.57 across the
   flats plus the planks). At 3.2 the trunk read clearly thinner than the sheet's in every side view.
5. **Dressing moved off the roots** (the spec's plan put BA, C3, C4 and R2 on roots):
   - Roots: RF 268° r 4.1, RFR 292° r 5.2, **RR 318° r 6.5 (the long front-right root)**, RB1 70° r 4.6, RB2 128° r 5.0,
     RL 176° r 4.3, RFL 238° r 4.4.
   - Bushes: BA (5.0, −0.6), 6 lobes, top 4.35; BB (8.0, 0.1), 5 lobes, top 3.5.
   - Rocks: R1 (−5.8, −1.5) 3.6 × 2.9 × 2.4; R2 (−0.9, −6.2) 3.8 × 3.1 × 2.5; R3 (2.6, 5.2) 2.7 × 2.2 × 1.8; R4 (8.3,
     3.4); R5 (−6.9, 3.2).
   - Clusters and sprigs moved: C2 (−8.0, −3.5), C4 (3.4, −4.8), S1 (2.0, −6.7).
   - Rock / root cut 0.000.

**Hero `TallPine`** = ground + trunk + T1L + T1U + T2 + crown, one object of **138 closed shells**: patch 1, trunk 1,
cores 4, blades 66, rocks 5, pebbles 3, lobes 11, hubs 8, leaves 39.
- Parts: `TallPineCanopyTier3`, `…CanopyTier2`, `…CanopyTier1Upper`, `…CanopyTier1Lower`, `…Trunk`, `…RootFoot`, each at
  the origin (bbox bottom centre).
- `o["m049_offset"]` is that origin in the build frame: hero (0.29, −0.04, 0); T1L (0.08, −0.04, 7.17); Trunk (0.63,
  −0.37, 0.05).

**Measured on the renders** (floor hidden, 3× lens; `m049w/tiers_r.py` and `prof.py` with the study's masks):

| View | Hems h / W (sheet) | Waists h / W (sheet) | Canopy W / H (sheet) |
| --- | --- | --- | --- |
| front_sheet (0, 7) | .814 / .36 (.801 / .35); .631 / .68 (.610 / .66); .397 / 1.0 (.386 / .99) | .794 / .32 (.780 / .23); .609 / .51 (.577 / .43) | .706 (.732) |
| rear_sheet (180, 7) | .819 / .35 (.783 / .41); .633 / .67 (.614 / .68); .387 / 1.0 | .802 / .30 (.764 / .29); .605 / .51 (.583 / .48) | .719 (.646) |
| side_sheet (90, 7) | .634 / .67 (.587 / .70); .39 / 1.0 (.356) | .611 / .57 (.547 / .50) | .706 (.668) |
| r34_sheet (165, 12) | .829 / .34; .414 / 1.0 (.367) | .806 / .30 (.765 / .27); .600 / .61 (.574 / .46) | .686 (.723) |
| f34_sheet (−15, 12) | width profile within ±.07 of the sheet at every h from .36 to .98 (h .60: .58 / .53; .70: .56 / .60; .78: .33 / .32; .84: .33 / .34); the sub-hem at h .44 is .93 wide (sheet 1.0) | .603 / .57 (.612 / .49) | .691 (.679) |

- f34 shares **G 70.2 / T 13.8 / S 6.0 / R 8.4** (sheet 69.0 / 15.5 / 4.4 / 8.7); front 71.3 / 13.1 / 4.7 / 9.4 (sheet
  72.0 / 14.2 / 3.2 / 7.7).
- Trunk widths (front, as a fraction of the canopy W): h .25 .239 (sheet .200); h .20 .263 (.239).
- Top (0, 89): W : D 1.08; G 94 / S 2.3 / R 2.0 (sheet 86 / 0 / 11).

## Stage 2 — Optimisation and cleanup

- **Tris: hero 3304** (ceiling 3600, limit 4000): blades 1188 (66 × 18), trunk 704, cores 494, leaves 390 (39 × 10),
  lobes 220, rocks 180, patch 56, hubs 48, pebbles 24.
  - Parts: CanopyTier3 254, CanopyTier2 420, CanopyTier1Upper 462, CanopyTier1Lower 546, Trunk 704, **RootFoot 918**
    (≤ 960). All are under 1000.
- **`M.audit`, all 7 objects:** non-manifold edges 0, **bowtie / non-manifold verts 0**, boundary 0, wire 0, loose 0,
  zero-area 0, n-gons 0, duplicate verts 0, normals outward, transforms applied, origin at the bbox bottom centre.
- **Per shell (`shells_report`, every object):** every shell is closed with a positive volume, with 0
  self-intersections and **0 winding errors**.
- **Thin triangles:** none under 2° on any object (smallest corner 2.15°, on the trunk). The patch's 0.04-high side wall
  gave 28 slivers (0.5°), so it was removed: the bevel now runs to the outline at the ground.
- **Sizes:** hero 19.45 × 16.99 × 22.00 (patch 19.45 × 15.4, canopy 16.8 × 17.0); T3 6.10 × 5.78 × 4.67; T2 11.59 ×
  11.58 × 5.88; T1U 14.46 × 14.56 × 6.75; T1L 16.78 × 16.99 × 7.78; Trunk 9.83 × 9.39 × 12.15; RootFoot 19.45 × 15.37 ×
  4.02.
- **Contact (no floating dressing):**
  - Hero: floating **0**, unchained **0**, worst gap 0.002.
  - Ring seats **0.015 ×4**, with 0 core / trunk intersections (the pegs clear the holes).
  - 65 blade pairs touch, and **0 cut more than 0.05** (deepest 0.050).
  - Leaves crossing a rock, a lobe or the trunk: 0. **Dressing buried in rock or trunk: max 0.000.** Rock / root cut
    0.000.
  - Each part: floating 0, unchained 0, deepest blade cut 0.042–0.050.
- Blade fixes in the final build (lifts / rolls / narrowings): T1L 23 / 13 / 0; T1U 91 / 12 / 1; T2 19 / 2 / 0; crown
  0 / 0 / 0.

## Stage 3 — UV

`M.smart_uv` (angle 45, ANGLE_BASED, margin 0.008), then `m012._uv_unfold`.
- Every object: **0 overlapping pairs, 0 flipped**, minimum island gap 0.016, border 0.008, texel density min / median /
  max 1.0 / 1.0 / 1.0, conformal stretch p95 1.008–1.027.
- Islands: hero 920, T3 58, T2 83, T1U 84, T1L 105, Trunk 90, RootFoot about 400.

## Stage 4 — Materials, colour and texture

- **Calibration:** `K.calibrate` (6 iterations, the spec's §5.4 targets), then a pass on the hero f34 render for the light
  key and the plant and bush deep keys. Final `PALETTE`:

  | Key | Hex | Dome render (target) |
  | --- | --- | --- |
  | needle | **#416E31** | 74,128,50 (#4C8232) |
  | needle_light | **#ACC22A** (calibrated #8CA634; raised because the f34 v > .7 lime read grey) | 172,201,53 at #8CA634 (#B0CD34) |
  | needle_deep | #274D39 | 44,88,60 (#2B583B) |
  | bark | **#9B5D1D** | 195,113,46 (#C5712A) |
  | bark_light | #B47B3B | 228,149,72 (#E59548) |
  | bark_deep | #6F411E | 138,80,44 (#8B512E) |
  | rock | #B0A496 | 217,202,182 (#DCCBB6) |
  | rock_light | #BEB2A2 | 227,212,191 |
  | rock_deep | #878382 | 170,159,151 |
  | sand | #BCAA88 | 238,208,157 (#EFD3A1) |
  | sand_deep | #B29E7B | 225,193,142 |
  | bush | #8EA625 | 175,201,37 (#B0C825) |
  | bush_deep | **#568A2A** (calibrated #446922; raised because the plants rendered olive, v .40) | |
  | plant | #8CA012 | 172,193,19 (#ABC013) |
  | plant_deep | **#66A02A** (calibrated #496A16; raised for the same reason) | |

- **Blends (by position and role only, in 25 % steps; never by facing):**
  - **Blades:** three bands along each blade (root fan, A→B, tip) on the deep ↔ light axis: T1L (−.5, −.25, −.25), T1U
    (−.5, 0, 0), T2 (−.25, +.25, +.25), crown long (0, +.25, +.25), crown short (0, 0, +.25). **No lime cap:** the tip
    band equals the body, except on the crown's short blades. Per-blade Tint ±0.04, plus a broad mottle of 0.03 (scale
    0.6).
  - **Cores:** needle_deep 75 %; the crown cone needle_light 25 %, its underside −25 %; top pegs bark; sleeves bark_deep
    75 %; holes bark_deep (a cavity, hard).
  - **Trunk:** bark; the ground band and the bottom 25 % deep; the two plank columns beside each groove 25 % deep; the
    recess 50 % deep; the knot bark_deep with its walls 50 %; the peg's cut top bark_light and the pith bark_deep. Plank
    columns Tint ±0.04, mottle 0.04 (scale 0.35).
  - **Rocks:** the top 22 % of the height +50 % light, the next 16 % +25 % light, the lowest 25 % +25 % deep; mottle 0.04.
  - **Sand:** the bevel and underside 50 % deep; within 0.4 of the trunk, roots, rocks, lobes and hubs 25 % deep; mottle
    0.03.
  - **Bushes:** per lobe, by the height of its top in the mound (the top lobe bush, middle lobes 50 %, low lobes 25 % bush
    over bush_deep); each lobe's lowest quarter a step deeper (by height); ±0.04 per lobe.
  - **Clusters:** outer leaves plant (every third plant_deep), inner leaves alternating plant_deep and plant; each leaf's
    base faces a step deeper; ±0.04 per leaf.
- **`K.check`:** no problems. Baked-shading (facing) correlation: hero 0.33, T3 0.03, T2 / T1U / T1L / Trunk 0.00,
  RootFoot 0.14 (limit 0.5).
- **Finish:** blades, bushes and leaves rough 0.85 with low specular; bark 0.9 (deep 0.95); rock 0.85; sand 0.95. No
  metal, no emission.
- **Re-measured** (`m049w/col.py`, ours | sheet):

  | Region | f34 | front |
  | --- | --- | --- |
  | Canopy median | **#4C8233** \| #528832 ✓ | #497F31 \| #548D31 ✓ |
  | Crown / T2 / skirt | #689531 / #6A9733 / #487E35 \| #578C33 / #5F9732 / #498032 | #5D8B2E / #618C2F / #457932 \| #508C35 / #5C9630 / #4D8730 |
  | Band v (crown / T2 / skirt) | .584 / .592 / .494 \| .549 / .592 / .502 (crown ≥ skirt + .08 ✓) | .545 / .549 / .475 |
  | Canopy v > .7 | #A3B77E \| #B0CD34 (✗: few pixels, desaturated by the studio's specular) | #A6BC80 \| #ABCA32 |
  | Trunk v > .7 | **#C3712E** \| lit-half target #C5712A ✓ (sheet v > .7 #E08835) | #C2712F \| #DB8836 |
  | Rock v > .7 | #D7C8B0 \| #DACBB7 ✓ (R > G > B, G − B 24) | #D3C6AC \| #D4C8B3 |
  | Sand | #F1D2A1 \| #EFD3A1 ✓ | #F0D1A1 \| #EDD0A1 |
  | Plants (h < .3) | #5D7613 \| #5B7F1D ✓ (v .46) | #597113 \| #567B1F |

  The side, rear and r34 canopies read darker than the sheet (#356226–#3B6A2B against #478633–#559031). The studio's key
  light is front-left, so views from the side and behind see the shaded side (M045 found the same). Not painted.

## Stage 5 — Lighting

Skipped: the sheet shows nothing glowing and no light (spec §7). No emission, no PointLight.

Studio notes (Requires Manual Validation): under the game's sun, check that the canopy reads lime on the lit side and deep
green in shade, the bark orange-brown (not red) and the rocks warm pale grey (not pink).

## Stage 6 — VFX

Skipped: the sheet shows no effect (spec §7). `build()` checks that the hero has no VFX sockets.

Collision: hero precise; the four canopy parts and the Trunk hull; RootFoot precise.

## Modeller's notes for the verifier

**Renders** are in `art/blender/renders/models/M049/`; the contact sheet is `M049_views.png`.
- Kit views: `front34`, `rear34`, `front`, `side`, `rear`, `top`, `underside`.
- Sheet views: `f34_sheet` (−15/12), `r34_sheet` (165/12), `front_sheet` / `side_sheet` / `rear_sheet` (e 7),
  `top_sheet` (floor hidden, 3× lens).
- Parts: `part_canopytier3` … `part_rootfoot` (−20/20), plus `exploded` and `scale`. The scale shot has a 5.5-stud marker
  under the skirt at (−3.6, −6.6); its head clears the lowest tips (z 7.2).
- Close-ups:
  - `ring_under`: Tier 1 lower from −40, blades round the bark hex sleeve and its dark hole (close-up 1);
  - `trunk_cu`: the rim, dished recess and peg, with a light cut top and a dark pith (close-up 2);
  - `root_cu` (close-up 3), `blade_cu` (edge thickness and chisel tips), `skirt_cu`.
- `cmp_conifers.png`: 042 / 045 / 047 / 049 at true scale from the f34 camera (`m049.compare_conifers()`).

**§1.5 differences, as built:**
- **Size:** 22.0 tall (042 16, 045 10, 047 20); canopy 16.8 × 17.0 (tips at r 8.3–8.5); trunk Ø ≈ 3.7 at z 5–7, 2.9 at
  the rim.
- **Lowest skirt tips z 7.17** (the front blade) to 7.7: above a 5.5 character's head (`scale`).
- **Silhouette:** a small crown (front hem .36 wide at h .81), Tier 2 (.68 at h .63), and the skirt (1.0 at h .40), with
  Tier 1 upper's tips 1.6–2.4 above and about 0.9 inside Tier 1 lower's.
- **Four rings: crown 10 + Tier 2 16 + Tier 1 upper 18 + Tier 1 lower 22 = 66 blades.** One outer blade (and one crown
  ridge) points at −Y on every ring.
- **Blade:** an 18-tri parallel-sided board, ridge 0.08 W, keel 0.12 W (the edge thickness), chisel point 0.26 W.
  Whole-blade chord : width (root to tip, root buried): T1L outer 1.9, T1U 2.3, T2 1.8, crown long 2.5, inner rows 1.3–1.7
  (see the leftovers).
- **Crown from above:** five long blades on the five cone ridges, a 5-ridge star (042: 4 + 4; 045: 4).
- **Joint:** the trunk's rim, recess and peg; every ring a bark hex sleeve with a blind hole over the peg below; seats
  0.015, head room 0.1, radial clearance 0.125.
- **Trunk:** a planked octagon with 3 grooves and a knot slit, bare from the sand to z 7.2 (front tips) or about 9 (the
  sides). **Seven buttress roots in the same shell**, ribs rising to z 3.4–4.4, reaching r 4.1–6.5. f34 T share 13.8 %.
- **Ground:** two faceted bush mounds (right), six upright broad-leaf clusters and two sprigs; five chunky warm pale grey
  rocks (two big ones at the front-left: R1 2.4 tall, R2 2.5) and three pebbles.

**Leftovers:**
- Blade L : W is 1.8–2.5 on the outer rows, below §1.5's 2.6–3.0. At the spec's widths the rings read as separate
  hanging blades with gaps (the first two builds). The blades are still parallel boards with chisel points, unlike 042's
  kites and 045's paddles (`cmp_conifers.png`).
- Inner-row tips sit at 0.39–0.48 of the outer radius (spec 0.6–0.65), to keep the waists (Stage 1, change 2).
- The front and side waist under Tier 2 is .51–.57 wide (sheet .43–.50). The governing f34 matches (.57 against the f34
  sheet's .53 at h .60): the sheet's front and side cells draw a narrower skirt top than its own f34.
- In the f34 the sub-hem reads as a shoulder (.93 wide at h .44) rather than a second 1.0-wide peak.
- Top view: the rocks barely peek past the skirt (R 2 %, sheet 11 %), and the blade ends read rounder than the sheet's
  points.
- The canopy's v > .7 pixels are greyer than the sheet's lime (the studio's specular). The side, rear and r34 canopies
  read darker (the studio light).
- In the f34, about 12 bark pixels (the crown's sleeve) show between the crown hem and Tier 2.

## Verification round 1 (verifier, 2026-10-29)

A fresh verifier ran this round read-only, in a background Blender on port 9881 (`wip/M049_verify.blend`, not saved).
Every number below was re-measured with my own code (bmesh shells, BVH overlap and nearest, 3-ray parity), not taken
from `build()`'s report. Renders, side-by-sides and scripts are in the scratchpad folder `m049_verify/`:
- `sbs_34.png`, `sbs_ortho.png`, `sbs_tops.png`, `sbs_parts.png`, `sbs_cu.png`, `zoom_f34_top.png`, `cmp_conifers.png`;
- `prof.py` and `col.py`, which apply the study's own masks to both the sheet cells and the renders.

### Measured

| Check | Result | Target | |
| --- | --- | --- | --- |
| Tris: hero / T3 / T2 / T1U / T1L / Trunk / RootFoot | 3304 / 254 / 420 / 462 / 546 / 704 / 918 | ≤ 3600 / < 1000 / RootFoot ≤ 960 | ✓ |
| Shells: hero / parts | 138 / 11, 17, 19, 23, 1, 67 | | ✓ |
| Non-manifold edges, boundary, wire, loose, bowtie verts, zero-area, n-gons (all 7 objects) | 0 everywhere | 0 | ✓ |
| Winding errors (edges walked the same way by both faces) | 0 everywhere | 0 | ✓ |
| Shells with volume ≤ 0 / self-intersecting face pairs within a shell | 0 / 0 | 0 | ✓ |
| Smallest triangle corner | 2.15° (trunk) | > 2° | ✓ |
| Origin and transforms (every object) | origin at the bbox bottom centre (offset 0.000); rotation 0, scale 1; no modifiers; UVMap present, with 0 zero-area or out-of-range UV faces | | ✓ |
| Sizes (hero) | 19.45 × 16.99 × 22.00; canopy 16.8 × 17.0 | 22 ± 0.4; canopy 16.4 ± 0.6 | ✓ (17.0 at the limit) |
| Floating shells (> 0.03 from everything; overlap counts as contact) / unchained | hero 0 / 0; every part 0 / 0; worst gap 0.002 | 0 / 0 | ✓ |
| Dressing inside rock or trunk (ray parity on vertices, face centres and edge midpoints) | Leaves, hubs, lobes, pebbles, blades: **none inside at all**. The only overlap is the sand patch's top under the sunk rocks (0.08) and trunk (0.10), the intended seats. | ≤ 0.05 | ✓ |
| Blade-into-blade cut outside the cores | 65 touching pairs, deepest 0.050 | ≤ 0.05 | ✓ |
| Blade into a foreign core or the trunk | 0 | 0 | ✓ |
| Ring seats (sleeve to the rim or cap below, BVH nearest) | 0.015 × 4; no core / trunk / peg overlap | 0.015, pegs clear | ✓ |
| Blades | 66, all 18 tris (10 + 16 + 18 + 22) | | ✓ |
| Blade L : W (PCA box, whole / visible past the core) | Outer rows: T1L 1.95 / 1.87, T1U 2.25 / 2.11, T2 1.86 / 1.68, crown 2.49 / 1.62. **Inner rows: T1L 1.44, T1U 0.97, T2 1.04** (visible 0.37–0.77). | 2.6–3.0 (decision 4, §1.5) | ✗ |
| Lowest skirt tips | z 7.29–7.87 (the builder gives the front blade 7.17) | 6.8–7.7, above 5.5 | ✓ |
| Front-aimed blade per ring | T1L 273°, T1U 263°, T2 270.5°, crown 261°; crown ridges at 62 / 131 / 195 / 262 / 340° | 270 ± 4 | ~ |
| f34 shares | G 70.2, T 13.8, S 6.0, R 8.5 | G 69.1 ± 4, T 15.5 ± 4 | ✓ |
| f34 W : H (whole silhouette) | 0.744 | self-test 0.872–0.915 (0.82–0.92) | ✗ minor |
| Front / side / rear / r34 W : H | 0.830 / 0.719 / 0.818 / 0.764 | | ✓ |
| Top (0, 89) shares | G 94.1, S 2.3, R 2.0 | R ≥ 3 | ✗ minor |

**Hems and waists.** Canopy G width per height, as a fraction of the canopy's widest row; the same script ran on the
sheet and the render. Each cell gives sheet / ours.

| View | Crown hem (h / W) | Waist 1 (h / W) | Dip | Tier 2 hem (h / W) | Waist 2 (h / W) | Dip |
| --- | --- | --- | --- | --- | --- | --- |
| f34 | .82 / .38 / .83 / .33 | .79 / .29 / .78 / .32 | .09 / **.01** | .64 / .68 / .63 / .63 | .60 / .53 / .59 / .58 | .15 / **.05** |
| r34 | .81 / .35 / .83 / .34 | .75 / .31 / .79 / .32 | .04–.09 / **.02** | .62 / .66 / .63 / .66 | .58 / .49 / .60 / .62 | .17 / **.04** |
| front | .80 / .36 / .81 / .37 | .77 / .24 / .77 / .34 | .12 / **.03** | .61 / .67 / .64 / .70 | .57 / .47 / .60 / .55 | .20 / .15 |
| side | .78 / .38 / **no hem** | .75 / .27 / **no waist** (.33 .32 .31, monotonic) | .11 / **0** | .59 / .70 / .64 / .67 | .55 / .50 / .61 / .59 | .20 / **.08** |
| rear | .78 / .41 / **no hem** | .75 / .32 / **no waist** (.33 .31 .31) | .09 / **0** | .60 / .68 / .64 / .66 | .57 / .49 / .59 / .53 | .19 / .13 |

- The skirt hem (1.0) sits at h .39–.42, against the sheet's .36–.44: ✓.
- The f34 sub-step is a shoulder (.97 → .90, no second peak). The sheet's is a small second peak (.99 / .94 / .98).

**Colour** (study masks, ours | sheet):

| Region | f34 | front | side / rear / r34 |
| --- | --- | --- | --- |
| Canopy median | #4E8336 \| #528832 ✓ | #4D8034 \| #548D31 ✓ | #39632A / #3B6A2F / #3B6A2E \| #518B30 / #559031 / #478633 (15–20 dark) |
| Crown / T2 / skirt v | .596 / .596 / .502 \| .580 / .592 / .486 ✓ (lighter top, deeper skirt) | .580 / .557 / .478 ✓ | ✓ same order |
| Canopy v > .7 | 0.1 % of pixels \| 33 % (#B0CD34) | 0.4 % \| 33 % | about 0 % \| 28–36 % |
| Right / left half | #4C8033 / #4F8438 \| #A8C931 / #1D6933 | | |
| Trunk lit quartile | #C5722F \| lit-half target #C5712A ✓ | #C2712F | |
| Rock median / lit | #B6AB92 / #EAD6BD, R > G > B, G − B 25 ✓ (warm, not pink) | #B3A48D, G − B 23 ✓ | G − B 20–22 ✓ |
| Sand | #F1D2A1 \| #EFD3A1 ✓ | #F0D1A1 ✓ | |
| Plants (h < .3) | #5D7714, hue 71, v .47 \| #5B7F1D, 81, .50 | #597114 \| #567B1F | |

- **No lime cap:** the blade tip band equals the body, except on the crown's short blades ✓.
- **Facing:**
  - `K.check` reports no problems.
  - A grep of `m049.py` finds no `normal`-based paint selection. The only `.normal` is the shell-volume sum in
    `shells_report`.
  - My own luminance-against-normal correlation per family: needle −0.08, plant 0.03, bark 0.33, bush 0.40, rock 0.68.
  - Rock, bush and bark are painted in **height** bands, as the spec prescribes. `rock()` picks faces by
    `calc_center_median().z`, bushes go by lobe height, and bark by the ground band and the rim and peg cut faces.
  - The rock figure is high only because each rock's top band is its flat crown. Painting is by position, so ✓.

### Findings

1. **Blocker: the tiers merge (decision 3, §9 pitfall 2).**
   - **Waist 1.** The crown does not separate from Tier 2. Under the crown there is no waist in the side and rear views,
     and only a .01–.03 dip in the f34, r34 and front. The sheet's waist is .09–.12 deep, down to .24–.32 wide.
   - **Waist 2.** The Tier 2 / Tier 1 waist is only .04–.08 deep and .58–.62 wide in the f34, r34 and side. The
     sheet's is .15–.20 deep and .49–.53 wide.
   - **How it reads.** In the side and r34 renders the canopy is one continuous cone of hanging boards. The sheet's tiers
     read as three crisp, stepped umbrellas (`sbs_ortho.png`, `zoom_f34_top.png`).
   - **Cause, waist 1.** Tier 2's inner row fills the band just under the crown hem (z 17.3–17.6). Those blades are pads
     W 2.3–2.4 with tips at r 2.3–3.0, z 16.1–17.4.
   - **Cause, waist 2.** The T1U and T2 boards are 3.0–3.2 wide, so each edge sits about 1.5 to the side of the blade's
     axis. T1U's silhouette therefore already reaches about r 5 at the height of the T2 hem.
   - **Fix target.** Measure in the f34, front, side and rear renders, and loosely in the r34.
     - Waist 1 at h .77 ± .03, width ≤ .32, at least .07 narrower than the crown hem.
     - Waist 2 at h .58 ± .03, width ≤ .53, at least .12 narrower than the Tier 2 hem.
     - At z 16.8 the visible width must stay within r 2.4. Lower and shorten Tier 2's inner row (tips z ≤ 16.3,
       r ≤ 2.6), or seat it nearer the core.
     - Narrowing the boards (finding 2) clears waist 2.
     - A dark crease band should show under each hem.
2. **Blocker: the blades are broad shields and pads, not long boards (decision 4; the binding §1.5 "Foliage element"
   row).**
   - The outer rows measure L : W 1.86–2.25, and 1.68–2.11 visible past the core. Decided: 2.6–3.0.
   - The inner rows are square pads, L : W 0.97–1.44 (visible 0.37–0.77). Decision 4 says "not kites, paddles or pads".
   - The chisel ends are 0.26 W on blades 3–3.8 wide, so every tip reads as a rounded hexagon.
   - The parts shot shows bells of hanging shields, where the exploded view shows wide umbrellas of narrow blades
     (`sbs_parts.png`). This is the "steep tents" miss from W04 R7-7.
   - **Fix target.**
     - Outer blades at least 2.5 L : W visible. Widths: T1L about 2.6–2.8, T1U 2.3–2.5, T2 2.0–2.2, crown about 1.3.
     - Close any gaps with more blades, not more width. About 300 tris of headroom allows 16 more blades (+2 T1L and
       +2 T1U per the spec's §4.3 note).
     - Inner rows at least 2.0 L : W, with tips 0.35 W.
3. **Blocker: the top view is a round rosette, and the 5-ridge crown star does not read (binding §1.5 "Crown from
   above"; §2.5; §9 pitfall 14; W04 R7-6).**
   - In `top_sheet` and `sbs_tops.png` the crown is a small dark star about 0.15 of the canopy across, ringed by five
     lighter pads.
   - The outline is a ring of rounded hexagonal plate ends with no pointed star points.
   - 042 and 045 both read as a crisp central star from above, so the current 049 reads less like the sheet's star
     than they do.
   - **Fix target.**
     - The top render shows at least 11 pointed outer star points, with the second row's tips between them.
     - The 5-ridge crown star reads lime and spans at least 0.3 of the canopy. Its ridges show as distinct lit and shaded
       facet pairs.
     - Build it either from narrow crown blades on the ridges, or as the bare ridged cone with short hem blades, as in
       the exploded view's Tier 3.
     - Most of this follows from finding 2.
4. **Minor: from above, the rocks barely show past the skirt** (R 2.0 %, sheet 11 %).
   - **Fix target:** R at least 3 % in the top view. Push R4, R5 and R1 out to r ≥ 8.6 inside the patch, or enlarge R4.
5. **Minor: f34 W : H is 0.744** (sheet 0.87–0.92; the front's 0.830 is fine).
   - At az −15 the base reads narrower than the sheet's. On screen the sheet's patch is 1.29 × the canopy width; ours is
     1.08 ×.
   - **Fix target:** lengthen the patch along X toward ±10.5, or move BB and C2 outward.
6. **Minor: there is no lime lit side.**
   - The canopy's v > .7 share is 0.1 % (sheet 33 %), and the right and left halves are equal.
   - The side, rear and r34 canopy medians are 15–20 levels darker than the sheet's.
   - This is the studio's front-left key light, and painting it in would be colour by facing. Leave it as **Requires
     Manual Validation** under the Studio sun. The medians and the band order pass.
7. **Minor: the f34 sub-step is a shoulder** (.97 → .90), not the sheet's small second peak.
   - Re-measure after finding 2: narrower T1U boards should let T1U's tips stand out.
8. **Minor: the trunk is Ø ≈ 3.7 at z 5–7**, against the binding table's 3.2.
   - It is still clearly distinct from 042's 2.0, and the f34 T share passes.
9. **Minor: two small mismatches.**
   - T1U's front-aimed blade and the crown's front ridge sit 7–9° off −Y (jitter limit ±4).
   - In `ring_under` the sleeve hole doesn't read as a dark hole; close-up 1 shows one clearly.
10. **Passed; leave these alone in the fix.**
    - Mesh hygiene and winding.
    - Contacts: 0 floating, 0 unchained, nothing buried, seats 0.015, pegs clear.
    - The stack and joints.
    - The trunk: its seven roots are in one shell with it, and the rim, recess and peg match close-up 2 (`trunk_cu`).
    - The bush mounds, the clusters, the warm rocks and the sand.
    - The colour medians and blends.
    - Names, collision (hero precise, T1L and Trunk hull, RootFoot precise), no sockets, and the budgets.

**Decisions:**

| # | Decision | Status |
| --- | --- | --- |
| 1 | Size | ✓ |
| 2 | Names and keys | ✓ |
| 3 | Rings | **✗** The tiers merge (finding 1). The counts are right and the inner rows lie on top. |
| 4 | Blades | **✗** L : W is too low and the inner rows are pads (finding 2). 18 tris, parallel sides, cut-off tips and edge thickness are all right. |
| 5 | Tier 1 exported as two parts | ✓ |
| 6 | Joints, no floating dressing, winding, burial | ✓ |
| 7 | Roots | ✓ |
| 8 | Branches | ✓ |
| 9 | Dressing | ✓ |
| 10 | Cameras | ✓ |
| 11 | Colour | ✓ by position (lit half: finding 6) |
| 12 | Lighting and VFX skipped | ✓ |
| 13 | Collision | ✓ |
| 14 | Budget | ✓ |

**§1.5 differences from 042, 045 and 047** (`cmp_conifers.png`). 049 does read as a different kit piece from all three.

| Row | Status |
| --- | --- |
| Size | ✓ |
| Lowest tips | ✓ |
| Canopy pieces | ✓ |
| Joint | ✓ |
| Trunk | ✓ |
| f34 bark share | ✓ |
| Ground plants | ✓ |
| Rocks | ✓ |
| Silhouette | **✗** the crown and Tier 2 merge |
| Foliage element | **✗** shields and pads |
| Crown from above | **✗** no readable 5-ridge star |

### Score and verdict

**6 / 10.** The engineering is clean: mesh, winding, contacts, joints, stack, budget and colour medians all pass. The
canopy's defining read is missing: three stepped umbrellas of long, narrow blades that show a star from above.

**FAIL (round 1).**
- Blockers 1–3 go back to a fresh modeller for stages 1 and 4.
- Change only the ring and blade geometry. Then re-run the contact and winding checks, and re-calibrate if the blade
  areas change.
- Minors 4–9 can go in the same pass, or stay as leftovers.

## Fix round 1 (fix modeller, 2026-10-29)

A fresh fix modeller worked in a background Blender on port 9881 (`kit/wip/M049.blend`, saved after the final build).
Only the ring and blade geometry changed (stages 1 and 4), plus three of the verifier's cheap minors. The final build
ran in a freshly restarted session, and `build()`'s problems list is empty. Scratch scripts are in the scratchpad
folder `m049fix/`:
- `it2.py` / `tune.py` / `run.sh`: the tuning loop;
- `prof.py` and `fine.py`: the verifier's width profile and a 0.01 h table;
- `col.py`: the verifier's colour script;
- `lw.py`: blade L : W (whole and visible past the own core, the verifier's method);
- `geo.py`: the plan radius at given heights and the front blades' azimuths;
- `sil.py`: which shell sets the silhouette edge at a given screen height;
- `pts.py`: outer star points in the top views;
- `m049_round1.py` and `before/`: the round-1 builder and renders.

### What changed

1. **The tiers no longer merge (blocker 1).** This follows M045's fix round 1: row B on top, narrow waists.
   - **Every tier builds its inner row first.** The inner row lies on its core, with roots under the cap. The outer
     (hem) row is then built as a **sink row** under it: a blade that cuts the inner row has its tip turned down
     about its buried root. The inner row still lies on top (decision 3).
   - **The cores are steeper**, so the inner blades leave them early:
     - T1L rim r 3.4 @ 12.25 → 1.75 @ 13.2;
     - T1U 2.5 @ 14.0 → 2.0 @ 13.85;
     - T2 2.2 @ 16.6 → 1.7 @ 16.75.
   - **The rim has one corner per outer blade.** The 2n-corner pleat is gone. It is hidden under the blades, and its
     tris paid for the extra blades.
   - **The outer rows flare.** A new `bend=(deg at A, deg at B)` in `blade()` replaces the two-step droop. A negative
     first angle flares the blade up at A, so the waist above stays narrow while the hem keeps its width. The second
     angle droops the tip. Bends: T1L (−14, −4), T1U (−14, −6), T2 (−16, −6).
   - **Tier 2's inner row** is shorter and lower: root (0.55, 18.0) → tip (3.4, 15.2), W 1.35. Round 1 had pads lifted
     to z 16.1–17.4 just under the crown hem.
   - **The T1L inner row is lowered**: (0.6, 14.15) → (3.7, 11.2). This clears the T1U outer row, so the T1U blades
     are no longer lifted into waist 2.
   - **The T2 hem** sits at r 5.85 @ 13.3, with the front blade at 13.0.
2. **Blades, not shields or pads (blocker 2).**
   - **Widths:** outer T1L 2.8 / T1U 2.5 / T2 2.05 / crown 1.3; inner 1.3 / 1.5 / 1.35; crown short 0.9.
   - **Counts:** crown 5 + 5, Tier 2 10 + 10, T1U 12 + 11, T1L 14 + 13. That is 80 blades, 14 more than round 1.
   - **Tip:** section B moved to 0.72 L (was 0.75) and TIPW to 0.24 W (was 0.26). The sides are still parallel from A
     to B, and the tip is still cut off. It now reads pointed from above.
   - **Ridge:** a per-row `ridge` setting. The crown's long blades use 0.35 W for distinct lit and shaded halves; every
     other row keeps 0.08 W.
3. **Top-view star (blocker 3).**
   - **The crown cone is a deep five-ridge star:** ridges r 2.3, valleys 1.5, rim z 18.3 (was 2.0 / 1.45 / 18.6). It is
     painted base needle (was 25 % light).
   - **Five long, narrow, lime blades lie just above its ridges**, from the apex (root (0.05, 21.8)) to the hem tips at
     r 3.5 @ 17.3. Their tones are (0.25, 0.5, 0.5): no tip cap, the tip equals the body.
   - **The five short valley blades** are tucked under them: tips r 2.45 @ 17.7, W 0.9.
4. **Minors.**
   - **Rocks:** R1 moved to (−7.2, −1.0), R4 to (9.1, 3.7) at 2.4 × 2.0 × 1.6, R5 to (−8.4, 3.9) at 1.8 × 1.5 × 1.1.
     Pebble P3 moved to (−8.2, 1.2) so it stays on the patch crest.
   - **Sleeve holes:** a new key, `m049_hole` #2E1C10. The holes now read near-black in `ring_under`. This is the
     hole's own faces, a geometric region.
   - **Front blades:** every ring's front blade is now at 269–272°, and the crown ridge is at exactly 270°.
5. **Not changed:** the trunk, roots, bushes, clusters, the sand patch shape and the calibrated palette keys.
   - The needle keys were not re-calibrated: the dome calibration does not depend on blade area.
   - The rendered medians were re-measured instead (below). Only the crown band moved, deliberately, for the lime star.

### Measured (final build, fresh session)

Widths are fractions of the canopy's widest row; h is a fraction of the silhouette height. Both use the verifier's
`prof.py` on the `*_sheet` renders.

| Check | Round 1 | Fix round 1 | Target |
| --- | --- | --- | --- |
| Waist 1 h / W: f34 | .78 / .32, dip .01 | **.78 / .26**, crown hem .81 / .39, dip .13 | h .77 ± .03, W ≤ .32, ≥ .07 below the hem |
| Waist 1: r34 | .79 / .32, dip .02 | **.79 / .23**, hem .82 / .39, dip .16 | the same |
| Waist 1: front | .77 / .34, dip .03 | **.78 / .26**, hem .81 / .41, dip .15 | the same |
| Waist 1: side | none | **.79 / .22**, hem .81 / .38, dip .16 | the same |
| Waist 1: rear | none | **.78 / .25**, hem .81 / .41, dip .16 | the same |
| Waist 2 h / W: f34 | .59 / .58, dip .05 | **.60 / .49**, T2 hem .65 / .67, dip .18 | h .58 ± .03, W ≤ .53, ≥ .12 below the hem |
| Waist 2: r34 | .60 / .62, dip .04 | **.60 / .49**, hem .65 / .66, dip .17 | the same |
| Waist 2: front | .60 / .55 | **.61 / .46**, hem .64 / .69, dip .23 | the same |
| Waist 2: side | .61 / .59, dip .08 | **.60 / .49**, hem .64 / .67, dip .18 | the same |
| Waist 2: rear | .59 / .53 | **.59 / .47**, hem .64 / .69, dip .22 | the same |
| Visible plan r at z 16.8 / 17.0 / 17.4 | T2 inner tips r 2.3–3.0 there | **2.15** / 1.88 / 3.66 (crown hem) | ≤ 2.4 at 16.8 |
| Outer blade L : W, visible (min / mean), mean W | T1L 1.87 (W 3.8), T1U 2.11 (3.2), T2 1.68 (3.0), crown 1.62 (2.0) | **T1L 2.81 / 3.34 (W 2.63); T1U 2.90 / 3.19 (2.46); T2 2.58 / 2.74 (2.04); crown 3.70 / 4.00 (1.32)** | ≥ 2.5; W 2.6–2.8 / 2.3–2.5 / 2.0–2.2 / ≈ 1.3 |
| Inner blade L : W, whole (visible), min | T1L 1.44 (0.37), T1U 0.97, T2 1.04 (0.37–0.77) | **T1L 3.07 (2.01), T1U 2.70 (2.04), T2 2.71 (2.03)**; crown short 3.24 (2.31) | ≥ 2.0 |
| Blades | 66 | 80 (+14) | about +16 |
| Top: outer star points (`pts.py`) | 11, rounded hexagonal plate ends | **12, pointed** (sheet 13) | ≥ 11 pointed |
| Top: crown star | dark, about 0.15 across | **lime five-ridge star with lit / shaded ridges, about 0.38 across** (tips r 3.5) | lime, ≥ 0.3 |
| Top shares R / S | 2.0 / 2.3 | **3.2** / 4.6 | R ≥ 3; S ≤ 3 |
| f34 shares G / T / S / R | 70.2 / 13.8 / 6.0 / 8.5 | **67.6 / 14.6** / 7.1 / 8.9 | G 69.1 ± 4, T 15.5 ± 4 |
| f34 W : H (whole) | 0.744 | 0.807 | 0.82–0.92 |
| Front-aimed blade azimuth: crown / T2 / T1U / T1L | 261 / 270.5 / 263 / 273 | 268.7 / 272.2 / 271.6 / 271.6; crown ridge 270.0 | 270 ± 4 |
| Hero tris; parts T3 / T2 / T1U / T1L / Trunk / RootFoot | 3304; 254 / 420 / 462 / 546 / 704 / 918 | **3532**; 254 / 484 / 546 / 626 / 704 / 918 | ≤ 3600; < 1000; RootFoot ≤ 960 |

- **Mesh, all 7 objects:** `M.audit` reports 0 non-manifold edges, 0 bowtie verts, 0 boundary, 0 wire, 0 loose,
  0 zero-area faces and 0 n-gons; normals outward; origin at the bbox bottom centre. Per shell, every shell is closed
  with a positive volume, 0 self-intersections and **0 winding errors**. The smallest triangle corner is 2.15° (the
  trunk, unchanged).
- **Contact (`contact_report` and the verifier's 3-ray `analyse`):**
  - Hero 152 shells: floating 0, unchained 0, worst gap 0.002.
  - Ring seats 0.015 × 4, with 0 core / trunk intersections; `core_vs_below` 0 on every ring.
  - Blade-into-blade cuts are at most 0.049, with 0 pairs over 0.05. Blade fixes: 0 unresolved.
  - Leaf cuts 0; leaves dropped 0.
  - **Dressing buried: 0.** The only overlaps are the intended seats: the patch under the sunk rocks (0.08) and under
    the trunk (0.10).
  - Every part: floating 0, unchained 0.
- **Sizes:**
  - Hero 19.7 × 16.8 × 22.0, origin offset (0.32, 0.10, 0).
  - T3 6.8 × 6.4 × 4.8; T2 11.4 × 11.7 × 5.7; T1U 14.2 × 14.9 × 6.8; T1L 16.4 × 16.8 × 7.8.
  - The lowest skirt tips are at z 7.18 (the front blade) to 7.9.
- **Colour** (`col.py`, ours | sheet):
  - **f34:** canopy median #4D8333 | #528832 ✓; band v crown .631 | .580, T2 .612 | .592, skirt .490 | .486.
  - **front:** crown .588 | .561, T2 .584 | .584, skirt .475 | .525.
  - **The crown band is about .03–.05 lighter than the sheet.** This is the price of the lime star from above. The
    order (crown and T2 lighter than the skirt) holds.
  - **Lit share:** canopy v > .7 is now 4.6 % in the f34 (round 1: 0.1 %).
  - Rocks are still warm (G − B 19–25); plants are unchanged.
  - `K.check` reports no problems. Facing is never used.
- **Renders:** `M049_views.png`, `*_sheet`, `top_sheet`, `ring_under`, `exploded`, the parts, and `cmp_conifers.png`
  (042 / 045 / 047 / 049 at the f34 camera). From the f34 / front / side / rear, the canopy reads as a crown, Tier 2 and
  a double skirt, with a dark crease under each hem. From above it reads as a lime five-point star in a ring of
  pointed blade tips, with rocks peeking out at the left and right.

### Leftovers

- **The skirt reads spikier than the sheet.**
  - At the hems, the narrower boards with pointed tips leave notches between the tips, where the sheet draws closed
    fans of broad boards.
  - The parts shot shows steep bells: T1U part W : H 2.19 (exploded 2.57); T1L 2.15 (2.39).
  - Closing the notches needs more blades. The hero has 68 tris of headroom (3532 / 3600), about 3 blades.
- **The f34 sub-step is still a shoulder:** .95 at h .42, .89 at .45, against the sheet's second peak at .44.
- **The crown is slightly fat just above its hem in the side view:** .38 → .34 over h .81–.85, where the sheet goes
  .39 → .26. A concave crown (droop −14, rim z 18.0) was tried and changed nothing measurable, so it was reverted.
- **The T2 hem sits at h .64–.65** against the sheet's .59–.64. The side view is the furthest off: .64 against .59.
- **Sand shows more:** f34 S 7.1 (sheet 4.4 ± 2) and top S 4.6 (≤ 3). The rocks moved out, so the patch grew.
- **Unchanged from round 1:** the trunk (Ø ≈ 3.7); the studio-light darkening of the side, rear and r34 canopies
  (Requires Manual Validation under the Studio sun).

## Verification round 2 (verifier, 2026-10-29)

A fresh verifier ran this round read-only, in a background Blender on port 9881 (`wip/M049_verify.blend`, not saved:
its mtime is unchanged). Every number was re-measured with my own code, not taken from the fix modeller's report or
`build()`. Scripts, renders and side-by-sides are in the scratchpad folder `m049_verify2/`:
- `mesh.py` (per-object and per-shell audit), `contact.py` (BVH overlap and nearest, 3-ray parity), `blades.py` (PCA
  blade L : W, visible length past the own core, A / B widths, tip width);
- `prof2.py` (hems, waists and shares with the study's masks, on both the sheet cells and the renders), `col2.py`
  (colour), `pts.py` (top-view star points and radial colour);
- `sbs_34.png`, `sbs_ortho.png`, `sbs_top.png`, `sbs_parts.png`, `sbs_cu.png`, `big_sbs_f34.png`, `big_sbs_side.png`,
  `cmp_conifers.png`.

### Measured

| Check | Result | Target | |
| --- | --- | --- | --- |
| Tris: hero / T3 / T2 / T1U / T1L / Trunk / RootFoot | 3532 / 254 / 484 / 546 / 626 / 704 / 918 | ≤ 3600 / < 1000 / RootFoot ≤ 960 | ✓ |
| Shells: hero / parts | 152 (patch 1, trunk 1, cores 4, blades 80, rocks 5, pebbles 3, lobes 11, hubs 8, leaves 39) / 11, 21, 24, 28, 1, 67 | | ✓ |
| Non-manifold, boundary, wire, loose, bowtie verts, zero-area, quads / n-gons, duplicate verts (all 7 objects) | 0 everywhere | 0 | ✓ |
| Winding errors (an edge walked the same way by both its faces) | **0** on all 7 objects | 0 | ✓ |
| Shells with volume ≤ 0 / self-intersecting face pairs within a shell | 0 / 0 | 0 | ✓ |
| Smallest triangle corner | 2.15° (trunk) | > 2° | ✓ |
| Origin, transforms, modifiers, UV | bbox bottom centre at 0.000 on every object; rotation 0, scale 1; no modifiers; `UVMap` present | | ✓ |
| Sizes | hero 19.70 × 16.84 × 22.00; T1L (canopy) 16.44 × 16.84 | 22 ± 0.4; canopy 16.4 ± 0.6 | ✓ |
| Floating / unchained shells (> 0.03; overlap counts as contact) | hero 0 / 0, worst gap 0.002; every part 0 / 0 | 0 / 0 | ✓ |
| Buried dressing (leaves, hubs, lobes, pebbles and blades inside rock or trunk; parity on verts, face centres, edge midpoints) | **0.000**: nothing inside at all | ≤ 0.05 | ✓ |
| Ring seats (each core to the trunk or cap below) | 0.015 × 4, 0 overlapping face pairs | 0.015, pegs clear | ✓ |
| Blade-into-blade cuts | 70 touching pairs, deepest 0.049, 0 over 0.05 | ≤ 0.05 | ✓ |
| Blade into a foreign core or the trunk | 0: every blade enters only its own core | 0 | ✓ |
| Inner row on top (rays up from the inner blades' outer half, per ring part: T2 / T1U / T1L) | covered by an outer blade 0 / 30, 0 / 33, 0 / 39; inner tips over an outer blade 7 / 10, 11 / 11, 13 / 13 | inner on top | ✓ |
| Outer blades: mean W; L : W whole / **visible past the core** (min) | T1L 2.63; 2.87 / **2.81**. T1U 2.46; 2.90 / **2.69**. T2 2.04; 2.71 / **2.52**. Crown long 1.32; 4.07 / **3.50** | visible ≥ 2.5 | ✓ |
| Inner blades: L : W whole (min); visible past the core (min / mean) | T1L 3.07; 1.98 / 2.15. T1U 2.70; 1.84 / 2.08. T2 2.71; 1.90 / 2.07. Crown short 3.24; 2.48 / 2.58 | ≥ 2.0 | ✓ (means; a few at 1.84–1.98) |
| Parallel sides (width at B / width at A); tip | 1.00 on every blade; tip 0.24 W, flat | parallel; cut-off tip | ✓ |
| Front-aimed blade: crown / T2 / T1U / T1L | 271.5 / 269.7 / 269.1 / 269.1° | 270 ± 4 | ✓ |
| Lowest skirt tips | z 7.15–7.79 | 6.8–7.7, above 5.5 | ✓ |
| Top: outer star points (polar radius peaks, the same script on both images) | 11 (`top_sheet`), 12 (kit top); sheet 12 | ≥ 11, pointed | ✓ |
| Top: crown star | five long lime blades on the five ridges, tips at r 3.33–3.67 against the canopy's 7.9–8.5: **0.42** across; centre ring hue 86, v .59 (sheet 87, .60) | lime, ≥ 0.3 | ✓ |
| Top shares G / S / R | 87.5 / 4.6 / 3.2 (sheet 86.3 / 0 / 11.3) | R ≥ 3, S ≤ 3 | ✓ R; S minor |
| f34 shares G / T / S / R | 67.5 / 14.6 / **7.1** / 8.9 (sheet 69.0 / 15.5 / 4.4 / 8.7) | G 69.1 ± 4, T 15.5 ± 4, S ± 2 | ✓ G, T; S minor |
| f34 W : H (whole silhouette) | 0.811 (sheet 0.874) | 0.82–0.92 | minor |

**Waists.** G width per height, as a fraction of the canopy's widest row. The same script ran on both images; each
cell gives sheet | ours.

| View | Crown hem h / W | Waist 1 h / W / dip | Tier 2 hem h / W | Waist 2 h / W / dip |
| --- | --- | --- | --- | --- |
| f34 | .82 / .38 \| .81 / .39 | .80 / .27 / .11 \| **.78 / .26 / .13** | .64 / .68 \| .65 / .68 | .61 / .49 / .19 \| **.60 / .49 / .19** |
| r34 | .80 / .37 \| .82 / .39 | .76 / .29 / .08 \| **.79 / .23 / .16** | .61 / .67 \| .65 / .66 | .59 / .48 / .18 \| **.60 / .49 / .17** |
| front | .80 / .36 \| .81 / .41 | .78 / .24 / .11 \| **.78 / .26 / .16** | .61 / .67 \| .63 / .70 | .58 / .46 / .21 \| **.60 / .46 / .24** |
| side | .77 / .39 \| .82 / .37 | .75 / .27 / .12 \| **.79 / .22 / .16** | .58 / .70 \| .63 / .69 | .54 / .50 / .20 \| **.61 / .45 / .24** |
| rear | .78 / .41 \| .81 / .42 | .76 / .30 / .11 \| **.79 / .25 / .17** | .60 / .68 \| .64 / .69 | .57 / .49 / .19 \| **.60 / .47 / .22** |

- Every view meets the targets.
  - Waist 1 sits at h .78–.79 (target .77 ± .03), W .22–.26 (≤ .32), .13–.17 below the crown hem (≥ .07).
  - Waist 2 sits at h .60–.61 (.58 ± .03), W .45–.49 (≤ .53), .17–.24 below the Tier 2 hem (≥ .12).
  - The side and r34 renders read as a crown, Tier 2 and a skirt with a dark crease under each hem, not as one cone.
- The f34 skirt rows (h .36–.44) are .69 .99 .98 .94 1.00 on the sheet, a second peak at .44; ours are .77 .89 1.00
  .95 .91, a shoulder.
- Between the Tier 2 hem and the crown ours narrows faster (f34 h .66–.74: .64 .59 .52 .43 .36 against the sheet's .66
  .63 .59 .51 .44). Tier 2 is a steeper bell than the sheet's.

**Colour** (study masks; each cell gives sheet | ours):

| Region | f34 | front | side / rear / r34 |
| --- | --- | --- | --- |
| Canopy median | #528832 \| #4D8333 ✓ | #548D31 \| #497E30 ✓ | #518B30 / #559031 / #478633 \| #386527 / #3C6B2B / #3C6B2B (the studio light, as in round 1) |
| Band v, crown / T2 / skirt | .580 / .592 / .486 \| **.635** / .612 / .490 | .561 / .584 / .525 \| .592 / .584 / .475 | order kept |
| Canopy v > .7 share | 33 % \| 4.6 % (#9DC639) | 33 % \| 4.1 % | 28–36 % \| 0.1–0.2 % |
| Trunk lit quartile | #E68D38 (lit-half target #C5712A) \| #C5722F, hue 27 ✓ | #C2712F ✓ | |
| Rock median / lit | #AAA197 / #DACBB7 \| #C2B79E / #D7C8AF; R > G > B, G − B 25, hue 33 ✓ | G − B 25 ✓ | G − B 19–22 ✓ |
| Sand | #EFD3A1 \| #F1D3A2 ✓ | #F0D2A2 ✓ | |
| Plants (h < .3) | #5B7F1D, hue 81, v .50 \| #648215, hue 72, v .51 | #617D14, v .49 | v .52–.57 (not olive) |

- **No lime cap.** Per blade, the root / mid / tip materials are:
  - 27 × deep 50 / deep 25 / deep 25;
  - 23 × deep 50 / needle / needle;
  - 20 × deep 25 / light 25 / light 25;
  - 5 × light 25 / light 50 / light 50;
  - 5 × needle / light 25 / light 25.

  The tip always equals the body.
- **Hole key `#2E1C10`.** 88 faces carry it, 22 per core. Every one lies within r 0.555 of the axis and is either a
  hole wall facing the axis or the downward-facing ceiling. These are the blind hole's own faces, a geometric region ✓.
- **Facing.**
  - `K.check` reports no problems.
  - A grep of `m049.py` finds no `normal`-based paint selection. The only `.normal` uses are blade and leaf geometry
    and the shell-volume sum.
  - My own key-luminance against normal correlation: needle −0.09, plant 0.03, sand 0.33, bush 0.40, bark 0.46, rock
    0.68 (z).
  - The rock, bush and bark figures come from height bands and role faces. `rock()` picks faces by
    `calc_center_median().z`, bushes go by lobe height, and bark by the ground band, the rim and the peg's cut top.
    This is colour by position, so ✓.

### Findings

**No blockers.** The mesh, winding, contacts, burial, stack, budget and names all pass, and so do the three round-1
blockers.

1. **Minor: the skirt and Tier 2 read spikier than the sheet** (`big_sbs_f34.png`, `big_sbs_side.png`).
   - The sheet draws closed fans of broad overlapping boards with short scalloped hems. Ours are longer, narrower boards
     with notches between the tips, so the hems read as a ragged spray.
   - The crown reads as a tuft of five long flaring blades, where the sheet draws a solid ridged cone with a short hem.
   - **Fix target (a later pass):**
     - Close the hem notches: 2–3 more outer blades on T1L and T1U within the 68-tri headroom, or outer boards 5–8 %
       wider.
     - Give the crown cone more of the silhouette above z 19.5: lay the crown's long blades flatter on the ridges, with
       their tips no more than 0.3 proud.
2. **Minor: the parts read as steep bells** (`sbs_parts.png`).
   - Object W : H is close to the spec: T1L 2.09, T1U 2.08, T2 2.01, T3 1.41 (spec 2.4 / 2.25 / 1.9 / 1.24).
   - On screen at (−20, 20), though, the parts measure 1.31 / 1.24 / 1.28 / 1.03, against the exploded view's 2.39 /
     2.57 / 2.02 / 1.15. The blades hang steeply from a tall core peak.
   - **Fix target:** lower the core peaks and the blade root pitch by about 8–10°, so the T1L and T1U parts reach a
     screen W : H of at least 1.8.
3. **Minor: the crown band is lighter than the sheet.**
   - f34 v .635 against .580 (+.055); front +.031. The order (crown and T2 above the skirt) holds.
   - **Fix target:** crown long blades from tones (0.25, 0.5, 0.5) to (0, 0.25, 0.25), once the star has been judged in
     Studio.
4. **Minor: the f34 sub-step is a shoulder.**
   - Ours runs .89 → 1.00 → .95 → .91 over h .38–.44. The sheet has a second peak, .94 → 1.00 at h .44.
   - **Fix target:** T1U's outer tips 0.3 further out (r ≈ 7.7) or 0.3 lower.
5. **Minor: the Tier 2 hem sits high.**
   - It is at h .63–.65, against the sheet's .58–.64. The side view is the furthest off: .63 against .58.
   - **Fix target:** T2's outer tips from z 13.24 to about 12.8.
6. **Minor: sand shows more than on the sheet.**
   - f34 S is 7.1 (target 4.4 ± 2) and top S 4.6 (≤ 3). The f34 W : H is 0.811 (0.82–0.92).
   - **Fix target:** trim the patch bevel by 0.3–0.5 toward the camera, or bring the outer edge in where no rock sits.
7. **Minor: the inner rows' visible L : W** is 1.84–1.98 on a few blades (means 2.07–2.15; whole blades 2.7–3.3).
   - The rows read as boards in the renders. Leave this.
8. **Minor: the blade counts differ from decision 3's literal numbers.**
   - As built: crown 5 + 5, Tier 2 10 + 10, T1U 12 + 11, T1L 14 + 13. Decision 3: crown 10, Tier 2 8 + 8, T1U 9 + 9,
     T1L 11 + 11.
   - Round 1's fix target asked for more blades instead of more width, §4.3 allows it, and the sheet's top shows 12–13
     points.
   - Everything else in decision 3 holds: four rings, the inner row on top, a front-aimed blade, no merge, and a
     sub-step (as a shoulder).
   - Recommend the main session records the new counts as an accepted change to decision 3.
9. **Minor, unchanged, Requires Manual Validation:**
   - A sliver of the crown's bark sleeve shows under the crown hem in the side and f34 renders.
   - The lit lime share (4.6 % against 33 %) and the darker side, rear and r34 canopies come from the studio's
     front-left key light. Painting them in would be colour by facing. Check them under the Studio sun.

**Decisions:**

| # | Decision | Status |
| --- | --- | --- |
| 1 | Size: 22 tall, canopy 16.4–16.8, tips 7.15–7.8 | ✓ |
| 2 | Names `TallPine*`, keys `m049_*` | ✓ |
| 3 | Four rings, inner row on top, front blade, no merge, sub-step | ✓ (counts raised: finding 8) |
| 4 | 18-tri parallel-sided blades, cut-off tips, edge thickness, ridge; not pads | ✓ |
| 5 | Tier 1 as two parts | ✓ |
| 6 | Peg and sleeve, seats 0.015, one hero object, no floating dressing, 0 winding errors, no burial | ✓ |
| 7 | Seven roots in the trunk shell | ✓ |
| 8 | No branches | ✓ |
| 9 | Dressing: faceted bush mounds, upright broad-leaf clusters, not olive | ✓ |
| 10 | Cameras | ✓ |
| 11 | Colour: canopy median, band order, no lime cap, bark, warm rock, sand, never by facing | ✓ (crown band +.03–.05: finding 3) |
| 12 | Lighting and VFX skipped | ✓ |
| 13 | Collision: hero precise | ✓ |
| 14 | Budget: 3532 / 3600, RootFoot 918 | ✓ |

**§1.5 differences from 042, 045 and 047** (`cmp_conifers.png`, true scale, f34 camera). 049 reads as its own kit
piece:
- the tallest (22, against 16 / 10 / 20);
- a small crown over Tier 2 over a long double skirt;
- long parallel boards, where 042 has lime-tipped kites, 045 paddles and 047 lobe pads;
- a thick planked trunk, bare up to the skirt, with buttress roots;
- faceted bush mounds and pale warm rocks.

Every row passes: size, lowest tips, silhouette, canopy pieces, foliage element, crown from above, joint, trunk, f34
bark share, ground plants and rocks.

### Score and verdict

**7.5 / 10.** The round-1 blockers are fixed and measured in every view: two clean waists, long parallel boards, and
from above a pointed outline round a lime five-ridge star. The engineering is clean throughout. What remains is style:
the hems are spikier and the parts steeper than the sheet's closed umbrellas.

**PASS (round 2).** Commit with findings 1–9 noted as leftovers.

## Main session ruling (2026-10-29)
- **Result:** passed round 2 (7.5/10) and committed. Round 1 failed (6/10) on merged tiers, shield-shaped blades and a round top.
- **Decision 3 amended:** blade counts are now crown 5+5, T2 10+10, T1U 12+11, T1L 14+13. Round 1 asked for this, and §4.3 allows it.
- **Left for a later polish pass:**
  - The hems are spikier than the sheet's closed fans, and the crown reads as a tuft.
  - The parts read as steep bells.
  - The crown is +.055 lighter.
  - The f34 sub-step reads as a shoulder.
  - The T2 hem sits high.
  - The f34 sand share is 7.1 %.
- **Studio checks:** the crown sleeve sliver, and the lit lime share and darker back views, which come from the key light.
- **Export:** 7 assets, 7 solid pieces, 7064 tris, 0 VFX sockets, palette 27 colours, 0 problems.
