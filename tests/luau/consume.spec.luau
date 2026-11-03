-- Eating and drinking from the hand (GDD §59). ConsumeRules is checked directly;
-- the server rule drives the real HealingService against fake inventory, survival
-- and boost services and a fake clock: held food and boosts are used only when
-- their animation has run its full time, medicine heals at once with its animation
-- as the lock (Q64), exactly one item per accepted request, a request during the
-- animation (or a replayed one) is refused and consumes nothing, and putting the
-- item away, switching slots, going down, dying or leaving interrupts a use not
-- yet applied with nothing used.

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server

local ConsumeRules = require(Shared.Survival.ConsumeRules)
local Consumables = require(Shared.Items.Consumables)
local GameConstants = require(Shared.GameConstants)
local SurvivalRules = require(Shared.Survival.SurvivalRules)

local TestSupport = game:GetService("ServerStorage").TestSupport
local FakeRoblox = require(TestSupport.FakeRoblox)
local scheduler = require(TestSupport.Scheduler).new(100):Install():InstallServerTime()

-- One player's world: carried counts, the held hotbar item, survival state.
local function newPlayer(name: string)
	return FakeRoblox.Player(0, {
		Name = name,
		Parent = {},
		counts = {},
		held = nil,
		rules = SurvivalRules.NewState(),
		humanoid = { Health = 50, MaxHealth = 100 },
		removed = {},
		notices = {},
		boosts = {},
	})
end

FakeRoblox.StubServices({
	InventoryService = {
		Count = function(player, catalogId)
			return player.counts[catalogId] or 0
		end,
		Equipped = function(player)
			return player.held and { catalogId = player.held } or nil
		end,
		RemoveAll = function(player, costs)
			for catalogId, amount in costs do
				if (player.counts[catalogId] or 0) < amount then
					return false, 0
				end
			end
			for catalogId, amount in costs do
				player.counts[catalogId] -= amount
				table.insert(player.removed, catalogId)
				if player.counts[catalogId] == 0 and player.held == catalogId then
					player.held = nil
				end
			end
			return true, 0
		end,
		Notify = function(player, message)
			table.insert(player.notices, message)
		end,
	},
	SurvivalService = {
		Get = function(player)
			return player.rules
		end,
		Humanoid = function(player)
			return player.humanoid
		end,
		SetHealth = function(player, health)
			player.humanoid.Health = health
		end,
	},
	ModifierService = {
		BoostTakes = function(player, boost)
			local running = player.boosts[boost.kind]
			return running == nil or running < boost.amount
		end,
		ApplyBoost = function(player, boost)
			player.boosts[boost.kind] = boost.amount
			return { kind = boost.kind, amount = boost.amount }, true
		end,
	},
})

local HealingService = require(Server.Services.HealingService)
local used = {}
HealingService.Used:Connect(function(player, catalogId)
	table.insert(used, { player, catalogId })
end)

local nextId = 0
local function requestId(): string
	nextId += 1
	return ("00000000-0000-0000-0000-%012d"):format(nextId)
end

-- Starts a use request as the remote does; returns a reader for its answer:
-- nil while it waits, else {ok, reason}.
local function ask(player, catalogId: string, id: string?)
	local answer = nil
	task.spawn(function()
		local ok, reason = HealingService.Use(player, id or requestId(), catalogId)
		answer = { ok, reason }
	end)
	return function()
		return answer
	end
end

local function advance(seconds: number)
	scheduler:Advance(seconds)
	HealingService.Step(scheduler.clock)
end

local function holding(catalogId: string, count: number)
	local player = newPlayer("P" .. tostring(nextId))
	player.counts[catalogId] = count
	player.held = catalogId
	return player
end

-- ConsumeRules ----------------------------------------------------------------------

