-- The Quest Journal window (art/reference/ui/lobby/07_quest_journal.png, spec
-- docs/ui/JournalScreen.md, ARCHITECTURE §4.7 and D12), built only from the UI
-- kit. Two side tabs hang off the frame's left edge:
--   book    quests: the list (daily first, then main; each row tagged with
--           its group)
--           and the chosen quest's page: illustration, name, description,
--           OBJECTIVES with progress and a check, REWARDS tiles, CLAIM, and the
--           QUEST PROGRESS bar along the bottom
--   trophy  progression, read-only, in the same layout (level, masteries,
--           titles; ProgressionController's snapshot)
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

local JournalWindow = {}
JournalWindow.__index = JournalWindow

JournalWindow.FRAME = { 1072, 688 }
JournalWindow.MARGIN = 50
JournalWindow.SIZE = { 1072 + 2 * 50, 688 }

-- Side tabs: {id, y}.
JournalWindow.TAB_X = -45
JournalWindow.TAB_SIZE = { 82, 84 }
JournalWindow.TAB_YS = { quests = 101, progress = 195 }

local Z = 8
-- The mockup's 357 × 95 quest cards at a 104 px pitch (the kit's soft row draws
-- its edge on its rect).
local ROW = { 357, 95 }
local ROW_GAP = 9
-- The thin rail sits on the mockup's scroll rule (x 735).
local LIST = { 59, 101, 379, 515 }
local OBJECTIVE = { 594, 62 }
local OBJECTIVE_GAP = 3
local OBJECTIVES = { 450, 278, 608, 199 }
-- Where a quest row's title and subtitle lines start.
local QUEST_TEXT_Y = { 5, 39 }
local OBJECTIVE_SUBTITLE_Y = 31
local TILE = { 92, 104 }
local TILE_PITCH = 98
-- How wide a reward amount may be before the icon steps aside for it.
local REWARD_AMOUNT_ROOM = 34

