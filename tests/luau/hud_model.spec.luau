local Shared = game:GetService("ReplicatedStorage").Shared
local HudLayout = require(Shared.UI.HudLayout)
local HudModel = require(Shared.UI.HudModel)

-- The grid tests below run on the shipped layout (D30: margin 24, gap 12, column 315).
local GRID = HudLayout.grid

test("fractions display as whole numbers 0–100", function()
	-- Rounds to nearest, clamps both ways; missing and NaN read 0.
	for input, shown in { [1] = 100, [0.724] = 72, [0.726] = 73, [1.4] = 100, [-0.2] = 0 } do
		expectEq(HudModel.Percent(input), shown, "Percent " .. input)
	end
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
	expectEq(HudModel.SliceScale(400, 100, 800, 200, 2), 0.5, "a 2x image's pixel corners draw at half")
	expectNear(HudModel.SliceScale(400, 100, 272, 68, 2), 0.34, 1e-9, "the shrink applies on top")
	expectEq(HudModel.SliceScale(400, 100, 800, 200, nil), 1, "no art scale: as before")
end)

test("Roblox's touch controls sit inside the device safe area", function()
	local phone = HudModel.Thumbstick(844, 390)
	expectEq(phone.size, 70, "a phone's thumbstick ring is 70 px")
	expectEq(phone.x, 25, "25 px from the left")
	expectEq(phone.y, 300, "90 px from the bottom, level with the jump button")
	local tablet = HudModel.Thumbstick(1024, 768)
	expectEq(tablet.size, 120, "a tablet's is 120 px")
	expectEq(tablet.x, 60, "60 px from the left")
	expectEq(tablet.y, 558, "210 px from the bottom")

	-- A notched phone held sideways: 47 px side insets.
	local notched = { left = 47, top = 0, right = 47, bottom = 0 }
	expectEq(HudModel.Thumbstick(844, 390, notched).x, 72, "the ring 25 px inside the left inset")
end)

