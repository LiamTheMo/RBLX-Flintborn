# 053 Dead Tree — spec

Reference: `art/blender/assets/references/053.png` (1024 × 1536 px). INDEX.md row 53: "Flintborn dead tree asset study".
The sheet's own header reads **"55 / 132 DEAD TREE"** with "FLINTBORN — INDIVIDUAL MODEL STUDY" under it (the page number
on the sheet is 55; our numbering is INDEX's 053, §3.1). Top right: "STYLIZED ENVIRONMENT ASSET" and four labelled
swatches (WOOD DARK, WOOD MID, ROCK, FOLIAGE). Footer "FLINTBORN — INDIVIDUAL MODEL STUDY".
Builder: `art/blender/kit/mcp/m053.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session puts the model
into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows no effect** (§7). Trees: "a
detailed skeleton plus foliage clumps; roots, branches and every view matter" (memory `kit-tree-detail`). **A dead tree
is that skeleton with nothing in front of it: the trunk, six plug-in branch modules, six roots, their kinks, forks, cut
ends and bore holes are the whole model, seen against the sky from every side and from above.** It has to be the best
skeleton in the kit.

Sheet text (paraphrased where long):
- **Description (top):** bare branches with angular forms; "Fallen and snapped"; a chunky, readable silhouette from
  simple broad shapes and clean topology.
- **1. "ASSEMBLED VIEW (FRONT THREE-QUARTER)"**, **2. "ASSEMBLED VIEW (REAR THREE-QUARTER)"**.
- **3. "ORTHOGRAPHIC VIEWS (CONSISTENT MODEL)":** "FRONT VIEW", "SIDE VIEW", "REAR VIEW", "TOP VIEW". They are not
  fully consistent (§3.3, §3.4).
- **4. "PARTS (EXPLODED VIEW)":** labels "BRANCH MODULE A", "BRANCH MODULE B", "BRANCH MODULE C", "ROOT MODULE A",
  "ROOT MODULE B", "ROOT MODULE C", "TRUNK CORE". Six branch modules are drawn (A, B, C on the left; three unlabelled on
  the top and right), four root modules (A, B, C and one unlabelled front-left), dashed arrows from every module's peg
  to a socket or stub on the trunk core.
- **5. "CONSTRUCTION CLOSE-UPS":** "BRANCH JOIN (PEG & SOCKET)" and "UNDERSIDE VIEW (ROOT JUNCTION)".
- **6. "MATERIAL PALETTE & MODEL NOTES":** WOOD DARK "Main trunk shadow planes and deep creases"; WOOD MID "Primary wood
  surface"; ROCK "Simple faceted rock, pale and clean"; FOLIAGE "Low, chunky grass clumps at base". Notes (paraphrased):
  modular construction (trunk core, branch modules, root modules); clean low-poly topology with broad flat-shaded
  faces; reusable branch and root modules with consistent join shapes; chunky shapes and a readable silhouette; the
  model matches the orthographic views.
- **Game context and the old kit:**
  - **W05 row 3 `DeadTree`** (`art/blender/scripts/kit/W05/dead_tree.py`, goals
    `art/blender/renders/kit/W05/dead_tree_goals.md`, compare `dead_tree_compare.png`) is the old kit's take on a
    similar reference row: 18 × 18 × 24, eight strand limbs, six roots, three variants. `MODEL_PROGRESS.md` row 63:
    "thick straight branches; block trunk; variants similar". Its compare image shows a thin-limbed fan on a cone trunk.
    **W05 owns every `DeadTree*` name and `DeadBranchModuleA/B`, `DeadTrunkBase`** (§8).
  - **Sister sheets:** 047 Old Pine (`GnarledPine`, 20 tall, committed) is the closest skeleton pattern (plug-in limbs,
    buttress roots, hollows). 054 broadleaf, 055 fallen log and 057 ancient tree come next. §1.5 lists what keeps 053
    apart.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Paper `#FAF7F0` (250, 247,
240), tolerance 12. Cell rules (measured grey lines): rows y 99 / 557–559 / 834–837 / 1490; columns x 12 / 511 / 1011;
ortho dividers x 264 / 511 / 759; exploded | close-ups x 663; close-up and palette frames y 1216–1219, 1371.
- **Cells** (`m.V`, `m.X`): f34 (16,125,508,553); r34 (515,125,1008,553); front (16,595,262,805); side (267,595,509,805);
  rear (514,595,757,805); top (762,595,1008,805); exploded (16,862,660,1486); close-up 1 "branch join" (672,868,1004,1012);
  close-up 2 "underside" (672,1026,1004,1182).
- **Swatches:** palette section 6 (688,1258,714,1276) wood dark, (688,1289,714,1303) wood mid, (688,1315,714,1329) rock,
  (688,1341,714,1356) foliage; the header legend repeats them at x 857–885, y 13–25 / 33–47 / 55–68 / 76–89.
- **Masks** are `cls()` in `m.py` (HSV, h in degrees, assigned in this order):
  - **X, cast shadow:** (s < 0.07, v ≥ 0.80) or (s < 0.10, v ≥ 0.72, B ≥ R − 2) or (h 200–250, s < 0.15, v ≥ 0.70). The
    sheet draws a lavender ground shadow to the left of every view.
  - **G, green:** h 50–180, s ≥ 0.30, v ≥ 0.12 (grass tufts and the lime moss ground).
  - **T, wood:** h < 48, s ≥ 0.30, v ≥ 0.12 (trunk, limbs, roots, cut faces).
  - **R, rock:** s < 0.30, v 0.22–0.95. About 1–1.5 points of each view's R sit above h 0.3: desaturated shade facets
    on the wood and the halo, not rock.
  - **O, other:** outlines, bore holes, the darkest creases.

**Scratch study material** (no Blender) in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m053_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14, Pillow, numpy; no scipy / skimage).
- **Helpers:** `m.py` (masks, boxes, `silhouette()`, `preview()`), `zoom.py` (`zoom.py x0 y0 x1 y1 scale out.png
  [grid]`), `comps.py` (`label()`, connected components; `comps.py front rear f34` lists rock and plant blobs).
- **Measurements:** `measure.py` (bbox, W : H, shares, fill, profiles, fifths), `trunk.py` (central wood run per height),
  `width.py` + `wpts.py` / `wroots.py` (distance-transform widths at named points), `polar.py` (arm count round the top
  view's centre), `dots.py` (dark specks), `samp.py` / `samp2.py` / `samp3.py` (colour per region, cut faces, holes,
  moss vs blades), `sw.py` (swatches), `lines.py` / `lines2.py` (cell rules).
- **Zooms:** plain `p_f34.png`, `p_r34.png`, `p_front.png`, `p_side.png`, `p_rear.png`, `p_top.png`, `p_f34trunk.png`,
  `p_f34crownL.png`, `p_f34crownR.png`, `p_expl.png`, `p_core.png`, `p_branches.png`, `p_roots.png`, `p_cu.png`;
  gridded (10 px sheet grid, labels every 50) `z_f34.png`, `z_r34.png`, `z_front.png`, `z_side.png`, `z_rear.png`,
  `z_top.png`, `z_ortho.png`, `z_expl.png`, `z_cu.png`, `z_pal.png`, `z_legend.png`; mask previews `cls_*.png`,
  `cls_mont.png`.
- **On our renders:** copy 047's `measure_render.py` and point it at `m.py` here (same masks, paper `#FAF7F0`).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset, a standalone dead tree with its own base dressing (no ground patch, §2.5). Hero budget
  4000 tris, each part under 1000. The plan in §4.3 lands at about 3000–3400.
- **Overall read (check this first).** A **bare, dead, chunky tree**: a **massive, twisted, orange-brown trunk** of
  rope-like strands faceted into long bark planks (waist Ø ≈ 0.28 H), **flaring into six thick roots** that arch down
  onto the ground and end in **split, blunt toes**; at about half height the trunk **throws out six chunky limbs**
  (one up the middle, the rest round the sides), each built of **straight faceted segments with hard angular kinks**,
  forking once or twice and ending in **short, blunt, square-cut tines**; **dark bore holes** pit every limb, root and
  the trunk (mostly at kinks and forks); a big **oval knot hole with a pale rim** on the front-right of the trunk; one
  **snapped limb end** with a pale broken face. Round the foot: **pale grey angular rocks** (two tall ones behind, low
  ones in front), **lime grass tufts** and **flat lime moss** between the roots. No leaves anywhere on the tree.
  - It reads **wood first and only**: wood is 77–79 % of every side view's silhouette, green 8 %, rock 11–12 %.
  - The crown is as wide as the tree is tall (W : H 0.97 front, f34 and rear), round in plan (top W : D 1.02), a
    **nine-armed star from above** round a cut trunk top.
- **Focal silhouettes, in order:**
  1. The trunk's mass and twist: a wide root flare, a waist at h .35–.40, the crotch at h .50 where the limbs leave.
  2. The six limbs against the sky: the thick left limb sweeping out then up, the central V leader, the up-left limb,
     the right limb rising then forking; 11–15 blunt tine ends in each side view.
  3. The kinks: every limb changes direction 1–3 times at a hard elbow, never a smooth curve.
  4. The roots splaying to the ground with split toes; the base dressing between them.
- **Target size: 18.0 tall (highest tine tip), crown 17.6 wide (X) × about 15 deep, trunk waist Ø 5.0 at z 6.3–7.2,
  root reach r 7.2–8.1** (decision §8.1). Tolerances: height ±0.4, crown width 17.6 ± 0.8.
  - **How it was derived.** The front cell's silhouette is 203 × 208 px (H = 208, ground at y 803), so 11.56 px / stud
    at H 18; the f34's 406 × 418 px gives 23.2 px / stud. Widths per height (`trunk.py`, `wpts.py`, fraction of H):

    | Feature | f34 | r34 | front | side | rear | adopted (studs) |
    | --- | --- | --- | --- | --- | --- | --- |
    | Root flare incl. root shoulders, h .20 | .555 | .549 | .519 | .469 | .546 | 9.4–9.9 at z 3.6 |
    | Flare top, h .25 | .414 | .409 | .380 | .353 | .396 | 7.0 at z 4.5 |
    | Trunk, h .30 | .292 | .328 | .308 | .300 | .329 | 5.4 at z 5.4 |
    | **Waist, h .35–.40** | .273–.285 | .275–.294 | .284–.293 | .246–.275 | .290–.295 | **Ø 5.0 at z 6.3–7.2** (DT centre width .262 = 4.7) |
    | Below the crotch, h .45 | .325 | .289 | .308 | .251 | .314 | 5.6 at z 8.1 (limb collars start) |
    | Crotch, h .50 (limbs leaving) | .486 | .395 | .385 | .444 | .551 | 7–9.9 across the collars at z 9 |
    | Limb base Ø (DT) | | | LM .117, R .102, C .089 | SL .117, SR .089 | .074–.103 | 1.6–2.1 |
    | Limb mid / elbow Ø | | | .065–.079 | .059–.065 | .043–.078 | 1.0–1.4 |
    | Tines Ø | | | .019–.035 | | | 0.4–0.6 |
    | Root Ø near trunk / mid / toes | | | .12 / .08–.12 / .04–.07 | | | 2.2 / 1.4–2.0 / 0.6–1.1 |

  - **Why 18.** 047 Old Pine is 20 with a 6.2 trunk; the dead tree should sit a little under it, and 054 broadleaf
    and 057 ancient tree come next (the ancient tree must be the biggest). At 18 the sheet's proportions give a 5-stud
    waist (two and a half characters wide), limbs that leave the trunk at z 8.4–9.6 (well above a 5.5 character's
    head, so players walk under the low limbs and between the roots), root shoulders at z 4–4.5 (chest high where they
    meet the trunk, ankle high at the toes) and rocks 0.9–3.8 tall. Smaller (16) puts the low limbs at 7.5, a jump
    from the roots; larger (22–24, W05's size) makes the tall rocks 4.6+ and the trunk wider than 047's.
  - **Against the character (5.5):** the tree is 3.3 C tall; the crotch at 1.6 C; the lowest tine (L1, z 8.5) at 1.5 C;
    the roots reach 1.4 C out from the axis.
- **Build frame:** front −Y, +X right, ground z 0. Trunk axis at (0, 0), **upright** (the central run's centre moves less
  than ±0.03 H up to h .45 in every view: no lean). Origin = bbox bottom centre; the crown runs about −8.3 … +8.6 in X,
  so the origin sits about +0.15 X of the trunk axis (record it).

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | T | G | R | O | fill |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (16,125,508,553) | 67–472 × 126–543 (406 × 418) | **0.971** | **78.0 %** | 7.9 | 12.2 | 1.8 | 0.437 |
| Rear three-quarter (515,125,1008,553) | 564–954 × 135–542 (391 × 408) | 0.958 | 78.2 | 8.0 | 11.5 | 2.3 | 0.420 |
| Front (16,595,262,805) | 42–244 × 596–803 (203 × 208) | 0.976 | 77.1 | 8.6 | 11.7 | 2.6 | 0.432 |
| Side (267,595,509,805) | 298–473 × 596–802 (176 × 207) | 0.850 | 78.3 | 7.5 | 11.2 | 2.9 | 0.409 |
| Rear (514,595,757,805) | 532–733 × 597–803 (202 × 207) | 0.976 | 79.2 | 7.7 | 10.5 | 2.5 | 0.435 |
| Top (762,595,1008,805) | 782–989 × 597–801 (208 × 205) | 1.015 (W : D) | 73.0 | 12.1 | 13.2 | 1.6 | 0.404 |

- Shares are of the silhouette (O included, X excluded). **Fill** = silhouette pixels / bbox area: it measures how
  thick the skeleton is against the sky (thin twigs drop it fast). 0.41–0.44 in every view.
- **Verifier tolerance:** T ±4, G ±3, R ±3 points; W : H ±0.06; fill ±0.04 (binding, §9.1); positions ±0.04 of H.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.1 W): the crown's top edge is a row of
separate peaks (tine groups) with dips between, never a smooth dome.

| f | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .49 | .75 | .90 | .89 | .78 | .75 | .91 | .95 | .79 | .88 | .11 |
| r34 | .68 | .78 | .92 | .88 | .68 | .84 | 1.0 | .64 | .80 | .87 | .75 |
| Front | .52 | .77 | .82 | .91 | .78 | .74 | .90 | .95 | .77 | .86 | .69 |
| Side | .05 | .65 | .72 | .95 | .91 | .70 | .90 | .94 | .68 | .82 | .04 |
| Rear | .68 | .84 | .75 | 1.0 | .90 | .75 | .79 | .92 | .80 | .69 | .75 |

**Width per height** (silhouette width at h .0 → 1.0 as a fraction of W):

```
f34    .34 .95 .85 .40 .30 .64 .51 .94 .68 .74 .02
r34    .03 .89 .72 .37 .29 .50 .60 .84 .81 .68 .01
front  .49 .91 .77 .32 .30 .65 .72 .88 .68 .42 .02
side   .60 .91 .71 .36 .30 .54 .60 .80 .57 .39 .02
rear   .49 .92 .76 .34 .31 .57 .56 .93 .75 .42 .46
```

