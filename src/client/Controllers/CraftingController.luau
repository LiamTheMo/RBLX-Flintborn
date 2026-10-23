-- Crafting menu (GDD §25.3, §16.8): every recipe with Owned/Needed counts from the
-- live inventory, the station it needs, and a Craft button that is disabled until
-- the ingredients are there. The server decides; this only sends the request.
-- World place only.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Recipes = require(ReplicatedStorage.Shared.Crafting.Recipes)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local InventoryController = require(script.Parent.InventoryController)
local Binds = require(script.Parent.Parent.Ui.Binds)

local CraftingController = {}

local player = Players.LocalPlayer
local ui = {}
local rows = {}

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

local function nameOf(catalogId: string): string
	local def = ItemCatalog.Get(catalogId)
	return def and def.name or catalogId
end

local function craft(recipe)
	local ok, success, reason = pcall(function()
		return Remotes.Get("Craft"):InvokeServer(HttpService:GenerateGUID(false), recipe.id)
	end)
	if ok and success then
		ui.status.Text = "Crafted "
			.. nameOf(recipe.output)
			.. (recipe.quantity > 1 and (" ×" .. recipe.quantity) or "")
	elseif reason == "NeedsWorkbench" then
		ui.status.Text = "Stand next to a workbench to craft that."
	elseif reason == "NeedsFurnace" then
		ui.status.Text = "Stand next to a furnace (build one with X) to cook that."
	else
		ui.status.Text = "Could not craft: " .. tostring(reason or success)
	end
end

local function refresh()
	for _, row in rows do
		local parts = {}
		local ready = true
		for input, amount in row.recipe.inputs do
			local owned = InventoryController.Count(input)
			ready = ready and owned >= amount
			table.insert(parts, ("%s %d/%d"):format(nameOf(input), math.min(owned, amount), amount))
		end
		table.sort(parts)
		row.needs.Text = table.concat(parts, "   ")
		row.button.Active = ready
		row.button.AutoButtonColor = ready
		row.button.BackgroundTransparency = ready and 0 or 0.6
	end
end

local function build()
	local gui = make("ScreenGui", { Name = "Crafting", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	-- Left of the navigation bar (140 px on the right edge), and never taller than
	-- the screen so the first recipe stays reachable on phones.
	ui.panel = make("Frame", {
		AnchorPoint = Vector2.new(1, 0.5),
		Position = UDim2.new(1, -164, 0.5, 0),
		Size = UDim2.new(0, 360, 1, -24),
		BackgroundColor3 = Color3.fromRGB(24, 20, 17),
		BackgroundTransparency = 0.05,
		Active = true,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.panel)
	make("UISizeConstraint", { MaxSize = Vector2.new(360, 480) }, ui.panel)
	make("UIPadding", {
		PaddingTop = UDim.new(0, 10),
		PaddingLeft = UDim.new(0, 10),
		PaddingRight = UDim.new(0, 10),
		PaddingBottom = UDim.new(0, 10),
	}, ui.panel)
	local close = make("TextButton", {
		Text = "✕",
		AnchorPoint = Vector2.new(1, 0),
		Size = UDim2.fromOffset(28, 24),
		Position = UDim2.fromScale(1, 0),
		BackgroundColor3 = Color3.fromRGB(70, 56, 40),
		TextColor3 = Color3.fromRGB(245, 236, 222),
		Font = Enum.Font.GothamBold,
		TextSize = 14,
	}, ui.panel)
	close.Activated:Connect(function()
		ui.panel.Visible = false
	end)
	ui.status = make("TextLabel", {
		Size = UDim2.new(1, -34, 0, 36),
		BackgroundTransparency = 1,
		Text = "Basic recipes work anywhere. Advanced ones need a workbench.",
		TextWrapped = true,
		TextColor3 = Color3.fromRGB(240, 232, 220),
		Font = Enum.Font.Gotham,
		TextSize = 13,
	}, ui.panel)
	local list = make("ScrollingFrame", {
		Position = UDim2.fromOffset(0, 40),
		Size = UDim2.new(1, 0, 1, -40),
		BackgroundTransparency = 1,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		CanvasSize = UDim2.new(),
		ScrollBarThickness = 6,
	}, ui.panel)
	make("UIListLayout", { Padding = UDim.new(0, 6), SortOrder = Enum.SortOrder.LayoutOrder }, list)

	for order, recipe in Recipes.List do
		local row = make("Frame", {
			Size = UDim2.new(1, -8, 0, 58),
			BackgroundColor3 = Color3.fromRGB(38, 32, 26),
			Active = true,
			LayoutOrder = order,
		}, list)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, row)
		local title = nameOf(recipe.output) .. (recipe.quantity > 1 and (" ×" .. recipe.quantity) or "")
		if recipe.station == Recipes.Workbench then
			title ..= "  · workbench"
		elseif recipe.station == Recipes.Furnace then
			title ..= "  · furnace"
		end
		make("TextLabel", {
			Text = title,
			Position = UDim2.fromOffset(8, 4),
			Size = UDim2.new(1, -100, 0, 20),
			BackgroundTransparency = 1,
			TextXAlignment = Enum.TextXAlignment.Left,
			TextColor3 = Color3.fromRGB(255, 230, 190),
			Font = Enum.Font.GothamBold,
			TextSize = 14,
		}, row)
		local needs = make("TextLabel", {
			Position = UDim2.fromOffset(8, 26),
			Size = UDim2.new(1, -100, 0, 28),
			BackgroundTransparency = 1,
			TextXAlignment = Enum.TextXAlignment.Left,
			TextWrapped = true,
			TextColor3 = Color3.fromRGB(220, 210, 196),
			Font = Enum.Font.Gotham,
			TextSize = 12,
		}, row)
		local button = make("TextButton", {
			Text = "Craft",
			AnchorPoint = Vector2.new(1, 0.5),
			Position = UDim2.new(1, -8, 0.5, 0),
			Size = UDim2.fromOffset(80, 36),
			BackgroundColor3 = Color3.fromRGB(150, 84, 36),
			TextColor3 = Color3.fromRGB(255, 245, 230),
			Font = Enum.Font.GothamBold,
			TextSize = 14,
		}, row)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, button)
		button.Activated:Connect(function()
			if button.Active then
				craft(recipe)
			end
		end)
		table.insert(rows, { recipe = recipe, needs = needs, button = button })
	end

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
		ui.panel.Visible = not ui.panel.Visible
	end)
end

local function setInRun(inRun: boolean)
	ui.toggle.Visible = inRun
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
	refresh()
end

return CraftingController
