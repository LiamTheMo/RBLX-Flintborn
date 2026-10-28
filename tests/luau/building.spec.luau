local Shared = game:GetService("ReplicatedStorage").Shared
local BuildRules = require(Shared.Building.BuildRules)
local StructureCatalog = require(Shared.Building.StructureCatalog)

local function totem(ownerKey, x, z, level)
	local stats = StructureCatalog.TotemLevels[level or 1]
	return { ownerKey = ownerKey, position = Vector3.new(x, 0, z), radius = stats.radius, hp = stats.hp, isTotem = true }
end

local function wall(ownerKey, x, z)
	return { ownerKey = ownerKey, position = Vector3.new(x, 0, z) }
end

test("the no-build aura rejects partial overlaps, not just centres", function()
	local auras = { { center = Vector3.new(0, 0, 0), radius = 50 } }
	local half = BuildRules.HalfExtents(Vector3.new(8, 8, 1), 0)
	expect(not BuildRules.OverlapsAura(Vector3.new(60, 0, 0), half, auras), "well outside")
	expect(BuildRules.OverlapsAura(Vector3.new(53, 0, 0), half, auras), "centre outside, edge inside")
	local turned = BuildRules.HalfExtents(Vector3.new(8, 8, 1), 1)
	expect(not BuildRules.OverlapsAura(Vector3.new(53, 0, 0), turned, auras), "rotated, the thin side stays out")
	expectNear(BuildRules.AURA_RADIUS, 50 / 0.28, 0.01, "50 m in studs")
end)

test("totem HP by level is 500 / 1,000 / 2,500 and upgrades grow the radius", function()
	expectEq(BuildRules.TotemLevel(1).hp, 500, "level 1")
	expectEq(BuildRules.TotemLevel(2).hp, 1000, "level 2")
	expectEq(BuildRules.TotemLevel(3).hp, 2500, "level 3")
	expect(BuildRules.TotemLevel(2).radius > BuildRules.TotemLevel(1).radius, "radius grows")
	expect(BuildRules.UpgradeCost(1) ~= nil and BuildRules.UpgradeCost(3) == nil, "two upgrades")
end)

test("cover stops decay; losing it assigns one 240–360 s deadline that never re-rolls", function()
	local rng = Random.new(1)
	local base = wall("A", 5, 0)
	local mine = totem("A", 0, 0)
	BuildRules.Reconcile(base, { mine }, 100, rng)
	expectEq(base.decayDeadline, nil, "covered")
	mine.hp = 0
	BuildRules.Reconcile(base, { mine }, 100, rng)
	local deadline = base.decayDeadline
	expect(deadline >= 340 and deadline <= 460, "240–360 s from now")
	BuildRules.Reconcile(base, { mine }, 150, rng)
	expectEq(base.decayDeadline, deadline, "no reset while uncovered")
	BuildRules.Reconcile(base, { totem("A", 0, 0) }, 160, rng)
	expectEq(base.decayDeadline, nil, "reclaiming clears it")
end)

test("rival totems neither cover nor take over while the owner's totem stands", function()
	local rng = Random.new(2)
	local base = wall("A", 5, 0)
	local mine = totem("A", 0, 0)
	local rival = totem("B", 8, 0)
	local totems = { mine, rival }
	expectEq(#BuildRules.Claim({ base }, rival, totems), 0, "no takeover under a standing totem")
	expectEq(base.ownerKey, "A", "original owner keeps it")
	mine.hp = 0
	BuildRules.Reconcile(base, totems, 0, rng)
	expect(base.decayDeadline ~= nil, "rival cover does not stop the owner's decay")
	expectEq(#BuildRules.Claim({ base }, rival, totems), 1, "claimable once the totem falls")
	expectEq(base.ownerKey, "B", "new owner")
	BuildRules.Reconcile(base, totems, 1, rng)
	expectEq(base.decayDeadline, nil, "the new owner's totem stops decay")
end)

test("server-generated structures are never claimable and never decay", function()
	local ruin = { generated = true, position = Vector3.new(1, 0, 1) }
	local rival = totem("B", 0, 0)
	expectEq(#BuildRules.Claim({ ruin }, rival, { rival }), 0, "never claimed")
	BuildRules.Reconcile(ruin, {}, 0, Random.new(3))
	expectEq(ruin.decayDeadline, nil, "never decays")
end)

test("tools hit 1.5× against their material; snapping uses the grid", function()
	expectEq(BuildRules.StructureDamage(10, "Axe", "Wood"), 15, "axe vs wood")
	expectEq(BuildRules.StructureDamage(10, "Pickaxe", "Iron"), 15, "pickaxe vs iron")
	expectEq(BuildRules.StructureDamage(10, "Pickaxe", "Adamantine"), 15, "pickaxe vs every metal tier")
	expectEq(BuildRules.StructureDamage(10, "Pickaxe", "Wood"), 10, "pickaxe vs wood")
	expectEq(BuildRules.StructureDamage(10, "Axe", "Stone"), 10, "axe vs stone")
	expectEq(BuildRules.StructureDamage(10, nil, "Wood"), 10, "weapons hit normally")
	local snapped = BuildRules.Snap(Vector3.new(5.1, 2.26, -6.2))
	expect(snapped.X == 4 and snapped.Z == -8 and snapped.Y == 2.5, "snapped")
end)

test("crops ripen on server timestamps", function()
	local berries = StructureCatalog.Crops.Redberry
	expectEq(BuildRules.CropRemaining(berries, 100, 100), 180, "3 minutes")
	expectEq(BuildRules.CropRemaining(berries, 100, 400), 0, "ripe")
	expectEq(StructureCatalog.Crops.Berries, nil, "plain Berries no longer grow")
	-- Planters grow Redberries, Sweetberries, Herbs, saplings (GDD §51) and Fiber (GDD §53).
	local grown = {}
	for _, cropId in StructureCatalog.CROP_ORDER do
		expect(StructureCatalog.Crops[cropId] ~= nil, cropId .. " is a crop")
		grown[StructureCatalog.Crops[cropId].yield.catalogId] = true
	end
	for _, catalogId in { "Redberry", "Sweetberry", "Herbs", "Wood", "Fiber" } do
		expect(grown[catalogId], "a planter grows " .. catalogId)
	end
end)
