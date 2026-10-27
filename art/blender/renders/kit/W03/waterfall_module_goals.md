# W03 row 2 - Waterfall Module: visual goals

Reference: `art/reference/kit/rows/W03_row2.png` (cells: ASSEMBLED, FRONT, SIDE/REAR, TOP,
PARTS (EXPLODED), VARIATIONS) and the full sheet `art/reference/kit/W03_shorelines_waterfalls_river.png`.
Compare image: `art/blender/renders/kit/W03/waterfall_module_compare.png`.

Status is updated after every build (MET / UNMET + one line of evidence, judged by eye against the
reference row; pixel samples only support the judgement). Light tops / dark sides in the reference
are lighting, not paint: every material is one base colour with a small random Tint (+-8%) centred
on 1.0. Revision 9 removed the rock's uniform ROCK_SCALE factor (it broke the Roblox export).
Revision 9 (verifier fail 7.3/10, export palette problem): goals V9a-V9d added.

Revision 6 (verifier fail, resemblance 6.5/10): verifier goals added as V6a-V6f (musts and shoulds).
Revision 7 (rework from the user: one colour per material, water and vapour are VFX, underwater is
w03_riverbed): goals RW1-RW9 added as musts; every goal re-judged after R7 build 3.

## ASSEMBLED / HERO (WaterfallModule)

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| H1 | must | Footprint 32 x 32 (+-0.2) studs, cliff-top grass at z=20.5 on a 0.5 soil band, overall height 26-29 with pines (cliff body ~21-23 with crowns). | MET | R6 build 3: KITSTAT 32.0 x 32.0 x 28.6; caps at 20.5 over the brown soil lip |
| H2 | must | Cliff reads as chunky columnar w03_rock prisms (fat hexagonal front columns, proud stepped columns in front, side rows), bevelled tops, deep vertical crevices; not a flat wall. | MET | R8 build 6: hero/front: 2-3 fat creased hex columns a side plus stepped corner columns, chamfered crowns, dark V crevices (superseded detail: see V8a/V8b) |
| H3 | must | A notch ~8 wide centred on x=0 at the lip; behind the fall the cliff face is recessed, so the cyan curtain beam reads against it. | MET | front cell: ~8-wide slot between the framing columns (which rise ~2 above the grass), recessed notch wall |
| H4 | must | Bright cyan curtain (2 waterfall_curtain beams, x=-2/+2, width 4.5) from the lip (z~20) to the pool (z~1), leaning out ~1.5; reads against the grey rock. | MET | hero/front: cyan streaked sheet from lip to pool, clearly bluer than the rock |
| H5 | must | White spray at the fall foot (waterfall_mist 1.3 + vapour + water_foam ring) as a white cloud >= the curtain width. | MET | front cell: white cloud at the foot as wide as the curtain, foam patches round it |
| H6 | must | Two grass caps split by an ~8-wide w03_water channel at z=20.0 from the back edge to the lip; brown soil band under every grass rim. | MET | top cell: cyan channel from the back edge to the lip between two green caps; soil lip on the rims |
| H7 | must | 5-6 pines (7-8 tall) on the cliff tops plus 1-2 at the front-left foot. | MET | hero/front: 3 big pines on each cap (one on the raised left shoulder), 2 at the front-left foot; cap pines ~15% taller than before |
| H8 | should | w03_bush bushes and >= 8 white daisies along the cliff-top rims; 1-3 boulders / rock crowns on the caps. | MET | top cell: daisies scattered on both caps, many bush clumps, grey rock crowns at the back corners and cap boulders |
| H9 | must | Round pool (flat w03_water z=1.0, w03_riverbed bed z=0.2) in the front ~40-45% of the tile, saturated cyan; a narrow w03_sand rim above the waterline, small land at the front corners. | MET | R8 build 6: top/hero cells: a big round cyan pool nearly edge to edge over the teal bed, thin sand rim, small corner wedges |
| H10 | must | 5-9 faceted w03_rock boulders in and around the pool (two big front pair), each with a water_foam socket, no foam geometry. | MET | hero/top: big front pair plus rim boulders, a white foam patch at each |
| H11 | must | Pool exits the front edge centre as a 12-wide mouth (x -6..6) at z=1.0. | MET | front cell: 12-wide water gap in the front bank |
| H12 | should | Stepped columns (ledges) at the sides carrying bushes / ferns; grass bank at the front-left with a pine. | MET | hero/front: low proud columns with bush/fern tops on both sides, front-left bank with 2 pines |

