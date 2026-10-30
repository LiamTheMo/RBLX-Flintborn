# Item art

Which art every catalog item (`ItemCatalog.Items`, generated gear, ores and bars
included) draws in slots, cards and the hotbar until it has art of its own. The
source is `ItemInfo.Icon(id) → (name, tint)` in `src/shared/Items/ItemInfo.luau`
(`ICONS`, `TINTS`, `EXACT`, `ART_SPRITES`); `Kit.ItemIcon` draws an item's own
`lk_item_<id>` / `item_<id>` sprite first when one exists, then this art, then the
item's name in ink.

- **exact**: the kit art depicts that very item.
- **stand-in**: the closest kit art, usually tinted. A tint is an `ImageColor3`
  multiply, so it darkens or shifts a hue; it cannot lighten. These items need
  real icon art.
- **none**: nothing in the kit reads as the item; the slot shows the item's name.

Totals: 144 items, 12 exact, 125 stand-in, 7 none.

Kit art used (all in `art/ui/kit/CATALOG.md`, checked against the sprite
manifest by the `inventory_backpack` capture scene): `lk_icon_berries`, `lk_icon_bone`, `lk_icon_build`, `lk_icon_campfire`, `lk_icon_crystals`, `lk_icon_drumstick`, `lk_icon_hatchet`, `lk_icon_heart`, `lk_icon_hide`, `lk_icon_lightning`, `lk_icon_logs`, `lk_icon_magma_ore`, `lk_icon_mushroom`, `lk_icon_pickaxe`, `lk_icon_plank`, `lk_icon_plant_fiber`, `lk_icon_rocks`, `lk_icon_rope`, `lk_icon_runestone`, `lk_icon_spear`, `lk_icon_star`, `lk_icon_stone`, `lk_icon_stone_axe`, `lk_icon_stones`, `lk_icon_torch`, `lk_icon_tusk`, `lk_icon_warning`.

Rebuild this table from `ItemInfo` when the mapping changes; the `item_info`
spec fails if an item stops resolving to listed art.


## Materials

| Item | Id | Art | Tint | Status |
|---|---|---|---|---|
| Abyssal Shard | `AbyssalShard` | `lk_icon_crystals` | #785AAA | stand-in |
| Adamantine Bar | `AdamantineBar` | `lk_icon_plank` | #BE82D7 | stand-in |
| Adamantine Ore | `AdamantineOre` | `lk_icon_magma_ore` | #BE82D7 | stand-in |
| Amethyst | `Amethyst` | `lk_icon_crystals` | #C88CFF | stand-in |
| Ancient Ember | `AncientEmber` | `lk_icon_campfire` | — | stand-in |
| Ashen Oil | `AshenOil` | `lk_icon_magma_ore` | #AAA5A0 | stand-in |
| Bloodroot | `Bloodroot` | `lk_icon_plant_fiber` | #E67878 | stand-in |
| Bone | `Bone` | `lk_icon_bone` | — | exact |
| Cave Mushroom | `CaveMushroom` | `lk_icon_mushroom` | #FAEBD7 | stand-in |
| Charged Core | `ChargedCore` | `lk_icon_lightning` | — | stand-in |
| Chestnut Mushroom | `ChestnutMushroom` | `lk_icon_mushroom` | — | exact |
| Clay | `Clay` | `lk_icon_stone` | #E18C64 | stand-in |
| Cobalt Bar | `CobaltBar` | `lk_icon_plank` | #82A0F0 | stand-in |
| Cobalt Ore | `CobaltOre` | `lk_icon_rocks` | #82A0F0 | stand-in |
| Copper Bar | `CopperBar` | `lk_icon_plank` | #F0A06E | stand-in |
| Copper Ore | `CopperOre` | `lk_icon_rocks` | #F0A06E | stand-in |
| Dire Hide | `DireHide` | `lk_icon_hide` | #8C736E | stand-in |
| Elderberry | `Elderberry` | `lk_icon_berries` | #785AA0 | stand-in |
| Emberglass | `Emberglass` | `lk_icon_crystals` | #FF8C46 | stand-in |
| Flint | `Flint` | `lk_icon_stone` | #9696A5 | stand-in |
| Frostleaf | `Frostleaf` | `lk_icon_plant_fiber` | #AFDCFF | stand-in |
| Glow-Fur | `GlowFur` | `lk_icon_hide` | #BEF5F5 | stand-in |
| Guardian Heart | `GuardianHeart` | `lk_icon_heart` | #BE5A6E | stand-in |
| Hazelnut | `Hazelnut` | `lk_icon_berries` | #C88C50 | stand-in |
| Herbs | `Herbs` | `lk_icon_plant_fiber` | #BEEBA0 | stand-in |
| Hide | `Hide` | `lk_icon_hide` | — | exact |
| Iron Bar | `IronBar` | `lk_icon_plank` | #C3C8D4 | stand-in |
| Iron Ore | `IronOre` | `lk_icon_rocks` | #C3C8D4 | stand-in |
| Jade | `Jade` | `lk_icon_crystals` | #78E696 | stand-in |
| Juniper Berry | `JuniperBerry` | `lk_icon_berries` | #8C96E6 | stand-in |
| Mithril Bar | `MithrilBar` | `lk_icon_plank` | #AAF0EB | stand-in |
| Mithril Ore | `MithrilOre` | `lk_icon_rocks` | #AAF0EB | stand-in |
| Moonpetal | `Moonpetal` | `lk_icon_plant_fiber` | #DCE1FF | stand-in |
| Obsidian | `Obsidian` | `lk_icon_stone` | #73648C | stand-in |
| Plant Fiber | `Fiber` | `lk_icon_plant_fiber` | — | exact |
| Raspberry | `Raspberry` | `lk_icon_berries` | #FFAABE | stand-in |
| Raw Meat | `RawMeat` | `lk_icon_drumstick` | #FF9696 | stand-in |
| Redcap Mushroom | `RedcapMushroom` | `lk_icon_mushroom` | #FF786E | stand-in |
| Resin | `Resin` | `lk_icon_crystals` | #FFB946 | stand-in |
| Siege Resin | `SiegeResin` | `lk_icon_crystals` | #E6783C | stand-in |
| Silver Bar | `SilverBar` | `lk_icon_plank` | #F0F5FF | stand-in |
| Silver Ore | `SilverOre` | `lk_icon_rocks` | #F0F5FF | stand-in |
| Starstone | `Starstone` | `lk_icon_stone` | #FFEB96 | stand-in |
| Stone | `Stone` | `lk_icon_stones` | — | exact |
| Stormglass | `Stormglass` | `lk_icon_crystals` | — | stand-in |
| Thornvine | `Thornvine` | `lk_icon_rope` | #96C86E | stand-in |
| Wood | `Wood` | `lk_icon_logs` | — | exact |

