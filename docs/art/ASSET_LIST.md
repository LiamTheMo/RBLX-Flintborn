# Flintborn asset list

Everything the game needs modelled or given an effect, taken from the game's own data rather than from wish lists:

- the catalogs in `src/shared` (nodes, biomes and POIs, build pieces, items and tiers, creatures, bosses, events);
- the placeholder model modules in `src/shared/Visuals` (`NodeModels`, `SceneryModels`, `PropModels`, `CreatureModels`, `GearModels`) and the services that spawn things;
- the art trackers: [`MODEL_PROGRESS.md`](MODEL_PROGRESS.md), [`art/blender/assets/references/INDEX.md`](../../art/blender/assets/references/INDEX.md), [`art/vfx/`](../../art/vfx/README.md) and the lobby export in `art/roblox/lobby/`.

State as of 2026-11-03 (branch v0.19).

## Status key

| Mark | Meaning |
| --- | --- |
| ✅ | Final art exists: a passed world-kit model, a lobby-set model or a live effect. It may still need hooking into the play world (see "The big gap" below). |
| 🔨 | In progress: a world-kit model being built or verified, or an effect whose texture and emitter spec exist but which is not live yet. |
| 🟨 | Placeholder only: a code-built primitive (`src/shared/Visuals/*Models.luau`, a service's plain part) or a stock Roblox effect. |
| ⬜ | Missing: nothing exists yet. |
| — | Not applicable (no such item, or no effect wanted). |

**Ref 049** means the numbered model reference `art/blender/assets/references/049.png`, tracked in `MODEL_PROGRESS.md`. **W09** and similar mean the older world-kit sheets in `art/reference/kit/`. **Suggested** marks an idea that is not in the game's data or design docs; it is a proposal, not a requirement.

## Summary

Counts are per line in the tables below, and per cell in the tier tables (every tier variant counts once).

| Section | Items | ✅ | 🔨 | 🟨 | ⬜ |
| --- | --- | --- | --- | --- | --- |
| 1. Environment | 218 | 64 | 2 | 65 | 87 |
| 2. Events, enemies and animals | 58 | 6 | 0 | 43 | 9 |
| 3. Physical gear | 111 | 12 | 0 | 93 | 6 |
| 4. Visual effects | 85 | 12 | 9 | 20 | 44 |
| **Total** | **472** | **94** | **11** | **221** | **146** |

Items marked "—" (not applicable) are not counted. In section 1, 12 of the ✅ items are lobby art (8 lobby groups holding 96 meshes, and 4 lobby-set stations); the other 52 are passed world-kit models.

### The big gap

**Nothing in the play world uses final art yet.** Every resource node, tree, rock, creature, boss, build piece, held item, event prop and landmark you see in a run is a code-built primitive. The world kit has 68 passed models exported to `art/roblox/kit/` (M001–M067, M069), but no game code loads them. Only the lobby (96 meshes, live) and the player character use final meshes. A loader that swaps the placeholder recipes (`NodeModels`, `SceneryModels`, `PropModels`) for kit meshes would move most of the ✅ lines in sections 1 and 2 from "art done" to "in game" at once.

### Biggest gaps

1. **Creatures and bosses: no art, no animation.** All 20 creatures, 6 bosses and the Guardian's pillars are primitive stacks that slide along the ground with no animation. There are no creature reference sheets in the repo, only the written briefs in `Modeling.md`. The 9 lobby NPC spots are empty.
2. **Gear: 78 weapons, tools and armor pieces, 10 with art.** Only the sheet-04 lobby props exist as models: wooden, stone and iron spears; stone and iron axes and pickaxes; a stone dagger, an iron sword and a wooden bow. No armor has art. About 22 shared meshes with tier materials would cover all of it (see section 3).
3. **Building: 32 tiered pieces and 9 single pieces are plain boxes.** Four shapes × three construction families (timber, stone, metal plate) plus metal tints would cover the 32.
4. **Art and game disagree on resources.** Coal, Gold, Sulfur, Quartz, Azurite and Amber have finished models but no game node. The game's Silver, Cobalt, Mithril and Jade deposits and its Redcap and Chestnut mushrooms have no art; Juniper, Elderberry, Raspberry and Hazel have reference sheets (125, 106, 107, 109) that have not been started.
5. **Caves, ruins, forts and Frostpeak are unstarted.** The Shattered Keep (the Guardian's arena), the Fallen Temple, Timberwatch, Emberhollow and Frostpeak all need sets that are still ⬜ (refs 071–102 and 143–157).

### Things that hurt gameplay readability now

- **Rare loot looks like common loot.** A dropped Epic or Legendary item has no glow, beam or colour; only Permanent items get a faint gold box, and only the Guardian's Fang highlights its carrier. GDD §36.5 asks that rare loot stays visible.
- **Arrows are thin brown sticks with no trail**, although the GDD wants slow, visible arrows.
- **No hit feedback in the world**: damage numbers only. Creatures have no wind-up or attack animation, so only a boss Quake (red disc) is telegraphed.
- **Depleted nodes vanish.** There is no stump or rubble, so players cannot see where a node will regrow.
- **A placed Portable Extraction Rune has no object**, only the beacon column, and the 3-second extraction departure has no effect.
- **Downed players have no world-side marker**: the downed state is a HUD card only, so tribe-mates have to find them by the overhead bar.

---

## 1. Environment

### 1.1 Terrain, cliffs and rocks (10)

The island ground itself is Roblox smooth Terrain with per-zone materials, so it needs no meshes. Scenery today is `SceneryModels` "Boulder" (2 placeholder variants). The older W01 Boulder, Rock Spire and Rock Cluster also passed but are superseded by 035, 039 and 036.

| Asset | Ref | Status | Notes |
| --- | --- | --- | --- |
| Boulder | 035 | ✅ | |
| Rock cluster | 036 | ✅ | |
| Rock spire | 039 | ✅ | |
| Pebble scatter | 038 | ✅ | |
| Cliff wall (tiling) | 040 | ✅ | Tiles with 043 and 044 |
| Terraced ledge | 043 | ✅ | |
| Natural ramp (walkable) | 044 | ✅ | |
| Natural arch | 046 | ✅ | |
| Snowy cliff and boulder | 096 | ⬜ | Frostpeak Ridge |
| Alpine ground patch | 097 | ⬜ | Frostpeak Ridge |

### 1.2 Caves and mine (10)

For Emberhollow Caves: the mouth landmark and the 450 × 350 interior carved under the hill.

| Asset | Ref | Status | Notes |
| --- | --- | --- | --- |
| Cave entrance ring | 079 | ⬜ | |
| Tunnel module | 082 | ⬜ | |
| Cave column | 085 | ⬜ | |
| Cave shelf / ledge | 087 | ⬜ | |
| Mine support frame | 081 | ⬜ | |
| Mine track | 084 | ⬜ | |
| Minecart | 086 | ⬜ | |
| Gantry and ore lift | 088 | ⬜ | |
| Mine stairs and ladder | 153 | ⬜ | |
| Mine sign and lantern | 155 | ⬜ | |

### 1.3 Water (6)

Water surfaces are Terrain water (Crater Lake, the river, the sea shelf); these are the dressing modules.

| Asset | Ref | Status | Notes |
| --- | --- | --- | --- |
| Shoreline corner | 032 | ✅ | |
| Shore shelf (sea stack) | 041 | ✅ | |
| Streambed section | 034 | ✅ | |
| Waterfall module | 037 | ✅ | |
| Ice pool | 099 | ⬜ | Frostpeak Ridge |
| Riverbank chunk | W03 | ⬜ | Only in the older kit sheet (rough draft); no numbered reference |

### 1.4 Trees and wood (13)

Scenery today is `SceneryModels` "Pine", "Broadleaf" and "Log" (2 placeholder variants each). The harvestable Tree node is in 1.11.

| Asset | Ref | Status | Notes |
| --- | --- | --- | --- |
| Classic pine | 049 | ✅ | |
| Young fir | 042 | ✅ | |
| Pine sapling | 045 | ✅ | |
| Old pine | 047 | ✅ | |
| Snow pine | 094 | ⬜ | Frostpeak; the game already draws snow on its "frost pines" |
| Broadleaf tree | 054 | ✅ | |
| Ancient tree | 057 | ✅ | Also dresses Giant Roots |
| Dead tree | 053 | ✅ | |
| Fallen log | 055 | ✅ | |
| Hollow stump | 092 | ⬜ | |
| Birch | 122 | ⬜ | |
| Willow | 123 | ⬜ | |
| Rowan | 127 | ⬜ | |

### 1.5 Plants, ground cover and fungi (33)

Scenery today is `SceneryModels` "Tuft" and "Fern" (1 placeholder each). These are decor only: none of them is gathered.

| Asset | Ref | Status | Notes |
| --- | --- | --- | --- |
| Grass tuft | 059 | ✅ | |
| Broadleaf fern | 060 | ✅ | |
| Low bush | 058 | ✅ | |
| Meadow herb (daisy) | 061 | ✅ | |
| Wildflowers | 065 | ✅ | |
| Ground scatter (leaves, pinecone, twigs) | 062 | ✅ | |
| Hanging vine | 063 | ✅ | Leaf outline left for a polish pass |
| Moss and ivy (ruin block) | 056 | ✅ | |
| Clover patch | 103 | ⬜ | |
| Field sedge | 104 | ⬜ | |
| Bluegrass clump | 105 | ⬜ | |
| Dandelion rosette | 108 | ⬜ | |
| Strap fern | 110 | ⬜ | |
| Rosehip scrub | 111 | ⬜ | |
| Trumpet vine | 112 | ⬜ | |
| Heartleaf creeper | 113 | ⬜ | |
| Bracken fern | 114 | ⬜ | |
| Bulrush fan | 115 | ⬜ | |
| Pondweed | 116 | ⬜ | |
| Cattail clump | 117 | ⬜ | |
| Water lily | 118 | ⬜ | |
| Amber shelf fungus | 119 | ⬜ | |
| Puffball | 121 | ⬜ | |
| Cave trumpet fungus | 124 | ⬜ | |
| Dry tussock | 126 | ⬜ | |
| Heather | 128 | ⬜ | |
| Alpine cushion | 129 | ⬜ | |
| Thorn scrub | 131 | ⬜ | |
| Flax patch | 130 | ⬜ | Uncommon harvestable in the art set; no game node or item |
| Silkleaf rosette | 132 | ⬜ | Same: no game node |
| Redroot | 134 | ⬜ | Same: no game node |
| Sunpod shrub | 137 | ⬜ | Same: no game node |
| Giant redcap mushroom | 101 | ⬜ | Landmark scale, not the Redcap node |

### 1.6 Paths, bridges and walkways (11)

| Asset | Ref | Status | Notes |
| --- | --- | --- | --- |
| Dock | 048 | ✅ | |
| Timber footbridge | 050 | ✅ | For Mill Bridge and Ferry Bridge |
| Rope crossing | 051 | ✅ | |
| Boardwalk | 052 | ✅ | |
| Root-arch walkway | 098 | ⬜ | Giant Roots landmark |
| Timber scaffold | 154 | ⬜ | |
| Wall catwalk | 157 | ⬜ | |
| Stone path | W09 | ⬜ | Older kit sheet only |
| Stone stair | W09 | ⬜ | Older kit sheet only |
| Timber fence | W09 | ⬜ | Older kit sheet only |
| Wayfinding post | W09 | ⬜ | Older kit sheet only; useful for navigation without a minimap |

### 1.7 Fortifications and buildings (10)

For Timberwatch, the event Forts (Abandoned Fort, Warlord's Hold) and Mosswick Forest.

| Asset | Ref | Status | Notes |
| --- | --- | --- | --- |
| Palisade wall (stockade + tiling module) | 069 | ✅ | |
| Timber hut | 068 | 🔨 | Built; round-2 verification next |
| Timber gate | 072 | ⬜ | |
| Barricade | 073 | ⬜ | |
| Wall walk | 075 | ⬜ | |
| Watchtower | 076 | ⬜ | Timberwatch Tower |
| Hunt workshop | 077 | ⬜ | |
| Guard lodge | 080 | ⬜ | |
| Lookout platform | 083 | ⬜ | |
| Mosswick stump hall | 095 | ⬜ | Mosswick Forest |

### 1.8 Ruins (10)

For the Shattered Keep (the Guardian's arena), the Fallen Temple and the Crumbling Ruins event.

| Asset | Ref | Status | Notes |
| --- | --- | --- | --- |
| Ruined lean-to | 070 | 🔨 | Built; verification next |
| Ruin block wall | 089 | ⬜ | |
| Ruin arch | 090 | ⬜ | |
| Ruin column | 091 | ⬜ | Keep and Temple both use broken columns |
| Courtyard floor and steps | 093 | ⬜ | Keep courtyard |
| Keep gate monument | 145 | ⬜ | Keep gates |
| Temple gateway | 147 | ⬜ | Fallen Temple |
| Courtyard ruin | 150 | ⬜ | |
| Lake ruin tower | 100 | ⬜ | Crater Lake; could also stand in for the Old Lighthouse |
| Ruin camp shelter | 102 | ⬜ | |

### 1.9 Camp, shore and storage props (11)

The lobby set (1.12) already has a campfire, barrels, crates, pots, baskets and benches that can dress world camps meanwhile.

| Asset | Ref | Status | Notes |
| --- | --- | --- | --- |
| A-frame tent | 064 | ✅ | Safe camps, Raider Camp |
| Canvas shelter | 066 | ✅ | |
| Table and seating | 067 | ✅ | |
| Supply crate (crates, barrels) | 071 | ⬜ | |
| Fire and light station (fire pit, tripod, brazier) | 074 | ⬜ | Camp fire pits |
| Craft rack | 078 | ⬜ | |
| Banner and brazier | 146 | ⬜ | Event Camp and Fort dressing |
| Shore work rack | 152 | ⬜ | |
| Rowboat | 148 | ⬜ | |
| Mooring post | 149 | ⬜ | |
| Log raft | 151 | ⬜ | |

### 1.10 POIs and landmarks (12)

All are built by `WorldBuildService` from parts at startup. Each needs a final set made from the kit pieces named in the notes.

| POI | Status | Placeholder today | Final art needs |
| --- | --- | --- | --- |
| Shattered Keep + Guardian arena | 🟨 | Walled courtyard, 4 corner towers, 2 gates, broken keep tower | 089–091, 093, 145, 150 |
| Fallen Temple | 🟨 | Broken columns, fallen roof slab, altar | 091, 147 |
| Timberwatch Tower | 🟨 | Block tower | 069 (done), 072, 075, 076, 080, 083 |
| Emberhollow Mouth and cave | 🟨 | Basalt pillars, lintel, glowing crystals; carved Terrain interior | 1.2 set |
| Frostpeak Summit | 🟨 | Peak marker | 094, 096, 097, 099 |
| Mill Bridge and Ferry Bridge | 🟨 | Plank bridges | 050 (done) |
| Old Lighthouse | 🟨 | Block tower | No reference sheet yet |
| Giant Roots | 🟨 | Root shapes | 057 (done), 098 |
| The Monoliths | 🟨 | Standing blocks | No reference sheet; the lobby rune stones are a start |
| Safe camps: Tidewater Camp, Mossfire Camp | 🟨 | Tents, fire pit, trader stalls | 064, 066, 067 (done), 074; the lobby market stalls |
| Ritual altars × 2 (Keep West, Keep North) | 🟨 | `PropModels.Altar`: plinth, 4 rune stones, bowl, flame | 143 |
| Authored island map (`ShatteredCrater`) | ⬜ | The generated island (`IslandLayout`) ships instead | `docs/maps/README.md` lists it as not started |

### 1.11 Resource nodes (26 nodes + 6 depleted shapes)

From `NodeCatalog.Nodes`. Each hit drops material on the ground. Placeholders are `NodeModels` recipes. The art column names the finished model to use.

| Node | Gives | Art to use | Status |
| --- | --- | --- | --- |
| Tree | Wood (+ Resin) | 049 / 054 / 042 (same art as the scenery trees) | ✅ |
| Rock | Stone (+ Flint) | 001 Stone; 002 Flint as a variant | ✅ |
| Fiber plant | Plant Fiber | 022 Fiber shrub | ✅ |
| Herb shrub | Herbs | 018 Healing herb | ✅ |
| Redberry bush | Redberry | 017 Berry bush | ✅ |
| Sweetberry bush | Sweetberry | 017 Berry bush with pink berries (shared) | ✅ |
| Copper deposit | Copper Ore | 006 | ✅ |
| Iron deposit | Iron Ore | 003 | ✅ |
| Silver deposit | Silver Ore | No sheet; 003's host rock with silver chunks | 🟨 |
| Cobalt deposit | Cobalt Ore | No sheet; 008 Azurite (blue) is closest | 🟨 |
| Mithril deposit | Mithril Ore | No sheet; 005 Quartz in pale cyan is closest | 🟨 |
| Obsidian outcrop | Obsidian | 004 | ✅ |
| Jade vein | Jade | No sheet; 005 Quartz in green is closest | 🟨 |
| Clay deposit | Clay | 023 | ✅ |
| Amethyst geode | Amethyst | 011 | ✅ |
| Starstone outcrop | Starstone | 014 | ✅ |
| Stormglass cluster | Stormglass | 016 | ✅ |
| Cave mushroom patch | Cave Mushroom | 031 | ✅ |
| Redcap mushroom patch | Redcap Mushroom | No small sheet (101 is the giant landmark) | 🟨 |
| Chestnut mushroom patch | Chestnut Mushroom | 120, not started | 🟨 |
| Thorn shrub | Thornvine | 024 | ✅ |
| Frost shrub | Frostleaf | 028 | ✅ |
| Juniper shrub | Juniper Berry | 125, not started | 🟨 |
| Elderberry shrub | Elderberry | 106, not started | 🟨 |
| Raspberry bush | Raspberry | 107, not started | 🟨 |
| Hazel shrub | Hazelnut | 109, not started | 🟨 |

**Depleted states.** Today a depleted node simply turns invisible until it regrows. Six shared shapes would cover every node. The older R-sheets hold rough drafts (for example `BerryShrubDepleted`), none passed.

| Depleted shape | Used by | Status | Notes |
| --- | --- | --- | --- |
| Chopped tree stump | Tree | ⬜ | 020 Hardwood stump is a ready base |
| Rock and ore rubble | Rock, 5 ore deposits, Obsidian, Jade, Clay | ⬜ | The exported host-rock parts (for example M003's) are a quick base |
| Broken crystal stub | Amethyst, Starstone, Stormglass | ⬜ | |
| Picked shrub | Berry, nut, thorn and frost shrubs (9 nodes) | ⬜ | |
| Picked herb / fiber tuft | Herb shrub, Fiber plant | ⬜ | |
| Picked mushroom patch | 3 mushroom patches | ⬜ | |

**Already modelled with no game node (not counted above):** 005 Quartz, 007 Coal, 008 Azurite, 010 Gold, 012 Amber, 013 Sulfur, 019 Resin node, 020 Hardwood stump, 021 Root cluster, 026 Softwood log, 027 Reed patch, 029 Ancient root, 030 Mooncap and 033 Cave moss. They can dress the world as decor, stand in for the nodes above (008 for Cobalt, 005 for Mithril and Jade, 020 as the stump), or become nodes later. 009, 015 and 025 are used by events (section 2).

### 1.12 Lobby (live) (11)

Built from the earlier Blender sheets 01–07, uploaded and placed by the lobby-map workflow. 96 meshes in all.

| Group | Meshes | Status | Contents |
| --- | --- | --- | --- |
| Buildings | 6 | ✅ | Vault Hall (+ red rug), Ancestral Forge, Deploy Gate, Thatch market stall, Hide market stall |
| Palisade, towers, bridge | 9 | ✅ | Palisade sections (2), main posts (plain, banner, torch), log rail fence, watchtower tall and roofed, small footbridge |
| Stations and furnishings | 15 | ✅ | Elder's totem (+ stela footings), quest board, ledger lectern, weapon rack, large anvil, workbench, smelting furnace, large and open chests, cabinet, barrel, crate, clay pot, woven basket |
| Weapon and tool display props | 11 | ✅ | See section 3; also a war club, bone club and blacksmith hammer the game has no item for |
| Camp | 7 | ✅ | Campfire, log bench, torch post, stone brazier, cut log, fallen log, stump |
| Rocks and rune stones | 9 | ✅ | 4 boulders, 2 rune stones, stepping stone, rock arch, two-level rock shelf |
| Trees and plants | 16 | ✅ | 4 broadleaf, 4 pine, 2 shrubs, berry bush, herb, 2 grass, wildflower, fern |
| Terrain, water, ground | 23 | ✅ | Cliff section and corner, switchback, riverbank, waterfall cliff, forest floor, forge stairs, rim skirt, 15 ground tiles |
| Rebirth shrine prop | — | ⬜ | Station id `RebirthShrine` exists; no distinct prop |
| Medical / Rarework table prop | — | ⬜ | Station id `RareworkTable` exists; the Forge has no fourth table |
| Recent Extractions board | — | ⬜ | Station id `ExtractionBoard`; only one board (the quest board) stands by the totem |

The station prompt parts (`LobbyStation:<id>`) are not placed yet either; that is a map task, not a model.

### 1.13 Building pieces (41 tier variants and pieces + 5 crops)

From `StructureCatalog`. Every piece is one plain box in its tier's colour and material (`BuildingService`). Suggested sharing: each tiered shape needs only three construction families (timber for Wood, masonry for Stone, plate for the metals), with the six metals told apart by colour and trim, so **12 meshes cover the 32 tier variants**.

| Piece (size, studs) | Wood | Stone | Copper | Iron | Silver | Cobalt | Mithril | Adamantine |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Wall (8 × 8 × 1) | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 |
| Floor (8 × 1 × 8) | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 |
| Door (4 × 8 × 1) | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 |
| Roof (8 × 1 × 8, a flat slab today) | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 |

| Single piece | Use | Status | Notes |
| --- | --- | --- | --- |
| Chest (4 × 3 × 3) | 20-slot public storage | ✅ | Lobby-set chest (sheet 03); resize to the piece box |
| Workbench (5 × 3 × 3) | Crafting station; also a placeable item | ✅ | Lobby `CraftingWorkbench` |
| Furnace (4 × 5 × 4) | Smelts ore into bars | ✅ | Lobby `SmeltingFurnace` |
| Anvil (4 × 3 × 3) | Silver-and-up and Jade gear | ✅ | Lobby anvil (sheet 03 has a small and a large one) |
| Bed (4 × 2 × 7) | Furniture (never a respawn point, GDD §6) | 🟨 | The 064 tent's bedroll is a start |
| Cauldron (4 × 3 × 4) | Potions and draughts | 🟨 | |
| Spike trap (4 × 1 × 4) | Hurts other tribes | 🟨 | |
| Planter (4 × 1.5 × 4) | Grows crops | 🟨 | |
| Totem, levels 1–3 (3 × 8 × 3) | Stops decay in a 15 / 35 / 70-stud radius | 🟨 | Three looks needed; the lobby Elder's totem shows the style |

| Crop in a planter | Status | Notes |
| --- | --- | --- |
| Redberry | 🟨 | One green part today; needs growing and ripe stages |
| Sweetberry | 🟨 | Same |
| Herbs | 🟨 | Same |
| Sapling (grows Wood) | 🟨 | Same |
| Fiber | 🟨 | Same |

### 1.14 Extraction sites (3)

| Asset | Status | Notes |
| --- | --- | --- |
| Portal site (6 fixed sites + the hidden Sunken Shrine) | 🟨 | `PropModels.Portal`: a ring of low stones, 4 totem posts and a glowing disc |
| Center portal (Crater Heart, 2× materials) | 🟨 | Same recipe in orange; a distinct look would help it read as the bonus exit |
| Placed Portable Extraction Rune | ⬜ | Only the beacon column appears; there is no rune object |

---

## 2. Events, enemies and animals

**Animation key:** I idle, W walk, R run, A attack, H hit, D death. Today no creature has any animation: each is an invisible hitbox carrying a primitive model (`CreatureModels`) that slides and turns. Sizes are hitbox studs (width × height × length). An event's elite or alpha member is the same creature at 1.4× size, so it shares the model.

### 2.1 Regular wildlife (11)

Roams in small groups per zone (`WildlifeRules`). Drops scale with size: small animals give Raw Meat and some Hide; medium ones Meat, Hide and Bone; large ones plenty of each.

| Creature | Behaviour | Size class (hitbox) | Zones | Animations | Notes | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Wild Boar | Neutral | Medium (2.5 × 2.5 × 4) | Pinewood Wilds, Mosswick | I W R A H D | Tusks; may drop Redberries | 🟨 |
| Forest Stag | Passive | Medium (2 × 4 × 4.5) | Rimlands, Pinewood, Mosswick | I W R H D | Antlers | 🟨 |
| Grey Wolf | Hostile | Medium (2 × 2.5 × 4) | Timberwatch, Fallen Temple, Frostpeak | I W R A H D | Packs of 2–3 | 🟨 |
| Brown Bear | Neutral | Large (3.5 × 4.5 × 6) | Timberwatch, Emberhollow, Frostpeak | I W R A H D | | 🟨 |
| River Crocodile | Hostile | Medium (2.5 × 1.6 × 7) | Riverlands, Crater Lake | I W R A H D | Needs a top view; long body | 🟨 |
| Plains Bison | Neutral | Large (3.5 × 4.5 × 6.5) | Rimlands, Riverlands | I W R A H D | | 🟨 |
| Meadow Rabbit | Passive | Small (1 × 1 × 1.6) | Rimlands, Pinewood, Mosswick, Riverlands | I W(hop) R H D | | 🟨 |
| Island Dodo | Passive | Small (1.6 × 2.4 × 2) | Rimlands beaches, Pinewood | I W R H D | Bird rig | 🟨 |
| River Capybara | Passive | Small (1.8 × 1.8 × 3) | Riverlands, Crater Lake | I W R H D | | 🟨 |
| Highland Goat | Passive | Medium (1.8 × 2.6 × 3) | Frostpeak | I W R H D | | 🟨 |
| Forest Tapir | Passive | Medium (2.2 × 2.6 × 4.5) | Mosswick, Timberwatch | I W R H D | | 🟨 |

### 2.2 Event creatures (6)

Spawned by the event director (`EventCatalog` "Npc" category) and announced to the server. Elites and alphas also drop Dire Hide, Charged Core and Glow-Fur.

| Creature | Event rarity · behaviour | Size class (hitbox) | Where | Animations | Notes | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Woolly Mammoth | Uncommon · Neutral | Large (7 × 9 × 11) | Grassland | I W R A H D | Trunk chain; the biggest animal | 🟨 |
| Giant Ground Sloth | Rare · Passive | Large (5 × 7 × 7) | Clearing | I W R H D | Long forelimbs, big claws | 🟨 |
| Ancient Tortoise | Rare · Passive | Large (6 × 4 × 7) | Lakeshore | I W H D | Domed shell, moss patches | 🟨 |
| Iron-Tusk Boar (alpha) | Rare · Hostile | Large (3.5 × 3.5 × 5.6) | Inner Ring clearing, with 3 Wild Boars | I W R A H D | Elite; big tusks, red crest | 🟨 |
| Saber-Toothed Tiger | Epic · Hostile | Large (3.6 × 4.2 × 7.4) | Inner Ring jungle | I W R A H D | Elite | 🟨 |
| Stonehide Rhino | Epic · Neutral | Large (4 × 5 × 8) | Inner Ring rocky ground | I W R A(charge) H D | Elite; also drops Iron Ore | 🟨 |

### 2.3 Skeletons and wisps (3)

| Creature | Role · behaviour | Size (hitbox) | Where | Animations | Notes | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Skeleton Warrior | Regular + event · Hostile | Humanoid (2 × 5 × 1.5) | Fallen Temple; Skeleton Patrol event; Raider Camp and Warlord's Hold defenders | I W R A H D | Holds a sword; drops Stone, Bone, Copper and Iron Ore | 🟨 |
| Keep Skeleton | Regular · Hostile | Humanoid (2.2 × 5.5 × 1.6) | Shattered Keep | I W R A H D | Armoured variant (iron shoulder plates); can share the Skeleton rig; also drops Silver Ore | 🟨 |
| Ember Wisp | Regular + Legendary event · Hostile | Small (2 × 2 × 2) | Emberhollow Caves | I (float) W A H D | Glowing core, flame tongues; 5% Ancient Ember | 🟨 |

### 2.4 Bosses (6 + 2 Guardian parts)

From `BossCatalog`. Attacks: **Slam** (melee), **Bolt** (slow projectile), **Quake** (telegraphed area). Every boss needs I W, an animation per attack (with a readable wind-up), H and D.

| Boss | Source | Size (hitbox) | Attacks | Look today (placeholder) | Drops | Status |
| --- | --- | --- | --- | --- | --- | --- |
| The Guardian | Own 15–20 min cycle, Keep courtyard | 10 × 18 × 8 | Slam, Bolt, Quake | Stone golem with glowing runes | Guardian's Fang at 25% HP; Guardian Heart, elite materials, Adamantine Ore | 🟨 |
| Crater Gorilla | Epic event, Inner Ring clearing | 7 × 9 × 6 | Slam, Bolt, Quake | Dark silverback with ember cracks | Meat, hide, bone, elite materials, Silver and Cobalt Ore | 🟨 |
| Ironhide Behemoth | Epic event, Inner Ring | 8 × 9 × 12 | Slam, Quake | Armoured horned beast | Hide, Iron Ore, Ancient Ember | 🟨 |
| Bone Colossus | Legendary event, anywhere | 7 × 16 × 5 | Slam, Bolt, Quake | Giant skeleton, ember in its ribcage | Iron Ore, Ancient Ember | 🟨 |
| Minotaur | Ritual at the Keep altars | 5.6 × 11.2 × 4.2 | Slam, Quake | Bull-headed brute with an axe | Silver and Cobalt Ore, Ancient Ember, elite materials, 5% Portable Extraction Rune | 🟨 |
| Raider Warlord | Warlord's Hold structure event | 4 × 7 × 3 | Slam, Bolt | Armoured human, red tabard, cape, sword | Iron Ore, Healing Potions | 🟨 |
| Guardian energy pillar (× 4, 1,500 HP each) | Guardian phase I | Column | Destroyed to drop the shield | Stone column, rune bands, crystal top | — | 🟨 |
| Guardian shield bubble | Guardian phase I | Shell round the boss | — | Translucent ball | — | 🟨 |

### 2.5 Lobby NPCs (6)

The lobby map already has `LobbyNPCSpot` markers for 9 roles, but no characters stand on them. Suggested: build them on the R6 survivor body (section 3.6) with outfit and prop variants.

| Role | Spots | Station | Status |
| --- | --- | --- | --- |
| Greeter | 1 | Arrival stones | ⬜ |
| Elder | 1 | Elder's totem (rebirth, boards) | ⬜ |
| Quest giver | 1 | Quest board | ⬜ |
| Vault keeper | 1 | Vault Hall | ⬜ |
| Blacksmith | 1 | Ancestral Forge | ⬜ |
| Merchant | 4 | Market stalls (one model, 4 outfits) | ⬜ |

### 2.6 Event set-pieces (24)

From `EventCatalog`. Rare event nodes pay out once and never regrow. Their placeholders (`PropModels`) are lit in the event's rarity colour. "Art to use" for the ⬜/🟨 rows is a proposed match for the owner to confirm.

**Vegetation events**

| Event (rarity) | Placeholder | Art to use | Status |
| --- | --- | --- | --- |
| Wild Herb Patch (Common) | Herb patch | 018 Healing herb, clustered | ✅ |
| Bloodberry Thicket (Uncommon) | Berry patch | 017 Berry bush, clustered | ✅ |
| Ironbark Sapling (Rare) | Sapling | 140 Silverbark tree | 🟨 |
| Wildbloom Shrub (Rare) | Bloom | 136 Heartpod bramble | 🟨 |
| Ancient Wildbloom (Epic) | Bloom | 139 Sunburst bloom | 🟨 |
| Emberbloom (Epic) | Bloom | 025 Emberbloom | ✅ |
| Elder Ironwood (Legendary) | Sapling | 138 Goldencrown tree | 🟨 |
| Starfall Lotus (Secret) | Bloom | No matching sheet; 118 Water lily with 133 Moonveil orchid's glow | 🟨 |
| Spare rare-flora sheet: Stormreed | — | 135, no event uses it yet | ⬜ |
| Spare rare-flora sheet: Giant coil fern | — | 141, no event uses it yet | ⬜ |
| Spare rare-flora sheet: Resinheart stump | — | 142, no event uses it yet | ⬜ |

**Ore events** (rock with crystals in the rarity colour today)

| Event (rarity) | Gives | Art to use | Status |
| --- | --- | --- | --- |
| Surface Stone Vein (Common) | Stone, Flint | 001 + 002 cluster | ✅ |
| Iron Outcrop (Uncommon) | Iron and Copper Ore | 003 + 006 cluster | ✅ |
| Rich Cobalt Lode (Rare) | Cobalt and Silver Ore | No art (see the Cobalt node) | 🟨 |
| Ember-Veined Rock (Epic) | Mithril Ore, Ancient Ember | No art | 🟨 |
| Heartstone Seam (Mythic) | Mithril and Adamantine Ore | No art; the rarest seam deserves its own look | 🟨 |

**Caches, meteors and structures**

| Set-piece | Used by | Placeholder | Art to use | Status |
| --- | --- | --- | --- | --- |
| Supply cache chest, closed and open, 4 rarity trims | Weathered, Ancient, Gilded and Elder caches; Fort, Camp and Hold events | Wood chest with bands, a lid that swings open, a gem that goes out | 144 Event cache (and 143 plinth) | 🟨 |
| Loot pile (search spot) | Crumbling Ruins | Rubble heap, smashed crate, hide scrap | — | 🟨 |
| Meteor rock | Meteor Crash (Rare), Great Meteor (Legendary) | Scorched rock with glowing cracks | 009 Iron meteor, 015 Ember meteor | ✅ |
| Meteor chunks × 8 (30 s to break, Mithril pickaxe) | Same | Plain cracked-lava cubes | 009's shell pieces are a base | 🟨 |
| Crater floor and rubble rim | Same | Scorched floor, rubble ring | — | 🟨 |
| Ruin walls (10-segment ring), gate and dressing | Crumbling Ruins | Crumbling stone walls, cracked arch, broken columns, rubble | 089–091 | 🟨 |
| Fort walls, gate and dressing | Abandoned Fort, Warlord's Hold | Sharpened-log walls, gate posts with banners, watch platform, spear rack, crates | 069 (done), 072, 076, 146 | 🟨 |
| Camp walls, gate and dressing | Raider Camp | Hide screens, skull poles, 3 hide tents, fire pit, log seats | 064 (done), 074, 146 | 🟨 |

---

## 3. Physical gear

The game generates gear from the tier ladder (`Tiers.Ladder`, `ItemCatalog`): each material makes only some families. `GearModels` already draws every item from one builder per family, tinted by tier, so the final art can work the same way.

**Suggested sharing:** per weapon and tool family, one "primitive" shape (a wood, stone, bone, flint, obsidian or jade head lashed to wood) and one "forged" shape for the six metals, told apart by material, colour and trim. That is about **12 meshes for 53 weapons and tools**, plus **9 armor meshes** (leather, bone and metal styles × 3 slots) for 24 armor pieces, plus the Guardian's Fang.

The ✅ cells below are the sheet-04 Blender models (`art/blender/assets/04_weapons_tools.blend`), built for the lobby display racks. They are not used in hand yet, and should be checked against the world kit's quality bar before being swapped in.

### 3.1 Weapons and tools (54)

| Family | Wood | Stone | Bone | Flint | Copper | Iron | Obsidian | Silver | Cobalt | Jade | Mithril | Adamantine |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Spear | ✅ | ✅ | 🟨 | 🟨 | 🟨 | ✅ | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 |
| Dagger | — | ✅ | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 |
| Sword | — | 🟨 | — | — | 🟨 | ✅ | — | 🟨 | 🟨 | — | 🟨 | 🟨 |
| Bow | ✅ | — | — | — | 🟨 | 🟨 | — | 🟨 | 🟨 | — | 🟨 | 🟨 |
| Axe | 🟨 | ✅ | — | — | 🟨 | ✅ | — | 🟨 | 🟨 | — | 🟨 | 🟨 |
| Pickaxe | 🟨 | ✅ | — | — | 🟨 | ✅ | — | 🟨 | 🟨 | — | 🟨 | 🟨 |

| Unique weapon | Status | Notes |
| --- | --- | --- |
| Guardian's Fang (Legendary sword, one tier above Adamantine) | 🟨 | Ivory blade with ember veins today; needs its own hero model |

Sheet 04 models: wooden, stone and iron spear; stone knife (the Stone Dagger); iron short sword; simple wooden bow; basic stone axe and iron axe; double stone pickaxe and iron pickaxe. Sheet 04 also has a broad-head stone axe and a laminated bow that could serve as variants.

### 3.2 Armor (24)

Worn on the R6 body: the head piece on the Head, the chest piece on the Torso with a pauldron on each arm, the legs piece as a greave on each leg.

| Slot | Hide | Bone | Copper | Iron | Silver | Cobalt | Mithril | Adamantine |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Head | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 |
| Chest (torso + 2 pauldrons) | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 |
| Legs / boots (2 greaves) | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 | 🟨 |

### 3.3 Ammo, siege items and placeables (8)

| Item | Status | Notes |
| --- | --- | --- |
| Flint Arrow, held (bundle in the bow hand) | 🟨 | |
| Arrow in flight | ✅ | Sheet-04 `StoneArrow`; the game flies a thin brown stick |
| Fire Bomb, held | 🟨 | |
| Fire Bomb, thrown (slow visible arc) | 🟨 | A plain ball |
| Breaching Charge, held | 🟨 | |
| Breaching Charge, set on a wall or door (8 s fuse) | 🟨 | Red box with stock fire, a light and a countdown label |
| Workbench, held as an item | 🟨 | A crate; once placed it is the Workbench piece (1.13) |
| Portable Extraction Rune, held (Legendary) | 🟨 | A crate; the placed rune is in 1.14 |

### 3.4 Consumables in hand (14)

Used from the hand with a timed animation (`Consumables`, `ConsumeRules`). Today there are three generic shapes: a red flask for medicine, a purple flask for draughts and a brown pouch for food. Suggested sharing: one flask in several liquid colours, one handful-of-berries in four tints, plus medicine wraps and a meat shape.

| Item (rarity) | Kind | Status |
| --- | --- | --- |
| Basic Medicine | Medicine (0.5 s) | 🟨 |
| Advanced Medicine | Medicine (1 s) | 🟨 |
| Healing Potion | Medicine (1.5 s) | 🟨 |
| Greater Healing Potion (Uncommon) | Medicine | 🟨 |
| Redberry | Food | 🟨 |
| Sweetberry | Food | 🟨 |
| Sunberry (Rare) | Food + boost | 🟨 |
| Glimmerberry (Rare) | Food + boost | 🟨 |
| Cooked Meat | Food | 🟨 |
| Hearty Tonic (Uncommon) | Food | 🟨 |
| Sunberry Draught (Uncommon) | Boost | 🟨 |
| Strong Sunberry Draught (Rare) | Boost | 🟨 |
| Glimmer Draught (Uncommon) | Boost | 🟨 |
| Strong Glimmer Draught (Rare) | Boost | 🟨 |

Materials (Wood, ores, bars, rare materials and so on) have no held model by design: they live in the backpack and show as inventory icons. There are no worn backpacks or accessories in the game.

### 3.5 Containers, drops and bodies (3)

| Asset | Status | Notes |
| --- | --- | --- |
| Dropped item on the ground | 🟨 | Gear lies as a small model of itself; materials and consumables show a plain tan box. Suggested: a small sack or per-material chunk |
| Gathered material pickups (from node hits) | 🟨 | A 1-stud cube in the material's colour |
| Lootable body (600 s after a death or departure) | 🟨 | A plain brown slab |

Storage chests, cache chests and loot piles are in 1.13 and 2.6.

### 3.6 Player character and animations (8)

The character is the one place in a run that already uses final art. Animations are listed here because the gear needs them.

| Asset | Status | Notes |
| --- | --- | --- |
| R6 survivor: body, face, shirt, pants in 10 colourways | ✅ | `art/roblox/character` |
| Attack and gather swing, hold pose | 🟨 | One stock Roblox swing and one stock hold for every weapon and tool |
| Per-family attacks: spear thrust, dagger stab, sword slash | ⬜ | |
| Bow draw and release | ⬜ | |
| Axe chop, pickaxe swing | ⬜ | |
| Drink medicine (0.5 / 1 / 1.5 s) and eat | ⬜ | The timings already exist in `GameConstants` |
| Throw (Fire Bomb), set charge, build | ⬜ | |
| Downed crawl, revive, extraction departure | ⬜ | |

---

## 4. Visual effects

**What exists:** the lobby's effects are live (fire, sparks, embers, smoke, waterfall mist and splash, foam, dust, rune motes, flickering lights). `art/vfx/` holds 13 particle textures and 20 emitter kinds, and the world-kit models carry `VFX_<kind>` sockets with full specs. The play world has no particle emitters yet: its few effects are Neon parts, ForceField discs, Highlights and stock Roblox Fire and Explosion.

### 4.1 Rarity and loot (12)

Item colours come from `Rarity.Colors`. Design guidance: GDD §36.5 wants rare loot to stay visible, and `visuals.md` §9 warns against making every item glow. Suggested scale: nothing for Common, rising from a faint glint to a tall beam at Legendary, on dropped items first and held items only from Epic up.

| Rarity / case | Items in the game today | Status | Now / suggested |
| --- | --- | --- | --- |
| Common (grey) | Most materials; Wood, Stone, Hide, Bone, Flint, Copper and Iron gear | — | No effect wanted |
| Uncommon (green) | Obsidian, Silver and Cobalt gear, ores and bars; Amethyst, Dire Hide, Greater Healing Potion, Hearty Tonic, the two plain draughts | ⬜ | Suggested: faint glint on the drop |
| Rare (blue) | Jade and Mithril gear; Starstone, Stormglass, Charged Core, Glow-Fur, Ashen Oil, Siege Resin, Bloodroot, Moonpetal, Sunberry, Glimmerberry, the two strong draughts, Fire Bomb, Breaching Charge | ⬜ | Suggested: glint and a small coloured light |
| Epic (purple) | Adamantine gear, ore and bar; Abyssal Shard, Emberglass, Ancient Ember | ⬜ | Suggested: short light pillar on the drop, sparkle on a held weapon |
| Legendary (gold) | Guardian's Fang, Guardian Heart, Portable Extraction Rune | 🟨 | Only the Fang's carrier gets a gold Highlight. Suggested: tall beam on the drop, carrier glow for every Legendary |
| Mythic (red) | Only the Heartstone Seam ore event | 🟨 | Event props lit in the rarity colour |
| Secret (teal) | Only the Starfall Lotus event | 🟨 | Same |
| Exclusive (pink) | Nothing uses it yet | — | |
| Rare event props (nodes, ore crystals, cache gem) | All event rarities | 🟨 | Neon accents in the rarity colour |
| Permanent item on the ground | Any Permanent gear | 🟨 | A gold Neon box round the drop |
| Permanent item held or worn | Any Permanent gear | ⬜ | Suggested: a subtle mark so others know it will not drop |
| Permanent conversion at the Eternal Anvil (lobby) | — | ⬜ | Suggested |

### 4.2 Events, bosses and the Guardian (21)

| Effect | Ref / spec | Status | Now |
| --- | --- | --- | --- |
| Meteor descent trail | 163 | ⬜ | The meteor just appears |
| Meteor impact burst | 165 | ⬜ | |
| Meteor site heat, cracks and embers | 167; `heat_glow` and `embers` sockets on 009 and 015 | 🔨 | One orange PointLight and Neon cracks |
| Cache beacon and sparkles (while waiting) | 168 | ⬜ | |
| Cache opening (after the 60 s channel) | — | 🟨 | The lid swings open and the gem goes out; suggested: a burst as the loot spills |
| Rare flora bloom | 166 | ⬜ | |
| Crystal idle glint | 162; `ore_glint`, `crystal_glow`, `crystal_halo` sockets on the gem models | 🔨 | |
| Frost bloom and snow drift | 169 | ⬜ | Frostpeak, Frost shrub |
| Event location marker in the world | — | ⬜ | Suggested: events are announced in the HUD only |
| Ritual altar glow (idle and active colours) | — | 🟨 | Neon parts change colour |
| Ritual summon (10 s) and boss arrival | — | ⬜ | |
| Guardian awakening dust and runes | 170 | ⬜ | The Horn of War is a sound only |
| Guardian shield bubble | — | 🟨 | Translucent ball |
| Guardian pillar runes | — | 🟨 | Neon bands |
| Pillar destroyed, shield breaks | — | ⬜ | |
| Legendary released at 25% HP | — | ⬜ | |
| Boss Quake telegraph | — | 🟨 | Red Neon disc, then damage |
| Boss Bolt projectile | — | 🟨 | Neon ball in the boss's colour |
| Boss Slam impact | — | ⬜ | |
| Boss spawn and death | — | ⬜ | |
| Ember Wisp glow and flames | — | 🟨 | Neon core in the placeholder model |

### 4.3 Combat (9)

| Effect | Status | Now / notes |
| --- | --- | --- |
| Damage numbers | ✅ | `DamageNumbers` |
| Overhead health bars and names | ✅ | `OverheadHealth` |
| Melee hit impact (on players and creatures) | ⬜ | |
| Hit flash on the target | ⬜ | |
| Arrow trail | ⬜ | The GDD wants slow, visible arrows |
| Creature death | ⬜ | The body just disappears |
| Downed player marker in the world | ⬜ | Suggested: the downed state is a HUD card only |
| Revive in progress and revived | ⬜ | |
| Elite / alpha creature tell | ⬜ | Suggested: alphas are only 1.4× larger |

### 4.4 Survival (5)

| Effect | Status | Now / notes |
| --- | --- | --- |
| Use progress (drink, eat) | ✅ | HUD bar (`ConsumeController`) |
| Medicine heal burst | ⬜ | Suggested |
| Food heal-over-time (10 s) | ⬜ | Suggested |
| Boost active (XP or Luck) | ⬜ | HUD icon exists; suggested: a faint aura |
| Level-up and mastery milestone | ⬜ | Suggested |

### 4.5 Building and raids (12)

| Effect | Status | Now / notes |
| --- | --- | --- |
| Build ghost (green OK, red refused) | 🟨 | Tinted copy of the piece |
| No-build auras and totem radius while building | 🟨 | ForceField discs |
| Piece placed | ⬜ | Suggested |
| Structure hit / damaged | ⬜ | |
| Structure destroyed | ⬜ | The piece just disappears |
| Decay countdown (out of totem cover, 240–360 s) | ⬜ | Nothing shows a piece is about to be removed |
| Totem placed / upgraded | ⬜ | Suggested |
| Fire Bomb burst | 🟨 | Expanding orange Neon ball |
| Breaching Charge fuse | 🟨 | Stock Roblox Fire and a light |
| Breaching Charge blast | 🟨 | Stock Roblox Explosion and a flash |
| Spike trap triggers | ⬜ | |
| Crop ripe in a planter | ⬜ | Suggested |

### 4.6 Gathering (7)

| Effect | Ref / spec | Status | Now / notes |
| --- | --- | --- | --- |
| Node hover outline | — | ✅ | Highlight in the UI kit's colours |
| Hit chips and splinters per material | 164; `harvest_hit` kind, `rock_chip` texture | 🔨 | Spec exists; no sockets placed on the exported models yet |
| Node depletes | `harvest_deplete` kind | 🔨 | Same |
| Harvest leaves and pollen (plants) | 172 | ⬜ | |
| Resin drip and amber glint | 171 | ⬜ | |
| Node regrows | — | ⬜ | Suggested |
| Material drop pop and pickup | — | ⬜ | Suggested |

### 4.7 Extraction (6)

| Effect | Status | Now / notes |
| --- | --- | --- |
| Portal site idle glow | 🔨 | A Neon disc now; the `rune_glow` kind is already live on the lobby rune stones |
| Extraction beacon (countdown started) | 🟨 | A 400-stud Neon column with a light |
| Extraction zone ring | 🟨 | A ForceField disc |
| Extraction departure (3 s protected transition) | ⬜ | Confirmed in GDD §22.2; nothing shows it |
| Portable rune activation | ⬜ | |
| Arrival in the lobby | ⬜ | Suggested |

### 4.8 Environment (15)

| Effect | Ref / spec | Status | Now / notes |
| --- | --- | --- | --- |
| Torch fire | `torch_fire` | ✅ | Live in the lobby |
| Campfire (flame, sparks, smoke) | `campfire` | ✅ | Live in the lobby |
| Brazier fire and embers | `brazier_fire`, `embers` | ✅ | Live in the lobby |
| Forge fire, heat shimmer, glyph glow | `forge_fire`, `heat_glow`, `glyph_glow` | ✅ | Live in the lobby |
| Fire flicker lights | `LightFlickerController` | ✅ | Steady under Reduced Motion |
| Waterfall curtain, mist and splash | `waterfall_curtain`, `waterfall_mist`; 159 | ✅ | Live in the lobby; 159 is a polish study |
| Dust motes | `dust` | ✅ | Live in the lobby |
| Rune glow motes | `rune_glow` | ✅ | Live in the lobby |
| Chimney smoke | `chimney_smoke` | 🔨 | Spec and texture only |
| River flow | 160; `water_flow` sockets on the kit water models | 🔨 | |
| Shore and stream foam | 161; `water_foam` sockets | 🔨 | |
| Lantern halos (tent, shelter) | `heat_glow` sockets on 064 and 066 | 🔨 | |
| Fire pits in world camps | — | 🟨 | Neon flame and a PointLight; swap in the campfire effect |
| Smoke plume | 158 | ⬜ | |
| Flame and embers upgrade | 156 | ⬜ | A study for a better flame than the current flipbook |

The game has no weather or day/night cycle, so no effects are listed for them.
