-- Server-side telemetry (GDD §26.3, §7.5). Records runs, verified actions
-- (harvests, crafts, Forge operations, events, creatures, bosses, PvP), item
-- releases, raids and the Coin/Gem faucets and sinks as Roblox Analytics custom
-- and economy events. Bounded: actions are aggregated per player and flushed each
-- minute. No personal information is logged (§23.3).

local AnalyticsService = game:GetService("AnalyticsService")
local Players = game:GetService("Players")

local BuildingService = require(script.Parent.BuildingService)
local CurrencyService = require(script.Parent.CurrencyService)
local DropService = require(script.Parent.DropService)
local ProgressionService = require(script.Parent.ProgressionService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local Analytics = {}

Analytics.FLUSH_SECONDS = 60

-- Server-wide counters, also handy when debugging a live server.
Analytics.Counters = {}

local pending = {}

local function count(key: string, amount: number?)
	Analytics.Counters[key] = (Analytics.Counters[key] or 0) + (amount or 1)
end

local function custom(player: Player, name: string, value: number?)
	pcall(function()
		AnalyticsService:LogCustomEvent(player, name, value or 1)
	end)
end

local function aggregate(player: Player, name: string)
	local perPlayer = pending[player]
	if perPlayer == nil then
		perPlayer = {}
		pending[player] = perPlayer
	end
	perPlayer[name] = (perPlayer[name] or 0) + 1
	count(name)
end

local function flush()
	for player, counts in pending do
		if player.Parent then
			for name, value in counts do
				custom(player, name, value)
			end
		end
	end
	table.clear(pending)
end

function Analytics.Start()
	WorldAdmissionService.RunStarted:Connect(function(player)
		count("RunStarted")
		custom(player, "RunStarted")
	end)
	WorldAdmissionService.RunEnded:Connect(function(player, reason)
		count("RunEnded:" .. reason)
		if player.Parent then
			custom(player, "RunEnded_" .. reason)
		end
	end)
	ProgressionService.Acted:Connect(function(player, action)
		aggregate(player, "Action_" .. action)
	end)
	DropService.Released:Connect(function(player, item)
		aggregate(player, if item.permanent then "PermanentReleased" else "ItemReleased")
	end)
	BuildingService.Removing:Connect(function(_, reason)
		count("Structure_" .. reason)
	end)
	CurrencyService.Changed:Connect(function(player, kind, coins, gems, coinBalance, gemBalance)
		for _, entry in { { "Coins", coins, coinBalance }, { "Gems", gems, gemBalance } } do
			local currency, delta, balance = entry[1], entry[2], entry[3]
			if delta ~= 0 then
				count(currency .. (if delta > 0 then "_Source_" else "_Sink_") .. kind, math.abs(delta))
				pcall(function()
					AnalyticsService:LogEconomyEvent(
						player,
						if delta > 0 then Enum.AnalyticsEconomyFlowType.Source else Enum.AnalyticsEconomyFlowType.Sink,
						currency,
						math.abs(delta),
						balance,
						kind
					)
				end)
			end
		end
	end)
	Players.PlayerRemoving:Connect(function(player)
		local counts = pending[player]
		if counts then
			for name, value in counts do
				custom(player, name, value)
			end
			pending[player] = nil
		end
	end)
	task.spawn(function()
		while true do
			task.wait(Analytics.FLUSH_SECONDS)
			flush()
		end
	end)
end

return Analytics
