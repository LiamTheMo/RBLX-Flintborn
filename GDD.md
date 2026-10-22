# Flintborn — Game Design Document

> **Status:** Comprehensive pre-production specification (not implemented)  
> **Design revision:** 0.4  
> **Last updated:** 2026-10-21  
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

**New confirmed direction (2026-10-21):** Resources carried safely through an extraction can fund special crafting outside an island run. Some eligible extracted items can be transformed into an expensive **Permanent** item type using hard-to-get ingredients. The transformation capability is Confirmed; exact death, transfer, recovery, slot, durability and trading rules are Open. All numerical costs below are illustrative hypotheses.

**Confirmed combat clarification (2026-10-21):** No player-usable shields, shield recipes or guard-blocking mechanics. Healing items provide active recovery. The Guardian's Phase I shield pillars are unchanged.

**Confirmed public-world/extraction decisions (2026-10-21):** Normal leave outside lobby creates an in-world body, forfeits carried ordinary items, and despawns after 10 minutes; privileged admin update kick preserves items. Extraction emits audio/visual cues, takes 120 seconds within the required area, and grants invulnerability and disconnect safety once the animation begins. More events (rare flora, materials, mobs, bosses, raidable structures, meteors), Booga Booga-style building and sustained public-world playstyle rewards are intended. See §29–33.

This GDD is the source of truth for gameplay intent. Engineering contracts, tuning tables, art briefs, and implementation tasks should reference it rather than silently changing its rules.

### Document navigation

