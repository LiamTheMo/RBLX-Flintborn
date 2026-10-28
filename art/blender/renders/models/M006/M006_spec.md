# 006 Copper — spec

Reference: `art/blender/assets/references/006.png` (COPPER). Builder: `art/blender/kit/mcp/m006.py` → `build()`.
Assets (collection `Kit/M006 Copper`): `Copper` (hero, all parts unioned), `CopperHostRock`, `CopperInsertA` (large), `CopperInsertB` (medium), `CopperInsertC` (small), `CopperBaseRockA` (left), `CopperBaseRockB` (right).

## Study (2a)

- **Classification:** full asset (resource node), budget 4000 tris; parts 1000.
- **Silhouette:** a pale, chunky faceted stone dome (near-round footprint, like the Stone node), bright copper inserts standing proud of it front, top, sides and rear, two small grey base rocks at the front corners; flat underside.
- **Inserts:** chunky faceted nuggets with broad facets of similar size, sitting proud with a clear contact edge; teal oxidation on some of their facets and smudged onto the host round each one.
- **Scale:** host 6.9 × 6.5 × 5.8 studs; hero 8.6 × 8.0 × 5.9.
- **Colours (true sRGB swatches):** stone host #BCA28E, copper metal #DC672D, oxidation #55958F, base rock #ADA6A4. Sheet host render median #978679.
- **Surface:** solid colours, flat shading, no noise.
- **Effects:** none shown; lighting and VFX stages skipped.

## Delivery

- Palette: `m006_stone` #958274, `m006_stone_cool` #8C7E78, `m006_copper` #D45A1E (roughness 0.55, metallic 0.2), `m006_oxidation` #3F8B80 (+ a stone/teal half-mix for soft smudge edges), `m006_base_rock` #958C8B. Rendered host #92837A vs the sheet's #978679.
- Host facets split once (coplanar) so the oxidation smudges stay small.
- Hero: exact boolean union of host, six inserts (the three part sizes repeated round the rock) and the two base rocks: one closed manifold shell, 1030 tris.

## Result

- Verifier round 1 PASS 6/10.
- Open minors: inserts read as rounded nuggets where the sheet's are angular and elongated; oxidation patches hard-edged; host facets smaller than the sheet's.
