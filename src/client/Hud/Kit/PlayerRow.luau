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
--   Kit.PlayerRow.new(list, { size = { 330, 52 }, userId = id, name = "LiamTheMo", levelBar = true })

local Players = game:GetService("Players")

local Art = require(script.Parent.Art)
local Badge = require(script.Parent.Badge)
local Bar = require(script.Parent.Bar)
local Button = require(script.Parent.Button)
local Core = require(script.Parent.Core)
local Divider = require(script.Parent.Divider)
local Interact = require(script.Parent.Interact)
local Motion = require(script.Parent.Motion)
local Portrait = require(script.Parent.Portrait)
local Scale = require(script.Parent.Scale)
local Text = require(script.Parent.Text)
local Tooltip = require(script.Parent.Tooltip)

local PlayerRow = {}
PlayerRow.__index = PlayerRow

-- props: rect | size, userId, name, level, leader (crown), badge ("leader" |
-- "ready" | "notReady"), status ("ready" | "notReady": a bare dot, compact
-- rows), action ({label, onPress, variant, enabled, size = {108, 45}}), empty,
-- emptyText, emptyIndent (px from the left to the disc), nameX, nameY, levelY
-- (line tops, px), badgeWidth / badgeHeight / badgeTextSize, nameSize,
-- levelSize, crownSize, portraitSize, shrinkName (true: long names shrink to
-- fit, down to minTextPx; false: "…"; default: shrink on desktop, "…" plus a
-- tooltip with the whole name on touch), compact (the HUD party list: smaller crown and
-- text, no level line), rule ("hairline" default; true = hairline, false,
-- or a Divider variant), frame ("none" default: the headshot fills its box with
-- no backdrop; "square" | "round"), backdrop (Portrait's), levelBar (true:
-- under the name "LV. n" and a small XP bar, compact rows too; the level and
-- `progress` (0-1) follow the player's Level / LevelProgress attributes while
-- they are in the server), progress, barHeight (px, default 8), onPress(row),
-- zIndex, name.
function PlayerRow.new(parent: Instance, props)
	local w, h = Core.Size(props, 330, 52)
	local base = Core.Root(parent, "PlayerRow", "row.player", props, w, h)
	local self = setmetatable({ root = base.root, base = base, w = w, h = h, props = props }, PlayerRow)
	if props.rule ~= false then
		local rule = if type(props.rule) == "string" then props.rule else "hairline"
		local native = rule == "ink" or rule == "hairline"
		Divider.new(base.visual, {
			name = "Rule",
			rect = if native then { 0, h - 2, w, 2 } else { 0, h - 8, w, 16 },
			variant = rule,
			zIndex = base.z,
		})
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
		-- The whole name when the row shows it cut short (touch).
		base.maid:Give(Tooltip.Attach(self, function()
			return if self.nameCut then self.fullName else nil
		end))
	end
	return self
end

