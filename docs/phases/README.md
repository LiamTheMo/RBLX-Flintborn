# Flintborn development phases

[`GDD.md`](../../GDD.md) is the source of truth for gameplay intent. These phase documents split it into ordered, buildable versions. Each phase names the GDD rules it implements, the code it adds, how it is validated, and what it deliberately leaves for later. If a phase document and the GDD disagree, the GDD wins and the phase document must be corrected.

**Finished phases** are marked ✅. Their documents are deleted once the phase's CI, deployment and tests pass; any Studio checks still to run move to [`docs/MANUAL_VALIDATION.md`](../MANUAL_VALIDATION.md). All 18 phases are shipped; promotion to `v1.00` follows [`docs/RELEASE_CHECKLIST.md`](../RELEASE_CHECKLIST.md).

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
| v0.04 ✅ | Survival core: health, stamina, food and healing | v0.03 | Sprint, hunger, medicine and food heals |
| v0.05 ✅ | Gathering, inventory and field crafting | v0.04 | Harvest nodes, 9+50 inventory, craft first gear in ≤10 min |
| v0.06 ✅ | Combat, armor and PvP rules | v0.05 | Melee, bows, EHP armor, PvP everywhere |
| v0.07 ✅ | Death, departure, tribes and revives | v0.06 | Corpses, logout loss, tribes, downed and revive, safe kicks |
| v0.08 ✅ | Extraction, lobby backpack and secure vault | v0.07 | **First complete risk → loot → extract → vault loop** |
| v0.09 ✅ | Ancestral Forge and Permanent items | v0.08 | Special recipes and the first Permanent pickaxe |
| v0.10 ✅ | Building, totems, raiding and farming | v0.07 | Booga Booga bases, totems, decay, raids, crops |
| v0.11 ✅ | World event director and rare spawns | v0.10 | Announced weighted events, rare nodes, ruins, caches |
| v0.12 ✅ | Bosses: Guardian and scalable encounters | v0.11 | Center Guardian and event, ritual and structure bosses |
| v0.13 ✅ | Account progression, masteries and rebirth | v0.08 | XP, levels, five masteries, rebirth tokens and perks |
| v0.14 ✅ | Economy, shops, trading and monetization | v0.13 | Coins, Gems, NPC shops, quests, lobby trading, Premium |
| v0.15 ✅ | Shattered Crater world, art direction and camera | v0.11 | Full island, biomes, POIs, art pass, adjustable camera |
| v0.16 ✅ | Onboarding, UX and accessibility | v0.14 | Guided tutorial, quests, polished UI on every input |
| v0.17 ✅ | Live-ops hardening | v0.16 | Telemetry, anti-exploit, performance, crash recovery |
| v0.18 ✅ | Release candidate and launch readiness | v0.17 | Launch-ready build, promoted to v1.00 |

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
