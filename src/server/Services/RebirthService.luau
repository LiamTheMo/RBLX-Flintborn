-- Rebirth and the perk shop (GDD §37, Q81–89). Lobby only. The preview spells out
-- what resets (the general level only), what is kept and what is gained before the
-- player confirms. Rebirths and perk purchases are once-only operations keyed by
-- the client's nonce, so a retry never grants tokens or ranks twice.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local ProgressionRules = require(ReplicatedStorage.Shared.Progression.ProgressionRules)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Validation = require(ReplicatedStorage.Shared.Data.Validation)
local ProfileService = require(script.Parent.ProfileService)
local ProgressionService = require(script.Parent.ProgressionService)

local RebirthService = {}

local function preview(player: Player)
	local profile = ProfileService.GetProfile(player)
	if profile == nil then
		return nil
	end
	local view = ProgressionRules.Preview(profile)
	local ok, reason = ProgressionRules.CanRebirth(profile)
	view.eligible = ok
	view.reason = reason
	return view
end

local function run(player: Player, prefix: string, nonce: any, kind: string, apply)
	if not Validation.IsId(nonce) or #nonce > 50 then
		return false, "BadRequest"
	end
	local ok, result = ProfileService.RunOperation(player, prefix .. nonce, kind, function(profile)
		local success, reason = apply(profile)
		if not success then
			error(reason, 0)
		end
	end)
	if not ok then
		return false, tostring(result)
	end
	ProfileService.SaveNow(player)
	ProgressionService.Publish(player)
	return true, nil
end

function RebirthService.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	Remotes.Get("RebirthPreview").OnServerInvoke = preview
	Remotes.Get("Rebirth").OnServerInvoke = function(player, nonce)
		return run(player, "rebirth:", nonce, "Rebirth", ProgressionRules.Rebirth)
	end
	Remotes.Get("BuyPerk").OnServerInvoke = function(player, perkId, nonce)
		return run(player, "perk:", nonce, "PerkPurchase", function(profile)
			return ProgressionRules.BuyPerk(profile, perkId)
		end)
	end
end

return RebirthService
