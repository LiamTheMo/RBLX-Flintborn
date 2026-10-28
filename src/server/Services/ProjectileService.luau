-- Server-simulated arrows (GDD §21.1, Q134): slow, visible, on a slight gravity arc.
-- Each step raycasts the travelled segment, so hits are decided on the server from
-- server state. The arrow part replicates as the visual. Thrown Fire Bombs fly the
-- same way with their own look and a heavier arc. World place only.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local WeaponCatalog = require(ReplicatedStorage.Shared.Combat.WeaponCatalog)

local ProjectileService = {}

ProjectileService.STUCK_SECONDS = 3

local arrows = {}
local folder = nil

local function arrowFolder()
	if folder == nil or folder.Parent == nil then
		folder = Instance.new("Folder")
		folder.Name = "Arrows"
		folder.Parent = workspace
	end
	return folder
end

-- Launches an arrow. `ignore` is the shooter's character; `onHit(result)` is called
-- once with the RaycastResult when it hits something. `style` (optional) overrides
-- the arrow's look and flight for other thrown things (the Fire Bomb): {name, size,
-- color, material, ball, gravityScale, lifetime, stuckSeconds}.
function ProjectileService.Fire(
	origin: Vector3,
	velocity: Vector3,
	ignore: Instance,
	onHit: (RaycastResult) -> (),
	style: { [string]: any }?
)
	style = style or {}
	local part = Instance.new("Part")
	part.Name = style.name or "Arrow"
	part.Anchored = true
	part.CanCollide = false
	part.CanQuery = false
	part.CanTouch = false
	if style.ball then
		part.Shape = Enum.PartType.Ball
	end
	part.Size = style.size or Vector3.new(0.2, 0.2, 2.5)
	part.Color = style.color or Color3.fromRGB(120, 90, 60)
	if style.material then
		part.Material = style.material
	end
	part.CFrame = CFrame.lookAt(origin, origin + velocity)
	part.Parent = arrowFolder()
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { ignore, arrowFolder() }
	table.insert(arrows, {
		part = part,
		position = origin,
		velocity = velocity,
		params = params,
		onHit = onHit,
		age = 0,
		gravityScale = style.gravityScale or WeaponCatalog.ARROW_GRAVITY_SCALE,
		lifetime = style.lifetime or WeaponCatalog.ARROW_LIFETIME,
		stuckSeconds = style.stuckSeconds or ProjectileService.STUCK_SECONDS,
	})
end

local function step(dt: number)
	for index = #arrows, 1, -1 do
		local arrow = arrows[index]
		local gravity = Vector3.new(0, -workspace.Gravity * arrow.gravityScale, 0)
		arrow.age += dt
		local displacement = arrow.velocity * dt + gravity * (0.5 * dt * dt)
		local result = workspace:Raycast(arrow.position, displacement, arrow.params)
		if result then
			table.remove(arrows, index)
			arrow.part.CFrame = CFrame.lookAt(result.Position, result.Position + arrow.velocity)
			task.delay(arrow.stuckSeconds, function()
				arrow.part:Destroy()
			end)
			local ok, err = pcall(arrow.onHit, result)
			if not ok then
				warn("[ProjectileService] Hit handler failed: " .. tostring(err))
			end
		elseif arrow.age >= arrow.lifetime then
			table.remove(arrows, index)
			arrow.part:Destroy()
		else
			arrow.position += displacement
			arrow.velocity += gravity * dt
			arrow.part.CFrame = CFrame.lookAt(arrow.position, arrow.position + arrow.velocity)
		end
	end
end

function ProjectileService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	RunService.Heartbeat:Connect(step)
end

return ProjectileService
