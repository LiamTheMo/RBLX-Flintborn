-- Build mode (GDD §6.1, §3.2, §25.4). The Build key (X by default; DPadRight) toggles it during a run.
-- Pick a piece from the palette and step its tier with ◀ ▶ (walls, floors, doors
-- and roofs come in every tier, Wood to Adamantine; furniture and stations in
-- one), with the cost shown against what you carry. A ghost follows the aim point
-- (mouse on desktop, screen centre on touch and controller), snaps to the grid and
-- shows ✓/✕ with colour. R / L2 / the Rotate button turns it; click, R1 or the Place button
-- builds. No-build auras around portals and totem radii are drawn while building,
-- and hovering a structure shows its HP, owner and decay timer. The server decides
-- every placement. World place only.

local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local BuildRules = require(ReplicatedStorage.Shared.Building.BuildRules)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local StructureCatalog = require(ReplicatedStorage.Shared.Building.StructureCatalog)
local InventoryController = require(script.Parent.InventoryController)
local Theme = require(script.Parent.Parent.Ui.Theme)
local Binds = require(script.Parent.Parent.Ui.Binds)

local BuildController = {}

local player = Players.LocalPlayer
local mouse = player:GetMouse()
local ui = {}
local state = { active = false, piece = "Wall", tier = "Wood", steps = 0, info = nil, valid = false, base = nil }
local visuals = {}
local renderConnection = nil

local OK_COLOR = Color3.fromRGB(110, 220, 120)
-- Pieces sit in one row that scrolls sideways, so new pieces never push the
-- palette under the tier row; buttons are touch-sized.
local PIECE_WIDTH = 78
local ROW_HEIGHT = 40
local BAD_COLOR = Color3.fromRGB(230, 90, 80)
local SELECTED = Color3.fromRGB(110, 70, 30)
local UNSELECTED = Color3.fromRGB(46, 38, 30)

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

-- The tier the current piece is built in: the chosen ladder tier when the piece
-- comes in it (the choice survives picking a chest in between), else its only one.
local function currentTier(): string
	return BuildRules.TierFor(state.piece, state.tier) or "Wood"
end

local function stats()
	return StructureCatalog.Get(state.piece, currentTier())
end

local function affordable(cost): boolean
	for catalogId, quantity in cost do
		if InventoryController.Count(catalogId) < quantity then
			return false
		end
	end
	return true
end

