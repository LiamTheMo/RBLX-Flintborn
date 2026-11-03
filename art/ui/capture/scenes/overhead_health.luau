-- Overhead health bars (docs/ui/HudScreen.md "Overhead health bars") as
-- OverheadHealth.Draw builds a billboard's content, over the lobby village
-- stand-in background (the harness draws no 3D world or BillboardGui, so each
-- sample is the billboard's frame at its screen size, its content at the
-- billboard's UIScale):
--   row 1 desktop (HUD scale 1): hurt 72 %, 35 %, 8 %; downed with half and a
--         sixth of the downed pool
--   row 2 phone (the HUD scale clamped to OverheadHealthModel.MIN_SCALE)
--   row 3 the desktop samples at 3x, to read the art
--
--   python3 art/ui/capture/capture.py overhead_health

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local W, H = 1672, 941
workspace.CurrentCamera.ViewportSize = Vector2.new(W, H)

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local OverheadHealthModel = require(ReplicatedStorage.Shared.UI.OverheadHealthModel)
local Kit = require(Client.Hud.Kit)
local OverheadHealth = require(Client.Hud.OverheadHealth)

local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end

local pool = GameConstants.DOWNED_HEALTH
local SAMPLES = {
	{ "hurt", 72, nil },
	{ "hurt", 35, nil },
	{ "hurt", 8, nil },
	{ "downed", 1, pool / 2 },
	{ "downed", 1, pool / 6 },
}

local gui, root = __screen(W, H)
local size = OverheadHealthModel.Size()

-- A billboard's frame at `k` with the content drawn as the game draws it.
local function billboard(x: number, y: number, k: number, sample)
	local holder = Instance.new("Frame")
	holder.Name = "Billboard"
	holder.BackgroundTransparency = 1
	holder.Position = UDim2.fromOffset(x, y)
	holder.Size = UDim2.fromOffset(math.ceil(size[1] * k), math.ceil(size[2] * k))
	holder.Parent = root
	local content = Instance.new("Frame")
	content.Name = "Content"
	content.BackgroundTransparency = 1
	content.Size = UDim2.fromOffset(size[1], size[2])
	content.Parent = holder
	local uiScale = Instance.new("UIScale")
	uiScale.Scale = k
	uiScale.Parent = content
	local mode, health, downedHealth = sample[1], sample[2], sample[3]
	local drawn = OverheadHealth.Draw(content, mode)
	local fraction = OverheadHealthModel.Fraction(mode, health, 100, downedHealth)
	drawn.bar:Set(fraction, true)
	return drawn, fraction
end

local function caption(y: number, text: string)
	Kit.Text.new(root, {
		name = "Caption",
		rect = { 60, y, 900, 26 },
		text = text,
		role = "rowTitle",
		outline = true,
		outlineThickness = 2,
		zIndex = 6,
	})
end

local rows = {
	{ y = 150, k = OverheadHealthModel.Scale(1), pitch = 280, label = "Desktop (HUD scale 1)" },
	{
		y = 320,
		k = OverheadHealthModel.Scale(0.42),
		pitch = 280,
		label = ("Phone (HUD scale 0.42, drawn at %.2f)"):format(OverheadHealthModel.Scale(0.42)),
	},
	{ y = 500, k = 3, pitch = 310, label = "Desktop at 3x" },
}
for _, row in rows do
	caption(row.y - 50, row.label)
	for index, sample in SAMPLES do
		local drawn, fraction = billboard(60 + (index - 1) * row.pitch, row.y, row.k, sample)
		local mode = sample[1]
		local fill = if mode == "downed" then "bar.fill.orange" else "bar.fill.red"
		local tag = ("%s %d (x%.2f)"):format(mode, index, row.k)
		check(drawn.bar.root:GetAttribute("KitRole") == fill, tag .. " draws " .. fill)
		check(
			math.abs((drawn.bar.root:GetAttribute("KitValue") or -1) - fraction) < 1e-6,
			("%s at %.2f"):format(tag, fraction)
		)
		check(drawn.label.root.Visible == (mode == "downed"), tag .. " Downed line only when downed")
		check(#drawn.parts > 0, tag .. " has parts to fade")
	end
end

__dump(root, W, H, { background = "art/reference/lobby_map.png" })
print(__failed and "SCENE FAILED" or "SCENE OK")
if __failed then
	error("overhead_health failed")
end
