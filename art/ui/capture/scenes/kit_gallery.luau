-- The UI kit gallery (docs/ui/KIT.md): every Kit component in every state at
-- 1672 × 941, one page per family, for comparison with the kit sheets in
-- art/reference/ui/lobby/kit. States are forced through the DebugState
-- attribute, as verifiers do. Run with --uploaded-only --suffix _fallback for
-- the stand-ins drawn before upload.
--
--   1 window: an Inventory-sized window placed where M02 has it, over the
--     lobby mockup, with tabs, search, category tabs, slots and a detail card
--   2 buttons, icon buttons, badges and tags, currency pills, key caps
--   3 tabs, slots, dividers
--   4 bars, checkboxes, toggles, sliders, dropdown, search, stepper
--   5 list rows, player rows, portraits, panels, section headers, scroll
--   6 toast, confirm dialog, tooltip, plaque and centred window headers

local Players = game:GetService("Players")
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local Kit = require(Hud.Kit)

local W, H = 1672, 941

-- Every role resolves to a sprite the manifest knows.
local missing = Kit.Art.Missing()
assert(#missing == 0, "roles without a manifest sprite: " .. table.concat(missing, ", "))

local function page()
	local gui, root = __screen(W, H)
	return gui, root
end

local function caption(parent, text, x, y, w)
	return Kit.Core.Label(parent, {
		text = text,
		role = "label",
		rect = { x, y, w or 200, 18 },
		z = 20,
	})
end

local function heading(parent, text, x, y)
	return Kit.Core.Label(parent, {
		text = text,
		role = "sectionHeader",
		color = "cream",
		rect = { x, y, 600, 30 },
		z = 20,
	})
end

local function force(component, state)
	component.root:SetAttribute("DebugState", state)
	return component
end

local STATES = { "normal", "hover", "pressed", "disabled" }

-- Page 1: window -------------------------------------------------------------------------

do
	local screen = Kit.Screen.new("FlintbornInventory", { size = { 1187, 652 } })
	local window =
		Kit.Window.new(screen, { title = "Inventory", icon = "backpack", clasps = "right", claspYs = { 0.18, 0.9 } })
	local v = window.base.visual
	local tabs = {
		Kit.Tab.new(v, {
			id = "backpack",
			rect = { 19, 108, 170, 58 },
			label = "Backpack",
			icon = "backpack_white",
			variant = "horizontal",
			zIndex = 8,
		}),
		Kit.Tab.new(v, {
			id = "vault",
			rect = { 198, 109, 165, 56 },
			label = "Vault",
			icon = "chest",
			variant = "horizontal",
			zIndex = 8,
		}),
	}
	Kit.TabGroup.new(tabs):Select("backpack")
	Kit.SearchBox.new(v, { rect = { 23, 179, 215, 41 }, placeholder = "Search items...", zIndex = 8 })
	local categories = {
		{ "All", "chest" },
		{ "Tools", "hammer" },
		{ "Materials", "stones" },
		{ "Food", "drumstick" },
		{ "Plants", "plant_fiber" },
		{ "Misc", "gift" },
	}
	local cats = {}
	for i, entry in categories do
		table.insert(
			cats,
			Kit.Tab.new(v, {
				id = entry[1],
				rect = { 24, 236 + (i - 1) * 64.6, 232, 54 },
				label = entry[1],
				icon = entry[2],
				variant = "category",
				zIndex = 8,
			})
		)
		if i > 1 and i < 6 then
			Kit.Divider.new(v, { rect = { 27, 236 + i * 64.6 - 15, 202, 16 }, variant = "rule", zIndex = 7 })
		end
	end
	Kit.TabGroup.new(cats):Select("All")
	local items = {
		{ "stone_axe", 1 },
		{ "pickaxe", 1 },
		{ "spear", 1 },
		{ "torch", 6 },
		{ "logs", 32 },
		{ "stones", 28 },
		{ "plank", 18 },
		{ "rope", 12 },
		{ "plant_fiber", 8 },
		{ "berries", 14 },
		{ "mushroom", 11 },
		{ "hide", 3 },
		{ "bone", 7 },
		{ "hatchet", 1 },
		{ "stone", 4 },
		{ "log", 9 },
	}
	for i = 1, 24 do
		local col, row = (i - 1) % 6, (i - 1) // 6
		local entry = items[i]
		local slot = Kit.Slot.new(v, {
			rect = { 249 + col * 99.8, 181 + row * 107.3, 92, 99 },
			item = entry and { catalogId = "Gallery" .. i, icon = entry[1], quantity = entry[2] } or nil,
			zIndex = 8,
		})
		if i == 1 then
			slot:SetSelected(true)
		end
	end
	Kit.Divider.new(v, { rect = { 845, 111, 18, 516 }, variant = "vertical", zIndex = 7 })
	local card = Kit.Panel.new(v, { rect = { 869, 109, 296, 520 }, variant = "inset", zIndex = 7 })
	local c = card.base.visual
	Kit.Icon.new(c, { rect = { 73, 30, 152, 166 }, icon = "stone_axe", zIndex = 9 })
	Kit.Text.new(c, { rect = { 19, 210, 258, 34 }, text = "Stone Axe", role = "itemTitle", zIndex = 9 })
	Kit.Text.new(c, {
		rect = { 19, 250, 258, 46 },
		text = "A reliable tool for chopping wood and gathering resources.",
		role = "bodySoft",
		wrap = true,
		yAlign = "Top",
		zIndex = 9,
	})
	local stats =
		{ { "hammer", "Harvest Power", "+10" }, { "clock", "Attack Speed", "0.9s" }, { "backpack_small", "Tier", "1" } }
	for i, stat in stats do
		Kit.ListRow.new(c, {
			rect = { 19, 300 + (i - 1) * 41, 258, 40 },
			variant = "line",
			icon = stat[1],
			title = stat[2],
			value = stat[3],
			zIndex = 9,
		})
	end
	Kit.Button.new(c, { rect = { 14, 450, 270, 61 }, label = "Equip", zIndex = 9 })
	screen:Open()
	screen.holder.Position = UDim2.fromOffset(243 + 1187 / 2, 150 + 652 / 2)
	screen.scale.Scale = 1
	__dump(Players.LocalPlayer.PlayerGui, W, H, { background = "art/reference/ui/lobby/01_hud.png" })
	screen:Destroy()
end

-- Page 2: buttons ----------------------------------------------------------------------------

do
	local gui, root = page()
	heading(
		root,
		"Button: primary / secondary / play / playSecondary × normal, hover, pressed, disabled, busy",
		30,
		14
	)
	local variants = { "primary", "secondary", "play", "playSecondary" }
	local states = { "normal", "hover", "pressed", "disabled", "busy" }
	for r, variant in variants do
		for c, state in states do
			local x, y = 30 + (c - 1) * 250, 70 + (r - 1) * 92
			force(
				Kit.Button.new(root, {
					rect = { x, y, 230, 61 },
					label = if variant == "secondary" then "Reset" else "Equip",
					variant = variant,
				}),
				state
			)
			caption(root, variant .. " · " .. state, x, y + 62)
		end
	end
	heading(root, "With icons, sizes, Invited (D18)", 1290, 14)
	Kit.Button.new(
		root,
		{ rect = { 1290, 70, 340, 76 }, label = "Play", icon = "play", variant = "play", sizeClass = "l" }
	)
	Kit.Button.new(root, { rect = { 1290, 162, 260, 58 }, label = "Confirm", icon = "check_white" })
	Kit.Button.new(root, { rect = { 1290, 236, 108, 42 }, label = "Invite", sizeClass = "s" })
	local invited = Kit.Button.new(root, { rect = { 1410, 236, 108, 42 }, label = "Invite", sizeClass = "s" })
	invited:SetVariant("secondary")
	invited:SetLabel("Invited")
	invited:SetEnabled(false)
	caption(root, "s Invite · Invited (disabled paper)", 1290, 282, 340)

	heading(root, "IconButton × normal, hover, pressed, disabled, selected", 30, 450)
	local icons = {
		{ "close", nil },
		{ "paper", "plus" },
		{ "paper", "minus" },
		{ "paper", "check" },
		{ "paper", "cross" },
		{ "paper", "arrow_left" },
		{ "leather", "arrow_right" },
		{ "small", "arrow_up" },
		{ "round", "arrow_down" },
		{ "hud", "play" },
		{ "tile", "backpack" },
		{ "settings", nil },
		{ "invite", nil },
		{ "plus", nil },
		{ "minus", nil },
		{ "dropdown", nil },
	}
	local istates = { "normal", "hover", "pressed", "disabled", "selected" }
	for i, entry in icons do
		local x = 30 + (i - 1) * 100
		local size = if entry[1] == "tile" then { 86, 86 } elseif entry[1] == "close" then { 60, 58 } else nil
		caption(root, entry[1] .. (if entry[2] then " " .. entry[2] else ""), x, 490, 100)
		for s, state in istates do
			local props = {
				rect = { x, 512 + (s - 1) * 72, size and size[1] or 60, size and size[2] or 58 },
				variant = entry[1],
				icon = entry[2],
			}
			if entry[1] == "tile" then
				props.rect = { x, 512 + (s - 1) * 72, 64, 64 }
			end
			if i == 11 and s == 1 then
				props.badge = { variant = "dot" }
			end
			force(Kit.IconButton.new(root, props), state)
		end
	end
	for s, state in istates do
		caption(root, state, 1630, 530 + (s - 1) * 72, 60)
	end

	heading(root, "Badge / tags", 1290, 320)
	Kit.Badge.new(root, { rect = { 1290, 360, 0, 34 }, variant = "leader" })
	Kit.Badge.new(root, { rect = { 1390, 360, 0, 34 }, variant = "ready" })
	Kit.Badge.new(root, { rect = { 1490, 360, 0, 34 }, variant = "notReady" })
	Kit.Badge.new(root, { rect = { 1290, 404, 34, 31 }, variant = "count", text = "12" })
	Kit.Badge.new(root, { rect = { 1340, 406, 26, 26 }, variant = "number", text = "3" })
	Kit.Badge.new(root, { rect = { 1380, 405, 0, 30 }, variant = "new" })
	Kit.Badge.new(root, { rect = { 1460, 410, 18, 18 }, variant = "dot" })
	Kit.CurrencyPill.new(root, { rect = { 1500, 398, 112, 46 }, currency = "coins", value = 2450 })
	__dump(gui, W, H)
	gui:Destroy()
end

-- Page 3: tabs, slots, key caps, dividers ------------------------------------------------------

do
	local gui, root = page()
	local tstates = { "normal", "hover", "pressed", "selected", "disabled" }
	heading(root, "Tab × normal, hover, pressed, selected, disabled", 30, 14)
	local variants = {
		{ "category", { 232, 54 }, "Tools", "hammer" },
		{ "arrow", { 200, 60 }, "Recipes", nil },
		{ "horizontal", { 170, 58 }, "Vault", "chest" },
		{ "large", { 237, 81 }, "Gameplay", "gear" },
		{ "side", { 80, 80 }, nil, "journal" },
	}
	local x = 30
	for _, entry in variants do
		caption(root, entry[1], x, 50)
		for s, state in tstates do
			force(
				Kit.Tab.new(root, {
					rect = { x, 72 + (s - 1) * 92, entry[2][1], entry[2][2] },
					label = entry[3],
					icon = entry[4],
					variant = entry[1],
				}),
				state
			)
		end
		x += entry[2][1] + 40
	end
	for s, state in tstates do
		caption(root, state, x - 20, 92 + (s - 1) * 92, 80)
	end

	heading(root, "Slot item / hotbar × normal, hover, pressed, selected, disabled, locked, empty", 30, 540)
	local sstates = { "normal", "hover", "pressed", "selected", "disabled", "locked", "empty" }
	for s, state in sstates do
		local sx = 30 + (s - 1) * 110
		caption(root, state, sx, 578, 100)
		local item = if state ~= "empty"
			then { catalogId = "G", icon = "logs", quantity = 32, permanent = s == 1 }
			else nil
		force(Kit.Slot.new(root, { rect = { sx, 600, 92, 99 }, item = item }), state)
		force(
			Kit.Slot.new(root, { rect = { sx, 720, 99, 98 }, variant = "hotbar", hotkey = tostring(s), item = item }),
			state
		)
	end
	caption(root, "count plaque", 830, 578)
	Kit.Slot.new(root, {
		rect = { 830, 600, 92, 99 },
		item = { catalogId = "G", icon = "stones", quantity = 99 },
		countStyle = "plaque",
	})
	caption(root, "hotbar empty 6", 830, 700)
	Kit.Slot.new(root, { rect = { 830, 720, 86, 86 }, variant = "hotbar", hotkey = "6" })

	heading(root, "Divider: rule / ornate / diamond / vertical", 1000, 540)
	Kit.Divider.new(root, { rect = { 1000, 590, 420, 16 }, variant = "rule" })
	Kit.Divider.new(root, { rect = { 1000, 630, 420, 26 }, variant = "ornate" })
	Kit.Divider.new(root, { rect = { 1000, 680, 420, 22 }, variant = "diamond" })
	Kit.Divider.new(root, { rect = { 1460, 580, 18, 200 }, variant = "vertical" })

	heading(root, "KeyCap cap / flat", 1000, 730)
	local keys = { "E", "TAB", "SHIFT", "ESC" }
	local kx = 1000
	for _, key in keys do
		local cap = Kit.KeyCap.new(root, { rect = { kx, 770, 0, 56 }, text = key })
		kx += cap.w + 12
	end
	kx = 1000
	for i, key in { "W", "Space", "Left Shift" } do
		local cap =
			Kit.KeyCap.new(root, { rect = { kx, 850, 0, 30 }, text = key, variant = "flat", onPress = function() end })
		if i == 2 then
			force(cap, "capturing")
		elseif i == 3 then
			force(cap, "hover")
		end
		kx += cap.w + 12
	end
	caption(root, "flat: normal · capturing · hover", kx + 10, 856, 260)
	__dump(gui, W, H)
	gui:Destroy()
end

-- Page 4: bars and controls ----------------------------------------------------------------------

do
	local gui, root = page()
	heading(root, "Bar fills at 0 / 50 / 100 % on the track", 30, 14)
	local fills = { "xp", "health", "stamina", "food", "blue" }
	for r, fill in fills do
		caption(root, fill, 30, 62 + (r - 1) * 44, 80)
		for c, value in { 0, 0.5, 1 } do
			Kit.Bar.new(
				root,
				{ rect = { 110 + (c - 1) * 250, 56 + (r - 1) * 44, 230, 28 }, fill = fill, value = value }
			)
		end
	end
	heading(root, "Frames: none / well / thin / stat", 30, 290)
	Kit.Bar.new(root, { rect = { 30, 335, 300, 22 }, fill = "orange", frame = "none", value = 0.7 })
	Kit.Bar.new(root, { rect = { 360, 325, 303, 55 }, fill = "green", frame = "well", value = 0.6 })
	Kit.Bar.new(root, { rect = { 690, 335, 182, 32 }, fill = "yellow", frame = "thin", value = 0.4 })
	Kit.Bar.new(
		root,
		{ rect = { 30, 400, 315, 65 }, fill = "health", frame = "stat", icon = "heart", text = "85", value = 0.85 }
	)
	Kit.Bar.new(
		root,
		{ rect = { 360, 400, 315, 65 }, fill = "stamina", frame = "stat", icon = "lightning", text = "60", value = 0.6 }
	)
	Kit.Bar.new(
		root,
		{ rect = { 690, 400, 315, 65 }, fill = "food", frame = "stat", icon = "drumstick", text = "30", value = 0.3 }
	)
	Kit.Bar.new(root, { rect = { 30, 485, 500, 18 }, fill = "xp", value = 450 / 750, text = "450/750 XP" })

	heading(root, "Checkbox box / gold / tile, Toggle × normal, hover, pressed, disabled", 30, 530)
	local cstates = { "normal", "hover", "pressed", "disabled" }
	for c, state in cstates do
		local x = 30 + (c - 1) * 250
		caption(root, state, x, 566)
		force(Kit.Checkbox.new(root, { rect = { x, 590, 230, 36 }, label = "Show Names", checked = false }), state)
		force(
			Kit.Checkbox.new(root, {
				rect = { x, 636, 240, 50 },
				label = "Show Damage",
				description = "Numbers over hits",
				checked = true,
				variant = "gold",
			}),
			state
		)
		force(
			Kit.Checkbox.new(
				root,
				{ rect = { x, 696, 160, 36 }, label = "Objective", checked = c % 2 == 0, variant = "tile" }
			),
			state
		)
		force(Kit.Toggle.new(root, { rect = { x, 746, 89, 49 }, on = c % 2 == 1 }), state)
		force(Kit.Toggle.new(root, { rect = { x + 110, 746, 89, 49 }, on = c % 2 == 0 }), state)
	end

	heading(root, "Slider × normal, hover, pressed, disabled", 1050, 14)
	for s, state in cstates do
		local y = 60 + (s - 1) * 60
		caption(root, state, 1050, y)
		force(
			Kit.Slider.new(root, {
				rect = { 1050, y + 18, 375, 34 },
				min = 0,
				max = 2,
				step = 0.1,
				value = 0.4 + s * 0.3,
			}),
			state
		)
	end
	Kit.Slider.new(
		root,
		{ rect = { 1050, 310, 375, 40 }, min = 0, max = 100, step = 1, value = 75, knob = "round", track = "paper" }
	)
	caption(root, "round knob, paper track", 1440, 320, 200)

	heading(root, "Dropdown (open), SearchBox, Stepper", 1050, 380)
	local dropdown = Kit.Dropdown.new(
		root,
		{ rect = { 1050, 420, 236, 43 }, options = { "All", "Tools", "Weapons", "Armor" }, value = "Tools" }
	)
	dropdown:SetOpen(true)
	force(
		Kit.Dropdown.new(root, { rect = { 1310, 420, 236, 43 }, options = { "English" }, value = "English" }),
		"hover"
	)
	Kit.SearchBox.new(root, { rect = { 1310, 480, 260, 41 }, placeholder = "Search players..." })
	force(Kit.SearchBox.new(root, { rect = { 1310, 535, 260, 41 }, text = "Iron" }), "focused")
	force(Kit.SearchBox.new(root, { rect = { 1310, 590, 260, 41 }, placeholder = "Disabled" }), "disabled")
	Kit.Stepper.new(root, { rect = { 1050, 660, 160, 48 }, min = 1, max = 10, value = 1 })
	Kit.Stepper.new(root, { rect = { 1240, 660, 250, 48 }, min = 1, max = 6, value = 4, allLabel = "All" })
	caption(root, "at min: − disabled", 1050, 712)
	__dump(gui, W, H)
	gui:Destroy()
end

-- Page 5: rows, player rows, panels ----------------------------------------------------------------

do
	local gui, root = page()
	heading(root, "ListRow card × states", 30, 14)
	local rstates = { "normal", "hover", "pressed", "selected", "disabled", "locked" }
	for s, state in rstates do
		local y = 52 + (s - 1) * 82
		force(
			Kit.ListRow.new(root, {
				rect = { 30, y, 300, 72 },
				variant = "card",
				icon = "pickaxe",
				title = "Iron Pickaxe",
				subtitle = "Mine stone and ore.",
				chevron = true,
				onPress = function() end,
			}),
			state
		)
		caption(root, state, 340, y + 26, 80)
	end
	heading(root, "row, line, option", 440, 14)
	Kit.ListRow.new(
		root,
		{ rect = { 440, 52, 280, 52 }, icon = "logs", title = "Wood", value = "12", onPress = function() end }
	)
	force(
		Kit.ListRow.new(
			root,
			{ rect = { 440, 112, 280, 52 }, icon = "stones", title = "Iron Ore", value = "6", onPress = function() end }
		),
		"selected"
	)
	Kit.ListRow.new(
		root,
		{ rect = { 440, 172, 280, 52 }, icon = "stone", title = "Iron Ore", value = "6 / 4", valueColor = "short" }
	)
	Kit.ListRow.new(root, { rect = { 440, 236, 280, 36 }, variant = "line", title = "Members", value = "1 / 8" })
	Kit.ListRow.new(
		root,
		{ rect = { 440, 276, 280, 36 }, variant = "line", title = "Join Type", value = "Invite Only" }
	)
	Kit.ListRow.new(
		root,
		{ rect = { 440, 324, 220, 40 }, variant = "option", title = "Tools", onPress = function() end }
	)

	heading(root, "PlayerRow", 760, 14)
	Kit.PlayerRow.new(
		root,
		{ rect = { 760, 52, 360, 56 }, userId = 1, name = "LiamTheMo", level = 12, leader = true, badge = "leader" }
	)
	Kit.PlayerRow.new(
		root,
		{ rect = { 760, 112, 360, 56 }, userId = 2, name = "ForestRanger", level = 15, action = { label = "Invite" } }
	)
	Kit.PlayerRow.new(root, {
		rect = { 760, 172, 360, 56 },
		userId = 3,
		name = "SunnyVale",
		level = 8,
		action = { label = "Invited", variant = "secondary", enabled = false },
	})
	Kit.PlayerRow.new(root, { rect = { 760, 232, 360, 56 }, userId = 1, name = "LiamTheMo", badge = "ready" })
	Kit.PlayerRow.new(root, { rect = { 760, 292, 360, 56 }, userId = 2, name = "ForestRanger", badge = "notReady" })
	Kit.PlayerRow.new(root, { rect = { 760, 352, 360, 52 }, empty = true })
	force(
		Kit.PlayerRow.new(
			root,
			{ rect = { 760, 412, 360, 56 }, userId = 1, name = "Selected row", level = 3, onPress = function() end }
		),
		"selected"
	)

	heading(root, "Portrait square / round", 1160, 14)
	Kit.Portrait.new(root, { rect = { 1160, 52, 101, 103 }, userId = 1 })
	Kit.Portrait.new(root, { rect = { 1280, 52, 82, 83 }, userId = 1, frame = "round" })
	Kit.Portrait.new(root, { rect = { 1380, 52, 56, 56 }, userId = 1 })

	heading(root, "Panel inset / card / plaque, SectionHeader, Scroll", 30, 560)
	local inset = Kit.Panel.new(root, {
		rect = { 30, 600, 360, 320 },
		title = "Your Party",
		icon = "party",
		count = "1/8",
		scroll = true,
		contentHeight = 600,
	})
	for i = 1, 5 do
		Kit.PlayerRow.new(inset:Content(), {
			size = { 300, 52 },
			layoutOrder = i,
			empty = i > 1,
			userId = 1,
			name = "LiamTheMo",
			level = 12,
			leader = i == 1,
		})
	end
	local card = Kit.Panel.new(
		root,
		{ rect = { 420, 600, 360, 320 }, variant = "card", title = "Party Details", icon = "exclamation" }
	)
	Kit.ListRow.new(
		card:Content(),
		{ rect = { 0, 0, 328, 36 }, variant = "line", title = "Party Leader", value = "LiamTheMo" }
	)
	Kit.ListRow.new(
		card:Content(),
		{ rect = { 0, 40, 328, 36 }, variant = "line", title = "Created", value = "Just now" }
	)
	Kit.Panel.new(root, { rect = { 810, 600, 420, 66 }, variant = "plaque", text = "Shattered Crater" })
	Kit.SectionHeader.new(root, { rect = { 810, 700, 400, 34 }, text = "Requires", icon = nil })
	Kit.SectionHeader.new(root, { rect = { 810, 760, 400, 34 }, text = "Invite Players", icon = "magnifier" })
	Kit.Text.new(root, {
		rect = { 810, 820, 500, 56 },
		text = "Ancestral Forge",
		role = "windowTitle",
		smallCaps = true,
		color = "cream",
	})
	Kit.Text.new(root, {
		rect = { 810, 876, 500, 26 },
		text = "Turn raw materials into tools for the island.",
		role = "subtitleHand",
		color = "cream",
	})
	__dump(gui, W, H)
	gui:Destroy()
end

-- Page 6: toast, dialog, tooltip, headers --------------------------------------------------------

do
	local gui, root = page()
	heading(root, "Toast quest / item / info / warn", 30, 14)
	Kit.Toast.new(
		root,
		{ rect = { 30, 50, 430, 84 }, kind = "quest", title = "Quest Complete", text = "Gather Supplies" }
	)
	Kit.Toast.new(root, {
		rect = { 30, 144, 430, 84 },
		kind = "item",
		title = "Items Received",
		text = "3 items from your run",
		actions = { { label = "View" } },
	})
	Kit.Toast.new(
		root,
		{ rect = { 30, 238, 430, 84 }, kind = "info", title = "Party invite", text = "ForestRanger invited you" }
	)
	Kit.Toast.new(root, { rect = { 30, 332, 430, 84 }, kind = "warn", title = "Vault full" })

	heading(root, "ConfirmDialog (normal, busy)", 500, 14)
	Kit.ConfirmDialog.new(root, {
		rect = { 500, 50, 560, 330 },
		title = "Take these into the run?",
		text = "Everything except ★ Permanent items can be lost in the run. Items in your vault always stay safe.",
		confirmLabel = "Enter",
	})
	local busy = Kit.ConfirmDialog.new(
		root,
		{ rect = { 1080, 50, 560, 330 }, title = "Rebirth", text = "Hold to confirm.", holdSeconds = 2 }
	)
	busy:SetBusy(true)

	heading(root, "Tooltip", 30, 440)
	Kit.Tooltip.new(root, { rect = { 30, 480, 0, 0 }, text = "Needs 2 more Iron Ore" })
	Kit.Tooltip.new(
		root,
		{ rect = { 30, 580, 0, 0 }, text = "Locked: reach level 5 to forge this recipe with the ancestral anvil." }
	)

	heading(root, "Window headers: plaque / centred / banner with subtitle", 420, 420)
	Kit.Window.new(root, { rect = { 420, 460, 400, 240 }, title = "Play", header = "plaque", showClose = true })
	Kit.Window.new(root, {
		rect = { 840, 460, 400, 240 },
		title = "Party",
		header = "centered",
		ornaments = { "tree", "tree" },
		showClose = false,
	})
	Kit.Window.new(root, {
		rect = { 1260, 460, 400, 240 },
		title = "Forge",
		smallCaps = true,
		subtitle = "Turn raw materials into tools.",
		icon = "anvil",
		clasps = true,
	})
	__dump(gui, W, H)
	gui:Destroy()
end

-- Page 7: the fix round -----------------------------------------------------------------

do
	local gui, root = page()
	heading(root, "Window header options, plain rules, glyphs", 30, 14)
	Kit.Window.new(root, {
		rect = { 30, 50, 560, 250 },
		title = "Ancestral Forge",
		icon = "anvil_hammer",
		iconRect = { 34, 14, 96, 80 },
		titleX = 150,
		smallCaps = true,
		smallCapsSizes = { 44, 36 },
		subtitle = "Turn raw materials into tools.",
		rule = "full",
		closeRect = { 486, 18, 52, 50 },
	})
	caption(root, "iconRect, titleX, smallCapsSizes, rule = full, closeRect", 30, 304, 560)
	Kit.Window.new(root, {
		rect = { 620, 50, 420, 250 },
		title = "Party",
		header = "centered",
		titleSize = 40,
		titleY = 22,
		ornaments = { "ink:people", "ink:people" },
		ornamentSize = 40,
		showClose = false,
	})
	caption(root, "centered: titleSize, titleY, ornament glyphs", 620, 304, 420)
	Kit.Window.new(root, {
		rect = { 1070, 50, 570, 250 },
		title = "Play",
		header = "plaque",
		plaqueRect = { 40, 22, 240, 80 },
		titleSize = 52,
	})
	caption(root, "plaque: plaqueRect, titleSize", 1070, 304, 400)

	heading(root, "Divider ink / hairline / rule", 30, 340)
	local paper = Kit.Panel.new(root, { rect = { 30, 380, 560, 120 }, variant = "inset" })
	Kit.Divider.new(paper.base.visual, { rect = { 20, 26, 520, 2 }, variant = "ink" })
	Kit.Divider.new(paper.base.visual, { rect = { 20, 56, 520, 2 }, variant = "hairline" })
	Kit.Divider.new(paper.base.visual, { rect = { 20, 78, 520, 16 }, variant = "rule" })

	heading(root, "Flat glyphs: ink / white", 620, 340)
	local glyphs = {
		"gamepad",
		"speaker",
		"monitor",
		"gears",
		"refresh",
		"people",
		"magnifier",
		"info",
		"check",
		"anvil",
		"book",
		"trophy",
		"map_pin",
		"backpack",
		"chest",
		"hammer",
		"compass",
	}
	local strip = Kit.Panel.new(root, { rect = { 620, 380, 1020, 60 }, variant = "inset" })
	local dark = Kit.Panel.new(root, { rect = { 620, 446, 1020, 60 }, variant = "plain" })
	Kit.Button
		.new(dark.base.visual, { rect = { 0, 0, 1020, 60 }, label = "", variant = "flat" }).root
		:SetAttribute("DebugState", "selected")
	for i, id in glyphs do
		Kit.Icon.new(strip.base.visual, { rect = { 10 + (i - 1) * 59, 10, 40, 40 }, icon = "ink:" .. id })
		Kit.Icon.new(dark.base.visual, { rect = { 10 + (i - 1) * 59, 10, 40, 40 }, icon = "white:" .. id, zIndex = 12 })
	end

	heading(root, "Rows", 30, 520)
	local soft = Kit.ListRow.new(root, {
		rect = { 30, 560, 300, 72 },
		variant = "soft",
		icon = "pickaxe",
		title = "Iron Pickaxe",
		subtitle = "Mine stone and ore.",
		subtitleHand = true,
		onPress = function() end,
	})
	local picked = Kit.ListRow.new(root, {
		rect = { 30, 642, 300, 72 },
		variant = "soft",
		icon = "hatchet",
		title = "Iron Hatchet",
		subtitle = "Locked: level 5",
		onPress = function() end,
	})
	picked:SetSelected(true)
	picked:SetState("locked")
	local objective = Kit.ListRow.new(root, {
		rect = { 30, 724, 300, 56 },
		variant = "soft",
		icon = "logs",
		iconSize = 40,
		textX = 70,
		title = "Collect Wood",
		value = "12 / 20",
		trailing = 30,
	})
	Kit.Checkbox.new(objective:Trailing(), { rect = { 0, 13, 30, 30 }, variant = "ring", readOnly = true })
	local done = Kit.ListRow.new(root, {
		rect = { 30, 790, 300, 56 },
		variant = "soft",
		icon = "stones",
		iconSize = 40,
		textX = 70,
		title = "Collect Stone",
		value = "15 / 15",
		trailing = 30,
	})
	Kit.Checkbox.new(done:Trailing(), { rect = { 0, 13, 30, 30 }, variant = "ring", readOnly = true, checked = true })
	local _ = soft

	heading(root, "PlayerRow, thin rail", 360, 520)
	local list = Kit.Panel.new(root, { rect = { 360, 560, 300, 230 }, variant = "card" })
	local scroll = Kit.Scroll.new(
		list.base.visual,
		{ rect = { 14, 14, 272, 200 }, rail = "thin", railOverlay = true, gap = 2, contentHeight = 400 }
	)
	Kit.PlayerRow.new(scroll:Content(), {
		size = { 250, 40 },
		layoutOrder = 1,
		compact = true,
		userId = 1,
		name = "LiamTheMo",
		leader = true,
		status = "ready",
	})
	for i = 2, 6 do
		Kit.PlayerRow.new(
			scroll:Content(),
			{ size = { 250, 36 }, layoutOrder = i, compact = true, empty = true, emptyIndent = 10, nameX = 44 }
		)
	end
	Kit.PlayerRow.new(root, {
		rect = { 690, 560, 360, 56 },
		userId = 2,
		name = "ForestRangerWithALongName",
		level = 15,
		action = { label = "Invite", size = { 108, 45 } },
	})
	Kit.PlayerRow.new(root, { rect = { 690, 620, 360, 52 }, empty = true, emptyIndent = 14, nameX = 74 })

	heading(root, "Stepper leather, play hover, roles, item art", 1080, 520)
	Kit.Stepper.new(root, { rect = { 1080, 560, 160, 48 }, min = 1, max = 10, value = 2, buttons = "leather" })
	force(
		Kit.Button.new(root, {
			rect = { 1260, 556, 260, 62 },
			label = "Forge",
			icon = "white:anvil",
			iconSize = 34,
			iconGap = 14,
			variant = "play",
		}),
		"hover"
	)
	Kit.Picture.new(root, { rect = { 690, 690, 359, 86 }, role = "hud.playerCard" })
	Kit.Picture.new(root, { rect = { 1000, 700, 39, 76 }, role = "hud.leaf" })
	Kit.Picture.new(root, { rect = { 1080, 640, 150, 150 }, role = "map.island" })
	Kit.Picture.new(root, { rect = { 1250, 640, 200, 150 }, role = "panel.party" })
	local items = { "StoneAxe", "StoneSpear", "IronOre", "Clay", "Resin", "Herbs" }
	for i, id in items do
		Kit.Slot.new(root, {
			rect = { 1080 + (i - 1) * 92, 810, 86, 86 },
			variant = "hotbar",
			hotkey = tostring(i),
			item = { itemId = id, quantity = i },
		})
	end
	scroll:ScrollToRow(3)
	__dump(gui, W, H)
	gui:Destroy()
end

-- Page 8: the polish round -----------------------------------------------------------------

do
	local gui, root = page()
	heading(root, "Ring 0 / 30 / 70 / 100 %", 30, 14)
	for i, value in { 0, 0.3, 0.7, 1 } do
		Kit.Ring.new(
			root,
			{ rect = { 30 + (i - 1) * 110, 50, 90, 90 }, value = value, text = ("%d%%"):format(value * 100) }
		)
	end
	heading(root, "TextField, low stat fill, dots", 500, 14)
	Kit.TextField.new(root, { rect = { 500, 50, 260, 41 }, placeholder = "Enter a code", clearButton = false })
	Kit.TextField.new(root, { rect = { 780, 50, 260, 41 }, text = "SUMMER-2026", maxLength = 20 })
	Kit.Bar.new(
		root,
		{ rect = { 500, 110, 315, 65 }, fill = "health", frame = "stat", icon = "heart", text = "8", value = 0.08 }
	)
	Kit.Bar.new(root, { rect = { 840, 125, 300, 28 }, fill = "xp", value = 0.12 })
	for i, variant in { "dotRed", "dotYellow", "dotGreen", "dotGrey" } do
		Kit.Badge.new(root, { rect = { 1180 + (i - 1) * 30, 60, 18, 18 }, variant = variant })
	end
	for i, rarity in { "Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic" } do
		Kit.Badge.new(root, { rect = { 1180 + (i - 1) * 24, 100, 12, 12 }, variant = "rarity", rarity = rarity })
	end
	caption(root, "status dots, rarity accents", 1180, 120, 300)

	heading(root, "Toast with two actions, no close", 30, 200)
	Kit.Toast.new(root, {
		rect = { 30, 240, 520, 84 },
		kind = "info",
		title = "Trade request",
		text = "ForestRanger wants to trade",
		hideClose = true,
		actionWidth = 104,
		actions = { { label = "Accept" }, { label = "Decline", variant = "secondary" } },
	})
	heading(root, "Horizontal scroll", 600, 200)
	local strip = Kit.Panel.new(root, { rect = { 600, 240, 520, 130 }, variant = "inset" })
	local scroll =
		Kit.Scroll.new(strip.base.visual, { rect = { 10, 8, 500, 114 }, direction = "X", gap = 8, contentHeight = 900 })
	for i = 1, 8 do
		Kit.Slot.new(
			scroll:Content(),
			{ size = { 92, 92 }, layoutOrder = i, item = { itemId = "Stone", quantity = i * 5 } }
		)
	end

	heading(root, "Portrait none, PlayerRow badge width and lines, ListRow lines", 30, 400)
	Kit.Portrait.new(root, { rect = { 30, 440, 56, 56 }, userId = 1, frame = "none" })
	Kit.PlayerRow.new(root, {
		rect = { 110, 440, 400, 60 },
		userId = 1,
		name = "LiamTheMo",
		level = 12,
		badge = "ready",
		badgeWidth = 90,
		nameY = 6,
		levelY = 34,
		frame = "none",
	})
	Kit.ListRow.new(root, {
		rect = { 540, 436, 330, 72 },
		variant = "soft",
		icon = "pickaxe",
		title = "Iron Pickaxe",
		titleY = 6,
		subtitle = "Mine stone and ore.",
		subtitleY = 40,
		onPress = function() end,
	})
	local selected = Kit.ListRow.new(root, {
		rect = { 900, 436, 330, 72 },
		variant = "soft",
		icon = "hatchet",
		title = "Selected card",
		subtitle = "Thin glow on the edge",
		onPress = function() end,
	})
	selected:SetSelected(true)
	local tabs = Kit.Tab.new(root, { rect = { 1260, 430, 82, 84 }, variant = "side", icon = "ink:book" })
	tabs:SetSelected(true)
	Kit.Stepper.new(root, { rect = { 1360, 440, 200, 48 }, buttons = "leather", gap = 16, buttonSize = 42 })
	Kit.Text.new(root, { rect = { 30, 540, 300, 30 }, text = "LV. 12   450/750 XP", role = "hudSmall", outline = true })
	caption(root, "HUD text with its outline", 30, 572, 300)
	Kit.Button.new(
		root,
		{ rect = { 400, 540, 260, 62 }, label = "Play", icon = "play", variant = "play", contentOffset = { 0, -3 } }
	)
	__dump(gui, W, H)
	gui:Destroy()
end
