# W06 row 3 - Hanging Vine: visual goals

Reference: `art/reference/kit/rows/W06_row3.png` (and the full sheet `W06_bushes_ferns_vines_moss.png`).
Module: `art/blender/scripts/kit/W06/hanging_vine.py`. Compare: `hanging_vine_compare.png`.

Note on the FRONT / SIDE / TOP cells: the reference draws these three cells as a single standalone
vine on a pad (the same object as Variation A), while the spec makes the hero the overgrown wall
chunk, and the runner renders the hero in those cells. The FRONT/SIDE/TOP goals below are therefore
written for the hero wall seen from those directions; the reference's single-vine views are matched
by StraightVine (goal 18).

Status after build 6 (final).

## ASSEMBLED / HERO (HangingVine)
1. **must** - Reads as a chunk of ruined light-grey stone wall overgrown by two thick vines; overall ~7 W x 4 D x 7 H studs (roughly as wide as tall in the iso view, like the reference). **MET** - iso cell shows a grey block wall with a braided vine at the left and at the right corner; wider than tall by ~1.2x as in the reference cell. Wall itself 6.6 x 3 x 6.1; with leaf tips the box is 8.2 x 4.8 x 6.9 (leaves at the foot and the corner run past the wall ends, as the reference's foot leaves do).
2. **must** - Wall is 4 stacked courses of chunky bevelled blocks (~1.6-2.4 long x ~1.45 high), staggered vertical joints, bevels give visible joint lines between blocks. **MET** - front and iso cells: 4 courses, 3 blocks per course with offset joints and bevel grooves.
3. **must** - Broken top: top-course blocks at uneven heights, the top-right block steps up and overhangs the right end, and the course below it is missing its corner block (a notch under the overhang). **MET** - front cell: middle top block dips below its neighbours, the right top block stands highest and runs past the courses below; the corner notch under it is mostly covered by the right vine's leaves (as the reference's right side is covered).
4. **must** - Two thick brown vines hang from the top edge to the ground: one in the left third of the front, one at the right-front corner; both run the full height and touch the ground. **MET** - front/iso cells: both vines start on the wall top, run down to the ground and curl forward at the foot.
5. **must** - Each vine is visibly two strands twisted together (at least 3 crossings visible per vine in the iso view), swinging gently side to side; combined vine ~0.6-0.8 studs wide, about as thick relative to the wall as in the reference. **MET** - iso cell: two brown strands with gaps between them cross 3-4 times per vine (loose braid, strand r 0.17, offset 0.21 -> ~0.76 wide).
6. **must** - Leaf clusters of 3 pointed ivy leaves sit every ~0.8 studs along each vine, alternating left/right; at least 7 clusters per vine on the front; leaves big (~1 stud) as in the reference, angled out off the wall. **MET** - front cell: 8-9 broad lobed 3-leaf clusters per vine, alternating sides, facing out from the wall.
7. **should** - Leaves spill onto the top of the wall at both vine heads (at least 3 clusters lying on top). **MET** - iso/top cells: 2-3 clusters lie over each vine head on the wall top and hang over the front edge.
8. **should** - A small pile of leaf clusters on the ground at the foot (at least 2 at the left foot, 1-2 at the right foot), with 2-3 small grey rubble stones and small dark soil patches at the vine roots. **MET** - front cell: leaf piles at both feet, a small grey stone between them; soil patches mostly under the leaves.
9. **should** - 5-10 small yellow-green moss specks sit in block joints on the front. **MET** - front cell: ~6 lime specks visible in joints.

## FRONT
10. **must** - Front view: 4 courses with staggered joints visible between the two vines; the two vines frame the wall left and right and span top to ground; leaf clusters alternate sides down each vine. **MET** - front cell shows exactly this.

## SIDE / REAR
11. **should** - Side view: wall depth ~3 with block ends per course; the right vine wraps the corner onto the side face; leaves stand out no more than ~1 stud from the front face. **MET** - side cell: 4 block ends stacked; the right vine hugs the front-right edge and swings onto the side around z 1.5-3; leaves stay within ~1 stud of the face except the arc over the top.

## TOP
12. **should** - Top view: rectangular wall top made of uneven blocks with the overhanging top-right block; leaf clusters cover the two vine heads and hang over the front edge. **UNMET** - top cell shows the 3 top blocks and leaf-covered vine heads over the front edge, but the overhang of the right block is not legible from above.

