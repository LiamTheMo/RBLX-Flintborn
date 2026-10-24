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
- **VFX:** live effects are **VFX sockets** (`lib/vfx.py`): Empties named `VFX_<kind>` parented to the asset at the emitter point, carrying the Roblox ParticleEmitter/PointLight spec as JSON. Kinds: torch_fire, campfire, brazier_fire, forge_fire, chimney_smoke, embers, heat_glow, glyph_glow, rune_glow, waterfall_mist, water_foam, dust. Particle textures are rendered by `scripts/build_08_vfx.py` into `art/vfx/textures/`, and `vfx.realize()` turns sockets into preview lights and particles. Emissive meshes stay on the asset as the static look.
- **Roblox export (later):** materials are flat palette colours; the `Tint` variation and emissive fire are Blender-side. Bake or split by material when exporting.

## Scale sheet (studs, width × depth × height)

| Sheet | Asset sizes |
| --- | --- |
| 01 Buildings | VaultHall 26×18×15 · AncestralForge 30×18×24 · DeployGate 26×6×20 (10-wide opening) · ThatchMarketStall 14×8×10 · HideMarketStall 14×8×10 · PrimitiveShelter 10×10×8 |
| 02 Fences & towers | PalisadePanelA 10×1.8×9.5 (6 stakes ≈1.65 Ø) · PalisadePanelB 10×1.8×8–10.5 · CornerPalisade 10×10×10 · CurvedPalisade 10 chord ×10 · PalisadeGate 10×2×10 · PalisadeEndPost 2.4 Ø ×10.5 · PalisadeTorchPost 3.5×2.4×11 · PalisadeBannerPanel 8.5×1.8×9.5 · WatchPlatformOpen 8×8×8 · WatchtowerTall 7×7×14 · WatchtowerRoofed 9×9×17 · FootbridgeSmall 14×6×4 · lobby wall: PalisadeMainPost 2.6 Ø ×12 on a 4.4×3.9 stone footing · PalisadeMainPostBanner 4.3×3.9×12 · PalisadeMainPostTorch 4.4×3.9×14.2 (flame) · PalisadeSection 10×2.4×8 · PalisadeSectionLow 10×1.9×5.8 · LogRailFence 10×2.3×4.1 (sections tile at 10; a main post stands centred on each join) |
| 03 Furnishings | SmallChest 3×2×2.2 · LargeChest 4.2×2.6×3.2 · OpenChest 3.6×2.4×3.6 · StorageCabinet 3.4×2.4×5.5 · EldersTotem 3.5×3.5×10 · QuestBoard 6×1.5×5.5 · LedgerLectern 3.5×3×4.5 · WeaponRack 6×2.5×5 · AnvilLarge 4×2×3.2 · AnvilSmall 2.6×1.6×2.8 · CraftingWorkbench 6×3×3.2 · SmeltingFurnace 4.5×4.5×7 · Barrel 2.4 Ø ×3.2 · SupplyCrate 3×3×3 · ClayStoragePot 2.4 Ø ×2.6 · WovenBasket 2.6 Ø ×1.2 |
| 04 Weapons & tools (length) | StoneAxeBasic 3.2 · StoneAxeBroadHead 3.4 · IronAxe 3.6 · StonePickaxeDouble 3.6 · IronPickaxe 3.6 · WoodenSpear 7 · StoneSpear 7 · IronSpear 7.2 · StoneKnife 1.8 · IronShortSword 3.6 · StoneWarClub 3.4 · TimberClubBone 3.4 · WoodenBowSimple 4.5 · WoodenBowLaminated 4.8 · StoneArrow 3 · BlacksmithHammer 2.8 |
| 05 Trees & plants (width × height) | BroadleafTreeStout 16×22 · BroadleafTreeTall 18×26 · BroadleafTreeWideOld 26×24 · BroadleafTreeLeaning 18×22 · PineTreeShortWide 15×18 · PineTreeTallNarrow 13×26 · PineTreeMature 17×24 · PineTreeYoung 9×14 · ShrubLowWide 7×3.5 · ShrubTallDense 5×5.5 · BerryBush 5.5×4.5 · BroadLeafHerb 4×2.5 · GrassTuftLarge 3×2 · GrassClumpSmall 2×1.4 · WildflowerWhite 3×2.4 · FernLeafy 4×2.4 |
| 07 Terrain kit (modular, 32-stud grid; front/cliff face toward -Y) | CliffSection 32×20×18 · CliffOuterCorner 32×32×18 · CliffInnerCorner 32×32×18 · RockShelfTwoLevels 32×24×10 · GrassRamp 32×20, rising 0→10 · EarthSwitchback 32×32×14 · CaveEntrance 32×24×18 (opening 10×9) · RockArch 32×20×16 (opening 12×9) · Riverbank 32×24×4 · RockyLakeshore 32×28×5 · WaterfallCliff 28×28×20 with pool · ForestFloor 32×32×3 |
| 06 Rocks, runes & camp | LowBoulder 8×6×4 · TallBoulder 5×4.5×9 · SplitBoulder 6.5×5.5×6 · LongBoulder 11×5×4 · LargeRuneStone 10×8×1.6 · ElongatedRuneStone 8×5×1.4 · TriangularRuneStone 6×5.5×2.5 · SteppingStone 8×6×1.4 · CutLog 8×2.4×2.4 · FallenLog 9×3×2.6 · Stump 3.4 Ø ×2.4 · ChoppingStump 2.6 Ø ×3 · Campfire 6.5 Ø ×5 · LogBench 7×1.8×1.8 · TorchPost 1 Ø ×7 · StoneBrazier 2.6×2.6×4.6 |
