-- Who may act on the world right now: the guards the building, drop, farming,
-- siege, cache, meteor and ritual services share. No Init/Start; a plain module
-- the Loader also loads.

local AntiExploitService = require(script.Parent.AntiExploitService)
local DownedService = require(script.Parent.DownedService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local InteractionService = {}

-- Extra slack for the last server-validated position, which lags a sample behind.
InteractionService.VALIDATED_SLACK = 8

-- True for a living, at-risk, non-downed player.
function InteractionService.CanAct(player: Player): boolean
	local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	return WorldAdmissionService.IsAtRisk(player)
		and humanoid ~= nil
		and humanoid.Health > 0
		and not DownedService.IsDowned(player)
end

-- True for a living, at-risk, non-downed player within `reach` of `part`, both
-- where their character is and where the server last validated it (a teleport
-- cannot hold a channel).
function InteractionService.CanInteract(player: Player, part: BasePart, reach: number): boolean
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if root == nil or humanoid == nil or humanoid.Health <= 0 then
		return false
	end
	if not WorldAdmissionService.IsAtRisk(player) or DownedService.IsDowned(player) then
		return false
	end
	if part.Parent == nil or (root.Position - part.Position).Magnitude > reach then
		return false
	end
	local validated = AntiExploitService.ValidatedPosition(player)
	return validated == nil or (validated - part.Position).Magnitude <= reach + InteractionService.VALIDATED_SLACK
end

return InteractionService
