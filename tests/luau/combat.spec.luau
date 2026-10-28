local Shared = game:GetService("ReplicatedStorage").Shared
local ArmorRules = require(Shared.Combat.ArmorRules)
local DamageRules = require(Shared.Combat.DamageRules)
local WeaponCatalog = require(Shared.Combat.WeaponCatalog)
local GameConstants = require(Shared.GameConstants)
local InventoryRules = require(Shared.Inventory.InventoryRules)

local function fullSet(tier)
	return {
		{ tier = tier, slot = "Head" },
		{ tier = tier, slot = "Chest" },
		{ tier = tier, slot = "Legs" },
	}
end

test("full armor sets follow the Hide → Adamantine ladder at 100 HP", function()
	-- Confirmed Hide ×1.2 and Iron ×2.0; Bone 1.5, Copper 1.8; then ×1.25 per metal.
	local ladder = {
		Hide = 120,
		Bone = 150,
		Copper = 180,
		Iron = 200,
		Silver = 250,
		Cobalt = 312.5,
		Mithril = 390.625,
		Adamantine = 488.28125,
	}
	for tier, ehp in ladder do
		expectNear(100 * ArmorRules.Factor(fullSet(tier)), ehp, 1e-9, tier .. " full set")
	end
	expectEq(ArmorRules.Factor({}), 1, "unarmored")
	-- Wood and Stone armor are removed; gem-class materials make no armor.
	for _, tier in { "Wood", "Stone", "Flint", "Obsidian", "Jade" } do
		expectEq(ArmorRules.Factor(fullSet(tier)), 1, tier .. " gives no armor")
	end
end)

test("armor pieces add and mixed tiers combine additively", function()
	local mixed = { { tier = "Iron", slot = "Chest" }, { tier = "Hide", slot = "Head" } }
	local expected = 1 + 1.0 * 0.45 + 0.2 * 0.25
	expectNear(ArmorRules.Factor(mixed), expected, 1e-9, "iron chest + hide head")
	expect(ArmorRules.Factor({ { tier = "Iron", slot = "Head" } }) < 2, "one iron piece never gives the full x2")
	local rolled = ArmorRules.PieceIncrement("Iron", "Chest", 0.05)
	expectNear(rolled, 0.45 * 1.05, 1e-9, "quality roll scales the piece")
end)

test("damage never takes HP below zero and armor stretches it", function()
	local iron = ArmorRules.Factor(fullSet("Iron"))
	expectNear(GameConstants.ApplyDamage(100, iron, 25), 87.5, 1e-9, "a stone spear hit on full iron")
	expectEq(GameConstants.ApplyDamage(10, 1, 25), 0, "clamped at zero")
end)

test("confirmed melee numbers and cooldowns", function()
	expectEq(WeaponCatalog.Hand.damage, 5, "rock 5")
	expectEq(WeaponCatalog.Hand.cooldown, 0.3, "rock 0.3 s")
	expectEq(WeaponCatalog.For("WoodenSpear").damage, 15, "wooden spear ~15")
	expectEq(WeaponCatalog.For("StoneSpear").damage, 25, "stone spear ~25")
	expectEq(WeaponCatalog.For("StoneSpear").cooldown, 0.9, "spear 0.9 s")
	expectEq(WeaponCatalog.For("StoneDagger").cooldown, 0.4, "dagger 0.4 s")
	expectEq(WeaponCatalog.For("StoneSword").cooldown, 0.7, "sword 0.7 s")
	expectEq(WeaponCatalog.For("StoneAxe"), WeaponCatalog.Hand, "tools strike like a rock")
	-- Every crafted tier hits about 25% harder than the one below it (GDD §51).
	local previous = 0
	for _, tier in { "Stone", "Copper", "Iron", "Silver", "Cobalt", "Mithril", "Adamantine" } do
		local damage = WeaponCatalog.For(tier .. "Sword").damage
		expect(damage > previous, tier .. " sword beats the tier below")
		previous = damage
	end
	expectEq(WeaponCatalog.For("AdamantineSword").damage, 69, "adamantine sword")
	expectEq(WeaponCatalog.For("GuardianFang").damage, 86, "the Guardian's Fang is one tier above Adamantine")
	expectEq(WeaponCatalog.For("GuardianFang").cooldown, 0.7, "the Fang swings like a sword")
end)

test("attack cadence is enforced per weapon", function()
	local spear = WeaponCatalog.For("StoneSpear")
	expect(DamageRules.CooldownReady(nil, 0, spear.cooldown), "first attack")
	expect(not DamageRules.CooldownReady(10, 10.5, spear.cooldown), "too soon")
	expect(DamageRules.CooldownReady(10, 10.9, spear.cooldown), "after 0.9 s")
end)

