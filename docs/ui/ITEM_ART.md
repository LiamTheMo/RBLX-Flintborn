# Item art

Every catalog item (`ItemCatalog.Items`, generated gear, ores and bars
included) draws **its own icon and nothing else**: `lk_item_<CatalogId>`, a
110 px slot icon packed into `atlas_lk_items4_1` / `atlas_lk_items4_2`, and its
356 px hero copy `lk_item_<CatalogId>__hi` (an image of its own) in the Forge /
Crafting picture and the Inventory detail card. Both are built from the owner's
512 px PNGs in `art/ui/items/source/` by `art/ui/items/build_item_icons.py`,
with the mapping in `art/ui/items/ICONS.json` (STYLE_GUIDE §9.7).

`Kit.ItemIcon` draws it everywhere an item is shown (`Art.ItemIcon` →
`ItemInfo.ItemSprite`). While the icon's atlas has not loaded on a client, the
picture shows the item's kind glyph (⚒ tools and weapons, ▤ armour, ◇
everything else; `Art.KindGlyph`), faded, and the icon replaces it by itself
when the atlas loads (STYLE_GUIDE §6.5). A slot never prints the item's name:
the name is in the icon root's `KitItemName` attribute, for tooltips and detail
cards.

The older kit art items drew before their own icons (`ItemInfo.Icon`: the
closest `lk_icon_*`, often tinted, for 95 items, and nothing for bows, swords,
daggers and armour) is gone. The `lk_icon_*` sprites it used stay in the
uploaded `atlas_lk_items`, where menus, stat rows, events and the Journal still
use them as icons.

Totals: 144 items; 81 in `atlas_lk_items4_1`, 63 in `atlas_lk_items4_2`.

Adamantine turned red (2026-11-04): the owner's 11 new Adamantine PNGs replaced
the purple ones, so every item moved from the uploaded `atlas_lk_items2_1` /
`_2` (retired, never changed) to the new `atlas_lk_items3_1` / `_2`, same split,
same rects; only the 11 Adamantine icons differ. Their 11 hero copies are new
images too. All 13 were uploaded the same day.

New spears (2026-11-04): the owner's 12 redrawn spears (every tier, Wooden to
Adamantine) replaced theirs the same way: every item moved from the uploaded
`atlas_lk_items3_*` (retired, never changed) to `atlas_lk_items4_1` / `_2`, same
split and rects, only the 12 spear icons different, and the 12 spear hero copies
rebuilt. All 14 were uploaded the same day (ids in `UiAssetIds.json`).

Rebuild this table from `ICONS.json` when an item is added; the `item_info`
spec fails if a catalog item has no icon or hero copy in `UiSprites.json`.

## Materials

