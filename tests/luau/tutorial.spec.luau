local Shared = game:GetService("ReplicatedStorage").Shared
local ItemCatalog = require(Shared.Items.ItemCatalog)
local ProfileSchema = require(Shared.Data.ProfileSchema)
local TutorialSteps = require(Shared.Tutorial.TutorialSteps)

test("steps follow the learning order and each has a completion trigger", function()
	local order = {}
	for _, step in TutorialSteps.Steps do
		expect(type(step.trigger) == "string" and #step.trigger > 0, step.id .. " trigger")
		expect(type(step.hint) == "string" and #step.hint > 20, step.id .. " hint")
		table.insert(order, step.id)
	end
	expectEq(order[1], "Play", "safe Play first")
	expect(TutorialSteps.Index.Extract < TutorialSteps.Index.Vault, "extract before the vault")
	expect(TutorialSteps.Index.Gather < TutorialSteps.Index.Craft, "gather before crafting")
end)

test("steps complete only in order and from their own trigger", function()
	local state = ProfileSchema.Default(0).tutorial
	expectEq(TutorialSteps.Advance(state, "Harvest", 1), nil, "cannot skip ahead")
	expectEq(TutorialSteps.Advance(state, "RunStarted", 1).id, "Play", "Play done")
	expectEq(TutorialSteps.Advance(state, "Harvest", 2), nil, "the next step is an explanation")
	expectEq(TutorialSteps.Advance(state, "Ack", 2).id, "Survive", "acknowledged")
	expectEq(TutorialSteps.Advance(state, "Harvest", 3).id, "Gather", "gathered")
end)

test("rewards are granted once, never after a skip, and replay never pays twice", function()
	local state = ProfileSchema.Default(0).tutorial
	local extract = TutorialSteps.Steps[TutorialSteps.Index.Extract]
	expect(TutorialSteps.ClaimReward(state, extract), "first time")
	expect(not TutorialSteps.ClaimReward(state, extract), "never twice")
	TutorialSteps.Replay(state)
	expect(not TutorialSteps.ClaimReward(state, extract), "replay does not pay again")
	local fresh = ProfileSchema.Default(0).tutorial
	expect(not TutorialSteps.Skip(fresh), "the safe Play step cannot be skipped")
	TutorialSteps.Advance(fresh, "RunStarted", 1)
	expect(TutorialSteps.Skip(fresh), "skippable afterwards")
	expect(not TutorialSteps.ClaimReward(fresh, extract), "skipping never grants rewards")
end)

test("no step grants a Permanent item or more than 25 Gems", function()
	for _, step in TutorialSteps.Steps do
		local reward = step.reward or {}
		expect(reward.item == nil or not ItemCatalog.Get(reward.item).permanent, step.id .. " no Permanent gear")
		expect(reward.permanent == nil, step.id .. " no Permanent conversion")
		expect((reward.gems or 0) <= 25, step.id .. " gems")
		expect((reward.coins or 0) <= 250, step.id .. " easy-tier Coins at most")
	end
end)
