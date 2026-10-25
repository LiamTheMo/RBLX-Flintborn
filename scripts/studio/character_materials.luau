-- Gives the default character's clothing its full materials (colour, normal and
-- roughness maps). Open Cloud scripts may not set SurfaceAppearance maps, so the
-- install workflow (scripts/roblox_character.py) falls back to plain textures;
-- Studio's command bar may set them.
--
-- How to use, once per place (lobby, then world):
--   1. Open the place in Roblox Studio.
--   2. View > Command Bar, paste this whole file, press Enter.
--   3. File > Publish to Roblox.
-- Re-running the install workflow puts the plain textures back; run this again after.
-- Ids come from art/roblox/character/asset_ids.json.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local StarterPlayer = game:GetService("StarterPlayer")

local function id(number)
	return "rbxassetid://" .. number
end

local SHIRT = { color = id(80911389263141), normal = id(74408081888643), roughness = id(80813666016513) }
local PANTS_NORMAL = id(99709380102012)
local PANTS_ROUGHNESS = id(108890917477580)
local PANTS = {
	Earth = 87086532976734,
	Ember = 78956550150619,
	Clay = 119018456466978,
	Ochre = 76115572783005,
	Moss = 121859381630502,
	Tide = 120802799686016,
	River = 106352113188971,
	Dusk = 96867273982977,
	Ash = 133410290875643,
	Bone = 117437649833721,
}

local function appearance(name, color, normal, roughness)
	local look = Instance.new("SurfaceAppearance")
	look.Name = name
	look.ColorMap = color
	look.NormalMap = normal
	look.RoughnessMap = roughness
	return look
end

local function dress(part, look)
	for _, old in part:GetChildren() do
		if old:IsA("SurfaceAppearance") then
			old:Destroy()
		end
	end
	part.TextureID = ""
	look:Clone().Parent = part
end

-- The tribe looks OutfitService puts on the shorts.
local outfits = ReplicatedStorage:FindFirstChild("CharacterOutfits") or Instance.new("Folder")
outfits.Name = "CharacterOutfits"
outfits.Parent = ReplicatedStorage
for name, color in PANTS do
	local old = outfits:FindFirstChild("Pants_" .. name)
	if old then
		old:Destroy()
	end
	appearance("Pants_" .. name, id(color), PANTS_NORMAL, PANTS_ROUGHNESS).Parent = outfits
end

-- The character itself: the shirt, and the shorts in the default Earth.
local character = StarterPlayer:FindFirstChild("StarterCharacter")
assert(character, "StarterCharacter is missing: run the 'Upload and install the player character' workflow first")
dress(character.Shirt, appearance("Shirt", SHIRT.color, SHIRT.normal, SHIRT.roughness))
for _, name in { "PantsWaist", "PantsLeftLeg", "PantsRightLeg" } do
	dress(character[name], outfits.Pants_Earth)
end
print("Character materials set (shirt and 10 tribe pants). Publish the place to keep them.")
