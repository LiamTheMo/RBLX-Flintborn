# W05 row 1 - Oak Tree: goals (revision 7)

Reference: `art/reference/kit/rows/W05_row1.png` (ASSEMBLED, FRONT, SIDE, TOP, PARTS, VARIATIONS).
Module: `art/blender/scripts/kit/W05/oak_tree.py`. Compare: `art/blender/renders/kit/W05/oak_tree_compare.png`.

Revision 7 reason: the verifier failed rev 6 (resemblance 5/10). The crown was small and sparse, the foliage pale
lime, the trunk a plain cone, OakTrunkCore narrow and unflared, and the side view a lollipop. Its unmet goals are
added below as V-goals. Statuses are judged by eye from build 4 of this pass. The light and dark you see are lighting.

## VERIFIER (rev 6 audit)
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| VG1 | HERO: the crown is five large, dense, faceted clumps that touch or overlap (top, left, right, two lower front), ~24 wide and clearly larger than the trunk | must | MET | Hero cell: five fat masses that touch, about 23.6 across, dominating a trunk about 7 wide. Gaps remain only low between the front pair. |
| VG2 | HERO: the foliage is a saturated yellow-green mid-tone with deeper green shadow sides, not pale lime | must | MET | All cells: lit tops are a saturated yellow-green and shadow sides a deep green, close to the reference. The oak uses w05_oak_leaf #7FA414. |
| VG3 | HERO: the crown is ~45-55% of the height and about twice the trunk width | must | MET | Hero and front cells: the crown spans z ~9.5-22.5 (about 55%) and is about 3x the trunk width at chest height. |
| VG4 | SIDE: a broad crown of 3-5 clumps with limbs and a twisting trunk, no lollipop | should | MET | Side cell: three masses (front low, middle, back high) with a gap and a limb showing, about 19 deep, on a swaying trunk. It is still slightly narrower than the reference. |
| VG5 | PARTS: OakTrunkCore is a cut-top column with a ragged pale heartwood top and a flared foot | must | MET | Parts cell: a column 7.8 wide and 12.1 tall that flares at the foot, with pale heartwood splinters standing up at the top. |
| VG6 | PARTS: OakRootBase is ~5-6 tall with chunky buttress roots | should | MET | Parts cell: a 6.1-tall stump with thick splayed root wedges. |
| VG7 | ASYMMETRIC: no bright yellow spikes at the base; grass and stones as on the hero | should | MET | Variant3 cell: a grass patch, tufts and stones. Root moss is off. |

## ASSEMBLED / HERO (OakTree)
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| H1 | Five distinct clumps (top, left, right, two lower front), each readable, with limbs showing between the lower ones | must | MET | Hero and front cells: five masses read separately, and brown limbs show between the front pair and below the side masses. |
| H2 | Size ~21-24 W x ~22 H, origin at the bottom centre | must | MET | KITSTAT 23.6 x 19.1 x 22.5. |
| H3 | Thick, twisting trunk (~7 at the flare), spiral ridge planes with V grooves, swaying rather than a straight cone | must | MET | Front cell: the ridged trunk has a waist and swells into the fork, with a visible S-sway and spiral grooves. The twist is now 125 degrees. |
| H4 | Fork at ~9 into 5 thick angular limbs (r ~1.3), each running into a clump | must | MET | Front cell: thick limbs leave the swollen fork and run into the masses. |
| H5 | Flared buttress roots splaying onto the base patch | must | MET | Hero cell: wedge roots splay onto the ground patch. |
| H6 | Base ring of 5-7 grey stones and 6-9 spiky grass tufts | must | MET | Hero and front cells: about 7 grey stones and spiky tufts. |
| H7 | Small dark knot hole on the trunk front at ~5 studs | should | MET | Front cell: a dark knot on the front right. |
| H8 | The top clump is the largest and highest; each clump is ~1/3-1/2 of the crown width | should | MET | Hero and front cells: the top mass (R 5.6) crowns the dome, and the others are about 10 wide. |

