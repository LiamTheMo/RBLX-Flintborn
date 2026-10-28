# World kit builder guide

This page is all a kit agent needs. **Read this instead of `flintkit.py`, `vfx.py`, `build_kit.py`, the README or the lobby sheet scripts.** Open one of those only to check a signature this page lacks, and then grep for that one function rather than reading the file. Units are studs (1 Blender unit). A Roblox character is about 5.5 studs tall. Fronts face -Y, and every asset's origin sits at its bottom centre.

## Module contract

`art/blender/scripts/kit/<SHEET>/<module>.py` defines:

```python
SUBJECT = "OakTree"      # PascalCase row label
ROW = 1                  # 1-4, the sheet row
PALETTE = {"w05_bark": ("#8A5A32", 0.9, 0.0, 0.0)}   # key: (hex, roughness, metallic, emission)
HERO_AZIMUTH = -22       # optional: hero/variant camera (-22 front-left, +22 front-right)
SIDE_AZIMUTH = 90        # optional: 135 = rear three-quarter when the SIDE/REAR cell shows the back

def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    a = fk.Asset("OakTree", "W05 OakTree")
    ...                                   # add parts (see below)
    o = a.finish()                        # one mesh, origin at the bottom centre
    vfx.add(o, "harvest_hit", (0, -2, 3))   # optional sockets, asset-local studs
    return [kit.tag(o, "hero", collision="hull", budget=6000, notes="...")]
```

- **Roles:** `hero`, `variant`, `part`, `depleted`, `drop`.
- **Default triangle budgets:** hero and variant 3000, part 1500, depleted 2000, drop 300. Large terrain, buildings and big trees can go up to 8000.
- **Collision:**
  - `box` or `hull` for solid objects;
  - `precise` for walkable or hollow shapes (arches, stairs, decks, huts);
  - `none` for small scatter that players walk through.
- **Every labelled part and every variation is its own asset,** with the PascalCase names from your spec.
- **Asset names must be unique across the whole sheet.** All 4 modules go into one `.blend`, so prefix part names with your subject: `DaisyStem`, `WildflowerLeaf`, never a bare `Stem` or `Leaf`. A duplicate gets renamed `Leaf.001` and fails the sheet build.

## Build and look

```bash
BLENDER_ARGS="<SHEET> --only <module>" art/blender/run.sh scripts/build_kit.py art/blender/assets/kit/wip/<SHEET>_<module>.blend
```

- **Output:** it prints `KITSTAT` lines (tris against budget, size in studs) and `KITPROBLEM` lines. A build is only done at **0 problems**.
- **Compare image:** read `art/blender/renders/kit/<SHEET>/<module>_compare.png`, which has the reference row on top and yours below. Open individual cells in `<module>_cells/` only when you need a close look at one of them.
- **Stats:** `art/blender/assets/kit/wip/<SHEET>_<module>_stats.json` records tris, sizes, materials, sockets, `baked_shading`, `shade_pairs` and problems.
- **Iterations:** 3 to 4 build-look-fix rounds, and stop as soon as every must goal is met. Don't re-read an image that hasn't changed.

## Asset API

All methods add geometry to the asset and return its verts. Rotations are radians (XYZ). `mat` is a palette key. Shading is flat and faceted.

| Method | Use |
| --- | --- |
| `rock(size, loc, rot, mat, subdiv=2, rough=0.12, facets=14, sink=0.15)` | chiselled boulder; `size` is the full (x, y, z) extent |
| `ico(radius or (rx, ry, rz), loc, rot, mat, subdiv=1, jitter, facets=deg, face_tint_var)` | faceted blob |
| `cyl(r1, r2, h, sides=8, loc, rot, mat, jitter, cap=True, twist)` | faceted cylinder or cone, base at z=0 |
| `box(size, loc, rot, mat, bevel, jitter, base=False)` | box; `plank(size, ...)`, `stone_block(size, ...)` |
| `beam(p1, p2, radius, sides=7, mat="wood", end_mat="wood_end")` | log between two points with cut ends |
| `stake(radius, height, tip, loc, sides=7)` / `post(radius, height, loc)` | palisade stake / flat-topped post |
| `poly_prism(points2d, depth, loc, rot, mat)` | extruded 2D outline (counter-clockwise points) |
| `tube_loop(points3d, thickness, mat, rseg=5, closed=True)` | rope, vine or root along a polyline |
| `rope_rings(radius, z, count, ...)`, `lashing(loc, size)`, `rope_band(xs, radius, z)` | rope wraps |
| `torus(R, r, loc, rot, mat)`, `strip(points2d, width, depth)`, `flame(height, radius, loc)` | misc |
| `leaf_blob(radius, loc, mat)` | one smooth blob: don't use it on its own for foliage |
| `leaf_cluster(radius, loc, mat, lobes=7, squash=0.8, facets=1, depth=1.0, axis=None, floor=None)` | one star-shaped, multi-lobed leaf clump (about 110–150 tris); use it for clump parts and hand-placed clumps |
| `canopy(center, size, mat, clumps=None, clump_radius=None, density=1.0, droop=0.0, facets=2, floor=None, bulge=0.45, tilt=0.35)` | **a whole dense crown or bush** (about 2400 tris for a 14×14×10 crown). For multi-mass crowns like the oak, call it once per mass (e.g. 4 masses of 8×8×6.5, `facets=1`). For more distinct clumps, use a smaller `clump_radius` and `tilt` around 0.5 |
| `transform(verts, loc, rot, scale)` | move verts you already built. **Hazard:** `rock()`, `ico(subdiv>=2)`, and `ico` or `leaf_blob` with `facets=` invalidate verts returned by *earlier* calls on the same Asset. Transform each part, or assign its material, right after creating it, never after a later rock or ico call |
| `finish()` | write the mesh; origin at the bottom centre; marked as an asset |

