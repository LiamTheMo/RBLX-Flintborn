-- Batch forging through the ForgeCraft handler (UI rebuild D4): the server checks
-- the count's type and range before anything runs, a batch commits as one
-- journal operation keyed by the nonce, and XP follows the crafts actually made.
-- Drives the real ForgeService against fake Roblox services and a fake profile.

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server

local guids = 0
local fakes = {
	HttpService = {
		GenerateGUID = function()
			guids += 1
			return ("guid-%d"):format(guids)
		end,
	},
}
local originalGetService = game.GetService
game.GetService = function(self, name)
	return fakes[name] or originalGetService(self, name)
end
warn = function() end

local PlaceConfig = require(Shared.Config.PlaceConfig)
PlaceConfig.IsLobby = function()
	return true
end
local Remotes = require(Shared.Net.Remotes)
local handlers = {}
Remotes.Handle = function(name, fn)
	handlers[name] = fn
end
Remotes.Get = function()
	return { FireClient = function() end }
end

local ForgeRules = require(Shared.Crafting.ForgeRules)
local ProfileSchema = require(Shared.Data.ProfileSchema)
local OperationJournal = require(Server.Infrastructure.OperationJournal)

local profiles = {}
local ProfileService = require(Server.Services.ProfileService)
ProfileService.GetProfile = function(player)
	return profiles[player]
end
ProfileService.RunOperation = function(player, operationId, kind, apply)
	local profile = profiles[player]
	local ok, result, applied = pcall(OperationJournal.Run, profile, operationId, kind, 1, apply)
	if not ok then
		return false, result, false
	end
	return true, result, applied
end

local xp = { calls = 0, share = nil, mastery = 0 }
local ProgressionService = require(Server.Services.ProgressionService)
ProgressionService.GrantXp = function(_, action, _, share)
	assert(action == "Forge", "forge XP")
	xp.calls += 1
	xp.share = share
end
ProgressionService.GrantMastery = function(_, track, actions)
	assert(track == "Crafting", "crafting mastery")
	xp.mastery += actions
end
local TradeService = require(Server.Services.TradeService)
TradeService.InSession = function()
	return false
end

local ForgeService = require(Server.Services.ForgeService)
ForgeService.Start()

local player = { UserId = 7, Name = "Smith", DisplayName = "Smith" }

local function fresh(ironBars: number)
	local profile = ProfileSchema.Default(0)
	profile.vault.materials = { IronBar = ironBars, Wood = 500 }
	ForgeRules.RefreshUnlocks(profile, 1)
	profiles[player] = profile
	xp.calls, xp.share, xp.mastery = 0, nil, 0
	return profile
end

test("the count is type- and range-checked before anything runs", function()
	for index, bad in { 0, -3, 11, 1.5, 0 / 0, math.huge, "2", true, {} } do
		local profile = fresh(1000)
		local ok, reason = handlers.ForgeCraft(player, "ForgeIronPickaxe", nil, "n-bad-" .. index, bad)
		expect(not ok and reason == "BadQuantity", "refused " .. tostring(bad))
		expectEq(profile.vault.materials.IronBar, 1000, tostring(bad) .. ": nothing charged")
		expectEq(next(profile.operations.records), nil, tostring(bad) .. ": no journal entry")
		expectEq(xp.calls, 0, tostring(bad) .. ": no XP")
	end
end)

test("older clients that send no count forge exactly one", function()
	local profile = fresh(1000)
	local ok, receipt = handlers.ForgeCraft(player, "ForgeIronPickaxe", nil, "n-one")
	expect(ok and receipt.count == 1, "one forged")
	expectEq(profile.vault.materials.IronBar, 980, "one charged")
	expect(xp.calls == 1 and xp.share == nil and xp.mastery == 2, "XP as before")
end)

test("a batch commits once under its nonce and earns XP for every craft", function()
	local profile = fresh(1000)
	local ok, receipt = handlers.ForgeCraft(player, "ForgeIronPickaxe", nil, "n-batch", 10)
	expect(ok and receipt.count == 10, "ten forged")
	expectEq(profile.vault.materials.IronBar, 800, "200 bars spent")
	expectEq(#profile.lobbyBackpack.slots, 10, "ten pickaxes")
	expect(xp.calls == 1 and xp.share == 10 and xp.mastery == 20, "XP and mastery for ten")
	local again
	ok, again = handlers.ForgeCraft(player, "ForgeIronPickaxe", nil, "n-batch", 10)
	expect(ok and again.count == 10, "a retry returns the receipt")
	expectEq(profile.vault.materials.IronBar, 800, "never charged twice")
	expectEq(#profile.lobbyBackpack.slots, 10, "never granted twice")
	expectEq(xp.calls, 1, "no XP for the retry")
end)

test("a batch the vault cannot fully pay for is refused whole", function()
	local profile = fresh(150)
	local ok, reason = handlers.ForgeCraft(player, "ForgeIronPickaxe", nil, "n-short", 8)
	expect(not ok and reason == "MissingMaterials", "eight need 160 bars")
	expectEq(profile.vault.materials.IronBar, 150, "nothing charged")
	expectEq(#profile.lobbyBackpack.slots, 0, "nothing granted")
	expectEq(xp.calls, 0, "no XP")
	ok = handlers.ForgeCraft(player, "ForgeIronPickaxe", nil, "n-short-7", 7)
	expect(ok, "seven fit")
end)

test("the snapshot tells the client how many it may forge", function()
	fresh(150)
	local view = handlers.ForgeSnapshot(player)
	expectEq(view.maxBatch, ForgeRules.MAX_BATCH, "batch cap sent")
	local byId = {}
	for _, recipe in view.recipes do
		byId[recipe.id] = recipe
	end
	expectEq(byId.ForgeIronPickaxe.maxCount, 7, "150 bars pay for seven")
	expectEq(byId.ForgeIronSword.maxCount, 0, "no hide, none")
	expectEq(byId.PermanentStonePickaxe.maxCount, 0, "no materials for a conversion")
end)
