-- Build mode (GDD §6.1, §3.2, §25.4). X (or DPadRight) toggles it during a run.
-- Pick a piece and tier from the palette; a ghost follows the aim point (mouse on
-- desktop, screen centre on touch and controller), snaps to the grid and shows ✓/✕
-- with colour. R / L2 / the Rotate button turns it; click, R1 or the Place button
-- builds. No-build auras around portals and totem radii are drawn while building,
-- and hovering a structure shows its HP, owner and decay timer. The server decides
-- every placement. World place only.

local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local BuildRules = require(ReplicatedStorage.Shared.Building.BuildRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local StructureCatalog = require(ReplicatedStorage.Shared.Building.StructureCatalog)
local InventoryController = require(script.Parent.InventoryController)

local BuildController = {}

local player = Players.LocalPlayer
local mouse = player:GetMouse()
local ui = {}
local state = { active = false, piece = "Wall", tier = "Wood", steps = 0, info = nil, valid = false, base = nil }
local visuals = {}
local renderConnection = nil

local OK_COLOR = Color3.fromRGB(110, 220, 120)
local BAD_COLOR = Color3.fromRGB(230, 90, 80)

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

local function stats()
	return StructureCatalog.Get(state.piece, state.tier)
end

local function affordable(cost): boolean
	for catalogId, quantity in cost do
		if InventoryController.Count(catalogId) < quantity then
			return false
		end
	end
	return true
end

local function costLine(cost): string
	local parts = {}
	for catalogId, quantity in cost do
		table.insert(parts, ("%s %d/%d"):format(catalogId, InventoryController.Count(catalogId), quantity))
	end
	table.sort(parts)
	return table.concat(parts, "  ")
end

local function clearVisuals()
	for _, part in visuals do
		part:Destroy()
	end
	table.clear(visuals)
end

local function disc(center: Vector3, radius: number, color: Color3)
	local part = make("Part", {
		Anchored = true,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
		Shape = Enum.PartType.Cylinder,
		Material = Enum.Material.ForceField,
		Color = color,
		Transparency = 0.4,
		Size = Vector3.new(0.3, radius * 2, radius * 2),
		CFrame = CFrame.new(center) * CFrame.Angles(0, 0, math.rad(90)),
	}, workspace.CurrentCamera)
	table.insert(visuals, part)
end

-- Draws the no-build auras and every totem's radius while building.
local function drawZones()
	clearVisuals()
	for _, aura in state.info and state.info.auras or {} do
		disc(aura.center, aura.radius, BAD_COLOR)
	end
	for _, part in workspace:GetChildren() do
		local radius = part:IsA("BasePart") and part:GetAttribute("TotemRadius")
		if radius then
			disc(part.Position - Vector3.new(0, part.Size.Y / 2, 0), radius, Color3.fromRGB(255, 200, 90))
		end
	end
end

local function aimRay()
	local camera = workspace.CurrentCamera
	if UserInputService.MouseEnabled and not UserInputService.TouchEnabled then
		local ray = camera:ScreenPointToRay(mouse.X, mouse.Y)
		return ray.Origin, ray.Direction
	end
	local viewport = camera.ViewportSize
	local ray = camera:ViewportPointToRay(viewport.X / 2, viewport.Y / 2)
	return ray.Origin, ray.Direction
end

local function describeHover(target: Instance?): string
	local part = target and target:IsA("BasePart") and target
	if not part or not part:GetAttribute("Piece") then
		return ""
	end
	local text = ("%s %s — %d/%d HP — %s"):format(
		part:GetAttribute("Tier") or "",
		part:GetAttribute("Piece"),
		part:GetAttribute("HP") or 0,
		part:GetAttribute("MaxHP") or 0,
		part:GetAttribute("Owner") or "unknown"
	)
	local level = part:GetAttribute("TotemLevel")
	if level then
		text ..= ("  · level %d, radius %d"):format(level, part:GetAttribute("TotemRadius") or 0)
	end
	local decayAt = part:GetAttribute("DecayAt")
	if decayAt then
		local left = math.max(0, math.floor(decayAt - workspace:GetServerTimeNow()))
		text ..= ("  · decays in %d:%02d"):format(left // 60, left % 60)
	end
	return text
end

local function update()
	local piece, tierStats = stats()
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if piece == nil or root == nil then
		return
	end
	local origin, direction = aimRay()
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { player.Character, ui.ghost, workspace.CurrentCamera }
	local hit = workspace:Raycast(origin, direction * 200, params)
	ui.hover.Text = describeHover(hit and hit.Instance)
	if hit == nil then
		ui.ghost.Transparency = 1
		state.base = nil
		return
	end
	local base = BuildRules.Snap(hit.Position)
	local half = BuildRules.HalfExtents(piece.size, state.steps)
	local center = base + Vector3.new(0, half.Y, 0)
	local reason = nil
	if (base - root.Position).Magnitude > BuildRules.REACH then
		reason = "Too far"
	elseif BuildRules.OverlapsAura(center, half, state.info and state.info.auras or {}) then
		reason = "Too close to an extraction portal"
	elseif not affordable(tierStats.cost) then
		reason = "Not enough materials"
	end
	state.base = base
	state.valid = reason == nil
	ui.ghost.Size = half * 2
	ui.ghost.CFrame = CFrame.new(center)
	ui.ghost.Transparency = 0.5
	ui.ghost.Color = if state.valid then OK_COLOR else BAD_COLOR
	ui.mark.Text = if state.valid then "✓" else "✕"
	ui.mark.TextColor3 = ui.ghost.Color
	ui.status.Text = reason or ("Place " .. state.piece)
end

local function place()
	if not state.active or state.base == nil then
		return
	end
	local ok, success, reason = pcall(function()
		return Remotes.Get("Build"):InvokeServer(state.piece, state.tier, state.base, state.steps)
	end)
	if not ok or not success then
		ui.status.Text = "Can't build here (" .. tostring(reason or success) .. ")"
	elseif state.piece == "Totem" then
		drawZones()
	end
end

local function rotate()
	state.steps = (state.steps + 1) % 4
end

local renderPalette

local function select(pieceId: string)
	state.piece = pieceId
	local piece = StructureCatalog.Pieces[pieceId]
	if piece.tiers[state.tier] == nil then
		state.tier = "Wood"
	end
	renderPalette()
end

function renderPalette()
	for _, child in ui.pieces:GetChildren() do
		if child:IsA("TextButton") then
			child:Destroy()
		end
	end
	for _, pieceId in StructureCatalog.ORDER do
		local b = make("TextButton", {
			Text = pieceId,
			Size = UDim2.fromOffset(78, 26),
			BackgroundColor3 = if pieceId == state.piece
				then Color3.fromRGB(110, 70, 30)
				else Color3.fromRGB(46, 38, 30),
			TextColor3 = Color3.fromRGB(245, 236, 222),
			Font = Enum.Font.GothamMedium,
			TextSize = 12,
		}, ui.pieces)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
		b.Activated:Connect(function()
			select(pieceId)
		end)
	end
	local piece = StructureCatalog.Pieces[state.piece]
	for _, tier in StructureCatalog.TIERS do
		local button = ui.tiers[tier]
		button.Visible = piece.tiers[tier] ~= nil
		button.BackgroundColor3 = if tier == state.tier then Color3.fromRGB(110, 70, 30) else Color3.fromRGB(46, 38, 30)
	end
	local _, tierStats = stats()
	ui.cost.Text = "Cost: " .. costLine(tierStats.cost)
end

local function setActive(active: boolean)
	state.active = active
	ui.panel.Visible = active
	ui.ghost.Parent = if active then workspace.CurrentCamera else nil
	if renderConnection then
		renderConnection:Disconnect()
		renderConnection = nil
	end
	if active then
		local ok, info = pcall(function()
			return Remotes.Get("BuildInfo"):InvokeServer()
		end)
		state.info = ok and info or nil
		drawZones()
		renderPalette()
		renderConnection = RunService.RenderStepped:Connect(update)
		-- Higher priority than attacking, so a click places instead of swinging.
		ContextActionService:BindActionAtPriority("FlintbornPlace", function(_, inputState)
			if inputState == Enum.UserInputState.Begin then
				place()
			end
			return Enum.ContextActionResult.Sink
		end, false, Enum.ContextActionPriority.High.Value, Enum.UserInputType.MouseButton1, Enum.KeyCode.ButtonR1)
		ContextActionService:BindAction("FlintbornRotate", function(_, inputState)
			if inputState == Enum.UserInputState.Begin then
				rotate()
			end
			return Enum.ContextActionResult.Sink
		end, false, Enum.KeyCode.R, Enum.KeyCode.ButtonL2)
	else
		ContextActionService:UnbindAction("FlintbornPlace")
		ContextActionService:UnbindAction("FlintbornRotate")
		clearVisuals()
	end
end

local function build()
	local gui = make("ScreenGui", { Name = "Build", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	ui.panel = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 1),
		Position = UDim2.new(0.5, 0, 1, -96),
		Size = UDim2.fromOffset(460, 150),
		BackgroundColor3 = Color3.fromRGB(24, 20, 17),
		BackgroundTransparency = 0.1,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.panel)
	ui.pieces = make("Frame", {
		Position = UDim2.fromOffset(8, 8),
		Size = UDim2.new(1, -16, 0, 56),
		BackgroundTransparency = 1,
	}, ui.panel)
	make("UIGridLayout", { CellSize = UDim2.fromOffset(78, 24), CellPadding = UDim2.fromOffset(4, 4) }, ui.pieces)
	ui.tiers = {}
	for index, tier in StructureCatalog.TIERS do
		local b = make("TextButton", {
			Text = tier,
			Position = UDim2.fromOffset(8 + (index - 1) * 72, 70),
			Size = UDim2.fromOffset(68, 24),
			TextColor3 = Color3.fromRGB(245, 236, 222),
			Font = Enum.Font.GothamBold,
			TextSize = 12,
		}, ui.panel)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
		b.Activated:Connect(function()
			state.tier = tier
			renderPalette()
		end)
		ui.tiers[tier] = b
	end
	local function action(text: string, x: number, onClick)
		local b = make("TextButton", {
			Text = text,
			AnchorPoint = Vector2.new(1, 0),
			Position = UDim2.new(1, x, 0, 70),
			Size = UDim2.fromOffset(80, 24),
			BackgroundColor3 = Color3.fromRGB(110, 70, 30),
			TextColor3 = Color3.fromRGB(255, 240, 220),
			Font = Enum.Font.GothamBold,
			TextSize = 12,
		}, ui.panel)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
		b.Activated:Connect(onClick)
	end
	-- Touch and controller players build with buttons instead of precise dragging.
	action("Place", -8, place)
	action("Rotate", -92, rotate)
	ui.cost = make("TextLabel", {
		Position = UDim2.fromOffset(8, 98),
		Size = UDim2.new(1, -16, 0, 20),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = Color3.fromRGB(230, 220, 200),
		Font = Enum.Font.Gotham,
		TextSize = 13,
	}, ui.panel)
	ui.status = make("TextLabel", {
		Position = UDim2.fromOffset(8, 120),
		Size = UDim2.new(1, -16, 0, 20),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = Color3.fromRGB(255, 214, 150),
		Font = Enum.Font.GothamBold,
		TextSize = 13,
	}, ui.panel)
	ui.hover = make("TextLabel", {
		AnchorPoint = Vector2.new(0.5, 1),
		Position = UDim2.new(0.5, 0, 0, -6),
		Size = UDim2.new(1, 0, 0, 20),
		BackgroundTransparency = 1,
		TextColor3 = Color3.fromRGB(240, 232, 220),
		TextStrokeTransparency = 0.4,
		Font = Enum.Font.GothamMedium,
		TextSize = 13,
	}, ui.panel)
	ui.ghost = make("Part", {
		Anchored = true,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
		Material = Enum.Material.SmoothPlastic,
		Transparency = 0.5,
	}, nil)
	local billboard = make("BillboardGui", {
		Size = UDim2.fromOffset(40, 40),
		AlwaysOnTop = true,
	}, ui.ghost)
	ui.mark = make("TextLabel", {
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBlack,
		TextSize = 30,
		TextStrokeTransparency = 0.3,
	}, billboard)
end

function BuildController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	ContextActionService:BindAction("FlintbornBuild", function(_, inputState)
		if inputState == Enum.UserInputState.Begin then
			local inRun = player:GetAttribute("SessionState") == "ActiveRun"
			setActive(inRun and not state.active)
		end
		return Enum.ContextActionResult.Pass
	end, false, Enum.KeyCode.X, Enum.KeyCode.DPadRight)
	player:GetAttributeChangedSignal("SessionState"):Connect(function()
		if state.active and player:GetAttribute("SessionState") ~= "ActiveRun" then
			setActive(false)
		end
	end)
	InventoryController.Changed:Connect(function()
		if state.active then
			renderPalette()
		end
	end)
end

return BuildController
