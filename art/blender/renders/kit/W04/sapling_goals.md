# W04 row 3 SAPLING: verification goals

Reference: `art/reference/kit/rows/W04_row3.png` (and the full sheet `W04_pines_firs_saplings.png`).
Compare render: `art/blender/renders/kit/W04/sapling_compare.png`.
Reference measurements (3x crop of the front cell, ~53 px per stud for a 6-stud tree): apex 6.0,
crown hem ~4.2, crown ~2.6-3 W, skirt ~4.6-5 W with its hem at ~2.2-2.4, skirt upper (second) hem
row at ~3.4, trunk ~1.0-1.3 wide under the skirt and ~1.9-2.2 wide at the root flare, soil patch ~5 W.
The foliage is built of BROAD panels: each tier is a solid cone of 6-8 wide, blunt, drooping panels
that touch side by side (no gaps), each panel a big two-plane facet with a crease, and a thick
downward-facing hem band. The light/dark split (dark-teal shaded panels, lime lit panels, orange lit
bark, pale rock tops) is LIGHTING: one palette key per material, shaded by the light.

Status key: MET / UNMET, evidence from the latest compare render (revision 2, build 5).

## ASSEMBLED / HERO
| # | pri | goal | status | evidence |
|---|-----|------|--------|----------|
| H1 | must | Exactly 2 foliage tiers (pointed top cone + lower skirt); the crown is a squat compact cone NESTED into the skirt: its hem overlaps the skirt's top, no gap / trunk / background visible between tiers (verifier) | MET | hero/front cells: one squat 6-panel crown whose thick hem overhangs the skirt's upper row, then the broad skirt; no trunk or background shows between the tiers |
| H2 | must | Hero ~6 H; foliage 4.6-5.4 studs wide; reads about as tall as a character | MET | front cell reads a character-height pine; KITSTAT 5.7 x 4.9 x 6.0 (foliage 5.0 W incl. the 8 skirt tips) |
| H3 | must | Lower skirt hem tips at ~0.37-0.42 H (2.2-2.5 studs); crown hem at ~0.65-0.70 H; apex the single highest point | MET | front cell: skirt tips at ~0.4 H (2.45), crown hem at ~0.67 H (4.05), single apex on top |
| H4 | must | Crown ~3 W x ~2 H (0.55-0.65 of skirt width), 6 broad blunt tips (verifier fix) | MET | front cell: crown clearly narrower than the skirt with 6 broad blunt panels; TopFoliage part 3.2 W x 2.2 H |
| H5 | must | Lower skirt: 8 broad drooping tips plus a second, higher hem row set in the notches (double hem) | MET | front/hero cells: 8 broad drooping skirt panels plus a second, shorter row set in the notches above them |
| H6 | must | Chunky toy-like facets: panels are broad, solid and touch side by side (no thin kite blades, no sliver gaps, no stray spikes); front view shows ~10-16 big foliage planes (verifier) | MET | front cell shows ~14 big two-plane panels touching edge to edge, no kite blades, slivers or spikes; hero 934 tris |
| H7 | must | Oversized stubby trunk: ~1.3-1.5 wide at mid height, ~2.0-2.3 at the root flare, visible ~1.8 studs below the skirt (about a third of the height), 4 visible roots (verifier) | MET | front cell: thick reddish trunk (~1.3 wide) visible from the rocks up to the skirt, flaring into 4 big roots ~2.2 wide at the foot |
| H8 | must | Ring of 4-6 grey rocks (0.4-0.8 studs high) hugging the trunk foot, at least 2 visible either side of the trunk in front view | MET | front cell: grey rocks on both sides of the trunk foot (6 in the ring, now 1.15x instead of 1.4x so they no longer dominate) |
| H9 | should | 3-4 grass tufts of bright spiky blades at left, front and right of the base | MET | 4 bright spiky w04_grass tufts at left, front, right and back-right |
| H10 | should | Thin cream w04_ground soil patch, irregular outline, ~5 dia, <= 0.08 thick | MET | cream irregular w04_ground patch ~5 dia under every tree, 0.04 thick |
| H11 | should | Row lighting matches the reference (lit from the right) (verifier) | UNMET | the studio sun is fixed by the runner (KEY_DIR front-left) and a module cannot change it; see open issues |

