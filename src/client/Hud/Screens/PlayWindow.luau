-- The Play window (docs/ui/PlayScreen.md, mockup art/reference/ui/lobby/05_play.png):
-- the island map with the crater marked, the world's name and detail rows, YOUR
-- PARTY, YOUR EQUIPMENT (the run hotbar) and the PLAY button, or the Ready toggle
-- for a party member who does not lead (ARCHITECTURE §4.5, D16). There is no
-- server picker (D7). Built only from Kit components at the mockup's 1053 × 665
-- window size, in window design px.
--
-- Display only: PlayController feeds it through the setters and reacts to the
-- callbacks (onPlay, onReady, onClose).
--
--   local window = PlayWindow.new({ onPlay = play, onReady = toggleReady })
--   window:SetParty(rows, true)
--   window:Open()

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local PlayModel = require(ReplicatedStorage.Shared.UI.PlayModel)
local IslandMap = require(script.Parent.Parent.IslandMap)
local Kit = require(script.Parent.Parent.Kit)

local PlayWindow = {}
PlayWindow.__index = PlayWindow

PlayWindow.GUI_NAME = "FlintbornPlay"
-- The mockup's window is 1053 × 665 from outline to outline. The frame art's
-- outline sits ART_INSET px inside its rect, so the window is drawn that much
-- larger and its content offset by it (layout below stays in mockup px).
PlayWindow.ART_INSET = { 6, 5 }
PlayWindow.CONTENT = { 1053, 665 }
PlayWindow.SIZE = { 1053 + 11, 665 + 10 }
-- The game's own island painting (D19), shared with the Journal and Map
-- (atlas_island). It has no Kit role yet, so it is named here.
PlayWindow.MAP_ART = "pm_map_island"

-- Window design px, measured from the mockup (PlayScreen.md element tree, minus
-- the window's top-left 309, 127). Art with a transparent margin (plaques, slots,
-- the close and PLAY plates) gets a rect that much larger, so its visible edge
-- lands on the mockup's.
local RECT = {
	titlePlaque = { 43, 27, 284, 94 },
	-- The title's ink sits a little left of and below the plaque's centre.
	titleShift = { -4, 3 },
	close = { 983, 8, 58, 55 },
	map = { 41, 92, 520, 542 },
	mapInset = 6,
	marker = 28,
	-- The rune the mockup paints in the map's top-left corner (sea there).
	rune = { 76, 154, 41, 69 },
	status = { 60, 636, 500, 20 },
	regionPlaque = { 583, 93, 428, 76 },
	sectionRule = { 588, 332, 419, 15 },
	partyHeading = { 590, 350, 300, 26 },
	party = { 587, 378, 441, 58 },
	partyRow = { 421, 56 },
	equipHeading = { 589, 446, 260, 28 },
	more = { 760, 446, 248, 28 },
	slotY = 477,
	slotSize = { 75, 81 },
	play = { 586, 567, 420, 77 },
}
-- Detail rows: centre y of each row, the icon / label / value columns, rules.
local DETAIL = {
	rows = { 191, 230, 269, 308 },
	icon = { 599, 34, 30 },
	label = { 658, 160 },
	value = { 830, 176 },
	rule = { 648, 354 },
	ruleY = { 211, 250, 290 },
}
PlayWindow.SLOT_X = { 576, 651, 726, 801, 874, 948 }

-- Mockup text sizes (ink-height matched; PlayScreen.md measurements log).
local TEXT_SIZE = {
	title = 64,
	region = 45,
	detail = 16,
	heading = 20,
	name = 16,
	level = 15,
	play = 40,
	status = 14,
}

export type Props = {
	parent: Instance?,
	onPlay: (() -> ())?,
	onReady: (() -> ())?,
	onClose: (() -> ())?,
}

export type PartyRow = {
	userId: number,
	name: string,
	level: number?,
	leader: boolean,
	ready: boolean?,
}

