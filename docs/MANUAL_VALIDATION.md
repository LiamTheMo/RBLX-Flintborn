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

- [ ] Join the lobby, open the portal tile (Play window) and press **PLAY** (Deploy): you land on the world menu ("You are safe until you enter the world"), **Play** unlocks once loaded, and pressing it spawns you with "Entering world — items are now at risk".
- [ ] No character exists before Play; leaving from the world menu or pressing **Return to lobby** loses nothing.
- [ ] Party: invite, accept and deploy as leader; every member lands in the same world. A non-leader sees the Ready toggle in place of PLAY, and the server refuses a non-leader's Deploy.
- [ ] Two players spawn at least 150 studs apart.
- [ ] Double-click Play: one character only.
- [ ] Joining the play-map place directly (not through the lobby) sends you back to the lobby.
- [ ] Die in the world: you return to the lobby after ~5 s, and deploying again never puts you back in that same world while it runs.

## v0.04 — Survival core: health, stamina, food and healing

Automated: 9 specs cover sprint timing, sprint-only stamina, food drain and the strict-25% slow, walk and sprint speeds, instant medicine with animation lock, 10 s food heals, hit halving with the ≤10 HP cutoff, stacking, and downed clearing. Deployed and verified on both places (2026-10-23).

Studio and live checks (until crafting arrives in v0.05, a Studio run starts with a test kit of medicine and food; live runs only carry what was in the lobby backpack):

- [ ] Hold Shift (or L3 / the touch Sprint button): sprint lasts about 3 s, the bar holds for 3 s after the sprint ends, then refills in about 5 s (GDD §47); melee and standing still never drain it.
- [ ] Food drains to 0 in 60 minutes (half after 30); below 25% the HUD shows "! slowed" and movement is 10% slower; nothing else happens at 0%.
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
- [ ] Hotbar keys 1–6 (six slots, GDD §56) equip tools and weapons, use medicine and food, and place a workbench; B (or gamepad Y) opens the backpack (rebindable, GDD §46); tap two slots to move or swap.
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

## v0.08 — Extraction, lobby backpack and secure vault

Automated: 12 specs cover deadline qualification (late arrivals in, early leavers and downed or dead players out), 120 s/30 s timers, Center-only 2× materials (never runes, never unique gear), 1,000-unit vault stacks and 50-slot backpack overflow deleted and listed on the receipt, receipt replay as a no-op, a failed settlement changing nothing, receipt retention, and manual vault deposits refused (never deleted) when full. Deployed and verified on both places (2026-10-23).

Map hooks: parts tagged `PortalSite` with attributes `Kind` (`Fixed` or `Center`) and `ZoneRadius`; without them the server lays out placeholder portals (a Center at the origin and 2 of 6 ring sites). Runes are refused near parts tagged `Workbench` or `Structure`. Placeholders: 3 active portals (Center always on), zones 12/8/10 studs (fixed/Center/rune), 60 s portal cooldown, 3 s protected animation, built-in ping as the alert sound (400-stud roll-off). Studio runs start with one Portable Extraction Rune.

Studio and live checks (two or more players):

- [ ] Two players trigger the same portal: one shared countdown; a stranger inside the zone at zero extracts on an enemy's timer.
- [ ] The activator dies or leaves the zone before zero; everyone else inside still extracts. Downed players inside do not.
- [ ] At zero the HUD switches to "Protected: extracting"; disconnecting during the 3 s animation still settles the items.
- [ ] Arriving in the lobby shows the receipt: every material (special ones included, Q164) banked to the vault, gear in the lobby backpack, overflow listed as deleted.
- [ ] A Center extraction doubles materials but never a sword; a rune placed at the Center does not double.
- [ ] A rune (hotbar) is refused next to a workbench and next to another running extraction; elsewhere it starts a 30 s countdown everyone can use.
- [ ] The Vault button opens the vault in the lobby: deposit from the backpack and withdraw items; materials have no withdraw action (Q164); a full vault refuses rather than deletes.
- [ ] Lobby backpack and vault contents survive logout, rejoining another lobby server and a world reset; Deploy takes the whole backpack except materials into the next run.

## v0.09 — Ancestral Forge and Permanent items

Automated: 10 specs cover unlocks granted once (two extractions plus an extracted Ancient Ember for the Permanent pickaxe), conversion charging each input once and consuming the source in place with its quality roll kept, rejection of foreign, unvaulted, already Permanent, ineligible, invented or in-transit sources, one commit for two conversions of the same item, nonce retries returning the same receipt, refused (never deleted) special crafts when the lobby backpack is full, Permanent items surviving death (several at once), ownership transfer on pickup, and Permanent items never deleted by backpack overflow. Deployed and verified on both places (2026-10-23).

Placeholders: Permanent archetypes are Basic Pickaxe, Stone Spear, Iron Sword and Iron armor. The Permanent pickaxe costs 150 Stone, 60 Wood, 20 Iron and 1 Ancient Ember (the rare-event reagent; events arrive in v0.11, Studio runs start with one). Special recipes are iron tools, weapons and armor, 50 arrows and potions. Ordinary drops vanish after 10 minutes; Permanent drops stay until the world resets.

Studio and live checks:

- [ ] Extract twice (once carrying the Studio Ancient Ember), vault the ember and a Basic Pickaxe, then open the Forge in the lobby: the Permanent pickaxe recipe is unlocked and counts only vaulted materials.
- [ ] The conversion dialog names the exact pickaxe and its quality roll, arms only after a short delay, and the vault then shows one ★ pickaxe with the same roll.
- [ ] Die carrying several ★ items: all come back in the lobby backpack; ordinary items stay in the body.
- [ ] Q drops a ★ item; a second player picks it up, is told they own it, and keeps it on death; the original owner cannot get it back after rejoining.
- [ ] A dropped ★ item left on the ground is gone after the world resets.
- [ ] Special Forge crafts land in the lobby backpack with no quality roll; a full backpack refuses the craft.

## v0.10 — Building, totems, raiding and farming

Automated: 7 specs cover the 50 m portal aura rejecting partial overlaps (whole footprint, rotation aware), totem HP 500 / 1,000 / 2,500 with growing radius, cover stopping decay and loss of cover assigning one 240–360 s deadline that never re-rolls, rival totems never covering or taking over while the owner's totem stands, takeover after it falls, server-generated structures never claimable or decaying, tool bonuses against materials, grid snapping and server-timed crops. Deployed and verified on both places (2026-10-23).

Placeholders: 50 m = 178.6 studs (1 stud = 0.28 m); totem radius 15 / 35 / 70 studs; wall HP wood 300 / stone 800 / iron 1,600; tools hit 1.5× against their material (axe vs wood, pickaxe vs stone/iron); crops Berries 3 min, Herbs 5 min, Sapling 10 min; chests 20 slots; traps 15 damage per 2 s; 300 pieces per owner. Solo players own their pieces until they join a tribe. A crafted workbench is placed as an ordinary structure.

Studio and live checks (two tribes):

