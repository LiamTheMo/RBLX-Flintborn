# Flintborn — Game Design Document

> **Status:** Initial design draft (pre-production)  
> **Design revision:** 0.1  
> **Last updated:** 2026-10-21  
> **Project:** Roblox / RBLX-Flintborn  
> **Genre:** Primitive-fantasy survival sandbox / PvPvE extraction  
> **Primary references:** Rust-style building and raiding, Booga Booga-style primitive progression, tactical extraction risk/reward  
> **Implementation status:** Concept only. This document does not imply any features are implemented.

## Document conventions

- **Confirmed:** Established in the project concept handoff or later design discussions. Preserve unless explicitly revised.
- **Proposed:** A design recommendation for evaluation and playtesting, **not** an approved requirement.
- **Open:** A decision required before the relevant system is implemented.
- Numerical values outside confirmed design are **starting hypotheses**, not final balance.

This GDD is the source of truth for gameplay intent. Engineering contracts, tuning tables, art briefs, and implementation tasks should reference it rather than silently changing its rules.

## 1. High concept

**Pitch:** Spawn at the edge of a fractured island with almost nothing. Gather, craft, establish a raidable tribal stronghold, and venture deeper to fight rival players and ancient monsters for enchanted loot. Carry your prizes to a dangerous extraction rune to secure them in a permanent vault. Fail, and others take what you carried.

**Unique proposition:** The strategic tension of an extraction game **without firearms**: stone and metal arms, spears, bows, tribal equipment, enchanted blades, and elemental magic. Combat, transport, raiding, and map control all happen in a primitive-fantasy setting.

**Intended player fantasy:** “I started with stone tools, fought over a legendary relic, escaped a rival tribe, and brought it home.”

### 1.1 Design pillars — Confirmed

1. **Risk is voluntary but meaningful.** Safer outer routes provide a viable exit; deeper objectives pay more and attract other players.
2. **Everything carried is at stake.** On death, the character drops carried loot; only successfully extracted items are protected.
3. **Survival and crafting matter.** Players harvest, craft weapons and armor, build forward bases, and manage resources in the field.
4. **The world creates PvPvE conflicts.** Announced resource crashes, caches, elite creatures, and a recurring central boss drive player movement.
5. **Primitive fantasy, not military extraction.** No firearms at any equipment tier. Magic supplements, rather than replaces, primitive weapons.
6. **Multiple paths to value.** Hunting, harvesting, ambushing, participating in events, and raiding undefended bases must all remain legitimate options.

### 1.2 Design guardrails — Proposed

- Avoid unavoidable busywork (extreme hunger/thirst upkeep, long empty travel, repeated re-crafting after every trivial mistake).
- Avoid a “rich get richer” lockout where fresh spawns cannot make progress.
- Prioritize readable telegraphs and counterplay over surprise one-hit kills.
- Never sell combat power or guaranteed extracted rare loot for Robux; cosmetics and convenience that does not influence outcomes are safer monetization directions.
- Keep the full loop understandable to a first-time Roblox player, including touch/controller input.

## 2. Core run structure

### 2.1 Primary loop — Confirmed

1. **Deploy:** Enter an active island session at the low-risk Outer Rim with minimal equipment.
2. **Scavenge:** Gather wood, stone, flora, and other materials; create tools, weapons, shelter, and supplies.
3. **Prepare:** Craft/upgrade gear; optionally join a tribe and establish a forward operating base (FOB).
4. **Take a risk:** Explore the Inner Ring, contest broadcast events, raid exposed bases, or challenge the Center Crater boss.
5. **Carry the prize:** Valuable items physically occupy the player's carried inventory; rare/event loot exposes a visual trail.
6. **Extract:** Reach a rune or portal and complete extraction to transfer eligible carried rewards to an unraidable persistent vault.
7. **Repeat:** Redeploy with a new plan and optional equipment drawn from the vault (withdrawal rules still **Open**).

