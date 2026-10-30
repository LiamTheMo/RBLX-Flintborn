local Shared = game:GetService("ReplicatedStorage").Shared
local KitModel = require(Shared.UI.KitModel)

-- State machine ------------------------------------------------------------------

test("live flags resolve to the strongest state", function()
	expectEq(KitModel.ResolveState({ enabled = true }), "normal", "nothing set")
	expectEq(KitModel.ResolveState({ hover = true }), "hover", "hover")
	expectEq(KitModel.ResolveState({ hover = true, pressed = true }), "pressed", "a press beats hover")
	expectEq(
		KitModel.ResolveState({ selected = true, hover = true }),
		"selected",
		"a selected tab stays selected under the pointer"
	)
	expectEq(
		KitModel.ResolveState({ selected = true, pressed = true }),
		"selected",
		"selection beats a press (the press scales)"
	)
	expectEq(
		KitModel.ResolveState({ enabled = false, hover = true, pressed = true }),
		"disabled",
		"disabled beats input"
	)
	expectEq(KitModel.ResolveState({ busy = true, hover = true }), "busy", "busy beats hover")
	expectEq(KitModel.ResolveState({ locked = true, selected = true }), "locked", "locked beats selected")
	expectEq(KitModel.ResolveState({ focused = true }), "focused", "gamepad focus")
	expectEq(KitModel.ResolveState({ capturing = true, hover = true }), "capturing", "a key cap waiting for a key")
	expectEq(KitModel.ResolveState({ empty = true }), "empty", "an empty slot")
	expectEq(KitModel.ResolveState({ empty = true, hover = true }), "hover", "hover over an empty slot")
	expectEq(KitModel.ResolveState({ open = true, hover = true }), "open", "an open dropdown")
end)

test("DebugState forces any valid state and ignores the rest", function()
	expectEq(KitModel.ResolveState({ enabled = false }, "hover"), "hover", "forced over disabled")
	expectEq(KitModel.ResolveState({ hover = true }, "pressed"), "pressed", "forced press")
	expectEq(KitModel.ResolveState({ hover = true }, ""), "hover", "empty string returns to live input")
	expectEq(KitModel.ResolveState({ hover = true }, nil), "hover", "nil returns to live input")
	expectEq(KitModel.ResolveState({ hover = true }, "sparkly"), "hover", "an unknown state is ignored")
	for _, state in KitModel.STATES do
		expectEq(KitModel.ResolveState({}, state), state, "forces " .. state)
	end
end)

test("states borrow art and tint where a role has none of its own", function()
	local sprite, borrowed = KitModel.ArtFor("button.primary", "hover")
	expectEq(sprite, "lk_button_leather_hover", "own hover art")
	expectEq(borrowed, false, "own art is not tinted")
	sprite, borrowed = KitModel.ArtFor("button.flat", "hover")
	expectEq(sprite, "lk_button_flat_paper", "no hover art: the normal plate")
	expectEq(borrowed, true, "tinted")
	sprite, borrowed = KitModel.ArtFor("button.play", "hover")
	expectEq(sprite, "lk_plaque_notched_leather", "the play plate has no hover art")
	expectEq(borrowed, false, "it lifts instead of darkening")
	sprite = KitModel.ArtFor("button.primary", "focused")
	expectEq(sprite, "lk_button_leather_hover", "gamepad focus draws hover")
	sprite = KitModel.ArtFor("slot.hotbar", "locked")
	expectEq(sprite, "lk_slot_locked", "own locked art")
	sprite, borrowed = KitModel.ArtFor("row.plate", "busy")
	expectEq(sprite, "lk_row_disabled", "busy borrows the disabled art")
	expectEq(borrowed, false, "borrowed state art is drawn as is")
	sprite = KitModel.ArtFor("tab.category", "normal")
	expectEq(sprite, nil, "a category tab has no plate until selected")
	expectEq(KitModel.ArtFor("tab.category", "selected"), "lk_tab_category", "selected plate")
	sprite, borrowed = KitModel.ArtFor("iconButton.close", "selected")
	expectEq(sprite, "lk_button_close_normal", "selected without art")
	expectEq(borrowed, false, "selected is never darkened")
	expectEq(KitModel.ArtFor("no.such.role", "normal"), nil, "unknown role")
	expectEq(KitModel.STATE_TINT.pressed, "pressed", "press tint")
end)

-- Modal stack --------------------------------------------------------------------

