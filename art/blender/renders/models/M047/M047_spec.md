# 047 Old Pine — spec

Reference: `art/blender/assets/references/047.png` (1024 × 1536 px). The sheet's title is "OLD PINE", subtitle "TREE MODEL
– INDIVIDIUAL ASSET PRODUCTION REFERENCE" (sic), "PAGE 48/132", with "FLINTBORN / STYLIZED 3D GAME ART / TREES, FIRS &
SAPLINGS" at the top right; the footer reads "FLINTBORN — INDIVIDUAL MODEL STUDY". INDEX.md row 47 calls it "Old Pine
Flintborn model study".
Builder: `art/blender/kit/mcp/m047.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7). Trees: "a detailed skeleton plus foliage clumps; roots,
branches and every view matter" (memory `kit-tree-detail`). **Here, unlike 042 and 045, the skeleton is the subject:**
a massive leaning forked trunk, five angled limbs that plug into sockets, seven buttress roots, cut stubs and a knot
hole, all visible between the foliage clusters from every side and from above.

Sheet text:
- **Hero cells:** "ASSEMBLED VIEW / FRONT THREE-QUARTER" and "REAR THREE-QUARTER" (both e ≈ 10–12°, §3.1).
- **"ORTHOGRAPHIC VIEWS (CONSISTENT MODEL)":** "FRONT", "SIDE", "REAR", "TOP". Front, side and rear are low views (e ≈
  6–7°); the top a plan. **The side cell is not consistent with the others** (§3.2).
- **"EXPLODED CONSTRUCTION":** labels "Canopy Tier" (arrow to the upper-left branch piece), "Branch (angled)" (arrow to
  the lower-left branch piece), "Forked Trunk", "Rocks / Base". Dashed arrows plug five branch pieces into sockets on the
  trunk: the crown piece into the leader's top socket, the upper-left piece into a side socket near the leader's top,
  the lower-left piece into the left fork, the right piece into the right fork, the lower-right piece into a low socket
  on the trunk's right; rocks and plants drop onto the ground.
- **"KEY CONSTRUCTION CLOSE-UPS"** (paraphrased): "BRANCH JOIN": an angled branch plugs into a trunk socket, flat faces
  for a clean join. "BASE / UNDERSIDE": root flares make a stable base; simple low-poly rock and plant clusters.
  "FOLIAGE JUNCTION": the canopy cluster sits on the branch on a flat cut surface; consistent thickness, simple forms.
- **"MATERIAL PALETTE (COLORS)":** six **unlabelled** swatches: dark green, mid green, light olive-lime, bark, a tan and
  a light grey (§5.1).
- **"MODELING NOTES"** (paraphrased): chunky, readable, low-poly forms; broad flat-shaded faces, no texture noise; the
  trunk built from simple extruded branches with flat join faces; foliage clusters are faceted low-poly blobs with no
  individual leaves; the base uses simple angular rocks and grouped plants; one consistent silhouette and proportion in
  every view.
- **Game context and the old kit:**
  - **W04 Pines & Firs, row 4 `OldPine`** (`art/blender/scripts/kit/W04/old_pine.py`, goals
    `art/blender/renders/kit/W04/old_pine_goals.md`) is the old kit's take, from a different reference row: 22.7 × 22.7
    × 26.4, 7254 tris, a slender fluted trunk (a quarter to a third of the crown width), fork at 14, six star pads on a
    ring. `MODEL_PROGRESS.md` row 59: "blob canopy (ref angular clumps on forked limbs); cone trunk". Its unmet goal V8g
    (knot hole doesn't read) applies here too. **W04 owns every `OldPine*` name** (§8).
  - **Sister sheets:** 042 Young Fir (`TieredFir`, 16 tall, committed), 045 Pine Sapling (`PineSapling`, 10 tall, being
    modelled), 049 Classic Pine and 094 Snow Pine later. §1.5 lists what keeps 047 apart.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is `#F4F0E5`
(244, 240, 229), tolerance 14. Cell borders (measured grey rules): rows y 85 / 544 / 827 / 1340 / 1493; columns x 12 /
515 / 1011, ortho dividers x 262 / 511 / 762, exploded | close-ups x 671.
- **Painted out (`TITLES` in `m.py`):** the two hero cell titles and the four exploded labels.
- **Masks** are `cls()` in `m.py`, the 045 classes (HSV, h in degrees, assigned in this order):
  - **X, cast shadow:** (s < 0.07, v ≥ 0.78) or (s < 0.08, v ≥ 0.70, B ≥ R − 3) or (h 200–245, s < 0.14, v ≥ 0.70). The
    sheet draws a lavender ground shadow to the left of every side view and lower-left of the top view.
  - **G, green:** h 50–180, s ≥ 0.25, v ≥ 0.10 (foliage and ground plants; split by height, §1.2).
  - **S, sand:** h 30–52, s 0.22–0.47, v ≥ 0.80. (24–72 px of lit pale bark per view also land in S; negligible.)
  - **T, trunk / bark:** h < 45, s ≥ 0.35, v ≥ 0.15.
  - **R, rock:** s < 0.30, v 0.25–0.95. **Note:** 2.0–3.5 % of each side view's R is above the ground (the pale halo
    round the clusters and a few grey shade facets), so true rock is about 6–7 %, not 9 % (§1.2).
  - **O, other:** outlines, the darkest creases.
- **Cells** (inside the borders): f34 (16,89,512,540); r34 (520,89,1008,540); front (16,572,258,790); side
  (265,572,508,790); rear (514,572,759,790); top (765,572,1008,790); exploded (16,860,668,1337); close-up 1 "branch join"
  (687,866,867,1001); close-up 2 "base / underside" (687,1018,867,1155); close-up 3 "foliage junction" (687,1172,867,1318).
- **Swatch inner boxes** 52 × 54 px at y 1385–1439, x 35 / 107 / 181 / 257 / 336 / 415 (`m.SW`).

**Scratch study material** (no Blender) in
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m047_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14, Pillow, numpy).
- **Helpers:** `m.py` (masks, boxes, `silhouette()`), `zoom.py` (`zoom.py x0 y0 x1 y1 scale out.png [grid]`),
  `comps.py` (`label()`, connected components), `colprof.py` (per-column green top / bottom), `lines.py` / `lines2.py`
  (cell rules, swatches).
- **Measurements:** `measure2.py` (bbox, W : H, shares, profiles, fifths), `trunk.py` (bark runs per height: trunk Ø,
  centre, lean), `base.py` (sand, rock and plant components), `samp.py` / `samp2.py` (colour per region, half, cluster
  and hue band).
- **Zooms:** `z_f34.png`, `z_f34top.png`, `z_r34.png`, `z_ortho.png`, `z_front.png`, `z_side.png`, `z_rear.png`,
  `z_top.png`, `z_top2.png`, `z_expl.png`, `z_expl_trunk.png`, `z_cu.png`, `z_cu1.png`, `z_cu2.png`, `z_cu3.png`; mask
  previews `cls_*.png`, `cls_mont1.png`.
- **On our renders:** `measure_render.py <render.png> [paper_hex] [--flip]` (same masks). Self-test on the sheet's own
  cells (`cell_f34.png`, `cell_front.png`, paper `#F4F0E5`): f34 W : H 0.965 (cell crop), G 48.2 / T 37.6 / S 3.4 /
  R 9.2; front W : H 1.015, G 49.3 / T 37.9 / S 1.6 / R 9.4.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a standalone old tree with its own ground patch. Hero budget 4000 tris, each part
  under 1000. The plan in §4.3 lands at about 3100–3400.
- **Overall read (check this first).** A **squat, massive old "cloud-pad" pine**: a **huge, leaning, buttressed,
  orange-brown trunk** (Ø ≈ 0.31 H just above the flare) faceted in long vertical bark planks, **flaring into seven
  angular buttress roots** on a pale sand patch, **forking at mid-height** into a leader and two fork stubs, from which
  **five angled, elbowed limbs** reach out and up, each ending in two or three short twigs that hold a **separate,
  chunky, faceted foliage cluster** (a domed mound of broad low-poly lobes, no individual leaves). The crown cluster sits
  on top, two clusters each side. A **cut branch stub with a hollow end** juts under the crown, a second hollow stub on
  the back of the trunk, a small **knot hole** on the front. The base is dressed with **pale warm-grey angular rocks**,
  a **dark green broad-leaf bush**, **lime upright leaf tufts** and small sprigs.
  - It must read as **bark first, foliage second**: the trunk and limbs are 38 % of the f34 silhouette, the clusters are
    separate pads with **sky between them** in every side view, and the limbs show between and under the pads.
  - Hero shares (f34): G 48.2 % (canopy ≈ 37, ground plants ≈ 11), T 37.6 %, R 9.3 % (rock ≈ 7.3), S 3.4 %.
- **Focal silhouettes, in order:**
  1. The trunk's mass: a broad flared foot, a waisted column leaning right, the fork bulge at mid-height, the leader.
  2. Five separate scalloped pads: crown on top (biggest), upper-left tucked under it, upper-right, and the two low side
     pads; the gaps between them.
  3. The angled limbs and twigs under each pad, and the hollow cut stub under the crown.
  4. The roots splaying onto the sand, the long front-right root; the base dressing.
- **Target size: 20.0 tall (crown top), canopy 20.3 wide (X) × about 12 deep (Y), trunk Ø 6.2 at z 5–7, root spread
  r 5.5–8.6, ground patch about 17 × 14** (decision §8.1). Tolerances: height ±0.4, canopy width 20.3 ± 0.8.
  - **How it was derived.** Front cell: silhouette 202 × 201 px with the ground's front edge at y 784 (e ≈ 7°), so
    10.05 px / stud at H 20. f34: 409 × 431 px, 21.5 px / stud. Trunk widths per height (`trunk.py`, fraction of H):

    | Feature | f34 | r34 | front | side | rear | adopted (studs) |
    | --- | --- | --- | --- | --- | --- | --- |
    | Trunk Ø above the flare, h .25–.35 | .29–.34 | .28–.31 | .31–.36 | .20–.27 | .29–.32 | Ø 6.2 at z 5–7 |
    | Fork bulge (limbs leaving), h .40–.45 | .35–.41 | .37 | .39–.42 | .25 | .40 | 8.0 across the fork stubs, z 8–9 |
    | Waist above the fork, h .50–.55 | .19–.32 | .17–.19 | .17–.20 | .07–.14 | .18–.20 | leader Ø 3.6 at z 10–11 |
    | Flare incl. root bases, h .15–.20 | .21–.27 | .39–.40 | .26–.30 | .22–.28 | .35–.44 | Ø 8.5–9 at z 2–3 |
    | Long root tip from the axis | screen +3.6 | | x +7.8 | | x +7.2 (mirrored) | root RT1 r 8.6, az 330° |
    | Canopy W / H (whole silhouette) | .949 | .952 | 1.005 | .714 | 1.010 | 20.3 / 20 |

  - **Why 20.** 042 is 16 tall and 045 10; the old pine must be the biggest and by far the heaviest. At 20, the sheet's
    proportions give a 6-stud trunk (three characters wide: reads "old"), pads whose undersides hang at 7.7–9 (well
    above a 5.5 character's head, so players walk under the low pads), rocks 1.6–2.5 tall (knee to waist) and plant
    bushes 2–3.6 (waist to shoulder). Smaller (16) gives a 5-stud trunk and pads at head height; larger (24, nearer W04's
    26) makes the base dressing chest-high boulders.
  - **Against the character (5.5):** the tree is 3.6 C tall; the trunk is about 3 C wide; the lowest pad (R) bottoms at
    7.7 (1.4 C); the fork is at about 1.6 C.
- **Build frame:** front −Y, +X right, ground z 0 = the sand patch's flat underside. Trunk foot axis at (0, 0); the trunk
  leans toward +X (and a little +Y). Origin = bbox bottom centre: the canopy runs −9.6 … +10.7 in X, so the origin sits
  about +0.5 X of the foot axis (record it).

### 1.2 Measured views (`measure2.py`)

| View (box) | Silhouette bbox (px) | W : H | G | T | S | R | O |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (16,89,512,540) | 68–476 × 103–533 (409 × 431) | **0.949** | 48.2 % | **37.6** | 3.4 | 9.3 | 1.5 |
| Rear three-quarter (520,89,1008,540) | 574–969 × 114–529 (396 × 416) | 0.952 | 46.6 | 40.8 | 3.3 | 7.7 | 1.7 |
| Front (16,572,258,790) | 38–239 × 584–784 (202 × 201) | 1.005 | 49.1 | 37.8 | 1.6 | 9.7 | 1.9 |
| Side (265,572,508,790) | 309–453 × 582–784 (145 × 203) | 0.714 | 60.2 | 28.9 | 1.3 | 7.5 | 2.0 |
| Rear (514,572,759,790) | 531–735 × 584–786 (205 × 203) | 1.010 | 48.6 | 39.6 | 2.0 | 8.1 | 1.7 |
| Top (765,572,1008,790) | 787–984 × 595–768 (198 × 174) | 1.138 (W : D) | 76.9 | **9.2** | 0.1 | 12.0* | 1.8 |

- Shares are of the silhouette (O included, X excluded). \*Top R is mostly the blue-grey cast shadow under the pads
  (the mask's X rule misses its darker part); judge the top on G and T.
- **R above the ground** (halo and grey shade facets, not rock): f34 2.0 %, r34 1.6, front 3.5, side 2.9, rear 3.2.
  Rock proper: f34 7.3, r34 6.0, front 6.2, side 4.7, rear 5.0.
- **Verifier tolerance:** G ±5, T ±4 (binding, §8), R ±3, S ±2 points; W : H ±0.06; positions ±0.05 of W / H.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.1 W):

| f | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .12 | .65 | .70 | .85 | .94 | 1.0 | .99 | .93 | .90 | .86 | .53 |
| r34 | .50 | .62 | .83 | .85 | .95 | 1.0 | .99 | .92 | .83 | .66 | .54 |
| Front | .54 | .67 | .70 | .89 | .94 | .99 | 1.0 | .92 | .86 | .82 | .50 |
| Side | .52 | .56 | .65 | .86 | .94 | .98 | .99 | .95 | .88 | .74 | .07 |
| Rear | .49 | .79 | .83 | .91 | .98 | .99 | .97 | .89 | .72 | .68 | .57 |

**Width per height** (silhouette width at h .0 → 1.0 as a fraction of W):

```
f34    .35 .99 .84 .56 .38 .96 .88 .64 .67 .48 .15
r34    .16 .87 .69 .31 .39 .98 .82 .61 .68 .38 .05
front  .36 .81 .67 .33 .69 1.0 .87 .82 .72 .42 .17
side   .48 .83 .35 .57 .85 .61 .78 .66 .60 .38 .03
rear   .03 .70 .56 .29 .66 .97 .87 .85 .60 .40 .04
```

- Reading (front): h .1 the patch and base dressing; h .2–.3 the bare trunk (.33 at h .3: Ø 6.6 incl. plants' tips);
  h .4 the low pads' bottoms appear; h .5 both low pads + trunk (widest); h .6–.7 the upper pads; h .8–1.0 the crown.
  **The narrow row at h .3 (.29–.56) is the bare trunk band between the base and the low pads: keep it.**

**Height fifths** (bottom → top, % of each class), f34: G 19.3 / 7.3 / 22.4 / 24.2 / 26.8 (the bottom fifth is the
ground plants, the second is bare trunk); T 19.5 / 29.3 / 32.2 / 18.0 / 1.0 (bark through four fifths: the limbs show
up to h .8). Front: G 19.1 / 1.3 / 28.2 / 25.7 / 25.7; T 20.8 / 31.2 / 30.0 / 17.8 / 0.3.

**Clusters (G components above the ground band, `comps.py`):**

| View | Components (sheet px boxes) | Reading |
| --- | --- | --- |
| f34 | L (71–243, 220–336) 173 × 117; top (175–452, 103–226) 278 × 124 = UL + C + UR touching; R (318–476, 233–348) 159 × 116 | 5 pads, 3 blobs |
| r34 | (573–708, 253–359); (618–727, 169–242); (711–894, 114–231); (799–969, 237–349) | R, UR, C + UL, L (mirrored) |
| Front | L (37–125, 640–697) 89 × 58; top (88–233, 584–652) = UL (85–122) + C (122–180) + UR (183–235); R (177–241, 660–707) 65 × 48 | 5 pads |
| Side | (308–450, 582–706) one stacked mass; a small low pad (400–446, 690–728) | §3.2 |
| Rear | (530–592, 660–709) R; (537–599, 618–659) UR; (588–682, 584–643) C + UL; (645–737, 639–698) L | 5 pads, mirrored |
| Top | W (787–866, 632–710); N + E (860–985, 595–692); S (860–947, 688–767) | 4 rosettes round a bark star, §3.3 |
| Exploded | C (288–511, 860–970) 224 × 111; UL (177–291, 910–989); UR (439–631, 967–1067); L (91–213, 991–1088); R (504–620, 1106–1202) | 5 pieces |

- **Pad outline:** each big pad's top edge shows about 6–9 scallops (lobes 2–2.8 studs wide on the outline). Pad W : H
  1.4–1.6 (f34 L 1.48, R 1.37; front L 1.53, R 1.36).
- **Plan (top cell, `z_top2.png`):** each pad reads from above as a **rosette**: a central 5–6-facet star (the top lobe)
  ringed by lower lobes. At the centre a **brown star of 5–6 limbs** radiates from the trunk top (T 9.2 % of the top
  silhouette): the limbs are not covered from above.

### 1.3 Silhouette and composition per view

**Front three-quarter (`z_f34.png`, `z_f34top.png`) — governs.** Seen from the **front-right** (camera az ≈ +25, e ≈
10°, §3.1), lit from the right; cast shadow to the left.
- **Trunk:** foot spans screen x 160–400 with root tips; the column (x 195–345 at y 360, Ø ≈ 7 on screen) leans right;
  long vertical bark planks, darker grooves between them, the left third in deep shade (`#55301D`) and the right lit
  orange (`#DF8B3F`). A small dark **knot hole** with a pale rim at (270, 318), h .50.
- **Fork:** at y 300–340 (h .45–.55) two fork stubs leave the column: left one carrying the long left limb (to the L
  pad), right one the right limb (to the R pad, joining at x 400–440). Above, the leader (Ø ≈ 3.5) rises to y 200 where
  the crown limb, the upper-left limb and the upper-right limb part; a **hollow cut stub** points up-right at (330, 193).
- **Limbs:** chunky (Ø 1.2–2.0 on screen), each with one or two elbows, then 2–3 short twigs rising into the pad's flat
  underside (`z_cu3.png`).
- **Pads:** L (left, h .46–.73), UL + C (top, the crown; C the most lit), UR (right, high), R (right, h .43–.70). Each is
  a scalloped dome of chunky faceted lobes: lit lime top facets, mid-green sides, dark teal undersides (light, not
  paint, §3.9).
- **Base:** sand patch x 83–479 (the widest thing at the bottom); a big pale rock front-left (x 126–228) with a smaller
  far-left rock (64–162); a **dark green broad-leaf bush** left-front of the trunk between the roots (149–272, top y
  420); a lime upright tuft far left (89–139); a big rock behind the trunk right (342–380, high); a rock right-front
  (383–436); a lime/green tuft group right (377–459); small lime sprigs and pebbles (269–295, 318–352, 366–389).
- **Roots:** the long front-right root runs toward the viewer to (345, 525); others splay left, front-left, front, right
  and back.

**Rear three-quarter (`z_r34.png`).** The same tree from behind (az ≈ +205, e ≈ 11°): the same five pads (mirrored), the
leader and limbs, the **second hollow stub** on the trunk's back (≈ (762, 325), protruding about 1 stud, a dark hole in a
pale rim), a long root to the right, pale rocks left and centre, tufts both sides.

**Front, side and rear cells (`z_front.png`, `z_side.png`, `z_rear.png`).** Low views (e ≈ 6–7°) at one scale (201–203 px
tall). Front and rear agree (§3.2): trunk leaning toward +X by about 7–8°, L pad left at z 8.7–14.3, R pad right at
7.7–12.3, UR right at 13.8–17.1, C on top (15.3–20.0) with UL tucked left of it. The cut stub under the crown shows in
both at x +3, z 15; the front shows the knot hole at (x 0, z 9.6); the rear shows the back stub at (x +1.6, z 9.1).
**The side cell draws a narrower, stacked, more conical tree** (W : H 0.71, the crown stacked in three tiers, a small low
pad behind): §3.2.

**Top (`z_top.png`, `z_top2.png`).** Four rosette pads round an exposed brown limb star; shadows lower-left. Its pad
layout doesn't match the front cell exactly (§3.3).

**Branch join (`z_cu1.png`).** A **six-sided socket stub** (top face cut flat, a raised rim round a dark hexagonal
socket, `#42281A`) on the trunk; the branch end is a **six-sided prism** with a flat end face and its own dark hollow
(`#231B18`) that plugs into the socket. Bark planks on the trunk beside it.

**Base / underside (`z_cu2.png`).** The trunk foot from low front: broad planked buttresses splitting into **long
faceted roots, each a 4–5-sided prism kinked once, tapering to a blunt point on the sand**; pale grey rocks with big
flat facets nestled between roots; lime and green leaf tufts; the sand patch with a soft edge.

**Foliage junction (`z_cu3.png`).** A limb (Ø ≈ 1.5) rises at about 45° and **splits into three short twigs** that end
in the pad's underside; the pad's underside is a **flat-ish lower surface** of broad dark facets, the sides scalloped
lobes, the top lit lime facets. "Consistent thickness": the pad is a thick mound, not a shell.

### 1.4 Parts (Exploded Construction, `z_expl.png`, `z_expl_trunk.png`)

The exploded is an elevated view from the front (e ≈ 20°). Its trunk is drawn at about 17.7 px / stud (leader socket to
ground 270 px ≈ 15.3), but **its pads are drawn about 1.6× the hero's** (C 224 px ≈ 12.7 studs against the hero's 7):
§3.4. **The hero governs every size**; the parts give shapes, counts and joints.

