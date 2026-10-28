# 005 Quartz — spec

Reference: `art/blender/assets/references/005.png` (QUARTZ, cave crystal). Builder: `art/blender/kit/mcp/m005.py` → `build()`.
Assets (collection `Kit/M005 Quartz`): `Quartz` (hero, all parts unioned), `QuartzMainCrystalM005`, `QuartzSideCrystalM005`, `QuartzBaseRockM005` (the kit's R03 sheet owns the plain names).

## Study (2a)

- **Classification:** full asset (cave crystal node), budget 4000 tris; parts 1000.
- **Silhouette:** one large pale crystal standing upright in the middle, four smaller side crystals fanning out (two at the sides, two at the front), all rising out of a mound of rounded dark faceted rocks; overall a little wider than tall.
- **Crystals:** six-sided prisms with a short flat root and a six-faced pyramidal cap to a point; broad simple facets. Main crystal width about 0.48 of its height.
- **Joining:** crystals mount into the rock mound (simple junction); flat bottom that sits on terrain.
- **Scale:** 11.1 × 7.9 × 9.5 studs.
- **Colours (true sRGB swatches):** crystal main #F1E1D4, crystal side #BEADA3, rock base #7A6E6B. Flat shaded; no noise or texture.
- **Effects:** none shown; lighting and VFX stages skipped.

## Delivery

- Palette: `m005_crystal` #E6D8CD, `m005_crystal_side` #B9ABA4 (broad face patches by noise, not by facing), `m005_rock` #7E716D, `m005_rock_cool` #776E6E.
- Hero: exact boolean union of rocks and crystals, cut flat at the rocks' base plane (z = 0), grazing-contact slivers repaired: one closed manifold shell, 1216 tris.

## Result

- Verifier round 1 PASS 6.5/10; main crystal colour then lifted toward the swatch (palette only).
- Open minors: crystals more regular and slimmer than the sheet's; rock mound smaller and sparser behind the main crystal.
