# Lobby screen UI spec

Reference: `art/reference/ui/parchment/13_lobby_master.png` (layout), with
`02_lobby_parts.png` (close-ups), `04_icons.png`, `03_buttons.png`,
`01_frames.png` and `06_materials.png` for the kit pieces.
Design resolution: 1672×941 (the same canvas as `HudLayout.json`).
Status: Approved for build. Source of truth for build: the reference sheets.

## Overview

The lobby place's always-on screen (GDD §11, §25.1): the player's profile with
level and XP, Coins and Gems, the settings button, the navigation tiles, the
party panel, and the Enter button with the server dropdown. It replaces the older
dark rope-frame lobby screen in the parchment-and-leather style of the new
sheets. It is not modal; popups (deploy check, party invites, server menu) open
above the Enter button as parchment cards.

## Tokens

All in `src/shared/UI/HudLayout.json` → `lobby.colors` / `fontFaces`.

| Token | Value | Used by |
|---|---|---|
| ink | #3A1F0F | Name, title, values, member names |
| inkSoft | #5A3A24 | Secondary text (invites, popup lines) |
| paper | #F6DDB8 | Fallback plates, status strip, popup rows |
| paperEdge | #6B4528 | Fallback strokes |
| line | #C4A27A | Party header divider and row rules |
| dot | #C9A681 | Empty party slot markers |
| thumb / track | #996E4B / #D8B890 | Party scrollbar |
| photo | #C5B3A1 | Portrait backdrop behind headshots |
| leather | #9B3A1E | Fallback Enter / primary buttons |
| cream | #FBEBD0 | Text on leather |
| Font.Serif | Merriweather Bold | Every lobby text (closest Roblox family to the sheets' slab serif) |

## Element tree

Bounds are design px (x, y, w, h) from the top-left of the 1672×941 canvas,
measured from the alpha components of the master (`ref_tools.py`-style
component scan, scanlines and ink boxes; see Measurements log).

| Element | Bounds | Anchor intent | Appearance | Content | Native or image |
|---|---|---|---|---|---|
| Profile | 48,85,529,135 | top-left | `pm_lobby_profile` | — | image |
| Profile.Headshot | 67,102,106,101 | in profile | photo #C5B3A1 under the frame's window | live headshot | native |
| Profile.Name | 206,111,290,40 | in profile | Serif 32, ink | DisplayName | native |
| Profile.Level | 208,159,74,26 | in profile | Serif 24, ink | "LV. 12" | native |
| Profile.XpFill | 287,165,232,14 | in profile | `pm_fill_xp` 9-slice, width = fraction | XP | image |
| Coins | 1253,99,162,66 | top-right | `pm_lobby_coins` | — | image |
| Coins.Value | 1321,113,88,38 | in pill | Serif 26, ink | "2,450" | native |
| Gems | 1425,99,132,66 | top-right | `pm_lobby_gems` | — | image |
| Gems.Value | 1489,113,64,38 | in pill | Serif 26, ink | "125" | native |
| Settings | 1569,98,69,66 | top-right | `pm_lobby_gear` | — | image |
| Nav tiles | 35,370 and 182,370 / 35,517 and 182,517 / 35,664 and 182,664; 142×141, pitch 147 | left | `pm_tile_*` | Inventory, Vault, Quests, Shop, Forge, Trade | image |
| Party | 1211,267,433,381 | top-right | `pm_lobby_party` | — | image |
| Party.Title | 1265,307,300,40 | in panel | Serif 34, ink | "PARTY  1/10" | native |
| Party.Divider | 1262,353,334,2 | in panel | line | — | native |
| Party.List | 1261,359,345,240 | in panel | scrolling; bar 10 px thumb/track | rows | native |
| Member row | h 75 | list | headshot 62×59 at 0,7; name Serif 24 at 82; crown 30×23 at 231,24; add-friend 68×52 at 276,9 (own row, leader, room left); rule at y 74 | members | native + images |
| Empty slot row | h 50 | list | dot 22 px at 3,14; rule at y 48 | free slots up to the cap | native |
| Enter | 525,741,622,180 | bottom-centre | `pm_lobby_enter` (lettering painted) | "ENTER / SHATTERED CRATER" | image |
| Server | 1150,799,251,71 | right of Enter | `pm_lobby_server` (icon + arrow painted) | "Choose server" Serif 19 at 1224,815,132,34 | image + native |
| Status strip | centred, bottom 736, 560×34 | above Enter | paper fill, paperEdge stroke, Serif 18 ink | status / maintenance text | native |

## Measurements log

- Element bounds: alpha connected components (alpha > 40) of the master.
- Text: ink boxes (luminance < 100) per region — profile name cap 120–144, level cap
  162–180, Coins cap 122–141, Gems cap 122–142, party title cap 314–339, member name
  cap 387–404, server cap 824–840. TextSize = cap height / 0.74 (Merriweather Bold
  cap height measured at 0.74 em).
- XP track: scanlines row 172 and columns 400/500 — outline 162–180, interior
  165–178, fill 287–462.
- Party rules: column scans at x 1276/1450 — divider 353–355, rules 433, 480, 532,
  583; dots 451–472 (22 px); scrollbar x 1595–1605, thumb #996E4B, track #D8B890.
- Portrait window: grid crop at 4× — 69–171 × 104–201.

## States

| Element | Default | Hover | Pressed | Busy / disabled | Focus (gamepad) | Source |
|---|---|---|---|---|---|---|
| Nav tile | art | UIScale 1.04 + name tag beside the tile | UIScale 0.97 | — | same as hover | default (reference shows none) |
| Profile / Coins / Settings / Server | art | UIScale 1.04 | 0.97 | — | as hover | default |
| Enter | art | UIScale 1.04 | 0.97 | dark veil over the leather, inactive | as hover | default |
| Add friend | art | 1.04 | 0.97 | hidden when not leader / party full | as hover | ref image 2 |
| Popup buttons | `pm_button_leather` / `pm_button_parchment` | `_hover` art | `_pressed` art | `_disabled` art | as hover | ref image 3 |

Reduced motion (the game's ReducedMotion attribute) turns the scale tweens off.

## Motion and effects

| Trigger | Target | Properties | Duration | Easing |
|---|---|---|---|---|
| Hover / select | button UIScale | 1 → 1.04 | 0.12 s | Quad Out |
| Press | button UIScale | → 0.97 | 0.12 s | Quad Out |
| XP change | fill width | → fraction | 0.25 s | Quad Out |

## Data and behavior

Unchanged from the previous lobby screen: `LobbyHudController` feeds it
(`ProgressionController`, `Coins`/`Gems` attributes, `LobbyController` party
view and deploy, `SettingsController`, `VaultController`, `WalletController`,
`ForgeController`, `TradeController`). Party actions are server-validated by
`LobbyService` / `PartyRules`; the screen only requests.

## Asset map

Generated by `art/ui/slice_parchment.py` into `art/ui/sprites/` and
`manifest.json`; uploaded by the "Upload HUD sprites to Roblox" workflow; ids in
`src/shared/UI/UiAssetIds.json`. Sprites carry 2 px of transparent padding.

| Asset | Source | Size | 9-slice |
|---|---|---|---|
| pm_lobby_profile | master, text erased, portrait cut out, XP fill removed | 533×139 | — |
| pm_lobby_coins / pm_lobby_gems | master, values erased | 166×70 / 136×70 | — |
| pm_lobby_gear | master | 73×70 | — |
| pm_lobby_party | master, content erased | 437×385 | — |
| pm_lobby_enter | master | 626×184 | — |
| pm_lobby_server | master, label erased | 255×75 | — |
| pm_tile_inventory / vault / quests / shop | master | 146×~145 | — |
| pm_tile_forge / pm_tile_trade | blank master tile + icon sheet hammer-and-axe / group | 146×145 | — |
| pm_fill_xp | master XP fill | 176×14 | 7,6,7,6 |
| pm_button_add_friend | master party row | 68×52 | — |
| pm_icon_crown / pm_icon_add_friend | icon sheet | — | — |
| pm_panel | frames sheet | 529×314 | 70,62,70,62 |
| pm_button_leather(_hover/_pressed/_disabled) | buttons sheet | ~404×141 | 64,44,64,44 |
| pm_button_parchment(_hover/_pressed/_disabled) | buttons sheet | ~386×159 | 56,48,56,48 |
| pm_button_x / pm_button_check | buttons sheet | 155×150 | — |

Until a sprite has an uploaded id, `Widgets.Sprite` draws a parchment-coloured
stand-in and the lobby adds the words the art would carry (tile names, ENTER).

## Architecture

- Scaling: design-resolution offsets with the root UIScale from
  `HudModel.HudScale` (existing). The lobby ScreenGui ignores the GUI inset so the
  master's full-screen coordinates apply (the master leaves the top bar clear).
- Regions: profile and nav top-left; Coins, Gems, Settings and Party top-right;
  Enter and the server dropdown bottom-centre. `LobbyHud:Fit` shrinks the nav grid
  and the party panel on short screens so they never meet the Enter group.
- Authoring: code-built (`src/client/Hud/LobbyHud.luau`, `LobbyPopups.luau`,
  `Widgets.luau`) from `HudLayout.json`, synced by Rojo. No Studio-only UI.
- Preview: `art/ui/preview_lobby.py` composites the layout with the sprites the
  same way the Luau does, for checking without Studio.

## Open questions (defaults taken)

1. The master shows four navigation tiles; the lobby has six actions. Default:
   Forge and Trade as a third row in the same tile style (hammer-and-axe and the
   group icon from the icon sheet).
2. No hover/selected look is drawn for tiles. Default: the existing scale
   feedback plus a name tag, so each tile is named in words too (GDD §11).
3. Status messages ("Party invite sent…") had no place in the master. Default: a
   parchment strip above Enter; the server dropdown always reads "Choose server".

## Deviations from reference

- Font: Merriweather Bold stands in for the sheets' slab serif (closest Roblox
  family); letter widths differ slightly.
- Headshots are live Roblox thumbnails, not the painted portrait.
