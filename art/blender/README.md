# Flintborn Blender assets

Source art for Flintborn's reusable 3D assets and the lobby map, built from the reference sheets in [`art/reference`](../reference).

| Path | Contents |
| --- | --- |
| `lib/flintkit.py` | Shared palette, modelling helpers (`Asset`), studio camera and contact-sheet renderer. **Every build script imports it.** |
| `scripts/build_NN_<sheet>.py` | One script per reference sheet. Builds every asset on that sheet from scratch and saves the `.blend`. |
| `assets/NN_<sheet>.blend` | Generated asset libraries: each asset is one mesh object, marked as a Blender asset, in a collection per category. |
| `lobby/FlintbornLobby.blend` | The lobby map, assembled from the asset libraries. |
| `renders/` | Contact sheets laid out like the reference sheets, plus single-asset cells, for side-by-side checks. |

## Running

Rebuild any sheet with the wrapper, which gives an honest exit code and checks that the `.blend` was actually rewritten:

```bash
art/blender/run.sh scripts/build_01_buildings.py
```

The wrapper exits 0 on success, 1 on a Blender or Python error, and 2 if the output wasn't updated. The full log goes to `art/blender/logs/`. Rebuild the sheets first, then `run.sh scripts/build_lobby.py`, which links them, then `run.sh scripts/build_showcase.py`.

Rendering uses Eevee headless (Blender 5.2). A 16-asset sheet renders in well under a minute.

## Conventions

- **Units:** 1 Blender unit = **1 Roblox stud**. A Roblox character is ~5.5 studs tall. Import into Studio with units set to studs.
- **One asset = one mesh object**, multi-material, named in PascalCase after its sheet label (`PalisadePanelA`, `EldersTotem`). The origin is at the **bottom centre** and the front faces **-Y**.
- **Held tools and weapons** are modelled upright, with the grip end at the origin and the head toward +Z; the render tilts them to match the sheet.
- **Look:** chunky, hand-hewn, faceted low poly with flat shading. Wood is hewn into 6–8 sided posts with pale carved tips and cut ends, lashed with golden rope; stone is chiselled into big facets; iron is dark with rivets; thatch is golden straw; leaves are faceted clusters.
- **Palette:** only `flintkit.PALETTE` keys. Every mesh carries a `Tint` colour attribute, so each part gets a slight hand-painted brightness variation.
- **Budget:** aim for ≤ 3,000 triangles for props, ≤ 8,000 for buildings and large trees (`obj["tris"]` records it). Roblox meshes must stay well under 20,000.
- **VFX:** live effects are **VFX sockets** (`lib/vfx.py`): Empties named `VFX_<kind>` parented to the asset at the emitter point, carrying the Roblox ParticleEmitter/PointLight spec as JSON. Kinds: torch_fire, campfire, brazier_fire, forge_fire, chimney_smoke, embers, heat_glow, glyph_glow, rune_glow, waterfall_mist, water_foam, dust, plus the world kit's waterfall_curtain, water_flow, vapour and harvest kinds (see World kit). Particle textures are rendered by `scripts/build_08_vfx.py` into `art/vfx/textures/`, and `vfx.realize()` turns sockets into preview lights and particles. Emissive meshes stay on the asset as the static look.
- **Roblox export:** `run.sh scripts/export_lobby_roblox.py art/roblox/lobby/manifest.json` writes the lobby to `art/roblox/lobby/`:
  - one `.glb` per unique mesh, so Roblox downloads each shape once and clones it for every placement;
  - `palette.png`, a single texture carrying every palette colour at 32 `Tint` levels;
  - `manifest.json`, with placements, collision profiles, VFX sockets, the arrival spawn and NPC spots.

  Fire colours become Neon parts and water becomes see-through parts. The **Upload and place the lobby map** workflow (`scripts/roblox_lobby_map.py`) uploads the export and builds `Workspace.LobbyMap` in the lobby place.

## World kit (`art/reference/kit`)

The world kit is the reusable library for the big map. It is built from 34 reference sheets in `art/reference/kit/`: World `W01`–`W16`, Resources `R01`–`R08` and Vegetation `V01`–`V10`. It sits alongside the lobby sheets above and never changes them.