### 2.2 Loss and persistence contract

| Domain | Established behavior | Design status |
| --- | --- | --- |
| On-person inventory | Drops on death and can be claimed by others | **Confirmed** |
| Successfully extracted loot | Secure in a permanent, unraidable out-of-game vault | **Confirmed** |
| In-world base storage | Can be looted if opposing players raid the base | **Confirmed** |
| Gear withdrawn from vault for deployment | Exact redeployment and loss rules | **Open** |
| Player progress (recipes, cosmetics, reputation, etc.) | Whether and what persists | **Open** |
| Bases across sessions/server shutdowns | Session-only, timed-wipe, or persistent-world model | **Open** |
| Disconnects during combat/extraction | Anti-combat-log and reconnection policy | **Open** |

**Proposed consistency rule:** Once a vault item is withdrawn into a live run, it is at risk like any other carried item. This preserves extraction stakes, but requires a fair reconnect/disconnect policy.

## 3. World — The Shattered Crater

**Confirmed:** One seamless island with three concentric risk regions. The overall map funnels progression inward without making the center mandatory for all players.

| Region | Risk | Features | Typical reason to visit |
| --- | --- | --- | --- |
| **Outer Rim** | Low relative risk, not guaranteed PvP immunity | Starting beaches, woodland, wood/stone/flora, starter wildlife, hidden Minor Extraction Runes | Learn, craft, collect essentials, extract modest returns |
| **Inner Ring** | Medium | Dense jungle, dangerous fauna, obsidian/jade and other rare material locations, contested approaches | Upgrade, stage a FOB, intercept events, hunt alphas |
| **Center Crater** | Extreme | Open volcanic caldera with little/no natural cover, Mega-Boss spawner, central Permanent Extraction Portal | Legendary boss reward and maximum extraction-value opportunity |

### 3.1 Spatial rules — Confirmed

- Players begin at the outskirts rather than in the center.
- Rare objectives and high-value extraction routes increasingly expose players to conflict.
- A **50-meter no-build Holy Aura** protects **all extraction portals/runes** from player construction that would enclose or obstruct them.
- The Mega-Boss can destroy player-built structures near its arena, preventing structure-based fight exploits.
- Event objectives advertise their location with UI, map indicators, and visible sky beacons.

### 3.2 World-quality proposals

- Distribute several spawn areas around the rim to lower spawn camping and overcrowding.
- Provide multiple navigable routes between rings, plus short tactical sightline breaks in the jungle.
- Place hidden minor runes behind discoverable environmental cues; avoid putting every low-risk route on a single campable path.
- Use landmarks (giant roots, ruins, monoliths, volcanic ridge) so orientation works even without a minimap.
- Clearly visualize the no-build aura while the build tool is equipped.
- Avoid automatic zone-wide PvP immunity unless a future decision explicitly calls for it; “low risk” is not “safe.”

### 3.3 Map decisions — Open

- Island scale, Roblox studs-to-meters convention, desired traversal times, biome count, verticality, water travel, and player capacity.
- Fixed versus rotating extraction locations; whether map markers initially reveal minor runes.
- Respawn distribution, spawn protection, and anti-camping enforcement.
- Structures-per-area caps and construction proximity rules beyond extraction auras.

## 4. Primitive-fantasy progression

**Confirmed:** Progression begins with stone/wood and expands into metal, tribal equipment, enchanted arms, and elemental magic. **No firearms.**

### 4.1 Candidate gear ladder — Proposed, subject to balance

