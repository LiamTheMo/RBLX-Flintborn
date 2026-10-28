# W04 row 1: Classic Pine goals

Reference: `art/reference/kit/rows/W04_row1.png` (full sheet `art/reference/kit/W04_pines_firs_saplings.png`).
Compare: `art/blender/renders/kit/W04/classic_pine_compare.png`.
Build: `BLENDER_ARGS="W04 --only classic_pine" art/blender/run.sh scripts/build_kit.py art/blender/assets/kit/wip/W04_classic_pine.blend`

REVISION 6 (verifier REWORK). New musts are tagged R6-*. Statuses are judged by eye, comparing each cell of
my row with the reference cell above it. Light and dark on the sheet come from lighting, and every material has ONE key.

## REVISION 7 (verifier FAIL 5.5/10): new musts
| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| R7-1 | must | 3 stacked tiers + tip, each a star of 7-8 LONG pointed flaps drooping well below the tier edge (tips 2-3 studs under the rim) and lapping over the tier below; tiers clearly separated, not a lumpy cone | MET (partly) | hero/front/side now show tip + 3 clearly separated tiers of 8 pointed flaps whose tips hang ~2.5 studs under the rim with a shadowed gap under each; flaps still slope more steeply (tent-like) and stick out less horizontally than the ref |
| R7-2 | must | Needles read mid green with lime lit tops and dark teal undersides/hems, from ONE darker mid-tone key + steep droop/overhang geometry | UNMET | one key #5E8E1A, Tint 0.8. Undersides and hem gaps now read darker, but lit tops are mid green, not the ref's yellow-lime, and the darks are not near-black teal |
| R7-3 | must | Trunk fat at base (~2.5 r) tapering to ~1.5 at crown, fluted, 5-6 buttress roots running out on the ground, warm brown | MET | front/hero cells: wide buttressed base (~5 studs across) on 6 root ridges running out on the soil, fluted brown column tapering under the canopy |
| R7-4 | must | No cauliflower leaf_cluster inner layer: large clean angular facets | MET | leaf_cluster inner layers removed: each tier is one skirt of 8 big two-facet flaps |
| R7-5 | must | Tier1 clearly widest, ~14-15 studs; tier radius ratio ~0.6 / 0.8 / 1.0 (Tier3/Tier2/Tier1) | MET | Tier1 15 wide, Tier2 12.3, Tier3 9.3, tip 5.1; in the parts cell Tier1 is clearly the biggest piece |
| R7-6 | should | Top view: clear 8-point star with grey rocks peeking out at the rim | UNMET | top cell: rocks now peek past the rim on left and right, but the crown reads as a dark layered rosette, not the ref's bright crisp 8-point star |
| R7-7 | should | Exploded tiers: flat-ish discs with strongly drooping flaps, Tier1 obviously widest | UNMET | exploded tiers are clearly graded in size with drooping pointed flaps, but they read as steep tents rather than the ref's flatter discs |
| R7-8 | should | Rocks ~25% smaller, 3 at r~7-8 outside the skirt, 5-6 lime tufts ringed between | MET | 3 smaller rocks at r~7.8 just outside the skirt (front-left, front-right, back), 6 lime tufts ringed between |
| R7-9 | should | ShortWide soil patch radius ~6 or less, cream w04_ground like the hero | MET | ShortWide patch shrunk to r 5.6, same w04_ground key; reads cream, about trunk-plus-roots wide |

