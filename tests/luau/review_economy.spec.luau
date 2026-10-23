-- Economy review: saves made before the permanent redemption ledger and the
-- remembered tutorial skip must not reopen the exploits those records close.
local Server = game:GetService("ServerScriptService").Server
local Shared = game:GetService("ReplicatedStorage").Shared
local EconomyRules = require(Shared.Economy.EconomyRules)
local OperationJournal = require(Server.Infrastructure.OperationJournal)
local ProfileSchema = require(Shared.Data.ProfileSchema)
local TutorialSteps = require(Shared.Tutorial.TutorialSteps)

local function strict(apply)
	return function(working)
		local ok, reason = apply(working)
		if not ok then
			error(reason, 0)
		end
		return reason
	end
end

local function flushJournal(profile)
	for index = 1, OperationJournal.RETENTION + 5 do
		OperationJournal.Run(profile, "filler:" .. index, "Filler", index, function() end)
	end
end

-- A save from before the ledger: the redemption lives only in the journal.
local function legacyRedeemedSave()
	local saved = ProfileSchema.Default(0)
	saved.currency.redeemedCodes = nil
	saved.currency.gems = 25
	saved.operations.records["code:FLINTBORN-LAUNCH"] =
		{ kind = "CodeRedeem", status = "committed", at = 1, result = nil }
	table.insert(saved.operations.order, "code:FLINTBORN-LAUNCH")
	return saved
end

test("a code redeemed before the ledger existed stays redeemed after the journal trims", function()
	local profile, problem = ProfileSchema.Migrate(legacyRedeemedSave(), 0)
	expectEq(problem, nil, "loads")
	flushJournal(profile)
	expectEq(OperationJournal.Get(profile, "code:FLINTBORN-LAUNCH"), nil, "journal trimmed")
	local ok, reason = pcall(
		OperationJournal.Run,
		profile,
		"code:FLINTBORN-LAUNCH",
		"CodeRedeem",
		9,
		strict(function(working)
			return EconomyRules.RedeemCode(working, "FLINTBORN-LAUNCH", { gems = 25 }, 9)
		end)
	)
	expect(not ok and reason == "AlreadyRedeemed", "the old redemption still counts")
	expectEq(profile.currency.gems, 25, "25 Gems once")
end)

test("only committed code redemptions are copied into the ledger", function()
	local saved = legacyRedeemedSave()
	saved.operations.records["code:FLINTBORN-LAUNCH"] = nil
	saved.operations.records["buy:code:x"] = { kind = "ShopBuy", status = "committed", at = 1 }
	saved.operations.records["code:FLINTBORN-RESPEC"] = { kind = "CodeRedeem", status = "pending", at = 1 }
	local profile = ProfileSchema.Migrate(saved, 0)
	expectEq(next(profile.currency.redeemedCodes), nil, "nothing redeemed")
end)

test("a tutorial skipped before skips were remembered still pays nothing after a replay", function()
	local saved = ProfileSchema.Default(0)
	saved.tutorial = { step = 2, skipped = true, completedAt = nil, rewardsGranted = {} }
	local profile = ProfileSchema.Migrate(saved, 0)
	local state = profile.tutorial
	local extract = TutorialSteps.Steps[TutorialSteps.Index.Extract]
	TutorialSteps.Replay(state)
	expect(not state.skipped, "the replay runs")
	expect(not TutorialSteps.ClaimReward(state, extract), "but never pays a skipper")
end)
