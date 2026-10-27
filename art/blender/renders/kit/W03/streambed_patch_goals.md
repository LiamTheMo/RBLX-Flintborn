# W03 row 4: Streambed Patch goals

Reference: `art/reference/kit/rows/W03_row4.png` and the full sheet `art/reference/kit/W03_shorelines_waterfalls_river.png`.
Render to check: `art/blender/renders/kit/W03/streambed_patch_compare.png`.

Status after revision 8, build 3: "8 assets, 15632 tris, 0 problems"; hero 32.0 x 32.0 x 4.5 (4023/8000); export 0 problems, 127 sockets, StreambedBankRocks exported as Hull. Every "must" goal is MET; B5, B6 and B7 (should) stay UNMET (see Open issues).

## VERIFIER GOALS (revision 8: BankRocks hull, bigger boulders)
- C1 [must] MET. PARTS: four named parts exist with the contract collision: BankRocks hull, BedSlab precise, SubmergedRocks hull, WaterPlane none; Flow Strips are water_flow sockets, not a mesh.
  Evidence: the export manifest lists StreambedBankRocks Hull, StreambedBedSlab PreciseConvexDecomposition, StreambedSubmergedRocks Hull, StreambedWaterPlane Box/CanCollide false. BankRocks is now ONE contiguous cluster (anchor + partner + chunk, 8.1 x 7.2 x 4.4, 200 tris), so its single convex hull hugs the rocks and cannot wall off the stream. In the parts cell it reads like the reference Bank Rocks: one big boulder with a smaller one against it.
- C2 [should] MET. HERO: the 2-3 biggest boulders per bank are ~15-20% bigger than in revision 7 and the height stays ~4.5.
  Evidence: anchors grow 1.18x wide (now ~6 wide), partners 1.08x; KITSTAT still 4.5 tall. In the hero cell the front-left, front-right and back clusters read as big chunky boulders, closer to the reference's biggest rocks.
- C3 [should] UNMET. Sand tan and water hue as on the reference (see B7): sheet-owner palette change.


## VERIFIER GOALS (revision 7: boulder mass and height)
- B1 [must] MET. HERO: 32 x 32 tile ~4.5 tall incl. boulders (KITSTAT height 4.3-4.7), banks at 1.6.
  Evidence: KITSTAT 32.0 x 32.0 x 4.5 (was 3.8); in the front cell the boulders now stand about three times the bank height over the tile base, like the reference front cell.
- B2 [must] MET. HERO: at least 6 big chunky flat-topped anchor boulders straddle BOTH waterlines (3+ per bank), each ~4.5-5.5 wide and rising ~2.5-3 above the sand (tops z ~4.4), so they dominate the skyline as separate tall boulders, not a low ridge.
  Evidence: the hero cell shows 3 big flat-capped boulders on each waterline (anchors ~5 wide, ~3.4 above the water) with ~3.5-wide partners, plus two lone boulders on the dry sand (back-left corner, right bank) as in the reference. They are still a little smaller relative to the tile than the reference's biggest boulders.
- B3 [must] MET. FRONT/SIDE: the skyline is a row of distinct boulder silhouettes roughly 2-3x the bank height above the tile base; anchors at least half as tall as wide.
  Evidence: the front cell shows 2 boulder groups flanking the cyan channel, each with 2-3 separate silhouettes; the side cell shows ~8 separate boulder tops with water visible between the two bank groups (reference: ~6 boulders with gaps).
- B4 [must] MET. VARIATIONS: each variant's anchor boulders are as big as the hero's.
  Evidence: KITSTAT Straight/Bend/Fork all 4.5 tall; the Bend cell shows a line of 5 big boulders along the outer bank, the Fork cell big boulders at the corners and one on the islet.
- B5 [should] UNMET. PARTS: the exploded cell reads like the reference: sand slab with stones, big boulders beside it, small submerged rocks and a flat water sheet in front.
  Evidence (rev 8): all parts read correctly (slab, one boulder cluster, 5 small slabs, water sheet), but the automatic grid (largest footprint first) now puts the water sheet beside the slab at the back right instead of in front, because BankRocks shrank to one cluster. The layout is the runner's, not the module's.
- B6 [should] UNMET. Bed stones visible as faceted shapes through the hero water.
  Evidence (rev 8): enlarged again (main 2.9-3.4 wide, tops 0.05-0.17 under the surface); in the top cell a few faceted shapes now show under the cyan, but they remain faint because they are the same w03_riverbed as the bed (only shading separates them).
- B7 [should] UNMET. Hues: sand warm tan, stream saturated cyan-blue as on the reference.
  Evidence: the sand still reads a little more orange and the water a little lighter/greener than the reference. The hex values are the shared W03 sheet palette (identical in all four modules), so this module cannot change them alone (see Open issues).

