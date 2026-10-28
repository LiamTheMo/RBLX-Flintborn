-- Dropping and picking up items in a world (GDD §17.1–17.2, Q13, Q156). A dropped
-- item lies on the ground until someone claims it, exactly once. Picking up a
-- Permanent item transfers ownership; the former owner has no way back to it.
-- Ordinary drops vanish after the body timer; Permanent drops stay until the world
-- resets, when anything unclaimed is lost. Gathered drops from node hits (GDD §53)
-- follow GroundDrops instead: the hitting player's for 10 s, gone after 2 minutes,
-- collected by walking over them or with Interact, within reach. World place only.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local GroundDrops = require(ReplicatedStorage.Shared.Resources.GroundDrops)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PermanentRules = require(ReplicatedStorage.Shared.Items.PermanentRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local ProfileSchema = require(ReplicatedStorage.Shared.Data.ProfileSchema)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local DownedService = require(script.Parent.DownedService)
local InventoryService = require(script.Parent.InventoryService)
local ProfileService = require(script.Parent.ProfileService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local DropService = {}

-- Fires (player, item) when a carried item is handed to the world or a chest.
DropService.Released = Signal.new()

DropService.ORDINARY_SECONDS = GameConstants.CORPSE_SECONDS

local drops = {}

local function canAct(player: Player): boolean
	local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	return WorldAdmissionService.IsAtRisk(player)
		and humanoid ~= nil
		and humanoid.Health > 0
		and not DownedService.IsDowned(player)
end

local function label(item): string
	local def = ItemCatalog.Get(item.catalogId)
	local name = def and def.name or item.catalogId
	return (item.permanent and "★ " or "") .. name .. (item.quantity and (" ×" .. item.quantity) or "")
end

local function updateLedger(player: Player, kind: string, apply)
	ProfileService.RunOperation(player, kind .. ":" .. HttpService:GenerateGUID(false), kind, apply)
end

-- Lets go of an item someone carried (dropped or stored in a public chest).
-- Releasing a Permanent item gives up ownership until it is picked up again (Q13).
function DropService.Release(player: Player, item, location: string)
	item.location = location
	DropService.Released:Fire(player, item)
	if item.permanent then
		updateLedger(player, "PermanentDropped", function(profile)
			profile.permanentItems[item.instanceId] = nil
		end)
	end
end

-- A copy of `item` as it would be once `player` claims it.
function DropService.PrepareClaim(player: Player, item)
	local copy = ProfileSchema.DeepCopy(item)
	if copy.permanent then
		PermanentRules.Transfer(copy, player.UserId)
		if item.ownerId == player.UserId then
			-- The owner took their own item back: no new owner, no version bump.
			copy.ownershipVersion = item.ownershipVersion
		end
	elseif copy.instanceId then
		copy.ownerId = player.UserId
		copy.location = "Carried"
	end
	return copy
end

-- Records a claimed Permanent item in the new owner's ledger.
function DropService.FinishClaim(player: Player, copy, previousOwnerId: number?)
	if not copy.permanent then
		return
	end
	updateLedger(player, "PermanentPickedUp", function(profile)
		profile.permanentItems[copy.instanceId] = PermanentRules.LedgerEntry(copy, os.time())
	end)
	if previousOwnerId ~= player.UserId then
		InventoryService.Notify(player, "You now own this Permanent " .. label(copy):gsub("^★ ", "") .. ".")
	end
end

local pickUp

-- Places an item on the ground until someone claims it. `gathered` marks a node
-- hit's drop (GDD §53): `ownerId` is the hitting player's UserId and `color` its
-- material's look; it follows the GroundDrops rules instead of the body timer.
function DropService.Spawn(item, position: Vector3, gathered: { ownerId: number, color: Color3? }?)
	local id = HttpService:GenerateGUID(false)
	local size = if gathered then 1 else 1.4
	local part = Instance.new("Part")
	part.Name = "DroppedItem"
	part.Size = Vector3.new(size, size, size)
	part.Anchored = true
	part.CanCollide = false
	part.Material = if item.permanent then Enum.Material.Neon else Enum.Material.SmoothPlastic
	part.Color = if item.permanent
		then Color3.fromRGB(255, 200, 90)
		else gathered and gathered.color or Color3.fromRGB(170, 150, 120)
	part.CFrame = CFrame.new(position + Vector3.new(0, size / 2, 0))
	-- Many small gathered drops never block rays, placement or line of sight.
	part.CanQuery = gathered == nil
	part.Parent = workspace
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Pick up"
	prompt.ObjectText = label(item)
	prompt.HoldDuration = if gathered then 0 else 0.3
	prompt.MaxActivationDistance = if gathered then GroundDrops.PICKUP_RANGE - 4 else 8
	prompt.RequiresLineOfSight = gathered == nil
	prompt.Parent = part
	local drop = {
		id = id,
		item = item,
		part = part,
		prompt = prompt,
		rules = if gathered then GroundDrops.New(gathered.ownerId, os.clock()) else nil,
	}
	drops[id] = drop
	prompt.Triggered:Connect(function(player)
		pickUp(player, id, false)
	end)
	if gathered then
		-- Walking over it collects it (server-checked like the prompt).
		part.Touched:Connect(function(hit)
			local player = hit.Parent and Players:GetPlayerFromCharacter(hit.Parent)
			if player then
				pickUp(player, id, true)
			end
		end)
	end
	if gathered or not item.permanent then
		local lifetime = if gathered then GroundDrops.LIFETIME_SECONDS else DropService.ORDINARY_SECONDS
		task.delay(lifetime, function()
			if drops[id] == drop then
				drops[id] = nil
				part:Destroy()
			end
		end)
	end
end

-- `walked` is a walk-over pickup of a gathered drop: it fails silently.
function pickUp(player: Player, id: string, walked: boolean)
	local drop = drops[id]
	if drop == nil or not canAct(player) then
		return
	end
	if drop.rules then
		local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
		local distance = if root then (root.Position - drop.part.Position).Magnitude else math.huge
		local ok, reason = GroundDrops.CanClaim(drop.rules, player.UserId, distance, os.clock())
		if not ok then
			if reason == "Expired" then
				drops[id] = nil
				drop.part:Destroy()
			elseif reason == "NotYours" and not walked then
				InventoryService.Notify(player, "Someone else's drop. It's free in a moment.")
			end
			return
		end
	end
	-- Claim first so a second, simultaneous pickup finds nothing.
	drops[id] = nil
	local copy = DropService.PrepareClaim(player, drop.item)
	local remaining = InventoryService.Add(player, copy)
	if remaining > 0 and (copy.instanceId or remaining == (drop.item.quantity or 1)) then
		drops[id] = drop
		if not walked then
			InventoryService.Notify(player, "No room to pick that up.")
		end
		return
	end
	if remaining > 0 then
		drop.item.quantity = remaining
		drop.prompt.ObjectText = label(drop.item)
		drops[id] = drop
	else
		drop.part:Destroy()
	end
	DropService.FinishClaim(player, copy, drop.item.ownerId)
end

local function dropItem(player: Player, area: any, index: any)
	if type(area) ~= "string" or type(index) ~= "number" then
		return false, "BadRequest"
	end
	if not canAct(player) then
		return false, "NotInRun"
	end
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if root == nil then
		return false, "NotInRun"
	end
	local item = InventoryService.TakeAt(player, area, index)
	if item == nil then
		return false, "Empty"
	end
	DropService.Release(player, item, "WorldDropped")
	local ground = workspace:Raycast(root.Position + root.CFrame.LookVector * 3, Vector3.new(0, -12, 0))
	DropService.Spawn(item, ground and ground.Position or (root.Position - Vector3.new(0, 2.5, 0)))
	return true, nil
end

function DropService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	Remotes.Handle("DropItem", dropItem)
end

return DropService
