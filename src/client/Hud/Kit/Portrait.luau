-- A player's headshot in a frame (sheets 01, 15; M01 card, M04 rows): "square"
-- the leather-cornered frame, "round" the round window. The headshot uses the
-- thumbnail content URL (no yield; the capture draws a placeholder head) and is
-- listed with SpriteLoader.Track for the image diagnostics.
--
--   Kit.Portrait.new(row, { rect = { 0, 2, 48, 48 }, userId = player.UserId })

local SpriteLoader = require(script.Parent.Parent.SpriteLoader)
local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Tokens = require(script.Parent.Tokens)

local Portrait = {}
Portrait.__index = Portrait

-- The frame's window as a share of its size {x, y, w, h}; the headshot fills it
-- with a little to spare under the frame's edge.
Portrait.WINDOW = {
	square = { 0.2, 0.22, 0.6, 0.58 },
	round = { 0.19, 0.2, 0.62, 0.6 },
	none = { 0, 0, 1, 1 },
}

function Portrait.Content(userId: number): string
	return ("rbxthumb://type=AvatarHeadShot&id=%d&w=150&h=150"):format(userId)
end

-- props: rect | size, userId, frame ("square" | "round" | "none": the bare
-- photo filling the box, as party lists draw it), backdrop (colour token
-- behind the photo; default photoBackdrop for "none"; false: none, so the
-- panel shows through the transparent headshot), zIndex, name.
function Portrait.new(parent: Instance, props)
	local frame = props.frame or "square"
	local role = if frame == "round" then "portrait.round" else "portrait.square"
	local w, h = Core.Size(props, 64, 64)
	local base = Core.Root(parent, "Portrait", role, props, w, h)
	local self = setmetatable({ root = base.root, base = base }, Portrait)
	local window = Portrait.WINDOW[frame] or Portrait.WINDOW.square
	self.headshot = Core.Make("ImageLabel", {
		Name = "Headshot",
		BackgroundTransparency = 1,
		Image = "",
		Position = UDim2.fromScale(window[1], window[2]),
		ScaleType = Enum.ScaleType.Crop,
		Size = UDim2.fromScale(window[3], window[4]),
		ZIndex = base.z,
	}, base.visual)
	local backdrop = props.backdrop
	if backdrop == nil then
		backdrop = if frame == "none" then "photoBackdrop" else nil
	end
	if backdrop then
		self.headshot.BackgroundTransparency = 0
		self.headshot.BackgroundColor3 = Tokens.Color(backdrop)
	end
	if frame == "round" then
		Core.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, self.headshot)
	end
	if frame ~= "none" then
		Art.Plate(base.visual, role, w, h, { z = base.z + 1 })
	end
	self:SetUser(props.userId)
	return self
end

function Portrait:SetUser(userId: number?)
	self.userId = userId
	self.headshot.Image = if userId and userId > 0 then Portrait.Content(userId) else ""
	SpriteLoader.Track(self.headshot)
end

function Portrait:Destroy()
	self.base.maid:Clean()
end

return Portrait
