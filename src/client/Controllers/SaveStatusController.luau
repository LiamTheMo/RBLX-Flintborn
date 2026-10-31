-- Small persistent indicator of the player's profile save state, driven by the
-- SaveStatus attribute the server sets: a kit status tag (a dot and words, never
-- colour alone) at the bottom right.

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
local badge = nil
local shown = nil

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
		IgnoreGuiInset = false,
		DisplayOrder = 10,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, nil)
	-- Bottom-right above the settings button: the XP bar owns the bottom-left.
	holder = Theme.Make("Frame", {
		Name = "Holder",
		AnchorPoint = Vector2.new(1, 1),
		BackgroundTransparency = 1,
		Position = UDim2.new(1, -12, 1, -84),
		Size = UDim2.fromOffset(0, HEIGHT),
		Visible = false,
	}, gui)
	gui.Parent = player:WaitForChild("PlayerGui")
	holder.Parent = Theme.HudRoot(gui)
	player:GetAttributeChangedSignal(STATUS_ATTRIBUTE):Connect(refresh)
	refresh()
end

return SaveStatusController
