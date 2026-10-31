-- The Party window (docs/ui/PartyScreen.md, mockup 04; ARCHITECTURE §4.4 and
-- decisions D5, D6, D18, D19), built only from Kit components at the mockup's
-- 1124 × 637 window size. Display only: PartyController feeds it SetData and
-- answers its callbacks.
--
--   YOUR PARTY n/8   the leader (crown, Leader tag), members (Ready / Not Ready
--                    tag) and Empty Slot rows; 8 rows, 7 visible, then scrolls
--   INVITE PLAYERS   incoming invitations (Accept / ✕), the search box and the
--                    players you may invite (Invite / Invited)
--   PARTY DETAILS    Party Leader, Members, Join Type, Created (no Play Style, D6;
--                    the freed row stays empty, PartyScreen open question 3a)
--   READIED STATUS   one row per member (one shows; the list scrolls), the
--                    ready tally and your Ready / Not Ready toggle (D18)
--   footer           CLOSE, and LEAVE PARTY while you share a party
--
--   local window = PartyWindow.new({ onInvite = invite, onReady = setReady, ... })
--   window:SetData(data) -- see SetData
--   window:Open()

local GuiService = game:GetService("GuiService")

local Kit = require(script.Parent.Parent.Kit)

local PartyWindow = {}
PartyWindow.__index = PartyWindow

-- Rects are measured on the mockup canvas (1672 × 941); ORIGIN is the window's
-- top-left there. Rects inside a panel are measured from the panel's top-left.
PartyWindow.ORIGIN = { 274, 143 }
PartyWindow.SIZE = { 1124, 637 }
PartyWindow.MOCKUP = {
	closeX = { 1324, 168, 56, 53 },
	party = { 304, 245, 360, 448 },
	invite = { 670, 245, 371, 448 },
	details = { 1047, 245, 322, 265 },
	ready = { 1047, 507, 322, 186 },
	close = { 711, 703, 250, 60 },
	leave = { 1103, 706, 240, 54 },
}

-- A mockup canvas rect in window design px.
local function inWindow(r: { number }): { number }
	local o = PartyWindow.ORIGIN
	return { r[1] - o[1], r[2] - o[2], r[3], r[4] }
end

-- Row heights (M04): the leader row from the heading rule to the first row
-- rule, the empty slots' 52.4 px pitch, invite rows on 66 px and the readied
-- row of 64 px.
PartyWindow.LEADER_ROW = 74
PartyWindow.ROW = 52.4
PartyWindow.INVITE_ROW = 66
PartyWindow.READY_ROW = 64
PartyWindow.LIST_W = { party = 328, invite = 337, ready = 289 }

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

