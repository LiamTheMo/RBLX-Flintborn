-- Server-validated long interactions on a ProximityPrompt (GDD §7.4). The prompt's
-- hold is the channel; the server records when each player began holding and only
-- accepts completion after the full time. Releasing early, leaving range or taking
-- damage (Channel.Interrupt) restarts it from zero.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local EventRules = require(ReplicatedStorage.Shared.Events.EventRules)

local Channel = {}

local active = {}

-- canUse(player) -> boolean; onComplete(player); onInterrupted(player)?
function Channel.Attach(prompt: ProximityPrompt, seconds: number, canUse, onComplete, onInterrupted)
	local started = {}
	active[started] = true
	prompt.HoldDuration = seconds
	prompt.PromptButtonHoldBegan:Connect(function(player)
		started[player] = if canUse(player) then os.clock() else nil
	end)
	prompt.PromptButtonHoldEnded:Connect(function(player)
		-- An early release interrupts; the end of a full hold may arrive either side
		-- of Triggered, so only a short hold clears the record.
		if not EventRules.ChannelComplete(started[player], os.clock(), seconds) then
			started[player] = nil
		end
	end)
	prompt.Triggered:Connect(function(player)
		local startedAt = started[player]
		started[player] = nil
		if canUse(player) and EventRules.ChannelComplete(startedAt, os.clock(), seconds) then
			onComplete(player)
		elseif onInterrupted then
			onInterrupted(player)
		end
	end)
	prompt.Destroying:Connect(function()
		active[started] = nil
	end)
end

-- Restarts every channel `player` is holding (they were hit).
function Channel.Interrupt(player: Player)
	for started in active do
		started[player] = nil
	end
end

return Channel
