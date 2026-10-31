-- Floating damage numbers (GDD §25 "Show Damage"): a hit's damage rises from where
-- it landed and fades. CombatController shows one for each hit the server confirms
-- while the player's ShowDamage setting is on. With reduced motion the number
-- stays put and only fades. Drawn in the kit's tokens: the display face
-- (Merriweather Heavy) in gold with an ink outline, so it reads against snow,
-- grass and night alike.

local TweenService = game:GetService("TweenService")

local Kit = require(script.Parent.Kit)

local DamageNumbers = {}

DamageNumbers.SECONDS = 0.9
DamageNumbers.RISE = 2.5 -- studs
-- At most this many on screen; the oldest goes first.
DamageNumbers.MAX = 12
-- Colour tokens for the number and its outline.
DamageNumbers.COLOR = "gold"
DamageNumbers.OUTLINE = "ink"

local live = {}

local function spread(): Vector3
	return Vector3.new((math.random() - 0.5) * 1.6, 2 + math.random() * 0.6, (math.random() - 0.5) * 1.6)
end

function DamageNumbers.Show(position: Vector3, amount: number)
	if amount <= 0 then
		return
	end
	local terrain = workspace:FindFirstChildOfClass("Terrain")
	if terrain == nil then
		return
	end
	while #live >= DamageNumbers.MAX do
		local oldest = table.remove(live, 1)
		oldest:Destroy()
	end
	local anchor = Instance.new("Attachment")
	anchor.Name = "DamageNumber"
	anchor.WorldPosition = position + spread()
	anchor.Parent = terrain
	local board = Instance.new("BillboardGui")
	board.Size = UDim2.fromOffset(120, 48)
	board.AlwaysOnTop = true
	board.LightInfluence = 0
	board.MaxDistance = 120
	board.Adornee = anchor
	board.Parent = anchor
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.Size = UDim2.fromScale(1, 1)
	label.Text = tostring(math.round(amount))
	label.TextScaled = true
	label.FontFace = Kit.Tokens.Font("display")
	label.TextColor3 = Kit.Tokens.Color(DamageNumbers.COLOR)
	label.TextStrokeColor3 = Kit.Tokens.Color(DamageNumbers.OUTLINE)
	label.TextStrokeTransparency = 0.1
	label.Parent = board
	table.insert(live, anchor)
	local steady = Kit.Motion.Reduced()
	local info = TweenInfo.new(DamageNumbers.SECONDS, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
	if not steady then
		TweenService:Create(board, info, { StudsOffsetWorldSpace = Vector3.new(0, DamageNumbers.RISE, 0) }):Play()
	end
	local fade = TweenService:Create(label, info, { TextTransparency = 1, TextStrokeTransparency = 1 })
	fade.Completed:Connect(function()
		local index = table.find(live, anchor)
		if index then
			table.remove(live, index)
		end
		anchor:Destroy()
	end)
	fade:Play()
end

return DamageNumbers
