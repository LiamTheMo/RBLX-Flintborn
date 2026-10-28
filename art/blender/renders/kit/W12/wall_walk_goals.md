# W12 WallWalk goals (row 3) - revision after verifier fail

Status is judged by eye against the reference row in `wall_walk_compare.png` (revision build 4).

## ASSEMBLED / HERO
1. [must] Long low walk silhouette (clearly wider than tall), deck at z7 visible from above-front. - PARTLY / UNMET - hero now reads long (about 2:1 wide), stair off to the left; the deck top is still mostly hidden behind the rails at the kit camera elevation
2. [must] 5 upright posts per side rise past the deck to ~z10 with pyramid caps and rope bands at the deck line. - MET - all 10 posts run to 10.3 with caps and tan bands at deck, mid and top rail
3. [must] Two rails (upper ~9.6, mid ~8.45) on both long sides and the right end, rope at joins; left end open only where the stair arrives. - MET - full two-bar rail front and back and right end; left end open for the stair
4. [must] 6 chunky steps at the left end, descending to the left, with two stringers and an outer handrail; front plank wall and banner unobstructed. - MET - stair runs -X off the left end; treads now stand proud of the lowered stringers; handrail on the front side
5. [must] Red swallowtail banner with cream diamond emblem fully visible on the front panel, centre-right. - MET - banner fully visible right of centre in hero and front cells
6. [must] Front panel of vertical planks under the deck with 45 deg braces and rope lashings. - MET - plank wall with alternating diagonal braces and lashings, banner bay kept clear
7. [must] Base dressing: 3-4 grey boulders 1.5-2.2 studs at post feet and stair foot, chunky clover clumps with small flowers along the base. - MET - 4 boulders (1.8-2.2) and 10 clover clumps r0.9-1.0 with yellow flowers; boulders still read a little smaller than the reference
8. [must] Scale: deck 11x4, 4 stud clear walkway, rail top ~2.6-2.8 above deck, ~7 deep, ~10 tall. - PARTLY - deck 11x4, rail top 2.8 above deck, 8.3 deep, 10.3 tall; length is 21 because a 6x1-stud stair run cannot fit in a 14 stud footprint beside an 11 stud deck (spec conflict)
9. [should] HERO_AZIMUTH -22. - MET - set to -22

## FRONT
10. [must] Front view: long rectangle, diagonal stair stringer/handrail at the left, banner right of centre. - MET - long rectangle with diagonal handrail and stair on the left, banner right of centre

## SIDE / REAR
11. [should] Rear view shows posts, braces and the stair profile on the right, wall lit. - MET - SIDE_AZIMUTH -160 shows the rear wall lit, rear braces and the stair profile on the right

## TOP
12. [should] Top view: long plank deck with post tops, stair treads at the left end. - UNMET - the top cell renders the long hero foreshortened and partly shadowed; deck and treads are hard to read

## PARTS
13. [must] All 5 parts present (capped post with rope band, two-bar railing, plank, post with 45 deg brace and lashing, 4-step block stair). - MET - all five built
14. [must] Each part readable in the parts grid with its own space. - UNMET - post, steps, railing and plank read; the brace sits between the steps and the railing and is only partly readable (grid packing is automatic; brace shortened to 4.3 to reorder it)

## VARIATIONS
15. [must] A STRAIGHT: 12x4 deck on chunky posts, rails both sides, X braces, no stair/banner, boulders and clover. - MET - 12 long deck at 5.4 on 1.3 posts, X braces, rails, 3 boulders, 5 clover clumps
16. [must] B CORNER: L deck of two 8x4 arms, outer rails only, tall corner post, extra braces, rope coil. - MET - L deck reads; one brace and the rope rings removed to declutter
17. [must] C STAIR BAY: taller (~11) posts, 8-step stair at the front-left with handrail, top rail, one end open. - MET - 11.4 posts, 8-step stair with handrail, open front-left

## PALETTE
18. [must] w12_wood #8F5A2C on all timber, warm orange-brown in render. - MET - matches the reference wood
19. [must] w12_tan rope, w12_stone grey boulders, w12_leaf green clover, w12_banner_red banner, w12_banner_trim emblem, w12_walk_flower #F2C230 tiny flowers. - MET - each material in its place
20. [should] Budgets and cleanliness: hero <=8000, parts <=1500, variants <=6000, 0 problems. - MET - hero 6368, variants 2.9-3.2k, parts <=336, 0 problems

## Iteration log
- Builds 1-4 (first run): see verifier report; hero was a square block with the stair across the front.
- Revision build 1: stair moved to the left end running -X, full front posts and rails, rails raised to 9.6/8.45, HERO_AZIMUTH -22, SIDE_AZIMUTH -160, bigger rocks, clover with flowers. Hero now long, banner clear, rear shows the stair.
- Revision build 2: bigger boulders; parts reordered (brace still hidden behind steps).
- Revision build 3: brace 4.3 tall so the grid puts it in front of the steps; steps turned to face the camera.
- Revision build 4 (cap): stringers lowered so treads read, hero posts 1.0, brace angled to the front-left. Brace readability and the deck-top view remain open.
