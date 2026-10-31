# UI progress

Branch: `ui/lobby-ui-rebuild`   Base: `v0.18`   Updated: 2026-10-31

The rebuild of every screen from one parchment-and-leather kit, matched to the
seven mockups in [`art/reference/ui/lobby/`](../../art/reference/ui/lobby/README.md)
(01 HUD, 02 Inventory, 03 Settings, 04 Party, 05 Play, 06 Forge, 07 Journal). Screens
without a mockup are restyled from the same kit. The contract is
[ARCHITECTURE.md](ARCHITECTURE.md); its §12 decisions override earlier sections.
Evidence lives in `art/ui/captures/` (`<scene>.png`, plus `_compare` and `_overlay`
against the mockup where one exists), rendered by
`python3 art/ui/capture/capture.py <scene>`. Independent verification: round 1
reports in `art/ui/verify/{visual,responsive,code}/REPORT.md`; the round-2
re-verification evidence (mockup compares, per-profile responsive data for 11 screen
sizes from 667 × 375 to 5120 × 1440, flow logs) in `art/ui/verify/round2/`, untracked.
Fix round 3 closed most round-1 findings; fix round 4 works through what round 2
still found (the K, W and S lists below).

Legend: ✅ done · 🔄 in progress · ⏳ not started or waiting · — not applicable.

| Screen / component | Reference | Spec | Assets | Static build | States | Motion | Integration | Visual | Platform | Code review | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Kit (`Hud/Kit`, `KitTokens.json`) | kit sheets 01–20 | ✅ [KIT.md](KIT.md), ARCHITECTURE §2–3 | ✅ sliced; the four `atlas_lk_*` atlases uploaded and their ids committed | ✅ | ✅ `kit_gallery` (every family and state, plus fallback pages) | ✅ tokens `motion` | — | ✅ `kit_gallery_compare` | ⏳ device | ✅ round 1 and 2 (no High) | Fix round 4: no-art placeholder, leather tones, toast ✕ pad (K1, K2, K4) |
| Lobby HUD (01) | `01_hud.png` | ✅ [LobbyScreen.md](LobbyScreen.md) | ✅ sliced; uploaded | ✅ `Screens/LobbyHud` | ✅ `lobby_hud_states` | ✅ | ✅ `LobbyHudController`: progression, currency, tiles, party panel, hotbar, notices; `lobby_hud_flow` | ✅ `lobby_hud_compare` | ✅ `lobby_hud_phone`, `lobby_hud_wide`; devices ⏳ | ✅ round 1 and 2 (no High) | Fix round 4: gamepad entry to the tiles, desktop leader name, invite below the fold (K5, K8, K9); S1 party view on join done |
| Inventory and Vault (02) | `02_inventory.png` | ✅ [InventoryScreen.md](InventoryScreen.md) | ✅ sliced, item art through `ItemInfo.Icon`; uploaded | ✅ `Screens/InventoryWindow` | ✅ `inventory_states` | ✅ | ✅ `VaultController` (Store/Take/Store all), `InventoryController` (run); `inventory_flow` | ✅ `inventory_backpack_compare` | ✅ verifier profiles (`verify/responsive/captures/inventory`); devices ⏳ | ✅ round 1 and 2 (no High) | Fix round 4: no-art placeholder, Vault tab label (K1, K9) |
| Settings (03) | `03_settings.png` | ✅ [SettingsScreen.md](SettingsScreen.md) | ✅ sliced; uploaded | ✅ `Screens/SettingsWindow`, 4 tabs (D1) | ✅ dirty, capturing key | ✅ | ✅ `SettingsController` (draft, APPLY/RESET, rebinding); `settings_flow` | 🔄 `settings_*_compare`; verifier FAIL (V3, V15) in fix round 3 | ✅ verifier profiles (`verify/responsive/captures/settings`); devices ⏳ | ✅ round 1 and 2 (no High) | Fix round 4: tab icon rule, phone headers truncate (K3, K7) |
| Party (04) | `04_party.png` | ✅ [PartyScreen.md](PartyScreen.md) | ✅ sliced; uploaded | ✅ `Screens/PartyWindow` | ✅ `party_states` (ready / not ready, Invited, member view) | ✅ | ✅ `PartyController`; server Ready, `createdAt`, `invited`, `fromUserId` (`party_ready.spec`); `party_flow` | ✅ `party_compare` | ✅ `party_phone`; devices ⏳ | ✅ round 1 and 2 (no High) | Fix round 4: leather tones (K2) |
| Play (05) | `05_play.png` | ✅ [PlayScreen.md](PlayScreen.md) | ✅ sliced, island painting; uploaded | ✅ `Screens/PlayWindow` | ✅ `play_states` (busy, nil preview, member, k of n ready) | ✅ | ✅ `PlayController`: deploy check, Deploy, Ready for non-leaders; `play_flow` | ✅ `play_compare` | ✅ `play_phone`; devices ⏳ | ✅ round 1 and 2 (no High) | Fix round 4: leather tones (K2) |
| Ancestral Forge (06) and field Crafting | `06_forge.png` | ✅ [ForgeScreen.md](ForgeScreen.md), [CraftingScreen.md](CraftingScreen.md) | ✅ sliced; uploaded | ✅ `Screens/RecipeWindow` (modes forge, crafting) | ✅ locked, short, busy, job running | ✅ | ✅ `ForgeController` with batch count (D4; `maxCount` counts backpack room, D22; `forge.spec`, `forge_batch.spec`); `CraftingController`; `forge_flow`, `crafting_flow` | 🔄 `forge_*_compare`; verifier FAIL (V1, V2, V8, V11) in fix round 3 | ✅ verifier profiles (`verify/responsive/captures/forge`); subtitles < 9 px (R9) in fix round 3; devices ⏳ | ✅ round 1 and 2 (no High) | Fix round 4: locked rows overflow on phones, no-art placeholder, leather tones (K6, K1, K2) |
| Quest Journal (07) | `07_journal.png` | ✅ [JournalScreen.md](JournalScreen.md) | ✅ sliced, island painting; uploaded | ✅ `Screens/JournalWindow`, `IslandMap` | ✅ claimable, claimed, side tabs (D12) | ✅ | ✅ `JournalController` (QuestView / QuestClaim); `journal_flow` | ✅ `journal_*_compare` | ✅ `journal_phone`; devices ⏳ | ✅ round 1 and 2 (no High) | Fix round 4: phone titles (K8) |
| Market, Trade, Progress, World map | none (restyle) | ✅ [ListWindows.md](ListWindows.md) | ✅ kit only | ✅ `Hud/ListWindow` on the kit | ✅ | ✅ | ✅ `WalletController`, `TradeController` (item art from server `catalogId`; invite toast with Accept / Decline, D22), `ProgressionController`, `MapController`; `market_flow`, `trade_flow`, `progress_flow`, `map_flow` | captures ✅ (no mockup) | devices ⏳ | ✅ round 1 and 2 (no High) | Fix round 4: ×20 open/close leak checks (W4) |
| In-world HUD | none (restyle) | ✅ [HudScreen.md](HudScreen.md) | ✅ kit only | ✅ `Vitals`, `BottomBar`, `PartyFrames`, `Compass`, `ObjectivePanel`, `EventPanel` | ✅ `world_hud_states` | ✅ bars ease | ✅ `HudController`; `world_hud_flow` | captures ✅ (no mockup) | ✅ `world_hud_phone`, `world_hud_wide`; devices ⏳ | ✅ round 1 and 2 (no High) | Fix round 4: phone event title vs timer, tribe frames vs thumbstick (W1, W3) |
| World overlays, notices, loot, storage, world menu | none (restyle) | ARCHITECTURE §4.8 | ✅ kit only | ✅ | ✅ | ✅ | ✅ `NoticeController`, `LootController` and `StorageController` (item art and rarity dot from server `catalogId`; takes by stable key with an in-flight guard, D22), `WorldMenuController`, …; `world_overlays_flow` | captures ✅ `world_overlays`, `notices`, `world_menu` | ✅ `world_overlays_phone`; devices ⏳ | ✅ round 1 and 2 (no High) | Fix round 4: world menu NotReady text (W2); loot rows show item art (V10 closed) |
| Atlases and upload | — | ARCHITECTURE §6 | ✅ `atlas_lk_lobby`, `atlas_lk_window`, `atlas_lk_icons`, `atlas_lk_items` uploaded, ids in `UiAssetIds.json` | — | — | — | — | `--uploaded-only` fallback pages ✅ | ⏳ | — | Uploaded; in-game look still to check on devices |
| Removal of the old UI (§9) | — | ARCHITECTURE §9 | — | — | — | — | — | — | — | — | 🔄 Old `Hud/LobbyHud`, `LobbyPopups`, `Parchment`, `ItemSlot`, `InventoryPanel`, `SettingsPanel`, `CraftingPanel`, `JournalPanel`, the HudLayout `lobby` section and the preview scripts are gone, and the deploy removes the old modules from the places (`RETIRED` in `scripts/roblox_live_publish.py`); legacy sprites and atlases stay until the `lk_` upload is live |

