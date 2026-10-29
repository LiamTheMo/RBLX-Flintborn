-- Vitals: Health, Stamina and Food rows (the parchment HUD draws each row as one
-- art piece, its icon plate and empty bar, with the coloured fill and number
-- over it; a row without art has an icon, label and track), plus a small status
-- pill for the medicine lock, food healing and hunger slow. Display only.

local Layout = require(script.Parent.Layout)
local Widgets = require(script.Parent.Widgets)

local Vitals = {}
Vitals.__index = Vitals

function Vitals.new(parent: Instance, layout)
	local cfg = layout.vitals
	local self = setmetatable({ rows = {} }, Vitals)
	self.root = Widgets.Panel(cfg, {
		Name = "Vitals",
		Size = UDim2.fromOffset(cfg.size[1], cfg.size[2]),
	}, parent)
	Layout.Place(self.root, cfg)
	for index, rowCfg in cfg.rows do
		local top = cfg.rowTop + (index - 1) * cfg.rowPitch
		local centreY = top + cfg.rowHeight / 2
		if rowCfg.art then
			Widgets.Sprite(rowCfg.art, {
				Name = rowCfg.label .. "Row",
				Position = UDim2.fromOffset(0, top),
				Size = UDim2.fromOffset(cfg.rowSize[1], cfg.rowSize[2]),
				ZIndex = 3,
			}, self.root)
		end
		if rowCfg.icon then
			Widgets.Sprite(rowCfg.icon, {
				Name = rowCfg.label .. "Icon",
				AnchorPoint = Vector2.new(0, 0.5),
				Position = UDim2.fromOffset(cfg.icon.x, centreY),
				Size = UDim2.fromOffset(cfg.icon.size, cfg.icon.size),
				ZIndex = 4,
			}, self.root)
		end
		if cfg.label then
			Widgets.Text(cfg.label, {
				Name = rowCfg.label .. "Label",
				Text = rowCfg.label,
				Position = UDim2.fromOffset(cfg.label.x, top),
				Size = UDim2.fromOffset(cfg.label.w, cfg.rowHeight),
			}, self.root)
		end
		local trackTop = centreY - cfg.track.h / 2
		local bar = Widgets.Bar({
			rect = { cfg.track.x, trackTop, cfg.track.w, cfg.track.h },
			inset = cfg.fillBar.inset,
			maxWidth = cfg.fillBar.w,
			track = cfg.track.sprite,
			fillColor = rowCfg.color,
		}, self.root)
		bar.root.Name = rowCfg.label .. "Bar"
		local value = Widgets.Text(cfg.value, {
			Name = rowCfg.label .. "Value",
			AnchorPoint = Vector2.new(1, 0),
			Position = UDim2.fromOffset(cfg.value.right, top),
			Size = UDim2.fromOffset(cfg.value.w, cfg.rowHeight),
			TextXAlignment = Enum.TextXAlignment.Right,
			ZIndex = 6,
		}, self.root)
		self.rows[rowCfg.key] = { bar = bar, value = value }
	end

	local statusCfg = layout.status
	self.status = Widgets.Make("Frame", {
		Name = "SurvivalStatus",
		BackgroundTransparency = 1,
		Visible = false,
	}, parent)
	Layout.Place(self.status, statusCfg)
	local pill = Widgets.Sprite(statusCfg.panel, {
		Name = "Pill",
		Size = UDim2.fromOffset(statusCfg.size[1], statusCfg.size[2]),
		ZIndex = 1,
	}, self.status)
	pill.Size = UDim2.fromScale(1, 1)
	self.statusText = Widgets.Text(statusCfg, {
		Name = "Text",
		Position = UDim2.fromOffset(10, 0),
		Size = UDim2.new(1, -20, 1, 0),
	}, self.status)
	return self
end

-- key: "health" | "stamina" | "food"
function Vitals:Set(key: string, fraction: number, valueText: string, instant: boolean?)
	local row = self.rows[key]
	if row then
		Widgets.SetBar(row.bar, fraction, instant)
		row.value.Text = valueText
	end
end

function Vitals:SetStatus(text: string)
	self.status.Visible = text ~= ""
	self.statusText.Text = text
end

return Vitals
