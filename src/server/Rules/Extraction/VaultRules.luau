-- The secure vault (GDD §10.3, §53, Q96, Q122, Q151, Q154). 25 item slots (+25
-- per upgrade, v0.14) and material storage of up to 1,000 per type. Item deposits
-- are manual and are refused when there is no room, never deleted. A material
-- deposit that would go over the capacity is refused until the player confirms
-- it, and then anything over the capacity is deleted (GDD §53). Item
-- and material withdrawals go to the lobby backpack, which deploys on the next
-- Play (Q155), materials included (GDD §53).

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local ExtractionRules = require(ReplicatedStorage.Shared.Extraction.ExtractionRules)
local InventoryRules = require(ReplicatedStorage.Shared.Inventory.InventoryRules)

local VaultRules = {}

function VaultRules.ItemCapacity(profile): number
	return GameConstants.VaultSlots(profile.vault.upgradeTier or 0)
end

-- Settles `quantity` of a material into its vault stack, deleting what exceeds the
-- capacity; a loss is recorded on `vault.lastOverflow` so the vault can show it.
-- Returns how much was deleted.
function VaultRules.BankMaterial(profile, catalogId: string, quantity: number, now: number): number
	local materials = profile.vault.materials
	local stored, over = GameConstants.SettleMaterialStack(materials[catalogId] or 0, math.max(0, quantity))
	materials[catalogId] = if stored > 0 then stored else nil
	if over > 0 then
		profile.vault.lastOverflow = { at = now, deleted = { [catalogId] = over } }
	end
	return over
end

-- How many of a lobby backpack slot's stack a deposit moves: `quantity` when it
-- is a whole number from 1 to the stack (a unique item is always 1), the whole
-- stack when nil; nil for anything else (the client's amount is never trusted).
function VaultRules.DepositAmount(item, quantity: any?): number?
	local owned = if item.instanceId then 1 else math.max(1, item.quantity or 1)
	if quantity == nil then
		return owned
	end
	if type(quantity) ~= "number" or quantity ~= quantity or quantity % 1 ~= 0 then
		return nil
	end
	if quantity < 1 or quantity > owned then
		return nil
	end
	return quantity
end

-- How much of the material stack in a lobby backpack slot depositing it (or
-- `quantity` of it) would delete for lack of vault capacity (0 for anything else).
function VaultRules.DepositLoss(profile, backpackIndex: number, quantity: any?): number
	local item = profile.lobbyBackpack.slots[backpackIndex]
	if item == nil or item.instanceId ~= nil or not ItemCatalog.IsMaterial(item.catalogId) then
		return 0
	end
	local amount = VaultRules.DepositAmount(item, quantity)
	if amount == nil then
		return 0
	end
	local current = profile.vault.materials[item.catalogId] or 0
	local _, over = GameConstants.SettleMaterialStack(current, amount)
	return over
end

VaultRules.WOULD_OVERFLOW = "VaultWouldOverflow"

-- Moves one lobby backpack slot (or `quantity` of its stack; nil: all of it)
-- into the vault. Returns (ok, reason). A material banks into its vault stack;
-- one that would go past the capacity is refused with WOULD_OVERFLOW
-- (DepositLoss says how much) unless `confirmed` = {catalogId, loss} accepts it:
-- the slot must still hold that material and lose no more than the player agreed
-- to, and then the excess is deleted (BankMaterial). What is not stored stays in
-- the backpack slot.
function VaultRules.Deposit(profile, backpackIndex: number, now: number?, confirmed: any?, quantity: any?)
	local slots = profile.lobbyBackpack.slots
	local item = slots[backpackIndex]
	if item == nil then
		return false, "Empty"
	end
	local amount = VaultRules.DepositAmount(item, quantity)
	if amount == nil then
		return false, "BadQuantity"
	end
	local owned = if item.instanceId then 1 else math.max(1, item.quantity or 1)
	if item.instanceId == nil and ItemCatalog.IsMaterial(item.catalogId) then
		local loss = VaultRules.DepositLoss(profile, backpackIndex, amount)
		local accepted = type(confirmed) == "table"
			and confirmed.catalogId == item.catalogId
			and type(confirmed.loss) == "number"
			and loss <= confirmed.loss
		if loss > 0 and not accepted then
			return false, VaultRules.WOULD_OVERFLOW
		end
		VaultRules.BankMaterial(profile, item.catalogId, amount, now or 0)
		if amount >= owned then
			table.remove(slots, backpackIndex)
		else
			item.quantity = owned - amount
		end
		return true, nil
	end
	local vaultItems = profile.vault.items
	if item.instanceId == nil and ItemCatalog.IsStackable(item.catalogId) then
		-- A stack tops up the vault's stacks of its type first (InventoryRules.Land),
		-- so it needs a free slot only for what they cannot take.
		local merges = InventoryRules.TopUpRoom(vaultItems, item.catalogId) >= amount
		if not merges and #vaultItems >= VaultRules.ItemCapacity(profile) then
			return false, "VaultFull"
		end
		local part = table.clone(item)
		part.quantity = amount
		InventoryRules.Land(vaultItems, part)
		if amount >= owned then
			table.remove(slots, backpackIndex)
		else
			item.quantity = owned - amount
		end
		return true, nil
	end
	if #vaultItems >= VaultRules.ItemCapacity(profile) then
		return false, "VaultFull"
	end
	if amount < owned then
		local part = table.clone(item)
		part.quantity = amount
		table.insert(vaultItems, part)
		item.quantity = owned - amount
		return true, nil
	end
	if item.instanceId then
		item.location = "Vault"
	end
	table.insert(profile.vault.items, item)
	table.remove(slots, backpackIndex)
	return true, nil
end

-- Moves one vault item back into the lobby backpack.
function VaultRules.WithdrawItem(profile, vaultIndex: number)
	local item = profile.vault.items[vaultIndex]
	if item == nil then
		return false, "Empty"
	end
	if ExtractionRules.AddToLobbyBackpack(profile.lobbyBackpack.slots, table.clone(item)) > 0 then
		return false, "BackpackFull"
	end
	table.remove(profile.vault.items, vaultIndex)
	return true, nil
end

-- Moves `quantity` of a vaulted material into the lobby backpack, all or nothing
-- (GDD §53). Returns (ok, reason).
function VaultRules.WithdrawMaterial(profile, catalogId: string, quantity: number)
	local current = profile.vault.materials[catalogId] or 0
	if quantity <= 0 or quantity % 1 ~= 0 or quantity > current then
		return false, "NotEnough"
	end
	local trial = table.clone(profile.lobbyBackpack.slots)
	for index, slot in trial do
		trial[index] = table.clone(slot)
	end
	if ExtractionRules.AddToLobbyBackpack(trial, { catalogId = catalogId, quantity = quantity }) > 0 then
		return false, "BackpackFull"
	end
	profile.lobbyBackpack.slots = trial
	local remaining = current - quantity
	profile.vault.materials[catalogId] = if remaining > 0 then remaining else nil
	return true, nil
end

return VaultRules
