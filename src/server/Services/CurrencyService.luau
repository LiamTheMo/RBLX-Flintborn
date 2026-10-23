-- Coins and Gems (GDD §10, Q90–94). Balances live in the profile and only change
-- inside once-only operations; they replicate to their owner as attributes and
-- never drop on death. Also the shared helper the economy services use to run a
-- client request as an operation keyed by its nonce.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Validation = require(ReplicatedStorage.Shared.Data.Validation)
local ProfileService = require(script.Parent.ProfileService)

local CurrencyService = {}

function CurrencyService.Publish(player: Player)
	local profile = ProfileService.GetProfile(player)
	if profile and player.Parent then
		player:SetAttribute("Coins", profile.currency.coins)
		player:SetAttribute("Gems", profile.currency.gems)
		player:SetAttribute("VaultTier", profile.vault.upgradeTier or 0)
	end
end

-- Runs `apply(profile) -> (ok, resultOrReason)` once for `prefix .. nonce`.
-- Returns (ok, resultOrReason) and publishes the wallet.
function CurrencyService.Run(player: Player, prefix: string, nonce: any, kind: string, apply)
	if not Validation.IsId(nonce) or #nonce > 50 then
		return false, "BadRequest"
	end
	local ok, result = ProfileService.RunOperation(player, prefix .. nonce, kind, function(profile)
		local success, value = apply(profile)
		if not success then
			error(value, 0)
		end
		return value
	end)
	CurrencyService.Publish(player)
	if not ok then
		return false, tostring(result)
	end
	return true, result
end

function CurrencyService.Start()
	ProfileService.ProfileLoaded:Connect(CurrencyService.Publish)
end

return CurrencyService