| Item | Id | Source (`art/ui/items/source/`) | Atlas |
|---|---|---|---|
| Abyssal Shard | `AbyssalShard` | `abyssal-shard.png` | `atlas_lk_items4_1` |
| Adamantine Bar | `AdamantineBar` | `adamantine-bar.png` | `atlas_lk_items4_1` |
| Adamantine Ore | `AdamantineOre` | `adamantine-ore.png` | `atlas_lk_items4_1` |
| Amethyst | `Amethyst` | `amethyst.png` | `atlas_lk_items4_1` |
| Ancient Ember | `AncientEmber` | `ancient-ember.png` | `atlas_lk_items4_1` |
| Ashen Oil | `AshenOil` | `ashen-oil.png` | `atlas_lk_items4_1` |
| Bloodroot | `Bloodroot` | `bloodroot.png` | `atlas_lk_items4_1` |
| Bone | `Bone` | `bone.png` | `atlas_lk_items4_1` |
| Cave Mushroom | `CaveMushroom` | `cave-mushroom.png` | `atlas_lk_items4_1` |
| Charged Core | `ChargedCore` | `charged-core.png` | `atlas_lk_items4_1` |
| Chestnut Mushroom | `ChestnutMushroom` | `chestnut-mushroom.png` | `atlas_lk_items4_1` |
| Clay | `Clay` | `clay.png` | `atlas_lk_items4_1` |
| Cobalt Bar | `CobaltBar` | `cobalt-bar.png` | `atlas_lk_items4_1` |
| Cobalt Ore | `CobaltOre` | `cobalt-ore.png` | `atlas_lk_items4_1` |
| Copper Bar | `CopperBar` | `copper-bar.png` | `atlas_lk_items4_1` |
| Copper Ore | `CopperOre` | `copper-ore.png` | `atlas_lk_items4_1` |
| Dire Hide | `DireHide` | `dire-hide.png` | `atlas_lk_items4_1` |
| Elderberry | `Elderberry` | `elderberry.png` | `atlas_lk_items4_1` |
| Emberglass | `Emberglass` | `emberglass.png` | `atlas_lk_items4_1` |
| Flint | `Flint` | `flint.png` | `atlas_lk_items4_1` |
| Frostleaf | `Frostleaf` | `frostleaf.png` | `atlas_lk_items4_1` |
| Glow-Fur | `GlowFur` | `glow-fur.png` | `atlas_lk_items4_1` |
| Guardian Heart | `GuardianHeart` | `guardian-heart.png` | `atlas_lk_items4_1` |
| Hazelnut | `Hazelnut` | `hazelnut.png` | `atlas_lk_items4_1` |
| Herbs | `Herbs` | `herbs.png` | `atlas_lk_items4_1` |
| Hide | `Hide` | `hide.png` | `atlas_lk_items4_1` |
| Iron Bar | `IronBar` | `iron-bar.png` | `atlas_lk_items4_1` |
| Iron Ore | `IronOre` | `iron-ore.png` | `atlas_lk_items4_1` |
| Jade | `Jade` | `jade.png` | `atlas_lk_items4_1` |
| Juniper Berry | `JuniperBerry` | `juniper-berry.png` | `atlas_lk_items4_1` |
| Mithril Bar | `MithrilBar` | `mithril-bar.png` | `atlas_lk_items4_1` |
| Mithril Ore | `MithrilOre` | `mithril-ore.png` | `atlas_lk_items4_1` |
| Moonpetal | `Moonpetal` | `moonpetal.png` | `atlas_lk_items4_1` |
| Obsidian | `Obsidian` | `obsidian.png` | `atlas_lk_items4_1` |
| Plant Fiber | `Fiber` | `plant-fiber.png` | `atlas_lk_items4_1` |
| Raspberry | `Raspberry` | `raspberry.png` | `atlas_lk_items4_1` |
| Raw Meat | `RawMeat` | `raw-meat.png` | `atlas_lk_items4_1` |
| Redcap Mushroom | `RedcapMushroom` | `redcap-mushroom.png` | `atlas_lk_items4_1` |
| Resin | `Resin` | `resin.png` | `atlas_lk_items4_1` |
| Siege Resin | `SiegeResin` | `siege-resin.png` | `atlas_lk_items4_1` |
| Silver Bar | `SilverBar` | `silver-bar.png` | `atlas_lk_items4_1` |
| Silver Ore | `SilverOre` | `silver-ore.png` | `atlas_lk_items4_1` |
| Starstone | `Starstone` | `starstone.png` | `atlas_lk_items4_1` |
| Stone | `Stone` | `stone.png` | `atlas_lk_items4_1` |
| Stormglass | `Stormglass` | `stormglass.png` | `atlas_lk_items4_1` |
| Thornvine | `Thornvine` | `thornvine.png` | `atlas_lk_items4_1` |
| Wood | `Wood` | `wood.png` | `atlas_lk_items4_1` |

## Tools

