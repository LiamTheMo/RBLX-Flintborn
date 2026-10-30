-- Makes sure images actually arrive. Phones refuse image requests that come in
-- a burst: in each session the first handful of HUD images loaded and every one
-- after them reported Failure, retries included, while the same images load
-- fine in the place.
--
-- HUD images (Widgets.Sprite) go through Assign: an ImageLabel starts empty and
-- its image is fetched one at a time (ContentProvider:PreloadAsync on a single
-- ImageLabel, the only fetch in flight), images with a label on screen first,
-- then handed to every label that uses it. A failed fetch waits a growing,
-- jittered delay and is asked again under the other spelling of the asset
-- (rbxassetid:// and the asset URL); after SHOW_AFTER failures its labels are
-- given the image anyway, while it keeps being retried, in case the preload is
-- wrong about it. Track lists a label whose image was set elsewhere (a
-- headshot) for the diagnostics.
--
-- Character textures (CharacterLookController) use TrackProperty: new ones are
-- preloaded in one batch and each failed fetch is retried with a growing delay,
-- reassigning it on everything that uses it so the engine asks again.

local ContentProvider = game:GetService("ContentProvider")

local SpriteLoader = {}

-- Pacing for HUD images: a tick every TICK seconds while images wait (IDLE
-- otherwise); one fetch in flight at a time, given up after FETCH_TIMEOUT. A
-- failed image is asked again after FIRST_WAIT, doubling up to MAX_WAIT.
-- Every device prefetches the art of closed menus after what is on screen, so a
-- menu opens with its art already there: with the art packed into atlases that is
-- a few images, one at a time.
SpriteLoader.TICK = 0.05
SpriteLoader.IDLE = 0.5
SpriteLoader.FETCH_TIMEOUT = 20
SpriteLoader.FIRST_WAIT = 4
SpriteLoader.MAX_WAIT = 60
SpriteLoader.SHOW_AFTER = 3
SpriteLoader.PREFETCH_HIDDEN = true

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

-- label -> {id, pending}. Held strongly and dropped when the label is
-- destroyed: with weak keys, Roblox collected the handles of labels no other
-- Lua held (most HUD art), and those images were never handed out.
local labels = {}
-- image id -> {state = "waiting" | "loading" | "loaded" | "failed", content,
-- tries, retryAt, status}
local hudImages = {}
local pumping = false
local inFlight = nil
-- Set only by the headless capture runtime (art/ui/capture/gui_env.luau); a
-- global that is nil in the game.
local CAPTURE = (__FlintbornCapture :: any) == true

local function now(): number
	return os.clock()
end

local function hold(label: GuiObject, entry)
	local fresh = labels[label] == nil
	labels[label] = entry
	if fresh then
		label.Destroying:Connect(function()
			labels[label] = nil
		end)
	end
end

local function imageFor(id: string)
	local image = hudImages[id]
	if image == nil then
		image = { state = "waiting", content = id, tries = 0, retryAt = 0, status = "Queued" }
		hudImages[id] = image
	end
	return image
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

-- A fetch status (an EnumItem, or the capture runtime's string) by name.
local function statusName(status: any): string
	if typeof(status) == "EnumItem" then
		return status.Name
	end
	return if type(status) == "string" then string.match(status, "(%w+)$") or status else "Unknown"
end

-- The other spelling of an asset image ("rbxassetid://N" <-> the asset URL),
-- or nil for content that has none.
local URL = "http://www.roblox.com/asset/?id="
local function otherSpelling(content: string): string?
	local id = string.match(content, "^rbxassetid://(%d+)$")
	if id then
		return URL .. id
	end
	id = string.match(content, "^http://www%.roblox%.com/asset/%?id=(%d+)$")
	return if id then "rbxassetid://" .. id else nil
end

local function waitFor(tries: number): number
	local base = math.min(SpriteLoader.FIRST_WAIT * 2 ^ (tries - 1), SpriteLoader.MAX_WAIT)
	return base * (0.75 + math.random() * 0.5)
end

-- Gives every waiting label of image `id` its picture.
local function hand(id: string)
	local image = hudImages[id]
	for label, entry in labels do
		if entry.pending and entry.id == id then
			entry.pending = false
			if (label :: any).Image == "" then
				(label :: any).Image = image.content
			end
		end
	end
end

-- Preloads one image (the only fetch in flight), then hands it out; a failure
-- waits its turn again under the other spelling.
local function fetch(id: string)
	local image = hudImages[id]
	image.state = "loading"
	local token = {}
	inFlight = { token = token, id = id, started = now() }
	task.spawn(function()
		local probe = Instance.new("ImageLabel")
		probe.Image = image.content
		local status = nil
		local ok = pcall(function()
			ContentProvider:PreloadAsync({ probe }, function(_, fetched)
				status = fetched
			end)
		end)
		probe:Destroy()
		if inFlight == nil or inFlight.token ~= token then
			return -- timed out meanwhile and already counted as a failure
		end
		inFlight = nil
		image.status = if ok then statusName(status) else "Error"
		if image.status == "Success" then
			image.state = "loaded"
			hand(id)
			return
		end
		image.state = "failed"
		image.tries += 1
		image.retryAt = now() + waitFor(image.tries)
		image.content = otherSpelling(image.content) or image.content
		if image.tries >= SpriteLoader.SHOW_AFTER then
			-- The preload may be wrong about it: let the labels try on their own as
			-- well, while it keeps being retried.
			hand(id)
		end
	end)
end

-- One tick: labels of loaded images get them; otherwise, with nothing in
-- flight, the next image to fetch is chosen (one with a label on screen first).
local function tick(): boolean
	local time = now()
	if inFlight and time - inFlight.started > SpriteLoader.FETCH_TIMEOUT then
		local image = hudImages[inFlight.id]
		inFlight = nil
		image.state = "failed"
		image.status = "TimedOut"
		image.tries += 1
		image.retryAt = time + waitFor(image.tries)
	end
	local waiting = false
	local best, bestShown = nil, false
	for label, entry in labels do
		if entry.pending then
			local image = hudImages[entry.id]
			if image.state == "loaded" then
				hand(entry.id)
			else
				waiting = true
				if image.state ~= "loading" and time >= image.retryAt and not bestShown then
					if shown(label) then
						best, bestShown = entry.id, true
					elseif best == nil and SpriteLoader.PREFETCH_HIDDEN then
						best = entry.id
					end
				end
			end
		end
	end
	if inFlight == nil and best then
		fetch(best)
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
			task.wait(if waiting then SpriteLoader.TICK else SpriteLoader.IDLE)
		end
	end)
end

-- A summary of the HUD images on this client for diagnostics: counts, image
-- states, and up to `limit` lines for images that have not loaded
-- ("<id> <state>/<last status> labels=<n> shown=<n> tries=<n>").
function SpriteLoader.Summary(limit: number)
	local counts = { labels = 0, pending = 0, loaded = 0 }
	local rows = {}
	for label, entry in labels do
		counts.labels += 1
		local image = hudImages[entry.id]
		if entry.pending then
			counts.pending += 1
		elseif image and image.state == "loaded" then
			counts.loaded += 1
		end
		if image then
			local row = rows[entry.id]
			if row == nil then
				row = { labels = 0, shown = 0 }
				rows[entry.id] = row
			end
			row.labels += 1
			if shown(label) then
				row.shown += 1
			end
		end
	end
	local statuses, lines = {}, {}
	for id, row in rows do
		local image = hudImages[id]
		statuses[image.state] = (statuses[image.state] or 0) + 1
		if image.state ~= "loaded" and #lines < limit then
			table.insert(
				lines,
				("%s %s/%s labels=%d shown=%d tries=%d"):format(
					id,
					image.state,
					image.status,
					row.labels,
					row.shown,
					image.tries
				)
			)
		end
	end
	if SpriteLoader.LastError then
		table.insert(lines, 1, "error: " .. string.sub(SpriteLoader.LastError, 1, 180))
	end
	return counts, statuses, lines
end

-- For the capture harness's loader scene: one tick, and the tables.
SpriteLoader._tick = tick
SpriteLoader._labels = labels
SpriteLoader._images = hudImages

-- Gives `label` the image `id` once it has been fetched (at once in the
-- headless capture, whose clock never runs).
function SpriteLoader.Assign(label: ImageLabel, id: string)
	if CAPTURE then
		label.Image = id
		return
	end
	local image = imageFor(id)
	if image.state == "loaded" then
		label.Image = image.content
		return
	end
	label.Image = ""
	hold(label, { id = id, pending = true })
	pump()
end

-- Lists a label whose image was set elsewhere (a headshot) in the diagnostics.
function SpriteLoader.Track(label: ImageLabel)
	local id = label.Image
	if CAPTURE or id == "" then
		return
	end
	local image = imageFor(id)
	image.state = "loaded"
	hold(label, { id = id, pending = false })
end

return SpriteLoader
