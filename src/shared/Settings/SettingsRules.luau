-- Player settings (GDD §11, §25, §46): every saved choice's default, valid range,
-- profile key and the player attribute it travels as. The server sanitises what
-- a client sends with these rules before saving; the client reads the same table
-- to draw the Settings screen and to fall back on defaults. Pure functions,
-- shared by the client, the server and specs. Keyboard rebinds live in Keybinds.

local SettingsRules = {}

export type Setting = {
	key: string, -- profile.choices key
	attribute: string, -- player attribute
	kind: "number" | "boolean" | "choice",
	default: any,
	min: number?,
	max: number?,
	step: number?,
	options: { string }?,
}

-- Ordered as they are listed. Volumes and camera sensitivity are whole percents.
SettingsRules.Settings = {
	{ key = "uiScale", attribute = "UiScale", kind = "number", default = 1, min = 0.8, max = 1.4, step = 0.1 },
	{ key = "colourBlindMode", attribute = "ColourBlind", kind = "boolean", default = false },
	{ key = "reducedMotion", attribute = "ReducedMotion", kind = "boolean", default = false },
	{ key = "subtitles", attribute = "Subtitles", kind = "boolean", default = true },
	{ key = "musicVolume", attribute = "MusicVolume", kind = "number", default = 75, min = 0, max = 100, step = 1 },
	{ key = "effectsVolume", attribute = "EffectsVolume", kind = "number", default = 80, min = 0, max = 100, step = 1 },
	-- 50 is Roblox's own sensitivity; 10 is a fifth of it and 100 twice it.
	{
		key = "cameraSensitivity",
		attribute = "CameraSensitivity",
		kind = "number",
		default = 50,
		min = 10,
		max = 100,
		step = 1,
	},
	{ key = "invertCamera", attribute = "InvertCamera", kind = "boolean", default = false },
	{ key = "showDamage", attribute = "ShowDamage", kind = "boolean", default = true },
	{ key = "showNames", attribute = "ShowNames", kind = "boolean", default = true },
	{
		key = "graphicsQuality",
		attribute = "GraphicsQuality",
		kind = "choice",
		default = "High",
		options = { "Low", "Medium", "High" },
	},
}

local byKey = {}
for _, setting in SettingsRules.Settings do
	byKey[setting.key] = setting
end

function SettingsRules.Get(key: string): Setting?
	return byKey[key]
end

-- A valid value for `setting` from anything a client sent, or nil when it is not
-- usable (the saved value then stays).
function SettingsRules.Clean(setting: Setting, value: any): any
	if setting.kind == "boolean" then
		return if type(value) == "boolean" then value else nil
	elseif setting.kind == "choice" then
		return if type(value) == "string" and table.find(setting.options :: { string }, value) then value else nil
	end
	local number = tonumber(value)
	if number == nil or number ~= number or number == math.huge or number == -math.huge then
		return nil
	end
	local step = setting.step or 1
	number = math.round(number / step) * step
	-- Snap off float noise from the division (0.30000000000000004 → 0.3).
	number = math.round(number * 1000) / 1000
	return math.clamp(number, setting.min :: number, setting.max :: number)
end

-- Every setting's value: `choices` where valid, else the default.
function SettingsRules.Resolve(choices: any): { [string]: any }
	local values = {}
	for _, setting in SettingsRules.Settings do
		local saved = if type(choices) == "table" then choices[setting.key] else nil
		local clean = if saved == nil then nil else SettingsRules.Clean(setting, saved)
		values[setting.key] = if clean == nil then setting.default else clean
	end
	return values
end

-- Applies a client's `changes` to `choices` in place, keeping only known keys
-- with valid values. Returns how many settings changed.
function SettingsRules.Apply(choices: { [string]: any }, changes: any): number
	if type(changes) ~= "table" then
		return 0
	end
	local changed = 0
	for _, setting in SettingsRules.Settings do
		local value = changes[setting.key]
		if value ~= nil then
			local clean = SettingsRules.Clean(setting, value)
			if clean ~= nil and choices[setting.key] ~= clean then
				choices[setting.key] = clean
				changed += 1
			end
		end
	end
	return changed
end

-- Camera sensitivity percent → Roblox's mouse-delta multiplier (50 → 1).
function SettingsRules.MouseSensitivity(percent: number?): number
	return math.clamp((percent or 50) / 50, 0.2, 2)
end

-- Volume percent → a SoundGroup volume (0–1).
function SettingsRules.Volume(percent: number?): number
	return math.clamp((percent or 100) / 100, 0, 1)
end

-- Graphics quality → the share of decorative particles kept and whether shadows draw.
SettingsRules.Graphics = {
	Low = { particles = 0.25, shadows = false },
	Medium = { particles = 0.6, shadows = true },
	High = { particles = 1, shadows = true },
}

return SettingsRules
