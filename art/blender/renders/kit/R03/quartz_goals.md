# R03 Quartz goals

Status after each build: MET / UNMET with one line of evidence (status below = revision build 4).
Revision: verifier failed the previous version (resemblance 5/10); goals V1-V8 added from its unmet list.

## ASSEMBLED / HERO
1. [must] Three pale hexagonal-prism crystals: tall Main in the centre, one Side crystal left and one right, both splayed outward ~15-20 deg. — MET - hero/front cells: main centred, both sides tip outward ~18 deg as in the reference.
2. [must] Main crystal clearly tallest (~9 studs); right side crystal slightly taller than the left (~6 vs ~5.5). — MET - front cell: right side tip sits visibly higher than the left; hero 8.9 high.
3. [must] Crystal tips pointed, built from several angled facets (not flat, not one smooth cone). — MET - tips show a sloped shoulder, two bevel rings and a 2-apex chisel ridge; several facets per tip visible in the hero cell.
4. [must] Ring of 6-7 chunky grey-taupe boulders (1.5-3.5 studs) hugs the base, larger front-centre, small at the ends; crystal bases hidden. — MET - 7 ring boulders plus 2 small wedge fillers; crystal bases hidden in hero/front cells.
5. [must] Strong value contrast: crystals near-white where lit, rocks mid/dark grey-taupe. — MET - same contrast as the reference row.
6. [must] Hero ~8 W x 7 D x 9 H studs. — MET - KITSTAT 8.7 x 7.2 x 8.9; renders about as wide as tall.
7. [should] Flat-shaded faceted look, crystals show long hex side faces, rocks show big chiselled facets. — MET - flat shaded; rocks are a little rounder/more ball-like than the reference's flat-topped boulders (see 21).
V1. [must] (verifier) Crystals are chunky prisms, width ~1/3 of height, angled multi-facet chiselled tips. — MET - main 3.1 across x 8.9, sides ~2.8 across; hero cell shows bulky shards with kinked shafts and chisel tips, no longer slim obelisks.
V2. [must] (verifier) Rock band ~30% of height, rocks overlap the crystal bases, no gaps. — MET - front cell: rock band reaches ~30% of the height, front fillers cover the crystal bottoms, no gaps visible between rocks and crystals.

## FRONT
8. [must] Front: symmetric fan, Main centre, sides tipping out, boulder band across the bottom ~1/4-1/3. — MET - front cell matches the reference fan, band ~30%.
V3. [should] (verifier) Front: rocks wide and low at the base, crystals not slim. — MET - wide boulder band spanning the full width, chunkier crystals.

## SIDE
9. [should] Side: tall Main with a shorter crystal in front, rocks at both ends. — MET - side cell shows the main with the right crystal overlapping in front and rocks front and back.
V4. [should] (verifier) Side: bulkier crystal mass, rocks piled in front and behind. — MET - side cell mass is wider than before, rocks at both ends; still a little narrower than the reference.

## TOP
10. [must] Top: rough ring of grey boulders around a central pale faceted crystal mass. — MET - top cell: crystal mass in the middle, boulders visible behind, at both sides and in front.
V5. [must] (verifier) Top: crystals centred in the footprint, rocks all the way round. — MET - crystals moved to the footprint centre (main y=0.35); rocks show on all four sides in the top cell, front ones partly under the side crystals (as in the reference).

## PARTS
11. [must] QuartzMainCrystal ~2.8 x 2.8 x 8.5 with a pointed faceted tip. — MET - 2.8 x 3.1 x 8.5, faceted chisel tip in the parts cell.
V6. [must] (verifier) Main Crystal is a faceted chunky prism with an angled chisel tip, not a plain pyramid. — MET - parts cell: kinked shaft, sloped shoulder, two bevel rings and a ridge tip (72 tris, was 34).
12. [must] QuartzSideCrystal ~5.5 high, ~2 wide, slightly angled off-centre tip. — MET - 2.0 x 2.3 x 5.5, off-centre slanted tip.
13. [must] QuartzBaseRock: two joined large boulders plus a small third rock, ~8 x 4 x 2.8. — MET - 7.8 x 3.6 x 2.8, two-boulder group and small rock in the parts cell.

## DROPS / DEPLETED
14. [must] QuartzCrystalDrop: chunky shard lying horizontally, pointed both ends, ~1.4 long. — MET - 1.3 x 0.8 x 0.9, lying, chisel points at both ends.
15. [must] QuartzCrystalDropB: more upright shard ~1.4 high, different facets. — MET - 1.0 x 0.8 x 1.4 upright with slanted tip.
16. [must] QuartzDepleted: only grey boulders (6-7, low ~2.2 H, ~7.5 W), no crystals, hero ring layout. — MET - 7 boulders 8.1 x 6.0 x 2.0, no crystals, hero ring positions.
V7. [should] (verifier) Depleted rocks not hidden by dust, hollow centre. — MET (partly) - harvest_deplete scaled to 0.35, rocks clearly visible; the hollow centre is not visible from the 3/4 camera (also not visible in the reference cell).

## PALETTE / SCALE / VFX
17. [must] Palette: r03_quartz (#D8CFC8) crystals, r03_rock (#8C7E78) rocks, no shade variants. — MET - only those two keys, verbatim; no shade-pair problems.
18. [must] VFX: harvest_hit at (0,-2.2,3) with quartz chips; harvest_deplete at (0,0,0.5) on hero and depleted; no ore_glint/light. — MET - sockets present as specified.
19. [should] All assets under budget, 0 problems. — MET - hero 872/3500, crystals 72, drops 88/72, base rock 214, depleted 490; 0 problems.
V8. [should] (verifier) Enough triangles for facet detail. — MET (partly) - crystals doubled to 72 tris with 7 rings; still far below budget by design (low-poly).
21. [should] Boulders read as flat-topped chunky angular rocks like the reference, not round balls. — UNMET - rocks are chunky but still rounder than the reference's broad flat-faceted boulders (rock() at subdiv=1 went to pointy icosahedra, subdiv=2 stays round).

## Iteration log
1-4 (first run): private-bmesh crystals, 7-rock ring; verifier failed it (slim crystals, sparse low rocks, crystals at the front in top view).
R1: new crystal(): 4-ring kinked hex shaft, sloped shoulder, bevel ring, 2-apex chisel ridge; wider crystals (r 1.6 / 1.1-1.2); bigger, taller ring; depleted dust scaled 0.35. Crystals chunkier; rocks still round.
R2: rocks at subdiv=1: pointy icosahedra, worse; added second tip bevel ring (72 tris per crystal); crystals moved back.
R3: rocks back to subdiv=2; two wedge filler rocks in front of the crystals raise the band to ~30% and bury the bases. Top view still crystal-heavy at the front.
R4: crystals recentred (perspective top camera), side crystals widened to r 1.38/1.42. Top view now centred and ringed; all musts met.
