-- Eating and drinking from the hand (GDD §59). A consumable's hotbar slot is held
-- like a tool (InventoryController equips it); the attack input (click, the touch
-- attack button or RT, CombatController) then asks the server to use it, one item
-- per press: holding the button does not repeat, and a press while a use is
-- running or waiting for the server does nothing. The server (HealingService)
-- decides everything and answers once the item is applied (medicine at once, food
-- and boosts when the animation ends); its refusals show the usual reason toast,
-- except Busy (a press during the animation) and an interruption (the player put
-- the item away or picked another slot), which are silent. Food and boosts
-- confirm with the server's toast.
--
-- While a use runs, the server's ConsumeItem/ConsumeStart/ConsumeEnd player
-- attributes drive, on every client, a procedural eat or drink pose on that
-- character (no animation asset): each frame, after the animations, the R6 right
-- shoulder is turned to bring the held item to the mouth (ConsumeRules.Pose),
-- blended over whatever the arm was doing, so walking and the hold pose carry on
-- underneath and the arm eases back down when the use ends or stops. The local
-- player also gets a kit progress bar ("Eating Cooked Meat") below the screen
-- centre, where the bow draw bar sits (only one item is held at a time). World
-- place only.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local ConsumeRules = require(ReplicatedStorage.Shared.Survival.ConsumeRules)
local Consumables = require(ReplicatedStorage.Shared.Items.Consumables)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Kit = require(script.Parent.Parent.Hud.Kit)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

local ConsumeController = {}

