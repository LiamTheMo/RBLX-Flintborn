-- Drag and drop between item slots (Kit.Slot): the inventory window's cells and
-- the HUD hotbars. A mouse drags once the pointer moves a few px with the button
-- held; a finger holds the slot for a moment first, so a quick swipe still
-- scrolls the grid. The item's picture follows the pointer, the slot under it
-- lights up when it would take the item, and letting go there hands
-- (fromId, toId) to the source's onDrop. Letting go anywhere else, or Escape,
-- puts nothing anywhere. Gamepads keep each screen's MOVE action instead.
--
-- Slots join a `group` ("run", "lobby"): a drag only lands on slots of its own
-- group, so the window and the HUD hotbar of one place work together. Each slot
-- names the cell it shows now through `id()` (pooled slots change cells).
--
--   Kit.Drag.Attach(slot, { group = "run", id = function() return "hotbar:1" end,
--       canDrop = function(from, to) return true end, onDrop = function(from, to) ... end })

local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")

local Core = require(script.Parent.Core)
local ItemIcon = require(script.Parent.ItemIcon)
local Tokens = require(script.Parent.Tokens)

local Drag = {}

-- Screen px a mouse moves before a press becomes a drag.
Drag.THRESHOLD = 6
-- Seconds a finger holds still on a slot before it picks the item up, and how
-- far it may wander meanwhile (further is a scroll).
Drag.HOLD_SECONDS = 0.3
Drag.TOUCH_SLOP = 12
-- The picture under the pointer: a share of the source slot's size, and its fade.
Drag.GHOST_SCALE = 0.85
Drag.GHOST_FADE = 0.15
-- How faint the source slot's own item draws while it is carried.
Drag.SOURCE_FADE = 0.6

export type Spec = {
	group: string,
	id: () -> string?,
	canDrag: ((id: string) -> boolean)?,
	canDrop: ((fromId: string, toId: string) -> boolean)?,
	onDrop: (fromId: string, toId: string) -> (),
}

-- slot -> spec, for every attached slot.
local slots: { [any]: Spec } = setmetatable({}, { __mode = "k" }) :: any
-- A press that may become a drag: {slot, spec, id, input, start, last, touch}.
local pending = nil
-- The drag in progress: {slot, spec, id, input, touch, gui, ghost, over, scrolls}.
local active = nil
local connected = false

-- The input's place on the whole screen (an input's Position leaves out the top
-- bar's inset; GUI rects drawn on the whole screen include it).
local function pointOf(input: InputObject): Vector2
	local inset = GuiService:GetGuiInset()
	return Vector2.new(input.Position.X, input.Position.Y) + inset
end

local function screenGuiOf(object: Instance): ScreenGui?
	return object:FindFirstAncestorWhichIsA("ScreenGui")
end

-- `object`'s rect on the whole screen.
local function rectOf(object: GuiObject): (Vector2, Vector2)
	local position = object.AbsolutePosition
	local gui = screenGuiOf(object)
	if gui and not gui.IgnoreGuiInset then
		position += GuiService:GetGuiInset()
	end
	return position, object.AbsoluteSize
end

local function contains(object: GuiObject, point: Vector2): boolean
	local position, size = rectOf(object)
	return point.X >= position.X
		and point.Y >= position.Y
		and point.X < position.X + size.X
		and point.Y < position.Y + size.Y
end

-- Whether `slot` shows on screen at `point`: inside its rect, every ancestor
-- visible, and inside every clipping ancestor (a scrolled-away cell is not).
local function showsAt(slot, point: Vector2): boolean
	local root = slot.root
	local gui = screenGuiOf(root)
	if gui == nil or not gui.Enabled or not contains(root, point) then
		return false
	end
	local node: Instance? = root
	while node and node ~= gui do
		if node:IsA("GuiObject") then
			local object = node :: GuiObject
			if not object.Visible then
				return false
			end
			if object ~= root and object.ClipsDescendants and not contains(object, point) then
				return false
			end
		end
		node = node.Parent
	end
	return true
end

-- The slot of `group` under `point`, in the topmost gui when several overlap.
local function slotAt(group: string, point: Vector2)
	local best, order = nil, -math.huge
	for slot, spec in slots do
		if spec.group == group and slot.root.Parent and showsAt(slot, point) then
			local gui = screenGuiOf(slot.root)
			local rank = gui and gui.DisplayOrder or 0
			if rank > order then
				best, order = slot, rank
			end
		end
	end
	return best
end

local function setHover(slot, on: boolean)
	if slot and slot.control then
		slot.control.flags.hover = on
		slot.control:Refresh()
	end
end

-- Whether the drag in progress may land on `slot`.
local function accepts(slot): boolean
	if active == nil or slot == nil or slot == active.slot then
		return false
	end
	local spec = slots[slot]
	local toId = spec and spec.id()
	if toId == nil then
		return false
	end
	local canDrop = active.spec.canDrop
	return canDrop == nil or canDrop(active.id, toId)
end

local function place(point: Vector2)
	if active then
		local size = active.ghost.AbsoluteSize
		active.ghost.Position = UDim2.fromOffset(point.X - size.X / 2, point.Y - size.Y / 2)
	end
end

local function hover(point: Vector2)
	if active == nil then
		return
	end
	local under = slotAt(active.spec.group, point)
	local target = if accepts(under) then under else nil
	if target ~= active.over then
		setHover(active.over, false)
		active.over = target
		setHover(target, true)
	end
end

