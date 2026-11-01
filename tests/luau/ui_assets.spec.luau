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
	-- Item art: a 2x copy, then a hero copy (the Forge picture) chained after it.
	tusk = { w = 80, h = 100, atlas = "atlas_items", rect = { 0, 0, 80, 100 }, hi = "tusk__hi" },
	tusk__hi = {
		w = 160,
		h = 200,
		scale = 2,
		of = "tusk",
		atlas = "atlas_journal_hi",
		rect = { 0, 0, 160, 200 },
		hi = "tusk__hi2",
	},
	tusk__hi2 = { w = 285, h = 356, scale = 3.56, of = "tusk", atlas = "atlas_items_hi", rect = { 0, 0, 285, 356 } },
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

test("copies chain least sharp first, each from its own magnification", function()
	local copies = UiAssets.Copies("tusk", SPRITES)
	expectEq(#copies, 2, "the 2x copy and the hero copy")
	expectEq(copies[1].name, "tusk__hi", "least sharp first")
	expectEq(copies[2].name, "tusk__hi2", "then the hero copy")
	expectEq(copies[1].from, UiAssets.HI_FROM, "a 2x copy draws from HI_FROM")
	expectNear(copies[2].from, 3.56 / UiAssets.HI_SHRINK, 1e-9, "a hero copy from its scale / HI_SHRINK")
	expectEq(#UiAssets.Copies("plain", SPRITES), 0, "no copy")
	expectEq(#UiAssets.Copies("missing", SPRITES), 0, "unknown")
	expectEq(UiAssets.HiFrom(2.04), UiAssets.HI_FROM, "the island map's copy keeps HI_FROM")
	expectEq(UiAssets.HiFrom(2.68), UiAssets.HERO_FROM, "a hero copy never draws at or below 1x")
end)

test("the sharpest uploaded copy whose magnification is reached draws", function()
	local all = ids({ atlas_items = "a", atlas_journal_hi = "b", atlas_items_hi = "c" })
	expectEq(UiAssets.Placement("tusk", 0.6, SPRITES, all).name, "tusk", "a slot: the 1x art")
	expectEq(UiAssets.Placement("tusk", 1.0, SPRITES, all).name, "tusk__hi", "below the hero copy's: the 2x copy")
	expectEq(UiAssets.Placement("tusk", 1.22, SPRITES, all).name, "tusk__hi", "the Journal illustration: the 2x copy")
	local hero = UiAssets.Placement("tusk", 2.54, SPRITES, all)
	expectEq(hero and hero.name, "tusk__hi2", "the Forge picture: the hero copy")
	expectEq(hero and hero.image, "c", "from its own atlas")
	expectNear(hero and hero.scale or 0, 3.56, 1e-9, "at its scale")
	expectEq(UiAssets.Placement("tusk", nil, SPRITES, all).name, "tusk__hi2", "unknown size: the sharpest")
	local noHero = ids({ atlas_items = "a", atlas_journal_hi = "b" })
	expectEq(UiAssets.Placement("tusk", 2.54, SPRITES, noHero).name, "tusk__hi", "hero atlas missing: the 2x copy")
	local onlyBase = ids({ atlas_items = "a" })
	expectEq(UiAssets.Placement("tusk", 2.54, SPRITES, onlyBase).name, "tusk", "no copy uploaded: the 1x art")
end)

test("hero copies draw in both hero boxes and never in a slot", function()
	-- slice_lobby_kit.py sizes an item's hero copy to 356 px on its long side
	-- (the 254 px Forge box at 1.4); item art is 72 to 196 px, about square.
	for _, size in { { 72, 73 }, { 85, 76 }, { 86, 116 }, { 116, 103 }, { 135, 124 }, { 156, 196 } } do
		local w, h = size[1], size[2]
		local from = UiAssets.HiFrom(356 / math.max(w, h))
		local forge = math.min(254 / w, 254 / h)
		local card = math.min(152 / w, 166 / h)
		expect(forge > from, ("%dx%d: the Forge picture draws the hero copy"):format(w, h))
		expect(card > from, ("%dx%d: the Inventory card draws the hero copy"):format(w, h))
		-- The biggest slot, the Inventory grid's 91 x 99, draws its item 67 px.
		expect(math.min(67 / w, 67 / h) <= from, ("%dx%d: a slot keeps the 1x art"):format(w, h))
	end
end)
