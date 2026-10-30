# The UI kit (`src/client/Hud/Kit`)

Every screen is built from these components and nothing else (ARCHITECTURE §12
D15). Screens never name sprites, colours or fonts: they pick components, roles
and tokens. This document is the API reference; `docs/ui/ARCHITECTURE.md` §2 is
the contract behind it.

```lua
local Kit = require(script.Parent.Kit) -- from a module in src/client/Hud
local screen = Kit.Screen.new("FlintbornInventory", { size = { 1187, 652 } })
local window = Kit.Window.new(screen, { title = "Inventory", icon = "backpack", clasps = "right" })
Kit.Button.new(window:Body(), { rect = { 860, 450, 270, 61 }, label = "Equip", onPress = equip })
screen:Watch()
screen:Open()
```

Galleries: `art/ui/captures/kit_gallery.png` and `kit_gallery_2.png` … `_6.png`
(every component in every state), `kit_gallery_*_fallback.png` (the stand-ins
drawn before upload) and `kit_gallery_flow.png` (a window with a dialog and the
toast column). Rebuild them with:

```bash
python3 art/ui/capture/capture.py kit_gallery
python3 art/ui/capture/capture.py kit_gallery --uploaded-only --suffix _fallback
python3 art/ui/capture/capture.py kit_gallery_flow   # behaviour checks + leak check
```

## 1. Files

| File | What it holds |
|---|---|
| `src/shared/UI/KitTokens.json` | Colours, fonts, text roles, spacing, scale, motion, display orders, blur, sound ids |
| `src/shared/UI/KitModel.luau` | Pure rules: the **role table** (`ROLES`), the state machine (`ResolveState`, `ArtFor`), the modal stack, the maid, layout sums. Tested by `tests/luau/kit_*.spec.luau` |
| `Kit/init.luau` | Re-exports everything below |
| `Kit/Tokens.luau` | `Color(key)`, `Tint(key)`, `Font(key)`, `TextStyle(role)`, `Space(key)`, `Scale(key)`, `Motion(key)` (TweenInfo), `Order(key)`, `Veil()`, `Sound(key)` |
| `Kit/Art.luau` | Roles to art: `Plate`, `Sprite`, `Icon`, `IconSprite`, `ItemSprite`, `SizeOf`, `SliceScale`, `Missing`, stand-ins |
| `Kit/Core.luau` | `Make`, `Size`, `Place`, `Root`, `Label`, `SetText`, `Style`, `TextWidth`, `Signal`, `Maid` |
| `Kit/Interact.luau` | The shared state machine (`attach`) |
| `Kit/Motion.luau` | `Play(inst, key, goal, onDone?)`, `Set`, `Stop`, `Pulse`, `Reduced()` |
| `Kit/Sound.luau` | `Play(key)` (silent while the token id is empty, D14) |
| `Kit/Scale.luau` | `TopInset(gui)`, `WindowTop(gui)`, `Hud(gui, root, opts)`, `WindowFit(...)`, `Window(screen)`, `IsSmallTouch(h)` |
| `Kit/Modal.luau` | One window at a time, dialogs above, Escape / B, selection save and restore, blur |
| `Kit/Debug.luau` | `Each(root, fn)`, `Force(root, state)`, `Find(root, role)` |
| Components | `Screen Window Panel SectionHeader Button IconButton Tab (TabGroup) Slot Bar Checkbox Toggle Slider Dropdown SearchBox Stepper KeyCap Divider ListRow PlayerRow Badge CurrencyPill Portrait Icon ItemIcon Text Scroll Toast ConfirmDialog Tooltip` |

## 2. Conventions

- **Constructor** `Kit.X.new(parent, props)`; the object has `.root` (its
  GuiObject) and `:Destroy()`, which disconnects everything it connected and
  destroys its instances (a maid). Kit components built inside another one are
  destroyed with it.
- **Placement**: `rect = {x, y, w, h}` in the parent's design px, **or**
  `size = {w, h}` with `layoutOrder` inside a layout. Optional `position`
  (UDim2) and `anchorPoint` (Vector2) for edge-pinned parts, `zIndex`
  (default 4), `name`, `visible`.
- **Design px**: everything is built at the 1672 × 941 mockup size; one UIScale
  per surface maps it to the screen (`Kit.Scale`). Never read `AbsoluteSize` to
  lay out: build from design numbers.
- **Callbacks** are props (`onPress`, `onChange`, `onSelect`, `onToggle`);
  setters are methods (`:SetLabel`, `:SetValue`, `:SetEnabled`, `:SetSelected`,
  `:SetState`, `:SetBusy`).
- **Attributes on every root**: `KitComponent` ("Button"), `KitRole`
  ("button.primary"; for parts without art a descriptive name such as
  `row.line`, `text.body`, `icon.coin`), `KitState` (the state drawn now),
  `DebugState` (input, see §3). Some add `KitValue`, `KitChecked`, `KitVariant`,
  `KitFrame`.
