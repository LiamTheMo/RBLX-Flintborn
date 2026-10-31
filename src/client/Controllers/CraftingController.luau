-- Field crafting (GDD §25.3, §16.8, §51) in the recipe window (Hud/Screens/
-- RecipeWindow, crafting mode). Recipes are listed by category (the dropdown)
-- and tier; the chosen one shows what it needs against what you carry (the live
-- inventory) and the station it needs, and its button says when none is in
-- reach. Smelting takes a batch (QUANTITY, or All for as many as the ore allows;
-- other recipes make one per request, CraftingRules.BatchCount) and shows its
-- progress on the right with a Stop button (the server publishes it as Smelt*
-- player attributes), beside which stations are within reach. The server
-- decides; this only sends the request. World place only.

local CollectionService = game:GetService("CollectionService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CraftingRules = require(ReplicatedStorage.Shared.Crafting.CraftingRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local RecipeModel = require(ReplicatedStorage.Shared.UI.RecipeModel)
local Recipes = require(ReplicatedStorage.Shared.Crafting.Recipes)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local InventoryController = require(script.Parent.InventoryController)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local RecipeWindow = require(script.Parent.Parent.Hud.Screens.RecipeWindow)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Reasons = require(script.Parent.Parent.Ui.Reasons)
local Theme = require(script.Parent.Parent.Ui.Theme)

local CraftingController = {}

-- How often the open window rechecks which stations are in reach, and ticks a
-- running smelt's time left (there is no event for either).
CraftingController.WATCH_SECONDS = 0.5

local player = Players.LocalPlayer
local make = Theme.Make
local ui = {}
local window = nil
local nearbyKey = ""
local watching = nil

local sortedRecipes = CraftingRules.Sorted(Recipes.List)

local REASON_TEXT = {
	Busy = "You are already smelting. Wait for it or press Stop.",
	TooFast = "Slow down a moment.",
	MissingIngredients = "You don't have the ingredients.",
	InventoryFull = "No room in your inventory for that.",
	Downed = "You can't craft while downed.",
	NotInRun = "You can only craft during a run.",
}

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

local function refresh()
	local nearby = stationsNearby()
	nearbyKey = keyOf(nearby)
	window:SetEntries(
		RecipeModel.CraftEntries(sortedRecipes, InventoryController.Count, nearby),
		RecipeModel.Carried(InventoryController.Snapshot.slots)
	)
	window:SetStations(RecipeModel.StationsText(nearby))
end
CraftingController.Refresh = refresh

local function craft(entry, count: number)
	local recipe = Recipes.Get(entry.id)
	if recipe == nil then
		return
	end
	-- Only timed recipes take a count (CraftingRules.BatchCount).
	local batch = if entry.timed then count else nil
	window:SetBusy(true)
	local ok, success, reason = pcall(function()
		return Remotes.Get("Craft"):InvokeServer(HttpService:GenerateGUID(false), recipe.id, batch)
	end)
	window:SetBusy(false)
	local name = RecipeModel.NameOf(recipe.output)
	if ok and success then
		if batch then
			window:SetStatus("Smelting", ("%d %s on the way."):format(batch, name), "info")
		else
			window:SetStatus("Crafted", name .. (if recipe.quantity > 1 then " ×" .. recipe.quantity else ""), "item")
		end
		return
	end
	local station = type(reason) == "string" and string.match(reason, "^Needs(%a+)$")
	if station and CraftingRules.IsStation(station) then
		window:SetStatus("Not crafted", stationHint(station), "warn")
	else
		local code = if ok then reason or success else "Request failed"
		window:SetStatus("Not crafted", REASON_TEXT[code] or Reasons.Text(code), "warn")
	end
end

local function stopSmelt()
	local recipeId = player:GetAttribute("SmeltRecipe")
	if recipeId == nil then
		return
	end
	local ok, stopped, reason = pcall(function()
		return Remotes.Get("Craft"):InvokeServer(HttpService:GenerateGUID(false), recipeId, 0)
	end)
	if ok and stopped then
		window:SetStatus("Smelting stopped", "Bars already made are yours.", "info")
	else
		window:SetStatus("Not stopped", Reasons.Text(if ok then reason else "Request failed"), "warn")
	end
end

-- Smelting progress ----------------------------------------------------------

local function renderSmelt()
	local recipe = Recipes.Get(player:GetAttribute("SmeltRecipe"))
	if recipe == nil then
		window:SetJob(nil)
		return
	end
	local count = player:GetAttribute("SmeltCount") or 1
	local done = player:GetAttribute("SmeltDone") or 0
	local seconds = player:GetAttribute("SmeltSeconds") or recipe.seconds or 1
	local endsAt = player:GetAttribute("SmeltEndsAt") or 0
	local progress, left = CraftingRules.Progress(done, count, endsAt, seconds, workspace:GetServerTimeNow())
	-- Time left for the whole batch: this unit's rest plus the units after it.
	window:SetJob({
		name = RecipeModel.NameOf(recipe.output),
		count = count,
		done = done,
		progress = progress,
		left = left + math.max(0, count - done - 1) * seconds,
	})
end

-- While the window is open: stations walked up to (or away from) change what
-- can be made here, and a running smelt's time left ticks down.
local function watch()
	local token = {}
	watching = token
	task.spawn(function()
		while watching == token do
			task.wait(CraftingController.WATCH_SECONDS)
			if watching ~= token then
				return
			end
			if keyOf(stationsNearby()) ~= nearbyKey then
				refresh()
			end
			if player:GetAttribute("SmeltRecipe") ~= nil then
				renderSmelt()
			end
		end
	end)
end

-- Building --------------------------------------------------------------------

local function build()
	local categories = {}
	for _, category in CraftingRules.CATEGORIES do
		table.insert(categories, { id = category.id, label = category.label })
	end
	window = RecipeWindow.new({
		mode = "crafting",
		name = "FlintbornCrafting",
		title = "Field Crafting",
		subtitle = "Make tools and supplies from what you carry.",
		icon = "build",
		categories = categories,
		parent = player:WaitForChild("PlayerGui"),
		onForge = function(entry, count)
			task.spawn(craft, entry, count)
		end,
		onStop = function()
			task.spawn(stopSmelt)
		end,
	})
	window:Watch()
	window.screen.Closed:Connect(function()
		watching = nil
	end)
	CraftingController.window = window

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
	end)
	ui.toggle.Activated:Connect(function()
		CraftingController.Toggle()
	end)
