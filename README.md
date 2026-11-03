# Flintborn

**Flintborn** is a Roblox primitive-fantasy survival sandbox / PvPvE extraction game. Gather and craft stone and metal gear, build and raid tribal bases, contest world events and ancient bosses, then extract loot into a persistent vault. Combat uses primitive melee weapons and crafted-arrow bows: **no firearms, player shields or player magic** at launch.

## Project documentation

Every document is listed in **[docs/README.md](docs/README.md)**, marked current, design record or history. Start with:

- **[Game Design Document](docs/design/GDD.md)** — the source of truth for gameplay intent: pillars, core loop, systems, owner decisions and change log.
- **[Development phases](docs/phases/README.md)** — the GDD split into ordered versions `v0.01` → `v0.19`, and the branch model.
- **[Deployment](docs/ops/DEPLOYMENT.md)** — how `main` publishes scripts to the live places, and the manual asset workflows.
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
| `src/assets` | Models and images → `ReplicatedStorage.Assets` ([README](src/assets/README.md)) |
| `src/maps` | Authored map models → `ServerStorage.Maps` (empty today; the island is generated) |
| `tests/luau` | Headless Luau specs (`*.spec.luau`) for shared modules and server modules with injected fakes; `run.py` bundles them with `prelude.luau` stubs |
| `tests/test_*.py` | Python tests: publish safety, the JSON-to-Luau literals, the spec runner, the UI upload script |
| `scripts/` | `roblox_cloud_sync.py` (script mapping), `roblox_live_publish.py` (the release), the manual asset tools (`roblox_lobby_map.py`, `roblox_character.py`, `roblox_upload_ui_assets.py`, `roblox_probe_ui_assets.py`, shared helpers in `roblox_common.py`) and `studio/` (a command-bar script) |
| `art/` | Source art: `blender/` (build scripts, `.blend` sheets, renders, the world kit, the lobby), `roblox/` (exported meshes and textures the workflows upload), `ui/` (sprites, kit slicing, item icons, headless UI captures), `reference/` (concept and reference images), `character/`, `vfx/` |
| `docs/` | Design, art, UI, maps, phases, release and operations documents ([index](docs/README.md)) |
| `.github/workflows` | `deploy.yml` (validate everywhere, publish from `main`) and the manual asset workflows |

## Code conventions

- One responsibility per Service (`src/server/Services/<Name>Service.luau`) and Controller (`src/client/Controllers/<Name>Controller.luau`). The Loader picks up every module in those folders, so adding one is just adding a file.
- Pure rules and catalogs live in `src/shared` so the server, client and headless specs share one definition. Tunable values live in shared config modules, never scattered literals.
- The server is authoritative (GDD §12.1). Clients send intent only and never decide risk, combat, inventory, crafting, extraction or persistence.
- Format with StyLua (`stylua src tests/luau`).
- **Deleting or moving a Luau module:** add its old instance path to `RETIRED` in `scripts/roblox_live_publish.py`. The release never deletes scripts on its own, so without it a stale copy keeps running in the places, and the Loader runs everything in `Services/` and `Controllers/` ([DEPLOYMENT.md](docs/ops/DEPLOYMENT.md#deleting-or-moving-a-script-retired)).

## Local development

Tools:

- **Rojo** is pinned in `rokit.toml`: `rokit install`.
- **StyLua 2.6.0** and the **Luau CLI 0.739.0** are installed with cargo, as CI does:
  `cargo install stylua --version 2.6.0 --features luau --locked` and `cargo install luau-cli --version 0.739.0 --locked`.
- **Python 3** for the scripts and tests (standard library only).
- **Selene** is optional and not run in CI; `selene.toml` sets the `roblox` standard library.

```sh
rojo serve                                   # live-sync into Roblox Studio
```

### Checks

The same checks CI runs (`.github/workflows/deploy.yml`):

```sh
python3 scripts/roblox_cloud_sync.py --check    # script mappings
python3 scripts/roblox_live_publish.py --check  # release batches and RETIRED paths
stylua --check src tests/luau                   # formatting
python3 tests/luau/run.py                       # every Luau spec (needs the luau CLI)
python3 -m unittest discover -s tests -p 'test_*.py'
rojo build default.project.json --output build/validation.rbxlx
```

Never run `roblox_live_publish.py --deploy` or the upload scripts with real credentials locally; the workflows do that.

## Branches and deployment

- `main` is the deployed state. Version branches (`v0.01`, `v0.02`, …) are permanent phase checkpoints. All work happens on short-lived branches merged into the active version branch, then into `main`.
- `.github/workflows/deploy.yml` validates every pull request and every push to `main` or a version branch. **Only pushes to `main` publish**, to both places in the universe: the play map (`ROBLOX_MAIN_PLACE_ID`) and the lobby (`ROBLOX_LOBBY_PLACE_ID`), using the `ROBLOX_API_KEY` and `ROBLOX_UNIVERSE_ID` repository secrets. Details, and the manual asset workflows, are in [DEPLOYMENT.md](docs/ops/DEPLOYMENT.md).
