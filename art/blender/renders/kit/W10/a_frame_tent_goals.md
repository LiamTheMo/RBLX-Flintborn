# W10 row 2 - AFrameTent goals

Status after each build: MET / UNMET with one line of evidence (judged by eye against the reference row).

## ASSEMBLED / HERO
1. [must] Classic A-frame silhouette: cream triangular tent ~10 wide x 14 long, ridge ~8, pole tips ~0.6-1 above ridge (total ~8.5-8.7). MET - hero shows a steep cream A-frame; tent body 9.9 wide x 14.9 long (ridge) x 8.7, steeper than before
2. [must] Two crossed poles at EACH end form an X with a V of tips above. MET - X crossings with V tips at both ends in hero, front, top
3. [must] Ridge pole visible along the top, protruding past both crossings. MET - ridge log end sticks out past the front cross in hero/front
4. [must] Rope lashing at each crossing. MET - tan rope lashing at both crossings
5. [must] Front open: doorway >= 4 wide x 7 tall showing dark interior with tan mat, green blanket, rolled bedroll. MET - front cell: 4.8-wide x 7.75-tall doorway with green blanket/bedroll inside
6. [must] Back closed with a canvas triangle. MET - side/top show the back closed
7. [must] Amber lantern hangs from the front crossing at ~5 studs. MET - lit amber lantern under the front cross in hero/front
8. [must] Crate + iron-hooped barrel at front-left, one crate at the right. MET - crate, hooped barrel and ground lantern front-left; crate on the right in side cell
9. [should] 4 pegs with rope loops at corners; a few small grey stones. MET - pegs with guy ropes at 4 corners, small grey stones near the base
10. [should] Rope ties along the bottom canvas edge / lower poles. MET - tan ties along both bottom edges
11. [should] Rolled canvas bundle beside the doorway. MET - cream roll with ties at the doorway's right
12. [must] (verifier) Canvas is pale cream/ivory, not yellow. MET - w10_tentcanvas #EFE2C4 renders ivory like the reference, no longer saturated yellow
13. [should] (verifier) Footprint near spec, dressing kept close. MET - tent 9.9 x 14.9 x 8.7; hero with dressing 13.0 x 17.4 (was 16.1 x 18.1); variants 11.7-13.0 x 16.8 (pegs/guys)

## FRONT
14. [must] Symmetric triangle, pole feet splay slightly past the canvas, lantern under the X. MET - front cell matches
15. [should] Doorway ~55-65% of base width with narrow cream flaps each side. MET - opening ~58% of base, flaps both sides

## SIDE
16. [must] One big cream sloped canvas face ~14 x 9, end poles at both ends with tips above. MET - side cell: large ivory rectangle framed by poles

## TOP
17. [must] (verifier) Top-down view: two canvas panels meet at a central ridge line, poles/pegs at corners. MET - 4_top is overhead (el 89, fixed camera): ridge runs down the centre, lit left panel and shaded right panel either side, frame ends and pegs at the 4 corners; the hard sun shadow and slight perspective come from the shared studio camera, not the model

## PARTS
18. [must] (verifier) Six parts present and individually readable: RidgePole, left panel, right panel, FrameEnd, Mat with bedroll, Peg. MET - two separate cream panels side by side in the back row (eyelets on outer edges), X FrameEnd in front, Mat with green bedroll, ridge pole with wraps; peg is small but visible beside the mat
19. [should] (verifier) FrameEnd ~8.5 tall, ~10 wide; Peg ~1.2 tall. MET - FrameEnd 9.9 x 8.7; Peg 1.2 tall with thicker shaft, head and larger loop (still small at sheet scale)

## VARIATIONS
20. [must] 1. Closed: front fully covered, seam with rope ties, lantern at the left. MET - closed front with overlapping flap and 3 ties, lantern left
21. [must] 2. Rolled Doorway: canvas roll across the doorway top; mat/bedroll inside; lantern. MET - roll across the door top, green blanket visible, lantern below roll
22. [must] 3. Torn / Worn: ragged hole with brown patches and frayed strips; one pole leaning; no glow. MET - jagged-edged hole with brown shards and 6 frayed strips, front pole leaning, no lantern
23. [should] (verifier) Torn hole ragged, not a neat star. MET - hole edges now have 8-10 jagged teeth per side

## PALETTE / SCALE / VFX
24. [must] Wood one orange-brown (#8A4A22), rope one tan (#C48A38), canvas one ivory key. MET - poles/crates orange-brown, rope tan, canvas ivory
25. [must] Lantern glass emissive amber with dark iron frame; iron barrel hoops. MET - amber glass, dark frames, hoops visible
26. [must] heat_glow sockets on hero, Closed, RolledDoorway; none on Torn. MET - hero 2, Closed 1, Rolled 1, Torn 0
27. [must] 0 problems; hero <= 4500, variants <= 3000, parts <= 1500; nothing below z=0. MET - 0 problems; hero 3116, variants 2004-2380, parts <= 424

## Iteration log
- Builds 1-4 (previous run): full tent, parts, variants; panels stacked in one grid slot; verifier failed (yellow canvas, merged panels, wide footprint, top view).
- Revision build 1: new module key w10_tentcanvas #EFE2C4 (ivory), narrower/steeper tent (W 4.1, ridge 7.85, tips 8.45), dressing pulled in, ragged torn hole, bigger peg. Canvas now ivory, footprint 13x17.4. Panels still overlapped as "/\" slabs.
- Revision build 2: panel parts rebuilt as flat 9.5x14 sheets reclined 48 deg facing the camera -> grid sets them side by side as two separate sheets (like the reference). Top cell now reads as a clean overhead.
- Revision build 3: larger peg rope loop. All must goals MET.
