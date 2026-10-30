--!nocheck
-- A headless stand-in for the Roblox GUI runtime, enough for the code-built
-- screens under src/client/Hud to run in the standalone Luau CLI. capture.py
-- bundles this with the game modules and a scene script; the scene builds a
-- screen and calls __dump(root), which prints the instance tree as JSON for
-- render.py to lay out and draw. Nothing here is used by the game.

-- The game's SpriteLoader paces image loading on a clock that never runs here;
-- in a capture it hands every image out at once.
__FlintbornCapture = true

-- Datatypes ----------------------------------------------------------------------

local function typed(kind, fields, meta)
	fields.__type = kind
	return setmetatable(fields, meta)
end

local UDimMeta = {}
UDimMeta.__index = UDimMeta
UDim = {}
function UDim.new(scale, offset)
	return typed("UDim", { Scale = scale or 0, Offset = offset or 0 }, UDimMeta)
end
UDimMeta.__add = function(a, b)
	return UDim.new(a.Scale + b.Scale, a.Offset + b.Offset)
end

local UDim2Meta = {}
UDim2Meta.__index = UDim2Meta
UDim2 = {}
function UDim2.new(xs, xo, ys, yo)
	if type(xs) == "table" then
		-- UDim2.new(UDim, UDim)
		return typed("UDim2", { X = xs, Y = xo }, UDim2Meta)
	end
	return typed("UDim2", { X = UDim.new(xs, xo), Y = UDim.new(ys, yo) }, UDim2Meta)
end
function UDim2.fromOffset(x, y)
	return UDim2.new(0, x or 0, 0, y or 0)
end
function UDim2.fromScale(x, y)
	return UDim2.new(x or 0, 0, y or 0, 0)
end
UDim2Meta.__add = function(a, b)
	return UDim2.new(a.X.Scale + b.X.Scale, a.X.Offset + b.X.Offset, a.Y.Scale + b.Y.Scale, a.Y.Offset + b.Y.Offset)
end
UDim2Meta.__sub = function(a, b)
	return UDim2.new(a.X.Scale - b.X.Scale, a.X.Offset - b.X.Offset, a.Y.Scale - b.Y.Scale, a.Y.Offset - b.Y.Offset)
end
UDim2Meta.__eq = function(a, b)
	return a.X.Scale == b.X.Scale and a.X.Offset == b.X.Offset and a.Y.Scale == b.Y.Scale and a.Y.Offset == b.Y.Offset
end
function UDim2Meta:Lerp(goal, t)
	return UDim2.new(
		self.X.Scale + (goal.X.Scale - self.X.Scale) * t,
		self.X.Offset + (goal.X.Offset - self.X.Offset) * t,
		self.Y.Scale + (goal.Y.Scale - self.Y.Scale) * t,
		self.Y.Offset + (goal.Y.Offset - self.Y.Offset) * t
	)
end

local Vector2Meta = {}
Vector2Meta.__index = function(v, key)
	if key == "Magnitude" then
		return math.sqrt(v.X * v.X + v.Y * v.Y)
	end
	return Vector2Meta[key]
end
Vector2 = {}
function Vector2.new(x, y)
	return typed("Vector2", { X = x or 0, Y = y or 0 }, Vector2Meta)
end
Vector2.zero = Vector2.new(0, 0)
Vector2.one = Vector2.new(1, 1)
Vector2Meta.__add = function(a, b)
	return Vector2.new(a.X + b.X, a.Y + b.Y)
end
Vector2Meta.__sub = function(a, b)
	return Vector2.new(a.X - b.X, a.Y - b.Y)
end
Vector2Meta.__mul = function(a, b)
	if type(a) == "number" then
		a, b = b, a
	end
	if type(b) == "number" then
		return Vector2.new(a.X * b, a.Y * b)
	end
	return Vector2.new(a.X * b.X, a.Y * b.Y)
end

local Vector3Meta = {}
Vector3 = {}
function Vector3.new(x, y, z)
	return typed("Vector3", { X = x or 0, Y = y or 0, Z = z or 0 }, Vector3Meta)
end
Vector3.zero = Vector3.new(0, 0, 0)
Vector3.one = Vector3.new(1, 1, 1)
local Vector3Methods = {}
function Vector3Methods.Dot(a, b)
	return a.X * b.X + a.Y * b.Y + a.Z * b.Z
end
function Vector3Methods.Cross(a, b)
	return Vector3.new(a.Y * b.Z - a.Z * b.Y, a.Z * b.X - a.X * b.Z, a.X * b.Y - a.Y * b.X)
