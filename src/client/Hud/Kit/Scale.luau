-- Screen scaling (ARCHITECTURE §1.1). Every surface is built in design px of the
-- 1672 × 941 mockups under one UIScale: Scale.Hud for edge-pinned HUD roots,
-- Scale.Window for modal windows, Scale.TopInset for the Roblox top bar.

local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local Tokens = require(script.Parent.Tokens)

local Scale = {}

-- How far the Roblox top bar reaches into `gui` (a ScreenGui), in screen px.
-- Absolute positions are measured from below the classic GUI inset, so a gui
-- that ignores the inset reports AbsolutePosition.Y = -inset.
function Scale.TopInset(gui: GuiBase2d): number
	local guiInset = GuiService:GetGuiInset().Y
	local bar = guiInset
	local ok, value = pcall(function()
		return GuiService.TopbarInset.Max.Y
	end)
	if ok and type(value) == "number" and value > 0 then
		bar = value
	end
	return math.max(0, bar - (gui.AbsolutePosition.Y + guiInset))
end

-- The top inset a window keeps clear of: the bar, never less than topInsetMin.
function Scale.WindowTop(gui: GuiBase2d): number
	return math.max(Scale.TopInset(gui), Tokens.Space("topInsetMin", 52))
end

-- True on a touch-only screen shorter than the phone height.
function Scale.IsSmallTouch(height: number): boolean
	return UserInputService.TouchEnabled
		and not UserInputService.KeyboardEnabled
		and height < Tokens.Scale("phoneHeight")
end

local function viewport(gui: GuiBase2d): Vector2
	local size = gui.AbsoluteSize
	if size.X <= 0 or size.Y <= 0 then
		local camera = workspace.CurrentCamera
		return if camera then camera.ViewportSize else Vector2.new(1672, 941)
	end
	return size
end

-- The HUD root's scale for a screen, and keeps it current. `root` is a frame
-- holding the HUD regions; it is sized to 1/scale of the screen so regions
-- pinned by Scale keep to the edges. opts.refW/refH override the canvas.
-- Returns a function that stops watching.
function Scale.Hud(gui: GuiBase2d, root: GuiObject, opts): () -> ()
	opts = opts or {}
	local ref = Tokens.Data.reference
	local uiScale = root:FindFirstChildWhichIsA("UIScale") or Instance.new("UIScale")
	uiScale.Parent = root
	local player = Players.LocalPlayer
	local function apply()
		local size = viewport(gui)
		local k = HudModel.HudScale(
			size.X,
			size.Y,
			opts.refW or ref.width,
			opts.refH or ref.height,
			Tokens.Scale("hudMin"),
			Tokens.Scale("hudMax"),
			player:GetAttribute("UiScale")
		)
		if Scale.IsSmallTouch(size.Y) then
			-- Phones: never below phoneHudMin, so HUD text stays readable; the
			-- regions are pinned to the screen edges and make room for it.
			k = math.max(k * Tokens.Scale("phoneHud"), Tokens.Scale("phoneHudMin"))
		end
		uiScale.Scale = k
		root.Size = UDim2.fromScale(1 / k, 1 / k)
	end
	local connections = {
		gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(apply),
		player:GetAttributeChangedSignal("UiScale"):Connect(apply),
	}
	apply()
	return function()
		for _, connection in connections do
			connection:Disconnect()
		end
	end
end

-- The scale and centre of a window w × h on a screen W × H whose top `top` px
-- belong to the Roblox top bar.
-- On a short touch screen (a landscape phone) a window takes the whole
-- screen height, over the top bar and the HUD, at the largest scale that fits,
-- so its text is as large as it can be.
function Scale.WindowFit(
	screenW: number,
	screenH: number,
	top: number,
	w: number,
	h: number,
	userScale: number?,
	smallTouch: boolean?
)
	local small = if smallTouch == nil then Scale.IsSmallTouch(screenH) else smallTouch
	local margin = Tokens.Space(if small then "phoneMargin" else "windowMargin", if small then 4 else 8)
	if small then
		top = 0
	end
	local ref = Tokens.Data.reference
	local k = KitModel.WindowScale(screenW, screenH, top, w, h, userScale, small, {
		margin = margin,
		refW = ref.width,
		refH = ref.height,
		minScale = Tokens.Scale("windowMin"),
		maxScale = Tokens.Scale("windowMax"),
	})
	-- Centred on the screen, its top edge kept below the top inset.
	local y = math.max(screenH / 2, top + margin + h * k / 2)
	return k, Vector2.new(screenW / 2, y)
end

-- Fits a Kit.Screen's window to its gui and keeps it fitted. Returns a function
-- that stops watching.
function Scale.Window(screen): () -> ()
	local gui = screen.gui
	local player = Players.LocalPlayer
	local function fit()
		local size = viewport(gui)
		local k, centre = Scale.WindowFit(
			size.X,
			size.Y,
			Scale.WindowTop(gui),
			screen.size[1],
			screen.size[2],
			player:GetAttribute("UiScale")
		)
		screen.scale.Scale = k
		screen.holder.Position = UDim2.fromOffset(centre.X, centre.Y)
	end
	local connections = {
		gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(fit),
		player:GetAttributeChangedSignal("UiScale"):Connect(function()
			task.defer(fit)
		end),
	}
	pcall(function()
		table.insert(connections, GuiService:GetPropertyChangedSignal("TopbarInset"):Connect(fit))
	end)
	fit()
	return function()
		for _, connection in connections do
			connection:Disconnect()
		end
	end
end

return Scale
