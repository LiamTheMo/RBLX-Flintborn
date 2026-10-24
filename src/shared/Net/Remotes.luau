-- Every RemoteEvent and RemoteFunction in one place. The server creates them under
-- ReplicatedStorage.FlintbornRemotes at start-up; clients wait for them. Remotes
-- carry intent only: the server validates every argument (GDD §12.1).

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local RemoteGuard = require(script.Parent.RemoteGuard)

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
	ExtractionReceipt = "RemoteEvent", -- server -> client: the latest extraction receipt
	ForgeSnapshot = "RemoteFunction", -- () -> recipes with vault counts and unlock state
	ForgeCraft = "RemoteFunction", -- (recipeId, sourceInstanceId?, nonce) -> ok, receipt or reason
	DropItem = "RemoteFunction", -- (area, index) -> ok, reason
	Build = "RemoteFunction", -- (pieceId, tier, basePosition, quarterTurns) -> ok, reason
	BuildInfo = "RemoteFunction", -- () -> no-build auras and build reach
	ChestOpened = "RemoteEvent", -- server -> client: (chestId, contents)
	ChestTake = "RemoteFunction", -- (chestId, index) -> ok, reason
	ChestPut = "RemoteFunction", -- (chestId, area, index) -> ok, reason
	EventAnnounced = "RemoteEvent", -- server -> all: (event view, isCatchUp?)
	EventEnded = "RemoteEvent", -- server -> all: (eventId)
	BossAlert = "RemoteEvent", -- server -> all: Guardian horn, phase, Legendary released, end
	ProgressionChanged = "RemoteEvent", -- server -> client: level, masteries, rebirth state
	XpGained = "RemoteEvent", -- server -> client: {amount, reason, levelUp}
	ProgressionSnapshot = "RemoteFunction", -- () -> progression view
	RebirthPreview = "RemoteFunction", -- () -> {reset, kept, gained, eligible, reason}
	Rebirth = "RemoteFunction", -- (nonce) -> ok, reason
	BuyPerk = "RemoteFunction", -- (perkId, nonce) -> ok, reason
	ShopView = "RemoteFunction", -- () -> stock, sellables, offers, vault tier
	ShopBuy = "RemoteFunction", -- (stockId, nonce) -> ok, reason
	MerchantSell = "RemoteFunction", -- (source, key, quantity, nonce) -> ok, coinsOrReason
	VaultUpgrade = "RemoteFunction", -- (nonce) -> ok, reason
	PerkRespec = "RemoteFunction", -- (nonce) -> ok, reason
	RedeemCode = "RemoteFunction", -- (code) -> ok, reason
	QuestView = "RemoteFunction", -- () -> quests with progress
	QuestClaim = "RemoteFunction", -- (questId) -> ok, reason
	TradeRequest = "RemoteFunction", -- (targetUserId) -> ok, sessionIdOrReason
	TradeRespond = "RemoteFunction", -- (sessionId, accept) -> ok, reason
	TradeOffer = "RemoteFunction", -- (sessionId, itemKeys, gems, materials?) -> ok, reason
	TradeLock = "RemoteFunction", -- (sessionId) -> ok, reason
	TradeConfirm = "RemoteFunction", -- (sessionId) -> ok, reason
	TradeCancel = "RemoteFunction", -- (sessionId) -> ok
	TradeChanged = "RemoteEvent", -- server -> client: invite, session state, closed
	SaveCamera = "RemoteEvent", -- client -> server: (zoom) preference, throttled
	SaveSettings = "RemoteEvent", -- client -> server: {uiScale, colourBlindMode, reducedMotion, subtitles}
	SaveKeybinds = "RemoteEvent", -- client -> server: {actionId = keyName} overrides of the default keys
	TutorialChanged = "RemoteEvent", -- server -> client: current tutorial step
	TutorialAction = "RemoteFunction", -- ("Ack" | "Skip" | "Replay") -> ok
	Notice = "RemoteEvent", -- server -> client: {title, text} important one-off notice
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

-- Server: guarded handlers. Every request passes the per-player rate limit and
-- argument sanitising (RemoteGuard) before `handler(player, ...)` runs; rejects
-- are reported to Remotes.OnViolation(player, name, reason).
Remotes.OnViolation = function(_player: Player, _name: string, _reason: string) end

local buckets = setmetatable({}, { __mode = "k" })

local function admit(player: Player, name: string, ...): boolean
	local perPlayer = buckets[player]
	if perPlayer == nil then
		perPlayer = {}
		buckets[player] = perPlayer
	end
	local now = os.clock()
	local bucket = perPlayer[name]
	if bucket == nil then
		bucket = RemoteGuard.NewBucket(now)
		perPlayer[name] = bucket
	end
	if not RemoteGuard.Take(bucket, now) then
		Remotes.OnViolation(player, name, "RateLimited")
		return false
	end
	if not RemoteGuard.Check(table.pack(...)) then
		Remotes.OnViolation(player, name, "MalformedArguments")
		return false
	end
	return true
end

-- Remotes this place has bound a server handler or listener to.
local bound = {}

-- Binds a RemoteFunction handler behind the guard.
function Remotes.Handle(name: string, handler)
	bound[name] = true
	Remotes.Get(name).OnServerInvoke = function(player, ...)
		if not admit(player, name, ...) then
			return false, "Rejected"
		end
		return handler(player, ...)
	end
end

-- Connects a RemoteEvent listener behind the guard.
function Remotes.Listen(name: string, listener)
	bound[name] = true
	return Remotes.Get(name).OnServerEvent:Connect(function(player, ...)
		if admit(player, name, ...) then
			listener(player, ...)
		end
	end)
end

-- Server: every remote nothing in this place listens to (server -> client
-- remotes, or another place's) still gets a guarded no-op, so client spam is
-- rate-limited, reported and dropped instead of queueing unread (GDD §24). Call
-- once services have started; a later Listen/Handle on the same remote takes over.
function Remotes.GuardUnused()
	for name, className in DEFINITIONS do
		if bound[name] then
			continue
		end
		local remote = Remotes.Get(name)
		if className == "RemoteEvent" then
			remote.OnServerEvent:Connect(function(player, ...)
				if not bound[name] then
					admit(player, name, ...)
				end
			end)
		else
			remote.OnServerInvoke = function(player, ...)
				admit(player, name, ...)
				return false, "Unavailable"
			end
		end
	end
end

return Remotes
