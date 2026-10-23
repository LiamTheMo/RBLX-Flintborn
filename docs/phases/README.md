# Flintborn development phases

[`GDD.md`](../../GDD.md) is the source of truth for gameplay intent. These phase documents split it into ordered, buildable versions. Each phase names the GDD rules it implements, the code it adds, how it is validated, and what it deliberately leaves for later. If a phase document and the GDD disagree, the GDD wins and the phase document must be corrected.

**Finished phases** are marked ✅. Their documents are deleted once the phase's CI, deployment and tests pass; any Studio checks still to run move to [`docs/MANUAL_VALIDATION.md`](../MANUAL_VALIDATION.md).

## Branch and release model

- Each phase is one **version branch** named after it (`v0.01`, `v0.02`, …). A version branch is kept permanently once complete.
- All work happens on short-lived minor branches cut from the active version branch, merged back into it, then merged into `main`.
- Only `main` publishes to Roblox (`.github/workflows/deploy.yml`). Version and minor branches only validate.
- A phase is finished when its **Exit criteria** pass, its automated checks are green on `main`, and its Studio checks have been run on the published place.

## Phase map

| Version | Phase | Builds on | Playable result |
| --- | --- | --- | --- |
| v0.01 ✅ | Project foundation and deployment pipeline | — | Repository, Rojo layout, CI and `main`-only publishing |
| v0.02 ✅ | Player data, persistence and session safety | v0.01 | Versioned profiles that save safely across servers |
| v0.03 ✅ | Lobby, protected world menu and Play admission | v0.02 | Lobby → teleport → safe menu → Play → random spawn |
| [v0.04](v0.04-survival-core.md) | Survival core: health, stamina, food and healing | v0.03 | Sprint, hunger, medicine and food heals |
| [v0.05](v0.05-gathering-inventory-and-field-crafting.md) | Gathering, inventory and field crafting | v0.04 | Harvest nodes, 9+50 inventory, craft first gear in ≤10 min |
| [v0.06](v0.06-combat-armor-and-pvp-rules.md) | Combat, armor and PvP rules | v0.05 | Melee, bows, EHP armor, PvP everywhere |
| [v0.07](v0.07-death-departure-tribes-and-revives.md) | Death, departure, tribes and revives | v0.06 | Corpses, logout loss, tribes, downed and revive, safe kicks |
| [v0.08](v0.08-extraction-lobby-backpack-and-vault.md) | Extraction, lobby backpack and secure vault | v0.07 | **First complete risk → loot → extract → vault loop** |
| [v0.09](v0.09-ancestral-forge-and-permanent-items.md) | Ancestral Forge and Permanent items | v0.08 | Special recipes and the first Permanent pickaxe |
| [v0.10](v0.10-building-totems-raiding-and-farming.md) | Building, totems, raiding and farming | v0.07 | Booga Booga bases, totems, decay, raids, crops |
| [v0.11](v0.11-world-event-director-and-rare-spawns.md) | World event director and rare spawns | v0.10 | Announced weighted events, rare nodes, ruins, caches |
| [v0.12](v0.12-bosses-guardian-and-scaling.md) | Bosses: Guardian and scalable encounters | v0.11 | Center Guardian and event, ritual and structure bosses |
| [v0.13](v0.13-account-progression-masteries-and-rebirth.md) | Account progression, masteries and rebirth | v0.08 | XP, levels, five masteries, rebirth tokens and perks |
| [v0.14](v0.14-economy-shops-trading-and-monetization.md) | Economy, shops, trading and monetization | v0.13 | Coins, Gems, NPC shops, quests, lobby trading, Premium |
| [v0.15](v0.15-shattered-crater-world-art-and-camera.md) | Shattered Crater world, art direction and camera | v0.11 | Full island, biomes, POIs, art pass, adjustable camera |
| [v0.16](v0.16-onboarding-ux-and-accessibility.md) | Onboarding, UX and accessibility | v0.14 | Guided tutorial, quests, polished UI on every input |
| [v0.17](v0.17-live-ops-hardening.md) | Live-ops hardening | v0.16 | Telemetry, anti-exploit, performance, crash recovery |
| [v0.18](v0.18-release-candidate-and-launch-readiness.md) | Release candidate and launch readiness | v0.17 | Launch-ready build, promoted to v1.00 |

Phases v0.10–v0.12 and v0.13–v0.14 depend only on the phases listed, so they may overlap in time if needed, but they are still merged in version order.

## Writing and maintaining a phase document

Every phase document uses the same sections:

1. **Objective** — the single outcome the phase proves.
2. **Player-facing result** — what a tester can see and do when it ships.
3. **Confirmed rules** — owner-approved GDD rules the code must follow exactly, with section and question references.
4. **Systems and modules** — services, controllers and shared modules, with their planned paths under `src/`.
5. **Data and persistence** — profile fields, receipts and server state touched.
6. **Security and anti-exploit** — what the server must never trust.
7. **UX and accessibility** — screens and cues, for desktop, touch and controller.
8. **Validation** — automated specs and Studio/manual checks.
9. **Exit criteria** — the checklist that closes the phase.
10. **Starting placeholders** — values the GDD leaves to tuning; use these until playtests say otherwise.
11. **Scope boundary** — what is intentionally deferred.

When a phase finishes, record any deviation from the GDD in the GDD's change log, not only in the phase document.
