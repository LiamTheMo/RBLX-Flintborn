-- Sprite drawing for the UI art sheets (art/ui/sprites): an uploaded sprite is
-- an ImageLabel (9-sliced when the manifest gives slice insets; from an uploaded
-- atlas it is nine plain pieces), loaded through SpriteLoader's pacing, and art
-- too big for one upload is laid together from tiles. Without art, Sprite
-- returns an empty frame in its place: the kit (Hud/Kit/Art) checks HasArt and
-- draws its own stand-ins, so nothing here needs a look of its own.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local UiAssets = require(ReplicatedStorage.Shared.UI.UiAssets)
local SpriteLoader = require(script.Parent.SpriteLoader)

local Widgets = {}

local function apply(object: Instance, props)
	if props then
		for key, value in props do
			(object :: any)[key] = value
		end
	end
	return object
end

-- Properties only images have: a stand-in Frame (or a tiled sprite's holder)
-- skips them, so a caller can tint or slice a sprite without knowing whether its
-- art is uploaded yet.
local IMAGE_ONLY = {
	Image = true,
	ImageColor3 = true,
	ImageTransparency = true,
	ImageRectOffset = true,
	ImageRectSize = true,
	ResampleMode = true,
	ScaleType = true,
	SliceCenter = true,
	SliceScale = true,
	TileSize = true,
}

local function applyFrame(object: Instance, props)
	if props then
		for key, value in props do
			if not IMAGE_ONLY[key] then
				(object :: any)[key] = value
			end
		end
	end
	return object
end

function Widgets.Make(className: string, props, parent: Instance?)
	local object = Instance.new(className)
	apply(object, props)
	object.Parent = parent
	return object
end

-- The capture harness (art/ui/capture) applies text caps in layout pixels.
local CAPTURE = (__FlintbornCapture :: any) == true

-- The capture harness (art/ui/capture) applies text caps in layout pixels.
local CAPTURE = (__FlintbornCapture :: any) == true

-- Caps scaled text at `maxSize` layout pixels (and keeps it at least `minSize`
-- screen pixels). Roblox applies a UITextSizeConstraint in screen pixels, after
-- any UIScale, so on a window drawn smaller (phones) a cap in layout pixels let
-- text grow far past its design; the cap follows the UIScales above the label.
function Widgets.TextCap(label: GuiObject, maxSize: number, minSize: number?)
	local floor = minSize or 1
	local cap = Widgets.Make("UITextSizeConstraint", { MaxTextSize = maxSize, MinTextSize = floor }, label)
	if CAPTURE then
		return cap
	end
	local function update()
		local k = 1
		local node: Instance? = label
		while node do
			local scale = node:FindFirstChildWhichIsA("UIScale")
			if scale then
				k *= scale.Scale
			end
			node = node.Parent
		end
		local top = math.max(1, math.floor(maxSize * k + 0.5))
		cap.MaxTextSize = top
		cap.MinTextSize = math.min(floor, top)
	end
	label:GetPropertyChangedSignal("AbsoluteSize"):Connect(update)
	label.AncestryChanged:Connect(update)
	update()
	return cap
end

local function targetSize(props): (number, number)
	local size = props and props.Size
	if typeof(size) == "UDim2" then
		return size.X.Offset, size.Y.Offset
	end
	return 0, 0
end

-- Without art: an empty frame where the sprite would be (callers that want a
-- look of their own check HasArt first, as the kit does).
local function fallback(name: string, props, parent: Instance?)
	local frame = Widgets.Make("Frame", { Name = name, BackgroundTransparency = 1, BorderSizePixel = 0 }, parent)
	return applyFrame(frame, props)
end

-- The uploaded atlas holding sprite `name` (art/ui/pack_atlas.py), or nil.
local function atlasImage(name: string): string?
	local sprite = UiAssets.sprite(name)
	if sprite and type(sprite.atlas) == "string" and type(sprite.rect) == "table" then
		return UiAssets.image(sprite.atlas)
	end
	return nil
end

-- True when sprite `name` can draw as art (an uploaded image or an uploaded
-- atlas holding it, or uploaded tiles); false means Widgets.Sprite would draw a
-- stand-in. The kit (Hud/Kit/Art) draws its own stand-ins in the kit's style.
function Widgets.HasArt(name: string): boolean
	local whole = UiAssets.sprite(name)
	if whole and type(whole.tiles) == "table" then
		for _, tile in whole.tiles do
			if atlasImage(tile[1]) == nil and UiAssets.image(tile[1]) == nil then
				return false
			end
		end
		return true
	end
	return atlasImage(name) ~= nil or UiAssets.image(name) ~= nil
end

-- Image properties a nine-piece sprite's holder passes on to its pieces.
local PASSED_ON = { "ImageColor3", "ImageTransparency", "ZIndex" }

-- A 9-sliced sprite from an atlas, drawn as nine plain pieces: each its own
-- rectangle of the atlas, stretched (corners keep their size, edges stretch one
-- way, the centre both). Phones drew Roblox's Slice of an atlas rectangle wrongly
-- (pieces cut, shifted, or taken from neighbouring sprites), while plain atlas
-- rectangles draw right everywhere. The holder is an ImageLabel without an image
-- of its own whose tint, transparency and ZIndex pass on to the pieces, so callers
-- treat it as any sprite.
local function nineSlice(name: string, sprite, id: string, props, parent: Instance?, sliceScale: number?): GuiObject
	local holder = Widgets.Make("ImageLabel", { Name = name, BackgroundTransparency = 1, Image = "" }, parent)
	local width, height = targetSize(props)
	local scale = sliceScale
		or (if width > 0 and height > 0 then HudModel.SliceScale(sprite.w, sprite.h, width, height) else 1)
	local l, t, r, b = sprite.slice[1], sprite.slice[2], sprite.slice[3], sprite.slice[4]
	local rx, ry = sprite.rect[1], sprite.rect[2]
	local xs = { 0, l, sprite.w - r, sprite.w }
	local ys = { 0, t, sprite.h - b, sprite.h }
	-- Each column (row): {scale, offset} of its position and of its size.
	-- Corners are whole pixels and the edge and centre pieces reach 1 px under
	-- their neighbours, so no seam opens at a fractional slice scale.
	local L, T = math.round(l * scale), math.round(t * scale)
	local R, B = math.round(r * scale), math.round(b * scale)
	local columns = {
		{ 0, 0, 0, L },
		{ 0, L - 1, 1, -(L + R) + 2 },
		{ 1, -R, 0, R },
	}
	local rows = {
		{ 0, 0, 0, T },
		{ 0, T - 1, 1, -(T + B) + 2 },
		{ 1, -B, 0, B },
	}
	local pieces = {}
	for i = 1, 3 do
		for j = 1, 3 do
			local w, h = xs[i + 1] - xs[i], ys[j + 1] - ys[j]
			if w > 0 and h > 0 then
				local column, row = columns[i], rows[j]
				local piece = Widgets.Make("ImageLabel", {
					Name = "Piece" .. i .. j,
					BackgroundTransparency = 1,
					ImageRectOffset = Vector2.new(rx + xs[i], ry + ys[j]),
					ImageRectSize = Vector2.new(w, h),
					Position = UDim2.new(column[1], column[2], row[1], row[2]),
					ScaleType = Enum.ScaleType.Stretch,
					Size = UDim2.new(column[3], column[4], row[3], row[4]),
				}, holder)
				SpriteLoader.Assign(piece, id)
				table.insert(pieces, piece)
			end
		end
	end
	for _, key in PASSED_ON do
		local function pass()
			for _, piece in pieces do
				(piece :: any)[key] = (holder :: any)[key]
			end
		end
		holder:GetPropertyChangedSignal(key):Connect(pass)
		pass()
	end
	return apply(holder, props)
end

-- Art larger than Roblox's 1024 px upload limit goes up as tiles (manifest
-- "tiles": [tile name, x, y, w, h]); a Frame lays them back together, each at its
-- share of the whole, so the sprite still resizes as one image.
local function tiled(name: string, sprite, props, parent: Instance?): GuiObject?
	local ids = {}
	for _, tile in sprite.tiles do
		local id = atlasImage(tile[1]) or UiAssets.image(tile[1])
		if id == nil then
			return nil
		end
		ids[tile[1]] = id
	end
	local holder = Widgets.Make("Frame", { Name = name, BackgroundTransparency = 1 }, parent)
	applyFrame(holder, props)
	for _, tile in sprite.tiles do
		local image = Widgets.Make("ImageLabel", {
			Name = tile[1],
			BackgroundTransparency = 1,
			ScaleType = Enum.ScaleType.Stretch,
			Position = UDim2.fromScale(tile[2] / sprite.w, tile[3] / sprite.h),
			Size = UDim2.fromScale(tile[4] / sprite.w, tile[5] / sprite.h),
			ZIndex = holder.ZIndex,
		}, holder)
		local piece = UiAssets.sprite(tile[1])
		if atlasImage(tile[1]) and piece then
			image.ImageRectOffset = Vector2.new(piece.rect[1], piece.rect[2])
			image.ImageRectSize = Vector2.new(piece.rect[3], piece.rect[4])
		end
		SpriteLoader.Assign(image, ids[tile[1]])
	end
	return holder
