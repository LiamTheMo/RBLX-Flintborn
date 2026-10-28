-- The lobby screen in the parchment-and-leather style (docs/ui/LobbyScreen.md,
-- art/reference/ui/parchment/13_lobby_master.png), drawn from the "lobby"
-- section of HudLayout.json with the pm_* sprites: the profile (headshot, name,
-- level and XP), Coins, Gems and Settings, the navigation tiles, the party panel,
-- the Enter button with the server dropdown, and a status strip above Enter.
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

-- A transparent button over `parent` that grows slightly on hover, selection and
-- press, unless `steady` says motion is reduced. `onFocus(bool)` hears hover and
-- gamepad selection.
local function hit(parent: Instance, name: string, steady: () -> boolean, onFocus: ((boolean) -> ())?, area)
	local button = Widgets.Make("TextButton", {
		Name = name,
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Position = if area then UDim2.fromOffset(area[1], area[2]) else UDim2.new(),
		Size = if area then UDim2.fromOffset(area[3], area[4]) else UDim2.fromScale(1, 1),
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
	local function focus(on: boolean)
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
	button.MouseButton1Up:Connect(function()
		to(1.04)
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
		Size = UDim2.new(1, -16, 1, 0),
		Position = UDim2.fromOffset(8, 0),
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

function LobbyHud.new(parent: Instance, layout, steady: () -> boolean)
	local cfg = layout.lobby
	local self = setmetatable({
		cfg = cfg,
		steady = steady,
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

	-- Profile: the live headshot shows through the frame's portrait window.
	local profileCfg = cfg.profile
	local profile = holder("Profile", profileCfg, self.root)
	art(profileCfg.sprite, profile, 3)
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
	self.nameText = inkText(profileCfg.name, rect(profileCfg.name, { Name = "PlayerName", ZIndex = 4 }), profile)
	self.levelText =
		inkText(profileCfg.level, rect(profileCfg.level, { Name = "Level", Text = "LV.", ZIndex = 4 }), profile)
	self.levelText.TextScaled = true
	Widgets.Make("UITextSizeConstraint", { MaxTextSize = profileCfg.level.textSize, MinTextSize = 12 }, self.levelText)
	self.xpBar = Widgets.Bar({
		rect = profileCfg.xp.rect,
		fill = profileCfg.xp.fill,
		fillColor = profileCfg.xp.fillColor,
	}, profile)
	Widgets.SetBar(self.xpBar, 0, true) -- empty until the first progression snapshot
	hit(profile, "OpenProgress", steady).Activated:Connect(function()
		self.ProfilePressed:Fire()
	end)

	-- Coins, Gems and Settings, top right.
	local function pill(name: string, entry): TextLabel
		local frame = holder(name, entry, self.root)
		art(entry.sprite, frame)
		return inkText(entry.value, rect(entry.value, { Name = "Value", Text = "0", ZIndex = 4 }), frame)
	end
	self.coinsText = pill("Coins", cfg.coins)
	self.gemsText = pill("Gems", cfg.gems)
	local settings = holder("Settings", cfg.settings, self.root)
	art(cfg.settings.sprite, settings)
	hit(settings, "OpenSettings", steady).Activated:Connect(function()
		self.SettingsPressed:Fire()
	end)

	-- Navigation tiles in a grid; each names itself on hover or selection (and
	-- always while its art is not uploaded).
	local navCfg = cfg.nav
	local rows = math.ceil(#navCfg.buttons / navCfg.columns)
	self.navHeight = navCfg.pitch[2] * (rows - 1) + navCfg.tile[2]
	local nav = holder("Navigation", {
		anchor = navCfg.anchor,
		pos = navCfg.pos,
		size = { navCfg.pitch[1] * (navCfg.columns - 1) + navCfg.tile[1], self.navHeight },
	}, self.root)
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
		local button = hit(tile, "Open" .. entry.id, steady, function(on)
			nameTag.Visible = always or on
		end)
		button.Activated:Connect(function()
			self.NavPressed:Fire(entry.id)
		end)
	end

	-- Party panel: title, divider, Leave, and a scrolling list of rows.
	local partyCfg = cfg.party
	local party = holder("Party", partyCfg, self.root)
	self.partyScale = Widgets.Make("UIScale", { Scale = 1 }, party)
	art(partyCfg.sprite, party)
	self.partyTitle =
		inkText(partyCfg.title, rect(partyCfg.title, { Name = "Title", Text = "PARTY", ZIndex = 4 }), party)
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
	self.leave = Widgets.Make(
		"Frame",
		rect(partyCfg.leave, { Name = "Leave", BackgroundTransparency = 1, Visible = false, ZIndex = 4 }),
		party
	)
	Widgets.Sprite(partyCfg.leave.sprite, { Size = UDim2.fromScale(1, 1), ZIndex = 5 }, self.leave)
	hit(self.leave, "LeaveParty", steady).Activated:Connect(function()
		self.LeavePressed:Fire()
	end)
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
	art(enterCfg.sprite, enter)
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
	self.serverText = inkText(
		serverCfg.label,
		rect(serverCfg.label, {
			Name = "Label",
			Text = serverCfg.label.text,
			ZIndex = 4,
		}),
		server
	)
	hit(server, "ChooseServer", steady).Activated:Connect(function()
		self.ServerPressed:Fire()
	end)

	-- Status strip above Enter (deploy status, invites sent, maintenance).
	local statusCfg = cfg.status
	self.status, self.statusText = tag(statusCfg.text, {
		Name = "Status",
		AnchorPoint = Vector2.new(statusCfg.anchor[1], statusCfg.anchor[2]),
		Position = UDim2.new(statusCfg.pos[1], statusCfg.pos[2], statusCfg.pos[3], statusCfg.pos[4]),
		Size = UDim2.fromOffset(statusCfg.size[1], statusCfg.size[2]),
		Visible = false,
		ZIndex = 6,
	}, self.root)
	self.statusText.TextWrapped = true
	return self
end

-- Fits the screen to `width` × `height` reference pixels: on short screens the
-- navigation grid shrinks to end above the bottom edge, and the party panel to
-- end above the Enter group under it. Neither goes below half size.
function LobbyHud:Fit(width: number, height: number)
	local navCfg, partyCfg = self.cfg.nav, self.cfg.party
	local navRoom = height - navCfg.bottomMargin - navCfg.pos[4]
	self.navScale.Scale = math.clamp(navRoom / self.navHeight, 0.5, 1)
	local below = if width < NARROW_WIDTH
		then self.cfg.enter.size[2] - self.cfg.enter.pos[4]
		else self.cfg.server.size[2] - self.cfg.server.pos[4]
	local partyRoom = height - below - 10 - partyCfg.pos[4]
	self.partyScale.Scale = math.clamp(partyRoom / partyCfg.size[2], 0.5, 1)
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
			BackgroundColor3 = Layout.Color("line"),
			BorderSizePixel = 0,
			ZIndex = 5,
		}),
		row
	)
	return row :: Frame
end

local function spriteButton(name: string, entry, parent: Instance, steady, onPress)
	local frame = Widgets.Make("Frame", rect(entry, { Name = name, BackgroundTransparency = 1, ZIndex = 6 }), parent)
	Widgets.Sprite(entry.sprite, { Size = UDim2.fromScale(1, 1), ZIndex = 6 }, frame)
	hit(frame, name .. "Button", steady).Activated:Connect(onPress)
	return frame
end

-- members: {{userId, name, leader, thumbnail?}}; invites: {{partyId, from}};
-- canInvite: the leader's row offers Invite; inParty: show Leave. Free places up
-- to `maxSize` show as empty slots.
function LobbyHud:SetParty(members, invites, maxSize: number, canInvite: boolean, inParty: boolean)
	local cfg = self.cfg.party
	self.partyTitle.Text = HudModel.PartyTitle(#members, maxSize)
	self.leave.Visible = inParty
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
		Widgets.Make("UIStroke", { Color = Layout.Color("paperEdge"), Thickness = 1.5 }, headshot)
		inkText(memberCfg.name, rect(memberCfg.name, { Name = "MemberName", Text = member.name, ZIndex = 6 }), row)
		if member.leader then
			Widgets.Sprite(memberCfg.crown.sprite, rect(memberCfg.crown, { Name = "Leader", ZIndex = 6 }), row)
			if canInvite then
				spriteButton("InviteFriends", memberCfg.invite, row, self.steady, function()
					self.InvitePressed:Fire()
				end)
			end
		end
	end
	local inviteCfg = cfg.invite
	for _, invite in invites do
		order += 1
		local row = self:_row(order, inviteCfg)
		inkText(
			inviteCfg.text,
			rect(inviteCfg.text, {
				Name = "From",
				Text = "Invite from " .. invite.from,
				ZIndex = 6,
			}),
			row
		)
		spriteButton("Accept", inviteCfg.accept, row, self.steady, function()
			self.InviteAnswered:Fire(invite.partyId, true)
		end)
		spriteButton("Decline", inviteCfg.decline, row, self.steady, function()
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

-- Shows `text` in the status strip above Enter (status and errors), or hides the
-- strip when `text` is nil. The server dropdown always reads "Choose server".
function LobbyHud:SetServerLine(text: string?)
	self.statusText.Text = text or ""
	self.status.Visible = text ~= nil and text ~= ""
end

function LobbyHud:SetEnterBusy(busy: boolean)
	self.enterShade.Visible = busy
	self.enterButton.Active = not busy
end

return LobbyHud
