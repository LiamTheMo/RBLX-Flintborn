# W09 StonePath goals (row 1) - revision 2 (after verifier fail, resemblance 5/10)

Status legend: [ ] pending, MET / UNMET after each build. Verifier goals added as musts (V*).

## ASSEMBLED / HERO
1. (must) Low flat flagstone slab ~16 x 24 x ~1.6 studs (greenery to ~3.5); much wider/longer than tall. MET - low flat slab, pavers ~1.6 high on 16x24 bed, greenery to ~3.3
2. (must, V) 9-11 irregular 5-7 sided pavers in an organic jigsaw, varied sizes (4-6 studs) and angles, uneven rows - NOT a 2-column brick grid. MET - top view shows 11 irregular rounded 5-7 sided pavers in uneven rows (3/2/3/2 pattern), no brick grid
3. (must, V) Thin dark soil seams between every paver; pavers fill the footprint; soil only a THIN (~0.5) rim/skirt lower than the pavers. MET - dark seams between all pavers; pavers now fill the footprint, brown skirt is a thin 0.45 band
4. (should, V) Paver tops softly faceted (several tilted facets + chamfer) with a visible faceted side band ~1 stud tall. MET - pavers show several tilted top facets, chamfer ring and a faceted side band in hero/parts
5. (must, V) Greenery only at edges and corners: 7-9 bushy tufts of 5-8 bright wide pointed blades (1.5-2.5 tall), densest at the 4 corners; walking middle clear. MET - 9 tufts of 10-13 wide blades on turf mounds, big clusters at all 4 corners, both long edges green, middle clear; still a little less lush than ref
6. (should) 5-6 white daisies with yellow centres in the tufts. MET - 6 small white daisies visible in the edge tufts (smaller than ref)
7. (should) 3 small cool-grey rocks (0.8-1.4 studs) at edges/corners. UNMET - rocks sit too low and are mostly hidden behind pavers/tufts in hero (grey only at back corner)

## FRONT / SIDE
8. (must) Front/side: chunky low profile; paver side band dominates, thin brown skirt below; tufts poke up at both ends. MET - front/side show thick paver band with thin brown skirt and tufts at both ends
9. (should) Side view shows the long run with tufts at both ends and along the edge. MET - side view: long run with tufts at both ends and along the edge

## TOP
10. (must) Top view: portrait ~1.5:1 rectangle filled by irregular big rounded polygons, green clumps along both long sides and corners, grey rocks at edges. MET - portrait rectangle of big irregular polygons, green clumps along both long sides and corners; rocks hard to see

## PARTS
11. (must) StonePaverA chunky 6-sided ~5 x 4.5 x 1.1, flat faceted top, bevelled, faceted sides. MET - PaverA chunky hexagon with faceted top and bevel
12. (must) StonePaverB 7-sided rounder with a notched corner; StonePaverC 5-sided longer ~5.5 x 4. MET - PaverB rounder with notch, PaverC longer 5-sided
13. (should, V) Part pavers ~100-200 tris each with 2-3 tilted top facets + faceted side walls. MET - 78-142 tris each with off-centre apex facets and faceted waist band
14. (must, V) StonePathGrassEdgeStrip: taller brown soil block, wavy overhanging grass cap ~0.5 thick, 3 tall wide leaf tufts, 2 daisies, grey rock at right end, clearly stepped ends. MET (partial) - wavy drip-edged overhanging cap, 3 tall wide tufts, 2 daisies, grey rock at right end; the stepped ends exist (0.35 high steps 1.7 long) but read only faintly at cell size

## VARIATIONS
15. (must) StonePathStraight: narrow 8 x 24 run of 7-8 pavers filling the footprint, tufts and daisies along both edges. MET - 8 pavers fill an 8 wide run, tufts and daisies on both edges
16. (must, V) StonePathCurved: smooth S-bend of ~10 pavers bending left then right, width 8, soil trimmed to the path outline, tufts on edges. MET - clear S-bend (left then right) of 10 pavers, width 8, soil trimmed to the path outline, tufts on edges
17. (must, V) StonePathJunction: 24 x 24 square fully paved with ~11 larger pavers radiating from a central paver; tufts at the 4 corners, rocks at 2 corners; NO flat grass squares. MET - fully paved square of 11 pavers around a centre stone, corner tufts, rocks at 2 corners, no flat grass squares

## PALETTE (one base colour each)
18. (must, V) Pavers warm sand-tan w09_paver (#D8B488 shared key), render matching ref tan, not pale/peach. UNMET - pavers still render peachier/more orange than the ref's beige tan; w09_paver is the shared sheet key copied verbatim (sheet-level issue, see shared_lib_requests)
19. (must) Leaf blades w09_foliage #3F9A2C, turf w09_grass #5FA52A, bright saturated, not olive. MET - blades and turf bright saturated green
20. (should) Soil w09_soil warm brown seams/skirt; rocks w09_boulder cool grey; petals white, centres yellow. MET - soil warm brown, rocks cool grey, petals white, centres yellow

## SCALE
21. (should) Paver thickness ~1.1, path height ~1.6 (below a 5.5-stud character's knee); hero 16 x 24 snaps to 8-stud grid. MET - pavers 1.1 thick, path 1.6 high, 16x24 footprint

## Iteration log (revision 1: builds 1-4 produced the failed version)
1-4 (rev 1). Voronoi pavers in a 2-column grid on a thick 0.95 soil bed; verifier failed (grid, thick soil, sparse tufts, wedge curve, grass squares).
5 (rev 2 build 1). Rewrote: irregular 11-seed jigsaw, soil bed 0.45, pavers 1.1 with faceted waist/apex top; wavy-cap strip with stepped ends; sine S-curve; fully paved junction. Jigsaw and soil fixed; greenery still small.
6 (build 2). Tufts +3 blades, mounds 1.8/1.3, wider blades, extra edge tufts; S amplitude 4.4. Junction over budget -> mid-side tufts replaced by turf. Greenery now reads bushy; S clear.
7 (build 3/4). Daisies 1.2, rocks x1.25, deeper strip steps, bigger strip rock. Rocks still placed too low in the hero (hidden) - next fix would raise rock z to SOIL_TOP + 0.35*size; 4-build limit reached.
Note 18: w09_paver #D8B488 is shared and copied verbatim; a deeper, less orange tan (~#CDAE88) would match the reference better.
