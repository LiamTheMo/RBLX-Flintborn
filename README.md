# Flintborn

**Flintborn** is a Roblox primitive-fantasy survival sandbox / PvPvE extraction game. Gather and craft stone and metal gear, build and raid tribal bases, contest world events and ancient bosses, then extract loot into a persistent vault. Combat uses primitive melee weapons and crafted-arrow bows: **no firearms, player shields or player magic** at launch.

## Project documentation

Every document is listed in **[docs/README.md](docs/README.md)**, marked current, design record or history. Start with:

- **[Game Design Document](docs/design/GDD.md)** — the source of truth for gameplay intent: pillars, core loop, systems, owner decisions and change log.
- **[Development phases](docs/phases/README.md)** — the GDD split into ordered versions `v0.01` → `v0.19`, and the branch model.
- **[Releasing](docs/ops/DEPLOYMENT.md)** — how a change reaches the live places: VS Code → Rojo → Studio → publish.
- **[Map designs](docs/maps/README.md)** — the lobby hub (built) and the shared map conventions; the Shattered Crater's document is not started.
- **[Release checklist](docs/release/RELEASE_CHECKLIST.md)** and **[manual validation](docs/release/MANUAL_VALIDATION.md)** — what remains before the permanent `v1.00` branch.
- **[UI style guide](docs/ui/STYLE_GUIDE.md)** — the entry point for any UI work.

**Current phase:** v0.19, the first fully playable build: placeholder models for every item, node, creature, event and structure, and click to chop, mine and gather (GDD §58). Phases v0.01–v0.18 are shipped and deployed. Next: the manual [release checklist](docs/release/RELEASE_CHECKLIST.md), then the permanent `v1.00` branch. Finished phases are listed in the [phase index](docs/phases/README.md); their documents are removed once CI, deployment and tests pass.

## Repository layout

| Path | Contents |
| --- | --- |
| `src/server` | Server entry point (`init.server.luau`) → `ServerScriptService.Server`. `Services/` (one singleton per responsibility, run by the Loader), `Infrastructure/` (DataStore gateway, profile store, operation journal, checkpoint store, `RequestLedger` and `Cooldown` request guards), `WorldBuild/` (the placeholder island's terrain, landmarks, safe camps and scenery, built by `WorldBuildService`), `Config/` (admins, codes) |
| `src/client` | Client entry point (`init.client.luau`) → `StarterPlayer.StarterPlayerScripts.Client`. `Controllers/` (run by the Loader), `Hud/` (HUD pieces, `Kit/` UI components, `Screens/` windows), `Ui/` (binds, reasons, theme) |
| `src/shared` | Pure rules, catalogs and models shared by server, client and specs → `ReplicatedStorage.Shared`, one folder per domain (`Admission`, `Combat`, `Crafting`, `Data`, `Economy`, `Items`, `Net/Remotes`, `UI`, `Visuals`, `World`, …), plus `Core/Loader`, `Core/Signal`, `GameConstants` and `Config/PlaceConfig`. JSON files here are published as ModuleScripts |
| `tests/luau` | Headless Luau specs (`*.spec.luau`) for shared modules and server modules with injected fakes; `run.py` bundles them with `prelude.luau` stubs |
| `tests/test_*.py` | Python tests: the spec runner, the UI upload script |
| `scripts/` | `roblox_cloud_sync.py` (script mapping), `roblox_upload_ui_assets.py` (UI sprite records and uploads) and `studio/` (a command-bar script) |
| `art/` | Source art: `blender/` (build scripts, `.blend` sheets, renders, the world kit, the lobby), `roblox/` (exported meshes and textures to import in Studio), `ui/` (sprites, kit slicing, item icons, headless UI captures), `reference/` (concept and reference images), `character/`, `vfx/` |
| `docs/` | Design, art, UI, maps, phases, release and operations documents ([index](docs/README.md)) |

## Code conventions

- One responsibility per Service (`src/server/Services/<Name>Service.luau`) and Controller (`src/client/Controllers/<Name>Controller.luau`). The Loader picks up every module in those folders, so adding one is just adding a file.
- Pure rules and catalogs live in `src/shared` so the server, client and headless specs share one definition. Tunable values live in shared config modules, never scattered literals.
- The server is authoritative (GDD §12.1). Clients send intent only and never decide risk, combat, inventory, crafting, extraction or persistence.
- Format with StyLua (`stylua src tests/luau`).
## Local development

Tools:

- **Rojo** is pinned in `aftman.toml`: `aftman install`.
- **StyLua 2.6.0** and the **Luau CLI 0.739.0** are installed with cargo:
  `cargo install stylua --version 2.6.0 --features luau --locked` and `cargo install luau-cli --version 0.739.0 --locked`.
- **Python 3** for the scripts and tests (standard library only).
- **Selene** is optional; `selene.toml` sets the `roblox` standard library.

```sh
rojo serve                                   # live-sync into Roblox Studio
```

### Checks

No CI runs these, so run them before merging:

```sh
python3 scripts/roblox_cloud_sync.py --check    # script mappings
stylua --check src tests/luau                   # formatting
python3 tests/luau/run.py                       # every Luau spec (needs the luau CLI)
python3 -m unittest discover -s tests -p 'test_*.py'
rojo build default.project.json --output build/validation.rbxlx
```

## Branches and releasing

- `main` is the released state. Version branches (`v0.01`, `v0.02`, …) are permanent phase checkpoints. All work is committed straight to the active (most recent) version branch in small, frequent commits, with no feature branches (owner's decision, 2026-11-04). The version branch is merged into `main` to release.
- Nothing publishes from GitHub. A release is `main` synced with Rojo into each place in Studio (the lobby and the play world) and published from Studio. Steps, the place IDs and how art is imported are in [DEPLOYMENT.md](docs/ops/DEPLOYMENT.md).
