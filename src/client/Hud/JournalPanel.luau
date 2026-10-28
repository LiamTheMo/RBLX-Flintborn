-- The parchment Journal (art/reference/ui/parchment/07_journal.png, spec
-- docs/ui/JournalScreen.md): the quest list with All / Daily / Main tabs on the
-- left, the chosen quest's card (objective with its progress bar, rewards and
-- CLAIM) in the middle and the painted island map on the right. The view only
-- draws and reports; JournalController fetches quests and claims rewards.
--
-- Positions are the reference sheet's own pixels (the window art was cut at
-- ORIGIN), so they read straight off the image.

local Layout = require(script.Parent.Layout)
local IslandMap = require(script.Parent.IslandMap)
local Parchment = require(script.Parent.Parchment)
local Widgets = require(script.Parent.Widgets)

local JournalPanel = {}
JournalPanel.__index = JournalPanel

JournalPanel.SIZE = { 1632, 772 }
local ORIGIN = { 20, 18 }

-- Tabs: Daily quests reset each day; Main ones pay once.
JournalPanel.TABS = {
	{ id = "All", label = "All" },
	{ id = "Daily", label = "Daily" },
	{ id = "Once", label = "Main" },
}

-- What each quest counts, as its objective line.
JournalPanel.OBJECTIVES = {
	Harvest = "Gather from resource nodes",
	Extract = "Extract from the island",
	Craft = "Craft items",
	Enemy = "Defeat creatures",
	Cache = "Open supply caches",
	Boss = "Defeat a world boss",
	Guardian = "Defeat the Guardian",
}

-- The place a quest points at on the map, when it has one.
JournalPanel.PLACES = {
	Guardian = "KeepTower",
	Boss = "KeepTower",
}

local ROW_PITCH = 92.5
local ROW_HEIGHT = 86
local LIST = { x = 66, y = 200, w = 372, h = 468 }

local function at(x: number, y: number, w: number, h: number)
	return { x - ORIGIN[1], y - ORIGIN[2], w, h }
end

local function place(object: GuiObject, r)
	object.Position = UDim2.fromOffset(r[1], r[2])
	object.Size = UDim2.fromOffset(r[3], r[4])
end

-- A rounded native rectangle (list backing, reward slots, bars, dots).
local function rounded(parent: Instance, r, color: string?, stroke: string?, radius: number?, z: number?): Frame
	local frame = Widgets.Make("Frame", {
		BackgroundColor3 = Layout.Color(color or "paper"),
		BackgroundTransparency = if color then 0 else 1,
		BorderSizePixel = 0,
		ZIndex = z or 3,
	}, parent) :: Frame
	place(frame, r)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0, radius or 8) }, frame)
	if stroke then
		Widgets.Make("UIStroke", { Color = Layout.Color(stroke), Thickness = 2 }, frame)
	end
	return frame
end

