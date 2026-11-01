-- Uploaded UI image ids and sprite slice data (GDD §11). Rojo turns the JSON files
-- beside this module into ModuleScripts:
--   UiAssetIds.json  {name: assetId}, written by scripts/roblox_upload_ui_assets.py
--                    ("" is a placeholder: packed but not uploaded yet)
--   UiSprites.json   {name: {w, h, slice = [left, top, right, bottom] or null,
--                    atlas?, rect?, tiles?, hi?}}, copied from art/ui/sprites/manifest.json
-- A sprite without an uploaded id returns nil, and the HUD draws a styled Frame
-- in its place, so the UI works before (and without) any upload.
--
-- High-resolution copies: a sprite's `hi` names another entry, the same art at
-- `scale` times the pixels (w, h, slice and rect of the copy are in its own
-- pixels; `of` names the sprite). The sprite's own w, h and slice stay the design
-- size every layout uses. Placement picks the copy where the art is magnified and
-- the copy's image is uploaded, else the sprite's own (1x) art, so an atlas that
-- is not uploaded yet never draws: its sprites keep drawing their 1x art from
-- the atlases already uploaded, each with its own rects.

local UiAssets = {}

local function loadJson(name: string)
	local ok, value = pcall(function()
		local module = script.Parent:FindFirstChild(name)
		if module == nil or not module:IsA("ModuleScript") then
			return {}
		end
		return require(module)
	end)
	if ok and type(value) == "table" then
		return value
	end
	return {}
end

-- name -> "rbxassetid://<id>"
UiAssets.Ids = {}
-- name -> {w, h, slice}
UiAssets.Sprites = loadJson("UiSprites")

-- "rbxassetid://<id>" for an id from UiAssetIds.json, or nil for a missing or
-- placeholder ("") id.
function UiAssets.AssetUrl(id: any): string?
	if type(id) == "number" and id > 0 then
		return "rbxassetid://" .. string.format("%d", id)
	elseif type(id) == "string" and id ~= "" then
		return if string.find(id, "^rbxassetid://") then id else "rbxassetid://" .. id
	end
	return nil
end

for name, id in loadJson("UiAssetIds") do
	UiAssets.Ids[name] = UiAssets.AssetUrl(id)
end

-- The uploaded image for a sprite name, or nil when it has not been uploaded.
function UiAssets.image(name: string): string?
	return UiAssets.Ids[name]
end

local function entryOf(sprites, name: string?)
	local sprite = name and sprites[name]
	if type(sprite) ~= "table" or type(sprite.w) ~= "number" or type(sprite.h) ~= "number" then
		return nil
	end
	return sprite
end

-- Natural size and slice insets for a sprite, or nil when the manifest lacks it.
function UiAssets.sprite(name: string)
	return entryOf(UiAssets.Sprites, name)
end

-- The 9-slice centre (Roblox SliceCenter) for a sprite, or nil when it does not slice.
function UiAssets.sliceCenter(name: string): Rect?
	local sprite = UiAssets.sprite(name)
	local slice = sprite and sprite.slice
	if type(slice) ~= "table" or #slice ~= 4 then
		return nil
	end
	return Rect.new(slice[1], slice[2], sprite.w - slice[3], sprite.h - slice[4])
end

-- The high-resolution copy is drawn once the art would be magnified past this
-- (design px drawn per design px of the sprite). Below it the 1x art is sharp
-- enough at every UI scale (≤ 1.05 at 1440p), and the copy would be shrunk more
-- than 2x.
UiAssets.HI_FROM = 0.75

export type Placement = {
	name: string, -- the entry drawn: the sprite or its copy
	entry: any, -- that entry (w, h, slice, rect in its own pixels)
	image: string?, -- its image (an atlas or its own); nil for tiled art
	rect: { number }?, -- its rect in the atlas image
	scale: number, -- its pixels per design pixel of the sprite
}

-- Where one entry draws from: its atlas, else its own image, else (tiled art)
-- its tiles when every tile has an image. nil when nothing is uploaded.
local function placementOf(sprites, imageOf, name: string, entry): Placement?
	if type(entry.tiles) == "table" then
		for _, tile in entry.tiles do
			local piece = entryOf(sprites, tile[1])
			local atlas = piece and type(piece.atlas) == "string" and piece.rect and imageOf(piece.atlas)
			if not atlas and not imageOf(tile[1]) then
				return nil
			end
		end
		return { name = name, entry = entry, scale = 1 }
	end
	if type(entry.atlas) == "string" and type(entry.rect) == "table" then
		local atlas = imageOf(entry.atlas)
		if atlas then
			return { name = name, entry = entry, image = atlas, rect = entry.rect, scale = 1 }
		end
	end
	local own = imageOf(name)
	if own then
		return { name = name, entry = entry, image = own, scale = 1 }
	end
	return nil
end

-- The art sprite `name` draws from when it is magnified `mag` times (design px
-- drawn per design px of the sprite; nil when unknown, which prefers the copy):
-- its high-resolution copy when it has one whose image is uploaded and mag >
-- HI_FROM, else its own art; nil when neither is uploaded. `sprites` and
-- `imageOf(name) -> id?` default to UiSprites.json and UiAssetIds.json.
function UiAssets.Placement(name: string, mag: number?, sprites: any?, imageOf: ((string) -> string?)?): Placement?
	sprites = sprites or UiAssets.Sprites
	local lookup: (string) -> string? = imageOf or UiAssets.image
	local base = entryOf(sprites, name)
	if base == nil then
		return nil
	end
	local hi = type(base.hi) == "string" and entryOf(sprites, base.hi)
	if hi and (mag == nil or mag > UiAssets.HI_FROM) then
		local placement = placementOf(sprites, lookup, base.hi, hi)
		if placement then
			placement.scale = if type(hi.scale) == "number" and hi.scale > 0 then hi.scale else hi.w / base.w
			return placement
		end
	end
	return placementOf(sprites, lookup, name, base)
end

-- The pixel size {w, h} of a sprite's sharpest art (its high-resolution copy's
-- full size when it has one, else its own), uploaded or not; nil when unknown.
function UiAssets.PixelSize(name: string, sprites: any?): (number?, number?)
	sprites = sprites or UiAssets.Sprites
	local base = entryOf(sprites, name)
	if base == nil then
		return nil, nil
	end
	local hi = type(base.hi) == "string" and entryOf(sprites, base.hi)
	if hi and type(hi.scale) == "number" then
		-- A 9-sliced copy's middle is stored short: its full size is the design
		-- size at its scale.
		return base.w * hi.scale, base.h * hi.scale
	end
	return base.w, base.h
end

return UiAssets
