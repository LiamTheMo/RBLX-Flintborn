-- One window at a time (ARCHITECTURE §1.3). Kit.Screen registers here when it
-- opens: opening a window closes the window already open (and any dialog over
-- it); a ConfirmDialog stacks above. Escape and gamepad B close the top layer
-- while anything is open. Gamepad selection moves to the opened layer's default
-- control and comes back on close. A shared Lighting.KitBlur is on while a
-- window is open on Medium and High graphics, and always restored on close.

local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local Lighting = game:GetService("Lighting")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local Input = require(script.Parent.Input)
local Motion = require(script.Parent.Motion)
local Tokens = require(script.Parent.Tokens)

local Modal = {}

Modal.BACK_ACTION = "KitModalBack"

local stack = KitModel.ModalStack()
local selections: { [any]: GuiObject? } = {}
local blurUsers = 0
local bound = false

local function graphicsAllowBlur(): boolean
	local ok, level = pcall(function()
		local settings = (UserSettings :: any)():GetService("UserGameSettings")
		return settings.SavedQualityLevel.Value
	end)
	-- Automatic quality (0) and anything at or above the token's level blur.
	return ok and type(level) == "number" and (level == 0 or level >= Tokens.Data.blur.minQuality)
end

local function blur(on: boolean)
	local effect = Lighting:FindFirstChild("KitBlur") :: BlurEffect?
	if on then
		blurUsers += 1
		if blurUsers > 1 or not graphicsAllowBlur() then
			return
		end
		if effect == nil then
			effect = Instance.new("BlurEffect")
			effect.Name = "KitBlur"
			effect.Size = 0
			effect.Parent = Lighting
		end
		Motion.Play(effect :: BlurEffect, "windowOpen", { Size = Tokens.Data.blur.size })
	else
		blurUsers = math.max(0, blurUsers - 1)
		if blurUsers == 0 and effect then
			effect:Destroy()
		end
	end
end

local function onBack(_, state)
	if state ~= Enum.UserInputState.Begin then
		return Enum.ContextActionResult.Pass
	end
	local top = stack:Top()
	if top == nil then
		return Enum.ContextActionResult.Pass
	end
	if top.Back then
		top:Back()
	else
		top:Close()
	end
	return Enum.ContextActionResult.Sink
end

-- Functions told when a layer opens or closes (the toast column moves clear of
-- an open window's title).
local changed: { [any]: boolean } = {}
function Modal.OnChanged(fn: () -> ()): () -> ()
	changed[fn] = true
	return function()
		changed[fn] = nil
	end
end

local function notify()
	for fn in table.clone(changed) do
		task.spawn(fn)
	end
end

local function bind()
	notify()
	local open = stack:Count() > 0
	if open and not bound then
		bound = true
		ContextActionService:BindActionAtPriority(
			Modal.BACK_ACTION,
			onBack,
			false,
			Enum.ContextActionPriority.High.Value,
			Enum.KeyCode.ButtonB,
			Enum.KeyCode.Escape
		)
	elseif not open and bound then
		bound = false
		ContextActionService:UnbindAction(Modal.BACK_ACTION)
	end
end

-- Registers `entry` (an object with :Close(), optional :Back(), .blur and
-- .defaultSelection) as open on `layer` ("window" | "dialog"). Entries it
-- displaces are closed first. Selection moves to entry.defaultSelection when a
-- gamepad is driving (`gamepad`, or something is selected already).
function Modal.Open(entry, layer: string?, gamepad: boolean?)
	if stack:IsOpen(entry) then
		return
	end
	local closing = stack:Open(entry, layer or "window")
	local previous = GuiService.SelectedObject
	for _, other in closing do
		-- Already off the stack: release what it held, then let it close. The
		-- new entry inherits the selection the displaced one would restore.
		if other.blur then
			blur(false)
		end
		previous = selections[other] or previous
		selections[other] = nil
		other:Close()
	end
	selections[entry] = previous
	if entry.blur then
		blur(true)
	end
	bind()
	-- A gamepad player always lands on the default control (opened with a
	-- gamepad, the last input a gamepad, or something already selected).
	local default = entry.defaultSelection
	if default and (gamepad or Input.IsGamepad() or GuiService.SelectedObject ~= nil) then
		GuiService.SelectedObject = default
	end
end

-- Marks `entry` closed; restores the selection it took and its blur.
function Modal.Closed(entry)
	if not stack:Close(entry) then
		return
	end
	if entry.blur then
		blur(false)
	end
	local previous = selections[entry]
	selections[entry] = nil
	if GuiService.SelectedObject ~= nil or previous ~= nil then
		GuiService.SelectedObject = if previous and previous.Parent then previous else nil
	end
	bind()
end

function Modal.Top(): any
	return stack:Top()
end

function Modal.IsOpen(entry): boolean
	return stack:IsOpen(entry)
end

function Modal.Count(): number
	return stack:Count()
end

-- Closes the top layer, as Escape or B would.
function Modal.Back(): boolean
	return onBack(nil, Enum.UserInputState.Begin) == Enum.ContextActionResult.Sink
end

return Modal
