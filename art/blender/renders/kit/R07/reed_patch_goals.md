# R07 reed_patch goals (ReedPatch, row 2)

Status after build 4 (final; judged by eye against the reference row).
Note: the white translucent shards over the bases in every cell are the harvest_deplete/harvest_hit
VFX preview stand-ins drawn by the pipeline, not geometry.

## ASSEMBLED / HERO
1. [must] Three chunky tan faceted cattail heads on tall stalks at clearly staggered heights (low left, mid, tallest back-right). — MET: three tan hex capsules at three clearly different heights, left lowest, right tallest, same read as the reference.
2. [must] Each head is an elongated faceted capsule (~1.1 wide x 2.2-2.4 tall) with a small nub on top. — MET: 6-sided tapered capsules with a thin nub on each, as in the reference.
3. [must] 8-10 flat, angular pointed leaf blades splay outward and upward in a fan; outer blades reach past the mud rim on left and right. — UNMET: blades now broad, flat and pointed and fan outward, but the outer tips only reach about the rim; the reference fan is wider and lower on the right.
4. [must] Low brown mud mound at the base, ~1.2 tall, with 5-7 grey pebbles at its rim (left and right-front most visible). — MET: brown faceted mound with grey pebbles at left, front and right rim (partly hidden by the VFX preview).
5. [must] Hero ~7 x 6 footprint, ~7.5 tall; silhouette about as wide as tall. — MET: 7.6 x 5.7 x 7.2 studs and the cell silhouette is roughly square like the reference.
6. [must] Two greens read distinctly: olive stalks vs darker deeper green blades. — MET: yellow-olive stalks stand out against the darker leaf green.
7. [must] Palette: heads tan, mud brown, pebbles purple-grey, saturated. — MET: tan heads, brown mud, grey pebbles match the reference swatches; greens are saturated, not pastel.
8. [should] Stalks thin (~0.35), straight, leaning slightly outward. — MET: thin straight stalks, small outward lean.

## FRONT
9. [must] Front view: three heads at three heights, foliage fan wider than the mound top, mound plus pebbles a wide low band. — MET: three staggered heads, leaf fan as wide as the mound, low mound band with pebbles.
10. [should] A few shorter blades in front low on the clump. — MET: short blades visible at the front base.

## SIDE
11. [should] Side view: heads staggered, leaves fanning to both sides, low wide mound. — UNMET: heads overlap more in side view and the leaf fan is narrower than the reference side cell.

## TOP
12. [must] Top view: round mud base with rim pebbles, rosette of green blades radiating out, three tan heads near the centre. — MET: rosette of pointed blades over a round brown base, three tan heads near centre, pebbles at the rim.

## PARTS
13. [must] ReedPatchReedStalk: thin straight green faceted stalk ~0.4x0.4x5 with a step/joint near the base. — MET: olive stalk with a visible node ring/step near the base.
14. [must] ReedPatchSeedHead: tan faceted capsule with short stalk piece and tip nub. — MET: tan capsule on a green stub with a nub (smaller in the cell than the reference's, same shape).
15. [must] ReedPatchLeafBlade: single flat pointed blade ~1x0.3x5.5, slightly bent, deeper green. — MET: flat pointed dark-green blade, slight bend.
16. [must] ReedPatchMudBase: faceted brown mud mound ~6.5x5.5x1.2 with a couple of grey pebbles. — UNMET: mound reads right but its two pebbles sit behind/at the sides and are barely visible in the parts cell.

## DROPS / VARIANT / DEPLETED
17. [must] ReedStems: 5-6 green stems lying flat, tan heads at one end, tan twine band, ~3x1.6x1.2, <=300 tris. — MET: 5 green stems with tan heads at the right end and a tan band in the middle, 280 tris; looks chunkier and less fanned than the reference.
18. [must] ReedPatchClippedPatch: mud base with 5-6 short cut stubs 1.5-2.5 tall, flat cut tops, no heads. — MET: short flat-topped green stubs on a mud base, no heads (partly hidden by the deplete VFX preview).
19. [must] ReedPatchDepleted: bare mud mound with pebbles only, ~6.5x5.5x1.3, no green. — MET: bare brown mound with grey pebbles at the rim, no green.

## VFX
20. [must] harvest_hit at (0,-1.5,3.5) in green chip colours and harvest_deplete at (0,0,0.5) on ReedPatch; harvest_deplete on ClippedPatch; no glint/light. — MET: sockets placed as specified (previews visible in the cells).

## Iteration log
- Build 1: first pass. Leaves read as thin grass (edge-on to camera, narrow taper), pebbles small, drop stems chunky.
- Build 2: wider leaves, more lean, bigger pebbles (7), cattails spread, mud-base rotation fixed, depleted flatter, drop stems thinner. Leaves still edge-on.
- Build 3: added a roll to the blades so their flat faces turn toward the camera; 6-sided heads. Faces show better, but blades are still narrow because of the taper profile.
- Build 4: blade profile now stays at full width until 55% of its length; outer blades lean more; heads 2.2 long; drop stems fan a little. Leaves now read as broad blades. Hit the 4-build cap with goals 3 and 16 still unmet.
