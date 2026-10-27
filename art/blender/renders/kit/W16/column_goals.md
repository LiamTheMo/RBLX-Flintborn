# W16 row 3 — RuinColumn goals (revision after verifier fail)

## HERO (ASSEMBLED)
1. [must] Column ~18 tall, shaft ~3.2 wide, plinth ~7 wide. — MET - hero 18.4 tall; slim shaft between a much wider plinth and cap, same stack as the reference (ours a little slimmer)
2. [must] H1: chunky two-tier stepped octagonal plinth (7.4x2.3 then 6.0x1.8), clearly wider than the shaft and visibly bulky. — MET - hero/front: two chamfered octagonal courses with a lip step, ~2.3x shaft width, ~1/4 of the height; reads as a stepped base, though the reference's is still a touch bulkier
3. [must] Shaft = 4 octagonal drums with visible joint grooves and tiny offsets. — MET - front/side: 4 chamfered-square drums with inset joint bands
4. [must] Flared square capital with smaller upper slab and corner bosses. — MET - flared cap + slab visible in hero/front, 4 bosses in top view
5. [must] H6: dense small-leaf ivy (12-20+ clusters) with brown vine spiralling up the left/back to the cap, plus clumps over the cap. — MET - 33 small clusters along a brown vine: front cell shows a leafy strip down the whole left edge, side cell shows the vine winding to the cap, clumps over the cap; reference curtain is still slightly fuller
6. [must] H2: 6-8+ chunky rubble blocks, a big block front-left touching the plinth (3.8 wide, with a block stacked on it), medium blocks at sides/back, shards on the ground. — MET - hero: big stacked block mass at front-left, a 2.8 block front-right, medium blocks round the sides, grey/tan shards; footprint widens like a low pyramid (less tall than the reference's heap)
7. [should] H3: 5+ lush fern clumps between the rubble. — MET - 8 broad-bladed fern clumps with leaf hearts visible round the base in hero/front/side

## FRONT
8. [must] Symmetric column, cap wider than shaft, plinth widest, ivy trailing down one side. — MET - front cell matches: plinth > cap > shaft, ivy down the left side, ferns at base

## SIDE
9. [should] Same stack profile, ivy on one edge, ferns/rubble at base. — MET - side cell: same profile, vine+leaves on the right edge, rubble/ferns at base

## TOP
10. [should] T1: square cap with slab and bosses, ivy at cap edges, rubble scattered around. — UNMET - top cell shows cap, bosses and ivy/fern ring, but the tan rubble is mostly hidden under ferns and blends with the ground; the reference's scattered blocks don't read

## PARTS
11. [must] Six parts: cap, octagonal drum, stacked base, broken cap, broken shaft, ivy overlay. — MET - all six present and recognisable in the parts cell
12. [should] P2: shaft part 3.2x3.2x3 (now 3.2x3.2x3.0), cap 5x5x2, base matching the hero. — MET - KITSTAT shaft 3.2x3.2x3.0, cap 5.1x5.0x2.2, base 7.0x7.0x3.0 (matches the hero plinth, wider than the 6x6 spec to match the reference's bulk). Auto-layout still crowds the parts (layout is the runner's, not the module's)

## VARIATIONS
13. [must] FULL COLUMN: slender clean 18-tall column, ivy up one side, small base rubble. — MET - FULL cell: clean column with vine+ivy up one side, small rubble and ferns
14. [must] STUMP: plinth + 2 drums with jagged top, ivy on top, grass/rubble at base. — MET - STUMP: stepped plinth, 2 drums, snapped slanted top under ivy, ferns/rubble; 9.9 tall (taller plinth), slightly over ~8
15. [must] V3 FALLEN: 4 drums lying with visible breaks, ~14 long x 3.5, flared cap at the right end, base stone + rubble at left, ivy+ferns. — MET - 4 drums 3.3 long with 0.22 gaps and staggered offsets = 13.9 shaft; flared cap+slab tipped at the right end; tall base stone and rubble heap at left; vine and ivy draped over the left half. The cap reads thinner than the reference's chunky end block

## PALETTE / SCALE
16. [must] All cut stone one warm tan sandstone (#CDA877). — MET - renders warm tan like the reference
17. [must] Foliage one saturated green (#3F8A1A); vines brown soil (#7A4A2A). — MET - saturated green leaves, brown vine visible on side/fallen
18. [should] Grey stone only on a few small chips. — MET - grey only on 3-4 small shards
19. [must] 0 problems; hero <= 6000 tris, parts <= 1500; nothing below z=0. — MET - 0 problems; hero 5904/6000, variants <= 2632/4000, parts <= 708/1500, floor0 clamps z

## Iteration log
- Builds 1-3 (previous run): verifier failed at 5/10 (thin plinth, sparse rubble, chunky sparse ivy, thin ferns, short fallen, shaft 3.5).
- Build 4: shaft back to 3.2; drums/plinth rebuilt as chamfered-square prisms with joint lips; ivy as many small clusters on a thicker vine; broad-bladed ferns; fallen 4x3.3 drums + flared cap. Dressing still read small.
- Build 5: plinth 7.0/5.6; rubble x1.3, ferns x1.35, ivy clusters 0.72-0.95. Better, plinth still read low.
- Build 6: plinth 7.4x2.3 + 6.0x1.8 (4.1 tall), drums 2.9; big stacked front-left block + front-right block; 24-cluster vine; fallen dressing compacted, base stone taller.
- Build 7: second leaf-only ivy strand (33 clusters total) down the front-left; hero 5904 tris. Top-view rubble scatter is still weak.
