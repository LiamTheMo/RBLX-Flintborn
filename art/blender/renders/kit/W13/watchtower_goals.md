# W13 Watchtower goals

Status per goal: MET / UNMET (judged by eye against the reference row, after build 4 of the revision).

## ASSEMBLED / HERO
1. [must] Silhouette: chunky four-leg tower, body ~2.2x taller than wide (body ~13 wide, tip ~30), legs open underneath, roof as wide as body plus overhang. — MET - chunky 2.0 posts splayed out to the stones; stocky stance now close to the ref; tip 30.4, body ~13 wide
2. [must] Roof is a low, wide cream pyramid, 4 faces to one tip, ~1.5-2 stud overhang past the posts, slightly drooped eaves, eave-to-apex rise ~5 studs. — MET - rise 5.5 over half-width 6.6; reads as the ref's moderate pyramid, not a steep cone; drooped edge midpoints visible
3. [must] Wooden finial on the roof tip: block + ball knob + point cap, ~2.5-3 studs tall. — MET - block, ball and point visible on every tower
4. [must] Four chunky square posts (~2.0 stud) with slight inward taper, continuing above the deck as roof posts, chunky bolted cap blocks at the deck joint and rail top. — MET - thick posts, cap blocks with bolt heads at deck and rail-top heights visible in hero and front
5. [must] X bracing (beams ~1.0 wide) on every face, two stacked levels, horizontal cross beams at bottom, mid and under deck, bolt block at each X centre. — MET - two X levels with cross beams on front and side
6. [must] Four grey chamfered stone footings (~3.6x3.6x2.0), clearly chunky under each post and set outward. — MET - big grey blocks under each leg in hero, front, side and variants (not visible in the top view, see 13)
7. [must] Open deck with railing (top rail, mid rail, balusters) at ~55% height; front rail has a gap above the ladder. — MET - railing on all sides, front gap at the ladder top-left
8. [must] Red swallowtail banner with cream diamond hanging on the front below the deck with a crossbar. — MET - centred on the front, z ~8-15
9. [should] Ladder from ground to deck, leaning, ~2.4 wide, rungs every 1.2, thick rails. — MET - ladder reaches the deck edge left of the banner, leaning ~2 studs; reference draws it centred under the banner, ours sits left so it does not cover the banner
10. [should] Base dressing: rubble stones, leafy green clumps, grass tufts, flower dots around the footings in hero and variants. — MET - green clumps, grass spikes and grey rubble visible at the base of every tower (small at cell size)

## FRONT
11. [must] Front view: symmetric tower, roof the widest element, banner centred, legs splay slightly to the stones. — MET - symmetric with splayed legs; ladder offset left (documented)

## SIDE
12. [must] Side view: X-brace tower with roof and finial, no banner, ladder slant at the front. — MET - side shows braces, roof and ladder slant; roof face reads darker here (lighting from behind)

## TOP
13. [must] Top view: cream roof with 4 ridge lines and a central knob, stones peeking out at the corners, grey frame visible. — UNMET - ridge lines and central knob show, but stones/frame stay hidden: the top cell uses a perspective camera ~35 studs above the roof, which magnifies the roof (z 21) relative to the stones (z 0-2) by ~1.6x, so stones 1.4 studs past the eaves are still covered. Needs an orthographic top camera (shared lib).

## PARTS
14. [must] Nine separate parts: RoofTip, CanvasRoof, Railing, DeckFloor, Post, Bracing, Banner, Ladder, BaseStone. — MET - all nine in the parts cell
15. [should] Deck floor shows ~7 distinct planks with gap lines. — MET - DeckFloor part now shows separate planks with dark gaps and alternating heights
16. [should] Parts hovering in an exploded arrangement like the reference. — UNMET - the runner lays parts out in an automatic grid on the floor; not controllable from the module

## VARIATIONS
17. [must] A Short Tower: ~20-22 tall, one bracing level, banner + ladder, lower deck. — MET - 22.2 tall, one X level, banner, ladder to the deck
18. [must] B Tall Tower: ~40 tall, narrower, three bracing levels, banner, long ladder. — MET - 41.7 tall, three X levels, narrower legs, ladder to the high deck
19. [must] C Damaged Tower: torn roof side with bare beams sticking up, missing railing, broken brace, shorter tattered banner, moss and green sack at base. — MET - torn left roof with rafters, missing right rail, stub front rail, jagged short banner, moss on stones and green sack

## PALETTE / SCALE
20. [must] Timber w13_timber #A9612C saturated orange-brown on all wood. — MET - rich orange-brown on posts, planks, ladder, finial
21. [must] Canvas w13_canvas #E6D2A4 renders as muted beige/cream on roof and emblem, no yellow cast. — UNMET - the sheet palette value renders pale yellow-cream next to the ref's beige; the key is fixed sheet-wide so the module cannot change it (request filed)
22. [must] Stone w13_stone #8A9199 grey on footings and rubble; banner w13_banner #C3262A red; moss w13_moss #4C9A3C on base clumps/grass and damaged moss. — MET - grey footings, red banner, green clumps
23. [should] Scale: deck ~z16.5, rail top ~z20, eaves ~z21.4, tip ~z30; tower body ~13x13 (dressing spreads the bbox to ~17.8). — MET - tip 30.4; body within spec; bbox larger only because of the dressing and ladder lean

## Iteration log
1-4 (first run): parametric tower, parts and variants; roof steepened; stones enlarged.
Revision build 1: posts 2.0, braces 1.0, stones 3.6x2.0 offset outward, roof half 6.8 / rise 4.5, deck gaps 0.3 with alternating heights, ladder to deck (2.4 wide) left of the banner with front rail gap, base dressing (rubble, clumps, grass, flowers). Tower now chunky; roof too flat; top view still hides stones.
Revision build 2: splayed legs (half 5.3 -> 4.4), stones further out, post-top cap blocks poking through roof corners. Top view gained brown corner squares but iso showed ugly horns.
Revision build 3: smaller caps; still horn-like in iso.
Revision build 4: caps sunk under the roof, roof rise raised to ~5.5 so it reads as the ref's pyramid; tip 30.4. Top-view stones remain hidden by the perspective top camera; canvas yellow cast is the fixed palette.
