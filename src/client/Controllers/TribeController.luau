-- Tribe panel (GDD §5.2, Q39): create a tribe, invite nearby players, accept
-- invites, kick (leader), leave, and propose alliances. Toggle with the Tribe key
-- (T by default) or the Tribe button. A kit window: members and nearby players
-- as player rows, alliances and invites as list rows, each with its action.
-- World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Kit = require(script.Parent.Parent.Hud.Kit)
local Binds = require(script.Parent.Parent.Ui.Binds)

local TribeController = {}

TribeController.SIZE = { 720, 640 }
TribeController.MAX_MEMBERS = 8

local ROW_H = 58
local HEADER_H = 40
local BUTTON_H = 50

local player = Players.LocalPlayer
local view = { tribe = nil, invites = {}, others = {} }
local ui = {}

local function act(name: string, argument)
	local ok, success, reason = pcall(function()
		return Remotes.Get("TribeAction"):InvokeServer(name, argument)
	end)
	ui.status:SetText(if ok and success then tostring(reason or "Done") else ("Failed: " .. tostring(reason)))
end

-- The list is rebuilt from the view: each part is added in order with its height.
local function add(part, height: number)
	table.insert(ui.parts, part)
	ui.height += height + 6
end

local function header(text: string, icon: string)
	add(
		Kit.SectionHeader.new(ui.list, {
			name = "Header" .. #ui.parts,
			size = { ui.listW, HEADER_H },
			layoutOrder = #ui.parts + 1,
			text = text,
			icon = icon,
		}),
		HEADER_H
	)
end

local function line(text: string)
	local holder = Kit.Core.Make("Frame", {
		Name = "Line" .. #ui.parts,
		BackgroundTransparency = 1,
		LayoutOrder = #ui.parts + 1,
		Size = UDim2.fromOffset(ui.listW, 30),
	}, ui.list)
	Kit.Text.new(holder, { name = "Text", rect = { 8, 0, ui.listW - 8, 30 }, text = text, role = "bodySoft" })
	add(holder, 30)
end

local function person(userId: number, name: string, leader: boolean, action)
	local other = Players:GetPlayerByUserId(userId)
	local level = other and other:GetAttribute("Level")
	add(
		-- `name` is the player's name (it also names the row).
		Kit.PlayerRow.new(ui.list, {
			size = { ui.listW, ROW_H },
			layoutOrder = #ui.parts + 1,
			userId = userId,
			name = name,
			level = if type(level) == "number" then level else nil,
			leader = leader,
			action = action,
		}),
		ROW_H
	)
end

local function choice(icon: string, title: string, label: string, onPress)
	local holder = Kit.Core.Make("Frame", {
		Name = "Choice" .. #ui.parts,
		BackgroundTransparency = 1,
		LayoutOrder = #ui.parts + 1,
		Size = UDim2.fromOffset(ui.listW, ROW_H),
	}, ui.list)
	Kit.ListRow.new(
		holder,
		{ name = "Row", rect = { 0, 0, ui.listW, ROW_H }, icon = icon, title = title, trailing = 120 }
	)
	Kit.Button.new(holder, {
		name = label,
		rect = { ui.listW - 14 - 120, (ROW_H - 42) / 2, 120, 42 },
		label = label,
		sizeClass = "s",
		zIndex = 6,
		onPress = onPress,
	})
	add(holder, ROW_H)
end

local function button(label: string, variant: string, onPress)
	local holder = Kit.Core.Make("Frame", {
		Name = "Action" .. #ui.parts,
		BackgroundTransparency = 1,
		LayoutOrder = #ui.parts + 1,
		Size = UDim2.fromOffset(ui.listW, BUTTON_H),
	}, ui.list)
	Kit.Button.new(holder, {
		name = label,
		rect = { 0, 0, 260, BUTTON_H },
		label = label,
		variant = variant,
		sizeClass = "s",
		onPress = onPress,
	})
	add(holder, BUTTON_H)
end

local function render()
	if ui.list == nil then
		return
	end
	for _, part in ui.parts or {} do
		part:Destroy()
	end
	ui.parts = {}
	ui.height = 0
	local tribe = view.tribe
	if tribe then
		header(("Your tribe %d/%d"):format(#tribe.members, TribeController.MAX_MEMBERS), "party")
		local leading = tribe.leader == player.UserId
		for _, member in tribe.members do
			person(
				member.userId,
				member.name,
				member.userId == tribe.leader,
				if leading and member.userId ~= player.UserId
					then {
						label = "Kick",
						variant = "secondary",
						onPress = function()
							act("kick", member.userId)
						end,
					}
					else nil
			)
		end
		if #tribe.allies > 0 then
			line(("Allied with %d tribe(s)"):format(#tribe.allies))
		end
		button("Leave tribe", "secondary", function()
			act("leave")
		end)
		if leading then
			local nearby = {}
			for _, other in Players:GetPlayers() do
				if other ~= player and other:GetAttribute("TribeId") == nil then
					table.insert(nearby, other)
				end
			end
			if #nearby > 0 then
				header("Invite nearby players", "invite")
				for _, other in nearby do
					person(other.UserId, other.DisplayName, false, {
						label = "Invite",
						onPress = function()
							act("invite", other.UserId)
						end,
					})
				end
			end
			if #view.others > 0 then
				header("Alliances", "flag")
				for _, other in view.others do
					choice("flag", ("%s's tribe (%d)"):format(other.leader, other.size), "Propose", function()
						act("ally", other.tribeId)
					end)
				end
			end
		end
	else
		header("No tribe", "party")
		line("You are not in a tribe.")
		button("Create tribe", "primary", function()
			act("create")
		end)
	end
	if #view.invites > 0 then
		header("Invites", "mail")
		for _, invite in view.invites do
			choice("party", invite.from .. "'s tribe", "Join", function()
				act("accept", invite.tribeId)
			end)
		end
	end
	ui.panel.scroll:SetContentHeight(ui.height)
end

local function refreshKey()
	ui.key:SetText(Binds.Label("Tribe"))
end

local function build()
	ui.screen = Kit.Screen.new("FlintbornTribe", { size = TribeController.SIZE })
	local window = Kit.Window.new(ui.screen, { title = "Tribe", icon = "totem" })
	local body = window:Body()
	local bw, bh = window.bodyRect[3], window.bodyRect[4]
	ui.status = Kit.Text.new(body, {
		name = "Status",
		rect = { 4, 0, bw - 8, 30 },
		text = "Tribes: up to 8. No friendly fire.",
		role = "bodySoft",
	})
	ui.panel =
		Kit.Panel.new(body, { name = "List", rect = { 0, 36, bw, bh - 36 - 52 }, variant = "inset", scroll = true })
	ui.list = ui.panel:Content()
	ui.listW = ui.panel.contentRect[3] - 14
	-- The live key that opens and closes this window.
	ui.key = Kit.KeyCap.new(body, { name = "Key", rect = { 4, bh - 42, 0, 40 }, text = Binds.Label("Tribe") })
	Kit.Text.new(body, {
		name = "KeyLabel",
		rect = { 4 + ui.key.w + 10, bh - 42, 300, 40 },
		text = "Open or close",
		role = "rowLabel",
	})
	-- Key hints only where there is a keyboard.
	ui.key.root.Visible = UserInputService.KeyboardEnabled
	body:FindFirstChild("KeyLabel").Visible = UserInputService.KeyboardEnabled
	ui.screen:Watch()
end

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function TribeController.Toggle()
	ui.screen:Toggle()
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
	Binds.Changed:Connect(refreshKey)
	render()
end

return TribeController
