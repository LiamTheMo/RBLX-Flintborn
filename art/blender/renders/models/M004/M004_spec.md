# 004 Obsidian — spec

Reference: `art/blender/assets/references/004.png` (OBSIDIAN). Builder: `art/blender/kit/mcp/m004.py` → `build()`.
Assets (collection `Kit/M004 Obsidian`): `Obsidian` (hero, all parts unioned), `ObsidianCrystalA`–`E` (the sheet's Obsidian Chunk A–E; the kit's R02 sheet owns `ObsidianChunk*`), `ObsidianRockCluster` (the sheet's Base Rock cluster).

## Study (2a)

- **Classification:** full asset (large resource node), budget 4000 tris; parts 1000.
- **Silhouette:** a cluster about as wide as it is tall; three tall crystals (A left, B centre and tallest, C right) fan outward from a low ring of rounded rocks, with two small crystals (D front-right, E front-left) in front.
- **Crystals:** fat faceted shafts (width about 0.45 of height), widest about a third of the way up, tapering to a sharp, slightly off-centre point; a flat joining surface underneath (sunk into the rocks: clean intersection, no gaps).
- **Base rock:** a ring of eleven rounded faceted rocks (about a third of the height) with broad planes; planar underside.
- **Scale:** 9.9 × 8.0 × 8.1 studs (about 1.5 character heights).
- **Colours (true sRGB):** swatches obsidian primary #2D2C32, mid tone #3C455C, edge tone #757585, base rock #9A8882. Rendered sheet: crystals median #2F313C (lit up to #737B8A), rocks lit #A69391.
- **Surface:** glassy (roughness 0.35) dark faces with broad mid-tone blue patches; the light edge tone is specular catch on thin sharp edges, so it is left to lighting (a modelled edge chamfer read as a wireframe overlay).
- **Effects:** none shown; lighting and VFX stages skipped.

## Delivery

- Palette: `m004_obsidian` #26262C, `m004_obsidian_mid` #353D55 (broad noise patches, not by facing), `m004_rock` #968680, `m004_rock_cool` #8E8483.
- Crystals fan outward 13-16° (true lean angle), about half their faces in the mid tone, short off-centre chisel tips.
- Hero: exact boolean union of rocks and crystals, cut flat at the rocks' base plane (z = 0): one closed manifold shell, 1380 tris.

## Result

- Rounds: 1 PASS 6.5 (crystals upright: a lean-angle bug) · 2 FAIL 6 (base left at z 0.34 with a stray vertex below) · **3 PASS 6.5/10** (flat base at z = 0, all checks clean). Rocks then lifted to `m004_rock` #968680 (palette only).
- Open minors: crystals leaner and sharper than the sheet's chunky blunt ones; small front crystals partly hidden by the front rocks.
