# UI architecture: the unified parchment-and-leather kit

Every screen in the game is rebuilt from one shared kit. The seven mockups in
[`art/reference/ui/lobby/`](../../art/reference/ui/lobby/README.md) are matched 1:1.
Every other screen is restyled with the same components and sprites. This document is
the contract for the kit builder, the screen builders and the integration engineer.
Per-screen measurements live in the analysts' specs (`docs/ui/<Screen>.md`). Where a
spec gives an exact number, it overrides the approximate ones here.

Terms:
- **design px**: pixels on the 1672 × 941 mockup canvas.
- **role**: what a sprite is for, for example "leather button, hover". Screens never
  name sprites. The kit maps roles to `lk_*` names from `art/ui/kit/CATALOG.md`.

---

## 1. Scaling and ScreenGui setup

### 1.1 Strategy

Every screen is built in design px (strategy A of the technical reference) under a
root `UIScale`. `HudModel.HudScale` stays the single formula. `Layout.Place`-style
entries `{anchor, pos=[sx,ox,sy,oy], size}` keep the HUD regions pinned to the
screen edges.

| Surface | Root scale | Anchoring | Notes |
|---|---|---|---|
| Lobby HUD (01) and world HUD | `HudModel.HudScale(screenW, screenH, 1672, 941, min 0.34, max 1.6, UiScale attr)`. On touch-only screens shorter than 500 px it is multiplied by 0.9 (as `LobbyHudController.applyScale` does today). | Root frame `Size = 1/scale` and regions placed by anchor. Player card: top-left. Currencies and settings: top-right. Tile grid: left, vertically centred (y ≈ 0.48). Party panel: right (top ≈ 258). XP bar and hotbar: bottom-centre. | Keep the top region clear of the Roblox top bar: `Kit.Scale.TopInset(gui)` (moved from `Parchment.TopInset`), never less than 52 screen px. |
| Windows (02–07 and every restyled window) | **Desktop and tablet:** `min(fitRoom, canvasFit × UiScale)`, so at 1672 × 941 a window draws exactly as large as in the mockup. **Touch-only with height < 500:** `fitRoom`, which fills the screen for readability. Clamped to 0.3–1.4. | Window centred on the screen centre (mockups centre windows at about (836, 470)). The top edge is clamped below the top inset plus an 8 px margin. | `fitRoom = min((W − 16)/w, (H − top − 16)/h)`, as in `Parchment.Screen:Fit`. `canvasFit = min(W/1672, H/941)`. |
| Toasts, tooltips, dialogs | Same scale as windows (dialogs) or HUD (toasts, tooltips) | Toasts: top-centre below the top inset. Dialog: centred. Tooltip: beside its target. | |

Approximate window sizes (outer frame, design px, from the mockups; specs give the
exact values): Inventory ≈ 1184 × 650, Settings ≈ 1096 × 658, Party ≈ 1124 × 635,
Play ≈ 1054 × 668, Forge ≈ 1102 × 679, Journal ≈ 1072 × 688 plus side tabs reaching
50 px left of the frame.

Text stays readable on phones because windows fill the screen there. `Kit.Text`
applies `Widgets.TextCap` (layout-px caps that follow parent UIScales) with a
screen-px floor of 9.

### 1.2 ScreenGuis

All ScreenGuis use `ZIndexBehavior = Sibling`, `ResetOnSpawn = false`,
`IgnoreGuiInset = true` and `ScreenInsets = DeviceSafeInsets` (in a pcall, as today).
A hidden screen sets `Enabled = false`.

| Gui | DisplayOrder | Default | Owner module |
|---|---|---|---|
| `FlintbornLobbyHud` / world `FlintbornHud` | 1 | on | Screens/LobbyHud, HudController |
| `TopStack` (world banners, `Theme.TopStack`) | 5 | on | Theme (existing) |
| One per window (`FlintbornInventory`, `FlintbornParty`, …) via `Kit.Screen` | 20 | off | each screen |
| `KitDialog` (ConfirmDialog over a window) | 30 | off | Kit |
| `KitToasts` | 40 | on, empty | Kit |
| `KitTooltip` | 45 | off | Kit |
| `Subtitles` (existing `Theme.Subtitle`) | 50 | — | Theme |

### 1.3 Overlay dim behind modal windows

The mockups darken the world to about 42 % brightness and slightly blur it. Sampled:
sky `#51A8F7` → `#244360`, wood `#A05127` → `#452510`.

- `Kit.Screen` draws a **veil**: a Frame with color `veil #0A0603`,
  `BackgroundTransparency 0.42`, `Active = true` (it sinks clicks), extended 400 px
  past the safe area (as `Parchment.Screen` does). It fades from 1 to 0.42 in 0.2 s,
  or instantly with reduced motion.
- **Optional blur:** one shared `Lighting.KitBlur` BlurEffect, Size 0 → 8, only while
  a window is open and only when `GraphicsQuality ~= "Low"`. It is ref-counted by
  `Kit.Modal` and always restored on close. Nothing else in the repo uses a
  BlurEffect today. Captures cannot show it (see §7).
- Only one window is open at a time. `Kit.Modal.Open(screen)` closes the current
  window before it shows the new one. ConfirmDialog stacks above the window.
  Escape and ButtonB close the top layer (ContextActionService bind while open).
  On open, gamepad selection goes to the window's default control, and the previous
  selection comes back on close. The window frame is a `SelectionGroup`.

---

## 2. The Kit module

### 2.1 Files

`src/client/Hud/Kit/` is a ModuleScript folder. `init.luau` re-exports everything,
so callers write `local Kit = require(Hud.Kit)` and then `Kit.Button.new(...)`.

| File | Contents |
|---|---|
| `init.luau` | `Kit.Tokens`, `Kit.Art`, `Kit.Interact`, `Kit.Motion`, `Kit.Sound`, `Kit.Scale`, `Kit.Modal`, plus every component below |
| `Tokens.luau` | Reads `src/shared/UI/KitTokens.json`. Provides `Tokens.Color(key)`, `Tokens.Font(role)`, `Tokens.TextStyle(role)`, `Tokens.Space(key)`, `Tokens.Motion(key)`, `Tokens.Order(key)` |
| `Art.luau` | Role → `lk_*` sprite table (`Art.ROLES`), `Art.Image(role, props, parent)`, `Art.Set(holder, role)` (state swap), `Art.Icon(id)`, `Art.ItemIcon(catalogId)`, and fallbacks drawn before upload |
| `Interact.luau` | The state machine shared by every interactive component (see 2.3) |
| `Motion.luau` | Tween presets from tokens, `Motion.Play(inst, key, goal)` (cancels running tweens per instance/property), honours `Theme.ReducedMotion()` |
| `Sound.luau` | `Sound.Play(key)`: hover, click, open, close, error, success. Ids come from tokens; an empty id is silent |
| `Scale.luau` | `Scale.Hud(gui, root, opts)`, `Scale.Window(screen)`, `Scale.TopInset(gui)` |
| `Modal.luau` | One-window-at-a-time registry, veil, blur, Escape/B, selection save and restore |
| `Debug.luau` | `Debug.Each(root, fn)`, `Debug.Force(root, state)` (sets `DebugState`) for scenes and verifiers |
| Component files | `Screen, Window, Panel, Button, IconButton, Tab, Slot, Bar, Checkbox, Toggle, Slider, Dropdown, SearchBox, Stepper, KeyCap, Divider, ListRow, PlayerRow, Badge, CurrencyPill, Portrait, Icon, Text, Scroll, Toast, ConfirmDialog, Tooltip` |

Screens live in `src/client/Hud/Screens/<Name>.luau`. They are display only: they
take data through setters and report presses through callbacks. Controllers fetch
data and call remotes. This is the split the repo already uses (LobbyHud and
LobbyHudController).

### 2.2 Conventions

- Constructor: `Kit.X.new(parent: Instance, props): X`. The object has `.root`
  (GuiObject) and `:Destroy()`, which disconnects everything.
- Placement props: `rect = {x, y, w, h}` in the parent's design px (the Parchment
  convention), **or** `size = {w, h}` plus `layoutOrder` for children of a layout.
  Optional: `zIndex`, `name`.
- Callbacks are props (`onPress`, `onChange`, `onSelect`), as in `Parchment`.
  Setters are methods (`:SetLabel`, `:SetValue`, `:SetEnabled`, `:SetSelected`,
  `:SetState`).
- Root attributes on every component, for verifiers and scenes:
  - `KitComponent`, for example `"Button"`.
  - `KitRole`, for example `"button.leather"`.
  - `KitState` (output): the state currently drawn.
  - `DebugState` (input): see 2.3.
- No text is baked into art. Every word is a live TextLabel, so it can be localized
  and stays honest. Kit parts whose art carries words ("PLAY", "CONFIRM",
  "QUEST COMPLETE", "CLAIM", "FORGE" on sheets 03, 12 and 13) are used only as
  word-free plates. The asset artist erases or skips their words.
- Item, menu and world icons go through `Kit.Icon` and `Kit.ItemIcon` only.

### 2.3 States and the debug hook

`Kit.Interact.attach(root, opts) → controller` is used by every interactive component.

