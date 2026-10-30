-- The state machine every interactive kit component shares (ARCHITECTURE §2.3).
--
-- A transparent "Hit" button over the component (padded towards 44 px for
-- fingers) takes the input. Actions run on Activated, so mouse, touch and
-- gamepad A all work; hover shows only for a mouse; a press lasts from
-- InputBegan to its InputEnded and is cancelled when the pointer leaves or the
-- input ends elsewhere; gamepad selection draws the hover state (the selection
-- image itself is an empty frame). Disabled sets Interactable = false and drops
-- out of gamepad selection; locked stays selectable so a tooltip can say why.
--
-- The `DebugState` attribute on the component root forces any state (scenes and
-- verifiers); "" or nil returns to live input. The drawn state is written to the
-- `KitState` attribute.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local Theme = require(script.Parent.Parent.Parent.Ui.Theme)
local Core = require(script.Parent.Core)
local Motion = require(script.Parent.Motion)
local Sound = require(script.Parent.Sound)
local Tokens = require(script.Parent.Tokens)

local Interact = {}

-- Controllers with a press in progress, so an input released outside the
-- button (where the button sees no InputEnded) still ends the press. One
-- shared connection serves them all.
local pressing: { [any]: boolean } = {}
local endWatch: RBXScriptConnection? = nil

local function watchEnds()
	if endWatch then
		return
	end
	endWatch = UserInputService.InputEnded:Connect(function(input: InputObject)
		for controller in table.clone(pressing) do
			if controller.pressInput == input or input.UserInputType == Enum.UserInputType.MouseButton1 then
				controller:_endPress()
			end
		end
	end)
end

-- True while the player is pointing with a mouse (touch has no hover).
function Interact.UsingMouse(): boolean
	local ok, mouse = pcall(Theme.UsingMouse)
	return not ok or mouse == true
end

local PRESS_TYPES = {
	[Enum.UserInputType.MouseButton1] = true,
	[Enum.UserInputType.Touch] = true,
}

local Controller = {}
Controller.__index = Controller

export type Options = {
	onPress: ((any) -> ())?,
	onLocked: ((any) -> ())?,
	render: ((string, any) -> ())?,
	pad: number?,
	hoverScale: boolean?,
	pressScale: boolean?,
	selectable: boolean?,
	sound: string?,
	debounce: number?,
	hit: GuiButton?,
	z: number?,
}

-- Attaches the state machine to a component base (Core.Root). Returns the
-- controller: :SetEnabled, :SetSelected, :SetBusy, :SetLocked, :Set(flag, v),
-- :State(), :Refresh(); `hit` is its button.
function Interact.attach(base, opts: Options)
	local root = base.root
	local self = setmetatable({
		base = base,
		root = root,
		opts = opts,
		flags = { enabled = true },
		state = "",
		lastPress = -math.huge,
		pressInput = nil,
	}, Controller)
	local w, h = base.w, base.h
	local touchMin = Tokens.Space("touchMin", 44)
	local pad = math.max(opts.pad or 0, (touchMin - math.min(w, h)) / 2, 0)
	local hit = opts.hit
	if hit == nil then
		hit = Core.Make("TextButton", {
			Name = "Hit",
			AutoButtonColor = false,
			BackgroundTransparency = 1,
			BorderSizePixel = 0,
			Position = UDim2.fromOffset(-pad, -pad),
			Size = UDim2.new(1, pad * 2, 1, pad * 2),
			Text = "",
			ZIndex = (opts.z or base.z) + 8,
		}, root)
	end
	local hitButton = hit :: GuiButton
	self.hit = hitButton
	hitButton.AutoButtonColor = false
	hitButton.Selectable = opts.selectable ~= false
	-- The kit's hover state is the gamepad selection cue.
	local empty = Core.Make("Frame", { Name = "NoSelectionImage", BackgroundTransparency = 1, Visible = false }, nil)
	hitButton.SelectionImageObject = empty
	local maid = base.maid
	maid:Give(empty)
	maid:Give(function()
		pressing[self] = nil
	end)

	maid:Give(hitButton.MouseEnter:Connect(function()
		if Interact.UsingMouse() then
			self.flags.hover = true
			if self.flags.enabled ~= false then
				Sound.Play("hover")
			end
			self:Refresh()
		end
	end))
	maid:Give(hitButton.MouseLeave:Connect(function()
		self.flags.hover = false
		-- Leaving cancels a press: releasing outside does not activate.
		self:_endPress()
		self:Refresh()
	end))
	maid:Give(hitButton.SelectionGained:Connect(function()
		self.flags.focused = true
		self:Refresh()
	end))
	maid:Give(hitButton.SelectionLost:Connect(function()
		self.flags.focused = false
		self:_endPress()
		self:Refresh()
	end))
	maid:Give(hitButton.InputBegan:Connect(function(input: InputObject)
		local pressKey = input.KeyCode == Enum.KeyCode.ButtonA
		if not (PRESS_TYPES[input.UserInputType] or pressKey) then
			return
		end
		if self.flags.enabled == false or self.flags.busy then
			return
		end
		self.flags.pressed = true
		self.pressInput = input
		pressing[self] = true
		watchEnds()
		self:Refresh()
	end))
	maid:Give(hitButton.InputEnded:Connect(function(input: InputObject)
		if input == self.pressInput or PRESS_TYPES[input.UserInputType] then
			if input.UserInputType == Enum.UserInputType.Touch then
				self.flags.hover = false
			end
			self:_endPress()
			self:Refresh()
		end
	end))
	maid:Give(hitButton.Activated:Connect(function()
		self:_activate()
	end))
	maid:Give(root:GetAttributeChangedSignal("DebugState"):Connect(function()
		self:Refresh()
	end))
	self:Refresh()
	return self