## Notes and blockers

- **Upload.** The four `atlas_lk_*` atlases are uploaded and their ids are in
  `src/shared/UI/UiAssetIds.json`; nothing may add, remove or change `lk_` sprites or
  atlas images without a new upload. How they draw on real devices is a manual check.
- **Captures, not Studio.** No Roblox Studio MCP server is connected to the build
  sessions, so every capture comes from `art/ui/capture/capture.py`, which runs
  the game's UI code headlessly (`gui_env.luau`) and renders it (`render.py`). The
  headless environment has no layout pass, blur, rotation or RichText sizes
  (ARCHITECTURE §7); those, device safe areas, real touch and gamepad focus are
  manual checks in [MANUAL_VALIDATION.md](../MANUAL_VALIDATION.md).
- **Verification.** Round 1: visual FAIL (2 High, 13 Medium), responsive FAIL
  (7 High, 11 Medium), code PASS. Round 2 (after fix round 3), whole-screen mean ΔE2000 / SSIM
  against the mockups: HUD 1.63 / 0.937, Inventory 7.07 / 0.898, Settings
  5.94 / 0.929, Party 6.01 / 0.944, Play 8.84 / 0.886, Forge 6.82 / 0.900,
  Journal 7.19 / 0.899 (whole-screen numbers include the world behind the veil and
  the stand-in art; per-element checks are in the reports). Responsive: world
  overlays reach at least 11 px text on phones with nothing off-screen, under the
  top bar or under 44 px touch targets (one text overflow at 844 and 667 wide, the
  event title, W1); the flow scenes pass, including ×20
  open/close checks of instances and connections where they exist. Remaining findings went to fix round 4: K (Kit and lobby screens,
  K1–K9), W (world, W1–W4) and S (server and docs: the party view on join, these
  docs, D23).
- **Device-only checks** (toast lane, SearchBox touch growth, top-bar and jump
  clearance, thumbstick vs tribe frames, lobby gamepad entry, party view on join,
  blur and motion) are listed in [MANUAL_VALIDATION.md](../MANUAL_VALIDATION.md).
- **Old specs.** `HudScreen.md`, `ListWindows.md`, `CraftingScreen.md` and parts of
  the screen specs still describe the parchment build or name removed modules; the
  analysts replace them (ARCHITECTURE §9).