- [ ] X opens build mode: the ghost snaps, rotates (R / L2 / Rotate) and shows ✓ or ✕ with colour; Place works on touch and controller.
- [ ] Building wood → stone → iron charges the shown costs; pieces near an extraction portal or rune are refused, including pieces whose edge crosses the red aura.
- [ ] Without a totem a piece shows a decay timer and vanishes in 4–6 minutes; a totem stops it; upgrading the totem grows the radius and HP.
- [ ] The owner leaves; the base stays. A raider breaks a wall with weapons/tools and opens a chest (public); a wall between the raider and the chest blocks it.
- [ ] Destroy a rival totem, place your own, and their pieces become yours; while their totem stands nothing changes hands.
- [ ] Only the owning tribe can open its doors. Traps hurt other tribes, not your own.
- [ ] Plant Berries/Herbs/Sapling in a planter, walk away, return to harvest; a destroyed chest spills its items.
- [ ] Empty the world: everything built is gone in the next world.

## v0.11 — World event director and rare spawns

Automated: 10 specs cover independent category rolls (several events per tick), the ~25% trigger rate, the waterfall from Secret (~0.025% per category per tick) down with Common fallback, categories without Common skipping, footprint separation, one-time claims (rare nodes never regrow), the full 60 s cache channel, budget caps, biome rings and catalog consistency (real items, real enemies, all six enemy themes, `event` tags). Deployed and verified on both places (2026-10-23).

Placeholders: ticks every 300 s live and 45 s in Studio (override with the workspace attribute `FlintbornEventSeconds`); rarity weights Secret 0.1%, Mythic 0.5%, Legendary 1.5%, Epic 5%, Rare 12%, Uncommon 25%; biome rings Center < 30%, Inner 30–65%, Outer 65–95% of the map radius; budgets 40 event NPCs and 6 large events; rare nodes 10 min, ruins 15 min, caches 10 min; meteors 8 chunks × 30 s; portable rune in 1% of Rare+ cache rolls. Enemies are simple blocks with name plates until art arrives (v0.15).

Studio and live checks:

- [ ] Every spawned event shows a banner (icon, rarity colour and name, direction and distance) with a sound, a list entry with its timer, a faint area circle and a sky beacon that does not hide arrows or extraction beacons.
- [ ] Events land across the outer, inner and centre rings, never overlapping each other.
- [ ] A cache needs 60 s of holding; releasing it, walking away or being hit (by a player, trap or creature) restarts it. Loot spills on the ground for anyone.
- [ ] Ore events need a pickaxe; rare nodes pay out once and vanish.
- [ ] Wolves, skeletons and raiders chase at-risk players nearby, give up past their leash, and drop loot when killed; an elite has more health and a gold name.
- [ ] Event loot is lost on death and only safe after extraction.
- [ ] A full 30-player server stays smooth with several events running.

## v0.12 — Bosses: Guardian and scalable encounters

Automated: 7 specs cover the Guardian schedule (15–20 min after the last encounter, 3 min horn), the 25% Legendary released once per encounter ID (re-crossing cannot duplicate it), scaling clamped to 0.75×–2.0× and frozen at spawn (later gear removal and alt joins change nothing), gear scores, per-source resets (event bosses leave with their event, structure bosses heal when idle and leave with their hold, ritual bosses and the Guardian leave when uncontested) and catalog consistency. Deployed and verified on both places (2026-10-23).

Placeholders: Guardian 25,000 HP with 4 pillars × 1,500 HP, arena radius 80 studs at the part tagged `GuardianArena` (else the map centre); scaling 0.75 + 0.25 × Σ(50% level/50 + 50% gear score) per at-risk player. Studio compresses the Guardian to a horn 30 s after start and a spawn 30 s later (override with the workspace attribute `FlintbornGuardianSeconds`). Ritual offering: 3 Ancient Ember + 50 Iron, 10 s summon. Event bosses: Ironhide Behemoth (Epic), Bone Colossus (Legendary); structure boss: Raider Warlord in Warlord's Hold. Bosses are blocks with phases shown in the boss bar until art arrives (v0.15).

Studio and live checks (two tribes):

- [ ] The Horn of War countdown appears 3 minutes ahead in a red style distinct from event banners; the Guardian rises shielded at the Center Crater.
- [ ] Both tribes contest the pillars; when the last falls the shield drops ("Gauntlet") and the bar turns red.
- [ ] Slams, slow bolts and red-circle quakes hurt players; standing outside the circle avoids the quake.
- [ ] At 25% the "LEGENDARY RELEASED" cue shows and Guardian's Fang drops once; its carrier glows gold; it can be stolen and extracted.
- [ ] Building within 80 studs of the arena is destroyed during the encounter.
- [ ] A ritual summon is broken by a third party's hit and the offering spills; an uninterrupted summon brings the Ember Titan with a public announcement.
- [ ] Event and structure bosses appear from the director and reset by their own rules.
- [ ] A full server stays smooth during the Guardian fight.

## v0.13 — Account progression, masteries and rebirth

Automated: 8 specs cover XP saved when earned and kept through death, the 100 × n^1.5 curve capped at 50, the Center bonus equal to the run's XP once (mastery XP too, never action counts; runes never), exactly five tracks capped at 10 with titles, +1% yield per level (+10% at 10), the 132 ordering example and Premium + booster adding to +75%, rebirth resetting only the level (vault, Permanent items, masteries and perks kept; harder each time), and perk ranks spending tokens once. Deployed and verified on both places (2026-10-23).

Placeholders: XP per action — gather 2, craft 5, crop 10, forge 15, chunk 15, creature 10 (elite 30), node 25, cache 40, player 20 (once per pair per 30 min), boss 100, Guardian 300. Mastery thresholds 25…3,000 actions; Crafting gives better quality rolls and, when smelting, a 2%-per-level bonus-bar chance (GDD §52; crafting speed, ingredient savings and larger outputs were removed 2026-10-28), and Forge recipes keep their Crafting level gates; PvP gives +0.5% damage per level (cap 5%) and +2% sprint per level. Rebirth needs level 50 and 1, 2, 3, 4, 6… Guardian Legendaries extracted since the last rebirth; tokens 3, +1 every third rebirth. Perks: Scholar (XP), Fortune (luck), Bounty (yield), Tidewalker (swim). Level gates now apply to Permanent spear (10) and iron gear (20), and Potions need Crafting 3.

Studio and live checks:

- [ ] Gathering, crafting and fighting show XP pop-ups; the level bar fills; dying keeps every point.
- [ ] A Center extraction receipt shows the run XP and an equal bonus; a rune extraction shows no bonus.
- [ ] Reaching mastery 5 grants its title once; the lobby name plate shows level and best title.
- [ ] P opens the panel; in the lobby, rebirth shows Reset / Kept / Gained before confirming; buying a perk rank spends tokens once and its effect applies (e.g. Tidewalker in water).
- [ ] A Premium test account sees "+25% XP" and earns 25% more.

## v0.14 — Economy, shops, trading and monetization

Automated: 12 specs cover the 250 / 1,000 / 3,000 quest bands, zero Coins and Gems from extraction (Center included), +25 vault slots per upgrade at the same Gem price, daily quests paying once, shop purchases into the lobby backpack, fixed merchant prices (crafted gear at 40% of materials, Forge-reagent warning, no Permanent sales), trade eligibility (Coins and raw materials refused; gear, flagged materials, Permanent items and Gems allowed; level 10 and 5% fee for Gems), settlement and crash reconciliation leaving one outcome, Permanent ownership moving with a trade, every Robux offer having an earnable route and no power, purchase receipts fulfilled once, and perk respec refunds. Deployed and verified on both places (2026-10-23).

