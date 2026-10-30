-- A scrolling list with the kit's rail and thumb (sheet 09). The native
-- scrollbar is hidden (its images cannot use atlas rects); the kit track and
-- thumb follow CanvasPosition. The canvas grows with its content
-- (AutomaticCanvasSize), with bottom padding so the last row is not flush.
--
--   local list = Kit.Scroll.new(column, { rect = { 0, 50, 330, 380 }, gap = 6 })
--   for i, member in members do Kit.PlayerRow.new(list:Content(), { size = { 300, 52 }, layoutOrder = i, ... }) end

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)

local Scroll = {}
Scroll.__index = Scroll

Scroll.RAIL = 14

-- props: rect | size, direction ("Y"), gap (list padding; false for no list
-- layout), padBottom (12), contentHeight (design px, used where the engine
-- has not measured the canvas yet, as in captures), zIndex, name.
function Scroll.new(parent: Instance, props)
	local w, h = Core.Size(props, 300, 300)
	local base = Core.Root(parent, "Scroll", "scroll.track", props, w, h)
	local rail = Scroll.RAIL
	local self = setmetatable({ root = base.root, base = base, w = w, h = h, contentHeight = props.contentHeight }, Scroll)
	local frame = Core.Make("ScrollingFrame", {
		Name = "List",
		Active = true,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		CanvasSize = UDim2.new(0, 0, 0, 0),
		ElasticBehavior = Enum.ElasticBehavior.WhenScrollable,
		ScrollBarThickness = 0,
		ScrollingDirection = Enum.ScrollingDirection.Y,
		Selectable = false,
		Size = UDim2.new(1, -(rail + 6), 1, 0),
		ZIndex = base.z,
	}, base.visual)
	Core.Make("UIPadding", { PaddingBottom = UDim.new(0, props.padBottom or 12), PaddingTop = UDim.new(0, 2) }, frame)
	if props.gap ~= false then
		Core.Make("UIListLayout", {
			Padding = UDim.new(0, props.gap or 6),
			SortOrder = Enum.SortOrder.LayoutOrder,
			HorizontalAlignment = Enum.HorizontalAlignment.Center,
		}, frame)
	end
	self.frame = frame
	self.track = Core.Make("Frame", {
		Name = "Rail",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(w - rail, 0),
		Size = UDim2.fromOffset(rail, h),
		ZIndex = base.z + 1,
	}, base.visual)
	Art.Plate(self.track, "scroll.track", rail, h, { z = base.z + 1 })
	self.thumb = Core.Make("Frame", {
		Name = "Thumb",
		BackgroundTransparency = 1,
		Size = UDim2.fromOffset(rail, h),
		ZIndex = base.z + 2,
	}, self.track)
	self.thumbPlate = Art.Plate(self.thumb, "scroll.thumb", rail, 40, { z = base.z + 2 })
	local maid = base.maid
	for _, key in { "CanvasPosition", "AbsoluteCanvasSize", "AbsoluteWindowSize" } do
		maid:Give(frame:GetPropertyChangedSignal(key):Connect(function()
			self:_sync()
		end))
	end
	self:_sync()
	return self
end

function Scroll:_sync()
	local frame = self.frame
	local window = frame.AbsoluteWindowSize.Y
	local canvas = frame.AbsoluteCanvasSize.Y
	local position = frame.CanvasPosition.Y
	if window <= 0 then
		-- Not measured yet: use the design numbers.
		window = self.h
		canvas = self.contentHeight or 0
		position = 0
	else
		-- Absolute sizes are in screen px; the thumb lives in design px.
		local k = window / self.h
		canvas /= k
		position /= k
		window = self.h
	end
	local thumb = KitModel.Thumb(window, canvas, position, self.h, 28)
	self.track.Visible = thumb.visible
	self.thumb.Position = UDim2.fromOffset(0, thumb.y)
	self.thumb.Size = UDim2.fromOffset(Scroll.RAIL, thumb.height)
	self.root:SetAttribute("KitState", if thumb.visible then "scrollable" else "normal")
end

-- The frame rows go in.
function Scroll:Content(): ScrollingFrame
	return self.frame
end

-- The content height in design px, where the engine cannot measure it.
function Scroll:SetContentHeight(height: number)
	self.contentHeight = height
	self:_sync()
end

function Scroll:Destroy()
	self.base.maid:Clean()
end

return Scroll
