-- Build mode (GDD §6.1, §3.2, §25.4, §60). The Build key (X by default; DPadRight) toggles it during a run.
-- Pick a piece from the palette and step its tier with ◀ ▶ (walls, floors, doors
-- and roofs come in every tier, Wood to Adamantine; furniture and stations in
-- one), with the cost shown against what you carry. Placement is free (§60): the
-- ghost stands wherever the aim ray lands (mouse on desktop; the last spot tapped
-- in the world, else the screen centre, on touch; the screen centre on a
-- controller), upright, with its base on that surface, and shows ✓/✕ with colour
-- and the reason. It turns in BuildRules.ROTATE_STEP (15°) steps: R (Shift+R
-- back; held, it keeps turning), RB / LB, or the palette's +15° / -15° buttons.
-- Near another piece it sticks to that piece's faces and edges when turned like it
-- (BuildRules.SnapToNeighbours); hold Ctrl, or switch Snap off in the palette, to
-- place freely. Click, RT or the Place button builds. No-build auras around
-- portals and totem radii are drawn while building, and hovering a structure
-- shows its HP, owner and decay timer. The server decides every placement; the
-- ghost's checks only preview them. World place only. The palette is a kit card
-- at the bottom centre: piece tabs, the tier stepper, Snap, the turn buttons and
-- Place, the cost and key caps with the player's own keys; the hover line is a
-- kit tooltip. With a gamepad the palette opens with the current piece selected
-- (the D-pad picks pieces, tiers, Snap, the turn buttons and Place); B leaves the
-- palette so the stick walks again, and B again goes back into it.

local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local BuildRules = require(ReplicatedStorage.Shared.Building.BuildRules)
local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local PlacementProbe = require(ReplicatedStorage.Shared.Building.PlacementProbe)
local Keybinds = require(ReplicatedStorage.Shared.Settings.Keybinds)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local StructureCatalog = require(ReplicatedStorage.Shared.Building.StructureCatalog)
local InventoryController = require(script.Parent.InventoryController)
local Kit = require(script.Parent.Parent.Hud.Kit)
local Theme = require(script.Parent.Parent.Ui.Theme)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

local BuildController = {}

local player = Players.LocalPlayer
local mouse = player:GetMouse()
local ui = {}
-- `yaw` is the turn the player chose; `placeYaw` and `base` what the ghost shows
-- (after any snap) and Place sends. `snap` is the palette's Snap switch.
local state = {
	active = false,
	piece = "Wall",
	tier = "Wood",
	yaw = 0,
	placeYaw = 0,
	snap = true,
	snapped = false,
	info = nil,
	valid = false,
	base = nil,
	rotateHold = nil,
	touchAim = nil,
}
local visuals = {}
local renderConnection = nil

local OK_COLOR = Color3.fromRGB(110, 220, 120)
local BAD_COLOR = Color3.fromRGB(230, 90, 80)

-- The palette in design px: piece tabs in rows of PIECES_PER_ROW, then the tier
-- row, then the cost and status lines. Controls are touch-sized.
BuildController.SIZE = { 852, 244 }
local PIECES_PER_ROW = 7
local PIECE_W, PIECE_H, PIECE_GAP = 112, 42, 4
-- Between the two rows of pieces: room for the touch pads (44 screen px).
local ROW_GAP = 8
local ROW_HEIGHT = 46
-- The tier row: ◀ tier ▶, then Snap, -15°, +15° and Place from the right edge.
local TIER_W = 190
local SNAP_W, TURN_W, PLACE_W = 156, 88, 136

local make = Theme.Make

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
			text = ('<font color="%s">%s</font>'):format(Kit.Tokens.Data.colors.short, text)
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
	local structures = workspace:FindFirstChild(PlacementProbe.FOLDER_NAME)
	for _, part in if structures then structures:GetChildren() else {} do
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
	-- Touch aims where the player last tapped the world (dragging turns the
	-- camera under it); a controller, and touch before the first tap, aim at the
	-- screen centre.
	if state.touchAim and Kit.Input.IsTouch() then
		local ray = camera:ScreenPointToRay(state.touchAim.X, state.touchAim.Y)
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
		text ..= "  · decays in " .. HudModel.FormatTimer(decayAt - workspace:GetServerTimeNow())
	end
	return text
end

