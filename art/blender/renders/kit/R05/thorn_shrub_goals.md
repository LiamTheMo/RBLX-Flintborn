# R05 ThornShrub goals (row 4)

Status after revision build 4 (build 7 overall): all must goals MET by eye; one should goal (side cell) partial.

## ASSEMBLED / HERO
1. [must] Dense rounded packed mound, body ~7.5 W x 7 D x 6 H studs, wider than tall; only thorn tips beyond the body. — MET - 15 clumps (+8%) now pack into one dome with no gaps visible; 9.8x7.5x7.4 overall incl. thorn tips, leaf body ~7.6 wide
2. [must] One heavy trunk (base r ~1.0-1.15) rising from front-centre bottom, forking at z~2.5 into 3 limbs that rise and loop across the front over the foliage. — MET - hero/front cells show a thick brown trunk rising from the base and forking up-left, up-right and up-centre in front of the leaves (no flat log pile)
3. [must] 12-15 chunky faceted olive clumps, bigger one top-centre, small pointed lumps sticking up around the top. — MET - 15 large-facet icos, big top-centre clump, 5 pointed lumps along the crown
4. [must] 5-6 large fat pale cream cones (~2.5-3 long, base r ~0.75), bases visible on the shell: upper L/R, front-left, lower front-right down-out, left. — MET - 6 cones with fat bases now read as chunky as ref, all six clearly break the outline
5. [should] Limbs angular zig-zag with thick tapered faceted segments. — MET - tapered 6/7-sided segments with kinks at every joint; no pipe-like uniform logs
6. [must] harvest_hit at (0,-3,2.5) (leaf/thorn colours), harvest_deplete at (0,0,0.5). — MET - both sockets present; hit puff scaled 0.6 so it no longer hides the trunk
7. [must] Hero is darker olive than BerryShrub yellow-green leaves. — MET - leaves render olive, darker/less yellow than the berry shrub

## FRONT
8. [must] Round crown, brown trunk Y/loop clearly visible across lower-middle, thorns breaking outline. — MET - front cell shows trunk rising centre and forking into a Y over the leaves; thorns left/right/top

## SIDE
9. [should] Rounded mass, trunk visible at bottom front, thorns poking out. — UNMET (partial) - rounded mass with 3 thorns; trunk shows only as a brown lobe at the left (front) edge rather than at the bottom centre as in ref

## TOP
10. [should] Round rosette of clumps with 3+ cream thorns radiating around the rim. — MET - round rosette, 5 thorns radiate; brown limbs peek at the front rim

## PARTS
11. [must] Leaf Cluster: 3 overlapping faceted olive lumps ~3x2.5x2. — MET - left wide lump, taller right lump and a small front lump give a 3-bump silhouette, 3.3x2.2x2.3 (cell layout overlaps it with the Branch)
12. [must] Thorn: single cream faceted cone ~1x1x2.4. — MET - upright cream 6-sided cone 1.0x1.3x2.6
13. [must] Branch: stout trunk (r ~0.75, ~3.3 tall, flat cut top) with one 45-degree side limb to the left, ~3.5x2x3.5. — MET - parts cell shows a thick upright trunk with a flat top and one angled left limb: a clear Y like ref, 3.1x1.6x3.4

## DROPS / DEPLETED
14. [must] Thorns (x2): two fat cream cones ~1.8 long, one standing, one tilted ~60 deg; closed, z>=0. — MET - one upright, one tilted cone, base r 0.55, 0 problems
15. [must] Depleted: bare heavy trunk (base r ~0.9-1.0) with 5 tapered kinked limbs fanned ~5.5 wide x 4 tall; no leaves/thorns. — MET - heavy stump, low left/right limbs and three upright limbs of varied length, 5.6x4.1, bark only

## PALETTE / SCALE / BUDGET
16. [must] One key per material: r05_thorn_leaf #6F7F28 clumps, r05_thorn #DDBE96 thorns, r05_bark #7A5030 trunk; no shade variants. — MET - 3 keys, 0 problems
17. [must] Budgets: hero <=4000, parts <=1500, drop <=300, depleted <=2000; 0 problems. — MET - hero 1072, parts 20-152, drop 40, depleted 544
18. [should] Collision: hero/depleted hull, Branch box, rest none. — MET

## Iteration log
- Builds 1-3 (first run): ico clumps, beam limbs; verifier failed: flat log pile, thin thorns, Branch two stubs, cluster one ball, too wide.
- Build 4 (revision 1): rewrote trunk as one heavy rising trunk (r0.95) forking at z2.3 into 3 rising limbs + low limb, tapered cyl segments instead of chamfered beams; repacked 15 clumps; thorns r0.75; Branch = stout trunk + 45-degree left limb; 3-lump cluster; drop thorns r0.55 with 60-degree tilt; depleted heavier with kinked tapered limbs.
- Build 5: trunk base r1.15, limbs thicker (0.7->0.36), fork 2.5; third leaf lump moved to the front; depleted side limbs lowered.
- Build 6: trunk moved forward (y -1.9), low front clumps pushed back, harvest_hit puff scale 0.6 so trunk shows in front view.
- Build 7: limbs pulled in to y>=-2.9, clumps +8% for a packed dome. Side-cell trunk is still at the front edge.
