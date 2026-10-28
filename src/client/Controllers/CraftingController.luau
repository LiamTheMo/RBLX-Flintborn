-- Crafting menu (GDD §25.3, §16.8, §51). Recipes are grouped by category and by
-- tier up the ladder; category chips, a tier stepper and a "Here only" toggle
-- narrow the list. Each row shows Owned/Needed counts from the live inventory,
-- the station it needs (marked when none is in reach, and its Craft button then
-- names the station) and, for smelting, the time per bar and a batch size. A
-- running smelt shows its progress at the top with a Stop button (the server
-- publishes it as Smelt* player attributes). The server decides; this only sends
-- the request. World place only.

local CollectionService = game:GetService("CollectionService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local CraftingRules = require(ReplicatedStorage.Shared.Crafting.CraftingRules)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Recipes = require(ReplicatedStorage.Shared.Crafting.Recipes)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local InventoryController = require(script.Parent.InventoryController)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Theme = require(script.Parent.Parent.Ui.Theme)

local CraftingController = {}

local player = Players.LocalPlayer
local make = Theme.Make
local C = Theme.Colors
local ui = {}
local rows = {}
local headers = {}
local filter = { category = nil, tier = nil, hereOnly = false }
-- nil (any tier) followed by every tier that has recipes.
local tierChoices = { false }
local tierIndex = 1
local nearby = {}
local nearbyKey = ""
local smeltConnection = nil

local ROW_HEIGHT = 66
local BUTTON_WIDTH = 80
-- Batch sizes a smelting row cycles through; "max" is as many as the ore allows.
local BATCHES = { 1, 5, 10, "max" }

local REASON_TEXT = {
	Busy = "You are already smelting. Wait for it or press Stop.",
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

-- How many units of `recipe` the carried inputs pay for, capped at MAX_BATCH.
local function affordableCount(recipe): number
	local most = CraftingRules.MAX_BATCH
	for input, amount in recipe.inputs do
		most = math.min(most, InventoryController.Count(input) // amount)
	end
	return most
end

local function batchOf(row): number
	local batch = BATCHES[row.batch]
	if batch == "max" then
		return math.max(affordableCount(row.recipe), 1)
	end
	return batch
end

local function craft(row)
	local recipe = row.recipe
	local timed = CraftingRules.IsTimed(recipe)
	local count = if timed then batchOf(row) else nil
	local ok, success, reason = pcall(function()
		return Remotes.Get("Craft"):InvokeServer(HttpService:GenerateGUID(false), recipe.id, count)
	end)
	if ok and success then
		ui.status.Text = if timed
			then ("Smelting %d %s…"):format(count, nameOf(recipe.output))
			else "Crafted " .. nameOf(recipe.output) .. (recipe.quantity > 1 and (" ×" .. recipe.quantity) or "")
		return
	end
	local station = type(reason) == "string" and string.match(reason, "^Needs(%a+)$")
	if station and CraftingRules.IsStation(station) then
		ui.status.Text = stationHint(station)
	else
		ui.status.Text = REASON_TEXT[reason] or ("Could not craft: " .. tostring(reason or success))
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
	ui.status.Text = "Smelting stopped. Bars already made are yours."
end

local function refresh()
	nearby = stationsNearby()
	nearbyKey = keyOf(nearby)
	local shownIn = {}
	local shown = 0
	for _, row in rows do
		local recipe = row.recipe
		local visible = CraftingRules.Matches(recipe, filter, nearby)
		row.frame.Visible = visible
		if not visible then
			continue
		end
		shown += 1
		shownIn[row.category] = true
		local count = if CraftingRules.IsTimed(recipe) then batchOf(row) else 1
		local parts = {}
		local enough = true
		for input, amount in recipe.inputs do
			local needed = amount * count
			local owned = InventoryController.Count(input)
			enough = enough and owned >= needed
			table.insert(parts, ("%s %d/%d"):format(nameOf(input), math.min(owned, needed), needed))
		end
		table.sort(parts)
		row.needs.Text = table.concat(parts, "   ")
		local here = CraftingRules.AvailableHere(recipe, nearby)
		local station = CraftingRules.StationFor(recipe)
		row.meta.TextColor3 = if here then C.Text else C.Warn
		row.meta.Text = row.metaText .. (if here then "" else "  — none nearby")
		if row.batchButton then
			row.batchButton.Text = if BATCHES[row.batch] == "max" then "Max" else ("×%d"):format(count)
		end
		local ready = enough and here
		row.button.Text = if here then row.verb else (station or row.verb)
		row.button.Active = ready
		row.button.AutoButtonColor = ready
		row.button.BackgroundTransparency = if ready then 0 else 0.6
	end
	for category, header in headers do
		header.Visible = shownIn[category] == true
	end
	ui.empty.Visible = shown == 0
end

-- Filters ---------------------------------------------------------------------

local function renderFilters()
	for id, chip in ui.chips do
		local selected = (id == "All" and filter.category == nil) or id == filter.category
		chip.BackgroundColor3 = if selected then C.Button else C.ButtonDisabled
	end
	local tier = tierChoices[tierIndex]
	ui.tierLabel.Text = if tier then tier else "Any tier"
	ui.here.Text = if filter.hereOnly then "Here only ✓" else "Here only"
	ui.here.BackgroundColor3 = if filter.hereOnly then C.Button else C.ButtonDisabled
	refresh()
end

local function stepTier(delta: number)
	tierIndex = (tierIndex - 1 + delta) % #tierChoices + 1
	filter.tier = tierChoices[tierIndex] or nil
	renderFilters()
end

-- Smelting progress ----------------------------------------------------------

local function renderSmelt()
	local recipe = Recipes.Get(player:GetAttribute("SmeltRecipe"))
	if recipe == nil then
		return
	end
	local count = player:GetAttribute("SmeltCount") or 1
	local done = player:GetAttribute("SmeltDone") or 0
	local seconds = player:GetAttribute("SmeltSeconds") or recipe.seconds or 1
	local endsAt = player:GetAttribute("SmeltEndsAt") or 0
	local progress, left = CraftingRules.Progress(done, count, endsAt, seconds, workspace:GetServerTimeNow())
	ui.smeltFill.Size = UDim2.fromScale(progress, 1)
	ui.smeltText.Text = ("Smelting %s  %d/%d  · %.1f s"):format(nameOf(recipe.output), done, count, left)
end

local layout

local function onSmeltChanged()
	local active = player:GetAttribute("SmeltRecipe") ~= nil
	if active and smeltConnection == nil then
		smeltConnection = RunService.RenderStepped:Connect(renderSmelt)
	elseif not active and smeltConnection then
		smeltConnection:Disconnect()
		smeltConnection = nil
	end
	ui.smelt.Visible = active
	layout()
	if active then
		renderSmelt()
	end
end

-- Moves the filters and list down while the smelting strip shows.
function layout()
	local top = if ui.smelt.Visible then 80 else 40
	ui.chipBar.Position = UDim2.fromOffset(0, top)
	ui.filterRow.Position = UDim2.fromOffset(0, top + 44)
	ui.list.Position = UDim2.fromOffset(0, top + 88)
	ui.list.Size = UDim2.new(1, 0, 1, -(top + 88))
end

-- Building --------------------------------------------------------------------

local function button(props, parent)
	local b = make("TextButton", {
		BackgroundColor3 = C.Button,
		TextColor3 = C.Text,
		Font = Theme.Fonts.Bold,
		TextSize = Theme.TextSize.Small + 1,
	}, parent)
	for key, value in props do
		b[key] = value
	end
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
	return b
end

local function buildRow(recipe, order: number, list)
	local timed = CraftingRules.IsTimed(recipe)
	local station = CraftingRules.StationFor(recipe)
	local row = {
		recipe = recipe,
		category = CraftingRules.Category(recipe),
		batch = 1,
		verb = if timed
			then "Smelt"
			elseif station == Recipes.Cauldron then "Brew"
			elseif station == Recipes.Furnace then "Cook"
			else "Craft",
	}
	row.metaText = if station then station else "By hand"
	if timed then
		row.metaText ..= ("  · %s s per bar"):format(tostring(recipe.seconds))
	end
	row.frame = make("Frame", {
		Size = UDim2.new(1, -8, 0, ROW_HEIGHT),
		BackgroundColor3 = C.Card,
		Active = true,
		LayoutOrder = order,
	}, list)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, row.frame)
	local textWidth = if timed then -(BUTTON_WIDTH + 70) else -(BUTTON_WIDTH + 18)
	make("TextLabel", {
		Text = nameOf(recipe.output) .. (recipe.quantity > 1 and (" ×" .. recipe.quantity) or ""),
		Position = UDim2.fromOffset(8, 4),
		Size = UDim2.new(1, textWidth, 0, 18),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextTruncate = Enum.TextTruncate.AtEnd,
		TextColor3 = C.Heading,
		Font = Theme.Fonts.Bold,
		TextSize = Theme.TextSize.Body,
	}, row.frame)
	row.meta = make("TextLabel", {
		Position = UDim2.fromOffset(8, 22),
		Size = UDim2.new(1, textWidth, 0, 14),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = C.Text,
		Font = Theme.Fonts.Body,
		TextSize = Theme.TextSize.Small - 1,
	}, row.frame)
	row.needs = make("TextLabel", {
		Position = UDim2.fromOffset(8, 37),
		Size = UDim2.new(1, textWidth, 0, 26),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextYAlignment = Enum.TextYAlignment.Top,
		TextWrapped = true,
		TextColor3 = Color3.fromRGB(220, 210, 196),
		Font = Enum.Font.Gotham,
		TextSize = Theme.TextSize.Small,
	}, row.frame)
	row.button = button({
		Text = row.verb,
		AnchorPoint = Vector2.new(1, 0.5),
		Position = UDim2.new(1, -8, 0.5, 0),
		Size = UDim2.fromOffset(BUTTON_WIDTH, Theme.TOUCH_TARGET),
		BackgroundColor3 = Color3.fromRGB(150, 84, 36),
		TextSize = Theme.TextSize.Body,
	}, row.frame)
	row.button.Activated:Connect(function()
		if row.button.Active then
			craft(row)
		end
	end)
	if timed then
		row.batchButton = button({
			Text = "×1",
			AnchorPoint = Vector2.new(1, 0.5),
			Position = UDim2.new(1, -(BUTTON_WIDTH + 14), 0.5, 0),
			Size = UDim2.fromOffset(52, Theme.TOUCH_TARGET),
			BackgroundColor3 = C.ButtonDisabled,
		}, row.frame)
		row.batchButton.Activated:Connect(function()
			row.batch = row.batch % #BATCHES + 1
			refresh()
		end)
	end
	table.insert(rows, row)
end

local function build()
	local gui = make("ScreenGui", { Name = "Crafting", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	-- Left of the navigation bar (140 px on the right edge), and never taller than
	-- the screen so the first recipe stays reachable on phones.
	ui.panel = make("Frame", {
		AnchorPoint = Vector2.new(1, 0.5),
		Position = UDim2.new(1, -164, 0.5, 0),
		Size = UDim2.new(0, 380, 1, -24),
		BackgroundColor3 = C.Panel,
		BackgroundTransparency = 0.05,
		Active = true,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.panel)
	make("UISizeConstraint", { MaxSize = Vector2.new(380, 560) }, ui.panel)
	make("UIPadding", {
		PaddingTop = UDim.new(0, 10),
		PaddingLeft = UDim.new(0, 10),
		PaddingRight = UDim.new(0, 10),
		PaddingBottom = UDim.new(0, 10),
	}, ui.panel)
	local close = button({
		Text = "✕",
		AnchorPoint = Vector2.new(1, 0),
		Size = UDim2.fromOffset(40, 36),
		Position = UDim2.fromScale(1, 0),
		BackgroundColor3 = Color3.fromRGB(70, 56, 40),
		TextSize = Theme.TextSize.Body,
	}, ui.panel)
	close.Activated:Connect(function()
		ui.panel.Visible = false
	end)
	ui.status = make("TextLabel", {
		Size = UDim2.new(1, -46, 0, 36),
		BackgroundTransparency = 1,
		Text = "Recipes marked with a station need one nearby. Filter by kind and tier below.",
		TextWrapped = true,
		TextColor3 = C.Text,
		Font = Enum.Font.Gotham,
		TextSize = Theme.TextSize.Small + 1,
	}, ui.panel)

	-- Smelting strip: a progress fill behind the text, and Stop.
	ui.smelt = make("Frame", {
		Position = UDim2.fromOffset(0, 40),
		Size = UDim2.new(1, 0, 0, 36),
		BackgroundColor3 = C.Card,
		ClipsDescendants = true,
		Visible = false,
	}, ui.panel)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, ui.smelt)
	ui.smeltFill = make("Frame", {
		Size = UDim2.fromScale(0, 1),
		BackgroundColor3 = Color3.fromRGB(170, 96, 40),
		BorderSizePixel = 0,
	}, ui.smelt)
	ui.smeltText = make("TextLabel", {
		Position = UDim2.fromOffset(8, 0),
		Size = UDim2.new(1, -86, 1, 0),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextTruncate = Enum.TextTruncate.AtEnd,
		TextColor3 = C.Text,
		TextStrokeTransparency = 0.6,
		Font = Theme.Fonts.Bold,
		TextSize = Theme.TextSize.Small + 1,
	}, ui.smelt)
	local stop = button({
		Text = "Stop",
		AnchorPoint = Vector2.new(1, 0.5),
		Position = UDim2.new(1, -4, 0.5, 0),
		Size = UDim2.fromOffset(70, 30),
	}, ui.smelt)
	stop.Activated:Connect(stopSmelt)

	-- Category chips, scrolling sideways on narrow screens.
	ui.chipBar = make("ScrollingFrame", {
		Size = UDim2.new(1, 0, 0, 40),
		BackgroundTransparency = 1,
		ScrollingDirection = Enum.ScrollingDirection.X,
		AutomaticCanvasSize = Enum.AutomaticSize.X,
		CanvasSize = UDim2.new(),
		ScrollBarThickness = 3,
	}, ui.panel)
	make("UIListLayout", {
		FillDirection = Enum.FillDirection.Horizontal,
		Padding = UDim.new(0, 4),
		SortOrder = Enum.SortOrder.LayoutOrder,
	}, ui.chipBar)
	ui.chips = {}
	local chipList = { { id = "All", label = "All" } }
	for _, category in CraftingRules.CATEGORIES do
		table.insert(chipList, category)
	end
	for order, category in chipList do
		local chip = button({
			Text = category.label,
			AutomaticSize = Enum.AutomaticSize.X,
			Size = UDim2.fromOffset(0, 34),
			LayoutOrder = order,
		}, ui.chipBar)
		make("UIPadding", { PaddingLeft = UDim.new(0, 12), PaddingRight = UDim.new(0, 12) }, chip)
		chip.Activated:Connect(function()
			filter.category = if category.id == "All" then nil else category.id
			renderFilters()
		end)
		ui.chips[category.id] = chip
	end

	-- Tier stepper and the "Here only" toggle.
	ui.filterRow = make("Frame", {
		Size = UDim2.new(1, 0, 0, 40),
		BackgroundTransparency = 1,
	}, ui.panel)
	local down = button({ Text = "◀", Size = UDim2.fromOffset(44, 40) }, ui.filterRow)
	down.Activated:Connect(function()
		stepTier(-1)
	end)
	ui.tierLabel = make("TextLabel", {
		Position = UDim2.fromOffset(48, 0),
		Size = UDim2.fromOffset(110, 40),
		BackgroundTransparency = 1,
		TextColor3 = C.Heading,
		Font = Theme.Fonts.Bold,
		TextSize = Theme.TextSize.Body,
	}, ui.filterRow)
	local up =
		button({ Text = "▶", Position = UDim2.fromOffset(162, 0), Size = UDim2.fromOffset(44, 40) }, ui.filterRow)
	up.Activated:Connect(function()
		stepTier(1)
	end)
	ui.here = button({
		Text = "Here only",
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.fromScale(1, 0),
		Size = UDim2.fromOffset(120, 40),
	}, ui.filterRow)
	ui.here.Activated:Connect(function()
		filter.hereOnly = not filter.hereOnly
		renderFilters()
	end)

	ui.list = make("ScrollingFrame", {
		BackgroundTransparency = 1,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		CanvasSize = UDim2.new(),
		ScrollBarThickness = 6,
	}, ui.panel)
	make("UIListLayout", { Padding = UDim.new(0, 6), SortOrder = Enum.SortOrder.LayoutOrder }, ui.list)

	local labels = {}
	for _, category in CraftingRules.CATEGORIES do
		labels[category.id] = category.label
	end
	local order = 0
	for _, recipe in CraftingRules.Sorted(Recipes.List) do
		local category = CraftingRules.Category(recipe)
		if headers[category] == nil then
			order += 1
			headers[category] = make("TextLabel", {
				Text = labels[category] or category,
				Size = UDim2.new(1, -8, 0, 22),
				BackgroundTransparency = 1,
				TextXAlignment = Enum.TextXAlignment.Left,
				TextColor3 = C.Heading,
				Font = Theme.Fonts.Title,
				TextSize = Theme.TextSize.Body,
				LayoutOrder = order,
			}, ui.list)
		end
		order += 1
		buildRow(recipe, order, ui.list)
	end
	ui.empty = make("TextLabel", {
		Text = "Nothing matches. Try another kind or tier, or turn off Here only.",
		Size = UDim2.new(1, -8, 0, 40),
		BackgroundTransparency = 1,
		TextWrapped = true,
		TextColor3 = C.Text,
		Font = Enum.Font.Gotham,
		TextSize = Theme.TextSize.Small + 1,
		LayoutOrder = order + 1,
		Visible = false,
	}, ui.list)

	for _, tier in CraftingRules.TiersIn(Recipes.List) do
		table.insert(tierChoices, tier)
	end
	layout()

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
		ui.panel.Visible = false
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

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function CraftingController.Toggle()
	ui.panel.Visible = not ui.panel.Visible
	if ui.panel.Visible then
		refresh()
	end
end

function CraftingController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	InventoryController.Changed:Connect(refresh)
	player:GetAttributeChangedSignal("SessionState"):Connect(function()
		setInRun(player:GetAttribute("SessionState") == "ActiveRun")
	end)
	setInRun(player:GetAttribute("SessionState") == "ActiveRun")
	for _, name in { "SmeltRecipe", "SmeltDone" } do
		player:GetAttributeChangedSignal(name):Connect(onSmeltChanged)
	end
	onSmeltChanged()
	renderFilters()
	-- Walking up to (or away from) a station changes what can be crafted here.
	task.spawn(function()
		while true do
			task.wait(0.5)
			if ui.panel.Visible and keyOf(stationsNearby()) ~= nearbyKey then
				refresh()
			end
		end
	end)
end

return CraftingController
