-- Pure display rules for the in-world HUD (GDD §11, §25.4): value formatting,
-- the compass projection, XP fraction, distances, timers, the HUD's screen scale
-- and the objective/event text. No Instances here, so the headless specs and the
-- HUD share one definition. The HUD only displays; the server owns every value.

local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local Keybinds = require(script.Parent.Parent.Settings.Keybinds)

local HudModel = {}

-- Roblox studs to metres for player-facing distances.
HudModel.METRES_PER_STUD = 0.28

-- Headings clockwise from north. -Z is north and +X is east on the island, the
-- same convention as MapController and EventFeedController.
HudModel.HEADINGS = { "N", "NE", "E", "SE", "S", "SW", "W", "NW" }

HudModel.OBJECTIVE_TITLE = "FIND EXTRACTION"
HudModel.EVENT_TITLE = "World Event"

-- One line per event category; names and rarities come from the server view.
HudModel.EVENT_BLURBS = {
	Vegetation = "Rare plants have sprouted",
	Ore = "A rich ore vein is exposed",
	Npc = "Hostile creatures are gathering",
	Cache = "A supply cache is up for grabs",
	Meteor = "A meteor has struck the crater",
	Structure = "Ancient ruins have surfaced",
	Boss = "A Guardian has awoken",
}

function HudModel.Clamp01(value: number?): number
	if type(value) ~= "number" or value ~= value then
		return 0
	end
	return math.clamp(value, 0, 1)
end

-- A 0–1 fraction as a whole number 0–100 (stamina and food replicate as fractions).
function HudModel.Percent(fraction: number?): number
	return math.round(HudModel.Clamp01(fraction) * 100)
end

-- Health fraction for the bar and the whole number shown beside it (rounded up,
-- so a living character never reads 0).
function HudModel.Health(health: number?, maxHealth: number?): (number, number)
	local current = math.max(0, if type(health) == "number" then health else 0)
	local maximum = if type(maxHealth) == "number" and maxHealth > 0 then maxHealth else 100
	return HudModel.Clamp01(current / maximum), math.ceil(math.min(current, maximum))
end

-- Fraction of the way to the next level; a max-level view (no xpToNext) is full.
function HudModel.XpFraction(xp: number?, xpToNext: number?): number
	if type(xpToNext) ~= "number" or xpToNext <= 0 then
		return 1
	end
	return HudModel.Clamp01((xp or 0) / xpToNext)
end

-- The badge text: "LV. 12", or "MAX" at the level cap (no xpToNext).
function HudModel.LevelText(level: number?, isMax: boolean?): string
	if isMax then
		return "MAX"
	end
	return ("LV. %d"):format(math.max(0, math.floor(level or 0)))
end

-- A whole number with thousands separators, as the lobby's currency bar shows it:
-- 2450 -> "2,450". Missing or negative values read 0.
function HudModel.Thousands(value: number?): string
	local text = tostring(math.max(0, math.floor(value or 0)))
	local formatted = text:reverse():gsub("(%d%d%d)", "%1,"):reverse()
	return (formatted:gsub("^,", ""))
end

-- The lobby party header: "PARTY 1/8" (alone counts as a party of one).
function HudModel.PartyTitle(members: number?, maxSize: number): string
	return ("PARTY  %d/%d"):format(math.clamp(math.floor(members or 1), 1, maxSize), maxSize)
end

-- Small text on a full XP bar at the level cap.
function HudModel.MaxLevelHint(level: number?): string
	return ("Level %d (max): rebirth in the lobby to keep climbing"):format(math.max(0, math.floor(level or 0)))
end

-- Seconds as m:ss, or h:mm:ss from an hour up. Negative time reads 0:00.
function HudModel.FormatTimer(seconds: number?): string
	local total = math.max(0, math.floor(seconds or 0))
	local hours = total // 3600
	local minutes = (total % 3600) // 60
	local secs = total % 60
	if hours > 0 then
		return ("%d:%02d:%02d"):format(hours, minutes, secs)
	end
	return ("%d:%02d"):format(minutes, secs)
end

function HudModel.StudsToMetres(studs: number): number
	return studs * HudModel.METRES_PER_STUD
end

-- "452 m" below a kilometre, then "1.2 km".
function HudModel.FormatDistance(studs: number?): string
	local metres = HudModel.StudsToMetres(math.max(0, studs or 0))
	if metres >= 1000 then
		return ("%.1f km"):format(metres / 1000)
	end
	return ("%d m"):format(math.floor(metres + 0.5))
end

-- Camera heading in degrees clockwise from north, from a look vector's X and Z.
function HudModel.Heading(lookX: number, lookZ: number): number
	return math.deg(math.atan2(lookX, -lookZ)) % 360