## FRONT

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| F1 | must | Rock columns frame the fall on both sides; the curtain is the central ~25-30% of the width, lip to pool. | MET | front cell: columns either side, central cyan curtain from lip to pool |
| F2 | should | White spray at the foot ~30-45% of the width; pines above the cliff top on both sides. | MET | front cell: spray ~30% wide; 3 + 3 pines |

## SIDE / REAR

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| S1 | must | Side view: separate columns of mixed height with plants on the stepped ones, grass top with pines, curtain past the face, pool and boulders at the foot. | MET | side cell: tall and stepped prisms with bush/fern ledges, pines on top, curtain and pool at the right |

## TOP

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| T1 | must | Top: cyan channel from the back edge to the lip splits two green halves; white foam at the fall foot mid-tile; round cyan pool with boulders in the front ~40%. | MET | R8 build 6: top cell: channel between green halves, white foot mid-tile, large round pool with boulders and foam swirls (see V8e) |

## PARTS (EXPLODED)

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| P1 | must | WaterfallTopWaterPlane: flat 8-wide channel water slab (tileable section) over its riverbed; water_flow + 2 waterfall_curtain sockets; collision none; <= 400 tris. | MET | R7: 22 tris, 8.0 x 2.6 x 0.7, w03_water over w03_riverbed; the cyan slab sits alone in the front row of the parts cell |
| P2 | must | WaterfallCliffTop: grass-capped block with soil band, bushes and daisies; precise; <= 4000 tris. | MET | 494 tris, 7.5 x 3.5 x 6.7, precise; green cap with bushes and daisies over a soil band and rock prisms |
| P3 | must | WaterfallCliffWallA/B/C: three fat hexagonal columns ~6-7 wide, ~14 / ~10 / ~6 tall, bevelled crowns, facet breaks, rubble at the foot; hull; <= 1500 each. | MET | R8 build 6: 14.1 / 10.0 / 6.1 tall, 6.2-7.3 wide, 82-92 tris, hull; parts cell shows crisp hex pieces with chamfered tops |
| P4 | must | No WaterfallCurtain / FoamRibbon / SplashDisc mesh assets; they are sockets named in the hero notes. | MET | 6 parts only; hero notes name VFX_WaterfallCurtain_N / FoamRibbon_N / Splash |
| P5 | should | Parts cell reads as an exploded layout with every piece visible. | MET | parts cell: walls A, B at the back, wall C and the cliff top in front of them, the water slab in front |

## VARIATIONS

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| V1 | must | WaterfallNarrow: ~4-wide notch, one curtain beam width 4, smaller pool. | MET | variant 1 cell: single slim curtain in a tight slot between stepped columns, smaller round pool |
| V2 | must | WaterfallWide: ~16-wide lip, four curtain beams (width 4.5) reading as one broad fall over a wide pool. | MET | R7 build 3: variant 2 cell shows one broad cyan sheet about half the tile width over a wide pool |
| V3 | must | WaterfallTwoStep: upper fall into a mid ledge basin (w03_water z=11 over riverbed), lower fall to the pool; ledges with fern/bush; mist + foam ring at each foot. | MET | R7 build 3: variant 3 cell shows two stacked falls with a white splash between them at the ledge, and plants on the ledges |
| V4 | must | Every variant 32 x 32, same seams (8-wide channel at the back z=20, 12-wide mouth at the front z=1.0). | MET | all 32.0 x 32.0; shared seam code |

