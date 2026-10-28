# R06 HardwoodStump goals

Status after revision build 5 (final of this revision): 22 MET, 2 UNMET (V2 must: squat look; 5 should: ridges).
Goals V1-V8 were added from the verifier's failed audit.

## ASSEMBLED / HERO
1. [must] Wide buttress-root flare at the ground (~12-13 studs) clearly wider than the trunk top (~6.1); bbox clearly wider than tall. MET: hero cell shows roots spreading well past the trunk on both sides (13.8 x 12.1 x 6.5 studs).
2. [must] 5 big angular buttress roots, each a faceted wedge sloping from ~3.5-4 up the trunk down to the ground ~6 studs out. MET: hero shows separate angular wedge arms at left, front and front-right, each sloping into the ground.
3. [must] Pale r06_cutwood (#E0B27C) cut face on top, slightly tilted, with 3 stepped concentric rings (geometry only, same colour). MET: hero/top cells show a pale tilted top with stepped ring outlines.
4. [should] Small chip notch on the rear edge of the cut face. MET: notch visible on the rear rim in the hero and front cells.
5. [should] Dark r06_hardbark (#5B3D2E) body with strong vertical facet ridges, large facets. UNMET (partly): triangular facets and some vertical ridges read, but the surface is less chiselled than the reference.
6. [must] 4 leaf tufts (r06_leaf #3F9A2C) between roots: 2 right, 1 front-left, 1 front-centre. MET: hero shows front-left, front-centre and a double tuft on the right (the 2 right tufts sit close together); top cell shows all 4.
7. [should] Trunk tapers upward from a bulged base. MET: trunk visibly widens toward the root collar.

## FRONT
8. [must] Front: trapezoid trunk on a wide root base, roots splaying left and right. MET: front cell shows root arms reaching out on both sides.
9. [should] Front shows a leaf tuft front-centre and tufts at the sides. MET: centre tuft plus left and right tufts.

## SIDE
10. [should] Side: flared silhouette, thin pale top band, roots spreading both sides. MET: side cell shows roots spreading left and right (lighting makes it dark).

## TOP
11. [must] Top: pale ringed cut face in the middle, 5 dark root arms radiating as a star, leaf tufts between arms; no stray line on the face. MET: top cell shows root arms sticking out around the face, 4 green tufts between them and a clean face (the notch groove that caused the line is gone).

## PARTS
12. [must] CutFace: separate thick pale 10-sided slice ~6.3 across, 0.8 thick, rings on top. MET: parts cell.
13. [must] Body: root-flared body, flat lower pale top, no ring slice, ~5.9 tall. MET: parts cell shows the same root arms and a flat top (11.1 x 12.1 x 5.9).
14. [must] Root: single triangular faceted wedge ~4 long x 2.5 tall, dark bark. MET: parts cell wedge.

## DROPS / DEPLETED
15. [must] Chunk: chunky faceted dark chunk ~2 studs with one pale cut face. MET: drops cell.
16. [must] BarkStrip: two flat dark bark strips side by side, ~3 long. MET: two tapered strips of different lengths (2.9 / 2.5).
17. [must] LowStump: ~2.5 tall, ~9-10 wide, flat roots, jagged pale top with a hollow dip, 2 leaf tufts. MET: depleted cell shows a low jagged pale top with a dip, low flat roots, 2 tufts.
18. [should] Drops 1-3 studs, <=300 tris, closed. MET: 32 tris each.

## VFX / tech
19. [must] harvest_hit on the trunk front at mid height with chip colours; harvest_deplete at the base centre; no glint or light. MET: puff visible on the trunk front.
20. [must] 0 problems, within budgets, nothing below z=0. MET: 0 problems; hero 1072/5000.

## Verifier goals (added as must)
- V1 [must] Roots: 4-5 separate angular wedge arms with gaps, 5-6 studs out, sloping into the ground. MET: five convex-hull wedges with visible valleys between them in the hero, front and top cells.
- V2 [must] Squat proportions, footprint ~1.6x height. UNMET (partly): the bbox is 13.8 x 6.5, but the front and hero cells still read a little taller than the reference because the trunk is a tall straight column above the roots.
- V3 [should] Strong vertical facet ridges. UNMET (partly): see 5.
- V4 [must] 4 leaf clumps in the root valleys, bright green. MET: see 6 (fuller tufts: clump core plus broad blades).
- V5 [must] Front and side show a flared silhouette with roots spreading to both sides. MET: front and side cells show the root arms.
- V6 [must] Top: 5-arm star with leaves between arms, no stray line. MET: see 11.
- V7 [should] Body part flare as in the hero. MET: same roots as the hero.
- V8 [must] The root flare is the dominant read, with tufts nestled between roots. MET: the roots now read as buttress arms, with tufts in the valleys.

## Iteration log
1-4. (earlier run) Lofted skirt trunk; roots read as a skirt. Verifier failed: 4/10.
5. Rev build 1: rebuilt the hero as a faceted triangulated trunk plus 5 two-segment hull root wedges; leaves use a leaf_cluster core plus blades; flat cut plane (fixed the notch groove that drew the stray line). Roots were too small under a wide trunk.
6. Rev build 2: narrowed the trunk (r 3.45 to 3.2) and enlarged the roots (4.2 up, 1.75 half-width). Roots read as arms.
7. Rev build 3: re-spread the roots (30/115/170/240/305) and moved the leaves into the right, front-left and front-centre valleys; lowered the top to 6.3; the low stump got smaller-trunk roots.
8. Rev build 4: lowered the depleted roots (they had poked through the dip as dark spots) and moved the second right tuft forward.
9. Rev build 5: bulged the trunk base (r 4.3) and widened the roots (2.0 half-width, 6.5 reach), with bigger tufts. A small gain; the build cap was reached.
