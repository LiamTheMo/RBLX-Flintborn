-- Overhead health bars (docs/ui/HudScreen.md "Overhead health bars"): a small
-- kit bar over every other player's head while they are below full health, so
-- everyone sees who is hurt. Hidden at full health; a bar that heals back to
-- full stays a moment (OverheadHealthModel.LINGER_SECONDS) and fades out. A
-- downed player's bar shows their downed pool in the orange fill under a
-- "Downed" line. Your own character has none (the HUD's health row shows it;
-- OverheadHealthModel.SHOW_OWN), and the Show Health Bars setting turns them all
-- off. World place only.
--
-- Built on this client for every character from what already replicates
-- (Humanoid Health and MaxHealth, the Downed and DownedHealth player
-- attributes), redrawn from their change signals, never per frame. A bar is a
-- BillboardGui in PlayerGui adorned to the head: built the first time that
-- character is hurt, destroyed when the character goes or the player leaves.
-- It is drawn in screen px at the HUD's scale (so it reads at range and is
-- never huge up close), hidden by walls (AlwaysOnTop off) and past
-- MAX_DISTANCE. Roblox's own overhead health bar is turned off on every
-- character so there is one bar; the name tag stays Roblox's (Show Names).

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local OverheadHealthModel = require(ReplicatedStorage.Shared.UI.OverheadHealthModel)
local SettingsRules = require(ReplicatedStorage.Shared.Settings.SettingsRules)
local Kit = require(script.Parent.Kit)

local OverheadHealth = {}