## PARTS
13. **must** - VineLeafCluster: three pointed, lobed ivy leaves fanned from one short brown stalk (centre leaf + two side leaves), ~1.2-1.4 across, flat-faceted with a midrib crease. **MET** - parts cell (front): three lobed green leaves fanned from a brown stalk, 1.2 across.
14. **must** - VineSegmentStraight: ~4 long, gently curved brown stick, r ~0.17, 6-7 visible facets along its length, flat cut ends with an inset ring; leans like the reference drawing. **MET** - parts cell (back): long brown stick leaning up-right with a slight bow, flat cut ends, 7-sided.
15. **must** - VineFork: Y/T junction ~1.6 W x 1.4 H - a downward leg, a short arm out to the left and a longer arm rising up-right, cut ends; same thickness and colour as the segment. **MET** - parts cell (middle): brown Y with leg, short left arm, long up-right arm.
16. **must** - VineAttachmentPad: grey faceted stone plate ~1 W x 0.5 D x 1.3 H (irregular hexagon/octagon outline, chamfered front face) with a round brown vine stub in a socket at the front centre. **MET** - parts cell (front right): grey faceted plate with a brown stub on its face, 1.0 x 0.7 x 1.3 incl. stub.
17. **should** - Modular: segment, fork, pad stub and every vine strand share radius 0.17 and the one bark colour, so they join cleanly. **MET** - one STRAND_R constant and one w06_bark key for all of them.

## VARIATIONS
18. **must** - A. StraightVine: grey stone pad at the top, a braided double-strand vine hanging straight down ~8 studs with a slight sway, leaf clusters alternating left/right all the way down (at least 9) and a leaf tip at the bottom; tall and narrow like the reference. **MET** - variant cell 1: grey block pad on top, loose two-strand braid, ~9 alternating clusters + tip cluster; 2.2 x 9.4.
19. **must** - B. BranchedVine: two pads ~4 apart (left one a little lower), two vines hanging to the ground and a diagonal vine from the right vine down to the left vine joined through a fork, giving an M/N silhouette with 2-3 hanging ends; ~5 W x 8 H. **MET** - variant cell 2: N/M silhouette, left pad lower, the diagonal merges into the left vine part-way (the fork), two hanging ends; 6.2 x 8.8.
20. **must** - C. CurvedDraping: two pads ~6 apart, a vine sagging in a U-shaped swag between them (lowest point ~2.5-3 below the pads) with leaf clusters along it, plus a hanging end ~5-6 long below each pad; ~7 W x 7.5 H. **MET** - variant cell 3: U swag dipping ~2.7 below the pads with leaves, a hanging end under each pad (right one longer); 7.8 x 7.9.
21. **must** - Every variant's vines start at a grey stone attachment pad (pads read as chunky grey blocks, clearly lighter than the bark). **MET** - all three variant cells show light grey block pads at the vine heads.

## PALETTE (one base colour per material)
22. **must** - Exactly these base colours: stone `w06_stone` #B1ADA9 (wall blocks, pads, rubble), bark `w06_bark` #8D6237 (vine strands, stalks, stubs, parts), leaves `w06_ivy` #66A828 (all leaves), moss `w06_moss` #ACC722 (joint specks only), soil `w06_soil` #6E4B2B (small root patches only). No shade variants; runner ends with 0 problems. **MET** - module PALETTE holds exactly these sheet entries; STATS line ends "0 problems".
23. **must** - By eye the leaves read as bright mid-green, the vines as mid-brown and the blocks as light warm grey, matching the reference hues. **MET** - compare image: same green/brown/grey families as the reference row.

## SCALE / BUDGET
24. **must** - Scale in studs: hero ~7 x 4 x 7; leaves ~0.9-1.1 long; strands r 0.17 everywhere; StraightVine ~9 H; BranchedVine ~5-6 x 8-9; CurvedDraping ~7-8 x 7.5-8. **MET** - KITSTAT: hero 8.2 x 4.8 x 6.9 (wall 6.6 x 3 x 6.1, the rest is leaf tips), StraightVine 9.4 H, BranchedVine 6.2 x 8.8, CurvedDraping 7.8 x 7.9; leaves 0.9 (variants) / 1.1 (hero).
25. **must** - Triangle budgets: hero <= 5000, each part <= 150, each variant <= 2500; nothing below z=0; one mesh per asset. **MET** - hero 3284, parts 74/150/132/96, variants 1128/2248/2416; runner reports no origin/z problems.

## Iteration log
- Build 1: first pass. Leaves read as small spiky stars (deep notches, 0.78 long), pads tiny, parts cell overlapped (segment in front hid the others); BranchedVine, CurvedDraping and VineFork over budget.
- Build 2: broader 10-point ivy outline with flat underside (18 tris), leaves face the viewer more, hero leaves 1.0, strands r 0.19; fork inner ends left open inside the junction, third branched end dropped, coarser rings. Budgets fixed except CurvedDraping (+120).
- Build 3: segment leans like the reference and parts footprints tuned so the grid lays segment at the back, fork, then cluster + pad in front (all four visible); variant pads bigger. Leaves now right-sized but pads hidden by leaves.
- Build 4: variant pads became chunky chamfered-square blocks (1.7 x 1.55 x 0.9) with one leaf cluster at the stub instead of two; LEAF_L 0.9. All budgets OK, 0 problems; pads clearly visible.
- Build 5: loose braid (strand r 0.17, offset 0.21, pitch 2.4) so the two strands and their crossings read; fixed the edge-on "spike" leaves over the wall top (side vector degenerate where the vine runs toward the viewer).
- Build 6: tightened hero footprint (shorter overhang, feet curl less, foot leaves closer), right vine moved out of the side face where it wraps the corner.
