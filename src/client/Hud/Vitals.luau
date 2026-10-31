-- Vitals: Health, Stamina and Food as the kit's composed stat bars (sheets 08,
-- 18, 20: icon tile, fill in its well, value plaque), stacked at the top right,
-- and a row of status plaques under them for the medicine lock, food healing
-- and hunger slow. A bar at or under the layout's `low` share shows a warning
-- mark over its icon tile and pulses the icon, so a low state never rests on
-- colour alone. Display only; HudController feeds the values.
--
--   local vitals = Vitals.new(root, layout)
--   vitals:Set("health", 0.85, "85/100")
--   vitals:SetStatus({ { icon = "hourglass", text = "Medicine 12.0 s" } })

local Kit = require(script.Parent.Kit)
local Layout = require(script.Parent.Layout)

local Vitals = {}
Vitals.__index = Vitals

function Vitals.new(parent: Instance, layout)
	local cfg = Layout.Section(layout, "vitals")
	local count = #cfg.rows
	local statusCfg = Layout.Section(layout, "status")
	local self = setmetatable({ rows = {}, low = cfg.low, statusCfg = statusCfg, chips = {} }, Vitals)
	self.root = Instance.new("Frame")
	self.root.Name = "Vitals"
	self.root.BackgroundTransparency = 1
	Layout.Place(self.root, {
		anchor = cfg.anchor,
		pos = cfg.pos,
		size = { cfg.size[1], cfg.pitch * (count - 1) + cfg.size[2] },
	})
	self.root.Parent = parent
	for index, rowCfg in cfg.rows do
		local bar = Kit.Bar.new(self.root, {
			name = rowCfg.label,
			rect = { 0, (index - 1) * cfg.pitch, cfg.size[1], cfg.size[2] },
			fill = rowCfg.fill,
			frame = "stat",
			icon = rowCfg.icon,
			text = "",
		})
		-- The low-state mark sits on the icon tile's corner.
		local mark = Kit.Icon.new(bar.root, {
			name = "Low",
			rect = { cfg.lowMark[1], cfg.lowMark[2], cfg.lowMark[3], cfg.lowMark[3] },
			icon = "warning",
			zIndex = 12,
		})
		mark.root.Visible = false
		self.rows[rowCfg.key] = { bar = bar, mark = mark, isLow = false }
	end

	-- Status plaques, right-aligned under the bars.
	self.status = Instance.new("Frame")
	self.status.Name = "SurvivalStatus"
	self.status.BackgroundTransparency = 1
	self.status.Visible = false
	Layout.Place(self.status, statusCfg)
	self.status.Parent = parent
	return self
end

-- key: "health" | "stamina" | "food"; valueText is the plaque's text ("85/100").
function Vitals:Set(key: string, fraction: number, valueText: string, instant: boolean?)
	local row = self.rows[key]
	if row == nil then
		return
	end
	row.bar:Set(fraction, instant)
	row.bar:SetText(valueText)
	local low = fraction <= self.low
	row.bar.root:SetAttribute("HudLow", low)
	if low == row.isLow then
		return
	end
	row.isLow = low
	row.mark.root.Visible = low
	if row.stopPulse then
		row.stopPulse()
		row.stopPulse = nil
	end
	local icon = row.bar.icon
	if low and icon and icon:IsA("ImageLabel") then
		row.stopPulse = Kit.Motion.Pulse(icon, "ImageTransparency", 0.45, 0)
	end
end

-- chips: array of {icon, text}; an empty array hides the row. Plaques are
-- rebuilt only when their texts change.
function Vitals:SetStatus(chips)
	local key = {}
	for _, chip in chips do
		table.insert(key, chip.icon .. "|" .. chip.text)
	end
	local signature = table.concat(key, "\n")
	if signature == self.signature then
		return
	end
	-- Same chips with new numbers (the medicine countdown): only the texts move.
	local sameShape = #chips == #self.chips
	for index, chip in chips do
		local old = self.chips[index]
		if not (old and old.icon == chip.icon and old.width == self:_chipWidth(chip.text)) then
			sameShape = false
		end
	end
	self.signature = signature
	self.status.Visible = #chips > 0
	if sameShape then
		for index, chip in chips do
			self.chips[index].text:SetText(chip.text)
		end
		return
	end
	for _, old in self.chips do
		old.panel:Destroy()
	end
	table.clear(self.chips)
	local cfg = self.statusCfg
	local h = cfg.size[2]
	local right = cfg.size[1]
	for index, chip in chips do
		local w = self:_chipWidth(chip.text)
		local panel = Kit.Panel.new(self.status, {
			name = "Status" .. index,
			rect = { right - w, 0, w, h },
			variant = "plaque",
			pad = 0,
		})
		local s = h - 12
		Kit.Icon.new(panel:Content(), { name = "Icon", rect = { 10, 6, s, s }, icon = chip.icon, zIndex = 8 })
		local text = Kit.Text.new(panel:Content(), {
			name = "Text",
			rect = { 14 + s, 0, w - s - 24, h },
			text = chip.text,
			role = "hudSmall",
			zIndex = 8,
		})
		table.insert(self.chips, { panel = panel, text = text, icon = chip.icon, width = w })
		right -= w + cfg.gap
	end
end

-- A plaque's width for its text, in steps of 20 px so a ticking number keeps it.
function Vitals:_chipWidth(text: string): number
	local h = self.statusCfg.size[2]
	local raw = Kit.Text.Width(text, "hudSmall") + h + 22
	return math.ceil(raw / 20) * 20
end

return Vitals
