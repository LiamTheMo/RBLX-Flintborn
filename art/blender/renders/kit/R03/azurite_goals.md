# R03 Azurite goals

Status after revision build 4 (MET / UNMET, judged by eye against the reference row; numbers only support).

## HERO (iso, -22)
1. [must] Three fat blue crystals; tallest in the middle (~7.5), left ~6, right ~5. -- MET - hero/front: three separate crystals, centre clearly tallest, left mid, right lowest.
2. [must] (verifier) Crystals fat and stubby (body width >= ~0.5x height), blunt multi-facet tops, much chunkier than quartz. -- MET - front view: main crystal body ~3.6 wide at 7.5 tall, side crystals as wide as the reference slabs; tops are blunt 2-step faceted points.
3. [must] Right crystal leans outward ~25 deg (and a little forward); left leans out left; main tilts slightly back. -- MET - front: left leans out ~18 deg, right ~20 deg right and forward; main nearly upright.
4. [must] (verifier) Big smooth-faced grey boulder in front dominates the base, wide low faceted mound with large clean facets, covering the lower ~35-40% of the crystals. -- MET - front/hero: wide faceted mound (~6 wide, ~3.5 high) with ~10 large planar faces, hides the crystal bases like the reference.
5. [must] (verifier) Crystals large relative to the boulder: main crystal dominates and rises well above the boulder. -- MET - front: main rises ~1.2x the boulder height above it, the same ratio measured on the reference front cell; the blue cluster spans the full hero width.
6. [should] 3-4 smaller rocks at the left and right bases plus a tiny rock at the far right. -- MET - small rocks at both bases and a tiny rock at the far right (hero, front).
7. [should] (verifier) Hero overall ~8 x 7 x 7.5 studs, width within 8. -- MET - 7.9 x 6.9 x 7.7 studs; width now from crystals and boulder, not spread rocks.
8. [should] (verifier) Facet density comparable to the reference (10+ faces visible per crystal). -- UNMET - each crystal shows ~8-10 faces; reference crystal tops have a few more facets. Hero 400/3500 tris.

## FRONT
9. [must] Front: central crystal above the boulder, side crystals flaring outward, boulder covering the lower ~35-40%. -- MET - front cell matches the reference layout closely.
10. [should] Large clean planar facets on boulder and crystals (no noisy faces, not too few on the boulder). -- MET - boulder shows ~10 big planes like the reference; crystals clean.

## SIDE
11. [should] (verifier) Side: main crystal behind, a lower side crystal in front, rocks at the base. -- MET - side cell now shows the tall main crystal behind and the lower right crystal in front leaning forward, rocks at the base.

## TOP
12. [must] (verifier) Top: blue cluster centred and ringed by rocks on all sides. -- UNMET - rocks show at left, back and front-right rims, but the high perspective top camera magnifies the tall crystals so the blue mass still hides most of the ring at the right and front-left.

## PARTS
13. [must] AzuriteMainCrystal ~3.2-3.5 x 2.8-3.2 x 7: fat faceted crystal, blunt point, slight lean, same function as the hero. -- MET - parts cell: fat faceted crystal like the reference; 4.1 x 3.2 x 7.0 (a bit wide).
14. [must] AzuriteSideCrystal ~2.4 x 2 x 4.5, same shape language. -- MET - 2.8 x 2.5 x 4.6, smaller tilted twin of the main.
15. [must] AzuriteBaseRock: big low faceted mound plus a separate small rock to its right. -- MET - parts cell: large faceted mound and a separate small rock at its right.

## DROPS / DEPLETED
16. [must] Two drops: chunky faceted blue shards ~1-1.5 studs, one lying diagonally, one in another pose; closed, <=300 tris. -- MET - drop A lies diagonally, drop B tilted upright; 44 tris each.
17. [must] AzuriteDepleted ~7 x 4.5 x 2.6: large boulder with one small rock left and one right, no crystals. -- MET - depleted cell: big boulder flanked by two small rocks (deplete haze overlays it).
18. [should] (verifier) Depleted rocks use the same faceted style as the hero boulder. -- MET - same subdiv-1 large-plane rock style on hero, base rock and depleted.

## PALETTE / MATERIAL / VFX
19. [must] Crystals single key r03_azurite (#1C8EDB) render saturated cyan-cobalt with pale lit facets. -- MET - crystals read saturated cyan-blue with pale highlights like the reference.
20. [must] Rocks single key r03_rock (#8C7E78) render warm grey-taupe. -- MET (lit faces) - lit faces match reference taupe; shadow faces render a little darker/browner. The key is shared by the sheet, so it stays unchanged.
21. [must] Sockets: ore_glint on the main gem (0,-1.5,5) x0.8, harvest_hit (0,-2.5,3) blue, harvest_deplete at depleted base, blue PointLight + motes. -- MET - glint sparkle sits on the main crystal face above the boulder; hit burst on the boulder/crystal front at mid height; deplete burst at the base.
22. [should] (verifier) VFX placement sits on rendered geometry, not in empty air. -- MET - glint on the main crystal surface, hit at the boulder top front.
23. [should] 0 problems and hero <= 3500 tris. -- MET - 0 problems, hero 400/3500.

## Iteration log
- Builds 1-5 (previous run): see verifier report; slim crystals, round dome boulder, 9.0 wide.
- Rev build 1: radii +20%, 8 sides, flatter-sided profile, subdiv-1 faceted rocks, rocks pulled inside +/-4. Crystals became blobby and too fat; boulder too low; top view still a blob.
- Rev build 2: radii back a bit, 4-ring profile (prism + blunt point), taller boulder, front-corner rocks added. Found the Z spin was swinging the left crystal's lean forward over the boulder.
- Rev build 3: lean set by X/Y with small Z spin, so leans point sideways; boulder 4.4 high. Front/hero much closer.
- Rev build 4: wider lower boulder (6.2 x 4.0), right crystal leans forward (side view now right), less left lean, ring rocks pushed outward. Hit the 4-build cap with the top-view ring (12) still UNMET.
