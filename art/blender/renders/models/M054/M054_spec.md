# 054 Broadleaf Tree — spec

Reference: `art/blender/assets/references/054.png` (1024 × 1536 px). INDEX.md row 54: "Flintborn broadleaf tree study".
The sheet's own header reads **"53 / 132  FLINTBORN — INDIVIDUAL MODEL STUDY"**, title **"BROADLEAF TREE"**, footer
"PAGE 53 / 132" (our number is INDEX's 054, §3.1).
Builder: `art/blender/kit/mcp/m054.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows no effect** (§7). Trees (memory
`kit-tree-detail`): "take the dead tree and add leaves to it"; "pay more attention to the details: the branches, the
different views"; roots "snaking out over the ground". **This model is 053's kind of skeleton (twisted rope-strand trunk,
plug-in branch modules, split-toed roots) with five rounded leaf clumps hung on the branch tips.** The limbs must still
read between and under the clumps in every view (047 round 1 failed on stub limbs and hidden twigs).

Sheet text (paraphrased):
- **Description (top left):** a stylised deciduous tree with a thick twisting trunk and rounded leaf clumps; a chunky,
  readable silhouette built from simple, reusable modules.
- **"MATERIAL PALETTE"** (top left, six labelled swatches): LEAF DARK, LEAF MID, LEAF LIGHT, BARK MID, BARK LIGHT, ROCK.
- **Assembled views:** a front three-quarter (unlabelled, top centre) and **"REAR THREE QUARTER (ASSEMBLED)"**.
- **"ORTHOGRAPHIC VIEWS (CONSISTENT MODEL)":** "FRONT VIEW", "SIDE VIEW", "REAR VIEW", "TOP VIEW". Front, side and rear
  are near copies of one drawing (§3.3).
- **"EXPLODED CONSTRUCTION (PARTS & ASSEMBLY)":** labels "Leaf Clump (Module)", "Branch Module", "Trunk Core", "Root
  Base". Drawn: five leaf clumps (three with a short stub under them), four branch modules, the trunk core (hollow socket
  top, socket bosses and root stubs round its flared foot), three long root modules and two short root pieces, six rocks,
  eight grass tufts; dashed arrows from every module to its socket.
- **"PART CONNECTION DETAIL":** "Branch Module plugs into Trunk Core with simple peg joint." / "Faceted surfaces with
  clean, flat shading."
- **"UNDERSIDE VIEW (TRUNK JUNCTION)":** "Underside shows root module layout and joining surfaces."
- **"LEAF CLUMP CROSS-SECTION":** "Leaf cards as simple chunky geometry." / "Solid branch core." / "Layered, overlapping
  leaf shapes for volume."
- **"MODELING NOTES":** built from reusable modules (trunk core, branch modules, leaf clumps, root base, rocks and
  foliage); chunky forms with broad flat-shaded faces; simple clean geometry with clear pivot / joint points; keep the
  silhouette, proportions and palette; no micro detail, noise or texture maps — a clean, stylised, game-ready look (§3.9).
- **Game context and the old kit:**
  - **W05 row 1 `OakTree`** (`art/blender/scripts/kit/W05/oak_tree.py`, goals `art/blender/renders/kit/W05/oak_tree_goals.md`)
    is the old kit's take on the same subject: 23.6 × 22.5, five clumps on a twisting trunk, parts `OakLeafClump`,
    `OakBranchModule`, `OakTrunkCore`, `OakRootBase`. `MODEL_PROGRESS.md` row 62: "flat blob crown (ref 5 clumps on
    twisting limbs); thin straight trunk; too pale". **W05 owns every `OakTree*` / `Oak*` part name**; the old lobby owns
    `BroadleafTree*` (§8).
  - **Sister sheets:** 047 Old Pine (`GnarledPine`, 20 tall, committed: limbs + domed pads), 053 Dead Tree
    (`TwistedSnag`, 18 tall, in progress: the skeleton pattern), 057 Ancient Tree next (must be the biggest). §1.5 keeps
    054 apart.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Paper `#FCF8EE` (252, 248, 238),
tolerance 12. Measured grey rules: header y 40–41; ortho frame y 501 / 798–799, x 14 / 1009 (no inner dividers);
lower frames y 806–807 / 1339–1340 / 1485, x 574–575 (exploded | right column) and x 586; right column splits y 1009–1010
and 1209–1210.
- **Cells** (`m.V`, `m.X`): f34 (185,95,620,495); r34 (615,95,1009,495); front (16,531,262,770); side (266,531,510,770);
  rear (514,531,758,770); top (762,531,1007,770); exploded (16,830,574,1339); cu1 "part connection" (586,830,1009,1006);
  cu2 "underside" (586,1035,1009,1206); cu3 "leaf clump cross-section" (586,1235,1009,1483).
- **Blanked text:** f34 description (185,95,325,138) + (185,138,300,158); r34 label (615,95,735,160); exploded labels.
- **Swatches** (squares 41 × 39 at x 29–69): LEAF DARK y 217–255, LEAF MID 262–300, LEAF LIGHT 306–344, BARK MID 351–389,
  BARK LIGHT 395–433, ROCK 440–477 (medians of the inner box, sd ≤ 1.5).
- **Masks** are `cls()` in `m.py` (HSV, h in degrees, assigned in this order): **X** cast shadow (s < 0.07, v ≥ 0.80, or
  s < 0.10, v ≥ 0.72, B ≥ R − 2, or h 200–250, s < 0.15, v ≥ 0.70: the lavender ground shadow left of every view);
  **G** green (h 50–180, s ≥ 0.30, v ≥ 0.12: leaves, grass, moss); **T** wood (h < 50, s ≥ 0.30, v ≥ 0.12); **R** rock
  (s < 0.30, v 0.22–0.95); **O** other (outlines, holes, darkest creases). Canopy = G above h 0.28; ground green = G
  below h 0.20.

**Scratch study material** (no Blender) in
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m054_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe`.
- **Helpers:** `m.py` (masks, boxes, `silhouette()`), `zoom.py` (`zoom.py x0 y0 x1 y1 scale out.png [grid]`),
  `comps_053.py` (`label()`), `woodmap.py` (wood-only map: T kept, leaves pale; `woodmap.py front 4 x0 y0 x1 y1`),
  `tonemap.py` (leaf tone classes light / mid / dark).
- **Measurements:** `measure.py` (bbox, W : H, shares, fill, profiles, fifths), `measure2.py` (trunk run per height,
  canopy top / bottom per column, canopy vs ground green, wood above h .45), `samp.py` / `samp2.py` (colour per region,
  tone bands, moss vs blades, holes, cut faces), `sw.py` (swatches), `comps.py` (rock and plant blobs), `expl.py`
  (exploded and close-up blobs), `scallops.py` (leaf-lobe peaks round the crown outline; point it at our renders too),
  `lines.py` (rules).
- **Zooms:** `z_f34.png`, `z_r34.png`, `z_f34crown.png`, `z_r34crown.png`, `z_f34base.png`, `z_front.png`,
  `z_side.png`, `z_rear.png`, `z_top.png`, `z_frontcrown.png`, `z_sidecrown.png`, `z_ortho.png`, `z_expl.png`,
  `z_explL.png`, `z_explR.png`, `z_explB.png`, `z_cu.png`, `z_cu1.png`, `z_cu2.png`; wood maps `w_front.png`,
  `w_f34.png`, `w_frontbase.png`, `w_rearbase.png`; tone maps `t_front.png`, `t_top.png`; masks `cls_*.png`,
  `cls_mont.png`.
- **On our renders:** copy 047's `measure_render.py` and point it at this folder's `m.py` (paper `#FCF8EE`).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a standalone tree with its own base dressing (no ground patch, §3.8). Hero budget 4000
  tris, each part under 1000. The plan in §4.3 lands at about 3500–3750.
- **Overall read (check this first).** A **big round-crowned deciduous tree**: a **massive, twisted, orange-brown trunk**
  of faceted rope strands (waist Ø ≈ 0.235 H) **flaring into six thick roots** that arch down onto the ground and end in
  split, blunt toes; at about half height the trunk **throws out two thick low limbs** (left and right, nearly level) and
  **continues as a short upper trunk that splits into a V leader**; **five rounded leaf clumps** sit on the limb tips —
  two low side clumps (left, right), two upper clumps in front (front-left, front-right) and the biggest, highest clump
  at the back centre — each a **mound of chunky lobed leaf cards** with a lime-yellow lit top, mid-green body and dark
  green underside; **bare limb runs and forks show between and under the clumps**; a **dark oval knot hole with a pale
  rim** on the trunk front at the crotch; small dark bark pits; round the foot **pale grey faceted rocks**, **tall
  pointed lime grass tufts** and **flat lime moss** between the roots.
  - It reads **green over wood**: in every side view the canopy is 47–48 % of the silhouette, ground green 5–9 %, wood
    33–38 % (of which 10–12 points are the limbs and upper trunk above h .45), rock 5–8 %.
  - The crown is **as wide as the tree is tall** (front W : H 1.009, rear 0.978), its bottom at h .39–.43 on both sides,
    round in plan (top W : D 1.03): **five clumps in a ring round a visible limb hub** seen from above.
- **Focal silhouettes, in order:**
  1. The crown's outline: a scalloped dome — top peak (back clump) at h 1.0, shoulders (front pair) at h .92–.94, side
     clumps falling to h .57–.69 at the rims and hanging to h .39–.41 underneath.
  2. The trunk's mass and twist: a wide root flare (Ø 9.6 at z 4 with the root shoulders), a waist at h .35 (z 7), the
     crotch at h .45–.50 where the two low limbs leave.
  3. The skeleton under the crown: the two low limbs running out under the side clumps to bare forked tips; the V leader
     and short limbs visible in the gaps between the upper clumps.
  4. Roots splaying to the ground with split toes; rocks and tall tufts between them.
- **Target size: 20.0 tall (top of the back clump), crown 20.2 wide (X) × about 19.5 deep, trunk waist Ø 4.7 at z 7,
  root reach r 7.2–8.4** (decision §8.1). Tolerances: height ±0.4, crown width 20.2 ± 0.8.
  - **How it was derived.** The front cell's silhouette is 228 × 226 px (H = 226, ground y 764), so **11.3 px / stud at
    H 20**; the f34's 417 × 381 px gives 19.05 px / stud; the top cell is 230 × 224 px at the front cell's scale (20.4 ×
    19.8). Trunk run width per height (`measure2.py`, fraction of H, the T run through the trunk centre):

    | Feature | f34 | r34 | front | side | rear | adopted (studs) |
    | --- | --- | --- | --- | --- | --- | --- |
    | Root shoulders, h .15–.20 | .30–.42 | .22–.24 | .48–.51 | .35–.49 | .38–.44 | 9.6 across at z 4 |
    | Flare top, h .25 | .367 | .306 | .367 | .307 | .327 | 7.3 at z 5 |
    | Trunk, h .30 | .289 | .251 | .288 | .249 | .261 | 5.8 at z 6 |
    | **Waist, h .35** | .268 | .249 | **.235** | .227 | .221 | **Ø 4.7 at z 7** |
    | h .40 | .255 | .377 | .248 | .267 | .265 | 5.0 at z 8 |
    | Crotch with the low limbs, h .45 | .625 | .372 | .593 | .391 | .518 | 7.7–11.9 across the limb bases at z 9–10 |
    | Limb bases, h .50 | .415 | .335 | .385 | .173 | .279 | |
    | Upper trunk, h .55–.60 | .215–.189 | .144–.131 | .150–.128 | .147–.142 | .150–.142 | Ø 3.6–4.0 at z 11–12 (partly hidden by leaves) |
    | V leader arms (front, z 13.6–14.5) | | | 1.3–1.4 studs each | | | Ø 1.4–1.6 |
    | Low limb Ø (front, vertical runs) | | | L: 2.9–3.6 at the knob, 1.2–1.6 mid, 0.4 twig; R: 2.3–2.6 base, 1.2–1.3 mid, 0.5 tip | | | base 2.2–2.4, mid 1.3–1.5, tips 0.5 |

  - **Why 20.** 047 Old Pine is 20 with a 6.2 trunk, 053 Dead Tree 18; a broadleaf at 20 sits with the pine, and 057
    Ancient Tree must be clearly bigger (memory `kit-relative-scale`). At 20 the sheet's proportions give the **lowest
    leaves at z 7.8–8.2** (2.3 above a 5.5 character's head, so players walk under the side clumps), the low limbs at z
    8–10.4 (the limb undersides clear a character by 2.4), a 4.7-stud waist, root shoulders at z 4–5 and rocks 1.2–2.6
    tall. At 18 the side clumps hang to 7.0 (only 1.5 above a head); at 22–24 (W05's 22.5) it rivals the ancient tree.
  - **Against the character (5.5):** the tree is 3.6 C tall; the crown bottom at 1.4–1.5 C; the crotch at 1.7 C; the
    roots reach 1.4–1.5 C out from the axis.
- **Build frame:** front −Y, +X right, ground z 0. Trunk axis at (0, 0), **upright** (the trunk run's centre moves less
  than ±0.03 H up to h .40 in every view). The upper trunk leans 0.8 toward +X above the crotch (front: run centre X
  +0.8 at z 11–13). Origin = bbox bottom centre; the crown runs about −9.8 … +10.4 in X, so the origin sits about +0.3 X
  of the trunk axis (record it).

### 1.2 Measured views (`measure.py`, `measure2.py`)

| View (box) | Silhouette bbox (px) | W : H | G | T | R | O | fill | canopy G | ground G | T above h .45 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (185,95,620,495) | 197–613 × 105–485 (417 × 381) | **1.094** | **57.0 %** | **32.6** | 7.6 | 2.8 | 0.646 | 47.8 | 9.2 | 10.8 |
| Rear three-quarter (615,95,1009,495) | 629–999 × 99–480 (371 × 382) | 0.971 | 53.6 | 38.0 | 5.2 | 3.2 | 0.576 | 46.8 | 6.8 | 12.1 |
| Front (16,531,262,770) | 28–255 × 539–764 (228 × 226) | **1.009** | **53.6** | **37.0** | 6.1 | 3.3 | 0.601 | 46.8 | 6.7 | 10.8 |
| Side (266,531,510,770) | 288–490 × 538–762 (203 × 225) | 0.902 | 54.7 | 37.2 | 4.8 | 3.3 | 0.614 | 49.3 | 5.4 | 10.0 |
| Rear (514,531,758,770) | 527–747 × 538–763 (221 × 226) | 0.978 | 53.5 | 37.8 | 5.5 | 3.2 | 0.590 | 46.9 | 6.6 | 11.9 |
| Top (762,531,1007,770) | 770–999 × 540–763 (230 × 224) | 1.027 (W : D) | 88.4 | 7.7 | 1.6 | 2.4 | 0.659 | | | |

- Shares are of the silhouette (O included, X excluded). **Fill** = silhouette / bbox area (0.58–0.65). **T above h
  .45** = limbs and upper trunk showing through and under the crown: **10–12 % in every side view — the skeleton
  visibility target** (§9.1). T between h .28 and .45 (the bare trunk below the crown) is 8.0–10.1 %.
- **Verifier tolerance:** G ±4, T ±4, R ±3 points; W : H ±0.06; fill ±0.05; T above h .45 ≥ 8; positions ±0.04 H.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.1 W): one dome with a peak and shoulders,
scalloped by leaf lobes.

| f | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .50 | .69 | .78 | .89 | 1.0 | .99 | .93 | .94 | .92 | .82 | .51 |
| r34 | .51 | .69 | .79 | .75 | .91 | .98 | .99 | .93 | .86 | .71 | .55 |
| Front | .54 | .72 | .78 | .88 | .96 | .99 | .91 | .93 | .83 | .70 | .55 |
| Side | .52 | .71 | .74 | .88 | .94 | .99 | .96 | .92 | .92 | .77 | .49 |
| Rear | .55 | .73 | .80 | .89 | .95 | 1.0 | .97 | .93 | .74 | .72 | .57 |

**Width per height** (silhouette width at h .0 → 1.0 as a fraction of W):

```
f34    .26 .87 .75 .42 .88 1.00 .92 .76 .65 .54 .16
r34    .08 .76 .47 .27 .56 .99 .95 .80 .47 .42 .02
front  .08 .82 .68 .30 .71 .98 .92 .81 .56 .44 .03
side   .45 .77 .41 .31 .90 .99 .92 .79 .61 .45 .03
rear   .43 .78 .62 .30 .54 .96 .96 .83 .58 .44 .02
```

- Reading (front): h .1 roots, rocks and tufts across .82 of W; h .2 the flare; **h .3 the bare trunk only (.30 of W:
  keep it)**; h .4 the side clumps' undersides and the low limbs appear (.71); h .5–.6 the crown at its widest (.92–.98);
  h .7–.9 the dome narrowing (.81 / .56 / .44); 1.0 the back clump's peak.

**Canopy outline per column** (front, x from the trunk centre as a fraction of H, every 0.05 from −0.45 to +0.50;
canopy = G above h .28):

```
x      -.45 -.40 -.35 -.30 -.25 -.20 -.15 -.10 -.05  .00  .05  .10  .15  .20  .25  .30  .35  .40  .45  .50
top     .57  .67  .75  .78  .78  .85  .89  .94  .97  .99  .98  .96  .92  .93  .94  .88  .80  .71  .69  .58
bottom  .48  .41  .43  .42  .48  .49  .58  .55  .56  .73  .68  .75  .53  .51  .41  .49  .43  .40  .39  .45
```

- The **bottom row is the clump layout**: side clumps hang to .39–.43 at x ±.25…±.45; the front pair's undersides at
  .51–.58 (x −.15…−.05 and +.15…+.20); a **gap at x .00–.10 where the bottom is .68–.75** — the trunk top and V leader
  show there under the back clump. Rear and side give the same pattern (rear bottoms .40–.55, gap .68–.74; side .36–.40
  at both sides, gap .68–.75).

**Height fifths** (bottom → top, % of each class):
- Front: G 12.2 / 0.5 / 28.9 / 37.4 / 20.9; T 32.5 / 27.0 / 31.5 / 9.0 / 0.0; R 75.9 / 4.5 / 11.0 / 6.5 / 2.1.
- f34: G 13.2 / 3.8 / 28.6 / 32.0 / 22.4; T 26.5 / 30.3 / 31.0 / 11.8 / 0.4.
- Rear: G 12.1 / 0.2 / 27.2 / 39.1 / 21.4; T 32.9 / 26.0 / 32.2 / 8.8 / 0.0. Side: T 34.3 / 26.5 / 28.5 / 10.7 / 0.0.
- **Wood fifth 3 (h .4–.6) holds 28–34 % of all wood**: the crotch, the low limbs and the knot are as heavy as the root
  flare. Wood fifth 4 (h .6–.8) holds 9–12 %: the V leader, upper limbs and twigs inside the crown. A model whose limbs
  hide in the clumps drops fifth 4 under 5 % (047 round 1).

**Scallops** (leaf-lobe peaks round the crown outline: a polar scan from the canopy centre, peaks with ≥ 2 px
prominence over ±3°, counted once per 2°): front 27 on about 700 px
of canopy outline (one per 25 px = **2.2 studs**), top 40 (one per 27 px = 2.4 studs), f34 35. **The visible leaf cards
are about 2–2.5 studs across.**

**Ground dressing blobs** (`comps.py`; x as a fraction of H from the trunk axis, h fraction of H; studs at 20):

| View | Rocks | Plants |
| --- | --- | --- |
| Front | far-left small −.42…−.35 h ≤ .07 (1.3 × 1.3); left −.37…−.24 h ≤ .12 (2.6 × 2.5); front-centre −.07…+.04 h ≤ .11 (2.1 × 2.2); right +.23…+.34 h ≤ .13 (2.1 × 2.7); far-right small +.37…+.42 h ≤ .14 (on a root); pebbles at −.15, +.06…+.12 | tall far-left tuft −.44…−.31 (2.7 wide, top h .20 = 4.1); left tuft −.26…−.18 (top .16); front-centre moss and sprigs −.12…+.16; right group +.19…+.47 (top .15); right tall tuft on the root +.28…+.39 (h .09–.24) |
| Rear (mirrored: rear −x is world +X) | −.38…−.20 h ≤ .11 (3.6 × 2.1); −.15…−.10; −.04…+.03; +.23…+.32 h ≤ .12; small +.37…+.39 | −.36…−.27 (h .08–.20); −.24…−.16; centre −.09…+.05; +.17…+.44; +.23…+.31 (h .14–.24) |
| f34 (19.05 px / stud) | big low front-left (255–323, 427–475) 3.6 × 2.5; far-left (233–277, 434–470); front-centre (369–412, 438–473) 2.3 × 1.8; small (423–438), (442–470); **big right rock (481–547, 400–461) 3.5 × 3.2, the tallest**; right (547–578, 416–442) | tufts: (218–249) far left; (255–297, 376–421) tall left on the root; (299–328) left; centre moss band (305–454) with sprigs; (469–512, 369–453) tall right; (483–594, 424–475) right group; (517–560, 379–429) tall right-back |

**Plan (top cell, `t_top.png`).** Round the limb hub (sheet ≈ (880, 650); sheet up = +Y, back) **five clumps** (studs at
11.3 px / stud):

| Clump | Sheet box | Centre (X, Y) | W × D |
| --- | --- | --- | --- |
| B, back (the biggest) | (842–960, 543–635) | (1.7, 5.5) | 10.4 × 8.1 |
| L, left | (773–872, 585–690) | (−5.2, 1.3) | 8.8 × 9.3 |
| R, right | (925–1000, 600–700) | (7.4, 0.2) | 6.6 × 8.8 |
| FL, front-left | (800–880, 680–760) | (−3.6, −5.8) | 7.1 × 7.1 |
| FR, front-right | (880–975, 665–762) | (4.4, −5.3) | 8.4 × 8.6 |

- Between them the brown **hub** shows (T 7.7 % of the top view): limb arms toward R (az ≈ 10–25°), B (≈ 100°), L / FL
  (≈ 215–255°), and a pale cut end at the hub centre (`#D88832`). Leaf tones from above: light 52 %, mid 35 %, dark 13 %.

### 1.3 Silhouette and composition per view

**Front three-quarter (`z_f34.png`, `z_f34crown.png`, `z_f34base.png`, `w_f34.png`) — governs the read with the front
cell.** Drawn nearly frontal and higher (e ≈ 12–15°: the ground band is h 0–.15 against .09 in the front cell) and
**about 8 % wider** than the front cell on both sides (crown x −.535…+.554 H against −.473…+.522): §3.2. Lit from the
upper right (wood lit `#F2A555`, shade `#4F2E17`); cast shadow to the left.
- **Trunk:** four to six rope strands faceted into long planks, twisting so the lit strands climb **lower-left → upper-
  right ("/")** on the front face; deep dark grooves between strands; waist at y 340 (h .38).
- **Knot** on the trunk front-right at the crotch (440, 300–330): a vertical pair of dark openings in a pale-rimmed
  oval; in the front cell one oval hole (148, 650–665) **0.9 × 1.3 studs in a pale rim 1.4 × 1.8**, a small dark hole above
  (146, 630) and 3–4 dark pits below.
- **Skeleton visible** (`w_f34.png`): the upper trunk rises to y 250 (h .62) and splits — an up-left limb (370→355,
  250→185) into the upper-left clump's underside with a two-twig fork at (340–360, 160–175); the leader continuing up
  (400–420, 250→170) into the top clump; an up-right limb (450, 240) → (500, 195) → fork (525/545, 185/175) into the
  upper-right clump. Low: the **left limb** leaves at (370, 315) as a **thick block with pale lit upper planes**
  (340–395, 295–330), runs left to (240, 320) and ends in a **bare down-left twig fork** (225, 340); an up-left arm
  (330, 300) → (300, 280) into the left clump. The **right limb** leaves at (470, 300) and runs right (520, 310) →
  (580, 325) under the right clump.
- **Clumps:** five; lime-yellow lit tops (upper right of each), mid green bodies, dark green lower-left rims and
  undersides; scalloped by leaf lobes ~2.2 studs apart; small dark gaps between leaf cards.
- **Base:** roots arch from the flare to the ground, toes split; lime moss patches on two root tops (yellow spots at
  (465, 435), front cell (163, 735)); pale grey faceted rocks, the tallest right-back; **tall pointed lime tufts** (blades
  lime at the tips, green inside); a continuous lime moss band on the ground.

**Rear three-quarter (`z_r34.png`, `z_r34crown.png`).** The same tree from behind: the knot shows here as a **hexagonal
pale raised rim round a dark hole** (832, 305); a thick limb block with pale upper planes leaves up-left (785–810,
270–300); low limbs left and right with forks; clumps mirrored.

**Front, side and rear cells (`z_front.png`, `z_side.png`, `z_rear.png`, `t_front.png`).** Low views (e ≈ 4–6°) at one
scale (225–226 px tall). They are **near copies**: the same knot, the same pale limb knob, the same clump layout (two
low side clumps, a top dome of three). §3.3.
- **Front clumps (`t_front.png`, sheet px; studs from the trunk axis):** L (low left) x 30–135, y 588–672 → X −9.4…−0.1,
  z 8.1–15.6, lime upper right; top-left dark mass x 88–125, y 553–600 → X −4.2…−0.9, z 14.5–18.7 (FL's top); top
  centre lime x 115–180, y 540–600 → X −1.9…+3.9, z 14.5–19.8 (B); top right x 165–215, y 553–600 → X +2.6…+7.0, z
  14.5–18.7 (FR); R (low right) x 160–252, y 600–690 → X +2.1…+10.3, z 6.5–14.5.
- **Front skeleton (`w_front.png`, `measure2.py` columns):** upper trunk X −0.4…+2.1 at z 11–13 (w 2.5–3.1 visible),
  splits at z 13.6 into a left lead (X −0.4…+0.8, w 1.3) and a right lead (X +1.6…+2.9 → +3.4…+4.2 at z 14.5);
  left low limb: the **pale knob** X −3.5…−1.4, z 9.2–11.9 (the limb base and its up-left arm), the lower arm X −4.8…−3.7
  Ø 1.2–1.6 at z 8.0–9.5, thinning to a 0.4 twig rising to (−6.9, 10.4); right low limb X +2.6…+3.6 Ø 2.3–2.6 (z
  7.9–10.6), X +4.2…+5.2 Ø 1.2–1.3, X +5.8…+6.8 Ø 0.5 at z 9.0–9.7 (a fork).

**Top (`z_top.png`, `t_top.png`).** Five rosette clumps in a ring round the brown hub (§1.2 plan table), lime centres,
dark rims; limbs radiating between them.

**Part connection (close-up 1, `z_cu1.png`).** The trunk carries a **raised 8-sided boss** (a short socket collar with a
flat face, lit `#EA9948`); the branch module's end is an **8-sided prism with a flat cut face**, a recessed ring and a
**round pale peg** (Ø ≈ 0.4 of the module's Ø, `#D69752`) that enters the boss's socket. Dashed arrows join them.

**Underside (close-up 2, `z_cu2.png`).** Looking up at the trunk foot: an **octagonal hollow** (dark `#44240F`) in a ring of
pale faceted rim planes — the trunk core is a hollow tube at its base — with **six faceted roots radiating** round it;
rocks and tufts between.

**Leaf clump cross-section (close-up 3, `z_cu.png` bottom).** A clump cut open: a **solid branch core** (a stem with a
Y fork and three or four twigs reaching out to the leaves) wrapped in **layered, overlapping lobed leaf cards** (rounded
4–5-lobed leaf shapes, chunky, flat-shaded): lime cards on top and outside, mid and dark green cards underneath and
inside.

### 1.4 Parts (exploded, `z_expl.png`, `z_explL.png`, `z_explR.png`, `z_explB.png`)

The exploded is an elevated front view at about 12.5 px / stud (the top clump is 130 px wide against the hero's 10.4
studs). **The hero governs every size and height** (§3.5); the parts give shapes, counts and joints.

| Part (label) | Box (px) | Notes |
| --- | --- | --- |
| Leaf Clump (Module) ×5 | TL (144–242, 851–937) 99 × 87; TC (266–395, 842–941) 130 × 100; TR (425–531, 861–952) 107 × 92; L (84–189, 935–1026) 106 × 92; R (477–557, 982–1053) 81 × 72 | rounded domes W : H 1.1–1.3 of lobed leaf cards; three carry a **short faceted stub** under them (183–213, 907–929; 311–349, 911–931; 449–480, 913–932) with a flat cut end — the clump's branch core; L and R are drawn on their branch tips |
| Branch Module (labelled) = **BM1** | (129–264, 991–1096) | the **big Y**: a thick 8-sided base with a flat end and a socket (255, 1060) runs left to a knuckle; an **upper arm rises up-left** and bends into the L clump; a **lower arm runs down-left to a bare two-tine fork** (160–180, 1070–1085) |
| BM2 (unlabelled, upper left) | (217–267, 929–1017) | a **short thick upright limb** (cut base with a dark socket hole at the bottom), one kink, a **two-tine fork** at its top (to the TL clump) |
| BM3 (unlabelled, top centre) | (321–425, 925–1004) | a base with a socket (340, 995), a **short upward spur** at the base, the main arm rising up-right to a **two-tine fork** (420, 930–945); dashed to the trunk top socket and to the TC and TR clumps |
| BM4 (unlabelled, right) | (383–516, 964–1079) | the **long riser**: base with a socket (390, 1050) rising up-right to a two-tine tip (480, 975); a **side branch** from mid-way runs right (440–500, 1015–1025) and **carries the R clump** |
| Trunk Core | (255–389, 1023–1215) | a **tapered faceted column** of planks with a **hollow socket ring at the top** (rim `#F8AB5F`), two side socket bosses near the top (left (275, 1075), right (355, 1070)), a **flared foot of six short root stubs** with sockets (and one pale peg (300, 1165)), dark bore pits |
| Root Base | long root modules: left (131–249, 1132–1232) 3 toes; front (227–300, 1185–1316) 2–3 toes; right (397–513, 1144–1252) 2 toes, curving; short pieces (385–465, 1204–1273) and (189–225, 1219–1254) | thick faceted tapering prisms with plank facets, a peg end, a kink where they meet the ground, **split blunt toes**; six rocks (pale grey, faceted, 8–12 broad facets) and eight lime tufts (pointed blades, lime tips, green hearts) |

#### Trunk core — exploded, close-ups 1 and 2, hero
- **Shape:** a twisted, planked column of six rope strands (§2.2), flared at the foot into six root stubs; a waist at z
  7; two side bosses at the crotch (BM1, BM4), one upper-left boss (BM2) and a top socket (BM3); the front knot and the
  back knot; 10–14 bark pits; an octagonal hollow underside.
- **Hero size:** body Ø 6.6 at z 0 (before the roots), 5.6 at z 3, 4.9 at z 6, **4.7 at z 7**, 5.2 at z 9.4, 3.9 at z
  11.6, 3.6 at the top (z 12.4). Part about 10 × 10 × 12.4 with the stubs and bosses.

#### Branch modules (four) — exploded, close-up 1, hero
- **Shape:** straight faceted prisms (main runs 6–8-sided, arms 5, tines and twigs 4: chunky), **hard kinks** at
  waypoints, a flat 8-sided cut base face with a round pale peg; forks with dark pits in the crotch; bare tines 0.9–1.4
  long, blunt, flat-ended (pale or dark ends).

#### Leaf clumps (five) — exploded, close-up 3, hero
- **Shape:** a rounded mound (W : H 1.15–1.45) of **chunky lobed leaf cards** layered and overlapping over a **solid dark
  core**, fed from below by a **branch core** (stem + Y fork + twigs) whose base is the clump module's stub. Scalloped
  outline with lobes ~2.2 studs apart; lime on top, mid on the body, dark underneath.

#### Root base — exploded, close-up 2, hero
- **Shape:** six thick tapering roots (6-sided, plank facets, a top ridge) leaving the trunk stubs at z 4–5, arching
  down, one kink where they meet the ground, then a low run that **splits into 2–3 blunt toes**; rocks, tufts and moss
  between them.

### 1.5 How 054 differs from its siblings and W05 `OakTree` (binding: the verifier checks these)

| | 047 Old Pine (`GnarledPine`) | 053 Dead Tree (`TwistedSnag`) | W05 `OakTree` (old kit) | **054 Broadleaf Tree** |
| --- | --- | --- | --- | --- |
| Size | 20 tall, canopy 20.3 × 12 | 18 tall, crown 17.6 × 15 | 22.5 tall, 23.6 wide | **20 tall, crown 20.2 × 19.5, W : H 1.0, round in plan** |
| Silhouette | five flat green pads with sky between, T 38 % | bare wood only, T 78 % | a flat blob crown | **one scalloped dome of five touching clumps, canopy G 47 %, T 37 % (10–12 above h .45), fill 0.60** |
| Foliage | domed pads of flattened lobes | none | star-lobed lumps | **mounds of chunky lobed leaf cards over a dark core, lime tops** |
| Trunk | Ø 6.2, planked, leaning 7°, forked | Ø 5.0 waist, six twisted strands | a plain cone, too thin | **Ø 4.7 waist, six twisted strands, flare 9.6, two low limbs at the crotch and a V leader** |
| Limbs | five elbowed limbs to pads | six bare modules, 11–15 tine ends | five thin limbs | **four plug-in modules (big Y, short upright, top V, riser with side branch) feeding five clumps; bare forked tips under the side clumps** |
| Roots | seven buttress roots on sand | six roots, split toes | wedge roots on a patch | **six roots arching to split toes, moss on two root tops** |
| Holes | a knot (slot), hollow stubs | 40–55 pits, a ringed knot, a snapped end | one knot | **a pale-rimmed oval knot front and a hex-rimmed knot back, 10–14 bark pits** |
| Top view | rosettes round a limb star | a nine-armed star | five round clumps | **five rosette clumps in a ring with a brown limb hub showing (T 7.7 %)** |
| Ground | sand patch | moss pads, tufts, rocks | grass patch | **no patch: a lime moss band, tall pointed lime tufts, pale grey rocks** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, trunk axis at (0, 0)). Plan azimuths: 0° = +X, counter-clockwise,
90° = +Y (back), 270° = −Y (front).

### 2.1 Stack (binding contact chain, bottom up; every seat gap 0.015)

| Piece | Sits on / in | Contact |
| --- | --- | --- |
| Trunk core (one closed shell: body, bosses, top socket, six root stubs) | ground | flat 8-sided bottom ring at z 0 with the hollow recess inside it (hidden) |
| Root modules (6) | their stubs and the ground | round peg into the stub socket 0.30 deep, 0.02 clearance; the module's base face 0.015 off the stub face and 0.02 wider all round; toes sunk 0.05 into z 0 |
| Branch modules (4) | their bosses / the top socket | peg 0.30 deep, 0.02 clearance; base face 0.015 off the boss face, 0.02 wider all round |
| Arms, tines, twigs inside a module | their parent segment | part of the module's ring-stack shell, or closed shells buried ≥ 0.15 in the parent (decision §8.6) |
| Clump branch core (stub + Y + twigs) | its module's tip | stub base face 0.015 off the module tip face, inside the clump's core underside by ≥ 0.3 (the joint never shows) |
| Clump core (dark solid dome) | the branch core's twigs | each twig tip buried 0.25–0.4 in the core |
| Leaf cards | the core and neighbours | each card's underside centre within 0.03 of the core surface (or a neighbour card); ≤ 25 % of its verts inside the core; none inside a neighbour (§6) |
| Rocks, pebbles | ground | sunk 0.10 / 0.04 |
| Moss pads | ground | z 0 … 0.08–0.12, sunk 0.02 |
| Tufts | ground or a moss pad | hub sunk 0.03; every blade within 0.03 of its hub |

### 2.2 Trunk core

| Ring z | 0 | 1.5 | 3.0 | 4.5 | 6.0 | 7.0 | 8.2 | 9.4 | 10.6 | 11.6 | 12.4 (top) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Body Ø (strand crests) | 6.6 | 6.0 | 5.6 | 5.2 | 4.9 | 4.7 | 4.9 | 5.2 | 4.4 | 3.9 | 3.6 |
| Centre X | 0 | 0 | 0 | 0 | 0 | 0 | 0.05 | 0.15 | 0.35 | 0.55 | 0.7 |
| Twist (strand azimuth offset) | 0° | 8° | 16° | 24° | 32° | 37° | 44° | 51° | 58° | 63° | 67° |

- **Section:** **six strands**, each three facets wide (18 sides); the vertex between two strands pulled in 0.30–0.40
  (a deep V groove), the strand's middle facet proud 0.06–0.12, alternating strands 8–12 % thicker. Strand azimuths at
  z 0 are the six root azimuths (§2.3): each root continues up as a strand; the strands feed the bosses at the crotch.
- **Twist:** counter-clockwise seen from above, about 67° foot to top, so the front grooves climb lower-left →
  upper-right ("/"), as the f34 and front show. No ring finer than these eleven.
- **Top:** a flat cut face, a 9-sided cap Ø 3.6 with a pale cut rim (0.35 wide) and the **top socket** (round hole Ø 1.1 ×
  0.35 for BM3's peg). From above, the rim shows as a pale ring round the leader base (the top cell's pale hub).
- **Bosses (3)** for the side modules, each an **8-sided collar** rising out of a strand pair, **flat face** with a round
  socket at its centre (close-up 1):

  | Boss | Face centre | Axis (az, rise above horizontal) | Collar Ø | Peg hole | Takes |
  | --- | --- | --- | --- | --- | --- |
  | B_L | (−2.75, 0.3, 9.6) | 175°, 15° | 2.6 | Ø 1.0 | BM1 (big Y, left) |
  | B_R | (2.85, −0.3, 9.7) | 355°, 15° | 2.6 | Ø 1.0 | BM4 (riser, right) |
  | B_UL | (−1.2, −1.6, 11.4) | 230°, 40° | 1.9 | Ø 0.75 | BM2 (short upright, front-left) |
  | S_TOP | (0.7, 0.1, 12.4) | up, tilted 8° toward +Y | 3.6 face | Ø 1.1 | BM3 (top V) |

  Collars protrude 0.4–0.6 beyond the strand crest; with the module bases they make the crotch 7.7–11.9 across at z
  9–10.
- **Root stubs (6):** at the foot, short faceted prisms leaving the strands at z 0.6–2.8, axis down-out 25–35°, ending at
  r 3.6–4.0 in a flat 8-sided face (Ø 2.2–2.6) with a round socket for the root's peg. Their top ridges carry the strand
  up to z 4–5 (the root shoulders: 9.6 across at z 4).
- **Front knot:** centre on the trunk surface at (1.05, −2.4, 9.4) (az 294°): an **oval recess 0.9 × 1.3, 0.4 deep**,
  inside a **raised pale rim** (outer 1.4 × 1.8, raised 0.10, 8-sided); a **small round hole** Ø 0.5 above it at (0.9,
  −2.2, 11.1); 3–4 bark pits below (z 7–8.5). It must read as **a dark oval hole with a pale ring** at cell scale, not a
  slot (047 leftover).
- **Back knot:** at (−0.1, 2.45, 9.4) (az 92°): a round recess Ø 0.9 in a **hexagonal pale raised rim** (outer Ø 1.5) —
  the r34's knot.
- **Bark pits (10–14 on the core):** small dark square or triangular insets (0.25–0.35, flat `hollow` insets on strand
  crests, never in grooves), mostly in the front and back faces between z 4 and 11.
- **Underside:** the flat bottom is an 8-sided ring (outer Ø ≈ 6.0) round an **octagonal hollow recess** (Ø 2.6 × 0.4
  deep, `hollow`) with a pale chamfer rim (close-up 2). Hidden on the hero; shown in the part's underside shot.

### 2.3 Roots (six)

| Root | Module | Azimuth | Reach r (toe tips) | Ø at stub → mid → toes | Toes | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| RT1 | Root A (long, 3 toes) | 195° | 7.6 | 2.4 → 1.6 → 0.7 | 3 | front tip x −.37 H; rear far side |
| RT2 | Root B (medium, 2 toes, curving) | 240° | 7.2 | 2.2 → 1.5 → 0.7 | 2 | front tips −.26…−.12; f34 front-left root to (230, 470) |
| RT3 | Root A (second instance, the big front root) | 295° | 7.8 | 2.6 → 1.9 → 0.9 | 3 | front tips +.07…+.21 (the thick front-right root); f34 (420, 475); exploded front root |
| RT4 | Root C (long, 2 toes) | 350° | 8.2 | 2.4 → 1.5 → 0.7 | 2 | front tips +.34…+.42; moss patch on its top |
| RT5 | Root B (second instance) | 45° | 7.4 | 2.2 → 1.4 → 0.7 | 2 | rear tips −.34…−.28 (world X +5.6…+6.8) |
| RT6 | Root C (second instance) | 125° | 7.6 | 2.4 → 1.6 → 0.8 | 2 | rear big near root +.02…+.17; rear far tips |

- **Profile:** each root's top ridge leaves its strand at z 4.0–5.0 at r ≈ 2.6, arches down over 2.0–2.6 of reach (the
  buttress), touches the ground at r 4.2–4.8 with **one kink**, then runs low (top 0.9–1.4 above the ground) to the
  toes. Section 6-sided: a top ridge, two upper flanks, two lower flanks splayed onto the ground, a flat bottom.
- **Toes:** 2–3 blunt prisms (4–5-sided, Ø 0.6–0.9, 0.7–1.1 long) splayed 20–30° apart, flat end faces (about half
  pale cut, half dark), sunk 0.05.
- **Moss on roots:** two lime moss patches on root tops (RT3 at r 3.2–4.2, RT4 at r 4.6–5.6), as a colour region on the
  root's ridge faces chosen by position (§5.5), not extra shells.
- Vary each repeated module's yaw ±5° and reach ±0.4 so the repeats don't read.

### 2.4 Branch modules (four) and their limbs

Waypoints are segment ends (straight segments; every waypoint a hard mitred kink). Ø per waypoint. Twigs and tines are
4-sided, flat-ended.

| Limb | Module | Boss | Waypoints (x, y, z) → | Ø | Arms, tines, twigs (tip (x, y, z)) | Feeds |
| --- | --- | --- | --- | --- | --- | --- |
| **LOW-L** | BM1, the big Y (labelled) | B_L | P0 (−2.75, 0.3, 9.6) → knuckle K (−4.0, 0.4, 9.9) | 2.4 → 2.0 | **upper arm** K → (−4.6, 0.8, 11.0) → stub joint J_L (−5.1, 1.1, 12.0), Ø 1.6 → 1.3; **lower arm** K → (−5.4, 0.0, 9.3) → fork (−6.6, −0.3, 9.6), Ø 1.4 → 0.9; **bare tines** to (−7.6, −0.8, 10.4) and (−7.8, 0.1, 9.1), Ø 0.5 | L clump (upper arm); the lower fork pokes out under L's lower-left edge |
| **UPPER-L** | BM2, the short upright | B_UL | (−1.2, −1.6, 11.4) → kink (−2.0, −3.0, 12.4) → stub joint J_FL (−3.1, −4.6, 13.2) | 1.7 → 1.4 → 1.1 | a spur at the kink to (−1.8, −3.2, 13.6) (Ø 0.6, cut end pale) | FL clump |
| **LEAD** | BM3, the top V | S_TOP | (0.7, 0.1, 12.4) → fork V (1.1, 0.6, 13.7) | 2.8 → 2.2 | **back-left arm** V → (0.8, 2.4, 14.6) → J_B1 (0.6, 4.0, 15.2), Ø 1.6 → 1.3; **right arm** V → (2.4, 1.6, 14.6) → J_B2 (3.4, 4.2, 15.4), Ø 1.5 → 1.2; **base spur** from (0.9, −0.3, 13.2) to (1.5, −1.3, 14.4), Ø 1.0, pale cut end facing up-front (the top-view hub) | B clump (both arms) |
| **LOW-R** | BM4, the riser | B_R | P0 (2.85, −0.3, 9.7) → elbow E (3.9, −0.7, 10.0) | 2.4 → 1.9 | **riser** E → (4.0, −2.6, 11.2) → J_FR (4.3, −4.2, 12.4), Ø 1.6 → 1.2; **side branch** E → (5.6, −0.3, 9.6) → J_R (6.8, 0.1, 10.6), Ø 1.4 → 1.0; **bare fork** at the side branch from (6.0, −0.2, 9.6): tines to (7.2, −0.9, 9.3) and (7.0, −0.6, 10.2), Ø 0.5 | FR (riser), R (side branch) |

- **Branch-by-branch from the sheet** (front cell, studs from the axis, z above the ground):

  | Limb | Leaves the trunk | Segments seen | Ends seen |
  | --- | --- | --- | --- |
  | LOW-L | (−1.4…−3.5, 9.2–11.9), the **pale knob**: the base plus the up-left arm start | lower arm out-left nearly level (Ø 1.2–1.6 at X −3.7…−4.8, z 8.0–9.5) | a 0.4 twig rising to (−6.9, 10.4) at the clump's lower-left edge |
  | LOW-R | (+2.6…+3.6, 7.9–10.6), Ø 2.3–2.6 | level right, Ø 1.2–1.3 at X +4.2…+5.2 | a forked 0.5 tip at (+5.8…+6.8, 9.0–9.7) under R |
  | LEAD | the upper trunk (−0.4…+2.1, 11–13.2) | V at z 13.6: left lead (−0.4…+0.8, w 1.3), right lead (+1.6…+2.9 → +3.4…+4.2 at z 14.5) | both enter the clumps above z 15 |
  | UPPER-L | hidden behind FL in the front; the f34 shows it rising up-left into the upper-left clump with a two-twig fork | | |

- **Visible limb lengths (binding, §9.1):** in the front, rear and f34 renders each of LOW-L, LOW-R and LEAD must show
  **≥ 1.5 studs of bare limb** not hidden by leaves or trunk, and each bare fork (LOW-L, LOW-R) its two tines against
  the sky or the clump underside. UPPER-L and the FR riser must show ≥ 1.0 stud in the f34 or r34.
- **Bark pits on modules (8–12):** at each knuckle, elbow and fork crotch first (dark square insets, §8.7).
- **Cut ends:** every tine and spur end flat; about half pale (`bark_light`), half dark (`hollow`).

### 2.5 Leaf clumps (five)

| Clump | Module tip | Centre (x, y) | Bottom z (inner / outer droop) → top z | W × D × H | Cards | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| **B** (back, crown) | J_B1, J_B2 (BM3) | (1.7, 5.3) | 13.8 / 13.2 → **20.0** | 10.4 × 8.6 × 6.6 | 18 | top 1.7, 5.5 (10.4 × 8.1); front top centre z 19.8, gap bottom .68–.75 H |
| **FL** (front-left) | J_FL (BM2) | (−3.6, −5.6) | 11.6 / 11.0 → 18.6 | 7.4 × 7.2 × 7.2 | 14 | top (−3.6, −5.8); front top-left z 18.7, bottom .55–.58 H |
| **FR** (front-right) | J_FR (BM4 riser) | (4.4, −5.2) | 11.2 / 10.4 → 18.6 | 8.4 × 8.4 × 7.6 | 15 | top (4.4, −5.3); front top-right z 18.7, bottom .51–.53 H |
| **L** (left, low) | J_L (BM1 upper arm) | (−5.4, 1.2) | 9.6 / 8.2 → 15.2 | 8.8 × 9.2 × 7.0 | 16 | top (−5.2, 1.3); front X −9.4…−0.1, bottom .41–.43 H, top .67–.78 |
| **R** (right, low) | J_R (BM4 side branch) | (7.2, 0.2) | 9.9 / 7.8 → 15.8 | 6.6 × 8.8 × 7.4 | 14 | top (7.4, 0.2); front X +2.1…+10.3, bottom .39–.43 H (droop outside the limb) |

- **Core (one per clump):** a solid flattened dome (7-sided, bottom ring + two bands + top vertex, ≈ 30–40 tris,
  `leaf_dark`), 0.75–0.8 of the clump's W and D and 0.7 of its H, its underside near-flat (the clump bottom). It fills
  the clump so no sky shows through between cards (cu3 "solid").
- **Branch core (one per clump, the module's stub):** a stub (Ø 1.0–1.3, 5-sided) from the module tip up into the core
  underside, a Y fork 0.6 inside, and 2–3 twigs (Ø 0.45–0.6, 4-sided) running out to the card layer; twig tips buried
  0.25–0.4 in the core's upper shell. One or two twigs on each low clump (L, R) and on FL may poke out between the lowest
  cards (the f34 shows twig forks under the upper-left clump).
- **Leaf card (closed, 16 tris):** an **8-vertex rim of four broad rounded lobes** (radii alternating 1.0 / 0.80 of the
  card radius, lobe tips widened by placing the notch verts at ±18° from the lobe axis), a **raised top centre** 0.18
  above the rim and a **lowered bottom centre** 0.12 below (a chunky bicone plate: no side walls, no zero-area faces,
  corners ≥ 8°). Card Ø 2.0–3.0 (top cards largest), so the outline scallops come ~2.2 apart as measured. If the budget
  allows, the ~40 most visible top and rim cards may use a 10-vertex 5-lobe rim (20 tris) — never pointed stars
  (memory `kit-quality-bar`: "spiky where the master is broad").
- **Card placement** (per clump, deterministic seed): cards on the core's surface by a Fibonacci spread over the upper
  80 % of the dome plus **one lower ring of 4–6 cards** that hangs 0.3–0.8 below the core rim on the clump's outer side
  (the droop; the inner side toward the trunk stays up so the limbs show). Each card's plane tangent to the dome, then
  tilted outward 15–30° (so its outer lobes stand proud and scallop the outline), random spin, overlapping neighbours
  by 30–50 % of its radius; underside centre seated within 0.03 of the core. Top cards larger and flatter, rim cards
  steeper.
- **Read:** each clump must read as **one rounded mound of overlapping leaves** — a scalloped outline, a lime top, a
  mid body, a dark underside — **not a cluster of separate balls** (047 round 1) and **not a smooth blob** (W05). The five
  clumps touch or overlap in the front view (as the sheet) but each keeps its own outline scallops.

### 2.6 Base dressing (no ground patch)

Plan positions from the front, rear and f34 blobs (§1.2). Every piece sits between roots (≥ 25° from the nearest root
azimuth) or against a root's flank without cutting it.

| Piece | Position (x, y) | Size W × D × H | Evidence |
| --- | --- | --- | --- |
| RK1 low front-left | (−5.7, −4.0), az 215° | 2.8 × 2.4 × 2.3, sloping faceted top | front −.37…−.24 h .12; f34 big low (255–323) |
| RK2 far-left small | (−8.4, −0.6), az 184° (past RT1's toes) | 1.4 × 1.2 × 1.3 | front −.42…−.35 h .07 |
| RK3 front-centre | (−0.6, −7.0), az 265° | 2.2 × 2.0 × 2.1 | front −.07…+.04 h .11; f34 (369–412) |
| RK4 tall right | (5.0, −3.9), az 322° | 2.6 × 2.2 × 2.8, a pointed top leaning to the trunk | front +.23…+.34 h .13; f34 big right rock (481–547), the tallest |
| RK5 back-right | (5.9, 2.4), az 22° | 2.6 × 2.2 × 2.1 | rear −.38…−.20 (world X +4…+7.6) |
| RK6 back-left | (−5.6, 3.6), az 147° | 2.2 × 2.0 × 2.0 | rear +.23…+.32 h .12 |
| RK7 back-centre small | (−2.2, 6.6), az 108° | 1.5 × 1.3 × 1.2 | rear −.04…+.03 |
| Pebbles ×4 | (−2.4, −7.4), (1.0, −7.6), (8.8, −2.6), (1.4, 6.8) | 0.5–0.8 | small greys in every view |
| Moss band: pads ×6 | between roots, mid-angles az 218°, 268°, 322°, 18°, 85°, 160°, at r 3.6–6.0 (inside the rock ring), plus their outer lobes cut round the rocks (≥ 0.05 clear) | lobed, 3.0–4.5 across, 0.08–0.12 thick | the continuous lime ground band in f34 / front / rear (ground G 5–9 %) |
| T1 tall far-left tuft | (−8.8, −3.4), az 201°, past RT1's toes | Ø 2.6, 3.2 tall, 7 blades | front −.44…−.31 top h .20; f34 (218–249) |
| T2 left tuft beside RT1 | (−5.9, 0.8), az 172° | Ø 2.0, 2.6 tall, 6 blades | f34 (255–297, 376–421) tall left |
| T3 front sprigs | (−0.7, −5.0), az 262° | Ø 1.6, 1.6 tall, 5 blades | front −.26…−.18 / centre |
| T4 front-centre sprigs | (1.4, −6.4), az 282° | Ø 1.4, 1.2 tall, 5 blades | front centre moss and sprigs |
| T5 right group | (4.6, −5.8) and (8.4, −3.6) | Ø 2.0 / 2.4, 2.2 / 2.6 tall, 6 + 7 blades | front +.19…+.47; f34 (483–594) |
| T6 tall right-back | (8.4, 3.4), az 22°, behind RK5 | Ø 2.2, 3.0 tall, 7 blades | front +.28…+.39 h .09–.24; f34 (517–560) |
| T7 back-left | (−7.6, 1.8), az 167° | Ø 2.0, 2.6 tall, 6 blades | rear +.17…+.44 group |
| T8 back-centre | (0.6, 7.4), az 85° | Ø 1.6, 1.8 tall, 5 blades | rear centre |

- **Clearances as planned** (lateral distance from the nearest root's centreline at the piece's radius, against the sum
  of half-widths): every piece ≥ 0.1 clear on paper; RK1, RK7, T4 and T5a are the tight ones (0.1–0.4). Re-check by ray
  parity after placement and nudge outward along the azimuth, never into a root.

- **Blades:** pointed lanceolate, **broad at the base** (length : width ≈ 4), folded once along the midrib (closed, 6
  tris), rising 60–85° and arching out from a small hub; tall (2–3.2) with lime tips and a green heart. The sheet's tufts
  are spiky grass, so pointed tips are right here, but never needles and never edge-on to the f34 or front camera (039).
- **Rocks:** pale grey angular blocks, flat base, 8–14 broad facets; RK4 the tallest (W : H 0.9, pointed top), the low
  ones W : H 1.2–1.4 with a sloping faceted top. Never `K.hull_rock` eggs.
- **Keep clear:** nothing more than 0.05 inside a root, toe, the trunk or a rock (047 round 2 blocker); every tuft hub ≥
  0.3 outside root surfaces; rocks may touch roots but cut ≤ 0.05.

### 2.7 Expected extents and screen checks

- **Extents:** X −9.8 … +10.5 (L and R clumps), Y about −9.6 … +9.6 (FL / FR fronts; B's back), Z 0 … 20.0. Bbox about
  20.2 × 19.2 × 20.0.
- **Checks on the renders** (floor hidden, `measure_render.py` with this folder's `m.py`):
  - **front_sheet (0, 5)** — governs positions: W : H 0.95–1.06 (sheet 1.009); G 53.6 ± 4 (canopy 46.8, ground 6.7), T
    37 ± 4, R 6 ± 3; fill 0.60 ± 0.05; **T above h .45 ≥ 8 % (sheet 10.8)**; canopy bottom row (§1.2) ±0.06 per column,
    with the **gap at x .00–.10 (bottom ≥ .62)**; top profile ±0.07 for f .1–.9; the knot a dark oval with a pale ring
    at (+.053 H, h .47); the low-limb forks at (−.31…−.36 H, h .45–.52) and (+.26…+.30 H, h .45–.48).
  - **f34_sheet (0, 13)** (probe az −35 … +35 × e 9 / 13 / 16, keep the best; §3.2): W : H 0.98–1.10 (sheet 1.094);
    G 57 ± 4, T 32.6 ± 4; T above h .45 ≥ 8 (sheet 10.8); light / mid / dark leaf tone shares 55 / 31 / 14 ± 8.
  - **rear_sheet (180, 5), r34_sheet (180, 13)** (probe 145 … 215): W : H 0.92–1.04; T 38 ± 4; T above h .45 ≥ 9; the
    back knot visible with its hex rim.
  - **side_sheet (90, 5):** content (§3.3): W : H 0.80–1.00 (sheet 0.902); clumps both sides of the trunk; low clump
    bottoms at h ≤ .45 on both sides of the trunk; the trunk visible from the ground to h .45.
  - **top (0, 89):** W : D 0.95–1.12 (sheet 1.027); five clump rosettes round the hub; T 4–12 % (sheet 7.7); leaf light
    / mid / dark ≈ 52 / 35 / 13 ± 10.

## 3. View conflicts and resolutions

### 3.1 Sheet number
- **Evidence.** The header says "53 / 132"; INDEX.md row 54 lists `054.png` as "Flintborn broadleaf tree study".
- **Resolution.** Our number is 054 (file name, keys `m054_*`). Note the header in the export notes only.

### 3.2 The front three-quarter is near-frontal and drawn wider
- **Evidence.** The f34's knot sits at +0.10 H (front +0.053), its limb tips at −0.46 / +0.50 H (front −0.36 / +0.32),
  its crown −0.535 … +0.554 H (front −0.473 … +0.522), and its ground band twice as deep. Both sides grow by the same
  amount, so it is not a turn: it is a higher camera and a looser drawing. The r34's W : H (0.971) equals the rear's
  (0.978).
- **Resolution (decision §8.10).** `front_sheet (0, 5)` governs positions; `f34_sheet (0, 13)` governs the read and the
  shares; probe az −35 … +35 (e 9–16) and keep the best; record the camera. Don't widen the crown to chase the f34's
  1.094 beyond 1.10.

### 3.3 Front, side and rear are the same drawing
- **Evidence.** The three ortho cells share one silhouette (W : H 1.01 / 0.90 / 0.98), one knot at the crotch, one pale
  limb knob, two low clumps at both sides (bottoms h .36–.43) and a three-clump top in each. A real tree with five
  clumps in a ring (the top cell) cannot show low clumps at both sides in two views 90° apart.
- **Resolution.** **Front and rear govern positions; the top governs the plan; the side is judged for content** (as 053
  §3.3). The plan (§2.5) puts the low clumps at the left and right and the high ones front and back, so the front and
  rear match; from the side the low clumps show as low masses either side of the trunk inside the front / back clumps.
  Side checks: W : H 0.80–1.00, clumps both sides, low bottoms ≤ .45 both sides, trunk visible.

### 3.4 Which clump each module feeds (exploded vs hero)
- **Evidence.** The exploded's dashed lines are loose: TL is dashed both to BM1's upright stem and to BM2's tine; TR to
  BM3's tip and BM4's riser; TC to BM3's base. The hero shows two low limbs, a V leader and limbs rising into the upper
  clumps.
- **Resolution.** **Modules are assigned by shape and the hero's limbs** (§2.4): BM1 → L, BM2 → FL, BM3 → B (both V arms),
  BM4 → FR (riser) and R (side branch). Five clumps on four modules, as the exploded counts.

### 3.5 Exploded scale vs the hero
- **Evidence.** At the clumps' scale (12.5 px / stud) the exploded trunk core's top rim is 85 px (6.8 studs) and BM1 is
  10.9 × 8.5 — the exploded is drawn closer and bigger.
- **Resolution.** **The hero governs sizes and heights**; the parts shot uses the hero's own module meshes.

### 3.6 How many roots
- **Evidence.** Exploded: three long root modules, two short pieces, stubs round the core foot. Close-up 2: six roots
  round the hollow. Front and rear: four to five root tips each, mirrored.
- **Resolution.** Six roots from three module shapes (A ×2, B ×2, C ×2), ±5° yaw and ±0.4 reach per instance (§2.3). The
  exploded's two short pieces are the B instances' look; not separate assets.

### 3.7 Sockets, pegs and joint seams in the hero
- **Evidence.** Close-up 1 and the exploded show pegs, bosses and sockets; the assembled views show no seams at the limb
  bases (only the lit pale planes of the BM1 knob and the r34 knob).
- **Resolution (decision §8.5).** Pegs, bosses and holes are modelled on the parts; in the hero each module's base face
  overhangs its boss by 0.02 all round so the joint reads as a plank crease, never a pale ring. The pale knob is the
  **upper planes of BM1's knuckle** in `bark_light` by role (§5.3), not a cut face.

### 3.8 Ground: no patch drawn
- **Evidence.** No soil disc in any cell: a lime moss band runs under the roots and tufts; paper shows past r ≈ 0.47 H.
- **Resolution.** No patch. Six broad, thin, lobed moss pads between the roots make the band; rocks, pebbles, tufts and
  root toes sit on z 0.

### 3.9 "No noise or texture maps" vs the user's colour rule
- **Evidence.** The modelling notes ask for "no micro detail, noise or texture maps"; the user wants rich, blended colour
  with broad Tint mottling (memory `lighting-not-paint`).
- **Resolution.** Several keys per material, blended by position and role; broad per-region Tint (0.03–0.04 per plank
  run / card / facet), never per-triangle confetti, no image textures beyond the exporter's palette.

### 3.10 Cast shadow
- The sheet's lavender shadow is excluded by the X mask. Render every `*_sheet` view with the studio floor hidden.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its exploded cell

1. `seg_chain(points, radii, sides, twist)` → one closed tapering prism chain, a ring of `sides` at each waypoint, mitred
   (the ring's plane bisects the two segments), flat end caps. **No smooth curves; every waypoint a hard kink.** Builds
   every limb, arm, twig, stub and root. Reuse 053's if `m053.py` has it (import, don't edit it).
2. `tine(base, tip, r)` → a 4-sided chunky prism with a flat end cap, its base buried ≥ 0.15 in the parent.
3. `pit(face, size)` → a flat `hollow` inset on a facet centre.
4. `peg(face, r)` → a round (8-sided) pale peg, Ø 0.4 × the base Ø, 0.30 + 0.20 visible on the part.
5. `branch_module(kind, joints)` for `big_y` (BM1), `upright` (BM2), `top_v` (BM3), `riser` (BM4): each in its own local
   frame (base face at the origin, axis +Z), so the same function serves the hero and the part. Check each against its
   exploded cell before assembling.
6. `root_module(kind)` for `A` (3 toes), `B` (2 toes, curving), `C` (2 toes, long).
7. `trunk_core()` → the twisted 6-strand body (§2.2), then the three bosses and six root stubs **unioned one at a time at
   the origin** (`m021._union_fine`, merge 0; save between unions; collapse corners under 3°), then the top socket, the
   two knots, the trunk pits and the underside hollow.
8. `leaf_card(r, lobes, seed)` → the closed bicone lobed plate (§2.5). `clump_core(w, d, h)` → the dark flattened dome.
   `branch_core(stub_len, twigs)` → the stub + Y + twigs. `leaf_clump(spec, seed)` → branch core + core + cards, placed
   by §2.5's rules, in its own local frame (stub base face at the origin), so one function builds all five clumps and
   the part.
9. `base()` → `rock(spec)` ×7 (explicit ring stacks: base ring, widest ring at 0.3 h, shoulder ring at 0.7 h, a flat
   sloping or pointed top; 8–14 broad facets), `pebble()` ×4, `moss_pad()` ×6, `tuft(spec)` ×9 with the placement guard
   (§6).
10. **Hero `ShadeTree`** = trunk core + four branch modules on their bosses + five clumps on the module tips + six roots on
    their stubs + base, joined into one object of closed shells.
11. **Parts shot** (0, 22) laid out like the exploded: the trunk core in the middle, branch modules round its top, the
    leaf clump above, the root base below; gaps 1.5–2.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a round-crowned broadleaf on a massive twisted planked trunk; five overlapping-leaf mounds, lime on
   top; two low limbs with bare forked tips under the side clumps; a V leader in the gap under the back clump; six
   split-toed roots; a pale-rimmed knot; pale grey rocks, tall lime tufts and a lime moss band at the foot.
2. **front_sheet / f34_sheet** per §2.7 (shares, fill, W : H, canopy bottom row with the gap, T above h .45).
3. **rear / r34 / side / top** per §2.7.
4. **Close-up renders:** `join_cu (−25, 20)` on the trunk core part's B_L boss with BM1's base and peg beside it, against
   close-up 1; `underside` (0, −89) on the trunk core part against close-up 2 (octagonal hollow, pale rim, six roots
   radiating); `clump_cu` — the FL clump cut by a plane (or rendered with its front cards hidden) against close-up 3
   (branch core Y with twigs inside, cards layered round it); `knot_cu (−10, 5)` on the front knot.
5. **Contact counts** (§6): floating shells 0; every card chained to its core, every core to its twigs, every module to
   its boss; buried cards 0.
6. **Hero size** per §2.7; a **scale shot** with a 5.5-stud marker under the R clump (its lowest leaves at z 7.8 clear
   the marker's head by 2.3) and a second marker between RT3 and RT4.

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Trunk body (18 sides × 10 bands, caps) | 1 | 370–400 | 370–400 |
| Bosses + top socket | 4 | 24–40 | 110–150 |
| Root stubs | 6 | 20–28 | 120–170 |
| Knots (front, back, small hole) + underside hollow | | | 60–90 |
| **Trunk core part** | | | **660–800** |
| Branch modules (main 6–8 sides, arms 5, twigs 4; pegs hidden in the hero) | 4 | 60–150 | 380–440 |
| Clump branch cores (stub + Y + 2–3 twigs) | 5 | 30–40 | 150–200 |
| Bark pits (flat insets) | 20–26 | 6 | 120–160 |
| Root modules (6-sided, 3 segments, 2–3 toes, peg) | 6 | 50–60 | 300–360 |
| **Skeleton** | | | **≈ 1600–1750** |
| Clump cores | 5 | 30–40 | 150–200 |
| Leaf cards (16 tris; up to 40 at 20) | 77 | 16–20 | 1230–1390 |
| **Foliage** | | | **≈ 1400–1580** |
| Rocks | 7 | 26–36 | 180–230 |
| Pebbles | 4 | 8–12 | 32–48 |
| Moss pads | 6 | 14–20 | 84–120 |
| Tuft blades (6 tris) + hubs (8) | 57 + 10 | | 340–420 |
| **Base** | | | **≈ 640–820** |
| **Hero** | | | **about 3600–3800** (limit 4000; ceiling 3800) |
| Parts: TrunkCore / BranchModule (BM1) / LeafClump (FL) / RootBase | | | 700–850 / 160–220 / 300–360 / 950 (limit 1000) |

- **Skeleton vs foliage split:** about 46 % skeleton, 39 % foliage, 15 % base. Spend headroom on the skeleton's read
  first (a 7th / 8th side on the low limbs' main segments, as the 8-sided cut end in close-up 1), then the 20-tri cards.
- **If the hero passes 3800:** drop the hidden pegs from the hero (decision §8.5), then cut tuft blades to 5, then the
  card count to 70 (never below 12 per clump), then drop T4. Never subdivide.
- **RootBase** is the tight part: roots 330 + rocks 210 + pebbles 40 + moss 100 + tufts 380 ≈ 1060 → keep it under 1000 by
  using 5 blades per tuft in the part, or leave the moss pads out of the part (they stay in the hero).

### 4.4 What to do better than W05's `OakTree`, 047 and 053

| Earlier | This one |
| --- | --- |
| W05: "flat blob crown"; clumps as star-lobed lumps | five mounds of overlapping lobed cards with scalloped outlines, lime tops, dark undersides |
| W05: "thin straight trunk", a plain cone; "too pale" | a 4.7 waist twisted six-strand trunk with a 9.6 flare; saturated lime / green / dark tones calibrated to the sheet |
| 047 round 1: stub limbs, hidden twigs | full limb runs, bare forked tips under the side clumps, the V leader in the gap; T above h .45 ≥ 8 % |
| 047 round 1: pads read as balls | cards overlapping 30–50 % on a dome, one outline per clump, tones ordered by height |
| 047 round 2: plants buried in roots and rocks | the ray-parity placement guard from day one (§6) |
| 047 leftover: knot as a slot; plants leaning yellow | an oval knot with a raised pale ring; blades calibrated, lime tips ≥ 60° hue, green hearts 78–85° |

### 4.5 Stages 2 and 3
- **Stage 2:** every shell closed and manifold; 0 bowties (card centres, tine junctions, pegs, pits and toe forks are the
  likely spots: `M.fix_bowties`); **0 winding errors per shell** (STAGES "Consistent winding": the bicone cards built by
  hand and the mitred kink rings flip easily — check every card); no zero-area faces, no n-gons except flat caps;
  corners ≥ 3°. Origin bottom centre, transforms applied.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box, sd ≤ 1.5)

| Swatch | Box | Hex | HSV | Use |
| --- | --- | --- | --- | --- |
| LEAF DARK | (29,217,69,255) | `#47852D` | 102°, 0.66, 0.52 | start for `leaf_dark` |
| LEAF MID | (29,262,69,300) | `#70A81F` | 85°, 0.82, 0.66 | start for `leaf_mid` |
| LEAF LIGHT | (29,306,69,344) | `#D6DF06` | 62°, 0.97, 0.87 | start for `leaf_light` |
| BARK MID | (29,351,69,389) | `#B4672C` | 26°, 0.76, 0.71 | start for `bark` |
| BARK LIGHT | (29,395,69,433) | `#D88E4B` | 29°, 0.65, 0.85 | start for `bark_light` |
| ROCK | (29,440,69,477) | `#998D86` | 22°, 0.12, 0.60 | start for `rock` |

### 5.2 Rendered regions (`samp.py`, `samp2.py`; median / v > .7 / lit quartile / shade quartile)

| Region | Median | v > .7 | Lit Q | Shade Q |
| --- | --- | --- | --- | --- |
| Canopy f34 / front / rear / side / top | `#A7C10A` (69°, .95, .76) / `#A5C50B` (70°, .94, .77) / `#94B70C` / `#97BD10` / `#A1C10F` | `#DCE709` / `#CEE30A` / `#D1E40B` / `#C4DF10` / `#CAE10E` | `#ECEF11` / `#DAEB0C` | `#3D6707` / `#3B610A` |
| Canopy by tone (front: light h < 72 / mid / dark h ≥ 92) | `#CDE209` / `#58880D` / `#498220` | | | |
| Canopy tone shares (light / mid / dark %) | f34 55 / 31 / 14; r34 43 / 31 / 26; front 56 / 31 / 13; side 48 / 34 / 18; rear 52 / 38 / 10; top 52 / 35 / 13 | | | |
| Canopy bands (front, light / mid / dark %) | h .85–1.0: 74 / 22 / 4; .70–.85: 56 / 28 / 16; .55–.70: 62 / 24 / 15; .40–.55: 33 / 54 / 13 | | | |
| Wood f34 / front / rear | `#8B5B31` (28°, .65, .55) / `#985F31` (27°, .68, .60) / `#986035` | `#EA9849` / `#E69646` / `#E79848` | `#F2A555` / `#F2A652` | `#4F2E17` / `#563317` |
| Wood by height (front): roots h < .2 / trunk .2–.45 / limbs > .45 | `#C27D3F` / `#8E5A33` / `#7C4A24` | `#EAA551` / `#E59041` / `#E18C3D` | | |
| Pale planes and cut faces (BM1 knob, r34 knob, knot rim lit, trunk top rim, cu1 boss) | `#E69E43` / `#F1A452` / `#F2A744` / `#F8AB5F` / `#EA9948` | | | |
| Holes (r34 knot, cu2 hollow, trunk-zone O) | `#301A03` / `#44240F` / `#151204` | | | |
| Rock f34 / front / rear | `#9B9287` / `#B5A58F` (35°, .21, .71) / `#A99D8F` | `#D4C1B0` / `#D5C1AC` / `#D6C2AC` | `#DDC9B8` / `#DFCCB8` | `#595A5D` / `#6A686C` |
| Ground moss (G at h < .035–.05) f34 / front / rear | `#CED203` (61°, .99, .82) / `#D2C90D` (57°, .94, .82) / `#D1CC0B` | `#D5D703` / `#D8D209` / `#D8D208` | | |
| Grass blades (G at h .07–.25) f34 / front / rear | `#729409` (75°, .94, .58) / `#708F11` / `#76930B` | `#D4D604` (61°) / `#CACE0A` / `#C9CD0C` | | `#34570C` (88°) / `#3A5410` / `#324A09` |

### 5.3 How the colour works

- **Leaves (cards and cores):** three keys ordered **by height within each clump and in the crown** (role and position,
  never facing): the **upper 40 %** of a clump's cards `leaf_light` (B and FR / FL tops 75 % light), the **middle** cards
  `leaf_mid`, the **lowest ring and droop cards** `leaf_dark`; the core dome `leaf_dark`. Low clumps L and R carry more
  mid and dark than B (the band shares above: the top band 74 % light, the lowest 33 %). `K.blend(mode="blend",
  steps=3)` across card heights so a clump goes lime → mid → dark without a hard band. Per-card Tint ±0.04.
- **Bark:** one warm orange-brown (`bark`, 24–28°, R > G > B) everywhere; **lighter** (`bark_light`) on cut faces
  (pegs, boss faces on the parts, the top cap's rim, the knot rims, tine and spur ends), on the **upper planes of the
  BM1 and BM4 knuckles** (the pale knob: a role region chosen by the knuckle's own geometry, i.e. the ring faces on the
  knuckle's convex side — a shape, not the sun) and **30 % on the crest facet of every other strand** (the sheet's light
  rope strands, by strand index); **deeper** (`bark_deep`) in the strand grooves (faces touching a pulled-in groove
  vertex), kink and fork crotches, under each boss, the lowest 0.5 of roots and toes, and the clump stubs inside the
  crown; **hollow** in sockets, knot recesses, the underside hollow, every pit and the dark tine / toe ends. Roots a
  touch lighter (`bark` 15 % toward `bark_light`) on their top ridges by position on the section.
- **Moss on roots:** two `moss` regions on root ridges (§2.3), hard at the edge, Tint ±0.03.
- **Rock:** pale neutral-warm grey (lit 30–36°, sat 0.12–0.20, R ≥ G ≥ B, never pink or blue); tops a step lighter
  (`rock_light`, top 30 % of each rock), feet a step deeper (`rock_deep`, lowest 25 %), by height within each rock.
- **Moss pads:** `moss` (57–61°, very saturated), edges 15 % `grass`.
- **Grass:** blades lime toward the tips and outer blades (`grass`), the inner and lower blades `grass_deep` (78–85°),
  so tufts read lime outside and green inside.
- **Hues stay apart:** bark 24–28°, cut wood 29–34°, moss 57–61°, leaf light 60–66°, grass 62–68°, leaf mid 82–88°, grass
  deep 78–85°, leaf dark 98–106°.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians where the sheet gives them, swatches where it doesn't. `K.sample`
kinds: `"brown"` for bark, `"stone"` for rock, `"vivid"` for the lime keys (`"green"` may reject the yellow lime),
`"green"` for leaf mid / dark.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m054_leaf_light` | canopy light-tone median `#CDE209` ± 12 (lit `#DAEB0C`; start `#D6DF06`) | 60–66°, ≥ 0.90 | upper cards | rough 0.8, low spec |
| `m054_leaf_mid` | the LEAF MID swatch `#70A81F` rendered lit ± 12 (canopy mid-tone median `#58880D` in shade) | 82–88°, 0.78–0.88 | middle cards | rough 0.85 |
| `m054_leaf_dark` | the LEAF DARK swatch `#47852D` rendered lit ± 12 (dark-tone median `#498220`) | 98–106°, 0.6–0.72 | low / droop cards, cores | rough 0.9 |
| `m054_bark` | front whole-wood median `#985F31` ± 15; v > .7 `#E69646` ± 12 (start `#B4672C`) | 24–28°, 0.65–0.76, **R > G > B** | trunk, limbs, roots | rough 0.9 |
| `m054_bark_light` | cut / pale planes `#F1A452` ± 12 lit (start `#D88E4B`) | 29–34°, 0.6–0.7 | cut faces, knuckle tops, knot rims, strand crests 30 % | rough 0.85 |
| `m054_bark_deep` | the wood shade quartile seen lit, `#7A4626` ± 15 | 22–26°, 0.65–0.72 | grooves 40 %, crotches 30 %, under bosses, root bottoms 25 %, clump stubs | rough 0.95 |
| `m054_hollow` | holes `#2E1806` ± 10 | 22–30°, 0.75–0.9, v ≤ 0.2 | sockets, knots, pits, dark ends, underside hollow (hard) | rough 1.0 |
| `m054_rock` | v > .7 rock `#D5C1AC` ± 10 (start `#998D86`) | 28–36°, 0.12–0.20, R ≥ G ≥ B | rocks, pebbles | rough 0.85, metal 0 |
| `m054_rock_light` | lit quartile `#DFCCB8` | 30–36°, 0.14–0.18 | top 30 % of each rock at 35 % | rough 0.85 |
| `m054_rock_deep` | the ROCK swatch `#998D86` | 20–30°, 0.10–0.14 | lowest 0.25 at 25 % | rough 0.9 |
| `m054_moss` | ground moss `#D2C90D` ± 12 (v > .7 `#D8D209`) | 56–61°, ≥ 0.90 | moss pads, root-top patches | rough 0.95, low spec |
| `m054_grass` | blades v > .7 `#CACE0A` ± 12; median `#708F11` | 62–68°, ≥ 0.85 | outer and taller blades | rough 0.85, low spec |
| `m054_grass_deep` | blade shade `#3A5410` rendered lit ± 12 → about `#4E7A14` | 78–85°, 0.75–0.88 | inner and lower blades, hubs | rough 0.85, low spec |

**Calibration warnings:**
- **The kit studio lights both halves** (042, 047): calibrate `bark` to the whole-wood median and v > .7 together, not
  the lit half alone (W05 "flat saturated orange"); record the lit-shade bias.
- **Leaves must not go pale or olive:** W05 rev 6 failed "pale lime"; 047 plants leaned yellow (aim 70° there). Here the
  sheet's lime is genuinely 62° and very saturated: `leaf_light` hue 60–66°, s ≥ 0.90; `leaf_mid` and `leaf_dark` must
  stay clearly green (≥ 82° and ≥ 98°). Check the canopy median within 15 of `#A5C50B` and the tone shares.
- **Bark must not go red:** R > G > B, hue ≥ 24° on every median.
- **Cut wood vs bark:** `bark_light` ≥ 40 levels lighter (V) than `bark` and ≥ 3° yellower, or the knot rims won't read.
- **Moss vs leaf light vs grass:** moss ≤ 61°, leaf light 60–66°, grass ≥ 62°; moss is the yellowest.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Clumps:** per card by its height rank within the clump (top light → middle mid → lowest dark), blended across 3 steps
  of rank; B's tone shifted 0.15 lighter, L / R 0.15 darker (crown height). Cores hard `leaf_dark`. Hard where card meets
  bark.
- **Trunk and roots:** `bark` base; `bark_deep` 40 % in the groove columns blended one facet out; `bark_light` 30 % on
  alternate strand crests (whole facet runs, not single triangles); 25 % `bark_deep` on the lowest 0.5 of every root and
  toe; hard `hollow` in holes; hard `bark_light` on cut faces and knot rims; hard `moss` on the two root-top patches.
  Per-plank Tint ±0.04 held in runs up each strand, plus broad noise 0.03 at scale 0.35.
- **Limbs:** `bark` base; a `bark_deep` ring at every kink and fork crotch (30 %); `bark_light` on the knuckle top
  regions; pits hard `hollow`.
- **Rocks:** height bands within each rock. **Grass, moss:** per blade by role; pad edges 15 % `grass`.
- **Hard edges only** where materials meet: cut face | bark, hole | rim, bark | leaf, wood | ground dressing, rock | moss.

### 5.6 Texture (Tint) and finish
- **Tint:** bark 0.04 per plank run + 0.03 broad; leaf cards 0.04 per card (whole cards, never per triangle); rock 0.04
  per facet; moss 0.03 at scale 0.2; blades 0.04 per blade.
- **Finish:** bark 0.9 (deep 0.95), cut wood 0.85, hollow 1.0; leaves 0.8–0.9, low spec; rock 0.85; grass and moss low
  spec. No emission.

### 5.7 Re-measure (final renders against the sheet, same masks)
- **Canopy:** front median within 15 of `#A5C50B`; v > .7 within 12 of `#CEE30A`; tone shares (light / mid / dark) 56 /
  31 / 13 ± 8 in the front, 55 / 31 / 14 ± 8 in the f34; the top band (h .85–1.0) ≥ 60 % light.
- **Bark:** front whole median within 20 of `#985F31`; v > .7 within 12 of `#E69646`; R > G > B.
- **Cut wood:** knot rims and the BM1 knob within 15 of `#F1A452`. **Holes:** v ≤ 0.25.
- **Rock:** v > .7 within 10 of `#D5C1AC`, R ≥ G ≥ B. **Moss** within 12 of `#D2C90D`; **blades** v > .7 within 12 of
  `#CACE0A`.
- **Shares** per §2.7.

## 6. Joins and contact (no floating dressing, no buried dressing)

- **Shells:** trunk core one closed shell (body + bosses + stubs, unioned); each branch module one or more closed shells
  (main run a ring-stack shell; arms, tines and twigs welded at a ring junction or closed shells buried ≥ 0.15,
  decision §8.6); each clump's branch core, core and every card its own closed shell; each root module, peg, rock,
  pebble, moss pad, blade and hub its own closed shell. All in one hero object.
- **Peg in socket:** 0.30 deep, 0.02 clearance, end 0.015 above the socket floor; base face 0.015 off the boss / stub
  face. Read the gaps back (BVH nearest per module: 0.005–0.03) and check **no peg corner inside the trunk solid** by
  ray parity (047's `plug_report`).
- **Clump chain:** card → core (or a neighbour card) within 0.03; core → twig tips buried 0.25–0.4; twigs → stub → module
  tip (0.015). **No card floating** off the dome (a tilted card must still touch it at its underside centre or rest on a
  neighbour), **no card buried**: card centre outside the core, ≤ 25 % of its verts inside the core, and no card more than
  50 % inside a neighbour card (046 had whole leaves inside a mass core; 047 round 2 had one lobe fully enclosed). Count
  both per clump and report them.
- **Limbs under clumps:** the bare forks (LOW-L, LOW-R) stay outside every card (no tine passing through a card); the
  module tip joints sit ≥ 0.3 inside their clump core.
- **Toes:** sunk 0.05 below z 0; root undersides 0–0.05 below z 0 along their low run.
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**. A shell floats if its nearest distance to
  every other shell and the ground is > 0.03 or it doesn't chain to the ground: card → core → twig → stub → module → peg /
  boss → core → ground; blade → hub → pad or ground; rock → ground.
- **Count buried shells** (STAGES; 047 round 2 blocker): **0 dressing shells more than 0.05 inside a root, toe, the trunk
  or a rock**, by ray parity against the full hero after the final placement step. Use 047's guard from the start
  (`_Solids`: trunk core + every root + every rock added as built; three skewed rays, two of three agree; placement
  accepts ≤ 0.03; a blade that still cuts after its retries is **dropped**, never kept).
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no particles, no falling leaves, no pollen, no fireflies, no dust.
The cast shadow is the render's.

- **Stage 5 (lighting): skip, and record why.** No emission, no lights. Studio notes (Requires Manual Validation): the
  canopy keeps its lime tops and green body under the game sun (not olive, not pale); the bark stays orange-brown, not
  red; the knots and pits read dark; cut faces pale; rocks pale grey; moss and grass lime.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** `lib/vfx.py` has no leaf kind; drifting leaves would be
  a new effect the sheet doesn't show (decision §8.14).
- **Collision:** hero `precise` (players walk under the clumps and between the roots; a hull would wrap a 20 × 19 × 20
  block); trunk core `precise`; branch module and leaf clump `hull`; root base `precise`. Moss pads and tufts walk-through
  only if the exporter already supports `kit_nocollide` (decision §8.11).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json`, the W-sheet and
lobby scripts and the repo text (`git grep`):
- **W05:** `OakTree`, `OakTreeRoundCrown`, `OakTreeWideCrown`, `OakTreeAsymmetric`, `OakTreeLeafClump`,
  `OakTreeBranchModule`, `OakTreeTrunkCore`, `OakTreeRootBase` (manifest), `OakLeafClump`, `OakBranchModule`,
  `OakTrunkCore`, `OakRootBase` (wip meshes); also `AncientTree*`, `DeadTree*`, `LogAndStump*`.
- **Old lobby / art scripts:** `BroadleafTreeStout`, `BroadleafTreeTall`, `BroadleafTreeWideOld`, `BroadleafTreeLeaning`
  (`build_05_trees_plants.py`, `build_lobby.py`, `export_lobby_roblox.py`, `art/blender/README.md`), `BroadleafStout`,
  `BroadleafCluster`, `FernAndBroadleaf*`; so **no `Broadleaf*` prefix** (a `BroadleafTree` hero would be a prefix of four
  lobby names).
- **Other trees:** `GnarledPine*` (047), `TwistedSnag*` (053), `OldPine*`, `TieredFir*`, `PineSapling*`,
  `SilverbarkTree`, `GoldencrownTree`, `ClassicPine*`, `TallPine*`.
- **`ShadeTree`, `Greenbough` and `m054` occur nowhere** (repo text, manifests, builders). `ShadeTree*` contains no owned
  name as a substring.

| Object | Part | Why |
| --- | --- | --- |
| `ShadeTree` | hero: trunk core, four branch modules, five leaf clumps, six roots, base dressing | a broad, round-crowned deciduous tree planted for shade; W05 owns `Oak*`, the lobby `Broadleaf*` |
| `ShadeTreeTrunkCore` | "Trunk Core": body, bosses, top socket, root stubs, knots, underside hollow | the sheet's label |
| `ShadeTreeBranchModule` | "Branch Module": BM1, the big Y with its bare fork | the label points at BM1 |
| `ShadeTreeLeafClump` | "Leaf Clump (Module)": the FL clump (the label points at the exploded's TL clump) with its stub and branch core | the label |
| `ShadeTreeRootBase` | "Root Base": the six roots with the rocks, tufts (and moss if it fits) as in the hero, without the trunk | the label |

- Palette keys `m054_*` (§5.4). Collection `Kit/M054 Broadleaf Tree`. No sockets (VFX).

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **20.0 tall, crown 20.2 × about 19.5, waist Ø 4.7, root reach 7.2–8.4** (recommended: matches 047,
   above 053's 18, leaves 057 room to be the biggest; lowest leaves at 7.8–8.2 so players walk under), or 22 (W05's
   22.5).
2. **Name (§8):** **`ShadeTree` and the four parts above** (recommended), or `Greenbough`. Not `Oak*` (W05) or
   `Broadleaf*` (lobby).
3. **Crown plan (§2.5, §3.3):** **five clumps from the top cell's plan — B back (highest, biggest), FL and FR front
   (upper), L and R at the sides (low) — with front / rear governing positions and the side judged for content**
   (recommended), or a symmetric ring that copies the side cell (no plan satisfies front, side and top at once).
4. **Limb plan (§2.4, §3.4):** **four modules: BM1 big Y → L (+ bare lower fork), BM2 short upright → FL, BM3 top V →
   B, BM4 riser → FR with its side branch → R** (recommended), or give FR its own fifth module (costs ~100 tris; the
   exploded draws four).
5. **Joints (§3.7):** **bosses and module overhangs in the hero; pegs and socket holes modelled only on the parts
   (`joints=False` in the hero)** (recommended: saves 120–180 hidden tris in a budget the leaves need), or pegs in the hero
   too (047 / 053 practice; then trim cards to 70).
6. **Branch shells (§6):** **main runs as ring-stack shells per module; arms, tines and twigs as closed shells buried ≥
   0.15** (recommended, as 053; no booleans in the crown), or weld per module with ring junctions.
7. **Bark pits:** **20–26 flat `hollow` insets (10–14 on the core, 8–12 on the modules, mostly at kinks and forks)**
   (recommended), or recessed (+80 tris).
8. **Leaf cards (§2.5):** **77 closed bicone cards of 16 tris (8-vertex, four broad rounded lobes, Ø 2.0–3.0), up to 40
   of them at 20 tris (10-vertex, five lobes) if the budget allows, over a dark solid core per clump** (recommended; the
   sheet's "leaf cards as simple chunky geometry ... layered, overlapping"), or 047-style lobed domes (cheaper, but
   047 round 1 failed them as balls and the sheet asks for cards).
9. **Side and top cells (§3.3):** **side judged for content, top for the plan** (recommended).
10. **Comparison cameras (§3.2):** **`front_sheet (0, 5)` governs positions, `f34_sheet (0, 13)` the read** (probe az
    −35 … +35, e 9–16); `rear_sheet (180, 5)`, `r34_sheet (180, 13)` (probe 145 … 215), `side_sheet (90, 5)`; kit
    `top`, `underside`; extras: parts shot (0, 22), `join_cu`, `clump_cu`, `knot_cu`, scale shot. Floor hidden in every
    `*_sheet` render.
11. **Collision (§7):** **hero, trunk core and root base `precise`; branch module and leaf clump `hull`**
    (recommended); tufts and moss walk-through only if `kit_nocollide` is already supported.
12. **Exported parts (§8):** **the hero plus the four labelled parts** (recommended), or also BM2–BM4 and the other four
    clumps.
13. **Colour (§5):** **leaves by height role to `#CDE209` / `#70A81F` / `#47852D` (canopy median `#A5C50B`); bark to
    `#985F31` with v > .7 `#E69646`; cut wood `#F1A452`; holes `#2E1806`; rock lit `#D5C1AC`; moss `#D2C90D`; grass
    `#CACE0A` / `#708F11`** (recommended).
14. **Stages 5 and 6:** **skip both, recorded** (recommended); a "falling leaves" emitter would be new to `lib/vfx.py` and
    is not on the sheet.
15. **Budget (§4.3):** **4000 limit, about 3600–3800 planned (skeleton ≈ 1650, foliage ≈ 1450, base ≈ 700), ceiling
    3800; parts under 1000** (recommended).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **Limbs hidden in the clumps (047 round 1 "stub limbs, hidden twigs"; the user's tree rule).** T above h .45 ≥ 8 % in
   the front, rear and f34 (sheet 10–12); wood fifth 4 ≥ 6 %; LOW-L, LOW-R and LEAD each ≥ 1.5 studs of bare limb in
   front, rear and f34; both bare forks visible under the side clumps; the canopy bottom gap at x .00–.10 (≥ .62 H) so
   the V leader shows; the inner droop of L and R kept up so their limbs show.
2. **Clumps as balls or blobs (047 round 1; W05 "flat blob crown").** Each clump one mound with a scalloped outline (front
   scallops 27 ± 8 round the crown), cards overlapping 30–50 %, tones ordered by height, no visible gaps to the sky
   through a clump's middle; five clumps touching in the front view with their own outlines.
3. **Spiky leaves (memory `kit-quality-bar` leaf lesson).** Cards with broad rounded lobes, never pointed stars or
   serrated edges; tuft blades broad at the base (L : W ≈ 4), not needles.
4. **Buried or floating dressing (STAGES; 035 / 036; 046; 047 round 2).** 0 floating shells; 0 cards with their centre
   inside the core or more than half inside a neighbour; 0 blades, hubs, pads or rocks more than 0.05 inside a root, toe,
   the trunk or a rock, by ray parity after the final placement; hubs ≥ 0.3 clear of root surfaces.
5. **A straight or cone trunk (047 leftover; W05 "thin straight trunk").** Six strands with V grooves 0.30–0.40 deep,
   twisted ~67° CCW, the "/" crossing on the front; waist 4.7 at z 7 between a 9.6 root-shoulder flare and the 7.7–11.9
   crotch; the bare-trunk row at h .3 ≤ 0.33 of W.
6. **Pale or olive canopy (W05 rev 6 "pale lime"; 047 plants yellow).** Canopy median within 15 of `#A5C50B`; leaf light
   60–66° saturated; mid and dark clearly green; tone shares within ±8.
7. **A knot read as a slot (047).** Oval dark recess, raised pale ring, a small hole above; the back knot with a hex rim.
8. **Floating or unseated modules (STAGES).** Every peg 0.015–0.03 from its socket walls, no peg corner inside the
   solid; every clump stub on its module tip; every tine within its parent.
9. **Colour by facing (042 ruling).** `bark_deep` only in creases and cavities; the pale knob a knuckle-shape region, not
   "faces pointing up"; card tones by height rank; `K.check` facing correlation < 0.5 per material.
10. **Flat orange or red bark (W05).** Whole median within 20 of `#985F31`, hue 24–28°, R > G > B.
11. **Egg, mauve or blue rocks (M034, M037).** Angular blocks, 8–14 broad facets, flat bases; R ≥ G ≥ B.
12. **Edge-on or needle grass (039).** Folded lanceolate blades facing the f34 and front cameras.
13. **Winding (044) and bowties.** 0 faces wound against their neighbours per shell — check every hand-built card and
    every mitred kink ring; `M.fix_bowties`; corners ≥ 3° on the core's union seams (047 left 43 under 3°).
14. **Exact booleans:** only the bosses and root stubs into the trunk body, at the origin, one at a time, saving between
    them (STAGES "Booleans"). Modules, cards, cores, pits and dressing are never unioned.
15. **Over budget from the leaves.** Count tris per clump as you go (target ≤ 300 for B, ≤ 260 for the others including
    core and branch core); cut cards before thinning the skeleton.
16. **Names and scope.** No `Oak*`, `Broadleaf*`, `GnarledPine*`, `TwistedSnag*`; only one agent drives a Blender session
    at a time; no commits, pushes or exports in stage agents; don't edit the frozen shared helpers, `m053.py` or
    `lib/vfx.py`; don't touch other models' collections.

## Decisions (main session, 2026-10-29)
All 15 recommendations are accepted.
1. **Size.** 20 tall, crown about 20.2 × 19.5. The lowest leaves sit at z 7.8–8.2, so a player can walk underneath.
2. **Names.** `ShadeTree` plus `ShadeTreeTrunkCore`, `…BranchModule`, `…LeafClump` and `…RootBase`. Keys `m054_*`, collection `Kit/M054 Broadleaf Tree`. Never `Oak*` or `BroadleafTree*`, which are already taken.
3. **Crown plan.** Five clumps, laid out from the top cell. The front and rear cells set positions; the side cell is judged for content only.
4. **Limbs.** Four modules feed five clumps, as tabled. **Each low limb and the leader must show at least 1.5 studs of bare limb** in the front, rear and f34 views (the user's tree rule).
5. **Joints.** Pegs and socket holes go on the parts only; the hero keeps the bosses and overhangs. No pale ring may show at a joint.
6. **Crown shells.** Main limbs are ring-stack runs. Tines and twigs are closed shells buried at least 0.15. No booleans in the crown.
7. **Bark pits.** 20–26 flat insets. The knots must read as holes, not slots.
8. **Leaves.** 77 lobed 16-tri cards over dark cores; up to 40 may be five-lobe cards if the budget allows. Cards overlap 30–50 % and are toned light → mid → dark by height within each clump. **No ball domes, nothing spiky, no floating or buried cards.**
9. **Views.** Side judged for content, top for the plan.
10. **Cameras.** `front_sheet (0, 5)` and `f34_sheet (0, 13)`. Probe azimuth ±35° once.
11. **Collision.** Hero, trunk core and root base precise; branch module and leaf clump hull.
12. **Exports.** The hero plus the four parts.
13. **Colour.**
    - Leaves `#CDE209` / `#70A81F` / `#47852D`, canopy median `#A5C50B`.
    - Bark `#985F31`, lit `#E69646`; cut wood `#F1A452`; holes `#2E1806`.
    - Rock lit `#D5C1AC`; moss `#D2C90D`; grass `#CACE0A` / `#708F11`.
    - Blend by position and role, **never by facing**. The canopy must not read pale or olive.
14. **Stages 5 and 6.** Skipped and recorded.
15. **Budget.** Limit 4000, ceiling 3800, every part under 1000.

**Packaging.** 0 winding errors, especially on the hand-built cards. Every shell is manifold. The trunk twists; it must not read as a cone.

**Binding.** The front shares in §1 (canopy green 47, wood 37, each ±4), and wood above h .45 at 10–12 % in every side view.
