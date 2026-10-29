-- Makes sure images actually arrive. A client that requests many new images at
-- once (phones especially) has some fetches fail, and Roblox leaves those images
-- blank for the session: the lobby showed its Enter plate and nothing else.
--
-- HUD images (Widgets.Sprite) go through Assign: an ImageLabel starts empty and
-- gets its image from a paced queue, a few per tick, those on screen first and
-- the hidden menus' art after, so the client never asks for every image at
-- once. A watchdog then checks each image on screen that has not shown
-- (IsLoaded) and asks again only when its fetch has ended without it (a fetch
-- still running is left alone: asking again would start it over), with a
-- growing, jittered delay and no giving up. Track watches a label whose image was set
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

-- image id -> { users = {Instance = property}, state = "pending" | "loading" |
-- "loaded" | "failed", tries }. Users are held strongly and dropped when they
-- are destroyed: Roblox may collect the Lua handle of an Instance nothing else
-- in Lua holds, so a weak table loses live parts and labels.
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
		entry = { users = {}, state = "pending", tries = 0 }
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
	instance.Destroying:Connect(function()
		entry.users[instance] = nil
	end)
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

-- label -> {id, pending, due, tries}. Held strongly and dropped when the label
-- is destroyed: with weak keys, Roblox collected the handles of labels no other
-- Lua held (most HUD art), and those images were never handed out.
local labels = {}

local function hold(label: GuiObject, entry)
	local fresh = labels[label] == nil
	labels[label] = entry
	if fresh then
		label.Destroying:Connect(function()
			labels[label] = nil
		end)
	end
end
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

-- The engine's fetch state for an image ("Loading", "Success", "Failure",
-- "TimedOut", "None"), or "Unknown".
local function fetchStatus(id: string): string
	local ok, status = pcall(function()
		return ContentProvider:GetAssetFetchStatus(id)
	end)
	return if ok and typeof(status) == "EnumItem" then status.Name else "Unknown"
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
					local status = fetchStatus(entry.id)
					if status == "Loading" or status == "None" then
						-- Still on its way (slow phone networks take a while).
						entry.due = time + SpriteLoader.FIRST_WAIT
					else
						reassign(label, "Image", entry.id)
						entry.tries += 1
						entry.due = time + waitFor(entry.tries)
						retries -= 1
					end
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
			-- An error in one tick must not stop every image after it.
			local ok, result = pcall(tick)
			local waiting = ok and result
			if not ok then
				SpriteLoader.LastError = tostring(result)
				warn("[SpriteLoader] " .. SpriteLoader.LastError)
			end
			-- Idle between sweeps once nothing waits that this tick could give out
			-- (a menu that opens is picked up within a sweep).
			task.wait(if waiting then SpriteLoader.TICK else SpriteLoader.SWEEP)
		end
	end)
end

-- A summary of the HUD images on this client for diagnostics: counts, the
-- engine's fetch state per image id, and up to `limit` lines for ids that have
-- not shown ("<id> <status> loaded=<n>/<labels> shown=<n> tries=<n>").
function SpriteLoader.Summary(limit: number)
	local ids = {}
	local counts = { labels = 0, pending = 0, loaded = 0 }
	for label, entry in labels do
		counts.labels += 1
		local row = ids[entry.id]
		if row == nil then
			row = { labels = 0, loaded = 0, shown = 0, tries = 0, pending = 0 }
			ids[entry.id] = row
		end
		row.labels += 1
		row.tries = math.max(row.tries, entry.tries)
		if entry.pending then
			counts.pending += 1
			row.pending += 1
		elseif label.IsLoaded then
			counts.loaded += 1
			row.loaded += 1
		end
		if shown(label) then
			row.shown += 1
		end
	end
	local statuses, lines = {}, {}
	for id, row in ids do
		local status = if row.pending == row.labels then "Queued" else fetchStatus(id)
		statuses[status] = (statuses[status] or 0) + 1
		if row.loaded < row.labels - row.pending and #lines < limit then
			table.insert(
				lines,
				("%s %s loaded=%d/%d shown=%d tries=%d"):format(
					id,
					status,
					row.loaded,
					row.labels,
					row.shown,
					row.tries
				)
			)
		end
	end
	if SpriteLoader.LastError then
		table.insert(lines, 1, "error: " .. string.sub(SpriteLoader.LastError, 1, 180))
	end
	return counts, statuses, lines
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
	hold(label, { id = id, pending = true, due = math.huge, tries = 0 })
	pump()
end

-- Watches a label whose image was set elsewhere and asks again while it does not
-- load.
function SpriteLoader.Track(label: ImageLabel)
	local id = label.Image
	if CAPTURE or id == "" then
		return
	end
	hold(label, { id = id, pending = false, due = now() + waitFor(0), tries = 0 })
	pump()
end

return SpriteLoader
