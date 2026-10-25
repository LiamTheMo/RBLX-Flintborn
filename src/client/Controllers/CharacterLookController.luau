-- Makes sure every character's clothing textures and face actually load on this
-- client. Characters spawned with grey clothing and a blank face when those
-- image fetches failed, so each character's MeshPart textures and decals are
-- handed to SpriteLoader, which preloads them and retries failures. A texture
-- that changes later (OutfitService recolouring the shorts for a tribe) is
-- tracked again.

local Players = game:GetService("Players")

local SpriteLoader = require(script.Parent.Parent.Hud.SpriteLoader)

local CharacterLookController = {}

local PROPERTIES = { MeshPart = "TextureID", Decal = "Texture" }

local function track(instance: Instance)
	local property = PROPERTIES[instance.ClassName]
	if property == nil then
		return
	end
	local last = (instance :: any)[property]
	SpriteLoader.TrackProperty(instance, property)
	instance:GetPropertyChangedSignal(property):Connect(function()
		-- Only a new image counts: SpriteLoader's own retries clear and restore the
		-- same id, and tracking that again would retry forever.
		local current = (instance :: any)[property]
		if current ~= "" and current ~= last then
			last = current
			SpriteLoader.TrackProperty(instance, property)
		end
	end)
end

local function watchCharacter(character: Model)
	for _, descendant in character:GetDescendants() do
		track(descendant)
	end
	character.DescendantAdded:Connect(track)
end

local function watchPlayer(player: Player)
	player.CharacterAdded:Connect(watchCharacter)
	if player.Character then
		watchCharacter(player.Character)
	end
end

function CharacterLookController.Start()
	Players.PlayerAdded:Connect(watchPlayer)
	for _, player in Players:GetPlayers() do
		watchPlayer(player)
	end
end

return CharacterLookController
