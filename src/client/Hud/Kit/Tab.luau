-- Tabs (sheets 03, 10, 14; M02, M03, M07):
--   "category"   a row with an icon; selected draws the paper arrow plate (M02)
--   "arrow"      paper arrow tab, leather when selected (sheet 14)
--   "horizontal" Backpack / Vault: parchment plate, leather when selected (M02)
--   "large"      Settings' tall tabs, same art, bigger text (M03)
--   "side"       square icon tab beside a window, gold glow when selected (M07)
-- Text and icon turn cream on leather. Kit.TabGroup keeps one selected.
--
--   local tabs = {
--       Kit.Tab.new(bar, { id = "backpack", rect = { 0, 0, 170, 58 }, label = "Backpack", icon = "backpack_white", variant = "horizontal" }),
--       Kit.Tab.new(bar, { id = "vault", rect = { 180, 0, 165, 58 }, label = "Vault", icon = "chest", variant = "horizontal" }),
--   }
--   local group = Kit.TabGroup.new(tabs, function(id) show(id) end)
--   group:Select("backpack")

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Interact = require(script.Parent.Interact)
local Tokens = require(script.Parent.Tokens)

local Tab = {}
Tab.__index = Tab

local ROLE = {
	category = "tab.category",
	arrow = "tab.arrow",
	horizontal = "tab.horizontal",
	large = "tab.horizontal",
	side = "tab.side",
}

-- Sprites drawn as leather (cream text and icon on them).
local LEATHER_SELECTED = { arrow = true, horizontal = true, large = true }

-- props: id, rect | size, label, icon, variant, onPress, zIndex, name, and:
--   selectedIcon  icon shown while selected ("white:gamepad", "backpack_white")
--   iconTint / selectedIconTint  colour tokens laid over the icon
--   iconSize, iconX, labelX  (design px; defaults per variant), textSize
function Tab.new(parent: Instance, props)
	local variant = props.variant or "horizontal"
	local role = ROLE[variant] or ROLE.horizontal
	local w, h = Core.Size(props, 200, 58)
	local base = Core.Root(parent, "Tab", role, props, w, h)
	local self = setmetatable({
		root = base.root,
		base = base,
		id = props.id or props.label,
		variant = variant,
		w = w,
		h = h,
		onPress = props.onPress,
	}, Tab)
	-- The category tab's arrow reaches past its row (M02: body to 475, tip at 486).
	self.plate = Art.Plate(base.visual, role, w, h, { z = base.z })
	local textRole = if variant == "large" then "tabLarge" else "tab"
	-- The arrow tab's leather strap takes its left edge.
	local x = if variant == "side" then 0 elseif variant == "arrow" then 30 else 14
	self.iconTint = props.iconTint
	self.selectedIconTint = props.selectedIconTint
	if props.icon then
		local s = props.iconSize
			or (if variant == "side" then math.floor(math.min(w, h) * 0.62) else math.floor(h * 0.62))
		local ix = props.iconX or (if variant == "side" then (w - s) / 2 else (if variant == "large" then 22 else 12))
		local rect = { ix, (h - s) / 2, s, s }
		self.icon = Art.Icon(base.visual, props.icon, rect, { z = base.z + 2, name = "Icon", tint = props.iconTint })
		if props.selectedIcon then
			self.selectedIcon = Art.Icon(base.visual, props.selectedIcon, rect, {
				z = base.z + 2,
				name = "SelectedIcon",
				tint = props.selectedIconTint,
			})
			self.selectedIcon.Visible = false
		end
		x = ix + s + (if variant == "large" then 22 else 12)
	end
	x = props.labelX or x
	if props.label and variant ~= "side" then
		self.label = Core.Label(base.visual, {
			name = "Label",
			text = props.label,
			role = textRole,
			size = props.textSize,
			scaled = true,
			rect = { x, 0, w - x - (if variant == "category" or variant == "arrow" then 34 else 12), h - 2 },
			z = base.z + 2,
		})
	end
	self.control = Interact.attach(base, {
		onPress = function()
			if self.group then
				self.group:Select(self.id, true)
			elseif self.onPress then
				self.onPress(self.id)
			end
		end,
		render = function(state)
			self:_render(state)
		end,
	})
	return self
end

function Tab:_render(state: string)
	-- A category row has no plate until selected; under the pointer it shows
	-- the selected plate faintly.
	local faint = self.variant == "category" and (state == "hover" or state == "focused" or state == "pressed")
	self.plate.alpha = if faint then 0.55 else 0
	self.plate:Show(if faint then "selected" else state)
	local onLeather = state == "selected" and LEATHER_SELECTED[self.variant]
	local color = if onLeather then "cream" elseif state == "disabled" then "inkSoft" else "inkLabel"
	if self.label then
		self.label.TextColor3 = Tokens.Color(color)
	end
	if self.selectedIcon then
		self.selectedIcon.Visible = state == "selected"
		self.icon.Visible = state ~= "selected"
	end
	if self.icon then
		if self.icon:IsA("ImageLabel") then
			local tint = if state == "selected" and self.selectedIconTint then self.selectedIconTint else self.iconTint
			if tint and not self.selectedIcon then
				(self.icon :: ImageLabel).ImageColor3 = Tokens.Color(tint)
			end
			-- Art icons draw as given (a leather tab passes a white icon such as
			-- "backpack_white"); a glyph stand-in turns cream on leather.
			(self.icon :: ImageLabel).ImageTransparency = if state == "disabled" then 0.45 else 0
		elseif self.icon:IsA("TextLabel") then
			(self.icon :: TextLabel).TextColor3 = Tokens.Color(if onLeather then "cream" else "ink")
		end
	end
end

function Tab:SetSelected(selected: boolean)
	self.control:SetSelected(selected)
end

function Tab:SetEnabled(enabled: boolean)
	self.control:SetEnabled(enabled)
end

function Tab:SetLabel(text: string)
	if self.label then
		Core.SetText(self.label, text)
	end
end

function Tab:Destroy()
	self.base.maid:Clean()
end

local TabGroup = {}
TabGroup.__index = TabGroup
Tab.Group = TabGroup

-- Keeps one of `tabs` selected; onSelect(id) runs when the player picks another.
function TabGroup.new(tabs: { any }, onSelect: ((string) -> ())?)
	local self = setmetatable({ tabs = tabs, onSelect = onSelect, selected = nil }, TabGroup)
	for _, tab in tabs do
		tab.group = self
	end
	return self
end

-- Selects tab `id`. `fromPress` runs onSelect (a press); scripted selection
-- does not, unless the id changed and `notify` is true.
function TabGroup:Select(id: string, fromPress: boolean?)
	local changed = id ~= self.selected
	self.selected = id
	for _, tab in self.tabs do
		tab:SetSelected(tab.id == id)
	end
	if fromPress and changed and self.onSelect then
		self.onSelect(id)
	end
end

function TabGroup:Selected(): string?
	return self.selected
end

function TabGroup:Destroy()
	for _, tab in self.tabs do
		tab:Destroy()
	end
end

return Tab
