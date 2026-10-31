-- The lobby's always-on HUD (docs/ui/LobbyScreen.md, art/reference/ui/lobby/01_hud.png,
-- ARCHITECTURE §4.1), built only from Kit components at the 1672 × 941 design
-- size: Coins, Gems and Settings, the 2 × 3 menu tiles, the Party panel (each
-- member with their level and XP bar), the level/XP bar and the six-slot
-- hotbar that shows the deploy loadout. (The mockup's top-left player card is
-- left out.)
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
-- reaches past the mockup's top margin TOP_Y (phones), keeping TOP_GAP below
-- it.
LobbyHud.TOP_Y = 60
LobbyHud.TOP_RIGHT = { right = 53, y = 70, w = 302, h = 46 }
LobbyHud.TILES = { x = 68, centreY = 448 / 941, w = 190, h = 272, pitchX = 102, pitchY = 94, tileW = 88, tileH = 84 }
LobbyHud.PARTY = { right = 53, y = 258, w = 294, h = 244 }
LobbyHud.BOTTOM = { bottom = 49, w = 572, h = 124 }
LobbyHud.TOP_GAP = 2

-- Hotbar slot lefts in the bottom region (mockup pitch 96.4).
LobbyHud.SLOT_X = { 0, 96, 193, 289, 386, 482 }

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
LobbyHud.ROW =
	{ w = 187, portrait = 41, nameX = 57, crown = 19, emptyDot = 22, emptyIndent = 5, levelSize = 11, barH = 7 }
-- The add-player button in the first member row.
LobbyHud.INVITE = { 196, 8, 45, 34 }

-- Spec text sizes (TextSize ≈ cap height ÷ 0.743, LobbyScreen.md).
LobbyHud.TEXT = { currency = 18, partyTitle = 20, memberName = 13, barText = 17 }

-- Phones and touch tablets (Kit.Scale.IsSmallTouch): the HUD draws at its
-- 0.5 floor there, so party names grow to stay at 9 screen px or more, rows
-- take the panel's width (the add-player button moves up beside the count), the pills widen for long values, the notice
-- wraps onto two lines and an invite gets one Respond button (opening the
-- Party window's invitations) instead of two small ✓ / ✕ buttons whose touch
-- pads would overlap.
LobbyHud.PHONE = {
	memberName = 15,
	memberLevel = 13,
	pills = { coins = { 0, 0, 150, 46 }, gems = { 162, 0, 124, 46 }, settings = { 298, 0, 52, 46 }, w = 350 },
	noticeH = 72,
	respond = { 98, 6, 125, 40 },
	-- The add-player button moves into the title row (panel px), so the first
	-- member's row has the panel's width for the larger name.
	invite = { 222, 21, 45, 34 },
}
LobbyHud.PILLS = { coins = { 0, 0, 116, 46 }, gems = { 133, 0, 101, 46 }, settings = { 250, 0, 52, 46 }, w = 302 }

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

-- actions: onCurrency(id), onSettings, onTile(id), onParty(section?),
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
		phone = Kit.Scale.IsSmallTouch(),
		coinValue = 0,
		gemValue = 0,
	}, LobbyHud)
	local function fire(name: string, ...)
		local fn = actions[name]
		if fn then
			fn(...)
		end
	end
	self.fire = fire

	-- Top right: Coins, Gems, Settings.
	local tr = LobbyHud.TOP_RIGHT
	self.topRight = region(parent, "TopRight", {
		Position = UDim2.new(1, -(tr.right + tr.w), 0, tr.y),
		Size = UDim2.fromOffset(tr.w, tr.h),
	})
	self:_buildTopRight()

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
	-- Gamepad: "RB Menu" over the tiles (LobbyHudController binds RB to step
	-- into them); shown only while a gamepad is the input.
	self.menuHint = region(self.tileRegion, "MenuHint", {
		Position = UDim2.fromOffset(0, -46),
		Size = UDim2.fromOffset(t.w, 36),
		Visible = false,
	})
	Kit.KeyCap.new(self.menuHint, { name = "Key", rect = { 0, 0, 0, 34 }, text = "RB", variant = "cap" })
	Kit.Text.new(self.menuHint, {
		name = "Label",
		rect = { 58, 0, t.w - 58, 34 },
		text = "Menu",
		role = "hudSmall",
		outline = true,
	})
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
	self.noticeText = ""
	self.noticeRegion = region(self.bottom, "Notice", {
		Position = UDim2.fromOffset((b.w - 560) / 2, -58),
		Size = UDim2.fromOffset(560, 46),
		Visible = false,
	})
	self:_buildNotice()

	self:_link()
	self:SetParty(LobbyHudModel.Party(nil, { userId = 0, name = "" }))
	self:SetHotbar(LobbyHudModel.Hotbar(nil))
	-- Hotkey badges (1–6) are keyboard keys: shown only while one is in use.
	self.stopInput = Kit.Input.Watch(function()
		self:_hotkeys()
	end)
	self:_hotkeys()
	-- Phone and desktop sizes follow the screen and the input devices.
	self.stopForm = Kit.Scale.OnFormFactorChanged(function()
		self:_formChanged()
	end)
	return self
