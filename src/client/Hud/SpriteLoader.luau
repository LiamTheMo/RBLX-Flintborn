-- Makes sure images actually arrive. A client that requests many new images at
-- once (phones especially) has some fetches fail, and Roblox leaves those images
-- blank for the session: the lobby showed its Enter plate and nothing else.
--
-- HUD images (Widgets.Sprite) go through Assign: an ImageLabel starts empty and
-- gets its image from a paced queue, a few per tick, those on screen first and
-- the hidden menus' art after, so the client never asks for every image at
-- once. A watchdog then checks each image on screen by what the label itself
-- reports (IsLoaded; ContentProvider's statuses can say a fetch failed when the
-- widget loads fine) and asks again, with a growing, jittered delay and no
-- giving up, until it shows. Track watches a label whose image was set
-- elsewhere (a headshot) the same way.
--
-- Character textures (CharacterLookController) use TrackProperty: new ones are
-- preloaded in one batch and each failed fetch is retried with a growing delay,
-- reassigning it on everything that uses it so the engine asks again.

local ContentProvider = game:GetService("ContentProvider")
local UserInputService = game:GetService("UserInputService")

local SpriteLoader = {}

-- HUD images assigned per tick while screens fill, and per tick for hidden
-- screens' art once nothing on screen is waiting. Touch-only devices (phones,
-- tablets) fetch a menu's art when it opens instead: the menus' window art is
-- several megapixels, which a phone's texture memory should not hold unused.
SpriteLoader.PER_TICK = 6
SpriteLoader.IDLE_PER_TICK = if UserInputService.TouchEnabled and not UserInputService.KeyboardEnabled then 0 else 2
SpriteLoader.TICK = 0.1
-- An image on screen not loaded this long after it was (re)assigned is asked
-- for again; the wait doubles each time up to MAX_WAIT (jittered so many
-- images do not retry together), and at most RETRIES_PER_SWEEP go per sweep.
SpriteLoader.FIRST_WAIT = 6
SpriteLoader.MAX_WAIT = 30
SpriteLoader.SWEEP = 1
SpriteLoader.RETRIES_PER_SWEEP = 4

SpriteLoader.RETRIES = 6
SpriteLoader.FIRST_DELAY = 1

-- image id -> { users = {Instance = property} (weak, so destroyed characters go),
-- state = "pending" | "loading" | "loaded" | "failed", tries }
local images = {}
local flushQueued = false

local function usersOf(id: string): { { any } }
	local list = {}
	for instance, property in images[id].users do
		if instance.Parent ~= nil and (instance :: any)[property] == id then
			table.insert(list, { instance, property })
		else
			images[id].users[instance] = nil
		end
	end
	return list
end

-- Clearing and reassigning makes the engine request the image again.
local function reassign(instance: Instance, property: string, id: string)
	local target: any = instance
	target[property] = ""
	target[property] = id
end

local preload

local function retry(id: string)
	local entry = images[id]
	entry.tries += 1
	if entry.tries > SpriteLoader.RETRIES then
		entry.state = "failed"
		warn("[SpriteLoader] could not load " .. id .. " after " .. SpriteLoader.RETRIES .. " retries")
		return
	end
	entry.state = "pending"
	task.delay(SpriteLoader.FIRST_DELAY * 2 ^ (entry.tries - 1), function()
		for _, user in usersOf(id) do
			reassign(user[1], user[2], id)
		end
		preload({ id })
	end)
end

preload = function(ids: { string })
	local batch = {}
	for _, id in ids do
		local entry = images[id]
		if entry and entry.state == "pending" then
			entry.state = "loading"
			table.insert(batch, id)
		end
	end
	if #batch == 0 then
		return
	end
	task.spawn(function()
		-- Raw content strings can fail the generic asset fetch even when the same
		-- image loads on a widget. ImageLabels request the image representation,
		-- including for the character textures tracked here.
		local assets = {}
		for _, id in batch do
			local image = Instance.new("ImageLabel")
			image.Image = id
			table.insert(assets, image)
		end
		local statuses = {}
		local ok = pcall(function()
			ContentProvider:PreloadAsync(assets, function(contentId: string, status: Enum.AssetFetchStatus)
				statuses[contentId] = status
			end)
		end)
		for _, image in assets do
			image:Destroy()
		end
		for _, id in batch do
			if ok and statuses[id] == Enum.AssetFetchStatus.Success then
				images[id].state = "loaded"
				-- Anything whose own fetch failed earlier stays blank until it asks
				-- again. ImageLabels say so (IsLoaded); textures and decals cannot,
				-- so they always ask once more, which the cache answers at once.
				for _, user in usersOf(id) do
					local instance = user[1]
					if not instance:IsA("ImageLabel") or not instance.IsLoaded then
						reassign(instance, user[2], id)
					end
				end
			else
				retry(id)
			end
		end
	end)
end

local function flush()
	flushQueued = false
	local pending = {}
	for id, entry in images do
		if entry.state == "pending" then
			table.insert(pending, id)
		end
	end
	preload(pending)
end

