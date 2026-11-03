-- Hides Roblox's own player list, backpack and health bar in both places (GDD
-- §46). The game has its own hotbar and inventory window (the Backpack key, B by
-- default), so the default backpack, which ` would open, and its hotbar are
-- turned off; the HUD draws its own health bar.

local StarterGui = game:GetService("StarterGui")

local CoreGuiController = {}

-- The core scripts can refuse the call for a moment while they load.
CoreGuiController.ATTEMPTS = 10

CoreGuiController.HIDDEN = { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Backpack, Enum.CoreGuiType.Health }

function CoreGuiController.Start()
	for _, coreGui in CoreGuiController.HIDDEN do
		task.spawn(function()
			for _ = 1, CoreGuiController.ATTEMPTS do
				local ok = pcall(StarterGui.SetCoreGuiEnabled, StarterGui, coreGui, false)
				if ok then
					return
				end
				task.wait(1)
			end
			warn("[CoreGui] could not hide the " .. coreGui.Name)
		end)
	end
end

return CoreGuiController
