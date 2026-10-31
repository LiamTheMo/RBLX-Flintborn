-- Progression UI (GDD §33, §37, §25.4). A level bar with XP pop-ups everywhere; P
-- (or ButtonSelect) opens the kit Progress window (Hud/ListWindow,
-- docs/ui/ListWindows.md): the level and mastery tracks as bars with their
-- next milestone, titles, and in the lobby the rebirth tab (Reset / Kept /
-- Gained in plain words, confirmed by holding the button) and the perk shop.
-- In the world the new HUD (HudMode) draws the level bar from Changed/View()
-- and hosts the pop-ups (MountPopups); the kit bar here shows only while no
-- HUD does.

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
local JournalModel = require(ReplicatedStorage.Shared.UI.JournalModel)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local Kit = require(script.Parent.Parent.Hud.Kit)
local ListWindow = require(script.Parent.Parent.Hud.ListWindow)
local Reasons = require(script.Parent.Parent.Ui.Reasons)
local Binds = require(script.Parent.Parent.Ui.Binds)

local ProgressionController = {}

-- The rebirth confirmation is a press-and-hold of this many seconds.
ProgressionController.CONFIRM_DELAY = 1.5
ProgressionController.TABS = {
	{ id = "Overview", label = "Overview", icon = "trophy" },
	{ id = "Perks", label = "Perks", icon = "star" },
	{ id = "Rebirth", label = "Rebirth", icon = "totem" },
	{ id = "Titles", label = "Titles", icon = "crown" },
}

-- Fires (view) with every new progression snapshot.
ProgressionController.Changed = Signal.new()

local player = Players.LocalPlayer
local ui = {}
local view = nil
local popupHost = nil
local window = nil
local tab = "Overview"

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
	ui.bar:Set(fraction)
	ui.barText:SetText(
		if view.xpToNext
			then ("Level %d: %d / %d XP"):format(view.level, view.xp, view.xpToNext)
			else ("Level %d (max): rebirth to keep climbing"):format(view.level)
	)
end

local renderPanel

-- Shows the rebirth question with what it resets, keeps and gains, in plain words.
local function confirmRebirth()
	local preview = invoke("RebirthPreview")
	if type(preview) ~= "table" then
		window:SetStatus("The rebirth preview could not load. Try again.", "warn")
		return
	end
	window:Confirm("", "Rebirth", ProgressionController.CONFIRM_DELAY, function()
		local ok, reason = invoke("Rebirth", HttpService:GenerateGUID(false))
		window:SetStatus(
			if ok then "Reborn. Your tokens are ready to spend." else ("Not reborn: " .. Reasons.Text(reason)),
			if ok then "good" else "warn"
		)
	end, {
		title = "Rebirth?",
		size = { 640, 440 },
		rows = {
			{ label = "Reset", text = table.concat(preview.reset, "; ") },
			{ label = "Kept", text = table.concat(preview.kept, "; ") },
			{ label = "Gained", text = table.concat(preview.gained, "; ") },
			{ label = "Hold to confirm", text = "Hold Rebirth until its bar fills." },
		},
	})
end

