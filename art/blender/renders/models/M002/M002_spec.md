# 002 Flint — spec

Reference: `art/blender/assets/references/002.png` (FLINT, page 2). Builder: `art/blender/kit/mcp/m002.py` → `build()`.
Assets (collection `Kit/M002 Flint`): `Flint` (hero, all parts unioned), `FlintLimestoneShell`, `FlintInsertLarge`, `FlintInsertMedium`, `FlintInsertSmallM002` (the kit's R01 sheet already owns `FlintInsertSmall`), `FlintBaseRocks`.

## Study (2a)

- **Classification:** full asset (resource node), budget 4000 tris; each part 1000.
- **Silhouette:** a pale, chunky limestone boulder, slightly taller than the Stone (front W:H about 1.15), broad faceted dome; three sharp dark flint shards stand out of its front faces, and three small pale base rocks sit at the foot.
- **Parts:** Limestone Shell (main body) with recesses; Flint Insert Large (front-left side, low), Medium (top front), Small (right side), each a chunky ~24-facet crystal sunk ~45% into a recess and spread round the dome so flint shows from every view; Base Rocks (three at the front and one at the rear; one part).
- **Scale:** in line with the Stone node; shell 6.7 × 6.5 × 5.8 studs, whole asset 8.5 × 6.7 × 5.8. Footprint near-round so it reads as a chunky node (user, 2026-10-27).
- **Colours (true sRGB):** swatches limestone #DDC4AC, flint #65636A, base rock #B9AEAC; rendered shell in the sheet's front view #C8AD96, flint #5B5A63. All matte, flat shaded.
- **Surface:** no noise or baked detail; subtle warm/cool drift on the limestone; flint is one colour (its lit faces are lighting).
- **Effects:** none shown; lighting and VFX stages skipped.

## Delivery

- Palette: `m002_limestone` #B3A093, `m002_limestone_warm` #AD9988, `m002_flint` #56586A, `m002_base_rock` #958A89 (calibrated: rendered shell #C8AD96, same as the sheet).
- Shell part: the inserts are boolean-subtracted, leaving their shallow recesses (pocket walls in the shaded limestone tone).
- Hero: exact boolean union of shell, inserts and base rocks: one closed manifold shell.
- UVs: Smart UV `UVMap`; the GLB exporter writes palette-cell UVs.

## Result

- Verifier rounds: 1 FAIL 4/10 (thin sliver inserts all on the front, no recesses, boolean slivers, a name clash that overwrote R01's FlintInsertSmall, since restored) · **2 PASS 6.5/10**.
- Open minors (for review): shell faceting more regular than the sheet's lumpy boulder; inserts read as symmetric gems rather than wedge shards with a recess rim; pebbles evenly spaced.

## Touch-up for the restyled sheet (2026-11-04)

The flint inserts stuck out as pyramid spikes (2.1–2.7 tall, about 1.5 above the surface). Both sheets draw flatter wedge shards lying in shallow recesses. Builder change:
- `INSERTS` heights 2.7 / 2.4 / 2.1 → 1.7 / 1.5 / 1.3 (the shard still sinks 45 % of its height, so it stands about 0.9 / 0.8 / 0.7 out of a recess about 0.75 deep);
- `SHARD_SIDE = 0.7`: the shard is 0.7 as wide across as along its long axis (a wedge, not a round gem). Large insert 2.6 × 1.9 × 1.7 (was 2.6 × 2.7 × 2.7);
- `M.finish(..., uv=UV)` with angle-based islands (45°): the default Smart UV folded the shell part's new recesses (9 overlaps). This also cleared the hero's 30 earlier overlaps.
- Positions, the shell, the base rocks and the palette are unchanged. The insert notes now say "flat dark faceted wedge shard".

| | Before | After |
| --- | --- | --- |
| Flint (hero) | 744 (8.5 × 6.7 × 5.8) | 738 (7.7 × 6.7 × 5.8) |
| FlintLimestoneShell | 466 | 460 |
| Inserts L / M / S | 24 / 24 / 24 | 24 / 24 / 24 |
| FlintBaseRocks | 144 | 144 |

- `m002.build()` problems: none.
- `kit_verify.run(objs, cls="asset")`: none caused by the change. Earlier findings that remain: the hero's 3 parity-inward faces (was 4), a 0.19° hero corner, 9 flipped UV triangles on the hero (was 8), the shell part's 2 parity-inward faces and a 0.048° corner (was 0.086°), and the base rocks buried in each other (the part is four loose rocks overlapping). These come from the hull and the boolean recesses. The UV overlaps the change caused are fixed.
- Removed: no part, socket or material.

## Touch-up verification (2026-11-04)

**Result: PASS, 6.5/10.** The shards are flatter wedges in shallow recesses, not pyramid spikes, as asked. Nothing broke. They are also smaller, so the hero shows about a third less flint than the sheet (minor 1).

**Technical** (`kit_verify.run`, cls asset, on the work copy; the committed kit objects were appended read-only for comparison):
- Flint 738 tris (was 744), 7.68 × 6.68 × 5.80 (was 8.54 wide), 1 shell, winding 0, self-hits 0. Shell part 460, inserts 24 / 24 / 24 (Large 2.62 × 1.89 × 1.70, was 2.62 × 2.70 × 2.70), base rocks 144.
- UVs: the angle-based islands cleared the committed hero's 30 overlaps and every island-gap / border shortfall (hero, shell, inserts and base rocks now all have gap 0.016 and border 0.008).
- No sockets and no glow keys, before or after. No part or material removed.
- Problems left, all **pre-existing** (same in the committed objects), none visible:
  - hero 3 parity-inward faces (was 4), shell part 2 (was 2); winding errors 0, so these are ray-parity hits on the boolean slivers;
  - hero thinnest corner 0.19° (same face, at the base); shell part 0.048° (was 0.086°: the same class of boolean sliver, now at the front-right recess rim);
  - hero 9 flipped UV triangles (was 8). The exporter writes its own palette UVs;
  - FlintBaseRocks: its four loose rocks overlap each other (unchanged part).

**Against the sheet** (compare at f34 (−30, 15), front (0, 6), side (90, 6), rear (180, 6), top (0, 89.9), r34 (150, 15); new and committed hero side by side; close-ups at each insert, `<temp>/.../M002/`):
- **Shape.** In the close-ups the Large and Medium inserts now read as flat faceted wedges lying in the surface, standing about 0.7–0.9 proud. The committed build had tall pyramids standing off the dome. This is what the sheet's insert close-up draws.
- **Flint share** (dark bluish pixels as a share of the model) against the sheet. The touch-up lost a third of the flint in the views that govern:

  | View | Sheet | Committed | Touch-up |
  | --- | --- | --- | --- |
  | f34 | 0.221 | 0.224 | 0.152 |
  | front | 0.217 | 0.215 | 0.137 |
  | top | 0.226 | – | 0.099 |
  | side | 0.134 | – | 0.068 |
  | rear | 0.138 | – | 0.034 |

- **Colours** (rendered medians): flint #636270 against the sheet's #575762; limestone f34 #DBBDA3 against #C6AB96. Both are unchanged from the committed build (#646471 / #DDBEA4).
- **Placement** is unchanged: the inserts sit on the silhouette (left edge, crown, right side). The sheet sets three large wedges on the front face.

**Blockers:** none.

**Minors:**
1. **Less flint than the sheet.** `SHARD_SIDE` 0.7 narrowed the shards' footprint as well as flattening them. Fix: keep the new heights, raise `SHARD_SIDE` to about 0.9 and the insert radii by about 1.2× (1.35 / 1.15 / 1.0 → 1.6 / 1.4 / 1.2). Re-measure: aim for a flint share of at least 0.19 in f34 and front.
2. Pre-existing: the inserts sit on the silhouette rather than on the front face, and the top / rear cells show fewer shards than the sheet.
3. Pre-existing technical items above (parity slivers, thin corners, flipped UVs, overlapping base rocks).
