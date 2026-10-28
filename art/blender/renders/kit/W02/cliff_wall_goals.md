# W02 row 1: CliffWall goals

Reference: `art/reference/kit/rows/W02_row1.png` (full sheet: `art/reference/kit/W02_cliffs_ledges_terrain.png`).
Compare: `art/blender/renders/kit/W02/cliff_wall_compare.png` (cells are in `cliff_wall_cells/`).
Module: `art/blender/scripts/kit/W02/cliff_wall.py`.

Status after revision 3 (palette migration), build P4: 7 assets, 20505 tris, 0 problems.

Revision 3 adds the user's REWORK as musts, marked (R): one palette key per material, no shade
variants, no colour picked by height, direction, tier or at random among shades, small Tint only,
and 0 runner problems. Goals from earlier verifier passes are marked (V).

Reference colours sampled from the row (sRGB). These are the sheet palette's sources:
- rock: lit #CAB9B1, faces #A1897F-#CDB4A6, so the key is `w02_rock` #B3A19C. The grey-green swatch #7F897C is the shadow side of the same rock, so it gets no key.
- grass: #B0C82B, key `w02_grass` #B0C82B.
- earth: #A26842, key `w02_earth` #A06A45.
- bush: #5C8D20-#7EA129, key `leaf` #6C9A28.
- connector: #898489, key `w02_connector` #8A868A.
- pebbles: `w02_slab` #CDC2C3.

## ASSEMBLED / HERO (iso)

1. **[must] Palisade body.** 7-9 tall, narrow, vertical faceted columns, 3-6 studs wide, with long vertical planes. Not boulders.
   - MET (P4): the hero and front cells show 7 tall columns with long vertical planes. The fronts now alternate in and out (even columns pushed out, odd columns pulled back), so the crevices read as shadowed recesses.
2. **[must] (V) Proud forward columns and foot shards.** Pointed forward columns about 16, 11.5, 9.5 and 7 tall stand about 3 studs proud. 4-6 leaning foot shards, 3-6 tall, break the foot outline.
   - MET (P4): the hero cell shows separate pointed spikes standing in front of the face. The front cell shows spikes at 4 heights and pointed shards along the foot and at both corners.
3. **[must] Cap.** A bright flat yellow-green cap at z=24, with a visible brown earth band and a scalloped lip overhanging the column fronts.
   - MET (P4): in the front cell a green line sits over a brown stripe across the full width, with rounded lobes over the columns. The top is flat.
4. **[must] (V) Corner bush clusters.** Big round leafy clusters, about 5-7 across, sit on the lip corners. The front ones spill over the face.
   - MET (P4): the hero cell shows big round clumps on all 4 corners. The two front clusters hang past the lip, each with a clump below it on the face.
   - All clumps are now the one `leaf` green, and the dome shading comes from the light.
5. **[should] Grass streaks.** 2-3 grass streaks drip 2-4 studs down the face.
   - MET (P4): the zoomed front shows 3 green streaks under the lip, now in `w02_grass`.
6. **[should] Foot dressing.** Small bushes, tufts, rubble and a grass fringe at the foot.
   - MET (P4): the hero and front cells show a green fringe, small bushes and rubble at the foot.
7. **[must] (V)(R) Single rock colour.** Every rock face is `w02_rock`: columns, forward columns, shards, rubble and the core. Light and dark come only from the facets.
   - MET (P4): the hero cell shows one grey-mauve rock. Lit faces are pale, side faces are darker, and the crevices are shadowed by geometry.
   - The shades `w02_rock_pale`, `_sage`, `_cool` and `_deep` are gone, along with the deep-crevice and inner-corner `deep_zone` code.
8. **[must] (V) Overall weight.** The block reads chunky and rock-forward with a lush cap, not a sheer smooth block.
   - MET (P4): side by side with the reference, the iso cell shows the same chunky palisade, spiky foot and bush-crowned cap.

## FRONT

