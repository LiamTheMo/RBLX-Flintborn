-- Makes sure the HUD's sprite images actually arrive. A client that requests many
-- new images at once (phones especially) can have some fetches fail, and Roblox
-- leaves those ImageLabels blank for the session: the lobby showed some icons and
-- not others. Widgets.Sprite tracks every image here; new ones are preloaded in
-- one batch, and each image whose fetch fails is retried with a growing delay,
-- reassigning it on every label that uses it so the engine asks again.

local ContentProvider = game:GetService("ContentProvider")

local SpriteLoader = {}

SpriteLoader.RETRIES = 6
SpriteLoader.FIRST_DELAY = 1

-- image id -> { labels = {ImageLabel = true}, state = "pending" | "loading" | "loaded" | "failed", tries }
local images = {}
local flushQueued = false

local function labelsOf(id: string): { ImageLabel }
	local list = {}
	for label in images[id].labels do
		if label.Parent ~= nil and label.Image == id then
			table.insert(list, label)
		else
			images[id].labels[label] = nil
		end
	end
	return list
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
		-- Clearing and reassigning makes the engine request the image again.
		for _, label in labelsOf(id) do
			label.Image = ""
			label.Image = id
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
		local statuses = {}
		local ok = pcall(function()
			ContentProvider:PreloadAsync(batch, function(contentId: string, status: Enum.AssetFetchStatus)
				statuses[contentId] = status
			end)
		end)
		for _, id in batch do
			if ok and statuses[id] == Enum.AssetFetchStatus.Success then
				images[id].state = "loaded"
				-- A label whose own fetch failed earlier stays blank until it asks again.
				for _, label in labelsOf(id) do
					if not label.IsLoaded then
						label.Image = ""
						label.Image = id
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

-- Watches `label` (its current Image): preloads it with the other new images
-- this frame, and retries the fetch if it fails.
function SpriteLoader.Track(label: ImageLabel)
	local id = label.Image
	if id == "" then
		return
	end
	local entry = images[id]
	if entry == nil then
		entry = { labels = {}, state = "pending", tries = 0 }
		images[id] = entry
	end
	entry.labels[label] = true
	if entry.state == "pending" and not flushQueued then
		flushQueued = true
		task.defer(flush)
	end
end

return SpriteLoader
