-- Top-left party frames: up to three tribe-mates, each with a headshot, name and
-- health bar. Display only; HudController feeds the members.

local Layout = require(script.Parent.Layout)
local Widgets = require(script.Parent.Widgets)

local PartyFrames = {}
PartyFrames.__index = PartyFrames

function PartyFrames.new(parent: Instance, layout)
	local cfg = layout.party
	local self = setmetatable({ rows = {} }, PartyFrames)
	self.root = Widgets.Make("Frame", { Name = "Party", BackgroundTransparency = 1 }, parent)
	Layout.Place(self.root, {
		anchor = cfg.anchor,
		pos = cfg.pos,
		size = { cfg.size[1], cfg.pitch * (cfg.maxRows - 1) + cfg.size[2] },
	})
	for index = 1, cfg.maxRows do
		local row = Widgets.Panel(cfg, {
			Name = "Member" .. index,
			Position = UDim2.fromOffset(0, (index - 1) * cfg.pitch),
			Size = UDim2.fromOffset(cfg.size[1], cfg.size[2]),
			Visible = false,
		}, self.root)
		local rect = cfg.portrait.rect
		local portrait = Widgets.Make("ImageLabel", {
			Name = "Headshot",
			BackgroundColor3 = Layout.Color("fallbackFill"),
			Position = Layout.Position(rect),
			Size = Layout.Size(rect),
			ScaleType = Enum.ScaleType.Crop,
			ZIndex = 4,
		}, row)
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 6) }, portrait)
		Widgets.Make("UIStroke", { Color = Layout.Color("outline"), Thickness = 2 }, portrait)
		local name = Widgets.Text(cfg.name, {
			Name = "MemberName",
			Position = Layout.Position(cfg.name.rect),
			Size = Layout.Size(cfg.name.rect),
		}, row)
		local bar = Widgets.Bar(cfg.bar, row)
		self.rows[index] = { root = row, portrait = portrait, name = name, bar = bar, userId = nil }
	end
	return self
end

-- members: array of {userId, name, health (0–1), thumbnail?}; extra rows hide.
function PartyFrames:Set(members, instant: boolean?)
	for index, row in self.rows do
		local member = members[index]
		row.root.Visible = member ~= nil
		if member then
			local changed = row.userId ~= member.userId
			row.userId = member.userId
			row.name.Text = member.name
			row.portrait.Image = member.thumbnail or ""
			Widgets.SetBar(row.bar, member.health, instant or changed)
		else
			row.userId = nil
		end
	end
	self.root.Visible = members[1] ~= nil
end

return PartyFrames
