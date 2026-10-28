# FlintNode (R01 row 2) — visual goals

Reference: art/reference/kit/rows/R01_row2.png (cells: hero iso, front, side, top, parts, drops + depleted).
Scale: 1 unit = 1 stud, origin bottom centre, front -Y. Measured from the reference front cell
(~78 px/stud on a 3x crop): shell ~6.6 W x 4.4-4.9 D x 5.5 H; top-left corner of the ridge at x ~-1.1,
right flank vertical to z ~3.3 then a shoulder; side view a tall pointed wedge.
Revision 5 (verifier 6/10): its unmet goals are added as musts, marked (V5). G1, G7, H4, G13 and D1 were
reset to UNMET and judged again by eye from the rev 5 renders (they are folded into V5a/V5b/V5d/V5e).
Revision 4 (colours): one palette key per material - r01_limestone #C9AE94, r01_flint #3A393F
(roughness 0.3, metallic 0.1), r01_stone #877C78; no shade keys, no kit_shading_ok waiver.

Status is from the latest build (rev 5 build 6): 10 assets, 1015 tris, 0 problems.

## ASSEMBLED / HERO
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| H1 | Shell ~6.6 W x 4.4-4.9 D x 5.5 H studs; hero with base rocks ~7.2 x 5.4 x 5.5 | must | MET | KITSTAT shell 6.6 x 4.3 x 5.5; hero 7.1 x 5.7 x 5.5 (depth includes the proud front/back crystals) |
| V5a (V5) | Front/hero silhouette: angular wide mound (not a dome/egg); steep, nearly straight left flank from z ~0.5 to ~4.5; short ridged peak left of centre (x ~-1.0); a visible stepped right shoulder (shelf at z ~3.7-4.0, width drop ~1 stud); tall narrow wedge in the side view | must | MET | Front cell: straight steep left edge up to a corner near the top, flat short ridge clearly left of centre, then the outline drops to a distinct shelf notch on the right at ~70% height before the vertical right flank; hero cell shows the same notch. Raymap: right edge steps from x 2.2 to 3.0 between z 4.15 and 3.85. Side cell: one tall narrow wedge (the shoulder shows only as an inner facet edge) |
| V5b (V5) | Crystals big and bold: upper long diamond ~2.6-3.0 x ~1.4 from near the peak to mid-right; front-left a big pyramid low; front-right a full pyramid ~1.5 wide facing the front; one on the back-right; each 0.4-0.6 studs proud, seated flat, not spikes | must | MET | Front cell: upper diamond runs from just under the ridge to mid-right (footprint 2.9 x 1.4), front-left triangular pyramid spans almost a third of the width, right pyramid fully faces the front below the shoulder (~1.6 wide); top cell shows the back-right one. FLINTSTAT: apexes 0.45-0.57 proud of the original surface on flat seats |
| V5c (V5) | Crystals cover a similar share of the front face as the reference (~25% of the front silhouette) | must | MET | Front cell: three dark crystals dominate the face as in the reference cell, with tan stone between them; front raymap ~22% flint cells |
| G3 | Facet style: crisp large planes with hard edges across the shell, ~50-100 planes, no smooth-egg look | must | MET | Front/hero cells: big flat planes with hard light/dark steps; FLINTSTAT shell 77 faces, mean dihedral 27 deg |
| H6 | 3 small grey base rocks at the foot: biggest front-left, one front-right, a pebble at the right | must | MET | Front and hero cells: big grey rock front-left, smaller one front-right, pebble at right |
| H7 | Hero taller and more pointed than StoneNode | should | MET | Side cell tapers to a narrow peak at 5.5 |

## PALETTE / MATERIAL
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| P1 | Limestone ONE base colour, pale sand-tan mid-tone #C9AE94 (r01_limestone), small random Tint only, on shell, hero and depleted slab; clearly lighter than the grey base rocks | must | MET | Hero/front/parts/depleted cells: one pale sand tan, faces shaded only by light; grey rocks visibly darker and greyer |
| P2 | Flint ONE colour near-black charcoal #3A393F (r01_flint, roughness 0.3) on every crystal, insert and flake; gloss from roughness + ore_glint, no painted lighter facet | must | MET | All cells: crystals uniformly near-black with glossy reflections and white glint sparkles; no second flint key |
| R4a | Exactly three palette keys: r01_limestone, r01_flint, r01_stone, verbatim sheet values | must | MET | PALETTE dict holds only those 3 keys, values verbatim |
| R4b | Grey base rocks (hero, parts, depleted) all r01_stone #877C78 | must | MET | GREY = ["r01_stone"] used for every base rock; cells show the same warm grey |
| P5 | No 'lighting is painted into the colours' problem; build ends "0 problems" | must | MET | STATS R01/flint_node: 10 assets, 1015 tris, 0 problems |

## FRONT / SIDE / TOP
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| F1 | Front view shows 3 crystals: upper long diamond centre-right, big front-left pyramid low, right pyramid low-right; tan limestone between them | must | MET | Front cell matches the reference layout cell for cell: diamond top-centre-right, triangle low-left, pyramid low-right |
| R4c | Side view: crystals stick out on BOTH the left and right flanks of the wedge; top view: one at the back-right | must | MET | Side cell: dark crystal shards on the left (front) flank, a dark pyramid on the right (back) flank; top cell: back crystal right of centre at the back rim |
| S1 | Side view tapers from ~4.4 deep at the base to a narrow peak (H/D ~1.25) | must | MET | Side cell: tall wedge narrowing to a pointed top; shell 4.3 deep x 5.5 tall (1.28) |
| G11 | Top view: rounded-polygon outline, crystals at the rim, back crystal at back-right | should | MET | Top cell: angular rounded outline, front crystals at the front rim, back crystal at the back-right |

