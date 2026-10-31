-- Lobby trading (GDD §10.2, §25.4, §53) in the kit Trade window
-- (Hud/ListWindow, docs/ui/ListWindows.md). The Trade tile opens it: pick a
-- player in this lobby to invite. During a trade it shows both offers as slot
-- panels with their lock state, your tradeable lobby-backpack items to add or
-- remove, your tradeable vault materials (+1, +10, all or remove), a Gem amount
-- (never Coins), a lock, a countdown and confirm (which asks once more with
-- both offers spelled out). Any change unlocks both sides. Invites arrive as a
-- toast with Accept and Decline. Lobby only.

local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local TradeRules = require(ReplicatedStorage.Shared.Economy.TradeRules)
local Kit = require(script.Parent.Parent.Hud.Kit)
local ListWindow = require(script.Parent.Parent.Hud.ListWindow)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

local TradeController = {}

-- An invite toast waits this long for an answer.
TradeController.INVITE_SECONDS = 60

local player = Players.LocalPlayer
local window = nil
local session = nil
local inviteId = nil
local countdown = nil
local confirmReady = nil
local gemsBox = nil
local invite = nil
local answering = nil
-- Bumped by every render; a render that yielded and is no longer the latest drops.
local renderToken = 0

-- A gems change typed while a push arrives waits for the box to lose focus.
local pending = false

local function invoke(name: string, ...)
	local ok, success, reason = pcall(Remotes.Get(name).InvokeServer, Remotes.Get(name), ...)
	if not ok then
		return false, "Request failed"
	end
	return success, reason
end

local render

-- My current offer: backpack slot keys, and vault materials {[catalogId] = quantity}.
local function myOffer()
	local keys, materials = {}, {}
	for _, item in session.mine.items do
		local catalogId = TradeRules.MaterialOf(item.key)
		if catalogId then
			materials[catalogId] = item.quantity
		else
			table.insert(keys, item.key)
		end
	end
	return keys, materials
end

local function sendOffer(keys, materials, gems: number)
	local ok, reason = invoke("TradeOffer", session.id, keys, gems, materials)
	if not ok then
		window:SetStatus("Offer refused: " .. Reasons.Text(reason), "warn")
	end
end

-- One side of the trade for the offer panel.
local function side(offer, title: string, icon: string, locked: boolean, confirmed: boolean)
	local items = {}
	for _, item in offer.items do
		-- The server names every offered item by its catalog id (TradeService.describe).
		table.insert(items, { itemId = item.catalogId, name = item.name, quantity = item.quantity })
	end
	return {
		title = title,
		icon = icon,
		items = items,
		gems = offer.gems,
		state = if confirmed then "confirmed" elseif locked then "locked" else "open",
	}
end

local function describe(offer): string
	local parts = {}
	for _, item in offer.items do
		table.insert(parts, item.name .. (item.quantity and (" ×" .. item.quantity) or ""))
	end
	if offer.gems > 0 then
		table.insert(parts, offer.gems .. " Gems")
	end
	return if #parts > 0 then table.concat(parts, ", ") else "Nothing."
end

local function countdownText(): string
	local left = math.ceil(session.confirmAt - workspace:GetServerTimeNow())
	return ("Both locked: confirm unlocks in %d s"):format(left)
end

local function invitePlayers()
	window:Line("Invite a player in this lobby to trade items and Gems (Coins can't be traded).")
	window:Section("Players in this lobby", "party")
	local any = false
	for _, other in Players:GetPlayers() do
		if other ~= player then
			any = true
			window:Player({
				key = "Player" .. other.UserId,
				userId = other.UserId,
				name = other.DisplayName,
				level = other:GetAttribute("Level"),
				action = {
					label = "Invite",
					key = "Invite",
					onPress = function()
						local ok, reason = invoke("TradeRequest", other.UserId)
						window:SetStatus(
							if ok then "Invite sent." else ("Couldn't invite: " .. Reasons.Text(reason)),
							if ok then "good" else "warn"
						)
					end,
				},
			})
		end
	end
	if not any then
		window:Line("Nobody else is in this lobby right now.", "ink")
	end
end