local function begin(point: Vector2)
	local press = pending
	pending = nil
	if press == nil or active ~= nil or press.slot.root.Parent == nil then
		return
	end
	local item = press.slot.item
	local catalogId = item and (item.catalogId or item.itemId)
	if catalogId == nil then
		return
	end
	local gui = Instance.new("ScreenGui")
	gui.Name = "FlintbornDrag"
	gui.IgnoreGuiInset = true
	gui.ResetOnSpawn = false
	gui.DisplayOrder = Tokens.Order("drag")
	pcall(function()
		gui.ScreenInsets = Enum.ScreenInsets.None
	end)
	local size = press.slot.root.AbsoluteSize * Drag.GHOST_SCALE
	local ghost = Instance.new("Frame")
	ghost.Name = "Ghost"
	ghost.BackgroundTransparency = 1
	ghost.Size = UDim2.fromOffset(size.X, size.Y)
	ghost.Parent = gui
	local icon = ItemIcon.new(ghost, { name = "Item", rect = { 0, 0, size.X, size.Y }, catalogId = catalogId })
	Core.Dim(icon.root, Drag.GHOST_FADE)
	gui.Parent = Players.LocalPlayer:FindFirstChildOfClass("PlayerGui")
	-- A finger dragging inside a scrolling list must not scroll it meanwhile.
	local scrolls = {}
	local node = press.slot.root.Parent
	while node do
		if node:IsA("ScrollingFrame") then
			scrolls[node] = node.ScrollingEnabled
			node.ScrollingEnabled = false
		end
		node = node.Parent
	end
	active = {
		slot = press.slot,
		spec = press.spec,
		id = press.id,
		input = press.input,
		touch = press.touch,
		gui = gui,
		ghost = ghost,
		over = nil,
		scrolls = scrolls,
	}
	press.slot.control:_endPress()
	Core.Dim(press.slot.icon.root, Drag.SOURCE_FADE)
	place(point)
	hover(point)
end

-- Ends the drag; `point` lands it there (nil cancels).
local function finish(point: Vector2?)
	local drag = active
	active = nil
	if drag == nil then
		return
	end
	setHover(drag.over, false)
	drag.gui:Destroy()
	for frame, enabled in drag.scrolls do
		frame.ScrollingEnabled = enabled
	end
	if drag.slot.root.Parent then
		Core.Dim(drag.slot.icon.root, 0)
	end
	-- The release over a slot must not also press it.
	local now = os.clock()
	drag.slot.control.lastPress = now
	if point == nil then
		return
	end
	-- Re-checked at the drop: the cells may have changed while it was carried.
	local target = slotAt(drag.spec.group, point)
	if target == nil then
		return
	end
	target.control.lastPress = now
	active = drag
	local ok = accepts(target)
	active = nil
	if ok then
		local toId = slots[target].id()
		task.spawn(drag.spec.onDrop, drag.id, toId :: string)
	end
end

local function isPointer(input: InputObject): boolean
	return input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.Touch
end

local function connect()
	if connected then
		return
	end
	connected = true
	UserInputService.InputChanged:Connect(function(input: InputObject)
		local mouse = input.UserInputType == Enum.UserInputType.MouseMovement
		local touch = input.UserInputType == Enum.UserInputType.Touch
		if not (mouse or touch) then
			return
		end
		local point = pointOf(input)
		if active then
			if (mouse and not active.touch) or input == active.input then
				place(point)
				hover(point)
			end
			return
		end
		local press = pending
		if press == nil then
			return
		end
		if press.touch then
			if input == press.input then
				press.last = point
				if (point - press.start).Magnitude > Drag.TOUCH_SLOP then
					-- Moved before the hold: a scroll, not a drag.
					pending = nil
				end
			end
		elseif mouse and (point - press.start).Magnitude >= Drag.THRESHOLD then
			begin(point)
		end
	end)
	UserInputService.InputEnded:Connect(function(input: InputObject)
		if not isPointer(input) then
			return
		end
		local mouse = input.UserInputType == Enum.UserInputType.MouseButton1
		if active and (if active.touch then input == active.input else mouse) then
			finish(pointOf(input))
		end
		if pending and (if pending.touch then input == pending.input else mouse) then
			pending = nil
		end
	end)
	UserInputService.InputBegan:Connect(function(input: InputObject)
		if active and input.KeyCode == Enum.KeyCode.Escape then
			finish(nil)
		end
	end)
end

-- Lets `slot` (a Kit.Slot) be dragged and dropped onto. Stops when the slot is
-- destroyed.
function Drag.Attach(slot, spec: Spec)
	connect()
	slots[slot] = spec
	local maid = slot.base.maid
	maid:Give(slot.control.hit.InputBegan:Connect(function(input: InputObject)
		if not isPointer(input) or active ~= nil then
			return
		end
		local id = spec.id()
		if id == nil or slot.item == nil or (spec.canDrag and not spec.canDrag(id)) then
			return
		end
		local touch = input.UserInputType == Enum.UserInputType.Touch
		local point = pointOf(input)
		local press = { slot = slot, spec = spec, id = id, input = input, start = point, last = point, touch = touch }
		pending = press
		if touch then
			task.delay(Drag.HOLD_SECONDS, function()
				if pending == press then
					begin(press.last)
				end
			end)
		end
	end))
	maid:Give(function()
		slots[slot] = nil
		if pending and pending.slot == slot then
			pending = nil
		end
		if active and active.slot == slot then
			finish(nil)
		end
	end)
end

-- True while an item is being carried (slots ignore presses meanwhile).
function Drag.Active(): boolean
	return active ~= nil
end

return Drag
