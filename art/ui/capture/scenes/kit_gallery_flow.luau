-- Kit behaviour, driven through real events (the env's signals are fireable):
-- the state machine (hover only for a mouse, press cancelled by leaving,
-- release-outside, disabled ignores input, DebugState), tab groups, the
-- one-window rule with Escape / B, toasts and a dialog over a window, and a
-- leak check (build and destroy every component 20 times; instance and
-- connection counts must come back). Fails loudly on any broken rule, then
-- dumps the window with its dialog and toasts.

local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local Kit = require(Hud.Kit)

local W, H = 1672, 941
local failures = 0
local function check(ok, message)
	if not ok then
		failures += 1
		print("FAIL " .. message)
	end
end

local function input(kind)
	return { UserInputType = Enum.UserInputType[kind], KeyCode = Enum.KeyCode.Unknown, Position = Vector3.new(0, 0, 0) }
end

local gui, root = __screen(W, H)

-- Buttons: hover, press, release-outside cancel, activation, disabled, debug.
do
	local presses = 0
	local button = Kit.Button.new(root, {
		rect = { 10, 10, 220, 58 },
		label = "Equip",
		onPress = function()
			presses += 1
		end,
	})
	local hit = button.control.hit
	local state = function()
		return button.root:GetAttribute("KitState")
	end
	check(state() == "normal", "starts normal")
	hit.MouseEnter:Fire()
	check(state() == "hover", "mouse hover")
	local mouse = input("MouseButton1")
	hit.InputBegan:Fire(mouse)
	check(state() == "pressed", "pressed")
	hit.MouseLeave:Fire()
	check(state() == "normal", "leaving cancels the press")
	hit.MouseEnter:Fire()
	hit.InputBegan:Fire(mouse)
	UserInputService.InputEnded:Fire(mouse)
	check(state() == "hover", "a release anywhere ends the press")
	hit.Activated:Fire()
	check(presses == 1, "Activated runs onPress")
	hit.Activated:Fire()
	check(presses == 1, "debounced")
	button:SetEnabled(false)
	check(state() == "disabled", "disabled")
	check(hit.Interactable == false and hit.Selectable == false, "disabled is not interactable or selectable")
	button.control:Activate()
	check(presses == 1, "disabled ignores activation")
	button.root:SetAttribute("DebugState", "pressed")
	check(state() == "pressed", "DebugState forces a state")
	button.root:SetAttribute("DebugState", "")
	check(state() == "disabled", "an empty DebugState returns to live")
	button:SetEnabled(true)
	button:SetBusy(true)
	check(state() == "busy" and button.label.Text == "…", "busy shows …")
	button.control:Activate()
	check(presses == 1, "busy ignores activation")
	button:SetBusy(false)
	button:SetVariant("secondary")
	button:SetLabel("Invited")
	button:SetEnabled(false)
	check(button.root:GetAttribute("KitRole") == "button.secondary", "variant switch (Invited)")
	-- Gamepad selection draws hover; touch never hovers.
	hit.SelectionGained:Fire()
	button:SetEnabled(true)
	check(state() == "focused", "gamepad selection")
	hit.SelectionLost:Fire()
	button:Destroy()
	check(button.root.Parent == nil, "destroyed")
end

-- Slots and locked state.
do
	local slot = Kit.Slot.new(root, { rect = { 10, 100, 92, 99 } })
	check(slot.root:GetAttribute("KitState") == "empty", "an empty slot")
	slot:SetItem({ catalogId = "Stone", icon = "stone", quantity = 4 })
	check(slot.root:GetAttribute("KitState") == "normal", "filled")
	check(slot.count.Text == "4", "count shown")
	slot:SetState("locked")
	local locked = 0
	slot.control.opts.onLocked = function()
		locked += 1
	end
	slot.control:Activate()
	check(slot.root:GetAttribute("KitState") == "locked" and locked == 1, "locked presses explain, not act")
	check(slot.control.hit.Selectable == true, "locked stays selectable")
	slot:Destroy()
end

-- Tabs: one selected; a press selects and reports.
do
	local picked = nil
	local tabs = {
		Kit.Tab.new(root, { id = "a", rect = { 10, 220, 170, 58 }, label = "Backpack" }),
		Kit.Tab.new(root, { id = "b", rect = { 190, 220, 170, 58 }, label = "Vault" }),
	}
	local group = Kit.TabGroup.new(tabs, function(id)
		picked = id
	end)
	group:Select("a")
	check(picked == nil, "scripted selection does not report")
	tabs[2].control:Activate()
	check(picked == "b", "a press reports")
	check(
		tabs[2].root:GetAttribute("KitState") == "selected" and tabs[1].root:GetAttribute("KitState") == "normal",
		"one selected"
	)
	group:Destroy()
end

-- Controls report their values.
do
	local toggled, value, chosen = nil, nil, nil
	local box = Kit.Checkbox.new(root, {
		rect = { 10, 300, 200, 36 },
		label = "x",
		onToggle = function(v)
			toggled = v
		end,
	})
	box.control:Activate()
	check(toggled == true and box.root:GetAttribute("KitChecked") == true, "checkbox toggles")
	local stepper = Kit.Stepper.new(root, {
		rect = { 10, 350, 160, 48 },
		min = 1,
		max = 3,
		value = 3,
		onChange = function(v)
			value = v
		end,
	})
	check(stepper.plus.root:GetAttribute("KitState") == "disabled", "+ disabled at max")
	stepper.minus.control:Activate()
	check(value == 2 and stepper.plus.root:GetAttribute("KitState") == "normal", "− steps and frees +")
	local dropdown = Kit.Dropdown.new(root, {
		rect = { 10, 420, 236, 43 },
		options = { "A", "B" },
		value = "A",
		onSelect = function(v)
			chosen = v
		end,
	})
	dropdown.control:Activate()
	check(dropdown:IsOpen() and dropdown.root:GetAttribute("KitState") == "open", "dropdown opens")
	dropdown.rows.B.control:Activate()
	check(chosen == "B" and not dropdown:IsOpen(), "picking closes and reports")
	local slider = Kit.Slider.new(root, { rect = { 10, 480, 375, 34 }, min = 0, max = 10, step = 1, value = 3 })
	slider:SetValue(7.6)
	check(slider.value == 8 and slider.valueLabel.Text == "8", "slider snaps and shows")
	for _, item in { box, stepper, dropdown, slider } do
		item:Destroy()
	end
end

-- One window at a time; Escape / B closes the top layer.
do
	local first = Kit.Screen.new("KitFlowA", { size = { 600, 400 } })
	local second = Kit.Screen.new("KitFlowB", { size = { 600, 400 } })
	first:Open()
	check(Kit.Modal.Top() == first, "first open")
	second:Open()
	check(not first:IsOpen() and second:IsOpen(), "opening a window closes the other")
	check(Kit.Modal.Count() == 1, "one window on the stack")
	Kit.Modal.Back()
	check(not second:IsOpen() and Kit.Modal.Count() == 0, "Escape / B closes it")
	check(second.gui.Enabled == false, "a closed screen disables its gui")
	first:Destroy()
	second:Destroy()
end

-- Leak check: build and destroy each component 20 times.
local function handlerCount()
	local total = 0
	for _, signal in { UserInputService.InputEnded, UserInputService.InputChanged } do
		total += #signal.handlers
	end
	return total
end
do
	local function buildAll(parent)
		return {
			Kit.Button.new(parent, { rect = { 0, 0, 200, 58 }, label = "A", icon = "play" }),
			Kit.IconButton.new(
				parent,
				{ rect = { 0, 0, 60, 58 }, variant = "tile", icon = "backpack", badge = { variant = "dot" } }
			),
			Kit.Tab.new(parent, { rect = { 0, 0, 170, 58 }, label = "T", icon = "chest" }),
			Kit.Slot.new(
				parent,
				{
					rect = { 0, 0, 92, 99 },
					hotkey = "1",
					item = { catalogId = "X", quantity = 3 },
					countStyle = "plaque",
				}
			),
			Kit.Bar.new(parent, { rect = { 0, 0, 300, 65 }, frame = "stat", icon = "heart", text = "5", value = 0.5 }),
			Kit.Checkbox.new(parent, { rect = { 0, 0, 200, 40 }, label = "C" }),
			Kit.Toggle.new(parent, { rect = { 0, 0, 89, 49 } }),
			Kit.Slider.new(parent, { rect = { 0, 0, 375, 34 }, min = 0, max = 1 }),
			Kit.Dropdown.new(parent, { rect = { 0, 0, 236, 43 }, options = { "A", "B" } }),
			Kit.SearchBox.new(parent, { rect = { 0, 0, 215, 41 } }),
			Kit.Stepper.new(parent, { rect = { 0, 0, 250, 48 }, allLabel = "All" }),
			Kit.KeyCap.new(parent, { rect = { 0, 0, 0, 30 }, text = "E", onPress = function() end }),
			Kit.Divider.new(parent, { rect = { 0, 0, 200, 16 } }),
			Kit.ListRow.new(
				parent,
				{ rect = { 0, 0, 300, 72 }, variant = "card", title = "R", chevron = true, onPress = function() end }
			),
			Kit.PlayerRow.new(
				parent,
				{
					rect = { 0, 0, 330, 52 },
					userId = 1,
					name = "P",
					level = 2,
					badge = "ready",
					action = { label = "Invite" },
					onPress = function() end,
				}
			),
			Kit.Badge.new(parent, { rect = { 0, 0, 0, 30 }, variant = "leader" }),
			Kit.CurrencyPill.new(parent, { rect = { 0, 0, 112, 46 }, value = 5, onPress = function() end }),
			Kit.Portrait.new(parent, { rect = { 0, 0, 60, 60 }, userId = 1 }),
			Kit.Icon.new(parent, { rect = { 0, 0, 40, 40 }, icon = "coin" }),
			Kit.ItemIcon.new(parent, { rect = { 0, 0, 40, 40 }, catalogId = "X" }),
			Kit.Text.new(parent, { rect = { 0, 0, 100, 20 }, text = "t" }),
			Kit.Scroll.new(parent, { rect = { 0, 0, 300, 300 } }),
			Kit.Panel.new(parent, { rect = { 0, 0, 300, 300 }, title = "P", scroll = true }),
			Kit.SectionHeader.new(parent, { rect = { 0, 0, 300, 34 }, text = "H" }),
			Kit.Toast.new(parent, { rect = { 0, 0, 430, 84 }, title = "T", actions = { { label = "Go" } } }),
			Kit.ConfirmDialog.new(parent, { rect = { 0, 0, 560, 330 }, title = "D", holdSeconds = 1 }),
			Kit.Tooltip.new(parent, { rect = { 0, 0, 0, 0 }, text = "tip" }),
			Kit.Window.new(parent, { rect = { 0, 0, 600, 400 }, title = "W", icon = "anvil", clasps = true }),
		}
	end
	local holder = Instance.new("Frame")
	holder.Parent = root
	local beforeKids = #holder:GetDescendants()
	local beforeHandlers = handlerCount()
	for _ = 1, 20 do
		for _, component in buildAll(holder) do
			component:Destroy()
		end
	end
	check(
		#holder:GetDescendants() == beforeKids,
		("no instances left after 20 builds (%d)"):format(#holder:GetDescendants())
	)
	check(
		handlerCount() == beforeHandlers,
		("no input connections left (%d -> %d)"):format(beforeHandlers, handlerCount())
	)
	-- Screens and their guis.
	local guis = #Players.LocalPlayer.PlayerGui:GetChildren()
	for _ = 1, 20 do
		local screen = Kit.Screen.new("KitLeak", { size = { 400, 300 } })
		Kit.Window.new(screen, { title = "Leak" })
		screen:Open()
		screen:Destroy()
	end
	check(#Players.LocalPlayer.PlayerGui:GetChildren() == guis, "screens leave no guis")
	check(Kit.Modal.Count() == 0, "modal stack empty")
	holder:Destroy()
end

assert(failures == 0, failures .. " kit flow checks failed")
print("kit flow: all checks passed")
gui:Destroy()

-- The page: a window with a dialog over it and the toast column.
local screen = Kit.Screen.new("FlintbornForge", { size = { 1102, 679 } })
local window = Kit.Window.new(screen, {
	title = "Ancestral Forge",
	smallCaps = true,
	subtitle = "Turn raw materials into tools for the island.",
	icon = "anvil_hammer",
	clasps = true,
	claspYs = { 0.24, 0.9 },
})
Kit.Panel.new(window:Body(), { rect = { 0, 10, 330, 520 }, title = "Recipes" })
screen:Open()
screen:Fit(W, H, 58, 1)
Kit.Toast.Show({ kind = "quest", title = "Quest Complete", text = "Gather Supplies" })
Kit.Toast.Show({ kind = "item", title = "Item Received", text = "Iron Pickaxe" })
Kit.ConfirmDialog.Show({
	title = "Forge Iron Pickaxe?",
	text = "Uses 4 Iron Ore and 3 Wood from your vault.",
	confirmLabel = "Forge",
})
check(Kit.Modal.Count() == 2, "the dialog stacks above the window")
assert(failures == 0, "dialog stacking failed")
__dump(Players.LocalPlayer.PlayerGui, W, H, { background = "art/reference/ui/lobby/01_hud.png" })
