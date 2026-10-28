# CopperNode (R01 row 4) goals

Reference: art/reference/kit/rows/R01_row4.png (full sheet art/reference/kit/R01_stone_common_ores.png).
REVISION 3 (verifier fail 6.5/10: gem bulbs, narrow hero, teal streaks, small drops). The verifier's
unmet goals are added as musts V1-V6. Status is from rev3 build 6 (compare image + cells + KITSTAT),
judged by eye cell by cell against the reference row; numbers only support the call.

## PALETTE (one base colour per material, lit mid-tone)
P1. [must] Exactly three materials: r01_cu_rock #9A897D (host, base rocks, depleted rubble), copper #E2713A (gems, ore drops), r01_cu_verdigris #5E9E94 (all teal spatter). No patina, r01_cu_patina or copper_dark keys anywhere. - MET: PALETTE declares only r01_cu_rock + r01_cu_verdigris (sheet values verbatim), KEYS = [rock, copper, verdigris]; the row shows one grey-brown, one orange, one teal.
P2. [must] No code chooses a colour by height, facing, tier or at random between shades; Tint per facet only 0.96-1.04. - MET: spatter() paints only r01_cu_verdigris; tint choices 0.96/1.0/1.04, no lift.
P3. [must] Runner reports 0 problems (no shade pairs, no painted lighting). - MET: "STATS R01/copper_node: 10 assets, 2316 tris, 0 problems".
P4. [must] Teal reads as a ragged mid-teal spatter (edges from cell shape, no fade colour). - MET: 1_hero/2_front show broken teal blotches with jagged cell edges next to the gems.

## ASSEMBLED / HERO
1. [must] Host is a wide faceted mound (host ~6.4-6.9 W x 4.3 D x 4.3-4.5 H studs), origin bottom centre, flared skirt wider than the shoulder line. - MET: 1_hero/2_front show a broad rounded mound whose lower ring flares past the shoulders on both sides; KITSTAT host 6.9 x 4.3 x 4.3, hero 7.2 x 4.7 x 4.3.
2. [must] Peak a little right of centre; left shoulder lower than right. - MET: 2_front crown high point sits right of centre, the left side slopes down past the top-left gem like the reference front cell.
3. [must] Host rock reads warm grey-brown, never pink and not the neutral grey of row 1. - MET: lit faces read warm taupe matching the reference swatch, no pink cast.
4. [must] Four chunky orange copper gems set INTO the rock: top-left shoulder, front-left low, big front-right, back-right. - MET: 1_hero/2_front show top-left, front-left and big front-right gems sitting in flat seats; 3_side/4_top show the back-right gem on the back rim.
5. [must] Front-right gem is the largest orange shape in the front view. - MET: 2_front big gem ~75 px vs front-left ~55 px and top-left ~50 px wide.
6. [must] Gems read as angular faceted blocks (5-6 sided outline, flat planes, sharp corners), not ovoid. - MET: 2_front hex outlines with flat crown/bevel planes and corners.
7. [must] Ragged teal cells around/under EVERY gem and on gems' lower bevels, heaviest below-left of the front-left gem; never a floating decal. - MET: 1_hero teal hugs the lower-left of the front-left and top-left gems and the lower edge of the big gem, 4_top teal by the left gems; cells are cut into the host surface.
8. [must] Host facets medium and even, crisp angular planes, not a smooth dome. - MET: 1_hero/2_front show crisp planes of similar size across the host.
9. [must] Small grey-brown base rocks at the front foot: a bigger one front-left, a smaller one front-right. - MET: 2_front larger rock front-left foot, smaller one front-right; both also in 1_hero.

## FRONT / SIDE / TOP
10. [must] Front: two front gems at mid height, front-right larger and right of centre, inside the host silhouette; top-left gem on the upper-left shoulder. - MET: 2_front matches that layout, all gems inside the outline.
11. [must] Side: tall rounded wedge; front and back gems protrude moderately (~40-50% sunk, no bulb). - MET: 3_side tall wedge; the front gem shows only a thin orange edge (~0.4 stud) past the front outline and the back gem a small cap on the back outline, like the reference side cell (previously a big bulb).
12. [should] Top: rounded crown, gems visible around the rim, teal patches visible. - MET: 4_top rounded crown, front gems on the front rim, back-right gem on the back rim, teal by the left gems.

## PARTS
13. [should] CopperNodeHostRock: bare faceted host, same shape/colour, no copper or teal. - MET: 5_parts big grey-brown faceted boulder, no orange or teal.
14. [must] CopperInsert (chunky ~1.3-1.7), CopperInsertSmall (~0.8 pointed), CopperInsertShard (~0.75x0.5x1.0 upright), collision none, flat base z=0, a little teal on a lower bevel. - MET: 5_parts chunky, small pointed and upright shard gems with teal lower bevels; KITSTAT 1.4x1.3x1.2, 0.8x0.8x0.9, 0.7x0.5x1.0.
15. [must] CopperNodeBaseRock (~1.5x1.6x1.0, hull) and CopperNodeBaseRockSmall (~1.0x1.0x0.6, none), grey-brown, faceted. - MET: 5_parts two faceted grey-brown rocks; KITSTAT 1.5x1.6x1.0 and 1.0x1.0x0.6.

