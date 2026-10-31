local Shared = game:GetService("ReplicatedStorage").Shared
local KitModel = require(Shared.UI.KitModel)

local MATERIALS = {
	paper = true,
	leather = true,
	slot = true,
	window = true,
	track = true,
	fill = true,
	dot = true,
	rule = true,
	glyph = true,
	none = true,
	pill = true,
}

-- Roles every component draws from; a missing one would draw nothing.
local USED = {
	"window.frame",
	"window.claspLeft",
	"window.claspRight",
	"window.plaque",
	"dialog.frame",
	"toast.frame",
	"tooltip.box",
	"tooltip.tail",
	"panel.inset",
	"panel.card",
	"button.primary",
	"button.secondary",
	"button.play",
	"button.playSecondary",
	"iconButton.close",
	"iconButton.paper",
	"iconButton.leather",
	"iconButton.tile",
	"iconButton.plus",
	"iconButton.minus",
	"tab.category",
	"tab.arrow",
	"tab.horizontal",
	"tab.side",
	"slot.item",
	"slot.hotbar",
	"badge.number",
	"badge.count",
	"badge.countWide",
	"badge.pill",
	"dot.green",
	"dot.grey",
	"dot.red",
	"bar.track",
	"bar.fill.yellow",
	"bar.fill.red",
	"bar.fill.green",
	"bar.fill.orange",
	"bar.fill.blue",
	"bar.frame",
	"bar.frameThin",
	"bar.stat",
	"bar.statPlate",
	"checkbox.off",
	"checkbox.on",
	"check.tileOff",
	"check.tileOn",
	"toggle.off",
	"toggle.on",
	"slider.track",
	"slider.trackPaper",
	"slider.fill",
	"slider.knob",
	"slider.knobRound",
	"field.value",
	"dropdown.field",
	"dropdown.list",
	"search.field",
	"keycap.cap",
	"keycap.wide",
	"keycap.flat",
	"scroll.track",
	"scroll.thumb",
	"divider.rule",
	"divider.ornate",
	"divider.diamond",
	"divider.vertical",
	"row.plate",
	"currency.pill",
	"portrait.square",
	"portrait.round",
	"portrait.empty",
	"mark.lock",
	"mark.crown",
	"mark.star",
	"mark.chevron",
	"mark.cross",
	"divider.ink",
	"divider.hairline",
	"row.soft",
	"check.ringOff",
	"check.ringOn",
	"scroll.thinTrack",
	"scroll.thinThumb",
	"hud.playerCard",
	"hud.leaf",
	"panel.party",
	"map.island",
}

test("every role a component draws is in the table", function()
	for _, name in USED do
		expect(KitModel.ROLES[name] ~= nil, "role " .. name)
	end
end)

test("every role names lk_ art, a known material and known states", function()
	local valid = {}
	for _, state in KitModel.STATES do
		valid[state] = true
	end
	-- Painted art from outside the lk_ kit that a role may name.
	local PAINTED = { pm_map_island = true }
	for name, role in KitModel.ROLES do
		if role.native then
			expect(role.sprite == nil and role.states == nil, name .. " is drawn natively, without art")
			expect(type(role.fill) == "string", name .. " has a colour")
		else
			expect(role.sprite ~= nil or role.states ~= nil, name .. " has art")
		end
		expect(MATERIALS[role.material] == true, name .. " material " .. tostring(role.material))
		if role.sprite then
			expect(
				string.match(role.sprite, "^lk_[%w_]+$") ~= nil or PAINTED[role.sprite],
				name .. " sprite " .. role.sprite
			)
		end
		for state, sprite in role.states or {} do
			expect(valid[state] == true, name .. " state " .. tostring(state))
			expect(string.match(sprite, "^lk_[%w_]+$") ~= nil, name .. " " .. state .. " sprite " .. sprite)
		end
		for sprite, px in role.grow or {} do
			local found = role.sprite == sprite
			for _, other in role.states or {} do
				found = found or other == sprite
			end
			expect(found, name .. " grows its own art " .. sprite)
			expect(type(px) == "number" and px >= 0 and px <= 8, name .. " grow in px")
		end
		if role.material == "fill" or role.material == "dot" then
			expect(type(role.fill) == "string", name .. " has a stand-in colour")
		end
	end
end)

test("state families keep one plate per state (sheets 03, 05, 09)", function()
	local leather = KitModel.ROLES["button.primary"].states
	expectEq(leather.hover, "lk_button_leather_hover", "leather hover")
	expectEq(leather.pressed, "lk_button_leather_pressed", "leather pressed")
	expectEq(leather.disabled, "lk_button_leather_disabled", "leather disabled")
	local close = KitModel.ROLES["iconButton.close"].states
	expectEq(close.pressed, "lk_button_close_pressed", "close pressed")
	local hotbar = KitModel.ROLES["slot.hotbar"].states
	for _, state in { "hover", "selected", "disabled", "locked" } do
		expect(hotbar[state] ~= nil, "hotbar slot " .. state)
	end
	expectEq(KitModel.ROLES["tab.horizontal"].states.selected, "lk_button_leather_normal", "a selected tab is leather")
end)

test("every plate sprite has its visible-edge margin", function()
	-- Lines, fills, dots and glyphs are placed as stored (Art.Outset).
	local asStored = { rule = true, fill = true, dot = true, glyph = true }
	for name, role in KitModel.ROLES do
		local sprite = role.sprite
		if
			not asStored[role.material]
			and sprite
			and string.sub(sprite, 1, 3) == "lk_"
			and role.edge ~= false
			and not string.find(sprite, "^lk_icon_")
			and not string.find(sprite, "^lk_glyph_")
			and not string.find(sprite, "^lk_dot_")
		then
			local edge = KitModel.EDGES[sprite]
			expect(edge ~= nil, name .. " has EDGES for " .. sprite)
			if edge then
				for i = 1, 4 do
					expect(edge[i] >= 0 and edge[i] <= 12, name .. " edge " .. i)
				end
			end
		end
	end
	expectEq(KitModel.Edge("lk_window_frame")[1], 5, "the window frame's edge is 5 px in")
	expectEq(KitModel.Edge(nil)[1], 0, "unknown sprites have no margin")
end)

test("the sprite list is sorted and unique", function()
	local list = KitModel.Sprites()
	expect(#list > 60, "many sprites")
	for i = 2, #list do
		expect(list[i - 1] < list[i], "sorted and unique at " .. list[i])
	end
end)