| State | Live trigger | Visual (default) |
|---|---|---|
| `normal` | — | normal art |
| `hover` | MouseEnter, only while `Theme.UsingMouse()`, or gamepad `SelectionGained` | hover art if the kit has one (03, 05, 09), otherwise `ImageColor3` 0.93 tint; tiles and icon buttons also scale to 1.03 |
| `pressed` | `InputBegan` (mouse, touch, gamepad A) until `InputEnded`; cancelled if the pointer leaves | pressed art, or 0.80 tint and scale 0.96 |
| `selected` | `:SetSelected(true)` (tabs, rows, slots) | selected art (gold glow `#FDAA09` on slots and rows, leather on tabs) |
| `disabled` | `:SetEnabled(false)` | disabled art (desaturated plates on 03, 05, 09), or 0.72 tint. Sets `Interactable = false` and `Selectable = false` |
| `locked` | `:SetState("locked")` | disabled art plus a lock icon (05, 13). Still selectable so the tooltip can explain why |
| `busy` | `:SetBusy(true)` (buttons) | label "…", not interactive |
| `capturing` | KeyCap waiting for a key | hover art plus pulsing outline |

- **`DebugState` attribute.** When a string is set on a component root, it overrides
  the live state immediately (read at build time and on
  `GetAttributeChangedSignal`). `nil` or `""` returns to live input. Scenes use it
  to capture every state headlessly. For example:
  `button.root:SetAttribute("DebugState", "hover")`.
- `Kit.Debug.Each(root, fn)` walks descendants that have `KitComponent`. Galleries
  and verifiers use it.
- **State swaps without rebuilding.** The variants of a role (normal, hover, pressed,
  disabled) are sliced to the same size and 9-slice insets and packed into the same
  atlas. `Art.Set(holder, role)` then only rewrites the 9 pieces'
  `ImageRectOffset`. A role whose variants differ falls back to rebuilding.
- **Touch.** There is no hover state. Each component's hit area is padded to at least
  44 screen px where the layout allows (`pad` prop, as in `Parchment.Pressable`).
- **Gamepad.** Each button sets `SelectionImageObject` to an empty frame. The kit's
  hover state is the selection cue.

### 2.4 Motion and sound defaults (tokens `motion`)

| Key | Time | Easing | Used by |
|---|---|---|---|
| hover | 0.12 s | Quad Out | tint, scale 1.03 |
| press | 0.07 s | Quad Out | scale 0.96 |
| release | 0.18 s | Back Out | scale back to 1 |
| windowOpen | 0.22 s | Quint Out | window UIScale 0.94 → 1, veil fade |
| windowClose | 0.15 s | Quad In | reverse |
| toastIn / toastOut | 0.25 s / 0.2 s | Quint Out / Quad In | slide 24 px and fade |
| bar | 0.25 s | Quad Out | bar fills (`Widgets.BAR_TWEEN`) |
| count | 0.4 s | Quad Out | currency count-up |
| knob | 0.12 s | Quad Out | toggle knob |

With reduced motion (`Theme.ReducedMotion()`), every move or scale becomes instant
and fades take at most 0.1 s.

There is no UI sound helper in the repo today. `Kit.Sound` creates pooled `Sound`s
under SoundService with no SoundGroup, so `PreferencesController` routes them to
Effects. The ids in `KitTokens.json` `sounds` stay empty (silent) until the owner
supplies them. Hover sounds never play on touch.

### 2.5 Components

Sheet numbers refer to `art/reference/ui/lobby/kit/NN_*.png`. "M" means the mockup.

| Component | Constructor | Parts (roles) | States | Sheets |
|---|---|---|---|---|
| **Screen** (modal layer) | `Kit.Screen.new(name, {size={w,h}, displayOrder=20, dim=true, blur=true, parent})` → `{gui, veil, window, scale}`; `:Open(gamepad?)`, `:Close()`, `:IsOpen()`, `:Watch()`; signals `Opened`, `Closed` | veil, window frame holder, UIScale | open / closed | — |
| **Window** | `Kit.Window.new(screen, {title, icon?, subtitle?, header="banner"\|"plaque"\|"centered", clasps?, showClose=true, onClose})`; `:Body()`, `:SetTitle()` | window frame (9-slice, corner pieces, optional side clasps), header icon (64–80 px), title, handwritten subtitle, header underline rule, close button | — | 04, 10, 13, 14 (corners, clasps); M02 banner, M05 plaque, M04 centred with tree ornaments |
| **Panel** / **SectionHeader** | `Kit.Panel.new(parent, {rect, title?, icon?, variant="inset"\|"card"\|"plain", scroll?})`; `:Content()`. `Kit.SectionHeader.new(parent, {rect, text, icon?, rule=true})` | inset frame, detail card, header caps text, header rule, optional Scroll | — | 01 (layouts), 10 (detail cards), 12 (frames); M04/M06 column insets |
| **Button** | `Kit.Button.new(parent, {rect\|size, label, variant="primary"\|"secondary"\|"play", size="s"\|"m"\|"l", icon?, onPress})`; `:SetLabel`, `:SetEnabled`, `:SetBusy` | leather plate (primary), parchment plate (secondary), notched plaque (play), icon at left, label | normal, hover, pressed, disabled, busy | 03 rows 1–2 and the bottom row (Play/Confirm plates, small parchment buttons ×3 states), 12 (Claim/Forge plates) |
| **IconButton** | `Kit.IconButton.new(parent, {rect, icon, variant="paper"\|"leather"\|"close"\|"tile"\|"round", onPress, badge?})` | square plate, glyph or icon, optional Badge | normal, hover, pressed, disabled, selected | 03 row 3 (close ×4 states), row 4 (+ − ✓ ✕ arrows, round frame); 02 (HUD square buttons); 06/07 (menu tiles); 15 (add-friend) |
| **Tab** + **TabGroup** | `Kit.Tab.new(parent, {rect, label, icon?, variant="category"\|"horizontal"\|"side"\|"large", onPress})`; `Kit.TabGroup.new(tabs, onSelect)` → `:Select(id)` | category: row with icon and a selected arrow plate (M02, 10, 14 arrow tabs); horizontal: Backpack/Vault (10); side: square icon tab (M07); large: leather/paper notched tab with clasps (M03, 03 row 5) | normal, hover, pressed, selected, disabled | 03, 10, 14 |
| **Slot** | `Kit.Slot.new(parent, {size=90, item?, count?, hotkey?, onPress})`; `:SetItem(item?)`, `:SetCount`, `:SetHotkey`, `:SetState` | slot frame, `Kit.ItemIcon`, count (text bottom-right as in M02, or count plaque), hotbar number badge (leather 1–6), lock, Permanent star | normal, hover, pressed, selected, disabled, locked, empty | 05 (5 states, badges 1–6, count plaques), 13 (count frames), 02 (numbered hotbar) |
| **Bar** | `Kit.Bar.new(parent, {rect, fill="xp"\|"health"\|"stamina"\|"food"\|"blue"\|"green"\|"orange", frame="none"\|"track"\|"stat", icon?, text?})`; `:Set(fraction, instant?)`, `:SetText` | track, fill (9-slice horizontal), stat frame with icon plate and value plaque | — (value) | 05 (XP fill + track), 08, 18 (0/50/100 %), 19 (5 fills, empty bar), 20 (3 widths) |
| **Checkbox** | `Kit.Checkbox.new(parent, {rect, label, description?, checked, onToggle})` | box, check, label, grey description | normal, hover, pressed, disabled; checked flag | 09, 12 (check rows); M03 yellow box |
| **Toggle** | `Kit.Toggle.new(parent, {rect, on, onToggle})` | pill track off/on, knob | normal, hover, pressed, disabled; on flag | 09 |
| **Slider** | `Kit.Slider.new(parent, {rect, min, max, step, value, valueBox=true, format?, onChange})`; `:SetValue` | track, fill, knob, value box | normal, hover, pressed (dragging), disabled | 09 (track, knob), M03 (yellow fill on a dark track), 01 (plaque value box) |
| **Dropdown** | `Kit.Dropdown.new(parent, {rect, options, value, onSelect, openUp?, layer?})` | field, ▼ arrow, list panel of ListRows | normal, hover, pressed, open, disabled | 09 |
| **SearchBox** | `Kit.SearchBox.new(parent, {rect, placeholder, onChanged, debounce=0.15})` | field, magnifier, TextBox, clear ✕ | normal, focused, disabled | 09, 10, 15 |
| **Stepper** | `Kit.Stepper.new(parent, {rect, min, max, value, onChange, allLabel?})` | − / + square buttons, value field | buttons as IconButton; at a limit the button is disabled | 09, 03 row 4, M06 |
| **KeyCap** | `Kit.KeyCap.new(parent, {rect\|height, text, autoWidth=true, onPress?})`; `Kit.KeyCap.Width(text)` | cap plate, key text | normal, hover, pressed, capturing, disabled | 09 (E/TAB/SHIFT/ESC), M03 flat boxes |
| **Divider** | `Kit.Divider.new(parent, {rect, variant="rule"\|"ornate"\|"vertical"\|"header"})` | line or ornate rule with diamond ends | — | 09, 14, 01 (column rules) |
| **ListRow** | `Kit.ListRow.new(parent, {size, icon?, title, subtitle?, value?, chevron?, variant="row"\|"card", onPress})` | plate, icon, title, subtitle, right value, chevron | normal, hover, pressed, selected, disabled, locked | 09 (3 states), 12 (objective rows), M06 recipe cards, M07 quest rows |
| **PlayerRow** | `Kit.PlayerRow.new(parent, {size, userId?, name?, level?, leader?, badge?, action?, empty?})`; `:Set(data)` | `Kit.Portrait`, name, "LV. n", crown, Badge, action Button; empty variant: dot + "Empty Slot" | normal, hover, selected, empty | 01, 15 (player rows, round frames), 06 (crown) |
| **Badge** | `Kit.Badge.new(parent, {text?, variant="leader"\|"ready"\|"notReady"\|"count"\|"number"\|"dot"\|"new"})` | plaque or pill, status dot | — | 01 (status dots, plaques), 13 (dots), 05 (number and count badges); M04 Leader/Ready |
| **CurrencyPill** | `Kit.CurrencyPill.new(parent, {rect, currency="coins"\|"gems", value, onPress?})`; `:SetValue(n, instant?)` | plaque, coin or gem icon, value (`HudModel.Thousands`) | normal, hover, pressed | 07, 06 |
| **Portrait** | `Kit.Portrait.new(parent, {rect, userId, frame="square"\|"round"})` | frame and headshot. The headshot uses the content URL `rbxthumb://type=AvatarHeadShot&id=<id>&w=150&h=150` (no yield; the capture draws its placeholder head), reported to `SpriteLoader.Track` | — | 01, 15, 07 |
| **Icon** / **ItemIcon** | `Kit.Icon.new(parent, {rect, icon=id, tint?})`; `Kit.ItemIcon.new(parent, {rect, catalogId})` | icon id → `lk_icon_*`. For items: `lk_item_<catalogId>`, then `item_<catalogId>`, else the item name in ink (the current `ItemSlot.IconFor` hook) | — | 06, 11, 16, 17; item art on 02, 10, 12, 16 |
| **Text** | `Kit.Text.new(parent, {rect, text, role, align, wrap, scaled, color?})`; `Kit.Text.SmallCaps(...)` | TextLabel with the role's FontFace, size and color; TextCap | — | — |
| **Scroll** | `Kit.Scroll.new(parent, {rect, direction="Y", padBottom=12})` | ScrollingFrame with `ScrollBarThickness = 0`, plus a kit track and thumb synced to `CanvasPosition` (native scrollbar images cannot use atlas rects) | — | 09 (rail and thumb), 10 |
| **Toast** | `Kit.Toast.Show({kind="quest"\|"item"\|"info"\|"warn", title, text?, icon?, duration=4, onPress?, actions?})` → handle | banner plate, emblem icon, title, ✕. Up to 3 stacked in `KitToasts`; the oldest goes first | in, out | 13 (Quest Complete / Item Received) |
| **ConfirmDialog** | `Kit.ConfirmDialog.Show({title, text?, build?(body), confirmLabel="CONFIRM", cancelLabel="CANCEL", danger?, holdSeconds?, onConfirm, onCancel})` → `{Close, SetBusy}` | dialog frame, title, ornate rule, body (text or custom rows), Cancel (secondary) and Confirm (primary) buttons, close ✕ | busy | 13 (confirm, empty dialog), 03 |
| **Tooltip** | `Kit.Tooltip.Attach(target, textOrBuilder, {side="top"\|"right"})` | box with tail | shown on hover (mouse), long-press (touch) or selection (gamepad) | 09, 13 |

