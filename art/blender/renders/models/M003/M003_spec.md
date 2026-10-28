# 003 Iron — spec

Reference: `art/blender/assets/references/003.png` (IRON, rock resource). Builder: `art/blender/kit/mcp/m003.py` → `build()`.
Assets (collection `Kit/M003 Iron`): `Iron` (hero, all parts unioned), `IronHostRockM003`, `IronChunkM003`, `IronBaseRockM003` (the kit's R02 sheet already owns `IronHostRock`, `IronChunk` and `IronBaseRock`, so these carry the model code).

## Study (2a)

- **Classification:** full asset (resource node), budget 4000 tris; parts 1000.
- **Silhouette:** a broad, chunky grey dome (front W:H about 1.2), round footprint, broad flat facets, no bevels.
- **Parts:** Host Rock (reusable) with flat facets where the chunks attach; Iron Chunk (reusable), a thick six-sided slab with a faceted steel top and a rust-orange depleted edge (rim band) round its sides; Base Rock (reusable), five small grey rocks round the foot.
- **Chunks:** five on the hero: large front-left, upper front-right, lower front-right, rear-left, rear-right, so the front, rear and top views each show three, as on the sheet.
- **Scale:** in line with the Stone and Flint nodes: host 6.9 × 6.4 × 5.6 studs; hero 7.8 × 6.8 × 5.6.
- **Colours (true sRGB):** swatches host #AB9B95, iron #675F5E, rim #BE7C5B; sheet render: host median #8B8081, chunk steel lit about #AEB3C7, rust rim #7C4126 (lit #B76746).
- **Surface:** clean solid colours, no textures; steel slightly glossy and metallic (roughness 0.35, metallic 0.4).
- **Effects:** none shown; lighting and VFX stages skipped.

## Delivery

- Palette: `m003_host` #7C7172, `m003_host_cool` #726C72, `m003_iron` #9CA3B8 (rough 0.35, metal 0.4), `m003_rust` #A85A33, `m003_base_rock` #8A8080. Rendered host median #887C7B vs the sheet's #8B8081.
- The steel/rust split is a material region (chunk vs depleted edge), flagged `kit_shading_ok`.
- Hero: exact boolean union of host, chunks and base rocks (chunks sunk 0.1 below their facets to avoid coplanar faces): one closed manifold shell, 988 tris.

## Result

- Verifier round 1 PASS 6.5/10; after a denser host (~110 verts), thinner gem-topped chunks with a tapered rim and seven base rocks, re-verified PASS 6.5/10.
- Open minors: chunk thickness (one verifier wants thin flush inlays, the other thicker slabs with a mottled rim); host smoother than the sheet's; steel facets flatter than the sheet's specular streaks.
