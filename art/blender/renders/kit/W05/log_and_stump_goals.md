# W05 row 4 - Log and Stump: verification goals

Reference: `art/reference/kit/rows/W05_row4.png` (full sheet `W05_broadleaf_roots_deadwood.png`).
Render checked: `art/blender/renders/kit/W05/log_and_stump_compare.png` (+ `_cells/`).

REVISION 5 (this run): the independent verifier failed revision 4 (resemblance 6/10). The two
must goals it found unmet were a thin heartwood rim and pale-yellow shard moss. They are added
below as VR1 and VR2. Its should goals are VR3-VR5, and its should fixes (rounder staves, thicker
branch, rock clear of the open end, front view into the bore) are VR6-VR8. Status is from build 6
of this run (the last). Every goal was judged by eye against the reference cell directly above it,
using 2x crops of the reference hero cell and my hero cell. The numbers support the judgements;
they do not prove them.

## VERIFIER GOALS (revision 6: colour rework)

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| VC1 | must | ONE palette key per material, no light/dark/tip shade keys, no colour chosen by height/facing/tier; Tint random only (+/-6%) | MET | PALETTE holds only the 7 sheet keys (+kit_rock); paint() ignores direction; runner reports no shade_pairs and 0 problems |
| VC2 | must | Moss reads lime-green and secondary to bark, not a yellow blanket over the whole top and front | MET | Build 9: blankets narrowed to 58-128 deg, drips cut to 2 short ones; compare row shows brown staves dominant with lime/green clumps on top, like the reference |
| VC3 | must | Grey rocks clearly visible in front of the log (two big ones mid-front) and left of the open end | MET | Rocks enlarged ~15%; hero cell shows 4 grey rocks along the front base and one left of the bore, not hidden by grass |
| VC4 | must | Ground moss patches small (only a little lime under the front), no large yellow pads | MET | Patches shrunk; hero and variants show only thin lime strips at the foot |
| VC5 | must | LowStump ~4 high x ~4.6 dia, pale ring top, flared roots, green leafy moss at the foot (w05_leaf), 2 big rocks | MET | Stump cell: squat ridged stump 4.0 tall, 5 concentric rings on top, 5 roots, green leaf mounds front, rocks left and right |

## VERIFIER GOALS (revision 5)

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| VR1 | must | Hero: pale heartwood plank ends form a thick scalloped rim round the bore, ~1.1-1.2 studs thick, bore ~60% of the diameter, no rock covering it | MET | The 2x hero crop shows a broad pale ring of 11 bevelled, staggered plank ends (scalloped outline) round a near-black bore. The rim is as wide as the reference's relative to the end. Geometry: bore 0.6 R, end faces from 0.6 R to 0.88 R plus a 0.45-stud bevel, 0.4-1.05 studs of stagger. The left rock now sits clear, left of the end |
| VR2 | must | Hero: lime moss blankets drape over the top and drip down the front as lumpy leafy mounds, green-lime (not pale yellow), running along the top | MET | The hero and front cells show rounded moss cushions and leafy sprig clumps covering the top from the open end to the +X end (a gap only at the branch). A curtain of leafy clumps hangs down the front beside the open end, with two smaller drips. Sampled hero moss median #BEDB3B (hue 71), close to the reference's #B9D11F (hue 68); the previous build was #E0E239 (hue 61). The shard hulls are now three-ring domes |
| VR3 | should | +X end snapped into staggered splinters, visible in the hero view | MET | Hero cell: jagged splinters stand up off the top right end of the log, past the branch; the stave ends are staggered by up to 1 stud |
| VR4 | should | Front and side cells match the reference framing: bore at left, log broadside, branch leaning right | UNMET (front) | Side cell (SIDE_AZIMUTH -10): broadside log, open pale-rimmed bore at the left, Y branch leaning right, like the reference's third cell. Front cell: broadside, branch right of centre, but the bore shows only as a narrow dark slot in the pale rim. The runner's front camera is fixed at 0 deg, and the 20 deg yaw (up from 12) is as far as I can turn the log without breaking the spec's footprint |
| VR5 | should | Colour balance: bark dominant, lime/leaf-green moss second, grey accents, pale only on cuts, black only in the bore | MET | Compare row: warm brown staves dominate. Lime-green moss and leaf clumps are second, grey rocks are accents, pale only on the rim, splinters and cuts, black only in the bores and the shell window. The moss reads greener and less dominant than in revision 4 |
| VR6 | should | Log reads as a round trunk of staves (rounder profile, deeper V grooves), not a stack of boards | MET | Deeper grooves (kg 0.80) and a higher crown (1.045). The hero, front and side cells show a round barrel with 4-5 broad staves across the front, each cut by a dark V groove. It still reads as planked, like the reference |
| VR7 | should | Branch thick with a clear Y fork | MET | Limb radius 1.25 (2.5 thick at the base), prongs 1.1-1.25 thick. Hero/front cells: a heavy limb rises off the back top and splits into an upright prong and a right-leaning one |
| VR8 | should | Hero end turned so the bore reads as a deep oval tunnel in the iso view | MET | HERO_AZIMUTH -17 with yaw 20: the hero cell shows a dark oval bore inside the pale rim, dark all the way in (plug 10.6 studs deep). The oval is a little narrower than the reference's |

