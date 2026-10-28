# Flintborn item and material catalog — draft for owner review

> **Status:** Approved by the owner on 2026-10-27 (GDD §51) and being implemented. Names are kept for now. Numbers marked *placeholder* are starting values for playtests. The data lives in `src/shared/Items/Tiers.luau`, `ItemCatalog.luau`, `Consumables.luau`, `src/shared/Crafting/Recipes.luau` and `ForgeRecipes.luau`.

## 1. Owner decisions this catalog follows

| Topic | Decision |
| --- | --- |
| Material list | Expand to the GDD §18.1 families. |
| Gear ladder | Wood → Stone → Copper → Iron → Silver → Cobalt → Mithril → Adamantine, extendable later. Cobalt replaced Emerald so the ladder is all metal. |
| Weapon families | Spear, dagger, sword and bow only. |
| Restricted (gem-class) materials | Jade, Obsidian, Flint and any future gemstone make **only daggers and spears**, plus Forge and Permanent inputs. **Flint is the only arrow tip.** Strength is staggered: Flint sits between Stone and Copper, Obsidian between Iron and Silver, Jade between Cobalt and Mithril. |
| Ores | Smelted into bars at the Furnace, **1 ore → 1 bar, no fuel**; time is the only cost. Crafting mastery adds a chance of one bonus bar per bar (2% per level, 2026-10-28). |
| Mining gate | Each ore needs a pickaxe of the previous tier. |
| Ore regions | By danger: Outer Rim has Stone, Copper and Iron; Inner Ring has Silver and Cobalt; the Crater has Mithril; Adamantine comes only from meteors, the Guardian and rare events. |
| Armor ladder | Hide → Bone → Copper → Iron → Silver → Cobalt → Mithril → Adamantine. Wood and Stone armor are removed. |
| Tools | Axes and pickaxes at every tier, Wood first. **Sickles are removed**; Fiber, Herbs and berries are gathered by hand at today's sickle rate. |
| Bows | Wooden Bow, then a metal-reinforced bow for each metal tier. |
| Bone | Bone armor, Bone daggers and Bone spears. |
| Stations | Wood, Stone, Flint and Bone gear by hand. Copper, Iron and Obsidian at the Workbench. Silver and up, and Jade, at a new **Anvil**. Smelting and cooking at the Furnace. Potions at a new **Cauldron**. |
| Tier strength | About 25% stronger per tier, compounding. |
| Rarity | Rises slowly with tier; Legendary and above are reserved for boss and event drops. |
| Quality rolls | Keep ±5% (Q139). |
| Components | No intermediates besides metal bars. Recipes use Wood, Fiber and Hide directly. |
| Consumables | Keep Basic Medicine, Advanced Medicine, Healing Potion and Cooked Meat. Berries come in varieties with different effects (healing, fullness, XP boost, luck boost), and brewing them at the Cauldron gives a stronger effect. A running boost never weakens: only a stronger one of the same kind takes over (2026-10-28). |
| Luck | Raises rare-drop chance only, from creatures, caches and events. |
| XP potions | Add to Premium and paid boosters, as with Q162. |
| Building | Full ladder: Wood through Adamantine walls, floors, doors and roofs. |
| Permanent | Any gear can be converted; the cost scales with tier. |
| Rare materials | Used for Permanent conversions, Mithril and Adamantine gear, and siege items. |
| Siege items | Fire Bomb (Ashen Oil) and Breaching Charge (Siege Resin). |
| Rare groups | Elite creatures, **including the Guardian**; ancient caches; meteor crashes; and a new **rare shrub event** that grows rare berries and rare herbs. Rare herbs also appear in crafting recipes. |
| Ancient Ember | Kept as the rare event reagent. |
| Trading | Elite and Guardian materials, meteor and cache materials, and rare berries and herbs may be traded. Common materials, ores and bars may not. |
| Shop | Starter supplies only: Wood and Stone tools, Flint Arrows, basic medicine and common berries. |
| Removed items in existing saves | Deleted (pre-launch). |

## 2. Materials

Extracted materials bank into the vault. Since 2026-10-28 (GDD §53) they can be withdrawn into the lobby backpack and carried into a run again, but the carried-in amount never gets the Center 2× or any other extraction multiplier.

Gathering (GDD §53): every hit drops material on the ground. Only the gatherer can pick it up for 10 s, then anyone can, and it disappears after 2 minutes. Walking over it or pressing Interact collects it.

### 2.1 Common (every region unless noted)