OverheadHealth.FOLDER = "OverheadHealth"
-- Motion tokens for the fade in and out (the toasts' timings).
OverheadHealth.FADE_IN = "toastIn"
OverheadHealth.FADE_OUT = "toastOut"

local player = Players.LocalPlayer
local getScale: () -> number = function()
	return 1
end
local folder: Folder? = nil
-- Player -> entry.
local entries = {}

local function enabled(): boolean
	local setting = SettingsRules.Get("showHealthBars")
	if setting == nil then
		return true
	end
	local value = SettingsRules.Clean(setting, player:GetAttribute(setting.attribute))
	if value == nil then
		return setting.default
	end
	return value
end

local function host(): Folder
	if folder == nil or folder.Parent == nil then
		local made = Instance.new("Folder")
		made.Name = OverheadHealth.FOLDER
		made.Parent = player:WaitForChild("PlayerGui")
		folder = made
	end
	return folder :: Folder
end

-- The bar's look, drawn into `content` (a frame in design px) for `mode`
-- ("hurt" or "downed"). Returns {bar (Kit.Bar), label (Kit.Text), parts}: parts
-- are the faded parts at their resting transparency. The capture scenes call it.
function OverheadHealth.Draw(content: Instance, mode: string)
	local barRect, labelRect = OverheadHealthModel.Rects()
	local bar = Kit.Bar.new(content, {
		name = "Health",
		rect = barRect,
		fill = OverheadHealthModel.FILLS[mode] or "health",
		frame = "track",
		zIndex = 2,
	})
	local label = Kit.Text.new(content, {
		name = "Downed",
		rect = labelRect,
		text = OverheadHealthModel.DOWNED_TEXT,
		role = "hudSmall",
		textSize = OverheadHealthModel.LABEL_SIZE,
		color = "cream",
		outline = "ink",
		outlineThickness = 1.5,
		align = "Center",
		zIndex = 4,
	})
	label.root.Visible = mode == "downed"
	return { bar = bar, label = label, parts = Kit.Toast.FadeParts(content) }
end

local function fade(entry, show: boolean, onDone: (() -> ())?)
	local key = if show then OverheadHealth.FADE_IN else OverheadHealth.FADE_OUT
	local live = {}
	for _, part in entry.drawn.parts do
		if part.object.Parent then
			table.insert(live, part)
		end
	end
	if #live == 0 and onDone then
		onDone()
	end
	for index, part in live do
		-- Every part shares the timing; the last one's tween reports the end.
		local done = if index == #live then onDone else nil
		Kit.Motion.Play(part.object, key, { [part.prop] = if show then part.rest else 1 }, done)
	end
end

local function clearDrawn(entry)
	if entry.drawn then
		entry.drawn.bar:Destroy()
		entry.drawn.label:Destroy()
		entry.drawn = nil
	end
end

local function destroyBoard(entry)
	entry.token += 1
	clearDrawn(entry)
	if entry.board then
		entry.board:Destroy()
		entry.board = nil
		entry.content = nil
		entry.uiScale = nil
	end
	entry.shown = false
	entry.fading = false
	entry.look = nil
end

local function ensureBoard(entry)
	if entry.board and entry.board.Parent then
		return
	end
	-- A board lost with its folder is drawn again from scratch.
	clearDrawn(entry)
	if entry.board then
		entry.board:Destroy()
	end
	entry.look = nil
	local size = OverheadHealthModel.Size()
	local board = Instance.new("BillboardGui")
	board.Name = "OverheadHealth_" .. entry.player.UserId
	board.Adornee = entry.head
	board.AlwaysOnTop = false
	board.LightInfluence = 0
	board.MaxDistance = OverheadHealthModel.MAX_DISTANCE
	board.ResetOnSpawn = false
	board.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	-- The foot of the billboard sits on its anchor (half its height up).
	board.SizeOffset = Vector2.new(0, 0.5)
	board.StudsOffsetWorldSpace = Vector3.new(0, OverheadHealthModel.StudsOffset(entry.head.Size.Y), 0)
	board.Enabled = false
	local content = Instance.new("Frame")
	content.Name = "Content"
	content.BackgroundTransparency = 1
	content.Size = UDim2.fromOffset(size[1], size[2])
	content.Parent = board
	local uiScale = Instance.new("UIScale")
	uiScale.Parent = content
	board.Parent = host()
	entry.board = board
	entry.content = content
	entry.uiScale = uiScale
	entry.k = nil
end

-- Sizes the billboard for the HUD's current scale.
local function applyScale(entry)
	local k = OverheadHealthModel.Scale(getScale())
	if entry.k ~= k then
		entry.k = k
		local size = OverheadHealthModel.Size()
		entry.uiScale.Scale = k
		entry.board.Size = UDim2.fromOffset(math.ceil(size[1] * k), math.ceil(size[2] * k))
	end
end

local function update(entry)
	local humanoid = entry.humanoid
	if humanoid == nil or entry.head == nil then
		return
	end
	local downed = entry.player:GetAttribute("Downed") == true
	local mode = OverheadHealthModel.Mode({
		health = humanoid.Health,
		maxHealth = humanoid.MaxHealth,
		downed = downed,
		isLocal = entry.player == player,
		enabled = enabled(),
	})
	local plan = OverheadHealthModel.Plan(mode, entry.shown)
	if plan == "none" then
		return
	elseif plan == "hide" then
		entry.token += 1
		entry.shown = false
		entry.lingering = false
		entry.fading = false
		if entry.board then
			entry.board.Enabled = false
		end
		return
	end
	local fraction = OverheadHealthModel.Fraction(
		mode,
		humanoid.Health,
		humanoid.MaxHealth,
		entry.player:GetAttribute("DownedHealth")
	)
	if plan == "linger" then
		if entry.drawn then
			entry.drawn.bar:Set(fraction)
		end
		if not entry.lingering then
			entry.lingering = true
			entry.token += 1
			local token = entry.token
			task.delay(OverheadHealthModel.LINGER_SECONDS, function()
				if entry.token ~= token or entry.drawn == nil then
					return
				end
				entry.fading = true
				fade(entry, false, function()
					if entry.token == token and entry.board then
						entry.board.Enabled = false
						entry.shown = false
						entry.lingering = false
						entry.fading = false
					end
				end)
			end)
		end
		return
	end
	-- "show": cancel a linger or a fade, draw the look, set the value.
	ensureBoard(entry)
	applyScale(entry)
	local wasShown = entry.shown
	if entry.lingering then
		entry.lingering = false
		entry.token += 1
	end
	if entry.look ~= mode then
		clearDrawn(entry)
		entry.drawn = OverheadHealth.Draw(entry.content, mode)
		entry.look = mode
		wasShown = false
	end
	if wasShown and entry.board.Enabled then
		entry.drawn.bar:Set(fraction)
		if entry.fading then
			-- Back from a fade that had started.
			entry.fading = false
			fade(entry, true)
		end
	else
		entry.drawn.bar:Set(fraction, true)
		for _, part in entry.drawn.parts do
			Kit.Motion.Set(part.object, { [part.prop] = part.rest })
		end
		entry.board.Enabled = true
		entry.fading = false
	end
	entry.shown = true
end

local function forgetCharacter(entry)
	for _, connection in entry.characterConnections do
		connection:Disconnect()
	end
	table.clear(entry.characterConnections)
	destroyBoard(entry)
	entry.lingering = false
	entry.humanoid = nil
	entry.head = nil
	entry.character = nil
end

local function watchCharacter(entry, character: Model)
	forgetCharacter(entry)
	entry.character = character
	local humanoid = character:WaitForChild("Humanoid", 10)
	local head = character:WaitForChild("Head", 10)
	if entry.character ~= character or humanoid == nil or not humanoid:IsA("Humanoid") then
		return
	end
	if head == nil or not head:IsA("BasePart") then
		return
	end
	-- One bar per character: Roblox's own (shown when damaged) is turned off here.
	humanoid.HealthDisplayType = Enum.HumanoidHealthDisplayType.AlwaysOff
	entry.humanoid = humanoid
	entry.head = head
	local function refresh()
		update(entry)
	end
	table.insert(entry.characterConnections, humanoid.HealthChanged:Connect(refresh))
	table.insert(entry.characterConnections, humanoid:GetPropertyChangedSignal("MaxHealth"):Connect(refresh))
	-- A head swapped or removed (a reset outfit, a fall into the void).
	table.insert(
		entry.characterConnections,
		head.AncestryChanged:Connect(function()
			if not head:IsDescendantOf(character) then
				destroyBoard(entry)
				entry.head = nil
			end
		end)
	)
	update(entry)
end

local function watchPlayer(other: Player)
	if entries[other] then
		return
	end
	local entry = {
		player = other,
		character = nil,
		humanoid = nil,
		head = nil,
		board = nil,
		content = nil,
		uiScale = nil,
		drawn = nil,
		look = nil,
		k = nil,
		shown = false,
		lingering = false,
		fading = false,
		-- Bumped whenever a pending linger or fade must not finish.
		token = 0,
		characterConnections = {},
		connections = {},
	}
	entries[other] = entry
	local function refresh()
		update(entry)
	end
	table.insert(
		entry.connections,
		other.CharacterAdded:Connect(function(character)
			watchCharacter(entry, character)
		end)
	)
	table.insert(
		entry.connections,
		other.CharacterRemoving:Connect(function(character)
			if entry.character == character then
				forgetCharacter(entry)
			end
		end)
	)
	table.insert(entry.connections, other:GetAttributeChangedSignal("Downed"):Connect(refresh))
	table.insert(entry.connections, other:GetAttributeChangedSignal("DownedHealth"):Connect(refresh))
	if other.Character then
		task.spawn(watchCharacter, entry, other.Character)
	end
end

local function forgetPlayer(other: Player)
	local entry = entries[other]
	if entry == nil then
		return
	end
	entries[other] = nil
	forgetCharacter(entry)
	for _, connection in entry.connections do
		connection:Disconnect()
	end
	table.clear(entry.connections)
end

local function refreshAll()
	for _, entry in entries do
		update(entry)
	end
end

-- getScale() returns the HUD's current UI scale (HudController's), so the bars
-- follow the HUD and the UI Scale setting.
function OverheadHealth.Start(scaleOf: () -> number)
	getScale = scaleOf
	for _, other in Players:GetPlayers() do
		watchPlayer(other)
	end
	Players.PlayerAdded:Connect(watchPlayer)
	Players.PlayerRemoving:Connect(forgetPlayer)
	local setting = SettingsRules.Get("showHealthBars")
	if setting then
		player:GetAttributeChangedSignal(setting.attribute):Connect(refreshAll)
	end
end

return OverheadHealth