function JournalPanel.new(parent: Instance?, handlers)
	local self = setmetatable({}, JournalPanel)
	self.handlers = handlers
	self.screen = Parchment.Screen("FlintbornJournal", JournalPanel.SIZE, 20, parent)
	local window = self.screen.window
	self.window = window
	self.quests = {}
	self.tab = "All"

	Widgets.Sprite("pm_window_journal", { Name = "Art", Size = UDim2.fromScale(1, 1), ZIndex = 1 }, window)
	local close = Widgets.Make("TextButton", {
		Name = "Close",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(1560 - ORIGIN[1], 50 - ORIGIN[2]),
		Size = UDim2.fromOffset(90, 84),
		ZIndex = 10,
	}, window)
	close.Activated:Connect(function()
		handlers.onClose()
	end)
	self.close = close

	-- Category tabs.
	self.tabs = {}
	local tabRects = { at(63, 144, 122, 54), at(189, 146, 125, 52), at(316, 146, 125, 52) }
	for index, tab in JournalPanel.TABS do
		local r = tabRects[index]
		local holder = Widgets.Make("Frame", { Name = tab.id, BackgroundTransparency = 1, ZIndex = 4 }, window)
		place(holder, r)
		local leather = Widgets.Sprite("pm_jtab_leather", { Size = UDim2.fromScale(1, 1), ZIndex = 4 }, holder)
		local paper = Widgets.Sprite("pm_jtab_paper", { Size = UDim2.fromScale(1, 1), ZIndex = 4 }, holder)
		local label = Parchment.Text(tab.label, { 8, 4, r[3] - 16, r[4] - 6 }, holder, {
			size = 25,
			align = "Center",
			scaled = true,
			z = 5,
		})
		local button = Parchment.Pressable(holder, paper, function()
			self:SelectTab(tab.id)
		end)
		self.tabs[tab.id] = { leather = leather, paper = paper, label = label, button = button }
	end

	-- The list: a darker paper backing with the quest rows scrolling in it.
	rounded(window, at(LIST.x - 2, LIST.y - 6, LIST.w + 4, LIST.h + 12), "listPaper", "listEdge", 10, 2)
	local list = Widgets.Make("ScrollingFrame", {
		Name = "Quests",
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		CanvasSize = UDim2.new(),
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		ScrollingDirection = Enum.ScrollingDirection.Y,
		ScrollBarThickness = 6,
		ScrollBarImageColor3 = Layout.Color("paperEdge"),
		ZIndex = 3,
	}, window) :: ScrollingFrame
	place(list, at(LIST.x, LIST.y, LIST.w, LIST.h))
	Widgets.Make("UIListLayout", {
		Padding = UDim.new(0, ROW_PITCH - ROW_HEIGHT),
		SortOrder = Enum.SortOrder.LayoutOrder,
		HorizontalAlignment = Enum.HorizontalAlignment.Center,
	}, list)
	Widgets.Make("UIPadding", { PaddingTop = UDim.new(0, 6), PaddingBottom = UDim.new(0, 6) }, list)
	self.list = list
	self.rows = {}

	-- The active-quests strip under the list.
	self.strip = Parchment.Button("pm_button_strip", at(76, 675, 354, 76), window, function()
		self:_jumpToClaimable()
	end, { name = "Active", label = "", color = "cream", size = 24 })

	self:_card(window)
	self.map = IslandMap.new(window, at(974, 141, 638, 611), {
		zoomButtons = { at(1546, 540, 62, 62), at(1546, 606, 62, 63) },
	})
	Widgets.Sprite("pm_compass_rose", {
		Name = "Compass",
		Position = UDim2.fromOffset(1500 - ORIGIN[1], 146 - ORIGIN[2]),
		Size = UDim2.fromOffset(93, 117),
		ImageColor3 = Layout.Color("ink"),
		ZIndex = 8,
	}, window)
	self:SelectTab("All")
	return self
end

