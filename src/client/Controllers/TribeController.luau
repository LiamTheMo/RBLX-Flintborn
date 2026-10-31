-- Tribe panel (GDD §5.2, Q39): create a tribe, invite nearby players, accept
-- invites, kick (leader), leave, and propose alliances. Toggle with the Tribe key
-- (T by default) or the Tribe button. A kit window: members and nearby players
-- as player rows, alliances and invites as list rows, each with its action.
-- A gamepad lands on the first action and keeps its place when the list redraws.
-- World place only.

local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Keybinds = require(ReplicatedStorage.Shared.Settings.Keybinds)
local Kit = require(script.Parent.Parent.Hud.Kit)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

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
	ui.status:SetText(
		if ok and success then tostring(reason or "Done") else ("Failed: " .. Reasons.Text(if ok then reason else nil))
	)
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

-- Remembers an action button for gamepad selection (`id` stays the same
-- across redraws). `noDefault`: never where a gamepad lands by itself (Leave).
local function remember(id: string, control, noDefault: boolean?)
	if control then
		table.insert(ui.buttons, { id = id, hit = control.hit, noDefault = noDefault })
	end
end

local function person(userId: number, name: string, leader: boolean, action)
	local other = Players:GetPlayerByUserId(userId)
	local level = other and other:GetAttribute("Level")
	-- `name` is the player's name (it also names the row).
	local row = Kit.PlayerRow.new(ui.list, {
		size = { ui.listW, ROW_H },
		layoutOrder = #ui.parts + 1,
		userId = userId,
		name = name,
		level = if type(level) == "number" then level else nil,
		-- Large enough to keep 9 px on phones.
		levelSize = 15,
		leader = leader,
		action = action,
	})
	add(row, ROW_H)
	if action and row.action then
		remember(("person/%d/%s"):format(userId, action.label), row.action.control)
	end
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
	local action = Kit.Button.new(holder, {
		name = label,
		rect = { ui.listW - 14 - 120, (ROW_H - 42) / 2, 120, 42 },
		label = label,
		sizeClass = "s",
		zIndex = 6,
		onPress = onPress,
	})
	add(holder, ROW_H)
	remember(("choice/%s/%s"):format(title, label), action.control)
end

local function button(label: string, variant: string, onPress, noDefault: boolean?)
	local holder = Kit.Core.Make("Frame", {
		Name = "Action" .. #ui.parts,
		BackgroundTransparency = 1,
		LayoutOrder = #ui.parts + 1,
		Size = UDim2.fromOffset(ui.listW, BUTTON_H),
	}, ui.list)
	local action = Kit.Button.new(holder, {
		name = label,
		rect = { 0, 0, 260, BUTTON_H },
		label = label,
		variant = variant,
		sizeClass = "s",
		onPress = onPress,
	})
	add(holder, BUTTON_H)
	remember("button/" .. label, action.control, noDefault)
end

-- "1 tribe", "2 tribes".
function TribeController.Plural(count: number, word: string): string
	return ("%d %s%s"):format(count, word, if count == 1 then "" else "s")
end

local function render()
	if ui.list == nil then
		return
	end
	-- The focused action, by id, so the redraw can give it back.
	local focus = GuiService.SelectedObject
	local focusId = nil
	if focus and focus:IsDescendantOf(ui.screen.gui) then
		focusId = "close"
		for _, entry in ui.buttons or {} do
			if entry.hit == focus then
				focusId = entry.id
			end
		end
	end
	for _, part in ui.parts or {} do
		part:Destroy()
	end
	ui.parts = {}
	ui.buttons = {}
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
			line("Allied with " .. TribeController.Plural(#tribe.allies, "tribe"))
		end
		button("Leave tribe", "secondary", function()
			act("leave")
		end, true)
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
	-- A gamepad lands on the first action (never Leave); a redraw keeps the
	-- focused one.
	local first = nil
	for _, entry in ui.buttons do
		if not entry.noDefault then
			first = entry.hit
			break
		end
	end
	ui.screen:SetDefaultSelection(first or ui.close)
	if focusId then
		local again = nil
		for _, entry in ui.buttons do
			if entry.id == focusId then
				again = entry.hit
			end
		end
		GuiService.SelectedObject = again or first or ui.close
	end
end

local function refreshKey()
	ui.key:SetText(Binds.Label("Tribe"))
end

local function build()
	ui.screen = Kit.Screen.new("FlintbornTribe", { size = TribeController.SIZE })
	local window = Kit.Window.new(ui.screen, { title = "Tribe", icon = "totem" })
	ui.close = window.close and window.close.control.hit
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
	-- The live key (or gamepad button) that opens and closes this window; no
	-- hint on touch.
	local gamepadKey = Keybinds.Get("Tribe").gamepad[1]
	ui.key = Kit.KeyCap.new(body, {
		name = "Key",
		rect = { 4, bh - 42, 0, 40 },
		text = Binds.Label("Tribe"),
		gamepadKey = gamepadKey,
		hideOnTouch = true,
	})
	local keyLabel = Kit.Text.new(body, {
		name = "KeyLabel",
		rect = { 4 + math.max(ui.key.w, 64) + 10, bh - 42, 300, 40 },
		text = "Open or close",
		role = "rowLabel",
	})
	local function showHint()
		keyLabel.root.Visible = not Kit.Input.IsTouch()
	end
	Kit.Input.Watch(showHint)
	showHint()
	ui.screen:Watch()
end

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function TribeController.Toggle()
	if not ui.screen:IsOpen() then
		-- Drawn first, so the window opens with its default action chosen.
		render()
	end
	ui.screen:Toggle()
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
