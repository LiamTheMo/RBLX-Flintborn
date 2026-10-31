-- Shows what a player holds and wears (v0.19): the equipped hotbar item as a
-- "HeldItem" model in the hand and each worn armor slot as an "Armor_<Slot>" model on
-- the body, all built from the placeholder recipes in GearModels. The server owns
-- the visuals: the parts are welded to the R6 character, so they replicate to every
-- client, and they are Massless and never collide, query or touch (ModelBuilder),
-- so they cannot change movement, hits or rays. Nothing here is gameplay state; the
-- inventory stays the authority (GDD §22.1.1, §56).
--
-- It follows InventoryService.Changed, which fires after every inventory change
-- (equip, drop, use, craft, pick-up, wear, take off), plus CharacterAdded. It rebuilds
-- only what changed: the catalog id shown per slot is cached per player. When the run
-- inventory goes away (RunEnded, player leaves) every model is removed. World place
-- only; the lobby has no inventory.
--
-- Grip: an R6 hand is at "Right Arm" * CFrame.new(0, -1, 0). A Roblox Tool sits in the
-- RightGrip with its handle's +Y pointing forward, so the recipe is turned by
-- Rx(-90): +Y (the business end) points along the arm's -Z, which is the way the
-- character faces. Bows are held upright in the "Left Arm" instead, belly forward,
-- so a bow never covers the sword arm. Characters without R6 parts show nothing.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GearModels = require(ReplicatedStorage.Shared.Visuals.GearModels)
local InventoryRules = require(ReplicatedStorage.Shared.Inventory.InventoryRules)
local ModelBuilder = require(ReplicatedStorage.Shared.Visuals.ModelBuilder)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local InventoryService = require(script.Parent.InventoryService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local EquipmentVisualService = {}

EquipmentVisualService.HELD_NAME = "HeldItem"
EquipmentVisualService.ARMOR_PREFIX = "Armor_"

-- How long a fresh character may take to grow its R6 arms before we give up.
EquipmentVisualService.CHARACTER_WAIT_SECONDS = 5

-- Handle +Y forward from the hand of the right arm; bows stand upright in the left.
local HAND = CFrame.new(0, -1, 0)
local TOOL_GRIP = HAND * CFrame.Angles(math.rad(-90), 0, 0)
local BOW_GRIP = HAND

-- state[player] = { character, held = {id, model}?, armor = { [slot] = {id, model} } }
local states = {}

local function clearModel(slot)
	if slot and slot.model then
		slot.model:Destroy()
	end
end

local function clear(player: Player)
	local state = states[player]
	if state == nil then
		return
	end
	states[player] = nil
	clearModel(state.held)
	for _, slot in state.armor do
		clearModel(slot)
	end
end

-- Whether `slot` still shows `id` on the live character.
local function current(slot, id: string?, character: Model): boolean
	if slot == nil then
		return id == nil
	end
	return slot.id == id and slot.model ~= nil and slot.model.Parent == character
end

local function refreshHeld(state, player: Player, character: Model)
	local item = InventoryService.Equipped(player)
	local id = item and item.catalogId
	local recipe = id and GearModels.Held(id)
	if recipe == nil then
		id = nil
	end
	if current(state.held, id, character) then
		return
	end
	clearModel(state.held)
	state.held = nil
	if id == nil or recipe == nil then
		return
	end
	local hostName = if GearModels.IsBow(id) then "Left Arm" else "Right Arm"
	local host = character:FindFirstChild(hostName)
	if host == nil or not host:IsA("BasePart") then
		return
	end
	local model = ModelBuilder.Attach(host, recipe, if hostName == "Left Arm" then BOW_GRIP else TOOL_GRIP, {
		name = EquipmentVisualService.HELD_NAME,
		parent = character,
	})
	model:SetAttribute("CatalogId", id)
	state.held = { id = id, model = model }
end

local function refreshArmor(state, player: Player, character: Model, inventory)
	for _, slotName in InventoryRules.ArmorSlots do
		local item = inventory.armor[slotName]
		local id = item and item.catalogId
		local recipes = id and GearModels.Armor(id)
		if recipes == nil then
			id = nil
		end
		if not current(state.armor[slotName], id, character) then
			clearModel(state.armor[slotName])
			state.armor[slotName] = nil
			if id and recipes then
				local model = Instance.new("Model")
				model.Name = EquipmentVisualService.ARMOR_PREFIX .. slotName
				for partName, recipe in recipes do
					local host = character:FindFirstChild(partName)
					if host and host:IsA("BasePart") then
						ModelBuilder.Decorate(host, recipe, { parent = model })
					end
				end
				model:SetAttribute("CatalogId", id)
				model.Parent = character
				state.armor[slotName] = { id = id, model = model }
			end
		end
	end
end

-- Brings the character's models in line with the inventory.
local function refresh(player: Player)
	local inventory = InventoryService.Get(player)
	local character = player.Character
	if inventory == nil or character == nil or character.Parent == nil then
		clear(player)
		return
	end
	local state = states[player]
	if state ~= nil and state.character ~= character then
		-- A new character: the old one's models went with it.
		clear(player)
		state = nil
	end
	if state == nil then
		state = { character = character, held = nil, armor = {} }
		states[player] = state
	end
	local humanoid = character:FindFirstChildOfClass("Humanoid")
	if humanoid == nil or humanoid.Health <= 0 then
		return
	end
	refreshHeld(state, player, character)
	refreshArmor(state, player, character, inventory)
end

local function watch(player: Player)
	player.CharacterAdded:Connect(function(character)
		clear(player)
		task.spawn(function()
			character:WaitForChild("Right Arm", EquipmentVisualService.CHARACTER_WAIT_SECONDS)
			if player.Parent and player.Character == character then
				refresh(player)
			end
		end)
	end)
	if player.Character then
		refresh(player)
	end
end

function EquipmentVisualService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	InventoryService.Changed:Connect(refresh)
	-- The run inventory is cleared by its own RunEnded listener; do not wait for a
	-- later Changed that never comes.
	WorldAdmissionService.RunEnded:Connect(clear)
	Players.PlayerAdded:Connect(watch)
	Players.PlayerRemoving:Connect(clear)
	for _, player in Players:GetPlayers() do
		watch(player)
	end
end

return EquipmentVisualService