| Part (label) | Box (px) | Notes |
| --- | --- | --- |
| Forked Trunk | (246–486, 1040–1333) | a six-sided **leader** (Ø 50 px) with a **hollow socket top** at y 1050; a **left fork stub** (socket at about (290–320, 1125), tilted ~40° left) and a **right fork stub** (socket (395–425, 1120), tilted ~20° right), both hexagonal with dark sockets; body waist 76–80 px at y 1184–1196; flare 140–171 px at y 1244–1280; **seven buttress roots** splaying to the ground |
| Crown piece (unlabelled) | pad C (288–511, 860–970); limb (356–458, 904–1008) | the biggest pad on a limb that drops into the leader's top socket (two arrows); a short **cut stub with a hollow end** on the limb's right |
| "Canopy Tier" | pad UL (177–291, 910–989); limb (215–301, 957–1043) | limb end with a dark hollow; arrow down then right into a **side socket near the leader's top** |
| "Branch (angled)" | pad L (91–213, 991–1088); limb (142–264, 1042–1132) | a long angled limb with an elbow, hollow end into the **left fork** |
| Right piece | pad UR (439–631, 967–1067); limb (442–579, 1019–1124) | hollow end into the **right fork** |
| Lower-right piece | pad R (504–620, 1106–1202); limb (494–562, 1148–1185) | a short limb into a **low socket on the trunk's right side** |
| Rocks / Base | rocks (190–250, 1284–1330), (475–546, 1282–1328), (242–320, 1208–1303) etc.; 7 plant clumps (37–49 px) + sprigs | no sand drawn (shadows only) |

#### Forked Trunk — exploded, close-ups 1 and 2, hero
- **Shape:** a faceted, planked column (8–10 sides, each split once vertically into planks, grooves between), leaning;
  flaring at the foot into seven buttress roots whose top ridges climb the trunk as plank ridges; a bulge at z 7.5–9
  where the two fork stubs leave; the leader above; five hexagonal sockets with flat cut tops (leader top, left fork,
  right fork, a side socket on the leader for UL, a low socket on the right side for R); a back hollow stub; a front
  knot hole.
- **Hero size:** Ø 9.2 at z 0.05 (between the roots), 7.0 at z 2.6, 6.4 at z 4.2, 6.2 at z 6.0, 6.4 at z 7.6, leader Ø
  4.2 at z 10.2, 3.7 at z 11.8, 3.4 at the top socket (z 13.5). Roots to r 5.5–8.6. Part about 17 × 15 × 13.5.

#### Branch pieces (five) — exploded, close-ups 1 and 3, hero
- **Shape:** each a six-sided limb (Ø 2.4 for the crown limb, 1.8–2.0 for the others at the socket end, tapering to
  1.0–1.2), one or two elbows (15–35°), a flat plug end with a shallow hex hollow, and at its far end 2–3 twigs (Ø
  0.55–0.75, 1.0–1.6 long) rising 30–60° into the pad's underside. The crown limb carries the cut stub.
- **Pad:** a faceted mound of 6–9 closed lobes (§2.3): flat-ish underside, scalloped sides, a raised rosette top.

#### Rocks / Base — exploded, close-up 2, hero
- **Shape:** a thin irregular sand patch (hero only); 6 chunky angular warm-grey rocks (10–16 broad facets each, flat
  base, sloping faceted top), 3–4 pebbles; one big dark broad-leaf bush, 5 lime/green upright tufts of broad folded
  leaves, 4 small sprigs.

### 1.5 How 047 differs from 042 Young Fir and 045 Pine Sapling (binding: the verifier checks these)

| | 042 Young Fir (`TieredFir`) | 045 Pine Sapling (`PineSapling`) | **047 Old Pine** |
| --- | --- | --- | --- |
| Size | 16 tall, canopy 12 | 10 tall, canopy 7 | **20 tall, canopy 20.3 × 12, W : H ≈ 1.0** |
| Silhouette | slim stepped spire, W : H .66 | slim stepped spire, W : H .70 | **broad, squat, five separate pads with sky between, W : H 0.95–1.0** |
| Bark share (f34) | T 12.8 % | T 10.8 % | **T 37.6 %**: the trunk and limbs dominate |
| Trunk | Ø 2.0, octagonal planked, straight | Ø 1.25, smooth 8-sided taper | **Ø 6.2 (0.31 H), planked, leaning 7–8°, forked at z 8–9, leader to 13.5** |
| Branches | none | none | **five angled, elbowed limbs plugged into hexagonal sockets, 2–3 twigs each** |
| Foliage | three tiers of thin kite flaps | three tiers of thick paddle plates | **five separate faceted lobe mounds ("cloud pads"), no flaps, no plates, no tiers** |
| Roots | six long kinked roots | six short blunt flares | **seven tall buttress roots**, the front-right one 8.6 long |
| Joints | caps and hubs | peg and recess | **plug-in hexagonal sockets; hollow cut stubs; a knot hole** |
| Top view | 8-point star, no bark | star, no bark | **4–5 rosettes round an exposed brown limb star (T ≥ 5 %)** |
| Rocks | warm beige | pale neutral grey | **warm light grey, lit `#DBCCB6`, shade neutral `#606161`** |
| Ground plants | lanceolate clumps | broad-leaf rosettes | **a dark broad-leaf bush + lime upright tufts** |

Also not W04's `OldPine` (slender fluted trunk a quarter of the crown, fork at 14, pads on a ring 8.5 out, 26 tall).

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, trunk foot axis at (0, 0)). Plan azimuths: 0° = +X, counter-
clockwise, 270° = −Y (front).

### 2.1 Stack (binding contact chain, bottom up; every seat gap VEG_GAP = 0.015)

| Piece | Sits on / in | Contact |
| --- | --- | --- |
| Sand patch | ground | flat underside z 0, crest 0.15, bevelled edge to 0.03 |
| Trunk + roots (one closed shell, §6) | patch | foot ring at z 0.05 (sunk 0.10); root tips sunk 0.05 into the patch |
| Fork stubs, sockets, back stub | trunk | part of the trunk shell (unioned), or closed shells buried ≥ 0.3 (decision §8.6) |
| Each limb | its socket | the plug end enters the socket hole 0.30 deep; plug radius = hole radius − 0.02 (contact ≤ 0.03, no coincident faces); the end face 0.015 above the hole floor |
| Twigs | the limb's end | twig roots buried 0.2 in the limb's last segment |
| Pad core lobe | the twig tips | each twig tip buried 0.25–0.4 in the core lobe's underside |
| Pad ring / top lobes | the core lobe and neighbours | each overlaps the core by 0.3–0.6 and a neighbour by 0.15–0.3 |
| Rocks, pebbles | patch | sunk 0.10 / 0.04 |
| Plant hubs | patch | sunk 0.03; every leaf within 0.03 of its hub |

### 2.2 Trunk and sockets

| Ring z | 0.05 | 1.2 | 2.6 | 4.2 | 6.0 | 7.6 | 8.8 | 10.2 | 11.8 | 13.5 (top) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Centre (x, y) | 0, 0 | 0.05, 0 | 0.1, 0.05 | 0.2, 0.1 | 0.35, 0.15 | 0.5, 0.2 | 0.6, 0.25 | 0.8, 0.35 | 1.1, 0.5 | 1.4, 0.6 |
| Corner r | 4.6 | 4.0 | 3.5 | 3.2 | 3.1 | 3.2 | 3.0 | 2.1 | 1.85 | 1.7 |

- **Section:** 9 sides, each split once (18 plank facets), the split vertex pulled in 0.12–0.20 (grooves) or pushed out
  0.08 (proud planks), alternating irregularly; rings twisted +3° each going up (the planks follow the lean). Plank
  facets are broad: no ring finer than these ten.
- **Fork stubs** (hexagonal, flat cut tops with sockets):

  | Socket | Socket face centre | Axis (tilt from vertical, toward) | Outer Ø | Hole Ø × depth | Takes |
  | --- | --- | --- | --- | --- | --- |
  | Leader top | (1.4, 0.6, 13.5) | 8°, +X | 3.4 (the leader) | 2.1 × 0.35 | crown limb |
  | UL side socket | (−0.6, 1.4, 12.2) | 55°, az 150° | 2.2 | 1.4 × 0.30 | UL limb |
  | Left fork | (−3.1, −0.6, 9.4) | 50°, az 190° | 2.6 | 1.7 × 0.35 | L limb |
  | Right fork | (3.3, 0.3, 10.4) | 28°, az 15° | 2.6 | 1.7 × 0.35 | UR limb |
  | Low right socket | (3.0, −1.3, 8.3) | 70°, az 330° | 2.2 | 1.4 × 0.30 | R limb |

  Each fork stub rises out of the trunk as two bark planks (no visible seam); its rim is a flat ring 0.18 wide round
  the hole; the hole walls and floor are their own faces (painted `bark_deep`).
- **Back hollow stub:** a hexagonal prism Ø 1.4 at (1.6, 2.9, 9.5), axis 75° from vertical toward az 80°, protruding
  1.0 beyond the bark, end face cut flat with a hex hollow Ø 0.8 × 0.3 (rear (625, 695), r34 (762, 325)).
- **Front knot hole:** on the front plank at (0.2, −2.35, 9.6): a hex rim Ø 0.9 raised 0.06 round a recess Ø 0.5 ×
  0.25 deep (f34 (270, 318), front (133, 688)). It must **read as a dark hole at cell scale** (W04 V8g missed this):
  recess walls and floor `bark_deep` (hard), the rim `bark_light`.
- **Roots (7)**, buttress section (5 sides: a tall top ridge, two upper flanks, two lower flanks splayed onto the sand),
  2–3 segments, one kink at 0.5–0.6 of the reach, blunt tip 0.4 wide, top ridge running up the trunk to z 3.5–4.5 as
  a plank ridge:

  | Root | Azimuth | Reach r | Height at trunk × width | Segments | Evidence |
  | --- | --- | --- | --- | --- | --- |
  | RT1 front-right (long) | 330° | 8.6 | 3.8 × 2.2 | 3 | f34 root to (345, 525); front tip x +7.8 |
  | RT2 right | 10° | 7.2 | 3.4 × 2.0 | 3 | rear tip x +7.2; f34 h .15 (375–412) |
  | RT3 front | 275° | 6.8 | 3.4 × 2.0 | 2 | f34 front root; z_cu2 |
  | RT4 front-left | 225° | 7.2 | 3.2 × 1.9 | 3 | f34 left roots; exploded |
  | RT5 left | 170° | 6.0 | 3.0 × 1.8 | 2 | front left foot |
  | RT6 back-left | 120° | 5.5 | 2.8 × 1.7 | 2 | r34, rear |
  | RT7 back | 65° | 5.8 | 3.0 × 1.8 | 2 | r34, rear |

### 2.3 Limbs and pads

| Limb → pad | From socket | Elbow(s) | End (twig fork) | Ø socket → end | Twigs |
| --- | --- | --- | --- | --- | --- |
| Crown → C | leader top | up 1.4, then toward (1.6, 2.8) | (1.6, 2.4, 15.3) | 2.4 → 1.5 | 3; plus the **cut stub**: Ø 1.1, 1.2 long, from (2.0, 1.2, 14.3) pointing az 0° tilted 45° up, hollow end Ø 0.6 × 0.25, tip ≈ (2.9, 1.2, 15.1) |
| UL → UL | UL side socket | one, at 1.6 | (−2.8, 2.6, 14.9) | 1.8 → 1.1 | 2 |
| UR → UR | right fork | one, at 2.0 | (6.8, 1.4, 14.0) | 1.9 → 1.1 | 3 |
| L → L | left fork | two (out level, then up 25°) | (−5.0, −1.8, 9.9) | 2.0 → 1.2 | 3 |
| R → R | low right socket | one, at 1.8 | (7.2, −2.0, 8.9) | 1.8 → 1.1 | 2–3 |

| Pad | Centre (x, y) | Bottom z → top z | W × D × H | Lobes (core + ring + top) | Evidence |
| --- | --- | --- | --- | --- | --- |
| C (crown) | (1.6, 2.8) | 15.2 → 20.0 | 7.0 × 6.0 × 4.8 | 9 (1 + 6 + 2) | front x −1.1…+4.7, z 15.3–20.0; exploded biggest |
| UL | (−3.0, 3.0) | 14.6 → 18.6 | 5.2 × 4.6 × 4.0 | 6 (1 + 4 + 1) | front top 18.6, x −5.0…−1.3; f34 (175–262) |
| UR | (7.2, 1.5) | 13.6 → 17.4 | 5.6 × 5.0 × 3.8 | 7 (1 + 5 + 1) | front x +4.8…+10.0, z 13.8–17.1 |
| L | (−5.2, −2.0) | 8.7 → 14.3 | 8.6 × 7.0 × 5.6 | 8 (1 + 6 + 1) | front x −9.6…−0.8, z 8.7–14.3; f34 widest pad |
| R | (7.4, −2.0) | 7.7 → 12.3 | 6.6 × 6.0 × 4.6 | 7 (1 + 5 + 1) | front x +4.4…+10.7, z 7.7–12.3 |

