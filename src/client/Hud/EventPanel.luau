-- Top-right world event panel: storm icon, "World Event", the event's name, a
-- one-line description and its countdown. Hidden while no event runs. Fed by
-- HudModel.WorldEvent; display only.

local Layout = require(script.Parent.Layout)
local Widgets = require(script.Parent.Widgets)

local EventPanel = {}
EventPanel.__index = EventPanel

function EventPanel.new(parent: Instance, layout)
	local cfg = layout.event
	local self = setmetatable({}, EventPanel)
	self.root = Widgets.Panel(cfg, {
		Name = "WorldEvent",
		Size = UDim2.fromOffset(cfg.size[1], cfg.size[2]),
		Visible = false,
	}, parent)
	Layout.Place(self.root, cfg)
	Widgets.Sprite(cfg.icon.icon, {
		Name = "Icon",
		Position = Layout.Position(cfg.icon.rect),
		Size = Layout.Size(cfg.icon.rect),
		ZIndex = 4,
	}, self.root)
	local function text(name: string, entry, alignRight: boolean?)
		return Widgets.Text(entry, {
			Name = name,
			Position = Layout.Position(entry.rect),
			Size = Layout.Size(entry.rect),
			TextXAlignment = if alignRight then Enum.TextXAlignment.Right else Enum.TextXAlignment.Left,
		}, self.root)
	end
	self.title = text("Title", cfg.title)
	self.timer = text("Timer", cfg.timer, true)
	self.name = text("EventName", cfg.name)
	self.description = text("Description", cfg.description)
	return self
end

-- panel: HudModel.WorldEvent(...) or nil to hide.
function EventPanel:Set(panel)
	self.root.Visible = panel ~= nil
	if panel then
		self.title.Text = panel.title
		self.timer.Text = panel.timer
		self.name.Text = panel.name
		self.description.Text = panel.description
	end
end

return EventPanel
