# 027 Reed Patch — spec

Reference: `art/blender/assets/references/027.png`. The sheet's own title is "REED PATCH", top line "FLINTBORN —
INDIVIDUAL MODEL STUDY, PAGE 26/132" (INDEX.md row 27 calls it "Flintborn reed patch study"; the page number on the
sheet is not the index number). The image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m027.py` → `build()`. Procedure: `art/blender/kit/mcp/STAGES.md` (one modeller does
stages 1–6 in a background Blender, then a fresh verifier does stage 7).

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7).

Sheet text:
- **Header:** "A small clump of reeds growing from a mud base. Built from simple, reusable parts. Stylized, chunky,
  low-poly aesthetic."
- **Material palette:** Seed Head "Plant (Dry)", Reed Leaf "Foliage", Reed Stalk "Plant Stem", Mud Base "Soil", Rock
  "Stone".
- **Views:** "Front Three-Quarter (Hero)", "Rear Three-Quarter", Front, Side, Rear, Top.
- **Exploded Construction:** labels Seed Head (part), Reed Stalk (part), Leaf Blade (part), Mud Base (part), Rock
  (part). The drawing shows **3 seed heads, 3 stalks, 8 leaves, 1 mud base, 5 rocks**, with dashed arrows from every
  stalk and leaf down into holes in the mud base's top and from the rocks into holes in its sides.
- **Construction close-ups:**
  - "Seed Head Connection": "Seed head fits over the top of the reed stalk. Simple cylindrical join for reuse across
    variants." (a short dark peg under the head over a hollow hexagonal stalk end).
  - "Leaf Base Junction": "Leaf blades and stalks insert into the mud base using simple cylindrical joins. Slightly
    angled for a natural spread." (also a tiny green sprig lying in a groove on the mud, §3.7).
  - "Base Underside": "Underside of mud base showing cylindrical sockets for reed stalks and leaves, and smaller sockets
    for rocks. Keeps assembly simple and reusable." (a flat faceted oval with 4 socket bosses).
- **Modeling notes:** "Built from a small set of reusable parts: seed head, reed stalk, leaf blade, mud base, rock.";
  "Keep forms chunky and readable with broad flat faces."; "Use clean, solid colors with no texture noise.";
  "Maintain clear silhouette and spacing between leaves."; "Rocks are optional detail pieces attached to the base.";
  "Geometry and proportions match the assembled views above."
- **Game context:** `src` has no reed node (`NodeCatalog.luau` lists `FiberPlant`, `HerbShrub`, the berry bushes,
  `ThornShrub`, mushrooms, ore and clay; the only "Reed" in `src` is the `ReedFerry` POI). WorldModeling §3.2:
  "Reeds / tall wetland plants 0.35–0.85 C, keep stalk count low and gaps visible". The old **R07** kit sheet has
  `ReedPatch` (7.6 W × 5.7 D × 7.2 H, 1004 tris, `harvest_hit` + `harvest_deplete`) and owns the `ReedPatch*` and
  `ReedStems` names (§8). MODEL_PROGRESS row R07: "mostly-done — thin dark blades; small seed heads"; its goals file
  (`art/blender/renders/kit/R07/reed_patch_goals.md`) logs three builds of edge-on, grass-like blades before the
  leaves read as broad. Sheet 117 (Cattail Clump, V04 `Cattail*`) and 135 (Stormreed, V09) are different plants.

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is about
`#F2EDE5` (242, 237, 229); each view's paper is the median of its box's top and bottom 4 rows. The masks are `cls()` in
`m.py` (HSV; background = within 18 of the paper). **The ground shadow is background**: it is pale grey (sat 0.05–0.06,
v 0.95) and lands in `bg` or `O`, never in the silhouette or the shares.
- **G, green (leaves + stalks):** sat ≥ 0.25, hue 55–165°, g > 35. Stalks and leaves are the same hue family in the
  renders (§5.2), so G is split only geometrically (stalk estimate, §1.2).
