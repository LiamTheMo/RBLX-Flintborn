-- The first-session tutorial (GDD §25.5, §36.5, Q59), in the proposed learning
-- order. Each step completes from a server-observed trigger; "ack" steps are short
-- explanations the player confirms and never pay a reward. Rewards are small and
-- never Permanent gear. Hints are placeholders for the copy pass.

local TutorialSteps = {}

TutorialSteps.Steps = {
	{
		id = "Play",
		title = "Enter the world safely",
		hint = "Press Play in the world menu. You are safe until you spawn at a random spot on the island.",
		trigger = "RunStarted",
	},
	{
		id = "Survive",
		title = "Health, food and stamina",
		hint = "Health does not regenerate. Food drains over 60 minutes; under 25% you slow down. Hold {Sprint} to sprint; stamina lasts 3 seconds.",
		trigger = "Ack",
	},
	{
		id = "Gather",
		title = "Gather materials",
		hint = "Walk up to a tree, rock or plant and hold {Interact} at the prompt. Better tools gather more.",
		trigger = "Harvest",
		reward = { xp = "Harvest" },
	},
	{
		id = "Craft",
		title = "Craft arrows or a tool",
		hint = "Press {Craft} to open crafting. Arrows come in tens and need wood and fiber.",
		trigger = "Craft",
	},
	{
		id = "Heal",
		title = "Heal up",
		hint = "Medicine heals instantly; food heals over 10 seconds and is halved if you are hit. Press its hotbar number to use it.",
		trigger = "Heal",
	},
	{
		id = "Tribes",
		title = "Tribes, revives and raids",
		hint = "Party up in the lobby to arrive as a tribe. Tribe members go down instead of dying and can be revived. Bases outlive you and can be raided any time.",
		trigger = "Ack",
	},
	{
		id = "Events",
		title = "Public events",
		hint = "Events are announced to everyone. Open a cache, harvest a rare node or defeat a creature — but others are coming too.",
		trigger = "Event",
	},
	{
		id = "Extract",
		title = "Extract",
		hint = "Start a portal: it counts down 120 seconds for everyone. Be alive and inside the zone at zero. The Center portal doubles materials.",
		trigger = "Extract",
		reward = { coins = 250 },
	},
	{
		id = "Vault",
		title = "The vault keeps everything",
		hint = "In the lobby open the Vault. Materials are already vaulted; deposit gear from your lobby backpack. Anything left in the backpack goes with you on Play.",
		trigger = "Vault",
	},
	{
		id = "Economy",
		title = "Coins, Gems, the Forge and progress",
		hint = "In the lobby, Market opens the shop, merchant and quests and the Forge makes Permanent items that survive death. {Progression} shows your level, masteries and rebirth.",
		trigger = "Ack",
	},
}

TutorialSteps.Index = {}
for index, step in TutorialSteps.Steps do
	TutorialSteps.Index[step.id] = index
end

-- Gameplay actions that complete a trigger.
TutorialSteps.ACTION_TRIGGERS = {
	Harvest = "Harvest",
	Craft = "Craft",
	Cache = "Event",
	RareNode = "Event",
	MeteorChunk = "Event",
	Enemy = "Event",
	Elite = "Event",
}

-- Advances `state` ({step, rewardsGranted, skipped, everSkipped, completedAt})
-- when `trigger` matches the current step. Returns the completed step, or nil.
function TutorialSteps.Advance(state, trigger: string, now: number)
	if state.skipped or state.completedAt then
		return nil
	end
	local step = TutorialSteps.Steps[state.step]
	if step == nil or step.trigger ~= trigger then
		return nil
	end
	state.step += 1
	if state.step > #TutorialSteps.Steps then
		state.completedAt = now
	end
	return step
end

-- True the first time a step's reward may be paid (never after any skip, even
-- one followed by a replay).
function TutorialSteps.ClaimReward(state, step): boolean
	if step.reward == nil or state.skipped or state.everSkipped or state.rewardsGranted[step.id] then
		return false
	end
	state.rewardsGranted[step.id] = true
	return true
end

-- Skipping is allowed once the safe Play step is done; it never pays.
function TutorialSteps.Skip(state): boolean
	if state.step <= 1 or state.completedAt then
		return false
	end
	state.skipped = true
	state.everSkipped = true
	return true
end

-- Replays from the start; rewards already paid stay paid (never twice), and a
-- skip stays on record so a replay cannot unlock rewards.
function TutorialSteps.Replay(state)
	-- Saves from before skips were remembered carry only `skipped`.
	state.everSkipped = state.everSkipped == true or state.skipped == true
	state.step = 1
	state.skipped = false
	state.completedAt = nil
end

return TutorialSteps
