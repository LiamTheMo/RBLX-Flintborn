-- The lobby's always-on HUD (docs/ui/LobbyScreen.md, art/reference/ui/lobby/01_hud.png,
-- ARCHITECTURE §4.1), built only from Kit components at the 1672 × 941 design
-- size: Coins and Gems, the 2 × 3 menu tiles, the Party panel (each member
-- with their level and XP bar), the level/XP bar, the six-slot hotbar that
-- shows the deploy loadout and the Settings button at the bottom left. (The
-- mockup's top-left player card is left out; the level/XP bar opens Progress
-- instead. The mockup's Settings button beside the pills moved to the bottom
-- left: owner decisions, ARCHITECTURE D27 and D28.)
--
-- The HUD grid (D30): the pieces the lobby shares with the run's HUD (the
-- menu tiles, the level/XP bar and hotbar, the ⚙, the right-hand column's
-- edge, top and width) come from HudLayout.json and Hud/Layout, the same
-- numbers and the same placement (Layout.PlaceColumns, HudModel.GearCorner),
-- so the two HUDs put them in the same place on every screen.
--
-- Display only: LobbyHudController feeds it through the setters and handles the
-- presses it reports through `actions`. Regions are pinned to the screen edges
-- inside `parent`, which Kit.Scale.Hud sizes to 1/scale of the whole screen
-- (Kit.Scale.FullScreen); SetTopInset and SetScreen place them on the grid.
--
--   local hud = LobbyHud.new(root, { onTile = open, onSettings = SettingsController.Toggle })
--   hud:SetProgress({ level = 12, xp = 450, xpToNext = 750 }, true)

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local LobbyHudModel = require(ReplicatedStorage.Shared.UI.LobbyHudModel)
local Kit = require(script.Parent.Parent.Kit)
local Layout = require(script.Parent.Parent.Layout)

local LobbyHud = {}
LobbyHud.__index = LobbyHud

-- The right-hand column's pieces (D30): Coins and Gems, then the Party
-- panel the grid's gap under them, both the grid's column wide (HudLayout
-- "grid"), as the run's vitals and objective are. Heights in design px.
LobbyHud.PILLS = { h = 46, gemsW = 138 }
LobbyHud.PARTY_H = 244

-- Party panel parts in the panel's px for a panel `w` wide (the mockup's is
-- 294; the grid's column is wider, and the rows widen with it): the pinned
-- first row and the scrolling list under it (its thin rail at the right).
function LobbyHud.PartyParts(w: number)
	return {
		pin = { 28, 57, w - 52, 51 },
		-- The title row (at 26, 18) and its parts in its own px.
		title = { 26, 18, w - 52, 40 },
		label = { 5, 4, 90, 30 },
		count = { 92, 4, 70, 30 },
		rule = { 3, 35, w - 59, 2 },
		list = { 28, 106, w - 51, 113 },
		-- The member row, the rules (they stop short of the rail) and the
		-- add-player button in the first member's row (phones: in the title
		-- row, panel px).
		rowW = w - 107,
		ruleW = w - 71,
		invite = { w - 98, 8, 45, 34 },
		phoneInvite = { w - 72, 21, 45, 34 },
	}
end
LobbyHud.LIST_BLEED = 6
-- Row heights (member row, empty-slot row; mockup pitch 51 / 35.6) and the
-- member row's layout.
LobbyHud.ROW_H = 51
LobbyHud.EMPTY_H = 36
LobbyHud.ROW = { portrait = 41, nameX = 57, crown = 19, emptyDot = 22, emptyIndent = 5, levelSize = 11, barH = 7 }

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
	-- 14: at a touch tablet's HUD scale (1024 × 768) "LV. n" still draws at
	-- 9 screen px or more.
	memberLevel = 14,
	noticeH = 72,
	respond = { 98, 6, 125, 40 },
}

-- The XP pop-up lane: over the bar (HudLayout bottom.popups), its foot `gap`
-- above the bar (or above the notice plaque while it shows).
LobbyHud.POPUP_GAP = 4

