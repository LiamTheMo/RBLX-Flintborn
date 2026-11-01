-- Reads the HUD layout (src/shared/UI/HudLayout.json) and turns its entries into
-- UDim2s, colours and fonts. Every position is in design px on the 1672×941
-- canvas the Kit is built at; the HUD root's UIScale (Kit.Scale.Hud) maps them
-- to the real screen. The world HUD's sections hold only places and sizes: its
-- art, type and colours come from the Kit (docs/ui/HudScreen.md).

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local KitScale = require(script.Parent.Kit.Scale)

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

-- True on a phone (the kit's "phone" form factor: touch only, a short
-- landscape screen), where the HUD canvas is short and the regions take their
-- entries' "phone" overrides. Tablets keep the desktop arrangement.
function Layout.IsPhone(): boolean
	return KitScale.FormFactor() == "phone"
end

-- True on touch-only phones and tablets (Kit.Scale.IsSmallTouch): the HUD
-- draws small there and body text is boosted, so text-heavy regions take their
-- entries' "touch" overrides (bigger text, two-line rows).
function Layout.IsTouchScreen(): boolean
	return KitScale.IsSmallTouch()
end

-- `entry` for this screen: on phones and tablets the fields of its "touch"
-- table replace the desktop ones (text sizes, row shapes), and on phones those
-- of its "phone" table too (positions and sizes for the short canvas).
function Layout.ForScreen(entry)
	if type(entry) ~= "table" or (entry.touch == nil and entry.phone == nil) then
		return entry
	end
	local touch = if type(entry.touch) == "table" and Layout.IsTouchScreen() then entry.touch else nil
	local phone = if type(entry.phone) == "table" and Layout.IsPhone() then entry.phone else nil
	if touch == nil and phone == nil then
		return entry
	end
	local merged = table.clone(entry)
	for _, override in { touch or {}, phone or {} } do
		for key, value in override do
			merged[key] = value
		end
	end
	return merged
end

-- The layout section `key` for this screen (Layout.ForScreen).
function Layout.Section(layout, key: string)
	return Layout.ForScreen(layout[key])
end

-- Places a top-level widget: {anchor = [ax, ay], pos = [sx, ox, sy, oy], size =
-- [w, h], phone? = {anchor?, pos?, size?}} (the phone override wins on phones).
function Layout.Place(object: GuiObject, entry)
	entry = Layout.ForScreen(entry)
	object.AnchorPoint = Vector2.new(entry.anchor[1], entry.anchor[2])
	local pos = entry.pos
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

return Layout
