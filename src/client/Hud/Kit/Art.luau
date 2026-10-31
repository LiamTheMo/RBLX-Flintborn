-- Roles to art. The role table lives in KitModel.ROLES (the one place a role
-- names its lk_* sprites); components ask Art for a role and never name sprites.
--
-- Uploaded art (an image id or an uploaded atlas) draws through Widgets.Sprite,
-- so the phone-safe nine-piece slicing, tiles and SpriteLoader pacing stay in one
-- place. Until a sprite is uploaded, Art draws a stand-in in the kit's style
-- (ARCHITECTURE §2.5): paper or leather plates with a brown stroke, slots,
-- tracks and fills as pills, glyphs in ink.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local ItemInfo = require(ReplicatedStorage.Shared.Items.ItemInfo)
local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local UiAssets = require(ReplicatedStorage.Shared.UI.UiAssets)
local SpriteLoader = require(script.Parent.Parent.SpriteLoader)
local Widgets = require(script.Parent.Parent.Widgets)
local Core = require(script.Parent.Core)
local Tokens = require(script.Parent.Tokens)

local Art = {}

Art.ROLES = KitModel.ROLES

-- Text stand-ins for icons by id (lk_icon_<id>), drawn in ink before upload.
Art.GLYPHS = {
	coin = "●",
	gem = "◆",
	gear = "⚙",
	gear_alt = "⚙",
	backpack = "▤",
	portal = "◎",
	scroll = "✉",
	market = "⌂",
	anvil = "⚒",
	trade = "⇄",
	crown = "♛",
	star = "★",
	heart = "♥",
	lightning = "⚡",
	lock = "🔒",
	check = "✓",
	cross = "✕",
	warning = "!",
	exclamation = "!",
	magnifier = "⌕",
	map = "▦",
	map_pin = "⌖",
	party = "☺",
	trophy = "♕",
	journal = "▤",
	clock = "◷",
	plus = "+",
	minus = "−",
	arrow_left = "←",
	arrow_right = "→",
	arrow_up = "↑",
	arrow_down = "↓",
	play = "▶",
	invite = "+",
	chevron_right = "›",
	tree = "♣",
	play_rune = "▶",
	play_rune_small = "▶",
}

-- The sprite of an icon id: lk_icon_<id>, else lk_glyph_<id> (the flat glyph
-- first when `preferGlyph`, as on square buttons), else the id itself when it
-- already names a sprite. "ink:<id>" and "white:<id>" name the flat glyphs
-- built by art/ui/capture/glyphs.py (lk_glyph_ink_<id>, lk_glyph_white_<id>).
-- A role name ("icon.playRune") gives the role's sprite, or its `fallback`
-- icon while that sprite has no art (not uploaded yet). nil when the kit has
-- no such art.
function Art.IconSprite(id: string, preferGlyph: boolean?): string?
	local role = KitModel.ROLES[id]
	if role and role.sprite then
		if role.fallback and not Widgets.HasArt(role.sprite) then
			return Art.IconSprite(role.fallback, preferGlyph) or role.sprite
		end
		return role.sprite
	end
	if string.sub(id, 1, 3) == "lk_" then
		return id
	end
	local colour, glyph = string.match(id, "^(%a+):([%w_]+)$")
	if colour then
		return "lk_glyph_" .. colour .. "_" .. glyph
	end
	local order = if preferGlyph
		then { "lk_glyph_" .. id, "lk_icon_" .. id }
		else { "lk_icon_" .. id, "lk_glyph_" .. id }
	for _, name in order do
		if UiAssets.sprite(name) or Widgets.HasArt(name) then
			return name
		end
	end
	return nil
end

-- True when `sprite` draws as art (uploaded, or previewed in a capture).
Art.HasArt = Widgets.HasArt

-- Seconds an uploaded image may take before its part shows the kit's
-- stand-in instead of nothing.
Art.GRACE = 2

