-- The lobby screen (art/reference/ui/lobby_master.png), drawn from the "lobby"
-- section of HudLayout.json with the UI art sheets' sprites: the profile panel
-- (headshot, name, level and XP), the navigation buttons, the currency bar, the
-- party panel, the Enter button with its server line, and the settings gear.
-- Display only: LobbyHudController feeds it and handles the signals.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local Layout = require(script.Parent.Layout)
local Widgets = require(script.Parent.Widgets)

local LobbyHud = {}
LobbyHud.__index = LobbyHud

local HOVER = TweenInfo.new(0.12, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)

local function rect(entry, props)
	props = props or {}
	props.Position = Layout.Position(entry.rect)
	props.Size = Layout.Size(entry.rect)
	return props
end

-- A transparent button over `parent` (or at `entry.rect`) that grows slightly on
-- hover and press, unless `steady` says motion is reduced.
local function hit(parent: Instance, props, steady: () -> boolean)
	local button = Widgets.Make("TextButton", {
		Name = "Hit",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		ZIndex = 8,
	}, parent)
	for key, value in props or {} do
		(button :: any)[key] = value
	end
	local scale = Widgets.Make("UIScale", { Scale = 1 }, parent)
	local function to(value: number)
		if steady() then
			scale.Scale = 1
			return
		end
		TweenService:Create(scale, HOVER, { Scale = value }):Play()
	end
	button.MouseEnter:Connect(function()
		to(1.04)
	end)
	button.MouseLeave:Connect(function()
		to(1)
	end)
	button.SelectionGained:Connect(function()
		to(1.04)
	end)
	button.SelectionLost:Connect(function()
		to(1)
	end)
	button.MouseButton1Down:Connect(function()
		to(0.97)
	end)
	button.MouseButton1Up:Connect(function()
		to(1.04)
	end)
	return button
end

local function rounded(color: Color3, radius: number, props, parent: Instance)
	local frame = Widgets.Make("Frame", { BackgroundColor3 = color, BorderSizePixel = 0 }, parent)
	for key, value in props do
		(frame :: any)[key] = value
	end
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0, radius) }, frame)
	return frame
end

