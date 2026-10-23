-- Admin commands (GDD §30, Q161b). Every kick command is a safe kick: held items
-- are saved to maintenance escrow first and the player is told on their next visit.
-- Usage in chat: "/safekick <name>" or "/safekick all". Admins come from the
-- server-held list in Config/Admins, never from the client.

local Players = game:GetService("Players")
local TextChatService = game:GetService("TextChatService")

local Admins = require(script.Parent.Parent.Config.Admins)
local MaintenanceService = require(script.Parent.MaintenanceService)

local AdminService = {}

AdminService.KICK_MESSAGE =
	"Game update: Flintborn is restarting for an update. Your items were saved and return on your next Play."

local function notify(player: Player?, message: string)
	if player then
		warn("[AdminService] " .. player.Name .. ": " .. message)
	end
end

function AdminService.IsAdmin(userId: number): boolean
	if table.find(Admins.UserIds, userId) then
		return true
	end
	if game.CreatorType == Enum.CreatorType.User then
		return userId == game.CreatorId
	end
	local player = Players:GetPlayerByUserId(userId)
	if player == nil then
		return false
	end
	local ok, rank = pcall(player.GetRankInGroup, player, game.CreatorId)
	return ok and rank >= Admins.MIN_GROUP_RANK
end

-- Safely kicks one player. Returns false when their items could not be saved.
function AdminService.SafeKick(target: Player): boolean
	if not MaintenanceService.Preserve(target) then
		return false
	end
	target:Kick(AdminService.KICK_MESSAGE)
	return true
end

local function runCommand(admin: Player, text: string)
	if not AdminService.IsAdmin(admin.UserId) then
		return
	end
	local argument = string.match(text, "^%s*/safekick%s+(.-)%s*$")
	if argument == nil or argument == "" then
		notify(admin, "Usage: /safekick <name> or /safekick all")
		return
	end
	local targets = {}
	for _, player in Players:GetPlayers() do
		local matches = string.lower(argument) == "all"
			or string.lower(player.Name) == string.lower(argument)
			or string.lower(player.DisplayName) == string.lower(argument)
		if matches then
			table.insert(targets, player)
		end
	end
	for _, target in targets do
		if not AdminService.SafeKick(target) then
			notify(admin, "Could not save " .. target.Name .. "'s items; they were not kicked.")
		end
	end
end

function AdminService.Start()
	if TextChatService.ChatVersion == Enum.ChatVersion.TextChatService then
		local command = Instance.new("TextChatCommand")
		command.Name = "FlintbornSafeKick"
		command.PrimaryAlias = "/safekick"
		command.Parent = TextChatService
		command.Triggered:Connect(function(source, text)
			local admin = Players:GetPlayerByUserId(source.UserId)
			if admin then
				runCommand(admin, text)
			end
		end)
	else
		Players.PlayerAdded:Connect(function(player)
			player.Chatted:Connect(function(text)
				runCommand(player, text)
			end)
		end)
	end
end

return AdminService
