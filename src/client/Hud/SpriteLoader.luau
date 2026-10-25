-- Makes sure images actually arrive. A client that requests many new images at
-- once (phones especially) can have some fetches fail, and Roblox leaves those
-- images blank for the session: the lobby showed some HUD icons and not others,
-- and characters spawned with grey clothing and no face. Widgets.Sprite tracks
-- every HUD image here and CharacterLookController every character texture; new
-- ones are preloaded in one batch, and each image whose fetch fails is retried
-- with a growing delay, reassigning it on everything that uses it so the engine
-- asks again.

local ContentProvider = game:GetService("ContentProvider")

local SpriteLoader = {}

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
		local statuses = {}
		local ok = pcall(function()
			ContentProvider:PreloadAsync(batch, function(contentId: string, status: Enum.AssetFetchStatus)
				statuses[contentId] = status
			end)
		end)
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

function SpriteLoader.Track(label: ImageLabel)
	SpriteLoader.TrackProperty(label, "Image")
end

return SpriteLoader
