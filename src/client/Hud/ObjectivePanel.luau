-- Top-right objective panel ("FIND EXTRACTION"): a waypoint icon, title and up to
-- two task lines with a checkbox, distance and progress. Fed by
-- HudModel.ExtractionObjective; display only.

local Layout = require(script.Parent.Layout)
local Widgets = require(script.Parent.Widgets)

local ObjectivePanel = {}
ObjectivePanel.__index = ObjectivePanel

local function checkbox(parent, x: number, size: number, centreY: number)
	local box = Widgets.Make("Frame", {
		Name = "Check",
		AnchorPoint = Vector2.new(0, 0.5),
		Position = UDim2.fromOffset(x, centreY),
		Size = UDim2.fromOffset(size, size),
		BackgroundColor3 = Layout.Color("stamina"),
		BackgroundTransparency = 1,
		ZIndex = 4,
	}, parent)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, box)
	Widgets.Make("UIStroke", { Color = Layout.Color("text"), Thickness = 1.5 }, box)
	local tickMark = Widgets.Make("TextLabel", {
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		Text = "✓",
		TextColor3 = Layout.Color("text"),
		TextScaled = true,
		Font = Enum.Font.GothamBold,
		Visible = false,
		ZIndex = 5,
	}, box)
	return box, tickMark
end

function ObjectivePanel.new(parent: Instance, layout)
	local cfg = layout.objective
	local self = setmetatable({ rows = {} }, ObjectivePanel)
	self.root = Widgets.Panel(cfg, {
		Name = "Objective",
		Size = UDim2.fromOffset(cfg.size[1], cfg.size[2]),
	}, parent)
	Layout.Place(self.root, cfg)
	-- The extraction icon: a hollow gold diamond with a walking figure inside.
	local diamond = cfg.diamond
	local side = math.min(diamond.rect[3], diamond.rect[4]) / math.sqrt(2)
	local outline = Widgets.Make("Frame", {
		Name = "Diamond",
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(diamond.rect[1] + diamond.rect[3] / 2, diamond.rect[2] + diamond.rect[4] / 2),
		Rotation = 45,
		Size = UDim2.fromOffset(side, side),
		ZIndex = 4,
	}, self.root)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 2) }, outline)
	Widgets.Make("UIStroke", { Color = Layout.Color(diamond.color), Thickness = diamond.thickness }, outline)
	local figure = Widgets.Sprite(cfg.figure.icon, {
		Name = "Figure",
		Position = Layout.Position(cfg.figure.rect),
		Size = Layout.Size(cfg.figure.rect),
		ZIndex = 4,
	}, self.root)
	if figure:IsA("ImageLabel") then
		figure.ImageColor3 = Layout.Color(cfg.figure.tint)
	end
	local dividers = cfg.dividers
	for _, y in dividers.y do
		Widgets.Make("Frame", {
			Name = "Divider",
			BackgroundColor3 = Layout.Color(dividers.color),
			BackgroundTransparency = dividers.transparency,
			BorderSizePixel = 0,
			Position = UDim2.fromOffset(dividers.x, y),
			Size = UDim2.fromOffset(dividers.w, 1),
			ZIndex = 4,
		}, self.root)
	end
	self.title = Widgets.Text(cfg.title, {
		Name = "Title",
		Position = Layout.Position(cfg.title.rect),
		Size = Layout.Size(cfg.title.rect),
	}, self.root)
	for index, y in cfg.rows.y do
		local centreY = y + cfg.rows.h / 2
		local box, tickMark = checkbox(self.root, cfg.check.x, cfg.check.size, centreY)
		local text = Widgets.Text(cfg.text, {
			Name = "Task" .. index,
			Position = UDim2.fromOffset(cfg.text.x, y),
			Size = UDim2.fromOffset(cfg.text.w, cfg.rows.h),
		}, self.root)
		local pin = Widgets.Pin(Layout.Color(cfg.pin.color), {
			AnchorPoint = Vector2.new(0, 0.5),
			Position = UDim2.fromOffset(cfg.pin.x, centreY),
			Size = UDim2.fromOffset(cfg.pin.size[1], cfg.pin.size[2]),
		}, self.root)
		local distance = Widgets.Text(cfg.distance, {
			Name = "Distance",
			Position = UDim2.fromOffset(cfg.distance.x, y),
			Size = UDim2.fromOffset(cfg.distance.w, cfg.rows.h),
		}, self.root)
		local progress = Widgets.Text(cfg.progress, {
			Name = "Progress",
			AnchorPoint = Vector2.new(1, 0),
			Position = UDim2.fromOffset(cfg.progress.right, y),
			Size = UDim2.fromOffset(cfg.progress.w, cfg.rows.h),
			TextXAlignment = Enum.TextXAlignment.Right,
		}, self.root)
		self.rows[index] = {
			box = box,
			tickMark = tickMark,
			text = text,
			pin = pin,
			distance = distance,
			progress = progress,
			textWidth = cfg.text.w,
			wideWidth = cfg.progress.right - cfg.progress.w - cfg.text.x,
		}
	end
	return self
end

-- model: HudModel.ExtractionObjective(...)
function ObjectivePanel:Set(model)
	self.title.Text = model.title
	for index, row in self.rows do
		local line = model.lines[index]
		local visible = line ~= nil
		row.box.Visible = visible
		row.text.Visible = visible
		row.progress.Visible = visible
		row.pin.Visible = visible and line.distance ~= nil
		row.distance.Visible = visible and line.distance ~= nil
		if line then
			row.text.Text = line.text
			-- Without a distance the task text may use the free space.
			local width = if line.distance then row.textWidth else row.wideWidth
			row.text.Size = UDim2.fromOffset(width, row.text.Size.Y.Offset)
			row.distance.Text = line.distance or ""
			row.progress.Text = line.progress
			row.tickMark.Visible = line.done
			row.box.BackgroundTransparency = if line.done then 0 else 1
		end
	end
end

return ObjectivePanel
