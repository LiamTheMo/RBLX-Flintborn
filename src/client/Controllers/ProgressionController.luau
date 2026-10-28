-- Progression UI (GDD §33, §37, §25.4). A level bar with XP pop-ups everywhere; P
-- (or ButtonSelect) opens the parchment Progress window (Hud/ListWindow): the
-- level and mastery tracks with their next milestone, titles, and in the lobby
-- the rebirth tab (Reset / Kept / Gained in plain words before confirming) and
-- the perk shop. In the world the new HUD (HudMode)
-- draws the level bar from Changed/View() and hosts the pop-ups (MountPopups).

local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local PerkCatalog = require(ReplicatedStorage.Shared.Progression.PerkCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local ProgressionRules = require(ReplicatedStorage.Shared.Progression.ProgressionRules)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local ListWindow = require(script.Parent.Parent.Hud.ListWindow)
local Reasons = require(script.Parent.Parent.Ui.Reasons)
local Binds = require(script.Parent.Parent.Ui.Binds)

local ProgressionController = {}

-- The rebirth confirmation arms after this many seconds.
ProgressionController.CONFIRM_DELAY = 1.5
ProgressionController.TABS = {
	{ id = "Overview", label = "Overview", glyph = "pm_glyph_person" },
	{ id = "Perks", label = "Perks", glyph = "pm_glyph_diamond" },
	{ id = "Rebirth", label = "Rebirth", glyph = "pm_glyph_mountain" },
	{ id = "Titles", label = "Titles", glyph = "pm_glyph_sword" },
}

-- Fires (view) with every new progression snapshot.
ProgressionController.Changed = Signal.new()

local player = Players.LocalPlayer
local ui = {}
local view = nil
local popupHost = nil
local window = nil
local tab = "Overview"

local CLOSE_ACTION = "FlintbornProgressClose"

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

-- Shows the rebirth question with what it resets, keeps and gains, in plain words.
local function confirmRebirth()
	local preview = invoke("RebirthPreview")
	if type(preview) ~= "table" then
		window:SetStatus("The rebirth preview could not load. Try again.")
		return
	end
	window:Confirm(
		("RESET: %s\n\nKEPT: %s\n\nGAINED: %s"):format(
			table.concat(preview.reset, "; "),
			table.concat(preview.kept, "; "),
			table.concat(preview.gained, "; ")
		),
		"REBIRTH",
		ProgressionController.CONFIRM_DELAY,
		function()
			local ok, reason = invoke("Rebirth", HttpService:GenerateGUID(false))
			window:SetStatus(
				if ok then "Reborn. Your tokens are ready to spend." else ("Not reborn: " .. Reasons.Text(reason))
			)
		end
	)
end

local function drawOverview()
	local rebirth = view.rebirth
	window:Row({
		key = "Level",
		title = ("Level %d"):format(view.level),
		detail = if view.xpToNext
			then ("%d / %d XP to level %d"):format(view.xp, view.xpToNext, view.level + 1)
			else "Max level: rebirth to keep climbing.",
		glyph = "pm_glyph_person",
		value = ("Rebirths %d"):format(rebirth.count),
	})
	window:Line(("Perk tokens: %d (spent on perks in the lobby)."):format(rebirth.tokens))
	local bonuses = {}
	if view.premium then
		table.insert(bonuses, "Premium +25% XP")
	end
	if view.boosterUntil > workspace:GetServerTimeNow() then
		table.insert(bonuses, "XP booster +50%")
	end
	if #bonuses > 0 then
		window:Line("Active: " .. table.concat(bonuses, " + "), "good")
	end
	window:Section("Masteries")
	for _, mastery in view.masteries do
		window:Row({
			key = mastery.track,
			title = ("%s  %d / 10"):format(mastery.track, mastery.level),
			detail = (if mastery.nextXp then ("%d / %d XP"):format(mastery.xp, mastery.nextXp) else "Mastered")
				.. (if mastery.nextReward then (" · next title: " .. mastery.nextReward) else ""),
			glyph = "pm_glyph_hammer",
			done = mastery.nextXp == nil,
		})
	end
end

local function drawTitles()
	if #view.titles == 0 then
		window:Line("No titles yet. Masteries, quests and the shop award them.", "ink")
		return
	end
	for _, title in view.titles do
		window:Row({ key = title, title = title, glyph = "pm_glyph_diamond", done = true })
	end
end

local function drawRebirth()
	local rebirth = view.rebirth
	window:Line(
		"Rebirth starts your level again in exchange for perk tokens. Review shows exactly what resets, what is kept and what you gain."
	)
	local levelOk = view.level >= rebirth.levelNeeded
	local legendOk = rebirth.legendaries >= rebirth.legendariesNeeded
	window:Row({
		key = "NeedLevel",
		title = ("Reach level %d"):format(rebirth.levelNeeded),
		detail = ("You: level %d"):format(view.level),
		glyph = "pm_glyph_person",
		done = levelOk,
	})
	window:Row({
		key = "NeedLegendary",
		title = ("Extract %d Guardian Legendary"):format(rebirth.legendariesNeeded),
		detail = ("Since your last rebirth: %d"):format(rebirth.legendaries),
		glyph = "pm_glyph_sword",
		done = legendOk,
	})
	window:Buttons({
		{
			label = "REVIEW REBIRTH",
			key = "Review",
			width = 260,
			enabled = levelOk and legendOk,
			onPress = confirmRebirth,
		},
	})
end

local function drawPerks()
	local rebirth = view.rebirth
	window:Line(
		("Perk tokens: %d. Tokens come from rebirths; a respec in the Market refunds them."):format(rebirth.tokens)
	)
	for _, perkId in PerkCatalog.ORDER do
		local perk = PerkCatalog.Perks[perkId]
		local rank = rebirth.ownedPerks[perkId] or 0
		local cost = ProgressionRules.PerkCost(perkId, rank)
		window:Row({
			key = perkId,
			title = ("%s  %d / %d"):format(perk.name, rank, #perk.costs),
			detail = perk.description,
			glyph = "pm_glyph_diamond",
			value = if cost then ("%d token%s"):format(cost, if cost == 1 then "" else "s") else nil,
			done = cost == nil,
			buttons = if cost
				then {
					{
						label = "BUY",
						key = "Buy",
						enabled = rebirth.tokens >= cost,
						onPress = function()
							local ok, reason = invoke("BuyPerk", perkId, HttpService:GenerateGUID(false))
							window:SetStatus(
								if ok then perk.name .. " upgraded." else ("Not bought: " .. Reasons.Text(reason))
							)
						end,
					},
				}
				else nil,
		})
	end
end

function renderPanel()
	window:SetTab(tab)
	window:Begin()
	if view == nil then
		window:Line("Your progress is still loading.", "ink")
	elseif tab == "Titles" then
		drawTitles()
	elseif tab == "Overview" then
		drawOverview()
	elseif not PlaceConfig.IsLobby() then
		window:Line("Rebirth and perks are in the lobby.", "ink")
	elseif tab == "Rebirth" then
		drawRebirth()
	else
		drawPerks()
	end
	window:Finish()
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
	-- In the lobby the lobby HUD's profile panel always shows the level instead.
	local function refreshBar()
		ui.bar.Visible = not ((HudMode.ReplacesLegacy() and HudMode.IsVisible()) or HudMode.ReplacesLobby())
	end
	HudMode.VisibilityChanged:Connect(refreshBar)
	refreshBar()
	placePopups()

	window = ListWindow.new(player:WaitForChild("PlayerGui"), {
		name = "FlintbornProgress",
		title = "PROGRESS",
		tabs = ProgressionController.TABS,
		onTab = function(id)
			tab = id
			window:SetStatus("")
			renderPanel()
		end,
		onClose = function()
			ProgressionController.Toggle()
		end,
	})
	window.screen:Watch()
end

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function ProgressionController.Toggle()
	if window.screen:IsOpen() then
		ContextActionService:UnbindAction(CLOSE_ACTION)
		window:Close()
		return
	end
	window:SetStatus("")
	window:Open(GuiService.SelectedObject ~= nil or UserInputService.GamepadEnabled)
	ContextActionService:BindAction(CLOSE_ACTION, function(_, state)
		if state == Enum.UserInputState.Begin then
			if window:IsConfirming() then
				window:HideConfirm()
			else
				ProgressionController.Toggle()
			end
		end
		return Enum.ContextActionResult.Sink
	end, false, Enum.KeyCode.ButtonB)
	renderPanel()
end

function ProgressionController.Start()
	build()
	Remotes.Get("ProgressionChanged").OnClientEvent:Connect(function(snapshot)
		view = snapshot
		updateBar()
		if window.screen:IsOpen() then
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
