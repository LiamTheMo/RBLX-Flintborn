# W14 TunnelModule goals (revision 2, after verifier fail 5/10)

Reference: art/reference/kit/rows/W14_row2.png. Status after each build: MET / UNMET + evidence.

## ASSEMBLED / HERO
1. [must] Straight tunnel segment, axis Y, open at both ends with a straight view-through. — MET: front cell shows straight passage with the far end open; hero iso open -Y end.
2. [must] Footprint exactly 32 x 32 (X and Y each <= 32.5 incl. dressing), height ~20 (18-21): tiles on the 32 grid. — UNMET (marginal): reads square, height 18.7; KITSTAT 33.4 x 32.7 - roof boulder roughness overshoots Y by ~0.35 per end (X overshoot is side slabs).
3. [must] Wide low cave: large squarish opening ~16 wide x 11 tall, ~50% of the front width and ~55-60% of the height; side slab walls clearly visible flanking it. — MET: front view shows a wide squarish ~16x11 opening, ~50% of width, flanked by tall slab jambs.
4. [must] Walls are rows of tall tapered angular slabs (4-5 per side, varied heights, slanted tops) with deep gaps, visible in hero/front/side, not bevelled boxes and not hidden by roof boulders. — MET: hero/front/side show 5 tall tapered slabs per side with slanted chipped tops and dark seams; no haunches.
5. [must] Roof is a lumpy boulder band (~6-8 thick, <= ~40% of total height) over the walls, slightly wider than the walls, bumpy top; no haunch boulders in the opening corners. — MET: roof is a ~7-stud lumpy boulder band (~38% of height) over the walls, bumpy top; slightly heavier/rounder than ref.
6. [must] Sand-tan floor of separate irregular plates with seams, slightly raised rock rim stones along both wall feet, floor running the whole 32 length to the front edge. — MET: irregular tan plates with seams run to the front edge, grey rim stones along both wall feet.
7. [should] 2-3 pebbles plus a couple of small boulders at the front corners, inside the footprint. — MET: two small boulders at front corners plus pebbles on the floor in hero/front.
8. [should] 3+ small green tufts at the front outer base and along the side base. — MET: green tufts at both front corners and along side bases.

## FRONT
9. [must] Front view: squarish opening ~16x11 with straight slab jambs, roof band of 3-5 lumpy boulders across the top, back opening visible as a light patch. — MET: front view: squarish opening with straight slab jambs under a 3-boulder roof band; back opening light.

## SIDE / REAR
10. [must] Side/rear cell is readable (not a near-black mass): the closed outer wall of vertical slabs topped by the boulder roof, with an end opening visible at one end. — MET: rear 3/4 cell now lit mid-grey: slab wall row under the boulder roof, end opening with floor visible at left.

## TOP
11. [must] Top view: ~32x32 square of lumpy roof boulders, bumpy, 10+ distinct boulders, wall slab tops visible along both long edges. — UNMET (should-level gap): top is a 32x32 square of 16 lumpy boulders but wall slab tops are hidden under the roof, unlike the ref cutaway.

## PARTS
12. [must] Five parts readable and similar to the ref: Ceiling (~32x30x8 lumpy boulder run, flat underside), LeftWall (~6-8 x 30 x 14 row of tapered slabs), RightWall (~6-8 x 30 x 13, different arrangement), Floor (~16x32 irregular plates + rim stones), Rubble (8-10 pebbles + 2 small boulders). — MET: parts cell: lumpy ceiling run, 5-slab left and 4-slab right walls, plate floor with rim, rubble set (small in the cell).
13. [should] Wall parts use tapered angular slabs of varied heights with gaps (several hundred tris each, not 236-300). — MET: wall parts are tapered angular slabs of varied height with gaps (436/328 tris).

## VARIATIONS
14. [must] A. Straight: rectilinear box, flat even roof of aligned boulders, straight slab walls, no haunches, visibly lower than the hero; distinguishable from the hero. — MET: Straight is a lower (14.5) rectilinear box with flat seamed block roof and straight slab walls; clearly different from the lumpy hero.
15. [must] B. Bend: rectilinear L readable from the iso view: -Y entry arm and +X exit arm, slab walls on the outer (-X and +Y) edges, inner corner pillar at +X/-Y with the roof notched above it, flat roof. — UNMET: flat block roof with a notch over the inner pillar at front-right is visible, but at this camera the L still reads mostly as a square box.
16. [must] C. Junction: plus-shaped roof readable from iso, four 16-wide openings (-Y,+Y,-X,+X), stacked-slab pillar clusters at the four corners, flat roof, sand cross floor. — UNMET: corner notches with slab pillar clusters visible (front-left), four openings exist, but the plus outline is weak from the iso; reads as a notched box.

## PALETTE / SCALE
17. [must] Rock is ONE warm grey-mauve key w14_rock #8C7F7A (ref mid-tone between lit ~#A89E96 and shadow ~#6A6066), renders warm grey, not chalky. — MET: rock renders warm grey-mauve, lit faces pale warm grey, shadows plum-grey, close to ref.
18. [must] w14_sand #C79B6C only on floor plates (reads tan, as pale as possible given the fixed palette); w14_moss #5C8A2E only on tufts. — MET: sand only on plates (reads orange-tan, more saturated than ref; palette is sheet-fixed), moss only on tufts.
19. [must] Nothing below z=0, every asset one mesh, hero <= 7000 tris, variants <= 6000, parts within budgets, 0 problems. — MET: 0 problems; hero 3170/7000, variants 1927-2402/6000, parts in budget, one mesh each.

## Iteration log
- Rev1 builds 1-4: boulder dome with haunches; failed verifier (Y 36.5, walls hidden, variants unreadable).
- Rev2 build 1: tapered 5-sided prism slabs, 3-col boulder roof, no haunches, 32-clamped; L/plus variants, HERO_ELEVATION 28, SIDE_AZIMUTH -135 -> opening wide, side cell lit; slabs read as round posts, roof gappy.
- Rev2 build 2: slabs as bevelled boxes tapered with slanted chipped tops; variant roofs as flat blocks -> walls read as slabs; hero roof spiky with gaps.
- Rev2 build 3: fuller overlapping subdiv-2 roof boulders, deeper variant notches -> hero/top filled, roof band reads.
- Rev2 build 4: seams between variant roof blocks, thinner Straight roof -> Straight reads as rectilinear seamed box. Build cap (4) reached; Bend/Junction legibility and 0.35-stud Y overshoot remain.
