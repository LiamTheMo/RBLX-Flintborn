# R06 RootCluster goals

Status after revision build 4 (build 8 overall; 0 problems, hero 2214/5000 tris, 11.5 x 10.4 x 6.5 studs).

## ASSEMBLED / HERO
1. [must] Broad low dirt dome ~11 x 9 x ~4, not a cone, tent or cube. — MET: hero cell reads as a wide low lumpy mound under the roots, about 1.8:1 width to height like the reference.
2. [must] Lumpy stony mound with many (20+) mid-size flat facets, not a smooth dome. — MET: 16 overlapping blobs plus pebbles; many chunky facets show between the roots (a bit more blocky than the reference).
3. [must] 4-5 THICK chunky roots (~1.8-2 visual thickness), sweeping fat arches draped over the mound, ends dipping to the ground. — MET: 5 roots about 2 studs thick sweep over the shoulders; front, front-right, back-right and back roots reach the ground.
4. [must] Each root end finishes in a pale chamfered cut tip; >=3 pale tips in the hero view. — MET: 4 pale tips visible (front-left, front, front-right, right).
5. [must] Roots cross irregularly near the top centre, some lying on top of others; layout asymmetric. — MET: the big front root lies over the left-right root at the crown, and the back-right root lies over it; the top cell shows a tangle, not meridians.
6. [must] 3 bright green pointed-leaf clumps: top centre, top right/back, left. — MET: three wide saturated clumps at the crown, back-right and left.
7. [should] 6-10 pebble bumps round the base (+ some on the upper mound), same r06_dirt. — MET: ~10 base pebbles visible in the front and side cells; the upper pebbles are mostly hidden by roots.
8. [should] Overall ~6.5 high, ~11-12 wide; lower, wider, lumpier outline, not an igloo. — MET: 11.5 x 6.5; the hero and front cells show a wide rounded outline. The side outline is still slightly more peaked than the reference.

## FRONT
9. [must] Wide dome with roots arching over it; 2-3 tips on the front ground line plus side roots. — MET: front cell shows 3 front tips plus roots on both shoulders.
## SIDE
10. [should] Roots across the back half too, one reaching the ground with a pale tip; mound facets visible. — MET: side cell has roots across the whole view, with a pale ground tip at each end and lower facets below; slightly steeper than the reference.
## TOP
11. [must] Oval mound; roots radiate from a crossing near the centre to tips past the edge; leaves on the crown. — MET: top cell shows the oval mound, tangled crossing roots and 3 leaf clumps.

## PARTS
12. [must] RootClusterDirtMound: lumpy faceted mound alone ~10 x 4 with base pebbles, no roots. — MET: 10.6 x 8.7 x 4.3 multi-blob lumpy mound (chunkier facets than the reference's).
13. [must] RootClusterRoot: single thick arch ~6-7 long x 3 high, tapered, asymmetric, with pale cut tips. — MET: 7.2 x 3.15, ~1.6 thick tapering, one leg longer, pale tips at both ends.
14. [must] RootClusterLeafModule: 5-6 pointed leaves on a short stem, ~3 wide. — MET: 6 wider leaves plus an upright centre leaf, 2.8 x 3.0; it reads a little small in the parts cell.

## DROPS / DEPLETED
15. [must] RootClusterRootBundle: straight root ~3 long with a clearly visible pale cut end; closed, <=300 tris. — MET: diagonal log whose pale octagonal cut end faces the camera in the drops cell; 72 tris, closed beam.
16. [should] RootClusterRootBundleForked: ~3 long with one branch and a pale cut end. — MET: Y fork with a pale cut end visible, 132 tris.
17. [must] RootClusterExposedMound: same lumpy mound ~11 x ~3, no roots or leaves, a few pebbles. — MET: 11.3 x 9.8 x 3.2 bare lumpy mound with pebbles.

## PALETTE / SCALE / VFX
18. [must] One colour per material: r06_dirt #6A5047 (mound + pebbles), r06_rootbark #9A6540 (roots), r06_cutwood #E0B27C (tips/cut ends), r06_leaf #3F9A2C (leaves). â€” MET: dirt reads purple-brown and darker than the warm roots, tips pale tan, leaves saturated green; no shade problems.
19. [must] VFX: harvest_hit at (0,-4,2.5) with root/cutwood chips; harvest_deplete at (0,0,0.5); no glint, no light. â€” MET: both sockets placed (chip preview visible on the front of the mound), no glint/light.
20. [should] Tris under budgets, nothing below z=0. — MET: hero 2214/5000, parts <=920, depleted 900, drops 72/132; floor clamped.

## REVISION goals (verifier, all treated as must)
21. [must] Lumpy faceted mound, 20+ mid-size facets (see 2). — MET: many chunky facets visible in hero/front/side.
22. [must] Thick chunky overlapping roots, ~1.8-2 thick (see 3). — MET: roots about 2 studs thick, draped and overlapping.
23. [must] Irregular crossing with roots on top of others (see 5). — MET: two over-crossings at the crown, asymmetric.
24. [must] Lower, wider lumpy silhouette ~6.5 high (see 8). — MET in hero/front; the side view is slightly peaked.
25. [must] Side view: roots across the back half (see 10). — MET.
26. [must] Straight drop shows its pale cut end (see 15). — MET.
27. [should] Root part ~1.6 thick, tapered, asymmetric (see 13). — MET.
28. [should] Dirt mound part uses the multi-blob build (see 12). — MET.
29. [should] Wider, fuller leaves. — MET in the hero; the leaf module still reads a bit small in the parts cell.

## Iteration log
- Build 1: mound + 5 roots + leaves. Problem: Tint 1.26x on DirtMound; roots thin, cage-like, tips buried at the edge; leaves tiny.
- Build 2: tint_var lowered (0 problems), roots R 0.72, tips placed above ground beyond the edge, bigger pebbles and leaves. Tips now visible, but roots floated like a tent cage.
- Build 3: roots hug the surface (smaller lifts) with curvier paths and a short back root; leaves bigger. Mound still steep-walled hemisphere.
- Build 4: lower slopes flared (flare 0.22) for a sloping dome, leaves lowered to bring height to 6.6. Closer to reference silhouette; straight drop's pale end still not reading (build cap reached).
- Revision build 1 (5): mound rebuilt from a core, 6+9 ring blobs and pebbles; roots r 0.8-1.0 on asymmetric crossing paths; drops became diagonal beam() logs with cutwood ends. The drop's pale end now reads; the mound was spiky and the crown peaked.
- Revision build 2 (6): smoother inner blobs (subdiv 2), flatter profile, lower lifts, tips pulled in, root part shortened. Still rib-like.
- Revision build 3 (7): roots re-laid tangentially across the shoulders, one tip on the slope, embedded deeper, bigger leaf clumps. Crossing and draping now read like the reference.
- Revision build 4 (8): lower crossing lifts and crown leaves, wider core; height 6.5.
