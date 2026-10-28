# R05 HealingHerb goals

Reference: art/reference/kit/rows/R05_row2.png (row 2 of R05_shrubs_berries_herbs.png).

## ASSEMBLED / HERO
1. [must] Low spreading rosette: hero ~5.5 x 5 x 3.5 studs, footprint clearly wider than tall (~1.5x).
   - MET - render reads as a low wide rosette, ~5.6 x 5.8 x 3.3 studs, clearly wider than tall like the ref
2. [must] 8-9 large broad pointed leaf blades radiating from the centre, each ~2.5-3 long x ~1.2 wide, tilted up and outward, outer tips drooping to a point near the ground.
   - MET - 7 outer + 4 inner broad blades; outer ones rise ~50 deg, arch, then droop to points at the ground; inner ones stand ~62 deg around the stalks, so the rosette reads as a bulky dome like the ref (tips a bit spikier)
3. [must] Each leaf is a thick faceted lance with a visible central fold ridge (midrib), few large facets, no noisy small ones.
   - MET - blades are thick (0.65) lances of ~10 big facets; the raised midrib splits each into a lit and a shaded half in the hero and top cells
4. [must] Two slim bright-green stalks rise from the centre, one ~2.5 and one ~2.0 tall, slightly leaning apart; the taller stands left/behind, the shorter right/front.
   - MET - two slim bright-green stalks, taller on the left, shorter on the right, leaning apart as in the ref hero
5. [must] Each stalk is crowned by a cream faceted teardrop bud (~0.9 wide x 1.2 tall), pointed top, larger than the stalk width by ~3x.
   - MET - cream faceted teardrop buds sit on both stalks, ~3x stalk width, close to the ref bud size
6. [should] Leaves reach only ~40% of total height; buds are the highest point (~3.5).
   - MET - buds peak at 3.58; the leaf dome now reaches about half the height, close to the ref
7. [should] Dark brown root mound (~1.2 wide) partly visible under the leaves at the centre.
   - MET - brown root mound shows under the leaves at the centre in the front and side cells

## FRONT
8. [must] Front view: symmetric fan of leaves, widest at the bottom, two buds above the centre at slightly different heights.
   - MET - front cell: a fan of leaves widest at the base, two buds at different heights above the centre
9. [should] Front view: leaf pairs visible at front, left and right with tips touching the ground line.
   - MET - front cell: leaves to the left, right and front touch the ground line

## SIDE
10. [should] Side view reads like the front: rosette + two stalks, buds overlapping slightly.
   - MET - side cell: rosette with two stalks, buds overlapping like the ref side

## TOP
11. [must] Top view: radial rosette star of 8-9 pointed leaves, two cream buds near the centre.
   - MET - top cell: radial star of ~9 pointed leaves with the two cream buds near the centre

## PARTS
12. [must] HealingHerbBud: one cream bud on a short (~1 stud) green stem, ~1 x 1 x 2.2.
   - MET - bud part: one cream bud on a short green stem, 1.0 x 1.0 x 2.2
13. [must] HealingHerbLeaf: a single large broad faceted leaf with midrib, lying flat-ish, ~3 x 1.6 x 0.8.
   - MET - leaf part: pointed at both ends, raised midrib keel splitting it into a lit and a shaded half, rolled and tip slightly up, 2.98 x 1.44 x 0.92 (matches the ref lance)
14. [must] HealingHerbRootPlug: small faceted brown rock-like lump ~1.6 x 1.4 x 1.0.
   - MET - root plug: faceted brown lump 1.6 x 1.3 x 1.0, matching the ref

## DROPS / DEPLETED
15. [must] HealingHerbSprig: two small sprigs, each a cream bud on a stem with two small leaves at its foot, ~1.5 tall, under 300 tris, nothing below z=0.
   - MET - two sprigs in one mesh, each a bud on a stem with two leaves at the foot, 1.6 tall, 168/300 tris, 0 problems
