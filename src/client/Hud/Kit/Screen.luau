-- A modal layer: its own ScreenGui with the veil over the game and a centred
-- window holder fitted to the screen (Kit.Scale.Window). Opening registers it
-- with Kit.Modal (one window at a time; Escape / B close it), fades the veil in
-- and pops the window from 0.94 to 1; closing reverses that and then disables
-- the gui.
--
--   local screen = Kit.Screen.new("FlintbornInventory", { size = { 1187, 652 } })
--   local window = Kit.Window.new(screen, { title = "Inventory", icon = "backpack" })
--   screen:Open()

local Players = game:GetService("Players")

local Core = require(script.Parent.Core)
local Modal = require(script.Parent.Modal)
local Motion = require(script.Parent.Motion)
local Scale = require(script.Parent.Scale)
local Sound = require(script.Parent.Sound)
local Tokens = require(script.Parent.Tokens)

local Screen = {}
Screen.__index = Screen

export type Props = {
	size: { number },
	displayOrder: number?,
	dim: boolean?,
	blur: boolean?,
	parent: Instance?,
	layer: string?,
	onClose: (() -> ())?,
}

function Screen.new(name: string, props: Props)
	local w, h = props.size[1], props.size[2]
	local gui = Core.Make("ScreenGui", {
		Name = name,
		DisplayOrder = props.displayOrder or Tokens.Order(if props.layer == "dialog" then "dialog" else "window"),
		Enabled = false,
		IgnoreGuiInset = true,
		ResetOnSpawn = false,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, nil)
	-- Windows fit themselves (Scale.Window applies the player's UI scale).
	gui:SetAttribute("FitsItself", true)
	gui:SetAttribute("KitComponent", "Screen")
	gui:SetAttribute("KitRole", "screen")
	gui:SetAttribute("KitState", "closed")
	pcall(function()
		gui.ScreenInsets = Enum.ScreenInsets.DeviceSafeInsets
	end)
	local veilColor, veilAlpha = Tokens.Veil()
	local veil = Core.Make("Frame", {
		Name = "Veil",
		Active = true,
		BackgroundColor3 = veilColor,
		BackgroundTransparency = if props.dim == false then 1 else veilAlpha,
		BorderSizePixel = 0,
		-- Past the safe-area edges too, so a notch's strip is veiled as well.
		Position = UDim2.fromOffset(-400, -400),
		Size = UDim2.new(1, 800, 1, 800),
		ZIndex = 0,
	}, gui)
	local holder = Core.Make("Frame", {
		Name = "Holder",
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(w, h),
		ZIndex = 1,
	}, gui)
	local scale = Core.Make("UIScale", { Name = "Fit", Scale = 1 }, holder)
	-- The window itself: the open/close pop scales it without touching the fit.
	local window = Core.Make("Frame", {
		Name = "Window",
		Active = true,
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromScale(1, 1),
		ZIndex = 1,
	}, holder)
	local pop = Core.Make("UIScale", { Name = "Pop", Scale = 1 }, window)
	gui.Parent = props.parent or Players.LocalPlayer:FindFirstChildOfClass("PlayerGui")
	local self = setmetatable({
		gui = gui,
		veil = veil,
		holder = holder,
		window = window,
		scale = scale,
		pop = pop,
		size = { w, h },
		layer = props.layer or "window",
		blur = props.blur ~= false and props.dim ~= false,
		dimAlpha = if props.dim == false then 1 else veilAlpha,
		onClose = props.onClose,
		isOpen = false,
		defaultSelection = nil,
		Opened = Core.Signal(),
		Closed = Core.Signal(),
		maid = Core.Maid(),
	}, Screen)
	self.maid:Give(gui)
	return self
end

-- Keeps the window fitted to the screen (call once after building).
function Screen:Watch()
	if self.unwatch == nil then
		self.unwatch = Scale.Window(self)
		self.maid:Give(self.unwatch)
	end
end

-- Fits the window by hand: a W × H screen whose top `top` px are the top bar.
function Screen:Fit(width: number, height: number, top: number?, userScale: number?)
	local k, centre = Scale.WindowFit(width, height, top or 0, self.size[1], self.size[2], userScale)
	self.scale.Scale = k
	self.holder.Position = UDim2.fromOffset(centre.X, centre.Y)
end

function Screen:IsOpen(): boolean
	return self.isOpen == true
end

-- The control gamepad selection moves to when the screen opens.
function Screen:SetDefaultSelection(object: GuiObject?)
	self.defaultSelection = object
end

-- Shows the screen. `gamepad` moves selection to the default control even when
-- nothing is selected yet.
function Screen:Open(gamepad: boolean?)
	if self.isOpen then
		return
	end
	self.isOpen = true
	self.closing = nil
	self.gui.Enabled = true
	self.window.Interactable = true
	self.gui:SetAttribute("KitState", "open")
	Modal.Open(self, self.layer, gamepad)
	Sound.Play("open")
	Motion.Set(self.veil, { BackgroundTransparency = 1 })
	Motion.Play(self.veil, "windowOpen", { BackgroundTransparency = self.dimAlpha })
	Motion.Set(self.pop, { Scale = Tokens.Scale("windowFrom") })
	Motion.Play(self.pop, "windowOpen", { Scale = 1 })
	self.Opened:Fire()
end

-- Hides the screen: the window stops taking input at once, shrinks back and
-- the veil fades, then the gui is disabled (at once with reduced motion).
function Screen:Close()
	if not self.isOpen then
		return
	end
	self.isOpen = false
	self.gui:SetAttribute("KitState", "closed")
	self.window.Interactable = false
	Modal.Closed(self)
	Sound.Play("close")
	local token = {}
	self.closing = token
	Motion.Play(self.veil, "windowClose", { BackgroundTransparency = 1 })
	Motion.Play(self.pop, "windowClose", { Scale = Tokens.Scale("windowFrom") }, function()
		if self.closing == token then
			self.closing = nil
			self.gui.Enabled = false
			Motion.Set(self.pop, { Scale = 1 })
		end
	end)
	if self.onClose then
		self.onClose()
	end
	self.Closed:Fire()
end

function Screen:Toggle(gamepad: boolean?)
	if self:IsOpen() then
		self:Close()
	else
		self:Open(gamepad)
	end
end

function Screen:Destroy()
	self:Close()
	self.Opened:Destroy()
	self.Closed:Destroy()
	self.maid:Clean()
end

return Screen
