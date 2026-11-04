-- Server half of Shared.Settings.SettingsRules: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SharedSettingsRules = require(ReplicatedStorage.Shared.Settings.SettingsRules)

local SettingsRules = table.clone(SharedSettingsRules)

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

return SettingsRules
