-- The island's safe camps (WorldBuildService): the SafeZone volume, the
-- boundary posts, tents, a fire pit, a trader's stall and the camp's sign.

local BuildKit = require(script.Parent.BuildKit)

local SafeCamp = {}

local block = BuildKit.block
local decor = BuildKit.decor
local groundAt = BuildKit.groundAt
local model = BuildKit.model
local part = BuildKit.part
local STONE = BuildKit.STONE
local DARK_STONE = BuildKit.DARK_STONE
local WOOD = BuildKit.WOOD

-- An open A-frame tent (two slanted cloth panels over a ridge pole) turned `yaw` degrees.
local TENT_PANEL = Vector3.new(6.4, 0.4, 9)

local function tent(parent, x: number, z: number, yaw: number, cloth: Color3)
	local frame = CFrame.new(groundAt(x, z)) * CFrame.Angles(0, math.rad(yaw), 0)
	for _, side in { -1, 1 } do
		block(
			parent,
			"Tent",
			frame * CFrame.new(side * 2.05, 2.45, 0) * CFrame.Angles(0, 0, math.rad(-side * 50)),
			TENT_PANEL,
			cloth,
			Enum.Material.Fabric
		)
	end
	block(parent, "TentPole", frame * CFrame.new(0, 4.95, 0), Vector3.new(0.5, 0.5, 10.4), WOOD, Enum.Material.Wood)
	decor(
		parent,
		"TentFloor",
		frame * CFrame.new(0, 0.15, 0),
		Vector3.new(8.4, 0.3, 9.4),
		Color3.fromRGB(110, 92, 70),
		Enum.Material.Fabric
	)
end

-- A ring of stones round three crossed logs and a glowing flame (lit: Neon + light).
local function firePit(parent, x: number, z: number)
	local at = groundAt(x, z)
	for index = 1, 8 do
		local angle = math.rad(index * 45)
		decor(
			parent,
			"FireStone",
			CFrame.new(at + Vector3.new(math.cos(angle) * 2.4, 0.4, math.sin(angle) * 2.4))
				* CFrame.Angles(0, -angle, 0),
			Vector3.new(1.2, 0.9, 1.6),
			if index % 2 == 0 then STONE else DARK_STONE,
			Enum.Material.Slate
		)
	end
	for index = 1, 3 do
		decor(
			parent,
			"FireLog",
			CFrame.new(at + Vector3.new(0, 0.5, 0)) * CFrame.Angles(0, math.rad(index * 60), math.rad(12)),
			Vector3.new(3.4, 0.7, 0.7),
			WOOD,
			Enum.Material.Wood
		)
	end
	local flame = decor(
		parent,
		"Flame",
		CFrame.new(at + Vector3.new(0, 1.6, 0)),
		Vector3.new(1.4, 2, 1.4),
		Color3.fromRGB(255, 150, 50),
		Enum.Material.Neon
	)
	local light = Instance.new("PointLight")
	light.Color = Color3.fromRGB(255, 160, 80)
	light.Range = 24
	light.Brightness = 1.5
	light.Parent = flame
end

-- A trader's stall: a counter under a red awning on four posts, with crates.
local function stall(parent, x: number, z: number, yaw: number)
	local frame = CFrame.new(groundAt(x, z)) * CFrame.Angles(0, math.rad(yaw), 0)
	block(parent, "Counter", frame * CFrame.new(0, 1.5, 0.8), Vector3.new(7, 3, 2), WOOD, Enum.Material.WoodPlanks)
	for _, post in { { -3.6, -2 }, { 3.6, -2 }, { -3.6, 2 }, { 3.6, 2 } } do
		block(
			parent,
			"StallPost",
			frame * CFrame.new(post[1], 3.6, post[2]),
			Vector3.new(0.5, 7.2, 0.5),
			WOOD,
			Enum.Material.Wood
		)
	end
	decor(
		parent,
		"Awning",
		frame * CFrame.new(0, 7.4, 0),
		Vector3.new(8.6, 0.4, 5.6),
		Color3.fromRGB(190, 60, 50),
		Enum.Material.Fabric
	)
	for index, crate in { { 5.6, 1.4 }, { 6.2, -1.2 } } do
		block(
			parent,
			"Crate",
			frame * CFrame.new(crate[1], 1.25, crate[2]) * CFrame.Angles(0, math.rad(index * 25), 0),
			Vector3.new(2.5, 2.5, 2.5),
			Color3.fromRGB(140, 104, 66),
			Enum.Material.WoodPlanks
		)
	end
end

local function safeCamp(entry)
	local center = groundAt(entry.x, entry.z)
	-- The server-side volume nobody can fight inside (SafeZoneService).
	local zone = part({
		Name = entry.name,
		Size = Vector3.new(entry.radius * 2, 40, entry.radius * 2),
		CFrame = CFrame.new(center + Vector3.new(0, 18, 0)),
		Transparency = 1,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
	}, { "SafeZone" })
	zone:SetAttribute("SafeName", entry.name)
	-- A colour-blind-safe boundary: alternating white and blue posts.
	for index = 1, 16 do
		local angle = math.rad(index * 22.5)
		local x, z = entry.x + math.cos(angle) * entry.radius, entry.z + math.sin(angle) * entry.radius
		part({
			Name = "CampPost",
			Size = Vector3.new(1.5, 8, 1.5),
			CFrame = CFrame.new(groundAt(x, z) + Vector3.new(0, 3, 0)),
			Color = if index % 2 == 0 then Color3.fromRGB(240, 240, 240) else Color3.fromRGB(40, 110, 220),
			Material = Enum.Material.SmoothPlastic,
		}, { "GeneratedStructure" })
	end
	-- A small camp: two tents, a fire pit and a trader's stall.
	local props = model(entry.name .. " Props")
	tent(props, entry.x - 12, entry.z - 8, 30, Color3.fromRGB(196, 170, 120))
	tent(props, entry.x - 10, entry.z + 11, 70, Color3.fromRGB(158, 98, 84))
	firePit(props, entry.x + 8, entry.z + 9)
	stall(props, entry.x + 12, entry.z - 9, -25)
	local sign = part({
		Name = "CampSign",
		Size = Vector3.new(1, 1, 1),
		CFrame = CFrame.new(center + Vector3.new(0, 14, 0)),
		Transparency = 1,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
	})
	local billboard = Instance.new("BillboardGui")
	billboard.Size = UDim2.fromOffset(220, 40)
	billboard.MaxDistance = 400
	billboard.Parent = sign
	local label = Instance.new("TextLabel")
	label.Size = UDim2.fromScale(1, 1)
	label.BackgroundTransparency = 1
	label.Text = "🛡 " .. entry.name .. " — safe camp"
	label.TextColor3 = Color3.fromRGB(220, 235, 255)
	label.TextStrokeTransparency = 0.2
	label.Font = Enum.Font.GothamBold
	label.TextSize = 16
	label.Parent = billboard
end

SafeCamp.Build = safeCamp

return SafeCamp
