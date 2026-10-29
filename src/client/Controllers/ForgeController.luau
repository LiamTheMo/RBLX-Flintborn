-- Ancestral Forge (GDD §15–16, §25.3) in the parchment recipe window
-- (Hud/CraftingPanel, forge mode). The Forge navigation button opens it in the
-- lobby: one tab per category, counts are vault-only Owned/Needed, and locked
-- recipes show what unlocks them. A Permanent conversion lists the vault gear it
-- can use (that gear first in the list) and asks for confirmation, naming the
-- exact item and the Permanent rules, before anything is spent. Lobby place only.

local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local ForgeRecipes = require(ReplicatedStorage.Shared.Crafting.ForgeRecipes)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local CraftingPanel = require(script.Parent.Parent.Hud.CraftingPanel)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

local ForgeController = {}

ForgeController.CONFIRM_DELAY = 1.5

-- Category tabs and their glyphs.
ForgeController.GLYPHS = {
	Tools = "pm_glyph_tools",
	Weapons = "pm_glyph_sword",
	Armor = "pm_glyph_armor",
	Supplies = "pm_glyph_bag",
	Permanent = "pm_glyph_diamond",
}

local player = Players.LocalPlayer
local panel = nil
local busy = false

local CLOSE_ACTION = "FlintbornForgeClose"

local function invoke(name: string, ...)
	local ok, success, reason = pcall(Remotes.Get(name).InvokeServer, Remotes.Get(name), ...)
	if not ok then
		return false, "Request failed"
	end
	return success, reason
end

local function rollText(roll: number?): string
	return if roll and roll ~= 0 then ("%+.1f%%"):format(roll * 100) else ""
end

-- A snapshot recipe as the window lists it.
local function entryFor(recipe)
	local inputs, can = {}, CraftingPanel.MAX_BATCH
	for _, input in recipe.inputs do
		table.insert(inputs, { id = input.catalogId, name = input.name, owned = input.owned, needed = input.needed })
		can = math.min(can, if input.needed > 0 then input.owned // input.needed else can)
	end
	local permanent = recipe.kind == ForgeRecipes.Kinds.Permanent
	local sources = nil
	if permanent then
		sources = {}
		for _, source in recipe.sources or {} do
			table.insert(sources, { id = source.instanceId, name = source.name, detail = rollText(source.qualityRoll) })
		end
	end
	return {
		id = recipe.id,
		output = recipe.output,
		name = recipe.name,
		quantity = recipe.quantity,
		category = recipe.category,
		inputs = inputs,
		can = can,
		here = true,
		where = "From your vault",
		timed = false,
		locked = not recipe.unlocked,
		lockText = if recipe.requirement ~= "" then recipe.requirement else "Locked",
		verb = if permanent then "CONVERT" else "FORGE",
		sources = sources,
		raw = recipe,
	}
end

local refresh

local function submit(recipeId: string, sourceId: string?)
	busy = true
	panel:SetBusy(true)
	-- One nonce per confirmed request; a retry of the same request reuses it.
	local nonce = HttpService:GenerateGUID(false)
	local ok, result = invoke("ForgeCraft", recipeId, sourceId, nonce)
	if not ok and result == "Request failed" then
		ok, result = invoke("ForgeCraft", recipeId, sourceId, nonce)
	end
	panel:SetStatus(
		if ok then "Forged. Check your lobby backpack or vault." else ("Not forged: " .. Reasons.Text(result))
	)
	refresh()
	busy = false
	panel:SetBusy(false)
end

local function confirm(entry, sourceId: string)
	local source = nil
	for _, candidate in entry.raw.sources or {} do
		if candidate.instanceId == sourceId then
			source = candidate
		end
	end
	if source == nil then
		return
	end
	local spend = {}
	for _, input in entry.inputs do
		table.insert(spend, ("%s ×%d"):format(input.name, input.needed))
	end
	local roll = rollText(source.qualityRoll)
	panel:Confirm(
		("Convert this %s%s into a Permanent item?\n\nSpends from your vault: %s.\n\n"):format(
			source.name,
			if roll ~= "" then (" (quality %s, kept exactly)"):format(roll) else "",
			table.concat(spend, ", ")
		)
			.. "Permanent items stay with you when you die. Dropping one lets whoever picks it up own it, "
			.. "and trading transfers it. The ordinary version is consumed. This cannot be undone.",
		"CONVERT",
		ForgeController.CONFIRM_DELAY,
		function()
			task.spawn(submit, entry.id, sourceId)
		end
	)
end

function refresh()
	local view = invoke("ForgeSnapshot")
	if type(view) ~= "table" then
		-- Keeps a forge result on screen; the list just stays as it was.
		if panel.card.status.Text == "" then
			panel:SetStatus("Your data is still loading.")
		end
		return
	end
	local entries = {}
	for _, recipe in view.recipes do
		table.insert(entries, entryFor(recipe))
	end
	-- Permanent conversions for gear already in the vault come first.
	local order = {}
	for index, entry in entries do
		order[entry] = index
	end
	table.sort(entries, function(a, b)
		local aHas = a.sources ~= nil and #a.sources > 0
		local bHas = b.sources ~= nil and #b.sources > 0
		if aHas ~= bHas then
			return aHas
		end
		return order[a] < order[b]
	end)
	panel:SetEntries(entries)
end

local function close()
	ContextActionService:UnbindAction(CLOSE_ACTION)
	panel:HideConfirm()
	local focus = GuiService.SelectedObject
	if focus and focus:IsDescendantOf(panel.screen.gui) then
		GuiService.SelectedObject = nil
	end
	panel.screen:SetOpen(false)
end

local function build()
	local categories = {}
	for _, id in ForgeRecipes.Categories do
		table.insert(categories, { id = id, label = id, glyph = ForgeController.GLYPHS[id] or "pm_glyph_bench" })
	end
	panel = CraftingPanel.new(player:WaitForChild("PlayerGui"), {
		onClose = close,
		onCraft = function(entry, _, sourceId)
			if busy then
				return
			end
			if entry.sources then
				if sourceId then
					confirm(entry, sourceId)
				end
			else
				task.spawn(submit, entry.id, nil)
			end
		end,
		onStop = function() end,
	}, {
		mode = "forge",
		name = "FlintbornForge",
		window = "pm_window_forge",
		title = "ANCESTRAL FORGE",
		categories = categories,
	})
	panel.screen:Watch()
end

-- Opens or closes the window (the Forge navigation button).
function ForgeController.Toggle()
	if panel.screen:IsOpen() then
		close()
		return
	end
	panel:SetStatus("")
	panel:HideConfirm()
	panel.screen:SetOpen(true)
	ContextActionService:BindAction(CLOSE_ACTION, function(_, state)
		if state == Enum.UserInputState.Begin then
			if panel:IsConfirming() then
				panel:HideConfirm()
			else
				close()
			end
		end
		return Enum.ContextActionResult.Sink
	end, false, Enum.KeyCode.ButtonB)
	if GuiService.SelectedObject ~= nil or UserInputService.GamepadEnabled then
		GuiService.SelectedObject = panel.close
	end
	task.spawn(refresh)
end

function ForgeController.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	build()
end

return ForgeController
