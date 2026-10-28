# 021 Root Cluster — spec

Reference: `art/blender/assets/references/021.png`. The sheet's own title is "ROOT CLUSTER — Stylized Environment Asset",
top right "FLINTBORN — Environment Art Reference", footer "FLINTBORN — INDIVIDUAL MODEL STUDY, PAGE 24/132". INDEX.md
row 21 calls it "Flintborn Root Cluster Study". The image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m021.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`
(one modeller does stages 1–6 in a background Blender; the main session does stage 7).

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7).

Sheet text:
- **Modeling notes:**
  - "Composed of a dirt/rock mound base, three root modules and leaf modules."
  - "Roots sit on flat joining surfaces on the rock base."
  - "Leaves are a separate module, placed in central crevice."
  - "Keep forms chunky and readable with broad, flat-shaded faces."
  - "Use clean, low-polygon geometry and simple solid colors." (but see §3.8)
  - "Maintain consistent proportions and silhouette as shown."
  - "Model parts as reusable modules for variation in level design."
- **Palette:** five unlabelled swatches: dark bark, bark, cut wood, mound, leaf (§5.1).
- **Exploded labels:** Leaf Module, Root Module (A), Root Module (B), Root Module (C), Dirt Mound (Base). B and C are
  drawn as **one forked piece** (§1.4).
- **Close-ups:** "Root / Rock Junction" with the label "Flat Joining Surface" (its pointer lands on a pale root tip,
  §3.6); "Underside View" with "Flat Base Surface (for placement)"; "Root Cross-Section" with "Faceted Cross-Section
  (Matches Style)".
- **Game context:** `src` has no root-cluster node (only the `GiantRoots` POI in `PoiCatalog.luau`); GDD.md mentions
  giant roots only as landmarks. The old R06 kit sheet has `RootCluster` (11.5 × 10.4 × 6.5, 2214 tris, 5 roots about
  2 thick, `harvest_hit` + `harvest_deplete`), which owns every `RootCluster*` name (§8).

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is
`#F2EEE9` (242, 238, 233). The masks are `cls()` in `m_cls.py` (HSV; background = max channel difference from the
paper < 16):
- **L, leaves:** sat ≥ 0.30, hue 55–160°, g > 50.
- **C, cut wood:** hue 24–50°, sat 0.15–0.58, v ≥ 0.80.
- **R, root bark:** hue 12–34°, sat ≥ 0.50, v ≥ 0.25. (The mound never reaches sat 0.50 except in deep crevices.)
- **M, mound:** hue ≤ 40° or ≥ 330°, sat 0.12–0.50, v 0.20–0.80.
- **rock:** the M pixels with sat < 0.33 and v ≥ 0.56: the lighter, greyer stone faces. Unreliable on its own (it
  catches only the lit tops of the stones), so shares count **M + rock** as the mound.
- **O, other:** ground shadow, dark edges and text; not counted.

