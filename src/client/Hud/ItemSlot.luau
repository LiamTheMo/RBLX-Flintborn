-- One parchment item slot (art/reference/ui/parchment/08_inventory_vault.png): the
-- slot plate, the item's icon or, until item icons exist, its name, a quantity
-- badge, a star for Permanent items, a rarity stripe and an optional key label.
-- Selected slots get the gold ring; the equipped hotbar slot a leather one.
--
-- Icon hook: an item shows the sprite "item_<catalogId>" once one is uploaded
-- (UiAssetIds.json); until then its name is written in the slot.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local UiAssets = require(ReplicatedStorage.Shared.UI.UiAssets)
local Layout = require(script.Parent.Layout)
local Parchment = require(script.Parent.Parchment)
local Widgets = require(script.Parent.Widgets)

local ItemSlot = {}
ItemSlot.__index = ItemSlot

ItemSlot.SIZE = { 93, 96 }

-- The uploaded icon sprite for an item, or nil.
function ItemSlot.IconFor(catalogId: string?): string?
	if catalogId == nil then
		return nil
	end
	local name = "item_" .. catalogId
	return if UiAssets.image(name) then name else nil
end

-- `props` places the slot's holder (Size, Position, LayoutOrder...). onPress()
-- runs on a press.
function ItemSlot.new(parent: Instance, props, onPress)
	local self = setmetatable({}, ItemSlot)
	local holder = Widgets.Make("Frame", { Name = "Slot", BackgroundTransparency = 1, ZIndex = 4 }, parent)
	for key, value in props or {} do
		(holder :: any)[key] = value
	end
	self.holder = holder
	local z = holder.ZIndex
	self.art = Widgets.Sprite("pm_item_slot", { Name = "Art", Size = UDim2.fromScale(1, 1), ZIndex = z }, holder, 0.7)
	self.name = Widgets.Text({ font = "serif", textSize = 16, color = "ink" }, {
		Name = "ItemName",
		Position = UDim2.new(0, 6, 0, 8),
		Size = UDim2.new(1, -12, 1, -30),
		TextStrokeTransparency = 1,
		TextWrapped = true,
		TextScaled = true,
		TextTruncate = Enum.TextTruncate.None,
		TextXAlignment = Enum.TextXAlignment.Center,
		ZIndex = z + 1,
	}, holder)
	Widgets.TextCap(self.name, 17, 9)
	self.stripe = Widgets.Make("Frame", {
		Name = "Rarity",
		AnchorPoint = Vector2.new(0, 1),
		BackgroundColor3 = Color3.new(1, 1, 1),
		BorderSizePixel = 0,
		Position = UDim2.new(0, 10, 1, -6),
		Size = UDim2.new(0.42, 0, 0, 4),
		ZIndex = z + 1,
	}, holder)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, self.stripe)
	self.badge = Widgets.Make("Frame", {
		Name = "Count",
		AnchorPoint = Vector2.new(1, 1),
		BackgroundColor3 = Layout.Color("badge"),
		BorderSizePixel = 0,
		Position = UDim2.new(1, -5, 1, -5),
		Size = UDim2.fromOffset(30, 23),
		AutomaticSize = Enum.AutomaticSize.X,
		ZIndex = z + 2,
	}, holder)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 5) }, self.badge)
	Widgets.Make("UIPadding", { PaddingLeft = UDim.new(0, 4), PaddingRight = UDim.new(0, 4) }, self.badge)
	self.count = Widgets.Text({ font = "serif", textSize = 17, color = "cream" }, {
		Name = "Text",
		AutomaticSize = Enum.AutomaticSize.X,
		Size = UDim2.new(0, 22, 1, 0),
		TextStrokeTransparency = 1,
		TextTruncate = Enum.TextTruncate.None,
		TextXAlignment = Enum.TextXAlignment.Center,
		ZIndex = z + 3,
	}, self.badge)
	self.star = Widgets.Text({ font = "serif", textSize = 18, color = "gold" }, {
		Name = "Permanent",
		Text = "★",
		Position = UDim2.fromOffset(6, 3),
		Size = UDim2.fromOffset(20, 20),
		TextStrokeTransparency = 0.4,
		ZIndex = z + 2,
	}, holder)
	self.key = Widgets.Text({ font = "serif", textSize = 14, color = "inkSoft" }, {
		Name = "Key",
		Position = UDim2.new(1, -54, 0, 3),
		Size = UDim2.fromOffset(50, 18),
		TextStrokeTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Right,
		Visible = false,
		ZIndex = z + 2,
	}, holder)
	self.ring = Widgets.Make("UIStroke", {
		Color = Layout.Color("selectGlow"),
		Thickness = 3,
		ApplyStrokeMode = Enum.ApplyStrokeMode.Border,
		Enabled = false,
	}, holder)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 9) }, holder)
	self.dim = Widgets.Make("Frame", {
		Name = "Dim",
		BackgroundColor3 = Layout.Color("paper"),
		BackgroundTransparency = 0.45,
		BorderSizePixel = 0,
		Size = UDim2.fromScale(1, 1),
		Visible = false,
		ZIndex = z + 4,
	}, holder)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 9) }, self.dim)
	self.button = Parchment.Pressable(holder, self.art, onPress or function() end)
	self.button.ZIndex = z + 5
	self:Set(nil)
	return self
end

-- `item` = {catalogId, name, quantity?, rarity?, permanent?} or nil for empty.
function ItemSlot:Set(item)
	self.item = item
	if self.icon then
		self.icon:Destroy()
		self.icon = nil
	end
	local iconName = item and ItemSlot.IconFor(item.catalogId)
	if iconName then
		self.icon = Widgets.Sprite(iconName, {
			Name = "Icon",
			AnchorPoint = Vector2.new(0.5, 0.5),
			Position = UDim2.fromScale(0.5, 0.45),
			Size = UDim2.fromScale(0.74, 0.74),
			ZIndex = self.holder.ZIndex + 1,
		}, self.holder)
	end
	self.name.Text = if item and not iconName then item.name or item.catalogId else ""
	local quantity = item and item.quantity
	self.badge.Visible = quantity ~= nil and quantity > 1
	self.count.Text = if quantity then tostring(quantity) else ""
	self.star.Visible = item ~= nil and item.permanent == true
	self.stripe.Visible = item ~= nil and item.rarity ~= nil and item.rarity ~= "Common"
	if item and item.rarity then
		self.stripe.BackgroundColor3 = Rarity.Colors[item.rarity] or Color3.new(1, 1, 1)
	end
end

function ItemSlot:SetSelected(selected: boolean, equipped: boolean?)
	self.ring.Enabled = selected or equipped == true
	self.ring.Color = Layout.Color(if selected then "selectGlow" else "leather")
	self.ring.Thickness = if selected then 3.5 else 3
end

function ItemSlot:SetKey(text: string?)
	self.key.Visible = text ~= nil and text ~= ""
	self.key.Text = text or ""
end

-- Dimmed when it does not match the tab or the search.
function ItemSlot:SetDimmed(dimmed: boolean)
	self.dim.Visible = dimmed
end

return ItemSlot