- **One module per subject row:** `scripts/kit/<SHEET>/<module>.py` defines `SUBJECT`, `ROW`, an optional `PALETTE` of extra colours (keys prefixed with the sheet id) and `build(kit)`. `build` tags every asset with `kit.tag(obj, role, collision=...)`. The roles are `hero` (assembled), `variant` (the VARIATIONS column), `part` (each exploded part, so pieces can be kit-bashed), and `depleted` / `drop` (resource nodes and the items they give).
- **Runner:** `BLENDER_ARGS="W01" run.sh scripts/build_kit.py assets/kit/W01.blend` builds a whole sheet. Add `--only <module>` to build one subject into `assets/kit/wip/`. The runner checks every asset: role, PascalCase name, bottom-centre origin, palette materials and triangle budget. It then writes `<SHEET>_stats.json` and renders `renders/kit/<SHEET>/<module>_compare.png`, with the reference row above the built row.
- **Colouring and texture:** a material may use several related palette keys for meaningful regions (young and old leaves, a damp rock base, warm and cool stone) and per-face Tint variation in broad patches for surface texture; avoid per-triangle confetti. The runner only records shade pairs (`shade_pairs`) and Tint range (`tint_spread`) per asset. In Roblox each face shows its key's colour at one of 32 Tint levels from `palette.png`.
- **Lighting is not paint:** the light tops and dark sides on the reference sheets come from lighting, so faces are never coloured by which way they face (colour regions and Tint texture are fine). The runner measures it per asset: brightness against face direction within each family of shades, recorded as `baked_shading`. Above 0.5 it reports a problem. A real material change, such as snow on top, can set `obj["kit_shading_ok"] = "reason"`. The kit studio is lit with a strong warm sun so the colours read like the sheets.
- **Foliage helpers:** build leaves with `Asset.leaf_cluster` and `Asset.canopy`, not with single smooth `leaf_blob` / `ico` spheres. Both keep one material, flat facets and a small random Tint per clump, and delete faces buried inside another clump.
  - `leaf_cluster(radius, loc, lobes=7, facets=1|2, ...)` makes one chunky "cauliflower" clump: a lobed dome with a low peak, broad protruding lobes and deep notches between them, and a flat base. It costs 110 tris for 7 lobes at `facets=1` and 152 at `facets=2`. Use it for the exploded "Leaf Clump" parts, small shrubs, and clumps placed by hand on branch tips.
  - `canopy(center, size, ...)` fills a crown or bush ellipsoid with ~14-18 overlapping clumps, plus an inner layer and a filler core, so it reads as one dense, lumpy mass. Clumps are bigger on top, tilted outward and sized to the canopy, and `droop` gives a hanging rim. A 14 × 14 × 10 crown costs ~2400-2600 tris. For a crown of several masses (one canopy per branch end), pass `facets=1, core=False, inner=False, clumps=6-9`, which costs ~750 tris per mass. Smaller `clump_radius` gives a finer floret texture but uses more tris.
