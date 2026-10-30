-- The Party window (docs/ui/PartyScreen.md, mockup 04; ARCHITECTURE §4.4 and
-- decisions D5, D6, D18, D19), built only from Kit components at the mockup's
-- 1124 × 637 design size. Display only: PartyController feeds it SetData and
-- answers its callbacks.
--
--   YOUR PARTY n/8   the leader (crown, Leader tag), members (Ready / Not Ready
--                    tag) and Empty Slot rows; 8 rows, 7 visible, then scrolls
--   INVITE PLAYERS   incoming invitations (Accept / ✕), the search box and the
--                    players you may invite (Invite / Invited)
--   PARTY DETAILS    Party Leader, Members, Join Type, Created (no Play Style, D6)
--   READIED STATUS   one row per member, the ready tally and your Ready / Not
--                    Ready toggle (D18); Party Details gives it the 36 px the
--                    dropped Play Style row freed (PartyScreen open question 3b)
--   footer           CLOSE, and LEAVE PARTY while you share a party
--
--   local window = PartyWindow.new({ onInvite = invite, onReady = setReady, ... })
--   window:SetData(data) -- see SetData
--   window:Open()

local GuiService = game:GetService("GuiService")

local Kit = require(script.Parent.Parent.Kit)

local PartyWindow = {}
PartyWindow.__index = PartyWindow

-- Rects are taken from the mockup canvas (1672 × 941). The kit's window and
-- inset-panel art draw their borders a few px inside their rects (window 4–6,
-- panels 6–7), so both grow by that much and the borders land where the mockup
-- draws them. ORIGIN is the window rect's top-left on the canvas.
PartyWindow.ORIGIN = { 268, 139 }
PartyWindow.SIZE = { 1136, 642 }
PartyWindow.MOCKUP = {
	closeX = { 1322, 166, 60, 57 },
	party = { 304, 245, 360, 448 },
	invite = { 670, 245, 371, 448 },
	details = { 1047, 245, 322, 229 },
	ready = { 1047, 471, 322, 222 },
	close = { 708, 701, 254, 63 },
	leave = { 1103, 706, 240, 54 },
}
local PANEL_INSET = 6

-- A mockup canvas rect in window design px.
local function inWindow(r: { number }): { number }
	local o = PartyWindow.ORIGIN
	return { r[1] - o[1], r[2] - o[2], r[3], r[4] }
end

-- A panel's rect, grown so its art border sits on the mockup's.
local function panelRect(r: { number }): { number }
	local w = inWindow(r)
	return { w[1] - PANEL_INSET, w[2] - PANEL_INSET, w[3] + 2 * PANEL_INSET, w[4] + PANEL_INSET + 4 }
end

-- A rect measured from the mockup panel's top-left, in the grown panel.
local function inPanel(x: number, y: number, w: number, h: number): { number }
	return { x + PANEL_INSET, y + PANEL_INSET, w, h }
end

-- Row heights: the leader row and the 52.4 px pitch of the empty slots (M04),
-- invite rows on a 66 px pitch, ready rows two to the card.
PartyWindow.LEADER_ROW = 62
PartyWindow.ROW = 52.4
PartyWindow.INVITE_ROW = 58
PartyWindow.INVITE_GAP = 8
PartyWindow.READY_ROW = 52

local Z = 6

export type Props = {
	onInvite: ((userId: number) -> ())?,
	onAccept: ((partyId: string) -> ())?,
	onDecline: ((partyId: string) -> ())?,
	onLeave: (() -> ())?,
	onReady: ((ready: boolean) -> ())?,
	onInviteFriends: (() -> ())?,
	onSearch: ((text: string) -> ())?,
	onClosed: (() -> ())?,
	parent: Instance?,
}

