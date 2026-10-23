# Flintborn

**Flintborn** is a Roblox primitive-fantasy survival sandbox / PvPvE extraction game. Gather and craft stone and metal gear, build and raid tribal bases, contest world events and ancient bosses, then extract loot into a persistent vault. Combat uses primitive melee weapons and crafted-arrow bows: **no firearms, player shields or player magic** at launch.

## Project documentation

- **[Game Design Document (GDD.md)](GDD.md)** — the source of truth for gameplay intent: pillars, core loop, systems, owner decisions and change log.
- **[Development phases (docs/phases)](docs/phases/README.md)** — the GDD split into ordered versions `v0.01` → `v0.18`, each with rules, modules, validation and exit criteria.
- **[Roblox live deployment](docs/roblox-live-deployment.md)** and **[cloud sync safety](docs/ROBLOX_CLOUD_SYNC.md)** — how `main` publishes scripts to the live place.

**Current phase:** [v0.01 — Project foundation and deployment pipeline](docs/phases/v0.01-project-foundation-and-deployment.md).

## Repository layout

| Path | Contents |
| --- | --- |
| `src/server` | Server entry point (`init.server.luau`) and `Services/` → `ServerScriptService.Server` |
| `src/client` | Client entry point (`init.client.luau`) and `Controllers/` → `StarterPlayer.StarterPlayerScripts.Client` |
| `src/shared` | Shared modules (`Core/Loader`, `Core/Signal`, `GameConstants`) → `ReplicatedStorage.Shared` |
| `src/assets` | Models and images → `ReplicatedStorage.Assets` |
| `src/maps` | World layouts → `ServerStorage.Maps` |
| `tests/luau` | Headless Luau specs for pure shared modules |
| `tests/test_cloud_live_publish.py` | Offline publish-safety tests |
| `scripts/` | Open Cloud script mapping and live publishing |

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
- `.github/workflows/deploy.yml` validates every pull request and every push to `main` or a version branch. **Only pushes to `main` publish**, using the `ROBLOX_API_KEY`, `ROBLOX_UNIVERSE_ID` and `ROBLOX_PLACE_ID` repository secrets.