## Tools

| Item | Id | Art | Tint | Status |
|---|---|---|---|---|
| Adamantine Axe | `AdamantineAxe` | `lk_icon_hatchet` | #BE82D7 | stand-in |
| Adamantine Pickaxe | `AdamantinePickaxe` | `lk_icon_pickaxe` | #BE82D7 | stand-in |
| Cobalt Axe | `CobaltAxe` | `lk_icon_hatchet` | #82A0F0 | stand-in |
| Cobalt Pickaxe | `CobaltPickaxe` | `lk_icon_pickaxe` | #82A0F0 | stand-in |
| Copper Axe | `CopperAxe` | `lk_icon_hatchet` | #F0A06E | stand-in |
| Copper Pickaxe | `CopperPickaxe` | `lk_icon_pickaxe` | #F0A06E | stand-in |
| Iron Axe | `IronAxe` | `lk_icon_hatchet` | — | exact |
| Iron Pickaxe | `IronPickaxe` | `lk_icon_pickaxe` | — | exact |
| Mithril Axe | `MithrilAxe` | `lk_icon_hatchet` | #AAF0EB | stand-in |
| Mithril Pickaxe | `MithrilPickaxe` | `lk_icon_pickaxe` | #AAF0EB | stand-in |
| Silver Axe | `SilverAxe` | `lk_icon_hatchet` | #F0F5FF | stand-in |
| Silver Pickaxe | `SilverPickaxe` | `lk_icon_pickaxe` | #F0F5FF | stand-in |
| Stone Axe | `StoneAxe` | `lk_icon_stone_axe` | — | exact |
| Stone Pickaxe | `StonePickaxe` | `lk_icon_pickaxe` | #D7D7DC | stand-in |
| Wooden Axe | `WoodenAxe` | `lk_icon_hatchet` | #E6AF78 | stand-in |
| Wooden Pickaxe | `WoodenPickaxe` | `lk_icon_pickaxe` | #E6AF78 | stand-in |

## Weapons

