# W02 row 3 NATURAL RAMP: goals

Reference: `art/reference/kit/rows/W02_row3.png` (full sheet `art/reference/kit/W02_cliffs_ledges_terrain.png`).
Compare: `art/blender/renders/kit/W02/natural_ramp_compare.png`.

Notes from studying the reference: the hero is a long, straight sandy-orange path that climbs from the
ground to a flat top. Bright yellow-green grass borders run along both sides, with round dark-green bush
clumps (about 5 per side), white and yellow flower dots, and pale pebbles. Under each border is a wall of tall,
narrow, faceted pale grey-mauve rock columns. On the reference's near (right) side these columns are bulky:
they stand well outside the grass, rise 2-4 studs above it toward the high end, and take up about as much of
the picture as the path. At the low end the walls shrink to small rocks and bushes. The path shows faint
darker cross seams like shallow terraces, and pebbles. The SIDE/REAR cell is seen from the rear 3/4: a flat
grey back face plus a flat grey wedge face. The parts show one grass strip, a square dirt pad with earth sides,
and a pale lilac-grey wedge with a crack. The variants are a long straight ramp, a 90 deg arc whose outer wall
faces the viewer, and a zig-zag path whose walls are slim rock flanks.

Colours sampled from the reference row (median of small boxes): rock swatch #C9B8B0, lit wall faces
#CCB1A1 / #BAA092, wedge top #DCCBC5, grass swatch #B2C82E, earth swatch #A06B47, lit path #F7BF87.

Runner cameras (from build_kit.py): hero and variants at azimuth -22 / elevation 20 (front-LEFT), front at
0 / 6, side at +90 / 6 (straight side-on from +X, +Y on the right), top straight down.

Status after build 16 (the 6th build of this revision pass). Measurements come from the KITSTAT lines, the
compare cells (320 x 240), and 3x close-ups of the cells.

## Verifier goals from the second failed review (all "must")
| # | prio | goal | status | evidence |
|---|---|---|---|---|
| V-R1 | must | HERO: both side walls read as tall, narrow, faceted pale columns that grow with the slope to ~11-13 and poke above the grass. A large pale rock mass is clearly visible beside the path, and the rock visibly exceeds the grass width | MET | The cross-section is reworked: the grass reference line is now at 6.1 (was 6.6), the cap is 1.4 wide, and the -X columns bulge 1.05-1.45 past the line with a 1.0 battered foot (outer foot at ~8.3). All 8 columns above z 4 rise as tips scaled by height (to +2.45, top 14.4). Hero cell: a tall, pale, jagged column wall now fills the whole left side of the ramp. It is about 2x the grass strip's width on screen, and the column tips rise above the grass from a quarter of the way up |
| V-R2 | must | SIDE: wedge profile with a clean flat grey face at the high end | MET | The +X side of the 8-deep landing is now a flat w02_connector face (0.4 thick, 7.6 long x 11.3 tall, under the grass lip). Side cell: a clean wedge rising from the ground on the left, then a flat grey rectangle over the whole landing on the right. The +X slope wall is "calm": broad columns with a sloped rim 0.25 under the grass lip, so the wedge's top line is clean |
| V-R3 | must | Rock shade: the side cell shows no strong purple-black facet scatter; rock is one pale grey-mauve | MET | Rock is one colour, w02_ramp_rock #B9ADA9, with a +-7% random Tint (the cool and deep scatter keys are gone). The side cell's +X wall now reads as an even mid grey-mauve with soft facet steps. It is darker than the reference only because that face is on the shadow side of the runner's light |
| V-R4 | must | FRONT: columnar rock visible at each side beside the grass strips (trapezoid silhouette) | MET | Front cell: faceted pale columns flank the grass on the left all the way up, and grey columns show outside the right grass strip toward the back. The silhouette widens toward the back |
| V-R5 | should | HERO: pale w02_slab wedge visible low on the sides under the path edge | PARTIAL | The low stretch (path below ~3.5) now has a chamfered pale-stone ledge, 1.4 wide and 0.85 under the path, with its top and chamfer facing the sky. In the 3x close-up of the hero cell it shows as pale pieces between the front shard and the corner bush. At cell size it is still small |
| V-R6 | should | HERO camera composition matches the reference (rising to the upper right, right wall visible) | UNMET (camera) | The runner's hero camera is fixed at azimuth -22 (front-left); the reference is a front-right view. Mirroring the asset would break "front faces -Y" plus the module set's left/right agreement. A per-subject azimuth is in shared_lib_requests |
| V-R7 | should | VARIATIONS: switchback has slim walls between and around the flights | PARTIAL | The middle wall is now narrow columns (3.0-4.2 wide, 0.7-1.0 bulge) whose tips rise 2 above the back flight's grass. The outer front and landing walls have bulging columns with tips. The riser is still tall at the high end, because the spec stacks a 12-to-24 flight above a 0-to-12 one (a 24-high difference at that end) |
| V-R8 | should | Flower dots legible at cell size | MET | Each flower cluster is 3 dots, each 0.76 wide (was 0.52), with 8 clusters per border. They are visible as white and yellow specks along both grass strips in the hero, front and top cells |