-- A column heading: the kit header (icon, capitals, optional count) placed so
-- its text starts where the mockup's does (`textX`, from the panel's left), and
-- the heading rule drawn separately across `ruleX`..`ruleX + ruleW` at y 52.
local function header(parent: Instance, text: string, icon: string, count: string?, textX: number, rule: { number })
	local w = rule[1] + rule[2] - (textX - 44)
	Kit.Divider.new(parent, {
		name = "HeaderRule",
		rect = inPanel(rule[1], 44, rule[2], 16),
		variant = "header",
		zIndex = Z + 1,
	})
	return Kit.SectionHeader.new(parent, {
		name = "Header",
		rect = inPanel(textX - 44, 18, w, 36),
		text = text,
		icon = icon,
		count = count,
		rule = false,
		zIndex = Z + 1,
	})
end

function PartyWindow.new(props: Props)
	local self = setmetatable({ props = props, lists = {}, selectables = {}, data = nil }, PartyWindow)
	local M = PartyWindow.MOCKUP
	local screen = Kit.Screen.new("FlintbornParty", { size = PartyWindow.SIZE, parent = props.parent })
	self.screen = screen
	self.window = Kit.Window.new(screen, {
		title = "Party",
		header = "centered",
		-- D19: the mockup's tent and pines are not in the kit; the camp fire and
		-- tree icons are the closest kit art.
		ornaments = { "campfire", "tree" },
		clasps = true,
		claspYs = { 0.856 },
		showClose = false,
	})
	local v = self.window.base.visual
	self.closeX = Kit.IconButton.new(v, {
		name = "CloseX",
		variant = "close",
		rect = inWindow(M.closeX),
		zIndex = Z + 4,
		onPress = function()
			screen:Close()
		end,
	})

	-- Your Party ----------------------------------------------------------------------
	local party = Kit.Panel.new(v, { name = "YourParty", rect = panelRect(M.party), variant = "inset", zIndex = Z })
	local pv = party.base.visual
	self.partyHeader = header(pv, "Your Party", "party", "1/8", 67, { 16, 329 })
	-- 7 rows show (the leader row and six at the mockup pitch); the 8th scrolls.
	self.memberList =
		Kit.Scroll.new(pv, { name = "Members", rect = inPanel(16, 67, 342, 379), gap = 0, zIndex = Z + 1 })

	-- Invite Players ------------------------------------------------------------------
	local invite =
		Kit.Panel.new(v, { name = "InvitePlayers", rect = panelRect(M.invite), variant = "inset", zIndex = Z })
	local iv = invite.base.visual
	self.inviteHeader = header(iv, "Invite Players", "magnifier", nil, 68, { 17, 336 })
	self.search = Kit.SearchBox.new(iv, {
		name = "Search",
		rect = inPanel(15, 69, 340, 42),
		placeholder = "Search players...",
		zIndex = Z + 2,
		onChanged = function(text)
			if props.onSearch then
				props.onSearch(text)
			end
		end,
	})
	Kit.Divider.new(iv, { name = "ListRule", rect = inPanel(18, 114, 333, 16), variant = "rule", zIndex = Z + 1 })
	self.inviteListRect = inPanel(16, 128, 351, 317)
	self.inviteList = Kit.Scroll.new(iv, {
		name = "Players",
		rect = self.inviteListRect,
		gap = PartyWindow.INVITE_GAP,
		zIndex = Z + 1,
	})
	-- Roblox friends who are not in this server (SocialService), shown only
	-- where the platform allows game invites.
	self.friends = Kit.Button.new(iv, {
		name = "InviteFriends",
		rect = inPanel(16, 400, 331, 40),
		label = "Invite Friends",
		icon = "invite",
		variant = "secondary",
		sizeClass = "s",
		zIndex = Z + 2,
		visible = false,
		onPress = function()
			if props.onInviteFriends then
				props.onInviteFriends()
			end
		end,
	})
	self.inviteNote = Kit.Text.new(iv, {
		name = "Note",
		rect = inPanel(20, 140, 331, 60),
		text = "",
		role = "bodySoft",
		align = "Center",
		wrap = true,
		zIndex = Z + 2,
	})

	-- Party Details -------------------------------------------------------------------
	local details =
		Kit.Panel.new(v, { name = "PartyDetails", rect = panelRect(M.details), variant = "inset", zIndex = Z })
	local dv = details.base.visual
	header(dv, "Party Details", "exclamation", nil, 64, { 16, 290 })
	-- The rows are drawn by SetData (a line row sizes its value when built).
	self.detailsVisual = dv
	self.detailRows = {}

	-- Readied Status ------------------------------------------------------------------
	local ready = Kit.Panel.new(v, { name = "ReadiedStatus", rect = panelRect(M.ready), variant = "inset", zIndex = Z })
	local rv = ready.base.visual
	header(rv, "Readied Status", "check", nil, 64, { 16, 290 })
	self.readyList = Kit.Scroll.new(rv, { name = "Ready", rect = inPanel(10, 57, 310, 108), gap = 0, zIndex = Z + 1 })
	self.tally = Kit.Text.new(rv, {
		name = "Tally",
		rect = inPanel(18, 172, 132, 42),
		text = "",
		role = "bodySoft",
		zIndex = Z + 1,
	})
	self.readyButton = Kit.Button.new(rv, {
		name = "ReadyToggle",
		rect = inPanel(150, 172, 155, 42),
		label = "Ready",
		sizeClass = "s",
		zIndex = Z + 2,
		onPress = function()
			local data = self.data
			if data and props.onReady and data.readyPending == nil then
				props.onReady(not data.selfReady)
			end
		end,
	})

	-- Footer --------------------------------------------------------------------------
	self.closeButton = Kit.Button.new(v, {
		name = "CloseButton",
		rect = inWindow(M.close),
		label = "Close",
		variant = "play",
		zIndex = Z + 2,
		onPress = function()
			screen:Close()
		end,
	})
	self.leaveButton = Kit.Button.new(v, {
		name = "LeaveParty",
		rect = inWindow(M.leave),
		label = "Leave Party",
		variant = "secondary",
		sizeClass = "s",
		zIndex = Z + 2,
		visible = false,
		onPress = function()
			if props.onLeave then
				props.onLeave()
			end
		end,
	})
	screen:SetDefaultSelection(self.readyButton.control.hit)
	screen.Closed:Connect(function()
		if props.onClosed then
			props.onClosed()
		end
	end)
	screen:Watch()
	return self
