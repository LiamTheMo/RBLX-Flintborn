-- Pure display rules for the in-world HUD (GDD §11, §25.4): value formatting,
-- the compass projection, XP fraction, distances, timers, the HUD's screen scale
-- and the objective/event text. No Instances here, so the headless specs and the
-- HUD share one definition. The HUD only displays; the server owns every value.

local GameConstants = require(script.Parent.Parent.GameConstants)
local Keybinds = require(script.Parent.Parent.Settings.Keybinds)

local HudModel = {}

-- Roblox studs to metres for player-facing distances.
HudModel.METRES_PER_STUD = GameConstants.METRES_PER_STUD

-- Headings clockwise from north. -Z is north and +X is east on the island, the
-- same convention as MapController and EventFeedController.
HudModel.HEADINGS = { "N", "NE", "E", "SE", "S", "SW", "W", "NW" }

HudModel.OBJECTIVE_TITLE = "FIND EXTRACTION"
HudModel.EVENT_TITLE = "World Event"

-- One line per event category; names and rarities come from the server view.
-- The card writes "<rarity> · <blurb>", so no blurb names a rarity ("Rare ·
-- Rare plants…" read twice, and an Epic event's "Rare plants" contradicted it).
HudModel.EVENT_BLURBS = {
	Vegetation = "Prized plants have sprouted",
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

-- A currency amount that fits a pill: separators below 100,000 (2,450), then
-- one decimal with K, M or B (250K, 1.2M, 3.4B); the decimal drops when it is 0.
function HudModel.Compact(value: number?): string
	local n = math.max(0, math.floor(value or 0))
	if n < 100000 then
		return HudModel.Thousands(n)
	end
	for _, unit in { { 1e9, "B" }, { 1e6, "M" }, { 1e3, "K" } } do
		if n >= unit[1] then
			-- Rounded down, so 999,999 never reads 1000K.
			local tenths = math.floor(n / unit[1] * 10) / 10
			local text = if tenths >= 100 or tenths % 1 == 0 then ("%d"):format(tenths) else ("%.1f"):format(tenths)
			return text .. unit[2]
		end
	end
	return HudModel.Thousands(n)
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

-- 9-slice corner scale for a sprite of natural (design) size (w, h) drawn at
-- (tw, th), so rope corners shrink with small widgets instead of overlapping.
-- `artScale` is the drawn image's pixels per design pixel (a high-resolution
-- copy at 2x has corner insets twice as many pixels): the result scales those
-- pixel insets, so the corners keep their design size.
function HudModel.SliceScale(
	width: number,
	height: number,
	targetWidth: number,
	targetHeight: number,
	artScale: number?
): number
	local k = if artScale and artScale > 0 then artScale else 1
	if width <= 0 or height <= 0 then
		return 1 / k
	end
	return math.clamp(math.min(targetWidth / width, targetHeight / height), 0.15, 1) / k
end

-- The device safe area (ARCHITECTURE D29): how far notches, the Dynamic
-- Island and rounded corners reach in from each edge of the screen, in screen
-- px ({left, top, right, bottom}; Kit.Scale.SafeInsets measures it). Roblox's
-- own touch controls sit inside it; the HUDs draw on the whole screen
-- (ScreenInsets None) and keep to it themselves (HudModel.EdgeGap).
HudModel.NO_INSETS = table.freeze({ left = 0, top = 0, right = 0, bottom = 0 })

local function safe(insets)
	return insets or HudModel.NO_INSETS
end

-- The HUD layout grid (ARCHITECTURE D30; HudLayout.json "grid", read by both
-- HUDs through Hud/Layout): `margin` (M) design px between the screen's edge
-- and every region pinned to it, `gap` (G) between stacked or neighbouring
-- regions, `column` the width of the right-hand column's pieces, and the
-- corner bands, the top `topBand` and the bottom `bottomBand` of the screen's
-- height, where a phone held sideways has no notch or island. The helpers
-- below take the grid as their first argument, so the specs and both HUDs
-- share one copy of the numbers.

-- True when a region spanning y top..bottom (screen px) on a screen `height`
-- px tall lies wholly in the top or the bottom corner band.
function HudModel.InCornerBand(grid, top: number, bottom: number, height: number): boolean
	return bottom <= height * grid.topBand + 0.5 or top >= height * (1 - grid.bottomBand) - 0.5
end

-- The edge rule (D29, applied per column by D30): the gap (design px, at HUD
-- scale k) between a column spanning y top..bottom (screen px, every piece of
-- it) and its side edge, whose device safe inset is `safeInset` screen px:
-- the margin when the whole column lies in a corner band, else the margin or
-- the safe inset, whichever is larger, for the whole column, so its pieces
-- keep one edge.
function HudModel.EdgeGap(grid, top: number, bottom: number, height: number, safeInset: number?, k: number): number
	if HudModel.InCornerBand(grid, top, bottom, height) then
		return grid.margin
	end
	return math.max(grid.margin, (safeInset or 0) / math.max(k, 0.01))
end

-- Stacks a column's pieces from `top` (design px) with `gap` between them:
-- `heights[i]` is piece i's height, or false for a hidden piece (it takes no
-- room). Returns each shown piece's top (nil for a hidden one) and the
-- column's foot (`top` when nothing shows).
function HudModel.Stack(top: number, heights: { number | false }, gap: number): ({ number? }, number)
	local tops, y, foot = {}, top, top
	for index, height in heights do
		if height then
			tops[index] = y
			foot = y + height
			y = foot + gap
		end
	end
	return tops, foot
