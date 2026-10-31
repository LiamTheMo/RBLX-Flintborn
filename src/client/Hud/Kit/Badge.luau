-- Small tags and badges (sheets 01, 05, 13; M04):
--   "leader"   the Leader plaque (value pill, gold tint)
--   "ready"    green dot on the light green pill (a status that is set: trade
--              locked, data saved; default text "Ready")
--   "notReady" grey dot on the value pill (the status not yet set)
--   "count"    stack count plaque, "number" the leather hotbar number badge
--   "new"      wide count plaque with "NEW", "dot" a red notification dot.
-- Pill widths follow their text. `anchor = "topRight"` pins the badge over
-- its parent's top-right corner (icon buttons, tiles).
--
--   Kit.Badge.new(row, { rect = { 250, 12, 0, 30 }, variant = "ready" })
--   Kit.Badge.new(slot, { variant = "number", text = "3", rect = { -4, -4, 26, 26 } })

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Text = require(script.Parent.Text)
local Tokens = require(script.Parent.Tokens)

local Badge = {}
Badge.__index = Badge

-- Per variant: the plate role, a status dot role, the default text, the text
-- role and colour, a tint over the plate, and the default size.
Badge.VARIANTS = {
	leader = { role = "badge.pill", text = "Leader", textRole = "tag", tint = "leaderTint", h = 34 },
	ready = { role = "badge.ready", dot = "dot.green", text = "Ready", textRole = "tag", h = 34 },
	notReady = { role = "badge.pill", dot = "dot.grey", text = "Not Ready", textRole = "tag", h = 34 },
	count = { role = "badge.count", text = "", textRole = "count", w = 34, h = 31 },
	number = { role = "badge.number", text = "", textRole = "badgeNum", w = 26, h = 26 },
	new = { role = "badge.countWide", text = "NEW", textRole = "tag", h = 30 },
	dot = { role = "dot.red", text = nil, w = 18, h = 18 },
	-- Status / marker dots, drawn untinted from their art.
	dotRed = { role = "dot.red", text = nil, w = 18, h = 18 },
	dotYellow = { role = "dot.yellow", text = nil, w = 18, h = 18 },
	dotGreen = { role = "dot.green", text = nil, w = 18, h = 18 },
	dotGrey = { role = "dot.grey", text = nil, w = 18, h = 18 },
	-- A rarity accent: `rarity` names the colour (rarity<Name> token).
	rarity = { role = "dot.rarity", text = nil, w = 12, h = 12 },
}

-- props: variant (also "dotRed" | "dotYellow" | "dotGreen" | "dotGrey" |
-- "rarity"), text, rect | size (a rect width of 0 fits the text), width (a
-- fixed width for pills), textSize, rarity ("Common" … for the rarity dot),
-- anchor ("topRight"), zIndex, name.
function Badge.new(parent: Instance, props)
	local variant = props.variant or "count"
	local spec = Badge.VARIANTS[variant] or Badge.VARIANTS.count
	local text = props.text or spec.text
	local h = if props.rect then props.rect[4] elseif type(props.size) == "table" then props.size[2] else spec.h
	local dotSize = math.floor(h * 0.5)
	local w = if props.rect and props.rect[3] > 0
		then props.rect[3]
		elseif type(props.size) == "table" and props.size[1] > 0 then props.size[1]
		else nil
	if w == nil and props.width then
		w = props.width
	end
	if w == nil then
		if spec.w then
			w = spec.w
		else
			local textW = Text.Width(text or "", spec.textRole)
			w = math.ceil(textW + 28 + (if spec.dot then dotSize + 8 else 0))
		end
	end
	local place = table.clone(props)
	place.rect = if props.rect then { props.rect[1], props.rect[2], w, h } else nil
	place.size = { w, h }
	if props.anchor == "topRight" and props.rect == nil then
		place.position = UDim2.new(1, -w * 0.55, 0, -h * 0.45)
	end
	local base = Core.Root(parent, "Badge", spec.role, place, w, h)
	base.root:SetAttribute("KitVariant", variant)
	local self = setmetatable({ root = base.root, base = base, variant = variant, spec = spec }, Badge)
	self.plate = Art.Plate(base.visual, spec.role, w, h, {
		z = base.z,
		tint = if spec.tint then Tokens.Color(spec.tint) else nil,
	})
	if variant == "rarity" then
		self:SetRarity(props.rarity)
	end
	local left = 0
	if spec.dot then
		local dotHolder = Core.Make("Frame", {
			Name = "Dot",
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(12, (h - dotSize) / 2),
			Size = UDim2.fromOffset(dotSize, dotSize),
			ZIndex = base.z + 1,
		}, base.visual)
		Art.Plate(dotHolder, spec.dot, dotSize, dotSize, { z = base.z + 1 })
		left = 12 + dotSize + 2
	end
	if text then
		self.label = Core.Label(base.visual, {
			name = "Label",
			text = text,
			role = spec.textRole,
			size = props.textSize,
			align = "Center",
			scaled = true,
			rect = { left + 4, 0, w - left - 8, h - 2 },
			z = base.z + 2,
		})
	end
	return self
end

function Badge:SetText(text: string)
	if self.label then
		Core.SetText(self.label, text)
	end
end

-- The rarity dot's colour (rarity<Name> token; unknown names read Common).
function Badge:SetRarity(rarity: string?)
	local key = "rarity" .. tostring(rarity or "Common")
	if Tokens.Data.colors[key] == nil then
		key = "rarityCommon"
	end
	for _, part in self.plate.holder:GetDescendants() do
		if part:IsA("Frame") and part.Name == "native" then
			part.BackgroundColor3 = Tokens.Color(key)
		end
	end
	self.root:SetAttribute("KitRarity", rarity)
end

function Badge:SetVisible(visible: boolean)
	self.root.Visible = visible
end

function Badge:Destroy()
	self.base.maid:Clean()
end

return Badge