end

-- The key of the list control gamepad selection is on, so a rebuild can put
-- it back on the same row's control.
function PartyWindow:_selectedKey(): string?
	local selected = GuiService.SelectedObject
	if selected == nil then
		return nil
	end
	for key, hit in self.selectables do
		if hit == selected then
			return key
		end
	end
	return nil
end

function PartyWindow:_clear(name: string)
	for _, component in self.lists[name] or {} do
		component:Destroy()
	end
	self.lists[name] = {}
	for key in self.selectables do
		if string.sub(key, 1, #name + 1) == name .. ":" then
			self.selectables[key] = nil
		end
	end
end

function PartyWindow:_add(name: string, component)
	table.insert(self.lists[name], component)
	return component
end

function PartyWindow:_members(data)
	self:_clear("members")
	local content = self.memberList:Content()
	local height = 0
	for i, member in data.members do
		local h = if i == 1 then PartyWindow.LEADER_ROW else PartyWindow.ROW
		self:_add(
			"members",
			Kit.PlayerRow.new(content, {
				size = { 322, h },
				layoutOrder = i,
				userId = member.userId,
				name = member.name,
				level = member.level,
				leader = member.leader,
				badge = if member.leader then "leader" elseif member.ready then "ready" else "notReady",
				zIndex = Z + 2,
			})
		)
		height += h
	end
	for i = #data.members + 1, data.maxSize do
		local h = if i == 1 then PartyWindow.LEADER_ROW else PartyWindow.ROW
		self:_add(
			"members",
			Kit.PlayerRow.new(content, {
				name = "EmptySlot",
				size = { 322, h },
				layoutOrder = i,
				empty = true,
				zIndex = Z + 2,
			})
		)
		height += h
	end
	self.memberList:SetContentHeight(height + 14)
end

PartyWindow.DETAILS = { "Party Leader", "Members", "Join Type", "Created" }

function PartyWindow:_details(data)
	self:_clear("details")
	local values = {
		["Party Leader"] = data.leaderName,
		Members = data.membersText,
		["Join Type"] = data.joinType,
		Created = data.createdText,
	}
	for i, label in PartyWindow.DETAILS do
		self.detailRows[label] = self:_add(
			"details",
			Kit.ListRow.new(self.detailsVisual, {
				name = (label:gsub(" ", "")),
				rect = inPanel(26, 60 + (i - 1) * 36, 274, 36),
				variant = "line",
				title = label,
				value = values[label],
				zIndex = Z + 1,
			})
		)
	end
end

local function inviteAction(row, onInvite)
	local state = row.state
	if state == "invited" then
		return { label = "Invited", variant = "secondary", enabled = false }
	end
	return {
		label = "Invite",
		variant = "primary",
		enabled = state ~= "full",
		onPress = function()
			if onInvite then
				onInvite(row.userId)
			end
		end,
	}
end

function PartyWindow:_invites(data)
	self:_clear("invites")
	local props = self.props
	local content = self.inviteList:Content()
	local order, height = 0, 0
	local w = self.inviteListRect[3] - 20
	local function section(text: string)
		order += 1
		height += 32 + PartyWindow.INVITE_GAP
		self:_add(
			"invites",
			Kit.SectionHeader.new(content, {
				name = "Section" .. order,
				size = { w, 32 },
				layoutOrder = order,
				text = text,
				zIndex = Z + 2,
			})
		)
	end
	local incoming = data.invites or {}
	if #incoming > 0 then
		section("Invitations")
		for _, entry in incoming do
			order += 1
			height += PartyWindow.INVITE_ROW + PartyWindow.INVITE_GAP
			-- The row leaves room at its right for the decline ✕.
			local holder = self:_add(
				"invites",
				Kit.Panel.new(content, {
					name = "Invitation" .. order,
					size = { w, PartyWindow.INVITE_ROW },
					layoutOrder = order,
					variant = "plain",
					zIndex = Z + 2,
				})
			)
			local row = Kit.PlayerRow.new(holder.base.visual, {
				rect = { 0, 0, w - 44, PartyWindow.INVITE_ROW },
				zIndex = Z + 2,
				userId = entry.userId,
				name = entry.from,
				level = entry.level,
				action = {
					label = "Accept",
					onPress = function()
						if props.onAccept then
							props.onAccept(entry.partyId)
						end
					end,
				},
			})
			local decline = Kit.IconButton.new(holder.base.visual, {
				name = "Decline",
				rect = { w - 40, 10, 38, 38 },
				variant = "small",
				icon = "cross",
				zIndex = Z + 3,
				onPress = function()
					if props.onDecline then
						props.onDecline(entry.partyId)
					end
				end,
			})
			holder.base.maid:Give(function()
				row:Destroy()
				decline:Destroy()
			end)
			if entry.busy then
				row.action:SetBusy(true)
				decline:SetEnabled(false)
			end
			self.selectables["invites:accept:" .. entry.partyId] = row.action.control.hit
			self.selectables["invites:decline:" .. entry.partyId] = decline.control.hit
		end
		if #data.inviteRows > 0 then
			section("Players")
		end
	end
	for _, entry in data.inviteRows do
		order += 1
		height += PartyWindow.INVITE_ROW + PartyWindow.INVITE_GAP
		local row = self:_add(
			"invites",
			Kit.PlayerRow.new(content, {
				size = { w, PartyWindow.INVITE_ROW },
				layoutOrder = order,
				zIndex = Z + 2,
				userId = entry.userId,
				name = entry.name,
				level = entry.level,
				action = inviteAction(entry, props.onInvite),
			})
		)
		if entry.state == "pending" then
			row.action:SetBusy(true)
		end
		self.selectables["invites:player:" .. entry.userId] = row.action.control.hit
	end
	self.inviteList:SetContentHeight(height + 14)
	local note = data.inviteNote
	self.inviteNote:SetText(note or "")
	self.inviteNote.root.Visible = note ~= nil
	-- The note sits under whatever the list already shows.
	self.inviteNote.root.Position = UDim2.fromOffset(PANEL_INSET + 20, self.inviteListRect[2] + 12 + height)
end

function PartyWindow:_ready(data)
	self:_clear("ready")
	local content = self.readyList:Content()
	for i, member in data.members do
		self:_add(
			"ready",
			Kit.PlayerRow.new(content, {
				size = { 290, PartyWindow.READY_ROW },
				layoutOrder = i,
				userId = member.userId,
				name = member.name,
				badge = if member.ready then "ready" else "notReady",
				zIndex = Z + 2,
			})
		)
	end
	self.readyList:SetContentHeight(#data.members * PartyWindow.READY_ROW + 14)
	local count = 0
	for _, member in data.members do
		if member.ready then
			count += 1
		end
	end
	self.tally:SetText(("%d of %d ready"):format(count, #data.members))
	local button = data.readyButton
	self.readyButton:SetVariant(button.variant)
	self.readyButton:SetLabel(button.label)
	self.readyButton:SetBusy(button.busy)
end

-- Draws everything from `data` (PartyController builds it with PartyModel):
--   members      {{userId, name, level?, leader, ready, isSelf}} leader first
--   maxSize      the cap (8)
--   leaderName, membersText, countText, createdText
--   readyButton  PartyModel.ReadyButton(...); selfReady, readyPending
--   inviteRows   PartyModel.InviteRows(...) plus level
--   inviteNote   text for an empty invite list, or nil
--   canInvite    false greys the search box
--   invites      {{partyId, from, userId?, level?, busy?}} waiting for you
--   canLeave, leaveBusy, friends (show Invite Friends)
function PartyWindow:SetData(data)
	local key = self:_selectedKey()
	self.data = data
	self.partyHeader:SetCount(data.countText)
	self:_details(data)
	self:_members(data)
	self:_invites(data)
	self:_ready(data)
	self.search:SetEnabled(data.canInvite)
	-- Invite Friends takes the bottom of the invite column when it shows.
	local friends = data.friends == true
	self.friends.root.Visible = friends
	self.inviteList.root.Size =
		UDim2.fromOffset(self.inviteListRect[3], self.inviteListRect[4] - (if friends then 50 else 0))
	self.leaveButton.root.Visible = data.canLeave
	self.leaveButton:SetBusy(data.leaveBusy == true)
	if key and GuiService.SelectedObject == nil and self.screen:IsOpen() then
		local again = self.selectables[key]
		GuiService.SelectedObject = if again then again else self.readyButton.control.hit
	end
end

-- Only the "Created" value (the once-a-minute clock).
function PartyWindow:SetCreated(text: string)
	if self.data and self.data.createdText ~= text then
		self.data.createdText = text
		self:_details(self.data)
	end
end

function PartyWindow:SearchText(): string
	return self.search:GetText()
end

-- Opens the window. `section` ("invite" | "ready" | "party") picks the control
-- gamepad selection starts on.
function PartyWindow:Open(section: string?, gamepad: boolean?)
	local default = self.readyButton.control.hit
	if section == "invite" then
		local first = nil
		for key, hit in self.selectables do
			if string.sub(key, 1, 8) == "invites:" and (first == nil or key < first) then
				first = key
			end
		end
		default = if first then self.selectables[first] else self.search.box
	elseif section == "party" then
		default = self.closeButton.control.hit
	end
	self.screen:SetDefaultSelection(default)
	self.screen:Open(gamepad)
end

function PartyWindow:Close()
	self.screen:Close()
end

function PartyWindow:IsOpen(): boolean
	return self.screen:IsOpen()
end

function PartyWindow:Destroy()
	for name in self.lists do
		self:_clear(name)
	end
	self.screen:Destroy()
end

return PartyWindow
