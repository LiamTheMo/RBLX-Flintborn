-- List rows (sheet 09 rows, sheet 12 objective rows; M06 recipe cards, M07
-- quest rows, M04 detail lines):
--   "row"    parchment row plate: icon, title, optional subtitle, value, chevron
--   "card"   the same, taller, with a bigger icon (recipes, quests)
--   "line"   no plate: label left, value right, a rule under (detail lines)
--   "option" a compact row for dropdown lists
-- Selected draws the gold-glow plate; locked draws the disabled plate with a
-- lock in place of the chevron and stays selectable (tooltips say why).
--
--   Kit.ListRow.new(list, { size = { 300, 72 }, variant = "card", icon = "pickaxe",
--       title = "Iron Pickaxe", subtitle = "Mine stone and ore.", chevron = true, onPress = pick })
--   Kit.ListRow.new(details, { size = { 280, 36 }, variant = "line", title = "Members", value = "1 / 8" })

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Divider = require(script.Parent.Divider)
local Interact = require(script.Parent.Interact)
local ItemIcon = require(script.Parent.ItemIcon)
local Text = require(script.Parent.Text)
local Tokens = require(script.Parent.Tokens)

local ListRow = {}
ListRow.__index = ListRow

-- props: rect | size, variant, icon (icon id), catalogId (item art instead),
-- title, subtitle, value, valueColor (token), chevron, onPress(row), zIndex, name.
function ListRow.new(parent: Instance, props)
	local variant = props.variant or "row"
	local plated = variant ~= "line"
	local w, h = Core.Size(props, 320, if variant == "card" then 72 elseif variant == "option" then 40 else 52)
	local role = if plated then "row.plate" else "row.line"
	local base = Core.Root(parent, "ListRow", role, props, w, h)
	local self = setmetatable({ root = base.root, base = base, variant = variant, w = w, h = h }, ListRow)
	if plated then
		self.plate = Art.Plate(base.visual, "row.plate", w, h, { z = base.z })
	else
		Divider.new(base.visual, { name = "Rule", rect = { 0, h - 8, w, 16 }, variant = "rule", zIndex = base.z })
	end
	local padX = if plated then 14 else 2
	local x = padX
	local iconSize = math.floor(h * (if variant == "card" then 0.8 elseif variant == "option" then 0.6 else 0.62))
	if props.catalogId then
		self.icon = ItemIcon.new(base.visual, {
			name = "Icon",
			rect = { x, (h - iconSize) / 2, iconSize, iconSize },
			catalogId = props.catalogId,
			icon = props.icon,
			zIndex = base.z + 1,
		}).root
		x += iconSize + 14
	elseif props.icon then
		self.icon = Art.Icon(base.visual, props.icon, { x, (h - iconSize) / 2, iconSize, iconSize }, {
			z = base.z + 1,
			name = "Icon",
		})
		x += iconSize + 14
	end
	local right = w - padX
	local markSize = math.floor(math.min(h * 0.4, 26))
	if props.chevron then
		self.chevron = Core.Make("Frame", {
			Name = "Chevron",
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(right - markSize * 0.7, (h - markSize) / 2),
			Size = UDim2.fromOffset(markSize * 0.7, markSize),
			ZIndex = base.z + 1,
		}, base.visual)
		Art.Plate(self.chevron, "mark.chevron", markSize * 0.7, markSize, { z = base.z + 1 })
		right -= markSize + 8
	end
	self.lock = Core.Make("Frame", {
		Name = "Lock",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(w - padX - markSize, (h - markSize) / 2),
		Size = UDim2.fromOffset(markSize, markSize),
		Visible = false,
		ZIndex = base.z + 2,
	}, base.visual)
	Art.Plate(self.lock, "mark.lock", markSize, markSize, { z = base.z + 2 })
	if props.value then
		-- The value keeps its full width; the title gives way.
		local vw = math.max(40, math.ceil(Text.Width(props.value, "value")) + 6)
		self.value = Core.Label(base.visual, {
			name = "Value",
			text = props.value,
			role = "value",
			color = props.valueColor,
			align = "Right",
			rect = { right - vw, 0, vw, h },
			z = base.z + 1,
		})
		self.valueWidth = vw
		right -= vw + 10
	end
	local hasSub = props.subtitle ~= nil
	local titleRole = if variant == "line" then "rowLabel" else "rowTitle"
	self.title = Core.Label(base.visual, {
		name = "Title",
		text = props.title or "",
		role = titleRole,
		rect = if hasSub then { x, h * 0.12, right - x, h * 0.46 } else { x, 0, right - x, h },
		z = base.z + 1,
	})
	if hasSub then
		self.subtitle = Core.Label(base.visual, {
			name = "Subtitle",
			text = props.subtitle,
			role = "small",
			color = "inkBody",
			rect = { x, h * 0.54, right - x, h * 0.36 },
			z = base.z + 1,
		})
	end
	if props.onPress or plated then
		self.control = Interact.attach(base, {
			pressScale = props.onPress ~= nil,
			selectable = props.onPress ~= nil,
			onPress = function()
				if props.onPress then
					props.onPress(self)
				end
			end,
			render = function(state)
				self:_render(state)
			end,
		})
		if props.onPress == nil then
			self.control.hit.Active = false
		end
	end
	return self
end

function ListRow:_render(state: string)
	if self.plate then
		self.plate:Show(state)
	end
	local locked = state == "locked"
	self.lock.Visible = locked
	if self.chevron then
		self.chevron.Visible = not locked
	end
	local dim = state == "disabled" or locked
	self.title.TextColor3 = Tokens.Color(if dim then "inkSoft" else "inkLabel")
	if self.icon and self.icon:IsA("ImageLabel") then
		(self.icon :: ImageLabel).ImageTransparency = if dim then 0.4 else 0
	end
end

function ListRow:SetTitle(text: string)
	Core.SetText(self.title, text)
end

function ListRow:SetSubtitle(text: string)
	if self.subtitle then
		Core.SetText(self.subtitle, text)
	end
end

function ListRow:SetValue(text: string, colorKey: string?)
	if self.value then
		self.value.Text = text
		self.value.TextColor3 = Tokens.Color(colorKey or "ink")
	end
end

function ListRow:SetSelected(selected: boolean)
	if self.control then
		self.control:SetSelected(selected)
	end
end

function ListRow:SetEnabled(enabled: boolean)
	if self.control then
		self.control:SetEnabled(enabled)
	end
end

-- "normal" | "locked" | "disabled".
function ListRow:SetState(state: string)
	if self.control then
		self.control:SetLocked(state == "locked")
		self.control:SetEnabled(state ~= "disabled")
	end
end

function ListRow:Destroy()
	self.base.maid:Clean()
end

return ListRow