Fallbacks before upload (`Art`): if a role's sprite has no id and no uploaded atlas,
Art draws a Frame in the role's material:

| Material | Fill | Stroke | Corner |
|---|---|---|---|
| paper | `paper` | 2 px `rule`/`paperEdge` | 8 |
| leather | `leather` | 2 px `leatherEdge` | 8 |
| slot | `slot` | 2 px `paperEdge` | 6 |
| bar | `track` and fill colors | — | pill |

- An icon falls back to a glyph in ink.
- The window frame falls back to `paper` with a 3 px `rail` stroke and corner 10.
- Selected and hover states add a 3 px `glow` UIStroke.

Captures still preview un-uploaded PNGs (capture.py `preview_ids`), so the art look
is verified before upload and the fallback look with `--uploaded-only`. `Art` calls
`Widgets.Sprite` for anything that is uploaded, so the phone-safe nine-piece
slicing, tiles and `SpriteLoader` pacing stay in one place.

---

## 3. Tokens

### 3.1 Where they live

`src/shared/UI/KitTokens.json` is read by `Kit/Tokens.luau`. It sits beside
HudLayout.json, so Rojo turns it into a ModuleScript and python tools can read it,
which is the repo's convention.

HudLayout.json keeps the world HUD's region rects until that HUD is rebuilt. Its
`lobby` section dies with the old lobby (§9). `src/client/Ui/Theme.luau` keeps its
helpers (`ReducedMotion`, `UsingMouse`, `TopStack`, `Subtitle`, `Option`,
`ColourBlindRarity`). Its dark `Colors`, `Fonts` and `TextSize` are retired once
nothing reads them.

```json
{ "reference": {"width": 1672, "height": 941},
  "colors": { "paper": "#FCDAB1", "...": "..." },
  "fonts": { "display": {"family": "Merriweather", "weight": "Heavy", "fallbackWeight": "Bold"},
             "heading": {"family": "Merriweather", "weight": "Bold"},
             "body": {"family": "Merriweather", "weight": "Regular"},
             "hand": {"family": "PatrickHand", "weight": "Regular"} },
  "text": { "windowTitle": {"font": "display", "size": 46, "color": "ink", "caps": true}, "...": {} },
  "space": {}, "motion": {}, "order": {}, "sounds": {} }
```

### 3.2 Colors

Sampled with PIL as box medians from the mockups and kit sheets.

| Token | Hex | Source |
|---|---|---|
| paper | `#FCDAB1` | window interior (M02, M04 `#FEDEB4`) |
| paperLight | `#FEE2BA` | rows, unselected tabs, keycaps (M06 recipe row, M03 tab) |
| paperDeep | `#FBD4A5` | detail card, search field (M02) |
| paperSelected | `#FED895` | selected recipe or material row (M06) |
| paperDisabled | `#E2CAAE` | disabled parchment button/slot (03, 05) |
| slot | `#FCDBB3` | empty slot (M02), HUD slot `#FBD39E` |
| leather | `#A53A0F` | primary button (M02 EQUIP; 03 normal `#B93F10`) |
| leatherHover | `#C03F0D` | 03 hover |
| leatherPressed | `#7C2B08` | 03 pressed |
| leatherDisabled | `#AA7654` | 03 disabled |
| leatherEdge | `#5D1D06` | button rim (M02) |
| corner | `#8A2E0F` | leather corner pieces (M04) |
| rail | `#290D02` | window outline (M02) |
| ink | `#220A01` | titles, names (M02) |
| inkHeader | `#340C00` | section headers (M04) |
| inkLabel | `#160C05` | row labels (M02) |
| inkBody | `#4E2E12` | descriptions (M06) |
| inkSoft | `#6C4F31` | item description, setting sublabels (M02, M03 `#6E4626`) |
| inkHand | `#522307` | handwritten subtitle (M06) |
| muted | `#A58260` | "Empty Slot", empty dots (M04; circle `#DFB891`) |
| placeholder | `#B4906B` | search placeholder (M02) |
| cream | `#FFFFFE` | text on leather (M02) |
| rule | `#C89868` | thin rules (M06) |
| ruleDark | `#301200` | title underline (M02) |
| divider | `#6B3A14` | footer divider (M03) |
| glow | `#FDAA09` | selected slot or row glow (M02; M06 `#F7A102`) |
| gold | `#FDBC07` | crown, checkbox fill (M03 `#FCBB0F`) |
| leaderTag | `#FDD18A` | Leader plaque (M04) |
| readyFill / readyDot | `#E7E9A2` / `#0CE01A` | Ready pill (M04) |
| badge | `#7B2E0D` | number badge plate (05) |
| xp | `#FCA502` | XP fill (M01; kit yellow `#FDB20F`) |
| track | `#59290B` | XP track (M01; 19 `#663F24`) |
| health | `#FB371C` | 08 |
| stamina | `#5DB702` | 08 (19 green `#73CE0F`) |
| food | `#FC7A04` | 08 (19 orange `#FE6C05`) |
| blue | `#2997FC` | 19 |
| short | `#9B1A12` | not-enough count (M06) |
| toggleOn | `#698010` | 09 |
| veil | `#0A0603` at 0.42 transparency | M01 vs M02 brightness ratio ≈ 0.42 |

Rarity colors stay in `Rarity` / `Theme.ColourBlindRarity`. They are always shown
with the rarity name.

### 3.3 Fonts

The repo uses Merriweather Bold through `HudLayout.fontFaces.serif`, and the capture
ships `art/ui/fonts/Merriweather-{Regular,Bold}.woff`.

| Use | Roblox family | Why |
|---|---|---|
| Window titles (INVENTORY, SETTINGS, PARTY, PLAY, QUEST JOURNAL), big detail titles | Merriweather, weight **Heavy** (900); Bold if the weight is missing | 4× crops show a heavy wedge-serif with Merriweather's letter shapes |
| "ANCESTRAL FORGE" | Merriweather Bold as small caps: `Kit.Text.SmallCaps` uses RichText `<font size>`, 46 for initials and 40 for the rest | M06 small caps (cap heights 35 vs 31) |
| Headers, names, labels, buttons, counts | Merriweather Bold | M02 "Stone Axe", buttons |
| Body and descriptions | Merriweather Regular | M02 description |
| Handwritten subtitle (M06) | **PatrickHand** Regular | upright rounded hand matches "Turn raw materials…" |

### 3.4 Text roles

Sizes are design px. TextSize ≈ cap height / 0.72, measured from the mockups.