- **Brown/tan family B:** hue 5–45° (or ≥ 340°), sat ≥ 0.28, not G. In the elevation views B is split **by height**:
  above 0.42 of the silhouette height it is **S, seed heads** (body, shaded chamfers and the dark nubs); below it is
  **M, mud**. (By colour alone the heads' shaded bottom chamfers, sat 0.50 v 0.55–0.60, overlap lit mud.) In the top
  view: S = sat ≥ 0.48 and v ≥ 0.60, M = the rest of B (so the heads' dark faces and nubs fall into M there).
- **R, rock:** sat < 0.28, v < 0.80, not G or B, below 0.42 H (top view: anywhere). The warm right-back rock's faces
  partly fall into M; compare **M + R together** where noted.
- **O, other:** ground shadow, AA fringe, grey edge pixels above the base; not counted.

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m027_study\`.
Run with the scratch venv `...\scratchpad\venv22\Scripts\python.exe` (Pillow + numpy).
- **Helpers:** `m.py` (masks, view boxes `V`, `raw`, `cls`, `stats`), `bb.json` (silhouette boxes), `crops.py`,
  `gridcrop.py`, `zoom.py`.
- **Measurements:** `measure.py` → `measure_out.txt` (bboxes, shares, top profiles, width per height, region extents,
  shares per height band); `comps.py` → `comps_out.txt` (seed-head components per view); `base.py` → `base_out.txt`
  (base extents, rock runs, green runs per height); `stalk.py` → `stalk_out.txt` (visible stalk runs and share);
  `head.py` (head width profile along its axis); `expl.py` → `expl_out.txt` (exploded parts by PCA, width profiles);
  `leafn.py` → `leafn_out.txt` (leaf axes and face normals of the §2.3 layout).
- **Colour:** `probe.py` (swatches), `samp.py` → `samp_out.txt` (views, parts, close-ups, deciles), `grad.py` →
  `grad_out.txt` (leaf base → tip, stalks, heads bottom → top, height bands, leaf hue by light), `rocks.py` →
  `rocks_out.txt` (individual rocks, mud face).
- **Crops:** `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `cu1.png` (seed head
  connection), `cu2.png` (leaf base junction), `cu3.png` (base underside), `pal.png`, `notes.png`; grids `g_*.png` (10 %
  grid on the silhouette bbox); mask previews `cls_*.png` (magenta = O).
- **Zooms:** `z_f34_left.png` (LA, LB, LC, H1 stalk), `z_f34_right.png` (LG, LH, H3 stalk), `z_f34_base.png` (mud
  lumps and rocks).
- **To run the scripts on our renders,** set `M027_IMG=<render.png>` and `M027_BOXES='{"f34":[x0,y0,x1,y1],…}'`
  (one box per view, with the studio floor hidden, §4.2) and re-run `measure.py` (it rewrites `bb.json`), then
  `comps.py`, `base.py`, `stalk.py`, `samp.py`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a wetland plant / resource clump). Hero budget 4000 tris, each part under 1000. The
  plan in §4.4 lands at about 1500–2100 after the unions.
- **Overall read (check this first).** A **flattened fan** of broad, faceted, pointed leaves and three tan cattail heads
  on straight green stalks, rising from a low, lumpy brown mud mound ringed with grey rocks. Wider than tall from the
  front (hero W : H 1.20), **narrow from the side** (D : H 0.63):
  - **a low oval mud mound** (about 3.9 × 2.5 including the rocks, 0.6 high) made of a few big chunky lumps with
    vertical creases between them, a nearly flat top, and **four or five faceted grey rocks** half sunk into its rim
    (two at the left, one front right, one back right, one small at the back);
  - **three seed heads**, each a fat **8-sided faceted capsule** (body L : Ø about 2.0, chamfered both ends) with a
    short **dark-brown nub** on top, on a thin straight **6-sided stalk**. They splay outward: the left head H1 is the
    lowest and leans 22° left, the centre head H2 leans 13° left, the right head H3 leans 16° right; H2 and H3 reach the
    top;
  - **nine broad lance leaves** (W : L 0.18–0.26, keeled, thick-edged), fanning out of the mound top: one big leaf
    sweeping out to the left, two big leaves sweeping out to the right (upper and lower), and six shorter upright ones in
    the middle. They stop at 0.70–0.72 H, so **the heads and the upper stalks stand clear above the leaves**;
  - hero shares: green 54 % (leaves about 52, visible stalks at least 2), seed heads 19 %, mud 17 %, rock 9 %.
- **Focal silhouettes, in order:**
  1. Three tan capsules on stalks at three heights, separated by clear V-dips in the top profile.
  2. The leaf fan splaying out to both sides (tips at f 0 / h .60 and f 1 / h .45), pinched to a narrow neck where it
     leaves the mound (0.56 W at h .3).
  3. The wide low mound with its rocks, under everything.
- **Target size: about 5.3 W × 2.8 D × 4.4 H studs** (H = 0.80 of the 5.5-stud character, inside WorldModeling's
  0.35–0.85 C reed range; the heads stand at the character's chest/shoulder height). Tolerances W ±0.3, D ±0.35,
  H ±0.2. Decision §8.1.
  - **How it was derived.** The sheet has no character. The heads and leaves are the subject, so the height is set
    near the top of the design doc's reed range (reeds are taller than the 3.6-stud forage shrubs M017/M022/M024).
    The hero (416 × 347 px) then gives **78.9 px per stud**; the front cell (230 × 211) **48.0**, the side (138 × 218)
    **49.5**, the rear (212 × 217) **49.3**; the exploded parts about **82** (their heads are 49 px across against the
    hero's 47–52).
  - **Width:** hero W : H 1.199 → 5.27. The front cell draws the same composition narrower (1.09 → 4.8; §3.1); the hero
    governs.
  - **Depth:** side D : H 0.633 → 2.79; base depth 125 px = 2.52. The top view's base looks round (§3.4); the side and
    the rear three-quarter both say oval.
  - **Alternatives:** 0.65 C (× 0.82: 4.3 × 2.3 × 3.6, the forage-shrub height), or R07's scale (7.6 × 5.7 × 7.2, taller
    than the player and above the doc's reed range).
  - Resulting part sizes: head body Ø 0.55–0.65 × L 1.18–1.36 plus nub Ø 0.17–0.20 × 0.22–0.25; stalk Ø 0.25;
    leaves L 1.5–3.3 × W 0.40–0.70; mud mound 3.6 × 2.3 × 0.6 (3.9 × 2.5 with rocks); rocks Ø 0.6–0.9.
- **Build frame:** front −Y, +X right, ground z 0, origin = the mud mound's centre on the ground. The leaf fan reaches
  further right than left, so the bbox centre sits at about X +0.19 of the mound centre; stage 2 re-centres to the
  bbox bottom centre.
- **Stud mappings used below** (elevation correction ignored; tune on the renders):
  - hero (f34): X = (f − 0.465) × 5.27 (the mound centre is at f .465), z ≈ h × 4.4 (±0.15; the camera is about 14°
    up, so points at +Y draw a little higher);
  - front cell: shapes and heights only (it is the hero drawn narrower, §3.1);
  - side cell: Y = (f − 0.54) × 2.79 (the mound centre is at f .54), **screen right = +Y (the back)** for the kit side
    camera at az 90 (+X), §3.3;
  - rear, r34 and top: counts, shares and spread only (§3.2, §3.4).

### 1.2 Measured views (`measure.py`, `comps.py`, `stalk.py`)

| View (box) | Silhouette bbox (px) | W : H | Green G | Heads S | Mud M | Rock R | Heads / rocks / leaf tips visible |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (30,120,498,492) | 50–465 × 134–480 (416 × 347) | 1.199 | 54.5 % | 19.3 % | 17.1 % | 9.1 % | 3 / 4 / 9–10 |
| Rear three-quarter (500,120,808,492) | 504–783 × 137–475 (280 × 339) | 0.826 | 49.1 % | 22.0 % | 18.6 % | 10.3 % | 3 / 4 / 8 |
| Front (22,536,288,772) | 42–271 × 548–758 (230 × 211) | 1.090 | 53.8 % | 18.9 % | 18.6 % | 8.7 % | 3 / 4 / 9 |
| Side (293,536,490,772) | 319–456 × 546–763 (138 × 218) | 0.633 (D : H) | 56.1 % | 12.7 % | 21.1 % | 10.0 % | 2 (one partly hidden) / 3–4 / 7 |
| Rear (495,536,746,772) | 513–724 × 545–761 (212 × 217) | 0.977 | 51.9 % | 19.2 % | 21.6 % | 7.3 % | 3 / 3–4 / 8 |
| Top (752,536,1005,772) | 775–980 × 555–765 (206 × 211) | 0.976 (W : D) | 54.0 % | 12.9 % | 18.6 % | 14.5 % | 3 / 4–5 / 7 |

- **Visible stalks** (`stalk.py`, lower bound; a stalk run is counted only while it is no wider than 1.6 × the stalk):
  f34 1.7 %, r34 3.8 %, front 2.1 %, side 2.1 %, rear 1.4 %. So **leaves ≈ 52 % (f34), 45 % (r34), 52 % (front), 54 %
  (side), 50 % (rear)**. Stalk runs: hero H1 16 px wide visible from the head bottom h .55 down to h .46; H3 19 px from
  h .67 to h .55 as an isolated run and on down to about h .35 beside LG; H2 only between its head and the leaf tops.
- **Shares per height band** (f34; G / S / M / R, h 0 → 1): .0 0/0/.91/.09; .1 .12/0/.43/.45; .2 .80/0/.05/.15;
  .3–.4 1.0 G; .5 .92/.08; .6 .48/.52; .7 .03/.97; .8–.9 heads only. Front, rear and side follow the same bands (side
  .6 .78/.22, .7 .22/.78; rear .6 .27/.73).
- **Reading:** every elevation is 52–56 % green, 13–22 % heads and 26–31 % mud + rock. The side has less head (12.7 %)
  because two heads overlap; the top has more rock (rocks ring the mound and the leaves hide its centre).
- **Verifier tolerance:** shares ±4 points (top ±6; M and R also as M + R ±4, since the rock/mud split depends on rock
  colour); profile values ±0.07 h; positions ±0.06 of W/H unless stated.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .60 | .60 | .60 | .57 | .84 | .78 | .68 | .90 | .94 | .90 | .71 | .62 | .86 | .95 | 1.0 | .67 | .70 | .71 | .50 | .47 | .45 |
| Front | .66 | .65 | .64 | .75 | .84 | .80 | .69 | .91 | 1.0 | .93 | .76 | .66 | .79 | .92 | .96 | .99 | .68 | .70 | .71 | .48 | .46 |
| Side | .62 | .62 | .61 | .61 | .59 | .57 | .69 | .73 | .72 | .69 | .88 | .93 | .97 | 1.0 | .93 | .64 | .68 | .71 | .73 | .76 | .56 |
| Rear | .61 | .60 | .59 | .57 | .88 | .85 | .82 | .72 | .54 | .91 | 1.0 | 1.0 | .54 | .73 | .82 | .87 | .88 | .59 | .61 | .61 | .62 |
| r34 | .62 | .61 | .60 | .58 | .83 | .78 | .76 | .68 | .59 | .93 | 1.0 | .94 | .89 | .76 | .86 | .87 | .92 | .56 | .58 | .59 | .59 |
| Top (h = back) | .75 | .75 | .75 | .75 | .76 | .83 | .86 | .86 | .88 | 1.0 | .94 | .91 | .92 | .90 | .87 | .84 | .85 | .87 | .67 | .62 | .24 |

- **Three head peaks with V-dips between them** in every elevation: f34 peaks .84 (f .20, H1), .94 (f .40, H2),
  1.0 (f .70, H3); dips .68 (f .30) and .62 (f .55). The dips are the leaf-top level, so **the heads clear the leaves
  by 0.15–0.3 H**. Stage 1 must reproduce three peaks with dips ≥ 0.15 h between them in f34_sheet and front_sheet.
- **Leaf shoulders:** f34 f 0–.15 flat at .57–.60 (LA's tip and upper edge), f .75–.85 at .67–.71 (LG), f .90–1.0
  falling .50 → .45 (LH's tip).

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .24@.34 .74@.09 .66@.12 .56@.18 .75@.12 .83@.06 .81@.00 .70@.17 .54@.18 .37@.35 .02@.68
front  .29@.32 .81@.07 .73@.10 .63@.17 .78@.12 .72@.08 .83@.03 .77@.16 .58@.17 .41@.35 .37@.37
side   .41@.33 .91@.09 .75@.17 .55@.26 .65@.21 .81@.13 .91@.01 .64@.31 .22@.50 .21@.51 .06@.61
rear   .32@.33 .84@.07 .75@.11 .63@.17 .75@.11 .86@.06 1.00@.00 .58@.20 .60@.20 .14@.45 .04@.50
r34    .28@.36 .88@.05 .78@.10 .62@.19 .74@.13 .85@.07 .70@.01 .62@.17 .65@.19 .39@.43 .05@.47
top    .01@.32 .43@.27 .67@.17 .85@.11 .93@.01 .88@.11 .88@.11 .86@.02 .62@.23 .23@.42 .01@.44
```

So every elevation has the same shape: the mound wide at h .1 (0.74–0.91 W), a **neck at h .3** (0.55–0.63 W) where
the leaves leave the mound, the fan widening to 0.81–1.0 W at h .5–.6 (the leaf tips), then only the heads above h .7.
**A column of upright leaves (no neck, no splay) fails this.**

**Base, rock and green runs** (`base.py`; f ranges at a given h):

```
base (M|R) widest   f34 h .10 .09-.82 (306 px = 3.88 st)   front h .10 .07-.87   side h .10 .09-.99 (125 px = 2.52 st)   rear h .10 .07-.90
base at the ground  f34 h .02 .20-.73                       front h .02 .17-.80   side h .02 .17-.93
rocks h .16         f34 .10-.20 | .21-.36 | .61-.74          front .08-.17 | .19-.33 | .64-.78   side .12-.39 | .41-.54 | .78-.91   rear .09-.19 | .21-.36 | .75-.83
green h .55         f34 .03-.18 (LA) | .29-.30 (H1 stalk) | .34-.39 (LB) | .43-.56 (LE, LF, H2 stalk) | .58-.62 (H3 stalk) | .63-.78 (LG)
                    front .06-.20 | .26-.29 | .33-.40 | .44-.57 | .59-.64 | .67-.82
                    side  .09-.25 (front leaf) | .33-.38 | .46-.51 | .54-.62 | .67-.88 (back leaves) | .93-.97
                    rear  .03-.15 | .28-.35 | .41-.59 | .64-.71 | .81-.95
green h .50         f34 .07-.23 | .27-.31 | .33-.42 | .44-.56 | .57-.76 | .87-.88     rear .07-.23 | .28-.37 | .40-.59 | .62-.71 | .75-.91
green h .40         f34 .13-.28 | .29-.85    front .13-.75 | .77-.89    side .21-.85    rear .12-.85
```

- At h .5–.55 the fan is **5–6 separate green runs with paper between them** in every elevation ("spacing between
  leaves"); by h .4 they merge into one mass.
- **Stage 1 target:** f34_sheet and front_sheet h .55 show the H3 stalk as its own run (0.03–0.05 W) between the centre
  leaves and LG, and 5–6 runs in all; side_sheet h .55 shows a front leaf run ≥ 0.12 W and a back leaf run ≥ 0.15 W.

**Seed-head components** (`comps.py`; centre (f, h), extents incl. the nub, PCA axis from +x, length × width in px):

| View | Heads |
| --- | --- |
| f34 | H1 (.24,.68) f .17–.31 h .54–.84, axis 112°, 90 × 41; H2 (.41,.78) f .33–.49 h .62–.98, 103°, 109 × 47; H3 (.65,.81) f .57–.73 h .66–1.0, 74°, 102 × 48 |
| front | H1 (.23,.70) f .15–.31 h .56–.85, 111°; H2 (.42,.81) f .34–.50 h .64–1.0, 101°; H3 (.68,.81) f .59–.76 h .66–1.0, 73° |
| side | low head partly hidden behind a leaf (.40,.59) f .37–.44 h .55–.65; tall head (.61,.81) f .49–.73 h .66–1.0, 85° |
| rear | (.27,.72) f .18–.36 h .59–.88, 109°; (.51,.82) f .44–.58 h .67–1.0, 88°; (.72,.73) f .63–.80 h .60–.88, 69° |
| r34 | (.27,.67) f .17–.38 h .54–.83, 110°; (.52,.81) f .42–.62 h .65–1.0, 96°; (.74,.77) f .64–.83 h .64–.92, 72° |
| top | (.37,.45) f .25–.47 h .35–.55, nub pointing −X; (.64,.31) f .54–.74 h .20–.42, nub pointing +X and front; (.71,.60) f .63–.83 h .50–.72, nub pointing +X and back |

- Heads lean outward; their L : W including the nub is 2.10–2.32 in every elevation.
- **Head anatomy** (`head.py`, width along the axis, exploded heads 119–122 px long): bottom peg 11 px wide × 10 long
  (0.22 W, dark); bottom chamfer 31 → 44 px over about 15 px; straight body 46–49 px wide over about 65 px; top chamfer
  44 → 29 over 15 px; nub 13–14 px wide × 15–20 long (0.28 W, dark brown). Hero H2: body 50–52 px, top chamfer
  47 → 28, nub 15 px × 4 bins. So **body (chamfer to chamfer) L : Ø ≈ 2.0, chamfers ≈ 0.15 of the body each, nub Ø ≈
  0.3 × body Ø and as long as 0.35–0.4 × body Ø.**

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, governs; `g_f34.png`).** Like M020/M022/M024's, it is **not** a three-quarter view:
the mound is centred and symmetric, and every head and leaf tip sits at the front cell's fractions (heads within ±0.03,
§1.2). The camera is on the front axis, a little higher than the front cell (the mound's top shows between the leaf
bases), e ≈ 14° (§3.1).
- **Heads:** H1 left, lowest (nub top h .84), smaller (body Ø ≈ 0.55), leaning 22° left; H2 just left of centre, tall
  (h .98), the biggest (Ø ≈ 0.65), leaning 13° left; H3 right, the highest point (h 1.0), Ø ≈ 0.62, leaning 16° right.
  Each is an 8-sided capsule with 3–4 facet columns showing, a horizontal facet break about mid-body, chamfered ends and
  a dark nub; the bottom chamfer is in shade.
- **Stalks:** straight 6-sided green rods, Ø ≈ 0.4 × the head (16–19 px = 0.20–0.24 studs at 78.9 px/stud), visible
  between each head and the leaf tops (H1 f .26–.30 h .46–.54; H3 f .58–.62 h .35–.66, long and clear; H2 short).
  They converge downward to the mound centre (each stalk's line runs back to within 0.35 of the centre at the mound top).
- **Leaves (`z_f34_left.png`, `z_f34_right.png`):**
  - LA: a big leaf sweeping out to the left, tip at f 0 h .60, its broad face toward the camera, a slight arch, an
    oblique knife tip; about 0.55 studs wide as drawn;
  - LB: a tall inner-left leaf behind H1's stalk, tip f .335 h .61;
  - LC: a short front-left blade, tip f .325 h .465 (a narrow blade tip shows just behind it at f .28 h .46);
  - LD: a short front-centre blade, tip f .44 h .42;
  - LE: a small centre blade, tip f .49 h .53;
  - LF: the tall centre leaf, tip f .51 h .71;
  - LG: a big upper-right leaf, tip f .87 h .70, broad, slightly arched;
  - LH: a big lower-right leaf, tip f 1.0 h .44, the widest-reaching element;
  - LI: a darker inner-right leaf behind LF and the H3 stalk, tip about f .60 h .57.
  - Every leaf is a broad lance with a **visible midrib fold** (two facet planes of different shade either side of a
    keel) and 2–3 long facets per half; edges thick enough to read at the tips.
- **Mound (`z_f34_base.png`):** 3–4 chunky lumps across the front (a big centre-front lump, one under each front rock)
  with vertical creases, a slightly lower flat top, and a small bottom chamfer. Rocks: RK1 dark grey far left (f .10–.20,
  behind), RK2 light grey front left (f .21–.36), RK3 light grey front right (f .61–.74), RK4 grey back right (f .75–.85,
  just above the right edge). Each rock is a faceted boulder with 8–14 visible facets, half sunk into the rim.

**Front (`g_front.png`).** The same drawing at e ≈ 10° and drawn narrower (W : H 1.09; leaf tips at f 0 h .66 and
f 1.0 h .46). Use it for heights and the profile shapes; compare with an extra `front_sheet (0, 10)`.

**Side (`g_side.png`; kit camera at +X, screen right = +Y, the back).** Narrow (D : H 0.633).
- **Heads:** one tall head at f .49–.73 (centre Y +0.2, top h 1.0: H3, nearest this camera, with H2 behind it) and a
  lower head at f .37–.50 half hidden behind a leaf tip (Y −0.4: H1). §3.3.
- **Leaves:** a broad front leaf to f 0 at h .61 (Y −1.5, z 2.7: LA), an inner front tip at f .32 h .73 (Y −0.6,
  z 3.2: LF), two broad back leaves to f .94 h .73 (Y +1.1, z 3.2: LG) and f .99 h .63 (Y +1.25, z 2.8: LB), shorter
  blades in the middle. **The leaves read broad from the side too** (front run .16 W, back run .21 W at h .55).
- **Mound:** f .09–.99 at h .1 (2.52 deep), rocks at front (f .12–.39, two), centre (f .41–.54) and back (f .78–.91).

**Rear (`g_rear.png`; screen right = −X).** The front's composition seen from behind, drawn almost symmetric: heads at
f .27 (h .88), .51 (1.0), .72 (.88); 8 leaf tips; rocks two at screen left, one at screen right. §3.2.

**Rear three-quarter (`g_r34.png`).** Narrower (W : H 0.826, a real three-quarter turn of the flat fan), three heads
(low one at screen left), rocks far left, left, centre and right. Its heads and rocks disagree on which side the camera
is (§3.2): compare by counts and shares.

**Top (`g_top.png`; image top = back by kit convention).** A round mound ringed by 4–5 rocks (back left, front left,
front centre, right, a small one back right); a **star of 7 leaf tips** (back, back-left, left, front-left, front-right,
right, back-right); the three heads near the middle seen nearly end-on (L : W 1.2–1.3) with their nubs pointing outward
(left head → −X, front-right head → +X and front, back-right head → +X and back). Drawn from about 75–85° up. Its round
base and its 360° star conflict with the side (§3.4).

**Close-ups.**
- **Seed Head Connection (cu1, 620,848,822,996):** the head's bottom: an 8-sided body, a two-step bottom chamfer, a
  short dark **peg** (Ø ≈ 0.22 of the head, 10 px) that drops into the **hollow** hexagonal stalk end (dashed arrow).
  Head `#D99D5E`, stalk `#7B9030`, peg `#5B4427`.
- **Leaf Base Junction (cu2, 620,1008,822,1144):** four leaf/stalk bases standing in the flat mud top, the mud lumpy
  with broad facets, a grey rock on the rim; a tiny dark-green sprig lies in a groove (not in any assembled view, §3.7).
- **Base Underside (cu3, 620,1156,822,1316):** a flat oval bottom inside a ring of 14–16 side facets, four round socket
  bosses with holes (notation, §3.6). Underside `#614931` (in shade).

### 1.4 Parts (Exploded Construction (18,810,606,1522), `expl.png`, `expl_out.txt`)

Scale: about 82 px per stud (head Ø 49 px = 0.6). Facet language: broad flat-shaded facets, chunky, no noise.

#### Seed Head ×3: (213,863,272,982), (320,840,371,958), (403,859,468,975), about 120 × 49 px; close-up cu1

- **Shape:** an **8-sided faceted capsule**: bottom peg (Ø 0.22 W, 0.08 L), bottom chamfer (Ø 0.65 → 1.0 over 0.13 of
  the length), straight body (0.55 of the length, a mid ring with ±4 % radius jitter so the facets break into two rows),
  top chamfer (1.0 → 0.6 over 0.13), and a **nub**: 6–8 sides, Ø 0.28–0.3 × the body, 0.15–0.18 of the total length,
  a flat top, slightly tapered. The heads in the exploded and the hero are the same shape; only the size differs.
- **Size (hero governs):** H2 body Ø 0.65 × 1.36 (chamfers included) + nub Ø 0.20 × 0.25; H3 Ø 0.62 × 1.32 + 0.20 ×
  0.24; H1 Ø 0.55 × 1.18 + 0.17 × 0.22. The part = H2 with its bottom peg (Ø 0.14 × 0.12).
- **Construction:** `_seed_head(d, body_l, nub_d, nub_l, seed, peg=False)`: rings (t, r) = (0, 0.62), (0.13, 1.0),
  (0.5, 1.03), (0.87, 1.0), (1.0, 0.60) × d/2, 8 sides, ring twist ±6° by seed; a flat top ring under the nub; the nub a
  6-sided prism tapered 10 % with a flat cap; optional peg. **About 100 tris** (8 × 4 × 2 = 64 body, caps 12, nub 18,
  peg 14 on the part only).

#### Reed Stalk ×3: (245,1000,300,1125), (320,980,355,1095), (370,995,425,1110), about 110 × 21 px

- **Shape:** a straight **6-sided prism**, Ø 0.25 (0.42 × the head), uniform, a flat end at each end (the close-up's
  hollow top is notation, §3.6). The exploded stalks are shortened (110 px ≈ 1.35 studs); the hero stalks run 2.3–2.65
  from inside the mound to inside the head bottom.
- **Construction:** `_stalk(p0, p1, d=0.25, seed)`: 6 sides, 2 segments (a ring at 0.45 with ±3 % jitter), flat caps.
  **About 32 tris.** The exported part = the H2 stalk (Ø 0.25 × 2.45).

#### Leaf Blade ×8 in the exploded: far-left part (77,1095,209,1262) 205 × 50 px; left tall (123,1004,238,1178) 203 × 37; right up (405,1091,517,1222) 163 × 43; right low (423,1162,561,1288) 178 × 41; four in the centre group (245,1106,416,1304)

- **Shape:** a broad **lance**: W : L 0.18–0.26; width profile base → tip (fraction of max, 10 steps, far-left part)
  **0.68 0.77 0.86 0.95 1.00 1.00 0.97 0.84 0.67 0.42**, i.e. already 0.7 wide at the base, widest at 0.4–0.65 L,
  tapering over the last 30 % to a **sharp, slightly oblique tip** (the tip vertex offset 0.15–0.25 W to one side). Outer
  leaves arch 15–30° over their length (tip falling outward); centre leaves are nearly straight (≤ 10°).
- **Section:** a **keeled lens**: a midrib fold along the centre (front face two planes meeting at about 150°, back face
  a lower single ridge), keel thickness about 0.13 W (0.06–0.09 studs), edge thickness about 0.03 so the edges never go
  paper-thin. 2–3 long facets per half from the 5–6 width stations; no serration, no noise.
- **Size:** the part = the far-left exploded leaf: **L 2.5 × W 0.6** (W : L 0.24), arched 25°. Hero leaves in §2.3
  (L 1.5–3.3, W 0.40–0.70).
- **Construction:** `_leaf(L, W, arch, twist, seed)`: stations at t 0, 0.15, 0.4, 0.62, 0.82, 1.0 with half-widths
  0.34, 0.40, 0.50, 0.49, 0.36, 0 × W (±4 % jitter); a midrib vertex per station raised 0.6 × the keel on the front and
  0.4 × on the back; the tip vertex offset sideways by seed; **twist 15–25°** from base to tip about the leaf axis (the
  sheet's leaves turn as they rise, which keeps them broad from more than one side); arch by bending the stations in
  the leaf's own plane. **About 44 tris** (5 segments × 2 faces × 4 + tip). Use this, **not** `K.leaf` (shallow ovate,
  folded card) or `NS["leaf"]` (narrow, serrated).

#### Mud Base ×1: (185,1312,462,1460), 277 × 146 px (perspective)

- **Shape:** a low **oval mound**, 3.6 × 2.3, 0.55–0.65 high at the front rim rising to about 0.75 in two back lumps;
  side band of 14–16 broad facets that bulge into **3–5 lumps** (alternating radius ±8 % with a crease between lumps);
  a small bottom chamfer (the ground ring at 0.94 of the max radius); the top nearly flat, sloping 0.05–0.1 down from
  the rim into a shallow dish (0.45–0.5) where the leaves and stalks stand. The exploded holes and the underside sockets
  are notation (§3.6).
- **Construction:** `_mud_base(rx, ry, h, n=16, seed)`: rings (z, r) = (0, 0.94), (0.12, 1.0), (0.40, 0.98 with the lump
  bulges), (0.58, 0.88, the rim, per-vertex height ±0.06 and two back lumps +0.15), (0.50, 0.55, the dish ring), centre
  vertex at 0.46; flat bottom cap. **About 180 tris.** The exported part = the same call with its rock seats empty.

#### Rock ×5: (98,1319,174,1380) 76 × 61 px, (105,1393,206,1475) 104 × 78, (412,1387,450,1430) 47 × 35, (418,1429,522,1498) 104 × 69, (480,1391,539,1446) 61 × 47

- **Shape:** chunky faceted boulders, slightly flattened (H about 0.75 × the width), 8–14 facets visible, flat bottom.
  Exploded sizes at 82 px/stud: 0.93, 1.27, 0.57, 1.27, 0.74 across; the hero's are 0.6–0.9 across showing (half sunk).
- **Construction:** `K.hull_rock(a, size, loc, seed, mat, keep_bottom=True)` with 3 rings of 5–7 points (≈ 30–40 tris).
  The exported part = a 0.9 × 0.8 × 0.65 rock.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, origin = the mound centre). Azimuths from +X counter-clockwise
(front = 270°, back = 90°); elevation = rise from horizontal.

### 2.1 Mud base and rocks

| Piece | Centre (x, y) | Size | Sheet evidence |
| --- | --- | --- | --- |
| Mud mound | (0, 0) | 3.6 × 2.3, rim 0.6 (front) to 0.75 (two back lumps), dish 0.46 | f34/front widest h .1 at 3.85 with rocks; side 2.52 deep; front rim h .13–.15 |
| RK1 dark, left | (−1.65, +0.2), z 0.25 | 0.75 × 0.7 × 0.6 | f34 rock run f .10–.20 at h .16 (behind RK2); top back-left rock |
| RK2 light, front left | (−0.95, −0.9), z 0.2 | 0.85 × 0.75 × 0.65 | f34 f .21–.36 (X −1.34 … −0.55), top at h .25; side front rocks |
| RK3 light, front right | (+1.1, −0.8), z 0.2 | 0.75 × 0.65 × 0.6 | f34 f .61–.74 (X +0.77 … +1.45) |
| RK4 grey, back right | (+1.55, +0.45), z 0.25 | 0.7 × 0.65 × 0.6 | f34 f .75–.85 above the right edge; side back rock f .78–.91; top right rock |
| RK5 small, back | (−0.3, +1.05), z 0.2 | 0.6 × 0.55 × 0.45 | the exploded's 5th rock; top front-centre/back rock; rear |

- Each rock sinks 30–40 % of its height into the mound's side/rim; rock tops at z 0.85–1.05.
- RK1 uses `rock_dark`; the others `rock` (§5.4).
- Footprint with rocks: X −2.0 … +1.9, Y −1.25 … +1.3 (3.9 × 2.55).

### 2.2 Stalks and seed heads

| Head | Stalk from (inside the mound) | Head bottom (stalk top) | Lean | Body Ø × L, nub Ø × L | Nub top z | Sheet evidence |
| --- | --- | --- | --- | --- | --- | --- |
| H1 left, low | (−0.20, −0.15, 0.30) | (−1.05, −0.35, 2.42) | 22° toward −X | 0.55 × 1.18, 0.17 × 0.22 | 3.72 | f34 (.24,.68), top h .84, axis 112°; side low head Y −0.4 |
| H2 centre | (+0.30, −0.10, 0.30) | (−0.20, +0.10, 2.72) | 13° toward −X | 0.65 × 1.36, 0.20 × 0.25 | 4.30 | f34 (.41,.78), top .98, axis 103°; hidden behind H3 from the side |
| H3 right | (+0.15, +0.30, 0.30) | (+0.82, +0.20, 2.85) | 16° toward +X | 0.62 × 1.32, 0.20 × 0.24 | 4.38 | f34 (.65,.81), top 1.0, axis 74°; side tall head Y +0.2 |

- **Each head is coaxial with its stalk**; the stalk top sinks 0.12 into the head's bottom (the peg is hidden).
- Stalk Ø 0.25, 6 sides; stalks are 2.3–2.65 long and at least 0.4 apart everywhere (S2 and S3 cross in front view
  but are 0.43–0.5 apart in depth).
- Expected head centres in the hero: H1 X −1.31 (f .22), H2 X −0.38 (f .39), H3 X +1.03 (f .66).

### 2.3 Leaves (9 copies of `_leaf`, each with its own seed)

| Leaf | Base (z 0.45, in the dish) | Tip | L × W | Axis az / el | Face normal (start) | Arch | Sheet evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LA left, big | (−0.45, −0.20) | (−2.45, −1.20, 2.65) | 3.15 × 0.70 | 207° / 45° | (+0.67, −0.67, +0.31) | 25° | f34 tip f 0 h .60; side front leaf to Y −1.5 |
| LB inner left, tall, back | (−0.25, +0.20) | (−0.75, +1.25, 2.75) | 2.6 × 0.55 | 115° / 63° | (−0.70, −0.70, +0.17) | 10° | f34 tip f .335 h .61; side back tip f .99 h .63 |
| LC front left, short | (−0.30, −0.35) | (−0.75, −0.75, 2.05) | 1.7 × 0.45 | 222° / 69° | (+0.71, −0.71, +0.02) | 5° | f34 tip f .325 h .465 |
| LD front centre, short | (−0.05, −0.45) | (−0.15, −0.90, 1.85) | 1.5 × 0.40 | 257° / 72° | (−0.69, +0.70, +0.17) | 5° | f34 tip f .44 h .42 |
| LE centre, small | (+0.10, −0.20) | (+0.12, −0.45, 2.35) | 1.9 × 0.45 | 275° / 82° | (+0.71, +0.70, +0.08) | 0° | f34 tip f .49 h .53 |
| LF centre, tall | (+0.10, −0.05) | (+0.25, −0.60, 3.15) | 2.75 × 0.55 | 285° / 78° | (+0.70, +0.71, +0.10) | 5° | f34 tip f .51 h .71; side inner tip Y −0.6 z 3.2 |
| LG right upper, big | (+0.35, +0.15) | (+2.15, +1.10, 3.05) | 3.3 × 0.70 | 28° / 52° | (−0.69, +0.69, +0.23) | 20° | f34 tip f .87 h .70; side back tip f .94 h .73 |
| LH right lower, big | (+0.40, −0.10) | (+2.85, −0.35, 1.95) | 2.9 × 0.70 | 354° / 31° | (−0.49, −0.50, +0.72) | 25° | f34 tip f 1.0 h .44 (the right extreme) |
| LI inner right, back | (+0.25, +0.25) | (+0.75, +0.90, 2.55) | 2.25 × 0.55 | 52° / 69° | (+0.71, −0.71, +0.05) | 10° | f34 dark leaf behind LF/H3 stalk, tip ≈ f .60 h .57 |

- **Face orientation (the 022 lesson).** The normals above are the start of each leaf's broad face (`leafn.py`, chosen
  perpendicular to the axis to maximise the worst of the front and side views). They sit about 45° between the front
  and side cameras, which gives |n · camera| ≈ 0.5–0.7 from the front, the side and the rear alike, so **no leaf is
  edge-on to any elevation camera**. The twist (15–25° base → tip) and the arch vary them; keep every leaf's mid-length
  normal within ±15° of its row. Because the face is diagonal, W is set 20–30 % above the drawn apparent width.
- **Contact:** every leaf base sinks 0.15 into the dish; neighbouring leaves may cross (LC in front of LB's base, LD in
  front of LE, LG over LI) but never with coplanar faces; no leaf passes through a stalk or a head.
- **Clearances:** leaf tips stay at or below z 3.15 (0.72 H); keep the H3 stalk clear between LF and LG from z 1.5 up
  (the hero's isolated stalk run), and keep H1's stalk clear above z 2.0.
- **Expected hero:** X −2.45 … +2.85 (LA and LH tips), Y −1.5 … +1.3 (LA's edge and the back rocks / LB), z 0 … 4.38 →
  **5.3 × 2.8 × 4.4**.

## 3. View conflicts and resolutions

### 3.1 The "front three-quarter (hero)" is an elevated front view, drawn wider than the front cell

- **Evidence.** The mound is centred and seen straight on; heads sit at f .24/.41/.65 against the front cell's
  .23/.42/.68 and at the same heights; the leaf tips and both profiles match (§1.2). Its W : H is 1.20 against the
  front cell's 1.09 because its leaves reach further out (the base is 0.88–0.89 H wide in both).
- **Resolution.** The hero governs W (5.3). Compare the hero with an extra **`f34_sheet (0, 14)`** and the front cell
  with **`front_sheet (0, 10)`** (expect front_sheet W : H about 1.2, not 1.09; record it). The kit `front34 (−28, 12)` has
  no sheet counterpart: self-consistency only.

### 3.2 Rear and rear three-quarter are not exact opposites of the hero

- **Evidence.** A true rear of the hero would put H3 (the tallest, +X) at screen left and H1 (the lowest, −X) at screen
  right. The rear cell draws the heads almost symmetric (.88 / 1.0 / .88); the r34 puts the low head at screen left
  (as only a front-left camera would) while its rocks (two left, one centre, one right) fit a back-right camera. The
  sheet repeats the hero's composition in its back views.
- **Resolution.** The hero, front and side govern the layout. Compare **`rear_sheet (180, 10)`** by shares (±4), W : H
  (0.90–1.10), 3 heads above the leaves with V-dips, 7–9 leaf tips, 3–4 rocks and the h .55 run count (5–6); expect
  the screen-left head at about h .97 against the sheet's .88 and record it. Compare the r34 with the kit **`rear34
  (152, 12)`** by shares (±5), W : H 0.75–0.95 and counts only.

### 3.3 Side cell agrees with the kit side camera

- **Evidence.** With the camera at +X (screen right = +Y, the back), the tall nearest head is H3 at Y +0.2, the low head
  half-hidden at screen left is H1 at Y −0.4, and H2 hides behind H3. The top view agrees (its left head sits a little
  to the front, its two right heads one front and one back). The broad leaves at screen left (LA, LF) lean forward and
  those at screen right (LG, LB) lean back.
- **Resolution.** Compare an extra **`side_sheet (90, 10)`** directly: D : H 0.58–0.70, shares ±5, two heads seen (one
  partly hidden), broad leaves both sides (§1.2 h .55 runs).

### 3.4 Top view: a round base and a 360° star against an oval, flattened fan

- **Evidence.** The top's mound is round (base 200 × 196 px) and its 7 leaf tips point all round, including straight
  back and straight front. The side (base 2.52 deep against 3.85 wide; D : H 0.633) and the r34's narrowing (W : H 0.826)
  both say oval and flattened. The top is also drawn from about 75–85°, not plan.
- **Resolution.** The hero and the side govern: **oval base 3.9 × 2.55, overall D 2.8**. Judge the top only by: a mound
  ringed with 4–5 rocks; **7–9 leaf tips spread over at least 300° of the circle**; three heads near the middle, nubs
  pointing outward; mud visible between the leaves. Expect its W : D about 1.7–1.9 against the sheet's 0.98 and record
  it. Compare the kit **`top (0, 89)`** and an extra **`top_tilt (0, 75)`** (shares ±6, S + M together).

### 3.5 Exploded against the hero

- **Leaves:** the exploded draws 8; the hero shows 9–10 tips (one narrow tip behind H1's stalk). Build 9 (decision §8.2).
- **Stalks:** the exploded stalks are shortened (about 1.35); the hero's are 2.3–2.65. One `_stalk` builder; the part is
  H2's stalk.
- **Rocks:** 5 in the exploded, 4 in the hero (the 5th at the back): build 5 (decision §8.3).

### 3.6 Holes, sockets and pegs

- The mud top's holes, the side sockets, the underside socket bosses, the hollow stalk ends and the head's bottom peg
  are joinery notation (the close-ups say "simple cylindrical joins"). **Not modelled in the hero**; the SeedHead part
  keeps its short bottom peg (as M022's tuft kept its peg); no holes anywhere (decision §8.5).

### 3.7 Leaf-base close-up sprig

- The small dark-green sprig lying in a groove on the mud (cu2) appears in no assembled view. Not modelled.

### 3.8 "Clean, solid colors with no texture noise" against the user's blended-colour rule

- The user's rule wins, and the sheet itself paints gradients (§5.3): every unshadowed exploded leaf runs from a darker
  green base to a lime tip, and the heads lighten slightly toward the top. Keep Tint low (no visible noise).

### 3.9 Effects

- The sheet shows none (no glow, fluff, floating seeds, water, dust). Stages 5/6 add nothing by default (§7).

## 4. Construction plan (modeller, stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `seed_head()` → `ReedClumpSeedHead`: H2's head with its bottom peg (Ø 0.65 × 1.36 + nub 0.20 × 0.25 + peg). Compare
     with the exploded heads and cu1: L : Ø including the nub and peg 2.4–2.6; 8 sides; two chamfer steps; dark nub.
   - `stalk()` → `ReedClumpStalk`: Ø 0.25 × 2.45, 6 sides, flat ends.
   - `leaf_blade()` → `ReedClumpLeafBlade`: L 2.5 × W 0.6, arched 25°, keeled. Compare with the far-left exploded leaf:
     W : L 0.20–0.27, the width profile within ±0.08 of §1.4, keel visible, sharp oblique tip.
   - `mud_base()` → `ReedClumpMudBase`: the mound alone (3.6 × 2.3 × 0.6–0.75), lumps and creases, flat dish, no holes.
   - `rock()` → `ReedClumpRock`: 0.9 × 0.8 × 0.65, flat bottom.
   - Render a parts shot (`extra`, about (−20, 15)) laid out as the exploded (heads top, stalks under them, leaves
     either side, base and rocks at the bottom).
2. **Hero:**
   1. `_mud_base`, 5 rocks (§2.1), 3 stalks and 3 heads (§2.2), 9 leaves (§2.3), placed with `_paste` (m011 pattern).
   2. Pre-unite each head (body + nub) and each rock to the mound one at a time; then stalks into the mound and heads onto
      stalks; then the leaves **one at a time**, saving the work file between risky steps; `m004.floor_cut` at z 0.
   3. Origin at the bbox bottom centre; transforms applied. One closed shell (decision §8.6).
3. **Budget** (§4.4): hero about 1500–2100 (limit 4000), each part ≤ 200 (limit 1000). Spend spare tris on leaf width
   stations or rock facets; never on smoothing.
4. **Placeholder keys** (stage 1): `m027_leaf`, `m027_stalk`, `m027_head`, `m027_mud`, `m027_rock`. Stage 4 adds the
   rest (§5.4).

### 4.2 Stage 1 acceptance (measurable; written from the 022/024 verifier failures)

Render the `*_sheet` cameras **with the studio floor hidden** (`FB_Ground.hide_render = True`) or measure only G/S/M/R
pixels: a grey ground shadow is indistinguishable from the grey rock class (M024's round 1 measured W : H wrong this
way). Use this folder's `m.py` masks on both images.

1. **Overall read:** a flattened fan of broad keeled leaves, three tan capsules on straight stalks standing clear above
   it, a lumpy mud mound with grey rocks; nothing grassy, spiky or column-like.
2. **Leaves are broad and face the cameras** (the 022 failure, and R07's three builds):
   - for each leaf, the broad-face normal at mid-length (from the builder's frame): |n · d| ≥ 0.35 for d = front
     (0, −1, 0), side (1, 0, 0) and rear (0, 1, 0), except LH (≥ 0.30, it lies low); **no leaf below 0.25 from any of
     the three**; report the table;
   - real widths per §2.3 (W : L 0.18–0.30); keel thickness 0.06–0.09; no leaf thinner than 0.035 at its edges;
   - in front_sheet, side_sheet and rear_sheet at h .55: 5–6 separate green runs with background between; front and
     rear: the outer runs (LA, LG / LH) each ≥ 0.12 W wide; side: the front-leaf run ≥ 0.12 W and the back-leaf run
     ≥ 0.15 W (§1.2).
3. **Silhouette per view** (f34_sheet, front_sheet, side_sheet, rear_sheet; §1.2 tables):
   - W : H: f34 1.12–1.28; front_sheet 1.12–1.28 (§3.1); side D : H 0.58–0.70; rear 0.90–1.10;
   - width per height at h .1, .3, .5, .6 within ±0.07 of the view's row, including **the neck at h .3 (0.55–0.63 W)
     between the mound (h .1) and the fan (h .5–.6)**;
   - top profile within ±0.07 at every 0.05 f, with **three head peaks and two dips ≥ 0.15 h** (f34: peaks f .20 / .40 /
     .70, dips at f .30 and .55); the outer shoulders at f 0–.15 (.57–.60) and f .90–1.0 (.50 → .45).
4. **Shares per view** (G / S / M / R ±4, M + R ±4, top ±6), **rear included**: f34 54.5 / 19.3 / 17.1 / 9.1;
   front 53.8 / 18.9 / 18.6 / 8.7; side 56.1 / 12.7 / 21.1 / 10.0; rear 51.9 / 19.2 / 21.6 / 7.3; r34 (kit rear34)
   49.1 / 22.0 / 18.6 / 10.3 (±5); top_tilt 54.0 / (S + M 31.5) / 14.5. Stalks visible as their own runs ≥ 1.4 % of each
   elevation (`stalk.py`).
5. **Heads:** components within ±0.06 of §1.2 in f34_sheet and front_sheet (centres and h extents); axes 112 / 103 / 74°
   ±8°; L : W including the nub 2.0–2.4; three heads above the leaves in every elevation except the side (two, one
   partly hidden).
6. **Base:** widest at h .1: f34 0.70–0.80 W; side 0.85–0.95 W; 4 rocks in f34 (runs at h .16 per §1.2 ±0.05), 3–4 from
   the side and rear, 4–5 in the top.
7. **Kit views** (front34, rear34, underside): self-consistency; the underside is a flat oval with the side facet band.
8. **Parts against their cells** (§4.1).
9. **Hero size** 5.3 × 2.8 × 4.4 (±0.3 / ±0.35 / ±0.2).

### 4.3 Stages 2 and 3

1. **Stage 2:**
   - zero non-manifold, boundary, wire and loose elements; zero bowtie vertices (`M.audit()` `nonmanifold_verts`; leaf
     bases crowding the dish are the likely spot, `M.fix_bowties`); no zero-area faces or n-gons; normals outward;
   - no faces under 5° where leaf bases, stalks and rocks meet the mound (m011 `_tidy` / `_desliver`);
   - don't decimate a leaf below 5 width stations with its keel, a head below 8 sides and 4 rings, a stalk below 6 sides,
     or a rock below about 24 tris.
2. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

### 4.4 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Mud mound (16 × 4 rings + dish + bottom) | 1 | 180 | 180 |
| Rocks (hull, 3 rings) | 5 | 36 | 180 |
| Stalks (6 sides, 2 segments, caps) | 3 | 32 | 96 |
| Seed heads (8 sides, 4 rings, nub) | 3 | 95 | 285 |
| Leaves (5 segments, keeled, twisted) | 9 | 44 | 396 |
| **Sum before union** | | | **about 1140** |
| **Hero after union** (seams, slivers, floor cut) | | | **about 1500–2100** (limit 4000) |
| Parts: SeedHead / Stalk / LeafBlade / MudBase / Rock | | | about 110 / 32 / 44 / 180 / 36 (limit 1000) |

## 5. Colour plan (modeller, stage 4)

### 5.1 Swatches (flat; medians of the inner 40 × 40 of each, x 842–882)

| Swatch | Rows | Hex | HSV |
| --- | --- | --- | --- |
| Seed Head | 162–220 | `#DBA76F` | 31°, 0.49, 0.86 |
| Reed Leaf | 229–287 | `#90A436` | 71°, 0.67, 0.64 |
| Reed Stalk | 297–354 | `#516B2C` | 85°, 0.59, 0.42 |
| Mud Base | 364–422 | `#7F5F40` | 30°, 0.50, 0.50 |
| Rock | 432–490 | `#87807D` | 18°, 0.07, 0.53 |

- **Seed Head** is a little paler and less saturated than the rendered heads (`#D1975C`–`#D99D5E`).
- **Reed Leaf** sits between the exploded leaves' middles (`#87A12E`–`#9CB436`) and their tips.
- **Reed Stalk** is much darker than the rendered exploded stalks (`#7C9230`) but close to the hero's shaded stalk
  (`#5E7A2A`): calibrate on the render, and keep the stalks darker than the leaf tips (§5.4).
- **Mud** matches the renders (`#806247`–`#86684B`). **Rock** matches the light rocks (`#8C8078`, `#8E847E`).

### 5.2 Rendered regions (`samp.py`, `grad.py`, `rocks.py`; median / lit quartile / shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Green, f34 / front / side | V | G | `#6A8229` / `#688228` / `#6F8729` | `#9FB43D` / `#9CB13C` / `#9FB440` | `#3E5412` / `#405613` / `#455C16` |
| Green, rear / r34 / top | V | G | `#698327` / `#6A8328` / `#6B8623` | `#9CB23C` / `#9BB139` / `#99AF3B` | `#415814` / `#3E5512` / `#32450B` |
| Leaves, exploded each | §1.4 boxes | G | `#86A02F` / `#97AF34` / `#77922D` / `#718B2B` | `#AAC042` / `#B4C649` / `#A6BC40` / `#A4BA3E` | `#5A732C` / `#5D762B` / `#5B7622` / `#607B23` |
| Leaves, exploded centre group / cu2 | (245,1106,416,1304) / (640,1010,822,1080) | G | `#708B29` / `#5C771F` | `#9CB338` / `#859E2C` | `#4B6516` / `#34490E` |
| Stalks, exploded / cu1 | (245,985,425,1125) / (640,930,740,996) | G | `#7C9230` / `#7B9030` | `#8CA136` / `#859C31` | `#556E2D` / `#57712F` |
| Stalk, hero H3 (tight box) | (293,268,306,292) | all | `#5E7A2A` | | |
| Heads (no nub), f34 / front / side / rear | V | S, v ≥ 0.5 | `#CA9258` / `#CE945A` / `#C58D54` / `#CE945A` | `#F2B776` / `#F1B776` / `#EBAF6F` / `#F0B371` | `#9B6F44` / `#996E46` / `#9C6F45` / `#9A6E43` |
| Heads, r34 / top | V | S | `#CF9459` / `#C58F57` | `#F1B675` / `#F1B675` | `#9A6D42` / `#A57646` |
| Heads, exploded / cu1 | (200,840,480,990) / (640,850,822,940) | tan | `#D1975C` / `#D99D5E` | `#E7AA6A` / `#E3A868` | `#A2764B` / `#AC7B4C` |
| Nubs (+ pegs), f34 / exploded / cu1 | S & v < 0.5 / (200,840,480,990) / (700,915,735,945) | dark B | `#6C4F33` / `#664D2F` / `#5B4427` | `#7C5A3B` / `#765838` / `#7E5935` | `#61472B` / `#4B3921` / `#453217` |
| Mud, f34 / front / side / rear | V | M | `#846549` / `#86684B` / `#86684A` / `#896A4C` | `#9F7A58` / `#A17D5B` / `#A27F5E` / `#A27E5D` | `#5E4B37` / `#614D38` / `#66513C` / `#634F3A` |
| Mud, exploded / cu2 / cu3 underside | (185,1312,462,1460) / (625,1060,822,1142) / (625,1160,822,1314) | B | `#806247` / `#A17B58` / `#614931` | `#A07B58` / `#AA8562` / `#927152` | `#5E4A36` / `#675238` / `#5B442D` |
| Mud front face (hero) | (200,455,330,475) | all | `#86674A` | `#93704E` | `#7A5D3E` |
| Rock, f34 / front / side / rear | V | R | `#83756F` / `#84776E` / `#87776E` / `#837469` | `#AF9E91` / `#AD9C8F` / `#AF9D8F` / `#B3A193` | `#5E554C` / `#5E574D` / `#5A5149` / `#5F564D` |
| Rocks, exploded / cu2 | (95,1315,540,1500) / (740,1060,795,1105) | R | `#8C8078` / `#A79384` | `#B0A299` / `#B6A293` | `#615B56` / `#756658` |
| Hero rocks RK1 dark / RK2 light / RK3 | (92,415,112,440) / (150,412,172,440) / (318,418,342,440) | all | `#6D6967` / `#8E847E` / `#7F7064` | `#877973` / `#A4978F` / `#B3A193` | `#655B54` / `#8B7D74` / `#66594F` |

**Gradients along a part** (medians in five equal steps):

```
leaf base -> tip (exploded, unshadowed)
  far-left part   #7A952C #87A12E #92AB31 #A8BE40 #A5BA3F
  left tall       #829B2C #8CA531 #9CB436 #B0C344 #B4C74B
  right up        #557120 #638025 #708C2C #9AB23C #AEC346
  right low       #6B8629 #718D2A #7C982D #9BB337 #B0C443
  hero LA         #425A18 #577023 #70892C #9CB13D #A7BA44      (base in the leaves' shade)
stalk bottom -> top (exploded)   #7E942E #82992F #899F32 #8DA133 #869B35 / #788F2F ... #7D9432 / #70882F ... #788F2F  (flat)
head bottom -> top (exploded; first = shaded bottom chamfer, last = top chamfer + nub)
  L / C / R       #9E6F41 #D4995D #E3A869 #E4AB6F #9B7048 / #976B3D #D0965B #E0A667 #E2AA6C #9E734A / #92673B #CD9257 #DBA060 #DFA668 #986E45
  hero H2         #A77343 #D1965A #E3A96A #E5AC71 #9A7048
```

**Height bands** (median per 0.1 h, h 0 → 1; `-` = too few pixels):

```
f34   G   -  #4D6216 #4F661D #5B7225 #6C842A #7E952F #A2B640 #B4C750   -       -
front G   -  #4C6016 #50681D #5A7225 #657D25 #7A932F #9FB541 #B3C55C   -       -
rear  G   -  #4C5915 #4D6619 #5C7522 #708A28 #8FA635 #95AA3E   -       -       -
side  G   -  #415114 #536A1E #597320 #657F25 #839930 #9CB142 #B1C251   -       -
f34   M   #816346 #8A6A4D #735E4C                                               (h .2 = the mound top in leaf shade)
f34   S   h .5-.9  #9A6F41 #AC7E50 #CA9258 #DDA365 #BE8F5E                      (h .9 = nubs)
```

**Leaf hue by light** (terciles of v): f34 dark 81° (sat 0.77) / mid 76° / lit 71°; exploded 81° / 75° / 71°.

Deciles (dark → light), f34:

```
green #2E4109 #435819 #4F6A1A #59722F #697D1B #6F872B #7B962E #90A636 #9CB138 #ACBF49
heads #8D6437 #9F7144 #A6794E #B58557 #C98D52 #C89967 #DCA365 #E2A767 #E9B47B #F5C493
mud   #46392B #634D39 #705740 #7E6043 #816449 #86664B #86694E #907152 #9E7956 #A4805E
rock  #514A42 #605751 #6D6056 #6F6B68 #817166 #8A7B70 #918379 #A59080 #AD9C8C #B6A494
```

### 5.3 How the colour works

**Leaves.**
- One yellow-green family: view medians hue 76–78°, sat 0.65–0.75. Lit faces lime (`#9FB43D`), shade faces deep green
  (`#3E5412`), and the shade is cooler (81° against 71°): that much is the light; never paint by facing.
- **Painted base → tip gradient on every leaf** (unshadowed exploded leaves): base mid-dark green (`#6B8629`–`#829B2C`,
  the right-up leaf `#557120`) → middle `#87A12E`–`#9CB436` → tip lime (`#A5BA3F`–`#B4C74B`). The hero's height
  bands show it strongly (h .1 `#4D6216` → h .7 `#B4C750`), helped by the leaves' shade near the mound.
- The two halves either side of the keel differ only by light.

**Stalks.**
- A plainer, slightly darker green than the leaf middles, with no gradient (exploded stalks flat `#788F2F`–`#8DA133`;
  the swatch says "Reed Stalk" is the darker green). In the hero the H3 stalk reads `#5E7A2A`, darker than the leaves
  beside it.

**Seed heads.**
- Warm orange-tan, hue 30–31°, sat 0.55–0.57, unshadowed `#D1975C`–`#D99D5E`. A mild **bottom → top lift** on the body
  (`#D4995D` → `#E4AB6F`, about 15 levels); the bottom chamfer reads dark only by light. **Nub** a dark warm brown
  (`#5B4427`–`#6C4F33`), clearly separate from the tan.

**Mud.**
- Warm mid brown, hue 28–30°, sat 0.44–0.45 (`#806247`–`#86684B`); the mound top under the leaves is darker
  (`#735E4C`, shade) and the creases between lumps darkest.

**Rocks.**
- Warm grey, hue 18–28°, sat 0.06–0.12. Two tones: light (`#8E847E`, RK2/RK3/RK4/RK5) and one darker rock
  (`#6D6967`, RK1).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered medians of **unshadowed** regions (exploded parts and close-ups), not swatches.
`K.sample` kinds: `"green"` for leaves and stalks; `"brown"` for mud and nubs; `"all"` on tight boxes for the heads
(tan) and `"stone"` for rocks.

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m027_leaf` | `#7F9A2E` (exploded leaf medians `#86A02F`, `#97AF34`, `#77922D`, `#718B2B`; mid fifths `#87A12E`–`#9CB436`; swatch `#90A436`) | leaf middles (t 0.3–0.7) | rough 0.8, `low_spec` |
| `m027_leaf_base` | `#6A862A` (base fifths `#7A952C`, `#829B2C`, `#557120`, `#6B8629`) | inner 30 % of each leaf | rough 0.8, `low_spec` |
| `m027_leaf_tip` | `#ACC144` (tip fifths `#A5BA3F`, `#B4C74B`, `#AEC346`, `#B0C443`; hero LA tip `#A7BA44`) | outer 30 % | rough 0.8, `low_spec` |
| `m027_stalk` | `#7A9030` (exploded `#7C9230`, cu1 `#7B9030`) | stalks | rough 0.8, `low_spec` |
| `m027_head` | `#D69A5D` (exploded `#D1975C`, cu1 `#D99D5E`, body second fifths `#D0965B`–`#D4995D`) | head body lower 50 %, bottom chamfer | rough 0.85 |
| `m027_head_light` | `#E2A86A` (body upper fifths `#E3A869`–`#E4AB6F`, `#E0A667`; cu1 lit `#E3A868`) | head body upper 50 %, top chamfer | rough 0.85 |
| `m027_nub` | `#644A2E` (exploded `#664D2F`, cu1 `#5B4427`, hero `#6C4F33`) | nubs; the SeedHead part's peg | rough 0.9 |
| `m027_mud` | `#826347` (exploded `#806247`; views `#846549`–`#86684B`; swatch `#7F5F40`) | mound sides and rim | rough 0.95 |
| `m027_mud_dark` | `#66503B` (shade quartiles `#5E4A36`–`#66513C`; hero top band `#735E4C`; underside `#614931`) | the dish top within 0.5 of the leaf bases, creases between lumps, the bottom chamfer | rough 0.95 |
| `m027_rock` | `#8C827B` (exploded `#8C8078`; hero RK2 `#8E847E`; swatch `#87807D`) | RK2–RK5, the Rock part | rough 0.85 |
| `m027_rock_dark` | `#6E6865` (hero RK1 `#6D6967`; exploded rock A `#7D7670`) | RK1 | rough 0.85 |

**Calibration warnings:**
- **Leaves:** greens calibrate darker than the painted sheet (kit memory); trust the render match. The f34_sheet green
  median must land within 12 of `#6A8229` with hue 74–80°; height bands with h .6–.7 the lightest (within 15 of
  `#B4C750`) and h .1–.2 the darkest. `leaf_tip` hue ≤ 74°, `leaf_base` ≥ 76°.
- **Stalks** must read as stalks: the f34_sheet H3 stalk box within 15 of `#5E7A2A`, at least 10 levels darker than the
  leaf tips around it and not lighter than the leaf middles.
- **Heads:** f34_sheet head median within 10 of `#CA9258`, hue 29–33°, sat ≥ 0.52; the lit quartile must not clip
  (≤ `#F8C080`-ish); if it washes out, lower the specular, not the key. The nub must stay ≥ 60 levels darker than the
  body.
- **Mud and rock:** f34_sheet mud within 10 of `#846549`, rock within 12 of `#83756F`; the rocks stay grey (sat ≤ 0.15),
  never brown.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Leaves** (field = each leaf's along-length t from its construction frame): t < 0.3 `leaf_base`; 0.3–0.7 `leaf`;
  t > 0.7 `leaf_tip`; 3 steps; ±0.08 noise on t. The short front blades LC/LD/LE shift 0.1 toward the base.
- **Stalks:** plain `m027_stalk`; the bottom 0.3 (inside the leaf shade) 30 % toward `leaf_base`.
- **Heads** (field = along-axis t, 0 = bottom): t < 0.5 `head`, t > 0.5 `head_light`, 3 steps; nub `m027_nub` (hard
  edge at the top chamfer ring).
- **Mud:** `mud` base; the dish faces and faces within 0.5 of a leaf/stalk base → 60 % `mud_dark`, fading over 0.3;
  crease faces between lumps 40 % `mud_dark`; broad patches (`K.patches` scale 0.6, level 0.3) between `mud` and a 25 %
  `mud_dark` mix.
- **Rocks:** one key per rock (RK1 `rock_dark`, the rest `rock`), each with per-rock `tint_var` 0.05.
- **Hard edges only** where materials meet: leaf | mud, stalk | mud, stalk | head, head | nub, rock | mud.

### 5.6 Texture (Tint) and finish

- **Tint** (`tint_var` per piece about 0.04, so each leaf, head and rock differs slightly):
  - leaves: `K.texture` amp 0.03, scale 0.5 (broad, per facet group);
  - heads: amp 0.025; stalks: amp 0.02;
  - mud: amp 0.05, scale 0.4 (broad soil mottling); rocks: amp 0.04;
  - never per-triangle confetti ("no texture noise").
- **Finish:**

| Material | Roughness | Specular | Metal | Notes |
| --- | --- | --- | --- | --- |
| Leaf and stalk keys | 0.8 | `FOLIAGE_SPEC` (`low_spec=True`) | 0 | matte faceted foliage |
| Head keys | 0.85 | normal (lower if the lit faces clip) | 0 | dry, matte |
| `m027_nub` | 0.9 | normal | 0 | matte |
| Mud keys | 0.95 | low | 0 | damp-looking but matte on the sheet |
| Rock keys | 0.85 | normal | 0 | matte stone |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Leaves:** f34_sheet green median within 12 of `#6A8229`; parts-shot leaf base → tip within 15 per step of the
  exploded far-left row; height bands light at h .6–.7.
- **Heads:** f34_sheet within 10 of `#CA9258`; parts-shot head within 10 of `#D1975C`; nub `#5B4427`–`#6C4F33` ±12.
- **Stalks:** parts-shot within 10 of `#7C9230`; hero H3 stalk within 15 of `#5E7A2A`.
- **Mud / rock:** parts-shot mud within 8 of `#806247`, rock within 10 of `#8C8078`; f34_sheet per §5.4.
- **Shares** per §4.2.

## 6. Joins and contact (no cracks or seams on this sheet)

- **Stalks into the mound:** each stalk starts 0.15 under the dish surface (z 0.30), straight; one exact union.
- **Heads onto stalks:** the stalk top sinks 0.12 into the head's bottom chamfer, coaxial; no visible peg in the hero.
  The stalk's flat end must not be coplanar with the head's bottom ring.
- **Leaves into the mound:** each leaf base sinks 0.15 into the dish; the base width (0.68 W) stays visible at the
  surface (no stalk-like petiole).
- **Rocks:** 30–40 % sunk into the mound side or rim, never floating; none coplanar with a mound face.
- **Ground:** floor-cut at z 0 (`m004.floor_cut`); the mound bottom and the rocks' flat bottoms make the contact.
- Overlap everything; exact booleans (pitfall 10).

## 7. Lighting and VFX plan (modeller, stages 5 and 6)

**What the sheet shows:** an ordinary sunlit plant clump on dry mud. No glow, light, sparkle, floating seeds or fluff,
water, mist or dust anywhere. The heads' pale lit faces are diffuse (their shade quartile `#9B6F44` is still brown), not
emission.

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight:** nothing glows. Emission ≥ 1.0 would export as flat Neon and erase the heads'
  bottom → top lift and the leaves' gradient.
- **Studio note (Requires Manual Validation):** check in Studio that the head tops don't clip under the game sun and
  that the leaf base → tip gradient survives the palette export; check the 0.25 stalks stay visible at normal camera
  distance.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **Recommended: none.** The sheet shows no effect, `src` has no reed node, and the recent plant models (M017, M018,
  M022, M024) shipped none. Record "Stage 6 skipped: sheet shows no VFX".
- **Option** (decision §8.7): the R07 `ReedPatch` pair, if the main session wants harvest feedback:
  - `harvest_hit` at the front of the leaves, (0, −1.2, 2.2), colour override `["#7F9A2E", "#D69A5D"]` (leaf and
    seed-head chips), scale about 0.5;
  - `harvest_deplete` at the mound, (0, 0, 0.5), colours `["#826347", "#7F9A2E"]`, `shape` about [3, 1, 2], scale
    about 0.3.
- **Not recommended:** `dust` or `vapour` (nothing floats; no water on this sheet), `ore_glint` (reads as magic), any
  light.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by `git grep` of the repo, the kit manifests and a search of every sheet .blend,
zstd-decompressed (`m027_study/blendall.py`):
- **R07 kit:** `ReedPatch` (61 hits in `FlintbornWorldKit.blend`), `ReedPatchLeafBlade`, `ReedPatchMudBase`,
  `ReedPatchReedStalk`, `ReedPatchSeedHead`, `ReedPatchClippedPatch`, `ReedPatchDepleted`, `ReedStems`; keys
  `r07_reed_leaf` (`#3A7A1F`), `r07_reed_stalk` (`#7B9C2C`), `r07_cattail` (`#D49A60`).
- **V04 kit:** `CattailClump` (35 hits), `CattailLeaf`, `CattailLeafy`, `CattailRootPlug`, `CattailSeedHead`,
  `CattailShortCompact`, `CattailStem`, `CattailTallDense` (sheet 117's subject).
- **V09 kit:** `Stormreed*`; key `v09_reed`.
- **`src`:** `ReedFerry` (a POI id), no node.
- `M.mk` would silently rename a clash to `<name>M027`, so avoid all of these.

**Proposed names.** `ReedClumpNode`, `ReedClumpSeedHead`, `ReedClumpStalk`, `ReedClumpLeafBlade`,
`ReedClumpMudBase`, `ReedClumpRock` and the `m027_` prefix occur nowhere in the repo or any sheet .blend (`ReedClump`
0 hits; `m027_` 0 hits).

| Object | Part | Why |
| --- | --- | --- |
| `ReedClumpNode` | hero | the sheet's own words ("a small clump of reeds"); `…Node` like `BerryBushNode` / `FiberPlantNode` / `ThornBushNode`; R07 owns `ReedPatch*` |
| `ReedClumpSeedHead` | Seed Head (H2 with its peg) | R07 owns `ReedPatchSeedHead`, V04 `CattailSeedHead` |
| `ReedClumpStalk` | Reed Stalk | R07 owns `ReedPatchReedStalk` |
| `ReedClumpLeafBlade` | Leaf Blade | R07 owns `ReedPatchLeafBlade` |
| `ReedClumpMudBase` | Mud Base | R07 owns `ReedPatchMudBase` |
| `ReedClumpRock` | Rock | generic `*Rock` names exist on other sheets only as longer names; this exact name is free |

- Fallback if the main session prefers the sheet's word: `ReedPatchNode` is free as an exact name, but its parts would
  need another stem (R07 owns `ReedPatch*` parts), so `ReedClump*` keeps the set consistent.
- Palette keys `m027_*` (§5.4). Collection `Kit/M027 Reed Patch`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **5.3 × 2.8 × 4.4** (recommended: H 0.80 C, near the top of the design doc's 0.35–0.85 C reed range,
   heads at chest/shoulder height), or 0.65 C (4.3 × 2.3 × 3.6, the forage-shrub height), or R07's scale
   (7.6 × 5.7 × 7.2, outside the doc's range).
2. **Leaves:** **9** (recommended: the hero's 9–10 tips; the exploded's 8 plus the dark inner-right LI), or 8 (the
   exploded count; the hero's centre reads thinner).
3. **Rocks:** **5** (recommended: the exploded's 5; 4 show from the front, the 5th fills the back for the rear and
   top), or 4.
4. **Footprint** (§3.4): **oval base 3.9 × 2.55, overall D 2.8, flattened fan** (recommended: the side and the r34
   agree; the hero governs), or a round base about 3.9 × 3.3 matching the top view (the side then reads about 30 % too
   deep).
5. **Pegs, holes and sockets:** **not modelled in the hero; no holes anywhere; the SeedHead part keeps its short bottom
   peg** (recommended: notation in the close-ups; holes add boolean risk), or also export loose pegs.
6. **Hero packaging:** **one closed shell** (recommended: STAGES default), pieces united one at a time.
7. **Stage 5/6:** **no emission, light or VFX** (recommended: the sheet shows none; matches the recent plants), or the
   R07-style `harvest_hit` / `harvest_deplete` pair (§7.2).
8. **Exports:** the hero plus 5 parts (`…SeedHead`, `…Stalk`, `…LeafBlade`, `…MudBase`, `…Rock`) (recommended: the sheet
   names exactly these five reusable parts). R07's clipped and depleted states and the `ReedStems` drop are not on
   this sheet; not built unless asked.
9. **Comparison cameras** (§3): `f34_sheet (0, 14)` for the hero, `front_sheet (0, 10)`, `side_sheet (90, 10)`,
   `rear_sheet (180, 10)` (counts and shares; heads not mirrored), kit `rear34 (152, 12)` for the r34 (counts and
   shares), kit top + `top_tilt (0, 75)`; kit front34 and underside as self-consistency; a parts shot `(−20, 15)`.
   **All `*_sheet` renders with the floor hidden.**
10. **Leaf orientation:** **broad faces about 45° between the front and side cameras, with a 15–25° twist** (recommended:
    broad from the front, side and rear, as the sheet draws them; the 022 back-half failure), or faces square to the
    front (best front read, edge-on from the side, as R07's early builds).
11. **Names** as proposed.

## 9. Pitfalls to avoid

1. **Grass blades.** Every leaf is a broad keeled lance (W : L 0.18–0.30, W 0.40–0.70 studs) with thick edges — not a
   card, not `K.leaf`, not `NS["leaf"]`. R07 was marked "thin dark blades".
2. **Edge-on leaves.** Check the face-normal dot products (§4.2 item 2) before rendering; the side and rear must show broad
   leaves too (M022's back half failed exactly here: LH/LI flat and edge-on, LG face pointing down).
3. **A column of leaves.** The fan has a neck at h .3 and splays to 0.81–1.0 W at h .5–.6, with paper between 5–6
   leaf runs at h .55. Keep "spacing between leaves".
4. **Heads buried or touching the leaves.** The heads and at least the top 0.4–1.0 of each stalk stand clear above the
   leaf tops (top-profile dips ≥ 0.15 h); the H3 stalk shows long.
5. **Thin or small heads.** The heads are fat capsules (body L : Ø ≈ 2.0, Ø 0.55–0.65 at this size) with chamfered
   ends and a dark nub — R07's other failure was "small seed heads". Not cylinders, not spindles, not round balls.
6. **Floating or detached pieces.** Stalks are coaxial with their heads; leaves and stalks rise out of the dish; rocks
   sink into the mound.
7. **A smooth dome base.** The mound is a few chunky lumps with creases, a flat dish and a chamfered bottom.
8. **Colour by facing.** Lime and deep-green faces on one leaf are light; paint along each leaf's length only;
   `K.check` facing correlation < 0.5.
9. **Flat one-colour parts.** The leaf base → tip and the head bottom → top gradients are on the sheet (§5.3); the
   stalks stay plainer and darker than the leaf tips; the nub stays dark.
10. **Exact booleans.** Overlap everything: stalks 0.15 into the mound, 0.12 into the heads, leaves 0.15 into the dish,
    rocks 30–40 % in; no coplanar faces (stalk end vs head bottom ring, leaf bases crowding each other). Add pieces one
    at a time and save the work file between; remove slivers with m011's `_tidy` / `_desliver`; check bowtie verts
    where leaf bases crowd.
11. **Comparing the wrong views.** The hero is an elevated front view drawn wider than the front cell; the rear and r34
    repeat the front composition (heads not mirrored); the top is tilted and round (§3).
12. **Measuring the ground shadow.** Hide the floor for the `*_sheet` renders: the rock class (grey) cannot be told from
    a grey shadow.
13. **Side-view handedness.** The kit side camera at az 90 sits at +X, so screen right is the model's back; the sheet's
    side cell agrees (H3 tall in the middle, H1 low at screen left).
14. **Naming clashes** with R07's `ReedPatch*` / `ReedStems`, V04's `Cattail*` and V09's `Stormreed*` (§8). Don't edit
    shared helpers (`kit_models.py`, `kit_mcp.py`, `build_kit.py`, `lib/vfx.py`); put new helpers in `m027.py`. No
    commits, pushes or exports in the modeller's stages.

## Decisions (main session, 2026-10-28)

All recommendations are accepted:
1. Size: 5.3 W × 2.8 D × 4.4 H (±0.3 / ±0.35 / ±0.2).
2. Nine leaves.
3. Five rocks.
4. An oval base 3.9 × 2.55 and a flattened fan. The top view's width to depth (about 1.8 against the sheet's 0.98) is a recorded, accepted miss.
5. No holes or sockets. Only the seed-head part keeps its short peg.
6. One closed shell. Add pieces one at a time.
7. No effects.
8. Hero plus the 5 parts.
9. Comparison cameras:
   - `f34_sheet (0,14)`, `front_sheet (0,10)` and `side_sheet (90,10)` compare directly;
   - `rear_sheet (180,10)` and the kit `rear34 (152,12)` compare by counts and shares only;
   - the kit top plus `top_tilt (0,75)`.
10. Leaf faces sit about 45° between the front and side cameras, with a 15–25° twist. No leaf may be edge-on from any view: the face score is ≥ 0.35 per camera, with a hard floor of 0.25.
11. Names as proposed (`ReedClump*`, hero `ReedClumpNode`).

Every `*_sheet` render hides the studio floor, because the grey rocks can't be told apart from the ground shadow.

## Stage 1 — Modelling (modeller, 2026-10-28)

Builder `art/blender/kit/mcp/m027.py`, `build()`. It takes about 15 s without renders and 31–38 s with them, uses
fixed seeds, and the hero guard passed on attempt 0 in the final build. It was built in a background Blender (bgmcp
port 9880, work file `art/blender/assets/kit/wip/M027.blend`).

**Parts, each from its own function** (all in the build frame: front −Y, +X right, ground z 0):
- `seed_head()`: one lofted 8-sided ring stack, no boolean, one closed shell:
  - bottom chamfer at 0.62;
  - body at 1.0, with a mid ring at 1.03 (±4 % jitter, ±6° ring twist);
  - top chamfer at 0.60;
  - a flat annulus at the top;
  - an 8-sided nub (taper 0.9, flat cap);
  - on the part only, a 0.07 × 0.12 peg.

  Part `ReedClumpSeedHead` = H2 (Ø 0.65 × 1.36 + nub 0.20 × 0.25 + peg).
- `stalk()`: 6-sided prism, rings at 0 / 0.45 (±3 %) / 1, flat caps. Part `ReedClumpStalk` Ø 0.25 × 2.45.
- `leaf()`: a broad keeled lance.
  - **Centre line:** a circular arc bent toward gravity. The arc's mid tangent is the chord, so the given face normal
    holds at mid-length. The leaf twists about its own axis from base to tip.
  - **Outline:** stations at t 0 / .15 / .40 / .62 / .82 with half-widths .34 / .40 / .50 / .49 / .36 × W, then a knife
    tip offset 0.2 W sideways (onto the upper edge of a leaning leaf).
  - **Section:** a midrib vertex on the front (faces slope 11° either side, a fold of about 158°) and one on the back
    (4°), and **thick edges (0.045)** as a top and a bottom line.
  - **Edge lines:** split into pieces of at most 0.25 between stations. The front and back halves are fans from the
    midrib to those edge points.
  - **Why the split:** a first version used plain 6-point rings. Its 0.045 × 0.5–0.85 edge strips were 3–5° slivers,
    and the polish collapsed them to paper edges (the part lost 16 tris). Now every strip corner is ≥ 7.7° and every
    0.045 edge survives (26 on the part, about 200 on the hero).

  Part `ReedClumpLeafBlade`: L 2.5 (chord) × W 0.6, arch 25°, leaning right with its face toward the studio key (see
  stage 4).
- `mud_base()`: a 16-sided oval loft, rx 1.85 × ry 1.18, with a flat bottom. Part `ReedClumpMudBase`.
  - Rings (z, r): (0, .94), (.12, 1.0), (.42, 1.02), the rim (.66, .90), the dish ring (.62, .58), centre .60.
  - The rim has ±0.06 height jitter and two back lumps (+0.15 / +0.13 at az 62° / 118°).
  - 5 lumps (radius ±14 % cosine), with vertical creases at the minima.
  - Quads are split on a seeded diagonal.
- `rock()`: `K.hull_rock`, rings (0, .9, 6), (.42, 1, 6), (.8, .66, 5), (1, .22, 2), flat bottom. Part `ReedClumpRock`
  0.9 × 0.8 × 0.65 (34 tris).

**Hero layout.** The final values are in `HEADS`, `LEAVES` and `ROCKS`, and every change is commented in the builder.
These differ from the study's §2:
- **Mound:** taller and steeper than §2.1 (rim 0.66, dish 0.60). With the §2.1 rings (rim 0.58, a rim inset to 0.88)
  it read as a thin chamfered disc, or a pan with a raised rim.
- **Rocks:**
  - sizes are §2.1 × 1.1: at × 1.0 they read 0.7 of the sheet's rock runs at h .16, and at × 1.3 R was 16 % against 9;
  - RK3 and RK4 are 10 % smaller again and RK5 15 % smaller (they are nearest the side and rear cameras);
  - each base sits at the mound surface − 0.3 × its height, tilted 12° outward;
  - their tops sit at z 0.8–1.0.
- **Heads:** as §2.2, except:
  - H1's head bottom moved 0.1 to the right, to x −0.95 (its head reached f .15 in f34 against the sheet's .17);
  - all stalk feet are at z 0.42 (the higher dish).

  Head axes in f34 are 110.6° / 102.3° / 74.6° (sheet 112 / 103 / 74).
- **Leaves:**
  - widths are §2.3 × 1.15–1.25, then × 1.08 for every hero leaf (`LEAF_W_SCALE`). The sheet's leaves read broader,
    and the side and rear green shares were 45–50 % against 52–56.
  - LA's tip moved to (−2.40, −1.65, 2.75) with a 35° arch, and LB's and LG's tips moved further out in depth (the
    side's D : H was 0.56 against 0.633).
  - LG's face turned up toward the front, to (−0.54, −0.60, 0.59). With §2.3's (−0.69, +0.69, +0.23) its underside
    faced the camera and read dark.
  - LC's tip now goes back-left to (−0.85, 0.20) and LI's back to (0.50, 1.05), so the top view's tips spread round the
    circle (§3.4).
  - The LA, LC, LE, LF and LI bases moved 0.06–0.22. A search found the smallest base move, tips fixed, that keeps
    every leaf at least 0.04 clear of every stalk and head above z 0.75. Before it, four leaves passed through a stalk.

**Stage 1 acceptance (§4.2).** Measured with the study's masks on both images (`m027.measure()`); every `*_sheet`
render hides the floor. Each cell is ours / sheet.

| View | W : H | G | S | M | R | M + R | Top-profile error mean / max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f34_sheet (0, 14) | 1.168 / 1.199 | 55.4 / 54.5 | 17.8 / 19.3 | 17.5 / 17.1 | 9.3 / 9.1 | 26.8 / 26.2 | 0.017 / 0.06 |
| front_sheet (0, 10) | 1.174 / 1.09 | 55.1 / 53.8 | 18.0 / 18.9 | 17.5 / 18.6 | 9.4 / 8.7 | 26.9 / 27.3 | 0.062 / 0.33 |
| side_sheet (90, 10) | 0.630 / 0.633 | 52.6 / 56.1 | 16.5 / 12.7 | 19.1 / 21.1 | 11.9 / 10.0 | 31.0 / 31.1 | 0.121 / 0.39 |
| rear_sheet (180, 10) | 1.103 / 0.977 | 48.6 / 51.9 | 20.0 / 19.2 | 22.4 / 21.6 | 9.0 / 7.3 | 31.4 / 28.9 | – |
| r34_sheet (152, 12) | 1.020 / 0.826 | 48.5 / 49.1 | 20.9 / 22.0 | 22.6 / 18.6 | 8.0 / 10.3 | 30.6 / 28.9 | – |
| top_tilt_sheet (0, 75) | 1.622 / 0.976 | 52.0 / 54.0 | S + M 36.9 / 31.5 | – | 11.2 / 14.5 | – | – |

Notes on the table:
- **front_sheet:** a W : H of about 1.2 was expected (§3.1). The front cell draws the same composition narrower, which
  is also why its profile error is higher.
- **rear_sheet:** the profile is not compared, because the sheet's rear heads are not mirrored (§3.2).
- **r34_sheet:** compared by counts and shares only (decision 9).
- **top_tilt_sheet:** the W : D miss is accepted (decision 4).

Profile and run details:
- f34 top profile, ours `.61 .60 .58 .56 .84 .80 .70 .93 .94 .88 .72 .65 .84 .95 1.00 .68 .73 .77 .46 .47 .48`;
  sheet `.60 .60 .60 .57 .84 .78 .68 .90 .94 .90 .71 .62 .86 .95 1.00 .67 .70 .71 .50 .47 .45`. Three head peaks
  (f .20 / .40 / .70) with dips of .70 and .65 (sheet .68 / .62).
- f34 width per height: h .1 0.77 (sheet .74), the h .3 neck 0.65 (.56), h .5 0.73 (.83), h .6 0.83@0.00 (.81@0.00).
- Green runs at h .55:
  - f34, 5 runs: LA .02–.17 (0.15 W); H1's stalk .30–.31; LB; the centre leaves with H2's and H3's stalks .43–.61;
    LG .65–.81;
  - front_sheet 4, rear 5;
  - side 3: the front-leaf run is .05–.43, the back-leaf run .72–.91.
- Rock runs at h .16 in f34: .08–.14 | .22–.36 | .64–.72 (sheet .10–.20 | .21–.35 | .62–.74).
- Hero size **5.24 × 2.96 × 4.38** (target 5.3 × 2.8 × 4.4, tolerance ± 0.3 / 0.35 / 0.2).

**Leaf face scores.** |n · camera| of each leaf's broad-face normal at mid-length, from the builder. The front and rear
scores are equal by symmetry.

| Leaf | Front / rear | Side | W (built) | Keel (built) |
| --- | --- | --- | --- | --- |
| LA | 0.610 | 0.765 | 0.918 | 0.168 |
| LB | 0.699 | 0.696 | 0.670 | 0.135 |
| LC | 0.672 | 0.673 | 0.540 | 0.119 |
| LD | 0.701 | 0.692 | 0.540 | 0.114 |
| LE | 0.702 | 0.709 | 0.594 | 0.125 |
| LF | 0.718 | 0.694 | 0.734 | 0.143 |
| LG | 0.583 | 0.510 | 0.918 | 0.166 |
| LH | 0.495 | 0.510 | 0.886 | 0.161 |
| LI | 0.693 | 0.714 | 0.648 | 0.132 |
| Part | 0.638 | 0.697 | 0.600 | 0.122 |

- Every score is ≥ 0.49 (target ≥ 0.35, LH ≥ 0.30, floor 0.25), and edge thickness is 0.045 everywhere (≥ 0.035).
- The built keel (edge plus midrib rises) is 0.11–0.17, above §1.4's 0.06–0.09. The study's two numbers conflict: a
  150° fold on a leaf 0.6–0.9 wide cannot be 0.09 thick. I kept the fold and the chunky edges because the sheet's
  leaves read thick.

**Leaf ↔ stalk / head clearance** above z 0.75 (`CLEAR`, computed inside `hero()` before the union): LA 0.048,
LB 0.201, LC 0.049, LD 0.198, LE 0.050, LF 0.044, LG 0.056, LH 0.122, LI 0.043. None intersect.

## Stage 2 — Optimisation and cleanup

- **Union:** M022's guarded exact union with merge 0 (`_union`: one shell at a time, volume-checked, nudged and
  retried on a bad result). 21 shells (mound, 5 rocks, 3 stalks, 3 heads, 9 leaves); none retried or left out.
- **Cleanup after the union**, in order:
  - `m004.floor_cut` at z 0 (floor faces re-keyed to plain mud, Tint 0.95);
  - M022's guarded `_clean_mesh`, `_finish` and `_polish`;
  - `M.fix_bowties`.
- **Hero guard:** if the fused hero is not one clean shell, every leaf base is jittered 0.02 × attempt and the hero is
  rebuilt (up to 6 tries). It checks shells, non-manifold edges, bowties, boundary edges, normals, self-intersections
  and inverted faces. An earlier layout needed attempt 1: two self-intersecting faces where two leaf bases crossed at a
  grazing angle. The final layout passes on attempt 0.

| Object | Tris | Size (studs) | Shells | Non-manifold edges / bowtie verts | Boundary | Wire / loose | Zero-area | N-gons | Self-intersecting pairs | Inverted faces | Min corner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ReedClumpNode (hero) | **1888** / 4000 | 5.24 × 2.96 × 4.38 | 1 | 0 / 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 | 5.04° |
| ReedClumpSeedHead | 140 | 0.64 × 0.66 × 1.73 | 1 | 0 / 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 | 15.3° |
| ReedClumpStalk | 32 | 0.25 × 0.23 × 2.45 | 1 | 0 / 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 | 5.25° |
| ReedClumpLeafBlade | 122 | 1.10 × 0.49 × 2.34 | 1 | 0 / 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 | 7.68° |
| ReedClumpMudBase | 158 | 4.12 × 2.54 × 0.84 | 1 | 0 / 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 | 8.95° |
| ReedClumpRock | 34 | 0.81 × 0.78 × 0.65 | 1 | 0 / 0 | 0 | 0 / 0 | 0 | 0 | 0 | 0 | 15.2° |

- **Budget:** each leaf costs more than §4.4's 44 tris because of the split edge lines, which is still within budget.
- **Transforms and shading:**
  - the origin is at the bounding-box bottom centre on every object, with rotation 0 and scale 1;
  - no custom normals, flat shading, no duplicate verts, normals outward;
  - `K.check` is clean;
  - 26 orphan meshes and 1 unused material were dropped.

## Stage 3 — UV

`M.smart_uv` (angle-based, angle 45°, margin 0.008, min_angle 45°) plus `m012._uv_unfold`.

| Object | Islands | Overlap pairs | Flipped | Min gap | Density (min / median / max) | Conformal stretch p95 |
| --- | --- | --- | --- | --- | --- | --- |
| hero | 288 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.006 |
| SeedHead | 34 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.000 |
| Stalk | 8 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.000 |
| LeafBlade | 5 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.011 |
| MudBase | 15 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.056 |
| Rock | 10 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.038 |

## Stage 4 — Materials, colour and texture

**Calibration.**
- **Pass 1:** `m027.calibrate()` runs `K.calibrate` on the dome for 6 iterations. Every key's dome median landed
  within 6 of its §5.4 target.
- **Pass 2:** the hero's f34_sheet against the f34 cell, with each family scaled in linear light. The values are in the
  builder's palette comment.

| Family | f34 median before pass 2 (ours / sheet) | Correction |
| --- | --- | --- |
| Leaves | #617325 / #6A8229 | scaled up |
| Heads | #C18D56 / #C99057 | scaled up |
| Mud | #715841 / #846549 | scaled up; mud_dark mixing cut back; raised again in pass 2b |
| Rocks | #7B736C / #83756F | scaled up |
| Stalk | part #728A2D / #7C9230 | raised in pass 2c |

| Key | Final hex | Calibration target (sheet render) |
| --- | --- | --- |
| m027_leaf | #719032 | #7F9A2E |
| m027_leaf_base | #5E7C2B | #6A862A |
| m027_leaf_tip | #9DB849 | #ACC144 |
| m027_stalk | #708734 | #7A9030 |
| m027_head | #AF8251 | #D69A5D |
| m027_head_light | #BA8F5E | #E2A86A |
| m027_nub | #503C23 | #644A2E |
| m027_mud | #796148 | #826347 |
| m027_mud_dark | #63503C | #66503B |
| m027_rock | #736C6A | #8C827B |
| m027_rock_dark | #5A5657 | #6E6865 |

**Re-measure** (final renders against the sheet, with the study's masks):

| Region | Ours median / lit / shade | Sheet median / lit / shade |
| --- | --- | --- |
| f34 green | #6D8529 / #A2C13F / #3E5115 | #6A8229 / #9FB43D / #3E5412 |
| f34 heads | #CA9258 / #ECAD6D / #6D4F30 | #C99057 / #F2B676 / #986B3F |
| f34 mud | #846649 / #9B7956 / #413121 | #846549 / #9F7A58 / #5E4B37 |
| f34 rock | #7F756E / #9C8E84 / #574F4A | #83756F / #AF9E91 / #5E554C |

| Region | Ours | Sheet |
| --- | --- | --- |
| Front green / heads / mud / rock (medians) | #6B8429 / #C99158 / #816345 / #7F756E | #688228 / #CC9258 / #86684B / #84776E |
| Hero nubs (f34) | #67492C | #6C4F33 (`#5B4427`–`#6C4F33`) |
| Hero H3 stalk box | #55671F | #5E7A2A |
| Parts shot: head / nub / stalk / mud / rock | #D69C5E / #6B4E31 / #7B9330 / #8F704F / #897D75 | #D1975C / #5B4427 / #7C9230 / #806247 / #8C8078 |
| Parts shot: leaf, base → tip in fifths | #71952C #7FA230 #8EB436 #9FC33D #B2D446 | #7A952C #87A12E #92AB31 #A8BE40 #A5BA3F |

The f34 heads' lit quartile doesn't clip (#ECAD6D). The nub is about 100 levels darker than the body.

**Blending.** All colour is by position fields, never by facing (`K.check`'s facing check is clean):
- **Leaves:** a ladder along each leaf's own t, plus ±0.06 broad noise, in 25 % steps: leaf_base → leaf over t
  0.12–0.42, then leaf → leaf_tip over t 0.58–0.88. LC, LD and LE shift 0.1 toward the base.
- **Heads:** head → head_light along the body's t, in 25 / 75 % steps. The nub and the part's peg are a hard m027_nub.
- **Stalks:** plain; the bottom 30 % is 25 % toward leaf_base.
- **Mud:** quarter steps of mud_dark:
  - the dish 50 %;
  - the rim band near a leaf or stalk foot 25 %;
  - the creases between lumps 25 %;
  - broad noise patches (scale 0.9, level 0.3) 25 %;
  - the floor-cut underside is plain mud.
- **Rocks:** RK1 is rock_dark, the rest rock.
- **Hard edges** only where two materials meet.
- **Slots:** the hero uses 21 material slots: mud ×3, rock ×2, stalk ×2, head ×4 (head, its 25 / 75 % mixes and
  head_light), nub, and leaf ×9 (the base → leaf → tip ladder).

**Tint.** Broad per-piece mottling (`_mottle`: noise patches about 1/scale studs across, never per face):

| Piece | Amp | Scale | Per-piece level |
| --- | --- | --- | --- |
| Leaves | 0.03 | 0.5 | ±0.04 |
| Heads | 0.025 | 0.7 | ±0.04 |
| Stalks | 0.02 | 0.6 | – |
| Mud | 0.05 | 0.4 | – |
| Rocks | 0.04 | 0.8 | 0.97–1.03 per rock |

**Finish:**

| Keys | Roughness | Specular |
| --- | --- | --- |
| Leaf and stalk | 0.8 | `FOLIAGE_SPEC` |
| Heads | 0.85 | default |
| Nub | 0.9 | default |
| Mud | 0.95 | 0.25 (`MUD_SPEC`) |
| Rocks | 0.85 | default |

## Stage 5 — Lighting

Skipped. The sheet shows an ordinary sunlit clump: no emissive key and no light (decision 7).

**Studio note (Requires Manual Validation).** In Studio, check that:
- the head tops don't clip under the game sun;
- the leaf base → tip ladder survives the palette export;
- the 0.25-stud stalks stay visible at normal camera distance.

## Stage 6 — VFX

Skipped. The sheet shows no glow, floating seeds, fluff, water or dust (decision 7). There are no sockets; the renders
used vfx=True.

## Modeller's notes for the verifier

**Renders.** Every `*_sheet` render hides the studio floor and uses the 3× lens: `f34_sheet (0, 14)`,
`front_sheet (0, 10)`, `side_sheet (90, 10)`, `rear_sheet (180, 10)`, `r34_sheet (152, 12)` and
`top_tilt_sheet (0, 75)`. The kit views, the exploded shot and the five part shots at (−20, 15) are rendered as well.

**Tools.** `m027.measure()` runs the study's masks on both images. `m027.compare()` writes `M027_sheet_compare.png`.

**Known misses, measured:**
1. **The upper halves of LA and LG read darker than the sheet.** The f34 green bands at h .6–.7 are #7E9631 / #7D922E,
   against the sheet's lightest bands #A2B640 / #B4C750. Neither cause is paint:
   - LG's upper half sits in H3's head and stalk shadow. The key light runs along (0.49, 0.59, −0.64), and no LG
     position inside the composition misses it.
   - LA's axis is almost parallel to the key, so it is grazing-lit whatever its roll.

   The f34 green median and lit and shade quartiles still match within 13.
2. **The side view's heads share is 16.5 against 12.7.** The sheet hides H1 half behind a leaf tip; ours shows it whole.
3. **The side view has 3 green runs at h .55 against the sheet's 6.** The broad 45° leaves overlap from the side. The
   front-leaf run (0.38 W) and back-leaf run (0.19 W) both exceed their targets.
4. **The rear W : H is 1.103, against the 0.90–1.10 band.** The r34 is 1.02 against 0.75–0.95, but the r34 compares by
   counts and shares only (decision 9).
5. **Two parts-shot colours miss:**
   - the leaf part's tip fifth is #B2D446 against #A5BA3F (G +26), because the tip key was raised for the hero's
     grazing-lit upper leaves;
   - the mud part is #8F704F against #806247, although on the hero the mud matches within 3.
6. **The hero's H3 stalk box reads #55671F against #5E7A2A.** The stalk sits partly in LI's and LG's shade.
7. **f34 has 5 green runs at h .55, not 6.** H3's stalk run merges with LI's tip.
8. **The keel is 0.11–0.17**, against §1.4's 0.06–0.09 (see stage 1).

**Accepted by decision:** the top view's W : D is 1.62 against the sheet's 0.98 (decision 4).

## Stage 7 — Verification (round 1)

Independent verifier, 2026-10-28. Read-only: background Blender on port 9880 with `wip/M027_verify.blend`, which was
not saved and on which `build()` was not called. The renders were made fresh with `m027.render_views()` into a
scratchpad folder, with `M.MODEL_RENDERS` redirected, so nothing under `renders/models/M027/` was overwritten. The mesh
checks are my own bmesh/BVH code, cross-checked with `M.audit`, `M.uv_stats` and `K.check`. The colours come from my
own sampler, which uses the study's masks on both images.

**Verdict: FAIL, 6.5 / 10.** The topology, size, UVs and front reads are clean. There are two blockers: the rocks and
mound read as a flat plank in the back views, and the leaf tips are either too bright or too dark in the hero.

### Technical (re-measured)

| Object | Tris | Size (studs) | Shells | NM edges / bowtie verts | Boundary / wire / loose | Zero-area / n-gons | Self-int. pairs | Inverted / interior faces | Min corner | Dup verts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ReedClumpNode | 1888 / 4000 | 5.245 × 2.960 × 4.376 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 / 0 | 5.04° | 0 |
| ReedClumpSeedHead | 140 | 0.644 × 0.657 × 1.730 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 / 0 | 15.3° | 0 |
| ReedClumpStalk | 32 | 0.249 × 0.227 × 2.450 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 / 0 | 5.25° | 0 |
| ReedClumpLeafBlade | 122 | 1.102 × 0.487 × 2.341 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 / 0 | 7.68° | 0 |
| ReedClumpMudBase | 158 | 4.122 × 2.539 × 0.842 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 / 0 | 8.95° | 0 |
| ReedClumpRock | 34 | 0.811 × 0.777 × 0.650 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 / 0 | 15.2° | 0 |

- **Size** is within the decided 5.3 × 2.8 × 4.4 (±0.3 / 0.35 / 0.2) on every axis.
- **Winding and normals:** winding is consistent (0 edges used twice in one direction), the signed volumes are
  positive and `M.audit` reports normals outward. Shading is flat, with no custom normals and no modifiers.
- **Origin and transforms:** the origin is at the bbox bottom centre (offset 0.0000) on all six objects, with rotation
  0 and scale 1.
- **UVs:** `UVMap` on every object; 0 overlap pairs, 0 flipped, 0 zero-area; min gap 0.016, border 0.008; density
  1.0/1.0/1.0. Conformal stretch p95: hero 1.006, mud 1.056.
- **Materials:**
  - 21 slots on the hero, none unused.
  - The keys match `PALETTE`, and the colour comes through the Tint attribute (range 0.945–1.053, broad).
  - `K.check` is clean.
  - Correlation of colour with normal z: leaves 0.16, rock 0.01, stalk −0.06.
  - The heads (+0.85) and mud (−0.54) correlate only because the paint follows position, which is allowed: head_light
    is on the upper half of the axis, so it lands on the up-facing top chamfer, and the dish is darker, so it lands on
    the up-facing top. No colour is chosen by facing.

### Leaf face scores (re-measured on the fused hero)

For each leaf-material component, I took the area-weighted |n·d|. Crossing leaves merge into 5 components.

| Component (tip) | Front | Side | Rear | f34 | side_sheet | kit rear34 | kit front34 | top |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LA (−2.62, −1.48, 2.90) | .615 | .714 | .615 | .644 | .745 | **.201** | **.266** | .263 |
| LB (−1.00, 1.32, 2.82) | .682 | .680 | .682 | .706 | .648 | .821 | .896 | .195 |
| LC (−0.29, −0.78, 1.88) | .684 | .679 | .684 | .620 | .643 | .374 | .302 | .182 |
| LD+LE+LF (−0.06, −0.43, 3.18) | .702 | .686 | .702 | .669 | .681 | .886 | .866 | .059 |
| LG+LH+LI (1.95, 1.48, 3.11) | .566 | .541 | .566 | .672 | .448 | .495 | .704 | .540 |

The decided cameras (front, side, rear) are all ≥ 0.54, so they pass. LA is near edge-on only from the kit
three-quarter cameras, which are not decision cameras; in the renders it hides behind the fan from rear34 and still
reads as a blade from front34. The leaves are broad in every sheet view.

### Shapes per view (re-rendered `*_sheet`, floor hidden; ours / sheet)

| View | W:H | G | S | M | R | M+R | Top-profile err mean / max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | 1.168 / 1.199 | 55.4 / 54.5 | 17.8 / 19.3 | 17.5 / 17.1 | 9.3 / 9.1 | 26.8 / 26.2 | .017 / .06 |
| front | 1.174 / 1.090 | 55.1 / 53.8 | 18.0 / 18.9 | 17.5 / 18.6 | 9.4 / 8.7 | 26.9 / 27.3 | .062 / .33 |
| side | 0.630 / 0.633 | 52.6 / 56.1 | 16.5 / 12.7 | 19.1 / 21.1 | 11.9 / 10.0 | 31.0 / 31.1 | .121 / .39 |
| rear | 1.103 / 0.977 | 48.6 / 51.9 | 20.0 / 19.2 | 22.4 / 21.6 | 9.0 / 7.3 | 31.4 / 28.9 | (not compared) |
| r34 | 1.020 / 0.826 | 48.5 / 49.1 | 20.9 / 22.0 | 22.6 / 18.6 | 8.0 / 10.3 | 30.6 / 28.9 | (counts only) |
| top_tilt | 1.622 / 0.976 | 52.0 / 54.0 | S+M 36.9 / 31.5 | | 11.2 / 14.5 | | (decision 4) |

- **Heads.** The f34 has three peaks at f .20 / .40 / .70 (.84 / .94 / 1.0), with dips of .70 and .65 against the
  sheet's .68 / .62. That passes. The heads are 8-sided capsules with chamfers and a dark nub, and they lean outward
  as on the sheet.
- **Neck and splay (f34 width per height).**

  | h | .1 | .3 | .4 | .5 | .6 |
  | --- | --- | --- | --- | --- | --- |
  | Ours | .77 | .65 | .84 | .73 | .83 |
  | Sheet | .74 | .56 | .75 | .83 | .81 |

  The neck exists but is 0.02 wider than its band (0.55–0.63). The fan reaches its widest at h .4 instead of h .5–.6,
  so it splays about 0.1 H too low.
- **Leaf runs at h .55:** f34 5 against 6; front 4 against 6; side 3 against 6. The leaves are broad, but they overlap
  more than the sheet's "spacing between leaves".
- **Side.** The two visible heads cluster at the top (f .35–.6, h .8–1.0). The sheet shows one tall head and a low head
  half hidden at h .55–.65. The sheet's side is itself inconsistent with its front, so this is a minor.
- **Rocks and mound.** I measured each rock against the mound mesh: the rock's top z, and the highest mud within 0.8 of
  its centre.

  | Rock | Top z | Mud nearby | Note |
  | --- | --- | --- | --- |
  | RK1 | 0.78 | 0.67 | |
  | RK2 | 1.04 | 0.69 | |
  | RK3 | 0.87 | 0.67 | |
  | RK4 | **0.72** | 0.75 | top below the mud |
  | RK5 | **0.62** | 0.84 | 0.22 below the rim |

  The spec puts rock tops at z 0.85–1.05, sitting on the rim. Rock runs at h .16: rear 2 against 3, r34 1 against 3,
  side at .08–.26 / .64–.67 / .91–.94 against .12–.39 / .41–.55 / .80–.91.

### Colours (sampled on both images; ours / sheet, median, with the ΔRGB of the median)

| Region | Ours | Sheet | ΔRGB |
| --- | --- | --- | --- |
| f34 leaves overall (G) | #6D8529 | #6A8229 | +3 +3 0 |
| f34 leaf base band (h .2–.32) | #425717 | #637A22 | −33 −35 −11 |
| f34 leaf mid band (h .4–.5) | #718A2B | #6C842A | +5 +6 +1 |
| f34 leaf top band (h .55–.72) | #809932 | #90A739 | −16 −14 −7 |
| f34 G height bands h .6 / .7 | #7E9631 / #7D922E | #A2B640 / #B4C750 | about −36 / −55 |
| LA tip | #90A837 | #A6BA43 | −22 −18 −12 |
| LA mid | #657B24 | #738D2D | −14 −18 −9 |
| **LG tip** | **#667B25** | **#ACC148** | **−70 −70 −35** |
| **LH tip** | **#D3F255** (lit #D6F556) | **#9BB13A** | **+56 +65 +27** |
| Parts-shot leaf fifths | #71942C #7EA230 #8EB436 #A0C43E **#C2E34D** | #7A952C #87A12E #92AB31 #A8BE40 #A5BA3F | tip +29 +41 +14 |
| H3 stalk (f34) | #55671F | #5E792A | −9 −18 −11 |
| Parts-shot stalk | #7B9330 | #7C9230 | −1 +1 0 |
| Heads f34 (v ≥ .5) | #CE965A (lit #EDB06F, shade #976C3F) | #CA9258 (#F2B776, #9B6F44) | +4 +4 +2 |
| Heads front | #CE955A | #CE945A | 0 +1 0 |
| Parts-shot head | #D69C5E | #D1975C | +5 +5 +2 |
| Nubs f34 / part | #664D2E / #6B4E31 | #6C4F34 / #5B4427–#6C4F33 | −6 −2 −6 |
| Mud f34 | #836548 (lit #9B7956, shade **#413121**) | #846549 (#9F7B58, #5F4C37) | −1 0 −1 (shade −30) |
| Parts-shot mud | #8F704F | #806247 | +15 +14 +8 |
| Rock f34 | #7F746D (lit #9B8D84) | #83756F (#AF9E90) | −4 −1 −2 (lit −20) |
| Parts-shot rock | #897D75 | #8C8078 | −3 −3 −3 |
| Side / rear (heads, mud, rock, leaf top) | | | all 15–37 darker |

The side and rear darkening comes from the studio rig. Its key light comes from the front, while the sheet lights every
cell from the camera side. This is not paint, and no fix is asked for it.

### Blockers

1. **The rocks and mound read as a flat plank with studs in the back views** (rear, side, r34). From behind, the mound
   shows a 0.3-tall vertical side wall with a flat top. RK4's top is below the mud beside it and RK5's is 0.22 below
   the rim, so both sit on the wall like studs instead of on the rim as on the sheet. Rock runs at h .16 are 2 / 1
   against the sheet's 3 / 3 in the rear and r34.
   **Fix (in `m027.py`):**
   - **Rock placement:** move each rock's centre to 0.92–1.0 × the local mound radius at the rim height. Raise each
     rock so its top is at z 0.85–1.05 and at least 0.12 above the highest mud within 0.8 of it; RK4 and RK5 most of all.
   - **Rock size and sinking:** bring RK4 back to × 1.0 and RK5 to × 0.95 (from 0.9 / 0.85). Keep about 35 % of each
     rock's height sunk into the rim.
   - **Mound profile:** replace the vertical wall ring `(0.42, 1.02)` with a sloped `(0.38, 0.97)`. Add a little of the
     lump amplitude to the rim ring as well, so the back silhouette shows rounded lumps (rim z varying ±0.08 between
     lumps).
   - **Re-check:** rock runs at h .16, with 3 runs in rear_sheet and r34_sheet. R share within ±4 everywhere: watch the
     rear, now 9.0 against 7.3.
2. **The leaf tips don't match the sheet's base → tip gradient in the hero.** Two problems:
   - LH's tip renders as a near-neon #D3F255, +56 against the sheet. The parts-shot tip fifth is #C2E34D, +29/+41
     against #A5BA3F. The `m027_leaf_tip` key was raised to compensate for shadowed leaves.
   - LG's tip is −70 (#667B25 against #ACC148) and LA's is −22. The f34 G bands at h .6–.7 are #7E9631 / #7D922E
     against the spec gate "within 15 of #B4C750, lightest band".

   **Fix:**
   - (a) Recalibrate `m027_leaf_tip` on the unshadowed parts shot, so the tip fifth lands within 15 of #A5BA3F. That
     makes the key about 10–15 % darker in linear light, and LH then lands near the sheet.
   - (b) For LA and LG only, start the tip ladder earlier: leaf → tip over t 0.40–0.70 instead of 0.58–0.88. This is
     the same per-leaf position shift the builder already gives LC/LD/LE, not paint by facing.
   - (c) Move LG's upper half out of H3's cast shadow under the kit key (0.49, 0.59, −0.64). For example, LG's tip
     +0.25 X and −0.2 Y, or H3's lean 2–3° less toward +X. Keep LG's face score ≥ 0.35 and the H3 stalk run clear.
   - **Re-check:** LG tip and LA tip within 20 of #ACC148 / #A6BA43; LH tip within 20 of #9BB13A; f34 band h .6 or .7
     the lightest.

### Minors (record; fix only if cheap)

- **f34 fan:** the neck at h .3 is 0.65 against 0.55–0.63, and the fan is widest at h .4 (0.84 against 0.75) instead of
  h .5 (0.73 against 0.83). Lifting LA's and LH's mid-length about 0.2 would fix both.
- **Leaf runs:** green runs at h .55 are f34 5, front 4 and side 3, against 6. The leaves overlap more than the sheet's
  "spacing between leaves".
- **Side view:**
  - the top profile error is mean .12 / max .39: two heads at the top, and the sheet's low half-hidden head is not
    reproduced. This is a sheet inconsistency, and the hero governs;
  - S 16.5 against 12.7 (within ±4).
- **W:H:** the rear is 1.103 against 0.90–1.10. The r34 is 1.02 against 0.75–0.95, but it compares by counts only.
- **Top view:** the leaf tips cover about 225°, not ≥ 300°, so the back and front-right are empty. This is tied to
  decision 4.
- **Exploded shot:** the leaves are posed near edge-on, so they read as thin slivers. The sheet's exploded leaves are
  broad. Rotate the EXPL leaf copies so their faces point at the camera.
- **SeedHead part:** L : Ø including the nub and peg is 2.66, against 2.4–2.6.
- **Mud part shot:** #8F704F against #806247, +15. On the hero the mud matches within 1.
- **Lighting depth:** the hero's mud shade quartile is −30 (#413121 against #5E4B37) and the rock lit quartile −20,
  from deeper contact shadows and a weaker bounce than the sheet. This is not paint.
- **H3 stalk:** −18 G, because it sits in LI's and LG's shade.
- **Keel:** 0.11–0.17, thicker than §1.4. Already explained by the modeller, and it reads right.

### What passes

- **Topology and technical requirements:** every object is clean on every requirement I re-measured.
- **Size, budget and parts:** the hero size and budget pass, and all five parts are present and clean.
- **Leaves:** 9 broad keeled leaves, none edge-on from the front, side or rear.
- **Heads:** three fat 8-sided heads with nubs, three peaks with real dips, axes matching the sheet.
- **Front read:** the f34 and front shares are within 1.5 points and the f34 profile is within .06.
- **Colours:**
  - the overall medians of the heads, nubs, stalks (part), mud (hero) and rocks are within 6;
  - the head bottom → top lift is mild, as on the sheet;
  - no colour by facing.

## Round 2 fixes (modeller)

Fresh modeller, 2026-10-28, in a background Blender (bgmcp port 9880, `wip/M027.blend`, saved after the final build).
Every change is in `m027.py` and commented with "round 2". The final `build()` takes 18.5 s without renders and 38 s
with them. The hero guard passes on attempt 0, and `problems` is empty.

### Blocker 1: rocks and mound from behind (fixed)

**Mound:**
- The side ring `(0.42, 1.02)` is now `(0.38, 0.97)`, a slope instead of a wall.
- The rim ring rises and falls with the lumps (`RIM_LUMP_Z` ±0.08: high on a lump, low in a crease).

**Rock placement** (new `rocks()`), applied to each rock:
- **Position:** the centre sits on the rim, at `ROCK_RIM_F` 0.96 × the rim ring's radius at the rock's azimuth (found by
  `_rim_point`).
- **Height:** the base sits at the surface − 0.35 × the height. The rock is then lifted or lowered so its top lies in
  z 0.85–1.05 and at least 0.12 above the highest mound vertex within 0.8.
- **Per-rock overrides** (`ROCK_PLACE`):
  - RK1: rim fraction 1.0, top 0.92, moved to az 165 (§2.1's back-left). It now shows left of RK2 in the hero, and its
    foot gives the r34 its third rock run.
  - RK4: top 0.98.
  - RK5: rim fraction 1.0, top 0.95. RK4 and RK5 are the rocks nearest the side and rear cameras; lowering them keeps
    the rear's green share within band.
- **Sizes:** RK4 is back to §2.1 × 1.0 and RK5 to × 0.95, both × `ROCK_SCALE` 1.1 as before.
- `build()` now adds a problem whenever a rock's top leaves 0.85–1.05 or sits less than 0.12 above the mud near it.

| Rock | Rim fraction | Top z | Highest mud within 0.8 | Clearance | Sunk (fraction of height under the surface at the centre) |
| --- | --- | --- | --- | --- | --- |
| RK1 | 1.0 | 0.92 | 0.77 | 0.149 | 0.60 |
| RK2 | 0.96 | 1.04 | 0.64 | 0.398 | 0.42 |
| RK3 | 0.96 | 1.01 | 0.68 | 0.331 | 0.35 |
| RK4 | 0.96 | 0.98 | 0.74 | 0.236 | 0.50 |
| RK5 | 1.0 | 0.95 | 0.81 | 0.139 | 0.65 |

RK1 and RK5 sit deeper than 35 % because their tops were lowered. They still stand 0.14–0.15 clear of the mud.

**Rock runs at h .16 (ours / sheet):**

| View | Ours | Sheet |
| --- | --- | --- |
| rear_sheet | 3: .20–.30, .56–.66, .84–.93 | 3 |
| r34_sheet | 3: .28–.41, .70–.82, .97–1.0 | 3 |
| f34_sheet | 3: .13–.15, .23–.38, .60–.72 | .10–.20, .21–.35, .62–.74 |

- The r34's third run is thin: the far rock (RK1) only just reaches the h .16 row.
- The side still shows 2 runs against 3.

**R share (ours / sheet, all within ±4):**

| View | Ours | Sheet |
| --- | --- | --- |
| f34 | 10.0 | 9.1 |
| front | 10.2 | 8.7 |
| side | 12.8 | 10.0 |
| rear | 9.9 | 7.3 |
| r34 | 9.1 | 10.3 |

From behind, the rocks now sit on the rim with their tops above it, as on the sheet, not on the wall. The mound still
reads a little thinner and less lumpy from behind than the sheet's.

### Blocker 2: leaf tips (LH and LG fixed; LA not)

- **(a) Tip key:**
  - Re-calibrated on the unshadowed parts shot: the tip fifth was #C2E34D against #A5BA3F, so the key is × (0.70, 0.64,
    0.67) in linear light.
  - `m027_leaf_tip` goes from #9DB849 to **#85963C**, back near pass 1's dome value #899D41. The cut is about 33 %, not
    the suggested 10–15 %; that is what the measurement needed.
  - New helpers: `m027.tips()`, `leaf_tips()` and `leaf_fifths()`.
- **(b) Ladder:** `LEAF_TIP_BANDS` sets these leaf → tip bands:
  - LA and LG: 0.40–0.70;
  - LH: 0.66–1.06, so its very tip is a 75 % mix. The sheet's LH tip, #9BB13A, is darker than the other tips.

  These are position shifts only, like LC/LD/LE's.
- **(c) LG and H3:** H3's cast shadow is measured by the new `shade()`, which casts rays to the verified studio key
  (0.492, 0.587, −0.643), and is reported in `build()["shade"]`. It covered 0.65 of LG's upper half and now covers
  **0.22**.
  - **LG's tip** moved (2.30, 1.30, 3.05) → (2.40, 0.92, 2.85).
  - **H3:** foot (0.15, 0.30) → (0.20, 0.30); head bottom (0.82, 0.20, 2.85) → (0.76, 0.24, 2.875). It now leans 12.9°
    instead of 15.6°, and its head top stays at x 1.11, so the f34 peak is still at f .70.
  - **Rejected:**

    | Option | LG shade | Why not |
    | --- | --- | --- |
    | Tip (2.55, 1.10) | 0.50 | too much shade |
    | Tip (2.55, 0.75) | 0.10 | the side lost its back leaf (D : H 0.57); the f34 LG tip moved to f .91 |
    | H3 leaning less about its old foot | | the head peak went to f .65, f34 profile max error 0.43; LI touched S3; an enclosed mud sliver forced a hero retry |
  - LG face scores: 0.515 minimum, front / rear 0.60.
  - Clearances above z 0.75 are at least 0.034 everywhere.

**Re-check, f34_sheet tips** (my sampler: the median of the green pixels within 0.06 W of each tip):

| Tip | Ours | Sheet (my sampler) | Verifier's target | Result |
| --- | --- | --- | --- | --- |
| LG | #ACBD42 | #B7CA4F | #ACC148 | within 6 of the verifier's target |
| LH | #A7BD41 | #A7B748 | #9BB13A | +12 / +12 / +7 against the verifier's target |
| LA | **#7A882D** | #A4B843 | #A6BA43 | **about −43, not fixed** |

**Why LA is not fixed.** Its axis (−0.55, −0.45, 0.70) points almost straight at the studio sun (dot −0.99).
- The camera-facing side of its tip gets a sun factor of 0.20, against LG 0.99 and LH 0.96.
- A sweep of LA's face roll, twist and arch at its sheet tip position reached at most 0.29.
- Reaching 0.40 needs the tip at Y −0.9, which removes the side view's front leaf (sheet Y −1.5).
- Painting LA brighter would bake the studio sun into the asset, so I left it. It is a lighting difference, not paint
  or shape.

**Other colour checks:**
- **f34 green bands h .1–.7:**
  - ours `#405218 #425818 #54691E #738A2C #7E9431 #A2B43F #AEBF48`;
  - sheet `#4D6216 #4F661D #5B7225 #6C842A #7E952F #A2B640 #B4C750`.

  The lightest band is h .7, and h .6 / .7 are within 6.
- **Parts-shot leaf fifths:**
  - ours `#71952C #7FA230 #8EB436 #97B939 #A9BF42`;
  - sheet `#7A952C #86A12E #8EA830 #A5BA3D #A5BA3F`.

  The tip is within 5.

### Minors

- **f34 neck (fixed):** LA's arch went 35 → 40 and LH's 25 → 45.
  - f34 width per height at h .1 / .3 / .4 / .5 / .6: **0.74 / 0.61 / 0.83 / 0.78 / 0.87**, against the sheet's .74 / .56 /
    .75 / .83 / .81. The neck is now inside 0.55–0.63.
  - The fan is still widest at h .4 and .6 rather than .5.
  - LA at 44–50° touches H1's stalk.
- **Mud (partly fixed):** the mud keys are × 0.93 in linear light (mud #755E45, mud_dark #604D3A).
  - Hero f34 mud: **#846545** against #846549.
  - Parts-shot mud: **#8D6E4D** against #806247 (+13; it was +15, and +18 after the sloped ring).
  - The rest of the gap is the lone part being unshadowed. A part-only Tint would make the exported part darker than the
    hero's mud, so I didn't add one.
- **Exploded leaves (fixed):** each leaf copy is turned about Z (at most 40°) to face the camera (`EXPL_FACE`). The
  area-weighted |n · camera| went from 0.46–0.78 to 0.82–0.90.
- **Leaf width:** `LEAF_W_SCALE` 1.08 → 1.12. The rocks above the rim had pushed the side and rear green below their
  bands.
- **LB's tip:** Y 1.35 → 1.55. This restores the side's back depth once LG came forward: side D : H 0.604, band
  0.58–0.70.

### Shapes and shares (final; ours / sheet; G / S / M / R)

| View | W : H | G | S | M | R | Profile error mean / max | Runs at h .55 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | 1.154 / 1.199 | 54.4 / 54.5 | 17.9 / 19.3 | 17.6 / 17.1 | 10.0 / 9.1 | .02 / .06 | 5 / 6 |
| front | 1.165 / 1.09 | 54.0 / 53.8 | 18.1 / 18.9 | 17.7 / 18.6 | 10.2 / 8.7 | .065 / .39 | 5 / 6 |
| side | 0.604 / 0.633 | 52.9 / 56.1 | 16.6 / 12.7 | 17.8 / 21.1 | 12.8 / 10.0 | .12 / .41 | 3 / 6 |
| rear | 1.094 / 0.977 | 48.1 / 51.9 | 20.5 / 19.2 | 21.4 / 21.6 | 9.9 / 7.3 | – | 5 / 5 |
| r34 | 1.00 / 0.826 | 48.3 / 49.1 | 21.0 / 22.0 | 21.5 / 18.6 | 9.1 / 10.3 | – | 5 / 5 |

Every share is within ±4 (r34 ±5). The side's G (−3.2) and S (+3.9) and the rear's G (−3.8) are close to the edge.

### Technical (final)

| Object | Tris | Size (studs) |
| --- | --- | --- |
| ReedClumpNode | 2140 / 4000 | 5.26 × 3.00 × 4.42 |
| ReedClumpSeedHead | 140 | 0.64 × 0.66 × 1.73 |
| ReedClumpStalk | 32 | 0.25 × 0.23 × 2.45 |
| ReedClumpLeafBlade | 122 | 1.10 × 0.49 × 2.34 |
| ReedClumpMudBase | 158 | 4.04 × 2.49 × 0.83 |
| ReedClumpRock | 34 | 0.81 × 0.78 × 0.65 |

- **Topology:** on all six objects:
  - 1 shell each;
  - 0 non-manifold edges and 0 bowtie verts;
  - 0 boundary, wire or loose elements;
  - 0 zero-area faces and 0 n-gons;
  - normals outward;
  - 0 inverted faces and 0 self-intersecting pairs;
  - no corner under 5°.
- **Checks:** `K.check` is clean, and the size is within tolerance.
- **UVs:** 0 overlaps and 0 flipped; min gap 0.016; density 1.0; hero stretch p95 1.007.
- **Leaf face scores:** every score is ≥ 0.495. The lowest are LH 0.495 and LG 0.515.

**Final palette:**

| Key | Hex |
| --- | --- |
| leaf | #719032 |
| leaf_base | #5E7C2B |
| leaf_tip | **#85963C** |
| stalk | #708734 |
| head | #AF8251 |
| head_light | #BA8F5E |
| nub | #503C23 |
| mud | **#755E45** |
| mud_dark | **#604D3A** |
| rock | #736C6A |
| rock_dark | #5A5657 |

## Stage 7 — Verification (round 2)

Independent verifier (not the round-1 verifier and no other stage), 2026-10-29. Read-only: background Blender on port
9880 with `wip/M027_verify.blend`, not saved, `build()` not called, session stopped at the end. Fresh renders came from
`m027.render_views()` with `M.MODEL_RENDERS` redirected to my scratchpad, so `renders/models/M027/` was not touched. The
mesh checks are my own bmesh/BVH code, cross-checked with `M.audit`, `M.uv_stats` and `K.check`.

**Verdict: PASS, 8 / 10.** Both round-1 blockers meet their targets. Everything left is a minor or the accepted LA
lighting miss.

### Technical (re-measured)

| Object | Tris | Size (studs) | Shells | NM edges / bowtie | Boundary / wire / loose | Zero-area / n-gons | Self-int. | Inverted | Bad winding | Min corner | Dup verts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ReedClumpNode | 2140 / 4000 | 5.262 × 3.005 × 4.415 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | 0 | 5.01° | 0 |
| ReedClumpSeedHead | 140 | 0.644 × 0.657 × 1.730 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | 0 | 15.3° | 0 |
| ReedClumpStalk | 32 | 0.249 × 0.227 × 2.450 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | 0 | 5.25° | 0 |
| ReedClumpLeafBlade | 122 | 1.102 × 0.487 × 2.341 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | 0 | 7.68° | 0 |
| ReedClumpMudBase | 158 | 4.042 × 2.490 × 0.828 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | 0 | 8.95° | 0 |
| ReedClumpRock | 34 | 0.811 × 0.777 × 0.650 | 1 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 | 0 | 0 | 15.2° | 0 |

- **Size:** inside 5.3 × 2.8 × 4.4 (±0.3 / ±0.35 / ±0.2) on every axis; D 3.005 is 0.145 inside the limit.
- **Origin and transforms:** bbox bottom centre at offset 0.0000 on all six; rotation 0, scale 1; no modifiers, no
  custom normals, flat shading; positive signed volumes, `M.audit` normals outward. `K.check` is clean.
- **UVs:** `UVMap` on all six; 0 overlaps, 0 flipped; min gap 0.016, border 0.008; density 1.0; hero conformal stretch
  p95 1.007 (worst 1.082), mud p95 1.031.
- **Materials:** 21 slots on the hero, none unused. The keys (Mix A, multiplied by the `Tint` corner attribute) read
  back exactly as the final palette above.
- **No colouring by facing** (area-weighted correlation of face colour × Tint with normal z; then with height removed):
  leaves 0.04 (−0.14 after height), rock 0.01, stalk 0.19 (30 faces; 0.15), heads 0.65 → **0.05** after height, mud
  −0.40 → **−0.06** after height. The head and mud correlations are explained by position (head_light on the upper
  body, darker dish), which is allowed. The builder's paint and `_mottle` use positions only.

### Leaf face scores (fused hero, area-weighted |n·d| per leaf-material component)

| Component (tip) | Front | Side | Rear | f34 | r34 (152, 12) | Kit front34 | Top |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LA (−2.63, −1.50, 2.90) | .639 | .746 | .570 | .643 | **.199** | .369 | .256 |
| LB (−1.01, 1.50, 2.83) | .689 | .654 | .611 | .695 | .798 | .862 | .225 |
| LC (−0.29, −0.80, 1.88) | .645 | .644 | .707 | .623 | .376 | .343 | .190 |
| LD+LE+LF (−0.07, −0.45, 3.18) | .673 | .674 | .692 | .659 | .840 | .761 | .092 |
| LG+LH+LI (2.05, 1.09, 2.93) | .653 | .455 | .493 | .677 | .511 | .746 | .501 |

(An 11-face leaf sliver cut off by a stalk crossing scores .59–.65.) Every decision camera is ≥ 0.455. LA's 0.199
from the r34 camera is the same as round 1 (0.201): it shows there as a thin blade beside H3's head (minor below).

### Blocker 1 (rocks and mound from behind): fixed

Rock tops and the highest mud vertex within 0.8 of each rock centre (my own component split of the rock material):

| Rock (az) | Centre | Top z | Mud near | Clearance |
| --- | --- | --- | --- | --- |
| 22° | (1.16, 0.46) | 0.980 | 0.744 | 0.236 |
| 116° | (−0.50, 1.04) | 0.950 | 0.811 | 0.139 |
| 167° | (−1.83, 0.44) | 0.920 | 0.771 | 0.149 |
| 212° | (−1.16, −0.73) | 1.040 | 0.879 | 0.161 |
| 320° | (0.76, −0.64) | 1.012 | 0.681 | 0.331 |

- Every top is inside 0.85–1.05 and at least 0.139 clear of the mud (target ≥ 0.12).
- The mound's back ring is now a slope (radius 0.95–1.28 falling from z 0.83 to 0), not a wall. The rim's highest mud
  per 15° of azimuth varies 0.62–0.88, so the lumps show in the silhouette.
- Rock runs at h .16: rear_sheet **3** (.20–.30, .56–.66, .84–.93) against 3; r34_sheet **3** (.28–.41, .70–.82,
  .97–1.0, the third thin) against 3; f34 3 against 3; side 2 against 3 (minor).
- R share (ours / sheet): f34 10.0 / 9.1, front 10.2 / 8.7, side 12.8 / 10.0, rear 9.9 / 7.3, r34 9.1 / 10.3. All
  within ±4.
- In the rear and r34 renders the rocks sit on the rim with their tops above it; it no longer reads as a plank with
  studs. The back of the mound is still smoother and flatter-topped than the sheet's (minor).

### Blocker 2 (leaf tips): LG and LH fixed; LA accepted

Tip medians in f34_sheet with `m027.leaf_tips` at three radii (0.035 / 0.06 / 0.09 W), each on both images; the picks
land at the same positions in both (LA f .00 h .60, LG f .88 h .72, LH f 1.0 h .47):

| Tip | Ours (r .06) | Sheet (r .06) | Round-1 target | Δ to target | Range across radii, ours / sheet |
| --- | --- | --- | --- | --- | --- |
| LG | #ACBD42 | #B7CA4F | #ACC148 | 0 −4 −6 | #ABBD42–#ADBE43 / #B7C94D–#B7CA50 |
| LH | #A7BD41 | #A7B748 | #9BB13A | +12 +12 +7 | #A7BD41–#A7BE42 / #9CB23B–#B4C14F |
| LA | #7A882D | #A4B843 | #A6BA43 | −44 −50 −22 | stable / #A5B943–#A8BA47 |

- LG and LH are within 20 of their targets (pass). LA is the accepted studio-lighting miss (main-session ruling): its
  axis points almost straight at the key light, and brightening it would be colouring by facing.
- f34 green bands h .1–.7, ours `#405218 #425818 #54691E #738A2C #7E9431 #A2B43F #AEBF48`, sheet `#4D6216 #4F661D
  #5B7225 #6C842A #7E952F #A2B640 #B4C750`. The lightest band is h .7 (−6 −8 −8); h .6 is within 2. The two lowest
  bands are 12–13 darker (contact shade).
- Parts-shot leaf fifths, ours `#71952C #7FA230 #8EB436 #97B939 #A9BF42`, sheet `#7A952C #86A12E #8EA830 #A5BA3D
  #A5BA3F`. The tip fifth is +4 +5 +3; the mid fifth is +6 G and the fourth fifth −14 R.
- No leaf reads neon any more.

### Shapes per view (fresh `*_sheet` renders; ours / sheet)

| View | W : H | G | S | M | R | Profile err mean / max | Green runs h .55 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | 1.154 / 1.199 | 54.4 / 54.5 | 17.9 / 19.3 | 17.6 / 17.1 | 10.0 / 9.1 | .02 / .06 | 5 / 6 |
| front | 1.165 / 1.090 | 54.0 / 53.8 | 18.1 / 18.9 | 17.7 / 18.6 | 10.2 / 8.7 | .065 / .39 | 5 / 6 |
| side | 0.604 / 0.633 | 52.9 / 56.1 | 16.6 / 12.7 | 17.8 / 21.1 | 12.8 / 10.0 | .12 / .41 | 3 / 6 |
| rear | 1.094 / 0.977 | 48.1 / 51.9 | 20.5 / 19.2 | 21.4 / 21.6 | 9.9 / 7.3 | .175 / .39 | 5 / 5 |
| r34 | 1.000 / 0.826 | 48.3 / 49.1 | 21.0 / 22.0 | 21.5 / 18.6 | 9.1 / 10.3 | (counts only) | 5 / 5 |
| top_tilt | 1.654 / 0.976 | 55.3 / 54.0 | 13.9 / 12.9 | 20.9 / 18.6 | 9.8 / 14.5 | (decision 4) | |

- f34 width per height h .1 / .3 / .4 / .5 / .6: ours .74 / .61 / .83 / .78 / .87, sheet .74 / .56 / .75 / .83 / .81.
  The neck at h .3 is inside 0.55–0.63.
- Side by side (`M027_sheet_compare.png` regenerated in my scratchpad): the f34 and front match in head count, lean,
  peaks, leaf fan and rock layout. The side shows two heads at the top, against the sheet's one tall head and a low
  half-hidden one. The rear and r34 read as the same plant with rocks on the rim.

### Colours (study masks on both images; median, ours / sheet, ΔRGB)

| Region | Ours | Sheet | ΔRGB |
| --- | --- | --- | --- |
| f34 G (median / lit / shade) | #70862B / #A0BF3E / #3E5115 | #6A8229 / #9FB43D / #3E5412 | +6 +4 +2 / +1 +11 +1 / 0 −3 +3 |
| f34 heads | #C99258 / #EBAE6E / #6F5030 | #C99057 / #F2B676 / #986B3F | 0 +2 +1 / −7 −8 −8 / −41 −27 −15 |
| f34 mud | #846545 / #967552 / #443423 | #846549 / #9F7A58 / #5E4B37 | 0 0 −4 / −9 −5 −6 / −26 −23 −20 |
| f34 rock | #7E746D / #9B8E84 / #4F4946 | #83756F / #AF9E91 / #5E554C | −5 −1 −2 / −20 −16 −13 / −15 −12 −6 |
| front G / heads / mud / rock | #70852A / #C99158 / #836445 / #7E746D | #688228 / #CC9258 / #86684B / #84776E | +8 +3 +2 / −3 −1 0 / −3 −4 −6 / −6 −3 −1 |
| side G / heads / mud / rock | #5E7725 / #9B7045 / #65503A / #706865 | #6F8729 / #C38A52 / #86684A / #87776E | −17 −16 −4 / −40 −26 −13 / −33 −24 −16 / −23 −15 −9 |
| rear G / heads / mud / rock | #5D7824 / #BC8A56 / #6C553C / #706865 | #698327 / #CE9359 / #896A4C / #837469 | −12 −11 −3 / −18 −9 −3 / −29 −21 −16 / −19 −12 −4 |
| Part head / stalk / mud / rock | #DA9C5E / #7B9330 / #8D6E4D / #897D75 | #D0955A / #7C9431 / #806247 / #8F857E | +10 +7 +4 / −1 −1 −1 / +13 +12 +6 / −6 −8 −9 |

The f34 and front medians are all within 8. The side and rear are 10–40 darker because the studio key comes from the
front while the sheet lights every cell from the camera side. That is lighting, not paint, as in round 1.

### Items

Blockers: **none.**

Minors (record; none needs a fix before commit):
1. **LA tip −44 / −50 / −22 in the hero** (#7A882D against #A6BA43). Accepted by the main session as a studio-lighting
   miss; no paint change.
2. **LA face score 0.199 from the r34 camera** (decision 10's hard floor is 0.25). It shows as a thin blade beside H3's
   head in r34_sheet; the r34 compares by counts and shares only. If ever wanted: roll LA's face 10–15° toward +X
   about its axis and re-check the front and side scores.
3. **Rear mound still a little smooth and flat-topped** against the sheet's lumpier back, and the side shows 2 rock runs
   against 3.
4. **Side view:** two heads at the top against the sheet's tall head plus a low half-hidden one; S 16.6 against 12.7;
   3 green runs against 6. This is a sheet inconsistency (the hero governs).
5. **Leaf runs at h .55:** 5 against 6 in the f34 and front. The leaves are broader and overlap more than the sheet's
   "spacing between leaves".
6. **f34 fan** is widest at h .4 and .6 (0.83 / 0.87) rather than h .5 (0.78 against 0.83).
7. **W : H:** rear 1.094 (inside 0.90–1.10 by 0.006); r34 1.00 against 0.826 (counts only); top 1.65 (decision 4).
8. **Parts-shot colours:** mud +13 (the unshadowed lone part; the hero's mud matches within 4); head +10.
9. **Lighting depth:** the f34 shade quartiles of the heads (−41 R), mud (−26) and rock lit quartile (−20) are darker
   than the sheet, from deeper contact shadow and weaker bounce. Not paint.
10. **Lowest two f34 green bands** 12–13 darker than the sheet (contact shade at the leaf bases).