## Rules every verifier enforces

1. **Proper colouring and texture.** Give each material real colour: several related palette keys for meaningful regions (young leaf tips vs older leaves, a damp base band on rock, a warmer and a cooler stone, bark vs heartwood) and per-face Tint variation in broad patches for surface texture. Avoid confetti: one random colour per triangle reads as noise. The runner records `shade_pairs` and `tint_spread` for reference only.
2. **Don't paint the sun in.** The reference's lit tops and shadowed sides come from lighting, so don't colour faces by which way they face. The runner reports `baked_shading` above 0.5 as a problem. A real material change (snow on top, a wet base) may set `obj["kit_shading_ok"] = "reason"`.
3. **Choosing a base colour.** Pick it so the **render** matches the reference: lit faces as bright and saturated as the reference's lit faces, and shadow faces as dark as its shadows. Start from the reference's middle tone, not the highlight. Foliage tends to render washed out, so darken and saturate it.
4. **Different materials** (moss vs leaves, bark vs heartwood, ore vs host rock) each get their own single key. Extra keys are prefixed with the lower-case sheet id, for example `w05_bark`.
5. **Water, falling water and vapour:**
   - Waterfalls, spray, foam lines, flow streaks, mist, smoke, steam and vapour are **VFX sockets, never meshes**.
   - Water surfaces are simple flat meshes using a key that contains `water`. They export as a tiled, semi-transparent water texture.
   - Anything under the water gets a deep blue-teal `<sheet>_riverbed` colour, about `#0B6E8F`. Never put `water` in that key's name.
6. **Drops** are closed meshes with no holes. Nothing sits below z=0. Each asset is one mesh.
7. **Goals.** Before modelling, write `art/blender/renders/kit/<SHEET>/<module>_goals.md`:
   - At least 15 must or should goals, one group per cell, about silhouette, proportions, counts, colours, scale and VFX.
   - After every build, mark each goal MET or UNMET **by eye** against the reference row. Numbers support a judgement but never prove a visual goal.

## VFX sockets

`vfx.add(obj, kind, loc, scale=1.0, end=None, **overrides)` takes asset-local studs. Overrides replace spec keys, for example `color=["#hex", "#hex"]`, `emitters=[...]` or `light={...}`. Only existing textures are available; put any new texture need in `shared_lib_requests`.

| Kind | Use |
| --- | --- |
| `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `embers`, `heat_glow`, `glyph_glow`, `rune_glow` | fire, glow, runes (pair each with an emissive mesh) |
| `chimney_smoke`, `vapour`, `dust` | smoke, white steam or haze, motes |
| `waterfall_curtain` | Beam from the top lip; `end=(x, y, z)` where the fall lands; `width=` override; use several side by side for a wide fall |
| `waterfall_mist`, `water_foam` | splash mist where a fall lands; foam along shores and rims |
| `water_flow` | flat Beam lying on a river; start→end is the flow direction |
| `harvest_hit`, `harvest_deplete`, `ore_glint` | resource nodes: hit on the strike face, deplete at the base, glint only on glossy ore |
| `crystal_glow`, `crystal_halo` | glowing crystals: a steady PointLight in the open (override `light`), and a faint glow billboard behind the crystal (override the emitter `color`) |

Note each socket's purpose in the asset's `kit.tag(..., notes=...)`.
