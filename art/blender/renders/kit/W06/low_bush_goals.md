# W06 row 1 - Low Bush: visual goals

Reference: `art/reference/kit/rows/W06_row1.png`. Build: `art/blender/renders/kit/W06/low_bush_compare.png`.
Status: revision 7 (verifier round 2), after build 4. Runner: 0 problems. Stats/KITSTAT: hero 3223/4000 tris, 6.4 x 6.4 x 4.5 studs; Dome 2823 (6.1 x 6.1 x 4.0), Hedge 3354 (8.7 x 4.2 x 3.5), Woody 2077 (7.6 x 4.6 x 4.9) of 3500; clump parts ~78 tris.
I judged each goal by eye against the reference cell directly above it. Numbers only support that judgement.

## REWORK (verifier) - must
W1. [must] Crowns and clumps use only Asset.canopy / Asset.leaf_cluster. - MET: every crown is canopy, and the parts and hand-placed clumps are leaf_cluster.
W2. [must] ONE palette key per material, no shade variants, Tint within +/-10%. - MET: leaf, bark, stone, moss, soil, petal, pollen and berry each have one key. Tint is +/-4% random, and the runner reports no shade pairs.
W3. [must] No water, vapour or smoke meshes. - MET: there are none. The only sockets are harvest_hit.
W4. [must] Use the sheet keys for the flowers and berries (w06_petal, w06_pollen, w06_berry). - MET: they replace flower_white, flower_yellow and berry.
W5. [must] Hero spec ~6 x 6 x 4.5. - MET: stats file 6.4 x 6.4 x 4.5 (build 4).
W6. [must] Hedge spec ~8 x 4 x 3.2 with clumps in a row and few flowers. - MET: 8.7 x 4.2 x 3.5, three rows of distinct clumps forming one continuous hedge, 3 flowers.

## VERIFIER REVISION (round 2) - from the failed audit
V1. [must] Hero: dome of chunky, rounded multi-lobed star clumps, big (~15-20 visible across the face), not small shards. - MET: the crown is now ~20 separate big leaf_cluster stars (r 1.0-1.25) in stepped rings; 12-15 distinct clumps are readable across the hero face with dark notches between them. Lobes are still a little pointier than the sheet's.
V2. [must] Hero proportions ~6 x 6 x 4.5 studs (stats file), wider than tall, reaching the ground. - MET: stats show 6.4 x 6.4 x 4.5 (Y includes the front rocks); the dome is wider than tall and its skirt ring reaches the rocks.
V3. [must] Hero silhouette and clump scale match the reference ASSEMBLED cell: big chunky lumps, strongly stepped outline. - MET: the hero outline steps clump by clump like the ASSEMBLED cell, with the forked trunk in the front window; no longer a fine jagged shell.
V4. [should] Leaf mass shows deep green recesses and lime lit tops through clump overlap and stepping (one leaf key). - UNMET (should): the side cell shows deep-green recesses, but the front/iso face still reads more uniformly bright than the sheet's lime tops.
V5. [should] Hero/Dome front rocks are big flat slabs ~1.6-2 studs wide. - MET: two flat grey slabs ~2 studs wide sit in front of the hero; Dome front rocks enlarged to ~1.3-1.5.
V6. [should] OpenWoody trunk visibly thick (~25% thicker than before) and the 4 limbs spread wide with larger tip clump groups. - MET: trunk radius +25%, limbs spread 1.3x in X, each tip carries a group of 4 distinct clumps.
V7. [should] Module notes quote the real hero dimensions. - MET: notes now say ~6 x 6 x 4.5.

## ASSEMBLED / HERO
1. [must] A rounded dome clearly wider than tall (~1.4x) that reaches near the ground. - MET: the final hero cell is a broad dome with its rim down near the rocks. The previous build was mushroom-shaped and that is fixed.
2. [must] Dense mass of big chunky faceted clumps; the outline is lumpy, not a clean hemisphere. - MET: big separate star clumps over a core; outline steps clump by clump.
3. [must] A brown forked trunk shows in the lower front gap. - MET: the thick brown trunk and roots are visible under the canopy at the front centre.
4. [must] 5-8 white five-petal flowers with yellow centres over the outer clumps. - MET: about 7 flowers over the front and top.
5. [must] Grey rocks at the foot: two flat ones in front plus one to the side. - MET: two big flat front slabs plus a side rock.
6. [should] 4-7 small lime moss tufts round the base. - MET: about 6 tufts.
7. [should] Soil only as a small dark patch under the trunk. - MET.
8. [must] Foliage is saturated green, not olive. - MET: w06_bushleaf #54A006 renders vivid green; lime-to-deep contrast is weaker than the sheet (see V4).

