# 016 Stormglass — spec

Reference: `art/blender/assets/references/016.png` (STORMGLASS, "Individual Model Study", footer "PAGE 16/132";
INDEX.md lists it as 16, "Stormglass Flintborn asset study"; 1024 × 1536 px).
Builder: `art/blender/kit/mcp/m016.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Glow and VFX ship wherever
the sheet shows them. Cracks and glowing seams need real depth. This sheet has no cracks or seams. The equivalent
recesses are the **branch sockets in the sand** (the "Branch Socket (Junction Detail)" close-up). Each is a real pit
with walls and a visible gap round the crystal, not a painted ring (§6).

Sheet text: "Chunky crystalline growth emerging from a rocky sand base. Stylized, low-poly and readable from all
angles. Used as environmental resource/decoration." Palette: Crystal "Bright teal, Flat color, Faceted faces"; Sand
Base "Warm beige"; Base Rock "Neutral gray-brown"; Rock Accent "Darker gray" (but see §3.9). WorldModeling §12.5:
"Stormglass uses short thick branching tube forms embedded in a sand base, not electrical particle strands."

All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, top-left origin. Paper is `#F2EDE6`. Masks (`m.py` `cls()`):
- **C, crystal:** g > r + 35 and b > r + 30.
- **S, sand:** r − b ≥ 36, sat ≥ 0.20, mean ≥ 95.
- **R, rock:** anything else that is not paper (mean < 225).
- The shaded lower-left sand of the top view partly falls into R. `rocks.py` `cls2()` (R = sat < 0.25 and
  mean < 200) separates it. Both masks are quoted below where they differ.

Scratch study material (pure Python, no Blender), in the session scratchpad
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m016_study\`:
- `png.py` (reader, `crop`, `sample`); `m.py` (masks, view boxes `V`);
- `measure.py` (bboxes, shares, top / crystal / crystal-bottom / sand / rock profiles), `runs.py` (crystal runs per
  row; `BB` silhouette boxes), `rowruns.py` (runs in any box), `comps.py` (connected parts), `rocks.py` (rock
  components with `cls2`, top-view rock centres), `samp.py` (median, quartiles, deciles), `spill.py` (colour against
  distance from the crystal), `gridcrop.py` (views with a 10 % grid: `g_front.png`, `g_side.png`, `g_rear.png`,
  `g_top.png`, `g_f34.png`, `g_r34.png`), `viz.py` (mask previews `cls.png`, `cls_top.png`);
- crops: `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `parts.png`,
  `ex_main.png`, `ex_side.png`, `ex_sand.png`, `junc.png`, `pit.png`, `under.png`, `cav.png`, `section.png`, and
  zooms `f34_fork.png`, `r34_fork.png`, `front_fork.png`, `rear_fork.png`, `side_fork.png`, `r34_sand.png`.
- To run them on our renders, point `R` at the render and set `P` to the render's background colour.

## 1. Study (2a)

### 1.1 Classification, size and scale

- **Classification:** full asset (resource / decoration node). Hero budget 4000 tris; each part under 1000.
- **What it is:** one chunky faceted teal crystal "tree" (the **Main Branch**: a thick upright trunk with two
  thick arms, all three ending in flat octagonal caps) set in a **socket** in a low faceted **sand mound**. A ring of
  **grey-brown faceted rocks** hugs the mound's foot, and two more sit on its upper slope by the trunk. The exploded
  view also shows a separate small **Side Branch** (a short Y twig), a second, smaller socket, four reusable rock
  shapes, and three socket cavities in the mound's underside.
- **Target size: about 10.2 W × 8.4 D × 8.0 H studs** over the rocks (H about 1.45× the 5.5-stud character, in
  line with M014 Starstone 7.8, M015 Ember Meteor 7.6 and the old R04 Stormglass 7.95). Tolerances W ±0.5, D ±0.5,
  H ±0.3. The sand mound alone is about 8.4 × 7.3 × 2.1.
  - How it was derived: the front, side and rear cells are drawn at one scale (silhouette height 174 px in each),
    about **19.9 px per stud**. The views look down about 9° (§3.3), so the apparent height is about 8.7 studs for a
    true 8.0. Measured widths: front 215 px (10.8), rear 192 px (9.6), side depth 167 px (8.4). Front and rear
    disagree (§3.5), so W is their mean.
- **Stud mappings used below** (build frame: front −Y, +X right, ground z 0, mound centre at the origin):
  - front view X = (f − 0.50) × 10.8; rear view X = (0.50 − f) × 9.6 (screen right is −X);
  - side view (camera at +X): Y = (f − 0.515) × 8.4, **screen right = +Y (back)** by `build_kit.frame_box`'s
    camera maths (§9, pitfall 13: M013–M015 state the opposite; confirm with a probe);
  - heights z ≈ h × 8.7 − (distance of the point in front of the far ground edge) × 0.156 (±0.4 for far points).

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | Crystal C | Sand S | Rock R (`cls2`) | Crystal span f | Crystal span h |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (25,131,450,468) | 37–427 × 136–460 | 1.20 | 46.0 % | 29.4 % | 24.6 % | 0.17–0.91 | 0.29–1.00 |
| Rear three-quarter (452,110,795,468) | 460–773 × 123–460 | 0.93 | 52.0 % | 26.0 % | 22.0 % | 0.13–0.90 | 0.29–1.00 |
| Front (30,545,279,728) | 41–256 × 548–722 | 1.24 | 52.6 % | 26.4 % | 21.0 % | 0.12–0.94 | 0.26–1.00 |
| Side (283,545,510,728) | 311–478 × 548–722 | 0.96 (D : H) | 54.5 % | 23.7 % | 21.8 % | 0.21–0.86 | 0.26–1.00 |
| Rear (513,545,762,728) | 539–731 × 548–722 | 1.10 | 57.0 % | 21.3 % | 21.7 % | 0.04–0.94 | 0.26–1.00 |
| Top (766,545,1018,728) | 806–974 × 561–722 | 1.04 (W : D) | 34.3 % | 44.3 % | 21.4 % | 0.07–0.83 | d 0.11–0.80 |

- Reading: from every side, about half the silhouette is crystal, standing on a low sand dome that fills the bottom
  quarter to third. From above, a third is crystal.
- **Verifier check:** shares ±4 points (top ±6, §3.2), crystal spans ±0.05, profiles below ±0.06 h.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front | .09 | .21 | .25 | .74 | .76 | .78 | .75 | .61 | .94 | .99 | .99 | .99 | .97 | .63 | .65 | .71 | .78 | .79 | .78 | .73 | .08 |
| Side | .07 | .16 | .20 | .24 | .71 | .78 | .93 | .97 | .99 | 1.0 | .99 | .99 | .94 | .61 | .68 | .69 | .68 | .67 | .20 | .14 | .06 |
| Rear | .07 | .68 | .72 | .74 | .74 | .71 | .60 | .95 | .99 | .99 | .99 | .98 | .93 | .60 | .64 | .75 | .76 | .76 | .75 | .65 | .07 |
| f34 | .16 | .21 | .29 | .34 | .75 | .77 | .77 | .71 | .92 | .98 | 1.0 | 1.0 | .97 | .68 | .71 | .82 | .84 | .84 | .81 | .24 | .13 |
| r34 | .15 | .23 | .25 | .71 | .74 | .75 | .74 | .71 | .64 | .93 | .98 | .99 | 1.0 | .99 | .96 | .70 | .71 | .71 | .67 | .22 | .14 |

