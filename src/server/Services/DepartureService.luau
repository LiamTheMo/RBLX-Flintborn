-- Death and active departure (GDD §29, Q156–157). When an at-risk player dies or
-- leaves the world any way at all, their ordinary carried items go into ONE
-- lootable body that lasts exactly 600 s; owned Permanent items go back to their
-- lobby backpack instead. Bodies are looted item by item. World place only.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local CrashRecoveryRules = require(ReplicatedStorage.Shared.Recovery.CrashRecoveryRules)
local DeathRules = require(ReplicatedStorage.Shared.Admission.DeathRules)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local ProfileSchema = require(ReplicatedStorage.Shared.Data.ProfileSchema)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Validation = require(ReplicatedStorage.Shared.Data.Validation)
local DownedService = require(script.Parent.DownedService)
local InventoryService = require(script.Parent.InventoryService)
local ProfileService = require(script.Parent.ProfileService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local DepartureService = {}

DepartureService.LOOT_RANGE = 12

local bodies = {}
local lastPositions = {}
local handled = {}

local function view(contents)
	local entries = {}
	for index, item in contents do
		local def = ItemCatalog.Get(item.catalogId)
		table.insert(entries, {
			index = index,
			name = def and def.name or item.catalogId,
			rarity = def and def.rarity or "Common",
			quantity = item.quantity,
			qualityRoll = item.qualityRoll,
		})
	end
	return entries
end

local function canLoot(player: Player, body): boolean
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	return root ~= nil
		and humanoid ~= nil
		and humanoid.Health > 0
		and WorldAdmissionService.IsAtRisk(player)
		and not DownedService.IsDowned(player)
		and (root.Position - body.part.Position).Magnitude <= DepartureService.LOOT_RANGE
end

local function createBody(position: Vector3, contents, ownerName: string)
	local id = HttpService:GenerateGUID(false)
	local part = Instance.new("Part")
	part.Name = "Body"
	part.Anchored = true
	part.CanCollide = false
	part.Size = Vector3.new(2, 1, 5)
	part.Color = Color3.fromRGB(90, 76, 64)
	part.CFrame = CFrame.new(position - Vector3.new(0, 2.5, 0))
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Loot"
	prompt.ObjectText = ownerName .. "'s body"
	prompt.HoldDuration = 0.5
	prompt.MaxActivationDistance = DepartureService.LOOT_RANGE - 2
	prompt.RequiresLineOfSight = false
	prompt.Parent = part
	part.Parent = workspace
	local body = { id = id, part = part, contents = contents, createdAt = os.clock() }
	bodies[id] = body
	prompt.Triggered:Connect(function(looter)
		if bodies[id] and canLoot(looter, body) then
			Remotes.Get("CorpseOpened"):FireClient(looter, id, view(body.contents))
		end
	end)
	-- The body and anything left in it disappear exactly 600 s after creation.
	task.delay(DeathRules.BODY_SECONDS, function()
		bodies[id] = nil
		part:Destroy()
	end)
	return body
end

local function take(looter: Player, bodyId: any, index: any)
	if not Validation.IsId(bodyId) then
		return false, "BadRequest"
	end
	local body = bodies[bodyId]
	if body == nil then
		return false, "Gone"
	end
	if not canLoot(looter, body) then
		return false, "TooFar"
	end
	local entry = body.contents[index]
	if entry == nil then
		return false, "Empty"
	end
	local copy = ProfileSchema.DeepCopy(entry)
	if copy.instanceId then
		-- A looted unique item now belongs to the looter (still unsecured).
		copy.ownerId = looter.UserId
	end
	local remaining = InventoryService.Add(looter, copy)
	if copy.instanceId then
		if remaining > 0 then
			return false, "NoRoom"
		end
		DeathRules.Take(body.contents, index)
	elseif remaining > 0 then
		entry.quantity = remaining
	else
		DeathRules.Take(body.contents, index)
	end
	Remotes.Get("CorpseOpened"):FireClient(looter, bodyId, view(body.contents))
	return true, nil
end

-- One body per run, whether the player died or left. Kept Permanent items and
-- the run's "Ended" crash receipt are written in one operation, synchronously,
-- so a leaving player's release save always includes them.
local function depart(player: Player, position: Vector3?)
	if handled[player] then
		return
	end
	handled[player] = true
	local items = ProfileSchema.DeepCopy(InventoryService.Items(player))
	local bodyItems, kept = DeathRules.Split(items)
	local ok, err = ProfileService.RunOperation(
		player,
		"depart:" .. HttpService:GenerateGUID(false),
		"PermanentKept",
		function(profile)
			for _, item in kept do
				item.location = "LobbyBackpack"
				table.insert(profile.lobbyBackpack.slots, item)
			end
			CrashRecoveryRules.MarkEnded(profile, os.time())
		end
	)
	if not ok then
		warn(("[DepartureService] Could not settle departure for %s: %s"):format(player.Name, tostring(err)))
	end
	-- Never lose a body for lack of a position (a logout right after spawning).
	local at = position or lastPositions[player]
	if at == nil then
		warn("[DepartureService] No known position for " .. player.Name .. "; placing the body at the origin")
		at = Vector3.new(0, 5, 0)
	end
	if #bodyItems > 0 then
		createBody(at, bodyItems, player.DisplayName)
	end
	if player.Parent then
		Remotes.Get("DeathSummary"):FireClient(player, { dropped = #bodyItems, kept = #kept })
	end
end

function DepartureService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	WorldAdmissionService.RunStarted:Connect(function(player, character)
		handled[player] = nil
		-- The confirmed spawn point is the first known position of every run.
		lastPositions[player] = character and character:GetPivot().Position or nil
	end)
	WorldAdmissionService.Death:Connect(depart)
	WorldAdmissionService.ActiveDeparture:Connect(function(player)
		local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
		depart(player, root and root.Position or nil)
	end)
	Remotes.Handle("CorpseTake", take)
	local elapsed = 0
	RunService.Heartbeat:Connect(function(dt)
		elapsed += dt
		if elapsed < 0.5 then
			return
		end
		elapsed = 0
		for _, player in Players:GetPlayers() do
			local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
			if root and WorldAdmissionService.IsAtRisk(player) then
				lastPositions[player] = root.Position
			end
		end
	end)
	Players.PlayerRemoving:Connect(function(player)
		task.defer(function()
			lastPositions[player] = nil
			handled[player] = nil
		end)
	end)
end

return DepartureService
