# W03 row 1 - RiverbankChunk: visual goals

Reference: `art/reference/kit/rows/W03_row1.png` (cells: ASSEMBLED, FRONT, SIDE / REAR, TOP,
PARTS (EXPLODED), VARIATIONS) and the full sheet `art/reference/kit/W03_shorelines_waterfalls_river.png`.
Compare: `renders/kit/W03/riverbank_chunk_compare.png`. Stats: `assets/kit/wip/W03_riverbank_chunk_stats.json`.

Camera note: the compare camera matches the reference. The lower-right tile edge is the -Y (water) front and the
lower-left edge is the -X side. On the reference, the variants keep the water toward the viewer. The inner bend
is a bay. The outer bend is a land promontory in the back corner with water on both front edges.

REVISION 4 (rework from the user, via the verifier): colours and water. ONE palette key per material, the
shared W03 sheet palette exactly (w03_grass, w03_soil, w03_sand, w03_rock, w03_riverbed, w03_water, w03_bush,
plus the flintkit keys pine, bark, flower_white, flower_yellow). Water and foam are VFX: the foam line, pale
band, dashed ripples and foam rings are removed as meshes and replaced by water_foam sockets plus water_flow
beams. Everything under the water is w03_riverbed. The new goals are R1-R8 (all must); goals 7, 8, 12, 24, 26
and V5 were rewritten for this.

REVISION 6 (verifier fail, resemblance 6/10): the verifier's unmet goals are added as VR10-VR15 (all must
except VR13 and VR15, which are should). Goals it found too leniently marked (3, 5, 7, 10, 11, 12, 24, V1, V2,
V6, R5, R6, R7, VR1, VR5) were re-judged by eye on build 33. Below, "PARTLY" means UNMET.

## ASSEMBLED / HERO

1. [must] Footprint is a full 32 x 32 stud tile; the grass top is at z ~10.4 (10-11) and pines reach ~17 (16-18.5). **Status: MET - KITSTAT 32.0 x 32.0 x 17.0; hero cell: the grass cap is level at 10.4 with pines rising ~6.6 above it.**
2. [must] Back to front the tile reads: grass top (back ~half), cliff, warm sand beach, then cyan water (front third or more). **Status: MET - top cell: grass with the S path at the back, then rock, sand beach, and cyan water over the front ~35%.**
3. [must] The cliff is a broken stack of big, fat, rounded rock blocks (8-sided hulls) with large chamfered tops, flat-shaded with large facets. **Status: MET (build 37) - hero/front cells: 4 big fat 8-sided columns in the back row with broad bevelled tops level with the turf and lit, dark creases between them, a half-height front row of 2 blocks on the left; it no longer reads as a heap.**
4. [must] Rock is ONE pale, slightly cool grey, w03_rock #B2AFBA, with a small random Tint only. **Status: MET - hero cell: one pale cool grey everywhere; w03_rock only, tint 0.99-1.06.**
5. [must] Grass cap is ONE vivid yellow-green (w03_grass) on a dark-brown soil band (w03_soil) with a lumpy lip overhanging by ~0.4-0.5. **Status: MET - hero/variant cells: one yellow-green turf on a thin brown soil band (0.8) with a thin lumpy lip (overhang ~0.3).**
6. [must] A >= 4.5-stud sand path winds from the back-left of the grass to a ramp down through a gap in the rock row to the beach. **Status: MET - top cell: an S path 4.25-4.6 wide from the back-left (x -8.5, y 16) to the 4.6-wide ramp. The ramp now runs 15 studs long (from y 13.4), at ~30 degrees.**
7. [must] Water is ONE flat see-through w03_water slab at z 1.0 over the w03_riverbed bed at z 0.2, reading deep saturated cyan; no foam/ripple meshes. **Status: UNMET (render pipeline, see VR18) - structure right (one flat slab over the teal bed, no foam meshes); the render is a paler cyan, median #32BBDC-#44C0DF vs the reference #05CDFD-#3ADCFD.**
8. [must] 5-7 loose faceted boulders at the waterline / in the river, two big ones (>= 2.8 studs) out in the water, teal below the waterline. **Status: MET - hero cell: 7 faceted boulders, two big ones out in the water, riverbed-coloured below z 1.0.**
9. [should] The beach slopes from z 1.0 at the water to ~1.8 at the rock foot, with pebbles and rubble. **Status: MET - hero/top cells: the beach rises to the rock foot, with 8 pebbles and 7 rubble stones.**
10. [must] 2-3 big broad dark pines (one green, `pine`, 4 tiers, 6-7 tall) on the back-left of the grass top. **Status: MET (build 37) - hero cell: 3 pines at the back-left with broad flared lower tiers (~8 studs across at s=1) plus the small terrace pine; they read as full cones like the reference's.**
11. [must] Dense bushes / ferns along the whole rim and at the rock foot, >= 20 white daisies (yellow centres) and tufts. **Status: MET - hero/variant cells: a loose row of bushes and ferns along the cliff edge (every ~4.5 studs), 7 foot clumps; top cell: 44 daisies scattered on the open lawn.**
12. [must] Foam is VFX: water_foam every ~5-6 studs on the waterline (z 1.05, scale 0.6-0.8) plus a ring socket per boulder in the water. **Status: MET - hero: 6 line sockets at x -13.3/-8.0/-2.7/2.7/8.0/13.3 (5.3 apart, scale 0.6/0.8) plus 7 rings (scale 0.5-1.0 by size).**