function PlayWindow.new(props: Props)
	local self = setmetatable({ props = props, rows = {}, mode = "solo", ready = false }, PlayWindow)
	local screen = Kit.Screen.new(PlayWindow.GUI_NAME, {
		size = PlayWindow.SIZE,
		parent = props.parent,
		onClose = props.onClose,
	})
	self.screen = screen
	-- The close button is drawn at the mockup's spot below (showClose = false).
	local window = Kit.Window.new(screen, { title = "Play", header = "plaque", showClose = false })
	self.window = window
	local inset = PlayWindow.ART_INSET
	-- Under the title plaque, which overlaps the map's top edge as in the mockup.
	local v = Kit.Core.Make("Frame", {
		Name = "Content",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(inset[1], inset[2]),
		Size = UDim2.fromOffset(PlayWindow.CONTENT[1], PlayWindow.CONTENT[2]),
		ZIndex = window.base.z + 1,
	}, window.base.visual)
	self.visual = v
	local z = window.base.z + 3
	self:_titlePlaque()
	self.close = Kit.IconButton.new(v, {
		name = "Close",
		variant = "close",
		rect = RECT.close,
		zIndex = z + 4,
		onPress = function()
			screen:Close()
		end,
	})
	self:_map(v, z)
	self.regionPlaque = Kit.Panel.new(v, {
		name = "RegionPlaque",
		rect = RECT.regionPlaque,
		variant = "plaque",
		pad = 0,
		zIndex = z,
	})
	local rp = RECT.regionPlaque
	self.regionTitle = Kit.Core.Label(v, {
		name = "RegionTitle",
		text = PlayModel.WORLD_NAME,
		-- The mockup's region name is Bold, not the display weight.
		role = "itemTitle",
		size = TEXT_SIZE.region,
		align = "Center",
		-- Centred 4 px left of the plaque's centre, as the mockup draws it.
		rect = { rp[1] - 4, rp[2], rp[3], rp[4] - 4 },
		z = z + 1,
	})
	self:_details(v, z)
	Kit.Divider.new(v, { name = "SectionRule", rect = RECT.sectionRule, variant = "rule", zIndex = z })
	self.partyHeading = Kit.Text.new(v, {
		name = "PartyHeading",
		rect = RECT.partyHeading,
		text = "Your Party",
		role = "sectionHeader",
		zIndex = z,
	})
	self.partyList = Kit.Scroll.new(v, {
		name = "Party",
		rect = RECT.party,
		gap = 6,
		padBottom = 0,
		contentHeight = RECT.partyRow[2],
		zIndex = z,
	})
	self.equipHeading = Kit.Text.new(v, {
		name = "EquipmentHeading",
		rect = RECT.equipHeading,
		text = "Your Equipment",
		role = "sectionHeader",
		zIndex = z,
	})
	self.more = Kit.Text.new(v, {
		name = "More",
		rect = RECT.more,
		text = "",
		role = "small",
		align = "Right",
		zIndex = z,
	})
	self.slots = {}
	for index, x in PlayWindow.SLOT_X do
		local slot = Kit.Slot.new(v, {
			name = "Slot" .. index,
			variant = "hotbar",
			rect = { x, RECT.slotY, RECT.slotSize[1], RECT.slotSize[2] },
			hotkey = tostring(index),
			zIndex = z,
		})
		-- Slots only show the loadout: gamepad selection skips them.
		slot.control.hit.Selectable = false
		self.slots[index] = slot
	end
	self.play = Kit.Button.new(v, {
		name = "Play",
		rect = RECT.play,
		label = "Play",
		icon = "play",
		variant = "play",
		sizeClass = "l",
		textSize = TEXT_SIZE.play,
		zIndex = z + 1,
		onPress = function()
			if props.onPlay then
				props.onPlay()
			end
		end,
	})
	self.readyButton = Kit.Button.new(v, {
		name = "Ready",
		rect = RECT.play,
		label = "Ready",
		variant = "play",
		sizeClass = "l",
		textSize = TEXT_SIZE.play,
		zIndex = z + 1,
		visible = false,
		onPress = function()
			if props.onReady then
				props.onReady()
			end
		end,
	})
	self.status = Kit.Core.Label(v, {
		name = "Status",
		text = "",
		role = "body",
		size = TEXT_SIZE.status,
		align = "Center",
		scaled = true,
		rect = RECT.status,
		z = z,
	})
	self.status.Visible = false
	-- Gamepad: PLAY (or Ready) first; up reaches the close button.
	for _, button in { self.play, self.readyButton } do
		button.control.hit.NextSelectionUp = self.close.control.hit
	end
	self.close.control.hit.NextSelectionDown = self.play.control.hit
	screen:SetDefaultSelection(self.play.control.hit)
	self:SetLoadout({}, 0)
	return self
end

