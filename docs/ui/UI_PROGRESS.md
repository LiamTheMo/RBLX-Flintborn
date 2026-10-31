# UI progress

Branch: `ui/lobby-ui-rebuild`   Base: `v0.18`   Updated: 2026-10-31

The rebuild of every screen from one parchment-and-leather kit, matched to the
seven mockups in [`art/reference/ui/lobby/`](../../art/reference/ui/lobby/README.md)
(01 HUD, 02 Inventory, 03 Settings, 04 Party, 05 Play, 06 Forge, 07 Journal). Screens
without a mockup are restyled from the same kit. The contract is
[ARCHITECTURE.md](ARCHITECTURE.md); its §12 decisions override earlier sections.
Evidence lives in `art/ui/captures/` (`<scene>.png`, plus `_compare` and `_overlay`
against the mockup where one exists), rendered by
`python3 art/ui/capture/capture.py <scene>`. The independent verifier reports
(round 1) are in `art/ui/verify/{visual,responsive,code}/REPORT.md`; their local
evidence (per-profile captures for 11 screen sizes, from 667 × 375 phones to
5120 × 1440) sits beside them, untracked. Fix round 3 is working through them.

Legend: ✅ done · 🔄 in progress · ⏳ not started or waiting · — not applicable.

| Screen / component | Reference | Spec | Assets | Static build | States | Motion | Integration | Visual | Platform | Code review | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Kit (`Hud/Kit`, `KitTokens.json`) | kit sheets 01–20 | ✅ [KIT.md](KIT.md), ARCHITECTURE §2–3 | ✅ 259 `lk_` sprites sliced; upload ⏳ | ✅ | ✅ `kit_gallery` (every family and state, plus fallback pages) | ✅ tokens `motion` | — | ✅ `kit_gallery_compare` | ⏳ device | ✅ round 1 (no High) | Fix round 3; waiting for the upload |
| Lobby HUD (01) | `01_hud.png` | ✅ [LobbyScreen.md](LobbyScreen.md) | ✅ sliced; upload ⏳ | ✅ `Screens/LobbyHud` | ✅ `lobby_hud_states` | ✅ | ✅ `LobbyHudController`: progression, currency, tiles, party panel, hotbar, notices; `lobby_hud_flow` | ✅ `lobby_hud_compare` | ✅ `lobby_hud_phone`, `lobby_hud_wide`; devices ⏳ | ✅ round 1 (no High) | Fix round 3 (verifier FAIL (V1, V11, V13)) |
| Inventory and Vault (02) | `02_inventory.png` | ✅ [InventoryScreen.md](InventoryScreen.md) | ✅ sliced, item art through `ItemInfo.Icon`; upload ⏳ | ✅ `Screens/InventoryWindow` | ✅ `inventory_states` | ✅ | ✅ `VaultController` (Store/Take/Store all), `InventoryController` (run); `inventory_flow` | ✅ `inventory_backpack_compare` | ✅ verifier profiles (`verify/responsive/captures/inventory`); devices ⏳ | ✅ round 1 (no High) | Built; in-game checks remain |
| Settings (03) | `03_settings.png` | ✅ [SettingsScreen.md](SettingsScreen.md) | ✅ sliced; upload ⏳ | ✅ `Screens/SettingsWindow`, 4 tabs (D1) | ✅ dirty, capturing key | ✅ | ✅ `SettingsController` (draft, APPLY/RESET, rebinding); `settings_flow` | 🔄 `settings_*_compare`; verifier FAIL (V3, V15) in fix round 3 | ✅ verifier profiles (`verify/responsive/captures/settings`); devices ⏳ | ✅ round 1 (no High) | Fix round 3 |
| Party (04) | `04_party.png` | ✅ [PartyScreen.md](PartyScreen.md) | ✅ sliced; upload ⏳ | ✅ `Screens/PartyWindow` | ✅ `party_states` (ready / not ready, Invited, member view) | ✅ | ✅ `PartyController`; server Ready, `createdAt`, `invited`, `fromUserId` (`party_ready.spec`); `party_flow` | ✅ `party_compare` | ✅ `party_phone`; devices ⏳ | ✅ round 1 (no High) | Fix round 3 (verifier FAIL (V11, V15)) |
| Play (05) | `05_play.png` | ✅ [PlayScreen.md](PlayScreen.md) | ✅ sliced, island painting; upload ⏳ | ✅ `Screens/PlayWindow` | ✅ `play_states` (busy, nil preview, member, k of n ready) | ✅ | ✅ `PlayController`: deploy check, Deploy, Ready for non-leaders; `play_flow` | ✅ `play_compare` | ✅ `play_phone`; devices ⏳ | ✅ round 1 (no High) | Fix round 3 (verifier FAIL (V14)) |
| Ancestral Forge (06) and field Crafting | `06_forge.png` | ✅ [ForgeScreen.md](ForgeScreen.md), [CraftingScreen.md](CraftingScreen.md) | ✅ sliced; upload ⏳ | ✅ `Screens/RecipeWindow` (modes forge, crafting) | ✅ locked, short, busy, job running | ✅ | ✅ `ForgeController` with batch count (D4; `maxCount` counts backpack room, D22; `forge.spec`, `forge_batch.spec`); `CraftingController`; `forge_flow`, `crafting_flow` | 🔄 `forge_*_compare`; verifier FAIL (V1, V2, V8, V11) in fix round 3 | ✅ verifier profiles (`verify/responsive/captures/forge`); subtitles < 9 px (R9) in fix round 3; devices ⏳ | ✅ round 1 (no High) | Fix round 3 |
| Quest Journal (07) | `07_journal.png` | ✅ [JournalScreen.md](JournalScreen.md) | ✅ sliced, island painting; upload ⏳ | ✅ `Screens/JournalWindow`, `IslandMap` | ✅ claimable, claimed, side tabs (D12) | ✅ | ✅ `JournalController` (QuestView / QuestClaim); `journal_flow` | ✅ `journal_*_compare` | ✅ `journal_phone`; devices ⏳ | ✅ round 1 (no High) | Fix round 3 (verifier FAIL (V6)) |
| Market, Trade, Progress, World map | none (restyle) | ✅ [ListWindows.md](ListWindows.md) | ✅ kit only | ✅ `Hud/ListWindow` on the kit | ✅ | ✅ | ✅ `WalletController`, `TradeController` (item art from server `catalogId`; invite toast with Accept / Decline, D22), `ProgressionController`, `MapController`; `market_flow`, `trade_flow`, `progress_flow`, `map_flow` | captures ✅ (no mockup) | devices ⏳ | ✅ round 1 (no High) | Fix round 3 (verifier FAIL (no-mockup screens: V1, V4, V5, V10, V12)) |
| In-world HUD | none (restyle) | ✅ [HudScreen.md](HudScreen.md) | ✅ kit only | ✅ `Vitals`, `BottomBar`, `PartyFrames`, `Compass`, `ObjectivePanel`, `EventPanel` | ✅ `world_hud_states` | ✅ bars ease | ✅ `HudController`; `world_hud_flow` | captures ✅ (no mockup) | ✅ `world_hud_phone`, `world_hud_wide`; devices ⏳ | ✅ round 1 (no High) | Fix round 3 (verifier FAIL (no-mockup screens)) |
| World overlays, notices, loot, storage, world menu | none (restyle) | ARCHITECTURE §4.8 | ✅ kit only | ✅ | ✅ | ✅ | ✅ `NoticeController`, `LootController` and `StorageController` (item art and rarity dot from server `catalogId`; takes by stable key with an in-flight guard, D22), `WorldMenuController`, …; `world_overlays_flow` | captures ✅ `world_overlays`, `notices`, `world_menu` | ✅ `world_overlays_phone`; devices ⏳ | ✅ round 1 (no High) | Fix round 3 (verifier FAIL (no-mockup screens)) |
| Atlases and upload | — | ARCHITECTURE §6 | 🔄 GROUPS in `art/ui/pack_atlas.py`; `lk_` ids not in `UiAssetIds.json` yet | — | — | — | — | `--uploaded-only` fallback pages ✅ | ⏳ | — | Waiting for the owner's upload run |
| Removal of the old UI (§9) | — | ARCHITECTURE §9 | — | — | — | — | — | — | — | — | 🔄 Old `Hud/LobbyHud`, `LobbyPopups`, `Parchment`, `ItemSlot`, `InventoryPanel`, `SettingsPanel`, `CraftingPanel`, `JournalPanel`, the HudLayout `lobby` section and the preview scripts are gone, and the deploy removes the old modules from the places (`RETIRED` in `scripts/roblox_live_publish.py`); legacy sprites and atlases stay until the `lk_` upload is live |

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
- **Verifier round 1:** visual FAIL (2 High, 13 Medium), responsive FAIL (7 High,
  11 Medium), code PASS (no High). Fix round 3 owners: F1 Kit, F2 lobby screens,
  F3 world HUD and overlays, F4 server, loot, trade and scripts; a fresh verifier
  round follows. Scene owners still to add `catalogId` and `key` to the mocked
  `CorpseOpened` / `ChestOpened` payloads in `world_overlays*.luau` (F3), or the
  loot captures keep showing rows without item art (V10).
- **Note for F2:** `ForgeScreen.md` (Data table, QUANTITY row, about line 214) still
  says `ForgeCraft` has no count; it has one (D4: `count` 1..10, all or nothing,
  `maxCount` per recipe in `ForgeSnapshot`, which also counts backpack room, D22).
- **Old specs.** `HudScreen.md`, `ListWindows.md`, `CraftingScreen.md` and parts of
  the screen specs still describe the parchment build or name removed modules; the
  analysts replace them (ARCHITECTURE §9).
