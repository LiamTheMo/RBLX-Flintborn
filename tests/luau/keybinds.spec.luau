-- Keyboard controls (GDD §46): requested defaults, rebinding with swaps, and saves
-- that can never leave two actions on one key or bind a reserved key.

local Shared = game:GetService("ReplicatedStorage").Shared
local Keybinds = require(Shared.Settings.Keybinds)
local TutorialSteps = require(Shared.Tutorial.TutorialSteps)

test("the requested defaults: Shift sprint, Tab backpack, 1-6 hotbar, Q drop, F interact", function()
	local map = Keybinds.Resolve(nil)
	expectEq(map.Sprint, "LeftShift", "hold Shift to sprint")
	expect(Keybinds.Get("Sprint").hold, "sprint acts while held")
	expectEq(map.Backpack, "Tab", "Tab opens the backpack")
	expectEq(map.Drop, "Q", "Q drops")
	expectEq(map.Interact, "F", "F interacts and picks up")
	for _, lobby in { "Vault", "Forge", "Market", "Trade" } do
		expectEq(Keybinds.Get(lobby), nil, lobby .. " has no key: the lobby uses its navigation buttons")
	end
	local digits = { "One", "Two", "Three", "Four", "Five", "Six" }
	for index, key in digits do
		expectEq(map["Hotbar" .. index], key, "hotbar slot " .. index)
	end
	expectEq(Keybinds.Get("Hotbar7"), nil, "six hotbar slots (§56): no seventh key")
	expectEq(Keybinds.Resolve({ Hotbar7 = "G" }).Hotbar7, nil, "a saved bind for a removed slot is ignored")
end)

test("every default is allowed and no two actions share one", function()
	local used = {}
	for _, action in Keybinds.Actions do
		expect(Keybinds.IsAllowed(action.default), action.id .. " default is bindable")
		expect(used[action.default] == nil, action.default .. " used once")
		used[action.default] = true
	end
end)

test("movement, chat and menu keys can never be bound", function()
	for _, key in { "W", "A", "S", "D", "Space", "Slash", "Escape", "Return", "Backspace", "F9", "Nope" } do
		expect(not Keybinds.IsAllowed(key), key .. " is reserved")
		expectEq(Keybinds.Assign({}, "Drop", key), nil, key .. " is refused")
	end
	expectEq(Keybinds.Assign({}, "NoSuchAction", "Z"), nil, "unknown actions are refused")
end)

test("binding a key another action uses swaps the two", function()
	local overrides = Keybinds.Assign({}, "Drop", "F")
	local map = Keybinds.Resolve(overrides)
	expectEq(map.Drop, "F", "Drop moved to F")
	expectEq(map.Interact, "Q", "Interact took Drop's old key")
	overrides = Keybinds.Assign(overrides, "Backpack", "B")
	map = Keybinds.Resolve(overrides)
	expectEq(map.Backpack, "B", "a free key needs no swap")
	expectEq(map.Drop, "F", "earlier rebinds are kept")
	overrides = Keybinds.Assign(overrides, "Drop", "Q")
	map = Keybinds.Resolve(overrides)
	expectEq(map.Drop, "Q", "back to Q")
	expectEq(map.Interact, "F", "Interact swapped back to F")
	expectEq(overrides.Drop, nil, "a key equal to its default is not stored")
	expectEq(overrides.Interact, nil, "nor is Interact")
	expectEq(overrides.Backpack, "B", "only real changes are stored")
end)

test("a tampered or stale save never breaks the controls", function()
	local clean = Keybinds.Sanitize({ Drop = "W", Sprint = 5, Nope = "Z", Backpack = "B" })
	expectEq(clean.Backpack, "B", "valid overrides survive")
	expectEq(clean.Drop, nil, "a reserved key is dropped")
	expectEq(clean.Sprint, nil, "a non-string key is dropped")
	expectEq(clean.Nope, nil, "unknown actions are dropped")
	local conflict = Keybinds.Sanitize({ Drop = "F" })
	expectEq(next(conflict), nil, "an override clashing with a default falls back")
	expectEq(Keybinds.Resolve("garbage").Backpack, "Tab", "a non-table save resolves to the defaults")
	local map = Keybinds.Resolve({ Drop = "F" })
	expectEq(map.Drop, "Q", "the conflicting override is not applied")
	local both = Keybinds.Resolve({ Drop = "Z", Craft = "Z", Backpack = "B" })
	expectEq(both.Drop, "Q", "two overrides on one key both revert")
	expectEq(both.Craft, "V", "the other one too")
	expectEq(both.Backpack, "B", "unrelated rebinds survive a clash")
end)

test("saves from before Interact moved to F keep everything that still fits", function()
	-- An older save: Forge (now removed) on Z, Drop on F, Backpack on B, Crouch on E.
	local map = Keybinds.Resolve({ Forge = "Z", Drop = "F", Backpack = "B", Crouch = "E" })
	expectEq(map.Interact, "F", "Interact takes its new default")
	expectEq(map.Drop, "Q", "the rebind that now clashes with Interact reverts")
	expectEq(map.Backpack, "B", "other rebinds are kept")
	expectEq(map.Crouch, "E", "E is free now, so Crouch keeps it")
	local clean = Keybinds.Sanitize({ Forge = "Z", Vault = "G", Backpack = "B" })
	expectEq(clean.Forge, nil, "removed lobby actions are dropped")
	expectEq(clean.Vault, nil, "all of them")
	expectEq(clean.Backpack, "B", "real rebinds stay")
end)

test("hints name the bound key, and tutorial tokens are real actions", function()
	local map = Keybinds.Resolve(Keybinds.Assign({}, "Sprint", "LeftControl"))
	expectEq(Keybinds.Format("Hold {Sprint} to sprint", map), "Hold Ctrl to sprint", "rebound key shown")
	expectEq(Keybinds.Format("Press {Hotbar1}", Keybinds.Resolve(nil)), "Press 1", "digits read as numbers")
	expectEq(Keybinds.Format("Keep {Unknown}", map), "Keep {Unknown}", "unknown tokens are left alone")
	for _, step in TutorialSteps.Steps do
		for token in string.gmatch(step.hint, "{(%w+)}") do
			expect(Keybinds.Get(token) ~= nil, step.id .. " hint names a real action: " .. token)
		end
	end
end)