end

local function setInRun(inRun: boolean)
	-- With the new HUD the hotbar spans this spot; the nav bar keeps a Craft button.
	ui.toggle.Visible = inRun and not HudMode.ReplacesLegacy()
	if not inRun then
		window:Close()
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

-- Opens or closes the window (the Craft key, and the on-screen navigation bar).
-- Escape / B close it (Kit.Modal).
function CraftingController.Toggle()
	if window == nil then
		return
	end
	if window:IsOpen() then
		window:Close()
		return
	end
	refresh()
	renderSmelt()
	window:Open()
	watch()
end

function CraftingController.IsOpen(): boolean
	return window ~= nil and window:IsOpen()
end

function CraftingController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	InventoryController.Changed:Connect(function()
		if window:IsOpen() then
			refresh()
		end
	end)
	player:GetAttributeChangedSignal("SessionState"):Connect(function()
		setInRun(player:GetAttribute("SessionState") == "ActiveRun")
	end)
	setInRun(player:GetAttribute("SessionState") == "ActiveRun")
	for _, name in { "SmeltRecipe", "SmeltDone", "SmeltCount", "SmeltEndsAt" } do
		player:GetAttributeChangedSignal(name):Connect(renderSmelt)
	end
	renderSmelt()
end

return CraftingController
