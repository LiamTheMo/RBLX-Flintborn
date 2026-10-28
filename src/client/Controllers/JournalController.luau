-- The Journal (GDD §10.1, §25): quests with their progress and rewards, and the
-- painted island map (Hud/JournalPanel). The lobby's Quests button opens it.
-- Quests come from the QuestView remote, refreshed while the Journal is open;
-- CLAIM pays a finished quest through QuestClaim.

local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local JournalPanel = require(script.Parent.Parent.Hud.JournalPanel)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

local JournalController = {}

JournalController.REFRESH_SECONDS = 5

local player = Players.LocalPlayer
local panel = nil
-- Bumped on every open and close, so a refresh loop or a reply from an earlier
-- opening drops out.
local session = 0

local CLOSE_ACTION = "FlintbornJournalClose"

local function invoke(name: string, ...)
	local ok, a, b = pcall(function(...)
		return Remotes.Get(name):InvokeServer(...)
	end, ...)
	if not ok then
		return nil, "Request failed"
	end
	return a, b
end

local function refresh(token: number)
	local quests = invoke("QuestView")
	if token == session and type(quests) == "table" then
		panel:SetQuests(quests)
	end
end

local function close()
	session += 1
	ContextActionService:UnbindAction(CLOSE_ACTION)
	local selected = GuiService.SelectedObject
	if selected and selected:IsDescendantOf(panel.screen.gui) then
		GuiService.SelectedObject = nil
	end
	panel.screen:SetOpen(false)
end

local function claim(questId: string)
	local token = session
	panel:SetClaiming(true)
	local ok, reason = invoke("QuestClaim", questId)
	if token ~= session then
		return
	end
	panel:SetClaiming(false)
	panel:SetMessage(if ok then "Reward claimed." else Reasons.Text(reason))
	refresh(token)
end

function JournalController.Toggle()
	if panel.screen:IsOpen() then
		close()
		return
	end
	session += 1
	local token = session
	panel:SetMessage("")
	panel.screen:SetOpen(true)
	ContextActionService:BindAction(CLOSE_ACTION, function(_, state)
		if state == Enum.UserInputState.Begin then
			close()
		end
		return Enum.ContextActionResult.Sink
	end, false, Enum.KeyCode.ButtonB)
	if GuiService.SelectedObject ~= nil or UserInputService.GamepadEnabled then
		GuiService.SelectedObject = panel.tabs[panel.tab].button
	end
	task.spawn(function()
		while token == session do
			refresh(token)
			task.wait(JournalController.REFRESH_SECONDS)
		end
	end)
end

function JournalController.Start()
	panel = JournalPanel.new(player:WaitForChild("PlayerGui"), {
		onClose = close,
		onClaim = function(questId: string)
			task.spawn(claim, questId)
		end,
	})
	panel.screen:Watch()
end

return JournalController
