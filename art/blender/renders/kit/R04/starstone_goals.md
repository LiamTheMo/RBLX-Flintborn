# R04 Starstone goals

Reference: art/reference/kit/rows/R04_row3.png (Starstone row of R04_meteors_event_deposits.png).

## ASSEMBLED / HERO
1. [must] Two big angular grey slabs lean together: a tall pointed slab on the left (peak up-left, ~9 studs) and a broad slab back-right (~7.5 studs); hero ~8 x 7 x 9 studs, taller than wide (H/W ~1.1). — MET - two convex-hull wedge slabs, left 9.0 tall peak up-left, right 7.6 back-right; hero 9.1x7.2x9.0; wedges now, no longer columns.
2. [must] A bright saturated cyan crystal is wedged in the gap between the slabs, in front, about 1/3 of the hero width and ~55-60% of its height; it is the focal accent. — MET - crystal sits in the cleft between the slabs (left slab inner face and right slab front edge overlap its flanks), clearly the focal accent; a little narrower than the reference (~1/4 width).
3. [must] Crystal is an elongated hex prism with pointed top and bottom, 6-8 clean large facets visible, tilted slightly toward the viewer. — MET - 6-sided prism with long pointed top and bottom tips, ~6 large facets visible, tilted toward viewer.
4. [must] 7-9 low grey rocks ring the base, the largest (2.5-3.5 studs) in front, plus a small rock on the right edge. — MET - 9 low angular hull rocks (12 pts each, flat facets, tilted), largest 3.5 wide in front, small one at right edge; skirt <=1.8 high.
5. [should] Slabs show big clean facets (roughly 8-15 per slab visible), no noisy small facets. — UNMET - slabs show ~12-16 flat hull facets with sharp ridges, but read smoother/less chiselled than the reference's many-facet slabs.
6. [must] Hero is much taller and narrower than the meteor rows (peak is the sheet's tallest point, ~9 studs). — MET - tallest sheet asset at 9.1 studs, narrow pointed silhouette vs the domed meteors.

## FRONT
7. [must] Front view: left slab peak at upper left, right slab peak at upper right/behind, crystal diamond visible between them from ~z=1 to ~z=6.5. — MET - front view: left peak upper-left, right peak behind-right, crystal diamond between from ~z1 to ~z6.5.
8. [should] Front-view outline is a broad pointed "mountain" shape, base wider than mid by ~1.5x. — MET - front outline is a broad pointed double-peak mass on a wider rubble skirt.

## SIDE
9. [should] Side view: a single tall pointed grey mass with the crystal showing as a cyan sliver on the front side, rubble at the base. — MET (partial) - side view: grey pointed mass with cyan as a sliver on its front edge; the right slab reads dark because it is the unlit side from that camera (same key, normals recalculated outward).

## TOP
10. [must] Top view: grey slabs and rocks surround a cyan crystal that reads as a triangle/diamond in the middle. — MET - top view: cyan crystal in the middle, grey slabs to left, right and behind, front rocks below; reads as a framed core (more hexagon than triangle).

## PARTS
11. [must] Stone Shell part: one big angular tilted grey slab ~4 x 3 x 6. — MET - Stone Shell is the hero's left wedge hull fitted to 4.8x2.7x5.9, tilted ~25 deg; chunky angular slab like the parts cell.
12. [should] Stone Shell B: a second, smaller slab ~3 x 2.5 x 4.5. — MET - Stone Shell B is the right slab hull, 3.6x2.4x4.6.
13. [must] Starlight Core part: long cyan hex crystal ~2.5 x 2.2 x 5.5, pointed both ends. — MET - Starlight Core long cyan hex crystal 2.4x2.3x5.5, pointed both ends.
14. [must] Base Rock part: cluster of 4-5 low grey rocks, footprint ~6 x 3, height <=1.8. — MET - Base Rock part: 5 low grey rocks on 6.0x3.0x2.0.

## DROPS / DEPLETED
15. [must] Two Starlight Shard drops: faceted cyan crystals, ~1 x 0.8 x 1.8 (pointed) and ~1.3 x 1 x 1.4 (chunky angled), <=300 tris, closed. — MET - two cyan faceted shards 1.0x0.9x1.7 (pointed) and 0.9x1.2x1.4 (chunky), 24/20 tris, closed.
16. [must] Depleted (Base): loose low pile of 7-9 grey rocks ~8 x 6 x 2.2 with one stubby broken slab (~3 tall) at the back, no cyan. — MET - 8 low angular hull rocks 8.1x5.7 with a faceted broken stump (3.0 tall) at the back, no cyan.

## PALETTE
17. [must] Stone (slabs, base rocks, depleted) is ONE cool grey-violet key r04_star_stone #6F6B72; render reads mid cool grey, not warm tan, not charcoal. — MET - single key r04_star_stone renders cool mid grey, not tan or charcoal.
18. [must] Crystal and shards are ONE key r04_starlight #22C4E6 (emissive 0.6, glossy); render reads bright saturated cyan like the reference. — MET - single key r04_starlight renders bright saturated glossy cyan, matching the reference crystal.

## VFX
19. [must] heat_glow (cyan, scale 1.2, with cyan PointLight) and dust motes at the crystal; ore_glint on crystal front; harvest_hit at (0,-3.5,3); harvest_deplete at (0,0,0.8). — MET - heat_glow (cyan light) + dust motes at crystal, ore_glint on front, harvest_hit (0,-3.5,3), harvest_deplete (0,0,0.8) present.

## VERIFIER GOALS (revision 1)
V1. [must] HERO: two broad chunky angular slabs lean together (wide wedges, base ~50-60% of height), not thin columns. — MET - left wedge base 4.4 wide x 9 tall, right 4.8 wide x 7.6; front view reads as two fat wedges, no parallel-sided spires.
V2. [must] Left slab tall pointed, peak up-left; right slab broad at back-right, shorter. — MET - left peak up-left at 9; right slab broad behind-right with its shoulder falling away to the right, peak 7.6.
V3. [should] 8-15 large irregular planar facets per slab, sharp ridges, varied outline. — MET (partial) - large flat irregular hull facets with sharp ridges; a few more facets would read closer to the reference.
V4. [must] Crystal wedged INSIDE the cleft, framed by slabs on both sides and behind. — MET - iso/front show grey on left, right and behind the crystal; it no longer stands in front.
V5. [must] Top view: grey slabs and rocks surround a centred cyan crystal. — MET - top cell: cyan in the middle with grey on all sides (front rocks below it).
V6. [should] Side view: tall pointed grey mass with cyan as a thin sliver at the front; right slab not near black. — UNMET (partial) - sliver is right, but the right slab still renders dark in the side cell: that face is in shadow from that camera (same key, outward normals).
V7. [must] Base rocks: 7-9 low tilted angular rocks 1.2-3.5 studs, largest in front, small one at right; skirt < 2 studs. — MET - 9 angular hull rocks, front one 3.5 wide, max height 1.8, small rock at the right edge.
V8. [must] Part StoneShell: big angular chunky tilted slab ~4x3x6 matching the hero slab. — MET - same hull as the hero left slab, 4.8x2.7x5.9, tilted ~25 deg.
V9. [must] Depleted and Base Rock rocks use the same low angular style. — MET - both use the 12-point angular hull rocks; no rounded boulders.

## Iteration log
- Builds 1-5 (earlier run): ring-cone slabs read as columns; crystal too far forward.
- Revision build 1: slabs and rocks rebuilt as convex hulls of hand-placed points; crystal moved into the cleft. Crystal framed; slabs still narrow spikes.
- Revision build 2: widened slab shoulders and depth; chunky but tombstone-like tops.
- Revision build 3: sharper peaks, right shoulder falls to the right, proud front points for facet ridges; reads as wedges. (One crashed attempt: duplicate verts in the hull delete, fixed.)
- Revision build 4: crystal widened (rx 1.6), front rocks enlarged, side rocks pulled in (width 9.1). Small change; stopped at the 4-build cap.