| Material | Source | Notes |
| --- | --- | --- |
| Wood | Trees (hand or axe) | Building, hafts, bows. |
| Stone | Rocks (hand or pickaxe) | Stone tier, building, stations. |
| Flint | Rocks: a 15% chance per hit of an extra drop, plus 1 when a rock is finished *(placeholder)* | Restricted: daggers, spears, arrow tips. |
| Plant Fiber | Fiber plants (hand) | Bindings in most recipes. |
| Herbs | Herb shrubs (hand) | Medicine. |
| Resin | Trees: a 10% chance per hit of an extra drop *(placeholder)* | Binding agent in Silver+ recipes and the Fire Bomb. |
| Hide | Hunted creatures | Hide armor; straps in metal armor. |
| Raw Meat | Hunted creatures | Cooked at the Furnace. |
| Bone | Hunted creatures | Bone armor, daggers and spears. |

### 2.2 Ores and bars

| Ore | Region | Pickaxe needed | Bar (Furnace, 1:1) | Smelt time *(placeholder)* |
| --- | --- | --- | --- | --- |
| Copper Ore | Outer Rim | Stone | Copper Bar | 2 s |
| Iron Ore | Outer Rim | Copper | Iron Bar | 3 s |
| Silver Ore | Inner Ring | Iron | Silver Bar | 4 s |
| Cobalt Ore | Inner Ring | Silver | Cobalt Bar | 5 s |
| Mithril Ore | Crater | Cobalt | Mithril Bar | 6 s |
| Adamantine Ore | Meteors, the Guardian, rare events | Mithril | Adamantine Bar | 8 s |

### 2.3 Restricted (gem-class) materials — daggers and spears only

| Material | Region | Pickaxe needed | Strength slot |
| --- | --- | --- | --- |
| Flint | Outer Rim (from rocks) | Hand | Between Stone and Copper; also arrow tips |
| Obsidian | Inner Ring outcrops | Iron | Between Iron and Silver |
| Jade | Inner Ring veins | Cobalt | Between Cobalt and Mithril |

### 2.4 Rare and endgame materials (tradeable)

| Group | Material | Source | Used for |
| --- | --- | --- | --- |
| Elite | Dire Hide | Elite creatures | Mithril and Adamantine armor |
| Elite | Charged Core | Alpha creatures and their packs | Mithril and Adamantine weapons; Permanent conversions |
| Elite | Glow-Fur | Alpha creatures and their packs | Mithril and Adamantine armor; Permanent conversions |
| Elite (Guardian) | Guardian Heart | The Crater Guardian only, with large amounts of Charged Core and Glow-Fur, Adamantine Ore and the mid-fight Legendary | Adamantine and Guardian's Fang Permanent conversions |
| Cache | Ashen Oil | Ancient caches | Fire Bomb |
| Cache | Siege Resin | Ancient caches | Breaching Charge |
| Meteor | Abyssal Shard | Meteor crashes | Adamantine weapons; Permanent conversions |
| Meteor | Emberglass | Meteor crashes | Adamantine armor; Permanent conversions |
| Event | Ancient Ember | Rare events (as today) | Forge and Permanent reagent (tradeable, as today) |

### 2.4a Gatherables with no use yet (GDD §53)

Bankable and sellable, not tradeable. Uses come later.

| Material | Node | Where | Needs |
| --- | --- | --- | --- |
| Clay | Clay deposit | Beach, woodland | Hand or any pickaxe |
| Amethyst (Uncommon) | Amethyst geode | Medium regions | Iron pickaxe |
| Starstone, Stormglass (Rare) | Outcrop, cluster | Extreme regions | Cobalt pickaxe |
| Cave, Redcap and Chestnut Mushroom | Mushroom patches | Forests and jungle | Hand |
| Thornvine, Frostleaf, Juniper Berry, Elderberry, Raspberry, Hazelnut | Thorn, Frost, Juniper, Elderberry, Hazel shrubs and Raspberry bush | Spread by habitat (Frost shrubs on high ground) | Hand |

### 2.5 Rare shrub event (new)

A rare shrub sprouts somewhere on the island as an announced event. Gathering it by hand gives rare berries and rare herbs. It is weighted like other rare events. **Every rare event type rolls on its own** (owner decision): it never competes with other events of its category or rarity.

| Rare herb (tradeable) | Use |
| --- | --- |
| Bloodroot | Healing Potion upgrade (stronger heal) and the haft wraps in Mithril and Adamantine weapons |
| Moonpetal | Strengthens and extends the XP and luck draughts; a Permanent conversion input for Cobalt-tier gear and above |

## 3. Food, berries and potions

Berries are food, not materials, so they can be carried into a run.

