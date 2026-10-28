# R06 SoftwoodLog goals

Reference: art/reference/kit/rows/R06_row1.png. Status column filled after each build.

## HERO (assembled, front-left iso)
1. [must] Chunky fallen log lying along X, ~14 studs long, ~5.5 diameter: length/diameter ~2.5:1, reads wide and chunky, not skinny. — MET: hero and side cells show a long, thick log; the front cell is foreshortened by the 24 deg yaw but still reads chunky
2. [must] Cross-section is a faceted 9-10 sided cylinder; bark shows large chiselled facets along the length (several facet bands), not a smooth tube. — MET: 10 sides, 7 length bands, jitter 0.13; chiselled facet patches are visible along the length in the hero and side cells
3. [must] Front-left (-X) end is cut flat and pale (r06_cutwood) with 3-4 concentric octagon rings in the same colour, a thin bark rim around it; it is the brightest focal point of the cell. — MET: hero yaw 24 deg plus azimuth -20 shows the -X end as a big pale octagon disc at the left, the brightest thing in the cell
4. [must] Tall angled branch stub (~3.5 studs) rises from the top-back, leaning, with a pale cut tip. — MET: thick stub leaning right from the top-back, pale tip, ~1.6x the log height
5. [must] Short stub (~2.5 studs) pokes out of the front-bottom toward the viewer/down, with a pale cut tip close to the ground. — MET: short stub from the front-bottom down to the ground, pale tip
6. [should] A small extra nub sits on the top behind the tall stub (as in the reference hero/top/main-log). — MET: small nub behind the tall stub in hero/front/top
7. [must] Bright green leaf clumps (5-6 pointed leaves each): one at the front base near the short stub, one at the front-right base, one on the top-right; ground clumps sit on z=0. — MET: tufts 1.4x larger; front-left tuft sits clear of the stub under the disc, plus right base and top-right
8. [should] Far (+X) end also shows a pale cut ring (visible in side/top views). — UNMET (hero): the +X ring shows in the side and top cells but faces away in the hero, as it does in the reference hero
9. [must] Log rests on the ground with a flat underside, nothing below z=0. — MET: flat underside on the ground, 0 problems

## FRONT / SIDE / TOP
10. [should] Front/side views: two stubs read clearly above the log silhouette at different heights. — MET: front and side show the tall stub and the nub above the log at different heights
11. [should] Top view: long log diagonal-ish bar with stubs sticking out to one side and leaf clumps on both sides of the log. — MET: top view shows a diagonal bar like the reference, stubs to one side, tufts on both sides

## PARTS
12. [must] SoftwoodLogMain: bare ~14 long log, both ends pale cut with rings (only the tiny top nub allowed). — MET: bare main log (tiny nub only), ~14 long, pale octagon end
13. [must] SoftwoodLogBranchStub: short ~3 stud angled stub, bark sides, pale cut tip, angled flat base. — MET: short angled stub, flat angled base, pale tip
14. [must] SoftwoodLogCutEnd: flat octagonal disc ~5.5 across, ~0.4 thick, all r06_cutwood with visible concentric octagon rings. — MET: upright pale octagon 5.5 x 5.5 with deeper stepped rings

## DROPS / DEPLETED
15. [must] SoftwoodLogWoodWedge: one long (~2.5) triangular wedge, pale cutwood faces with a bark back face; reads like a split piece of firewood. — MET: tapered split-wood wedge 2.5 long x 1.4 tall; the trapezoid end faces the camera, pale split faces, brown bark strip on the top edge
16. [must] SoftwoodLogBranchStick: two thin bark sticks crossed in an X, ~3 long, pale cut ends. — MET: two crossed bark sticks with pale ends, thinner than the reference
17. [must] SoftwoodLogStump: short broken stump ~3.5 wide x 2.5 tall, bark sides, jagged splintered pale top, two small leaf clumps at the base, flat on the ground. — MET: jagged stump 2.5 tall with pale splintered top and two base tufts; footprint pulled in to 4.6 x 3.7

## Palette
18. [must] Bark = r06_softbark #8A5B3E (warm mid brown) on log, stubs, sticks, stump sides; render reads warm brown like the reference, not grey. — MET: bark renders warm mid brown like the reference
19. [must] Cut wood = r06_cutwood #E0B27C on all end caps, stub tips, wedge, cut-end disc, stump top; reads pale tan. — MET: ends, tips, disc, stump top and wedge render pale tan
20. [must] Leaves = r06_leaf #3F9A2C saturated green, not washed out. — MET: leaves render saturated green

