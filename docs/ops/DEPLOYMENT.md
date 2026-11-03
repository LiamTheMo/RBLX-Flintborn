# Deployment: GitHub → the live places

Local development uses **Rojo** against Roblox Studio. The release workflow
(`.github/workflows/deploy.yml`) publishes **only from `main`**: it updates the
Git-managed scripts *inside the latest published version* of each place through
Open Cloud **Luau Execution**, then saves the place with
`AssetService:SavePlaceAsync`. It never uploads a Rojo-built place.

## Who owns what

| Owner | Contents | How it reaches the live places |
| --- | --- | --- |
| Git (`src/server`, `src/client`, `src/shared`) | Scripts and JSON modules, mapped by `default.project.json` | The release, on every push to `main` |
| Studio | World geometry, terrain, models, lighting, hand-made UI, every other non-script instance | Publish from Studio |
| Git (`src/assets`, `src/maps`) | Models and images (`ReplicatedStorage.Assets`), map models (`ServerStorage.Maps`) | Rojo sync into Studio, then publish from Studio; never the release |
| Git (`art/roblox`, `art/ui/sprites`) | The lobby map, the player character, the UI sprites | The [manual asset workflows](#manual-asset-workflows) |

## One-time setup

1. In Studio, make a backup with **File → Save to File**, publish the
   up-to-date maps, models and assets to the production place, and connect Rojo
   once so `ServerScriptService/Server`, `ReplicatedStorage/Shared` and
   `StarterPlayer/StarterPlayerScripts/Client` exist in that place. The release
   never creates these roots.
2. Creator Dashboard → Experiences → the game → Places → the place →
   **Permissions**: enable **Allow place to be updated using Save Place API**.
   Close any Team Create session before a release.
3. Creator Dashboard → **Credentials**: create an Open Cloud API key with
   **Luau execution session task write**
   (`universe.place.luau-execution-session:write`) for this experience.
4. Set the GitHub Actions secrets `ROBLOX_API_KEY`, `ROBLOX_UNIVERSE_ID`,
   `ROBLOX_MAIN_PLACE_ID` (the play world) and `ROBLOX_LOBBY_PLACE_ID` (the
   lobby). Never commit credentials. Steps 1 and 2 apply to both places.

## The release

`deploy.yml` validates every pull request and every push to `main` or a version
branch (`v0.19`, …): the mapping checks, StyLua, the Luau specs, the Python tests
and a Rojo build (see [Local checks](#local-checks)). **Only a push to `main`
publishes.** The `deploy` job then runs once per place (matrix `main`, `lobby`,
one at a time because both share the key's rate limit):

- It writes `src/shared/Generated/PlaceIds.luau` from the two place-ID secrets so
  each place knows whether it is the lobby or the play world (git-ignored; in
  Studio, set the workspace attribute `FlintbornPlaceRole` to `Lobby` or `World`
  instead, default `World`), sets `ROBLOX_PLACE_ID` to that job's place, and runs
  `python3 scripts/roblox_live_publish.py --deploy`.
- The publisher maps every script and JSON module under the three roots, rejects
  class collisions and non-code ancestors, creates only missing code instances
  inside the approved roots, and updates only `Source`.
- Roblox refuses a Luau Execution task script over 1 MiB, so the release goes up
  in **batches** of at most 900 KB. Every batch's mapping is validated before the
  first batch writes anything; the batches then apply and save in order, and
  every batch is verified against the latest published place at the end. If a
  batch fails part-way, the earlier batches are already saved: re-run the deploy
  to finish (a batch only writes sources that differ).
- **JSON modules** (`*.json` under the roots, except `*.project.json`,
  `*.meta.json` and `*.model.json`) are published as ModuleScripts named after the
  file, whose `Source` is the JSON converted to a Luau table (`return {...}`), as
  Rojo does. Publish and verify both compare against that converted source. The
  JSON must be strict: comments or trailing commas stop the release.
- **Every save strips the engine's default player scripts** (`SAVE_PLACE` in
  `roblox_live_publish.py`): each Luau task's server inserts a `PlayerModule`
  into `StarterPlayer` and `RbxCharacterSounds` into `StarterPlayerScripts`, and
  saving them piled up copies until the lobby grew past what a cloud save can
  upload. Servers insert their own copies, so the place keeps none.

### Deleting or moving a script: `RETIRED`

The release never deletes Studio objects on its own. A Luau module deleted from
Git, or moved, would keep running in the places with its last published source,
and the Loader runs every module in `Services/` and `Controllers/`. So **add the
old instance path of every deleted or moved module to `RETIRED` in
`scripts/roblox_live_publish.py`**. The last batch destroys each listed path,
only at that exact path and only if a script is what is there.
`roblox_live_publish.py --check` (run by CI) refuses a `RETIRED` path outside the
managed roots or one that Git still publishes.

### Limits and recovery

- Studio-managed geometry, terrain, models, lighting and UI are never targeted,
  but the headless task loads the live game: startup scripts that change the
  world can still have side effects on a full-place save. Test a risky release on
  a separate place first.
- The task works from the **latest published** place, not unpublished Studio
  edits. After changing map or asset content in Studio, publish it from Studio
  before the next release, or those edits are not guaranteed to survive.
- GitHub cannot bypass Roblox's Team Create restriction on `SavePlaceAsync`: a
  blocked save fails the workflow; close the Studio session and re-run.
- Code changes reach **new servers**; running servers keep the old code until
  they restart.
- A failed or partly completed task needs a look at the place's version history
  in the Creator Dashboard before retrying.
- Roll back a bad publish from the Creator Dashboard's place version history,
  then fix the code on a new branch. Never fix production by editing `main`
  directly.
- No package manager is used. Shipping Wally packages would need the release
  extended to publish `ReplicatedStorage/Packages` first.

## Script mapping: `roblox_cloud_sync.py`

`scripts/roblox_cloud_sync.py` is the mapping library the release and the tests
share: `discover()` maps files to instance paths with Rojo's `*.server.luau`,
`*.client.luau`, `*.luau` and `init.*` conventions, `local_source()` reads a file
(converting a JSON module with `json_to_luau()`), and `luau_string()` quotes text
for Luau. `roblox_live_publish.py`, `roblox_common.py` and `tests/luau/run.py`
import it.

`python3 scripts/roblox_cloud_sync.py --check` lists every mapping offline and is
what CI runs. The script also keeps an **optional manual tool** that CI never
runs: with `ROBLOX_API_KEY`, `ROBLOX_UNIVERSE_ID` and `ROBLOX_PLACE_ID` set and a
key for the Open Cloud Engine Instance API (`universe-place-instances`, read and
write), `--dry-run` runs a read-only preflight and lists what would change, and
`--deploy` updates the `Source` of scripts that already exist. It never creates,
deletes or publishes anything: the change goes live only when the place is
published. The Engine Instance API is beta, limits an update to 200 KB, and
cannot edit a script open in Studio or inside a package.

## Manual asset workflows

Each runs only when started by hand (**Actions → workflow → Run workflow**).
They never commit: the asset ids come back as a workflow artifact for a person
to commit through the normal branch → version branch → `main` flow. Modes that
**save a live place are deploys, so they run only from `main`** (and share the
release's lock, so a release and a place save never overlap); uploads and
read-only modes run from any branch.

| Workflow | Script | Modes (main-only in bold) | Secrets | Artifact |
| --- | --- | --- | --- | --- |
| `lobby-map.yml` Upload and place the lobby map | `roblox_lobby_map.py` | `inspect`, `diagnose`, `uiprobe` (read-only), `upload`, **`place`**, **`lighting`**, **`all`** | uploads: `ROBLOX_ASSETS_API_KEY` (falls back to `ROBLOX_API_KEY`) and the creator; place tasks: `ROBLOX_API_KEY`, `ROBLOX_UNIVERSE_ID`, `ROBLOX_LOBBY_PLACE_ID` | `lobby-asset-ids`: `art/roblox/lobby/asset_ids.json` |
| `character.yml` Upload and install the player character | `roblox_character.py` | `upload`, `probe` (read-only, lobby), **`install`**, **`all`** (both places) | as above, plus `ROBLOX_MAIN_PLACE_ID` | `character-asset-ids`: `art/roblox/character/asset_ids.json` |
| `upload-ui-assets.yml` Upload HUD sprites to Roblox | `roblox_upload_ui_assets.py` | dry run (default), `upload`, `inspect <id>`, `resolve`; never touches a place | `ROBLOX_ASSETS_API_KEY` (falls back to `ROBLOX_API_KEY`) and the creator | `ui-asset-ids`: `src/shared/UI/UiAssetIds.json`, `art/ui/uploaded_decals.json` |
| `probe-ui-assets.yml` Probe UI images in a live place | `roblox_probe_ui_assets.py` | **every mode** (the whole job is main-only): `--names`, `--reports`; read-only, nothing saved | `ROBLOX_API_KEY`, `ROBLOX_UNIVERSE_ID`, `ROBLOX_LOBBY_PLACE_ID` or `ROBLOX_MAIN_PLACE_ID` | none (the job log) |

**The creator** owns uploaded assets and must own the experience so the places
can load them. With `creator: group` the workflows pass `ROBLOX_CREATOR_ID` (the
owning group's id; the older `ROBLOX_CREATOR_GROUP_ID`, then
`ROBLOX_CREATOR_USER_ID`, are fallbacks) as `ROBLOX_CREATOR_GROUP_ID`; with
`creator: user` they pass `ROBLOX_CREATOR_USER_ID`. `ROBLOX_ASSETS_API_KEY` is an
Open Cloud key with asset write permission, for example one created under the
group; `resolve` also needs the `legacy-asset:manage` scope.

The character's clothing materials need one more Studio step that Open Cloud
cannot do: `scripts/studio/character_materials.luau` (regenerate it with
`python3 scripts/roblox_character.py --studio-script`) is pasted into each
place's command bar, then the place is published. Re-running the install puts
the plain textures back.

## Local checks

Never run `--deploy` or the upload scripts with real credentials locally; the
workflows do that.

```sh
python3 scripts/roblox_cloud_sync.py --check
python3 scripts/roblox_live_publish.py --check
python3 -m unittest discover -s tests -p 'test_*.py'
rojo build default.project.json --output build/validation.rbxlx
```

The `.rbxlx` build (in the git-ignored `build/`) is **validation only**, never
uploaded. The full list of checks CI runs is in the
[README](../../README.md#checks).

References:
- https://create.roblox.com/docs/cloud/reference/features/luau-execution
- https://create.roblox.com/docs/reference/engine/classes/AssetService
- https://devforum.roblox.com/t/saveplaceasync-now-supports-all-places/3805169
- https://create.roblox.com/docs/cloud/guides/instance