## ASSEMBLED / HERO (iso)
| # | prio | goal | status | evidence |
|---|---|---|---|---|
| H1 | must | Footprint 16 W x 32 D (+-0.7) with the origin at the bottom centre; total height 12-14.5 (path top 12 at the landing) | MET | KITSTAT 16.6 x 32.6 x 14.4; runner origin check ok |
| H2 | must | Slope 24 long rising from the ground to 12 (<= 30 deg, about 26 deg), then a flat landing 7.5-8 deep at z=12 | MET | H(s) = 0.25 + 11.75 s/24 (26.1 deg), then flat to y=15.6; the side cell shows the wedge, then the flat top |
| H3 | must | Sandy-orange path (w02_path) about 9.5-10 wide (~60% of the width), centred, and the dominant light colour | MET | path faces +-5.0 with the grass lip from 4.7, so about 9.4 visible (57% of 16.6). The top cell's path band dominates the middle |
| H4 | must | 6-8 faint cross seams, one every 3-4 studs on the slope | UNMET (hero cell) | The 7 seams are now geometry (0.3 riser steps, one path colour, because the runner's new "one colour per material" rule bans the darker seam key). They read clearly in the straight and curved variant cells. In the hero cell at 26 deg, the riser and tread faces get nearly the same light, so the seams are barely visible. This needs one more build (deeper or under-cut risers), and the 6-build cap was reached |
| H5 | must | 6-10 small pale pebbles scattered on the path | MET | 8 pebbles, seated on the stepped surface; visible as pale chips in the hero cell |
| H6 | must | Grass border on each side (bright w02_grass over a brown w02_earth band, scalloped outer edge) | MET | cap 1.4 + 0-0.45 scallop + lip, with the earth band under it. The hero and front cells show bright strips both sides |
| H7 | must | 4-6 round bush clumps per border, plus at least 6 white or yellow flower dots per border | MET | 5 three/four-lobe bushes per border, plus a corner bush; 8 clusters x 3 dots per border |
| H8 | must | Each side wall is a row of tall faceted pale rock columns, taller toward the high end, about 11-14 at the back | MET | hero cell: the -X wall rises to 14.4 at the back; side cell: the +X wall follows the slope up to the landing |
| H9 | should | At the low end the walls shrink to small pointed shards and ground-level bushes at the front corners | MET | one 1.2-2.6 shard on the pale ledge and a ground bush with a flower tuft at each front corner |
| H10 | should | 2-4 column tips rise above the grass, stronger on the high side | MET | -X wall: 8 tips scaled by height; the hero cell shows the jagged tips standing above the grass |
| H12 | must | The back (+Y) end is a flat matte grey w02_connector plate about 14 x 11.5 with tabs on its vertical edges | MET | plate 14.0 x 0.4 x 11.5 at y 15.6-16.0, with 1.5 x 0.5 x 0.4 tabs at z 2 and 10 on both vertical edges |

## FRONT
| # | prio | goal | status | evidence |
|---|---|---|---|---|
| F1 | must | The path recedes up the middle, centred between a grass border and a rock wall on each side; the low front edge sits at the ground | MET | front cell: orange path centred, green borders with bushes both sides, low lip at the ground |
| F2 | should | Trapezoid silhouette: rock walls on both sides rising to the back | MET | see V-R4 |

## SIDE / REAR
| # | prio | goal | status | evidence |
|---|---|---|---|---|
| S1 | must | Wedge profile: low at the front, rising evenly to the high end, flat over the landing | MET | side cell: a clean wedge from the ground to 12, then the flat landing |
| S2 | should | The side face reads as a calm rock mass plus a flat grey panel, not busy small facets | MET | see V-R2 / V-R3. The -X wall's tips show above the +X rim as a few blocks behind it |

## TOP
| # | prio | goal | status | evidence |
|---|---|---|---|---|
| T1 | must | A long strip about 2:1: a light path band about 60% wide down the middle, a green border with bush dots on each side, rock only at the outer edges | MET | top cell: a 2:1 strip, path band ~57%, 5-6 bushes per side, grey rock along both outer edges |
| T2 | should | Seams visible as faint cross lines on the path in the top view | PARTIAL | the seam risers show as very faint lines in the top cell |

## PARTS
| # | prio | goal | status | evidence |
|---|---|---|---|---|
| P1 | must | NaturalRampGrassBorder: one sloped strip, 24 long, about 2.5 wide and 1 thick, rising about 12, with 4-6 bushes, pebbles and flowers; <= 1500 tris; collision none | MET | 3.1 x 24.0 x 13.4 (2.2 cap), 1011 tris, collision none; 5 bushes, a boulder, pebbles, 8 flower clusters |
| P2 | must | NaturalRampTopLandingPad: 10 x 8 x 1.5 slab, path top with tonal patches, w02_earth sides, 1-2 pebbles; <= 800 tris; collision box | MET | 10.0 x 8.0 (slab 1.5), 169 tris, box; two Tint-dip patches visible in the parts cell, 2 pebbles |
| P3 | must | NaturalRampWedge: a clean pale lilac-grey wedge 10 W x 24 L rising from 0 to 12, chamfered edges, one crack line; <= 300 tris; collision hull | MET | 10.0 x 24.0 x 12.0, 34 tris, hull, 0.5 chamfer. The crack is now a thin steep ridge in the same stone, showing as a faint zig-zag line in the parts cell |
| R6 | must | PARTS: the wedge stone is a lilac-grey, not pink or salmon | MET | w02_ramp_slab #B8B0B6; the parts cell shows a pale lilac-grey wedge |

## VARIATIONS
| # | prio | goal | status | evidence |
|---|---|---|---|---|
| V1 | must | NaturalRampStraight: 16 x 48 rising from 0 to 12 (about 14 deg), no landing, grass and rock walls on both sides, grey plate at the high end; <= 5000 tris | MET | 16.7 x 48.6 x 13.5, 4338/5000 tris; variant 1 cell: a long ramp with clear seams and pale walls |
| V2 | must | NaturalRampCurved: 90 deg arc (centreline radius 20), about 32 x 32, rising from 0 to 12; the outer wall faces the viewer with columns rising above the grass; <= 7000 tris | MET | 31.5 x 31.5 x 14.3, 3981 tris; outer wall tips above the grass in the variant 2 cell |
| V3 | must | NaturalRampSwitchback: two flights (0 to 12, 12 to 24) joined by a flat U-turn landing at 12 on 32 x 32; rock wall between the flights; <= 8000 tris | MET | 32.4 x 31.9 x 25.2, 6078 tris; the variant 3 cell reads as a Z with a wall between the flights |

## Palette and build
| # | prio | goal | status | evidence |
|---|---|---|---|---|
| C1 | must | The sheet's 15 w02_* keys copied verbatim, plus flower keys and w02_-prefixed module keys. ONE colour per material: rock #B9ADA9, slab #B8B0B6, grass #A9BE26, earth #9F6A47, path #E2A86E, bush #4F8A3B, connector #8A858A | MET | The module uses only those 7 base colours plus the flower keys. The light/dark/cool/deep/seam variants were removed (the runner's new shade_pairs check). The remaining look-alike pairs are real material changes, waived through kit_two_tone_ok: rock vs slab vs connector, and path vs earth vs flower_yellow |
| C2 | must | Build ends with "0 problems": every asset within budget, nothing below z=0, one mesh per asset, correct roles and collision | MET | "STATS W02/natural_ramp: 7 assets, 18831 tris, 0 problems" |