test("one window at a time; dialogs stack above it", function()
	local stack = KitModel.ModalStack()
	local inventory, party, dialog = { name = "inventory" }, { name = "party" }, { name = "dialog" }
	expectEq(#stack:Open(inventory, "window"), 0, "first window closes nothing")
	expectEq(stack:Top(), inventory, "inventory on top")
	expectEq(#stack:Open(dialog, "dialog"), 0, "a dialog closes nothing")
	expectEq(stack:Top(), dialog, "Escape closes the dialog first")
	expectEq(stack:Count(), 2, "two layers")
	local closing = stack:Open(party, "window")
	expectEq(#closing, 2, "a new window closes the old window and its dialog")
	expectEq(closing[1], dialog, "top first")
	expectEq(closing[2], inventory, "then the window")
	expectEq(stack:Top(), party, "party on top")
	expectEq(stack:Count(), 1, "only the new window")
	expectEq(stack:IsOpen(inventory), false, "inventory closed")
end)

test("a dialog opened before its window still sits above it", function()
	local stack = KitModel.ModalStack()
	local window, dialog = {}, {}
	stack:Open(dialog, "dialog")
	-- Opening a window closes dialogs too (they belonged to the old window).
	local closing = stack:Open(window, "window")
	expectEq(#closing, 1, "the stray dialog is closed")
	stack:Open(dialog, "dialog")
	expectEq(stack:Top(), dialog, "dialog above")
	expectEq(stack:Close(dialog), true, "closes")
	expectEq(stack:Close(dialog), false, "closing twice is a no-op")
	expectEq(stack:Top(), window, "window back on top")
	expectEq(#stack:Open(window, "window"), 0, "re-opening the open window closes nothing")
	expectEq(stack:Count(), 1, "still one entry")
end)

-- Maid -----------------------------------------------------------------------------

test("the maid undoes everything once, newest first", function()
	local maid = KitModel.Maid()
	local log = {}
	local connection = {
		Connected = true,
		Disconnect = function(self)
			self.Connected = false
			table.insert(log, "disconnect")
		end,
	}
	local instance = {
		Destroy = function()
			table.insert(log, "destroy")
		end,
	}
	maid:Give(instance)
	maid:Give(connection)
	maid:Give(function()
		table.insert(log, "fn")
	end)
	expectEq(maid:Count(), 3, "three items")
	maid:Clean()
	expectEq(table.concat(log, ","), "fn,disconnect,destroy", "newest first")
	expectEq(connection.Connected, false, "disconnected")
	expectEq(maid:Count(), 0, "emptied")
	maid:Clean()
	expectEq(#log, 3, "a second clean does nothing")
	expectEq(maid:Give(instance), instance, "Give returns its item")
end)

-- Layout sums --------------------------------------------------------------------------

test("slider and stepper values snap and clamp", function()
	expectEq(KitModel.Snap(0.73, 0, 2, 0.1), 0.7, "snaps to a tenth")
	expectEq(KitModel.Snap(57.4, 10, 100, 1), 57, "whole steps")
	expectEq(KitModel.Snap(140, 10, 100, 1), 100, "clamped high")
	expectEq(KitModel.Snap(-3, 1, 10, 1), 1, "clamped low")
	expectEq(KitModel.Snap(12, 10, 100, 5), 10, "steps count from min")
	expectEq(KitModel.Snap(0.333333, 0, 1), 0.333, "no step: three decimals")
	expectEq(KitModel.Fraction(55, 10, 100), 0.5, "fraction")
	expectEq(KitModel.Fraction(5, 5, 5), 0, "empty range")
end)

test("bar fills hide below their end caps and show the real fraction", function()
	local width, visible = KitModel.FillWidth(0.5, 200, 24)
	expectEq(width, 100, "half")
	expectEq(visible, true, "shown")
	width, visible = KitModel.FillWidth(0.05, 200, 24)
	expectEq(width, 10, "a sliver")
	expectEq(visible, false, "hidden below the caps")
	_, visible = KitModel.FillWidth(0, 200, 0)
	expectEq(visible, false, "empty is hidden")
	width = KitModel.FillWidth(0 / 0, 200, 24)
	expectEq(width, 0, "NaN reads empty")
	width = KitModel.FillWidth(3, 200, 24)
	expectEq(width, 200, "clamped full")
end)

test("scroll thumbs follow the canvas", function()
	local thumb = KitModel.Thumb(300, 300, 0, 300, 28)
	expectEq(thumb.visible, false, "nothing to scroll")
	thumb = KitModel.Thumb(300, 600, 0, 300, 28)
	expectEq(thumb.height, 150, "half the content shows")
	expectEq(thumb.y, 0, "at the top")
	thumb = KitModel.Thumb(300, 600, 300, 300, 28)
	expectEq(thumb.y, 150, "at the bottom")
	thumb = KitModel.Thumb(300, 30000, 0, 300, 28)
	expectEq(thumb.height, 28, "never shorter than the minimum")
end)

test("windows draw at mockup size on desktop and fill phones", function()
	expectEq(KitModel.WindowScale(1672, 941, 58, 1187, 652), 1, "design size: 1:1")
	expectNear(KitModel.WindowScale(1672, 941, 58, 1187, 652, 1.2), 1.2, 1e-9, "the player's UI scale")
	local phone = KitModel.WindowScale(844, 390, 0, 1187, 652, 1, true)
	expectNear(phone, (390 - 16) / 652, 1e-9, "a short touch screen fills the room")
	local small = KitModel.WindowScale(1280, 720, 58, 1187, 652)
	expectNear(small, 720 / 941, 1e-9, "canvas fit on a smaller desktop")
	expectEq(KitModel.WindowScale(300, 200, 0, 1187, 652, 1, true), 0.3, "clamped to the minimum")
	expectEq(KitModel.WindowScale(0, 0, 0, 1, 1), 1, "unmeasured screen")
end)

test("key caps, small caps and the toast column", function()
	expectEq(KitModel.KeyCapWidth(10, 56), 56, "single keys stay square")
	expectEq(KitModel.KeyCapWidth(60, 56), 88, "words widen by the padding")
	expectEq(
		KitModel.SmallCaps("Ancestral Forge", 46, 40),
		'<font size="46">A</font><font size="40">NCESTRAL</font> <font size="46">F</font><font size="40">ORGE</font>',
		"initials big, the rest small"
	)
	expectEq(KitModel.SmallCaps("I", 46, 40), '<font size="46">I</font>', "a one-letter word")
	local column = {}
	expectEq(#KitModel.PushToast(column, "a", 3), 0, "room for one")
	KitModel.PushToast(column, "b", 3)
	KitModel.PushToast(column, "c", 3)
	local out = KitModel.PushToast(column, "d", 3)
	expectEq(out[1], "a", "the oldest goes first")
	expectEq(#column, 3, "at most three")
end)