| Role | Font | Size | Color | Example (cap px) |
|---|---|---|---|---|
| windowTitle | display, caps | 46 | ink | INVENTORY (33–35) |
| detailTitle | display | 40 | ink | Shattered Crater, Gather Supplies (28–35) |
| subtitleHand | hand | 20 | inkHand | Forge subtitle (14) |
| itemTitle | heading | 28 | ink | Stone Axe (20) |
| buttonL | heading, caps | 40 | cream / ink | PLAY (29) |
| button | heading, caps | 28 | cream / ink | EQUIP, CLOSE (19–21) |
| buttonS | heading | 20 | cream / ink | Invite |
| sectionHeader | heading, caps | 22 | inkHeader | YOUR PARTY, GAMEPLAY (15–17) |
| rowTitle | heading | 20 | inkLabel | Tools, Iron Pickaxe (14) |
| body | body | 16 | inkBody | descriptions (11) |
| bodySoft | body | 16 | inkSoft | setting sublabel |
| muted | body | 16 | muted | Empty Slot (11) |
| value | heading | 18 | ink | +10, 1 / 10, 12 / 20 |
| count | heading | 20 | inkLabel | slot counts (15) |
| hudName | heading | 21 | ink | LiamTheMo (15) |
| hudSmall | heading | 16 | ink | LV. 12, 450/750 XP (11–13) |
| currency | heading | 20 | ink | 2,450 (14) |
| keycap | heading | 17 | ink | W (12) |
| badgeNum | heading | 15 | cream | hotbar 1–6 (11) |

### 3.5 Spacing and radii

All values are design px; specs refine them.

| Token | Value |
|---|---|
| windowPad | 24 (frame to content) |
| colGap | 14 (between insets) |
| sectionHeaderH | 34 (rule 2 px at its foot) |
| rowH | 52 (party rows), 64 (category rows), 72 (recipe and quest rows), 36 (keybind and detail rows) |
| slot | 90 square, pitch 99 (inventory); hotbar 86, pitch 97 |
| tile | 86 square, pitch 102 × 95 (HUD grid) |
| touchMin | 44 screen px |
| fallbackCorner | 8 (plates), 6 (slots), 10 (windows) |

Corners, rims and bevels come from the art; native UICorner and UIStroke are used
only in fallbacks and glow strokes.

---

## 4. Screen plan

Status codes: **New** = a new module; **Rewrite** = the module is rewritten in
place and keeps its public API.

### 4.1 Lobby HUD (01)

| | |
|---|---|
| Module | `Hud/Screens/LobbyHud.luau` (New), replacing `Hud/LobbyHud.luau` and `Hud/LobbyPopups.luau` |
| Controller | `Controllers/LobbyHudController.luau` (rewrite). Keeps the `HudMode.ReplacesLobby()` gate and the fallback to `LobbyController.BuildFallback()` |

| Element | Data source |
|---|---|
| Player card (portrait, name, LV, mini XP) | `player.DisplayName`; `Kit.Portrait(UserId)`; `ProgressionController.View()` + `.Changed` (`ProgressionChanged`); `HudModel.XpFraction`, `HudModel.LevelText`. Press → `ProgressionController.Toggle` |
| Coins / Gems | attributes `Coins`, `Gems` (CurrencyService). Press → `WalletController.Open("Shop")` |
| Settings | `SettingsController.Toggle` |
| Tile grid, 2 × 3 | backpack → `VaultController.Open("Backpack")`; portal → `PlayController.Toggle`; scroll → `JournalController.Toggle`; market → `WalletController.Open("Shop")`; anvil → `ForgeController.Toggle`; trade → `TradeController.Toggle`. Optional Badge "dot" on scroll when a quest is claimable (one `QuestView` on join) |
| Party panel "PARTY n/8" | `LobbyController.PartyView()` + `Changed("party")`; `PartyRules.MAX_SIZE` (8). Rows: portrait, name, crown, ready dot. Add-person button → `PartyController.Open("invite")`. Row press → `PartyController.Open()`. Incoming invites show as rows with ✓/✕ (`PartyAction` accept/decline) |
| XP bar "LV. 12 … 450/750 XP" | progression view |
| Hotbar 1–6 | `PlayModel.LoadoutHotbar(LobbyController.Preview())` = `InventoryRules.FromItems(items).hotbar`. This is the same packing `InventoryService` applies at run start (`LoadoutService.carriedPart`), so it shows exactly what lands in the run's hotbar. Badges read 1–6. A press opens the Inventory |
| Status / maintenance | `Kit.Toast` (info) for `LobbyController.Status()`. A small plaque in `TopStack` while `MaintenanceNotice` is set |
| XP pop-ups | `ProgressionController.MountPopups(host)` beside the tiles |

Removed from the lobby: the ENTER button and the server dropdown (`onServer`). The
"Vault" tile is gone; the Vault is a tab inside Inventory.

### 4.2 Inventory and Vault (02)

| | |
|---|---|
| Module | `Hud/Screens/InventoryWindow.luau` (New), replacing `Hud/InventoryPanel.luau` and `Hud/ItemSlot.luau` |
| Controllers | `VaultController` (lobby: tabs Backpack / Vault); `InventoryController` (world: tabs Backpack / Equipped) |
| Lobby data | `VaultSnapshot` → `{backpack, items, materials, itemCapacity, backpackCapacity, overflow}`; `VaultDeposit(backpackIndex, confirmOverflow?)`, `VaultWithdrawItem(vaultIndex)`, `VaultWithdrawMaterial(catalogId, quantity)`; `ExtractionReceipt` event |
| World data | `InventoryChanged` snapshot `{hotbar, backpack, armor}`; `MoveItem`, `EquipSlot`, `EquipArmor`, `UnequipArmor`, `DropItem`, `UseConsumable`, `PlaceItem`; `Notify` |
| Layout | search, category column, a scrolling 6-wide slot grid (backpack 50, vault `itemCapacity` plus a materials section), detail card, action button |

| Mockup | Game | Decision |
|---|---|---|
| Categories All / Tools / Materials / Food / Plants / Misc | `ItemInfo.CATEGORIES` = All / Tools / Materials / Food | All / Tools / Materials / Food / **Misc**. Misc = items with no category today (armour, ammo, siege, placeables), derived in `ItemInfo.Category`. **Plants is dropped**: there is no plant family; herbs and fiber are Materials |
| Description text | ItemCatalog has no descriptions | Show rarity name + family + "Permanent — kept on death" / "At risk — drops on death" (GDD §25.4). A description line appears only if the owner adds catalog text (open question) |
| Harvest Power / Attack Speed / Durability | `ItemInfo.Stats` chips: weapon damage, weapon cooldown, tool tier and kind, armour %, healing, food, boost, quantity | New `ItemInfo.StatRows(item)` → `{icon, label, value}`: Damage, **Attack Speed (real weapon cooldown)**, Tool Tier, Armour, Heals, Food, Boost, Quantity. **No Durability**: GDD says nothing wears or breaks |
| EQUIP | Lobby has no equipping | Lobby: STORE IN VAULT (backpack tab), TAKE (vault tab; materials get a Stepper with All), STORE ALL in the tab bar. World: EQUIP (to hotbar / wear), USE, DROP (secondary) |
| Vault tab | yes | The tab label carries the capacity "Vault 23/25". When full, a link to Shop → Offers |

The extraction receipt shows as Toast "ITEMS RECEIVED", which opens a ConfirmDialog-style
card listing the receipt.

### 4.3 Settings (03)

| | |
|---|---|
| Module | `Hud/Screens/SettingsWindow.luau` (New), replacing `Hud/SettingsPanel.luau` |
| Controller | `SettingsController` (draft, APPLY/RESET, rebinding, UI-scale and palette application). The world gear button `FlintbornSettingsButton` becomes a Kit IconButton |
| Data | `SettingsRules.Settings`; `Keybinds.Actions` / `Binds`; remotes `SaveSettings`, `SaveKeybinds`, `TutorialAction("Replay")` |

| Mockup | Game | Decision |
|---|---|---|
| 4 tabs (Gameplay, Audio, Graphics, Controls) | 5 tabs, incl. Accessibility | **Recommend 4 tabs (1:1).** Graphics gets UI Scale, Colour-blind palette and Reduced Motion; Audio gets Subtitles. Alternative: a 5th large tab, at the cost of a tighter tab pitch and dropping the plant ornament |
| Gameplay: Camera Sensitivity, FOV, Interaction Range, Auto Loot, Show Item Notifications, Language | Camera Sensitivity, Invert Camera, Show Damage, Show Names | Show the real ones in the mockup's controls. Slider: Camera Sensitivity 10–100. Checkboxes with descriptions: Show Damage Numbers, Show Names, Invert Camera. **FOV, Interaction Range, Auto Loot, Item Notifications and Language are not shown** (no source; Roblox owns language) |
| Key Binds: W/S/A/D/Space/E/B/M/Shift/Ctrl | 17 rebindable actions (Interact E, Backpack B, Map M, Sprint LeftShift, …; no crouch since GDD 1.24); movement keys are Roblox's and not rebindable | Gameplay's right column lists the first 10 rebindable actions with live keys. Controls lists all of them (Scroll) plus Replay Tutorial and the "gamepad buttons are fixed" note |
| RESET / APPLY | same semantics (`SetDirty`) | keep |

### 4.4 Party (04)

| | |
|---|---|
| Module | `Hud/Screens/PartyWindow.luau` (New) |
| Controller | `Controllers/PartyController.luau` (New): `Open(section?)`, `Toggle()`, `IsOpen()` |
| Data | `LobbyController.PartyView()` (with the §5 fields), `LobbyController.Invitable()`, each player's `Level` attribute (set by `ProgressionService.Publish`, already replicated), `LobbyController.PartyAction("invite"\|"accept"\|"decline"\|"leave"\|"ready", arg)`, `SocialService:PromptGameInvite` |

