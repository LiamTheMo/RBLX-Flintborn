-- The lobby screen (GDD §11, §25; docs/ui/LobbyScreen.md): the profile with level
-- and XP, the navigation tiles, Coins, Gems and Settings, the party panel and the
-- Enter button with the server dropdown, built by Hud/LobbyHud from
-- HudLayout.json's "lobby" section.
-- Lobby place only (HudMode.ReplacesLobby); the older lobby visuals stay hidden.
-- If the HUD fails to build, the lobby falls back to those older visuals.
--
-- Everything acts through the existing controllers: LobbyController deploys,
-- reads the deploy preview and runs party actions; the buttons open the Vault,
-- Journal (quests), Market (Shop tab), Forge, Trade, Progress and Settings panels.

local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SocialService = game:GetService("SocialService")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PartyRules = require(ReplicatedStorage.Shared.Admission.PartyRules)
local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local ForgeController = require(script.Parent.ForgeController)
local JournalController = require(script.Parent.JournalController)
local LobbyController = require(script.Parent.LobbyController)
local ProgressionController = require(script.Parent.ProgressionController)
local SettingsController = require(script.Parent.SettingsController)
local TradeController = require(script.Parent.TradeController)
local VaultController = require(script.Parent.VaultController)
local WalletController = require(script.Parent.WalletController)
local Hud = script.Parent.Parent.Hud
local HudMode = require(Hud.HudMode)
local Layout = require(Hud.Layout)
local LobbyHud = require(Hud.LobbyHud)
local LobbyPopups = require(Hud.LobbyPopups)
local Theme = require(script.Parent.Parent.Ui.Theme)

local LobbyHudController = {}

-- How long a status message stays in the status strip.
LobbyHudController.STATUS_SECONDS = 6

local player = Players.LocalPlayer
local layout, gui, root, uiScale, hud, popups
local statusToken = 0
-- userId -> headshot image, or a list of callbacks while the fetch runs.
local thumbnails = {}
-- Which button last opened the vault panel (Inventory and Vault both open it).
local vaultOpener = nil

local function steady(): boolean
	return Theme.ReducedMotion()
end

-- A headshot for userId, fetched once. While it loads this returns nil and `done`
-- runs when it arrives; a failed fetch is forgotten, so the next ask retries.
local function thumbnail(userId: number, done: (() -> ())?): string?
	local cached = thumbnails[userId]
	if type(cached) == "string" then
		return cached
	end
	if type(cached) == "table" then
		if done then
			table.insert(cached, done)
		end
		return nil
	end
	local waiting = if done then { done } else {}
	thumbnails[userId] = waiting
	task.spawn(function()
		local ok, image = pcall(function()
			return Players:GetUserThumbnailAsync(userId, Enum.ThumbnailType.HeadShot, Enum.ThumbnailSize.Size150x150)
		end)
		if ok and type(image) == "string" then
			thumbnails[userId] = image
			for _, callback in waiting do
				task.spawn(callback)
			end
		else
			thumbnails[userId] = nil
		end
	end)
	return nil
end

local function openVault(id: string)
	-- Inventory then Vault (or back) keeps the panel open instead of closing it.
	if VaultController.IsOpen() and vaultOpener ~= id then
		vaultOpener = id
		return
	end
	vaultOpener = id
	VaultController.Toggle()
end

local NAV_ACTIONS = {
	-- The lobby backpack lives in the vault panel, beside the vault itself.
	Inventory = function()
		openVault("Inventory")
	end,
	Vault = function()
		openVault("Vault")
	end,
	Quests = function()
		JournalController.Toggle()
	end,
	Shop = function()
		WalletController.Open("Shop")
	end,
	Forge = function()
		ForgeController.Toggle()
	end,
	Trade = function()
		TradeController.Toggle()
	end,
}

-- How far down the Roblox top bar (menu and chat buttons) reaches into this
-- ScreenGui, in screen pixels.
local function topInset(): number
	local ok, inset = pcall(function()
		return GuiService.TopbarInset.Max.Y
	end)
	if not ok or type(inset) ~= "number" then
		-- Older clients without TopbarInset: the classic GUI inset.
		inset = GuiService:GetGuiInset().Y
	end
	return math.max(0, inset - gui.AbsolutePosition.Y)
end

