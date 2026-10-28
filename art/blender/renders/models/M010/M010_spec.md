# 010 Gold — spec

Reference: `art/blender/assets/references/010.png` (GOLD, page 6). Builder: `art/blender/kit/mcp/m010.py` → `build()`.

Assets (collection `Kit/M010 Gold`):

- `Gold` (hero, all parts unioned).
- `GoldHost`. The R02 kit sheet owns `GoldHostRock`.
- `GoldNuggetLarge`, `GoldNuggetMedium`, `GoldNuggetSmall`.
- `GoldRockSmall`. The R02 kit sheet owns `GoldBaseRock`.

## Study (2a)

- **Classification:** full asset (resource node), budget 4000 tris; parts 1000.
- **Silhouette:** a lumpy brown faceted host rock, nearly as tall as it is wide, narrowing to a peaked crown. Chunky bright-yellow nuggets stand proud of it in shallow seats: three on the front (left, centre-right and top-right) and three round the back. Small grey base rocks sit round the foot, and the bottom is flat. Broad flat faces.
- **Parts:**
  - host rock;
  - gold nuggets: large, medium and small;
  - base rock (small, reusable).
- **Scale:** 9.6 × 9.6 × 7.6 studs.
- **Colours (sheet swatches):** host #9F7C68, gold #F7CC3A, dark brown #76605A. The lit host crown in the sheet's renders reads #AA836C. Solid colours, no texture.
- **Effects:** none shown, so the lighting and VFX stages were skipped. (The nuggets are slightly metallic, but no glow is shown.)

## Delivery

- **Palette:**
  - `m010_host` #8F705F, with `m010_host_dark` #806456 as broad patches (by noise). These are set halfway between the swatch and the darker sheet render. Our crown now reads #B88B71 against the sheet's #AA836C.
  - `m010_gold` #F7CC3A, with `m010_gold_deep` #EBB72A facets; metallic 0.3.
  - `m010_base` #9A8A82.
- **Hero:** exact boolean union of the host, six nuggets (seated by ray casts) and four base rocks. One closed manifold shell, 710 tris.

## Result

- Verifier round 1 PASS 6/10 (all technical checks clean). Then: host made taller, with a peaked, lumpier crown; nuggets made more irregular; the front base rocks enlarged.
- Open minors: no visible recessed seats round the nuggets (they are sunk into the host instead); the host reads a touch pink under the studio key light.
