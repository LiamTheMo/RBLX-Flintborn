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