-- The progress bar, in design px from the screen centre (CombatController.DRAW's place).
ConsumeController.BAR = { y = 52, w = 300, h = 46 }

local player = Players.LocalPlayer
local pending = false
local hinted = false
local bar = nil
-- poses[player] = {start, style, blend, raise, across, releasedAt?, base?, written?}
local poses = {}

-- True while the local player is eating or drinking (or waiting for the server).
function ConsumeController.IsBusy(): boolean
	return pending or player:GetAttribute(ConsumeRules.ITEM_ATTRIBUTE) ~= nil
end

-- Asks the server to use the held `catalogId` and waits for its answer (food and
-- boosts: until the animation ends). Returns (ok, reason); a press while busy
-- returns (false, "Busy") silently.
function ConsumeController.Use(catalogId: string): (boolean, string?)
	if ConsumeController.IsBusy() then
		return false, "Busy"
	end
	pending = true
	local remote = Remotes.Get("UseConsumable")
	local ok, success, reason = pcall(remote.InvokeServer, remote, HttpService:GenerateGUID(false), catalogId)
	pending = false
	if not ok then
		success, reason = false, "Request failed"
	end
	if not success and reason ~= "Interrupted" and reason ~= "Busy" then
		Kit.Toast.Show({
			kind = "warn",
			title = "Not possible",
			text = "Can't use that now: " .. Reasons.Text(reason),
			duration = 3,
		})
	end
	return success == true, reason
end

-- The first time a consumable is held this session, says how to use it.
function ConsumeController.Hint(catalogId: string)
	local item = Consumables.Get(catalogId)
	if hinted or item == nil then
		return
	end
	hinted = true
	local def = ItemCatalog.Get(catalogId)
	Kit.Toast.Show({
		kind = "info",
		title = def and def.name or item.name,
		text = ConsumeRules.HoldHint(item, Kit.Input.Type()),
		duration = 4,
	})
end

-- The progress bar in `parent` (a HUD-scaled root): returns {frame, Set}.
-- Set(text, fraction, icon) shows it as a kit stat bar (the vitals' look: the
-- item kind's icon, cream words over the orange fill); Set(nil) hides it.
function ConsumeController.MountBar(parent: Instance)
	local spec = ConsumeController.BAR
	local frame = Instance.new("Frame")
	frame.Name = "Consume"
	frame.BackgroundTransparency = 1
	frame.AnchorPoint = Vector2.new(0.5, 0.5)
	frame.Position = UDim2.new(0.5, 0, 0.5, spec.y)
	frame.Size = UDim2.fromOffset(spec.w, spec.h)
	frame.Visible = false
	frame.Parent = parent
	local fill, shownText, shownIcon = nil, nil, nil
	local mounted = { frame = frame }
	function mounted.Set(text: string?, fraction: number?, icon: string?)
		if text == nil then
			frame.Visible = false
			return
		end
		if fill == nil or shownIcon ~= icon then
			if fill then
				fill:Destroy()
			end
			fill = Kit.Bar.new(frame, {
				name = "Progress",
				rect = { 0, 0, spec.w, spec.h },
				fill = "food",
				frame = "stat",
				icon = icon,
				text = text,
			})
			shownIcon, shownText = icon, text
			mounted.bar = fill
		elseif shownText ~= text then
			shownText = text
			fill:SetText(text)
		end
		fill:Set(fraction or 0, true)
		frame.Visible = true
	end
	return mounted
end

local function build()
	local gui = Instance.new("ScreenGui")
	gui.Name = "Consume"
	gui.ResetOnSpawn = false
	gui.DisplayOrder = Kit.Tokens.Order("hud")
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.IgnoreGuiInset = true
	local root = Instance.new("Frame")
	root.Name = "Root"
	root.BackgroundTransparency = 1
	root.Size = UDim2.fromScale(1, 1)
	root.Parent = gui
	bar = ConsumeController.MountBar(root)
	gui.Parent = player:WaitForChild("PlayerGui")
	Kit.Scale.Hud(gui, root)
end

local function updateBar(now: number)
	local catalogId = player:GetAttribute(ConsumeRules.ITEM_ATTRIBUTE)
	local start = player:GetAttribute(ConsumeRules.START_ATTRIBUTE)
	local ends = player:GetAttribute(ConsumeRules.END_ATTRIBUTE)
	local item = Consumables.Get(catalogId)
	if item == nil or type(start) ~= "number" or type(ends) ~= "number" then
		bar.Set(nil)
		return
	end
	bar.Set(ConsumeRules.BarText(item), ConsumeRules.Progress(start, ends, now), ConsumeRules.AttackIcon(item))
end

-- Turns `character`'s right shoulder toward the pose by `blend`, over what the
-- animations set this frame (0 puts that back). The turn is built in torso space
-- about the shoulder joint (raise about the torso's X axis, then across about its
-- Z axis) and moved into the joint's own frame: Transform = C0.Rotation⁻¹ · turn ·
-- C0.Rotation. When no animation writes the joint (the value is still what this
-- wrote last frame), the last animated value stays the base, so the arm always
-- comes back down.
local function pose(record, character: Model?, blend: number)
	local torso = character and character:FindFirstChild("Torso")
	local shoulder = torso and torso:FindFirstChild("Right Shoulder")
	if shoulder == nil or not shoulder:IsA("Motor6D") then
		return
	end
	local current = shoulder.Transform
	if record.written == nil or current ~= record.written then
		record.base = current
	end
	local base = record.base or CFrame.identity
	local written = base
	if blend > 0 then
		local rotation = shoulder.C0.Rotation
		local turn = CFrame.Angles(0, 0, math.rad(record.across)) * CFrame.Angles(math.rad(record.raise), 0, 0)
		written = base:Lerp(rotation:Inverse() * turn * rotation, math.min(blend, 1))
	end
	shoulder.Transform = written
	record.written = written
end

local function stepPoses(now: number)
	for _, other in Players:GetPlayers() do
		local catalogId = other:GetAttribute(ConsumeRules.ITEM_ATTRIBUTE)
		local start = other:GetAttribute(ConsumeRules.START_ATTRIBUTE)
		local ends = other:GetAttribute(ConsumeRules.END_ATTRIBUTE)
		local record = poses[other]
		if catalogId ~= nil and type(start) == "number" and type(ends) == "number" then
			if record == nil or record.start ~= start or record.releasedAt ~= nil then
				record = { start = start, style = ConsumeRules.Style(Consumables.Get(catalogId)) }
				poses[other] = record
			end
			record.blend, record.raise, record.across = ConsumeRules.Pose(record.style, now - start, ends - start)
			pose(record, other.Character, record.blend)
		elseif record then
			-- Ended or interrupted: lower the arm from wherever it was.
			record.releasedAt = record.releasedAt or now
			local blend = ConsumeRules.Release(record.blend or 0, now - record.releasedAt)
			pose(record, other.Character, blend)
			if blend <= 0 then
				poses[other] = nil
			end
		end
	end
end

function ConsumeController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	RunService.RenderStepped:Connect(function()
		updateBar(workspace:GetServerTimeNow())
	end)
	-- After the animations each frame (PreSimulation), so the pose wins over the
	-- walk and hold tracks; Stepped where PreSimulation is missing.
	local ok, afterAnimation = pcall(function()
		return RunService.PreSimulation
	end)
	if not ok or afterAnimation == nil then
		afterAnimation = RunService.Stepped
	end
	afterAnimation:Connect(function()
		stepPoses(workspace:GetServerTimeNow())
	end)
	Players.PlayerRemoving:Connect(function(other)
		poses[other] = nil
	end)
end

return ConsumeController