end

-- Roblox's classic touch thumbstick (the ring the "Thumbstick" movement mode
-- draws) on a screen w × h (screen px), as the default PlayerModule
-- (ClassicThumbstick) places it inside the safe area (`insets`, screen px),
-- the mirror of the jump button: 70 px square, 25 px from the left and 90 from the bottom when the
-- short side is 500 px or less; otherwise 120 px square, 60 from the left and
-- 210 from the bottom. Returns {x, y, size}, its top-left corner and side.
function HudModel.Thumbstick(width: number, height: number, insets: any?)
	local i = safe(insets)
	local small = math.min(width, height) <= 500
	local size = if small then 70 else 120
	return {
		x = i.left + (if small then size / 2 - 10 else size / 2),
		y = height - i.bottom - (if small then size + 20 else size * 1.75),
		size = size,
	}
end

-- Where the HUDs' bottom-left corner button (the ⚙: `gear`, HudLayout's
-- {size = {w, h}, ringGap, pad}) sits, as its distance from the HUD root's
-- left and bottom edges in design px. `screen`: {width, height (screen px),
-- scale (the HUD's UIScale), touch, insets}. The corner (D30): the grid's
-- margin from the screen's left and bottom edges, in both HUDs, on every
-- screen where its touch pad (`pad` screen px) keeps `ringGap` px from
-- Roblox's thumbstick ring (desktops, notched phones, whose ring stands 25 px
-- inside the 47 px inset, tablets and large touch screens, whose ring stands
-- high). Where the ring reaches the corner (a phone without a side inset) it
-- stands above the ring instead, its foot `ringGap` px over it, at the edge
-- rule's gap from the left. Returns left, bottom and where it went ("corner"
-- or "above").
function HudModel.GearCorner(grid, gear, screen): (number, number, string)
	local margin = grid.margin
	local width, height = screen.width or 0, screen.height or 0
	if not screen.touch or width <= 0 or height <= 0 then
		return margin, margin, "corner"
	end
	local k = math.max(screen.scale or 1, 0.01)
	local insets = safe(screen.insets)
	local stick = HudModel.Thumbstick(width, height, insets)
	local w, h = gear.size[1] * k, gear.size[2] * k
	local pad = gear.pad or 44
	local padW, padH = math.max(pad, w), math.max(pad, h)
	local cx, cy = margin * k + w / 2, height - margin * k - h / 2
	local gap = gear.ringGap or 12
	local clear = cx + padW / 2 + gap <= stick.x + 0.01
		or cy + padH / 2 + gap <= stick.y + 0.01
		or cx - padW / 2 >= stick.x + stick.size + gap - 0.01
		or cy - padH / 2 >= stick.y + stick.size + gap - 0.01
	if clear then
		return margin, margin, "corner"
	end
	local bottom = math.max(margin, math.ceil((height - stick.y + gap) / k))
	local foot = height - bottom * k
	return HudModel.EdgeGap(grid, foot - h, foot, height, insets.left, k), bottom, "above"