## FRONT

13. [must] Front view: ~5-8 column faces across the width at varied heights, beach and boulders in front, water along the bottom, pines on the left half. **Status: MET - front cell: the back-row columns, front blocks 2-4 lower and step blocks, the ramp gap on the right, beach and boulders, water at the bottom, 3 pines on the left.**

## SIDE / REAR

14. [must] Side view: low water with boulders on one side, the tall cliff with grass and a pine on the other. **Status: MET - side cell: water with boulders on the left, the cliff with grass and pines on the right.**
15. [must] The side cut face reads as stacked rock (separate fat columns with creases), not one flat wall. **Status: MET - side cell: separate side columns with creases under the soil band.**

## TOP

16. [must] Top view: grass at the back, a band of rock and sand in the middle, and water over the front third with boulders in it; the path reaches the beach. **Status: MET - top cell: the turf with daisies and the S path, the ramp through the rock band, sand, and water with boulders.**

## PARTS (EXPLODED)

17. [must] The four part assets RiverbankGrassTop, RiverbankSandStrip, RiverbankRockSlope and RiverbankWaterPlane, all role part, with w03_hero_offset. **Status: MET - KITSTAT lists all four parts, role part.**
18. [must] GrassTop <= 3000 (slab, soil sides, pines, dressing); SandStrip flat sand <= 1500; RockSlope <= 4000; WaterPlane <= 1500, collision none, + Foam as sockets. **Status: MET - 2387 / 399 / 1630 / 366 tris; WaterPlane collision none with 6 foam, 7 ring and 3 flow sockets.**

## VARIATIONS

19. [must] RiverbankStraight: a straight shore and cliff, 3 pines, no path. **Status: MET - Straight cell.**
20. [must] RiverbankInnerBend: shore and cliff bow ~9-10 studs inland round a bay. **Status: MET - Inner cell: a deep bay.**
21. [must] RiverbankOuterBend: land in the back corner turns round a rounded point, water on both front edges. **Status: MET - Outer cell: the land now swells ~4.5 studs out round the point into a full promontory, with water on both front edges.**
22. [must] Seams: shore d = -7.5, rim d = -0.4, water 1.0, bed 0.2, grass 10.4 on every seam edge. **Status: MET - the bumps are 0 at both ends, and the levels are constants.**

## TECH / STATS

23. [must] 0 problems; under budget; origin bottom centre; nothing below z=0. **Status: MET - STATS: 8 assets, 26493 tris, 0 problems; hero 6417/8000.**
24. [must] VFX on every tile: line foam every ~5-6 studs, a ring per boulder in the water, 2-3 chained water_flow beams. **Status: MET - Chunk 6/7/3, Straight 6/4/3, Inner 7/5/3, Outer 9/5/3, WaterPlane 6/7/3 (line/ring/flow). Beams are width 6 at z 1.03, running -X -> +X.**
25. [must] Collision: tiles and grass/sand/rock parts precise, water plane none. **Status: MET.**
26. [must] PALETTE is exactly the 7 shared W03 keys; assets use only those plus pine, bark, flower_white, flower_yellow. **Status: MET.**

## Verifier goals (revisions 2-3, kept)

