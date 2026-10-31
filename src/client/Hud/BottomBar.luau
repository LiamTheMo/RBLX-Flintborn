-- Bottom-centre group, the same parts and measures as the lobby HUD's (Kit
-- XP track with "LV. n" before it and "450/750 XP" after it, then six hotbar
-- slots with leather number badges): the run's hotbar items as their art
-- (ItemInfo through Kit.ItemIcon), stack counts, the Permanent star and the
-- selected slot's gold glow. The badges name the bound keys. A press fires
-- SlotPressed, which HudController turns into the same use as the key. At the
-- level cap the bar is full and points to rebirth.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local LobbyHudModel = require(ReplicatedStorage.Shared.UI.LobbyHudModel)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local Kit = require(script.Parent.Kit)
local Layout = require(script.Parent.Layout)

local BottomBar = {}
BottomBar.__index = BottomBar

-- Beside the full bar at the level cap (rebirth happens in the lobby).
BottomBar.MAX_TEXT = "Max level · rebirth in the lobby"

function BottomBar.new(parent: Instance, layout)
	local cfg = layout.bottom
	local self = setmetatable({ slots = {}, selected = nil, level = nil }, BottomBar)
	-- Fires (index) when a slot is tapped or clicked.
	self.SlotPressed = Signal.new()
	self.root = Instance.new("Frame")
	self.root.Name = "BottomBar"
	self.root.BackgroundTransparency = 1
	Layout.Place(self.root, cfg)
	self.root.Parent = parent

	self.levelText = Kit.Text.new(self.root, {
		name = "Level",
		rect = cfg.level,
		text = "",
		role = "hudSmall",
		textSize = cfg.textSize,
		-- Over the world: a paper outline keeps it readable on any scene.
		outline = true,
		align = "Right",
	})
	self.xpBar = Kit.Bar.new(self.root, { name = "XpBar", rect = cfg.xp, fill = "xp" })
	self.xpText = Kit.Text.new(self.root, {
		name = "Xp",
		rect = cfg.xpText,
		text = "",
		role = "hudSmall",
		textSize = cfg.textSize,
		-- Over the world: a paper outline keeps it readable on any scene.
		outline = true,
		scaled = true,
	})

	local hotbar = cfg.hotbar
	self.hotbar = Instance.new("Frame")
	self.hotbar.Name = "Hotbar"
	self.hotbar.BackgroundTransparency = 1
	self.hotbar.Position = UDim2.fromOffset(0, hotbar.y)
	self.hotbar.Size = UDim2.fromOffset(cfg.size[1], hotbar.slot[2])
	self.hotbar.Parent = self.root
	for index = 1, hotbar.count do
		local slot = Kit.Slot.new(self.hotbar, {
			name = "Slot" .. index,
			rect = { hotbar.x[index], 0, hotbar.slot[1], hotbar.slot[2] },
			variant = "hotbar",
			hotkey = tostring(index),
			onPress = function()
				self.SlotPressed:Fire(index)
			end,
		})
		self.slots[index] = slot
	end
	for index, slot in self.slots do
		local hit = slot.control.hit
		local left, right = self.slots[index - 1], self.slots[index + 1]
		hit.NextSelectionLeft = left and left.control.hit
		hit.NextSelectionRight = right and right.control.hit
	end
	return self
end

-- labels[index]: the key that selects each slot ("1", or a rebound key).
function BottomBar:SetSlotLabels(labels: { string })
	for index, slot in self.slots do
		slot:SetHotkey(labels[index] or tostring(index))
	end
end

-- items[index]: {itemId, quantity, permanent} or nil/false for an empty slot.
function BottomBar:SetSlotItems(items)
	for index, slot in self.slots do
		local item = items[index]
		slot:SetItem(if item then item else nil)
	end
end

function BottomBar:Select(index: number)
	self.selected = index
	for slotIndex, slot in self.slots do
		slot:SetSelected(slotIndex == index)
	end
end

-- view: the progression snapshot {level, xp, xpToNext}; no xpToNext = level cap.
function BottomBar:SetProgress(view, instant: boolean?)
	local progress = LobbyHudModel.Progress(view)
	local isMax = type(view) == "table" and view.xpToNext == nil
	local levelledUp = self.level ~= nil and type(view) == "table" and (view.level or 0) > self.level
	self.level = if type(view) == "table" then view.level else nil
	self.levelText:SetText(progress.level)
	self.xpText:SetText(if isMax then BottomBar.MAX_TEXT else progress.text)
	if levelledUp and not instant then
		-- Start the new level's bar from empty so the gain reads as a level-up.
		self.xpBar:Set(0, true)
	end
	self.xpBar:Set(progress.fraction, instant)
end

return BottomBar
