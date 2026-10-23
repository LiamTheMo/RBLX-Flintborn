# Manual validation still to run

Checks from finished phases that need Roblox Studio or the live game and cannot run in CI. Each phase document is deleted once its automated checks and deployment pass; its remaining manual checks move here. Tick an item when it has been run on the published places, and remove a phase's section once every item in it is ticked.

| Status | Meaning |
| --- | --- |
| [ ] | Requires manual validation |
| [x] | Validated on the published place |

## v0.01 — Project foundation and deployment pipeline

All manual checks done: both places prepared with Rojo, Save Place API enabled, and the first `main` deploy published and verified on both places (2026-10-23).

## v0.02 — Player data, persistence and session safety

Automated: 16 specs cover schema defaults and migration, validation, item records, leases, exactly-once operations, stale and lost-lease writes, DataStore retries and pending saves. Deployed and verified on both places (2026-10-23).

Studio and live checks still to run (Studio needs **Enable Studio Access to API Services**, otherwise ProfileService uses an in-memory store and warns):

- [ ] Join, let a change save, leave, rejoin: the data persists, and the save indicator (bottom-left) shows "✓ Saved".
- [ ] Join the lobby place, then the play-map place with the same account: the second place waits for the lease and loads once the first releases it (fully exercised by the v0.03 teleport flow).
- [ ] Shut down a live server (Creator Dashboard → shut down servers): the release save completes during shutdown.
- [ ] Leave and rejoin the same server within a few seconds: the profile resumes without a lease error.