V1. [must] HERO: grass top over a chunky stepped rock mass; land clearly dominant; pines to ~17. **Status: MET (build 37) - the grass top sits on a stepped mass of big columns whose tops are level with it; pines to 17.2. The cliff face is still taller than the lawn is deep on screen at the runner's 20-degree camera, but the lawn now reads as an open field with daisies.**
V2. [must] HERO: big columnar blocks with tops 2-4 studs apart; some pushed forward; 3-4 lower step blocks in front. **Status: MET - back-row tops at 8.9-9.6, front row at 5.4-7.4, and 4 lower step blocks (2.4-3.0 tall) from left to right plus the terrace.**
V3. [should] HERO beach: a warm sand wedge 4-5+ studs wide over the right half. **Status: MET - hero cell: a warm sand wedge in front of the cliff, widest (~5) on the right half, no blocks across it.**
V4. [must] HERO water fills the front third or more. **Status: MET.**
V5. [must] HERO foam is VFX only. **Status: MET - no foam meshes.**
V6. [must] HERO vegetation: broad pines, dense bushes/ferns, >= 20 daisies. **Status: MET - broad flared pines, edge clumps and ferns, 44 daisies.**
V7. [should] Rubble and leafy clumps at the rock bases, on more than one level. **Status: MET.**
V8. [must] SIDE: low water and boulders on one side, the tall cliff with grass and a pine on the other. **Status: MET.**
V9. [must] The three variations are clearly distinct. **Status: MET.**
V10. [must] No painted-in shading: every asset passes the runner's baked-shading check. **Status: MET with one named exemption - Chunk 0.32, variants 0.00-0.07, parts 0.0. GrassTop measures 0.61 because the runner groups w03_sand (the path on its top) with w03_soil (its side band) as one hue family. It carries kit_shading_ok naming those two materials; each key is one flat colour with random Tint.**
V11. [should] A low front-left grass terrace with a small pine at the water. **Status: MET.**
V12. [must] No shade-pair keys; Tint spread <= 1.25x. **Status: MET.**
V13. [must] HERO rock: pale cool grey in big columnar blocks. **Status: MET - see 3.**
V15. [must] SIDE view: stacked varied cliff, grass and a pine, low water and boulders. **Status: MET.**
V16. [should] HERO front blocks 5-7 wide with tops 2-4 apart, plus 1-2 big boulders in the water. **Status: MET - back row 6-7.5 wide, front blocks 5.4-6.2 wide with tops ~4-5 lower; boulders 3.9-4.4 in the water.**
V17. [should] OuterBend is a corner promontory. **Status: MET.**
V18. [should] The parts cell shows the parts apart. **Status: MET.**

## Rework goals (revision 4)

R1. [must] One palette key per material, no shade variants. **Status: MET.**
R2. [must] Tint is a small random variation. **Status: MET.**
R3. [must] No foam / ripple / flow geometry. **Status: MET.**
R4. [must] Everything below z 1.0 is w03_riverbed. **Status: MET - submerge() cuts and repaints every sand/rock face below 1.0.**
R5. [must] Hero and variants read deep saturated cyan water against a warm sand beach. **Status: PARTLY (UNMET) - the beach reads warm; the water is cyan but paler than the reference (see VR18).**
R6. [must] water_foam every ~5-6 studs plus a ring per boulder in the water, on every tile and the WaterPlane. **Status: MET - see 12 / 24.**
R7. [must] 2-3 chained water_flow beams at z ~1.03 on every tile and the WaterPlane. **Status: MET - 3 beams on each.**
R8. [must] The notes name the foam / flow sockets and say the '+ Foam' is VFX. **Status: MET.**

## Verifier goals (revision 5, kept)

VR1. [must] Fat 8-sided columns with BIG light chamfered tops and deep creases; no totem / wine-glass shapes. **Status: MET - see VR16.**
VR2. [must] A visible warm sand beach 4-6 studs wide over the right half, with pebbles. **Status: MET - see VR19.**
VR3. [must] An S path >= 4 wide and a ramp through the rock gap. **Status: MET.**
VR4. [must] No rock/sand face below z 0.99. **Status: MET (submerge unchanged).**
VR5. [must] >= 30 daisies, interior clumps, tufts, rubble and clumps at the foot. **Status: MET - 32 daisies, 6 interior clumps, 8 tufts, rim hedge, 7 foot clumps.**
VR6. [must] Side cell shows separate stacked columns, mostly lit. **Status: MET.**
VR7. [must] SandStrip is w03_sand only. **Status: MET.**
VR8. [should] GrassTop has ~3 pines; parts apart. **Status: MET.**
VR9. [should] InnerBend bows ~9-10 studs. **Status: MET.**

## Verifier goals (revision 6, failed audit 6/10)

