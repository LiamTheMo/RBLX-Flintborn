-- Small lookups on players' characters that the server services share: the root
-- part, the humanoid, and the list of every character (what a ray ignores).

local Players = game:GetService("Players")

local Characters = {}

function Characters.RootOf(player: Player)
	local character = player.Character
	return character and character:FindFirstChild("HumanoidRootPart")
end

function Characters.HumanoidOf(player: Player): Humanoid?
	return player.Character and player.Character:FindFirstChildOfClass("Humanoid") or nil
end

-- The humanoid while it still has health, or nil.
function Characters.AliveHumanoid(player: Player): Humanoid?
	local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	return humanoid and humanoid.Health > 0 and humanoid or nil
end

-- Every player's character, then each instance of `extra`.
function Characters.All(extra: { Instance }?): { Instance }
	local list = {}
	for _, player in Players:GetPlayers() do
		if player.Character then
			table.insert(list, player.Character)
		end
	end
	for _, instance in extra or {} do
		table.insert(list, instance)
	end
	return list
end

return Characters