9. **[must] Proportions.** The front cell is about 1.15:1 wide to tall, with 7-9 column faces and clear crevices.
   - MET (P4): the hero measures 32.0 x 24.0 x 28.1 including bushes. The front cell shows 7 columns separated by shadowed crevices.
10. **[must] Forward column heights.** The forward columns rise to different heights with pointed tops, and shards line the foot.
    - MET (P4): the front cell shows spikes at about 2/3, 1/2, 2/5 and 1/3 of the height.
11. **[should] (V) Stepped crest.** Column heights step and the crest varies under the cap.
    - MET (P4): the front cell shows bevelled crests dropping under the lip, and pointed ledges partway up on the stacked columns.
12. **[should] Clean facets.** Large, clean facets with no noisy small triangles.
    - MET (P4): hull plus a 3-degree dissolve leaves long planes in the front cell.

## SIDE / REAR

13. **[must] Flush side.** The side is flush at x=+16, with vertical columns and a flat grass top across the full depth.
    - MET (P4): the side cell shows a flat cap line and vertical relief.
14. **[must] Connector plate.** A dead-flat grey `w02_connector` plate, 31 x 0.4 x 23.5, sits on +Y with 1.5 x 0.5 x 0.4 tabs at 8-stud spacing on both vertical edges.
    - MET (P4): the side cell shows the flat grey plate on the back edge. The parts cell shows its tabs.
15. **[should] Plate visible in side view.** The plate shows as prominently as in the reference's rear 3/4 view.
    - UNMET: the runner's side camera is straight side-on, so it sees the plate edge-on. SIDE_AZIMUTH=135 would show the back, but the cell would then lose the side columns. I kept 90, as the earlier passes did.

## TOP

16. **[must] Top view.** The top is mostly bright yellow-green, with bushes at the corners, pale pebbles and 10-15 flower dots.
    - MET (P4): the top cell shows a bright green field, clusters at all 4 corners, 8 pale pebbles and 14 white and yellow dots.
    - The toned patches are now the same `w02_grass` with a +6-9% Tint, so they are faint.
17. **[should] Scalloped edge.** Only the cliff edge is scalloped. The back and sides are straight.
    - MET (P4).

## PARTS

18. **[must] Three part assets, all readable in the parts cell.** CliffWallGrassTopLip, CliffWallBody and CliffWallBackConnector.
    - MET (P4): the body stands at the back, the lip slab with bushes and flowers lies in front, and the grey plate with tabs stands at the right, turned to the viewer as in the reference.
    - In P2 the runner's new grid packer put the 32-wide plate in front of everything and hid the lip. So the plate part is now authored along Y, with its outer face toward -X (closed on both sides, 82 tris), and its notes say to rotate it -90 degrees for the +Y back.
19. **[should] (V) Body matches the hero.** The body part reads as the same column mass with foot spikes.
    - MET (P4): the parts cell shows the same columns and spikes.
20. **[should] Lip reads as a slab.** The lip part shows the slab with its earth band, bushes, pebbles and flowers.
    - MET (P4): visible in front in the parts cell.

## VARIATIONS

21. **[must] A. CliffWallStraight, 32 x 16 x 24.** Same lip, columns and +Y connector.
    - MET (P4): it measures 32.0 x 16.0 x 27.2 and reads as a shallower run with the same cap and bushes.
22. **[must] B. CliffWallInnerCorner, 32 x 32.** A concave L facing -Y and -X, with an L cap 16 deep and connectors on +Y and +X.
    - MET (P4): the variant cell shows the L cap and two faces meeting in a shadowed inner corner. That corner is now dark from geometry, not from a painted deep tone.
23. **[must] C. CliffWallOuterCorner, 32 x 32.** A rounded convex corner of big columns, a square cap and connectors on +Y and +X.
    - MET (P4): the variant cell shows big bulging corner columns, a square cap and a corner shard.
24. **[should] (V) Variants are lush.** The variants carry the same cap, bushes and foot dressing.
    - MET (P4).

## Palette / scale / technical

