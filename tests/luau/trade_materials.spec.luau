-- Vault material trades (GDD §10.2, §45, Q56, Q164): materials live only in the
-- vault, so eligible ones are offered from there by quantity and land in the
-- receiver's vault. Covers eligibility, capacity, exactly-once settlement,
-- crash reconciliation and rollback, and the real TradeService session flow
-- (snapshots, unlock on any vault change, all-or-nothing transfer) against fake
-- Roblox services and a fake clock.

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server

-- Fake clock and task scheduler ---------------------------------------------------

local clock = 0
local queue = {}
local sequence = 0
local threadErrors = {}

local function resume(thread, ...)
	local ok, err = coroutine.resume(thread, ...)
	if not ok then
		table.insert(threadErrors, tostring(err))
	end
end

task = {}
function task.spawn(fn, ...)
	local thread = if type(fn) == "thread" then fn else coroutine.create(fn)
	resume(thread, ...)
	return thread
end
function task.delay(seconds, fn, ...)
	sequence += 1
	table.insert(
		queue,
		{ at = clock + (seconds or 0), sequence = sequence, thread = coroutine.create(fn), args = table.pack(...) }
	)
end
function task.wait(seconds)
	sequence += 1
	table.insert(
		queue,
		{ at = clock + (seconds or 0), sequence = sequence, thread = coroutine.running(), args = table.pack() }
	)
	coroutine.yield()
	return seconds
end

warn = function() end

-- Runs everything due within the next `seconds`, in time order.
local function advance(seconds: number)
	local target = clock + seconds
	while true do
		local best = nil
		for index, entry in queue do
			if entry.at <= target then
				local current = best and queue[best]
				if
					current == nil
					or entry.at < current.at
					or (entry.at == current.at and entry.sequence < current.sequence)
				then
					best = index
				end
			end
		end
		if best == nil then
			break
		end
		local entry = table.remove(queue, best)
		clock = math.max(clock, entry.at)
		resume(entry.thread, table.unpack(entry.args, 1, entry.args.n))
	end
	clock = target
end

-- Fake Roblox services ------------------------------------------------------------

local Players = { _list = {} }
local removing = {}
Players.PlayerRemoving = {
	Connect = function(_, fn)
		table.insert(removing, fn)
	end,
}
function Players.GetPlayers(self)
	return table.clone(self._list)
end
function Players.GetPlayerByUserId(self, userId)
	for _, player in self._list do
		if player.UserId == userId then
			return player
		end
	end
	return nil
end

