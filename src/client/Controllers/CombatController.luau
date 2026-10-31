-- Attack input (GDD §5.1, Q26, Q134): click, tap or right trigger. With a melee
-- weapon (or empty hands, or a tool) each press sends a swing toward the aim
-- point; with a bow the press starts a draw and release fires, and a longer draw
-- shoots farther (never harder). The server decides every hit. World place only.
-- The same swing chops trees, mines rocks and ores and gathers plants (GDD §4.1,
-- §53; HarvestRules): on desktop the node under the mouse, when in reach, gets a
-- prompt plaque (InteractionPrompt's look: a CLICK key cap, the action, the node
-- and its pickaxe gate, the gate in red while the held tool falls short) and an
-- outline in the kit's colours. Touch and gamepad aim along the camera with no
-- hover. A gather shows "+2 Wood" on the hit marker.
-- Swings are paced to the item's cooldown (the harvest cadence while a node is in
-- front, so no swing is wasted) and play the stock R6 tool slash; any held item
-- but a bow is held out with the R6 tool pose. Both play on the Animator the server
-- made, so everyone sees them.
-- On touch screens the attack is a Kit round button beside the jump button
-- (its touch pad comes from the Kit), showing an axe or pickaxe while one is held;
-- the hit marker is a Kit plaque and the bow draw a Kit bar, at the HUD's scale.
-- Clicks on the HUD never swing: Kit buttons and screens sink them before
-- ContextActionService sees them.

