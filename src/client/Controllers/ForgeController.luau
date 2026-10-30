-- Ancestral Forge (GDD §15–16, §25.3) in the recipe window (Hud/Screens/
-- RecipeWindow, forge mode). The Forge tile opens it in the lobby. Counts are
-- vault-only Owned/Needed; a special recipe may be forged in a batch (QUANTITY,
-- up to the snapshot's maxCount, all paid for in one request or none of it);
-- locked recipes show what unlocks them. A Permanent conversion names the exact
-- vault item (the player picks one when there are several) and the Permanent
-- rules, and CONVERT is press-and-hold before anything is spent. The snapshot is
-- fetched when the window opens and after each request. Lobby place only.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ForgeRecipes = require(ReplicatedStorage.Shared.Crafting.ForgeRecipes)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local RecipeModel = require(ReplicatedStorage.Shared.UI.RecipeModel)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local RecipeWindow = require(script.Parent.Parent.Hud.Screens.RecipeWindow)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

local ForgeController = {}

-- How long CONVERT is held before a Permanent conversion is sent.
ForgeController.CONFIRM_DELAY = RecipeWindow.CONVERT_HOLD

local player = Players.LocalPlayer
local window = nil
local busy = false
local loaded = false

local function invoke(name: string, ...)
	local ok, success, result = pcall(Remotes.Get(name).InvokeServer, Remotes.Get(name), ...)
	if not ok then
		return false, "Request failed"
	end
	return success, result
end

-- Player-facing text for a refusal code.
local function reasonText(code: any): string
	local text = Reasons.Text(code)
	if text == tostring(code) and RecipeModel.REASONS[code] then
		return RecipeModel.REASONS[code]
	end
	return text
end

local function refresh()
	local ok, view = pcall(function()
		return Remotes.Get("ForgeSnapshot"):InvokeServer()
	end)
	if not ok or type(view) ~= "table" then
		-- The list stays as it was; say so only before the first snapshot.
		if not loaded then
			window:SetStatus("Still loading", "Your data is still loading. Try again in a moment.", "warn")
		end
		return
	end
	loaded = true
	local entries = RecipeModel.ForgeEntries(view)
	window:SetEntries(entries, RecipeModel.Materials(entries))
end
ForgeController.Refresh = refresh

-- Sends one forge request: `count` crafts of `entry` (a Permanent conversion
-- always 1, with its source item). One nonce per request; a transport retry
-- reuses it so the server never charges twice.
local function submit(entry, count: number, sourceId: string?)
	if busy then
		return
	end
	busy = true
	window:SetBusy(true)
	local nonce = HttpService:GenerateGUID(false)
	local ok, result = invoke("ForgeCraft", entry.id, sourceId, nonce, count)
	if not ok and result == "Request failed" then
		ok, result = invoke("ForgeCraft", entry.id, sourceId, nonce, count)
	end
	if ok then
		local title, text = RecipeModel.ForgeReceipt(entry, result, count)
		window:SetStatus(title, text, "item")
	else
		window:SetStatus(
			if entry.kind == ForgeRecipes.Kinds.Permanent then "Not converted" else "Not forged",
			reasonText(result),
			"warn"
		)
	end
	refresh()
	busy = false
	window:SetBusy(false)
end

local function onForge(entry, count: number)
	if busy then
		return
	end
	if entry.kind == ForgeRecipes.Kinds.Permanent then
		window:ConfirmConversion(entry, function(sourceId: string)
			task.spawn(submit, entry, 1, sourceId)
		end)
	else
		task.spawn(submit, entry, count, nil)
	end
end

local function build()
	local categories = {}
	for _, id in ForgeRecipes.Categories do
		table.insert(categories, { id = id, label = id })
	end
	window = RecipeWindow.new({
		mode = "forge",
		name = "FlintbornForge",
		title = "Ancestral Forge",
		subtitle = "Turn raw materials into tools for the island.",
		icon = "anvil_hammer",
		categories = categories,
		parent = player:WaitForChild("PlayerGui"),
		onForge = onForge,
	})
	window:Watch()
	ForgeController.window = window
end

-- Opens or closes the window (the Forge tile). Escape / B close it (Kit.Modal).
function ForgeController.Toggle()
	if window == nil then
		return
	end
	if window:IsOpen() then
		window:Close()
		return
	end
	window:Open()
	task.spawn(refresh)
end

function ForgeController.IsOpen(): boolean
	return window ~= nil and window:IsOpen()
end

function ForgeController.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	build()
	-- The vault changing elsewhere (a deposit or withdrawal) refreshes the counts.
	local ok, VaultController = pcall(require, script.Parent.VaultController)
	local changed = ok and type(VaultController) == "table" and (VaultController :: any).Changed
	if changed and changed.Connect then
		changed:Connect(function()
			if window:IsOpen() and not busy then
				task.spawn(refresh)
			end
		end)
	end
end

return ForgeController