Placeholders: vault upgrade 500 Gems (max 8 tiers), respec 250 Gems, Gem trades 2,000/day, merchant Wood/Stone 2, Iron 8, Hide 5, Jade 12, Obsidian 10, Ancient Ember 300 Coins; shop Bandage 50, Berries ×5 40, Arrows ×10 60, seeds 25, tools 150, titles 2,000/8,000 Coins. Robux offers show "coming soon" until developer product IDs are set in `src/shared/Economy/OfferCatalog.luau`; codes live in `src/server/Config/Codes.luau`.

Studio and live checks (two accounts):

- [ ] The Market button opens the market: buy from the shop, sell to the merchant (a Forge reagent shows a warning), claim each quest tier once; the wallet updates; Coins and Gems never drop on death.
- [ ] Upgrade the vault with Gems; G shows 25 more slots. Redeem `FLINTBORN-RESPEC` once to refund perk tokens.
- [ ] The Trade button opens trading: invite, add a ★ item and Gems, lock, wait for the countdown, confirm; any change unlocks both sides; Coins are never offered.
- [ ] Disconnect one player mid-trade: the trade closes and nothing changes hands. (Crash recovery between the two saves is covered by specs; a forced server kill is a live check.)
- [ ] Once product IDs exist: buy a vault upgrade and a Gem pack with Robux in a test place; each purchase grants exactly once.
- [ ] Review Roblox purchase policy (paid random items, Premium) before release.

## v0.15 — Shattered Crater world, art direction and camera

> The placeholder island described here was replaced on 2026-10-28 by the 4,096-stud map in GDD §54; see "Play-world map and creatures (GDD §54)" for the current checks.

Automated: 6 specs cover every portal POI having a zone radius inside its region (3 Outer + 1 hidden, 3 Inner, 1 Center), every biome having a resource pool with jade and obsidian only in the Inner Ring, safe camps with volumes in the Outer Rim, spawn candidates in all three regions, the island profile (sea, beach, a tall ridge with route gaps, an open caldera) and camera bounds. Deployed and verified on both places (2026-10-23).

Placeholders: until an authored `ShatteredCrater` model is placed in the world place (Workspace or `ServerStorage.Maps`), the server builds a blocky placeholder island at start-up (radius 1,200 studs, 48-stud tiles, Outer Rim 750–1,200, Inner Ring 300–750, crater < 300, ridge at 300 with four route gaps) and removes the Studio `Baseplate` at runtime only. Set the workspace attribute `FlintbornGenerateIsland = false` to opt out. POIs and landmarks come from `src/shared/World/PoiCatalog.luau`. Camera zoom 8–40 studs.

Studio and live checks:

- [ ] The island loads with beaches, woodland, jungle, the ridge and caldera; landmarks (Giant Roots, Old Ruins, Monoliths, Jade Falls) are visible from a distance on low graphics.
- [ ] Spawns land in all three regions, away from other players; extraction portals appear at named POIs with a different subset per server; the Center portal is in the crater.
- [ ] The two safe camps show white-and-blue posts, a sign and a "safe: no damage here" notice; nobody can be hurt inside.
- [ ] Jade and obsidian nodes appear only in the jungle and need a pickaxe.
- [ ] N opens the map with regions, landmarks, camps, active portals and events; the compass follows the camera.
- [ ] Zoom with wheel, pinch and right stick stays within 8–40 studs and is restored on the next spawn.
- [ ] Traverse every ring on mobile and note travel times; 30-player performance on a mid-range phone.

## v0.16 — Onboarding, UX and accessibility

Automated: 4 specs cover the tutorial's learning order with a completion trigger per step, steps completing only in order and from their own trigger, rewards paid once (never after a skip or on replay, the safe Play step unskippable), and no step granting Permanent gear, more than 25 Gems or more than easy-tier Coins. Deployed and verified on both places (2026-10-23).

Placeholders: ten steps (Play → Survive → Gather → Craft → Heal → Tribes → Events → Extract → Vault → Economy); rewards are a gathering XP grant and 250 Coins on the first extraction. Settings: UI scale 0.8–1.4, colour-blind (Okabe–Ito based) rarity palette, reduced motion, subtitles on by default. No new-player PvP protection (GDD Open, default none).

Studio and live checks (desktop, touch and controller):

- [ ] A fresh profile sees "Tutorial 1/10" in the world menu; each step advances only after doing it; "Got it" advances the explanation steps; Skip appears after the safe Play step.
- [ ] The marker points at the nearest node, event or portal and does not bob with reduced motion on.
- [ ] The first extraction pays 250 Coins once; replaying the tutorial from settings pays nothing again.
- [ ] ⚙ / O opens settings: UI scale applies to every screen at once; the colour-blind palette changes rarity colours everywhere (names still shown); subtitles caption event, extraction and Guardian alerts; choices persist after rejoining.
- [ ] Without a keyboard, the lobby HUD's tiles and buttons open every window (Inventory with its Vault tab, Play, Journal, Market, Forge, Trade; Progress from the player card; Party from the party panel; Settings from the gear), and the in-run navigation tiles open backpack, craft, build, tribe, map and progress.
- [ ] Testers can explain Vaulted vs Permanent; a colour-blind simulation pass over every screen.

## v0.17 — Live-ops hardening

Automated: 4 crash-recovery specs (a crash with no heartbeat is eligible; logout and planned shutdown never are; items already dropped, stored or traded away are excluded; restored once even when retried) and 16 security specs, one per GDD §24 case: forged Permanent IDs, double Forge requests, simultaneous devices, teleport mid-operation, death vs extraction, Center bonus replays, ineligible trades, trade interruption, double purchase receipts, rebirth replays, repeated 25% boss grants, negative quantities, DataStore budget exhaustion, structures in portal auras, malformed remote arguments and floods, and impossible movement. The spec runner also fails on require cycles. Deployed and verified on both places (2026-10-23).

Placeholders: remote limits 20 calls/s per remote per player (burst 40), arguments ≤ 8, strings ≤ 256, tables ≤ 64 entries and depth 2; flood kick at 150 violations per minute; checkpoints every 15 s plus 1 s after changes, 24 h expiry; server heartbeat every 30 s, stale after 90 s; recovery retries 3 × 100 s while the player stays; movement tolerance 1.6× sprint speed + 6 studs per 0.25 s sample, two strikes before a pull-back (tightened by the post-release hardening pass below). Analytics flush every 60 s. MemoryStore outages mean a crash cannot be recovered (documented scope).

Studio and live checks:

- [ ] Kill a test world server mid-fight: on rejoin (after ~90 s) the lobby shows "Server crashed — your items were recovered" and the items return once.
- [ ] Quit normally mid-fight: no recovery; a body is left. A `/safekick` or update shutdown restores through escrow instead.
- [ ] Drop an item, then kill the server: that item is not restored (whoever picked it up keeps it).
- [ ] A speed exploit or teleport is pulled back; normal sprinting, crawling and long falls are not.
- [ ] Spamming any remote gets throttled without errors for honest play.
- [ ] Creator Dashboard shows the custom and economy events; poor-network and client-close-mid-portal tests; load tests with many drops and structures; 30-player profiling on real devices.

## v0.18 — Release candidate and launch readiness