- **Text** is always a live label (no words baked in art). Roles in capitals
  (`caps`) upper-case through `Core.SetText` / `:SetText`.
- **Structure**: `root` (placement, transparent) → `Visual` (centred, carries a
  `Motion` UIScale for hover/press) → art and text; the `Hit` TextButton sits
  over the root (padded towards 44 px for touch).

## 3. States and how to force them

| State | Live trigger | Drawn as |
|---|---|---|
| `normal` | — | normal art |
| `hover` | MouseEnter while the mouse is the input (`Interact.UsingMouse`) | hover art, else normal art tinted `tints.hover` (0.93); tiles, slots, icon buttons and pills scale to 1.03 |
| `focused` | gamepad `SelectionGained` | as hover (the selection image is an empty frame) |
| `pressed` | `InputBegan` (MouseButton1, Touch, ButtonA) until its `InputEnded`; leaving the button or releasing anywhere else cancels | pressed art, else tint 0.80; scale 0.96, Back-out release |
| `selected` | `:SetSelected(true)` | selected art (gold glow on slots, rows, side tabs; leather on tabs) |
| `disabled` | `:SetEnabled(false)` | disabled art, else tint 0.72; `Interactable = false`, `Selectable = false` |
| `locked` | `:SetState("locked")` / `control:SetLocked(true)` | locked art (slots) or disabled art plus a lock; stays selectable; a press calls `onLocked` (tooltip) instead of `onPress` |
| `busy` | `:SetBusy(true)` | disabled art, label "…", not interactive |
| `capturing` | `KeyCap:SetCapturing(true)` | hover art, pulsing label |
| `open` | an open Dropdown | hover art |
| `empty` | an empty Slot or PlayerRow | normal art, no item |

Priority when several hold (`KitModel.STATES`): disabled > busy > locked >
capturing > selected > pressed > open > focused > hover > empty > normal.

**Forcing a state** (scenes and verifiers): set the `DebugState` attribute on a
component root to any state name; `""` or `nil` returns it to live input.

```lua
button.root:SetAttribute("DebugState", "pressed")
Kit.Debug.Force(slot.root, "locked")
Kit.Debug.Each(window.root, function(root) print(root:GetAttribute("KitRole"), root:GetAttribute("KitState")) end)
```