| Column | Content |
|---|---|
| YOUR PARTY n/8 | 8 rows: members (PlayerRow with Leader badge and crown) and "Empty Slot" rows. The mockup shows 7 rows at its pitch; the spec fits 8 by tightening the pitch to about 46 or scrolling |
| INVITE PLAYERS | SearchBox (DisplayName or Name contains the query); Invitable list (portrait, name, LV, Invite button). The button reads "Invited" and is disabled while `party.invited` holds that player. Non-leaders see "Only the party leader can invite". An "Invitations" block lists incoming invites with Accept/Decline. Footer: "Invite Roblox friends" (secondary) |
| PARTY DETAILS | Party Leader; Members n / 8; Join Type "Invite Only" (true: joining is only by invite); Created (relative time from `createdAt` via `workspace:GetServerTimeNow()`: "Just now", "5 min ago", "2 h ago"). **No Play Style row** |
| READIED STATUS | One row per member with Ready / Not ready badge. Your own badge is a toggle (`PartyAction("ready", bool)`). Solo players can be Ready too |
| Footer | CLOSE (as in the mockup), plus LEAVE PARTY (secondary) when in a party of 2 or more. **No kick**: the game has no kick |

### 4.5 Play (05)

| | |
|---|---|
| Module | `Hud/Screens/PlayWindow.luau` (New), replacing the ENTER button, the server dropdown and the `LobbyPopups` deploy check |
| Controller | `Controllers/PlayController.luau` (New): `Open()`, `Toggle()`, `IsOpen()`; owns the deploy check |
| Data | `LobbyController.Preview()` / `FetchPreview()` (`DeployPreview`), `LobbyController.Deploy()` (`Deploy`), `IsDeploying()`, `Status()`, `PartyView()`, `Level` attributes, `SessionState` |

| Mockup element | Decision |
|---|---|
| Island painting | The real painted island (`pm_map_island` via `IslandMap` in a static, non-zoom mode, or `Kit.Icon`-style image) in the play-map frame. **No X mark**: spawns are random (GDD §3.1) |
| Title "Shattered Crater" | True: it is the world's name (GDD §3) |
| Region / Biome / Difficulty / Recommended Level 10+ | **Recommended level has no source.** Proposed honest rows (owner to confirm): Regions "Outer Rim · Inner Ring · Center Crater"; Spawn "Random, away from other players"; Mode "PvPvE extraction"; **Carrying "N items · M at risk"** (from the preview). Icons from sheet 17 |
| YOUR PARTY | Rows: crown, portrait, name, LV n, ready dot |
| YOUR EQUIPMENT 1–6 | `PlayModel.LoadoutHotbar(preview)`, the predicted run hotbar, plus "+N more in backpack" |
| PLAY | Leader: PLAY → `FetchPreview()`. An empty list deploys at once. Otherwise **ConfirmDialog "TAKE THESE INTO THE RUN?"** (restyled deploy check) lists every item (★ Permanent, ×qty), "Everything except ★ Permanent items can be lost in the run." and "Items in your vault always stay safe.", with ENTER / CANCEL. When the preview is nil: "COULD NOT READ YOUR BACKPACK" with ENTER ANYWAY. When not every member is ready, the dialog adds "k of n party members are ready" (advisory; see open questions). The button is busy while `IsDeploying()` |
| (non-leader) | The big button becomes the Ready toggle (leather "READY" / parchment "NOT READY") with the caption "The party leader starts the run" (the server refuses with `OnlyLeaderDeploys`) |

There is no server selection anywhere.

### 4.6 Ancestral Forge (06) and field Crafting

| | |
|---|---|
| Module | `Hud/Screens/RecipeWindow.luau` (New), with modes `"forge"` and `"crafting"`; replaces `Hud/CraftingPanel.luau` |
| Controllers | `ForgeController` (lobby), `CraftingController` (world) |
| Forge data | `ForgeSnapshot` → recipes `{id, kind, category, name, output, quantity, unlocked, requirement, inputs{catalogId, name, owned, needed}, tier, family, sources}`; `ForgeCraft(recipeId, sourceInstanceId?, nonce)` |
| Crafting data | recipe catalogs in `Shared.Crafting`, `InventoryController.Count`, nearby stations, `Smelt*` attributes, `Craft(requestId, recipeId, count?)` |

| Mockup | Decision |
|---|---|
| Title and handwritten subtitle | UI copy, not data: keep |
| RECIPES list | ListRow: icon, name, subtitle. The subtitle is derived (`ItemInfo.StatRows`, e.g. "Pickaxe · Tier 3"), or the unlock requirement when locked (locked state). A **category Dropdown** (All / Tools / Weapons / Armor / Supplies / Permanent) sits in the header row: the mockup shows no categories, but the game has them |
| Centre description | No descriptions exist: show the derived stat rows instead |
| REQUIRES cards | `inputs`: icon, name, owned / needed. Owned is in `short` red when below needed |
| QUANTITY − 1 + | **Forge: hidden** (`ForgeCraft` has no count). Crafting: shown for smelts (`Craft` takes a count), with "Craft all" |
| FORGE button | Disabled with a Tooltip reason: locked, short, or busy. A Permanent conversion picks the source and asks through ConfirmDialog, naming the exact item and the Permanent rules (GDD §25.3) |
| YOUR MATERIALS | Distinct `inputs` with owned > 0 (vault-only counts, GDD §25.3). Rows the selected recipe needs are `selected` |
| Crafting extras | stations line; job progress (`Kit.Bar` orange) with STOP |

### 4.7 Quest Journal (07)

| | |
|---|---|
| Module | `Hud/Screens/JournalWindow.luau` (New), replacing `Hud/JournalPanel.luau`; `Hud/IslandMap.luau` is restyled |
| Controller | `JournalController` |
| Data | `QuestView` → `{id, name, tier, coins, gems, booster, count, needed, claimed, repeats, action}`; `QuestClaim(questId)` |

| Mockup | Decision |
|---|---|
| Side tabs book / trophy / map / party | book = all quests (Daily first, rows tagged "Daily"); trophy = one-time quests (`repeats == "Once"`); map = island map page (`IslandMap`). **The party tab is hidden** (no source) |
| Row icon and line | Icon by `action` (Gather → log, Extract → portal, Craft → hammer, Hunt → paw, Caches → chest, Boss → tusk; sheets 11, 16, 17). The objective line is derived from the action, as `JournalPanel` does today |
| Several objectives | One objective per quest: one row, count / needed, circle → check |
| Item rewards | Rewards are Coins, Gems and Booster only: tiles for those |
| CLAIM | Enabled when count ≥ needed and not claimed; "CLAIMED" after |
| QUEST PROGRESS | finished or claimed / total in the open tab, shown as "1 / 5 Completed" |

### 4.8 Restyled screens (no mockup; same kit)

| Screen | Module | Controller / data | Kit usage |
|---|---|---|---|
| Market (Shop / Sell / Offers / Codes) | `Hud/ListWindow.luau` (Rewrite on Kit, same API: `Begin`, `Section`, `Line`, `Row`, `Buttons`, `Input`, `Pair`, `Confirm`, …) | `WalletController`: `ShopView`, `ShopBuy`, `MerchantSell`, `VaultUpgrade`, `PerkRespec`, `RedeemCode` | Window, large tabs, ListRow, Button, SearchBox, ConfirmDialog |
| Trade | ListWindow | `TradeController`: `TradeRequest`, `TradeRespond`, `TradeOffer`, `TradeLock`, `TradeConfirm`, `TradeCancel`, `TradeChanged`, `VaultSnapshot` | Slot, PlayerRow, Stepper, Toast for invites |
| Progress (levels, masteries, titles, rebirth, perks) and XP pop-ups | ListWindow; pop-ups as small toasts | `ProgressionController`: `ProgressionSnapshot`, `ProgressionChanged`, `XpGained`, `RebirthPreview`, `Rebirth`, `BuyPerk` | Bar, ListRow, ConfirmDialog with `holdSeconds` |
| World map | `MapController` on `Kit.Screen` / Window; `IslandMap` | `EventAnnounced`, `EventEnded`, `PortalKind`, `SafeName` | Window, IconButton zoom ±, map frame (15) |
| Field crafting | RecipeWindow, crafting mode | §4.6 | |
| In-world HUD | `HudController` + `Hud/Vitals`, `BottomBar`, `PartyFrames`, `Compass`, `ObjectivePanel`, `EventPanel`, `InteractionPrompt`, `DamageNumbers` (Rewrite) | Humanoid health, `Stamina`, `Food`, `MedicineLockUntil`, `FoodHealing`; inventory snapshot; events | Bar with frame "stat" (08, 20), Slot with hotkey badge (`Binds.Label("HotbarN")`), PlayerRow mini, Panel plaques, KeyCap in prompts |
| World tiles | `NavController` | — | IconButton tile |
| Notices and toasts | `Hud/NoticeCard.luau` (Rewrite onto Kit card + Toast), `NoticeController` (`Notice`), trade and party invites | — | Toast, ConfirmDialog |
| World menu (protected arrival) | `WorldMenuController` (`RequestPlay`, `ReturnToLobby`) | — | Window, Button play, Toast |
| Overlays | `BoostHud`, `BossUi` (`BossAlert`), `Downed`, `Extraction`, `EventFeed`, `Tutorial`, `SaveStatus`, `Loot` (`CorpseOpened`/`CorpseTake`/`DeathSummary`), `Storage` (`ChestOpened`/`ChestTake`/`ChestPut`), `Tribe` (`TribeAction`/`TribeChanged`), `Build` palette | — | Panel plaques in TopStack, Bar, Slot grids, Window, Button |
| Deploy check | PlayController ConfirmDialog | §4.5 | |
| `LobbyController.BuildFallback` | unchanged plain fallback | — | It must not depend on Kit: it is the fallback if Kit fails |