end
function Vector3Methods.Lerp(a, b, t)
	return Vector3.new(a.X + (b.X - a.X) * t, a.Y + (b.Y - a.Y) * t, a.Z + (b.Z - a.Z) * t)
end
Vector3Meta.__index = function(v, key)
	if key == "Magnitude" then
		return math.sqrt(v.X * v.X + v.Y * v.Y + v.Z * v.Z)
	elseif key == "Unit" then
		local m = math.sqrt(v.X * v.X + v.Y * v.Y + v.Z * v.Z)
		return if m > 0 then Vector3.new(v.X / m, v.Y / m, v.Z / m) else Vector3.new(0 / 0, 0 / 0, 0 / 0)
	end
	return Vector3Methods[key]
end
Vector3Meta.__add = function(a, b)
	return Vector3.new(a.X + b.X, a.Y + b.Y, a.Z + b.Z)
end
Vector3Meta.__sub = function(a, b)
	return Vector3.new(a.X - b.X, a.Y - b.Y, a.Z - b.Z)
end
Vector3Meta.__unm = function(a)
	return Vector3.new(-a.X, -a.Y, -a.Z)
end
Vector3Meta.__mul = function(a, b)
	if type(a) == "number" then
		a, b = b, a
	end
	if type(b) == "number" then
		return Vector3.new(a.X * b, a.Y * b, a.Z * b)
	end
	return Vector3.new(a.X * b.X, a.Y * b.Y, a.Z * b.Z)
end
Vector3Meta.__div = function(a, b)
	if type(b) == "number" then
		return Vector3.new(a.X / b, a.Y / b, a.Z / b)
	end
	return Vector3.new(a.X / b.X, a.Y / b.Y, a.Z / b.Z)
end
Vector3Meta.__eq = function(a, b)
	return a.X == b.X and a.Y == b.Y and a.Z == b.Z
end

local RectMeta = {}
RectMeta.__index = function(r, key)
	if key == "Width" then
		return r.Max.X - r.Min.X
	elseif key == "Height" then
		return r.Max.Y - r.Min.Y
	end
	return nil
end
Rect = {}
function Rect.new(a, b, c, d)
	if type(a) == "table" then
		return typed("Rect", { Min = a, Max = b }, RectMeta)
	end
	return typed("Rect", { Min = Vector2.new(a, b), Max = Vector2.new(c, d) }, RectMeta)
end

local Color3Meta = {}
Color3Meta.__index = Color3Meta
Color3 = {}
function Color3.new(r, g, b)
	return typed("Color3", { R = r or 0, G = g or 0, B = b or 0 }, Color3Meta)
end
function Color3.fromRGB(r, g, b)
	return Color3.new((r or 0) / 255, (g or 0) / 255, (b or 0) / 255)
