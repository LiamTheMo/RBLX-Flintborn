-- Dresses every character in its tribe's shorts colour. Everyone spawns as the
-- default R6 character (StarterPlayer.StarterCharacter, installed by
-- scripts/roblox_character.py); its shorts are three pieces (PantsWaist,
-- PantsLeftLeg, PantsRightLeg). Each takes the look named "Pants_<Colour>" from
-- ReplicatedStorage.CharacterOutfits: a SurfaceAppearance to clone in, or a
-- texture id attribute. The colour follows the TribeId attribute (CharacterLook),
-- so joining or leaving a tribe recolours the shorts at once.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CharacterLook = require(ReplicatedStorage.Shared.Character.CharacterLook)

local OutfitService = {}

OutfitService.PANTS = { "PantsWaist", "PantsLeftLeg", "PantsRightLeg" }

local function look(name: string): Instance?
	local outfits = ReplicatedStorage:FindFirstChild("CharacterOutfits")
	return outfits and outfits:FindFirstChild("Pants_" .. name)
end

-- Puts the player's tribe colour on their character's shorts.
function OutfitService.Dress(player: Player)
	local character = player.Character
	if character == nil then
		return
	end
	local name = CharacterLook.PantsFor(player:GetAttribute("TribeId"))
	if character:GetAttribute("PantsColor") == name then
		return
	end
	local source = look(name)
	if source == nil then
		return -- the outfits are not installed in this place (yet)
	end
	for _, partName in OutfitService.PANTS do
		local part = character:FindFirstChild(partName)
		if part and part:IsA("MeshPart") then
			local old = part:FindFirstChildWhichIsA("SurfaceAppearance")
			if old then
				old:Destroy()
			end
			if source:IsA("SurfaceAppearance") then
				source:Clone().Parent = part
			else
				part.TextureID = source:GetAttribute("TextureId") or ""
			end
		end
	end
	character:SetAttribute("PantsColor", name)
end

local function watch(player: Player)
	player.CharacterAdded:Connect(function()
		OutfitService.Dress(player)
	end)
	player:GetAttributeChangedSignal("TribeId"):Connect(function()
		OutfitService.Dress(player)
	end)
	if player.Character then
		OutfitService.Dress(player)
	end
end

function OutfitService.Start()
	Players.PlayerAdded:Connect(watch)
	for _, player in Players:GetPlayers() do
		watch(player)
	end
end

return OutfitService
