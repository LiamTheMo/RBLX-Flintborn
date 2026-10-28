-- Ancestral Forge (GDD §15–16, §25.3). The Forge navigation button opens the recipe browser in
-- the lobby, one tab per category. Counts are vault-only Owned/Needed; locked
-- recipes show what unlocks them. The Permanent tab lists conversions for the gear
-- in your vault first; "show all" lists every conversion grouped by tier, each
-- tier collapsed to one line until opened. A Permanent conversion asks for
-- confirmation naming the exact item and the Permanent rules before anything is
-- spent. Lobby place only.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ForgeRecipes = require(ReplicatedStorage.Shared.Crafting.ForgeRecipes)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

local ForgeController = {}

ForgeController.CONFIRM_DELAY = 1.5

local player = Players.LocalPlayer
local ui = {}
local pending = nil
-- The last snapshot, the open tab, and the Permanent tab's filter and open tiers.
local view = nil
local category = "Permanent"
local showAll = false
local expanded = {}

local GOOD = Color3.fromRGB(160, 230, 160)
local SHORT = Color3.fromRGB(240, 140, 120)
local TEXT = Color3.fromRGB(235, 226, 212)

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

local function invoke(name: string, ...)
	local ok, success, reason = pcall(Remotes.Get(name).InvokeServer, Remotes.Get(name), ...)
	if not ok then
		return false, "Request failed"
	end
	return success, if success then reason else Reasons.Text(reason)
end

