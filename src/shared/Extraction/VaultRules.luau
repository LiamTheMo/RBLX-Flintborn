-- The secure vault (GDD §10.3, Q96, Q122, Q151, Q154). 25 item slots (+25 per
-- upgrade, v0.14) and material storage of up to 1,000 per stack. Deposits are
-- manual and are refused when there is no room, never deleted. Item withdrawals go
-- to the lobby backpack, which deploys on the next Play (Q155); materials never
-- leave the vault for a run.

local GameConstants = require(script.Parent.Parent.GameConstants)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local ExtractionRules = require(script.Parent.ExtractionRules)

local VaultRules = {}

function VaultRules.ItemCapacity(profile): number
	return GameConstants.VaultSlots(profile.vault.upgradeTier or 0)
end

-- Moves one lobby backpack slot into the vault. Returns (ok, reason).
function VaultRules.Deposit(profile, backpackIndex: number)
	local slots = profile.lobbyBackpack.slots
	local item = slots[backpackIndex]
	if item == nil then
		return false, "Empty"
	end
	if item.instanceId == nil and ItemCatalog.IsMaterial(item.catalogId) then
		local current = profile.vault.materials[item.catalogId] or 0
		if current + item.quantity > GameConstants.MATERIAL_STACK_MAX then
			return false, "VaultStackFull"
		end
		profile.vault.materials[item.catalogId] = current + item.quantity
	else
		if #profile.vault.items >= VaultRules.ItemCapacity(profile) then
			return false, "VaultFull"
		end
		if item.instanceId then
			item.location = "Vault"
		end
		table.insert(profile.vault.items, item)
	end
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

return VaultRules