end
function Color3.fromHex(hex)
	hex = string.gsub(hex, "#", "")
	assert(#hex == 6, "bad hex " .. hex)
	return Color3.fromRGB(tonumber(hex:sub(1, 2), 16), tonumber(hex:sub(3, 4), 16), tonumber(hex:sub(5, 6), 16))
end
function Color3.fromHSV(h, s, v)
	local i = math.floor(h * 6)
	local f = h * 6 - i
	local p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
	local row = ({ { v, t, p }, { q, v, p }, { p, v, t }, { p, q, v }, { t, p, v }, { v, p, q } })[i % 6 + 1]
	return Color3.new(row[1], row[2], row[3])
end
function Color3Meta:Lerp(other, t)
	return Color3.new(self.R + (other.R - self.R) * t, self.G + (other.G - self.G) * t, self.B + (other.B - self.B) * t)
end
function Color3Meta:ToHex()
	return string.format("%02X%02X%02X", self.R * 255 + 0.5, self.G * 255 + 0.5, self.B * 255 + 0.5)
end
function Color3Meta:ToHSV()
	local r, g, b = self.R, self.G, self.B
	local max, min = math.max(r, g, b), math.min(r, g, b)
	local h, s, v = 0, 0, max
	local d = max - min
	if max > 0 then
		s = d / max
	end
	if d > 0 then
		if max == r then
			h = ((g - b) / d) % 6
		elseif max == g then
			h = (b - r) / d + 2
		else
			h = (r - g) / d + 4
		end
		h /= 6
	end
	return h, s, v
end
Color3Meta.__eq = function(a, b)
	return a.R == b.R and a.G == b.G and a.B == b.B
end

ColorSequenceKeypoint = {}
function ColorSequenceKeypoint.new(t, c)
	return { __type = "ColorSequenceKeypoint", Time = t, Value = c }
end
ColorSequence = {}
function ColorSequence.new(a, b)
	if type(a) == "table" and a.__type == "Color3" then
		return {
			__type = "ColorSequence",
			Keypoints = { ColorSequenceKeypoint.new(0, a), ColorSequenceKeypoint.new(1, b or a) },
		}
	end
	return { __type = "ColorSequence", Keypoints = a }
end
NumberSequenceKeypoint = {}
function NumberSequenceKeypoint.new(t, v)
	return { __type = "NumberSequenceKeypoint", Time = t, Value = v }
end
NumberSequence = {}
function NumberSequence.new(a, b)
	if type(a) == "number" then
		return {
			__type = "NumberSequence",
			Keypoints = { NumberSequenceKeypoint.new(0, a), NumberSequenceKeypoint.new(1, b or a) },
		}
	end
	return { __type = "NumberSequence", Keypoints = a }
end
NumberRange = {}
function NumberRange.new(a, b)
	return { __type = "NumberRange", Min = a, Max = b or a }
end

TweenInfo = {}
function TweenInfo.new(time, style, direction, repeats, reverses, delay)
	return { __type = "TweenInfo", Time = time or 1 }
end

Font = {}
function Font.new(family, weight, style)
	return { __type = "Font", Family = family, Weight = weight or "FontWeight.Regular", Style = style }
end
function Font.fromName(name, weight, style)
	return Font.new("rbxasset://fonts/families/" .. name .. ".json", weight, style)
end
function Font.fromEnum(enum)
	return Font.new(tostring(enum), "FontWeight.Regular")
end

DateTime = {}
function DateTime.now()
	return { UnixTimestamp = 0, UnixTimestampMillis = 0 }
end

-- Enum items are their "Enum.Item" names (comparable, and readable by render.py).
Enum = setmetatable({}, {
	__index = function(_, enumName)
		local items = setmetatable({}, {
			__index = function(_, itemName)
				return enumName .. "." .. itemName
			end,
		})
		function items.GetEnumItems()
			return {}
		end
		return items
	end,
})

-- Signals ------------------------------------------------------------------------

local SignalMeta = {}
SignalMeta.__index = SignalMeta
local function newSignal()
	return setmetatable({ handlers = {} }, SignalMeta)
end
function SignalMeta:Connect(fn)
	table.insert(self.handlers, fn)
	local signal = self
	return {
		Connected = true,
		Disconnect = function(c)
			c.Connected = false
			local i = table.find(signal.handlers, fn)
			if i then
				table.remove(signal.handlers, i)
			end
		end,
	}
end
SignalMeta.Once = SignalMeta.Connect
function SignalMeta:Fire(...)
	for _, fn in table.clone(self.handlers) do
		fn(...)
	end
end
function SignalMeta:Wait()
	return nil
end

-- Instances -----------------------------------------------------------------------

local BASES = {
	Frame = { "GuiObject", "GuiBase2d" },
	ScrollingFrame = { "GuiObject", "GuiBase2d" },
	CanvasGroup = { "GuiObject", "GuiBase2d" },
	ViewportFrame = { "GuiObject", "GuiBase2d" },
	TextLabel = { "GuiObject", "GuiBase2d" },
	TextButton = { "GuiButton", "GuiObject", "GuiBase2d" },
	TextBox = { "GuiObject", "GuiBase2d" },
	ImageLabel = { "GuiObject", "GuiBase2d" },
	ImageButton = { "GuiButton", "GuiObject", "GuiBase2d" },
	ScreenGui = { "LayerCollector", "GuiBase2d" },
	BillboardGui = { "LayerCollector", "GuiBase2d" },
	SurfaceGui = { "LayerCollector", "GuiBase2d" },
	UIListLayout = { "UIGridStyleLayout", "UILayout", "UIComponent" },
	UIGridLayout = { "UIGridStyleLayout", "UILayout", "UIComponent" },
	Part = { "BasePart", "PVInstance" },
	MeshPart = { "BasePart", "PVInstance" },
}

-- Properties Roblox only has on some classes: setting one elsewhere errors there
-- ("X is not a valid member of Frame"), so it errors here too. A scene may still
-- stub a method with a function value.
local IMAGE_PROPS = {
	"Image",
	"ImageColor3",
	"ImageTransparency",
	"ImageRectOffset",
	"ImageRectSize",
	"ResampleMode",
	"ScaleType",
	"SliceCenter",
	"SliceScale",
	"TileSize",
}
local TEXT_PROPS = {
	"Text",
	"TextColor3",
	"TextSize",
	"TextScaled",
	"TextWrapped",
	"TextXAlignment",
	"TextYAlignment",
	"TextTransparency",
	"TextStrokeColor3",
	"TextStrokeTransparency",
	"TextTruncate",
	"Font",
	"FontFace",
	"RichText",
	"LineHeight",
	"MaxVisibleGraphemes",
}
local ONLY = {}
for _, key in IMAGE_PROPS do
	ONLY[key] = { ImageLabel = true, ImageButton = true }
end
for _, key in TEXT_PROPS do
	ONLY[key] = { TextLabel = true, TextButton = true, TextBox = true }
end
ONLY.AutoButtonColor = { TextButton = true, ImageButton = true, GuiButton = true }
local GUI_CLASSES = { Frame = true, ScrollingFrame = true, CanvasGroup = true, ViewportFrame = true }
for name in ONLY.Image do
	GUI_CLASSES[name] = true
end
for name in ONLY.Text do
	GUI_CLASSES[name] = true
end

function checkProperty(className, key, value)
	if (key == "Text" or key == "PlaceholderText") and type(value) ~= "string" then
		error(("%s must be a string, got %s"):format(key, type(value)), 3)
	end
	local allowed = ONLY[key]
	if allowed and GUI_CLASSES[className] and not allowed[className] and type(value) ~= "function" then
		error(("%s is not a valid member of %s"):format(key, className), 3)
	end
end

local function defaults(className)
	local p = {
		Visible = true,
		ZIndex = 1,
		LayoutOrder = 0,
		Position = UDim2.new(0, 0, 0, 0),
		Size = UDim2.new(0, 0, 0, 0),
		AnchorPoint = Vector2.new(0, 0),
		Rotation = 0,
		BackgroundColor3 = Color3.fromRGB(163, 162, 165),
		BackgroundTransparency = 0,
		BorderSizePixel = 1,
		ClipsDescendants = false,
		AutomaticSize = "AutomaticSize.None",
		Active = false,
		Selectable = false,
		Interactable = true,
		AbsoluteSize = Vector2.new(0, 0),
		AbsolutePosition = Vector2.new(0, 0),
	}
	if className == "TextLabel" or className == "TextButton" or className == "TextBox" then
		p.Text = className == "TextLabel" and "Label" or (className == "TextButton" and "Button" or "")
		p.TextSize = 14
		p.TextColor3 = Color3.new(0, 0, 0)
		p.TextTransparency = 0
		p.TextStrokeTransparency = 1
		p.TextStrokeColor3 = Color3.new(0, 0, 0)
		p.TextScaled = false
		p.TextWrapped = false
		p.TextXAlignment = "TextXAlignment.Center"
		p.TextYAlignment = "TextYAlignment.Center"
		p.TextTruncate = "TextTruncate.None"
		p.Font = "Font.Legacy"
		p.FontFace = Font.new("rbxasset://fonts/families/LegacyArial.json")
		p.RichText = false
		p.LineHeight = 1
		p.MaxVisibleGraphemes = -1
		p.TextBounds = Vector2.new(0, 0)
		p.PlaceholderText = ""
	end
	if className == "ImageLabel" or className == "ImageButton" then
		p.Image = ""
		p.ImageColor3 = Color3.new(1, 1, 1)
		p.ImageTransparency = 0
		p.ScaleType = "ScaleType.Stretch"
		p.SliceCenter = Rect.new(0, 0, 0, 0)
		p.SliceScale = 1
		p.ImageRectOffset = Vector2.new(0, 0)
		p.ImageRectSize = Vector2.new(0, 0)
		p.IsLoaded = true
	end
	if className == "TextButton" or className == "ImageButton" then
		p.AutoButtonColor = true
		p.Selectable = true
		p.Active = true
	end
	if className == "ScrollingFrame" then
		p.CanvasSize = UDim2.new(0, 0, 2, 0)
		p.CanvasPosition = Vector2.new(0, 0)
		p.AutomaticCanvasSize = "AutomaticSize.None"
		p.ScrollBarThickness = 12
		p.ScrollBarImageColor3 = Color3.new(0, 0, 0)
		p.ScrollBarImageTransparency = 0
		p.ScrollingDirection = "ScrollingDirection.XY"
		p.VerticalScrollBarInset = "ScrollBarInset.None"
		p.AbsoluteCanvasSize = Vector2.new(0, 0)
		p.AbsoluteWindowSize = Vector2.new(0, 0)
	end
	if className == "ScreenGui" then
		p.Enabled = true
		p.DisplayOrder = 0
		p.IgnoreGuiInset = false
		p.ResetOnSpawn = true
	end
	if className == "UIListLayout" or className == "UIGridLayout" then
		p.FillDirection = className == "UIListLayout" and "FillDirection.Vertical" or "FillDirection.Horizontal"
		p.HorizontalAlignment = "HorizontalAlignment.Left"
		p.VerticalAlignment = "VerticalAlignment.Top"
		p.SortOrder = "SortOrder.LayoutOrder"
		p.Padding = UDim.new(0, 0)
		p.CellSize = UDim2.new(0, 100, 0, 100)
		p.CellPadding = UDim2.new(0, 5, 0, 5)
		p.FillDirectionMaxCells = 0
		p.AbsoluteContentSize = Vector2.new(0, 0)
	end
	if className == "UIPadding" then
		p.PaddingLeft = UDim.new(0, 0)
		p.PaddingRight = UDim.new(0, 0)
		p.PaddingTop = UDim.new(0, 0)
		p.PaddingBottom = UDim.new(0, 0)
	end
	if className == "UICorner" then
		p.CornerRadius = UDim.new(0, 8)
	end
	if className == "UIStroke" then
		p.Color = Color3.new(0, 0, 0)
		p.Thickness = 1
		p.Transparency = 0
		p.ApplyStrokeMode = "ApplyStrokeMode.Contextual"
		p.Enabled = true
	end
	if className == "UIScale" then
		p.Scale = 1
	end
	if className == "UIGradient" then
		p.Color = ColorSequence.new(Color3.new(1, 1, 1))
		p.Transparency = NumberSequence.new(0)
		p.Rotation = 0
		p.Offset = Vector2.new(0, 0)
		p.Enabled = true
	end
	if className == "UITextSizeConstraint" then
		p.MaxTextSize = 100
		p.MinTextSize = 1
	end
	if className == "UISizeConstraint" then
		p.MinSize = Vector2.new(0, 0)
		p.MaxSize = Vector2.new(math.huge, math.huge)
	end
	if className == "UIAspectRatioConstraint" then
		p.AspectRatio = 1
		p.DominantAxis = "DominantAxis.Width"
		p.AspectType = "AspectType.FitWithinMaxSize"
	end
	return p
end

local EVENTS = {
	MouseEnter = true,
	MouseLeave = true,
	MouseButton1Down = true,
	MouseButton1Up = true,
	MouseButton1Click = true,
	MouseButton2Click = true,
	Activated = true,
	InputBegan = true,
	InputEnded = true,
	InputChanged = true,
	SelectionGained = true,
	SelectionLost = true,
	FocusLost = true,
	Focused = true,
	ChildAdded = true,
	ChildRemoved = true,
	DescendantAdded = true,
	Destroying = true,
	AncestryChanged = true,
	Changed = true,
	AttributeChanged = true,
	Completed = true,
	TouchTap = true,
	PromptShown = true,
	PromptHidden = true,
	PromptTriggered = true,
	PlayerAdded = true,
	PlayerRemoving = true,
	CharacterAdded = true,
	OnClientEvent = true,
	OnClientInvoke = true,
	RenderStepped = true,
	Heartbeat = true,
	Stepped = true,
	Event = true,
}

local InstanceMeta = {}
local Methods = {}

local function rawProps(self)
	return rawget(self, "__props")
end

InstanceMeta.__index = function(self, key)
	local props = rawProps(self)
	if key == "Parent" then
		return rawget(self, "__parent")
	end
	local value = props[key]
	-- A scene may stub a method on one instance (a remote's FireServer).
	if type(value) == "function" then
		return value
	end
	if Methods[key] then
		return Methods[key]
	end
	if value ~= nil then
		return value
	end
	if EVENTS[key] then
		local signal = newSignal()
		props[key] = signal
		return signal
	end
	-- Children by name, like Roblox's dot access.
	for _, child in rawget(self, "__children") do
		if child.Name == key then
			return child
		end
	end
	return nil
end

InstanceMeta.__newindex = function(self, key, value)
	if key == "Parent" then
		local old = rawget(self, "__parent")
		if old then
			local siblings = rawget(old, "__children")
			local i = table.find(siblings, self)
			if i then
				table.remove(siblings, i)
			end
		end
		rawset(self, "__parent", value)
		if value then
			table.insert(rawget(value, "__children"), self)
			local added = rawProps(value).ChildAdded
			if added then
				added:Fire(self)
			end
		end
		return
	end
	local props = rawProps(self)
	checkProperty(props.ClassName, key, value)
	local old = props[key]
	props[key] = value
	if old ~= value then
		local signals = rawget(self, "__changed")
		if signals[key] then
			signals[key]:Fire()
		end
	end
end

InstanceMeta.__tostring = function(self)
	return rawProps(self).Name
end

function Methods:IsA(className)
	local own = rawProps(self).ClassName
	if own == className or className == "Instance" then
		return true
	end
	for _, base in BASES[own] or {} do
		if base == className then
			return true
		end
	end
	return false
end
function Methods:GetChildren()
	return table.clone(rawget(self, "__children"))
end
function Methods:GetDescendants()
	local out = {}
	local function walk(node)
		for _, child in rawget(node, "__children") do
			table.insert(out, child)
			walk(child)
		end
	end
	walk(self)
	return out
end
function Methods:FindFirstChild(name, recursive)
	for _, child in rawget(self, "__children") do
		if child.Name == name then
			return child
		end
	end
	if recursive then
		for _, child in rawget(self, "__children") do
			local found = child:FindFirstChild(name, true)
			if found then
				return found
			end
		end
	end
	return nil
end
function Methods:FindFirstChildOfClass(className)
	for _, child in rawget(self, "__children") do
		if child.ClassName == className then
			return child
		end
	end
	return nil
end
function Methods:FindFirstChildWhichIsA(className)
	for _, child in rawget(self, "__children") do
		if child:IsA(className) then
			return child
		end
	end
	return nil
end
function Methods:FindFirstAncestorOfClass(className)
	local node = self.Parent
	while node do
		if node.ClassName == className then
			return node
		end
		node = node.Parent
	end
	return nil
end
function Methods:FindFirstAncestorWhichIsA(className)
	local node = self.Parent
	while node do
		if node:IsA(className) then
			return node
		end
		node = node.Parent
	end
	return nil
end
function Methods:WaitForChild(name)
	return self:FindFirstChild(name)
end
function Methods:IsDescendantOf(other)
	local node = self.Parent
	while node do
		if node == other then
			return true
		end
		node = node.Parent
	end
	return false
end
function Methods:Destroy()
	-- Roblox fires Destroying before taking the instance (and its subtree) apart.
	self.Destroying:Fire()
	for _, child in table.clone(rawget(self, "__children")) do
		child:Destroy()
	end
	self.Parent = nil
	rawset(self, "__destroyed", true)
end
function Methods:ClearAllChildren()
	for _, child in table.clone(rawget(self, "__children")) do
		child:Destroy()
	end
end
function Methods:GetPropertyChangedSignal(key)
	local signals = rawget(self, "__changed")
	signals[key] = signals[key] or newSignal()
	return signals[key]
end
function Methods:GetAttribute(name)
	return rawget(self, "__attributes")[name]
end
function Methods:SetAttribute(name, value)
	rawget(self, "__attributes")[name] = value
	local signals = rawget(self, "__attrChanged")
	if signals[name] then
		signals[name]:Fire()
	end
end
function Methods:GetAttributes()
	return table.clone(rawget(self, "__attributes"))
end
function Methods:GetAttributeChangedSignal(name)
	local signals = rawget(self, "__attrChanged")
	signals[name] = signals[name] or newSignal()
	return signals[name]
end
function Methods:Clone()
	local copy = Instance.new(rawProps(self).ClassName)
	for key, value in rawProps(self) do
		if type(value) ~= "table" or value.handlers == nil then
			rawProps(copy)[key] = value
		end
	end
	for _, child in rawget(self, "__children") do
		child:Clone().Parent = copy
	end
	return copy
end
function Methods:CaptureFocus() end
function Methods:ReleaseFocus() end
function Methods:IsFocused()
	return false
end

Instance = {}
local serial = 0
function Instance.new(className, parent)
	serial += 1
	local props = defaults(className)
	props.ClassName = className
	props.Name = className
	local object = setmetatable({
		__props = props,
		__children = {},
		__changed = {},
		__attributes = {},
		__attrChanged = {},
		__id = serial,
	}, InstanceMeta)
	if parent then
		object.Parent = parent
	end
	return object
end

-- Services --------------------------------------------------------------------------

local services = {}
local function service(name)
	if services[name] == nil then
		services[name] = Instance.new(name)
		rawProps(services[name]).Name = name
	end
	return services[name]
end

local LocalPlayer = Instance.new("Player")
rawProps(LocalPlayer).Name = "LiamTheMo"
rawProps(LocalPlayer).DisplayName = "LiamTheMo"
rawProps(LocalPlayer).UserId = 1
Instance.new("PlayerGui", LocalPlayer).Name = "PlayerGui"

local Players = service("Players")
rawProps(Players).LocalPlayer = LocalPlayer
function Methods:GetUserThumbnailAsync()
	return "rbxthumb://type=AvatarHeadShot&id=1&w=150&h=150", true
end
function Methods:GetPlayers()
	-- The local player, and any Player a scene parents to Players.
	local list = {}
	for _, child in Players:GetChildren() do
		if child.ClassName == "Player" then
			table.insert(list, child)
		end
	end
	return if #list > 0 then list else { LocalPlayer }
end
function Methods:GetPlayerByUserId(id)
	return if id == 1 then LocalPlayer else nil
end

function Methods:Create(object, info, goal)
	-- TweenService: tweens finish at once.
	local tween = { Completed = newSignal() }
	function tween.Play()
		for key, value in goal do
			object[key] = value
		end
		tween.Completed:Fire("PlaybackState.Completed")
	end
	function tween.Cancel() end
	function tween.Pause() end
	return tween
end
-- A scene may set __fetchStatus[content] = "AssetFetchStatus.Failure" etc.;
-- everything else reads as loaded.
function Methods:GetAssetFetchStatus(content)
	local statuses = __fetchStatus or {}
	return statuses[content] or "AssetFetchStatus.Success"
end
-- A scene may set __preloadStatus[content] = "AssetFetchStatus.Failure" etc.;
-- everything else preloads.
function Methods:PreloadAsync(list, callback)
	if callback then
		for _, item in list do
			local content = if type(item) == "string" then item else item.Image or ""
			local statuses = __preloadStatus or {}
			callback(content, statuses[content] or "AssetFetchStatus.Success")
		end
	end
end
-- capture.py injects __textWidths: advance widths per px of TextSize for the
-- legacy fonts the kit measures with (Merriweather, Patrick Hand), read from
-- the same font files render.py draws with. Other fonts use an average width.
function Methods:GetTextSize(text, size, font, frame)
	local widths = (__textWidths or {})[tostring(font)]
	local width = 0
	if widths then
		for _, code in utf8.codes(tostring(text)) do
			width += (widths[utf8.char(code)] or 0.6) * size
		end
	else
		width = #tostring(text) * size * 0.55
	end
	local lines = 1
	if frame and frame.X < width then
		lines = math.ceil(width / math.max(1, frame.X))
		width = frame.X
	end
	return Vector2.new(width, lines * size * 1.2)
end
function Methods:BindAction() end
function Methods:BindActionAtPriority() end
function Methods:UnbindAction() end
function Methods:GetLastInputType()
	return "UserInputType.MouseMovement"
end
function Methods:GetGuiInset()
	return Vector2.new(0, 58), Vector2.new(0, 0)
end
function Methods:IsKeyDown()
	return false
end
function Methods:GetMouseLocation()
	return Vector2.new(0, 0)
end
function Methods:SetCore() end
function Methods:SetCoreGuiEnabled() end
function Methods:IsStudio()
	return true
end
function Methods:IsClient()
	return true
end
function Methods:IsServer()
	return false
end
function Methods:JSONEncode(value)
	return __json(value)
end
function Methods:GenerateGUID()
	serial += 1
	return "guid-" .. serial
end
function Methods:PlayLocalSound() end
function Methods:InvokeServer()
	return false, "Offline"
end
function Methods:FireServer() end
function Methods:GetServerTimeNow()
	return 0
end

-- CollectionService tags (on any instance; the service's methods take it).
local tagged = {}
function Methods:AddTag(instance, tag)
	if tag == nil then
		instance, tag = self, instance
	end
	tagged[tag] = tagged[tag] or {}
	if not table.find(tagged[tag], instance) then
		table.insert(tagged[tag], instance)
	end
end
function Methods:RemoveTag(instance, tag)
	if tag == nil then
		instance, tag = self, instance
	end
	local list = tagged[tag] or {}
	local i = table.find(list, instance)
	if i then
		table.remove(list, i)
	end
end
function Methods:HasTag(instance, tag)
	if tag == nil then
		instance, tag = self, instance
	end
	return table.find(tagged[tag] or {}, instance) ~= nil
end
function Methods:GetTagged(tag)
	return table.clone(tagged[tag] or {})
end
local tagSignals = {}
function Methods:GetInstanceAddedSignal(tag)
	tagSignals[tag] = tagSignals[tag] or newSignal()
	return tagSignals[tag]
end
Methods.GetInstanceRemovedSignal = Methods.GetInstanceAddedSignal

-- BindableEvent:Fire reaches its Event's listeners.
function Methods:Fire(...)
	self.Event:Fire(...)
end

rawProps(service("UserInputService")).TouchEnabled = false
rawProps(service("UserInputService")).KeyboardEnabled = true
rawProps(service("UserInputService")).MouseEnabled = true
rawProps(service("UserInputService")).GamepadEnabled = false
rawProps(service("GuiService")).TopbarInset = Rect.new(0, 0, 1672, 58)
rawProps(service("GuiService")).ReducedMotionEnabled = false
rawProps(service("Workspace")).CurrentCamera = Instance.new("Camera")
rawProps(rawProps(service("Workspace")).CurrentCamera).ViewportSize = Vector2.new(1672, 941)

-- Module tree and require ---------------------------------------------------------------

local function node(path)
	local current = nil
	for index, name in path do
		if index == 1 then
			current = service(name)
		else
			local child = current:FindFirstChild(name)
			if child == nil then
				child = Instance.new("Folder")
				rawProps(child).Name = name
				child.Parent = current
			end
			current = child
		end
	end
	return current
end

local loaders = {}
local cache = {}

function __defineModule(path, loader)
	local module = node(path)
	rawProps(module).ClassName = "ModuleScript"
	loaders[module] = loader
end

local builtinRequire = require
function require(target)
	if type(target) ~= "table" or rawget(target, "__props") == nil then
		return builtinRequire(target)
	end
	if cache[target] == nil then
		local loader = loaders[target]
		assert(loader, "no module at " .. rawProps(target).Name)
		cache[target] = loader(target)
	end
	return cache[target]
end

game = Instance.new("DataModel")
function Methods:GetService(name)
	return service(name)
end
workspace = service("Workspace")

-- Time never passes in a capture: a spawned thread runs until its first wait and
-- then stays parked there (so refresh loops run once), and delays never fire.
-- A wait on the main thread returns at once.
task = {
	spawn = function(fn, ...)
		if type(fn) == "function" then
			local thread = coroutine.create(fn)
			local ok, err = coroutine.resume(thread, ...)
			if not ok then
				error(debug.traceback(thread, tostring(err)), 2)
			end
		end
	end,
	defer = function(fn, ...)
		if type(fn) == "function" then
			fn(...)
		end
	end,
	delay = function() end,
	wait = function()
		if coroutine.isyieldable() then
			coroutine.yield()
		end
		return 0
	end,
	cancel = function() end,
}
function wait()
	return 0
end
function tick()
	return 0
end
function time()
	return 0
end
function warn(...)
	print("WARN", ...)
end

-- JSON dump ----------------------------------------------------------------------------

local function jsonString(s)
	s = string.gsub(s, '[%c"\\]', function(c)
		if c == '"' then
			return '\\"'
		elseif c == "\\" then
			return "\\\\"
		elseif c == "\n" then
			return "\\n"
		end
		return string.format("\\u%04x", string.byte(c))
	end)
	return '"' .. s .. '"'
end

function __json(value)
	local kind = type(value)
	if kind == "nil" then
		return "null"
	elseif kind == "boolean" then
		return tostring(value)
	elseif kind == "number" then
		if value ~= value or value == math.huge or value == -math.huge then
			return if value > 0 then "1e9" else "-1e9"
		end
		return string.format("%.4f", value)
	elseif kind == "string" then
		return jsonString(value)
	elseif kind == "table" then
		if rawget(value, "__props") then
			return jsonString("<" .. rawProps(value).ClassName .. ">")
		end
		if value.handlers then
			return "null"
		end
		if #value > 0 then
			local parts = {}
			for _, item in value do
				table.insert(parts, __json(item))
			end
			return "[" .. table.concat(parts, ",") .. "]"
		end
		local parts = {}
		for key, item in value do
			if type(key) == "string" and type(item) ~= "function" then
				table.insert(parts, jsonString(key) .. ":" .. __json(item))
			end
		end
		return "{" .. table.concat(parts, ",") .. "}"
	end
	return "null"
end

local function dumpNode(object)
	local props = {}
	for key, value in rawProps(object) do
		if type(value) ~= "function" and not (type(value) == "table" and value.handlers) then
			props[key] = value
		end
	end
	local children = {}
	for _, child in rawget(object, "__children") do
		table.insert(children, dumpNode(child))
	end
	return { props = props, children = children }
end

function __dump(root, width, height)
	print("@@GUI@@" .. __json({ width = width, height = height, root = dumpNode(root) }) .. "@@END@@")
end

function __screen(width, height)
	local gui = Instance.new("ScreenGui")
	rawProps(gui).Name = "Capture"
	local root = Instance.new("Frame", gui)
	rawProps(root).Name = "Root"
	root.BackgroundTransparency = 1
	root.Size = UDim2.fromScale(1, 1)
	return gui, root
end

LocalPlayer.Parent = Players