end

-- Coins, Gems and Settings (rebuilt when the form factor changes).
function LobbyHud:_buildTopRight()
	for _, part in { self.coins, self.gems, self.settings } do
		part:Destroy()
	end
	local layout = if self.phone then LobbyHud.PHONE.pills else LobbyHud.PILLS
	local tr = LobbyHud.TOP_RIGHT
	local fire = self.fire
	self.topRight.Size = UDim2.fromOffset(layout.w, tr.h)
	self.topRight.Position = UDim2.new(1, -(tr.right + layout.w), 0, tr.y + self.shift)
	self.coins = Kit.CurrencyPill.new(self.topRight, {
		name = "Coins",
		rect = layout.coins,
		currency = "coins",
		value = self.coinValue,
		textSize = LobbyHud.TEXT.currency,
		iconSize = 30,
		onPress = function()
			fire("onCurrency", "coins")
		end,
	})
	self.gems = Kit.CurrencyPill.new(self.topRight, {
		name = "Gems",
		rect = layout.gems,
		currency = "gems",
		value = self.gemValue,
		textSize = LobbyHud.TEXT.currency,
		iconSize = 30,
		onPress = function()
			fire("onCurrency", "gems")
		end,
	})
	self.settings = Kit.IconButton.new(self.topRight, {
		name = "Settings",
		rect = layout.settings,
		variant = "settings",
		onPress = function()
			fire("onSettings")
		end,
	})
	self.coins:SetValue(self.coinValue, true)
	self.gems:SetValue(self.gemValue, true)
	self.parts.coins, self.parts.gems, self.parts.settings = self.coins.root, self.gems.root, self.settings.root
end

-- The game-update plaque: one line on desktop, two on phones.
function LobbyHud:_buildNotice()
	if self.notice then
		self.notice:Destroy()
	end
	local b = LobbyHud.BOTTOM
	local h = if self.phone then LobbyHud.PHONE.noticeH else 46
	self.noticeRegion.Position = UDim2.fromOffset((b.w - 560) / 2, -12 - h)
	self.noticeRegion.Size = UDim2.fromOffset(560, h)
	self.notice = Kit.Panel.new(self.noticeRegion, {
		name = "Plaque",
		rect = { 0, 0, 560, h },
		variant = "plaque",
		pad = 18,
		text = self.noticeText,
		textRole = "hudSmall",
	})
	if self.notice.label then
		-- Shrinks to fit, wrapping onto a second line before it gets small.
		self.notice.label.root.TextWrapped = self.phone
	end
end

-- The hotbar's 1–6 badges while a keyboard or mouse is the input.
function LobbyHud:_hotkeys()
	local kind = Kit.Input.Type()
	local keys = kind == "mouse" or kind == "keyboard"
	for index, slot in self.slots do
		slot:SetHotkey(if keys then tostring(index) else nil)
	end
end

function LobbyHud:_formChanged()
	local phone = Kit.Scale.IsSmallTouch()
	if phone == self.phone then
		return
	end
	self.phone = phone
	self:_buildTopRight()
	self:_buildNotice()
	self:_link()
	if self.party then
		self:SetParty(self.party)
	end
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
		button.NextSelectionUp = if n.up then hit(self.tiles[n.up]) else hit(self.coins)
		button.NextSelectionDown = if n.down then hit(self.tiles[n.down]) else hit(self.slots[1])
		button.NextSelectionLeft = if n.left then hit(self.tiles[n.left]) else nil
		button.NextSelectionRight = if n.right then hit(self.tiles[n.right]) else self.titleControl.hit
	end
	local top = { hit(self.coins), hit(self.gems), hit(self.settings) }
	for index, button in top do
		button.NextSelectionLeft = top[index - 1] or hit(self.tiles[2])
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

-- Shows the gamepad "RB Menu" hint over the tiles.
function LobbyHud:SetMenuHint(visible: boolean)
	self.menuHint.Visible = visible
end

-- How far the Roblox top bar reaches down, in design px: the top regions move
-- below it when it reaches past the mockup's top margin.
function LobbyHud:SetTopInset(designPx: number)
	local tr, p = LobbyHud.TOP_RIGHT, LobbyHud.PARTY
	local shift = math.max(0, math.ceil(designPx + LobbyHud.TOP_GAP - LobbyHud.TOP_Y))
	self.shift = shift
	local w = (if self.phone then LobbyHud.PHONE.pills else LobbyHud.PILLS).w
	self.topRight.Position = UDim2.new(1, -(tr.right + w), 0, tr.y + shift)
	self.partyRegion.Position = UDim2.new(1, -(p.right + p.w), 0, p.y + shift)
