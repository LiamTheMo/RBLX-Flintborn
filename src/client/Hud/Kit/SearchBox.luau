-- A search field (sheet 09; M02, M04): the paper box with its magnifier, a
-- TextBox with placeholder, and a clear ✕ while it holds text. onChanged(text)
-- runs after typing settles for `debounce` seconds.
--
--   Kit.SearchBox.new(column, { rect = { 0, 0, 215, 41 }, placeholder = "Search items...", onChanged = filter })

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Tokens = require(script.Parent.Tokens)

local SearchBox = {}
SearchBox.__index = SearchBox

-- props: rect | size, placeholder, text, debounce (0.15), onChanged(text),
-- zIndex, name.
function SearchBox.new(parent: Instance, props)
	local w, h = Core.Size(props, 215, 41)
	local base = Core.Root(parent, "SearchBox", "search.field", props, w, h)
	local self = setmetatable({ root = base.root, base = base, serial = 0 }, SearchBox)
	self.plate = Art.Plate(base.visual, "search.field", w, h, { z = base.z })
	-- The magnifier is baked into the art's left inset (44 px at full height).
	local left = math.floor(44 * math.min(1, h / 53)) + 4
	local clear = math.floor(h * 0.42)
	local box = Core.Make("TextBox", {
		Name = "Input",
		BackgroundTransparency = 1,
		ClearTextOnFocus = false,
		PlaceholderText = props.placeholder or "",
		Position = UDim2.fromOffset(left, 0),
		Size = UDim2.fromOffset(w - left - clear - 16, h),
		Text = props.text or "",
		TextTruncate = Enum.TextTruncate.AtEnd,
		TextXAlignment = Enum.TextXAlignment.Left,
		ZIndex = base.z + 2,
	}, base.visual)
	Core.Style(box, "rowLabel", "ink")
	box.PlaceholderColor3 = Tokens.Color("placeholder")
	self.box = box
	self.clear = Core.Make("TextButton", {
		Name = "Clear",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(w - clear - 12, (h - clear) / 2),
		Size = UDim2.fromOffset(clear, clear),
		Text = "",
		Visible = box.Text ~= "",
		ZIndex = base.z + 3,
	}, base.visual)
	Art.Plate(self.clear, "mark.cross", clear, clear, { z = base.z + 3 })
	local maid = base.maid
	maid:Give(self.clear.Activated:Connect(function()
		box.Text = ""
	end))
	maid:Give(box:GetPropertyChangedSignal("Text"):Connect(function()
		self.clear.Visible = box.Text ~= ""
		self.serial += 1
		local serial = self.serial
		task.delay(props.debounce or 0.15, function()
			if serial == self.serial and props.onChanged and self.root.Parent then
				props.onChanged(box.Text)
			end
		end)
	end))
	-- A text field takes focus, not presses: it keeps its own small state
	-- (normal, focused, disabled) with the same DebugState hook.
	self.flags = { enabled = true }
	maid:Give(box.Focused:Connect(function()
		self.flags.focused = true
		self:_render()
	end))
	maid:Give(box.FocusLost:Connect(function()
		self.flags.focused = false
		self:_render()
	end))
	maid:Give(base.root:GetAttributeChangedSignal("DebugState"):Connect(function()
		self:_render()
	end))
	self:_render()
	return self
end

function SearchBox:GetText(): string
	return self.box.Text
end

function SearchBox:SetText(text: string)
	self.box.Text = text
end

function SearchBox:_render()
	local state = KitModel.ResolveState(self.flags, self.root:GetAttribute("DebugState"))
	self.root:SetAttribute("KitState", state)
	-- The field has no focused art: the caret shows focus.
	self.plate:Show(if state == "focused" then "normal" else state)
	self.box.TextTransparency = if state == "disabled" then 0.4 else 0
end

function SearchBox:SetEnabled(enabled: boolean)
	self.flags.enabled = enabled
	self.box.TextEditable = enabled
	self.box.Interactable = enabled
	self:_render()
end

function SearchBox:Destroy()
	self.base.maid:Clean()
end

return SearchBox
