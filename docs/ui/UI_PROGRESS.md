# UI progress

Parchment-and-leather UI from the reference sheets in `art/reference/ui/parchment/`.

| Screen / component | Reference | Spec | Assets | Static build | States | Motion | Integration | Visual | Platform | Code review | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Lobby screen | 13_lobby_master, 02_lobby_parts | ✅ [LobbyScreen.md](LobbyScreen.md) | ✅ | ✅ | ✅ | ✅ | ✅ | preview ✅, Studio ⏳ | layout ✅, devices ⏳ | ✅ | Built; Studio capture and devices need manual validation |
| Lobby popups (deploy check, invites, server) | 01_frames, 03_buttons | in LobbyScreen.md | ✅ | ✅ | ✅ | ✅ | ✅ | preview ⏳ | — | ✅ | Built |
| Journal (quests) | 07_journal | — | — | — | — | — | — | — | — | — | Not started |
| Inventory & Vault | 08_inventory_vault | — | — | — | — | — | — | — | — | — | Not started |
| Crafting | 09_crafting | — | — | — | — | — | — | — | — | — | Not started |
| Settings | 10_settings | — | — | — | — | — | — | — | — | — | Not started |
| In-world HUD (parchment) | 12_hud_master, 05_widgets | — | — | — | — | — | — | — | — | — | Not started |
| Kit sheets | 01, 03–06, 11, 14–16 | — | partial (lobby pieces) | — | — | — | — | — | — | — | Sliced as screens need them |

## Notes and blockers

- No Roblox Studio MCP server is connected to the build sessions, so captures come
  from `art/ui/preview_lobby.py`; an in-Studio capture is a manual check.
