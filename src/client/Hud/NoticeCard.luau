-- A notice card built from the kit (sheet 13's parchment card with leather
-- corners): an optional emblem, a title, wrapping text, an optional bar and
-- buttons, and an optional close ✕. The card grows with its text. Used for
-- server notices, trade invites, the safe-camp note and the in-run status cards
-- (downed, extraction, tutorial, boss, boosts), in the shared top-centre column
-- (Theme.TopStack) or a gui of their own. Sizes are design px (1672 × 941); the
-- gui holding the card scales it.
--
--   local card = NoticeCard.new(Theme.TopStack(), { name = "Downed", icon = "heart", width = 460 })
--   card:SetBar(0.4, "red")
--   card:Show("Bleeding out in 24 s", "Downed")

local Kit = require(script.Parent.Kit)

local NoticeCard = {}
NoticeCard.__index = NoticeCard

local PAD_X, PAD_TOP, PAD_BOTTOM = 26, 18, 20
local ICON = 52
local TITLE_H = 32
local GAP = 6
local BAR_H = 26
local BUTTON_H = 46
local BUTTON_W = 160
local KEY_H = 34

-- Layout colour keys the older callers pass to SetTone, as kit tokens.
local TONES = { haveEnough = "toggleOn", haveShort = "short" }

-- How many lines `text` wraps to in `width` design px in a type role.
function NoticeCard.Lines(text: string, role: string, width: number, size: number?): number
	local count = 0
	local space = Kit.Text.Width(" ", role, size)
	for line in string.gmatch(text .. "\n", "(.-)\n") do
		local lines, used = 1, 0
		for word in string.gmatch(line, "%S+") do
			local wordW = Kit.Text.Width(word, role, size)
			if used > 0 and used + space + wordW > width then
				lines += 1
				used = wordW
			else
				used += (if used > 0 then space else 0) + wordW
			end
		end
		count += lines
	end
	return math.max(count, 1)
end

-- opts: name, width (design px, default 440), layoutOrder, title (nil for text
-- only), icon (an emblem icon id), textRole ("body"), onPress (the whole card
-- acts when pressed; omit when it has buttons), onClose (shows the ✕).
function NoticeCard.new(parent: Instance, opts)
	local self = setmetatable({}, NoticeCard)
	self.w = opts.width or 440
	self.h = 0
	self.icon = opts.icon
	self.textRole = opts.textRole or "body"
	self.onClose = opts.onClose
	self.frame = Kit.Core.Make("Frame", {
		Name = opts.name or "Notice",
		BackgroundTransparency = 1,
		LayoutOrder = opts.layoutOrder or 0,
		Size = UDim2.fromOffset(self.w, 120),
		Visible = false,
		ZIndex = 1,
	}, parent) :: Frame
	-- Holds the title, text, bar and buttons above the card art.
	self.body = Kit.Core.Make("Frame", {
		Name = "Body",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		ZIndex = 6,
	}, self.frame)
	local textX = PAD_X + (if self.icon then ICON + 14 else 0)
	local right = if opts.onClose or opts.onPress then 52 else PAD_X
	self.textX = textX
	self.textW = self.w - textX - right
	self.titleText = Kit.Text.new(self.body, {
		name = "Title",
		rect = { textX, PAD_TOP, self.textW, TITLE_H },
		text = opts.title or "",
		role = "itemTitle",
		textSize = 24,
		caps = true,
		scaled = true,
		zIndex = 7,
	})
	self.title = self.titleText.root
	self.title.Visible = opts.title ~= nil and opts.title ~= ""
	self.lines = Kit.Text.new(self.body, {
		name = "Text",
		rect = { textX, PAD_TOP, self.textW, 20 },
		text = "",
		role = self.textRole,
		wrap = true,
		yAlign = "Top",
		zIndex = 7,
	})
	self.text = self.lines.root
	if self.icon then
		self.emblem =
			Kit.Icon.new(self.body, { name = "Emblem", rect = { PAD_X, PAD_TOP, ICON, ICON }, icon = self.icon })
	end
	if opts.onPress then
		local press = Kit.Core.Make("TextButton", {
			Name = "Press",
			AutoButtonColor = false,
			BackgroundTransparency = 1,
			Size = UDim2.fromScale(1, 1),
			Text = "",
			ZIndex = 8,
		}, self.frame)
		press.Activated:Connect(opts.onPress)
	end
	if opts.onClose or opts.onPress then
		self.close = Kit.IconButton.new(self.body, {
			name = "Close",
			variant = "close",
			rect = { self.w - 48, 12, 36, 36 },
			zIndex = 9,
			onPress = opts.onClose or opts.onPress,
		})
	end
	self.buttons = nil
	self.buttonList = {}
	self:_layout()
	return self
end

-- Lays the parts out for the current text and rebuilds the card art when the
-- height changed.
function NoticeCard:_layout()
	local y = PAD_TOP
	if self.title.Visible then
		self.title.Position = UDim2.fromOffset(self.textX, y)
		y += TITLE_H + 2
	end
	local hasText = self.text.Text ~= ""
	self.text.Visible = hasText
	if hasText then
		local style = Kit.Tokens.TextStyle(self.textRole)
		local lineH = math.ceil(style.size * 1.35)
		local lines = NoticeCard.Lines(self.text.Text, self.textRole, self.textW)
		self.text.Position = UDim2.fromOffset(self.textX, y)
		self.text.Size = UDim2.fromOffset(self.textW, lines * lineH)
		y += lines * lineH
	end
	if self.icon then
		y = math.max(y, PAD_TOP + ICON)
	end
	if self.bar then
		y += GAP + 2
		self.bar.root.Position = UDim2.fromOffset(self.textX, y)
		y += BAR_H
	end
	if self.keys then
		y += GAP + 2
		self.keys.Position = UDim2.fromOffset(self.textX, y)
		y += KEY_H
	end
	if self.buttons and self.buttons.Visible then
		y += GAP + 6
		self.buttons.Position = UDim2.fromOffset(self.textX, y)
		y += BUTTON_H
	end
	local h = math.max(y + PAD_BOTTOM, 72)
	if h ~= self.h then
		self.h = h
		self.frame.Size = UDim2.fromOffset(self.w, h)
		if self.panel then
			self.panel:Destroy()
		end
		self.panel =
			Kit.Panel.new(self.frame, { name = "Card", rect = { 0, 0, self.w, h }, variant = "card", zIndex = 2 })
	end
