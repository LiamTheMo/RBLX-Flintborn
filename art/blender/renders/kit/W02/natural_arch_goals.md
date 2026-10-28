# W02 row 4 — NaturalArch: goals

Reference: `art/reference/kit/rows/W02_row4.png` (full sheet `art/reference/kit/W02_cliffs_ledges_terrain.png`).
Compare: `art/blender/renders/kit/W02/natural_arch_compare.png`. Module: `art/blender/scripts/kit/W02/natural_arch.py`.

Revision 3 (after the second verifier fail, resemblance 6/10). Goals R1-R9 are the verifier's unmet goals and fixes,
added as musts (its "should" fixes are kept as should). Every goal is re-judged from scratch on build 6. Earlier MET
claims that the verifier disputed (2, 11, 16, V1, V3, V4) are re-checked against the new renders, not carried over.

Status key: MET / UNMET, with one line of evidence from the latest compare render, a 800x600 debug render of the same
asset, or KITSTAT.

## Verifier goals (revision 3)
R1. [must] (H3) Nothing hangs into the hole top: the arch outline is a clean round faceted ring, no flat rectangular slab at the crown (hero, Narrow), and Wide has no boxy flat lintel. — MET: front cell and 800px front render show a round 6-facet arch with an apex and no hanging slab. Cause found and fixed: facade bottoms were projected from z=-5 along sloped facet normals, which slid them sideways so the flat crown block hung below its neighbours. Wide is now 8 facets under a ring of voussoir blocks.
R2. [must] (P3) TopSpan reads as a bulky rocky lintel: rock fills the full ~22 width and ~18 depth, faceted bulging front/back/ends, underside a 5-facet bridge arch rising 4+, grass only a 0.3-0.8 lip, 2-3 clumps. — MET: parts cell and front render show a full-width 22 x 17.2 rock band 6.5-7 tall on two springer feet, dark 5-facet arch rising 4.0, grass lip 0.2-0.6 past the rock, 3 clumps; KITSTAT 23.0 x 19.9 x 8.7 (clumps included).
R3. [must] Other parts' grass plates no wider than their rock (no floating discs). — MET: parts cell shows each cap lipping just past its rock; Left 10.1 wide, Right 10.9 wide including caps and clumps (KITSTAT).
R4. [should] (H12) Hero silhouette is a squat rounded mound with an arch (inverted U, rounded heavy shoulders), not tall and spiky. — MET: front cell is an inverted U, 34.2 x 23.0 (1.49:1, ref front ~1.4:1); shoulders drop 6.0 on a rounder profile, walls batter 2.4 (was 3.4); 3 shards in place of 5.
R5. [should] Left mass ~10 wide, springer a bulging faceted boulder cluster (not a trumpet flare), chunky foot boulder. — MET: KITSTAT 10.1 x 22.1 x 20.5; parts cell shows a columnar shaft under six faceted lumps bulging ~0.6 past it, and a 5.8 x 4.8 x 5.0 foot boulder at the front-left.
R6. [should] Right mass ~10 wide, cap trimmed to the rock, 1-2 bushes. — MET: KITSTAT 10.9 x 22.6 x 18.2; cap lips 0.2-0.6; 2 clumps on top (the ledge clump was removed).
R7. [should] Foot rocks: at least 2 chunky multi-facet boulders (front-left heaviest) and only 3-6 leaning shards. — MET: front cell shows the front-left boulder cluster (5.6 x 4.6 x 5.4 and 4.4 x 3.6 x 3.8) plus 2 right boulders; 3 shards (2 left, 1 right), 3.4-6.4 tall.
R8. [should] Bush clumps read as the reference's leafy dark-to-mid green, not a heavy uniform canopy hiding the cap; lime cap visible. — MET: clump count cut to 8 rim + 2 hanging + 2 corners (hero), 8 (Narrow), 9 (Wide), 3 (Broken left top); the lime cap shows between clumps in hero, Wide and Broken cells. All clumps are w02_bush: the runner now rejects shades of one material, and w02_bush matches the reference's leaf tone (sampled #33712B in shade).
R9. [should] Apron reads soft tan, not saturated orange. — UNMET (accepted): the apron must be w02_path #E2A86E, a fixed sheet key, and it renders orange under the studio sun. The verifier said to accept this if the key can't change. The path_dark seams are gone, so it reads as one soft surface.

## ASSEMBLED / HERO (iso)
1. [must] Hero bounding box about 32 W x 24 D x 22 H (each within ~2 studs; bush crowns add ~1). — MET: KITSTAT 34.2 x 24.7 x 23.0; rock ~31 wide, grass top ~21.
2. [must] A big round-arched hole runs through the full depth (12 wide x 13 tall); the iso shows the dark tunnel and its exit, and the backdrop shows through. — MET: hero cell shows the dark tunnel with the lit exit; front cell shows the backdrop through a round 12 x 13 hole.
3. [must] Soffit and tunnel lining in w02_rock_cool, clearly darker and bluer than the warm mauve front, so the hole reads dark-edged. — MET: hero and Wide cells show the blue-grey tunnel lining under the mauve voussoir ring.
4. [must] Each side mass is built from tall vertical columnar facets (at least 3 columns across each front), with vertical crevices. — MET: front render shows 3-4 tall prism columns per side, plus stepped shoulder columns.
5. [must] Leaning shards (3-9 tall) and at least 2 chunky boulders at the feet, front-left heaviest. — MET: see R7.
6. [must] Grass cap over the top: grass over a brown earth band, scalloped lip 0.3-0.8, domed. — MET: front and side cells show the earth band under a scalloped lip; dome 0.9.
7. [must] 8-12 bush clumps round the rim, at least 2 hanging over the arch face. — MET: 8 rim + 2 front-corner clumps, and 2 clumps hanging over the arch's upper corners in the front cell.
8. [must] Tan w02_path apron fans 4-5 studs out of the opening over a pale w02_slab sill that shows at its edges, with pebbles. — MET: front render shows the path fanning 4.6 out, pale sill bands either side in the hole, and pebbles.
9. [should] Base dressing: a green fringe, 15+ small bushes, tufts, flower dots and rubble. — MET: 16 base bushes, 18 tufts, 16 flowers and 9 rubble stones on a grass fringe (code); visible along the foot in the front cell.
10. [must] The front arch is framed by a ring of big chunky voussoir blocks (as in the reference), not a flat wall. — MET: the front render shows 6 bulging blocks round the opening, each about 6 deep at the crown, standing proud of the wall.

## FRONT
11. [must] Opening ~37-42% of the front width and ~55-62% of the height, with a round faceted top and the backdrop visible; outline an inverted U. — MET: 12/31 = 39% of the rock width, 13/21.2 = 61% of the grass height; round top with an apex; inverted-U outline.
12. [should] Domed grass top line with 5+ clump bumps and clumps on both upper corners. — MET: front cell top line has ~8 clump bumps, with big clumps on both corners.

## SIDE / REAR
13. [must] Side (+X): rock columns with a grass top over the front ~58% of the depth, a flat grey w02_connector face over the rear ~42%, tabs on its edge. — MET: side cell shows columns at the left (front) and the grey plate at the right (rear) about 42%; grass and clumps on top.
14. [must] Back +Y connector plate (inset 0.5, 0.4 thick) with the hole cut out so it stays open; tabs at 8-stud spacing. — MET: the plate outline is the hole grown 0.1 (code); the backdrop shows through in the front cell; tabs at z 4/12 on both edges.

## TOP
15. [should] Top view: broad grass with a clump ring, pebbles and flower dots; the tan apron and base fringe show in front. — MET: top cell shows the lime cap with a clump ring, flower dots, and the apron at the front.

## PARTS
16. [must] Four part assets in the parts cell at about spec size: Left ~10 x 22 x 20, Right ~10 x 22 x 18, TopSpan ~22 x 18 x 7, Sill ~14 x 10 x 0.6. — MET: KITSTAT Left 10.1 x 22.1 x 20.5, Right 10.9 x 22.6 x 18.2, Span 23.0 x 19.9 x 8.7 (rock 22 x 17.2 x ~7; clumps add the rest), Sill 14.2 x 10.0 x 0.6.
17. [must] Left mass: columnar pillar with a bulging springer, grass-tuft top and a big foot boulder; Right: columnar block with a grass top and 1-2 bushes. — MET: see R5 and R6. Both are columnar on every face.
18. [must] TopSpan: see R2. — MET.
19. [must] Ground sill: flat pale w02_slab slab, chamfered, with a crack seam. — MET: parts cell shows the bevelled pale slab and a crack line (soil in the crack, w02_earth).

## VARIATIONS
20. [must] A. Narrow ~24 x 20 x 22 with a tall narrow ~6 x 12 opening (>= 4 x 7) and thick pillars. — MET: KITSTAT 26.4 x 18.8 x 22.8; 6 x 12 opening with a 6-facet round top; pillars ~8.6 wide.
21. [must] B. Wide ~32 x 24 x 18 with a broad squat ~18 x 11 opening under a long thin span, dirt floor over a pale sill, no boxy lintel. — MET: KITSTAT 33.6 x 24.5 x 18.8; 18 x 11 opening under an 8-facet ring with a 4.1 span; tan floor with pale sill edges.
22. [must] C. Broken ~28 x 20: left ~20 tall with a broken stub over the gap, right ~12 stepped, ~10-wide walkable gap, 2-3 fallen chunks, grass and bushes on both tops. — MET: KITSTAT 30.6 x 20.8 x 20.8; stub over the 10-wide gap; right tops at 12.6 and 9.4; 3 chunks; lime caps with clumps on both sides, the left top thinned to 3 rim clumps.
23. [should] Variants share the hero's language (columns, voussoir ring, cap, clumps, apron) and read as one kit. — MET: Narrow and Wide use the same ring, columns, cap and apron; Broken uses the same columns, caps and clumps.

## Palette / technical
24. [must] Only palette keys: the sheet's w02_* keys copied verbatim, plus flower_white and flower_yellow. — MET: PALETTE holds the 15 w02_* keys verbatim.
25. [must] Runner ends with 0 problems; each asset under budget; one mesh each, origin at the bottom centre, nothing below z=0; collision precise for hero, variants and span, hull for masses, box for the sill. — MET: 'STATS W02/natural_arch: 8 assets, 23417 tris, 0 problems'; hero 5230/7000, Narrow 4752, Wide 5544, Broken 4742, Left 971, Right 934, Span 1154, Sill 90.
26. [must] One base colour per material (the runner's new shade-pair check): outer rock w02_rock (sampled render #9A8884-#AD9993 vs ref #8B838B-#BBA49F), grass w02_grass, clumps w02_bush, path w02_path, earth band w02_earth. Second colours only for real material changes: soffit lining w02_rock_cool, sill w02_slab, connector plate w02_connector. — MET: no shade problems; kit_two_tone_ok names each of these materials, and kit_shading_ok covers the soffit.

## Iteration log
Revision 1 (builds 0-6): boxy mound and a thin cap. The verifier failed it (5/10).
Revision 2 (builds 1-7): rounded mound, warm tone mix, bridge-style TopSpan. The verifier failed it (6/10): a crown slab, a table-like TopSpan, wide parts, and a spiky silhouette.
Revision 3:
1. Facade and core bottoms placed on the facet lines, not projected from z=-5. The crown slab is gone. TopSpan rebuilt as a full-width band of 7 blocks over a 5-facet arch. Left mass narrowed to 10, with a lump springer. Shoulders rounder (drop 6.0, batter 2.4), 3 shards. Bush tone mix lighter. Build 1 hit 7 problems from a new runner check (shades of one material).
2. One colour per material: rock_light for all outer rock, cool soffit, one grass, one bush, path without dark seams, earth crack in the sill. Waivers added for soffit, sill, connector and earth/path. 0 problems. The rock read too peach and the clumps too lime against the reference (sampled).
3. Rock switched to w02_rock (matches the reference's sampled mauve-grey), clumps to w02_bush. Facade rebuilt as a voussoir ring (6 deep at the crown) with a round 6-facet arch (Narrow 6, Wide 8 facets). Left mass rebuilt as a column grid plus six lumps. TopSpan raised. The springer blocks jutted out as shelves.
4. Springer voussoirs slimmer (T and forward bulge scale with the facet's tilt); fewer clumps (hero 8+2+2, Narrow 8, Wide 9); TopSpan rock to 6.5 with a 0.8 cap.
5. Broken's left top thinned to 3 rim clumps.
6. Code tidy only (legacy tone-mix fields), and a confirming build: 0 problems.
