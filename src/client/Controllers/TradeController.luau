-- Lobby trading (GDD §10.2, §25.4). Y (or ButtonL1) opens the trade panel: pick a
-- player in this lobby to invite. The trade window shows both offers, your
-- tradeable lobby-backpack items to add or remove, a Gem amount (never Coins), a
-- lock, a countdown and confirm. Any change unlocks both sides. Lobby only.

local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)

local TradeController = {}

local player = Players.LocalPlayer
local ui = {}
local session = nil
local inviteId = nil

local TEXT = Color3.fromRGB(235, 226, 212)
local GOLD = Color3.fromRGB(255, 214, 150)

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

local function invoke(name: string, ...)
	local ok, success, reason = pcall(Remotes.Get(name).InvokeServer, Remotes.Get(name), ...)
	if not ok then
		return false, "Request failed"
	end
	return success, reason
end

local function clear()
	for _, child in ui.list:GetChildren() do
		if not child:IsA("UIListLayout") then
			child:Destroy()
		end
	end
end

local order = 0
local function nextOrder()
	order += 1
	return order
end

local function line(text: string, color: Color3?)
	make("TextLabel", {
		Text = text,
		Size = UDim2.new(1, -8, 0, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextWrapped = true,
		TextColor3 = color or TEXT,
		Font = Enum.Font.GothamMedium,
		TextSize = 13,
		LayoutOrder = nextOrder(),
	}, ui.list)
end

local function button(text: string, enabled: boolean, onClick)
	local b = make("TextButton", {
		Text = text,
		Size = UDim2.new(1, -8, 0, 28),
		BackgroundColor3 = if enabled then Color3.fromRGB(110, 70, 30) else Color3.fromRGB(50, 44, 38),
		TextColor3 = if enabled then Color3.fromRGB(255, 240, 220) else Color3.fromRGB(140, 130, 120),
		AutoButtonColor = enabled,
		Font = Enum.Font.GothamBold,
		TextSize = 13,
		LayoutOrder = nextOrder(),
	}, ui.list)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
	if enabled then
		b.Activated:Connect(onClick)
	end
end

local render

local function myKeys()
	local keys = {}
	for _, item in session.mine.items do
		table.insert(keys, item.key)
	end
	return keys
end

local function sendOffer(keys, gems: number)
	local ok, reason = invoke("TradeOffer", session.id, keys, gems)
	if not ok then
		ui.status.Text = "Offer refused: " .. tostring(reason)
	end
end

local function describe(offer): string
	local parts = {}
	for _, item in offer.items do
		table.insert(parts, item.name .. (item.quantity and (" ×" .. item.quantity) or ""))
	end
	if offer.gems > 0 then
		table.insert(parts, offer.gems .. " Gems")
	end
	return if #parts > 0 then table.concat(parts, ", ") else "nothing yet"
end

function render()
	clear()
	order = 0
	ui.gems.Visible = session ~= nil
	if session == nil then
		line("Invite a player in this lobby to trade items and Gems (Coins can't be traded).", TEXT)
		for _, other in Players:GetPlayers() do
			if other ~= player then
				button("Invite " .. other.DisplayName, true, function()
					local ok, reason = invoke("TradeRequest", other.UserId)
					ui.status.Text = if ok then "Invite sent." else ("Couldn't invite: " .. tostring(reason))
				end)
			end
		end
		return
	end
	line(("Trading with %s"):format(session.partner), GOLD)
	line("You give: " .. describe(session.mine), TEXT)
	line("You get: " .. describe(session.theirs), TEXT)
	line(
		("Locks — you: %s · them: %s"):format(
			session.locked.mine and "locked" or "open",
			session.locked.theirs and "locked" or "open"
		),
		TEXT
	)
	-- Tradeable items come from the lobby backpack view the vault panel uses.
	local view = invoke("VaultSnapshot")
	if type(view) == "table" then
		line("Your tradeable lobby-backpack items (tap to add or remove):", GOLD)
		local offered = myKeys()
		for _, item in view.backpack do
			local key = item.key
			if key and item.tradeable then
				local inOffer = table.find(offered, key) ~= nil
				local label = (inOffer and "✓ " or "+ ")
					.. item.name
					.. (item.quantity and (" ×" .. item.quantity) or "")
				button(label, true, function()
					local keys = myKeys()
					local index = table.find(keys, key)
					if index then
						table.remove(keys, index)
					else
						table.insert(keys, key)
					end
					sendOffer(keys, session.mine.gems)
				end)
			end
		end
	end
	local now = workspace:GetServerTimeNow()
	if session.confirmAt and now < session.confirmAt then
		line(("Both locked — confirm unlocks in %d s"):format(math.ceil(session.confirmAt - now)), GOLD)
	end
	button("Lock offer", not session.locked.mine, function()
		invoke("TradeLock", session.id)
	end)
	button(
		"Confirm trade",
		session.confirmAt ~= nil and now >= session.confirmAt and not session.confirmed.mine,
		function()
			local ok, reason = invoke("TradeConfirm", session.id)
			if not ok then
				ui.status.Text = "Not yet: " .. tostring(reason)
			end
		end
	)
	button("Cancel trade", true, function()
		invoke("TradeCancel", session.id)
	end)
end

local function build()
	local gui = make("ScreenGui", { Name = "Trade", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	ui.panel = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.55, 0.5),
		Size = UDim2.new(0.4, 0, 0.7, 0),
		BackgroundColor3 = Color3.fromRGB(24, 20, 17),
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.panel)
	make("UISizeConstraint", { MaxSize = Vector2.new(500, 600), MinSize = Vector2.new(300, 300) }, ui.panel)
	local close = make("TextButton", {
		Text = "✕",
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.new(1, -6, 0, 6),
		Size = UDim2.fromOffset(28, 24),
		BackgroundColor3 = Color3.fromRGB(70, 56, 40),
		TextColor3 = Color3.fromRGB(245, 236, 222),
		Font = Enum.Font.GothamBold,
		TextSize = 14,
	}, ui.panel)
	close.Activated:Connect(function()
		ui.panel.Visible = false
	end)
	ui.gems = make("TextBox", {
		PlaceholderText = "Gems to offer",
		Text = "",
		Position = UDim2.fromOffset(10, 6),
		Size = UDim2.fromOffset(160, 24),
		BackgroundColor3 = Color3.fromRGB(40, 34, 28),
		TextColor3 = TEXT,
		Font = Enum.Font.Gotham,
		TextSize = 13,
		ClearTextOnFocus = false,
		Visible = false,
	}, ui.panel)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, ui.gems)
	ui.gems.FocusLost:Connect(function()
		local gems = tonumber(ui.gems.Text)
		if session and gems and gems >= 0 and gems % 1 == 0 then
			sendOffer(myKeys(), gems)
		end
	end)
	ui.list = make("ScrollingFrame", {
		Position = UDim2.fromOffset(10, 36),
		Size = UDim2.new(1, -20, 1, -68),
		BackgroundTransparency = 1,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		CanvasSize = UDim2.new(),
		ScrollBarThickness = 6,
	}, ui.panel)
	make("UIListLayout", { Padding = UDim.new(0, 4), SortOrder = Enum.SortOrder.LayoutOrder }, ui.list)
	ui.status = make("TextLabel", {
		Text = "",
		AnchorPoint = Vector2.new(0, 1),
		Position = UDim2.new(0, 10, 1, -6),
		Size = UDim2.new(1, -20, 0, 22),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = TEXT,
		Font = Enum.Font.Gotham,
		TextSize = 13,
	}, ui.panel)

	ui.invite = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0),
		Position = UDim2.new(0.5, 0, 0, 60),
		Size = UDim2.fromOffset(380, 70),
		BackgroundColor3 = Color3.fromRGB(30, 26, 20),
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.invite)
	ui.inviteText = make("TextLabel", {
		Position = UDim2.fromOffset(10, 4),
		Size = UDim2.new(1, -20, 0, 26),
		BackgroundTransparency = 1,
		TextColor3 = GOLD,
		Font = Enum.Font.GothamBold,
		TextSize = 14,
	}, ui.invite)
	for index, choice in { { "Accept", true }, { "Decline", false } } do
		local b = make("TextButton", {
			Text = choice[1],
			Position = UDim2.new((index - 1) * 0.5, 10, 0, 34),
			Size = UDim2.new(0.5, -20, 0, 28),
			BackgroundColor3 = Color3.fromRGB(110, 70, 30),
			TextColor3 = Color3.fromRGB(255, 240, 220),
			Font = Enum.Font.GothamBold,
			TextSize = 13,
		}, ui.invite)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
		b.Activated:Connect(function()
			ui.invite.Visible = false
			if inviteId then
				invoke("TradeRespond", inviteId, choice[2])
				inviteId = nil
			end
		end)
	end
end

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function TradeController.Toggle()
	ui.panel.Visible = not ui.panel.Visible
	if ui.panel.Visible then
		render()
	end
end

function TradeController.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	build()
	Remotes.Get("TradeChanged").OnClientEvent:Connect(function(payload)
		if payload.kind == "Invite" then
			inviteId = payload.id
			ui.inviteText.Text = payload.from .. " wants to trade with you"
			ui.invite.Visible = true
		elseif payload.kind == "Session" then
			session = payload
			ui.panel.Visible = true
			render()
		elseif payload.kind == "Closed" then
			session = nil
			ui.invite.Visible = false
			ui.status.Text = "Trade " .. string.lower(payload.reason) .. "."
			if ui.panel.Visible then
				render()
			end
		end
	end)
	ContextActionService:BindAction("FlintbornTrade", function(_, state)
		if state == Enum.UserInputState.Begin then
			TradeController.Toggle()
		end
		return Enum.ContextActionResult.Pass
	end, false, Enum.KeyCode.Y, Enum.KeyCode.ButtonL1)
	-- The confirm countdown ticks while the window is open.
	task.spawn(function()
		while true do
			task.wait(1)
			if session and session.confirmAt and ui.panel.Visible then
				render()
			end
		end
	end)
end

return TradeController
