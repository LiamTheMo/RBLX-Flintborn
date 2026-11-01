local Shared = game:GetService("ReplicatedStorage").Shared
local UiAssets = require(Shared.UI.UiAssets)

-- A sprite with a 2x copy in an atlas of its own, the way the slicer and
-- pack_atlas.py write them (the copy's size, insets and rect in its own pixels).
local SPRITES = {
	frame = {
		w = 100,
		h = 50,
		slice = { 10, 8, 10, 8 },
		atlas = "atlas_old",
		rect = { 4, 4, 100, 50 },
		hi = "frame__hi",
	},
	frame__hi = {
		w = 120,
		h = 76,
		slice = { 20, 16, 20, 16 },
		atlas = "atlas_new",
		rect = { 0, 0, 120, 76 },
		scale = 2,
		of = "frame",
	},
	plain = { w = 40, h = 40, atlas = "atlas_old", rect = { 110, 4, 40, 40 } },
	map = { w = 1000, h = 1000, atlas = "atlas_map", rect = { 0, 0, 1000, 1000 }, hi = "map__hi" },
	map__hi = {
		w = 2040,
		h = 2040,
		scale = 2.04,
		of = "map",
		tiles = { { "map__hi__1_1", 0, 0, 1022, 2040 }, { "map__hi__1_2", 1018, 0, 1022, 2040 } },
	},
	map__hi__1_1 = { w = 1022, h = 2040, atlas = "atlas_map_hi_1", rect = { 0, 0, 1022, 2040 } },
	map__hi__1_2 = { w = 1022, h = 2040, atlas = "atlas_map_hi_2", rect = { 0, 0, 1022, 2040 } },
}

local function ids(list)
	return function(name: string)
		return list[name]
	end
end

test("asset ids: numbers and strings, placeholders read as missing", function()
	expectEq(UiAssets.AssetUrl(123), "rbxassetid://123", "number")
	expectEq(UiAssets.AssetUrl("456"), "rbxassetid://456", "string")
	expectEq(UiAssets.AssetUrl("rbxassetid://7"), "rbxassetid://7", "already a url")
	expectEq(UiAssets.AssetUrl(""), nil, "an empty placeholder is not uploaded")
	expectEq(UiAssets.AssetUrl(0), nil, "zero is not an id")
	expectEq(UiAssets.AssetUrl(nil), nil, "missing")
end)

test("a copy whose atlas is not uploaded never draws: the 1x art does", function()
	local only = ids({ atlas_old = "rbxassetid://1" })
	local p = UiAssets.Placement("frame", 1, SPRITES, only)
	expectEq(p and p.name, "frame", "the sprite itself")
	expectEq(p and p.image, "rbxassetid://1", "from the uploaded atlas")
	expectEq(p and p.rect[1], 4, "with its own rect")
	expectEq(p and p.scale, 1, "at 1x")
	expectEq(UiAssets.Placement("frame", 1, SPRITES, ids({})), nil, "nothing uploaded: no art")
end)

test("the copy draws where the art is magnified, the 1x art where it is shrunk", function()
	local both = ids({ atlas_old = "rbxassetid://1", atlas_new = "rbxassetid://2" })
	local p = UiAssets.Placement("frame", 1, SPRITES, both)
	expectEq(p and p.name, "frame__hi", "magnified: the copy")
	expectEq(p and p.image, "rbxassetid://2", "from its own atlas")
	expectEq(p and p.rect[3], 120, "its own rect")
	expectEq(p and p.entry.slice[1], 20, "its own pixel insets")
	expectEq(p and p.scale, 2, "its scale")
	expectEq(UiAssets.Placement("frame", nil, SPRITES, both).name, "frame__hi", "unknown size: the copy")
	expectEq(UiAssets.Placement("frame", 0.5, SPRITES, both).name, "frame", "shrunk: the 1x art")
	expectEq(UiAssets.Placement("frame", UiAssets.HI_FROM, SPRITES, both).name, "frame", "at the threshold: 1x")
	local onlyNew = ids({ atlas_new = "rbxassetid://2" })
	expectEq(UiAssets.Placement("frame", 0.5, SPRITES, onlyNew), nil, "shrunk without its 1x atlas: no art")
	expectEq(UiAssets.Placement("plain", 3, SPRITES, both).name, "plain", "no copy: the sprite")
end)

test("tiled copies draw only when every tile is uploaded", function()
	local base = ids({ atlas_map = "rbxassetid://9" })
	expectEq(UiAssets.Placement("map", 1.3, SPRITES, base).name, "map", "no tiles uploaded: the 1x map")
	local half = ids({ atlas_map = "rbxassetid://9", atlas_map_hi_1 = "rbxassetid://10" })
	expectEq(UiAssets.Placement("map", 1.3, SPRITES, half).name, "map", "one tile missing: the 1x map")
	local all = ids({ atlas_map = "rbxassetid://9", atlas_map_hi_1 = "a", atlas_map_hi_2 = "b" })
	local p = UiAssets.Placement("map", 1.3, SPRITES, all)
	expectEq(p and p.name, "map__hi", "all tiles: the copy")
	expectEq(p and p.image, nil, "tiles have no single image")
	expectNear(p and p.scale or 0, 2.04, 1e-9, "its scale")
end)

test("pixel size is the sharpest art's full size", function()
	local w, h = UiAssets.PixelSize("frame", SPRITES)
	expectEq(w, 200, "a 9-sliced copy's full width (its stored middle is short)")
	expectEq(h, 100, "and height")
	w, h = UiAssets.PixelSize("plain", SPRITES)
	expectEq(w, 40, "no copy: its own size")
	expectEq(UiAssets.PixelSize("missing", SPRITES), nil, "unknown")
end)
