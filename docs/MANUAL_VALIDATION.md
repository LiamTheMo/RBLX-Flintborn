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

## v0.03 — Lobby, protected world menu and Play admission

Automated: 9 specs cover the GDD §31.2 state machine and risk states, transit reserve/consume/rollback, spawn distance and fallback, matchmaking capacity and exclusions, parties, and place-role detection. Deployed and verified on both places with the generated `PlaceIds` module (2026-10-23).

Place setup still to confirm:

- [ ] Play-map place **Max Players** set to 30 (Creator Dashboard → Places → Settings).
- [ ] The play map has ground within 1,000 studs of the origin (or parts tagged `SpawnCandidate`, or the workspace attribute `FlintbornMapRadius`) so random spawns find terrain.

Live checks (GDD §31.7), all on the published places:

- [ ] Join the lobby, press **Deploy**: you land on the world menu ("You are safe until you enter the world"), **Play** unlocks once loaded, and pressing it spawns you with "Entering world — items are now at risk".
- [ ] No character exists before Play; leaving from the world menu or pressing **Return to lobby** loses nothing.
- [ ] Party: invite, accept and deploy as leader; every member lands in the same world. A non-leader's Deploy is refused.
- [ ] Two players spawn at least 150 studs apart.
- [ ] Double-click Play: one character only.
- [ ] Joining the play-map place directly (not through the lobby) sends you back to the lobby.
- [ ] Die in the world: you return to the lobby after ~5 s, and deploying again never puts you back in that same world while it runs.

## v0.04 — Survival core: health, stamina, food and healing

Automated: 9 specs cover sprint timing, sprint-only stamina, food drain and the strict-25% slow, crouch and sprint speeds, instant medicine with animation lock, 10 s food heals, hit halving with the ≤10 HP cutoff, stacking, and downed clearing. Deployed and verified on both places (2026-10-23).

Studio and live checks (until crafting arrives in v0.05, a Studio run starts with a test kit of medicine and food; live runs only carry what was in the lobby backpack):

- [ ] Hold Shift (or L3 / the touch Sprint button): sprint lasts about 3 s, the bar refills in about 5 s; melee, crouching and standing still never drain it.
- [ ] Toggle crouch with C (or R3 / touch): slower movement, no stamina use.
- [ ] Food drains to 0 in 5 minutes; below 25% the HUD shows "! slowed" and movement is 10% slower; nothing else happens at 0%.
- [ ] Medicine heals instantly; spamming it during the animation heals once and consumes one item.
- [ ] Eat while taking hits: pending food healing halves per hit and stops at 10 HP or less; health never regenerates on its own.
- [ ] The HUD is readable on desktop, touch and gamepad.
