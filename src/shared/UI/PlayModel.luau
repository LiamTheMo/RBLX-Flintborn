-- Pure display rules for the Play window (docs/ui/PlayScreen.md, ARCHITECTURE
-- §4.5): the run hotbar the deploy preview packs into, what the player carries,
-- the party list and its advisory ready count (D3), who may press Play (D16), the
-- deploy check's wording and the world's honest detail rows (D7). No Instances
-- here, so the headless specs and the window share one definition. The server
-- decides everything; these only describe what it will do.

local GameConstants = require(script.Parent.Parent.GameConstants)
local InventoryRules = require(script.Parent.Parent.Inventory.InventoryRules)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local BiomeCatalog = require(script.Parent.Parent.World.BiomeCatalog)

local PlayModel = {}

PlayModel.HOTBAR_SLOTS = GameConstants.HOTBAR_SLOTS

-- The world every run starts in (GDD §3).
PlayModel.WORLD_NAME = "Shattered Crater"
-- The zone the world is named for, marked on the map (the Keep in Crater Lake).
PlayModel.MARKED_ZONE = "ShatteredKeep"
-- Where a run starts: a random valid place away from other players (GDD §3.1,
-- SpawnService).
PlayModel.SPAWN_TEXT = "Random location"

-- Danger tiers from mildest to worst (BiomeCatalog.Regions risks).
PlayModel.RISK_ORDER = { "Low", "Medium", "High", "Extreme" }

PlayModel.TITLE_CHECK = "Take these into the run?"
PlayModel.TITLE_UNREAD = "Could not read your backpack"
PlayModel.TITLE_START = "Start the run?"
PlayModel.LINE_AT_RISK = "Everything except ★ Permanent items can be lost in the run."
PlayModel.LINE_UNREAD =
	"The item list did not load. Everything you carry except ★ Permanent items can be lost in the run."
PlayModel.LINE_VAULT = "Items in your vault always stay safe."
PlayModel.LINE_NOTHING = "Nothing from your backpack goes with you."
PlayModel.MEMBER_CAPTION = "The party leader starts the run."
PlayModel.MEMBER_READY_CAPTION = "You are ready. The party leader starts the run."

-- The run hotbar `items` (the deploy preview, {catalogId, quantity, permanent}[])
-- lands in: InventoryRules.FromItems, the packing InventoryService applies at run
-- start (LoadoutService.carriedPart). Returns slot -> item for slots 1–6 and how
-- many more stacks go to the run backpack (or stay behind when it is full).
function PlayModel.LoadoutHotbar(items): ({ [number]: any }, number)
	if type(items) ~= "table" then
		return {}, 0
	end
	local copies = {}
	for _, item in items do
		if type(item) == "table" and type(item.catalogId) == "string" then
			table.insert(copies, table.clone(item))
		end
	end
	local inventory, leftovers = InventoryRules.FromItems(copies)
	local hotbar = {}
	for index = 1, PlayModel.HOTBAR_SLOTS do
		local entry = inventory.hotbar[index]
		if entry then
			hotbar[index] = { catalogId = entry.catalogId, quantity = entry.quantity, permanent = entry.permanent }
		end
	end
	local more = #leftovers
	for _, entry in inventory.backpack do
		if entry then
			more += 1
		end
	end
	return hotbar, more
end

-- "+3 more in your backpack" under the hotbar, or nil when nothing is left over.
function PlayModel.MoreText(more: number?): string?
	if type(more) ~= "number" or more < 1 then
		return nil
	end
	return ("+%d more in your backpack"):format(more)
end

-- How many stacks go into the run and how many of them can be lost.
function PlayModel.Carrying(items): { stacks: number, atRisk: number, permanent: number }
	local summary = { stacks = 0, atRisk = 0, permanent = 0 }
	for _, item in if type(items) == "table" then items else {} do
		summary.stacks += 1
		if item.permanent then
			summary.permanent += 1
		else
			summary.atRisk += 1
		end
	end
	return summary
end

-- The Carrying row: "3 items, 2 at risk", "Nothing", or "Checking…" before the
-- first preview arrives.
function PlayModel.CarryingText(items): string
	if type(items) ~= "table" then
		return "Checking…"
	end
	local summary = PlayModel.Carrying(items)
	if summary.stacks == 0 then
		return "Nothing"
	end
	local count = ("%d %s"):format(summary.stacks, if summary.stacks == 1 then "item" else "items")
	if summary.atRisk == 0 then
		return count .. ", all Permanent"
	end
	return ("%s, %d at risk"):format(count, summary.atRisk)
end

-- The danger range across the world's zones: "Low to Extreme".
function PlayModel.RiskRange(): string
	local present = {}
	for _, region in BiomeCatalog.Regions do
		present[region.risk] = true
	end
	local first, last
	for _, risk in PlayModel.RISK_ORDER do
		if present[risk] then
			first = first or risk
			last = risk
		end
	end
	if first == nil then
		return ""
	end
	return if first == last then first else first .. " to " .. last
