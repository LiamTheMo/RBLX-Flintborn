# W14 CaveEntranceRing goals

Revision after verifier FAIL (4/10). Judged by eye against the reference row after build 7 (3rd build of this revision).
Verifier goals were added as V1-V11 (all must except V8).

## ASSEMBLED / HERO
1. [must] Arch reads as distinct chunky boulders stacked around an open mouth (slab walls + cap + crown). — MET: hero cell shows 2 slab walls, shoulder rocks, big cap and 5 crown rocks, each distinct.
2. [must] V1 Tall arch ~32w x ~24h with a clear 14x12 walk-through opening, dark hollow behind. — MET: 32.9 x 30.3 x 23.8; front cell shows a wide open mouth, back closure pushed to y>=+8 and below z=8 so it reads as a dark recessed back wall, not a plug.
3. [must] V2 Left/right walls are tall angular slab pillars leaning inward, distinct from the crown. — MET: hero/front show tall slab verticals on both sides, tops leaning in; crown sits on them.
4. [must] V3 Ceiling rock is the largest flat-topped faceted boulder capping the arch. — MET: front and hero cells show one wide flat cap clearly bigger than the crown stones.
5. [must] V4 Biggest boulder at outer front-left foot, smaller rubble at feet. — MET: a ~7-stud boulder stands clear in front of the left wall (hero and front cells), 2-3 stud stones elsewhere.
6. [must] Interior shallow hollow with sand floor continuing inside. — MET: sand plate visible inside under the arch.
7. [must] Chunky large facets, no noisy small ones. — MET: each rock shows a handful of big planes.
8. [should] 2-3 spiky green fern fans at wall feet and apron edge, about reference size. — MET: 3 fans, ~1.4x larger than before.

## FRONT
9. [must] Front: two vertical slab walls, cap across the top, opening wider than half the ring. — MET: front cell shows this; the opening top is flatter than the reference's rounded arch.
10. [should] Sand apron wider than the opening, spilling forward with plate gaps. — MET.

## SIDE
11. [must] V7 Side view: legible deep profile, crown stepping back, pillars readable, not black. — MET: side cell (now from the lit side, SIDE_AZIMUTH -70) shows front slab, back slab and crown in warm grey.

## TOP
12. [should] V8 Top: ring of boulders around an open floor with fan apron in front. — UNMET: straight-down view shows the cap/crown covering the hollow (a roofed cave); the fan apron reads.

## PARTS
13. [must] Five parts: CeilingRock 16x12x7 flat-topped, LeftWall ~6x6x18, RightWall ~6x6x17, FloorSill ~24x14x1.2 plates+pebbles, Rubble 3-4 stones. — MET: 16.3x12.5x7.0 flat top; walls are tall angular pillar clusters leaning in; sill 23x14 plates; 4 rubble stones.
14. [should] Walls in the parts cell read as tall angular crystal-like slabs as in the exploded view. — MET.

## VARIATIONS
15. [must] V9 A Rounded: taller rounder arch, 12x13 opening, semicircular crown. — MET: variant 1 shows a round ring of boulders over a tall narrower opening, no flat cap.
16. [must] V10 B Wide: ~20 wide x 10 tall opening, pillars at outer edges, extra top boulder. — MET: variant 2 is visibly wider and lower than the hero with a long low cap and one boulder on top.
17. [must] V11 C Split: central pillar and two doors under a lintel. — MET: variant 3 shows a long lintel on a central pillar with two doorways either side.
18. [should] Every variant has sill + ferns, within budget. — MET: 1292-1408 tris each.

## PALETTE / SCALE
19. [must] V5 w14_rock one key, renders warm light grey-mauve, side not black. — MET: lit faces render warm grey (~#9E928C), shadows plum-grey; the old darkness was self-shadowing geometry, which is gone. Slightly darker than the reference's lit highlight.
20. [must] V6 w14_sand pale tan, w14_moss saturated green, one key each, no painted shading. — UNMET for sand: renders orange-tan vs the reference's paler tan. The sheet palette (#C79B6C) must be copied verbatim into all four W14 modules and the sheet build takes the last module's values, so this module cannot change it alone; requested as a sheet-wide change (#C9A983). Moss MET.
21. [must] Tris within budget, 0 problems, nothing below z=0. — MET: hero 1546/6000, 0 problems.

## Iteration log
- Builds 1-4 (earlier run): generic elliptic boulder arc; verifier failed it (squat dome, clogged opening, black side).
- Build 5: rebuilt as slab walls + shoulder rocks + flat-capped cap + crown; low back closure; ferns 1.4x; SIDE_AZIMUTH -70. Rock now light. Slabs too thin/spiky (subdiv 1).
- Build 6: walls rebuilt as chunky stacked slabs (subdiv 2) on all assets; more crown rocks. Split pillar invisible, crown rocks floating above lintel.
- Build 7: split pillar as a 6-sided faceted column with a foot rock; crown rocks seated on the lintel; back closure pushed to y~10.4-11; front-left boulder 7 studs at x~-14.4. All must goals met except the sand tone (sheet palette lock).
