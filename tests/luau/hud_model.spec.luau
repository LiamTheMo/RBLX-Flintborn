local Shared = game:GetService("ReplicatedStorage").Shared
local HudModel = require(Shared.UI.HudModel)

test("fractions display as whole numbers 0–100", function()
	expectEq(HudModel.Percent(1), 100, "full")
	expectEq(HudModel.Percent(0.724), 72, "rounds down below .5")
	expectEq(HudModel.Percent(0.726), 73, "rounds up from .5")
	expectEq(HudModel.Percent(1.4), 100, "clamped above")
	expectEq(HudModel.Percent(-0.2), 0, "clamped below")
	expectEq(HudModel.Percent(nil), 0, "missing reads 0")
	expectEq(HudModel.Percent(0 / 0), 0, "NaN reads 0")
end)

test("health shows its fraction and a rounded-up number", function()
	local fraction, shown = HudModel.Health(72.2, 100)
	expectNear(fraction, 0.722, 1e-9, "fraction")
	expectEq(shown, 73, "a living character never shows less than it has")
	fraction, shown = HudModel.Health(150, 120)
	expectEq(fraction, 1, "clamped")
	expectEq(shown, 120, "never above max")
	fraction, shown = HudModel.Health(-5, 100)
	expectEq(fraction, 0, "dead is empty")
	expectEq(shown, 0, "dead reads 0")
	fraction = HudModel.Health(50, 0)
	expectEq(fraction, 0.5, "a missing max falls back to 100")
end)

test("XP fraction and level text", function()
	expectEq(HudModel.XpFraction(1250, 2000), 0.625, "partway")
	expectEq(HudModel.XpFraction(2500, 2000), 1, "clamped")
	expectEq(HudModel.XpFraction(10, nil), 1, "max level is full")
	expectEq(HudModel.XpFraction(10, 0), 1, "zero requirement is full")
	expectEq(HudModel.LevelText(12), "LV. 12", "badge text")
	expectEq(HudModel.LevelText(nil), "LV. 0", "missing level")
	expectEq(HudModel.LevelText(50, true), "MAX", "level cap")
	expect(string.find(HudModel.MaxLevelHint(50), "rebirth", 1, true) ~= nil, "max hint names rebirth")
end)

test("lobby currency and party header text", function()
	expectEq(HudModel.Thousands(2450), "2,450", "thousands")
	expectEq(HudModel.Thousands(125), "125", "under a thousand")
	expectEq(HudModel.Thousands(1000000), "1,000,000", "millions")
	expectEq(HudModel.Thousands(999), "999", "no leading comma")
	expectEq(HudModel.Thousands(nil), "0", "missing reads 0")
	expectEq(HudModel.Thousands(-5), "0", "negative reads 0")
	expectEq(HudModel.PartyCount(nil, 8), "1/8", "alone is a party of one")
	expectEq(HudModel.PartyCount(3, 8), "3/8", "members")
	expectEq(HudModel.PartyCount(12, 8), "8/8", "clamped to the cap")
end)

test("timers read m:ss and h:mm:ss", function()
	expectEq(HudModel.FormatTimer(372), "6:12", "minutes and seconds")
	expectEq(HudModel.FormatTimer(120), "2:00", "two minutes")
	expectEq(HudModel.FormatTimer(5.9), "0:05", "fractions round down")
	expectEq(HudModel.FormatTimer(-3), "0:00", "never negative")
	expectEq(HudModel.FormatTimer(3725), "1:02:05", "hours")
end)

test("distances convert studs to metres", function()
	expectNear(HudModel.StudsToMetres(100), 28, 1e-9, "0.28 m per stud")
	expectEq(HudModel.FormatDistance(1614), "452 m", "452 m")
	expectEq(HudModel.FormatDistance(0), "0 m", "zero")
	expectEq(HudModel.FormatDistance(5000), "1.4 km", "kilometres from 1,000 m")
	expectEq(HudModel.FormatDistance(nil), "0 m", "missing")
end)

test("heading and bearing use -Z as north, clockwise", function()
	expectNear(HudModel.Heading(0, -1), 0, 1e-9, "north")
	expectNear(HudModel.Heading(1, 0), 90, 1e-9, "east")
	expectNear(HudModel.Heading(0, 1), 180, 1e-9, "south")
	expectNear(HudModel.Heading(-1, 0), 270, 1e-9, "west")
	expectNear(HudModel.Bearing(10, 10, 20, 0), 45, 1e-9, "north-east")
	expectEq(HudModel.HeadingLetter(44), "NE", "44 rounds to NE")
	expectEq(HudModel.HeadingLetter(338), "N", "338 rounds to N")
	expectEq(HudModel.HeadingLetter(-90), "W", "negative wraps")
end)