## COLOUR / VFX

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| C1 | must | One palette key per material: w03_rock, w03_grass, w03_soil, w03_sand, w03_riverbed, w03_water, w03_bush, pine, bark, flower_white, flower_yellow (w03_water_shallow removed). | MET | R7 stats: only these 11 keys on every asset; the render shows one grey rock, one green turf, one cyan water |
| C2 | must | No material or Tint picked by height/direction; Tint a small random variation centred on 1.0 (no material-wide factor). | MET | R9: ROCK_SCALE removed; rock_fn gives w03_rock one random value per rock (0.96-1.04, +-1.5% per face); exported w03_rock row levels 0.92-1.08; 0 problems |
| C3 | must | Build ends with "0 problems". | MET | R7 build 3: 0 problems, no shade pairs |
| C4 | must | No water-effect geometry (curtain, foam, splash, ripples, flow stripes); only flat water surfaces. | MET | only flat slabs; all effects are sockets |
| C5 | must | Rock is one grey-lilac key, the shared sheet value w03_rock #B2AFBA (same as the other W03 modules). | MET | R9: PALETTE w03_rock = #B2AFBA verbatim, no multiplier; the exported palette row is #B2AFBA at levels 0.92-1.08 |
| C6 | must | Sockets per spec: curtain at every lip, mist + vapour at every foot, foam ring + boulder + rim foam, water_flow on channel and pool. | MET | hero: 2 curtain, splash, vapour, foam ribbon ring, pool/rim/channel foam, 2 flow |

## REVISION 5: verifier goals

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| R1 | must | HERO: chunky prisms of mixed heights plus proud stepped columns, bevelled tops, deep shadowed crevices; not a flat box with a notch. | MET | R8: superseded by V8a/V8b (fat 5-7 wide hex columns, 2-4 a side); front cell shows stepped crowns and dark crevices |
| R2 | must | HERO: rock mid-tone matches the reference's mid grey-lilac. | UNMET (blocked) | R9 build 3: with the multiplier gone the cliff reads pale cool grey, lighter than the sheet (front-cell median #AFABAF vs #9E96A1). Needs the sheet-wide w03_rock change, see V9a and the open issue |
| R3 | must | HERO: round pool (~30 x 16 ellipse, small land + sand collar at the front corners), saturated cyan, >= 5 boulders with foam, 12-wide mouth. | MET | R8 build 6: top/hero cells: large round saturated cyan pool, thin sand rim, 9 pool boulders with foam, 12-wide mouth |
| R4 | must | HERO: curtain reads as a saturated cyan beam against grey rock with a white spray cloud at the foot >= curtain width. | MET | hero/front: cyan sheet over the grey rock, white cloud at the foot ~curtain width |
| R5 | must | Overall silhouette: massive cliff with an irregular top (no two neighbouring crowns level), cliff taller (20.5) than the pool is deep (16), side corners stepping down, asymmetric. | MET | hero/front: rock crowns and a pine shoulder 1.5-2.5 above the grass, corners recede (4.6 / 3.6) and step down to low ledge columns |
| R6 | should | HERO: >= 5 green bush/fern tufts on the cliff face and side ledges, daisies on the banks, rubble at the wall feet. | MET | front cell: bush/fern on every low proud column, crevice ferns, bank daisies, rubble |
| R7 | should | PARTS: every piece visible. | MET | parts cell shows all 5 pieces, the water slab alone in front |
| R8 | should | VARIATIONS: Narrow and Wide read differently (tight slot vs broad sheet). | MET | variant cells: one slim curtain between high walls vs a broad 14-wide sheet |

