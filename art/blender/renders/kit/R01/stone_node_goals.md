# R01 row 1 - StoneNode goals (revision 5)

Reference: art/reference/kit/rows/R01_row1.png (and the full sheet art/reference/kit/R01_stone_common_ores.png).
Studs: 1 unit = 1 stud, character ~5.5. The compare camera is a close perspective (front cell elevation 6), so
cells read a little taller than the near-orthographic reference. Goals are judged by eye against the reference cell
directly above; KITSTAT studs are support only.

Revision 5 brief: the verifier failed revision 4 (resemblance 6.3): the hero read as a tall barn-like bun (~1.15:1,
walls steep to ~80% height), only ~8-10 low-contrast planes read, the crown read central, and the side was a
tombstone column. A zoomed crop of the reference front cell shows a GEODESIC boulder: a broad ellipsoid cut flat
at the ground, walls near vertical through the lower third (widest at ~25-30% height), then a dome curving in
steadily in 3 facet tiers to a crown left of centre. Revision 5 rebuilt the main rock on that model.

## REVISION 5 VERIFIER GOALS (must)
25. [must] (V5) HERO/FRONT: broad planted dome: front cell reads about 1.3:1 W/H (6.3 x 4.7); near-vertical walls through the lower part, then the outline curves in to the crown. - UNMET (improved): the front cell is now a dome that curves in from ~40% height on the right and has a long sloping right shoulder (no barn lid), but by eye it still reads ~1.15:1 (204 x 179 px), not 1.3:1, and the left side stays near vertical to ~60%. Studs are 6.2 x 4.2 x 4.8 (1.29:1). Build cap reached before a further widen/lower pass.
26. [must] (V6) HERO/FRONT: 14-18 clearly separate large flat planes readable in the front cell, long straight ridges, no tall near-coplanar wall slabs. - MET (low contrast): a 3x zoom of the front cell shows ~14 separate planes in a geodesic pattern (top face, crown facets, upper ring, two lower diamond tiers, dark right flank) meeting at straight ridges; the old single tall front slab is gone. Light/dark steps are softer than the reference's (studio lighting, no painted rim highlights).
27. [must] (V7) HERO/FRONT: crown visibly left of centre in the front and hero cells, with a long shoulder falling to the right. - MET: front cell apex at ~35-40% of the rock width from the left with a long right shoulder sloping down to the right wall; hero cell shows the same leftward lean.
28. [must] (V8) SIDE: upright egg, narrower than the front, profile narrowing toward a rounded crown. - MET: side cell is an upright egg/bullet, clearly narrower than the front, narrowing from ~35% height to a rounded faceted top; no parallel tombstone sides.
29. [must] (V9) TOP: polygonal outline, crown left, supports peeking out; hero D <= 4.7. - UNMET (partly): outline is polygonal with big planes and hero D is 4.5, but the crown offset is hard to see from straight above and the supports peek out lower-left, lower-right and upper-left, while the reference top shows one at the upper right and one at the lower left (the spec places the third support back-LEFT, which conflicts with the reference top view's upper-right one).

## ASSEMBLED / HERO
1. [must] Main rock ~6.3 W x 4.3 D x 4.7 H studs; hero bbox with supports ~6.4-6.8 W x 4.5-4.7 D. - MET (within 0.1 stud): main rock 6.2 x 4.2 x 4.8, hero 6.9 x 4.5 x 4.8 (W 0.1 over the range because the front supports were moved out of the wall).
2. [must] Few big flat chisel planes (not a noisy icosphere): ~30 planes in 5 rings, long straight ridges. - MET: 30 cut planes + cap (108 tris); hero and front cells show big unequal planes, no small noisy facets.
3. [must] Hero cell reads as a broad faceted DOME, wider than tall, curving in to a crown; not a tombstone with a flat lid. - MET: hero cell shows a dome leaning left with a long right shoulder; wider than tall (but see V5 for the ratio).
4. [must] Near-vertical lower walls, flat planted base, lower flanks do NOT tuck in. - MET: front and hero cells show vertical lower walls standing on a flat base; no tuck.
5. [must] Crown sits left of centre. - MET: see V7.
6. [must] Three low flat-topped angular support rocks (~1.4-1.6 W x 0.8-1.0 H) against the foot at front-left, front-right and back-left. - MET: front cell shows flat-topped lumps at both lower corners, now standing clear of the wall; the back-left one shows in the top cell at the upper left.
7. [must] Origin bottom centre, nothing below z=0, front faces -Y. - MET: runner 0 problems; strike socket on -Y.

## FRONT
8. [must] Front cell: support rocks at both lower corners, the dome fills most of the cell and is wider than tall. - MET: both supports visible at the corners; dome wider than tall (ratio: see V5).
9. [should] A broad strike face on the front (-Y) at mid height where the harvest_hit socket sits. - MET: harvest_hit sprite sits on a front facet at z 2.4.

## SIDE
10. [must] Side cell reads as an upright egg: narrower than the front, depth < height, faceted rounded top. - MET: see V8 (4.2 D < 4.8 H).
11. [should] Side cell shows support rocks at the foot. - MET (partly): the front-right support shows at the front foot.

## TOP
12. [should] Top cell: polygonal outline with ~8-10 corners and big planes, supports peeking out. - MET: angular outline of big planes, three supports poking out; the studio sun casts a long shadow.

## PARTS
13. [must] StoneNodeMainRock is exactly the hero's main rock mesh, hull collision. - MET: both from main_points(), 108 tris, hull.
14. [must] StoneNodeSupportRock: low flat-topped angular rock ~1.6 x 1.6 x 1.0, hull. - MET: parts cell shows a squat lump with leaning walls and a flat top; 1.6 x 1.5 x 1.0, 40 tris.

## DROPS / DEPLETED
15. [must] StoneChunk ~1.3 x 1.0 x 0.85 angular wedge with a broad flat face to a sharp ridge, chamfered ends; box, <=300 tris. - MET: drops cell wedge; 1.3 x 0.9 x 0.8, 32 tris, box.
16. [must] StoneChunkB ~1.4 x 1.3 x 1.0 rounder faceted lump with a small flat top; box, <=300 tris. - MET: drops cell rounder lump; 1.4 x 1.3 x 1.0, 44 tris, box.
17. [must] StoneNodeDepleted ~6.8 W x 4.7 D x 2.3 H: a low, wide broken mound with sloping faceted flanks; hull. - MET: depleted cell low wide mound; 6.9 x 4.6 x 2.3, 240 tris.
18. [must] Depleted: small angular rocks clustered at BOTH ends. - MET: flat-topped rocks at both the left and right ends.
24. [should] Depleted top: broad flat mined-off plane, broken by a couple of notches. - MET (subtle): one broad flat top; two notch planes now clip its front-left and back-right top edges (small in the cell).

## PALETTE / VFX
19. [must] ONE colour per material: only r01_stone ("#877C78"); Tint a small random per-plane jitter (+/-4%), never by direction. - MET: runner 0 problems.
20. [must] No water, foam, mist, smoke or steam meshes. - MET: none.
21. [should] Rendered stone tone matches the reference's warm grey. - MET: same warm grey, no pink/blue cast.
22. [must] harvest_hit on the front (-Y) face at z ~2.4 with chips #AA9E99/#635F60 and dust #C9C0BA/#A39A95; harvest_deplete at (0,0,0.25), same colours; no ore_glint; no VFX on parts/drops/depleted. - MET.
23. [should] Budgets: hero <=3000, parts <=1500, depleted <=2000, drops <=300. - MET: hero 228, main 108, support 40, depleted 240, drops 32/44 (692 total).

## Iteration log
- Revisions 1-4: see git history; rev 4 ended as a 24-plane ellipsoid-tangent dome that read barn-like (failed, 6.3).
- Rev5 build 1: walls to 2.5 (x) / 1.1 (y), elliptic dome, peak -1.25, rings at el 4/30/55/80. Front became a box with a lid and one big front slab - worse.
- Rev5 build 2: planes now placed at chosen HEIGHTS on a target surface along its normal (surface_planes), so rings spread evenly on a non-spherical rock. Still boxy.
- Rev5 build 3: 5 staggered rings, y dome exponent 1.6: side became an egg; front got triangular facets but the crown lean made the left side a vertical cliff.
- Rev5 build 4: lean starts at the x wall top, walls lean 10%: left side curves, but the top read as a flat lid (barn).
- Rev5 build 5: rebuilt on the reference's geodesic model (zoomed reference crop): ellipsoid cut at the ground, x dome from 1.2, y dome from 0.9, peak -0.9, rings at ~0/22/45/65 deg plus a small top face. Front became a dome leaning left with a long right shoulder; supports moved out of the wall.
- Rev5 build 6-7: sizes trimmed (6.2 x 4.2) and a crown cap plane added (4.9 -> 4.8 H). Build cap exceeded (7 builds); V5 (front cell ratio ~1.15 by eye) and V9 (top-view support positions) remain open.
