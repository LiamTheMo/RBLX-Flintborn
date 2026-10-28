# W13 GuardLodge goals (row 2)

Reference: art/reference/kit/rows/W13_row2.png. Note: the reference hero/side cells are front-RIGHT
three-quarter views (front gable with door on the left of the image, long +X side wall with the window on
the right), so the hero camera sits front-RIGHT (HERO_AZIMUTH = +46, not the spec's -22): -22 shows the -X wall and
puts the door on the right of the image, the mirror of every reference cell. SIDE_AZIMUTH = 62 because the
reference SIDE cell is a side-on three-quarter view, not a flat elevation. Ridge runs along Y (gables
face -Y/+Y), as every reference cell shows; the spec's "ridge along X" contradicts its own "gable ends
front/back".

## ASSEMBLED / HERO
1. [must] Silhouette: a small house about as tall as it is wide (height ~15.5-16 incl. ridge cap vs 17 wide roof), roof is the top ~45% of the height.
2. [must] Cream canvas roof (w13_canvas) pitched with ridge along Y, overhangs ~1.5 studs past the side walls and drapes down at the eaves with a scalloped hem.
3. [must] Four 1x1 timber corner posts whose cube caps poke clearly above the roof edge at all four corners; a cap/knob at the ridge ends.
4. [must] Plank walls: vertical planks visible on front gable and side wall, with horizontal frame beams (top plate, lintel beam across the front, a rail on the side wall).
5. [must] Grey stone footing course (w13_stone, ~1.2 high) runs round the whole base with larger corner blocks.
6. [must] Front: framed doorway 4.5 wide with plank door showing an X brace, left open enough to walk through, dark interior visible; 2 plank steps up to it.
7. [must] Lantern on a bracket left of the door at z~5.5 with glowing orange glass (w13_lantern_glow) and a heat_glow socket.
8. [must] Small square window (~2.5) with dark w13_glass panes and timber frame on the right (+X) side wall, with a canvas awning above it.
9. [should] Crate and barrel stand beside the front-left corner.
10. [should] Small base dressing: 2-3 rubble stones and 2 moss/grass tufts at the footing.

## FRONT
11. [must] Front view reads as a gable house: triangular canvas roof outline with apex centred, door centred, lantern left of the door, corner caps at both eave corners; width ~1.15x the wall height+roof... overall front silhouette ~17 wide x ~16 tall.
12. [should] Gable triangle above the door is planks with a centre king post and a horizontal beam over the door.

## SIDE
13. [must] Side view shows the long side wall with the window + awning, roof as a slanted surface with eave hem, footing below.

## TOP
14. [must] Top view: an almost square cream canvas rectangle (~17 x 14) with a ridge line along Y and four timber corner caps at the corners.

## VERIFIER GOALS (revision 1, all must unless tagged)
23. [must] HERO: steep canvas pitch like the reference tent roof, roof ~top 40-45% of the height, not flat/bulky.
24. [must] HERO: front gable with door on the left of the image, +X side wall with window + awning legible on the right.
25. [must] HERO: wood reads warm mid golden brown, not darker/redder than the reference.
26. [should] HERO: base dressing: 4-6 rubble stones and 2-3 leafy clumps round the footing.
27. [should] HERO: crate and barrel at the front-left, both readable.
28. [must] FRONT: centred closed/ajar plank door with X brace in a frame, lantern left, 2 steps, king post + beam.
29. [must] SIDE: long plank wall with rail, dark-glass window with striped awning, slanted roof with hem, no door leaf sticking out.
30. [must] VARIANT B: front (-Y) lower wall removed; half wall + counter, bench and posts on the lit front, interior visible.
31. [should] Awning has stripe bands; stone footing ~1.4 high with chunky corner blocks.

## PARTS
15. [must] All 11 labelled parts exist as separate assets: CanvasRoof, RoofBeam, WallPanel, InteriorShelf, Floor, RearWall, SideWall, Doorframe, Door, WindowAwning, Window.
16. [should] CanvasRoof part is a pitched cream canvas with a timber ridge/rafter frame; Door part shows the X brace; Floor part is planks on stone blocks; InteriorShelf has two small crates.

## VARIATIONS
17. [must] A. Narrow Lodge: visibly narrower (~10 wide) same-style lodge with door, steps, lantern and window+awning.
18. [must] B. Open Guard Hut: the side wall replaced by a low half wall/counter with posts under the canvas, interior visible; lantern kept.
19. [must] C. Abandoned Lodge: canvas torn open at the ridge exposing rafters, a ladder leaning on the side, broken steps, missing/leaning planks, green moss/vines (w13_moss) on footing and roof, no lantern.

## PALETTE / SCALE
20. [must] Palette: all wood one key w13_timber (#A9612C), canvas w13_canvas (#E6D2A4) only on roof/awning, stone w13_stone (#8A9199) only on footing/rubble/knob, w13_glass on window panes, w13_lantern_glow only lantern glass, w13_moss only tufts/vines. Render shows warm orange-brown wood and warm cream canvas like the reference.
21. [must] Scale: hero footprint ~14 x 12 walls (+ roof overhang 17 x 14 + steps), walls ~8 tall above footing, ridge ~15; doorway lets a 5.5-stud character walk in (opening >= 7 tall).
22. [must] Tris within budgets (hero/variants <= 8000, parts <= 1500), build ends with 0 problems.

## Status (revision build 4, judged by eye against the reference row)
1. MET - hero: compact house about as tall as wide; roof is the top ~45%.
2. MET - side/hero: steep cream canvas, ~1 stud overhang with a light scalloped hem draping over the wall tops.
3. MET - four cube caps poke above the eave corners in hero, front and top; stone knob at the front ridge.
4. MET - vertical planks on gable and side wall; lintel beam, top plate and side rail visible.
5. MET - grey footing course, taller now (1.4) with 2x2 corner blocks, visible all round.
6. MET - front: framed 4.5 x 7.5 doorway, plank door ajar ~22 deg, X brace faces out, sits centred; 2 steps.
7. MET - glowing orange lantern left of the door in hero and front cells; heat_glow socket.
8. MET - hero/side: dark-paned window with frame on the +X wall, awning above it, window no longer covered.
9. MET - front cell: crate stack and barrel stand at the front-left beside the steps (hero shows them at the left edge).
10. MET - 6 rubble stones and 4 moss clumps round the footing (hero/front), still smaller than the ref's.
11. MET - front: centred triangular gable, door centred, lantern left, caps at both eave corners.
12. MET - king post and horizontal beam across the gable over the door.
13. MET - side: long plank wall, window + awning, slanted roof with hem, footing, no door leaf at the left.
14. MET - top: near-square cream canvas with four corner caps.
15. MET - parts cell shows all 11 parts.
16. MET - roof on frame, X-brace door, plank floor on stones, shelf with crates.
17. MET - Narrow lodge visibly narrower with door, steps, lantern, window + awning (window on +X like ref cell A).
18. MET - Open hut: front lower wall gone, counter + half wall + bench + posts on the lit front, interior shelf visible.
19. MET - Abandoned: torn canvas with rafters, ladder, broken steps, missing/leaning planks, moss/vines, no lantern.
20. MET - only the 6 sheet keys, each on its listed material.
21. MET - walls 14 x 12, ~8.6 incl. footing, ridge ~15.9, door 4.5 x 7.5, roof 16 x 14.
22. MET - hero 7212/8000, variants 6132-7540, parts <= 1500; 0 problems.
23. MET - roof slope 0.98 (~44 deg) reads as a steep tent roof like the ref; overhang cut to 1.0 so it is lighter.
24. MET - hero at +46: gable with door on the left, lit +X wall with window and awning on the right.
25. UNMET - wood still renders orange (#A9612C sheet key); ref is more golden. The sheet palette must be copied
    verbatim and all four W13 modules use #A9612C, so changing it here alone would break sheet consistency
    (requested sheet-wide #B87A3A in shared_lib_requests). Walls are no longer mostly in shadow.
26. MET - 6 stones + 4 clumps (thinner than the ref, which also has flowers that need a key the sheet lacks).
27. MET - front cell shows crate stack and barrel side by side at the front-left.
28. MET - front cell: centred X-brace door ajar, lantern left, 2 steps, king post + beam.
29. MET - side cell: plank wall with rail, dark window, awning with 4 raised bands, slanted roof with hem (bands are same-colour so stripes read only faintly).
30. MET - variant B cell: open front with counter, bench, posts and visible interior, lantern on the left post.
31. MET - footing 1.4 with 2x2x1.8 corner blocks; awning has raised stripe bands (faint).

## Iteration log
- Builds 1-4 (first pass): see earlier version; ended with door swung wide, flat roof, OpenHut counter on +X.
- Rev build 1: slope 0.82->0.98, overhang 1.5->1.0, footing 1.4, door 7.5 ajar 22 deg, OpenHut open front with counter/bench/posts, awning bands, more dressing, barrel moved out. Window was hidden by the eave hem.
- Rev build 2: shallower hem, eave/wall +0.2, window up, HERO_AZIMUTH 46. Awning still covered the window top.
- Rev build 3: crates+barrel moved to the front-left by the steps; window lowered, awning shorter.
- Rev build 4: awning raised to 7.45 so the window shows fully under it. Build cap reached.
