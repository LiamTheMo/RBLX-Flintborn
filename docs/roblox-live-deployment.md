# Roblox GitHub → live place (scripts only)

Local development uses **Rojo** against Roblox Studio. The GitHub Actions release
workflow runs **only from `main`**, after repository validation, and uses Open
Cloud **Luau Execution** to update Git-managed scripts *inside the latest
published Roblox place*. It does **not** upload a Rojo-generated whole place.

## One-time setup per repository

1. In Studio, make a backup with **File → Save to File**, publish your
   up-to-date maps/models/assets to the intended production **Place ID**, and
   connect Rojo once so `ServerScriptService/Server`,
   `ReplicatedStorage/Shared`, and `StarterPlayer/StarterPlayerScripts/Client`
   exist in that place.
2. Creator Dashboard → Experiences → select your game → Places → select the
   target place → **Permissions**: enable **Allow place to be updated using Save
   Place API**. Close any active Studio Team Create session before a release.
3. Creator Dashboard → **Credentials**: create an Open Cloud API key with
   **Luau execution session task write** permission
   (`universe.place.luau-execution-session:write`) for the precise experience.
4. Set GitHub Actions secrets: `ROBLOX_API_KEY`, `ROBLOX_UNIVERSE_ID`,
   `ROBLOX_PLACE_ID`. Never commit credentials.

Publishing is always on: every validated push to `main` releases. Nothing
else (pull requests, version branches, minor branches) ever publishes.

## Release behavior

- Pull requests and major version branch pushes run offline mapping tests,
  repository tests where available, and a Rojo build. **No deployment**.
- A push to `main` runs validation then `scripts/roblox_live_publish.py --deploy`.
- The publisher validates the complete code mapping, rejects existing class
  collisions, creates **only missing code instances inside approved roots**,
  updates only source, calls `AssetService:SavePlaceAsync({SaveWithoutPublish=false})`,
  then separately checks code in Roblox's latest published place.
- Entirely Studio-managed world geometry, terrain, models, lighting, and UI
  objects are **never targeted**. However, the headless task loads the live
  game: any startup scripts that modify the world can still have side effects
  on a full-place save. Test the complete release on a separate place.
- The task operates from the **latest published** place, not unpublished Studio
  changes. After changing map or asset content in Studio, **publish those
  assets from Studio before the next automated script release**. Otherwise
  unpublished edits are not guaranteed to appear in the newly published version.
- GitHub cannot bypass Roblox's active Team Create restriction for
  `SavePlaceAsync`. A blocked save fails the workflow and requires closing
  the Studio session before retrying.
- Runtime code changes are verified for **new servers**; existing servers may
  need a Roblox-managed restart/migration depending on game requirements.
- A failed or partially completed Roblox task needs manual confirmation of
  the Creator Dashboard version history before retrying.
- The release **never deletes** scripts. A module removed from Git stays in the
  live place with its last published source. Retire a module the Loader walks
  (`Services/`, `Controllers/`) by replacing it with an empty `return {}` rather
  than deleting it, and remove leftovers in Studio by hand.
- Wally packages are not shipped by this publisher. Before adding a Wally
  dependency that live code requires, extend the release to ship
  `ReplicatedStorage/Packages` (as RBLX-Tank-Blast does) in its own change.

## Local checks

```sh
python3 scripts/roblox_cloud_sync.py --check
python3 scripts/roblox_live_publish.py --check
python3 -m unittest discover -s tests -p 'test_cloud_live_publish.py'
rojo build default.project.json --output validation.rbxlx
```

The `.rbxlx` build is **validation only**, never uploaded.

## Recovery

Use the Creator Dashboard's place version history to roll back a bad publish,
then fix the code on a new temporary branch. Do not fix production by editing
`main` directly.

References:
- https://create.roblox.com/docs/cloud/reference/features/luau-execution
- https://create.roblox.com/docs/reference/engine/classes/AssetService
- https://devforum.roblox.com/t/saveplaceasync-now-supports-all-places/3805169
