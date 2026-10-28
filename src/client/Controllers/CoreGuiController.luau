-- Hides Roblox's own player list in both places (GDD §46): Tab is the game's
-- Backpack key, which opens the inventory (the backpack in a run, the backpack
-- and vault panel in the lobby) instead of the list.

local StarterGui = game:GetService("StarterGui")

local CoreGuiController = {}

-- The core scripts can refuse the call for a moment while they load.
CoreGuiController.ATTEMPTS = 10

function CoreGuiController.Start()
	task.spawn(function()
		for _ = 1, CoreGuiController.ATTEMPTS do
			local ok = pcall(StarterGui.SetCoreGuiEnabled, StarterGui, Enum.CoreGuiType.PlayerList, false)
			if ok then
				return
			end
			task.wait(1)
		end
		warn("[CoreGui] could not hide the player list")
	end)
end

return CoreGuiController
