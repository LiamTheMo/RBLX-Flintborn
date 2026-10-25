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
-- The ids below come from art/roblox/character/asset_ids.json (regenerate with
-- python scripts/roblox_character.py --studio-script after an upload).

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local StarterPlayer = game:GetService("StarterPlayer")

local function id(number)
	return "rbxassetid://" .. number
end

-- BEGIN IDS
-- END IDS

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
