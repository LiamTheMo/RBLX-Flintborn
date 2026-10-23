# Roblox code-only Open Cloud synchronization

## Ownership and safety

- **GitHub:** Lua/Luau files mapped under `src/server`, `src/client`, and `src/shared`.
- **Roblox Studio:** World, terrain, models, manually authored UI, animation objects, lighting, binary assets, and all non-script objects.
- **Rojo:** Local testing and integration. Use Rojo to create new scripts in Studio, then save/publish that place once.
- **GitHub Actions:** On approved `main` integrations only, update the Source property of existing scripts using the Roblox Open Cloud Engine Instance beta API.
- **No automated place publication:** The pipeline never calls Roblox's full-place publishing endpoint or uploads a Rojo-generated place. A Studio publish is required to make edits live.

## Setup

1. Back up the Studio place (`File > Save to File`) and retain a known-good published version.
2. Enable collaborative editing (Team Create) for the target Roblox experience. Close open script-editor tabs during cloud sync.
3. Use Rojo locally to ensure all Git-managed scripts are **already present in the selected place** at their expected paths and classes. Publish once from Studio after syncing new scripts.
4. Create an API key at https://create.roblox.com/dashboard/credentials using the **`universe-place-instances`** API system, with Read and Write permission for the specific experience. Give it an expiration and limit access as far as practical for GitHub runners.
5. Set repository **Actions secrets** `ROBLOX_API_KEY`, `ROBLOX_UNIVERSE_ID`, and `ROBLOX_PLACE_ID`. The IDs must match the intended exact place.
6. Run `python3 scripts/roblox_cloud_sync.py --check` to inspect the source-to-instance mapping, then use `--dry-run` with credentials for a read-only cloud preflight. Only enable the automatic production job after the dry run is successful.
7. Promote an audited change through the current version branch to `main`. Only `main` invokes the authenticated sync operation.

## Cloud safeguards

- Mappings derive from `default.project.json` and Rojo's `*.server.luau`, `*.client.luau`, `*.luau`, and `init.*` conventions.
- Script mapping is **allowlisted** to `src/server`, `src/client`, and `src/shared` only. Asset folders and place structure never get uploaded by the cloud job.
- All targets must already exist, be uniquely identifiable by hierarchy, match their expected script class, and expose readable Source.
- A complete preflight finishes **before the first write**; errors stop the deployment without creating or deleting instances.
- After each changed Source update, the runner reads the script again to verify it matches the repository content.
- If an update fails after earlier writes succeeded, the workflow exits nonzero and requires reconciliation before retry. There is no atomic rollback across multiple scripts.
- The Engine Instance API is beta, has a 200 KB update limit, and cannot edit a script currently open in Studio or an instance inside a package.

## Important limitations

The cloud sync is an **editing** integration, not a live-game publisher. To go live, open the correct Studio place, reconcile it with the approved Git state using Rojo, test, then publish from Studio. Do not publish a stale local place over newer cloud edits. New scripts and changed hierarchy must be introduced through Rojo/Studio first.

Official guide: https://create.roblox.com/docs/cloud/guides/instance
