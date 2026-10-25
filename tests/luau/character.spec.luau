local Shared = game:GetService("ReplicatedStorage").Shared
local CharacterLook = require(Shared.Character.CharacterLook)

test("players outside a tribe wear the default Earth shorts", function()
	expectEq(CharacterLook.PantsFor(nil), "Earth", "no tribe")
	expectEq(CharacterLook.PantsFor(""), "Earth", "empty id")
	expectEq(CharacterLook.COLORS[1].name, CharacterLook.DEFAULT, "Earth is listed first")
end)

test("a tribe always gets the same non-default colour", function()
	local names = {}
	for _, color in CharacterLook.COLORS do
		names[color.name] = true
	end
	local seen = {}
	for index = 1, 200 do
		local id = "tribe-" .. index
		local name = CharacterLook.PantsFor(id)
		expect(name ~= "Earth", "tribes never wear the default")
		expect(names[name] == true, "a listed colour")
		expectEq(CharacterLook.PantsFor(id), name, "stable for the same id")
		seen[name] = true
	end
	local count = 0
	for _ in seen do
		count += 1
	end
	expectEq(count, #CharacterLook.COLORS - 1, "tribes spread over every other colour")
end)
