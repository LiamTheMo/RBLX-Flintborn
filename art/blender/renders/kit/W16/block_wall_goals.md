# W16 row 2 BlockWall: goals

Reference: art/reference/kit/rows/W16_row2.png. Status after the latest build (build 5) in brackets.

## ASSEMBLED / HERO
1. [must] Straight wall ~20 long x 3.5 thick, ~9 tall in the middle; hero ~2x wider than the wall is tall (excluding pier). [MET: hero cell reads as a long wall about 2x wider than tall, as in the reference]
2. [must] Visible staggered courses: 4 courses in the middle, offset vertical joints (running bond), mixed long (~4), medium (~2.5) and short (~1.8) blocks. [MET: the front cell shows 4 courses with offset joints and mixed block lengths]
3. [must] (verifier) Right end: square pier ~4.5 wide made of stacked blocks, clearly taller than the wall (~1.2-1.4x, top ~12 vs wall ~9), with a wider overhanging coping cap. [MET: the pier now towers above the wall by more than a course plus its cap. The 5.5 cap overhangs on all sides in the hero, front and side cells]
4. [must] (verifier) Left end steps down to ~6.5 with a smaller cap stone, and the step is clearly readable. [MET: the left third is a full course lower with a thin small cap. The step reads in the hero and front cells]
5. [must] 5-7+ tumbled blocks of varied sizes, rotated and piled at the front-right base, some stacked, 1-2 grey. [MET: a pile of 9 blocks at the front-right, two stacked on others, three grey. It reads like the reference pile]
6. [must] (verifier) Ivy: two dense vertical bands plus one over the pier. Leaf clumps big enough (~2-3 studs across) to read as the reference's leafy masses, with each band nearly continuous. [MET: three wide, near-continuous bands of big 5-lobe clumps. Leaf size now matches the reference masses]
7. [must] Brown w16_soil vine stems visible inside the ivy bands. [MET: wavy brown stems show between the clumps in the hero and intact cells]
8. [should] (verifier) Small ivy at the top edge and pier cap, and at least 8 grass tufts around the base. [MET: ivy sits on the top edge and pier cap, with 9 tufts at the base. The tufts are as big as the reference tufts]
9. [should] Blocks read as tan cut stone with chamfered edges and small irregularities. [MET: chamfered, jittered blocks]

## FRONT
10. [must] Front view: long rectangle of 4 courses, taller pier on the right, lower left end, ivy as vertical green strips. [MET: the front cell matches this layout]

## SIDE
11. [should] Side view: pier dominates as a tall narrow stack with an overhanging cap, rubble at its foot. [MET: the side cell shows a tall stack, its cap and rubble]

## TOP
12. [should] (verifier) Top view: wall strip, a distinct wider pier square at the end, rubble in front, ideally an L return. [UNMET (partly): the strip, the wider pier square and the rubble read, but there is no L return. The spec hero is a straight wall, so the L appears only in the CORNER SECTION variant]

## PARTS
13. [must] Five parts: Coping (8x3.5x1.2 with centre seam), BlockLarge 4x3x2, BlockMedium 2.5x3x2, BlockSmall 1.8x2.5x1.8, and Corner (4-block stack on a wider base, ~9 tall, with cap). [MET: all five are present at spec sizes. The coping keeps its 8x3.5x1.2 spec size and seam]
14. [should] (verifier) Corner part has a clearly wider ~5.5 base block, and its cap is wider than the stack. [MET: the 5.5 base visibly juts out under the 3.8 stack, and the 4.6 cap overhangs the stack]
15. [should] (verifier) Parts cell composition is exploded like the reference: coping at the top, blocks at the right, corner stack at the left. [UNMET: the runner lays out the parts grid automatically (corner top-left, coping bottom). The module cannot control it]

## VARIATIONS
16. [must] INTACT WALL: even full-height ~9-10 wall, uniform courses, continuous coping, ivy patches. Proportions ~1.6-1.8x wider than tall, like the reference. [MET: even rectangle with continuous coping and two dense ivy bands, about 1.65x wider than tall]
17. [must] BROKEN / STEPPED: wall steps from ~7 on the left down to ~3.5 on the right, with loose blocks at its feet and on the steps, and ivy. [MET: three clear steps with loose blocks on the steps and at the feet, ivy on the left]
18. [must] (verifier) CORNER SECTION: clear L-shaped footprint (two ~14 arms) visible from the hero camera, tall corner pier clearly above the wall, coping, ivy up the pier. [MET: seen from inside the L, the back arm and the forward-coming right arm both read. The 13.2 pier with its cap clearly rises above the 9.8 arms, and an ivy band climbs it]

## PALETTE / SCALE
19. [must] (verifier) w16_sandstone is the only colour on cut blocks and renders pale beige like the reference, not orange. [MET: retuned at sheet level to #D4B98C as the verifier asked. The render is now pale beige, close to the reference, maybe a touch more yellow]
20. [must] w16_ivy #3F8A1A on all leaves and tufts reads as saturated mid green; w16_soil #7A4A2A only on stems; w16_stone_grey #8F8D86 only on a few rubble blocks. [MET: matches the reference greens; grey only on 3-4 rubble blocks]
21. [should] Block scale consistent (4 / 2.5 / 1.8). Hero under 6000 tris, parts under 1500. [MET: hero 5012/6000, variants max 4496, parts max 498]

## Iteration log
- Build 1: first pass. 4 problems (sandstone and soil shade pair). Ivy too small and sparse, rubble small.
- Build 2: kit_two_tone_ok waiver on the soil stems. Bigger ivy and tufts, more rubble. 0 problems.
- Build 3: larger rubble pile, more top-edge ivy. 0 problems. Verifier failed it: pier not tall enough, ivy sparse, L not legible, too orange.
- Build 4 (revision): wall courses 2.2 (8.8 tall), pier 5 courses plus cap (12.2), clearer left step. Ivy bands rebuilt as alternating 1.1-1.45 clumps with lobes=5 for budget. Sandstone set to #D4B98C. Corner part gets a 5.5 base and a wider cap. Corner section rebuilt as a concave L seen from inside. All improved, but the corner pier was still not prominent.
- Build 5: corner section pier raised to 13.2 with a 5.7 cap. Hero pier band and broken-wall ivy slightly reduced. All must goals MET, 0 problems.