-- A column heading at the top of a panel `w` wide: flat ink glyph at `icon`
-- ({id, x, y, w, h} from the panel's top-left), capitals from `textX`, an
-- optional count and the ink rule `rule` ({x, y, w}).
local HEADER_Y = 7
local function header(parent: Instance, w: number, text: string, icon, textX: number, rule, count: string?)
	return Kit.SectionHeader.new(parent, {
		name = "Header",
		rect = { 0, HEADER_Y, w, 56 },
		text = text,
		icon = icon[1],
		iconRect = { icon[2], icon[3] - HEADER_Y, icon[4], icon[5] },
		textX = textX,
		count = count,
		countGap = 25,
		ruleRect = { rule[1], rule[2] - HEADER_Y, rule[3], 2 },
		zIndex = Z + 1,
	})
end

-- A list in a panel: the thin rail sits over the gap right of the rows, so
-- rows keep the mockup's width.
local function list(parent: Instance, name: string, rect, gap: number)
	return Kit.Scroll.new(parent, {
		name = name,
		rect = rect,
		gap = gap,
		rail = "thin",
		railOverlay = true,
		railInset = -10,
		padBottom = 0,
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
		titleSize = 48,
		titleY = 20,
		-- D19: the mockup's tent and pines are not in the kit; the tree icon is
		-- the closest kit art (KIT.md §8).
		ornaments = { "tree", "tree" },
		ornamentSize = 52,
		ornamentGap = 26,
		ruleRect = { 481 - 274, 229 - 143, 781, 3 },
		clasps = true,
		claspYs = { 0.856 },
		closeRect = inWindow(M.closeX),
	})
	self.closeX = self.window.close
	local v = self.window.base.visual

	-- Your Party ----------------------------------------------------------------------
	local party = Kit.Panel.new(v, { name = "YourParty", rect = inWindow(M.party), variant = "inset", zIndex = Z })
	local pv = party.base.visual
	self.partyHeader = header(pv, 360, "Your Party", { "ink:people", 19, 18, 36, 26 }, 69, { 16, 52, 329 }, "1/8")
	-- 7 rows show (the leader row and six at the mockup pitch); the 8th scrolls.
	self.memberList = list(pv, "Members", { 16, 55, PartyWindow.LIST_W.party, 391 }, 0)

	-- Invite Players ------------------------------------------------------------------
	local invite =
		Kit.Panel.new(v, { name = "InvitePlayers", rect = inWindow(M.invite), variant = "inset", zIndex = Z })
	local iv = invite.base.visual
	self.inviteHeader = header(iv, 371, "Invite Players", { "ink:magnifier", 23, 17, 26, 27 }, 67, { 17, 52, 336 })
	self.search = Kit.SearchBox.new(iv, {
		name = "Search",
		rect = { 15, 69, 340, 42 },
		placeholder = "Search players...",
		zIndex = Z + 2,
		onChanged = function(text)
			if props.onSearch then
				props.onSearch(text)
			end
		end,
	})
	Kit.Divider.new(iv, { name = "ListRule", rect = { 16, 121, 337, 2 }, variant = "hairline", zIndex = Z + 1 })
	self.inviteListRect = { 16, 120, PartyWindow.LIST_W.invite, 325 }
	self.inviteList = list(iv, "Players", self.inviteListRect, 0)
	-- Roblox friends who are not in this server (SocialService), shown only
	-- where the platform allows game invites.
	self.friends = Kit.Button.new(iv, {
		name = "InviteFriends",
		rect = { 16, 400, 337, 40 },
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
		rect = { 20, 140, 331, 60 },
		text = "",
		role = "bodySoft",
		align = "Center",
		wrap = true,
		zIndex = Z + 2,
	})

	-- Party Details -------------------------------------------------------------------
	local details =
		Kit.Panel.new(v, { name = "PartyDetails", rect = inWindow(M.details), variant = "inset", zIndex = Z })
	local dv = details.base.visual
	header(dv, 322, "Party Details", { "ink:info", 17, 16, 31, 30 }, 63, { 16, 52, 290 })
	-- The rows are drawn by SetData (a line row sizes its value when built).
	self.detailsVisual = dv
	self.detailRows = {}

	-- Readied Status ------------------------------------------------------------------
	local ready = Kit.Panel.new(v, { name = "ReadiedStatus", rect = inWindow(M.ready), variant = "inset", zIndex = Z })
	local rv = ready.base.visual
	header(rv, 322, "Readied Status", { "ink:check", 17, 16, 31, 31 }, 63, { 16, 53, 290 })
	-- One row shows, as in the mockup; more members scroll.
	self.readyList = list(rv, "Ready", { 16, 57, PartyWindow.LIST_W.ready, 68 }, 0)
	self.tally = Kit.Text.new(rv, {
		name = "Tally",
		rect = { 18, 134, 120, 42 },
		text = "",
		role = "bodySoft",
		zIndex = Z + 1,
	})
	self.readyButton = Kit.Button.new(rv, {
		name = "ReadyToggle",
		rect = { 150, 134, 155, 42 },
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
				size = { PartyWindow.LIST_W.party, h },
				layoutOrder = i,
				userId = member.userId,
				name = member.name,
				level = member.level,
				leader = member.leader,
				badge = if member.leader then "leader" elseif member.ready then "ready" else "notReady",
				portraitSize = if i == 1 then 56 else nil,
				nameX = 75,
				nameSize = 17,
				levelSize = 15,
				crownSize = 26,
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
				size = { PartyWindow.LIST_W.party, h },
				layoutOrder = i,
				empty = true,
				portraitSize = 52,
				emptyIndent = 12,
				nameX = 76,
				nameSize = 14,
				zIndex = Z + 2,
			})
		)
		height += h
	end
	self.memberList:SetContentHeight(height + 2)
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
				rect = { 26, 61 + (i - 1) * 36, 274, 36 },
				variant = "line",
				title = label,
				value = values[label],
				titleSize = 15,
				valueSize = 15,
				zIndex = Z + 1,
			})
		)
	end
end

local function inviteAction(row, onInvite)
	local state = row.state
	if state == "invited" then
		return { label = "Invited", variant = "secondary", enabled = false, size = { 108, 45 } }
	end
	return {
		label = "Invite",
		variant = "primary",
		size = { 108, 45 },
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
	local w = self.inviteListRect[3]
	local function section(text: string)
		order += 1
		height += 36
		self:_add(
			"invites",
			Kit.SectionHeader.new(content, {
				name = "Section" .. order,
				size = { w, 36 },
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
			height += PartyWindow.INVITE_ROW
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
				portraitSize = 52,
				nameX = 70,
				nameSize = 17,
				levelSize = 14,
				action = {
					size = { 108, 45 },
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
				rect = { w - 40, 14, 38, 38 },
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
		height += PartyWindow.INVITE_ROW
		local row = self:_add(
			"invites",
			Kit.PlayerRow.new(content, {
				size = { w, PartyWindow.INVITE_ROW },
				layoutOrder = order,
				zIndex = Z + 2,
				userId = entry.userId,
				name = entry.name,
				level = entry.level,
				portraitSize = 52,
				nameX = 70,
				nameSize = 17,
				levelSize = 14,
				action = inviteAction(entry, props.onInvite),
			})
		)
		if entry.state == "pending" then
			row.action:SetBusy(true)
		end
		self.selectables["invites:player:" .. entry.userId] = row.action.control.hit
	end
	self.inviteList:SetContentHeight(height + 2)
	local note = data.inviteNote
	self.inviteNote:SetText(note or "")
	self.inviteNote.root.Visible = note ~= nil
	-- The note sits under whatever the list already shows.
	self.inviteNote.root.Position = UDim2.fromOffset(20, self.inviteListRect[2] + 12 + height)
end

function PartyWindow:_ready(data)
	self:_clear("ready")
	local content = self.readyList:Content()
	for i, member in data.members do
		self:_add(
			"ready",
			Kit.PlayerRow.new(content, {
				size = { PartyWindow.LIST_W.ready, PartyWindow.READY_ROW },
				layoutOrder = i,
				userId = member.userId,
				name = member.name,
				badge = if member.ready then "ready" else "notReady",
				portraitSize = 48,
				nameX = 65,
				nameSize = 16,
				zIndex = Z + 2,
			})
		)
	end
	self.readyList:SetContentHeight(#data.members * PartyWindow.READY_ROW + 2)
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