-- Tradeable items come from the lobby backpack and vault views the vault panel
-- uses. Materials are offered only from the vault (GDD §53: deposit a backpack
-- stack to offer it).
local function offerables(view)
	local offered, offeredMaterials = myOffer()
	local backpack = {}
	for _, item in view.backpack do
		if item.key and TradeRules.IsTradeableSlot(item) then
			table.insert(backpack, item)
		end
	end
	if #backpack > 0 then
		window:Section("Your lobby backpack", "backpack")
	end
	for _, item in backpack do
		local key = item.key
		local inOffer = table.find(offered, key) ~= nil
		window:Row({
			key = "Slot" .. tostring(key),
			title = item.name .. (if item.quantity then (" ×" .. item.quantity) else ""),
			icon = item.catalogId,
			detail = if inOffer then "In your offer." else nil,
			buttons = {
				{
					label = if inOffer then "Remove" else "Add",
					key = "Toggle",
					kind = if inOffer then "paper" else nil,
					onPress = function()
						local keys, materials = myOffer()
						local index = table.find(keys, key)
						if index then
							table.remove(keys, index)
						else
							table.insert(keys, key)
						end
						sendOffer(keys, materials, session.mine.gems)
					end,
				},
			},
		})
	end
	local shown = false
	for _, material in view.materials or {} do
		local catalogId, stock = material.catalogId, material.quantity
		if not TradeRules.IsTradeableMaterial(catalogId) then
			continue
		end
		if not shown then
			window:Section("Your vault materials", "chest")
			shown = true
		end
		local current = offeredMaterials[catalogId] or 0
		local function setQuantity(quantity: number)
			local keys, materials = myOffer()
			materials[catalogId] = if quantity > 0 then math.min(quantity, stock) else nil
			sendOffer(keys, materials, session.mine.gems)
		end
		window:Row({
			key = "Material" .. catalogId,
			title = material.name,
			detail = ("%d in your vault · offering %d"):format(stock, current),
			icon = catalogId,
			buttons = {
				{
					label = "Remove",
					key = "Remove",
					kind = "paper",
					enabled = current > 0,
					onPress = function()
						setQuantity(0)
					end,
				},
				{
					label = "All",
					key = "All",
					enabled = current < stock,
					onPress = function()
						setQuantity(stock)
					end,
				},
				{
					label = "+10",
					key = "Ten",
					enabled = current < stock,
					onPress = function()
						setQuantity(current + 10)
					end,
				},
				{
					label = "+1",
					key = "One",
					enabled = current < stock,
					onPress = function()
						setQuantity(current + 1)
					end,
				},
			},
		})
	end
	-- Tradeable berries deposited in the vault offer from the backpack only.
	local stored = {}
	for _, item in view.items or {} do
		if item.quantity and TradeRules.IsTradeableSlot(item) then
			table.insert(stored, item.name)
		end
	end
	if #stored > 0 then
		window:Line("Withdraw " .. table.concat(stored, ", ") .. " from the vault to offer it.")
	end
	window:Line("Rare materials and rare berries trade; ores, bars and common materials never do.")
end

function render()
	renderToken += 1
	local token = renderToken
	local current = session
	if gemsBox and gemsBox.Parent and gemsBox:IsFocused() then
		-- Redrawn when the player finishes typing.
		pending = true
		return
	end
	-- Fetch first, then clear and rebuild without yielding, so a TradeChanged push
	-- during the round trip can't interleave and duplicate rows.
	local view = if current then invoke("VaultSnapshot") else nil
	if token ~= renderToken or session ~= current then
		return
	end
	if gemsBox and gemsBox.Parent and gemsBox:IsFocused() then
		-- Focused during the round trip: still wait for the player.
		pending = true
		return
	end
	pending = false
	window:Begin()
	countdown = nil
	confirmReady = nil
	gemsBox = nil
	if session == nil then
		window:SetTitle("Trade")
		invitePlayers()
		window:Finish()
		return
	end
	window:SetTitle("Trade with " .. session.partner)
	window:Line(("Trading with %s. Any change unlocks both offers."):format(session.partner), "ink")
	window:Pair(
		side(session.mine, "You give", "backpack", session.locked.mine, session.confirmed.mine),
		side(session.theirs, "You get", "gift", session.locked.theirs, session.confirmed.theirs)
	)
	local now = workspace:GetServerTimeNow()
	if session.confirmAt and now < session.confirmAt then
		countdown = window:Line(countdownText(), "gold")
	end
	confirmReady = session.confirmAt ~= nil and now >= session.confirmAt
	window:Buttons({
		{
			label = "Cancel",
			key = "Cancel",
			kind = "paper",
			onPress = function()
				invoke("TradeCancel", session.id)
			end,
		},
		{
			label = if session.locked.mine then "Locked" else "Lock Offer",
			key = "Lock",
			width = 180,
			enabled = not session.locked.mine,
			onPress = function()
				invoke("TradeLock", session.id)
			end,
		},
		{
			label = if session.confirmed.mine then "Confirmed" else "Confirm",
			key = "Confirm",
			width = 180,
			enabled = confirmReady and not session.confirmed.mine,
			onPress = function()
				local current = session
				window:Confirm("", "Trade", 0, function()
					if session ~= current then
						return
					end
					local ok, reason = invoke("TradeConfirm", current.id)
					if not ok then
						window:SetStatus("Not yet: " .. Reasons.Text(reason), "warn")
					end
				end, {
					title = "Confirm this trade?",
					rows = {
						{ label = "You give", text = describe(current.mine) },
						{ label = "You get", text = describe(current.theirs) },
					},
				})
			end,
		},
	})
	gemsBox = window:Input("Gems to offer", "0", function(text)
		local gems = if text == "" then 0 else tonumber(text)
		if session and gems and gems >= 0 and gems % 1 == 0 and gems ~= session.mine.gems then
			local keys, materials = myOffer()
			sendOffer(keys, materials, gems)
		end
		if pending then
			task.defer(render)
		end
	end, true)
	gemsBox.Text = if session.mine.gems > 0 then tostring(session.mine.gems) else ""
	if type(view) == "table" then
		offerables(view)
	end
	window:Finish()
