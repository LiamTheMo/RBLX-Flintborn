-- Server-validated long interactions on a ProximityPrompt (GDD §7.4). The prompt's
-- hold is the channel; the server records when each player began holding and only
-- accepts completion after the full time. Releasing early, leaving range or taking
-- damage (Channel.Interrupt) restarts it from zero. The server does not wait for
-- the client to report a release: every POLL_SECONDS it re-checks each holder and
-- interrupts anyone who can no longer use the prompt, briefly disabling the prompt
-- so the client's hold bar resets too.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local EventRules = require(ReplicatedStorage.Shared.Events.EventRules)

local Channel = {}

Channel.POLL_SECONDS = 0.25
-- How long an interrupted prompt stays disabled so the client drops its hold.
Channel.RESET_SECONDS = 0.1

local active = {}
local polling = false

-- Re-enables `prompt` after RESET_SECONDS (replaceable in specs).
Channel.Schedule = function(seconds: number, callback)
	task.delay(seconds, callback)
end

-- Stops `player`'s channel on `channel` and resets the prompt's hold bar.
local function interrupt(channel, player: Player)
	if channel.started[player] == nil then
		return
	end
	channel.started[player] = nil
	local prompt = channel.prompt
	-- Toggling the prompt resets every holder's bar, so only when nobody else holds it.
	if prompt.Enabled and next(channel.started) == nil then
		prompt.Enabled = false
		Channel.Schedule(Channel.RESET_SECONDS, function()
			if active[channel] then
				prompt.Enabled = true
			end
		end)
	end
	if channel.onInterrupted then
		channel.onInterrupted(player)
	end
end

-- One pass over every holder: anyone who can no longer use their prompt (walked
-- off, went down, left the run) is interrupted.
function Channel.Poll()
	for channel in active do
		for player in channel.started do
			if not channel.canUse(player) then
				interrupt(channel, player)
			end
		end
	end
end

-- Forgets a departed player everywhere, without notifying them.
function Channel.Forget(player: Player)
	for channel in active do
		channel.started[player] = nil
	end
end

local function startPolling()
	if polling then
		return
	end
	polling = true
	game:GetService("Players").PlayerRemoving:Connect(Channel.Forget)
	task.spawn(function()
		while true do
			task.wait(Channel.POLL_SECONDS)
			local ok, err = pcall(Channel.Poll)
			if not ok then
				warn("[Channel] Poll failed: " .. tostring(err))
			end
		end
	end)
end

-- canUse(player) -> boolean; onComplete(player); onInterrupted(player)?
function Channel.Attach(prompt: ProximityPrompt, seconds: number, canUse, onComplete, onInterrupted)
	local channel = { prompt = prompt, started = {}, canUse = canUse, onInterrupted = onInterrupted }
	local started = channel.started
	active[channel] = true
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
		active[channel] = nil
	end)
	if task then
		startPolling()
	end
	return channel
end

-- Restarts every channel `player` is holding (they were hit).
function Channel.Interrupt(player: Player)
	for channel in active do
		interrupt(channel, player)
	end
end

return Channel
