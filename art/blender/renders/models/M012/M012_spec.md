# 012 Amber — spec

Reference: `art/blender/assets/references/012.png` (AMBER, page 12). Builder: `art/blender/kit/mcp/m012.py` → `build()`.

Assets (collection `Kit/M012 Amber`):

- `Amber` (hero, all parts unioned).
- `AmberCrystalMain`, the sheet's Amber Nodule. The R03 kit sheet owns `AmberNodule`.
- `AmberWoodFront`, `AmberWoodBack`, `AmberWoodLeft`, `AmberWoodRight`: the sheet's Wood Base (Front) and (Rear), and Side Wood (Left) and (Right).

## Study (2a)

- **Classification:** full asset (resource node), budget 4000 tris; parts 1000.
- **Silhouette:** a big egg-shaped faceted amber nodule nestled in weathered wood.
  - Chunky splintered beams lie stacked across its front and back.
  - Broad upright splintered planks stand at its sides and rear, leaning outward, and the tallest at the back right reaches the top of the nodule.
  - Flat bottom; broad flat faces.
- **Parts:** amber nodule; wood base (front) and (rear); side wood (left) and (right). The hero also has two broad rear uprights as on the sheet's rear views.
- **Scale:** 9.2 × 7.8 × 6.9 studs.
- **Colours (sheet swatches):** amber light #FECD64, mid #FE7719, dark #D25117; wood #8D5D3D. Solid colours, no texture.
- **Effects:** none shown, so the lighting and VFX stages were skipped.

## Delivery

- **Palette:**
  - Ambers at the swatch colours, mostly mid with light and dark facet regions (by noise, not by facing); roughness 0.3.
  - `m012_wood` #8D5D3D, with `m012_wood_light` #9C6845 and `m012_wood_dark` #84563A patches.
- **Wood pieces:** five-sided beams with uneven sides and unevenly cut (splintered) ends. The uprights taper to about half width at the top.
- **Hero:** exact boolean union, then cut flat at the ground. One closed manifold shell, 820 tris.

## Result

- Verifier round 1 PASS 6/10 (all technical checks clean). Then: the thin upright spikes merged into fewer, broader slabs; the front log made thicker and sloped; the nodule given more facets (40 points); the dark wood lightened.
- Open minors: the wood reads very dark in the rear, side and underside renders (studio lighting).
