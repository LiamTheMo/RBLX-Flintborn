-- The Play window (docs/ui/PlayScreen.md, mockup art/reference/ui/lobby/05_play.png):
-- the island map with the crater marked, the world's name and detail rows, YOUR
-- PARTY, YOUR EQUIPMENT (the run hotbar) and the PLAY button, which only a solo
-- player or the party leader can press (ARCHITECTURE §4.5, D24); other members
-- see it disabled. There is no server picker (D7). Built only from Kit
-- components with the Inventory window's size and chrome (D25: header icon,
-- title, ink underline and close button as in InventoryWindow, the map in an
-- inset panel, section headings instead of plaques), in window design px. The
-- owner's Play rune art (sheet 21, D26) is the header icon and the PLAY
-- button's crystal glyph, and two rune pillars stand at the button's ends.
--
-- Display only: PlayController feeds it through the setters and reacts to the
-- callbacks (onPlay, onClose).
--
--   local window = PlayWindow.new({ onPlay = play })
--   window:SetParty(rows)
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
-- The Inventory window's size and chrome (D25): the same header (icon, title,
-- underline), close button and clasps as InventoryWindow, so the Play window
-- reads as one of the menus rather than mockup 05's plaque style.
PlayWindow.SIZE = { 1187, 650 }

-- Window design px. The header copies InventoryWindow's measured header; the
-- content sits between its underline and the window's bottom edge (the
-- Inventory detail card's 109..629).
local RIGHT_X, RIGHT_W = 575, 590
local RECT = {
	-- InventoryWindow's header: the rune play icon, title, underline, close button.
	icon = { 40, 15, 71, 77 },
	titleX = 138,
	rule = { 113, 78, 995, 16 },
	close = { 1103, 18, 60, 57 },
	-- The map in an inset panel like Inventory's detail card.
	map = { 23, 109, 520, 520 },
	-- The painting sits inside the panel with a margin.
	mapInset = 17,
	marker = 28,
	-- The rune in the map's top-left corner (sea there), in ink so it reads on
	-- the sea; from the map's top-left.
	rune = { 35, 62, 41, 69 },
	-- Messages sit on a paper plaque over the map's bottom edge.
	statusPlaque = { 52, 575, 462, 40 },
	-- The right column: the region heading, detail rows, party, equipment.
	region = { RIGHT_X, 106, RIGHT_W, 44 },
	partyHeading = { RIGHT_X, 302, RIGHT_W, 34 },
	-- One row tall; more members scroll (the rail sits right of the rows).
	party = { RIGHT_X, 343, RIGHT_W, 63 },
	-- A row's slot in the list, and the light inset box drawn in it.
	partyRow = { RIGHT_W - 14, 61 },
	rowArt = { 2, 3 },
	rowBox = { RIGHT_W - 20, 56 },
	equipHeading = { RIGHT_X, 414, RIGHT_W, 34 },
	more = { RIGHT_X + RIGHT_W - 262, 417, 260, 26 },
	slotY = 458,
	slotSize = { 71, 77 },
	-- The PLAY button between its two rune pillars (D26). The pillars
	-- (lk_pillar_rune_*, 88 x 160 stored) are about 1.6x the button's height
	-- and overlap each end by 17 px, like posts holding a banner. They stand
	-- under the loadout slots (bottom 535, 538 with a selected slot's glow),
	-- end inside the window's paper margin (637; the rail starts at about
	-- 642) and keep 5 px inside the right column (1165), clear of the frame's
	-- lower right clasp and corner. The button keeps its own rect as its hit
	-- area; it sits low enough that its touch pad (44 screen px at the
	-- 844 x 390 phone's 0.51 window scale) does not reach the slots' pads.
	play = { 826, 562, 298, 60 },
	pillarLeft = { 790, 541, 53, 96 },
	pillarRight = { 1107, 541, 53, 96 },
	-- The crystal glyph and its gap to the label.
	playIcon = 40,
	playGap = 12,
}
-- Detail rows: centre y of each row, the icon / label / value columns, rules.
local DETAIL = {
	rows = { 173, 207, 241, 275 },
	icon = { RIGHT_X + 10, 34, 30 },
	label = { RIGHT_X + 66, 180 },
	value = { RIGHT_X + 266, 316 },
	-- Phones and touch tablets: the values start further left, so a long one
	-- ("10 · Low to Extreme") keeps 9 screen px.
	phoneValue = { RIGHT_X + 230, 352 },
	rule = { RIGHT_X + 56, RIGHT_W - 56 },
	ruleY = { 190, 224, 258 },
}
PlayWindow.SLOT_X = {}
for index = 1, 6 do
	PlayWindow.SLOT_X[index] = RIGHT_X + (index - 1) * 82
end

-- Mockup text sizes (ink-height matched; PlayScreen.md measurements log).
local TEXT_SIZE = {
	-- InventoryWindow's title size; the region heading as a section heading.
	title = 44,
	region = 26,
	detail = 16,
	heading = 20,
	name = 16,
	level = 15,
	play = 34,
	status = 14,
	-- "+1 more in your backpack": larger on phones (9 screen px at the
	-- window's phone scale, about 0.48 on the smallest).
	more = 13,
	morePhone = 16,
}

export type Props = {
	parent: Instance?,
	onPlay: (() -> ())?,
	onClose: (() -> ())?,
}

-- The status plaque's text inset and size.
local STATUS_PAD = 16

export type PartyRow = {
	userId: number,
	name: string,
	level: number?,
	leader: boolean,
}

function PlayWindow.new(props: Props)
	local self = setmetatable({
		props = props,
		rows = {},
		rowMaids = {},
		loadout = {},
		mode = "solo",
		enabled = true,
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
	-- The same header as InventoryWindow (D25): the Play tile's rune icon
	-- (D26), the title, the plain ink underline and the close button in its
	-- corner.
	local window = Kit.Window.new(screen, {
		title = "Play",
		icon = "icon.playRune",
		clasps = "right",
		claspYs = { 0.18, 0.9 },
		ruleRect = RECT.rule,
		iconRect = RECT.icon,
		titleX = RECT.titleX,
		titleSize = TEXT_SIZE.title,
		closeRect = RECT.close,
		onClose = function()
			screen:Close()
		end,
	})
	self.window = window
	self.close = window.close
	local v = Kit.Core.Make("Frame", {
		Name = "Content",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		ZIndex = window.base.z + 1,
	}, window.base.visual)
	self.visual = v
	local z = window.base.z + 3
	self:_map(v, z)
	-- The world's name as a section heading over a hairline (as Journal and
	-- Settings head their sections), not a plaque.
	self.regionHeading = Kit.SectionHeader.new(v, {
		name = "Region",
		rect = RECT.region,
		text = PlayModel.WORLD_NAME,
		textSize = TEXT_SIZE.region,
		rule = "hairline",
		zIndex = z,
	})
	self:_details(v, z)
	self.partyHeading = Kit.SectionHeader.new(v, {
		name = "PartyHeading",
		rect = RECT.partyHeading,
		text = "Your Party",
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
	self.equipHeading = Kit.SectionHeader.new(v, {
		name = "EquipmentHeading",
		rect = RECT.equipHeading,
		text = "Your Equipment",
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
		-- The crystal arrow (D26); the white play glyph until it is uploaded.
		icon = "mark.playRune",
		-- The primary leather button, as the other menus' main actions.
		variant = "primary",
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
	-- The rune pillars stand in front of the button's ends (decoration only:
	-- not interactive, so presses on them reach nothing and the button keeps
	-- its own hit area). They draw nothing until their art is loaded.
	self.pillars = {
		Kit.Picture.new(v, { name = "PillarLeft", rect = RECT.pillarLeft, role = "deco.pillarLeft", zIndex = z + 3 }),
		Kit.Picture.new(
			v,
			{ name = "PillarRight", rect = RECT.pillarRight, role = "deco.pillarRight", zIndex = z + 3 }
		),
	}
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
	-- Gamepad: PLAY first; up reaches the loadout slots, then the close button.
	self.play.control.hit.NextSelectionUp = self.slots[1].control.hit
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
	local rune = RECT.rune
	Kit.Icon.new(v, {
		name = "Rune",
		rect = { r[1] + rune[1], r[2] + rune[2], rune[3], rune[4] },
		icon = "lk_emblem_rune",
		tint = "ink",
		zIndex = z + 1,
	})
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

-- One party row: crown (leader), headshot, name, level. Every part goes into
-- `maid`, so cleaning it takes the row apart.
local function partyRow(parent: Instance, row: PartyRow, order: number, maid)
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
	w, h = RECT.rowBox[1], RECT.rowBox[2]
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
	return outer
end

-- The party rows (leader first; PlayModel.Members). The old rows are taken
-- apart through their maids (Kit components included).
function PlayWindow:SetParty(rows: { PartyRow })
	local content = self.partyList:Content()
	for _, maid in self.rowMaids do
		maid:Clean()
	end
	table.clear(self.rowMaids)
	for order, row in rows do
		local maid = KitModel.Maid()
		partyRow(content, row, order, maid)
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

-- "solo" / "leader": PLAY can be pressed; "member": PLAY shows disabled (only
-- the leader starts the run; the status line says so).
function PlayWindow:SetMode(mode: string)
	self.mode = mode
	self:_syncPlay()
end

-- PLAY's enabled state; its pillars dim with it.
function PlayWindow:_syncPlay()
	local enabled = self.enabled and self.mode ~= "member"
	self.play:SetEnabled(enabled)
	for _, pillar in self.pillars do
		pillar:SetState(if enabled then "normal" else "disabled")
	end
end

-- The big button's busy state (a request in flight).
function PlayWindow:SetBusy(busy: boolean)
	self.play:SetBusy(busy)
end

function PlayWindow:SetEnabled(enabled: boolean)
	self.enabled = enabled
	self:_syncPlay()
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
	for _, pillar in self.pillars do
		pillar:Destroy()
	end
	self.close:Destroy()
	self.partyList:Destroy()
	self.window:Destroy()
	self.screen:Destroy()
end

return PlayWindow