| Stage | Theme | Example materials | Example equipment | Acquisition emphasis |
| --- | --- | --- | --- | --- |
| Starter | Wood, stone, fiber | Wood, stone, vines, hide | Stone axe, wooden spear, sling, rough hide tunic | Outer Rim gathering |
| Early | Flint and bone | Flint, bone, leather | Flint knife, reinforced club, shortbow, hide shield | Crafting and low-tier enemies |
| Mid | Worked metals | Copper/bronze/iron (exact metallurgy TBD) | Metal spear, sword, axe, chain or scale armor | Deeper mining and workshops |
| Advanced | Volcanic and rare minerals | Obsidian, jade, special beast components | Obsidian blade, jade ward, heavy tribal armor | Inner Ring and alpha encounters |
| Endgame | Elemental / relic-infused | Abyssal meteor material, charged cores, boss relics | Ember spear, storm bow, runic armor, legendary relic | Broadcast events, raids, Mega-Boss |

**Important:** Stage labels are illustrative, **not** five confirmed tiers. Resource Crash explicitly uses a rare **Tier-5** resource; the complete item-tier taxonomy is **Open**.

### 4.2 Initial item families — Proposed

| Category | Examples | Design role |
| --- | --- | --- |
| Gathering | Stone axe, pickaxe, reinforced pick, sickle | Resource acquisition and contested harvest efficiency |
| Melee | Spear, club, knife, sword, war axe, hammer | Different reach, tempo, stagger, armor penetration |
| Ranged | Sling, bow, longbow, throwing spear, javelin | Mid-range pressure with recoverable/consumable ammunition |
| Defensive | Buckler, hide shield, tower shield, light/heavy tribal armor | Block, positioning, durability and stamina tradeoffs |
| Utility | Torch, rope, traps, healing wrap, smoke bundle | Survival, stealth, escape, siege and counterplay |
| Magic | Ember, frost, shock, nature/earth imbues | Status effects and tactical utility, never gun-like firearms |
| Construction | Walls, foundations, roofs, doors, gates, storage, workstations | Temporary strongholds and protected resource staging |
| Siege | Primitive breaching charges, fire pots, rams (TBD) | Counterplay to fortifications with clear costs and warning |

### 4.3 Enchantment principles — Proposed

- **Ember:** Damage-over-time/burning; countered by cleansing/water or positioning.
- **Frost:** Slow or brief control; control durations tightly capped in PvP.
- **Storm:** Chain/interrupt or shield-pressure, with explicit target limits.
- **Earth/Nature:** Defensive wards or situational terrain/poison effects.
- Enchanted power should have cooldown, durability, stamina/mana cost, charge limit, or a comparable tradeoff.
- Make all status effects legible on Roblox-scale characters and mobile screens.
- Rare enchantments modify how primitive weapons are used; they should not turn combat into sustained automatic projectile fire.

### 4.4 Crafting questions — Open

Recipe discovery/unlocks; durability/repair; encumbrance; resource stack sizes; ammo recovery; equipment weight and stamina; whether magic requires a dedicated catalyst; item binding/trading; and whether equipment or crafted material can be permanently withdrawn/deployed from the vault.

## 5. Combat and PvP

### 5.1 Intended combat identity — Confirmed / Proposed

- **Confirmed:** Combat relies on primitive melee, bows, thrown weapons, armor, and elemental effects; encounters combine hostile fauna/bosses with player competition.
- **Proposed:** Readable melee arcs, directional/blockable attacks, brief commitment/recovery windows, sprint/dodge or sidestep movement, and distinct weapon reach.
- **Proposed:** Skill and positioning should matter even when equipment tiers differ. High-tier gear gives advantage, not unconditional wins.
- **Proposed:** Armor carries mobility/stamina tradeoffs. Shields counter some frontal threats, flanking and heavy attacks counter shields.

### 5.2 Tribes and social systems — Open

Tribe size cap, friendly fire, invitations, permissions, loot rights, tribe base authorization, alliance rules, betrayal penalties (if any), and sharing rewards. Avoid designing core events assuming all players are in organized groups.

### 5.3 Fair-play requirements — Proposed

