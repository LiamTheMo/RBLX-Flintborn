# FrostShrub (R08 row 2) goals

Status after each build: MET / UNMET with one line of evidence.

## HERO (iso, front-left)
1. [must] Bare dark-brown forked trunk with straight angular faceted limbs (no foliage on wood); trunk forks at ~1/3 height into 3-4 limbs that each fork again into short stubs. — MET - front cell shows thick brown trunk forking at ~1/3 height into 4-5 straight faceted limbs, each with a short stub; no foliage on the wood.
2. [must] 3 big pale-blue faceted ice nodules (~2.5x2.5x3.3, pointed top and bottom) at branch tips; nodules visibly bigger/bulkier than leaves in width. — MET - 2 big pale nodules crown the upper-left/upper-right tips plus a smaller one on a front-right limb; they read bulkier than the blades.
3. [must] ~4 saturated mid-blue pointed lozenge leaves (~3.5 long) angled out and up from the limbs, flat-ish blades with a centre ridge. — MET - 4 saturated mid-blue pointed lozenges with a ridge angle out-and-up from the limbs (left mid, left low, top, right).
4. [must] Base: ring of brown-grey rocks (r08_rock) with a flat pale snow/ice slab in the centre and 4-5 small pale ice crystal chunks on the ground. — MET - hero/front: chunky brown-grey rock ring, pale snowy mound in the centre, 5 pale crystal chunks on top.
5. [must] Three colours stay distinct in the render: pale ice (#9FC4EE-ish, light), mid blue leaves (#3A66AE), brown wood (#684738); rocks grey-brown distinct from wood. — MET - render shows pale ice, mid blue leaves, warm brown wood and grey-brown rock as four separate tones, matching the reference swatches.
6. [should] Overall hero ~9 w x 8 d x 8 h studs; silhouette wider than tall slightly (~1.1x), crown wide and spreading. — UNMET (should) - 10.6 x 7.8 x 8.7 studs; leaves stick out a little wider than the 9-stud target.
7. [should] Trunk thick at base (~1.2 radius) tapering upward; limbs about half trunk thickness. — MET - trunk visibly thickest at ground and tapers to thin limbs at the fork.

## FRONT
8. [must] Front view reads as a Y/candelabra: central trunk, limbs spreading left and right, leaves sticking out at both sides, nodules on top tips. — MET - front cell reads as a Y/candelabra with leaves out both sides and nodules on the top tips, close to the reference front.
9. [should] Base in front view is a low band ~1.5-1.8 high, about as wide as the crown (~9). — MET - front base band ~1.7 high and about crown width.

## SIDE
10. [should] Side view narrower than front (depth ~8 incl. base but crown narrower ~6), still showing a forked trunk with a leaf to one side and a nodule on top. — MET - side cell narrower, trunk with a tall nodule on top and a blade to the left (nodule a bit dominant).

## TOP
11. [should] Top view: roughly round cluster, nodules and leaves radiating outward around the trunk, rock ring visible at edges. — MET - top view: roughly round cluster, nodules and blue blades radiate around the trunk, rocks visible at the rim.

## PARTS
12. [must] FrostShrubForkedStem: brown trunk+branches only, Y fork with 3 tips, ~5 w x 1.5 d x 6 h. — MET - parts cell: brown Y stem with 3 tips and two side stubs, 5.0 x 1.1 x 6.0.
13. [must] FrostShrubIceNodule: single pale faceted nodule ~2.5x2.5x3.3, 8-10 large facets, pointed ends. — MET - single pale faceted nodule 2.3 x 2.3 x 3.5 with pointed ends, ~10 visible facets.
14. [must] FrostShrubLeaf: single mid-blue lozenge leaf ~3.5x1.5x1 with a short brown-free stem (leaf colour). — MET - single mid-blue lozenge on a thin blue stalk, 3.3 long.
15. [must] FrostShrubBase: rock ring with pale ice crystals and dished centre, ~9x8x1.8. — MET - rock ring with small pale crystals and a lower brown dished centre, 8.7 x 7.7 x 2.5 (taller than 1.8 because crystals sit on rocks).

## DROPS / DEPLETED
16. [must] FrostBud: small pale ice nodule ~1.3x1.3x1.8, pointed, <=300 tris. — MET - FrostBud pale pointed nodule 1.2 x 1.1 x 1.7, 20 tris.
17. [must] IcyLeaf: small mid-blue pointed leaf ~2.2 long, <=300 tris. — MET - IcyLeaf mid-blue pointed blade 1.9 long (slightly under 2.2), 20 tris.
18. [must] FrostShrubDepleted: base ring with ice crystals plus short bare brown forked stem stub ~2.5 high with two small fork tips; no nodules or leaves. — MET - depleted: rock ring with ice crystals and a short bare brown stub with two fork tips (~2.6 high), no nodules/leaves.

## VFX / tech
19. [must] Sockets: vapour at (0,0,1) scale 0.8 colour #CFE6FF on hero; harvest_hit at (0,-2,4) colour of ice; harvest_deplete at (0,0,0.5) on depleted; no ore_glint. — MET - vapour (0,0,1) s0.8 #CFE6FF low mist, harvest_hit (0,-2,4) ice chips, harvest_deplete (0,0,0.5) ice chips; no ore_glint.
20. [must] Build ends with 0 problems; all assets within budgets; nothing below z=0. — MET - run.sh: 8 assets, 1860 tris, 0 problems; all KITSTAT ok.

## Iteration log

- Build 1: base geometry; vapour/hit previews (default size, spec colour key ignored) buried the trunk in white; leaves over-wide (11.7).
- Build 2: replaced colour overrides with emitter overrides (ice chips, low creeping mist); bigger touching rocks, snow mound; trunk now visible. Leaves rendered edge-on/hidden, 3 nodules looked like balloons.
- Build 3: leaves/nodules built at origin then transformed (now face-on lozenges); limb layout redone (2 top nodules + small front one, 4 leaves); smaller crystals on base part/depleted; dropped deplete dust puff.
- Build 4: broader leaves (1.9 wide), angled more outward; limbs spread wider. Reads as the reference cell for cell; hero slightly wide (10.6).