function LobbyHud.new(parent: Instance, layout, steady: () -> boolean)
	local cfg = layout.lobby
	local colors = cfg.colors
	local function color(key: string): Color3
		return Color3.fromHex(colors[key])
	end
	local self = setmetatable({
		cfg = cfg,
		color = color,
		steady = steady,
		NavPressed = Signal.new(),
		ProfilePressed = Signal.new(),
		SettingsPressed = Signal.new(),
		EnterPressed = Signal.new(),
		ServerPressed = Signal.new(),
		InvitePressed = Signal.new(),
		LeavePressed = Signal.new(),
		InviteAnswered = Signal.new(), -- (partyId, accept)
		thumbnails = {},
	}, LobbyHud)
	self.root = Widgets.Make("Frame", {
		Name = "Lobby",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
	}, parent)

	-- Profile: headshot, name, "LV. n" and the XP bar. Opens Progress.
	local profileCfg = cfg.profile
	local profile = Widgets.Panel(profileCfg, {
		Name = "Profile",
		Size = UDim2.fromOffset(profileCfg.size[1], profileCfg.size[2]),
	}, self.root)
	Layout.Place(profile, profileCfg)
	self.avatar = Widgets.Make(
		"ImageLabel",
		rect(profileCfg.avatar, {
			Name = "Headshot",
			BackgroundColor3 = color("row"),
			ScaleType = Enum.ScaleType.Crop,
			ZIndex = 4,
		}),
		profile
	)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 8) }, self.avatar)
	Widgets.Make("UIStroke", { Color = color("rowStroke"), Thickness = 2 }, self.avatar)
	self.nameText = Widgets.Text(profileCfg.name, rect(profileCfg.name, { Name = "PlayerName" }), profile)
	self.levelText = Widgets.Text(profileCfg.level, rect(profileCfg.level, { Name = "Level", Text = "LV." }), profile)
	self.xpBar = Widgets.Bar({
		rect = profileCfg.xp.rect,
		inset = profileCfg.xp.inset,
		track = profileCfg.xp.track,
		fillColor = profileCfg.xp.fillColor,
	}, profile)
	Widgets.SetBar(self.xpBar, 0, true) -- empty until the first progression snapshot
	hit(profile, { Name = "OpenProgress" }, steady).Activated:Connect(function()
		self.ProfilePressed:Fire()
	end)

	-- Navigation buttons: rope-framed squares with an icon and a label.
	local navCfg = cfg.nav
	local nav = Widgets.Make("Frame", {
		Name = "Navigation",
		BackgroundTransparency = 1,
	}, self.root)
	self.navHeight = navCfg.pitch * (#navCfg.buttons - 1) + navCfg.button[2]
	Layout.Place(nav, {
		anchor = navCfg.anchor,
		pos = navCfg.pos,
		size = { navCfg.button[1], self.navHeight },
	})
	-- Shrinks the column on short screens so it ends above the settings gear (Fit).
	self.navScale = Widgets.Make("UIScale", { Scale = 1 }, nav)
	for index, entry in navCfg.buttons do
		local slot = Widgets.Make("Frame", {
			Name = entry.id,
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(0, (index - 1) * navCfg.pitch),
			Size = UDim2.fromOffset(navCfg.button[1], navCfg.button[2]),
		}, nav)
		local slotRect = { 0, 0, navCfg.button[1], navCfg.button[2] }
		local frame = Widgets.Frame(navCfg.frame, slotRect, slot, navCfg.sliceScale, { 0, 0, 0, 0 })
		frame.ZIndex = 2
		Widgets.Sprite(entry.icon, rect(navCfg.icon, { Name = "Icon", ZIndex = 4 }), slot)
		local labelProps = rect(navCfg.label, {
			Name = "Label",
			Text = entry.label,
			TextXAlignment = Enum.TextXAlignment.Center,
			TextStrokeTransparency = 0.4,
		})
		Widgets.Text(navCfg.label, labelProps, slot)
		hit(slot, { Name = "Open" .. entry.id }, steady).Activated:Connect(function()
			self.NavPressed:Fire(entry.id)
		end)
	end

	-- Currency bar: Coins and Gems.
	local currencyCfg = cfg.currency
	local currency = Widgets.Panel(currencyCfg, {
		Name = "Currency",
		Size = UDim2.fromOffset(currencyCfg.size[1], currencyCfg.size[2]),
	}, self.root)
	Layout.Place(currency, currencyCfg)
	Widgets.Sprite(currencyCfg.coinIcon.icon, rect(currencyCfg.coinIcon, { Name = "CoinIcon", ZIndex = 4 }), currency)
	self.coinsText = Widgets.Text(currencyCfg.coins, rect(currencyCfg.coins, { Name = "Coins", Text = "0" }), currency)
	Widgets.Sprite(currencyCfg.gemIcon.icon, rect(currencyCfg.gemIcon, { Name = "GemIcon", ZIndex = 4 }), currency)
	self.gemsText = Widgets.Text(currencyCfg.gems, rect(currencyCfg.gems, { Name = "Gems", Text = "0" }), currency)

	-- Party panel: header, then a scrolling list of rows.
	local partyCfg = cfg.party
	local party = Widgets.Panel(partyCfg, {
		Name = "Party",
		Size = UDim2.fromOffset(partyCfg.size[1], partyCfg.size[2]),
	}, self.root)
	Layout.Place(party, partyCfg)
	local partyIcon = Widgets.Sprite(partyCfg.icon.icon, rect(partyCfg.icon, { Name = "Icon", ZIndex = 4 }), party)
	if partyCfg.icon.tint and partyIcon:IsA("ImageLabel") then
		partyIcon.ImageColor3 = Layout.Color(partyCfg.icon.tint)
	end
	self.partyTitle = Widgets.Text(partyCfg.title, rect(partyCfg.title, { Name = "Title", Text = "PARTY" }), party)
	Widgets.Make(
		"Frame",
		rect(partyCfg.divider, {
			Name = "Divider",
			BackgroundColor3 = Color3.new(1, 1, 1),
			BackgroundTransparency = partyCfg.divider.transparency,
			BorderSizePixel = 0,
			ZIndex = 4,
		}),
		party
	)
	-- Leave: a small exit button at the header's right while you are in a party.
	self.leave = Widgets.Make("Frame", {
		Name = "Leave",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(partyCfg.size[1] - 46, 14),
		Size = UDim2.fromOffset(26, 26),
		Visible = false,
		ZIndex = 4,
	}, party)
	Widgets.Sprite("icon_exit", { Size = UDim2.fromScale(1, 1), ZIndex = 5 }, self.leave)
	hit(self.leave, { Name = "LeaveParty" }, steady).Activated:Connect(function()
		self.LeavePressed:Fire()
	end)
	self.list = Widgets.Make(
		"ScrollingFrame",
		rect(partyCfg.list, {
			Name = "List",
			BackgroundTransparency = 1,
			BorderSizePixel = 0,
			CanvasSize = UDim2.new(),
			AutomaticCanvasSize = Enum.AutomaticSize.Y,
			ScrollBarThickness = partyCfg.list.scrollBar,
			ScrollBarImageColor3 = color("scroll"),
			ScrollingDirection = Enum.ScrollingDirection.Y,
			ZIndex = 4,
		}),
		party
	)
	Widgets.Make("UIListLayout", {
		Padding = UDim.new(0, partyCfg.list.rowGap),
		SortOrder = Enum.SortOrder.LayoutOrder,
	}, self.list)

	-- Enter button with its server line underneath.
	local enterCfg = cfg.enter
	local enter = Widgets.Panel(enterCfg, {
		Name = "Enter",
		Size = UDim2.fromOffset(enterCfg.size[1], enterCfg.size[2]),
	}, self.root)
	Layout.Place(enter, enterCfg)
	Widgets.Sprite(enterCfg.icon.icon, rect(enterCfg.icon, { Name = "Icon", ZIndex = 4 }), enter)
	local function goldText(entry, name: string)
		local props = rect(entry, {
			Name = name,
			Text = entry.text,
			TextColor3 = Color3.new(1, 1, 1),
			TextXAlignment = Enum.TextXAlignment.Center,
			TextStrokeTransparency = 1,
			TextTruncate = Enum.TextTruncate.None,
			ZIndex = 5,
		})
		local label = Widgets.Text(entry, props, enter)
		Widgets.Make("UIGradient", {
			Rotation = 90,
			Color = ColorSequence.new(color("ctaTop"), color("ctaBottom")),
		}, label)
		Widgets.Make("UIStroke", { Color = color("ctaStroke"), Thickness = 2.5 }, label)
		return label
	end
	self.enterTitle = goldText(enterCfg.title, "Title")
	self.enterSubtitle = goldText(enterCfg.subtitle, "Subtitle")
	self.enterShade = Widgets.Make("Frame", {
		Name = "Busy",
		BackgroundColor3 = Color3.new(0, 0, 0),
		BackgroundTransparency = 0.45,
		BorderSizePixel = 0,
		Position = UDim2.fromOffset(6, 6),
		Size = UDim2.new(1, -12, 1, -12),
		Visible = false,
		ZIndex = 7,
	}, enter)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 8) }, self.enterShade)
	self.enterButton = hit(enter, { Name = "EnterWorld" }, steady)
	self.enterButton.Activated:Connect(function()
		self.EnterPressed:Fire()
	end)

	local serverCfg = enterCfg.server
	local server = Widgets.Make("TextButton", {
		Name = "Server",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(serverCfg.rect[1], serverCfg.rect[2]),
		Size = UDim2.fromOffset(serverCfg.rect[3], serverCfg.rect[4]),
		ZIndex = 5,
	}, enter)
	Widgets.Make("UIListLayout", {
		FillDirection = Enum.FillDirection.Horizontal,
		HorizontalAlignment = Enum.HorizontalAlignment.Center,
		VerticalAlignment = Enum.VerticalAlignment.Center,
		Padding = UDim.new(0, 8),
		SortOrder = Enum.SortOrder.LayoutOrder,
	}, server)
	self.serverText = Widgets.Text(serverCfg, {
		Name = "Label",
		Text = serverCfg.text,
		AutomaticSize = Enum.AutomaticSize.X,
		Size = UDim2.fromOffset(0, serverCfg.rect[4]),
		TextTruncate = Enum.TextTruncate.None,
		TextStrokeTransparency = 0.3,
		LayoutOrder = 1,
	}, server)
	self.chevron = Widgets.Sprite(enterCfg.chevron.icon, {
		Name = "Chevron",
		Size = UDim2.fromOffset(enterCfg.chevron.size, enterCfg.chevron.size),
		LayoutOrder = 2,
		ZIndex = 5,
	}, server)
	server.Activated:Connect(function()
		self.ServerPressed:Fire()
	end)

	-- Settings gear.
	local settingsCfg = cfg.settings
	local settings = Widgets.Make("Frame", { Name = "Settings", BackgroundTransparency = 1 }, self.root)
	Layout.Place(settings, settingsCfg)
	local gearRect = { 0, 0, settingsCfg.size[1], settingsCfg.size[2] }
	local gearFrame = Widgets.Frame(settingsCfg.frame, gearRect, settings, settingsCfg.sliceScale, { 0, 0, 0, 0 })
	gearFrame.ZIndex = 2
	Widgets.Sprite(settingsCfg.icon.icon, rect(settingsCfg.icon, { Name = "Icon", ZIndex = 4 }), settings)
	hit(settings, { Name = "OpenSettings" }, steady).Activated:Connect(function()
		self.SettingsPressed:Fire()
	end)
	return self
