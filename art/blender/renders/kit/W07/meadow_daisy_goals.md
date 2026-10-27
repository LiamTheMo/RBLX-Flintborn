# W07 row 2 - Meadow Daisy goals

Status: all must goals MET after build 7 (revision after verifier fail, builds 5-7)

## ASSEMBLED / HERO
1. [must] Exactly 3 daisy heads at clearly different heights: tallest centre/back, one leaning left (lowest), one leaning right (middle). MET - 3 heads, tallest centre, left lowest, right middle
2. [must] (verifier) Each head has 5 crisp, faceted cream petals with distinct pointed tips and clear notches between them, around a faceted yellow nugget. MET - build 7 hero/top cells: 5 separated lozenge petals with pointed tips, star outline, raised golden nugget
3. [must] Heads tilt toward the viewer (petal faces visible from the iso camera); side heads tilt outward. MET - all three faces visible; right head less edge-on after yaw 28->18
4. [must] (verifier) Dense bright lime-green rosette of ~9 large separate pointed lozenge blades leaning outward, covering the stem bases, spreading to the full ~3 width. MET - 9 big blades (1.75-1.9 x 1.1-1.15) plus 3 low rim leaves, lime, rosette as wide as the hero, stem bases hidden
5. [must] Slender green stems with a visible gentle bend; side stems curve outward. MET - thin stems bow outward
6. [must] Scale ~3.0 x 3.0 x 3.6 studs (within 20%); origin bottom centre, nothing below z=0. MET - KITSTAT 3.6 x 3.0 x 3.9
7. [should] Head size ~1.3 wide, roughly 0.4 of the rosette width, as in the reference. MET - heads enlarged to size 1.15-1.2; read about the same head/rosette ratio as ref
8. [should] Hero tris <= 1500, chunky facets. MET - 1056/1500

## FRONT
9. [must] Front view: heads read as white 5-point stars with yellow dots; silhouette near square. MET - front cell: white stars with yellow dots over a wide rosette
10. [should] Leaves read as large separate pointed blades, not one blob. MET - separate pointed blade tips round the rim
11. [should] (verifier) Front cell in the reference is a single daisy; ours renders the hero from the front. UNMET - the runner renders the hero asset in the FRONT cell; not changeable from a module

## SIDE
12. [should] Side view: heads in profile tilted forward, leaves spread both ways. MET - side cell shows tilted heads and a two-sided rosette

## TOP
13. [must] Top view: white 5-petal stars with yellow centres over a green star rosette. MET - top cell: pointed 5-petal stars over a lime leaf star

## PARTS
14. [must] (verifier) Petal part: pointed cream petal ~1.0 x 0.45-0.5 with a ridge/crease, chunky and legible in the parts grid, 60-90 tris. MET - standing faceted lozenge gem petal, ridge front, crease back, 64 tris, 1.0 tall, reads like the ref's tall petal
15. [must] Center part: faceted golden nugget ~0.5 across. MET - 0.5 faceted golden dome
16. [must] Stem part: slender 6-sided stalk ~2.4 tall with bend and flared tip. MET - 2.4 bent stalk with flared tip
17. [must] Leaf part: broad pointed lozenge ~1.5 x 0.8 with central crease, lime green. MET - broad pointed leaf with crease

## VARIATIONS
18. [must] Single White: one daisy on ~2.6 stem facing front, 4 leaves at base, ~1.8 wide. MET - one front daisy, 4 big + 2 small leaves, 2.2 x 1.7
19. [must] White Clump: 3-4 smaller white daisies at different heights over a leaf clump, ~2.6 x 3.0. MET - 4 white daisies, 2.7 x 2.6 x 3.3
20. [must] Yellow Clump: 3-4 all-yellow 5-petal flowers at different heights over leaves. MET - 4 all-yellow pointed-petal flowers

## PALETTE
21. [must] (verifier) One key per material: petals w07_petal_white #F2EAD2 cream, centres w07_daisy_yellow #F5B800 golden, leaves+stems w07_leaf bright saturated mid-green; no painted shading. MET - w07_leaf changed to #62B232 rough 0.8; lit leaf faces now read lime like ref; 0 problems, no shade pairs
22. [should] Leaf lit faces as bright lime as the reference. MET - build 6/7 leaves match ref lime closely

## Iteration log
- Builds 1-4 (first pass): heads, stems, rosette; verifier failed: dark leaf, dense dark rosette, round petals, sliver Petal part.
- Build 5: w07_leaf #4E9A2C -> #62B232 (r 0.8); lozenge petal profile widest at 60%; gem Petal part (64 tris); 9-leaf rosette at ~30 deg. Leaf colour fixed; petals fused into a pentagon disc, rosette too flat.
- Build 6: narrower petals, leaves raised to ~40 deg, shallower crease, heads 1.2. Rosette good; petals still merging.
- Build 7: pw 0.5, longer petals, more lift, bigger centre, rim leaves pulled in, right head yaw 18. Petals now separate pointed stars.