end

-- Roblox's top-bar buttons (the Roblox logo, then the menu and chat pill) are
-- 44 px tall and end 2 px above the bar's inset. TOP_ROW_MIN keeps a row 12 px
-- from the screen's top edge when the bar is shorter or hidden.
HudModel.TOP_BUTTON = 44
HudModel.TOP_BUTTON_FOOT = 2
HudModel.TOP_ROW_MIN = 12

-- The top bar's button row for a bar reaching `inset` screen px down: its top
-- and its centre line, in screen px (inset 58: 12 and 34).
function HudModel.TopRow(inset: number): (number, number)
	local top = math.max(HudModel.TOP_ROW_MIN, inset - HudModel.TOP_BUTTON - HudModel.TOP_BUTTON_FOOT)
	return top, top + HudModel.TOP_BUTTON / 2
end

-- The centre x of an item `itemW` wide in the top bar's row of a screen
-- `width` wide: the screen's centre, moved just enough to keep `gap` from
-- Roblox's left-hand buttons (reaching x `left`) and from what starts at x
-- `right` (the right-hand column or the bar's right end). nil when it fits in
-- neither (it then goes below the bar). All in one unit (design px).
function HudModel.RowCentre(width: number, itemW: number, left: number, right: number, gap: number): number?
	local lo = left + gap + itemW / 2
	local hi = right - gap - itemW / 2
	if lo > hi then
		return nil
	end
	return math.clamp(width / 2, lo, hi)
end

-- Next hotbar slot for a step (the right bumper = +1), wrapping around. The mouse
-- wheel never steps the hotbar: it stays on camera zoom.
function HudModel.HotbarStep(current: number, step: number, count: number): number
	return ((current - 1 + step) % count) + 1
end

-- The hotbar's items from an inventory snapshot ({slots, equipped}):
-- index -> {itemId, quantity, permanent}, or nil for an empty slot.
function HudModel.HotbarItems(snapshot, count: number)
	local items = {}
	for _, slot in (snapshot and snapshot.slots) or {} do
		local index = slot.index
		if slot.area == "hotbar" and type(index) == "number" and index >= 1 and index <= count then
			items[index] = {
				itemId = slot.catalogId,
				quantity = slot.quantity,
				permanent = slot.permanent == true,
			}
		end
	end
	return items
end

-- Gamepad buttons; keyboard keys read as Keybinds shows them ("One" → "1").
local KEY_NAMES = {
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

-- The status plaques for the survival state: medicine lock (hourglass), pending
-- food healing (heart) and the hunger slow (warning), each in words.
function HudModel.StatusChips(medicineLockLeft: number?, foodHealing: number?, slowed: boolean?)
	local chips = {}
	if (medicineLockLeft or 0) > 0 then
		table.insert(chips, { icon = "hourglass", text = ("Medicine ready in %.1f s"):format(medicineLockLeft) })
	end
	if (foodHealing or 0) > 0 then
		table.insert(chips, { icon = "heart", text = ("Food healing +%d"):format(foodHealing) })
	end
	if slowed then
		table.insert(chips, { icon = "warning", text = "Hungry: slowed" })
	end
	return chips
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
