# R07 cave_moss (CaveMoss) goals

Status after each build: MET / UNMET with one line of evidence.

## ASSEMBLED / HERO
1. [must] Big grey faceted dome rock with three plump green moss clumps capping its top (left, centre-back, right); grey rock clearly visible below and in front of the moss. — MET: hero cell shows three green clumps on a grey dome, grey faceted rock front and below.
2. [must] Hero silhouette ~1.6-1.7x wider than tall (about 8 x 6.5 footprint, ~4.8 tall). — MET (approx): 8.2 x 6.8 x 5.9 incl. sprout; moss top ~4.9; silhouette ~1.4x wider than tall vs ref ~1.55, slightly taller due to sprout.
3. [must] Centre-back moss clump rises highest (top ~4.8), left and right clumps lower (~4.0-4.3). — MET: centre-back clump visibly highest in hero/front cells, left/right lower.
4. [must] Moss blobs are chunky faceted (large flat planes, ~10-20 visible facets each), not smooth spheres. — MET: clumps show large flat facets (subdiv 3 + dissolve), though rounder than the ref's chunkier planes.
5. [must] Two bright-lime sprouts of 3-4 pointed elongated leaves: one at front centre in a rock crevice/at moss foot, one tall on the right-back moss. — MET: front-centre sprout at rock crevice (partly veiled by harvest_hit preview) and right-back sprout above the moss, 4 pointed leaves each.
6. [must] 3-4 small flanking boulders (1.2-2 studs) at the front-left, front-right and back-right corners of the base. — MET: four small boulders at front-left, front-right, right and back-right visible in hero/front.
7. [should] Moss clumps bulge slightly past the rock's outline at left and right sides, like the reference. — MET: left and right clumps bulge to the rock outline in front view.

## FRONT
8. [must] Front view: moss occupies roughly the upper half, rock the lower half; front sprout sits centred between left and right clumps. — MET: front view moss upper half, rock lower half, sprout centred.
9. [should] Rock reads as 8-15 large facets in front view, no noisy small ones. — MET: front rock reads as ~12 big facets.

## SIDE
10. [should] Side view: dome rock with moss on top, sprout leaves visible above the moss, small boulders at both base ends. — MET: side shows dome, moss cap, sprout leaves above, boulders at ends.

## TOP
11. [must] Top view: oval grey rock rim visible all round, green moss filling the centre as 2-3 lobes, lime sprouts at back (top of image) and front (bottom). — MET: top view oval grey rim around green lobes, sprouts near back and front (front one veiled by VFX).

## PARTS
12. [must] CaveMossMossClump: large plump faceted green blob ~3.5x3.2x2.6; CaveMossMossClumpSmall ~2.6x2.3x1.8, clearly smaller. — MET: parts cell shows large clump 3.5x3.3x2.7 and smaller 2.6x2.4x1.8.
13. [must] CaveMossSprout: 3-4 pointed lime leaves fanning from one point, ~1.8x1.8x2.6. — MET: lime 4-leaf fan sprout 2.1x1.4x2.5 in parts cell.
14. [must] CaveMossRockBase: domed faceted grey rock ~7.5x6x3 with 2 small flanking rocks, no moss. — MET: grey dome rock 7.7x6.3x3.3 with two flanking rocks, no moss.

## DROPS / DEPLETED
15. [must] CaveMossChunk: closed green faceted chunk ~2x1.6x1.4, <=300 tris. — MET: closed faceted green chunk 2.0x1.7x1.5, 80 tris.
16. [must] CaveMossDepleted: bare grey dome rock with 2-3 flanking rocks, no moss or sprouts, ~7.5x6x3, low. — MET: bare grey dome with 3 flanking rocks, 8.1x6.4x3.3, no green.

## PALETTE
17. [must] r07_moss #4A9122 is the only moss colour (clumps, chunk) and renders saturated mid green like the reference, not pale/olive. — MET: single r07_moss key used for all moss; renders saturated green (a touch brighter than ref, sheet palette fixed).
18. [must] r07_sprout #98C82C renders bright lime, clearly lighter/yellower than the moss. — MET: sprouts clearly yellower/lighter lime than the moss in every cell.
19. [must] r07_stone #77737A grey, slightly purple tint, one key for all rock in hero, parts and depleted. — MET: single r07_stone grey for all rocks.

## SCALE / TECH / VFX
20. [must] Hero under 3500 tris, depleted under 2000, chunk under 300; 0 KITPROBLEM. — MET: hero 1422/3500, depleted 346/2000, chunk 80/300, 0 problems.
21. [must] VFX: harvest_hit on the centre moss clump front (0,-2.5,3) coloured moss green; harvest_deplete at (0,0,0.5). No ore_glint, no light. — MET: sockets added per spec with moss-green colour; no glint/light.

## Iteration log
- B1: first pass. Moss/rock too low-poly (80 tris each), clumps small, rock apex pointed.
- B2: subdiv 3 for rock/moss, bigger moss, wider leaves. Moss became a flat mat covering the rock.
- B3: taller dome rock (sink 0.4), moss moved back/up. Rock now reads, but moss looked squashed.
- B4: taller rounder clumps pushed out to the sides; three distinct clumps capping the rock, matches ref closely.
