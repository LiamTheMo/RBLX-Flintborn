# Flintborn v1.00 release checklist

Phase v0.18 (release candidate) ships the automated part: the complete CI suite on `main` (Luau specs including the GDD §24 security suite and profile migrations, publish-safety tests and the Rojo build) passes, and both places are deployed and verified. Promotion to the permanent `v1.00` branch waits for the manual items below. Mark each one when it passes.

## 1. Regression lists on the published place

Run every Studio and live check in `docs/MANUAL_VALIDATION.md` (v0.01–v0.17) on the published places. These cover the GDD regression lists in §27.1, §31.7, §34.4, §35.4, §36.6, §37.4, §38.4, §39.6, §41.3 and §42.3.

- [ ] All manual checks pass on the published lobby and world places.
- [ ] The post-release hardening checks in [`MANUAL_VALIDATION.md`](MANUAL_VALIDATION.md#post-release-hardening-after-v018) pass, especially movement rubber-banding on a real network.

## 2. Playtests (GDD §27.2)

- [ ] Fresh solo onboarding from spawn through first extraction and first special recipe.
- [ ] Testers can explain **Vaulted vs Permanent**.
- [ ] Tutorial completed on desktop, touch and controller without help.
- [ ] Colour-blind simulation pass on every screen.

## 3. Soak test

- [ ] 30 players for two or more hours: no data loss, stable server memory, heartbeat at least 50 Hz.

## 4. Device smoke tests

- [ ] Mobile (mid-range), desktop and console: Play, gather, craft, fight, build, extract, vault, Forge, market and trade.
- [ ] At least 30 FPS on a mid-range phone in a full server.

## 5. Drills

- [ ] Crash-recovery drill: stop a test world server mid-fight; on rejoin the lobby shows "Server crashed — your items were recovered" and the items return once.
- [ ] Ordinary quit mid-fight: no recovery (a body is left instead).
- [ ] Rollback drill: restore a previous place version from the Creator Dashboard, then republish `main`.

## 6. Economy telemetry

- [ ] Creator Dashboard analytics show the custom events (runs, actions, releases) and Coin/Gem economy events.
- [ ] Earnings per active hour near the targets (~10,000 Coins, ~100 Gems) and the §26.2 healthy signals.

## 7. Platform, store and security

- [ ] Developer product IDs set in `src/shared/Economy/OfferCatalog.luau`; each purchase tested in a test place.
- [ ] Roblox paid-random-item and Premium policy reviewed (§38.1); every paid benefit has its earnable route (enforced by spec).
- [ ] Redemption codes in `src/server/Config/Codes.luau` reviewed (remove any not meant for launch).
- [ ] Admin allowlist in `src/server/Config/Admins.luau` reviewed.
- [ ] Repository secrets confirmed; rotate `ROBLOX_API_KEY` if it was ever shared.
- [ ] Store page: icon, thumbnails, description and the age/content questionnaire.
- [ ] Decision recorded: keep or reset the playtest profile DataStore (`ProfileService.STORE_NAME`).
- [ ] The authored Shattered Crater map (if ready) placed in the world place as a `ShatteredCrater` model; the generated placeholder steps aside automatically.

## 8. Promotion

- [ ] GDD §13.2 documentation checklist ticked.
- [ ] `v0.18` merged to `main`, deployed and verified (done by CI on every release).
- [ ] Create the permanent `v1.00` branch from that `main` commit and add the launch entry to the GDD change log (§43).