## Scale / tech
21. [must] Budgets: hero <=4000, parts <=1500, drops <=300, depleted <=2000 tris; build ends with 0 problems. — MET: hero 688/4000, parts <=404, drops <=64, stump 152; 0 problems
22. [must] VFX: harvest_hit on the -X cut end at mid height (cutwood chip colour); harvest_deplete at base centre; no glint/light. — MET: harvest_hit on the yawed -X cut end at z 2.7 (computed after the yaw and origin shift) with chip colours; harvest_deplete at (0,0,0.5)

## Iteration log
- Build 1: faceted loft log, stepped ring discs, leaf_cluster clumps. Stump was flagged for painted lighting (cutwood vs bark family); waiver added. Leaves were tiny blobs, stubs were thin.
- Build 2: thicker stubs, bigger leaves, hero yawed 34 deg. The hero became foreshortened; the leaves were still blobby.
- Build 3: custom pointed-leaf tufts (they read like the reference); bevelled ring steps make the rings visible; yaw 22.
- Build 4: yaw 6 (log reads long now, but the cut end is almost edge-on), wider leaves, wedge taller and rotated -30. Still a slab.
- Earlier run, build cap (4) reached. Open: #3 needs a hero yaw of about +12-14 deg (between builds 1 and 4). #15 needs the bark face on the camera-visible side, or a rotation so the triangular end faces -Y.

## Revision goals (verifier fail, 5.5/10) — added as must unless noted
23. [must] HERO: pale ringed -X end is a large, clearly visible focal disc with 3-4 rings, ~30-45 deg to camera. — MET: big pale octagon disc at the left of the hero at about 45 deg; 3 stepped octagon ring outlines visible, lower contrast than the reference because the end is strongly lit
24. [must] HERO: 3+ leaf clumps (front-left base, right base, top-right), pointed 5-6 leaves, each about the reference size (~1/4-1/3 of the log diameter tall, ~3 studs across); front-left clump not hidden by the stub. — MET: four pointed 6-leaf tufts about 3 studs across: front-left base under the disc (clear of the stub), right base, top-right and back-right; similar size to the reference
25. [should] HERO: far +X end shows a pale cut ring. — UNMET: with the -X end turned to the camera the +X end faces away; it shows in the SIDE and TOP cells. The reference hero does not show it either
26. [must] FRONT cell: the ringed cut end faces the camera (clearly visible disc) and both stubs sit above the log. — MET: FRONT cell shows the pale ringed -X disc at the left at about 66 deg, with the tall stub and the nub above the log. The reference draws it mirrored (disc at right); the front camera is fixed at az 0, so the mirror is not possible
27. [must] SIDE cell: long side view of the log with an end disc seen obliquely at one end (reference SIDE), not an end-on view. — MET: SIDE (az 54) shows the log long and horizontal with the +X pale ringed end visible obliquely at the right, like the reference SIDE
28. [must] DROP: SoftwoodLogWoodWedge reads as a split-wood wedge ~2.5 long, ~1.4 tall, triangular end visible, pale cut faces + bark strip on the back/top edge. — MET: wedge-shaped prism narrowing to a bark-strip top; reads as split firewood, not a slab
29. [should] Bark: more pronounced chiselled facets (10 sides, stronger jitter, more length segments). — MET: 10 sides with stronger jitter; facets read as large chiselled patches
30. [should] SoftwoodLogCutEnd ~5.5 across flats with deeper stepped rings that read clearly. — MET: 5.5 x 5.5 across with ring steps 0.1 apart
31. [should] SoftwoodLogStump footprint about 4.5-5 wide (spec 3.5 + tufts), not 5.9. — MET: 4.6 x 3.7 footprint

## Revision iteration log
- Rev build 1: hero yaw 6 -> 30 at azimuth -18 (disc now faces the camera; front cell shows the disc), SIDE_AZIMUTH 45, tufts 1.4x larger with the front-left tuft moved clear, 10-sided log with jitter 0.13, wedge rebuilt as a tapered prism with a bark top, CutEnd 5.5 across with deeper rings, stump pulled in. The hero log looked a little foreshortened and the side cell hid the end disc.
- Rev build 2: yaw 24, azimuth -20 (log reads longer), SIDE_AZIMUTH 54 (right end disc visible), taller and more tapered ring steps, narrower wedge top.
- Rev build 3: ring steps raised again (0.12-0.54) with a 0.72 taper; ring outlines are faintly better. All must goals are met. Stopped.
