-- Body looting (GDD §29.2) and the death summary (GDD §25.4). Interacting with a
-- body opens its contents in a kit window; take items one by one while in range.
-- After your own death, a kit notice card separates what dropped from what you
-- kept. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Kit = require(script.Parent.Parent.Hud.Kit)
local NoticeCard = require(script.Parent.Parent.Hud.NoticeCard)
local Theme = require(script.Parent.Parent.Ui.Theme)

local LootController = {}

LootController.SIZE = { 600, 560 }
LootController.ROW_H = 64

local player = Players.LocalPlayer
local ui = {}
local openBodyId = nil

-- One item row: the item's art, name, rarity and count, and an action button
-- over the row's right end. `entry.catalogId` (sent by the server with every body
-- and chest entry) picks the art.
function LootController.ItemRow(parent: Instance, order: number, w: number, entry, action: string, onAction)
	local h = LootController.ROW_H
	local holder = Kit.Core.Make("Frame", {
		Name = "Item" .. order,
		BackgroundTransparency = 1,
		LayoutOrder = order,
		Size = UDim2.fromOffset(w, h),
	}, parent)
	Kit.ListRow.new(holder, {
		name = "Row",
		rect = { 0, 0, w, h },
		itemId = entry.catalogId,
		title = entry.name,
		subtitle = entry.rarity .. (if entry.permanent then " · Permanent" else ""),
		value = if entry.quantity then "×" .. entry.quantity else nil,
		trailing = 112,
	})
	Kit.Button.new(holder, {
		name = action,
		rect = { w - 14 - 112, (h - 42) / 2, 112, 42 },
		label = action,
		sizeClass = "s",
		zIndex = 6,
		onPress = onAction,
	})
	return holder
end

local function clear()
	for _, part in ui.rows do
		part:Destroy()
	end
	table.clear(ui.rows)
end

local function render(bodyId: string, entries)
	openBodyId = bodyId
	clear()
	local w = ui.listW
	if #entries == 0 then
		table.insert(
			ui.rows,
			Kit.Text.new(ui.list, {
				name = "Empty",
				size = { w, 40 },
				layoutOrder = 1,
				text = "Nothing left.",
				role = "muted",
				align = "Center",
			}).root
		)
	end
	for order, entry in entries do
		table.insert(
			ui.rows,
			LootController.ItemRow(ui.list, order, w, entry, "Take", function()
				local ok, success, reason = pcall(function()
					return Remotes.Get("CorpseTake"):InvokeServer(openBodyId, entry.index)
				end)
				if not ok or not success then
					ui.status:SetText("Could not take that (" .. tostring(reason) .. ")")
				end
			end)
		)
	end
	ui.panel.scroll:SetContentHeight(math.max(1, #entries) * (LootController.ROW_H + 6))
	ui.status:SetText("")
	ui.screen:Open()
end

local function build()
	local w, h = LootController.SIZE[1], LootController.SIZE[2]
	ui.rows = {}
	ui.screen = Kit.Screen.new("FlintbornLoot", { size = LootController.SIZE })
	local window = Kit.Window.new(ui.screen, { title = "Body", icon = "bone" })
	local body = window:Body()
	local bw, bh = window.bodyRect[3], window.bodyRect[4]
	ui.panel =
		Kit.Panel.new(body, { name = "Contents", rect = { 0, 0, bw, bh - 44 }, variant = "inset", scroll = true })
	ui.list = ui.panel:Content()
	ui.listW = ui.panel.contentRect[3] - 14
	ui.status = Kit.Text.new(body, {
		name = "Status",
		rect = { 4, bh - 38, bw - 8, 34 },
		text = "",
		role = "body",
		color = "short",
	})
	ui.screen:Watch()
	ui.screen.Closed:Connect(function()
		openBodyId = nil
	end)

	-- The death summary: centred, until the teleport to the lobby.
	local gui = Theme.Make("ScreenGui", {
		Name = "Loot",
		ResetOnSpawn = false,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, player:WaitForChild("PlayerGui"))
	local holder = Theme.Make("Frame", {
		Name = "Holder",
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Position = UDim2.fromScale(0.5, 0.35),
		Size = UDim2.fromOffset(w, 0),
	}, gui)
	Theme.FitHud(gui, Theme.Make("UIScale", { Name = "Fit" }, holder))
	ui.summary = NoticeCard.new(holder, { name = "Summary", width = w, title = "You died", icon = "bone" })
	ui.summary.frame.AnchorPoint = Vector2.new(0, 0.5)
	ui.summary.frame.Active = true
	ui.summary:SetTone("short")
end

function LootController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	Remotes.Get("CorpseOpened").OnClientEvent:Connect(render)
	Remotes.Get("DeathSummary").OnClientEvent:Connect(function(summary)
		ui.summary:Show(
			("Dropped and lootable: %d item(s) in your body (10 minutes)\nSafe in vault: unchanged\nPermanent: %d kept\nReturning to the lobby…"):format(
				summary.dropped or 0,
				summary.kept or 0
			)
		)
	end)
end

return LootController