end

-- The world detail rows (D7: real data only). The fourth row, Carrying, comes
-- from the preview (CarryingRow).
function PlayModel.WorldRows(): { { icon: string, label: string, value: string } }
	return {
		{ icon = "mountain", label = "Region", value = PlayModel.WORLD_NAME },
		{
			icon = "tree",
			label = "Zones",
			value = ("%d · %s"):format(#BiomeCatalog.ZONE_IDS, PlayModel.RiskRange()),
		},
		{ icon = "map_pin", label = "Spawn", value = PlayModel.SPAWN_TEXT },
	}
end

function PlayModel.CarryingRow(items): { icon: string, label: string, value: string }
	return { icon = "chest", label = "Carrying", value = PlayModel.CarryingText(items) }
end

-- Where the marked zone sits on the island painting as 0–1 fractions, given the
-- painting's span in studs (IslandMap.MAP_SPAN), −Z (north) up.
function PlayModel.MarkerUV(span: number): (number, number)
	local x, z = BiomeCatalog.Center(PlayModel.MARKED_ZONE)
	return 0.5 + x / span, 0.5 + z / span
end

-- "solo", "leader" or "member": who presses what (D16). Solo players and leaders
-- press PLAY; other members get the Ready toggle.
function PlayModel.Role(view, userId: number): string
	local party = type(view) == "table" and view.party or nil
	if party == nil then
		return "solo"
	end
	return if party.leader == userId then "leader" else "member"
end

-- The party as rows, leader first: {userId, name, leader, ready}. Alone, a party
-- of one led by `me` ({userId, name}).
function PlayModel.Members(view, me): { { userId: number, name: string, leader: boolean, ready: boolean } }
	local party = type(view) == "table" and view.party or nil
	if party == nil then
		return {
			{ userId = me.userId, name = me.name, leader = true, ready = type(view) == "table" and view.ready == true },
		}
	end
	local rows = {}
	for _, member in party.members or {} do
		local row = {
			userId = member.userId,
			name = member.name or tostring(member.userId),
			leader = member.userId == party.leader,
			ready = member.ready == true,
		}
		if row.leader then
			table.insert(rows, 1, row)
		else
			table.insert(rows, row)
		end
	end
	return rows
end

-- How many of the party are ready, and its size (a solo player counts alone).
function PlayModel.ReadyCounts(view, me): (number, number)
	local ready, total = 0, 0
	for _, row in PlayModel.Members(view, me) do
		total += 1
		if row.ready then
			ready += 1
		end
	end
	return ready, total
end

-- The advisory note in the leader's deploy check (D3), or nil for a solo player.
function PlayModel.ReadyNote(ready: number, total: number): string?
	if total <= 1 then
		return nil
	end
	if ready >= total then
		return ("All %d party members are ready."):format(total)
	end
	return ("%d of %d party members are ready."):format(ready, total)
end

-- One line per item in the deploy check: "★ Stone Axe", "• Wood ×20".
function PlayModel.ItemLine(item): string
	local def = ItemCatalog.Get(item.catalogId)
	local name = def and def.name or tostring(item.catalogId)
	local count = if item.quantity and item.quantity > 1 then " ×" .. item.quantity else ""
	return (if item.permanent then "★ " else "• ") .. name .. count
end

-- What Play asks before deploying (GDD Q155), or nil to deploy at once:
-- {title, lines, notes, confirmLabel}. `items` is the fresh preview (nil when it
-- could not be read); `note` the ready note. An empty backpack with nothing to
-- point out deploys straight away.
function PlayModel.DeployCheck(items, note: string?, allReady: boolean?)
	if type(items) ~= "table" then
		return {
			title = PlayModel.TITLE_UNREAD,
			lines = {},
			notes = { PlayModel.LINE_UNREAD, PlayModel.LINE_VAULT, note },
			confirmLabel = "Enter anyway",
		}
	end
	if #items == 0 then
		if note == nil or allReady then
			return nil
		end
		return {
			title = PlayModel.TITLE_START,
			lines = {},
			notes = { PlayModel.LINE_NOTHING, note },
			confirmLabel = "Enter",
		}
	end
	local lines, atRisk = {}, false
	for _, item in items do
		table.insert(lines, PlayModel.ItemLine(item))
		atRisk = atRisk or not item.permanent
	end
	local notes = {}
	if atRisk then
		table.insert(notes, PlayModel.LINE_AT_RISK)
	end
	table.insert(notes, PlayModel.LINE_VAULT)
	if note then
		table.insert(notes, note)
	end
	return { title = PlayModel.TITLE_CHECK, lines = lines, notes = notes, confirmLabel = "Enter" }
end

return PlayModel
