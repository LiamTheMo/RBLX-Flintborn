# R02 IronNode goals

Reference: art/reference/kit/rows/R02_row1.png (row 1, IRON). Status updated after each build.
Revision 2: verifier failed v1 (5.5/10). Verifier goals added as musts (V1-V7).

## Palette (one base colour per material)
- G1 [must] Host is ONE medium cool grey-brown whose render mid tone matches the reference (~#6A6466 rendered; key lightened to ~#77..), never near-black in the side view; clearly darker than base rocks. — MET: host renders warm mid grey-brown in hero/front/top like the reference, darker than base rocks; side cell has a shadowed half but mid-grey faces, no black.
- G2 [must] Base rocks are ONE warm light grey (r02_base_rock #8C827D), visibly lighter than host. — MET: base rocks render light warm grey, clearly lighter than the host.
- G3 [must] Iron plates are ONE steel-blue glossy metal (r02_iron, ~#8FA3C4) with bright, silvery near-white facets next to darker blue facets (not flat lilac). — MET: plates are one pale steel-blue key; the big front, shoulder and top plates show near-white crown facets beside blue ones (medium plate flatter than the reference).
- G4 [must] Every chunk carries a bright orange rust border (r02_rust #C4602B) visible all round its edge, thin (~0.25 studs). — MET: every plate has a continuous thin orange collar in hero, front and top.

## ASSEMBLED / HERO
- G5 [must] Round dome, wider than tall (~1.2x), widest in the lower half; ~9-10 x 8-9 x 7.5-8 studs. — MET: dome reads round and wider than tall (hero 10.5x10.0x7.2 with rocks), widest low.
- G6 [must] 3 big chunks visible in hero view: large lower-left front, medium front-right low, one on upper right shoulder tilted skyward. — MET: hero shows the big lower-left front plate, medium front-right low plate and the skyward shoulder plate.
- G7 [must] Plates are gem-like: pentagon table + 2-3 rings of bevel facets at distinct angles, proud of the dome ~0.6 studs. — MET: plates are pentagon tables with a crown ring of triangular facets at varied angles, standing proud of the dome.
- G8 [must] 5-6 light base rocks (1.2-2.4 studs) half sunk around the foot, biggest at left-front and right-front. — MET: six light rocks round the foot, biggest at left-front and right-front, half sunk.
- G9 [must] (V1) Host has LARGE chiselled facets (~14-18 per visible side), reads as a faceted boulder not a smooth ball. — MET: host is a coarse 80-face chiselled boulder; front view shows ~15-20 large planes, no tiny facets.
- G10 [must] Under 4500 tris, one mesh, origin bottom centre, nothing below z=0, hull collision. — MET: 768/4500 tris, one mesh, 0 problems, hull collision.

## FRONT
- G11 [must] Front view: dome ~1.1x wider than tall, big plate left of centre, plate upper-right, smaller plate lower-right. — MET: front view big plate left, plate upper-right, plate lower-right, dome slightly wider than tall.
- G12 [should] Base rocks visible along the bottom edge at both front corners. — MET: rocks visible at both front corners.

## SIDE
- G13 [should] Side view: depth < width, rimmed plates visible on the front half; host shows mid-grey faces, not black. — MET: side view narrower than front, rimmed plates on the front half and top; mid-grey top faces.

## TOP
- G14 [must] (V4) Top view: round outline with 4 clearly separate rimmed plates (3 large in a triangle, 1 small at the top edge). — MET: top view shows 4 separate rimmed plates: big front-left, medium front-right, shoulder right and the small one near the top edge.

## PARTS
- G15 [must] (V5) IronHostRock: bare host ~9x8x7, large facets, VISIBLE flat pentagonal pockets/patches where chunks seat, no steel. — MET: IronHostRock part shows two flat pentagonal seat pads in pockets on its front, large facets, no steel.
- G16 [must] (V6) IronChunk: standalone faceted gem-like steel pentagon ~3 x 1.5-1.8 x 4 with thin rust rim, leaning upright; many facets. — MET: IronChunk 3.4x1.7x4.4, gem-crowned steel pentagon with thin rust collar, leaning upright (partly behind the host in the parts layout).
- G17 [must] IronBaseRock: light warm grey faceted low dome ~2x1.7x1.4. — MET: light warm grey faceted low dome rock 1.9x1.7x1.2.

## DROPS / DEPLETED
- G18 [must] (V7) Two DIFFERENTLY shaped closed faceted steel chunks ~1.1-1.6 studs (drop 2 flatter, hexagonal), 80-200 tris, rust at the underside edges. — UNMET (tri target only): drop 1 is a tall pentagonal gem, drop 2 a flatter hexagonal gem, both closed with rust underside skirts and clearly different, but 52/64 tris, under the 80 set here; build cap reached.
- G19 [must] IronNodeDepleted: low wide mound ~9x7.5x3, large facets, slight off-centre hump, 2-3 light base rocks at the ends, a few shallow pits, no chunks. — MET: low wide faceted mound 10.7x7.4x2.9 with an off-centre hump, flattened pits, rocks at the ends, no chunks.

## VFX
- G20 [must] harvest_hit on the front strike face at mid height; ore_glint on big front plate; harvest_deplete at depleted base centre; no light (iron does not glow). — MET: harvest_hit (-1.5,-4.5,3.5), ore_glint (-2,-4.6,3.5) s0.8, harvest_deplete (0,0,0.5); no light.

## Iteration log
- v1 builds 1-4: see verifier report (smooth subdiv-3 host, flat lilac plates, crude drops).
- v2 build 1: subdiv-2 host (80 faces, rough 0.07) -> big chiselled planes; gem plates with crown facet ring; tilted big/medium plates up for the top view; recessed seat pads on host part; gem drops; depleted hump. Host #77707A read lilac.
- v2 build 2: host #776E6B (warmer), iron #9DB1D2 rough 0.18 metal 0.45, thinner rims (0.18), plates sunk 0.3.
- v2 build 3: steeper crowns scaled by plate size (more white facets), dome flattened to 7.2 tall.
- v2 build 4: host lightened to #7B7270, medium plate tilted up 0.45. Build cap reached.
- Open: drops only 52/64 tris (simpler than reference); medium plate facets weaker than reference.