## REVISION 6: verifier goals (fail, resemblance 6.5/10)

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| V6a | must | HERO: tall columnar cliff spanning the tile with chunky prisms (now fat 5-7 wide hex columns per the R8 verifier), light bevelled tops visible, deep crevices (wall set back 2.4 under the cap), side ledge columns, recessed notch. | MET | R8 build 6: see V8a-V8c; side cell shows 2-3 fat side columns with plant ledges |
| V6b | must | Overall silhouette: massive cliff with an irregular top outline (rock crowns and grassy shoulders 1.5-3 above the cap), outer corners recessed and stepping down, taller than the pool is deep; not a box. | MET | hero: top outline broken by the framing crowns, a pine shoulder at the left, rock crowns at the back corners and crowns along the sides; front corners step down to 6-11 tall ledge columns |
| V6c | must | The -X side face reads as separate stacked columns with crevices and stepped ledges, not a plain wall. | MET | hero/side cells: the left face is a row of alternately proud (lower, plant-topped) and recessed (tall) prisms with gaps between them |
| V6d | should | Cap pines ~15-30% bigger than before (crowns ~7-8 above the cap); more daisy and bush clusters and 2+ cap boulders/rock crowns. | MET | cap pines 1.15x (top z 28.3-28.6), 24 cap daisies, 5 more bushes, 3 rock crowns + 3 cap boulders |
| V6e | should | Parts cell: all 5 parts clearly separated, none hiding another (tall walls at the back, cliff top and water plane in front). | MET | parts cell: A and B at the back, C and the cliff top in a middle row, the slab in front; C covers only A's foot |
| V6f | should | One sheet-wide rock colour: w03_rock = #B2AFBA as in the shared W03 palette. | MET | PALETTE copied verbatim from the sheet palette |

## REVISION 7: rework goals (one colour per material; water and vapour are VFX; riverbed)

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| RW1 | must | PALETTE is exactly the sheet's 7 keys (w03_grass, w03_soil, w03_sand, w03_rock #B2AFBA, w03_riverbed #0B6E8F, w03_water #18CFFA roughness 0.15, w03_bush), identical to the sheet spec; no shade variants of any material. | MET | module PALETTE copied verbatim; w03_water_shallow and its shore band are gone; the pool and channel read as one cyan |
| RW2 | must | No code picks a material or Tint by height, direction, tier or at random between shades; Tint is a small random variation centred on 1.0. | MET | R9: rock_fn random per rock, no ROCK_SCALE; 0 problems |
| RW3 | must | Runner reports 0 problems (no shade pairs). | MET | R7 build 3: "0 problems", shade_pairs empty on all 9 assets |
| RW4 | must | Everything under a water surface is w03_riverbed: pool bed z=0.2, the shore slope below z=1.0, submerged boulder and column bases (cut at the waterline), the channel bed and its under-water banks, and the tile-edge walls under the water skirts. | MET | side/hero cells: dark teal shows through the pool round the boulder feet and along the shore; the top channel reads deeper cyan over its teal bed |
| RW5 | must | Sand sits only above the waterline (the bank collar at z=1.2 and the shore band 1.2 -> 1.0); no sand under the water. | MET | hero/top cells: thin sand rim on the bank, the pool floor reads teal-cyan, not sand |
| RW6 | must | Hero sockets: 2 waterfall_curtain beams at x=-2/+2, z=20.05, width 4.5, end (x, lip_y-1, 1.0); waterfall_mist 1.4 + vapour above it; 7 water_foam ring sockets (0.7) round the impact zone, one per pool boulder and 4 on the rim; water_flow on the channel (y=+16 -> lip) and the pool (impact zone -> y=-16). | MET | hero/front cells: cyan curtain lip to pool, a white splash cloud at the foot, foam rings round the foot and every pool boulder; stats list 2 curtain, 1 mist, 1 vapour, 2 flow, 20 foam |
| RW7 | must | Variant sockets: Narrow 1 curtain width 4 and mist 1.0; Wide 4 curtains width 4.5 across a ~16-wide lip, mist 1.8 + 2 vapour, a 10-socket foam ring; TwoStep 2 curtains per tier, mist + vapour + foam ring at the basin and the pool, a water_flow across the basin. | MET | variant cells: one slim fall / one broad 4-beam sheet / two stacked falls with white at both feet; stats: 1 / 4 / 4 curtains, 1 / 2 / 2 vapour |
| RW8 | must | No water-effect geometry anywhere (curtain, foam, splash, ripple, flow); the hero and top water plane notes say the sheet's 'Waterfall Mesh (Curtain)', 'Foam Ribbon' and 'Splash Disc' are the waterfall_curtain, water_foam and waterfall_mist (+vapour) sockets. | MET | parts cell has only walls, cliff top and the flat slab; notes on both assets name the three sockets |
| RW9 | should | No per-module water transparency override (the shared w03_water keeps the sheet-wide default); the riverbed gives the deep cyan. | MET | set_water_transparency call removed; the pool still reads saturated cyan in every cell |