- Server-authoritative health/damage, loot ownership and drops, crafting costs, durability, building, event rewards and extraction outcomes.
- Validate attack distance, timings, rate limits, line-of-sight where relevant, inventory changes and tool provenance.
- Design anti-spawn-camp protections without creating exploitable invulnerability near valuable objectives.
- Offer solo players stealth, speed, traps or alternate extraction paths rather than requiring a large tribe.

## 6. Building, FOBs, and raiding

**Confirmed:** Players can create modular Rust-like structures, from wooden beach huts to fortified stone towers. Bases hold loot and can be raided. An undefended FOB is a legitimate target while its owners chase events.

### 6.1 Building loop — Proposed

1. Harvest building resources and craft a construction tool.
2. Place snap-aligned foundations, walls, floors, roofs, doors, and storage.
3. Upgrade structural materials, reinforce entrances, and place functional workstations.
4. Establish a forward base near (but not inside) valuable zones.
5. Defend against rival raids or abandon the base and extract before it falls.

### 6.2 Structural principles — Confirmed / Proposed

- **Confirmed:** No building within **50 meters** of any extraction portal/rune.
- **Confirmed:** Mega-Boss area attacks can splinter nearby builds; do not permit wall-cheese against boss mechanics.
- **Proposed:** Additional build exclusion at spawn areas, boss interaction objectives, and event interactables to prevent trapping.
- **Proposed:** Access controls for tribe-owned doors/storage, plus bounded structure counts and physics complexity.
- **Proposed:** Breaching should cost resources and signal attackers; structural tiers should improve defense without making raids mathematically impossible.
- **Open:** Structural decay/upkeep, base ownership after logout, server wipes, door locks, and whether a fully offline base can be raided.

## 7. Dynamic server-wide events

**Confirmed shared event presentation:**

1. Server-wide stylized banner announces the event.
2. HUD/minimap marker shows a location or search radius.
3. Large colored beam or comparable world beacon marks the location.
4. Rare rewards and required interaction time create contestable objectives.

| Event | Confirmed encounter | Confirmed reward concept | Tactical tension |
| --- | --- | --- | --- |
| **Resource Crash / Abyssal Meteor** | Limited Tier-5 event node requiring sustained/special mining interaction | Rare reinforcement material for endgame bases | A miner is vulnerable while allies screen attackers |
| **Ancient Supply Cache** | Chest drops/arrives, requires **60 continuous seconds** to unlock | Pre-crafted high-tier weapons and raiding explosives | Area control and interruption under attack |
| **Alpha Mob** | Shadow Panther / Crystal Golem-style elite with protective pack | Glow-Fur, Charged Cores, magical modifiers | PvPvE hunt with third-party ambush risk |

**Interpretation note:** The handoff calls the meteor “un-mineable” yet also requires prolonged mining. This draft interprets it as **not harvestable by ordinary instant mining**, but harvestable through a special contested interaction. Exact tool and harvest requirements remain **Open**.

### 7.1 Event scheduler — Proposed

- Use a centrally controlled schedule with randomized locations and sufficient notice to rotate players across the map.
- Avoid excessive overlaps that spread the server too thin or conflict with the recurring Mega-Boss.
- Make rewards and ownership server-authoritative, resilient to repeated remote calls and reconnects.
- When interacting, show progress and interruption clearly. The Supply Cache unlock requires a continuous 60-second attempt; interruption should require a new uninterrupted attempt unless changed by design.

### 7.2 Event questions — Open

Spawn intervals, coexistence limits, reward quantity, whether players can steal progress, rarity distribution, event expiration, sound accessibility, exact-vs-radius disclosure, and whether a single tribe can repeatedly monopolize spawns.

## 8. Mega-Boss — The Guardian Awakening

**Confirmed:** A premier world event in the central caldera approximately **every 15–20 minutes**, contested by top-geared players and rival tribes.

### 8.1 Start sequence — Confirmed

