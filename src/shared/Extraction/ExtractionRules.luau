-- Extraction qualification and settlement (GDD §9, §10.3, §53, Q17–24, Q119,
-- Q126–129, Q151–154, Q158). Presence counts only at the deadline. Only the fixed
-- Center portal doubles material quantities; portable runes never do. Materials
-- may be carried into a run (GDD §53), and what was carried in never multiplies:
-- Play records each material's carried-in quantity on the run (RecordCarriedIn),
-- and per material only the extracted amount above it is multiplied. That is
-- keyed on totals, not stacks, so dropping, re-picking or trading units inside a
-- run changes nothing. Every material, special ones included, banks into the
-- vault: its material capacity (1,000 per type) decides what is deleted, and the
-- receipt lists it. Everything else lands in the durable 50-slot lobby backpack,
-- where only a full backpack deletes. Unique gear is never multiplied.

local GameConstants = require(script.Parent.Parent.GameConstants)
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

local function count(value: any): number
	return if type(value) == "number" and value == value and value > 0 and value ~= math.huge then value else 0
end

-- Adds the material stacks among `items` to the run's carried-in record
-- ({[catalogId] = quantity}), which Settle never multiplies. Play records what
-- enters the run inventory, inside its consume operation, so the record is saved
-- with the run and survives a rejoin or a crash.
function ExtractionRules.RecordCarriedIn(run, items)
	local carried = run.carriedIn or {}
	for _, item in items do
		if item.instanceId == nil and ItemCatalog.IsMaterial(item.catalogId) then
			local quantity = count(item.quantity)
			if quantity > 0 then
				carried[item.catalogId] = (carried[item.catalogId] or 0) + quantity
			end
		end
	end
	run.carriedIn = carried
end

-- The settled quantity of `extracted` units of a material when `carriedIn` of
-- them entered the run: the carried-in part counts once, only the rest multiplies
-- (bring 100, extract 160 at the Center: 100 + 60 × 2 = 220).
function ExtractionRules.MaterialYield(extracted: number, carriedIn: number, multiplier: number): number
	local unmultiplied = math.min(extracted, carriedIn)
	return unmultiplied + (extracted - unmultiplied) * multiplier
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
	-- Materials settle per type, from their extracted totals (GDD §53).
	local run = profile.progression.currentRun
	local carried = if run and not run.settled and type(run.carriedIn) == "table" then run.carriedIn else {}
	local totals, order = {}, {}
	for _, item in items do
		local catalogId = item.catalogId
		if item.instanceId == nil and ItemCatalog.IsMaterial(catalogId) then
			if totals[catalogId] == nil then
				totals[catalogId] = 0
				table.insert(order, catalogId)
			end
			totals[catalogId] += count(item.quantity)
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
	for _, catalogId in order do
		local extracted = totals[catalogId]
		local carriedIn = count(carried[catalogId])
		local current = materials[catalogId] or 0
		local stored, deleted =
			GameConstants.SettleMaterialStack(current, ExtractionRules.MaterialYield(extracted, carriedIn, multiplier))
		bump(receipt.vaulted, catalogId, stored - current)
		bump(receipt.deleted, catalogId, deleted)
		materials[catalogId] = if stored > 0 then stored else nil
		if multiplier ~= 1 then
			-- Units the bonus skipped because they were carried in, for the receipt.
			local skipped = math.min(extracted, carriedIn)
			if skipped > 0 then
				receipt.carriedIn = receipt.carriedIn or {}
				bump(receipt.carriedIn, catalogId, skipped)
			end
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
