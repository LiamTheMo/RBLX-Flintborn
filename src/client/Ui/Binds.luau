-- Binds game actions to the player's chosen keys (GDD §46). Controllers call
-- Binds.Bind instead of ContextActionService directly; when the player rebinds a
-- key in Settings (the server echoes it back as the "Keybinds" attribute), every
-- bound action moves to its new key at once and Changed fires so hint labels can
-- refresh. Interact is the key for proximity prompts (pick up, open, loot).

local ContextActionService = game:GetService("ContextActionService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ProximityPromptService = game:GetService("ProximityPromptService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Keybinds = require(ReplicatedStorage.Shared.Settings.Keybinds)

local Binds = {}

local player = Players.LocalPlayer
local changed = Instance.new("BindableEvent")
local overrides = {}
local map = Keybinds.Resolve(nil)
local bound = {}
local shownPrompts = {}
-- The key each prompt was authored with, remembered the first time it shows.
local authoredKeys = setmetatable({}, { __mode = "k" })

-- Fires after the player's keys change.
Binds.Changed = changed.Event

local function enumKey(name: string): Enum.KeyCode?
	local ok, key = pcall(function()
		return (Enum.KeyCode :: any)[name]
	end)
	return if ok then key else nil
end

local function actionName(id: string): string
	return "Flintborn" .. id
end

local function apply(id: string)
	local entry = bound[id]
	local action = Keybinds.Get(id)
	local inputs = {}
	local key = enumKey(map[id])
	if key then
		table.insert(inputs, key)
	end
	for _, name in action.gamepad do
		local button = enumKey(name)
		if button then
			table.insert(inputs, button)
		end
	end
	for _, extra in entry.options.extra or {} do
		table.insert(inputs, extra)
	end
	local name = actionName(id)
	ContextActionService:UnbindAction(name)
	if entry.options.priority then
		ContextActionService:BindActionAtPriority(
			name,
			entry.handler,
			entry.options.touchButton == true,
			entry.options.priority,
			table.unpack(inputs)
		)
	else
		ContextActionService:BindAction(name, entry.handler, entry.options.touchButton == true, table.unpack(inputs))
	end
	if entry.options.title then
		ContextActionService:SetTitle(name, entry.options.title)
	end
end

-- Binds `handler` (a ContextActionService handler) to action `id`'s key and its
-- fixed gamepad buttons. Options: priority, touchButton, title, and `extra`
-- inputs that are not rebindable (a mouse button).
function Binds.Bind(id: string, handler, options: any?)
	assert(Keybinds.Get(id), "Unknown keybind action: " .. id)
	bound[id] = { handler = handler, options = options or {} }
	apply(id)
end

function Binds.Unbind(id: string)
	if bound[id] then
		bound[id] = nil
		ContextActionService:UnbindAction(actionName(id))
	end
end

-- The KeyCode currently bound to action `id`.
function Binds.Key(id: string): Enum.KeyCode?
	return enumKey(map[id])
end

-- The bound key as players read it ("Tab", "1", "Shift").
function Binds.Label(id: string): string
	return Keybinds.Display(map[id] or "?")
end

-- Fills {Action} tokens in a hint with the bound keys.
function Binds.Format(text: string): string
	return Keybinds.Format(text, map)
end

-- The player's saved overrides (what Settings edits and sends to the server).
function Binds.Overrides(): { [string]: string }
	return table.clone(overrides)
end

-- The full action → key-name map in force.
function Binds.Map(): { [string]: string }
	return table.clone(map)
end

-- Only prompts authored on E (the Interact default) follow the Interact key; a
-- prompt offering a second choice on another key (a planter's other crops) keeps
-- its own.
local function retargetPrompt(prompt: ProximityPrompt)
	if authoredKeys[prompt] == nil then
		authoredKeys[prompt] = prompt.KeyboardKeyCode
	end
	local key = Binds.Key("Interact")
	if key and authoredKeys[prompt] == Enum.KeyCode.E and prompt.KeyboardKeyCode ~= key then
		prompt.KeyboardKeyCode = key
	end
end

local function load()
	local raw = player:GetAttribute("Keybinds")
	local decoded = nil
	if type(raw) == "string" and raw ~= "" then
		local ok, value = pcall(HttpService.JSONDecode, HttpService, raw)
		decoded = if ok then value else nil
	end
	overrides = Keybinds.Sanitize(decoded)
	map = Keybinds.Resolve(overrides)
	for id in bound do
		apply(id)
	end
	for prompt in shownPrompts do
		retargetPrompt(prompt)
	end
	changed:Fire()
end

-- Proximity prompts are server objects; the key that triggers them is a local
-- choice, so each prompt is retargeted as it appears.
ProximityPromptService.PromptShown:Connect(function(prompt)
	shownPrompts[prompt] = true
	retargetPrompt(prompt)
end)
ProximityPromptService.PromptHidden:Connect(function(prompt)
	shownPrompts[prompt] = nil
end)

player:GetAttributeChangedSignal("Keybinds"):Connect(load)
load()

return Binds