## PALETTE
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| C1 | Foliage is one key that renders like the reference's saturated yellow-green | must | MET | w05_oak_leaf #7FA414. The render's mid-tones match the reference's yellow-green (see VG2). |
| C2 | Bark (trunk, roots, limbs, knot rim) is all w05_bark, a warm mid-brown | must | MET | Trunk, roots and limbs are one warm brown. |
| C3 | Ground patch and tufts are w05_grass, a few root tops w05_moss, stones kit_rock | must | MET | A green grass patch (no longer pale lime), green tufts, grey stones and small moss on the hero root tops. |
| C4 | Cut ends are w05_heartwood; the knot void is w05_hollow | should | MET | Parts cell: pale heartwood on the trunk-core top, the stump top and the attach ends. The knot is dark. |

## FRONT / TOP
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| F1 | FRONT: the top-centre clump is above the side clumps, two low clumps flank the trunk, and limbs show in the gaps; the crown dominates | must | MET | Front cell: the 1+2+2 arrangement with limbs in the gaps, and the crown is about 3x the trunk width. |
| T1 | TOP: five round clumps in a rosette, filling the frame | must | MET | Top cell: five masses in a rosette, with brown limbs showing slightly at the centre. |

## PARTS (each its own asset, <= 1500 tris)
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| P1 | OakLeafClump: one star-lobed mass ~5-6 across on a stub with a heartwood attach face, hull | must | MET | Parts cell: one lumpy mass, 5.3 x 5.1 x 6.4, 1284 tris. |
| P2 | OakBranchModule: a forked angular branch ~7 long, heartwood attach end, stub stick, hull | must | MET | Parts cell: a Y branch with a second small fork and a stub, 7.1 long, 180 tris. |
| P3 | OakTrunkCore: see VG5 | must | MET | See VG5. |
| P4 | OakRootBase: flared buttress roots round a stump, precise collision | must | MET | Parts cell: chunky roots round a 6-tall stump. |

## VARIATIONS (budget 8000)
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| V1 | RoundCrown: a compact round crown of packed clumps on a stocky trunk | must | MET | Variant1 cell: a big round dome, 17.4 wide, over a stocky trunk. |
| V2 | WideCrown: a broad, flat, spreading crown | must | MET | Variant2 cell: a flat crown 20.5 wide on level limbs. |
| V3 | Asymmetric: a leaning trunk with the crown skewed to one side | must | MET | Variant3 cell: the trunk leans to +X with the crown massed on +X. |
| V4 | Every variant has the grass patch, stones and tufts | should | MET | All three variant cells. |

## TECH
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| X1 | Hero and variants <= 8000 tris, parts <= 1500, nothing below z=0, one mesh each, 0 problems | must | MET | Hero 7449, variants 6052-7812, parts 180-1284, 0 problems. |
| X2 | No VFX sockets (the reference shows none) | should | MET | No sockets. |

## Iteration log
Revisions 1-6: palette, ridged trunk, wedge roots, elbow limbs, canopy-built clumps.
Revision 7:
1. Build 1: oak leaf key #7FA414, ground patch to grass, bigger masses (R 5.2-6.0), swollen fork, thicker limbs,
   twist 125 degrees, wider trunk core with a heartwood splinter crown, a taller root base, and a second fork on the
   branch. Seen: deeper colour and a big crown, but the masses merged into one flat mushroom.
2. Build 2: masses R 4.6-5.6 with more height spread, an S-swaying trunk, no root moss on the Asymmetric variant.
   Seen: five readable clumps with limbs in the gaps. The side view was still narrow.
3. Build 3: crown spread deeper in Y (back mass ring 3.8, front pair ring 7.2), less sway. Seen: the side view shows
   three masses at different heights, about 19 deep.
4. Build 4: Round Crown enlarged to a 17-wide dome. All must goals are met.
