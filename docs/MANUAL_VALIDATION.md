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

## v0.05 — Gathering, inventory and field crafting

Automated: 9 specs cover one-slot-per-type stacking and caps, unique items never merging, 9 + 50 capacity, all-or-nothing removal, slot moves, recipe validity and the 10-arrow craft, starter-set cost, ±5% rolls only at world workbenches, the relative best-roll chance, and tool-dependent node yields. Deployed and verified on both places (2026-10-23).

Until the real map (v0.15), the play map scatters placeholder trees, rocks, iron, fiber, herbs and berry bushes within the map radius. Tag parts `ResourceNode` with a `NodeType` attribute to place them by hand instead.

Studio and live checks:

- [ ] From a fresh spawn with nothing, gather by hand and craft a wooden spear, bow, arrows and bandage in under 10 minutes.
- [ ] Harvest prompts work with E, gamepad X and touch; a stone axe gives more wood than bare hands; iron needs a pickaxe.
- [ ] A depleted node disappears and regrows after about 2 minutes; two players hitting the same node never get its last yield twice.
- [ ] Hotbar keys 1–9 equip tools and weapons, use medicine and food, and place a workbench; B (or gamepad Y) opens the backpack; tap two slots to move or swap.
- [ ] Advanced recipes only craft next to a workbench, and their gear shows a quality roll of at most ±5%; the craft menu (V or D-pad up) shows Owned/Needed counts.
- [ ] A full inventory refuses a craft or harvest without consuming anything.

## v0.06 — Combat, armor and PvP rules

Automated: 9 specs cover full-set EHP (120/150/180/200), additive mixed pieces and rolls, confirmed melee damage and cadence, cooldown enforcement, friendly fire / risk state / safe-zone gating, reach and arc, draw-independent bow damage, and wearing armor. Deployed and verified on both places (2026-10-23).

Safe zones are parts tagged `SafeZone` (which POIs get them is map content for v0.15). Placeholder values in use: armor split Head 25% / Chest 45% / Legs 30%, dagger 9 / sword 18 / iron sword 26 damage, arrows 60–120 studs/s at 0.35× gravity, basic bow + arrow 12 damage, allied tribes not yet protected from each other.

Studio and live checks (two players):

- [ ] Duels with each weapon family: spears hit hardest and slowest, daggers fastest; spam-clicking never beats the cadence.
- [ ] Arrows fly visibly slow on an arc, each shot uses one arrow, and a longer draw goes farther without hitting harder.
- [ ] Wearing armor (select a piece in the backpack, tap its Head/Chest/Legs slot) noticeably lengthens fights; full iron roughly doubles effective health.
- [ ] Nobody can hurt a player on the world menu, while spawning, or inside a `SafeZone` part; tribe members cannot hurt each other (tribes arrive in v0.07).
- [ ] Combat feels fair on a throttled connection (Studio network simulation).

## v0.07 — Death, departure, tribes and revives

Automated: 8 specs cover the pausing 60 s bleed-out, the 10 s revive, single reviver, armored downed HP and mid-revive finishing, revived HP, tribe size/invite/kick/leadership, mutual alliances, and Permanent items never entering a 600 s body. Deployed and verified on both places (2026-10-23).

Admins: the experience owner (or group ranks 254+) plus any user IDs in `src/server/Config/Admins.luau`. Command: `/safekick <name>` or `/safekick all` in chat. A graceful server shutdown also preserves every active run. Placeholders: crawl speed 2, revive range 8, alliances are labels only (allies can still hurt each other).

Studio and live checks:

- [ ] A solo player at 0 HP dies at once, leaves a body with their items, sees the death summary, returns to the lobby and cannot rejoin that world.
- [ ] A tribe member at 0 HP goes down: crawls slowly, cannot heal, the 60 s timer runs; a stranger's 10 s hold revives them (timer shows "paused"); a second reviver is refused; hitting the reviver does not stop it; enemies can finish them mid-revive.
- [ ] A revived player in full iron gets back 10 HP (at 100 max HP) and has no protection.
- [ ] Quitting or disconnecting during a run leaves a body; leaving from the world menu does not.
- [ ] Looting a body takes items one by one; the body and anything left vanish exactly 10 minutes after the death.
- [ ] A lobby party arrives in the world as one tribe; T opens the tribe panel; no friendly fire inside a tribe.
- [ ] `/safekick` mid-fight: no body, a game-update notice appears, and the same items come back once on the next Play.
