-- UI sounds: hover, click, open, close, error, success. Ids come from the
-- tokens' "sounds"; an empty id is silent (none are supplied yet, D14). Sounds
-- are pooled under SoundService with no SoundGroup, so PreferencesController
-- routes them to the Effects volume. Hover never plays on touch.

local SoundService = game:GetService("SoundService")

local Tokens = require(script.Parent.Tokens)

local Sound = {}

local pool: { [string]: Sound } = {}

function Sound.Play(key: string)
	local id = Tokens.Sound(key)
	if id == "" then
		return
	end
	local sound = pool[key]
	if sound == nil or sound.Parent == nil then
		sound = Instance.new("Sound")
		sound.Name = "KitSound_" .. key
		sound.SoundId = if string.find(id, "^rbxassetid://") then id else "rbxassetid://" .. id
		sound.Volume = 0.5
		sound.Parent = SoundService
		pool[key] = sound
	end
	sound.TimePosition = 0
	sound:Play()
end

return Sound