-- Redraws the row from `data` (same fields as the props; layout options not
-- in `data` keep their constructor values).
function PlayerRow:Set(data)
	self:_unfollow()
	if self.levelBar then
		self.levelBar:Destroy()
		self.levelBar = nil
	end
	self.levelLabel = nil
	for _, child in self.content:GetChildren() do
		child:Destroy()
	end
	if self.action then
		self.action:Destroy()
		self.action = nil
	end
	local props = self.props
	local function opt(key: string): any
		local value = data[key]
		if value == nil then
			return props[key]
		end
		return value
	end
	local w, h = self.w, self.h
	local z = self.base.z + 1
	local compact = opt("compact") == true
	self.empty = data.empty == true
	self.root:SetAttribute("KitState", if self.empty then "empty" else "normal")
	local ps = opt("portraitSize") or (h - 6)
	local nameSize = opt("nameSize") or (if compact then 15 else nil)
	if self.empty then
		local d = math.floor(ps * (if compact then 0.6 else 0.66))
		local indent = opt("emptyIndent") or ((ps - d) / 2 + 2)
		local disc = Core.Make("Frame", {
			Name = "EmptyDot",
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(indent, (h - d) / 2 - 1),
			Size = UDim2.fromOffset(d, d),
			ZIndex = z,
		}, self.content)
		Art.Plate(disc, "portrait.empty", d, d, { z = z })
		local tx = opt("nameX") or (ps + 16)
		Core.Label(self.content, {
			name = "Name",
			text = data.emptyText or props.emptyText or "Empty Slot",
			role = "muted",
			size = nameSize,
			rect = { tx, 0, w - tx, h - 2 },
			z = z,
		})
		return
	end
	self.portrait = Portrait.new(self.content, {
		name = "Portrait",
		rect = { 0, (h - ps) / 2, ps, ps },
		userId = data.userId,
		frame = opt("frame") or "none",
		backdrop = if opt("backdrop") ~= nil then opt("backdrop") else false,
		zIndex = z,
	})
	local x = opt("nameX") or (ps + 14)
	local right = w - 4
	local action = data.action
	if action then
		local size = action.size
		local bw = if size then size[1] else math.max(96, math.ceil(Text.Width(action.label, "buttonS")) + 40)
		local bh = if size then size[2] else math.min(42, h - 10)
		self.action = Button.new(self.content, {
			name = "Action",
			variant = action.variant or "primary",
			sizeClass = "s",
			label = action.label,
			textSize = action.textSize,
			rect = { right - bw, (h - bh) / 2 - 1, bw, bh },
			zIndex = z + 1,
			onPress = action.onPress,
		})
		if action.enabled == false then
			self.action:SetEnabled(false)
		end
		right -= bw + 10
	end
	if data.badge then
		self.badge = Badge.new(self.content, {
			name = "Tag",
			variant = data.badge,
			rect = { 0, 0, opt("badgeWidth") or 0, opt("badgeHeight") or 32 },
			textSize = opt("badgeTextSize"),
			zIndex = z + 1,
		})
		local bw = self.badge.root.Size.X.Offset
		local bh = self.badge.root.Size.Y.Offset
		self.badge.root.Position = UDim2.fromOffset(right - bw, (h - bh) / 2 - 1)
		right -= bw + 10
	end
	local status = data.status
	if status then
		-- A bare status dot (the HUD party list).
		local d = if compact then 14 else 18
		local dot = Core.Make("Frame", {
			Name = "Status",
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(right - d, (h - d) / 2),
			Size = UDim2.fromOffset(d, d),
			ZIndex = z,
		}, self.content)
		Art.Plate(dot, if status == "ready" then "dot.green" else "dot.grey", d, d, { z = z })
		right -= d + 8
	end
	if data.leader then
		local c = opt("crownSize") or (if compact then 20 else 28)
		local crown = Core.Make("Frame", {
			Name = "Crown",
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(right - c, (h - c) / 2 - 1),
			Size = UDim2.fromOffset(c, c),
			ZIndex = z,
		}, self.content)
		Art.Plate(crown, "mark.crown", c, c, { z = z })
		right -= c + 8
	end
	local withBar = opt("levelBar") == true
	local hasLevel = withBar or (data.level ~= nil and not compact)
	-- shrinkName: true / false, or unset: shrink to fit (down to the text
	-- floor) on desktop, keep the size and end in "…" on touch, where a
	-- pressable row shows the whole name in a tooltip.
	local shrink = opt("shrinkName")
	if shrink == nil then
		shrink = not Scale.IsSmallTouch()
	end
	local nameRight = right
	self.fullName = data.name or ""
	self.nameCut = not shrink and Text.Width(self.fullName, "rowTitle", nameSize) > nameRight - x - 2
	Core.Label(self.content, {
		name = "Name",
		text = data.name or "",
		role = "rowTitle",
		size = nameSize,
		color = "ink",
		scaled = shrink,
		rect = if opt("nameY")
			then { x, opt("nameY"), right - x, h * 0.46 }
			elseif hasLevel then { x, h * 0.1, right - x, h * 0.46 }
			else { x, 0, right - x, h - 2 },
		z = z,
	})
	if hasLevel then
		local ly, lh = opt("levelY") or h * 0.54, h * 0.34
		self.levelLabel = Core.Label(self.content, {
			name = "Level",
			text = if data.level then ("LV. %d"):format(data.level) else "",
			role = "small",
			size = opt("levelSize"),
			color = "inkBody",
			rect = { x, ly, right - x, lh },
			z = z,
		})
		if withBar then
			self.barHeight = opt("barHeight") or 8
			self.levelSize = opt("levelSize")
			self.level, self.progress = data.level, opt("progress") or 0
			self:_buildBar()
			self:_follow(data.userId)
		end
	end
	if self.control then
		self.control:Refresh()
	end
end

-- The XP bar on the level line, after the label's text (rebuilt when the
-- text's width changes).
function PlayerRow:_buildBar()
	local label = self.levelLabel
	if self.levelBar then
		self.levelBar:Destroy()
	end
	local x, y = label.Position.X.Offset, label.Position.Y.Offset
	local lw, lh = label.Size.X.Offset, label.Size.Y.Offset
	local gap = if label.Text == "" then 0 else math.ceil(Text.Width(label.Text, "small", self.levelSize)) + 6
	local bh = self.barHeight
	self.levelBar = Bar.new(self.content, {
		name = "XpBar",
		rect = { x + gap, math.floor(y + (lh - bh) / 2 + 0.5), math.max(0, lw - gap), bh },
		fill = "xp",
		frame = "track",
		zIndex = label.ZIndex,
	})
	self.levelBar:Set(math.clamp(self.progress or 0, 0, 1), true)
end

-- Updates the level line and its XP bar in place (nil keeps a value).
function PlayerRow:SetLevel(level: number?, progress: number?)
	if not self.levelBar then
		return
	end
	self.level = level or self.level
	self.progress = progress or self.progress
	local text = if self.level then ("LV. %d"):format(self.level) else ""
	if self.levelLabel.Text ~= text then
		self.levelLabel.Text = text
		self:_buildBar()
	end
	self.levelBar:Set(math.clamp(self.progress or 0, 0, 1), Motion.Reduced())
end

-- Follows the player's replicated Level / LevelProgress attributes.
function PlayerRow:_follow(userId: number?)
	local player = if userId and userId > 0 then Players:GetPlayerByUserId(userId) else nil
	if not player then
		return
	end
	local function read()
		local level, progress = player:GetAttribute("Level"), player:GetAttribute("LevelProgress")
		self:SetLevel(
			if type(level) == "number" then level else nil,
			if type(progress) == "number" then progress else nil
		)
	end
	self.follows = {
		player:GetAttributeChangedSignal("Level"):Connect(read),
		player:GetAttributeChangedSignal("LevelProgress"):Connect(read),
	}
	read()
end

function PlayerRow:_unfollow()
	for _, connection in self.follows or {} do
		connection:Disconnect()
	end
	self.follows = nil
end

function PlayerRow:SetSelected(selected: boolean)
	if self.control then
		self.control:SetSelected(selected)
	end
end

function PlayerRow:Destroy()
	self:_unfollow()
	if self.levelBar then
		self.levelBar:Destroy()
	end
	if self.action then
		self.action:Destroy()
	end
	self.base.maid:Clean()
end

return PlayerRow
