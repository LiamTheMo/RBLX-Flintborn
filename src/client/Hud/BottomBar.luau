-- Bottom-centre group: the "LV. n" badge with a long XP bar, and the 9-slot
-- hotbar. The hotbar is selection only and deliberately empty (no item icons or
-- counts yet). At the level cap the badge reads MAX over a full bar with a short
-- rebirth hint. Display only.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local Layout = require(script.Parent.Layout)
local Widgets = require(script.Parent.Widgets)

local BottomBar = {}
BottomBar.__index = BottomBar

function BottomBar.new(parent: Instance, layout)
	local cfg = layout.bottom
	local self = setmetatable({ slots = {}, selected = nil, level = nil }, BottomBar)
	-- Fires (index) when a slot is tapped or clicked.
	self.SlotPressed = Signal.new()
	self.root = Widgets.Make("Frame", { Name = "BottomBar", BackgroundTransparency = 1 }, parent)
	Layout.Place(self.root, cfg)

	local badgeCfg = cfg.badge
	local badge = Widgets.Sprite(badgeCfg.sprite, {
		Name = "LevelBadge",
		Position = Layout.Position(badgeCfg.rect),
		Size = Layout.Size(badgeCfg.rect),
		ZIndex = 6,
	}, self.root)
	self.levelText = Widgets.Text(badgeCfg, {
		Name = "Level",
		Text = "LV.",
		Size = UDim2.fromScale(1, 1),
		TextXAlignment = Enum.TextXAlignment.Center,
		ZIndex = 7,
	}, badge)

	local xpCfg = cfg.xp
	local inset = xpCfg.inset
	self.xpBar = Widgets.Bar({
		rect = xpCfg.rect,
		inset = inset[2],
		insetX = inset[1],
		maxWidth = xpCfg.rect[3] - inset[1] - inset[3],
		track = xpCfg.track,
		fillColor = xpCfg.fillColor,
	}, self.root)
	local xpRect = { 0, 0, xpCfg.rect[3], xpCfg.rect[4] }
	Widgets.Frame(xpCfg.frame, xpRect, self.xpBar.root, nil, xpCfg.frameOutset).ZIndex = 6
	self.maxHint = Widgets.Text(cfg.maxHint, {
		Name = "MaxHint",
		Size = UDim2.fromScale(1, 1),
		TextXAlignment = Enum.TextXAlignment.Center,
		TextStrokeTransparency = 0.3,
		Visible = false,
		ZIndex = 7,
	}, self.xpBar.root)

	local hotbarCfg = cfg.hotbar
	local slotWidth, slotHeight = hotbarCfg.slot[1], hotbarCfg.slot[2]
	self.hotbar = Widgets.Make("Frame", {
		Name = "Hotbar",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(hotbarCfg.x, hotbarCfg.y),
		Size = UDim2.fromOffset(hotbarCfg.pitch * (hotbarCfg.count - 1) + slotWidth, slotHeight),
	}, self.root)
	for index = 1, hotbarCfg.count do
		local slot = Widgets.Make("TextButton", {
			Name = "Slot" .. index,
			Text = "",
			AutoButtonColor = false,
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset((index - 1) * hotbarCfg.pitch, 0),
			Size = UDim2.fromOffset(slotWidth, slotHeight),
		}, self.hotbar)
		local slotRect = { 0, 0, slotWidth, slotHeight }
		local frame = Widgets.Frame(hotbarCfg.frame, slotRect, slot, hotbarCfg.sliceScale, hotbarCfg.frameOutset)
		frame.ZIndex = 2
		local ring = Widgets.SelectionRing(cfg.selected, slot)
		local number = Widgets.Text(cfg.slotNumber, {
			Name = "Number",
			Text = tostring(index),
			Position = Layout.Position(cfg.slotNumber.rect),
			Size = Layout.Size(cfg.slotNumber.rect),
			TextTruncate = Enum.TextTruncate.None,
			ZIndex = 5,
		}, slot)
		slot.Activated:Connect(function()
			self.SlotPressed:Fire(index)
		end)
		self.slots[index] = { button = slot, ring = ring, number = number }
	end
	return self
end

-- labels[index]: the key that selects each slot ("1", or a rebound key).
function BottomBar:SetSlotLabels(labels: { string })
	for index, slot in self.slots do
		local text = labels[index] or tostring(index)
		slot.number.Text = text
		-- A long key name ("Right Shift") shrinks to fit the slot corner.
		slot.number.TextScaled = #text > 2
	end
end

function BottomBar:Select(index: number)
	self.selected = index
	for slotIndex, slot in self.slots do
		slot.ring.Visible = slotIndex == index
	end
end

-- view: the progression snapshot {level, xp, xpToNext}; no xpToNext = level cap.
function BottomBar:SetProgress(view, instant: boolean?)
	local isMax = view.xpToNext == nil
	local fraction = HudModel.XpFraction(view.xp, view.xpToNext)
	local levelledUp = self.level ~= nil and view.level > self.level
	self.level = view.level
	self.levelText.Text = HudModel.LevelText(view.level, isMax)
	self.maxHint.Visible = isMax
	self.maxHint.Text = if isMax then HudModel.MaxLevelHint(view.level) else ""
	if levelledUp and not instant then
		-- Start the new level's bar from empty so the gain reads as a level-up.
		Widgets.SetBar(self.xpBar, 0, true)
	end
	Widgets.SetBar(self.xpBar, fraction, instant)
end

return BottomBar