### 4.9 Cross-screen contracts

These controller functions must exist; the owner of each controller provides them.

| Controller | Functions | Status |
|---|---|---|
| VaultController | `Toggle()`, `Open(tab?)`, `IsOpen()`, `Changed` (backpack or vault changed → HUD and Play refresh the preview) | `Open` and `Changed` are new |
| PartyController | `Open(section?)`, `Toggle()`, `IsOpen()` | new |
| PlayController | `Open()`, `Toggle()`, `IsOpen()` | new |
| JournalController | `Toggle()`, `Open(tab?)` | `Open` is new |
| ForgeController, TradeController, SettingsController, ProgressionController | `Toggle()` | existing |
| WalletController | `Open(tab)` | existing |
| LobbyController | `PartyView()`, `Invitable()`, `PartyAction()`, `SetReady(bool)`, `IsReady(userId)`, `Deploy()`, `IsDeploying()`, `Preview()`, `RefreshPreview()`, `FetchPreview()`, `Status()`, `Changed` | `SetReady` and `IsReady` are new |

---

## 5. Server work

There is no new remote. Everything rides the existing guarded `PartyAction` /
`PartyChanged` pair: `Remotes.Handle` rate bucket + `RemoteGuard` argument check +
`PartyService.REQUEST_COOLDOWN_SECONDS = 0.25`.

| Change | File | Details |
|---|---|---|
| Ready state | `src/shared/Admission/PartyRules.luau` | `State.ready: {[userId]: true}`, kept apart from parties so solo players can be ready **without creating a party** (a party of one would write a deploy record and start a tribe). `PartyRules.SetReady(state, userId, ready: boolean)` returns `(ok, reason)`; `PartyRules.IsReady(state, userId)`; `PartyRules.ClearReady(state, userIds)` |
| Reset rules | PartyRules | Ready clears for **every member of both parties** on `Accept`, `Leave` and `Forget` (any membership change), on the player's deploy (`DeployService`, at the start of a deploy, for the whole group), and on `PlayerRemoving`. It does **not** clear on `Invite` or `Decline` |
| createdAt | PartyRules | `Ensure(state, userId, partyId, now)` stores `createdAt = now` (`os.time()` passed by the service; the module stays pure) |
| Pending outgoing invites | PartyService `viewFor` | `party.invited = {userId…}` from `party.invites`, so Invite buttons can show "Invited" honestly |
| Action `ready` | `src/server/Services/PartyService.luau` `handle` | `action == "ready" and type(argument) == "boolean"` → `SetReady`; then `broadcast()`. Other argument types return `BadRequest`. The existing cooldown covers spam |
| View fields | PartyService `viewFor` | `members[i].ready`, `party.createdAt`, `party.invited`, top-level `view.ready` (self, for solo) |
| Deploy clears | `src/server/Services/DeployService.luau` | Call `PartyService.ClearReady(group)` when a deploy starts |
| Lobby list with levels | none | Clients read `Player:GetAttribute("Level")` (set in every place by `ProgressionService.Publish`) and listen for changes |
| HudMode gate | `src/client/Hud/HudMode.luau` | `ReplacesLobby()` = `PlaceConfig.IsLobby() and not lobbyFailed` (no longer tied to `HudLayout.lobby`) |
| Client wrapper | `src/client/Controllers/LobbyController.luau` | `SetReady(bool)`, `IsReady(userId)`; pass the new view fields through |
| Remotes doc | `src/shared/Net/Remotes.luau` | Comment only: `PartyAction` now includes `"ready"` |
| Specs | `tests/luau/party_ready.spec.luau` (new), `tests/luau/followup_party.spec.luau` | set and clear, reset on accept/leave/forget, createdAt, invited list |

Not proposed (open questions): server-enforced "all ready" before Deploy, a
`ForgeCraft` count, ItemCatalog descriptions.

---

## 6. Atlas plan

Every atlas is at most 1024 × 1024 with GAP 4 (`art/ui/pack_atlas.py` GROUPS, owned
by the asset artist). Rules:
- State variants of one role share size and slice and sit in the same atlas.
- Sprites keep their own PNGs as the per-sprite fallback.
- The first lobby screen needs **one** atlas (two with item icons in the hotbar).
  `SpriteLoader` prefetches the rest after what is on screen.

| Atlas | Roles | When needed |
|---|---|---|
| `atlas_lk_lobby` | player card, portrait frame, mini XP track and fill, leaf ornament, coin pill, gem pill, settings button, HUD tile plate (one sprite, used 6 times), 6 menu icons (backpack, portal, scroll, market, anvil, trade), party panel frame, crown, add-friend button, empty-slot dot, thin scrollbar, long XP track and fill, hotbar slot, number badges 1–6 | lobby join |
| `atlas_lk_window` | window frame (plain + clasped), corner pieces, header rule, close ×4, leather button ×4, parchment button ×4, small parchment ×3, play plaque, inset panel, detail card, section rule, ornate divider, list row ×3 + selected, category tab ×2 (arrow), horizontal tab leather/paper, large tab leather/paper, side tab ×2 | first window opened |
| `atlas_lk_controls` | scrollbar track/thumb, search box, dropdown field + arrow, checkbox off/on, toggle off/on, slider track/fill/knob, value box, stepper ±, keycap ×states, tooltip boxes with tails, Leader plaque, Ready pill, count tag, status dots, lock, check, cross, warning, confirm dialog frame (if distinct), toast banner plates | first window opened (split from `atlas_lk_window` only if that overflows) |
| `atlas_lk_slots` | slot ×5 states + lock, count plaque, bar track and 5 fills, stat bar frame and icon plates (health, stamina, food, XP), value plaque, reward tile, check tile | inventory, forge, play, journal, world HUD |
| `atlas_lk_icons` | sheet 11 (20 menu and section icons), sheet 16 status icons, section-header glyphs (party, search, info, check), toast emblems, at 64–96 px | windows |
| `atlas_lk_items` | item icons from sheets 02, 10, 12, 16 (only where the art truly depicts that catalog item: `lk_item_<CatalogId>`), at 96 px; sheet 17 world icons for quest and Play art at 96–128 px | inventory, forge, journal, hotbar |
| `atlas_lk_hud_world` | world-only parts: compass plaque, prompt frame, objective and event panels, boss and downed bar frames (anything not already in `atlas_lk_slots`) | run start |
| `atlas_island` (existing) | `pm_map_island` painting, reused by Play, Journal and Map | Play, Journal, Map |

Old `atlas_lobby`, `atlas_hud`, `atlas_ui`, `atlas_pieces`, `atlas_map` and
`atlas_window_*` stay until §9.

---

## 7. Capture scenes

Run with `python3 art/ui/capture/capture.py <scene>`. Each scene builds the real
screen module at 1672 × 941 with mockup sample data (LiamTheMo, LV 12, 450/750 XP,
2,450 Coins, 125 Gems, party 1/8). It places the window where the mockup has it and
calls `__dump`, once per state page.

| Scene | Owner | Pages |
|---|---|---|
| `kit_gallery.luau` | Kit builder | one page per family: buttons and icon buttons × every state; tabs; slots (all states, counts, badges, lock); bars (every fill at 0/50/100, stat frames); controls (checkbox, toggle, slider, dropdown open, search, stepper, keycaps); rows, player rows, badges, pills; toast, dialog, tooltip; window header variants; plus a fallback page (`--uploaded-only`) |
| `lobby_hud`, `lobby_hud_phone` (844 × 390), `lobby_hud_wide` (2560 × 1080) | S1 | invites present; maintenance |
| `inventory_backpack`, `inventory_vault`, `inventory_world`, `inventory_flow` | S2 | each category; selected item; material stepper; full vault |
| `settings` (each tab), `settings_flow` | S3 | dirty state; capturing key |
| `party`, `party_invites`, `party_member` (non-leader) | S4 | ready / not ready; Invited |
| `play`, `play_deploy_check`, `play_member` | S5 | busy; nil preview |
| `forge`, `forge_permanent`, `crafting`, `crafting_flow` | S6 | locked; short; job running |
| `journal`, `journal_map`, `journal_flow` | S7 | claimable; claimed |
| `world_hud`, `world_hud_phone` | W1 | low health; selected slot |
| `notices`, `world_overlays`, `world_menu` | W2 | |
| `market_flow`, `trade_flow`, `progress_flow`, `map_flow` | W3 | |

**Forcing states:**
- `component.root:SetAttribute("DebugState", "pressed")` before `__dump`.
- `Kit.Debug.Each` finds parts by `KitRole`.
- Flows fire real events: `button.Activated:Fire()`, `MouseEnter:Fire()` (the env's
  signals are fireable).
- Remotes are mocked by creating `FlintbornRemotes` children with handlers, as
  `vault_flow.luau` does.
- Tweens finish at once, so the end state is captured.

**Headless environment limits** (from `gui_env.luau` and `render.py`):