-- Watches the image in instance[property] (an ImageLabel's Image, a MeshPart's
-- TextureID, a Decal's Texture): preloads it with the other new images this
-- frame, and retries the fetch if it fails.
function SpriteLoader.TrackProperty(instance: Instance, property: string)
	local id = (instance :: any)[property]
	if type(id) ~= "string" or id == "" then
		return
	end
	local entry = images[id]
	if entry == nil then
		entry = { users = setmetatable({}, { __mode = "k" }), state = "pending", tries = 0 }
		images[id] = entry
	elseif entry.state == "failed" and entry.users[instance] == nil then
		-- Something new wants an image that gave up earlier: try it again from scratch.
		entry.state = "pending"
		entry.tries = 0
	end
	if entry.users[instance] == property then
		return -- already watching this image here
	end
	entry.users[instance] = property
	if entry.state == "loaded" and not instance:IsA("ImageLabel") then
		-- Already fetched: ask once more in case this one's own fetch failed.
		task.defer(reassign, instance, property, id)
	end
	if entry.state == "pending" and not flushQueued then
		flushQueued = true
		task.defer(flush)
	end
end

-- HUD images ---------------------------------------------------------------------

-- label -> {id, pending, due, tries}; weak, so destroyed labels drop out.
local labels = setmetatable({}, { __mode = "k" })
local pumping = false
-- Set only by the headless capture runtime (art/ui/capture/gui_env.luau); a
-- global that is nil in the game.
local CAPTURE = (__FlintbornCapture :: any) == true

local function now(): number
	return os.clock()
end

-- On screen: in an enabled gui, with every GuiObject up the chain visible.
local function shown(label: GuiObject): boolean
	local gui = label:FindFirstAncestorWhichIsA("LayerCollector")
	if gui == nil or not (gui :: any).Enabled then
		return false
	end
	local node: Instance? = label
	while node and node ~= gui do
		if node:IsA("GuiObject") and not node.Visible then
			return false
		end
		node = node.Parent
	end
	return true
end

local function waitFor(tries: number): number
	local base = math.min(SpriteLoader.FIRST_WAIT * 2 ^ tries, SpriteLoader.MAX_WAIT)
	return base * (0.75 + math.random() * 0.5)
end

local function give(label: any, entry)
	entry.pending = false
	entry.due = now() + waitFor(0)
	-- Something else may have set an image meanwhile; it wins.
	if label.Image == "" then
		label.Image = entry.id
	end
end

-- One tick: assign queued images (on screen first), then, once a sweep is due,
-- ask again for images on screen that have not loaded.
local lastSweep = 0
local function tick(sweepNow: boolean?): boolean
	local budget = SpriteLoader.PER_TICK
	local waiting, hidden = false, {}
	for label, entry in labels do
		if entry.pending then
			if shown(label) then
				waiting = true
				if budget > 0 then
					give(label, entry)
					budget -= 1
				end
			elseif #hidden < SpriteLoader.IDLE_PER_TICK then
				-- Hidden art keeps the fast pace only where it is prefetched.
				waiting = true
				table.insert(hidden, label)
			end
		end
	end
	-- Nothing on screen was waiting: fetch a little of the hidden menus' art.
	if budget == SpriteLoader.PER_TICK then
		for _, label in hidden do
			give(label, labels[label])
		end
	end
	local time = now()
	if sweepNow or time - lastSweep >= SpriteLoader.SWEEP then
		lastSweep = time
		local retries = SpriteLoader.RETRIES_PER_SWEEP
		for label, entry in labels do
			if retries <= 0 then
				break
			end
			if not entry.pending and time >= entry.due and label.Image == entry.id then
				if label.IsLoaded then
					entry.due = math.huge
				elseif shown(label) then
					reassign(label, "Image", entry.id)
					entry.tries += 1
					entry.due = time + waitFor(entry.tries)
					retries -= 1
				end
			end
		end
	end
	return waiting
end

local function pump()
	if pumping then
		return
	end
	pumping = true
	task.spawn(function()
		while true do
			local waiting = tick()
			-- Idle between sweeps once nothing waits that this tick could give out
			-- (a menu that opens is picked up within a sweep).
			task.wait(if waiting then SpriteLoader.TICK else SpriteLoader.SWEEP)
		end
	end)
end

-- For the capture harness's loader scene: one tick, and the label table.
SpriteLoader._tick = tick
SpriteLoader._labels = labels

-- Gives `label` the image `id` through the paced queue (at once in the headless
-- capture, whose clock never runs).
function SpriteLoader.Assign(label: ImageLabel, id: string)
	if CAPTURE then
		label.Image = id
		return
	end
	label.Image = ""
	labels[label] = { id = id, pending = true, due = math.huge, tries = 0 }
	pump()
end

-- Watches a label whose image was set elsewhere and asks again while it does not
-- load.
function SpriteLoader.Track(label: ImageLabel)
	local id = label.Image
	if CAPTURE or id == "" then
		return
	end
	labels[label] = { id = id, pending = false, due = now() + waitFor(0), tries = 0 }
	pump()
end

return SpriteLoader