## REVISION 8: verifier goals (fail, resemblance 6.5/10: spindly slab columns, pale rock, small pool)

The R6/R5 goals H2, R1 and V6a (narrow 3-4.5 wide prisms) are superseded by V8a/V8b: the reference
columns are fat. Every R8 goal is a must unless tagged otherwise.

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| V8a | must | HERO silhouette: one massive cliff block spanning the tile, ~21 tall plus pines to ~27, stepped irregular top; reads as a heavy solid mass, not thin spires (front cell: no skinny tower stacks flanking the fall). | MET | R8 build 6: hero/front cells show two broad rock masses of 2-3 fat columns each flanking the fall, crowns only ~1 above the grass, outer columns stepping down; 32 x 32 x 28.6 |
| V8b | must | HERO facets: fat hexagonal columns 5-7 wide (2-4 per side on the front face), 6-sided cross-sections, visible light bevelled crown on each (chamfer ~0.8-1), 1-2 mid-height facet breaks; deep V crevices between neighbours. | MET | hero/front: each column shows two big front planes meeting at a vertical crease (one lit, one shaded), a light chamfered crown on the stepped ones and a kink where the faces break; 2 front columns + 1 proud + corner steps a side |
| V8c | must | Crevices and the set-back wall read DARK by lighting alone (back wall inset >= 2 studs under the cap soffit, V gaps narrow and deep); no painted dark colour. | MET | R9 build 3: front and hero cells show a dark slot between every pair of front columns (0.4-0.7 gaps to a wall set back 3.4 under the soffit); side cell shows slots between the side prisms too |
| V8d | must | HERO rock base colour: one w03_rock key; the rendered rock mid-tone reads as the reference's mid grey-lilac, not washed out. | UNMET (blocked) | Superseded by V9a: one key and no shading split are met, but the tone is the sheet key's pale grey until the sheet-wide w03_rock is lowered |
| V8e | must | TOP cell: cyan channel from the back edge to the lip between two green halves, white foam mid-tile, and a LARGE round pool: the front ~40-45% of the tile mostly cyan out to the side edges and the front, only small land wedges at the front corners; foam rings dense round the impact zone, boulders and rim. | MET | top cell: cyan channel between the green halves, white splash at mid-tile, and the front ~45% is cyan nearly edge to edge with foam swirls round the foot, boulders and rim; only thin sand/grass strips at the sides and corners |
| V8f | must | Pool ~30 x 16 (ellipse rx 15, ry 8.2), 12-wide mouth unchanged; >= 8 rim / mouth foam sockets plus an 8-socket ring at the foot. | MET | HERO pool (0, -7.4, 15.0, 8.2); 8 VFX_PoolRimFoam + 8 VFX_WaterfallFoamRibbon sockets; mouth x -6..6 |
| V8g | should | PARTS: WaterfallCliffWallA/B/C are fat hexagonal chunks (hex cross-section, bevelled crown, 1-2 facet breaks, rubble at the foot) as the sheet's pieces. | MET | parts cell: three crisp hexagonal columns with flat chamfered crowns, A with visible facet kinks, rubble chunks at the feet; 82-92 tris each (cheaper than 150, but the shape reads; no tris wasted) |
| V8h | should | 6-10 small rubble stones and 3-4 more bush clumps with daisies along the cliff foot. | MET | 10 foot rocks (shallows and side banks), 4 more bushes on the side banks (one skipped: no ground), 10 bank daisies; visible in the hero/front cells |
| V8i | must | Overall mass: the cliff reads as broad and heavy (column widths ~1/5-1/6 of the tile, not ~1/9). | MET | front cell: each column ~1/6 of the tile wide (5-6.8 studs); the cliff halves read as two heavy blocks |

