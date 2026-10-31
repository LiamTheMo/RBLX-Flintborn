-- The lobby's always-on HUD (docs/ui/LobbyScreen.md, art/reference/ui/lobby/01_hud.png,
-- ARCHITECTURE §4.1), built only from Kit components at the 1672 × 941 design
-- size: the player card (portrait, name, level, XP bar), Coins, Gems and
-- Settings, the 2 × 3 menu tiles, the Party panel, the level/XP bar and the
-- six-slot hotbar that shows the deploy loadout.
--
-- Display only: LobbyHudController feeds it through the setters and handles the
-- presses it reports through `actions`. Regions are pinned to the screen edges
-- inside `parent`, which Kit.Scale.Hud sizes to 1/scale of the screen.
--
--   local hud = LobbyHud.new(root, { onTile = open, onSettings = SettingsController.Toggle })
--   hud:SetProgress({ level = 12, xp = 450, xpToNext = 750 }, true)

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local LobbyHudModel = require(ReplicatedStorage.Shared.UI.LobbyHudModel)
local Kit = require(script.Parent.Parent.Kit)

local LobbyHud = {}
LobbyHud.__index = LobbyHud

-- Region origins and sizes in design px (measured on the mockup; the spec's
-- element tree). Top regions move down together when the Roblox top bar
-- reaches past the card's top (phones), keeping TOP_GAP below it.
LobbyHud.CARD = { 39, 60, 359, 81 }
LobbyHud.TOP_RIGHT = { right = 53, y = 70, w = 302, h = 46 }
LobbyHud.TILES = { x = 68, centreY = 448 / 941, w = 190, h = 272, pitchX = 102, pitchY = 94, tileW = 88, tileH = 84 }
LobbyHud.PARTY = { right = 53, y = 258, w = 294, h = 244 }
LobbyHud.BOTTOM = { bottom = 49, w = 572, h = 124 }
LobbyHud.TOP_GAP = 2

-- Hotbar slot lefts in the bottom region (mockup pitch 96.4).
LobbyHud.SLOT_X = { 0, 96, 193, 289, 386, 482 }

-- The headshot's window in the player card art.
LobbyHud.CARD_WINDOW = { 10, 9, 67, 63 }

-- Party panel parts in the panel's px: the pinned first row and the scrolling
-- list under it (its thin rail at x 1588..1596 of the mockup).
LobbyHud.PIN = { 28, 57, 242, 51 }
-- The title row's parts in the title row's px (the row starts at 26, 18).
LobbyHud.TITLE = { label = { 5, 4, 90, 30 }, count = { 92, 4, 70, 30 }, rule = { 3, 35, 235, 2 } }
LobbyHud.LIST = { 28, 106, 243, 113 }
-- Row heights (member row, empty-slot row; mockup pitch 51 / 35.6), the rule
-- width (the rules stop short of the rail) and the member row's layout.
LobbyHud.ROW_H = 51
LobbyHud.EMPTY_H = 36
LobbyHud.RULE_W = 223
LobbyHud.ROW = { w = 187, portrait = 41, nameX = 57, crown = 19, emptyDot = 22, emptyIndent = 5 }
-- The add-player button in the first member row.
LobbyHud.INVITE = { 196, 8, 45, 34 }

-- Spec text sizes (TextSize ≈ cap height ÷ 0.743, LobbyScreen.md).
LobbyHud.TEXT = { cardName = 19, cardLevel = 16, currency = 18, partyTitle = 20, memberName = 13, barText = 17 }

local function region(parent: Instance, name: string, props): Frame
	local frame = Instance.new("Frame")
	frame.Name = name
	frame.BackgroundTransparency = 1
	frame.BorderSizePixel = 0
	for key, value in props do
		(frame :: any)[key] = value
	end
	frame.Parent = parent
	return frame
end

