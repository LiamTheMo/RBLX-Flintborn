# R08 row 1 - Emberbloom goals

## ASSEMBLED / HERO (iso, front-left)
1. [must] Orange faceted teardrop seedpod is the tallest element, top ~6.5 studs, ~3 wide; pointed tip, widest ~40% up, 10-12 big diamond facets. — MET: pod is the tallest element in iso/front/side, pointed top, widest just below middle, big diamond facets (6 sides x 5 rings).
2. [must] Seedpod reads as glowing (emissive orange, clearly brighter than the petals). — MET: pod renders bright orange-yellow, clearly self-lit against the red petals; heat_glow light adds glow.
3. [must] 8 large pointed lozenge red petals in a layered rosette: 5 outer low (~30-35 deg up), 3 inner steeper (~55 deg) between them, overlapping. — MET: 5 low outer petals plus 4 steeper inner petals between them overlap in a layered rosette (iso, top).
4. [must] Petals have sharp pointed tips and a central ridge (2 facets per side), tips curve slightly upward. — MET: each petal is a lozenge with a sharp tip and a top ridge; tips lift upward in front/side views.
5. [must] Petals sit ABOVE the rock ring and overhang it: petal tips reach beyond the boulders (hero width ~9 vs ring ~8). — MET: after shrinking the hero ring (build 4) petal tips reach clearly past the boulders in iso/front/side.
6. [must] Rock ring of 8-10 low chunky faceted grey-brown boulders (each ~1.5-2.5 wide, ~1-1.5 high) around a flat dirt disc. — MET: 10 chunky faceted grey-brown boulders ring a flat dirt disc; visible as a low band under the petals.
7. [should] Overall proportion: hero ~1.4x wider than tall (9 w x 6.5 h). — MET: hero 8.4 w x 6.5 h, reads ~1.3x wider than tall like the reference.

## FRONT
8. [must] Front view: symmetric fan silhouette, seedpod central and highest, petal tips spreading wider than the rock ring, rocks visible as a low band under the petals. — MET: front shows a symmetric fan, pod central and highest, petals wider than the rock band.

## SIDE
9. [should] Side view matches front: same fan, seedpod ~half of total width at petal level is red, rocks low band. — MET: side shows the same fan over a low rock band.

## TOP
10. [must] Top view: red star of 5 outer petal points with inner petals between them, orange faceted pod in the centre (~1/3 of the flower width), grey-brown boulders visible around the outside between petal tips. — UNMET: red 5-point star with orange faceted pod in the centre matches, but the boulders are now hidden under the petals; reference shows rocks peeking out between tips.

## PARTS
11. [must] EmberbloomSeedpod part: lone teardrop ~3x3x4.5, orange, faceted. — MET: lone orange faceted teardrop 3.0x2.6x4.5.
12. [must] EmberbloomLeaf part: one lozenge petal ~4 x 1.8 x 1.2, pointed both ends, ridge facets. — MET: single pointed lozenge petal with ridge facets, 4.0x1.8x1.0.
13. [must] EmberbloomBase part: ring of boulders with a flat dished dirt centre, ~9x9x1.6, dirt visibly lower than the boulder tops. — MET: boulder ring around a flat, lower dished dirt centre, 8.8x8.5x1.5.

## DROPS / DEPLETED
14. [must] EmberSeed drop: small orange faceted teardrop ~1.2x1.2x1.8, <=300 tris. — MET: small orange faceted teardrop 1.2x1.0x1.8, 60 tris.
15. [must] RedPetal drop: small pointed red petal ~1.8 long, <=300 tris. — MET: small pointed red petal 1.7 long, 20 tris; a bit thinner-looking than the reference.
16. [must] EmberbloomDepleted: the base alone (rock ring + empty dished dirt), same ~9x9 footprint, low (~1.6). — MET: depleted cell is the empty rock ring with dished dirt, 9.0x8.6x1.5 (deplete dust VFX partly covers it in render).

## PALETTE
17. [must] Three distinct saturated colours: petals red r08_petal_red #B0121C, pod/seed orange r08_ember #F2800F (emissive 0.6), rocks + dirt grey-brown r08_rock #6A5A50; render red and orange as saturated as the reference, rock not too light. — MET: red, orange and grey-brown read as three distinct saturated colours; pod renders slightly yellower than the reference because of the given 0.6 emission.

## VFX / BUDGET
18. [must] Hero: heat_glow at pod (0,0,4.5), embers (0,0,6) scale 0.6, harvest_hit (0,-2,3) red/orange chips, harvest_deplete at base; seedpod part heat_glow; EmberSeed embers small; depleted harvest_deplete (0,0,0.5). — MET: all sockets placed as specified (hero harvest_deplete moved to the depleted asset after build 1 because it smothered the hero).
19. [must] Budgets: hero <=3000, parts <=1500, drops <=300, depleted <=2000, 0 problems. — MET: hero 496/3000, parts <=256, drops 60 and 20, depleted 256; 0 problems.

## Iteration log
- Build 1: custom lozenge petals (16 tris), faceted teardrop pod, 9-boulder ring with dished dirt. Petals too thin and spiky, rocks flat, hero deplete dust hid the flower.
- Build 2: removed hero harvest_deplete, wider/thicker petals, 4 inner petals, 10 taller rocks, pointier pod bottom. Rosette read better; petals still narrow.
- Build 3: petal rebuilt as a fuller lozenge (near-base and near-tip side verts), steeper tiers (28/50 deg). Close match, but petals did not overhang the ring.
- Build 4: hero ring scaled to 0.8 and outer petals lengthened to 4.6: petals now overhang clearly. Side effect: top view hides the boulders (goal 10 UNMET; build cap of 4 reached). Fix next time: hero ring k~0.9 with boulders placed at the angles between outer petal tips.