## PARTS
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| A1 | All six parts exist with collision: shell hull, inserts none, BaseRock hull, BaseRockSmall none | must | MET | KITSTAT lists all six; collision tags unchanged |
| A2 | Parts cell shell reads as a faceted polyhedron with the same stepped silhouette | must | MET | Parts cell: big-planed shell with the right shoulder notch visible |
| V5d (V5) | FlintInsert is a chunky faceted blade ~2.0 x 1.1 x 3.4 with a broad body and a clear lower second peak (~2.2); Small a short broad diamond; Thin a slim 3-sided blade ~0.8 x 0.6 x 2.5 with a chunky body, no needle; none read as spikes | must | MET | Parts cell: FlintInsert is a broad tapering shard (full 2.0 x 1.1 foot, tip near the centre) with a separate lower second peak on its right; Small a broad diamond; Thin a slim triangular blade, full width at the foot, chisel tip ~0.25 wide. The runner's grid puts them in front of the shell's foot, so they overlap it (runner layout) |
| A3 | Base Rock ~1.6x1.4x1.1, small pebble ~0.8, faceted grey | should | MET | KITSTAT BaseRock 1.8x1.3x1.2, BaseRockSmall 0.8x0.7x0.5 |

## DROPS / DEPLETED
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| V5e (V5) | FlintFlake reads as a chunky rhombic faceted flake ~1.3 x 0.9 x 0.8 with pointed ends and a faceted top ridge (~30 tris), box collision, <=300 tris | must | MET | Drops cell: an elongated rhombic lozenge with pointed ends, propped up at one end, showing separate top-ridge and girdle planes; KITSTAT 1.4x0.9x0.8, 28 tris |
| V5f (V5) | FlintFlakeAlt: one fat end tapering to a long point, readable in the drops cell | must | MET | Drops cell: right flake has a tall blunt end and a lit taper facet running down to a point; 1.3x0.8x0.8, 26 tris |
| V5g (V5) | Drops visually legible at cell scale: several distinct lit/shaded planes per flake, not a dark blob | must | MET | Drops cell: each flake shows 3-4 distinguishable planes plus a glint; they are small because the runner spaces drops 3 studs apart, not because of the mesh |
| D3 | Depleted: low flat tan limestone lozenge ~6.5 x 4.0 x 1.5 with a stepped faceted top, grey rocks at both ends (two left, one right), no flint | must | MET | Depleted cell: long flat tan slab, two grey rocks at the left end, one at the right; KITSTAT 6.5x4.0x1.5 |
| D4 | Depleted top shows 3+ distinct stepped planes | should | MET | Depleted cell: the top shows 4-5 large planes with distinct shading steps (two extra step cuts added) |

## VFX
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| V1 | harvest_hit on the front strike face at mid height (z ~2.4); Chips #C9AE94/#45444A, Dust tan | must | MET | Socket from a +Y ray at (0.4, z 2.4), 0.25 off the face; recoloured emitters; the dust puff shows in the front cell between the crystals |
| V2 | harvest_deplete at the base centre; Chips #C9AE94/#4A4950 | must | MET | Socket at (0, 0, 0.3), recoloured emitters |
| V3 | ore_glint: 2 on the hero just off the two biggest front crystals (scale 0.5, rate 0.5, #F4F8FF/#C9D6EA); one on FlintInsert; one (scale 0.25) per flake | must | MET | Glint sparkles are visible on the front-left and upper crystals, the FlintInsert and each flake in the cells |

## Iteration log
- Revs 2-4: see git history (rev 4 ended at 865 tris, 0 problems; verifier 6/10: dome silhouette, small crystals, spike inserts, blob flakes).
- Rev 5 build 1: shell = union (exact boolean) of a main hull (left flank 3.3 to z 4.4, ridge peak at x -1.55..-0.55) and a right shoulder hull (shelf z ~3.8); crystals enlarged (upper 2.9 x 1.4), FlintInsert = union of two blades, Thin made 3-sided, flakes rebuilt, two extra depleted step cuts. Result: front shows the step and peak left; shell 7.1 wide, crystals still flat; the side view shows the shoulder as a second arch.
- Build 2: body narrowed (shell 6.6), shoulder tapered in depth; crystals lifted 0.6-0.8 off seats cut at 50% (0.45-0.57 proud of the old surface); right crystal turned to face the front. Flakes became tilted rhombic plates. Result: bolder pyramids, right crystal full; side arch still visible.
- Build 3: shoulder top sloped toward +X; thicker flake (15 deg tilt). Result: flakes read as faceted lozenges.
- Build 4: shoulder top ring cut to 5 points (angular shelf edge, side arch mostly gone); FlintInsert given a broad foot; Thin full width at the foot with a chisel tip.
- Build 5: FlintInsert body tapers above the foot.
- Build 6: FlintInsert tip moved toward the centre so the left edge slants (a triangular shard, not a pillar). Result: 1015 tris, 0 problems; every must is MET by eye.