- Reading (front): h .1 the roots and base dressing at full width; h .2 the flare; **h .3–.4 the bare trunk only
  (.30–.32 of W): keep it**; h .5 the low limbs leave; h .6–.7 the crown at its widest (the L and R limb tips); h .8–.9
  the upper tines; 1.0 the leader and TL tips.

**Height fifths** (bottom → top, % of each class):
- f34: T 26.0 / 21.1 / 23.5 / 22.0 / 7.4; G 91.9 / 8.1 / 0 / 0 / 0; R 62.7 / 26.4 / 4.5 / 3.7 / 2.7.
- Front: T 26.3 / 20.8 / 24.2 / 21.9 / 6.8; G 95.4 / 4.6 / 0 / 0 / 0.
- Rear: T 27.5 / 20.7 / 23.9 / 21.1 / 6.8. Side: T 29.1 / 22.7 / 24.3 / 18.2 / 5.7.
- **Wood is spread evenly through four fifths**: the crown's limbs are as heavy, in pixels, as the trunk. A thin crown
  drops fifths 3–4 below 15 %.

**Ground dressing blobs** (`comps.py`; x as a fraction of H from the axis, h fraction of H; studs at 18):

| View | Rocks | Plants |
| --- | --- | --- |
| Front | tall back-left x −.39…−.27, top h .236 (W 2.1, top 4.2); low front-left −.33…−.19, h ≤ .115 (2.5 × 2.0); front-centre −.07…+.04, h ≤ .087 (2.0 × 1.6); small front-right +.24…+.30 (1.1); tall back-right +.26…+.38, top h .255; pebbles at −.36, +.10 | far-left tuft −.47…−.37 (1.8 wide, h ≤ .14); left −.26…−.13; front-centre moss and sprigs −.15…+.04; right-centre +.19…+.24; back-right +.22…+.26 (behind, h .20–.26); big right tuft group +.30…+.48 (3.1 wide, 2.4 tall) |
| Rear (mirrored: rear −x is world +X) | tall left −.38…−.27 top .242; centre −.18…−.02 (2.8 × 2.0); right +.17…+.25; tall right +.28…+.40 top .232 | far left (world +X) −.48…−.31; centre −.06…+.06; right +.19…+.36; far right +.39…+.48 |
| f34 | tall left (106–158, 438–503) 2.2 × top 4.5; big low front-left (126–203, 492–538) 3.3 × 2.0; front-centre (249–307) 2.5 × 1.6; right-front (370–398) 1.2; tall right-back (375–433, 420–472) 2.5 × top 4.2; pebbles | left tuft (83–116) 1.4 × 1.7; front-left tuft (174–225) 2.2 × 1.7; centre sprigs; right tuft groups (353–414) and (398–457) 2.5 × 2.2 |

**Plan (top cell, `polar.py`, `p_top.png`).** Round the trunk top's centre (882.5, 701), a scan at r 0.40 H finds **nine
arms** at about 15°, 58°, 104°, 129°, 168°, 204°, 247°, 292° and 336° (sheet up = +Y, gaps 26–45°), each 18–21° wide at
r 0.30 H (Ø ≈ 1.7–2.0) and splitting into two tines at r 0.45–0.50 H. The trunk top shows as a 10–12-sided faceted cap
with a **pale cut disc** (`#F9C984`) and a **small dark square socket** (`#433013`) at its centre. Grey rocks and green
clumps show between the arms within r ≈ 0.35 H.

### 1.3 Silhouette and composition per view

**Front three-quarter (`p_f34.png`, `p_f34trunk.png`, `p_f34crownL/R.png`) — governs with the front cell.** Drawn
almost frontal (the knot, the root tips and every limb tip sit within 0.02 H of their front-cell positions, §3.2) and
from higher (e ≈ 10–14°: the ground band is twice as deep). Lit from the right (wood right half `#C57035`, left
`#855633`); cast shadow to the left.
- **Trunk:** three or four **rope-like strands** twist round each other; on the front face the lit strand climbs from
  the front-left root **up and to the right** ("/") into the leader, and the strand from the right root climbs up-left
  into the thick left limb, so the grooves cross in an X at h .3–.45. Each strand is faceted into long narrow planks
  (2–3 facets across a strand), with deep dark grooves between strands.
- **Knot hole** on the front-right (sheet (322, 380), h .39): a dark oval (0.5 × 0.75 studs) in a **raised pale rim**
  (outer 0.8 × 1.3), with a **small round pale cut boss** (Ø 0.5) just below it. A second, smaller hole with a pale rim
  sits on the front root's top at h .23.
- **Limbs** (`p_f34crownL/R.png`): each a chain of **straight 5–6-sided prisms**, broad flat facets, hard kinks; at
  each kink and fork a dark square pit; tines short (1–2 studs) and **blunt with flat square-cut ends**, some ends dark
  (hollow).
- **Base:** roots arch from the flare to the ground, toes split; a tall pointed rock behind each side; low rocks in
  front; lime tufts (pointed blades) left, front and right; lime moss strips on the ground.

**Rear three-quarter (`p_r34.png`).** The same tree from behind: the left limb (world −X) now on the right with its
two side branches and its upper stem, the right limb on the left, the leader and TL up the middle, roots and rocks
mirrored. Strand twist and holes as in front.

**Front, side and rear cells (`z_front.png`, `z_side.png`, `z_rear.png`).** Low views (e ≈ 3–6°: the root tips at
the back sit only 0.7 stud higher on screen than the front ones) at one scale (207–208 px tall). **Front and rear
agree** (mirrored; §1.4 table). The side shows four limb masses (two spreading out each side at h .5–.8, two tall ones
up the middle to h .98), W : H 0.85: §3.3.

**Top (`p_top.png`, `z_top.png`).** A nine-armed star of chunky limbs radiating from the trunk top (the pale cut disc
with the square socket at the centre), each arm forking into two blunt tines; rocks and grass between; shadow
lower-right. §3.4.

**Branch join (close-up 1, `p_cu.png` top).** A limb end: an **8-sided prism with a flat cut end face** (a lighter
cut rim, `#DA8239`) from which a **rectangular pale peg** (about 0.35 × 0.35 of the limb Ø in section, 0.5 Ø long,
light `#FAC882`) sticks out; dashed arrow to the trunk, where a **raised socket collar** (a short stub with a flat cut
face) holds a **dark oval socket** (`#1A0E07`). Beside it on the trunk, a **round knot hole with a thick pale raised
ring** (`#F6BE70`, interior `#241308`).

**Underside (close-up 2, `p_cu.png` bottom).** Looking up at the root junction: the trunk's **flat bottom is a
12-sided disc** in wood dark (`#865633`) with a **chamfered rim band** (light on its lit edge, `#E89B52`) and a **small
pin hole** at the centre; **six thick roots** radiate from round it, faceted prisms with plank facets; rocks between.

### 1.4 Parts (exploded, `p_expl.png`, `p_core.png`, `p_branches.png`, `p_roots.png`)

The exploded is an elevated front view (e ≈ 20–25°). Its trunk core is 308 px from the top rim to the front root's
end; at the hero's core height (11.9, §2.2) that is 25.9 px / stud. Branch module A is 5.7–5.9 studs long, its base Ø
1.7: close to the hero's left limb. **The hero governs every size and height** (§3.5); the parts give shapes, counts and
joints.

| Part (label) | Box (px) | Notes |
| --- | --- | --- |
| Trunk core | (300–415, 1040–1353) | a **tapered faceted column** (top Ø ≈ 0.19 of its height, mid ≈ 0.34), planked, with a **round hollow top** (a socket ring, rim `#CC7234`); a **big oval knot hole** with a raised rim on the front-right at 0.6 of its height (`#341B09` inside); 15+ small dark bore dots; a **flared foot** with **five stubs** (left, right, front-left, back-left, back-right: short faceted root starts ending in flat cut faces, three of them with pegs) and **one built-in front root** that runs down to the ground and ends in a flat 6-sided foot |
| Branch Module A | (150–315, 865–1010) | the **big Y**: a thick base (Ø 1.7) with a peg, one fork: a long main stem rising to a two-tine tip and a long side branch out to the left ending in a small fork; 5–6 bore holes |
| Branch Module B | (150–275, 975–1075) | a **kinked limb** (two kinks) ending in a two-tine Y, a small spur at the first kink |
| Branch Module C | (110–275, 1075–1150) | the **comb**: a near-horizontal limb with two short side twigs and a forked tip |
| Top module (unlabelled) | (345–435, 862–995) | a short thick base (peg down) splitting into a **V** of two upward tines and a small spur: the leader |
| Upper-right module (unlabelled) | (400–560, 885–1050) | a **long rising limb** with a side branch out to the right that forks; the longest module |
| Right module (unlabelled) | (430–585, 1015–1100) | a near-horizontal limb ending in a **Y-fork** of two tines |
| Root Module A | (40–235, 1225–1380) | long, thick (Ø ≈ 2), tapering, faceted planks; peg at its high inner end; it slopes down and **splits into three blunt toes** |
| Root module (unlabelled, front-left) | (170–300, 1335–1470) | medium, **two toes** |
| Root Module B | (410–520, 1330–1460) | medium, **two toes**, dark holes on the toe ends |
| Root Module C | (480–640, 1225–1350) | long, **three toes** |

#### Trunk core — exploded, close-ups 1 and 2, hero
- **Shape:** a twisted, planked column of six rope strands (§2.2), flared at the foot; a waist at z 6.3–7.2; collars
  for five side sockets round the crotch and a top socket; stubs for five root modules plus one built-in front root;
  the knot and a second small hole; 10–14 bore pits; a flat 12-sided underside with a chamfer rim and a centre pin.
- **Hero size:** Ø 6.4 at z 0 (body, before the roots), 5.6 at z 3.6, 5.0 at z 6.3–7.2, 5.2 at z 8.1, 3.8 at z 10.0,
  2.6 at the top (z 11.9). Part about 9.5 × 9.5 × 11.9 with the stubs.

#### Branch modules (six) — exploded, close-up 1, hero
- **Shape:** straight prism segments (main limbs 6-sided, side branches 5, tines 4: square, chunky), hard kinks, a flat
  cut base face with a lighter rim and a square pale peg; forks with dark pits in the crotch; tines 1.0–2.2 long, blunt,
  flat-ended, about half of the ends dark (hollow). One module (A on the hero) has a **snapped end**: a jagged pale
  broken face where the upper stem stops short.

#### Root modules — exploded, close-up 2, hero
- **Shape:** a thick tapering prism (6-sided, plank facets, a ridge along the top), one kink where it meets the ground,
  then a low run along the ground that **splits into 2–3 blunt toes** (Ø 0.6–0.8, 0.7–1.0 long, flat dark-ended); a
  square peg at the inner end into its stub.

### 1.5 How 053 differs from 047 Old Pine and W05 `DeadTree` (binding: the verifier checks these)

| | 047 Old Pine (`GnarledPine`) | W05 `DeadTree` (old kit) | **053 Dead Tree** |
| --- | --- | --- | --- |
| Size | 20 tall, canopy 20.3 × 12 | 23.6 tall, 19.5 wide | **18 tall, crown 17.6 × ≈ 15, W : H 0.97** |
| Silhouette | five green pads with sky between, T 38 % | a thin-limbed fan on a cone | **bare wood only: T 78 %, fill 0.43; 11–15 blunt tine ends per view** |
| Trunk | Ø 6.2, planked, leaning 7–8°, forked | twisted strands, reads as a smooth cone | **Ø 5.0 waist, upright, six twisted rope strands with an X of crossing grooves, flare to 9.9** |
| Limbs | five elbowed limbs to foliage pads | eight strand limbs, pointed antler tines | **six plug-in modules (V leader, big Y, kinked B, comb C, long riser, Y-fork) of straight prisms with hard kinks; blunt square-cut tines** |
| Roots | seven buttress roots on sand | six strand roots | **six root modules / stubs arching to the ground, ending in 2–3 split toes** |
| Joints | hexagonal sockets with hollow plugs | none (one mesh) | **raised socket collars + square pale pegs**; flat 12-sided underside with a pin |
| Holes | a knot, two hollow stubs | 2–3 knot holes | **40–55 small dark bore pits + an oval knot with a pale rim and boss + one snapped pale end** |
| Top view | rosettes round a limb star | 8 spokes and a hub knot | **nine-armed star round a pale cut disc** |
| Ground | sand patch | moss mounds, pebbles | **no patch: lime moss pads and pointed lime tufts between the roots, pale grey rocks (two tall behind)** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, trunk axis at (0, 0)). Plan azimuths: 0° = +X, counter-clockwise,
90° = +Y (back), 270° = −Y (front).

### 2.1 Stack (binding contact chain, bottom up; every seat gap 0.015)

| Piece | Sits on / in | Contact |
| --- | --- | --- |
| Trunk core (one closed shell: body, collars, stubs, front root) | ground | flat 12-sided bottom at z 0 (no sink needed: the kit ground is a plane); the built-in front root's toes at z 0 |
| Root modules (6) | their stubs and the ground | square peg into the stub's socket 0.30 deep, 0.02 clearance; the module's base face 0.015 off the stub's cut face and **0.02 wider all round** (it hides the stub face, §6); toes sunk 0.05 into z 0 |
| Branch modules (6) | their collars | peg into the collar socket 0.30 deep, 0.02 clearance; base face 0.015 off the collar face, 0.02 wider all round |
| Side branches, tines, spurs inside a module | their parent segment | either part of the module's shell (ring-stack junction) or closed shells buried ≥ 0.15 in the parent (decision §8.6) |
| Rocks, pebbles | ground | sunk 0.10 / 0.04 |
| Moss pads | ground | z 0 … 0.08–0.12, sunk 0.02 |
| Tufts | ground or a moss pad | hub sunk 0.03; every blade within 0.03 of its hub |

### 2.2 Trunk core

| Ring z | 0 | 1.0 | 2.4 | 3.8 | 5.2 | 6.6 | 8.0 | 9.2 | 10.4 | 11.9 (top) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Body Ø (strand crests) | 6.4 | 6.1 | 5.8 | 5.5 | 5.2 | 5.0 | 5.1 | 4.6 | 3.6 | 2.6 |
| Twist (strand azimuth offset) | 0° | 6° | 14° | 22° | 30° | 38° | 46° | 52° | 58° | 62° |

- **Section:** **six strands**, each three facets wide (18 sides); the vertex between two strands pulled in 0.30–0.40
  (a deep V groove), the strand's middle facet proud 0.06–0.12, alternating strands 8–12 % thicker. Strand azimuths at
  z 0 are the six root azimuths (§2.3): **each root continues up as a strand**, and each strand feeds a limb collar at
  the top.
- **Twist:** counter-clockwise seen from above (azimuth increases going up), about 60° from the foot to the top. On the
  front face this makes the grooves climb **lower-left → upper-right ("/")**, as the f34 and front cells show. Rings
  stay broad: no ring finer than these ten.