Flows can also fire real events (the capture env's signals are fireable):
`button.control.hit.MouseEnter:Fire()`, `hit.InputBegan:Fire(input)`,
`button.control:Activate()` (runs the press action, skipping the debounce).

## 4. Tokens (`KitTokens.json`)

- `colors`: the palette of ARCHITECTURE §3.2, plus `veil` `#050403`,
  `white`/`black`, and tints laid over art: `leaderTint` (Leader tag gold),
  `checkTint` (M03 gold checkbox), `notReadyTint`.
- `veil`: colour key and `BackgroundTransparency` **0.30** (D8, as updated).
- `tints`: grey multipliers for borrowed state art (hover 0.93, pressed 0.80,
  disabled / locked 0.72).
- `fonts`: `display` Merriweather Heavy (Roblox falls back to Bold), `heading`
  Merriweather Bold, `body` Merriweather Regular, `hand` Patrick Hand, `symbol`
  Builder Sans Bold (stand-in glyphs only). `legacy` names the `Enum.Font` used to
  measure text; `weightWidth` corrects for weight.
- `text`: type roles → font, size (design px), colour, caps:

| Role | Font | Size | Colour | Role | Font | Size | Colour |
|---|---|---|---|---|---|---|---|
| windowTitle (caps) | display | 42 | ink | rowTitle | heading | 19 | inkLabel |
| detailTitle | display | 38 | ink | rowLabel | body | 16 | inkLabel |
| subtitleHand | hand | 20 | inkHand | body / bodySoft | body | 15 | inkBody / inkSoft |
| itemTitle | heading | 27 | ink | small | body | 13 | inkSoft |
| buttonL (caps) | heading | 36 | cream | muted | body | 15 | muted |
| button (caps) | heading | 24 | cream | value | heading | 17 | ink |
| buttonS | heading | 18 | cream | count | heading | 19 | inkLabel |
| tab / tabLarge | heading | 18 / 22 | inkLabel | hudName / hudSmall | heading | 20 / 15 | ink |
| sectionHeader (caps) | heading | 20 | inkHeader | currency | heading | 19 | ink |
| keycap | heading | 16 | ink | badgeNum / tag | heading | 14 | cream / ink |
| placeholder | body | 15 | placeholder | label | body | 14 | cream |

  Sizes are a little under the specs' cap-height sizes because Merriweather is
  wider than the mockup face (the specs' "width-matched" sizes). A screen that
  must hit a spec number passes `textSize` / `size` to the component.
- `space`: windowPad 24, colGap 14, sectionHeaderH 34, row heights (52, 64, 72,
  36), slot 90 / pitch 99, hotbar 86 / 97, tile 86, touchMin 44, window header
  100, close button 60 inset 22, toast 430 × 84, tooltip max 300 …
- `scale`: HUD 0.34–1.6, windows 0.3–1.4, phone height 500 (× 0.9 for the HUD),
  hover 1.03, pressed 0.96, window pop from 0.94.
- `motion`: hover 0.12 Quad Out, press 0.07, release 0.18 Back Out, windowOpen
  0.22 Quint Out, windowClose 0.15 Quad In, toastIn 0.25 / toastOut 0.2, bar
  0.25, count 0.4, knob 0.12, pulse 0.6, reducedFade 0.1.
- `order`: hud 1, topStack 5, window 20, dialog 30, toasts 40, tooltip 45.

**Reduced motion** (`Theme.ReducedMotion()` or `GuiService.ReducedMotionEnabled`):
`Kit.Motion` lands moves and scales at once and caps fades at 0.1 s.

## 5. Roles (`KitModel.ROLES`)

The one place a role names its art. States without their own sprite borrow
(`KitModel.ART_FALLBACK`: focused / capturing / open → hover, locked / busy →
disabled) or draw the normal sprite tinted. `grow` draws a state's sprite larger
per side (glow rings outside the plate: slot and side-tab selected +3 px, row
selected +2 px, tile selected +3 px). `material` picks the stand-in.

| Role | Sprite | States | Stand-in |
|---|---|---|---|
| `badge.count` | `lk_badge_count` | — | paper |
| `badge.countWide` | `lk_badge_count_wide` | — | paper |
| `badge.number` | `lk_badge_number` | — | leather |
| `badge.pill` | `lk_pill_value` | — | paper |
| `bar.fill.blue` | `lk_bar_fill_blue` | — | fill |
| `bar.fill.green` | `lk_bar_fill_green` | — | fill |
| `bar.fill.orange` | `lk_bar_fill_orange` | — | fill |
| `bar.fill.red` | `lk_bar_fill_red` | — | fill |
| `bar.fill.yellow` | `lk_bar_fill_yellow` | — | fill |
| `bar.frame` | `lk_bar_frame` | — | paper |
| `bar.frameThin` | `lk_bar_frame_thin` | — | paper |
| `bar.stat` | `lk_statbar_frame` | — | paper |
| `bar.track` | `lk_bar_track` | — | track |
| `button.flat` | `lk_button_flat_paper` | disabled `lk_button_flat_disabled`, selected `lk_button_flat_leather` | paper |
| `button.play` | `lk_plaque_notched_leather` | disabled `lk_plaque_notched_disabled` | leather |
| `button.playSecondary` | `lk_plaque_notched_paper` | disabled `lk_plaque_notched_disabled` | paper |
| `button.primary` | `lk_button_leather_normal` | disabled `lk_button_leather_disabled`, hover `lk_button_leather_hover`, pressed `lk_button_leather_pressed` | leather |
| `button.secondary` | `lk_button_paper_normal` | disabled `lk_button_paper_disabled`, hover `lk_button_paper_hover`, pressed `lk_button_paper_pressed` | paper |
| `button.small` | `lk_button_paper_small_normal` | disabled `lk_button_paper_small_disabled`, hover `lk_button_paper_small_hover` | paper |
| `check.tileOff` | `lk_tile_check_off` | — | paper |
| `check.tileOn` | `lk_tile_check_on` | — | paper |
| `checkbox.off` | `lk_checkbox_off` | — | paper |
| `checkbox.on` | `lk_checkbox_on` | — | paper |
| `currency.pill` | `lk_currency_pill` | — | paper |
| `dialog.frame` | `lk_dialog_frame` | — | window |
| `divider.diamond` | `lk_divider_diamond` | — | rule |
| `divider.ornate` | `lk_divider_ornament` | — | rule |
| `divider.rule` | `lk_divider_line` | — | rule |
| `divider.vertical` | `lk_divider_vertical` | — | rule |
| `dot.green` | `lk_dot_green` | — | dot |
| `dot.grey` | `lk_dot_brown` | — | dot |
| `dot.red` | `lk_dot_red` | — | dot |
| `dot.yellow` | `lk_dot_yellow` | — | dot |
| `dropdown.field` | `lk_dropdown` | — | paper |
| `dropdown.list` | `lk_tooltip` | — | paper |
| `field.value` | `lk_button_paper_small_normal` | — | paper |
| `iconButton.close` | `lk_button_close_normal` | disabled `lk_button_close_disabled`, hover `lk_button_close_hover`, pressed `lk_button_close_pressed` | leather |
| `iconButton.dropdown` | `lk_dropdown_button` | — | paper |
| `iconButton.hud` | `lk_button_hud` | selected `lk_button_paper_small_hover` | paper |
| `iconButton.invite` | `lk_button_invite` | — | paper |
| `iconButton.leather` | `lk_button_square_leather` | — | leather |
| `iconButton.minus` | `lk_button_stepper_minus` | — | paper |
| `iconButton.paper` | `lk_button_square_paper` | selected `lk_button_paper_small_hover` | paper |
| `iconButton.plus` | `lk_button_stepper_plus` | — | paper |
| `iconButton.round` | `lk_frame_round` | — | paper |
| `iconButton.settings` | `lk_button_settings` | — | paper |
| `iconButton.small` | `lk_button_square_small` | selected `lk_button_paper_small_hover` | paper |
| `iconButton.tile` | `lk_tile_frame` | selected `lk_slot_selected` | paper |
| `keycap.cap` | `lk_keycap` | — | paper |
| `keycap.flat` | `lk_button_paper_small_normal` | disabled `lk_button_paper_small_disabled`, hover `lk_button_paper_small_hover` | paper |
| `keycap.wide` | `lk_keycap_wide` | — | paper |
| `mark.check` | `lk_glyph_checkmark` | — | glyph |
| `mark.chevron` | `lk_glyph_chevron_right` | — | glyph |
| `mark.confirm` | `lk_glyph_check_white` | — | glyph |
| `mark.cross` | `lk_glyph_cross` | — | glyph |
| `mark.crown` | `lk_icon_crown` | — | glyph |
| `mark.lock` | `lk_icon_lock` | — | glyph |
| `mark.play` | `lk_glyph_play` | — | glyph |
| `mark.star` | `lk_icon_star` | — | glyph |
| `panel.card` | `lk_panel` | — | paper |
| `panel.inset` | `lk_panel_inset` | — | paper |
| `panel.plaque` | `lk_plaque_small` | — | paper |
| `portrait.empty` | `lk_frame_round_paper` | — | dot |
| `portrait.round` | `lk_frame_hollow_circle` | — | none |
| `portrait.square` | `lk_portrait_frame` | — | none |
| `row.bullet` | `lk_row_bullet` | — | paper |
| `row.plate` | `lk_row_normal` | disabled `lk_row_disabled`, locked `lk_row_disabled`, selected `lk_row_hover` | paper |
| `scroll.thumb` | `lk_scroll_thumb` | — | leather |
| `scroll.track` | `lk_scroll_track` | — | track |
| `search.field` | `lk_search` | — | paper |
| `slider.fill` | `lk_bar_fill_yellow` | — | fill |
| `slider.knob` | `lk_button_paper_small_normal` | — | paper |
| `slider.knobRound` | `lk_slider_knob` | — | dot |
| `slider.track` | `lk_bar_track` | — | track |
| `slider.trackPaper` | `lk_slider_track` | — | paper |
| `slot.hotbar` | `lk_slot_normal` | disabled `lk_slot_disabled`, hover `lk_slot_hover`, locked `lk_slot_locked`, selected `lk_slot_selected` | slot |
| `slot.item` | `lk_slot_item_normal` | disabled `lk_slot_disabled`, locked `lk_slot_locked`, selected `lk_slot_item_selected` | slot |
| `slot.tile` | `lk_tile_blank` | — | slot |
| `tab.arrow` | `lk_tab_arrow_paper` | selected `lk_tab_arrow_leather` | paper |
| `tab.category` | — | selected `lk_tab_category` | none |
| `tab.horizontal` | `lk_button_paper_normal` | disabled `lk_button_paper_disabled`, hover `lk_button_paper_hover`, pressed `lk_button_paper_pressed`, selected `lk_button_leather_normal` | paper |
| `tab.side` | `lk_tile_frame` | disabled `lk_slot_disabled`, selected `lk_slot_item_selected` | paper |
| `toast.frame` | `lk_toast_frame` | — | paper |
| `toggle.off` | `lk_toggle_off` | — | paper |
| `toggle.on` | `lk_toggle_on` | — | fill |
| `tooltip.box` | `lk_tooltip` | — | paper |
| `tooltip.tail` | `lk_tooltip_tail` | — | none |
| `window.claspLeft` | `lk_clasp_left` | — | leather |
| `window.claspRight` | `lk_clasp_right` | — | leather |
| `window.frame` | `lk_window_frame` | — | window |
| `window.plaque` | `lk_plaque_paper` | — | paper |
| `window.rule` | `lk_divider_line` | — | rule |

Icons are not roles: `Kit.Icon` takes an id and resolves `lk_icon_<id>`, then
`lk_glyph_<id>` (square buttons prefer the glyph). Item art: `lk_item_<CatalogId>`,
then `item_<CatalogId>`, then the item's name in ink.

## 6. Components

Every example assumes `local Kit = require(...Hud.Kit)`.

### Screen
`Kit.Screen.new(name, {size = {w, h}, displayOrder?, dim = true, blur = true, layer = "window" | "dialog", parent?, onClose?})`
→ `{gui, veil, holder, window, scale, pop, Opened, Closed}`; `:Open(gamepad?)`,
`:Close()`, `:Toggle()`, `:IsOpen()`, `:Watch()` (keeps it fitted, ARCHITECTURE
§1.1), `:Fit(W, H, top, userScale)`, `:SetDefaultSelection(guiObject)`, `:Destroy()`.
Opening registers with `Kit.Modal` (closes any other window), fades the veil
(#050403 at 0.30) in and pops the window 0.94 → 1; closing reverses and then
disables the gui. Build into `screen.window` (the window's design-px frame).
```lua
local screen = Kit.Screen.new("FlintbornParty", { size = { 1124, 635 } })
screen:Watch()
screen.Closed:Connect(function() PartyController.OnClosed() end)
```

### Window
`Kit.Window.new(screenOrParent, {title, icon?, subtitle?, header = "banner" | "plaque" | "centered", smallCaps?, clasps? (true | "left" | "right"), claspYs? = {0.2, 0.86}, ornaments?, showClose = true, onClose?, rect? / size?})`;
`:Body()`, `.bodyRect`, `:SetTitle(text)`, `.close` (IconButton), `.title`.
Banner: icon 76 px at (40, 12), title at x 140 in `windowTitle`, subtitle in
`subtitleHand`, underline rule at y 80 up to the close button. Plaque (M05): the
title on `window.plaque` at top left. Centered (M04): the title centred with two
ornament icons (`tree` by default, D19) and a full rule. The close button sits
22 px in from the top-right corner and closes the screen (or calls `onClose`).
```lua
local window = Kit.Window.new(screen, { title = "Ancestral Forge", smallCaps = true,
    subtitle = "Turn raw materials into tools for the island.", icon = "anvil_hammer", clasps = true })
```

### Panel / SectionHeader
`Kit.Panel.new(parent, {rect, variant = "inset" | "card" | "plaque" | "plain", title?, icon?, count?, text?, textRole?, pad = 16, scroll?, contentHeight?})`
→ `:Content()`, `.contentRect`, `.header`. Inset = thin border on parchment
(columns, detail card); card = leather corners; plaque = paper title plaque
(`text` centred in `detailTitle`, M05 "Shattered Crater").
`Kit.SectionHeader.new(parent, {rect, text, icon?, count?, rule = true})` → `:SetText`, `:SetCount`.
```lua
local party = Kit.Panel.new(body, { rect = { 0, 0, 360, 445 }, title = "Your Party", icon = "party", count = "1/8", scroll = true })
```

### Button
`Kit.Button.new(parent, {rect | size, label, variant = "primary" | "secondary" | "play" | "playSecondary" | "flat", sizeClass = "s" | "m" | "l", icon?, textRole?, textSize?, onPress})`;
`:SetLabel`, `:SetVariant`, `:SetEnabled`, `:SetBusy`. Heights s 42 / m 58 /
l 76. Icons sit left of the label, centred together; white glyphs
(`play`, `check_white`) are tinted ink on paper.
**Invited (D18)**: `b:SetVariant("secondary"); b:SetLabel("Invited"); b:SetEnabled(false)`.
```lua
Kit.Button.new(footer, { rect = { 600, 0, 420, 76 }, label = "Play", icon = "play", variant = "play", sizeClass = "l", onPress = play })
```

### IconButton
`Kit.IconButton.new(parent, {rect | size, variant = "close" | "paper" | "leather" | "small" | "round" | "hud" | "tile" | "settings" | "invite" | "plus" | "minus" | "dropdown", icon?, tint?, badge?, onPress})`;
`:SetEnabled`, `:SetSelected`. Close, settings, invite, plus, minus and dropdown
carry their glyph in the art. Squares take flat glyphs (`plus minus check cross
arrow_left arrow_right arrow_up arrow_down`), tiles and HUD buttons take menu
icons. `badge = {variant = "dot"}` pins a Badge on the top-right corner.
```lua
Kit.IconButton.new(grid, { size = { 86, 86 }, layoutOrder = 1, variant = "tile", icon = "backpack", onPress = openBackpack })
```

### Tab / TabGroup
`Kit.Tab.new(parent, {id?, rect | size, label?, icon?, variant = "category" | "arrow" | "horizontal" | "large" | "side", onPress?})`;
`:SetSelected`, `:SetEnabled`, `:SetLabel`. `Kit.TabGroup.new(tabs, onSelect)` →
`:Select(id)` (scripted, no callback), `:Selected()`, `:Destroy()`; a press
selects and calls `onSelect(id)`. Category: no plate until selected (the
paper arrow plate; hover shows it faintly). Horizontal / large: parchment,
leather when selected with cream text (pass a white icon such as
`backpack_white` for the leather look). Side (M07): square tile, gold glow
when selected.
```lua
local group = Kit.TabGroup.new({
    Kit.Tab.new(bar, { id = "Gameplay", rect = { 0, 0, 237, 81 }, label = "Gameplay", icon = "gear", variant = "large" }),
    Kit.Tab.new(bar, { id = "Audio", rect = { 0, 94, 237, 81 }, label = "Audio", icon = "speech", variant = "large" }),
}, showPage)
group:Select("Gameplay")
```

### Slot
`Kit.Slot.new(parent, {rect | size, variant = "item" | "hotbar", item?, count?, hotkey?, countStyle = "text" | "plaque", onPress})`;
`:SetItem({catalogId, quantity?, permanent?, icon?} | nil)`, `:SetCount(n)`,
`:SetHotkey(text | nil)`, `:SetState("normal" | "locked" | "disabled")`,
`:SetSelected`, `:SetEnabled`. Count bottom-right (hidden for 1), Permanent star
top-right, leather number badge top-left. `icon` shows an icon id when the item
has no art of its own yet.
```lua
local slot = Kit.Slot.new(grid, { size = { 92, 99 }, layoutOrder = i, onPress = function(s) select(s.item) end })
slot:SetItem({ catalogId = item.catalogId, quantity = item.quantity, permanent = item.permanent })
```

### Bar
`Kit.Bar.new(parent, {rect, fill = "xp" | "health" | "stamina" | "food" | "blue" | "yellow" | "red" | "green" | "orange", frame = "track" | "none" | "well" | "thin" | "stat", icon?, text?, textColor = "ink", value = 0})`;
`:Set(fraction, instant?)` (eases with the `bar` token; the real fraction, D20),
`:SetText`. Stat frame: icon in the left box, `text` in the right box, the fill
in the well. Fills thinner than their end caps hide.
```lua
local health = Kit.Bar.new(hud, { rect = { 0, 0, 315, 65 }, fill = "health", frame = "stat", icon = "heart", text = "85" })
health:Set(0.85)
```

### Checkbox
`Kit.Checkbox.new(parent, {rect, label?, description?, checked, variant = "box" | "gold" | "tile", boxSize?, onToggle(checked)})`;
`:SetChecked`, `:SetEnabled`. "gold" tints the ticked box as M03 draws it;
"tile" is the quest objective check (sheet 12).
```lua
Kit.Checkbox.new(page, { rect = { 0, 230, 380, 50 }, label = "Show Damage Numbers", description = "Numbers pop up over what you hit", checked = v, variant = "gold", onToggle = set })
```

### Toggle
`Kit.Toggle.new(parent, {rect = 89 × 49, on, onToggle(on)})`; `:Set(on)`, `:SetEnabled`.

### Slider
`Kit.Slider.new(parent, {rect, min, max, step?, value, valueBox = true, boxWidth = 74, format?(v) → string, knob = "plate" | "round", track = "dark" | "paper", onChange(v)})`;
`:SetValue(v)` (no callback), `:SetEnabled`. Dark track with the yellow fill
and a paper knob (M03); drag, track press, or gamepad left / right while
selected.
```lua
Kit.Slider.new(page, { rect = { 0, 40, 375, 34 }, min = 10, max = 100, step = 1, value = 50,
    format = function(v) return ("%.1f"):format(SettingsRules.MouseSensitivity(v)) end, onChange = set })
```

### Dropdown
`Kit.Dropdown.new(parent, {rect, options, value?, onSelect(v), openUp?, layer?})`;
`:SetValue`, `:SetOpen(bool)`, `:IsOpen()`, `:SetEnabled`. Options are
`ListRow` "option" rows on a paper panel; a press outside closes it; `layer`
(the page) is raised while open.

### SearchBox
`Kit.SearchBox.new(parent, {rect, placeholder, text?, debounce = 0.15, onChanged(text)})`;
`:GetText`, `:SetText`, `:SetEnabled`. States normal / focused / disabled
(a text field has no press state; `DebugState` still works).

### Stepper
`Kit.Stepper.new(parent, {rect, min = 1, max, value, step = 1, allLabel?, onChange(v)})`;
`:SetValue`, `:SetRange(min, max)`. − / + disable at the limits.

### KeyCap
`Kit.KeyCap.new(parent, {text, rect = {x, y, 0, h} (0 fits the text) | height, variant = "cap" | "flat", onPress?})`;
`Kit.KeyCap.Width(text, height)`, `:SetText`, `:SetCapturing(bool)`,
`:SetEnabled`. "cap" is the raised key (wide art for words), "flat" the M03
key-binds box.

### Divider
`Kit.Divider.new(parent, {rect, variant = "rule" | "header" | "ornate" | "diamond" | "vertical"})`.
The art keeps its own thickness, centred on the rect's mid-line.

### ListRow
`Kit.ListRow.new(parent, {rect | size, variant = "row" | "card" | "line" | "option", icon?, catalogId?, title, subtitle?, value?, valueColor?, chevron?, onPress?})`;
`:SetTitle`, `:SetSubtitle`, `:SetValue(text, colorKey?)`, `:SetSelected`,
`:SetEnabled`, `:SetState("normal" | "locked" | "disabled")`. Selected = gold
glow plate (M06 / M07); locked = disabled plate + lock. "line" has no plate:
label left, value right, a rule under (detail rows). Not-enough counts:
`valueColor = "short"`.
```lua
Kit.ListRow.new(list, { size = { 300, 72 }, layoutOrder = i, variant = "card", icon = "pickaxe",
    title = "Iron Pickaxe", subtitle = "Pickaxe · Tier 3", chevron = true, onPress = pick })
```

### PlayerRow
`Kit.PlayerRow.new(parent, {rect | size, userId?, name?, level?, leader?, badge? ("leader" | "ready" | "notReady"), action? ({label, onPress, variant?, enabled?}), empty?, emptyText?, rule = true, frame?, onPress?})`;
`:Set(data)` redraws, `:SetSelected`. The empty row is a muted disc and
"Empty Slot".
```lua
Kit.PlayerRow.new(list, { size = { 330, 52 }, userId = id, name = name, level = level, leader = isLeader, badge = if ready then "ready" else "notReady" })
```

### Badge
`Kit.Badge.new(parent, {variant = "leader" | "ready" | "notReady" | "count" | "number" | "new" | "dot", text?, rect = {x, y, 0, h} (0 fits the text), anchor? = "topRight"})`;
`:SetText`, `:SetVisible`. Ready = green dot + "Ready", Not Ready = grey dot +
"Not Ready" (D18).

### CurrencyPill
`Kit.CurrencyPill.new(parent, {rect = 112 × 46, currency = "coins" | "gems", value, onPress?})`;
`:SetValue(n, instant?)` counts up with thousands separators.

### Portrait
`Kit.Portrait.new(parent, {rect, userId, frame = "square" | "round"})`; `:SetUser(id)`.
Headshot `rbxthumb://type=AvatarHeadShot&id=<id>&w=150&h=150` behind the frame,
reported to `SpriteLoader.Track`.

### Icon / ItemIcon
`Kit.Icon.new(parent, {rect, icon, tint?})`; `:SetIcon(id)`.
`Kit.ItemIcon.new(parent, {rect, catalogId, icon?})`; `:SetItem(catalogId, icon?)`.

### Text
`Kit.Text.new(parent, {rect, text, role, align = "Left", yAlign = "Center", wrap?, scaled?, color?, caps?, smallCaps?})`;
`:SetText`, `:SetColor(token)`. `Kit.Text.SmallCaps(text, role?, ratio?)` builds
the RichText small caps; `Kit.Text.Width(text, role, size?)` measures.

### Scroll
`Kit.Scroll.new(parent, {rect, gap = 6 (false for no list layout), padBottom = 12, contentHeight?})`
→ `:Content()` (the ScrollingFrame with a UIListLayout), `:SetContentHeight(h)`.
The kit rail and thumb follow `CanvasPosition`; the native bar is hidden.

### Toast
`Kit.Toast.Show({kind = "quest" | "item" | "info" | "warn", title, text?, icon?, duration = 4, onPress?, onClose?, actions? = {{label, onPress, variant?}}})`
→ handle `{Close, toast}`. Up to three stacked top-centre in `KitToasts`
(DisplayOrder 40); the oldest goes first; each slides 24 px and fades.
`Kit.Toast.new(parent, props)` draws one card in place.

### ConfirmDialog
`Kit.ConfirmDialog.Show({title, text? | build?(body, w, h), confirmLabel = "Confirm", cancelLabel = "Cancel", danger?, holdSeconds?, onConfirm(dialog), onCancel?, size? = {560, 330}})`
→ `{Close, SetBusy, dialog, screen}`. Opens on the dialog layer above the
window (Escape / B and ✕ cancel). It closes itself after onConfirm unless
`SetBusy(true)` was called inside it (then call `Close()` when the request
returns). `holdSeconds` makes CONFIRM a press-and-hold with a filling bar.
`Kit.ConfirmDialog.new(parent, props)` draws one in place.
```lua
local dialog = Kit.ConfirmDialog.Show({ title = "Take these into the run?", build = listItems, confirmLabel = "Enter",
    onConfirm = function(d) d:SetBusy(true); LobbyController.Deploy() end })
```

### Tooltip
`Kit.Tooltip.Attach(target (component or GuiObject), textOrFn, {side = "top" | "right"})` → detach function.
Shows on mouse hover, a 0.5 s touch hold and gamepad selection, in `KitTooltip`
(DisplayOrder 45). `Kit.Tooltip.new(parent, {rect = {x, y, 0, 0}, text, tail = "bottom" | "top" | "none"})` draws one in place.

### Modal, Scale, Interact (for screen code that needs them)
- `Kit.Modal.Open(entry, layer, gamepad?)`, `Closed(entry)`, `Top()`, `Count()`,
  `IsOpen(entry)`, `Back()`. Screens do this themselves; call `Back()` from a
  custom back button.
- `Kit.Scale.Hud(gui, root, {refW?, refH?})` → stop function; sizes `root` to
  1/scale and keeps the HUD scale (`HudModel.HudScale`, × 0.9 on short touch
  screens). `Kit.Scale.TopInset(gui)` replaces `Parchment.TopInset`.
- `Kit.Interact.attach(base, {onPress, onLocked, render(state, ctrl), pad, hoverScale, pressScale, selectable, sound, debounce, hit})`
  for a custom interactive part built on `Kit.Core.Root`.

## 7. Before upload: stand-ins

Until a sprite has an uploaded id (or sits in an uploaded atlas), `Art` draws a
stand-in in the kit's style: paper `#FCDAB1` / leather `#A53A0F` plates with a
2 px brown stroke and 8 px corners, slots with 6 px corners, windows with a
3 px rail stroke and 10 px corners, tracks and fills as pills, glyphs and icons
as text. Hover, focus and selection add the 3 px gold glow stroke. See
`kit_gallery_*_fallback.png`.

**UiSprites.json must list the `lk_` sprites** before they draw as art in game
(sizes and 9-slice insets): the asset artist's
`scripts/roblox_upload_ui_assets.py --sprites` sync does it. Captures read them
from `art/ui/sprites/manifest.json` until then.

## 8. Deviations from the mockups (D19: closest `lk_` art)

| Where | Mockup | Kit |
|---|---|---|
| Window title underline | plain tapering rule | `lk_divider_line` (diamond ends) |
| Slider knob (M03) | small paper knob | `lk_button_paper_small_normal` at 23 × 26 (`knob = "round"` for the sheet-09 ball) |
| Slider track (M03) | dark track, yellow fill | `lk_bar_track` + `lk_bar_fill_yellow` |
| Ticked checkbox (M03) | gold box | `lk_checkbox_on` tinted `checkTint` (variant "gold") |
| Leader tag (M04) | gold plaque | `lk_pill_value` tinted `leaderTint` |
| Ready tag (M04) | yellow-green pill | `lk_pill_value` (untinted: a multiply tint cannot lighten green) + `lk_dot_green` |
| Not Ready dot | grey dot | `lk_dot_brown` |
| Empty party slot dot | muted disc | `lk_frame_round_paper` |
| Party header trees (M04) | tent and trees | `lk_icon_tree` ornaments |
| Category icons (M02) | grid, apple, leaf, sack | closest icons (`chest`, `drumstick`, `plant_fiber`, `gift`); screens choose |
| Rows / tags rules | plain thin rules | `lk_divider_line` |

## 9. Capture notes and limits

- Fonts: `art/ui/fonts` holds Merriweather Regular, Bold, Black (Heavy) and
  Patrick Hand (SIL OFL 1.1; `OFL.txt`, `OFL-PatrickHand.txt`). Merriweather Black
  comes from the upstream `SorkinType/Merriweather` repository (Google Fonts now
  ships only the variable font); Patrick Hand from `google/fonts`.
- `render.py` draws RichText `<font size>` / `<font color>` runs on one line
  (small caps), nested ScreenGuis (a whole PlayerGui), and a per-page background
  image (`__dump(root, w, h, {background = "art/reference/..."})`).
- `TextService:GetTextSize` in the env measures with the real font widths
  (injected by `capture.py`), so auto-width badges, key caps and buttons match.
- `capture.py --compare <ref.png> [--crop x y w h]` writes `_compare.png`
  (side by side) and `_overlay.png` (50 % blend) and prints the mean difference;
  `--page n` writes one page; `--suffix` tags outputs.
- **Not drawn in captures:** `Rotation` (the tooltip's top tail is the bottom
  tail rotated: it draws pointing down), CanvasGroup `GroupTransparency` (toast
  fades), BlurEffect, tween motion (tweens finish at once), and symbol glyphs
  Merriweather lacks (★ draws as a box; Roblox falls back to another font in
  game). Absolute sizes are zero, so `Scroll` sizes its thumb from
  `contentHeight` and the slider drag maths runs only in game.
- Escape is also Roblox's menu key; gamepad B is the dependable back input.
- `KitModel` specs cannot read the sprite manifest (the spec runner mounts only
  Luau modules), so "every role resolves to a manifest sprite" is asserted by
  `kit_gallery` (`Kit.Art.Missing()` must be empty) on every capture.