-- "Iron Bar 3/8  Stone 4/4", with what is still missing in the warning colour.
local function costLine(cost): string
	local parts = {}
	for catalogId, quantity in cost do
		local def = ItemCatalog.Get(catalogId)
		local owned = InventoryController.Count(catalogId)
		local text = ("%s %d/%d"):format(def and def.name or catalogId, math.min(owned, quantity), quantity)
		if owned < quantity then
			text = ('<font color="#FFAA78">%s</font>'):format(text)
		end
		table.insert(parts, { key = catalogId, text = text })
	end
	table.sort(parts, function(a, b)
		return a.key < b.key
	end)
	local texts = {}
	for _, part in parts do
		table.insert(texts, part.text)
	end
	return table.concat(texts, "  ")
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
	if Theme.UsingMouse() then
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
	local pieceId = part:GetAttribute("Piece")
	-- Furniture and stations have one tier, so only tiered pieces name it.
	local tier = if BuildRules.IsTiered(pieceId) then (part:GetAttribute("Tier") or "") .. " " else ""
	local text = ("%s%s — %d/%d HP — %s"):format(
		tier,
		pieceId,
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
	ui.status.Text = reason
		or ("Place " .. (if BuildRules.IsTiered(state.piece) then currentTier() .. " " else "") .. state.piece)
end

local function place()
	if not state.active or state.base == nil then
		return
	end
	local ok, success, reason = pcall(function()
		return Remotes.Get("Build"):InvokeServer(state.piece, currentTier(), state.base, state.steps)
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
	renderPalette()
end

-- Steps the building tier up or down the ladder (walls, floors, doors, roofs).
local function cycleTier(delta: number)
	if BuildRules.IsTiered(state.piece) then
		state.tier = BuildRules.CycleTier(state.piece, currentTier(), delta) or state.tier
		renderPalette()
	end
end

function renderPalette()
	for pieceId, button in ui.pieceButtons do
		button.BackgroundColor3 = if pieceId == state.piece then SELECTED else UNSELECTED
	end
	local tiered = BuildRules.IsTiered(state.piece)
	local tier = currentTier()
	local _, tierStats = stats()
	ui.tierDown.Visible = tiered
	ui.tierUp.Visible = tiered
	if tiered then
		local tiers = BuildRules.TiersOf(state.piece)
		ui.tierLabel.Text = ("%s  %d/%d  · %d HP"):format(tier, table.find(tiers, tier) or 1, #tiers, tierStats.hp)
	else
		ui.tierLabel.Text = ("%s  · %d HP"):format(state.piece, tierStats.hp)
	end
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
		Binds.Bind("Rotate", function(_, inputState)
			if inputState == Enum.UserInputState.Begin then
				rotate()
			end
			return Enum.ContextActionResult.Sink
		end)
	else
		ContextActionService:UnbindAction("FlintbornPlace")
		Binds.Unbind("Rotate")
		clearVisuals()
	end
end

local function build()
	local gui = make("ScreenGui", { Name = "Build", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	ui.panel = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 1),
		Position = UDim2.new(0.5, 0, 1, -96),
		Size = UDim2.fromOffset(460, 156),
		BackgroundColor3 = Color3.fromRGB(24, 20, 17),
		BackgroundTransparency = 0.1,
		-- Active panels swallow clicks, so a tap on the panel never places behind it.
		Active = true,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.panel)
	ui.pieces = make("ScrollingFrame", {
		Position = UDim2.fromOffset(8, 8),
		Size = UDim2.new(1, -16, 0, ROW_HEIGHT + 6),
		BackgroundTransparency = 1,
		Active = true,
		ScrollingDirection = Enum.ScrollingDirection.X,
		AutomaticCanvasSize = Enum.AutomaticSize.X,
		CanvasSize = UDim2.new(),
		ScrollBarThickness = 4,
	}, ui.panel)
	make("UIListLayout", {
		FillDirection = Enum.FillDirection.Horizontal,
		Padding = UDim.new(0, 4),
		SortOrder = Enum.SortOrder.LayoutOrder,
	}, ui.pieces)
	ui.pieceButtons = {}
	for order, pieceId in StructureCatalog.ORDER do
		local b = make("TextButton", {
			Text = pieceId,
			Size = UDim2.fromOffset(PIECE_WIDTH, ROW_HEIGHT),
			LayoutOrder = order,
			BackgroundColor3 = UNSELECTED,
			TextColor3 = Color3.fromRGB(245, 236, 222),
			Font = Enum.Font.GothamMedium,
			TextSize = 12,
		}, ui.pieces)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
		b.Activated:Connect(function()
			select(pieceId)
		end)
		ui.pieceButtons[pieceId] = b
	end
	local function button(text: string, position: UDim2, width: number, onClick)
		local b = make("TextButton", {
			Text = text,
			Position = position,
			Size = UDim2.fromOffset(width, ROW_HEIGHT),
			BackgroundColor3 = SELECTED,
			TextColor3 = Color3.fromRGB(255, 240, 220),
			Font = Enum.Font.GothamBold,
			TextSize = 13,
		}, ui.panel)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
		b.Activated:Connect(onClick)
		return b
	end
	-- Tier stepper: ◀ Copper 3/8 · 1000 HP ▶ (hidden arrows for one-tier pieces).
	local rowY = ROW_HEIGHT + 18
	ui.tierDown = button("◀", UDim2.fromOffset(8, rowY), 44, function()
		cycleTier(-1)
	end)
	ui.tierLabel = make("TextLabel", {
		Position = UDim2.fromOffset(56, rowY),
		Size = UDim2.fromOffset(170, ROW_HEIGHT),
		BackgroundTransparency = 1,
		TextColor3 = Color3.fromRGB(255, 230, 190),
		Font = Enum.Font.GothamBold,
		TextSize = 13,
		TextTruncate = Enum.TextTruncate.AtEnd,
	}, ui.panel)
	ui.tierUp = button("▶", UDim2.fromOffset(230, rowY), 44, function()
		cycleTier(1)
	end)
	-- Touch and controller players build with buttons instead of precise dragging.
	button("Rotate", UDim2.new(1, -172, 0, rowY), 80, rotate)
	button("Place", UDim2.new(1, -88, 0, rowY), 80, place)
	ui.cost = make("TextLabel", {
		Position = UDim2.fromOffset(8, rowY + ROW_HEIGHT + 6),
		Size = UDim2.new(1, -16, 0, 20),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = Color3.fromRGB(230, 220, 200),
		Font = Enum.Font.Gotham,
		TextSize = 13,
		RichText = true,
		TextTruncate = Enum.TextTruncate.AtEnd,
	}, ui.panel)
	ui.status = make("TextLabel", {
		Position = UDim2.fromOffset(8, rowY + ROW_HEIGHT + 28),
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

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function BuildController.Toggle()
	local inRun = player:GetAttribute("SessionState") == "ActiveRun"
	setActive(inRun and not state.active)
end

function BuildController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	Binds.Bind("Build", function(_, inputState)
		if inputState == Enum.UserInputState.Begin then
			BuildController.Toggle()
		end
		return Enum.ContextActionResult.Pass
	end)
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
