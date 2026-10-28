local Shared = game:GetService("ReplicatedStorage").Shared
local BuildRules = require(Shared.Building.BuildRules)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local Recipes = require(Shared.Crafting.Recipes)
local SiegeRules = require(Shared.Combat.SiegeRules)
local StructureCatalog = require(Shared.Building.StructureCatalog)
local Tiers = require(Shared.Items.Tiers)

test("siege items are thrown or placed, stack to 10 and craft at a Workbench", function()
	expectEq(SiegeRules.Kind("FireBomb"), "Thrown", "Fire Bomb")
	expectEq(SiegeRules.Kind("BreachingCharge"), "Placed", "Breaching Charge")
	expectEq(SiegeRules.Kind("StoneSpear"), nil, "weapons are not siege items")
	expectEq(SiegeRules.Kind(nil), nil, "empty hands")
	for _, id in { SiegeRules.FIRE_BOMB, SiegeRules.BREACHING_CHARGE } do
		expectEq(ItemCatalog.StackCap(id), 10, id .. " stack cap")
		expectEq(Recipes.Get(id) and Recipes.Get(id).station, "Workbench", id .. " station")
	end
end)

test("fire burns Wood x3, Stone x1 and every metal x0.25", function()
	local base = SiegeRules.BURST_DAMAGE
	expectEq(SiegeRules.FireDamage("Wood"), base * 3, "wood")
	expectEq(SiegeRules.FireDamage("Stone"), base, "stone")
	for _, metal in Tiers.Metals do
		expectEq(SiegeRules.FireDamage(metal), base * 0.25, metal)
	end
	-- Every building tier's walls carry their tier as material, so the burn follows.
	for _, tier in StructureCatalog.TIERS do
		local _, stats = StructureCatalog.Get("Wall", tier)
		local expected = if tier == "Wood" then 3 elseif tier == "Stone" then 1 else 0.25
		expectEq(SiegeRules.FireMultiplier(stats.material), expected, tier .. " wall")
	end
end)

test("siege damage ignores the held tool's match bonus", function()
	for _, tool in { false, "Axe", "Pickaxe" } do
		for _, material in { "Wood", "Stone", "Iron", "Adamantine" } do
			local kind = if tool then tool else nil
			local raw = SiegeRules.RawFor(900, kind, material)
			expectNear(BuildRules.StructureDamage(raw, kind, material), 900, 1e-9, tostring(tool) .. " vs " .. material)
		end
	end
end)

test("a breaching charge breaks wood and stone and takes a big chunk of metal", function()
	local damage = SiegeRules.BreachDamage()
	expectEq(SiegeRules.FUSE_SECONDS, 8, "8 s fuse")
	for _, piece in { "Wall", "Door" } do
		for _, tier in { "Wood", "Stone" } do
			local _, stats = StructureCatalog.Get(piece, tier)
			expect(damage >= stats.hp, tier .. " " .. piece .. " does not survive")
		end
	end
	for _, metal in Tiers.Metals do
		local _, wall = StructureCatalog.Get("Wall", metal)
		expect(damage < wall.hp, metal .. " wall survives one charge")
		expect(damage / wall.hp >= 0.25, metal .. " wall loses at least a quarter")
	end
end)

test("charges go only on enemy walls and doors, near, in sight and outside safe areas", function()
	local function target(overrides)
		local base = {
			pieceId = "Wall",
			ownedByPlacer = false,
			distance = 4,
			validatedDistance = 5,
			inSafeZone = false,
			inNoBuildAura = false,
		}
		for key, value in overrides do
			base[key] = value
		end
		return base
	end
	expectEq(SiegeRules.ChargeRefusal(target({})), nil, "enemy wall in reach")
	expectEq(SiegeRules.ChargeRefusal(target({ pieceId = "Door" })), nil, "enemy door")
	expectEq(SiegeRules.ChargeRefusal(nil), "NoTarget", "aim hit no structure (or a wall in the way)")
	expectEq(SiegeRules.ChargeRefusal(target({ pieceId = "Floor" })), "NotBreachable", "floors")
	expectEq(SiegeRules.ChargeRefusal(target({ pieceId = "Totem" })), "NotBreachable", "totems")
	expectEq(SiegeRules.ChargeRefusal(target({ ownedByPlacer = true })), "OwnStructure", "own wall")
	expectEq(SiegeRules.ChargeRefusal(target({ distance = SiegeRules.CHARGE_REACH + 0.5 })), "TooFar", "reach")
	local farValidated = SiegeRules.CHARGE_REACH + SiegeRules.VALIDATED_SLACK + 1
	expectEq(SiegeRules.ChargeRefusal(target({ validatedDistance = farValidated })), "TooFar", "validated reach")
	expectEq(SiegeRules.ChargeRefusal(target({ inSafeZone = true })), "SafeZone", "safe zone")
	expectEq(SiegeRules.ChargeRefusal(target({ inNoBuildAura = true })), "NoRaidZone", "portal aura")
	for _, reason in { "NoTarget", "NotBreachable", "OwnStructure", "TooFar", "SafeZone", "NoRaidZone", "NoItem" } do
		expect(SiegeRules.MESSAGES[reason] ~= nil, reason .. " has player-facing text")
	end
end)

test("a burst reaches pieces within its radius of their nearest face", function()
	local position, half = Vector3.new(0, 4, 0), Vector3.new(4, 4, 0.5)
	local radius = SiegeRules.BURST_RADIUS
	expect(SiegeRules.InBurst(Vector3.new(0, 2, 0.5 + radius - 0.1), position, half), "just inside, beside")
	expect(not SiegeRules.InBurst(Vector3.new(0, 2, 0.5 + radius + 0.1), position, half), "just outside, beside")
	expect(SiegeRules.InBurst(Vector3.new(0, 8 + radius - 0.1, 0), position, half), "just inside, above")
	expect(not SiegeRules.InBurst(Vector3.new(4 + radius, 8 + radius, 0), position, half), "diagonal corner")
end)

test("throws arc upward at a fixed speed, are rate-limited and range-capped", function()
	local level = SiegeRules.ThrowVelocity(Vector3.new(1, 0, 0))
	expectNear(level.Magnitude, SiegeRules.THROW_SPEED, 1e-9, "speed")
	expect(level.Y > 0, "a level throw still lobs upward")
	expect(SiegeRules.ThrowReady(nil, 0), "first throw")
	expect(not SiegeRules.ThrowReady(10, 10.5), "too soon")
	expect(SiegeRules.ThrowReady(10, 10 + SiegeRules.THROW_COOLDOWN), "after the cooldown")
	expect(not SiegeRules.ChargeReady(10, 10.2), "charges too")
	local from = Vector3.new(0, 0, 0)
	expect(SiegeRules.WithinRange(from, Vector3.new(SiegeRules.THROW_MAX_RANGE - 1, 0, 0)), "in range")
	expect(not SiegeRules.WithinRange(from, Vector3.new(SiegeRules.THROW_MAX_RANGE + 1, 0, 0)), "out of range")
	expectEq(SiegeRules.FuseLabel(7.2), "8", "countdown rounds up")
	expectEq(SiegeRules.FuseLabel(-1), "0", "never negative")
end)