## ASSEMBLED / HERO (FallenHollowLog, iso cell)

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| H1 | must | Log body ~13-13.5 long x ~5.5 dia (2.4:1), ~9 tall incl. branch, ~15-17 wide with dressing, lying along X with the open -X end turned to camera-left/front | MET | Log 13.2 x 5.5; KITSTAT 16.6 W x 10.2 D x 9.0 H. The hero cell reads as a long chunky barrel receding to the right with the open end at front-left, like the reference |
| H1b | should | Footprint depth 8-10 | UNMET | Depth 10.5 (bigger rocks): the yaw went from 12 to 20 to show the bore to the fixed front camera (verifier fix). The dressing was pulled in, which costs ~0.2 |
| H2 | must | Open -X end reads as a deep near-black tunnel (w05_hollow bore, ~60% of the end diameter), dark for >= 2 studs inside | MET | See VR1/VR8 |
| H3 | must | Pale rim: 11 w05_heartwood plank ends round the bore, staggered by stave | MET | See VR1 |
| H4 | must | Branch stub: thick limb from the back top at ~55-60% of the length, leaning to +X, top ~3-3.5 above the log, visible Y fork | MET | See VR7; top of the branch at 9.0, ~3.5 above the log top |
| H5 | must | Moss: lumpy mounds over the top along the log, a broad drape down the front beside the open end, smaller drips/patch near +X | MET | See VR2 |
| H6 | must | Bark: ~11 long broad staves with V grooves (4-5 visible on the front face) | MET | See VR6 |
| H7 | should | +X end broken: stave ends staggered with pale splinters | MET | See VR3 |
| H8 | must | Grey kit_rock rocks: one left of the open end, two big ones (~2.3-2.6) in front of the log middle, one or two small ones; chunky faceted | MET | Hero cell: one rock left of the end (clear of the rim), two big rocks and two smaller ones along the front base |
| H9 | must | 5+ spiky w05_grass tufts round the base, the biggest ~3 tall in front of the log middle; a w05_moss ground patch under the front dressing | MET | 6 spiky tufts (the tallest between the front rocks) and lime ground patches under the front and at the left of the end |
| H10 | should | Planks read as separate boards through a small random per-stave Tint (not by direction) | MET | Staves differ slightly in tone at random; the runner reports no baked shading |
| H11 | should | Leafy fern sprigs on the moss at the left end and right end of the log top | MET | Hero cell: leafy sprigs over the open end's top and at the right end, as in the reference |

## FRONT VIEW

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| F1 | must | Log fills the cell width; open end at the left showing its pale rim and dark bore; Y-forked branch right of centre; rocks + grass along the base | MET | Front cell: the log spans the cell, with the pale plank rim and a dark bore slot at the left and the Y branch right of centre. Rocks and tufts run along the base. The bore is narrower than the reference's (see VR4) |

## SIDE VIEW

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| S1 | should | Side cell shows the log broadside with the open planked end at the left, branch leaning right, rocks/grass at the foot | MET | SIDE_AZIMUTH -10: matches the reference's third cell |

## TOP VIEW

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| T1 | must | Top view: long log with moss along its top, rocks and green tufts poking out along the sides | MET | Top cell: long diagonal log covered along most of its top by lime-green moss and leaf clumps, with rocks and tufts along the front side. The runner's top camera fixes the orientation (the reference's log is vertical) |

## PARTS

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| P1 | must | LogBranchStub: tapering limb with a clear Y fork (two prongs, splintered tips) and a pale heartwood cut base with bark ring lines | MET | Parts cell: limb with an upright prong and a side prong; slanted pale cut base with bark rings |
| P2 | must | LogMossFoliage: 2-3 leafy spiky clumps (w05_moss) plus a small w05_grass fern sprig; no bark | MET | Two spiky lime clumps and a small green sprig |
| P3 | must | LogShell: bare hollow stave tube ~12 x ~5 dia, open dark -X end with a thick pale plank rim, grooves, no moss | MET | 12.3 x 5.2 planked tube; dark bore in a broad pale bevelled rim at -X |
| P3b | should | Both shell ends visibly open in the parts cell | MET | Broken-away staves at the +X end show a dark window next to the cap |
| P4 | must | LogCutEndCap: thick disc ~4.5 dia x ~1.6 on its edge, heartwood face with >= 3 bark ring lines and a bark rim | MET | 4.7 x 1.6 x 4.7 disc: pale face, 4 concentric bark rings, bark rim |