end

-- view: the progression snapshot {level, xp, xpToNext} (nil while loading).
function LobbyHud:SetProgress(view, instant: boolean?)
	local progress = LobbyHudModel.Progress(view)
	self.barLevel:SetText(progress.level)
	self.barText:SetText(progress.text)
	self.bar:Set(progress.fraction, instant)
end

function LobbyHud:SetCurrency(coins: number?, gems: number?, instant: boolean?)
	self.coinValue = math.max(0, math.floor(coins or 0))
	self.gemValue = math.max(0, math.floor(gems or 0))
	self.coins:SetValue(self.coinValue, instant)
	self.gems:SetValue(self.gemValue, instant)
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
	-- On phones a row takes the panel's width (the add-player button sits in
	-- the title row there).
	local w = if self.phone then LobbyHud.RULE_W else r.w
	-- PlayerRow names its root after the player (`name` is both).
	local row = Kit.PlayerRow.new(holder, {
		rect = { 0, 0, w, LobbyHud.ROW_H },
		userId = member.userId,
		name = member.name,
		leader = member.leader,
		compact = true,
		status = if showReady then (if member.ready then "ready" else "notReady") else nil,
		portraitSize = r.portrait,
		nameX = r.nameX,
		nameSize = if self.phone then LobbyHud.PHONE.memberName else LobbyHud.TEXT.memberName,
		-- "LV. n" and the member's XP bar under the name (their replicated
		-- Level / LevelProgress attributes).
		levelBar = true,
		levelSize = if self.phone then LobbyHud.PHONE.memberLevel else r.levelSize,
		barHeight = r.barH,
		-- Desktop shrinks a long name to fit (down to the text floor); touch
		-- keeps the size, ends in "…" and shows the whole name in a tooltip.
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
	self.party = party
	self:_clearRows()
	self.countText:SetText(party.count)
	local fire = self.fire
	local width = LobbyHud.RULE_W
	-- The first member stays at the top with the add-player button.
	local pinned = region(self.pinned, "Row0", { Size = UDim2.fromScale(1, 1) })
	pinned:SetAttribute("LobbyRow", true)
	local first = self:_member(pinned, party.members[1], party.showReady)
	-- On phones the list shows few rows: with three or more members a waiting
	-- invite is below the fold, so the add-player button carries a dot.
	local hiddenInvite = self.phone and #party.invites > 0 and #party.members >= 3
	local invite = Kit.IconButton.new(if self.phone then self.partyRegion else pinned, {
		name = "Invite",
		rect = if self.phone then LobbyHud.PHONE.invite else LobbyHud.INVITE,
		variant = "invite",
		badge = if hiddenInvite then { variant = "dotRed" } else nil,
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
		local respondW = LobbyHud.PHONE.respond[3]
		local row = Kit.ListRow.new(holder, {
			name = "InviteFrom",
			rect = { 0, 0, width - (if self.phone then respondW + 8 else 80), LobbyHud.ROW_H },
			variant = "line",
			icon = "party",
			title = from.from,
			subtitle = "Party invite",
			zIndex = 6,
		})
		table.insert(self.rows, row)
		if self.phone then
			-- One touch-sized button: the Party window's invitations answer it.
			local respond = Kit.Button.new(holder, {
				name = "Respond",
				rect = LobbyHud.PHONE.respond,
				label = "Respond",
				variant = "secondary",
				sizeClass = "s",
				zIndex = 6,
				onPress = function()
					fire("onParty", "invite")
				end,
			})
			respond:SetBusy(from.busy == true)
			table.insert(self.rows, respond)
			table.insert(self.parts.answers, respond.root)
		else
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
			-- An answer on its way: neither can be pressed again.
			accept:SetEnabled(from.busy ~= true)
			decline:SetEnabled(from.busy ~= true)
			table.insert(self.rows, accept)
			table.insert(self.rows, decline)
			table.insert(self.parts.answers, accept.root)
			table.insert(self.parts.answers, decline.root)
		end
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
	self.noticeText = text or ""
	self.noticeRegion.Visible = text ~= nil and text ~= ""
	if self.notice.label then
		self.notice.label:SetText(text or "")
	end
end

function LobbyHud:Destroy()
	self.stopInput()
	self.stopForm()
	self:_clearRows()
	for _, part in
		{
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
	self.titleRow.maid:Clean()
	for _, frame in { self.topRight, self.tileRegion, self.partyRegion, self.bottom } do
		frame:Destroy()
	end
end

return LobbyHud