-- The middle card: icon, title, objective, notes, rewards and CLAIM.
function JournalPanel:_card(window: Instance)
	local card = {}
	Widgets.Sprite("pm_icon_scroll", {
		Name = "Icon",
		Position = UDim2.fromOffset(480 - ORIGIN[1], 152 - ORIGIN[2]),
		Size = UDim2.fromOffset(118, 106),
		ZIndex = 4,
	}, window)
	card.title = Parchment.Text("", at(606, 160, 312, 76), window, {
		size = 42,
		scaled = true,
		minSize = 20,
		wrap = true,
		name = "Title",
	})
	Parchment.Divider(at(476, 241, 446, 28), window)
	-- The objective: box (ticked when done), name, bar and count.
	card.boxOff = Widgets.Sprite("pm_check_off", {
		Name = "Open",
		Position = UDim2.fromOffset(484 - ORIGIN[1], 287 - ORIGIN[2]),
		Size = UDim2.fromOffset(31, 32),
		ZIndex = 4,
	}, window)
	card.boxOn = Widgets.Sprite("pm_check_green", {
		Name = "Done",
		Position = UDim2.fromOffset(484 - ORIGIN[1], 287 - ORIGIN[2]),
		Size = UDim2.fromOffset(34, 34),
		ZIndex = 4,
	}, window)
	card.objective = Parchment.Text("", at(534, 284, 380, 36), window, { size = 22, scaled = true })
	local track = rounded(window, at(535, 321, 305, 21), "sliderTrack", nil, 10, 4)
	Widgets.Make("UIStroke", { Color = Layout.Color("ink"), Thickness = 1.5 }, track)
	-- Gold while under way, green when done.
	card.fill = Widgets.Fill("sliderFill", { Size = UDim2.fromScale(0.5, 1), ZIndex = 5 }, track)
	card.fillDone = Widgets.Fill("questDone", { Size = UDim2.fromScale(1, 1), ZIndex = 5 }, track)
	card.count = Parchment.Text("", at(850, 312, 82, 38), window, { size = 24, scaled = true, minSize = 14 })
	-- Notes: tier, how often it resets.
	card.notes = Parchment.Text("", at(486, 372, 430, 140), window, {
		size = 20,
		wrap = true,
		color = "inkSoft",
	})
	card.notes.TextYAlignment = Enum.TextYAlignment.Top
	-- A claim's outcome, under the notes.
	card.message = Parchment.Text("", at(486, 478, 430, 32), window, { size = 19, color = "leather", scaled = true })
	Parchment.Divider(at(476, 521, 446, 28), window)
	Parchment.Text("REWARDS", at(487, 558, 200, 26), window, { size = 20 })
	card.slots = {}
	for index = 1, 4 do
		local x = 493 + (index - 1) * 107
		local slot = rounded(window, at(x, 588, 95, 88), nil, "slotEdge", 10, 4)
		local amount = Parchment.Text(
			"",
			{ 4, 54, 87, 32 },
			slot,
			{ size = 23, align = "Center", scaled = true, z = 5 }
		)
		table.insert(card.slots, { frame = slot, amount = amount })
	end
	card.claim = Parchment.Button("pm_button_claim", at(506, 682, 388, 78), window, function()
		if self.selected then
			self.handlers.onClaim(self.selected)
		end
	end, { name = "Claim", label = "CLAIM", color = "cream", size = 40 })
	self.card = card
end

-- Rewards as {sprite, amount text} pairs.
local function rewards(quest)
	local list = { { "pm_icon_coin", tostring(quest.coins or 0) } }
	if quest.gems and quest.gems > 0 then
		table.insert(list, { "pm_icon_gem", tostring(quest.gems) })
	end
	if quest.booster then
		table.insert(list, { "pm_icon_bolt", "XP Boost" })
	end
	return list
end

local function status(quest): string
	if quest.claimed then
		return "claimed"
	elseif quest.count >= quest.needed then
		return "ready"
	end
	return "open"
end
JournalPanel.Status = status

function JournalPanel:_visible()
	local shown = {}
	for _, quest in self.quests do
		if self.tab == "All" or quest.repeats == self.tab then
			table.insert(shown, quest)
		end
	end
	return shown
end

function JournalPanel:_drawList()
	for _, row in self.rows do
		row.holder:Destroy()
	end
	self.rows = {}
	for order, quest in self:_visible() do
		local holder = Widgets.Make("Frame", {
			Name = quest.id,
			BackgroundTransparency = 1,
			LayoutOrder = order,
			Size = UDim2.fromOffset(360, ROW_HEIGHT),
			ZIndex = 4,
		}, self.list)
		local selected = quest.id == self.selected
		local art = Widgets.Sprite(if selected then "pm_quest_row_selected" else "pm_quest_row", {
			Name = "Art",
			Size = UDim2.fromScale(1, 1),
			ZIndex = 4,
		}, holder)
		Parchment.Text(quest.name, { 96, 4, 196, ROW_HEIGHT - 8 }, holder, {
			size = 21,
			scaled = true,
			minSize = 13,
			wrap = true,
			z = 5,
		})
		local state = status(quest)
		local dot =
			rounded(holder, { 293, 30, 26, 26 }, if state == "ready" then "questReady" else "questOpen", "ink", 13, 5)
		if state == "claimed" then
			dot.BackgroundColor3 = Layout.Color("questDone")
		end
		Parchment.Pressable(holder, art, function()
			self:Select(quest.id)
		end)
		table.insert(self.rows, { holder = holder, quest = quest })
	end
end