local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local HarvestRules = require(ReplicatedStorage.Shared.Resources.HarvestRules)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local NodeCatalog = require(ReplicatedStorage.Shared.Resources.NodeCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local SiegeRules = require(ReplicatedStorage.Shared.Combat.SiegeRules)
local WeaponCatalog = require(ReplicatedStorage.Shared.Combat.WeaponCatalog)
local DamageNumbers = require(script.Parent.Parent.Hud.DamageNumbers)
local InteractionPrompt = require(script.Parent.Parent.Hud.InteractionPrompt)
local Kit = require(script.Parent.Parent.Hud.Kit)
local Layout = require(script.Parent.Parent.Hud.Layout)
local Theme = require(script.Parent.Parent.Ui.Theme)

local CombatController = {}

-- The hit marker and draw bar, in design px from the screen centre.
CombatController.MARKER = { y = -70, w = 220, h = 46 }
CombatController.DRAW = { y = 48, w = 280, h = 36 }
-- The touch attack button when the HUD layout has no entry for it.
CombatController.ATTACK = { anchor = { 1, 1 }, pos = { 1, -300, 1, -60 }, size = { 130, 124 } }
-- Roblox's stock R6 tool animations: the slash, and the arm held out.
CombatController.SWING_ANIMATION = "rbxassetid://129967478"
CombatController.HOLD_ANIMATION = "rbxassetid://182393478"
-- The hover plaque's key cap for the mouse.
CombatController.CLICK_KEY = "CLICK"
-- How far the hover ray looks past the camera for a node.
CombatController.HOVER_RAY = 300

local player = Players.LocalPlayer
local mouse = player:GetMouse()
local sequence = 0
local drawStartedAt = nil
local lastSwingAt = nil
local bound = false
local ui = {}
local tracks = {}
local hover = {}

local function nextSequence(): number
	sequence += 1
	return sequence
end

local function equippedDef()
	local catalogId = player:GetAttribute("EquippedItem")
	return catalogId and ItemCatalog.Get(catalogId), catalogId
end

local function equippedProfile()
	local def, catalogId = equippedDef()
	return WeaponCatalog.For(def and def.family == ItemCatalog.Families.Weapon and catalogId or nil)
end

-- The held tool ({kind, tier}) or nil, as the server's NodeCatalog checks see it.
local function equippedTool()
	local def = equippedDef()
	return def and def.tool or nil
end

local function rootPart(): BasePart?
	local character = player.Character
	return character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
end

-- Aim from the head toward the mouse on desktop, or along the camera elsewhere.
local function aimDirection(): Vector3
	local head = player.Character and player.Character:FindFirstChild("Head")
	if head and Theme.UsingMouse() then
		local direction = mouse.Hit.Position - head.Position
		if direction.Magnitude > 0.5 then
			return direction.Unit
		end
	end
	return workspace.CurrentCamera.CFrame.LookVector
end

local function flash(text: string, colorKey: string)
	ui.markerText:SetText(text)
	ui.markerText:SetColor(colorKey)
	ui.marker.Visible = true
	task.delay(0.6, function()
		if ui.markerText.root.Text == text then
			ui.marker.Visible = false
		end
	end)
end

-- Nodes ------------------------------------------------------------------------

-- A node hitbox as a HarvestRules candidate.
local function candidate(part: BasePart)
	local frame = part.CFrame
	return {
		part = part,
		center = part.Position,
		half = HarvestRules.WorldHalf(frame.RightVector, frame.UpVector, frame.LookVector, part.Size),
		active = part:GetAttribute("Active") ~= false,
	}
end

-- True when a swing with `profile` along the aim would land on a node (the
-- server's pick, without line of sight), so the swing waits for the harvest cadence.
local function nodeInFront(profile): boolean
	local root = rootPart()
	if root == nil then
		return false
	end
	local params = OverlapParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { player.Character }
	local candidates = {}
	for _, part in workspace:GetPartBoundsInRadius(root.Position, NodeCatalog.HARVEST_RANGE, params) do
		if part:GetAttribute("NodeLabel") ~= nil then
			table.insert(candidates, candidate(part))
		end
	end
	if #candidates == 0 then
		return false
	end
	local aim = aimDirection()
	local flatAim = Vector3.new(aim.X, 0, aim.Z)
	return HarvestRules.Pick(root.Position, flatAim, HarvestRules.Reach(profile.reach), candidates) ~= nil
end

-- True when the held item swings (not a bow, not a siege item to throw).
local function swingsAtNodes(profile): boolean
	return profile.kind == "Melee" and SiegeRules.Kind(player:GetAttribute("EquippedItem")) == nil
end

local function hideHover()
	if hover.billboard then
		hover.billboard.Enabled = false
		hover.highlight.Enabled = false
	end
	hover.part = nil
end

local function buildHover()
	local billboard = Instance.new("BillboardGui")
	billboard.Name = "FlintbornNodeHover"
	billboard.AlwaysOnTop = true
	billboard.Enabled = false
	billboard.LightInfluence = 0
	billboard.ResetOnSpawn = false
	billboard.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	local content = Instance.new("Frame")
	content.Name = "Content"
	content.BackgroundTransparency = 1
	content.Parent = billboard
	local scale = Instance.new("UIScale")
	scale.Parent = content
	-- One outline at a time, in the kit's glow over a faint paper fill.
	local highlight = Instance.new("Highlight")
	highlight.Name = "FlintbornNodeOutline"
	highlight.Enabled = false
	highlight.DepthMode = Enum.HighlightDepthMode.Occluded
	highlight.FillColor = Kit.Tokens.Color("paper")
	highlight.FillTransparency = 0.85
	highlight.OutlineColor = Kit.Tokens.Color("glow")
	highlight.OutlineTransparency = 0
	highlight.Parent = workspace.CurrentCamera
	hover.billboard, hover.content, hover.scale, hover.highlight = billboard, content, scale, highlight
	billboard.Parent = player:WaitForChild("PlayerGui")
end

-- The node under the mouse, if the held item can reach it, with its candidate.
local function hoveredNode(profile, root: BasePart)
	local location = UserInputService:GetMouseLocation()
	local ray = workspace.CurrentCamera:ViewportPointToRay(location.X, location.Y)
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { player.Character }
	local result = workspace:Raycast(ray.Origin, ray.Direction * CombatController.HOVER_RAY, params)
	local part = result and result.Instance
	if part == nil or part:GetAttribute("NodeLabel") == nil or part:GetAttribute("Active") == false then
		return nil, nil
	end
	local node = candidate(part :: BasePart)
	if HarvestRules.SurfaceDistance(root.Position, node.center, node.half) > HarvestRules.Reach(profile.reach) then
		return nil, nil
	end
	return part, node
end

local function updateHover()
	local root = rootPart()
	local profile = equippedProfile()
	if not bound or root == nil or not Theme.UsingMouse() or not swingsAtNodes(profile) then
		hideHover()
		return
	end
	local part, node = hoveredNode(profile, root)
	if part == nil then
		hideHover()
		return
	end
	local nodeType = part:GetAttribute("NodeType")
	local action = part:GetAttribute("NodeAction") or "Gather"
	local label = part:GetAttribute("NodeLabel")
	local short = type(nodeType) == "string" and NodeCatalog.GateNotice(nodeType, equippedTool()) ~= nil
	local scale = ui.uiScale and ui.uiScale.Scale or 1
	local signature = table.concat({ action, tostring(label), tostring(short), tostring(scale) }, "|")
	if hover.part ~= part or hover.signature ~= signature then
		if hover.drawn then
			for _, drawnPart in hover.drawn.parts do
				drawnPart:Destroy()
			end
		end
		local drawn = InteractionPrompt.Draw(hover.content, {
			key = CombatController.CLICK_KEY,
			action = action,
			object = label,
		})
		-- The object line (after plaque, key and title) turns red below the gate.
		local object = drawn.parts[4]
		if short and object then
			object:SetColor("short")
		end
		hover.drawn, hover.part, hover.signature = drawn, part, signature
		hover.content.Size = UDim2.fromOffset(drawn.width, drawn.height)
		hover.scale.Scale = scale
		hover.billboard.Size = UDim2.fromOffset(drawn.width * scale, drawn.height * scale)
		hover.billboard.Adornee = part
		hover.highlight.Adornee = part:FindFirstChild(HarvestRules.LOOK_MODEL) or part
	end
	local height = HarvestRules.LabelHeight(node.center.Y, node.half.Y, root.Position.Y) - node.center.Y
	hover.billboard.StudsOffsetWorldSpace = Vector3.new(0, height, 0)
	hover.billboard.Enabled = true
	hover.highlight.Enabled = true
end

-- Animations ---------------------------------------------------------------------

local function refreshHold()
	local hold = tracks.hold
	if hold == nil then
		return
	end
	local holding = player:GetAttribute("EquippedItem") ~= nil and equippedProfile().kind ~= "Bow"
	if holding and not hold.IsPlaying then
		hold:Play(0.15)
	elseif not holding and hold.IsPlaying then
		hold:Stop(0.15)
	end
end

-- Loads the slash and hold on the server-made Animator: tracks played there on
-- the local character replicate to everyone (a client-made Animator would not).
local function loadTracks(character: Model)
	tracks = {}
	local humanoid = character:WaitForChild("Humanoid", 10)
	local animator = humanoid and humanoid:WaitForChild("Animator", 10)
	if animator == nil or character ~= player.Character then
		return
	end
	local function load(id: string, priority: Enum.AnimationPriority, looped: boolean): AnimationTrack?
		local animation = Instance.new("Animation")
		animation.AnimationId = id
		local ok, track = pcall(function()
			return (animator :: Animator):LoadAnimation(animation)
		end)
		if not ok then
			return nil
		end
		track.Priority = priority
		track.Looped = looped
		return track
	end
	tracks.slash = load(CombatController.SWING_ANIMATION, Enum.AnimationPriority.Action, false)
	tracks.hold = load(CombatController.HOLD_ANIMATION, Enum.AnimationPriority.Movement, true)
	refreshHold()
end

-- True when a swing may go now (paced to the item, or to the harvest cadence
-- while a node is in front); plays the slash.
local function swing(profile): boolean
	local now = os.clock()
	local interval = HarvestRules.SwingInterval(profile.cooldown, nodeInFront(profile))
	if lastSwingAt and now - lastSwingAt < interval then
		return false
	end
	lastSwingAt = now
	if tracks.slash then
		tracks.slash:Play(0.05)
	end
	return true
end

-- Input --------------------------------------------------------------------------

local function onAttack(_, inputState)
	local profile = equippedProfile()
	if profile.kind == "Bow" then
		if inputState == Enum.UserInputState.Begin then
			drawStartedAt = os.clock()
			ui.drawBar:Set(0, true)
			ui.draw.Visible = true
		elseif inputState == Enum.UserInputState.End and drawStartedAt then
			local held = os.clock() - drawStartedAt
			drawStartedAt = nil
			ui.draw.Visible = false
			Remotes.Get("Shoot"):FireServer(nextSequence(), held, aimDirection())
		end
	elseif inputState == Enum.UserInputState.Begin and swing(profile) then
		Remotes.Get("Attack"):FireServer(nextSequence(), aimDirection())
	end
	return Enum.ContextActionResult.Pass
end

local function bind(active: boolean)
	bound = active
	ui.attack.Visible = active and UserInputService.TouchEnabled
	if active then
		-- No Roblox touch button: touch players press the Kit button instead.
		-- ContextActionService only sees clicks the HUD did not sink.
		ContextActionService:BindAction(
			"FlintbornAttack",
			onAttack,
			false,
			Enum.UserInputType.MouseButton1,
			Enum.KeyCode.ButtonR2
		)
	else
		ContextActionService:UnbindAction("FlintbornAttack")
		drawStartedAt = nil
		ui.draw.Visible = false
		hideHover()
	end
end

-- A design-px region centred on the screen, `y` px below the centre.
local function centred(parent: Instance, name: string, spec): Frame
	local frame = Instance.new("Frame")
	frame.Name = name
	frame.BackgroundTransparency = 1
	frame.AnchorPoint = Vector2.new(0.5, 0.5)
	frame.Position = UDim2.new(0.5, 0, 0.5, spec.y)
	frame.Size = UDim2.fromOffset(spec.w, spec.h)
	frame.Visible = false
	frame.Parent = parent
	return frame
end

-- The touch attack button with `icon`; press starts the swing or the draw,
-- release fires a drawn bow.
local function makeAttackButton(icon: string)
	if ui.attackButton then
		ui.attackButton:Destroy()
	end
	ui.attackIcon = icon
	local cfg = ui.attackCfg
	ui.attackButton = Kit.IconButton.new(ui.attack, {
		name = "Button",
		rect = { 0, 0, cfg.size[1], cfg.size[2] },
		variant = "round",
		icon = icon,
	})
	local hit = ui.attackButton.control.hit
	local function isPress(input: InputObject): boolean
		return input.UserInputType == Enum.UserInputType.Touch or input.UserInputType == Enum.UserInputType.MouseButton1
	end
	hit.InputBegan:Connect(function(input)
		if isPress(input) then
			onAttack(nil, Enum.UserInputState.Begin)
		end
	end)
	hit.InputEnded:Connect(function(input)
		if isPress(input) then
			onAttack(nil, Enum.UserInputState.End)
		end
	end)
end

-- An axe or pickaxe shows on the touch button while one is held.
local function refreshAttackIcon()
	local tool = equippedTool()
	local icon = HarvestRules.AttackIcon(tool and tool.kind)
	if icon ~= ui.attackIcon then
		makeAttackButton(icon)
	end
end

local function build()
	local gui = Instance.new("ScreenGui")
	gui.Name = "Combat"
	gui.ResetOnSpawn = false
	gui.DisplayOrder = Kit.Tokens.Order("hud")
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.IgnoreGuiInset = true
	pcall(function()
		gui.ScreenInsets = Enum.ScreenInsets.DeviceSafeInsets
	end)
	local root = Instance.new("Frame")
	root.Name = "Root"
	root.BackgroundTransparency = 1
	root.Size = UDim2.fromScale(1, 1)
	root.Parent = gui

	local m = CombatController.MARKER
	ui.marker = centred(root, "HitMarker", m)
	Kit.Panel.new(ui.marker, { name = "Plaque", rect = { 0, 0, m.w, m.h }, variant = "plaque", pad = 0 })
	ui.markerText = Kit.Text.new(ui.marker, {
		name = "Text",
		rect = { 14, 0, m.w - 28, m.h },
		text = "",
		role = "hudName",
		align = "Center",
		scaled = true,
		zIndex = 8,
	})

	local d = CombatController.DRAW
	ui.draw = centred(root, "Draw", d)
	ui.drawBar =
		Kit.Bar.new(ui.draw, { name = "Range", rect = { 0, 0, d.w, d.h }, fill = "xp", frame = "well", text = "" })

	local layout = Layout.Get()
	ui.attackCfg = layout and layout.attack or CombatController.ATTACK
	ui.attack = Instance.new("Frame")
	ui.attack.Name = "Attack"
	ui.attack.BackgroundTransparency = 1
	ui.attack.Visible = false
	-- On phones the layout's phone position puts it right of the hotbar and
	-- left of the Roblox jump button.
	Layout.Place(ui.attack, ui.attackCfg)
	ui.attack.Parent = root
	refreshAttackIcon()
	gui.Parent = player:WaitForChild("PlayerGui")
	Kit.Scale.Hud(gui, root)
	-- The hover plaque follows the HUD's scale.
	ui.uiScale = root:FindFirstChildWhichIsA("UIScale")
	buildHover()
end

function CombatController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	-- With Show Damage off the markers still confirm a hit, without the number.
	Remotes.Get("CombatFeedback").OnClientEvent:Connect(function(kind, amount, hitPosition, catalogId)
		local numbers = player:GetAttribute("ShowDamage") ~= false
		if kind == "Hit" then
			flash(if numbers then "Hit " .. tostring(amount) else "Hit", "ink")
			if numbers and typeof(hitPosition) == "Vector3" and type(amount) == "number" then
				DamageNumbers.Show(hitPosition, amount)
			end
		elseif kind == "Hurt" then
			flash(if numbers then "Hurt -" .. tostring(amount) else "Hurt", "short")
		elseif kind == "Harvest" and type(amount) == "number" then
			-- The material itself lands on the ground; the marker names it.
			local item = ItemCatalog.Get(catalogId)
			flash(("+%d %s"):format(amount, item and item.name or tostring(catalogId)), "ink")
		end
	end)
	RunService.RenderStepped:Connect(function()
		if drawStartedAt then
			local t = math.clamp((os.clock() - drawStartedAt) / WeaponCatalog.FULL_DRAW_SECONDS, 0, 1)
			ui.drawBar:Set(t, true)
			ui.drawBar:SetText(("Range %d%%"):format(math.round(t * 100)))
		end
		updateHover()
	end)
	local function refresh()
		bind(player:GetAttribute("SessionState") == "ActiveRun")
	end
	player:GetAttributeChangedSignal("SessionState"):Connect(refresh)
	refresh()
	player:GetAttributeChangedSignal("EquippedItem"):Connect(function()
		refreshHold()
		refreshAttackIcon()
	end)
	player.CharacterAdded:Connect(function(character)
		loadTracks(character)
	end)
	if player.Character then
		task.spawn(loadTracks, player.Character)
	end
end

return CombatController
