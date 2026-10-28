# W07 row 1 - GrassTuft goals

Status after revision build 4 (8 builds total): every must goal MET by eye against the reference row; 0 problems.

## ASSEMBLED / HERO
1. [must] MET - Blades are chunky solid prisms (6-sided section) with a raised mid-rib crease and a pointed tip, not flat cards. Evidence: hero and front cells show two-tone halves split along a centre crease on every blade.
2. [must] MET - (verifier) 5 dominant broad lanceolate blades (2.15-3.0 tall, 1.2-1.3 wide at the widest point, about 0.75 at the base) plus 2 low side blades, fanned from one base. Evidence: the hero cell shows 5 fat leaf-shaped blades and low blades at the left and right foot. It no longer has 9 thin spikes.
3. [must] MET - Blades splay outward from one base like a fan. Low side blades lean out near the foot. Evidence: hero and front cells.
4. [must] MET - 3 grey pebbles at the foot of the hero (0.48-0.72 studs). Evidence: grey stones at the front-left, front-right and front foot. They read a little smaller than the reference's.
5. [should] PARTLY - Hero size ~3.2 x 3.2 x 3.0. Evidence: KITSTAT 3.5 x 3.2 x 3.0. Depth and height are fixed; the low side blades leave the width 0.3 over.
6. [should] MET - Hero ~800 tris with chunky facets. Evidence: 604/800 (was 380). Each blade has 6 rings x 6 sides.
7. [should] MET - Blades are lanceolate: narrow base, widest at ~35-50% of the height, tapering to a point. Evidence: the front cell shows leaf-shaped blades, like the reference.

## FRONT
8. [must] MET - The front view shows a fan of 5-7 broad pointed blades from a narrow base, width about equal to height. Evidence: the front cell.
9. [should] MET - Pebbles show at the left and right foot in the front view.

## SIDE
10. [should] MET - The side view shows a fanned clump, not a flat comb. Evidence: the side cell shows blades splaying to both sides.

## TOP
11. [must] MET - The top view is a star of pointed blades radiating from the centre, with the orange root visible. Evidence: the top cell shows about 6 lobes around an orange centre. It is a little more crowded than the reference's clean 6-point star, because the side blades are rolled to face the front.

## PARTS
12. [must] MET - SingleBlade is ~2.6 tall and ~0.7 wide, ridged, broad-bodied, pointed, with a slight lean. Evidence: the right blade in the parts cell (0.7 x 0.6 x 2.6), 94/150 tris (was 30).
13. [must] MET - (verifier) ThreeBladeClump is ~1.6 wide, with a tall centre (2.6) and two 2.0 flanks splaying left and right, broad (0.85), joined at the base. Evidence: KITSTAT 1.5 wide, 282/500 tris (was 2.84 wide and 90 tris). The parts cell shows three fat blades.
14. [must] MET - RootBase is an orange-brown stub ~0.7 tall with 5 flared root fins. Evidence: the orange stub in the parts cell (0.6 x 0.8 x 0.7). The auto layout hides some of it behind the clump.

## VARIATIONS
15. [must] MET - ShortWide: 7 short broad blades 1.4 tall in a low rosette (3.9 x 3.6), clearly wider than tall. Evidence: the variant cell, a low spreading star.
16. [must] MET - (verifier) TallPointed: 6 upright broad blades 4.2 tall with sharp points, broader than a spindle. Evidence: the variant cell shows fat leaf-shaped blades (1.1 wide) in a tall clump, 2.0 x 1.6 x 4.2. It fans out less than the reference.
17. [must] MET - DryGrass: hero-like 6 broad blades 2.8 tall with drooping tips, all w07_grass_dry gold. Evidence: the variant cell shows a gold clump with curled-over tips.
18. [should] MET - The variants differ by silhouette: low and wide, tall and narrow, gold and drooping.

## PALETTE / SCALE / TECH
19. [must] MET - The blades are w07_grass #5A9A1E and render as saturated lime green on lit faces. Each material has one key.
20. [must] MET - w07_root #B8672A is on the root base (RootBase and the top-view centre). w07_stone #8E8E94 is on the pebbles. w07_grass_dry #D2A850 is on the dry blades.
21. [must] MET - Origin is at the bottom centre and nothing sits below z=0. Collision is none on all 7 assets. Evidence: the build reports 0 problems (the runner checks origin and z).
22. [should] MET - Tris are spent on silhouette: hero 604, ShortWide 538, TallPointed 540, DryGrass 468, SingleBlade 94, ThreeBladeClump 282, RootBase 54. All are under budget.
23. [should] UNMET - In the parts cell, SingleBlade overlaps RootBase/ThreeBladeClump. The build_kit layout places them, so this can't be fixed in the module.

## Iteration log
- Builds 1-4 (first run): diamond-section blades and a 9-blade hero. The verifier failed it as thin and spiky.
- Revision build 1: 6-sided ridged section, 6-8 rings, hero cut to 5+2 broad blades, roll parameter, flanks rolled to face the front. Blades were broad but wide at the base (spiky), ThreeBladeClump was 1.1 wide, TallPointed was a spindle.
- Revision build 2: lanceolate profile (widest mid-blade), hero blades 1.2-1.3 wide, bigger pebbles, more flank lean. The blades now read as fat leaves. ThreeBladeClump went to 2.0 wide.
- Revision build 3: flank lean tuned (ThreeBladeClump 1.5), hero depth 3.2, thicker ridge (0.62), TallPointed blades 1.1 wide.
- Revision build 4: rolled the side blades of the hero and TallPointed to face the front, so the broad faces show in the front and hero views.