## VARIATIONS

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| V1 | must | HollowLog: ~10 long x ~4.8 dia, open dark end with a pale rim at front-left, thick forked stub, leafy moss with drips, rocks + grass | MET | Variant cell: big dark bore in a pale scalloped rim, forked stub, lime-green moss and leaf clumps on top with drips, rocks and tufts |
| V2 | must | BrokenLog: open dark end, +X end snapped into tall jagged shards, a split along the top, a short stub, a little moss, rocks | MET | Pale-rimmed open end, tall shards at the snapped end, a split on top, a stub, a moss patch at the left, rocks and grass |
| V3 | must | LowStump: squat (~4.6 dia x 4), flat heartwood top with >= 3 bark ring lines | MET | 4.6 dia x 4.0 stump, pale top with 5 ring lines |
| V4 | must | LowStump: ridged bark with 10-12 grooves, flared roots, moss at the foot, 2 big rocks plus grass | MET | 12 ridged staves, 5 roots, lime moss mounds at the front, 2 big rocks and tufts |

## PALETTE / TECHNICAL

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| X1 | must | ONE key per material, the sheet's verbatim: bark w05_bark #A5653A, cut wood w05_heartwood #F0B26E, bore w05_hollow #1C130F, moss w05_moss #C6CB1F, leafy sprigs w05_leaf #9CBB1C, grass w05_grass #86AC22, rocks kit_rock | MET | PALETTE is copied verbatim. The .blend dump shows only these 7 materials. w05_leaf is the sheet's key for the "small leafy sprigs on deadwood" |
| X2 | must | Runner: 0 problems; hero <= 3000, parts <= 1500, variants <= 3000; origin bottom centre; nothing below z=0 | MET | "0 problems". Hero 2812, variants 2128/1339/1732, parts 160/582/908/474. min z = 0.0 on all 8 |
| X3 | should | Big readable facets, no noisy tiny faces | MET | Moss cushions are now 3-ring domes with broad facets; the leaf points are the smallest pieces |
| X4 | must | Tint only small random variation; every moss, leaf, grass and fern face kit_nocollide = 1, everything else 0 | MET | .blend dump: w05_moss, w05_leaf and w05_grass faces are 1 on all assets (hero 420/843/240); bark, heartwood, hollow and rock faces are 0 |
| X5 | must | Colour balance (see VR5) | MET | See VR5 |
| X6 | must | No VFX sockets (the reference shows none) | MET | No vfx.add calls |

## Iteration log

- Revisions 1-4 (earlier runs): palette rework, staves, rim, stump, yaw 12, moss dressing. The verifier failed revision 4 on the thin rim and the pale shard moss.
- Build 1 (this run): `chamfer0` added to log_tube, giving the open end a pale bevel on each staggered plank end; bore 0.6; rings cut from 10 to 6, which bought deeper grooves (kg 0.8). The moss mounds became rounded 3-ring domes, and leafy w05_leaf sprig clumps now alternate with them. Branch thicker; +X splinters added; left rock moved clear. Result: a thick pale rim and greener moss, but the hero view was too end-on.
- Build 2: yaw 20, azimuth -18, two leafy clumps per moss cushion. The front cell got a sliver of bore. The hero was still a bit end-on and the moss median was still yellow (#D4D632).
- Build 3: 11 lumps on the main blanket, a longer front drip, azimuth -10. The moss median became #BEDB3B (hue 71, matching the reference). The bore became too oblique.
- Build 4: azimuth -17. The bore oval and the broadside log are both visible, close to the reference framing.
- Builds 5-6: docstring update; end tufts pulled in. The size stayed 16.6 x 10.2 x 9.0 (the log, the yaw and the ground patch set it).
- Open: the front cell's bore is only a slot, because the front camera is fixed and the spec caps the yaw. A sheet-level greener w05_moss would let the blanket base match too (shared_lib_requests).
- Revision 6 build 7: rebuilt as-is; 0 problems, no shade pairs (single key per material already). Compare: moss too yellow/dominant, rocks hidden, stump short.
- Build 8: moss blankets narrowed, drips reduced, ground patches shrunk, rocks enlarged and moved forward, stump moss -> w05_leaf, stump h 4.6. Moss now secondary, rocks read; stump too columnar.
- Build 9: stump h 4.0, R 2.3: squat with flared roots, matching the reference. All musts MET.
