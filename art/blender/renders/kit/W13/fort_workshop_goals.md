# W13 FortWorkshop goals

Status after revision build 4 (R4). Palette mid-tones: timber #A9612C (all wood), canvas #E6D2A4 (canopy, banner emblem), stone #8A9199 (footings, tools), banner #C3262A, moss #4C9A3C (green sack, grass clumps), lantern glow #FFB23A (lantern glass only).

## ASSEMBLED / HERO
1. (must) Open shed: 4 corner posts with cube caps above a cream canvas canopy. [MET] all 4 caps stand above the canvas in hero and top cells.
2. (must, verifier) Canopy is a readable tent: slanted high toward the back, peak ~4 above the front hem, front hem drooping, overhang ~0.5. [MET] hip tent with four sloped panels and crisp ridges meeting at a peak behind centre; front hem sags between the front posts; overhang 0.5 front / 0.7 back.
3. (must) Grey stone footing under each post. [MET] grey blocks at all 4 corners in hero, front and side.
4. (must) Waist-high horizontal plank half walls back and right; open front with a 6-wide step. [MET] side cell shows 4 offset horizontal planks on the right wall; step plank at the front in hero and top.
5. (must, verifier) Interior contents (workbench, anvil/tools, crate with sack, lantern) visible under the canopy. [MET] the hero shows the bench with a grey anvil and a tool rack, a green sack on the crate and the glowing lantern. The interior is still shaded, which is correct for sun from the front-left (rule: lighting is not paint), but every object reads.
6. (must) Red banner with cream diamond on the back beam. [MET] visible behind the bench in the front cell; hidden in iso, as in the reference.
7. (should) Crate + green sack left, barrel, log stack, rubble and grass. [MET] sack, crate and barrel at the left; grass clumps and rubble around the base.
8. (must) Palette: orange-brown wood, warm cream canvas, grey stone, red banner. [MET] colours match the reference swatches.
9. (should, verifier) Overall bounds about 15x13. [MET] hero is 15.3 x 13.9 x 13.9 studs (was 16.6 x 14.3).

## FRONT
10. (must) Front posts frame the opening, sagging hem, banner at the back, lantern upper left. [MET] all present in the front cell; the canvas peak is visible above the hem.

## SIDE
11. (must, verifier) Side: waist-high horizontal plank half wall, open front, canopy sloping. [MET] SIDE_AZIMUTH 60 (front-right three-quarter): the right half wall is lit with separate offset planks, the post caps are visible and the open front and the bench show; there is no white horizon strip.

## TOP
12. (must) Near-square cream canvas with 4 caps and the step at the front. [MET] the top cell shows a square canvas with hip ridges, 4 caps and the step.

## PARTS
13. (must) 11 parts present and recognisable. [MET] canvas (now a tent), beam, post, wall, floor, banner, hook lantern, table, rack, crate+barrel, stone.
14. (should) Floor 5-7 planks; half wall horizontal planks with a post. [MET] the floor has 7 planks; the wall has 4 planks and a post.
15. (should) Banner part red with a cream diamond and bar. [MET] visible in the parts cell.
16. (should, verifier) Parts are composed as an exploded set, not sparse. [UNMET] the parts cell layout is automatic (grid by build_kit); the large floor and canopy make the small parts look small.

## VARIATIONS
17. (must, verifier) A Carpenter Bay: bench with saw and lumber, sawhorse, no banner, lantern, distinct from the hero. [MET] the sawhorse with a long plank sits front-centre, a lumber stack is at the left front, boards lean on the back wall and a grey saw blade is on the bench. It has no banner and no crate or sack.
18. (must, verifier) B Storage Shed: a big stack of log ends fills the bay. [MET] a 5-row wall of round log ends (8/7/7/6/4) about 4.5 studs high faces the front, with a full side rack at the right and a loose pile at the left.
19. (must) C Trader Bay: counter with goods and a green sack, banner front-left, lantern right. [MET] the red banner hangs at the front left, the lantern is at the right and the counter with boxes and a sack is visible.
20. (should) Lantern heat_glow socket (#FFB23A, 0.5) on hero, A, B and C; tris < 8000. [MET] sockets on all four; hero 5637 tris, variants 4.5k-7.1k.

## Iteration log
Prior run (builds 1-4): flat slab canopy, then a gable, posts raised and overhang cut to 0.9. The interior was still a dark cave and the verifier failed it.
R1: raised the canopy (front 9.7, back 11.6, peak 13.6), cut the overhang to 0.5 front / side 0.25, offset and tilted the wall planks, set SIDE_AZIMUTH 60, rebuilt the A/B contents. Result: the side view became readable. The canopy still looked like a slab.
R2: added a stronger hip, moved the bench forward to y 1.4 with a tool rack on the wall cap, gave the anvil bigger tools, moved the B log wall forward. Result: the canopy looked like a pillow dome.
R3: made the canopy a min-of-planes hip tent, set HERO_ELEVATION 14 and pulled the scatter in. Result: the interior became visible and the bounds came to 15.3x13.9. The top view showed stair-stepped ridges.
R4: rebuilt the canvas as rings around the apex, so the hip ridges run straight to the corners. Result: clean tent facets in every cell.
