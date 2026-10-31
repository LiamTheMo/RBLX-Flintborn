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

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local PlayModel = require(ReplicatedStorage.Shared.UI.PlayModel)
local IslandMap = require(script.Parent.Parent.IslandMap)
local Kit = require(script.Parent.Parent.Kit)

local PlayWindow = {}
PlayWindow.__index = PlayWindow

PlayWindow.GUI_NAME = "FlintbornPlay"
-- The mockup's window, outline to outline (309..1361 × 127..791).
PlayWindow.SIZE = { 1053, 663 }

-- Window design px, measured from the mockup (PlayScreen.md element tree, minus
-- the window's top-left 309, 127). Kit plates draw their visible edge on the rect.
local RECT = {
	titlePlaque = { 47, 30, 276, 87 },
	-- The title's ink sits a little left of the plaque's centre.
	title = { -4, 3, 276, 83 },
	close = { 985, 9, 54, 52 },
	map = { 41, 92, 520, 542 },
	-- The painting sits inside the paper sheet with a margin, as the mockup
	-- draws its map on a sheet of paper.
	mapInset = 17,
	marker = 28,
	-- The rune the mockup paints in the map's top-left corner (sea there),
	-- in ink so it reads on the sea.
	rune = { 76, 154, 41, 69 },
	-- Messages sit on a paper plaque over the map's bottom edge, clear of the
	-- window frame under it.
	statusPlaque = { 70, 580, 462, 40 },
	regionPlaque = { 585, 96, 423, 70 },
	sectionRule = { 588, 339, 419, 2 },
	partyHeading = { 590, 350, 300, 26 },
	-- One row tall; more members scroll (the rail sits right of the rows).
	party = { 585, 375, 444, 63 },
	-- A row's slot in the list, and where the mockup's 421 × 56 box (896, 507)
	-- sits in it; the kit draws the box's border on that rect.
	partyRow = { 424, 61 },
	rowArt = { 2, 3 },
	equipHeading = { 589, 446, 260, 28 },
	more = { 760, 446, 248, 28 },
	slotY = 479,
	slotSize = { 71, 77 },
	play = { 586, 569, 416, 72 },
	-- The play glyph: its cream fill is 29 × 35 in the mockup (the art's dark
	-- outline and margin make the square larger), and its gap to the label.
	playIcon = 46,
	playGap = 15,
}
-- Detail rows: centre y of each row, the icon / label / value columns, rules.
local DETAIL = {
	rows = { 191, 230, 269, 308 },
	icon = { 599, 34, 30 },
	label = { 658, 160 },
	value = { 830, 176 },
	-- Phones and touch tablets: the values start further left, so a long one
	-- ("10 · Low to Extreme") keeps 9 screen px.
	phoneValue = { 790, 216 },
	rule = { 648, 354 },
	ruleY = { 211, 250, 290 },
}
PlayWindow.SLOT_X = { 578, 653, 728, 803, 876, 950 }

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
	-- "+1 more in your backpack": larger on phones (9 screen px at the
	-- window's phone scale, about 0.48 on the smallest).
	more = 13,
	morePhone = 16,
}

export type Props = {
	parent: Instance?,
	onPlay: (() -> ())?,
	onReady: (() -> ())?,
	onClose: (() -> ())?,
}

-- The status plaque's text inset and size.
local STATUS_PAD = 16

export type PartyRow = {
	userId: number,
	name: string,
	level: number?,
	leader: boolean,
	ready: boolean?,
}

function PlayWindow.new(props: Props)
	local self = setmetatable({
		props = props,
		rows = {},
		rowMaids = {},
		loadout = {},
		mode = "solo",
		ready = false,
		moreText = "",
		phone = Kit.Scale.IsSmallTouch(),
		maid = KitModel.Maid(),
	}, PlayWindow)
	local screen = Kit.Screen.new(PlayWindow.GUI_NAME, {
		size = PlayWindow.SIZE,
		parent = props.parent,
		onClose = props.onClose,
	})
	self.screen = screen
	local window = Kit.Window.new(screen, {
		title = "Play",
		header = "plaque",
		plaqueRect = RECT.titlePlaque,
		titleRect = RECT.title,
		titleSize = TEXT_SIZE.title,
		closeRect = RECT.close,
	})
	self.window = window
	self.close = window.close
	-- Under the title plaque, which overlaps the map's top edge as in the mockup.
	local v = Kit.Core.Make("Frame", {
		Name = "Content",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		ZIndex = window.base.z + 1,
	}, window.base.visual)
	self.visual = v
	local z = window.base.z + 3
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
		rect = { rp[1] - 4, rp[2] + 1, rp[3], rp[4] - 4 },
		z = z + 1,
	})
	self:_details(v, z)
	Kit.Divider.new(v, { name = "SectionRule", rect = RECT.sectionRule, variant = "hairline", zIndex = z })
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
	self.moreZ = z
	self:_buildMore()
	self.slots = {}
	self.tooltips = {}
	for index, x in PlayWindow.SLOT_X do
		local slot = Kit.Slot.new(v, {
			name = "Slot" .. index,
			variant = "hotbar",
			rect = { x, RECT.slotY, RECT.slotSize[1], RECT.slotSize[2] },
			hotkey = tostring(index),
			zIndex = z,
		})
		-- Slots show the loadout; a gamepad can select one to read its item
		-- (the tooltip names it), as a mouse hovers it.
		self.tooltips[index] = Kit.Tooltip.Attach(slot, function()
			return self:_slotText(index)
		end)
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
		iconSize = RECT.playIcon,
		iconGap = RECT.playGap,
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
	local sp = RECT.statusPlaque
	self.statusPlaque = Kit.Panel.new(v, {
		name = "StatusPlaque",
		rect = sp,
		variant = "plaque",
		pad = 0,
		zIndex = z + 2,
		visible = false,
	})
	self.status = Kit.Core.Label(v, {
		name = "Status",
		text = "",
		role = "body",
		size = TEXT_SIZE.status,
		align = "Center",
		wrap = true,
		scaled = true,
		rect = { sp[1] + STATUS_PAD, sp[2] + 4, sp[3] - STATUS_PAD * 2, sp[4] - 8 },
		z = z + 3,
	})
	self.status.Visible = false
	-- Gamepad: PLAY (or Ready) first; up reaches the loadout slots, then the
	-- close button.
	for _, button in { self.play, self.readyButton } do
		button.control.hit.NextSelectionUp = self.slots[1].control.hit
	end
	for index, slot in self.slots do
		local hit = slot.control.hit
		hit.NextSelectionLeft = if self.slots[index - 1] then self.slots[index - 1].control.hit else nil
		hit.NextSelectionRight = if self.slots[index + 1] then self.slots[index + 1].control.hit else nil
		hit.NextSelectionDown = self.play.control.hit
		hit.NextSelectionUp = self.close.control.hit
	end
	self.close.control.hit.NextSelectionDown = self.play.control.hit
	screen:SetDefaultSelection(self.play.control.hit)
	self:SetLoadout({}, 0)
	-- The slots' 1–6 badges are keyboard keys: shown only while one is in use.
	self.maid:Give(Kit.Input.Watch(function()
		self:_hotkeys()
	end))
	self:_hotkeys()
	-- Phone and desktop text sizes follow the screen and the input devices.
	self.maid:Give(Kit.Scale.OnFormFactorChanged(function()
		local phone = Kit.Scale.IsSmallTouch()
		if phone ~= self.phone then
			self.phone = phone
			self:_buildMore()
			self:_placeValues()
		end
	end))
	return self
