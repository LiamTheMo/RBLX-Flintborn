# W14 CaveColumn goals (revision after verifier fail)

## ASSEMBLED / HERO
1. [must] Strong hourglass: massive base ~22 wide x ~11-13 high, waist ~9-11 wide, flared cap ~20-22 wide x ~7-8 high, 32 tall. MET: base pile now reaches ~40% height and is as wide as the cap; waist about half the cap width; 32.4 tall. Neck is still a little long compared with the reference.
2. [must] Base is a heavy pile of 4-6 large overlapping boulders, the biggest in front (-Y), spilling outward. MET: six 9-12 stud boulders around a 14-high core; the tallest sits front-centre in the hero and front cells.
3. [must] 3+ clearly visible loose rocks (3-5 studs) round the foot, plus small 1.5-2 stud pebbles beyond them. MET: 6 solid rocks at radius 12-13 and 3 pebbles at radius 14-15 show clearly in the hero and front cells.
4. [should] Neck is stacked angular rock with large planar facets, not a smooth cylinder. MET: 4 offset faceted chunks; reads a little banded in the front view.
5. [must] Cap flares mushroom-like: 8 lumpy boulders bulge outward past a flat top at z=32. MET: lumps now overhang the flat heptagon top and the underside lumps flare out.
6. [must] 2-3 small spiky green tufts (w14_moss) at the base boulders, visible from the front. MET: 3 tufts at the front foot.
7. [should] A few small flat sand-tan chips (1-2 studs) at the very foot. MET: 4 orange-tan chips.
8. [should] Big chunky facets with no noisy small faces. MET.

## FRONT
9. [must] Front view: a symmetric hourglass with cap width about equal to base width. MET.

## SIDE
10. [should] Side view shows the same hourglass, with lighting and value close to the reference (not near-black). MET: SIDE_AZIMUTH set to -90 (the lit side), so the facets are readable and the tone matches the front.

## TOP
11. [should] Top view: a 7-sided faceted centre ringed by 7-8 boulders. MET: a clear heptagon disc ringed by 8 lumps. The tall-column shadow smear is still in the cell (camera/lighting, not the model).

## PARTS
12. [must] UpperSection: lumpy block wider at the top than the bottom, flat top, ~14x14x9. MET.
13. [must] MiddleSection: chunky faceted block ~10x10x10 of stacked offset chunks, not a plain box. MET: 3 offset faceted chunks round a thin core. It is only 230 tris, because facet merging keeps the count low.
14. [must] BaseSection: flat-topped block ~18x18x9 with a ring of boulders at its foot. MET: 7 boulders ring a heptagonal block.
15. [should] Stalactite: sharp 6-sided cone pointing down, bulge about 2/3 up, flat narrower top, ~5x11. MET: diamond-like bulging profile.
16. [must] Stalagmite: sharp 6-sided cone ~10 high on a small rock base ~6 wide. MET.

## VARIATIONS
17. [should] A Full Column: slimmer neck but still chunky, with a rubble base, 32 tall. MET.
18. [must] B Broken Column: low rubble heap ~20 wide with a jagged stump ~12 high, no ear-like spikes. MET: 8 ring boulders and a stump of 3 stacked angular blocks plus a shard, with a slanted broken top; 21x24x12.2.
19. [must] C Paired: left a full column with cap; right a stalactite under its own cap plus a floor stalagmite; ~32 wide and 32 tall. MET: the left column is now chunky (neck 1.2); 33x21x32.
20. [should] Variants have small moss tufts at their bases. MET.

## PALETTE
21. [must] w14_rock renders a warm grey-taupe like the reference, not pink. MET: changed to #837A77 in this module; the render now reads grey-taupe. The other W14 modules still use #8C7F7A, so a sheet-level sync has been requested.
22. [must] Moss tufts are saturated green (#5C8A2E) and appear only at rock feet. MET.
23. [should] w14_sand appears only as small foot chips. MET.

## Iteration log
- Earlier run: 4 builds, then failed by the verifier (mushroom on a stick, faint foot rocks, pinkish rock).
- Rev build 1: rewrote the base (6 big boulders), loose rocks with low sink, a 7-sided cap core with a lump ring, the stalactite bulge, the Broken stump blocks, the middle-section chunks, SIDE_AZIMUTH -90 and rock #837A77. The side view is fixed and the rocks show, but the neck and base were still thin and low.
- Rev build 2: base heights 9-12.5 with a 14-high core, neck lumps at subdiv 2 and 11-13 wide, a thicker cap (h 8). The hourglass now reads.
- Rev build 3: offset taller neck chunks, a smaller cap core so the lumps overhang, a jagged Broken top shard and a chunkier Paired neck.
- Rev build 4: thinned the middle-section core so its stacked chunks dominate.