function JournalPanel:_drawCard()
	local quest = nil
	for _, entry in self.quests do
		if entry.id == self.selected then
			quest = entry
		end
	end
	local card = self.card
	if quest == nil then
		card.title.Text = if #self.quests == 0 then "Loading…" else "No quests here"
		card.objective.Text = ""
		card.count.Text = ""
		card.fill.Visible = false
		card.fillDone.Visible = false
		card.boxOn.Visible = false
		card.boxOff.Visible = false
		card.notes.Text = ""
		for _, slot in card.slots do
			slot.frame.Visible = false
		end
		card.claim.SetEnabled(false)
		self.map:Select(nil)
		return
	end
	local state = status(quest)
	card.title.Text = quest.name
	card.objective.Text = JournalPanel.OBJECTIVES[quest.action or ""] or quest.name
	card.count.Text = ("%d/%d"):format(math.min(quest.count, quest.needed), quest.needed)
	local fraction = if quest.needed > 0 then math.clamp(quest.count / quest.needed, 0, 1) else 1
	card.fill.Visible = fraction > 0 and fraction < 1
	card.fill.Size = UDim2.new(fraction, 0, 1, 0)
	card.fillDone.Visible = fraction >= 1
	card.boxOn.Visible = fraction >= 1
	card.boxOff.Visible = fraction < 1
	local kind = if quest.repeats == "Daily" then "Daily quest: resets at midnight UTC." else "Main quest: pays once."
	card.notes.Text = ("%s difficulty. %s%s"):format(
		quest.tier or "Normal",
		kind,
		if state == "claimed" then "\nReward claimed." elseif state == "ready" then "\nDone: claim your reward." else ""
	)
	local list = rewards(quest)
	for index, slot in card.slots do
		local reward = list[index]
		slot.frame.Visible = reward ~= nil
		if slot.icon then
			slot.icon:Destroy()
			slot.icon = nil
		end
		if reward then
			slot.icon = Widgets.Sprite(reward[1], {
				Name = "Icon",
				AnchorPoint = Vector2.new(0.5, 0.5),
				Position = UDim2.fromOffset(47.5, 33),
				Size = UDim2.fromOffset(54, 52),
				ZIndex = 5,
			}, slot.frame)
			slot.amount.Text = reward[2]
		end
	end
	card.claim.label.Text = if state == "claimed" then "CLAIMED" else "CLAIM"
	card.claim.SetEnabled(state == "ready" and not self.claiming)
	local placeId = JournalPanel.PLACES[quest.action or ""]
	self.map:Select(placeId)
	if placeId then
		local pin = self.map.pins[placeId]
		self.map:Focus(pin.place.x, pin.place.z)
	end
end

function JournalPanel:_drawStrip()
	local active = 0
	for _, quest in self.quests do
		if status(quest) ~= "claimed" then
			active += 1
		end
	end
	self.strip.label.Text = ("%d Active Quest%s"):format(active, if active == 1 then "" else "s")
end

function JournalPanel:_jumpToClaimable()
	for _, quest in self:_visible() do
		if status(quest) == "ready" then
			self:Select(quest.id)
			return
		end
	end
end

function JournalPanel:SelectTab(id: string)
	self.tab = id
	for name, tab in self.tabs do
		local on = name == id
		tab.leather.Visible = on
		tab.paper.Visible = not on
		tab.label.TextColor3 = Layout.Color(if on then "cream" else "ink")
	end
	-- Keep the chosen quest if it is on this tab, else the first one.
	local shown = self:_visible()
	local keep = false
	for _, quest in shown do
		keep = keep or quest.id == self.selected
	end
	if not keep then
		self.selected = if shown[1] then shown[1].id else nil
	end
	self:_drawList()
	self:_drawCard()
end

function JournalPanel:Select(id: string)
	if id ~= self.selected then
		self.card.message.Text = ""
	end
	self.selected = id
	self:_drawList()
	self:_drawCard()
end

-- `quests` from the QuestView remote ({id, name, tier, action?, coins, gems?,
-- booster?, count, needed, claimed, repeats}).
function JournalPanel:SetQuests(quests)
	self.quests = quests or {}
	self:_drawStrip()
	self:SelectTab(self.tab)
end

-- A short line under the card's notes (a claim's outcome); "" clears it.
function JournalPanel:SetMessage(text: string)
	self.card.message.Text = text
end

-- While a claim is on its way, CLAIM stays dimmed.
function JournalPanel:SetClaiming(claiming: boolean)
	self.claiming = claiming
	self:_drawCard()
end

return JournalPanel
