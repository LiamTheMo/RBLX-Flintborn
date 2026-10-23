-- Downed overlay (GDD §5.3, §25.4): the bleed-out timer (marked paused while a
-- revive runs), downed health, who is reviving and their progress. Crawling uses
-- normal movement at the server's crawl speed. World place only.

local GameConstants = require(game:GetService("ReplicatedStorage").Shared.GameConstants)
local PlaceConfig = require(game:GetService("ReplicatedStorage").Shared.Config.PlaceConfig)
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local Theme = require(script.Parent.Parent.Ui.Theme)

local DownedController = {}

local player = Players.LocalPlayer
local ui = {}

local function build()
	-- Lives in the shared top-centre column so it never covers the other banners.
	ui.frame = Instance.new("Frame")
	ui.frame.Name = "Downed"
	ui.frame.LayoutOrder = Theme.TopOrder.Downed
	ui.frame.Size = UDim2.fromOffset(420, 96)
	ui.frame.BackgroundColor3 = Color3.fromRGB(80, 24, 20)
	ui.frame.BackgroundTransparency = 0.15
	ui.frame.Visible = false
	ui.frame.Parent = Theme.TopStack()
	Instance.new("UICorner").Parent = ui.frame
	ui.text = Instance.new("TextLabel")
	ui.text.Size = UDim2.fromScale(1, 1)
	ui.text.BackgroundTransparency = 1
	ui.text.TextColor3 = Color3.fromRGB(255, 240, 230)
	ui.text.Font = Enum.Font.GothamBold
	ui.text.TextSize = 16
	ui.text.TextWrapped = true
	ui.text.Parent = ui.frame
end

local function update()
	local isDowned = player:GetAttribute("Downed") == true
	ui.frame.Visible = isDowned
	if not isDowned then
		return
	end
	local remaining = player:GetAttribute("DownedRemaining") or 0
	local health = player:GetAttribute("DownedHealth") or 0
	local reviver = player:GetAttribute("DownedReviver")
	local progress = player:GetAttribute("DownedReviveProgress") or 0
	local lines = { ("✚ DOWNED — %d HP left"):format(health) }
	if reviver then
		table.insert(lines, ("Bleed-out PAUSED at %d s"):format(remaining))
		table.insert(lines, ("%s is reviving you: %.1f / %d s"):format(reviver, progress, GameConstants.REVIVE_SECONDS))
	else
		table.insert(lines, ("Bleeding out in %d s — anyone can revive you"):format(remaining))
	end
	table.insert(lines, "You can crawl slowly but cannot heal.")
	ui.text.Text = table.concat(lines, "\n")
end

function DownedController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	RunService.RenderStepped:Connect(update)
end

return DownedController
