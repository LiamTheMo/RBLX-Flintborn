-- The default player character's look (art/blender/scripts/build_09_character.py):
-- the colours its shorts come in. Players outside a tribe (and everyone in the
-- lobby) wear Earth, the brown of the reference; each tribe wears one of the
-- other colours, picked from its public TribeId so every server agrees.
-- scripts/roblox_character.py installs one pants look per colour, named
-- "Pants_<Name>", in ReplicatedStorage.CharacterOutfits.

local CharacterLook = {}

CharacterLook.DEFAULT = "Earth"

-- In the order the art sheet shows them; Earth (the default) first.
CharacterLook.COLORS = {
	{ name = "Earth", hex = "#643E20" },
	{ name = "Ember", hex = "#9C3328" },
	{ name = "Clay", hex = "#B5602F" },
	{ name = "Ochre", hex = "#B98A2E" },
	{ name = "Moss", hex = "#4F6C2F" },
	{ name = "Tide", hex = "#2E7671" },
	{ name = "River", hex = "#2F5C90" },
	{ name = "Dusk", hex = "#5D3F79" },
	{ name = "Ash", hex = "#55575C" },
	{ name = "Bone", hex = "#D6CAB1" },
}

-- The shorts colour for a tribe: Earth without one, otherwise one of the other
-- colours chosen by a stable hash of the TribeId (djb2, kept under 2^32).
function CharacterLook.PantsFor(tribeId: string?): string
	if type(tribeId) ~= "string" or tribeId == "" then
		return CharacterLook.DEFAULT
	end
	local hash = 5381
	for index = 1, #tribeId do
		hash = (hash * 33 + string.byte(tribeId, index)) % 4294967296
	end
	local others = #CharacterLook.COLORS - 1
	return CharacterLook.COLORS[2 + hash % others].name
end

return CharacterLook