## FRONT / SIDE / TOP
9. [must] FRONT: the dome is ~1.5x wider than tall, with the trunk in the lower centre, rocks each side and flowers on the face. - MET.
10. [must] SIDE: one dense dome reaching the ground, with no waist or seam. - MET: one continuous mass. The back is in shadow, as on the sheet.
11. [must] TOP: a round crown of clumps with flowers on the rim and no trunk visible. - MET.

## PARTS
12. [must] LeafClumpLarge / Medium / Small are lobed star clumps about 2.4 / 1.8 / 1.2 across. - MET.
13. [must] BranchStem is a brown Y-fork with flat cut ends plus a short second stem. - MET.
14. [should] BushBerries: ~5 red berries (w06_berry) on a tiny stalk. - MET.
15. [should] BushFlower: a white flower with a yellow centre. - MET.

## VARIATIONS
16. [must] A. DomeBush: a closed round compact dome down to the ground with ~5 flowers. - MET.
17. [must] B. HedgeBush: wider and flatter (~8 x 4 x 3.2), clumps in a row, a level top and few flowers. - MET (see W6).
18. [must] C. OpenWoodyBush: a thick brown trunk with 3-4 forked branches carrying separate leaf groups on top, airy. - MET: a thick trunk with 4 limbs and separated clump groups. Its top is a little less spread than the sheet's.

## PALETTE / SCALE / TECH / VFX
19. [must] Leaves w06_bushleaf #54A006, bark w06_bark #8D6237, stone w06_stone #B1ADA9, moss w06_moss #ACC722, soil w06_soil #6E4B2B. - MET.
20. [must] A leaf-green harvest_hit socket on the hero and on each variant; no other VFX. - MET.
21. [must] One mesh per asset, origin at the bottom centre, nothing below z=0, within budget, 0 problems. - MET.

## Iteration log (revision 6)
1. Added w06_berry, w06_petal and w06_pollen. Hero canopy narrowed to 5.6 with 20 facets=2 clumps and the skirt pulled in. Hedge spacing tightened to 8 wide; Woody trunk thicker with bigger tip masses. Result: over budget (4467).
2. Cut to 17 and then 16 clumps, and the ring to 5. Result: 0 problems, but the hero was mushroom-shaped (high canopy with a waist) and taller-looking than wide.
3. Canopy made wider and lower (6.0 x 5.4 x 3.9, flat_bottom 0.65). Result: still a waist, and only a few flowers showed.
4. Canopy 6.2 x 5.6 x 4.1 at z 2.05 with flat_bottom 0.8 (it reaches the ground), ring reduced to front flanks plus back, and 8 flower rays aimed higher. Result: a broad dome to the ground, ~7 flowers, trunk gap kept. Final.
Open issue: the canopy clumps read slightly shard-like compared with the sheet's rounded star clumps. That shape comes from the shared helper.

## Iteration log (revision 7, verifier round 2)
1. Canopy helper with fewer, bigger clumps, depth 0.55, raised to z 2.35. Result: 5.9 x 6.4 x 4.5 but clumps merged into a smooth blob - worse.
2. Replaced every crown with hand-placed leaf_cluster rings on an ellipsoid shell (Bush.shell) over a low-poly leaf core; Woody tips became clump groups. Result: separate clumps, trunk visible, but hero looked tall/egg-shaped (5.7 x 4.2).
3. Clumps pushed out along the shell normal (stepping and dark recesses), shell widened and lowered, hedge segments tightened. Result: lumpy stepped dome 6.7 x 4.5.
4. Hero width trimmed to 6.4, shallower lobes (depth 0.6), Woody tips 4 smaller rounder clumps. Final: 0 problems, hero 6.4 x 6.4 x 4.5.
Open: clump lobes still a bit pointier than the sheet's rounded stars (shape of the shared leaf_cluster); lit tops less lime than the sheet.
