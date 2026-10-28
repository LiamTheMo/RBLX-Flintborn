# 011 Amethyst — spec

Reference: `art/blender/assets/references/011.png` (AMETHYST, page 11). Builder: `art/blender/kit/mcp/m011.py` → `build()`.

Assets (collection `Kit/M011 Amethyst`):

- `Amethyst` (hero).
- `AmethystShellTop` (the hollow dome).
- `AmethystShellBottom` (the rock lip).
- `AmethystShard` (reusable crystal).

The R03 kit sheet owns `AmethystTopShell`, `AmethystBottomShell` and `AmethystCrystal`, which is why the parts have these names.

## Study (2a)

- **Classification:** full asset (resource node / geode), budget 4000 tris; parts 1000.
- **Silhouette:** a broad, hollow, faceted rock dome open to the front, with a thick, rounded lip of stone rolled right round the mouth. Its mouth leans back over the crown, so the crystals show from above. The walls are thick stone, and the cavity is bare shaded stone; only the crystals are purple. A fan of purple crystals stands on the cave floor: a tall main one reaching most of the way up the mouth, two big leaning side ones and four smaller ones, filling the mouth. Two big flat-topped slabs form the lip across the mouth, with one more slab at each side. The rear reads as a plain rounded boulder.
- **Parts:** top shell, bottom shell, crystal (x4+, reusable).
- **Scale:** 11.7 × 10.0 × 8.3 studs.
- **Colours (sheet swatches):** crystal light #C097DD, mid #924EC3, dark #5F3289; rock #9E8F8B. The sheet's cave interior reads a dark violet (#362333 in shadow). Solid colours, no texture.
- **Effects:** none shown, so the lighting and VFX stages were skipped.

## Delivery

- **Palette:**
  - Crystal light, mid and dark at the swatch colours, as broad facet regions (by noise, not by facing).
  - `m011_rock` #9E8F8B, with `m011_rock_dark` #8D7F7C patches.
  - `m011_cave` #857774 and `m011_cave_dark` #736764, the bare stone inside the cave (two tones as broad facet patches).
- **Hero:**
  - A faceted dome.
  - The cavity and mouth are carved by an exact boolean difference (`kit_models.carve`). The cut faces take the cave stone, and the walls are about 1.5 studs thick.
  - The mouth is a flat cut through the dome's front, leaning back 20°. A faceted torus of stone (tube radius 0.85) follows the cavity's edge on that cut, so the lip is thick and round.
  - The crystals and lip rocks are joined in (`kit_models.merge_in`), then unioned and cut flat at z = 0.
  - One closed manifold shell, 1122 tris.

## Result

- Verifier round 1 PASS 6/10 (all technical checks clean; no crystal pokes through the shell). Then: the dome made wider and rounder; the mouth tilted further back so the crystals show from above; the crystals made fatter, with a front-left one added; the lip made blocky and flat-topped and wrapped round the sides.
- User review ("looks a little odd"): the cave read as an empty dark void with small crystals at the bottom, and the lip read as a row of pebbles. Fixed by making the crystals much bigger so they fill the mouth, using a lighter violet lining, and making the lip two big slabs plus side slabs. A 4-face boolean speck left inside is now removed (`kit_models.drop_specks`).
- User review 2 ("should have a bit of rock/stone but it just turns into the crystal purple inside with a thin lining"): the inside is now bare stone in two shades instead of a violet lining, and the cavity is smaller, so the walls and rim are about 1.5 studs thick.
- User review 3 ("still has that thin lip on the outer area"; "it should still have the lip but like thicker and round"): the rounded scoop that thinned the wall to a knife edge was replaced by a flat cut with a thick rolled lip on it. The crystals moved back so the hood covers them.
- Open minors: the rock reads slightly pink under the studio key light.