-- A hit button for a short control whose touch pad may only grow upwards (the
-- party title over the first member row, the XP bar over the hotbar): on
-- touch screens it reaches up until the control is touchMin screen px tall,
-- and never covers what lies under it.
local function upwardHit(base): TextButton
	local hit = Kit.Core.Make("TextButton", {
		Name = "Hit",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		Size = UDim2.fromScale(1, 1),
		Text = "",
		ZIndex = base.z + 8,
	}, base.root)
	local function fit()
		local shown = base.root.AbsoluteSize
		if not UserInputService.TouchEnabled or shown.X <= 0 or base.w <= 0 then
			return
		end
		local k = shown.X / base.w
		local need = math.max(0, Kit.Tokens.Space("touchMin", 44) / k - base.h)
		hit.Position = UDim2.fromOffset(0, -need)
		hit.Size = UDim2.new(1, 0, 1, need)
	end
	base.maid:Give(base.root:GetPropertyChangedSignal("AbsoluteSize"):Connect(fit))
	fit()
	return hit
end

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
-- onAnswer(partyId, accept), onSlot(index), onProgress(). Every one is optional.
function LobbyHud.new(parent: Instance, actions)
	actions = actions or {}
	local layout = assert(Layout.Get(), "the HUD layout (HudLayout.json) is missing")
	local grid = layout.grid
	local self = setmetatable({
		actions = actions,
		layout = layout,
		grid = grid,
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

	-- Top right: Coins and Gems, the right-hand column's first piece.
	self.topRight = region(parent, "TopRight", {
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.new(1, -grid.margin, 0, grid.margin),
		Size = UDim2.fromOffset(grid.column, LobbyHud.PILLS.h),
	})
	self:_buildTopRight()

	-- Left: the menu tiles, the run's grid (HudLayout "tiles": 2 × 3 centred
	-- on the screen's height; phones 3 × 2 under the top bar).
	self.tileRegion = region(parent, "Tiles", {})
	self:_buildTiles()

	-- Right: the Party panel (the 01 frame), right under the pills. The title
	-- row opens the Party window (D17). The first member's row (with the
	-- add-player button) stays put; the rest of the party, invites and free
	-- places scroll beside the thin rail under it, as the mockup draws the rail.
	local pw, ph = grid.column, LobbyHud.PARTY_H
	local parts = LobbyHud.PartyParts(pw)
	self.partyParts = parts
	self.partyRegion = region(parent, "Party", {
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.new(1, -grid.margin, 0, grid.margin + LobbyHud.PILLS.h + grid.gap),
		Size = UDim2.fromOffset(pw, ph),
	})
	self.panel = Kit.Picture.new(self.partyRegion, { name = "Panel", rect = { 0, 0, pw, ph }, role = "panel.party" })
	local body = self.partyRegion
	local title = Kit.Core.Root(
		body,
		"PartyTitle",
		"row.title",
		{ name = "Title", rect = parts.title, zIndex = 6 },
		parts.title[3],
		parts.title[4]
	)
	self.titleRow = title
	-- "PARTY" and the count as two labels over a hairline (the mockup's title
	-- row; SectionHeader cuts "PARTY" short at this size).
	self.titleText = Kit.Text.new(title.visual, {
		name = "Label",
		rect = parts.label,
		text = "Party",
		role = "sectionHeader",
		color = "ink",
		textSize = LobbyHud.TEXT.partyTitle,
		zIndex = title.z + 1,
	})
	self.countText = Kit.Text.new(title.visual, {
		name = "Count",
		rect = parts.count,
		text = "1/8",
		role = "sectionHeader",
		color = "ink",
		textSize = LobbyHud.TEXT.partyTitle,
		zIndex = title.z + 1,
	})
	self.titleRule = Kit.Divider.new(title.visual, {
		name = "Rule",
		rect = parts.rule,
		variant = "hairline",
		zIndex = title.z + 1,
	})
	local lit = Kit.Art.Plate(title.visual, "row.plate", parts.title[3], parts.title[4], { z = title.z })
	lit.holder.Visible = false
	self.titleControl = Kit.Interact.attach(title, {
		-- Its touch pad grows up, off the first member's row.
		hit = upwardHit(title),
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
	local pin = parts.pin
	self.pinned = region(body, "Pinned", {
		Position = UDim2.fromOffset(pin[1], pin[2]),
		Size = UDim2.fromOffset(pin[3], pin[4]),
		ZIndex = 6,
	})
	-- The list reaches LIST_BLEED px further left than its rows, which keep
	-- their place: a row's hover and pressed plate is drawn a few px past the
	-- row, and the list clips whatever crosses its edge.
	local l = parts.list
	local bleed = LobbyHud.LIST_BLEED
	self.list = Kit.Scroll.new(body, {
		name = "List",
		rect = { l[1] - bleed, l[2], l[3] + bleed, l[4] },
		gap = 0,
		padBottom = 0,
		padLeft = bleed,
		rail = "thin",
		railOverlay = true,
		zIndex = 6,
	})

	-- Bottom centre: level, XP bar and value, and the hotbar, as the run's
	-- (HudLayout "bottom": the same place, parts and sizes).
	local b = layout.bottom
	self.bottom = region(parent, "Bottom", {})
	Layout.Place(self.bottom, b)
	-- The level, bar and XP text open Progress (touch players have no other
	-- way there in the lobby; gamepad reaches it from the hotbar). They sit in
	-- the press area's visual, so the kit's press feedback moves them together:
	-- a touch larger on hover and gamepad focus (with the gold focus ring),
	-- smaller while held, and the bar's art at the hover / pressed tints.
	local press = LobbyHud.XpPress(b)
	local px, py = press[1], press[2]
	local xp = Kit.Core.Root(self.bottom, "XpPress", "bar.track", {
		name = "XpPress",
		rect = press,
		zIndex = 4,
	}, press[3], press[4])
	self.xpPress = xp
	local function within(rect)
		return { rect[1] - px, rect[2] - py, rect[3], rect[4] }
	end
	self.barLevel = Kit.Text.new(xp.visual, {
		name = "Level",
		rect = within(b.level),
		text = "",
		role = "hudSmall",
		-- Over the world: a paper outline keeps it readable on any scene.
		outline = true,
		textSize = b.textSize,
		align = "Right",
	})
	self.bar = Kit.Bar.new(xp.visual, { name = "XpBar", rect = within(b.xp), fill = "xp" })
	self.barText = Kit.Text.new(xp.visual, {
		name = "Xp",
		rect = within(b.xpText),
		text = "",
		role = "hudSmall",
		-- Over the world: a paper outline keeps it readable on any scene.
		outline = true,
		textSize = b.textSize,
	})
	-- The bar's own colours, recorded the first time a state tints them.
	local barColours: { [ImageLabel]: Color3 } = setmetatable({}, { __mode = "k" }) :: any
	local function tintBar(state: string)
		local key = KitModel.STATE_TINT[state]
		local tint = if key then Kit.Tokens.Tint(key) else Color3.new(1, 1, 1)
		for _, image in self.bar.root:GetDescendants() do
			if image:IsA("ImageLabel") then
				local own = barColours[image]
				if own == nil then
					own = image.ImageColor3
					barColours[image] = own
				end
				image.ImageColor3 = Kit.Tokens.Multiply(own, tint)
			end
		end
	end
	self.xpControl = Kit.Interact.attach(xp, {
		-- Its touch pad grows up, off the hotbar.
		hit = upwardHit(xp),
		hoverScale = true,
		render = tintBar,
		onPress = function()
			fire("onProgress")
		end,
	})
	self.parts.xp = xp.root
	local hotbar = b.hotbar
	for index, x in hotbar.x do
		local slot = Kit.Slot.new(self.bottom, {
			name = "Slot" .. index,
			rect = { x, hotbar.y, hotbar.slot[1], hotbar.slot[2] },
			variant = "hotbar",
			hotkey = tostring(index),
			onPress = function()
				fire("onSlot", index)
			end,
		})
		self.slots[index] = slot
	end

	-- Bottom left: Settings, in the grid's corner as the run's (HudLayout
	-- "gear"; SetScreen places it, HudModel.GearCorner).
	local g = layout.gear.size
	self.settingsRegion = region(parent, "Settings", {
		AnchorPoint = Vector2.new(0, 1),
		Position = UDim2.new(0, grid.margin, 1, -grid.margin),
		Size = UDim2.fromOffset(g[1], g[2]),
	})
	self.settings = Kit.IconButton.new(self.settingsRegion, {
		name = "Settings",
		rect = { 0, 0, g[1], g[2] },
		variant = "settings",
		onPress = function()
			fire("onSettings")
		end,
	})
	self.parts.settings = self.settings.root

	-- XP pop-ups stack just above the XP bar, where the run's HUD shows them
	-- (HudLayout bottom.popups; ProgressionController.MountPopups), and above
	-- the game-update notice while it shows (_placePopups).
	local lane = b.popups
	self.popups = region(self.bottom, "XpPopups", {
		Position = UDim2.fromOffset(lane[1], -LobbyHud.POPUP_GAP - lane[4]),
		Size = UDim2.fromOffset(lane[3], lane[4]),
	})

	-- Above the XP bar: the game-update notice, shown only while it applies
	-- (status toasts take the top centre).
	self.noticeText = ""
	self.noticeRegion = region(self.bottom, "Notice", {
		Position = UDim2.fromOffset((b.size[1] - 560) / 2, -58),
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

-- Coins and Gems (rebuilt when the form factor changes).
function LobbyHud:_buildTopRight()
	for _, part in { self.coins, self.gems } do
		part:Destroy()
	end
	-- The two pills fill the column's width with the grid's gap between them.
	local p, grid = LobbyHud.PILLS, self.grid
	local coinsW = grid.column - grid.gap - p.gemsW
	local fire = self.fire
	self.coins = Kit.CurrencyPill.new(self.topRight, {
		name = "Coins",
		rect = { 0, 0, coinsW, p.h },
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
		rect = { coinsW + grid.gap, 0, p.gemsW, p.h },
		currency = "gems",
		value = self.gemValue,
		textSize = LobbyHud.TEXT.currency,
		iconSize = 30,
		onPress = function()
			fire("onCurrency", "gems")
		end,
	})
	self.coins:SetValue(self.coinValue, true)
	self.gems:SetValue(self.gemValue, true)
	self.parts.coins, self.parts.gems = self.coins.root, self.gems.root
end

-- The menu tiles in the run's grid for this screen (HudLayout "tiles",
-- Layout.TileGrid); rebuilt when the form factor changes it.
function LobbyHud:_buildTiles()
	for _, tile in ipairs(self.tiles) do
		tile:Destroy()
	end
	table.clear(self.tiles)
	if self.menuHint then
		self.menuHint:Destroy()
	end
	local cfg = Layout.ForScreen(self.layout.tiles)
	local tiles = Layout.TileGrid(cfg, #LobbyHudModel.TILES)
	self.tileCfg, self.tileColumns = cfg, tiles.columns
	local holder = self.tileRegion
	holder.AnchorPoint = Vector2.new(cfg.anchor[1], cfg.anchor[2])
	holder.Position = UDim2.new(cfg.pos[1], cfg.pos[2], cfg.pos[3], cfg.pos[4])
	holder.Size = UDim2.fromOffset(tiles.w, tiles.h)
	local fire = self.fire
	for index, tile in LobbyHudModel.TILES do
		local button = Kit.IconButton.new(holder, {
			name = tile.id,
			rect = tiles.rects[index],
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
	self.menuHint = region(holder, "MenuHint", {
		Position = UDim2.fromOffset(0, -46),
		Size = UDim2.fromOffset(tiles.w, 36),
		Visible = self.menuHintShown == true,
	})
	Kit.KeyCap.new(self.menuHint, { name = "Key", rect = { 0, 0, 0, 34 }, text = "RB", variant = "cap" })
	Kit.Text.new(self.menuHint, {
		name = "Label",
		rect = { 58, 0, tiles.w - 58, 34 },
		text = "Menu",
		role = "hudSmall",
		outline = true,
	})
end

-- The level/XP press area in the bottom region's px (HudLayout "bottom"):
-- from the level text's left to the XP text's right, the bar's height plus
-- the text's overhang.
function LobbyHud.XpPress(bottom)
	local level, text = bottom.level, bottom.xpText
	return { level[1], level[2], text[1] + text[3] - level[1], level[4] }
end

-- The game-update plaque: one line on desktop, two on phones.
function LobbyHud:_buildNotice()
	if self.notice then
		self.notice:Destroy()
	end
	-- Centred over the bar, the grid's gap above its text.
	local w = self.layout.bottom.size[1]
	local h = if self.phone then LobbyHud.PHONE.noticeH else 46
	self.noticeRegion.Position = UDim2.fromOffset((w - 560) / 2, -self.grid.gap - h)
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
	self:_placePopups()
end

-- The XP pop-up lane ends just above the XP bar, or above the notice plaque
-- while it shows (its height differs on phones), so a pop-up never runs
-- under the plaque.
function LobbyHud:_placePopups()
	local lane, gap = self.layout.bottom.popups, LobbyHud.POPUP_GAP
	local bottom = -gap
	if self.noticeRegion.Visible then
		bottom = self.noticeRegion.Position.Y.Offset - gap
	end
	self.popups.Position = UDim2.fromOffset(lane[1], bottom - lane[4])
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
	local tiles = Layout.ForScreen(self.layout.tiles)
	local tilesChanged = tiles.columns ~= self.tileCfg.columns
		or tiles.tile[1] ~= self.tileCfg.tile[1]
		or tiles.tile[2] ~= self.tileCfg.tile[2]
		or tiles.centreY ~= self.tileCfg.centreY
	if phone == self.phone and not tilesChanged then
		return
	end
	if tilesChanged then
		self:_buildTiles()
	end
	if phone ~= self.phone then
		self.phone = phone
		self:_buildNotice()
		if self.party then
			self:SetParty(self.party)
		end
	end
	self:_link()
	self:_place()
end

-- Gamepad neighbours: the tile grid, the top-right row, the party column, the
-- hotbar and the Settings button under the tiles, joined where they face each
-- other.
function LobbyHud:_link()
	local function hit(component): GuiButton?
		local control = component and component.control
		return control and control.hit
	end
	local gear = hit(self.settings) :: GuiButton
	local columns = self.tileColumns
	local count = #self.tiles
	-- The bottom row's first tile, and the top row's last.
	local bottomLeft = (math.ceil(count / columns) - 1) * columns + 1
	local topRight = math.min(columns, count)
	for index, tile in ipairs(self.tiles) do
		local n = LobbyHudModel.TileNeighbours(index, columns)
		local button = hit(tile) :: GuiButton
		button.NextSelectionUp = if n.up then hit(self.tiles[n.up]) else hit(self.coins)
		-- Down from the bottom row: the left tile to Settings under it, the
		-- others to the XP bar.
		button.NextSelectionDown = if n.down then hit(self.tiles[n.down]) elseif n.left then self.xpControl.hit else gear
		button.NextSelectionLeft = if n.left then hit(self.tiles[n.left]) else nil
		button.NextSelectionRight = if n.right then hit(self.tiles[n.right]) else self.titleControl.hit
	end
	local top = { hit(self.coins), hit(self.gems) }
	for index, button in top do
		button.NextSelectionLeft = top[index - 1] or hit(self.tiles[topRight])
		button.NextSelectionRight = top[index + 1]
		button.NextSelectionDown = self.titleControl.hit
	end
	self.titleControl.hit.NextSelectionUp = top[#top]
	self.titleControl.hit.NextSelectionLeft = hit(self.tiles[topRight])
	-- The XP bar sits between the tiles and the hotbar.
	local xp = self.xpControl.hit
	for index, slot in self.slots do
		local button = hit(slot) :: GuiButton
		button.NextSelectionLeft = hit(self.slots[index - 1])
		button.NextSelectionRight = hit(self.slots[index + 1])
		button.NextSelectionUp = xp
	end
	xp.NextSelectionUp = hit(self.tiles[bottomLeft])
	xp.NextSelectionDown = hit(self.slots[1])
	xp.NextSelectionLeft = hit(self.tiles[bottomLeft])
	-- Settings sits under the tiles' bottom-left tile, left of the hotbar.
	local first = hit(self.slots[1]) :: GuiButton
	first.NextSelectionLeft = gear
	gear.NextSelectionRight = first
	gear.NextSelectionUp = hit(self.tiles[bottomLeft])
	gear.NextSelectionLeft = nil
	gear.NextSelectionDown = nil
end

-- The control a gamepad selects first: the Inventory tile.
function LobbyHud:DefaultSelection(): GuiObject
	return self.tiles[1].control.hit
end

-- Shows the gamepad "RB Menu" hint over the tiles.
function LobbyHud:SetMenuHint(visible: boolean)
	self.menuHintShown = visible
	self.menuHint.Visible = visible
end

-- Places the regions on the HUD grid (D30), as the run's HUD places its own
-- (HudController.PlaceTop): the right-hand column (Coins and Gems, the Party
-- panel the grid's gap under them) the grid's margin from the top (below the
-- bar only when its right-hand area reaches over them); the menu tiles at the
-- left (centred on the screen's height, or on phones the grid's gap under
-- Roblox's buttons); each column at one edge by the edge rule
-- (Layout.PlaceColumns); Settings in the bottom-left corner
-- (HudModel.GearCorner).
function LobbyHud:_place()
	local screen = self.screen
	if screen == nil then
		return
	end
	local grid = self.grid
	local k = math.max(screen.scale or 1, 0.01)
	local bar = self.topBar or { inset = 58 / k, rowTop = HudModel.TopRow(58) / k, reachesOver = false }
	local rightTop = grid.margin
	if bar.reachesOver then
		rightTop = math.max(rightTop, math.ceil(bar.inset + grid.gap))
	end
	local leftTop = math.ceil(bar.rowTop + HudModel.TOP_BUTTON / k + grid.gap)
	local centred = type(self.tileCfg.centreY) == "number"
	self.placed = Layout.PlaceColumns({
		right = { stack = { self.topRight, self.partyRegion }, top = rightTop },
		left = {
			stack = if centred then {} else { self.tileRegion },
			free = if centred then { self.tileRegion } else {},
			top = leftTop,
		},
	}, screen)
	local left, bottom = HudModel.GearCorner(grid, self.layout.gear, screen)
	self.settingsRegion.Position = UDim2.new(0, left, 1, -bottom)
end

-- The screen (Kit.Scale.HudScreen: {width, height, scale, touch, insets}):
-- places the regions on the grid for it (_place).
function LobbyHud:SetScreen(screen)
	self.screen = screen
	self:_place()
end

-- The Roblox top bar: `designPx` how far it reaches down and `rowTop` the top
-- of its button row, in design px (default: the row under a standard bar).
-- The tiles keep the grid's gap under the buttons on phones; Coins and Gems
-- go below the bar only when its right-hand area reaches over them
-- (`reachesOver`).
function LobbyHud:SetTopInset(designPx: number, rowTop: number?, reachesOver: boolean?)
	local k = if self.screen then math.max(self.screen.scale or 1, 0.01) else 1
	self.topBar = {
		inset = designPx,
		rowTop = rowTop or HudModel.TopRow(designPx * k) / k,
		reachesOver = reachesOver == true,
	}
	self:_place()
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
		Size = UDim2.fromOffset(self.partyParts.list[3], height),
	})
	holder:SetAttribute("LobbyRow", true)
	return holder
end

function LobbyHud:_member(holder: Frame, member)
	local fire = self.fire
	local r = LobbyHud.ROW
	-- On phones a row takes the panel's width (the add-player button sits in
	-- the title row there).
	local w = if self.phone then self.partyParts.ruleW else self.partyParts.rowW
	-- PlayerRow names its root after the player (`name` is both).
	local row = Kit.PlayerRow.new(holder, {
		rect = { 0, 0, w, LobbyHud.ROW_H },
		userId = member.userId,
		name = member.name,
		leader = member.leader,
		compact = true,
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
	-- "LV. n" shows once the member's level is known (their replicated Level
	-- attribute); until then the XP bar hides too, so no row shows a bar
	-- without its level.
	local function levelKnown()
		if row.levelBar and row.levelLabel then
			row.levelBar.root.Visible = row.levelLabel.Text ~= ""
		end
	end
	if row.levelLabel then
		row.levelLabel:GetPropertyChangedSignal("Text"):Connect(levelKnown)
		levelKnown()
	end
	-- The rule runs on under the add-player button.
	table.insert(
		self.rows,
		Kit.Divider.new(holder, {
			name = "Rule",
			rect = { 0, LobbyHud.ROW_H - 2, self.partyParts.ruleW, 2 },
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
	local width = self.partyParts.ruleW
	-- The first member stays at the top with the add-player button.
	local pinned = region(self.pinned, "Row0", { Size = UDim2.fromScale(1, 1) })
	pinned:SetAttribute("LobbyRow", true)
	local first = self:_member(pinned, party.members[1])
	-- On phones the list shows few rows: with three or more members a waiting
	-- invite is below the fold, so the add-player button carries a dot.
	local hiddenInvite = self.phone and #party.invites > 0 and #party.members >= 3
	local invite = Kit.IconButton.new(if self.phone then self.partyRegion else pinned, {
		name = "Invite",
		rect = if self.phone then self.partyParts.phoneInvite else self.partyParts.invite,
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
		self:_member(self:_holder(order, LobbyHud.ROW_H), party.members[index])
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
	self:_placePopups()
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
	self.xpPress.maid:Clean()
	self.list:Destroy()
	self.panel:Destroy()
	self.pinned:Destroy()
	self.notice:Destroy()
	self.titleRow.maid:Clean()
	for _, frame in { self.topRight, self.tileRegion, self.partyRegion, self.bottom, self.settingsRegion } do
		frame:Destroy()
	end
end

return LobbyHud
