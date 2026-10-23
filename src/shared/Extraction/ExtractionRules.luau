-- Extraction qualification and settlement (GDD §9, §10.3, Q17–24, Q119, Q126–129,
-- Q151–154, Q158). Presence counts only at the deadline. Only the fixed Center
-- portal doubles material quantities, and only what was gathered during a run:
-- units deployed from the lobby stay tagged on their stack (InventoryRules
-- `fromLobby`) whoever ends up carrying them; portable runes never double. Ordinary materials auto-bank into vault stacks of at
-- most 1,000; everything else lands in the durable 50-slot lobby backpack.
-- Anything over a capacity limit is deleted and listed on the receipt. Unique
-- gear is never multiplied.

local GameConstants = require(script.Parent.Parent.GameConstants)
local InventoryRules = require(script.Parent.Parent.Inventory.InventoryRules)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local ProgressionRules = require(script.Parent.Parent.Progression.ProgressionRules)
local Receipts = require(script.Parent.Parent.Data.Receipts)

local ExtractionRules = {}

ExtractionRules.FIXED_SECONDS = GameConstants.FIXED_EXTRACTION_SECONDS
ExtractionRules.PORTABLE_SECONDS = GameConstants.PORTABLE_EXTRACTION_SECONDS

ExtractionRules.Kinds = { Fixed = "Fixed", Center = "Center", Portable = "Portable" }

-- Only living, non-downed, at-risk players inside the zone at the deadline extract.
function ExtractionRules.Qualifies(candidate): boolean
	return candidate.alive and not candidate.downed and candidate.atRisk and candidate.inZone
end

function ExtractionRules.InZone(playerPosition, center, radius: number): boolean
	local dx, dz = playerPosition.X - center.X, playerPosition.Z - center.Z
	return math.sqrt(dx * dx + dz * dz) <= radius and math.abs(playerPosition.Y - center.Y) <= radius + 10
end

function ExtractionRules.Multiplier(kind: string): number
	return if kind == ExtractionRules.Kinds.Center then GameConstants.CENTER_MULTIPLIER else 1
end

-- Adds an item to the lobby backpack (one slot per stackable type, 50 slots).
-- Returns how much did not fit (deleted by the caller per Q154).
function ExtractionRules.AddToLobbyBackpack(slots, item): number
	local cap = ItemCatalog.StackCap(item.catalogId)
	if item.instanceId == nil and cap ~= nil then
		-- One slot per stackable type (Q128); anything beyond its cap does not fit.
		local quantity = item.quantity or 0
		for _, slot in slots do
			if slot.instanceId == nil and slot.catalogId == item.catalogId then
				local added = math.min(quantity, cap - slot.quantity)
				slot.quantity += added
				return quantity - added
			end
		end
		if quantity <= 0 then
			return 0
		end
		if #slots >= GameConstants.BACKPACK_SLOTS then
			return quantity
		end
		local added = math.min(quantity, cap)
		table.insert(slots, { catalogId = item.catalogId, quantity = added })
		return quantity - added
	end
	-- Permanent items are never deleted for lack of room (Q156: no limit on them).
	if #slots >= GameConstants.BACKPACK_SLOTS and not item.permanent then
		return 1
	end
	item.location = "LobbyBackpack"
	table.insert(slots, item)
	return 0
end

local function bump(map, key: string, amount: number)
	if amount > 0 then
		map[key] = (map[key] or 0) + amount
	end
end

-- A material stack's settled quantity: the multiplier applies only to units
-- gathered in a run, never to the ones it carries that were deployed from a lobby
-- (by this player or anyone they took them from).
local function multiplied(item, multiplier: number): number
	local quantity = item.quantity or 0
	local fromLobby = InventoryRules.FromLobby(item)
	return fromLobby + (quantity - fromLobby) * multiplier
end

-- A Guardian Legendary counts toward the rebirth challenge on its first
-- extraction only (v0.13); the stored copy is marked so trades and later
-- extractions never count it again.
local function creditsRebirth(item): boolean
	local def = ItemCatalog.Get(item.catalogId)
	return item.guardianEncounterId ~= nil and not item.rebirthCredited and def ~= nil and def.rarity == "Legendary"
end

-- Moves extracted items into the profile and returns the receipt. Runs inside a
-- ProfileService operation, so it applies once per receipt ID.
function ExtractionRules.Settle(profile, items, kind: string, receiptId: string, now: number)
	local multiplier = ExtractionRules.Multiplier(kind)
	local receipt = {
		at = now,
		kind = kind,
		multiplier = multiplier,
		vaulted = {},
		toBackpack = {},
		deleted = {},
		shown = false,
	}
	local materials = profile.vault.materials
	for _, item in items do
		local catalogId = item.catalogId
		if item.instanceId == nil and ItemCatalog.IsMaterial(catalogId) then
			local quantity = multiplied(item, multiplier)
			if ItemCatalog.IsOrdinaryMaterial(catalogId) then
				local stored, deleted = GameConstants.SettleMaterialStack(materials[catalogId] or 0, quantity)
				bump(receipt.vaulted, catalogId, stored - (materials[catalogId] or 0))
				bump(receipt.deleted, catalogId, deleted)
				materials[catalogId] = stored
			else
				local left = ExtractionRules.AddToLobbyBackpack(
					profile.lobbyBackpack.slots,
					{ catalogId = catalogId, quantity = quantity }
				)
				bump(receipt.toBackpack, catalogId, quantity - left)
				bump(receipt.deleted, catalogId, left)
			end
		else
			local copy = table.clone(item)
			if creditsRebirth(copy) then
				copy.rebirthCredited = true
				profile.rebirth.legendariesSinceRebirth = (profile.rebirth.legendariesSinceRebirth or 0) + 1
			end
			local left = ExtractionRules.AddToLobbyBackpack(profile.lobbyBackpack.slots, copy)
			local amount = copy.instanceId and 1 or (copy.quantity or 0)
			bump(receipt.toBackpack, catalogId, amount - left)
			bump(receipt.deleted, catalogId, left)
		end
	end
	-- Everything extracted counts as discovered for Forge recipe unlocks (v0.09).
	for _, item in items do
		profile.recipes.discovered[item.catalogId] = true
	end
	ProgressionRules.SettleRun(profile, receipt, kind)
	Receipts.Store(profile.receipts.extraction, receiptId, receipt)
	profile.metrics.extractions += 1
	return receipt
end

return ExtractionRules