-- The hover line: a kit tooltip over the palette, rebuilt only when it changes.
local function setHover(text: string)
	if text == ui.hoverText then
		return
	end
	ui.hoverText = text
	if ui.hover then
		ui.hover:Destroy()
		ui.hover = nil
	end
	if text ~= "" then
		local w, h = Kit.Tooltip.Measure(text)
		ui.hover = Kit.Tooltip.new(ui.holder, {
			name = "Hover",
			rect = { (BuildController.SIZE[1] - w) / 2, -h - 12, w, h },
			text = text,
			tail = "bottom",
		})
	end
end

-- The aim ray skips every character, the ghost and the zone discs.
local function aimParams(): RaycastParams
	local ignore = { ui.ghost, workspace.CurrentCamera }
	for _, other in Players:GetPlayers() do
		if other.Character then
			table.insert(ignore, other.Character)
		end
	end
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = ignore
	return params
end

-- Snapping is on unless the Snap switch is off or Ctrl is held.
local function snapping(): boolean
	local free = UserInputService:IsKeyDown(Enum.KeyCode.LeftControl)
		or UserInputService:IsKeyDown(Enum.KeyCode.RightControl)
	return state.snap and not free
end

local function rotate(direction: number)
	state.yaw = BuildRules.Turn(state.yaw, direction)
end

-- A held rotate input keeps turning after a short delay.
local function stepRotateHold()
	local hold = state.rotateHold
	if hold and os.clock() >= hold.nextAt then
		rotate(hold.direction)
		hold.nextAt = os.clock() + BuildRules.ROTATE_REPEAT
	end
end

-- What the server would refuse the ghost for, as a refusal code, or nil. The
-- ghost can check the pieces near it, the ground under it and the zones it knows;
-- world geometry and sight are left to the server, whose answer shows on Place.
local function problem(base: Vector3, yaw: number, size: Vector3, nearby, root: BasePart, cost): string?
	local half = BuildRules.HalfExtents(size, yaw)
	local localHalf = size / 2
	local center = base + Vector3.new(0, half.Y, 0)
	if not BuildRules.InWorld(base) then
		return "OutOfBounds"
	elseif (base - root.Position).Magnitude > BuildRules.REACH then
		return "TooFar"
	elseif BuildRules.OverlapsAura(center, localHalf, state.info and state.info.auras or {}, yaw) then
		return "NoBuildZone"
	end
	local box = { center = center, half = localHalf, yaw = yaw }
	for _, other in nearby do
		if BuildRules.BoxesOverlap(box, other) then
			return "Blocked"
		end
	end
	local unsupported = BuildRules.SupportVerdict(PlacementProbe.SupportSamples(base, localHalf, yaw))
	if unsupported then
		return unsupported
	end
	if not affordable(cost) then
		return "MissingMaterials"
	end
	return nil
end

local function update()
	stepRotateHold()
	local piece, tierStats = stats()
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if piece == nil or root == nil then
		return
	end
	local origin, direction = aimRay()
	local params = aimParams()
	local hit = workspace:Raycast(origin, direction * 200, params)
	setHover(describeHover(hit and hit.Instance))
	if hit == nil then
		ui.ghost.Transparency = 1
		state.base = nil
		return
	end
	-- The base sits flush on the surface aimed at. Aimed at a wall-like face, the
	-- piece stands just clear of it, on whatever is below; then it sticks to a
	-- neighbour.
	local size = piece.size
	local aimed = hit.Position
	local beside = BuildRules.OffsetFromFace(aimed, hit.Normal, size, state.yaw)
	if beside then
		local below = workspace:Raycast(beside, Vector3.new(0, -BuildRules.REACH * 2, 0), params)
		aimed = if below then below.Position else beside
	end
	local nearby = PlacementProbe.NearbyPieces(aimed, size.Magnitude / 2 + 12)
	for _, other in nearby do
		other.center = other.position
	end
	local base, yaw, snapped = aimed, state.yaw, false
	if snapping() then
		base, yaw, snapped = BuildRules.SnapToNeighbours(base, yaw, size, nearby)
	end
	local code = problem(base, yaw, size, nearby, root, tierStats.cost)
	local half = BuildRules.HalfExtents(size, yaw)
	state.base, state.placeYaw, state.snapped = base, yaw, snapped
	state.valid = code == nil
	ui.ghost.Size = size
	ui.ghost.CFrame = CFrame.new(base + Vector3.new(0, half.Y, 0)) * CFrame.Angles(0, math.rad(yaw), 0)
	ui.ghost.Transparency = 0.5
	ui.ghost.Color = if state.valid then OK_COLOR else BAD_COLOR
	ui.markOk.Visible = state.valid
	ui.markBad.Visible = not state.valid
	if code == "MissingMaterials" then
		ui.status:SetText(Reasons.Sentence(code))
	elseif code then
		ui.status:SetText("Can't build here: " .. Reasons.Text(code))
	else
		local name = (if BuildRules.IsTiered(state.piece) then currentTier() .. " " else "") .. state.piece
		ui.status:SetText(("Place %s  · %d°%s"):format(name, yaw, if snapped then "  · lined up" else ""))
	end
