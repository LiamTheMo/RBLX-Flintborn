-- TEMPORARY diagnostic: the character's textures and face, and the lobby map's
-- palette, load on the server but not on the user's phone. For 90 seconds after
-- joining, a small readout lists each image with the fetch status this client
-- reports, so one screenshot shows which images fail and how. Remove once the
-- cause is found.

local ContentProvider = game:GetService("ContentProvider")
local Players = game:GetService("Players")

local AssetProbeController = {}

local SHOW_SECONDS = 90
-- The old palette loads on phones; the newer upload of the same picture did not.
local CONTROLS = {
	{ "palette 10-24 (control)", "rbxassetid://81552715112600" },
	{ "palette 10-26", "rbxassetid://110506060164856" },
}

local function characterImages(): { { string } }
	local list = {}
	local character = Players.LocalPlayer.Character
	if character == nil then
		return list
	end
	for _, d in character:GetDescendants() do
		if d:IsA("MeshPart") and d.TextureID ~= "" then
			table.insert(list, { d.Name, d.TextureID })
		elseif d:IsA("Decal") and d.Texture ~= "" then
			table.insert(list, { "decal " .. d.Name, d.Texture })
		end
	end
	return list
end

local function mapImage(): { string }?
	local map = workspace:FindFirstChild("LobbyMap")
	if map == nil then
		return nil
	end
	for _, d in map:GetDescendants() do
		if d:IsA("MeshPart") and d.TextureID ~= "" then
			return { "map uses", d.TextureID }
		end
	end
	return nil
end

function AssetProbeController.Start()
	task.spawn(function()
		local player = Players.LocalPlayer
		if player.Character == nil then
			player.CharacterAdded:Wait()
		end
		task.wait(4) -- the outfit service recolours the shorts just after spawning
		local gui = Instance.new("ScreenGui")
		gui.Name = "AssetProbe"
		gui.DisplayOrder = 100
		gui.ResetOnSpawn = false
		local label = Instance.new("TextLabel")
		label.AnchorPoint = Vector2.new(0.5, 0)
		label.Position = UDim2.new(0.5, 0, 0, 70)
		label.Size = UDim2.new(0, 520, 0, 0)
		label.AutomaticSize = Enum.AutomaticSize.Y
		label.BackgroundColor3 = Color3.new(0, 0, 0)
		label.BackgroundTransparency = 0.25
		label.TextColor3 = Color3.new(1, 1, 1)
		label.Font = Enum.Font.Code
		label.TextSize = 13
		label.TextXAlignment = Enum.TextXAlignment.Left
		label.TextWrapped = true
		label.Parent = gui
		gui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")

		local entries = {}
		for _, e in characterImages() do
			table.insert(entries, e)
		end
		local map = mapImage()
		if map then
			table.insert(entries, map)
		end
		for _, e in CONTROLS do
			table.insert(entries, e)
		end
		-- A fresh request for each, recording the status the engine reports.
		local preload = {}
		for _, e in entries do
			local id = e[2]
			task.spawn(function()
				local ok, err = pcall(function()
					ContentProvider:PreloadAsync({ id }, function(_, status)
						preload[id] = status.Name
					end)
				end)
				if not ok then
					preload[id] = "error: " .. tostring(err)
				end
			end)
		end

		local started = os.clock()
		while os.clock() - started < SHOW_SECONDS do
			local lines = { "IMAGE CHECK (screenshot this)  " .. math.floor(SHOW_SECONDS - (os.clock() - started)) .. "s" }
			for _, e in entries do
				local id = e[2]
				local now = ContentProvider:GetAssetFetchStatus(id).Name
				table.insert(lines, string.format("%s  %s  now=%s  preload=%s", e[1], string.match(id, "%d+") or id, now,
					preload[id] or "waiting"))
			end
			label.Text = table.concat(lines, "\n")
			task.wait(1)
		end
		gui:Destroy()
	end)
end

return AssetProbeController
