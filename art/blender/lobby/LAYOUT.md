# Lobby map layout (from `art/reference/lobby_map.png`)

Coordinates are studs. Origin = the bonfire at the plaza centre. **+Y = north** (toward the Deploy gate), **+X = east**. Every asset's front faces -Y in its library, so rotate each one around Z until its front faces the plaza unless noted. The reference is a high three-quarter view from the south; the camp is a **wide oval**.

This matches the draft plan in [`docs/maps/lobby-hub.md`](../../../docs/maps/lobby-hub.md): Deploy north, Arrival south, Forge NE, Vault E, Elder's totem NW, Market W, bonfire plaza in the centre.

## Ground and terrain

| Element | Spec |
| --- | --- |
| Plateau | Grass ground ellipse ~95 × 75 radius, gently uneven, `grass_ground`. Beyond it the terrain drops away into grey chiselled cliffs built from the **07 terrain kit**: CliffSection runs with CliffOuterCorner/CliffInnerCorner tiles around the plateau rim, RockShelfTwoLevels for stepped edges, ForestFloor tiles under the outer forest, and a GrassRamp or EarthSwitchback where the north path leaves the gate and descends |
| River and waterfall | The NE river uses Riverbank tiles, with a **WaterfallCliff** where it drops off the plateau edge (top right of the reference) |
| Plaza | Dirt disc, radius ~22, `dirt`, centred at the origin |
| Paths | Dirt paths ~7 wide from the plaza edge to: the Deploy gate (north), the Arrival stones and the south entrance (south), the Forge (NE), the Vault hall (E), the Market (W) and the Elder's totem (NW). The north path continues out of the gate into the forest |
| Grass patches | Between the paths: grass tufts, clumps, ferns, herbs, wildflowers and shrubs clustered along path edges and the wall |
| River | NE corner, outside the wall: a river running down from the top right, with a waterfall drop and a FootbridgeSmall crossing it near (70, 48) |
| Forest | A dense ring of broadleaf and pine trees outside the wall on every side, thickest north and at the bottom corners. Mix every tree variant; random rotation and ±15% scale |

## Palisade ring

- An oval wall, radius **x 68, y 50**, built from PalisadePanelA/B (10 studs wide), alternating with some random variation, following the ellipse tangent. That is ~36 panels.
- **North gap** for the DeployGate at (0, 50), about 26 wide. **South entrance** at (0, -50): a ~10-wide gap closed by a low rail fence made of FootbridgeSmall rails or planks, flanked by PalisadeEndPosts.
- A **PalisadeTorchPost** every ~5 panels, plus extra torches flanking both gaps.
- **PalisadeBannerPanel** on either side of the Deploy gate, either side of the south entrance, and at the east and west extremes.
- Boulders (sheet 06) half-buried along the base of the wall inside and out.
- **WatchPlatformOpen** at the SW curve, around (-62, -30). **WatchtowerTall** at the W/NW curve, around (-66, 14). Both stand inside the wall, against it.

## Zones

| Zone | Centre | Contents |
| --- | --- | --- |
| Bonfire plaza | (0, 0) | Campfire at the centre; **six LogBenches** in a ring of radius ~11, each tangent to the ring. Torch posts at the plaza edge facing the paths |
| Deploy gate | (0, 50) | DeployGate in the wall gap, facing south into the camp. A stepping-stone path from the plaza to the gate. Two StoneBraziers at the gate's inner corners |
| Elder's totem | (-40, 32) | EldersTotem (scaled ~1.6×). Two or three TallBoulders and ElongatedRuneStones stood upright around it. StoneBrazier and TorchPost nearby. QuestBoard at (-24, 27) facing the plaza. Barrels and crates by the board. A BroadleafTreeWideOld inside the wall behind the totem |
| Ancestral Forge | (40, 32) | AncestralForge facing SW toward the plaza. Out front: AnvilLarge, CraftingWorkbench, a WeaponRack, Barrels, a SmeltingFurnace to one side, a stone step apron |
| Vault hall | (45, -6) | VaultHall facing west toward the plaza. Inside and in front: LargeChest, SmallChest, OpenChest, a LedgerLectern at the entrance, WeaponRacks either side, and a red rug made of a thin `cloth_red` slab |
| Market | (-46, 0) | ThatchMarketStall at (-55, 6), HideMarketStall at (-38, 5) and another HideMarketStall at (-50, -12), all facing the plaza. Barrels, SupplyCrates, ClayStoragePots, WovenBaskets and a CraftingWorkbench as a counter around them |
| Arrival stones | (0, -32) | LargeRuneStone at the centre. A ring of SteppingStones and small rune stones around it (radius ~7). A StoneBrazier beside it. Paths lead north to the plaza and south to the entrance |

## Camera for the comparison render

A perspective camera south of the camp, high and looking north-down at ~50–55°, framing the whole oval wall plus a band of forest, like the reference. Lighting: a warm, bright afternoon sun from the upper left, soft sky fill, and glowing torch and forge emissives.
