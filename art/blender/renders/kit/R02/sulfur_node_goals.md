# R02 SulfurNode goals

Palette: r02_base_rock #8C827D (warm light grey, all rock: slabs + base rocks); r02_sulfur #E6DB2E (acid lemon yellow, matte, chunks only). Sheet palette copied verbatim (verifier's "nice" suggestion #EEE63A not applied: the sheet palette must stay identical across the four R02 modules).

## ASSEMBLED / HERO
1. [must] Hero reads as a wide, low, flat tiered grey slab plateau with a yellow chunk pile on top; width ~1.4x+ height; pile ~40-50% of the height (verifier goal).
2. [must] 2-3 visible stacked slab tiers with stepped ledges / horizontal ledge lines on the front face.
3. [must] 3 big blocky yellow chunks + 1 small crumb on top: big one right-front, tall one back-centre, medium left; they overlap each other.
4. [must] Chunks are chunky rounded rectangular blocks with chamfered edges and a few big facets, NOT pointed crystals and not plain boxes (verifier goal).
5. [must] Chunk pile covers ~55-65% of the top slab.
6. [must] 4-5 small base rocks (1.4-2.4 studs) along the foot at left-front and right-front.
7. [must] Only two materials: lemon yellow chunks and warm light grey rock.
8. [should] Asymmetric tiers (top slab offset right, middle offset back) and an irregular, lumpy rounded plateau outline, not a regular octagon (verifier goal).
9. [should] Rock facets are large and few (low-poly chiselled), no noisy small facets.

## FRONT
10. [must] Front view: wide low stack of slabs, chunk pile on top centre-right, base rocks at both lower corners.
11. [should] Front view shows 2-3 horizontal ledge lines crossing the slab face.

## SIDE
12. [should] Side view: slabs stepped, chunks sit on top; tall block dominant.

## TOP
13. [must] Top view readable: irregular rounded slab outline with 3-4 yellow blocks covering ~45% of the area, not hidden by vapour (verifier goal).

## PARTS
14. [must] SulfurHostRock: slab stack without chunks ~10x8x5, flat tiered top (verifier goal).
15. [must] SulfurChunk: single chamfered faceted yellow block ~4x2.8x2.4.
16. [must] SulfurBaseRock: small faceted grey rock ~2x1.7x1.4.

## DROPS / DEPLETED
17. [must] SulfurChunkDrop: closed chamfered faceted yellow block ~1.5x1.1x1.0, <=300 tris, collision box.
18. [should] SulfurChunkDrop2: squat faceted chunk ~1.4x1.2x0.9, not a plain prism, visibly different from Drop (verifier goal).
19. [must] SulfurNodeDepleted: two low grey tiers ~10x8x3.2 with small rocks at ends, no yellow; caption 'Depleted (Base)' in notes.

## VFX / TECH
20. [must] Sockets: harvest_hit at (1,-3.5,5) yellow chips; vapour yellowish-white wisp above/behind pile, faint and small enough not to obscure the model (verifier goal); subtle second vapour; harvest_deplete at base of depleted; no ore_glint (matte).
21. [must] Build reports 0 problems; hero <=5000 tris, nothing below z=0.

## Status (after revision build 3)
1. MET - iso/front read as a broad low plateau with the pile on top (mesh 11.3x9.4x6.5, ratio 1.75); pile is ~45% of the cell height, slab walls no longer dominate.
2. MET - three tiers with clear ledge lines in iso, front and side cells.
3. MET - big block right-front, tall block back, medium left, crumb at right edge, overlapping.
4. MET - chamfered blocks now show several big jittered facets (96 tris each), no points.
5. MET - top cell: pile covers most of the top slab.
6. MET - 5 base rocks at left-front and right-front feet.
7. MET - only lemon yellow + warm grey in every cell.
8. MET - top cell shows a lumpy, non-octagonal outline; middle tier steps back and top tier shifts right in iso (offsets 0.9/1.0 stud).
9. MET - large slab facets and 80-tri base rocks.
10. MET - front: wide low stack, pile centre-right, rocks at both corners.
11. MET - 2-3 ledge lines across the front.
12. MET - side: stepped tiers, tall block on top; slab side reads darker (lighting) than ref.
13. MET - top cell now shows the yellow blocks and grey lumpy outline clearly; only a small wisp near the front edge.
14. MET - 10.3x8.0x4.7, three tiers, no chunks; reads like the ref Host Rock cell.
15. MET - 3.9x2.9x2.5 faceted chamfered block.
16. MET - 2.0x1.7x1.4 faceted grey rock.
17. MET - closed faceted block 1.7x1.35x1.0, 96 tris, box collision.
18. MET - 1.5x1.5x0.9 squat chunk with a sloped top, faceted, different from Drop.
19. MET - 10.3x8.4x3.1 two tiers, rocks at ends, no yellow; notes carry the caption.
20. MET - harvest_hit, 2 vapour (scale 0.5/0.3, smaller fainter emitters, at (0,0.5,7) and (-2,0.5,6.3)), harvest_deplete; no ore_glint. Vapour no longer washes out the top or hero cells.
21. MET - 0 problems, hero 1073/5000.

## Iteration log
- B1-B4 (first run): superellipse slab lofts, bevelled box chunks; verifier failed on tall/dark hero, octagonal outline, HostRock 3.4 tall, vapour hiding top cell, plain chunks.
- R1: lumpy 13-point outlines, tier offsets back/right, custom 10-sided chamfered chunk loft (96 tris) for chunks and drops, smaller/fainter vapour moved behind, HostRock rebuilt 10x8x5. Top readable; but slabs too thin, pile dominated.
- R2: thicker slabs (stack 3.6), flatter leaning chunks. Balance close to ref.
- R3: more chunk jitter for big facets, slightly wider bottom tier, lower tall block. All musts met.
