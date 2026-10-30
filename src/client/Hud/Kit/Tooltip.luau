-- Tooltips (sheet 09): a paper box with a tail pointing at its target. Shown
-- while the mouse hovers the target, on a long press (touch) and while a
-- gamepad selects it; one at a time in the KitTooltip gui. Kit.Tooltip.new
-- draws one in place (galleries, help text).
--
--   Kit.Tooltip.Attach(forgeButton, "Needs 2 more Iron Ore", { side = "top" })
--   Kit.Tooltip.Attach(slot, function() return itemLine(slot.item) end)

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Interact = require(script.Parent.Interact)
local Tokens = require(script.Parent.Tokens)

local Tooltip = {}
Tooltip.__index = Tooltip

Tooltip.TAIL = { 32, 21 }

-- The box size for `text`: up to tooltipMaxW wide, wrapped.
function Tooltip.Measure(text: string): (number, number)
	local pad = Tokens.Space("tooltipPad", 14)
	local maxW = Tokens.Space("tooltipMaxW", 300)
	local width = Core.TextWidth(text, "body")
	local lines = math.max(1, math.ceil(width / (maxW - pad * 2)))
	local w = math.min(maxW, math.ceil(width) + pad * 2 + 4)
	local h = lines * Tokens.TextStyle("body").size * 1.35 + pad * 2
	return w, math.ceil(h)
end

-- props: rect | size (a width of 0 fits the text), text, tail ("bottom" |
-- "top" | "none"), zIndex, name. The rect is the box; the tail hangs outside.
function Tooltip.new(parent: Instance, props)
	local mw, mh = Tooltip.Measure(props.text or "")
	local w, h = Core.Size(props, mw, mh)
	if w <= 0 then
		w, h = mw, mh
	end
	local place = table.clone(props)
	if props.rect then
		place.rect = { props.rect[1], props.rect[2], w, h }
	end
	local base = Core.Root(parent, "Tooltip", "tooltip.box", place, w, h)
	local self = setmetatable({ root = base.root, base = base }, Tooltip)
	Art.Plate(base.visual, "tooltip.box", w, h, { z = base.z })
	local tail = props.tail or "bottom"
	if tail ~= "none" then
		local tw, th = Tooltip.TAIL[1], Tooltip.TAIL[2]
		local holder = Core.Make("Frame", {
			Name = "Tail",
			AnchorPoint = Vector2.new(0.5, 0),
			BackgroundTransparency = 1,
			Position = if tail == "top" then UDim2.new(0.5, 0, 0, -th + 4) else UDim2.new(0.5, 0, 1, -5),
			Rotation = if tail == "top" then 180 else 0,
			Size = UDim2.fromOffset(tw, th),
			ZIndex = base.z + 1,
		}, base.visual)
		Art.Plate(holder, "tooltip.tail", tw, th, { z = base.z + 1 })
	end
	local pad = Tokens.Space("tooltipPad", 14)
	self.label = Core.Label(base.visual, {
		name = "Text",
		text = props.text or "",
		role = "body",
		color = "inkLabel",
		align = "Center",
		wrap = true,
		rect = { pad, pad - 2, w - pad * 2, h - pad * 2 },
		z = base.z + 2,
	})
	return self
end

function Tooltip:Destroy()
	self.base.maid:Clean()
end

-- The shared layer --------------------------------------------------------------------

local layer: ScreenGui? = nil
local current = nil

local function gui(): ScreenGui
	if layer and layer.Parent then
		return layer
	end
	layer = Core.Make("ScreenGui", {
		Name = "KitTooltip",
		DisplayOrder = Tokens.Order("tooltip"),
		IgnoreGuiInset = true,
		ResetOnSpawn = false,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, Players.LocalPlayer:FindFirstChildOfClass("PlayerGui"))
	return layer :: ScreenGui
end

local function hide(owner)
	if current and (owner == nil or current.owner == owner) then
		current.tip:Destroy()
		current.holder:Destroy()
		current = nil
	end
end

local function show(owner, target: GuiObject, text: string, side: string)
	hide()
	local screen = gui()
	local size = screen.AbsoluteSize
	local ref = Tokens.Data.reference
	local k = HudModel.HudScale(size.X, size.Y, ref.width, ref.height, Tokens.Scale("hudMin"), 1.2, nil)
	local holder = Core.Make("Frame", {
		Name = "Tip",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1 / k, 1 / k),
	}, screen)
	Core.Make("UIScale", { Scale = k }, holder)
	local w, h = Tooltip.Measure(text)
	local pos, extent = target.AbsolutePosition, target.AbsoluteSize
	local gap = Tooltip.TAIL[2] + 2
	local x, y
	if side == "right" then
		x, y = (pos.X + extent.X) / k + gap, (pos.Y + extent.Y / 2) / k - h / 2
	else
		x, y = (pos.X + extent.X / 2) / k - w / 2, pos.Y / k - h - gap
	end
	-- Kept on screen.
	x = math.clamp(x, 8, math.max(8, size.X / k - w - 8))
	y = math.clamp(y, 8, math.max(8, size.Y / k - h - 8))
	local tip = Tooltip.new(holder, { rect = { x, y, w, h }, text = text, tail = if side == "right" then "none" else "bottom", zIndex = 5 })
	current = { owner = owner, tip = tip, holder = holder }
end

-- Attaches a tooltip to `target` (a kit component or a GuiObject). `content`
-- is the text or a function returning it (nil or "" shows nothing). opts.side:
-- "top" (default) or "right". Returns a function that detaches it.
function Tooltip.Attach(target, content: string | () -> string?, opts): () -> ()
	opts = opts or {}
	local root: GuiObject = if type(target) == "table" then target.root else target
	local hit: GuiObject = if type(target) == "table" and target.control then target.control.hit else root
	local owner = {}
	local function text(): string?
		local value = if type(content) == "function" then content() else content
		return if type(value) == "string" and value ~= "" then value else nil
	end
	local function open()
		local value = text()
		if value then
			show(owner, root, value, opts.side or "top")
		end
	end
	local connections = {}
	local function on(signal, fn)
		local ok, connection = pcall(function()
			return signal:Connect(fn)
		end)
		if ok then
			table.insert(connections, connection)
		end
	end
	local pressSerial = 0
	on(hit.MouseEnter, function()
		if Interact.UsingMouse() then
			open()
		end
	end)
	on(hit.MouseLeave, function()
		hide(owner)
	end)
	on(hit.SelectionGained, open)
	on(hit.SelectionLost, function()
		hide(owner)
	end)
	on(hit.InputBegan, function(input: InputObject)
		if input.UserInputType == Enum.UserInputType.Touch then
			pressSerial += 1
			local serial = pressSerial
			task.delay(Tokens.Space("longPress", 0.5), function()
				if serial == pressSerial then
					open()
				end
			end)
		end
	end)
	on(hit.InputEnded, function(input: InputObject)
		if input.UserInputType == Enum.UserInputType.Touch then
			pressSerial += 1
			hide(owner)
		end
	end)
	on(root.Destroying, function()
		hide(owner)
	end)
	return function()
		for _, connection in connections do
			connection:Disconnect()
		end
		hide(owner)
	end
end

return Tooltip
