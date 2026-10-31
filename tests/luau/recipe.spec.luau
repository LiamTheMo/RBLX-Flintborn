-- The placeholder model recipe format (v0.19): validation, bounds and colour helpers.
local Shared = game:GetService("ReplicatedStorage").Shared
local Recipe = require(Shared.Visuals.Recipe)

local P = Recipe.Part

test("a well-formed recipe has no problems", function()
	local recipe = {
		parts = {
			P("Block", { 1, 2, 1 }, { 0, 1, 0 }, { 120, 80, 40 }, "Wood"),
			P("Ball", { 2, 2, 2 }, { 0, 3, 0 }, { 60, 140, 60 }, nil, { 0, 45, 0 }, { name = "Canopy" }),
		},
	}
	expectEq(#Recipe.Problems(recipe), 0, "no problems")
	expectEq(recipe.parts[2].name, "Canopy", "extra fields are kept")
end)

test("bad recipes are reported", function()
	expectEq(Recipe.Problems(nil)[1], "no parts", "nil")
	expectEq(Recipe.Problems({ parts = {} })[1], "no parts", "empty")
	local bad = {
		parts = {
			P("Sphere", { 1, 1, 1 }, { 0, 0, 0 }, { 1, 1, 1 }),
			P("Block", { 0, 1, 1 }, { 0, 0, 0 }, { 1, 1, 1 }),
			P("Block", { 1, 1, 1 }, { 0, 0 }, { 1, 1, 1 }),
			P("Block", { 1, 1, 1 }, { 0, 0, 0 }, { 300, 1, 1 }),
			P("Block", { 1, 1, 1 }, { 0, 0, 0 }, { 1, 1, 1 }, nil, { 0, 0 / 0, 0 }),
		},
	}
	expectEq(#Recipe.Problems(bad), 5, "one problem per bad part")
	local many = { parts = {} }
	for _ = 1, 5 do
		table.insert(many.parts, P("Block", { 1, 1, 1 }, { 0, 0, 0 }, { 1, 1, 1 }))
	end
	expectEq(#Recipe.Problems(many, 4), 1, "part cap")
	expectEq(#Recipe.Problems(many, 5), 0, "at the cap is fine")
end)

test("bounds cover every part", function()
	local recipe = {
		parts = {
			P("Block", { 2, 2, 2 }, { 0, 1, 0 }, { 1, 1, 1 }),
			P("Block", { 1, 1, 1 }, { 3, 4, -2 }, { 1, 1, 1 }),
		},
	}
	local low, high = Recipe.Bounds(recipe)
	expectEq(low[1], -1, "min x")
	expectEq(low[2], 0, "min y")
	expectEq(low[3], -2.5, "min z")
	expectEq(high[1], 3.5, "max x")
	expectEq(high[2], 4.5, "max y")
	expectEq(high[3], 1, "max z")
end)

test("colour helpers stay in range", function()
	local rgb = Recipe.Rgb(Color3.fromRGB(10, 128, 250))
	expectEq(rgb[1], 10, "r")
	expectEq(rgb[2], 128, "g")
	expectEq(rgb[3], 250, "b")
	local darker = Recipe.Shade({ 100, 200, 50 }, 0.5)
	expectEq(darker[1], 50, "darker r")
	expectEq(darker[2], 100, "darker g")
	local lighter = Recipe.Shade({ 100, 200, 250 }, 1.5)
	expect(lighter[1] > 100 and lighter[3] <= 255, "lighter stays within 0..255")
	expectEq(Recipe.Shade({ 255, 255, 255 }, 2)[1], 255, "clamped")
end)
