# R07 ClayDeposit goals

Status after each build: MET / UNMET with one line of evidence.

## ASSEMBLED / HERO
1. [must] Low wide heap: hero ~9 x 8 studs footprint, ~5 tall (width:height ~1.8:1). — MET - hero 9.5x8.1x5.0; reads as a low wide heap, though the lobes sit a little taller on the pad than the reference.
2. [must] 5 orange lobes visible: big main lobe back-centre-left is the tallest (~5), big lobe front-right, medium front-left, two small (left edge, right-back). — MET - hero cell shows main lobe back-left tallest, big front-right, medium front-left, small left and right-back lobes.
3. [must] Lobes are chunky flat-faced boulders with few large facets (each big lobe shows ~6-12 broad faces, no noisy small faces). — MET - each big lobe shows roughly 8-14 broad flat faces, no noisy small faces (slightly rounder than the reference).
4. [must] Heap reads back-high, front-low: front lobes top out at 2.5-3.5 studs. — MET - front lobes top at ~3 studs, main lobe rises to 5 behind them.
5. [must] Brown soil pad visible as a slab rim all around the lobes, ~1-1.2 tall, much wider than tall, with a rough faceted edge. — MET - brown sloped slab rim visible front, left and right, ~1.1 tall, faceted jittered edge.
6. [must] 6-8 small grey pebbles (0.8-1.4 studs) around the rim and wedged between lobes, mostly left, front and right. — MET - 8 grey pebbles on the rim (left, front, right) and between the front lobes.

## FRONT
7. [should] Front view: front-right lobe is the largest visible mass, main lobe rises behind it; silhouette a broad dome over a wider pad. — MET - front cell: front-right lobe biggest front mass, main lobe behind, broad dome over wider pad.

## SIDE
8. [should] Side view: lobes stepped from tall back to low front over the flat pad; pebbles at pad ends. — MET - side cell: tall back lobe stepping to low front lobe over the pad, pebbles at pad ends.

## TOP
9. [must] Top view: roughly round/oval pad with 5 orange lobes (3 big, 2 small) and grey pebbles in the brown ring. — UNMET - top cell shows round pad with 5 lobes and pebbles, but the brown ring is narrower than the reference (lobes cover more of the pad).

## PARTS
10. [must] ClayDepositMainClayLobe: single large faceted orange boulder ~4.5x4x3.8, flat-faced. — MET - parts cell: one large faceted orange boulder 4.4x4.2x3.5.
11. [must] ClayDepositClayLobe: smaller angular wedge-like orange lobe ~2.6x2.2x2.2. — MET - smaller angular orange wedge 2.0x2.3x2.1 beside it.
12. [must] ClayDepositSoilBase: low brown soil mound ~8x6.5x1.2 with 3-4 small grey pebbles on its edge. — MET - low brown soil mound 8.3x6.8x1.2 with 4 grey pebbles on its edge.

## DROPS / DEPLETED
13. [must] ClayLump drop: one closed orange faceted lump ~1.6x1.5x1.5, <=300 tris. — MET - closed faceted orange lump 1.6x1.5x1.4, 68 tris.
14. [must] ClayDepositDepleted: only the flat brown pad (~9x8x1.3) with 4-5 grey pebbles on its rim, no orange. — MET - depleted cell: only a low brown pad with a slightly lumpy top and 5 rim pebbles, no orange.

## PALETTE / SCALE / VFX
15. [must] Clay is one saturated orange (r07_clay #D4572B); render lit faces bright orange, not pastel or brown. — MET - render lit faces bright saturated orange like the reference, not pastel.
16. [must] Soil pad one mid brown (r07_soil #7A5636), pebbles one purple-grey (r07_stone #77737A); no other colours. — MET - only orange, brown and purple-grey in every cell.
17. [must] VFX: harvest_hit on front-right lobe face ~(2,-3.2,2.4) in clay colour, harvest_deplete at (0,0,0.5); no ore_glint, no light. — MET - harvest_hit at (2,-3.2,2.4) clay colour, harvest_deplete at (0,0,0.5); no glint/light.
18. [should] Hero under 4000 tris, parts under 1500, drop under 300, depleted under 2000; nothing below z=0. — MET - hero 520/4000, parts <=116, drop 68/300, depleted 176/2000; runner reports 0 problems.

## Iteration log
- Build 1: cylinder pad, 5 rock lobes (facets 16), small pebbles. Heap read right but lobes rounded, pebbles too small, drop a 20-tri pyramid.
- Build 2: ellipsoid-mound pad (too thin and wide, buried pebbles) - reverted. Lobes facets 24 (flatter faces), drop subdiv 2.
- Build 3: back to sloped cylinder slab, larger lobes and pebbles, soil lumps on depleted top. Pad looked like a vertical drum.
- Build 4: pad top ratio 0.7 (sloped rim), lobes ~8% smaller and pulled in, pebbles on the ground leaning on the rim. Closest match; top-view brown ring still narrower than the reference (build cap reached).