| Item | Id | Art | Tint | Status |
|---|---|---|---|---|
| Adamantine Bow | `AdamantineBow` | — | — | none |
| Adamantine Dagger | `AdamantineDagger` | `lk_icon_tusk` | #BE82D7 | stand-in |
| Adamantine Spear | `AdamantineSpear` | `lk_icon_spear` | #BE82D7 | stand-in |
| Adamantine Sword | `AdamantineSword` | `lk_icon_tusk` | #BE82D7 | stand-in |
| Bone Dagger | `BoneDagger` | `lk_icon_tusk` | #FAF0D7 | stand-in |
| Bone Spear | `BoneSpear` | `lk_icon_spear` | #FAF0D7 | stand-in |
| Cobalt Bow | `CobaltBow` | — | — | none |
| Cobalt Dagger | `CobaltDagger` | `lk_icon_tusk` | #82A0F0 | stand-in |
| Cobalt Spear | `CobaltSpear` | `lk_icon_spear` | #82A0F0 | stand-in |
| Cobalt Sword | `CobaltSword` | `lk_icon_tusk` | #82A0F0 | stand-in |
| Copper Bow | `CopperBow` | — | — | none |
| Copper Dagger | `CopperDagger` | `lk_icon_tusk` | #F0A06E | stand-in |
| Copper Spear | `CopperSpear` | `lk_icon_spear` | #F0A06E | stand-in |
| Copper Sword | `CopperSword` | `lk_icon_tusk` | #F0A06E | stand-in |
| Flint Dagger | `FlintDagger` | `lk_icon_tusk` | #9696A5 | stand-in |
| Flint Spear | `FlintSpear` | `lk_icon_spear` | #9696A5 | stand-in |
| Guardian's Fang | `GuardianFang` | `lk_icon_tusk` | — | stand-in |
| Iron Bow | `IronBow` | — | — | none |
| Iron Dagger | `IronDagger` | `lk_icon_tusk` | #C3C8D4 | stand-in |
| Iron Spear | `IronSpear` | `lk_icon_spear` | #C3C8D4 | stand-in |
| Iron Sword | `IronSword` | `lk_icon_tusk` | #C3C8D4 | stand-in |
| Jade Dagger | `JadeDagger` | `lk_icon_tusk` | #96E1AA | stand-in |
| Jade Spear | `JadeSpear` | `lk_icon_spear` | #96E1AA | stand-in |
| Mithril Bow | `MithrilBow` | — | — | none |
| Mithril Dagger | `MithrilDagger` | `lk_icon_tusk` | #AAF0EB | stand-in |
| Mithril Spear | `MithrilSpear` | `lk_icon_spear` | #AAF0EB | stand-in |
| Mithril Sword | `MithrilSword` | `lk_icon_tusk` | #AAF0EB | stand-in |
| Obsidian Dagger | `ObsidianDagger` | `lk_icon_tusk` | #73648C | stand-in |
| Obsidian Spear | `ObsidianSpear` | `lk_icon_spear` | #73648C | stand-in |
| Silver Bow | `SilverBow` | — | — | none |
| Silver Dagger | `SilverDagger` | `lk_icon_tusk` | #F0F5FF | stand-in |
| Silver Spear | `SilverSpear` | `lk_icon_spear` | #F0F5FF | stand-in |
| Silver Sword | `SilverSword` | `lk_icon_tusk` | #F0F5FF | stand-in |
| Stone Dagger | `StoneDagger` | `lk_icon_tusk` | #CDCDD4 | stand-in |
| Stone Spear | `StoneSpear` | `lk_icon_spear` | — | exact |
| Stone Sword | `StoneSword` | `lk_icon_tusk` | #CDCDD4 | stand-in |
| Wooden Bow | `WoodenBow` | — | — | none |
| Wooden Spear | `WoodenSpear` | `lk_icon_spear` | #E6AF78 | stand-in |

## Armour

