-- Reports how the HUD's images are loading on this device (diagnostics for the
-- parchment UI on phones). Thirty seconds and two minutes after joining, the
-- client sends SpriteLoader's summary (image counts, the engine's fetch state
-- per image, the images that have not shown) and its screen and input kind; the
-- server keeps the latest few for the "Probe UI images" workflow to read. No
-- personal information is sent.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local UiAssets = require(ReplicatedStorage.Shared.UI.UiAssets)
local SpriteLoader = require(script.Parent.Parent.Hud.SpriteLoader)

local UiDiagnosticsController = {}

UiDiagnosticsController.AFTER = { 30, 120 }
UiDiagnosticsController.MAX_LINES = 40

local function nameOf(ids: { [string]: string }, line: string): string
	local id = string.match(line, "^(%S+)")
	return (id and ids[id] or "?") .. " " .. line
end

local function report(seconds: number)
	local counts, statuses, lines = SpriteLoader.Summary(UiDiagnosticsController.MAX_LINES)
	local states = {}
	for status, count in statuses do
		table.insert(states, status .. "=" .. count)
	end
	table.sort(states)
	local camera = workspace.CurrentCamera
	local viewport = if camera then camera.ViewportSize else Vector2.zero
	local summary = ("%s t=%ds labels=%d pending=%d loaded=%d ids[%s] touch=%s keyboard=%s screen=%dx%d"):format(
		PlaceConfig.Role(),
		seconds,
		counts.labels,
		counts.pending,
		counts.loaded,
		table.concat(states, " "),
		tostring(UserInputService.TouchEnabled),
		tostring(UserInputService.KeyboardEnabled),
		viewport.X,
		viewport.Y
	)
	-- Sprite names make the lines readable.
	local names = {}
	for name, id in UiAssets.Ids do
		names[id] = name
	end
	local named = {}
	for _, line in lines do
		table.insert(named, string.sub(nameOf(names, line), 1, 200))
	end
	pcall(function()
		Remotes.Get("ReportUiImages"):FireServer(string.sub(summary, 1, 250), named)
	end)
end

function UiDiagnosticsController.Start()
	if Players.LocalPlayer == nil then
		return
	end
	local started = os.clock()
	for _, seconds in UiDiagnosticsController.AFTER do
		task.delay(seconds, function()
			report(math.floor(os.clock() - started))
		end)
	end
end

return UiDiagnosticsController