## PALETTE (one colour per material; the sheet's light/dark is lighting)
| # | pri | goal | status | evidence |
|---|-----|------|--------|----------|
| P0 | must | Exactly ONE key per material: needles w04_needle, bark w04_bark, cut wood w04_wood_end, soil w04_ground, grass w04_grass, rocks kit_rock; no shade variants or shade-picking code; Tint within +/-7% per material; runner 0 problems | MET | module uses only w04_needle, w04_bark, w04_wood_end, w04_ground, w04_grass, kit_rock; Tint jitter +/-5%; STATS 8 assets, 0 problems |
| P1 | must | Foliage is the brightest, most yellow-green on the sheet: w04_needle (#6A963E) at Tint ~1.15; lit faces read lime | MET | compare row: lit panels read lime/yellow-green, the brightest greens on the W04 sheet (w04_needle at Tint 1.15) |
| P2 | must | The dark band under each hem comes from geometry (thick downward-facing hem band + under-cone), not paint | MET | hero/front cells: a darker band under each hem comes from the thick downward-facing hem band and under-cone, all one key |
| P3 | should | Trunk/roots one reddish-brown w04_bark; trunk part cut top w04_wood_end with a recessed heart | MET | trunk and roots are one reddish-brown with lit and shaded facets; trunk part has a pale w04_wood_end cut top with a sunken heart |
| P4 | should | Rocks one grey kit_rock, not oversized; grass one bright w04_grass; soil one cream w04_ground | MET | rocks one grey, smaller than before; tufts one bright green; soil one cream (kit_rock stays slightly warm grey: see open issues) |

## FRONT / SIDE
| # | pri | goal | status | evidence |
|---|-----|------|--------|----------|
| F1 | must | Front view: two stacked solid cones, crown hem overlapping the skirt with no gap, short thick trunk visible below, rocks either side of the foot (verifier) | MET | front cell: two nested solid cones, the crown overlapping the skirt with no gap, stout trunk below, rocks either side |
| F2 | should | Side view matches the front (roughly radial), depth ~ width | MET | side cell has the same two-tier silhouette; 4.9 D vs 5.7 W |

## TOP
| # | pri | goal | status | evidence |
|---|-----|------|--------|----------|
| T1 | must | Top view is a compact star: a distinct pointed 6-point crown star (steep ridges, clear lit/shaded facets) over a radiating 8+8-point skirt star with notches; rocks/grass peeking at the rim (verifier) | MET | top cell: spiky 16-point skirt star with notches, and a 6-point crown star in the centre with steep lit/shaded ridges and a shaded outline |

## PARTS
| # | pri | goal | status | evidence |
|---|-----|------|--------|----------|
| A1 | must | Four parts with exact names SaplingTopFoliage, SaplingLowerFoliage, SaplingTrunk, SaplingRootsBase | MET | parts cell shows crown cone, skirt, trunk and roots/base; KITSTAT lists all four names |
| A2 | must | Part sizes: top ~3 W x 2 H pointed cone; lower ~5 W x ~2.5 H skirt; trunk ~1.3-1.6 dia x ~3 H, flared foot; roots/base ~5 W x ~1 H | MET | TopFoliage 3.2 x 2.2; LowerFoliage 5.1 x 2.8; Trunk 2.5 x 2.2 x 2.9 incl. roots (shaft ~1.3 dia); RootsBase 5.4 x 1.3 |
| A3 | should | Trunk part: tapered, w04_wood_end cut top with a recessed heart, root flare at the foot | MET | parts cell: tapered trunk with a pale orange cut top, sunken heart and 4 flaring roots |
| A4 | should | Roots/Base part: short flared stump with 4 roots + rock ring + grass + soil patch | MET | parts cell: cut stump with roots, rock ring, tufts and a soil patch |

## VARIATIONS
| # | pri | goal | status | evidence |
|---|-----|------|--------|----------|
| V1 | must | SaplingSeedling: ONE tier on a short thick stub, ~3 W x ~3.5 H (3.3-3.7), pebbles + tufts (verifier: was 2.8 H) | MET | seedling cell: one double-hem tier on a short thick stub, pebbles + tufts; 3.2 x 2.9 x 3.6 |
| V2 | must | SaplingBushy: 3 wide overlapping tiers, ~6 W x ~6 H (5.7-6.3 each), low and round, broadest skirt of the row (verifier: was 5.0 H) | MET | bushy cell: 3 wide overlapping tiers, broadest skirt in the row, round-topped; 6.3 x 6.2 x 6.0 |
| V3 | must | SaplingSlender: 3 narrow tiers on a thinner, taller trunk, ~4 W x ~7.5 H | MET | slender cell: 3 narrow tiers on a thin trunk, tallest in the row; 4.4 x 3.9 x 7.5 |

## TECH
| # | pri | goal | status | evidence |
|---|-----|------|--------|----------|
| X1 | must | Runner: 8 assets, exact names, 0 problems, every asset under budget, origin bottom centre, nothing below z=0 | MET | STATS W04/sapling: 8 assets, 4764 tris, 0 problems; hero 934/2000, every asset under budget |
| X2 | must | Collision: hero/foliage parts/trunk/bushy/slender hull; RootsBase and Seedling none | MET | hull for hero/foliage parts/trunk/bushy/slender, none for RootsBase and Seedling |
| X3 | must | No water/vapour meshes; no VFX sockets (not harvestable) | MET | no water, mist or smoke meshes; no sockets |

## Iteration log

Earlier runs: run 1 (19 builds) painted lighting with per-flap green cycles; revision 1 (7 builds)
moved to one key per material but built tiers from thin kite flaps over a cone, which the verifier
failed (resemblance 6/10): crown blades with a gap above the skirt, thin dark trunk, spindly slivers,
Seedling 2.8 H and Bushy 5.0 H short of spec.

Revision 2 (this run, max 6 builds):
1. Build 1: replaced the kite-flap tiers with `star_row`: one closed solid cone per row of 6-9 BROAD
   panels meeting edge to edge (two planes creased on a ridge, a drooping tip, a raised notch), a
   thick hem band and a downward under-cone; the double hem is a second, shorter row in the notches.
   The crown hem (4.05) is dropped below the skirt apex (4.9) so it nests with no gap. Trunk widened
   (0.82 -> 0.64 r, flare 0.45) with 4 bigger roots; skirt raised to 2.45 so ~1.8 studs of trunk
   show. Seedling resized to 3.6 H, Bushy to 6.0 H, rocks 1.4x -> 1.15x. Result: chunky solid tiers,
   no gaps, thick trunk; but the top view was a rounded blob.
2. Build 2: narrower panel corners (0.24 step, 0.8 R), deeper notches (0.6 R) and more droop ->
   top view becomes a spiky star; front tips read as drooping points.
3. Build 3: skirt's second row lower and wider (0.84 R at 0.3 h) so the tree reads as two tiers;
   4 roots added to the trunk part.
4. Build 4: Bushy reworked: only the bottom tier double-hemmed, rounder shoulders, R 3.15/2.55/1.75
   -> 6.3 x 6.2 x 6.0, wide and round instead of a tall many-row fir.
5. Build 5: crown R 1.7 with a thicker (0.26) hem and steeper upper slope -> the crown overhangs the
   skirt and its 6-point star stands out in the top view. All must goals MET; 4764 tris, 0 problems.

Known differences: the studio sun is front-left (fixed by the runner), so the lit/shaded sides are
mirrored versus this row, which is lit from the right (H11, should); kit_rock (#A89C9C) is a slightly
warm grey because the sheet keeps the shared KIT_PALETTE key (all four W04 modules use it).