## ASSEMBLED / HERO
| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| H1 | must | Hero ~24 H, lowest skirt ~17 W, origin at bottom centre | MET | H 24, lowest tier 15 W (rev 7, per verifier R7-5); bottom skirt clearly widest |
| R6-1 | must | (SUPERSEDED by R7-4: verifier asked to remove the leaf_cluster layer) | n/a | each two-layer tier's inner layer is now one 8-lobe leaf_cluster dome bulging between the pointed flaps. The hero and front cells read fuller and lumpier than rev 5 |
| H2 | must | Clearly stepped into 4 tiers (Top Tip + 3), visible hem overhang, single sharp apex | MET | the front, side and hero cells step out at each tier with an overhanging hem and one sharp apex |
| V5-H1 | must | Broad, chunky, overlapping flaps, not a fine pleat | MET | big spade flaps with lumpy cluster lobes between them, about 4 per tier across the front |
| V5-H2 | must | Flaps drooping, with a ridge fold and strongly two-tone lit/shaded halves | UNMET | the shape matches: folded drooping spades whose halves shade differently. The contrast is still softer than the ref's lime/teal-black (see limits) |
| V5-H3 | must | Dark band under every hem, from geometry | UNMET | keels make a darker strip under each tier, but it is mid green, not the ref's near-black teal |
| H6 | must | Stout reddish fluted trunk visible for the lowest ~quarter, 5 buttress roots on the soil | MET | front cell: brown fluted trunk under the canopy with flared roots |
| H7 | should | 3-4 grey rocks mostly front/left, 5-7 lime tufts, cream soil patch | MET | 4 grey rocks, 6 tufts (4 now chunky leaf_cluster clumps), cream patch |
| R6-2 | must | ONE palette key per material, no shade variants, no colour chosen by height, facing or tier; Tint within +/-10% random (plus one uniform per-tree needle Tint) | MET | keys: w04_needle, w04_bark, w04_wood_end, w04_ground, w04_grass, kit_rock. Runner: 0 problems, shade_pairs [] |
| V5-C | must | Needles a saturated mid green (~#5E8E1A at mid-tone), not pale or grey | MET | uniform needle Tint 0.82 (sheet note: darken if washed out). The canopy now reads a deeper, saturated green, closer to the ref than rev 5's lime |

## FRONT
| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| F1 | must | Symmetric stepped triangle, apex centred, bare trunk below the lowest hem | MET | front cell: symmetric 4-step cone, centred apex, trunk and roots below |
| F2 | should | Root flare >= 2x the trunk width; rocks left and right | MET | flare is about 2x; rocks on both sides |

## SIDE / REAR
| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| S1 | must | Same tiered silhouette as the front | MET | the side cell matches the front's 4-step outline |

## TOP
| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| V5-T | must | Star-shaped top view: pointed 8-point outline of layered tiers | MET | with the wider lowest skirt the top cell now shows a clear pointed star outline around layered rings (rev 5 was a round rosette) |
| T3 | should | 1-2 grey rocks peek past the canopy | UNMET | the rocks are hidden under the wider skirt / in its shadow |

## PARTS
| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| P1 | must | Six parts with exact names | MET | TopTip, CanopyTier3, CanopyTier2, CanopyTier1, Trunk, RootFoot |
| P2 | must | Tier sizes grow TopTip < Tier3 < Tier2 < Tier1 (~6 / ~9 / ~13 / ~17 W) | MET | the parts cell shows four star domes of rising size |
| P3 | should | Tier parts are low, wide star domes of drooping flaps that re-stack exactly into the hero | MET | same skirt and cluster calls as the hero; low lumpy star domes |
| P4 | must | Trunk part: tapered fluted column with a w04_wood_end cut top | MET | tall brown column with an orange top in the parts cell |
| P5 | must | RootFoot: flared roots cut at z=2, rocks, tufts, soil | MET | stump with a pale cut top, rocks, tufts and soil |

## VARIATIONS
| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| V1 | must | TallNarrow: a slim, taller spire of many tiers | MET | narrow tall stepped spire with a bare trunk |
| V2 | must | ShortWide: squat, broad drooping tiers, short thick trunk | MET | broad low cone with a short trunk |
| V3 | must | Asymmetric: lopsided crown, uneven tiers, side branch stub | MET | crown heavy to the left, tip drifts right, stub with a pale end on the trunk |
| V4 | should | All variants keep rocks, tufts and soil | MET | visible in all three cells |

## TECH
| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| C3 | must | Under budget, nothing below z=0, hull collision, tufts kit_nocollide | MET | rev 7: hero 2286/5000, tall 2318, wide 2022, asym 2127, tiers 144-160/1500, trunk 220/800, root 1472/1500; 0 problems |
| C4 | must | No VFX or water meshes (the reference shows none) | MET | 0 sockets, no water |

## Overall
| # | Pri | Goal | Status | Evidence |
|---|-----|------|--------|----------|
| V5-O | must | Overall resemblance: chunky layered conifer, hem overhang, strong colour contrast | UNMET | silhouette, tiers, layering and star top all match cell for cell. The ref's lime/teal-black contrast is still softer here |

## Limits (why V5-H2 contrast, V5-H3 and V5-O stay UNMET)
Studio lighting (build_kit/flintkit, which this module does not own) has a bright sky ambient and fill. With one
flat needle key, shaded faces cannot reach the reference's near-black teal, and lit faces cannot reach its
yellow-lime, without painting light into the colours, which the rules forbid. The geometry already does what it
can: ridge folds, 45-degree keels and tucked hems.

## Iteration log
Revisions 1-5: 37 builds (see git history). Pine skirts, fluted trunk, roots, dressing, one key per material.

Revision 6 (4 builds):
1. Each tier's inner hem became a shared `leaf_cluster` (8 lobes), and the leafy tufts became leaf_cluster
   clumps. Denser and chunkier, but the domes were too tall and blurred the tier steps.
2. Cluster height cut to gap + 0.15 and radius to 0.92 R; needle Tint 0.88. The steps came back and the green deepened.
3. Hero H 24 (spec), Tint 0.82. The green is darker and closer to the ref.
4. Lowest skirt widened (W 17, upper widths scaled down). The bottom tier overhangs and the top view is now a star.

Revision 7 (4 builds, verifier FAIL 5.5):
1. Skirt shape: shoulder 0.24R (longer flaps), deeper keel, droop_k 0.5, Tint 0.78; no leaf_cluster layer; W 15, tiers 0.6/0.8/1.0;
   trunk r 1.75 with foot 1.45x (2.5 base), 6 roots reach 5.2; rocks smaller at r~7.8; tufts ringed; ShortWide patch 5.6.
   Trunk flare much better; but 7 thin hems read as a shingled cone.
2. One skirt per tier (tip + 3; variants 6/3/4 skirts), droop_k 0.65: tiers clearly separate, but flaps were steep tents.
3. Flatter inner flap (BEND_Z 0.85), FOLD 0.5, droop_k 0.42: little visible change.
4. FOLD 0.38, shallower notches, droop_k 0.34, Tint 0.8, widths 0.34/0.62/0.82/1.0: final. Tiers separate with drooping
   tips; contrast and top-view star remain weaker than the ref (build cap of 4 reached).
