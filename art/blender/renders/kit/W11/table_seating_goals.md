# W11 TableSeating goals

Reference: art/reference/kit/rows/W11_row1.png. Status after build 3 (by eye, compare image).

## ASSEMBLED / HERO
1. (must) Picnic table with TWO benches, one each long side, parallel and lower than the table. [MET: both benches flank the table, seats at about half table height]
2. (must) Overall ~10 x 9 x 3.2 studs; top at 3.2, bench seat top ~1.6. [MET: 10.2 x 8.3 x 3.3; hero cell proportions match the reference cell]
3. (must) Table top reads as 4 thick planks along x with visible gaps and uneven ends. [MET: 4 planks with dark gap lines and staggered ends in hero and top cells]
4. (must) Two A-frame trestles near the ends: splayed legs, top cleat, diagonal brace. [MET: side cell shows the A with brace; legs visible under hero top ends]
5. (must) One crossbar along x between the trestles. [MET: crossbar visible in front cell between the end legs]
6. (must) Bench legs are thick blocky end legs. [MET: chunky square block legs at each bench end]
7. (should) Small dark 6-sided nail heads at plank/leg joints. [MET: dark hex studs over the legs on top planks, benches and trestle sides]
8. (should) Chunky timber proportions, no thin rods. [MET: all members 0.4-0.85 thick; reads chunky like the reference]

## FRONT
9. (must) Wide low silhouette, bench strip in front at ~half height, crossbar with diagonal braces visible between end legs. [MET: build 2+ crossbar/braces show above the bench like the reference front]

## SIDE
10. (must) A-frame trestle (wide feet, narrow top) with diagonal brace; bench ends either side lower. [MET: side cell shows A-frame + brace with bench blocks both sides]

## TOP
11. (must) 4 table planks with gaps along x plus a bench strip each side. [MET: top cell shows 4 gapped planks with a bench above and below]

## PARTS
12. (must) Four part assets: TableTop, TrestleLeg, Crossbar, BenchSeat. [MET: all four visible in the parts cell]
13. (should) Trestle part reads as an A with diagonal brace, face-on. [MET: build 3 splay makes the A read clearly]

## VARIATIONS
14. (must) Stool ~1.8x1.8x2, thick square seat, splayed legs, low stretchers. [MET: legs splay outwards to the feet like the reference stool; stretchers low]
15. (must) Long Bench ~7x1.6x2 with chunky end legs, nails. [MET: 7.1 x 1.6 x 2.1, block end legs, nails on seat]
16. (must) Workbench ~6x2.8, top ~3.2, back posts to ~5, shelf ~1.2, side braces. [MET (revised): see 23]

## PALETTE / MATERIALS
17. (must) All wood ONE warm orange-brown w11_wood. [see 21: overridden to #A2622A]
18. (should) Only w11_iron on nail heads; no other materials. [MET: two keys only]
19. (should) No ground dressing (reference row shows none). [MET: bare props as in the reference]

## Iteration log
- Build 1: first pass, 0 problems. Front view: crossbar/braces hidden behind bench; trestle part weak; stool seat too thick and nails oversized.
- Build 2: crossbar raised to 1.75, benches lowered to 1.55 and moved to y=+-3.45, chunkier trestle legs, thinner stool seat, smaller stool nails. Front now matches.
- Build 3: more leg splay on trestles (A reads clearly) and on stool. All musts met.

## REVISION (verifier fail, resemblance 6/10) - added musts
20. (must) HERO: trestle A-frames with diagonal braces and the crossbar visible under the top, chunky legs reading below the top; crossbar at ~1.0-1.2. [UNMET (partial): crossbar now at 1.1 and 0.8 thick, legs at x=+-3.6 show below the top in the hero cell, front cell shows crossbar + braces; but the hero camera still shows the A-frame end only obliquely and the near bench covers the lower legs, so the A does not read as clearly as the reference]
21. (must) COLOUR: w11_wood render matches the reference's browner honey tone (not lighter/more saturated orange); override to ~#A2622A. [MET: #A2622A renders browner/deeper than build 3; shadow sides match the reference, lit tops a touch darker than the reference honey]
22. (must) PARTS: four parts each legible; trestle leg face-on with a clear diagonal brace; crossbar chunky (~0.8x0.8) with tenons; tabletop clearly thicker/wider than bench seat. [UNMET (partial): crossbar 0.8x0.8 with tenons, top 0.9 thick vs seat 0.7 and 4 vs 2 planks; trestle face-on with brace. Only one leg can show: TrestleLeg is one asset per spec and the runner lays parts out]
23. (must) WORKBENCH: two separate tall back posts to ~5 with small cap blocks, NO spanning rail; X side braces thick enough to read. [MET: rail removed; two separate back posts to 5.0 with cap blocks; X braces 0.4 thick set proud, visible on the -x side but small at this angle]
24. (must) HERO table top ~0.9 thick (reads chunky like the reference). [MET: planks 0.9 thick; top reads chunky in hero, front and side cells]
25. (should) STOOL: smaller nail heads, seat ~0.45 thick. [MET: nail r=0.05 on stool, seat 0.45]
26. (should) LONG BENCH: end legs splay slightly outward, seat ~0.8 thick. [MET: end legs splay 0.25 outward, seat 0.8]
- Revision build 4: wood #A2622A, top 0.9 thick at z 3.2, crossbar 0.8 at z 1.1, thicker trestle legs, benches y=+-3.3 seat 1.5, workbench rail removed + capped posts, stool/long bench fixes. Colour now browner; hero still squat.
- Revision build 5: benches lowered to 1.3, workbench X braces proud. Small gain.
- Revision build 6: benches out to y=+-3.7 (reference top view shows a gap). Top view now matches the reference gap.
- Revision build 7: trestles to x=+-3.6 so the legs show near the table ends. Legs visible under the top ends; A-frame still only oblique in hero. Build cap (4) reached.
