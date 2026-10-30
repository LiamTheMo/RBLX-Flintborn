-- The Quest Journal window (art/reference/ui/lobby/07_quest_journal.png, spec
-- docs/ui/JournalScreen.md, ARCHITECTURE §4.7 and D12), built only from the UI
-- kit. Four side tabs hang off the frame's left edge:
--   book    quests: the list (daily first, then main, under section headers)
--           and the chosen quest's page: illustration, name, description,
--           OBJECTIVES with progress and a check, REWARDS tiles, CLAIM, and the
--           QUEST PROGRESS bar along the bottom
--   trophy  progression, read-only, in the same layout (level, masteries,
--           titles; ProgressionController's snapshot)
--   map pin the painted island map (Hud/IslandMap) with the chosen quest's place
--   party   opens the Party window (the controller does it; no page here)
-- The window only draws pages (JournalModel) and reports presses; the
-- JournalController fetches quests and claims rewards.
--
-- Positions are the mockup's pixels less the window's top-left (300, 150), so
-- they read straight off the image. The tabs reach 50 px left of the frame, so
-- the screen is 50 px wider on both sides and the frame stays centred.

local GuiService = game:GetService("GuiService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local JournalModel = require(ReplicatedStorage.Shared.UI.JournalModel)
local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local Kit = require(script.Parent.Parent.Kit)
local IslandMap = require(script.Parent.Parent.IslandMap)

local JournalWindow = {}
JournalWindow.__index = JournalWindow

JournalWindow.FRAME = { 1072, 688 }
JournalWindow.MARGIN = 50
JournalWindow.SIZE = { 1072 + 2 * 50, 688 }
-- The kit frame's art sits a little inside its rect at the top, right and
-- bottom: this rect draws its edges on the mockup's (300–1372, 150–838).
JournalWindow.FRAME_RECT = { 50, -4, 1078, 698 }
-- Where the mockup's window corner (300, 150) falls inside that frame.
JournalWindow.ORIGIN = { 0, 4 }

-- Side tabs: {id, y}. The party tab opens another window.
JournalWindow.TAB_X = -45
JournalWindow.TAB_SIZE = { 82, 84 }
JournalWindow.TAB_YS = { quests = 101, progress = 195, map = 288, party = 383 }

local Z = 8
local ROW = { 357, 95 }
local ROW_GAP = 9
local HEADER_H = 30
local LIST = { 62, 109, 380, 512 }
local OBJECTIVE = { 590, 59 }
local OBJECTIVE_GAP = 6
local OBJECTIVES = { 452, 280, 610, 197 }
local TILE = { 92, 104 }
local TILE_PITCH = 98
local MAP = { 51, 108, 991, 512 }

-- Moves a kit label to a mockup rect, optionally at another text size.
local function nudge(label: GuiObject, rect, size: number?)
	label.Position = UDim2.fromOffset(rect[1], rect[2])
	label.Size = UDim2.fromOffset(rect[3], rect[4])
	if size then
		(label :: TextLabel).TextSize = size
	end
end

-- parent: where the ScreenGui goes (PlayerGui by default). handlers: onClose(),
-- onTab(id), onSelect(id), onClaim(id), onParty().
function JournalWindow.new(parent: Instance?, handlers)
	local self = setmetatable({}, JournalWindow)
	self.handlers = handlers or {}
	self.maid = KitModel.Maid()
	self.pages = {}
	self.selected = {}
	self.tab = "quests"
	local screen = Kit.Screen.new("FlintbornJournal", { size = JournalWindow.SIZE, parent = parent })
	self.screen = screen
	self.maid:Give(screen)
	local window = Kit.Window.new(screen.window, {
		rect = JournalWindow.FRAME_RECT,
		title = "Quest Journal",
		icon = "compass",
		onClose = function()
			if self.handlers.onClose then
				self.handlers.onClose()
			else
				screen:Close()
			end
		end,
	})
	self.window = window
	self.maid:Give(window)
	screen:SetDefaultSelection(window.close.control.hit)
	-- Everything below is placed in mockup px less (300, 150).
	local v = Kit.Core.Make("Frame", {
		Name = "Content",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(JournalWindow.ORIGIN[1], JournalWindow.ORIGIN[2]),
		Size = UDim2.fromOffset(JournalWindow.FRAME[1], JournalWindow.FRAME[2]),
		ZIndex = Z,
	}, window.base.visual)
	self.visual = v
	self:_header(v)
	self:_tabs(v)
	self:_entriesPage(v)
	self:_footer(v)
	self:SelectTab("quests")
	return self
end

-- The header as the mockup draws it: the compass, QUEST JOURNAL and the rule
-- under both, and the ✕.
function JournalWindow:_header(v: Frame)
	local window = self.window
	local ox, oy = JournalWindow.ORIGIN[1], JournalWindow.ORIGIN[2]
	nudge(window.icon, { 64 + ox, 9 + oy, 84, 88 })
	nudge(window.title.root, { 155 + ox, 16 + oy, 700, 70 }, 47)
	-- The rule runs under the compass too, the full width of the header.
	window.rule.root.Visible = false
	Kit.Divider.new(v, { name = "HeaderRule", rect = { 39, 85, 992, 16 }, variant = "header", zIndex = Z })
	window.close.root.Position = UDim2.fromOffset(995 + ox, 20 + oy)
end

function JournalWindow:_tabs(v: Frame)
	local tabs = {}
	self.tabs = {}
	for _, id in { "quests", "progress", "map" } do
		local tab = Kit.Tab.new(v, {
			id = id,
			name = "Tab" .. id,
			rect = {
				JournalWindow.TAB_X,
				JournalWindow.TAB_YS[id],
				JournalWindow.TAB_SIZE[1],
				JournalWindow.TAB_SIZE[2],
			},
			icon = JournalModel.TAB_ICONS[id],
			variant = "side",
			zIndex = Z + 4,
		})
		table.insert(tabs, tab)
		self.tabs[id] = tab
	end
	self.tabGroup = Kit.TabGroup.new(tabs, function(id)
		self:SelectTab(id)
		if self.handlers.onTab then
			self.handlers.onTab(id)
		end
	end)
	self.maid:Give(self.tabGroup)
	self.partyTab = Kit.Tab.new(v, {
		id = "party",
		name = "Tabparty",
		rect = {
			JournalWindow.TAB_X,
			JournalWindow.TAB_YS.party,
			JournalWindow.TAB_SIZE[1],
			JournalWindow.TAB_SIZE[2],
		},
		icon = JournalModel.TAB_ICONS.party,
		variant = "side",
		zIndex = Z + 4,
		onPress = function()
			if self.handlers.onParty then
				self.handlers.onParty()
			end
		end,
	})
	self.tabs.party = self.partyTab
	self.maid:Give(self.partyTab)
end

-- The list and the detail page, shared by the quest and progress tabs.
function JournalWindow:_entriesPage(v: Frame)
	local page = Kit.Core.Make("Frame", {
		Name = "Entries",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		ZIndex = Z,
	}, v)
	self.entriesFrame = page
	Kit.Divider.new(page, { name = "ListRule", rect = { 43, 110, 16, 506 }, variant = "vertical", zIndex = Z })
	Kit.Divider.new(page, { name = "ScrollRule", rect = { 427, 110, 16, 506 }, variant = "vertical", zIndex = Z })
	self.list = Kit.Scroll.new(page, { name = "Quests", rect = LIST, gap = ROW_GAP, padBottom = 6, zIndex = Z })
	self.rows = {}
	self.listParts = KitModel.Maid()
	self.empty = Kit.Text.new(page, {
		name = "Empty",
		rect = { 72, 130, 340, 60 },
		text = "",
		role = "bodySoft",
		wrap = true,
		zIndex = Z + 1,
	})

	local detail = Kit.Core.Make("Frame", {
		Name = "Detail",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		ZIndex = Z,
	}, page)
	self.detail = detail
	self.illustration = Kit.Icon.new(detail, { name = "Illustration", rect = { 466, 112, 197, 122 }, zIndex = Z })
	self.heading = Kit.Text.new(detail, {
		name = "Heading",
		rect = { 679, 112, 350, 50 },
		text = "",
		role = "detailTitle",
		scaled = true,
		zIndex = Z,
	})
	self.heading.root.TextSize = 36
	self.description = Kit.Text.new(detail, {
		name = "Description",
		rect = { 684, 163, 350, 60 },
		text = "",
		role = "body",
		wrap = true,
		yAlign = "Top",
		zIndex = Z,
	})
	self.description.root.TextSize = 18
	self.description.root.LineHeight = 1.12
	Kit.Divider.new(detail, { name = "DetailRule", rect = { 455, 238, 587, 16 }, variant = "rule", zIndex = Z })
	self.objectivesHead = Kit.Text.new(detail, {
		name = "ObjectivesHead",
		rect = { 455, 250, 300, 28 },
		text = "Objectives",
		role = "sectionHeader",
		zIndex = Z,
	})
	self.objectivesHead.root.TextSize = 18
	self.objectives = Kit.Scroll.new(detail, {
		name = "Objectives",
		rect = OBJECTIVES,
		gap = OBJECTIVE_GAP,
		padBottom = 2,
		zIndex = Z,
	})
	self.rewardsRule = Kit.Divider.new(detail, {
		name = "RewardsRule",
		rect = { 452, 470, 590, 16 },
		variant = "rule",
		zIndex = Z,
	})
	self.rewardsHead = Kit.Text.new(detail, {
		name = "RewardsHead",
		rect = { 456, 480, 300, 28 },
		text = "Rewards",
		role = "sectionHeader",
		zIndex = Z,
	})
	self.rewardsHead.root.TextSize = 18
	self.detailParts = KitModel.Maid()
	self.claim = Kit.Button.new(detail, {
		name = "Claim",
		rect = { 859, 511, 183, 88 },
		label = "Claim",
		textSize = 27,
		zIndex = Z + 1,
		onPress = function()
			local entry = self:_entry()
			if entry and entry.claim and entry.claim.enabled and self.handlers.onClaim then
				self.handlers.onClaim(entry.id)
			end
		end,
	})
	self.maid:Give(self.listParts)
	self.maid:Give(self.detailParts)
end

-- The progress line along the bottom: label, bar and count.
function JournalWindow:_footer(v: Frame)
	Kit.Divider.new(v, { name = "FooterRule", rect = { 50, 619, 980, 16 }, variant = "rule", zIndex = Z })
	self.footerLabel = Kit.Text.new(v, {
		name = "ProgressLabel",
		rect = { 90, 634, 252, 32 },
		text = "",
		role = "sectionHeader",
		align = "Right",
		zIndex = Z,
	})
	self.footerLabel.root.TextSize = 17
	self.footerBar = Kit.Bar.new(v, { name = "ProgressBar", rect = { 357, 640, 375, 18 }, fill = "xp", zIndex = Z })
	self.footerText = Kit.Text.new(v, {
		name = "ProgressText",
		rect = { 749, 634, 300, 32 },
		text = "",
		role = "value",
		zIndex = Z,
	})
	self.footerText.root.TextSize = 19
end

-- The map page, built the first time the map tab opens.
function JournalWindow:_mapPage()
	if self.map then
		return
	end
	local v = self.visual
	local frame = Kit.Core.Make("Frame", {
		Name = "MapPage",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		Visible = false,
		ZIndex = Z,
	}, v)
	self.mapFrame = frame
	Kit.Panel.new(frame, { name = "MapPanel", rect = MAP, variant = "inset", zIndex = Z })
	local inner = { MAP[1] + 8, MAP[2] + 8, MAP[3] - 16, MAP[4] - 16 }
	self.map = IslandMap.new(frame, inner, {
		zIndex = Z + 1,
		zoomButtons = {
			{ inner[1] + inner[3] - 70, inner[2] + inner[4] - 134, 58, 58 },
			{ inner[1] + inner[3] - 70, inner[2] + inner[4] - 70, 58, 58 },
		},
	})
	self.maid:Give(self.map)
end

-- The page shown under the tabs: quests and progress draw entries; the map tab
-- shows the map with the quests' footer.
function JournalWindow:SelectTab(id: string)
	if id == "party" then
		return
	end
	self.tab = id
	self.tabGroup:Select(id)
	local isMap = id == "map"
	if isMap then
		self:_mapPage()
	end
	self.entriesFrame.Visible = not isMap
	if self.mapFrame then
		self.mapFrame.Visible = isMap
	end
	self:_draw()
	if isMap then
		self:_pointMap()
	end
end

function JournalWindow:Tab(): string
	return self.tab
end

-- The page a tab draws (JournalModel.QuestPage / ProgressPage). The map tab
-- uses the quest page's footer and places.
function JournalWindow:SetPage(tab: string, page)
	self.pages[tab] = page
	if tab == self.tab or (tab == "quests" and self.tab == "map") then
		self:_draw()
	end
end

-- Chooses an entry on the current tab (quests on the map tab).
function JournalWindow:Select(id: string?)
	local tab = if self.tab == "map" then "quests" else self.tab
	self.selected[tab] = id
	self:_draw()
	if self.handlers.onSelect then
		self.handlers.onSelect(id)
	end
end

-- The id chosen on `tab` (default: the shown one).
function JournalWindow:Selected(tab: string?): string?
	local key = tab or (if self.tab == "map" then "quests" else self.tab)
	return self.selected[key]
end

-- The party tab works only where the Party window exists (the lobby).
function JournalWindow:SetPartyAvailable(available: boolean)
	self.partyTab:SetEnabled(available)
end

function JournalWindow:_page()
	local tab = if self.tab == "map" then "quests" else self.tab
	return self.pages[tab], tab
end

function JournalWindow:_entry()
	local page, tab = self:_page()
	if page == nil then
		return nil
	end
	return JournalModel.Find(page, self.selected[tab])
end

function JournalWindow:_draw()
	local page, tab = self:_page()
	-- Keep the chosen entry while it is listed; else the first one.
	if page and JournalModel.Find(page, self.selected[tab]) == nil then
		local first = JournalModel.First(page)
		self.selected[tab] = first and first.id
	end
	local footer = page and page.footer
	self.footerLabel:SetText(footer and footer.label or "")
	self.footerBar:Set(footer and footer.fraction or 0)
	self.footerText:SetText(footer and footer.text or "")
	if self.tab == "map" then
		self:_pointMap()
		return
	end
	self:_drawList(page, tab)
	self:_drawDetail(self:_entry())
end

-- Rebuilds the rows; gamepad focus on a row moves to the same entry's new row.
function JournalWindow:_drawList(page, tab: string)
	local focused = nil
	local focus = GuiService.SelectedObject
	for id, row in self.rows do
		if focus and focus:IsDescendantOf(row.root) then
			focused = id
		end
	end
	self.listParts:Clean()
	self.rows = {}
	local content = self.list:Content()
	local order, height = 0, 0
	local groups = page and page.groups or {}
	local selectedHit = nil
	for _, group in groups do
		if group.title then
			order += 1
			local header = self.listParts:Give(Kit.SectionHeader.new(content, {
				name = "Group" .. group.id,
				size = { ROW[1], HEADER_H },
				layoutOrder = order,
				text = group.title,
				count = group.note,
				zIndex = Z + 1,
			}))
			if header.count then
				header.count.TextSize = 14
				header.count.TextColor3 = Kit.Tokens.Color("inkSoft")
				header.count.Size = UDim2.fromOffset(200, HEADER_H - 6)
			end
			height += HEADER_H + ROW_GAP
		end
		for _, entry in group.entries do
			order += 1
			local row = self:_row(content, entry, order)
			self.rows[entry.id] = row
			height += ROW[2] + ROW_GAP
			if entry.id == self.selected[tab] then
				selectedHit = row.control.hit
			end
			if entry.id == focused then
				GuiService.SelectedObject = row.control.hit
			end
		end
	end
	self.list:SetContentHeight(height)
	self.empty.root.Visible = order == 0
	self.empty:SetText(if order == 0 and page then page.empty or "" elseif order == 0 then "Loading…" else "")
	self.detail.Visible = order > 0
	self.screen:SetDefaultSelection(selectedHit or self.window.close.control.hit)
	self:_navigation(selectedHit)
end

-- One list row: icon, title, line, chevron; a red dot while a reward waits and a
-- check once it is claimed.
function JournalWindow:_row(content: Instance, entry, order: number)
	local row = self.listParts:Give(Kit.ListRow.new(content, {
		name = entry.id,
		size = ROW,
		layoutOrder = order,
		variant = "card",
		icon = entry.icon,
		title = entry.title,
		subtitle = entry.subtitle,
		chevron = true,
		zIndex = Z + 1,
		onPress = function()
			self:Select(entry.id)
		end,
	}))
	nudge(row.icon, { 10, 11, 92, 72 })
	nudge(row.title, { 119, 12, 205, 36 }, 19)
	nudge(row.subtitle, { 120, 46, 200, 28 }, 15)
	local tab = if self.tab == "map" then "quests" else self.tab
	row:SetSelected(entry.id == self.selected[tab])
	if entry.status == "ready" then
		Kit.Badge.new(row.base.visual, { name = "Ready", variant = "dot", rect = { 331, 9, 16, 16 }, zIndex = Z + 4 })
	elseif entry.status == "claimed" then
		Kit.Icon.new(row.base.visual, { name = "Claimed", rect = { 323, 8, 26, 22 }, icon = "check", zIndex = Z + 4 })
	end
	return row
end

-- Gamepad order: tabs → the chosen row → CLAIM (when it can be pressed) → ✕.
function JournalWindow:_navigation(selectedHit: GuiObject?)
	local tabHit = self.tabs[self.tab] and self.tabs[self.tab].control.hit
	for _, row in self.rows do
		row.control.hit.NextSelectionLeft = tabHit
		row.control.hit.NextSelectionRight = self.claim.control.hit
	end
	for _, tab in self.tabs do
		tab.control.hit.NextSelectionRight = selectedHit
	end
	self.claim.control.hit.NextSelectionLeft = selectedHit
	self.claim.control.hit.NextSelectionUp = self.window.close.control.hit
end

function JournalWindow:_drawDetail(entry)
	self.detailParts:Clean()
	if entry == nil then
		self.detail.Visible = false
		return
	end
	self.detail.Visible = true
	self.illustration:SetIcon(entry.illustration)
	self.heading:SetText(entry.heading or entry.title)
	self.description:SetText(entry.description or "")

	local content = self.objectives:Content()
	for index, objective in entry.objectives or {} do
		self:_objective(content, objective, index)
	end
	local count = #(entry.objectives or {})
	self.objectives:SetContentHeight(count * (OBJECTIVE[2] + OBJECTIVE_GAP))

	local rewards = entry.rewards or {}
	local hasRewards = #rewards > 0
	self.rewardsHead.root.Visible = hasRewards
	self.rewardsRule.root.Visible = hasRewards or entry.claim ~= nil
	self.rewardsHead:SetText(entry.rewardsTitle or "Rewards")
	for index, reward in rewards do
		self:_reward(reward, index)
	end

	local claim = entry.claim
	self.claim.root.Visible = claim ~= nil
	if claim then
		self.claim:SetLabel(claim.label)
		self.claim:SetBusy(claim.busy == true)
		self.claim:SetEnabled(claim.enabled == true or claim.busy == true)
	end
end

-- One objective row: icon, title, description, n / m and the check.
function JournalWindow:_objective(content: Instance, objective, index: number)
	local hasCount = objective.count ~= nil and objective.needed ~= nil
	local row = self.detailParts:Give(Kit.ListRow.new(content, {
		name = "Objective" .. index,
		size = OBJECTIVE,
		layoutOrder = index,
		variant = "row",
		icon = objective.icon,
		title = objective.title,
		subtitle = objective.description,
		value = if hasCount then ("%d / %d"):format(objective.count, objective.needed) else nil,
		zIndex = Z + 1,
	}))
	nudge(row.icon, { 10, 7, 54, 45 })
	nudge(row.title, { 84, 6, 330, 26 }, 18)
	nudge(row.subtitle, { 84, 31, 380, 20 }, 14)
	if row.value then
		nudge(row.value, { 412, 0, 110, OBJECTIVE[2] }, 19)
	end
	local check = Kit.Checkbox.new(row.base.visual, {
		name = "Check",
		rect = { 542, 14, 32, 32 },
		variant = "tile",
		checked = objective.done == true,
		zIndex = Z + 3,
	})
	-- A display, not a control: the server decides when an objective is done.
	check.control.hit.Visible = false
	check.control.hit.Selectable = false
	return row
end

-- One reward tile: icon, amount over its corner, label under it.
function JournalWindow:_reward(reward, index: number)
	local x = 451 + (index - 1) * TILE_PITCH
	local tile = self.detailParts:Give(Kit.Panel.new(self.detail, {
		name = "Reward" .. index,
		rect = { x, 512, TILE[1], TILE[2] },
		variant = "inset",
		pad = 0,
		zIndex = Z,
	}))
	local c = tile.base.visual
	Kit.Icon.new(c, { name = "Icon", rect = { 12, 12, 58, 50 }, icon = reward.icon, zIndex = Z + 1 })
	local amount = Kit.Text.new(c, {
		name = "Amount",
		rect = { 4, 55, TILE[1] - 12, 20 },
		text = reward.amount,
		role = "count",
		align = "Right",
		zIndex = Z + 2,
	})
	amount.root.TextSize = 18
	local label = Kit.Text.new(c, {
		name = "Label",
		rect = { 3, 75, TILE[1] - 6, 24 },
		text = reward.label,
		role = "value",
		align = "Center",
		wrap = true,
		scaled = true,
		zIndex = Z + 2,
	})
	label.root.TextSize = 15
end

-- On the map tab: the chosen quest's place gets its name plate and the map
-- centres on it.
function JournalWindow:_pointMap()
	if self.map == nil then
		return
	end
	local entry = self:_entry()
	local place = entry and entry.place
	if place == self.pointedAt then
		return
	end
	self.pointedAt = place
	self.map:Select(place)
	local pin = place and self.map.pins[place]
	if pin then
		self.map:Focus(pin.place.x, pin.place.z)
	end
end

function JournalWindow:Destroy()
	self.maid:Clean()
end

return JournalWindow
