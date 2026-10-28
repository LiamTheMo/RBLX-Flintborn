# R07 CaveMushroom goals

Reference: art/reference/kit/rows/R07_row3.png. Status after each build in [brackets].

## ASSEMBLED / HERO
1. (must) Three mushrooms in a clear size hierarchy: large centre-back, medium left, small right-front. [MET: large centre-back, medium left, small right-front read clearly in hero and front.]
2. (must) Big cap is a broad faceted dome ~5.2 wide x 2.4 tall, clearly wider than the stalk (~2.7x stalk width) and overhanging it on every side. [MET: big cap ~5.2 wide overhangs the stalk all round in front and side views.]
3. (must) Hero overall ~8 x 7 studs footprint, ~6.5 tall; silhouette ~1.25x wider than tall in the iso view. [MET: KITSTAT 8.7 x 7.0 x 6.4; iso silhouette wider than tall like the reference.]
4. (must) Caps read as chunky low-poly domes with ~12-16 large facets, no noisy small facets. [UNMET: subdiv-2 domes show ~40 mid-size facets; reference shows ~12-16 large ones. The 20-face version (build 1) was pointy; no in-between tried within 4 builds.]
5. (must) A cream underside rim band is visible just under the edge of each cap. [MET: thin cream band visible under the big and medium cap rims in front/side.]
6. (must) Grey faceted rock cluster forms a lumpy ring holding all three stalk bases: one wide low main rock front-centre plus 5-6 smaller rocks (0.9-2 studs) around the rim and behind. [UNMET (partial): main rock + rim rocks hold the bases in front, but the cluster reads lower and sparser than the reference's lumpy ring; the main rock still looks like a flat pillow.]
7. (should) Big stalk is fat and tapering (~1.9 wide at the base, ~1.5 under the cap), ~3 studs of stalk visible above the rocks in front view. [MET: stalk ~2.3 at base tapering to ~1.7, ~2.5 visible above the rocks.]

## FRONT
8. (must) Front view: big mushroom centred, medium mushroom at the left lower than the big cap's rim (medium cap top below big cap rim height), main rock across the front. [MET: front view big centred, medium left below the big rim, main rock across the front.]
9. (should) Medium cap leans slightly left; small cap tilted. [MET: medium cap leans left, small cap tilted right.]

## SIDE
10. (should) Side view keeps the big cap overhang on both sides and shows a smaller mushroom at the side, rocks along the base. [MET: side view shows big overhang, a smaller mushroom at the side, rocks along the base.]

## TOP
11. (must) Top view: big round cap dominates (~60% of footprint width), two smaller round caps visible beside it, grey rocks peeking around the rim. [UNMET: top view big cap covers most of the footprint and the rocks barely peek out at the front; reference shows three separate caps with rocks around the right rim.]

## PARTS
12. (must) CaveMushroomMushroomCap: rust dome ~5x5x2.4 with a cream flat underside. [MET: parts cell shows rust dome with cream flat underside.]
13. (must) CaveMushroomCapUnderside: thin flat cream faceted disc ~4.6x4.6x0.5. [MET: flat cream faceted disc ~4.4x4.6x0.6.]
14. (must) CaveMushroomMushroomStalk: cream faceted tapered stalk ~1.9 wide x 3 tall, wider at the base. [MET: cream tapered faceted stalk 1.9x3 (reads small in the parts grid).]
15. (must) CaveMushroomRockBase: wide low grey rock ~6x4.5x2 with 2 small flanking rocks. [MET (partial): wide low grey rock with two small flanking rocks; a little flatter than the reference.]

## DROPS / DEPLETED
16. (must) CaveMushroomWhole: small complete mushroom (rust cap on cream stalk) ~1.6x1.6x2, <=300 tris. [MET: rust cap on cream stalk, 1.6x1.7x2.0, 140 tris.]
17. (must) CaveMushroomCapDrop: loose rust faceted dome ~2x1.8x1, <=300 tris. [MET: loose rust dome 2.0x2.1x1.0, 80 tris.]
18. (must) CaveMushroomDepleted: rocks only, ~8x7x2.2, with exactly two short cream stalk stubs with flat cut tops (~0.9 wide, 1.0-1.4 tall). [MET: rock cluster 8.5x6.5x2.0 with two short cream stubs with flat tops.]

## PALETTE
19. (must) Caps one saturated rust-brown r07_cap (#A84526) that renders like the reference's mid rust, not pastel or dark brown. [UNMET (palette fixed): r07_cap #A84526 renders more orange-red/brighter than the reference's brown-rust; the sheet palette must be copied verbatim, so the key cannot change from this module.]
20. (must) Stalks/underside one cream r07_stalk (#E0C298); rocks one purple-grey r07_stone (#77737A). Only these three keys. [MET: only r07_cap, r07_stalk, r07_stone used; cream stalks and purple-grey rocks match.]

## VFX / TECH
21. (must) harvest_hit at the big cap edge (1,-2.5,4.5) in cap colour, harvest_deplete at (0,0,0.5); optional subtle dust above the cap; no emissive. 0 problems, under budgets. [MET: harvest_hit (1,-2.5,4.5) cap colour, harvest_deplete (0,0,0.5); dust dropped (read as smoke puffs); 0 problems, all under budget.]

## Iteration log
- Build 1: icosahedron caps (20 faces) too pointy; rocks sparse; dust puffs looked like smoke; Tint 1.26x problem on depleted.
- Build 2: subdiv-2 flattened domes (rounder), bigger/taller rim rocks, dust removed, tint_var 0.05 -> 0 problems.
- Build 3: wider cream underside band, extra rocks at medium/small stalk bases, caps spread apart.
- Build 4: fatter stalks, flatter big cap (5.2x2.3), taller rocks. Stopped at the 4-build cap with goals 4, 6, 11, 19 open.