-- Whether image `id` may be drawn for a part made at os.clock() `born`
-- (KitModel.ArtMode over SpriteLoader's state).
function Art.ArtReady(id: string, born: number): boolean
	return KitModel.ArtMode(SpriteLoader.State(id), os.clock() - born, Art.GRACE) == "art"
end

-- The natural size {w, h} of a sprite, or nil when the manifest lacks it.
function Art.SizeOf(sprite: string?): (number?, number?)
	local entry = sprite and UiAssets.sprite(sprite)
	if entry then
		return entry.w, entry.h
	end
	return nil, nil
end

-- The 9-slice corner scale for `sprite` drawn at w × h (nil when it does not slice).
function Art.SliceScale(sprite: string, w: number, h: number): number?
	local entry = UiAssets.sprite(sprite)
	if entry == nil or type(entry.slice) ~= "table" then
		return nil
	end
	return HudModel.SliceScale(entry.w, entry.h, w, h)
end

local function isLeather(sprite: string?, material: string): boolean
	if sprite == nil then
		return material == "leather"
	end
	return string.find(sprite, "leather") ~= nil
		or string.find(sprite, "close") ~= nil
		or string.find(sprite, "badge_number") ~= nil
		or string.find(sprite, "scroll_thumb") ~= nil
		or string.find(sprite, "clasp") ~= nil
end

-- The stand-in's fill token for a material in a state.
local function standInFill(material: string, leather: boolean, state: string, role): string?
	if material == "fill" or material == "dot" or material == "pill" then
		return role.fill or "xp"
	elseif material == "track" then
		return "track"
	elseif material == "rule" or material == "glyph" or material == "none" or material == "deco" then
		return nil
	elseif leather then
		return ({
			hover = "leatherHover",
			focused = "leatherHover",
			pressed = "leatherPressed",
			disabled = "leatherDisabled",
			locked = "leatherDisabled",
			busy = "leatherDisabled",
		})[state] or "leather"
	elseif material == "slot" then
		return if state == "disabled" or state == "locked" then "paperDisabled" else "slot"
	end
	return ({
		hover = "paperLight",
		focused = "paperLight",
		selected = "paperSelected",
		disabled = "paperDisabled",
		locked = "paperDisabled",
		busy = "paperDisabled",
	})[state] or "paper"
end

-- Draws the stand-in for `role` in `state` into `frame` (re-used across states).
local function paintStandIn(frame: Frame, roleName: string, state: string, w: number, h: number)
	local role = Art.ROLES[roleName] or { material = "paper" }
	local material = role.material or "paper"
	local sprite = KitModel.ArtFor(roleName, state)
	local leather = isLeather(sprite, material)
	local fill = standInFill(material, leather, state, role)
	local stroke = frame:FindFirstChild("Edge") :: UIStroke?
	local corner = frame:FindFirstChild("Round") :: UICorner?
	local glyph = frame:FindFirstChild("Glyph") :: TextLabel?
	local rule = frame:FindFirstChild("Line") :: Frame?
	frame.BackgroundTransparency = if fill then 0 else 1
	if fill then
		local color = Tokens.Color(fill)
		if state == "pressed" and not leather then
			color = Tokens.Multiply(color, Tokens.Tint("pressed"))
		end
		frame.BackgroundColor3 = color
	end
	local round = Tokens.Space("fallbackCorner", 8)
	local strokeKey, thickness = "paperEdge", Tokens.Space("fallbackStroke", 2)
	if material == "window" then
		round, strokeKey, thickness =
			Tokens.Space("fallbackCornerWindow", 10), "rail", Tokens.Space("fallbackStrokeWindow", 3)
	elseif material == "slot" then
		round = Tokens.Space("fallbackCornerSlot", 6)
	elseif material == "pill" then
		round, strokeKey, thickness = Tokens.Space("pillCorner", 7), role.stroke or "paperEdge", 1.5
	elseif leather then
		strokeKey = "leatherEdge"
	end
	if material == "fill" or material == "dot" or material == "track" then
		corner.CornerRadius = UDim.new(0.5, 0)
	else
		corner.CornerRadius = UDim.new(0, round)
	end
	-- Hover, focus and selection add the gold glow; tracks, fills, dots, rules and
	-- glyphs carry no edge.
	local glowing = state == "hover" or state == "focused" or state == "selected" or state == "capturing"
	-- Decorations (pillars) draw nothing at all until their art arrives.
	local edged = material ~= "fill"
		and material ~= "dot"
		and material ~= "rule"
		and material ~= "glyph"
		and material ~= "deco"
	stroke.Enabled = edged or (glowing and material ~= "deco")
	stroke.Color = Tokens.Color(if glowing then "glow" else strokeKey)
	stroke.Thickness = if glowing then Tokens.Space("glowStroke", 3) else thickness
	if material == "none" and not glowing then
		stroke.Thickness = Tokens.Space("fallbackStrokeWindow", 3)
	end
	rule.Visible = material == "rule"
	if material == "rule" then
		local vertical = h > w
		local thick = role.thickness or 2
		rule.Size = if vertical then UDim2.new(0, thick, 1, 0) else UDim2.new(1, 0, 0, thick)
		rule.BackgroundColor3 = Tokens.Color(role.fill or "divider")
	end
	local text = role.glyph
	if text == nil and material == "glyph" then
		text = "•"
	end
	glyph.Visible = text ~= nil
	if text then
		glyph.Text = text
		glyph.TextColor3 = Tokens.Color(if leather or material == "fill" then "cream" else "ink")
		if state == "disabled" or state == "locked" then
			glyph.TextColor3 = Tokens.Color("muted")
		end
	end
end

local function standIn(roleName: string, w: number, h: number, parent: Instance, z: number): Frame
	local frame = Core.Make("Frame", {
		Name = "StandIn",
		BorderSizePixel = 0,
		Size = UDim2.fromScale(1, 1),
		ZIndex = z,
	}, parent)
	Core.Make("UICorner", { Name = "Round" }, frame)
	Core.Make("UIStroke", { Name = "Edge", ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, frame)
	Core.Make("Frame", {
		Name = "Line",
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundColor3 = Tokens.Color("divider"),
		BorderSizePixel = 0,
		Position = UDim2.fromScale(0.5, 0.5),
		Visible = false,
		ZIndex = z,
	}, frame)
	local glyph = Core.Make("TextLabel", {
		Name = "Glyph",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		Text = "",
		TextScaled = true,
		Visible = false,
		ZIndex = z + 1,
	}, frame)
	glyph.FontFace = Tokens.Font("symbol")
	Widgets.TextCap(glyph, math.max(10, math.floor(math.min(w, h) * 0.7)))
	paintStandIn(frame, roleName, "normal", w, h)
	return frame :: Frame
end

-- One sprite drawn to fill `parent` at design size w × h (9-sliced with its
-- corners scaled to fit). `props` override the image's properties.
-- `sliceScale` overrides the corner scale (a thinner glow ring).
function Art.Sprite(sprite: string, w: number, h: number, parent: Instance, props, sliceScale: number?): GuiObject
	local base = {
		Name = sprite,
		Size = UDim2.fromOffset(w, h),
		ZIndex = 4,
	}
	for key, value in props or {} do
		base[key] = value
	end
	return Widgets.Sprite(sprite, base, parent, sliceScale or Art.SliceScale(sprite, w, h))
end

export type Plate = {
	holder: Frame,
	role: string,
	state: string,
	Show: (self: Plate, state: string) -> (),
	SetRole: (self: Plate, role: string) -> (),
	SetTint: (self: Plate, color: Color3?) -> (),
	SetTransparency: (self: Plate, value: number) -> (),
	Destroy: (self: Plate) -> (),
}

local PlateMethods = {}
PlateMethods.__index = PlateMethods

-- The art of a role in all its states, at design size w × h, filling
-- `parent` (or opts.rect). Each state's sprite is built the first time it is
-- shown and then only toggled, so a state change never rebuilds or refetches.
-- opts: rect {x, y, w, h}, z, tint (a Color3 laid over every state), exact
-- (default true: the art's visible edge sits on the rect; false draws the
-- sprite image itself at the rect, its transparent margin inside).
function Art.Plate(parent: Instance, roleName: string, w: number, h: number, opts): Plate
	opts = opts or {}
	local holder = Core.Make("Frame", {
		Name = "Art",
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		Size = UDim2.fromScale(1, 1),
		ZIndex = opts.z or 4,
	}, parent)
	if opts.rect then
		holder.Position = UDim2.fromOffset(opts.rect[1], opts.rect[2])
		holder.Size = UDim2.fromOffset(opts.rect[3], opts.rect[4])
	end
	local self = setmetatable({
		holder = holder,
		role = roleName,
		state = "",
		w = w,
		h = h,
		z = opts.z or 4,
		tint = opts.tint,
		exact = opts.exact ~= false,
		alpha = 0,
		variants = {},
		born = os.clock(),
		watches = {},
	}, PlateMethods)
	self:Show("normal")
	return self :: any
end

-- Materials whose art is placed as stored (lines, fills, dots and glyphs
-- sit inside their rect by design).
local AS_STORED = { rule = true, fill = true, dot = true, glyph = true, deco = true }

-- How far (design px per side) a sprite is drawn outside the plate so its
-- visible edge lands on the plate's rect: KitModel.EDGES at the sprite's scale.
function Art.Outset(roleName: string, sprite: string, w: number, h: number): { number }
	local role = Art.ROLES[roleName]
	if role == nil or role.edge == false or AS_STORED[role.material] then
		return { 0, 0, 0, 0 }
	end
	local edge = KitModel.Edge(sprite)
	local nw, nh = Art.SizeOf(sprite)
	if nw == nil or nh == nil then
		return { 0, 0, 0, 0 }
	end
	-- 9-sliced art keeps its corners at the slice scale; fitted art scales whole.
	local k = Art.SliceScale(sprite, w, h) or math.min(w / nw, h / nh)
	k *= Art.Thin(roleName, sprite)
	return { edge[1] * k, edge[2] * k, edge[3] * k, edge[4] * k }
end

-- The extra corner scale a role draws a state's art at (role.thin), else 1.
function Art.Thin(roleName: string, sprite: string): number
	local role = Art.ROLES[roleName]
	return role and role.thin and role.thin[sprite] or 1
end

function PlateMethods:_variant(sprite: string): GuiObject
	local variant = self.variants[sprite]
	if variant then
		return variant
	end
	if sprite ~= "native" and Widgets.HasArt(sprite) then
		-- A state's art may be drawn larger than the plate (a slot's glow ring),
		-- and every plate is outset so its visible edge sits on the rect.
		local role = Art.ROLES[self.role]
		local grow = role and role.grow and role.grow[sprite] or 0
		local out = if self.exact then Art.Outset(self.role, sprite, self.w, self.h) else { 0, 0, 0, 0 }
		local l, t = grow + out[1], grow + out[2]
		local dw, dh = grow * 2 + out[1] + out[3], grow * 2 + out[2] + out[4]
		local thin = Art.Thin(self.role, sprite)
		local slice = Art.SliceScale(sprite, self.w + dw, self.h + dh)
		variant = Art.Sprite(sprite, self.w + dw, self.h + dh, self.holder, {
			Name = sprite,
			Position = UDim2.fromOffset(-l, -t),
			Size = UDim2.new(1, dw, 1, dh),
			ZIndex = self.z,
		}, if slice and thin ~= 1 then slice * thin else nil)
	else
		variant = standIn(self.role, self.w, self.h, self.holder, self.z)
		variant.Name = sprite
	end
	self.variants[sprite] = variant
	return variant
end

local function tintOf(state: string, borrowed: boolean): Color3
	if not borrowed then
		return Color3.new(1, 1, 1)
	end
	local key = KitModel.STATE_TINT[state]
	return if key then Tokens.Tint(key) else Color3.new(1, 1, 1)
end

-- Draws the role in `state`.
function PlateMethods:Show(state: string)
	self.state = state
	local role = Art.ROLES[self.role]
	local sprite, borrowed = KitModel.ArtFor(self.role, state)
	if role and role.native then
		-- Drawn as a flat kit shape by design (plain rules, discs, thin rails).
		sprite, borrowed = "native", false
	end
	local shown = nil
	if sprite and sprite ~= "native" and Widgets.HasArt(sprite) and not self:_artReady(sprite) then
		-- Uploaded art that has not arrived (or failed): the kit's stand-in.
		shown = self:_standIn()
	else
		shown = sprite and self:_variant(sprite)
	end
	for _, variant in self.variants do
		variant.Visible = variant == shown
	end
	if shown == nil then
		return
	end
	if shown.Name == sprite and shown:IsA("ImageLabel") then
		local color = tintOf(state, borrowed)
		if self.tint then
			color = Tokens.Multiply(color, self.tint)
		end
		-- Leather has two tones in the mockups: the sprite's own (bright: PLAY,
		-- APPLY) and the leatherTint most buttons and tabs draw at (EQUIP,
		-- CLAIM, Invite), with leatherDark for the darkest (FORGE, Party
		-- CLOSE). A plate's tone (Plate:SetTone, Button `tone`) picks one.
		if isLeather(sprite, "") then
			color = Tokens.Multiply(color, Tokens.Color(self.tone or "leatherTint"))
		end
		shown.ImageColor3 = color
		shown.ImageTransparency = self.alpha
	elseif shown:IsA("Frame") and shown:FindFirstChild("Edge") then
		paintStandIn(shown :: Frame, self.role, state, self.w, self.h)
		if self.tint and shown.BackgroundTransparency < 1 then
			shown.BackgroundColor3 = Tokens.Multiply(shown.BackgroundColor3, self.tint)
		end
	end