16. [must] HealingHerbDepleted: skirt of ~7 flatter leaves (~5 wide x 1.8 tall max) around a short flat-topped cut stump ~0.6 tall; no buds, no tall stalks.
   - MET - depleted cell: 7-leaf skirt around a short flat-topped brown stump, no buds or stalks

## PALETTE
17. [must] Leaves one r05_herb_leaf that renders the ref's mid green (verifier: not brighter or more saturated than the ref), cooler than the berry shrub yellow-green.
   - MET - retuned to #4A7846 (rule 3); sampled render mid-tone #628C5C vs ref #678656, no longer the vivid green of #4C9B52; still cooler than the berry shrub #5A9E22
18. [must] Stalks one bright yellow-green r05_herb_stem (#6FAE2E); buds one cream r05_bud (#F0E2A6); root mound/plug one greyish brown r05_root (#6E5442).
   - MET - stalks bright yellow-green, buds cream, mound and plug greyish brown; each material uses one key

## VFX
19. [must] Hero has harvest_hit at (0,-1.5,2.5) scale 0.8 and harvest_deplete at (0,0,0.3), noted in tag notes.
   - MET - harvest_hit (0,-1.5,2.5) s0.8 and harvest_deplete (0,0,0.3) use leaf/cream chip bursts with no grey dust; noted in the tag

## VERIFIER REVISION (added as must)
20. [must] HERO: 8-9+ large broad pointed blades, upright and arching, outer ones drooping to a point; leaves bulky and dominant beside the buds.
   - MET - build 8: outer blades rise steeply and arch before drooping; the inner ring stands near-upright round the stalks; the leaf mass fills the lower half (5.7 x 6.2 x 3.6). The tips are still a little spikier than the ref's broad ellipses
21. [must] PARTS: HealingHerbLeaf is a crisp pointed folded lance with a midrib, ~3 x 1.6 x 0.8.
   - MET - see goal 13: a diamond lance with a keel ridge and two shaded halves, 2.98 x 1.44 x 0.92
22. [must] COLOUR: leaves are a mid green matching the ref mid-tone, not brighter or yellower.
   - MET - see goal 17: #4A7846 renders #628C5C mid vs ref #678656
23. [should] Stalks visibly longer above the leaf line; buds ~0.9 x 1.2.
   - MET - stalks 2.15 / 1.65 plus buds; both buds and the upper stalks clear the leaf dome in the front and side cells
24. [should] Sprig buds ~15% smaller.
   - MET - sprig bud radius 0.24 -> 0.2; the buds sit in proportion to the two foot leaves

## Status / iteration log
- Build 1: first pass. The default harvest VFX dust (grey smoke puffs) covered the hero cells; leaves were narrow and lay flat; stalks too tall (3.9).
- Build 2: replaced the VFX emitters with leaf/cream chips (no dust), so the cells are clear. Shortened the stalks to 3.4, widened and raised the leaves, gave the root plug more facets, enlarged the sprig leaves.
- Build 3: sharper leaf tips, higher tip_z so the blades arch up; the leaf part now tilts.
- Build 4: fuller elliptic leaf outline (width 1.75), shorter blades bring the footprint to 5.6 x 5.8, rounder and larger buds. The silhouette now matches cell for cell; the leaf colour is still brighter than the ref (fixed sheet palette).
- Build 5 (revision): leaf colour #3A8546; split the leaves into 7 outer arching blades and 4 inner upright blades; new 4-ring LANCE leaf part; stalks 2.15/1.65; smaller sprig buds. The blades rise now, but they were thin and narrow, and the colour was still vivid.
- Build 6: wider and thicker blades. Sampling showed the render mid-tone #519754 against the ref's #678656, still too saturated.
- Build 7: leaf #4A7846 (render mid #628C5C now matches the ref); longer outer blades (2.4), higher arch; the depleted blades rise more (1.55 tall).
- Build 8: broader blade tips; the leaf part is thicker (0.75 keel) and rolled 0.45, so the midrib fold reads as two shaded halves; front inner blade shortened. 0 problems, 1424 tris.