local function applyScale()
	local size = gui.AbsoluteSize
	local scale = HudModel.HudScale(
		size.X,
		size.Y,
		layout.reference.width,
		layout.reference.height,
		layout.scale.min,
		layout.scale.max,
		player:GetAttribute("UiScale")
	)
	uiScale.Scale = scale
	root.Size = UDim2.fromScale(1 / scale, 1 / scale)
	local top = topInset() / scale
	hud:Fit(size.X / scale, size.Y / scale, top, scale)
	popups:SetScreen(size.Y / scale, top, scale)
end

local refreshParty

local function refreshProfile()
	hud:SetProfile(player.DisplayName, thumbnail(player.UserId, refreshProfile))
end

refreshParty = function()
	local view = LobbyController.PartyView()
	local party = view.party
	local members = {}
	if party then
		for _, member in party.members do
			table.insert(members, {
				userId = member.userId,
				name = member.name,
				leader = member.userId == party.leader,
				thumbnail = thumbnail(member.userId, refreshParty),
			})
		end
	else
		-- Alone: a party of one, led by you.
		table.insert(members, {
			userId = player.UserId,
			name = player.DisplayName,
			leader = true,
			thumbnail = thumbnail(player.UserId, refreshParty),
		})
	end
	local leads = party == nil or party.leader == player.UserId
	local canInvite = leads and #members < PartyRules.MAX_SIZE
	hud:SetParty(members, view.invites or {}, PartyRules.MAX_SIZE, canInvite, party ~= nil)
end

local function refreshCurrency()
	hud:SetCurrency(player:GetAttribute("Coins"), player:GetAttribute("Gems"))
end

-- The status strip between messages: empty, or the game-update notice
-- while it applies.
local function idleLine(): string?
	return if player:GetAttribute("MaintenanceNotice") then LobbyController.MAINTENANCE_TEXT else nil
end

-- Shows a status message in the status strip for a few seconds.
local function showStatus(text: string)
	statusToken += 1
	local token = statusToken
	hud:SetServerLine(text)
	task.delay(LobbyHudController.STATUS_SECONDS, function()
		if token == statusToken and not LobbyController.IsDeploying() then
			hud:SetServerLine(idleLine())
		end
	end)
end

local function deploy()
	popups:Hide()
	hud:SetEnterBusy(true)
	task.spawn(function()
		LobbyController.Deploy()
		hud:SetEnterBusy(false)
	end)
end

local function confirm(title: string, lines: { string }, enterLabel: string)
	popups:Show({
		title = title,
		lines = lines,
		buttons = {
			{ label = enterLabel, primary = true, onPress = deploy },
			{
				label = "CANCEL",
				onPress = function()
					popups:Hide()
				end,
			},
		},
	})
end

-- Enter: reads the deploy preview fresh, and when anything goes with you lists it
-- first and asks (GDD Q155). With an empty backpack it deploys straight away.
local entering = false
local function onEnter()
	if entering or LobbyController.IsDeploying() then
		return
	end
	entering = true
	hud:SetEnterBusy(true)
	task.spawn(function()
		local items = LobbyController.FetchPreview()
		hud:SetEnterBusy(false)
		entering = false
		if items == nil then
			confirm("COULD NOT READ YOUR BACKPACK", {
				"The item list did not load. Everything you carry except ★ Permanent items can be lost in the run.",
				"Items in your vault always stay safe.",
			}, "ENTER ANYWAY")
			return
		end
		if #items == 0 then
			deploy()
			return
		end
		local lines, atRisk = {}, false
		for _, item in items do
			local def = ItemCatalog.Get(item.catalogId)
			local name = def and def.name or tostring(item.catalogId)
			local count = if item.quantity then " ×" .. item.quantity else ""
			atRisk = atRisk or not item.permanent
			table.insert(lines, (if item.permanent then "★ " else "• ") .. name .. count)
		end
		if atRisk then
			table.insert(lines, "Everything except ★ Permanent items can be lost in the run.")
		end
		table.insert(lines, "Items in your vault always stay safe.")
		confirm("TAKE THESE INTO THE RUN?", lines, "ENTER")
	end)
end

local function inviteRoblox()
	popups:Hide()
	local ok, canInvite = pcall(function()
		return SocialService:CanSendGameInviteAsync(player)
	end)
	if ok and canInvite then
		pcall(function()
			SocialService:PromptGameInvite(player)
		end)
	else
		showStatus("Roblox invites are not available right now.")
	end
end