- **Gameplay foundation:** [Core loop](#2-core-run-structure), [Shattered Crater map](#3-world--the-shattered-crater), [equipment](#4-primitive-fantasy-progression), [combat](#5-combat-and-pvp), [bases and raids](#6-building-fobs-and-raiding).
- **Contested objectives:** [Server-wide events](#7-dynamic-server-wide-events), [Mega-Boss](#8-mega-boss--the-guardian-awakening), [extraction and vault](#9-extraction-and-permanent-vault).
- **Long-term progression:** [Special crafting / Permanent rules](#15-cross-run-special-crafting-and-the-permanent-item-class), [Ancestral Forge](#16-the-ancestral-forge-crafting-outside-the-run), [Permanent gear policy](#17-permanent-gear-operational-rules), [material sources](#18-resource-tiers-economy-and-acquisition-sources), [recipe examples](#19-special-recipe-examples--proposed-balancing-placeholders).
- **Implementation:** [Inventory state transitions](#22-detailed-inventory-extraction-and-death-state-transitions), [Roblox architecture](#23-proposed-roblox-luau-services-and-persistence-model), [threat model](#24-economy-abuse-cases-and-anti-duplication-tests), [UX requirements](#25-ux-specifications-and-interface-inventory), [tuning plan](#26-quantitative-tuning-and-live-analytics-plan), [QA](#27-detailed-verification-matrix-and-qa-plan), [production phases](#28-production-milestones-and-documentation-maintenance).

**Navigation links follow GitHub Markdown heading anchors; section numbers are stable only within this revision.**

## 1. High concept

**Pitch:** Spawn at the edge of a fractured island with almost nothing. Gather, craft, establish a raidable tribal stronghold, and venture deeper to fight rival players and ancient monsters for enchanted loot. Carry your prizes to a dangerous extraction rune to secure them in a permanent vault. Fail, and others take what you carried.

**Unique proposition:** The strategic tension of an extraction game **without firearms**: stone and metal arms, spears, bows, tribal equipment, enchanted blades, and elemental magic. Combat, transport, raiding, and map control all happen in a primitive-fantasy setting.

**Intended player fantasy:** “I started with stone tools, fought over a legendary relic, escaped a rival tribe, and brought it home.”

### 1.1 Design pillars — Confirmed

1. **Risk is voluntary but meaningful.** Safer outer routes provide a viable exit; deeper objectives pay more and attract other players.
2. **Ordinary loot is at risk.** On death or ordinary departure outside the lobby, a lootable body remains in the server for **10 minutes**, with any unclaimed items despawning at expiry. The player loses carried ordinary loot. The protected extraction animation and authorized game-update kicks are exceptions (§29–30); Permanent gear recovery is still Open (§15–17).
3. **Survival and crafting matter.** Players harvest, craft weapons and armor, build forward bases, and manage resources in the field.
4. **The world creates diverse PvPvE opportunities.** Meteors, rare shrubs/trees and material nodes, raidable structures, unusual mob and boss spawns, caches and the Guardian move players across the island.
5. **Primitive fantasy, not military extraction.** No firearms or player-usable shields at any tier. Magic supplements primitive weapons and consumable healing.
6. **Multiple paths to value.** Hunting, farming, building, ambushing, events and base raiding are all legitimate playstyles. Engaged players who remain in the public world can earn activity-based benefits without promoting AFK waiting.

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
7. **Build long-term power:** Spend extracted ingredients on special recipes or save for costly Permanent conversions (confirmed mechanic; specific recipes proposed).
8. **Continue or extract:** Remain in a public world to pursue farming/building/PvP, or complete a telegraphed **120-second in-area extraction hold** to enter the protected animation. Simply leaving the world forfeits ordinary carried gear.

### 2.2 Loss and persistence contract

| Domain | Established behavior | Design status |
| --- | --- | --- |
| On-person inventory | Drops on death or ordinary non-lobby departure with lootable **10-minute body** | **Confirmed** |
| Lobby departure | Can safely leave from the lobby | **Confirmed** |
| Protected extraction | Requires **120 seconds inside designated area** and audio/visual cues; animation then grants invulnerability and disconnect safety | **Confirmed** |
| Administrator maintenance kick | Safe removal for game updates without losing held items | **Confirmed**; escrow details Proposed |
| Successfully extracted loot | Secure in a permanent, unraidable out-of-game vault | **Confirmed** |
| Extracted crafting resources | Feed special recipes and costly permanent conversions | **Confirmed** |
| Converted Permanent equipment | Conversion is available; death, recovery and deployment rules are not yet finalized | **Confirmed capability / Open mechanics** |
| In-world base storage | Can be looted if opposing players raid the base | **Confirmed** |
| Gear withdrawn from vault for deployment | Exact redeployment and loss rules | **Open** |
| Player progress (recipes, cosmetics, reputation, etc.) | Whether and what persists | **Open** |
| Bases across sessions/server shutdowns | Session-only, timed-wipe, or persistent-world model | **Open** |
| Public world playstyles | Benefits for engaged PvPers, base-builders, farmers and other active playstyles | **Confirmed direction**; specific rewards Proposed |
| Disconnects during combat/extraction | Ordinary non-lobby disconnect leaves a lootable body; once protected extraction animation starts, disconnect is safe | **Confirmed**; crash reconciliation Open |

**Working default:** Ordinary vaulted items become unsecured after deployment. Converted Permanent equipment may retain ownership subject to still-open rules. **Confirmed:** A normal non-lobby departure creates a lootable 10-minute body, not a safe logout. Animation-start protection and authorized update kicks are exceptions, and must be implemented without duplication (§29–30).

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

**Confirmed:** Progression starts with stone/wood and expands to metal, tribal gear, enchanted arms, elemental magic and **finite healing consumables**. **No firearms or player-usable shields.**

### 4.1 Candidate gear ladder — Proposed, subject to balance

| Stage | Theme | Example materials | Example equipment | Acquisition emphasis |
| --- | --- | --- | --- | --- |
| Starter | Wood, stone, fiber | Wood, stone, vines, hide | Stone axe, wooden spear, sling, rough hide tunic | Outer Rim gathering |
| Early | Flint and bone | Flint, bone, leather | Flint knife, reinforced club, shortbow, herbal bandage | Crafting and low-tier enemies |
| Mid | Worked metals | Copper/bronze/iron (exact metallurgy TBD) | Metal spear, sword, axe, chain or scale armor | Deeper mining and workshops |
| Advanced | Volcanic and rare minerals | Obsidian, jade, special beast components | Obsidian blade, jade-treated armor, advanced restorative tonic | Inner Ring and alpha encounters |
| Endgame | Elemental / relic-infused | Abyssal meteor material, charged cores, boss relics | Ember spear, storm bow, runic armor, legendary relic | Broadcast events, raids, Mega-Boss |

**Important:** Stage labels are illustrative, **not** five confirmed tiers. Resource Crash explicitly uses a rare **Tier-5** resource; the complete item-tier taxonomy is **Open**.

### 4.2 Initial item families — Proposed

| Category | Examples | Design role |
| --- | --- | --- |
| Gathering | Stone axe, pickaxe, reinforced pick, sickle | Resource acquisition and contested harvest efficiency |
| Melee | Spear, club, knife, sword, war axe, hammer | Different reach, tempo, stagger, armor penetration |
| Ranged | Sling, bow, longbow, throwing spear, javelin | Mid-range pressure with recoverable/consumable ammunition |
| Armor | Hide clothing, bone-mail, metal and runic armor | Passive resistance at durability, weight and mobility cost; **no shields** |
| Healing consumables | Fiber bandage, herbal poultice, restorative tonic, antidote | Finite health recovery/selected ailment cleansing; tactical application windows and costs |
| Utility | Torch, rope, traps, herbal satchel, smoke bundle | Survival, stealth, escape, siege and counterplay |
| Magic | Ember, frost, shock, nature/earth imbues | Status effects and tactical utility, never gun-like firearms |
| Construction | Walls, foundations, roofs, doors, gates, storage, workstations | Temporary strongholds and protected resource staging |
| Siege | Primitive breaching charges, fire pots, rams (TBD) | Counterplay to fortifications with clear costs and warning |

### 4.3 Enchantment principles — Proposed

- **Ember:** Damage-over-time/burning; countered by cleansing/water or positioning.
- **Frost:** Slow or brief control; control durations tightly capped in PvP.
- **Storm:** Chain effects and brief attack interruption with explicit target limits, not shield pressure.
- **Earth/Nature:** Nature-based restorative items, cleansing or situational terrain/poison effects; no magical shield barriers.
- Enchanted power should have cooldown, durability, stamina/mana cost, charge limit, or a comparable tradeoff.
- Make all status effects legible on Roblox-scale characters and mobile screens.
- Rare enchantments modify how primitive weapons are used; they should not turn combat into sustained automatic projectile fire.

### 4.4 Crafting questions — Open

**Confirmed:** Extracted materials are used in secure-hub special crafting and in expensive eligible-item Permanent conversions. **Open:** Recipe discovery, durability and repair, encumbrance, stack sizes, ammunition recovery, magic catalysts, Permanent equipment binding, cooldown, trade and deployment specifics. See §15–28.

### 4.5 Healing items and special recipes — Confirmed direction / Proposed specifics

**Confirmed:** Player-usable shields do not exist. Healing items provide health recovery; armor, evasion, cover and movement also contribute to survival. Boss shield pillars in §8 are an **enemy invulnerability mechanic** and unaffected by this rule.

| Progression stage | Sample item | Candidate materials / source | Function (proposed) |
| --- | --- | --- | --- |
| Starter | **Fiber Bandage** | Outer Rim fiber, basic herbs | Small recovery, easy field craft |
| Early | **Herbal Poultice** | Herbs, clean cloth, resin | Gradual healing after a vulnerable application |
| Mid | **Restorative Tonic** | Rare plants, purified mineral catalyst | More efficient single-use recovery |
| Advanced | **Antidote Draught** | Jungle flora, beast glands | Removes specified poison/burning effects, limited or no direct heal |
| High rarity | **Guardian Renewal Draught** | Securely extracted Guardian/Alpha reagents | Expensive single-use emergency heal/cleanse; never unlimited |

**Open:** Actual heal amount, use duration, speed penalty, stack sizes, cooldown, whether damage interrupts, cleanse rules and whether healing can occur during portal activation. Names and numbers above are design examples. Higher-tier special healing recipes can use **extracted materials** at the Ancestral Forge; healing stacks brought into a run remain vulnerable, drop on death and **cannot be made Permanent**, avoiding infinite free healing.

## 5. Combat and PvP

### 5.1 Intended combat identity — Confirmed / Proposed

- **Confirmed:** Combat uses primitive melee, bows, thrown weapons, armor, elemental effects and **healing consumables**, without player-usable shields; encounters mix PvE and PvP.
- **Proposed:** Readable melee arcs, attack commitment and recovery, sprint/dodge or sidestep movement, and distinct reach. No shield blocking, parrying or guard-meter system.
- **Proposed:** Skill and positioning should matter even when equipment tiers differ. High-tier gear gives advantage, not unconditional wins.
- **Confirmed:** **Healing items** replace usable shields as the active recovery option; armor, cover, spacing and evasion remain relevant.
- **Proposed:** Armor has mobility/stamina tradeoffs; healing exposes a vulnerable application window instead of granting invulnerability.

### 5.2 Tribes and social systems — Open

Tribe size cap, friendly fire, invitations, permissions, loot rights, tribe base authorization, alliance rules, betrayal penalties (if any), and sharing rewards. Avoid designing core events assuming all players are in organized groups.

### 5.3 Fair-play requirements — Proposed

- Server-authoritative damage, health, healing consume/cooldowns, interruption, loot ownership and drops, crafting costs, durability, building, event rewards and extraction.
- Validate attack distance, timings, rate limits, line-of-sight where relevant, inventory changes and tool provenance.
- Design anti-spawn-camp protections without creating exploitable invulnerability near valuable objectives.
- Offer solo players stealth, speed, traps or alternate extraction paths rather than requiring a large tribe.

### 5.4 Healing combat contract — Proposed implementation

1. Alive player selects a healing item; quick slot shows stack count, expected recovery, animation and use window.
2. Client requests to start use with item/slot and operation nonce. **Server** checks ownership, remaining stack, cooldown, health state and eligibility.
3. Player performs a clear treatment/drinking animation, remaining vulnerable; a proposed slow or movement restriction creates a tactical choice.
4. Damage, sprinting, weapon switching or leaving the allowed state **may interrupt** the attempt; exact interruption conditions remain Open.
5. On validated completion, server deducts **exactly one** unit, heals up to max health or applies its cleanse. Cancelled use must not grant health or consume materials unless a published partial-use rule says otherwise.
6. Server publishes health/stack delta. Repeated remotes and disconnects cannot apply multiple heals or consume repeatedly.

**Balance constraints:** No equipable shield, guard meter, free temporary barrier, auto-regeneration exploit, full-HP panic button or bottomless consumable. Limit repeated sustain by inventory weight/stack cap, application time and shared cooldown. Effective healing rates must allow committed enemies to finish fights; solo players should still access affordable early healing. Enchantments may modify individual crafted healing effects, never create a reusable unlimited-health source.

**QA:** Test damage interruption, concurrent use, latency, repeated remotes, negative stack attempts, healing at max health, death while channeling, zero-stack requests, use during extraction, controller/touch accessibility, trade/drop interactions and no Permanent healing-stacks path. Mark precise timings and values Open until playtest.

## 6. Building, FOBs, and raiding

**Confirmed:** Building is approachable and **Booga Booga-like**, using primitive placeable structures, modular foundations/walls, crafting benches and storage. Bases remain raidable, from small beach shelters to stone strongholds. Precise placement and upgrade proposals appear in §32.

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
- **Proposed:** Access controls for tribe-owned doors/storage, bounded structures/physics, rapid mobile-friendly placement, rotation/snap/repair and no-build protection around contested objectives.
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
- Activating an extraction rune starts an **exact 2-minute / 120-second countdown** while the player remains in the specified extraction area. The attempt sends **audible and visual cues** to other players so it can be contested.
- The player is vulnerable during the countdown. **Once the extraction animation begins**, the player is invulnerable, safe from loot theft and safe to disconnect, even if the animation is not finished.
- Leaving before the protected animation (without an authorized maintenance exemption) counts as an ordinary non-lobby departure, leaving a lootable body for 10 minutes.
- Extraction transfers eligible items into a **persistent, unraidable vault** outside the live island run.
- Outer hidden Minor Extraction Runes offer a lower-risk escape with **modest value multipliers**.
- The Center Crater's main Permanent Extraction Portal offers the **highest value multiplier**.
- Death before successful extraction drops carried items for looting.
- All extraction sites have **50-meter no-build auras**.
- Carriers of event-exclusive resources/legendary boss gear reveal themselves through embers, shadow trails or similar visible particles (**Burden of Wealth**).

### 9.2 Confirmed timing and proposed server implementation

1. Player activates portal while alive and in the designated area; server validates the attempt and broadcasts **audio/visual extraction cues**.
2. Server starts a **120-second** countdown; player must remain in the specified area throughout. Normal PvP and damage remain possible. Whether taking damage alone interrupts the countdown is **Open**.
3. If the player leaves the area or dies before completion, the attempt fails. **Proposed:** leaving the boundary cancels and requires full restart (rather than pausing). Ordinary departure during this stage creates a lootable body.
4. After 120 valid seconds, server authorizes **ExtractionAnimationStarted**, locks the exact carried-item snapshot, and grants **invulnerability and safe disconnect immediately upon animation start**. Other players can no longer loot that snapshot.
5. Server establishes a recoverable extraction receipt/entitlement as part of the protected transition; vault persistence may finish after animation or player disconnect, but the locked loot must never be forfeited or duplicated.
6. After verified commit, show the secure-vault receipt and return to protected lobby. A pending backend write must be shown as pending, not falsely settled.

**Critical boundary:** Protection begins when the **server-authorized animation** begins, not when the animation ends. A client-only visual effect cannot mint items or assert protected state.

**Proposed anti-camping protections:** Multiple minor extraction locations and readable approach paths; **the 120-second hold stays risky** and the post-hold animation is invulnerable. The marked hold area needs clear world geometry/UI.

### 9.3 Value multiplier guardrail — Proposed

Multipliers should apply to **valuation/payout**, not produce copies of unique loot or quest-critical crafting materials. Define a stable base value and a bonus per portal type, then tune with data. Rare items should remain rare after extraction.

### 9.4 Vault/transaction guardrail — Proposed

Treat extraction hold, protected animation, death, ordinary leave, maintenance kick and item pickup as competing **server-authoritative** transitions. Lock exact item IDs at animation start and create a recoverable receipt before allowing safe disconnect. The server decides the protected animation state; a client-side animation alone is not proof of successful extraction.

### 9.5 Extraction decisions — Open

**Confirmed:** 120-second stay-in-zone hold, audio/visual warning to other players, animation-start invulnerability/disconnect safety, 10-minute loot bodies on ordinary departure, maintenance kicks preserving holdings, and extracted materials for special crafts. **Open:** Exact area geometry, exit reset mechanics, damage interruption, alert range, simultaneous attempts, portal availability, value multipliers, party rules, lobby return and crash recovery.

## 10. Economy, stakes and balancing

### 10.1 Three economic locations

| Location | Risk profile | Meaning |
| --- | --- | --- |
| **Carried inventory** | Highest until protected extraction | Death or ordinary non-lobby departure leaves lootable body for 10 minutes; animation-start locks items against loss |
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

- **Lobby / vault:** Vault inventory, loadout/deployment decisions, run results and risk explanation.
- **In-world HUD:** Health, stamina, equipped weapon, healing quick slots/use timer, inventory burden, compass/minimap, extraction and event markers.
- **Crafting/building:** Recipe requirements, snap previews, construction restrictions and durability.
- **Event UI:** Clear announcement, direction/search radius, beacon color and event time state.
- **Boss UI:** Three-phase status, 3-minute warning, pillar progress and readable 25% phase transition.
- **Extraction UI:** Site name, projected bonus, **120-second hold timer and boundary**, audible/visual alert to nearby rivals, vulnerability during hold, explicit animation-start protection and verified receipt.
- **Death UI:** Clear loss summary plus next-run action.

Make major cues redundant across color, icon, words and sound. Provide comfortable interactions on Roblox mobile, desktop and controller; avoid interactions that require precise cursor control.

## 12. Technical direction (architecture proposal, not implementation)

This section records intent so later Luau/Rojo architecture serves the game rules; there is **no game code in the repository yet**.

### 12.1 Authority boundaries

- **Client:** Input, animations, local UI, prediction, non-authoritative audiovisual effects. Client never decides what was securely extracted, what is bound, or whether crafting succeeded.
- **Server:** Damage and status, material grants, inventory ownership, loot drops, structure placement/health, crafting, events, boss state, portal eligibility, extraction transactions, vault writes.
- **Shared definitions:** Typed item catalog, tags, combat/status definitions, event/biome IDs, validated protocol shapes and tunable balance values.

### 12.2 Candidate service boundaries

`SessionService` (deploy/reconnect), `InventoryService` (items, drops, transfer), `VaultService` (persistent stores), `ExtractionService` (portal state and atomic handoff), `ResourceService`, `CraftingService`, `BuildingService`, `CombatService`, `TribeService`, `EventDirector`, `BossService`, and `WorldRulesService`.

**Important invariants for code review:**

1. No client-created rare items or client-declared combat hits without server validation.
2. No player-built structure can exist within an extraction no-build zone.
3. An item cannot simultaneously exist as world loot, carried inventory, vault inventory, Forge-reserved input and account-owned Permanent equipment. A deployed bound manifestation references one canonical record; it is never a second tradable item.
4. Extraction **and Permanent conversion** have explicit persisted success/failure states; retries cannot duplicate items or double-charge ingredients.
5. A valid **120-second in-zone hold** gates protected animation; invulnerability and disconnect safety begin at server-authorized animation start with an immutable inventory snapshot.
6. Ordinary departure outside lobby creates a single lootable body expiring after 600 seconds; authorized maintenance removal preserves holdings without auto-extraction.
7. Boss Legendary release at 25% occurs at most once per encounter.
8. Only `main` may trigger production publishing workflows; development branches never publish.

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
| **A. Gather/craft** | Outer-rim test arena; wood/stone/herbs; axe/spear; inventory and bandage | A new player can gather, craft a weapon and healing item, and use both without admin commands |
| **B. Fight/lose** | Primitive combat, healing, ordinary non-lobby leave, body looting | Body persists for 10 minutes; death and ordinary leave forfeit items exactly once |
| **C. Extract/secure** | One rune; audio/visual alarm; **120-second hold** then protected extraction animation and vault | Defend inside region; animation makes invulnerable and disconnect-safe; no duplicates or premature protection |
| **C2. Permanent Forge prototype** | One ordinary special recipe and one eligible source-to-Permanent conversion | Ingredients charged once, converted source retired, owned Permanent record survives test death/rejoin, other carried loot still drops |
| **D. Build/raid** | Accessible Booga Booga-like construction, foundations/walls/doors/stash, raid damage | Quick placement and raidable storage, with protected extraction auras |
| **E. Contest** | Rare herb/tree, mob, meteor or raidable structure event; beacons and rare carrier | Varied activities are contestable; valuable rewards still need extraction |
| **F. Center encounter** | Boss prototype with pillars, attack cycle, 25% drop, central portal | Mid-fight Legendary appears once; boss structures cannot cheese; relic must be extracted |

### 13.1 Explicit non-goals for the first slice

Full island art, every biome, elaborate weather, large equipment catalog, trading/auction house, polished monetization, cross-server base persistence, advanced tribe diplomacy, and every elemental school. The minimal Forge conversion proof **is included** in the first playable slice, as a core loop.

### 13.2 Documentation validation checklist

- [x] Flintborn primitive fantasy equipment explicitly excludes **firearms and player shields**; healing uses finite items.
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
| **P0** | Run/session model, vault withdrawal, Permanent ownership after death and what persists between servers | Inventory authority, saved data, base lifecycle, player stakes |
| **P0** | Permanent conversion eligibility, irreversible ingredient usage, binding/slot/recovery | Avoid trivial risk bypass and item-duplication pathways |
| **P0** | Death, disconnect, reconnect and combat-logging policy | Exploit resistance and player trust |
| **P0** | Portal activation/interrupt logic and multiplier definition | Core extraction risk and economy correctness |
| **P0** | Server population, solo/tribe sizes, and PvP rules | Map size, reward access, balance and performance |
| **P1** | Weapons, dodge/movement, healing timings and interruptions, hit detection, magic resources | Combat feel and network design without shields/guard meters |
| **P1** | Build/raid costs, protected zones, raid time and structure upkeep | Base fairness and grief prevention |
| **P1** | Event schedule/loot tables, boss loot distribution and reset logic | Server pacing and endgame |
| **P1** | Biomes, distances, terrain elevation, portals and spawn points | World prototyping and movement |
| **P1** | Special Forge recipe unlocks, rare source costs, repair/durability and material sinks | Core cross-run progression and balance |
| **P2** | Currency, optional trading and cosmetic mastery | Long-term economic depth |
| **P2** | UI art direction, onboarding and optional cosmetics | Presentation and retention |

## 15. Cross-run special crafting and the Permanent item class

> **Confirmed:** The player can spend successfully extracted materials to craft special items. Some eligible items brought back alive can be converted to a **Permanent** type by spending scarce, expensive ingredients. This is a central cross-run progression pillar.
>
> **Working default — awaiting approval:** Permanent means durable *account ownership* of one converted gear instance through ordinary death, raid and island wipes. A deployed manifestation disappears on death and returns to the owner's protected armory with a repair/recovery cost. This interpretation is proposed, not yet a confirmed specification.

### 15.1 The three interlocking loops

1. **Moment-to-moment:** Gather stone, wood, flora, bone and ore; fight with weapons and elemental magic; build and raid tactical shelters; collect unsecured loot.
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
| Permanent converted item | Single eligible vaulted source + conversion recipe | Bound manifestation, limited slot | Manifestation vanishes; owned original survives (**Proposed**) | Protected account armory and recovery |
| Recipe knowledge | Earned milestones / discoveries | No physical item | Persists (**Proposed**) | Unlocks future recipes |

**Vocabulary requirement:** "Secured" or "Vaulted" means safely stored outside a run. "Permanent" describes a specific conversion class. An item is not Permanent just because it is in persistent storage.

### 15.3 Eligibility and source consumption — Proposed

- A Permanent conversion targets a specific, uniquely identified **extracted gear instance**, not an abstract catalog item or arbitrary stack.
- Eligible item families initially include weapons, select armor and a restricted set of tools. Exclude raw materials, currency, siege charges, structures, ammunition, potions, vault keys and anything creating limitless economic output.
- The source item must be owned by the player, present in a secure vault, unlocked for the chosen recipe, not currently equipped in another active session and not already bound.
- Converting **transforms/consumes** the source instance; it does not create both an ordinary tradeable source and a new Permanent copy.
- Source item attributes (quality, rarity roll, enchantment, crafted name) can be preserved as a defined snapshot if eligible; never claim affix preservation without recipe specification.
- No client can submit a chosen output rarity, free ingredient amounts, owner ID or arbitrary "Permanent" flag.
- The confirmed 25%-HP boss Legendary remains ordinary world loot until a player takes it to a rune and extracts. It cannot be made Permanent instantly in the crater.

### 15.4 Alternative interpretations still open

| Model | Ownership after death | Strength | Risk |
| --- | --- | --- | --- |
| **Bound gear + recovery (Working default)** | Retained by account | Earned, tangible, reliable long-term reward | Strong persistent player advantage must be capped |
| **Permanent blueprint** | Blueprint retained, gear rebuilt for a smaller cost | Strong replenishment sink | Can feel misleading if called Permanent |
| **Permanent cosmetic variant** | Appearance retained, ordinary gear still lost | High competitive fairness | Too weak to fulfill "Permanent item" ambition |
| Infinite spawnable copies | Unlimited copies | None | **Rejected proposal:** trivial duplication / economy collapse |

Do not select an option silently. The first row is an internally consistent working specification, not design-owner approval.

## 16. The Ancestral Forge: crafting outside the run

### 16.1 Two crafting domains

| Characteristic | Island field crafting | Secure Ancestral Forge |
| --- | --- | --- |
| Place | Island workbench/backpack | Protected lobby/hub or dedicated secure menu |
| Inputs | Live at-risk backpack / raidable station stock | Successfully extracted resources and vaulted gear only |
| Outputs | Field tools, armor, arrows, structures, raiding equipment | Rare special gear, enchantments, conversion reagents, Permanent gear |
| Conflict | Vulnerable to PvP, raids, weather and events | Not raid-able, but all writes server-authoritative |
| Persistence | Crafted item must still be extracted | Committed output stays in vault/armory until deployed |
| Main purpose | Survive next minutes | Grow player account over many expeditions |

The hub location and station names are **Proposed**, not mandated. A single Roblox place with distinct panels is acceptable if it reduces loading and engineering scope.

### 16.2 Proposed stations and recipe categories

- **Stonecarver's Table:** Refined flint, bone, resin and early special tools; introductory secure-crafting tutorial.
- **Tribal Smithy:** Iron, obsidian, blades, wearable armor and repairs (**no shields**).
- **Rune Altar:** Charged cores, imbuements, restorative elixirs, antidotes and elemental resistance, never protective barriers.
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
- Rare enchantments modify spears, bows, axes, clubs and armor; nature magic can modify **single-use** healing items. No guns or automatic firearm analogues.
- Recipe discovery is achievement-based or material-discovery-based, with clear reveal paths. Avoid forcing players to consult external guides.
- Multiple viable weapon archetypes prevent a single mandatory optimal Permanent item.
- Crafts that consume an item must use a unique instance ID; stacks use bounded positive integers and no fractional duplication.
- Recipe versions are immutable for active transactions so a live balance patch cannot alter an operation halfway through.

## 17. Permanent gear operational rules

### 17.1 Bound armory / manifestation — Working default

- **Canonical record:** Permanent gear exists once in a protected account armory; it owns a fixed ID, quality, permitted enchantments, durability and provenance.
- **Manifestation:** When a player deploys, server creates a temporary bound representation of the canonical record. The representation is not a tradeable second item.
- **Death:** The active copy vanishes and yields no transferable loot; regular backpack and ordinary equipped gear still drop. Permanent ownership enters **Recovery Needed**.
- **Recovery:** The player pays a lesser repair/rearm resource sink or observes a cooldown at the hub; exact delay and materials remain Open.
- **Withdraw/drop/trade:** Player can unequip the bound record to the armory, but cannot trade, drop, store in a raidable base or hand it to a different account.
- **Disconnect:** Combat logging cannot bypass active-run death. Bound recovery follows the server-owned outcome, not client disconnect timing.
- **Persistence:** Island server closure and scheduled base wipes never erase verified armory ownership.
- **Double deployment:** One bound item cannot be active in two servers at once. Equip/deploy requires a profile/session lease.
- **Repair insolvency:** Item remains owned even if unusable until repair; it must not be permanently deleted for insufficient materials.

### 17.2 Hard boundaries for balance — Proposed

- Start with **one bound weapon OR one bound armor piece** deployable per run. More slots require testing, not early monetization.
- Temporary high-risk Legendary gear may have stronger peak stats than a safer bound counterpart; earned long-term equipment must not invalidate event risk.
- Permanent tools cannot passively duplicate mining outputs or bypass resource/raid permissions.
- Bound weapons still pay stamina, draw time, arrow/ammo consumption and enchantment charges. Firearms remain excluded.
- Add optional wear and repair rather than a no-cost infinite-use weapon. All sinks should be visible before conversion.
- Cap crowd-control durations, automatic status procs and stacked elemental synergies; PvP must retain readable defenses.
- Bound items still occupy carry/equip slots and have normal weight/mobility tradeoffs.
- Rare-carrying glow and extraction risk apply to **new event loot** even when carrier uses permanent weapons.
- Neither the main crater portal nor any minor rune can grant free Permanent status as a multiplier.

### 17.3 Approval questions — P0

**Before code:** Is account-retained bound gear on death correct, or should the account receive only a rebuild blueprint? Is Permanent transferable? What exact recovery cost/cooldown applies? What item families can be Permanent? How many bound slots per run? Does use degrade durability? Can a converted Legendary keep its affixes? No answer is presumed approved beyond the user's confirmed conversion concept.

## 18. Resource tiers, economy and acquisition sources

### 18.1 Proposed material families

| Acquisition | Region/event | Examples (working names) | Special craft function |
| --- | --- | --- | --- |
| Common harvest | Outer Rim | Wood, Stone, Plant Fiber, Rawhide | Starter recipes, repair kits, field equipment |
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
- Ingredients can compete between building reinforcement, enchantments and long-term binding for real opportunity cost.
- Favor several different event sources for advanced recipes so an elite group cannot monopolize one boss and control every equipment path.
- Maintain a viable solo/midgame route to an early Permanent item, even if rarest Guardian conversion takes coordinated PvPvE activity.
- Vault contents are never raid-able; run bases and carried resources are, giving extraction its reason to exist.
- Portal multiplier should affect valuation/payout, **not duplicate unique gear, crafting inputs, Keystone, or Guardian drops** (Proposed).
- No pay-to-win Permanent catalysts or Robux-bought combat power.

### 18.3 Material sink model — Proposed

Resources exit the economy through (a) field supply/ammunition/raids, (b) secure special crafting, (c) consumed source equipment, (d) Permanent conversion, and (e) repairs/recovery. Track acquisition and sinks separately by material source; adjust source drop rates only after observing actual extracts, loss, and monopolization. Never apply arbitrary hidden wipes to the protected Permanent armory.

## 19. Special recipe examples — proposed balancing placeholders

**All quantities below are intentionally provisional.** Nothing in this table is a live drop promise; exact recipe materials, unlocks, rates and costs require simulation/playtests. An input gear instance must already be owned and vaulted.

| Output | Station | Consumed secured inputs | Role |
| --- | --- | --- | --- |
| Flint Hunter Spear | Stonecarver | Flint ×12, Bone ×6, Fiber ×10 | Reach-oriented low-cost weapon |
| Tidewoven Cloak | Stonecarver | Rawhide ×18, Resin ×8, Fiber ×20 | Light armor, mobility |
| Ironroot War Axe | Tribal Smithy | Iron Bloom ×24, Dire Hide ×6, Resin ×10 | Heavy stagger, slow recovery |
| Obsidian Fang | Tribal Smithy | Obsidian ×18, Bone ×16, Iron Bloom ×10 | Short-range cutting and bleeding |
| Jadeweave Vest | Rune Altar | Jade ×15, Iron Bloom ×16, Resin ×15 | Torso armor with modest elemental resistance and a weight tradeoff; no shield effect |
| Ember-Touched Spear | Rune Altar | Vaulted Metal Spear ×1, Emberglass ×6, Charged Core ×1 | Finite burn charges |
| Stormstring Bow | Rune Altar | Vaulted Reinforced Bow ×1, Charged Core ×2, Glow-Fur ×8 | Charged bow shots with cooldown |
| Frostwoven Mantle | Rune Altar | Tidewoven Cloak ×1, Jade ×14, Ancient Binding ×2 | Brief frost resistance |
| Ashen Breach Pot | Smithy | Emberglass ×5, Resin ×9, Obsidian ×4 | **Ordinary consumable**, never Permanent |
| Guardian Renewal Draught | Rune Altar | Jade ×25, Crown Ash ×2, Ancient Binding ×3 | Rare single-use heal or cleanse; **not Permanent** |

### 19.1 Permanent conversion examples — more expensive than ordinary crafting

| New Permanent record | Required eligible extracted source | Additional secured inputs | Gate / tradeoff |
| --- | --- | --- | --- |
| **Eternal Hunter Spear** | Flint Hunter Spear ×1 | Abyssal Shard ×2, Jade ×30, Ancient Binding ×5, Keystone ×1 | Early aspirational bound melee build |
| **Bound Ironroot Axe** | Ironroot War Axe ×1 | Abyssal Shard ×3, Obsidian ×30, Charged Core ×3, Keystone ×1 | Costly high-impact melee identity |
| **Everjade Vestments** | Jadeweave Vest ×1 | Jade ×50, Glow-Fur ×18, Guardian Heart ×1, Keystone ×1 | Permanent torso armor with bounded passive resistance, no shield or free healing |
| **Runebound Stormstring** | Stormstring Bow ×1 | Charged Core ×6, Emberglass ×20, Crown Ash ×4, Keystone ×1 | Costly bow mastery, finite charges |
| **Oath of the Guardian** | Eligible vaulted Guardian Legendary ×1 | Guardian Heart ×2, Abyssal Shard ×8, Crown Ash ×10, Keystone ×2 | Prestige goal, strict PvP power cap |

**Keystone** is a *placeholder* for the signature conversion reagent; working source concept is combining Keystone Fragments from multiple high-risk event types. Avoid impossible single-source monopolies. The 25%-boss-health Legendary is the **unconverted source**, not the free recipe result. Specific recipes are proposed examples, not confirmed craft specifications.

### 19.2 Upgrade and rarity guardrails

- Do not make highest rarity automatically best for every encounter: reach, weight, attack wind-up, status resistance and counterplay should matter.
- Permanent binding should not raise damage without clear statistical budgeting. Binding itself is a long-term utility advantage.
- If recipe affix rerolling is later considered, publish chances and safeguard ownership; **no hidden destruction chances by default**.
- Test whether a permanent tool grants unfairly rapid initial re-gearing. A recovery cost and loadout cap may be required.
- Material inflation, hoarding and recipe dominance should be measured by event/region, account tenure and solo/tribe cohort.

## 20. Detailed player journeys

### 20.1 New player, safe first extraction

Spawn on Outer Rim; gather wood and stone; craft a crude spear; fight a small hostile; find a hidden minor rune; extract uncommon ingredients for a modest payout. At the secure hub, receive an unmistakable **Vaulted** receipt and the first special Forge recipe preview. The player cannot convert the spear immediately; they need several further extractions. A failed first run drops carried loot but does not erase earlier vault progress. Goal: teach risk, safety, and long-term crafting in one sequence.

### 20.2 Solo scavenger, long-term progress without boss domination

Explore Inner Ring at quieter times, hunt smaller elites, withdraw only inexpensive vaulted gear, and extract Jade and occasional Charged Cores through variable rune routes. Build an ordinary special spear. Pin its Permanent recipe, deliberately choose a risky meteor run for the missing reagent, and eventually convert one signature weapon. This path must not require joining a dominant tribe. Endgame Guardian permanence can still require tougher objectives.

### 20.3 Rival tribes, betrayal and raid

Two tribes contest the Guardian's energy pillars as the Horn of War countdown ends. At 25% HP, a Legendary drops **before** boss death. A carrier grabs it and emits the high-value glow. A rival team ambushes and takes it. Meanwhile another squad raids the carrier's unguarded FOB and steals stored ordinary resources. Only a successful portal extraction secures loot; neither a base nor a bound weapon makes the Legendary safe. The tribe that escapes can later consider a very expensive Permanent conversion.

### 20.4 Death while wearing Permanent gear

A veteran equips one recovered bound sword plus ordinary armor, potions, arrows and newly gathered Obsidian. An enemy kills the veteran. The sword's manifested copy vanishes and enters armory recovery (**Working default**); everything else carried drops and can be claimed. The opponent earns real loot without creating a duplicate bound sword. The veteran must pay recovery/repair requirements before redeployment but never needs to win the sword from the boss again. This illustrates both long-term reward and continuing high-stakes risk.

## 21. Combat, progression and acquisition balance

### 21.1 Weapon-archetype vocabulary — Proposed

- **Spears/javelins:** Reach and committed thrusts; countered by lateral movement, inside-close pressure and punishing misses.
- **Clubs/axes/mauls:** High stagger/armor pressure, slow recovery and stamina cost; effective raiding preparation.
- **Blades/daggers:** Speed and flanking; shorter reach and weaker stagger against durable armor.
- **Bows/slings:** Draw commitments, projectile arcs, retrievable/consumed ammo, imperfect mobile aim assistance, countered by cover/rush.
- **Healing consumables:** Finite recovery with telegraphed use, potential interruption and cooldown. Consumables are never convertible to reusable Permanent sources.
- **Armor:** Passive mitigation and elemental resistance with mobility/weight tradeoffs, no blocking button.
- **Ember/frost/storm/earth magic:** Distinct status utility with telegraphs, charges and PvP control-duration caps, never machine-gun analogues.

### 21.2 Encounter difficulty

Starter wildlife teaches timing; Inner Ring fauna pressures mobility and counterattack; Alpha packs require kiting/positioning; Guardian requires shield-pillar coordination and telegraphed lethal abilities. The three-phase boss and 15–20-minute event cadence remain fixed from the concept, while damage, health, aggro, PvP contribution and loot counts are Open. Ordinary gear should be a viable counter to Permanent gear within reasonable tier/skill ranges.

### 21.3 Power-progression economy

Player strength comes from execution, temporary risked gear, group tactics and optionally limited long-term bound choices. Bound equipment should be **sidegrades or bounded advantages**, not a full gear set guaranteeing victory. Track win rates against account age and equipped item types; explicitly support solo extracts and stealthy base raids as alternatives to head-on crater fights.

## 22. Detailed inventory, extraction and death state transitions

### 22.1 Canonical item-location state machine — Proposed

| Authoritative state | Legal next state(s) | Notes |
| --- | --- | --- |
| **WorldSpawned** | Carried, despawned | Unique drop instance, distance and pickup validated by server |
| **Carried** | WorldDropped, BaseStored, Consumed, ExtractionPending | All ordinary inventory remains at risk |
| **BaseStored** | Carried, WorldDropped, Consumed | Raiding, door permissions and destruction rules apply |
| **ExtractionPending** | Carried (interrupt/death), ExtractionCommitting | Channel server-time and portal-zone checks |
| **ExtractionCommitting** | Vaulted (commit), retry pending | Item cannot simultaneously be dropped as corpse loot |
| **Vaulted** | Carried (withdraw), ForgeReserved | A safe storage location, *not* permanent status |
| **ForgeReserved** | Vaulted (cancel/rollback), Consumed / PermanentOwned (commit) | Reservation tied to idempotent operation ID |
| **PermanentOwned** | ArmoryRecovery, ArmoryAvailable, BoundActive | One immutable canonical account-owned instance |
| **BoundActive** | ArmoryRecovery, ArmoryAvailable | Temporary representation, never tradeable or duplicated |
| **Consumed** | Terminal | No replayable recreation without new server reward grant |

**Invariant:** Each ordinary instance occupies **one** authoritative world/inventory/vault/escrow location. A bound manifestation is an active *reference*, not a second owned transferable item. Stack totals are bounded integers and can be split only through server-validated operations.

### 22.2 Two-minute hold, protected animation and vault ledger — Confirmed / Proposed engineering

1. Client clicks the extraction rune. Server validates player, position, alive status and portal eligibility, sends audible/visual alerts to other players and starts the **120-second** countdown.
2. Server continuously confirms that the player remains within the marked area. Player is vulnerable to PvP and creature damage during the countdown. Exiting the area invalidates the attempt; restarting rather than pausing is proposed.
3. If death or an ordinary world departure occurs during the hold, there is no extraction. Instead the ordinary lootable-body rules apply.
4. After 120 valid seconds, an authoritative **ExtractionAnimationStarted** transition locks the exact eligible inventory snapshot and grants **invulnerability and safe disconnect at the moment animation begins**.
5. An immutable operation/receipt ID protects that locked inventory even if the player quits, teleports, loses connection or a DataStore write is still retrying. The backend must eventually reconcile the snapshot to the vault without forfeiture or duplication.
6. The animation communicates safety; only the server may authorize that state. An untrusted client's animation cannot grant or spoof protection.
7. Once the durable vault receipt is confirmed, show success and transfer to lobby. Until then, UI may show **Protected — Saving**; it must never claim final saved status prematurely.
8. Race resolution: death/ordinary leave before animation => single lootable body; server-authorized animation before death/leave => no body for committed items. Maintenance safe-kick uses a distinct audited exemption.

**Engineering invariant:** The user-facing animation start is the protection threshold, not the animation end or return-to-lobby transition. It requires a recoverable extraction entitlement so item safety is guaranteed while eventual storage may be pending.

### 22.3 Disconnect, shutdown and concurrent sessions — Confirmed / Proposed engineering

- **Confirmed:** Ordinary player departure from anywhere outside the lobby — voluntary quit or lost connection — leaves a single lootable character body in the active server and forfeits carried ordinary loot. **Body and unclaimed loot disappear after 10 minutes / 600 seconds.**
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
| **PermanentArmoryService** | Permanent canonical records, loadout lease, death recovery | Bound armory, recovery conditions, slot occupancy |
| **LoadoutService** | Ordinary equipment withdrawal, bound caps, deployment preparation | Risk labels and confirmed slots |
| **ExtractionService** | Exactly 120-second in-area hold, alerts, animation-start invulnerability, vault receipt | Countdown/boundary, opponent alerts, protection and verified receipt |
| **CombatService** | Validated hits, movement/dodge, healing consume and interruption, enchantment procs, PvP cooldowns | Health/status animations, healing progress and hit feedback |
| **BuildingService** | Booga Booga-style placement, rotation/snap, ownership, exclusions, raids and stash damage | Responsive build previews, repair and access errors |
| **EventDirector** | Meteor/cache/alpha, rare flora, deposits, regional bosses and raidable structures | Tiered alerts, discovery markers and beacons |
| **BossService** | Horn, timer, shield pillars, HP phases, once-only Legendary drop | Boss warnings, phase UI, rewards at risk |
| **AnalyticsService** | Economy, public-world activities, participation, reward abuse, dupes/failures | Verified activity rewards/diagnostics |
| **DepartureService** | Normal non-lobby body + 600-second TTL, lobby exit, protected extraction exit and maintenance exception | Risk warning, body/despawn and restoration statuses |

All persistent crafting and extraction grants happen on the **server**. Client may request an action but cannot dictate rarity, cost, exact output, reward source, success flag, or timestamp.

### 23.2 Versioned profile structure — Proposed

| Field group | Representative fields | Constraints |
| --- | --- | --- |
| Profile envelope | schemaVersion, profileRevision, sessionLease, lastCommittedOperationId | Migration/backward compatibility and stale-write checks |
| Vault stacks | itemCatalogId → safe integer quantity | Nonnegative, bounded, server-calculated |
| Vault instances | instanceId → catalogId, quality, rolls, wear, acquisition ID | Unique IDs and verified provenance |
| Permanent armory | instanceId, catalogId, boundOwnerId, affixes, recovery, deployLease | No trade/drop path, no duplicate manifestations |
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

- Shared typed definitions: item archetypes, tiers, stats, recipes, event types, magic schools, damage/status tags, portal definitions, validation schemas and tuning constants.
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
| Permanent item dropped/traded to alternate account | No bound trade, world-drop or base-stash transfer endpoint |
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

- Filters for tools, weapons, armor, enchantments, consumables and Permanent recipes.
- Crafting detail includes **Owned/Required** stacks, region/event sources for missing rare reagents, recipe unlock status, source gear stats, result stats, durability and material loss.
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
9. Bound item on death disappears from field and resolves to recovery while ordinary carried materials still drop.
10. Bound items cannot be looted, traded, hidden in chests, duplicated by rejoin or equipped in two Roblox servers simultaneously.
11. Guardian Legendary spawns once per encounter at 25%; killing boss is not automatic extraction or conversion.
12. All rune auras reject new construction within 50 meters; externally anchored overlapping geometry cannot enclose portals.
13. Portal payout never duplicates unique materials, Keystone, Legendary source instances or crafting outputs.
14. Cache requires a continuous 60-second unlock under specified interruption rules; event UI and world beacon agree.
15. Invalid melee reach, firing interval, elemental effect spam, hit provenance and malicious client remote sequences are rejected.
16. DataStore throttle, teleport failure, competing sessions, server shutdown and stale revision rejoin retain safe state integrity.
17. Mobile and controller players can navigate Forge and extraction without mouse-only precision.
18. Recipe tracker reflects only safely extracted materials; death changes only at-risk inventory.
19. No deployment or publishing workflows target temporary/version branches; only main may publish.
20. Deployed Roblox place testing is **not applicable until source/place credentials are connected**.
21. Ordinary non-lobby departure produces exactly one corpse for 600 seconds, with unclaimed loot despawning at expiry and claimed loot owned exclusively by looter.
22. Lobby exit never creates a loot body or forfeits inventory.
23. Authorized admin-update safe-kick preserves exact held items (no extract/multiplier); forged client admin flags and duplicate restore requests fail.
24. Rune click broadcasts audible/visual cues; countdown takes exactly 120 continuous in-area seconds, validated by server; dying, quitting or exiting area early cannot extract.
25. At valid animation-start threshold, damage and disconnect cannot cause item loss; idempotent locked receipt settles exactly once, even after DataStore fault.
26. Corpse-versus-extract and corpse-versus-maintenance races never grant double inventory or lose protected items.
27. Rare plants/materials, elite mobs/bosses, raid structures and meteors have finite rewards and tier-appropriate announcements.
28. Activity rewards are validated across PvP, farming and building and resist AFK/idle/server-hopping exploits.

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

1. What exactly does Permanent retain through death: bound gear itself or a rebuildable blueprint?
2. Recovery payment/delay and whether bound gear can wear out permanently.
3. Bound equipment slot cap and compatible archetypes.
4. Account binding vs trading/gifting (default: no trade).
5. Ordinary vaulted item withdrawal and reconnection handling.
6. Item-instance provenance, cross-server session locking and operation journal semantics.
7. How event-critical unique items are represented and multiplied/valued on extraction.

**P1 — can remain proposed through first prototype, then tune:**

8. Recipe resource quantities, sources and rarity names, Keystone path, unlock milestone requirements.
9. Permanent damage/power cap relative to consumable top-tier gear.
10. Enchantment affix preservation and charge/repair rules.
11. Vault capacity, material stack weights, equipment durability.
12. Boss clear rewards beyond the confirmed mid-fight Legendary.
13. Map size, portal timing/camping protection, tribe capacities and wipe schedule.
14. Cosmetic monetization, tutorial content, achievement rewards and hub architecture.

## 28. Production milestones and documentation maintenance

| Step | Scope | Completion evidence |
| --- | --- | --- |
| 1. Design agreement | Choose Permanent death model, rarity/eligibility and vault semantics | Explicit signed-off GDD decisions (not just proposed paragraphs) |
| 2. Risk loop vertical slice | Gather, heal, fight, death/leave corpse, extract by 120-second hold and protected animation | Body expires at 600 seconds; alarm, safe disconnect and eventual vault receipt validated |
| 3. Forge / ownership proof | Ordinary special recipe, one eligible source conversion, bind slot, recovery | Verified exactly-once crafting under retries, real rejoin/death tests |
| 4. Social / PvP slice | Spear, bow, **healing consumables**, one elemental effect, solo/tribe safeguards | Test sustained damage vs healing rates, interruption and escape; no player shield equipment |
| 5. World + raids | Outer/Inner biome, Booga Booga-like structures, 50-meter exclusions and stash raids | Quick placement, raidable storage and no portal obstruction |
| 6. Broadcast event | Rare plants/materials, mob/boss events, raidable structures, meteor, beacon and rare carry burden | Varied events and playstyles, with loot requiring extraction |
| 7. Crater Guardian | 15–20-minute cadence, horn, pillars, fight, 25%-HP drop | One mid-fight Legendary and accurate telegraphs; no auto-vault |
| 8. Economy alpha | Recipes, conversions, activity rewards, economy telemetry and sinks | Solo/farmer/builder/PvPer progression viable, no AFK exploits or observed dupes |
| 9. Launch readiness | Full server profiling, accessibility, persistence faults, anti-exploit | Reviewed CI, manual playtests and publish-from-main gates |

**Current actual status:** Design only. The GitHub repository contains Markdown documentation, not a playable Roblox implementation. Recipe prices and operational policies are hypotheses until explicit approval, simulation and testing.

## 29. Design change log

| Revision | Date | Change |
| --- | --- | --- |
| **0.1** | 2026-10-21 | Created Flintborn GDD from the original primitive extraction handoff; recorded primitive-fantasy/no-firearms direction; added proposed systems, technical guardrails, vertical slice and decision backlog. |
| **0.2** | 2026-10-21 | Added confirmed extracted-material special crafting and expensive eligible-item Permanent conversion; expanded item taxonomy, Forge design, working death/recovery policy, resource/recipe catalog, cross-run economy and player journeys. Further implementation details in §22–28. |

---

**Working principle:** Protect the identity of Flintborn: **primitive survival, no firearms or player shields, healing supplies, raidable preparation, contested events, visible rare loot, manual extraction, safe vault, rare special crafting and costly Permanent conversion**. Proposed features are not final decisions until approved and tested.