-- actions: onProfile, onCurrency(id), onSettings, onTile(id), onParty(section?),
-- onAnswer(partyId, accept), onSlot(index). Every one is optional.
function LobbyHud.new(parent: Instance, actions)
	actions = actions or {}
	local self = setmetatable({
		actions = actions,
		shift = 0,
		tiles = {},
		slots = {},
		rows = {},
		parts = {},
	}, LobbyHud)
	local function fire(name: string, ...)
		local fn = actions[name]
		if fn then
			fn(...)
		end
	end
	self.fire = fire

	-- Top left: the player card (sheet 07 art, the headshot in its window). A
	-- press opens Progress.
	local c = LobbyHud.CARD
	local card = Kit.Core.Root(parent, "PlayerCard", "card.player", { rect = c, name = "PlayerCard" }, c[3], c[4])
	self.card = card
	local win = LobbyHud.CARD_WINDOW
	self.portrait = Kit.Portrait.new(card.visual, { name = "Portrait", rect = win, zIndex = 4 })
	-- The card's own frame surrounds the headshot: the portrait's frame stays
	-- hidden and the headshot fills its window on the photo backdrop.
	self.portrait.headshot.Position = UDim2.fromScale(0, 0)
	self.portrait.headshot.Size = UDim2.fromScale(1, 1)
	self.portrait.headshot.BackgroundTransparency = 0
	self.portrait.headshot.BackgroundColor3 = Kit.Tokens.Color("paperDisabled")
	for _, child in self.portrait.base.visual:GetChildren() do
		if child ~= self.portrait.headshot and child:IsA("GuiObject") then
			child.Visible = false
		end
	end
	self.plate = Kit.Picture.new(
		card.visual,
		{ name = "Card", rect = { 0, 0, c[3], c[4] }, role = "hud.playerCard", zIndex = 5 }
	)
	self.name = Kit.Text.new(card.visual, {
		name = "Name",
		rect = { 109, 17, 200, 24 },
		text = "",
		role = "hudName",
		textSize = LobbyHud.TEXT.cardName,
		zIndex = 7,
	})
	self.level = Kit.Text.new(card.visual, {
		name = "Level",
		rect = { 109, 44, 48, 20 },
		text = "",
		role = "hudSmall",
		textSize = LobbyHud.TEXT.cardLevel,
		-- Shrinks to fit when phones boost the text size.
		scaled = true,
		zIndex = 7,
	})
	self.cardBar = Kit.Bar.new(card.visual, { name = "XpBar", rect = { 159, 49, 161, 12 }, fill = "xp", zIndex = 7 })
	self.cardControl = Kit.Interact.attach(card, {
		hoverScale = false,
		onPress = function()
			fire("onProfile")
		end,
		render = function(state)
			self.plate:SetState(state)
		end,
	})
	self.parts.card = card.root

	-- Top right: Coins, Gems, Settings.
	local tr = LobbyHud.TOP_RIGHT
	self.topRight = region(parent, "TopRight", {
		Position = UDim2.new(1, -(tr.right + tr.w), 0, tr.y),
		Size = UDim2.fromOffset(tr.w, tr.h),
	})
	self.coins = Kit.CurrencyPill.new(self.topRight, {
		name = "Coins",
		rect = { 0, 0, 116, 46 },
		currency = "coins",
		textSize = LobbyHud.TEXT.currency,
		iconSize = 30,
		onPress = function()
			fire("onCurrency", "coins")
		end,
	})
	self.gems = Kit.CurrencyPill.new(self.topRight, {
		name = "Gems",
		rect = { 133, 0, 101, 46 },
		currency = "gems",
		textSize = LobbyHud.TEXT.currency,
		iconSize = 30,
		onPress = function()
			fire("onCurrency", "gems")
		end,
	})
	self.settings = Kit.IconButton.new(self.topRight, {
		name = "Settings",
		rect = { 250, 0, 52, 46 },
		variant = "settings",
		onPress = function()
			fire("onSettings")
		end,
	})
	self.parts.coins, self.parts.gems, self.parts.settings = self.coins.root, self.gems.root, self.settings.root

	-- Left: the menu tiles, a vertically centred 2 × 3 group.
	local t = LobbyHud.TILES
	self.tileRegion = region(parent, "Tiles", {
		AnchorPoint = Vector2.new(0, 0.5),
		Position = UDim2.new(0, t.x, t.centreY, 0),
		Size = UDim2.fromOffset(t.w, t.h),
	})
	for index, tile in LobbyHudModel.TILES do
		local column, row = (index - 1) % 2, (index - 1) // 2
		local button = Kit.IconButton.new(self.tileRegion, {
			name = tile.id,
			rect = { column * t.pitchX, row * t.pitchY, t.tileW, t.tileH },
			variant = "tile",
			icon = tile.icon,
			onPress = function()
				fire("onTile", tile.id)
			end,
		})
		self.tiles[tile.id] = button
		table.insert(self.tiles, button)
	end
	-- XP pop-ups appear to the right of the tiles (ProgressionController.MountPopups).
	self.popups = region(self.tileRegion, "XpPopups", {
		Position = UDim2.fromOffset(t.w + 24, 0),
		Size = UDim2.fromOffset(320, t.h),
	})

	-- Right: the Party panel (the 01 frame). The title row opens the Party
	-- window (D17). The first member's row (with the add-player button) stays
	-- put; the rest of the party, invites and free places scroll beside the
	-- thin rail under it, as the mockup draws the rail.
	local p = LobbyHud.PARTY
	self.partyRegion = region(parent, "Party", {
		Position = UDim2.new(1, -(p.right + p.w), 0, p.y),
		Size = UDim2.fromOffset(p.w, p.h),
	})
	self.panel = Kit.Picture.new(self.partyRegion, { name = "Panel", rect = { 0, 0, p.w, p.h }, role = "panel.party" })
	local body = self.partyRegion
	local title = Kit.Core.Root(
		body,
		"PartyTitle",
		"row.title",
		{ name = "Title", rect = { 26, 18, 242, 40 }, zIndex = 6 },
		242,
		40
	)
	self.titleRow = title
	-- "PARTY" and the count as two labels over a hairline (the mockup's title
	-- row; SectionHeader cuts "PARTY" short at this size).
	local th = LobbyHud.TITLE
	self.titleText = Kit.Text.new(title.visual, {
		name = "Label",
		rect = th.label,
		text = "Party",
		role = "sectionHeader",
		color = "ink",
		textSize = LobbyHud.TEXT.partyTitle,
		zIndex = title.z + 1,
	})
	self.countText = Kit.Text.new(title.visual, {
		name = "Count",
		rect = th.count,
		text = "1/8",
		role = "sectionHeader",
		color = "ink",
		textSize = LobbyHud.TEXT.partyTitle,
		zIndex = title.z + 1,
	})
	self.titleRule = Kit.Divider.new(title.visual, {
		name = "Rule",
		rect = th.rule,
		variant = "hairline",
		zIndex = title.z + 1,
	})
	local lit = Kit.Art.Plate(title.visual, "row.plate", 242, 40, { z = title.z })
	lit.holder.Visible = false
	self.titleControl = Kit.Interact.attach(title, {
		pressScale = false,
		onPress = function()
			fire("onParty", nil)
		end,
		render = function(state)
			local on = state ~= "normal" and state ~= "disabled"
			lit.holder.Visible = on
			if on then
				lit:Show(state)
			end
		end,
	})
	self.parts.partyTitle = title.root
	local pin = LobbyHud.PIN
	self.pinned = region(body, "Pinned", {
		Position = UDim2.fromOffset(pin[1], pin[2]),
		Size = UDim2.fromOffset(pin[3], pin[4]),
		ZIndex = 6,
	})
	local l = LobbyHud.LIST
	self.list = Kit.Scroll.new(body, {
		name = "List",
		rect = l,
		gap = 0,
		padBottom = 0,
		rail = "thin",
		railOverlay = true,
		zIndex = 6,
	})

	-- Bottom centre: level, XP bar and value, and the hotbar.
	local b = LobbyHud.BOTTOM
	self.bottom = region(parent, "Bottom", {
		AnchorPoint = Vector2.new(0.5, 1),
		Position = UDim2.new(0.5, 0, 1, -b.bottom),
		Size = UDim2.fromOffset(b.w, b.h),
	})
	self.barLevel = Kit.Text.new(self.bottom, {
		name = "Level",
		rect = { -40, -4, 114, 24 },
		text = "",
		role = "hudSmall",
		-- Over the world: a paper outline keeps it readable on any scene.
		outline = true,
		textSize = LobbyHud.TEXT.barText,
		align = "Right",
	})
	self.bar = Kit.Bar.new(self.bottom, { name = "XpBar", rect = { 81, 0, 356, 16 }, fill = "xp" })
	self.barText = Kit.Text.new(self.bottom, {
		name = "Xp",
		rect = { 448, -4, 160, 24 },
		text = "",
		role = "hudSmall",
		-- Over the world: a paper outline keeps it readable on any scene.
		outline = true,
		textSize = LobbyHud.TEXT.barText,
	})
	for index, x in LobbyHud.SLOT_X do
		local slot = Kit.Slot.new(self.bottom, {
			name = "Slot" .. index,
			rect = { x, 31, 89, 93 },
			variant = "hotbar",
			hotkey = tostring(index),
			onPress = function()
				fire("onSlot", index)
			end,
		})
		self.slots[index] = slot
	end

	-- Above the XP bar: the game-update notice, shown only while it applies
	-- (status toasts take the top centre).
	self.noticeRegion = region(self.bottom, "Notice", {
		Position = UDim2.fromOffset((b.w - 560) / 2, -58),
		Size = UDim2.fromOffset(560, 46),
		Visible = false,
	})
	self.notice = Kit.Panel.new(self.noticeRegion, {
		name = "Plaque",
		rect = { 0, 0, 560, 46 },
		variant = "plaque",
		pad = 18,
		text = "",
		textRole = "hudSmall",
	})

	self:_link()
	self:SetParty(LobbyHudModel.Party(nil, { userId = 0, name = "" }))
	self:SetHotbar(LobbyHudModel.Hotbar(nil))
	return self
