-- Tweens from the motion tokens. Motion.Play cancels the tween already running
-- on the same instance and property before starting the next, so state changes
-- never stack. With reduced motion (the player's setting or the device's),
-- moves and scales land at once and fades take at most the reducedFade time.

local GuiService = game:GetService("GuiService")
local TweenService = game:GetService("TweenService")

local Theme = require(script.Parent.Parent.Parent.Ui.Theme)
local Tokens = require(script.Parent.Tokens)

local Motion = {}

-- instance -> property -> running Tween. Weak keys: a destroyed instance that
-- nothing else holds drops out.
local running: { [Instance]: { [string]: Tween } } = setmetatable({}, { __mode = "k" }) :: any

local FADES = {
	BackgroundTransparency = true,
	ImageTransparency = true,
	TextTransparency = true,
	Transparency = true,
	GroupTransparency = true,
}

function Motion.Reduced(): boolean
	local ok, reduced = pcall(Theme.ReducedMotion)
	if ok and reduced then
		return true
	end
	local deviceOk, device = pcall(function()
		return GuiService.ReducedMotionEnabled
	end)
	return deviceOk and device == true
end

local function cancel(instance: Instance, property: string)
	local byProp = running[instance]
	local tween = byProp and byProp[property]
	if tween then
		byProp[property] = nil
		tween:Cancel()
	end
end

-- Tweens `instance` to `goal` with the motion token `key`. Returns the tween,
-- or nil when it landed at once. `onDone` runs when it completes (not when it
-- is cancelled), or at once when nothing tweens.
function Motion.Play(instance: Instance, key: string, goal: { [string]: any }, onDone: (() -> ())?): Tween?
	local reduced = Motion.Reduced()
	local fades, moves = {}, {}
	for property, value in goal do
		cancel(instance, property)
		if FADES[property] then
			fades[property] = value
		else
			moves[property] = value
		end
	end
	local info = Tokens.Motion(key)
	if reduced then
		for property, value in moves do
			(instance :: any)[property] = value
		end
		moves = {}
		info = Tokens.Motion("reducedFade")
	end
	local all = {}
	for property, value in fades do
		all[property] = value
	end
	for property, value in moves do
		all[property] = value
	end
	if next(all) == nil then
		if onDone then
			onDone()
		end
		return nil
	end
	local tween = TweenService:Create(instance, info, all)
	running[instance] = running[instance] or {}
	for property in all do
		running[instance][property] = tween
	end
	tween.Completed:Connect(function(state)
		if onDone and state == Enum.PlaybackState.Completed then
			onDone()
		end
		local byProp = running[instance]
		if byProp then
			for property in all do
				if byProp[property] == tween then
					byProp[property] = nil
				end
			end
		end
	end)
	tween:Play()
	return tween
end

-- Sets `goal` at once, cancelling any running tween on those properties.
function Motion.Set(instance: Instance, goal: { [string]: any })
	for property, value in goal do
		cancel(instance, property)
		(instance :: any)[property] = value
	end
end

-- Cancels every running tween on `instance`.
function Motion.Stop(instance: Instance)
	local byProp = running[instance]
	if byProp then
		running[instance] = nil
		for _, tween in byProp do
			tween:Cancel()
		end
	end
end

-- A repeating, reversing transparency pulse (a key cap waiting for a key).
-- Returns a function that stops it and restores `rest`.
function Motion.Pulse(instance: Instance, property: string, low: number, rest: number): () -> ()
	if Motion.Reduced() then
		(instance :: any)[property] = rest
		return function() end
	end
	local spec = Tokens.Data.motion.pulse
	local info = TweenInfo.new(spec.time, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true)
	cancel(instance, property)
	local tween = TweenService:Create(instance, info, { [property] = low })
	running[instance] = running[instance] or {}
	running[instance][property] = tween
	tween:Play()
	return function()
		cancel(instance, property);
		(instance :: any)[property] = rest
	end
end

return Motion
