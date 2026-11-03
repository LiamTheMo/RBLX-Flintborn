-- Player-facing words for the refusal codes the server returns ("TooFar",
-- "NoRoom", ...). Every code a server service or shared rule returns has a
-- short line here (tests/luau/reasons.spec.luau checks it against the source),
-- and a code that is not listed never reaches a player as it is: it reads as
-- the generic FALLBACK instead.
--
-- Lines are lower-case clauses with no full stop, because screens put them
-- after their own words ("Party: slow down a little and try again", "Not
-- bought: you need more coins"); ReasonText.Sentence makes one a sentence.
-- Keep to characters Merriweather has (no ★ or →; STYLE_GUIDE §1.3).

local ReasonText = {}

ReasonText.FALLBACK = "that didn't work"

ReasonText.TEXT = {
	-- Requests, timing and the connection
	BadRequest = "something went wrong with that request — try again",
	Rejected = "the request was turned down",
	TooFast = "slow down a little and try again",
	TooSoon = "that isn't ready again yet",
	Cooldown = "wait a moment before doing that again",
	Duplicate = "that request was already handled",
	Busy = "something is already in progress — wait for it to finish",
	Interrupted = "you stopped before finishing",
	InProgress = "that is already under way",
	Unavailable = "that isn't available right now — try again shortly",
	ShuttingDown = "this server is closing — try again in a moment",
	WorldLoading = "the island is still being built — try again in a few seconds",
	["Request failed"] = "the server didn't answer — try again",
	["request failed"] = "the server didn't answer — try again",
	RequestFailed = "the server didn't answer — try again",

	-- Your data
	NotLoaded = "your data is still loading — try again in a moment",
	ProfileNotLoaded = "your data is still loading — try again in a moment",
	LeaseLost = "your data is open on another server",
	RecoveringItems = "your items from a crashed server are still being recovered — try again in a minute",
	NoCheckpoint = "there is nothing to recover",
	InTransit = "your items are still on their way",

	-- Where you are and what you're doing
	NoCharacter = "your character isn't in the world yet",
	Downed = "you can't do that while downed",
	NotInRun = "you can only do that on the island",
	NotInMenu = "you can only do that from the island's menu",
	SafeZone = "you can't do that in a safe zone",
	TooFar = "you're too far away",
	NoLineOfSight = "you can't see that spot from here",
	NoGround = "there's no ground there",
	Blocked = "something is in the way",
	InsideStructure = "you can't do that inside a building",
	TooCloseToExtraction = "that's too close to an extraction point",
	NoBuildZone = "you can't build here",
	InTrade = "finish your trade first",
	AlreadyDeploying = "you're already on your way to the island",
	NoSpawn = "no safe place to land was found — try again",
	SpawnFailed = "you couldn't be placed on the island — try again",
	ReservationFailed = "the island server couldn't be reached — try again",
	OnlyLeaderDeploys = "only the party leader can start the run",

	-- Items, rooms and amounts
	BadQuantity = "that amount isn't allowed",
	Empty = "there's nothing there",
	Gone = "that's no longer there",
	SlotChanged = "that slot changed — check it again",
	Expired = "that has gone",
	NotYours = "that isn't yours",
	NoItem = "you don't have that item",
	MissingItem = "you no longer have that item",
	NotCarried = "you aren't carrying that",
	NotHeld = "hold that item first",
	UnknownItem = "that item no longer exists",
	NotConsumable = "that can't be used",
	NotArmor = "that can't be worn",
	NotPlaceable = "that can't be placed",
	NotARune = "that isn't a rune",
	InvalidMove = "that can't go there",
	NoRoom = "there's no room for that",
	InventoryFull = "your backpack is full",
	BackpackFull = "your lobby backpack has no room for that",
	ChestFull = "the chest is full",
	VaultFull = "your vault is full",
	VaultWouldOverflow = "your vault can't hold all of that material",
	NotEnough = "your vault doesn't hold that many",
	NotVaulted = "that item has to be in your vault",

	-- Crafting, the Forge and Permanent items
	UnknownRecipe = "that recipe no longer exists",
	Locked = "that recipe is still locked",
	MissingMaterials = "you don't have enough materials for that",
	MissingIngredients = "you don't have the ingredients for that",
	WrongSource = "that item can't be used for this",
	BadSource = "that item can't be used for this",
	NoSource = "choose an item to use",
	NotEligible = "that item can't be made Permanent",
	AlreadyPermanent = "that item is already Permanent",

	-- Building and sieges
	PieceLimit = "you've placed as many pieces as you can",
	TotemLimit = "you've already placed a totem",

	-- Coins, gems, the shop and quests
	NotEnoughCoins = "you need more coins",
	NotEnoughGems = "you need more gems",
	NotEnoughTokens = "you need more rebirth tokens",
	AlreadyOwned = "you already own that",
	NotBought = "that can't be sold",
	PermanentNotSold = "Permanent items can't be sold",
	MaxTier = "that's already at its highest tier",
	MaxRank = "that's already at its highest rank",
	UnknownCode = "that code isn't valid",
	AlreadyRedeemed = "you've already used that code",
	UnknownQuest = "that quest no longer exists",
	NotFinished = "that quest isn't finished yet",
	AlreadyClaimed = "you've already claimed that",
	AlreadyPaid = "that reward was already given",
	BoostActive = "a boost at least as strong is already running",

	-- Progression
	LevelTooLow = "your level is too low for that",
	ChallengeIncomplete = "finish the rebirth challenge first",
	UnknownPerk = "that perk no longer exists",
	NothingToRespec = "you have no perks to reset",

	-- Trading
	PlayerNotHere = "that player isn't in this server any more",
	NoInvite = "that invite has expired",
	NotReady = "not ready yet — wait a moment",
	ItemsChanged = "the items on offer changed — check them again",
	TradePending = "a recent trade is still being saved — try again shortly",
	TradeSettling = "a recent trade is still being saved — try again shortly",
	TooManyItems = "that's too many items for one trade",
	NotTradeable = "that item can't be traded",
	CoinsNotTradeable = "coins can't be traded",
	BadGems = "that gem amount isn't allowed",
	GemLevel = "you need a higher level to trade gems",
	PartnerGemLevel = "they need a higher level to trade gems",
	GemDailyLimit = "you've traded as many gems as you can today",
	PartnerGemDailyLimit = "they've traded as many gems as they can today",
	PartnerVaultFull = "their vault has no room for that many",

	-- Parties and tribes
	CannotInviteSelf = "you can't invite yourself",
	NotLeader = "only the leader can do that",
	AlreadyMember = "they're already in your party",
	PartyFull = "the party is full",
	NotInParty = "you're not in a party",
	AlreadyInTribe = "you're already in a tribe",
	NoTribe = "you're not in a tribe",
	NoSuchTribe = "that tribe no longer exists",
	NotMember = "they're not in your tribe",
	TribeExists = "that tribe already exists",
	TribeFull = "that tribe is full",
}

-- True when `code` has its own line.
function ReasonText.Has(code: any): boolean
	return type(code) == "string" and ReasonText.TEXT[code] ~= nil
end

-- The line for a refusal code; anything unknown (nil, a number, a code with no
-- line) reads as the generic FALLBACK, never as the raw code.
function ReasonText.Text(code: any): string
	return if type(code) == "string" then ReasonText.TEXT[code] or ReasonText.FALLBACK else ReasonText.FALLBACK
end

-- The line as a sentence: a capital first letter and a full stop.
function ReasonText.Sentence(code: any): string
	local text = ReasonText.Text(code)
	return (text:gsub("^%l", string.upper)) .. "."
end

return ReasonText
