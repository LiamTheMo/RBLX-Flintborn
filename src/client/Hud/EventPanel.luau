-- Top-right world event card (on phones under the menu tiles at the top left,
-- clear of the Roblox jump button): a Kit.Panel "card" with a section header
-- (the event category's icon, "WORLD EVENT" and the countdown as its count),
-- the event's name, a wrapped line naming its rarity and what it is, and where
-- it is ("NE, 312 m") on a line of its own after a map pin, so a distance never
-- breaks across lines. The card grows with its text, up to the layout's
-- maxLines of description. Hidden while no event runs. Fed by
-- HudModel.WorldEvent; display only.

local Kit = require(script.Parent.Kit)
local Layout = require(script.Parent.Layout)
local NoticeCard = require(script.Parent.NoticeCard)

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
-- Below the last line of text.
EventPanel.PAD_BOTTOM = 14
-- Line height as a share of the drawn text size.
EventPanel.LINE = 1.3

-- Splits HudModel.WorldEvent's description ("Rare · what · NE, 312 m  (+1
-- more)") into the words and the place ("NE, 312 m  (+1 more)"); a description
-- without a place comes back whole.
function EventPanel.SplitPlace(description: string): (string, string?)
	local parts = string.split(description, " · ")
	local last = parts[#parts]
	if #parts >= 2 and string.match(last, "^%u%u?, ") then
		table.remove(parts)
		return table.concat(parts, " · "), last
	end
	return description, nil
end

function EventPanel.new(parent: Instance, layout)
	local cfg = Layout.Section(layout, "event")
	local self = setmetatable({ cfg = cfg, icon = nil, h = 0 }, EventPanel)
	self.root = Instance.new("Frame")
	self.root.Name = "WorldEvent"
	self.root.BackgroundTransparency = 1
	self.root.Visible = false
	Layout.Place(self.root, cfg)
	self.root.Parent = parent
	-- The words sit in their own frame over the card art, which is redrawn at
	-- the card's height.
	self.body = Kit.Core.Make("Frame", {
		Name = "Content",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		ZIndex = 8,
	}, self.root)
	self:_header(EventPanel.DEFAULT_ICON)
	local x, rowW = cfg.header[1], cfg.header[3]
	self.x, self.rowW = x, rowW
	self.name = Kit.Text.new(self.body, {
		name = "EventName",
		rect = { x, cfg.nameY, rowW, cfg.nameH },
		text = "",
		role = "rowTitle",
		-- Bigger screens shrink a long name; phones (at the 9 px floor) end it in "…".
		scaled = not Layout.IsPhone(),
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
	self.description.root.TextTruncate = Enum.TextTruncate.AtEnd
	local lineH = self:_lineHeight()
	self.pin = Kit.Icon.new(self.body, {
		name = "Pin",
		rect = { x, 0, 16, 16 },
		icon = "map_pin",
		zIndex = 8,
	})
	self.place = Kit.Text.new(self.body, {
		name = "Place",
		rect = { x + 20, 0, rowW - 20, lineH },
		text = "",
		role = "bodySoft",
		textSize = cfg.descriptionSize,
		zIndex = 8,
	})
	self:_layout("", nil)
	return self
end

-- One description line, in design px.
function EventPanel:_lineHeight(): number
	return math.ceil(self.cfg.descriptionSize * Kit.Core.TextBoost("bodySoft") * EventPanel.LINE)
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

-- Sizes the description and place lines for their text and redraws the card
-- art when its height changes.
function EventPanel:_layout(words: string, place: string?)
	local cfg = self.cfg
	local lineH = self:_lineHeight()
	local lines = if words == ""
		then 0
		else math.min(NoticeCard.Lines(words, "bodySoft", self.rowW * 0.95, cfg.descriptionSize), cfg.maxLines or 3)
	local y = cfg.descriptionY
	self.description.root.Visible = lines > 0
	self.description.root.Size = UDim2.fromOffset(self.rowW, lines * lineH)
	y += lines * lineH
	local hasPlace = place ~= nil
	self.pin.root.Visible = hasPlace
	self.place.root.Visible = hasPlace
	if hasPlace then
		self.place.root.Position = UDim2.fromOffset(self.x + 20, y)
		self.pin.root.Position = UDim2.fromOffset(self.x, y + (lineH - 16) / 2)
		y += lineH
	end
	local h = math.max(y + EventPanel.PAD_BOTTOM, cfg.size[2])
	if h ~= self.h then
		self.h = h
		self.root.Size = UDim2.fromOffset(cfg.size[1], h)
		if self.panel then
			self.panel:Destroy()
		end
		self.panel = Kit.Panel.new(self.root, {
			name = "Panel",
			rect = { 0, 0, cfg.size[1], h },
			variant = "card",
			pad = 0,
			zIndex = 2,
		})
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
	local words, place = EventPanel.SplitPlace(panel.description or "")
	if words ~= self.words or place ~= self.placeText then
		self.words, self.placeText = words, place
		self.description:SetText(words)
		self.place:SetText(place or "")
		self:_layout(words, place)
	end
end

return EventPanel
