-- Progression UI (GDD §33, §37, §25.4). A level bar with XP pop-ups everywhere; P
-- (or ButtonSelect) opens the panel: mastery tracks with their next milestone,
-- titles, and in the lobby the rebirth screen (Reset / Kept / Gained in plain
-- words before confirming) and the perk shop. In the world the new HUD (HudMode)
-- draws the level bar from Changed/View() and hosts the pop-ups (MountPopups).

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PerkCatalog = require(ReplicatedStorage.Shared.Progression.PerkCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local ProgressionRules = require(ReplicatedStorage.Shared.Progression.ProgressionRules)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local Binds = require(script.Parent.Parent.Ui.Binds)

local ProgressionController = {}

-- Fires (view) with every new progression snapshot.
ProgressionController.Changed = Signal.new()

local player = Players.LocalPlayer
local ui = {}
local view = nil
local popupHost = nil

-- The latest progression snapshot {level, xp, xpToNext, ...}, or nil while loading.
function ProgressionController.View()
	return view
end

local function placePopups()
	if ui.popups == nil or popupHost == nil then
		return
	end
	ui.popups.AnchorPoint = Vector2.new(0, 1)
	ui.popups.Position = UDim2.fromScale(0, 1)
	ui.popups.Size = UDim2.fromScale(1, 1)
	ui.popups.Parent = popupHost
end

-- Moves the XP pop-ups into `host`: the new HUD keeps them just above its XP bar,
-- in a gui that stays enabled outside a run so no pop-up is missed.
function ProgressionController.MountPopups(host: GuiObject)
	popupHost = host
	placePopups()
end

local TEXT = Color3.fromRGB(235, 226, 212)
local GOLD = Color3.fromRGB(255, 214, 150)

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
	return success, reason
end

local function line(text: string, color: Color3?, size: number?, order: number?)
	return make("TextLabel", {
		Text = text,
		Size = UDim2.new(1, -8, 0, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextWrapped = true,
		TextColor3 = color or TEXT,
		Font = Enum.Font.GothamMedium,
		TextSize = size or 13,
		LayoutOrder = order or 0,
	}, ui.list)
end

local function button(text: string, enabled: boolean, order: number, onClick)
	local b = make("TextButton", {
		Text = text,
		Size = UDim2.new(1, -8, 0, 28),
		BackgroundColor3 = if enabled then Color3.fromRGB(110, 70, 30) else Color3.fromRGB(50, 44, 38),
		TextColor3 = if enabled then Color3.fromRGB(255, 240, 220) else Color3.fromRGB(140, 130, 120),
		AutoButtonColor = enabled,
		Font = Enum.Font.GothamBold,
		TextSize = 13,
		LayoutOrder = order,
	}, ui.list)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
	if enabled then
		b.Activated:Connect(onClick)
	end
end

local function updateBar()
	if view == nil then
		return
	end
	ProgressionController.Changed:Fire(view)
	local fraction = if view.xpToNext then math.clamp(view.xp / view.xpToNext, 0, 1) else 1
	ui.fill.Size = UDim2.fromScale(fraction, 1)
	ui.barText.Text = if view.xpToNext
		then ("Level %d — %d / %d XP"):format(view.level, view.xp, view.xpToNext)
		else ("Level %d (max) — rebirth to keep climbing"):format(view.level)
end

local renderPanel

local function confirmRebirth()
	local preview = invoke("RebirthPreview")
	if type(preview) ~= "table" then
		return
	end
	ui.confirmText.Text = ("Rebirth?\n\nRESET: %s\n\nKEPT: %s\n\nGAINED: %s"):format(
		table.concat(preview.reset, "; "),
		table.concat(preview.kept, "; "),
		table.concat(preview.gained, "; ")
	)
	ui.confirm.Visible = true
end

function renderPanel()
	for _, child in ui.list:GetChildren() do
		if not child:IsA("UIListLayout") then
			child:Destroy()
		end
	end
	if view == nil then
		line("Your progress is still loading.")
		return
	end
	local order = 0
	local function nextOrder()
		order += 1
		return order
	end
	line(
		("Level %d · Rebirths %d · Tokens %d"):format(view.level, view.rebirth.count, view.rebirth.tokens),
		GOLD,
		16,
		nextOrder()
	)
	local bonuses = {}
	if view.premium then
		table.insert(bonuses, "Premium +25% XP")
	end
	if view.boosterUntil > workspace:GetServerTimeNow() then
		table.insert(bonuses, "XP booster +50%")
	end
	if #bonuses > 0 then
		line("Active: " .. table.concat(bonuses, " + "), Color3.fromRGB(160, 230, 160), 12, nextOrder())
	end
	line("Masteries", GOLD, 15, nextOrder())
	for _, mastery in view.masteries do
		local progress = if mastery.nextXp then ("%d / %d"):format(mastery.xp, mastery.nextXp) else "max"
		local reward = if mastery.nextReward then "  · next title: " .. mastery.nextReward else ""
		line(("%s %d/10 — %s%s"):format(mastery.track, mastery.level, progress, reward), TEXT, 13, nextOrder())
	end
	if #view.titles > 0 then
		line("Titles: " .. table.concat(view.titles, ", "), Color3.fromRGB(200, 180, 255), 12, nextOrder())
	end
	if not PlaceConfig.IsLobby() then
		line("Rebirth and perks are in the lobby.", TEXT, 12, nextOrder())
		return
	end
	line("Rebirth", GOLD, 15, nextOrder())
	local rebirth = view.rebirth
	line(
		("Needs level %d (you: %d) and %d Guardian Legendary extraction(s) since your last rebirth (you: %d)."):format(
			rebirth.levelNeeded,
			view.level,
			rebirth.legendariesNeeded,
			rebirth.legendaries
		),
		TEXT,
		12,
		nextOrder()
	)
	local eligible = view.level >= rebirth.levelNeeded and rebirth.legendaries >= rebirth.legendariesNeeded
	button("Review rebirth…", eligible, nextOrder(), confirmRebirth)
	line("Perk shop", GOLD, 15, nextOrder())
	for _, perkId in PerkCatalog.ORDER do
		local perk = PerkCatalog.Perks[perkId]
		local rank = rebirth.ownedPerks[perkId] or 0
		local cost = ProgressionRules.PerkCost(perkId, rank)
		local label = ("%s %d/%d — %s"):format(perk.name, rank, #perk.costs, perk.description)
		line(label, TEXT, 12, nextOrder())
		if cost then
			button(("Buy rank %d (%d tokens)"):format(rank + 1, cost), rebirth.tokens >= cost, nextOrder(), function()
				local ok, reason = invoke("BuyPerk", perkId, HttpService:GenerateGUID(false))
				ui.status.Text = if ok then perk.name .. " upgraded." else ("Not bought: " .. tostring(reason))
			end)
		end
	end
end

local function popup(payload)
	local text = if payload.amount > 0 then ("+%d XP · %s"):format(payload.amount, payload.reason) else payload.reason
	if payload.levelUp then
		text = "▲ " .. text
	end
	local label = make("TextLabel", {
		Text = text,
		Size = UDim2.new(1, 0, 0, 18),
		BackgroundTransparency = 1,
		TextColor3 = if payload.levelUp then GOLD else Color3.fromRGB(200, 230, 255),
		TextStrokeTransparency = 0.4,
		Font = Enum.Font.GothamBold,
		TextSize = if payload.levelUp then 16 else 13,
	}, ui.popups)
	task.delay(2.5, function()
		label:Destroy()
	end)
end

local function build()
	-- Above the always-open lobby panel.
	local gui = make(
		"ScreenGui",
		{ Name = "Progression", ResetOnSpawn = false, DisplayOrder = 2 },
		player:WaitForChild("PlayerGui")
	)
	ui.bar = make("Frame", {
		AnchorPoint = Vector2.new(0, 1),
		Position = UDim2.new(0, 12, 1, -12),
		Size = UDim2.fromOffset(240, 22),
		BackgroundColor3 = Color3.fromRGB(30, 26, 22),
		BackgroundTransparency = 0.2,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, ui.bar)
	ui.fill = make("Frame", {
		Size = UDim2.fromScale(0, 1),
		BackgroundColor3 = Color3.fromRGB(120, 170, 230),
		BackgroundTransparency = 0.3,
		BorderSizePixel = 0,
	}, ui.bar)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, ui.fill)
	ui.barText = make("TextLabel", {
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
		TextColor3 = Color3.fromRGB(245, 240, 230),
		TextStrokeTransparency = 0.5,
		Font = Enum.Font.GothamBold,
		TextSize = 12,
	}, ui.bar)
	-- In the world the Survival HUD sits above the XP bar, so pop-ups go above it.
	ui.popups = make("Frame", {
		AnchorPoint = Vector2.new(0, 1),
		Position = UDim2.new(0, 12, 1, if PlaceConfig.IsWorld() then -152 else -40),
		Size = UDim2.fromOffset(320, 120),
		BackgroundTransparency = 1,
	}, gui)
	make("UIListLayout", { VerticalAlignment = Enum.VerticalAlignment.Bottom, Padding = UDim.new(0, 2) }, ui.popups)
	-- The new HUD replaces the level bar while it is on screen and hosts the
	-- pop-ups; whenever it is hidden (world menu, protected, dead) this bar shows.
	local function refreshBar()
		ui.bar.Visible = not (HudMode.ReplacesLegacy() and HudMode.IsVisible())
	end
	HudMode.VisibilityChanged:Connect(refreshBar)
	refreshBar()
	placePopups()

	ui.panel = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.new(0.45, 0, 0.75, 0),
		BackgroundColor3 = Color3.fromRGB(24, 20, 17),
		Active = true,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.panel)
	make("UISizeConstraint", { MaxSize = Vector2.new(520, 620), MinSize = Vector2.new(300, 300) }, ui.panel)
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
	ui.list = make("ScrollingFrame", {
		Position = UDim2.fromOffset(10, 34),
		Size = UDim2.new(1, -20, 1, -66),
		BackgroundTransparency = 1,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		CanvasSize = UDim2.new(),
		ScrollBarThickness = 6,
	}, ui.panel)
	make("UIListLayout", { Padding = UDim.new(0, 4), SortOrder = Enum.SortOrder.LayoutOrder }, ui.list)
	ui.status = make("TextLabel", {
		Text = "",
		AnchorPoint = Vector2.new(0, 1),
		Position = UDim2.new(0, 10, 1, -6),
		Size = UDim2.new(1, -20, 0, 22),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = TEXT,
		Font = Enum.Font.Gotham,
		TextSize = 13,
	}, ui.panel)

	ui.confirm = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(420, 0),
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
	ui.confirmText = make("TextLabel", {
		Size = UDim2.new(1, 0, 0, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextWrapped = true,
		TextColor3 = TEXT,
		Font = Enum.Font.GothamMedium,
		TextSize = 14,
		LayoutOrder = 1,
		ZIndex = 5,
	}, ui.confirm)
	local function confirmButton(text: string, order: number, onClick)
		local b = make("TextButton", {
			Text = text,
			Size = UDim2.new(1, 0, 0, 30),
			BackgroundColor3 = Color3.fromRGB(110, 70, 30),
			TextColor3 = Color3.fromRGB(255, 240, 220),
			Font = Enum.Font.GothamBold,
			TextSize = 14,
			LayoutOrder = order,
			ZIndex = 5,
		}, ui.confirm)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
		b.Activated:Connect(onClick)
	end
	confirmButton("Rebirth now", 2, function()
		ui.confirm.Visible = false
		local ok, reason = invoke("Rebirth", HttpService:GenerateGUID(false))
		ui.status.Text = if ok then "Reborn. Your tokens are ready to spend." else ("Not reborn: " .. tostring(reason))
	end)
	confirmButton("Cancel", 3, function()
		ui.confirm.Visible = false
	end)
end

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function ProgressionController.Toggle()
	ui.panel.Visible = not ui.panel.Visible
	ui.confirm.Visible = false
	if ui.panel.Visible then
		ui.status.Text = ""
		renderPanel()
	end
end

function ProgressionController.Start()
	build()
	Remotes.Get("ProgressionChanged").OnClientEvent:Connect(function(snapshot)
		view = snapshot
		updateBar()
		if ui.panel.Visible then
			renderPanel()
		end
	end)
	Remotes.Get("XpGained").OnClientEvent:Connect(popup)
	task.spawn(function()
		local snapshot = invoke("ProgressionSnapshot")
		if type(snapshot) == "table" then
			view = snapshot
			updateBar()
		end
	end)
	Binds.Bind("Progression", function(_, state)
		if state == Enum.UserInputState.Begin then
			ProgressionController.Toggle()
		end
		return Enum.ContextActionResult.Pass
	end)
end

return ProgressionController
