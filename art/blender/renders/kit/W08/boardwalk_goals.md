# W08 Boardwalk goals (revision 2)

Reference: art/reference/kit/rows/W08_row3.png. The reference FRONT cell draws the long side and its SIDE cell the end, while its TOP cell draws the length vertically. The runner's FRONT camera is fixed at azimuth 0, so the hero and all variants are now built with the length along X (stairs at -X). FRONT then shows the long side and SIDE (az 90) shows the end, matching the reference. The cost is that TOP shows the strip horizontally, not vertically (documented deviation). The deck was raised from 1.6 to 1.9 so the legs below the thick band read with the reference's proportions (legs ~25% of the height).

## ASSEMBLED / HERO
1. [must] Long, low walkway: ~15 x ~6.5 studs (12 of deck + 3 of stairs), deck top ~1.9, post tops ~4.3, length >2x width. -- MET: the hero reads as a long railed deck running across the cell; 15.0 x 6.5 x 4.4.
2. [must] (verifier) The deck is ~20 chunky across-width planks with visible seams, and reads as a thick slab with a fat stacked-timber edge band. -- MET: the hero (elevation 36) shows separate planks with dark gaps across the deck top; the long edge shows plank ends stacked on a thick stringer (band 0.95 of the 1.9 height).
3. [must] Double-rail fence on each side: tall square posts (4 per side) above a top rail, plus a mid rail. -- MET: hero and front cells show 4 chunky posts with a top and a mid rail on each side.
4. [must] 3-step plank staircase at one end, 4 wide, steps made of planks, at the left of the hero like the reference. -- MET: 3 stacked plank steps at the left end of the hero with side stringers and foot posts.
5. [must] (verifier) Support legs under the deck (3 pairs) with crossbeams; open space under the deck. -- MET: legs with gaps under the band are visible in the hero and front cells.
6. [should] Thin tan rope lines on the deck top plus a short rope run beside the stairs. -- MET: two tan lines run along the deck centre and a rope sags from the rail post to the stair foot post.
7. [should] Brass nail heads visible on the post joints at hero scale. -- MET: enlarged (1.5x) brass dots show on post tops, rail joints and stringer/leg joints in the hero and front cells.

## FRONT
8. [should] (verifier) FRONT shows the long side as in the reference: tall posts with the double rail across, thick deck band with nails, legs below. -- MET: the front cell now shows the long side with 4 posts, two rails, plank-end band and legs; the stairs sit at the left end.

## SIDE
9. [must] (verifier) Support legs with bold diagonal brace pairs and a heavy deck band visible from the side. -- MET: the hero and front cells show V-shaped brace pairs (0.32 x 0.36 beams, ~35 degrees) between the legs under a thick band; the end view shows an A-frame brace pair between the leg pair.
10. [should] SIDE shows the end view: two post groups with rails, the deck slab and legs, like the reference SIDE cell. -- MET: the side cell shows the end with the posts on both sides, rails running back and legs/braces under the deck (framed close by the runner).

## TOP
11. [should] Top view: a long narrow strip with cross planks, posts along both edges and stairs at one end. -- MET with a deviation: the strip is horizontal (stairs at left) rather than vertical, because the length now runs along X to make FRONT match.

## PARTS
12. [must] (verifier) The parts cell shows all six items readable: RailPost, Rail, FloorPlank, SupportPost, Stairs, Crossbeam. -- MET: the stairs read as 3 stacked plank steps at the back and the five beams/posts lie in front of them, none hidden. The posts are authored lying along X so the runner's footprint sort no longer puts two tall posts in front of everything.
13. [should] (verifier) The Stairs part has 3 distinct plank treads with side stringers, 1.6 tall. -- MET: three treads (0.5 thick) visible at the back of the parts cell; size 4.3 x 3.0 x 1.6.
14. [should] The parts cell mirrors the reference's exploded arrangement with standing posts. -- UNMET: the runner's grid layout is fixed, and the posts lie flat to stay readable (shared_lib request filed).

## VARIATIONS
15. [must] A. Straight: ~8-stud section with rails on both sides, no stairs, 4 support pairs. -- MET: variant 1 shows a short railed deck on legs with braces.
16. [must] B. Corner (L): L-shaped 6x6 deck with 4-wide arms, rails only on the two outer edges, larger corner post. -- MET: variant 2 shows the L deck, rails on the two far edges and a bigger corner post.
17. [must] C. Ramp End: deck sloping to the ground at ~25 degrees with cleats, a handrail on one side following the slope with a rope strand. -- MET: variant 3 shows the cleated ramp at the front left, the sloped handrail and the rope.

## PROPORTIONS / PALETTE / SCALE
18. [should] (verifier) Chunky timbers: rail posts 0.65 square, top rail 0.4 x 0.5, support legs 0.75, stout toy-like silhouette. -- MET: posts and rails read blocky in the hero and front cells.
19. [must] All timber is one orange-brown (w08_wood #A8582A, the sheet palette value) rendering warm orange on lit faces and red-brown in shadow. -- MET: one timber colour everywhere; it reads slightly redder than the reference, but the shared sheet palette can't be changed per module.
20. [should] Rope uses w08_rope and nails w08_nail; no other colours. -- MET: only w08_wood, w08_rope and w08_nail are used.
21. [must] (verifier) Origin at the bottom centre, nothing below z=0, one mesh per asset. -- MET: the runner reports 0 problems; all geometry starts at z>=0 (legs and stairs sit on 0).
22. [must] Triangles: hero <= 7000, parts <= 1500, variants 3000-5000; 0 problems. -- MET: hero 4108; variants 3412, 3240 and 3742; parts 84-348; 0 problems.

## Iteration log
- Rev1 builds 1-4: first full set (see the earlier record); the verifier failed it on deck chunkiness, braces, the front cell and the parts layout.
- Rev2 build 1: turned the hero and Straight variant to run along X (FRONT = long side), thicker planks (0.42) with 0.1 seams and height jitter, stringer 0.75, posts 0.65, rails 0.4x0.5, nails 1.5x, stairs part 1.6 with 0.5 treads, posts lying in the parts cell. The parts are now all readable; the braces on the stringer face looked cluttered and the legs were too short.
- Rev2 build 2: braces moved into the leg plane under the stringer, band 0.4+0.5, roll jitter reduced, corner and ramp also turned so variants keep the earlier good view.
- Rev2 build 3: deck raised to 1.9 (legs visibly taller, braces bolder), plank-end stagger reduced, ramp run lengthened to 3.3 (~25 degrees).
- Rev2 build 4: hero elevation 28 -> 36 so the deck top and its seams read in the hero, as in the reference.
