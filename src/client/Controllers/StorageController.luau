-- Storage chests (GDD §6.1, Q39). Opening a chest shows its contents next to your
-- carried items in a kit window: take from the chest or store from your
-- inventory. Chests are public, so anything stored can be taken by anyone who
-- reaches it. World only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Kit = require(script.Parent.Parent.Hud.Kit)
local InventoryController = require(script.Parent.InventoryController)
local LootController = require(script.Parent.LootController)

local StorageController = {}

StorageController.SIZE = { 1000, 600 }

local player = Players.LocalPlayer
local ui = {}
local openChestId = nil
local contents = {}

local function invoke(name: string, ...)
	local ok, success, reason = pcall(Remotes.Get(name).InvokeServer, Remotes.Get(name), ...)
	if not ok then
		return false, "Request failed"
	end
	return success, reason
end

local function clear(column)
	for _, part in column.rows do
		part:Destroy()
	end
	table.clear(column.rows)
end

local function fill(column, entries, action: string, onAction)
	clear(column)
	for order, entry in entries do
		table.insert(
			column.rows,
			LootController.ItemRow(column.list, order, column.w, entry, action, function()
				onAction(entry)
			end)
		)
	end
	if #entries == 0 then
		table.insert(
			column.rows,
			Kit.Text.new(column.list, {
				name = "Empty",
				size = { column.w, 40 },
				layoutOrder = 1,
				text = "Nothing here.",
				role = "muted",
				align = "Center",
			}).root
		)
	end
	column.panel.scroll:SetContentHeight(math.max(1, #entries) * (LootController.ROW_H + 6))
end

local function render()
	if openChestId == nil then
		return
	end
	fill(ui.chest, contents, "Take", function(entry)
		local ok, reason = invoke("ChestTake", openChestId, entry.index)
		if not ok then
			ui.status:SetText("Could not take that (" .. tostring(reason) .. ")")
		end
	end)
	local carried = {}
	for _, slot in InventoryController.Snapshot.slots do
		if slot.area ~= "armor" then
			local def = ItemCatalog.Get(slot.catalogId)
			table.insert(carried, {
				catalogId = slot.catalogId,
				name = def and def.name or slot.catalogId,
				rarity = def and def.rarity or "Common",
				quantity = slot.quantity,
				permanent = slot.permanent,
				slot = slot,
			})
		end
	end
	fill(ui.mine, carried, "Store", function(entry)
		local ok, reason = invoke("ChestPut", openChestId, entry.slot.area, entry.slot.index)
		if not ok then
			ui.status:SetText("Could not store that (" .. tostring(reason) .. ")")
		end
	end)
	ui.screen:Open()
end

local function column(body, x: number, w: number, h: number, title: string, icon: string)
	local panel = Kit.Panel.new(
		body,
		{ name = title, rect = { x, 0, w, h }, variant = "inset", title = title, icon = icon, scroll = true }
	)
	return { panel = panel, list = panel:Content(), w = panel.contentRect[3] - 14, rows = {} }
end

local function build()
	ui.screen = Kit.Screen.new("FlintbornStorage", { size = StorageController.SIZE })
	local window = Kit.Window.new(ui.screen, {
		title = "Storage chest",
		subtitle = "Public: anyone who reaches it can take items.",
		icon = "chest",
	})
	local body = window:Body()
	local bw, bh = window.bodyRect[3], window.bodyRect[4]
	local gap = Kit.Tokens.Space("colGap", 14)
	local cw = (bw - gap) / 2
	ui.chest = column(body, 0, cw, bh - 44, "In the chest", "chest")
	ui.mine = column(body, cw + gap, cw, bh - 44, "Carried", "backpack")
	ui.status = Kit.Text.new(body, {
		name = "Status",
		rect = { 4, bh - 38, bw - 8, 34 },
		text = "",
		role = "body",
		color = "short",
	})
	ui.screen:Watch()
	ui.screen.Closed:Connect(function()
		openChestId = nil
	end)
end

function StorageController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	Remotes.Get("ChestOpened").OnClientEvent:Connect(function(chestId, entries)
		openChestId = chestId
		contents = entries
		ui.status:SetText("")
		render()
	end)
	InventoryController.Changed:Connect(function()
		if openChestId and ui.screen:IsOpen() then
			render()
		end
	end)
	-- Walking away or ending the run closes the chest view.
	player:GetAttributeChangedSignal("SessionState"):Connect(function()
		ui.screen:Close()
		openChestId = nil
	end)
end

return StorageController