- **Gaps:** between L and C/UL (front x −1 … −0.8 at z 14–15) and between UR and R (z 12.3–13.6) the sky shows; the
  trunk band between the base and the low pads (z 4–7.7) is bare. Keep ≥ 0.6 between neighbouring pads' outlines in
  the front and rear views except where the sheet lets them touch (UL / C / UR read as one top mass in the front).
- **Lobe (closed, about 29 tris):** a bottom hexagon (4 tris, near-flat, sloping up 5–10° to the rim), a widest ring of
  6 at 0.4 h (rotated half a step, r = w / 2 ± 8 %), a shoulder ring of 5 at 0.78 h (r 0.55), a top vertex offset
  ±0.1 w. Facets are big and flat; no subdivision, no sphere. Lobe sizes: core 0.55–0.65 of the pad W, ring lobes
  0.32–0.42, top lobes 0.35–0.45; heights 0.55–0.7 of their width.
- **Pad assembly:** the core lobe sits on the twig tips (its underside is the "flat cut surface" of close-up 3); ring
  lobes at azimuths k · 360 / n (jitter ±12°), their centres at 0.62–0.72 of the pad radius, bottoms 0.2–0.5 below the
  core's (the rim droops), each overlapping the core and its neighbours; top lobes raise the dome to the pad's top z and
  make the rosette seen from above. The pad's outline then has 6–9 scallops, as measured.
- **Pad underside:** near-flat (the bottoms of core and ring lobes within 0.5 of each other), so it reads dark and broad
  from below by lighting.

### 2.4 Base

Plan positions from the f34 (camera +25°, inverted), front and rear cells.

| Piece | Position (x, y) | Size | Evidence |
| --- | --- | --- | --- |
| Sand patch | lobed outline, 16 points, r 6.4–9.2 (longest toward 330° under RT1 and 150°) | 17.2 × 14.0, crest 0.15, bevel 0.6 wide to 0.03 | front 54–227 (17.2), rear 16.1, side 13.6 |
| RK1 big front-left | (−3.2, −5.2) | 3.0 × 2.6 × 2.4 tall | f34 (126–228, 468–523), the prominent pale rock |
| RK2 far left | (−7.4, −2.4) | 2.6 × 2.2 × 1.8 | f34 (64–162); front (45–107) |
| RK3 right-front | (6.0, −4.6) | 2.4 × 2.0 × 1.7 | f34 (383–436); front (184–204) |
| RK4 back-right | (4.6, 3.2) | 2.0 × 1.8 × 1.8 | f34 (342–380) high on screen; front (172–191) z 3–4.4 |
| RK5 back | (1.0, 5.4) | 2.6 × 2.2 × 2.0 | rear (618–644), the pale centre rock |
| RK6 back-left | (−2.2, 5.0) | 1.6 × 1.4 × 1.2 | rear (650–667) |
| Pebbles ×4 | (2.6, −5.9), (0.4, −6.5), (−5.6, −0.4), (5.2, 4.9) | 0.4–0.6 | f34 small greys (269–295, 366–389) |
| B1 dark broad-leaf bush | (−3.6, −3.4), between RT3 and RT4 | Ø 4.4, 3.4 tall, 11 leaves (8 dark, 3 green) | f34 (149–272, top y 420), front (56–128) |
| T1 lime tuft far left | (−7.0, −0.6) | Ø 2.4, 2.8 tall, 7 leaves | f34 (89–139) |
| T2 right tuft group | (6.6, −1.4) and (5.6, −2.6) | Ø 3.4 together, 3.0 tall, 12 leaves (lime + green) | f34 (377–459); front (190–219) |
| T3 small right-front | (3.8, −5.1) | Ø 1.8, 1.8 tall, 5 leaves | f34 (345–393) |
| T4 back-right | (6.0, 3.6) | Ø 2.4, 2.6 tall, 7 leaves | rear (570–597) |
| T5 back-left | (−4.6, 3.8) | Ø 2.8, 2.6 tall, 8 leaves | rear (675–711) |
| Sprigs ×4 | (−1.8, −6.0), (1.6, −6.2), (−6.0, −4.2), (2.4, 6.0) | Ø 0.8–1.0, 0.8–1.2 tall, 4 lime leaves | f34 sprigs |

- **Leaves:** each a closed folded lanceolate shell (8 tris), **broad** (length : width ≈ 3 for tufts, ≈ 2.4 for the
  bush), rising 55–75° and arching out from a small hub; never needles, never edge-on to the f34 or front camera (039).
- **Keep clear:** nothing cuts more than 0.05 into a root ridge or the trunk; the dressing stays inside the patch by ≥
  0.3; the bush B1 sits in the notch between two roots, its back leaves touching the trunk.

### 2.5 Expected extents and screen checks

- **Extents:** X −9.6 … +10.7 (pads), Y about −7.0 … +7.0 (patch; pads −5.5 … +5.8), Z 0 … 20.0. Bbox about 20.3 ×
  14.0 × 20.0.
- **Checks on the renders** (floor hidden, `measure_render.py`):
  - **f34_sheet (+25, 10)** (probe az +10 … +40 × e 6 / 10 / 14, keep the best; §3.1): W : H 0.89–1.01 (sheet 0.949);
    shares G 48.2 ± 5, T 37.6 ± 4, R 9.3 ± 3, S 3.4 ± 2; top profile ±0.08 for f .1–.9; width per height ±0.10 at h
    .2–.9 with the narrow bare-trunk row at h .3 (≤ 0.62); T fifths within ±7; L, top mass and R at their §1.2 boxes
    ± 0.05.
  - **front_sheet (0, 6), rear_sheet (180, 6):** W : H 0.95–1.06; shares G 49 ± 5, T 38 ± 4; pads L / top / R at
    their §1.2 boxes ± 0.05; the cut stub under the crown at x ≈ +3, z ≈ 15; the knot (front) and back stub (rear)
    visible.
  - **r34_sheet (+205, 11):** loosely, W : H 0.89–1.01, T 40.8 ± 5, five pads.
  - **side_sheet (90, 6):** content only (§3.2): crown on top, pads both sides, trunk and roots visible, W : H 0.72–0.9.
  - **top (0, 89):** W : D 1.05–1.35 (sheet 1.138); 4–5 separate rosette pads with gaps; **bark T ≥ 5 %** (a limb
    star visible at the centre); G ≥ 70 %.

## 3. View conflicts and resolutions

### 3.1 Which side the "front three-quarter" sees, and the elevations

- **Evidence.** The front and rear cells agree: the trunk leans toward +X, the long root's tip is at x +7.2 … +7.8.
  In the f34 that root runs almost straight at the viewer (screen +3.6), the lean reads stronger than in the front, and
  the L / R pads sit at −5.2 / +6.0 on screen against −5.2 / +7.6 in the front: a camera **from the front-right**
  (kit az ≈ +25 … +35, camera at (sin az, −cos az)). The patch's screen depth gives e ≈ 10° (f34), 11° (r34), 6–7°
  (front, side, rear).
- **Resolution (decision §8.10).** `f34_sheet (+25, 10)` governs (probe az +10 … +40, e 6–14); `r34_sheet (+205, 11)`
  (probe 150 … 215); `front_sheet (0, 6)`, `side_sheet (90, 6)`, `rear_sheet (180, 6)`, kit `top`, `underside`. Note:
  unlike 042 (−35), this f34 is from the right.

### 3.2 The side cell is a different tree

- **Evidence.** Side W : H 0.714 (others 0.95–1.01), G 60 % / T 29 % (others 48 / 38), the crown stacked in three
  tiers, a small extra pad low behind the trunk (400–446, 690–728), the trunk Ø 0.20–0.27 H (others 0.29–0.34). With
  pads 12 deep and 20 wide, the side should be about 0.7 × the front's width, so its narrowness is partly right; its
  stacked conical crown is not.
- **Resolution.** Front, rear, f34 and r34 govern. The side is judged for content (crown on top, pads both sides, the
  trunk and roots, the base) and W : H 0.72–0.9. The low back pad is the exploded's lower-right piece seen from the side;
  in our plan R sits at the front-right instead (front and rear cells both show it there).

### 3.3 The top cell's pad layout

- **Evidence.** The top shows pads at W (−6.4, 0), N (+1, +4.5), E (+6.8, +1.6) and S (+1.3, −5.5) round an exposed
  limb star, with depth 17 against width 20. The front and rear cells put no pad in front of the trunk (the trunk is
  bare from z 4 to 12 in both), and the f34 puts the pads' depth within ±3.
- **Resolution.** The pads go back and forth moderately (§2.3: L and R at y −2, UL / C / UR at +1.5 … +3), which keeps
  the front, rear and f34 right and gives the top a crown set back from the trunk top, so the **limb star shows from
  above** (the top cell's T 9.2 %). The top is judged for content: 4–5 separate rosettes, gaps, exposed limbs.

### 3.4 Exploded scale vs the hero

- **Evidence.** Exploded trunk ≈ 17.7 px / stud; its pads 115–224 px (6.5–12.7 studs at that scale) against the hero's
  5.2–8.6; its C is the biggest pad (224 px) while the hero's C is mid-sized in the front (5.8 visible).
- **Resolution.** The hero governs every size; the parts are the hero's own pieces (same functions), so the parts shot
  will show smaller pads than the exploded. C is made the biggest-volume pad (7.0 × 6.0 × 4.8) to honour the exploded.

### 3.5 Which socket each limb uses (exploded vs hero)

- **Evidence.** Exploded: L → left fork, UR → right fork, UL → a side socket high on the leader, C → the leader top,
  R → a low socket on the right side. Front cell: the L and R limbs leave the trunk at z 8.4–9.4, the UR limb rises
  from z ≈ 10–12.5, the crown limb from the leader top.
- **Resolution.** As the exploded, with heights from the front (§2.2): left fork at z 9.4, low right socket at 8.3,
  right fork at 10.4, UL side socket at 12.2, leader top at 13.5.

### 3.6 Sockets and hollows: inside the hero or visible?

- **Evidence.** Close-up 1 and the exploded show hollow sockets and hollow branch ends; the assembled views show only
  the cut stub under the crown, the back stub and the knot as hollows (the sockets are filled by limbs).
- **Resolution.** Model every socket with its hole (hidden in the hero, shown on the ForkedTrunk part) and every plug
  end with a shallow hex hollow (shown on the branch parts). The visible hero hollows are the crown-limb stub, the back
  stub and the knot.

### 3.7 Base dressing between views

- **Resolution.** The f34 + front + rear plan (§2.4) governs (6 rocks, 1 bush, 5 tufts, 4 sprigs, 4 pebbles); the side
  and exploded are judged for content.

### 3.8 The palette: six unlabelled swatches

- **Evidence.** dark green `#2D5642`, mid green `#5F8E42`, light olive-lime `#ADAC38`, bark `#935733`, tan `#B89073`,
  light grey `#B1ADA8`. The rendered sand is `#E2C698` (37°, .33); cut rims render light orange (`#BE7239`, lit
  `#EEA259`), not tan; rocks render warm grey lit (`#DBCCB6`) and neutral in shade (`#606161`).
- **Resolution.** The tan is the **ground / sand shade** tone (045's "ground foliage" swatch was the same role): start
  for `sand_deep`. The grey is the rock. Cut faces take `bark_light` (an orange, from the render). Calibrate to the
  rendered regions (§5.4), not the swatches.

### 3.9 "No texture noise" vs the user's blended-colour rule; the lit / shade split

- **Evidence.** Every pad: top third lime (`#A3BC32` on C), bottom third dark teal (`#163823`); every view's canopy
  left half 105–120° and right half 79–83°; trunk left half `#77462A`, right `#A05829`. That is the sheet's light.
- **Resolution.** The user's rule wins quietly: broad position / role blends (C the lightest pad, inner lobes a step
  deeper than outer lobes, grooves and hollows deeper, cut faces lighter), whole-facet Tint at low amplitude; **never by
  facing** (042 ruling: no deep key on undersides).

### 3.10 Cast shadow

- The sheet's lavender shadow is excluded by the X mask. Render every `*_sheet` view with the studio floor hidden.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its exploded cell

1. `lobe(centre, w, h, rot, seed)` → one closed faceted lobe (§2.3, about 29 tris).
2. `pad(spec)` → one pad: core lobe + ring lobes + top lobes, every lobe a closed shell overlapping the core. Check the
   outline scallops (6–9 on a big pad), W : H 1.4–1.6, the rosette from above, the flat underside.
3. `limb(spec)` → a six-sided limb from the plug end (with its shallow hollow) through its elbows to the twig fork,
   plus `twig()` ×2–3 and, for the crown limb, `cut_stub()`. One closed shell per limb (an explicit mesh: the elbows are
   ring stacks, no booleans), twigs and stub separate closed shells buried 0.2 in the limb.
4. `branch_piece(name)` = limb + pad, seated by contact. Five pieces: crown, UL, UR, L, R.
5. `trunk()` → the planked body (§2.2 rings), the fork stubs and sockets (modelled into the body or buried shells,
   decision §8.6), the back stub, the knot, and seven `root(spec)` buttresses unioned into the body one at a time at the
   origin (`m021._union_fine`, merge 0; save between unions; collapse corners under 3°, 042 finding 1).
6. `root_base()` → `patch()`, `rock(spec)` ×6 (explicit ring stacks: base ring, widest ring at 0.3 h, shoulder ring at
   0.7 h, a flat sloping 4–6-corner top; 10–16 broad facets; never `K.hull_rock` balls), `pebble()` ×4, `bush()`,
   `tuft(spec)` ×5, `sprig()` ×4.
7. **Hero `GnarledPine`** = root base + trunk + the five branch pieces plugged into their sockets, joined into one object
   of closed shells.
8. **Parts shot** (+20, 15) laid out like the exploded: the crown piece on top, UL and L to the left, UR and R to the
   right, the trunk in the middle, the base below; gaps 1.5–2.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a squat old pine on a massive leaning planked trunk, five separate faceted pads on angled limbs,
   seven buttress roots, a cut stub under the crown, a knot on the front; sky between the pads.
2. **f34_sheet** per §2.5 (shares, W : H, profiles, the bare trunk band, pad boxes).
3. **front / rear / r34 / side / top** per §2.5.
4. **Close-up renders:** `join_cu (−20, 25)` on the ForkedTrunk part's right fork against close-up 1 (hex socket, flat
   rim, dark hole) and a branch part's plug end (hex hollow); `base_cu (+15, 18)` on the trunk foot against close-up 2
   (kinked buttress roots, rocks between them, tufts); `foliage_cu (−35, −8)` on the L branch piece against close-up 3
   (limb splitting into three twigs into a flat dark underside).
5. **Contact counts** (§6): floating shells 0; every lobe chained to its core, every core to its twigs, every limb to
   its socket, the trunk to the patch.
6. **Hero size** per §2.5; a **scale shot** with a 5.5-stud marker under the R pad (the pad's underside above the
   marker's head).
7. **Underside view:** the pads' broad flat undersides, the limbs and twigs, the patch's flat bottom.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Trunk body (18 facets × 9 bands) | 1 | 330–380 | 330–380 |
| Sockets / fork stubs (5), back stub, knot | 7 | 20–40 | 160–220 |
| Roots | 7 | 28–40 | 200–280 |
| Limbs (6-sided, 3–4 rings, plug hollow) | 5 | 50–70 | 250–350 |
| Twigs + cut stub | 14 + 1 | 12–20 | 180–260 |
| Pad lobes | 37 | 28–32 | 1040–1180 |
| Sand patch | 1 | 80–110 | 80–110 |
| Rocks | 6 | 36–56 | 220–320 |
| Pebbles | 4 | 8–12 | 32–48 |
| Plant leaves (bush 11, tufts 39, sprigs 16) | 66 | 8 | 528 |
| Plant hubs | 10 | 6–8 | 60–80 |
| **Hero** | | | **about 3080–3560** (limit 4000; ceiling 3800) |
| Parts: ForkedTrunk / CrownCanopy / CanopyTier (UL) / BranchAngled (L) / RootBase | | | 700–880 / 360–420 / 250–300 / 310–360 / 920–990 (limit 1000) |

- If the RootBase part passes 1000, drop one tuft's leaves to 5 and the sprigs to 3 leaves before touching rocks.
- **Spend headroom on the read:** if a pad looks thin or lumpy-round, add a second top lobe or split the core lobe's
  widest ring to 8 (35 tris) before anything else; never subdivide.

### 4.4 What to do better than W04's `OldPine` and the kit's earlier trees

| Earlier | This one |
| --- | --- |
| W04 `OldPine`: slender fluted cone trunk, fork at 14, 26 tall | the sheet's **massive** trunk (Ø 0.31 H), fork at z 8–10, 20 tall |
| W04 pads "mushy" / boxy star pads hugging the trunk; "blob canopy" | five separate **faceted lobe mounds** on visible limbs, sky between |
| W04 knot "barely reads" (V8g) | a knot with a proud rim and a dark recess; two hollow stubs |
| 042 canopy "sparse and spiky", core showing between flaps | dense closed pads: no gap through a pad except from below |
| 042 lime tip on every flap (a scale pattern) | colour by whole pad and whole lobe; no per-lobe lime cap |

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 52 × 54 box inside each, sd ≤ 1.1)