25. **[must] (R) Sheet palette.** PALETTE holds exactly the 6 `w02_` sheet keys, with the sheet hex values verbatim. `leaf`, `flower_white` and `flower_yellow` come from flintkit.PALETTE, whose values are identical.
    - MET: the runner reports "extra palette key must start with w02_" for non-w02_ keys in a module PALETTE (build P1). So those 3 keys are listed only in a comment.
26. **[must] (R) One key per material.** Rock is `w02_rock`, grass/streaks/tufts/fringe are `w02_grass`, the band is `w02_earth`, bushes are `leaf`, pebbles are `w02_slab` and the plate is `w02_connector`.
    - MET: a grep for the old shade keys and constants (PALE, SAGE, COOL, DEEP, GRASS_L/D, BUSH*, SUN, deep_zone) finds nothing.
27. **[must] (R) Tint is small and random.** Tint varies within 1.25x per material and never by direction.
    - MET: the runner's tint_spread is 1.19 on every asset.
    - Measured per material, each one is flat: relative brightness spread is 0.015-0.03, and correlation with face direction is 0.15 or less (rock 0.12/0.01, grass 0.01/-0.02 on the hero).
28. **[must] (R) Runner clean.** 0 problems, every asset under budget, origins at the bottom centre, nothing below z=0.
    - MET (P4):

      | Asset | Tris / budget |
      | --- | --- |
      | Hero | 4576 / 6000 |
      | Straight | 3568 / 5000 |
      | Inner | 4147 / 6500 |
      | Outer | 4042 / 6500 |
      | Lip | 2232 / 2500 |
      | Body | 1858 / 5000 |
      | Connector | 82 / 200 |

29. **[must] (R) Honest waivers.** `kit_two_tone_ok` is set only where `w02_rock` meets `w02_connector` or `w02_slab`. `kit_shading_ok` is set only where `leaf` meets `w02_grass`.
    - MET: the runner's baked_shading is 0.68-0.71 on the assets holding both leaf and grass, and that comes only from grouping those two materials by hue (grass+leaf correlation 0.69). Each material alone scores 0.15 or less.
    - Body, which holds only rock plus foot dressing, also scores 0.15 or less per material. The connector scores 0.0.
30. **[must] (R) No water or vapour meshes.** The reference shows none, so there are no VFX sockets and no stand-in meshes.
    - MET.
31. **[must] (V) Footprint and cap.** The hero is 32 x 24 with the grass top at z=24 and a 1.0 cap (0.6 grass over 0.4 earth).
    - MET: SLAB_BOT is 23.0 and EARTH_TOP is 23.4. The column tops are at 23.3.

## Iteration log

Earlier passes 1-6, R1-R7 and S1-S6 are summarised in git history and the earlier goals file. That build used shade sets (rock_pale/sage/cool/deep, grass_light/dark, bush_light/dark), which the user's REWORK rejected.

**P1.**
- Changed: PALETTE replaced with the 9 sheet keys; every face remapped (rock tones to w02_rock, grass shades to w02_grass, bushes to leaf, pebbles to w02_slab); tone() reduced to one key with a +/-5% random Tint; deep crevice, deep_zone and shade-patch code removed; light grass patches became a Tint step.
- Result: 8 problems. 3 were "extra palette key must start with w02_" (leaf and flower_*). 5 were the baked-shading score of 0.68-0.70 from leaf+grass grouped by hue.

**P2.**
- Changed: leaf and flower_* are used from flintkit (identical values); a `kit_shading_ok` waiver is set for leaf vs grass; `kit_two_tone_ok` is set for rock vs connector/slab.
- Result: 0 problems. But the runner's new parts grid packer stood the 32-wide plate in front of the lip and body.

**P3.**
- Changed: the connector part is authored along Y with its outer face -X and is closed on both sides.
- Result: the parts cell now shows body, lip and plate like the reference.

**P4.**
- Changed: column fronts alternate harder in and out, since there is no painted crevice tone any more.
- Result: crevices read as shadowed recesses in the front and iso cells; 0 problems.
