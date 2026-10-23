-- Keyboard controls (GDD §25.4, §46). Every action has a default key; players may
-- rebind any of them in Settings and the choice saves to their profile. Only the
-- keyboard key is rebindable; gamepad buttons stay fixed. Two actions never share
-- a key: assigning a key that another action uses swaps the two. A profile only
-- stores the actions that differ from the default, and anything malformed falls
-- back to the defaults. Pure functions, shared by the client, the server and specs.

local Keybinds = {}

-- Ordered as Settings lists them. `gamepad` buttons are fixed; `hold` actions act
-- while the key is held.
Keybinds.Actions = {
	{ id = "Sprint", label = "Sprint (hold)", default = "LeftShift", gamepad = { "ButtonL3" }, hold = true },
	{ id = "Crouch", label = "Crouch", default = "C", gamepad = { "ButtonR3" } },
	{ id = "Interact", label = "Interact / pick up", default = "E", gamepad = {} },
	{ id = "Backpack", label = "Backpack / inventory", default = "Tab", gamepad = { "ButtonY" } },
	{ id = "Drop", label = "Drop item", default = "Q", gamepad = { "ButtonL1" } },
	{ id = "Hotbar1", label = "Hotbar slot 1", default = "One", gamepad = {} },
	{ id = "Hotbar2", label = "Hotbar slot 2", default = "Two", gamepad = {} },
	{ id = "Hotbar3", label = "Hotbar slot 3", default = "Three", gamepad = {} },
	{ id = "Hotbar4", label = "Hotbar slot 4", default = "Four", gamepad = {} },
	{ id = "Hotbar5", label = "Hotbar slot 5", default = "Five", gamepad = {} },
	{ id = "Hotbar6", label = "Hotbar slot 6", default = "Six", gamepad = {} },
	{ id = "Hotbar7", label = "Hotbar slot 7", default = "Seven", gamepad = {} },
	{ id = "Hotbar8", label = "Hotbar slot 8", default = "Eight", gamepad = {} },
	{ id = "Hotbar9", label = "Hotbar slot 9", default = "Nine", gamepad = {} },
	{ id = "Craft", label = "Crafting", default = "V", gamepad = { "DPadUp" } },
	{ id = "Build", label = "Build mode", default = "X", gamepad = { "DPadRight" } },
	{ id = "Rotate", label = "Rotate piece", default = "R", gamepad = { "ButtonL2" } },
	{ id = "Tribe", label = "Tribe", default = "T", gamepad = { "DPadLeft" } },
	{ id = "Map", label = "Map", default = "N", gamepad = { "DPadDown" } },
	{ id = "Progression", label = "Progress", default = "P", gamepad = { "ButtonSelect" } },
	{ id = "Vault", label = "Vault (lobby)", default = "G", gamepad = { "DPadRight" } },
	{ id = "Forge", label = "Forge (lobby)", default = "F", gamepad = { "DPadDown" } },
	{ id = "Market", label = "Market (lobby)", default = "M", gamepad = { "ButtonL2" } },
	{ id = "Trade", label = "Trade (lobby)", default = "Y", gamepad = { "ButtonL1" } },
	{ id = "Settings", label = "Settings", default = "O", gamepad = {} },
}

local byId = {}
for _, action in Keybinds.Actions do
	byId[action.id] = action
end

function Keybinds.Get(id: string)
	return byId[id]
end

-- Keys a player may bind. Movement (W A S D, Space), chat (/), menus (Escape),
-- Enter and Backspace stay with Roblox.
local ALLOWED = {}
for _, name in
	{
		"B",
		"C",
		"E",
		"F",
		"G",
		"H",
		"I",
		"J",
		"K",
		"L",
		"M",
		"N",
		"O",
		"P",
		"Q",
		"R",
		"T",
		"U",
		"V",
		"X",
		"Y",
		"Z",
		"Zero",
		"One",
		"Two",
		"Three",
		"Four",
		"Five",
		"Six",
		"Seven",
		"Eight",
		"Nine",
		"Tab",
		"CapsLock",
		"LeftShift",
		"RightShift",
		"LeftControl",
		"RightControl",
		"LeftAlt",
		"RightAlt",
		"Backquote",
		"Minus",
		"Equals",
		"LeftBracket",
		"RightBracket",
		"Semicolon",
		"Quote",
		"Comma",
		"Period",
	}
do
	ALLOWED[name] = true
end

function Keybinds.IsAllowed(key: any): boolean
	return type(key) == "string" and ALLOWED[key] == true
end

local DISPLAY = {
	Zero = "0",
	One = "1",
	Two = "2",
	Three = "3",
	Four = "4",
	Five = "5",
	Six = "6",
	Seven = "7",
	Eight = "8",
	Nine = "9",
	LeftShift = "Shift",
	RightShift = "Right Shift",
	LeftControl = "Ctrl",
	RightControl = "Right Ctrl",
	LeftAlt = "Alt",
	RightAlt = "Right Alt",
	CapsLock = "Caps Lock",
	Backquote = "`",
	Minus = "-",
	Equals = "=",
	LeftBracket = "[",
	RightBracket = "]",
	Semicolon = ";",
	Quote = "'",
	Comma = ",",
	Period = ".",
}

-- A key name as players read it ("One" → "1", "LeftShift" → "Shift").
function Keybinds.Display(key: string): string
	return DISPLAY[key] or key
end

-- The full action → key map: defaults overlaid with the valid saved overrides.
-- If the overrides would give two actions one key (a stale or tampered save),
-- every override is dropped and the defaults apply.
function Keybinds.Resolve(overrides: any): { [string]: string }
	local map = {}
	for _, action in Keybinds.Actions do
		map[action.id] = action.default
	end
	if type(overrides) ~= "table" then
		return map
	end
	for id, key in overrides do
		if byId[id] and Keybinds.IsAllowed(key) then
			map[id] = key
		end
	end
	local used = {}
	for _, action in Keybinds.Actions do
		local key = map[action.id]
		if used[key] then
			return Keybinds.Resolve(nil)
		end
		used[key] = true
	end
	return map
end

-- The overrides worth storing: actions whose key differs from the default.
function Keybinds.Overrides(map: { [string]: string }): { [string]: string }
	local overrides = {}
	for _, action in Keybinds.Actions do
		local key = map[action.id]
		if key ~= nil and key ~= action.default then
			overrides[action.id] = key
		end
	end
	return overrides
end

-- Cleans overrides received from a client: unknown actions and keys are dropped,
-- and a conflicting set resets to the defaults.
function Keybinds.Sanitize(overrides: any): { [string]: string }
	return Keybinds.Overrides(Keybinds.Resolve(overrides))
end

-- Binds `key` to action `id`, swapping with whichever action held it. Returns the
-- new overrides, or nil (changing nothing) for an unknown action or key.
function Keybinds.Assign(overrides: any, id: string, key: string): { [string]: string }?
	if byId[id] == nil or not Keybinds.IsAllowed(key) then
		return nil
	end
	local map = Keybinds.Resolve(overrides)
	local previous = map[id]
	for other, otherKey in map do
		if other ~= id and otherKey == key then
			map[other] = previous
		end
	end
	map[id] = key
	return Keybinds.Overrides(map)
end

-- Replaces {Action} tokens in a hint with the bound key, e.g. "Press {Craft}".
function Keybinds.Format(text: string, map: { [string]: string }): string
	return (
		string.gsub(text, "{(%w+)}", function(id)
			local key = map[id]
			return if key then Keybinds.Display(key) else nil
		end)
	)
end

return Keybinds