## Iteration log
- Builds 1-10 (earlier runs): every asset built with 0 problems. The verifier failed it (6.3/10): the hero and
  front walls were thin, the side cell was dark and busy with no grey panel, the hero is mirrored, the slab
  was hard to see, the switchback was heavy, and the flowers were tiny.
- Build 11: new cross-section (path +-5.0, ref line 6.1, cap 1.4). Columns bulge 1.2-1.65 with height-scaled tips,
  and tip tops step flat outside the grass. A pale chamfered slab ledge was added at the low end, flowers are
  bigger 3-dot clusters, and a flat connector face covers the +X side of the landing. Result: the hero and front
  cells show bulky rock, but the +X tips made the side cell a spiky skyline and the hero was 15.1 tall.
- Build 12: +X wall made calm (no tips, a clean sloped rim under the grass); -X tips 2.6. Result: clean wedge
  plus a flat grey panel in the side cell; hero 14.6 tall.
- Build 13: battered foot (1.0) on the -X wall, tips 2.45. Result: a wider pale wall in the hero, 14.4 tall.
- Build 14: +X bulge 1.2-1.45 with a 0.9 foot, for more rock beside the grass in the front cell. The runner had
  meanwhile gained a "shades of one material" check, so this build reported 6 problems.
- Build 15: one colour per material (rock, grass, bush, path, pad). Seams moved into the geometry and the wedge
  crack became a ridge; kit_two_tone_ok covers the real material pairs. 0 problems. The seams became too faint.
- Build 16: seam risers 0.3 deep, a bigger crack ridge, pebbles seated on the stepped surface. 0 problems. The
  seams read in the variants but barely in the hero (26 deg, front light).
- Open: H4 hero seams (next step: under-cut risers, so each seam casts a thin shadow line), V-R6 camera
  azimuth, V-R7 switchback riser height (set by the spec).
