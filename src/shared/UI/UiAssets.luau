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
-- pixels; `of` names the sprite). A copy's own `hi` names a sharper copy (the
-- tusk: its 2x copy, then its hero copy for the Forge picture). The sprite's own
-- w, h and slice stay the design size every layout uses. Placement picks the
-- sharpest copy whose magnification is reached (HiFrom) and whose image is
-- uploaded, else the sprite's own (1x) art, so an atlas that is not uploaded yet
-- never draws: its sprites keep drawing their 1x art from the atlases already
-- uploaded, each with its own rects.

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

-- Copies up to HI_MAX times the pixels (the slicer's 2x copies of frames,
-- buttons and icons, the island map's 2.04x) draw past HI_FROM. A sharper copy
-- (an item's hero copy, 2.6x to 4.9x) draws only where the art is magnified
-- past HERO_FROM and past scale / HI_SHRINK, so it is never shrunk more than 2x
-- at 1440p (windows draw at 1.4 there: HI_SHRINK = 2 x 1.4): in the Forge
-- picture and the Inventory detail card, never in slots, rows or the Journal
-- illustration (Kit.Icon caps those at 1).
UiAssets.HI_MAX = 2.1
UiAssets.HERO_FROM = 1
UiAssets.HI_SHRINK = 2.8

-- The magnification (design px drawn per design px of the sprite) past which a
-- copy of `scale` draws.
function UiAssets.HiFrom(scale: number): number
	if scale <= UiAssets.HI_MAX then
		return UiAssets.HI_FROM
	end
	return math.max(UiAssets.HERO_FROM, scale / UiAssets.HI_SHRINK)
end

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

export type Copy = {
	name: string, -- the copy's entry name
	entry: any, -- its entry (w, h, slice, rect in its own pixels)
	scale: number, -- its pixels per design pixel of the sprite
	from: number, -- the magnification past which it draws (HiFrom)
}

-- The high-resolution copies of sprite `name`, least sharp first (its `hi`,
-- then that copy's `hi`, ...), uploaded or not; empty when it has none.
function UiAssets.Copies(name: string, sprites: any?): { Copy }
	sprites = sprites or UiAssets.Sprites
	local copies = {}
	local base = entryOf(sprites, name)
	local link = base and base.hi
	while type(link) == "string" and #copies < 4 do
		local copy = entryOf(sprites, link)
		if copy == nil then
			break
		end
		local scale = if type(copy.scale) == "number" and copy.scale > 0 then copy.scale else copy.w / base.w
		table.insert(copies, { name = link, entry = copy, scale = scale, from = UiAssets.HiFrom(scale) })
		link = copy.hi
	end
	return copies
end

-- The art sprite `name` draws from when it is magnified `mag` times (design px
-- drawn per design px of the sprite; nil when unknown, which prefers the
-- sharpest copy): the sharpest copy whose image is uploaded and whose `from`
-- the magnification exceeds, else its own art; nil when none is uploaded.
-- `sprites` and `imageOf(name) -> id?` default to UiSprites.json and
-- UiAssetIds.json.
function UiAssets.Placement(name: string, mag: number?, sprites: any?, imageOf: ((string) -> string?)?): Placement?
	sprites = sprites or UiAssets.Sprites
	local lookup: (string) -> string? = imageOf or UiAssets.image
	local base = entryOf(sprites, name)
	if base == nil then
		return nil
	end
	local copies = UiAssets.Copies(name, sprites)
	for index = #copies, 1, -1 do
		local copy = copies[index]
		if mag == nil or mag > copy.from then
			local placement = placementOf(sprites, lookup, copy.name, copy.entry)
			if placement then
				placement.scale = copy.scale
				return placement
			end
		end
	end
	return placementOf(sprites, lookup, name, base)
end

return UiAssets
