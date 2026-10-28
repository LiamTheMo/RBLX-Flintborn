# W04 row 4 - OLD PINE: visual goals

Reference: `art/reference/kit/rows/W04_row4.png`. Compare: `art/blender/renders/kit/W04/old_pine_compare.png`.
Module: `art/blender/scripts/kit/W04/old_pine.py`.

Revision 8 (verifier fail, resemblance 5/10: squat fat trunk, small mushy pads hugging the trunk, yellow-ring knot,
tiny canopy part). Status after build 4: "STATS W04/old_pine: 8 assets, 27382 tris, 0 problems".
Hero 7254/8000, 22.7 x 22.7 x 26.4. All goals judged by eye against the reference row.

## REVISION 8: VERIFIER GOALS (added as must unless noted)
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| V8a | Hero tall, wide, sprawling: ~26 tall x 22 wide, crown clearly wider than trunk | must | MET | Hero cell: tall tree, pads sprawl out to both sides on long limbs; 22.7 x 26.4. |
| V8b | Trunk slender vs crown (~1/4-1/3 crown width at mid height), twisting, fluted, flaring to roots | must | MET | Hero/front cells: trunk narrows to about a quarter of the crown width mid height, spiral grooves, splayed root fins. |
| V8c | Visible fork and elbowed limbs leading to separate pads (5-6 pads, big crown on top) | must | MET | Hero/front cells: fork at ~14, bare elbowed limbs visible under each of six pads, biggest pad on top. |
| V8d | Pads: big chunky star pads, each ~1/4-1/3 of the tree width, flat underside, saturated green | must | MET | Pads ~7-8.6 wide on a 23-wide tree; chunky faceted star clumps with flat floors, mid green. Slightly boxier than the ref's rosettes. |
| V8e | Front: tall column, pads left, right and top, trunk tapering up | must | MET | Front cell: tapering trunk, two pads left, two right, crown on top. |
| V8f | Parts: CanopyTier ~7x7, Branch log, ForkedTrunk two stubs, RootsBase, all at comparable scale | must | MET | Parts cell: pad 7.1 x 7.4 (as big as the roots base), branch log 8.3 long, forked trunk 13 tall; grid layout is set by the runner, not the module. |
| V8g | Knot hole reads as a dark hole, not a yellow ring | should | UNMET | Build 4: the yellow ring is gone (thin 0.9 rim, bark-lined 5r well), but the knot now barely reads at cell scale. |
| V8h | Side cell: same upright sprawl, no lean | should | MET | Side cell: upright trunk, pads both sides and top (build 3). |
| V8i | Stub hollows read dark at cell scale | should | MET | Parts cell: forked-trunk tops and branch log ends show a thin pale rim round a dark brown well. |
| V8j | Bent: three separate pads with gaps, visible elbows | should | MET | Bent cell: left, top and right pads separated by clear gaps on bare elbowed limbs. |

## ASSEMBLED / HERO (OldPine)
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| H1 | About 22 W x 22 D x 26 H studs | must | MET | 22.7 x 22.7 x 26.4; hero cell taller than wide like the ref. |
| H2 | Fluted twisting trunk ~1/3 crown width mid height flaring into ~6 buttress roots | must | MET | See V8b. |
| H3 | Trunk forks high (~14) into leaders; elbowed side limbs to the other pads | must | MET | See V8c. |
| H4 | 5-6 flat-floored star cloud pads, big crown on top, others 7-9 out on side branches | must | MET | Pads on a ring 8.5 out, crown pad 8.6 wide on top. |
| H5 | Small knot hole on the front | should | UNMET | See V8g. |
| H6 | Sandy patch ~18 across, 4+ pale rocks, 8+ grass tufts, 3-4 leafy bushes | must | MET | Hero cell: cream disc, grey rocks, lime tufts, green clumps. |

## FRONT / SIDE / TOP
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| F1 | Front: tapering column to the fork, pads left, right and top | must | MET | See V8e. |
| S1 | Side reads as the same upright tree, pads both sides and top | should | MET | See V8h. |
| T1 | Top: 5-6 separate star pads round visible brown limbs | must | MET | Top cell (build 3): six separate star clumps with gaps, brown limbs between. |

## PARTS
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| P1 | CanopyTier: one chunky star pad ~7 x 7 x 3-5 | must | MET | 7.1 x 7.4 x 4.9; big star clump in the parts cell. |
| P2 | BranchAngled: bent log with elbow and pale cut ends | must | MET | Parts cell: elbowed log, thin pale rim round dark end. |
| P3 | ForkedTrunk: fluted trunk, V of two leaders with hollow cut tops | must | MET | Parts cell: V trunk, two hollow tops. |
| P4 | RootsBase: root spread with cut top, rocks, tufts, soil | must | MET | Parts cell: root stump, rocks, grass, sand. |

## VARIATIONS
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| V1 | SplitTrunk: trunk splits low into two limbs, pads on both | must | MET | Variant 1 cell: low V split, pads on both leaders. |
| V2 | Bent: trunk curves sideways, wide crown | must | MET | Variant 2 cell: S-curved trunk, 25.4 wide x 19 tall. |
| V3 | BrokenCrown: snapped top with jagged pale splinters over a hollow, pads only on side branches | must | MET | Variant 3 cell: pale shards at the top, three side pads. |

## PALETTE / TECH
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| C1 | w04_bark on trunk/roots/limbs and hollow linings; w04_wood_end only on thin cut rims/splinters | must | MET | Cells: brown bark, pale only at rims and shards. |
| C2 | Needle pads (w04_needle #5E8E1A) render saturated mid green | should | MET | Pads render mid green with lime lit facets. |
| X1 | 8 assets, budgets met, nothing below z=0, 0 problems; hull trees, grass/bushes nocollide | must | MET | 0 problems; every KITSTAT ok. |

## Iteration log (revision 8)
- Build 1: trunk slimmed (cone 4.4 -> 2.1), fork raised to 14, pads moved 7-9 out on long elbowed limbs; pads rebuilt
  as 1 big leaf_cluster star + top star + satellites; thin rim, bark-lined hollows; bigger branch log. Pads too flat.
- Build 2: pads taller/chunkier (squash 0.78), bigger R; cut rim 0.82. Read well; top view pads merged.
- Build 3: pads re-spread on a 5-azimuth ring + centre crown, satellites pulled in: separate pads in the top view.
- Build 4: knot rim 0.9, 5r deep, pointed slightly down: yellow ring gone, knot barely visible (should, left UNMET).