local guids = 0
local fakes = {
	Players = Players,
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
game.JobId = "job-trade"
workspace = {
	GetServerTimeNow = function()
		return clock
	end,
}

local PlaceConfig = require(Shared.Config.PlaceConfig)
PlaceConfig.IsLobby = function()
	return true
end
local Remotes = require(Shared.Net.Remotes)
local handlers = {}
local pushed = {}
Remotes.Handle = function(name, fn)
	handlers[name] = fn
end
Remotes.Get = function()
	return {
		FireClient = function(_, player, payload)
			pushed[player] = payload
		end,
	}
end

local GameConstants = require(Shared.GameConstants)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local ProfileSchema = require(Shared.Data.ProfileSchema)
local TradeRules = require(Shared.Economy.TradeRules)
local VaultRules = require(Shared.Extraction.VaultRules)

-- Profiles live in memory; a save copies one into `stored`.
local ProfileService = require(Server.Services.ProfileService)
local profiles, stored = {}, {}
ProfileService.GetProfile = function(player)
	return profiles[player]
end
ProfileService.Mutate = function(player, apply)
	local profile = profiles[player]
	if profile == nil then
		return false
	end
	apply(profile)
	-- The real service banks any backpack material after every write (GDD §45).
	if VaultRules.BankMaterials then
		VaultRules.BankMaterials(profile, clock)
	end
	return true
end
ProfileService.SaveNow = function(player)
	stored[player.UserId] = ProfileSchema.DeepCopy(profiles[player])
	return true
end
ProfileService.ReadStored = function(userId)
	return true, stored[userId]
end
local CurrencyService = require(Server.Services.CurrencyService)
CurrencyService.Publish = function() end

local TradeService = require(Server.Services.TradeService)
TradeService.Start()

local DAY = 86400 * 20000
local EMBER = "AncientEmber"

local function sword(id)
	return { instanceId = id, catalogId = "IronSword", ownerId = 1, location = "LobbyBackpack", qualityRoll = 0 }
end

local function trader(ember: number?)
	local profile = ProfileSchema.Default(0)
	profile.progression.level = 12
	profile.vault.materials = { [EMBER] = ember, Stone = 200 }
	return profile
end

local nextUserId = 100
local function join(profile)
	nextUserId += 1
	local player = { UserId = nextUserId, DisplayName = "P" .. nextUserId, Parent = Players }
	function player.SetAttribute() end
	table.insert(Players._list, player)
	profiles[player] = profile
	stored[player.UserId] = ProfileSchema.DeepCopy(profile)
	return player
end

-- Two joined players in an accepted session.
local function session(profileA, profileB)
	local a, b = join(profileA), join(profileB)
	local ok, id = handlers.TradeRequest(a, b.UserId)
	assert(ok, "invite")
	assert(handlers.TradeRespond(b, id, true), "accept")
	return a, b, id
end

local function lockAndConfirm(a, b, id)
	handlers.TradeLock(a, id)
	handlers.TradeLock(b, id)
	advance(TradeService.COUNTDOWN_SECONDS)
	handlers.TradeConfirm(a, id)
	return handlers.TradeConfirm(b, id)
end

-- Rules ---------------------------------------------------------------------------

test("only flagged materials trade, and only from the vault", function()
	expect(TradeRules.IsTradeableMaterial(EMBER), "Ancient Ember is flagged special")
	expect(not TradeRules.IsTradeableMaterial("Stone"), "ordinary Stone is not")
	expect(not TradeRules.IsTradeableMaterial(42), "nonsense IDs are not")
	expect(not TradeRules.IsTradeableSlot({ catalogId = EMBER, quantity = 2 }), "no backpack material slot")
	expect(TradeRules.IsTradeableSlot(sword("s1")), "gear still trades from the backpack")
	expectEq(TradeRules.MaterialOf(TradeRules.MaterialKey(EMBER)), EMBER, "material keys round-trip")
	expectEq(TradeRules.MaterialOf("stack:FlintArrow"), nil, "backpack keys are not material keys")
end)

test("a vault material offer is checked against the vault", function()
	local profile = trader(5)
	local function check(materials)
		return TradeRules.ValidateOffer(profile, { items = {}, materials = materials }, DAY)
	end
	expect(check({ [EMBER] = 5 }), "all five")
	local ok, reason = check({ [EMBER] = 6 })
	expect(not ok and reason == "MissingItem", "not more than the vault holds")
	ok, reason = check({ Stone = 10 })
	expect(not ok and reason == "NotTradeable", "ordinary materials stay refused")
	for _, bad in { 0, -1, 1.5, 0 / 0, math.huge } do
		ok, reason = check({ [EMBER] = bad })
		expect(not ok and reason == "BadQuantity", "bad quantity " .. tostring(bad))
	end
	profile.lobbyBackpack.slots = {}
	for index = 1, TradeRules.MAX_ITEMS do
		profile.lobbyBackpack.slots[index] = sword("s" .. index)
	end
	local nine = table.create(TradeRules.MAX_ITEMS - 1, 0)
	for index = 1, TradeRules.MAX_ITEMS - 1 do
		nine[index] = index
	end
	expect(TradeRules.ValidateOffer(profile, { items = nine, materials = { [EMBER] = 1 } }, DAY), "eight plus one")
	table.insert(nine, TradeRules.MAX_ITEMS)
	ok, reason = TradeRules.ValidateOffer(profile, { items = nine, materials = { [EMBER] = 1 } }, DAY)
	expect(not ok and reason == "TooManyItems", "a material counts toward the item limit")
end)

test("the receiver needs vault room, so a trade never deletes", function()
	local receiver = trader(GameConstants.MATERIAL_STACK_MAX - 5)
	local ok, reason = TradeRules.ValidateReceive(receiver, 0, DAY, { [EMBER] = 6 })
	expect(not ok and reason == "PartnerVaultFull", "six do not fit")
	expect(TradeRules.ValidateReceive(receiver, 0, DAY, { [EMBER] = 5 }), "five fit exactly")
end)

local function settle(giverEmber: number, quantity: number, receiverEmber: number?)
	local a, b = trader(giverEmber), trader(receiverEmber)
	b.currency.gems = 100
	local aStored, bStored = ProfileSchema.DeepCopy(a), ProfileSchema.DeepCopy(b)
	TradeRules.Settle("m1", { profile = a, userId = 1, offer = { items = {}, materials = { [EMBER] = quantity } } }, {
		profile = b,
		userId = 2,
		offer = { items = {}, gems = 100 },
	}, DAY)
	return a, b, aStored, bStored
end

test("a settled material trade moves vault to vault once, with the Gem fee", function()
	local a, b = settle(10, 4, 3)
	expectEq(a.vault.materials[EMBER], 6, "out of the giver's vault")
	expectEq(b.vault.materials[EMBER], 7, "into the receiver's vault")
	expectEq(#b.lobbyBackpack.slots, 0, "never through the backpack")
	expectEq(a.currency.gems, 95, "5% Gem fee")
	expectEq(a.trades.pending.m1.gave.materials[EMBER], 4, "recorded for reconciliation")
	expectEq(TradeRules.Reconcile(a, "m1", b, DAY + 1), "Settled", "B has it pending")
	expectEq(TradeRules.Reconcile(b, "m1", a, DAY + 1), "Settled", "A settled it")
	expectEq(TradeRules.Reconcile(a, "m1", b, DAY + 2), "None", "a replay does nothing")
	expectEq(a.vault.materials[EMBER] + b.vault.materials[EMBER], 13, "no Ember created")
end)

test("giving the whole stack clears the vault entry", function()
	local a = settle(4, 4)
	expectEq(a.vault.materials[EMBER], nil, "no zero stack left behind")
end)

test("a crash rolls the giver back into the vault exactly once", function()
	local a, _, _, bStored = settle(10, 4, 3)
	-- B never saved: its stored profile is the old one.
	expectEq(TradeRules.Reconcile(a, "m1", bStored, DAY + 1), "RolledBack", "A undone")
	expectEq(a.vault.materials[EMBER], 10, "A's Ember is back in the vault")
	expectEq(a.currency.gems, 0, "A's received Gems removed")
	expectEq(TradeRules.Reconcile(a, "m1", bStored, DAY + 2), "None", "a second reconcile does nothing")
	expectEq(a.vault.materials[EMBER], 10, "still ten: nothing duplicated")
	expectEq(bStored.vault.materials[EMBER], 3, "B never received it")
end)

test("a rolled-back receiver loses only what it received", function()
	local _, b, aStored = settle(10, 4, 3)
	expectEq(TradeRules.Reconcile(b, "m1", aStored, DAY + 1), "RolledBack", "A never saved")
	expectEq(b.vault.materials[EMBER], 3, "B keeps its own three")
	expectEq(b.currency.gems, 100, "B's Gems come back")
	expectEq(TradeRules.Reconcile(b, "m1", aStored, DAY + 2), "None", "replay does nothing")
	expectEq(b.vault.materials[EMBER], 3, "nothing more taken")
end)

test("a rollback finds received material wherever it sits and never goes negative", function()
	local _, b, aStored = settle(10, 4)
	-- Moved to the backpack somehow: the claw-back follows it.
	b.vault.materials[EMBER] = 1
	table.insert(b.lobbyBackpack.slots, { catalogId = EMBER, quantity = 3 })
	TradeRules.Reconcile(b, "m1", aStored, DAY + 1)
	expectEq(b.vault.materials[EMBER], nil, "vault part taken")
	expectEq(#b.lobbyBackpack.slots, 0, "backpack part taken")
end)

test("returning given material past the vault capacity deletes the overflow", function()
	local a, _, _, bStored = settle(10, 4)
	a.vault.materials[EMBER] = GameConstants.MATERIAL_STACK_MAX - 1
	TradeRules.Reconcile(a, "m1", bStored, DAY + 1)
	expectEq(a.vault.materials[EMBER], GameConstants.MATERIAL_STACK_MAX, "capped at 1,000 (Q154)")
end)

test("a pending trade from before vault offers still reconciles", function()
	local a = trader(nil)
	a.lobbyBackpack.slots = { sword("s1") }
	a.trades.pending.old = {
		counterpart = 2,
		gave = { items = {}, gems = 0 },
		received = { items = { { catalogId = EMBER, quantity = 3 } }, gems = 0 },
		at = DAY,
	}
	-- The received backpack stack has since been banked.
	a.vault.materials[EMBER] = 5
	expectEq(TradeRules.Reconcile(a, "old", ProfileSchema.Default(0), DAY + 1), "RolledBack", "rolled back")
	expectEq(a.vault.materials[EMBER], 2, "the three received are taken back")
end)

-- TradeService --------------------------------------------------------------------

test("a session offers vault material by quantity and settles it vault to vault", function()
	local a, b, id = session(trader(10), trader(3))
	local ok, reason = handlers.TradeOffer(a, id, {}, 0, { [EMBER] = 4 })
	expect(ok, "offer accepted: " .. tostring(reason))
	local theirs = pushed[b].theirs.items[1]
	expectEq(theirs and theirs.key, "mat:" .. EMBER, "the partner sees the material")
	expectEq(theirs and theirs.quantity, 4, "with its quantity")
	expectEq(theirs and theirs.name, ItemCatalog.Get(EMBER).name, "and its name")
	expect(lockAndConfirm(a, b, id), "confirmed")
	expectEq(pushed[a].kind, "Closed", "session closed")
	expectEq(pushed[a].reason, "Completed", "completed")
	expectEq(profiles[a].vault.materials[EMBER], 6, "out of A's vault")
	expectEq(profiles[b].vault.materials[EMBER], 7, "into B's vault")
	expectEq(next(profiles[a].trades.pending), nil, "finalised after both saves")
	expectEq(stored[b.UserId].vault.materials[EMBER], 7, "B's save holds it")
end)

test("ordinary materials, backpack materials and malformed offers are refused", function()
	local giver = trader(10)
	giver.lobbyBackpack.slots = { { catalogId = EMBER, quantity = 2 } }
	-- An old save's stack the sweep has not banked yet still cannot be offered.
	local a, b, id = session(giver, trader())
	local ok, reason = handlers.TradeOffer(a, id, {}, 0, { Stone = 5 })
	expect(not ok and reason == "NotTradeable", "ordinary Stone")
	ok, reason = handlers.TradeOffer(a, id, { "stack:" .. EMBER }, 0)
	expect(not ok and reason == "NotTradeable", "a backpack material stack")
	ok, reason = handlers.TradeOffer(a, id, { "mat:" .. EMBER }, 0)
	expect(ok and #pushed[b].theirs.items == 0, "a bare material key offers nothing")
	for _, bad in { "x", { [EMBER] = -1 }, { [EMBER] = 0 }, { [EMBER] = 1.5 }, { [EMBER] = "1" }, { [1] = 1 } } do
		ok, reason = handlers.TradeOffer(a, id, {}, 0, bad)
		expect(not ok and reason == "BadRequest", "malformed " .. tostring(bad))
	end
	ok, reason = handlers.TradeOffer(a, id, {}, 0, { [EMBER] = 11 })
	expect(not ok and reason == "MissingItem", "more than the vault holds")
	handlers.TradeCancel(a, id)
	expectEq(profiles[b].vault.materials[EMBER], nil, "nothing moved")
end)

test("an offer the partner's vault cannot hold is refused", function()
	local a, _, id = session(trader(10), trader(GameConstants.MATERIAL_STACK_MAX - 2))
	local ok, reason = handlers.TradeOffer(a, id, {}, 0, { [EMBER] = 3 })
	expect(not ok and reason == "PartnerVaultFull", "no room for three")
	expect(handlers.TradeOffer(a, id, {}, 0, { [EMBER] = 2 }), "two fit")
	handlers.TradeCancel(a, id)
end)

test("any vault material change unlocks both sides", function()
	local a, b, id = session(trader(10), trader())
	assert(handlers.TradeOffer(a, id, {}, 0, { [EMBER] = 4 }))
	handlers.TradeLock(a, id)
	handlers.TradeLock(b, id)
	expect(pushed[a].locked.mine and pushed[a].locked.theirs, "both locked")
	profiles[a].vault.materials[EMBER] = 9
	advance(TradeService.WATCH_SECONDS)
	expect(not pushed[a].locked.mine and not pushed[b].locked.theirs, "both unlocked")
	expectEq(pushed[a].confirmAt, nil, "the countdown is cancelled")
	local ok, reason = handlers.TradeConfirm(a, id)
	expect(not ok and reason == "NotReady", "nothing to confirm")
	-- Dropping below the offer can never settle, even when both lock again.
	profiles[a].vault.materials[EMBER] = 3
	advance(TradeService.WATCH_SECONDS)
	ok, reason = handlers.TradeLock(a, id)
	expect(not ok and reason == "ItemsChanged", "A cannot lock an offer it no longer holds")
	handlers.TradeCancel(a, id)
	expectEq(profiles[b].vault.materials[EMBER], nil, "B received nothing")
end)

test("a failed transfer restores both vaults", function()
	local a, b, id = session(trader(10), trader(3))
	assert(handlers.TradeOffer(a, id, {}, 0, { [EMBER] = 4 }))
	local original = TradeRules.Settle
	TradeRules.Settle = function(...)
		original(...)
		error("write failed")
	end
	lockAndConfirm(a, b, id)
	TradeRules.Settle = original
	expectEq(pushed[a].reason, "Failed", "reported as failed")
	expectEq(profiles[a].vault.materials[EMBER], 10, "A's Ember untouched")
	expectEq(profiles[b].vault.materials[EMBER], 3, "B's Ember untouched")
	expectEq(next(profiles[a].trades.pending), nil, "nothing pending")
end)

test("no spawned thread errored", function()
	advance(60)
	for _, err in threadErrors do
		print("    thread error: " .. err)
	end
	expectEq(#threadErrors, 0, "thread errors")
end)
