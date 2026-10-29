-- Player settings (GDD §11, §25): defaults, ranges and what the server accepts.

local Shared = game:GetService("ReplicatedStorage").Shared
local SettingsRules = require(Shared.Settings.SettingsRules)
local ProfileSchema = require(Shared.Data.ProfileSchema)

test("a fresh profile has every setting at its default", function()
	local choices = ProfileSchema.Default().choices
	local values = SettingsRules.Resolve(choices)
	for _, setting in SettingsRules.Settings do
		expectEq(choices[setting.key], setting.default, setting.key .. " is in the profile default")
		expectEq(values[setting.key], setting.default, setting.key .. " resolves to its default")
	end
	expectEq(values.musicVolume, 75, "music 75")
	expectEq(values.effectsVolume, 80, "effects 80")
	expectEq(values.cameraSensitivity, 50, "camera sensitivity 50")
	expectEq(values.graphicsQuality, "High", "graphics High")
	expectEq(values.showDamage, true, "damage numbers on")
	expectEq(values.showNames, true, "names on")
	expectEq(values.invertCamera, false, "camera not inverted")
end)

test("numbers snap to their step and stay in range", function()
	local scale = SettingsRules.Get("uiScale")
	expectEq(SettingsRules.Clean(scale, 1.26), 1.3, "UI scale rounds to 0.1")
	expectEq(SettingsRules.Clean(scale, 9), 1.4, "UI scale capped")
	expectEq(SettingsRules.Clean(scale, 0.1), 0.8, "UI scale floored")
	local music = SettingsRules.Get("musicVolume")
	expectEq(SettingsRules.Clean(music, 42.6), 43, "whole percents")
	expectEq(SettingsRules.Clean(music, -5), 0, "never negative")
	expectEq(SettingsRules.Clean(music, 250), 100, "at most 100")
	expectEq(SettingsRules.Clean(music, 0 / 0), nil, "NaN refused")
	expectEq(SettingsRules.Clean(music, math.huge), nil, "infinity refused")
	expectEq(SettingsRules.Clean(music, "loud"), nil, "text refused")
	local camera = SettingsRules.Get("cameraSensitivity")
	expectEq(SettingsRules.Clean(camera, 1), 10, "camera sensitivity floor")
end)

test("toggles and choices accept only their own kinds", function()
	local names = SettingsRules.Get("showNames")
	expectEq(SettingsRules.Clean(names, false), false, "false is a value")
	expectEq(SettingsRules.Clean(names, "false"), nil, "a string is not a boolean")
	local quality = SettingsRules.Get("graphicsQuality")
	expectEq(SettingsRules.Clean(quality, "Low"), "Low", "a listed choice")
	expectEq(SettingsRules.Clean(quality, "Ultra"), nil, "an unlisted choice")
end)

test("applying changes keeps known, valid keys only", function()
	local choices = ProfileSchema.Default().choices
	local changed = SettingsRules.Apply(choices, {
		musicVolume = 10,
		invertCamera = true,
		graphicsQuality = "Ultra",
		hacked = 99999,
		uiScale = 1.2,
	})
	expectEq(changed, 3, "three settings changed")
	expectEq(choices.musicVolume, 10, "music saved")
	expectEq(choices.invertCamera, true, "invert saved")
	expectEq(choices.graphicsQuality, "High", "bad quality ignored")
	expectEq(choices.hacked, nil, "unknown key ignored")
	expectEq(choices.uiScale, 1.2, "scale saved")
	expectEq(SettingsRules.Apply(choices, "nope"), 0, "non-table ignored")
	expectEq(SettingsRules.Apply(choices, { musicVolume = 10 }), 0, "same value is no change")
end)

test("saved junk resolves to defaults", function()
	local values = SettingsRules.Resolve({ musicVolume = "x", showDamage = 1, graphicsQuality = "Potato" })
	expectEq(values.musicVolume, 75, "bad volume -> default")
	expectEq(values.showDamage, true, "bad toggle -> default")
	expectEq(values.graphicsQuality, "High", "bad quality -> default")
	expectEq(SettingsRules.Resolve(nil).effectsVolume, 80, "no choices at all")
end)

test("effect conversions", function()
	expectNear(SettingsRules.MouseSensitivity(50), 1, 1e-9, "50 is Roblox's own")
	expectNear(SettingsRules.MouseSensitivity(100), 2, 1e-9, "100 doubles")
	expectNear(SettingsRules.MouseSensitivity(10), 0.2, 1e-9, "10 is a fifth")
	expectNear(SettingsRules.Volume(80), 0.8, 1e-9, "volume percent")
	expectEq(SettingsRules.Graphics.Low.shadows, false, "low turns shadows off")
	expectEq(SettingsRules.Graphics.High.particles, 1, "high keeps every particle")
end)
