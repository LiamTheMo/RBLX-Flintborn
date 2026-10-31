-- Item slots (sheets 05, 10, 13; M02 grid, M01 / M05 hotbar):
--   "item"   inventory grid slot (gold glow ring when selected)
--   "hotbar" hotbar / equipment slot with hover, selected, disabled and
--            locked art, and a leather number badge (hotkey) at its top left.
-- Holds a Kit.ItemIcon, a count (bottom-right text, or a count plaque), and a
-- star for Permanent items. States: normal, hover, pressed, selected,
-- disabled, locked (lock art; still selectable), empty.
--
--   local slot = Kit.Slot.new(grid, { size = { 92, 99 }, layoutOrder = i, onPress = pick })
--   slot:SetItem({ catalogId = "StoneAxe", quantity = 1, permanent = true })
--   slot:SetSelected(true)

local Art = require(script.Parent.Art)
local Badge = require(script.Parent.Badge)
local Core = require(script.Parent.Core)
local Interact = require(script.Parent.Interact)
local ItemIcon = require(script.Parent.ItemIcon)

local Slot = {}
Slot.__index = Slot

-- `itemId` is accepted for `catalogId`. Art and tint always come from
-- ItemInfo.Icon(id); `icon` is used (untinted) only when ItemInfo has none.
export type Item = { catalogId: string?, itemId: string?, quantity: number?, permanent: boolean?, icon: string? }

-- props: rect | size (default 90), variant ("item" | "hotbar"), item, count,
-- hotkey (badge text), countStyle ("text" | "plaque"), countInset ({right,
-- bottom} px, default {10, 10}), countSize, onPress(slot),
-- zIndex, name.
function Slot.new(parent: Instance, props)
	local variant = props.variant or "item"
	local role = if variant == "hotbar" then "slot.hotbar" else "slot.item"
	local w, h = Core.Size(props, 90, 90)
	local base = Core.Root(parent, "Slot", role, props, w, h)
	local self = setmetatable({
		root = base.root,
		base = base,
		variant = variant,
		w = w,
		h = h,
		countStyle = props.countStyle or "text",
		item = nil,
	}, Slot)
	self.plate = Art.Plate(base.visual, role, w, h, { z = base.z })
	local s = math.floor(math.min(w, h) * 0.74)
	self.icon = ItemIcon.new(base.visual, {
		name = "Item",
		rect = { (w - s) / 2, (h - s) / 2 - 2, s, s },
		zIndex = base.z + 1,
	})
	self.count = Core.Label(base.visual, {
		name = "Count",
		text = "",
		role = "count",
		size = props.countSize,
		align = "Right",
		yAlign = "Bottom",
		-- countInset {right, bottom}: the count's distance from the slot's edges.
		rect = { 8, 6, w - 8 - (props.countInset and props.countInset[1] or 10), h - 6 - (props.countInset and props.countInset[2] or 10) },
		z = base.z + 3,
	})
	self.star = Core.Make("Frame", {
		Name = "Permanent",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(w - 30, 6),
		Size = UDim2.fromOffset(24, 24),
		Visible = false,
		ZIndex = base.z + 3,
	}, base.visual)
	Art.Plate(self.star, "mark.star", 24, 24, { z = base.z + 3 })
	self.control = Interact.attach(base, {
		hoverScale = true,
		onPress = function()
			if props.onPress then
				props.onPress(self)
			end
		end,
		render = function(state)
			self.plate:Show(state)
			-- Locked art carries its own lock: the item and count give way to it.
			local locked = state == "locked"
			local dim = state == "disabled"
			self.icon.root.Visible = not locked
			self.star.Visible = not locked and self.item ~= nil and self.item.permanent == true
			self.count.Visible = not locked
			self.count.TextTransparency = if dim then 0.4 else 0
			for _, part in self.icon.root:GetDescendants() do
				if part:IsA("ImageLabel") then
					part.ImageTransparency = if dim then 0.4 else 0
				end
			end
		end,
	})
	if props.hotkey then
		self:SetHotkey(props.hotkey)
	end
	self:SetItem(props.item)
	if props.count then
		self:SetCount(props.count)
	end
	return self
end

-- Shows an item ({catalogId, quantity, permanent, icon}) or nil for empty.
function Slot:SetItem(item: Item?)
	self.item = item
	self.icon:SetItem(item and (item.catalogId or item.itemId), item and item.icon)
	-- A pooled slot shows a new item: a press on it is a fresh press.
	self.control.lastPress = -math.huge
	self.star.Visible = item ~= nil and item.permanent == true
	self:SetCount(item and item.quantity)
	self.control:Set("empty", item == nil)
end

-- The count at the bottom right; 1 and nil show nothing.
function Slot:SetCount(count: number?)
	local text = if count and count > 1 then tostring(count) else ""
	if self.countStyle == "plaque" then
		if self.countBadge == nil and text ~= "" then
			self.countBadge = Badge.new(self.base.visual, {
				variant = "count",
				text = text,
				rect = { self.w - 38, self.h - 34, 34, 31 },
				zIndex = self.base.z + 3,
			})
		end
		if self.countBadge then
			self.countBadge:SetText(text)
			self.countBadge:SetVisible(text ~= "")
		end
		self.count.Text = ""
	else
		self.count.Text = text
	end
end

-- The hotbar number badge (nil hides it).
function Slot:SetHotkey(text: string?)
	if text == nil then
		if self.hotkey then
			self.hotkey:SetVisible(false)
		end
		return
	end
	if self.hotkey == nil then
		self.hotkey = Badge.new(self.base.visual, {
			variant = "number",
			text = text,
			rect = { 3, 3, 26, 26 },
			zIndex = self.base.z + 4,
		})
	end
	self.hotkey:SetText(text)
	self.hotkey:SetVisible(true)
end

-- "normal" | "locked" | "disabled": the slot's standing state.
function Slot:SetState(state: string)
	self.control:SetLocked(state == "locked")
	self.control:SetEnabled(state ~= "disabled")
end

function Slot:SetSelected(selected: boolean)
	self.control:SetSelected(selected)
end

function Slot:SetEnabled(enabled: boolean)
	self.control:SetEnabled(enabled)
end

function Slot:Destroy()
	self.base.maid:Clean()
end

return Slot
