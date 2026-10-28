# BerryShrub (R05 row 1) goals

## ASSEMBLED / HERO
1. [must] Rounded dome silhouette, ~1.25x wider than tall (~7 w x 6 d x 5.5 h studs).
2. [must] Canopy built from 9-12 big chunky faceted leaf clumps with obvious flat facets (no smooth blobs, no noisy small facets).
3. [must] Larger clumps top-centre and front; smaller clumps tucked low at the sides.
4. [must] 7 glossy red berries (~1 stud dia) sitting on clump surfaces, spread front, both sides, top and upper right (not one ring).
5. [must] 3-4 short thick brown trunks, splayed outward, visible below the canopy for roughly the lower 1/4 of the height.
6. [should] Trunks taper upward and fan from a small base footprint.
7. [must] Palette: leaves one yellow-green r05_shrub_leaf #5A9E22; trunks one brown r05_bark #7A5030; berries one saturated red r05_berry #D81E1E. Render tones match reference (leaves not washed-out).
8. [should] Hero under 3000 tris, hull collision, origin bottom centre, harvest_hit socket at front (0,-2.5,2.5), harvest_deplete at base.

## FRONT
9. [must] Front view: dome with ~8-10 visible clumps, 4-6 berries visible across the face, trunks visible at the bottom centre.

## SIDE
10. [should] Side view: similar rounded dome slightly narrower than front, berries visible on the side and top.

## TOP
11. [must] Top view reads as a round rosette of clumps with ~5-7 red berries between/on them.

## PARTS
12. [must] BerryShrubLeafClump: 3 overlapping faceted green lobes, ~3 x 2.5 x 2 studs.
13. [must] BerryShrubBerry: single faceted red berry, ~1 stud diameter.
14. [must] BerryShrubTrunkFork: Y-shaped brown stem, ~2.5 tall trunk with two branches splitting, ~3 x 1.5 x 3.

## DROPS / DEPLETED
15. [must] BerryShrubBerries: two faceted red berries side by side in one closed mesh, ~0.5 radius each, nothing below z=0.
16. [must] BerryShrubDepleted: same trunks with only 4-5 smaller leaf clumps, ~5.5 wide x ~4 tall, zero berries, sparser than hero (trunks clearly visible).
17. [should] Depleted under 2000 tris, hull collision; no sockets.

## Verifier revision goals (added as must)
18. [must] HERO: crown reads as 9-12 distinct big pointy icosahedron-like clumps with obvious flat facets and visible overlap gaps.
19. [must] HERO: 3-4 splayed brown trunks fanning from a small base, visible below the canopy.
20. [must] FRONT: 8-10 visible clumps, 4-6 berries across the face, trunks at the bottom.
21. [must] SIDE: dome of distinct clumps with ~5 berries on side and top, trunks below.
22. [must] TOP: rosette of clumps with 6-7 berries between the clumps (not on the rim).
23. [must] Berries nestled into gaps between clumps, not perched on the rim.
24. [must] DEPLETED: same 3-4 trunk fan as the hero.
25. [should] Leaf Clump part lobes pointy/chunky wedges, not flat rounded.
26. [should] Berry is a ~80-tri faceted sphere (subdiv 2), not a coarse 20-tri icosahedron.

## Status (after revision build 4, final)
1. MET - front cell is a rounded dome clearly wider than tall (7.4 x 6.4 x 5.8), close to the reference outline.
2. MET - 11 separate subdiv-1 icosahedron clumps; each shows big flat facets with visible gaps between bodies.
3. MET - largest clump top-centre, big front clump, smaller clumps tucked low at both sides.
4. MET - hero iso shows 7 red berries spread over front, both sides, top and upper right.
5. MET - 4 tapering brown trunks fan from a small base; the front cell shows 3 splayed legs below the canopy.
6. MET - trunks taper upward from one small base footprint.
7. MET - one key per material at the sheet values; bark brown and berries vivid red match; leaves read slightly greener than the reference (sheet value is fixed).
8. MET - 884/3000 tris, hull, origin bottom centre, leaf-coloured harvest_hit at front, harvest_deplete at base.
9. MET - front cell: ~9 distinct clumps, 5 berries spread across the face, 3 trunks at the bottom.
10. MET - side cell: dome of distinct clumps, ~4-5 berries on the side and top, trunks below.
11. MET - top cell: big centre clump ringed by 6 clumps, 7 berries spread round the crown in the gaps.
12. MET - leaf clump part: 3 chunky faceted lobes, centre one tallest, 3.7 x 2.2 x 2.4.
13. MET - single faceted red berry ~1 stud.
14. MET - Y-shaped brown fork, 2.5 x 1.1 x 2.9.
15. MET - two faceted berries side by side in one mesh, 160 tris, nothing below z=0.
16. MET - depleted: 5 smaller clumps over a visible splayed trunk fan, 5.4 x 4.4, no berries.
17. MET - 204/2000 tris, hull, no sockets.
18. MET - crown reads as distinct chunky icosahedra, no merged lumpy mass.
19. MET - 4-trunk fan, 3 legs visible splayed in the hero and front cells.
20. MET - front: ~9 clumps, 5 berries across the face, trunks at the bottom.
21. MET - side: distinct clumps, ~4-5 berries, trunks below (one fewer berry than the reference).
22. MET - top: rosette of centre plus ring of 6, 7 berries spread round between clumps.
23. MET - berries sit at ray exits between clumps, half embedded, not perched on top.
24. MET - depleted uses the same 4-trunk fan (several legs visible).
25. MET - leaf clump lobes are chunky pointed icosahedra, not flat rounded blobs.
26. MET - berry is an 80-tri subdiv-2 icosphere in the part, hero and drop.

## Iteration log
- Build 1: subdiv-1 icosahedra (too coarse), berries floating off a shell, grey VFX dust hid the trunks.
- Build 2: subdiv-2 clumps with facets merged, berries attached to the clumps; dust still hid the base.
- Build 3: VFX swapped to green leaf chips with no dust (base now visible), trunks splayed, side clumps lowered, leaf clump lobes put in a row, depleted spread out.
- Build 4: berries moved round to the top and back-left so the top view is better spread. This was the last of the 4 builds allowed.
- Revision build 1: clumps changed to subdiv-1 icosahedra with rotations, laid out as a rosette (centre + ring of 6 + 4 low); 4-trunk fan; berries placed by ray exit through clump gaps. Clumps now distinct, but trunks merged into one stump and berries sunk too far.
- Revision build 2: thinner trunks, wider spread and offset, low clumps raised; berries pushed outward. Trunk fan now visible; berries still mostly on the rim.
- Revision build 3: berry directions raised to sit between centre and ring clumps, 3 on the front. Front now shows 5 berries, top 7, but they bunched toward the front.
- Revision build 4: moved the top and left berries toward the back. The top view now has 7 berries spread round the rosette.