test("use time: medicine its animation, food and boosts CONSUME_SECONDS", function()
	for _, catalogId in { "BasicMedicine", "Potion" } do
		local item = Consumables.Get(catalogId)
		expectEq(ConsumeRules.Duration(item), item.animationSeconds, catalogId .. " takes its animation")
	end
	expectEq(ConsumeRules.Duration(Consumables.Get("CookedMeat")), GameConstants.CONSUME_SECONDS.Food, "food")
	expectEq(ConsumeRules.Duration(Consumables.Get("GlimmerDraught")), GameConstants.CONSUME_SECONDS.Boost, "boost")
	expect(
		GameConstants.CONSUME_SECONDS.Food > 0.5 and GameConstants.CONSUME_SECONDS.Food < 3,
		"a short, sensible time"
	)
	expectEq(ConsumeRules.Style(Consumables.Get("Redberry")), ConsumeRules.Eat, "berries are eaten")
	expectEq(ConsumeRules.Style(Consumables.Get("Potion")), ConsumeRules.Drink, "potions are drunk")
	expectEq(ConsumeRules.Style(Consumables.Get("SunberryDraught")), ConsumeRules.Drink, "draughts are drunk")
end)

test("the pose rests at both ends, holds the item up in between and stays bounded", function()
	for _, style in { ConsumeRules.Eat, ConsumeRules.Drink } do
		for _, duration in { 0.5, 1.2, 1.5 } do
			local start = ConsumeRules.Pose(style, 0, duration)
			local finish = ConsumeRules.Pose(style, duration, duration)
			local middle, raise, across = ConsumeRules.Pose(style, duration / 2, duration)
			expectEq(start, 0, style .. " starts at rest")
			expectEq(finish, 0, style .. " ends at rest")
			expectEq(middle, 1, style .. " fully raised mid-way")
			expect(raise > 90 and raise < 170 and across > 30 and across < 90, style .. " hand near the mouth")
			local previous = -1
			for step = 0, 10 do
				local blend = ConsumeRules.Pose(style, duration * 0.3 * step / 10, duration)
				expect(blend >= previous - 1e-9 and blend <= 1, style .. " rises smoothly")
				previous = blend
			end
		end
	end
	expectEq(ConsumeRules.Release(1, 0), 1, "an interruption lowers from where it was")
	expectEq(ConsumeRules.Release(1, ConsumeRules.LOWER_SECONDS), 0, "and is down after LOWER_SECONDS")
	expectEq(ConsumeRules.Progress(10, 11, 10.5), 0.5, "half way")
	expectEq(ConsumeRules.Progress(10, 11, 12), 1, "progress caps at 1")
end)

test("interruption: gone, dead, downed, or no longer holding the item", function()
	local cases = {
		{ "still holding it", { present = true, alive = true, downed = false, held = "Redberry" }, nil },
		{ "left", { present = false, alive = true, held = "Redberry" }, "NotInRun" },
		{ "died", { present = true, alive = false, held = "Redberry" }, "NotInRun" },
		{ "downed", { present = true, alive = true, downed = true, held = "Redberry" }, "Downed" },
		{ "put away", { present = true, alive = true, held = nil }, "Interrupted" },
		{ "another slot", { present = true, alive = true, held = "StoneAxe" }, "Interrupted" },
	}
	for _, case in cases do
		expectEq(ConsumeRules.Interruption(case[2], "Redberry"), case[3], case[1])
	end
end)

test("touch icon, bar text and the first-hold hint name the action", function()
	expectEq(ConsumeRules.AttackIcon(Consumables.Get("CookedMeat")), "drumstick", "food")
	expectEq(ConsumeRules.AttackIcon(Consumables.Get("Potion")), "heart", "medicine")
	expectEq(ConsumeRules.BarText(Consumables.Get("CookedMeat")), "Eating Cooked Meat", "eating")
	expectEq(ConsumeRules.BarText(Consumables.Get("Potion")), "Drinking Healing Potion", "drinking")
	local food = Consumables.Get("Redberry")
	expect(string.find(ConsumeRules.HoldHint(food, "mouse"), "^Click to eat") ~= nil, "mouse: click")
	expect(string.find(ConsumeRules.HoldHint(food, "touch"), "attack button") ~= nil, "touch: the attack button")
	expect(
		string.find(ConsumeRules.HoldHint(Consumables.Get("Potion"), "gamepad"), "RT to drink") ~= nil,
		"gamepad: RT"
	)
end)

-- HealingService --------------------------------------------------------------------