- “Horn of War” broadcasts island-wide.
- Sky turns crimson; an audible horn signals danger.
- A **3-minute warning** leads into the boss emergence.
- Boss AoE can destroy player-built defenses near the arena.

### 8.2 Three-phase design — Confirmed

| Phase | Trigger | Boss behavior | Player decision |
| --- | --- | --- | --- |
| **I — The Shield** | Boss appears | Boss is invulnerable while external energy pillars survive | Split to destroy pillars while managing rival players |
| **II — The Gauntlet** | Pillars destroyed | Lethal melee, ranged and AoE mechanics | Commit damage, revive/retreat where supported, fight or evade opponents |
| **III — The Betrayal** | Boss at **25% health** | Primary **Legendary item drops during the fight**, before boss death | Compete for the relic, defend the carrier, or finish the boss |

### 8.3 Boss-fight proposals

- Telegraph lethal AoE with clear ground effects, animation anticipation and sound; avoid unexplained instant deaths.
- Keep a believable exit path, but make retreat cost time and risk.
- Separate **mid-fight Legendary drop** from potential boss-clear rewards to make the 25% betrayal meaningful.
- Prevent construction, pathfinding exploits, aggro dragging, and safe-distance projectile cheese.
- Use server-side unique reward IDs and item grant/drop records to prevent duplication.
- Do not award a participant automatic vault loot: players must still physically escape and extract.

### 8.4 Boss decisions — Open

Boss identity, scaling with player count, target priority, contribution rewards, reset/leash, encounter timeout, PvP friendly-fire effects, whether the Legendary drops once per encounter, and whether the timer resets from spawn or defeat.

## 9. Extraction and permanent vault

### 9.1 Confirmed extraction contract

- Players must **physically transport carried loot** to extraction runes/portals.
- Extraction transfers eligible items into a **persistent, unraidable vault** outside the live island run.
- Outer hidden Minor Extraction Runes offer a lower-risk escape with **modest value multipliers**.
- The Center Crater's main Permanent Extraction Portal offers the **highest value multiplier**.
- Death before successful extraction drops carried items for looting.
- All extraction sites have **50-meter no-build auras**.
- Carriers of event-exclusive resources/legendary boss gear reveal themselves through embers, shadow trails or similar visible particles (**Burden of Wealth**).

### 9.2 Proposed extraction interaction

1. Enter a clearly marked activation zone with carried items.
2. Start a visible, interruptible channel (duration **TBD**).
3. Defend or evade while nearby players can detect/contest the attempt (notification scope **TBD**).
4. After server validation, atomically remove the successfully extracted items from the run and commit them to secure vault storage.
5. Display a receipt/summary and return to the lobby or redeployment flow (destination **TBD**).

**Proposed anti-camping protections:** Multiple minor exits, sightline design, disclosed activation windows, temporary portal downtime/rotation if required by testing. Do **not** make every portal permanently safe; risk is the point.

### 9.3 Value multiplier guardrail — Proposed

Multipliers should apply to **valuation/payout**, not produce copies of unique loot or quest-critical crafting materials. Define a stable base value and a bonus per portal type, then tune with data. Rare items should remain rare after extraction.

### 9.4 Vault/transaction guardrail — Proposed

Treat extract, death, disconnect, and item pickup as competing server-authoritative state transitions. Give item instances unique IDs; use idempotent persistence/receipt processing and a transaction model that prevents either disappearing items or duplicate permanent inventory. A client UI animation must never be proof of successful extraction.

### 9.5 Extraction decisions — Open

Channel duration and interrupt rules, portal reveal/rotation, exact valuation formula, party extraction and distribution, partial vs full backpack extraction, how extracted materials are used, vault capacity/organization, lobby experience, reconnect behavior, and whether the central portal is usable while the boss is alive.

## 10. Economy, stakes and balancing

### 10.1 Three economic locations