end

-- A button under the text: kind "leather" (default, primary) or "paper"
-- (secondary).
function NoticeCard:AddButton(label: string, kind: string?, onPress)
	if self.buttons == nil then
		self.buttons = Kit.Core.Make("Frame", {
			Name = "Buttons",
			BackgroundTransparency = 1,
			Size = UDim2.fromOffset(self.textW, BUTTON_H),
			ZIndex = 7,
		}, self.body)
	end
	local button = Kit.Button.new(self.buttons, {
		name = label,
		rect = { 0, 0, BUTTON_W, BUTTON_H },
		label = label,
		variant = if kind == "paper" then "secondary" else "primary",
		sizeClass = "s",
		zIndex = 8,
		onPress = onPress,
	})
	table.insert(self.buttonList, button)
	self:_flowButtons()
	return button
end

-- Places the visible buttons side by side; the row takes no room without any.
function NoticeCard:_flowButtons()
	local x = 0
	for _, button in self.buttonList do
		if button.root.Visible then
			button.root.Position = UDim2.fromOffset(x, 0)
			x += BUTTON_W + 12
		end
	end
	self.buttons.Visible = x > 0
	self:_layout()
end

-- Shows or hides a button AddButton returned.
function NoticeCard:SetButtonVisible(button, visible: boolean)
	if button.root.Visible ~= visible then
		button.root.Visible = visible
		self:_flowButtons()
	end
end

-- Key hints under the text: {{key = "E", label = "Interact"}, …}, drawn as
-- kit key caps; an empty list removes them.
function NoticeCard:SetKeys(keys: { { key: string, label: string } })
	local signature = ""
	for _, entry in keys do
		signature ..= entry.key .. "=" .. entry.label .. ";"
	end
	if signature == self.keySignature then
		return
	end
	self.keySignature = signature
	if self.keys then
		self.keys:Destroy()
		self.keys = nil
	end
	if #keys > 0 then
		self.keys = Kit.Core.Make("Frame", {
			Name = "Keys",
			BackgroundTransparency = 1,
			Size = UDim2.fromOffset(self.textW, KEY_H),
			ZIndex = 7,
		}, self.body)
		local x = 0
		for index, entry in keys do
			local cap = Kit.KeyCap.new(self.keys, {
				name = "Key" .. index,
				rect = { x, 0, 0, KEY_H },
				text = entry.key,
				zIndex = 8,
			})
			x += cap.w + 8
			local labelW = math.ceil(Kit.Text.Width(entry.label, "rowLabel")) + 4
			Kit.Text.new(self.keys, {
				name = "KeyLabel" .. index,
				rect = { x, 0, labelW, KEY_H },
				text = entry.label,
				role = "rowLabel",
				zIndex = 8,
			})
			x += labelW + 18
		end
	end
	self:_layout()
end

-- A progress bar under the text (fill: a Kit.Bar fill); nil removes it.
function NoticeCard:SetBar(fraction: number?, fill: string?, text: string?)
	if fraction == nil then
		if self.bar then
			self.bar:Destroy()
			self.bar = nil
			self:_layout()
		end
		return
	end
	if self.bar and self.barFill ~= fill then
		self.bar:Destroy()
		self.bar = nil
	end
	if self.bar == nil then
		self.barFill = fill
		self.bar = Kit.Bar.new(self.body, {
			name = "Bar",
			rect = { self.textX, 0, self.textW, BAR_H },
			fill = fill or "xp",
			frame = "track",
			text = text,
			textColor = "cream",
			zIndex = 7,
		})
		self.bar:Set(fraction, true)
		self:_layout()
	else
		self.bar:Set(fraction)
		if text then
			self.bar:SetText(text)
		end
	end
end

-- Sets the text (and the title when given) and shows the card.
function NoticeCard:Show(text: string, title: string?)
	local changed = self.text.Text ~= text
	if title ~= nil then
		local visible = title ~= ""
		if self.title.Visible ~= visible then
			changed = true
		end
		self.titleText:SetText(title)
		self.title.Visible = visible
	end
	self.lines:SetText(text)
	if changed then
		self:_layout()
	end
	self.frame.Visible = true
end

function NoticeCard:Hide()
	self.frame.Visible = false
end

function NoticeCard:IsShown(): boolean
	return self.frame.Visible
end

-- The colour of the title: a kit colour token, or the older layout keys
-- "haveEnough" / "haveShort".
function NoticeCard:SetTone(colorKey: string)
	self.titleText:SetColor(TONES[colorKey] or colorKey)
end

-- Swaps the emblem icon (when the card was built with one).
function NoticeCard:SetIcon(icon: string)
	if self.emblem and icon ~= self.iconNow then
		self.iconNow = icon
		self.emblem:SetIcon(icon)
	end
end

function NoticeCard:Destroy()
	self.frame:Destroy()
end

return NoticeCard
