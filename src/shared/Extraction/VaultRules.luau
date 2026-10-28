-- The secure vault (GDD §10.3, §53, Q96, Q122, Q151, Q154). 25 item slots (+25
-- per upgrade, v0.14) and material storage of up to 1,000 per type. Item deposits
-- are manual and are refused when there is no room, never deleted. Material
-- deposits always go in: anything over the capacity is deleted (GDD §53). Item
-- and material withdrawals go to the lobby backpack, which deploys on the next
-- Play (Q155), materials included (GDD §53).

local GameConstants = require(script.Parent.Parent.GameConstants)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local ExtractionRules = require(script.Parent.ExtractionRules)

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

-- Moves one lobby backpack slot into the vault. Returns (ok, reason). A material
-- stack banks whole, past the capacity included (BankMaterial).
function VaultRules.Deposit(profile, backpackIndex: number, now: number?)
	local slots = profile.lobbyBackpack.slots
	local item = slots[backpackIndex]
	if item == nil then
		return false, "Empty"
	end
	if item.instanceId == nil and ItemCatalog.IsMaterial(item.catalogId) then
		VaultRules.BankMaterial(profile, item.catalogId, item.quantity or 0, now or 0)
		table.remove(slots, backpackIndex)
		return true, nil
	end
	if #profile.vault.items >= VaultRules.ItemCapacity(profile) then
		return false, "VaultFull"
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