-- The Kit plaque header, at the mockup's size with its 64 px title (Kit.Window
-- draws the plaque at 44, 24 and the title at windowTitle size).
function PlayWindow:_titlePlaque()
	local title = self.window.title
	local plaque = title.root.Parent :: Frame
	local r = RECT.titlePlaque
	local inset = PlayWindow.ART_INSET
	plaque.Position = UDim2.fromOffset(r[1] + inset[1], r[2] + inset[2])
	plaque.Size = UDim2.fromOffset(r[3], r[4])
	title.root.Position = UDim2.fromOffset(RECT.titleShift[1], RECT.titleShift[2])
	title.root.Size = UDim2.fromOffset(r[3], r[4] - 4)
	title.root.TextSize = TEXT_SIZE.title
end

-- The island painting in an inset frame, cropped to fill it, with the crater
-- the world is named for marked on it.
function PlayWindow:_map(v: Frame, z: number)
	local r = RECT.map
	local frame = Kit.Panel.new(v, { name = "Map", rect = r, variant = "inset", pad = 0, zIndex = z - 1 })
	self.mapPanel = frame
	local inset = RECT.mapInset
	local w, h = r[3] - inset * 2, r[4] - inset * 2
	local clip = Kit.Core.Make("Frame", {
		Name = "Clip",
		BackgroundTransparency = 1,
		ClipsDescendants = true,
		Position = UDim2.fromOffset(inset, inset),
		Size = UDim2.fromOffset(w, h),
		ZIndex = z,
	}, frame.base.visual)
	local side = math.max(w, h)
	local left, top = (w - side) / 2, (h - side) / 2
	self.mapArt = Kit.Art.Sprite(PlayWindow.MAP_ART, side, side, clip, {
		Name = "Island",
		Position = UDim2.fromOffset(left, top),
		Size = UDim2.fromOffset(side, side),
		ZIndex = z,
	})
	Kit.Icon.new(v, { name = "Rune", rect = RECT.rune, icon = "lk_emblem_rune", zIndex = z + 1 })
	local u, vv = PlayModel.MarkerUV(IslandMap.MAP_SPAN)
	local m = RECT.marker
	self.marker = Kit.Icon.new(clip, {
		name = "Marker",
		rect = { left + u * side - m / 2, top + vv * side - m / 2, m, m },
		icon = "cross",
		zIndex = z + 1,
	})
end

function PlayWindow:_details(v: Frame, z: number)
	self.details = {}
	for index, cy in DETAIL.rows do
		local icon = Kit.Icon.new(v, {
			name = "DetailIcon" .. index,
			rect = { DETAIL.icon[1], cy - DETAIL.icon[3] / 2, DETAIL.icon[2], DETAIL.icon[3] },
			icon = "mountain",
			zIndex = z,
		})
		local label = Kit.Core.Label(v, {
			name = "DetailLabel" .. index,
			text = "",
			role = "rowTitle",
			size = TEXT_SIZE.detail,
			rect = { DETAIL.label[1], cy - 11, DETAIL.label[2], 24 },
			z = z,
		})
		local value = Kit.Core.Label(v, {
			name = "DetailValue" .. index,
			text = "",
			role = "rowTitle",
			size = TEXT_SIZE.detail,
			scaled = true,
			rect = { DETAIL.value[1], cy - 11, DETAIL.value[2], 24 },
			z = z,
		})
		self.details[index] = { icon = icon, label = label, value = value }
	end
	for index, y in DETAIL.ruleY do
		Kit.Divider.new(v, {
			name = "DetailRule" .. index,
			rect = { DETAIL.rule[1], y - 7, DETAIL.rule[2], 15 },
			variant = "rule",
			zIndex = z - 1,
		})
	end
end

-- The four detail rows: {icon, label, value}.
function PlayWindow:SetDetails(rows)
	for index, entry in self.details do
		local row = rows[index]
		entry.icon.root.Visible = row ~= nil
		if row then
			if entry.icon.id ~= row.icon then
				entry.icon:SetIcon(row.icon)
			end
			entry.label.Text = row.label
			entry.value.Text = row.value
		else
			entry.label.Text = ""
			entry.value.Text = ""
		end
	end
end

