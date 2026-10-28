-- Crafting menu (GDD §25.3, §16.8, §51) in the parchment Crafting window
-- (Hud/CraftingPanel). Recipes are listed by category (tabs) and tier, with a
-- search box; the chosen recipe shows what it needs against what you carry
-- (from the live inventory) and the station it needs, marked when none is in
-- reach. Smelting takes a batch (the stepper, or Craft all for as many as the ore
-- allows) and shows its progress on the right with a Stop button (the server
-- publishes it as Smelt* player attributes), beside which stations are within
-- reach. The server decides; this only sends the request. World place only.

local CollectionService = game:GetService("CollectionService")
local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local CraftingRules = require(ReplicatedStorage.Shared.Crafting.CraftingRules)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Recipes = require(ReplicatedStorage.Shared.Crafting.Recipes)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local InventoryController = require(script.Parent.InventoryController)
local CraftingPanel = require(script.Parent.Parent.Hud.CraftingPanel)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Theme = require(script.Parent.Parent.Ui.Theme)

local CraftingController = {}

local player = Players.LocalPlayer
local make = Theme.Make
local ui = {}
local panel = nil
local nearbyKey = ""
local smeltConnection = nil

local CLOSE_ACTION = "FlintbornCraftingClose"

-- Category tabs and their glyphs.
CraftingController.GLYPHS = {
	Weapons = "pm_glyph_sword",
	Tools = "pm_glyph_tools",
	Armor = "pm_glyph_armor",
	Bars = "pm_glyph_bag",
	Consumables = "pm_glyph_heart",
	Other = "pm_glyph_bench",
}

local sortedRecipes = CraftingRules.Sorted(Recipes.List)

local REASON_TEXT = {
	Busy = "You are already smelting. Wait for it or press ✕ to stop.",
	TooFast = "Slow down a moment.",
	MissingIngredients = "You don't have the ingredients.",
	InventoryFull = "No room in your inventory for that.",
	Downed = "You can't craft while downed.",
	NotInRun = "You can only craft during a run.",
}

local function nameOf(catalogId: string): string
	local def = ItemCatalog.Get(catalogId)
	return def and def.name or catalogId
end

local function stationHint(station: string): string
	local verb = if station == Recipes.Cauldron
		then "brew"
		elseif station == Recipes.Furnace then "smelt or cook"
		else "craft"
	return ("Stand next to a %s (build one with %s) to %s that."):format(
		string.lower(station),
		Binds.Label("Build"),
		verb
	)
end

-- The station kinds within reach, as a set.
local function stationsNearby()
	local set = {}
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if root == nil then
		return set
	end
	for _, station in CraftingRules.STATIONS do
		for _, part in CollectionService:GetTagged(station) do
			if part:IsA("BasePart") and (part.Position - root.Position).Magnitude <= CraftingRules.STATION_RANGE then
				set[station] = true
				break
			end
		end
	end
	return set
end

local function keyOf(set): string
	local parts = {}
	for _, station in CraftingRules.STATIONS do
		if set[station] then
			table.insert(parts, station)
		end
	end
	return table.concat(parts, ",")
end

