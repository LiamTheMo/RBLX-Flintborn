-- Medicine, food and boost use (GDD §4.5, §51, §59, Q64–65, Q135, Q137). A
-- consumable is used from the hand: the player holds it (its hotbar slot is
-- equipped) and the attack input asks to use it. The server checks the item is
-- carried and held, and the character eats or drinks for the item's use time
-- (ConsumeRules: medicine its animation time, food and boosts CONSUME_SECONDS).
-- Exactly one item is consumed per accepted request:
--   * medicine heals at once and its animation is the only cooldown (Q64: "not a
--     pre-heal channel"; ConsumeRules.APPLY_AT_START);
--   * food and boosts are used when the animation ends: food feeds and starts its
--     heal, a boost berry or draught starts its timed boost (ModifierService).
-- Food and boosts confirm with a toast.
--
-- One use runs at a time: a request while one runs (the medicine animation
-- included) is refused as Busy and consumes nothing, and a replayed request ID is
-- refused as Duplicate. A use still to be applied is interrupted, with nothing
-- consumed, when the player stops holding the item (puts it away, picks another
-- slot, the stack leaves the slot), goes down, dies or leaves the run; a refusal
-- found when the time is up (the item is gone, a stronger boost started) also
-- consumes nothing. Interrupting medicine only stops its animation: the heal
-- already landed and the medicine lock runs on. The request answers once the item
-- is applied ((true): at once for medicine, at the end for the rest) or refused
-- ((false, reason)). The running use is shown through the player's ConsumeItem,
-- ConsumeStart and ConsumeEnd attributes, from which every client animates the
-- character. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local BoostRules = require(ReplicatedStorage.Shared.Survival.BoostRules)
local ConsumeRules = require(ReplicatedStorage.Shared.Survival.ConsumeRules)
local Consumables = require(ReplicatedStorage.Shared.Items.Consumables)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local SurvivalRules = require(ReplicatedStorage.Shared.Survival.SurvivalRules)
local Validation = require(ReplicatedStorage.Shared.Data.Validation)
local RequestLedger = require(script.Parent.Parent.Infrastructure.RequestLedger)
local InventoryService = require(script.Parent.InventoryService)
local ModifierService = require(script.Parent.ModifierService)
local SurvivalService = require(script.Parent.SurvivalService)

local HealingService = {}

-- Fires (player, catalogId) after a medicine, food or boost item is used.
HealingService.Used = Signal.new()

HealingService.REMEMBERED_REQUESTS = 32

-- Remembers request IDs so a replayed or duplicated request is applied once.
local requests = RequestLedger.new(function()
	return HealingService.REMEMBERED_REQUESTS
end)
-- uses[player] = the running use (ConsumeRules.Begin) plus `applied`, the waiting
-- request's `thread` and, for medicine, `lockBefore` (the lock it replaced).
local uses = {}

local function heldId(player: Player): string?
	local item = InventoryService.Equipped(player)
	return item and item.catalogId or nil
end

-- Why `item` cannot be used now (checked when asked and again when it is
-- applied), or nil.
local function blocker(player: Player, catalogId: string, item): string?
	if InventoryService.Count(player, catalogId) < 1 then
		return "NotCarried"
	end
	if item.boost ~= nil and not BoostRules.IsValid(item.boost) then
		return "NotConsumable"
	end
	-- A draught that would change nothing (a boost at least as strong is running)
	-- is refused rather than wasted; food still feeds and leaves the boost as is.
	if item.kind == Consumables.Boost and not ModifierService.BoostTakes(player, item.boost) then
		return "BoostActive"
	end
	return nil
end

local function show(player: Player, use)
	player:SetAttribute(ConsumeRules.ITEM_ATTRIBUTE, use and use.catalogId or nil)
	player:SetAttribute(ConsumeRules.START_ATTRIBUTE, use and use.startedAt or nil)
	player:SetAttribute(ConsumeRules.END_ATTRIBUTE, use and use.endsAt or nil)
end

-- Consumes one item and applies it. Returns (ok, reason).
local function apply(player: Player, use): (boolean, string?)
	local item, catalogId = use.item, use.catalogId
	local rules = SurvivalService.Get(player)
	local humanoid = SurvivalService.Humanoid(player)
	if rules == nil or humanoid == nil or humanoid.Health <= 0 then
		return false, "NotInRun"
	end
	local reason = blocker(player, catalogId, item)
	if reason then
		return false, reason
	end
	if not InventoryService.RemoveAll(player, { [catalogId] = 1 }) then
		return false, "NotCarried"
	end
	local now = workspace:GetServerTimeNow()
	if item.kind == Consumables.Medicine then
		SurvivalService.SetHealth(player, SurvivalRules.MedicineHeal(item, humanoid.Health, humanoid.MaxHealth))
	elseif item.kind == Consumables.Food then
		SurvivalRules.Eat(rules, item, now)
	end
	local kept = nil
	if item.boost then
		local entry, started = ModifierService.ApplyBoost(player, item.boost)
		kept = if started then nil else entry
	end
	if item.kind ~= Consumables.Medicine then
		InventoryService.Notify(player, BoostRules.UseText(item, kept))
	end
	HealingService.Used:Fire(player, catalogId)
	return true, nil
end

-- Ends `player`'s use (already out of `uses`): hides it and answers a waiting
-- request with (ok, reason). A use that never applied gives back the medicine
-- lock it took.
local function finish(player: Player, use, ok: boolean, reason: string?)
	if not use.applied and not ok and use.lockBefore ~= nil then
		local rules = SurvivalService.Get(player)
		if rules and rules.medicineLockUntil == use.endsAt then
			SurvivalRules.CancelMedicine(rules, use.lockBefore)
		end
	end
	if player.Parent then
		show(player, nil)
	end
	local thread = use.thread
	use.thread = nil
	if thread then
		task.spawn(thread, ok, reason)
	end
end

-- What the server sees of `player` for ConsumeRules.Interruption.
local function view(player: Player)
	local humanoid = SurvivalService.Humanoid(player)
	return {
		present = player.Parent ~= nil,
		alive = SurvivalService.Get(player) ~= nil and humanoid ~= nil and humanoid.Health > 0,
		downed = player:GetAttribute("Downed") == true,
		held = heldId(player),
	}
end

-- Advances every running use to `now`: interrupts the ones that must stop and
-- applies the ones whose time is up (each exactly once). Called every Heartbeat.
function HealingService.Step(now: number)
	local running = {}
	for player, use in uses do
		table.insert(running, { player, use })
	end
	for _, entry in running do
		local player, use = entry[1], entry[2]
		if uses[player] ~= use then
			continue
		end
		local reason = ConsumeRules.Interruption(view(player), use.catalogId)
		if reason then
			uses[player] = nil
			-- Already applied (medicine): only the animation stops.
			finish(player, use, use.applied == true, if use.applied then nil else reason)
		elseif ConsumeRules.Done(use, now) then
			-- Out of the table first, so nothing can apply it twice.
			uses[player] = nil
			if use.applied then
				finish(player, use, true, nil)
			else
				local ok, why = apply(player, use)
				finish(player, use, ok, why)
			end
		end
	end
end

-- True while `player` is eating or drinking.
function HealingService.IsUsing(player: Player): boolean
	return uses[player] ~= nil
end

-- Asks to use the held consumable `catalogId`. Returns (ok, reason) once it is
-- applied (medicine at once; food and boosts yield until the animation ends) or
-- refused; a refusal consumes nothing.
function HealingService.Use(player: Player, requestId: any, catalogId: any)
	if not Validation.IsId(requestId) then
		return false, "BadRequest"
	end
	local item = Consumables.Get(catalogId)
	if item == nil then
		return false, "NotConsumable"
	end
	local rules = SurvivalService.Get(player)
	local humanoid = SurvivalService.Humanoid(player)
	if rules == nil or humanoid == nil or humanoid.Health <= 0 then
		return false, "NotInRun"
	end
	if player:GetAttribute("Downed") then
		return false, "Downed"
	end
	if not requests:FirstTime(player, requestId) then
		return false, "Duplicate"
	end
	if uses[player] ~= nil then
		return false, "Busy"
	end
	local reason = blocker(player, catalogId, item)
	if reason then
		return false, reason
	end
	if heldId(player) ~= catalogId then
		return false, "NotHeld"
	end
	local now = workspace:GetServerTimeNow()
	local use = ConsumeRules.Begin(requestId, catalogId, item, now)
	if item.kind == Consumables.Medicine then
		local before = rules.medicineLockUntil
		if not SurvivalRules.StartMedicine(rules, item, now) then
			return false, "Cooldown"
		end
		use.lockBefore = before
	end
	if ConsumeRules.AppliesAtStart(item) then
		local ok, why = apply(player, use)
		if not ok then
			finish(player, use, false, why)
			return false, why
		end
		use.applied = true
		uses[player] = use
		show(player, use)
		return true, nil
	end
	use.thread = coroutine.running()
	uses[player] = use
	show(player, use)
	return coroutine.yield()
end

function HealingService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	Remotes.Handle("UseConsumable", HealingService.Use)
	RunService.Heartbeat:Connect(function()
		if next(uses) ~= nil then
			HealingService.Step(workspace:GetServerTimeNow())
		end
	end)
	Players.PlayerRemoving:Connect(function(player)
		local use = uses[player]
		if use then
			uses[player] = nil
			finish(player, use, use.applied == true, if use.applied then nil else "NotInRun")
		end
		requests:Forget(player)
	end)
end

return HealingService
