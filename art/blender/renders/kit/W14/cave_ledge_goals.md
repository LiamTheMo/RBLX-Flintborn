# W14 row 4 CaveLedge goals (revision 2, after verifier fail 4/10)

Status is judged by eye against the reference row after the final build (build 4 of this revision).

## ASSEMBLED / HERO
1. [must] Hero reads as a wide flat ledge, ~32 wide x ~16 tall (about 2:1), deck top at z~9. MET: the 34.6 x 16.7 hero reads as a wide, flat ledge.
2. [must] Deck top is 4-6 large flat sand plates with visible seams; the seams are not radial. MET: 4 large plates with dark seams are clear in the hero and top views.
3. [must] A band of chunky, chipped rock (w14_rock) edge blocks runs round the deck rim, top roughly flush with the deck. MET: blocky rim band in the hero, front and top views.
4. [must] (verifier) The deck is a wide, thick, pale tan slab on a bulky mass of rock. UNMET: the rim band is thick, but from the iso the rock mass under it hardly shows, so the deck still looks low on a ring of rock.
5. [must] (verifier) A strongly undercut, deep, jagged underside of stacked and hanging angular chunks, recessed ~3 studs, as the main volume under the deck. UNMET: there are three tiers of chunks plus a core (front view shows them), but in the iso they read as a dark strip, not the reference's big hanging mass.
6. [must] (verifier) Back wall of 3-5 tall angular rocks, highest at the left (~16), with the wall mass running down to the ground at the left end. MET: faceted prism rocks with chipped crowns run along the back and the back-left. The left ones are tallest (16.4) and reach the ground.
7. [should] A lower boulder pair (~7 tall) at the front-left base. MET: two angular boulders sit at the front-left in the hero and side views.
8. [should] Tiny moss tufts (w14_moss) at the back of the deck, with rubble and grass tufts at the base. MET: moss at the back of the deck, grass and rubble at the base.
9. [must] Rock renders warm grey-mauve (single key w14_rock #8C7F7A), not chalky or blue. MET: warm grey-mauve in every cell.
10. [must] (verifier) Sand base colour (w14_sand) is pale pinkish tan, judged on the mid-tone. MET (closer): with #C8A88C it renders pale peach-tan, no longer orange. It is still slightly warmer than the reference.

## FRONT
11. [must] (verifier) Front view: a wide deck band, a jagged crown of wall rocks behind it, and an inverted-trapezoid underside of big chunks. UNMET: the band and crown match, and the chunk band below is now visible, but it is close to rectangular, not a tapering trapezoid.

## SIDE
12. [must] (verifier) Side view: a tall wall mass from floor to top on the same side as the reference (left), with the deck cantilevered out to the right. MET: with SIDE_AZIMUTH -90 the tall wall mass is on the left and the deck projects right over the boulders. The hanging chunks there are small.

## TOP
13. [must] Top view: an irregular rounded, chipped outline, a sand interior with seams, rock rim blocks all round, and bigger wall rocks at the back and left. MET: an irregular oval with rim blocks, and wall rocks at the back and left.

## PARTS
14. [must] (verifier) CaveLedgeBackWallPanel is a merged cluster of 4-6 tall angular rocks, ~20x5x14, left tallest. UNMET: 6 overlapping angular rocks (21.5 x 6.9 x 13.6, left tallest), but in the parts cell it still reads partly as a row of posts.
15. [must] CaveLedgePlatformSlab: a flat slab ~24x16x3 with a sand plate top, seams and rock edges/underside. MET: a 25.8 x 18.5 x 3.4 slab with plates and a rock rim.
16. [should] (verifier) CaveLedgeCornerFiller is a blocky 2-rock block ~7x7x9; CaveLedgeCornerFillerSmall is an angled cluster ~5x5x6. MET: the filler is now two blocky chipped slabs (8.2 x 7.6 x 9.9), and Small is an angled 2-rock cluster.

## VARIATIONS
17. [must] (verifier) A. Wall Ledge: a smaller deck with higher back and side walls, reading as one attached chunk with rock mass under the deck. MET: built like the hero (undercut mass and a merged angular wall), with the deck at 7.5 and the wall up to 16.
18. [must] (verifier) B. Natural Span: a rock arch with a clear rounded opening ~14x7-8, boulder piers, a flat top ~8 wide at z~10, about 32 long. MET: 11 voussoirs make a visible curved opening (~12.4 wide x 6.8 tall) between chunky piers, under a flat sand top at 10.8. Length is 32.0. The opening is lumpier than the reference's.
19. [must] C. Pit Rim: a closed ring of stacked slabs, outer ~32, ~8 tall, open centre with no floor. MET: a 32 x 8.2 closed ring with an open centre.
20. [should] Budgets: hero <= 7000, variants <= 6000, parts within budget, 0 problems. MET: the hero is 2713 tris, variants 930-2033, 0 problems.

## Iteration log (revision 2)
- R2 build 1: sand set to #C8A88C, SIDE_AZIMUTH -90, deck thickened, cones replaced by 3 tiers of rock() chunks plus a core, new prism-and-block pillars, block corner filler, real voussoir arch. Sand fixed. The voussoirs were hidden behind the piers and deck, and the box crowns read as cubes.
- R2 build 2: pillars became 2 tall prisms with slanted tops, and the tier-1 chunks moved flush to the edge (subdiv 2). The front underside improved, but the pillars read as thin basalt posts.
- R2 build 3: pillars now have a wide prism body plus an icosahedral angular crown, so the wall reads as angular rocks. Span voussoirs became centred icos with no rim over the arch, the top was raised to 10.8, and the front-left wall was trimmed so the side view shows the deck.
- R2 build 4: smaller arch (A 6.2, B 6.8, 11 voussoirs) with spandrels, so the arch curve is now visible. Shorter tier-1 chunks. The back wall panel is 6 overlapping rocks. Stopped at the 4-build cap.
- Still open: the hero underside does not read as the dominant mass in the iso (goals 4, 5, 11), and the BackWallPanel is still slightly post-like (goal 14).
