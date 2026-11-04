-- Placeholder creature, boss and pillar models (CreatureModels): every catalog
-- entry has a valid, normalized recipe that stands on its hitbox floor.
local Server = game:GetService("ServerScriptService").Server
local BossCatalog = require(Server.Rules.Bosses.BossCatalog)
local CreatureModels = require(Server.Rules.Visuals.CreatureModels)
local EnemyCatalog = require(Server.Rules.Enemies.EnemyCatalog)
local Recipe = require(Server.Rules.Visuals.Recipe)

-- Parts stay roughly inside the hitbox (fractions of each axis from its centre).
local REACH = 0.75
-- The lowest point sits on the hitbox floor, within this much.
local FLOOR = -0.5
local FLOOR_TOLERANCE = 0.1

local function sortedIds(map)
	local ids = {}
	for id in map do
		table.insert(ids, id)
	end
	table.sort(ids)
	return ids
end

local function checkRecipe(label: string, recipe, maxParts: number)
	assert(recipe, label .. " has no recipe")
	local problems = Recipe.Problems(recipe, 20)
	expectEq(#problems, 0, label .. " problems: " .. table.concat(problems, "; "))
	expectEq(recipe.normalized, true, label .. " is normalized")
	expect(#recipe.parts <= maxParts, ("%s has %d parts (max %d)"):format(label, #recipe.parts, maxParts))
	local low, high = Recipe.Bounds(recipe)
	for axis, name in { "x", "y", "z" } do
		expect(low[axis] >= -REACH, ("%s %s reaches %.2f below the hitbox"):format(label, name, low[axis]))
		expect(high[axis] <= REACH, ("%s %s reaches %.2f above the hitbox"):format(label, name, high[axis]))
	end
	expect(
		math.abs(low[2] - FLOOR) <= FLOOR_TOLERANCE,
		("%s lowest point is %.2f, not on the floor (%.1f)"):format(label, low[2], FLOOR)
	)
end

local function named(recipe, name: string)
	local found = {}
	for _, spec in recipe.parts do
		if spec.name == name then
			table.insert(found, spec)
		end
	end
	return found
end

test("every enemy and boss, and any unknown id, has a valid normalized model standing on its hitbox", function()
	for _, enemyId in sortedIds(EnemyCatalog.Enemies) do
		checkRecipe(enemyId, CreatureModels.For(enemyId), CreatureModels.MAX_CREATURE_PARTS)
	end
	for _, bossId in sortedIds(BossCatalog.Bosses) do
		checkRecipe(bossId, CreatureModels.ForBoss(bossId), CreatureModels.MAX_BOSS_PARTS)
	end
	-- An unknown id still gets a model, by theme or a generic one.
	checkRecipe("unknown enemy", CreatureModels.For("NoSuchCreature"), CreatureModels.MAX_CREATURE_PARTS)
	checkRecipe("unknown boss", CreatureModels.ForBoss("NoSuchBoss"), CreatureModels.MAX_BOSS_PARTS)
end)

test("the Guardian's pillar and shield have models", function()
	checkRecipe("pillar", CreatureModels.ForPillar(), CreatureModels.MAX_BOSS_PARTS)
	local shield = CreatureModels.Shield()
	expectEq(#Recipe.Problems(shield, 20), 0, "shield problems")
	expectEq(shield.normalized, true, "shield is normalized")
end)

test("models are shared data and keep the catalog colour", function()
	expect(CreatureModels.For("WildBoar") == CreatureModels.For("WildBoar"), "enemy recipes are cached")
	expect(CreatureModels.ForBoss("Minotaur") == CreatureModels.ForBoss("Minotaur"), "boss recipes are cached")
	-- The body part wears the catalog colour.
	for _, enemyId in { "WildBoar", "GreyWolf", "BrownBear" } do
		local expected = Recipe.Rgb(EnemyCatalog.Get(enemyId).color)
		local body = named(CreatureModels.For(enemyId), "Body")[1]
		assert(body, enemyId .. " has a body")
		for channel = 1, 3 do
			expectEq(body.color[channel], expected[channel], enemyId .. " colour channel " .. channel)
		end
	end
end)

test("creatures look like their kind; glowing parts are Neon and shells translucent", function()
	local function count(recipe, name: string): number
		return #named(recipe, name)
	end
	for _, enemyId in { "WildBoar", "GreyWolf", "BrownBear", "PlainsBison", "StonehideRhino", "WoollyMammoth" } do
		expectEq(count(CreatureModels.For(enemyId), "Leg"), 4, enemyId .. " legs")
	end
	expectEq(count(CreatureModels.For("IslandDodo"), "Leg"), 2, "dodo legs")
	expect(count(CreatureModels.For("IslandDodo"), "Beak") == 1, "dodo beak")
	expect(count(CreatureModels.For("WoollyMammoth"), "Tusk") == 2, "mammoth tusks")
	expect(count(CreatureModels.For("WoollyMammoth"), "Trunk") == 1, "mammoth trunk")
	expect(count(CreatureModels.For("StonehideRhino"), "Horn") >= 1, "rhino horn")
	expect(count(CreatureModels.For("AncientTortoise"), "Shell") == 1, "tortoise shell")
	expect(count(CreatureModels.For("Skeleton"), "Skull") == 1, "skeleton skull")
	expect(count(CreatureModels.For("EmberWisp"), "Core") == 1, "wisp core")
	expect(count(CreatureModels.ForBoss("Minotaur"), "Horns") == 2, "minotaur horns")
	local wisp = CreatureModels.For("EmberWisp")
	local shell, core = named(wisp, "Shell")[1], named(wisp, "Core")[1]
	assert(shell and core, "wisp has a shell and a core")
	expectEq(core.material, "Neon", "wisp core glows")
	expect(shell.transparency ~= nil and shell.transparency > 0, "wisp shell is translucent")
end)
