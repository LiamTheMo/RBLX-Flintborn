-- Uploaded UI image ids and sprite slice data (GDD §11). Rojo turns the JSON files
-- beside this module into ModuleScripts:
--   UiAssetIds.json  {name: assetId}, written by scripts/roblox_upload_ui_assets.py
--   UiSprites.json   {name: {w, h, slice = [left, top, right, bottom] or null}},
--                    copied from art/ui/sprites/manifest.json
-- A sprite without an uploaded id returns nil, and the HUD draws a styled Frame
-- in its place, so the UI works before (and without) any upload.

local UiAssets = {}

local function loadJson(name: string)
	local module = script.Parent:FindFirstChild(name)
	if module == nil or not module:IsA("ModuleScript") then
		return {}
	end
	local ok, value = pcall(require, module)
	if ok and type(value) == "table" then
		return value
	end
	return {}
end

-- name -> "rbxassetid://<id>"
UiAssets.Ids = {}
-- name -> {w, h, slice}
UiAssets.Sprites = loadJson("UiSprites")

for name, id in loadJson("UiAssetIds") do
	if type(id) == "number" then
		UiAssets.Ids[name] = "rbxassetid://" .. string.format("%d", id)
	elseif type(id) == "string" and id ~= "" then
		UiAssets.Ids[name] = if string.find(id, "^rbxassetid://") then id else "rbxassetid://" .. id
	end
end

-- The uploaded image for a sprite name, or nil when it has not been uploaded.
function UiAssets.image(name: string): string?
	return UiAssets.Ids[name]
end

-- Natural size and slice insets for a sprite, or nil when the manifest lacks it.
function UiAssets.sprite(name: string)
	local sprite = UiAssets.Sprites[name]
	if type(sprite) ~= "table" or type(sprite.w) ~= "number" or type(sprite.h) ~= "number" then
		return nil
	end
	return sprite
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

return UiAssets