local function onInvite()
	local rows = {}
	for _, other in LobbyController.Invitable() do
		table.insert(rows, {
			text = other.DisplayName,
			thumbnail = thumbnail(other.UserId) or "",
			action = "INVITE",
			onPress = function()
				popups:Hide()
				task.spawn(LobbyController.PartyAction, "invite", other.UserId)
				showStatus("Party invite sent to " .. other.DisplayName .. ".")
			end,
		})
	end
	popups:Show({
		title = "INVITE TO YOUR PARTY",
		lines = if #rows == 0 then { "No one else is in this lobby server yet." } else {},
		rows = rows,
		buttons = { { label = "INVITE ROBLOX FRIENDS", primary = true, onPress = inviteRoblox } },
	})
end

local function onServer()
	popups:Show({
		title = "CHOOSE SERVER",
		rows = { { text = "✓  Best match (automatic)" } },
		lines = { "Your party joins the best open world together, and the leader starts it." },
	})
end

local function build()
	gui = Instance.new("ScreenGui")
	gui.Name = "FlintbornLobbyHud"
	gui.ResetOnSpawn = false
	gui.DisplayOrder = 1
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	-- The layout uses the master's full-screen coordinates and keeps clear of the
	-- top bar itself (LobbyHud:Fit); device cut-outs (notches) stay excluded.
	gui.IgnoreGuiInset = true
	pcall(function()
		gui.ScreenInsets = Enum.ScreenInsets.DeviceSafeInsets
	end)
	root = Instance.new("Frame")
	root.Name = "Root"
	root.BackgroundTransparency = 1
	root.Size = UDim2.fromScale(1, 1)
	root.Parent = gui
	uiScale = Instance.new("UIScale")
	uiScale.Parent = root
	hud = LobbyHud.new(root, layout, steady)
	popups = LobbyPopups.new(root, layout)
	-- XP pop-ups appear under the profile panel, above the navigation tiles.
	local host = Instance.new("Frame")
	host.Name = "XpPopups"
	host.BackgroundTransparency = 1
	host.Parent = root
	hud:AddTopWidget(host, { anchor = { 0, 0 }, pos = { 0, 48, 0, 232 }, size = { 320, 120 } })
	ProgressionController.MountPopups(host)
	gui.Parent = player:WaitForChild("PlayerGui")
end

local function start()
	layout = Layout.Get()
	build()
	applyScale()
	gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(applyScale)
	pcall(function()
		GuiService:GetPropertyChangedSignal("TopbarInset"):Connect(applyScale)
	end)
	player:GetAttributeChangedSignal("UiScale"):Connect(function()
		task.defer(applyScale)
	end)

	refreshProfile()
	local view = ProgressionController.View()
	if view then
		hud:SetProgress(view, true)
	end
	ProgressionController.Changed:Connect(function(progress)
		hud:SetProgress(progress, steady())
	end)
	refreshCurrency()
	player:GetAttributeChangedSignal("Coins"):Connect(refreshCurrency)
	player:GetAttributeChangedSignal("Gems"):Connect(refreshCurrency)

	refreshParty()
	hud:SetServerLine(idleLine())
	player:GetAttributeChangedSignal("MaintenanceNotice"):Connect(function()
		hud:SetServerLine(idleLine())
	end)
	LobbyController.Changed:Connect(function(what)
		if what == "party" then
			refreshParty()
		elseif what == "status" then
			showStatus(LobbyController.Status())
		end
	end)

	hud.NavPressed:Connect(function(id)
		local action = NAV_ACTIONS[id]
		if action then
			action()
		end
	end)
	hud.ProfilePressed:Connect(ProgressionController.Toggle)
	hud.SettingsPressed:Connect(SettingsController.Toggle)
	hud.EnterPressed:Connect(onEnter)
	hud.ServerPressed:Connect(onServer)
	hud.InvitePressed:Connect(onInvite)
	hud.LeavePressed:Connect(function()
		task.spawn(LobbyController.PartyAction, "leave")
	end)
	hud.InviteAnswered:Connect(function(partyId, accept)
		task.spawn(LobbyController.PartyAction, if accept then "accept" else "decline", partyId)
	end)
end

function LobbyHudController.Start()
	if not HudMode.ReplacesLobby() then
		return
	end
	local ok, err = pcall(start)
	if not ok then
		-- Never leave the lobby without Deploy: hand it back to the older visuals.
		warn("[LobbyHud] failed to build, using the older lobby screen: " .. tostring(err))
		if gui then
			gui:Destroy()
		end
		HudMode.SetLobbyFailed()
		LobbyController.BuildFallback()
	end
end

return LobbyHudController