| Item | Id | Source (`art/ui/items/source/`) | Atlas |
|---|---|---|---|
| Adamantine Axe | `AdamantineAxe` | `adamantine-axe.png` | `atlas_lk_items4_2` |
| Adamantine Pickaxe | `AdamantinePickaxe` | `adamantine-pickaxe.png` | `atlas_lk_items4_2` |
| Cobalt Axe | `CobaltAxe` | `cobalt-axe.png` | `atlas_lk_items4_2` |
| Cobalt Pickaxe | `CobaltPickaxe` | `cobalt-pickaxe.png` | `atlas_lk_items4_2` |
| Copper Axe | `CopperAxe` | `copper-axe.png` | `atlas_lk_items4_2` |
| Copper Pickaxe | `CopperPickaxe` | `copper-pickaxe.png` | `atlas_lk_items4_2` |
| Iron Axe | `IronAxe` | `iron-axe.png` | `atlas_lk_items4_2` |
| Iron Pickaxe | `IronPickaxe` | `iron-pickaxe.png` | `atlas_lk_items4_2` |
| Mithril Axe | `MithrilAxe` | `mithril-axe.png` | `atlas_lk_items4_2` |
| Mithril Pickaxe | `MithrilPickaxe` | `mithril-pickaxe.png` | `atlas_lk_items4_2` |
| Silver Axe | `SilverAxe` | `silver-axe.png` | `atlas_lk_items4_2` |
| Silver Pickaxe | `SilverPickaxe` | `silver-pickaxe.png` | `atlas_lk_items4_2` |
| Stone Axe | `StoneAxe` | `stone-axe.png` | `atlas_lk_items4_1` |
| Stone Pickaxe | `StonePickaxe` | `stone-pickaxe.png` | `atlas_lk_items4_1` |
| Wooden Axe | `WoodenAxe` | `wooden-axe.png` | `atlas_lk_items4_1` |
| Wooden Pickaxe | `WoodenPickaxe` | `wooden-pickaxe.png` | `atlas_lk_items4_1` |

## Weapons

