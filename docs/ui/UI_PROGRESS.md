# UI progress

Branch: `ui/lobby-ui-rebuild`   Base: `main`   Updated: 2026-10-31

The rebuild of every screen from one parchment-and-leather kit, matched to the
seven mockups in [`art/reference/ui/lobby/`](../../art/reference/ui/lobby/README.md)
(01 HUD, 02 Inventory, 03 Settings, 04 Party, 05 Play, 06 Forge, 07 Journal). Screens
without a mockup are restyled from the same kit. The contract is
[ARCHITECTURE.md](ARCHITECTURE.md); its §12 decisions override earlier sections.
Evidence lives in `art/ui/captures/` (`<scene>.png`, plus `_compare` and `_overlay`
against the mockup where one exists), rendered by
`python3 art/ui/capture/capture.py <scene>`.

Legend: ✅ done · 🔄 in progress · ⏳ not started or waiting · — not applicable.

| Screen / component | Reference | Spec | Assets | Static build | States | Motion | Integration | Visual | Platform | Code review | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Kit (`Hud/Kit`, `KitTokens.json`) | kit sheets 01–20 | ✅ [KIT.md](KIT.md), ARCHITECTURE §2–3 | ✅ 259 `lk_` sprites sliced; upload ⏳ | ✅ | ✅ `kit_gallery` (every family and state, plus fallback pages) | ✅ tokens `motion` | — | ✅ `kit_gallery_compare` | ⏳ device | ⏳ | Built; waiting for the upload |
| Lobby HUD (01) | `01_hud.png` | ✅ [LobbyScreen.md](LobbyScreen.md) | ✅ sliced; upload ⏳ | ✅ `Screens/LobbyHud` | ✅ `lobby_hud_states` | ✅ | ✅ `LobbyHudController`: progression, currency, tiles, party panel, hotbar, notices; `lobby_hud_flow` | ✅ `lobby_hud_compare` | ✅ `lobby_hud_phone`, `lobby_hud_wide`; devices ⏳ | ⏳ | Built; in-game checks remain |
| Inventory and Vault (02) | `02_inventory.png` | ✅ [InventoryScreen.md](InventoryScreen.md) | ✅ sliced, item art through `ItemInfo.Icon`; upload ⏳ | ✅ `Screens/InventoryWindow` | ✅ `inventory_states` | ✅ | ✅ `VaultController` (Store/Take/Store all), `InventoryController` (run); `inventory_flow` | ✅ `inventory_backpack_compare` | phone capture ⏳; devices ⏳ | ⏳ | Built; phone capture and in-game checks remain |
| Settings (03) | `03_settings.png` | ✅ [SettingsScreen.md](SettingsScreen.md) | ✅ sliced; upload ⏳ | ✅ `Screens/SettingsWindow`, 4 tabs (D1) | ✅ dirty, capturing key | ✅ | ✅ `SettingsController` (draft, APPLY/RESET, rebinding); `settings_flow` | ✅ `settings_*_compare` for every tab | phone capture ⏳; devices ⏳ | ⏳ | Built; phone capture and in-game checks remain |
| Party (04) | `04_party.png` | ✅ [PartyScreen.md](PartyScreen.md) | ✅ sliced; upload ⏳ | ✅ `Screens/PartyWindow` | ✅ `party_states` (ready / not ready, Invited, member view) | ✅ | ✅ `PartyController`; server Ready, `createdAt`, `invited`, `fromUserId` (`party_ready.spec`); `party_flow` | ✅ `party_compare` | ✅ `party_phone`; devices ⏳ | ⏳ | Built; in-game checks remain |
| Play (05) | `05_play.png` | ✅ [PlayScreen.md](PlayScreen.md) | ✅ sliced, island painting; upload ⏳ | ✅ `Screens/PlayWindow` | ✅ `play_states` (busy, nil preview, member, k of n ready) | ✅ | ✅ `PlayController`: deploy check, Deploy, Ready for non-leaders; `play_flow` | ✅ `play_compare` | ✅ `play_phone`; devices ⏳ | ⏳ | Built; in-game checks remain |
| Ancestral Forge (06) and field Crafting | `06_forge.png` | ✅ [ForgeScreen.md](ForgeScreen.md), [CraftingScreen.md](CraftingScreen.md) | ✅ sliced; upload ⏳ | ✅ `Screens/RecipeWindow` (modes forge, crafting) | ✅ locked, short, busy, job running | ✅ | ✅ `ForgeController` with batch count (D4, `forge.spec`, `forge_batch.spec`); `CraftingController`; `forge_flow`, `crafting_flow` | ✅ `forge_*_compare` | phone capture ⏳; devices ⏳ | ⏳ | Built; phone capture and in-game checks remain |
| Quest Journal (07) | `07_journal.png` | ✅ [JournalScreen.md](JournalScreen.md) | ✅ sliced, island painting; upload ⏳ | ✅ `Screens/JournalWindow`, `IslandMap` | ✅ claimable, claimed, side tabs (D12) | ✅ | ✅ `JournalController` (QuestView / QuestClaim); `journal_flow` | ✅ `journal_*_compare` | ✅ `journal_phone`; devices ⏳ | ⏳ | Built; in-game checks remain |
| Market, Trade, Progress, World map | none (restyle) | ✅ [ListWindows.md](ListWindows.md) | ✅ kit only | ✅ `Hud/ListWindow` on the kit | ✅ | ✅ | ✅ `WalletController`, `TradeController` (item art from server `catalogId`), `ProgressionController`, `MapController`; `market_flow`, `trade_flow`, `progress_flow`, `map_flow` | captures ✅ (no mockup) | devices ⏳ | ⏳ | Built; in-game checks remain |
| In-world HUD | none (restyle) | ✅ [HudScreen.md](HudScreen.md) | ✅ kit only | ✅ `Vitals`, `BottomBar`, `PartyFrames`, `Compass`, `ObjectivePanel`, `EventPanel` | ✅ `world_hud_states` | ✅ bars ease | ✅ `HudController`; `world_hud_flow` | captures ✅ (no mockup) | ✅ `world_hud_phone`, `world_hud_wide`; devices ⏳ | ⏳ | Built; in-game checks remain |
| World overlays, notices, loot, storage, world menu | none (restyle) | ARCHITECTURE §4.8 | ✅ kit only | ✅ | ✅ | ✅ | ✅ `NoticeController`, `LootController` and `StorageController` (item art from server `catalogId`), `WorldMenuController`, …; `world_overlays_flow` | captures ✅ `world_overlays`, `notices`, `world_menu` | ✅ `world_overlays_phone`; devices ⏳ | ⏳ | Built; in-game checks remain |
| Atlases and upload | — | ARCHITECTURE §6 | 🔄 GROUPS in `art/ui/pack_atlas.py`; `lk_` ids not in `UiAssetIds.json` yet | — | — | — | — | `--uploaded-only` fallback pages ✅ | ⏳ | — | Waiting for the owner's upload run |
| Removal of the old UI (§9) | — | ARCHITECTURE §9 | — | — | — | — | — | — | — | — | 🔄 Old `Hud/LobbyHud`, `LobbyPopups`, `Parchment`, `ItemSlot`, `InventoryPanel`, `SettingsPanel`, `CraftingPanel`, `JournalPanel`, the HudLayout `lobby` section and the preview scripts are gone; legacy sprites and atlases stay until the `lk_` upload is live |

## Notes and blockers

- **Upload.** No `lk_` sprite or `atlas_lk_*` id is in `src/shared/UI/UiAssetIds.json`
  yet, so in game every screen draws the kit's fallback look until the owner runs
  `scripts/roblox_upload_ui_assets.py --upload`. Captures preview the unuploaded
  PNGs; the `--uploaded-only` pages show the fallback look.
- **Captures, not Studio.** No Roblox Studio MCP server is connected to the build
  sessions, so every capture comes from `art/ui/capture/capture.py`, which runs
  the game's UI code headlessly (`gui_env.luau`) and renders it (`render.py`). The
  headless environment has no layout pass, blur, rotation or RichText sizes
  (ARCHITECTURE §7); those, device safe areas, real touch and gamepad focus are
  manual checks in [MANUAL_VALIDATION.md](../MANUAL_VALIDATION.md).
- **Phone captures missing** for Inventory, Settings and the Forge.
- **Code review** of the rebuilt screens is still to be done.
- **Old specs.** `HudScreen.md`, `ListWindows.md`, `CraftingScreen.md` and parts of
  the screen specs still describe the parchment build or name removed modules; the
  analysts replace them (ARCHITECTURE §9).