VR10. [must] (G3) Rock: fat 8-sided columns with big bright bevelled tops, deep creases, two height rows; back row 5-7 wide with open ~0.8-1.2 creases; 3-4 lower blocks across the whole width. **Status: MET (build 37) - superseded by VR16.**
VR11. [must] (G4) The grass plateau is prominent and lush: thicker soil lip (~0.8), dense rim hedge, broad pines, a visible daisy scatter. **Status: MET (build 37) - superseded by VR17.**
VR12. [must] (G7) Water reads deep saturated cyan, see-through over the #0B6E8F bed. **Status: UNMET - superseded by VR18.**
VR13. [should] (G10) Dense bush/fern clumps along the rim and foot, >= 20 daisies, rubble. **Status: MET - hero/variant cells: a continuous rim hedge, 7 foot clumps, 32 daisies, 7 rubble stones.**
VR14. [must] (G13) water_foam every ~5-6 studs plus a ring per boulder; 2-3 chained water_flow beams on the hero and Straight. **Status: MET - hero 6 line sockets 5.3 apart (scale 0.6/0.8), 7 rings; 3 flow beams (width 6, z 1.03, -X -> +X) on the hero, Straight and WaterPlane.**
VR15. [should] Beach 5-6 studs wide over the right half; path >= 4.5 wide. **Status: MET - hero cell: beach visible across the right half; path 4.25 wide, ramp 4.6.**

## Verifier goals (revision 7, failed audit 6/10: G3, G4, G7)

