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
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m047_study\`.
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
