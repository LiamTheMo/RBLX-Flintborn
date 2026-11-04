# Releasing: VS Code → Rojo → Studio → the live places

Every change reaches Roblox through **Rojo and Studio**. Code is edited in VS
Code, Rojo (installed with Aftman, `aftman.toml`) syncs it into the open place in
Studio, and the place goes live when it is published from Studio. The repository
has no GitHub workflows. (Until 2026-11-03, workflows published `main` and
installed the lobby map and the character through Open Cloud; they were removed,
and are in the Git history.)

## Who owns what

| Owner | Contents | How it reaches the live places |
| --- | --- | --- |
| Git (`src/server`, `src/client`, `src/shared`) | Scripts and JSON modules, mapped by `default.project.json` | Rojo sync into Studio, then publish from Studio |
| Studio | World geometry, terrain, the lobby map, the player character, lighting, hand-made UI, every other non-script instance | Publish from Studio |
| Git (`art/roblox`, `art/ui`) | Exported meshes and textures, UI sprites and their recorded asset ids | Imported or uploaded through Studio (see [Art and images](#art-and-images)) |

## The two places

The universe has two places (GDD Q163). Their IDs are in
`src/shared/Config/PlaceIds.luau`; `PlaceConfig` tells the places apart by them
and `TravelService` teleports between them.

| Place | Place ID |
| --- | --- |
| Lobby | 134617527037631 |
| Play world | 94130042056743 |

Both places use the same Rojo project, so a code change has to be synced into and
published from **each** place. A place file opened under another ID (a local copy
or a test place) falls back to the workspace attribute `FlintbornPlaceRole`
(`Lobby` or `World`), and Studio defaults to `World`. Teleports never run in
Studio.

## Releasing a change

1. Make the change on a minor branch, check it (see [Local checks](#local-checks)),
   and merge it through the version branch into `main` as usual.
2. Check out `main` locally, so what Rojo syncs is what was released.
3. Start the Rojo server from VS Code (or `rojo serve`), open the **lobby** place
   in Studio, and connect the Rojo plugin.
4. Test in Studio, then **File → Publish to Roblox**.
5. Do the same for the **play world** place.
6. Check the change in a **new server**. Running servers keep the old version
   until they restart.

Notes:

- Rojo mirrors the folders it maps (`Server`, `Shared`, `Client`, `Assets`,
  `Maps`). A module deleted or moved in Git disappears from Studio on the next
  sync, so nothing has to be retired by hand.
- Everything else in the place belongs to Studio, and Rojo never touches it.
  Publishing from Studio publishes those Studio edits too.
- Close Team Create edits that touch the synced folders before syncing, so
  nobody's script edits are overwritten.
- Roll back a bad publish from the Creator Dashboard's place version history,
  then fix the code on a new branch.
- No package manager is used. Wally packages would need a `Packages` entry in
  `default.project.json`.

## Art and images

- **Meshes and textures** (the lobby map, kit models, the character) are exported
  to `art/roblox/` by the Blender scripts and imported into the place in Studio
  (3D Importer or Asset Manager → Bulk Import), then published.
- **UI images**: `scripts/roblox_upload_ui_assets.py` keeps the sprite records.
  `--sprites` regenerates `src/shared/UI/UiSprites.json` and the default dry run
  lists what is not uploaded yet; both are local and need no key. Upload the
  images either in Studio (Asset Manager → Bulk Import, then write each image's
  id into `src/shared/UI/UiAssetIds.json`) or with the script's `--upload` mode,
  which needs an Open Cloud key with asset write permission in `ROBLOX_API_KEY`
  and `ROBLOX_CREATOR_USER_ID` or `ROBLOX_CREATOR_GROUP_ID`. The uploader must own
  the experience (or its group), so the places can load the images. Never commit
  a key.
- **Character clothing materials**: `scripts/studio/character_materials.luau` is
  pasted into each place's command bar, then the place is published.

## Script mapping: `roblox_cloud_sync.py`

`scripts/roblox_cloud_sync.py` maps files to instance paths with Rojo's
`*.server.luau`, `*.client.luau`, `*.luau` and `init.*` conventions (`discover()`),
reads a file, converting a JSON module with `json_to_luau()` as Rojo does
(`local_source()`), and quotes text for Luau (`luau_string()`). The Luau spec
runner (`tests/luau/run.py`) and the UI capture harness use it.
`python3 scripts/roblox_cloud_sync.py --check` lists every mapping offline.

## Local checks

No CI runs these, so run them before merging:

```sh
python3 tests/luau/run.py
stylua --check src tests/luau
python3 scripts/roblox_cloud_sync.py --check
python3 -m unittest discover -s tests -p 'test_*.py'
rojo build default.project.json --output build/validation.rbxlx
```

The `.rbxlx` build (in the git-ignored `build/`) is validation only.

References:
- https://rojo.space/docs/v7/
- https://create.roblox.com/docs/projects/assets/manager
