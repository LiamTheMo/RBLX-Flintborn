-- Every RemoteEvent and RemoteFunction in one place. The server creates them under
-- ReplicatedStorage.FlintbornRemotes at start-up; clients wait for them. Remotes
-- carry intent only: the server validates every argument (GDD §12.1).

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Remotes = {}

local FOLDER_NAME = "FlintbornRemotes"

local DEFINITIONS = {
	-- Lobby
	PartyAction = "RemoteFunction", -- (action, argument) -> ok, reason
	PartyChanged = "RemoteEvent", -- server -> client: party snapshot
	Deploy = "RemoteFunction", -- () -> ok, reason
	DeployPreview = "RemoteFunction", -- () -> list of items that will enter the run
	-- World
	RequestPlay = "RemoteFunction", -- (requestId) -> ok, reason
	ReturnToLobby = "RemoteFunction", -- () -> ok, reason
	SetMovement = "RemoteEvent", -- client -> server: (sprintHeld, crouching)
	UseConsumable = "RemoteFunction", -- (requestId, catalogId) -> ok, reason
	InventoryChanged = "RemoteEvent", -- server -> client: inventory snapshot
	MoveItem = "RemoteFunction", -- (fromArea, fromIndex, toArea, toIndex) -> ok, reason
	EquipSlot = "RemoteFunction", -- (hotbarIndex or nil) -> ok, reason
	Craft = "RemoteFunction", -- (requestId, recipeId) -> ok, reason
	PlaceItem = "RemoteFunction", -- (hotbarIndex) -> ok, reason
	Notify = "RemoteEvent", -- server -> client: short message
	EquipArmor = "RemoteFunction", -- (area, index) -> ok, reason
	UnequipArmor = "RemoteFunction", -- (slot) -> ok, reason
	Attack = "RemoteEvent", -- client -> server: (sequence, aimDirection)
	Shoot = "RemoteEvent", -- client -> server: (sequence, drawSeconds, aimDirection)
	CombatFeedback = "RemoteEvent", -- server -> client: (kind, amount)
	TribeAction = "RemoteFunction", -- (action, argument) -> ok, reason
	TribeChanged = "RemoteEvent", -- server -> client: tribe snapshot
	CorpseOpened = "RemoteEvent", -- server -> client: (corpseId, contents)
	CorpseTake = "RemoteFunction", -- (corpseId, index) -> ok, reason
	DeathSummary = "RemoteEvent", -- server -> client: what dropped and what was kept
	ExtractionEvent = "RemoteEvent", -- server -> all: an extraction countdown started
	ExtractionEnded = "RemoteEvent", -- server -> all: (eventId)
	PlaceRune = "RemoteFunction", -- (hotbarIndex) -> ok, reason
	VaultSnapshot = "RemoteFunction", -- () -> vault and lobby backpack view
	VaultDeposit = "RemoteFunction", -- (backpackIndex) -> ok, reason
	VaultWithdrawItem = "RemoteFunction", -- (vaultIndex) -> ok, reason
	VaultWithdrawMaterial = "RemoteFunction", -- (catalogId, quantity) -> ok, reason
	ExtractionReceipt = "RemoteEvent", -- server -> client: the latest extraction receipt
	ForgeSnapshot = "RemoteFunction", -- () -> recipes with vault counts and unlock state
	ForgeCraft = "RemoteFunction", -- (recipeId, sourceInstanceId?, nonce) -> ok, receipt or reason
	DropItem = "RemoteFunction", -- (area, index) -> ok, reason
	Build = "RemoteFunction", -- (pieceId, tier, basePosition, quarterTurns) -> ok, reason
	BuildInfo = "RemoteFunction", -- () -> no-build auras and build reach
	ChestOpened = "RemoteEvent", -- server -> client: (chestId, contents)
	ChestTake = "RemoteFunction", -- (chestId, index) -> ok, reason
	ChestPut = "RemoteFunction", -- (chestId, area, index) -> ok, reason
}

local function folder()
	local existing = ReplicatedStorage:FindFirstChild(FOLDER_NAME)
	if existing then
		return existing
	end
	if RunService:IsServer() then
		local created = Instance.new("Folder")
		created.Name = FOLDER_NAME
		created.Parent = ReplicatedStorage
		return created
	end
	return ReplicatedStorage:WaitForChild(FOLDER_NAME)
end

-- Server: creates every remote. Safe to call more than once.
function Remotes.Init()
	local parent = folder()
	for name, className in DEFINITIONS do
		if parent:FindFirstChild(name) == nil then
			local remote = Instance.new(className)
			remote.Name = name
			remote.Parent = parent
		end
	end
end

function Remotes.Get(name: string)
	assert(DEFINITIONS[name], "Unknown remote " .. tostring(name))
	local parent = folder()
	if RunService:IsServer() then
		Remotes.Init()
		return parent:FindFirstChild(name)
	end
	return parent:WaitForChild(name)
end

return Remotes
