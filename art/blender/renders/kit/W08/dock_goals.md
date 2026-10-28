# W08 Dock goals (revision 2, after verifier fail)

Orientation (revised): long axis along Y (8 long) and width along X (6), as the spec and the reference TOP
cell require (long vertical deck, planks across). The runner's FRONT camera is fixed at azimuth 0, so the
FRONT cell now shows the short end (2 posts + X brace) and the SIDE cell (az 90) the long side (3 posts).
That swaps the reference's front/side content; a module cannot change it (there is no FRONT_AZIMUTH).
HERO_AZIMUTH = -112 and HERO_ELEVATION = 30 so the hero and variant iso views look down at the long side, as the reference hero does.
Post height: the spec says ~6, but the reference's legs are about 1.8x the post height above the deck. The verifier also judged the posts too tall.
Posts therefore stop at 5.2 (2.0 above the deck); the hero is 6.5 x 8.5 x 5.2.

## ASSEMBLED / HERO
1. [must] Raised pier 8 long (Y) x 6 wide (X), deck top z~3.2, posts above. -- MET: the hero shows a long deck receding left to right, deck mid-height. Size 6.5 x 8.5 x 5.2.
2. [must] (verifier) Low wide platform: short sturdy dark legs, thin deck band (0.4 plank + 0.7 beam), posts ~2 above the deck. -- MET: the legs are short and dark and the deck band is thin. The posts rise about as high as in the ref hero, and the 30-deg camera shows the deck top like the ref.
3. [must] Six dark-brown piles (w08_pile_wood) under an orange-brown deck (w08_wood); legs clearly darker. -- MET: the legs render dark brown under an orange deck in every cell.
4. [must] Six mooring posts (4 corners + 2 mid long sides) rise above the deck, each with a tan rope wrap in its upper third. -- MET: the top view shows 6 caps at the corners and mid long sides. Each post has a 3-turn tan wrap near the top.
5. [must] Rope swags sag between posts along a long side and across one end; rope thin. -- MET: thin tan swags (0.09) sag along the far long side and the +Y end. They are thinner than in rev1 and close to the ref.
6. [must] ~10 chunky deck planks running ACROSS the 6-stud width with visible gaps and jitter. -- MET: the top view shows 10 horizontal planks with dark gaps and slight jitter.
7. [should] Brass nail heads (w08_nail) on beam/pile joints and brace crossings. -- MET: brass studs show on the beams at the piles and on the X-brace crossing (front cell).
8. [should] No ground dressing (reference shows plain white). -- MET: no dressing.

## FRONT (az 0: short end, see orientation)
9. [must] 2 wrapped posts above the deck, crossbeam under the deck, X brace between the two dark piles. -- MET: the front cell shows 2 wrapped posts, the end crossbeam and a big X brace between the dark legs, matching the ref SIDE cell.
10. [should] Front silhouette about as wide as tall. -- MET: the front cell is about 6.5 wide x 5.2 tall.

## SIDE (az 90: long side)
11. [must] 3 wrapped posts with rope swags between them, beam band under the deck, 3 dark legs. -- MET: the side cell shows 3 wrapped posts with 2 swags, a beam band with nails and 3 dark legs, matching the ref FRONT cell.

## TOP
12. [must] (verifier) Long VERTICAL deck (~8:6) with planks running horizontally across it. -- MET: the top cell shows a tall deck with horizontal planks, like the ref top.
13. [must] (verifier) 6 round 8-sided post tops at the corners and mid long sides; rope does not outline all four edges. -- MET: 6 round caps (3 per long edge). Rope shows only on the right edge and the top end, not on all four.
14. [should] (verifier) ~10 planks across the width with visible gaps. -- MET: 10 planks with gaps.

## PARTS
15. [must] DockMooringPost: short square orange post, rope wrap near the top, round cap. -- MET: an orange post with a round cap and a tan wrap sits in front of the pile.
16. [must] DockRopeTie: chunky tan rope piece ~1.5 long with a coiled knot. -- MET: a small tan coiled rope (1.7 long), chunkier than rev1. It is small in the cell.
17. [must] DockPile: tall dark post 0.8 x 0.8 (6 tall) with rope band near the top. -- MET: a tall dark pile with a tan band near the top.
18. [must] DockDeckPlank, DockBeam, DockBrace, all w08_wood. -- MET: orange plank, beam and slanted brace at the left of the cell. The runner's layout overlaps them a little.

## VARIATIONS
19. [must] DockStraight: long narrow pier 12 x 4, 8 wrapped posts, tall legs. -- MET: a long narrow pier runs left to right with 8 wrapped posts, swags and tall dark legs.
20. [must] (verifier) DockTHead: walkway joins a 10 x 4 cross T-platform with continuous planks, legs under both, 8 posts, whole T visible. -- MET: the T bar sits across the back and the walkway comes toward the viewer, like the ref. Planks are continuous, legs stand under both parts, and the X braces sit between the walkway piles.
21. [must] DockLHead: 8 x 4 pier with a 4 x 4 perpendicular extension (clear L), 6 posts, rope ties. -- MET: the extension juts toward the viewer from the main pier with its planks turned 90 deg. It has 6 wrapped posts and swags.

## Palette
22. [must] Sheet palette verbatim; one flat colour each; deck warm orange-brown, rope tan. -- MET: the keys match the sheet verbatim, with flat colours. The deck renders orange-brown and the rope tan.
23. [should] (verifier) Rope thinner and less dominant; wood less red. -- UNMET (partly): the rope is thinner now (swag 0.09, wraps 0.1). The wood still renders slightly red because w08_wood is a shared sheet key; requested as a sheet-level change.

## Iteration log
- Rev1 builds 1-3: long axis X; the verifier failed the top-view rotation, the T-Head silhouette and the thick rope.
- Rev2 build 1: long axis moved to Y, 10 planks across X, thinner rope, swags only on one long side and one end, HERO_AZIMUTH -112. The top cell now matches. Posts too tall; the T walkway ran sideways.
- Rev2 build 2: posts cut to 2.0 above the deck. The T-Head walkway now runs along X toward the camera, with the T bar at the back. The T reads clearly.
- Rev2 build 3: HERO_ELEVATION 30. The hero and variants show the deck top like the ref, and the hero reads lower and wider. 0 problems.