test("angle deltas take the short way round", function()
	expectEq(HudModel.AngleDelta(350, 10), 20, "across north clockwise")
	expectEq(HudModel.AngleDelta(10, 350), -20, "across north anticlockwise")
	expectEq(HudModel.AngleDelta(0, 180), 180, "opposite is +180")
	expectEq(HudModel.AngleDelta(90, 90), 0, "same")
end)

test("compass marks project letters around the heading", function()
	local marks = HudModel.CompassMarks(0, 117, 15)
	local byLabel = {}
	for index, mark in marks do
		if mark.label then
			byLabel[mark.label] = mark.offset
		end
		if index > 1 then
			expect(marks[index - 1].offset < mark.offset, "sorted left to right")
		end
	end
	expectEq(byLabel.N, 0, "N centred when facing north")
	expectEq(byLabel.NE, 45, "NE right of centre")
	expectEq(byLabel.NW, -45, "NW left of centre")
	expectEq(byLabel.E, 90, "E at +90")
	expectEq(byLabel.W, -90, "W at -90")
	expectEq(byLabel.S, nil, "S is behind and hidden")
	expectEq(#marks, 15, "one mark every 15 degrees across the span")

	local limited = HudModel.CompassMarks(0, 108, 15, 90)
	for _, mark in limited do
		expect(mark.major or math.abs(mark.offset) <= 90, "no minor marks beyond 90 degrees")
	end
	expectEq(#limited, 13, "minor marks at ±105 are dropped")

	local turned = HudModel.CompassMarks(100, 60, 45)
	expectEq(#turned, 3, "facing 100: NE, E, SE")
	expectEq(turned[2].label, "E", "E nearest the centre")
	expectEq(turned[2].offset, -10, "E is 10 degrees left")
end)

test("compass offsets for waypoints hide what is out of view", function()
	expectEq(HudModel.CompassOffset(0, 30, 117), 30, "ahead-right")
	expectEq(HudModel.CompassOffset(350, 20, 117), 30, "across north")
	expectEq(HudModel.CompassOffset(0, 180, 117), nil, "behind")
end)

test("HUD scale fits the reference canvas within bounds", function()
	expectNear(HudModel.HudScale(1672, 941, 1672, 941, 0.5, 1.6), 1, 1e-9, "reference size")
	expectNear(HudModel.HudScale(1920, 1080, 1672, 941, 0.5, 1.6), 1080 / 941, 1e-9, "1080p fits height")
	expectEq(HudModel.HudScale(844, 390, 1672, 941, 0.5, 1.6), 0.5, "phones are clamped to the minimum")
	expectEq(HudModel.HudScale(844, 390, 1672, 941, 0.5, 1.6, 1.25), 0.5, "a phone at 1.25 stays at the minimum")
	expectNear(HudModel.HudScale(1672, 941, 1672, 941, 0.5, 1.6, 0.8), 0.8, 1e-9, "a smaller setting shrinks")
	expectNear(HudModel.HudScale(1672, 941, 1672, 941, 0.5, 1.6, 1.25), 1, 1e-9, "a larger setting is capped")
	expectNear(HudModel.HudScale(3344, 1882, 1672, 941, 0.5, 1.6, 1.25), 1.6, 1e-9, "and by the maximum")
	expectEq(HudModel.HudScale(0, 0, 1672, 941, 0.5, 1.6), 1, "no screen yet")

	-- The 844×390 phone at 1.25: the hotbar's left edge (reference x 372, centred
	-- at 836 − 28) stays right of the vitals panel's right edge (reference x 331).
	local phoneScale = HudModel.HudScale(844, 390, 1672, 941, 0.5, 1.6, 1.25)
	local vitalsRight = 331 * phoneScale
	local hotbarLeft = 844 / 2 + (372 - 836) * phoneScale
	expect(hotbarLeft > vitalsRight, "hotbar clears the vitals panel on a phone")
end)

test("slice scale shrinks corners for small widgets", function()
	expectEq(HudModel.SliceScale(400, 100, 800, 200), 1, "never enlarges")
	expectNear(HudModel.SliceScale(400, 100, 272, 68), 0.68, 1e-9, "follows the tighter axis")
	expectEq(HudModel.SliceScale(400, 100, 800, 5), 0.15, "has a floor")
end)

test("hotbar stepping wraps", function()
	expectEq(HudModel.HotbarStep(1, 1, 9), 2, "next")
	expectEq(HudModel.HotbarStep(9, 1, 9), 1, "wraps forward")
	expectEq(HudModel.HotbarStep(1, -1, 9), 9, "wraps back")
end)

test("hotbar slots show their items, stacks and the equipped one", function()
	local views = HudModel.HotbarSlots({
		equipped = 2,
		slots = {
			{ area = "hotbar", index = 1, catalogId = "FlintArrow", quantity = 24 },
			{ area = "hotbar", index = 2, catalogId = "IronSword", permanent = true },
			{ area = "hotbar", index = 3, catalogId = "Redberry", quantity = 1 },
			{ area = "backpack", index = 4, catalogId = "Wood", quantity = 50 },
			{ area = "hotbar", index = 12, catalogId = "Wood", quantity = 5 },
		},
	}, 9)
	expectEq(views[1].name, "Flint Arrow", "item name")
	expectEq(views[1].count, "×24", "stack count")
	expectEq(views[1].equipped, false, "not equipped")
	expectEq(views[2].name, "★ Iron Sword", "Permanent items carry a star")
	expectEq(views[2].count, "", "unique items show no count")
	expectEq(views[2].equipped, true, "the equipped slot")
	expectEq(views[3].count, "", "a single item shows no count")
	expectEq(views[4], nil, "backpack items stay off the hotbar")
	expectEq(views[5], nil, "an empty slot is nil")
	expectEq(views[12], nil, "out-of-range slots are ignored")
	expectEq(next(HudModel.HotbarSlots(nil, 9)), nil, "no snapshot, empty hotbar")
end)

test("prompt keycaps name the key for the input in use", function()
	expectEq(HudModel.KeyLabel("Keyboard", "E"), "E", "keyboard key")
	expectEq(HudModel.KeyLabel("Keyboard", "One"), "1", "number keys read as digits")
	expectEq(HudModel.KeyLabel("Gamepad", "ButtonX"), "X", "gamepad button")
	expectEq(HudModel.KeyLabel("Touch", "E"), "TAP", "touch")
	expectEq(HudModel.KeyLabel("Keyboard", "LeftShift"), "Shift", "rebindable keys read as in Settings")
	expectEq(HudModel.KeyLabel("Keyboard", "Unknown"), "F", "unknown falls back to the default Interact key")
	expectEq(HudModel.KeyLabel("Keyboard", nil, "G"), "G", "or to the player's bound Interact key")
end)

test("survival status keeps the medicine lock and food healing", function()
	expectEq(HudModel.SurvivalStatus(0, 0, false), "", "nothing to show")
	expectEq(HudModel.SurvivalStatus(3.24, 0, false), "Medicine ready in 3.2 s", "lock")
	expectEq(
		HudModel.SurvivalStatus(1, 5, true),
		"Medicine ready in 1.0 s  ·  Food healing +5  ·  ! Hungry: slowed",
		"all three"
	)
	expectEq(HudModel.SurvivalStatus(0, 0, false, true), "Crouching", "crouching")
end)

test("the extraction objective tracks reaching and holding the zone", function()
	local idle = HudModel.ExtractionObjective({ name = "Salt Cliffs", distance = 1614, inZone = false, total = 120 })
	expectEq(idle.title, "FIND EXTRACTION", "title")
	expectEq(idle.lines[1].text, "Reach Salt Cliffs", "named site")
	expectEq(idle.lines[1].distance, "452 m", "distance in metres")
	expectEq(idle.lines[1].progress, "0/1", "not reached")
	expectEq(idle.lines[2].text, "Hold the zone for 2:00", "hold line")
	expectEq(idle.lines[2].progress, "0:00/2:00", "no countdown yet")

	local holding = HudModel.ExtractionObjective({
		name = "Crater Heart",
		kind = "Center",
		distance = 3,
		inZone = true,
		remaining = 78,
		total = 120,
	})
	expectEq(holding.lines[1].text, "Reach Crater Heart (2×)", "centre bonus named")
	expect(holding.lines[1].done, "reached")
	expectEq(holding.lines[1].distance, nil, "no distance once inside")
	expectEq(holding.lines[2].progress, "0:42/2:00", "countdown progress")
	expect(not holding.lines[2].done, "still holding")

	local none = HudModel.ExtractionObjective(nil)
	expectEq(#none.lines, 1, "a single search line without a known site")
end)

test("the world event panel shows the soonest event", function()
	local views = {
		{
			id = "a",
			name = "Iron Vein",
			rarity = "Rare",
			category = "Ore",
			endsAt = 500,
			position = Vector3.new(0, 0, -100),
		},
		{
			id = "b",
			name = "Meteor",
			rarity = "Epic",
			category = "Meteor",
			endsAt = 472,
			position = Vector3.new(0, 0, 0),
		},
		{ id = "c", name = "Old", rarity = "Common", category = "Cache", endsAt = 50, position = Vector3.new() },
	}
	local panel = HudModel.WorldEvent(views, 100, 0, 0)
	expectEq(panel.id, "b", "soonest running event")
	expectEq(panel.timer, "6:12", "time left")
	expectEq(panel.title, "World Event", "title")
	expect(string.find(panel.description, "Epic", 1, true) ~= nil, "rarity named in words")
	expect(string.find(panel.description, "(+1 more)", 1, true) ~= nil, "other running events counted")
	expectEq(HudModel.WorldEvent({}, 100), nil, "hidden with no events")
	expectEq(HudModel.WorldEvent({ views[3] }, 100), nil, "ended events are ignored")
end)