end

-- Fits the navigation column between its top and the settings gear on a screen
-- `height` reference pixels tall (short phone screens), never below half size.
function LobbyHud:Fit(height: number)
	local navCfg, gear = self.cfg.nav, self.cfg.settings
	local available = height + gear.pos[4] - gear.size[2] - 12 - navCfg.pos[4]
	self.navScale.Scale = math.clamp(available / self.navHeight, 0.5, 1)
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

function LobbyHud:_row(order: number)
	local cfg = self.cfg.party
	local row = rounded(self.color("row"), cfg.row.radius, {
		Name = "Row" .. order,
		LayoutOrder = order,
		Size = UDim2.fromOffset(cfg.row.width, cfg.list.rowHeight),
		ZIndex = 4,
	}, self.list)
	Widgets.Make("UIStroke", {
		Color = self.color("rowStroke"),
		Thickness = 1.5,
		Transparency = cfg.row.strokeTransparency,
	}, row)
	return row
end

local function iconButton(name: string, sprite: string, rectValue, parent: Instance, steady, onPress)
	local holder = Widgets.Make("Frame", {
		Name = name,
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(rectValue[1], rectValue[2]),
		Size = UDim2.fromOffset(rectValue[3], rectValue[4]),
		ZIndex = 5,
	}, parent)
	Widgets.Sprite(sprite, { Size = UDim2.fromScale(1, 1), ZIndex = 6 }, holder)
	hit(holder, { Name = name .. "Button" }, steady).Activated:Connect(onPress)
	return holder