local function drawOverview()
	local rebirth = view.rebirth
	window:Row({
		key = "Level",
		title = ("Level %d"):format(view.level),
		detail = if view.xpToNext
			then ("%d / %d XP to level %d"):format(view.xp, view.xpToNext, view.level + 1)
			else "Max level: rebirth to keep climbing.",
		glyph = "trophy",
		bar = { value = if view.xpToNext then view.xp / math.max(view.xpToNext, 1) else 1 },
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
	window:Section("Masteries", "star")
	for _, mastery in view.masteries do
		window:Row({
			key = mastery.track,
			title = ("%s  %d / 10"):format(mastery.track, mastery.level),
			detail = (if mastery.nextXp then ("%d / %d XP"):format(mastery.xp, mastery.nextXp) else "Mastered")
				.. (if mastery.nextReward then (" · next title: " .. mastery.nextReward) else ""),
			glyph = JournalModel.TRACK_ICONS[mastery.track] or "star",
			bar = {
				value = if mastery.nextXp then mastery.xp / math.max(mastery.nextXp, 1) else 1,
				fill = "green",
			},
			done = if mastery.nextXp == nil then true else nil,
		})
	end
end

local function drawTitles()
	if #view.titles == 0 then
		window:Line("No titles yet. Masteries, quests and the shop award them.", "ink")
		return
	end
	for _, title in view.titles do
		window:Row({ key = title, title = title, glyph = "crown", done = true })
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
		glyph = "trophy",
		bar = { value = view.level / math.max(rebirth.levelNeeded, 1) },
		done = levelOk,
	})
	window:Row({
		key = "NeedLegendary",
		title = ("Extract %d Guardian Legendary"):format(rebirth.legendariesNeeded),
		detail = ("Since your last rebirth: %d"):format(rebirth.legendaries),
		glyph = "crown_gem",
		done = legendOk,
	})
	window:Buttons({
		{
			label = "Review Rebirth",
			key = "Review",
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
			glyph = "star",
			bar = { value = rank / math.max(#perk.costs, 1), fill = "blue" },
			value = if cost then ("%d token%s"):format(cost, if cost == 1 then "" else "s") else nil,
			done = if cost == nil then true else nil,
			buttons = if cost
				then {
					{
						label = "Buy",
						key = "Buy",
						enabled = rebirth.tokens >= cost,
						onPress = function()
							window:Confirm(
								("Spend %d perk token%s on %s rank %d?"):format(
									cost,
									if cost == 1 then "" else "s",
									perk.name,
									rank + 1
								),
								"Buy",
								0,
								function()
									local ok, reason = invoke("BuyPerk", perkId, HttpService:GenerateGUID(false))
									window:SetStatus(
										if ok
											then perk.name .. " upgraded."
											else ("Not bought: " .. Reasons.Text(reason)),
										if ok then "good" else "warn"
									)
								end,
								{ title = "Buy " .. perk.name .. "?" }
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
	-- Kit type on the world: cream (gold for a level-up) with an ink outline.
	local label = Kit.Text.new(ui.popups, {
		name = "Popup",
		size = { 320, if payload.levelUp then 22 else 18 },
		text = text,
		role = "hudSmall",
		textSize = if payload.levelUp then 17 else 14,
		color = if payload.levelUp then "gold" else "cream",
	}).root
	label.Size = UDim2.new(1, 0, 0, if payload.levelUp then 22 else 18)
	label.TextStrokeColor3 = Kit.Tokens.Color("ink")
	label.TextStrokeTransparency = 0.3
	task.delay(2.5, function()
		label:Destroy()
	end)
end

local function build()
	-- Above the always-open lobby panel.
	local make = Kit.Core.Make
	local gui = make("ScreenGui", {
		Name = "Progression",
		DisplayOrder = 2,
		ResetOnSpawn = false,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, player:WaitForChild("PlayerGui"))
	-- The fallback level bar: the kit's XP fill on its track, the level above it.
	ui.barHolder = make("Frame", {
		Name = "Level",
		AnchorPoint = Vector2.new(0, 1),
		BackgroundTransparency = 1,
		Position = UDim2.new(0, 12, 1, -12),
		Size = UDim2.fromOffset(260, 40),
	}, gui)
	ui.barText = Kit.Text.new(ui.barHolder, {
		name = "Text",
		rect = { 2, 0, 258, 20 },
		text = "",
		role = "hudSmall",
		color = "cream",
		scaled = true,
	})
	ui.barText.root.TextStrokeColor3 = Kit.Tokens.Color("ink")
	ui.barText.root.TextStrokeTransparency = 0.3
	ui.bar = Kit.Bar.new(ui.barHolder, { name = "Bar", rect = { 0, 22, 260, 16 }, fill = "xp", frame = "track" })
	-- In the world the Survival HUD sits above the XP bar, so pop-ups go above it.
	ui.popups = make("Frame", {
		AnchorPoint = Vector2.new(0, 1),
		Position = UDim2.new(0, 12, 1, if PlaceConfig.IsWorld() then -152 else -56),
		Size = UDim2.fromOffset(320, 120),
		BackgroundTransparency = 1,
	}, gui)
	make("UIListLayout", { VerticalAlignment = Enum.VerticalAlignment.Bottom, Padding = UDim.new(0, 2) }, ui.popups)
	-- The new HUD replaces the level bar while it is on screen and hosts the
	-- pop-ups; whenever it is hidden (world menu, protected, dead) this bar shows.
	-- In the lobby the lobby HUD's profile panel always shows the level instead.
	local function refreshBar()
		ui.barHolder.Visible = not ((HudMode.ReplacesLegacy() and HudMode.IsVisible()) or HudMode.ReplacesLobby())
	end
	HudMode.VisibilityChanged:Connect(refreshBar)
	refreshBar()
	placePopups()

	window = ListWindow.new(player:WaitForChild("PlayerGui"), {
		name = "FlintbornProgress",
		title = "Progress",
		icon = "trophy",
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
end

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function ProgressionController.Toggle()
	-- Escape and gamepad B close the question first, then the window (Kit.Modal).
	if window.screen:IsOpen() then
		window:Close()
		return
	end
	window:SetStatus("")
	window:Open(GuiService.SelectedObject ~= nil or UserInputService.GamepadEnabled)
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