| Berry | Where | Eaten raw | Brewed at the Cauldron |
| --- | --- | --- | --- |
| Redberry (today's Berries) | Common bushes, planters | Heals 10 over 10 s; +10% food | **Healing Potion**: Redberry ×5 + Herbs ×5 → heals 50 at once (today's potion values) |
| Sweetberry | Common bushes, planters | +25% food, no heal | **Hearty Tonic**: Sweetberry ×6 → +60% food |
| Sunberry (rare shrub) | Rare shrub event | +10% XP for 3 min | **Sunberry Draught**: Sunberry ×3 + Herbs ×2 → +25% XP for 10 min (Moonpetal makes it 15 min) |
| Glimmerberry (rare shrub) | Rare shrub event | +5% rare-drop chance for 3 min | **Glimmer Draught**: Glimmerberry ×3 + Herbs ×2 → +15% rare-drop chance for 10 min (Moonpetal makes it 15 min) |

- Medicine is unchanged: Basic Medicine (heal 10) and Advanced Medicine (heal 25).
- Cooked Meat is unchanged (Raw Meat at the Furnace).
- Boosts don't stack. A running boost never weakens or resets: a weaker or equal one changes nothing (a draught is refused and kept), and only a stronger one takes over with its own timer (2026-10-28). XP boosts add to Premium and paid boosters.
- Effect sizes and durations are placeholders.

## 4. Gear by tier

Strength multiplies by about 1.25 per tier from Stone, keeping the GDD's confirmed values (wooden spear 15, stone spear 25, Q66). Rarity rises slowly. Recipes take bars plus Wood, Fiber or Hide; Mithril and Adamantine also need rare materials.

### 4.1 What each material makes

| Tier | Rarity | Station | Spear | Dagger | Sword | Bow | Axe/Pickaxe | Armor (3 pieces) | Building |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Wood | Common | Hand | ✓ | — | — | Wooden Bow | ✓ | — | ✓ |
| Hide | Common | Hand | — | — | — | — | — | ✓ | — |
| Stone | Common | Hand | ✓ | ✓ | ✓ | — | ✓ | — | ✓ |
| Flint | Common | Hand | ✓ | ✓ | — | arrow tips | — | — | — |
| Bone | Common | Hand | ✓ | ✓ | — | — | — | ✓ | — |
| Copper | Common | Workbench | ✓ | ✓ | ✓ | Copper Bow | ✓ | ✓ | ✓ |
| Iron | Common | Workbench | ✓ | ✓ | ✓ | Iron Bow | ✓ | ✓ | ✓ |
| Obsidian | Uncommon | Workbench | ✓ | ✓ | — | — | — | — | — |
| Silver | Uncommon | Anvil | ✓ | ✓ | ✓ | Silver Bow | ✓ | ✓ | ✓ |
| Cobalt | Uncommon | Anvil | ✓ | ✓ | ✓ | Cobalt Bow | ✓ | ✓ | ✓ |
| Jade | Rare | Anvil | ✓ | ✓ | — | — | — | — | — |
| Mithril | Rare | Anvil | ✓ | ✓ | ✓ | Mithril Bow | ✓ | ✓ | ✓ |
| Adamantine | Epic | Anvil | ✓ | ✓ | ✓ | Adamantine Bow | ✓ | ✓ | ✓ |

Legendary and above stay reserved for boss and event drops, such as the Guardian's Fang.

### 4.2 Weapon damage *(placeholder, about 1.25× per tier)*

| Tier | Spear (0.9 s) | Sword (0.7 s) | Dagger (0.4 s) | Bow (+ Flint Arrow 6) |
| --- | --- | --- | --- | --- |
| Wood | 15 | — | — | 6 |
| Stone | 25 | 18 | 9 | — |
| Flint | 28 | — | 10 | — |
| Bone | 27 | — | 10 | — |
| Copper | 31 | 23 | 11 | 8 |
| Iron | 39 | 28 | 14 | 9 |
| Obsidian | 44 | — | 16 | — |
| Silver | 49 | 35 | 18 | 12 |
| Cobalt | 61 | 44 | 22 | 15 |
| Jade | 68 | — | 25 | — |
| Mithril | 76 | 55 | 27 | 18 |
| Adamantine | 95 | 69 | 34 | 23 |

Bow damage is the bow's damage plus 6 for the Flint Arrow, unchanged by draw time (Q134). Flint Arrows: Wood ×3 + Flint ×1 + Fiber ×2 make 10.

### 4.3 Drops per hit and node health (GDD §53)

A hit drops **1 + one per tier the tool is above the node** and uses that much node health, so a better tool empties a node in fewer hits for the same total. Bare hands are rank 0: trees, rocks and Clay give 1 per hit by hand, 2 with a Wooden tool, 3 with Stone, and so on. An ore or gem node's rank is the pickaxe it needs (the previous tier's), which gives 1 per hit; each pickaxe tier above adds 1. Plants, bushes, mushrooms and shrubs give 1 per hit by hand. Gathering mastery adds a 1%-per-level chance of one extra drop per hit, without using node health.

