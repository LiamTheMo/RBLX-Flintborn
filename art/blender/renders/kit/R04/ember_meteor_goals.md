# R04 EmberMeteor goals

Reference: art/reference/kit/rows/R04_row2.png. Status after the latest build (revision build 4) in [brackets]. Goals V1-V6 were added from the verifier's failed audit.

## ASSEMBLED / HERO
1. (must) Bright orange faceted core is the focal point, bulging forward between dark slabs, ~35-45% of the silhouette width in iso. [MET - large orange core fills the centre of the iso cell and bulges forward between the slabs.]
2. (must) 3-4 tall dark angular slabs wrap the core on the left, back-right and front-right, plus a small left-front slab, and lean outward like opened petals. [MET - four angular slabs (left, back-right, front-right, small left-front), each tilted about 12-15 degrees outward. They read as petals around the core, though they lean less than in the reference.]
3. (must, V1) The silhouette is peaked and craggy and tallest at the back-right, about 7.5 studs. It reads as one crag, with a large slab mass on the left. [MET - angular, chopped-top slabs give a peaked crag silhouette. The back-right slab is the highest point and the hero is 7.5 studs. The left slab is now a big mass of about 4 x 4 x 7. The silhouette is still slightly more open than the reference's tight mass.]
4. (must, V3) 3-4 thin glowing seams (~0.2-0.3 wide) run along the slab edges and faces and read as cracks in the rock, not floating sticks. [UNMET - there are 4 seams, and they now follow the slabs' own mesh edges, offset 0.06, so they sit on the rock. But each is only 1-2 short straight segments. The reference shows longer zig-zag cracks, so they still read more as glowing edge lines than as cracks.]
5. (must) A ring of 8-10 low, warm grey-tan rubble rocks circles the base, the largest at the front-right (~3 x 2.5 x 2.5). [MET - 10 grey-tan rocks circle the base, and the big one is at the front-right.]
6. (must) Hero is ~9 x 8 x 7.5 studs, slightly wider than tall. [MET - 9.5 x 8.5 x 7.5 studs; it reads wider than tall.]
7. (should, V2) Slabs show large flat crisp facets, about 6-12 per slab, with no smoothing. [MET - the slabs are icosahedra with chopped tips and render as crisp polygonal planes. They are no longer ovals.]

## FRONT
8. (must) Front view shows the core as an orange band in the middle (~1/3 of the width), slabs left and right, and a rubble row across the bottom. [MET - the front cell matches this layout. The core band is a little wider than in the reference.]
9. (should) Seams show on the front as thin bright lines on the slab edges beside the core. [MET - two thin lines are visible on the edges of the left and right slabs beside the core.]

## SIDE
10. (should, V5) Slabs cover most of the side profile, the orange core shows on one side as in the reference (right), and rubble sits at the base. [MET - with SIDE_AZIMUTH -90 the core shows on the right beside the tall dark slabs, with rubble at the base, as in the reference.]

## TOP
11. (must) Top view shows the orange core in the middle, dark slabs around it on 3 sides, and rubble at the rim. [MET - the top cell shows orange in the centre, with slabs around 3 sides and rubble at the rim.]

## PARTS
12. (must) EmberMeteorShellPiece is one tall angular charcoal slab ~4 x 3 x 5 with one glowing seam. [MET - an angular slab of 3.6 x 3.0 x 4.3 with one zig-zag seam on its face. It is slightly short of the 5-stud target.]
13. (should, V6) The shell part shows a lighter mid-tone with visible planes. [UNMET - the planes are now visible, but the colour is near-black. The fixed sheet key #2E2E36 is the cause; see goal 18.]
14. (should) EmberMeteorShellPieceB is a flatter angular slab ~5 x 2.5 x 3. [MET - a flat angular slab of 4.6 x 2.5 x 2.6.]
15. (must) EmberMeteorCore is a faceted orange core ~4.5 x 4 x 4.5, with flat facets, and is emissive. [MET - an orange core of 4.4 x 3.9 x 4.3. Facet edges are visible but soft under the emission.]
16. (must) EmberMeteorImpactBase is 6-7 grey-tan rocks of 0.6-3 studs on a ~7 x 3 x 1.8 footprint. [MET - 7 rocks on 6.9 x 3.1 x 1.8.]

## DROPS / DEPLETED
17. (must) CooledEmberFragment (~1.2 x 1 x 1.3) and CooledEmberFragmentB (~1 x 0.9 x 1.4) are chunky faceted shards in dull burnt orange-red, with no glow. [MET - two faceted red-orange shards, 1.2 x 0.9 x 1.2 and 1.0 x 1.0 x 1.3, with no glow.]
18b. (must) EmberMeteorDepleted is 7-9 grey-tan rocks in a low loose pile ~8 x 6 x 2, with no slab and no orange. [MET - 8 rocks, 8.1 x 5.3 x 1.7.]

## PALETTE
18. (must, V4) The charcoal slabs render with a mid-tone of about #46464E, and their light and dark facets come only from lighting. [UNMET - IMPOSSIBLE WITHIN THE CONVENTIONS. The shared sheet key r04_meteor_rock #2E2E36 must be copied verbatim and renders near-black. Tint is a linear multiply that would need about 2.3x, against a 1.25 limit, and it must not stand in for colour. The sheet owner needs to change r04_meteor_rock to about #44444C, which is listed in shared_lib_requests.]
19. (must) r04_ember_core #E8501A is emissive on the core only and visibly redder than the r04_lava_crack #FF9A1E yellow seams. [MET - the core renders red-orange and the seams render yellow-orange.]
20. (must) r04_impact_rock #7D7570 is on the rubble and r04_cooled_ember #A8401F is on the drops only. [MET - the rubble is warm grey-tan and the drops are burnt orange-red.]

## VFX
21. (must) The node has heat_glow (scale 1.5, #FF6A10/#FFB030, orange PointLight) at the core, embers above it, a small heat_glow on each seam, harvest_hit at (0,-4,3) and harvest_deplete at (0,0,0.8), and no ore_glint. [MET - all of these sockets are present.]

## Iteration log
- Builds 1-4 (first pass): rock() slabs at subdiv 2 came out as blobby ovals, the seams were straight sticks, and the result FAILED verification.
- Revision build 1: slabs became icosahedra (subdiv 1, crisp planes), seams walked the mesh edges and SIDE_AZIMUTH was set to -90. The facets were crisp but too spiky and the seams too thick. The side view became correct.
- Revision build 2: subdiv 2 + facets 19 made the slabs rounded again. Tint 1.4 had almost no visible effect, because it is a linear multiply.
- Revision build 3: back to subdiv 1 with the tips chopped at 93%, which gave chunky crags. Tint went back to 1.0, the seams were made thinner and the core facets bigger. The back slab was raised and the hero reached 7.5.
- Revision build 4: the left slab was enlarged to about 4x4x7, the front-right slab grew, and a second seam was added on the left slab. Seam paths were densified and allowed sideways steps. Build limit reached; the seams are still short (goal 4).
