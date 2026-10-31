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
--
-- SetData updates rows in place: a row whose player and contents are unchanged
-- stays as it is (only its order moves); changed rows are redrawn and rows that
-- left are removed, so a search keystroke or one member's Ready redraws only
-- what changed. On phones and touch tablets (Kit.Scale.IsSmallTouch) names and
-- level lines draw larger and long names end in "…" rather than shrinking
-- below 9 screen px.

local GuiService = game:GetService("GuiService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local Kit = require(script.Parent.Parent.Kit)

local PartyWindow = {}
PartyWindow.__index = PartyWindow

-- Rects are measured on the mockup canvas (1672 × 941); ORIGIN is the window's
-- top-left there. Rects inside a panel are measured from the panel's top-left.
PartyWindow.ORIGIN = { 276, 146 }
PartyWindow.SIZE = { 1120, 631 }
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

-- The kit draws the inset panel's border on its rect, so no compensation is
-- left (kept for callers that read it).
PartyWindow.PANEL_ART = { 0, 0, 0, 0 }

-- An inset panel on the mockup rect `r`; returns the frame its contents go in
-- (design px from the mockup panel's top-left).
local function panel(parent: Instance, name: string, r: { number }): Frame
	local a = PartyWindow.PANEL_ART
	local o = inWindow(r)
	local plate = Kit.Panel.new(parent, {
		name = name,
		rect = { o[1] - a[1], o[2] - a[2], o[3] + a[1] + a[3], o[4] + a[2] + a[4] },
		variant = "inset",
		zIndex = Z,
	})
	local inner = Kit.Panel.new(plate.base.visual, {
		name = "Inner",
		rect = { a[1], a[2], o[3], o[4] },
		variant = "plain",
		pad = 0,
		zIndex = Z,
	})
	return inner.base.visual
end

-- Rows (M04). A framed row is a slot of `h` in its list holding a PlayerRow at
-- `inner` ({x, y, w, h}; its name and level lines sit where the mockup's do)
-- and the hairline `rule` ({x, y, w}) the mockup draws under it. The empty
-- slots keep their 52.4 px pitch as plain PlayerRows.
PartyWindow.ROW = 52.4
PartyWindow.FRAMES = {
	leader = { h = 74, inner = { 0, 7, 334, 59 }, rule = { 0, 71, 328 } },
	member = { h = 52.4, inner = { 0, 0, 334, 52.4 }, rule = { 0, 50.4, 328 } },
	invite = { h = 66, inner = { 0, 8, 337, 51 }, rule = { 0, 65, 334 } },
	ready = { h = 64, inner = { 0, 0, 295, 64 }, rule = { 0, 62, 289 } },
}
PartyWindow.LIST_W = { party = 328, invite = 337, ready = 289 }

local Z = 6

-- Text sizes, desktop and phone (phone sizes keep names, levels and button
-- labels at 9 screen px or more at the phone window scale, about 0.51).
PartyWindow.TEXT = {
	desktop = { name = 17, level = 15, inviteLevel = 13, action = nil, detail = 15, emptyName = 14, readyName = 16 },
	phone = { name = 15, level = 15, inviteLevel = 15, action = 15, detail = 15, emptyName = 15, readyName = 15 },
}
-- How long the search box waits after the last keystroke.
PartyWindow.SEARCH_DEBOUNCE = 0.3

-- `text` cut to fit `width` design px in `role` at `size`, ending in "…".
local function fitText(text: string, role: string, size: number?, width: number): string
	if Kit.Text.Width(text, role, size) <= width then
		return text
	end
	local cut = text
	while #cut > 1 do
		cut = string.sub(cut, 1, #cut - 1)
		local candidate = cut .. "…"
		if Kit.Text.Width(candidate, role, size) <= width then
			return candidate
		end
	end
	return cut
end

-- A row's signature: its fields joined, so an unchanged row is kept.
local function signature(...): string
	local parts = table.pack(...)
	for index = 1, parts.n do
		parts[index] = tostring(parts[index])
	end
	return table.concat(parts, "|", 1, parts.n)
end

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
		countGap = 31,
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
	local self = setmetatable({
		props = props,
		lists = {},
		selectables = {},
		data = nil,
		phone = Kit.Scale.IsSmallTouch(),
		maid = KitModel.Maid(),
	}, PartyWindow)
	local M = PartyWindow.MOCKUP
	local screen = Kit.Screen.new("FlintbornParty", { size = PartyWindow.SIZE, parent = props.parent })
	self.screen = screen
	self.window = Kit.Window.new(screen, {
		title = "Party",
		header = "centered",
		titleSize = 48,
		titleY = 22,
		-- The mockup centres its title 7.5 px right of the window's centre.
		titleRect = { 843.5 - PartyWindow.ORIGIN[1] - 120, 22, 240, 60 },
		-- D19: the mockup's tent and pines are not in the kit; the tree icon is
		-- the closest kit art (KIT.md §8).
		ornaments = { "tree", "tree" },
		ornamentSize = 52,
		ornamentGap = 26,
		ruleRect = { 481 - PartyWindow.ORIGIN[1], 229 - PartyWindow.ORIGIN[2], 781, 3 },
		clasps = true,
		claspYs = { 0.856 },
		closeRect = inWindow(M.closeX),
	})
	self.closeX = self.window.close
	local v = self.window.base.visual

	-- Your Party ----------------------------------------------------------------------
	local pv = panel(v, "YourParty", M.party)
	self.partyHeader = header(pv, 360, "Your Party", { "ink:people", 19, 18, 36, 26 }, 69, { 16, 52, 329 }, "1/8")
	-- 7 rows show (the leader row and six at the mockup pitch); the 8th scrolls.
	self.memberList = list(pv, "Members", { 16, 57, PartyWindow.LIST_W.party, 389 }, 0)

	-- Invite Players ------------------------------------------------------------------
	local iv = panel(v, "InvitePlayers", M.invite)
	self.inviteHeader = header(iv, 371, "Invite Players", { "ink:magnifier", 23, 17, 26, 27 }, 67, { 17, 52, 336 })
	self.search = Kit.SearchBox.new(iv, {
		name = "Search",
		rect = { 15, 69, 340, 42 },
		placeholder = "Search players...",
		debounce = PartyWindow.SEARCH_DEBOUNCE,
		zIndex = Z + 2,
		onChanged = function(text)
			if props.onSearch then
				props.onSearch(text)
			end
		end,
	})
	Kit.Divider.new(iv, { name = "ListRule", rect = { 16, 121, 337, 2 }, variant = "hairline", zIndex = Z + 1 })
	self.inviteListRect = { 18, 120, PartyWindow.LIST_W.invite, 325 }
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
	local dv = panel(v, "PartyDetails", M.details)
	-- The mockup's circled "i" is not in the kit; the book (a record of the
	-- party) is the closest neutral glyph (the "!" read as a warning).
	header(dv, 322, "Party Details", { "ink:book", 18, 16, 30, 30 }, 63, { 16, 52, 290 })
	-- The rows are drawn by SetData (a line row sizes its value when built).
	self.detailsVisual = dv
	self.detailRows = {}

	-- Readied Status ------------------------------------------------------------------
	local rv = panel(v, "ReadiedStatus", M.ready)
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
		-- M04's CLOSE is the darker leather.
		tone = "dark",
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
	self.maid:Give(screen.Closed:Connect(function()
		if props.onClosed then
			props.onClosed()
		end
	end))
	screen:Watch()
	-- Phone and desktop text sizes follow the screen and the input devices.
	self.maid:Give(Kit.Scale.OnFormFactorChanged(function()
		local phone = Kit.Scale.IsSmallTouch()
		if phone ~= self.phone then
			self.phone = phone
			for name in self.lists do
				self:_clear(name)
			end
			if self.data then
				self:SetData(self.data)
			end
		end
	end))
	return self
end

function PartyWindow:_text()
	return if self.phone then PartyWindow.TEXT.phone else PartyWindow.TEXT.desktop
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

-- Removes every row of list `name` (and its gamepad targets).
function PartyWindow:_clear(name: string)
	for _, entry in self.lists[name] or {} do
		self:_drop(entry)
	end
	self.lists[name] = {}
end

function PartyWindow:_drop(entry)
	entry.component:Destroy()
	for key in entry.selectables do
		self.selectables[key] = nil
	end
end

-- Brings list `name` in step with `rows` ({key, sig, build(order) ->
-- (component, {[selectableKey] = hit}?)}) in order: a row with the same key
-- and signature is kept and only re-ordered; any other is (re)built; rows no
-- longer listed are removed.
function PartyWindow:_sync(name: string, rows)
	local old = self.lists[name] or {}
	local new = {}
	for order, row in rows do
		local entry = old[row.key]
		if entry and entry.sig == row.sig then
			entry.component.root.LayoutOrder = order
		else
			if entry then
				self:_drop(entry)
			end
			local component, selectables = row.build(order)
			entry = { component = component, sig = row.sig, selectables = selectables or {} }
			for key, hit in entry.selectables do
				self.selectables[key] = hit
			end
		end
		old[row.key] = nil
		new[row.key] = entry
	end
	for _, entry in old do
		self:_drop(entry)
	end
	self.lists[name] = new
end

-- A framed row (PartyWindow.FRAMES[kind]) in `content`; returns the holder,
-- whose `.row` is the PlayerRow. On phones long names end in "…" at their
-- size instead of shrinking past the 9 px floor.
function PartyWindow:_framed(content: Instance, kind: string, order: number, rowProps, w: number?)
	local frame = PartyWindow.FRAMES[kind]
	local width = w or frame.inner[3]
	local holder = Kit.Panel.new(content, {
		name = "Row" .. order,
		size = { PartyWindow.LIST_W[if kind == "leader" or kind == "member" then "party" else kind], frame.h },
		layoutOrder = order,
		variant = "plain",
		pad = 0,
		zIndex = Z + 2,
	})
	local props = table.clone(rowProps)
	props.rect = { frame.inner[1], frame.inner[2], width, frame.inner[4] }
	props.rule = false
	props.zIndex = Z + 2
	if self.phone then
		props.shrinkName = false
	end
	local row = Kit.PlayerRow.new(holder.base.visual, props)
	local rule = Kit.Divider.new(holder.base.visual, {
		name = "Rule",
		rect = { frame.rule[1], frame.rule[2], frame.rule[3], 2 },
		variant = "hairline",
		zIndex = Z + 2,
	})
	holder.row = row
	holder.props = row.props
	holder.action = row.action
	holder.base.maid:Give(function()
		row:Destroy()
		rule:Destroy()
	end)
	return holder
end

function PartyWindow:_members(data)
	local content = self.memberList:Content()
	local text = self:_text()
	local rows = {}
	local height = 0
	for i, member in data.members do
		local leaderRow = i == 1
		local badge = if member.leader then "leader" elseif member.ready then "ready" else "notReady"
		table.insert(rows, {
			key = "member:" .. member.userId,
			sig = signature(member.name, member.level, member.leader, badge, leaderRow),
			build = function(order: number)
				local rowProps = {
					userId = member.userId,
					name = member.name,
					level = member.level,
					leader = member.leader,
					badge = badge,
					nameX = 75,
					nameSize = text.name,
					levelSize = text.level,
					crownSize = 26,
					portraitSize = if leaderRow then 56 else nil,
				}
				return self:_framed(content, if leaderRow then "leader" else "member", order, rowProps)
			end,
		})
		height += if leaderRow then PartyWindow.FRAMES.leader.h else PartyWindow.ROW
	end
	for i = #data.members + 1, data.maxSize do
		table.insert(rows, {
			key = "empty:" .. i,
			sig = "empty",
			build = function(order: number)
				return Kit.PlayerRow.new(content, {
					name = "EmptySlot",
					size = { PartyWindow.LIST_W.party, PartyWindow.ROW },
					layoutOrder = order,
					empty = true,
					portraitSize = 52,
					emptyIndent = 12,
					nameX = 76,
					nameSize = text.emptyName,
					zIndex = Z + 2,
				})
			end,
		})
		height += PartyWindow.ROW
	end
	self:_sync("members", rows)
	self.memberList:SetContentHeight(height + 2)
end

PartyWindow.DETAILS = { "Party Leader", "Members", "Join Type", "Created" }
-- A detail row's width and the gap between its label and value.
PartyWindow.DETAIL_W = 274

function PartyWindow:_details(data)
	local size = self:_text().detail
	local values = {
		["Party Leader"] = data.leaderName,
		Members = data.membersText,
		["Join Type"] = data.joinType,
		Created = data.createdText,
	}
	local rows = {}
	for i, label in PartyWindow.DETAILS do
		-- A long value (a 20-character leader name) ends in "…" so the label
		-- keeps its room.
		local room = PartyWindow.DETAIL_W - Kit.Text.Width(label, "rowLabel", size) - 24
		local value = fitText(values[label] or "", "value", size, room)
		table.insert(rows, {
			key = label,
			sig = value,
			build = function()
				local row = Kit.ListRow.new(self.detailsVisual, {
					name = (label:gsub(" ", "")),
					rect = { 26, 61 + (i - 1) * 36, PartyWindow.DETAIL_W, 36 },
					variant = "line",
					title = label,
					value = value,
					titleSize = size,
					valueSize = size,
					zIndex = Z + 1,
				})
				self.detailRows[label] = row
				return row
			end,
		})
	end
	self:_sync("details", rows)
end

local function inviteAction(row, onInvite, textSize: number?)
	local state = row.state
	if state == "invited" then
		return { label = "Invited", variant = "secondary", enabled = false, size = { 108, 45 }, textSize = textSize }
	end
	return {
		label = "Invite",
		variant = "primary",
		size = { 108, 45 },
		textSize = textSize,
		enabled = state ~= "full",
		onPress = function()
			if onInvite then
				onInvite(row.userId)
			end
		end,
	}
end

function PartyWindow:_invites(data)
	local props = self.props
	local text = self:_text()
	local content = self.inviteList:Content()
	local rows = {}
	local height = 0
	local w = self.inviteListRect[3]
	local frameH = PartyWindow.FRAMES.invite.h
	local function section(title: string)
		height += 36
		table.insert(rows, {
			key = "section:" .. title,
			sig = title,
			build = function(order: number)
				return Kit.SectionHeader.new(content, {
					name = "Section" .. order,
					size = { w, 36 },
					layoutOrder = order,
					text = title,
					zIndex = Z + 2,
				})
			end,
		})
	end
	local function rowProps(name: string, userId: number?, level: number?, action)
		return {
			userId = userId,
			name = name,
			level = level,
			portraitSize = 52,
			nameX = 68,
			nameSize = text.name,
			levelSize = text.inviteLevel,
			action = action,
		}
	end
	local incoming = data.invites or {}
	if #incoming > 0 then
		section("Invitations")
		for _, entry in incoming do
			height += frameH
			table.insert(rows, {
				key = "in:" .. entry.partyId,
				sig = signature(entry.from, entry.userId, entry.level, entry.busy),
				build = function(order: number)
					-- The row leaves room at its right for the decline ✕.
					local holder = self:_framed(
						content,
						"invite",
						order,
						rowProps(entry.from, entry.userId, entry.level, {
							size = { 108, 45 },
							label = "Accept",
							textSize = text.action,
							onPress = function()
								if props.onAccept then
									props.onAccept(entry.partyId)
								end
							end,
						}),
						w - 44
					)
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
						decline:Destroy()
					end)
					if entry.busy then
						holder.action:SetBusy(true)
						decline:SetEnabled(false)
					end
					return holder,
						{
							["invites:accept:" .. entry.partyId] = holder.action.control.hit,
							["invites:decline:" .. entry.partyId] = decline.control.hit,
						}
				end,
			})
		end
		if #data.inviteRows > 0 then
			section("Players")
		end
	end
	for _, entry in data.inviteRows do
		height += frameH
		table.insert(rows, {
			key = "player:" .. entry.userId,
			sig = signature(entry.name, entry.level, entry.state),
			build = function(order: number)
				local holder = self:_framed(
					content,
					"invite",
					order,
					rowProps(entry.name, entry.userId, entry.level, inviteAction(entry, props.onInvite, text.action))
				)
				if entry.state == "pending" then
					holder.action:SetBusy(true)
				end
				return holder, { ["invites:player:" .. entry.userId] = holder.action.control.hit }
			end,
		})
	end
	self:_sync("invites", rows)
	self.inviteList:SetContentHeight(height + 2)
	local note = data.inviteNote
	self.inviteNote:SetText(note or "")
	self.inviteNote.root.Visible = note ~= nil
	-- The note sits under whatever the list already shows.
	self.inviteNote.root.Position = UDim2.fromOffset(20, self.inviteListRect[2] + 12 + height)
end

function PartyWindow:_ready(data)
	local content = self.readyList:Content()
	local text = self:_text()
	local rows = {}
	for _, member in data.members do
		local badge = if member.ready then "ready" else "notReady"
		table.insert(rows, {
			key = "ready:" .. member.userId,
			sig = signature(member.name, badge),
			build = function(order: number)
				return self:_framed(content, "ready", order, {
					userId = member.userId,
					name = member.name,
					badge = badge,
					portraitSize = 48,
					nameX = 65,
					nameSize = text.readyName,
				})
			end,
		})
	end
	self:_sync("ready", rows)
	self.readyList:SetContentHeight(#data.members * PartyWindow.FRAMES.ready.h + 2)
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
-- Rows whose contents did not change are kept as they are.
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

-- The components of list `name` ("members", "invites", "details", "ready")
-- in their shown order (scenes and verifiers).
function PartyWindow:Rows(name: string)
	local list = {}
	for _, entry in self.lists[name] or {} do
		table.insert(list, entry.component)
	end
	table.sort(list, function(a, b)
		return a.root.LayoutOrder < b.root.LayoutOrder
	end)
	return list
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
	self.maid:Clean()
	for name in self.lists do
		self:_clear(name)
	end
	self.screen:Destroy()
end

return PartyWindow
