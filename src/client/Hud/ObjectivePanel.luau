-- Top-right objective card ("FIND EXTRACTION"): a Kit.Panel "card" with a
-- section header (exit icon and the title) and up to two task lines, each the
-- quest journal's round check (Kit.Checkbox "ring", read only), the task, a
-- map pin and distance, and the progress at the right. On phones and tablets
-- (the layout's "twoLine") each task takes two lines, so its words keep the 9 px floor: the
-- task on the first, the pin, distance and progress under it; a task too long
-- for the line ends in "…". Fed by HudModel.ExtractionObjective; display only.

local Kit = require(script.Parent.Kit)
local Layout = require(script.Parent.Layout)

local ObjectivePanel = {}
ObjectivePanel.__index = ObjectivePanel

function ObjectivePanel.new(parent: Instance, layout)
	local cfg = Layout.Section(layout, "objective")
	local self = setmetatable({ cfg = cfg, rows = {}, titleText = nil }, ObjectivePanel)
	self.root = Instance.new("Frame")
	self.root.Name = "Objective"
	self.root.BackgroundTransparency = 1
	Layout.Place(self.root, cfg)
	self.root.Parent = parent
	local w, h = cfg.size[1], cfg.size[2]
	self.panel = Kit.Panel.new(self.root, { name = "Panel", rect = { 0, 0, w, h }, variant = "card", pad = 0 })
	local body = self.panel:Content()
	self.header = Kit.SectionHeader.new(body, {
		name = "Header",
		rect = cfg.header,
		text = "Find Extraction",
		icon = "exit",
		zIndex = 8,
	})
	local x, rowW = cfg.header[1], cfg.header[3]
	local twoLine = cfg.twoLine == true
	self.twoLine = twoLine
	for index = 1, 2 do
		local y = cfg.rowTop + (index - 1) * cfg.rowHeight
		local rh = cfg.rowHeight
		-- One line per row, or (twoLine) the task line and the detail line.
		local lineH = if twoLine then rh / 2 else rh
		local detailY = if twoLine then y + lineH else y
		local textX = x + cfg.check + 8
		local check = Kit.Checkbox.new(body, {
			name = "Check" .. index,
			rect = { x, y + (lineH - cfg.check) / 2, cfg.check, cfg.check },
			variant = "ring",
			readOnly = true,
			checked = false,
			zIndex = 8,
		})
		local wide = rowW - cfg.check - 8
		local text = Kit.Text.new(body, {
			name = "Task" .. index,
			rect = { textX, y, if twoLine then wide else cfg.textW, lineH },
			text = "",
			role = "rowLabel",
			textSize = cfg.textSize,
			scaled = not twoLine,
			zIndex = 8,
		})
		local progress = Kit.Text.new(body, {
			name = "Progress",
			rect = { x + rowW - cfg.progressW, detailY, cfg.progressW, lineH },
			text = "",
			role = "value",
			textSize = cfg.textSize,
			align = "Right",
			scaled = not twoLine,
			zIndex = 8,
		})
		local pinX = if twoLine then textX else x + rowW - cfg.progressW - cfg.distanceW - cfg.pin
		local pin = Kit.Icon.new(body, {
			name = "Pin",
			rect = { pinX, detailY + (lineH - cfg.pin) / 2, cfg.pin, cfg.pin },
			icon = "map_pin",
			zIndex = 8,
		})
		local distanceW = if twoLine then rowW - cfg.check - 8 - cfg.pin - 2 - cfg.progressW - 6 else cfg.distanceW - 4
		local distance = Kit.Text.new(body, {
			name = "Distance",
			rect = { pinX + cfg.pin + 2, detailY, distanceW, lineH },
			text = "",
			role = "small",
			textSize = cfg.textSize,
			scaled = not twoLine,
			zIndex = 8,
		})
		local rule = Kit.Divider.new(body, {
			name = "Rule",
			rect = { x, y + rh - 1, rowW, 2 },
			variant = "hairline",
			zIndex = 7,
		})
		rule.root.Visible = index == 1
		self.rows[index] = {
			check = check,
			text = text,
			progress = progress,
			pin = pin,
			distance = distance,
			rule = rule,
			x = textX,
			narrow = if twoLine then wide else cfg.textW,
			wide = if twoLine then wide else rowW - cfg.check - 8 - cfg.progressW - 6,
		}
	end
	return self
end

-- One-line rows shrink a task to fit, but no further than SHRINK of its size;
-- a task still too long then keeps that size and ends in "…".
ObjectivePanel.SHRINK = 0.7

function ObjectivePanel.Fit(label: TextLabel, text: string, width: number, size: number)
	local least = size * ObjectivePanel.SHRINK
	local fits = Kit.Text.Width(text, "rowLabel", least) <= width
	label.TextScaled = fits
	if not fits then
		label.TextSize = least * Kit.Core.TextBoost("rowLabel")
		label.TextTruncate = Enum.TextTruncate.AtEnd
	end
end

-- model: HudModel.ExtractionObjective(...)
function ObjectivePanel:Set(model)
	if model.title ~= self.titleText then
		self.titleText = model.title
		self.header:SetText(model.title)
		-- The header label was sized for its first text; give it the row, and a
		-- smaller size when the title (1.2 × on touch screens) would not fit.
		local label = self.header.label
		local room = self.cfg.header[3] - label.Position.X.Offset
		label.Size = UDim2.fromOffset(room, label.Size.Y.Offset)
		local size = Kit.Tokens.TextStyle("sectionHeader").size
		local need = Kit.Text.Width(model.title, "sectionHeader", size) * 1.04 + 4
		if need > room then
			size = math.floor(size * room / need)
		end
		label.TextSize = size * Kit.Core.TextBoost("sectionHeader")
	end
	for index, row in self.rows do
		local line = model.lines[index]
		local visible = line ~= nil
		local hasDistance = visible and line.distance ~= nil
		row.check.root.Visible = visible
		row.text.root.Visible = visible
		row.progress.root.Visible = visible
		row.pin.root.Visible = hasDistance
		row.distance.root.Visible = hasDistance
		if line then
			row.text:SetText(line.text)
			-- Without a distance the task text may use the free space.
			local width = if hasDistance then row.narrow else row.wide
			row.text.root.Size = UDim2.fromOffset(width, row.text.root.Size.Y.Offset)
			if not self.twoLine then
				ObjectivePanel.Fit(row.text.root, line.text, width, self.cfg.textSize)
			end
			row.distance:SetText(line.distance or "")
			row.progress:SetText(line.progress)
			row.check:SetChecked(line.done == true)
		end
		if index == 1 then
			row.rule.root.Visible = model.lines[2] ~= nil
		end
	end
end

return ObjectivePanel