| Node | Health *(placeholder)* | Regrows after |
| --- | --- | --- |
| Tree, Rock | 12 | 2 min |
| Fiber, Herbs, berry bushes | 3 | 2 min |
| Copper, Iron deposits | 8 | 3 min |
| Silver, Cobalt deposits | 8 | 5 min |
| Obsidian outcrop | 5 | 5 min |
| Jade vein | 5 | 8 min |
| Mithril deposit | 6 | 8 min |
| Clay, mushrooms, shrubs | 4 | 2 min |
| Amethyst geode | 4 | 5 min |
| Starstone, Stormglass | 4 | 8 min |

Adamantine only comes from meteors, the Guardian and rare events; rare event nodes never regrow.

### 4.4 Armor (owner decision: 25% compounding)

The confirmed anchors stay (Hide ×1.2, Iron ×2.0, Q134). Above Iron, each metal adds 25% compounding.

| Set | Hide | Bone | Copper | Iron | Silver | Cobalt | Mithril | Adamantine |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Full-set EHP factor | 1.2 | 1.5 | 1.8 | 2.0 | 2.5 | 3.13 | 3.91 | 4.88 |

### 4.5 Building HP per piece *(placeholder, 1.25× per tier after Stone)*

| Tier | Wood | Stone | Copper | Iron | Silver | Cobalt | Mithril | Adamantine |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Wall HP | 300 | 800 | 1,000 | 1,250 | 1,560 | 1,950 | 2,440 | 3,050 |

Floors, doors and roofs scale the same way from today's values; metal tiers cost that metal's bars. Iron walls drop from 1,600 to 1,250 HP so the curve stays even. Totem levels stay as they are, using Iron Bars at level 3.

## 5. Stations, siege items and placeables

| Item | Recipe *(placeholder)* | Purpose |
| --- | --- | --- |
| Workbench | Wood ×20, Stone ×10 (unchanged) | Copper, Iron and Obsidian gear |
| Furnace | Stone ×30, Wood ×10 (unchanged) | Smelting (1 ore → 1 bar) and cooking |
| **Anvil** (new) | Iron Bar ×20, Stone ×30 | Silver and up, and Jade gear |
| **Cauldron** (new) | Stone ×20, Copper Bar ×5 | Healing Potion, Hearty Tonic, draughts |
| **Fire Bomb** (new, consumable) | Ashen Oil ×1, Resin ×1, Fiber ×2 | Thrown; burns structures: Wood ×3 damage, Stone ×1, metal ×0.25 |
| **Breaching Charge** (new, placeable) | Siege Resin ×2, Iron Bar ×2, Fiber ×2 | Placed on a wall or door; 8 s fuse; heavy damage to that one piece |

The Portable Extraction Rune and the existing building pieces (chest, bed, trap, planter, totem) are unchanged. Planters grow Redberries, Sweetberries, Herbs, saplings and Fiber (GDD §53); saplings and Fiber share one prompt (tap to switch, hold to plant). Seeds that were carried into the run grow a harvest that counts as carried. Sunberries and Glimmerberries are wild-only.

## 6. Permanent conversions

Any weapon, tool or armor piece can become Permanent. Proposed cost: **10× its crafting recipe**, plus:

| Tier | Ancient Ember | Rare inputs |
| --- | --- | --- |
| Wood, Stone, Flint, Bone, Hide, Copper | 1 | — |
| Iron, Obsidian, Silver | 2 | — |
| Cobalt, Jade | 3 | Moonpetal ×2 |
| Mithril | 4 | Charged Core ×3 (weapons and tools) or Glow-Fur ×3 (armor) |
| Adamantine | 5 | Guardian Heart ×1 + Abyssal Shard ×3 (weapons) or Emberglass ×3 (armor) |

## 7. Shop (lobby)

- Wooden Axe, Wooden Pickaxe, Stone Axe and Stone Pickaxe.
- Flint Arrows ×10.
- Basic Medicine.
- Redberries and Sweetberries.
- Redberry and Sweetberry seeds.
- Titles, as today.

No metal, bars or higher gear.

## 8. Removed from the game (deleted from saves)

- Sickle.
- Wood armor and Stone armor.
- The plain Arrow, replaced by Flint Arrows.
- The "HerbSeeds" entry, already gone.

Also deleted (pre-release): the old "Iron" material, the Basic Pickaxe (now the Stone Pickaxe), the Basic Bow (now the Wooden Bow) and plain Berries (now Redberries). Existing Iron gear (Iron Sword, axe, pickaxe, armor) keeps its IDs and stays.

## 9. Owner answers (2026-10-27)

1. **Armor:** 25% compounding (§4.4).
2. **Guardian's Fang:** beats Adamantine: one tier above the Adamantine sword (86 damage), Legendary, Permanent-eligible.
3. **Names:** kept as drafted for now.
4. **Rare shrub:** same frequency as other rare events, and every rare event type is rolled individually.
5. **Iron already in vaults:** removed with the other legacy items (pre-release).
