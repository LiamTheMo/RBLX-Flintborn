# 001 Stone — spec

Reference: `art/blender/assets/references/001.png` (STONE, page 1). Builder: `art/blender/kit/mcp/m001.py` → `build()`.
Assets (collection `Kit/M001 Stone`): `Stone` (hero, the three parts unioned), `StoneMainRock`, `StoneSupportRockLeft`, `StoneSupportRockRight`.

## Study (2a)

- **Classification:** full asset (resource node), budget 4000 tris; each part 1000.
- **Silhouette:** a chunky faceted dome, wider than tall (front view W:H ≈ 1.3), near-vertical lower sides bulging slightly above a flat base, broad shoulder, blunt crown. Footprint near-round (depth ≈ 0.9 of width): the sheet's side view suggests ~0.75, but at that depth the node read thin from above, so the user asked for a chunkier node (2026-10-27).
- **Parts:** Main Rock; Support Rock (Left), larger, set into the main rock's left foot; Support Rock (Right), smaller, at its right foot. They join on flat facets ("joining surface") at the main rock's base.
- **Scale:** matches the kit's in-game Stone node: main rock 6.7 × 6.1 × 5.0 studs (character 5.5); whole asset 8.7 × 6.1 × 5.0.
- **Facet style:** broad flat faces, hard edges with a slight chamfer, consistent thickness; flat shading.
- **Colours (true sRGB, sampled):** swatches #B4A49C (light), #847773 (mid), #484749 (dark). Rendered rock in the sheet: median #958682, lit #C0ACA2, shade #6B605C. Matte, no metal, no emission.
- **Surface:** solid colours only ("no noise, textures or photo detail"); subtle warm/cool facet drift.
- **Effects:** none shown. Lighting and VFX stages skipped (nothing to deliver).
- **Views on the sheet:** front ¾, rear ¾, front, side, rear, top, exploded, parts, underside, edge close-up.

## Delivery

- Palette keys `m001_stone` #93898B and `m001_stone_cool` #838188 (+ two in-between blends), calibrated so the kit studio render matches the sheet (front view median #948684 vs #968784).
- Hero = exact boolean union of the three closed parts: one manifold shell, no interior faces.
- UVs: Smart UV Project `UVMap` (margin 0.002). The repo GLB exporter writes palette-cell UVs on export.
- Export: `BLENDER_ARGS="art/blender/assets/kit/FlintbornWorldKit.blend --sheet M001" art/blender/run.sh scripts/export_kit_roblox.py` → `art/roblox/kit/M001/` (4 GLBs, palette.png, manifest with sizes in studs).
