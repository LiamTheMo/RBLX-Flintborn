-- Key caps (sheet 09; M03): "cap" the raised key (E, TAB, SHIFT, ESC; wide
-- art for words) and "flat" the small paper box the key-binds list uses.
-- Pressable when onPress is given (rebinding); "capturing" (waiting for a key)
-- draws the hover art with a pulsing label.
--
--   local key = Kit.KeyCap.new(row, { rect = { 210, 4, 0, 30 }, text = "E", variant = "flat", onPress = rebind })
--   key:SetCapturing(true)

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Interact = require(script.Parent.Interact)
local Input = require(script.Parent.Input)
local Motion = require(script.Parent.Motion)

local KeyCap = {}
KeyCap.__index = KeyCap

KeyCap.PAD = 14

-- A cap's width for `text` at `height`: at least square.
function KeyCap.Width(text: string, height: number?): number
	local h = height or 56
	local size = math.floor(h * 0.5)
	return math.max(h, math.ceil(Core.TextWidth(text, "keycap", size) + KeyCap.PAD * 2))
end

-- props: text, rect | size | height (a width of 0 fits the text), variant
-- ("cap" | "flat"), gamepadKey (KeyCode name shown on a gamepad), hideOnTouch,
-- onPress(cap), zIndex, name.
function KeyCap.new(parent: Instance, props)
	local variant = props.variant or "cap"
	local h = if props.rect
		then props.rect[4]
		elseif type(props.size) == "table" then props.size[2]
		else (props.height or 56)
	local given = if props.rect then props.rect[3] elseif type(props.size) == "table" then props.size[1] else 0
	local w = if given and given > 0 then given else KeyCap.Width(props.text or "", h)
	local role = if variant == "flat" then "keycap.flat" elseif w > h * 1.4 then "keycap.wide" else "keycap.cap"
	local place = table.clone(props)
	if props.rect then
		place.rect = { props.rect[1], props.rect[2], w, h }
	end
	local base = Core.Root(parent, "KeyCap", role, place, w, h)
	local self = setmetatable({ root = base.root, base = base, w = w, h = h }, KeyCap)
	self.plate = Art.Plate(base.visual, role, w, h, { z = base.z })
	-- A raised cap's face sits above its thicker bottom edge.
	local lift = if variant == "flat" then 0 else math.floor(h * 0.08)
	self.label = Core.Label(base.visual, {
		name = "Key",
		text = props.text or "",
		role = "keycap",
		size = if variant == "flat" then nil else math.floor(h * 0.42),
		align = "Center",
		scaled = true,
		rect = { 6, 0, w - 12, h - lift * 2 },
		z = base.z + 1,
	})
	-- Input-aware hints: gamepadKey (a KeyCode name such as "ButtonX") shows the
	-- button's name on a gamepad; hideOnTouch hides the cap on touch.
	if props.gamepadKey or props.hideOnTouch then
		self.keyboardText = props.text or ""
		self.gamepadKey = props.gamepadKey
		self.hideOnTouch = props.hideOnTouch
		base.maid:Give(Input.Watch(function()
			self:_hint()
		end))
		self:_hint()
	end
	if props.onPress then
		self.control = Interact.attach(base, {
			onPress = function()
				props.onPress(self)
			end,
			render = function(state)
				self:_render(state)
			end,
		})
	else
		base.root:SetAttribute("KitState", "normal")
	end
	return self
end

function KeyCap:_render(state: string)
	self.plate:Show(state)
	local capturing = state == "capturing"
	if capturing and self.stopPulse == nil then
		self.stopPulse = Motion.Pulse(self.label, "TextTransparency", 0.6, 0)
	elseif not capturing and self.stopPulse then
		self.stopPulse()
		self.stopPulse = nil
	end
	if state == "disabled" then
		self.label.TextTransparency = 0.45
	elseif not capturing then
		self.label.TextTransparency = 0
	end
end

function KeyCap:SetText(text: string)
	self.keyboardText = text
	self.label.Text = text
	if self.gamepadKey or self.hideOnTouch then
		self:_hint()
	end
end

function KeyCap:_hint()
	local kind = Input.Type()
	self.root.Visible = not (self.hideOnTouch and kind == "touch")
	local text = if kind == "gamepad" and self.gamepadKey
		then Input.GAMEPAD_NAMES[self.gamepadKey] or self.gamepadKey
		else self.keyboardText
	self.label.Text = text
	self.root:SetAttribute("KitInput", kind)
end

-- Waiting for a key: the cap shows "…" until SetText.
function KeyCap:SetCapturing(capturing: boolean)
	if self.control then
		if capturing then
			self.label.Text = "…"
		end
		self.control:Set("capturing", capturing)
	end
end

function KeyCap:SetEnabled(enabled: boolean)
	if self.control then
		self.control:SetEnabled(enabled)
	end
end

function KeyCap:Destroy()
	if self.stopPulse then
		self.stopPulse()
	end
	self.base.maid:Clean()
end

return KeyCap
