-- Tribe panel (GDD §5.2, Q39): create a tribe, invite nearby players, accept
-- invites, kick (leader), leave, and propose alliances. Toggle with the Tribe key (T by default) or the
-- Tribe button. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Binds = require(script.Parent.Parent.Ui.Binds)

local TribeController = {}

local player = Players.LocalPlayer
local view = { tribe = nil, invites = {}, others = {} }
local ui = {}

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

local function label(text: string)
	return make("TextLabel", {
		Text = text,
		Size = UDim2.new(1, 0, 0, 20),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = Color3.fromRGB(240, 232, 220),
		Font = Enum.Font.Gotham,
		TextSize = 13,
	}, ui.list)
end

local function action(text: string, name: string, argument)
	local b = make("TextButton", {
		Text = text,
		Size = UDim2.new(1, 0, 0, 28),
		BackgroundColor3 = Color3.fromRGB(92, 64, 40),
		TextColor3 = Color3.fromRGB(245, 236, 222),
		Font = Enum.Font.GothamBold,
		TextSize = 13,
	}, ui.list)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
	b.Activated:Connect(function()
		local ok, success, reason = pcall(function()
			return Remotes.Get("TribeAction"):InvokeServer(name, argument)
		end)
		ui.status.Text = if ok and success then tostring(reason or "Done") else ("Failed: " .. tostring(reason))
	end)
end

local function render()
	for _, child in ui.list:GetChildren() do
		if not child:IsA("UIListLayout") then
			child:Destroy()
		end
	end
	local tribe = view.tribe
	if tribe then
		label(("Your tribe (%d/8)"):format(#tribe.members))
		local leading = tribe.leader == player.UserId
		for _, member in tribe.members do
			label((member.userId == tribe.leader and "★ " or "• ") .. member.name)
			if leading and member.userId ~= player.UserId then
				action("Kick " .. member.name, "kick", member.userId)
			end
		end
		if #tribe.allies > 0 then
			label(("Allied with %d tribe(s)"):format(#tribe.allies))
		end
		action("Leave tribe", "leave")
		if leading then
			for _, other in Players:GetPlayers() do
				if other ~= player and other:GetAttribute("TribeId") == nil then
					action("Invite " .. other.DisplayName, "invite", other.UserId)
				end
			end
			for _, other in view.others do
				action(("Propose alliance: %s's tribe (%d)"):format(other.leader, other.size), "ally", other.tribeId)
			end
		end
	else
		label("You are not in a tribe.")
		action("Create tribe", "create")
	end
	for _, invite in view.invites do
		action("Join " .. invite.from .. "'s tribe", "accept", invite.tribeId)
	end
end

local function build()
	local gui = make("ScreenGui", { Name = "Tribe", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	ui.panel = make("Frame", {
		AnchorPoint = Vector2.new(0, 0.5),
		Position = UDim2.new(0, 16, 0.5, 0),
		Size = UDim2.new(0, 280, 1, -24),
		BackgroundColor3 = Color3.fromRGB(24, 20, 17),
		BackgroundTransparency = 0.05,
		Active = true,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.panel)
	make("UISizeConstraint", { MaxSize = Vector2.new(280, 360) }, ui.panel)
	make("UIPadding", {
		PaddingTop = UDim.new(0, 8),
		PaddingLeft = UDim.new(0, 8),
		PaddingRight = UDim.new(0, 8),
	}, ui.panel)
	local close = make("TextButton", {
		Text = "✕",
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.fromScale(1, 0),
		Size = UDim2.fromOffset(28, 24),
		BackgroundColor3 = Color3.fromRGB(70, 56, 40),
		TextColor3 = Color3.fromRGB(245, 236, 222),
		Font = Enum.Font.GothamBold,
		TextSize = 14,
	}, ui.panel)
	close.Activated:Connect(function()
		ui.panel.Visible = false
	end)
	ui.status = make("TextLabel", {
		Size = UDim2.new(1, -34, 0, 20),
		BackgroundTransparency = 1,
		TextColor3 = Color3.fromRGB(255, 220, 170),
		Font = Enum.Font.GothamMedium,
		TextSize = 13,
		Text = "Tribes: up to 8. No friendly fire.",
	}, ui.panel)
	ui.list = make("ScrollingFrame", {
		Position = UDim2.fromOffset(0, 26),
		Size = UDim2.new(1, 0, 1, -34),
		BackgroundTransparency = 1,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		CanvasSize = UDim2.new(),
		ScrollBarThickness = 6,
	}, ui.panel)
	make("UIListLayout", { Padding = UDim.new(0, 4) }, ui.list)
end

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function TribeController.Toggle()
	ui.panel.Visible = not ui.panel.Visible
	render()
end

function TribeController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	Remotes.Get("TribeChanged").OnClientEvent:Connect(function(snapshot)
		view = snapshot
		render()
	end)
	Binds.Bind("Tribe", function(_, state)
		if state == Enum.UserInputState.Begin then
			TribeController.Toggle()
		end
		return Enum.ContextActionResult.Sink
	end)
	render()
end

return TribeController
