# W07 row 4 Ground Scatter - goals

Status after each build: MET / UNMET with one line of evidence (judged by eye vs reference row).

## ASSEMBLED / HERO
1. [must] Low flat pile: footprint ~5 x 4 studs, height <= ~1.4; viewed iso it is >= 3x wider than tall. MET - hero iso reads as a low flat pile, ~5.4 x 4.8 x 1.3, far wider than tall like the ref
2. [must] 2 large green lobed leaves (one left, one right-front), clearly the biggest leaves in the pile. MET - two big green lobed leaves, left and right-front, largest leaves in the pile
3. [must] 4-6 orange/rust maple leaves with pointed lobes visible around the pile edges. MET - 6 orange pointed maple leaves ring the pile edges (front-left biggest, as in ref)
4. [must] 2-3 brown twigs crossing in an X over the pile, longest ~4 studs, with visible cut ends. MET - three brown twigs, two thick ones cross in an X over the pile, tan cut ends visible
5. [must] One pinecone near the centre-front with visible stacked scale rows. MET - pinecone sits centre-front in front of the twig X, rows of plate scales visible
6. [must] 2 grey faceted stones (one left, one back-right), clearly different sizes. MET - grey faceted stones left-front and back-right, back-right clearly larger
7. [should] A few tiny twig bits scattered at the edges. MET - 4 small twig bits at the edges
8. [must] Nothing below z=0; leaves read as thin slabs, slightly cupped, not blobs. MET - leaves are thin cupped slabs, nothing below ground (runner 0 problems)

## FRONT
9. [should] Front view: low strip of leaves with pinecone and stone the tallest bumps; twigs poke out to the sides. MET - front: low leaf strip, pinecone and stone the tallest bumps, twigs poke out sideways

## SIDE
10. [should] Side view: same low profile, pinecone silhouette in the middle, stone at one end. MET - side: low profile, pinecone in middle, stone at the right end

## TOP
11. [must] Top view: lobed leaf silhouettes readable (green + orange), twigs as long brown diagonals, round grey stones. MET - top: green and orange lobed silhouettes, twigs as brown diagonals, grey stones

## PARTS
12. [must] Leaf: one green leaf ~2.4 long, broad with pointed lobes, slightly cupped, centre ridge. MET - broad green leaf ~2.4 with pointed lobes, cupped, raised midrib; ref Leaf is a plainer oval, spec asks lobed
13. [must] Leaf (Variant): orange maple leaf ~2.2 across with 5 sharp lobes. MET - orange maple leaf ~2 across, 5 sharp lobes, reads like ref Leaf (Variant)
14. [must] Twig: ~4 long, 0.25 thick, one small side branch, cut ends. MET - slightly bent 4-stud twig, one side branch, tan cut ends
15. [must] Pinecone: ~1.3 tall x 1.0 dia, egg shape tapering to a tip, rows of overlapping angled scales. MET - egg-shaped cone 1.0 x 1.2 with overlapping rings of plate scales tapering to the top
16. [must] Ground Stone: chiselled grey ~1.8 x 1.4 x 1.0 plus small GroundStoneSmall ~0.9 x 0.7 x 0.5. MET - large chiselled grey stone 1.8 x 1.3 x 0.9 and small one 0.8 x 0.7 x 0.5 side by side

## VARIATIONS
17. [must] Leaf Litter: dense overlapping spread ~4.5 x 4 of ~10 mixed orange/green leaves with tiny twig bits, no stones. MET - 10 overlapping orange/green leaves with crossing twig bits, no stones; flatter than the ref heap
18. [must] Twig Patch: 4-5 crossed twigs in a lattice ~5 x 4, a few orange leaves, one green leaf, 1 small stone. MET - 5 crossed twigs, 3 orange + 1 green leaf, 1 small stone; reads as a lattice
19. [must] Mixed Scatter (Sparse): 1 twig, 1 pinecone, 2 stones, 3-4 leaves with visible ground gaps. MET - 1 twig, pinecone, 2 stones, 4 leaves spread with gaps

## PALETTE / SCALE
20. [must] Palette: green leaf one key w07_leaf (#4E9A2C, renders saturated mid green), autumn leaf w07_leaf_autumn (#C0561E rust-orange), twigs/pinecone w07_wood (#7A4A2A mid brown), stones w07_stone (#8E8E94 mid grey); cut twig ends lighter tan (existing wood_end). No shade variants. MET - one key per material; green, rust-orange (slightly brighter than ref), brown, grey; tan cut ends via wood_end
21. [should] All assets collision none, origin bottom centre, under budget (hero 2500, parts as spec, variants 1200). MET - all collision none, all under budget (hero 1442/2500)

## Iteration log
- Build 1: first pass. Twig/LeafLitter over budget; maple lobes spiky stars, pinecone read as a pine tree, green leaf jagged.
- Build 2: 3-point broader maple lobes, egg-shaped pinecone, 5/4-sided twigs -> 0 problems, all under budget.
- Build 3: ivy-style 5-lobe green leaf, bigger stones, thicker raised crossing twigs, larger hero pinecone.
- Build 4: pinecone scales as broad plates (no spikes); pinecone moved in front of the twig X. All musts MET.
