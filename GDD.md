# Flintborn — Game Design Document

> **Status:** Comprehensive pre-production specification (not implemented)  
> **Design revision:** 0.7  
> **Last updated:** 2026-10-22  
> **Project:** Roblox / RBLX-Flintborn  
> **Genre:** Primitive-fantasy survival sandbox / PvPvE extraction  
> **Primary references:** Rust-style building and raiding, Booga Booga-style primitive progression, tactical extraction risk/reward  
> **Implementation status:** Concept only. This document does not imply any features are implemented.

## Document conventions

- **Confirmed:** Established in the project concept handoff or later design discussions. Preserve unless explicitly revised.
- **Proposed:** A design recommendation for evaluation and playtesting, **not** an approved requirement.
- **Open:** A decision required before the relevant system is implemented.
- **Working default:** A coherent starting rule for prototyping, not yet approved by the design owner.
- Numerical values outside confirmed design are **starting hypotheses**, not final balance.

**New confirmed direction (2026-10-21):** Extracted resources enable special crafting and expensive eligible-item Permanent conversion. **Confirmed after later clarification:** Permanent gear survives owner death, stays at the **same stats** as its source and may be manually dropped, stolen or traded. Gear does **not** wear/break, and exact Permanent recovery material fee and active-slot limit remain Open. All numerical costs are illustrative.

**Confirmed combat clarification (2026-10-21, extended 2026-10-22):** No player-usable shields, firearms or playable magic for launch. Medical consumables heal **immediately**, animation then prevents immediate repeat use; food heals over time with partial interruption on damage. The Guardian's shield-pillar boss phase remains unchanged.

**Confirmed decisions (2026-10-21):** Public island target **30 players**, adjusted for world size/performance; instance stays alive while populated and resets completely when empty. Death kicks the player from the world and is intended to prevent immediate same-world rejoining, while eligible surviving players may return to that running instance. Converted Permanent gear preserves original stats and survives death, but may be voluntarily dropped, stolen or traded. **Fixed extraction countdowns are shared server events** (120 seconds); eligible living players need to stand in a small exit zone **only at deadline**, free to hide, fight and heal beforehand. Alerts play audio/visual cues over a large radius. Active fixed extraction POIs vary by server; rare consumable runes enable **30-second anywhere** extractions. Extractions send players to the secure lobby. Protected pre-spawn menu, teleport safety, 10-minute corpses, no player shields and admin maintenance preservation remain confirmed (§34).

This GDD is the source of truth for gameplay intent. Engineering contracts, tuning tables, art briefs, and implementation tasks should reference it rather than silently changing its rules.

### Document navigation