| Location | Risk profile | Meaning |
| --- | --- | --- |
| **Carried inventory** | Highest | Active stakes; dropped on death |
| **In-world base stash** | Raid risk | Can stage larger expeditions but opponents can breach and steal |
| **Persistent vault** | Secure | Only confirmed safe store for successful extraction |

**Confirmed:** Event materials, crafted weapons, raiding resources, and boss loot form the world economy.  
**Open:** Trading/market systems, vault withdrawals, currency definitions, sink mechanisms, recipe costs and rarity curves.

### 10.2 Balance hypotheses — Proposed

- Outer Rim players should be able to complete a modest extract without needing a tribe or boss loot.
- Inner Ring creates meaningful upgrades before requiring the Center Crater.
- Event rewards should justify travel and exposure without being mandatory for every competitive build.
- Raiding cost should scale with structure grade and target contents; avoid free repeated base destruction.
- A visible rare-loot burden should create tension but not provide global wallhack-style tracking.
- Repeated attempts should offer skill growth; the best strategy should not be idling safely until a dominant tribe wins.

### 10.3 Playtest measures

First extraction rate/time; loss-on-death rate; success by solo/duo/tribe; extraction share by portal; median equipment gap in PvP; event contest rate; boss participation/clear rate; legendary secured-vs-dropped ratio; base raid profit/cost; time spent travelling, harvesting, fighting and waiting; new-player return rate.

## 11. Player-facing interface and accessibility

**Required design surfaces — Proposed (not implemented):**

- **Lobby / vault:** Vault inventory, loadout/deployment decisions, run results and risk explanation.
- **In-world HUD:** Health, stamina, equipped primitive weapon, inventory burden, compass/minimap, extraction information and event markers.
- **Crafting/building:** Recipe requirements, snap previews, construction restrictions and durability.
- **Event UI:** Clear announcement, direction/search radius, beacon color and event time state.
- **Boss UI:** Three-phase status, 3-minute warning, pillar progress and readable 25% phase transition.
- **Extraction UI:** Site name, projected bonus, channel status, interrupt warning and final verified receipt.
- **Death UI:** Clear loss summary plus next-run action.

Make major cues redundant across color, icon, words and sound. Provide comfortable interactions on Roblox mobile, desktop and controller; avoid interactions that require precise cursor control.

## 12. Technical direction (architecture proposal, not implementation)

This section records intent so later Luau/Rojo architecture serves the game rules; there is **no game code in the repository yet**.

### 12.1 Authority boundaries

- **Client:** Input, animations, local UI, prediction, non-authoritative audiovisual effects.
- **Server:** Damage and status, material grants, inventory ownership, loot drops, structure placement/health, crafting, events, boss state, portal eligibility, extraction transactions, vault writes.
- **Shared definitions:** Typed item catalog, tags, combat/status definitions, event/biome IDs, validated protocol shapes and tunable balance values.

### 12.2 Candidate service boundaries

`SessionService` (deploy/reconnect), `InventoryService` (items, drops, transfer), `VaultService` (persistent stores), `ExtractionService` (portal state and atomic handoff), `ResourceService`, `CraftingService`, `BuildingService`, `CombatService`, `TribeService`, `EventDirector`, `BossService`, and `WorldRulesService`.

**Important invariants for code review:**

1. No client-created rare items or client-declared combat hits without server validation.
2. No player-built structure can exist within an extraction no-build zone.
3. An item cannot simultaneously exist in world loot, carried inventory, and permanent vault.
4. Extraction has an explicit persisted success/failure outcome; retries cannot duplicate items.
5. Boss Legendary release at 25% occurs at most once per encounter.
6. Only `main` may trigger production publishing workflows; development branches never publish.

### 12.3 Platform and performance considerations — Proposed

