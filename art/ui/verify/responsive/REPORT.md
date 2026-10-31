# Responsive & Platform QA — round 1
Result: FAIL (7 High, 11 Medium, 6 Low). 13 scenes × 11 profiles (1920×1080, 1366×768, 2560×1080, 1280×800, 1024×768, 2532×1170, 1334×750, 844×390, 667×375, 5120×1440, console 1080p). Nothing off-screen anywhere.

| # | Finding | Sev | Owner |
|---|---|---|---|
| R1 | Lobby HUD text on phones: party names 6–7.5 px (4.5 with 20-char names), level/hotbar badges 8 px, long coin/notice values ~5.5 px | High | Screens/LobbyHud, Kit/PlayerRow |
| R2 | World HUD text on phones: objective 6–7 px, compass 7.5, event 7.8, badges 8, prompt 7–8 | High | ObjectivePanel, Compass, EventPanel, BottomBar, InteractionPrompt, HudLayout.json |
| R3 | Toasts/tooltips no phone floor (toast scale 0.41 → 7 px text); toast ✕ raw button without hit pad (9 px phone) | High | Kit/Toast, Kit/Tooltip:111 |
| R4 | World settings gear (unscaled 52 px at 1,-12) sits on the Roblox jump button on phones; jump button covers World Event panel | High | SettingsController:257-276, EventPanel placement |
| R5 | 667×375: attack button covers hotbar slot 6 (91%) | High | HudLayout.json attack.phonePos |
| R6 | Console: no way into UI — LobbyHud:DefaultSelection never called; World Menu, Loot, Storage, Tribe, Build palette no default selection; Play/Party/Forge/ConfirmDialog open without gamepad flag; ButtonSelect bound to Progress | High | LobbyHudController, world controllers, Kit/Modal, Keybinds |
| R7 | Lobby invite Accept/Decline on phones: 17 px buttons 3 px apart, 44 px pads overlap 62% | High | Screens/LobbyHud |
| R8 | Phone windows draw under the Roblox top bar (WindowFit top = 0) | Med | Kit/Modal / Scale |
| R9 | Phone window text < 9 px: Map legend 8 (scale 0.444), Journal Daily tag 8, Forge subtitles 8.1–8.4 | Med | ListWindow/Map, JournalWindow, RecipeWindow |
| R10 | Touch tablets (1024×768, 1280×800) get desktop sizing (0.61): small text 7.3–8 px; IsSmallTouch only checks height < 500 | Med | Kit/Scale |
| R11 | Phones: toasts cover the server notice card's title | Med | Kit/Toast / NoticeCard placement |
| R12 | Long strings: 20-char names overflow at 9 px floor (lobby, Party, world party frames); "+1 more in your backpack", "REPLAY TUTORI…", "Party Leader" truncated; Journal description overflows | Med | screens |
| R13 | World Event description overflows its panel at every resolution | Med | EventPanel |
| R14 | Text boxes have no touch pad (search 24–33 px, Market code box 27 px) | Med | Kit/SearchBox, TextField, ListWindow |
| R15 | Gamepad: dropdowns don't move selection into options/back; recipe list re-render orphans selection | Med | Kit/Dropdown, RecipeWindow |
| R16 | Glyphs ignore input type: no LastInputTypeChanged; hotbar badges always 1–6; gamepad tooltips "Backpack (B)"; Controls lists keyboard only | Med | Kit, BottomBar, SettingsWindow |
| R18 | Phones: world tile grid in the thumbstick zone (device check) | Med | HudLayout.json |
| R17,R19–R24 | Low: build-time phone decisions (3 floors); console body 17 px; Play loadout slots/material rows not selectable; literal-pixel phone profiles get desktop rules; 32:9 HUD at far edges; Inventory/Forge select Close first; Map drag vs zoom z-order | Low | various |

Passed: nothing off-screen; desktop/tablet clear of top bar; Kit controls reach 44 px targets; B closes top layer (dialog first); selection returns on close; one-window rule; Settings/Journal/Party default selection.
Needs a device: unibar/top-bar size on phones, TouchGui geometry, notches, DPI and 10-foot readability, UITextSizeConstraint under UIScale, padded hit clipping, ButtonSelect pass-through.