end

-- members: {{userId, name, leader, thumbnail?}}; invites: {{partyId, from}};
-- canInvite: show the Invite Friends row; inParty: show Leave.
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
	for _, member in members do
		order += 1
		local row = self:_row(order)
		local headshot = Widgets.Make(
			"ImageLabel",
			rect(cfg.headshot, {
				Name = "Headshot",
				BackgroundColor3 = Color3.new(0.12, 0.12, 0.12),
				Image = member.thumbnail or "",
				ScaleType = Enum.ScaleType.Crop,
				ZIndex = 5,
			}),
			row
		)
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 6) }, headshot)
		local dot = rounded(self.color("online"), cfg.dot.size, {
			Name = "Online",
			AnchorPoint = Vector2.new(0.5, 0.5),
			Position = UDim2.fromOffset(cfg.dot.centre[1], cfg.dot.centre[2]),
			Size = UDim2.fromOffset(cfg.dot.size, cfg.dot.size),
			ZIndex = 6,
		}, row)
		Widgets.Make("UIStroke", { Color = Color3.new(0, 0, 0), Thickness = 1 }, dot)
		Widgets.Text(cfg.memberName, rect(cfg.memberName, { Name = "MemberName", Text = member.name }), row)
		if member.leader then
			Widgets.Sprite(cfg.crown.icon, rect(cfg.crown, { Name = "Leader", ZIndex = 5 }), row)
		end
	end
	for _, invite in invites do
		order += 1
		local row = self:_row(order)
		Widgets.Sprite(cfg.inviteIcon.icon, rect(cfg.inviteIcon, { Name = "Icon", ZIndex = 5 }), row)
		Widgets.Text(cfg.memberName, {
			Name = "From",
			Text = "From " .. invite.from,
			Position = UDim2.fromOffset(cfg.invite.rect[1], cfg.invite.rect[2]),
			Size = UDim2.fromOffset(cfg.invite.rect[3] - 60, cfg.invite.rect[4]),
			TextSize = 14,
		}, row)
		iconButton("Accept", "icon_check", { cfg.row.width - 62, 12, 24, 24 }, row, self.steady, function()
			self.InviteAnswered:Fire(invite.partyId, true)
		end)
		iconButton("Decline", "icon_x", { cfg.row.width - 32, 12, 24, 24 }, row, self.steady, function()
			self.InviteAnswered:Fire(invite.partyId, false)
		end)
	end
	if canInvite then
		order += 1
		local row = self:_row(order)
		Widgets.Sprite(cfg.inviteIcon.icon, rect(cfg.inviteIcon, { Name = "Icon", ZIndex = 5 }), row)
		Widgets.Text(cfg.invite, rect(cfg.invite, { Name = "Label", Text = cfg.invite.text }), row)
		hit(row, { Name = "InviteFriends" }, self.steady).Activated:Connect(function()
			self.InvitePressed:Fire()
		end)
	end
end

-- Shows `text` on the server line (status and errors), or the "Choose server"
-- label again when `text` is nil.
function LobbyHud:SetServerLine(text: string?)
	self.serverText.Text = text or self.cfg.enter.server.text
	self.chevron.Visible = text == nil
end

function LobbyHud:SetEnterBusy(busy: boolean)
	self.enterShade.Visible = busy
	self.enterButton.Active = not busy
end

return LobbyHud
