# R02 ObsidianNode goals (revision 2, after verifier fail 5/10)

Status is from the final build (build 8), judged by eye against the reference row.

## Palette
- G1 (must) Crystals use ONE key r02_obsidian; render reads near-black navy, glossy, not grey or royal blue. MET: crystals read near-black with navy sheen like the reference (build 6 was too blue; darkened to #1E2338).
- G2 (must) Rocks use ONE key r02_base_rock #8C827D; render reads light warm grey, clearly contrasting the crystals. MET: rocks warm light grey, strong contrast.
- V3 (must, verifier) Obsidian shows navy/blue edge highlights on the facets, not flat dark. UNMET (partial): chamfered edge strips and metallic 0.6 now give blue-grey sheen on several edges and facets (front and side cells), but not the reference's crisp, continuous light-blue edge lines on every edge; those are a stylised edge treatment that flat palette shading cannot reproduce.

## ASSEMBLED / HERO
- G3 (must) Three big crystals: tall centre-back, right one tilted out right, left-front one tilted left; tops fan outward. MET: tall centre crystal, right leans out right, left leans left; the tops fan out as in the reference.
- V1 (must, verifier) Crystals are fat, chunky gems, and the cluster reads broad, not narrow leaf spires. MET: tall crystal 6.8 x 5.4 at the belly, the right and left crystals 5.4 and 5.0 wide; hero 12.6 wide x 10.6 tall; the cell reads as a broad cluster of chunky gems.
- V2 (must, verifier) Crystal tips chamfered and truncated with broad shoulders (widest ~60% up), irregular facet planes, not symmetric points. MET: each crystal widens to ~58% up, has a shoulder ring and a chamfer ring, then a short off-centre point; facets split on random diagonals so planes are irregular. Tips are a little rounder than the reference's.
- G5 (must) Hero ~10-12.6 x 8-9.5 x 10.5 studs, about as wide as tall or wider. MET: 12.6 x 9.5 x 10.6.
- G6 (must) Broad skirt of light-grey boulders heaped round the crystal bases, biggest (~4.3 x 3.6 x 3.4) centre-front, covering the lower ~25-30%. MET: big centre-front boulder plus large left-front, left, right and rear boulders and small front rocks ring the whole base.
- G7 (should) Small rocks along the front edge (2-4 under 1.5 studs). MET: 4 small rocks along the front and front corners.
- G8 (should) Small 4th crystal low right, visible. MET: the small crystal shows at the right base in the hero and front cells.
- G9 (must) <= 5000 tris, 0 problems, hull collision. MET: 858/5000, 0 problems, hull. The facet count is deliberately low: larger facets match the reference's big planes better than many small ones.

## FRONT
- G10 (must) Centre crystal highest, crystal tops form a fan. MET: front cell shows the centre peak with the right and left crystals lower and fanning out.
- G11 (should) Rocks across the full base width in front. MET: a row of rocks spans the base.

## SIDE
- G12 (should) Crystals overlap as one mass with a big grey rock front-lower. UNMET (partial): crystals now bunch as one dark mass, with a grey rock at the front-lower right, but it is smaller and less central than the reference's big rock.

## TOP
- G13 (should) Dense dark crystal mass with grey rocks peeking out on several sides. MET: top cell shows a dark mass with rocks peeking out at the rear, the left, the right and the front.

## PARTS
- G14 (must) ObsidianChunk: one big fat elongated crystal lying diagonally, ~7.5 long, pointed. MET: a fat 6.8 x 3.0 x 5.0 chunk lying diagonally with a chamfered point; reads like the reference's chunk.
- G15 (must) ObsidianChunkB: shorter fat pointed crystal ~3 x 2.6 x 4.5. MET: upright gem, 3.1 x 2.6 x 4.3.
- V4 (should, verifier) ObsidianChunkB has no stray bright white face. UNMET: one facet still mirrors the bright sky as a white patch at this camera angle (pure glossy specular, no emission). Roughness was raised from 0.18 to 0.26, which softened it but did not remove it.
- G16 (must) ObsidianHostRock: flat cracked plates ~7 x 5 x 2, two big plates meeting at a crack plus smaller plates. MET: 4 bevelled irregular plates (5-6 sided) with visible cracks plus 2 small plates, 7.5 x 6.3 x 2.2.
- G17 (should) ObsidianBaseRock ~1.4 x 1.2 x 1.0. MET: 1.5 x 1.2 x 0.9 faceted rock.

## DROPS / DEPLETED
- G18 (must) ObsidianChunkDrop: elongated pointed shard ~1.8 x 1 x 1, closed, <=300, box. MET: 1.8 x 1.0 x 1.3 fat pointed shard, 138 tris.
- G19 (should) ObsidianChunkDrop2: short pointed shard ~1.2 x 1 x 1.6. MET: 1.3 x 1.0 x 1.5.
- G20 (must) ObsidianNodeDepleted: cracked flat slabs and small rocks, ~8 x 6 x 2.5, no crystals. MET: 8.8 x 6.3 x 2.6, with bevelled plates and 3 small rocks.

## VFX
- G21 (must) harvest_hit (0,-3,4) in obsidian colours; harvest_deplete at the base of the hero and the depleted state; ore_glint (0,-1.8,6) s1.0 and (3,-1.5,4.5) s0.8; no light. MET: sockets present; the chip burst shows on the front face.

## Iteration log
- Builds 1-4 (first run): see the earlier notes. They ended with slim leaf-like spires and failed the verifier.
- Build 5: rewrote crystal(): 5-6 irregular sides with chamfered vertical edges (paired verts), widest at 58%, shoulder and chamfer rings, off-centre apex, faces split on random diagonals; spread crystals, wider rock skirt, depleted taller. Result: fatter gems; edges still weak; white specular patches.
- Build 6: obsidian #283050, roughness 0.16, metallic 0.45, more rings. Result: too royal-blue, and the extra rings made the crystals rounder and lumpier. Worse.
- Build 7: darkened to #1E2338 and went back to 5 bold rings. Result: near-black again; the white patches remain.
- Build 8: roughness 0.26, metallic 0.6 (tinted, softer highlights); crystals 8-10% wider; chamfers narrower for a crisper silhouette. Result: broad chunky cluster; the blue sheen on edges is better but still not crisp lines. This is the final build (4-build cap).