end

-- Bearing in degrees clockwise from north from one X/Z point to another.
function HudModel.Bearing(fromX: number, fromZ: number, toX: number, toZ: number): number
	return HudModel.Heading(toX - fromX, toZ - fromZ)
end

-- Signed shortest turn from `from` to `to`, in (-180, 180].
function HudModel.AngleDelta(from: number, to: number): number
	local delta = (to - from) % 360
	if delta > 180 then
		delta -= 360
	end
	return delta
end

function HudModel.HeadingLetter(degrees: number): string
	return HudModel.HEADINGS[math.floor(((degrees % 360) + 22.5) / 45) % 8 + 1]
end

-- Marks visible on the compass strip for a camera heading: one every `step`
-- degrees within `halfSpan` of the centre. Every 45° carries its letter; unlabelled
-- (minor) marks stop at `minorLimit` degrees from the centre when it is given.
-- Each mark is {angle, offset} where offset is degrees right of centre.
function HudModel.CompassMarks(heading: number, halfSpan: number, step: number, minorLimit: number?)
	local marks = {}
	for angle = 0, 359, step do
		local offset = HudModel.AngleDelta(heading, angle)
		local label = if angle % 45 == 0 then HudModel.HEADINGS[angle // 45 + 1] else nil
		local limit = if label == nil and minorLimit then math.min(minorLimit, halfSpan) else halfSpan
		if math.abs(offset) <= limit then
			table.insert(marks, { angle = angle, offset = offset, label = label, major = label ~= nil })
		end
	end
	table.sort(marks, function(a, b)
		return a.offset < b.offset
	end)
	return marks
end

-- Where a world bearing sits on the strip: degrees right of centre, or nil when it
-- is outside the visible span.
function HudModel.CompassOffset(heading: number, bearing: number, halfSpan: number): number?
	local offset = HudModel.AngleDelta(heading, bearing)
	if math.abs(offset) > halfSpan then
		return nil
	end
	return offset
end

-- The HUD's UIScale: the fit of the reference canvas in the screen times the
-- player's UI scale setting, kept between the layout's bounds (phones stay
-- readable) and never above the fit itself (or the minimum, where that is larger),
-- so a larger setting cannot push the hotbar into the vitals panel.
function HudModel.HudScale(
	screenWidth: number,
	screenHeight: number,
	refWidth: number,
	refHeight: number,
	minScale: number,
	maxScale: number,
	userScale: number?
): number
	if screenWidth <= 0 or screenHeight <= 0 then
		return 1
	end
	local fit = math.min(screenWidth / refWidth, screenHeight / refHeight)
	local scaled = math.clamp(fit * (userScale or 1), minScale, maxScale)
	return math.min(scaled, math.max(fit, minScale))
end

-- 9-slice corner scale for a sprite of natural size (w, h) drawn at (tw, th), so
-- rope corners shrink with small widgets instead of overlapping. The preview
-- (art/ui/preview_hud.py) uses the same formula.
function HudModel.SliceScale(width: number, height: number, targetWidth: number, targetHeight: number): number
	if width <= 0 or height <= 0 then
		return 1
	end
	return math.clamp(math.min(targetWidth / width, targetHeight / height), 0.15, 1)
end

-- Next hotbar slot for a step (the right bumper = +1), wrapping around. The mouse
-- wheel never steps the hotbar: it stays on camera zoom.
function HudModel.HotbarStep(current: number, step: number, count: number): number
	return ((current - 1 + step) % count) + 1
end

-- What each HUD hotbar slot shows for an inventory snapshot ({slots, equipped}):
-- index -> {name, count, rarity, equipped}, or nil for an empty slot. `count` is
-- "" for unique items and "×n" for stacks; Permanent items carry a star.
function HudModel.HotbarSlots(snapshot, count: number)
	local views = {}
	for _, slot in (snapshot and snapshot.slots) or {} do
		local index = slot.index
		if slot.area == "hotbar" and type(index) == "number" and index >= 1 and index <= count then
			local def = ItemCatalog.Get(slot.catalogId)
			views[index] = {
				name = (if slot.permanent then "★ " else "") .. (if def then def.name else tostring(slot.catalogId)),
				count = if slot.quantity and slot.quantity > 1 then ("×%d"):format(slot.quantity) else "",
				rarity = if def then def.rarity else "Common",
				equipped = snapshot.equipped == index,
			}
		end
	end
	return views
end

local KEY_NAMES = {
	One = "1",
	Two = "2",
	Three = "3",
	Four = "4",
	Five = "5",
	Six = "6",
	Seven = "7",
	Eight = "8",
	Nine = "9",
	Zero = "0",
	ButtonA = "A",
	ButtonB = "B",
	ButtonX = "X",
	ButtonY = "Y",
	ButtonL1 = "LB",
	ButtonR1 = "RB",
	ButtonL2 = "LT",
	ButtonR2 = "RT",
}

-- The keycap text for a prompt: the keyboard key, the gamepad button, or TAP.
-- A keyboard prompt without a key reads `fallbackKey` (the player's bound
-- Interact key), or else the default Interact key (Keybinds, GDD §46).
function HudModel.KeyLabel(inputType: string, keyName: string?, fallbackKey: string?): string
	if inputType == "Touch" then
		return "TAP"
	end
	if keyName == nil or keyName == "" or keyName == "Unknown" then
		if inputType == "Gamepad" then
			return "X"
		end
		keyName = fallbackKey or Keybinds.Get("Interact").default
	end
	return KEY_NAMES[keyName] or Keybinds.Display(keyName :: string)
end

-- Medicine lock, pending food healing, hunger slow and crouching: what only the
-- old survival HUD showed in words.
function HudModel.SurvivalStatus(
	medicineLockLeft: number?,
	foodHealing: number?,
	slowed: boolean?,
	crouching: boolean?
): string
	local parts = {}
	if (medicineLockLeft or 0) > 0 then
		table.insert(parts, ("Medicine ready in %.1f s"):format(medicineLockLeft))
	end
	if (foodHealing or 0) > 0 then
		table.insert(parts, ("Food healing +%d"):format(foodHealing))
	end
	if slowed then
		table.insert(parts, "! Hungry: slowed")
	end
	if crouching then
		table.insert(parts, "Crouching")
	end
	return table.concat(parts, "  ·  ")
end

-- The objective panel for extraction. `target` is the nearest extraction:
-- {name?, kind?, distance (studs)?, inZone, remaining (s)?, total (s)} where
-- `remaining` is set only while its countdown runs. Returns {title, lines} with
-- each line {text, distance?, progress, done}.
function HudModel.ExtractionObjective(target)
	if target == nil then
		return {
			title = HudModel.OBJECTIVE_TITLE,
			lines = { { text = "Search for an extraction site", progress = "0/1", done = false } },
		}
	end
	local total = target.total or 120
	local name = if target.name then "Reach " .. target.name else "Reach the extraction site"
	if target.kind == "Center" then
		name ..= " (2×)"
	end
	local reached = target.inZone == true
	local elapsed = if target.remaining then math.clamp(total - target.remaining, 0, total) else 0
	return {
		title = HudModel.OBJECTIVE_TITLE,
		lines = {
			{
				text = name,
				distance = if reached then nil else HudModel.FormatDistance(target.distance),
				progress = if reached then "1/1" else "0/1",
				done = reached,
			},
			{
				text = "Hold the zone for " .. HudModel.FormatTimer(total),
				progress = HudModel.FormatTimer(elapsed) .. "/" .. HudModel.FormatTimer(total),
				done = reached and target.remaining ~= nil and target.remaining <= 0,
			},
		},
	}
end

-- The world event panel for the most urgent announced event (soonest to end).
-- `views` are the server's event views; returns nil when none run.
function HudModel.WorldEvent(views, now: number, fromX: number?, fromZ: number?)
	local soonest = nil
	for _, view in views do
		if view.endsAt > now and (soonest == nil or view.endsAt < soonest.endsAt) then
			soonest = view
		end
	end
	if soonest == nil then
		return nil
	end
	local active = 0
	for _, view in views do
		if view.endsAt > now then
			active += 1
		end
	end
	local blurb = HudModel.EVENT_BLURBS[soonest.category] or "Something stirs in the crater"
	-- Rarity is always named in words, not shown by colour alone (§11).
	local description = ("%s · %s"):format(tostring(soonest.rarity or "Common"), blurb)
	if fromX and fromZ and soonest.position then
		local offsetX, offsetZ = soonest.position.X - fromX, soonest.position.Z - fromZ
		description = ("%s · %s, %s"):format(
			description,
			HudModel.HeadingLetter(HudModel.Bearing(fromX, fromZ, soonest.position.X, soonest.position.Z)),
			HudModel.FormatDistance(math.sqrt(offsetX * offsetX + offsetZ * offsetZ))
		)
	end
	if active > 1 then
		description ..= ("  (+%d more)"):format(active - 1)
	end
	return {
		id = soonest.id,
		title = HudModel.EVENT_TITLE,
		name = soonest.name,
		rarity = soonest.rarity,
		description = description,
		timer = HudModel.FormatTimer(soonest.endsAt - now),
	}
end

return HudModel
