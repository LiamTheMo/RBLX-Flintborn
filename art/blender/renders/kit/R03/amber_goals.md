# R03 Amber goals

Reference: art/reference/kit/rows/R03_row4.png. Revision after verifier fail (6/10). Status in [brackets] after the latest build.

## ASSEMBLED / HERO
1. (must) One large egg-shaped orange nodule dominates: ~5 wide x 6.5 tall, ~1.3x taller than wide, slight tilt. [MET: hero/front show a big upright egg 5.3 x 6.6 tilted slightly, the dominant mass as in the reference.]
2. (must) Nodule surface reads as a cut gem: 30+ small triangular facets, no smooth sphere. [MET: dozens of small triangular facets break up the egg in every cell; no smooth sphere.]
3. (must) Nodule top rises well above all wood (top ~25-35% clear), bottom third hidden by wood; nodule top at z ~8. [MET: front cell, top ~35% of the egg clears the wood; hero height 8.4, nodule top ~8.4.]
4. (must, verifier) Long diagonal split log across the front, ~8 long, ~1.5 thick, clearly angled ~20-25 deg, high at left, sloping down to the front-right; built from 2-3 overlapping split slabs, not one box bar. [MET: front/hero cells show the thick log stepping down from the left end (z~3.2) to the front-right ground in clearly kinked overlapping split segments, ~22 deg.]
5. (must, verifier) Upright broken spikes: left ~5 high and right-back ~6.5 high, tapering, slanted broken tops, framing the nodule in a U/V from the front. [MET: front cell shows a splintered spike at the left rising above the log end and a tall dark split slab at right-back reaching ~6.5, framing the egg like the reference.]
6. (should) 2-3 small wood chunks at the front-left corner. [MET: three blocky chunks plus a chip at the front-left corner in hero and front cells.]
7. (should, verifier) Hero footprint ~8 x 7 (width <= 8.5), height ~8.5. [MET: 8.2 x 7.6 x 8.4 studs; reads the same scale/proportion as the reference hero cell.]

## FRONT
8. (must) Front view: nodule centred, framed by a spike left and a taller spike right; front log crosses the lower third diagonally. [MET: front cell: egg centred, spike left, taller slab right, log crossing the lower third diagonally.]
9. (should) Front width : height about 1 : 1. [MET: front cell roughly square like the reference.]

## SIDE
10. (should) Side view: tall spikes beside the nodule, nodule rising above/behind them. [MET: side cell shows the tall splintered slab beside the egg with the egg rising behind, like the reference.]

## TOP
11. (must) Top view: egg centred inside a rough ring of crossing slabs on all four sides. [MET: top cell shows the egg centred in a ragged ring of crossing slabs on all sides.]

## PARTS
12. (must) AmberNodule part: the faceted egg alone, ~5 x 4.5 x 6.5. [MET: parts cell shows the lone faceted egg, 5.3 x 4.6 x 6.6.]
13. (must, verifier) AmberWoodBase ~9 x 5 x 4 (width <= 9.3): long diagonal split log with a tall spike at the left end and a taller spike at the right end, clear U silhouette, plus chunks. [MET: parts cell shows the long split log with an upright spike at the left end and a taller one at the right end (U), 8.0 x 5.4 x 4.0, chunks below.]
14. (should) AmberSideWood: small stump ~2 x 2 x 2.5, flat angled top. [MET: stump 1.7 x 1.6 x 2.4 with a slanted broken top and a small chip; slightly narrower than 2.]

## DROPS / DEPLETED
15. (must) Two Raw Amber drops: distinct angular faceted orange chunks, lying, closed, <=300 tris. [MET: two distinct angular orange chunks lying flat, closed, 80 tris each.]
16. (should, verifier) Drop A ~1.5 x 1.1 x 1.1, drop B ~1.2 x 1.0 x 1.4, ~40-100 tris each with irregular facets (not 20-tri blobs). [MET: A 1.5 x 1.1 x 1.1, B 1.2 x 1.0 x 1.4, 80 tris each with planar cut facets; B reads a bit pointier than the reference.]
17. (must, verifier) Depleted: low cradle ~8 x 4.5 x 2.5, no amber: long diagonal log in front, TWO short upright slabs (2-2.5 high) behind/beside it both visible from the hero camera, small chunk at front-left, some crossing slabs. [MET: depleted cell shows the long diagonal log in front, two short uprights (left and right) clearly above it behind, a crossing slab, and a chunk at front-left; 7.7 x 4.9 x 2.4.]

## PALETTE / MATERIALS
18. (must) Amber is ONE key r03_amber (#F28A1C, emission 0.5); renders saturated orange, never brown or pale. [MET (weak): one key, renders saturated yellow-orange, never brown; a touch yellower than the reference, but the sheet hex/emission are fixed.]
19. (must, verifier) Wood is ONE key r03_amber_wood (#7A4A2B), chocolate brown, chunky split slabs with angular chiselled faceted edges and broken ends; reads as split wood, not smooth lumber planks. [MET: one brown key; wood is now irregular faceted split pieces with jagged broken ends, splinters on the spikes and chips on the log; less planky than before, still a little blockier than the reference.]
20. (should) Only per-face tint variation (<=7%); no extra shade keys; 0 runner problems. [MET: two keys only, per-face tint +/-4%; runner reports 0 problems.]

## VFX
21. (must) heat_glow at (0,0,4) warm colours, soft light + motes; ore_glint (0,-2,4.5) x0.8 on the nodule; harvest_hit (0,-2.5,3) amber chips; harvest_deplete (0,0,0.5) on depleted. [MET: sockets heat_glow (0,0,4) warm colours + light 0.6 + motes, ore_glint (0,-2,4.5) x0.8, harvest_hit (0,-2.5,3), harvest_deplete (0,0,0.5); puffs visible.]

## Iteration log
- Builds 1-4 (earlier run): box slabs, nodule subdiv 3, 20-tri drops. Verifier failed: boxy near-horizontal log, short spikes, plank-like wood, hidden depleted slab, small drops.
- Build 5: wood rebuilt from irregular flattened polygon pieces (cyl, per-vertex split-line radial variation, jagged/slanted ends, per-face tint); front log 3 kinked segments, ~22 deg; spikes 5 / 6.5; nodule raised to top 8.4; drops ico+planar cuts at spec sizes. 1 problem (tint 1.27x).
- Build 6: per-face tint cut to 4% (0 problems); front log left end lowered so the left spike shows; all wood ~1.3x thicker; depleted log lowered and uprights spread so both show.
- Build 7: splinters added to every spike (stepped split look), sharper section variation, extra drop cuts (no pointy tops).
- Build 8 (final): logs 8-sided, front log 4 segments, 3 split chips on the logs. All must goals MET by eye.