**Crystal bottom** (lowest crystal pixel per column: the sand line on the trunk, the arms' undersides; `—` = none):

```
f       .00 .05 .10 .15 .20 .25 .30 .35 .40 .45 .50 .55 .60 .65 .70 .75 .80 .85 .90 .95 1.0
front    —   —   —  .58 .52 .49 .43 .33 .30 .27 .28 .33 .29 .34 .45 .48 .49 .52 .59 .72  —
side     —   —   —   —   —  .58 .37 .26 .28 .30 .29 .26 .27 .30 .34 .44 .48 .55  —   —   —
rear     —  .61 .52 .49 .46 .43 .36 .29 .31 .29 .27 .29 .33 .29 .37 .45 .48 .51 .56  —   —
```

**Sand top** (highest S pixel per column; values at f 0.40–0.65 are where the sand meets the crystal or rock T1):

```
front    —   —  .12 .21 .22 .28 .34 .32 .30 .27 .21 .33 .29 .34 .30 .25 .22 .20 .11  —   —
side     —   —  .10  —  .19 .20 .27 .26 .28 .29 .28 .26 .21 .19 .25 .21 .17 .10  —  .05  —
rear     —   —  .07 .17 .20 .24 .28 .29 .30 .29 .26 .22 .32 .29 .28 .24 .20 .17 .09  —   —
```

**Ground-contact rise** at the silhouette ends (camera elevation cue, §3.3): front 0.080 / 0.057, side 0.040 /
0.029, rear 0.040 / 0.034 (left / right end).

### 1.3 Silhouette and composition per view

**Front (`g_front.png`):**
- **Trunk:** vertical, centred at f 0.51 (X ≈ +0.1). Width 43–49 px (2.1–2.4 studs) from the cap down to h 0.65;
  its cap is the top (h 1.0). The flat cap top shows as a thin ellipse (h 0.95–1.0).
- **Left arm:** leaves the trunk low. Its underside meets the trunk at h 0.33–0.43, the crotch on its upper side is at
  (0.35, 0.61). It rises out-left to a **flat cap tilted up-left**, spanning f 0.13–0.33 at h 0.65–0.70; cap top
  (0.25, 0.78); outer edge X ≈ −4.0.
- **Right arm:** the mirror, a little longer. Underside meets the trunk at h 0.34; crotch (0.65, 0.63); cap tilted
  up-right at f 0.70–0.94, top (0.85, 0.79); outer edge X ≈ +4.6.
- Between h 0.35 and 0.60 the arm roots and the trunk make one wide fork (f 0.29–0.87 at h 0.55).
- **Sand line on the trunk** at h 0.27–0.30. The trunk's foot is partly hidden by rock T1 (f 0.48–0.60,
  h 0.22–0.33).
- **Mound:** a low, broad dome from f 0.06 to 0.92 at its foot; its silhouette rises from h 0.12 (f 0.10) to about
  0.30 by the trunk.
- **Rocks** (`rocks.py`; studs): far-left R10 f 0.00–0.12 (top 0.27); big front-left R1 f 0.10–0.35 (0.20, 2.7 wide);
  front-centre R2 0.43–0.60 (0.13); T1 at the trunk foot 0.48–0.60 (h 0.22–0.33); front-right R3 0.67–0.83 (0.11);
  far-right R4 0.87–1.00 (0.22). Seen over the mound: back-left R9 at f 0.18–0.29 and back-right R7 at 0.68–0.83
  (tops 0.35–0.36).

**Side (camera at +X; `g_side.png`, `side_fork.png`):**
- **Trunk:** cap at f 0.30–0.60 (h 0.80–0.95, 51 px = 2.5 studs: its section is a little deeper than wide), top at
  f 0.45 (Y ≈ −0.5).
- **Near arm** (the right arm, pointing at the camera): reads as a **near-vertical column in front of the trunk** at
  screen left, f 0.21–0.30, cap top (0.255, 0.78). Its cap overlaps the trunk outline: it is nearer than the trunk.
- **Far arm** (the left arm): leaves from behind the trunk's right edge at h 0.45–0.55 and angles up-right to a cap at
  f 0.65–0.86, top h 0.67–0.69.
- Rocks: front-left group f 0.00–0.31 (to 0.32, including T1); low near rock 0.50–0.74 (0.13); T2 / back rocks
  0.57–0.75 (h 0.20–0.31); back rocks 0.78–1.00 (0.22).

**Rear (camera at +Y; `g_rear.png`, `rear_fork.png`):**
- Mirrors the front. Trunk at f 0.47 (X ≈ +0.3), leaning about 5° to +X at the top (optional).
- Screen-left arm (the right arm) cap f 0.04–0.27, top h 0.74; its root passes **behind** the trunk.
- Screen-right arm (the left arm) cap f 0.71–0.94, top h 0.76; its root's top facet crosses **in front of** the
  trunk.
- Rocks: R5 / R6 at f 0.00–0.14 (0.19); R7 0.11–0.35 (0.18); R8 0.48–0.71 (0.16); a low one 0.72–0.84 (0.12); R9
  0.85–1.00 (0.20); T2 at the trunk foot 0.53–0.67 (h 0.22–0.32); front rocks over the mound at 0.16–0.28 and
  0.69–0.82 (0.30–0.31).

**Top (`g_top.png`, `cls_top.png`):**
- The mound is almost round (W : D 1.04), lumpy, with **ten rim rocks** evenly round it at 4.2–4.7 studs
  (top-view scale) from the centre. Angles measured from +X: 177, −153, 140 (the biggest from above, 2.4 × 2.4),
  −117, 95, −71, 58, −35, 25, −5.
- The crystal shows **three flat octagonal caps with radial fan facets**: a big one up-right of centre (f 0.67,
  d 0.65, 2.6 across), one at the left (0.17, 0.38, 2.2) and one at the lower right (0.73, 0.21, 1.9). A thick bar
  joins the left cap through the centre to the big cap, and an arm runs to the lower-right cap: a **T**.
- The T does not fit the other views (§3.2).

**Close-ups:**
- **Branch Socket (Junction Detail), (28,1305,372,1515), `pit.png`:** the crystal's tapering lower end goes down into
  a **squarish/hex pit** in the sand.
  - The pit has steep dark-brown walls (`#88674C`, dark `#69523D`) and a floor `#716357`. It has a slightly raised,
    bevelled rim. At the rim the crystal fills about 0.65 of the opening, so there is a **visible gap all round**,
    widening with depth as the crystal tapers.
  - The crystal below the rim reads dull grey-teal (`#618A87`, sat 0.29).
- **Base Underside (Socket Cavities), (382,1305,700,1515), `cav.png`:** the mound's flat bottom carries **three
  hexagonal blind pockets**.
  - About 1.4 across and 0.4–0.5 deep, in a loose triangle about 2 studs from the centre; same shaded sand
    `#A88261`.
  - Rocks ring the underside's edge.
- **Crystal Branch (Section / Thickness), (700,1305,1018,1515):** a tapering faceted crystal and its cut section,
  which is solid all through: **the branches are solid**, never hollow tubes.

### 1.4 Parts (exploded view (20,795,662,1268) and Parts Breakdown (664,800,1018,1268))

Labels: "Crystal Assembly (Main Branch)", "Crystal Branch (Side Branch)", "Sand Base", "Base Rock (Reusable)",
"Side Branch (Crystal)", "Sand Base (with sockets)", "Base Rock Pieces (Reusable)". The arrows put the main branch's
foot into a socket on the mound top and push the rocks into dents in the mound's flanks.

Scale: the Parts Breakdown's trunk cap (55 px) against the hero's (2.45 studs) gives **about 22.4 px per stud** there.
The exploded is about 33 px per stud. Facet language for every part: medium triangulated facets (0.5–1.2 studs),
irregular but calm, flat-shaded, no spikes and no confetti.

#### Main Branch: exploded (196,802,477,1045) 282 × 244 px; parts (699,827,860,996) 162 × 170 px; crop `ex_main.png`

