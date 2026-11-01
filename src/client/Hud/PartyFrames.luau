-- Top-left tribe frames: the lobby party panel's card (Kit.Panel "card" with a
-- "TRIBE n" section header) listing up to the layout's row count of tribe-mates
-- on this server, each a compact Kit.PlayerRow (headshot, name) with a small
-- Kit health bar under the name. Long names shrink a little on bigger screens;
-- on phones and tablets (at the 9 px floor) they keep their size and the strip's
-- cells widen for the longest name (up to the layout's cellMaxW; only a name
-- longer than that ends in "…").
-- Hidden while no tribe-mate is here. Display only; HudController feeds the
-- members. On phones (the layout's "strip") the members sit side by side in
-- one short card under the compass, with the tribe icon and count at its left,
-- so the frames stay above the thumbstick's zone and clear of the jump button.

local Kit = require(script.Parent.Kit)
local Layout = require(script.Parent.Layout)

local PartyFrames = {}
PartyFrames.__index = PartyFrames

function PartyFrames.new(parent: Instance, layout)
	local cfg = Layout.Section(layout, "party")
	local self = setmetatable(
		{ cfg = cfg, rows = {}, shown = 0, cellW = cfg.cellW, shrink = not Layout.IsTouchScreen() },
		PartyFrames
	)
	self.root = Instance.new("Frame")
	self.root.Name = "Party"
	self.root.BackgroundTransparency = 1
	self.root.Visible = false
	Layout.Place(self.root, {
		anchor = cfg.anchor,
		pos = cfg.pos,
		size = { PartyFrames.Width(cfg, 1, cfg.cellW), PartyFrames.Height(cfg, 1) },
	})
	self.root.Parent = parent
	return self
end

-- The panel's height for `count` rows (a strip: one row).
function PartyFrames.Height(cfg, count: number): number
	if cfg.strip then
		return cfg.height
	end
	return cfg.listTop + count * cfg.rowHeight + cfg.padBottom
end

-- The panel's width for `count` members `cellW` wide each (a strip grows
-- sideways; cellW defaults to the layout's).
function PartyFrames.Width(cfg, count: number, cellW: number?): number
	if cfg.strip then
		return cfg.cellX + count * (cellW or cfg.cellW) + 10
	end
	return cfg.width
end

-- A strip cell's width for `members`' names: the layout's, widened so the
-- longest name shows whole at its size beside the headshot (with the kit's
-- fit slack), up to cellMaxW.
function PartyFrames.CellWidth(cfg, members, count: number): number
	if not cfg.strip then
		return cfg.cellW
	end
	local need = 0
	for index = 1, count do
		local name = members[index].name or ""
		need = math.max(need, Kit.Text.Width(name, "rowTitle", Kit.Core.TextFloor(15)) / (1 - Kit.Core.FIT_SLACK))
	end
	-- The cell's gap (8), the row's right margin (4) and the name's x
	-- (headshot + 14).
	local width = math.ceil(need) + 8 + 4 + cfg.portrait + 14
	return math.clamp(width, cfg.cellW, cfg.cellMaxW or cfg.cellW)
end

-- Rebuilds the card for `count` rows (the plate is drawn at its size).
function PartyFrames:_build(count: number, cellW: number)
	local cfg = self.cfg
	self.cellW = cellW
	if self.panel then
		self.panel:Destroy()
	end
	table.clear(self.rows)
	local h = PartyFrames.Height(cfg, count)
	local width = PartyFrames.Width(cfg, count, cellW)
	self.root.Size = UDim2.fromOffset(width, h)
	self.panel = Kit.Panel.new(self.root, { name = "Panel", rect = { 0, 0, width, h }, variant = "card", pad = 0 })
	local body = self.panel:Content()
	local x, w = cfg.header[1], cfg.header[3]
	if cfg.strip then
		-- The tribe icon and the count, then one cell per member.
		local s = h - 18
		Kit.Icon.new(body, { name = "TribeIcon", rect = { 14, 9, s, s }, icon = "party", zIndex = 8 })
		self.countText = Kit.Text.new(body, {
			name = "Count",
			rect = { 14 + s + 4, 0, cfg.cellX - s - 20, h },
			text = "",
			role = "sectionHeader",
			zIndex = 8,
		})
		self.header = nil
		w = cellW - 8
	else
		self.countText = nil
		self.header = Kit.SectionHeader.new(body, {
			name = "Header",
			rect = cfg.header,
			text = "Tribe",
			icon = "party",
			count = "",
			zIndex = 8,
		})
	end
	for index = 1, count do
		local rx, y = x, cfg.listTop + (index - 1) * cfg.rowHeight
		if cfg.strip then
			rx, y = cfg.cellX + (index - 1) * cellW, 0
		end
		local holder = Instance.new("Frame")
		holder.Name = "Member" .. index
		holder.BackgroundTransparency = 1
		holder.Position = UDim2.fromOffset(rx, y)
		holder.Size = UDim2.fromOffset(w, if cfg.strip then h else cfg.rowHeight)
		holder.Parent = body
		local bar = Kit.Bar.new(holder, {
			name = "Health",
			rect = { cfg.barX, cfg.barY, w - cfg.barX - 4, cfg.barH },
			fill = "health",
			zIndex = 10,
		})
		self.rows[index] = { holder = holder, bar = bar, row = nil, userId = nil, name = nil }
	end
	self.shown = count
end

-- members: array of {userId, name, health (0–1)}; total: tribe-mates on this
-- server (the header count; rows stop at the layout's maximum).
function PartyFrames:Set(members, instant: boolean?, total: number?)
	local count = math.min(#members, self.cfg.maxRows)
	self.root.Visible = count > 0
	if count == 0 then
		return
	end
	local cellW = PartyFrames.CellWidth(self.cfg, members, count)
	if count ~= self.shown or cellW ~= self.cellW then
		self:_build(count, cellW)
	end
	if self.header then
		self.header:SetCount(tostring(total or #members))
	else
		self.countText:SetText(tostring(total or #members))
	end
	local cfg = self.cfg
	for index, entry in self.rows do
		local member = members[index]
		local changed = entry.userId ~= member.userId or entry.name ~= member.name
		if changed then
			if entry.row then
				entry.row:Destroy()
			end
			entry.row = Kit.PlayerRow.new(entry.holder, {
				-- PlayerRow names its root after the player (`name` is both).
				name = member.name,
				rect = if cfg.strip
					then { 0, 0, self.cellW - 8, cfg.height }
					else { 0, 0, cfg.header[3], cfg.rowHeight },
				userId = member.userId,
				compact = true,
				shrinkName = self.shrink,
				portraitSize = cfg.portrait,
				rule = if index < count and not cfg.strip then "hairline" else false,
				zIndex = 8,
			})
			-- The name sits over the health bar instead of centred on the row.
			local label = entry.row.content:FindFirstChild("Name")
			if label and label:IsA("TextLabel") then
				label.Position = UDim2.fromOffset(label.Position.X.Offset, cfg.nameY)
				label.Size = UDim2.fromOffset(label.Size.X.Offset, cfg.nameH)
				label.TextYAlignment = Enum.TextYAlignment.Bottom
			end
			entry.userId = member.userId
			entry.name = member.name
		end
		entry.bar:Set(member.health, instant or changed)
	end
end

return PartyFrames
