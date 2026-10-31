-- Which input the player is using now, so hints match it: "mouse",
-- "keyboard", "touch" or "gamepad" (from the last input; PreferredInput where
-- the engine has it). Key caps, tooltips and screens read it to show gamepad
-- button names or hide keyboard hints; Input.Changed fires when it changes.
--
--   Kit.Input.Hint("B", "ButtonX")   -- "B" with a keyboard, "X" on a gamepad, nil on touch
--   local stop = Kit.Input.Watch(function(kind) refreshHints(kind) end)
--   Kit.Input.SetHudDefault(hud.tiles[1].control.hit) -- gamepad lands here when nothing is selected

local GuiService = game:GetService("GuiService")
local UserInputService = game:GetService("UserInputService")

local Input = {}

-- Gamepad button names as players read them.
Input.GAMEPAD_NAMES = {
	ButtonA = "A",
	ButtonB = "B",
	ButtonX = "X",
	ButtonY = "Y",
	ButtonL1 = "LB",
	ButtonR1 = "RB",
	ButtonL2 = "LT",
	ButtonR2 = "RT",
	ButtonL3 = "LS",
	ButtonR3 = "RS",
	ButtonSelect = "View",
	ButtonStart = "Menu",
	DPadUp = "D-Up",
	DPadDown = "D-Down",
	DPadLeft = "D-Left",
	DPadRight = "D-Right",
}

local function kindOf(inputType: any): string?
	local name = if typeof(inputType) == "EnumItem" then inputType.Name else tostring(inputType)
	if string.find(name, "Gamepad") then
		return "gamepad"
	elseif string.find(name, "Touch") then
		return "touch"
	elseif string.find(name, "Keyboard") then
		return "keyboard"
	elseif string.find(name, "Mouse") then
		return "mouse"
	end
	return nil
end

-- The input in use now.
function Input.Type(): string
	local ok, preferred = pcall(function()
		return (UserInputService :: any).PreferredInput
	end)
	if ok and preferred ~= nil then
		local name = if typeof(preferred) == "EnumItem" then preferred.Name else tostring(preferred)
		if string.find(name, "Gamepad") then
			return "gamepad"
		elseif string.find(name, "Touch") then
			return "touch"
		end
	end
	local last = kindOf(UserInputService:GetLastInputType())
	if last then
		return last
	end
	if UserInputService.GamepadEnabled and not UserInputService.KeyboardEnabled then
		return "gamepad"
	elseif UserInputService.TouchEnabled and not UserInputService.KeyboardEnabled then
		return "touch"
	end
	return "mouse"
end

function Input.IsGamepad(): boolean
	return Input.Type() == "gamepad"
end

function Input.IsTouch(): boolean
	return Input.Type() == "touch"
end

-- The hint for the current input: `keyboard` text, the gamepad button's name
-- for `gamepadKey` (a KeyCode name, or text) on a gamepad, and nil on touch
-- (touch has no key hints).
function Input.Hint(keyboard: string?, gamepadKey: string?): string?
	local kind = Input.Type()
	if kind == "touch" then
		return nil
	elseif kind == "gamepad" then
		if gamepadKey == nil then
			return nil
		end
		return Input.GAMEPAD_NAMES[gamepadKey] or gamepadKey
	end
	return keyboard
end

-- Changed: calls fn(kind) whenever the input kind changes. Returns a stop function.
local listeners: { [any]: boolean } = {}
local current: string? = nil
local hudDefault: GuiObject? = nil
local hooked = false

local function hook()
	if hooked then
		return
	end
	hooked = true
	current = Input.Type()
	UserInputService.LastInputTypeChanged:Connect(function()
		local now = Input.Type()
		if now == current then
			return
		end
		current = now
		-- A gamepad picked up with nothing selected lands on the HUD default.
		if now == "gamepad" and GuiService.SelectedObject == nil and hudDefault and hudDefault.Parent then
			GuiService.SelectedObject = hudDefault
		end
		for fn in table.clone(listeners) do
			task.spawn(fn, now)
		end
	end)
end

function Input.Watch(fn: (string) -> ()): () -> ()
	hook()
	listeners[fn] = true
	return function()
		listeners[fn] = nil
	end
end

-- The control gamepad selection goes to when a gamepad is picked up and
-- nothing is selected (the HUD's first menu tile). nil clears it.
function Input.SetHudDefault(object: GuiObject?)
	hook()
	hudDefault = object
	if object and Input.IsGamepad() and GuiService.SelectedObject == nil then
		GuiService.SelectedObject = object
	end
end

return Input