| Supported | Not supported, and what to do |
|---|---|
| UDim2, AnchorPoint, UIScale, UIPadding, UIListLayout, UIGridLayout, AutomaticSize, UISizeConstraint, UIAspectRatioConstraint, ScrollingFrame canvas and native scrollbar, ClipsDescendants, sibling ZIndex, Frame fill + UICorner + UIStroke + UIGradient, ImageLabel Stretch/Fit/Crop/Slice + ImageRect + ImageColor3, TextLabel FontFace/TextScaled/TextCap/wrap/truncate/stroke, `rbxthumb` placeholder head, attributes, fireable signals | **Absolute\* are zero and TextBounds is zero.** No layout runs in Luau, so Kit must place things from its own design numbers, never from `AbsoluteSize` (use `TextService:GetTextSize`, which the env implements). **RichText tags are stripped**, so a SmallCaps label draws at one size: the kit builder extends `render.py` to honour `<font size>`. **Rotation is ignored**, so avoid rotated art. **UIGradient on images is ignored** (frames only). **CanvasGroup group transparency is ignored**, so do not use CanvasGroup for looks. **BlurEffect and Lighting are not drawn**, so blur is verified in game. **Fonts:** only Merriweather Regular and Bold ship; the kit builder adds Merriweather Black/Heavy and PatrickHand (both OFL) to `art/ui/fonts` and `FONT_FILES`. Device safe areas, real touch and DPI remain manual checks |

The kit builder also adds `capture.py --compare <mockup.png>`, which writes a
side-by-side and a 50 % overlay next to the capture for verifiers.

---

## 8. File ownership

One owner per file. Ask the owner for a change; never edit another agent's file.

| Agent | Owns (create, edit, delete) |
|---|---|
| **Asset artist** (already running) | `art/ui/sprites/lk_*.png`, `art/ui/kit/**` (CATALOG.md and the slicing script), `art/ui/sprites/manifest.json`, `art/ui/pack_atlas.py`, `src/shared/UI/UiSprites.json` (via `roblox_upload_ui_assets.py --sprites`) |
| **Kit builder** | `src/client/Hud/Kit/**`, `src/shared/UI/KitTokens.json`, `src/client/Hud/Widgets.luau`, `src/client/Hud/SpriteLoader.luau`, `src/client/Hud/Parchment.luau` (deletes it at the end), `src/shared/UI/HudModel.luau` + `tests/luau/hud_model.spec.luau`, `tests/luau/kit_*.spec.luau`, `art/ui/capture/capture.py`, `render.py`, `gui_env.luau`, `scenes/kit_gallery.luau`, `art/ui/fonts/**` |
| **S1 Lobby HUD** | `Hud/Screens/LobbyHud.luau`, `Controllers/LobbyHudController.luau`, deletes `Hud/LobbyHud.luau` and `Hud/LobbyPopups.luau`, `art/ui/preview_lobby.py`, scenes `lobby_hud*` (deletes `lobby.luau`, `lobby_phone.luau`) |
| **S2 Inventory** | `Hud/Screens/InventoryWindow.luau`, `Controllers/VaultController.luau`, `Controllers/InventoryController.luau`, `src/shared/Items/ItemInfo.luau` + `tests/luau/item_info.spec.luau`, deletes `Hud/InventoryPanel.luau` and `Hud/ItemSlot.luau`, scenes `inventory_*` (deletes `inventory.luau`, `inventory_flow.luau`, `vault_flow.luau` or replaces them) |
| **S3 Settings** | `Hud/Screens/SettingsWindow.luau`, `Controllers/SettingsController.luau`, deletes `Hud/SettingsPanel.luau`, scenes `settings*` |
| **S4 Party** | `Hud/Screens/PartyWindow.luau`, `Controllers/PartyController.luau`, `src/shared/UI/PartyModel.luau` (relative time, ready counts) + spec, scenes `party*` |
| **S5 Play** | `Hud/Screens/PlayWindow.luau`, `Controllers/PlayController.luau`, `src/shared/UI/PlayModel.luau` (`LoadoutHotbar`, carrying summary) + spec, scenes `play*` |
| **S6 Forge/Crafting** | `Hud/Screens/RecipeWindow.luau`, `Controllers/ForgeController.luau`, `Controllers/CraftingController.luau`, deletes `Hud/CraftingPanel.luau`, scenes `forge*`, `crafting*` |
| **S7 Journal** | `Hud/Screens/JournalWindow.luau`, `Controllers/JournalController.luau`, `Hud/IslandMap.luau`, deletes `Hud/JournalPanel.luau`, scenes `journal*` |
| **W1 World HUD** | `Controllers/HudController.luau`, `NavController.luau`, `SurvivalHudController.luau`, `CombatController.luau` (touch buttons), `Hud/Vitals`, `BottomBar`, `PartyFrames`, `Compass`, `ObjectivePanel`, `EventPanel`, `InteractionPrompt`, `DamageNumbers`, `Hud/Layout.luau`, `src/shared/UI/HudLayout.json`, `art/ui/preview_hud.py`, scenes `hud.luau`, `world_hud*` |
| **W2 World overlays and notices** | `Controllers/BoostHudController`, `BossUiController`, `DownedController`, `ExtractionController`, `EventFeedController`, `TutorialController`, `SaveStatusController`, `LootController`, `StorageController`, `TribeController`, `BuildController`, `WorldMenuController`, `NoticeController`, `Hud/NoticeCard.luau`, `src/client/Ui/Theme.luau`, scenes `notices`, `world_overlays`, `world_menu` |
| **W3 Lists and map** | `Hud/ListWindow.luau`, `Controllers/WalletController`, `TradeController`, `ProgressionController`, `MapController`, scenes `market_flow`, `trade_flow`, `progress_flow`, `map_flow` |
| **I1 Integration / server** | `src/shared/Net/Remotes.luau`, `src/shared/Admission/PartyRules.luau`, `src/server/Services/PartyService.luau`, `DeployService.luau`, `Controllers/LobbyController.luau`, `Hud/HudMode.luau`, `tests/luau/party_ready.spec.luau`, `tests/luau/followup_party.spec.luau` |
| **Reference analysts** | `docs/ui/<Screen>.md` specs (replacing the old ones) |
| **Architect** | `docs/ui/ARCHITECTURE.md` |
| **Orchestrator / owner** | `GDD.md` (decision log for Ready, Play and Vault-as-tab), `docs/ui/UI_PROGRESS.md`, `src/shared/UI/UiAssetIds.json` and `art/ui/uploaded_decals.json` (written only by the manual upload workflow), git |

Read-only for everyone except the owner: `src/shared/Items/ItemCatalog.luau`,
`src/shared/Inventory/InventoryRules.luau` and every other gameplay module.
`ItemInfo.StatRows` (S2) is the one stats source that S6 consumes; S2 lands it first.

---

## 9. Removal plan

Remove only after the new screens are live **and** their `lk_` art is uploaded and
seen working in game.

| Remove | When |
|---|---|
| `Hud/LobbyHud.luau`, `Hud/LobbyPopups.luau`, HudLayout.json `lobby` section, `art/ui/preview_lobby.py` | S1 done |
| `Hud/InventoryPanel.luau`, `Hud/ItemSlot.luau` | S2 done |
| `Hud/SettingsPanel.luau` | S3 done |
| `Hud/CraftingPanel.luau` | S6 done |
| `Hud/JournalPanel.luau` | S7 done |
| `Hud/Parchment.luau` (`TopInset` moved to `Kit.Scale`) | no `require` left |
| In `Widgets.luau`: `PARCHMENT_GLYPHS`, `PARCHMENT_LABELS`, `LEATHER`, `PARCHMENT_BADGES`, `parchmentFallback`, the old `GLYPHS`/`FILL_COLORS` fallbacks | no `pm_` or legacy sprite names left in `src/` |
| `Theme.Colors`, `Theme.Fonts`, `Theme.TextSize` | W2 done and `grep` clean |
| `art/ui/sprites/pm_*.png` (123), legacy unprefixed sprites (`button_*`, `frame_*`, `icon_*`, `fill_*`, `compass_marker`, …), `atlas_lobby`, `atlas_hud`, `atlas_ui`, `atlas_pieces`, `atlas_map`, `atlas_window_*`, `_parchment_contact.png`, `_slice_test.png`, and their `manifest.json`, `UiSprites.json` and `UiAssetIds.json` entries | a sprite is deletable when no string in `src/` references it and no GROUP lists it. Keep `pm_map_island` and `atlas_island` |
| `art/ui/slice_parchment.py`, `art/ui/slice_ui.py`, `art/ui/preview_hud.py` | their outputs are gone |
| Old capture scenes (`lobby`, `lobby_phone`, `inventory`, `inventory_flow`, `vault_flow`, `settings`, `settings_flow`, `journal`, `journal_flow`, `crafting`, `crafting_flow`, `forge_flow`, `hud`) | replaced by the new scenes of the same owner |
| Old specs `docs/ui/{Lobby,Hud,Inventory,Settings,Journal,Crafting}Screen.md`, `ListWindows.md` | replaced by the analysts |

Uploaded decals stay on Roblox; that is harmless.

---

## 10. Ordered build plan