Automated: 3 release specs cover loading a profile saved by the earliest phase into the final schema with every later group filled, refusing profiles from a newer schema, and catalog completeness (every item has a source; every weapon has combat stats — this found and fixed Cooked Meat having no source: creatures now drop Raw Meat, cooked at a built Furnace). The full CI suite (20 spec files including the §24 security suite) passes on `main`. Deployed and verified on both places (2026-10-23).

Everything still manual before `v1.00` is in [`docs/RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md).

- [ ] Hunt a wolf or boar, build a Furnace (X), and cook Raw Meat into Cooked Meat (V, "furnace" recipes).

## Post-release hardening (after v0.18)

Automated: three rounds of independent review across economy, trading, progression, run lifecycle, persistence, crash recovery, combat, building, enemies and anti-cheat, plus the client. Each confirmed bug has a regression case. The new specs are `hardening_economy`, `hardening_lifecycle`, `hardening_gameplay`, `review_economy`, `review_lifecycle` (which runs the real server services against faked Roblox services), `review_gameplay`, `followup_recovery` and `followup_extraction`. The spec runner now covers 28 spec files.

Closed in this pass:
- **Economy and trades:**
  - Code reuse is closed, including codes redeemed before the redemption record existed.
  - Center 2× no longer doubles lobby materials (superseded by Q164 below: materials never enter a run from the lobby).
  - Trades are protected against bait-and-switch, and reconcile or roll back after a crash.
  - Selling, Forge crafts, Gem spending and Deploy are refused with "TradeSettling" while a trade can still roll back.
  - Purchase entitlements are checked.
  - Rebirth credit counts only Guardian Fangs.
- **Run lifecycle and crash recovery:**
  - Shutdown, safekick and failed-save paths never lose or duplicate a loadout.
  - Runs are recorded at Play, so a crash before the first checkpoint still restores the loadout.
  - A new run can't overwrite an unrecovered crash checkpoint: Play is refused with "RecoveringItems" until it settles.
  - Checkpoints are deleted only when they still belong to the same run.
- **Combat:**
  - Melee and arrows need line of sight and a server-validated position.
  - Bow draw is measured by the server.
  - Enemies and bosses respond to ranged attackers within their leash.
  - Safe zones block attacks in both directions.
- **Building and movement:**
  - Buried or overlapping placements are rejected, totems are capped at 3 per owner, and a player who leaves a tribe loses control of its pieces.
  - Movement uses a draining latency budget at 1.25× the server walk speed, and a large blink is pulled back at once.
  - Sprint stops at empty stamina until the key is released or the bar is full again.
- **Parties:** party tribes are verified through a server-written MemoryStore record instead of client teleport data.
- **Client:**
  - Touch controls are no longer scaled down.
  - Panels block click-through.
  - The new refusal reasons show friendly text.

Placeholders:
- **Movement:** tolerance is 1.25× the server-set WalkSpeed plus a draining 6-stud latency budget; a jump of more than 3× the limit is pulled back immediately.
- **Combat:** melee and shots are refused when the root or head is more than 12 studs from the validated position. Provoked enemies hunt for 10 s within leash + 150 studs.
- **Building:** at most 3 totems per owner; crop XP at most 6 grants per player per minute.
- **Parties:** deploy records expire after 1 hour.
- **Recovery:** recovery retries every 15 s while the player stays.

Known limits, by design or deferred:
- A trade rollback can't recover items the other player already spent before the guard existed.
- The 1-unit crafting ingredient refund comes back unmarked, so at most 1 unit per craft could be doubled at the Center.
- An old server that lost its lease but keeps heartbeating holds the RecoveringItems gate until it clears its checkpoint or shuts down.
- Private survival attributes still replicate to all clients (low impact).

Studio and live checks:

- [ ] Sprint, crawl, fall and ride lag spikes on a real network without rubber-banding. Being pushed or sliding while downed doesn't trigger repeated pull-backs, and spawn or pull-back snaps aren't judged as teleports.
- [ ] A speed or teleport exploit is pulled back; teleporting in, swinging and teleporting back does no damage.
- [ ] Melee hits on stepped ground and point-blank; arrows don't pass through walls; bosses can reach players and don't climb onto pillars.
- [ ] Building: roofing from outside a hut and placing a floor under your own feet behave sensibly; buried totems are refused; a fourth totem is refused.
- [ ] A player kicked from a tribe can't open its doors or walk over its traps.
- [ ] Chest reach works with tall avatar bodies.
- [ ] Cache channel: the hold bar resets for an interrupted holder, and other holders keep their bars.
- [ ] A party deploys from the lobby and forms its tribe right after Play. With MemoryStore unavailable, members arrive solo and the deploy still works.
- [ ] Kill a world server mid-run, rejoin another world and press Play: "RecoveringItems" shows, then the items are restored once and Play works.
- [ ] Kill a world server within a second of pressing Play: the loadout is restored once.
- [ ] Shut down a server while a Play is loading: the loadout stays in the lobby. A `/safekick` whose save fails retries and kicks once saved.
- [ ] Trade, then immediately try to sell, Forge, spend Gems or deploy: refused with the "recent trade" message, then allowed after the save lands.
- [ ] On a phone, the touch thumbstick, jump and Sprint buttons are full size; the lobby HUD's tiles, party panel and hotbar don't block the jump button or camera drag.

## Q164 — Materials stay in the lobby (superseded by GDD §53)

> Replaced on 2026-10-28: materials can be carried back into runs. The checks below describe the old behaviour; see "Resources, gathering and boosts (GDD §53)" for the current ones.

Owner decisions (GDD §45, Q164/Q164a): extracted materials never come back out into the play world; any material that reaches the lobby backpack goes straight into the vault and cannot be taken out, and the vault's material capacity alone decides what is deleted.

Automated:
- A Deploy reserves gear, ammo and consumables but leaves every material (Wood, Iron, Ancient Ember) in the lobby backpack. A rollback returns the reserved items beside them.
- The vault has no material withdrawal.
- Extraction banks every material, special ones included, into the vault and doubles it at the Center.
- With a full 50-slot backpack and 990 Stone in the vault, a Center extraction stores 1,000 and deletes 50, still vaults Ancient Ember, and deletes only the gear that overflows the backpack.
- Backpack materials bank into the vault at once with overflow deleted and recorded; a material can't be deposited as an item.
- Driving the real ProfileService: an old save with backpack Iron loads banked with the overflow deleted, and both an operation and a direct mutation that land materials in the backpack end with them banked.
- Trades offer eligible materials (special or Exclusive) straight from the vault by quantity; backpack and ordinary materials are refused, the receiver's vault must have room, settlement and rollback move vault to vault exactly once (`trade_materials.spec.luau`, 16 cases).
- The per-stack carried-in tagging and its specs are removed; the party-verification cases moved to `followup_party.spec.luau`.

Studio and live checks:

- [ ] A profile saved before this change with materials in its backpack loads with them in the vault; anything over 1,000 shows as "Vault full — deleted" in the vault's materials column for a day.
- [ ] Trade Ancient Ember from the vault with +1 / +10 / All / Remove: both players see the offer update, the Ember moves vault to vault, and the next Deploy brings only gear. A trade that would push the partner's vault past 1,000 is refused ("their vault has no room").
- [ ] Rejoin after a crash mid-trade: a rolled-back Ember returns to the giver's vault.
- [ ] Extract with Ancient Ember: the receipt shows it vaulted, and the vault's materials column shows it with no withdraw action.
- [ ] Forge recipes that use Ancient Ember still work from the vault.
- [ ] The shop no longer lists Herb seeds; planting Herbs uses Herbs gathered in the run.

## Keyboard controls and rebinding

Owner request (GDD §46): defaults of hold Shift to sprint, Tab for the backpack, 1–9 for hotbar slots (1–6 since the six-slot hotbar, §56), Q to drop and E to interact or pick up (F in revisions 1.12–1.23); revision 1.24 moved the backpack to B and the map to M and removed crouch, with every keyboard action rebindable in Settings. Lobby windows have no keys (besides Tab for the Inventory); the lobby HUD's tiles open them.

Automated (`keybinds.spec.luau`, 7 cases):
- The requested defaults, with every default allowed and unique.
- Reserved keys (W A S D, Space, /, Esc, Enter, Backspace, function keys) and unknown actions are refused.
- Rebinding to a used key swaps the two actions; keys equal to their default are not stored.
- Tampered saves resolve to the defaults. In a conflicting or older save, only the clashing rebind reverts and every other rebind is kept; removed lobby actions are dropped.
- Hints name the bound key, and every tutorial token is a real action.

Studio and live checks:

- [ ] Fresh profile: Shift sprints while held, B opens and closes the backpack, M opens the map, 1–6 select hotbar slots (7–9 do nothing), Q drops, C does nothing, and E picks up a dropped item, loots a body and harvests a node.
- [ ] Settings → Controls: rebind Backpack to Tab. B stops opening it, Tab opens it, and every on-screen key hint for the backpack reads Tab. Rejoin: the binding is kept, in both the lobby and the world.
- [ ] Rebind Drop to F: Interact moves to Q, and prompts show and accept Q.
- [ ] Pressing a reserved key (W, Space, /) while rebinding shows "reserved" and changes nothing; clicking the waiting key again cancels.
- [ ] Pressing Tab while rebinding doesn't open the backpack.
- [ ] Reset controls to defaults restores everything.
- [ ] Roblox's player list never appears in either place (GDD §52); Tab opens the backpack in the world and the Inventory window (Backpack and Vault tabs) in the lobby, and Tab again closes it.
- [ ] Planters offer their three crops on F / R / E with the default binds, and no two share a key after rebinding Interact.
- [ ] In the lobby, G / F / M / Y do nothing; the HUD tiles open the Inventory, Forge, Market and Trade, and Settings → Controls doesn't list them.
- [ ] The tutorial hints name the current keys after a rebind.

## Stamina recovery delay and walk-after-sprint fix

Owner decision and bug report (GDD §47): recovery stops when a sprint starts and resumes 3 s after it ends. Walking after releasing sprint no longer drains stamina.

Automated (`survival.spec.luau`, `hardening_gameplay.spec.luau`, `review_gameplay.spec.luau`):
- 3 s of sprint empties the bar, a 3 s pause follows, then it refills in 5 s.
- A sprint during the pause restarts it.
- 20 s of walking with uneven 0.2 s position samples (60–140 % of walk speed) after a sprint recovers and never drains.
- Travel at sprint pace without a sprint request is still caught and drained; one sample, or a change of allowed speed, never judges a full window.

Placeholders: recovery pause 3 s; pace window 1 s; sprint pace 1.25× walk speed (20 studs/s at the 16 / 24 starting speeds).

Studio and live checks:

- [ ] Hold Shift + W, release Shift and keep W held: the stamina bar stops falling at once, holds for 3 s, then refills.
- [ ] Sprint briefly again during the pause: the 3 s restarts.
- [ ] Walk normally on a laggy connection (Studio network simulation): stamina never drains.
- [ ] A speed exploit without the sprint key still loses stamina (and is pulled back by movement checks).

## Item and material catalog (GDD §51)

Owner-defined catalog, with full tables in [`docs/ITEM_CATALOG.md`](ITEM_CATALOG.md).

Automated (new specs):
- `gathering_tiers`, 13 cases: the pickaxe gate, Resin and Flint bonuses, ores by region, the rare shrub event, per-type event rolls.
- `stations_smelting`, 14 cases: the Anvil and Cauldron, timed smelting, every interruption, and no duplication when spamming, leaving, or using two furnaces.
- `boosts`, 12 cases: berry and draught boosts, replacement, and luck and XP stacking.
- `siege`, 7 cases: Fire Bomb and Breaching Charge damage, refusals and throw limits.
- `catalog_migration`, 16 cases: removed items pruned from every save location, Forge conversions, the shop and trading.

Every older spec was migrated to the new IDs and rules, for 37 spec files in all.

Placeholders:
- **Tiers:** ×1.25 per tier, smelt times 2–8 s per bar, recipe amounts.
- **Boosts:** berries +10% XP or +5% luck for 3 min; draughts +25% XP or +15% luck for 10 min (15 min for the Strong versions).
- **Fire Bomb:** base 60, 6-stud burst, 20 damage to players and creatures, about 40 studs of range.
- **Breaching Charge:** 900 damage after an 8 s fuse, placed within 8 studs.
- **Bonus drops:** Resin 10% and Flint 15% per hit.
- **Prices:** merchant values in ShopCatalog.

Studio and live checks:

- [ ] **Old saves:** load one holding Iron, Berries, Arrows, a Basic Pickaxe or Bow, and Wood or Stone armor. They are gone from the vault, backpack and Forge, and nothing errors.
- [ ] **Mining gate:** hit Copper with a Wooden Pickaxe and get nothing plus "Needs a Stone Pickaxe or better". A Stone Pickaxe mines it. The same applies up the ladder, and prompts show "· X Pickaxe+".
- [ ] **Ore regions:** Copper and Iron appear in the Outer Rim, Silver, Cobalt, Jade and Obsidian in the Inner Ring, and Mithril in the Crater, with distinct looks.
- [ ] **Gathering:** trees sometimes give Resin and rocks give Flint, always on the last hit. Plants are gathered by hand.
- [ ] **Smelting:** a batch at a Furnace shows a progress bar. Walking more than 12 studs away, dying or breaking the furnace stops it, and the bars already made are kept. The Stop button works.
- [ ] **Stations:** an Anvil enables Silver and up and Jade gear. A Cauldron enables potions and draughts.
- [ ] **Build mode:** cycles all 8 tiers with HP and cost, and offers the Anvil and Cauldron. Check the panel layout on a phone.
- [ ] **Crafting menu:** the chips, tier stepper and "Here only" toggle work on touch.
- [ ] **Boosts:** the toast and HUD line appear with a countdown. Drinking another boost of the same kind replaces it, and boosts end on death, extraction and leaving.
- [ ] **XP stacking:** Premium, a booster and a potion add up: 100 XP becomes 200.
- [ ] **Luck:** comes from the killer, the cache opener and the boss's top damage dealer.
- [ ] **Fire Bomb:** arcs, and burns Wood far more than Stone and barely touches metal. It respects PvP, friendly fire and safe zones.
- [ ] **Breaching Charge:** places on an enemy wall or door within reach and shows its countdown. It is refused on your own pieces, floors, safe zones and portal auras, and breaks a Wood or Stone wall.
- [ ] **Meteors:** chunks need a Mithril Pickaxe and give Adamantine Ore.
- [ ] **Rare shrubs:** the event is announced and gives rare berries and herbs. Several events can start in one tick without overlapping.
- [ ] **Forge:** tabs work; Permanent opens on your vaulted gear; the show-all toggle groups conversions by tier; the confirmation names the item and its cost.
- [ ] **Shop and merchant:** the shop shows only starter supplies. The merchant sells by ×10 or all, with no "Sell all" for Forge reagents.
- [ ] **Trading:** a Sunberry and an Ancient Ember trade between two players. Ores, bars and common materials are refused.
- [ ] **Planters:** all four crops have their own prompt keys.

## Boosts, Crafting mastery, touch hotbar and Tab (GDD §52)

Owner decisions 2026-10-28: a running boost never weakens; Crafting mastery gives only quality rolls and a smelting bonus bar (no crafting speed); the HUD hotbar shows items and taps use them; the Roblox player list is gone and Tab opens the inventory.

Automated (`boosts.spec.luau`, `progression.spec.luau`, `stations_smelting.spec.luau`, `hud_model.spec.luau`):
- A weaker or equal boost leaves the running one untouched (strength and timer); a stronger one takes over; any boost starts once the old one ends; the berry toast says the running boost keeps going.
- Crafting mastery's buffs are exactly BestRollLevel and SmeltBonus (20% at level 10); CraftSpeed, IngredientSave, CraftOutput and RecipeTier are gone.
- A certain bonus makes three ore into six bars, each bar still taking its own ore; instant crafts get no bonus; a bonus bar with no room drops at the smelter's feet and the job still finishes.
- HUD hotbar slots show item names, Permanent stars and stack counts, mark the equipped slot, and ignore backpack and out-of-range slots.

Placeholders: bonus-bar chance 2% per Crafting level.

Studio and live checks:

- [ ] Drink a Sunberry Draught, then eat a Sunberry: you're fed, the toast says the +25% XP boost keeps running, and the HUD timer doesn't change. Drinking a second Sunberry Draught is refused with "a boost at least as strong is already running" and the draught stays in the hotbar.
- [ ] Eat a Sunberry, then drink a Sunberry Draught: the boost rises to +25% with a new 10:00 timer.
- [ ] At Crafting mastery 0, smelting 10 ore gives exactly 10 bars. At a high level, some smelts give an extra bar (the count rises by 2 for one ore).
- [ ] Crafting speed is the same at every Crafting level (one craft per second).
- [ ] On a phone or tablet (or Studio's device emulator): the HUD hotbar shows each item's name and count. Tapping a weapon equips it (the ring moves there), tapping food eats it, tapping a Workbench places it, and tapping a Fire Bomb readies it.
- [ ] Pressing a number key moves the ring to that slot and uses it, as a tap does.
- [ ] With the backpack open, the HUD hotbar hides and the backpack's own strip still moves items.

## Resources, gathering and boosts (GDD §53)

Owner decisions 2026-10-28:
- Materials can go back into runs, but the carried-in amount never gets the Center 2×.
- Boosts pause between runs.
- Every gathering hit drops material on the ground, and better tools take more node health per hit.
- Nodes regrow on tiered timers, and every region has basic resources.
- New gatherable items with no use yet, creature ore drops, and Fiber in planters.

Automated:
- **Vault and carry-in** (`admission`, `extraction`, `review_lifecycle`, `catalog_migration`, `trade_materials`):
  - Withdrawing a vault material is all-or-nothing into the lobby backpack, and a deploy carries materials.
  - The carried-in record is saved at Play and survives checkpoints, reloads and migration.
  - The Center multiplier settles min(extracted, carried in) at 1× and the rest at 2×: bring 100 Wood and extract 160 → 220; extract only 40 → 40.
  - Deposits over 1,000 are deleted and recorded.
- **Boost pause** (`boost_pause.spec.luau`):
  - Extraction saves the remaining time; the next deploy resumes the same time, and time in the lobby doesn't count.
  - Death or leaving clears saved boosts.
  - A stronger boost still takes over a resumed one.
  - Saves are sanitized.
- **Gathering** (`gathering_drops.spec.luau`, `gathering_tiers`, `building`):
  - Drops per hit follow tool rank against node rank, use the same node health, and the last hit is clamped.
  - Ores need their pickaxe; plants give 1 per hit.
  - Mastery adds extra drops without using health; Flint and Resin bonuses still drop.
  - Pickups: the gatherer has a 10 s window, drops despawn after 120 s, each is claimed once, and a full inventory leaves it on the ground.
  - Regrow times follow the tiers; every biome has basics.
  - The new items are sellable and not tradeable.
  - Creature ore drops; the Fiber crop.

Placeholders:
- Node health: trees and rocks 12, plants and bushes 3, Copper to Cobalt 8, Mithril 6, Obsidian and Jade 5, new nodes 4.
- Regrowth: 2 / 3 / 5 / 8 minutes.
- Sell values for the new items: Clay 2 up to Starstone and Stormglass 40.
- The Fiber crop costs 3 Fiber and grows 12 in 240 s.

Studio and live checks:

- [ ] Vault → pick ×10 and click Wood: 10 Wood moves to the lobby backpack. Deploy: the Wood is in the run inventory.
- [ ] Bring 100 Wood, gather 60 more, and extract at the Center: the receipt shows 100 "brought in, not doubled" and 120 from the gathered 60, so the vault gains 220.
- [ ] Drink a Sunberry Draught, extract with 6:00 left, and wait in the lobby: the next deploy shows about 6:00 on the HUD. Die with a boost running: it's gone on the next deploy.
- [ ] Hit a tree by hand: 1 Wood drops beside it. With a Stone axe, 3 drop and the tree empties in 4 hits.
- [ ] A friend can't pick up your drop for 10 s, then can. Drops vanish after 2 minutes.
- [ ] Walking over a drop collects it, and so does pressing F on it. Check F still harvests a node when drops lie beside it.
- [ ] An emptied Copper node regrows after about 3 minutes, a Mithril node after about 8.
- [ ] Clay, mushrooms, shrubs, Amethyst, Starstone and Stormglass nodes can be gathered, banked and sold, and are not offered in trades.
- [ ] Plant Fiber in a planter (H key): it grows 12 Fiber.
- [ ] The planter's gamepad key (R1) doesn't fight the hotbar step or build placement.

## Play-world map and creatures (GDD §54)

Owner request 2026-10-28: a small, playable placeholder world MVP. It has the new layout, the wildlife roster with roaming spawns, creature events, placeholder nodes and the Keep ritual.

**Map** (generated at server start when no authored `ShatteredCrater` model exists):
- A terrain island about 3,900 studs across inside a 6,144-stud ocean. −Z is north.
- Zones:
  - Low: Rimlands (south coast), Pinewood Wilds (NW), Mosswick Forest (NE), Riverlands (E).
  - Medium: Timberwatch (W), Fallen Temple (SW), Emberhollow Caves (SE hill, with a 450 × 350 interior reached by a tunnel from the south).
  - Extreme: Frostpeak Ridge (N, peaks 596/505/470), Crater Lake (centre, water level 28), Shattered Keep (island plateau 120, courtyard 180 × 220).
- One river runs from the lake through the Riverlands to the sea. A land bridge from the south and a ford from the east reach the Keep.
- Portals:
  - Low: Driftwood Cove, Elder Grove, Reed Ferry.
  - Medium: Lookout Gate, Temple Steps, Ember Gate.
  - Center: Crater Heart, on the Keep's lower terrace.
  - Hidden: Sunken Shrine.
- Safe camps: Tidewater (Rimlands) and Mossfire (Mosswick).
- The Guardian fights in the Keep courtyard. Ritual altars: Keep West and Keep North.
- 57 spawn points, in Low and Medium zones only.
- About 1,260 nodes, with basics in every zone. Mithril, Starstone and Stormglass appear only in Extreme zones; Frost shrubs only on Frostpeak.

**Creatures:**
- Roaming wildlife: 25 groups, about 52 creatures (cap 60). A group respawns 180 s after it dies, at least 150 studs from players and outside camps.
- Behaviour:
  - Passive animals flee and never hurt anyone.
  - A Neutral group fights back for 20 s after it is hurt.
  - Hostile creatures attack on sight.
- Events: Skeleton Patrol, Woolly Mammoth, Giant Ground Sloth, Ancient Tortoise, Iron-Tusk Boar with boars, Saber-Toothed Tiger, Stonehide Rhino, Ember Wisps (cave), and the Crater Gorilla boss.
- The Minotaur is now the Keep's ritual boss (3 Ancient Ember + 50 Iron Ore). The Ember Titan and Bandits are removed. Raider Camp and Warlord's Hold are guarded by Skeletons.

Automated:
- `world.spec`: zones, footprints, heights, POIs on dry ground in the right tier, `RandomPointIn`, node pools by tier.
- `wildlife.spec`: spawn tables, density, respawn rules, behaviours.
- `events.spec`: zone and habitat placement, no Bandits, camps guarded, no Minotaur event.
- `bosses.spec`: the Minotaur ritual.
- `gathering_drops`: fewer basics deeper in.

Placeholders: every creature stat, drop, group size and event weight; zone positions and heights; node counts per zone.

Studio and live checks:

- [ ] Server start prints "Built the placeholder island in X s"; note X. The server keeps running while it builds:
  - Matchmaking reports straight away.
  - Pressing Play before the island is ready says the world is still loading, and works once `FlintbornWorldReady` is set.
- [ ] In Studio, run `require(game.ServerScriptService.Server.Services.WorldBuildService).Generate()` from the command bar and save the place. The next start reuses the saved island without rebuilding it. Check the module path in the Explorer.
- [ ] Passive animals give a quarter of the usual kill XP and still count as hunts for quests.
- [ ] Walk or fly the coast and every zone boundary: no holes, floating terrain or cliffs you can't climb where routes should be. Frostpeak's summit reads as the tallest point.
- [ ] Walk the Crater Lake rim and cross to the Keep by the south land bridge and by the east ford (wading, not swimming). Climb the Keep ramp and the Fallen Temple ramp.
- [ ] Enter Emberhollow through the south tunnel: the interior is lit enough, its roof has no holes, and cave nodes and Ember Wisps stand on the cave floor.
- [ ] Spawns land in Low and Medium zones, never in water or terrain, and never in Extreme zones.
- [ ] Each portal (and the Center portal on the Keep) works; both safe camps protect players.
- [ ] Nodes sit on the ground across zones (none floating or underwater).
- [ ] Animals:
  - Rabbits, dodos, capybaras, stags, goats and tapirs flee.
  - Boars, bears, bison and mammoths ignore you until you hit them, then the group fights back and calms down after about 20 s.
  - Wolves, crocodiles and skeletons attack on sight.
- [ ] Kill a group and stay nearby: it doesn't respawn on top of you. About 3 minutes later a group is back somewhere else in that zone.
- [ ] Events appear in their zones and habitats: Mammoth on grassland, Tortoise by the lake, Ember Wisps inside the cave, the Crater Gorilla in a clearing toward the crater.
- [ ] Offer 3 Ancient Ember and 50 Iron Ore at a Keep altar: the Minotaur is summoned. A third party's hit breaks the summon and spills the offering.
- [ ] The Guardian fight works inside the courtyard walls.
- [ ] N opens the map: zones tinted by danger, zone names, the lake, river and points of interest, and a legend. It opens without a long freeze.
- [ ] With 20–30 players and about 50 creatures, the server holds frame rate. Note heartbeat and memory.
- [ ] Gamepad: in a planter, a tap on the fourth crop button switches Sapling ↔ Fiber, and holding it plants the crop shown.

## Knee-deep water, no swimming (GDD §55)

How it's built:
- Every water bed sits on the 4-stud voxel grid, with a quarter-full water voxel on top, which makes 1 stud of water.
- The lake bed is at 28. The river and creek step down in 4-stud stages. There are six marsh pools.
- A 64-stud shelf at 0 runs along the coast. An invisible wall stands 40 studs offshore, and the sea beyond it is deep.
- Swimming is disabled for players. Creatures always stand on the bed.
- Walking or sprinting with your feet in water runs at 70% speed; the Tidewalker perk adds back while wading. Creatures slow to 70% too.

Automated (`world.spec`, `survival.spec`):
- Water is 0.8–1.3 studs deep everywhere it can be reached.
- Beds are on the voxel grid.
- Everything placed is inside the wall.
- The lake can be waded and the bridge stays dry.
- Speed multipliers stack correctly.
- Stepping into or out of water never trips the pace check.

Studio and live checks:

- [ ] Water reaches about knee height on the default character, everywhere: lake, river, marsh pools and the coastal shelf. If a quarter-full water voxel renders too thin or not at all, raise `WATER_DEPTH` (IslandLayout) toward 1.3.
- [ ] Nothing ever swims: jump into the lake, the river and the sea shelf.
- [ ] Speed drops to 70% at the water's edge and comes back on dry ground, with no movement warnings or kicks.
- [ ] The offshore wall stops walking and jumping out to sea.
- [ ] The river's small step-down "rapids" and the shorelines look acceptable; the ocean surface meets the shelf without a seam.
- [ ] Creatures wade on the bed at reduced speed.

## Rebuilt UI: the shared kit and the seven lobby screens

How it's built: every screen comes from one kit (`src/client/Hud/Kit`, tokens in `src/shared/UI/KitTokens.json`) and the `lk_` sprites; the lobby screens live in `src/client/Hud/Screens/` (`LobbyHud`, `InventoryWindow`, `SettingsWindow`, `PartyWindow`, `PlayWindow`, `RecipeWindow`, `JournalWindow`) and are driven by their controllers. Contract: `docs/ui/ARCHITECTURE.md` (§12 decisions win); per-screen specs in `docs/ui/`; status in `docs/ui/UI_PROGRESS.md`. Until the `lk_` sprites are uploaded, screens in game draw the kit's fallback look (flat paper and leather plates).

Automated: `tests/luau/run.py` (`party_ready`, `followup_party`, `forge`, `forge_batch`, `party_model`, `lobby_hud_model`, `item_info`, `settings`, `hud_model` and the rest); `python3 art/ui/capture/capture.py <scene>` renders `kit_gallery`, `lobby_hud*`, `inventory_*`, `settings*`, `party*`, `play*`, `forge*`, `crafting*`, `journal*`, `world_hud*`, `world_overlays*`, `notices`, `world_menu`, `market_flow`, `trade_flow`, `progress_flow` and `map_flow`, and the `*_flow` scenes drive each controller against mocked remotes.

Studio and live checks (desktop, touch and controller unless stated):

- [ ] **Lobby HUD:** player card, Coins, Gems, gear, the 2 × 3 tiles, the PARTY n/8 panel, the XP bar and the six-slot hotbar sit where `01_hud.png` has them and stay clear of the Roblox top bar; the hotbar shows what the next run's hotbar will hold.
- [ ] **One window at a time:** opening any window closes the one before; the world behind dims (and blurs on Medium and High graphics); ✕, Escape and gamepad B close the top layer, a confirm dialog before its window.
- [ ] **Play window deploy flow (leader or solo):** the portal tile opens PLAY; the rows show the real party (crown, level, ready dot) and the predicted hotbar plus "+N more in backpack". PLAY with an empty backpack deploys at once; otherwise the "TAKE THESE INTO THE RUN?" dialog lists every item (★ Permanent, ×quantity) and ENTER deploys while CANCEL changes nothing. With a party not all ready the dialog adds "k of n party members are ready" but ENTER still works. While the deploy runs the button is busy; a failed deploy says why and nothing is lost. If the backpack cannot be read, "COULD NOT READ YOUR BACKPACK" offers ENTER ANYWAY.
- [ ] **Play window (party member):** the big button is the READY / NOT READY toggle with "The party leader starts the run"; it never deploys.
- [ ] **Party Ready toggle:** your own badge in READIED STATUS toggles Ready for you only, also when solo, and every member sees the change within a moment. Ready clears for everyone involved when someone accepts an invite, leaves or disconnects, and for the whole group when the leader deploys (also after a failed deploy). Spamming the toggle is throttled, never desynchronised.
- [ ] **Party window:** YOUR PARTY lists members with Leader badge and crown, then Empty Slot rows (seven visible, the eighth scrolls); INVITE PLAYERS searches by name; a leader's Invite turns to "Invited" (disabled) until the player answers; non-leaders read "Only the party leader can invite"; incoming invitations show Accept / Decline with the inviter's name; PARTY DETAILS shows Party Leader, Members n / 8, Join Type "Invite Only" and Created ("Just now", "5 min ago"); LEAVE PARTY appears only in a party of two or more.
- [ ] **Batch forging:** in the Forge, QUANTITY steps from 1 up to the most the vault can pay for (at most 10) and is hidden for Permanent conversions; FORGE ×N charges N times the inputs and puts all N results in the lobby backpack, or refuses the whole batch (short materials or a full backpack) without spending anything; a slow connection never charges twice; XP and Crafting mastery match N single crafts.
- [ ] **Forge, other states:** locked recipes show what unlocks them and cannot be forged; short inputs show their owned count in red; a Permanent conversion picks the source item, asks through the confirm dialog naming the exact item and the Permanent rules, arms after the delay and converts only that piece.
- [ ] **Field crafting (run):** V opens the same window in crafting mode; counts follow the backpack live; nearby stations enable their recipes; smelting takes the stepper's batch or Craft all; the job bar shows progress and STOP keeps the bars made.
- [ ] **Inventory Store / Take (lobby):** Tab and the backpack tile open Inventory on the Backpack tab; STORE IN VAULT moves the chosen item; on the Vault tab (its label shows used / capacity) TAKE brings an item back and a material's stepper takes the chosen amount or All; STORE ALL vaults what fits and says how many overflowed; a near-full material deposit asks first and deletes only what it said; a full vault links to Shop → Offers.
- [ ] **Inventory (run):** the window shows the 50 backpack slots, the six hotbar slots with their keys and the three armour slots; EQUIP, wear, USE and DROP work; categories All / Tools / Materials / Food / Misc and search filter the grid; item icons show for every item.
- [ ] **Settings tabs:** Gameplay, Audio, Graphics and Controls each show their page (Accessibility options live under Graphics and Audio); the selected tab is the leather one; APPLY stays disabled until something changes, saves, and survives a rejoin; RESET restores only the open tab; closing without APPLY keeps the old values; rebinding from Gameplay and Controls swaps clashing keys and refuses reserved ones; Replay Tutorial works.
- [ ] **Quest Journal:** the scroll tile opens it; the book tab lists quests (Daily first), trophy shows progression, the map pin the island map and the party tab opens the Party window; CLAIM pays a finished quest once and then reads CLAIMED; the progress line counts completed quests.
- [ ] **Restyled windows:** Market (Shop, Sell, Offers, Codes), Trade, Progress, world map, loot (body) and storage chest windows use the kit plates; body, chest and trade rows show each item's own icon (from the server's catalog id), including the partner's offer.
- [ ] **Phone touch targets and readability (844 × 390 and a small phone):** every window fills the screen; buttons, tabs, rows, steppers, ✕ and the Ready toggle are tappable without hitting a neighbour (about 44 screen px); body text stays readable (note any line under about 9 px); nothing sits under the notch or the Roblox top bar; tooltips appear on long-press.
- [ ] **Gamepad navigation:** opening a window selects its default control and closing it returns selection to where it was; the D-pad reaches every tile, tab, row, slot, stepper and button in a sensible order (lobby HUD: card → tiles → hotbar, top-right → party panel); A presses, B closes; the selection cue is the kit's hover look, never Roblox's default box.
- [ ] **In-world HUD and overlays:** vitals, compass, objective and event cards, party frames, the hotbar and notices use the kit look and stay readable on phone, desktop and console sizes.

## UI images on phones (SpriteLoader pacing)

How it's built: `Hud/SpriteLoader` fetches HUD images one at a time (a single preload in flight), images on screen first, then hands each to every label that uses it; phones fetch a menu's art when it opens; a failed fetch is asked again later under the other spelling of the asset, and its labels try on their own after a few failures. Phones refused bursts of image requests (the first handful loaded, the rest failed), so the sprites are also packed into atlas images (`art/ui/pack_atlas.py`): `atlas_lobby` and `atlas_hud` for the lobby and the run HUD, `atlas_ui` for the kit every window shares (the Market, Progress and Trade windows need only it), `atlas_pieces` for the Crafting, Forge, Inventory, Journal and Settings pieces, `atlas_map` and `atlas_island` for the maps, and `atlas_window_<screen>_1/_2` holding each screen's window frame as two full-resolution tiles. Once uploaded, a screen fetches one to four images and draws every sprite as its rectangle of one. Phones drew Roblox's own 9-slice of an atlas rectangle wrongly (pieces cut, shifted or taken from neighbouring sprites), so `Widgets.Sprite` draws a sliced atlas sprite as nine plain atlas rectangles; every device also prefetches closed menus' atlases after what is on screen, so menus open with their art loaded. Roblox applies text-size caps in screen pixels after UIScale, so `Widgets.TextCap` scales each cap with the window. The rebuilt screens draw the kit's `lk_` sprites from the `atlas_lk_*` atlases (ARCHITECTURE §6) once uploaded; the older atlases stay until then. Automated: `capture.py sprite_loader_flow`. Device reports: each client sends its image states 30 s and 2 min after joining; the "Probe UI images in a live place" workflow on main prints them (reports = true).

- [ ] On a phone, on a fresh server: every lobby plate, tile, coin and gem appears within a few seconds of joining.
- [ ] On a phone, each menu's art appears within a second or two of opening it, and the in-world HUD's art appears when a run starts.
- [ ] On a phone: quest rows, tabs, BUY buttons, the search box and the hotbar slots keep their rounded ends and arrows (no cut or shifted pieces), and tab and button labels stay their designed size.
- [ ] F9 → Client log shows no repeating image errors.
