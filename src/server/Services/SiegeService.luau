-- Siege items (GDD §6.3, §51; docs/ITEM_CATALOG.md §5; numbers in SiegeRules).
-- Fire Bomb: with one equipped, the attack input (CombatService.SiegeAttack) throws
-- it from the head on a slow arc (ProjectileService); the burst burns structures by
-- material, scorches other players under the usual PvP rules (never the thrower)
-- and singes creatures. Breaching Charge: set on an enemy wall or door the player
-- is looking at within reach (hotbar activation, or the attack input while it is
-- equipped); it shows an 8 s fuse and then deals one heavy blow to that piece only.
-- A set charge cannot be removed; it fizzles if its piece goes first or its placer
-- leaves the server. Every request is checked here: risk state, the item held and
-- consumed exactly once, cadence, the validated position, reach, sight and
-- safe/no-build zones. Structure damage goes through BuildingService.Hit, so
-- ownership, HP publishing, removal and its signals stay in one place. World only.

local CollectionService = game:GetService("CollectionService")
local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local BuildRules = require(ReplicatedStorage.Shared.Building.BuildRules)
local InventoryRules = require(ReplicatedStorage.Shared.Inventory.InventoryRules)
local MovementRules = require(ReplicatedStorage.Shared.Security.MovementRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local SiegeRules = require(ReplicatedStorage.Shared.Combat.SiegeRules)
local AntiExploitService = require(script.Parent.AntiExploitService)
local BuildingService = require(script.Parent.BuildingService)
local CombatService = require(script.Parent.CombatService)
local DownedService = require(script.Parent.DownedService)
local ExtractionService = require(script.Parent.ExtractionService)
local InventoryService = require(script.Parent.InventoryService)
local NpcService = require(script.Parent.NpcService)
local ProjectileService = require(script.Parent.ProjectileService)
local SafeZoneService = require(script.Parent.SafeZoneService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local SiegeService = {}

SiegeService.FOLDER_NAME = "SiegeCharges"
-- Folders holding creature bodies a burst can reach (NpcService.HitPart decides).
SiegeService.CREATURE_FOLDERS = { "EventEnemies", "Bosses", "GuardianArena" }
-- How often a fuse's countdown and light refresh.
SiegeService.FUSE_TICK = 0.25

local BOMB_STYLE = {
	name = "FireBomb",
	size = Vector3.new(0.9, 0.9, 0.9),
	ball = true,
	color = Color3.fromRGB(214, 96, 32),
	material = Enum.Material.Neon,
	gravityScale = SiegeRules.THROW_GRAVITY_SCALE,
	lifetime = SiegeRules.THROW_LIFETIME,
	stuckSeconds = 0,
}

local lastThrow = {}
local lastCharge = {}
-- Armed charges: {player, record, part, label, light, detonateAt}.
local charges = {}
local folder = nil

local function siegeFolder(): Folder
	if folder == nil or folder.Parent == nil then
		folder = Instance.new("Folder")
		folder.Name = SiegeService.FOLDER_NAME
		folder.Parent = workspace
	end
	return folder
end

local function characters()
	local list = {}
	for _, other in Players:GetPlayers() do
		if other.Character then
			table.insert(list, other.Character)
		end
	end
	return list
end

local function canAct(player: Player): boolean
	local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	return WorldAdmissionService.IsAtRisk(player)
		and humanoid ~= nil
		and humanoid.Health > 0
		and not DownedService.IsDowned(player)
end

local function validDirection(direction: any): Vector3?
	if typeof(direction) ~= "Vector3" or direction.Magnitude < 0.5 or direction.Magnitude ~= direction.Magnitude then
		return nil
	end
	return direction.Unit
end

-- True when nothing solid lies between `from` and `to`, other than `target`.
local function clearLine(from: Vector3, to: Vector3, ignore, target: Instance?): boolean
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = ignore
	params.RespectCanCollide = true
	params.IgnoreWater = true
	local hit = workspace:Raycast(from, to - from, params)
	return hit == nil or (target ~= nil and (hit.Instance == target or hit.Instance:IsDescendantOf(target)))
end

-- Portal auras and tagged no-build zones: nothing may be set there. (The Guardian
-- arena clears every structure inside it, so there is nothing to breach.)
local function noBuildAuras()
	local list = ExtractionService.Auras()
	for _, zone in CollectionService:GetTagged(BuildingService.NO_BUILD_TAG) do
		if zone:IsA("BasePart") then
			table.insert(list, { center = zone.Position, radius = zone:GetAttribute("Radius") or zone.Size.X / 2 })
		end
	end
	return list
end

-- Damages exactly `record` by `amount` through BuildingService.Hit: the hit starts
-- at the piece's own centre (no arc test) and only its part may be chosen. Hit
-- adds the held tool's match bonus, which SiegeRules.RawFor takes back out.
local function damageStructure(player: Player, record, amount: number): boolean
	local part = record.part
	if BuildingService.Get(part) ~= record then
		return false
	end
	local tool = InventoryService.EquippedTool(player)
	local raw = SiegeRules.RawFor(amount, tool and tool.kind, record.material)
	return BuildingService.Hit(player, record.position, Vector3.new(0, 0, 1), 0, raw, function(candidate)
		return candidate == part
	end)
end

-- A short expanding glow (bursts and blasts); never collides or blocks queries.
local function flash(center: Vector3, radius: number, color: Color3, seconds: number)
	local ball = Instance.new("Part")
	ball.Name = "SiegeFlash"
	ball.Shape = Enum.PartType.Ball
	ball.Anchored = true
	ball.CanCollide = false
	ball.CanQuery = false
	ball.CanTouch = false
	ball.Material = Enum.Material.Neon
	ball.Color = color
	ball.Transparency = 0.2
	ball.Size = Vector3.new(1, 1, 1)
	ball.CFrame = CFrame.new(center)
	ball.Parent = siegeFolder()
	TweenService:Create(ball, TweenInfo.new(seconds), { Size = Vector3.one * radius * 2, Transparency = 1 }):Play()
	Debris:AddItem(ball, seconds + 0.1)
end

-- Fire Bomb -------------------------------------------------------------------

local function burst(player: Player, result: RaycastResult, validated: Vector3?)
	local center = result.Position + result.Normal * 0.5
	flash(center, SiegeRules.BURST_RADIUS, Color3.fromRGB(255, 140, 40), 0.5)
	-- A thrower who left has nobody to credit; a burst out of range or inside a
	-- safe zone harms nothing.
	if player.Parent == nil or not SiegeRules.WithinRange(validated, center) or SafeZoneService.Contains(center) then
		return
	end
	local ignore = characters()
	local structures = workspace:FindFirstChild(BuildingService.FOLDER_NAME)
	if structures then
		local params = OverlapParams.new()
		params.FilterType = Enum.RaycastFilterType.Include
		params.FilterDescendantsInstances = { structures }
		for _, part in workspace:GetPartBoundsInRadius(center, SiegeRules.BURST_RADIUS, params) do
			local record = BuildingService.Get(part)
			if
				record
				and SiegeRules.InBurst(center, record.position, record.half)
				and clearLine(center, record.position, ignore, part)
			then
				damageStructure(player, record, SiegeRules.FireDamage(record.material))
			end
		end
	end
	for _, other in Players:GetPlayers() do
		local root = other ~= player and other.Character and other.Character:FindFirstChild("HumanoidRootPart")
		if
			root
			and (root.Position - center).Magnitude <= SiegeRules.BURST_RADIUS
			and clearLine(center, root.Position, ignore)
		then
			-- PvP, tribe, downed and safe-zone rules all apply (DamageRules.CanDamage).
			CombatService.ApplyHit(player, other, SiegeRules.BURST_PLAYER_DAMAGE)
		end
	end
	local creatureFolders = {}
	for _, name in SiegeService.CREATURE_FOLDERS do
		local container = workspace:FindFirstChild(name)
		if container then
			table.insert(creatureFolders, container)
		end
	end
	if #creatureFolders > 0 then
		local params = OverlapParams.new()
		params.FilterType = Enum.RaycastFilterType.Include
		params.FilterDescendantsInstances = creatureFolders
		for _, part in workspace:GetPartBoundsInRadius(center, SiegeRules.BURST_RADIUS, params) do
			if clearLine(center, part.Position, ignore, part) then
				NpcService.HitPart(part, SiegeRules.BURST_CREATURE_DAMAGE, player)
			end
		end
	end
end

local function refuse(player: Player, reason: string)
	-- Cooldown refusals stay quiet: holding the attack input would spam them.
	if reason ~= "TooSoon" then
		InventoryService.Notify(player, SiegeRules.Message(reason))
	end
end

-- Throws one Fire Bomb along `aim` (unit). Returns ok, reason.
local function throw(player: Player, aim: Vector3): (boolean, string?)
	local character = player.Character
	local head = character and character:FindFirstChild("Head")
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if head == nil or root == nil or not canAct(player) then
		return false, "NotInRun"
	end
	local held = InventoryService.Equipped(player)
	if held == nil or held.catalogId ~= SiegeRules.FIRE_BOMB then
		return false, "NotHeld"
	end
	if SafeZoneService.Contains(root.Position) then
		return false, "SafeZone"
	end
	-- Launched from the client-owned head, so it must be near the validated spot.
	local validated = AntiExploitService.ValidatedPosition(player)
	if not MovementRules.NearValidated(head.Position, validated, SiegeRules.VALIDATED_SLACK) then
		return false, "TooFar"
	end
	local now = os.clock()
	if not SiegeRules.ThrowReady(lastThrow[player], now) then
		return false, "TooSoon"
	end
	if not InventoryService.RemoveAll(player, { [SiegeRules.FIRE_BOMB] = 1 }) then
		return false, "NoItem"
	end
	lastThrow[player] = now
	ProjectileService.Fire(head.Position, SiegeRules.ThrowVelocity(aim), character, function(result)
		burst(player, result, validated)
	end, BOMB_STYLE)
	return true, nil
end

-- Breaching Charge ------------------------------------------------------------

local function removeCharge(charge)
	charges[charge] = nil
	charge.part:Destroy()
end

local function detonate(charge)
	local position = charge.part.Position
	removeCharge(charge)
	-- A charge whose placer left fizzles: there is nobody to credit the raid to.
	if charge.player.Parent == nil or BuildingService.Get(charge.record.part) ~= charge.record then
		return
	end
	local explosion = Instance.new("Explosion")
	explosion.Position = position
	explosion.BlastRadius = 4
	-- Visual only: the blow below is the charge's whole effect.
	explosion.BlastPressure = 0
	explosion.DestroyJointRadiusPercent = 0
	explosion.ExplosionType = Enum.ExplosionType.NoCraters
	explosion.Parent = siegeFolder()
	Debris:AddItem(explosion, 2)
	flash(position, 4, Color3.fromRGB(255, 190, 90), 0.4)
	damageStructure(charge.player, charge.record, SiegeRules.BreachDamage())
end

local function makeCharge(position: Vector3, normal: Vector3)
	local part = Instance.new("Part")
	part.Name = "BreachingCharge"
	part.Anchored = true
	part.CanCollide = false
	part.CanQuery = false
	part.CanTouch = false
	part.Size = Vector3.new(1.4, 1.4, 0.6)
	part.Color = Color3.fromRGB(120, 40, 30)
	part.Material = Enum.Material.SmoothPlastic
	local at = position + normal * 0.3
	part.CFrame = if math.abs(normal.Y) > 0.99 then CFrame.new(at) else CFrame.lookAt(at, at + normal)
	local fuse = Instance.new("Fire")
	fuse.Size = 1
	fuse.Heat = 2
	fuse.Parent = part
	local light = Instance.new("PointLight")
	light.Color = Color3.fromRGB(255, 70, 40)
	light.Range = 8
	light.Brightness = 2
	light.Parent = part
	local billboard = Instance.new("BillboardGui")
	billboard.Size = UDim2.fromOffset(60, 30)
	billboard.StudsOffset = Vector3.new(0, 1.6, 0)
	billboard.MaxDistance = 120
	billboard.AlwaysOnTop = true
	billboard.Parent = part
	local label = Instance.new("TextLabel")
	label.Size = UDim2.fromScale(1, 1)
	label.BackgroundTransparency = 1
	label.Font = Enum.Font.GothamBlack
	label.TextSize = 22
	label.TextColor3 = Color3.fromRGB(255, 120, 80)
	label.TextStrokeTransparency = 0.3
	label.Text = SiegeRules.FuseLabel(SiegeRules.FUSE_SECONDS)
	label.Parent = billboard
	part.Parent = siegeFolder()
	return part, label, light
end

local function arm(player: Player, record, position: Vector3, normal: Vector3)
	local part, label, light = makeCharge(position, normal)
	local charge = {
		player = player,
		record = record,
		part = part,
		label = label,
		light = light,
		detonateAt = os.clock() + SiegeRules.FUSE_SECONDS,
	}
	charges[charge] = true
	task.spawn(function()
		while charges[charge] do
			local remaining = charge.detonateAt - os.clock()
			if remaining <= 0 then
				detonate(charge)
				return
			end
			charge.label.Text = SiegeRules.FuseLabel(remaining)
			charge.light.Enabled = not charge.light.Enabled
			task.wait(math.min(SiegeService.FUSE_TICK, remaining))
		end
	end)
end

-- Sets a Breaching Charge on the wall or door along `aim` (unit) from the head.
-- The caller has checked that the player holds one. Returns ok, reason.
local function placeCharge(player: Player, aim: Vector3): (boolean, string?)
	local character = player.Character
	local head = character and character:FindFirstChild("Head")
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if head == nil or root == nil or not canAct(player) then
		return false, "NotInRun"
	end
	local validated = AntiExploitService.ValidatedPosition(player)
	if not MovementRules.NearValidated(head.Position, validated, SiegeRules.VALIDATED_SLACK) then
		return false, "TooFar"
	end
	local now = os.clock()
	if not SiegeRules.ChargeReady(lastCharge[player], now) then
		return false, "TooSoon"
	end
	-- What the player looks at: the first solid thing along the aim, from the head
	-- (so nothing can be set through a wall).
	local ignore = characters()
	table.insert(ignore, siegeFolder())
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = ignore
	params.RespectCanCollide = true
	params.IgnoreWater = true
	local hit = workspace:Raycast(head.Position, aim * (SiegeRules.CHARGE_REACH + 1), params)
	local record = hit and BuildingService.Get(hit.Instance)
	local target = record
		and {
			pieceId = record.pieceId,
			ownedByPlacer = BuildingService.IsOwnedBy(player, record),
			distance = (hit.Position - head.Position).Magnitude,
			validatedDistance = validated and (hit.Position - validated).Magnitude,
			inSafeZone = SafeZoneService.Contains(root.Position)
				or SafeZoneService.OverlapsBox(record.position, record.half),
			inNoBuildAura = BuildRules.OverlapsAura(record.position, record.half, noBuildAuras()),
		}
	local reason = SiegeRules.ChargeRefusal(target)
	if reason then
		return false, reason
	end
	if not InventoryService.RemoveAll(player, { [SiegeRules.BREACHING_CHARGE] = 1 }) then
		return false, "NoItem"
	end
	lastCharge[player] = now
	arm(player, record, hit.Position, hit.Normal)
	return true, nil
end

-- PlaceCharge remote: the Breaching Charge in hotbar slot `index`, aimed along `direction`.
local function placeFromHotbar(player: Player, index: any, direction: any)
	local size = InventoryRules.Size(InventoryRules.Hotbar) or 0
	if type(index) ~= "number" or index % 1 ~= 0 or index < 1 or index > size then
		return false, "BadRequest"
	end
	local aim = validDirection(direction)
	if aim == nil then
		return false, "BadRequest"
	end
	local inventory = InventoryService.Get(player)
	if inventory == nil then
		return false, "NotInRun"
	end
	local item = inventory[InventoryRules.Hotbar][index]
	if item == nil or item.catalogId ~= SiegeRules.BREACHING_CHARGE then
		return false, "NotHeld"
	end
	return placeCharge(player, aim)
end

-- The attack input with a siege item equipped (CombatService validated the aim).
local function siegeAttack(player: Player, aim: Vector3)
	local held = InventoryService.Equipped(player)
	local kind = SiegeRules.Kind(held and held.catalogId)
	local ok, reason
	if kind == "Thrown" then
		ok, reason = throw(player, aim)
	elseif kind == "Placed" then
		ok, reason = placeCharge(player, aim)
		if ok then
			InventoryService.Notify(player, SiegeRules.Message("ChargeSet"))
		end
	else
		return
	end
	if not ok then
		refuse(player, reason or "BadRequest")
	end
end

function SiegeService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	siegeFolder()
	CombatService.SiegeAttack = siegeAttack
	Remotes.Handle("PlaceCharge", placeFromHotbar)
	-- A charge whose piece is destroyed (or decays) first goes with it.
	BuildingService.Removing:Connect(function(record)
		for charge in charges do
			if charge.record == record then
				removeCharge(charge)
			end
		end
	end)
	Players.PlayerRemoving:Connect(function(player)
		lastThrow[player] = nil
		lastCharge[player] = nil
	end)
end

return SiegeService