- **Overall:** about 7.5 studs long (top of the trunk cap to the root tip); arm span about 8.5. It is a solid
  low-poly **tube tree**: three thick limbs with flat ends, joined in a wide fork. It is not a crystal cluster of
  pointed shards.
- **Trunk** (parts runs, top → bottom):

  | Station (t from the top) | Width (studs) | What |
  | --- | --- | --- |
  | 0.00–0.11 | 0.2 → 2.45 | the cap: a low faceted fan dome on an octagon, then a bevel ring |
  | 0.11–0.46 | 2.4 → 1.9 | upper shaft, narrowing slightly downward |
  | 0.49–0.66 | 4.1–6.1 (with arm roots) | the fork |
  | 0.70–0.88 | 2.9 → 2.1 | lower trunk (wider than the upper shaft at first) |
  | 0.88–1.00 | 2.1 → 0.45 | a blunt tapering root (buried, §6) |

  - 8 sides, rings every 0.8–1.0, each ring turned and scaled a little (±8 % radius, ±10° twist). That gives the
    sheet's irregular triangulated facets.
  - **Cap:** a flat octagon of radius about 0.6 R with a centre vertex raised 0.10–0.15 (the top view's radial fan),
    and a bevel ring 0.25–0.35 down to the full radius. The same cap ends every limb.
- **Left arm** (in the exploded drawn at the upper left):
  - Leaves the trunk at t 0.50–0.62. It is about 1.7–1.9 thick at the root and 1.6 at the neck, swelling to a
    2.0–2.2 cap.
  - It runs out and up at about 30–35°, then a short end segment turns up about 20° more to the cap.
  - Length about 3.3 along its axis. 7–8 sides.
- **Right arm:**
  - Leaves a little lower (t 0.53–0.66). It is longer (about 3.8 along its axis) with a clear elbow at 55–60 %: first
    up-out at about 40°, then flatter (about 20°).
  - Cap 2.0 across, facing up and out.
- **Triangles:** about 350–450 for the part (trunk 120–150, arms 2 × 90–120, caps 3 × 24–32).
- **Construction:** three faceted tube limbs (`_limb(path, radii, sides, seed)`: rings along a polyline with parallel
  transport, as R04's `limb()` but without its coral bulges), plus caps. The arms overlap the trunk by 0.4. One exact
  self-union (m011 `_self_union`), then `union_loose`. Rings must stay at least 0.5 apart near the fork so the union
  leaves no slivers.

#### Side Branch: exploded (478,946,581,1054) 104 × 109 px; parts (902,868,981,949) 80 × 82 px; crop `ex_side.png`

- **Shape: a short Y twig**, about **3.6 W × 3.7 H**, all limbs about 1.35 thick with the same flat caps (1.4
  across).
  - The stem rises slightly leaning to a tall cap at the upper left (t 0.0, cap spans t 0.0–0.43).
  - At t 0.45–0.60 an arm leaves up-right at about 45–50° to a lower cap (t 0.24–0.45).
  - Below the fork, the stem tapers from 2.0 (with the fork) to a blunt root point (t 0.67 → 0.98: 2.0 → 1.2 →
    0.45).
- **Triangles:** 160–240. Build from the same `_limb` and cap helpers.
- **Not placed in the hero** (§3.6). It is a reusable part (drops, variants, the second socket).

#### Sand Base: exploded (195,1096,470,1231) 276 × 136 px; parts (694,1029,887,1119); crop `ex_sand.png`

- **Shape: a broad, low, lumpy faceted dome**, about **8.4 × 7.3 × 2.1** (H : W 0.25).
  - The top is gently rounded, almost a plateau.
  - The flanks steepen into a short skirt at the ground.
  - The outline is lobed (7–9 broad lobes, ±6 % radius).
  - Facets 0.8–1.5 studs. A flat bottom.
- **Sockets on top** (exploded):
  - **Socket 1**, larger, hexagonal: the main branch's (§6.1).
  - **Socket 2**, smaller, squarish-hex, beside it: the side branch's.
  - Both have steep walls and dark floors.
- **Rock dents:** shallow dents on the flanks where the rocks plug in. They are hidden by the rocks in the hero; don't
  model them, but sink the rocks 0.2–0.4 into the skirt.
- **Underside cavities:** three blind hex pockets (§1.3).
- **Construction:** hull or ring dome (rings (0, 1.00), (0.45, 0.93), (1.15, 0.78), (1.75, 0.52), (2.05, 0.22),
  top 2.1; 13–15 points per ring on a 4.2 × 3.65 ellipse, broad sector jitter ±6 %). Then `M.carve` the two sockets
  (§6.1). After the hero's floor cut, carve the three underside pockets.
- **Triangles:** 250–400.

#### Base Rocks: exploded cluster; parts (690–990, 1155–1220); four shapes

| Sheet piece | Parts box | Drawn W × H (studs at 22.4 px) | Shape |
| --- | --- | --- | --- |
| A, broad boulder | (690,1155,778,1220) | 3.9 × 2.9 | wide rounded, broad top facet |
| B, dome | (794,1155,856,1205) | 2.8 × 2.2 | rounded dome |
| C, peaked dome | (874,1154,930,1196) | 2.5 × 1.9 | pointed off-centre crown |
| D, small cobble | (945,1157,990,1190) | 2.0 × 1.5 | low small dome |

- The drawn heights include some of the top (3/4 view). True H : W is about 0.55–0.75, and up to 1.1 for the tall
  far-left R10.
- Faceted rounded boulders with a **flat bottom** and 16–24 broad facets (0.5–1.0 studs). Blunt crowns, no needles.
- **Construction:** one part `StormglassStone` from `K.hull_rock` (`keep_bottom=True`), rings about (0.0, 0.92, 8),
  (0.25, 1.0, 8), (0.55, 0.85, 7), (0.80, 0.55, 6), (0.95, 0.2, 3), 30–48 tris. Shapes B–D are build-only variants
  (`_m016_stone_b/c/d`, different seeds and crowns), as M009 and M015 allow. The hero uses transformed copies:
  non-uniform scale 0.5–1.4 per axis, a z turn, mirroring.

## 2. Layout (starting values; tune to §1.2–§1.3 on the sheet-elevation extras)

Build frame: front −Y, +X right, ground z 0, mound centre at the origin. Every piece is a transformed copy of a
finished part mesh (m011 `_paste` pattern).

### 2.1 Crystal (Main Branch, arms on a line about 30° off the X axis, §3.1)

| Feature | Position (X, Y, z) | Size / notes |
| --- | --- | --- |
| Trunk axis | (+0.2, −0.5); vertical (an optional 3–5° lean to +X at the top, from the rear view) | section 2.3 W × 2.5 D at the shaft, 2.6–2.9 just above the sand |
| Trunk cap top | (+0.2, −0.5, 8.0) | cap 2.4–2.5 across; the highest point |
| Sand line on the trunk | z ≈ 1.95 | the trunk enters socket 1 here |
| Root tip | (+0.2, −0.5, 0.45) | buried; ≥ 0.3 clear of the underside pockets |
| **Right arm** (front-right, toward the camera in the front view) | root centre (+1.0, −0.9, 3.4); elbow (+2.5, −1.4, 4.5); cap centre (+3.4, −1.8, 5.8) | cap tilted about 35° toward (+X, −Y); cap top z ≈ 6.3; outer edge X ≈ +4.5 |
| **Left arm** (back-left, behind the trunk in the front view) | root centre (−0.9, +0.1, 3.6); elbow (−2.1, +1.2, 4.6); cap centre (−3.0, +1.9, 5.35) | cap tilted about 35° toward (−X, +Y); cap top z ≈ 5.8; outer edge X ≈ −4.1 |
| Crotches (upper root edges) | right z ≈ 5.2, left z ≈ 4.9 | front-view crotches at h 0.63 / 0.61 |

- The line from the left cap to the right cap runs at about −28° to −32° from +X. That is perpendicular to the kit's
  front34 (−28) and rear34 (152) camera axes, so both kit 3/4 renders show the arms fully spread, as the sheet's
  3/4 views do (§3.1, §3.4).
- The right cap sits about 0.5 higher than the left (the f34's +0.07 h). In the side view the far (left) cap then reads
  lower than the near column, as on the sheet (§3.7).

### 2.2 Sand Base and sockets

| Piece | Position | Size | Notes |
| --- | --- | --- | --- |
| Mound | centre (0, 0) | 8.4 × 7.3 × 2.1 | the peak hides under the trunk; sand z ≈ 1.95 at the trunk, 1.5–1.6 at r 2.5, 0.9–1.1 at r 3.5, 0.3–0.5 at the foot |
| Socket 1 (main) | (+0.2, −0.5) | hex, circumradius 1.65 (flats 2.86); depth 0.70 (floor z ≈ 1.25) | rim lip +0.08 with a 0.2 chamfer; gap to the trunk 0.28 at the flats, 0.5 at the corners, widening with depth |
| Socket 2 (empty) | (−1.6, +1.4) | hex, circumradius 0.75; depth 0.45 | the r34's dimple (§3.6); hidden from the front and the side by the trunk and the left arm's root, from the top mostly by the left arm, and from the rear partly by T2 and R9 (check the rear render; if it shows as a hole there, move it 0.3 toward −X) |
| Underside pockets × 3 | (−1.8, +1.2), (+1.9, +0.6), (−0.2, −2.0) at z 0 | hex, circumradius 0.7, depth 0.45 | carved after the floor cut; at least 0.3 from the root tip and from socket 2's floor |

### 2.3 Rocks (`StormglassStone` copies and variants; floor-cut at z 0)

Top-view Y values are scaled by 0.86 to the side view's depth (§3.2).

| Rock | Centre (X, Y) | W × D × H | Variant | Seen in |
| --- | --- | --- | --- | --- |
| R1 front-left, big | (−2.8, −2.8) | 2.8 × 2.2 × 1.6 | A | front 0.10–0.35 (0.20); f34's biggest front rock; rear over the mound 0.69–0.82 (0.31) |
| R2 front-centre | (+0.2, −3.6) | 1.9 × 1.5 × 1.1 | B | front 0.43–0.60 (0.13) |
| R3 front-right | (+2.4, −3.2) | 1.7 × 1.4 × 1.0 | D | front 0.67–0.83 (0.11); rear over the mound 0.16–0.28 (0.30) |
| R4 right-front | (+3.8, −2.1) | 1.6 × 1.8 × 1.5 | C | front 0.87–1.00 (0.22); top −35° |
| R5 right | (+4.4, −0.3) | 1.3 × 1.7 × 1.2 | B | top −5°; side 0.50–0.74 (0.13) |
| R6 right-back | (+3.8, +1.6) | 1.5 × 1.8 × 1.5 | C | top 25°; rear 0.00–0.14 (0.19); side 0.78–1.00 |
| R7 back-right | (+2.2, +3.1) | 1.8 × 1.4 × 1.5 | B | rear 0.11–0.35 (0.18); front over the mound 0.68–0.83 (0.35) |
| R8 back | (−0.4, +3.6) | 2.1 × 1.3 × 1.3 | A | rear 0.48–0.71 (0.16); top 95° |
| R9 back-left, big | (−3.2, +2.4) | 2.4 × 2.1 × 1.6 | A | top 140° (the biggest from above); rear 0.72–1.00 (0.12 / 0.20); front over the mound 0.18–0.29 (0.36) |
| R10 left, tall | (−4.5, +0.1) | 1.4 × 1.7 × 1.6 | C | front 0.00–0.12 (0.27, the tallest rim rock, peaked) |
| R11 left-front | (−4.0, −1.7) | 1.6 × 1.9 × 1.4 | B | top −153°; f34 left |
| T1 trunk foot, front | (+0.5, −2.5), on the mound | 1.4 × 1.1 × 1.0, sunk 0.3, top z ≈ 2.55 | D | front 0.48–0.60 (h 0.22–0.33), in front of the trunk's foot; f34 the same |
| T2 trunk foot, back | (−0.6, +2.6), on the mound | 1.5 × 1.2 × 0.95, sunk 0.3, top z ≈ 2.35 | B | rear 0.53–0.67 (h 0.22–0.32), in front of the trunk's foot from behind |

- Rim rocks sink 0.2–0.4 into the mound's skirt and may touch neighbours (union). One or two small ones may stay
  separate shells (as M009). **T1 and T2 stay clear of the socket rims** (T1's back edge Y ≥ −1.95; T2 at least 0.1
  from socket 2's rim), so the pits keep their gaps.
- If the rear profile misses by more than 0.05 at f 0.72–1.00, split R9 into a low R9a (−2.7, +3.0; 1.3 × 1.2 × 1.0)
  and R9b (−4.0, +1.8; 1.5 × 1.8 × 1.6), as the rear draws it.

**Expected hero:** about 10.25 × 8.6 × 8.0. Tris: main branch 350–450; sand base 250–400 with five pits; 13 rocks ×
30–48 ≈ 400–600. Union total about 1100–1500. The side branch (160–240) is a separate part.

## 3. View conflicts and resolutions

### 3.1 Which arm points to the front (the main layout decision)

- **Occlusion cues, all strong:**
  - **Front:** the right arm's top facet crosses in front of the trunk's right edge; the trunk's left edge runs
    unbroken over the left arm's root.
  - **Rear:** the reverse. The left arm (screen right) crosses in front; the right arm is behind.
  - **f34:** as the front.
  - **Side:** the near arm stands in front of the trunk at screen left. With the camera at +X that is the right arm
    at −Y; with the camera at −X it is the left arm at +Y.
- **Resolution: right arm front-right (+X, −Y), left arm back-left (−X, +Y)** (layout §2.1), on a line about 30° off X.
- **Against it:**
  - The cap heights in the front and rear orthographic views differ by only 0.01–0.02 h. They imply a slight
    preference the other way, but are within drawing noise.
  - The sheet's r34 draws its screen-left arm in front of the trunk. It reads as the f34 mirrored, which these
    generated sheets often do (as M014 found).
- **Bonus:** this line is perpendicular to the kit's front34 and rear34 camera axes, so the default kit 3/4 renders
  show the wide spread of the sheet's 3/4 views.

### 3.2 The top view's T does not fit

- The top view shows the caps at the left, lower right and upper right in a T, with the biggest (trunk) cap up-right
  of centre. No rotation, tilt or perspective with plausible numbers maps §2.1 onto it. The arms there are about 90°
  apart; in the front and side they are nearly opposite.
- **Resolution:** the front, side and rear govern the crystal. The top view governs only:
  - the round, lumpy mound footprint;
  - the ten rim rocks' angular spacing (§2.3);
  - three flat octagonal caps with radial fan facets seen from above;
  - a crystal share of about 34 % (±6).
- Compare with the kit's top (0, 89, straight down) and an extra `top_tilt` at **(−20, 70)**. The sheet's top looks
  tilted, with high points displaced up-right. Its D also reads about 15 % deeper than the side's 8.4 (tilt adds
  height), hence the 0.86 scale on top-view Y.

### 3.3 Camera elevation

- The ground contact rises 0.03–0.08 h at the silhouette ends, which suggests about 6–8°. The far-side rim rocks show
  over the mound at h 0.30–0.36 in the front and rear, which needs about 10–11° (at 6° they would be 0.5 stud
  taller than the near view shows them). The trunk's cap top shows as a thin face.
- **Resolution:** about **9°**. Render extras `front_sheet (0, 9)`, `side_sheet (90, 9)` and `rear_sheet (180, 9)`
  through `M.views(..., extra=...)` and compare §1.2's profiles on those. The kit's 4° renders will read flatter: the
  sand line and rocks about 0.03 h lower, far rocks less visible over the mound.

### 3.4 The sheet's three-quarter views

- The f34 crystal is relatively a little narrower than the front's (crystal W / crystal H 1.25 against 1.36). Its
  right cap reads 0.07 h higher than its left. Its camera is about 10–15° off axis at about 12° elevation, but the
  exact angle cannot be pinned down (the cues disagree).
- The r34 reads as the f34 mirrored (§3.1).
- **Resolution:** judge the f34 against the kit's front34 (−28, 12) and an extra `f34_near (−15, 12)`. Judge the
  r34 against the kit's rear34 (152, 12), an extra `r34_near (165, 12)`, and the sheet's r34 flipped horizontally.
  Use the shares and the arm spread, not the exact outline.

### 3.5 Front and rear widths differ

- The front is 215 px wide, the rear 192 px; the crystal is the same in both (176 / 172 px). The difference is the
  mound and the end rocks, drawn wider in the front.
- **Resolution:** W 10.2 (between 10.8 and 9.6). Expect our front W : H about 0.06 under the sheet's and the rear's
  about 0.06 over; tolerance ±0.08.

### 3.6 The Side Branch and the second socket

- The exploded and the Parts Breakdown show two parts and two sockets. In every assembled view there are exactly
  three limb ends (the main branch's), and the crystal leaves the sand as one trunk (the base gaps in the runs are
  rock T1 in front).
- **Resolution:**
  - The hero holds the Main Branch only, in socket 1.
  - Socket 2 stays empty as a small shallow pit back-left of the trunk. The r34 shows exactly such a dimple behind the
    trunk, and the other views hide it.
  - The Side Branch is built and exported as its own part.
- **Alternative:** omit socket 2 (5 of 6 hero views show none). The main session decides (§8).

### 3.7 Arm heights per view

- Cap tops in studs: front gives left 5.7–6.0 and right 6.4–6.6; rear gives left 6.3 and right 5.5–5.7; the side
  draws the far arm 1.5–2 studs lower than the near one.
- **Resolution:** right cap top 6.3, left 5.8 (§2.1). Acceptance per view ±0.06 h. Known misses: the rear's
  screen-left cap reads about 0.05 h high, and the side's far cap reads 0.68 on the sheet (expect about 0.72).
  Record them.

### 3.8 Back-rock heights

- The front draws the back rim rocks over the mound at 0.35–0.36; the rear draws them at 0.16–0.20 from their own
  side. At 9° elevation both fit tops of about 1.5–1.7.
- **Resolution:** the near view governs each rock's height; the far view is checked ±0.06.

### 3.9 "Rock Accent — Darker gray" swatch is lighter than "Base Rock"

- Measured: Base Rock `#746E6D` (9°, 0.06, 0.45); Rock Accent `#94837C` (17°, 0.16, 0.58). The label says
  "darker", the swatch is lighter and warmer.
- **Resolution:** follow the measured swatches and the renders. In the renders the rocks' decile 8 is `#91827B`–
  `#93817A`, the accent. The accent is the warm lighter patches on the rocks (§5), not a darker colour.

### 3.10 The crystal's root inside the socket looks translucent

- In the junction close-up the crystal below the rim is dull grey-teal (`#618A87`), as if seen through sand or
  glass.
- **Resolution:** no transparency (WorldModeling §5.2; Roblox exports opaque). Paint the in-pit faces with a dull
  `glass_root` key; the pit's own shadow does the rest (§5.5).

### 3.11 "Flat color" against the user's blended-colour rule

- The user's standing rule wins: graded regions (deep → body → light along each limb) plus calm Tint. The sheet's
  own renders show these gradients (§5.3), so this matches the sheet.

## 4. Construction plan (Stage 1)

1. **Parts first**, each with its own function and checked against its cell: `branch()` (Main Branch), `sprig()`
   (Side Branch), `mound()` (Sand Base, sockets carved), `stone(variant)` (A–D).
   - Render a parts shot (`extra`, about (−20, 15)) laid out as the Parts Breakdown: the branch over the mound, the
     sprig to the right, the four rocks in a row below.
2. **Hero:**
   1. `_paste` the mound; the branch with its root through socket 1's floor; 11 rim rocks; T1 and T2.
   2. One exact self-union, then `union_loose`, then `m004.floor_cut` at z 0.
   3. Then carve the three underside pockets.
3. **Placeholder keys** (stage 1): `m016_glass`, `m016_glass_root`, `m016_sand`, `m016_sand_pit`, `m016_rock`.
   Stage 4 adds the others (§5.4).
4. **Stage 1 acceptance** (render, compare every view, measure):
   1. **Profiles:** top, crystal-bottom and sand-top profiles within ±0.06 h of §1.2 on the 9° extras. Rock tops
      within ±0.05.
   2. **Shares** (C / S / R, same masks) within ±4 points per view: front 53 / 26 / 21, side 55 / 24 / 22, rear
      57 / 21 / 22, f34 extra 46 / 29 / 25, r34 extra 52 / 26 / 22, top 34 / 44 / 21 (±6).
   3. **Arms:** the right arm in front of the trunk in the front render, behind it in the rear. In the side render
      the near arm is a column in front of the trunk at screen left (if the probe confirms screen right = +Y). Cap
      tops at front (0.25, 0.78) / (0.85, 0.79), rear (0.15, 0.74) / (0.82, 0.76), side (0.255, 0.78) /
      (0.76, 0.68), ±0.06 f and ±0.06 h. The crystal spans per §1.2 ±0.05.
   4. **Limbs:** trunk 2.1–2.5 thick, arms 1.6–1.9 at the neck, caps 2.0–2.5. Every end is a flat octagonal cap with
      a fan centre and a bevel ring. 7–8 sides; no smooth tubes, no pointed tips.
   5. **Sockets** (BVH ray pairs, 6 stations round socket 1): gap 0.25–0.55 between the crystal and the pit wall at
      the rim; pit depth ≥ 0.6 below the rim; the walls visible in the front34 and junction extra. Socket 2 depth
      ≥ 0.4. No rock inside a pit.
   6. **Parts against their cells** (shape, proportions, facet count; the main branch's root taper; the sprig's Y).
   7. **Hero size** 10.2 × 8.4 × 8.0 (±0.5 / ±0.5 / ±0.3). Mound 8.4 × 7.3 × 2.1 (±0.4 / ±0.4 / ±0.2).

## 5. Colour plan (Stage 4)

### 5.1 Swatches (flat; medians of a 40 × 50 box inside each)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Crystal "Bright teal" | (835,130,875,180) | `#62EAEC` | 181°, 0.58, 0.93 |
| Sand Base "Warm beige" | (835,222,875,272) | `#DFBB96` | 30°, 0.33, 0.87 |
| Base Rock "Neutral gray-brown" | (835,313,875,363) | `#746E6D` | 9°, 0.06, 0.45 |
| Rock Accent "Darker gray" | (835,404,875,454) | `#94837C` | 17°, 0.16, 0.58 |

- The crystal swatch is the render's **lit tone** (deciles 9–10 `#41E6DE`–`#68F1EA`), not its body. The rendered
  crystal median is `#21C3B9`: darker, more saturated, 4–5° greener. Calibrate to the render, never to the swatch.
- The sand swatch matches the rendered body (`#DFB68E`).
- The Base Rock swatch is close to the rendered rock median (`#746A66`–`#7D6E69`); the Accent swatch is decile 8.

### 5.2 Rendered regions (`samp.py`; median, lit quartile, shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Crystal, f34 | V f34 | C | `#1FBEB5` | `#49E8E2` | `#0FA298` |
| Crystal, r34 | V r34 | C | `#1EBCB2` | `#4AEAE2` | `#10A196` |
| Crystal, front | V front | C | `#21C3B9` | `#4BE8E1` | `#0EA096` |
| Crystal, side | V side | C | `#22C8BE` | `#51EBE4` | `#11A398` |
| Crystal, rear | V rear | C | `#21C7BE` | `#4BE8E1` | `#0FA39A` |
| Crystal, top | V top | C | `#34DAD1` | `#5CF1EB` | `#12A398` |
| Crystal, exploded main | (196,802,478,1046) | C | `#1FBBB1` | `#48E7E0` | `#13A399` |
| Crystal, exploded side branch | (478,946,582,1055) | C | `#1EBBB3` | `#50EAE3` | `#12A298` |
| Crystal, parts main / side | (699,827,861,997) / (902,868,982,950) | C | `#1FBBB2` / `#1EB7AF` | `#49E4DD` / `#51EAE4` | `#14A49A` / `#13A198` |
| Crystal, section close-up | (700,1305,860,1515) | C | `#27CEC6` | `#58E8E5` | `#11A9A1` |
| Crystal in the pit (junction) | (60,1395,240,1495) | hue 160–190, v < 0.62 | `#618A87` | `#649896` | `#4B7171` |
| Sand, f34 / r34 | V | S | `#E1B790` / `#DAB28B` | `#EFCAA3` / `#EDC8A1` | `#BE9A79` / `#B79374` |
| Sand, front / side / rear | V | S | `#E3BA93` / `#DEB78F` / `#DCB38C` | `#EFCCA5` / `#F1CDA5` / `#EECBA5` | `#BA9777` / `#BD9878` / `#B89676` |
| Sand, exploded / parts | (195,1096,471,1232) / (694,1029,888,1120) | S | `#D8AF87` / `#DBB289` | `#EDCAA4` / `#EDC9A3` | `#B89272` / `#B69374` |
| Sand, junction close-up | (28,1305,372,1515) | S | `#DFB993` | `#EDCBA6` | `#D2A982` |
| Pit walls (junction) | (60,1395,240,1495) | hue 15–40, sat > 0.25, v < 0.70 | `#88674C` | `#967456` | `#69523D` |
| Pit floor (junction) | (130,1470,170,1485) | all | `#716357` | | `#655142` |
| Underside, flat and cavities | (382,1305,700,1515) | S | `#A98362` | `#B48E6D` | `#A27C5C` |
| Rocks, f34 / r34 | V | R | `#756D6A` / `#756967` | `#AA968C` / `#A39088` | `#5D5552` / `#5F5754` |
| Rocks, front / side / rear | V | R | `#746A66` / `#776A66` / `#7D6E69` | `#AA978E` / `#A7948A` / `#AA988E` | `#5C524E` / `#5E5450` / `#5D524E` |
| Rocks, exploded and parts (10 rocks) | §1.4 boxes | R | `#726862`–`#877A73` (per rock) | `#9E8B85`–`#B9A79F` | `#58514E`–`#696363` |
| Rocks, underside close-up | (382,1305,700,1515) | R | `#715F5B` | | `#544739` |

### 5.3 How the colour works

**Crystal.**
- **One hue family, 175–178°.** Dark tones are saturated teal (sat 0.88–0.92), light tones pale aqua (sat
  0.54–0.58). No blue (the swatch's 181° is the brightest tone), no green.
- Front-view deciles (dark → light):

  ```
  #0D978B #0FA39A #17ADA4 #1AB4AA #1FBEB4 #22C8BE #27D1C7 #30DBD1 #41E6DE #68F1EA
  ```

- **Lit, not luminous.** The darkest decile is 0.57 of the lightest's luminance; the sand's ratio is 0.66, the
  rocks' 0.42. The shade facets go genuinely dark teal: nothing reads self-lit. **No spill on the sand:** sand
  within 1–8 px of the crystal is `#DCB895`–`#E9C7A0` (hue 30–32°), the same family as the sand far away
  (`#E2B992`). Rock pixels next to the crystal are only edge mixes (`spill.py`).
- **Gradient along the limbs** (median per height band, front; the side and rear agree within 6 levels):

  | h band | 0.26–0.36 | 0.36–0.46 | 0.46–0.56 | 0.56–0.66 | 0.66–0.76 | 0.76–0.86 | 0.86–0.94 | 0.94–1.0 |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | Median | `#18ACA2` | `#1BB7AF` | `#1FBCB5` | `#20BEB3` | `#29D3CA` | `#22C7BB` | `#24D1C7` | `#5DEFE9` |
  | What | trunk base, sand line | fork, arm roots | fork | arms | arm ends and caps | upper trunk | upper trunk | trunk cap top |

  So it runs deep at the sand, mid through the body, and light towards every limb end. The cap tops are the
  palest (`#4DEBE6`–`#5DEFE9` in every orthographic view, including the rear). That is mostly sun on up-facing
  faces, but the caps are also a region of their own (the cut ends).
- **Facet steps** are lighting on jittered flat facets; neighbouring facets differ by one step. The deep-to-light
  span along a limb is paint.

**Sand.**
- Warm beige, hue 28–32°, sat 0.29–0.40.
- **Height gradient** (front; side, rear and f34 agree):

  | h band | 0.00–0.08 | 0.08–0.16 | 0.16–0.24 | 0.24–0.32 |
  | --- | --- | --- | --- | --- |
  | Median | `#D6AA82` | `#E1B78F` | `#E8C199` | `#ECC8A0` |

  The crown is paler and less saturated; the foot deeper. Part of it is sun on the flatter crown. Paint about half of
  it as a height field (never by facing).
- **Contact darkening:** sand within 1–2 px of a rock is `#BF9D81`–`#C09D80` (partly an edge mix); at 3–5 px it is
  `#D2A880` (f34) to `#DEB48B`. So there is a thin darker contact band, about 0.15–0.25 stud.
- **Pits:** walls `#88674C`, floor `#716357`: shaded deeper sand. Underside `#A98362`.

**Rocks.**
- Neutral grey-brown, hue 9–17°, sat 0.10–0.16. Medians `#746A66`–`#7D6E69`.
- Per-rock medians run from cool `#706A6B` (350°, 0.05; the shaded far-left rocks) to warm `#84726A`–`#877A73`
  (18–21°, 0.20). Part of that is light. The rest is the Base Rock / Rock Accent pair: some rocks and patches warmer
  and lighter.
- Front deciles:

  ```
  #4F4744 #5F5551 #665D5A #6D625E #706765 #7C6D68 #887770 #93817A #A59389 #B9A9A0
  ```

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered medians, not swatches. Kinds: `K.sample(..., "vivid")` for the crystal;
`M.sample(..., "brown")` for the sand (check n; the pale crown has sat ≈ 0.30, so fall back to `"all"` on the
calibration dome); `M.sample(..., "stone")` for the rocks.

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m016_glass` | `#20C0B7` (view medians `#1FBEB5`–`#22C8BE`) | limb bodies | rough 0.3, metal 0, spec 0.4 |
| `m016_glass_light` | `#2CD6CC` (arm-end band `#29D3CA`; rear `#32DDD3`) | the last ~1.5 studs of every limb and the caps' bevel rings | rough 0.3 |
| `m016_glass_glint` | `#5DEFE9` (cap-top band `#4DEBE6`–`#5DEFE9`; swatch `#62EAEC`) | the caps' top fan faces only (3 × 8 faces) | rough 0.25 |
| `m016_glass_deep` | `#18ACA2` (sand-line band `#15ABA3`–`#18B6A9`) | the trunk's last ~1.0 above the sand; the inner crotch faces | rough 0.3 |
| `m016_glass_root` | `#4E9A94`, then re-measure to `#618A87` ±12 in the junction extra | crystal faces below the socket rim (inside the pit) | rough 0.5 |
| `m016_sand` | `#DFB68E` (view medians `#DCB38C`–`#E3BA93`; swatch `#DFBB96`) | mound body | rough 0.95 |
| `m016_sand_light` | `#EAC49C` (crown bands `#E8C199`–`#ECC8A0`) | crown (height field) | rough 0.95 |
| `m016_sand_dark` | `#D0A57E` (foot band `#CBA17B`–`#D8AF85`; contact `#D2A880`) | foot band; 0.25 round each rock; the bottom face | rough 0.95 |
| `m016_sand_pit` | `#A07C5C`, then re-measure walls to `#88674C` ±12 and floor to `#716357` ±12 in the junction extra | pit walls and floors; the underside pockets | rough 0.95 |
| `m016_rock` | `#776C68` (view medians `#746A66`–`#7D6E69`; swatch `#746E6D`) | rock bodies | rough 0.9 |
| `m016_rock_accent` | `#8E7D76` (decile 8 `#93817A`; swatch `#94837C`) | broad warm patches; 3 rocks mostly accent | rough 0.9 |
| `m016_rock_dark` | `#5E5450` (shade quartiles `#5C524E`–`#5E5450`) | ground-contact row; faces within 0.3 of the sand line or a neighbour | rough 0.9 |

- **Calibration warnings:**
  - The crystal's light keys sit near the g/b clip (`#xxF1EA`). Lower the specular rather than raising brightness
    if the dome washes to white.
  - `glass_glint` goes on up-facing faces. Keep the cap-top faces few (24), so `K.check`'s facing correlation stays
    below 0.5. If it fails, drop `glass_glint` and let `glass_light` plus the sun make the cap tops pale.
  - Calibrate `glass_root` and `sand_pit` on the dome, then re-measure them in the hero junction extra, where the pit
    shades them.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Crystal**, per limb, with u = distance along the limb from its sand line or root (0) to its cap (1):
  - u < 0.12 (and the trunk below z 2.9) → `glass_deep`, blending to `glass` by u 0.25;
  - 0.25–0.65 → `glass`;
  - > 0.70, and every cap bevel face → `glass_light`;
  - cap fan faces → `glass_glint` (hard: a real cap edge);
  - inner crotch faces (within 0.4 of where two limbs meet, on the inside of the fork) → 50 % `glass_deep`;
  - faces below the socket rim → `glass_root` (hard at the rim line: the sand edge hides it);
  - plus broad noise ±0.08 on u, so the bands don't read as rings.
- **Sand:**
  - body `sand`;
  - height field: z > 1.5 → 50 % `sand_light`, > 1.8 → 75 %;
  - foot band z < 0.35 → 50 % `sand_dark`;
  - within 0.25 of a rock → 50 % `sand_dark` (a soft contact band);
  - broad noise (patches 2–3 studs) sand ↔ sand_light at level 0.3;
  - the pit rim chamfer → 50 % toward `sand_pit`; the walls and floor `sand_pit`.
- **Rocks:**
  - body `rock`;
  - noise patches `rock_accent` at level 0.3 (25–35 % of faces);
  - three rocks (R1, R6, R10) mostly accent (mix 0.6);
  - ground row (bottom 20 % of each rock) and faces within 0.3 of the sand → 50 % `rock_dark`;
  - the crown (top 30 %) no dark.
- **Hard edges only** where materials meet: crystal against sand, rock against sand. These are automatic, because
  they are separate keys on separate faces.

### 5.6 Texture (Tint) and finish

- **Tint:** per piece `tint_var` about 0.04, so neighbouring rocks differ.
  - `K.texture` sand: amp 0.05, scale 0.4, jitter ±0.015 (calm faceted mottling).
  - Rocks: amp 0.06, scale 0.45.
  - Crystal: amp 0.025 (the sheet's "flat color"; broad only).
  - Never confetti.
- **Finish:**

  | Material | Roughness | Specular | Metal | Notes |
  | --- | --- | --- | --- | --- |
  | Crystal keys | 0.25–0.3 (`glass_root` 0.5) | 0.4 | 0 | glossy facets; pale cap tops; no transparency, no emission |
  | Sand keys | 0.95 | normal | 0 | matte |
  | Rock keys | 0.9 | normal | 0 | matte |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- Crystal median within about 10 levels of `#21C3B9` per view.
- The band table in §5.3 within about 12 levels.
- Sand median within 10 levels of `#DFB68E`; its height bands in order (foot darker, crown paler).
- Rock median within 8 levels of `#776C68`.
- Pit walls and floor per §5.4.
- Shares per §4, step 4.2.

## 6. Depth: the sockets

### 6.1 Socket 1 (the junction)

- Cut a hexagonal pit into the mound (circumradius 1.65, depth 0.70, walls tapering in 5°; rim lip +0.08 with a
  0.2 chamfer) **before** the hero union.
- The Main Branch's lower trunk passes down through the pit's floor and on to its buried root tip (z 0.45). The
  union merges crystal and sand only below the pit floor.
- **The gap is real:** 0.28–0.5 at the rim, widening to 0.45–0.7 at the floor as the trunk tapers. It shows as dark
  walls (`sand_pit`) and a dull crystal root (`glass_root`), as on the close-up.
- **Check** (BVH ray pairs, 6 stations round the trunk at the rim height and 0.5 below): the gap is 0.25–0.55 at the
  rim; the depth from rim to floor is ≥ 0.6; no wall touches the crystal above the floor.
- From the front34 extra and the junction extra (hero, about (−20, 35)), at least two walls must be visible.
- In the orthographic fronts, rock T1 hides most of it, as on the sheet.
- **Keep the pit faces in stage 2.** They are colour and shape geometry: don't dissolve the rim chamfer or the walls.

### 6.2 Socket 2 and the underside pockets

- Socket 2: circumradius 0.75, depth 0.45, a flat floor, the same rim treatment.
- Underside pockets: blind, closed hex recesses (circumradius 0.7, depth 0.45) in the flat bottom. Carve them after
  the floor cut, so the cut doesn't remove them. At least 0.3 stays from the root tip and from socket 2.
- They are visible only in the kit's underside view (20, −45), which matches the "Base Underside" close-up.

## 7. Lighting and VFX plan (Stages 5 and 6)

**What the sheet shows:**
- The crystal is lit, not luminous: the shade facets go dark teal (§5.3, ratio 0.57).
- No teal spill on the sand or the rocks (§5.3).
- No glow panel, halo, sparkle, lightning, dust or particles anywhere on the sheet. Only the normal specular
  highlights on the facets and pale cap tops (p95 `#61F2EC`–`#71F1ED`).
- WorldModeling §12.5: Stormglass is "not electrical particle strands". §5.2: crystals must read without emission or
  bloom. §1.2: no "ordinary asset recolored neon with a glow halo".

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces.** `export_kit_roblox.py` makes every face with emission ≥ `GLOW_EMISSION` (1.0) a Neon part,
  one flat unlit colour per key. On these limbs that would erase the deep → body → light gradient and the facet steps
  the sheet shows. Emission between 0 and 1 does nothing in Roblox except drop the Tint.
- **No PointLight.** The sheet shows no spill; unlike M011's cave, nothing here is enclosed or dark.
- **Optional** (decision §8): a faint `crystal_glow` light for night readability at about (+1.0, −2.6, 4.0), in the
  open in front of the fork, ≥ 0.8 from every surface. Colour `#4FE3DA`, brightness 0.4, range 6, shadows true, no
  flicker. Default: off, as M013's no-glow sheet.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`,
  `vapour`, `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `dust`. (M014's decision adds
  `crystal_halo`; it is not in the file yet.) Nothing on this sheet needs a storm, lightning or spark kind.
  **No new kind is proposed.**
- **Recommended:** 3 × `ore_glint` (decision §8), one per cap, for the resource-node sparkle every crystal node so
  far carries (M011, M012, M014). They also mark the sheet's brightest facets (the cap tops and bevels).
  - Overrides: colour `["#E8FFFC", "#62EAEC"]`, size [0, 0.45, 0], rate 0.3 (trunk 0.4), shape [1.6, 0.6, 1.6]
    (Roblox XYZ, flat over the cap).
  - Positions (build frame, on the cap top faces): trunk (+0.2, −0.5, 7.95); right (+3.5, −1.85, 6.15); left
    (−3.1, +2.0, 5.7). Snap them to the built caps' fan centres.
  - All sockets go on the hero only (the parts carry none), as in m011–m015. Render with `vfx=True`. The export
    STATS line must report 3 sockets and 0 glow pieces.
- **Not added:** halo, light, dust (the old R04 Stormglass had dust and a cyan `heat_glow`; this sheet shows neither),
  smoke, embers, lightning strands.
- **Harvest sockets:** none, as m009 and m011–m015 decided.

## 8. Naming and decisions for the main session

The R04 kit sheet owns the old Stormglass set (`scripts/kit/R04/stormglass.py`, `R04_stats.json`,
`kit/wip/R04_stormglass_stats.json`, `art/roblox/kit/R04/manifest.json`): `Stormglass`, `StormglassMainBranch`,
`StormglassSideBranch`, `StormglassSandBase`, `StormglassBranchStub`, `StormglassDepleted`, `StormglassFragment`,
`StormglassFragmentB`, and the keys `r04_stormglass`, `r04_sand`, `r04_storm_rock`. `M.mk` would silently rename a
clash to `<name>M016`, so avoid them all.

**Proposed names** (a `git grep -w` of the whole repo found none of them; `m016_` is unused too):

| Object | Part | Why |
| --- | --- | --- |
| `StormglassNode` | hero | R04 owns `Stormglass`; matches M014's `StarstoneNode` |
| `StormglassBranch` | Crystal Assembly (Main Branch) | R04 owns `StormglassMainBranch` (and `StormglassBranchStub`, a different word) |
| `StormglassSprig` | Crystal Branch (Side Branch) | R04 owns `StormglassSideBranch` |
| `StormglassMound` | Sand Base (with sockets) | R04 owns `StormglassSandBase` |
| `StormglassStone` | Base Rock (Reusable) | variants B–D build-only `_m016_stone_b/c/d` |

- Palette keys `m016_*` (§5.4). Collection `Kit/M016 Stormglass`.

**Decisions needed:**
1. **Arm layout** (§3.1): right arm front-right, left arm back-left (recommended), or the mirror.
2. **Socket 2** (§3.6): an empty shallow pit back-left of the trunk (recommended; the exploded, the parts and the r34
   show it), or omitted.
3. **Side Branch** (§3.6): built and exported as `StormglassSprig`, not placed in the hero (recommended).
4. **Underside pockets** (§6.2): model the three blind pockets (recommended; the sheet shows them; about 50 tris).
5. **Exports:** hero plus `StormglassBranch`, `StormglassSprig`, `StormglassMound`, `StormglassStone` (5 objects,
   recommended), or also the three rock variants.
6. **Stage 5/6:** no Neon and no light (recommended); 3 `ore_glint` on the caps (recommended) or none, since the
   sheet shows no sparkle; the optional faint `crystal_glow` (§7.1).
7. **Names** as proposed.

## 9. Pitfalls to avoid

1. **A crystal cluster or shards.** This is a tube tree: three thick 7–8-sided limbs with flat octagonal caps (fan
   centre, bevel ring), joined in a wide fork. No pointed tips, no hexagonal prisms with pyramid tips, no needles.
2. **Smooth or clean tubes.** Facets come from turned and scaled rings (±8 % radius, ±10° twist, rings every
   0.8–1.0). No subdivision, no smooth shading, no perfectly regular prisms.
3. **Thin arms or a thin trunk.** Trunk 2.1–2.5, arms 1.6–1.9, caps 2.0–2.5. The arms leave the trunk low (undersides
   at z ≈ 2.8–3.4), so the fork is wide and chunky.
4. **The arms in the XZ plane.** They lie on a line about 30° off X: the right arm comes forward, the left goes back
   (§3.1). Flat arms fail the side view (no near column, no far arm).
5. **The Side Branch in the hero.** Every assembled view shows three limb ends.
6. **A painted socket.** The junction is a real pit with a 0.25–0.55 gap and ≥ 0.6 depth; the crystal's root
   continues down inside it (§6). No flush union at the sand line, no dark ring painted on the sand.
7. **Crystal too pale or too blue.** The swatch `#62EAEC` is the lit tone; the body renders `#21C3B9` (176°, 0.83).
   Hue 175–178° only.
8. **Neon or a glow.** The sheet shows none (§7). Emission between 0 and 1 is useless in Roblox.
9. **Colour by facing.** The sand's pale crown and the pale cap tops are partly sun. Paint height, limb position,
   cap region and contact fields only. Check `K.check`'s facing correlation (< 0.5).
10. **Rocks too pink or too grey.** Medians `#746A66`–`#7D6E69`, hue 9–17°, sat 0.10–0.16. "Rock Accent" is the
    lighter, warmer one despite its label (§3.9).
11. **A smooth hemisphere mound.** It is a low lumpy faceted dome (H : W 0.25) with a flatter top and a short skirt,
    7–9 lobes.
12. **Floating or buried rocks.** Rim rocks sink 0.2–0.4 into the skirt and sit on the ground. T1 and T2 sit on the
    upper slope and stay clear of the pits.
13. **Side-view handedness.** By `frame_box` (`direction = (sin az · cos el, −cos az · cos el, sin el)`,
    `to_track_quat("-Z", "Y")`), the az 90 camera at +X has screen right = **+Y (back)**. M013–M015's specs say
    "screen right is the front". Before trusting either, put a small probe cube at (0, −5, 1) and render `side`: if
    it lands at screen left, this spec's side mapping holds. Otherwise mirror the side-view Y values in §1.3 (the
    3D layout in §2 stays, because the near-arm occlusion fixes it either way).
14. **Comparing the wrong views.** Use the 9° extras for the orthographic profiles, `f34_near` and `r34_near` plus
    the kit's 3/4 views for the three-quarters (the r34 also flipped), and `top_tilt` plus the kit's top for the top.
15. **Exact booleans.** Overlap everything: arms 0.4 into the trunk, rocks 0.2–0.4 into the mound, the root at least
    1.0 below the pit floor. No coplanar contact. Remove boolean slivers with m011's `_tidy` / `_desliver`, but lock
    the pit rows and the ground plane.
16. **Slivers at the fork.** The ring stations of the arms and the trunk meet in the union. Keep triangles above 5°
    (M012's lesson) and rings at least 0.5 apart near the fork.
17. **Naming clashes** with R04 (§8). Only one agent drives Blender at a time. No commits, pushes or exports in stage
    agents.

## Decisions (main session, 2026-10-28)

All recommendations are accepted:
1. The right arm points front-right and the left arm back-left.
2. Socket 2 stays as an empty shallow pit back-left of the trunk.
3. The Side Branch (`StormglassSprig`) is built and exported but not placed in the hero.
4. The three underside pockets are modelled.
5. Export the hero plus 4 parts.
6. No Neon and no light; three low-rate `ore_glint` sockets on the caps.
7. Names as proposed (`StormglassNode`, `StormglassBranch`, `StormglassSprig`, `StormglassMound`, `StormglassStone`).

Side-view direction (pitfall 13): confirmed from `frame_box`'s maths. The side camera at +X has screen right = +Y, the back. The 013–015 specs carry a correction note.
