# Settings screen UI spec

Reference: `art/reference/ui/parchment/10_settings.png` (window, Gameplay tab and
the control strip under it). Kit pieces from `03_buttons.png` (paper button).
Design resolution: the window art's own 1630×706 px, cut from the sheet at
(21, 58); every position below is a reference-sheet pixel.
Status: Built. Source of truth for build: the reference sheet.

## Overview

The modal Settings window (GDD §25, §46, §57), opened by the lobby's gear, the ⚙
button in the world, or the Settings key (O). A dark veil covers the game; the
window is centred below the Roblox top bar and scales to fit the screen
(`Parchment.Screen`, 0.3–1.4× times the player's UI scale). Five tabs down the
left choose a page; RESET and APPLY sit under every page.

Changes collect in a draft. APPLY saves the settings that differ from what is
saved (`SaveSettings`) and the key overrides (`SaveKeybinds`); APPLY is dimmed
while there is nothing to save. RESET returns the open tab's settings and keys to
their defaults in the draft. Closing discards the draft.

## Tokens

`src/shared/UI/HudLayout.json` `colors` (lobby tokens in `LobbyScreen.md`):

| Token | Value | Used by |
|---|---|---|
| ink / inkSoft | #2A0B02 / #5A3A24 | Labels, values / notes |
| cream | #FBEBD0 | Selected tab label and glyph |
| leather | #9B3A1E | Header marks, key notes |
| headerRule | #9E6B42 | Header underlines, column divider |
| rule | #DEC09E | Row rules |
| sliderTrack | #50311D | Slider track |
| sliderFill | #FDB335 | Slider fill |
| damage | #FFE1A0 | Floating damage numbers |
| veil | #1A0E06 at 45% | Behind the window |
| Font.Serif | Merriweather Bold | Every text |

## Element tree

| Element | Bounds (x, y, w, h) | Sprite / build |
|---|---|---|
| Window art | 21, 58, 1630, 706 | `pm_window_settings` (two tiles; title, close button, rope divider baked in) |
| Close (touch area) | 1504, 96, 94, 90 | transparent button over the baked ✕ |
| Tab *i* (1–5) | 86, 193.5 + 100.5·(i−1), 316, 100 | `pm_tab_paper` / `pm_tab_leather` (selected, drawn 2 px larger), glyph centred at x 149, label at x 196 (25 pt) |
| Header | mark 448 / 1060, y 220, h 34 | `pm_glyph_diamond` tinted leather, 33 pt capitals, 2 px `headerRule` underline |
| Slider row | label 491; track 683, cy−10, 260, 20; value 966 | native track + fill, `pm_slider_knob` (38 px) |
| Checkbox row | 490, cy−21, 470, 42 | `pm_check_on` / `pm_check_off`, label 20.5 pt at x 558 |
| Graphics dropdown | 713, cy−32, 304, 64 | `pm_dropdown` (9-slice), options list of 48 px rows |
| Key row | label 1123; key 1279, cy−24, w, 48 | `pm_keycap` (slice scale 0.62); width 60/76/94/106/116 for 1–5 characters |
| Column divider | 1061, 248, 2, 368 | `headerRule` |
| RESET | 1077, 634, 212, 77 | `pm_button_reset` (label baked) |
| APPLY | 1302, 624, 284, 94 | `pm_button_apply` (label baked) |

Rows (centre y): sliders 303, 360, 418; checkboxes 480, 531, 585; Graphics
Quality 663; key rows 300, 367, 436, 507, 578. Rules at 330, 388, 448, 505, 558,
612 (left) and 333, 402, 471, 542, 612 (right).

## Pages

| Tab | Left column | Right column |
|---|---|---|
| Gameplay (reference) | Music, Effects, Camera Sensitivity; Show Damage, Show Names, Invert Camera; Graphics Quality (opens upward) | KEY BINDINGS: Move W A S D (shown, fixed), Inventory (Backpack), Interact, Sprint, Map |
| Audio | Music, Effects; Subtitles for alert sounds | About Sound notes |
| Graphics | Graphics Quality; UI Scale (0.8–1.4×) | Quality notes |
| Controls | every rebindable action in two scrolling columns of keycaps | — (hint and last change under the list) |
| Accessibility | Colour-blind palette, Reduced motion, Subtitles; UI Scale | TUTORIAL: Replay tutorial (`pm_button_parchment`) |

A setting shown on two pages (Music, UI Scale, Subtitles, Graphics Quality) is
one draft value; changing it on one page shows on the other.

## States

| Control | Rest | Hover / gamepad focus | Pressed | Disabled |
|---|---|---|---|---|
| Sprite button, keycap | art | art ×0.93 | art ×0.80 | art ×0.72 (APPLY with nothing to save; keycaps without a keyboard) |
| Tab | paper, ink | paper ×0.93 | — | — |
| Tab (selected) | leather, cream | — | — | — |
| Slider | knob 38 px | knob ×1.1 (gamepad), ←/→ step | drag follows the pointer | — |
| Keycap capturing | "…" | — | — | — |

## Behaviour

- Rebinding: press a keycap, then the new key; Esc cancels; a key another action
  uses swaps with it; keys kept for movement, chat and menus are refused with a
  note. The draft keys save on APPLY.
- Gamepad: opening selects the current tab; B closes.
- Saved changes echo back as player attributes; an open window with nothing
  unsaved reloads them.
- Effects (PreferencesController, DamageNumbers, CombatController): volumes on
  the Music / Effects sound groups, `MouseDeltaSensitivity`, inverted vertical
  look through the PlayerModule's camera input, other players' name tags,
  `Lighting.GlobalShadows` and particle rates, floating damage numbers.

## Verification

`python3 art/ui/capture/capture.py settings` renders every tab from the game's
own code (`settings.png`, `settings_2…5.png`, the Gameplay tab pinned to the
sheet's place for overlay); `settings_flow` drives the controller (open, change,
APPLY, RESET, close) and fails on a wrong save. In-Studio and device checks are
in `docs/MANUAL_VALIDATION.md`.