-- parent: where the ScreenGui goes (PlayerGui by default). handlers: onClose(),
-- onTab(id), onSelect(id), onClaim(id).
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
	-- The header: the compass (the kit's full-colour icon, not the mockup's flat
	-- glyph), QUEST JOURNAL, the rule under both the full width, and the ✕.
	local window = Kit.Window.new(screen.window, {
		-- The kit draws the frame on its rect: 3 px shorter matches M07's frame.
		rect = { JournalWindow.MARGIN, 0, JournalWindow.FRAME[1], JournalWindow.FRAME[2] - 3 },
		title = "Quest Journal",
		icon = "compass",
		iconRect = { 64, 9, 84, 88 },
		titleRect = { 155, 16, 700, 70 },
		titleSize = 47,
		rule = "full",
		ruleRect = { 39, 92, 992, 2 },
		closeRect = { 995, 20, 60, 60 },
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
	local v = window.base.visual
	self.visual = v
	self:_tabs(v)
	self:_entriesPage(v)
	self:_footer(v)
	self:SelectTab("quests")
	return self
end

function JournalWindow:_tabs(v: Frame)
	local tabs = {}
	self.tabs = {}
	for _, id in JournalModel.TABS do
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
			iconSize = 50,
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
	-- The mockup's thin rules: left of the list, and the scroll rule the
	-- list's thin rail runs on.
	Kit.Divider.new(page, { name = "ListRule", rect = { 50, 110, 2, 506 }, variant = "hairline", zIndex = Z })
	Kit.Divider.new(page, { name = "ScrollRule", rect = { 434, 110, 2, 506 }, variant = "hairline", zIndex = Z })
	self.list = Kit.Scroll.new(page, {
		name = "Quests",
		rect = LIST,
		gap = ROW_GAP,
		padTop = 7,
		padBottom = 6,
		rail = "thin",
		zIndex = Z,
	})
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
	-- Shrinks to fit, and a long heading ("Gather 100 times in the Ancient
	-- Grove") wraps onto a second line rather than shrinking past the 9 px
	-- floor on phones; a short one keeps one line at the largest size.
	self.heading = Kit.Text.new(detail, {
		name = "Heading",
		rect = { 679, 108, 350, 54 },
		text = "",
		role = "detailTitle",
		textSize = 36,
		scaled = true,
		wrap = true,
		zIndex = Z,
	})
	-- Shrinks to fit its box (never into the OBJECTIVES rule below it) when a
	-- long description or the phone text boost would need a third line.
	self.description = Kit.Text.new(detail, {
		name = "Description",
		rect = { 684, 163, 350, 60 },
		text = "",
		role = "body",
		textSize = 18,
		wrap = true,
		scaled = true,
		yAlign = "Top",
		zIndex = Z,
	})
	self.description.root.LineHeight = 1.12
	Kit.Divider.new(detail, { name = "DetailRule", rect = { 455, 245, 587, 2 }, variant = "hairline", zIndex = Z })
	self.objectivesHead = Kit.Text.new(detail, {
		name = "ObjectivesHead",
		rect = { 455, 250, 300, 28 },
		text = "Objectives",
		role = "sectionHeader",
		textSize = 18,
		zIndex = Z,
	})
	self.objectives = Kit.Scroll.new(detail, {
		name = "Objectives",
		rect = OBJECTIVES,
		gap = OBJECTIVE_GAP,
		padBottom = 2,
		rail = "thin",
		zIndex = Z,
	})
	self.rewardsRule = Kit.Divider.new(detail, {
		name = "RewardsRule",
		rect = { 452, 477, 590, 2 },
		variant = "hairline",
		zIndex = Z,
	})
	self.rewardsHead = Kit.Text.new(detail, {
		name = "RewardsHead",
		rect = { 456, 480, 300, 28 },
		text = "Rewards",
		role = "sectionHeader",
		textSize = 18,
		zIndex = Z,
	})
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
	Kit.Divider.new(v, { name = "FooterRule", rect = { 50, 626, 980, 2 }, variant = "hairline", zIndex = Z })
	self.footerLabel = Kit.Text.new(v, {
		name = "ProgressLabel",
		rect = { 90, 634, 252, 32 },
		text = "",
		role = "sectionHeader",
		textSize = 17,
		align = "Right",
		zIndex = Z,
	})
	self.footerBar = Kit.Bar.new(v, { name = "ProgressBar", rect = { 357, 640, 375, 18 }, fill = "xp", zIndex = Z })
	self.footerText = Kit.Text.new(v, {
		name = "ProgressText",
		rect = { 749, 634, 300, 32 },
		text = "",
		role = "value",
		textSize = 19,
		zIndex = Z,
	})
end

-- The page shown under the tabs (quests or progress).
function JournalWindow:SelectTab(id: string)
	if self.tabs[id] == nil then
		return
	end
	self.tab = id
	self.tabGroup:Select(id)
	self:_draw()
end

function JournalWindow:Tab(): string
	return self.tab
end

-- The page a tab draws (JournalModel.QuestPage / ProgressPage).
function JournalWindow:SetPage(tab: string, page)
	self.pages[tab] = page
	if tab == self.tab then
		self:_draw()
	end
end

-- Chooses an entry on the current tab.
function JournalWindow:Select(id: string?)
	self.selected[self.tab] = id
	self:_draw()
	if self.handlers.onSelect then
		self.handlers.onSelect(id)
	end
end

-- The id chosen on `tab` (default: the shown one).
function JournalWindow:Selected(tab: string?): string?
	return self.selected[tab or self.tab]
end

function JournalWindow:_page()
	return self.pages[self.tab], self.tab
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

-- One list row: icon, title, line, chevron and the group tag ("Daily" /
-- "Main") in its top-right corner; on the icon's corner a red dot while a
-- reward waits and a check once it is claimed.
function JournalWindow:_row(content: Instance, entry, order: number)
	-- Phones and touch tablets: the tag and the line large enough for 9
	-- screen px at the window's phone scale (0.48–0.51 below the top bar).
	local phone = Kit.Scale.IsSmallTouch()
	local row = self.listParts:Give(Kit.ListRow.new(content, {
		name = entry.id,
		size = ROW,
		layoutOrder = order,
		variant = "soft",
		icon = entry.icon,
		iconRect = { 5, 11, 96, 72 },
		textX = 119,
		title = entry.title,
		titleSize = 19,
		-- A long title shrinks to fit rather than ending in "…".
		fitTitle = true,
		titleY = QUEST_TEXT_Y[1],
		subtitle = entry.subtitle,
		subtitleSize = if phone then 16 else 15,
		subtitleY = QUEST_TEXT_Y[2],
		chevron = true,
		zIndex = Z + 1,
		onPress = function()
			self:Select(entry.id)
		end,
	}))
	row:SetSelected(entry.id == self.selected[self.tab])
	local v = row.base.visual
	if entry.tag then
		Kit.Text.new(v, {
			name = "Group",
			rect = if phone then { 224, 1, 120, 20 } else { 240, 3, 104, 16 },
			text = entry.tag,
			role = "tag",
			textSize = if phone then 16 else 12,
			color = "inkSoft",
			align = "Right",
			zIndex = Z + 3,
		})
	end
	if entry.status == "ready" then
		Kit.Badge.new(v, { name = "Ready", variant = "dot", rect = { 88, 7, 16, 16 }, zIndex = Z + 4 })
	elseif entry.status == "claimed" then
		Kit.Icon.new(v, { name = "Claimed", rect = { 82, 5, 26, 22 }, icon = "check", zIndex = Z + 4 })
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

-- One objective row: icon, title, description, n / m and the ring check.
function JournalWindow:_objective(content: Instance, objective, index: number)
	local hasCount = objective.count ~= nil and objective.needed ~= nil
	local row = self.detailParts:Give(Kit.ListRow.new(content, {
		name = "Objective" .. index,
		size = OBJECTIVE,
		layoutOrder = index,
		variant = "soft",
		icon = objective.icon,
		iconRect = { 12, 9, 54, 45 },
		textX = 86,
		title = objective.title,
		titleSize = 18,
		subtitle = objective.description,
		subtitleSize = if Kit.Scale.IsSmallTouch() then 16 else 14,
		value = if hasCount then ("%d / %d"):format(objective.count, objective.needed) else nil,
		valueSize = 19,
		trailing = 44,
		zIndex = Z + 1,
	}))
	row.subtitle.Position = UDim2.fromOffset(row.subtitle.Position.X.Offset, OBJECTIVE_SUBTITLE_Y)
	-- A display, not a control: the server decides when an objective is done.
	Kit.Checkbox.new(row:Trailing(), {
		name = "Check",
		rect = { 12, 17, 28, 28 },
		variant = "ring",
		readOnly = true,
		checked = objective.done == true,
		zIndex = Z + 3,
	})
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
	-- The amount sits on the icon's lower right corner, as the mockup draws
	-- it; a long one ("x250") moves the icon up and left so they never overlap.
	local amountW = Kit.Text.Width(reward.amount or "", "count", 18)
	local long = amountW > REWARD_AMOUNT_ROOM
	Kit.Icon.new(c, {
		name = "Icon",
		rect = if long then { 6, 6, 50, 44 } else { 12, 12, 58, 50 },
		icon = reward.icon,
		zIndex = Z + 1,
	})
	Kit.Text.new(c, {
		name = "Amount",
		rect = { 4, 55, TILE[1] - 12, 20 },
		text = reward.amount,
		role = "count",
		textSize = 18,
		align = "Right",
		zIndex = Z + 2,
	})
	Kit.Text.new(c, {
		name = "Label",
		rect = { 3, 75, TILE[1] - 6, 24 },
		text = reward.label,
		role = "value",
		textSize = 15,
		align = "Center",
		wrap = true,
		scaled = true,
		zIndex = Z + 2,
	})
end

function JournalWindow:Destroy()
	self.maid:Clean()
end

return JournalWindow