end

-- Switches to another role (a primary button turned secondary) and redraws.
function PlateMethods:SetRole(roleName: string)
	if roleName == self.role then
		return
	end
	for _, variant in self.variants do
		variant:Destroy()
	end
	self.variants = {}
	self.role = roleName
	self:Show(self.state)
end

-- A colour laid over the art in every state (Leader tag gold), or nil.
function PlateMethods:SetTint(color: Color3?)
	self.tint = color
	self:Show(self.state)
end

-- The leather tone token ("leatherBright" | "leatherTint" | "leatherDark").
function PlateMethods:SetTone(token: string?)
	self.tone = token
	self:Show(self.state)
end

function PlateMethods:SetTransparency(value: number)
	self.alpha = value
	self:Show(self.state)
end

function PlateMethods:Destroy()
	self:_unwatch()
	self.holder:Destroy()
end

-- The one stand-in frame this plate draws while its art's image is missing.
function PlateMethods:_standIn(): GuiObject
	local frame = self.variants.__standIn
	if frame == nil then
		frame = standIn(self.role, self.w, self.h, self.holder, self.z)
		frame.Name = "StandIn"
		self.variants.__standIn = frame
	end
	return frame
end

-- Whether `sprite`'s image may be drawn now (Art.ArtReady); watches the
-- image so the plate redraws when it loads or fails.
function PlateMethods:_artReady(sprite: string): boolean
	local id = Widgets.ImageId(sprite)
	if id == nil then
		return true
	end
	local ready = Art.ArtReady(id, self.born)
	if not ready or SpriteLoader.State(id) ~= "loaded" then
		self:_watch(id)
	end
	return ready