end

function PlayWindow:_hotkeys()
	local kind = Kit.Input.Type()
	local keys = kind == "mouse" or kind == "keyboard"
	for index, slot in self.slots do
		slot:SetHotkey(if keys then tostring(index) else nil)
	end
end

-- The "+n more" line (rebuilt when the form factor changes its size).
function PlayWindow:_buildMore()
	if self.more then
		self.more:Destroy()
	end
	self.more = Kit.Text.new(self.visual, {
		name = "More",
		rect = RECT.more,
		text = self.moreText,
		role = "small",
		textSize = if self.phone then TEXT_SIZE.morePhone else TEXT_SIZE.more,
		align = "Right",
		scaled = true,
		zIndex = self.moreZ,
	})
end

-- The detail values' column (further left on phones).
function PlayWindow:_placeValues()
	local value = if self.phone then DETAIL.phoneValue else DETAIL.value
	for index, entry in self.details do
		local cy = DETAIL.rows[index]
		entry.value.Position = UDim2.fromOffset(value[1], cy - 11)
		entry.value.Size = UDim2.fromOffset(value[2], 24)
	end
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
	-- The game's own island painting (D19), shared with the Journal and Map.
	self.mapArt =
		Kit.Picture.new(clip, { name = "Island", rect = { left, top, side, side }, role = "map.island", zIndex = z })
	Kit.Icon.new(v, { name = "Rune", rect = RECT.rune, icon = "lk_emblem_rune", tint = "ink", zIndex = z + 1 })
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
			-- Scaled text keeps the Kit's 9 screen-px floor on phones.
			scaled = true,
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
	self:_placeValues()
	for index, y in DETAIL.ruleY do
		-- The mockup's faint 1 px rules between the rows.
		Kit.Divider.new(v, {
			name = "DetailRule" .. index,
			rect = { DETAIL.rule[1], y, DETAIL.rule[2], 1 },
			variant = "hairline",
			thickness = 1,
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
-- Every part goes into `maid`, so cleaning it takes the row apart.
local function partyRow(parent: Instance, row: PartyRow, order: number, showReady: boolean, maid)
	local w, h = RECT.partyRow[1], RECT.partyRow[2]
	local outer = Kit.Core.Make("Frame", {
		Name = "Member" .. order,
		BackgroundTransparency = 1,
		LayoutOrder = order,
		Size = UDim2.fromOffset(w, h),
	}, parent)
	outer:SetAttribute("UserId", row.userId)
	maid:Give(outer)
	-- The mockup's row is a light inset box, not the list-row plate.
	local art = RECT.rowArt
	w, h = 421, 56
	Kit.Art.Plate(outer, "panel.inset", w, h, { z = 5, rect = { art[1], art[2], w, h } })
	local holder = Kit.Core.Make("Frame", {
		Name = "Inside",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(art[1], art[2]),
		Size = UDim2.fromOffset(w, h),
		ZIndex = 6,
	}, outer)
	if row.leader then
		maid:Give(Kit.Icon.new(holder, { name = "Crown", rect = { 15, 16, 27, 23 }, icon = "crown", zIndex = 6 }))
	end
	maid:Give(Kit.Portrait.new(holder, {
		name = "Portrait",
		rect = { 51, 2, 52, 52 },
		userId = row.userId,
		-- The headshot fills its box over the row's paper.
		frame = "none",
		backdrop = false,
		zIndex = 6,
	}))
	Kit.Core.Label(holder, {
		name = "Name",
		text = row.name,
		role = "rowTitle",
		color = "ink",
		size = TEXT_SIZE.name,
		scaled = true,
		rect = { 120, 2, 200, h - 2 },
		z = 6,
	})
	local levelText = if row.level then HudModel.LevelText(row.level) else ""
	Kit.Core.Label(holder, {
		name = "Level",
		text = levelText,
		role = "hudSmall",
		size = TEXT_SIZE.level,
		scaled = true,
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
	return outer
end

-- The party rows (leader first; PlayModel.Members). `showReady` adds each
-- member's ready dot (in a party; a solo player has none, as in the mockup).
-- The old rows are taken apart through their maids (Kit components included).
function PlayWindow:SetParty(rows: { PartyRow }, showReady: boolean)
	local content = self.partyList:Content()
	for _, maid in self.rowMaids do
		maid:Clean()
	end
	table.clear(self.rowMaids)
	for order, row in rows do
		local maid = KitModel.Maid()
		partyRow(content, row, order, showReady, maid)
		table.insert(self.rowMaids, maid)
	end
	local h = RECT.partyRow[2]
	self.partyList:SetContentHeight(#rows * h + math.max(0, #rows - 1) * 6)
	self.rows = rows
end

-- The run hotbar (slot -> {catalogId, quantity, permanent}) and how many more
-- stacks go to the backpack.
function PlayWindow:SetLoadout(hotbar, more: number?)
	self.loadout = hotbar
	for index, slot in self.slots do
		local item = hotbar[index]
		-- itemId: the slot takes its art and tint from ItemInfo.
		slot:SetItem(
			if item then { itemId = item.catalogId, quantity = item.quantity, permanent = item.permanent } else nil
		)
	end
	self.moreText = PlayModel.MoreText(more) or ""
	self.more:SetText(self.moreText)
end

-- A loadout slot's tooltip: the item's name and count, or nil when empty.
function PlayWindow:_slotText(index: number): string?
	local item = self.loadout[index]
	if item == nil then
		return nil
	end
	local def = ItemCatalog.Get(item.catalogId)
	local name = if def then def.name else tostring(item.catalogId)
	return if (item.quantity or 1) > 1 then ("%s ×%d"):format(name, item.quantity) else name
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
	self.statusPlaque.root.Visible = shown
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
	self.maid:Clean()
	self.more:Destroy()
	for _, maid in self.rowMaids do
		maid:Clean()
	end
	for _, detach in self.tooltips do
		detach()
	end
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
