-- Robux developer products (GDD §36, §38.1). ProcessReceipt fulfils each purchase
-- exactly once through an operation keyed by its PurchaseId, backed by a permanent
-- entitlement record, so retries and server restarts never grant twice; it
-- reports success only after the grant is committed and saved. Every offer has an
-- earnable route (OfferCatalog).

local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local EconomyRules = require(ReplicatedStorage.Shared.Economy.EconomyRules)
local OfferCatalog = require(ReplicatedStorage.Shared.Economy.OfferCatalog)
local CurrencyService = require(script.Parent.CurrencyService)
local ProfileService = require(script.Parent.ProfileService)
local ProgressionService = require(script.Parent.ProgressionService)

local PurchaseService = {}

local function processReceipt(receipt)
	local player = Players:GetPlayerByUserId(receipt.PlayerId)
	local offer = OfferCatalog.ByProduct[receipt.ProductId]
	if player == nil or offer == nil or ProfileService.GetProfile(player) == nil then
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
	local ok = ProfileService.RunOperation(player, "purchase:" .. receipt.PurchaseId, "Purchase", function(profile)
		return EconomyRules.FulfilPurchase(profile, receipt.PurchaseId, offer, receipt.ProductId, os.time())
	end)
	if not ok then
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
	local saved = ProfileService.SaveNow(player)
	if not saved then
		-- Committed in memory; Roblox retries and the journal makes that a no-op.
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
	CurrencyService.Publish(player)
	ProgressionService.Publish(player)
	return Enum.ProductPurchaseDecision.PurchaseGranted
end

function PurchaseService.Start()
	MarketplaceService.ProcessReceipt = processReceipt
end

return PurchaseService
