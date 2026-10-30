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
	for name, role in KitModel.ROLES do
		expect(role.sprite ~= nil or role.states ~= nil, name .. " has art")
		expect(MATERIALS[role.material] == true, name .. " material " .. tostring(role.material))
		if role.sprite then
			expect(string.match(role.sprite, "^lk_[%w_]+$") ~= nil, name .. " sprite " .. role.sprite)
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

test("the sprite list is sorted and unique", function()
	local list = KitModel.Sprites()
	expect(#list > 60, "many sprites")
	for i = 2, #list do
		expect(list[i - 1] < list[i], "sorted and unique at " .. list[i])
	end
end)
