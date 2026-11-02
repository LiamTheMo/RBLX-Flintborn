-- Reads the HUD layout (src/shared/UI/HudLayout.json) and turns its entries into
-- UDim2s, colours and fonts. Every position is in design px on the 1672×941
-- canvas the Kit is built at; the HUD root's UIScale (Kit.Scale.Hud) maps them
-- to the real screen. The world HUD's sections hold only places and sizes: its
-- art, type and colours come from the Kit (docs/ui/HudScreen.md).

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
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

-- The HUD layout grid (HudLayout "grid", ARCHITECTURE D30): {margin, gap,
-- column, topBand, bottomBand}; both HUDs place their edge regions on it.
function Layout.Grid()
	local layout = Layout.Get()
	return layout and layout.grid
end

-- The ⚙ corner button both HUDs share (HudLayout "gear"): {size, ringGap, pad}.
function Layout.Gear()
	local layout = Layout.Get()
	return layout and layout.gear
end

-- An entry placed on the grid by its "column" (D30): "right" (the right-hand
-- column: the grid's margin from the right and the top, the column's width),
-- "left" (the margin from the left; vertically centred at "centreY" when it
-- has one, else at the top) or "bottom" (centred, the margin from the
-- bottom). An entry with a "height" gets its size: the column's width (or its
-- own "width") by that height. The HUD's placement (Layout.PlaceColumns)
-- then stacks the columns and keeps each to one edge.
local function onGrid(entry)
	local column = entry.column
	if column ~= "right" and column ~= "left" and column ~= "bottom" then
		return entry
	end
	local grid = Layout.Grid()
	local m = grid.margin
	local out = table.clone(entry)
	if column == "right" then
		out.anchor, out.pos = { 1, 0 }, { 1, -m, 0, m }
	elseif column == "left" and type(entry.centreY) == "number" then
		out.anchor, out.pos = { 0, 0.5 }, { 0, m, entry.centreY, 0 }
	elseif column == "left" then
		out.anchor, out.pos = { 0, 0 }, { 0, m, 0, m }
	else
		out.anchor, out.pos = { 0.5, 1 }, { 0.5, 0, 1, -m }
	end
	if type(entry.height) == "number" then
		out.size = { entry.width or grid.column, entry.height }
	end
	return out
end

-- `entry` for this screen: on phones and tablets the fields of its "touch"
-- table replace the desktop ones (text sizes, row shapes), and on phones those
-- of its "phone" table too (positions and sizes for the short canvas); then
-- its place on the grid (its "column").
function Layout.ForScreen(entry)
	if type(entry) ~= "table" then
		return entry
	end
	local touch = if type(entry.touch) == "table" and Layout.IsTouchScreen() then entry.touch else nil
	local phone = if type(entry.phone) == "table" and Layout.IsPhone() then entry.phone else nil
	if touch == nil and phone == nil then
		return onGrid(entry)
	end
	local merged = table.clone(entry)
	for _, override in { touch or {}, phone or {} } do
		for key, value in override do
			merged[key] = value
		end
	end
	return onGrid(merged)
end

-- The layout section `key` for this screen (Layout.ForScreen).
function Layout.Section(layout, key: string)
	return Layout.ForScreen(layout[key])
end

-- Places a top-level widget: {anchor = [ax, ay], pos = [sx, ox, sy, oy], size =
-- [w, h], phone? = {anchor?, pos?, size?}} (the phone override wins on phones),
-- or an entry on the grid ({column, height?}).
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

-- The menu tile grid both HUDs draw (HudLayout "tiles", for this screen):
-- `count` tiles `columns` to a row at the entry's tile size and pitch.
-- Returns {w, h, columns, rects = {{x, y, w, h}}} in the grid's own px.
function Layout.TileGrid(cfg, count: number)
	local columns = cfg.columns or 2
	local rows = math.ceil(count / columns)
	local rects = {}
	for index = 1, count do
		local column, row = (index - 1) % columns, (index - 1) // columns
		rects[index] = { column * cfg.pitch[1], row * cfg.pitch[2], cfg.tile[1], cfg.tile[2] }
	end
	return {
		w = (columns - 1) * cfg.pitch[1] + cfg.tile[1],
		h = (rows - 1) * cfg.pitch[2] + cfg.tile[2],
		columns = columns,
		rects = rects,
	}
end

-- A region's top and bottom in design px on a root `rootH` tall.
local function span(object: GuiObject, rootH: number): (number, number)
	local h = object.Size.Y.Scale * rootH + object.Size.Y.Offset
	local top = object.Position.Y.Scale * rootH + object.Position.Y.Offset - object.AnchorPoint.Y * h
	return top, top + h
end

-- Places the HUD's side columns on the grid (ARCHITECTURE D30), the one
-- placement both HUDs use. `columns` = {right?, left?}, each {stack =
-- {GuiObject}, top = design px, free = {GuiObject}?}: the stack's shown pieces
-- go one under another from `top` with the grid's gap between them (a hidden
-- piece takes no room); `free` pieces keep their own height (the desktop menu
-- tiles, centred). Then each column keeps one edge: the grid's margin from
-- the screen's side when every shown piece lies in a corner band, else the
-- margin or the device safe inset on that side, whichever is larger
-- (HudModel.EdgeGap over the whole column). `screen` is Kit.Scale.HudScreen's.
-- Returns {side = gap in design px}.
function Layout.PlaceColumns(columns, screen)
	local grid = Layout.Grid()
	local k = math.max(screen.scale or 1, 0.01)
	local rootH = (screen.height or 0) / k
	local insets = screen.insets or HudModel.NO_INSETS
	local placed = {}
	for side, column in columns do
		local heights = {}
		for index, object in column.stack do
			heights[index] = if object.Visible then object.Size.Y.Offset else false
		end
		local tops = HudModel.Stack(column.top, heights, grid.gap)
		for index, object in column.stack do
			if tops[index] then
				local x = object.Position.X
				object.Position = UDim2.new(x.Scale, x.Offset, 0, tops[index] + object.AnchorPoint.Y * heights[index])
			end
		end
		local all = table.clone(column.stack)
		table.move(column.free or {}, 1, #(column.free or {}), #all + 1, all)
		local lo, hi = math.huge, -math.huge
		for _, object in all do
			if object.Visible then
				local top, bottom = span(object, rootH)
				lo, hi = math.min(lo, top), math.max(hi, bottom)
			end
		end
		local gap = if lo < hi
			then HudModel.EdgeGap(grid, lo * k, hi * k, screen.height, insets[side], k)
			else grid.margin
		for _, object in all do
			local w, ax = object.Size.X.Offset, object.AnchorPoint.X
			local y = object.Position.Y
			object.Position = if side == "left"
				then UDim2.new(0, gap + ax * w, y.Scale, y.Offset)
				else UDim2.new(1, -gap - (1 - ax) * w, y.Scale, y.Offset)
		end
		placed[side] = gap
	end
	return placed
end

return Layout
