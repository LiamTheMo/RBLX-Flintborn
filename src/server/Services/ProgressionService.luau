-- General XP, levels and masteries (GDD §33, Q52, Q69–80). Every grant comes from
-- a server-verified action, passes through the one modifier pipeline, and is
-- written to the profile the moment it is earned, so dying never takes it back.
-- Each run's XP is tracked for the Center extraction bonus. In the lobby, players
-- show their level and best mastery title over their heads.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local LevelCurve = require(ReplicatedStorage.Shared.Progression.LevelCurve)
local MasteryCatalog = require(ReplicatedStorage.Shared.Progression.MasteryCatalog)
local ModifierRules = require(ReplicatedStorage.Shared.Progression.ModifierRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local ProgressionRules = require(ReplicatedStorage.Shared.Progression.ProgressionRules)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local BossService = require(script.Parent.BossService)
local CombatService = require(script.Parent.CombatService)
local ModifierService = require(script.Parent.ModifierService)
local NpcService = require(script.Parent.NpcService)
local ProfileService = require(script.Parent.ProfileService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local ProgressionService = {}

-- Base XP per verified action (placeholders).
ProgressionService.XP = {
	Harvest = 2,
	CropHarvest = 10,
	Craft = 5,
	Forge = 15,
	RareNode = 25,
	Cache = 40,
	MeteorChunk = 15,
	Enemy = 10,
	Elite = 30,
	Boss = 100,
	Guardian = 300,
	PvpKill = 20,
}

-- The same victim credits the same attacker at most once per window (alt farming).
ProgressionService.PVP_REPEAT_SECONDS = 1800

-- What the client shows: level bar, masteries with next milestones, rebirth state.
function ProgressionService.Snapshot(player: Player)
	local profile = ProfileService.GetProfile(player)
	if profile == nil then
		return nil
	end
	local progression = profile.progression
	local masteries = {}
	for _, name in MasteryCatalog.TRACKS do
		local entry = progression.masteryTracks[name] or { level = 0, counters = {} }
		local nextLevel = math.min(entry.level + 1, MasteryCatalog.MAX_LEVEL)
		local milestones = MasteryCatalog.MILESTONES[name]
		local nextTitle = nil
		for level = entry.level + 1, MasteryCatalog.MAX_LEVEL do
			if milestones[level] then
				nextTitle = ("%s at level %d"):format(milestones[level], level)
				break
			end
		end
		table.insert(masteries, {
			track = name,
			level = entry.level,
			xp = entry.counters.xp or 0,
			nextXp = if entry.level >= MasteryCatalog.MAX_LEVEL then nil else MasteryCatalog.THRESHOLDS[nextLevel],
			nextReward = nextTitle,
		})
	end
	local titles = {}
	for title in progression.titles do
		table.insert(titles, title)
	end
	table.sort(titles)
	local rebirth = profile.rebirth
	return {
		level = progression.level,
		xp = progression.xp,
		xpToNext = if progression.level >= LevelCurve.MAX_LEVEL then nil else LevelCurve.XpForLevel(progression.level),
		masteries = masteries,
		titles = titles,
		rebirth = {
			count = rebirth.count,
			tokens = rebirth.tokens,
			ownedPerks = rebirth.ownedPerks,
			legendaries = rebirth.legendariesSinceRebirth or 0,
			legendariesNeeded = ProgressionRules.RequiredLegendaries(rebirth.count),
			levelNeeded = ProgressionRules.REBIRTH_LEVEL,
		},
		premium = ModifierService.IsPremium(player),
		boosterUntil = profile.boosters.xpUntil or 0,
	}
end

-- The best title earned so far, for the lobby name plate.
local function bestTitle(profile): string?
	local best, bestLevel = nil, 0
	for _, milestones in MasteryCatalog.MILESTONES do
		for level, title in milestones do
			if profile.progression.titles[title] and level > bestLevel then
				best, bestLevel = title, level
			end
		end
	end
	return best
end

local function nameplate(player: Player)
	if not PlaceConfig.IsLobby() then
		return
	end
	local profile = ProfileService.GetProfile(player)
	local head = player.Character and player.Character:FindFirstChild("Head")
	if profile == nil or head == nil then
		return
	end
	local billboard = head:FindFirstChild("FlintbornNameplate")
	if billboard == nil then
		billboard = Instance.new("BillboardGui")
		billboard.Name = "FlintbornNameplate"
		billboard.Size = UDim2.fromOffset(200, 24)
		billboard.StudsOffset = Vector3.new(0, 2.5, 0)
		billboard.MaxDistance = 80
		local label = Instance.new("TextLabel")
		label.Name = "Text"
		label.Size = UDim2.fromScale(1, 1)
		label.BackgroundTransparency = 1
		label.TextColor3 = Color3.fromRGB(255, 220, 160)
		label.TextStrokeTransparency = 0.3
		label.Font = Enum.Font.GothamBold
		label.TextSize = 14
		label.Parent = billboard
		billboard.Parent = head
	end
	local title = bestTitle(profile)
	billboard.Text.Text = ("Lv %d%s%s"):format(
		profile.progression.level,
		if profile.rebirth.count > 0 then (" ✦%d"):format(profile.rebirth.count) else "",
		if title then " · " .. title else ""
	)
end

function ProgressionService.Publish(player: Player)
	local view = ProgressionService.Snapshot(player)
	if view and player.Parent then
		Remotes.Get("ProgressionChanged"):FireClient(player, view)
		player:SetAttribute("Level", view.level)
		nameplate(player)
	end
end

-- Fires (player, action, detail) for every verified action that grants XP; quests
-- count progress from it. `action` is a key of ProgressionService.XP.
ProgressionService.Acted = Signal.new()

-- Grants general XP for a verified action (a key of ProgressionService.XP),
-- through the modifier pipeline.
function ProgressionService.GrantXp(player: Player, action: string, reason: string)
	local base = ProgressionService.XP[action]
	assert(base, "Unknown XP action " .. tostring(action))
	ProgressionService.Acted:Fire(player, action, reason)
	local amount = ModifierRules.Final(base, ModifierService.Get(player, "Xp"))
	local gained = 0
	if
		not ProfileService.Mutate(player, function(profile)
			gained = ProgressionRules.GrantXp(profile, amount)
		end)
	then
		return
	end
	Remotes.Get("XpGained"):FireClient(player, { amount = amount, reason = reason, levelUp = gained > 0 })
	ProgressionService.Publish(player)
end

-- Counts verified actions on a mastery track.
function ProgressionService.GrantMastery(player: Player, track: string, actions: number)
	local gained = 0
	if
		not ProfileService.Mutate(player, function(profile)
			gained = ProgressionRules.GrantMastery(profile, track, actions)
		end)
	then
		return
	end
	if gained > 0 then
		local profile = ProfileService.GetProfile(player)
		Remotes.Get("XpGained"):FireClient(player, {
			amount = 0,
			reason = ("%s mastery %d"):format(track, profile.progression.masteryTracks[track].level),
			levelUp = true,
		})
	end
	ProgressionService.Publish(player)
end

-- A player kill: PvP mastery and XP, never twice for the same pair in the window.
-- The window lives in the attacker's profile, so it survives server hops.
local function creditKill(attacker: Player, victim: Player)
	local credited = false
	ProfileService.Mutate(attacker, function(profile)
		credited = ProgressionRules.CreditPvp(profile, victim.UserId, os.time(), ProgressionService.PVP_REPEAT_SECONDS)
	end)
	if not credited then
		return
	end
	ProgressionService.GrantXp(attacker, "PvpKill", "Player defeated")
	ProgressionService.GrantMastery(attacker, "PvP", 1)
end

function ProgressionService.Start()
	Remotes.Handle("ProgressionSnapshot", ProgressionService.Snapshot)
	ProfileService.ProfileLoaded:Connect(function(player)
		ProgressionService.Publish(player)
	end)
	if PlaceConfig.IsLobby() then
		Players.PlayerAdded:Connect(function(player)
			player.CharacterAdded:Connect(function()
				task.wait(0.5)
				nameplate(player)
			end)
		end)
		for _, player in Players:GetPlayers() do
			player.CharacterAdded:Connect(function()
				task.wait(0.5)
				nameplate(player)
			end)
		end
		return
	end
	if not PlaceConfig.IsWorld() then
		return
	end
	WorldAdmissionService.RunStarted:Connect(function(player, _, _, runId)
		ProfileService.Mutate(player, function(profile)
			local run = profile.progression.currentRun
			-- The Play's consume normally recorded this run already (crash recovery).
			if run == nil or runId == nil or run.runId ~= runId then
				ProgressionRules.StartRun(profile, runId or HttpService:GenerateGUID(false))
			end
		end)
	end)
	NpcService.Died:Connect(function(npc)
		local killer = npc.lastAttacker
		if killer and killer.Parent then
			ProgressionService.GrantXp(killer, if npc.elite then "Elite" else "Enemy", npc.name .. " defeated")
		end
	end)
	-- Only players who damaged the boss share its XP (and the quest progress it
	-- counts); standing nearby earns nothing.
	BossService.Defeated:Connect(function(boss)
		local action = if boss.source == "Guardian" then "Guardian" else "Boss"
		local contributors = boss.contributors or {}
		for _, player in Players:GetPlayers() do
			if contributors[player] and WorldAdmissionService.IsAtRisk(player) then
				ProgressionService.GrantXp(player, action, boss.def.name .. " defeated")
			end
		end
	end)
	CombatService.Damaged:Connect(function(attacker, target, _, newHealth)
		if newHealth <= 0 then
			creditKill(attacker, target)
		end
	end)
end

return ProgressionService
