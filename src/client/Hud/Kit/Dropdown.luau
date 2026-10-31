-- A dropdown (sheet 09; M03 Language): the paper field with its ▼, the chosen
-- option, and a list of option rows on a paper panel that opens below (or
-- above with openUp). While open the dropdown rises over its neighbours (and
-- `layer`, the page holding it, rises too) and a press anywhere else closes it.
--
--   Kit.Dropdown.new(page, { rect = { 140, 500, 236, 43 }, options = { "All", "Tools", "Weapons" },
--       value = "All", onSelect = filter })

local GuiService = game:GetService("GuiService")

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Interact = require(script.Parent.Interact)
local ListRow = require(script.Parent.ListRow)

local Dropdown = {}
Dropdown.__index = Dropdown

Dropdown.ROW_H = 40

-- props: rect | size, options ({string}), value, onSelect(value), openUp,
-- layer (GuiObject raised while open), zIndex, name.
function Dropdown.new(parent: Instance, props)
	local w, h = Core.Size(props, 236, 43)
	local base = Core.Root(parent, "Dropdown", "dropdown.field", props, w, h)
	local options = props.options or {}
	local self = setmetatable({
		root = base.root,
		base = base,
		options = options,
		value = props.value or options[1],
		onSelect = props.onSelect,
		layer = props.layer,
		layerZ = props.layer and props.layer.ZIndex,
		baseZ = base.z,
		rows = {},
		open = false,
	}, Dropdown)
	self.plate = Art.Plate(base.visual, "dropdown.field", w, h, { z = base.z })
	self.label = Core.Label(base.visual, {
		name = "Value",
		text = self.value or "",
		role = "rowLabel",
		color = "ink",
		rect = { 18, 0, w - 18 - 48, h },
		z = base.z + 1,
	})
	-- A press outside the open list closes it.
	self.catcher = Core.Make("TextButton", {
		Name = "Outside",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(-4000, -4000),
		Selectable = false,
		Size = UDim2.new(1, 8000, 1, 8000),
		Text = "",
		Visible = false,
		ZIndex = base.z + 15,
	}, base.root)
	base.maid:Give(self.catcher.Activated:Connect(function()
		self:SetOpen(false)
	end))
	local rowH = Dropdown.ROW_H
	local listH = rowH * #options + 4 * (#options - 1) + 20
	self.list = Core.Make("Frame", {
		Name = "Options",
		BackgroundTransparency = 1,
		Position = if props.openUp then UDim2.fromOffset(0, -listH - 4) else UDim2.fromOffset(0, h + 4),
		Size = UDim2.fromOffset(w, listH),
		Visible = false,
		ZIndex = base.z + 16,
	}, base.root)
	Art.Plate(self.list, "dropdown.list", w, listH, { z = base.z + 16 })
	for index, option in options do
		local row = ListRow.new(self.list, {
			name = option,
			variant = "option",
			rect = { 10, 10 + (index - 1) * (rowH + 4), w - 20, rowH },
			title = option,
			zIndex = base.z + 17,
			onPress = function()
				self:SetOpen(false)
				if option ~= self.value then
					self:SetValue(option)
					if self.onSelect then
						self.onSelect(option)
					end
				end
			end,
		})
		self.rows[option] = row
	end
	self.control = Interact.attach(base, {
		pressScale = false,
		onPress = function()
			self:SetOpen(not self.open)
		end,
		render = function(state)
			self.plate:Show(state)
		end,
	})
	self:SetValue(self.value)
	return self
end

function Dropdown:SetOpen(open: boolean)
	local wasOpen = self.open
	self.open = open
	self.list.Visible = open
	self.catcher.Visible = open
	self.root.ZIndex = if open then self.baseZ + 20 else self.baseZ
	if self.layer and self.layerZ then
		self.layer.ZIndex = if open then self.layerZ + 30 else self.layerZ
	end
	self.control:Set("open", open)
	-- Gamepad: selection moves into the options (the chosen one) and comes
	-- back to the field when the list closes.
	local selected = GuiService.SelectedObject
	if open and not wasOpen and selected ~= nil then
		local row = self.rows[self.value] or select(2, next(self.rows))
		if row then
			GuiService.SelectedObject = row.control.hit
		end
	elseif not open and wasOpen and selected ~= nil and selected:IsDescendantOf(self.list) then
		GuiService.SelectedObject = self.control.hit
	end
end

function Dropdown:IsOpen(): boolean
	return self.open
end

-- Shows `value` as chosen without calling onSelect.
function Dropdown:SetValue(value: string?)
	self.value = value
	self.label.Text = value or ""
	for option, row in self.rows do
		row:SetSelected(option == value)
	end
end

function Dropdown:SetEnabled(enabled: boolean)
	if not enabled then
		self:SetOpen(false)
	end
	self.control:SetEnabled(enabled)
end

function Dropdown:Destroy()
	for _, row in self.rows do
		row:Destroy()
	end
	self.base.maid:Clean()
end

return Dropdown