end

-- Escape and gamepad B close the question first, then the window (Kit.Modal).
local function close()
	window:Close()
end

local function open()
	window:Open(GuiService.SelectedObject ~= nil or UserInputService.GamepadEnabled)
	render()
end

local function hideInvite()
	if invite then
		invite.Close()
		invite = nil
	end
end

-- The invite: a toast (KitToasts sits above the windows, so it can be answered
-- with a menu open) whose View opens the question with Accept and Decline.
local function showInvite(from: string)
	hideInvite()
	local function answer(accept: boolean)
		if inviteId then
			invoke("TradeRespond", inviteId, accept)
			inviteId = nil
		end
	end
	local function ask()
		hideInvite()
		if answering then
			answering.Close()
		end
		answering = Kit.ConfirmDialog.Show({
			title = "Trade invite",
			text = from .. " wants to trade with you.",
			confirmLabel = "Accept",
			cancelLabel = "Decline",
			onConfirm = function()
				answering = nil
				answer(true)
			end,
			onCancel = function()
				answering = nil
				answer(false)
			end,
		})
	end
	invite = Kit.Toast.Show({
		kind = "info",
		icon = "trade",
		title = "Trade invite",
		text = from .. " wants to trade.",
		duration = TradeController.INVITE_SECONDS,
		onPress = ask,
		actions = { { label = "View", onPress = ask } },
	})
end

local function build()
	window = ListWindow.new(player:WaitForChild("PlayerGui"), {
		name = "FlintbornTrade",
		title = "Trade",
		icon = "trade",
		onClose = close,
	})
end

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function TradeController.Toggle()
	if window.screen:IsOpen() then
		close()
	else
		window:SetStatus("")
		open()
	end
end

function TradeController.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	build()
	Remotes.Get("TradeChanged").OnClientEvent:Connect(function(payload)
		if payload.kind == "Invite" then
			inviteId = payload.id
			showInvite(payload.from)
		elseif payload.kind == "Session" then
			if session == nil then
				-- A new trade: the invite's outcome line is old news.
				window:SetStatus("")
			end
			session = payload
			if window.screen:IsOpen() then
				render()
			else
				open()
			end
		elseif payload.kind == "Closed" then
			session = nil
			hideInvite()
			if answering then
				answering.Close()
				answering = nil
			end
			window:HideConfirm()
			window:SetStatus("Trade " .. string.lower(payload.reason) .. ".")
			-- Always re-render (cheap with no session) so an in-flight render drops.
			render()
		end
	end)
	-- The confirm countdown ticks while the window is open: only its label changes,
	-- plus one re-render when the Confirm button becomes available.
	task.spawn(function()
		while true do
			task.wait(1)
			if session and session.confirmAt and window.screen:IsOpen() then
				local ready = workspace:GetServerTimeNow() >= session.confirmAt
				if ready ~= confirmReady then
					render()
				elseif countdown and countdown.Parent then
					countdown.Text = countdownText()
				end
			end
		end
	end)
end

return TradeController
