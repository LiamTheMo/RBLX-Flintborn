-- Pure rules for the lobby HUD (docs/ui/LobbyScreen.md, ARCHITECTURE §4.1): the
-- menu tiles, the level and XP lines, the party panel's rows and the hotbar
-- that shows the deploy loadout. No Instances here, so the specs and the
-- screen (Hud/Screens/LobbyHud) share one definition.

local GameConstants = require(script.Parent.Parent.GameConstants)
local InventoryRules = require(script.Parent.Parent.Inventory.InventoryRules)
local HudModel = require(script.Parent.HudModel)

local LobbyHudModel = {}

-- The 2 × 3 menu grid, left to right and top to bottom (M01): what each tile
-- opens and its icon id (a role name for the Play tile's rune art, D26).
LobbyHudModel.TILES = {
	{ id = "Inventory", icon = "backpack" },
	{ id = "Play", icon = "icon.playRune" },
	{ id = "Quests", icon = "scroll" },
	{ id = "Shop", icon = "market" },
	{ id = "Forge", icon = "anvil" },
	{ id = "Trade", icon = "trade" },
}

LobbyHudModel.HOTBAR_SLOTS = GameConstants.HOTBAR_SLOTS

-- The level and XP lines for a progression snapshot {level, xp, xpToNext}
-- (no xpToNext = the level cap: the level still reads as its number, the XP
-- line says so). While the snapshot loads (nil) the lines are blank and the
-- bars empty, rather than a made-up level.
function LobbyHudModel.Progress(view): { level: string, fraction: number, text: string }
	if type(view) ~= "table" then
		return { level = "", fraction = 0, text = "" }
	end
	local isMax = view.xpToNext == nil
	if isMax then
		return { level = HudModel.LevelText(view.level), fraction = 1, text = "Max level" }
	end
	local xp = math.max(0, math.floor(view.xp or 0))
	local need = math.max(0, math.floor(view.xpToNext))
	return {
		level = HudModel.LevelText(view.level),
		fraction = HudModel.XpFraction(xp, need),
		text = ("%d/%d XP"):format(xp, need),
	}
end

export type Member = { userId: number, name: string, leader: boolean, self: boolean }

-- The party panel from LobbyController.PartyView() and you ({userId, name}):
-- {count = "1/8", members = {Member}, free = empty rows, invites = {{partyId,
-- from, busy}}, canInvite}. Alone you are a party of one, led by you. Only
-- the leader (or a solo player) can invite, and only while there is room. `busy` maps the partyIds whose answer
-- is on its way (PartyController.AnswerBusy); those invites are marked busy.
function LobbyHudModel.Party(view, me: { userId: number, name: string }, busy: { [string]: boolean }?)
	view = view or {}
	local maxSize = view.maxSize or 8
	local party = view.party
	local members = {}
	if party then
		for _, member in party.members or {} do
			table.insert(members, {
				userId = member.userId,
				name = member.name or tostring(member.userId),
				leader = member.userId == party.leader,
				self = member.userId == me.userId,
			})
		end
	end
	if #members == 0 then
		table.insert(members, {
			userId = me.userId,
			name = me.name,
			leader = true,
			self = true,
		})
	end
	local leads = party == nil or party.leader == me.userId
	-- Copies: the view's own tables stay untouched.
	local invites = {}
	for _, invite in view.invites or {} do
		local entry = table.clone(invite)
		entry.busy = busy ~= nil and busy[invite.partyId] == true
		table.insert(invites, entry)
	end
	return {
		count = HudModel.PartyCount(#members, maxSize),
		members = members,
		free = math.max(0, maxSize - #members),
		invites = invites,
		canInvite = leads and #members < maxSize,
	}
end

-- What lands in the run's hotbar for the deploy preview ({catalogId, quantity,
-- permanent}[]): the same packing the server applies at run start
-- (InventoryRules.FromItems, as LoadoutService does). A list of
-- HOTBAR_SLOTS entries, each an item ({itemId, quantity, permanent}; the Kit
-- takes its art and tint from ItemInfo) or false for an empty slot; all empty
-- while the preview is unknown (nil).
function LobbyHudModel.Hotbar(items): { any }
	local slots = table.create(LobbyHudModel.HOTBAR_SLOTS, false)
	if type(items) ~= "table" then
		return slots
	end
	local inventory = InventoryRules.FromItems(items)
	for index = 1, LobbyHudModel.HOTBAR_SLOTS do
		local entry = inventory.hotbar[index]
		if entry then
			slots[index] = {
				itemId = entry.catalogId,
				quantity = entry.quantity,
				permanent = entry.permanent == true,
			}
		end
	end
	return slots
end

-- Gamepad neighbours in the 2 × 3 tile grid: {up, down, left, right} as tile
-- indices (nil at an edge).
function LobbyHudModel.TileNeighbours(index: number): { up: number?, down: number?, left: number?, right: number? }
	local count = #LobbyHudModel.TILES
	local column = (index - 1) % 2
	return {
		up = if index - 2 >= 1 then index - 2 else nil,
		down = if index + 2 <= count then index + 2 else nil,
		left = if column == 1 then index - 1 else nil,
		right = if column == 0 and index + 1 <= count then index + 1 else nil,
	}
end

return LobbyHudModel
