-- The lobby screen in the parchment-and-leather style (docs/ui/LobbyScreen.md,
-- art/reference/ui/parchment/13_lobby_master.png), drawn from the "lobby"
-- section of HudLayout.json with the pm_* sprites: the profile (headshot, name,
-- level and XP), Coins, Gems and Settings, the navigation tiles, the party panel,
-- the Enter button with the server dropdown, and a status strip.
-- Display only: LobbyHudController feeds it and handles the signals.
--
-- Until a sprite is uploaded Widgets draws a paper stand-in, and the words the
-- art would carry (tile names, ENTER) are added so the screen still reads.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local UiAssets = require(ReplicatedStorage.Shared.UI.UiAssets)
local Layout = require(script.Parent.Layout)
local Widgets = require(script.Parent.Widgets)

local LobbyHud = {}
LobbyHud.__index = LobbyHud

local HOVER = TweenInfo.new(0.12, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
-- Every sprite carries this much transparent padding around its art.
local SPRITE_PAD = 2
-- Below this design width the Enter button reaches under the party panel.
local NARROW_WIDTH = 1544
-- Clearance kept under the Roblox top bar, in design pixels.
local TOP_GAP = 8
-- Room kept from the screen's left and right edges, in screen pixels (the
-- Roblox menu button's own margin), and between the top-right pills.
local EDGE = 12
local ROW_GAP = 10
-- Between the profile and the navigation grid, and Coins and the party panel,
-- in design px.
local COLUMN_GAP = 14
-- Coins, Gems and Settings sit in the Roblox top bar's row, right to left.
local TOP_ROW = { "Settings", "Gems", "Coins" }
-- Smallest touch target on screen, in points (Roblox's mobile guidance).
local MIN_TAP = 44
-- Room kept clear on each side of the status strip at the top, in design px.
local STATUS_GAP = 16

local function rect(entry, props)
	props = props or {}
	props.Position = Layout.Position(entry.rect)
	props.Size = Layout.Size(entry.rect)
	return props
end

local function hasArt(name: string): boolean
	return UiAssets.image(name) ~= nil
end

-- A sprite filling `parent` (its art lands on the parent's bounds; the padding
-- spills over).
local function art(name: string, parent: Instance, zIndex: number?): GuiObject
	return Widgets.Sprite(name, {
		Name = "Art",
		Position = UDim2.fromOffset(-SPRITE_PAD, -SPRITE_PAD),
		Size = UDim2.new(1, SPRITE_PAD * 2, 1, SPRITE_PAD * 2),
		ZIndex = zIndex or 2,
	}, parent)
end

-- A top-level holder placed from a layout entry {anchor, pos, size}.
local function holder(name: string, entry, parent: Instance): Frame
	local frame = Widgets.Make("Frame", { Name = name, BackgroundTransparency = 1 }, parent)
	Layout.Place(frame, entry)
	return frame
end

-- Text that shrinks to fit its box, from the entry's size down to `minSize`.
local function fitted(label: TextLabel, maxSize: number, minSize: number?): TextLabel
	label.TextScaled = true
	Widgets.TextCap(label, maxSize, minSize or 12)
	return label
end

-- A transparent button over `parent` (or `area` inside it) that grows slightly
-- on hover, selection and press, unless `steady` says motion is reduced.
-- `onFocus(bool)` hears hover and gamepad selection. `pad` widens the touch area
-- past the art on every side for small buttons.
local function hit(
	parent: Instance,
	name: string,
	steady: () -> boolean,
	onFocus: ((boolean) -> ())?,
	area,
	pad: number?
)
	pad = pad or 0
	local button = Widgets.Make("TextButton", {
		Name = name,
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Position = if area then UDim2.fromOffset(area[1] - pad, area[2] - pad) else UDim2.fromOffset(-pad, -pad),
		Size = if area
			then UDim2.fromOffset(area[3] + pad * 2, area[4] + pad * 2)
			else UDim2.new(1, pad * 2, 1, pad * 2),
		ZIndex = 8,
	}, parent)
	local scale = Widgets.Make("UIScale", { Scale = 1 }, parent)
	local function to(value: number)
		if steady() then
			scale.Scale = 1
			return
		end
		TweenService:Create(scale, HOVER, { Scale = value }):Play()
	end
	local hovering = false
	local function focus(on: boolean)
		hovering = on
		to(if on then 1.04 else 1)
		if onFocus then
			onFocus(on)
		end
	end
	button.MouseEnter:Connect(function()
		focus(true)
	end)
	button.MouseLeave:Connect(function()
		focus(false)
	end)
	button.SelectionGained:Connect(function()
		focus(true)
	end)
	button.SelectionLost:Connect(function()
		focus(false)
	end)
	button.MouseButton1Down:Connect(function()
		to(0.97)
	end)
	button.InputEnded:Connect(function(input: InputObject)
		-- Touch has no hover: a lifted finger returns the button to rest.
		if input.UserInputType == Enum.UserInputType.Touch then
			focus(false)
		elseif input.UserInputType == Enum.UserInputType.MouseButton1 then
			to(if hovering then 1.04 else 1)
		end
	end)
	return button
end

local function rounded(colorKey: string, radius: UDim, props, parent: Instance): Frame
	local frame = Widgets.Make("Frame", {
		BackgroundColor3 = Layout.Color(colorKey),
		BorderSizePixel = 0,
	}, parent)
	for key, value in props do
		(frame :: any)[key] = value
	end
	Widgets.Make("UICorner", { CornerRadius = radius }, frame)
	return frame :: Frame
end

-- A paper name tag (tile names, the status strip).
local function tag(entry, props, parent: Instance): (Frame, TextLabel)
	local frame = rounded("paper", UDim.new(0, 8), props, parent)
	Widgets.Make("UIStroke", { Color = Layout.Color("paperEdge"), Thickness = 2 }, frame)
	local label = Widgets.Text(entry, {
		Name = "Text",
		Size = UDim2.new(1, -16, 1, -4),
		Position = UDim2.fromOffset(8, 2),
		TextXAlignment = Enum.TextXAlignment.Center,
		TextStrokeTransparency = 1,
		ZIndex = frame.ZIndex + 1,
	}, frame)
	return frame, label
end

local function inkText(entry, props, parent: Instance): TextLabel
	props.TextStrokeTransparency = 1
	return Widgets.Text(entry, props, parent)
end

-- Widens a small button's touch area past its art until it is at least MIN_TAP
-- points on screen at `screenScale` (never past `target.maxPad` on each side,
-- {left, top, right, bottom} in reference px, which keeps
-- neighbours apart).
local function padTouch(target, screenScale: number)
	local want = MIN_TAP / math.max(screenScale, 0.01)
	local limit = target.maxPad -- {left, top, right, bottom}
	local x = math.max(0, (want - target.w) / 2)
	local y = math.max(0, (want - target.h) / 2)
	local left, right = math.min(x, limit[1]), math.min(x, limit[3])
	local up, down = math.min(y, limit[2]), math.min(y, limit[4])
	target.button.Position = UDim2.fromOffset(-left, -up)
	target.button.Size = UDim2.new(1, left + right, 1, up + down)
end

function LobbyHud.new(parent: Instance, layout, steady: () -> boolean)
	local cfg = layout.lobby
	local self = setmetatable({
		cfg = cfg,
		steady = steady,
		-- Top-anchored widgets and their layout entries, moved down by Fit when the
		-- Roblox top bar would cover them.
		topWidgets = {},
		-- Small buttons whose touch areas Fit sizes for the screen.
		targets = {},
		screenScale = 1,
		NavPressed = Signal.new(),
		ProfilePressed = Signal.new(),
		SettingsPressed = Signal.new(),
		EnterPressed = Signal.new(),
		ServerPressed = Signal.new(),
		InvitePressed = Signal.new(),
		LeavePressed = Signal.new(),
		InviteAnswered = Signal.new(), -- (partyId, accept)
	}, LobbyHud)
	self.root = Widgets.Make("Frame", {
		Name = "Lobby",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
	}, parent)
	self.topByName = {}
	local function top(name: string, entry): Frame
		local frame = holder(name, entry, self.root)
		table.insert(self.topWidgets, { frame, entry, name })
		self.topByName[name] = { frame, entry }
		return frame
	end

	-- Profile: the live headshot shows through the frame's portrait window. Its
	-- paper stand-in has no window, so until the art is uploaded the headshot
	-- sits on top of it instead.
	local profileCfg = cfg.profile
	local profile = top("Profile", profileCfg)
	art(profileCfg.sprite, profile, if hasArt(profileCfg.sprite) then 3 else 1)
	self.avatar = Widgets.Make(
		"ImageLabel",
		rect(profileCfg.avatar, {
			Name = "Headshot",
			BackgroundColor3 = Layout.Color("photo"),
			BorderSizePixel = 0,
			ScaleType = Enum.ScaleType.Crop,
			ZIndex = 2,
		}),
		profile
	)
	self.nameText = fitted(
		inkText(profileCfg.name, rect(profileCfg.name, { Name = "PlayerName", ZIndex = 4 }), profile),
		profileCfg.name.textSize,
		16
	)
	self.levelText = fitted(
		inkText(profileCfg.level, rect(profileCfg.level, { Name = "Level", Text = "LV.", ZIndex = 4 }), profile),
		profileCfg.level.textSize
	)
	self.xpBar = Widgets.Bar({
		rect = profileCfg.xp.rect,
		fill = profileCfg.xp.fill,
		fillColor = profileCfg.xp.fillColor,
		-- The art carries its own groove; its stand-in needs one drawn.
		trackColor = if hasArt(profileCfg.sprite) then nil else "line",
	}, profile)
	Widgets.SetBar(self.xpBar, 0, true) -- empty until the first progression snapshot
	hit(profile, "OpenProgress", steady).Activated:Connect(function()
		self.ProfilePressed:Fire()
	end)

	-- Coins, Gems and Settings, top right.
	local function pill(name: string, entry): TextLabel
		local frame = top(name, entry)
		art(entry.sprite, frame)
		local value = inkText(entry.value, rect(entry.value, { Name = "Value", Text = "0", ZIndex = 4 }), frame)
		return fitted(value, entry.value.textSize, 11)
	end
	self.coinsText = pill("Coins", cfg.coins)
	self.gemsText = pill("Gems", cfg.gems)
	local settings = top("Settings", cfg.settings)
	art(cfg.settings.sprite, settings)
	local settingsButton = hit(settings, "OpenSettings", steady)
	settingsButton.Activated:Connect(function()
		self.SettingsPressed:Fire()
	end)
	self:_target(settingsButton, cfg.settings.size[1], cfg.settings.size[2], cfg.settings.touchPad, false)

	-- Navigation tiles in a grid; each names itself on hover or selection (and
	-- always while its art is not uploaded).
	local navCfg = cfg.nav
	local rows = math.ceil(#navCfg.buttons / navCfg.columns)
	self.navHeight = navCfg.pitch[2] * (rows - 1) + navCfg.tile[2]
	local nav = top("Navigation", {
		anchor = navCfg.anchor,
		pos = navCfg.pos,
		size = { navCfg.pitch[1] * (navCfg.columns - 1) + navCfg.tile[1], self.navHeight },
	})
	self.navScale = Widgets.Make("UIScale", { Scale = 1 }, nav)
	for index, entry in navCfg.buttons do
		local column = (index - 1) % navCfg.columns
		local row = (index - 1) // navCfg.columns
		local tile = Widgets.Make("Frame", {
			Name = entry.id,
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(column * navCfg.pitch[1], row * navCfg.pitch[2]),
			Size = UDim2.fromOffset(navCfg.tile[1], navCfg.tile[2]),
		}, nav)
		art(entry.sprite, tile)
		local always = not hasArt(entry.sprite)
		local nameTag, label =
			tag(navCfg.label, rect(navCfg.label, { Name = "Name", Visible = always, ZIndex = 5 }), tile)
		label.Text = entry.label
		fitted(label, navCfg.label.textSize)
		local button = hit(tile, "Open" .. entry.id, steady, function(on)
			nameTag.Visible = always or on
		end)
		button.Activated:Connect(function()
			self.NavPressed:Fire(entry.id)
		end)
	end

	-- Party panel: "PARTY" and its count, divider, Leave, and a scrolling list.
	local partyCfg = cfg.party
	-- Placed by Fit, which may move it up on short screens.
	local party = holder("Party", partyCfg, self.root)
	self.party = party
	self.partyScale = Widgets.Make("UIScale", { Scale = 1 }, party)
	art(partyCfg.sprite, party)
	inkText(partyCfg.title, rect(partyCfg.title, { Name = "Title", Text = partyCfg.title.text, ZIndex = 4 }), party)
	self.partyCount = inkText(partyCfg.count, rect(partyCfg.count, { Name = "Count", Text = "", ZIndex = 4 }), party)
	Widgets.Make(
		"Frame",
		rect(partyCfg.divider, {
			Name = "Divider",
			BackgroundColor3 = Layout.Color("line"),
			BorderSizePixel = 0,
			ZIndex = 4,
		}),
		party
	)
	self.leave = self:_spriteButton("Leave", partyCfg.leave, party, function()
		self.LeavePressed:Fire()
	end)
	self.leave.Visible = false
	local listCfg = partyCfg.list
	local listRect = listCfg.rect
	self.track = rounded("scrollTrack", UDim.new(0.5, 0), {
		Name = "ScrollTrack",
		Position = UDim2.fromOffset(listRect[1] + listRect[3] - listCfg.scrollBar, listRect[2]),
		Size = UDim2.fromOffset(listCfg.scrollBar, listRect[4]),
		Visible = false,
		ZIndex = 4,
	}, party)
	self.list = Widgets.Make(
		"ScrollingFrame",
		rect(listCfg, {
			Name = "List",
			BackgroundTransparency = 1,
			BorderSizePixel = 0,
			CanvasSize = UDim2.new(),
			AutomaticCanvasSize = Enum.AutomaticSize.Y,
			ScrollBarThickness = listCfg.scrollBar,
			ScrollBarImageColor3 = Layout.Color("thumb"),
			VerticalScrollBarInset = Enum.ScrollBarInset.ScrollBar,
			ScrollingDirection = Enum.ScrollingDirection.Y,
			ZIndex = 5,
		}),
		party
	)
	Widgets.Make("UIListLayout", { SortOrder = Enum.SortOrder.LayoutOrder }, self.list)
	local function showTrack()
		self.track.Visible = self.list.AbsoluteCanvasSize.Y > self.list.AbsoluteWindowSize.Y + 1
	end
	self.list:GetPropertyChangedSignal("AbsoluteCanvasSize"):Connect(showTrack)
	self.list:GetPropertyChangedSignal("AbsoluteWindowSize"):Connect(showTrack)

	-- Enter (its lettering is painted on the art) with a veil while busy.
	local enterCfg = cfg.enter
	local enter = holder("Enter", enterCfg, self.root)
	local enterArt = art(enterCfg.sprite, enter)
	if not hasArt(enterCfg.sprite) then
		-- The stand-in plate covers only the banner (the part that is the button).
		enterArt.Position = UDim2.fromOffset(enterCfg.hit[1], enterCfg.hit[2])
		enterArt.Size = UDim2.fromOffset(enterCfg.hit[3], enterCfg.hit[4])
	end
	if not hasArt(enterCfg.sprite) then
		for _, key in { "title", "subtitle" } do
			local entry = enterCfg[key]
			inkText(
				entry,
				rect(entry, {
					Name = key,
					Text = entry.text,
					TextXAlignment = Enum.TextXAlignment.Center,
					ZIndex = 4,
				}),
				enter
			)
		end
	end
	self.enterShade = rounded(
		"veil",
		UDim.new(0, 10),
		rect(enterCfg.veil, {
			Name = "Busy",
			BackgroundTransparency = enterCfg.veil.transparency,
			Visible = false,
			ZIndex = 7,
		}),
		enter
	)
	self.enterButton = hit(enter, "EnterWorld", steady, nil, enterCfg.hit)
	self.enterButton.Activated:Connect(function()
		self.EnterPressed:Fire()
	end)

	-- Server dropdown beside Enter.
	local serverCfg = cfg.server
	local server = holder("Server", serverCfg, self.root)
	art(serverCfg.sprite, server)
	fitted(
		inkText(
			serverCfg.label,
			rect(serverCfg.label, { Name = "Label", Text = serverCfg.label.text, ZIndex = 4 }),
			server
		),
		serverCfg.label.textSize
	)
	local serverButton = hit(server, "ChooseServer", steady)
	serverButton.Activated:Connect(function()
		self.ServerPressed:Fire()
	end)
	self:_target(serverButton, serverCfg.size[1], serverCfg.size[2], serverCfg.touchPad, false)

	-- Status strip, top centre between the profile and the currencies (deploy
	-- status, invites sent, maintenance); up to two lines.
	local statusCfg = cfg.status
	self.status, self.statusText = tag(statusCfg.text, {
		Name = "Status",
		Visible = false,
		ZIndex = 6,
	}, self.root)
	Layout.Place(self.status, statusCfg)
	self.statusText.TextWrapped = true
	fitted(self.statusText, statusCfg.text.textSize)
	return self
end

-- Registers a small button whose touch area Fit grows on small screens. `party`
-- buttons sit in the party panel and shrink with it.
function LobbyHud:_target(button: GuiObject, w: number, h: number, maxPad: { number }, party: boolean)
	local target = { button = button, w = w, h = h, maxPad = maxPad, party = party }
	table.insert(self.targets, target)
	padTouch(target, self.screenScale * (if party then self.partyScale.Scale else 1))
end

-- A small sprite button at `entry.rect` (party panel) with a touch area that
-- grows to MIN_TAP on small screens, up to `entry.touchPad` ({left, top, right,
-- bottom}) so it never reaches a neighbouring button.
function LobbyHud:_spriteButton(name: string, entry, parent: Instance, onPress)
	local frame = Widgets.Make("Frame", rect(entry, { Name = name, BackgroundTransparency = 1, ZIndex = 6 }), parent)
	Widgets.Sprite(entry.sprite, { Size = UDim2.fromScale(1, 1), ZIndex = 6 }, frame)
	local button = hit(frame, name .. "Button", self.steady)
	button.Activated:Connect(onPress)
	self:_target(button, entry.rect[3], entry.rect[4], entry.touchPad or { 0, 0, 0, 0 }, true)
	return frame
end

-- Adds a widget (from the controller) that Fit places by name: "XpPopups"
-- beside the navigation grid.
function LobbyHud:AddTopWidget(frame: GuiObject, entry, name: string?)
	Layout.Place(frame, entry)
	table.insert(self.topWidgets, { frame, entry, name })
end

-- Fits the screen to `width` × `height` reference pixels drawn at `screenScale`,
-- with the Roblox top bar ending `topInset` reference pixels down:
-- * Coins, Gems and Settings sit at the very top of the right edge, level with
--   the top bar's buttons;
-- * the profile sits right under the top bar's buttons at the left edge, with
--   the navigation grid right under it (shrunk to end above the bottom edge)
--   and the XP pop-ups beside the grid;
-- * the party panel sits right under Coins, shrinking only to end above the
--   Enter group under it (never below half size);
-- * the status strip sits between the profile and Coins when there is room,
--   else above Enter;
-- * small buttons' touch areas grow to MIN_TAP points.
function LobbyHud:Fit(width: number, height: number, topInset: number?, screenScale: number?)
	local cfg = self.cfg
	self.screenScale = screenScale or 1
	local top = topInset or 0
	local edge = EDGE / self.screenScale
	local navCfg, partyCfg = cfg.nav, cfg.party

	-- The left column: profile, then the navigation grid.
	local profileTop = top + TOP_GAP
	local profileBottom = profileTop + cfg.profile.size[2]
	local navTop = profileBottom + COLUMN_GAP
	local navRoom = height - navCfg.bottomMargin - navTop
	self.navScale.Scale = math.clamp(navRoom / self.navHeight, 0.5, 1)
	local navWidth = (navCfg.pitch[1] * (navCfg.columns - 1) + navCfg.tile[1]) * self.navScale.Scale
	-- Coins, Gems and Settings right to left along the top edge.
	local x = -edge
	local rowTop = edge
	local rowBottom = 0
	for _, name in TOP_ROW do
		local item = self.topByName[name]
		if item then
			local frame, entry = item[1], item[2]
			frame.AnchorPoint = Vector2.new(1, 0)
			frame.Position = UDim2.new(1, x, 0, rowTop)
			x -= entry.size[1] + ROW_GAP
			rowBottom = math.max(rowBottom, rowTop + entry.size[2])
		end
	end
	for _, item in self.topWidgets do
		local frame, name = item[1], item[3]
		if name == "Profile" then
			frame.Position = UDim2.fromOffset(edge, profileTop)
		elseif name == "Navigation" then
			frame.Position = UDim2.fromOffset(edge, navTop)
		elseif name == "XpPopups" then
			frame.Position = UDim2.fromOffset(edge + navWidth + COLUMN_GAP, navTop)
		end
	end

	local below = if width < NARROW_WIDTH
		then cfg.enter.size[2] - cfg.enter.pos[4]
		else cfg.server.size[2] - cfg.server.pos[4]
	local bottom = height - below - 10
	local partyTop = rowBottom + COLUMN_GAP
	self.partyScale.Scale = math.clamp((bottom - partyTop) / partyCfg.size[2], 0.5, 1)
	self.party.AnchorPoint = Vector2.new(1, 0)
	self.party.Position = UDim2.new(1, -edge, 0, partyTop)

	local statusCfg = cfg.status
	local left = edge + cfg.profile.size[1] + STATUS_GAP
	local right = width + x - STATUS_GAP
	local room = right - left
	if room >= statusCfg.minWidth then
		local stripWidth = math.min(statusCfg.size[1], room)
		self.status.AnchorPoint = Vector2.new(0.5, 0)
		self.status.Position = UDim2.fromOffset((left + right) / 2, rowTop)
		self.status.Size = UDim2.fromOffset(stripWidth, statusCfg.size[2])
	else
		self.status.AnchorPoint = Vector2.new(0.5, 1)
		self.status.Position = UDim2.new(0.5, 0, 1, cfg.enter.pos[4] - cfg.enter.size[2] - 10)
		self.status.Size = UDim2.fromOffset(math.min(statusCfg.size[1], width - 40), statusCfg.size[2])
	end

	local live = {}
	for _, target in self.targets do
		if target.button.Parent ~= nil then
			table.insert(live, target)
			padTouch(target, self.screenScale * (if target.party then self.partyScale.Scale else 1))
		end
	end
	self.targets = live
end

function LobbyHud:SetProfile(name: string, thumbnail: string?)
	self.nameText.Text = name
	self.avatar.Image = thumbnail or ""
end

-- view: the progression snapshot {level, xp, xpToNext}; no xpToNext = level cap.
function LobbyHud:SetProgress(view, instant: boolean?)
	local isMax = view.xpToNext == nil
	self.levelText.Text = HudModel.LevelText(view.level, isMax)
	Widgets.SetBar(self.xpBar, if isMax then 1 else HudModel.XpFraction(view.xp, view.xpToNext), instant)
end

function LobbyHud:SetCurrency(coins: number?, gems: number?)
	self.coinsText.Text = HudModel.Thousands(coins)
	self.gemsText.Text = HudModel.Thousands(gems)
end

function LobbyHud:_row(order: number, entry): Frame
	local row = Widgets.Make("Frame", {
		Name = "Row" .. order,
		BackgroundTransparency = 1,
		LayoutOrder = order,
		Size = UDim2.new(1, 0, 0, entry.height),
		ZIndex = 5,
	}, self.list)
	Widgets.Make(
		"Frame",
		rect(entry.rule, {
			Name = "Rule",
			BackgroundColor3 = Layout.Color("rule"),
			BorderSizePixel = 0,
			ZIndex = 5,
		}),
		row
	)
	return row :: Frame
end

-- members: {{userId, name, leader, thumbnail?}}; invites: {{partyId, from}};
-- canInvite: the leader's row offers Invite; inParty: show Leave. Free places up
-- to `maxSize` show as empty slots.
function LobbyHud:SetParty(members, invites, maxSize: number, canInvite: boolean, inParty: boolean)
	local cfg = self.cfg.party
	self.partyCount.Text = HudModel.PartyCount(#members, maxSize)
	self.leave.Visible = inParty
	-- The rows' buttons are about to go: forget their touch areas.
	local kept = {}
	for _, target in self.targets do
		if not target.button:IsDescendantOf(self.list) then
			table.insert(kept, target)
		end
	end
	self.targets = kept
	for _, child in self.list:GetChildren() do
		if child:IsA("GuiObject") then
			child:Destroy()
		end
	end
	local order = 0
	local memberCfg = cfg.member
	for _, member in members do
		order += 1
		local row = self:_row(order, memberCfg)
		local headshot = Widgets.Make(
			"ImageLabel",
			rect(memberCfg.headshot, {
				Name = "Headshot",
				BackgroundColor3 = Layout.Color("photo"),
				BorderSizePixel = 0,
				Image = member.thumbnail or "",
				ScaleType = Enum.ScaleType.Crop,
				ZIndex = 6,
			}),
			row
		)
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 6) }, headshot)
		Widgets.Make("UIStroke", { Color = Layout.Color("photoEdge"), Thickness = 1.5 }, headshot)
		fitted(
			inkText(memberCfg.name, rect(memberCfg.name, { Name = "MemberName", Text = member.name, ZIndex = 6 }), row),
			memberCfg.name.textSize
		)
		if member.leader then
			Widgets.Sprite(memberCfg.crown.sprite, rect(memberCfg.crown, { Name = "Leader", ZIndex = 6 }), row)
			if canInvite then
				self:_spriteButton("InviteFriends", memberCfg.invite, row, function()
					self.InvitePressed:Fire()
				end)
			end
		end
	end
	local inviteCfg = cfg.invite
	for _, invite in invites do
		order += 1
		local row = self:_row(order, inviteCfg)
		fitted(
			inkText(
				inviteCfg.text,
				rect(inviteCfg.text, { Name = "From", Text = "From " .. invite.from, ZIndex = 6 }),
				row
			),
			inviteCfg.text.textSize
		)
		self:_spriteButton("Accept", inviteCfg.accept, row, function()
			self.InviteAnswered:Fire(invite.partyId, true)
		end)
		self:_spriteButton("Decline", inviteCfg.decline, row, function()
			self.InviteAnswered:Fire(invite.partyId, false)
		end)
	end
	local emptyCfg = cfg.empty
	for _ = #members + 1, maxSize do
		order += 1
		local row = self:_row(order, emptyCfg)
		rounded("dot", UDim.new(0.5, 0), rect(emptyCfg.dot, { Name = "Free", ZIndex = 6 }), row)
	end
end

-- Shows `text` in the status strip (status and errors), or hides the strip when
-- `text` is nil. The server dropdown always reads "Choose server".
function LobbyHud:SetServerLine(text: string?)
	self.statusText.Text = text or ""
	self.status.Visible = text ~= nil and text ~= ""
end

function LobbyHud:SetEnterBusy(busy: boolean)
	self.enterShade.Visible = busy
	self.enterButton.Active = not busy
end

return LobbyHud