| Item | Id | Source (`art/ui/items/source/`) | Atlas |
|---|---|---|---|
| Adamantine Bow | `AdamantineBow` | `adamantine-bow.png` | `atlas_lk_items4_2` |
| Adamantine Dagger | `AdamantineDagger` | `adamantine-dagger.png` | `atlas_lk_items4_2` |
| Adamantine Spear | `AdamantineSpear` | `adamantine-spear.png` | `atlas_lk_items4_2` |
| Adamantine Sword | `AdamantineSword` | `adamantine-sword.png` | `atlas_lk_items4_2` |
| Bone Dagger | `BoneDagger` | `bone-dagger.png` | `atlas_lk_items4_1` |
| Bone Spear | `BoneSpear` | `bone-spear.png` | `atlas_lk_items4_2` |
| Cobalt Bow | `CobaltBow` | `cobalt-bow.png` | `atlas_lk_items4_2` |
| Cobalt Dagger | `CobaltDagger` | `cobalt-dagger.png` | `atlas_lk_items4_2` |
| Cobalt Spear | `CobaltSpear` | `cobalt-spear.png` | `atlas_lk_items4_2` |
| Cobalt Sword | `CobaltSword` | `cobalt-sword.png` | `atlas_lk_items4_2` |
| Copper Bow | `CopperBow` | `copper-bow.png` | `atlas_lk_items4_2` |
| Copper Dagger | `CopperDagger` | `copper-dagger.png` | `atlas_lk_items4_2` |
| Copper Spear | `CopperSpear` | `copper-spear.png` | `atlas_lk_items4_2` |
| Copper Sword | `CopperSword` | `copper-sword.png` | `atlas_lk_items4_2` |
| Flint Dagger | `FlintDagger` | `flint-dagger.png` | `atlas_lk_items4_2` |
| Flint Spear | `FlintSpear` | `flint-spear.png` | `atlas_lk_items4_2` |
| Guardian's Fang | `GuardianFang` | `guardians-fang.png` | `atlas_lk_items4_1` |
| Iron Bow | `IronBow` | `iron-bow.png` | `atlas_lk_items4_2` |
| Iron Dagger | `IronDagger` | `iron-dagger.png` | `atlas_lk_items4_2` |
| Iron Spear | `IronSpear` | `iron-spear.png` | `atlas_lk_items4_2` |
| Iron Sword | `IronSword` | `iron-sword.png` | `atlas_lk_items4_2` |
| Jade Dagger | `JadeDagger` | `jade-dagger.png` | `atlas_lk_items4_2` |
| Jade Spear | `JadeSpear` | `jade-spear.png` | `atlas_lk_items4_2` |
| Mithril Bow | `MithrilBow` | `mithril-bow.png` | `atlas_lk_items4_2` |
| Mithril Dagger | `MithrilDagger` | `mithril-dagger.png` | `atlas_lk_items4_2` |
| Mithril Spear | `MithrilSpear` | `mithril-spear.png` | `atlas_lk_items4_2` |
| Mithril Sword | `MithrilSword` | `mithril-sword.png` | `atlas_lk_items4_2` |
| Obsidian Dagger | `ObsidianDagger` | `obsidian-dagger.png` | `atlas_lk_items4_2` |
| Obsidian Spear | `ObsidianSpear` | `obsidian-spear.png` | `atlas_lk_items4_2` |
| Silver Bow | `SilverBow` | `silver-bow.png` | `atlas_lk_items4_2` |
| Silver Dagger | `SilverDagger` | `silver-dagger.png` | `atlas_lk_items4_2` |
| Silver Spear | `SilverSpear` | `silver-spear.png` | `atlas_lk_items4_2` |
| Silver Sword | `SilverSword` | `silver-sword.png` | `atlas_lk_items4_2` |
| Stone Dagger | `StoneDagger` | `stone-dagger.png` | `atlas_lk_items4_1` |
| Stone Spear | `StoneSpear` | `stone-spear.png` | `atlas_lk_items4_1` |
| Stone Sword | `StoneSword` | `stone-sword.png` | `atlas_lk_items4_1` |
| Wooden Bow | `WoodenBow` | `wooden-bow.png` | `atlas_lk_items4_1` |
| Wooden Spear | `WoodenSpear` | `wooden-spear.png` | `atlas_lk_items4_1` |

## Armour

| Item | Id | Source (`art/ui/items/source/`) | Atlas |
|---|---|---|---|
| Adamantine Chest | `AdamantineChest` | `adamantine-chest.png` | `atlas_lk_items4_2` |
| Adamantine Head | `AdamantineHead` | `adamantine-head.png` | `atlas_lk_items4_2` |
| Adamantine Legs/Boots | `AdamantineLegs` | `adamantine-legs-and-boots.png` | `atlas_lk_items4_2` |
| Bone Chest | `BoneChest` | `bone-chest.png` | `atlas_lk_items4_1` |
| Bone Head | `BoneHead` | `bone-head.png` | `atlas_lk_items4_2` |
| Bone Legs/Boots | `BoneLegs` | `bone-legs-and-boots.png` | `atlas_lk_items4_2` |
| Cobalt Chest | `CobaltChest` | `cobalt-chest.png` | `atlas_lk_items4_2` |
| Cobalt Head | `CobaltHead` | `cobalt-head.png` | `atlas_lk_items4_2` |
| Cobalt Legs/Boots | `CobaltLegs` | `cobalt-legs-and-boots.png` | `atlas_lk_items4_2` |
| Copper Chest | `CopperChest` | `copper-chest.png` | `atlas_lk_items4_2` |
| Copper Head | `CopperHead` | `copper-head.png` | `atlas_lk_items4_2` |
| Copper Legs/Boots | `CopperLegs` | `copper-legs-and-boots.png` | `atlas_lk_items4_2` |
| Hide Chest | `HideChest` | `hide-chest.png` | `atlas_lk_items4_1` |
| Hide Head | `HideHead` | `hide-head.png` | `atlas_lk_items4_1` |
| Hide Legs/Boots | `HideLegs` | `hide-legs-and-boots.png` | `atlas_lk_items4_1` |
| Iron Chest | `IronChest` | `iron-chest.png` | `atlas_lk_items4_2` |
| Iron Head | `IronHead` | `iron-head.png` | `atlas_lk_items4_2` |
| Iron Legs/Boots | `IronLegs` | `iron-legs-and-boots.png` | `atlas_lk_items4_2` |
| Mithril Chest | `MithrilChest` | `mithril-chest.png` | `atlas_lk_items4_2` |
| Mithril Head | `MithrilHead` | `mithril-head.png` | `atlas_lk_items4_2` |
| Mithril Legs/Boots | `MithrilLegs` | `mithril-legs-and-boots.png` | `atlas_lk_items4_2` |
| Silver Chest | `SilverChest` | `silver-chest.png` | `atlas_lk_items4_2` |
| Silver Head | `SilverHead` | `silver-head.png` | `atlas_lk_items4_2` |
| Silver Legs/Boots | `SilverLegs` | `silver-legs-and-boots.png` | `atlas_lk_items4_2` |