- Use Roblox DataStores/persistent storage patterns with careful retry budgets, versioned schemas and migration handling.
- Use spatial partitioning, streaming-compatible props, capped loose loot/build pieces, pooled effects and server budgets.
- Profile real mobile devices and full servers, not only Roblox Studio solo testing.
- Ensure server-owned timers and reward grants survive player disconnects without repeat claims.
- Determine cross-server economy and session design before promising persistent bases.

## 13. Initial vertical slice (recommended development order)

The first milestone should prove the **risk → loot → extraction → vault** loop before implementing a full open world.

| Slice increment | Included | Acceptance criteria |
| --- | --- | --- |
| **A. Gather/craft** | Small outer-rim test arena; wood/stone; axe/spear; basic inventory | A new player can gather, craft and equip without admin commands |
| **B. Fight/lose** | Primitive PvE enemy; basic PvP; dropped backpack/loot | Death drops correct eligible items; server rejects invalid combat/inventory requests |
| **C. Extract/secure** | One minor rune; channel; persistent vault | Extracted loot survives rejoin; interrupted extracts do not grant loot; retries do not duplicate |
| **D. Build/raid** | Foundations/walls/door/stash; damage and breaching; no-build aura | Another player can attack/loot stash; portal cannot be blocked |
| **E. Contest** | One broadcast cache or alpha event; beacon; rare item carrying effect | Competing players can find, fight over and extract the objective |
| **F. Center encounter** | Boss prototype with pillars, attack cycle, 25% drop, central portal | Mid-fight Legendary appears once; boss structures cannot cheese; relic must be extracted |

### 13.1 Explicit non-goals for the first slice

Full island art, every biome, elaborate weather, large equipment catalog, trading/auction house, polished monetization, cross-server base persistence, advanced tribe diplomacy, and every elemental school.

### 13.2 Documentation validation checklist

- [x] Project title is Flintborn; primitive-fantasy equipment; no firearms.
- [x] Full run loop, three world zones and vault/death stakes documented.
- [x] Three event families and exact known 60-second cache rule recorded.
- [x] Mega-Boss cadence, 3-minute alert, three phases and 25% drop recorded.
- [x] All portals covered by the 50-meter no-build rule.
- [x] Proposed mechanics explicitly differentiated from confirmed design.
- [ ] Prototype tests and runtime/CI validation — **not applicable yet; no game source exists**.
- [ ] Design-owner decisions for outstanding systems — **pending**.

## 14. Decision backlog (priority order)

| Priority | Decision | Why it matters |
| --- | --- | --- |
| **P0** | Run/session model, vault withdrawal and what persists between servers | Inventory authority, saved data, base lifecycle, player stakes |
| **P0** | Death, disconnect, reconnect and combat-logging policy | Exploit resistance and player trust |
| **P0** | Portal activation/interrupt logic and multiplier definition | Core extraction risk and economy correctness |
| **P0** | Server population, solo/tribe sizes, and PvP rules | Map size, reward access, balance and performance |
| **P1** | Weapons, stamina/blocking, hit detection, magic resources | Combat feel and network design |
| **P1** | Build/raid costs, protected zones, raid time and structure upkeep | Base fairness and grief prevention |
| **P1** | Event schedule/loot tables, boss loot distribution and reset logic | Server pacing and endgame |
| **P1** | Biomes, distances, terrain elevation, portals and spawn points | World prototyping and movement |
| **P2** | Progression unlocks, repair/durability, currency and trading | Long-term item economy |
| **P2** | UI art direction, onboarding and optional cosmetics | Presentation and retention |

## 15. Design change log

| Revision | Date | Change |
| --- | --- | --- |
| **0.1** | 2026-10-21 | Created Flintborn GDD from the original primitive extraction handoff; recorded primitive-fantasy/no-firearms direction; added proposed systems, technical guardrails, vertical slice and decision backlog. |

---

**Working principle:** Protect the identity of Flintborn: **primitive survival + raidable preparation + contested world events + visible high-value loot + manual extraction + persistent secure vault**. Proposed features are not final decisions until approved and tested.