end

local function place()
	if not state.active or state.base == nil then
		return
	end
	local ok, success, reason = pcall(function()
		return Remotes.Get("Build"):InvokeServer(state.piece, currentTier(), state.base, state.placeYaw)
	end)
	if not ok or not success then
		ui.status:SetText("Can't build here: " .. Reasons.Text(if ok then reason else "RequestFailed"))
	elseif state.piece == "Totem" then
		drawZones()
	end
end

local function toggleSnap()
	state.snap = not state.snap
	ui.snap:SetLabel(if state.snap then "Snap: on" else "Snap: off")
end

local renderPalette
local refreshKeys
local selectPalette

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
	ui.pieces:Select(state.piece)
	local tiered = BuildRules.IsTiered(state.piece)
	local tier = currentTier()
	local _, tierStats = stats()
	ui.tierDown.root.Visible = tiered
	ui.tierUp.root.Visible = tiered
	if tiered then
		local tiers = BuildRules.TiersOf(state.piece)
		ui.tierLabel:SetText(("%s  %d/%d  · %d HP"):format(tier, table.find(tiers, tier) or 1, #tiers, tierStats.hp))
	else
		ui.tierLabel:SetText(("%s  · %d HP"):format(state.piece, tierStats.hp))
	end
	ui.cost:SetText("Cost: " .. costLine(tierStats.cost))
	refreshKeys()
end

-- Gamepad selection on the current piece's tab.
function selectPalette()
	local tab = ui.tabs[state.piece]
	if tab then
		GuiService.SelectedObject = tab.control.hit
	end
end

local function setActive(active: boolean)
	state.active = active
	ui.holder.Visible = active
	if not active then
		setHover("")
	end
	ui.ghost.Parent = if active then workspace.CurrentCamera else nil
	if renderConnection then
		renderConnection:Disconnect()
		renderConnection = nil
	end
	state.rotateHold = nil
	state.touchAim = nil
	if active then
		local ok, info = pcall(function()
			return Remotes.Get("BuildInfo"):InvokeServer()
		end)
		state.info = ok and info or nil
		drawZones()
		renderPalette()
		renderConnection = RunService.RenderStepped:Connect(update)
		-- Higher priority than attacking, so a click or RT places instead of swinging.
		ContextActionService:BindActionAtPriority("FlintbornPlace", function(_, inputState)
			if inputState == Enum.UserInputState.Begin then
				place()
			end
			return Enum.ContextActionResult.Sink
		end, false, Enum.ContextActionPriority.High.Value, Enum.UserInputType.MouseButton1, Enum.KeyCode.ButtonR2)
		-- R / RB turn one step, Shift+R / LB one step back; holding keeps turning.
		-- High, so the bumpers turn the piece instead of stepping the hotbar or dropping.
		Binds.Bind("Rotate", function(_, inputState, input)
			if inputState == Enum.UserInputState.Begin then
				local back = (input and input.KeyCode == Enum.KeyCode.ButtonL1)
					or UserInputService:IsKeyDown(Enum.KeyCode.LeftShift)
					or UserInputService:IsKeyDown(Enum.KeyCode.RightShift)
				local direction = if back then -1 else 1
				rotate(direction)
				state.rotateHold = { direction = direction, nextAt = os.clock() + BuildRules.ROTATE_REPEAT_DELAY }
			elseif inputState == Enum.UserInputState.End or inputState == Enum.UserInputState.Cancel then
				state.rotateHold = nil
			end
			return Enum.ContextActionResult.Sink
		end, { priority = Enum.ContextActionPriority.High.Value, extra = { Enum.KeyCode.ButtonL1 } })
		-- Gamepad: B steps out of the palette (the stick walks again) and back in.
		ContextActionService:BindActionAtPriority("FlintbornBuildPalette", function(_, inputState)
			if inputState ~= Enum.UserInputState.Begin then
				return Enum.ContextActionResult.Pass
			end
			local selected = GuiService.SelectedObject
			if selected and selected:IsDescendantOf(ui.holder) then
				GuiService.SelectedObject = nil
				return Enum.ContextActionResult.Sink
			elseif selected == nil then
				selectPalette()
				return Enum.ContextActionResult.Sink
			end
			return Enum.ContextActionResult.Pass
		end, false, Enum.ContextActionPriority.Medium.Value + 1, Enum.KeyCode.ButtonB)
		if Kit.Input.IsGamepad() then
			selectPalette()
		end
	else
		ContextActionService:UnbindAction("FlintbornPlace")
		ContextActionService:UnbindAction("FlintbornBuildPalette")
		Binds.Unbind("Rotate")
		clearVisuals()
		local selected = GuiService.SelectedObject
		if selected and selected:IsDescendantOf(ui.holder) then
			GuiService.SelectedObject = nil
		end
	end
end

-- The hint for a bind with the input in use: its key, its gamepad button's
-- name, or nil on touch (the palette's buttons do it there).
local function hint(action: string): string?
	local bind = Keybinds.Get(action)
	return Kit.Input.Hint(Binds.Label(action), bind and bind.gamepad[1])
end

-- Key caps for the player's own Rotate and Build keys, Ctrl for free placement
-- (or the gamepad buttons; none on touch), right-aligned on the status line; the
-- status takes the room left of them.
function refreshKeys()
	local rotateKey, buildKey = hint("Rotate"), hint("Build")
	local entries = {}
	if rotateKey and buildKey then
		if Kit.Input.IsGamepad() then
			table.insert(entries, { "LB / RB", "Rotate" })
		else
			table.insert(entries, { rotateKey, "Rotate" })
			table.insert(entries, { "Ctrl", "Free" })
		end
		table.insert(entries, { buildKey, "Close" })
	end
	local parts = {}
	for _, entry in entries do
		table.insert(parts, entry[1] .. "=" .. entry[2])
	end
	local signature = table.concat(parts, ";")
	if signature == ui.keySignature then
		return
	end
	ui.keySignature = signature
	if ui.keys then
		ui.keys:Destroy()
	end
	local w = BuildController.SIZE[1]
	local width = 460
	ui.keys = Kit.Core.Make("Frame", {
		Name = "Keys",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(w - 20 - width, 196),
		Size = UDim2.fromOffset(width, 34),
		ZIndex = 6,
	}, ui.card.root)
	local x = width
	for index = #entries, 1, -1 do
		local cap, label = entries[index][1], entries[index][2]
		local labelW = math.ceil(Kit.Text.Width(label, "rowLabel")) + 4
		x -= labelW
		Kit.Text.new(ui.keys, { name = "Label" .. index, rect = { x, 0, labelW, 34 }, text = label, role = "rowLabel" })
		local capW = Kit.KeyCap.Width(cap, 34)
		x -= capW + 8
		Kit.KeyCap.new(ui.keys, { name = "Key" .. index, rect = { x, 0, capW, 34 }, text = cap })
		x -= 18
	end
	if ui.status then
		-- Whatever the key caps leave, and never less than half the card.
		local used = width - x - 18 + 12
		ui.status.root.Size = UDim2.fromOffset(math.max(w - 44 - math.max(used, 0), w / 2), 34)
	end
end

local function build()
	local w, h = BuildController.SIZE[1], BuildController.SIZE[2]
	local gui = make("ScreenGui", {
		Name = "Build",
		ResetOnSpawn = false,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, player:WaitForChild("PlayerGui"))
	ui.holder = make("Frame", {
		Name = "Palette",
		AnchorPoint = Vector2.new(0.5, 1),
		BackgroundTransparency = 1,
		-- Above the world HUD's XP bar and hotbar.
		Position = UDim2.new(0.5, 0, 1, -182),
		Size = UDim2.fromOffset(w, h),
		Visible = false,
	}, gui)
	ui.holder.Parent = Theme.HudRoot(gui)
	ui.card = Kit.Panel.new(ui.holder, { name = "Card", rect = { 0, 0, w, h }, variant = "card" })
	-- Active panels swallow clicks, so a tap on the panel never places behind it.
	ui.card.root.Active = true
	local card = ui.card.root
	local tabs = {}
	for order, pieceId in StructureCatalog.ORDER do
		local column = (order - 1) % PIECES_PER_ROW
		local row = (order - 1) // PIECES_PER_ROW
		table.insert(
			tabs,
			Kit.Tab.new(card, {
				id = pieceId,
				name = pieceId,
				rect = { 20 + column * (PIECE_W + PIECE_GAP), 16 + row * (PIECE_H + ROW_GAP), PIECE_W, PIECE_H },
				label = pieceId,
				variant = "horizontal",
				textSize = 15,
				-- The whole tab for the label, so "Workbench" keeps 9 px on phones.
				labelX = 8,
				zIndex = 6,
			})
		)
	end
	ui.pieces = Kit.TabGroup.new(tabs, select)
	ui.tabs = {}
	for _, tab in tabs do
		ui.tabs[tab.id or tab.root.Name] = tab
	end
	-- Tier stepper: ◀ Copper 3/8 · 1000 HP ▶ (hidden arrows for one-tier pieces).
	local rowY = 16 + 2 * (PIECE_H + ROW_GAP) + 2
	ui.tierDown = Kit.IconButton.new(card, {
		name = "TierDown",
		rect = { 20, rowY, ROW_HEIGHT, ROW_HEIGHT },
		variant = "small",
		icon = "arrow_left",
		zIndex = 6,
		onPress = function()
			cycleTier(-1)
		end,
	})
	ui.tierLabel = Kit.Text.new(card, {
		name = "Tier",
		rect = { 20 + ROW_HEIGHT + 8, rowY, TIER_W, ROW_HEIGHT },
		text = "",
		role = "rowTitle",
		align = "Center",
		scaled = true,
		zIndex = 6,
	})
	ui.tierUp = Kit.IconButton.new(card, {
		name = "TierUp",
		rect = { 20 + ROW_HEIGHT + TIER_W + 16, rowY, ROW_HEIGHT, ROW_HEIGHT },
		variant = "small",
		icon = "arrow_right",
		zIndex = 6,
		onPress = function()
			cycleTier(1)
		end,
	})
	-- Touch and controller players build with buttons instead of keys: Snap,
	-- turn back and forward one step, Place (right to left from the card's edge).
	local placeX = w - 20 - PLACE_W
	local rotateX = placeX - 12 - TURN_W
	local backX = rotateX - 8 - TURN_W
	local snapX = backX - 12 - SNAP_W
	ui.snap = Kit.Button.new(card, {
		name = "Snap",
		rect = { snapX, rowY, SNAP_W, ROW_HEIGHT },
		label = if state.snap then "Snap: on" else "Snap: off",
		variant = "secondary",
		sizeClass = "s",
		zIndex = 6,
		onPress = toggleSnap,
	})
	Kit.Button.new(card, {
		name = "RotateBack",
		rect = { backX, rowY, TURN_W, ROW_HEIGHT },
		label = ("-%d°"):format(BuildRules.ROTATE_STEP),
		variant = "secondary",
		sizeClass = "s",
		zIndex = 6,
		onPress = function()
			rotate(-1)
		end,
	})
	Kit.Button.new(card, {
		name = "Rotate",
		rect = { rotateX, rowY, TURN_W, ROW_HEIGHT },
		label = ("+%d°"):format(BuildRules.ROTATE_STEP),
		variant = "secondary",
		sizeClass = "s",
		zIndex = 6,
		onPress = function()
			rotate(1)
		end,
	})
	Kit.Button.new(card, {
		name = "Place",
		rect = { placeX, rowY, PLACE_W, ROW_HEIGHT },
		label = "Place",
		icon = "build",
		sizeClass = "s",
		zIndex = 6,
		onPress = place,
	})
	ui.cost = Kit.Text.new(card, {
		name = "Cost",
		rect = { 22, rowY + ROW_HEIGHT + 10, w - 44, 26 },
		text = "",
		role = "rowLabel",
		rich = true,
		zIndex = 6,
	})
	ui.status = Kit.Text.new(card, {
		name = "Status",
		rect = { 22, 196, w - 400, 34 },
		text = "",
		role = "rowTitle",
		scaled = true,
		zIndex = 6,
	})
	refreshKeys()
	Binds.Changed:Connect(refreshKeys)
	Kit.Input.Watch(refreshKeys)
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
	-- The sheet-13 status icons: a green check or a red cross, with the words in
	-- the palette's status line.
	ui.markOk = Kit.Icon.new(billboard, { name = "Ok", rect = { 0, 0, 40, 40 }, icon = "check" }).root
	ui.markBad = Kit.Icon.new(billboard, { name = "Bad", rect = { 0, 0, 40, 40 }, icon = "cross" }).root
	ui.markBad.Visible = false
end

-- Opens or closes this panel (keys, and the HUD's menu tiles).
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
	-- Touch: a tap on the world (not on the palette or HUD) moves the aim there.
	UserInputService.TouchTapInWorld:Connect(function(position, processedByUI)
		if state.active and not processedByUI then
			state.touchAim = position
		end
	end)
end

return BuildController