-- One party row: crown (leader), headshot, name, ready dot (in a party), level.
local function partyRow(parent: Instance, row: PartyRow, order: number, showReady: boolean)
	local w, h = RECT.partyRow[1], RECT.partyRow[2]
	local holder = Kit.Core.Make("Frame", {
		Name = "Member" .. order,
		BackgroundTransparency = 1,
		LayoutOrder = order,
		Size = UDim2.fromOffset(w, h),
	}, parent)
	holder:SetAttribute("UserId", row.userId)
	-- The mockup's row is a light inset box, not the list-row plate.
	Kit.Art.Plate(holder, "panel.inset", w, h, { z = 5 })
	if row.leader then
		Kit.Icon.new(holder, { name = "Crown", rect = { 15, 16, 27, 23 }, icon = "crown", zIndex = 6 })
	end
	Kit.Portrait.new(holder, { name = "Portrait", rect = { 51, 2, 52, 52 }, userId = row.userId, zIndex = 6 })
	Kit.Core.Label(holder, {
		name = "Name",
		text = row.name,
		role = "rowTitle",
		color = "ink",
		size = TEXT_SIZE.name,
		rect = { 120, 2, 200, h - 2 },
		z = 6,
	})
	local levelText = if row.level then HudModel.LevelText(row.level) else ""
	Kit.Core.Label(holder, {
		name = "Level",
		text = levelText,
		role = "hudSmall",
		size = TEXT_SIZE.level,
		align = "Right",
		rect = { w - 120, 2, 101, h - 2 },
		z = 6,
	})
	if showReady then
		local levelW = Kit.Text.Width(levelText, "hudSmall", TEXT_SIZE.level)
		local d = 16
		local dot = Kit.Core.Make("Frame", {
			Name = if row.ready then "Ready" else "NotReady",
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(w - 20 - levelW - 10 - d, (h - d) / 2 - 1),
			Size = UDim2.fromOffset(d, d),
			ZIndex = 6,
		}, holder)
		Kit.Art.Plate(dot, if row.ready then "dot.green" else "dot.grey", d, d, { z = 6 })
	end
	return holder
end

-- The party rows (leader first; PlayModel.Members). `showReady` adds each
-- member's ready dot (in a party; a solo player has none, as in the mockup).
function PlayWindow:SetParty(rows: { PartyRow }, showReady: boolean)
	local content = self.partyList:Content()
	for _, child in content:GetChildren() do
		if child:IsA("Frame") then
			child:Destroy()
		end
	end
	for order, row in rows do
		partyRow(content, row, order, showReady)
	end
	local h = RECT.partyRow[2]
	self.partyList:SetContentHeight(#rows * h + math.max(0, #rows - 1) * 6)
	self.rows = rows
end

-- The run hotbar (slot -> {catalogId, quantity, permanent}) and how many more
-- stacks go to the backpack.
function PlayWindow:SetLoadout(hotbar, more: number?)
	for index, slot in self.slots do
		slot:SetItem(hotbar[index])
	end
	self.more:SetText(PlayModel.MoreText(more) or "")
end

-- "solo" / "leader": the PLAY button; "member": the Ready toggle (leather READY
-- while not ready, parchment NOT READY once ready).
function PlayWindow:SetMode(mode: string, ready: boolean?)
	self.mode = mode
	self.ready = ready == true
	local member = mode == "member"
	self.play.root.Visible = not member
	self.readyButton.root.Visible = member
	if member then
		self.readyButton:SetVariant(if self.ready then "playSecondary" else "play")
		self.readyButton:SetLabel(if self.ready then "Not Ready" else "Ready")
	end
	self.screen:SetDefaultSelection((if member then self.readyButton else self.play).control.hit)
end

-- The big button's busy state (a request in flight).
function PlayWindow:SetBusy(busy: boolean)
	self.play:SetBusy(busy)
	self.readyButton:SetBusy(busy)
end

function PlayWindow:SetEnabled(enabled: boolean)
	self.play:SetEnabled(enabled)
	self.readyButton:SetEnabled(enabled)
end

-- The status line under the map (deploy progress, failures, maintenance, the
-- member caption); nil hides it.
function PlayWindow:SetStatus(text: string?)
	local shown = text ~= nil and text ~= ""
	self.status.Visible = shown
	self.status.Text = text or ""
	if shown then
		Kit.Motion.Set(self.status, { TextTransparency = 1 })
		Kit.Motion.Play(self.status, "hover", { TextTransparency = 0 })
	end
end

function PlayWindow:Open(gamepad: boolean?)
	self.screen:Open(gamepad)
end

function PlayWindow:Close()
	self.screen:Close()
end

function PlayWindow:Toggle(gamepad: boolean?)
	self.screen:Toggle(gamepad)
end

function PlayWindow:IsOpen(): boolean
	return self.screen:IsOpen()
end

function PlayWindow:Destroy()
	for _, slot in self.slots do
		slot:Destroy()
	end
	self.play:Destroy()
	self.readyButton:Destroy()
	self.close:Destroy()
	self.partyList:Destroy()
	self.window:Destroy()
	self.screen:Destroy()
end

return PlayWindow
