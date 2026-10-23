-- Quests (GDD §10.1, Q90–92, Q117, Q121). Progress counts verified actions in
-- either place (the XP action keys plus extractions) and saves as it happens;
-- rewards are claimed once per period through an operation keyed by quest and day.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local EconomyRules = require(ReplicatedStorage.Shared.Economy.EconomyRules)
local QuestCatalog = require(ReplicatedStorage.Shared.Economy.QuestCatalog)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local CurrencyService = require(script.Parent.CurrencyService)
local ProfileService = require(script.Parent.ProfileService)
local ProgressionService = require(script.Parent.ProgressionService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local QuestService = {}

local function view(player: Player)
	local profile = ProfileService.GetProfile(player)
	return profile and EconomyRules.QuestView(profile, os.time()) or nil
end

function QuestService.Start()
	local function record(player: Player, action: string)
		ProfileService.Mutate(player, function(profile)
			EconomyRules.RecordQuest(profile, action, os.time())
		end)
	end
	ProgressionService.Acted:Connect(record)
	WorldAdmissionService.RunEnded:Connect(function(player, reason)
		if reason == "Extracted" then
			record(player, "Extract")
		end
	end)
	Remotes.Get("QuestView").OnServerInvoke = view
	Remotes.Get("QuestClaim").OnServerInvoke = function(player, questId)
		local quest = QuestCatalog.Get(questId)
		if quest == nil then
			return false, "BadRequest"
		end
		local key = quest.id .. "-" .. QuestCatalog.Period(quest, os.time())
		local ok, result = CurrencyService.Run(player, "quest:", key, "QuestReward", function(profile)
			return EconomyRules.ClaimQuest(profile, questId, os.time())
		end)
		ProgressionService.Publish(player)
		return ok, result
	end
end

return QuestService