end

-- Gamepad neighbours: the tile grid, the top-right row, the party column and
-- the hotbar, joined where they face each other.
function LobbyHud:_link()
	local function hit(component): GuiButton?
		local control = component and component.control
		return control and control.hit
	end
	for index, tile in ipairs(self.tiles) do
		local n = LobbyHudModel.TileNeighbours(index)
		local button = hit(tile) :: GuiButton
		button.NextSelectionUp = if n.up then hit(self.tiles[n.up]) else self.cardControl.hit
		button.NextSelectionDown = if n.down then hit(self.tiles[n.down]) else hit(self.slots[1])
		button.NextSelectionLeft = if n.left then hit(self.tiles[n.left]) else nil
		button.NextSelectionRight = if n.right then hit(self.tiles[n.right]) else self.titleControl.hit
	end
	self.cardControl.hit.NextSelectionDown = hit(self.tiles[1])
	self.cardControl.hit.NextSelectionRight = hit(self.coins)
	local top = { hit(self.coins), hit(self.gems), hit(self.settings) }
	for index, button in top do
		button.NextSelectionLeft = top[index - 1] or self.cardControl.hit
		button.NextSelectionRight = top[index + 1]
		button.NextSelectionDown = self.titleControl.hit
	end
	self.titleControl.hit.NextSelectionUp = top[3]
	self.titleControl.hit.NextSelectionLeft = hit(self.tiles[2])
	for index, slot in self.slots do
		local button = hit(slot) :: GuiButton
		button.NextSelectionLeft = hit(self.slots[index - 1])
		button.NextSelectionRight = hit(self.slots[index + 1])
		button.NextSelectionUp = hit(self.tiles[#self.tiles - 1])
	end
end

-- The control a gamepad selects first: the Inventory tile.
function LobbyHud:DefaultSelection(): GuiObject
	return self.tiles[1].control.hit
end

-- How far the Roblox top bar reaches down, in design px: the top regions move
-- below it when it reaches past the mockup's top margin.
function LobbyHud:SetTopInset(designPx: number)
	local shift = math.max(0, math.ceil(designPx + LobbyHud.TOP_GAP - LobbyHud.CARD[2]))
	self.shift = shift
	local c = LobbyHud.CARD
	self.card.root.Position = UDim2.fromOffset(c[1], c[2] + shift)
	local tr, p = LobbyHud.TOP_RIGHT, LobbyHud.PARTY
	self.topRight.Position = UDim2.new(1, -(tr.right + tr.w), 0, tr.y + shift)
	self.partyRegion.Position = UDim2.new(1, -(p.right + p.w), 0, p.y + shift)
end

-- The local player's name and headshot.
function LobbyHud:SetProfile(name: string, userId: number?)
	self.name:SetText(name)
	self.portrait:SetUser(userId)
end

-- view: the progression snapshot {level, xp, xpToNext} (nil while loading).
function LobbyHud:SetProgress(view, instant: boolean?)
	local progress = LobbyHudModel.Progress(view)
	self.level:SetText(progress.level)
	self.barLevel:SetText(progress.level)
	self.barText:SetText(progress.text)
	self.cardBar:Set(progress.fraction, instant)
	self.bar:Set(progress.fraction, instant)
end

function LobbyHud:SetCurrency(coins: number?, gems: number?, instant: boolean?)
	self.coins:SetValue(math.max(0, math.floor(coins or 0)), instant)
	self.gems:SetValue(math.max(0, math.floor(gems or 0)), instant)
end

function LobbyHud:_clearRows()
	for _, row in self.rows do
		row:Destroy()
	end
	table.clear(self.rows)
	self.parts.members, self.parts.empty, self.parts.invite, self.parts.answers = {}, {}, nil, {}
	self.invite = nil
	for _, holder in { self.pinned, self.list:Content() } do
		for _, child in holder:GetChildren() do
			if child:IsA("GuiObject") and child:GetAttribute("LobbyRow") then
				child:Destroy()
			end
		end
	end
end

-- A transparent row holder in the list, left-aligned (rows and their side
-- buttons share it).
function LobbyHud:_holder(order: number, height: number): Frame
	local holder = region(self.list:Content(), "Row" .. order, {
		LayoutOrder = order,
		Size = UDim2.fromOffset(LobbyHud.LIST[3], height),
	})
	holder:SetAttribute("LobbyRow", true)
	return holder
end

function LobbyHud:_member(holder: Frame, member, showReady: boolean)
	local fire = self.fire
	local r = LobbyHud.ROW
	-- PlayerRow names its root after the player (`name` is both).
	local row = Kit.PlayerRow.new(holder, {
		rect = { 0, 0, r.w, LobbyHud.ROW_H },
		userId = member.userId,
		name = member.name,
		leader = member.leader,
		compact = true,
		status = if showReady then (if member.ready then "ready" else "notReady") else nil,
		portraitSize = r.portrait,
		nameX = r.nameX,
		nameSize = LobbyHud.TEXT.memberName,
		crownSize = r.crown,
		rule = false,
		zIndex = 6,
		onPress = function()
			fire("onParty", nil)
		end,
	})
	row.root:SetAttribute("LobbyUserId", member.userId)
	row.root:SetAttribute("LobbyReady", member.ready)
	-- The rule runs on under the add-player button.
	table.insert(
		self.rows,
		Kit.Divider.new(holder, {
			name = "Rule",
			rect = { 0, LobbyHud.ROW_H - 2, LobbyHud.RULE_W, 2 },
			variant = "hairline",
			zIndex = 6,
		})
	)
	table.insert(self.rows, row)
	table.insert(self.parts.members, row.root)
	return row
end

-- party: LobbyHudModel.Party(...) — members, incoming invites, free rows and
-- whether you may invite.
function LobbyHud:SetParty(party)
	self:_clearRows()
	self.countText:SetText(party.count)
	local fire = self.fire
	local width = LobbyHud.RULE_W
	-- The first member stays at the top with the add-player button.
	local pinned = region(self.pinned, "Row0", { Size = UDim2.fromScale(1, 1) })
	pinned:SetAttribute("LobbyRow", true)
	local first = self:_member(pinned, party.members[1], party.showReady)
	local invite = Kit.IconButton.new(pinned, {
		name = "Invite",
		rect = LobbyHud.INVITE,
		variant = "invite",
		zIndex = 7,
		onPress = function()
			fire("onParty", "invite")
		end,
	})
	invite:SetEnabled(party.canInvite)
	self.invite = invite
	self.parts.invite = invite.root
	table.insert(self.rows, invite)
	local order, height = 0, 0
	for index = 2, #party.members do
		order += 1
		self:_member(self:_holder(order, LobbyHud.ROW_H), party.members[index], party.showReady)
		height += LobbyHud.ROW_H
	end
	for _, from in party.invites do
		order += 1
		local holder = self:_holder(order, LobbyHud.ROW_H)
		local row = Kit.ListRow.new(holder, {
			name = "InviteFrom",
			rect = { 0, 0, width - 80, LobbyHud.ROW_H },
			variant = "line",
			icon = "party",
			title = from.from,
			subtitle = "Party invite",
			zIndex = 6,
		})
		local accept = Kit.IconButton.new(holder, {
			name = "Accept",
			rect = { width - 76, 9, 34, 34 },
			variant = "small",
			icon = "check",
			zIndex = 6,
			onPress = function()
				fire("onAnswer", from.partyId, true)
			end,
		})
		local decline = Kit.IconButton.new(holder, {
			name = "Decline",
			rect = { width - 36, 9, 34, 34 },
			variant = "small",
			icon = "cross",
			zIndex = 6,
			onPress = function()
				fire("onAnswer", from.partyId, false)
			end,
		})
		table.insert(self.rows, row)
		table.insert(self.rows, accept)
		table.insert(self.rows, decline)
		table.insert(self.parts.answers, accept.root)
		table.insert(self.parts.answers, decline.root)
		height += LobbyHud.ROW_H
	end
	local r = LobbyHud.ROW
	for _ = 1, party.free do
		order += 1
		local holder = self:_holder(order, LobbyHud.EMPTY_H)
		local row = Kit.PlayerRow.new(holder, {
			name = "Empty",
			rect = { 0, 0, width, LobbyHud.EMPTY_H },
			empty = true,
			emptyText = "",
			compact = true,
			portraitSize = r.emptyDot,
			emptyIndent = r.emptyIndent,
			zIndex = 6,
			onPress = function()
				fire("onParty", if party.canInvite then "invite" else nil)
			end,
		})
		table.insert(self.rows, row)
		table.insert(self.parts.empty, row.root)
		height += LobbyHud.EMPTY_H
	end
	self.list:SetContentHeight(height + 2)
	if self.titleControl then
		self.titleControl.hit.NextSelectionDown = first.control and first.control.hit or nil
	end
end

-- slots: LobbyHudModel.Hotbar(...) — six entries, an item or false.
function LobbyHud:SetHotbar(slots)
	for index, slot in self.slots do
		local item = slots[index]
		slot:SetItem(if item then item else nil)
	end
end

-- The game-update notice plaque (nil hides it).
function LobbyHud:SetNotice(text: string?)
	self.noticeRegion.Visible = text ~= nil and text ~= ""
	if self.notice.label then
		self.notice.label:SetText(text or "")
	end
end

function LobbyHud:Destroy()
	self:_clearRows()
	for _, part in
		{
			self.portrait,
			self.plate,
			self.cardBar,
			self.coins,
			self.gems,
			self.settings,
			self.titleText,
			self.countText,
			self.titleRule,
		}
	do
		part:Destroy()
	end
	for _, tile in ipairs(self.tiles) do
		tile:Destroy()
	end
	for _, slot in self.slots do
		slot:Destroy()
	end
	self.bar:Destroy()
	self.list:Destroy()
	self.panel:Destroy()
	self.pinned:Destroy()
	self.notice:Destroy()
	self.card.maid:Clean()
	self.titleRow.maid:Clean()
	for _, frame in { self.topRight, self.tileRegion, self.partyRegion, self.bottom } do
		frame:Destroy()
	end
end

return LobbyHud
