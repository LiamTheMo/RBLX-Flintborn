-- Reads the HUD layout (src/shared/UI/HudLayout.json) and turns its entries into
-- UDim2s, colours and fonts. Every position is in design px on the 1672×941
-- canvas the Kit is built at; the HUD root's UIScale (Kit.Scale.Hud) maps them
-- to the real screen. The world HUD's sections hold only places and sizes: its
-- art, type and colours come from the Kit (docs/ui/HudScreen.md). The colour
-- and font tables still serve the older Widgets and Parchment screens.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Layout = {}

local cached = nil
local loaded = false

-- The layout table, or nil when the JSON module is missing (for example a place
-- whose scripts were published without it); the old HUD then stays in charge.
function Layout.Get()
	if not loaded then
		loaded = true
		local folder = ReplicatedStorage:FindFirstChild("Shared")
		folder = folder and folder:FindFirstChild("UI")
		local module = folder and folder:FindFirstChild("HudLayout")
		if module and module:IsA("ModuleScript") then
			local ok, value = pcall(require, module)
			if ok and type(value) == "table" and type(value.reference) == "table" then
				cached = value
			end
		end
	end
	return cached
end

-- True on a short touch-only screen (a landscape phone), where the HUD canvas
-- is short and some regions move (an entry's "phonePos").
function Layout.IsPhone(): boolean
	local UserInputService = game:GetService("UserInputService")
	local camera = workspace.CurrentCamera
	return UserInputService.TouchEnabled
		and not UserInputService.KeyboardEnabled
		and camera ~= nil
		and camera.ViewportSize.Y > 0
		and camera.ViewportSize.Y < 500
end

-- Places a top-level widget: {anchor = [ax, ay], pos = [sx, ox, sy, oy], size =
-- [w, h], phonePos? (the position on phones)}.
function Layout.Place(object: GuiObject, entry)
	object.AnchorPoint = Vector2.new(entry.anchor[1], entry.anchor[2])
	local pos = if entry.phonePos and Layout.IsPhone() then entry.phonePos else entry.pos
	object.Position = UDim2.new(pos[1], pos[2], pos[3], pos[4])
	object.Size = UDim2.fromOffset(entry.size[1], entry.size[2])
end

-- A child rectangle [x, y, w, h] in its parent's reference pixels.
function Layout.Position(rect): UDim2
	return UDim2.fromOffset(rect[1], rect[2])
end

function Layout.Size(rect): UDim2
	return UDim2.fromOffset(rect[3], rect[4])
end

local colorCache = {}

function Layout.Color(key: string?): Color3
	local layout = Layout.Get()
	local hex = layout and layout.colors and layout.colors[key or "text"] or key
	if type(hex) ~= "string" then
		return Color3.new(1, 1, 1)
	end
	if colorCache[hex] == nil then
		local ok, color = pcall(Color3.fromHex, hex)
		colorCache[hex] = if ok then color else Color3.new(1, 1, 1)
	end
	return colorCache[hex]
end

function Layout.Font(key: string?): Enum.Font
	local layout = Layout.Get()
	local name = layout and layout.fonts and layout.fonts[key or "body"] or key
	local ok, font = pcall(function()
		return (Enum.Font :: any)[name]
	end)
	return if ok and font then font else Enum.Font.GothamMedium
end

local faceCache = {}

-- A FontFace for `key` from the layout's "fontFaces" ({family, weight}), or nil
-- when the key names only a classic font. Families are Roblox's built-in ones
-- (rbxasset://fonts/families/<family>.json).
function Layout.FontFace(key: string?): Font?
	local layout = Layout.Get()
	local spec = layout and layout.fontFaces and layout.fontFaces[key or ""]
	if type(spec) ~= "table" or type(spec.family) ~= "string" then
		return nil
	end
	if faceCache[key] == nil then
		local ok, face = pcall(function()
			local weight = (Enum.FontWeight :: any)[spec.weight or "Regular"] or Enum.FontWeight.Regular
			return Font.new("rbxasset://fonts/families/" .. spec.family .. ".json", weight)
		end)
		faceCache[key] = if ok then face else false
	end
	return faceCache[key] or nil
end

return Layout
