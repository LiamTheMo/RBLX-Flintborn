-- Keeps the clients' HUD image reports (UiDiagnosticsController) so the "Probe
-- UI images" workflow can read how images load on real devices. Each player may
-- send a few reports per server; the latest REPORTS_KEPT across the universe are
-- kept in one DataStore key. Reports hold counts, image ids and device kind
-- only; the player is recorded by user id.

local DataStoreService = game:GetService("DataStoreService")
local HttpService = game:GetService("HttpService")

local Remotes = require(game:GetService("ReplicatedStorage").Shared.Net.Remotes)

local UiDiagnosticsService = {}

UiDiagnosticsService.STORE = "FlintbornDiagnostics"
UiDiagnosticsService.KEY = "uiimages:latest"
UiDiagnosticsService.REPORTS_KEPT = 8
UiDiagnosticsService.PER_PLAYER = 3

local sent = setmetatable({}, { __mode = "k" })

local function store(entry)
	pcall(function()
		DataStoreService:GetDataStore(UiDiagnosticsService.STORE):UpdateAsync(UiDiagnosticsService.KEY, function(old)
			local list = if type(old) == "table" then old else {}
			table.insert(list, 1, entry)
			while #list > UiDiagnosticsService.REPORTS_KEPT do
				table.remove(list)
			end
			return list
		end)
	end)
end

function UiDiagnosticsService.Start()
	Remotes.Listen("ReportUiImages", function(player: Player, summary, lines)
		local count = (sent[player] or 0) + 1
		sent[player] = count
		if count > UiDiagnosticsService.PER_PLAYER or type(summary) ~= "string" then
			return
		end
		local kept = {}
		if type(lines) == "table" then
			for _, line in lines do
				if type(line) == "string" and #kept < 40 then
					table.insert(kept, string.sub(line, 1, 200))
				end
			end
		end
		local entry = {
			at = os.time(),
			user = player.UserId,
			server = game.JobId,
			summary = string.sub(summary, 1, 250),
			lines = kept,
		}
		print("[UiDiagnostics] " .. HttpService:JSONEncode({ entry.summary, #kept }))
		task.spawn(store, entry)
	end)
end

return UiDiagnosticsService
