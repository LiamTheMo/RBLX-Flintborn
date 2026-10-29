# UI progress

Parchment-and-leather UI from the reference sheets in `art/reference/ui/parchment/`.

| Screen / component | Reference | Spec | Assets | Static build | States | Motion | Integration | Visual | Platform | Code review | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Lobby screen | 13_lobby_master, 02_lobby_parts | ✅ [LobbyScreen.md](LobbyScreen.md) | ✅ uploaded | ✅ | ✅ | ✅ | ✅ | preview ✅ (4 verifier rounds), Studio ⏳ | layout ✅, phones ✅ except 568×320 (documented), devices ⏳ | ✅ | Live; Studio capture and device touch remain manual checks |
| Lobby popups (deploy check, invites, server) | 01_frames, 03_buttons | in LobbyScreen.md | ✅ uploaded | ✅ | ✅ | ✅ | ✅ | code-reviewed; not in the preview, Studio ⏳ | sizing simulated ✅ | ✅ | Built |
| Journal (quests + island map) | 07_journal | ✅ [JournalScreen.md](JournalScreen.md) | ✅ sliced + painted map (upload ⏳) | ✅ | ✅ | n/a | ✅ QuestView / QuestClaim | capture ✅, Studio ⏳ | fit ✅, devices ⏳ | ⏳ | Built; upload and in-game checks remain |
| Inventory & Vault (lobby + run) | 08_inventory_vault | ✅ [InventoryScreen.md](InventoryScreen.md) | ✅ sliced (upload ⏳); item icons later | ✅ | ✅ | n/a | ✅ VaultController + InventoryController | capture ✅, Studio ⏳ | fit ✅, devices ⏳ | ⏳ | Built; upload and in-game checks remain |
| Crafting + Forge | 09_crafting | ✅ [CraftingScreen.md](CraftingScreen.md) | ✅ sliced (upload ⏳); item icons later | ✅ | ✅ | n/a | ✅ Craft / smelt / ForgeCraft | capture ✅, Studio ⏳ | fit ✅, devices ⏳ | ⏳ | Built; upload and in-game checks remain |
| Settings | 10_settings | ✅ [SettingsScreen.md](SettingsScreen.md) | ✅ sliced (upload ⏳) | ✅ | ✅ | n/a (instant) | ✅ new settings live through attributes | capture ✅, Studio ⏳ | fit ✅, devices ⏳ | ⏳ | Built; upload and in-game checks remain |
| Market, Progress, Trade + notice cards | 11_panel_layouts | ✅ [ListWindows.md](ListWindows.md) | ✅ sliced (upload ⏳); item icons later | ✅ | ✅ | n/a | ✅ Shop / Sell / Offers / Codes, perks, rebirth, trades, notices | capture ✅, Studio ⏳ | fit ✅, devices ⏳ | ⏳ | Built; upload and in-game checks remain |
| World map | 11_panel_layouts + Journal map | ✅ in [ListWindows.md](ListWindows.md) | ✅ sliced + painted map (upload ⏳) | ✅ | ✅ | n/a | ✅ portals, events, camps, you | capture ✅, Studio ⏳ | fit ✅, devices ⏳ | ⏳ | Built; upload and in-game checks remain |
| In-world HUD (parchment) | 12_hud_master | ✅ [HudScreen.md](HudScreen.md) | ✅ sliced (upload ⏳) | ✅ | ✅ | bars ease | ✅ same HudController data | capture ✅, Studio ⏳ | scale ✅, devices ⏳ | ⏳ | Built (six slots, GDD §56); upload and in-game checks remain |
| Kit sheets | 01, 03–06, 11, 14–16 | — | partial (lobby pieces) | — | — | — | — | — | — | — | Sliced as screens need them |

## Notes and blockers

- No Roblox Studio MCP server is connected to the build sessions, so captures come
  from `art/ui/capture/capture.py`, which runs the game's own UI code headlessly
  (`gui_env.luau`) and renders what it builds (`render.py`); an in-Studio capture
  is a manual check. Sprites not uploaded yet are previewed from their PNGs.
