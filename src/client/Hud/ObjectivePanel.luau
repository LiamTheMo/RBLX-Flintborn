-- Top-right objective card ("FIND EXTRACTION"): a Kit.Panel "card" with a
-- section header (exit icon and the title) and up to two task lines, each the
-- quest journal's round check (Kit.Checkbox "ring", read only), the task, a
-- map pin and distance, and the progress at the right. Fed by
-- HudModel.ExtractionObjective; display only.

local Kit = require(script.Parent.Kit)
local Layout = require(script.Parent.Layout)

local ObjectivePanel = {}
ObjectivePanel.__index = ObjectivePanel

function ObjectivePanel.new(parent: Instance, layout)
	local cfg = layout.objective
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
	for index = 1, 2 do
		local y = cfg.rowTop + (index - 1) * cfg.rowHeight
		local rh = cfg.rowHeight
		local check = Kit.Checkbox.new(body, {
			name = "Check" .. index,
			rect = { x, y + (rh - cfg.check) / 2, cfg.check, cfg.check },
			variant = "ring",
			readOnly = true,
			checked = false,
			zIndex = 8,
		})
		local text = Kit.Text.new(body, {
			name = "Task" .. index,
			rect = { x + cfg.check + 8, y, cfg.textW, rh },
			text = "",
			role = "rowLabel",
			textSize = cfg.textSize,
			scaled = true,
			zIndex = 8,
		})
		local progress = Kit.Text.new(body, {
			name = "Progress",
			rect = { x + rowW - cfg.progressW, y, cfg.progressW, rh },
			text = "",
			role = "value",
			textSize = cfg.textSize,
			align = "Right",
			scaled = true,
			zIndex = 8,
		})
		local pinX = x + rowW - cfg.progressW - cfg.distanceW - cfg.pin
		local pin = Kit.Icon.new(body, {
			name = "Pin",
			rect = { pinX, y + (rh - cfg.pin) / 2, cfg.pin, cfg.pin },
			icon = "map_pin",
			zIndex = 8,
		})
		local distance = Kit.Text.new(body, {
			name = "Distance",
			rect = { pinX + cfg.pin + 2, y, cfg.distanceW - 4, rh },
			text = "",
			role = "small",
			textSize = cfg.textSize,
			scaled = true,
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
			x = x + cfg.check + 8,
			narrow = cfg.textW,
			wide = rowW - cfg.check - 8 - cfg.progressW - 6,
		}
	end
	return self
end

-- model: HudModel.ExtractionObjective(...)
function ObjectivePanel:Set(model)
	if model.title ~= self.titleText then
		self.titleText = model.title
		self.header:SetText(model.title)
		-- The header label was sized for its first text; give it the row.
		local label = self.header.label
		label.Size = UDim2.fromOffset(self.cfg.header[3] - label.Position.X.Offset, label.Size.Y.Offset)
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