| Item | Id | Art | Tint | Status |
|---|---|---|---|---|
| Adamantine Chest | `AdamantineChest` | `lk_icon_hide` | #BE82D7 | stand-in |
| Adamantine Head | `AdamantineHead` | `lk_icon_hide` | #BE82D7 | stand-in |
| Adamantine Legs/Boots | `AdamantineLegs` | `lk_icon_hide` | #BE82D7 | stand-in |
| Bone Chest | `BoneChest` | `lk_icon_hide` | #FAF0D7 | stand-in |
| Bone Head | `BoneHead` | `lk_icon_hide` | #FAF0D7 | stand-in |
| Bone Legs/Boots | `BoneLegs` | `lk_icon_hide` | #FAF0D7 | stand-in |
| Cobalt Chest | `CobaltChest` | `lk_icon_hide` | #82A0F0 | stand-in |
| Cobalt Head | `CobaltHead` | `lk_icon_hide` | #82A0F0 | stand-in |
| Cobalt Legs/Boots | `CobaltLegs` | `lk_icon_hide` | #82A0F0 | stand-in |
| Copper Chest | `CopperChest` | `lk_icon_hide` | #F0A06E | stand-in |
| Copper Head | `CopperHead` | `lk_icon_hide` | #F0A06E | stand-in |
| Copper Legs/Boots | `CopperLegs` | `lk_icon_hide` | #F0A06E | stand-in |
| Hide Chest | `HideChest` | `lk_icon_hide` | #D7A578 | stand-in |
| Hide Head | `HideHead` | `lk_icon_hide` | #D7A578 | stand-in |
| Hide Legs/Boots | `HideLegs` | `lk_icon_hide` | #D7A578 | stand-in |
| Iron Chest | `IronChest` | `lk_icon_hide` | #C3C8D4 | stand-in |
| Iron Head | `IronHead` | `lk_icon_hide` | #C3C8D4 | stand-in |
| Iron Legs/Boots | `IronLegs` | `lk_icon_hide` | #C3C8D4 | stand-in |
| Mithril Chest | `MithrilChest` | `lk_icon_hide` | #AAF0EB | stand-in |
| Mithril Head | `MithrilHead` | `lk_icon_hide` | #AAF0EB | stand-in |
| Mithril Legs/Boots | `MithrilLegs` | `lk_icon_hide` | #AAF0EB | stand-in |
| Silver Chest | `SilverChest` | `lk_icon_hide` | #F0F5FF | stand-in |
| Silver Head | `SilverHead` | `lk_icon_hide` | #F0F5FF | stand-in |
| Silver Legs/Boots | `SilverLegs` | `lk_icon_hide` | #F0F5FF | stand-in |

## Ammunition

| Item | Id | Art | Tint | Status |
|---|---|---|---|---|
| Flint Arrow | `FlintArrow` | `lk_icon_spear` | #9696A5 | stand-in |

## Medicine, food and draughts

| Item | Id | Art | Tint | Status |
|---|---|---|---|---|
| Advanced Medicine | `AdvancedMedicine` | `lk_icon_heart` | — | stand-in |
| Basic Medicine | `BasicMedicine` | `lk_icon_heart` | #FFC8C8 | stand-in |
| Cooked Meat | `CookedMeat` | `lk_icon_drumstick` | — | exact |
| Glimmer Draught | `GlimmerDraught` | `lk_icon_star` | #AAE6FF | stand-in |
| Glimmerberry | `Glimmerberry` | `lk_icon_berries` | #96E6FF | stand-in |
| Greater Healing Potion | `GreaterPotion` | `lk_icon_heart` | #BE6EC8 | stand-in |
| Healing Potion | `Potion` | `lk_icon_heart` | #E696C8 | stand-in |
| Hearty Tonic | `HeartyTonic` | `lk_icon_heart` | #FFB46E | stand-in |
| Redberry | `Redberry` | `lk_icon_berries` | — | exact |
| Strong Glimmer Draught | `StrongGlimmerDraught` | `lk_icon_star` | #82BEFF | stand-in |
| Strong Sunberry Draught | `StrongSunberryDraught` | `lk_icon_lightning` | #FFBE5A | stand-in |
| Sunberry | `Sunberry` | `lk_icon_berries` | #FFD76E | stand-in |
| Sunberry Draught | `SunberryDraught` | `lk_icon_lightning` | — | stand-in |
| Sweetberry | `Sweetberry` | `lk_icon_berries` | #FFB4DC | stand-in |

## Siege items

| Item | Id | Art | Tint | Status |
|---|---|---|---|---|
| Breaching Charge | `BreachingCharge` | `lk_icon_warning` | — | stand-in |
| Fire Bomb | `FireBomb` | `lk_icon_torch` | — | stand-in |

## Placeables

| Item | Id | Art | Tint | Status |
|---|---|---|---|---|
| Portable Extraction Rune | `ExtractionRune` | `lk_icon_runestone` | — | stand-in |
| Workbench | `Workbench` | `lk_icon_build` | — | stand-in |

## Notes

- Armour: the kit has no helmet, chestpiece or boots art. Every piece uses the
  hide icon tinted by its material; the Equipped tab labels the slots Head, Chest
  and Legs. Each needs its own icon.
- Swords and daggers use the tusk (a blade) tinted by material; only Guardian's
  Fang is the tusk untinted. Spears use the spear icon; the stone spear is exact.
- Bows have no art: nothing in the kit reads as a bow.
- Ores are the rocks icon tinted per metal (Adamantine Ore uses the magma ore);
  bars are the plank tinted per metal (no ingot art).
- Medicine and potions use the heart; draughts use the lightning (XP) or star
  (Luck) icon, the same glyphs as the boost stat rows.