## REVISION 9: verifier goals (fail 7.3/10: rock tint multiplier broke the Roblox export)

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| V9a | must | HERO rock base colour: one w03_rock key, mid-tone grey-lilac (~#9A97AA), no painted shading, no shade split. | UNMET (blocked by the sheet palette) | One key, no shading and no split are met (R9: w03_rock only, Tint 0.96-1.04). The tone is not: by eye the cliff is a paler cool grey than the sheet's (front median #AFABAF vs #9E96A1, hero #C2BDC4 vs #A0969E). The rules require the sheet palette verbatim and identical in all four W03 modules, forbid tint multipliers, and this module may not edit flintkit or the other modules. Only a sheet-wide w03_rock of ~#9D9AA6 can fix it, and that is filed as a shared request |
| V9b | must | (new) Roblox export of the module succeeds with 0 problems, so the in-game rock colour matches the render. | MET | R9 build 3: export_kit_roblox.py: "9 assets, 14 pieces (9 solid, 5 water, 0 glow), 22375 tris, 136 vfx sockets ... 0 problems"; the w03_rock row is #B2AFBA at levels 0.92-1.08 |
| V9c | should | Crevices between columns read as dark vertical slots, not mid grey. | MET | R9 builds 1-3: front columns spaced 0.4-0.7 apart (were overlapping) onto a wall set back 3.4 (was 2.4); front/hero cells show a dark slot at every seam, and the side cell shows slots between the side prisms |
| V9d | should | WaterfallCliffWallA/B/C: one more facet break per column and a few rubble stones at the feet (chunkier). | MET | R9: breaks 3 (A, B) / 2 (C), 4 rubble stones each (122-124 tris, were 82-92); the parts cell shows kinked hex columns with a rubble cluster at each foot |

## BUDGET, TECH

| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| X1 | must | Hero and variants <= 8000 tris; parts within budget; origin bottom centre, nothing below z=0. | MET | R9 build 3: hero 7166, Narrow 4742, Wide 4188, TwoStep 5431 / 8000; parts 22-456; 0 problems |
| X2 | must | Collision: hero/variants precise, wall pieces hull, cliff top precise, top water plane none. | MET | kit.tag collisions as listed |

## Open issue (rock colour, sheet-wide)

The shared sheet key w03_rock #B2AFBA renders paler than the reference under the kit lighting
(R9 front-cell rock median #AFABAF vs the reference's #9E96A1). R8 darkened it with a uniform Tint
factor (ROCK_SCALE 0.76), but the Roblox exporter could not fit those tints into the w03_rock palette
row ("row is full, a tint lands 0.220 from its level"), so R9 removed it: the rock is the sheet key
exactly and the export is clean. The fix is a sheet-wide w03_rock of ~#9D9AA6 in the W03 palette
(all four modules at once). That is outside this module's ownership and is filed in
shared_lib_requests. V9a (and R2/V8d) stay UNMET until then.

## Iteration log

- builds 1-16 (revisions 1-3), R4 builds 1-4 and R5 builds 1-5: shapes, pool, side prisms, dressing;
  water effects moved to VFX sockets; sheet palette; round pool; face prisms of mixed heights.
- R6 build 1: front-face prisms narrowed to 3-3.9 wide with real gaps between them (0.25-0.5),
  alternating proud low ledges (2.2-3.0 out, bush/fern on top) and recessed tall crowns (up to 2.5
  above the grass); stronger top bevels and more mid-height facets; side face rebuilt as one row of
  alternately proud and recessed prisms with gaps; grassy/pine/rock shoulders on the caps; corners
  pulled back further (4.6 / 3.6) with extra corner step columns; cap pines 1.2x; more bushes and
  daisies; w03_rock back to the sheet's #B2AFBA; parts re-sized so the parts grid puts walls at the
  back and the cliff top and slab in front. The silhouette is now irregular and the parts are all visible.
  Height reached 30.2 because of the pine on the shoulder.
- R6 build 2: shoulder and cap pines lowered (to 28.6 overall); column yaw +-0.26 so the faces turn
  to and from the sun, giving more tonal variety; corner bushes moved onto ground.
- R6 build 3: the rock wall behind the face columns is set back 1.6 under the cap's soil lip, with a
  soffit, so the gaps are deeper; the recessed columns are broader (3.6-4.6), so they read chunkier.
  All goals are MET except R2, which needs a sheet-wide palette decision.
- R7 build 1 (rework): PALETTE set to the sheet's 7 keys (w03_riverbed added, w03_water roughness
  0.15, w03_water_shallow and its shore band removed); pool bed, channel bed, under-water channel
  banks, the shore slope below z=1.0 and the tile-edge walls under the water skirts are w03_riverbed;
  a submerge() pass cuts rock faces at each water level and paints the parts under the water riverbed;
  the channel soil band now stops at the waterline; water transparency override removed. Sockets to
  the spec: curtain ends at (x, lip-1, 1.0), hero mist 1.4, 7-socket foam ring at 0.7, flow from
  y=+16; Wide lip widened to 16 with 4 curtains (4.5), mist 1.8 + 2 vapour, 10 foam ring sockets and
  a wider pool; TwoStep basin raised to z=11; top water plane is now water over riverbed with 2
  curtain sockets. 0 problems; the look is unchanged except the deeper teal under the water.
- R7 build 2: TwoStep mist raised (1.1 / 1.2) so the white splash at the basin reads between the falls.
- R7 build 3: hero sand collar narrowed (1.5 -> 1.1) to the spec's narrow rim above the waterline.
  All musts MET except R2 (sheet palette constraint).
- R8 build 1 (verifier fail 6.5): column() rewritten as a fat hexagonal prism (6-sided jittered rings,
  1-2 mid-height facet breaks, chamfered crown inset ~0.8-1); front columns 5-6.8 wide (2 a side plus
  1 proud and the corner steps), side columns 4.8-6, shoulders 4.6-5.4; wall set back 2.4 under the
  cap; hero pool (0,-7.4,15,8.2) nearly edge to edge, variant pools wider; 8 rim foam + 8 ring foam;
  10 foot rocks and 4 side-bank bushes; parts walls hex with rubble. Columns read fat; rock still pale.
- R8 builds 2-4: columns mostly turned crease-front (two big planes, one in shade) so each column has
  a lit and a dark side as on the sheet; framing crowns lowered to 0.8-1.5 above the grass; per-rock
  Tint 0.96-1.04; riverbed faces cut from rock drop the rock factor (fixed a 1.26 tint-spread problem).
- R8 build 5: ROCK_SCALE 0.76 (linear) on every rock face: the rendered rock median went from ~#C2BCC2
  to ~#A5A0A6 (reference ~#9995A2-#A39EA6); by eye the cliff now reads mid grey-lilac.
- R8 build 6: wall parts without split faces (crisp hex, chamfer 0.85, stronger facet breaks) and two
  rubble chunks at each foot. All must goals MET; 0 problems.
- R9 build 1 (verifier fail 7.3, export palette problem): ROCK_SCALE removed (Tint clamp 0.90-1.08,
  rock Tint centred on 1.0); the wall behind the face columns is set back 3.4 (was 2.4) and the front
  columns are spaced 0.25-0.55 apart instead of overlapping, so each seam is a slot onto the shaded
  wall; wall parts get 3 / 2 facet breaks and 4 rubble stones. Export: 0 problems (w03_rock row
  #B2AFBA, levels 0.92-1.08). The rock now reads paler (sheet key), but the crevices read darker.
- R9 build 2: the side-face prisms are spaced 0.25-0.5 apart too, giving slots on the side face; 92%
  of columns turned crease-front (two big planes, one in shade).
- R9 build 3: slots widened (front 0.4-0.7, side 0.4-0.65); dark lines now show at every seam in the
  hero/front/side cells. Export again 0 problems. All musts MET except the rock tone (V9a/R2/V8d),
  which is blocked by the sheet palette.
