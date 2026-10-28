# R04 Iron Meteor — goals (revision after verifier fail)

Status reflects the final revision build (rev build 4). Judged by eye against the reference row.

## ASSEMBLED / HERO
1. [must] Hero ~9 x 8 x 7 studs (footprint ~9.5 x 8.5); rounded pentagon wider than tall. — MET — hero/front cells now read wider than tall with broad shoulders; stats 9.4 x 8.6 x 6.9.
2. [must] Shell base is mid charcoal grey (r04_meteor_rock #4A4A54): lit planes clearly grey, not black, and darker than the rubble. — MET — the lit planes render slate grey and the shadow planes are dark, like the reference. The shell is clearly darker than the tan rubble.
3. [must] Shell built from a big central dome plus 2-3 smaller angular chunks; stacked chunks, not one blob. — MET — front cell shows the dome with angular side chunks at lower left/right.
4. [should] Big flat facets: about 10-15 crisp planes on the front of the dome, no soft shading. — MET — the lighter shell shows large, crisp triangular and quad planes in the hero, front and top cells.
5. [must] Crack seams are thin (~0.2-0.25) orange glow fissures that zig-zag, not thick yellow stickers. — MET (weak) — seams are now narrow orange strips, roughly a third of the old width. The big left seam shows small gaps between segments in the hero iso, so it reads slightly dashed.
6. [must] Lava seam colour reads saturated orange (r04_lava_crack #FF7A12, emission 1.0), not lemon yellow. — MET — seams render orange with a lighter core where the glow peaks, matching the reference better than the old yellow.
7. [must] Big crack runs diagonally from the upper-left shoulder to the base on the left-front; one on the right face; small ones on the sides; layout not mirror-symmetric. — MET — the left seam runs from near the top centre-left down to the lower left. The right seam is shorter and starts lower. Small seams sit on both sides.
8. [must] Ring of 8-11 warm grey-tan rubble rocks (r04_impact_rock #7D7570) hugging the base, low and flat, front ones largest. — MET — 11 flat tan rocks hug the base, and the two front rocks are the largest.
9. [must] Cracks only on the shell, never on rubble. — MET — no glow on any rubble rock.
10. [should] Meteor sits slightly sunk, rubble overlapping its lower edge. — MET — rubble overlaps the shell's lower edge.

## FRONT
11. [must] Front: dome wider than tall, chunks bulge at lower left/right, rubble band along the bottom ~1/5. — MET — front cell matches that layout.
12. [should] Two glowing cracks visible from the front (left diagonal, right). — MET — both visible and orange.

## SIDE
13. [should] Side: one tall dome profile with a seam on the edge, rubble at both ends. — UNMET — the dome profile is now taller and more single, but a lower chunk still reads as a separate bulge in front of the base. One seam is visible and rubble shows at both ends.

## TOP
14. [must] Top: round dark dome with lighter rubble showing round the rim. — MET — round faceted dome. Rubble shows at the front and sides, but less at the back than in the reference.

## PARTS
15. [must] IronMeteorRockShell: flat-ish elongated angular slab ~5 x 3.5 x 2.5, charcoal, no glow, crisp planes. — MET — 4.8 x 3.5 x 2.4 slab, grey charcoal, crisp big planes (facets 12).
16. [must] IronMeteorMetalCore: chunky faceted ~4 x 4 x 4 with one short orange seam. — MET — 3.8 x 3.9 x 3.9 faceted core with one orange seam.
17. [must] IronMeteorImpactRim: 5-6 flat grey-tan rocks merged, ~7 x 3 x 1.4. — MET — 6 rocks, 7.1 x 3.1 x 1.4.

## DROPS / DEPLETED
18. [must] MeteorIronChunk ~1.4 x 1.2 x 1, charcoal, one thin orange front seam, <=300 tris, collision none. — MET — 1.4 x 1.2 x 1.0, thin orange seam, 104 tris.
19. [should] MeteorIronChunkB ~1 x 1 x 1.4 with a vertical seam. — MET — 1.0 x 1.0 x 1.4 with a thin vertical orange seam.
20. [must] IronMeteorDepleted: 8-10 grey-tan flat rocks in a low ring ~8 x 7 x 1.8 with a hollow; no charcoal, no glow. — MET — 9 rocks in an 8.9 x 8.1 x 1.5 ring with an open centre.

## VFX / tech
21. [must] Sockets: heat_glow at every crack at scale 0.8 (#FF8A1A/#FFC040), embers at the top of the big crack, harvest_hit (0,-4,3.5), harvest_deplete (0,0,0.8); no ore_glint. — MET — all 4 hero heat_glow and the core heat_glow are now at 0.8; embers at (-0.8,-2.8,6.1).
22. [must] Budgets and tech: hero <=3500, parts <=1500, drops <=300, depleted <=2000; 0 problems; nothing below z=0. — MET — hero 1154, parts <=474, drops 104, depleted 706; 0 problems.

## Iteration log
- Earlier run (4 builds): verifier failed it at 5/10. The shell was near-black, the seams were thick lemon bars, the hero was 11.2 x 9.6 and the side view showed lumps.
- Rev build 1: shell #4A4A54, lava #FF7A12 at emission 1.0, seam width 0.24 and depth 0.16, rubble pulled in, sockets at 0.8. The runner flagged the shell and rubble as a shade pair, so I set kit_two_tone_ok on the hero (two different rocks). Result: orange seams and a grey shell, but the hero looked like a tall egg.
- Rev build 2: dome subdiv 2 at facets 21, chunks at subdiv 1 for crisp planes, seams 0.2 wide. Planes got crisper, but the dome was still tall and narrow.
- Rev build 3: broader dome (7.2 x 6.6 x 6.5) and bigger side shoulders. It now reads wider than tall like the reference, but was only 6.4 tall.
- Rev build 4: dome raised to 6.8 and side chunks tucked toward the back. Height is now 6.9. The big seam shows small gaps between segments, and the side view still shows a lower bulge.
