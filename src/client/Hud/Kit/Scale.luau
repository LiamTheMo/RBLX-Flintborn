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
-- The device's form factor: "phone" (touch only, viewport shorter than
-- phoneHeight), "tablet" (touch only, short side under tabletShortSide) or
-- "desktop" (everything with a keyboard, consoles, big touch screens). Sizes
-- default to the current viewport.
function Scale.FormFactor(height: number?, width: number?): string
	if not UserInputService.TouchEnabled or UserInputService.KeyboardEnabled then
		return "desktop"
	end
	local camera = workspace.CurrentCamera
	local size = if camera then camera.ViewportSize else Vector2.new(1672, 941)
	local h = height or size.Y
	local w = width or size.X
	if h > 0 and h < Tokens.Scale("phoneHeight") then
		return "phone"
	end
	if math.min(w, h) > 0 and math.min(w, h) < Tokens.Scale("tabletShortSide") then
		return "tablet"
	end
	return "desktop"
end

-- True on touch-only phones and tablets: windows fill the screen there and
-- body text is boosted. (Before this round only phones counted.)
function Scale.IsSmallTouch(height: number?, width: number?): boolean
	return Scale.FormFactor(height, width) ~= "desktop"
end

-- On phones and tablets: the least design size (px) that draws at
-- phoneText.minPx screen px in a typical window (phoneText.refWindow) below
-- the top bar, so boosted body text never drops under that floor.
function Scale.PhoneTextFloor(): number
	local camera = workspace.CurrentCamera
	local size = if camera then camera.ViewportSize else Vector2.new(1672, 941)
	local spec = Tokens.Data.phoneText
	local k = Scale.WindowFit(size.X, size.Y, spec.topInset, spec.refWindow[1], spec.refWindow[2], nil, true)
	return spec.minPx / math.max(k, 0.05)
end

-- The one phone floor table (tokens "phoneFloor"): the least scale for "hud"
-- or "overlay" (toasts, tooltips, notice cards) on phones.
function Scale.PhoneFloor(kind: string): number
	return Tokens.Data.phoneFloor[kind] or Tokens.Data.phoneFloor.overlay
end

-- Fires (with the new form factor) when the viewport or the input devices
-- change it, so phone and tablet decisions are not frozen at build time.
local listeners: { [any]: boolean } = {}
local current: string? = nil
local watching = false
local function recheck()
	local now = Scale.FormFactor()
	if now ~= current then
		current = now
		for fn in table.clone(listeners) do
			task.spawn(fn, now)
		end
	end
end
function Scale.OnFormFactorChanged(fn: (string) -> ()): () -> ()
	if not watching then
		watching = true
		current = Scale.FormFactor()
		local camera = workspace.CurrentCamera
		if camera then
			camera:GetPropertyChangedSignal("ViewportSize"):Connect(recheck)
		end
		UserInputService:GetPropertyChangedSignal("TouchEnabled"):Connect(recheck)
		UserInputService:GetPropertyChangedSignal("KeyboardEnabled"):Connect(recheck)
		UserInputService.LastInputTypeChanged:Connect(recheck)
	end
	listeners[fn] = true
	return function()
		listeners[fn] = nil
	end
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
		if Scale.IsSmallTouch(size.Y, size.X) then
			-- Phones and touch tablets: never below the HUD phone floor, so HUD
			-- text stays readable; the regions are pinned to the screen edges.
			k = math.max(k * Tokens.Scale("phoneHud"), Scale.PhoneFloor("hud"))
		end
		uiScale.Scale = k
		root.Size = UDim2.fromScale(1 / k, 1 / k)
	end
	local connections = {
		gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(apply),
		player:GetAttributeChangedSignal("UiScale"):Connect(apply),
	}
	local stopForm = Scale.OnFormFactorChanged(apply)
	table.insert(connections, { Disconnect = stopForm })
	apply()
	return function()
		for _, connection in connections do
			connection:Disconnect()
		end
	end
end

-- Safe areas and screen edges (ARCHITECTURE D29) ------------------------------

-- Makes a HUD ScreenGui draw on the whole screen (ScreenInsets None, not
-- clipped to the device safe area), so its corner regions can reach the
-- screen's edges; the regions keep out of notches themselves (Scale.PinToEdge,
-- HudModel.EdgeGap). Windows keep DeviceSafeInsets (Kit.Screen).
function Scale.FullScreen(gui: ScreenGui)
	gui.IgnoreGuiInset = true
	pcall(function()
		gui.ScreenInsets = Enum.ScreenInsets.None
	end)
	pcall(function()
		(gui :: any).ClipToDeviceSafeArea = false
	end)
end

-- Two hidden probe guis, one on the whole screen and one inside the device
-- safe area: the difference of their rectangles is the safe area's insets.
local probes: { full: ScreenGui, safe: ScreenGui }? = nil
local function probe()
	if probes == nil then
		local player = Players.LocalPlayer
		local parent = player and player:FindFirstChildOfClass("PlayerGui")
		if parent == nil then
			return nil
		end
		local function make(name: string, insets: string): ScreenGui
			local gui = Instance.new("ScreenGui")
			gui.Name = name
			gui.ResetOnSpawn = false
			gui.IgnoreGuiInset = true
			pcall(function()
				gui.ScreenInsets = (Enum.ScreenInsets :: any)[insets]
			end)
			gui.Parent = parent
			return gui
		end
		probes = {
			full = make("FlintbornScreenProbe", "None"),
			safe = make("FlintbornSafeAreaProbe", "DeviceSafeInsets"),
		}
	end
	return probes