**Scratch study material** (pure Python with Pillow and numpy installed to `pylib/`; no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m021_study\`.
Run with `C:/Users/Orang/.local/bin/python3.14.exe` from that folder (the scripts add `pylib` to the path).
- **Helpers:** `m.py` (loader, HSV, view boxes `V`, hex), `m_cls.py` (masks, preview colours), `bb.json` (silhouette
  boxes).
- **Measurements:** `measure.py` → `measure_out.txt` (bbox, shares, top and root-top profiles, width per height,
  leaf / cut / rock components); `bottom.py` (bottom profiles); `runs.py` (root widths from horizontal runs);
  `mound.py` (exploded mound and part boxes, exploded cut tips); `rad.py`, `rad2.py` (leaf-module radial bands,
  cross-section rings, leaf hub).
- **Layout fitting:** `proxy.py` (dome + root-tube + leaf proxy, orthographic projection into any camera),
  `proxy2.py` (the §2 layout), `proxy3.py` (extents, top/side elevations), `fitleaf.py` (leaf hubs from the hero).
- **Colour:** `samp.py` → `samp_out.txt` (swatches, region medians and quartiles, deciles, height bands, exploded
  parts, close-ups, stones).
- **Crops** (2×): `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `cu_junc.png`,
  `cu_under.png`, `cu_xsec.png`, `pal.png`, `notes.png`; mask previews `cls_*.png`, `cls_row.png`, `cls_expl.png`.
- **Zooms:** `z_expl_A.png`, `z_expl_BC.png`, `z_expl_stub.png`, `z_expl_leaf.png`, `z_expl_mound.png`,
  `z_f34_crown.png`, `z_f34_left.png`, `z_f34_right.png`, `z_f34_tipA.png`, `z_r34_crown.png`, `z_r34_left.png`,
  `z_top_c.png`, `z_rear_c.png`.
- **To run the scripts on our renders,** point `R` (in `m.py`) at the render, set `P` to its background colour, set
  `V` to the render's cell box and re-run `measure.py` (it rewrites `bb.json`).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a resource node / world prop). Hero budget 4000 tris, each part under 1000. The plan
  in §4.3 lands at about 2600–3100.
- **Overall read (check this first).** A **low, lumpy, faceted dirt mound** (mauve-brown, many mid-size flat facets,
  a few lighter grey-brown stones showing between the roots, boulders round its foot) with **three thick, warm-orange
  root modules draped over it from a crown just behind the centre**. Every root end that reaches the ground is a
  **tapered pale cut-wood tip**. **Three bright leaf modules** sit in the crevices at the crown.
  - Root A is an inverted **V/J**: its bend lies on the crown at the back-left; one leg runs down the front-left to a
    pale tip on the ground, the other down the left flank to a pale tip at the back-left.
  - Roots B and C are **one forked module**: a short blunt bark stub at the crown; C runs right and down the
    front-right to a pale tip; B springs off C near the stub, arches up and runs down the back-right to a pale tip.
  - It must read as **roots lying on and gripping a mound**, not a cage of tubes floating over a dome, and not a
    tent of equal tentacles (WorldModeling §6.3).
  - Hero shares: mound 49 %, root bark 35 %, leaves 9 %, cut tips 7 %.
- **Focal silhouettes, in order:**
  1. The front leg of A: a thick, slightly S-curved root falling from the crown to its big pale tip at the front-left.
  2. C falling to its pale tip at the right; the broad lumpy dome between them.
  3. A's left leg sweeping over the left shoulder; the leaf clumps at the left, top and right of the crown.
- **Target size: about 9.4 W × 7.7 D × 5.0 H studs** (H = 0.91 of the 5.5-stud character; roots' top at the crown
  about 4.75, mound crown 3.6–3.7). Root Ø 1.3 (A), 1.2 (C), 1.0 (B). Tolerances W ±0.4, D ±0.4, H ±0.25.
  Decision §8.1.
  - **How it was derived.** The sheet has no character. Two internal anchors agree:
    - the leaf clumps: hero left clump 89 px against a 448 px silhouette; at M019/M020 leaf sizes (span 1.8–2.0,
      leaf L 0.85–1.0) that is **≈ 47.5 px/stud**;
    - the roots: A's front leg measures 60–65 px across (perpendicular to its axis; `runs.py`), C's 52–55 px, so
      Ø 1.3 / 1.15 at 47.5 px/stud, which is a thigh-thick root on the 5.5 character.
    - The fitted layout (§2, `proxy2.py`) then spans 9.44 × 7.7 × 4.92 and reproduces the hero W : H (1.45 against
      the sheet's 1.413) and every tip position within ±0.04 (§2.3).
  - **Why this size.** A waist-to-chest-high harvest node (0.9 C) reads at gameplay distance without towering over the
    player. R06 `RootCluster` was 11.5 × 10.4 × 6.5 (taller than the player, roots 2 thick); our roots stay thick
    but the mound is smaller. Neighbours: M020 Hardwood Stump 9.0 × 8.5 × 4.3, M019 Resin Node 7.0 × 5.9 × 4.45.
- **Build frame:** front −Y, +X right, ground z 0, origin = the mound's plan centre. The bbox centre sits at about
  (−0.2, −0.25); stage 2 re-centres to the bbox bottom centre.

### 1.2 Measured views (`measure.py`, `bottom.py`)

| View (box) | Silhouette bbox (px) | W : H | Leaves L | Cut C | Root bark R | Mound M + rock |
| --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (15,118,510,460) | 52–499 × 126–442 | 1.413 | 8.9 % | 6.7 % | 35.2 % | 49.2 % (rock 2.1) |
| Rear three-quarter (515,118,1010,460) | 546–995 × 123–442 | 1.406 | 11.4 % | 6.0 % | 38.5 % | 44.1 % (0.9) |
| Front (12,500,282,712) | 25–271 × 528–697 | 1.453 | 9.0 % | 6.6 % | 35.3 % | 49.1 % (1.9) |
| Side (286,500,508,712) | 299–498 × 526–696 | 1.170 | 10.2 % | 8.4 % | 35.9 % | 45.5 % (0.7) |
| Rear (516,500,778,712) | 524–770 × 526–700 | 1.411 | 12.7 % | 7.0 % | 35.5 % | 44.8 % (0.8) |
| Top (782,500,1012,712) | 796–999 × 500–696 | 1.036 | 9.0 % | 8.7 % | 43.9 % | 38.4 % (1.8) |

- **The "Front" cell is the f34 drawing again** at 0.55 scale: every component sits at the same fractions (leaves
  .197/.194, .566/.557, .750/.745; tips .315/.309, .909/.921; stones .145/.144, .318/.313, .598/.600) and the profiles
  agree within 0.03.
- **The r34 cell is the hero drawn again** with small changes (same stones .327/.600, same right tip .909, same crown
  clumps), not a view from the back (§3.2).
- **Verifier tolerance:** shares ±4 points (C ±2); positions ±0.06 of W/H unless stated.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .22 | .49 | .60 | .68 | .78 | .83 | .88 | .92 | .90 | .89 | .92 | 1.0 | .93 | .86 | .85 | .88 | .87 | .69 | .58 | .48 | .36 |
| r34 | .35 | .47 | .57 | .65 | .75 | .82 | .88 | .90 | .88 | .92 | .97 | .95 | .91 | .84 | .87 | .86 | .67 | .55 | .50 | .42 | .21 |
| Side | .15 | .30 | .44 | .58 | .67 | .72 | .77 | .81 | .94 | .92 | .95 | .99 | .88 | .88 | .80 | .80 | .65 | .50 | .46 | .40 | .27 |
| Rear | .27 | .40 | .55 | .65 | .70 | .86 | .86 | .86 | .91 | .89 | 1.0 | .90 | .86 | .86 | .87 | .87 | .67 | .61 | .51 | .39 | .24 |
| Top | .42 | .58 | .68 | .72 | .77 | .85 | .92 | .94 | .93 | .92 | .90 | 1.0 | .96 | .91 | .89 | .88 | .83 | .75 | .71 | .67 | .40 |

**Root-bark-only top line** (leaves excluded: where the roots lie; 0 = no bark in that column):

```
f34   .00 .48 .58 .67 .78 .83 .88 .91 .90 .86 .85 .84 .82 .86 .71 .70 .71 .68 .58 .32 .34
side  .00 .08 .43 .57 .67 .72 .76 .81 .82 .72 .78 .77 .79 .79 .68 .64 .61 .32 .12 .22 .00
rear  .00 .25 .53 .64 .70 .71 .71 .85 .84 .78 .83 .84 .86 .86 .76 .72 .67 .61 .49 .37 .00
top   .00 .56 .68 .72 .77 .85 .91 .94 .93 .92 .76 .81 .82 .88 .89 .80 .82 .74 .71 .58 .37
```

**Bottom profiles** (lowest silhouette pixel per column; the base outline): f34 `.21 .16 .09 .07 .08 .07 .06 .03 .01
.00 .00 .01 .03 .06 .06 .07 .09 .10 .10 .11 .19` (the base curves up 0.07–0.10 H toward the sides: elevation ≈ 18–20°);
side `.10 … .01 .01 .01 .08 .25` (nearly flat: ≈ 8°).

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .07@.45 .88@.06 .99@.01 .92@.04 .96@.03 .87@.06 .79@.10 .68@.16 .59@.22 .33@.32 .01@.55
r34    .05@.50 .77@.15 .94@.06 .95@.00 .94@.02 .84@.06 .72@.12 .62@.16 .50@.24 .29@.32 .01@.51
front  .10@.43 .93@.06 .99@.00 .91@.04 .88@.04 .83@.06 .78@.10 .67@.16 .57@.23 .33@.31 .01@.54
side   .06@.81 .97@.00 .91@.02 .94@.05 .85@.09 .73@.12 .64@.17 .53@.23 .47@.33 .20@.38 .03@.55
rear   .13@.44 .82@.10 .92@.08 .96@.01 .89@.05 .81@.09 .74@.12 .58@.19 .47@.26 .19@.40 .02@.49
top    .03@.24 .60@.20 .86@.11 .87@.08 1.00@.00 .92@.03 .92@.06 .81@.12 .60@.22 .45@.28 .03@.55
```

**Components** (`measure.py`): centre (f, h); extent; size in px.

| View | Pale cut tips | Leaf clumps | Stones (lit) |
| --- | --- | --- | --- |
| f34 | A-front .315, .247 (f .23–.40, h .10–.39, 77 × 93); C .909, .215 (f .85–.96, h .10–.32, 53 × 70) | left .197, .631 (f .10–.29, h .50–.75, 89 × 80); top .566, .897 (h .82–1.0, 74 × 57); right .750, .793 (f .67–.83, h .69–.88, 74 × 60) | .145, .185 (front-left pebble); .318, .574 (under A's bend); .598, .541 (between A and C, 41 × 51) |
| r34 | far-left .036, .375 (h .31–.46); A-front .357, .119 (h .02–.20); a sliver at the crown .455, .797 (11 × 16); C .909, .224 | left .219, .617 (+ a stray leaf .181, .508); top .531, .892; **centre .552, .527 (h .44–.63, 62 × 62, in the front crevice)**; right .704, .791 | .327, .558; .600, .561 |
| front | .309, .281; .921, .209 | .194, .634; .557, .902; .745, .802 | .144, .191; .313, .585; .600, .541 |
| side | left .068, .203 (f .00–.14, h .09–.32); right .824, .139 (f .73–.91, h .02–.27) | top .499, .844 (f .37–.67, 61 × 56); right .729, .727 | — |
| rear | left .039, .313; centre .498, .094 (h .01–.21); right .936, .269 | a crown spray f .21–.77, h .45–1.0 (4–5 pieces) | — |
| top | left .043, .456 (h .37–.56); front .281, .120; right-low .911, .238; right-high .929, .638 | crown .531, .874 + .668, .761 (one module round the hub, split by a root) | .542, .120 (front base); .616, .488 |

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, governs; `f34.png`, `cls_f34.png`).** The fit (§2.3) puts the camera **straight in
front (az ≈ 0) at e ≈ 20°**, not at a three-quarter azimuth.
- **Mound:** a broad lumpy dome, 0.88–0.99 W wide from h .1 to .4, narrowing to 0.59 W at h .8; its own top is hidden
  under the roots. Broad flat facets about 30–50 px (0.6–1.0 stud) across, each split into 2–4 triangles of slightly
  different tone. Boulders bulge out of its foot: a big trapezoid boulder at the front centre (f .40–.61, h 0–.2), a
  pebble at the front-left (f .12–.17), lumps at the right edge (f .9–1.0, h .3–.5) and the far left.
- **Stones:** two lighter, greyer lumps show **in the crevices**: one under A's bend between its legs (f .32, h .57),
  one between A's front leg and C (f .60, h .54, the larger). They are the crown and upper-left mound lumps (§1.4).
- **Root A:** its bend lies on the crown at the upper left (root top line .88–.91 at f .30–.40). The front leg falls
  with a slight S-curve down to the big pale tip (f .23–.40, h .10–.39); the left leg runs over the left shoulder to
  the far left edge (f .0–.1, h .2–.48), where its tip is **hidden** behind the left base boulders.
- **B/C fork:** a blunt brown stub end faces the camera at the crown centre (f .5–.6, h .8–.9, `z_f34_crown.png`). C
  runs right along the crown (root top .82–.86 at f .55–.65), bends on the right shoulder (f .7, h .7) and falls to its
  pale tip at the right (f .85–.96, h .10–.32). B's upper arch shows behind C at the upper right (f .8–.9, h .55–.7);
  its tip is hidden.
- **Leaf clumps:** left (on A's left leg, the biggest), top (behind the stub at the crown, the highest point of the
  silhouette), right (on the fork between B and C).

**Rear three-quarter (`r34.png`).** The hero again from slightly further left (fits az ≈ −12, e ≈ 15; §3.2): A's
left-leg tip now shows at the far left, the front tip sits lower, and a **small fourth leaf clump** sits in the front
crevice between A's front leg and C, in front of the larger stone.

**Side (`side.png`).** A narrow drawing (W : H 1.17): one root **arch** over the mound with a pale tip at each end
(left .068, .203; right .824, .139) and leaves on the apex and the right shoulder. It fits the **kit side camera at
+X** with the B/C fork as the arch: C running to the front (screen left), B to the back (screen right, the model's back
at az 90) (§3.3).

**Rear (`rear.png`).** Three tips (far left raised, centre near, far right) and a wide crown spray of leaves. Its
composition (a root coming straight at the camera, roots to both sides) is the hero composition again; no single
back camera reproduces it from the hero's layout (§3.4).

**Top (`top.png`, `z_top_c.png`).** Not a plan view: the hero from about **e 50°** at the same azimuth (§3.5).
- Roots radiate from a hub just behind the centre, under the crown leaf module (a brown knob `#996948` shows at the
  hub);
- 4 pale tips: A-left at the far left (.043, .456), A-front at the front-left (.281, .120), C at the front-right (.911,
  .238), B at the back-right (.929, .638);
- the two stones show at the front base (.542, .120) and between the roots (.616, .488).

**Close-ups.**
- **Root / Rock Junction** (658,790,925,950): a root lies on a mound slope, a leaf clump behind it; its pale tip is
  a long faceted taper. The root's underside meets the mound with no gap and no seam: one clean contact line ("Flat
  Joining Surface", §3.6).
- **Underside View** (658,1000,1005,1205): a **flat, lobed base** (`#73594D`, flat-shaded); 4 pale root tips stick out
  past the base outline (left ×2, back-right, right). The base outline is an irregular blob, about 1.6 : 1.
- **Root Cross-Section** (660,1250,883,1420): a straight-cut root end, a **10–11-sided** faceted disc: a light centre
  (r < 0.3 R), a slightly darker ring (0.3–0.6 R), a light outer band (0.6–0.9 R) and a thin edge (§5.3).

### 1.4 Parts (Exploded Construction (15,725,637,1240), `expl.png`)

Scale: the exploded roots measure about 54 px across (A) and 57 px (C) → **about 43 px per stud** (× 0.9 of the f34).
Facet language everywhere: broad flat-shaded facets, irregular triangles, no smoothing.

#### Dirt Mound (Base): about (120,1015,465,1215), 345 × 200 px (`z_expl_mound.png`)

- **What it is:** a broad dome built from **overlapping faceted lumps**: a crown lump on top, an upper-left lump (the
  dashed arrow lands on it), a centre-front lump, a big trapezoid boulder at the front foot, a small pebble at the
  front-left foot, and lumps round the back and right. W : H 1.70 as drawn (≈ 7.9 × 4.6 at 43 px/stud, including the
  view's elevation).
- **Colour:** the top fifth is greyer (sat 0.30) than the middle (sat 0.38–0.39): the upper lumps are the "rock" of
  "dirt/rock mound" (§5.3).
- **Construction:** `_mound(seed)`:
  - a core dome (16-gon footprint, semi-axes 3.8 × 3.4, 4 height rings, top 3.2, ring centres offset ±0.15, radius ±6 %
    by broad sectors), flattened at z 0;
  - **lumps** with `K.hull_rock` (WorldModeling §12.1: 5–8-sided footprints, 2–3 rings, quiet tops), each sunk 30–45 %
    into the core (§2.1 table);
  - one exact union, floor cut at z 0, a flat underside;
  - facets about 0.6–1.0 stud; each broad face split into 2–4 triangles by beauty fill (the sheet's tone breaks).
- **Triangles:** core about 200 + 11 lumps × 50–70 → about **800–950** after the union (limit 1000 as a part).

#### Root Module (A): (47,855,278,1078), 232 × 224 px (`z_expl_A.png`)

- **Shape:** an inverted **J/V**: a long leg and a shorter leg joined by a rounded knee. Both legs end in pale tips.
  As drawn, the long leg is about 4.9 Ø, the short leg about 2.8 Ø, the tips 125 px (2.9 Ø) apart. In the hero
  both legs are long (about 4.1–4.6 Ø each, §2.2); the hero governs (§3.7).
- **Section:** a 10-sided tube (cross-section close-up), Ø 1.3 at the knee, tapering to 1.15 at the tip collars;
  ring radius ±6 %, ±8° twist per ring, vertex jitter ±0.04, so the long facets break into irregular triangles.
- **Knee:** 3–4 rings round the bend, outer side slightly fuller (+5 %), so it reads as a thick elbow, not a pipe bend.
- **Tips** (`z_f34_tipA.png`): the last 1.2 Ø is **pale cut wood**, a tapered faceted cap: the bark/cut boundary is a
  **slanted collar** (about 35° to the axis, not a square ring); the cap narrows to 0.45 Ø and ends in a small flat
  end face (10-gon). Long facets run along the cap; no rings on its sides.
- **Construction:** `_root_tube(path, radii, seed, sides=10)` along a Catmull–Rom path through the §2.2 control
  points (resample to stations about 0.7 apart, 0.4 round the knee; the two legs total about 11 studs);
  `_tip(collar_frame, len, r0, r1)` for the caps.
- **Triangles:** 10 × 2 × about 17 stations ≈ 340 + 2 tips × 50 ≈ **450**.

#### Root Module (B) + (C): one forked piece (313,832,606,1129), 294 × 298 px (`z_expl_BC.png`, `z_expl_stub.png`)

- **C, the main limb:** from a **short blunt stub** at the crown end (brown bark, rounded end, no pale cut; it
  protrudes about 0.7 Ø past the fork) it runs out and down to a pale tip. Ø 1.2 → 1.05. One gentle bend.
- **B, the branch:** springs from C just past the stub (child radius 0.85 of C, WorldModeling §6.3), **arches up**
  above C and descends to its own pale tip. Ø 1.0 → 0.9. It reads as a hoop rising off C's back.
- **Tips:** as A's (slanted collar, 1.2 Ø long taper to 0.45 Ø, small flat end face).
- **Construction:** C and B as two tubes (`sides` 10 and 9) unioned at the fork (B's base sunk 0.6 into C); the stub is
  C's first 0.8 with a domed bark end (a 10-gon fan raised 0.15).
- **Triangles:** C 10 × 2 × 11 ≈ 220, B 9 × 2 × 10 ≈ 180, stub end 10, 2 tips × 50 → about **500**.

#### Leaf Module: (255,759,380,854), 126 × 96 px (`z_expl_leaf.png`)

- **Shape:** an **eight-leaf star** (7–8 leaves, about 45° apart ±12°) radiating from a **dark hub** (`#2C1A08`, a
  small knob). Each leaf is a broad **pointed kite**: narrow base, widest at about 0.45 L, straight sides to a sharp
  tip, **W : L ≈ 0.42**, with a midrib fold (a lit and a shaded half). Leaves rise 25–50° from the hub plane; the
  back ones stand up more (the hero's crown clump looks upright).
- **Size (hero governs):** clump span **1.9** (left), **1.7** (top, right); leaf L 0.85–0.95, W 0.36–0.40. The
  exploded module is drawn larger (about 2.9 across at 43 px/stud).
- **Construction:** `_leaf_module(span, seed, n=8, fan=360)`: the M019/M020 broad kite recipe (8-point outline
  `[(0.25, 0.40), (0.55, 0.50), (0.82, 0.28)]`, camber 0.06 L, keel 0.03 L, 16 tris each), a hidden 5-sided hub cone
  (10 tris) in `stem` colour. Per leaf ±8 % L, ±6 % W, ±12° yaw, ±6° roll by seed. **Not** `NS["leaf"]` (spiky).
- **Triangles:** 8 × 16 + 10 ≈ **140** per module.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, origin = the mound's plan centre). From `proxy2.py` /
`fitleaf.py`, fitted to the f34 (az 0, e 20) and top (az 0, e 50) cells at once.

### 2.1 Mound lumps (hull rocks on the core dome)

| Lump | Centre (x, y) | Size Ø × height | Sheet evidence | Paint |
| --- | --- | --- | --- | --- |
| Core dome | (0, 0.2) | 7.6 × 6.8 footprint, top 3.2 | f34 width .88–.99 W for h .1–.4 | `mound` |
| Crown lump | (0.2, 0.6) | 2.6, top z 3.7 | under the roots' crossing; the stone at f .60, h .54 is its front face | `stone` top |
| Upper-left lump | (−1.8, −0.6) | 2.0, top 3.2 | the stone under A's bend (f .32, h .57 → X −1.9) | `stone` top |
| Front shoulder lump | (0.6, −1.8) | 2.6, top 2.6 | the broad lit front facets left of C | `mound` |
| Front foot boulder | (0.0, −3.2) | 2.0 W × 1.4 D, top 1.0 | f34 f .40–.61, h 0–.2 (trapezoid) | `stone` 50 % |
| Front-left pebble | (−3.4, −2.4) | 1.1, top 0.7 | f34 stone .145, .185 | `stone` |
| Left shoulder lump | (−3.0, 0.2) | 2.2, top 2.0 | f34 left edge h .2–.45 (hides A-left's tip) | `mound` |
| Left-back foot | (−3.4, 1.9) | 1.4, top 0.9 | underside lobes | `mound` |
| Right lumps | (3.4, −0.4); (3.4, 1.6) | 2.2 / 2.0, top 1.9 / 1.6 | f34 right edge f .9–1.0, h .3–.5 | `mound` |
| Back lumps | (−1.2, 2.6); (1.4, 2.8) | 2.4 / 2.0, top 2.0 / 1.6 | top cell back edge; rear cell | `mound` |

### 2.2 Roots (centre-line control points, x, y, z)

| Root | Control points | Ø (start → end) | Tip end | Notes |
| --- | --- | --- | --- | --- |
| A knee | (−0.9, 0.5, 4.1) | 1.3 | — | on the crown, back-left of the stub; top surface z ≈ 4.75 (f34 root top .91) |
| A front leg | knee → (−1.2, −1.0, 3.6) → (−1.6, −2.4, 2.3) → (−2.0, −3.3, 1.1) → (−2.15, −3.75, 0.5) | 1.3 → 1.15 | f34 f .23, h .10 | slight S-curve; the hero's main read |
| A left leg | knee → (−2.2, 0.6, 3.4) → (−3.3, 0.8, 2.1) → (−4.0, 1.0, 1.0) → (−4.35, 1.05, 0.5) | 1.3 → 1.15 | hidden in f34; top .043, .456; r34 .036, .375 | tip pointing left-back, behind the left shoulder lumps from the front |
| Stub (B/C) | end (0.1, 0.0, 4.2), pointing front-left and up; fork at (0.9, 0.0, 4.1) | 1.2 | domed bark end | faces the camera at f34 f .55, h .85 |
| C | stub → (1.4, −0.2, 3.9) → (2.5, −0.8, 3.1) → (3.3, −1.6, 1.9) → (3.8, −2.3, 0.9) → (4.0, −2.6, 0.5) | 1.2 → 1.05 | f34 f .96, h .10 | bend on the right shoulder |
| B | from C at (0.9, 0.0, 4.1) → (1.4, 1.0, 4.2) → (2.4, 1.7, 3.3) → (3.1, 2.1, 2.0) → (3.5, 2.35, 1.0) → (3.6, 2.45, 0.5) | 1.0 → 0.9 | hidden in f34; top .929, .638; side right .824 | arch top at (1.4, 1.0) |

- **Contact:** every root's underside sinks **0.15–0.25 Ø** into the mound wherever it lies on it ("Roots sit on flat
  joining surfaces"); where a root crosses a hollow, slide the control point down until it touches. The pale tips rest
  on the foot boulders or the ground (tip underside z 0–0.15) and stick out 0.3–0.8 past the base outline (underside
  close-up).
- **Crossing order at the crown:** A's knee lies left of and slightly over the stub; B rises behind C. No root passes
  under another.

### 2.3 Leaf modules and expected numbers

| Module | Hub (x, y, z) | Span | Sheet evidence | Notes |
| --- | --- | --- | --- | --- |
| Left | (−3.0, −0.3, 2.9) | 1.9 | f34 .197, .631 (proxy → .20, .63) | on A's left leg's front flank, leaves fanning up and left (fan 260°) |
| Top (crown) | (0.4, 1.15, 4.4) | 1.7 | f34 .566, .897; top .531, .874 (proxy .57, .91) | in the central crevice behind the stub, between A's knee and B; leaves upright; the highest point (≈ 5.0) |
| Right | (2.15, 0.95, 3.7) | 1.7 | f34 .750, .793; top .668, .761 (proxy .75, .83) | in the crotch between B and C on the right shoulder |
| (Option) Front crevice | (0.6, −1.2, 3.0) | 1.3 | r34 only: .552, .527 | decision §8.4 |

- **Hubs** sink 0.1–0.15 into a root or the mound.
- **Expected hero:** X −4.9 … +4.5, Y −4.1 … +3.6, z 0 … 5.0 → **9.4 × 7.7 × 5.0**.
- **Proxy checks** (orthographic, `proxy2.py`): `f34_sheet (0, 20)`: W : H 1.45 (sheet 1.413), tips Af (.30, .09)
  and C (.93, .13) against the sheet's tip ends (.23–.40, .10) and (.85–.96, .10); B's and A-left's tips must be
  hidden. `top_sheet (0, 50)`: Af .30 (sheet .28), A-left .07, .47 (.04, .46), C .93, .20 (.91, .24), B .89, .67
  (.93, .64). `side_sheet (90, 8)`: Af .08, .24 (sheet left tip .068, .203), B .83 (sheet right tip .824).

## 3. View conflicts and resolutions

### 3.1 The "front three-quarter" is an elevated front view

- **Evidence.** The mound is symmetric about the image centre; the fitted tips land within ±0.04 only at az −5…+5
  (az −28 puts A's front tip at f .56, the sheet has .31; `proxy.py`). The base outline curves up 0.07–0.10 H at the
  sides: e ≈ 18–20°.
- **Resolution.** Compare the f34 and front cells with an extra **`f34_sheet (0, 20)`**. The kit `front34 (−28, 12)`
  has no sheet counterpart: self-consistency only. The hero governs (WorldModeling §1.1).

### 3.2 The rear three-quarter is the hero again

- **Evidence.** Its stones (.327/.600) and right tip (.909) sit where the f34's do; it shows the same three crown
  clumps. A real back view would put C's tip on the left and hide A's front tip. The differences (A-left's tip at the
  far left, a lower front tip at .357) match the proxy at **az ≈ −12, e ≈ 15** (Af .35).
- **Resolution.** Compare with an extra **`r34_sheet (−12, 15)`**: shares ±5, A-left's tip visible at the far left,
  3 crown clumps (+ the optional crevice clump). The kit `rear34 (152, 12)` has no counterpart: self-consistency only.

### 3.3 The side cell is the +X side, drawn narrow

- **Evidence.** Two tips and one arch: from +X the B/C fork makes exactly that arch (C to screen left, B to screen
  right = the back), with the crown and right clumps on top. The proxy gives W : H 1.37 at e 8 against the sheet's
  1.17, and it also shows C's tip low and near (f .25), which the sheet leaves out; A's front tip sits at the far left
  (.08, .24), where the sheet draws its left tip.
- **Resolution.** Compare with **`side_sheet (90, 8)`** by shares (±5), the arch over the mound, tips at the far left
  and right (±0.08), leaves on the apex; accept W : H up to +20 % and the extra near tip; record both.

### 3.4 The rear cell cannot be reproduced

- **Evidence.** From the back (az 180) the layout gives B near at the left (.11), C far left, A-left far right (.93),
  A's front tip hidden; the sheet draws a near tip at the **centre** (.498) and W : H 1.41 against the proxy's 1.73.
  Its composition is the hero's (a root coming at the camera, roots to both sides).
- **Resolution.** Compare the kit `rear (180, 4)` by shares (±6), 3 tips, a wide crown of leaves; record the tip
  positions as a known miss. The top view and the hero govern B's position.

### 3.5 The top cell is a high front view

- **Evidence.** Tip fractions match the proxy at (0, 50) (§2.3), but its W : H 1.036 is far below any orthographic
  view of the layout (1.23–1.32 at e 50–70): the sheet's view is a perspective shot from above, which enlarges the
  near crown.
- **Resolution.** Compare with **`top_sheet (0, 50)`** by tip positions (±0.06), the 2 clumps at the crown, the stones,
  and shares; don't chase W : H. The kit `top (0, 89)` is self-consistency only (it should show a lumpy oval with 4
  roots radiating from a hub just behind the centre).

### 3.6 "Flat Joining Surface" points at a pale tip

- **Evidence.** In the junction close-up the label's pointer sits on the pale cut tip; the notes say "Roots sit on flat
  joining surfaces on the rock base".
- **Resolution.** The joining surface is the root's contact with the mound: roots sunk 0.15–0.25 Ø into the mound with
  one exact union (a clean contact line, no gap, no pad). No extra pad geometry (decision §8.5).

### 3.7 Exploded against hero

- **A's legs:** drawn 4.9 Ø and 2.8 Ø long; in the hero both are long. The hero governs (front leg about 5.8 along its
  path, left leg about 5.1, from the §2.2 control points).
- **Sizes:** exploded parts are drawn at about 0.9 of the hero's scale but the leaf module larger (2.9 across against
  the hero's 1.7–1.9). The hero governs.
- **B/C stub:** the exploded's stub end is brown, not pale; so is the hero's crown stub. Keep it bark.

### 3.8 "Simple solid colors" against the user's blended-colour rule

- The user's rule wins, and the sheet itself shows painted variation:
  - the mound's upper lumps are greyer and lighter than its middle (`#866A5E` sat .30 against `#7D5B4C` sat .39 in the
    exploded mound, which has no roots to shade it), and the crevice stones render `#9C7A69`–`#A78675`;
  - the roots darken toward their ground ends (exploded A: top third `#9B6141`, bottom third `#835133` = the dark bark
    swatch `#82563E`);
  - the leaves run from dark at the hub (`#428116`) to lime tips (`#7BB330`);
  - the cut end has a darker ring band.
- Keep Tint low so it still reads "clean".

### 3.9 Cross-section close-up against the hero tips

- **Evidence.** The close-up shows a straight-cut root with a full-Ø ringed end face; every hero tip is a tapered pale
  cap with a small end face.
- **Resolution.** Hero tips as drawn (tapered); the cross-section's rings go on each tip's small end face (one ring
  loop), and in full on the `...RootA` part only if the main session wants a straight-cut variant (not recommended).

### 3.10 Effects

- The sheet shows none (no glow, sparkle, dust or chips). Stage 5/6 add nothing by default (§7).

## 4. Construction plan (stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `mound()` → `ArchedRootClusterMound`: core + 11 lumps, flat base. Compare with the exploded mound: crown lump on
     top, upper-left lump, front foot boulder and pebble, W : H ≈ 1.7 from (−20, 15).
   - `root_a()` → `ArchedRootClusterRootA`: knee and both legs, 2 tips. Compare: inverted J, knee fuller, slanted
     tip collars, tips 0.45 Ø.
   - `root_fork()` → `ArchedRootClusterRootFork`: stub + C + B, 2 tips. Compare: B a hoop off C's back, stub blunt
     and brown.
   - `leaf_module()` → `ArchedRootClusterLeafModule`: span 1.9, 8 leaves, dark hub.
   - Render a parts shot (`extra`, about (−20, 15)) laid out like the exploded.
2. **Hero:**
   1. `_paste` (m011 pattern) the mound, A, the fork and 3 leaf modules at §2.
   2. One exact self-union (add pieces one at a time and save between: STAGES "Booleans"), then `union_loose`, then
      `m004.floor_cut` at z 0.
   3. Origin at the bbox bottom centre; transforms applied. One closed shell (decision §8.6).
3. **Budget** (§4.3): hero about 2600–3100 (limit 4000); each part under 1000. If the mound runs over, drop lumps'
   rings to 2 before cutting root sides; roots keep ≥ 9 sides (the cross-section shows 10–11).
4. **Placeholder keys** (stage 1): `m021_mound`, `m021_bark`, `m021_cut`, `m021_leaf`. Stage 4 adds the rest (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** a lumpy mound with three thick roots lying on it, gripping it (no gaps under the roots, no
      floating arches; extra `junction_cu (-20, 25)` framed on C's right-shoulder bend against the junction
      close-up); pale tapered tips; leaf clumps in the crown crevices.
   2. **`f34_sheet (0, 20)` against the f34 cell:**
      - W : H 1.36–1.50; shares within ±4 (C ±2) of 8.9 / 6.7 / 35.2 / 49.2;
      - top profile within ±0.07; root-only top line within ±0.08;
      - pale tips: A-front at .315, .247 and C at .909, .215 (±0.06); **exactly 2 tips visible** (A-left's and B's
        hidden, a sliver ≤ 0.5 % of the silhouette allowed);
      - leaf clumps at §1.2 ±0.06; the stub's end visible at f .5–.6, h .8–.9; the two stones visible (lighter than the
        mound around them).
   3. **`top_sheet (0, 50)`:** 4 tips at §1.2 ±0.06; crown clump at the hub; shares ±5.
   4. **`side_sheet (90, 8)`:** the B/C arch; tips at the far left and right (±0.08); shares ±5 (§3.3).
   5. **`r34_sheet (−12, 15)`:** A-left's tip visible at the far left; shares ±5.
   6. **Kit views** (front34, rear34, front, side, rear, top, underside): self-consistency; the underside shows a
      flat lobed base with 4 tips past its edge.
   7. **Parts against their cells** (§4.1).
   8. **Hero size** 9.4 × 7.7 × 5.0 (±0.4 / ±0.4 / ±0.25).
6. **Stage 2:**
   - zero non-manifold, boundary, wire and loose elements; no zero-area faces or n-gons; normals outward;
   - no faces under 5° where roots, tips, hubs and lumps meet (m011 `_tidy` / `_desliver`);
   - don't decimate the root sections below 9 sides, the tip collars, or the leaves' 8-point outlines.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Mound (core + 11 lumps, after its own union) | 1 | 850 | 850 |
| Root A (10 sides, ~17 stations, 2 tips) | 1 | 450 | 450 |
| Root fork B/C (10 / 9 sides, stub, 2 tips) | 1 | 500 | 500 |
| Leaf modules (8 × 16 + hub 10) | 3 | 140 | 420 |
| **Sum before union** | | | **about 2220** |
| **Hero after union** (contact seams, slivers, floor cut) | | | **about 2600–3100** (limit 4000) |
| Parts: Mound / RootA / RootFork / LeafModule | | | about 850 / 450 / 500 / 140 (limit 1000) |

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 28 × 20 box inside each, x 42–70)

| Swatch (order on sheet) | Box | Hex | HSV | Reads as |
| --- | --- | --- | --- | --- |
| 1 | (42,1291,70,1311) | `#82563E` | 21°, 0.52, 0.51 | dark bark (root ends, undersides) |
| 2 | (42,1329,70,1349) | `#AF7450` | 23°, 0.54, 0.69 | bark (= rendered lit quartile `#B6744D`) |
| 3 | (42,1366,70,1386) | `#E4BA8B` | 32°, 0.39, 0.89 | cut wood (= exploded tips `#E2BA8C`) |
| 4 | (42,1403,70,1423) | `#82685C` | 19°, 0.29, 0.51 | mound / stone (= exploded mound top `#866A5E`) |
| 5 | (42,1440,70,1460) | `#68A12F` | 90°, 0.71, 0.63 | leaf (between the mid and tip bands) |

### 5.2 Rendered regions (`samp.py`, `rad.py`, `rad2.py`; median / lit quartile / shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Root bark, f34 / front / r34 | V | R | `#A06440` / `#A06340` / `#A3643F` | `#C47F54` / `#C48055` / `#C78053` | `#633D28` / `#613D28` / `#643D26` |
| Root bark, side / rear / top | V | R | `#995F3D` / `#955E3E` / `#9A603F` | `#BC784E` / `#BE7A51` / `#BA774E` | `#653E28` / `#5E3B26` / `#69412A` |
| Root bark, exploded A / B+C (unshadowed) | (45,850,300,1080) / (300,820,620,1150) | R | `#955B3B` / `#975E3D` | `#B6744D` / `#B8754D` | `#623C26` / `#65402C` |
| Exploded A by thirds (top / mid / bottom) | A box | R | `#9B6141` / `#955A3A` / `#835133` | | |
| Root bark by height, f34 h 0–.2 / .2–.4 / .4–.6 / .6–.8 / .8–1 | bands | R | `#6F4E35` / `#9D603C` / `#A0633F` / `#A36541` / `#A86946` | | |
| Root bark, junction / cross-section close-ups | cu boxes | R | `#8C5639` / `#8B573A` | `#BA7750` / `#BD7950` | `#5C3824` / `#633D29` |
| Mound, f34 / front / r34 | V | M | `#835E4D` / `#83604F` / `#865F4C` | `#9D745F` / `#9E7661` / `#A0745E` | `#61473A` / `#62483A` / `#624839` |
| Mound, side / rear / top | V | M | `#815D4B` / `#84604F` / `#77584A` | `#99705C` / `#9E7865` / `#967261` | `#64493B` / `#5B4336` / `#564137` |
| Mound, exploded (unshadowed) | (110,1010,480,1222) | M | `#816151` | `#937060` | `#624C42` |
| Exploded mound by height fifth, bottom → top | bands | M | `#7B5E50` / `#7D5B4C` / `#886555` / `#7F6256` / `#866A5E` | | |
| Mound by height, f34 h 0–.2 / .2–.4 / .4–.6 / .6–.8 / .8–1 | bands | M | `#805E4D` / `#825C4B` / `#8A6350` / `#5B473D` (crevices under roots) / `#9C6D54` | | |
| Stones, f34 (under A's bend / between A and C / front-left pebble) | (184,250,204,270) / (310,258,332,282) / (108,378,124,392) | M | `#9C7A69` / `#A78675` / `#99786A` (sat 0.30–0.33) | `#A07D6D` / `#B79F90` / `#9A796A` | `#816558` / `#A07F6D` / `#957669` |
| Mound, underside close-up (flat base) | (658,1000,1005,1205) | M | `#73594D` | `#786054` | `#6F564A` |
| Mound, junction / cross-section close-ups | cu boxes | M | `#8B6555` / `#705345` | `#9B7563` / `#916C5A` | `#765748` / `#402E25` |
| Cut tips, f34 / front / r34 / side / rear / top | V | C | `#E7BD8E` / `#E9C192` / `#E8BD8F` / `#E7BF91` / `#E9C295` / `#ECC597` | `#FCDBB1` / `#FDDCB0` / `#FCDAAE` / `#FDDDB1` / `#FDE1BA` / `#FBD7AA` | `#D2A575` / `#DDAE7B` / `#D2A474` / `#D7AA7A` / `#DAAC7A` / `#D9B080` |
| Cut tips, exploded A / B+C / junction close-up / underside | boxes | C | `#E2BA8C` / `#F4CFA1` / `#F3C998` / `#E8BF92` | `#F5CFA1` / `#FBDAB0` / `#FBD9AD` / `#FBD9AF` | `#D2A677` / `#D9AB7B` / `#E0B280` / `#D5A978` |
| Leaves, f34 / front / r34 / side / rear / top | V | L | `#609C1C` / `#5E981F` / `#5A961B` / `#5D931E` / `#5C8E1D` / `#5E9821` | `#8BBD2A` / `#8FBF2C` / `#89BC26` / `#8DBE2E` / `#81B827` / `#86BB2C` | `#315C14` / `#345B15` / `#325E13` / `#365E13` / `#355912` / `#346216` |
| Leaf module, exploded | (255,760,395,880) | L | `#5A9821` | `#83B92D` | `#3B7719` |
| Leaf hub (exploded) / crown knob (top cell) | (310,808,324,822) / (899,539,911,551) | | `#2C1A08` / `#996948` | | |

**Leaf module, radial from the hub (315, 817)** (px: 0–8 / 8–16 / 16–26 / 26–38 / 38–52 / 52–70):
`#447214` (hub shade) / `#428116` / `#4E8C1C` / `#549321` / `#6CA828` / `#7BB330`.

**Cross-section rings** (centre (807, 1349), r as a fraction of the face radius):

| r / R | 0–.15 | .15–.30 | .30–.45 | .45–.60 | .60–.75 | .75–.90 | .90–1.0 | bark lip |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| median | `#EDC18C` | `#EDC28F` | `#E8B67E` | `#E4B17A` | `#EBC394` | `#EBC495` | `#E7BE8D` | `#895B43` |
| sat | 0.41 | 0.40 | 0.46 | 0.46 | 0.37 | 0.37 | 0.39 | 0.51 |

Deciles (dark → light), f34:

```
root   #503221 #663F2A #7A4D33 #8C583A #9C603E #A56641 #B06E47 #BB774E #C27D53 #CA8457
mound  #4B372D #644B3E #745445 #7C5947 #7F5C4A #88614E #906753 #956C58 #9C725D #A57D69
cut    #CEA271 #D4A777 #DDB282 #DFB688 #E2B98A #EBC190 #F2CA9A #F4CD9F #FBD8AC #FEE2BA
leaves #27460F #346515 #407919 #4A871D #5B9619 #64A01E #6DA823 #76B124 #88BA23 #9BC933
```

### 5.3 How the colour works

**Root bark.**
- One warm orange-brown family: hue 21–23°, sat 0.58–0.62, much more saturated and warmer than the mound (19–20°,
  sat 0.38–0.43). That contrast is the asset's main read: keep it.
- **Painted signals:**
  1. **Darker toward the ground ends:** exploded A's bottom third `#835133` against its top `#9B6141` (no shading
     difference on an isolated part, so paint); the f34's bottom band `#6F4E35`. The dark bark swatch `#82563E` is
     this colour. Field: distance along the root from the crown and world z.
  2. **Slightly lighter on the crown:** f34 top band `#A86946` against mid `#A0633F`.
  3. The undersides are dark from shade (`#633D28` quartile): light, not paint.

**Mound.**
- A muted mauve-brown, hue 18–20°, sat 0.30–0.43, v 0.45–0.55.
- **Painted signals:**
  1. **Stones lighter and greyer:** the crown and upper-left lumps' tops, the front foot boulder and the pebble (sat
     0.30–0.33, `#9C7A69`–`#A78675` rendered; exploded top fifth `#866A5E`), against the dirt body `#7D5B4C`–`#886555`
     (sat 0.38–0.40).
  2. **Dark crevices under the roots:** f34 h .6–.8 `#5B473D` (sat .33). Mostly the roots' shadow, which Roblox doesn't
     cast on itself (no AO), so paint a touch: faces within 0.5 of a root's underside contact.
  3. **Ground contact slightly darker:** underside and lowest band `#73594D` / `#7B5E50`.

**Cut tips.** A pale warm tan (31–33°, sat 0.36–0.41). The renders range `#D2A575` (shade) → `#FCDBB1` (lit facets):
light on the faceted taper, so paint one colour. The end face gets the cross-section ring: light centre `#EDC18C`,
darker ring `#E4B17A` (+0.06 sat, −8 levels), light outer `#EBC394`.

**Leaves.**
- Vivid yellow-green, hue 86–95°, sat 0.73–0.83.
- **Hub → tip** (exploded module, unshadowed): base `#428116` (95°), middle `#4E8C1C`–`#549321` (93°), tips
  `#6CA828`–`#7BB330` (86–88°). The hero clumps follow the same ramp (deciles `#407919` → `#88BA23`).
- The midrib fold gives each leaf a lit and a shaded half (geometry, not paint).

**Hub / stub.** The leaf hub is a tiny near-black brown knob (`#2C1A08`); the crown knob seen in the top cell is the
B/C stub's bark (`#996948`).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

The calibration targets are rendered medians of **unshadowed** regions (exploded parts and close-ups), not swatches.
- **`K.sample` kinds:** `"brown"` for the bark keys (`#965C3C`: r − g 58, sat 0.60, passes) and probably the mound
  (`#816151`: r − g 32, sat 0.37; if `"brown"`'s filter rejects it use `"stone"` or `"all"` on tight boxes);
  `"green"` for the leaves; `"all"` on tight boxes for the cut wood and stones.

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m021_bark` | `#965C3C` (exploded A `#955B3B`, B+C `#975E3D`) | roots, the default | rough 0.9 |
| `m021_bark_dark` | `#835133` (exploded A bottom third; swatch `#82563E`) | the last 1.5 studs of each leg before the tip collar, root undersides by position (bottom 35 % of the local section), the stub's underside | rough 0.92 |
| `m021_bark_light` | `#A56845` (f34 crown band `#A86946`; between median and the Bark swatch `#AF7450`) | root tops within 1.5 of the crown, as a 40 % mix; broad patches | rough 0.9 |
| `m021_cut` | `#E4BA8B` (swatch = exploded A tips `#E2BA8C` = underside tips `#E8BF92`) | tip caps (sides and end faces) | rough 0.85 |
| `m021_cut_ring` | `#E2AE76` (ring `#E4B17A`, pushed 4 levels so it survives) | the ring band on each tip's end face | rough 0.85 |
| `m021_mound` | `#7F5F50` (exploded mound median `#816151`; body bands `#7D5B4C`–`#886555`) | dirt body, the default | rough 0.95 |
| `m021_stone` | `#8A6E62` (exploded top fifth `#866A5E`; swatch `#82685C`) | crown and upper-left lump tops, the front foot boulder, the pebble, a few upper facets | rough 0.9 |
| `m021_mound_dark` | `#6B5145` (underside `#73594D`; crevice band `#5B473D` is mostly shade) | crevices under roots, the lowest 0.3 of the mound and lumps | rough 0.95 |
| `m021_leaf` | `#529020` (exploded mid bands `#4E8C1C`–`#549321`) | leaf middles | rough 0.8, `low_spec` |
| `m021_leaf_tip` | `#74AE2C` (tip bands `#6CA828`–`#7BB330`) | outer 30 % of each leaf | rough 0.8, `low_spec` |
| `m021_leaf_base` | `#428116` (8–16 px band) | inner 25 %, keel faces | rough 0.8, `low_spec` |
| `m021_stem` | `#3A2312` (hub `#2C1A08`, lifted so it isn't black) | leaf hubs | rough 0.9 |

**Calibration warnings:**
- **Mound against bark:** after calibration the f34_sheet medians must keep the sat gap: mound `#835E4D` ±10 with sat
  ≤ 0.45, roots `#A06440` ±10 with sat ≥ 0.55. If the mound drifts orange it merges with the roots.
- **Stones:** they must render lighter and greyer than the dirt around them in `f34_sheet` (target `#9C7A69`–`#A78675`
  ±12 on the two crevice stones), but not white-grey: hue stays 18–22°.
- **Cut tips:** check the f34_sheet median `#E7BD8E` ±10 and the lit/shade spread (≥ 35 levels between quartiles).
- **Leaves:** greens calibrate darker than the painted sheet (kit memory); trust the render match. f34_sheet leaf
  median within 12 of `#609C1C`, sat ≥ 0.75, `m021_leaf_tip` ≤ 90° hue. M019/M020's vivid keys are the nearest
  precedent; don't reuse M018's.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Roots** (fields: arc length s from the crown along each leg, normalised; height fraction within the local
  section; world z):
  - `bark` base;
  - s > 0.7 (toward the tip collar) → up to 60 % `bark_dark`, fading in from s 0.55; the collar ring itself plain
    `bark_dark`;
  - bottom 35 % of each section → 35 % `bark_dark` (position in the section frame, not the normal);
  - within 1.5 of the crown (stub, A's knee, B's arch top) → 40 % `bark_light`;
  - broad patches (`K.patches` scale 0.8, level 0.3) between `bark` and a 30 % `bark_light` mix; never single faces.
- **Mound** (fields: lump membership, world z, distance to the nearest root contact):
  - `mound` base;
  - stone lumps: faces of the crown, upper-left, front foot and pebble lumps above 40 % of their own height → `stone`,
    blending over 2 steps into `mound` below;
  - z < 0.3 → 40 % `mound_dark`; faces within 0.5 of a root contact → 45 % `mound_dark` (soft, 3 steps);
  - broad patches between `mound` and a 30 % `stone` mix on the upper dome (the sheet's lighter facets), never per
    triangle.
- **Tips:** `cut` caps, **hard** edge at the slanted collar; end face: `cut` centre (r < 0.3), `cut_ring` (0.3–0.6),
  `cut` outer, `steps=2` soft.
- **Leaves** (field = each leaf's along-length t): t < 0.25 `leaf_base`; 0.25–0.7 `leaf`; t > 0.7 `leaf_tip`; 3 steps,
  ±0.08 noise on t; keel faces +0.25 toward `leaf_base`; hub `stem` (hard).
- **Hard edges only** where materials meet: bark | cut collar, leaf hub | leaves, root | mound contact (different
  materials, so hard by nature).

### 5.6 Texture (Tint) and finish

- **Tint** (`tint_var` per piece about 0.04):
  - roots: `K.texture` amp 0.05, scale 0.5 (facet-group mottling along the roots);
  - mound: amp 0.06, scale 0.6 (each broad face a slightly different tone, as on the sheet);
  - cut: amp 0.025; leaves: amp 0.035, scale 0.5;
  - never per-triangle confetti.
- **Finish:**

| Material | Roughness | Specular | Metal | Notes |
| --- | --- | --- | --- | --- |
| Bark keys | 0.9 / 0.92 / 0.9 | normal | 0 | matte |
| Mound / stone / dark | 0.95 / 0.9 / 0.95 | normal | 0 | matte earth and stone |
| Cut keys | 0.85 | normal | 0 | matte sawn wood |
| Leaf keys | 0.8 | `FOLIAGE_SPEC` (`low_spec=True`) | 0 | matte |
| Stem | 0.9 | normal | 0 | |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- `f34_sheet`: roots `#A06440` ±10, mound `#835E4D` ±10, cut `#E7BD8E` ±10, leaves `#609C1C` ±12; shares per §4 step
  5.2.
- Parts shot: root A median `#955B3B` ±8 with its bottom third darker than its top by ≥ 12 levels; mound top fifth
  greyer (sat ≤ 0.34) than its middle.
- The two crevice stones lighter than the mound around them by ≥ 15 levels.
- Leaves: tips lighter than bases in the parts shot; a tip end face shows its ring in an extra `tip_cu (-30, 10)`.

## 6. Joins and contact

- **Roots on the mound:** each root sinks 0.15–0.25 Ø into the mound along its contact; exact union; the contact reads
  as one clean line (junction close-up). Lift a control point where a root would sink deeper than 0.4 Ø.
- **B into C:** B's base sinks 0.6 into C at the fork; one exact union; no collar.
- **Tips:** the tip cap is part of its root tube (same vertex rings), so no seam besides the slanted material edge.
- **Leaf hubs:** sunk 0.1–0.15 into their root or the mound.
- **Ground:** floor-cut at z 0 (`m004.floor_cut`): a flat underside ("Flat Base Surface (for placement)"); the tips
  overhang the base outline and must not dip below z 0.
- No coplanar faces between lumps; overlap everything; add union pieces one at a time and save between (STAGES
  "Booleans").

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** an ordinary sunlit root cluster. No glow, light, sparkle, dust, chips or particles anywhere.
WorldModeling §1.2 forbids "an ordinary asset recolored neon with a glow halo".

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight:** nothing on the sheet glows.
- **Studio note (Requires Manual Validation):** check in Studio that the roots stay clearly warmer and more saturated
  than the mound under the game's sun, that the stones read lighter, and that the leaf hub → tip ramp survives the
  palette export.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **Recommended: none.** The sheet shows no effect, and M009 and M011–M020 decided against harvest sockets. Record
  "Stage 6 skipped: sheet shows no VFX".
- **Option** (decision §8.8): the R06 `RootCluster` pair, if the main session wants harvest feedback:
  - `harvest_hit` on A's front leg, about (−1.6, −2.6, 2.4), colour override `["#965C3C", "#E4BA8B"]` (bark and cut
    chips);
  - `harvest_deplete` at the base centre, (0, 0, 0.5), colours `["#7F5F50", "#965C3C"]` (dirt and bark), `shape`
    about [8, 1, 7].
- **Not recommended:** `dust` (nothing floats on the sheet), `ore_glint` (roots don't sparkle), any light.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by `git grep` of the repo, plus every sheet .blend (zstd-decompressed) searched with
`m020_study/blendall.py`:
- **R06 kit:** `RootCluster`, `RootClusterDirtMound`, `RootClusterRoot`, `RootClusterLeafModule`,
  `RootClusterExposedMound`, `RootClusterRootBundle`, `RootClusterRootBundleForked`; keys `r06_dirt`,
  `r06_rootbark`, `r06_cutwood`, `r06_leaf`. (`RootCluster` occurs 59 times in `FlintbornWorldKit.blend`, 57 in
  `R06.blend`; `DirtMound` 6 and `LeafModule` 6–12 in both.)
- **W06:** `FernRootCluster`. **W05:** `*RootModule` names (9 hits in `W05.blend` and the kit file). **M019:**
  `ResinBranchLeafClump`; **M020:** `ChoppedHardwoodStump*`.
- **`src`:** no root-cluster node id.
- `M.mk` would silently rename a clash to `<name>M021`, so avoid all of these.

**Proposed names.** None of these occur in the repo, the decompressed kit .blend or any sheet .blend; `m021_` and
`M021` are unused.

| Object | Part | Why |
| --- | --- | --- |
| `ArchedRootCluster` | hero | R06 owns `RootCluster`; the roots arch over the mound |
| `ArchedRootClusterMound` | Dirt Mound (Base) | R06 owns `RootClusterDirtMound` |
| `ArchedRootClusterRootA` | Root Module (A) | R06 owns `RootClusterRoot`; W05 owns `*RootModule` |
| `ArchedRootClusterRootFork` | Root Modules (B) + (C), one forked piece | as drawn |
| `ArchedRootClusterLeafModule` | Leaf Module | R06 owns `RootClusterLeafModule` |

- Palette keys `m021_*` (§5.4). Collection `Kit/M021 Root Cluster`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **9.4 × 7.7 × 5.0, roots Ø 1.0–1.3** (recommended: leaf- and root-anchored, a waist-to-chest-high
   node), or R06's scale (about 11.5 × 6.5, ×1.25, roots 1.6).
2. **Hero camera:** **`f34_sheet (0, 20)`** governs (recommended, §3.1); the kit front34 is self-consistency only.
3. **Root A's legs:** **both long, as in the hero** (recommended), or the exploded's long/short legs (4.9 / 2.8 Ø).
4. **Leaf modules:** **3 (left, crown, right; the hero and front cells)** (recommended), or add the r34's small
   fourth module in the front crevice (span 1.3, about 140 tris).
5. **"Flat joining surface":** **roots sunk 0.15–0.25 Ø into the mound with one exact union, no pads** (recommended,
   §3.6), or flat pads under each contact.
6. **Hero packaging:** **one closed shell** (recommended: STAGES default), or roots and leaves as separate objects for
   level-design variation (the notes' "reusable modules" are served by the part exports).
7. **Exports:** the hero plus 4 parts (`...Mound`, `...RootA`, `...RootFork`, `...LeafModule`) (recommended). R06's
   drops and depleted mound are not on this sheet and are not built unless asked.
8. **Stage 5/6:** **no emission, light or VFX** (recommended: the sheet shows none; consistent with M009–M020), or the
   R06 `harvest_hit` / `harvest_deplete` pair (§7.2).
9. **Comparison cameras** (recommended, §3): `f34_sheet (0, 20)` for the f34 and front cells, `r34_sheet (−12, 15)`
   for the r34, `side_sheet (90, 8)` for the side, `top_sheet (0, 50)` for the top; kit front34, rear34, front, side,
   rear, top and underside as self-consistency only; extras `junction_cu (-20, 25)`, `tip_cu (-30, 10)` and a parts
   shot `(-20, 15)`.
10. **Tip end faces:** **one ring loop with `cut_ring`** (recommended: carries the cross-section's ring at about
    10 tris per tip), or plain.
11. **Names** as proposed.

## 9. Pitfalls to avoid

1. **A cage over a dome.** The roots lie on the mound and grip it (sunk 0.15–0.25 Ø); no daylight under a root
   except where the sheet shows a gap (none in the hero). Check the junction extra and the f34 root lines.
2. **Tentacles.** Three modules, four tips, different thicknesses (1.3 / 1.2 / 1.0), one fork, one knee; not
   equal-length radial tubes (WorldModeling §6.3).
3. **A smooth dome.** The mound is lumpy: a core plus 11 hull lumps with broad facets 0.6–1.0 across, boulders at the
   foot, two lighter stones in the crevices. No subdivision, no noise displacement (§12.1).
4. **Orange mound / brown-grey roots.** The roots are warmer and much more saturated (sat ≥ 0.55) than the mauve-brown
   mound (≤ 0.45). Check both medians after calibration.
5. **Square-cut or round tips.** Tips are pale tapered caps with a slanted collar and a small flat end face; they rest
   on the ground or a foot boulder.
6. **Comparing with the wrong camera.** The f34 is an elevated front view; the r34 is the hero again; the side is the
   +X arch; the rear can't be reproduced; the top is a high front view (§3).
7. **Spiky leaves.** Broad kites (W : L ≈ 0.42), 8 per module, dark hub; use the broad-leaf recipe, not `NS["leaf"]`.
8. **Floating clumps.** Every hub sinks 0.1–0.15 into a root or the mound.
9. **Colour by facing.** Dark bark goes by arc length and section height; stones by lump; crevices by distance to a
   root contact. `K.check` facing correlation < 0.5.
10. **Exact booleans.** Overlap everything; no coplanar lump faces; add pieces one at a time and save between; remove
    slivers with m011's `_tidy` / `_desliver`.
11. **Mound part over budget.** It must stay under 1000 as a part; drop lump rings before root sides.
12. **Naming clashes** with R06 `RootCluster*`, W05 `*RootModule`, W06 `FernRootCluster` (§8). No commits, pushes or
    exports in the modeller's stages.

## Decisions (main session, 2026-10-28)

All recommendations are accepted:
1. Size: 9.4 W × 7.7 D × 5.0 H.
2. Hero camera: `f34_sheet (0, 20)` governs.
3. Root A: both legs long, as in the hero view.
4. Three leaf modules.
5. Sink the roots 0.15–0.25 Ø into the mound and join them with one union; no pads.
6. One closed shell. Add pieces one at a time.
7. Hero plus 4 parts; no drops and no depleted mound.
8. No VFX.
9. Comparison cameras: `f34_sheet (0,20)`, `r34_sheet (−12,15)`, `side_sheet (90,8)`, `top_sheet (0,50)`.
10. One ring loop on each tip's end face.
11. Names as proposed: `ArchedRootCluster` with `Mound`, `RootA`, `RootFork` and `LeafModule`.
