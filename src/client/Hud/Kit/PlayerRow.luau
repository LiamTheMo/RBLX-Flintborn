-- A player row (sheets 01, 15; M04 party and invite lists, M05 party):
-- portrait, name, "LV. n" under it, a crown for the leader, a tag (Leader,
-- Ready, Not Ready) and an optional action button (Invite). The empty variant
-- is a muted disc and "Empty Slot". A rule runs under each row.
--
--   local row = Kit.PlayerRow.new(list, { size = { 330, 52 }, userId = id, name = "LiamTheMo",
--       level = 12, leader = true, badge = "leader" })
--   Kit.PlayerRow.new(list, { size = { 330, 52 }, name = "ForestRanger", level = 15,
--       action = { label = "Invite", onPress = invite } })
--   Kit.PlayerRow.new(list, { size = { 330, 52 }, empty = true })

local Art = require(script.Parent.Art)
local Badge = require(script.Parent.Badge)
local Button = require(script.Parent.Button)
local Core = require(script.Parent.Core)
local Divider = require(script.Parent.Divider)
local Interact = require(script.Parent.Interact)
local Portrait = require(script.Parent.Portrait)
local Text = require(script.Parent.Text)

local PlayerRow = {}
PlayerRow.__index = PlayerRow

-- props: rect | size, userId, name, level, leader (crown), badge ("leader" |
-- "ready" | "notReady"), action ({label, onPress, variant}), empty,
-- emptyText, rule (true), frame ("square" | "round"), onPress(row), zIndex, name.
function PlayerRow.new(parent: Instance, props)
	local w, h = Core.Size(props, 330, 52)
	local base = Core.Root(parent, "PlayerRow", "row.player", props, w, h)
	local self = setmetatable({ root = base.root, base = base, w = w, h = h, props = props }, PlayerRow)
	if props.rule ~= false then
		Divider.new(base.visual, { name = "Rule", rect = { 0, h - 8, w, 16 }, variant = "rule", zIndex = base.z })
	end
	self.content = Core.Make("Frame", {
		Name = "Content",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		ZIndex = base.z + 1,
	}, base.visual)
	self:Set(props)
	if props.onPress then
		-- A pressable row lights its plate under the pointer and when selected.
		self.highlight = Art.Plate(base.visual, "row.plate", w, h - 4, { z = base.z, rect = { -6, -2, w + 12, h - 4 } })
		self.highlight.holder.Visible = false
		self.control = Interact.attach(base, {
			pressScale = false,
			onPress = function()
				props.onPress(self)
			end,
			render = function(state)
				local lit = state ~= "normal" and state ~= "empty" and state ~= "disabled"
				self.highlight.holder.Visible = lit
				if lit then
					self.highlight:Show(state)
				end
				self.root:SetAttribute("KitState", if self.empty and state == "normal" then "empty" else state)
			end,
		})
	end
	return self
end

-- Redraws the row from `data` (same fields as the props).
function PlayerRow:Set(data)
	for _, child in self.content:GetChildren() do
		child:Destroy()
	end
	if self.action then
		self.action:Destroy()
		self.action = nil
	end
	local w, h = self.w, self.h
	local z = self.base.z + 1
	self.empty = data.empty == true
	self.root:SetAttribute("KitState", if self.empty then "empty" else "normal")
	local ps = h - 6
	if self.empty then
		local d = math.floor(h * 0.62)
		local disc = Core.Make("Frame", {
			Name = "EmptyDot",
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset((ps - d) / 2 + 2, (h - d) / 2 - 2),
			Size = UDim2.fromOffset(d, d),
			ZIndex = z,
		}, self.content)
		Art.Plate(disc, "portrait.empty", d, d, { z = z })
		Core.Label(self.content, {
			name = "Name",
			text = data.emptyText or "Empty Slot",
			role = "muted",
			rect = { ps + 16, 0, w - ps - 16, h - 4 },
			z = z,
		})
		return
	end
	self.portrait = Portrait.new(self.content, {
		name = "Portrait",
		rect = { 0, 1, ps, ps },
		userId = data.userId,
		frame = data.frame,
		zIndex = z,
	})
	local x = ps + 14
	local right = w - 4
	if data.action then
		local bw = math.max(96, math.ceil(Text.Width(data.action.label, "buttonS")) + 40)
		local bh = math.min(42, h - 10)
		self.action = Button.new(self.content, {
			name = "Action",
			variant = data.action.variant or "primary",
			sizeClass = "s",
			label = data.action.label,
			rect = { right - bw, (h - bh) / 2 - 2, bw, bh },
			zIndex = z + 1,
			onPress = data.action.onPress,
		})
		if data.action.enabled == false then
			self.action:SetEnabled(false)
		end
		right -= bw + 10
	end
	if data.badge then
		self.badge = Badge.new(self.content, {
			name = "Tag",
			variant = data.badge,
			rect = { 0, 0, 0, 32 },
			zIndex = z + 1,
		})
		local bw = self.badge.root.Size.X.Offset
		self.badge.root.Position = UDim2.fromOffset(right - bw, (h - 32) / 2 - 2)
		right -= bw + 10
	end
	if data.leader then
		local c = 28
		local crown = Core.Make("Frame", {
			Name = "Crown",
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(right - c, (h - c) / 2 - 2),
			Size = UDim2.fromOffset(c, c),
			ZIndex = z,
		}, self.content)
		Art.Plate(crown, "mark.crown", c, c, { z = z })
		right -= c + 10
	end
	local hasLevel = data.level ~= nil
	Core.Label(self.content, {
		name = "Name",
		text = data.name or "",
		role = "rowTitle",
		color = "ink",
		rect = if hasLevel then { x, h * 0.1, right - x, h * 0.46 } else { x, 0, right - x, h - 4 },
		z = z,
	})
	if hasLevel then
		Core.Label(self.content, {
			name = "Level",
			text = ("LV. %d"):format(data.level),
			role = "small",
			color = "inkBody",
			rect = { x, h * 0.54, right - x, h * 0.34 },
			z = z,
		})
	end
	if self.control then
		self.control:Refresh()
	end
end

function PlayerRow:SetSelected(selected: boolean)
	if self.control then
		self.control:SetSelected(selected)
	end
end

function PlayerRow:Destroy()
	if self.action then
		self.action:Destroy()
	end
	self.base.maid:Clean()
end

return PlayerRow