- **Gameplay foundation:** [Core loop](#2-core-run-structure), [Shattered Crater map](#3-world--the-shattered-crater), [equipment](#4-primitive-fantasy-progression), [combat](#5-combat-and-pvp), [bases and raids](#6-building-fobs-and-raiding).
- **Contested objectives:** [Server-wide events](#7-dynamic-server-wide-events), [Mega-Boss](#8-mega-boss--the-guardian-awakening), [extraction and vault](#9-extraction-and-permanent-vault).
- **Long-term progression:** [Special crafting / Permanent rules](#15-cross-run-special-crafting-and-the-permanent-item-class), [Ancestral Forge](#16-the-ancestral-forge-crafting-outside-the-run), [Permanent gear policy](#17-permanent-gear-operational-rules), [material sources](#18-resource-tiers-economy-and-acquisition-sources), [recipe examples](#19-special-recipe-examples--proposed-balancing-placeholders).
- **Implementation:** [Inventory state transitions](#22-detailed-inventory-extraction-and-death-state-transitions), [Roblox architecture](#23-proposed-roblox-luau-services-and-persistence-model), [threat model](#24-economy-abuse-cases-and-anti-duplication-tests), [UX requirements](#25-ux-specifications-and-interface-inventory), [tuning plan](#26-quantitative-tuning-and-live-analytics-plan), [QA](#27-detailed-verification-matrix-and-qa-plan), [production phases](#28-production-milestones-and-documentation-maintenance).
- **Critical onboarding and live-world systems:** [10-minute lootable bodies](#29-ordinary-departure-death-and-lootable-bodies), [administrator safe updates](#30-administrator-update-kicks-and-maintenance-safe-preservation), [protected in-world Play menu and teleport safety](#31-protected-play-world-main-menu-and-teleport-safety-design), [events and building](#32-expanded-public-world-content-and-booga-booga-style-construction), [public-world playstyle rewards](#33-public-world-playstyle-rewards-and-engagement-design).

**Navigation links follow GitHub Markdown heading anchors; section numbers are stable only within this revision.**

## 1. High concept

**Pitch:** Arrive in a protected play-world menu, wait for loading, then press **Play** to spawn at a **random world location** and begin inventory risk. Harvest resources, craft primitive and metal gear, establish a raidable tribal base, fight other players and ancient creatures, and recover rare materials or relics. Extract via a contested server-wide countdown and return to the secure lobby; death sends the player back to the lobby with unsecured loot left behind.

**Unique proposition:** A primitive survival/extraction game **without firearms, player shields, or player-cast magic at launch**. The playable combat baseline is **click melee and slow, visible bow projectiles with crafted arrows**, supported by health, sprint-only stamina, food, instant medical heals and tribe revives. Ancient and elemental **enemies** can still fit the mythology.

**Intended player fantasy:** “I started with stone tools, fought over a legendary relic, escaped a rival tribe, and brought it home.”

### 1.1 Design pillars — Confirmed

1. **Risk is voluntary but meaningful.** Safer outer routes provide a viable exit; deeper objectives pay more and attract other players.
2. **Risk begins only after successful Play admission.** Loading, teleport failures and the protected in-world main menu are loss-free. Once server-confirmed active gameplay starts, ordinary gear drops on death/leave as a **10-minute corpse**. Protected extraction and authorized update kicks are exceptions (§29–31); Permanent recovery remains Open (§15–17).
3. **Survival and crafting matter.** Players harvest, craft weapons and armor, build forward bases, and manage resources in the field.
4. **The world creates diverse PvPvE opportunities.** Meteors, rare shrubs/trees and material nodes, raidable structures, unusual mob and boss spawns, caches and the Guardian move players across the island.
5. **Primitive fantasy, not military extraction.** No firearms, equipable shields or playable magic at launch. Players wield melee weapons and crafted-arrow bows, survive using medicine and food, and build raidable bases with wood/stone/iron progression.
6. **Multiple paths to value.** Hunting, farming, building, ambushing, events and base raiding are all legitimate playstyles. Engaged players who remain in the public world can earn activity-based benefits without promoting AFK waiting.

### 1.2 Design guardrails — Proposed

- Survival meters at launch are **health, stamina and food only**; do **not** add thirst, temperature or weather-exposure survival meters by default. Exact food depletion/penalty rates remain Open.
- Avoid a “rich get richer” lockout where fresh spawns cannot make progress.
- Prioritize readable telegraphs and counterplay over surprise one-hit kills.
- Never sell combat power or guaranteed extracted rare loot for Robux; cosmetics and convenience that does not influence outcomes are safer monetization directions.
- Keep the full loop understandable to a first-time Roblox player, including touch/controller input.

## 2. Core run structure

### 2.1 Primary loop — Confirmed

1. **Prepare safely:** Travel to a play-world server and wait at its protected main menu until profile/assets are ready. **Explicitly click Play**; the server confirms a successful character spawn before making equipped ordinary gear at risk. Teleport/load/spawn failures never forfeit items.
2. **Scavenge:** Gather wood, stone, flora, and other materials; create tools, weapons, shelter, and supplies.
3. **Prepare:** Craft/upgrade gear; optionally join a tribe and establish a forward operating base (FOB).
4. **Take a risk:** Explore the Inner Ring, contest broadcast events, raid exposed bases, or challenge the Center Crater boss.
5. **Carry the prize:** Valuable items physically occupy the player's carried inventory; rare/event loot exposes a visual trail.
6. **Extract:** Activate a fixed exit's shared 120-second server timer (or a rare portable rune's 30-second timer), then be alive and within its zone **when it ends** to enter the protected animation and bank loot.
7. **Build long-term power:** Spend extracted ingredients on special recipes or save for costly Permanent conversions (confirmed mechanic; specific recipes proposed).
8. **Continue or extract:** Stay in the public world to build/farm/fight, or wait nearby for an extraction timer to end while you stand inside the small exit zone. Hiding, healing and fighting are allowed before the deadline. Active-world quits forfeit ordinary items; pre-spawn menu quits are safe.

### 2.2 Loss and persistence contract

| Domain | Established behavior | Design status |
| --- | --- | --- |
| On-person active-run inventory | Drops on death or ordinary departure **after successful Play admission**, leaving lootable **10-minute body** | **Confirmed** |
| Lobby or world main-menu departure | Safe regardless of teleport/load failures or pre-spawn kick | **Confirmed** |
| World admission | Only successful explicit Play/ready/spawn transition activates carried inventory risk | **Confirmed** |
| Protected extraction | **120-second shared fixed-site countdown** with large-radius cues; living players must be **inside zone only at completion**, not throughout. Portable runes use 30 seconds; invulnerability begins at animation start. | **Confirmed** |
| Administrator maintenance kick | Safe removal for game updates without losing held items | **Confirmed**; escrow details Proposed |
| Successfully extracted loot | Secure in a permanent, unraidable out-of-game vault | **Confirmed** |
| Extracted crafting resources | Feed special recipes and costly permanent conversions | **Confirmed** |
| Converted Permanent equipment | Survives death, **same stats as source**; deliberate drop/loot and trade can change ownership; only designated items qualify | **Confirmed**; recovery cost/slot cap Open |
| In-world base storage | Can be looted if opposing players raid the base | **Confirmed** |
| Gear withdrawn from vault for deployment | Extracted items and materials may be withdrawn, becoming ordinary at-risk gear on successful active Play admission | **Confirmed**; loadout limits Open |
| Player progression | Player **levels** and recipe **discovery** both exist | **Confirmed**; exact XP curve/unlock combinations Open |
| Bases and public world resets | Server resets its complete **in-world state only after it becomes empty** | **Confirmed**; scope of ordinary extracted vault storage needs clarification |
| Public world playstyles | Benefits for engaged PvPers, base-builders, farmers and other active playstyles | **Confirmed direction**; specific rewards Proposed |
| Disconnects during combat/extraction | Actual active-run disconnect leaves lootable body; **pre-spawn menu and loading are safe**; after protected extraction animation starts, disconnect is safe | **Confirmed**; crash reconciliation Open |

**Confirmed and clarification pending:** Ordinary vaulted items may be withdrawn and become at risk only when active play begins. Converted Permanent equipment remains with the owner on death, but deliberate drop or trade can transfer ownership. The **secure vault has upgradeable capacity**. Empty-server resets definitely erase live-world builds and materials. Whether they also erase ordinary **previously extracted** vault items is ambiguous and therefore still Open (§34.2); original cross-session secure-vault behavior remains the provisional interpretation.

## 3. World — The Shattered Crater

**Confirmed:** One seamless island with three concentric risk regions. The overall map funnels progression inward without making the center mandatory for all players.

| Region | Risk | Features | Typical reason to visit |
| --- | --- | --- | --- |
| **Outer Rim** | Low relative risk, not guaranteed PvP immunity | Starting beaches, woodland, wood/stone/flora, starter wildlife, hidden Minor Extraction Runes | Learn, craft, collect essentials, extract modest returns |
| **Inner Ring** | Medium | Dense jungle, dangerous fauna, obsidian/jade and other rare material locations, contested approaches | Upgrade, stage a FOB, intercept events, hunt alphas |
| **Center Crater** | Extreme | Open volcanic caldera with little/no natural cover, Mega-Boss spawner, central Permanent Extraction Portal | Legendary boss reward and maximum extraction-value opportunity |

### 3.1 Spatial rules — Confirmed

- After successful Play admission, the first risk-bearing character **spawns at a randomly selected valid location anywhere on the map**, not automatically on the outskirts. The protected loading menu remains loss-free. Precise spawn validation and whether designated safe-zone POIs may host spawns are Open.
- Rare objectives and high-value extraction routes increasingly expose players to conflict.
- A **50-meter no-build Holy Aura** protects **all extraction portals/runes** from player construction that would enclose or obstruct them.
- The Mega-Boss can destroy player-built structures near its arena, preventing structure-based fight exploits.
- Event objectives advertise their location with UI, map indicators, and visible sky beacons.

### 3.2 World-quality proposals

- Distribute valid **random spawn candidates across the whole island**, including appropriate Outer/Inner/Central geography as feasible; server validates terrain, crowding and world hazards. PvP is enabled unless the destination is a designated POI safe zone.
- Provide multiple navigable routes between rings, plus short tactical sightline breaks in the jungle.
- Place hidden minor runes behind discoverable environmental cues; avoid putting every low-risk route on a single campable path.
- Use landmarks (giant roots, ruins, monoliths, volcanic ridge) so orientation works even without a minimap.
- Clearly visualize the no-build aura while the build tool is equipped.
- **Confirmed:** PvP is enabled throughout the active world by default, including Outer Rim and random-spawn areas. **Only specifically designated POIs** may have a PvP safe zone; these must be visibly marked and server-enforced. The protected pre-spawn menu is not active gameplay.

### 3.3 Public-world capacity, lifetime and POIs — Confirmed / Open

- **Confirmed provisional limit:** 30 players per island, reconsidered after mapping and performance validation.
- **Confirmed world lifetime:** A public world persists while **any players remain**. When the last player leaves, that instance resets/ends; all bases, raidable structures, world loot, nodes, mobs and other live-world changes disappear. New servers initialize clean worlds.
- **Confirmed extraction POIs:** Candidate locations are fixed and recognizable across maps, but only a server-specific subset has an available extraction in each instance.
- **Confirmed same-world rejoin:** Players can return to their earlier still-running public instance if they have **not died and been kicked/excluded** and the server remains open/capacity permits. Ordinary active disconnect still leaves a 10-minute corpse and forfeits unsecured items; rejoining must not restore them.
- **Open:** Map size and travel times, server list/rejoin UX, spawn distribution, exact active-site selection/reveal, and anti-reentry after death implementation.
- **Ambiguity:** The user said “everything disappears, only Permanent items survive” on world reset. Live-world state clearly wipes; whether this also overrides the previously confirmed secure-vault persistence for ordinary extracted materials needs confirmation (§34.2).

## 4. Primitive progression, resource gathering and food

> **Confirmed launch constraints:** Primitive stone and metal weapons, crafted-arrow bows, nonmagical armor, healing medicines, food, and wood/stone/iron base building. **No player-cast magic, enchantment combat effects, firearms or player-usable shields at launch.** Supernatural enemies and rare ancient materials may exist; weapon magic is reserved as a **future-update possibility**, not an MVP system.

### 4.1 Harvesting and equipment progression

**Gathering** means acquiring world materials by interacting with resource nodes: **cutting down trees for wood, mining stone and iron ore, picking herbs/shrubs, harvesting plants and crops, and collecting creature-derived hides/bones**. Gathering is an economic action, **not** a fourth survival meter.

| Stage | Materials | Illustrative launch equipment | Gameplay function |
| --- | --- | --- | --- |
| Primitive | Wood, stone, fiber, common plant/animal drops | Stone axe, simple spear, simple bow, starter bandage | Cheap survival and resource harvesting |
| Early | Flint, bone, hide, herbs | Improved club, spear, simple armor, better bow, medical supplies | Early crafting and first PvP choices |
| Worked metal | Iron/available ore, processed hide | Iron axe, blade, spear, metal armor and stronger bow | Higher material investment and better combat tools |
| High rarity | Rare monster parts, meteors and boss/structure loot | Special **nonmagical** crafted gear and conversion-eligible items | Risk-driven loot and rare Permanent conversion |

**Confirmed:** Resource families added over time can extend gear and building progression, but initial construction progression is **wood → stone → iron**. The example weapons and precise stats remain Proposed. Rare crafting is independent of playable spellcasting.

### 4.2 Initial item families

| Family | Examples / rule |
| --- | --- |
| Harvesting tools | Axe, pickaxe, sickle; server validates harvest ranges and legitimate node yields |
| Melee weapons | Spears, clubs, axes, swords, daggers; **simple click-to-attack** at launch |
| Ranged weapons | At least bows; other ranged families (slings, javelins, crossbows) are possible future content, not all confirmed for launch |
| Ammunition | **Arrows must be crafted** and occupy a finite resource/inventory supply; projectile speed is deliberately slow and visible |
| Armor | Nonmagical protective clothing/leather/iron; **lasts indefinitely** rather than breaking or needing durability repairs |
| Medical items | Bandages, medical supplies and potions **restore health immediately on validated use**, then an animation imposes the usage cooldown |
| Food | Food meter exists; eating provides **healing over time**, partially interrupted by damage; exact food-drain rates, food list and effect sizes Open |
| Utility | Torches, storage supplies, farm tools, primitive traps and other nonmagical gear |
| Building | Placeable shelters/doors/storage/totems/farms and functional stations; initial wood, stone and iron tiers |
| Future (not launch) | Elemental spells, enchanted combat weapons, special defensive resistances and any charge/mana subsystem |

### 4.3 Survival attributes — Confirmed and Open

- **Health:** Damage removes HP; medical items restore HP **immediately** (subject to max-health cap). Death/downed behavior depends on tribe membership (§5).
- **Stamina:** **Only limits how long the player can sprint.** Melee attacks, crouching, gathering, bow shots, raiding and standard movement **do not consume stamina**. Stamina regen duration, sprint speed and UI thresholds are Open.
- **Food:** An active food system is included; **food consumption grants health regeneration over time**. Incoming damage **partially interrupts** that healing, but does not necessarily erase the whole effect. Exact interruption fraction, food meter depletion rate and starvation effects are Open.
- **Excluded at launch:** Thirst, temperature, magical energy/mana, shield meters, equipment durability and weather survival stats unless explicitly approved in a later revision.

### 4.4 Recipes and Permanent equipment

- Successfully **extracted** materials support special crafting; conversion targets only specifically designated equipment and **does not increase its stats**.
- Recipes are acquired through a combination of **player levels and discovery**; high-tier special recipes use multiple resource and event types.
- Weapons/armor **last indefinitely** through ordinary use. If Permanent ownership needs a post-death material payment for balance, that is a separate **Open recovery cost**, not wear-based durability.
- All enchantments, rune combat effects and spell recipes proposed in older sections are **future-update candidates**. Any existing named magical recipes (§19) are conceptual content backlog and **not approved launch recipes**.
- Exact item caps, inventory weight, crafting arrows per batch, crafting station limits and food-heal values remain Open.

### 4.5 Medical items, healing and food — Confirmed / Proposed details

| Item type | Server-side trigger | When HP changes | After-use behavior |
| --- | --- | --- | --- |
| Bandage / medical kit | Valid inventory item selected and consumed | **Immediately** at use activation | Play medical animation; block re-use during its duration |
| Potion | Valid single-use item selected and consumed | **Immediately** at use activation | Potion-drink animation acts as cooldown *after the heal* |
| Food | Valid edible consumed | **Over time** after eating | Food HoT ticks over a configured duration; damage partially interrupts active healing |

**Important:** A medical animation is the **cooldown**, not a pre-heal channel. Incoming damage cannot retroactively cancel an already applied instant medical heal. Repeated use requests during the animation must not apply another heal or consume another item. A player may still be attacked while animating; movement lock/speed during the animation remains Open.

**Food interruption working interpretation (Proposed):** If hit while food HoT is active, reduce the remaining scheduled healing rather than cancelling all future food healing. The precise percentage/duration behavior remains Open. Health cannot exceed its defined maximum without a separately approved rule.

**Potential item names** (Fiber Bandage, Herbal Poultice, Restorative Tonic, Healing Potion) and ingredients are examples, not official content. Unlimited-use medical gear and Permanent-converted healing consumables are excluded.



## 5. Combat, movement, tribes and revival

### 5.1 Launch combat baseline — Confirmed / Open

- **Confirmed for current design:** Basic click-to-attack melee; bow shots with **slower, clearly visible physical projectiles** and **crafted arrows**. Exact hitboxes, attack interval, damage, ranged arc/velocity and ammunition counts remain Open.
- **Confirmed:** Players can **sprint and crouch**. Stamina decreases **only while sprinting**; crouching and attacks do not require stamina. No dodge-roll or sliding system has been approved.
- **Confirmed:** No usable shield, blocking/guard-meter combat mechanic, player-cast magic or magical attacks for launch. Advanced weapon combos and alternate ranged families remain possible future decisions.
- **Confirmed:** PvP is enabled **everywhere in the active play world except clearly designated safe-zone POIs**. Random world spawning must honor safe player-admission initialization but does not automatically guarantee PvP immunity.
- **Proposed:** All damage and hit detection are server-validated with bounded latency compensation, distance/arc checks and rate limits. Different ordinary weapons may vary in reach, cadence or damage without needing complicated launch combat.
- **Open:** Friendly fire within a tribe and across alliances, spawn invulnerability if any, safe-zone list/boundaries, projectile travel speed, aim support on controller/mobile and damage scaling.

### 5.2 Tribe membership and social functions

- **Confirmed:** A tribe has a maximum of **8 players**. Players can **invite, kick and form alliances**.
- **Confirmed:** Tribes can establish claim ownership on **their own player-created structures** with totems; they **cannot claim server-generated structures**.
- **Confirmed:** **Storage in active public worlds is accessible to anyone**, including unrelated players and enemy tribes. A tribe claim never acts as a secure vault or private chest lock.
- **Open:** Alliance friendly-fire, whether rival access requires physically reaching/breaching a chest behind walls, tribe leadership transfer, exact totem claim radius and whether players can be in multiple alliances.
- **Proposed:** Tribe roster, invite/kick/alliances and in-world permissions are enforced by server, never by local UI. Tribe membership is validated at the moment a player is downed.

### 5.3 Downed, revive and death rules — Confirmed / Proposed mechanics

1. **Non-tribe solo player:** Takes lethal damage → **immediate death**. Ordinary items move to the 10-minute lootable body; the player is **ejected to the lobby**. No same-world respawn.
2. **Tribe member:** On would-be lethal damage, enters a **Downed** state instead of dying immediately. Start a **60-second rescue window** on a server-authoritative clock.
3. A valid **tribe member** can start reviving the downed player. While a revive interaction is actively in progress, **pause the remaining 60-second downed timer**; it cannot expire mid-revive.
4. If the revive interaction is **cancelled or interrupted**, resume the countdown from the **remaining time**, not from a new 60 seconds.
5. On a successful revive, the downed character resumes active play without a new Play/world re-entry or item-drop corpse. Exact revived HP, time to complete interaction and invulnerability if any are Open.
6. If 60 seconds of **unpaused** downed time elapse, or the downed player is finally eliminated through an approved mechanic, finish ordinary death/body creation and **send/eject them to the separate lobby**. There is **no respawn in the same world**.
7. Once dead/ejected, the player must wait for their tribe to return to lobby (or find a new party) before rejoining that tribe's expedition. Same-server death rejoin restriction remains in force.

**Critical abuse prevention:** Only server-validated, present and eligible tribe members can keep the revive timer paused. A disconnected/dead reviver, moved-out-of-range reviver or invalid/abandoned action cannot freeze a downed player indefinitely. Whether the downed person can crawl, be damaged/finished, consume healing items or be revived by an allied-but-not-same-tribe player remains **Open**. Never allow a downed body to extract simply because it lies in a portal zone.

### 5.4 Medicine, food and sprint timing

- **Medical item or potion:** Server confirms valid consumable, **immediately heals** and deducts one item exactly once. Begin **after-heal animation cooldown**; cannot immediately chain another medical item before cooldown ends.
- **Food:** Eating grants a timed healing-over-time effect. Taking damage **partially interrupts remaining HoT** according to a to-be-balanced rule (e.g., trimming some pending ticks as a *proposal*). No retroactive cancellation of completed healing.
- **Movement:** Sprint drains and is limited by stamina. Crouch does not, and stamina has **no melee/bow/building/harvesting cost**.
- **Downed:** Pending revive and death rules supersede medical-use/attack inputs while downed (exact allowed downed actions still Open).

### 5.5 Combat integrity and spawn safety

- Prohibit forged bow shots, impossible melee reach, modified projectile speed/hit position, zero-cost arrow duplication and replayed medical-use remotes.
- Validate safe POI boundaries server-side, including projectile origin and impact handling; exact outward/inward protection semantics remain Open.
- Protected play-world menu and unsuccessful Play admission remain safe; **successful spawn selects any valid random map location**, not necessarily the Outer Rim (§3).
- Same world death is terminal even for a tribe member who was not successfully revived. The body lasts **600 seconds**, and the server enforces same-JobId exclusion.
- **Proposed:** Eligible players may rejoin a still-running world after an ordinary accidental disconnect if they were not killed/ejected; unsecured carried loot still stays in their forfeited 10-minute body.



## 6. Booga Booga-style construction, claims, farms and raids

> **Confirmed:** Building behaves similarly to *Booga Booga*: fast, accessible placement of craftable primitive structures. A player's or tribe's base **stays in the public server after they leave**, allowing **other players to take it over**. Every placed structure **decays over time without a nearby active tribe claim totem**. Tribes can claim their own constructed structures but **never server-generated structures**. Raiding is legal **at any time**, with **no special siege equipment required**. All in-world storage is accessible to anyone able to reach it.

### 6.1 Building materials and objects

- **Initial progression:** **wood → stone → iron** for structural tiers, with further tiers added only as materials/content expand. Exact HP, harvest requirements, upgrade prices and damage resistances remain Open.
- **Confirmed desired objects:** Walls, floors/foundations, doors, roofs, storage chests, farms/planters, beds, crafting/workbenches, traps, furnaces/smelters and functional structures as useful.
- **Booga Booga-style usability:** Select a structure from simple craft/build palette, see placement preview, rotate/position quickly and place using owned materials (preview/snap requirements Proposed, but accessible building Confirmed).
- **Beds:** Can be furniture/utility structures, **not same-world respawn points**. No respawn in the same public instance after death (§5).
- **Storage:** Anyone in the public world can **open/access storage** once they can physically reach it. Walls and doors can still block movement but are raid-able. **No owner-only secure chest** in the island; only the out-of-world vault is safe.
- **Farming:** Players can plant and grow crops/trees and harvest products. Farming continues **while owner is away** if the **public server remains populated and running**, subject to server-side growth timestamps. After world empties, farms reset with all other world content.
- **Open:** Which seeds, tree crops and growth times are included, whether harvested crops can be replanted endlessly, farm area limits and effects of other players harvesting owner-grown plants.

### 6.2 Tribe claim totems and structure decay

- **Confirmed:** A tribe claim totem protects nearby **player-built** structures from the normal **unclaimed decay** mechanic. All structures **without a totem close enough decay over time**, even if their owner remains in-server.
- **Proposed:** Totem has a clearly visible influence radius; nearby valid tribe-built pieces are registered to the totem's claim set. This is **decay protection and recognized ownership, not anti-raid immunity and not private chest permissions**.
- **Proposed:** Destroying/removing the totem exposes the now-unclaimed pieces to the normal decay clock. Exact grace period, durability and repair/healing of structures remain Open.
- **Confirmed house takeover design:** After owners leave, structures **remain standing**, items in reachable storage remain accessible and an opposing group can **occupy and reuse** the abandoned fortification. Whether an attacker may place a new totem to claim a captured base, and ownership-transfer rules, are **Open** and need a takeover design.
- **Confirmed:** Generated event/ruin/outpost structures are **never tribe-claimable**, even when raided. Their scripted state remains owned by the world event system.
- **Open:** Maximum totems per tribe, overlapping claim resolution, claim radius, decay speed, anti-spam safeguards, placement of totems inside contested POIs, tribe departure/dissolution behavior.

### 6.3 Always-on raiding, no special tools

- **Confirmed:** Any active opponent may raid **at any time**; there is no nighttime/offline raid protection or raid schedule.
- **Confirmed:** **No special raid tools required.** Basic legitimate weapons/tools can damage a structure, with rates controlled by structure material and weapon damage.
- **Proposed optional future:** Siege tools or explosives may accelerate raids, but cannot become a **mandatory prerequisite** for breaking wooden, stone or iron structures.
- Raidables include player structures **and** special naturally generated abandoned/defended/ruined outposts (§7), but cannot claim generated structures as their own.
- Base building cannot block fixed extraction 50-meter no-build zones; rare anywhere portable rune interactions remain separately Open.
- Structures and farms persist as long as their public server runs; **all disappear when server becomes empty**. No persistent cross-server bases.
- **Open:** Damage values, totem protection radius/health, offline-building grief mitigation, claim-transfer UI and tribe alliance raiding permissions.



## 7. Weighted world-event system and public announcements

> **Confirmed:** The event director operates through **weighted rarity selection on recurring server ticks**. At each event check, an event **may or may not occur** based on its weight and eligibility. This includes all **non-Guardian events**, meaning world events *other than the main central Guardian*: rare shrubs, trees, deposits, special mobs, event bosses, meteors, supply caches and generated raidable structures. **All events are announced publicly.** Rare resource sites spawn at **random valid positions inside their relevant biome**.

### 7.1 Event generation and broadcast sequence

1. When the public island is active, a **server-authoritative event scheduler tick** evaluates whether the server should spawn a new event and which type. **Weights** define relative rarity, possibly including a "no event" result.
2. Filter events by valid biome, existing encounter limits and event category availability, then pick using server RNG and versioned probability tables.
3. Spawn event at a **random feasible location within the appropriate biome**, checking terrain, other structures, accessible pathing and protected interaction points.
4. **Publicly announce every event** to the server with audiovisual notification. **Open:** whether all have exact map icons/beacons or some only offer a public biome hint; *announcement itself is confirmed* for all.
5. Players may compete for event loot, even when the encounter has hostile mobs. Reward items are ordinary at-risk physical loot until extraction and can be stolen.
6. Once resolved, expire the event and restore capacity for future weighted checks. Do not have players directly request weighted rolls.

**Design flexibility:** Tick interval, event-type weights, cooldowns, concurrency and "nothing happens" probability are **Open**; they are not fixed every X minutes. **The existing Guardian concept's approximately 15–20-minute cadence and 3-minute warning are preserved as a distinct established rule** until a later decision explicitly changes it (§8).

### 7.2 Event catalog and three boss sources

| Family | Trigger | Spawn style | Player interest |
| --- | --- | --- | --- |
| Rare shrubs/herbs/trees | Weighted event tick | Random suitable spot within its biome | Farming, healing supplies, prized wood |
| Rare stone/ore/minerals | Weighted event tick | Random biome-valid node | Mining, iron and advanced recipes |
| Rare hostile mobs | Weighted event tick | Randomized biome encounter | Ancient, mythological and creature reagent hunting |
| **World-event boss** | Weighted rare boss event | Random eligible region/arena | Contested rare gear or ritual materials |
| **Ritual boss** | **Player places/consumes designated ritual materials** | Valid ritual location/arena | Player-planned summoning at risk of third-party interference |
| **Structure boss** | Player enters/engages eligible generated structure | Event outpost, ruin, dungeon or defended camp | Combat and raiding interlock |
| Meteor/resource crash | Weighted event tick | Random permitted impact area | Scarce minerals, prolonged contested harvesting |
| Ancient Supply Cache | Weighted event tick | Contested marked drop site | High-tier ordinary equipment and resource loot |
| Raidable generated structures | Weighted event tick | Abandoned fort, hostile NPC outpost or ruin | All three environmental structure varieties are confirmed |

**Ritual summoning is a material-based world interaction, not the player casting a magic combat spell.** It does not violate the launch no-magic rule.

### 7.3 Enemy faction palette — Confirmed

Creature/NPC sets can feature **primitive animals, ancient creatures, skeletons, elemental monsters, evil hostile NPCs, and mythological beings**. Elemental *enemies* do not imply player spellcasting. Individual enemy species, weapons, loot distribution, animation and artificial intelligence are content proposals.

### 7.4 Existing event mechanics retained

- **Resource Crash / Abyssal Meteor:** Event resource that requires a special, lengthy contestable harvesting/mining interaction rather than ordinary instant mining; potential Tier-5 reinforcement components.
- **Ancient Supply Cache:** Requires **60 continuous seconds** of valid interaction to unlock. A disrupted channel restarts as already established. Can provide strong equipment and **optional** siege equipment; siege gear is **never mandatory** to raid ordinary player bases.
- **Alpha Mob:** Rare elite creature (e.g., Shadow Panther or Crystal Golem concept) with protective enemies; physical ingredient/reward examples are proposed.
- **Generated raidable structure:** May be abandoned and lootable, defended by enemy NPCs, or a ruin. All are **not claimable by player tribes**. Appropriate for world events, not persistent tribe structures.

### 7.5 Server implementation and remaining questions

- Seed random spawn positions by authorized server decision; use biome/terrain checks and avoid inaccessibly clipped shrines/trees.
- Cap concurrent events, spawned NPCs, generated structures and rare-node density for a 30-player target (tune through performance tests).
- Event weights and rewards should be visible in balance configuration, with analytics tracking actual spawn frequency and **successful extractions** of their loot.
- Public announcement must reach clients with UI/sound accessibility support; alert destination accuracy and radius are **Open**, but no secret unannounced rare event should contradict this design.
- A full 30-player server and a low-population server may require different cooldown/budget controls, but reward rates and spawn rarity must stay fair.
- **Open:** Tick interval, chance of no event, weight tables, overlap limits, per-biome valid spawn positions, discovery of ritual recipes, summoned boss cancellation, NPC/ruin despawn, whether raid damage persists until world empties, and special event-level loot rights.


## 8. Guardian mega-boss and scalable encounters

> **Confirmed retained Guardian concept:** Center-caldera boss appears approximately **every 15–20 minutes** with **3-minute Horn of War** advance announcement, a pillar-based first stage and an unusually valuable **Legendary item dropped at 25% health**, *before death*. Its timed cadence remains the existing special case; weighted event spawning governs other event types unless the owner explicitly changes the Guardian schedule.

### 8.1 Guardian encounter and phase rules

| Phase | Trigger | Mechanic | Public-world tension |
| --- | --- | --- | --- |
| I — Shield pillars | Guardian appears | Invulnerable **NPC boss** until external energy pillars are destroyed | Attack pillars while vulnerable to hostile players |
| II — Gauntlet | Pillars broken | Boss melee, slow projectile/AoE and timed attacks | Teams fight while rivals contest them |
| III — Betrayal | At **25% HP** | Mid-fight **physical Legendary item** is released | Looting, ambushing, escorting and extraction before boss death |

**Guardian energy-pillar shielding is a boss-only invulnerability phase, not equippable player shields**. The Guardian is fully contested by players at all stages; it is not an isolated private PvE room.

### 8.2 Boss spawning categories and reset

- **World-event bosses:** Scheduled/weighted world event creates one encounter. Reset rules depend on that event's individual spawn/despawn definition.
- **Ritual-summoned bosses:** A player initiates via designated rare ritual materials. Players may still fight over this encounter and its loot. Reset/cancellation depends on validity of ritual site, available server state and encounter type.
- **Structure-only bosses:** Bosses exist or activate at designated generated structures; their reset may depend on structure state or next event refresh.
- **Guardian:** Keeps its previously confirmed approximate 15–20 minute cadence for now. Exact timer anchor (start vs defeat), leashing, per-world active cap and post-defeat cooldown are Open.
- **Confirmed scaling direction:** Scale a boss according to **average player level or average gear level** of the active server/lobby/world population. Exact choice, sampling window, formula, min/max and fairness safeguards remain **Open**. Since the user describes average *lobby level or gear level*, document it as candidate measurement of eligible active population rather than assuming the protected hub's unrelated population.
- **PvP and loot:** The whole game is PvP-first. **No automatic boss rewards** should make secured loot immune to rival players. Physical reward objects stay contested/unsecured until successful extraction; whether some participants receive XP or recipe discovery progress is Open.
- **Anti-exploit:** Scaling must not respond instantly to players dropping their high-tier gear, artificially changing server membership or cycling in a low-level alternate account.

### 8.3 Future boss design questions — Open

Exact boss health/stat formulas, average **account level vs equipped gear score vs blended score**, timing of stat capture, downed tribe revive access inside boss arena, mechanics per boss family, guardians' timer semantics, damage contribution accounting and loot roll tables. None alter the specified 60-second tribe downed window or 25%-HP Guardian Legendary release.


## 9. Extraction and permanent vault

### 9.1 Extraction mechanics — Confirmed

- **Fixed sites:** Known POIs can have a portal, but which candidate POIs contain **available** portals differs by public server. Their positions are fixed, not freely rotated after map creation.
- **Start:** Clicking an available portal begins **one server-shared 120-second countdown for that portal event**, not a per-client timer.
- **Telegraph:** Audible and visual extraction alerts are perceptible within a **large radius** so attackers may challenge departing players. Exact radius and VFX are still Open.
- **Move freely:** Players **do not** need to stay inside the capture area while the timer runs. They may hide, travel nearby, fight and heal. **Taking damage does not reset or pause the event timer**.
- **Deadline:** At the exact expiry, every **living, eligible participant physically inside the relatively small capture area** is eligible for the protected extraction animation; anyone outside misses the extraction. This applies to groups and tribes on the same server event. Whether non-group strangers can join the same extraction is Open; public participation is the working default.
- **Safety boundary:** The instant a qualified player's **server-authorized extraction animation starts**, they are invulnerable and safe to disconnect. Prior death/quit leaves the normal 10-minute loot body.
- **Rare portable rune:** An extremely rare reward/drop enables a player to **choose an extraction location anywhere** and starts a **30-second countdown**. Portable-rune consumption, participant capacity, zone radius, announcements and anti-placement exploits are Open. Do not weaken the confirmed wherever/30-second feature without design approval.
- **Destination:** Successfully extracted players transfer to the separate secure **lobby**, not the play-world loading menu.
- **Stakes:** Active fixed portals retain the 50-meter no-build rule. A portable rune is a separate dynamic object whose exclusion/placement details are Open.
- **Payout:** Main Center Crater portal has greater value incentive than lesser fixed portals, but the precise meaning of that multiplier has not been chosen (§9.3).
- **Loot:** Safely extracted materials feed crafting; extraction does not automatically mint Permanent item ownership or extra Legendary copies.

### 9.2 Server-shared timer and qualifying snapshot — Confirmed / Proposed engineering

1. Server validates an activation and reserves **one** event at the available site, with its own start/end timestamps. For a regular fixed exit, expiry is **120 seconds** later; for a rare portable rune it is **30 seconds** later.
2. The server emits the audible and visible alert. The clock continues independently of player proximity, combat, deaths or healing.
3. Players may leave the capture area and return as often as desired. No continuous stay counter exists. An alive character may also arrive late and qualify if physically inside at the exact finish.
4. At expiry, server captures the set of eligible **alive characters inside the defined zone** and grants protected animation to each, including multiple group/tribe members using the same timer. No late entry after the snapshot.
5. Each eligible player gets an individual locked inventory and extraction receipt; the portal event has one shared unique ID. No player can claim someone else's items, join twice or receive two extracts from the same event.
6. At the animation transition, the player's invulnerability and safe-disconnect guarantees take effect; individual loot snapshots settle idempotently to secure vault.
7. Successful players go to lobby after persistence confirms. Unqualified players remain vulnerable and gain no automatic protection; the shared event ends.

**Open behavior:** Whether anyone may start another countdown on the same site immediately, whether the activator's death cancels the event (working default: **no**), whether enemies can intentionally use an opponent-triggered extraction (working default: **yes**), the minimum participant distance, visual radius and portable-rune interactions. All are design choices; the freedom to leave the area and fight/heal is already Confirmed.

### 9.3 Value multiplier guardrail — Proposed

Multipliers should apply to **valuation/payout**, not produce copies of unique loot or quest-critical crafting materials. Define a stable base value and a bonus per portal type, then tune with data. Rare items should remain rare after extraction.

### 9.4 Vault/transaction guardrail — Proposed

Treat extraction hold, protected animation, death, ordinary leave, maintenance kick and item pickup as competing **server-authoritative** transitions. Lock exact item IDs at animation start and create a recoverable receipt before allowing safe disconnect. The server decides the protected animation state; a client-side animation alone is not proof of successful extraction.

### 9.5 Remaining extraction questions — Open

**Confirmed:** 120-second shared timer per fixed exit, free movement/combat/healing during countdown, living-in-zone check **only at expiry**, large-radius cues, multi-player/group eligibility, 30-second portable anywhere rune, animation-start protection and lobby return. **Open:** Actual capture radius, notification radius, public stranger eligibility, activator-death behavior, site reuse and cooldown, portal population per server, portable rune consumption and temporary boundary, party admission, value/multiplier formula, full vs partial carried-inventory banking, portal existence during Guardian encounter, and crash-recovery implementation.

## 10. Economy, stakes and balancing

### 10.1 Three economic locations

| Location | Risk profile | Meaning |
| --- | --- | --- |
| **Active-run carried inventory** | Highest until protected extraction | Death/ordinary active departure yields 10-minute lootable body; staging/menu loadout stays safe until successful Play admission |
| **In-world base stash** | Raid risk | Can stage larger expeditions but opponents can breach and steal |
| **Persistent vault** | Secure | Only confirmed safe store for successful extraction |

**Confirmed:** Event materials, crafted weapons, raiding resources, and boss loot form the world economy.  
**Confirmed:** Special crafting, extracted-material sinks and expensive Permanent conversion. **Open:** Trading/market systems, withdrawals, currency, exact sink magnitudes, recipe costs, Permanent ownership restrictions and rarity curves.

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

- **Lobby / vault:** Vault inventory, protected loadout/transit reservation, deployment decisions, run results and risk explanation.
- **Play-world pre-spawn main menu:** Mandatory protected loading/status, Play enablement only after readiness, safe leave/retry and explicit risk transition after successful spawn (§31).
- **In-world HUD:** Health, sprint-only stamina, food, equipment and crafted-arrow count, medical-item **post-heal animation cooldown**, food heal-over-time status, 60-second downed timer/revive interaction for tribe members, inventory burden, compass/map, extraction and announced events.
- **Crafting/building:** Recipe requirements, arrows and medicine crafting, intuitive placeable preview, structure health, **totem claim radius** and **unclaimed decay**. Weapons/armor have no durability wear.
- **Event UI:** Clear announcement, direction/search radius, beacon color and event time state.
- **Boss UI:** Three-phase status, 3-minute warning, pillar progress and readable 25% phase transition.
- **Extraction UI:** Site name, projected bonus, shared fixed-portal 120-second countdown (or rare portable 30 seconds), audiovisual alert and small must-be-here-at-zero area; explicit animation-start protection and verified receipt.
- **Death UI:** Clear loss summary plus next-run action.

Make major cues redundant across color, icon, words and sound. Provide comfortable interactions on Roblox mobile, desktop and controller; avoid interactions that require precise cursor control.

## 12. Technical direction (architecture proposal, not implementation)

This section records intent so later Luau/Rojo architecture serves the game rules; there is **no game code in the repository yet**.

### 12.1 Authority boundaries

- **Client:** Input, animations, protected pre-spawn menu, local UI, prediction and non-authoritative effects. Client never decides risk activation, successful character admission, extracted/bound ownership or crafting success.
- **Server:** Player-session readiness, safe random spawn, PvP POI exemptions, attacks and slow bow shots, instant-medical/heal-animation lock, food HoT/damage interruption, tribe downed/revive authority, inventory and corpse ownership, totem/decay/raid/building, weighted announced events and biome spawns, scalable bosses, extraction and vault writes. Place ID or client loading-complete flag cannot start risk.
- **Shared definitions:** Typed item catalog, tags, combat/status definitions, event/biome IDs, validated protocol shapes and tunable balance values.

### 12.2 Candidate service boundaries

`SessionService` (deploy/reconnect), `InventoryService` (items, drops, transfer), `VaultService` (persistent stores), `ExtractionService` (portal state and atomic handoff), `ResourceService`, `CraftingService`, `BuildingService`, `CombatService`, `TribeService`, `EventDirector`, `BossService`, and `WorldRulesService`.

**Important invariants for code review:**

1. No client-created rare items, client-declared combat hits, or client-asserted successful Play admission without server validation.
2. No player-built structure can exist within an extraction no-build zone.
3. Every unique item, including **tradeable Permanent equipment**, exists at exactly one authoritative location/owner. A deliberate drop/trade transfers the one canonical instance; death retains Permanent items still legitimately owned.
4. Extraction **and Permanent conversion** have explicit persisted success/failure states; retries cannot duplicate items or double-charge ingredients.
5. A valid **120-second shared fixed-site timer** (or 30-second portable one) evaluates the **alive/in-zone roster at deadline**; each eligible character then begins invulnerable, disconnect-safe animation with locked inventory.
6. **Only a confirmed ActiveRun/ExtractionHolding** departure creates a lootable body expiring after 600 seconds; loading/pre-spawn menus and failed teleports never drop gear. Authorized maintenance removal preserves holdings without auto-extraction.
7. In-world menu loading/PlayRequested cannot start active combat until successful server-controlled spawn and inventory risk transition.
8. Boss Legendary release at 25% occurs at most once per encounter.
9. Only `main` may trigger production publishing workflows; development branches never publish.

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
| **A. Safe staging + gather/craft** | In-world main menu and loading gate, then Outer Rim wood/stone/herbs, spear and bandage | No avatar at risk before successful explicit Play; failed teleport/spawn preserves inventory; active player can gather, craft and heal |
| **B. Fight/lose** | Click melee, slow bow projectile, crafted arrows, instant medical + post-heal cooldown, food HoT and tribe downed/revive | Solo death ejects to lobby; tribe downed lasts 60 unpaused seconds; revive pauses count; item loss/corpse only on final death or active exit |
| **C. Extract/secure** | One fixed portal with shared server **120-second clock**, large-radius alert, deadline-only presence check and protected animation | Player may roam/fight/heal until expiry; only living characters in zone at finish extract; no duplicates |
| **C2. Permanent Forge prototype** | One ordinary special recipe and one eligible source-to-Permanent conversion | Ingredients charged once, converted source retired, owned Permanent record survives test death/rejoin, other carried loot still drops |
| **D. Build/raid** | Booga Booga placement, wood/stone/iron, totems, decay, accessible chests/farms and any-time tool raids | Base remains when owners leave; totem prevents decay not raids; generated structures cannot be claimed |
| **E. Contest** | Weighted event tick, public announcements, biome-random resources, ritual/event/structure bosses | Eligible weighted events spawn fairly and announce to all; contested loot needs extraction |
| **F. Center encounter** | Boss prototype with pillars, attack cycle, 25% drop, central portal | Mid-fight Legendary appears once; boss structures cannot cheese; relic must be extracted |

### 13.1 Explicit non-goals for the first slice

Full island art, every biome, elaborate weather, large equipment catalog, trading/auction house, polished monetization, cross-server base persistence, advanced tribe diplomacy, and every elemental school. The minimal Forge conversion proof **is included** in the first playable slice, as a core loop.

### 13.2 Documentation validation checklist

- [x] Flintborn launch excludes firearms, player shields **and player magic**; finite medical items heal instantly, food heals over time; stamina only limits sprint.
- [x] 8-player tribes with timed downed/revival; no same-world respawn; PvP default with explicitly marked POI exceptions.
- [x] Booga Booga builds, wood/stone/iron, totem-dependent decay, public storage, farming and all-hours raiding.
- [x] Weighted publicly announced non-Guardian events, three boss source types and biome-random rare resources.
- [x] **Play-world pre-spawn main menu** required; failed teleport, loading, kick or spawn before Play admission is loss-free.
- [x] Full run loop, three world zones and vault/death stakes documented.
- [x] Three event families and exact known 60-second cache rule recorded.
- [x] Mega-Boss cadence, 3-minute alert, three phases and 25% drop recorded.
- [x] All portals covered by the 50-meter no-build rule.
- [x] Proposed mechanics explicitly differentiated from confirmed design.
- [x] Extracted-material special crafting and costly Permanent conversion documented as Confirmed concepts.
- [ ] Permanent death rules, recipes, costs and caps approved and validated in gameplay.
- [ ] Prototype tests and runtime/CI validation — **not applicable yet; no game source exists**.
- [ ] Design-owner decisions for outstanding systems — **pending**.

## 14. Decision backlog (priority order)

| Priority | Decision | Why it matters |
| --- | --- | --- |
| **P0** | Run/session model, protected loadout reservation, active admission risk threshold, Permanent death ownership, base lifecycle | Inventory authority, teleport safety and player stakes |
| **P0** | Permanent conversion eligibility, irreversible ingredient usage, binding/slot/recovery | Avoid trivial risk bypass and item-duplication pathways |
| **P0** | Protected pre-spawn world main menu, explicit Play readiness/spawn risk boundary, loss-free teleport errors and active-only body/drop rules | Avoid gear loss from failed loading and prevent combat-logging exploits |
| **P0** | Authenticated maintenance safe-kick inventory recovery and two-minute contested extraction handoff into disconnect-safe animation | Preserve loot across planned updates and protect extraction without duplication |
| **P0** | Portal activation/interrupt logic and multiplier definition | Core extraction risk and economy correctness |
| **P0** | Server population, solo/tribe sizes, and PvP rules | Map size, reward access, balance and performance |
| **P1** | Click melee, slow bow projectiles and crafted arrows, sprint-only stamina, crouch, instant medical cooldown, partial food HoT interruption | Launch PvP readability and mobile input; **no player magic, dodge-roll or gear wear in MVP** |
| **P1** | Totem radius/decay, accessible storage, wood/stone/iron construction, all-time tool raiding and takeover permissions | Claimed buildings avoid decay without becoming raid-immune; all owners absent does not delete structure in populated instance |
| **P1** | Weighted event tick/rarity, public announcements, biome-random spawns, ritual/event/structure boss resets and level/gear scaling | Event variety, server fairness, contestable loot, scalable performance |
| **P1** | Biomes, distances, terrain elevation, portals and spawn points | World prototyping and movement |
| **P1** | Special Forge levels/discoveries, rare material sources, medical/food/arrow crafting and post-death Permanent upkeep if adopted | Cross-run progression with **indefinite ordinary equipment lifespan** |
| **P2** | Currency, optional trading and cosmetic mastery | Long-term economic depth |
| **P2** | UI art direction, onboarding and optional cosmetics | Presentation and retention |

## 15. Cross-run special crafting and the Permanent item class

> **Confirmed:** The player can spend successfully extracted materials to craft special items. Some eligible items brought back alive can be converted to a **Permanent** type by spending scarce, expensive ingredients. This is a central cross-run progression pillar.
>
> **Confirmed:** Permanent equipment persists through death, but can be intentionally dropped, picked up and stolen, or traded. Binding does not raise its combat stats; only designated source items are convertible. Post-death maintenance costs, gear limits and unclaimed dropped-item fate remain **Open**.

### 15.1 The three interlocking loops

1. **Moment-to-moment:** Gather wood/stone/iron, herbs, planted food and animal materials; fight with **simple melee and slow craft-arrow bows**, build/raid shelters, heal using medicine/food and contest unsecured loot. No player magic at launch.
2. **Expedition:** Decide between pursuing a richer portal or safely carrying the prize to a minor rune. Dying before a completed extraction drops carried ordinary loot.
3. **Between expeditions:** Deposit extracted materials, select secure Forge recipes, create special ordinary equipment and slowly earn the ingredients to convert a prized eligible item into a Permanent one.

Extraction is **not** conversion: securing a legendary boss drop only places an ordinary, high-value item in the vault. Converting it requires a separate recipe, material sacrifice and server-side commit. A player can prefer immediately redeploying the risky Legendary instead of waiting to convert it.

### 15.2 Item taxonomy and risk

| Class | Ownership and source | In-run risk | Fate at death | Secure-hub behavior |
| --- | --- | --- | --- | --- |
| Unsecured materials | Fresh gathering, events, dead players or raided base | Carried or base-stashed | Drops / remains lootable | No access until extraction |
| Ordinary vaulted stacks | Extracted wood, ore, jade, cores, etc. | Becomes unsecured if withdrawn | Dropped if carried | Protected and usable by Forge |
| Ordinary vaulted gear | Extracted or special-crafted gear | Becomes unsecured if withdrawn | Dropped if carried | Can be stored or consumed as source |
| Special ordinary gear | Secure Forge recipe using vault inputs | Droppable on deployment | Drops if carried | Safe only while stored in vault |
| Permanent converted item | Designated vaulted source + costly recipe | Owner retains through death; may voluntarily drop/trade | Retained by owner if held; may be stolen through deliberate drop | Single secure canonical record, transferable |
| Recipe knowledge | Earned milestones / discoveries | No physical item | Persists (**Proposed**) | Unlocks future recipes |

**Vocabulary requirement:** "Secured" or "Vaulted" means safely stored outside a run. "Permanent" describes a specific conversion class. An item is not Permanent just because it is in persistent storage.

### 15.3 Eligibility and source consumption — Confirmed constraints / Proposed catalog

- **Confirmed:** Only designated extracted gear may be Permanent-converted. The source is a unique, server-validated vaulted instance, not an arbitrary inventory stack.
- Eligible item families initially include weapons, select armor and a restricted set of tools. Exclude raw materials, currency, siege charges, structures, ammunition, potions, vault keys and anything creating limitless economic output.
- The specific source must be owned and vaulted, eligible under the designer catalog, unlocked through applicable **level/discovery requirements**, not deployed elsewhere and not already Permanent.
- Converting **transforms/consumes** the source instance; it does not create both an ordinary tradeable source and a new Permanent copy.
- Source attributes (quality, rarity roll, source crafting identity) should be preserved where eligible. **No player magical/enchantment combat affixes at launch**; any future special-roll support requires explicit item catalog/versioning.
- No client can submit a chosen output rarity, free ingredient amounts, owner ID or arbitrary "Permanent" flag.
- The confirmed 25%-HP boss Legendary remains ordinary world loot until a player takes it to a rune and extracts. It cannot be made Permanent instantly in the crater.

### 15.4 Confirmed Permanent definition (replaces earlier proposals)

**Permanent gear survives the current owner's death**, retains **exactly the source item's combat stats**, and is **transferable** through deliberate ground dropping (and another player taking it) or voluntary trading. Only approved extracted items are eligible. A Permanent gear instance is not an infinite number of freely spawnable copies and never appears as loot **just because its wearer dies**. The earlier **nontradeable, account-bound manifestation** proposal is superseded by these confirmed decisions. See §17 for the single-instance transferable model. Post-death repair costs and item/slot caps remain Open.

## 16. The Ancestral Forge: crafting outside the run

### 16.1 Two crafting domains

| Characteristic | Island field crafting | Secure Ancestral Forge |
| --- | --- | --- |
| Place | Island workbench/backpack | Protected lobby/hub or dedicated secure menu |
| Inputs | Live at-risk backpack / raidable station stock | Successfully extracted resources and vaulted gear only |
| Outputs | Ordinary durable tools/armor, **craftable arrows**, food, instant medicine, structures | **Nonmagical** special gear, rare medicine/materials and Permanent conversion |
| Conflict | Vulnerable to PvP, raids, weather and events | Not raid-able, but all writes server-authoritative |
| Persistence | Crafted item must still be extracted | Committed output stays in vault/armory until deployed |
| Main purpose | Survive next minutes | Grow player account over many expeditions |

The hub location and station names are **Proposed**, not mandated. A single Roblox place with distinct panels is acceptable if it reduces loading and engineering scope.

### 16.2 Proposed stations and recipe categories

- **Stonecarver's Table:** Refined flint, bone, resin and early special tools; introductory secure-crafting tutorial.
- **Tribal Smithy:** Iron processing, weapons, wearable armor, arrows and **structure** components (no player shields or equipment durability repairs).
- **Medical / Rarework Table:** Harvested herbs, food supplies, medicinal recipes and rare nonmagical source components; **no player enchantment or spell system at launch**.
- **Eternal Anvil:** Permanent transformations requiring a validated source instance, scarce Keystone and multiple rare materials.
- **Vault Ledger:** Material balance, pinned blueprints, provenance, missing-ingredient list, operation history and safe-ownership receipts.

### 16.3 Exact crafting UX contract

1. Successful extraction produces an authoritative **vault receipt** (items + amounts + extracted portal and payout).
2. Show the player which recipes gained progress from that haul. Merely landing near a rune or dying in its channel cannot count.
3. Player chooses a special recipe, source weapon if relevant, and confirms material requirements displayed as **Owned / Needed**.
4. Server checks recipe unlock, source instance, remaining stacks, vault capacity, session ownership, selected affixes and balance version.
5. For irreversible conversion, explicit confirmation names the exact sacrificed weapon and its permanent bound restrictions.
6. Forge operation is reserved under a unique ID. Both target gear and consumed ingredient stacks must be unavailable to simultaneous requests.
7. On successful durable commit, source and costs disappear **exactly once**, and resulting output is created **exactly once**.
8. UI presents a verified receipt, not an optimistic client-granted item. Failed or pending operations reconcile before retrying.
9. Ordinary special crafts go to the vault; Permanent conversion goes to the separate armory. Both are tracked in the player's persistent profile.

### 16.4 Crafting principles — Proposed

- No random recipe-failure chance that destroys expensive ingredients and a Legendary. **Default: 100% conversion if valid and fully funded**.
- Recipes should encourage players to seek *different* objectives (ore + alpha component + meteor resource), not repeatedly grind a single trivial node.
- Special recipes use scarce extracted components to make **ordinary nonmagical** weapons, crafted-arrow supplies, instant medical items, food or Permanent versions of **designated** equipment. Magical enchantment concepts are postponed.
- Recipe discovery is achievement-based or material-discovery-based, with clear reveal paths. Avoid forcing players to consult external guides.
- Multiple viable weapon archetypes prevent a single mandatory optimal Permanent item.
- Crafts that consume an item must use a unique instance ID; stacks use bounded positive integers and no fractional duplication.
- Recipe versions are immutable for active transactions so a live balance patch cannot alter an operation halfway through.

## 17. Permanent gear: death protection and ownership transfer

> **Confirmed:** Certain **designated** extracted item types may be made Permanent using costly materials from **multiple** sources and recipes gated by player leveling and discoveries. Permanent conversion **does not modify combat stats** relative to the selected source gear. A Permanent item **survives its owner's death**, but if the owner **deliberately drops it** and another player collects it, it changes owner. Permanent items can also be **traded**. Neither dropping nor trading creates a duplicate.
>
> **Open:** Possible post-death material costs/repairs, simultaneous Permanent gear limit, trade venue/fees, exact eligible list, what happens to an unclaimed dropped Permanent item if it expires or the world resets, and whether items can be sold through a marketplace.

### 17.1 Single persistent but transferable item instance

- A Permanent weapon/armor piece has **one unique canonical instance ID**, original stats, owner/location and provenance. It can exist in account-safe armory/vault, equipped in active world, dropped on the ground, or escrowed for an agreed trade — never multiple at once.
- **Death / ordinary active departure:** The owner retains the Permanent gear instance; the server returns it to their secure armory or a proposed recovery-pending state. All ordinary unsecured gear follows the corpse-drop rules.
- **Intentional drop:** The item leaves the owner's possession and becomes a physical pickup. If another player validly picks it up, **the ownership is transferred** and the original owner cannot retrieve it through death protection or a duplicate armory record.
- **Trading:** A direct exchange is permitted in principle. Trade transfers both sides' item IDs atomically/idempotently through server validation; no client-side grant or forged accept.
- **No death-based trade exploit:** A thief cannot take a Permanent item solely by killing its wearer. They must obtain it through its legitimate **manual drop / pickup**, explicit trade, or a separately approved mechanic.
- **Normal stats:** No automatic rarity/damage/speed bonus for becoming Permanent. The privilege is death-retention and long-term ownership only.
- **World reset:** Owned Permanent items survive. **Unclaimed manually dropped Permanent gear** needs a specific expiry/reset policy; no assumption that ground items auto-return was approved.
- **Maintenance and teleport:** Protected staging, update kick and extraction animation preserve whatever canonical Permanent items the player still legitimately owns, respecting prior transfers.

### 17.2 Ownership state safety — Proposed

| Operation | Validation | Expected single result |
| --- | --- | --- |
| Convert designated saved gear | Owner, source instance, recipe unlock by discovery/level, rare inputs | Source transformed once into exactly one Permanent item |
| Die wearing Permanent gear | Run death and prior item owner | Ordinary loot drops; single Permanent instance safely retained |
| Manually drop Permanent gear | Owner, equip state, permitted proximity, authoritative input | One active pickup item; it is no longer simultaneously in armory |
| Another player picks up drop | Drop exists, player can reach it, not previously claimed | One canonical ownership transfer |
| Trade Permanent gear | Players and gear valid, both confirm, trade escrow exists | Single atomic transfer; no dupe from cancel/disconnect |
| Owner reconnects after theft | Authoritative latest owner record and claim history | Former owner cannot reclaim stolen gear |
| World empties | Last-player exit and active world cleanup | Persistent owned items survive; unresolved ground-item loss rule flagged |
| Repair/rearm | Cost/rules not yet approved | No invented mandatory cooldown or irreversible gear wipe |

**Design challenge:** Transferable death-protected items are unusually sensitive to **drop/loot ordering** and cross-server ownership. Server IDs and write-ahead receipts must prevent a voluntary drop followed by a disconnect from giving the original owner a restored copy. Logs must identify which user owns the one real item after every valid pickup or trade.

### 17.3 Balance remaining undecided

1. **Post-death cost:** Material repair/recovery may restrain indefinite reuse. Its existence and price are not final.
2. **Slot cap:** The number of simultaneously equipped Permanent weapons, armor or tools remains genuinely undecided; do not hardcode one item as Confirmed.
3. **Eligibility catalog:** Only designer-flagged items may be converted; categories/rarities are to be chosen.
4. **Affixes:** Binding adds no stats, but whether a source's existing roll/affixes are preserved or re-rolled needs explicit agreement.
5. **Trade paths:** Safe lobby exchange, ground-drop transfer and possible market are distinct UX/safety mechanics. Ground dropping and trading are Confirmed; trade channel/currency remain Open.

## 18. Resource tiers, economy and acquisition sources

### 18.1 Proposed material families

| Acquisition | Region/event | Examples (working names) | Special craft function |
| --- | --- | --- | --- |
| Common harvest | Across valid biomes | Wood, Stone, Plant Fiber, Rawhide, common food | Starter recipes, medical supplies, crafted arrows and field equipment |
| Uncommon harvest | Outer caves/Inner trails | Flint, Bone, Resin, Copper Ore | Beginner Forge, bow/spear component upgrades |
| Rare harvest | Inner jungle/volcanic slope | Iron Bloom, Obsidian, Jade, Dire Hide, rare herbs | Metal weapons, healing mixtures, resistances and special armor |
| Elite creatures | Alpha Mob + protective pack | Charged Core, Glow-Fur, Ancient Binding | Elemental upgrades and conversion gates |
| Ancient caches | Timed 60-second unlocking | Finished weapons, Ashen Oil, Siege Resin | Prepared gear, raids, rare catalytic components |
| Tier-5 Resource Crash | Prolonged contested meteor interaction | Abyssal Shard, Emberglass | Endgame reinforcement and multiple conversion inputs |
| Mega-Boss / Guardian | Crater's three-stage challenge | Guardian Heart, Crown Ash, one mid-fight Legendary | Extreme-tier conversion and prestige rewards |

**Known facts:** Jade and Obsidian come from the Inner Ring; alpha drops support modifiers; meteor supplies rare reinforcement; cache unlock is 60 continuous seconds; the Legendary appears mid-boss-fight at 25%. The specific additional names, quantities, sources and probabilities above are **Proposed**.

### 18.2 Scarcity design — Proposed

- Base recipe costing on **materials successfully extracted per player-hour**, not simply how often a mob is killed.
- Multiple extraction successes should be needed for a meaningful conversion; a single lucky Tier-5 harvest should not mint several Permanent weapons.
- Ingredients compete between wood/stone/iron building, consumable arrows, medical/food supplies, ordinary special equipment and high-cost Permanent conversion.
- Favor several different event sources for advanced recipes so an elite group cannot monopolize one boss and control every equipment path.
- Maintain a viable solo/midgame route to an early Permanent item, even if rarest Guardian conversion takes coordinated PvPvE activity.
- Vault contents are never raid-able; run bases and carried resources are, giving extraction its reason to exist.
- Portal multiplier should affect valuation/payout, **not duplicate unique gear, crafting inputs, Keystone, or Guardian drops** (Proposed).
- No pay-to-win Permanent catalysts or Robux-bought combat power.

### 18.3 Material sink model — Proposed

Resources exit the economy through (a) field supply/ammunition/raids, (b) secure special crafting, (c) consumed source equipment, (d) Permanent conversion, and (e) repairs/recovery. Track acquisition and sinks separately by material source; adjust source drop rates only after observing actual extracts, loss, and monopolization. Never apply arbitrary hidden wipes to the protected Permanent armory.

## 19. Nonmagical special crafting and Permanent conversion examples

All examples in this section are **Proposed balance data**, not finalized recipes, quantities, loot guarantees or launch catalog entries. **No launch recipe may grant player magic, enchantment attacks, infinite healing or shield equipment.** The Ancestral Forge uses materials **successfully extracted into the protected vault**, not gear sitting in raidable field storage. Player recipe discoveries and levels can gate each recipe.

### 19.1 Ordinary special recipes — nonmagical launch direction

| Sample output | Input sources / items (provisional) | Station | Core use |
| --- | --- | --- | --- |
| **Flint Hunter Spear** | Extracted flint, bone, fiber | Stonecarver | Reach-oriented ordinary melee weapon |
| **Ironroot War Axe** | Iron ore, hide, hard resin | Smithy | High-cost heavy axe; slower normal attack |
| **Reinforced Bow** | Rare tough wood, fiber, horn | Bowyer/Smithy | Improved bow with **slow physical arrows**, no special energy shots |
| **Iron Arrows** | Extracted iron/wood/fiber | Bowyer/Smithy | Finite craftable arrow stack, ordinary projectile |
| **Hunter's Field Kit** | Herb bundles, hide, cloth | Medical table | Several **single-use** medical items; each applies immediate healing |
| **Restorative Tonic** | Herbs, purified ingredients, rare creature gland | Medical table | Immediate medical heal followed by visible animation cooldown |
| **Long-Keeping Rations** | Farm-grown crops, preserved herbs | Cookfire/medical table | Food supply; gives **healing over time** |
| **Stonework Reinforcement Pack** | Stone, iron fittings, resin | Smithy | Build/repair supplies; not a player shield |
| **Tribe Claim Totem** | Wood, stone, crafted symbol | Field workbench | Claims nearby player-built structures for **decay protection only** |
| **Rare Harvesting Pick** | Iron, rare ore and beast parts | Smithy | Nonmagical resource harvesting; indefinite item lifespan |

Exact counts, material names, unlock conditions, output stats and station placement are **Open**. The item names above are illustrative. Rare plants, meteors, creatures, rituals and raidable structure events feed different recipes without requiring playable spellcasting.

### 19.2 Costly Permanent conversions — illustrative

| Permanent conversion | Eligible securely extracted source | Additional scarce resources (example families) | Confirmed limitations |
| --- | --- | --- | --- |
| **Permanent Flint Hunter Spear** | Designer-designated Flint Hunter Spear | Rare flora component + meteor stone + boss/elite reagent | **Same source stats**, retains owner on death, manually droppable/tradeable |
| **Permanent Ironroot Axe** | Designer-designated Ironroot War Axe | High-grade iron + unique resource + multiple event reagents | Same stats; requires costly multi-source extraction |
| **Permanent Reinforced Bow** | Designer-designated Reinforced Bow | Rare tree wood + metal + hostile structure reward | Same bow velocity/damage properties; arrows remain craftable and consumable |
| **Permanent Iron Armor** | Eligible designated iron armor piece | Rare metal + creature hide + boss/ritual material | Armor itself persists, but **no extra magical resistances** |
| **Permanent Guardian Relic Weapon** | Eligible extracted Guardian weapon | Multiple scarce boss/event/resource materials | Not automatically permanent just because it dropped at 25% HP |

**Confirmed:** Only specifically designated source items can be converted, conversion changes **death/ownership behavior but not stats**, Permanent gear may be **dropped, taken and traded**, and ingredient costs should be expensive and require multiple source families.

**Open:** Exact amounts, first accessible conversion tier, post-death material upkeep/rearming (not durability), Permanent simultaneous equipment limits, future weapon eligibility, conversion source-affix preservation and drop/trade escrow UX.

### 19.3 No launch enchantment system

Earlier example recipes such as elemental storm bows, fire-infused spears, frost mantles or defensive wards are **archived concepts for potential future updates**, not requirements for the first playable game. **Elemental/skeleton/mythological enemy types remain permitted.** A ritual used to summon a world boss is a **resource interaction**, not player-cast combat magic.



## 20. Detailed player journeys

### 20.1 New player, safe first extraction

The new player arrives in the play-world **protected main menu** while assets/profile load, then explicitly presses **Play** to spawn at a **random valid map location**, which need not be the Outer Rim. Harvest nearby wood/stone/iron or food ingredients according to biome, craft click-attack melee gear and crafted arrows, and learn basic medical/food healing. Activate an available fixed rune's **shared 120-second countdown**; hide/fight/heal and return to the small zone in time to qualify for invulnerable animation and extract. All event alerts remain public. At the secure hub, receive an unmistakable **Vaulted** receipt and the first special Forge recipe preview. The player cannot convert the spear immediately; they need several further extractions. A failed first run drops carried loot but does not erase earlier vault progress. Goal: teach risk, safety, and long-term crafting in one sequence.

### 20.2 Solo scavenger, long-term progress without boss domination

Explore Inner Ring at quieter times, hunt smaller elites, withdraw only inexpensive vaulted gear, and extract Jade and occasional Charged Cores through variable rune routes. Build an ordinary special spear. Pin its Permanent recipe, deliberately choose a risky meteor run for the missing reagent, and eventually convert one signature weapon. This path must not require joining a dominant tribe. Endgame Guardian permanence can still require tougher objectives.

### 20.3 Rival tribes, betrayal and raid

Two tribes contest the Guardian's energy pillars as the Horn of War countdown ends. At 25% HP, a Legendary drops **before** boss death. A carrier grabs it and emits the high-value glow. A rival team ambushes and takes it. Meanwhile another squad raids the carrier's unguarded FOB and steals stored ordinary resources. Only a successful portal extraction secures loot; neither a base nor a bound weapon makes the Legendary safe. The tribe that escapes can later consider a very expensive Permanent conversion.

### 20.4 Death while wearing Permanent gear

A veteran equips an owned **Permanent sword** alongside ordinary armor, instant-heal potions, crafted arrows and freshly harvested rare ore. Enemies defeat them: if a tribe member, the **60-second downed timer** begins and a teammate may pause it by starting revival; if revival fails, they are ejected to lobby, with their **ordinary** items left in a 10-minute corpse. The Permanent sword remains theirs and keeps the exact same combat stats; any post-death material rearm fee remains Open. If they had **manually dropped** that sword and a rival picked it up first, ownership would instead belong to the rival.

## 21. Launch combat balance and player activity

### 21.1 Combat vocabulary — Confirmed / Proposed stats

- **Click melee:** Simple, readable hit animations using valid equipped spears, swords, clubs or axes; attack speed, recovery and reach are item stats to be balanced. **Melee consumes no stamina.**
- **Bows:** Physical arrow projectiles with **deliberately slower visible travel**, craftable finite arrows and server-authoritative collision. **Shooting consumes no stamina.** Exact speed, gravity and falloff TBD.
- **Sprinting:** Drains stamina until fatigued, then stamina regenerates according to a tuned rule. **Only sprinting uses stamina**.
- **Crouching:** Low profile/stealth/movement choice; does not consume stamina. Sprinting and crouch interactions are implementation choices.
- **Medicine:** Instant HP restoration, then cooldown expressed through the animation duration. Cannot stack instant heals through repeated/parallel RemoteEvents.
- **Food:** Food item heals over time; incoming damage partially interrupts remaining healing, exact amount Open.
- **Armor:** Ordinary physical damage protection; armor items remain usable indefinitely with **no degradation/breaking**. Rare specialized defenses are a *future-update idea*, not a launch mechanic.
- **No player magic/shields:** Skeletons, elementals and other mythical adversaries remain enemy content; magic attacks, magical barriers and dodge/stamina combos are out of launch scope.

### 21.2 Downed and revival tactical balance

- A **solo non-tribe** character reaching lethal HP dies and is ejected to lobby; their body remains on the island 10 minutes.
- A **tribe member** receives a **60-second** downed window. A valid tribe revive interaction **pauses** this timer; cancellation **resumes remaining time**. Death/ejection occurs if unpaused time is exhausted.
- Revive time, restored HP, reviver interruption on incoming damage, execution/finish mechanics and one-member-only eligible tribes need balancing. No revives of already-dead/ejected characters in the same world.
- Tribe cap is **8** and all worlds remain PvP-enabled except explicitly protected POIs. No respawn in the same world, including from beds.
- Social implications: tribe members must eventually extract and return to lobby to regroup with a dead comrade. There is no short death → sprint back → corpse-loot loop in that instance.

### 21.3 Equipment and long-term progression

High-value gear improves outcomes through ordinary damage/range/armor/rarity differences, but **making the item Permanent does not grant extra stats**. Resource harvesting, level-gated/discovered recipes and multi-source special crafting drive progression. Raiding can occur any time with basic damage tools, so no time-based "unraidable" window. Farmers/builders can establish persistent-in-world holdings until the last player leaves; totem-protected structures resist *decay*, not PvP.

### 21.4 Encounters and balance telemetry

Measure melee duel duration, arrow velocity readability, damage accuracy under mobile latency, sprint duration, medicine-use cadence, food HoT completion after repeated attacks, successful revives (incl. paused timers), tribe versus solo survivability, raid time against wood/stone/iron and event reward extraction rates. Bosses scale by an average **player level or gear level** population signal, with anti-exploit normalization yet to be designed. The Guardian's original 15–20-minute timing stays as a separate established concept.



## 22. Detailed inventory, extraction and death state transitions

### 22.1 Canonical item-location state machine — Proposed

| Authoritative state | Legal next state(s) | Notes |
| --- | --- | --- |
| **WorldSpawned** | Carried, despawned | Unique drop instance, distance and pickup validated by server |
| **Carried** | WorldDropped, BaseStored, Consumed, QualifiedAtDeadline | Ordinary gear remains at risk during shared extraction timer; only qualifying alive/in-zone players become protected |
| **BaseStored** | Carried, WorldDropped, Consumed | Raiding, door permissions and destruction rules apply |
| **ExtractionEventActive** | QualifiedAtDeadline, MissedDeadline, Death | Shared event timer is independent of player position/damage until a one-time alive/in-zone check at expiry |
| **QualifiedAtDeadline / ExtractionProtected** | Vaulted (commit), retry pending | Server-authorized animation begins invulnerability and locks the participant's own exact inventory snapshot |
| **Vaulted** | Carried (withdraw), ForgeReserved | A safe storage location, *not* permanent status |
| **ForgeReserved** | Vaulted (cancel/rollback), Consumed / PermanentOwned (commit) | Reservation tied to idempotent operation ID |
| **PermanentOwned** | PermanentEquipped, PermanentVaulted, PermanentWorldDropped, PermanentTradeEscrow, PermanentRecovery | Canonical equipment has one *current owner*; death retains it but deliberate drop/trade can transfer it |
| **PermanentEquipped** | PermanentVaulted, PermanentWorldDropped, PermanentTradeEscrow, PermanentRecovery | One canonical transferable ID, retained on death, manually droppable |
| **Consumed** | Terminal | No replayable recreation without new server reward grant |

**Invariant:** Each gear instance, including transferable Permanent equipment, has exactly **one** authoritative current owner/location and cannot simultaneously be in an armory, active inventory, world drop or trade escrow. Stack totals use bounded integers and server-validated transfers.

### 22.2 Shared extraction event and protected animation — Confirmed / Proposed engineering

1. Server accepts activation at an available known-POI exit and creates **one event timer ending 120 seconds later**, or creates an eligible portable rune's temporary **30-second** event at the selected location.
2. Broadcast a large-radius audiovisual warning. Countdown continues regardless of whether the activator runs away, dies, gets hit or heals. It is a **server timer**, not a channel owned by one player or tribe.
3. At the precise expiry, the server builds the **one-time qualifying set** of alive players actually inside the small exit volume. All eligible members of groups/tribes can use the same event; strangers are Open.
4. Every eligible player transitions into server-authorized protected animation, immediately becomes invulnerable and may safely disconnect, and receives **their own** locked inventory snapshot, operation ID and recoverable vault entitlement.
5. Dead players, characters outside the area and anyone arriving after the snapshot receive no protection or vault receipt. Active death/quit still follows the ordinary body rules.
6. Retry/rejoin/teleport and DataStore failures reconcile each player's snapshot exactly once; never let the event timer generate duplicate items or a group member extract items owned by someone else.
7. Successfully settled players go to the separate lobby. A pending durable write remains protected and marked pending; it cannot be treated as a normal active logout.

**Important:** The previous continuous **stay-in-zone for two minutes** proposal is revoked. There is no area-exit timer reset or interrupt-on-damage mechanic; presence matters **only at the deadline**. Implementation must respect the confirmed portable-rune freedom while evaluating anti-cheat and server placement safeguards separately.

### 22.3 Disconnect, shutdown and concurrent sessions — Confirmed / Proposed engineering

- **Confirmed:** Ordinary voluntary quit or lost connection **after the server has admitted/spawned the player into ActiveRun or ExtractionHolding** creates one lootable character body, forfeiting carried ordinary loot. **Body and unclaimed loot disappear after 10 minutes / 600 seconds.** Pre-spawn menu/loading departure is safe even though it happens inside a play-world place.
- **Confirmed:** Disconnect is safe once the valid protected extraction animation begins, even before it finishes. The player must receive their locked extracted contents once persistence reconciles.
- **Confirmed:** Authorized administrator update/removal commands safely kick players without losing held items. The server must preserve them separately from successful extraction and not grant extraction bonuses/Forge eligibility; see §30.
- **Proposed:** Unexpected entire-server crash cannot keep a corpse in a server that no longer exists. Deliberate admin maintenance and platform failure require different audited state/recovery policies.
- Keep a per-account/profile session lease so two concurrent servers cannot both withdraw, restore or mint the same item.
- Under DataStore throttling, preserve pending operation receipts and retry within budgets; never silently mark a pending write successful or forfeit protected holdings.
- Block stale profile writes during reconnect or fast teleport; do not let an old server overwrite newer inventory, Permanent conversion or maintenance restoration.
- Do not auto-extract everyone when a server restarts. Authorized maintenance preserves unsecured holdings without granting payout. Unexpected failures need a separately defined and tested fairness policy.
- A failed Forge operation must not consume ingredients permanently without an eventual committed output or safe rollback; shutdown must also preserve that consistency.

### 22.4 Base raid and protection boundary

Vault and Permanent armory are outside the island and cannot be directly raided. Players may steal **only items that are actually unsecured and present** in the world (carried gear, raidable containers, physical drops, unlocked cached supplies). Building a base does not grant secure ownership; nothing in a tribe chest gains Permanent status. The 50-meter portal no-build rule remains enforced on the server, including overlapping piece geometry, not just its center point.

## 23. Proposed Roblox Luau services and persistence model

### 23.1 Service contracts

| System | Server responsibility | Client-facing information |
| --- | --- | --- |
| **ProfileService** | Session locks, schema upgrades, revisions, protected extraction and maintenance recovery | Saved/pending/recovery status and safe profile view |
| **ItemCatalog** | Definitions, valid tags and input/output restrictions | Static icons/descriptions/stats for display |
| **InventoryService** | Transfer/drop/pickup, stack accounting, world provenance | Inventory and equip deltas |
| **VaultService** | Safe storage/withdrawal, capacity and extraction receipt application | Vault tabs, item detail, secure totals |
| **ForgeService** | Recipe eligibility, ingredient reservation, output issuance, commit | Preview, costs, progress, authoritative receipts |
| **PermanentEquipmentService** | One canonical owner, death retention, manual drops, theft pickup, trade escrow and optional recovery | Current owner, transfer receipt, tentative repair/slot status |
| **LoadoutService** | Safe cross-place loadout reservation, active-only withdrawal, configurable Permanent slot limits and validation | Safe menu equipment preview and risk labels |
| **ExtractionService** | Server-shared 120s fixed or 30s portable timer; end-of-timer presence snapshot, alerts and protected animation | Shared countdown, deadline zone and verified individual receipt |
| **CombatService** | Validated click melee, slow bow projectiles and arrow spend, sprint-only stamina, medical instant heals/cooldown, food HoT | Health/stamina/food HUD, heal cooldown, validated hits |
| **BuildingService** | Booga Booga construction; wood/stone/iron tier, **tribe totem claim**, unclaimed decay, accessible storage and any-time ordinary-tool raids | Build previews, visible totem coverage, structure HP/decay |
| **EventDirector** | **Weighted ticking**, announced events, random biome-appropriate flora/ores/NPCs, meteor/cache/raid structures | **Every event announced publicly**, with appropriate markers/cues |
| **BossService** | Guardian phases and timed drop; weighted/ritual/structure bosses; average server player-level/gear-score scaling | Announcements, boss phase UI, contested drops |
| **AnalyticsService** | Economy, public-world activities, participation, reward abuse, dupes/failures | Verified activity rewards/diagnostics |
| **DepartureService** | Active-run departure/body + 600-second TTL, safe lobby/pre-spawn menu, protected extraction and maintenance exemption | Risk warnings, safe pre-spawn state, body and recovery status |
| **WorldAdmissionService** | Protected loading/menu, profile/world readiness, safe transit reservation, successful Play/spawn risk activation | Play/loading status, retry/return, clear risk transition |

All persistent crafting and extraction grants happen on the **server**. Client may request an action but cannot dictate rarity, cost, exact output, reward source, success flag, or timestamp.

### 23.2 Versioned profile structure — Proposed

| Field group | Representative fields | Constraints |
| --- | --- | --- |
| Profile envelope | schemaVersion, profileRevision, sessionLease, lastCommittedOperationId | Migration/backward compatibility and stale-write checks |
| Vault stacks | itemCatalogId → safe integer quantity | Nonnegative, bounded, server-calculated |
| Vault instances | instanceId → catalogId, quality, rolls, wear, acquisition ID | Unique IDs and verified provenance |
| Permanent equipment | instanceId, catalogId, **currentOwnerId**, location, affixes, recovery, activeLease, ownershipVersion | Death-protected while held, but transferable by intentional drop/pickup or validated trade; no duplicates |
| Recipe unlocks | recipeId, unlockSource, unlockedAt | Server-derived achievements |
| Crafting operations | operationId, recipeVersion, status, sourceId, inputs, outputId | Pending/committed/failed reconciliations |
| Extraction receipts | receiptId, runId, portalId, items, valuation, status | Retry-safe source item accounting |
| Player choices | pinnedRecipeIds, safe loadout settings, cosmetic choice | Untrusted display choices validated when used |
| Metrics | run counts, secure extracts, deaths, event participation | Bounded and versionable counters |

Large histories may need compaction and retention limits to fit Roblox data budgets. Use separate identifiers for **item instance**, **boss encounter reward grant**, **extraction receipt**, and **Forge operation**; never reuse one ID as every concept.

### 23.3 Operation transaction sketch — Proposed

- **Forge request:** (player, recipeId, selected vaulted sourceId, requestNonce).
- **Reserve:** Acquire serialized profile mutation; validate stored quantities and source; record exact recipe version and input snapshot; escrow/lock inputs.
- **Commit:** Mark all inputs consumed and create exactly one ordinary output or Permanent armory record in the same logical profile update where possible.
- **Acknowledge:** Return committed operation ID, authoritative output identity and new balances only after durable state.
- **Retry:** Query same nonce/operation; if already committed, return prior receipt; if pending, reconcile; never repeat grants or charges.
- **Audit:** Log status changes and unusual repeated attempts without dumping sensitive player information.

**Implementation caution:** A DataStore update is not a general distributed transaction across player profiles, world-drop actors and other stores. Prefer coherent single-profile atomic mutation for Secure Forge and carefully documented protocols for run-to-vault handoff. Do not promise true multi-store atomicity without building and load-testing reconciliation.

### 23.4 Recommended module boundaries and content definitions

- Shared typed definitions: item archetypes/levels, armor, arrows and physical-projectile profiles, healing/food effects, tribe/downed/revive states, structures/totem decay, weighted events/biome spawns, extraction definitions and tuning constants. **No player magic school system in MVP**.
- Server-only domain actions: validated combat, event reward creation, world loot, binding/withdrawal, conversion, anti-grief structure placement and DataStore handling.
- Client-only UI and effects: input mapping (mouse/touch/gamepad), preview/animation, inventory panels, rarity icons, world beacons and visual Burden of Wealth.
- Build a short integration test environment for all state-changing remotes with synthetic invalid/duplicate requests before adding production recipes.
- Use Rojo-local workflow where applicable, but **publishing only from main**. No code or deployments are implied by this GDD revision.

## 24. Economy abuse cases and anti-duplication tests

| Threat / fault | Required prevention |
| --- | --- |
| Client sends invented Permanent equipment ID | Output resolved only from server catalog and validated recipe |
| Player converts item still in active island | Only eligible secure-vault source instance can be escrowed |
| Reuse of source in two Forge requests | Source reservation and per-player serialization |
| Repeat same request from lag or macro | Idempotency key returns one durable result |
| Two devices simultaneously crafting | Session lease, profile revision and per-profile mutation queue |
| Teleport during consumption | Recoverable journal with stable operation and committed output IDs |
| Client manipulates ingredient count | Never trust client quantities or balance changes |
| Forge item created but source not deducted | One logical transaction / repairable pending operation |
| Rarity changed in client preview | Immutable server recipe version and source attribute snapshot |
| Permanent item dropped or traded to another account | **Allow** valid server-authoritative single-instance ownership transfer; reject duplicate pickups, forged trade acceptance or stale owner restores |
| Second instance manifested on another server | Server-held active lease; reconnect resolution |
| Dead player extracts and also drops loot | Exclusive death vs extraction commit state gate |
| Portal multiplier mints extra rare resources | Portal bonus applies only to designated payout value |
| Boss health crosses 25% multiple times | Encounter-scoped once-only Legendary grant |
| Crafted item with negative/overflowed quantities | Positive bounded integer validation and inventory caps |
| Shutdown/data budget exhausted | Pending receipts, retry/backoff and explicit non-success states |
| Raiding vault from physical island structure | Vault and Permanent armory have no in-world raid surface |
| Building piece overlaps portal aura | Validate full geometry overlap within 50-meter world-rule zone |

Create security-oriented automated tests for each abuse case before release. Admin repair/restoration procedures require audited permission boundaries and a unique restoration ID, so support tools cannot unintentionally duplicate Permanent equipment.

## 25. UX specifications and interface inventory

### 25.1 Lobby / hub navigation

The persistent hub should offer **Deploy**, **Secure Vault**, **Permanent Armory**, **Special Forge**, **Recipe Tracker**, and **Recent Extractions**. Display safe/protected versus risked status using words and distinct iconography; do not rely on rare colors alone. A permanent item in recovery is shown as **Owned — Recovery Needed**, not missing from inventory.

### 25.2 Post-extraction receipt

Show (a) rune/portal and completed status, (b) vaulted materials by exact quantities, (c) unique extracted gear, (d) valuation/multiplier breakdown without fabricating extra item copies, (e) craft milestones and newly available recipes, and (f) next step. If the write is still pending, state that unambiguously rather than playing a success animation.

### 25.3 Forge recipe browser and permanent conversion confirmation

- Filters for tools, ordinary weapons, armor, **food and medical consumables**, construction parts and Permanent recipes. **No launch enchantment category**.
- Crafting detail includes **Owned/Required** stacks, region/event sources for scarce ingredients, recipe/level unlock, source/result stats and consumed crafting materials; **weapons and armor do not wear or break**.
- Permanent conversion displays the exact source instance that will disappear, a preview of bound restrictions, recovery costs (if any), and *confirm/cancel* with deliberate focus for touch and controller.
- Show recipe progress in percentage only when genuinely derived from verified vault stack totals; do not count unextracted backpack materials.
- "Craft" button disabled when there is an unresolved conflicting Forge operation, invalid source, not enough resources or capacity failure.
- On successful commit, animate the transformed source becoming a **single** Permanent armory record. Backend confirmation precedes celebration.

### 25.4 In-world HUD / inventory

- Weapon slot labels indicate **At Risk / Drops on Death** versus **Bound / Armory Recovery on Death** under chosen policy.
- Rune activation shows name, portal valuation bonus, time/channel progress, interruptions and nearby threat cues.
- When special event loot is carried, server triggers visible burden VFX and explains that it increases ambush risk.
- Map and alert cues combine icon, text, motion and sound for accessibility. The 3-minute Guardian countdown remains distinct from ordinary cache beacons.
- On death, categorize **Dropped and lootable**, **Safe in Vault**, and **Bound armory recovery** separately.
- On mobile, minimize precision drag requirements for recipe source selection and field base placement.

### 25.5 First-session tutorial beats — Proposed

Teach gathering/crafting; light PvE combat; a visible stash risk warning; successful minor rune extraction; secure vault contents; a preview of a special recipe; a clear example of how a rare ingredient later converts a specific piece of gear into Permanent. Never grant free Permanent gear merely as a tutorial completion shortcut.

## 26. Quantitative tuning and live analytics plan

### 26.1 Balancing equations

- **Secured output per run** = opportunities × average item drop quantity × pickup share × successful-extraction probability.
- **Time to ordinary recipe** = recipe cost ÷ safe acquisition rate, accounting for competing uses and deaths.
- **Time to Permanent** = expected runs required across multiple rare input sources + original gear acquisition + requisite crafting mastery.
- **Net supply** = extracted supply − regular crafts − Permanent crafts − field usage − repairs/recovery.
- **Risk-adjusted central portal value** = (probability of escaping center × payout) − (expected loss of carried kit and materials). This should sometimes be inferior to the minor-rune strategy, depending on run circumstances.

Never tune crafting only from nominal boss drop rates. If most boss loot is stolen or lost before extraction, vault acquisition rates are dramatically lower.

### 26.2 Starting success criteria — proposed directions, not fixed thresholds

| Observable | Healthy signal | Warning |
| --- | --- | --- |
| First extraction | A solo novice can finish one in early play | Every rune is permanently camped |
| First special craft | Realistic after several cautious successful expeditions | Forge appears unreachable or gives instant best gear |
| First Permanent craft | Aspirational across multiple runs | Single event trivially completes recipe, or only largest tribe can qualify |
| Endgame Permanent acquisition | Hard, multisource progression | Forced repetitive boss monopoly |
| Bound vs ordinary PvP | Real counterplay at similar skill/tier | New players have zero credible chance |
| Center portal | Sometimes worth extra danger | Always optimal with no tradeoff |
| Base raiding | Cost and risk balanced against accessible stash loot | Free endless structure destruction |
| Resource sinks | Saved rare materials remain valuable | Hoarding inflates or repair consumes everything |
| Persistence | Zero observed dupes and unexplained committed losses | Rejoining duplicates bound gear or deletes inventory |
| Solo vs tribe | Multiple viable routes and extraction patterns | Players need a dominant clan for every conversion |

### 26.3 Telemetry schema proposals

Record server-side structured events for: run start/end, first harvest/craft, ordinary item death drop, unique loot pickup/stolen, meteor mine, cache channel, alpha reward, boss phase and 25% drop, portal start/interrupted/committed, vault receipt, recipe preview, Forge reserved/committed/reconciled, Permanent equip/death recovery, stash raid, and repair/sink. Segment anonymously by solo/tribe, gear band, portal tier, event source and account tenure. Audit economy by item/source category, not by treating every drop as banked.

## 27. Detailed verification matrix and QA plan

### 27.1 Automated functional test targets (when code exists)

1. Secure extraction deposits correct resource stacks and unique gear once; death or interruption before commit deposits nothing.
2. Partial network failure with a completed extraction commit shows the correct receipt after rejoin.
3. Same extraction receipt replayed repeatedly does not credit double stacks or gear.
4. Converting an eligible stored source charges each ingredient once, consumes the source and creates one bound record.
5. Reject conversion if source belongs to another player, is not vaulted, is already Permanent, is leased, or is ineligible.
6. Insufficient ingredient quantity, invalid unlock, stale recipe version, malformed requests and negative values cannot forge gear.
7. Two simultaneous conversion calls targeting same weapon: only one can commit.
8. Retry after timeout before/after a durable write yields the same final state; no missing weapon or duplicated result.
9. Permanent item **still owned** at death remains with owner with unchanged stats (recovery material cost Open); ordinary items go to corpse. No second Permanent instance minted.
10. Permanent items can be **manually dropped, stolen by valid pickup, and traded**, but cannot be duplicated, forged, double-claimed from one ground drop or simultaneously equipped on multiple servers.
11. Guardian Legendary spawns once per encounter at 25%; killing boss is not automatic extraction or conversion.
12. All rune auras reject new construction within 50 meters; externally anchored overlapping geometry cannot enclose portals.
13. Portal payout never duplicates unique materials, Keystone, Legendary source instances or crafting outputs.
14. Cache requires a continuous 60-second unlock under specified interruption rules; event UI and world beacon agree.
15. Invalid click melee reach/rate, forged **slow physical bow projectile** or crafted-arrow count, healing replay, food HoT tampering, and malicious client remote sequences are rejected. No player-cast elemental effects in launch builds.
16. DataStore throttle, teleport failure, competing sessions, server shutdown and stale revision rejoin retain safe state integrity.
17. Mobile and controller players can navigate Forge and extraction without mouse-only precision.
18. Recipe tracker reflects only safely extracted materials; death changes only at-risk inventory.
19. No deployment or publishing workflows target temporary/version branches; only main may publish.
20. Deployed Roblox place testing is **not applicable until source/place credentials are connected**.
21. Joining a play-world place creates no active avatar/loot risk before loading and explicit Play; a failed teleport, profile load, kick or character spawn from that state cannot delete gear.
22. Duplicate Play/forged remote cannot start combat, award an item or cause corpse loss; risk begins only after a successful server-controlled spawn/ActiveRun transition.
23. Ordinary **active-run** departure (not a protected world main-menu leave) produces exactly one corpse for 600 seconds, with unclaimed loot despawning at expiry and claimed loot owned exclusively by looter.
24. Safe lobby exit, loading-screen quit, world main-menu quit, failed teleport and unsuccessful Play admission never create a loot body or forfeit inventory.
25. Authorized admin-update safe-kick preserves exact held items (no extract/multiplier), shows player update/saved-inventory notification and allows continued use on next Play; forged client admin flags and duplicate restore requests fail.
26. Clicking an available fixed rune broadcasts large-radius audio/visual cues and starts **one server-shared 120-second event**; players may leave the area, fight and heal, and qualify only by being alive **inside it at expiry**. Rare portable runes use 30 seconds.
27. At valid animation-start threshold, damage and disconnect cannot cause item loss; idempotent locked receipt settles exactly once, even after DataStore fault.
28. Corpse-versus-extract and corpse-versus-maintenance races never grant double inventory or lose protected items.
29. Rare plants/materials, elite mobs/bosses, raid structures and meteors have finite rewards and tier-appropriate announcements.
30. Activity rewards are validated across PvP, farming and building and resist AFK/idle/server-hopping exploits.

### 27.2 Manual playtests — Requires Manual Validation

- Fresh solo onboarding from beach through first secure extraction and first special recipe.
- Two-to-four player contested alpha/cache interactions; 60-second cache stand-off tests.
- Tribe FOB raid while defenders are away; stash loot/drop and structure limits.
- PvP duels contrasting early, normal legendary and bound permanent builds.
- Boss telegraph accessibility under particle-heavy full-server combat, including 25% betrayal.
- Permanent crafting comprehension: can testers clearly explain the difference between **Vaulted** and **Permanent**?
- Simulated poor mobile network, client close mid-portal channel and rejoin mid-Forge request.
- Performance under many dropped items, structures, beacons and ability effects.
- Event and recipe progression viability for solo players compared with large coordinated tribes.

### 27.3 P0/P1 design review gates

**P0 — must explicitly decide before implementing persistence or permanent systems:**

1. **Confirmed:** A specific Permanent equipment instance survives death, but legitimate deliberate ground-drop pickup or trade **transfers ownership**. Engineering must prevent double restoring the former owner.
2. Recovery payment/delay and whether bound gear can wear out permanently.
3. **Open:** Permanent equipment slot cap and archetypes (no hardcoded final number).
4. **Confirmed:** Permanent equipment is transferable by deliberate ground drop/pickup or valid trade. **Open:** Gifting, market mechanics, safeguards and post-drop unclaimed item fate.
5. Ordinary vaulted item withdrawal and reconnection handling.
6. Item-instance provenance, cross-server session locking and operation journal semantics.
7. How event-critical unique items are represented and multiplied/valued on extraction.

**P1 — can remain proposed through first prototype, then tune:**

8. Recipe resource quantities, sources and rarity names, Keystone path, unlock milestone requirements.
9. **Confirmed:** Permanent conversion gives **no extra combat stats** compared with source equipment. **Open:** PvP source item and repair balance.
10. **Open future-only:** Whether enchantment affixes or specialized defenses should be introduced in an update. No launch item durability repair/charge mechanic.
11. **Confirmed:** Vault has upgradeable capacity and withdrawal. Ordinary gear lasts indefinitely without durability wear. **Open:** Upgrade prices, tiers and carrying stack weights.
12. Boss clear rewards beyond the confirmed mid-fight Legendary.
13. **Confirmed:** Provisional 30-player instances wipe **when empty only**; fixed exit countdown 120 seconds (zone check only at expiry), portable 30 seconds; exact travel/raid/party balance Open.
14. Cosmetic monetization, tutorial content, achievement rewards and hub architecture.

## 28. Production milestones and documentation maintenance

| Step | Scope | Completion evidence |
| --- | --- | --- |
| 1. Design agreement | Choose Permanent death model, rarity/eligibility, vault semantics and precise ActiveRun admission authority | Explicit signed-off GDD decisions (not just proposed paragraphs); confirmed pre-spawn safety preserved |
| 2. Risk loop vertical slice | Protected world menu/Play readiness, then gather, fight/heal, corpse, shared 120s timer and protected animation | Teleport failures safe; death kicks/ejects; corpse 600s; roaming countdown and deadline-only zone qualification; individual protected receipts |
| 3. Forge / ownership proof | Ordinary special recipe, one eligible source conversion, bind slot, recovery | Verified exactly-once crafting under retries, real rejoin/death tests |
| 4. Social / PvP slice | Click spear/sword, slow arrow-projectile bow, crafted arrows, sprint/crouch, instant medicine, food HoT, 60-second tribe revive | Validate solo immediate death, revive pause/resume, no respawn, PvP everywhere except safe POIs; no magic |
| 5. World + raids | Random map spawning; Booga Booga wood/stone/iron, totems/decay, open storage, crops/trees and raids | Owner leaves but base remains, totem stops natural decay, no special raid tool, farming progresses while server active |
| 6. Broadcast event | Weighted event tick, **all events publicly announced**, biome-random resources, boss ritual/event/structure sources and rare carry burden | Server event distributions measurable, PvP loot contested and still requires extraction |
| 7. Crater Guardian | 15–20-minute cadence, horn, pillars, fight, 25%-HP drop | One mid-fight Legendary and accurate telegraphs; no auto-vault |
| 8. Economy alpha | Recipes, conversions, activity rewards, economy telemetry and sinks | Solo/farmer/builder/PvPer progression viable, no AFK exploits or observed dupes |
| 9. Launch readiness | Full server profiling, accessibility, persistence faults, anti-exploit | Reviewed CI, manual playtests and publish-from-main gates |

**Current actual status:** Design only. The GitHub repository contains Markdown documentation, not a playable Roblox implementation. Costs, health/food/stamina tuning, revival mechanics, damage/protection boundaries and weighted event probabilities need implementation and playtest validation.

## 29. Ordinary departure, death and lootable bodies

### 29.1 Confirmed risk and loss boundary

**Only an active, successfully spawned play-world character has inventory risk.** This is the latest confirmed design clarification. Merely connecting to a play-world server, loading assets, arriving via teleport, viewing its pre-spawn main menu, or pressing a Play button that has not successfully admitted/spawned the character **must never cause loss**. See §31.

When an actually active character dies or voluntarily/involuntarily leaves the play world **before protected extraction**, that character leaves a **lootable body in the same active public server**. The player loses their unsecured ordinary carried items; nearby players may loot the body. The body **and any unclaimed remaining loot despawn after exactly 10 minutes (600 seconds)** from body creation. A successful extraction animation, an authorized maintenance safe-kick, and the protected pre-spawn menu are explicit exceptions. A character is never converted into loot merely because the Roblox client teleported into a new place and is still loading.

| Player location/state when leaving | Body created? | Are unsecured held items lost? | Safe storage outcome |
| --- | --- | --- | --- |
| Secure lobby/hub | No | **No** | Existing vault/transit inventory preserved |
| Destination play-world server, pre-spawn loading or main menu | No | **No** | Reserved loadout retained in recoverable safe state |
| Play clicked but server has not successfully admitted/spawned character | No | **No** | Play reservation rolled back or safely retried |
| Active play-world character | **Yes**, 600-second corpse | **Yes**, regular carried gear/resources | No extraction or vault payout |
| Active 120-second extraction countdown | **Yes**, if player quits/dies before qualifying and protected animation | **Yes** | Shared event timer keeps running; no extraction for dead/out-of-zone characters at deadline |
| Server-authorized protected extraction animation | No loot corpse for locked items | **No** | Locked extraction entitlement reconciles to vault |
| Authorized administrator update safe-kick | No loot corpse | **No** | Held inventory preserved in maintenance-recovery escrow |
| Platform failure terminating the entire server | Cannot maintain body after the instance ends | No automatic extraction | **Open:** explicitly designed crash recovery (not normal leave) |

**Permanent item exception:** It **stays with its rightful current owner** on death, with no corpse copy. It **can** appear as a lootable ground item when *intentionally dropped* and then ownership legitimately transfers to the picker (§17); the previous nontradeable model is superseded.

### 29.2 Body creation and looting — Confirmed behavior / Proposed implementation

1. Upon active character death or ordinary departure, freeze the inventory transfer and create **one** server-owned corpse/container with an immutable corpse ID, player/run ID, creation time and expiration time exactly **600 seconds later**.
2. Place only eligible *unsecured* inventory into that corpse, once. Vault items, protected extraction snapshots, Forge reservations and Permanent armory canonical records are not valid corpse inputs.
3. Other active characters may interact/pick up individual stacks and gear if server proximity and capacity requirements are met. For unique gear, one item instance can have only one owner/location.
4. Loot remaining in the body at expiration is deleted from the active world, not returned to the disconnected player. Items successfully claimed before expiration remain with the looter, still unsecured until **their own extraction**.
5. Expiration is server-authoritative and starts from body creation, not first discovery or first looting. The visual model must not remain as a separate loot source after its container is destroyed.
6. **Proposed:** Show a readable world body and loot prompt, supported on mobile/controller, with a short decay/despawn indicator while interacting. Do not broadcast every death globally.
7. On double death/disconnect callbacks or rejoin, idempotency keeps exactly one corpse/drop transfer. Client never specifies corpse contents or expiration.

**Open:** Death animation/model, physics collision, whether gear equipped by the fallen player shows visually on the corpse, loot reservation rights and whether stacks dropped separately from the corpse. None may invalidate the confirmed 10-minute body TTL.

### 29.3 Disconnect semantics

- Ordinary network loss, rage quit or closing Roblox **after entering ACTIVE gameplay** is a forfeiture, even if no attacker is nearby.
- The game must **not** infer Active from place ID alone. Pre-spawn main menu users remain safe despite physically occupying a play-world server (§31).
- If a player leaves after the protected extraction animation started, the protection outcome wins regardless of whether they see the final vault-receipt screen.
- Safe administrator maintenance removal is authorized by the server, not by a client flag or mere kick reason string.
- A duplicated character session must not generate repeated bodies or recall items that others already looted.
- **Confirmed / Proposed UX:** An active-run disconnect forfeits ordinary unsecured gear; the player may **rejoin that still-running world** if they were not killed/forcibly excluded, but does not regain lost items. A **death** ejects them to reduce corpse retrieval chances, with a same-world admission restriction to implement. Pre-spawn failure never counts as death or item loss.

## 30. Administrator update kicks and maintenance-safe preservation

### 30.1 Confirmed product requirement

Administrators need commands to remove players **without losing their items when updating the game**. The next protected menu **notifies them of the update kick and saved held inventory**, which they resume on next successful Play. This is a privileged exception to ordinary active-world departure, not extraction or free vault deposit. It also works during an extraction timer; players still on pre-spawn menu are already safe.

### 30.2 Proposed safe-removal protocol

1. Authenticated, permissioned administrator issues a deliberate **maintenance-safe kick** or update shutdown through server-only administration tooling. An ordinary kick must not accidentally acquire safe privileges.
2. Freeze the affected player's active inventory and turn off new loot pickup, transfers, crafting, drop and portal commit until the preservation outcome is resolved.
3. Record the **exact ordinary gear/material/consumable snapshot** under a unique maintenance-recovery operation ID. This is **unsecured preserved carryover**, not a successful extraction. Do not apply portal bonuses or make it usable for the protected Forge while in recovery.
4. Persist the snapshot in an access-controlled, retry-safe recovery state and prevent the same world inventory from also becoming a corpse.
5. Only after recovery entitlement is established, perform the safe kick/server restart; if persistent storage fails, do not falsely promise safe removal. Retry/defer shutdown as supported and surface the operational error.
6. At the player's next lobby/pre-spawn admission, **explicitly notify them of the admin game-update kick and their saved inventory**. **Confirmed:** They resume with the exact previously held items after the next explicit successful Play; these have **not** been extracted or made Forge-safe.
7. Each maintenance operation can be consumed/resumed once. New active server session IDs and item IDs prevent concurrent duplicated restorations; audited administrators cannot silently create a second equipment set.
8. **If a valid extraction animation already started first**, honor extraction snapshot ownership rather than also granting a maintenance escrow copy.

### 30.3 Permission, grief and abuse safeguards

- Authorize commands using server-held administrator IDs/roles and restricted command dispatch; never trust client-provided permission tags or arbitrary RemoteEvent requests.
- **Proposed:** Separate ordinary moderation kick (may exclude rejoin) from audited **safe-update kick** (preserves items and notifies player). Exact command names and treatment of punitive kicks remain **Open**.
- Update shutdown should safely process all active player snapshots; pre-spawn menu players never had risky inventory so retain their reserved loadouts without world body creation.
- Record initiator, timestamp, update version, server job/run ID, affected sessions, escrow operation IDs and success/error status.
- Never allow players to spoof a maintenance kick with a client disconnect, intentionally triggering a crash, or asking a player-owned NPC to end the session.
- A platform outage is **not** implicitly a safe-update kick and cannot be treated as confirmed preservation without separately implemented crash recovery rules.

## 31. Protected play-world main menu and teleport-safety design

### 31.1 Confirmed user journey and safety invariant

**The play-world server itself has a main menu.** Every arrival enters a **non-risk, pre-spawn staging state**, including first deployment, rejoin, returning from another place, and teleport retries. The server does not spawn a vulnerable player avatar merely because Roblox reports that the player joined. The player sees the menu while profile, loadout, scripts, UI and required world assets load.

**Only when the player explicitly clicks Play, server readiness checks pass, and the character successfully spawns into gameplay is their inventory put at risk.** If anything fails before that authoritative activation — network timeout, kick, game closure, loading error, teleport failure, death-like automatic spawn failure, Roblox server rejection — **nothing can be looted or forfeited**. The admission state, not the physical server/place, defines risk. There is no "free death" on a loading screen.

**Recommended engineering order:** Delay automatic character loading (for example, use server-controlled character spawning); do not create a vulnerable character while the loading menu is displayed. If the engine or character customizer requires a preview avatar, keep it isolated/invulnerable and **outside the actual run inventory system**. Begin risk only when a real play avatar is validated and activated.

### 31.2 Server-authoritative player-session states

| State | Can player take combat damage? | Can leave safely? | Has lootable body? | Exit/next transition |
| --- | --- | --- | --- | --- |
| **LobbySafe** | No | Yes | No | TeleportPending or stay |
| **TeleportPending** (source lobby, in-flight) | No | Yes | No | StagingLoading, or safe return/retry on failure |
| **StagingLoading** (inside world server) | No | Yes | No | WorldMainMenuReady; failure stays safe |
| **WorldMainMenuReady** | No | Yes | No | PlayRequested only via Play button |
| **PlayRequested / SpawnPreparing** | No | Yes | No | ActiveRun after server-confirmed successful spawn, or safe revert |
| **ActiveRun** | Yes | **No**, normal leave drops loot | Yes on death/ordinary departure | ExtractionHolding, death/body, or authorized maintenance |
| **ExtractionHolding** | Yes | No, normal leave drops loot | Yes on death/ordinary departure | ActiveRun on cancel, or ExtractionProtected |
| **ExtractionProtected** (animation has begun) | **No, invulnerable** | **Yes** | No for locked loot | Persistent receipt reconciliation / LobbySafe |
| **MaintenancePreserved** | No | Yes | No | Recoverable safe staging / explicit future Play |
| **Dead / BodyLootable** | Not a living player | N/A | Yes, exactly 600-second expiration | **Kick/eject player from that play-world instance**; mark same-world rejoin ineligible until instance ends |

**Nonnegotiable boundary:** Being inside a play-world Roblox place is not synonymous with **ActiveRun**. All death-drop, logout penalty, body-spawn and loot-loss actions must check authoritative ActiveRun/ExtractionHolding state and **must not execute** for loading, menu, failed admission, protected extraction or maintenance-preserved states.

### 31.3 Main-menu loading, Play enablement and spawn protocol — Proposed

1. Player joins the play-world server. Assign new session ID and set **StagingLoading** before any avatar can participate in combat. Disable normal spawns/physics-based world interactions.
2. Load/verify account profile and secure loadout reservation, pending protected extraction receipts and maintenance carryover escrow. Lock profile against conflicting writes across simultaneous servers.
3. Load required server-side world rules and the essential client interface/assets. Client may report its loading progress, but **server** must verify profile ownership, world readiness and final admission constraints. Never treat an untrusted "loaded=true" remote as the sole proof.
4. Show menu with progress, connection status, Play button and clear text: **"You are safe until you enter the world."** While loading, Play is unavailable. A failed load offers retry/return; no item consumption or corpse.
5. Once ready, enter **WorldMainMenuReady**. The character has **not** spawned into lethal gameplay. Allow menu exit or disconnection with no penalty.
6. When player clicks **Play**, server validates ready state, intended loadout, one active session and valid available spawn. Repeated button clicks must be idempotent and must not spawn multiple characters.
7. Prepare/spawn real character in a valid starting area **without exposing it to damage while incomplete**; only after initialization succeeds commit the **ActiveRun** state and release protection. **That successful admission is the inventory-risk threshold.**
8. If profile/character/spawn placement/teleport handoff fails, revert to safe pre-spawn state with all reserved ordinary gear intact and zero corpse. Do not debit consumables, apply item wear or count deaths.
9. On active death/ordinary leave, use §29's corpse rules; on valid extraction animation, use §9/§22's protected receipt rules; on authorized maintenance, use §30's preservation rules.

### 31.4 Loadout and inventory escrow during teleport — Proposed

- Before a lobby-to-world teleport, keep ordinary selected gear in the safe source profile or create **one** atomic/resumable transit reservation. The source never drops it just because a teleport was requested.
- The destination must validate transfer/session identity and stage the chosen loadout while **not yet at risk**. A player leaving the destination main menu, erroring before Play, or failing an asset load recovers the selected gear exactly once, not duplicated into both destinations.
- Withdrawn ordinary gear becomes **at risk only after ActiveRun successfully begins**. The word **Withdraw** in UI cannot override this server admission contract.
- Inventory risk must not start at Play button press if the actual spawn/initialization never succeeds; preserve the user's intended "click Play to enter" experience with an atomic server acknowledgement.
- Once ActiveRun was legitimately entered, a later unauthorized voluntary teleport or client exit must **not** bypass the normal death/body rule. The safe lobby-to-world handoff exemption is for *pre-run* staging, not an active combat escape hatch.
- Pending Forge or extraction operations use their original durable receipt rules; do not let fast retries mint a second copy of consumables or bound gear.

### 31.5 Failure/edge-case matrix

| Failure or action | Required outcome |
| --- | --- |
| Teleport fails from lobby before world arrival | Player remains safe; selected gear still owned; no body |
| Roblox client closes during teleport | Safe transit can reconcile on next join; no loss |
| Client closes while pre-spawn menu is loading | No death, loot, corpse or inventory loss |
| Client closes with main menu open | Same loss-free result |
| World server kicks player before Play | Safe reserved inventory; no body, even if auto-character callback fires |
| Profile DataStore timeout before Play | Remain safely loading/retry; Play unavailable |
| Duplicate Play requests | Exactly one successful spawn/admission; no duplicated equipment |
| Character cannot spawn or is destroyed before successful admission | Return safely to menu; zero combat death/loot drop |
| Server admits player and they enter active gameplay | Risk starts, with explicit gameplay HUD/transition |
| Active player dies | Corpse appears for 600 seconds, player is **kicked out of the play world**, and same-world rejoin gate rejects that user while this instance exists |
| Eligible active player leaves but has not died/kicked | Ordinary carried items are forfeited to corpse; they may rejoin the same running server if eligible but previous items are not restored |
| Player deliberately quits after becoming ActiveRun | One lootable body; 600-second unclaimed loot expiry |
| Player quits with 15 seconds left on shared extraction countdown | Ordinary body; may not extract even if others qualify when timer expires |
| Player closes client one frame after protected animation begins | Safe; locked loot reconciles to vault |
| Update admin safe-kicks an ActiveRun player | Preserve held gear in maintenance escrow; no body or free extract |
| Entire Roblox instance crashes | Must define crash recovery separately; no fake corpse timer in destroyed server |

### 31.6 UX and accessibility rules

- World main menu contains the game identity, **Play**, loading/connection status and optional tutorial/help/settings. Show risk explanation only as Play is enabled; do not force players to defend a loading screen.
- The Play button must not accept input until critical loading completes; on invalid or duplicate press, keep a clear status rather than silently putting player into combat.
- Transition animation must communicate **"Entering world — items are now at risk"** only when server confirms actual active spawn.
- Once in active play, pause/menu UI is **not safe** by itself; opening a settings menu does not suspend risk.
- Extraction explicitly changes from **"120-second danger"** to **"Protected: extracting"** at the server-authorized animation. Safe lobby/menu players cannot use the extraction-activation path without an active avatar.
- For touch/controller, ensure accessible menu focus, large enough Play activation, visible loading failures and easy retry controls.

### 31.7 Acceptance tests (P0)

- Join into world 100+ times with delayed assets/profile; cannot spawn vulnerable or drop equipment before confirmed Play admission.
- Simulate Roblox teleport failure, disabled network, character-loading failure, profile timeout and a kick from menu: each leaves identical safe inventory and no corpse.
- Inject double Play and remote spoofing; one authoritative ActiveRun only.
- Under lag, attempt to kill a pending character before admission: no valid CombatService damage; no loot/body.
- Verify admission state transitions atomically with inventory transfer and player-session lease; crashing between stages cannot lose or duplicate gear.
- Verify intentional active quit still creates a corpse, despite the world having a main menu feature.
- Validate protected extraction/mid-animation disconnect and maintenance update overrides as separate states, not global safe logout.
- Test resume/return after lobby, world, mobile and console teleport failures; no loss and accessible error presentation.

## 32. World ecology, procedural rare spawns and structure takeover

### 32.1 Weighted publicly announced events — Confirmed

The event director **ticks periodically** and uses **weighted rarity** to decide whether an event occurs and which valid category appears (§7). **Every event has a public announcement**, even for rare shrubs or trees. Flora, ore and event resources appear at **random suitable biome positions**, not guaranteed coordinates.

| Event category | Valid location | Possible gameplay |
| --- | --- | --- |
| Rare shrubs/trees/herbs | Random in appropriate biome | Harvest for healing/food and special recipes; rivals may intercept |
| Rare mineral nodes | Random biome-valid deposits | Risky iron or advanced material harvesting |
| Rare mobs | Biome-selected locations | Ancient creatures, skeletons, elemental monsters, evil NPCs, mythical enemies |
| Event-only regional boss | Scheduler-selectable arena | PvPvE fight with contested material drops |
| Material ritual boss | Valid player-triggered summon location | Spend rare materials to call an enemy; other players can steal its loot |
| Structure boss | Inside/described by generated structure | Loot through combat and raids |
| Raidable public structures | Abandoned shelters, defended camps, ruins | All three variants supported and **never player-claimable** |
| Meteors/caches | Valid landing zone | Contested harvesting or 60-second cache unlock |

**Elemental enemies do not grant players a magic system.** The Guardian remains a distinct central boss with its prior timeline unless explicitly revised.

### 32.2 Accessible player construction and takeover

**Confirmed:** Booga Booga-inspired placement; wood → stone → iron initial structure tiers; farms, chests, workstations, furniture, beds and other functional objects are desirable. Player bases remain for others after owners leave, subject to **unclaimed decay**, and are **raidable around the clock** with ordinary weapons/tools.

- **Tribe claim totems:** Nearby claimed **player-built** structures are protected from **natural decay only**, not damage/raiding. Without a nearby totem, each structure eventually decays. Radius and decay rate still need design.
- **Takeover:** A deserted base may be occupied by a different group even if its original owners left. Replacing/destroying claim totems and transferring structural ownership need a ruleset; unclaimed storage is already accessible to anyone.
- **Storage:** **All players can access world storage** once they can reach it. A locked chest concept must not override this rule. Terrain/building walls may prevent physical access until raided.
- **Farms:** Crops and planted trees grow **as long as that server is populated**, even after the farmer leaves. When the world empties, plants, buildings and all other world state disappear.
- **Structure sources:** Server-generated ruins, outposts and structures remain world-owned, **never** claimable through a tribe totem. They may be raided and looted.
- **Breach:** Standard weapons/tools can damage structures; rare siege tools may accelerate breaches but are **not required**.
- **PvP:** Enabled everywhere except specifically designated safe POIs. Totems are not safe-zone anchors, and no ordinary player base grants PvP immunity.
- **Build exclusions:** Keep confirmed fixed-extraction **50-meter no-build auras**. Portable-rune placement interactions remain a later balance decision.

### 32.3 QA gates

Verify biome randomness, event public announcements, weighted distribution, 8-member tribe maximum, tribe claim scope excluding server-generated structures, decay start/stop based on totem proximity, persistent-in-live-world abandoned bases, no-respawn beds, accessible public storage, any-time ordinary-tool raids, and farming continuing after owner exit while other players keep server alive. All resets must discard temporary world objects once its last player departs.


## 33. Public-world playstyle rewards and engagement design

### 33.1 Confirmed intent

Remaining active in a shared **public world** should be useful even without continuously pursuing the Guardian or PvP. The system should recognize materially different contributions: **PvPers**, **base-builders**, **farmers/gatherers**, hunters and explorers. Rewards should create fresh reasons to stay in a populated world, engage in the local ecology, form rivalries and extract meaningful resources, without making idle time a dominant strategy.

**Clarification:** Confirmed is the goal of rewards/benefits for sustained public-world participation, **not** passive cash paid per minute, guaranteed safe item drops, free vaulting or unlimited combat stat buffs. The proposed reward ideas below require tuning and owner approval.

### 33.2 Candidate playstyle loops — Proposed

| Identity | Meaningful in-world contribution | Example optional benefit | Exploit guardrail |
| --- | --- | --- | --- |
| **Farmer / herbalist** | Tend and harvest farm plots, locate rare shrubs and trees, transport supplies | Herbal medicine recipes, farming-oriented crafting proficiency or resource yield insight | Cap repeated identical plots; verify genuine growth and harvest intervals |
| **Builder / engineer** | Construct, repair, reinforce and defend raidable FOBs | Alternate structure skins, repair efficiency or construction recipe progress | Prevent rapid place/destroy loops and worthless-structure spam |
| **PvPer / raider** | Win meaningful hostile encounters, contest high-value objectives and loot enemy supplies | Cosmetic titles, tracked rivalries, raiding recipe discoveries | No rewards for alt kills, same-player kill trading or spawn farming |
| **Hunter / boss challenger** | Track fauna, fight alphas and contest rare regional bosses | Hunting trophies, tracker utility, alpha-reagent craft unlocks | Server contribution checks; avoid merely tagging bosses |
| **Explorer / scout** | Discover rare event spawn areas, new routes and extraction runes | Cartography discoveries, regional knowledge and exploration cosmetics | One-time/progression caps per genuine discovery |
| **Tribe supporter** | Supply shared fortification and field expeditions | Tribe contribution records, cooperative craft objectives | Avoid permanent exclusive buffs for the largest tribes |

### 33.3 Public-session progression proposal

1. Track verified **active contribution** within one public server: unique harvests, completed gathering interactions, distinct building/repair tasks, legitimate hostile combat, boss assists and exploratory milestones.
2. Award modest short-session milestones, achievements, recipe progress or discretionary **in-world** opportunities based on actual activity rather than time alone.
3. If retention benefits exist, use a **session-engagement track** with varied objectives and transparent thresholds; no safety or loot guarantee merely for being present.
4. Preserve competitive stakes: earned resources obtained in a public world remain **unsecured until successful extraction**, unless the benefit is an explicitly defined account-level knowledge/cosmetic unlock. No silent autopayout to vault.
5. Allow players to pursue different tasks toward progression; farmers/builders should not have to win constant PvP, and PvPers should not be forced into excessive harvest grinding.
6. Cap advantages by progression band and solo/tribe size; don't grant permanent stat boosts that only large organized tribes can stack indefinitely.
7. Prevent AFK exploitation with actual action/contribution validation, distinct task caps, cooldowns and anti-collusion checks (not solely movement spam or time online).
8. Visualize personal progress unobtrusively, without distracting players during combat or extraction.

### 33.4 Economy and integrity constraints

- Never grant Permanent gear merely for idling a specified time in a public world. Expensive Secure Forge conversion continues to require actual extracted rare materials and eligible gear.
- An ordinary logout **after ActiveRun admission** still drops the body; the world main-menu/loading state remains exempt even though the player occupies the game server. Account progress/cosmetics never make carried loot safe.
- Rewards earned while inside protected pre-spawn menu/loading **do not count as active public-world play**.
- When a **shared extraction timer ends**, only qualifying alive players **inside the area** begin protected animation; stop earning live-world combat/gathering rewards for **those extracted players**, not everyone around the rune.
- Proposed builder/farmer benefits must not enable invulnerable farming enclosures or permanent structures around protected **fixed** portals. Temporary portable rune interaction with buildings remains Open.
- PvP rewards should value real combat/contested outcomes, not repetitive farming of a cooperative alternate account.
- Telemetry should compare retention, solo success, conflict rates and material supply across playstyles before any direct resource multiplier is locked.

### 33.5 First implementation and QA gates

- Build and instrument **one** meaningful active-world contribution path for farming, building and PvP in a prototype, without substantial permanent numerical rewards.
- Evaluate whether players actually remain engaged within public worlds while extraction remains the primary safe banking mechanism.
- Test idle player, automated gather loop, place/remove spam, same-tribe kill trading, repeated alt defeats and server-hopping; none should infinitely print account rewards.
- Ensure pre-spawn menu waiting, loading delay, teleport retry and safe maintenance downtime do not count as active-game time.
- Track metrics by playstyle, gear tier and group size; maintain viable solo-player paths.
- Owner approval is required for exact award types, reward cadence, session persistence, and whether any benefits reset per server.


## 34. Owner-approved answers 1–24 (2026-10-21)

These answers supersede earlier proposals where conflicting. Specific balancing values and ambiguities explicitly left undecided are **Open**, not silently decided.

### 34.1 Server, world and death (1–7)

| Number | Owner decision | Status and necessary detail |
| --- | --- | --- |
| 1 | Target **30 players** per island | Provisional; refine based on map size and performance |
| 2 | A public world **resets only after its final player leaves** | Confirmed; no scheduled wipe while populated |
| 3 | **Everything in live world disappears** on reset; only Permanent gear survives | Confirmed for island structures/loot; possible contradiction with **ordinary extracted vault** is Open (§34.5) |
| 4 | Surviving, non-kicked players can return to the **same active world** | Confirmed, capacity permitting; an active ordinary quit still forfeits unsecured carried gear |
| 5 | On death, **kick/eject player from play world** to impede body retrieval | Confirmed; block immediate same-world rejoin via server admission as technical recommendation |
| 6 | Unexpected full-server crash should **safely restore active items** if feasible, or use special recovery | Confirmed preference; feasibility and fraud-proof implementation Open |
| 7 | Authorized update kicks **preserve precise carried items** and notify players of inventory preservation | Confirmed; player resumes with held items at next Play, not free extraction |

**Proposed Roblox rejoin implementation:** Separate start-place lobby and play-world place, configure play-world place **Secure within universe only** for server-initiated teleport access, and enforce a per-JobId death/kick exclusion in lobby matchmaking **and** play-world server admission. Killed players may join **different** worlds, not their previous world. This is not a universal setting to disable all friend-joining; Roblox user privacy/visibility is separately controlled. Roblox documentation: https://create.roblox.com/docs/projects/teleport and https://create.roblox.com/docs/matchmaking/scoring .

**Crash policy:** A whole-instance crash cannot leave a corpse behind for 600 seconds if the server no longer exists. Provide separately audited recovery/escrow, distinguish an involuntary server outage from an ordinary single-player connection loss, preserve latest actual owner and prevent restoration if a gear instance was already looted or traded. This is an engineering requirement, not a tested existing guarantee.

### 34.2 Permanent equipment, crafting and vault (8–16)

| Number | Owner decision | Status |
| --- | --- | --- |
| 8 | Permanent gear **survives death**, but manually dropping it lets others take it | Confirmed; stolen item is transferred, not cloned |
| 9 | Recovery/repair **material costs may apply** | **Open**: balancing option, not requirement |
| 10 | Maximum simultaneous Permanent equipment | **Open**; no default cap approved |
| 11 | Converted Permanent item has **same combat stats** as source | Confirmed; no automatic power increase |
| 12 | **Designated equipment only** is eligible for conversion | Confirmed; catalog not finalized |
| 13 | Permanent items **can be traded** | Confirmed; exact trade UI, fees and safeguards Open |
| 14 | Extracted gear/materials can be **withdrawn**; vault size is **upgradeable** | Confirmed; slot and cost curve Open |
| 15 | Recipes obtained through **discovery and player leveling** | Confirmed; precise levels/XP/requirements Open |
| 16 | High-tier recipes require materials from **multiple activities/sources** | Confirmed; exact drops and numbers Open |

**Non-duplication policy:** One transferable Permanent item exists at any moment: in a player's safe collection, equipped, on the ground after intentional drop, or in trade escrow. Death returns a currently owned item to its owner; an item already **manually dropped and legitimately claimed by another player** cannot return to its former owner. Ground-item expiration when unclaimed remains Open.

**Critical clarification of answer 3:** Earlier GDD versions confirmed that successfully **extracted ordinary materials and gear** live permanently in an unraidable account vault so they can pay for later special crafting. “Everything disappears; only Permanent items survive” was stated about **empty-world resets**, so the **working interpretation** is that the live island resets but already vaulted items remain saved. If the user instead wants all ordinary **previously vaulted** resources to disappear too, that would radically change the core extraction/Forge economy and needs explicit approval. This question remains **Open** rather than treated as answered.

### 34.3 Extraction, portals and return (17–24)

| Number | Owner decision | Status |
| --- | --- | --- |
| 17 | Players may move **outside** the zone during countdown; must be **inside only at the exact end** | Confirmed; small extraction area |
| 18 | Timer does not pause/reset on zone exit | Confirmed consequence of shared timer |
| 19 | Combat, healing and being hit are permitted without cancelling countdown; dead players do not qualify | Confirmed |
| 20 | Large-radius audio and visual warnings alert nearby players | Confirmed; radius/VFX Open |
| 21 | A **single timer on server** applies to an extraction event; groups/tribes can share it | Confirmed; unrelated strangers using same event Open |
| 22 | Known candidate extraction POIs; **different active subsets per server**; extremely rare portable rune gives **30-second anywhere** extraction | Confirmed; item consumption, alert radius, temporary zone and abuse protections Open |
| 23 | Central portal higher-value multiplier | **Open** — owner requested explanation; cannot select a reward type |
| 24 | Successful extraction returns players to the **separate secure lobby** | Confirmed; not the play-world pre-spawn menu |

**Important revision:** The original “remain within extraction region for the entire 120-second hold” mechanic is **replaced**. On click a fixed portal starts its own countdown; the initiating player can hide nearby or fight, heal, leave and re-enter at will. At expiry the server collects every **alive and eligible character currently inside the region** for protected animation. A character outside by even a short distance at the finish misses the event. Damage does not reset it. Each qualifying character receives their **own** idempotent vault receipt; the portal's timer belongs to the server, not one player.

**Portable rune:** Extremely scarce one-use rewards/drops can provide a fast **30-second** exit at a player-chosen location, including locations outside predetermined POIs. Exact beneficiary group size, placement conflicts, interaction with building/raid mechanics, destruction rules and no-build restrictions need future decisions; “anywhere” and 30 seconds are Confirmed.

**What question 23 means:** Imagine extracting 10 rare ore and one Legendary with a hypothetical 2× center bonus. Possible designs: **20 ore**, or **10 ore and the same Legendary plus bonus currency/experience/score**. Neither is approved. The recommendation is to reward added currency/experience/score, **not duplicate** conversion catalysts or Legendary equipment, but await the owner's choice.

### 34.4 New acceptance tests

1. Servers support a provisional capacity target of 30 and preserve live world state while populated; an empty server resets temporary world structures/resources on the next instance.
2. Dead player is ejected and same-JobId rejoin denied, while an eligible survivor may return to that server if not full; prior voluntary quit forfeiture is never undone.
3. Staff safe-update command preserves actual current holdings and gives a clear **game update / inventory saved** notification when the player resumes.
4. A full-instance crash follows recovery rather than being falsely treated as a voluntary single-player quit; item ownership cannot be duplicated.
5. Permanent gear retains baseline stats and remains owned through death; intentional drop/pickup or confirmed trade changes current owner once, with previous owner unable to reclaim it.
6. Recipe unlocks combine level progress and discoveries, allow only designated items, and use real successfully extracted materials from different sources.
7. Upgradeable vault capacity is enforced: upgrade increases capacity; insufficient room never deletes stored items.
8. Two activators at the same fixed exit create **one shared 120-second event**, not parallel client countdowns.
9. A player can move out, hide, fight and heal, and still qualify by being alive **inside at exactly 120 seconds**. A player outside at the end does not qualify regardless of prior time inside.
10. Entire parties/tribes can leave using that one timer with separate non-duplicated saved inventories.
11. Different public worlds activate different subsets of the same known extraction POIs.
12. Rare portable rune initiates an authorized **30-second** temporary extraction at a chosen location without generating extra runes or duplicated vault awards.
13. Successfully protected extraction animation is safe to disconnect and transfers to separate lobby; game does not reroute to unsafe world menu.
14. Vault wipe interpretation and center multiplier stay marked **Open** until explicitly confirmed.


## 35. Owner-approved answers 25–48 (2026-10-22)

> This chapter records **confirmed rules** from the design owner. Ambiguous or undecided mechanics remain **Open**. The gameplay and technical rules in §§4–8, 19, 21 and 32 were rewritten to match these answers. Former proposals for player magic, weapon durability, continuous extraction occupancy, respawning in the same world and mandatory siege equipment are superseded.

### 35.1 Survival, combat, healing and movement (25–33)

| # | Subject | Design-owner answer and confirmed rule | Remaining Open specifics |
| --- | --- | --- | --- |
| **25** | Survival attributes | **Health, stamina and food only**. "Gathering" means harvesting trees, ore, stone, shrubs, crops and creature materials, **not a meter**. | Food meter depletion, hunger penalty, rates |
| **26** | Attacks | **Simple click attacks** and **bow shots with slow projectiles** for launch; combat expansion undetermined | Swing speed, projectile velocity, damage, combo prospects |
| **27** | Movement | **Sprinting and crouching**; **stamina only restricts sprint duration**. | Speed, stamina regeneration, control bindings |
| **28** | Ranged gear | **Ranged weapons exist; arrows must be crafted**. Bow baseline; extra ranged archetypes not all confirmed | Arrow recipes, stack caps, projectile gravity/recovery |
| **29** | Magic | **No player magic for now**; future release possibility, not launch | Whether/when added; enemy elementals allowed |
| **30** | Medicine and food | **Medical items and potions heal instantly on use; the following animation is the cooldown**. **Food grants healing over time; taking damage partially interrupts HoT**. | Instant heal size; animation lengths; precise damage interruption amount |
| **31** | Gear wear and defenses | **Equipment lasts indefinitely**, with no equipment durability wear/breaks. Special defensive traits can be a future update. | Baseline armor mitigation; optional separate Permanent recovery cost |
| **32** | Tribal down/revive | Tribe members can be **downed for 60 seconds**. When a valid tribe member starts revival, the timer **pauses**; on cancel it **resumes from remaining time**. Non-tribe solo players **die immediately**. | Revive channel length, HP restored, finishing downed enemies, allied vs tribe-only |
| **33** | PvP and spawn | **Random spawn location anywhere on the map**; PvP enabled **everywhere**, except designated POIs with explicit safe zones | Spawn candidate validation, safe-zone list, friendly fire, spawn damage timing |

**PvP state semantics:** A living active player can be damaged inside almost any world zone, including while raiding, farming or handling extraction. Protected pre-spawn menus and post-extraction animation remain exceptions. A safe POI, if one exists, must be explicitly mapped and server-enforced; a private base/totem never creates a safe zone.

**Death outcomes:** A tribe member enters downed state on lethal damage. A valid revive may save them without triggering death/ejection. If unpaused time runs out, they die and are **kicked/sent to the separate lobby**, with no same-server return. Solo non-tribe players skip downed and go directly to death/ejection. The ordinary 10-minute world loot-body rules remain.

### 35.2 Building, tribes, takeover and farming (34–41)

| # | Subject | Design-owner answer and confirmed rule | Remaining Open specifics |
| --- | --- | --- | --- |
| **34** | Construction interaction | **Booga Booga-style** accessible building | Exact snapping, rotation and costs |
| **35** | Building objects | **Yes** to functional structures: storage, beds, workbenches, farms, traps, furnaces and core walls/floors/doors | Full launch content catalog |
| **36** | Material tiers | **Wood → stone → iron** for initial building; later tiers follow actual material additions | Structure stats and prices |
| **37** | Persistent bases and decay | Owner leaves -> **structures remain in populated public world** for takeover. **Without a nearby tribe totem, placed structures decay over time**; valid totem protects local player-built structures from natural decay. | Totem radius, decay speed, takeover/claim transfer |
| **38** | Raiding | **Any time**, including absent owners; **no specialized raid tools required**. | Damage values and raid pacing |
| **39** | Tribe rules | Maximum **8** players; invite, kick, alliances. Tribes claim **only player-built** structures, **not generated structures**. **World storage can be opened by anyone**. | Leader succession, alliance FF, access through doors and exact claim rules |
| **40** | Respawn and regroup | **No respawn in same server**. Death sends player to **lobby**, and they must **wait for their tribe to return to lobby** to play again with that tribe's expedition. | Queuing/new-world invite and session transfer interface |
| **41** | Farming | **Yes** to planting/cultivating trees and crops; may continue growing while farmer is away if public server remains active | Growth cycles, plant categories, grief/crop harvesting |

**Totem versus vault:** A tribe totem is a **structural claim/anti-decay mechanism**, not secure storage, raid immunity or a place to revive dead players. Ordinary storage is public-accessible if reachable. Server-generated structures remain world-owned and cannot be claimed.

**Takeover:** An unguarded house does not vanish just because its owner leaves. Another player/tribe may enter, use accessible inventory and potentially take control. Exact claim-transfer procedure must be designed without violating the existing public-build and no-scheduled-wipe rules. As soon as the last player leaves the world, the entire temporary world resets, regardless of totems.

### 35.3 Weighted events, mobs and bosses (42–48)

| # | Subject | Design-owner answer and confirmed rule | Remaining Open specifics |
| --- | --- | --- | --- |
| **42** | Event cadence | **Weighted event-rarity roll on server ticks**; an event **may** occur depending on the weights, not one fixed non-Guardian interval. "Non-Guardian" simply means **all events except the central Guardian boss**. | Tick interval, weights, overlap/cooldown, none outcome |
| **43** | Event alerts | **All events are publicly announced**; no unannounced rare shrubs/trees/minerals | Whether every event gets exact marker vs regional hint |
| **44** | Enemy themes | **Primitive, ancient, skeletal, elemental, evil NPC, mythological** and similar monsters | Full roster and behavior |
| **45** | Boss entry method | Three variants: **player-ritual summoned** by materials, **event-only boss**, and **structure-only boss** | Ritual recipes, spawn/despawn, reward lists |
| **46** | Boss PvP and scaling | Fully contested **PvP loot**; bosses reset by **spawn type**; scaling uses **average server/lobby player level or gear level** | Exact metric, capture window, scaling formula, reward distribution |
| **47** | Generated structures | **All three**: abandoned structures, actively NPC-defended camps and naturally generated ruins | Spawn types, raid loot amounts |
| **48** | Rare resource locations | **Random valid locations within appropriate biomes** | Min spacing, node density, biome spawn pools |

**Guardian distinction:** The original Guardian-specific cadence of approximately **15–20 minutes**, **3-minute warning**, shield-pillar encounter and **25%-HP Legendary world drop** remains in the GDD because answer 42 addresses weighted *non-Guardian* events. Any change to Guardian's dedicated cadence must be explicitly approved.

**Boss combat scaling:** Average **player level** or **gear level** from active server population are candidate inputs. A blended score is an alternate **proposal**. Select which to use and define bounds without enabling manipulative “remove armor / connect alts” difficulty exploits.

### 35.4 Acceptance and regression matrix — P0/P1

1. On Play, choose a validated random map spawn. Do not force starting Outer Rim. PvP is active except for explicit server-enforced safe POIs.
2. Only Health, Food and Stamina exist as launch survival meters. Bow shots/melee/harvesting do not use stamina; sprint does.
3. Click melee deals bounded server-authoritative damage; bows produce visibly slow server-validated projectiles and consume **crafted arrows** without duplication.
4. No player-cast magic/elemental combat, player shields, gear durability wear or dedicated thirst/temperature system is loaded in launch content.
5. First eligible use of a medical consumable applies HP immediately and deducts exactly one item, then starts animation cooldown. Repeat input/RemoteEvent during cooldown does not grant another heal.
6. Food applies a timed HoT. On damage, remaining healing is partially interrupted according to an explicitly configured rule and never applies duplicate/full-health overcap.
7. A non-tribe solo player takes lethal damage and is dead immediately with world corpse and lobby ejection.
8. A qualifying tribe member (maximum tribe 8) becomes downed with exactly **60 seconds remaining**. Starting valid revive pauses countdown; cancellation resumes original remainder; multiple invalid revivers cannot freeze timer indefinitely.
9. Once unpaused downed time expires, create one 10-minute lootable body, eject to lobby and deny re-entry to same live server. Teammates must regroup in lobby for the next shared run.
10. Tribe invites, kicks and alliances obey authoritative membership; no one can add ninth member. Server-generated structures are unclaimable.
11. A Booga Booga-style player structure may be placed and upgraded wood → stone → iron, with damage allowed from ordinary player gear at any time.
12. Totem-covered player structures avoid **natural decay** but may still be raided. Outside totem radius, structural decay advances while world is live. Owner departure does not despawn house.
13. Any active player physically reaching a storage box can open it without owner/tribe credentials; walls may require raiding.
14. Farms and planted trees progress while the owner is away, provided server remains active; world-empty wipe clears all world farms/structures.
15. Event tick selects no event or a weighted eligible event; all actual spawns receive server-wide announcement. Resource nodes randomize **within appropriate biome** rather than deterministic fixed coordinates.
16. Ritual items trigger boss spawns only in validated contexts; event bosses appear only through weighted event rules; structure bosses are tied to valid generated structures.
17. Boss difficulty sampling uses a configured average level/gear value resistant to manipulation; NPC deaths/drop eligibility remain PvP-contested.
18. Guardian special events keep their dedicated legacy design unless deliberately modified by a later owner decision.
19. Secure vault, transferable Permanent item identity, maintenance recovery, shared 120-second extraction, rare portable 30-second rune and protected pre-spawn Play gate must not regress.

### 35.5 Decisions still open after questions 25–48

**High priority for implementation:** (1) amount/duration of food HoT partially cancelled by damage, (2) medical cooldown animation duration, (3) revive hold time and whether active attackers can finish a downed enemy, (4) attack/projectile speeds and ranged archetypes beyond bows, (5) totem radius/decay speed/claim transfer for abandoned homes, (6) exact designated PvP-safe POIs, (7) event weight tables, tick period and concurrency cap, (8) level-vs-gear boss scaling and ritual recipe specifics, (9) details of protected dropped Permanent items and recovery costs, (10) central portal bonus type from question 23 and secure-vault reset interpretation from question 3.

**Next owner questions:** 49–60 on currency, trading, item rarity, XP/progression details, public-world rewards, economy, graphics, camera, onboarding and monetization.


## 36. Design change log

| Revision | Date | Change |
| --- | --- | --- |
| **0.1** | 2026-10-21 | Created Flintborn GDD from the original primitive extraction handoff; recorded primitive-fantasy/no-firearms direction; added proposed systems, technical guardrails, vertical slice and decision backlog. |
| **0.2** | 2026-10-21 | Added confirmed extracted-material special crafting and expensive eligible-item Permanent conversion; expanded item taxonomy, Forge design, working death/recovery policy, resource/recipe catalog, cross-run economy and player journeys. Further implementation details in §22–28. |
| **0.3** | 2026-10-21 | Removed player-usable shields and added consumable healing progression, recipes and PvP interruption rules; kept Guardian shield-pillar boss mechanics. |
| **0.4** | 2026-10-21 | Confirmed 120-second telegraphed extraction hold, invulnerable and disconnect-safe animation, 600-second lootable bodies after active exit, admin update preservation, rare events, accessible building and diverse playstyle incentives. |
| **0.5** | 2026-10-21 | Established the mandatory **protected play-world loading/main menu** with explicit Play-to-spawn risk activation. Teleport, loading, pre-spawn kick, and failed admission cannot forfeit items. Added full state machine, recovery flows, detailed QA and cross-references in §29–33. |
| **0.6** | 2026-10-21 | Recorded answers 1–24: 30-player world target, empty-server reset, same-world rejoin/death kick, crash/update recovery, transferable same-stat Permanent items, vault upgrades and levels, server-shared 120-second end-only extraction, rare portable 30-second anywhere rune, and lobby return. Clarified unresolved reset-vault and payout semantics. |
| **0.7** | 2026-10-22 | Confirmed questions 25–48: health/stamina/food only; click melee and craft-arrow slow bows; sprint/crouch, no player magic or equipment wear; instant medical healing with post-use animation cooldown, food HoT partially interrupted by damage; 60-second pauseable tribe revives, solo immediate death and lobby ejection; random map spawns, PvP with designated safe-POI exceptions; 8-member tribes, totem-based structure decay, public storage, any-time normal-tool raids, wood/stone/iron, persistent-in-live-world farming/takeovers; weighted publicly announced events, biome-random rare nodes, three boss sources and level/gear-based scaling. Added §35 and revised affected launch/QA/technical sections. |

---

**Working principle:** Flintborn combines **protected pre-spawn Play**, death-triggered lobby ejection, random map spawning, **open PvP** with explicitly safe POIs, primitive click melee and slow crafted-arrow bows, **health/food/sprint-only stamina**, instant medicine and food HoT, **60-second tribe revives**, 8-member tribes, Booga Booga-style totem-protected but always-raidable bases, weighted publicly announced rare events, server-shared 120-second extraction (or rare 30-second anywhere rune), secure vault crafting and transferable death-retained Permanent gear. **No playable magic, firearms, shields or equipment durability wear at launch.** Proposed rates, metrics and future features require approval.
