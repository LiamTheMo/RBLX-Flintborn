# 007 Coal — spec

Reference: `art/blender/assets/references/007.png` (COAL, page 3). Builder: `art/blender/kit/mcp/m007.py` → `build()`.
Assets (collection `Kit/M007 Coal`): `Coal` (hero, all parts unioned), `CoalChunkMain`, `CoalChunkLeft`, `CoalChunkRight` (the sheet's Main Chunk and Side Chunks; R01 owns `CoalMainChunk`), `CoalBaseRockCenter`, `CoalBaseRockLeft`, `CoalBaseRockRight`.

## Study (2a)

- **Classification:** full asset (resource node), budget 4000 tris; parts 1000.
- **Silhouette:** a tall dark faceted main chunk with a shorter side chunk each side, a broad pale base rock in front and smaller base rocks round the foot; wider than tall; broad flat faces, no bevels.
- **Parts:** 1 main chunk, 2 side chunks, 3 base rocks (left, centre, right); the hero adds four small extra foot rocks as on the sheet's views.
- **Scale:** 10.4 × 7.1 × 7.2 studs.
- **Colours (true sRGB swatches):** coal #313035, base rock #9D8F8A, secondary grey #727075. Matte; solid colours, no texture.
- **Effects:** none shown; lighting and VFX stages skipped.

## Delivery

- Palette: `m007_coal` #2C2C31 with `m007_coal_grey` #3B3B42 patches (broad, by noise), `m007_base_rock` #9B8C88, `m007_base_rock_cool` #928988.
- Hero: exact boolean union, cut flat at the base plane (z = 0), grazing slivers repaired: one closed manifold shell, 834 tris.

## Result

- Verifier round 1 PASS 7/10; base rock then nudged toward the swatch (palette only).
- Open minors: chunks taller and more columnar than the sheet's rounder, egg-like ones; side chunks could tuck in tighter.
