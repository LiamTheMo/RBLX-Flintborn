-- Spike traps (GDD §6.1). A trap hurts any at-risk player from another tribe who
-- steps on it, at most once per victim per cooldown, under the normal combat rules
-- (no damage in safe zones or to the trap owner's own tribe). Per-victim cooldowns
-- are dropped when the trap goes or the victim leaves. World place only.
--
-- Touches on a player's character are reported by that player's client, which can
-- suppress them, so the server also looks for anyone standing on each trap every
-- POLL_SECONDS, by where their character is and where it last validated it.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Characters = require(ReplicatedStorage.Shared.World.Characters)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local StructureCatalog = require(ReplicatedStorage.Shared.Building.StructureCatalog)
local AntiExploitService = require(script.Parent.AntiExploitService)
local BuildingService = require(script.Parent.BuildingService)
local CombatService = require(script.Parent.CombatService)

local TrapService = {}

TrapService.POLL_SECONDS = 0.2
-- How far round the trap's footprint, and how high above it, a standing
-- player's root counts as on it (the root sits about 3 studs up).
TrapService.EDGE = 1
TrapService.ROOT_HEIGHT = 4.5

-- record.id -> {Player -> last hit time}
local cooldowns = {}
-- record.id -> record, for every armed trap.
local armed = {}

local function hurt(record, victim: Player)
	local lastHit = cooldowns[record.id]
	if lastHit == nil or BuildingService.Get(record.part) == nil or BuildingService.IsOwnedBy(victim, record) then
		return
	end
	local at = os.clock()
	if lastHit[victim] and at - lastHit[victim] < StructureCatalog.TRAP_COOLDOWN then
		return
	end
	lastHit[victim] = at
	CombatService.ApplyEnvironmentHit(victim, StructureCatalog.TRAP_DAMAGE)
end

-- True when a root at `position` stands on the trap.
local function onTrap(part: BasePart, position: Vector3): boolean
	local point = part.CFrame:PointToObjectSpace(position)
	local half = part.Size / 2
	return math.abs(point.X) <= half.X + TrapService.EDGE
		and math.abs(point.Z) <= half.Z + TrapService.EDGE
		and point.Y >= -half.Y - TrapService.EDGE
		and point.Y <= half.Y + TrapService.ROOT_HEIGHT
end

local function poll()
	for _, record in armed do
		for _, player in Players:GetPlayers() do
			local root = Characters.RootOf(player)
			local validated = AntiExploitService.ValidatedPosition(player)
			if
				(root and onTrap(record.part, root.Position))
				or (validated and onTrap(record.part, validated))
			then
				hurt(record, player)
			end
		end
	end
end

local function arm(record)
	cooldowns[record.id] = {}
	armed[record.id] = record
	record.part.Touched:Connect(function(hit)
		local model = hit:FindFirstAncestorOfClass("Model")
		local victim = model and Players:GetPlayerFromCharacter(model)
		if victim then
			hurt(record, victim)
		end
	end)
end

function TrapService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	BuildingService.Placed:Connect(function(record)
		if record.pieceId == "Trap" then
			arm(record)
		end
	end)
	BuildingService.Removing:Connect(function(record)
		cooldowns[record.id] = nil
		armed[record.id] = nil
	end)
	Players.PlayerRemoving:Connect(function(player)
		for _, lastHit in cooldowns do
			lastHit[player] = nil
		end
	end)
	task.spawn(function()
		while true do
			task.wait(TrapService.POLL_SECONDS)
			poll()
		end
	end)
end

return TrapService