| Step | Who | Work | Gate |
|---|---|---|---|
| 0 | analysts, asset artist (in parallel, now) | specs for the 7 screens; `lk_*` slices + CATALOG.md | — |
| 1 | Kit builder | KitTokens.json; Kit core (Tokens, Art + roles + fallbacks, Interact + DebugState, Motion, Sound, Scale, Modal, Screen, Window, Text); capture upgrades (fonts, `--compare`, `<font size>`); `kit_gallery` page 1 | gallery renders; Window matches M02 frame and header |
| 1′ | I1 (in parallel with 1) | Party Ready, createdAt, invited; DeployService clear; LobbyController API; HudMode gate; specs | `tests/luau/run.py` green |
| 2 | Kit builder | every component in §2.5, every state in the gallery | independent verifier compares the gallery with sheets 01–20 |
| 3 | S1–S7 (parallel) | static screen from spec + sample-data scene → verify against the mockup → wire controller → flow scene. S2 lands `ItemInfo.StatRows` first. S1 wires the Play and Party tiles once S4 and S5 export `Open`/`Toggle` (stub calls until then) | per-screen verifier: capture vs mockup at 1672 × 941, all states, phone 844 × 390 |
| 4 | W1–W3 (parallel, may start with step 3) | restyle in-world HUD, overlays and notices, list windows and map | same kit, gallery parity |
| 5 | asset artist | final GROUPS (§6), `pack_atlas.py`, `UiSprites.json` sync; hand the upload list to the owner | the owner runs `scripts/roblox_upload_ui_assets.py --upload` |
| 6 | integration pass (I1 + orchestrator) | one-window rule, Escape/B, gamepad order, ready flow end-to-end, open/close ×20 leak check in a scene (descendant counts), phone and wide captures, `--uploaded-only` fallback captures | reviewer sign-off |
| 7 | each owner | removal (§9) | `grep` proves nothing references removed files or sprites |
| 8 | orchestrator | UI_PROGRESS.md, GDD decision log | — |

---

## 11. Open questions for the owner

1. **Settings tabs:** merge Accessibility into Graphics and Audio (4 tabs, 1:1), or a 5th tab?
2. **Mockup-only settings** (FOV, Interaction Range, Auto Loot, Item Notifications, Language): omit (proposed), or build them as real features, as GDD §57 did for the last mockup?
3. **Play info rows:** there is no "Recommended level" or difficulty data. Are the proposed honest rows (Regions, Spawn, Mode, Carrying) acceptable?
4. **Ready:** advisory (proposed: the leader's Play dialog says "k of n ready"), or should the server refuse Deploy until everyone is ready?
5. **Item descriptions:** add authored text to ItemCatalog (content work), or keep the derived lines?
6. **Forge quantity:** keep hidden, or add a count to `ForgeCraft` server-side?
7. **Journal party tab:** hidden (proposed). Is there a party-quest feature planned?
8. **Inventory categories:** drop "Plants" and add "Misc" as proposed?
9. **Party list:** 8 rows (cap 8) where the mockup shows 7. Is a tighter pitch acceptable, or scroll?
10. **Heading weight:** confirm Merriweather Heavy renders on device (fallback Bold).
11. **UI sound ids:** none exist yet. Supply them, or stay silent?
12. **Background blur behind windows:** on for Medium and High graphics (proposed)?

---

## 12. Decisions (resolved; these override anything above)

Owner answers and reconciled measurements. Where this section disagrees with an
earlier section or a screen spec, this section wins.

| # | Topic | Decision |
|---|---|---|
| D1 | Settings tabs | 4 tabs (Gameplay, Audio, Graphics, Controls) as in the mockup. Accessibility settings move into Graphics and Audio, using the same row styles. |
| D2 | Mockup-only settings | Omitted: Field of View, Interaction Range, Auto Loot, Show Item Notifications, Language. Only settings that already work are shown. |
| D3 | Ready | Advisory. The leader can always press Play; the Play confirm says "k of n ready". Ready is lobby-only and server-tracked (§5). |
| D4 | Forge quantity | Kept. `ForgeCraft` gains a server-validated count (1..`ForgeRules.MAX_BATCH`, default 10, also capped by what the materials allow); materials are checked and spent for all N atomically. Owner: I1 (`ForgeService.luau`, `ForgeRules.luau`, `Remotes.luau` + spec). |
| D5 | Party size | Real cap 8 ("1/8"). The list shows 7 rows at the mockup pitch and scrolls for the 8th. |
| D6 | Party details | No "Play Style" row. Join Type reads "Invite Only". Created uses `createdAt`. |
| D7 | Play window | No server selection anywhere. Rows show only real data (region, biome from BiomeCatalog if it has one, and honest derived rows); no invented difficulty or recommended level. |
| D8 | Dim overlay | Measured by three analysts: near-black at about 68 % opacity. Veil color `#050403`, `BackgroundTransparency 0.30` (fits 0.29–0.32 across all seven mockups; replaces 0.42 in §1.3). The HUD behind a window stays where it is in 01_hud; the shifted hotbar in the window mockups is ignored. |
| D9 | Blur | On for Medium and High graphics, Size 8; never in captures. |
| D10 | Item descriptions | Short authored descriptions live in the UI layer (`ItemInfo`, owned by S2), not in gameplay modules; items without one show their derived line. |
| D11 | Inventory categories | All, Tools, Materials, Food, Plants (only if `ItemInfo` can classify plant items reliably from catalog data, otherwise dropped), Misc. |
| D12 | Journal side tabs | Book = quests; trophy = progression (the Progress content, read-only view); map pin = the island map; party = opens the Party window. |
| D13 | Fonts | Merriweather Heavy for titles (Bold fallback), Merriweather Bold for labels and headings, Merriweather Regular for row labels and descriptions; Patrick Hand for the Forge subtitle and other handwritten notes. Forge title uses fake small caps via size steps. |
| D14 | UI sounds | Silent unless the repo already has UI sound ids; the Kit keeps the hook. |
| D15 | Unity | Every screen, including the restyled ones, is built only from Kit components and `lk_` art. No screen draws its own frame, button, slot, bar or tab. |
| D16 | Who presses Play | Anyone may press Play solo; in a party only the leader deploys, and Ready never blocks it (D3). Specs that say "all members ready" are overridden. |
| D17 | Opening the Party window | The HUD party panel's title row and its add-player button, and the Journal party tab. |
| D18 | Ready controls | Each member's row shows a Ready tag (green dot, "Ready") or a Not Ready tag (grey dot, "Not Ready"). The local player toggles it with a Ready / Not Ready button in the Readied Status card. Invite buttons show "Invited" (disabled paper) while an invite is pending. |
| D19 | Missing art | Where a mockup shows art the kit lacks (Party header tent and trees, Settings sketches, flat glyphs), use the closest `lk_` art (e.g. `icon_tree`, `icon_campfire`, emblems) and list it as a deviation; never draw ad-hoc shapes. The Play window's map is the game's real island map art. |
| D20 | XP and counts | Bars always show the real fraction, not the mockup's drawn fill. |
| D21 | Controls | Crouch is removed from the game (GDD 1.24). Defaults: Interact E, Backpack B, Map M, so the mockup's key rows match except the dropped Crouch row. |
| D22 | Fix round 3 (server, loot, trade) | Party views go only to players whose view changed; an unchanged Ready flag or another no-op sends nothing. Body and chest takes name the entry by a stable key (`ListingKeys`: instance id, or `stack:<catalogId>`) besides its index, and the server refuses a take whose entry is gone, so a double press or a stale list never takes a different item; Take buttons ignore presses while one is in flight. Loot and chest rows show the item's art and a rarity dot from the server's `catalogId`. `ForgeSnapshot` `maxCount` also counts lobby backpack room, so the quantity stepper never offers a batch that would fail BackpackFull. A Forge batch is one Forge action for analytics, the tutorial and quests; XP and Crafting mastery scale with the count. A trade invite toast answers directly (Accept primary, Decline secondary, no ✕); pressing the card opens the same question as a dialog. |
| D23 | Fix round 4 | The lobby HUD never takes gamepad selection by itself; a controller player enters it with an explicit lobby-only button (hint shown) and leaves with B. Items without their own art show a neutral "picture missing" placeholder (never a glyph that looks like a real item) in slots, rows and detail pictures; the name stays in tooltips and detail text. Leather buttons use two tones sampled from the mockups: the bright primary is the sprite's own colour, the darker one a token tint. Settings tabs follow one rule for all four (an icon for each, or text only for each). The client asks for its party view on start (`PartyAction("view")`, rate-limited like every party action); the server resends it even when unchanged. |
| D24 | Party Ready removed (supersedes D3, D16, D18) | There is no Ready flag anywhere. The server has no `PartyAction("ready")`, no per-player ready state and no `ready` fields in the party view; deploys and membership changes no longer clear it. The Party window drops the Readied Status card, its toggle and the "k of n ready" tally, and Party Details takes the whole right column (mockup top y 245, bottom y 693). Member rows carry no Ready / Not Ready tags and the HUD party panel no ready dots. Only a solo player or the party leader can press Play; other members see Play disabled with "The party leader starts the run." The deploy check has no ready line. The leader is marked only by the crown next to the name: no Leader tag on any screen. |
| D25 | Play window chrome (deviation from mockup 05) | The Play window looks like the other menus, with Inventory as the model: the same window size (1187 × 650), header (the Play tile's portal icon, "PLAY" at Inventory's title size and position, the plain ink underline), clasps and close-button corner. No raised title plaque. The map sits in an inset panel like Inventory's detail card (the real island art and crater marker). The right column opens with a section heading "SHATTERED CRATER" over a hairline (no plaque), then the detail rows with hairlines, YOUR PARTY and YOUR EQUIPMENT as standard SectionHeaders, the six slots, and the primary leather PLAY button with the play glyph at the bottom right. |
