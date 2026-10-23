# Flintborn

**Flintborn** is a Roblox primitive-fantasy survival sandbox / PvPvE extraction game. Gather and craft stone and metal gear, build and raid tribal bases, contest world events and ancient bosses, then extract loot into a persistent vault. Combat uses primitive melee weapons and crafted-arrow bows: **no firearms, player shields or player magic** at launch.

## Project documentation

- **[Game Design Document (GDD.md)](GDD.md)** — the source of truth for gameplay intent: pillars, core loop, systems, owner decisions and change log.
- **[Development phases (docs/phases)](docs/phases/README.md)** — the GDD split into ordered versions `v0.01` → `v0.18`, each with rules, modules, validation and exit criteria.
- **[Roblox live deployment](docs/roblox-live-deployment.md)** and **[cloud sync safety](docs/ROBLOX_CLOUD_SYNC.md)** — how `main` publishes scripts to the live place.

**Current phase:** [v0.08 — Extraction, lobby backpack and secure vault](docs/phases/v0.08-extraction-lobby-backpack-and-vault.md). Finished phases are listed in the [phase index](docs/phases/README.md); their documents are removed once CI, deployment and tests pass.

## Repository layout

| Path | Contents |
| --- | --- |
| `src/server` | Server entry point (`init.server.luau`), `Services/` and `Infrastructure/` (DataStore gateway, profile store, operation journal) → `ServerScriptService.Server` |
| `src/client` | Client entry point (`init.client.luau`) and `Controllers/` → `StarterPlayer.StarterPlayerScripts.Client` |
| `src/shared` | Shared modules (`Core/Loader`, `Core/Signal`, `GameConstants`, `Data/` profile rules, `Admission/` session and travel rules, `Config/PlaceConfig`, `Net/Remotes`) → `ReplicatedStorage.Shared` |
| `src/assets` | Models and images → `ReplicatedStorage.Assets` |
| `src/maps` | World layouts → `ServerStorage.Maps` |
| `tests/luau` | Headless Luau specs for shared modules and server modules with injected fakes |
| `tests/test_cloud_live_publish.py` | Offline publish-safety tests |
| `scripts/` | Open Cloud script mapping and live publishing |

## Code conventions

- One responsibility per Service (`src/server/Services/<Name>Service.luau`) and Controller (`src/client/Controllers/<Name>Controller.luau`). The Loader picks up every module in those folders, so adding one is just adding a file.
- Pure rules and catalogs live in `src/shared` so the server, client and headless specs share one definition. Tunable values live in shared config modules, never scattered literals.
- The server is authoritative (GDD §12.1). Clients send intent only and never decide risk, combat, inventory, crafting, extraction or persistence.
- Format with StyLua (`stylua src tests/luau`). Selene uses the `roblox` standard library.

## Local development

Tools are pinned in `rokit.toml` (`rokit install`).

```sh
rojo serve                                   # live-sync into Roblox Studio
python3 scripts/roblox_cloud_sync.py --check # list script mappings
stylua --check src tests/luau                # formatting
python3 tests/luau/run.py                    # Luau specs (needs the luau CLI)
python3 -m unittest discover -s tests -p 'test_cloud_live_publish.py'
rojo build default.project.json --output build/validation.rbxlx
```

## Branches and deployment

- `main` is the deployed state. Version branches (`v0.01`, `v0.02`, …) are permanent phase checkpoints. All work happens on short-lived branches merged into the active version branch, then into `main`.
- `.github/workflows/deploy.yml` validates every pull request and every push to `main` or a version branch. **Only pushes to `main` publish**, to both places in the universe: the play map (`ROBLOX_MAIN_PLACE_ID`) and the lobby (`ROBLOX_LOBBY_PLACE_ID`), using the `ROBLOX_API_KEY` and `ROBLOX_UNIVERSE_ID` repository secrets.
