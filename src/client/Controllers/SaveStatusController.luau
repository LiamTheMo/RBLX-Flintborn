-- Small persistent indicator of the player's profile save state, driven by the
-- SaveStatus attribute the server sets: a kit status tag (a dot and words, never
-- colour alone). Desktop: at the bottom right. Phones and touch tablets: the
-- bottom right is the Roblox jump button's (and the left the thumbstick's), so
-- the tag sits in the free part of the Roblox top bar (GuiService.TopbarInset),
-- at its right end.

local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")

local Kit = require(script.Parent.Parent.Hud.Kit)
local Theme = require(script.Parent.Parent.Ui.Theme)

local SaveStatusController = {}

local STATUS_ATTRIBUTE = "SaveStatus"
local HEIGHT = 34

local LABELS = {
	Loading = "Loading data…",
	Saved = "Saved",
	Saving = "Saving…",
	Pending = "Save pending",
	LeaseLost = "Data in use on another server",
	Error = "Data error",
}

-- The green dot only when the data is safely saved; every other state the grey one.
SaveStatusController.VARIANTS = { Saved = "ready" }

local holder = nil
local root = nil
local badge = nil
local shown = nil

-- Desktop: bottom right, above the settings button (the XP bar owns the
-- bottom left).
local DESKTOP_POSITION = UDim2.new(1, -12, 1, -84)
-- Touch: px kept from the end of the top bar's free area.
local TOUCH_GAP = 8

-- Places the tag for the form factor. `root` is the HUD root, scaled by
-- `fit` (screen px = root px × fit.Scale).
local function place()
	if holder == nil or root == nil then
		return
	end
	if not Kit.Scale.IsSmallTouch() then
		holder.AnchorPoint = Vector2.new(1, 1)
		holder.Position = DESKTOP_POSITION
		return
	end
	local fit = root:FindFirstChildWhichIsA("UIScale")
	local k = if fit then math.max(fit.Scale, 0.01) else 1
	local ok, bar = pcall(function()
		return GuiService.TopbarInset
	end)
	if ok and typeof(bar) == "Rect" and bar.Width > 0 and bar.Height > 0 then
		-- Right-aligned in the top bar's free area, centred on its height.
		holder.AnchorPoint = Vector2.new(1, 0.5)
		holder.Position = UDim2.fromOffset((bar.Max.X - TOUCH_GAP) / k, (bar.Min.Y + bar.Height / 2) / k)
	else
		-- No top bar: the top right corner, clear of the thumbstick and jump zones.
		holder.AnchorPoint = Vector2.new(1, 0)
		holder.Position = UDim2.new(1, -TOUCH_GAP / k, 0, TOUCH_GAP / k)
	end
end

local function refresh()
	local status = Players.LocalPlayer:GetAttribute(STATUS_ATTRIBUTE)
	local text = LABELS[status] or ""
	holder.Visible = status ~= nil and text ~= ""
	if text == shown then
		return
	end
	shown = text
	if badge then
		badge:Destroy()
		badge = nil
	end
	if text ~= "" then
		badge = Kit.Badge.new(holder, {
			name = "Status",
			variant = SaveStatusController.VARIANTS[status] or "notReady",
			text = text,
			rect = { 0, 0, 0, HEIGHT },
		})
		holder.Size = UDim2.fromOffset(badge.root.Size.X.Offset, HEIGHT)
	end
end

function SaveStatusController.Start()
	local player = Players.LocalPlayer
	local gui = Theme.Make("ScreenGui", {
		Name = "SaveStatus",
		ResetOnSpawn = false,
		-- Screen coordinates: on touch the tag sits in the top bar's row.
		IgnoreGuiInset = true,
		DisplayOrder = 10,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, nil)
	holder = Theme.Make("Frame", {
		Name = "Holder",
		AnchorPoint = Vector2.new(1, 1),
		BackgroundTransparency = 1,
		Position = DESKTOP_POSITION,
		Size = UDim2.fromOffset(0, HEIGHT),
		Visible = false,
	}, gui)
	gui.Parent = player:WaitForChild("PlayerGui")
	root = Theme.HudRoot(gui)
	holder.Parent = root
	player:GetAttributeChangedSignal(STATUS_ATTRIBUTE):Connect(refresh)
	refresh()
	-- Re-placed when the screen, the input devices, the HUD scale or the top
	-- bar change.
	Kit.Scale.OnFormFactorChanged(place)
	local fit = root:FindFirstChildWhichIsA("UIScale")
	if fit then
		fit:GetPropertyChangedSignal("Scale"):Connect(place)
	end
	pcall(function()
		GuiService:GetPropertyChangedSignal("TopbarInset"):Connect(place)
	end)
	place()
end

return SaveStatusController