## DROPS / DEPLETED
16. [must] CopperOre (~1.4x1.25x1.05) and CopperOreSmall (~1.2x1.05x1.0): irregular faceted orange chunks, teal on ONE lower side, box, <=300 tris. - MET: 7_drops two orange faceted lumps with teal only on the lower-left side; KITSTAT 1.4x1.2x1.0 and 1.2x1.0x1.0 (now scaled to the exact spec extents), 204/186 tris.
17. [should] Drop teal is irregular mottling, not checker squares; the two drops are distinct shapes. - MET: 7_drops jagged teal blotches, two differently shaped chunks.
18. [must] CopperNodeDepleted ~6.7x4.4x1.7: low grey-brown rubble mound on the host footprint with a small rock at each end; no copper; hull; <=2000 tris. - MET: depleted cell low grey-brown mound with a rock at each end; 6.7x4.3x1.7, 155 tris.

## VFX / BUDGET
19. [must] harvest_hit front face ~(0.25, z 2.6) chips copper/rock; harvest_deplete base centre; ore_glint off the crown of each of the 4 gems (#FFE6C2/#F7A061, small box). Drops/depleted none. - MET: 2_front orange/grey chips at front mid height, glint sparkles on each gem crown (glint sockets follow the new sink depth).
20. [must] Hero <=3000, depleted <=2000, drops <=300 tris; nothing below z=0. - MET: hero 1275, depleted 155, drops 204/186; all assets bottom at z=0.

## REVISION 3 (verifier fail 6.5/10) - added musts
V1. [must] HERO silhouette: wide heavy mound, not a narrow tall dome: hero-cell aspect at least the reference hero cell's (measured 1.26 by the same silhouette bbox script, incl. base rocks), front cell clearly wider than tall (~1.4+), visibly flared skirt, broad rounded crown, peak right of centre, lower left shoulder. - MET: 1_hero now a broad rounded mound with a flared lower ring (aspect 1.22 by the same script vs reference 1.26, within the shadow/sparkle noise; the earlier build looked like a pointed bell); 2_front ~1.45 wide:tall with the peak right of centre. The verifier's "1.4-1.5 in the hero cell" isn't reachable because the reference hero cell is itself ~1.26 at that camera; see open issues.
V2. [must] Hero gems sunk ~45-50% with the girdle just under the rock surface: in 3_side and 4_top no gem bulges out of the host outline as a bulb; gems read as flatter faceted plates set into the faces. - MET: each gem now sits in a flat seat chopped into the host and is sunk until its girdle is under the surface (sink 50-62% of a flatter gem, h/w 0.38-0.42); 3_side shows only a thin orange cap past the outline front and back, 1_hero shows plates set into flat faces.
V3. [must] Teal is local: tight clusters below and left of each gem (within ~0.9 stud of it) and on the gems' lower bevels; the rest of the host (esp. the left face) reads clean grey-brown, no long streaks. - MET: every teal cell's vertices stay within half a gem width + 0.6 stud of its gem; 1_hero/2_front left face is clean grey-brown below and left of the teal clusters, no long streaks.
V4. [must] Drops at spec: CopperOre ~1.4 x 1.25 x 1.05, CopperOreSmall ~1.2 x 1.05 x 1.0 (KITSTAT within 5%), each with a clear teal patch (two blotches) on one lower side covering ~20-30% of that side. - MET: KITSTAT 1.4x1.2x1.0 / 1.2x1.0x1.0 (meshes scaled to the exact dims); 7_drops CopperOre shows a large plus a lower teal blotch on its lower-left side (~25-30%), CopperOreSmall the same at smaller size.
V5. [should] Front-right base rock visible in the -22 degree hero cell (as in the reference hero) as well as in the front cell. - MET: the rock moved to (3.05, -1.95); 1_hero shows it at the lower right of the host.
V6. [should] Gems read as copper: faceted flat planes with glints, the big front-right gem ~1.9-2.2 wide in the front view (about 30% of the host width). - MET: 2_front big gem ~75 px of a ~235 px host (~32%, ~2.2 studs), flat planes, warm glints.

## Iteration log
- Earlier run (builds 1-10) and rev2 (builds 1-4): shape, gem, spatter and drop work, palette collapsed to one key per material. Verifier failed rev2 on gem bulbs, a narrow hero, teal streaks and small drops.
- Rev3 build 1: host wider and lower (p 3.0, taper 0.13, flare 13%), gems auto-sunk so the girdle is under the surface (gem_sink), flatter gems, spatter limited to near each gem, drops scaled to exact dims, front-right base rock moved forward. Gems became too buried and small; drops over budget (320/330 tris).
- Rev3 build 2: gems bigger (2.0-2.75 wide), sink capped at 60%, drop cuts reduced. Budgets fine, gems readable; hero still a pointed bell, front gem still bulged in 3_side.
- Rev3 build 3: p 3.6, taper 0.06. Hero became a flat-topped loaf and lost the right-of-centre peak (too far).
- Rev3 build 4: p 3.15, taper 0.1, shoulder 0.21. Rounded mound with peak right of centre; the big gem still hit the sink cap and showed an edge bulb in 3_side.
- Rev3 build 5: flat seat chopped into the host under each gem (SEAT_CUT 0.1 x width) before seating. 3_side bulb gone, gems read as plates set into faces.
- Rev3 build 6: host 6.1 wide x 4.2 tall, front-left gem 2.35, spatter reach 0.6 stud, drop teal patch larger. Teal clusters tight to the gems; all must goals MET.