local function text(parent, value: string, color: Color3, size: number?, order: number?)
	return make("TextLabel", {
		Text = value,
		Size = UDim2.new(1, 0, 0, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextWrapped = true,
		TextColor3 = color,
		Font = Enum.Font.GothamMedium,
		TextSize = size or 13,
		LayoutOrder = order or 0,
	}, parent)
end

local function button(parent, label: string, enabled: boolean, order: number, onClick)
	local b = make("TextButton", {
		Text = label,
		Size = UDim2.new(1, 0, 0, 28),
		BackgroundColor3 = enabled and Color3.fromRGB(110, 70, 30) or Color3.fromRGB(50, 44, 38),
		TextColor3 = enabled and Color3.fromRGB(255, 240, 220) or Color3.fromRGB(140, 130, 120),
		AutoButtonColor = enabled,
		Font = Enum.Font.GothamBold,
		TextSize = 13,
		LayoutOrder = order,
	}, parent)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
	if enabled then
		b.Activated:Connect(onClick)
	end
	return b
end

local refresh
local draw

local function submit(recipeId: string, sourceId: string?)
	-- One nonce per confirmed request; a retry of the same request reuses it.
	local nonce = HttpService:GenerateGUID(false)
	local ok, result = invoke("ForgeCraft", recipeId, sourceId, nonce)
	if not ok and result == "Request failed" then
		ok, result = invoke("ForgeCraft", recipeId, sourceId, nonce)
	end
	ui.status.Text = if ok then "Forged. Check your lobby backpack or vault." else ("Not forged: " .. tostring(result))
	refresh()
end

local function confirm(recipe, source)
	local spend = {}
	for _, input in recipe.inputs do
		table.insert(spend, ("%s ×%d"):format(input.name, input.needed))
	end
	local roll = if source.qualityRoll and source.qualityRoll ~= 0
		then (" (quality %+.1f%%, kept exactly)"):format(source.qualityRoll * 100)
		else ""
	ui.confirmText.Text = ("Convert this %s%s into a Permanent item?\n\nSpends from your vault: %s.\n\nPermanent items stay with you when you die. Dropping one lets whoever picks it up own it, and trading transfers it. The ordinary version is consumed. This cannot be undone."):format(
		source.name,
		roll,
		table.concat(spend, ", ")
	)
	local request = { recipeId = recipe.id, sourceId = source.instanceId }
	pending = request
	ui.confirm.Visible = true
	ui.yes:SetAttribute("Armed", false)
	ui.yes.Text = "Read the rules above…"
	task.delay(ForgeController.CONFIRM_DELAY, function()
		if pending == request then
			ui.yes:SetAttribute("Armed", true)
			ui.yes.Text = "Convert (cannot be undone)"
		end
	end)
end

local function renderRecipe(recipe, order: number)
	local card = make("Frame", {
		Size = UDim2.new(1, -8, 0, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundColor3 = Color3.fromRGB(38, 32, 27),
		Active = true,
		LayoutOrder = order,
	}, ui.list)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, card)
	make("UIPadding", {
		PaddingTop = UDim.new(0, 6),
		PaddingBottom = UDim.new(0, 6),
		PaddingLeft = UDim.new(0, 8),
		PaddingRight = UDim.new(0, 8),
	}, card)
	make("UIListLayout", { Padding = UDim.new(0, 3), SortOrder = Enum.SortOrder.LayoutOrder }, card)
	local title = recipe.name .. (recipe.quantity > 1 and (" ×" .. recipe.quantity) or "")
	text(card, (recipe.unlocked and "" or "🔒 ") .. title, Color3.fromRGB(255, 214, 150), 14, 1)
	local funded = true
	for index, input in recipe.inputs do
		local enough = input.owned >= input.needed
		funded = funded and enough
		text(
			card,
			("%s  %d / %d"):format(input.name, input.owned, input.needed),
			enough and GOOD or SHORT,
			12,
			1 + index
		)
	end
	if not recipe.unlocked then
		text(card, recipe.requirement, TEXT, 12, 50)
		return
	end
	if recipe.kind == "Permanent" then
		if #recipe.sources == 0 then
			text(card, "Vault an ordinary one of these to convert it.", TEXT, 12, 50)
		end
		for index, source in recipe.sources do
			local roll = if source.qualityRoll and source.qualityRoll ~= 0
				then (" (%+.1f%%)"):format(source.qualityRoll * 100)
				else ""
			button(card, "Convert " .. source.name .. roll, funded, 50 + index, function()
				confirm(recipe, source)
			end)
		end
	else
		button(card, "Forge", funded, 50, function()
			submit(recipe.id, nil)
		end)
	end
end

local function clear()
	for _, child in ui.list:GetChildren() do
		if not child:IsA("UIListLayout") then
			child:Destroy()
		end
	end
end

local FAMILY_NAMES = { Weapon = "weapons", Tool = "tools", Armor = "armor" }

local function tierLabel(tierId: string, recipes): string
	local families, seen = {}, {}
	for _, recipe in recipes do
		local family = FAMILY_NAMES[recipe.family]
		if family and not seen[family] then
			seen[family] = true
			table.insert(families, family)
		end
	end
	return ("%s gear — %d conversion%s (%s)"):format(
		tierId,
		#recipes,
		#recipes == 1 and "" or "s",
		table.concat(families, ", ")
	)
end

-- The Permanent tab: vaulted gear first, or every conversion grouped by tier.
local function drawPermanent(recipes, nextOrder)
	button(
		ui.list,
		if showAll then "Show only gear in your vault" else "Show every Permanent conversion",
		true,
		nextOrder(),
		function()
			showAll = not showAll
			draw()
		end
	)
	if not showAll then
		local any = false
		for _, recipe in recipes do
			if #recipe.sources > 0 then
				any = true
				renderRecipe(recipe, nextOrder())
			end
		end
		if not any then
			text(
				ui.list,
				"None of the gear in your vault can be converted yet. Deposit gear in the Vault, or show every conversion to see what each costs.",
				TEXT,
				13,
				nextOrder()
			)
		end
		return
	end
	text(
		ui.list,
		"Any weapon, tool or armor piece can become Permanent; the cost rises with its tier.",
		TEXT,
		12,
		nextOrder()
	)
	for _, tierId in view.tiers or {} do
		local group = {}
		for _, recipe in recipes do
			if recipe.tier == tierId then
				table.insert(group, recipe)
			end
		end
		if #group == 0 then
			continue
		end
		-- Every conversion in a tier unlocks together, so the header carries the lock.
		local first = group[1]
		local header = (expanded[tierId] and "▾ " or "▸ ")
			.. (first.unlocked and "" or "🔒 ")
			.. tierLabel(tierId, group)
		button(ui.list, header, true, nextOrder(), function()
			expanded[tierId] = not expanded[tierId]
			draw()
		end)
		if expanded[tierId] then
			if not first.unlocked then
				text(ui.list, first.requirement, TEXT, 12, nextOrder())
			end
			for _, recipe in group do
				renderRecipe(recipe, nextOrder())
			end
		end
	end
end

-- Rebuilds the list from the last snapshot without yielding.
function draw()
	clear()
	for name, tab in ui.tabs do
		tab.BackgroundColor3 = if name == category then Color3.fromRGB(110, 70, 30) else Color3.fromRGB(46, 38, 30)
	end
	if type(view) ~= "table" then
		ui.status.Text = "Your data is still loading."
		return
	end
	local order = 0
	local function nextOrder()
		order += 1
		return order
	end
	local recipes = {}
	for _, recipe in view.recipes do
		if recipe.category == category then
			table.insert(recipes, recipe)
		end
	end
	if category == "Permanent" then
		drawPermanent(recipes, nextOrder)
		return
	end
	for _, recipe in recipes do
		renderRecipe(recipe, nextOrder())
	end
end

function refresh()
	view = invoke("ForgeSnapshot")
	draw()
end

local function build()
	-- Above the always-open lobby panel.
	local gui =
		make("ScreenGui", { Name = "Forge", ResetOnSpawn = false, DisplayOrder = 2 }, player:WaitForChild("PlayerGui"))
	ui.panel = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.42, 0.5),
		Size = UDim2.new(0.45, 0, 0.8, 0),
		BackgroundColor3 = Color3.fromRGB(24, 20, 17),
		Active = true,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.panel)
	make("UISizeConstraint", { MaxSize = Vector2.new(560, 640), MinSize = Vector2.new(320, 320) }, ui.panel)
	make("TextLabel", {
		Text = "Ancestral Forge — counts vaulted materials only",
		Position = UDim2.fromOffset(10, 6),
		Size = UDim2.new(1, -50, 0, 24),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextTruncate = Enum.TextTruncate.AtEnd,
		TextColor3 = Color3.fromRGB(255, 214, 150),
		Font = Enum.Font.GothamBlack,
		TextSize = 16,
	}, ui.panel)
	local close = make("TextButton", {
		Text = "✕",
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.new(1, -6, 0, 6),
		Size = UDim2.fromOffset(28, 24),
		BackgroundColor3 = Color3.fromRGB(70, 56, 40),
		TextColor3 = Color3.fromRGB(245, 236, 222),
		Font = Enum.Font.GothamBold,
		TextSize = 14,
	}, ui.panel)
	close.Activated:Connect(function()
		ui.panel.Visible = false
		ui.confirm.Visible = false
	end)
	-- One tab per recipe category.
	local tabs = make("Frame", {
		Position = UDim2.fromOffset(8, 34),
		Size = UDim2.new(1, -16, 0, 24),
		BackgroundTransparency = 1,
	}, ui.panel)
	make("UIListLayout", {
		FillDirection = Enum.FillDirection.Horizontal,
		Padding = UDim.new(0, 4),
		SortOrder = Enum.SortOrder.LayoutOrder,
	}, tabs)
	ui.tabs = {}
	for index, name in ForgeRecipes.Categories do
		local tab = make("TextButton", {
			Text = name,
			Size = UDim2.new(1 / #ForgeRecipes.Categories, -4, 1, 0),
			BackgroundColor3 = Color3.fromRGB(46, 38, 30),
			TextColor3 = Color3.fromRGB(245, 236, 222),
			Font = Enum.Font.GothamBold,
			TextSize = 12,
			LayoutOrder = index,
		}, tabs)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, tab)
		tab.Activated:Connect(function()
			category = name
			ui.status.Text = ""
			draw()
		end)
		ui.tabs[name] = tab
	end
	ui.list = make("ScrollingFrame", {
		Position = UDim2.fromOffset(8, 64),
		Size = UDim2.new(1, -16, 1, -98),
		BackgroundTransparency = 1,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		CanvasSize = UDim2.new(),
		ScrollBarThickness = 6,
	}, ui.panel)
	make("UIListLayout", { Padding = UDim.new(0, 6), SortOrder = Enum.SortOrder.LayoutOrder }, ui.list)
	ui.status = make("TextLabel", {
		Text = "",
		AnchorPoint = Vector2.new(0, 1),
		Position = UDim2.new(0, 10, 1, -6),
		Size = UDim2.new(1, -20, 0, 22),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextTruncate = Enum.TextTruncate.AtEnd,
		TextColor3 = TEXT,
		Font = Enum.Font.Gotham,
		TextSize = 13,
	}, ui.panel)

	ui.confirm = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(400, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundColor3 = Color3.fromRGB(40, 28, 18),
		Active = true,
		Visible = false,
		ZIndex = 5,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.confirm)
	make("UIPadding", {
		PaddingTop = UDim.new(0, 12),
		PaddingBottom = UDim.new(0, 12),
		PaddingLeft = UDim.new(0, 12),
		PaddingRight = UDim.new(0, 12),
	}, ui.confirm)
	make("UIListLayout", { Padding = UDim.new(0, 8), SortOrder = Enum.SortOrder.LayoutOrder }, ui.confirm)
	ui.confirmText = text(ui.confirm, "", TEXT, 14, 1)
	ui.confirmText.ZIndex = 5
	-- Deliberate on every input: the confirm button only arms after a short read delay.
	ui.yes = button(ui.confirm, "Convert", true, 2, function()
		if ui.yes:GetAttribute("Armed") and pending then
			local request = pending
			pending = nil
			ui.confirm.Visible = false
			submit(request.recipeId, request.sourceId)
		end
	end)
	ui.yes.ZIndex = 5
	local no = button(ui.confirm, "Cancel", true, 3, function()
		pending = nil
		ui.confirm.Visible = false
	end)
	no.ZIndex = 5
end

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function ForgeController.Toggle()
	ui.panel.Visible = not ui.panel.Visible
	ui.confirm.Visible = false
	if ui.panel.Visible then
		ui.status.Text = ""
		refresh()
	end
end

function ForgeController.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	build()
end

return ForgeController
