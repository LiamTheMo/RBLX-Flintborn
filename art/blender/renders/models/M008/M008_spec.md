# 008 Azurite — spec

Reference: `art/blender/assets/references/008.png` (AZURITE, page 10). Builder: `art/blender/kit/mcp/m008.py` → `build()`.
Assets (collection `Kit/M008 Azurite`): `Azurite` (hero, all parts unioned), `AzuriteCrystalMain`, `AzuriteCrystalSide` (reusable for all three side crystals), `AzuriteRockBase`, `AzuriteRockSide` (reusable, x2). The R03 kit sheet owns `AzuriteMainCrystal` and `AzuriteBaseRock`, so the parts use crystal/rock-first names.

## Study (2a)

- **Classification:** full asset (resource node), budget 4000 tris; parts 1000.
- **Silhouette:** four chunky bright-blue six-sided crystals: a tall main crystal, a large one leaning left, two smaller ones leaning right. They grow out from behind a broad low faceted base mound, with side rocks round the foot and smaller rocks behind. Broad flat faces, no bevels.
- **Parts:** 1 main crystal, 3 side crystals (one reusable part), 1 base rock, 2 side rocks; the hero adds four back rocks as on the sheet's rear and top views.
- **Scale:** 12.6 × 8.4 × 9.2 studs.
- **Colours (sheet swatches):** azurite light #3FCBFD, mid #0F96F4, dark #0170C0; rock light #C8B7AE, mid #9B8B83, dark #897B76. Crystals are slightly glossy; rocks are matte. Solid colours, no texture.
- **Effects:** none shown; lighting and VFX stages skipped.

## Delivery

- Palette: `m008_azurite_light` #1AB4EE, `m008_azurite_mid` #0A8ADC, `m008_azurite_dark` #0562B4 as broad facet regions (by noise, not by facing). Rocks: `m008_rock_mid` #827877, with `m008_rock_light` #998F8E and `m008_rock_dark` #6A6463 as smaller patches. Tones are calibrated against the sheet's rock renders (#9F928D front, #BCA79B three-quarter).
- Hero: exact boolean union, cut flat at the base plane (z = 0): one closed manifold shell, 908 tris, zero non-manifold edges.

## Result

- Verifier round 1 PASS 6.5/10 (all technical checks clean). Then: base mound made more angular, crystal tops chunkier, the two right crystals 15% larger and the front one moved forward, one more back rock.
- Open minors: rear, side and underside renders read the rocks near-black (studio lighting, not the palette).