## REWORK GOALS (revision 6: sheet palette, riverbed under the water, one water key)
- RV1 [must] MET. PALETTE is exactly the 7 sheet keys (w03_grass, w03_soil, w03_sand, w03_rock #B2AFBA, w03_riverbed #0B6E8F, w03_water #18CFFA roughness 0.15, w03_bush); no w03_water_shallow or other shade key.
  Evidence: module PALETTE dict; runner 0 problems; the renders show only tan, teal, cyan, grey, green and the daisy colours.
- RV2 [must] MET. Everything under the water surface is w03_riverbed: bed, underwater slope, bed stones, wet rock bases, channel walls under the skirt. Sand only above the waterline.
  Evidence: the BedSlab part shows tan banks with a deep teal dished channel; the BankRocks anchors and the submerged slabs show teal bands below z 1.0 with grey above; the front cell shows the cyan skirt over a teal wall across the channel and tan walls on the banks.
- RV3 [must] MET. The water is ONE flat w03_water slab at z=1.0: no shallow band, no shoal patches, no foam/ripple/strip geometry.
  Evidence: the WaterPlane part is one even pale-cyan sheet (142 tris); the hero water has no lighter shore band.
- RV4 [must] MET. HERO/TOP: the stream reads deep saturated cyan against the tan banks.
  Evidence: the hero and top cells show a vivid cyan channel (sampled #34C2E5 in the top cell, reference about #3BC4F2), not pale.
- RV5 [must] MET. 0 problems (no shade pairs, no painted lighting, Tint within +/-10%).
  Evidence: STATS line "0 problems".
- RV6 [should] MET. Rock reads as one pale grey next to the sand, light tops from lighting only.
  Evidence: the boulders read light grey with only a faint cool cast (the reference's rocks are a cool grey too); one key, small random Tint.

## VERIFIER GOALS (revision 5, kept)
- VR2 [should] MET. Boulders are 2-4.6 stud chunky flat-topped rocks in clusters.
  Evidence: the hero cell shows 6 clusters of an anchor plus 2-3 smaller flat-capped chunks.
- VR4 [should] MET. Pebbles, grass tufts and daisies grouped beside the clusters.
  Evidence: green tufts and white daisies at the cluster feet in the hero and top cells, pebbles along both banks.
- VW2 [must] MET. HERO: chunky flat-topped boulders cluster on BOTH waterlines with visible mass.
  Evidence (rev 7): 3 clusters per bank whose anchors are now ~5 wide with tops at z ~4.4, rising out of the water's edge with wet teal bases; see B2.
- VW3 [must] MET. Bed stones read as low shapes on the riverbed through the water.
  Evidence: the BedSlab part shows a dozen faceted teal stones on the bed; in the hero cell they show as subtle darker facets under the cyan (subtle by design now that they are riverbed, as the spec asks).
- VC1 [must] MET. The hero channel is 12 wide at the seams (~38% of the tile) and widens to about half the tile mid-tile.
  Evidence: the top cell shows the water at about 40% of the width at the front and back edges and about half mid-tile (reference: about 40-50%).
- VP2 [should] MET. The WaterPlane part is not cut off in the parts cell.
  Evidence: in the parts cell the whole water sheet sits at the top right inside the frame (now only 20 wide with the skirts).

## ASSEMBLED / HERO (StreambedPatch)
- H1 [must] MET. 32 x 32, ~4.5 tall incl. boulders, banks at 1.6, flat walls to z 0.
  Evidence (rev 7): KITSTAT 32.0 x 32.0 x 4.5; the front cell shows a thin flat slab with tall boulders on it.
- H2 [must] MET. A gently meandering channel runs front to back, 12 wide at both seams and wider mid-tile.
  Evidence: the top cell shows an S channel centred at both seam edges.
- H3 [must] MET. Both banks are broad warm sand, slightly lumpy, sloping to the waterline.
  Evidence: hero and top cells: tan banks covering about half the tile.
- H4 [must] MET. Big boulder clusters on both waterlines, partly in the water with teal wet bases.
  Evidence (rev 7): see B2; the BankRocks part shows both banks' boulders with teal bands at the base.
- H5 [must] MET. 4-6 low flat rocks in the channel just break the surface.
  Evidence: the top cell shows 5 grey slab tops mid-channel with foam previews; the part shows teal sides and grey tops.
- H7 [should] MET. Pebbles, tufts and daisies dress the banks. Evidence: see VR4.
- H8 [should] MET. All rock one grey, light tops from lighting. Evidence: see RV6.

## FRONT / SIDE / TOP
- F1 [must] MET. Front view: wide thin slab, cyan channel in the middle, boulders both sides.
  Evidence: the front cell.
- S1 [should] MET. Side view: long low slab with a boulder skyline, under 5 tall.
  Evidence (rev 7): the side cell shows separate boulder tops at 4.5, about 3x the bank height.
- T1 [must] MET. Top view: full-height meandering channel, 4+ rocks per waterline, rocks in the channel.
  Evidence: the top cell shows 10-11 rocks along each waterline and 5 slabs.

## PARTS
- P1 [must] MET. Exactly four parts: BankRocks (hull), BedSlab (precise), SubmergedRocks (hull), WaterPlane (none); Flow Strips are water_flow sockets (in the notes).
  Evidence (rev 8): KITSTAT BankRocks 200/4000 (hull), BedSlab 2086/3000 (precise), Submerged 246/2000 (hull), WaterPlane 142/1500 (none); manifest collision fidelities match (see C1).
- P2 [must] MET. BankRocks is a set of chunky boulders with teal wet bases.
  Evidence (rev 8): the parts cell shows one big grey flat-capped boulder with a smaller one against it and teal bands at their bases, like the reference's Bank Rocks; collision hull.
- P3 [must] MET. BedSlab is tan banks with a deep riverbed-coloured dished channel and bed stones.
  Evidence: the parts cell (top left).
- P4 [must] MET. SubmergedRocks is 5 low flat rocks <=1.5 tall, teal below z 1.0, grey tops.
  Evidence: the parts cell; part 1.4 tall.
- P5 [must] MET. WaterPlane is only the flat water slab (one key) and carries the flow and foam sockets.
  Evidence (rev 7): the parts cell shows one flat cyan sheet with foam previews, now in front of the slab as in the reference. It is a little paler than the reference's plane because the see-through water sits over the light backdrop.

## VARIATIONS
- V1 [must] MET. Straight: straight centred channel, boulders both banks, rocks in the stream.
  Evidence: the Straight cell.
- V2 [must] MET. Bend: smooth quarter circle front -> right, boulders on the outer bank, flow beams follow the curve.
  Evidence: the Bend cell; beams use the bend path.
- V3 [must] MET. Fork: channels from left and right join and leave through the front round a sand islet with a boulder.
  Evidence: the Fork cell shows the T with the islet boulder in the split.
- V4 [must] MET. Every variant 32 x 32, same cross-section (riverbed under water), 12-wide seams.
  Evidence: KITSTAT 32 x 32 for all 3; teal beds and teal channel walls in each cell.

## Iteration log
Revisions 1-5 built the channel field, rocks, variants, parts, VFX water and vivid water over a sand bed.

Revision 6 (user rework: sheet palette, riverbed under water, one water key):
1. Build 1: PALETTE set to the 7 sheet keys (w03_rock #B2AFBA, w03_water roughness 0.15, new w03_riverbed); ground faces below the waterline contour and channel walls are w03_riverbed; rock hulls crossing z=1.0 are bisected there (teal below, grey above); the shallow band, shoal patches and the WATER_T override were removed. Result: 0 problems; the channel reads deep saturated cyan, wet rock bases teal; bed stones hard to see.
2. Build 2: bed stones enlarged (main 2.3-2.8, partners 1.2-1.5). Result: slightly more visible in the BedSlab part.
3. Build 3: big bed stones built as flat slab hulls with steep side facets. Result: they read as faceted stones on the riverbed in the BedSlab part and as subtle shapes in the hero. All must goals MET.

Revision 7 (verifier: boulders too small and low, hero 3.8 tall):
1. Build 1: bank boulders scaled 1.15x wide and 1.12x tall (anchors ~5 wide), height cap 3.9 and tops to z 4.35, anchor rings gain a shoulder ring under the flat cap; bed stones enlarged and raised to 0.07-0.2 under the surface. Result: hero 4.4 tall, boulders read tall and chunky in the front/side cells; the clusters' smallest chunks looked cluttered.
2. Build 2: dropped the three 1.5-wide filler chunks in the hero clusters; BankRocks now holds both banks' boulders (collision precise), so the parts grid puts it beside the slab with the water sheet in front. Result: the parts cell matches the reference layout; hero clusters read as distinct boulders.
3. Build 3: tops capped at z 4.42 (hero 4.5) and two lone boulders added on the dry sand (back-left corner, right bank). Result: all must goals MET; 0 problems, 16512 tris.

Revision 8 (verifier: BankRocks must be hull; boulders a bit small):
1. Build 1: StreambedBankRocks rebuilt from the hero's left-bank middle cluster only (select b3-b5) and tagged hull; anchors (spec h >= 3) grow 1.18x wide. Result: 0 problems, BankRocks 8.1 x 7.2 x 4.4 single cluster; hero boulders visibly chunkier; parts grid moved the water sheet to the back right.
2. Build 2: partners grow 1.08x. Result: clusters read as two big boulders plus a chunk, like the reference.
3. Build 3: big bed stones 2.9-3.4 wide, tops 0.05-0.17 under the surface. Result: faint faceted shapes in the top cell; export checked: BankRocks Hull, 127 sockets, 0 problems.

## Open issues
- Water transparency: no W03 module overrides FB_w03_water any more (checked with grep), so all four use the default. If one module overrides it again, the last one built changes this tile's water look: a more opaque value hides the riverbed and the bed stones and makes the stream read paler.
- Sand/water hue (B7): the verifier suggested w03_sand ~#D4A55E and w03_water ~#1FB8F2. The W03 palette must be identical in all four modules, so the change belongs to the sheet owner.
- BankRocks is one cluster (hull) rather than the full set of six clusters; the hero places six. A full both-bank set would need per-island hulls in export_kit_roblox.py.
- Parts cell layout (B5) is chosen by build_kit.grid_parts (largest footprint first), so the water sheet sits beside the slab, not in front.