end

function PlateMethods:_watch(id: string)
	if self.watches[id] then
		return
	end
	local function redraw()
		if self.holder.Parent then
			self:Show(self.state)
		end
	end
	local stop = SpriteLoader.OnState(id, redraw)
	self.watches[id] = stop
	-- Past the grace period a still-missing image shows the stand-in.
	task.delay(Art.GRACE, redraw)
	if self.unwatchOnDestroy == nil then
		self.unwatchOnDestroy = self.holder.Destroying:Connect(function()
			self:_unwatch()
		end)
	end
end

function PlateMethods:_unwatch()
	for id, stop in self.watches do
		stop()
		self.watches[id] = nil
	end
end

-- Glyphs drawn white (for leather); on paper they are tinted ink.
Art.WHITE_GLYPHS = { lk_glyph_play = true, lk_glyph_check_white = true, lk_icon_backpack_white = true }

-- An icon by id (lk_icon_<id> / lk_glyph_<id> / "ink:<id>" / "white:<id>")
-- at rect, fitted. opts: tint (colour token), color (a Color3 tint, item
-- recolours), glyph (prefer the flat glyph), transparency, standInScale (the
-- ink glyph's size as a share of the rect, 0.8), z, name. Before upload, or
-- while its uploaded image is not served, it is its glyph in ink.
local function glyphLabel(parent: Instance, sprite: string?, id: string, rect, opts, z: number): TextLabel
	local short = if sprite then string.gsub(string.gsub(sprite, "^lk_icon_", ""), "^lk_glyph_", "") else id
	short = string.gsub(short, "^%a+_", function(prefix)
		return if prefix == "ink_" or prefix == "white_" then "" else prefix
	end)
	short = string.gsub(short, "_white$", "")
	local glyph = Core.Make("TextLabel", {
		Name = opts.name or "Icon",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(rect[1], rect[2]),
		Size = UDim2.fromOffset(rect[3], rect[4]),
		Text = Art.GLYPHS[short] or string.upper(string.sub(short, 1, 1)),
		TextColor3 = Tokens.Color(opts.tint or "ink"),
		TextScaled = true,
		ZIndex = z,
	}, parent)
	glyph.FontFace = Tokens.Font("symbol")
	Widgets.TextCap(glyph, math.max(10, math.floor(math.min(rect[3], rect[4]) * (opts.standInScale or 0.8))))
	return glyph
end

function Art.Icon(parent: Instance, id: string, rect, opts): GuiObject
	opts = opts or {}
	local sprite = Art.IconSprite(id, opts.glyph)
	local z = opts.z or 5
	if sprite and Widgets.HasArt(sprite) then
		local image = Art.Sprite(sprite, rect[3], rect[4], parent, {
			Name = opts.name or "Icon",
			Position = UDim2.fromOffset(rect[1], rect[2]),
			ZIndex = z,
			ScaleType = Enum.ScaleType.Fit,
		})
		if image:IsA("ImageLabel") then
			if opts.tint then
				image.ImageColor3 = Tokens.Color(opts.tint)
			elseif opts.color then
				image.ImageColor3 = opts.color
			end
			if opts.transparency then
				image.ImageTransparency = opts.transparency
			end
		end
		-- An image not loaded yet: its ink glyph stands in (after the grace, or at
		-- once when the fetch failed) until the art arrives.
		local imageId = Widgets.ImageId(sprite)
		if imageId and SpriteLoader.State(imageId) ~= "loaded" then
			local born = os.clock()
			local glyph = glyphLabel(parent, sprite, id, rect, opts, z)
			glyph.Name = (opts.name or "Icon") .. "StandIn"
			local function update()
				local ready = Art.ArtReady(imageId, born)
				image.Visible = ready
				glyph.Visible = not ready
			end
			local stop = SpriteLoader.OnState(imageId, update)
			task.delay(Art.GRACE, function()
				if image.Parent then
					update()
				end
			end)
			-- The glyph follows the image when its owner moves it (a button's
			-- icon is placed after it is made).
			for _, key in { "Position", "Size", "AnchorPoint" } do
				image:GetPropertyChangedSignal(key):Connect(function()
					local value = (image :: any)[key];
					(glyph :: any)[key] = value
				end)
			end
			image.Destroying:Connect(function()
				stop()
				glyph:Destroy()
			end)
			update()
		end
		return image
	end
	return glyphLabel(parent, sprite, id, rect, opts, z)
end

-- The sprite (and optional Color3 tint) ItemInfo.Icon / ItemInfo.Sprite give a
-- catalog item, when the kit can draw it; nil otherwise.
function Art.ItemIcon(catalogId: string?): (string?, Color3?)
	if catalogId == nil then
		return nil, nil
	end
	local ok, icon, tint = pcall(ItemInfo.Icon, catalogId)
	if not ok or type(icon) ~= "string" then
		return nil, nil
	end
	local sprite = ItemInfo.Sprite(icon)
	if UiAssets.sprite(sprite) == nil and not Widgets.HasArt(sprite) then
		return nil, nil
	end
	return sprite, if typeof(tint) == "Color3" then tint else nil
end

-- The sprite of a catalog item: lk_item_<id>, then item_<id>; nil when neither
-- has art or a manifest entry (ItemIcon then writes the item's name in ink).
function Art.ItemSprite(catalogId: string?): string?
	if catalogId == nil then
		return nil
	end
	for _, name in { "lk_item_" .. catalogId, "item_" .. catalogId } do
		if Widgets.HasArt(name) then
			return name
		end
	end
	return nil
end

-- How faded an item's kind glyph draws when the item has no art: it reads as
-- "picture missing", never as a real item.
Art.STAND_IN_FADE = 0.6

-- The neutral glyph for an item without art, by its kind (drawn faded):
-- tools and weapons a hammer, armour a backpack, everything else a chest.
function Art.KindGlyph(catalogId: string?): string
	local entry = catalogId and ItemCatalog.Get(catalogId)
	if entry == nil then
		return "ink:chest"
	elseif entry.weapon or entry.tool then
		return "ink:hammer"
	elseif entry.armor then
		return "ink:backpack"
	end
	return "ink:chest"
end

function Art.ItemName(catalogId: string?): string
	local entry = catalogId and ItemCatalog.Get(catalogId)
	return entry and entry.name or catalogId or ""
end

-- Every role sprite the manifest lacks (UiSprites.json, or the capture's
-- preview of art/ui/sprites/manifest.json). Empty when the table is complete.
function Art.Missing(): { string }
	local missing = {}
	for _, name in KitModel.Sprites() do
		if UiAssets.sprite(name) == nil then
			table.insert(missing, name)
		end
	end
	return missing
end

return Art