-- A recipe as the window lists it, with what the player carries and whether a
-- station for it is in reach.
local function entryFor(recipe, nearby)
	local inputs = {}
	local can = CraftingRules.MAX_BATCH
	for input, amount in recipe.inputs do
		local owned = InventoryController.Count(input)
		can = math.min(can, owned // amount)
		table.insert(inputs, { id = input, name = nameOf(input), owned = owned, needed = amount })
	end
	table.sort(inputs, function(a, b)
		return a.name < b.name
	end)
	local timed = CraftingRules.IsTimed(recipe)
	local station = CraftingRules.StationFor(recipe)
	local here = CraftingRules.AvailableHere(recipe, nearby)
	return {
		id = recipe.id,
		output = recipe.output,
		name = nameOf(recipe.output),
		quantity = recipe.quantity,
		category = CraftingRules.Category(recipe),
		inputs = inputs,
		can = can,
		here = here,
		where = (station or "Anywhere") .. (if timed then (" · %s s each"):format(tostring(recipe.seconds)) else ""),
		timed = timed,
		verb = if not here and station
			then ("NEED %s"):format(string.upper(station))
			elseif timed then "SMELT"
			else "CRAFT",
	}
end

local function refresh()
	local nearby = stationsNearby()
	nearbyKey = keyOf(nearby)
	local entries = {}
	for _, recipe in sortedRecipes do
		table.insert(entries, entryFor(recipe, nearby))
	end
	panel:SetNearby(nearby)
	panel:SetEntries(entries)
end

local function craft(entry, count: number?)
	local recipe = Recipes.Get(entry.id)
	if recipe == nil then
		return
	end
	panel:SetBusy(true)
	local ok, success, reason = pcall(function()
		return Remotes.Get("Craft"):InvokeServer(HttpService:GenerateGUID(false), recipe.id, count)
	end)
	panel:SetBusy(false)
	if ok and success then
		panel:SetStatus(
			if count
				then ("Smelting %d %s…"):format(count, nameOf(recipe.output))
				else "Crafted " .. nameOf(recipe.output) .. (recipe.quantity > 1 and (" ×" .. recipe.quantity) or "")
		)
		return
	end
	local station = type(reason) == "string" and string.match(reason, "^Needs(%a+)$")
	if station and CraftingRules.IsStation(station) then
		panel:SetStatus(stationHint(station))
	else
		panel:SetStatus(REASON_TEXT[reason] or ("Could not craft: " .. tostring(reason or success)))
	end
end

local function stopSmelt()
	local recipeId = player:GetAttribute("SmeltRecipe")
	if recipeId == nil then
		return
	end
	pcall(function()
		return Remotes.Get("Craft"):InvokeServer(HttpService:GenerateGUID(false), recipeId, 0)
	end)
	panel:SetStatus("Smelting stopped. Bars already made are yours.")
end

-- Smelting progress ----------------------------------------------------------

local function renderSmelt()
	local recipe = Recipes.Get(player:GetAttribute("SmeltRecipe"))
	if recipe == nil then
		panel:SetJob(nil)
		return
	end
	local count = player:GetAttribute("SmeltCount") or 1
	local done = player:GetAttribute("SmeltDone") or 0
	local seconds = player:GetAttribute("SmeltSeconds") or recipe.seconds or 1
	local endsAt = player:GetAttribute("SmeltEndsAt") or 0
	local progress, left = CraftingRules.Progress(done, count, endsAt, seconds, workspace:GetServerTimeNow())
	-- Time left for the whole batch: this unit's rest plus the units after it.
	local total = left + math.max(0, count - done - 1) * seconds
	panel:SetJob({
		entry = entryFor(recipe, {}),
		count = count,
		done = done,
		progress = progress,
		left = total,
	})
end

local function onSmeltChanged()
	local active = player:GetAttribute("SmeltRecipe") ~= nil
	if active and smeltConnection == nil then
		smeltConnection = RunService.RenderStepped:Connect(function()
			if panel.screen:IsOpen() then
				renderSmelt()
			end
		end)
	elseif not active and smeltConnection then
		smeltConnection:Disconnect()
		smeltConnection = nil
	end
	renderSmelt()
end

-- Building --------------------------------------------------------------------

local function close()
	ContextActionService:UnbindAction(CLOSE_ACTION)
	local focus = GuiService.SelectedObject
	if focus and focus:IsDescendantOf(panel.screen.gui) then
		GuiService.SelectedObject = nil
	end
	panel.screen:SetOpen(false)
end

local function build()
	local categories = {}
	for _, category in CraftingRules.CATEGORIES do
		table.insert(categories, {
			id = category.id,
			label = category.label,
			glyph = CraftingController.GLYPHS[category.id] or "pm_glyph_bench",
		})
	end
	panel = CraftingPanel.new(player:WaitForChild("PlayerGui"), {
		onClose = close,
		onCraft = function(entry, count)
			task.spawn(craft, entry, count)
		end,
		onStop = function()
			task.spawn(stopSmelt)
		end,
		onEmpty = function()
			panel:SelectCategory("Bars")
		end,
	}, { mode = "crafting", name = "FlintbornCrafting", window = "pm_window_crafting", categories = categories })
	panel:SetStations(CraftingRules.STATIONS)
	panel.screen:Watch()
	local function hint()
		panel:SetHint(
			("Stand within %d studs of a station to use its recipes. Build stations with %s."):format(
				CraftingRules.STATION_RANGE,
				Binds.Label("Build")
			)
		)
	end
	hint()

	-- The legacy HUD's Craft button (the new HUD's nav bar has its own).
	local gui = make("ScreenGui", { Name = "Crafting", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	ui.toggle = make("TextButton", {
		Text = "Craft (" .. Binds.Label("Craft") .. ")",
		AnchorPoint = Vector2.new(0, 1),
		Position = UDim2.new(0.5, 8 + 9 * 33, 1, -12),
		Size = UDim2.fromOffset(100, 30),
		BackgroundColor3 = Color3.fromRGB(70, 56, 40),
		TextColor3 = Color3.fromRGB(245, 236, 222),
		Font = Enum.Font.GothamBold,
		TextSize = 13,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, ui.toggle)
	Binds.Changed:Connect(function()
		ui.toggle.Text = "Craft (" .. Binds.Label("Craft") .. ")"
		hint()
	end)
	ui.toggle.Activated:Connect(function()
		CraftingController.Toggle()
	end)
end

local function setInRun(inRun: boolean)
	-- With the new HUD the hotbar spans this spot; the nav bar keeps a Craft button.
	ui.toggle.Visible = inRun and not HudMode.ReplacesLegacy()
	if not inRun then
		close()
		Binds.Unbind("Craft")
		return
	end
	Binds.Bind("Craft", function(_, state)
		if state == Enum.UserInputState.Begin then
			CraftingController.Toggle()
		end
		return Enum.ContextActionResult.Sink
	end)
end

-- Opens or closes the window (keys, and the on-screen navigation bar).
function CraftingController.Toggle()
	if panel.screen:IsOpen() then
		close()
		return
	end
	panel:SetStatus("")
	refresh()
	renderSmelt()
	panel.screen:SetOpen(true)
	ContextActionService:BindAction(CLOSE_ACTION, function(_, state)
		if state == Enum.UserInputState.Begin then
			close()
		end
		return Enum.ContextActionResult.Sink
	end, false, Enum.KeyCode.ButtonB)
	if GuiService.SelectedObject ~= nil or UserInputService.GamepadEnabled then
		GuiService.SelectedObject = panel.close
	end
end

function CraftingController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	InventoryController.Changed:Connect(function()
		if panel.screen:IsOpen() then
			refresh()
		end
	end)
	player:GetAttributeChangedSignal("SessionState"):Connect(function()
		setInRun(player:GetAttribute("SessionState") == "ActiveRun")
	end)
	setInRun(player:GetAttribute("SessionState") == "ActiveRun")
	for _, name in { "SmeltRecipe", "SmeltDone", "SmeltCount" } do
		player:GetAttributeChangedSignal(name):Connect(onSmeltChanged)
	end
	onSmeltChanged()
	-- Walking up to (or away from) a station changes what can be crafted here.
	task.spawn(function()
		while true do
			task.wait(0.5)
			if panel.screen:IsOpen() and keyOf(stationsNearby()) ~= nearbyKey then
				refresh()
			end
		end
	end)
end

return CraftingController