test("food is used only when its animation ends, one item per request; clicks meanwhile are Busy", function()
	local player = holding("CookedMeat", 3)
	player.rules.food = 0.5
	local answer = ask(player, "CookedMeat")
	expectEq(answer(), nil, "the request waits for the animation")
	expectEq(player:GetAttribute(ConsumeRules.ITEM_ATTRIBUTE), "CookedMeat", "every client sees what is eaten")
	expectEq(
		player:GetAttribute(ConsumeRules.END_ATTRIBUTE),
		scheduler.clock + GameConstants.CONSUME_SECONDS.Food,
		"and until when"
	)
	advance(GameConstants.CONSUME_SECONDS.Food - 0.1)
	expectEq(answer(), nil, "not yet")
	expectEq(player.counts.CookedMeat, 3, "nothing consumed during the animation")
	expectNear(player.rules.food, 0.5, 1e-9, "nothing applied during the animation")
	advance(0.1 + 1e-6)
	local result = answer()
	expect(result ~= nil and result[1] == true, "applied when it ends")
	expectEq(player.counts.CookedMeat, 2, "exactly one consumed")
	expectNear(player.rules.food, 0.85, 1e-9, "fed")
	expectEq(#player.rules.foodHeals, 1, "the food heal started")
	expectEq(#player.notices, 1, "the toast")
	expectEq(player:GetAttribute(ConsumeRules.ITEM_ATTRIBUTE), nil, "the animation ends")
	advance(5)
	expectEq(player.counts.CookedMeat, 2, "never applied twice")
	expectEq(#player.removed, 1, "one removal in total")

	-- Clicks during the animation are refused as Busy and consume nothing.
	local berries = holding("Redberry", 5)
	local first = ask(berries, "Redberry")
	local second = ask(berries, "Redberry")()
	expect(second ~= nil and second[1] == false and second[2] == "Busy", "the second click is refused at once")
	advance(0.5)
	expect(ask(berries, "Redberry")()[2] == "Busy", "still busy part-way")
	advance(1)
	expect(first()[1] == true, "the first finishes")
	expectEq(berries.counts.Redberry, 4, "one berry for three clicks")
end)

test("medicine heals at once and its animation is the lock (Q64); a request during it consumes nothing", function()
	local player = holding("BasicMedicine", 3)
	player.humanoid.Health = 50
	local answer = ask(player, "BasicMedicine")
	local result = answer()
	expect(result ~= nil and result[1] == true, "answered at once")
	expectEq(player.humanoid.Health, 60, "+10 immediately")
	expectEq(player.counts.BasicMedicine, 2, "one consumed")
	expectEq(player.rules.medicineLockUntil, scheduler.clock + 0.5, "the 0.5 s animation is the lock")
	expectEq(player:GetAttribute(ConsumeRules.END_ATTRIBUTE), scheduler.clock + 0.5, "and is animated")
	advance(0.4)
	local refused = ask(player, "BasicMedicine")()
	expect(refused[1] == false and refused[2] == "Busy", "refused during the medicine animation")
	expectEq(player.counts.BasicMedicine, 2, "and nothing consumed")
	expectEq(player.humanoid.Health, 60, "no extra heal")
	advance(0.1 + 1e-6)
	expectEq(player:GetAttribute(ConsumeRules.ITEM_ATTRIBUTE), nil, "the animation ends")
	expect(ask(player, "BasicMedicine")()[1] == true, "the next one may start when it ends")
	expectEq(player.humanoid.Health, 70, "+10 again")
	expectEq(player.counts.BasicMedicine, 1, "two used")
	advance(1)
	expectEq(player.counts.BasicMedicine, 1, "never applied twice")
end)

test("interrupting medicine stops the animation; the heal stays and the lock runs on", function()
	local player = holding("AdvancedMedicine", 2)
	player.counts.BasicMedicine = 1
	player.humanoid.Health = 50
	expect(ask(player, "AdvancedMedicine")()[1] == true, "drunk")
	advance(0.3)
	player.held = "BasicMedicine"
	advance(0.05)
	expectEq(player:GetAttribute(ConsumeRules.ITEM_ATTRIBUTE), nil, "switching slots stops the animation")
	expectEq(player.humanoid.Health, 75, "the heal already landed")
	local refused = ask(player, "BasicMedicine")()
	expect(refused[1] == false and refused[2] == "Cooldown", "other medicine waits for the lock")
	expectEq(player.counts.BasicMedicine, 1, "and nothing consumed")
	advance(1)
	expect(ask(player, "BasicMedicine")()[1] == true, "usable once the lock ends")
end)

test("a replayed request ID is applied once", function()
	local player = holding("Redberry", 5)
	local id = requestId()
	local answer = ask(player, "Redberry", id)
	advance(2)
	expect(answer()[1] == true, "the first is used")
	local replay = ask(player, "Redberry", id)()
	expect(replay[1] == false and replay[2] == "Duplicate", "the replay is refused")
	expectEq(player.counts.Redberry, 4, "one berry")
end)

test("the item must be carried and held", function()
	local player = holding("Redberry", 5)
	player.held = "StoneAxe"
	local result = ask(player, "Redberry")()
	expect(result[1] == false and result[2] == "NotHeld", "not in hand")
	player.held = "Redberry"
	player.counts.Redberry = 0
	result = ask(player, "Redberry")()
	expect(result[1] == false and result[2] == "NotCarried", "none left")
	result = ask(player, "Wood")()
	expect(result[1] == false and result[2] == "NotConsumable", "not a consumable")
	player:SetAttribute("Downed", true)
	player.counts.Redberry = 1
	result = ask(player, "Redberry")()
	expect(result[1] == false and result[2] == "Downed", "not while downed")
	expectEq(player:GetAttribute(ConsumeRules.ITEM_ATTRIBUTE), nil, "no animation for a refusal")
end)

test("putting it away, switching slots, going down, dying or leaving interrupts it", function()
	-- Each interruption, and the reason the request is refused with.
	local reasons = {
		["put away"] = "Interrupted",
		["another slot"] = "Interrupted",
		downed = "Downed",
		died = "NotInRun",
		left = "NotInRun",
	}
	for name, expected in reasons do
		local player = holding("CookedMeat", 2)
		player.rules.food = 0.5
		local before = #used
		local answer = ask(player, "CookedMeat")
		advance(0.6)
		if name == "put away" then
			player.held = nil
		elseif name == "another slot" then
			player.held = "StoneAxe"
		elseif name == "downed" then
			player:SetAttribute("Downed", true)
		elseif name == "died" then
			player.humanoid.Health = 0
		else
			player.Parent = nil
		end
		advance(0.05)
		local result = answer()
		expect(result ~= nil and result[1] == false and result[2] == expected, name .. " stops it: " .. expected)
		expectEq(player.counts.CookedMeat, 2, name .. ": nothing consumed")
		expectNear(player.rules.food, 0.5, 1e-9, name .. ": not fed")
		expectEq(#player.rules.foodHeals, 0, name .. ": no food heal")
		expectEq(#used, before, name .. ": nothing used")
		if player.Parent then
			expectEq(player:GetAttribute(ConsumeRules.ITEM_ATTRIBUTE), nil, name .. ": the animation stops")
		end
		advance(2)
		expectEq(player.counts.CookedMeat, 2, name .. ": still nothing later")
	end
end)

test("a draught refused when its time is up consumes nothing", function()
	local player = holding("SunberryDraught", 1)
	local answer = ask(player, "SunberryDraught")
	-- A stronger XP boost arrives while drinking (say from a quest reward).
	player.boosts.XP = 1
	advance(2)
	local result = answer()
	expect(result[1] == false and result[2] == "BoostActive", "refused at the end")
	expectEq(player.counts.SunberryDraught, 1, "the draught stays")
	player.boosts.XP = nil
	answer = ask(player, "SunberryDraught")
	advance(2)
	expect(answer()[1] == true, "drunk once nothing stronger runs")
	expectEq(player.boosts.XP, 0.25, "the boost started")
	expectEq(player.counts.SunberryDraught, 0, "and the draught is used")
end)

test("the last one used leaves the hand empty; the Used signal fires once per item", function()
	local player = holding("Sweetberry", 1)
	local before = #used
	local answer = ask(player, "Sweetberry")
	advance(2)
	expect(answer()[1] == true, "eaten")
	expectEq(player.held, nil, "nothing left in hand")
	expectEq(#used, before + 1, "one Used")
	local result = ask(player, "Sweetberry")()
	expect(result[1] == false and result[2] == "NotCarried", "nothing more to eat")
	expect(not HealingService.IsUsing(player), "idle")
end)