## Ammunition

| Item | Id | Source (`art/ui/items/source/`) | Atlas |
|---|---|---|---|
| Flint Arrow | `FlintArrow` | `flint-arrow.png` | `atlas_lk_items4_1` |

## Medicine, food and draughts

| Item | Id | Source (`art/ui/items/source/`) | Atlas |
|---|---|---|---|
| Advanced Medicine | `AdvancedMedicine` | `advanced-medicine.png` | `atlas_lk_items4_1` |
| Basic Medicine | `BasicMedicine` | `basic-medicine.png` | `atlas_lk_items4_1` |
| Cooked Meat | `CookedMeat` | `cooked-meat.png` | `atlas_lk_items4_1` |
| Glimmer Draught | `GlimmerDraught` | `glimmer-draught.png` | `atlas_lk_items4_1` |
| Glimmerberry | `Glimmerberry` | `glimmerberry.png` | `atlas_lk_items4_1` |
| Greater Healing Potion | `GreaterPotion` | `greater-healing-potion.png` | `atlas_lk_items4_1` |
| Healing Potion | `Potion` | `healing-potion.png` | `atlas_lk_items4_1` |
| Hearty Tonic | `HeartyTonic` | `hearty-tonic.png` | `atlas_lk_items4_1` |
| Redberry | `Redberry` | `redberry.png` | `atlas_lk_items4_1` |
| Strong Glimmer Draught | `StrongGlimmerDraught` | `strong-glimmer-draught.png` | `atlas_lk_items4_1` |
| Strong Sunberry Draught | `StrongSunberryDraught` | `strong-sunberry-draught.png` | `atlas_lk_items4_1` |
| Sunberry | `Sunberry` | `sunberry.png` | `atlas_lk_items4_1` |
| Sunberry Draught | `SunberryDraught` | `sunberry-draught.png` | `atlas_lk_items4_1` |
| Sweetberry | `Sweetberry` | `sweetberry.png` | `atlas_lk_items4_1` |

## Siege items

| Item | Id | Source (`art/ui/items/source/`) | Atlas |
|---|---|---|---|
| Breaching Charge | `BreachingCharge` | `breaching-charge.png` | `atlas_lk_items4_1` |
| Fire Bomb | `FireBomb` | `fire-bomb.png` | `atlas_lk_items4_1` |

## Placeables

| Item | Id | Source (`art/ui/items/source/`) | Atlas |
|---|---|---|---|
| Portable Extraction Rune | `ExtractionRune` | `portable-extraction-rune.png` | `atlas_lk_items4_1` |
| Workbench | `Workbench` | `workbench.png` | `atlas_lk_items4_1` |