end

-- The device safe area's insets in screen px ({left, top, right, bottom}),
-- measured by the probes; all 0 until they are laid out and on screens
-- without cut-outs.
function Scale.SafeInsets()
	local p = probe()
	if p == nil then
		return HudModel.NO_INSETS
	end
	local fp, fs = p.full.AbsolutePosition, p.full.AbsoluteSize
	local sp, ss = p.safe.AbsolutePosition, p.safe.AbsoluteSize
	if fs.X <= 0 or fs.Y <= 0 or ss.X <= 0 or ss.Y <= 0 then
		return HudModel.NO_INSETS
	end
	return {
		left = math.max(0, sp.X - fp.X),
		top = math.max(0, sp.Y - fp.Y),
		right = math.max(0, fp.X + fs.X - (sp.X + ss.X)),
		bottom = math.max(0, fp.Y + fs.Y - (sp.Y + ss.Y)),
	}
end

-- Calls `fn` when the safe area changes (rotation, a resized window).
-- Returns a function that stops watching.
function Scale.OnSafeInsetsChanged(fn: () -> ()): () -> ()
	local p = probe()
	if p == nil then
		return function() end
	end
	local connections = {}
	for _, gui in { p.full, p.safe } do
		for _, property in { "AbsoluteSize", "AbsolutePosition" } do
			table.insert(connections, gui:GetPropertyChangedSignal(property):Connect(fn))
		end
	end
	return function()
		for _, connection in connections do
			connection:Disconnect()
		end
	end
end

-- The screen a HUD gui (Scale.FullScreen) draws on at HUD scale `k`: {width,
-- height (screen px), scale, touch, insets (Scale.SafeInsets)}; the input
-- HudModel.EdgeGap, HudModel.GearCorner and Scale.PinToEdge take.
function Scale.HudScreen(gui: GuiBase2d, k: number)
	local size = viewport(gui)
	return {
		width = size.X,
		height = size.Y,
		scale = k,
		touch = UserInputService.TouchEnabled,
		insets = Scale.SafeInsets(),
	}
end

-- Pins `object` (a region on a HUD root at the screen's scale) to the `side`
-- ("left" or "right") edge by the edge rule (HudModel.EdgeGap): the corner
-- margin while it lies in a corner band, else at least the safe inset. Only
-- its X changes; returns the gap in design px.
function Scale.PinToEdge(object: GuiObject, side: string, screen): number
	local k = math.max(screen.scale or 1, 0.01)
	local rootH = screen.height / k
	local pos, size, anchor = object.Position, object.Size, object.AnchorPoint
	local h = size.Y.Scale * rootH + size.Y.Offset
	local top = pos.Y.Scale * rootH + pos.Y.Offset - anchor.Y * h
	local insets = screen.insets or HudModel.NO_INSETS
	local gap =
		HudModel.EdgeGap(top * k, (top + h) * k, screen.height, if side == "left" then insets.left else insets.right, k)
	local w = size.X.Offset
	if side == "left" then
		object.Position = UDim2.new(0, gap + anchor.X * w, pos.Y.Scale, pos.Y.Offset)
	else
		object.Position = UDim2.new(1, -gap - (1 - anchor.X) * w, pos.Y.Scale, pos.Y.Offset)
	end
	return gap
end

-- The scale and centre of a window w × h on a screen W × H whose top `top` px
-- belong to the Roblox top bar.
-- On a touch phone or tablet a window takes all the room below the top bar
-- (over the HUD) at the largest scale that fits, so its text is as large as it
-- can be; it never draws under the Roblox top bar. A small window (a dialog)
-- draws at most scale.touchSmallMax × the scale of a typical window
-- (phoneText.refWindow) there, so it is not blown up (and blurred) to fill
-- the screen.
function Scale.WindowFit(
	screenW: number,
	screenH: number,
	top: number,
	w: number,
	h: number,
	userScale: number?,
	smallTouch: boolean?
)
	local small = if smallTouch == nil then Scale.IsSmallTouch(screenH, screenW) else smallTouch
	local margin = Tokens.Space(if small then "phoneMargin" else "windowMargin", if small then 4 else 8)
	local ref = Tokens.Data.reference
	local k = KitModel.WindowScale(screenW, screenH, top, w, h, userScale, small, {
		margin = margin,
		refW = ref.width,
		refH = ref.height,
		minScale = Tokens.Scale("windowMin"),
		maxScale = Tokens.Scale("windowMax"),
		-- Phones and tablets: small dialogs stay near the big windows' scale.
		touchRef = Tokens.Data.phoneText.refWindow,
		touchMax = Tokens.Scale("touchSmallMax"),
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
	table.insert(connections, { Disconnect = Scale.OnFormFactorChanged(fit) })
	fit()
	return function()
		for _, connection in connections do
			connection:Disconnect()
		end
	end
end

return Scale