| Swatch | Box | Hex | HSV | Use |
| --- | --- | --- | --- | --- |
| 1 dark green | (35,1385,87,1439) | `#2D5642` | 151°, 0.48, 0.34 | start for `leaf_deep` |
| 2 mid green | (107,1385,159,1439) | `#5F8E42` | 97°, 0.54, 0.56 | start for `leaf` |
| 3 light olive-lime | (181,1385,233,1439) | `#ADAC38` | 59°, 0.68, 0.68 | start for `leaf_light` and `plant` |
| 4 bark | (257,1385,309,1439) | `#935733` | 22°, 0.65, 0.58 | start for `bark` |
| 5 tan | (336,1385,388,1439) | `#B89073` | 25°, 0.38, 0.72 | start for `sand_deep` (§3.8) |
| 6 light grey | (415,1385,467,1439) | `#B1ADA8` | 33°, 0.05, 0.69 | start for `rock` / `rock_deep` |

### 5.2 Rendered regions (`samp.py`, `samp2.py`; median / v > .7 median / lit quartile / shade quartile)

| Region | Median | v > .7 | Lit Q | Shade Q | Halves (right = lit / left = shade) |
| --- | --- | --- | --- | --- | --- |
| Canopy f34 | `#50822F` (96°, .64, .51) | `#B0C431` | `#ACC230` | `#1F4626` | R `#719C2E` (83°) / L `#387330` (113°) |
| Canopy r34 / front / side / rear / top | `#4E812D` / `#4B802F` / `#4C812F` / `#50832F` / `#5C892C` | `#B1C530` / `#AAC131` / `#AFC630` / `#B3C833` / `#ABC12B` | | `#1D4525` … `#21512A` | front R `#779F2E` / L `#367130` |
| Pads, f34 (median / v > .7 / lime share) | C `#80A62E` / `#B1C631` / 54 %; UR `#709A2E` / 40 %; R `#608E2E` / 35 %; L `#40772F` / 25 %; UL `#2D6232` / 3 % (in C's shadow) | | | | top thirds `#A3BC32` (C) … `#759F33` (L); bottom thirds `#163823` … `#2C562D` |
| Canopy hue bands (f34) | lime (h < 80) 31 % `#A5BE2F`; green (80–110) 29 % `#5B8C2F`; dark (≥ 110) 40 % `#27592E` | | | | |
| Trunk f34 / r34 / front / exploded | `#8B4E2A` (22°, .70, .55) / `#91522A` / `#884D2B` / `#9F5A2D` | `#DB843B` / `#DC833A` / `#D8813A` / `#D78039` | `#E38D41` | `#55301D` | f34 R `#A05829` (24°, .74, .63) / L `#77462A`; r34 R `#C26E31` |
| Cut faces (socket rim, stubs) | `#BE7239` (26°, .70, .74); lit `#EEA259` | | | | |
| Hollows (socket hole, branch end, knot) | `#42281A` / `#231B18` / `#4B2816` | | | | |
| Rock f34 / r34 / front (ground band) | `#8F8D8B` (30°, .03) / `#8D8885` / `#948C87` | `#DBCCB6` (36°, .17, .86) / `#D6C7B5` / `#DBCCB4` | `#E3D1BB` | `#606161` (neutral: light) | |
| Sand f34 / r34 / close-up 2 | `#E2C698` (37°, .33, .89) / `#E2C596` / `#E2C69E` | | `#E5CB9E` | `#DEC293` | |
| Ground plants f34 | `#476E27` (93°) | `#A8BC28` | `#92AE27` | `#144022` | lime 31 % `#8CA824`; green 36 % `#4B7526`; dark 33 % `#18492C` |

### 5.3 How the colour works

- **Pads:** one mid green that renders lime where lit and deep teal-green in shade; **C the lightest pad, L and R the
  most mid-toned**; within a pad the core and inner (lower) lobes a step deeper than the outer and top lobes, by lobe
  role, whole lobes only. The hard lit-top / dark-underside split is the light: **never colour by facing**. Keep the pads
  (lit 79–83°, shade 105–120°) apart from the ground plants' lime (65–70°) and from the bark (22–26°) by hue.
- **Bark:** one warm orange-brown (22–26°, sat 0.65–0.75, R > G > B); **deeper** in the plank grooves (the pulled-in
  split vertices), the lowest 0.4 near the sand, and inside every hole; **lighter** on cut faces (socket rims, stub
  ends, the knot rim) and the proud plank ridges' upper halves by position. The dark left side is the light.
- **Rock:** warm light grey (lit 33–36°, sat 0.12–0.17, R ≥ G ≥ B, never mauve or blue); tops a step lighter, feet a
  step deeper, by height within each rock.
- **Sand:** pale warm sand; a step deeper within 0.5 of the trunk, roots and rocks and on the bevel.
- **Ground plants:** three tones per leaf by role: the bush B1 mostly dark (`plant_deep`), tufts lime outside and
  green inside, sprigs all lime.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians (lit half or v > .7), not swatches. `K.sample` kinds: `"green"` for
pads and plants, `"brown"` for bark and sand, `"stone"` for rock, `"vivid"` for the lime keys if `"green"` rejects them.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m047_leaf` | f34 canopy median `#50822F` ± 15 whole-canopy; lit-half median `#719C2E` ± 12 (start `#5F8E42`) | 85–100°, G > R > B | every lobe by default | rough 0.85, `low_spec=True` |
| `m047_leaf_light` | v > .7 canopy `#B0C431` ± 12 (start `#ADAC38`) | 68–78°, sat ≥ 0.68 | C top and ring lobes 40 %; UR / UL top lobes 25 %; other pads' top lobes 15 % | rough 0.85, low spec |
| `m047_leaf_deep` | the dark swatch `#2D5642` rendered lit ± 12 | 130–150°, sat 0.45–0.6 | core lobes 40 %; L and R ring lobes nearest the trunk 20 % | rough 0.9, low spec |
| `m047_bark` | f34 lit-half trunk `#A05829` ± 12; v > .7 `#DB843B` (start `#935733`) | 22–26°, sat 0.65–0.75, **R > G > B** | trunk, roots, limbs, twigs | rough 0.9 |
| `m047_bark_light` | cut rim `#BE7239`; lit `#EEA259` | 26–30° | socket rims, stub and plug end faces, knot rim (hard: cut faces); proud plank ridges' upper halves 20 % | rough 0.9 |
| `m047_bark_deep` | hollow `#42281A` (start); groove a step below `bark` | 18–22°, sat 0.6–0.7 | hole walls and floors, knot recess (hard); grooves 40 %; trunk and roots below z 1.0 25 % | rough 0.95 |
| `m047_rock` | v > .7 rock `#DBCCB6` ± 10 (start `#B1ADA8`) | 30–36°, 0.10–0.17, R ≥ G ≥ B, R − B ≥ 25 lit | rocks, pebbles | rough 0.85, metal 0 |
| `m047_rock_light` | lit quartile `#E3D1BB` | 32–36°, 0.12–0.17 | top 30 % of each rock's height at 35 % | rough 0.85 |
| `m047_rock_deep` | the grey swatch `#B1ADA8` | 25–35°, 0.04–0.08 | lowest 0.25 at 25 % | rough 0.9 |
| `m047_sand` | `#E2C698` ± 8 | 36–39°, 0.30–0.35 | patch | rough 0.95 |
| `m047_sand_deep` | shade quartile `#DEC293`, toward the tan `#B89073` | 30–38°, 0.33–0.40 | within 0.5 of trunk, roots, rocks 25 %; bevel 30 % | rough 0.95 |
| `m047_plant` | lime leaves `#8CA824`; v > .7 `#A8BC28` | 64–72°, sat ≥ 0.75 | outer / taller tuft leaves; sprigs | rough 0.85, low spec |
| `m047_plant_mid` | green leaves `#4B7526` | 88–98°, 0.6–0.7 | inner tuft leaves; B1's 3 outer leaves | rough 0.85, low spec |
| `m047_plant_deep` | dark leaves `#18492C` rendered lit (start `#2D5642`) | 120–150°, 0.5–0.65 | B1's 8 leaves | rough 0.85, low spec |

**Calibration warnings:**
- **Pads (W04 P2, M035, M036, M038: dark, grey or olive).** f34 canopy lit (v > .7) within 12 of `#B0C431`, whole
  median within 15 of `#50822F`, sat median ≥ 0.6. C must measure lighter than L and R.
- **The kit studio lights both halves** (042 stage 4): don't calibrate the base to the sheet's lit half alone or the
  whole canopy goes lime (042's first pass reached `#9CBE35`). Calibrate the base to the whole-canopy median, the light
  key to v > .7.
- **Bark:** f34 lit half within 12 of `#A05829`, R > G > B; the whole-trunk median will be lighter than `#8B4E2A` (our
  shade side is lit): record, ≤ 25 levels.
- **Rock:** R ≥ G ≥ B on every median; never pink, never blue.
- **Plants vs pads:** `m047_plant` ≥ 8° yellower than `m047_leaf_light` after calibration.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Pads:** per pad offset (C +40 % light, UR / UL +25 % on their top lobes, L / R base); per lobe role (core 40 %
  deep, ring lobes base, top lobes light per the table). Blend across the lobe overlap (steps 3) so neighbouring lobes
  shade into each other; Tint ±0.04 per lobe. **No lime cap per lobe** (042 finding 3).
- **Trunk, roots, limbs:** `bark` base; `bark_deep` in the grooves (by the pulled-in vertices: position, not normals),
  below z 1.0 (25 %), hard in every hole; `bark_light` hard on cut faces, 20 % on proud ridges' upper halves; limbs a
  touch lighter toward their twig ends (10 %). Per-plank tint ±0.04 (whole facets).
- **Rocks:** height bands within each rock (light top 30 %, deep lowest 25 %).
- **Sand:** distance and bevel; averaged with neighbours before quantising (no triangle shards).
- **Plants:** per leaf by role.
- **Hard edges only** where materials meet: bark | leaf (twig in lobe), bark | sand, rock | sand, leaf | sand, cut face
  | bark, hole | rim.

### 5.6 Texture (Tint) and finish

- **Tint:** lobes amp 0.04 per lobe plus broad noise 0.03 at scale 0.5; bark 0.04 per plank column plus 0.04 / 0.35;
  rock 0.04 per facet; sand 0.03 at scale 0.15; leaves 0.04 per leaf. Never per-triangle confetti.
- **Finish:** pads and plants low spec, rough 0.85; bark 0.9 (deep 0.95); rock 0.85; sand 0.95. No emission.

### 5.7 Re-measure (final renders against the sheet, same masks)

- **Canopy:** f34 lit (v > .7) within 12 of `#B0C431`; whole within 15 of `#50822F`; C lighter than L and R; front /
  rear canopy medians within 15 of `#4B802F` / `#50832F`; top within 15 of `#5C892C`.
- **Trunk:** f34 lit half within 12 of `#A05829`; v > .7 within 15 of `#DB843B`.
- **Rock:** f34 v > .7 within 10 of `#DBCCB6`, R ≥ G ≥ B.
- **Sand:** within 8 of `#E2C698`.
- **Plants:** f34 v > .7 within 12 of `#A8BC28`; a dark bush present (dark-band share ≥ 20 % of plant pixels).
- **Shares** per §2.5.

## 6. Joins and contact (no floating dressing)

- **Shells:** trunk + roots one closed shell (unioned); fork stubs and sockets either part of that shell or buried
  closed shells (decision §8.6); each limb, twig, stub, lobe, rock, pebble, leaf and plant hub its own closed shell; the
  patch one closed shell. All in one hero object.
- **Limb in socket:** the plug enters the hole 0.30 deep with 0.02 radial clearance and its end 0.015 above the hole
  floor: contact within 0.03, no coincident faces, the hole's rim covering the seam. Read the clearance back (BVH
  nearest distance per limb: 0.005–0.03).
- **Twigs:** roots buried 0.2 in the limb; tips buried 0.25–0.4 in the core lobe.
- **Lobes:** each overlaps the core by 0.3–0.6 (buried part hidden); ring lobes may overlap neighbours by up to 0.3;
  no lobe touches only by a corner.
- **Base:** rocks sunk 0.10, pebbles 0.04, hubs 0.03; every leaf within 0.03 of its hub; leaves may touch rocks, roots
  or the trunk but cut ≤ 0.05 into them.
- **Count floating shells before reporting** (STAGES; 035 and 036 failed round 1): **0**. A shell floats if its nearest
  distance to every other shell and the ground is > 0.03 or it doesn't chain to the ground. Pads are the risk here:
  every lobe → core → twig → limb → socket → trunk → patch.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0 (socket rims, lobe apexes and leaf hubs are the
  likely spots).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no particles, no falling needles, no motes, no resin. The cast
shadow is the render's.

- **Stage 5 (lighting): skip, and record why.** No emission, no lights. Studio notes (Requires Manual Validation): the
  pads read lime on top and deep green below under the game sun (W04 P2); the bark stays orange-brown, not red; the
  knot and hollows read dark; the rocks stay warm grey.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** Not recommended: falling leaves, pollen, dust.
- **Collision:** hero `precise` (players walk under the low pads and between the roots; a hull would wrap a 20 × 14 ×
  20 block); ForkedTrunk `hull`, the branch parts `hull`, RootBase `precise`.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json`, the W-sheet
scripts, the repo text (`git grep`) and every sheet / kit / wip `.blend` (zstd-decompressed, `blendall.py`):
- **W04:** `OldPine`, `OldPineSplitTrunk`, `OldPineBent`, `OldPineBrokenCrown`, `OldPineCanopyTier`,
  `OldPineBranchAngled`, `OldPineBranchA`, `OldPineBranchB`, `OldPineForkedTrunk`, `OldPineRootsBase` (in `W04.blend`,
  the kit file and every wip copy); also `YoungFir*`, `ClassicPine*`, `Sapling*`; keys `w04_*`.
- **Other trees:** `AncientTree*`, `AncientBranchModule`, `OakTree*`, `DeadTree*`, `GoldencrownTree`,
  `GoldencrownAncientFork`, `SilverbarkTree`, `JuniperGnarled`; `TieredFir*` (042), `PineSapling*` (045), `pine_*`
  (032 / 037).
- **`GnarledPine`, `ElderPine`, `AgedPine`, `VeteranPine`, `KnottedPine` and `m047` occur nowhere** (repo text,
  manifests, any `.blend`). `GnarledPine*` contains no W04 name as a substring (`JuniperGnarled` is a different order).

| Object | Part | Why |
| --- | --- | --- |
| `GnarledPine` | hero: base, trunk, five branch pieces | W04 owns `OldPine*`; "gnarled" names the old, knotted, forked read |
| `GnarledPineForkedTrunk` | "Forked Trunk": body, sockets, roots, back stub, knot | the sheet's label |
| `GnarledPineCrownCanopy` | the crown piece: crown limb + cut stub + pad C | unlabelled on the sheet; the biggest piece |
| `GnarledPineCanopyTier` | "Canopy Tier": the upper-left piece (limb + pad UL) | the label's arrow |
| `GnarledPineBranchAngled` | "Branch (angled)": the lower-left piece (limb + pad L) | the label's arrow |
| `GnarledPineRootBase` | "Rocks / Base": patch, 6 rocks, 4 pebbles, bush, 5 tufts, 4 sprigs | the sheet's label |

- Palette keys `m047_*` (§5.4). Collection `Kit/M047 Old Pine`. No sockets.

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **20.0 tall, canopy 20.3 × about 12, trunk Ø 6.2 at z 5–7, patch about 17 × 14** (recommended: the
   biggest and heaviest pine; low pads above head height; base dressing at knee-to-shoulder), or 18 (trunk 5.6, pads at
   7), or 24 (nearer W04's 26; boulders chest-high).
2. **Name (§8):** **`GnarledPine` and the five parts above** (recommended), or `ElderPine`. Not `OldPine*` (W04).
3. **Pads (§2.3):** **five separate pads of faceted closed lobes (C 9, UL 6, UR 7, L 8, R 7; about 29 tris each),
   seated on 2–3 twigs, no booleans** (recommended), or one hull-like closed mesh per pad (one shell each, but harder
   to scallop and riskier to build).
4. **Joints (§2.2, §3.5, §3.6):** **five hexagonal sockets as on the sheet (leader top, UL side, left fork, right fork,
   low right), plugs 0.30 deep with 0.02 clearance; sockets and plug ends modelled hollow** (recommended), or limbs
   simply buried in the trunk (no sockets: loses the sheet's construction).
5. **Exported parts (§8):** **ForkedTrunk, CrownCanopy, CanopyTier (UL), BranchAngled (L), RootBase** (recommended:
   the labels plus the crown piece), or all five branch pieces (add `…BranchRight` (R) and `…BranchUpper` (UR)).
6. **Trunk shell (§6):** **roots unioned into the body one at a time at the origin (as 042); fork stubs, sockets and the
   back stub modelled into the body mesh as explicit ring stacks rising out of plank pairs** (recommended: no extra
   booleans, no seams), or every stub a buried closed shell (simplest, but a visible crease where each meets the bark).
7. **Pad depth (§3.3):** **moderate front-back spread (L, R at y −2; UL, C, UR at +1.5 … +3), crown set back so the
   limb star shows from above** (recommended), or the top cell's full spread (depth 17, which breaks the f34 and front).
8. **Side cell (§3.2):** **judged for content only** (recommended).
9. **Dressing (§2.4):** **6 rocks, 4 pebbles, 1 dark broad-leaf bush, 5 tufts, 4 sprigs, on the f34 + front + rear
   plan** (recommended).
10. **Comparison cameras (§3.1):** **`f34_sheet (+25, 10)` governing** (probe az +10 … +40, e 6–14); `r34_sheet (+205,
    11)`; `front_sheet (0, 6)`, `side_sheet (90, 6)`, `rear_sheet (180, 6)`; kit `top`, `underside`; extras: parts shot
    (+20, 15), `join_cu (−20, 25)`, `base_cu (+15, 18)`, `foliage_cu (−35, −8)`, scale shot. Floor hidden in every
    `*_sheet` render.
11. **Colour (§5):** **leaf base / light / deep calibrated to the whole-canopy median `#50822F`, v > .7 `#B0C431` and
    the dark swatch; C the lightest pad; colour by pad and lobe role, never by facing; bark lit half `#A05829`; cut
    faces `#BE7239`; hollows `#42281A`; rock lit `#DBCCB6`; sand `#E2C698`; plants lime / green / dark per leaf**
    (recommended).
12. **Stages 5 and 6:** **skip both, recorded** (recommended).
13. **Collision (§7):** **hero `precise`, ForkedTrunk and branch parts `hull`, RootBase `precise`** (recommended).
14. **Budget (§4.3):** **4000 limit, about 3100–3500 planned, ceiling 3800; parts under 1000** (recommended).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **Reading as 042 / 045 or W04's `OldPine`.** The verifier compares the f34 renders of 042, 045 and 047 side by side.
   047 must show: W : H ≈ 0.95, **T 37.6 ± 4 %**, a trunk 0.31 H thick, five separate pads on visible limbs with sky
   between, no tiers, no flaps or plates.
2. **Floating dressing (STAGES; 035 and 036 round 1).** Every lobe, twig, limb, rock, leaf and hub within 0.03 of a
   neighbour, its core, its socket or the patch, and chained to the ground: **0 floating shells**. Pads are the new
   risk: a lobe touching nothing but air, a twig tip short of the core, a plug hovering in its socket.
3. **Sparse, spiky or see-through pads (042 finding 2).** Each pad is a dense mound: no core or limb visible through it
   from the sides or above; scalloped, not spiky; W : H 1.4–1.6; a near-flat underside.
4. **Lumpy balls or lettuce heads (M036 "ivy mounds", M038 "cupped lettuce").** Lobes are low-poly faceted domes with
   big flat facets and flat-ish bottoms, not smooth spheres, not cups; the pad's top is a rosette from above.
5. **A per-lobe lime cap pattern (042 finding 3).** Light / deep by whole pad and lobe role, gentle; no regular lime
   spots.
6. **Colour by facing (042 ruling).** No dark undersides painted on pads, no light-right / dark-left bark. Fields by
   pad, lobe role, height, groove position and cut faces; `K.check` facing correlation < 0.5 per material.
7. **Canopy too dark, grey or olive (W04 P2; M035; M036; M038).** Lit canopy within 12 of `#B0C431`, sat ≥ 0.6;
   C lighter than L and R.
8. **A thin or hidden skeleton (W04 "cone trunk"; the user's tree rule).** Trunk Ø 6.2 at z 5–7; bare trunk band z 4–7.7
   in the front and rear; limbs, elbows and twigs visible under every pad in the front, rear, f34, r34 and from below;
   the limb star visible from above (top T ≥ 5 %); seven roots of different reach (5.5–8.6), checked in `base_cu`,
   front, side, rear and underside.
9. **Hollows that don't read (W04 V8g).** The knot, the crown-limb stub and the back stub each show a dark hole with a
   lighter cut rim at cell scale in their views (front / f34, front / rear / f34, rear / r34).
10. **Egg or mauve rocks (M034 round 1; M037 "rock parts egg-shaped").** Chunky angular blocks, flat base, sloping
    faceted top, 10–16 broad facets, W : H 1.2–1.6; R ≥ G ≥ B, hue 30–36°.
11. **Spiky or edge-on ground leaves (039).** Broad folded leaves (length : width ≈ 2.4–3), never needles, not edge-on
    to the f34 or front camera; the dark bush is a mass of broad leaves, not a ball.
12. **Over-wide patch or base clutter (042 finding 4).** Patch about 17 × 14 and thin; f34 S ≤ 5.4 %; dressing below
    3.4 tall and inside the patch.
13. **Bowties and slivers.** `M.fix_bowties` everywhere; collapse union corners under 3° on the trunk (042 finding 1).
14. **Exact booleans:** only the roots into the trunk, at the origin, one at a time, saving between them (STAGES
    "Booleans"). Pads, limbs and stubs are never unioned.
15. **Names and scope.** No `OldPine*` (W04), no `TieredFir*` / `PineSapling*`; only one agent drives a Blender session
    at a time; no commits, pushes or exports in stage agents; don't edit `lib/vfx.py` or the frozen shared helpers;
    don't touch M045's objects (being modelled in parallel).

## Decisions (main session, 2026-10-29)
All 14 recommendations are accepted.
1. **Size:** 20 tall, canopy about 20.3 × 12, trunk Ø 6.2. Low pad undersides at 7.7–9, so players walk under them.
2. **Names:** `GnarledPine`, plus `GnarledPineForkedTrunk`, `…CrownCanopy`, `…CanopyTier`, `…BranchAngled` and `…RootBase`. Keys `m047_*`. Never `OldPine*` (W04).
3. **Pads:** separate closed faceted lobes (C 9, UL 6, UR 7, L 8, R 7), seated on twigs by contact, with no booleans. **No floating lobes, twigs or plugs.**
4. **Joints:** five hexagonal sockets. Limbs plug in 0.30 deep with 0.02 clearance.
5. **Exports:** the hero plus the five parts.
6. **Trunk:** only the roots are unioned. Fork stubs, sockets and the back stub are built into the trunk mesh. Every shell is manifold with 0 bowties.
7. **Pad depth:** a moderate spread, so the brown limb star shows from above.
8. **Side cell:** judged for content only.
9. **Dressing:** 6 angular rocks (not eggs), 4 pebbles, 1 broad-leaf bush, 5 tufts and 4 sprigs, all seated.
10. **Cameras:** the front three-quarter at (+25, 10) governs. The rest are as listed, plus close-ups and a scale shot.
11. **Colour:**
    - Foliage keys are calibrated to the canopy median `#50822F`, the brightest pixels `#B0C431` and the dark swatch. The crown pad is the lightest.
    - Colour follows the pad and lobe role, **never facing**. There is no lime cap on every lobe.
    - Bark: lit `#A05829`, cut faces `#BE7239`.
    - Hollow interiors `#42281A` are a geometric region: the inner faces of each hole.
    - Rock lit `#DBCCB6` (R > G > B, never mauve). Sand `#E2C698`.
12. **Lighting and VFX:** both skipped and recorded.
13. **Collision:** hero precise.
14. **Budget:** a limit of 4000, with a planning ceiling of 3800.

**Binding checks:** §1.5, which separates this tree from M042, M045 and W04, and the f34 shares (green 48.2 %, bark 37.6 % ± 4).

## Stage 1 — Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m047.py` (`build()`), background session port 9880 on `wip/M047.blend`. Every exploded part has
its own function and the hero is assembled from exactly those functions:
- `trunk_body()` (planked body: 9 sides each split once = 18 facets, grooves pulled in / proud planks pushed out, rings
  twisted 3° per level, the flare offset to −X so the trunk leans to +X; the leader top is a 9-corner ring with a socket
  hole tilted 18° back toward the crown pad), `knot()` (the front knot cut into one plank facet: raised rim + 0.28 deep
  hole, built into the body, no boolean), `stub()` (four hexagonal socket stubs with walled holes: lf, rf, lr, ul; the back
  hollow stub), `root()` ×7 (four-sided buttress prisms, kinked once, ridge rising inside the trunk). Only the stubs and
  roots are exact-unioned into the body, one at a time at the world origin (`m033._union_fine`, merge 0) → one shell.
  **Deviation from decision 6:** the fork stubs are unioned closed hex prisms, not hand-bridged ring stacks; the result is
  still one manifold trunk shell with no seam shells and 0 bowties.
- `limb()` (hex tube: hollow plug end in the hole, a thin shoulder 0.05–0.09 over the rim slightly wider than the stub
  so it hides the rim, elbows, flat twig-fork end), `twigs()` (4-sided, roots buried in the limb end, tips buried 0.32
  in the core lobe), `cut_stub()` (crown limb), `pad()` (core + lower ring + upper ring + top lobes; `lobe()` = 22-tri
  hexagonal faceted dome, core 18 tris). `branch_piece()` = limb + twigs (+ stub) + pad.
- `root_base_part()`: `patch()`, `rock()` ×6 + `pebble()` ×4 (ring-stack hulls with a sloping crown, not balls),
  `clump()` ×11 (bush B1, tufts T1 T2a T2b T3 T4 T5, sprigs S1–S4; closed 8-tri leaves round a buried hub).

Layout as built (build frame): pads C (1.7, 3.9) 15.2→20.0 W 8.0; UL (−3.4, 4.1) 14.4→18.6 W 6.0; UR (7.4, 1.6)
13.5→17.4 W 6.4; L (−5.4, −3.0) 8.7→14.3 W 9.2; R (7.2, −3.3) 7.7→12.3 W 7.2. Lobes: C 13, UL 10, UR 11, L 13, R 12 = 59
(more, smaller lobes than the study's 37: the sheet's lobes are about a third of the pad wide). Socket faces: top
(1.85, 0.6, 13.5), lf (−2.38, −0.47, 8.34), rf (4.30, 0.95, 12.64; it protrudes 1.9 so its whole hole clears the leader),
lr (3.74, −1.62, 8.05), ul (−0.59, 1.54, 12.49); back stub face (1.55, 3.55, 9.69); knot (0.94, −1.92, 9.5).
Roots reach 5.6 / 5.9 / 6.4 / 6.8 / 7.2 / 7.4 / 8.6 (RT1, front-right, the longest).

Iterations (side by side against the sheet cells, scratch `m047w/cmp.py`):
1. Pads of 6–9 big gem lobes read as separate balls → 59 smaller hexagonal lobes in three tiers, ring lobes tilted out.
2. The trunk read as a column with swallowed roots → asymmetric flare, narrower foot (r 4.2), taller and wider roots;
   the fork widening removed so the trunk tapers like the sheet.
3. Stubby hidden limbs → limb shoulder wider than the stub, elbows, inner lower lobes lifted so the limbs show.
4. Top view covered → pads spread a little in Y (decision 7) so the brown limb star shows (top T 18 %).

## Stage 2 — Optimisation and cleanup

| Object | Tris | Size (studs) | Shells |
| --- | --- | --- | --- |
| GnarledPine (hero) | **3746** (ceiling 3800) | 20.35 × 15.99 × 19.98 | 150 |
| GnarledPineForkedTrunk | 976 | 14.01 × 12.47 × 13.73 | 1 |
| GnarledPineCrownCanopy | 446 | 8.04 × 7.43 × 7.07 | 18 |
| GnarledPineCanopyTier | 310 | 6.12 × 5.73 × 6.94 | 13 |
| GnarledPineBranchAngled | 400 | 8.49 × 7.41 × 6.99 | 17 |
| GnarledPineRootBase | 904 | 17.83 × 15.99 × 3.64 | 72 |

- Hero tris by shell kind: trunk 976, lobes 59 / 1278, limbs 5 / 398, cut stub 46, twigs 12 / 144, rocks + pebbles
  10 / 320, patch 96, leaves + hubs 61 / 488.
- Budget savings: knot built as an inset (−60 against a union), 4-sided roots and twigs, 2-segment RT2 / RT4, a
  9-corner leader top, 5-sided core lobes, a 16-point patch.
- Every object: 0 non-manifold edges, 0 bowtie verts, 0 boundary / wire / loose / zero-area / n-gon / duplicate verts,
  normals outward, transforms applied, origin bottom centre (offsets in `o["m047_offset"]`; hero 0.49, −0.29, 0).
- Per shell, all six objects: **0 winding errors** (manifold edges whose two faces disagree, `BMEdge.is_contiguous`),
  0 self-intersections, volume > 0. Smallest corner 2.01° (trunk union seams; slivers under 2° forced). `K.check`: clean.
- **Contact (no floating dressing):** floating 0, unchained 0 in all six objects (tol 0.03; chained to the patch in the
  hero and root base, to the trunk or limb in the parts). Plugs (`plug_report`): every plug corner 0.015–0.053 from the
  socket walls / floor, none inside the trunk solid.

## Stage 3 — UV

`M.smart_uv` angle-based (45°, margin 0.008) + `m012._uv_unfold`: all six objects 0 overlaps, 0 flipped, min island gap
0.016, border 0.008, density 1.0 / 1.0 / 1.0, conformal stretch p95 ≤ 1.026. Islands: hero 1482, trunk 166, crown 187,
tier 126, angled 183, base 385.

## Stage 4 — Materials, colour and texture

1. **`K.calibrate`** (dome) to TARGETS: leaf `#4F7830`, leaf_light `#8DA031`, leaf_deep `#294C40` (kind "all": the
   green mask rejects the teal), bark `#7E481D`, bark_light `#955E2D`, bark_deep `#301606`, rock `#A9A29A`, rock_light
   `#B4ADA4`, rock_deep (calibrated `#8C8E90` came out blue: set warm `#8E8A85` by hand), sand `#B2A283`, sand_deep
   `#A69175`, plant `#7E9526`, plant_mid `#426526`, plant_deep `#214D33`. Each rendered within 6 of its target on the dome.
2. **Re-measured on the f34_sheet render** (scratch `m047w/col47.py`, the study's masks): the tree renders darker than
   the dome (lobes and trunk shade each other), so the families were scaled in linear light (leaf ×1.5, bark ×1.45,
   plant mid / deep ×1.4) and the hues set so plant is ≥ 8° yellower than leaf_light (63.8° vs 71.8°).
   **Final `PALETTE`:** leaf `#5F903A`, leaf_light `#A6C234`, leaf_deep `#2D5346`, bark `#955522`, bark_light `#B06F35`,
   bark_deep `#341807`, rock `#A9A29A`, rock_light `#B4ADA4`, rock_deep `#8E8A85`, sand `#B2A283`, sand_deep `#A69175`,
   plant `#919824`, plant_mid `#558331`, plant_deep `#265A3B`.
3. **Roles (never facing):**
   - Pads: tone C 0.75, UL / UR 0.25, L / R 0. Top lobes leaf→light 0.5 + tone/2; upper ring 0.25 + tone/2; lower ring
     by plan side: outer (away from the trunk) tone/2, side lobes deep 25 %, inner lobes deep 50 %; cores deep 75 %.
   - Bark: grooves (pulled-in plank verts) and the foot below z 1 deep 25 %; root ridge strips light 25 %; limb last
     segment light 25 %; cut faces (socket rims, plug and stub ends, knot rim, leader top) bark_light, hard; every hole
     interior (socket walls / floors, plug pits, stub pits, knot hole) bark_deep, hard: a geometric region.
   - Rocks by height band (light top, deep foot); sand deep on the bevel and within 0.5 of trunk / roots / rocks;
     plants per leaf (tallest lime, then mid; the bush mostly deep with 4 mid outer leaves).
4. **Tint:** per lobe ±0.04 and pad mottle 0.03 / 0.5; bark per plank column ±0.04 + mottle 0.04 / 0.35; limbs, roots,
   rocks and sand mottled as §5.6; leaves ±0.04. Facing correlation (`kit_baked_shading`): hero 0.02, parts ≤ 0.06.
5. **Finish:** pads and plants rough 0.85, low spec; bark 0.9 (deep 0.95); rock 0.85; sand 0.95; no emission.

**Measured against the sheet** (ours / sheet, same masks):

| View | W : H | G | T | S | R |
| --- | --- | --- | --- | --- | --- |
| f34_sheet (+25, 10) | 0.943 / 0.949 | 48.7 / 48.2 | 38.4 / 37.6 | 4.1 / 3.4 | 7.8 / 9.3 |
| front_sheet (0, 6) | 0.977 / 1.005 | 47.5 / 49.1 | 41.3 / 37.8 | 3.4 / 1.6 | 7.4 / 9.7 |
| rear_sheet (180, 6) | 0.943 / 1.010 | 44.5 / 48.6 | 44.0 / 39.6 | 1.8 / 2.0 | 8.1 / 8.1 |
| r34_sheet (205, 11) | 0.966 / 0.952 | 43.1 / 46.6 | 43.0 / 40.8 | 2.7 / 3.3 | 8.7 / 7.7 |
| side_sheet (90, 6) | 0.739 / 0.714 (content only) | 46.2 | 41.7 | 2.1 | 8.4 |
| top_sheet | W : D 1.379 / 1.138 | 69.8 / 76.9 | 18.3 / 9.2 | | |

- Colours (f34): canopy median `#517D30` vs `#50822F`; G v>.7 `#9AC53B` vs `#AFC330`; trunk median `#915128` vs
  `#8B4E2A`, right (lit) half `#965328` vs `#A05829` (10 levels), v>.7 `#C26E37` vs `#DB843B`; rock v>.7 `#D3C8B2` vs
  `#DBCCB6` (R > G > B); sand `#E3C69A` vs `#E2C698`; plants v>.7 `#BCBF29` vs `#ABBD29`, dark share 25 % vs 33 %.
- Crown lightest pad (f34 crops): C lum 91, L 84, R 73 (sheet 105 / 79 / 87).
- Top profile (front, every 0.1 W): .51 .70 .78 .93 .85 .99 1.0 .85 .87 .84 .46 vs sheet .54 .67 .70 .89 .94 .99 1.0
  .92 .86 .82 .50. Width per height (front): .27 .79 .82 .30 .65 .97 .84 .86 .71 .46 vs .36 .81 .67 .33 .69 1.0 .87 .82
  .72 .42; the bare-trunk row at h .3 is kept (.30).

## Stage 5 — Lighting

Skipped: the sheet shows no emission or light. Studio notes (Requires Manual Validation): pads should read lime on top
and deep green below under the game sun; bark orange-brown, not red; holes dark; rocks warm grey.

## Stage 6 — VFX

Skipped: the sheet shows no effect. No sockets on any object (checked in `build()`).

## Renders

`art/blender/renders/models/M047/`:
- `M047_views.png` (contact sheet); kit `front` `side` `rear` `top` `underside`; `f34_sheet` `r34_sheet` `front_sheet`
  `side_sheet` `rear_sheet` `top_sheet` (floor hidden, long lens); `front34` / `rear34` (25 / 205, 12).
- The five part shots `part_*`; `exploded` (the five branch pieces drawn out of their sockets, the trunk lifted).
- `scale`: a 5.5-stud marker at (8.4, −4.6), inside the R pad's footprint; the R pad's lowest point is 7.7.
- Close-ups: `join_cu` (rf and leader-top sockets from above: hex rims round dark holes, close-up 1), `plug_cu` (the
  angled branch's hollow plug end), `base_cu` (trunk foot, roots, rocks, tufts; close-up 2), `foliage_cu` (the L limb's
  twigs rising into the pad's underside; close-up 3), `stub_cu` (crown cut stub, knot), `back_cu` (back hollow stub).

## §1.5 differences, as measured

| | 047 as built |
| --- | --- |
| Size | 20.35 × 15.99 × 19.98; f34 W : H 0.943, front 0.977 |
| Silhouette | five separate pads with sky between (front top profile above); no tiers, flaps or plates |
| Bark share (f34) | **T 38.4 %** (042 12.8, 045 10.8) |
| Trunk | corner r 3.05 at z 6 (Ø ≈ 6.1), planked 18 facets, centre −0.55 → 1.85 (lean ≈ 8° above z 4), forks at z 8–12.6, leader to 13.5 |
| Branches | five hex-socket limbs (plugs 0.015–0.053 from the walls), 12 twigs (C and L 3; UL, UR and R 2) |
| Foliage | 59 faceted lobes in 5 pads (13 / 10 / 11 / 13 / 12) |
| Roots | 7 buttress roots, reach 5.6–8.6, RT1 8.6 front-right |
| Joints | 5 walled sockets, hollow plug ends, hollow cut stub, hollow back stub, inset knot |
| Top view | rosettes round an exposed limb star: T 18.3 %, G 69.8 % |
| Rocks | lit `#D3C8B2`, warm grey, R > G > B |
| Ground plants | dark broad-leaf bush B1, lime / green tufts, sprigs |

## Modeller's notes for the verifier

- Rebuild in a fresh session: `import kit_mcp; kit_mcp.install(); import m047; m047.build()`.
  `m047.plug_report(bpy.data.objects["GnarledPine"])` gives the plug seats; `shells_report()` includes `winding_errors`.
- Known leftovers:
  1. **Top W : D 1.38** (target 1.05–1.35): decision 7's moderate pad spread keeps the depth near the patch's; the top
     cell's front pad is not modelled (§3.3).
  2. Lime highlights are fewer than on the sheet (f34 canopy lime 19 % vs 31 %, dark 16 % vs 40 %): the sheet's strong
     sun / shade split is light, not paint, and the kit studio lights both sides.
  3. The plants' brightest leaves are a little yellower than the sheet's (`#BCBF29` vs `#ABBD29`), from the rule that
     plant is ≥ 8° yellower than leaf_light.
  4. Front / rear T 41–44 % (sheet 38–40): the trunk foot is a touch broad from those angles; f34 is on target.
  5. The fork stubs are unioned prisms rather than bridged ring stacks (Stage 1); the trunk is still one manifold shell.
  6. Two `plug_gaps` of 0.0 in the hero's contact report are limbs whose shoulders touch the bark beside their sockets,
     not the plugs (`plug_report` is clean).
- No commits, pushes or exports were made.

## Verification round 1 (verifier, 2026-10-29)

Fresh verifier, read-only on port 9880 (`wip/M047_verify.blend`; nothing built, edited or saved). All numbers were
re-measured with my own bmesh / BVH code (not `shells_report` / `plug_report`). Renders and montages are in the
session scratchpad `m047_verify/` (`cmp_<view>.png` sheet | ours, `cmp_conifers.png` 042 | 045 | 047, `big_*`,
`cu_*`, `part_*`).

### Measured

| Object | Tris | Size (studs) | Shells | Non-man. / bound. / wire / loose | Bowtie | Winding | Zero-area / n-gon / dup | Self-hits | Min corner (< 3°) | Origin |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GnarledPine | **3746** / 4000 (ceiling 3800) | 20.35 × 15.99 × 19.98 | 150 | 0 / 0 / 0 / 0 | 0 | **0** | 0 / 0 / 0 | 0 | 2.01° (42) | bottom centre, rot 0, scale 1 |
| GnarledPineForkedTrunk | 976 | 14.01 × 12.47 × 13.73 | 1 | 0 | 0 | 0 | 0 | 0 | 2.01° (42) | ok |
| GnarledPineCrownCanopy | 446 | 8.04 × 7.43 × 7.07 | 18 | 0 | 0 | 0 | 0 | 0 | 8.4° | ok |
| GnarledPineCanopyTier | 310 | 6.12 × 5.73 × 6.94 | 13 | 0 | 0 | 0 | 0 | 0 | 9.9° | ok |
| GnarledPineBranchAngled | 400 | 8.49 × 7.41 × 6.99 | 17 | 0 | 0 | 0 | 0 | 0 | 8.0° | ok |
| GnarledPineRootBase | 904 | 17.83 × 15.99 × 3.64 | 72 | 0 | 0 | 0 | 0 | 0 | 4.4° | ok |

- Every shell of every object has positive volume (normals outward). No modifiers, no custom normals, UVMap present.
- Hero shells: trunk 1, limbs 5, cut stub 1, twigs 12, lobes 59, leaves + hubs 61, rocks + pebbles 10, patch 1.
- **Floating dressing:** 0 shells more than 0.03 from everything, 0 unchained, in all six objects (hero and base
  anchored on the patch, parts on the trunk or limb).
- **Plugs:** all five limbs' nearest corners are 0.015 from the socket walls; no plug corner inside the trunk solid
  (ray parity + nearest-normal test). A few limb **shoulder** corners (UR limb at rf 1, crown limb at the leader top
  2, plus 2 more by the sign test) sit 0.11–0.165 inside the cut rims: hidden under the shoulder sleeve, harmless.
- `K.check`: no problems. `kit_baked_shading` 0.02. Tint (corner) 0.926–1.072, sd 0.021: broad, not confetti.
- No children or VFX sockets, no emission on any of the 23 materials (stages 5–6 skipped as decided).
- Lobes: 59, 18 / 22 tris, height : width median **0.74** (range 0.39–1.07; study 0.55–0.70).
- Trunk sections (ForkedTrunk part, build frame): r_med 4.1 at z 1.2, 2.93 at z 6.0 (Ø ≈ 5.9), 2.29 at z 10.2
  (Ø ≈ 4.6), 1.57 at z 13.2; centre x 0.3 → 1.66 (lean ≈ 7°). Matches §2.2.
- Limb runs, socket face → twig fork (from `LIMBS` / `SOCK` as built): C ≈ 2.5, UL ≈ 3.1, **UR ≈ 2.4 (plan 5.1)**,
  L ≈ 3.2 (rises ≈ 17°), **R ≈ 2.7 (plan 4.3)**.

Views (study masks, `measure_render.py`, floor hidden; ours / sheet):

| View | W : H | G | T | S | R |
| --- | --- | --- | --- | --- | --- |
| f34_sheet (+25, 10) | 0.943 / 0.949 | **48.7 / 48.2** | **38.4 / 37.6** | 4.1 / 3.4 | 7.8 / 9.3 |
| front_sheet (0, 6) | 0.977 / 1.005 | 47.4 / 49.1 | 41.3 / 37.8 | 3.4 / 1.6 | 7.4 / 9.7 |
| rear_sheet (180, 6) | 0.943 / 1.010 | 44.5 / 48.6 | 44.0 / 39.6 (+4.4) | 1.8 / 2.0 | 8.1 / 8.1 |
| r34_sheet (205, 11) | 0.966 / 0.952 | 43.1 / 46.6 | 43.0 / 40.8 | 2.7 / 3.3 | 8.7 / 7.7 |
| side_sheet (90, 6) | 0.739 (0.72–0.9) | 46.2 | 41.7 | 2.1 | 8.4 |
| top_sheet | W : D 1.379 / 1.138 | 69.8 / 76.9 | 18.3 / 9.2 | | |
| 042 TieredFir at (+25, 10) | 0.653 | 71.5 | 11.8 | | |
| 045 PineSapling at (+25, 10) | 0.741 | 76.7 | 9.7 | | |

Colours (f34, ours / sheet): canopy median `#52772F` / `#50822F`; canopy lit quartile `#90BB3E` (81°) / `#ACC230`
(69°); trunk median `#915128` / `#8B4E2A`, lit `#C36E37`; sand `#E3C69A` / `#E2C698`; rock median `#B0A790`, lit
`#DED4BD` (42°, R > G > B, not mauve) / lit `#DBCCB6` (36°).

### Findings

**Passed:** mesh, winding, budget, origin and transforms on all six objects; no floating dressing; plugs seated;
f34 shares (G +0.5, T +0.8) and W : H; §1.5 differences: next to 042 and 045 it is unmistakably a different tree
(W : H 0.94 against 0.65 / 0.74, T 38 % against 12 / 10 %, massive planked leaning trunk, five pads with sky between,
seven buttress roots, sockets, hollows, a bark star from above); it is nothing like W04's slender `OldPine`. Colour
family right (orange-brown bark, warm-grey rock, sand, green pads with a lime crown), hollows are geometric
`bark_deep` regions, no facing-based paint anywhere in `m047.py` (only geometric `.normal` uses), no lime cap per lobe.
Knot, back stub and the ForkedTrunk part's hex sockets read clearly.

1. **Blocker: the limbs and twigs don't read; the skeleton is the subject of this sheet (spec §1, user tree rule).**
   - In the f34, front, rear and r34, the limbs are short, thick, near-level stubs that run straight into the pads.
     UR and R are about half their planned length (2.4 and 2.7 against 5.1 and 4.3), and the L limb rises only about
     17° (the sheet shows 30–45°, with an elbow). The 12 twigs are hidden in every view except two under UL.
   - Close-up 3 (a limb splitting into three twigs under a flat pad underside) has no counterpart: `cu_foliage_L`
     shows the limb disappearing into drooping lower lobes.
   - The `BranchAngled` part reads as a heap of lobes with a stub behind it, where the sheet's "Branch (angled)" is a
     long elbowed limb with the pad on its end.
   - **Fix target:**
     - Bring back the planned runs: UR from a lower right fork (z ≈ 10.4) about 5 long, R about 4.3, L rising 30–40°
       after one elbow.
     - Seat each pad so 1.5–2.5 studs of limb show between the bark and the pad in the front, rear and f34, and the
       2–3 twigs (Ø 0.6–0.75) show under every pad.
     - Raise or remove the inner lower-ring lobes that hide the twig fork, so each pad has the near-flat underside the
       twigs enter (§2.3).
     - Check: the twigs are visible under at least L, R and UR in `front_sheet`, and `foliage_cu` matches close-up 3.
2. **Blocker: the pads read as bunches of separate faceted balls, not scalloped cloud mounds (pitfall 4, the class
   failure of M036 / M038).**
   - Each lobe is a d20-like gem (height : width median 0.74, up to 1.07), and the 59 lobes stay distinct.
   - The lower ring's role colour puts a dark band through the middle of each pad, with lighter outer lobes below it.
     The sheet's pads are one mound: a lit rosette top, scalloped sides, and the darkest tone at the bottom.
   - **Fix target:**
     - Flatten the lobes to height : width 0.55–0.65.
     - Overlap them more (ring lobes 0.4–0.6 into the core), so each pad reads as one dome with a scalloped outline.
     - Give each pad a broad top rosette of large flat facets (decision 3's 6–9 lobes per pad is the reference
       count; 59 is past it).
     - Order the role tones by height within the pad: the lowest lobes deepest, the ring at the pad's tone, the top
       light. That is by role, not by facing, and keeps C the lightest pad.
3. **Minor: spiky ground plants.** The bush B1 is a pointed star, and the tufts look like agave. The sheet shows a
   mound of broad leaves and broad upright tufts (pitfall 11, and the "spiky where the master is broad" lesson).
   **Fix target:** broad ovate leaves with rounded tips, and the bush as a domed mass of 10–12 overlapping leaves.
4. **Minor: the crown cut stub doesn't read.** It is hidden by the crown limb and pad in the f34 and front.
   **Fix target:** move it out so its hollow end faces the f34 camera at about (2.9, 1.2, 15.1) (§2.3), with a dark
   pit and a light rim visible.
5. **Minor: 42 corners under 3° (min 2.01°) on the trunk union seams.** Pitfall 13 asked for none under 3°. It does
   no harm on an opaque, flat-shaded solid in Roblox. Collapse them if the trunk is rebuilt.
6. **Minor (main session to rule): decision 6 deviation.** The fork stubs are exact-unioned prisms, not ring stacks
   built into the body. The result is clean (1 shell, 0 bowties, 0 self-hits, 0 winding errors), and the junctions
   read as joins rather than seams. I accept it on outcome. It is the source of item 5.
7. **Minor (main session to rule): decision 3 lobe counts.** The pads have 13 / 10 / 11 / 13 / 12 lobes, against the
   decided 9 / 6 / 7 / 8 / 7. This feeds item 2.
8. **Minor: top view.** W : D is 1.38 (the target is 1.05–1.35). The pads crowd each other, so the rosettes are not
   clearly separate from above. The limb star does show (T 18 %). Accepted as a leftover, but item 1's pad moves
   should open the gaps.
9. **Minor: lime highlights.** The f34 canopy lit quartile is `#90BB3E` (81°) against `#ACC230` (69°): too few, and
   too green. This is partly the two-sided studio light (the modeller's note 2). Item 2's top rosettes on C and UR
   should carry more `leaf_light`. The plants' slight yellow (note 3) is accepted.
10. **Minor: front and rear bark at 41.3 % and 44.0 %** (sheet 37.8 and 39.6; the rear is 0.4 outside ±4). The f34,
    which is binding, is on target. Re-measure after item 1.
11. **Minor: other shapes.**
    - The rocks are faceted domes, a little rounded, and a touch yellow (42° against 36°). They are still R > G > B
      and not eggs. Give RK1 a flatter, more angular top.
    - The knot reads as a dark rectangular slot. A rounder hex rim would read as a knot.
    - The trunk lacks the sheet's gentle S-curve, though its lean and sections match §2.2.
    - The patch is 16 deep against about 14 in the plan.

**Decisions:**
- 1, 2, 4, 5, 8, 9 (counts: 6 rocks, 4 pebbles, 1 bush, 6 tuft clumps (T2 counted as two clumps), 4 sprigs), 10, 11,
  12, 13 and 14 were followed.
- 3: no floating lobes, twigs or plugs, and no pad booleans, but the lobe counts depart from the decision (item 7).
- 6: deviates (item 6).
- 7: moderate depth, and the limb star shows.

**Score: 6.5 / 10.** The mesh is clean and the colour, shares and §1.5 separation are good. The skeleton and pad
form don't match the sheet yet.

**Verdict: FAIL.** Fix blockers 1 and 2: the visible limbs, twigs and flat pad undersides, and the pads as flattened,
overlapping single mounds. Pick up minors 3 and 4 in the same pass. Then a fresh verifier runs round 2.

## Main session ruling after round 1 (2026-10-29)
- **Item 6 (fork stubs exact-unioned):** accepted on outcome. The trunk is one clean manifold shell. The sub-3° seam corners are minor.
- **Item 7 (lobe counts):** reduce toward decision 3's 9/6/7/8/7, to at most 1.5× those counts (14/9/11/12/11). Use fewer, larger, flatter lobes that overlap, so each pad reads as one dome. This feeds blocker 2.
- Fix round 1 covers blockers 1 and 2 and minors 3 and 4, with targets as in Verification round 1.

## Fix round 1 (fix modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m047.py` edited (the source of truth); port 9880 on `wip/M047.blend` (saved). Final numbers come
from a freshly restarted session (`kit_mcp.install(); m047.build()`), measured with the study masks
(`measure_render.py`, `col47.py`) and the builder's own checks. Scratch: `m047fix/` (`final.json`, `cmp3.png` sheet |
ours for f34 / front / rear / r34, `big_*.png`). No commits, pushes or exports.

### Changes

1. **Skeleton (blocker 1).**
   - Sockets moved so each limb has a real run and rise: right fork `rf` face (4.12, 0.79, **10.49**), was 12.64 and
     protruding 1.9; low right `lr` face (3.73, −1.71, **4.94**), was 8.05; left fork `lf` face (−2.88, −0.68,
     **6.59**), was 8.34. `out` raised on `rf` / `lr` / `lf` (0.95 / 0.85 / 1.0) so no plug corner sits inside the bark
     (`plug_report` inside_solid 0 everywhere).
   - New `LIMBS` waypoints: every limb leaves along its socket axis, bends at an elbow, then rises 30–46° to a twig
     fork placed 1.2–1.5 below its pad's flat core underside, so the 2–3 twigs (now Ø 0.74 → 0.56; three on L, R, UR
     and C, two on UL) show under the pads.
   - Pads re-seated outward and lower (L c (−5.6, −3.0) core 9.6; R (7.2, −3.2) core 8.75; UR (7.6, 1.6) core 14.2;
     UL core 15.2), so the limbs show between the bark and the pads instead of running straight into them.
   - Inner ring lobes (toward the trunk) lifted 0.5 above the core underside; the rim only droops on the pad's outer
     side in X (the lobes facing the −Y cameras stay up), so the underside is near-flat where the twigs enter.
   - Branch-piece part shots now from (33, 6) (side-on to the limbs) and `foliage_cu` from (33, −6), side-on to the L
     limb, like close-up 3.
2. **Pads as single domed clouds (blocker 2).** `pad()` rewritten: one broad flat-bottomed core (h : w 0.5–0.6, 6
   sides), a ring of 5–7 flattened lobes (0.44 W wide, h : w 0.54, centres 0.31 W out, overlapping the core by about
   half their width, tilted out 7°), an upper ring of 2–4 lobes over the core's shoulder (0.38 W) and one broad 7-sided
   top lobe (0.46 W; the rosette from above). Ring and upper lobes are 5-sided (18 tris: bigger facets, fewer tris).
   Colour by **lobe mid height within the pad** (`_pad_key`): the lowest lobes `leaf_deep` 50 % (25 % on the crown
   pad), then 25 % deep, the middle at the pad's tone, the upper ring light 25–50 %, the top lobe light 75–100 %; C
   (tone 0.75) lightest. Position and role only; no normal is used for colour.
3. **Ground plants (minor 3).** `_rleaf` (m044's `_dleaf`: a 10-tri broad round-tipped leaf with a raised midrib and a
   flat underside) replaces the pointed `_leaf8` on every tuft and sprig; tufts L : W 2.0. The dark bush B1 is now
   `bush()`, m044's dome bush on the flat patch: a hidden 16-tri heart dome clad in ten round-tipped leaves (crown 3
   mid green, middle 3 and skirt 4 deep), every leaf slid to touch the heart; skirt leaves climb the dome if they would
   cut the sand or a root (`_trunk_guard`, a BVH of the built trunk). Tuft counts trimmed (T1 5, T2a 5, T5 4) and one
   deep leaf added per larger tuft, to keep RootBase under 1000 and the plants' dark share ≥ 20 %.
4. **Crown cut stub (minor 4).** `CUT_STUB` r 0.5, 1.9 long, from 0.6 along the crown limb's first segment, pointing
   az 325° tilted 52°: its end (3.08, −0.12, 15.1) faces the f34 and front cameras below the crown pad; hollow 0.6 ×
   0.3 (a `bark_deep` pit in a `bark_light` rim). Reads as a dark hole in `f34_sheet`, `front_sheet` and `stub_cu`.
5. New checks in the builder: `limb_visibility()` (per limb and view, the centreline length not hidden behind pads,
   trunk or base, and the twigs at least half seen), `lobe_report()` (lobe height : width as the round-1 verifier
   measured it), `STUB_INFO`; `_kind` classifies 10-tri leaves and 8 / 16-tri hubs.

### Before → after

| Measure | Round 1 | Fix round 1 | Target |
| --- | --- | --- | --- |
| Hero tris | 3746 | **3590** | ≤ 3800 |
| Parts: trunk / crown / tier / angled / base | 976 / 446 / 310 / 400 / 904 | 960 / 410 / 280 / 328 / 992 | < 1000 |
| Hero size | 20.35 × 15.99 × 19.98 | 20.93 × 15.99 × 20.00 | 20.3 ± 0.8, H 20 ± 0.4 |
| Lobes per pad C / UL / UR / L / R | 13 / 10 / 11 / 13 / 12 (59) | **13 / 9 / 10 / 11 / 10 (53)** | ≤ 14 / 9 / 11 / 12 / 11 |
| Lobe h : w median (min–max) | 0.74 (0.39–1.07) | **0.607 (0.53–0.66)** | 0.55–0.65 |
| Limb run, socket face → twig fork: C / UL / UR / L / R | 2.5 / 3.1 / 2.4 / 3.2 / 2.7 | 2.27 / 3.13 / **3.92** / 3.27 / **4.13** | UR ≈ 5, R ≈ 4.3 |
| Rise, last segment (overall): UR / L / R | – / ≈ 17° / – | 46° (36°) / 35° (29°) / 34° (36°) | 30–45° |
| Visible limb, front (3D, not hidden by pads / trunk): C / UL / UR / L / R | stubs | 2.4 / 2.8 / 3.9 / 3.3 / 4.1 | 1.5–2.5+ |
| … rear | | 2.5 / 3.1 / 3.9 / 3.2 / 3.8 | |
| … f34 | | 2.5 / 2.6 / 2.3 / 3.3 / 4.1 | |
| Twigs at least half seen, front (L / R / UR / UL / C) | hidden (2 under UL only) | **3 / 3 / 3 / 2 / 3** | L, R, UR visible |
| … f34 ; rear | | 1 / 1 / 3 / 2 / 3 ; 3 / 3 / 3 / 2 / 1 | |
| f34 W : H | 0.943 | 0.977 | 0.89–1.01 (sheet 0.949) |
| f34 G / T / S / R | 48.7 / 38.4 / 4.1 / 7.8 | **47.0 / 40.6** / 3.7 / 7.6 | 48.2 ± 4 / 37.6 ± 4 |
| front G / T, W : H | 47.5 / 41.3, 0.977 | 45.0 / 43.9, 1.000 | 49 ± 5 / 38 ± 4 (minor) |
| rear G / T | 44.5 / 44.0 | 41.5 / 46.9 | 48.6 / 39.6 (minor) |
| r34 G / T | 43.1 / 43.0 | 40.9 / 45.4 | T 40.8 ± 5 |
| side W : H | 0.739 | 0.750 | 0.72–0.9 |
| top W : D, G, T | 1.379, 69.8, 18.3 | 1.356, 75.3, 16.2 | 1.05–1.35, ≥ 70, ≥ 5 |
| f34 canopy median / lit (v > .7) / lime share | `#52772F` / `#90BB3E` / 19 % | `#5D8D30` / `#A2C93A` / 30 % | `#50822F` ± 15 / `#B0C431` ± 12 / 31 % |
| Pad lightness, front (C top mass / L / R) | | 122 / 118 / 117 | C lightest |
| f34 trunk median / v > .7 | `#915128` / `#C26E37` | `#8A4E28` / `#C36E37` | `#8B4E2A` / `#DB843B` |
| f34 rock v > .7, sand | `#D3C8B2`, `#E3C69A` | `#D4C7B2`, `#E3C69A` | `#DBCCB6` ± 10, `#E2C698` ± 8 |
| f34 plants v > .7, dark share | `#BCBF29`, 25 % | `#BDBE2B`, 21 % | `#ABBD29`, ≥ 20 % |
| Floating / unchained shells (all 6 objects) | 0 / 0 | **0 / 0** | 0 |
| Non-manifold / bowtie / boundary / winding / self-hits (every shell, all 6) | 0 | **0** | 0 |
| Plugs: corner gap, inside solid | 0.015–0.053, 0 | 0.015–0.053, **0** | seated |
| `K.check`; baked shading hero / parts | clean; 0.02 / ≤ 0.06 | **clean**; 0.03 / ≤ 0.14 | < 0.5 |
| UV overlaps / flipped, min gap | 0 / 0, 0.016 | 0 / 0, 0.016 | |
| Min corner | 2.01° (trunk seams) | 2.01° (trunk seams) | minor 5 (accepted) |

Hero shells: trunk 1 (960 tris), limbs 5 (410), cut stub 1 (46), twigs 14 (168), lobes 53 (1014), leaves 48 (480),
hubs and the bush heart 11 (96), rocks and pebbles 10 (320), patch 1 (96). Origins at the bottom centre (hero offset
0.327, −0.293, 0). §1.5 still holds: 20 tall, W : H 0.95–1.0, T 40.6 % in the f34 (042 12.8, 045 10.8), a massive
planked leaning trunk, five plug-in limbs with twigs, five separate domed pads with sky between, seven buttress roots,
hollow stubs and a knot, a brown limb star from above (top T 16 %).

### Left over (for the verifier)

- **UR and R runs** are 3.9 and 4.1 from socket face to fork (plan 5.1 / 4.3); from the bark they are about 4.9 and 5.0
  (the stubs protrude 0.95 / 0.85). Longer runs would push the UR pad down into the R pad, or the R socket into the
  roots.
- **Twigs in the f34:** L and R show one twig each at (+25, 10); their pads' near lobes hang in front of the other two.
  All three show in the front, rear, underside and `foliage_cu`.
- **Front and rear bark share** is 43.9 / 46.9 % (sheet 37.8 / 39.6), from the visible limbs and the massive trunk.
  The binding f34 is in tolerance (T +3.0). The pads are a little smaller than the sheet's (fewer, larger lobes, as
  ruled).
- **f34 lit canopy** `#A2C93A` is 14 levels off `#B0C431` in R (G and B within 9): the two-sided studio light.
- **Top view** W : D 1.356 (target ≤ 1.35); the rosettes touch at their rims.
- **RootBase** is 992 / 1000 tris, so there is no headroom for more leaves.
- Unchanged from round 1 (outside this round's scope): the trunk's sub-3° union seam corners, the knot's slot shape,
  the rocks' slight yellow, the patch depth 16 (plan 14), and no S-curve in the trunk.

## Verification round 2 (verifier, 2026-10-29)

Fresh verifier, read-only on port 9880 (`wip/M047_verify.blend`, holding the fix-round model plus M042 and M045). I
built, edited and saved nothing. Every number below comes from my own bmesh / BVH / ray-parity code and my own renders
(800 × 700, long lens, floor hidden for `*_sheet`), not from `shells_report`, `plug_report` or `limb_visibility`.
Scratch: `m047_verify2/` in the session scratchpad. It holds `cmp_<view>.png` (sheet | ours), `cmp_conifers.png`
(042 | 045 | 047), `m_foliage.png`, `m_base.png` and `m_join.png` (sheet close-up | ours), `m_parts.png`, and the
scripts `audit.py`, `contact.py`, `buried.py`, `skel.py` and `col.py`.

### Measured

| Object | Tris | Size (studs) | Shells | Non-man. / bound. / wire / loose | Bowtie | Winding | Zero-area / n-gon | Self-hits | Min corner (< 3°) | Origin, transforms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GnarledPine | **3590** / 3800 | 20.93 × 15.99 × 20.00 | 144 | 0 / 0 / 0 / 0 | 0 | **0** | 0 / 0 | 0 | 2.01° (43) | bottom centre, rot 0, scale 1 |
| GnarledPineForkedTrunk | 960 | 14.01 × 12.47 × 13.73 | 1 | 0 | 0 | 0 | 0 | 0 | 2.01° (43) | ok |
| GnarledPineCrownCanopy | 410 | 8.69 × 8.24 × 7.09 | 18 | 0 | 0 | 0 | 0 | 0 | 8.6° | ok |
| GnarledPineCanopyTier | 280 | 5.90 × 6.23 × 6.94 | 12 | 0 | 0 | 0 | 0 | 0 | 10.5° | ok |
| GnarledPineBranchAngled | 328 | 9.36 × 7.21 × 8.80 | 15 | 0 | 0 | 0 | 0 | 0 | 8.5° | ok |
| GnarledPineRootBase | 992 | 17.81 × 15.99 × 3.27 | 70 | 0 | 0 | 0 | 0 | 0 | 4.4° | ok |

- Every shell of every object has positive volume, so the normals point outward. No object has modifiers, custom
  normals, children or sockets. Each has a UVMap. `K.check` finds no problems on all six. No material is emissive.
- **Hero shells:** trunk 1, limbs 5, cut stub 1, twigs 14, lobes 53, plant leaves and hubs 58, bush heart 1, rocks and
  pebbles 10, patch 1.
- **Floating:** 0 shells more than 0.03 from everything, and 0 unchained, in all six objects.
- **Plugs:** every limb's nearest corner is 0.015 from its socket, with 12 corners within 0.03. No plug corner is
  inside the trunk solid. Two shoulder corners of the crown limb sit 0.165 inside the leader-top rim, under the
  sleeve, as in round 1.
- **Buried (ray parity in two directions, checked again by the nearest-face normal sign and by
  `m044._rock_depth`):** this fails. See blocker 1.

| Shell (hero local) | Into | Verts inside | Depth |
| --- | --- | --- | --- |
| T2b hub (4.97, −2.61, 0.18) | root | **6 / 6 (the whole hub)** | 0.38 |
| T2a / T2b leaves (5.37, −2.36), (4.78, −2.04), (4.52, −2.80), (5.40, −3.42) | roots RT1 / RT2 | 3–5 / 7 | 0.22 / **0.80** / 0.40 / 0.37 |
| B1 bush leaves (−2.52, −2.91), (−0.46, −4.39), (−0.92, −4.22), (−3.19, −3.53) | trunk foot / roots RT3–RT4 | 1–3 / 7 | **0.88** / **0.77** / 0.56 / 0.035 |
| B1 leaves (−4.27, −4.74), (−3.54, −4.99), (−2.52, −6.30) | rock RK1 | 1–3 / 7 | 0.32 / 0.15 / 0.14 |
| B1 heart dome | rock RK1 | 2 / 10 | 0.10 |
| S4 sprig leaf (1.81, 6.03) | rock RK5 | 2 / 7 | 0.10 |
| Rocks RK3 (6.11, −5.14), RK6 (−2.92, 5.52) | roots | 2–3 / 22 | 0.23 / 0.14 |

- **Lobes (53, in pads of 13 / 9 / 10 / 11 / 10 by `PADS`):** within the ruling's 14 / 9 / 11 / 12 / 11.
  - Height : width per pad: medians C 0.63, UL 0.58, UR 0.60, L 0.62, R 0.62. The range is 0.529–0.656: one UR lobe
    is 0.02 under 0.55, and two lobes are a hair over 0.65.
  - Every non-core lobe cuts 0.07–1.26 into its pad's core, typically 0.6–1.0.
  - One C ring lobe, at local (−1.62, 4.41, 16.07), is entirely inside the UL and C lobes: 18 tris that never show.
- **Tone ordered by height within each pad.** Lobe luminance against mid height correlates at 0.91 / 0.96 / 0.98 /
  0.98 / 0.98 (C / UL / UR / L / R), from the deepest at the bottom to the lime top lobe. Each lobe is a single
  material. Pad luminance is C 139, UR 133, R 130, L 128, UL 121, so C is the lightest.
- **No colour by facing.** Across all leaf faces, luminance against normal.z correlates at −0.01; across the bark,
  0.05 (normal.z) and 0.00 (normal.x). Every `normal` in `m047.py` is geometric: lobe tilt, the bush's leaf frames
  and recalculation. No paint is selected by normals.
- **Skeleton** (my own: limb faces that face the camera and are unoccluded per ray cast, binned at 0.2 along the limb
  axis). Twigs count as seen when at least half their camera-facing faces are unoccluded.

| View | Visible limb C / UL / UR / L / R (studs) | Twigs seen C / UL / UR / L / R |
| --- | --- | --- |
| front (0, 6) | 2.4 / 3.2 / 4.0 / 3.4 / 4.0 | 0/3 / 2/2 / 2/3 / 1/3 / 2/3 |
| rear (180, 6) | 2.8 / 3.2 / 4.4 / 3.8 / 4.0 | 0/3 / 2/2 / 2/3 / 2/3 / 2/3 |
| f34 (25, 10) | 3.6 / 3.4 / 4.2 / 3.8 / 4.0 | 0/3 / 2/2 / 2/3 / 0/3 / 0/3 |
| r34 (205, 11) | 3.2 / 3.4 / 4.2 / 3.8 / 3.2 | 0/3 / 1/2 / 1/3 / 0/3 / 1/3 |

  - Limb lengths, plug to fork: C 3.65, UL 3.69, UR 4.59, L 4.11, R 4.76.
  - Last-segment rises from `LIMBS`: UR 46°, L 35°, R 33°.
  - In the `underside` render, all three twigs show under L and under R.

**Views** (study masks, `measure_render.py` and `col.py`; ours / sheet):

| View | W : H | G | T | S | R |
| --- | --- | --- | --- | --- | --- |
| f34_sheet (+25, 10) | 0.974 / 0.949 | **47.5 / 48.2** | **41.0 / 37.6 (+3.4, in ±4)** | 3.9 / 3.4 | 6.6 / 9.3 |
| front_sheet (0, 6) | 1.003 / 1.005 | 45.5 / 49.1 | 44.5 / 37.8 | 3.3 / 1.6 | 6.4 / 9.7 |
| rear_sheet (180, 6) | 0.987 / 1.010 | 41.9 / 48.6 | 47.4 / 39.6 | 1.4 / 2.0 | 7.8 / 8.1 |
| r34_sheet (205, 11) | 1.000 / 0.952 | 41.3 / 46.6 | 45.7 / 40.8 | 2.3 / 3.3 | 7.9 / 7.7 |
| side_sheet (90, 6) | 0.750 (0.72–0.9) | 46.6 | 42.2 | 1.8 | 7.7 |
| top_sheet | W : D 1.354 / 1.138 | 75.5 / 76.9 | 16.2 / 9.2 | | |
| 042 TieredFir (+25, 10) | 0.653 | 72.5 | 11.9 | | |
| 045 PineSapling (+25, 10) | 0.734 | 76.4 | 10.7 | | |

**Colour** (f34, the same masks on both; ours / sheet):

| Region | Ours | Sheet | Verdict |
| --- | --- | --- | --- |
| Canopy median | `#5B8D30` | `#51822F` | within 15 |
| Canopy v > .7 | `#A1CB3D` | `#AFC431` | R −14, B +12: just outside ±12 |
| Canopy lime / green / dark (%) | 31 / 66 / 3 | 31 / 30 / 39 | the sheet's dark share is its light (§3.9) |
| Trunk median | `#8A4E27` (24°, .72) | `#8B4E2A` (22°, .70) | match |
| Trunk v > .7 | `#C46E37` | `#DB843B` | 23 levels low; studio light |
| Rock v > .7 | `#D4C6B2` (35°, .16) | `#DDCDB6` (35°, .18) | within 10; R > G > B, no longer yellow |
| Sand | `#E3C699` | `#E2C698` | match |
| Plants v > .7 | `#C2C42B` | `#AABD26` | **R +24: too yellow** |
| Plants dark share | 23 % | 34 % | ≥ 20 |

- **Front:** canopy `#5F8E31` against `#4B802F`; rock lit `#D4C5B1` against `#DBCCB4`.
- **Rear:** canopy `#538331` against `#50842F`.
- **Hues:** bark keys 26°, R > G > B. Hollows `bark_deep` `#341807`, a geometric region in every hole.

### Findings

**Round-1 blockers, re-judged:**
- **Skeleton reads (blocker 1 of round 1, resolved).**
  - Each limb now shows 2.4–4.4 studs of bare bark between the trunk and its pad in the front, rear, f34 and r34.
    That meets the 1.5–2.5+ target.
  - Each limb leaves its socket along the axis, bends at an elbow, and rises 33–46°.
  - Twigs show under UL, UR and R in the front and rear, and under all pads from below.
  - `cu_foliage_L` matches close-up 3: a limb rising into three twigs under a flat dark underside.
- **Pads read as single domed clouds (blocker 2 of round 1, resolved).**
  - Each pad is one dome: a flat underside, a scalloped ring, an upper ring and a broad lime top lobe.
  - From above each pad is a rosette (`cmp_top_sheet`). Lobes are flattened and heavily overlapped, and tone follows
    height.
  - They no longer read as bunches of balls.
- **Minors 3 and 4 of round 1, fixed.**
  - The bush B1 is a rounded dark dome of broad leaves, and the tufts are broad round-tipped leaves.
  - The crown cut stub shows a dark pit in a light rim facing the f34 and front cameras (`m_join`, panel 3).

**§1.5 (binding): passes.**
- Beside 042 and 045 (`cmp_conifers.png`) this is unmistakably a different tree:
  - W : H 0.97 against 0.65 / 0.73, and T 41 % against 12 / 11 %;
  - a massive planked leaning trunk with five plug-in limbs and five separate pads with sky between;
  - seven buttress roots, hex sockets, hollow stubs, a knot, and a brown limb star from above (top T 16 %).
- It is nothing like W04's slender fluted `OldPine`.
- The f34 shares are in tolerance: G −0.7 and T +3.4 against ±4.

1. **Blocker: buried dressing (STAGES "No floating dressing", spec §2.4 "cut ≤ 0.05").** This is new in the fix
   round's plant rebuild. The fix log says skirt leaves "climb the dome if they would cut ... a root"; they don't.
   - **T2b's whole hub is inside a root**, 0.38 deep: the tuft grows out of the root.
   - Eight leaves cut 0.22–0.88 into the trunk foot and roots RT1 / RT2 / RT3 / RT4: four from B1 and four from T2a
     and T2b.
   - Three B1 leaves cut 0.14–0.32 into RK1, the B1 heart 0.10 into RK1, and an S4 leaf 0.10 into RK5.
   - It is visible in `m_base.png`: the bush is pushed into the root flare, and T2's leaves pass through the root.
   - Cause, from the builder:
     - `clump()` retries a guarded leaf once, then keeps it even if it still cuts.
     - `bush()` gives up after a 36° climb.
     - Hubs are never guarded.
     - Rocks are never in the guard.
   - **Fix target (round 3, this item only):**
     - Move T2b clear of RT1 / RT2: its hub must be at least 0.3 outside the root surface, for example
       about 1.0 further out along its own azimuth. Or drop T2b; RootBase is at 992 tris.
     - Move B1 about 0.8 out from the foot, away from RT3 / RT4 and RK1, or shrink its inner skirt.
     - Make the guard reject: drop any leaf that still cuts more than 0.05 after its retries, rather than keeping it.
     - Include the rocks in the guard BVH.
     - Re-measure every plant shell by ray parity against the hero's trunk and rock shells after the final
       placement: 0 more than 0.05 inside.
2. **Minor: twigs under L, R and C.** By my strict count, the f34 shows none under L or R. The front shows one under
   L. C's three twigs are hidden in every side view behind the leader top and the crown limb. They all show from
   below. **Target, if touched:** turn one L twig and one R twig toward +X / −Y so they clear the near ring lobes.
3. **Minor: front, rear and r34 bark** are T 44.5 / 47.4 / 45.7 against 37.8 / 39.6 / 40.8, which is +6.7, +7.8 and
   +4.9. The trunk is a heavy, almost straight column, and the pads are smaller relative to it than on the sheet. The
   binding f34 is in tolerance. Accept as a leftover.
4. **Minor: colour leftovers.** All three are accepted.
   - The lit canopy is `#A1CB3D` against `#AFC431` (R −14), and the lit trunk is 23 levels low. Both come from the
     two-sided studio light.
   - **The plants are too yellow:** v > .7 `#C2C42B` against `#AABD26`. The tufts read olive-yellow beside the sheet's
     fresh green. Target: `m047_plant` hue about 70° rather than 64°.
5. **Minor: top view.** W : D is 1.354, 0.004 over the 1.35 limit. The rosettes touch at their rims, where the sheet
   shows four with gaps. The limb star shows (T 16 %). Accept.
6. **Minor: UR and R runs** are 4.6 / 4.8 plug to fork, with 4.0–4.4 visible. That is short of the plan's 5.1 from the
   socket face, but it reads. Accept.
7. **Minor: wasted geometry.** One C ring lobe, at hero local (−1.62, 4.41, 16.07), is fully enclosed by the UL and C
   lobes: 18 tris that never show. Remove it or move it outward if the builder is touched.
8. **Minor: rocks RK3 and RK6 cut 0.23 and 0.14 into roots.** They read as nestled. Pull them out 0.2 if round 3
   touches the base.
9. **Minor: the BranchAngled part.** From the sheet's exploded angle (0, 20) the pad hides the limb. The limb is about
   0.45 of the pad's width; the exploded shows about 1.0, with a visible elbow. It reads correctly from the modeller's
   (33, 6) shot. Accept.
10. **Minor, unchanged from round 1 (all accepted):**
    - the knot reads as a rectangular slot;
    - the trunk is a near-straight column with no S-curve;
    - the roots read as a flared skirt rather than the sheet's long separate prisms (`m_base`, close-up 2);
    - the patch is 16 deep;
    - 43 trunk-seam corners are under 3°.

**Decisions:**
- Followed:
  - **1** (20.0 tall, canopy 20.93 within 20.3 ± 0.8);
  - **2**;
  - **3** (13 / 9 / 10 / 11 / 10 lobes within the ruling, no booleans, no floating lobes, twigs or plugs);
  - **4** (plugs seated at 0.015);
  - **5**;
  - **6** (deviation accepted by the ruling);
  - **7**;
  - **8**;
  - **10**;
  - **11** (calibrated keys, C the lightest, role and height colour, no facing, no lime cap on every lobe, geometric
    hollows, warm-grey rock, sand);
  - **12** (no emission, no sockets);
  - **13** (hero precise);
  - **14** (3590 / 3800, parts < 1000).
- **9 is not met.** The counts are right (6 rocks, 4 pebbles, 1 bush, tufts T1 / T2a / T2b / T3 / T4 / T5, and 4
  sprigs), but "all seated" fails because T2b and several leaves are buried (blocker 1).

**Score: 7.5 / 10.**
- The mesh, winding, budget and contact chain are clean.
- Both round-1 blockers are fixed, so the skeleton and the cloud pads now read like the sheet.
- §1.5 and the f34 shares pass, and the colour is in family and never by facing.
- One new placement fault remains: plants buried in the roots and rocks.

**Verdict: FAIL.** There is one narrow blocker, buried dressing (item 1). STAGES allows a targeted third round that
fixes only that blocker. Re-measure with ray parity against the hero's trunk and rocks, then commit with items 2–10
noted as leftovers. Nothing else needs another modelling pass.

## Fix round 2 (targeted, fix modeller, 2026-10-29)

Scope: verification round 2's one blocker, buried ground dressing. Nothing else about the model was changed: the
skeleton, pads, lobes, trunk, limbs, colours and every other placement are as in round 2. Builder
`art/blender/kit/mcp/m047.py` edited; port 9880 on `wip/M047.blend` (saved). The final numbers come from a freshly
restarted session (`kit_mcp.install(); m047.build()`), which also rewrote the renders in this folder. Scratch:
`m047fix2/` in the session scratchpad (`final_build.json`, `final_full.json`, `second.py`, `buried_v2.json`, `b_*.png`).
No commits, pushes or exports.

### Changes

1. **Placement guard (`_Solids`, `_trunk_guard`).** It is now the built trunk part (body and the seven roots) plus
   every rock and pebble, added one by one as `root_base_part` builds them. Depth is tested by **ray parity**
   (m046's three skewed rays, two of three must agree) over every vert and face centre, measured as the distance to
   that shell's surface. The old guard was the trunk's BVH only, tested by the nearest face's normal sign.
   Placement accepts a piece at ≤ `BURY_PLACE` 0.03, leaving a margin under the 0.05 limit (`BURY`).
2. **Tufts and sprigs (`clump`).** A guarded leaf now has seven tries: as built, then stood up 16° at 0.9 size,
   then turned ±0.35 rad, then turned ±0.7 rad at 0.85, then stood at 80° at 0.75. If it still cuts, it is
   **dropped**, never kept. The tries draw no rng, so leaves that were clear stay exactly as they were. The hub's
   depth is recorded (`BASE_INFO`).
3. **Bush (`bush`).** The heart dome is guarded too: it narrows (rx × 0.93 per step) until it clears, ending at rx
   1.17 instead of 1.8. Each leaf tries, in order:
   - shortening (× 0.85, × 0.72);
   - climbing the dome 6° at a time, up to 36°;
   - turning ±0.3 rad at 0.85, then ±0.6 rad at 0.75;
   - 0.65 length;
   - as a last resort, moving ±0.9 or ±1.2 rad round the dome onto the bush's free front.

   A leaf that clears none of these is dropped. In the final build none was dropped: all 10 leaves stay (7
   re-seated), so the bush keeps its leaf count, its dark share and its dome outline.
4. **Placements (`CLUMPS`, `ROCKS`).**
   - **T2b** moved from (5.3, −2.9), which was on top of RT1, to **(7.2, −3.0)**: between RT1 and the T2a tuft, its hub
     0.34 clear of the root surface.
   - **B1** moved from (−1.9, −5.0) to **(−1.0, −5.9)**, 1.3 out of the notch between RT3, RT4 and RK1. The pocket
     there is only about 1 stud wide at heart height, so no position within 0.8 cleared a 1.8 heart. B1 still sits
     between RK1 and RT3, with its back leaves touching the root (spec §2.4).
   - **RK3** moved 0.3 to (6.4, −5.7), off RT1's tip, and **RK6** 0.4 to (−2.6, 5.6), off RT6's tip.
   - The patch outline lets itself out for T2b, so RootBase is now 18.21 wide (was 17.81). The hero is unchanged.
5. **`bury_report(o)` in `build()`.** It runs on the hero and on RootBase. Every plant shell (leaf, hub, bush heart)
   is tested by ray parity against the trunk shell and each rock and pebble shell; RootBase, which has no trunk
   shell, is tested against the trunk part brought into its frame. Each rock is also tested against the trunk. Any
   plant shell, or any rock, more than 0.05 in is a `problem`. `build()` returns `bury` and `base_info`.

### Before → after

| Measure | Round 2 | Fix round 2 | Target |
| --- | --- | --- | --- |
| Plant shells > 0.05 inside trunk / roots / rocks: builder parity (verts + face centres) | 13, max 0.88 | **0, max 0.027** | 0 |
| … second method: angle-weighted pseudo-normal sign (own code, `second.py`) | | **0, max 0.027** | 0 |
| … third: verifier round 2's `buried.py` (two-ray parity, verts) | fail (its table above), max 0.88 | **0 plants > 0.05** (max 0.027; the only other row is the crown limb plug shoulder, 0.165, unchanged) | 0 |
| T2b hub | whole hub 0.38 inside RT1 | **0.34 clear** of the root surface | ≥ 0.3 clear |
| B1 heart | 0.10 into RK1 (verifier); 0.59 by face centres | 0.027 (rx 1.17) | ≤ 0.05 |
| B1 leaves cutting trunk foot / RT3–RT4 / RK1 | 7 (0.14–0.88) | **0** (10 leaves kept, 7 re-seated) | 0 |
| T2a / T2b leaves cutting RT1 / RT2 | 4 (0.22–0.80) | **0** (one T2a leaf re-seated) | 0 |
| S4 sprig leaf in RK5 | 0.10 | 0 (stood up) | 0 |
| Rocks into roots: RK3 / RK6 | 0.23 / 0.14 (verifier); 0.28 / 0.26 by face centres | **0.005 / 0** | ≤ 0.05 |
| Floating / unchained (all six objects) | 0 / 0 | **0 / 0** | 0 |
| Non-manifold / boundary / winding / self-hits; `K.check` | 0; clean | **0; clean** | 0 |
| Hero tris; RootBase | 3590; 992 | **3590; 992** | ≤ 3800; < 1000 |
| Hero size | 20.93 × 15.99 × 20.00 | 20.93 × 15.99 × 20.00 | |
| Plugs: corner gap, inside solid | 0.015–0.053, 0 | 0.015–0.053, 0 | seated |
| Lobes (C / UL / UR / L / R), h : w median (min–max) | 53 (13/9/10/11/10), 0.607 (0.529–0.656) | unchanged | |
| f34 G / T (`measure_render.py`) | 47.5 / 41.0 | **47.1 / 40.3** | 48.2 ± 4 / 37.6 ± 4 |
| front / rear / r34 G / T | 45.5/44.5, 41.9/47.4, 41.3/45.7 | 45.8/43.0, 42.4/46.3, 41.6/44.9 | (minor 3, leftover) |
| side W : H; top W : D | 0.750; 1.354 | 0.750; 1.356 | |
| f34 plants v > .7, dark share (`col47.py`, same tool on both renders) | `#BEC02A`, 22 % | `#BFC12B`, 20 % | dark ≥ 20 % |

`base_cu.png` and the scratch close-ups (`b_bush.png`, `b_bushF.png`, `b_t2.png`) show the change:
- B1 is a dark leafy dome standing on the sand between RK1 and RT3, no longer pushed into the root flare.
- The T2a / T2b pair grows beside RT1, not through it.
- RK3 and RK6 sit beside their roots' tips.

### Left over (unchanged, outside this round)

Verifier round 2's minors 2–10 stand as written, including:
- the C ring lobe enclosed by the UL and C lobes;
- the plants' yellow lean;
- twigs under L and R in the f34;
- the front, rear and r34 bark share.

One new note: B1 now sits about 1.3 from its round-2 spot (the verifier suggested about 0.8) and its hidden heart
is narrower (rx 1.17). The leaves keep the outline a dome.

## Main session ruling (2026-10-29)
- **Committed** after a targeted round 3 that fixed only the round-2 blocker.
- **Rounds:**

  | Round | Score | Outcome |
  |---|---|---|
  | 1 | 6.5 | Failed: the skeleton didn't read and the pads looked like balls |
  | 2 | 7.5 | Failed: the plant rebuild buried 13 plant shells in the roots and rocks |
  | 3 | — | The buried-plant blocker is fixed |

- **Round-3 check:** the main session's GUI rebuild found 0 of 59 plant shells more than 0.05 in (max 0.027). The fix modeller's two methods and the round-2 verifier's own script agree.
- **Left for a later polish pass** (from verification round 2):
  - no twigs show under L and R in the f34;
  - bark share is high in the front, rear and r34;
  - the plants lean yellow (aim around 70° hue);
  - the lit canopy and trunk read low, from the studio light;
  - the top W:D is 1.354;
  - one crown lobe is enclosed;
  - the knot is a slot;
  - the trunk is a straight column;
  - the patch is 16 deep.
- **Export:** 6 assets, 6 solid pieces, 6560 tris, 0 VFX sockets, palette 23 colours, 0 problems.