- **Top:** the top ring (z 11.9) carries a flat cut face, a 10–12-sided cap Ø 2.6 with a pale cut rim; the **top
  socket** in it (square hole 0.62 × 0.62 × 0.35 for the leader's peg).
- **Socket collars (5)** for the side modules, each a short stub rising out of a strand pair, **flat cut face**
  (pale rim 0.15 wide), a square socket 0.30 deep at its centre:

  | Socket | Face centre | Axis (az, rise above horizontal) | Collar Ø | Peg hole | Takes |
  | --- | --- | --- | --- | --- | --- |
  | S_LM | (−2.55, −0.45, 8.8) | 190°, 25° | 2.2 | 0.75 sq | Branch A (LM) |
  | S_L1 | (−2.55, 0.68, 8.4) | 165°, 25° | 1.5 | 0.55 sq | Branch C (L1) |
  | S_R | (2.25, 0.60, 9.4) | 15°, 60° | 2.0 | 0.70 sq | upper-right module (R) |
  | S_FR | (0.84, −2.10, 9.6) | 292°, 20° | 1.7 | 0.60 sq | right module (FR) |
  | S_TL | (−1.30, 0.75, 11.2) | 150°, 50° | 1.3 | 0.48 sq | Branch B (TL) |
  | S_TOP | (0.2, 0.2, 11.9) | up, tilted 10° toward 58° | 2.6 face | 0.62 sq | top module (leader) |

  Collars protrude 0.35–0.55 beyond the strand crest; they are what makes the crotch wide (7–9.9 across at z 9).
- **Root stubs (5) and the built-in front root:** at the foot, each a short faceted prism leaving a strand at z 0.6–2.6,
  axis down-out 25–35°, ending at r 3.6–4.0 in a flat cut face (Ø 2.0–2.3) with a square socket for the root module's
  peg. The **built-in front root (RT3)** is part of the core: it runs on to its toes (§2.3).
- **Knot (front-right):** centre on the trunk surface at (2.1, −1.36, 6.9) (az 327°): an oval recess 0.55 × 0.8, 0.35
  deep, inside a **raised pale rim** (outer 0.85 × 1.3, raised 0.08); a **round pale boss** Ø 0.5 proud 0.12 just below
  it at z 6.2. It must read as a **round dark hole with a pale ring** at cell scale, not a slot (047 leftover).
- **Second hole:** on RT3's top at (1.4, −2.6, 4.1): a round recess Ø 0.4 in a pale rim Ø 0.65.
- **Underside:** the flat bottom is a 12-sided disc Ø ≈ 5.6 with a 0.2 chamfer ring and a centre pin hole Ø 0.25 × 0.1
  (close-up 2).

### 2.3 Roots (six)

| Root | Module | Azimuth | Reach r (toe tips) | Ø at stub → mid → toes | Toes | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| RT1 | Root A | 185° | 8.1 | 2.2 → 1.4 → 0.7 | 3 | front tip x −0.45 H; rear far right |
| RT2 | Root B (the exploded's unlabelled front-left) | 240° | 7.6 | 2.0 → 1.4 → 0.7 | 2 | front tip x −0.21 H; side front tip |
| RT3 | built into the core | 300° | 7.6 | 2.4 → 2.0 → 1.1 | 2 | front tip x +0.21 H (the thick front root, DT 2.1 mid); exploded front root |
| RT4 | Root C | 355° | 7.9 | 2.2 → 1.4 → 0.7 | 3 | front tip x +0.40 H; rear far left x +0.47 H |
| RT5 | Root B (second instance) | 55° | 8.1 | 2.0 → 1.3 → 0.7 | 2 | rear x +0.285 H; side back tips |
| RT6 | Root A (second instance) | 115° | 7.7 | 2.0 → 1.3 → 0.7 | 3 | rear x −0.16 H; side back tip y +0.415 H |

- **Profile:** each root's top ridge leaves its strand at z 4.0–4.6 at r ≈ 2.6, arches down over 2.0–2.6 of reach
  (the buttress), touches the ground at r 4.0–4.6 with **one kink**, then runs low (top 0.9–1.3 above the ground) to
  the toes. Section 6-sided: a top ridge, two upper flanks, two lower flanks splayed onto the ground, a flat bottom.
- **Toes:** 2–3 blunt prisms (4–5-sided, Ø 0.6–0.8, 0.7–1.0 long) splayed 20–30° apart, flat end faces (dark on about
  half of them), sunk 0.05.

### 2.4 Branch modules (six) and their limbs

Waypoints are segment ends (straight segments between them; each waypoint is a hard kink). Ø per waypoint. Tines are
4-sided, flat-ended.

| Limb | Module | Socket | Waypoints (x, y, z) → | Ø | Tines / spurs (tip (x, y, z)) |
| --- | --- | --- | --- | --- | --- |
| **LEAD** (leader) | top module, the V | S_TOP | P0 (0.2, 0.2, 11.9) → P1 (0.6, 0.6, 13.6) → fork P2 (1.1, 1.2, 15.2) | 1.7 → 1.4 → 1.1 | right tine via (1.9, 2.4, 16.4) to (2.7, 3.3, 18.0) (the highest point); left tine via (0.8, 1.3, 16.2) to (0.6, 1.5, 17.0); spur from (2.0, 2.5, 16.5) to (3.4, 2.8, 16.9) |
| **TL** (up-left) | Branch B, the kinked | S_TL | (−1.30, 0.75, 11.2) → P1 (−1.7, 1.0, 12.6) → elbow P2 (−3.1, 1.8, 15.9) → fork P3 (−4.2, 2.4, 17.0) | 1.3 → 1.15 → 0.9 → 0.7 | tines to (−4.7, 2.7, 17.6) and (−4.9, 2.1, 16.9); spur at P2 to (−3.4, 2.6, 16.6) |
| **LM** (left major) | Branch A, the big Y | S_LM | (−2.55, −0.45, 8.8) → elbow P1 (−4.5, −0.8, 10.0) → P2 (−4.8, 1.5, 11.6) → J (−5.0, 2.3, 12.2) → P3 (−5.2, 4.6, 13.4) → **snapped end** (−5.4, 6.4, 14.4) | 2.1 → 1.5 → 1.25 → 1.15 → 0.95 → 0.8 | side branch L2 from J: E (−6.6, 0.2, 12.9), tines to (−7.3, −0.8, 13.9) and (−7.8, −1.6, 12.8), Ø 0.85 → 0.6 → 0.45 |
| **L1** (low left) | Branch C, the comb | S_L1 | (−2.55, 0.68, 8.4) → P1 (−4.7, 1.2, 9.6) → elbow P2 (−7.0, 1.6, 9.7) | 1.3 → 0.95 → 0.7 | tines to (−8.1, 1.9, 10.8) and (−8.3, 1.4, 8.5); comb twigs from (−5.6, 1.4, 9.7) to (−5.9, 2.0, 10.9) and from (−6.3, 1.5, 9.7) to (−6.5, 2.6, 9.0) |
| **R** (right) | upper-right module, the long riser | S_R | (2.25, 0.60, 9.4) → elbow P1 (4.0, 1.0, 13.1) → fork P2 (6.1, 0.9, 13.5) | 1.9 → 1.3 → 1.0 | up branch via (6.8, 1.6, 14.8) to (7.4, 2.0, 15.9) + a short tine (7.0, 2.4, 16.2); right branch via (7.4, −1.5, 13.1) to tines (8.3, −3.7, 12.8) and (8.6, −2.4, 12.1) |
| **FR** (front-right) | right module, the Y-fork | S_FR | (0.84, −2.10, 9.6) → P1 (1.9, −4.8, 10.6) → fork P2 (2.6, −6.8, 11.6) | 1.6 → 1.15 → 0.85 | tines to (3.2, −7.9, 12.9) and (3.8, −7.4, 11.3) |

- **Branch-by-branch from the sheet** (front cell, sheet px → studs at 11.56 px / stud, x from the axis, z above the
  ground; angles are screen angles above horizontal; lengths projected):

  | Limb | Leaves the trunk | Segments (angle, projected length) | Kinks | Ends | Ø base → end |
  | --- | --- | --- | --- | --- | --- |
  | LM | (−1.6, 8.8), from the left of the crotch | out-left 25° (3.1) → up 87° (3.6) → up-left 70° (0.9) | 2 (62° then 17°) | snapped pale end at (−5.4, 14.4); side branches L2 at z 12.4 and (behind it) L1 | 2.1 → 0.7 |
  | L2 (on LM) | (−5.3, 12.4) | out-left 17° (1.8) | 1 | Y of two tines: up 74° to (−7.4, 13.9), level to (−7.9, 12.8) | 0.8 → 0.4 |
  | L1 | appears from behind LM at (−4.7, 9.8) | level 0° (2.6) | 1 | Y of two tines: up-left 50° to (−8.1, 10.8), down-left −48° to (−8.3, 8.5); two comb twigs | 0.95 → 0.5 |
  | TL | (−0.8, 12.6), the top of the column | up-left 57° (3.9) → 44° (2.4) | 1 + a spur at the elbow | (−4.7, 17.6) | 1.0 → 0.5 |
  | LEAD | (0.6, 12.8), the column's continuation | up 77° (2.5) | fork at (1.2, 15.2) | V: left tine 106° to (0.7, 16.7), right tine 54° to (2.9, 17.6), spur to (3.5, 16.8) | 1.6 → 0.35 |
  | R | (1.8, 9.4), right of the crotch | up-right 60° (4.3) → 11° (2.2) | 2 | fork at (6.1, 13.5): up 61° to (7.4, 15.8); right −16° / −27° to (8.5, 12.8) and (8.6, 12.2) | 1.85 → 0.5 |
  | FR | hidden in front (it comes toward the camera over R's base) | | | side cell: front-pointing limb to y −0.37 H, z .72 H | |

  The rear cell agrees, mirrored: its left limb (world +X) rises from (−1.6 … 3.2 in rear screen) to an elbow and a
  three-way fork, its right limb (world −X) carries the low side branch (h .47–.49), the mid side branch (h .73) and
  the upper stem (h .86); its two middle limbs reach h .98–1.0. **Tip count against the sky: front ≈ 13, rear ≈ 12,
  side ≈ 11, f34 ≈ 14.**
- **Plan azimuths of the arm ends** (as planned): R-right 336°, R-up 15°, LEAD 58° (short in plan, steep), L3 snapped
  end 132°, TL 150°, L1 168°, L2 192°, FR 292°. Against the top cell's nine arms (15, 58, 104, 129, 168, 204, 247, 292,
  336): seven match within 15°; 104° and 247° have no limb because the front and rear cells show nothing pointing at
  the camera there (§3.4).
- **Bore pits (40–55 on the hero):** small dark recesses (square or triangular, 0.20–0.35 across, 0.05–0.08 deep, or
  flat inset faces in `hollow`, decision §8.7), **at every kink and fork crotch first**, then along limbs every 1.5–2.5
  studs, 10–14 on the trunk core (mostly on strand crests, never in grooves), 1–2 per root. Close-ups show them as dark
  squares on facet centres. Visible count target: 25–35 per side view.
- **Cut ends:** every tine end flat; about half dark (`hollow`), the rest `wood_light` rimmed. The LM snapped end:
  4–5 jagged pale facets (`wood_light`) round a dark centre.

### 2.5 Base dressing (no ground patch)

Plan positions from the front, rear and f34 blobs (§1.2). Keep every piece between roots: the azimuths below are
chosen ≥ 25° from the nearest root.

| Piece | Position (x, y) | Size W × D × H | Evidence |
| --- | --- | --- | --- |
| RK1 tall back-left | (−5.8, 2.6), az 156° | 2.4 × 2.0 × 3.8, pointed sloping top | front x −.39…−.27 H top .236; f34 tall left; rear tall right |
| RK2 tall back-right | (5.6, 2.8), az 27° | 2.2 × 2.0 × 3.6 | front +.26…+.38 top .255; rear tall left |
| RK3 low front-left | (−5.2, −3.6), az 215° | 2.6 × 2.2 × 1.9 | front −.33…−.19 h .115; f34 big low (126–203) |
| RK4 front-centre | (−0.4, −6.2), az 266° | 2.0 × 1.8 × 1.4 | front −.07…+.04; f34 (249–307) |
| RK5 small front-right | (5.6, −3.9), az 325° | 1.2 × 1.1 × 0.9 | front +.24…+.30; f34 (370–398) |
| RK6 back-centre | (0.5, 6.0), az 85° | 2.6 × 2.2 × 1.9 | rear centre −.18…−.02 h .11 |
| Pebbles ×5 | (−6.6, −1.8), (1.8, −6.8), (7.4, −1.4), (−3.0, 6.4), (7.2, 3.6) | 0.45–0.8 | small greys in every view |
| Moss pads ×6 | between roots at r 3.5–7.0: az 212°, 270°, 328°, 25°, 85°, 150° | lobed, 1.6–3.0 across, 0.08–0.12 thick | lime strips on the ground in f34 / front / rear (G bottom band) |
| T1 far-left tuft | (−7.6, −2.6) | Ø 1.8, 1.6 tall, 7 blades | front −.47…−.37; f34 (83–116) |
| T2 front-left tuft | (−3.0, −5.2) | Ø 2.0, 1.5 tall, 7 blades | f34 (174–225); front −.26…−.13 |
| T3 front-centre sprigs | (0.8, −6.6) | Ø 1.2, 0.9 tall, 5 blades | front centre |
| T4 right-centre tuft | (4.0, −4.4) | Ø 1.4, 1.2 tall, 6 blades | front +.19…+.24 |
| T5 big right group | (7.2, −0.4) and (6.4, 1.2) | Ø 3.2 together, 2.4 tall, 14 blades | front +.30…+.48; f34 (398–457) |
| T6 back-right tuft | (4.0, 4.6) | Ø 1.6, 1.4 tall, 6 blades | front back-right, h .20–.26 |
| T7 back-centre tuft | (−1.8, 6.6) | Ø 1.6, 1.6 tall, 6 blades | rear centre |
| T8 back-left tuft | (−6.4, 4.4) | Ø 2.0, 1.6 tall, 7 blades | rear right side |

- **Blades:** pointed lanceolate, broad at the base (length : width ≈ 4), folded once along the midrib (closed, 6
  tris), rising 55–80° and arching out from a small hub; chunky, never needles, never edge-on to the f34 or front camera.
  The sheet's tufts are spikier than 047's broad leaves: pointed tips are right here.
- **Rocks:** chunky angular blocks, flat base, 10–16 broad facets; the two tall ones W : H 0.6, a pointed top leaning
  toward the tree; the low ones W : H 1.4–1.8 with a sloping faceted top. Never `K.hull_rock` balls or eggs.
- **Keep clear:** nothing more than 0.05 inside a root, toe or the trunk (047 round-2 blocker); every tuft hub ≥ 0.3
  outside root surfaces; rocks may touch roots but cut ≤ 0.05.

### 2.6 Expected extents and screen checks

- **Extents:** X −8.3 … +8.6 (L1 and R tines), Y about −7.9 … +7.0 (FR tines; RT6 / RT5 toes), Z 0 … 18.0. Bbox about
  16.9 × 14.9 × 18.0 (sheet front W 17.6: tune tines out by ≤ 0.4 if the front W : H falls under 0.92).
- **Checks on the renders** (floor hidden, `measure_render.py` with this folder's `m.py`):
  - **f34_sheet (0, 12)** (probe az −30 … +30 × e 6 / 10 / 14, keep the best; §3.2): W : H 0.91–1.03 (sheet 0.971);
    shares T 78 ± 4, G 8 ± 3, R 12 ± 3; fill 0.44 ± 0.04; top profile ±0.08 for f .1–.9; width per height ±0.10 at
    h .2–.9 with **the bare-trunk rows at h .3–.4 ≤ 0.36**; T fifths each within ±6 of 26 / 21 / 24 / 22 / 7.
  - **front_sheet (0, 4), rear_sheet (180, 4):** W : H 0.92–1.03; T 77–79 ± 4; fill 0.43 ± 0.04; every tip group of
    §2.4's table at its position ± 0.04 H; the knot visible as a dark hole with a pale ring (front); tip count 11–15.
  - **r34_sheet (180, 12)** (probe 150 … 210): W : H 0.90–1.02, T 78 ± 5.
  - **side_sheet (90, 4):** content (§3.3): four limb masses, two each side out to 0.33–0.42 H, two tall middle limbs
    to h ≥ 0.95, roots both sides; W : H 0.78–0.92.
  - **top (0, 89):** W : D 0.95–1.20 (sheet 1.015); ≥ 8 arm ends round the centre, largest gap ≤ 90°; T ≥ 65 %; rock
    and green visible between the arms.

## 3. View conflicts and resolutions

### 3.1 Sheet number

- **Evidence.** The header says "55 / 132"; INDEX.md row 53 lists `053.png` as "Flintborn dead tree asset study".
- **Resolution.** Our number is 053 (file name, keys `m053_*`). Note the header in the export notes only.

### 3.2 The "front three-quarter" is drawn almost frontal

- **Evidence.** Positions in the f34 against the front cell (fractions of H): knot +0.127 / +0.119; L1 tip −0.483 /
  −0.46; R tines +0.468 / +0.48; TL tip −0.28 / −0.26; leader right tip +0.169 / +0.16; root tips −0.17 and +0.22 /
  −0.21 and +0.21. The f34's W : H (0.971) equals the front's (0.976). Only the elevation differs: the f34's ground band
  is about twice as deep (e ≈ 10–14° against 3–6°). The r34 is likewise close to the rear cell.
- **Resolution (decision §8.10).** `f34_sheet (0, 12)` governs with `front_sheet`; probe az −30 … +30 (e 6–14) and keep
  the best match; `r34_sheet (180, 12)` probe 150 … 210. Record the chosen cameras.

### 3.3 The side cell shows front- and back-pointing limbs the front and rear don't

- **Evidence.** The side cell has a limb spreading out each side (to −0.37 H and +0.40 H at h .5–.8) and two tall
  middle limbs (tips at −0.20 H and +0.14 H, h .98). The front and rear cells show nothing coming straight at the camera
  in front of the trunk at h .5–.75 (the trunk and the leader / TL bases fill that area, cleanly). A tree with limbs only
  in the X-Z plane would show the side as a narrow column; the side's W : H is 0.85.
- **Resolution.** Front and rear govern positions; the side and top are judged for content. The plan (§2.4) swings the
  limbs 20–60° off the X axis so their X matches the front while their Y spreads them in the side and top: FR runs
  front-right (y −7.9) behind R's base in the front cell; LM's upper stem bends back (y +6.4) behind its own elbow;
  TL, L1 and R-up lean back. The side then shows FR out front, LM's stem and TL out back, LEAD and TL up the middle.

### 3.4 The top cell's nine even arms

- **Evidence.** Nine arms of equal reach (r 0.47–0.50 H) at 26–45° spacing, all leaving the trunk top, and a bare pale
  cut disc with a square socket in the middle. The front cells have the limbs leaving at z 8.4–12.6 at different
  heights, a leader standing in the top socket, and no limb pointing at the camera.
- **Resolution.** The plan gives eight arm ends at 15–336° (seven within 15° of a top-cell arm, §2.4); the leader
  covers the centre. To keep the top cell's pale disc, the trunk top's **cut face (Ø 2.6) is wider than the leader's
  base (Ø 1.7)**, so a pale ring about 0.45 wide shows round the leader from above (decision §8.8: drop it to `wood` if
  it reads as a pale band in the f34). Judge the top for content: ≥ 8 arm ends, gap ≤ 90°, a light ring at the centre,
  rock and green between.

### 3.5 Exploded heights and scale vs the hero

- **Evidence.** The exploded puts module A highest on the left (near the core's rim), B in the middle, C lowest; the
  upper-right module near the rim, the right one lower. The hero's highest left limb is TL (z 11.2–12.6), whose shape
  (two kinks, a Y tip, a spur) is module B's; the thick, low left limb with two side branches (LM) is module A's big Y.
  The exploded's root modules are drawn about 1.5× the hero's length (closer to the camera).
- **Resolution.** **The hero governs heights and sizes; modules are assigned by shape** (§2.4: A → LM, B → TL, C → L1,
  top → LEAD, upper-right → R, right → FR). The part shots use the hero's own module meshes.

### 3.6 How many roots

- **Evidence.** Exploded: four root modules + one built-in front root + stubs at the back. Close-up 2: six roots round
  the 12-sided bottom. Front, rear and side tips: six directions (§2.3).
- **Resolution.** Six roots: Root A ×2 (RT1, RT6), Root B ×2 (RT2, RT5), Root C ×1 (RT4), the built-in front root
  (RT3). Reusing modules is what the sheet's notes ask for; vary each instance's yaw by ±5° and its reach ±0.4 so the
  repeats don't read.

### 3.7 Sockets, pegs and joint seams in the hero

- **Evidence.** Close-up 1 and the exploded show pegs and dark sockets; the assembled views show no seams, rims or
  pegs at the limb bases or root stubs.
- **Resolution (decision §8.5).** As in 047: model every socket with its hole and every module with its peg (hidden in
  the hero, shown on the parts). Each module's base face overhangs its collar or stub face by 0.02 all round, so the
  collar's pale cut face is hidden in the hero and the join reads as a plank crease, not a pale ring.

### 3.8 "WOOD DARK: main trunk shadow planes" vs the no-facing rule

- **Evidence.** The sheet's wood dark swatch (`#865331`) is the colour of its shade side and creases; every view's
  shade half is `#855633`–`#935C35` against `#C3743B`–`#C77237` lit.
- **Resolution.** The shade side is the light. `wood_dark` goes only where the geometry is a crease or a cavity: strand
  grooves, kink and fork crotches, round the bore pits, under collars, the lowest 0.5 of roots and toes, the underside
  disc. **Never by facing** (042 ruling).

### 3.9 Ground: no patch drawn

- **Evidence.** No sand or soil disc in any cell: lime moss strips and tufts sit straight on the paper between the
  roots, with grey rocks; the top cell shows paper beyond r 0.35 H.
- **Resolution.** No patch. Six thin lobed moss pads between the roots (§2.5) give the lime ground band; rocks,
  pebbles, tufts and root toes sit on z 0.

### 3.10 Cast shadow

- The sheet's lavender shadow is excluded by the X mask. Render every `*_sheet` view with the studio floor hidden.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its exploded cell

1. `seg_chain(points, radii, sides, twist)` → one closed tapering prism chain: a ring of `sides` at each waypoint
   (mitred: the ring's plane bisects the two segments' directions, so kinks stay hard and never pinch), flat end caps.
   **No smooth curves; every waypoint is a hard kink.** This one primitive builds every limb, branch, tine and root.
2. `tine(base, tip, r)` → a 4-sided chunky prism with a flat end cap, its base buried ≥ 0.15 in the parent (or welded
   into a ring-stack junction, decision §8.6).
3. `pit(face, size)` → a bore pit on a facet centre (§2.4; decision §8.7).
4. `peg(face, side)` → a square pale peg (side 0.35 × the base Ø, length 0.30 + 0.20 visible on the part) on a module's
   base face.
5. `branch_module(kind)` for kinds `A` (big Y + snapped end), `B` (kinked + spur), `C` (comb), `top` (V + spur),
   `riser` (long, with a forked side branch), `yfork`: each a function returning one module in its own local frame
   (base face at the origin, axis +Z), so the same function serves the hero and the part. Check each against its
   exploded cell before assembling.
6. `root_module(kind)` for `A` (3 toes), `B` (2 toes), `C` (3 toes), local frame like the branches.
7. `trunk_core()` → the twisted 6-strand body (§2.2 rings), then the five collars, five root stubs and the built-in
   front root (RT3) **unioned one at a time at the origin** (`m021._union_fine`, merge 0; save between unions; collapse
   corners under 3°), then the sockets, the knot, the second hole, the trunk pits and the underside chamfer and pin.
8. `base()` → `rock(spec)` ×6 (explicit ring stacks: base ring, widest ring at 0.3 h, shoulder ring at 0.7 h, a flat
   sloping or pointed top; 10–16 broad facets), `pebble()` ×5, `moss_pad()` ×6, `tuft(spec)` ×8 with the placement
   guard (§6).
9. **Hero `TwistedSnag`** = trunk core + six branch modules on their collars + six roots on their stubs + base, joined
   into one object of closed shells.
10. **Parts shot** (0, 22) laid out like the exploded: the trunk core in the middle, branch modules round its top (A,
    B, C left; top, upper-right, right), root modules round its foot; gaps 1.5–2.

### 4.2 Stage 1 acceptance (render, compare every view, measure with this folder's scripts)

1. **Overall read:** a bare dead tree on a massive twisted planked trunk, six chunky kinked limbs with blunt tines,
   six split-toed roots, bore pits, an oval knot with a pale rim, a snapped pale end; pale grey rocks, lime tufts and
   moss at the foot.
2. **f34_sheet** per §2.6 (shares, fill, W : H, profiles, the bare-trunk rows, T fifths).
3. **front / rear / r34 / side / top** per §2.6; every §2.4 tip group at its place ± 0.04 H in front and rear.
4. **Close-up renders:** `join_cu (−25, 20)` on the trunk core part's S_LM collar with Branch A's base and peg beside
   it, against close-up 1 (square pale peg, flat cut face with a lighter rim, dark socket in a raised collar, the knot
   ring nearby); `underside` (0, −89) against close-up 2 (12-sided flat bottom, chamfer ring, pin, six roots radiating);
   `knot_cu (−15, 5)` on the front-right; `crown_cu` from the f34 camera cropped to the upper third against
   `p_f34crownL/R.png` (straight prisms, hard kinks, square tines, dark pits at kinks).
5. **Contact counts** (§6): floating shells 0; every tine chained to its branch, every module to its collar or stub,
   the core to the ground.
6. **Hero size** per §2.6; a **scale shot** with a 5.5-stud marker under the L1 limb (its lowest tine at z 8.5 clears
   the marker's head by 3).

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Trunk body (18 sides × 9 bands, caps) | 1 | 340–380 | 340–380 |
| Collars + sockets (5 side + top) | 6 | 24–36 | 150–210 |
| Root stubs (5) + built-in RT3 with toes | 6 | 24–70 | 170–220 |
| Knot + second hole + underside chamfer / pin | | | 70–100 |
| **Trunk core part** | | | **750–900** |
| Branch modules (main 6-sided, branches 5, tines 4; pegs) | 6 | 90–170 | 700–850 |
| Root modules (6-sided, 3 segments, 2–3 toes, peg) | 5 | 60–80 | 300–400 |
| Bore pits (flat insets 6–8, or recessed 12–16) | 40–55 | 6–16 | 280–500 |
| Rocks | 6 | 32–48 | 220–280 |
| Pebbles | 5 | 8–12 | 40–60 |
| Moss pads | 6 | 14–20 | 90–120 |
| Tuft blades (6 tris) + hubs (8) | 63 + 8 | | 440 |
| **Hero** | | | **about 3000–3450** (limit 4000; ceiling 3800) |
| Parts: TrunkCore / BranchA / BranchB / BranchC / RootA / RootB / RootC | | | 750–900 / 170–200 / 110–140 / 120–150 / 80–100 / 70–90 / 80–100 (limit 1000) |

- **Spend headroom on the skeleton:** if a limb reads thin or tubular, add a 7th / 8th side to the main limb segments
  (the sheet's cut end in close-up 1 is octagonal) or one more kink, before anything else; then more plank facets on
  the trunk's front half. Never subdivide.
- If the hero passes 3800, flatten the pits (recessed → flat inset), then drop T3 and one moss pad.

### 4.4 What to do better than W05's `DeadTree` and 047

| Earlier | This one |
| --- | --- |
| W05: thin limbs, the trunk reads as a cone (verifier rev 4, 6/10) | limbs Ø 1.6–2.1 at the base (0.32–0.42 of the waist), fill 0.43; strands with deep V grooves crossing in an X |
| W05: pointed antler tines | blunt, square-cut, flat-ended 4-sided tines, half with dark ends |
| W05: one mesh, no joints | plug-in modules with pegs, collars and stubs, as the sheet's construction |
| 047 round 1: stub limbs, hidden twigs | full limb runs (§2.4), every tine visible against the sky |
| 047 leftover: a knot read as a slot; a straight column | an oval knot with a pale raised ring and boss; a twisted, flared, waisted trunk |
| 047 round 2: plants buried in roots and rocks | the ray-parity placement guard from day one (§6) |

### 4.5 Stages 2 and 3

- **Stage 2:** every shell closed and manifold; 0 bowties (tine junctions, pegs, pits and toe forks are the likely
  spots: `M.fix_bowties`); **0 winding errors per shell** (STAGES "Consistent winding": the mitred kink rings and the
  inset pits flip easily); no zero-area faces, no n-gons except the flat caps (triangulate the 12-sided bottom as a fan
  round the pin ring); corners ≥ 3°. Origin bottom centre, transforms applied.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box, sd ≤ 2.1)

| Swatch | Box | Hex | HSV | Use |
| --- | --- | --- | --- | --- |
| WOOD DARK | (688,1258,714,1276) | `#865331` (legend `#865230`) | 24°, 0.63, 0.53 | start for `wood_dark` |
| WOOD MID | (688,1289,714,1303) | `#CF8548` (legend `#CF8447`) | 27°, 0.65, 0.81 | start for `wood` |
| ROCK | (688,1315,714,1329) | `#9B9390` (legend `#9E9692`) | 16–20°, 0.07, 0.61 | start for `rock` |
| FOLIAGE | (688,1341,714,1356) | `#AAB91C` (legend `#B1BE1F`) | 65–66°, 0.85, 0.73 | start for `grass` and `moss` |

### 5.2 Rendered regions (`samp.py`, `samp2.py`, `samp3.py`; median / v > .7 / lit quartile / shade quartile)

| Region | Median | v > .7 | Lit Q | Shade Q | Halves (left shade / right lit) |
| --- | --- | --- | --- | --- | --- |
| Wood f34 | `#B26634` (24°, .71, .70) | `#DA8340` | `#EC9F59` | `#60361D` | `#855633` / `#C57035` |
| Wood front / rear / side / r34 / top | `#B66936` / `#A46033` / `#AB6538` / `#A76137` / `#B56D3B` | `#DC8644` / `#DE8946` / `#E08D4C` / `#DD8946` / `#DE8D4C` | `#EFA05B` … `#EF9F59` | `#5D351E` … `#63381F` | front `#935C35` / `#C77237` |
| Trunk h .2–.45 (f34 / front) | `#C56F35` / `#C46E36` | `#D57D3A` / `#D77D3C` | `#E7924C` | `#663A1F` | |
| Limbs h > .6 (f34 / front) | `#9D5C37` / `#AA6238` | `#DD8746` / `#DF8C4B` | `#E89A56` | `#623822` | |
| Roots h < .12 (f34 / front) | `#B86E35` / `#AB6A36` | `#E3A24C` / `#E69B55` | `#F5B167` | `#583219` | |
| Cut wood (top disc, knot ring, pegs lit) | `#F9C984` (35°, .47, .98) / `#F6BE70` / `#FAC882` | | | | exploded peg `#F1A259`, branch end rim `#DA8239` |
| Holes (socket, knot, top socket, exploded knot) | `#1A0E07` / `#241308` / `#433013` / `#341B09` | | | | |
| Underside disc (cu2) | `#865633` (= WOOD DARK) | | | | rim band lit `#E89B52` |
| Rock f34 / r34 / front / rear | `#898080` / `#A4978A` / `#85827E` / `#9C9286` | `#C5B9AD` (30°, .12, .77) / `#C7BBAD` / `#C7BEB1` / `#C6BDAC` | `#C8BCB0` … `#D3C6B9` | `#5E5E5D` … `#635E5B` (neutral) | |
| Moss ground (G at h < .03) f34 / front / rear | `#C8B810` (55°, .92, .78) / `#C2B620` / `#BAB414` | `#CABB0E` | `#D5C414` | `#9B941C` | |
| Grass blades (G at h > .06) f34 / front / rear | `#86910C` (65°, .92, .57) / `#838F0F` / `#768115` | `#BEC20D` / `#C0BC1B` / `#C4BD1D` | `#C2C510` | `#44540D` (75°) | |

### 5.3 How the colour works

- **Wood:** one warm orange-brown (`wood`, 22–27°, sat 0.65–0.73, R > G > B) everywhere; **deeper** (`wood_dark`) in
  the strand grooves (the pulled-in groove vertices: position), in kink and fork crotches (the ring at each kink, 30 %),
  round each pit (one facet ring, 25 %), under each collar, on the lowest 0.5 of roots and toes and on the underside
  disc; **lighter** (`wood_light`) on cut faces only: pegs, collar and stub faces, the top cap's ring, the knot rim and
  boss, the second hole's rim, the snapped end, the light tine ends; **hollow** (`hollow`, near black-brown) in every
  socket hole, the knot recess, the second hole, every pit and the dark tine and toe ends. Limbs a touch lighter toward
  their tines (10 %, by position along the limb), roots a touch lighter on their top ridges (by position on the
  section), never by facing.
- **Rock:** pale neutral-warm grey (lit 30–35°, sat 0.10–0.14, R ≥ G ≥ B, never pink or blue); tops a step lighter,
  feet a step deeper, by height within each rock.
- **Moss:** a yellower lime than the blades (55–58° against 65°), on the pads.
- **Grass:** lime blades (`grass`), the inner and lower blades of each tuft a step deeper green (`grass_deep`, 75–78°)
  by role, so tufts read lime outside and green inside; never dark undersides.
- **Hues stay apart:** wood 22–27°, cut wood 30–35°, moss 55–58°, grass 62–68°, grass_deep 75–78°.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians, not swatches. `K.sample` kinds: `"brown"` for wood, `"stone"` for
rock, `"vivid"` for grass and moss (`"green"` may reject the yellow lime).

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m053_wood` | f34 whole-wood median `#B26634` ± 15; v > .7 `#DA8340` ± 12 (start `#CF8548`) | 22–27°, 0.65–0.73, **R > G > B** | trunk, limbs, roots | rough 0.9 |
| `m053_wood_dark` | the WOOD DARK swatch `#865331` rendered lit ± 12 | 20–25°, 0.6–0.68 | grooves 40 %, kink rings 30 %, pit rings 25 %, under collars, root bottoms 25 %, underside disc (hard) | rough 0.95 |
| `m053_wood_light` | cut wood `#F6BE70` ± 12 (lit `#F9C984`) | 30–36°, 0.45–0.55 | pegs, collar / stub faces, top ring, knot rim and boss, snapped end, light tine ends (hard: cut faces) | rough 0.85 |
| `m053_hollow` | holes `#2A160A` ± 10 | 20–28°, 0.7–0.8, v ≤ 0.2 | sockets, knot recess, pits, dark tine and toe ends (hard) | rough 1.0 |
| `m053_rock` | v > .7 rock `#C6BCAE` ± 10 (start `#9B9390`) | 28–35°, 0.08–0.14, R ≥ G ≥ B | rocks, pebbles | rough 0.85, metal 0 |
| `m053_rock_light` | lit quartile `#D0C4B6` | 30–35°, 0.10–0.14 | top 30 % of each rock at 35 % | rough 0.85 |
| `m053_rock_deep` | the ROCK swatch `#9B9390` | 16–30°, 0.05–0.08 | lowest 0.25 at 25 % | rough 0.9 |
| `m053_moss` | moss ground `#C8B810` ± 12 | 54–58°, ≥ 0.80 | moss pads | rough 0.95, low spec |
| `m053_grass` | blades v > .7 `#BEC20D` ± 12; median `#86910C` (start `#AAB91C`) | 62–68°, ≥ 0.80 | outer and taller blades | rough 0.85, low spec |
| `m053_grass_deep` | shade-band green `#4B5F0E` rendered lit ± 12 | 74–80°, 0.75–0.88 | inner and lower blades, hubs | rough 0.85, low spec |

**Calibration warnings:**
- **The kit studio lights both halves** (042, 047): don't calibrate `wood` to the sheet's lit half alone or the tree
  goes flat orange (W05 V8 / V16: "a flat saturated orange"). Calibrate to the whole-wood median and the v > .7 median;
  the whole median may read up to 20 levels lighter than `#B26634` because our shade side is lit: record it.
- **Wood must not go red or pink:** R > G > B, hue ≥ 22° on every median.
- **Cut wood vs wood:** `wood_light` ≥ 50 levels lighter (V) than `wood` and ≥ 6° yellower, or the pegs and the knot
  rim won't read.
- **Rock:** R ≥ G ≥ B on every median; the sheet's rock is cleaner and paler than 047's.
- **Grass vs moss:** `moss` ≥ 6° yellower than `grass` after calibration.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Trunk and roots:** `wood` base; `wood_dark` 40 % in the groove columns (faces touching a pulled-in groove vertex),
  blended one facet out (steps 3) so each strand reads rounded by shade; 25 % on the lowest 0.5 of every root and toe;
  hard `hollow` in holes; hard `wood_light` on cut faces. Per-plank Tint (whole facets) ±0.04 held in runs up each
  strand, plus broad noise 0.03 at scale 0.35.
- **Limbs:** `wood` base; a `wood_dark` ring at every kink and fork crotch (30 %, blended one ring each way); 10 %
  lighter toward the tines; pits hard `hollow` with a 25 % `wood_dark` facet ring.
- **Rocks:** height bands within each rock (light top 30 %, deep lowest 25 %).
- **Grass, moss:** per blade by role; moss pads 15 % `grass` at their edges.
- **Hard edges only** where materials meet: cut face | bark, hole | rim, wood | ground dressing, rock | moss.

### 5.6 Texture (Tint) and finish

- **Tint:** wood 0.04 per plank column plus 0.03 broad; rock 0.04 per facet; moss 0.03 at scale 0.2; blades 0.04 per
  blade. Never per-triangle confetti (the pits are geometry, not noise).
- **Finish:** wood 0.9 (dark 0.95), cut wood 0.85, hollow 1.0; rock 0.85; grass and moss low spec. No emission.

### 5.7 Re-measure (final renders against the sheet, same masks)

- **Wood:** f34 whole median within 20 of `#B26634` (record the lit-shade bias); v > .7 within 12 of `#DA8340`; R > G > B.
- **Cut wood:** the knot rim and the f34-visible cut faces within 15 of `#F6BE70`.
- **Holes:** pits and knot recess v ≤ 0.25.
- **Rock:** f34 v > .7 within 10 of `#C5B9AD`, R ≥ G ≥ B.
- **Grass:** f34 blades v > .7 within 12 of `#BEC20D`; moss within 12 of `#C8B810`.
- **Shares** per §2.6.

## 6. Joins and contact (no floating dressing, no buried dressing)

- **Shells:** trunk core one closed shell (body + collars + stubs + RT3, unioned); each root module and each branch
  module one or more closed shells (main limb a ring-stack shell; side branches and tines either welded into it at a
  ring junction or separate closed shells buried ≥ 0.15, decision §8.6); each peg, rock, pebble, moss pad, blade and
  hub its own closed shell. All in one hero object.
- **Peg in socket:** the peg enters 0.30 deep with 0.02 clearance on every side, its end 0.015 above the socket floor;
  the module's base face 0.015 off the collar / stub face. Read the gaps back (BVH nearest per module: 0.005–0.03) and
  check **no peg corner inside the trunk solid** by ray parity (047's `plug_report`).
- **Tines and side branches:** roots buried ≥ 0.15 in the parent segment; no tine touching its parent only along an
  edge; no tine passing through a neighbouring limb.
- **Toes:** sunk 0.05 below z 0; root modules' undersides 0–0.05 below z 0 along their low run.
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**. A shell floats if its nearest
  distance to every other shell and the ground is > 0.03 or it doesn't chain to the ground: tine → branch → module →
  peg / collar → core → ground; blade → hub → moss pad or ground; rock → ground.
- **Count buried shells** (STAGES; 047 round 2 blocker): **0 dressing shells more than 0.05 inside a root, toe, the
  trunk or a rock**, by ray parity against the full hero after the final placement step. Use 047's guard from the start
  (`_Solids`: trunk core + every root module + every rock added as built; three skewed rays, two of three agree;
  placement accepts ≤ 0.03; a blade that still cuts after its retries is **dropped**, never kept).
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no particles, no falling bark, no dust, no fireflies. The cast
shadow is the render's.

- **Stage 5 (lighting): skip, and record why.** No emission, no lights. Studio notes (Requires Manual Validation): the
  wood stays orange-brown under the game sun, not red; the pits, knot and sockets read dark; cut faces read pale; the
  rocks stay pale grey; the grass lime.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** Not recommended: falling leaves (there are none),
  crows, dust motes.
- **Collision:** hero `precise` (players walk under the limbs and between the roots; a hull would wrap an 18 × 15 × 18
  block); trunk core `precise`; branch modules `hull`; root modules `hull`. Tufts and moss pads could be walk-through
  (`kit_nocollide = 1`, as W05 did) if the exporter supports it for this kit (decision §8.11).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json`, the W-sheet
scripts and the repo text (`git grep`):
- **W05:** `DeadTree`, `DeadTreeUpright`, `DeadTreeLeaning`, `DeadTreeSnappedTrunk`, `DeadTreeTrunkBase`,
  `DeadTreeBranchModuleA`, `DeadTreeBranchModuleB` (manifest), `DeadBranchModuleA`, `DeadBranchModuleB`, `DeadTrunkBase`
  (wip meshes); also `AncientTree*`, `AncientTrunkCore`, `AncientBranchModule`, `AncientRootModuleA/B/C`,
  `OakTree*`, `OakTrunkCore`, `OakBranchModule`, `LogAndStump*`, `HardwoodStump*`, `ResinheartStump*`; keys `w05_*`.
- **Other trees:** `GnarledPine*` (047), `OldPine*` (W04), `TieredFir*` (042), `PineSapling*` (045), `JuniperGnarled`,
  `SilverbarkTree`, `GoldencrownTree`.
- **`TwistedSnag`, `Snag`, `BareTree`, `WitheredTree`, `DeadOak`, `TwistedTree` and `m053` occur nowhere** (repo text,
  manifests). ("snag" appears only as a verb in two docs.) `TwistedSnag*` contains no W05 name as a substring. Note for
  057 Ancient Tree: W05 owns `AncientTree*` / `Ancient*Module*` too.

| Object | Part | Why |
| --- | --- | --- |
| `TwistedSnag` | hero: core, six branch modules, six roots, base dressing | W05 owns `DeadTree*`; a snag is a standing dead tree, "twisted" names the rope-strand trunk |
| `TwistedSnagTrunkCore` | "TRUNK CORE": body, collars, sockets, stubs, RT3, knot, holes | the sheet's label |
| `TwistedSnagBranchA` | "BRANCH MODULE A": the big Y with the snapped end (LM) | the label |
| `TwistedSnagBranchB` | "BRANCH MODULE B": the kinked limb (TL) | the label |
| `TwistedSnagBranchC` | "BRANCH MODULE C": the comb (L1) | the label |
| `TwistedSnagRootA` | "ROOT MODULE A": three toes | the label |
| `TwistedSnagRootB` | "ROOT MODULE B": two toes | the label |
| `TwistedSnagRootC` | "ROOT MODULE C": three toes | the label |

- Palette keys `m053_*` (§5.4). Collection `Kit/M053 Dead Tree`. No sockets (VFX).

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **18.0 tall, crown 17.6 × about 15, waist Ø 5.0, root reach 7.2–8.1** (recommended: just under
   047's 20; low limbs at 8.4–9.6 so players walk under them; rocks 0.9–3.8), or 16 (limbs at 7.5), or 22 (nearer
   W05's 24; trunk wider than 047's).
2. **Name (§8):** **`TwistedSnag` and the seven parts above** (recommended), or `WitheredTree`. Not `DeadTree*` (W05).
3. **Limb plan (§2.4, §3.3, §3.5):** **six modules on six sockets as tabled (A → LM, B → TL, C → L1, top → LEAD,
   riser → R, Y-fork → FR), limbs swung 20–60° off the X axis so the front and rear match and the side and top spread**
   (recommended), or add a seventh module (a second B at az 250°, z 9.0) to fill the top cell's 247° arm (costs ~130
   tris and puts a limb in front of the trunk that the front cell doesn't show).
4. **Roots (§2.3, §3.6):** **six: A ×2, B ×2, C ×1 and the built-in front root, ±5° yaw / ±0.4 reach per instance**
   (recommended), or seven (add a short back stub root).
5. **Joints (§3.7):** **pegs and sockets modelled (hidden in the hero), module faces overhanging their collars by
   0.02, as 047** (recommended), or no holes and pegs in the hero (saves about 200 tris of hidden geometry, but the
   hero and the parts then differ).
6. **Branch shells (§6):** **main limb segments as one ring-stack shell per module; side branches and tines as closed
   shells buried ≥ 0.15 in the parent** (recommended: no booleans in the crown, as 047's twigs), or weld everything per
   module into one shell with ring junctions (cleaner seams, much harder; the trunk core stays unioned either way).
7. **Bore pits (§2.4):** **40–55 flat inset pits (the facet's centre inset, its inner face `hollow` with a `wood_dark`
   ring), recessed 0.05 only where they face the governing cameras** (recommended: about 300 tris), or all recessed
   (about 500), or 25 (cheaper, but the sheet's speckle of holes is part of the read).
8. **Top ring (§3.4):** **the core's top cut face 0.45 wider than the leader's base, `wood_light`, so a pale ring shows
   from above** (recommended), switched to `wood` if it reads as a pale band in the f34.
9. **Side and top cells (§3.3, §3.4):** **judged for content** (recommended).
10. **Comparison cameras (§3.2):** **`f34_sheet (0, 12)` governing with `front_sheet (0, 4)`** (probe az −30 … +30,
    e 6–14); `r34_sheet (180, 12)` (probe 150 … 210); `side_sheet (90, 4)`, `rear_sheet (180, 4)`; kit `top`,
    `underside`; extras: parts shot (0, 22), `join_cu (−25, 20)`, `knot_cu (−15, 5)`, `crown_cu`, scale shot. Floor
    hidden in every `*_sheet` render.
11. **Collision (§7):** **hero `precise`, trunk core `precise`, branch and root modules `hull`** (recommended); tufts
    and moss walk-through only if the exporter already supports `kit_nocollide` for this kit.
12. **Exported parts (§8):** **the hero plus the seven labelled parts** (recommended), or also the three unlabelled
    branch modules (`…BranchLeader`, `…BranchRiser`, `…BranchFork`).
13. **Colour (§5):** **wood calibrated to the whole-wood median `#B26634` and v > .7 `#DA8340`; `wood_dark` by crease
    and cavity position only; cut wood `#F6BE70`; holes `#2A160A`; rock lit `#C6BCAE`; moss `#C8B810`; grass
    `#BEC20D` / `#86910C`** (recommended).
14. **Stages 5 and 6:** **skip both, recorded** (recommended).
15. **Budget (§4.3):** **4000 limit, about 3000–3450 planned, ceiling 3800; parts under 1000** (recommended).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **A thin or tubular skeleton (W05 rev 4; 047 round 1 "stub limbs"; the user's tree rule).** Limb bases Ø 1.6–2.1,
   elbows 1.0–1.4, tines ≥ 0.4; **fill 0.43 ± 0.04 and T 78 ± 4 in the f34, front and rear**; T fifths 3–4 each ≥ 18 %;
   every §2.4 limb at its full run with its kinks; 11–15 tine ends against the sky per side view.
2. **Smooth curves instead of angular kinks.** Every waypoint is a hard mitred kink between straight prisms; no bezier,
   no spin, no subdivision. Check `crown_cu` against `p_f34crownL/R.png`.
3. **A straight or cone trunk (047 leftover; W05).** Six strands with V grooves 0.30–0.40 deep, twisted 60° CCW, the
   "/" crossing on the front; waist 5.0 at h .35–.40 between a 9.4–9.9 flare and the 7–9.9 crotch; the bare-trunk rows
   at h .3–.4 ≤ 0.36 of W.
4. **Pointed antler tines (W05) or needles.** Tines are 4-sided, blunt, flat-ended, 1.0–2.2 long; half the ends dark.
5. **A knot read as a slot (047).** Oval dark recess, raised pale ring, pale boss below; it reads as a ringed hole at
   cell scale in the front and f34.
6. **Pits as confetti or missing.** 40–55 discrete dark pits, mostly at kinks and forks, 25–35 visible per side view;
   never per-triangle colour noise.
7. **Floating or unseated modules (STAGES; 035 / 036).** Every peg 0.015–0.03 from its socket walls, no peg corner
   inside the solid; every tine within its parent; **0 floating shells**.
8. **Buried dressing (047 round 2 blocker).** 0 tufts, blades, hubs, pads or rocks more than 0.05 inside a root, toe,
   the trunk or a rock, by ray parity after the final placement; hubs ≥ 0.3 clear of root surfaces.
9. **Colour by facing (042 ruling).** `wood_dark` only in creases and cavities by position; `K.check` facing
   correlation < 0.5 per material.
10. **Flat saturated orange or red wood (W05 V8 / V16).** Whole median within 20 of `#B26634`, hue 22–27°, R > G > B,
    lit and shade facets from the light.
11. **Egg, mauve or blue rocks (M034, M037).** Angular blocks, 10–16 broad facets, flat bases; R ≥ G ≥ B; the two tall
    ones W : H ≈ 0.6 with pointed tops.
12. **Edge-on or needle grass (039).** Folded lanceolate blades L : W ≈ 4, facing the f34 and front cameras.
13. **Winding (044) and bowties.** 0 faces wound against their neighbours per shell (mitred kink rings and inset pits
    flip easily); `M.fix_bowties`; corners ≥ 3° on the core's union seams (047 left 43 under 3°).
14. **Exact booleans:** only the collars, stubs and RT3 into the trunk body, at the origin, one at a time, saving
    between them (STAGES "Booleans"). Modules, tines, pits and dressing are never unioned.
15. **Names and scope.** No `DeadTree*` / `DeadBranch*` / `DeadTrunk*` (W05), no `GnarledPine*`; only one agent drives
    a Blender session at a time; no commits, pushes or exports in stage agents; don't edit the frozen shared helpers or
    `lib/vfx.py`; don't touch other models' collections.

## Decisions (main session, 2026-10-29)
All 15 recommendations are accepted.

1. **Size.** 18 tall. Crown about 17.6 × 15, trunk waist Ø 5.0. Limbs leave the trunk at z 8.4–9.6, so players walk under them.
2. **Names.** `TwistedSnag` with `…TrunkCore`, `…BranchA/B/C` and `…RootA/B/C`; keys `m053_*`. Never `DeadTree*`, which W05 owns.
3. **Limbs.** The six modules in the table, with no seventh. **The skeleton is the model** (the user's tree rule). Every limb must read in every view, with real length, hard kinks and blunt tines, never stubs.
4. **Roots.** Six, with ±5° yaw and ±0.4 reach per repeated instance.
5. **Joints.** Pegs and sockets, modelled and hidden in the hero. No pale ring shows at a joint.
6. **Crown shells.** Each limb is a ring-stack shell. Tines and side branches are closed shells buried at least 0.15. Booleans only on the trunk core.
7. **Bore pits.** 40–55 flat insets in the `hollow` key, recessed where the governing cameras see them. The knot hole must read as a hole, not a slot.
8. **Top ring.** The pale ring stays as specified; switch it to `wood` if it reads as a pale band in the f34.
9. **Side and top views.** Judged for content only.
10. **Cameras.** `f34_sheet (0, 12)` and `front_sheet (0, 4)` govern. The other views use e 4 with the floor hidden.
11. **Collision.** Hero and trunk core precise; branch and root modules hull.
12. **Exports.** The hero plus the seven parts.
13. **Colour.** Calibrate wood to the median `#B26634` and the lit tone (v > .7) `#DA8340`. Cut wood `#F6BE70`, holes `#2A160A`, rock lit `#C6BCAE`, moss `#C8B810`, grass `#BEC20D` / `#86910C`. "Wood dark" goes on creases and cavities by position only, **never by facing**.
14. **Stages 5 and 6.** Skipped, and recorded as skipped.
15. **Budget.** Limit 4000, ceiling 3800, every part under 1000.

**Packaging.** Every shell is manifold with **0 winding errors**. **No floating dressing**, and no dressing more than 0.05 into rock or wood. The trunk twists; it must not read as a straight column. Rocks must not be eggs.

**Binding.** The silhouette shares in §1 (wood 77–79 %, ±4) and the fill check (0.41–0.44) on the f34 and front views.

## Stage 1 — Modelling (modeller, 2026-10-29/30)

Builder `art/blender/kit/mcp/m053.py` (`build()`), background session port 9881 on `wip/M053.blend` (saved after every
good build). Final numbers below come from a **freshly restarted session** (`kit_mcp.install(); m053.build()`).
Every exploded part has its own function and the hero is assembled from exactly those functions:
- **`trunk_body()`**: six rope strands = 18 columns (a pulled-in groove vertex 0.42 deep, two crest vertices per
  strand, alternating strands 1.0–1.08 thick), 9 rings (z 0 / 2.0 / 4.2 / 5.6 / 6.9 / 8.4 / 9.8 / 11.0 / 11.9, Ø 6.4 →
  5.0 waist → 2.4 top), twisted **82° counter-clockwise** from foot to top (the front grooves climb "/"). A flat underside with a
  square pin hole; a flat cut top face tilted 10° toward az 58 (perpendicular to the leader) round the square leader
  socket (0.62 sq, 0.35 deep).
- **Deviation from decision 6 / spec 4.1-7 (budget): no booleans for the collars, stubs or knot.** Exact-unioned
  collars and stubs cost about 25 tris per seam (first try: 1566 tris, over the 1000 part limit). Instead every feature is
  *grown out of the facet grid*: `_block()` takes a block of body facets, deletes it and walks its boundary loop (by
  angle) to the feature's ring. The trunk core stays one closed manifold shell with no boolean seams:
  - `knot()`: the 2 × 2 block round the crest vertex nearest (z 6.9, az 327) → an oval ring set: swell, raised pale
    rim (two rings), a hole 0.32 deep with walls and floor. `_boss()`: a raised pale square boss on the crest facet below.
  - `collar()` ×5 (LM, L1, R, FR, TL): the free 2 × 2 block nearest each bark point (conflicts resolved automatically)
    → a six-sided ring at F = bark point + axis × out, a pale cut face with a square socket (hollow walls and floor).
  - `stub()` ×6: each strand's three columns over the two lowest bands → the root section, upright, at plan distance
    4.0 with its flat bottom on the ground: the **buttress from the strand down onto the ground** (the strand → root
    continuity the spec asks for). Five carry a square socket; RT3's ring runs straight on as the built-in front root.
  - Only RT3's two toes are exact-unioned (at the origin, `m033._union_fine`, 0 retries).
- **`chain()`**: the one limb primitive: rings in each kink's mitre plane (the bisector), parallel-transported frames,
  so every waypoint is a hard kink that doesn't pinch. `cap()` makes the end caps: flat, cut (pale rim), dark (rim and a sunk hollow), snap
  (a jagged pale break round a sunk dark centre) or socket.
- **`branch_module(name)`** ×6 (LEAD the top V, TL = Branch B, LM = Branch A the big Y with the snapped end, L1 = Branch C
  the comb, R the riser, FR the Y-fork). Each has:
  - a peg;
  - a six-sided main chain: its base face sits 0.015 off the collar face and 0.02 wider, and a shoulder runs along the socket axis, long enough that its mitre never cuts back;
  - side branches and tines as closed 4–5-sided shells, each started on the parent's axis so the parent's radius buries it;
  - bore pits.

  There are 30 tine and branch ends in all.
- **`root_chain(name)`**: Root A is used twice (RT1, RT6), Root B twice (RT2, RT5) and Root C once (RT4); RT6 and RT5 are turned ∓4°. Each root has:
  - a peg;
  - a six-sided section (a top plank, upper flanks, splayed lower flanks and a flat bottom on z 0) through 4 stations, with a plan kink of ±6–8° at the ground;
  - 2–3 blunt five-sided toes with flat ends, hollow on every other toe;
  - 2 bore pits.
- **`pit()`**: a bore pit on any facet: a square (≤ 0.34, inside the facet), walked round from the facet's outline,
  sunk 0.06–0.07, with a hollow floor (+8 tris each).
- **`base_dressing()`**:
  - 6 rocks: ring-stack hulls with flat bases, never `hull_rock` balls. RK1 and RK2 are tall, blunt-pointed and lean toward the trunk; the others are low with sloping tops.
  - 5 pebbles and 10 lobed moss pads.
  - 9 tufts: pointed, folded lanceolate blades (8 tris each), turned toward the front cameras, round a 5-sided hub.

  A placement guard runs from the start (`_Solids`, ray parity):
  - rocks walk out 0.15 at a time while they cut a root by more than 0.03;
  - moss pads and tuft hubs search a ring pattern round their planned spot (`_SEARCH`) for the nearest clear spot, with hubs at least 0.3 clear;
  - blades retry, and are dropped if they still cut.

Iterations, compared side by side against the sheet cells (scratch `m053w/cmp.py`) and measured with `m053w/mr.py` (the study masks):
1. Booleans gave a 1566-tri core; I rebuilt it as grown blocks (860 → 880).
2. The first hero had pipes that were too thin, roots that were low runners and only a slight trunk twist. I made the limbs thicker and the roots bigger (stub face at 4.0), raised the twist from 62° to 82°, and deepened the grooves from 0.34 to 0.42.
3. The shares were T 87 %, G 3.7 % and R 8 %. I made the rocks blunter and larger, the tufts and pads larger, and the blades broader (L : W 3.3).
4. The crown read as fat pipes with stub ends. I made the tine and toe ends single flat cut faces (−290 tris), slimmed the main limbs to × 0.85 and the tines to × 0.9, and added five more tines. I lowered L1 to fill the h .5 row and narrowed the upper trunk (Ø 3.7 / 2.85 / 2.4).
5. The checks found these, all fixed:
   - pit squares collapsed on faces that had no normal yet (`normal_update`);
   - LM's collar face dipped into the bark (out 0.75 → 1.0);
   - RootB's last segment was only 0.21 long (minimum now 0.8);
   - L1's collar took LM's block.

**Comparison cameras (decision 10, spec 3.2 probe).** I probed the f34 at az −20 / 0 / +20 × e 6 / 10 / 14:
- W : H at az −20: 0.967 / 0.934 / 0.906;
- at az 0: 0.920 / 0.892 / 0.868;
- at az +20: 0.868 and lower.

**`f34_sheet` = (−20, 10)**, chosen over e 6 because the sheet's f34 shows a deeper ground band than its front. `r34_sheet` = (160, 10); front, side and rear are (0 / 90 / 180, 4); top is (0, 89). Every `*_sheet` shot hides the floor and uses a 3× lens (`m033._long_lens`).

## Stage 2 — Optimisation and cleanup

| Object | Tris | Size (studs) | Shells |
| --- | --- | --- | --- |
| TwistedSnag (hero) | **3562** (ceiling 3800) | 17.89 × 17.06 × 18.18 | 142 |
| TwistedSnagTrunkCore | 880 | 8.86 × 11.76 × 12.10 | 1 |
| TwistedSnagBranchA | 216 | 5.94 × 9.27 × 7.10 | 5 |
| TwistedSnagBranchB | 172 | 4.08 × 3.85 × 6.85 | 5 |
| TwistedSnagBranchC | 152 | 6.77 × 2.98 × 2.93 | 5 |
| TwistedSnagRootA | 120 | 4.75 × 2.89 × 2.21 | 5 |
| TwistedSnagRootB | 104 | 3.92 × 4.70 × 2.05 | 4 |
| TwistedSnagRootC | 120 | 4.77 × 2.79 × 2.13 | 5 |

- Hero tris by shell kind:
  - trunk: 880 (1 shell);
  - limbs, branches, tines, root modules and toes: 1508 (42);
  - pegs: 132 (11, hidden);
  - rocks and pebbles: 246 (11);
  - moss pads: 260 (10);
  - blades and hubs: 536 (67).
- Size against the targets:
  - height 18.18 (18 ± 0.4) ✓;
  - width 17.89 (17.6 ± 0.9) ✓;
  - depth 17.06, against the spec's "about 15": the FR limb runs to y −7.9, and the back roots and RK6 run to +8.5.

  The origin is at the bottom centre; the hero offset is (0.144, −0.183, 0) from the trunk axis.
- Every object has:
  - 0 non-manifold edges and **0 bowtie verts**;
  - 0 boundary, wire, loose, zero-area, n-gon or duplicate verts;
  - outward normals and applied transforms;
  - its origin at the bottom centre (`o["m053_offset"]`).
- Per shell, in all eight objects: **0 winding errors** (`BMEdge.is_contiguous`), **0 self-intersections**, and volume > 0.
- `K.check` is clean. Baked-shading correlation (limit 0.5): hero 0.15, core 0.28, roots 0.13–0.34, branches 0.0.
- **Contact:** 0 floating and 0 unchained in all eight objects (tolerance 0.03). The hero, core and roots chain to the ground; the branch parts chain to their main chain.
- **Buried:**
  - 0 of 77 dressing shells sit more than 0.05 inside wood or rock (max 0.028, a moss pad edge at the trunk foot);
  - 0 rocks sit more than 0.05 into the roots (all six were placed at 0.0 depth; none had to move).
- **Pegs** (`plug_report`): every peg corner is 0.015–0.122 from the socket walls and floor, and none is inside the trunk solid.
- Smallest corners:
  - trunk core: 2.14° (`m012._force_slivers` forced 14 slivers open);
  - hero: 0.5° on 22 faces, at the pit-square zips and mitred tine starts in the branch shells. They are flat, opaque and harmless (a leftover).

## Stage 3 — UV

`M.smart_uv` angle-based (45°, margin 0.008) plus `m012._uv_unfold` (6 faces cut free on the hero). All eight objects have:
- 0 overlaps and 0 flipped;
- a minimum island gap of 0.016 and a border of 0.008;
- density 1.0 / 1.0 / 1.0;
- conformal stretch p95 ≤ 1.089 (BranchC; the others are ≤ 1.029).

Islands: hero 1116, core 222, branches 56 / 39 / 40, roots 31 / 25 / 30.

## Stage 4 — Materials, colour and texture

1. **`K.calibrate`** on the dome to the spec 5.4 targets; every key rendered within 6 of its target:

   | Key | Calibrated |
   | --- | --- |
   | wood | `#90532B` |
   | wood_dark | `#6A4427` |
   | wood_light | `#C69B60` |
   | hollow | `#170100` (set by hand to `#1E0E06`: the calibrated value was too red-black) |
   | rock | `#9B9894` |
   | rock_light | `#A39E9A` |
   | rock_deep | `#7A787B` (B > G, so set warm by hand to `#7C7974`) |
   | moss | `#9E9610` |
   | grass | `#979E0D` |
   | grass_deep | `#40530C` |
2. **Re-measured on the renders** (study masks) and nudged:
   - wood → `#985B2D`: its lit tone was 28 low;
   - grass → `#8F9E10`: greener, per the spec's "lime, not yellow-olive".

   **Final `PALETTE`:** wood `#985B2D`, wood_dark `#6A4427`, wood_light `#C69B60`, hollow `#1E0E06`, rock `#9B9894`,
   rock_light `#A39E9A`, rock_deep `#7C7974`, moss `#9E9610`, grass `#8F9E10`, grass_deep `#40530C`.
3. **Roles (never by facing).** `.normal` is used only for pit geometry, never for colour.
   - Trunk:
     - the flank facets (touching two pulled-in groove verts) and the buttress walls in the grooves are 30 % wood_dark;
     - low buttress faces (centre z < 0.42) are 30 % dark;
     - the underside disc is wood_dark;
     - cut faces (the top, collar and stub faces, the knot rim, the boss) are wood_light;
     - every hole (sockets, the top socket, the pin, the knot, the pits) is hollow;
     - Tint: ±0.05 per plank, held up each strand column, plus a broad mottle (0.03 / 0.35).
   - Limbs:
     - the base segment is 30 % dark (under the collar);
     - each later segment is 0–12 % lighter toward the tips (position along the limb);
     - tines and side branches are 10 % light;
     - tine ends are pale (cut) or hollow (dark), about half each;
     - LM's snapped end is jagged pale facets round a hollow centre;
     - pits are hollow;
     - Tint: ±0.04 per segment plus mottle (0.04 / 0.4).
   - Roots:
     - faces low on the root are 30 % dark;
     - the top plank is 15 % light (its place on the section);
     - the end is deep, the base face pale, the pits hollow;
     - on the toes, the low faces are 30 % dark and the ends alternate hollow and pale.
   - Rocks go by height band: the top 30 % → light 60 %, the next band → light 30 %, the lowest 22 % → deep 30 %, plus ±0.03 Tint per facet.
   - Moss pads have a 20 % grass rim.
   - Blades: the tallest are lime (grass); the lower and inner ones are grass → deep 55 %. Hubs are deep.
   - I did not darken a ring at each kink (spec 5.5). Each limb segment is a single facet band, so a ring at a kink would darken a whole segment. The kinks read through the pits and the lighting instead.
4. **Finish:**
   - wood 0.9 (dark 0.95), cut wood 0.85, hollow 1.0;
   - rock 0.85 (deep 0.9);
   - grass and moss low spec;
   - no emission.

**Measured against the sheet** (ours / sheet, study masks, `mr.py`):

| View | W : H | T | G | R | fill |
| --- | --- | --- | --- | --- | --- |
| f34_sheet (−20, 10) | 0.932 / 0.971 | 79.2 / 78.0 | 7.3 / 7.9 | 13.3 / 12.2 | 0.442 / 0.437 |
| front_sheet (0, 4) | 0.938 / 0.976 | 80.5 / 77.1 | 6.9 / 8.6 | 12.4 / 11.7 | 0.464 / 0.432 |
| rear_sheet (180, 4) | 0.926 / 0.976 | 80.1 / 79.2 | 6.1 / 7.7 | 13.5 / 10.5 | 0.462 / 0.435 |
| r34_sheet (160, 10) | 0.955 / 0.958 | 78.3 / 78.2 | 7.2 / 8.0 | 14.3 / 11.5 | 0.439 / 0.420 |
| side_sheet (90, 4) | 0.858 / 0.850 | 82.5 / 78.3 | 5.2 / 7.5 | 11.7 / 11.2 | 0.402 / 0.409 |
| top_sheet | W : D 1.123 / 1.015 | 74.6 / 73.0 | 13.6 / 12.1 | 11.8 / 13.2 | |

- **Binding (the decisions' "Binding" rule): on the f34 and front, every share is within tolerance (T ±4, G and R ±3) and fill is within ±0.04, so both pass.** The closest margins are front T +3.4 and front fill +0.032. Rear R is +3.0 (at the edge) and r34 R is +2.8.
- Front width per height (h .0 → 1.0):
  - ours: .10 .92 .73 .30 .29 .72 .73 .89 .77 .35 .02;
  - sheet: .49 .91 .77 .32 .30 .65 .72 .88 .68 .42 .02.

  Every row from h .2 to .9 is within ±0.10. **The bare-trunk rows h .3 / .4 are .30 / .29** (≤ .36).
- Front top profile:
  - ours: .56 .78 .95 .92 .72 .97 .98 .78 .79 .87 .70;
  - sheet: .52 .77 .82 .91 .78 .74 .90 .95 .77 .86 .69.
- Front T fifths: ours 23 / 16 / 27 / 25 / 9, sheet 26 / 21 / 24 / 22 / 7. Fifth 2 is low (see the leftovers).
- Colours (f34):
  - wood median: `#B86C3A` against `#B26634` (6 / 6 / 6 off; R > G > B, hue 24°);
  - wood median, front: `#AD6637` against `#B66936`;
  - wood v > .7: `#C5743F` against `#DA8340`, low by 21 / 15 / 1 because the studio lights both sides (as in 042 and 047);
  - grass and moss v > .7: `#BFC019` against `#BEC20D` (lime);
  - rock v > .7: `#CFC3B3` against `#C5B9AD` (R ≥ G ≥ B, warm, not mauve).

## Stage 5 — Lighting

Skipped (decision 14): the sheet shows no emission or light. Studio notes (Requires Manual Validation): under the game sun,
- the wood should stay orange-brown, not red;
- the pits, knot and sockets should read dark;
- the cut faces should read pale;
- the rocks should read pale warm grey and the grass lime.

## Stage 6 — VFX

Skipped (decision 14): the sheet shows no effect. No object has sockets (`build()` checks this).

## Renders

All in `art/blender/renders/models/M053/`:
- `M053_views.png`: the contact sheet.
- The kit views: `front`, `side`, `rear`, `top`, `underside`.
- The sheet comparisons: `f34_sheet`, `r34_sheet`, `front_sheet`, `side_sheet`, `rear_sheet`, `top_sheet`.
- `front34` / `rear34`, at (−28 / 152, 12).
- `part_*`: the seven parts, at (−25, 18).
- `exploded`: the core in the middle, the six branch modules drawn out along their socket axes, the five root modules along their stub axes.
- `scale`: a 5.5-stud marker at (−6.6, 0.4) under L1. L1's lowest tine, at z 8.4, clears its head by about 2.9.
- Close-ups:
  - `twist_cu`: the crossing strands;
  - `kink_cu`: LM's elbow;
  - `tines_cu`: the leader V and the TL tips;
  - `knot_cu`: a round dark hole in a raised pale ring, with the boss below;
  - `root_cu`: the RT3 and RT4 toes;
  - `base_cu`: the foot, rocks, moss and tufts;
  - `join_cu`: the core's LM collar, a pale cut face round a dark square socket (close-up 1);
  - `peg_cu`: Branch A's peg end;
  - `under_cu`: the dark underside disc with the pin, and the six roots (close-up 2).

## Modeller's notes for the verifier

- **Rebuilding.** In a fresh session run `import kit_mcp; kit_mcp.install(); import m053; m053.build()`. It takes about 1 min to build and about 1 min to render.
  - These re-measure everything: `m053.shells_report(o)`, `contact_report(o)`, `bury_report(h)`, `plug_report(h)` and `limb_visibility(h)`.
  - `build()["problems"]` is empty.
- **Visible limb lengths** (`limb_visibility`; the main chain from the shoulder to the end, as visible 3D / on screen / total, in studs):

  | Limb | Front | Rear | Side | F34 |
  | --- | --- | --- | --- | --- |
  | LEAD | 7.2 / 6.5 / 7.2 | 7.2 / 6.1 | 7.2 / 6.5 | 7.2 / 6.5 |
  | TL | 7.0 / 6.6 | | 6.9 | |
  | LM | 10.8 / 7.2 | 10.8 / 6.2 | 5.8 / 5.8 (its base is behind the trunk) | 10.8 / 8.5 |
  | L1 | 6.4 / 6.2 | 6.4 / 6.1 | **3.1 / 1.8** (L1 runs along −X, behind the trunk and LM from +X) | |
  | R | 9.2 / 8.4 | 9.2 / 8.1 | 9.2 / 6.9 | |
  | FR | 6.8 / 3.7 (it points at the camera, as on the sheet) | | 6.8 / 6.3 | |

  Tine ends seen per view (not hidden by the trunk or dressing): LEAD 4, TL 4, LM 4, L1 4 (3 in the side view), R 5, FR 3. That is all 24.
- Bore pits: 12 on the trunk, 27 on the limbs and 10 on the roots, about 49 in all (40–55 ✓).
- **Leftovers:**
  1. **Deviation from decision 6.** The core's collars, stubs and knot are grown from the body grid rather than unioned; only RT3's toes are booleans. The 1000-tri part limit forced this, and the core is still one clean manifold shell. The stubs are horizontal buttresses with a flat bottom on the ground, rather than prisms angled 25–35° down and out.
  2. The crown still reads as a slightly more upright vase than the sheet's spread. The limbs leave the upper trunk fairly steeply, and the trunk above the crotch (z 9–12) is a touch wide. Front T fifth 2 (h .2–.4) is 16 % against 21 %, and the crown fifths are a little heavy (27 / 25 against 24 / 22).
  3. The lit wood (v > .7) is 15–21 levels below the sheet's lit half, because the studio lights both sides. The medians match.
  4. The side and top are judged for content (decision 9).
     - Side: FR shows out front, LM's stem and TL out back, LEAD and TL up the middle, with roots on both sides.
     - Top: W : D is 1.12, every arm end is seen, and rock and green show between them. The limbs cross near the centre, though, rather than forming the sheet's clean nine-armed star.
  5. The hero is 17.06 deep, against the spec's "about 15", and the rear R share is 13.5, at the edge of ±3.
  6. 22 hero corners are under 2° (min 0.5°), at the pit zips and tine starts. The core's smallest corner is 2.14°.
  7. The part shots at (−25, 18) hide some of Branch A's side branch behind its main stem. The root parts are short and framed close.
  8. No kink-ring wood_dark, because each segment is a single facet band (see Stage 4).
- I made no commits, pushes or exports.

- **Main session (2026-10-30):** the decision-6 deviation is accepted. The collars, root stubs and knot are grown from the body's facet grid instead of unioned, which keeps the core one clean shell at 880 tris.

## Verification round 1 (verifier, 2026-10-30)

Fresh stage-7 verifier, read-only on port 9881 (`wip/M053_verify.blend`, the integrated model; nothing built, edited or
saved). Everything below was re-measured with my own code (scratch `m053_verify/v_mesh.py`, `v_contact.py`,
`v_colour.py`, `v_limbs.py`, `v_cross.py`, `meas.py`); renders went to the scratchpad only (`m053_verify/*_sheet.png`,
`c_*.png`). Shares and colours use the study's own `cls()` masks on both the sheet cells and our renders (our paper
`#F2E8D9`, sampled from the render corners).

### Measured: mesh

| Object | Tris | Size (studs) | Shells | Bnd / NM / wire / loose / zero / n-gon / dup | Bowties | Winding errs | Self-x | Vol < 0 | Min corner (< 2°) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TwistedSnag | **3562** / 3800 | 17.90 × 17.06 × 18.18 | 142 | 0 / 0 / 0 / 0 / 0 / 0 / 0 | 0 | 0 | 0 | 0 | 0.50° (22) |
| TrunkCore | 880 | 8.86 × 11.76 × 12.10 | 1 | all 0 | 0 | 0 | 0 | 0 | 2.14° (0) |
| BranchA | 216 | 5.94 × 9.27 × 7.10 | 5 | all 0 | 0 | 0 | 0 | 0 | 1.24° (5) |
| BranchB | 172 | 4.08 × 3.85 × 6.85 | 5 | all 0 | 0 | 0 | 0 | 0 | 0.52° (4) |
| BranchC | 152 | 6.77 × 2.98 × 2.93 | 5 | all 0 | 0 | 0 | 0 | 0 | 0.50° (4) |
| RootA | 120 | 4.75 × 2.89 × 2.21 | 5 | all 0 | 0 | 0 | 0 | 0 | 5.68° |
| RootB | 104 | 3.92 × 4.70 × 2.05 | 4 | all 0 | 0 | 0 | 0 | 0 | 5.50° |
| RootC | 120 | 4.77 × 2.79 × 2.13 | 5 | all 0 | 0 | 0 | 0 | 0 | 5.53° |

- Every object: bbox centre (0, 0) and min z 0 (origin bottom centre), rotation 0, scale 1, no modifiers, no custom
  normals, flat shading, one UV layer. Winding is checked per edge (`is_contiguous`); with every shell's volume > 0 the
  normals are outward. Self-intersection is a per-shell BVH overlap of non-adjacent faces.
- **The 22 hero corners under 2°** (5 under 1°) are all on tine and side-branch side bands (`wood_x_light_5/10`), not
  pit zips: strips 1.0–2.3 long and 0.011–0.038 wide, folded 2–18° against their neighbours. Not zero-area and not a
  topology fault; at 0.01–0.04 wide they can't be seen. Judged harmless (minor 7).
- Shell kinds (by material): wood 54 (core, 10 module main chains, kids, 11 pegs, RT3 toes), rock 11, moss 10, grass 67.
  Modules: 11 contact groups (6 branch, 5 root), no module intersecting another module or the core.

### Measured: contact

| Check | Result |
| --- | --- |
| Floating (nearest > 0.03 to any shell or the ground), all 8 objects | **0** |
| Unchained to the ground (hero, core, roots) / to the main chain (branch parts) | **0** |
| Buried dressing: rock / moss / grass vertices inside wood or rock (3-ray parity, 2 of 3), 88 dressing shells | 8 touch, max **0.016** (a blade at (−2.1, 6.1)), **0 over 0.05** |
| Pegs (11): overlap with the core / verts inside the core solid / gap to the socket | 0 / 0 / 0.015 each |
| Joints in the hero (renders `c_joint_LM/R/FR`) | no pale ring at any collar; the module base hides the collar face |
| Bore pits (2-tri hollow floors) | 52 (+ sockets, knot, dark ends: 82 hollow islands) |

### Measured: silhouette against the sheet (ours / sheet)

| View (camera) | W : H | T | G | R | fill |
| --- | --- | --- | --- | --- | --- |
| **f34_sheet (−20, 10)** | 0.932 / 0.971 | **78.7** / 78.0 | 7.3 / 7.9 | 13.9 / 12.2 | **0.445** / 0.434 |
| f34 at (0, 12) (check) | 0.881 / 0.971 | 79.0 | 7.2 | 13.6 | 0.463 |
| **front_sheet (0, 4)** | 0.943 / 0.976 | **80.0** / 77.1 | 6.8 / 8.6 | 12.9 / 11.7 | **0.464** / 0.432 |
| rear_sheet (180, 4) | 0.926 / 0.971 | 79.6 / 79.2 | 6.1 / 7.7 | 14.0 / 10.5 | 0.465 / 0.433 |
| r34_sheet (160, 10) | 0.955 / 0.958 | 77.8 / 78.2 | 7.2 / 8.0 | 14.9 / 11.5 | 0.442 / 0.420 |
| side_sheet (90, 4) | 0.861 / 0.855 | 82.0 / 78.3 | 5.2 / 7.5 | 12.2 / 11.2 | 0.403 / 0.406 |
| top_sheet (0, 89) | W : D 1.119 / 1.015 | 74.1 / 73.0 | 13.5 / 12.1 | 12.4 / 13.2 | 0.531 / 0.404 |

- **Binding (f34 and front): T and fill are inside ±4 / ±0.04 on both.** Front T +2.9 and front fill +0.032 are the
  closest margins. G and R are inside ±3 on both.
- Front width per height h .2–.9: ours .73 .30 .29 .72 .72 .88 .77 .35, sheet .76 .32 .30 .65 .73 .88 .68 .42: every
  row within ±0.10; bare-trunk rows .30 / .29 (≤ .36).
- f34 width per height: h .6 **.84 / .51** and h .9 **.34 / .73** are outside ±0.10; the other rows pass. Front top
  profile f .5 **.97 / .75** and f .7 **.78 / .95** are outside ±0.08 (the leader V sits about 1–1.5 studs left of the
  sheet's, so our peak is where the sheet has its centre dip).
- T fifths, f34: 22.6 / 17.7 / 25.6 / 25.8 / 8.3 against 25.6 / 21.3 / 23.7 / 22.0 / 7.4 (all within ±6).
- Rear R +3.5 and r34 R +3.4 are just outside ±3 (non-governing views).

### Measured: skeleton

- **Trunk:** six strands with deep V grooves climbing "/" on the front (`c_twist`, `front_sheet`); it reads twisted and
  planked, not a straight column. Waist rows .30 / .29 of W as on the sheet.
- **Limbs** (my own ray test: main chain centreline toward the camera, blocked by anything including other limbs, so
  stricter than the modeller's `limb_visibility`; visible 3D / on screen, studs):

  | Limb (total) | Front | Rear | Side | f34 | Top |
  | --- | --- | --- | --- | --- | --- |
  | LEAD (7.5) | 5.5 / 5.0 | 6.7 / 5.8 | 3.7 / 3.3 | 4.2 / 4.0 | 3.2 / 2.2 |
  | TL (7.9) | 5.7 / 5.4 | 6.0 / 5.4 | 2.5 / 2.3 | 5.9 / 5.9 | 4.7 / 2.8 |
  | LM (11.2) | 3.7 / 2.7 | 2.6 / 2.0 | 4.3 / 4.3 | 7.7 / 5.8 | 9.5 / 8.3 |
  | L1 (6.9) | 3.1 / 3.0 | 4.7 / 4.4 | 1.0 / 0.7 | 3.5 / 3.5 | 4.6 / 4.2 |
  | R (9.6) | 5.4 / 5.0 | 8.2 / 7.4 | 3.7 / 2.8 | 6.5 / 6.0 | 6.0 / 4.4 |
  | FR (7.2) | 1.6 / 1.1 | 1.6 / 1.2 | 6.0 / 5.6 | 5.0 / 3.5 | 5.6 / 4.8 |

  Every limb has a readable run in the governing f34 (3.5–7.7). The low numbers are geometric and match the sheet: FR
  points at the front and rear cameras, L1 is behind the trunk from +X, and LM's base is behind L1 and its own elbow in
  front and rear. Kinks are hard mitres between straight 6-sided prisms; tines and side branches are 4–5-sided with flat
  square-cut ends, about half pale and half hollow (`c_crown_f34`, `c_crown_rear`). 30 tine and branch ends; 13–15 read
  against the sky in front and f34.
- **Roots:** six (5 modules + the built-in RT3), each ending in 2–3 blunt split toes (`c_under`, `c_roots_front/rear`).
- **Bore pits:** 52, dark squares on facet centres, at kinks and along limbs.
- **Knot:** a ringed hole (dark recess, pale raised rim, pale boss below). It's round and clear in the side view. In
  `front_sheet` it sits on the right flank and reads as a narrow dark oval (about 0.4 : 1) with a thin pale rim, much as
  the sheet's front cell draws it. In `f34_sheet (−20, 10)` it is **hidden** behind the flank, though the sheet's f34
  shows it as its clearest detail (minor 1).
- **Snapped end** on LM: pale broken facets round a dark centre (`c_snap`). It reads as a cut more than a jagged break
  at cell scale.

### Measured: colour (ours / sheet, study masks)

| Region | f34 | front | Notes |
| --- | --- | --- | --- |
| Wood median | `#B86C3A` / `#B26634` | `#AD6637` / `#B66936` | hue 23.5°, R > G > B, orange-brown ✓ |
| Wood v > .7 | `#C5743F` / `#DA8340` | `#C4743F` / `#DC8644` | **21–24 low in R**, 15–18 in G (minor 3) |
| Rock v > .7 | `#D1C5B5` / `#C8BBAF` | `#D1C5B5` / `#CBC3B4` | warm, R ≥ G ≥ B, hue 34°, sat .12; never mauve ✓ |
| Moss (G, h < .03) | `#C8B91E` / `#C8B810` | `#C6B920` / `#C2B620` | matches the sheet's moss (55°) in the lit views |
| Blades v > .7 | `#B7C414` / `#BEC20D` | `#B6C11A` / `#C0BC1B` | lime, 65° ✓ |
| Moss in shaded views | rear `#969118`, r34 `#8C8514`, side `#8D8619` | sheet rear `#BAB414` | reads olive-mustard there and in the top view (minor 4) |

- **Wood dark by position only.** The builder uses `.normal` only for pit geometry (line 252) and the shell-volume
  report; no paint selection reads a normal. Wood lightness against normal: corr z 0.24, x −0.02, y 0.02 (< 0.5). The
  positive z correlation comes from the dark underside disc and the low root faces (both by position).
- `K.check` on all eight objects: **[]** (clean). `kit_baked_shading` 0.15.
- **Tint:** a per-corner `Tint` colour attribute, 0.94–1.08, sd 0.019. The mean neighbour difference is 0.0036 against
  0.0205 for random face pairs, so it is broad and coherent, not confetti. Wood sd 0.023, rock 0.023, grass 0.024 (by
  blade), moss 0.008.
- Finish: wood 0.9, dark 0.95, cut 0.85, hollow 1.0, rock 0.85; metal 0; emission 0 everywhere.

### Lighting, VFX, decisions

- No lights in the collection, no emission, no child sockets on any object: stages 5 and 6 skipped as decided ✓.
- Decisions: 1 size ✓ (18.18 tall, 17.90 wide; 17.06 deep against "about 15", minor 5). 2 names ✓ (no `DeadTree*`).
  3 six modules as tabled, no seventh ✓. 4 six roots, A ×2, B ×2, C ×1 + RT3 ✓. 5 pegs and sockets modelled, hidden,
  no pale ring ✓. 6 ring-stack limbs, kids as buried closed shells; core booleans replaced by grown blocks (the main
  session accepted this) ✓. 7 pits 52 ✓; knot is a hole, not a slot, but hidden in f34 (minor 1). 8 top ring pale
  (`c_topcentre`: broken into fragments by the TL and LEAD bases, not a band in the f34) ✓. 9 side and top judged for
  content ✓. 10 cameras ✓ (f34 at (−20, 10), recorded). 11 collision: hero and core precise, modules hull ✓. 12 the
  hero + seven parts ✓. 13 colour: median ✓, lit tone low (minor 3), wood dark by position ✓. 14 stages 5 and 6
  skipped ✓. 15 budget 3562 ✓, parts 104–880 ✓. Packaging: manifold, 0 winding, 0 floating, 0 buried ✓; rocks are
  angular ring-stack hulls, not eggs ✓.

### Findings

No blockers.

1. **minor: the knot is hidden in the governing f34.** It's correct as a ringed hole and reads in front and side, but
   it is the sheet f34's clearest detail. Fix target: turn the knot about 15–25° toward the front (centre az ≈ 305–310
   on the trunk surface, z 6.9). Check that it shows in `f34_sheet (−20, 10)` as a dark oval with a pale rim, with an
   aspect ≥ 0.55 in `front_sheet`.
2. **minor: the crown is chunkier and less branched than the sheet.** The sheet's limbs taper strongly and end in Y
   forks of two or three blunt tines with small side twigs. Ours stay thick to the end (pipe-like). R and L1 end in
   down-hooked last segments, and several tines are short perpendicular spurs. The mass is right (T, fill and the front
   width rows pass), but the character is heavier. Fix targets:
   - taper every main chain to ≤ 0.45 × its base radius at the end;
   - turn R's and L1's hooked last segments into Y forks of two tines (spec 2.4 tips);
   - give each limb end a two-tine fork;
   - restore the leader V's centre dip in the front (move LEAD's left tine about 1 stud to +X, so the front top profile
     f .5 is ≤ .83 and f .7 ≥ .87);
   - keep fill within 0.43 ± 0.04.
3. **minor: the lit wood is 21–24 levels low in R** (v > .7 `#C5743F` against `#DA8340`). The medians match, and the
   studio lights both sides (the same bias as 042 and 047). Fix target, if the main session wants it: more lit-tone
   spread, for example `wood` toward `#A0612F` with the groove share of `wood_x_dark_30` kept, re-checking that the
   median stays within 20 of `#B26634`.
4. **minor: the moss pads read olive-mustard in the shaded and top views** (rear `#969118`, r34 `#8C8514`; the top view
   shows large yellow pads where the sheet's top cell shows lime clumps at 66°). They match the sheet's moss in the lit
   views. Fix target: `moss` toward 58–60° with V +10 %, and shrink the pads that show between the arms from above
   (top G share 13.5 against 12.1).
5. **minor: the hero is 17.06 deep against about 15**, and rear and r34 R are 14.0 and 14.9 (just over +3). FR's tines
   reach y −7.9, and the back roots and RK6 reach +8.5. Fix target: pull RK6 and the back pebbles in by 0.8–1.0, and
   shrink RK1, RK2 or RK6 by about 10 % so that rear R ≤ 13.5.
6. **minor: the top view is tangled.** The limbs cross over the centre and the pale top ring shows only as fragments,
   rather than the sheet's clean nine-armed star round a pale disc. This is judged for content (decision 9): 8+ arm
   ends, rock and green between, a pale centre. Accepted.
7. **minor: 22 sliver corners under 2° (5 under 1°)** on tine and side-branch side bands (0.011–0.038 wide). Harmless.
   If touched, collapse those under 1° with `m012._force_slivers`, as on the core.
8. **minor: the f34 crown's width rows** h .6 (.84 / .51) and h .9 (.34 / .73) are outside ±0.10 at (−20, 10). The
   sheet's f34 is wider high up (its TL and R tips reach h .88–.90 at the edges). Fix 2 (forked ends) would raise R's
   upper tips. Not binding: the front passes everywhere.
9. **minor: no wood_dark kink rings** (spec 5.5; not in the decisions). The kinks read through the light and the pits.
   Accepted.

Modeller's leftovers judged:
- **"Upright vase":** not confirmed. In the front, every width row from h .2 to .9 is within ±0.10. In the f34 the crown
  is wider at h .6 and narrower at h .9 than the sheet (a flatter spread, finding 8).
- **Lit wood low:** confirmed, 21–24 (finding 3).
- **Top view limbs crossing:** confirmed (finding 6).
- **17.1 deep:** confirmed (finding 5).
- **No darker kink rings:** confirmed and accepted (finding 9).
- The modeller called the slivers "pit zips". They are actually on tine side bands, and are still harmless.

### Score and verdict

**7 / 10. PASS.** The mesh is clean on every count, and contact, pegs, budget, decisions, the binding shares and the
colour family are all met. The skeleton reads as a twisted, kinked, square-tined dead tree in every view. The two
findings most worth a round 2 are 1 (the knot in the f34) and 2 (tapering and forking the limb ends).

## Main session ruling (2026-10-30)
- **Verdict:** passed in round 1 (7/10) and committed.
- **Left for a later polish pass** (the verifier's main targets first):
  - The knot is hidden at the f34 camera. Turn it to about az 305–310.
  - The crown is chunkier and less branched than the sheet. Taper each limb to ≤ 0.45 of its base, give it a Y-fork end, and move the leader's left tine toward +X.
  - Lit wood reads 21–24 levels low.
  - Moss reads olive in shade. Shift it toward 58–60° and raise its value by 10 %.
  - The hero is 17 deep; pull the back rocks in.
  - The top view is tangled.
  - Collapse the 5 slivers under 1°.
- **Export:** 8 assets, 8 solid pieces, 5326 tris, 0 VFX sockets, palette 18 colours, 0 problems.
