-- Top-right world event card: a Kit.Panel "card" with a section header (the
-- event category's icon, "WORLD EVENT" and the countdown as its count), the
-- event's name and a wrapped line naming its rarity, what it is and where.
-- Hidden while no event runs. Fed by HudModel.WorldEvent; display only.

local Kit = require(script.Parent.Kit)
local Layout = require(script.Parent.Layout)

local EventPanel = {}
EventPanel.__index = EventPanel

-- Header icon per event category (the server view's `category`).
EventPanel.ICONS = {
	Vegetation = "plant_fiber",
	Ore = "magma_ore",
	Npc = "paw",
	Cache = "chest",
	Meteor = "crystals",
	Structure = "ruin",
	Boss = "tusk",
}
EventPanel.DEFAULT_ICON = "warning"

function EventPanel.new(parent: Instance, layout)
	local cfg = layout.event
	local self = setmetatable({ cfg = cfg, icon = nil }, EventPanel)
	self.root = Instance.new("Frame")
	self.root.Name = "WorldEvent"
	self.root.BackgroundTransparency = 1
	self.root.Visible = false
	Layout.Place(self.root, cfg)
	self.root.Parent = parent
	local w, h = cfg.size[1], cfg.size[2]
	self.panel = Kit.Panel.new(self.root, { name = "Panel", rect = { 0, 0, w, h }, variant = "card", pad = 0 })
	self.body = self.panel:Content()
	self:_header(EventPanel.DEFAULT_ICON)
	local x, rowW = cfg.header[1], cfg.header[3]
	self.name = Kit.Text.new(self.body, {
		name = "EventName",
		rect = { x, cfg.nameY, rowW, cfg.nameH },
		text = "",
		role = "rowTitle",
		scaled = true,
		zIndex = 8,
	})
	self.description = Kit.Text.new(self.body, {
		name = "Description",
		rect = { x, cfg.descriptionY, rowW, cfg.descriptionH },
		text = "",
		role = "bodySoft",
		textSize = cfg.descriptionSize,
		yAlign = "Top",
		wrap = true,
		zIndex = 8,
	})
	return self
end

function EventPanel:_header(icon: string)
	if self.header then
		self.header:Destroy()
	end
	self.icon = icon
	self.header = Kit.SectionHeader.new(self.body, {
		name = "Header",
		rect = self.cfg.header,
		text = "World Event",
		icon = icon,
		count = "",
		zIndex = 8,
	})
	-- The countdown sits at the header's right end.
	local count = self.header.count
	if count then
		count.TextXAlignment = Enum.TextXAlignment.Right
		count.Position = UDim2.fromOffset(self.cfg.header[3] - 120, 0)
	end
end

-- panel: HudModel.WorldEvent(...) or nil to hide; category picks the icon.
function EventPanel:Set(panel, category: string?)
	self.root.Visible = panel ~= nil
	if panel == nil then
		return
	end
	local icon = EventPanel.ICONS[category or ""] or EventPanel.DEFAULT_ICON
	if icon ~= self.icon then
		self:_header(icon)
	end
	self.header:SetText(panel.title)
	self.header:SetCount(panel.timer)
	self.name:SetText(panel.name)
	self.description:SetText(panel.description)
end

return EventPanel