end

function Controller:_endPress()
	pressing[self] = nil
	self.pressInput = nil
	if self.flags.pressed then
		self.flags.pressed = false
		self:Refresh()
	end
end

function Controller:_activate()
	local flags = self.flags
	if flags.enabled == false or flags.busy then
		return
	end
	if flags.locked then
		Sound.Play("error")
		if self.opts.onLocked then
			self.opts.onLocked(self)
		end
		return
	end
	local now = os.clock()
	if now - self.lastPress < (self.opts.debounce or Tokens.Space("debounce", 0.15)) then
		return
	end
	self.lastPress = now
	Sound.Play(self.opts.sound or "click")
	if self.opts.onPress then
		self.opts.onPress(self)
	end
end

-- Runs the press action as an activation would (flows and keyboard shortcuts).
function Controller:Activate()
	self.lastPress = -math.huge
	self:_activate()
end

-- The state drawn now.
function Controller:State(): string
	return self.state
end

function Controller:Refresh()
	local debug = self.root:GetAttribute("DebugState")
	local state = KitModel.ResolveState(self.flags, debug)
	local changed = state ~= self.state
	local previous = self.state
	self.state = state
	self.root:SetAttribute("KitState", state)
	if self.opts.render then
		self.opts.render(state, self)
	end
	if not changed then
		return
	end
	-- Scale feedback on the visual frame: down while pressed, a touch up on hover
	-- for tiles and icon buttons, an overshoot back on release.
	local target = 1
	local key = "hover"
	if state == "pressed" and self.opts.pressScale ~= false then
		target, key = Tokens.Scale("pressed"), "press"
	elseif (state == "hover" or state == "focused") and self.opts.hoverScale then
		target = Tokens.Scale("hover")
	elseif previous == "pressed" then
		key = "release"
	end
	Motion.Play(self.base.scale, key, { Scale = target })
end

function Controller:Set(flag: string, value: any)
	if self.flags[flag] == value then
		return
	end
	self.flags[flag] = value
	self:Refresh()
end

function Controller:SetEnabled(enabled: boolean)
	self.flags.enabled = enabled
	if not enabled then
		self.flags.pressed = false
		pressing[self] = nil
	end
	self:_applyInteractable()
	self:Refresh()
end

function Controller:_applyInteractable()
	local live = self.flags.enabled ~= false and not self.flags.busy
	pcall(function()
		(self.hit :: any).Interactable = live or self.flags.locked == true
	end)
	self.hit.Selectable = self.opts.selectable ~= false and (live or self.flags.locked == true)
end

function Controller:SetSelected(selected: boolean)
	self:Set("selected", selected == true)
end

function Controller:SetBusy(busy: boolean)
	self.flags.busy = busy == true
	self:_applyInteractable()
	self:Refresh()
end

-- Locked: drawn disabled with a lock, still selectable; presses call onLocked.
function Controller:SetLocked(locked: boolean)
	self.flags.locked = locked == true
	self:_applyInteractable()
	self:Refresh()
end

return Interact