test("friendly fire, risk state and safe zones gate all damage", function()
	local function actor(state, tribe, safe)
		return { state = state, tribeId = tribe, inSafeZone = safe }
	end
	expect(DamageRules.CanDamage(actor("ActiveRun"), actor("ActiveRun")), "two strangers in a run")
	expect(not DamageRules.CanDamage(actor("ActiveRun", "t1"), actor("ActiveRun", "t1")), "no friendly fire")
	expect(DamageRules.CanDamage(actor("ActiveRun", "t1"), actor("ActiveRun", "t2")), "rival tribes fight")
	expect(not DamageRules.CanDamage(actor("ActiveRun"), actor("WorldMainMenuReady")), "menu players are safe")
	expect(not DamageRules.CanDamage(actor("ActiveRun"), actor("PlayRequested")), "spawning players are safe")
	expect(not DamageRules.CanDamage(actor("ActiveRun"), actor("ExtractionProtected")), "extracting players are safe")
	expect(not DamageRules.CanDamage(actor("ActiveRun", nil, true), actor("ActiveRun")), "no damage from a safe zone")
	expect(not DamageRules.CanDamage(actor("ActiveRun"), actor("ActiveRun", nil, true)), "no damage into a safe zone")
end)

test("reach and arc checks", function()
	expect(DamageRules.WithinReach(11.5, 10), "inside reach plus allowance")
	expect(not DamageRules.WithinReach(13, 10), "too far")
	local facing = Vector3.new(0, 0, -1)
	expect(DamageRules.WithinArc(facing, Vector3.new(0, 0, -5), 50), "straight ahead")
	expect(not DamageRules.WithinArc(facing, Vector3.new(0, 0, 5), 50), "behind")
	expect(not DamageRules.WithinArc(facing, Vector3.new(5, 0, -5), 50), "outside a narrow spear arc")
	expect(DamageRules.WithinArc(facing, Vector3.new(5, 0, -5), 120), "inside a wide arc")
end)

test("bow damage ignores draw time while range grows", function()
	local bow = WeaponCatalog.For("WoodenBow")
	expectEq(DamageRules.ArrowDamage(bow, "FlintArrow"), 12, "wooden bow + flint arrow")
	expectEq(WeaponCatalog.ARROW, "FlintArrow", "flint is the only arrow tip")
	expectEq(WeaponCatalog.Arrows.Arrow, nil, "the plain Arrow is gone")
	-- Each metal bow adds 25% to the bow's own damage; the Flint Arrow adds 6.
	for tier, damage in { Copper = 14, Iron = 15, Silver = 18, Cobalt = 21, Mithril = 24, Adamantine = 29 } do
		local metalBow = WeaponCatalog.For(tier .. "Bow")
		expectEq(metalBow.kind, "Bow", tier .. " bow is a bow")
		expectEq(DamageRules.ArrowDamage(metalBow, "FlintArrow"), damage, tier .. " bow + flint arrow")
	end
	expect(DamageRules.ArrowSpeed(0.2) < DamageRules.ArrowSpeed(1), "longer draw flies faster")
	expectEq(DamageRules.ArrowSpeed(5), DamageRules.ArrowSpeed(1), "capped at a full draw")
	expectNear(DamageRules.MeleeDamage(WeaponCatalog.For("StoneSword"), -0.05), 17.1, 1e-9, "roll scales damage")
end)

test("armor equips into its slot, swaps, and still counts as carried", function()
	local inv = InventoryRules.New()
	local helmet = { instanceId = "h1", catalogId = "IronHead", ownerId = 1, location = "Carried", qualityRoll = 0 }
	local helmet2 = { instanceId = "h2", catalogId = "HideHead", ownerId = 1, location = "Carried", qualityRoll = 0 }
	InventoryRules.Add(inv, helmet)
	InventoryRules.Add(inv, helmet2)
	expect(InventoryRules.EquipArmor(inv, "backpack", 1), "equip iron helmet")
	expectEq(inv.armor.Head.instanceId, "h1", "worn")
	expectEq(InventoryRules.At(inv, "backpack", 1), nil, "slot freed")
	expect(InventoryRules.EquipArmor(inv, "backpack", 2), "swap in the hide helmet")
	expectEq(inv.armor.Head.instanceId, "h2", "hide now worn")
	expectEq(InventoryRules.At(inv, "backpack", 2).instanceId, "h1", "iron swapped back")
	expectEq(#InventoryRules.Items(inv), 2, "worn armor is still carried")
	expect(InventoryRules.UnequipArmor(inv, "Head"), "unequip")
	expectEq(inv.armor.Head, nil, "nothing worn")
	local spear = { instanceId = "s1", catalogId = "StoneSpear", ownerId = 1, location = "Carried", qualityRoll = 0 }
	InventoryRules.Add(inv, spear)
	local area, index = InventoryRules.FindInstance(inv, "s1")
	expect(not InventoryRules.EquipArmor(inv, area, index), "weapons cannot be worn")
	expectEq(InventoryRules.At(inv, area, index).instanceId, "s1", "the spear stays put")
end)
