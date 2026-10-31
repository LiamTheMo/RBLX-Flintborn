-- Pure rules for the UI kit (src/client/Hud/Kit, docs/ui/KIT.md): the role table
-- that maps what a sprite is for to its lk_* art, the interaction state machine,
-- the one-window modal stack, a cleanup maid and the small layout sums the
-- components share. No Instances here, so the headless specs and the kit share
-- one definition.

local KitModel = {}

-- Role -> art. `sprite` is the normal art and `states` the art of other states
-- (lk_* names from art/ui/kit/CATALOG.md). `material` picks the drawn stand-in
-- while the art is not uploaded (paper, leather, slot, window, track, fill,
-- glyph, rule, none); `fill` is the stand-in colour of a bar fill and `glyph` the
-- text of a glyph stand-in; `grow` draws a state's sprite that many px larger
-- per side (glow rings sit outside the plate). `native` roles are drawn as
-- flat kit shapes by design (the mockups' plain discs and rails), never as a
-- sprite; `edge = false` keeps a sprite at its rect instead of placing its
-- visible edge there (see EDGES). Screens never name sprites: they name roles.
KitModel.ROLES = {
	-- Windows, dialogs and panels
	["window.frame"] = { sprite = "lk_window_frame", material = "window" },
	["window.claspLeft"] = { sprite = "lk_clasp_left", material = "leather" },
	["window.claspRight"] = { sprite = "lk_clasp_right", material = "leather" },
	["window.rule"] = { sprite = "lk_divider_line", material = "rule" },
	["window.plaque"] = { sprite = "lk_plaque_paper", material = "paper" },
	["dialog.frame"] = { sprite = "lk_dialog_frame", material = "window" },
	["toast.frame"] = { sprite = "lk_toast_frame", material = "paper" },
	["tooltip.box"] = { sprite = "lk_tooltip", material = "paper" },
	["tooltip.tail"] = { sprite = "lk_tooltip_tail", material = "none", edge = false },
	["panel.inset"] = { sprite = "lk_panel_inset", material = "paper" },
	["panel.card"] = { sprite = "lk_panel", material = "paper" },
	["panel.plaque"] = { sprite = "lk_plaque_small", material = "paper" },
	-- The HUD's party panel (M01): the window frame's parchment and corners.
	["panel.party"] = { sprite = "lk_window_frame", material = "window" },
	["hud.playerCard"] = { sprite = "lk_player_card", material = "paper" },
	["hud.leaf"] = { sprite = "lk_emblem_leaf", material = "glyph", glyph = "❦", edge = false },
	-- The painted island (Play window, Journal map page, world map).
	["map.island"] = { sprite = "pm_map_island", material = "paper", edge = false },

	-- Buttons
	["button.primary"] = {
		sprite = "lk_button_leather_normal",
		material = "leather",
		states = {
			hover = "lk_button_leather_hover",
			pressed = "lk_button_leather_pressed",
			disabled = "lk_button_leather_disabled",
		},
	},
	["button.secondary"] = {
		sprite = "lk_button_paper_normal",
		material = "paper",
		states = {
			hover = "lk_button_paper_hover",
			pressed = "lk_button_paper_pressed",
			disabled = "lk_button_paper_disabled",
		},
	},
	["button.play"] = {
		sprite = "lk_plaque_notched_leather",
		material = "leather",
		states = { disabled = "lk_plaque_notched_disabled" },
		-- No hover art: the plate lifts (scale) instead of darkening.
		untinted = { hover = true, focused = true },
	},
	["button.playSecondary"] = {
		sprite = "lk_plaque_notched_paper",
		material = "paper",
		states = { disabled = "lk_plaque_notched_disabled" },
	},
	["button.flat"] = {
		sprite = "lk_button_flat_paper",
		material = "paper",
		states = { selected = "lk_button_flat_leather", disabled = "lk_button_flat_disabled" },
	},
	["button.small"] = {
		sprite = "lk_button_paper_small_normal",
		material = "paper",
		states = { hover = "lk_button_paper_small_hover", disabled = "lk_button_paper_small_disabled" },
	},

	-- Icon buttons
	["iconButton.close"] = {
		sprite = "lk_button_close_normal",
		material = "leather",
		glyph = "✕",
		states = {
			hover = "lk_button_close_hover",
			pressed = "lk_button_close_pressed",
			disabled = "lk_button_close_disabled",
		},
	},
	["iconButton.paper"] = {
		sprite = "lk_button_square_paper",
		material = "paper",
		states = { selected = "lk_button_paper_small_hover" },
	},
	["iconButton.leather"] = { sprite = "lk_button_square_leather", material = "leather" },
	["iconButton.small"] = {
		sprite = "lk_button_square_small",
		material = "paper",
		states = { selected = "lk_button_paper_small_hover" },
	},
	["iconButton.round"] = { sprite = "lk_frame_round", material = "paper" },
	["iconButton.hud"] = {
		sprite = "lk_button_hud",
		material = "paper",
		states = { selected = "lk_button_paper_small_hover" },
	},
	["iconButton.tile"] = {
		sprite = "lk_tile_frame",
		material = "paper",
		states = { selected = "lk_slot_selected" },
		grow = { lk_slot_selected = 3 },
	},
	["iconButton.settings"] = { sprite = "lk_button_settings", material = "paper", glyph = "⚙" },
	["iconButton.invite"] = { sprite = "lk_button_invite", material = "paper", glyph = "+" },
	["iconButton.plus"] = { sprite = "lk_button_stepper_plus", material = "paper", glyph = "+" },
	["iconButton.minus"] = { sprite = "lk_button_stepper_minus", material = "paper", glyph = "−" },
	["iconButton.dropdown"] = { sprite = "lk_dropdown_button", material = "paper", glyph = "▼" },

	-- Tabs
	["tab.category"] = { material = "none", states = { selected = "lk_tab_category" } },
	["tab.arrow"] = {
		sprite = "lk_tab_arrow_paper",
		material = "paper",
		states = { selected = "lk_tab_arrow_leather" },
	},
	["tab.horizontal"] = {
		sprite = "lk_button_paper_normal",
		material = "paper",
		states = {
			hover = "lk_button_paper_hover",
			pressed = "lk_button_paper_pressed",
			disabled = "lk_button_paper_disabled",
			selected = "lk_button_leather_normal",
		},
	},
	["tab.side"] = {
		sprite = "lk_tile_frame",
		material = "paper",
		states = { selected = "lk_slot_item_selected", disabled = "lk_slot_disabled" },
		-- The selected glow shares the tile's edge and draws thinner (M07).
		thin = { lk_slot_item_selected = 0.6 },
	},

	-- Slots and tiles
	["slot.item"] = {
		sprite = "lk_slot_item_normal",
		material = "slot",
		states = {
			selected = "lk_slot_item_selected",
			disabled = "lk_slot_disabled",
			locked = "lk_slot_locked",
		},
		grow = { lk_slot_item_selected = 3 },
	},
	["slot.hotbar"] = {
		sprite = "lk_slot_normal",
		material = "slot",
		states = {
			hover = "lk_slot_hover",
			selected = "lk_slot_selected",
			disabled = "lk_slot_disabled",
			locked = "lk_slot_locked",
		},
		grow = { lk_slot_selected = 3 },
	},
	["slot.tile"] = { sprite = "lk_tile_blank", material = "slot" },

	-- Badges, tags and dots
	["badge.number"] = { sprite = "lk_badge_number", material = "leather" },
	["badge.count"] = { sprite = "lk_badge_count", material = "paper" },
	["badge.countWide"] = { sprite = "lk_badge_count_wide", material = "paper" },
	["badge.pill"] = { sprite = "lk_pill_value", material = "paper" },
	["dot.green"] = { sprite = "lk_dot_green", material = "dot", fill = "readyDot" },
	["dot.grey"] = { sprite = "lk_dot_brown", material = "dot", fill = "muted" },
	["dot.red"] = { sprite = "lk_dot_red", material = "dot", fill = "health" },
	["dot.yellow"] = { sprite = "lk_dot_yellow", material = "dot", fill = "gold" },
	-- A rarity accent: a small flat dot coloured from the rarity tokens.
	["dot.rarity"] = { native = true, material = "dot", fill = "rarityCommon" },

	-- Bars
	["bar.track"] = { sprite = "lk_bar_track", material = "track" },
	["bar.fill.yellow"] = { sprite = "lk_bar_fill_yellow", material = "fill", fill = "xp" },
	["bar.fill.red"] = { sprite = "lk_bar_fill_red", material = "fill", fill = "health" },
	["bar.fill.green"] = { sprite = "lk_bar_fill_green", material = "fill", fill = "stamina" },
	["bar.fill.orange"] = { sprite = "lk_bar_fill_orange", material = "fill", fill = "food" },
	["bar.fill.blue"] = { sprite = "lk_bar_fill_blue", material = "fill", fill = "blue" },
	["bar.frame"] = { sprite = "lk_bar_frame", material = "paper" },
	["bar.frameThin"] = { sprite = "lk_bar_frame_thin", material = "paper" },
	["bar.stat"] = { sprite = "lk_statbar_frame", material = "paper" },

	-- Controls
	["checkbox.off"] = { sprite = "lk_checkbox_off", material = "paper" },
	["checkbox.on"] = { sprite = "lk_checkbox_on", material = "paper", glyph = "✓" },
	["check.tileOff"] = { sprite = "lk_tile_check_off", material = "paper" },
	["check.tileOn"] = { sprite = "lk_tile_check_on", material = "paper", glyph = "✓" },
	-- The quest objective's round check (M07): the empty ring, and the ring
	-- filled when done (a check mark is laid over it).
	["check.ringOff"] = { sprite = "lk_ring_track", material = "none" },
	["check.ringOn"] = { sprite = "lk_ring_full", material = "fill", fill = "gold" },
	-- The progress ring (sheet 19): its empty track and the full fill revealed
	-- clockwise by Kit.Ring.
	["ring.track"] = { sprite = "lk_ring_track", material = "none" },
	["ring.fill"] = { sprite = "lk_ring_full", material = "fill", fill = "xp", edge = false },
	["toggle.off"] = { sprite = "lk_toggle_off", material = "paper" },
	["toggle.on"] = { sprite = "lk_toggle_on", material = "fill", fill = "toggleOn" },
	["slider.track"] = { sprite = "lk_bar_track", material = "track" },
	["slider.trackPaper"] = { sprite = "lk_slider_track", material = "paper" },
	["slider.fill"] = { sprite = "lk_bar_fill_yellow", material = "fill", fill = "xp" },
	["slider.knob"] = { sprite = "lk_button_paper_small_normal", material = "paper" },
	["slider.knobRound"] = { sprite = "lk_slider_knob", material = "dot", fill = "gold" },
	["field.value"] = { sprite = "lk_button_paper_small_normal", material = "paper" },
	["dropdown.field"] = { sprite = "lk_dropdown", material = "paper" },
	["dropdown.list"] = { sprite = "lk_tooltip", material = "paper" },
	["search.field"] = { sprite = "lk_search", material = "paper" },
	["keycap.cap"] = { sprite = "lk_keycap", material = "paper" },
	["keycap.wide"] = { sprite = "lk_keycap_wide", material = "paper" },
	["keycap.flat"] = {
		sprite = "lk_button_paper_small_normal",
		material = "paper",
		states = { hover = "lk_button_paper_small_hover", disabled = "lk_button_paper_small_disabled" },
	},
	["scroll.track"] = { sprite = "lk_scroll_track", material = "track", edge = false },
	["scroll.thumb"] = { sprite = "lk_scroll_thumb", material = "leather", edge = false },
	-- The thin flat rail of the HUD party list and long lists (about 8 px).
	["scroll.thinTrack"] = { native = true, material = "fill", fill = "railTrack" },
	["scroll.thinThumb"] = { native = true, material = "fill", fill = "railThumb" },

	-- Dividers
	["divider.rule"] = { sprite = "lk_divider_line", material = "rule" },
	["divider.ornate"] = { sprite = "lk_divider_ornament", material = "rule" },
	["divider.diamond"] = { sprite = "lk_divider_diamond", material = "rule" },
	["divider.vertical"] = { sprite = "lk_divider_vertical", material = "rule" },
	-- Plain rules: most mockup rules are a thin ink line or a faint hairline.
	["divider.ink"] = { native = true, material = "rule", fill = "ruleDark" },
	["divider.hairline"] = { native = true, material = "rule", fill = "hairline" },

	-- Rows
	["row.plate"] = {
		sprite = "lk_row_normal",
		material = "paper",
		states = { selected = "lk_row_hover", disabled = "lk_row_disabled", locked = "lk_row_disabled" },
		grow = { lk_row_hover = 2 },
	},
	-- The mockups' soft cards (M06 recipes and materials, M07 quests): the thin
	-- inset border, gold glow when selected.
	["row.soft"] = {
		sprite = "lk_panel_inset",
		material = "paper",
		states = { selected = "lk_row_hover", disabled = "lk_row_disabled", locked = "lk_row_disabled" },
		-- The selected glow sits on the card's own edge, thinner (M06, M07).
		thin = { lk_row_hover = 0.55 },
	},
	["row.bullet"] = { sprite = "lk_row_bullet", material = "paper" },

	-- Currency, portraits
	["currency.pill"] = { sprite = "lk_currency_pill", material = "paper" },
	["portrait.square"] = { sprite = "lk_portrait_frame", material = "none" },
	["portrait.round"] = { sprite = "lk_frame_hollow_circle", material = "none" },
	-- The empty party slot (M01, M04): a flat tan disc.
	["portrait.empty"] = { native = true, material = "dot", fill = "emptyDot" },

	-- Marks drawn on top of other parts
	["mark.lock"] = { sprite = "lk_icon_lock", material = "glyph", glyph = "🔒" },
	["mark.crown"] = { sprite = "lk_icon_crown", material = "glyph", glyph = "♛" },
	["mark.star"] = { sprite = "lk_icon_star", material = "glyph", glyph = "★" },
	["mark.chevron"] = { sprite = "lk_glyph_chevron_right", material = "glyph", glyph = "›" },
	["mark.cross"] = { sprite = "lk_glyph_cross", material = "glyph", glyph = "✕" },
	["mark.check"] = { sprite = "lk_glyph_checkmark", material = "glyph", glyph = "✓" },
	["mark.play"] = { sprite = "lk_glyph_play", material = "glyph", glyph = "▶" },
	["mark.confirm"] = { sprite = "lk_glyph_check_white", material = "glyph", glyph = "✓" },
}

-- Every state a component can draw, from strongest to weakest: when several
-- hold at once (a selected tab under the mouse), the first one wins.
KitModel.STATES = {
	"disabled",
	"busy",
	"locked",
	"capturing",
	"selected",
	"pressed",
	"open",
	"focused",
	"hover",
	"empty",
	"normal",
}

-- A state with no art of its own draws the art of these states, in order.
KitModel.ART_FALLBACK = {
	capturing = { "hover" },
	open = { "hover" },
	locked = { "disabled" },
	busy = { "disabled" },
}

-- Image tint (a tints token key) for a state drawn with borrowed art.
KitModel.STATE_TINT = {
	hover = "hover",
	capturing = "hover",
	open = "hover",
	pressed = "pressed",
	disabled = "disabled",
	locked = "locked",
	busy = "disabled",
}

local VALID_STATE = {}
for _, state in KitModel.STATES do
	VALID_STATE[state] = true
end

function KitModel.IsState(state: any): boolean
	return type(state) == "string" and VALID_STATE[state] == true
end

-- The state to draw from live flags {enabled, busy, locked, capturing, selected,
-- pressed, open, focused, hover, empty}; a valid `debugState` (the DebugState
-- attribute) wins over all of them.
function KitModel.ResolveState(flags, debugState: string?): string
	if KitModel.IsState(debugState) then
		return debugState :: string
	end
	if flags.enabled == false then
		return "disabled"
	end
	for _, state in KitModel.STATES do
		if state ~= "disabled" and state ~= "normal" and flags[state] then
			return state
		end
	end
	return "normal"
end

-- The sprite to draw for `role` in `state`, and whether it is borrowed (so the
-- state's tint applies). nil when the role has no art in that state (a category
-- tab draws nothing until it is selected).
function KitModel.ArtFor(roleName: string, state: string): (string?, boolean)
	local role = KitModel.ROLES[roleName]
	if role == nil then
		return nil, false
	end
	local states = role.states or {}
	if states[state] then
		return states[state], false
	end
	for _, other in KitModel.ART_FALLBACK[state] or {} do
		if states[other] then
			return states[other], false
		end
	end
	local untinted = role.untinted and role.untinted[state]
	return role.sprite, not untinted and state ~= "normal" and state ~= "selected" and state ~= "empty"
end

-- The transparent margin [left, top, right, bottom] round each lk_ plate's
-- visible edge, in the sprite's own px (middle row and column, alpha > 128).
-- Plates are drawn outset by it (times their scale), so the art's visible edge
-- lands exactly on the component's rect. Regenerate with
-- `python3 art/ui/capture/capture.py --edges`. lk_panel_inset is set by hand:
-- its parchment is opaque to the image edge and its visible edge is the thin
-- border line inside it.
KitModel.EDGES = {
	lk_badge_count = { 2, 2, 2, 2 },
	lk_badge_count_wide = { 2, 3, 2, 2 },
	lk_badge_number = { 2, 2, 2, 2 },
	lk_banner_leather = { 2, 3, 2, 4 },
	lk_banner_paper = { 5, 5, 5, 7 },
	lk_bar_fill_blue = { 2, 2, 2, 2 },
	lk_bar_fill_green = { 2, 2, 2, 2 },
	lk_bar_fill_orange = { 2, 2, 2, 2 },
	lk_bar_fill_red = { 2, 3, 2, 2 },
	lk_bar_fill_yellow = { 2, 2, 2, 2 },
	lk_bar_frame = { 3, 5, 3, 4 },
	lk_bar_frame_plain = { 3, 5, 3, 4 },
	lk_bar_frame_thin = { 2, 2, 2, 2 },
	lk_bar_track = { 2, 2, 2, 3 },
	lk_button_close_disabled = { 3, 2, 2, 2 },
	lk_button_close_hover = { 2, 2, 2, 3 },
	lk_button_close_normal = { 2, 2, 2, 2 },
	lk_button_close_pressed = { 3, 2, 2, 2 },
	lk_button_flat_disabled = { 3, 2, 2, 3 },
	lk_button_flat_leather = { 3, 2, 2, 2 },
	lk_button_flat_paper = { 2, 2, 3, 3 },
	lk_button_hud = { 2, 2, 2, 2 },
	lk_button_invite = { 2, 2, 2, 2 },
	lk_button_invite_card = { 4, 5, 4, 4 },
	lk_button_leather_disabled = { 3, 2, 3, 2 },
	lk_button_leather_hover = { 2, 3, 2, 3 },
	lk_button_leather_normal = { 3, 3, 2, 3 },
	lk_button_leather_pressed = { 3, 2, 2, 3 },
	lk_button_paper_disabled = { 2, 2, 3, 2 },
	lk_button_paper_hover = { 2, 2, 2, 2 },
	lk_button_paper_normal = { 2, 2, 2, 2 },
	lk_button_paper_pressed = { 2, 3, 2, 3 },
	lk_button_paper_small_disabled = { 2, 2, 2, 2 },
	lk_button_paper_small_hover = { 3, 2, 2, 2 },
	lk_button_paper_small_normal = { 2, 2, 2, 2 },
	lk_button_play_square = { 2, 2, 2, 2 },
	lk_button_settings = { 2, 2, 3, 2 },
	lk_button_square_leather = { 2, 2, 2, 3 },
	lk_button_square_paper = { 2, 2, 2, 2 },
	lk_button_square_small = { 3, 3, 3, 2 },
	lk_button_stepper_minus = { 2, 2, 2, 2 },
	lk_button_stepper_plus = { 2, 2, 2, 2 },
	lk_card_detail = { 3, 3, 2, 2 },
	lk_checkbox_off = { 2, 2, 2, 2 },
	lk_checkbox_on = { 2, 2, 2, 2 },
	lk_clasp_left = { 2, 3, 2, 3 },
	lk_clasp_right = { 2, 4, 2, 4 },
	lk_corner_bl = { 2, 15, 12, 2 },
	lk_corner_br = { 10, 13, 2, 2 },
	lk_corner_fold = { 19, 4, 2, 23 },
	lk_corner_ornate_bl = { 2, 21, 23, 2 },
	lk_corner_ornate_br = { 23, 21, 3, 2 },
	lk_corner_ornate_tl = { 2, 3, 24, 22 },
	lk_corner_ornate_tr = { 24, 2, 3, 22 },
	lk_corner_tl = { 2, 2, 13, 14 },
	lk_corner_tr = { 13, 2, 2, 12 },
	lk_currency_pill = { 3, 3, 2, 2 },
	lk_dialog_frame = { 5, 9, 7, 6 },
	lk_divider_diamond = { 2, 9, 2, 8 },
	lk_divider_line = { 2, 7, 2, 6 },
	lk_divider_ornament = { 3, 0, 233, 0 },
	lk_divider_vertical = { 8, 2, 8, 3 },
	lk_dropdown = { 3, 3, 3, 3 },
	lk_dropdown_button = { 2, 2, 2, 2 },
	lk_emblem_leaf = { 6, 3, 6, 3 },
	lk_emblem_rune = { 18, 2, 18, 2 },
	lk_frame_capped_hollow = { 2, 4, 2, 3 },
	lk_frame_hollow = { 4, 3, 4, 3 },
	lk_frame_hollow_bar = { 3, 3, 3, 3 },
	lk_frame_hollow_capped = { 3, 3, 3, 3 },
	lk_frame_hollow_circle = { 3, 3, 3, 3 },
	lk_frame_hollow_large = { 3, 3, 4, 2 },
	lk_frame_hollow_small = { 2, 3, 3, 3 },
	lk_frame_hollow_speech = { 3, 3, 3, 12 },
	lk_frame_hollow_wide = { 3, 3, 3, 3 },
	lk_frame_rails = { 3, 3, 3, 3 },
	lk_frame_ring = { 2, 2, 3, 2 },
	lk_frame_ring_leaves = { 7, 3, 6, 2 },
	lk_frame_round = { 2, 2, 2, 2 },
	lk_frame_round_paper = { 2, 2, 2, 2 },
	lk_keycap = { 3, 2, 2, 2 },
	lk_keycap_wide = { 2, 3, 2, 2 },
	lk_map_parchment = { 7, 5, 7, 6 },
	lk_medallion_octagon = { 4, 2, 4, 2 },
	lk_medallion_round = { 3, 2, 4, 2 },
	lk_medallion_square = { 4, 4, 4, 4 },
	lk_nail = { 7, 2, 7, 2 },
	lk_panel = { 4, 3, 3, 3 },
	lk_panel_inset = { 6, 6, 5, 5 },
	lk_pill_value = { 2, 3, 2, 3 },
	lk_plaque_capped = { 3, 4, 2, 3 },
	lk_plaque_leather = { 2, 2, 3, 3 },
	lk_plaque_leather_bar = { 3, 3, 2, 3 },
	lk_plaque_notched_disabled = { 2, 2, 2, 3 },
	lk_plaque_notched_leather = { 2, 2, 2, 2 },
	lk_plaque_notched_paper = { 2, 2, 2, 3 },
	lk_plaque_paper = { 4, 3, 4, 3 },
	lk_plaque_paper_bar = { 2, 3, 2, 3 },
	lk_plaque_rivet_leather = { 2, 3, 2, 2 },
	lk_plaque_rivet_paper = { 2, 3, 2, 3 },
	lk_plaque_small = { 3, 3, 2, 3 },
	lk_player_card = { 3, 8, 5, 10 },
	lk_portrait_frame = { 4, 4, 4, 3 },
	lk_portrait_plaque = { 3, 7, 3, 7 },
	lk_rail_h = { 3, 3, 2, 3 },
	lk_rail_v = { 3, 2, 3, 3 },
	lk_ring_full = { 2, 2, 2, 2 },
	lk_ring_half = { 2, 2, 2, 2 },
	lk_ring_track = { 2, 2, 2, 2 },
	lk_rivet = { 2, 2, 2, 2 },
	lk_rope_cross = { 10, 2, 3, 3 },
	lk_rope_knot = { 9, 8, 2, 13 },
	lk_rope_ring = { 2, 3, 2, 2 },
	lk_row_bullet = { 2, 2, 2, 3 },
	lk_row_check_off = { 2, 2, 2, 3 },
	lk_row_check_on = { 2, 2, 2, 3 },
	lk_row_disabled = { 2, 2, 2, 2 },
	lk_row_hover = { 3, 3, 3, 3 },
	lk_row_normal = { 2, 3, 3, 3 },
	lk_scroll_thumb = { 2, 2, 2, 2 },
	lk_scroll_track = { 2, 2, 2, 2 },
	lk_search = { 3, 3, 2, 3 },
	lk_slider_knob = { 2, 2, 2, 2 },
	lk_slider_track = { 2, 2, 2, 2 },
	lk_slot_disabled = { 2, 3, 2, 2 },
	lk_slot_hotbar = { 2, 3, 3, 2 },
	lk_slot_hover = { 2, 4, 2, 2 },
	lk_slot_item_normal = { 2, 2, 3, 3 },
	lk_slot_item_selected = { 2, 2, 2, 2 },
	lk_slot_locked = { 2, 3, 2, 2 },
	lk_slot_normal = { 2, 3, 2, 2 },
	lk_slot_selected = { 2, 2, 2, 2 },
	lk_spike = { 4, 2, 4, 2 },
	lk_statbar_frame = { 3, 8, 3, 6 },
	lk_stepper_box = { 3, 3, 2, 2 },
	lk_strap_leather = { 3, 5, 3, 4 },
	lk_strap_leather_short = { 3, 4, 3, 4 },
	lk_tab_arrow_leather = { 3, 2, 2, 2 },
	lk_tab_arrow_paper = { 3, 3, 2, 3 },
	lk_tab_category = { 3, 4, 3, 5 },
	lk_tile_blank = { 2, 2, 2, 3 },
	lk_tile_check_off = { 2, 3, 2, 3 },
	lk_tile_check_on = { 2, 3, 2, 3 },
	lk_tile_frame = { 3, 3, 3, 3 },
	lk_tile_header = { 3, 2, 3, 3 },
	lk_tile_paper = { 3, 3, 3, 3 },
	lk_tile_rail = { 4, 3, 3, 3 },
	lk_tile_small = { 3, 3, 2, 2 },
	lk_tile_tab = { 3, 2, 3, 3 },
	lk_toast_frame = { 4, 6, 3, 5 },
	lk_toggle_off = { 2, 2, 2, 2 },
	lk_toggle_on = { 2, 2, 2, 2 },
	lk_tooltip = { 3, 3, 3, 3 },
	lk_tooltip_tail = { 8, 2, 8, 2 },
	lk_window_clasp_frame = { 4, 5, 5, 4 },
	lk_window_frame = { 5, 5, 5, 5 },
}

-- The margin of `sprite` (zeros when unknown).
function KitModel.Edge(sprite: string?): { number }
	return sprite and KitModel.EDGES[sprite] or { 0, 0, 0, 0 }
end

-- Every sprite name the role table uses, sorted (native roles have none).
function KitModel.Sprites(): { string }
	local seen, list = {}, {}
	local function add(name)
		if type(name) == "string" and not seen[name] then
			seen[name] = true
			table.insert(list, name)
		end
	end
	for _, role in KitModel.ROLES do
		add(role.sprite)
		for _, name in role.states or {} do
			add(name)
		end
	end
	table.sort(list)
	return list
end

-- Modal stack ---------------------------------------------------------------------

-- Layers from bottom to top. Only one entry of the "window" layer is open at a
-- time; dialogs stack above it.
KitModel.LAYERS = { window = 1, dialog = 2 }

local Stack = {}
Stack.__index = Stack

function KitModel.ModalStack()
	return setmetatable({ entries = {} }, Stack)
end

-- Opens `entry` on `layer`. Returns the entries to close first, top first:
-- opening a window closes the other window and every dialog over it.
function Stack:Open(entry, layer: string): { any }
	local level = KitModel.LAYERS[layer] or 1
	local closing = {}
	for i = #self.entries, 1, -1 do
		local item = self.entries[i]
		if item.entry == entry then
			table.remove(self.entries, i)
		elseif level == 1 then
			table.insert(closing, item.entry)
			table.remove(self.entries, i)
		end
	end
	table.insert(self.entries, { entry = entry, level = level })
	table.sort(self.entries, function(a, b)
		return a.level < b.level
	end)
	return closing
end

-- Removes `entry`; true when it was open.
function Stack:Close(entry): boolean
	for i, item in self.entries do
		if item.entry == entry then
			table.remove(self.entries, i)
			return true
		end
	end
	return false
end

-- The entry Escape / ButtonB closes, or nil.
function Stack:Top(): any
	local top = self.entries[#self.entries]
	return top and top.entry
end

function Stack:Count(): number
	return #self.entries
end

function Stack:IsOpen(entry): boolean
	for _, item in self.entries do
		if item.entry == entry then
			return true
		end
	end
	return false
end

-- Maid ------------------------------------------------------------------------------

-- Collects what a component must undo when it is destroyed: connections
-- (Disconnect), instances and objects (Destroy), threads (task.cancel through
-- `cancel`) and functions (called). Clean runs them newest first, once.
local Maid = {}
Maid.__index = Maid

function KitModel.Maid()
	return setmetatable({ items = {} }, Maid)
end

function Maid:Give<T>(item: T): T
	table.insert(self.items, item)
	return item
end

function Maid:Count(): number
	return #self.items
end

function Maid:Clean(cancel: ((thread) -> ())?)
	local items = self.items
	self.items = {}
	for i = #items, 1, -1 do
		local item: any = items[i]
		local kind = type(item)
		if kind == "function" then
			item()
		elseif kind == "thread" then
			if cancel then
				pcall(cancel, item)
			end
		elseif typeof(item) == "RBXScriptConnection" or (kind == "table" and item.Disconnect) then
			item:Disconnect()
		elseif item ~= nil and (item :: any).Destroy then
			item:Destroy()
		end
	end
end

-- Layout sums -------------------------------------------------------------------------

-- `value` clamped to [min, max] and snapped to `step` from `min`.
function KitModel.Snap(value: number, min: number, max: number, step: number?): number
	local v = math.clamp(value, min, max)
	if step and step > 0 then
		v = min + math.round((v - min) / step) * step
		v = math.clamp(v, min, max)
	end
	return math.round(v * 1000) / 1000
end

function KitModel.Fraction(value: number, min: number, max: number): number
	if max <= min then
		return 0
	end
	return math.clamp((value - min) / (max - min), 0, 1)
end

-- A bar fill's width for `fraction` of `maxWidth`; a sliced fill narrower than its
-- two end caps (`minWidth`) would fold over itself, so it is hidden instead.
function KitModel.FillWidth(fraction: number, maxWidth: number, minWidth: number): (number, boolean)
	local f = if type(fraction) == "number" and fraction == fraction then math.clamp(fraction, 0, 1) else 0
	local width = maxWidth * f
	return width, width >= minWidth and f > 0
end

-- A scrollbar thumb: {height, y, visible} on a track of `trackHeight` for a
-- window `windowSize` tall over a canvas `canvasSize` tall scrolled to `position`.
function KitModel.Thumb(windowSize: number, canvasSize: number, position: number, trackHeight: number, minThumb: number)
	if canvasSize <= windowSize + 0.5 or windowSize <= 0 then
		return { height = trackHeight, y = 0, visible = false }
	end
	local height = math.max(minThumb, trackHeight * windowSize / canvasSize)
	local travel = math.max(0, canvasSize - windowSize)
	local fraction = math.clamp(position / travel, 0, 1)
	return { height = height, y = (trackHeight - height) * fraction, visible = true }
end

-- The window scale (ARCHITECTURE §1.1): on desktop and tablet the smaller of
-- the room fit and the canvas fit times the player's UI scale, so at the design
-- size a window draws exactly as in the mockup; on a short touch screen the
-- room fit, which fills the screen. Clamped to [minScale, maxScale].
function KitModel.WindowScale(
	screenW: number,
	screenH: number,
	topInset: number,
	w: number,
	h: number,
	userScale: number?,
	touchSmall: boolean?,
	opts
): number
	opts = opts or {}
	local margin = opts.margin or 8
	local refW, refH = opts.refW or 1672, opts.refH or 941
	if screenW <= 0 or screenH <= 0 or w <= 0 or h <= 0 then
		return 1
	end
	local fitRoom = math.min((screenW - margin * 2) / w, (screenH - topInset - margin * 2) / h)
	local scale
	if touchSmall then
		scale = fitRoom
	else
		local canvasFit = math.min(screenW / refW, screenH / refH)
		scale = math.min(fitRoom, canvasFit * (userScale or 1))
	end
	return math.clamp(scale, opts.minScale or 0.3, opts.maxScale or 1.4)
end

-- A key cap's width for a label `textWidth` px wide: at least square.
function KitModel.KeyCapWidth(textWidth: number, height: number, pad: number?): number
	return math.max(height, math.ceil(textWidth + (pad or 14) * 2))
end

-- RichText fake small caps: the first letter of each word at `big` px, the
-- rest upper-cased at `small` px ("Ancestral Forge" in M06).
function KitModel.SmallCaps(text: string, big: number, small: number): string
	local out = {}
	for word in string.gmatch(text, "%S+") do
		local first, rest = string.sub(word, 1, 1), string.sub(word, 2)
		local piece = ('<font size="%d">%s</font>'):format(big, string.upper(first))
		if rest ~= "" then
			piece ..= ('<font size="%d">%s</font>'):format(small, string.upper(rest))
		end
		table.insert(out, piece)
	end
	return table.concat(out, " ")
end

-- Pushes `item` on a toast column holding at most `max`; returns the items
-- pushed out, oldest first.
function KitModel.PushToast(list: { any }, item, max: number): { any }
	table.insert(list, item)
	local removed = {}
	while #list > max do
		table.insert(removed, table.remove(list, 1))
	end
	return removed
end

return KitModel
