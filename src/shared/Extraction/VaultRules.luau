-- The secure vault (GDD §10.3, Q96, Q122, Q151, Q154, Q164). 25 item slots (+25
-- per upgrade, v0.14) and material storage of up to 1,000 per type. Item deposits
-- are manual and are refused when there is no room, never deleted. Item
-- withdrawals go to the lobby backpack, which deploys on the next Play (Q155).
-- Materials live only in the vault: any that reach the lobby backpack bank at
-- once (BankMaterials), anything over the capacity is deleted, and they never
-- come back out.

local GameConstants = require(script.Parent.Parent.GameConstants)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local ExtractionRules = require(script.Parent.ExtractionRules)

local VaultRules = {}

function VaultRules.ItemCapacity(profile): number
	return GameConstants.VaultSlots(profile.vault.upgradeTier or 0)
end

-- Banks every material stack in the lobby backpack into the vault, deleting what
-- exceeds the vault's material capacity. Runs after every profile operation and
-- on load, so the backpack never holds a material. Returns {catalogId = deleted}
-- (empty when nothing was lost) and records any loss on `vault.lastOverflow`.
function VaultRules.BankMaterials(profile, now: number)
	local slots = profile.lobbyBackpack.slots
	local materials = profile.vault.materials
	local deleted, lost = {}, false
	for index = #slots, 1, -1 do
		local item = slots[index]
		if item.instanceId == nil and ItemCatalog.IsMaterial(item.catalogId) then
			local current = materials[item.catalogId] or 0
			local stored, over = GameConstants.SettleMaterialStack(current, math.max(0, item.quantity or 0))
			materials[item.catalogId] = if stored > 0 then stored else nil
			if over > 0 then
				deleted[item.catalogId] = (deleted[item.catalogId] or 0) + over
				lost = true
			end
			table.remove(slots, index)
		end
	end
	if lost then
		profile.vault.lastOverflow = { at = now, deleted = deleted }
	end
	return deleted
end

-- Moves one lobby backpack item into the vault. Returns (ok, reason).
function VaultRules.Deposit(profile, backpackIndex: number)
	local slots = profile.lobbyBackpack.slots
	local item = slots[backpackIndex]
	if item == nil then
		return false, "Empty"
	end
	if item.instanceId == nil and ItemCatalog.IsMaterial(item.catalogId) then
		-- Never an item slot: the sweep after this operation banks it.
		return false, "MaterialsBankAutomatically"
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

return VaultRules