end

-- An image from the art sheets by sprite name, or its styled fallback. A sprite
-- packed into an uploaded atlas (art/ui/pack_atlas.py) is drawn as its
-- rectangle of the atlas, so a screen fetches one image for many sprites (phones
-- refuse bursts of separate downloads); otherwise it is its own image.
-- `sliceScale` overrides the automatic 9-slice corner scale (layout "sliceScale").
function Widgets.Sprite(name: string, props, parent: Instance?, sliceScale: number?): GuiObject
	local whole = UiAssets.sprite(name)
	-- Art too big for one image is laid together from its tiles.
	if whole and type(whole.tiles) == "table" then
		return tiled(name, whole, props, parent) or fallback(name, props, parent)
	end
	local atlas = atlasImage(name)
	local id = atlas or UiAssets.image(name)
	if id == nil then
		return fallback(name, props, parent)
	end
	local center = UiAssets.sliceCenter(name)
	if atlas and center then
		return nineSlice(name, whole, atlas, props, parent, sliceScale)
	end
	local image = Widgets.Make("ImageLabel", { Name = name, BackgroundTransparency = 1 }, parent)
	if atlas then
		image.ImageRectOffset = Vector2.new(whole.rect[1], whole.rect[2])
		image.ImageRectSize = Vector2.new(whole.rect[3], whole.rect[4])
	end
	SpriteLoader.Assign(image, id)
	local sprite = UiAssets.sprite(name)
	if center and sprite then
		image.ScaleType = Enum.ScaleType.Slice
		image.SliceCenter = center
		local width, height = targetSize(props)
		if sliceScale then
			image.SliceScale = sliceScale
		elseif width > 0 and height > 0 then
			image.SliceScale = HudModel.SliceScale(sprite.w, sprite.h, width, height)
		end
	elseif string.sub(name, 1, 5) == "fill_" then
		image.ScaleType = Enum.ScaleType.Stretch
	else
		image.ScaleType = Enum.ScaleType.Fit
	end
	return apply(image, props)
end

return Widgets
