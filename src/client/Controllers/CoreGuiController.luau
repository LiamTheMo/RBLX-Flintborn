-- Hides Roblox's own player list, backpack and health bar in both places (GDD
-- §46). The game has its own hotbar and inventory window (the Backpack key, B by
-- default), so the default backpack, which ` would open, and its hotbar are
-- turned off; the HUD draws its own health bar. Roblox's overhead health bars
-- (over any hurt character) are off for this player too, everywhere and from the
-- start: the only bar over a player is the game's own (Hud/OverheadHealth).

local Players = game:GetService("Players")
local StarterGui = game:GetService("StarterGui")

local CoreGuiController = {}

-- The core scripts can refuse the call for a moment while they load.
CoreGuiController.ATTEMPTS = 10

CoreGuiController.HIDDEN = { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Backpack, Enum.CoreGuiType.Health }

function CoreGuiController.Start()
	-- 0 = this player never sees Roblox's overhead health bar on any humanoid.
	local ok, err = pcall(function()
		Players.LocalPlayer.HealthDisplayDistance = 0
	end)
	if not ok then
		warn("[CoreGui] could not hide Roblox's overhead health bars: " .. tostring(err))
	end
	for _, coreGui in CoreGuiController.HIDDEN do
		task.spawn(function()
			for _ = 1, CoreGuiController.ATTEMPTS do
				local hidden = pcall(StarterGui.SetCoreGuiEnabled, StarterGui, coreGui, false)
				if hidden then
					return
				end
				task.wait(1)
			end
			warn("[CoreGui] could not hide the " .. coreGui.Name)
		end)
	end
end

return CoreGuiController