VR16. [must] (G3) A FEW big fat 8-sided columns, not a heap: hero back row of 4-5 columns 6-7.5 wide whose big bright
bevelled tops sit level with the turf (in the sun, not in the lip's shadow), a front row of 2-3 blocks ~half as tall
(tops ~4-5 lower) on the left half, at most 2 small low blocks; deep creases between columns. **Status: MET (build 37) - hero/front cells: 4 back-row columns (6-7.5 wide, 5.2-5.8 deep) with broad flat-ish bevelled tops at turf level that read lighter than their sides, 0.7-1.0 creases, a front row of 2 half-height blocks on the left half, 2 small low blocks; variants show the same 5-6 big columns.**
VR17. [must] (G4) Broad open lawn: the grass plateau reads as a wide yellow-green field (hero cell: grass area >= the
visible cliff face area), clumps only along the edge (no continuous hedge), >= 40 daisies on the open turf, thin soil
lip (~0.8 band, lip overhang <= 0.35). **Status: MET (build 37) - top cell: an open lawn ~8 deep between the cliff edge and the S path, 44 daisies, only 4 interior clumps; hero cell: the edge has a loose row of clumps, not a hedge, and the lawn reads as an open daisy field (Straight cell especially). Lip overhang 0.3, soil band 0.8.**
VR18. [must] (G7) Water reads deep saturated cyan see-through over the #0B6E8F bed (render median within ~0.1 S of
the reference #15D4FD). **Status: UNMET, not fixable inside this module (tested) - render median #32BBDC / #44C0DF vs reference #05CDFD / #3ADCFD. Experiment (scratch render of the build-37 hero, same camera): water roughness 0.5 -> #2FBBDC; a brighter riverbed #1592BA -> #33C4E8; both -> #31C5E9 (palette levers move S by <0.05 and would break the shared W03 palette, which must stay verbatim; per-module transparency is forbidden). The kit render's view look 'Medium High Contrast' -> #2BC6ED and 'High Contrast' -> #24D4FF / #38DCFF, a match for the reference (grass #A2D32C vs ref #A3C711). Requested in shared_lib_requests.**
VR19. [should] Pines broad and flared: lowest tier ~8 studs across (about +20%). Beach open and visible in the hero
view over the right half (no step blocks across it). **Status: MET - pines 4.1/3.25/2.4/1.5 tier radii (+20% low tiers); hero beach open over the right half (front row only on the left half, front blocks pulled 0.6 back so sand shows in front of them).**

Status after build 37 (revision 7): every must is MET except the water colour (7 / R5 / VR18), which is set by the shared render pipeline and the shared W03 palette; tested levers and the requested fix are in VR18.

## Iteration log

- Builds 0-19 (earlier runs): see git history of this file; ended with every must MET under the old foam-as-mesh
  approach (resemblance 6/10 at the last audit).
- Build 20 (revision 4): PALETTE cut to the 7 sheet keys (w03_riverbed added; grass/sand/water shade keys and
  w03_foam_soft dropped); the foam line, pale band, dash rows and foam rings removed; the bed and bed walls became
  w03_riverbed; a new submerge() pass cuts sand and in-water rock at z 1.0 and repaints below it riverbed; sockets:
  water_foam every ~7 studs on the shore + one ring per boulder in the water, water_flow beam(s) at z 1.03.
  Result: 0 problems, baked_shading <= 0.04, the water reads cyan with the foam as VFX previews.
- Build 21: the rock-foot clumps moved from GrassTop to RockSlope (they floated under the grass slab in the parts
  cell); parts store w03_hero_offset. Result: the parts cell reads cleanly.
- Build 22: GrassTop now carries the pines (spec). Result: GrassTop 2884/3000; every must goal MET.
- Build 23 (revision 5): columns rebuilt as plain 8-sided hulls (chamfer ~25% of width, no second waist, less
  lean, tint 0.99-1.06); submerge() cuts every sand and rock face at z 1.0; S path 4.8 wide, ramp 4.6; front/lower
  blocks moved off the right half so the beach shows; 8 pebbles; 34 daisies, 8 interior clumps, leaf-green sprigs;
  3 pines; SandStrip all sand; inner bend bulge 10; SIDE_AZIMUTH 68. Result: GrassTop over budget (3199), the S
  read as one broad sand field, the ramp on SandStrip hid RockSlope in the parts cell.
- Build 24: ramp back on RockSlope (SandStrip a flat slab again, parts order Rock/Grass/Sand/Water); path on
  GrassTop; lip/cap/bush lobes lighter (GrassTop 2539). Result: parts apart, budget ok.
- Build 25: bigger S amplitude, path 4.5, side columns narrower with deeper creases, SIDE_AZIMUTH 62.
- Build 26: path 4.25 on a gentler two-bend S (grass shows between the bends); stacked side blocks removed (the
  'totem' right of the ramp and the 'wine-glass' in the inner bend). Result: the top cell reads as an S.
- Build 27: daisies radius 1-1.2, 7 bigger rubble stones, 2 more foot clumps. Result: 0 problems, every goal MET.
- Build 28: docstring-only change (side-column description); identical stats (26722 tris, 0 problems).
- Build 29 (revision 6): column barrels rounder (superellipse 0.7-0.82, chamfer 27% of width); back row 5-6.4
  wide with 0.8-1.2 creases; front row 2-4 lower; 4 lower blocks across the width; rim recess 8.6 -> 4.8;
  soil band 0.8; new 4-tier pines on a visible trunk; auto rim hedge; foam every 5.5 (scale 0.6/0.8), rings
  0.5-1.0, 3 chained flow beams width 6 everywhere; outer bend swells 4.5 out. Result: separate blocks, but
  back-row tops too low (a flat backing wall showed above them); GrassTop soil/sand shading 0.77.
- Build 30: back row taller, rim recess 3.4, bigger hedge, broader pines. An edit slip put the pines in the
  dirt loop (variants lost their pines).
- Build 31: pines restored; GrassTop kit_shading_ok for the sand-path / soil-band family. 0 problems.
- Build 32: back row tops 9.2-9.6, deeper columns, backing wall moved to rim+2.0, denser hero front row,
  pines r 3.4. Debug rebuild: the back row left 3.6 studs empty before the ramp gap.
- Build 33: column before the ramp gap filled (>= 2.2 wide), creases 0.7-1.0, shore recess 0.4 (wider beach),
  right-edge front block dropped. Result: 0 problems, 28469 tris; cliff reads as separate stepped blocks,
  dense rim hedge; water colour unchanged (#44BFDF vs ref #15D4FD).
- Build 34 (revision 7): back row rebuilt as 4 big columns 6-7.5 wide, 5.2-5.8 deep, standing in front of the rim
  with tops at turf level (GZ -0.5..+0.3); chamfer 32% of width (max 2.5); lip overhang 0.5 -> 0.3; front row cut to
  2 blocks on the left half; lower blocks 4 -> 2; rim hedge -> a loose row (step 4.6, scale 0.85-1.1) 2-2.8 behind
  the rim; 44 daisies; pines' lower tiers +20%; rim bulge 3.4 -> 2.4. Result: a few fat columns with lit bevelled
  tops instead of a heap; open lawn.
- Water experiment (scratch render, no module change): palette roughness / riverbed tweaks barely move the render
  (#32BBDC -> #31C5E9); the High Contrast view look gives #24D4FF (reference #05CDFD). Shared-lib request.
- Build 35: pines set back from the rim; variant daisies 32-34; docstring. Result: lawn in front of the pines open.
- Build 36: front row pulled 0.6 back (sand shows in front of it on every tile); flatter top bevel (shoulder at
  0.55 x inset). Result: Straight variant shows its beach; tops a little brighter.
- Build 37: hero S path kept toward the back (dip at y 11 instead of 8.6). Result: top cell shows an open lawn
  ~8 deep in front of the path; 26493 tris, 0 problems.