- **Colours:** kit colours live in `flintkit.KIT_PALETTE`, separate from `PALETTE`, so the lobby's uploaded `palette.png` keeps its layout.
- **Harvest VFX:** `harvest_hit` and `harvest_deplete` are burst sockets. They have no steady rate; the game calls `Emit(burst)` when the socket's `trigger` happens (`hit` or `deplete`). `ore_glint` adds twinkles on glossy ore. The chip texture is `rock_chip`. Render only new textures with `FX_ONLY=tex FX_TEX=rock_chip run.sh scripts/build_08_vfx.py ../vfx/textures/rock_chip.png`.
- **Reference rows:** `BLENDER_ARGS="W01 R01" run.sh scripts/kit_crop_refs.py <expected png>` cuts sheets into `art/reference/kit/rows/<SHEET>_row<N>.png`.
- **Water and vapour VFX:** falling water, flowing streaks and steam are VFX sockets, not only mesh.
  - `waterfall_curtain`: a Roblox **Beam** of falling water. Put the socket on the top lip and pass the point where the fall meets the pool: `vfx.add(obj, "waterfall_curtain", lip, end=foot, width=8)`. It has two layers of the `waterfall_streaks` texture, scrolling down at 15 and 22 studs/s (Wrap, 10 and 6 studs per tile, LightEmission 0.25 and 0.35, transparency 0.15–0.3 and 0.5–0.7, white to pale blue). It also has a light `Spray` emitter (splash_droplets) along the lip, whose width follows `width`. For a wide fall, use several sockets side by side.
  - `water_flow`: a flat Beam (FaceCamera false) lying on a river or stream surface, with `water_streaks` scrolling slowly (4 studs/s) from the socket to `end`, so start → end is the flow direction. Put it a few hundredths of a stud above the water.
  - `vapour`: soft white rising steam or spray haze (`mist_soft` and `smoke_puff`, 72–100% transparent, slow). It is separate from the grey `chimney_smoke`.

  A **beam** spec has: name, texture, color and transparency (sequences from start to end), width0/width1, texture_speed (studs/s, positive = start to end), texture_length (studs per tile), texture_mode, light_emission, light_influence, segments, face_camera, and optionally curve0/curve1.
  - The socket stores `vfx_end` (Blender local) and has a child Empty `<socket>_End` at the end point.
  - The JSON gets `end` (Roblox axes, relative to the socket), `axis` (the Attachments' Axis, which CurveSize bends along) and `normal` (their SecondaryAxis, the face of a flat beam). `normal=` and `axis=` override them.
  - A beam texture's width (u) runs along the beam. Both beam textures tile in u and v; they are painted with numpy, not rendered.
  - `vfx.realize()` previews each beam as a textured, blended strip from the socket to its end, so kit renders show the falling water.
  - Render only new textures: `FX_ONLY=tex FX_TEX=waterfall_streaks,water_streaks run.sh scripts/build_08_vfx.py ../vfx/textures/waterfall_streaks.png`.
- **See-through water:** water keys are `water`, `water_deep`, `water_shallow` and any key containing `water` (`w03_water_shallow`, `w03_water_fall`).
  - In Blender, kit water renders blended with alpha = 1 − its Roblox transparency, single-sided and without a shadow. This applies only to KIT_PALETTE and sheet-prefixed keys; PALETTE water stays opaque, so the lobby renders as before.
  - Transparency is 0.3 for keys with `deep`, 0.5 for `shallow` and 0.4 otherwise. A material's `kit_transparency` property overrides it; set it with `flintkit.set_water_transparency(mat, t)`.
  - Kit water renders with the same texture the exporter writes (`lib/kitwater.py`, cached as `assets/kit/water_preview/<key>.png` and repainted when the colour changes), times Tint, box-projected from Object coordinates at 16 studs per tile, so the preview matches Roblox.
- **Roblox export:** `scripts/export_kit_roblox.py` writes `art/roblox/kit/<SHEET>/`: one `.glb` per mesh piece, a per-sheet `palette.png`, and a manifest with sizes, collision settings and VFX sockets.
  - **Water** becomes one piece per water key, `<Asset>_water_<key>.glb`, plus a 512×512 tileable texture `water/<key>.png`. The texture is painted from the key's colour: lighter cartoon caustic lines, a fainter fine net, and a few foam specks. It is seamless both ways.
  - Water UVs are a box projection in studs from the asset origin, one tile per 16 studs (up-facing faces: u = X/16, v = Z/16 in Roblox). The pattern runs on across pieces and across assets placed on a 16-stud grid.
  - Each water piece in the manifest has `texture`, `tile_studs`, `transparency`, `material: SmoothPlastic`, `cast_shadow: false` and no collision. It also has `flow` (direction, speed) when the asset has a `water_flow` socket, so a place script can scroll a Texture.
  - Water uses SmoothPlastic, not Glass. Glass tints and reflects the sky, which washes out the stylised colours. It also hides transparent things behind it, such as the waterfall Beam and particles, and it looks different at each graphics quality level.
  - Beam sockets carry `end`, `axis` and `normal` in Roblox axes.
- **Logs:** `run.sh` names each log after the script and its `BLENDER_ARGS` (`logs/build_kit-W01_only_boulder.log`), so parallel module builds never overwrite each other's logs.

## Scale sheet (studs, width × depth × height)

| Sheet | Asset sizes |
| --- | --- |
| 01 Buildings | VaultHall 26×18×15 · AncestralForge 30×18×24 · DeployGate 26×6×20 (10-wide opening) · ThatchMarketStall 14×8×10 · HideMarketStall 14×8×10 · PrimitiveShelter 10×10×8 |
| 02 Fences & towers | PalisadePanelA 10×1.8×9.5 (6 stakes ≈1.65 Ø) · PalisadePanelB 10×1.8×8–10.5 · CornerPalisade 10×10×10 · CurvedPalisade 10 chord ×10 · PalisadeGate 10×2×10 · PalisadeEndPost 2.4 Ø ×10.5 · PalisadeTorchPost 3.5×2.4×11 · PalisadeBannerPanel 8.5×1.8×9.5 · WatchPlatformOpen 8×8×8 · WatchtowerTall 7×7×14 · WatchtowerRoofed 9×9×17 · FootbridgeSmall 14×6×4 · lobby wall: PalisadeMainPost 2.6 Ø ×12 on a 4.4×3.9 stone footing · PalisadeMainPostBanner 4.3×3.9×12 · PalisadeMainPostTorch 4.4×3.9×14.2 (flame) · PalisadeSection 10×2.4×8 · PalisadeSectionLow 10×1.9×5.8 · LogRailFence 10×2.3×4.1 (sections tile at 10; a main post stands centred on each join) |
| 03 Furnishings | SmallChest 3×2×2.2 · LargeChest 4.2×2.6×3.2 · OpenChest 3.6×2.4×3.6 · StorageCabinet 3.4×2.4×5.5 · EldersTotem 3.5×3.5×10 · QuestBoard 6×1.5×5.5 · LedgerLectern 3.5×3×4.5 · WeaponRack 6×2.5×5 · AnvilLarge 4×2×3.2 · AnvilSmall 2.6×1.6×2.8 · CraftingWorkbench 6×3×3.2 · SmeltingFurnace 4.5×4.5×7 · Barrel 2.4 Ø ×3.2 · SupplyCrate 3×3×3 · ClayStoragePot 2.4 Ø ×2.6 · WovenBasket 2.6 Ø ×1.2 |
| 04 Weapons & tools (length) | StoneAxeBasic 3.2 · StoneAxeBroadHead 3.4 · IronAxe 3.6 · StonePickaxeDouble 3.6 · IronPickaxe 3.6 · WoodenSpear 7 · StoneSpear 7 · IronSpear 7.2 · StoneKnife 1.8 · IronShortSword 3.6 · StoneWarClub 3.4 · TimberClubBone 3.4 · WoodenBowSimple 4.5 · WoodenBowLaminated 4.8 · StoneArrow 3 · BlacksmithHammer 2.8 |
| 05 Trees & plants (width × height) | BroadleafTreeStout 16×22 · BroadleafTreeTall 18×26 · BroadleafTreeWideOld 26×24 · BroadleafTreeLeaning 18×22 · PineTreeShortWide 15×18 · PineTreeTallNarrow 13×26 · PineTreeMature 17×24 · PineTreeYoung 9×14 · ShrubLowWide 7×3.5 · ShrubTallDense 5×5.5 · BerryBush 5.5×4.5 · BroadLeafHerb 4×2.5 · GrassTuftLarge 3×2 · GrassClumpSmall 2×1.4 · WildflowerWhite 3×2.4 · FernLeafy 4×2.4 |
| 07 Terrain kit (modular, 32-stud grid; front/cliff face toward -Y) | CliffSection 32×20×18 · CliffOuterCorner 32×32×18 · CliffInnerCorner 32×32×18 · RockShelfTwoLevels 32×24×10 · GrassRamp 32×20, rising 0→10 · EarthSwitchback 32×32×14 · CaveEntrance 32×24×18 (opening 10×9) · RockArch 32×20×16 (opening 12×9) · Riverbank 32×24×4 · RockyLakeshore 32×28×5 · WaterfallCliff 28×28×20 with pool · ForestFloor 32×32×3 |
| 09 Character (R6) | Default R6 sizes: Head part 2×1×1 (rounded mesh 1.25×1.25×1.2, centred 0.5 above the neck) · Torso 2×2×1 · Arms 1×2×1 · Legs 1×2×1 (5 studs tall). The armature uses Roblox's default R6 joints (RootJoint, Neck, Shoulders, Hips), with each part rigidly on its bone. Clothing is separate meshes: Shirt (hide wrap and knot, on the Torso), PantsWaist (Torso), PantsLeftLeg / PantsRightLeg (their legs). Baked colour, normal and roughness maps, a neutral pants map for tinting, and ten tribe colours, in `art/character/textures/`. Roblox export with joint data in `art/roblox/character/manifest.json` |
| 06 Rocks, runes & camp | LowBoulder 8×6×4 · TallBoulder 5×4.5×9 · SplitBoulder 6.5×5.5×6 · LongBoulder 11×5×4 · LargeRuneStone 10×8×1.6 · ElongatedRuneStone 8×5×1.4 · TriangularRuneStone 6×5.5×2.5 · SteppingStone 8×6×1.4 · CutLog 8×2.4×2.4 · FallenLog 9×3×2.6 · Stump 3.4 Ø ×2.4 · ChoppingStump 2.6 Ø ×3 · Campfire 6.5 Ø ×5 · LogBench 7×1.8×1.8 · TorchPost 1 Ø ×7 · StoneBrazier 2.6×2.6×4.6 |