test("the HUD layout pins regions to grid columns (D30)", function()
	local layout = HudLayout
	-- Every edge-pinned region names its column instead of carrying offsets.
	for _, key in { "vitals", "status", "objective", "event" } do
		expectEq(layout[key].column, "right", key .. " is in the right-hand column")
		expect(layout[key].pos == nil and layout[key].anchor == nil, key .. " carries no offsets of its own")
	end
	expectEq(layout.tiles.column, "left", "the menu tiles are in the left-hand column")
	expectEq(layout.event.phone.column, "left", "on phones the world event joins the left-hand column")
	expectEq(layout.bottom.column, "bottom", "the level/XP bar and hotbar sit the margin above the bottom")
	-- The XP bar is centred over the hotbar (both in the 572 px bottom group).
	local b = layout.bottom
	local hotbarRight = b.hotbar.x[#b.hotbar.x] + b.hotbar.slot[1]
	expect(math.abs((b.xp[1] + b.xp[3] / 2) - hotbarRight / 2) <= 0.5, "the XP bar is centred over the hotbar")
	expect(math.abs((b.popups[1] - b.xp[1])) < 1e-6 and b.popups[3] == b.xp[3], "the XP pop-ups over the bar")
end)

test("the edge rule per column: the margin in the corner bands, else the safe inset for the whole column", function()
	-- 844 × 390: the top band ends at y 117, the bottom band starts at 292.5.
	expect(HudModel.InCornerBand(GRID, 12, 95, 390), "the vitals' rows fit the top band")
	expect(not HudModel.InCornerBand(GRID, 12, 165, 390), "a column down to y 165 reaches the middle band")
	expect(HudModel.InCornerBand(GRID, 355, 378, 390), "the corner ⚙ is in the bottom band")
	expect(not HudModel.InCornerBand(GRID, 250, 273, 390), "one above the thumbstick is not")
	expectEq(HudModel.EdgeGap(GRID, 12, 95, 390, 47, 0.5), 24, "corner band: the margin, inset or not")
	expectEq(HudModel.EdgeGap(GRID, 12, 205, 390, 47, 0.5), 94, "middle band: the 47 px inset (94 design px at 0.5)")
	expectEq(HudModel.EdgeGap(GRID, 12, 205, 390, 0, 0.5), 24, "middle band without an inset: the margin")
	expectEq(HudModel.EdgeGap(GRID, 12, 205, 390, 5, 0.5), 24, "never closer than the margin")
end)

test("a column stacks its shown pieces with the gap", function()
	local tops, foot = HudModel.Stack(24, { 166, false, 134, 128 }, 12)
	expectEq(tops[1], 24, "the first piece at the top")
	expectEq(tops[2], nil, "a hidden piece takes no room")
	expectEq(tops[3], 202, "the next shown piece the gap under the first")
	expectEq(tops[4], 348, "and the next")
	expectEq(foot, 476, "the column's foot")
	tops, foot = HudModel.Stack(24, { 166, 38, 134 }, 12)
	expectEq(tops[2], 202, "status shown: the gap under the vitals")
	expectEq(tops[3], 252, "the objective the gap under the status")
	tops, foot = HudModel.Stack(40, { false }, 12)
	expectEq(foot, 40, "nothing shown: the foot is the top")
end)

test(
	"the corner settings button: the grid's corner, or above the thumbstick ring when it reaches the corner",
	function()
		local gear = HudLayout.gear
		local left, bottom, where =
			HudModel.GearCorner(GRID, gear, { width = 1672, height = 941, scale = 1, touch = false })
		expectEq(left, 24, "desktop: the margin from the left")
		expectEq(bottom, 24, "desktop: and from the bottom")
		expectEq(where, "corner", "desktop: the corner")

		-- A notched phone: the ring stands 25 px inside the 47 px inset (x 72),
		-- so the ⚙ takes the very corner, 12 px from the left and the bottom.
		local notched = { left = 47, top = 0, right = 47, bottom = 0 }
		local screen = { width = 844, height = 390, scale = 0.5, touch = true, insets = notched }
		left, bottom, where = HudModel.GearCorner(GRID, gear, screen)
		expectEq(where, "corner", "notched phone: the corner")
		expectEq(left, 24, "notched phone: 12 px from the left")
		expectEq(bottom, 24, "notched phone: 12 px from the bottom")
		local padRight = 24 * 0.5 + 26 / 2 + 44 / 2
		expect(padRight + 12 <= 72 + 1e-6, "its touch pad 12 px or more clear of the ring")

		-- No inset (a 667 × 375 phone): the ring starts 25 px in, so above it.
		left, bottom, where = HudModel.GearCorner(GRID, gear, { width = 667, height = 375, scale = 0.5, touch = true })
		expectEq(where, "above", "the ring reaches the corner: above it")
		expectEq(bottom, 204, "its foot (90 + 12) / 0.5 up")
		expectEq(left, 24, "at the margin (no inset)")
		-- A tablet and a large touch screen: their ring stands high, the corner is free.
		left, bottom, where =
			HudModel.GearCorner(GRID, gear, { width = 1024, height = 768, scale = 0.55, touch = true })
		expectEq(where, "corner", "a tablet: the corner")
		left, bottom, where =
			HudModel.GearCorner(GRID, gear, { width = 2000, height = 924, scale = 0.98, touch = true })
		expectEq(where, "corner", "a 2000 × 924 touch screen: the corner")
	end
)

test("the top bar's row and an item centred in it", function()
	local top, centre = HudModel.TopRow(58)
	expectEq(top, 12, "Roblox's 44 px buttons start 12 px down a 58 px bar")
	expectEq(centre, 34, "their centre line")
	top = HudModel.TopRow(0)
	expectEq(top, 12, "no bar: 12 px from the top")
	top = HudModel.TopRow(72)
	expectEq(top, 26, "a taller bar moves the row down")

	expectEq(HudModel.RowCentre(1672, 481, 180, 1379, 16), 836, "room on both sides: the screen's centre")
	expectEq(HudModel.RowCentre(1334, 481, 446, 1041, 16), 702.5, "moved right off Roblox's buttons")
	expectEq(HudModel.RowCentre(1334, 481, 560, 1041, 16), nil, "no room: nil (below the bar)")
end)

test("hotbar stepping wraps", function()
	expectEq(HudModel.HotbarStep(1, 1, 6), 2, "next")
	expectEq(HudModel.HotbarStep(6, 1, 6), 1, "wraps forward")
	expectEq(HudModel.HotbarStep(1, -1, 6), 6, "wraps back")
end)

test("hotbar slots show their items, stacks and the Permanent ones", function()
	local items = HudModel.HotbarItems({
		equipped = 2,
		slots = {
			{ area = "hotbar", index = 1, catalogId = "FlintArrow", quantity = 24 },
			{ area = "hotbar", index = 2, catalogId = "IronSword", permanent = true },
			{ area = "hotbar", index = 3, catalogId = "Redberry", quantity = 1 },
			{ area = "backpack", index = 4, catalogId = "Wood", quantity = 50 },
			{ area = "hotbar", index = 7, catalogId = "Wood", quantity = 5 },
		},
	}, 6)
	expectEq(items[1].itemId, "FlintArrow", "item id")
	expectEq(items[1].quantity, 24, "stack count")
	expectEq(items[1].permanent, false, "not Permanent")
	expectEq(items[2].itemId, "IronSword", "the second slot")
	expectEq(items[2].permanent, true, "Permanent items are marked for the star art")
	expectEq(items[2].quantity, nil, "unique items carry no count")
	expectEq(items[3].quantity, 1, "a single item")
	expectEq(items[4], nil, "backpack items stay off the hotbar")
	expectEq(items[5], nil, "an empty slot is nil")
	expectEq(items[7], nil, "slots past the sixth are ignored")
	expectEq(next(HudModel.HotbarItems(nil, 6)), nil, "no snapshot, empty hotbar")
end)

test("prompt keycaps name the key for the input in use", function()
	expectEq(HudModel.KeyLabel("Keyboard", "E"), "E", "keyboard key")
	expectEq(HudModel.KeyLabel("Keyboard", "One"), "1", "number keys read as digits")
	expectEq(HudModel.KeyLabel("Gamepad", "ButtonX"), "X", "gamepad button")
	expectEq(HudModel.KeyLabel("Touch", "E"), "TAP", "touch")
	expectEq(HudModel.KeyLabel("Keyboard", "LeftShift"), "Shift", "rebindable keys read as in Settings")
	expectEq(HudModel.KeyLabel("Keyboard", "Unknown"), "E", "unknown falls back to the default Interact key")
	expectEq(HudModel.KeyLabel("Keyboard", nil, "G"), "G", "or to the player's bound Interact key")
end)

test("survival status keeps the medicine lock and food healing", function()
	expectEq(#HudModel.StatusChips(0, 0, false), 0, "nothing to show")
	local lock = HudModel.StatusChips(3.24, 0, false)
	expectEq(#lock, 1, "one plaque")
	expectEq(lock[1].icon, "hourglass", "the lock's icon")
	expectEq(lock[1].text, "Medicine ready in 3.2 s", "lock")
	local all = HudModel.StatusChips(1, 5, true)
	expectEq(#all, 3, "all three")
	expectEq(all[1].text, "Medicine ready in 1.0 s", "lock first")
	expectEq(all[2].icon, "heart", "then food healing")
	expectEq(all[2].text, "Food healing +5", "its amount")
	expectEq(all[3].icon, "warning", "then the hunger slow")
	expectEq(all[3].text, "Hungry: slowed", "in words")
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
	-- The card reads "<rarity> · <blurb>": no blurb names a rarity again.
	local Rarity = require(Shared.Items.Rarity)
	for category, blurb in HudModel.EVENT_BLURBS do
		for _, rarity in Rarity.Order do
			expect(
				not string.find(" " .. string.lower(blurb) .. " ", " " .. string.lower(rarity) .. " ", 1, true),
				category .. "'s blurb does not repeat a rarity (" .. rarity .. ")"
			)
		end
	end
end)

test("currency text has separators, and compacts past 100,000", function()
	for input, text in { [125] = "125", [999] = "999", [2450] = "2,450", [1000000] = "1,000,000", [-5] = "0" } do
		expectEq(HudModel.Thousands(input), text, "Thousands " .. input)
	end
	expectEq(HudModel.Thousands(nil), "0", "missing reads 0")
	-- Three-digit thousands drop the decimal and never round up to 1000K.
	for input, text in { [2450] = "2,450", [99999] = "99,999", [100000] = "100K", [250500] = "250K", [999999] = "999K" } do
		expectEq(HudModel.Compact(input), text, "Compact " .. input)
	end
	for input, text in { [1234567] = "1.2M", [2000000] = "2M", [3400000000] = "3.4B" } do
		expectEq(HudModel.Compact(input), text, "Compact " .. input)
	end
	expectEq(HudModel.Compact(nil), "0", "missing reads 0")
end)
