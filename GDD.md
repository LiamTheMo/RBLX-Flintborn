# Flintborn — Game Design Document

> **Status:** Comprehensive pre-production specification (not implemented)  
> **Design revision:** 1.1  
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

**Confirmed economic decisions (2026-10-22):** The secure vault **always retains ALL extracted items and materials**, across empty-world resets. **Center Crater extraction doubles every material stack quantity, including rare ingredients, and XP**; gear item instances are not necessarily materials. Coins and Gems are persistent; Gems are premium-leaning but earnable. Direct player trading exists (not auction/marketplace); raw materials may trade only if a specific rare/Exclusive type is designer-enabled. Rarity: **Common → Uncommon → Rare → Epic → Legendary → Mythic → Secret → Exclusive**. Persistent account levels and crafting/activity mastery milestones grant modest permanent buffs/cosmetics. Top-tier Permanent gear requires contested high-end objectives; farming/building alone cannot yield the rarest. Booga Booga-inspired enhanced primitive visuals, adjustable camera, tutorial and guided quests. Monetization includes cosmetics, convenience, memberships/private-server-like access and rebirth tokens spent on perks; **every benefit must also be earnable through sufficient gameplay currency/resources**. Platform-native product restrictions remain to be validated. See §36.

**Confirmed Q116–150 (2026-10-22):** No automatic Coin reward on extraction; fixed-price NPC shops/sales, 250/1000/3000 Coin quest payouts, typical Gem award ~25. Constant Gem price per +25 vault item-slot tier (amount TBD). **9-slot hotbar**, **50-slot backpack**, one logical ordinary material stack per backpack slot, and separately **~1,000 secure material allowance** (unit semantics Open). Ordinary extracted materials auto-bank, while equipment/tools/other items and special materials remain in a protected lobby backpack until manually vaulted. Full armor set EHP factors Hide ×1.2, Wood ×1.5, Stone ×1.8, Iron ×2.0 with three pieces contributing additively. Medical animations 0.5/1/1.5 seconds; revival restores 10% max EHP converted to actual HP. Rock/dagger/sword/spear attack-cadence targets 0.3/0.4/0.7/0.9 seconds; bow hold changes range not damage. Craft quality ±5%; mastery improves best-roll odds multiplicatively by 5% per level (1% → 1.05% at level 1 → 1.5% at level 10). Event categories roll independently after ~25% trigger checks, descending Secret (~0.1% illustrative) to Common fallback; no fixed event count cap beyond footprint/performance. Totems start hut-sized and upgrade via materials, overlapping areas preserve original ownership until takeover. Bosses have fixed baseline plus combined level/gear scaling. First Permanent pickaxe candidate. Premium baseline XP +25% and temporary consumable boosters earnable by everyone. See §39.

This GDD is the source of truth for gameplay intent. Engineering contracts, tuning tables, art briefs, and implementation tasks should reference it rather than silently changing its rules.

### Document navigation

- **Gameplay foundation:** [Core loop](#2-core-run-structure), [Shattered Crater](#3-world--the-shattered-crater), [survival/equipment](#4-primitive-progression-resource-gathering-and-food), [combat/revival](#5-combat-movement-tribes-and-revival), [bases](#6-booga-booga-style-construction-claims-farms-and-raids).
- **Contested objectives:** [Weighted events](#7-weighted-world-event-system-and-public-announcements), [Guardian](#8-guardian-mega-boss-and-scalable-encounters), [extraction/vault](#9-extraction-and-permanent-vault), [currencies/trading/rarity](#10-persistent-currencies-resource-economy-trading-and-rarity).
- **Long-term progression:** [Special crafting / Permanent](#15-cross-run-special-crafting-and-the-permanent-item-class), [Ancestral Forge](#16-the-ancestral-forge-crafting-outside-the-run), [Permanent ownership](#17-permanent-gear-death-protection-and-ownership-transfer), [material sources](#18-resource-tiers-economy-and-acquisition-sources), [nonmagical recipes](#19-nonmagical-special-crafting-and-permanent-conversion-examples), [persistent masteries](#33-permanent-playstyle-masteries-milestones-and-world-engagement).
- **Implementation:** [Inventory state transitions](#22-detailed-inventory-extraction-and-death-state-transitions), [Roblox architecture](#23-proposed-roblox-luau-services-and-persistence-model), [threat model](#24-economy-abuse-cases-and-anti-duplication-tests), [UX requirements](#25-ux-specifications-and-interface-inventory), [tuning plan](#26-quantitative-tuning-and-live-analytics-plan), [QA](#27-detailed-verification-matrix-and-qa-plan), [production phases](#28-production-milestones-and-documentation-maintenance).
- **Critical onboarding/world systems:** [10-minute corpses](#29-ordinary-departure-death-and-lootable-bodies), [admin update kicks](#30-administrator-update-kicks-and-maintenance-safe-preservation), [protected Play menu](#31-protected-play-world-main-menu-and-teleport-safety-design), [world ecology/takeover](#32-world-ecology-procedural-rare-spawns-and-structure-takeover), [masteries](#33-permanent-playstyle-masteries-milestones-and-world-engagement), [final economy/rebirth decisions](#36-owner-approved-economy-appearance-and-monetization-decisions-q3-q23-q4960).

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

- Survival meters at launch are **health, stamina and food only**. **Base maximum HP: 100** (can increase through approved upgrades/gear). **Full sprint duration: 3 seconds**, then **5 seconds for full stamina recovery**. **Full food meter depletes to empty in 5 minutes** (baseline), and food **below 25% slows movement by 10%**. No thirst, temperature or weather-exposure survival meters.
- Avoid a “rich get richer” lockout where fresh spawns cannot make progress.
- Prioritize readable telegraphs and counterplay over surprise one-hit kills.
- **Confirmed monetization rule:** All paid benefits must have an **earnable in-game currency/resource path** given enough playtime, even if monetization goes beyond cosmetics/convenience. Avoid unbounded pay-to-win advantage, and preserve contested rare-item gameplay; exact perk caps and native Roblox purchase feasibility are Open.
- Keep the full loop understandable to a first-time Roblox player, including touch/controller input.

## 2. Core run structure

### 2.1 Primary loop — Confirmed

1. **Prepare safely:** Travel to a play-world server and wait at its protected main menu until profile/assets are ready. **Explicitly click Play**; the server confirms a successful character spawn before making equipped ordinary gear at risk. Teleport/load/spawn failures never forfeit items.
2. **Scavenge:** Gather wood, stone, flora, and other materials; create tools, weapons, shelter, and supplies.
3. **Prepare:** Craft/upgrade gear; optionally join a tribe and establish a forward operating base (FOB).
4. **Take a risk:** Explore the Inner Ring, contest broadcast events, raid exposed bases, or challenge the Center Crater boss.
5. **Carry the prize:** Valuable items physically occupy the player's carried inventory; rare/event loot exposes a visual trail.
6. **Extract:** Activate a fixed exit's shared 120-second server timer (or a rare portable rune's 30-second timer), then be alive and within its zone **when it ends** to enter the protected animation and bank loot.
7. **Build permanent progression:** Save vault materials, craft designated Permanent equipment, upgrade vault capacity, gain **persistent Coins/Gems/XP and activity masteries**, earn small permanent buffs/cosmetics and eventually rebirth perk tokens. The **central portal doubles extracted material stack quantities and XP**.
8. **Continue or extract:** Stay in the public world to build/farm/fight, or wait nearby for an extraction timer to end while you stand inside the small exit zone. Hiding, healing and fighting are allowed before the deadline. Active-world quits forfeit ordinary items; pre-spawn menu quits are safe.

### 2.2 Loss and persistence contract

| Domain | Established behavior | Design status |
| --- | --- | --- |
| On-person active-run inventory | Drops on death or ordinary departure **after successful Play admission**, leaving lootable **10-minute body** | **Confirmed** |
| Lobby or world main-menu departure | Safe regardless of teleport/load failures or pre-spawn kick | **Confirmed** |
| World admission | Only successful explicit Play/ready/spawn transition activates carried inventory risk | **Confirmed** |
| Protected extraction | **120-second shared fixed-site countdown** with large-radius cues; living players must be **inside zone only at completion**, not throughout. Portable runes use 30 seconds; invulnerability begins at animation start. | **Confirmed** |
| Administrator maintenance kick | Safe removal for game updates without losing held items | **Confirmed**; escrow details Proposed |
| Successfully extracted loot | **Always saved** in secure account vault across all world resets, including ordinary materials and gear | **Confirmed** |
| Extracted crafting resources | Feed special recipes and costly permanent conversions | **Confirmed** |
| Converted Permanent equipment | Survives death, **same stats as source**; deliberate drop/loot and trade can change ownership; only designated items qualify | **Confirmed**; recovery cost/slot cap Open |
| In-world base storage | Can be looted if opposing players raid the base | **Confirmed** |
| Gear withdrawn from vault for deployment | Extracted items and materials may be withdrawn, becoming ordinary at-risk gear on successful active Play admission | **Confirmed**; loadout limits Open |
| Player progression | Player **levels** and recipe **discovery** both exist | **Confirmed**; exact XP curve/unlock combinations Open |
| Bases and public world resets | On empty server **only world state resets**; **all already vaulted equipment/materials persist** | **Confirmed — Q3 clarified** |
| Public world playstyles | **Exactly five mastery tracks:** Mining, Woodcutting, Farming, Crafting and PvP, capped at 10 with a buff each milestone level. Cosmetics persist. Other activities still grant XP/quests but no separate mastery track | **Confirmed Q71–80**; thresholds and stat caps Open |
| Account currencies | Persistent **Coins** and premium-leaning but earnable **Gems**; player XP/levels, crafting mastery and rebirth tokens | **Confirmed**; rates/prices Open |
| Trading | **Lobby-only direct trades** with eligible items and **Gems only**, **NO Coins**; material types only if designer-enabled rare/Exclusive; Permanent items tradeable | **Confirmed Q98**; catalog/fraud controls Open |
| Rarity ladder | Common → Uncommon → Rare → Epic → Legendary → Mythic → Secret → Exclusive | **Confirmed** |
| Disconnects during combat/extraction | Actual active-run disconnect leaves lootable body; **pre-spawn menu and loading are safe**; after protected extraction animation starts, disconnect is safe | **Confirmed**; crash reconciliation Open |

**Confirmed Q3 resolution:** **Every item and material deposited into the protected vault remains saved across world resets, ALWAYS**, regardless of rarity or Permanent status. Public worlds discard bases, loose resource nodes and world loot when empty; they **never wipe already vaulted inventory, account Coins/Gems, earned XP/levels or permanent mastery**. Vault capacity is upgradeable. Previously at-risk gear remains subject to death and disconnect loss before extraction.

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
- **Confirmed Q3 resolution:** When a world empties, **all temporary island objects reset**. **All previously extracted items/materials in the protected vault are ALWAYS saved**, no matter their rarity or Permanent status. Account currencies, levels/masteries and cosmetic entitlements are unaffected.

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

**Confirmed:** Keep **a small starting resource catalog** (candidate wood, stone, iron, fiber, food, hides and rare event drops) and expand later. Initial construction tiers remain **wood → stone → iron**. Exact sources/numbers are Proposed. No player magic at launch.

### 4.2 Initial item families

| Family | Examples / rule |
| --- | --- |
| Harvesting tools | Axe, pickaxe, sickle; server validates harvest ranges and legitimate node yields |
| Launch melee weapons | **Spears, daggers and swords**; basic rock/tool attacks remain possible. Clubs, combat axes and other weapon families are future options |
| Launch ranged weapons | **Bows**, with slow visible projectiles; slings, javelins and crossbows not committed at launch |
| Ammunition | **Every arrow recipe crafts 10 arrows**, with better material tiers optionally increasing damage; slow physical projectiles |
| Armor | **Head**, **Chest** and combined **Legs/Boots** are the only three armor slots; gear lasts indefinitely, no shields |
| Medical items | Basic **+10 HP**, advanced **+25 HP**, potion **+50 HP** immediately (capped at current max), followed by varying animation durations as the reuse cooldown |
| Food | Food meter drains from full to zero in **5 minutes**; below **25%** slows movement **10%**. Eating produces food-dependent healing over **10 seconds**, halved on hits, with small remainder cutoff |
| Utility | Torches, storage supplies, farm tools, primitive traps and other nonmagical gear |
| Building | Placeable shelters/doors/storage/totems/farms and functional stations; initial wood, stone and iron tiers |
| Future (not launch) | Elemental spells, enchanted combat weapons, special defensive resistances and any charge/mana subsystem |

### 4.3 Survival attributes — Confirmed and Open

- **Health:** **100 base maximum HP**, with gear/upgrades allowed to change the cap; exact bonus sources and caps remain Open. Effective damage is transformed through the equipped armor **effective-HP multiplier** (§21.5), not a simple flat subtraction from normal HP. Medical items heal immediately subject to the *current modified* maximum HP. Tribe downing at 0 HP uses a separate **20-HP downed pool**, protected by armor (§5.3).
- **Stamina:** A full bar allows **3 seconds of continuous sprint**; **5 seconds to recover from empty to full**. **Only sprinting spends stamina**. Melee, crouching, gathering, bow shots, raiding and ordinary movement do not. Whether recovery pauses on renewed sprint or begins after sprint ends, sprint speed and stamina UI granularity remain Open.
- **Food:** A full food meter falls from **100% to 0% over 300 seconds (5 minutes)** under the baseline drain. **When strictly below 25%**, apply **10% movement-speed reduction**; it remains while below threshold. Food items grant item-specific healing totals over **10 seconds**. Incoming damage halves *remaining unapplied* HoT healing; if the remainder **after halving is ≤10 HP**, clear it to zero. No food-caused extra HP above the current max has been approved. Drain modifiers, refill quantities and zero-food additional penalties are Open.
- **Excluded at launch:** Thirst, temperature, magical energy/mana, shield meters, equipment durability and weather survival stats unless explicitly approved in a later revision.

### 4.4 Recipes and Permanent equipment

- Successfully **extracted** materials support special crafting; conversion targets only specifically designated equipment and **does not increase its stats**.
- Recipes are acquired through a combination of **player levels and discovery**; high-tier special recipes use multiple resource and event types.
- Weapons/armor **last indefinitely** through ordinary use. If Permanent ownership needs a post-death material payment for balance, that is a separate **Open recovery cost**, not wear-based durability.
- All enchantments, rune combat effects and spell recipes proposed in older sections are **future-update candidates**. Any existing named magical recipes (§19) are conceptual content backlog and **not approved launch recipes**.
- Exact item caps, inventory weight, crafted arrow batches, crafting stations, **individual food item healing totals**, food refill amounts and tier-specific medical animation durations remain Open. Food healing **duration is fixed at 10 seconds**.

### 4.5 Medical items, healing and food — Confirmed / Proposed details

| Item type | Server-side trigger | When HP changes | After-use behavior |
| --- | --- | --- | --- |
| Basic medicine | Valid stack and cooldown checked, then one unit consumed | **Immediately +10 HP** (up to current max HP) | Visible animation after healing; blocks another medical use until duration finishes |
| Advanced medicine | Valid item consumed | **Immediately +25 HP** (up to current max HP) | Tier-specific animation/reuse cooldown; exact duration Open |
| Potion | Valid item consumed | **Immediately +50 HP** (up to current max HP) | Tier-specific after-heal animation/reuse cooldown; exact duration Open |
| Food | Valid edible consumed | **Over 10 seconds** after eating; amount depends on food | Each hit halves unapplied remaining heal; if post-hit remainder ≤10 HP, cancel remainder completely |

**Important:** A medical animation is the **cooldown**, not a pre-heal channel. Incoming damage cannot retroactively cancel an already applied instant medical heal. Repeated use requests during the animation must not apply another heal or consume another item. A player may still be attacked while animating; movement lock/speed during the animation remains Open.

**Confirmed food interruption (Q65):** Each damaging hit cuts the **remaining, not-yet-applied** food healing in half. If the **remainder after the 50% cut is ≤10 HP**, set remaining food healing to **zero**. Already-healed HP is never removed by the interruption rule (normal hit damage still applies). Example: 40 HP remaining potential → hit leaves 20; a second hit leaves 10 and therefore cancels the rest. Food item total varies, but its heal window is **10 seconds**. The term “overheal” here means *pending food regeneration*, not a temporary shield or permission to exceed maximum HP. Stacking several food heals, pause/tick timing and whether the duration resets on hit are still Open.

**Potential item names** (Fiber Bandage, Herbal Poultice, Restorative Tonic, Healing Potion) and ingredients are examples, not official content. Unlimited-use medical gear and Permanent-converted healing consumables are excluded.



## 5. Combat, movement, tribes and revival

### 5.1 Launch combat baseline — Confirmed / Open

- **Confirmed:** Click-to-attack melee and slow crafted physical bow arrows. **Working Q66 damage baselines: rock hit 5 damage at high attack cadence; wooden spear ~15 at slower cadence and longer reach; stone spear ~25** before armor. Wooden/stone spear figures are **tentative playtest targets** (the owner said “maybe”), not locked final values. Attacks/second, precise reach, projectile damage/velocity and hitboxes remain Open.
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

### 5.3 Downed, 10-second revive and death — Confirmed / Open tuning

1. **Solo non-tribe character:** Ordinary HP reaching **0** means immediate death. Ordinary items transfer to a 10-minute lootable body, and the character is **ejected to the separate lobby**, with no same-world respawn.
2. **Tribe member:** When normal HP reaches **0**, enter the **Downed** state with a separate **20-HP downed pool**, and start the existing **60-second unpaused rescue window**. These 20 points apply *after* the normal health bar hits zero, not as extra regular HP before downing.
3. **Finishing attacks are permitted immediately.** The downed player remains damageable; opponents can kill them by exhausting the **20 downed HP** even before the 60-second window expires. **Armor protection continues to apply**, using the same EHP calculation (§21.5), including during revival.
4. A valid tribe member starts a revive that needs **10 continuous seconds**. While an eligible revive is actively running, **pause** the remaining 60-second downed timer. This pause **does not make the downed player invulnerable**.
5. If the revive cancels, is interrupted or becomes invalid, the rescue timer **resumes from its exact remaining duration** (not 60 fresh seconds). Only validated active revivers may hold the pause; disconnected or distant actors cannot freeze it indefinitely.
6. After **10 uninterrupted valid revive seconds**, return to ActiveRun without corpse or new-world spawn. **Normal HP restored on revival is Open**; never infer that the 20 downed HP automatically becomes post-revive HP.
7. Death occurs if the 20 downed HP reach zero after armor-adjusted damage, **or** 60 seconds of *unpaused* downed time elapse. Generate one lootable body (600-second TTL), eject to lobby and apply same-JobId rejoin denial. An attack can finish the downed person **while another person is reviving them**.
8. The **8-player maximum tribe** and no same-world respawns (including beds) remain. Downed players do **not** qualify as alive for portal extraction until successfully revived.

**Confirmed:** Downed health **20**, revive **10 seconds**, rescue timer **60 unpaused seconds**, valid revive pauses timer, cancelled revive resumes it, opponents may finish immediately, and armor affects damage while downed. **Open:** Post-revive normal HP, allied-versus-tribe reviver eligibility, whether incoming damage interrupts *the reviver's* action, whether downed players crawl or can heal, multiple reviver behavior and any temporary protection after revival.


### 5.4 Medicine, food and sprint timing

- **Medical item or potion:** Server confirms valid consumable, **immediately heals** and deducts one item exactly once. Begin **after-heal animation cooldown**; cannot immediately chain another medical item before cooldown ends.
- **Food:** Every food grants its item-specific healing total over **10 seconds**; each damaging hit halves the *remaining unapplied* healing, cancelling it if the post-hit remainder is **≤10 HP**. Previously healed HP is not taken away by this cancellation rule.
- **Movement:** Sprint lasts **3 continuous seconds** from full stamina; empty-to-full regeneration takes **5 seconds**, and only sprint drains stamina. Food takes **5 minutes** to go from full to empty; below **25%**, walking/running movement speed is **10% lower**. Crouching, attacks, harvesting and building do not cost stamina.
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

### 6.2 Tribe claim totems and unclaimed decay (Q113–114)

- **Confirmed:** Player-built bases persist in the populated public world after owners leave and can be taken over, until the entire instance becomes empty. A valid tribe claim totem within range protects **nearby player-built structures** from natural decay only; it never prevents PvP/raiding.
- **Totem influence radius depends on eventual map scale**; no fixed numerical radius yet. **Totem claim zones are allowed to overlap**, including zones belonging to different tribes. The **priority, ownership attribution and access/conflict resolution** for overlapping areas remain Open; do not silently disallow overlap.
- **Confirmed unclaimed decay target:** If a structure has no valid protecting tribe totem nearby, it **fully decays over approximately 5 minutes with ±1-minute random variation**, i.e. **4–6 minutes** as an initial proposed time-to-destruction window. If the user intends this as a *damage tick interval* rather than whole destruction, clarify before final numerical implementation; initial working interpretation is **total unclaimed lifespan**.
- **Proposed engineering:** On becoming unclaimed, assign a server-authoritative decay deadline in the 4–6-minute range. Restoring valid totem coverage pauses/cancels decay according to a clearly tested rule; loss of coverage begins/resumes it. Do not let rapid placement/remove instantly reset endlessly or create negative health.
- Tribes may claim **their own built structures** only; **server-generated events/ruins cannot be claimed**. Any physically reachable storage remains openable by anyone; totems do not lock chests.
- **Open:** Totem radius, max totems, overlapping ownership priority, whether reclaiming unclaimed/abandoned bases grants new ownership, exact decay distribution, material-tier decay effect and structural repair mechanisms.


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

**Confirmed Q111 target:** The weighted **non-Guardian** scheduler checks for an eligible event **approximately every 5 minutes** (tunable target), and **multiple events may coexist**, provided the server validates a **minimum separation / no overlap** between their active footprints. Roll may legitimately select no event; exact probability weights and separation radius remain Open. **Guardian** keeps its distinct established ~15–20-minute cadence and 3-minute announcement unless separately changed (§8).

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
- Allow **multiple simultaneous non-Guardian events**, constrained by spatial collision/separation, total NPC/structure budgets and 30-player server performance. A newly rolled event that would be too near an active one must relocate to a valid biome position or safely skip/defer, without spawning overlapping reward sources.
- Event weights and rewards should be visible in balance configuration, with analytics tracking actual spawn frequency and **successful extractions** of their loot.
- Public announcement must reach clients with UI/sound accessibility support; alert destination accuracy and radius are **Open**, but no secret unannounced rare event should contradict this design.
- A full 30-player server and a low-population server may require different cooldown/budget controls, but reward rates and spawn rarity must stay fair.
- **Confirmed:** Approximately **5-minute weighted event check**; rare event resource occurrences are **one-time** until an event of that type happens again; routine trees/rocks/ores regrow after **~2 minutes**. **Open:** Exact chance of no event, weight tables, spatial footprint distance/overlap limits, event concurrency/performance caps, ritual recipes, encounter cancellation, ruin despawn and special reward rights.


### 7.6 Routine node respawning versus one-time event spawns (Q112)

- **Ordinary trees, rocks and basic ore nodes:** Initial respawn target **~120 seconds** after harvesting/depletion, at a valid server-authoritative location/state (precise timing and spawn probability to be tuned).
- **Rare event resource nodes/shrubs/trees:** **One spawn per event**, with **no ordinary two-minute regrowth**. Players must wait for a **future new weighted event** of that type, which may occur at a different valid biome location.
- Respawned ordinary resources must not duplicate simultaneously via concurrent harvest requests, and repeated event callbacks must not re-award one-time rare drops.

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

### 8.3 Baseline-plus-scaling boss difficulty (Q115)

**Confirmed:** Every boss archetype has its own **defined baseline level/difficulty**. An additional difficulty scaling component adjusts challenge using eligible active-server population strength, but the **formula and signal are intentionally unresolved**.

**Open candidates:** Average server player level, average equipped gear score, a blended metric, and whether party or engaged participant count matters. Scale-at-spawn vs live updates also remains Open. **Proposed working safeguard:** Snapshot a validated population metric at spawn (rather than reacting to rapid unequipping or alternate account joins). Prevent boss difficulty reduction when an attacker removes armor after initiating a fight. Respect world-event, ritual and structure boss-specific reset rules; central Guardian retains its separate cadence.

### 8.4 Future boss design questions — Open

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
- **Payout:** The **Center Crater portal grants 2× all material stack quantities and 2× XP** to eligible extracted players, **including rare crafting materials** (§9.3). Coins/Gems and individual equipment copies were not explicitly specified as doubled.
- **Loot:** Safely extracted material stacks feed crafting; the center bonus **legitimately adds material quantities** including rare catalysts but does **not** auto-convert equipment to Permanent. Unique gear instances are not presumed doubled.

### 9.2 Server-shared timer and qualifying snapshot — Confirmed / Proposed engineering

1. Server validates an activation and reserves **one** event at the available site, with its own start/end timestamps. For a regular fixed exit, expiry is **120 seconds** later; for a rare portable rune it is **30 seconds** later.
2. The server emits the audible and visible alert. The clock continues independently of player proximity, combat, deaths or healing.
3. Players may leave the capture area and return as often as desired. No continuous stay counter exists. An alive character may also arrive late and qualify if physically inside at the exact finish.
4. At expiry, server captures the set of eligible **alive characters inside the defined zone** and grants protected animation to each, including multiple group/tribe members using the same timer. No late entry after the snapshot.
5. Each eligible player gets an individual locked inventory and extraction receipt; the portal event has one shared unique ID. No player can claim someone else's items, join twice or receive two extracts from the same event.
6. At the animation transition, the player's invulnerability and safe-disconnect guarantees take effect; individual loot snapshots settle idempotently to secure vault.
7. Successful players go to lobby after persistence confirms. Unqualified players remain vulnerable and gain no automatic protection; the shared event ends.

**Open behavior:** Whether anyone may start another countdown on the same site immediately, whether the activator's death cancels the event (working default: **no**), whether enemies can intentionally use an opponent-triggered extraction (working default: **yes**), the minimum participant distance, visual radius and portable-rune interactions. All are design choices; the freedom to leave the area and fight/heal is already Confirmed.

### 9.3 Confirmed Center Crater bonus: 2× all materials and XP

**Confirmed Q23 + Q69:** A successful **Center Crater portal** extraction doubles **every extracted material quantity** and **all XP earned during that expedition**, not merely the XP normally granted at extraction. This includes valid **general/player XP and mastery XP** awarded for the run's harvesting, crafting, events, PvP and quests; final extraction XP, if awarded, is included in that run ledger. **Confirmed Q70:** Base XP and mastery progress are saved **as earned before extraction** and **are not forfeited on death or unsuccessful exit**. Center extraction grants an additional amount equal to the total qualifying run XP already earned, one time.

| Payload example | Regular extraction | Center Crater extraction |
| --- | --- | --- |
| 10 Stone | 10 Stone | **20 Stone** |
| 3 rare ore | 3 rare ore | **6 rare ore** |
| 1 rare boss crafting reagent (material) | 1 reagent | **2 reagents** |
| 100 XP earned during this run (already saved) | Keep **100 XP** | Keep original **100 XP** + **100 bonus XP** = **200 total** |
| 1 individually unique Legendary sword (equipment) | 1 sword | **1 sword**, unless separately approved |

**Important:** This is *real item stack duplication by design*, not merely display valuation or extra coins. Rare materials can double; do not reintroduce the older rule preventing rare reagent multiplication. **Only uniquely identified equipment items**, which are distinct from stackable materials, remain at one canonical instance unless the owner approves otherwise.

**Confirmed Q69/Q70 XP boundary:** General/player XP **and mastery XP** are applied to persistent account records when legitimately earned during the active run, **without requiring an extraction**. A successful center extraction then grants **one additional full run's worth** of each XP category based on immutable run-specific earned-XP ledgers. Ordinary death/logout **does not delete previously earned XP or mastery progression**, but cannot receive the conditional center bonus. Prior run XP and unrelated lobby/Forge XP cannot be retroactively doubled. **Open:** Coins/Gems doubling (**not confirmed**); stacking of mastery/XP multipliers; material vault overflow, partial inventory, portable rune bonus and exact rounding rules.

**Engineering:** Validate and persist each legitimate XP grant **immediately** with an XP grant ID and run ID (two categories: player XP/mastery XP). Track cumulative **base XP earned in this run** separately from lifetime totals. At the server-authorized center animation transition, lock those run totals with the material snapshot and issue an idempotent receipt granting **bonus XP equal to already-earned run XP** for each category. If saving is delayed, protection and owed receipt still apply. A repeated remote, rejoin or journal retry never grants another center bonus; an ordinary exit/death still leaves earlier XP intact. Preserve XP milestones applied both before and after a center extraction; avoid double-awarding one-time milestone perks/cosmetics.


### 9.4 Vault/transaction guardrail — Proposed

Treat extraction hold, protected animation, death, ordinary leave, maintenance kick and item pickup as competing **server-authoritative** transitions. Lock exact item IDs at animation start and create a recoverable receipt before allowing safe disconnect. The server decides the protected animation state; a client-side animation alone is not proof of successful extraction.

### 9.5 Remaining extraction questions — Open

**Confirmed:** 120-second shared timer per fixed exit; free combat/movement/healing during countdown; eligibility only at expiry; large-radius audiovisual alerts; group extraction, rare 30-second anywhere rune and protected animation/lobby return. **Center Crater extraction doubles every material stack (including rare reagents) AND all player/mastery XP earned in the current run**; XP and mastery earned before any extraction **remain saved even if the player dies**. **Open:** Radius, public stranger eligibility, activator-death effects, cooldown, active POIs, portable rune boundary, Coins/Gems multipliers, material overflow, partial banking, central portal during Guardian battle and crash recovery.

## 10. Coin shops, extraction resale economy, currencies and storage

### 10.1 Income and shops — Confirmed Q116–125

| System | Decision | Remains Open |
| --- | --- | --- |
| **Coin sinks** | **NPC shops must sell items**; consider food, medicine, seeds, arrows, beginner gear, cosmetics, maps and safe crafting services as *proposals only* | Actual catalog, prices, other Coin utilities |
| **Coin quests** | Easy **250**, normal **1,000**, hard **3,000 Coins** as current initial targets | Quest repeatability and exact tuning |
| **Extraction rewards** | **No Coins simply for extracting**; items/materials have **NPC sell value** | Potential opt-in auto-sale of useless materials |
| **Center portal** | **2× eligible materials and run XP only**. **No Coins multiplied**; no Gem payout bonus | Material/XP eligibility/overflow |
| **NPC merchants** | **Fixed sell quotes**, not dynamic market pricing; can buy common or rare materials, monster drops and crafted gear | Per-item prices and location |
| **Gem rewards** | **~25 Gems** as a starting point for a meaningful quest/milestone/achievement/rare encounter grant; actual amounts vary | Tables by source |
| **Coin-to-Gem exchange** | **Undetermined**; reconsider after Coin sinks/Gem acquisition are balanced | Existence and conversion rate |
| **Currencies** | Coins/Gems **persist and never drop**; active-hour target remains **~10k Coins and ~100 Gems**, not passive wages | Inflation and realized earnings |

**Possible auto-sell:** Only explicitly flagged **otherwise-unused** materials might be automatically sold on extraction, with clear user permission and settlement receipts. **This is Proposed, not yet enabled**. Normal extracts must not pay extra Coins nor unexpectedly delete rare conversion reagents.

**NPC shop Coin ideas to evaluate:** (1) essential first-run food/medical/arrow restocks, (2) basic seeds and farm supplies, (3) cheap tools/entry-level equipment, (4) aesthetic decorations and tribe banners, (5) optional world-navigation aids/crafting service charges, (6) cosmetic dye and personalization. Pricing should avoid making harvesting/crafting irrelevant or introducing direct Robux combat power.

### 10.2 Gem trading and player safety

- Direct trade **only in protected lobby**: designer-eligible items and **Gems**, **never Coins**. Basic materials cannot trade except flagged rare/Exclusive types. Permanent items can trade.
- **Q125 confirms restrictions** on Gem trading, potentially involving minimum level, limits and/or transaction fees; exact combination and values **Open**. Block alt-account laundering/scams and use server-owned escrow with two-party confirmation.
- NPC selling is not direct player trading; merchants may buy common and rare materials under fixed catalog prices.

### 10.3 Backpack, post-extraction settlement, vault — Confirmed Q122/Q126–129

- **Hotbar exactly 9 slots. Backpack starts with 50 slots.** Each ordinary material type occupies **one logical backpack slot**, irrespective of its consolidated count (numerical quantity cap remains Open).
- Secure **item/equipment vault starts with 25 slots**, +25 per upgrade, at a **constant Gem price per upgrade tier** (amount not chosen), or equivalent Robux upgrade. Robux cost constancy remains Open.
- **Secure material vault allowance ~1,000 (near-unlimited relative to backpack)**, separate from 25 equipment slots; unclear whether **1,000 total units**, **units per material**, or **material storage entries**. Keep implementation configurable and mark the precise interpretation Open.
- **On successful extraction:** Regular **ordinary materials automatically transfer to safe material vault storage**, with center portal's valid ×2 quantity. **Weapons, tools, other items and special materials remain in a protected lobby backpack**, where the player may manually deposit desired items into the safe vault.
- **Important:** Center 2× applies to extracted **special materials** even when those remain in lobby backpack awaiting a manual vault deposit. Distinguish material bonus computation from automatic deposit destination.
- **Open:** Exact item categories automatically banked, handling of capped backpack/material vault or overlarge 2× award, whether unvaulted lobby backpack survives account logout and across subsequent re-entries, and how the player is prompted to store risky items before their next expedition.
- **Strong engineering requirement:** No successfully extracted item should disappear due to full vault or a failed settlement. Server-owned inventory receipts reserve item IDs/stack credits, temporary pending escrow and user-visible recovery state; no duplicated accounts/loot on retry.
- **Account-safe vault always persists** across world wipes. A lobby backpack is only definitely **protected while in secure lobby**, not a substitute for the explicit vault forever under an unapproved policy.

### 10.4 Monetization and Premium XP — Confirmed Q123/Q150

- Meaningful premium-equivalent purchase can take roughly **10 active gameplay hours** of currency/material earning; scale shorter for small beginner cosmetics and longer for major prestige offers. Test actual player retention, don't force a single price.
- Robux offers **only quality-of-life or faster progression**, never sell direct PvP attack/armor/health benefits. Every paid feature has a gameplay-earned route.
- **Premium subscriber base +25% XP** is persistent while status is valid; **non-Premium players have no innate subscription XP baseline**.
- **Consumable temporary XP boosters are available to ALL players**, Premium and non-Premium, via the earned-gameplay economy. Whether Premium boosts **stack** with consumables and how additive/multiplicative ordering applies is **Open**; Q150 does not explicitly settle stacking.
- Exact booster strength/duration/cost, affected XP category and entitlement distinction (Premium vs other paid membership systems) still Open. Check current Roblox entitlements and paid-random-item policies before implementing Robux-supported RNG.


## 11. Player-facing interface and accessibility

**Required design surfaces — Proposed (not implemented):**

- **Lobby / vault:** Always-persistent vault inventory/capacity, Coins/Gems, XP/levels, **all eight rarity labels**, masteries, cosmetic rewards, direct trade, rebirth tokens/perks, protected loadout/transit reservation, extraction results and risk explanation.
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

Full island art, every biome, weather, extensive equipment and premium offers, **any auction house/global marketplace** (not part of confirmed direct trading), cross-server persistent bases, advanced diplomacy and playable elemental magic remain outside the initial vertical slice. Forge conversion, account save integrity, center 2× payout and basic XP/vault progression are part of core proofs.

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
| **P0** | Center extraction **2× all materials and XP** with idempotent receipts, correct vault capacity and shared 120s timing | Core extraction risk and rare material economy correctness |
| **P0** | Server population, solo/tribe sizes, and PvP rules | Map size, reward access, balance and performance |
| **P1** | Click melee, slow bow projectiles and crafted arrows, sprint-only stamina, crouch, instant medical cooldown, partial food HoT interruption | Launch PvP readability and mobile input; **no player magic, dodge-roll or gear wear in MVP** |
| **P1** | Totem radius/overlap ownership, ~4–6-minute unclaimed decay, accessible storage and any-time tool raids | Totem shields against decay only, never raids; radius/claim priority Open |
| **P1** | Weighted event tick/rarity, public announcements, biome-random spawns, ritual/event/structure boss resets and level/gear scaling | Event variety, server fairness, contestable loot, scalable performance |
| **P1** | Biomes, distances, terrain elevation, portals and spawn points | World prototyping and movement |
| **P1** | Special Forge levels/discoveries, rare material sources, medical/food/arrow crafting and post-death Permanent upkeep if adopted | Cross-run progression with **indefinite ordinary equipment lifespan** |
| **P1** | Persistent Coins/Gems, eight rarity tiers, direct-only item trading, permanent mastery buffs and rebirth tokens/perks | Account progression and fair earnable premium choices; balance Open |
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

### 16.8 Ordinary crafting locations and quality rolls (Confirmed Q103/Q105)

- **Basic recipes** work **anywhere**, without a station; the first useful equipment set should take **10 minutes or less** in a normal initial expedition, using a few harvested ingredients. What constitutes the “first set” is Open.
- **Advanced gear** requires **workbenches**. Craft in the **dangerous public world** for an opportunity at **slightly better quality/stat rolls** (enhanced by higher Crafting mastery), or use **secure lobby workbenches** for the **default item quality**, without the dangerous field station's roll bonus.
- Each piece has an **immutable catalog rarity**, not a randomly chosen rarity. Minor **quality rolls vary between separate instances of the exact same item**, even if they have the same item name/rarity.
- Server validates station, recipe, input provenance, allowed quality stat variance and the player's mastery; never trust client-selected stats. Raw materials remain at risk in the active world.
- **Ten arrows per craft**; upgraded arrows use higher-tier inputs and may deal more damage. Exact ingredients/range/damage and inventory constraints remain Open.
- **Permanent conversion** still requires designated eligible gear and expensive **extracted vault inputs**; binding preserves whatever small stat roll the original item had, and adds no new damage multiplier.

## 17. Permanent gear: death protection and ownership transfer

> **Confirmed:** Certain **designated** extracted item types may be made Permanent using costly materials from **multiple** sources and recipes gated by player leveling and discoveries. Permanent conversion **does not modify combat stats** relative to the selected source gear. A Permanent item **survives its owner's death**, but if the owner **deliberately drops it** and another player collects it, it changes owner. Permanent items can also be **traded**. Neither dropping nor trading creates a duplicate.
>
> **Open:** Possible post-death material costs, simultaneous Permanent gear limit, **direct trade** venue/fees, eligible catalog and fate of unclaimed dropped Permanent gear. **Global marketplace or auction is excluded**.

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
5. **Trade paths:** **Lobby-only** direct trading allows **eligible items and Gems**, never Coins. Intentional ground drops in the active world are a separate physical looting/ownership path, not a trade UI. No global auction or market.

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
- **Confirmed revised rule:** The central portal grants **2× every material stack including rare/Keystone-type ingredients** and 2× XP. Unique equipment items/Legendary weapons remain single instances unless separately approved.
- **Confirmed entitlement parity:** No purchased advantage, item, cosmetic, private-session feature or rebirth/perk benefit should require Robux exclusively; players must be able to obtain the equivalent through earned in-game currencies/resources given sufficient time. **Open:** Which advantages are sold, their earnable pricing and how to map Roblox-native passes/private-server subscriptions to game-controlled equivalents without violating platform requirements.

### 18.3 Material sink model — Proposed

Resources exit the economy through (a) field supply/ammunition/raids, (b) secure special crafting, (c) consumed source equipment, (d) Permanent conversion, and (e) repairs/recovery. Track acquisition and sinks separately by material source; adjust source drop rates only after observing actual extracts, loss, and monopolization. Never apply arbitrary hidden wipes to the protected Permanent armory.

## 19. Launch equipment, starter crafting and Permanent eligibility

### 19.1 Confirmed equipment families and slots (Q100–104)

- **Four weapon families for launch:** **Spears, Daggers, Swords and Bows**, along with basic harvesting tools/rock attacks. No shields or player-cast magic.
- **Three armor slots:** Head, Chest, combined Legs/Boots. The armor EHP calculation and indefinite equipment lifespan remain intact (§21.5).
- **Small resource catalog first:** Wood, stone, iron, fiber, hides, food/herbs and a small roster of creature/event ingredients are candidate starters; the actual launch item/material list and biome sources require approval.
- **Fixed rarity by item type**, e.g. “Rare Iron Sword” vs “Common Stone Sword”; no random Rare/Epic roll of the same sword. Instances of an exact archetype may roll **small quality/stat variations**.
- **Basic items are craftable anywhere**; advanced equipment uses a workbench. World workbenches offer **better minor quality-roll chances** at higher Crafting mastery; lobby workbenches use default quality.
- **Every arrow recipe yields 10 arrows**. Stronger arrow recipes may require stronger materials and deliver increased damage.
- **Starter pace:** A few raw materials per beginner recipe, **approximately ten minutes or less to craft the first gear set**. Exact contents/costs remain Open.

### 19.2 Sample nonmagical recipes — costs Proposed

| Recipe | Illustrative ingredients | Confirmed constraints |
| --- | --- | --- |
| Basic Wood Spear | Wood, fiber | Simple any-location starter craft |
| Stone Spear | Stone, wood, fiber | Ordinary melee equipment, playtest ~25 raw hit damage |
| Stone Dagger | Stone, fiber | Fast short melee family |
| Common Stone Sword | Stone, wood/fiber | Catalog rarity stays Common |
| Basic Bow | Wood, fiber | Slow physical arrow projectiles |
| Arrow Bundle | Wood + fiber (improved versions use upgraded tips) | **Output exactly 10 arrows** |
| Rare Iron Sword | Iron, wood, refined materials | Separate defined Rare catalog archetype, small quality rolls at eligible field station |
| Iron Helmet / Chest / Legs-Boots | Iron, hide, fiber | Three separate armor slots, EHP multipliers Open |
| Basic / Advanced / Potion | Gathered herbs, prepared resources | Immediate HP +10 / +25 / +50, then animation cooldown |

### 19.3 Permanent conversion prototype — Confirmed pacing direction

- **Only a designer-selected allowlist of item archetypes** can ever be Permanent converted. Some special items qualify; other special items **never qualify**. Rarity alone grants no eligibility.
- Early conversion should plausibly need **a couple of successful extractions plus one rare public event**, not a guaranteed two-extraction unlock. This is the **first conversion progression target**; the rarest Permanent recipes remain substantially harder and depend on contested advanced encounters.
- Converts one eligible **vaulted gear instance** using securely extracted reagents and Forge requirements. The exact **source roll/stats are preserved**. Permanent status protects ownership on death but permits intentional dropping/theft/trading, as confirmed.
- Example source: designated iron weapon + suitable extracted common materials + reagent from a rare mob/tree/meteor event. Material counts, recipes and eligible catalog entries remain Open.
- No field crafting of Permanent gear is implied; the protected hub forge is still the conversion destination.


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

- **Click melee:** Raw hit damage starting points remain rock **5**, wooden spear **~15**, stone spear **~25**, prior to armor. **Q133 provisional attack cooldowns:** Rock **0.3s**, Dagger **0.4s**, Sword **0.7s**, Spear **0.9s**. These cadence numbers were accepted as approximate, not per-archetype locked; exact reach/animation windows, dagger/sword damage and stone-vs-wood spear differences remain Open. Melee spends no stamina.
- **Bows:** **Both bow and arrow tier contribute to arrow damage**. Projectile is deliberately slow and follows a **slight gravity arc**. Holding fire **pulls back/charges the bow animation**, increasing arrow launch strength/range with longer held duration; **damage stays unchanged at any draw duration**. Shorter holds result in less travel distance, not reduced damage. Exact hold minimum/maximum, launch speed/flight distance formula, bow+arrow damage combination, arrow count and client/mobile input remain Open. Shooting consumes no stamina.
- **Sprinting:** At full stamina a player can sprint **3 continuous seconds**. From empty to full, stamina **recovers in 5 seconds**. Only sprint spends stamina; regen delay/partial-sprint behavior, pace and speed remain Open.
- **Crouching:** Low profile/stealth/movement choice; does not consume stamina. Sprinting and crouch interactions are implementation choices.
- **Medicine:** Basic **+10 HP** with **0.5s animation**, advanced **+25 HP** with **1.0s animation**, potion **+50 HP** with **1.5s animation**. Healing applies **immediately**, then the animation is the **ONLY cooldown**; another medical use is prohibited until animation completes. The server blocks replayed/parallel remotes, including latency abuse. No additional hidden cooldown.
- **Food:** Full meter decays in **5 minutes**; below **25%** gives **−10% speed**. **Accepted starter food examples (Q137):** Berries replenish **10% of hunger and heal 10 HP over 10 seconds**; Cooked Meat replenishes **35% hunger and heals 30 HP over 10 seconds**. Actual launch recipe/catalog still subject to naming. Each damaging hit halves pending food healing; if new remaining heal ≤10 HP, cancel it entirely.
- **Armor:** Armor modifies **effective HP (EHP)** using a multiplier, not direct flat damage reduction: **EHP = current HP × armor factor** and damage applies to EHP; convert back to displayed actual HP (§21.5). Early armor multipliers are slightly different but visibly useful. Equipment remains indefinitely durable; magical/special resistance is future-only.
- **No player magic/shields:** Skeletons, elementals and other mythical adversaries remain enemy content; magic attacks, magical barriers and dodge/stamina combos are out of launch scope.

### 21.2 Downed and revival tactical balance

- A **solo non-tribe** character reaching lethal HP dies and is ejected to lobby; their body remains on the island 10 minutes.
- A **tribe member** receives a **60-second** downed window. A valid tribe revive interaction **pauses** this timer; cancellation **resumes remaining time**. Death/ejection occurs if unpaused time is exhausted.
- **Confirmed:** Revive takes **10 continuous seconds**, which pauses the **60-second bleed-out timer**; interruption resumes time remaining. Tribe character has **20 downed HP** at normal 0 HP; enemies can **finish at any moment**, requiring armor-adjusted damage sufficient to exhaust that pool. **Open:** normal HP restored on revival, reviver interruption/crawl/finishing UI. No revival after final death/ejection in same world.
- Tribe cap is **8** and all worlds remain PvP-enabled except explicitly protected POIs. No respawn in the same world, including from beds.
- Social implications: tribe members must eventually extract and return to lobby to regroup with a dead comrade. There is no short death → sprint back → corpse-loot loop in that instance.

### 21.3 Equipment and long-term progression

High-value gear improves outcomes through ordinary damage/range/armor/rarity differences, but **making the item Permanent does not grant extra stats**. Resource harvesting, level-gated/discovered recipes and multi-source special crafting drive progression. Raiding can occur any time with basic damage tools, so no time-based "unraidable" window. Farmers/builders can establish persistent-in-world holdings until the last player leaves; totem-protected structures resist *decay*, not PvP.

### 21.4 Encounters and balance telemetry

Measure melee duel duration, arrow velocity readability, damage accuracy under mobile latency, sprint duration, medicine-use cadence, food HoT completion after repeated attacks, successful revives (incl. paused timers), tribe versus solo survivability, raid time against wood/stone/iron and event reward extraction rates. Bosses scale by an average **player level or gear level** population signal, with anti-exploit normalization yet to be designed. The Guardian's original 15–20-minute timing stays as a separate established concept.



### 21.5 Additive piece-based EHP armor — Confirmed Q132/Q136

**Confirmed EHP targets for FULL THREE-PIECE matching sets** (Head + Chest + Legs/Boots), based on 100 base HP:

| Armor set | Full-set EHP factor | Base-HP EHP | Increment vs unarmored |
| --- | --- | --- | --- |
| Unarmored | **×1.00** | 100 | 0 |
| Hide | **×1.20** | 120 | +20% |
| Wood | **×1.50** | 150 | +50% |
| Stone | **×1.80** | 180 | +80% |
| Iron | **×2.00** | 200 | +100% |

**Pieces add their armor factor contributions**, rather than multiplying each other. Let each worn head/chest/combined-legs piece have server-catalog armor increment \(a_i\) above the unarmored baseline; \(A = 1 + a_{\mathrm{head}} + a_{\mathrm{chest}} + a_{\mathrm{legs}}\). For a complete matching set, contributions add to **0.20, 0.50, 0.80 or 1.00** respectively. **Open:** Allocation across the three pieces (equal shares, chest-weighted or another distribution) and mixed-tier piece stats. Never apply the full-set ×2 Iron factor to each separate Iron piece.

For normal current HP \(H\), \(E=H A\); a raw damage hit \(D\) produces \(E'=\max(0,E-D)\) and **actual HP \(H'=\max(0,E'/A)\)**, clamped to current valid maximum HP. This is armor-scaled EHP, not a per-hit flat defense stat.

**Revival Q136:** The revived player receives **10% of their current maximum EHP**, not 10% of a fixed 100. Compute \(E_{\mathrm{revive}}=0.10 (H_{\max} A)\) and convert back to displayed actual HP as \(H_{\mathrm{revive}}=E_{\mathrm{revive}}/A = 0.10 H_{\max}\). Example: 100 max HP with full Iron (A=2) → 200 maximum EHP → 20 revived EHP → **10 actual HP**. Upgraded max HP 150 with Iron → 300 EHP → 30 EHP → **15 actual HP**. This avoids inadvertently granting extra armor-multiplied healing twice.

**Downed state unchanged:** At normal 0 HP, tribe member enters separate **20 downed actual HP**, armor still applies. Enemies can finish downed players by consuming its EHP; 10-second valid revive pauses the 60-second bleed-out timer. No invulnerability assumed after revival.

**Open:** Piece weighting, armor mitigation from mixed sets, decimals/UI rounding, health upgrades and mastery buffs, temporary armor swaps during PvP, equipment roll ±5% application to EHP and per-hit minimum raw damage.



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

### 22.1.1 Fixed backpack/hotbar and consolidated resources — Confirmed Q108

- **Hotbar contains a fixed number of slots**. **Backpack also has a fixed number of slots**; exact counts remain Open.
- **All units of the same resource type appear as one logical consolidated stack** in the backpack UI (e.g., one Stone entry with a single quantity) for simplicity, rather than dozens of duplicated Stone icons. Exact underlying maximum quantity, whether hidden sub-stacks are required for implementation, carry limits, and over-capacity behavior are Open.
- Weapons, tools, armor and other **unique gear instances remain individually distinguishable** because their rarity/catalog types and minor quality rolls may differ. Consolidated raw material stack behavior must **not** merge differently rolled swords or duplicate Permanent instances.
- **Three equipped armor slots:** Head, Chest and combined Legs/Boots. **No shields**.
- **Vault uses a separate upgradeable capacity** beginning at 25 slots with +25 each purchase; do not confuse those secure slots with live backpack slots.
- **Coin and Gem balances are account UI balances, not world inventory slots**; they do not drop at death and Coins are not player-tradeable.

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
| **ProfileService** | Session locks, schema upgrades, revisions, **persistent vault/Coins/Gems/XP/masteries/rebirth entitlements**, protected extraction and maintenance recovery | Saved/pending/recovery status, currency, level and perk state |
| **ItemCatalog** | Definitions, valid tags and input/output restrictions | Static icons/descriptions/stats for display |
| **InventoryService** | Fixed-count hotbar and backpack slots, **one logical stack per resource type in backpack**, three armor slots, at-risk/lootable items and valid server pickup/craft transfers | Hotbar, backpack and gear UI; aggregated resource quantities |
| **VaultService** | Always-persistent inventory, **initial 25 secure slots +25 per validated Gem/Robux upgrade**, withdrawals and 2× Center material bonus receipts | Slot used/max, tier, Gem/Robux price and secure totals |
| **ForgeService** | Anywhere basic recipes, **in-world workbench quality-roll bonuses**, lobby default-quality workbench crafts, higher mastery influences *minor* field roll odds, extracted-only Permanent conversion | Preview, quality/probability disclosure where applicable, costs and crafted arrow output of 10 |
| **PermanentEquipmentService** | One canonical owner, death retention, manual drops, theft pickup, trade escrow and optional recovery | Current owner, transfer receipt, tentative repair/slot status |
| **LoadoutService** | Safe cross-place loadout reservation, active-only withdrawal, configurable Permanent slot limits and validation | Safe menu equipment preview and risk labels |
| **ExtractionService** | Server-shared 120s fixed or 30s portable timer; end-of-timer presence snapshot, alerts and protected animation | Shared countdown, deadline zone and verified individual receipt |
| **CombatService** | Rock/wooden spear/stone spear raw damage targets (5/~15/~25), server EHP/armor and variable max HP, 20 downed HP and armor-adjusted finishing, 10s tribe revive, crafted arrows, 3s sprint/5s recovery, 300s food drain/low-food slow, instant medicine 10/25/50 and 10s food HoT cutoff | HP, stamina/food, downed/revive UI, post-heal cooldown and hits |
| **BuildingService** | Booga Booga construction; wood/stone/iron tier, **tribe totem claim**, unclaimed decay, accessible storage and any-time ordinary-tool raids | Build previews, visible totem coverage, structure HP/decay |
| **EventDirector** | **~5-minute non-Guardian weighted checks**, allow spatially separated concurrent events, 2-minute ordinary node respawn, one-time rare resource spawns, publicly announced biome-valid events | Event broadcast, map locations and spatially valid cues |
| **BossService** | Guardian phases/drops and ritual/event/structure bosses; **archetype base difficulty plus population-based scaling** (source/formula Open) | Announcements, baseline encounter difficulty and contested drops |
| **AnalyticsService** | Currency faucets/sinks, mastery milestones, rebirth token spend, paid/free entitlement parity, rarity sources, rare 2× extraction and abuse counters | Verified activity rewards and progression diagnostics |
| **ProgressionService** | **Persist general and mastery XP immediately as earned**, per-run grant ledger, death-proof progress, milestones and idempotent center run-XP bonus | Live XP/mastery, center bonus and saved account state |
| **CurrencyService** | Coins from quests/merchant sales/extraction, Gems from quests/milestones/rare resources/events/rebirth/Robux, **death-safe currencies**, server-verified merchant buy/sell and premium parity | Balances and approximate earn routes (working targets 10k Coins/h, 100 Gems/h) |
| **DirectTradeService** | **Protected-lobby-only** atomic trades, **eligible items and Gems only; reject Coins**, specific rare/Exclusive material allowlist, Permanent owner transfer | Two-party locked confirmation; allowed item/Gem-only offer |
| **RebirthPerkService** | Server-validated rebirth preview/commit, **token grants, perk purchases** and exact authorized reset terms | Rebirth overview, token balance, perk costs and caps |
| **DepartureService** | Active-run departure/body + 600-second TTL, safe lobby/pre-spawn menu, protected extraction and maintenance exemption | Risk warnings, safe pre-spawn state, body and recovery status |
| **WorldAdmissionService** | Protected loading/menu, profile/world readiness, safe transit reservation, successful Play/spawn risk activation | Play/loading status, retry/return, clear risk transition |

All persistent crafting and extraction grants happen on the **server**. Client may request an action but cannot dictate rarity, cost, exact output, reward source, success flag, or timestamp.

### 23.2 Versioned profile structure — Proposed

| Field group | Representative fields | Constraints |
| --- | --- | --- |
| Profile envelope | schemaVersion, profileRevision, sessionLease, lastCommittedOperationId | Migration/backward compatibility and stale-write checks |
| Vault stacks | itemCatalogId → safe integer quantity, slotId | Nonnegative, server-calculated, **25 starting secure slots** with +25-tier upgrades and safe overflow reconciliation |
| Vault instances | instanceId → catalogId, catalogFixedRarity, **minorQualityRoll**, sourceStation, craftingMasterySnapshot, acquisitionId | Unique IDs, **no equipment wear**, tiny server-authorized quality changes within one archetype |
| Permanent equipment | instanceId, catalogId, **currentOwnerId**, location, affixes, recovery, activeLease, ownershipVersion | Death-protected while held, but transferable by intentional drop/pickup or validated trade; no duplicates |
| Recipe unlocks | recipeId, unlockSource, unlockedAt | Server-derived achievements |
| Crafting operations | operationId, recipeVersion, status, sourceId, inputs, outputId | Pending/committed/failed reconciliations |
| Extraction receipts | receiptId, runId, portalId, baseMaterialStacks, **centerMultiplier=2**, bonusStacks, runGeneralXPEarned, runMasteryXPEarned, **centerBonusGeneralXP**, **centerBonusMasteryXP**, settlementStatus | One center bonus equal to current-run previously earned XP per category and double materials; no unique gear duplication |
| Player choices | pinnedRecipeIds, safe loadout, cosmetic choice, camera preferences, hotbarBindings | Client preferences validated; fixed hotbar/backpack size and three equipment armor slots |
| Persistent currency | coins, gems, currencyGrantLedger, **npcSaleReceipts**, purchaseEntitlements | **Never drop on death**; reject Coin trades, allow safe-lobby Gem trades, verify merchant sales and paid purchase grants |
| Progression | level, xp, masteryTracks, appliedMilestones, permanentModifiers, **xpGrantLedger(runId,grantId,category,amount)**, **perRunEarnedBaseTotals** | XP/mastery awards persist immediately, survive death and are matched by a once-only center bonus |
| Rebirth/perks | rebirthCount, rebirthTokens, ownedPerks, committedRebirthOps | Explicit owner-approved reset policy, unique token/perk operation IDs and anti-double-grant |
| Trade records | directTradeId, participants, lockedOffers, eligibilitySnapshot, outcome | Two-player atomic intent and idempotent cross-profile settlement with compensation/recovery |
| Rarity catalog | Common, Uncommon, Rare, Epic, Legendary, Mythic, Secret, Exclusive; **fixed archetypeRarity**, itemTradeEligible, resourceTradeEligible, minorRollRange | Rarity is defined by item type, not an instance-randomized rarity; material trading explicitly allowlisted |
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
| Central bonus creates intended extra rare materials | **Allow exactly one 2× award per qualifying receipt** (including rare crafting reagents) and **2× XP**; reject further grants from retry |
| Direct trade attempts non-eligible common raw material | Reject server-side even if both players confirm; only catalog-approved rare/Exclusive resources trade |
| Direct trade interrupted between two players' writes | Trade escrow and compensating state must recover to one settled ownership outcome, no double item/currency grant |
| Currency purchase and milestone double submit | Unique grant/purchase operation, authoritative persistent Coins/Gems/XP/mastery balances and once-only rewards |
| Rebirth grants repeat tokens or resets stored gear without approval | Idempotent rebirth transaction and explicitly previewed reset policy; no accidental vault deletion |
| User must pay Robux for promised earnable feature | Equivalent in-game Coin/Gem/resource entitlement or platform-compliant game-managed access path must exist before release |
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

Show (a) rune/portal and completion, (b) **base material stacks + legitimate 2× Center Crater bonus quantities where applicable**, including rare materials, (c) unique equipment instances separately with no unapproved copies, (d) **base and doubled XP** breakdown, (e) recipe and mastery milestone progress, (f) next action. If persistence is pending, display pending, not saved.

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

### 25.4.1 Updated inventory, merchants, world workbench and trading UX (Q90–110)

- **Hotbar fixed-slot strip**, separately capped backpack grid, **one icon/entry per raw resource type with total owned count**, and visually separate individually rolled equipment.
- Gear screen has **Head**, **Chest**, **Legs/Boots** armor slots and primary weapon families Spears, Daggers, Swords and Bows. Shield slot does not exist.
- **Vault:** shows **25 starting slots** and each **+25 capacity upgrade**; present side-by-side earned-Gem and Robux choices, identical capacity effects, actual current server-trusted prices, safe overflow/pending states.
- **Lobby trading:** Gem wallet plus catalog-approved eligible items (including explicitly enabled rare/Exclusive materials). **Coin balance cannot be added** and no active-world trade button exists. Show both offers, confirmation and cancellation protections.
- **NPC merchant:** show quote for materials, rare/event reagents, creature drops and crafted gear; rare ingredient sale should have a strong warning since it could be needed for Permanent crafting.
- **Field vs hub workbench:** Default gear quality in lobby, chance of **small improved stat rolls** in unsafe world crafting; higher Crafting mastery modifies eligible chances. Preview probabilities if randomized products are indirectly purchasable using Robux-funded Gems, and validate current Roblox paid-random-item rules.
- **Premium XP:** clearly show subscription-eligible +25% XP benefit and an **earnable equivalent**, without selling direct PvP damage/armor boosts for Robux.
- **Upgraded arrows:** show **10 produced each craft**, tier-specific ingredients and improved arrow damage.
- **Extraction:** clear summary of whether center 2× has been earned, and separate run-earned XP, credited XP and conditional successful center bonus.

### 25.5 First-session tutorial beats — Confirmed direction / Proposed sequence

**Confirmed:** Tutorial and guided quests are required as the first-player introduction, along with user-adjustable camera. Proposed learning order: random-map spawning and safe pre-spawn Play → health/food/sprint stamina → gathering and craftable arrows → instant medicine/food HoT → tribe revives/raid risk → weighted public event cues → shared 120-second extraction (center grants **2× all materials/XP**) → always-saved vault → Coins/Gems, rarity, special recipes, mastery and later rebirth tokens. Never hand out free Permanent gear merely for opening tutorial. Exact rewards/skippability/Open PvP-safe training design remain Open.

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

1. Secure extraction deposits correct material/equipment stacks once; death before protected animation deposits **no loot**, but **always retains legitimately earned general XP and mastery progress**.
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
13. Center Crater payout intentionally doubles all extracted materials and awards **bonus general and mastery XP equal to all current-run base XP already saved**; death/ordinary leave retains those base XP records but no center bonus. Retries never double again; unique equipment instances stay single.
14. Cache requires a continuous 60-second unlock under specified interruption rules; event UI and world beacon agree.
15. Reject impossible melee reach/rate, forged slow bow/arrow counts, **wrong armor/EHP damage**, impossible medicine healing +10/+25/+50, food HoT 10s/cutoff exploits, forged revive and downed state, bogus food/stamina updates and malicious remotes; no player magic at launch.
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
31. After public world becomes empty, **all securely vaulted ordinary/rare items and earned Coin/Gem/XP/mastery/perk records remain unchanged**.
32. A central receipt of N rare materials grants **2N material stacks** and **2× eligible XP once**; normal or portable exit does not silently inherit the center bonus.
33. Coin and Gem amounts cannot be forged; earned Gems, cosmetics and entitlements survive world reset.
34. Direct trades reject ineligible common materials, exchange allowed designated rare/Exclusive materials and Permanent gear once, and survive disconnect/timeouts safely.
35. Mastery milestone bonuses and cosmetics are permanent, bounded, once-only and not earnable indefinitely through idling, alt fights or craft-cancel spam.
36. Rebirth token grants/purchases require validated eligibility/confirmed reset semantics and idempotent commit; no unapproved vault wipe.
37. First-time guided tutorial and adjustable camera work for keyboard/touch/controller and unpredictable random world spawn; paid offers have gameplay-earned equivalents.

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
4. **Confirmed:** Permanent equipment can transfer through deliberate ground drop/pickup or **direct player-to-player trade**. No auction/global market. **Open:** Gift UI, trade safeguards and unclaimed drop fate.
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
14. **Confirmed:** Guided tutorial/quests, adjustable camera, enhanced primitive visuals and in-game currency routes to all paid benefits. **Open:** Content, platform native offer mechanics and exact fees.

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

- **Tribe claim totems:** Nearby player-built structures resist natural decay, not raids. **Totem areas can overlap**; radius depends on map size. Without valid totem, full decay takes **~4–6 minutes** under Q114 working interpretation; conflict priority/duration semantics Open.
- **Takeover:** A deserted base may be occupied by a different group even if its original owners left. Replacing/destroying claim totems and transferring structural ownership need a ruleset; unclaimed storage is already accessible to anyone.
- **Storage:** **All players can access world storage** once they can reach it. A locked chest concept must not override this rule. Terrain/building walls may prevent physical access until raided.
- **Farms:** Crops and planted trees grow **as long as that server is populated**, even after the farmer leaves. When the world empties, plants, buildings and all other world state disappear.
- **Structure sources:** Server-generated ruins, outposts and structures remain world-owned, **never** claimable through a tribe totem. They may be raided and looted.
- **Breach:** Standard weapons/tools can damage structures; rare siege tools may accelerate breaches but are **not required**.
- **PvP:** Enabled everywhere except specifically designated safe POIs. Totems are not safe-zone anchors, and no ordinary player base grants PvP immunity.
- **Build exclusions:** Keep confirmed fixed-extraction **50-meter no-build auras**. Portable-rune placement interactions remain a later balance decision.

### 32.3 QA gates

Verify biome randomness, event public announcements, weighted distribution, 8-member tribe maximum, tribe claim scope excluding server-generated structures, decay start/stop based on totem proximity, persistent-in-live-world abandoned bases, no-respawn beds, accessible public storage, any-time ordinary-tool raids, and farming continuing after owner exit while other players keep server alive. All resets must discard temporary world objects once its last player departs.


## 33. Five permanent masteries, levels and milestone buffs

### 33.1 Five launch tracks — Confirmed (Q71–80)

**Only five masteries:** **Mining, Woodcutting, Farming, Crafting and PvP**. Building, raiding, hunting, exploration and tribe support remain possible activities and quest/XP sources, but are **not independent mastery tracks** unless approved in a future update.

| Mastery | Verified milestone activity (proposed counting details) | Buff direction and rewards |
| --- | --- | --- |
| **Mining** | Authentic ores/nodes mined and mining objectives | **+1% per mastery level** to suitable mining/resource yield; cosmetics |
| **Woodcutting** | Trees legitimately chopped, varied wood harvested | **+1% per level** to suitable wood yield; cosmetics |
| **Farming** | Crops planted, matured and harvested | **+1% per level** to eligible crop output; cosmetics |
| **Crafting** | Legitimate completed crafting actions and achievements | **All of:** ingredient efficiency, craft output/batches, crafting speed and recipe unlocks, balanced by level |
| **PvP** | Real opponent combat, kills and contested objectives | **Both** minor combat and noncombat perks (e.g. loot/coins/utility), plus cosmetics |

**Confirmed:** Mastery level **cap is 10** for now. Each mastery level grants a **buff**, and the player advances through meaningful **milestones**, not merely passive hours logged in. **+1% per eligible level** is the baseline for resource-yield buffs (at ten earned +1% increments, an illustrative cap of **+10%**). This does **not** automatically mean +1% raw PvP damage or every crafting stat per level; precise perk catalogs, milestone thresholds and tier associations remain **Open**. Mastery levels, buffs and cosmetics remain **permanent account progress** across world reset, death and rebirth.

### 33.2 Milestone progression, XP and visibility

1. Track verified milestone counters by category (ore mined, trees cut, crops harvested, items crafted, meaningful PvP). Milestones determine mastery levels 0–10. Exact counts and whether level starts at zero or one are Open.
2. Apply **a permanent buff at each newly earned level**, with a once-only milestone entitlement ID. Cosmetics, titles, visual effects, animations and decorative structures can also be milestone rewards (Q79).
3. **General XP and any independently awarded mastery XP** still save immediately, including on death; center extraction adds the run's XP again on success (Q69/Q70). **Doubled XP does not fabricate additional underlying mastery actions.** One mined ore stays one mined ore in the milestone counter, even if extracting centrally doubles XP.
4. If milestone thresholds are ever implemented based on mastery XP rather than actions, the exact way center XP affects progression is **Open**. Confirmed preference remains *milestone progression* and **10 levels**.
5. **Mastery levels/titles may be visible in the protected lobby** (Q80); exact profile/overhead UI and privacy options still need design.
6. Prevent AFK progression, PvP alt-account farming, repeating refunded crafts, illegitimate harvests and bot-generated action floods; verify milestone triggers on the server.
7. Farming/mining mastery may grant increased resource yield, yet even fully specialized peaceful play cannot itself craft **the rarest Permanent equipment** without high-risk ingredient requirements.

### 33.3 Both additive and multiplicative buffs — Confirmed category distinction

**Confirmed Q78:** The game includes **specific additive** and **specific multiplicative** modifiers. Each buff/perk must declare its operation, source, magnitude and stacking cap. Proposed general example:

    finalGatherYield = floor(baseGatherYield × (1 + sum(additiveBonuses)) × product(multiplicativeFactors))

For illustrative, unapproved perk values only: base 100, +10% mastery and ×1.2 rebirth perk means **132 gathered resources**. A subsequent **Center Crater extraction doubles the legitimately carried material stacks to 264**. These are examples of **ordering**, not approved rebirth multiplier stats or item outputs. Count the actual harvesting *action* once even if subsequent extraction doubles the carried stack.

**Open:** Exactly which modifiers count as additive or multiplicative, rounding, max multiplier, PvP armor/attack stacking and whether XP buffs affect milestone progression.

### 33.4 Persistence and playtest tests

- Verify five and only five launch mastery tabs, each cap level 10 and buff per level; permanent cosmetic entitlements and lobby display.
- Simulate death, world wipe, safe maintenance kick, protected extraction, rebirth and server change; unlocked mastery buffs/cosmetics survive all of them.
- Test exact 1%-per-level resource yield increments where relevant, +10% illustrative level-10 bonus, plus independent additive/multiplicative perk categories and center 2× materials/XP.
- Test crafting mastery supports all four benefit families at catalog-chosen milestones; PvP mastery includes both bounded combat and noncombat progression.
- Prevent replayed milestones and repeated resource/kill/XP awards; no bonus XP may silently mint twice as many verified tree cuts, PvP kills or harvested crops.



## 34. Owner-approved answers 1–24 (2026-10-21)

These answers supersede earlier proposals where conflicting. Specific balancing values and ambiguities explicitly left undecided are **Open**, not silently decided.

### 34.1 Server, world and death (1–7)

| Number | Owner decision | Status and necessary detail |
| --- | --- | --- |
| 1 | Target **30 players** per island | Provisional; refine based on map size and performance |
| 2 | A public world **resets only after its final player leaves** | Confirmed; no scheduled wipe while populated |
| 3 | Entire **live island** wipes when empty; **every item already deposited in the separate vault ALWAYS persists**, ordinary or Permanent | **Confirmed by later clarification**; no account-vault wipe |
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

**Final Q3 clarification (2026-10-22):** **ALL materials and equipment successfully stored in the secure vault survive every world reset, ALWAYS**. The old “only Permanent items survive” statement applies to **ordinary carried equipment when players die**, not deletion of securely deposited inventory; empty-world wipes remove live bases, farms, corpses, loose resources and unextracted loot, not account vault holdings. This rule is Confirmed and is no longer Open.

### 34.3 Extraction, portals and return (17–24)

| Number | Owner decision | Status |
| --- | --- | --- |
| 17 | Players may move **outside** the zone during countdown; must be **inside only at the exact end** | Confirmed; small extraction area |
| 18 | Timer does not pause/reset on zone exit | Confirmed consequence of shared timer |
| 19 | Combat, healing and being hit are permitted without cancelling countdown; dead players do not qualify | Confirmed |
| 20 | Large-radius audio and visual warnings alert nearby players | Confirmed; radius/VFX Open |
| 21 | A **single timer on server** applies to an extraction event; groups/tribes can share it | Confirmed; unrelated strangers using same event Open |
| 22 | Known candidate extraction POIs; **different active subsets per server**; extremely rare portable rune gives **30-second anywhere** extraction | Confirmed; item consumption, alert radius, temporary zone and abuse protections Open |
| 23 | **2× all extracted material stack quantities and 2× XP** at the Center Crater portal, **including rare boss/meteor crafting materials** | **Confirmed later**; unique gear/Coins/Gems not automatically multiplied |
| 24 | Successful extraction returns players to the **separate secure lobby** | Confirmed; not the play-world pre-spawn menu |

**Important revision:** The original “remain within extraction region for the entire 120-second hold” mechanic is **replaced**. On click a fixed portal starts its own countdown; the initiating player can hide nearby or fight, heal, leave and re-enter at will. At expiry the server collects every **alive and eligible character currently inside the region** for protected animation. A character outside by even a short distance at the finish misses the event. Damage does not reset it. Each qualifying character receives their **own** idempotent vault receipt; the portal's timer belongs to the server, not one player.

**Portable rune:** Extremely scarce one-use rewards/drops can provide a fast **30-second** exit at a player-chosen location, including locations outside predetermined POIs. Exact beneficiary group size, placement conflicts, interaction with building/raid mechanics, destruction rules and no-build restrictions need future decisions; “anywhere” and 30 seconds are Confirmed.

**Final Q23 clarification (2026-10-22):** The owner confirmed **all extracted material quantities double and XP doubles** at a successful central portal extraction. Thus 10 rare ore legitimately produces **20 rare ore** in the vault and an extraction worth 100 XP awards **200 XP**. Rare materials are explicitly included. **Single-instance equipment** is not automatically multiplied; this remains separate from raw materials. Retune rare-source economy to handle this intentional doubling; apply once per protected receipt.

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
14. **Regression requirement, now Confirmed:** An empty-world reset **never wipes protected vaulted items**. Center extraction awards exactly **2× material stack quantities (including rare ingredients) and 2× XP**, idempotently.


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
| **32** | Tribal down/revive | Tribe members have **60 seconds** of unpaused downed time; valid revive pauses countdown, cancel resumes; solo players die immediately | **Later Q68 confirmed:** revive 10 seconds, 20 downed HP, armor still applies and enemies can finish; post-revive HP Open |
| **33** | PvP and spawn | **Random spawn location anywhere on the map**; PvP enabled **everywhere**, except designated POIs with explicit safe zones | Spawn candidate validation, safe-zone list, friendly fire, spawn damage timing |

**PvP state semantics:** A living active player can be damaged inside almost any world zone, including while raiding, farming or handling extraction. Protected pre-spawn menus and post-extraction animation remain exceptions. A safe POI, if one exists, must be explicitly mapped and server-enforced; a private base/totem never creates a safe zone.

**Death outcomes:** A tribe member enters downed state on lethal damage. A valid revive may save them without triggering death/ejection. If unpaused time runs out, they die and are **kicked/sent to the separate lobby**, with no same-server return. Solo non-tribe players skip downed and go directly to death/ejection. The ordinary 10-minute world loot-body rules remain.

### 35.2 Building, tribes, takeover and farming (34–41)

| # | Subject | Design-owner answer and confirmed rule | Remaining Open specifics |
| --- | --- | --- | --- |
| **34** | Construction interaction | **Booga Booga-style** accessible building | Exact snapping, rotation and costs |
| **35** | Building objects | **Yes** to functional structures: storage, beds, workbenches, farms, traps, furnaces and core walls/floors/doors | Full launch content catalog |
| **36** | Material tiers | **Wood → stone → iron** for initial building; later tiers follow actual material additions | Structure stats and prices |
| **37** | Bases and decay | Owner-away bases remain live; totem claim regions may overlap and protect against decay. **Unclaimed structures expire in ~4–6 minutes** as initial full-lifespan interpretation | Radius, ownership conflict, decay timing details Open |
| **38** | Raiding | **Any time**, including absent owners; **no specialized raid tools required**. | Damage values and raid pacing |
| **39** | Tribe rules | Maximum **8** players; invite, kick, alliances. Tribes claim **only player-built** structures, **not generated structures**. **World storage can be opened by anyone**. | Leader succession, alliance FF, access through doors and exact claim rules |
| **40** | Respawn and regroup | **No respawn in same server**. Death sends player to **lobby**, and they must **wait for their tribe to return to lobby** to play again with that tribe's expedition. | Queuing/new-world invite and session transfer interface |
| **41** | Farming | **Yes** to planting/cultivating trees and crops; may continue growing while farmer is away if public server remains active | Growth cycles, plant categories, grief/crop harvesting |

**Totem versus vault:** A tribe totem is a **structural claim/anti-decay mechanism**, not secure storage, raid immunity or a place to revive dead players. Ordinary storage is public-accessible if reachable. Server-generated structures remain world-owned and cannot be claimed.

**Takeover:** An unguarded house does not vanish just because its owner leaves. Another player/tribe may enter, use accessible inventory and potentially take control. Exact claim-transfer procedure must be designed without violating the existing public-build and no-scheduled-wipe rules. As soon as the last player leaves the world, the entire temporary world resets, regardless of totems.

### 35.3 Weighted events, mobs and bosses (42–48)

| # | Subject | Design-owner answer and confirmed rule | Remaining Open specifics |
| --- | --- | --- | --- |
| **42** | Event cadence | Non-Guardian **weighted rolls roughly every 5 minutes**, events publicly announced, multiple spatially separate events may coexist; Guardian remains on own schedule | Q111 confirmed approximate interval; weights/spacing/concurrency Open |
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

**Retrospective Q25–48 note — superseded in part by Q61–89:** Food HoT is now **10 seconds**, hit halves pending healing with ≤10 HP cutoff, and tribe revival is **10 seconds**, after 20 armor-protected downed HP. Five level-10 mastery tracks and a rebirth level-1 reset are confirmed. **Still Open:** medical animation lengths, post-revive HP, attack speeds, armor tier multipliers, totem decay/claims, safe POIs, event weights, boss scaling, Permanent costs/slots, Coin/Gem rates, mastery milestones, rebirth perks and platform entitlement mapping.

**Owner questions 49–60 were answered on 2026-10-22**; see §36 for confirmed account economy, rarity, permanent mastery/XP, appearance, onboarding and accessible monetization. Precise numeric tuning and platform-native purchasing mechanics remain Open.


## 36. Owner-approved economy, appearance and monetization decisions (Q3, Q23, Q49–60)

> **Confirmed by owner (2026-10-22):** This completes all numbered concept questions 1–60 at the feature-direction level. Numerical tuning, technical enforcement, platform purchases and specific reward catalogs remain **Open**.

### 36.1 Complete decision registry

| # | Subject | Confirmed choice | Still Open |
| --- | --- | --- | --- |
| **3** | World resets | **ALL previously vaulted materials and equipment are ALWAYS saved**, ordinary or Permanent. Only the live island resets on empty. | Vault capacity/overflow mechanics |
| **23** | Center extraction | **2× all material stacks including rare ingredients, and 2× XP** | **Later Q69 confirms all current-run XP** (not just exit XP); whether Coins/Gems and unique gear multiply remains Open |
| **49** | Currency | **Persistent Coins and Gems**; Gems feel more premium but are **earned through gameplay too** | Drop rates, sinks, vendor prices |
| **50** | Trade mode | **Direct player-to-player trading only**, not marketplace or auction | Venue, item/currency eligibility and safe transfer |
| **51** | Rarity | **Common → Uncommon → Rare → Epic → Legendary → Mythic → Secret → Exclusive** | Drop odds, visuals, Exclusive availability |
| **52** | Player advancement | **XP, levels and crafting mastery; NO skill trees** | XP thresholds, mastery awards, level gates |
| **53** | Playstyle growth | **Five permanent mastery tracks**: Mining, Woodcutting, Farming, Crafting, PvP; level-10 cap, per-level buff, cosmetics | **Confirmed Q71–80**; milestone thresholds/effects Open |
| **54** | Mastery duration | Buffs are **permanent account progression retained after rebirth** | **Confirmed Q82**; no rebirth wipe of intended protected masteries |
| **55** | Farmer/builder progression | **Cannot earn the very rarest Permanent gear solely by farming/building** | Which high-tier encounter ingredients/requirements apply |
| **56** | Material sourcing and trades | Materials **mainly mined/gathered**, with **quests and world events**; no general raw-material trading, **except specific designer-eligible rare or Exclusive materials** | Eligible item allowlist, source/quest rewards |
| **57** | Art | **Primitive, blocky Booga Booga look** with more detail in **map, structures and equipment** | Exact style bible, palette, asset budget |
| **58** | Camera | **Adjustable camera** | Zoom limits, first-person toggle and PvP fairness |
| **59** | Onboarding | **Tutorial and guided quests** for stronger first-player impression | Skippable vs forced, quest rewards, safety |
| **60** | Monetization/rebirth | All monetized benefits have earnable alternatives; rebirth requires level and challenge, increases in cost, resets general level to 1 and grants tokens for **permanently active** perks | Actual tokens, thresholds, respec fees, platform billing and numeric perk caps Open |

### 36.2 Coins, Gems, offers and purchasing parity

- **Coins:** Core persistent currency. Candidate purchases include vault upgrades, cosmetic skins, common services and optional convenience. Actual catalog/prices and rates require approval.
- **Gems:** Higher-premium persistent currency, but **always earnable in-game** rather than solely sold for Robux. Earning rate can be slower, but the route must be achievable given sufficient playtime.
- **Purchasing-parity rule — Confirmed:** Every monetized benefit must have an **earnable currency/resource route to the same or equivalent functional benefit**, so a paying player can gain convenience faster without making essential content permanently unobtainable for a non-paying player.
- **Candidate offer families:** Cosmetics, cosmetic packs, non-exclusive conveniences, entitlement-style passes, premium memberships/features, private-session/server access and additional owner-approved categories. These are **possible offerings**, not a finalized SKU list.
- **Technical gate:** Roblox-native game passes, subscriptions and paid private servers may have platform-specific purchase/ownership restrictions. Do **not** assume Coins/Gems can literally buy a platform-native Robux entitlement. Confirm the platform rules, and if necessary implement **game-managed equivalent access** bought with earned currency to meet the gameplay requirement. No claim of implementation has been made.
- **Fairness question:** The owner allowed additional monetization beyond cosmetics. How combat-oriented perks or progression accelerators coexist with full PvP and rare contested gear must be decided; the free equivalent and bounded power are important balancing goals, not evidence that a specific paid item is approved.

### 36.3 Increasing-cost rebirths and permanent token perks — Confirmed Q81–89

**Confirmed Q81–82:** Each rebirth requires **both a general-player-level threshold and an endgame challenge**; rebirthing **resets general player level to 1**, while systems intended to persist **remain preserved**. The secure vault, owned Permanent gear, five mastery tracks/buffs, cosmetics and already purchased permanent rebirth perks remain safe. Exact treatment of unspent currencies and XP totals is Open; preserve them by default rather than deleting silently.

**Confirmed Q83–85:** Rebirth requirements/costs become **progressively harder and more expensive**. Later rebirths **may award more tokens**; whether this happens, thresholds and exact amounts remain Open. Do not invent a fixed maximum rebirth count.

**Confirmed Q86–88:** Rebirth tokens are spent on **specific always-active, permanent perks**, not equippable limited perk slots or a branching skill tree. Candidate perk types include **XP boosts, rare-drop luck/chance, loot/drop quantity and increased walking speed through water**. Some perks may have multiple upgrade ranks; others only one purchase. Item categories, caps, token costs, ranks, rarity interactions and additive-versus-multiplicative type remain Open.

**Confirmed Q89:** Players can **buy a perk respec** via **Gems, Robux, or a redemption code**. Gems are earned through play, preserving earnable parity. Exact Gem/Robux prices, code grants, refunds and Roblox native product fulfillment are Open.

**Proposed server transaction model:**
1. Validate the current level, completed endgame challenge and rising rebirth costs. Preview exact reset and retained state. **General level resets to 1; protected progress is retained**.
2. Persist one unique rebirth operation, spend approved costs, increment count and award configured tokens exactly once. Do not create double grants on retry.
3. Token purchase grants one permanently active perk (or next rank if allowed), logging source and modifier type. Effects remain permanently active except for explicit valid respec.
4. Respec route (Gem purchase, validated Robux purchase receipt or valid code) grants **one respec entitlement**. The actual respec atomically changes eligible perk selection/token balances, and cannot refund more than legitimately spent.
5. For every paid respec, an achievable **earned-Gem path** remains. No client-controlled token balance, perk stat or promo code acceptance.
6. Treat rebirth-perk modifiers as explicitly **additive or multiplicative**, with milestone mastery modifiers and the center's 2× payout composed via catalog-defined rules.

**Still Open:** Rebirth target levels/challenges, costs, number of tokens per rebirth and scaling, upper limit, Coin/Gem effect, precise XP history, perk catalog/ranks/caps, Gem/Robux respec price, code redemption and refunded token handling, and PvP balance limits.



### 36.4 Five-track mastery and rarity economy

- **Confirmed tracks (Q71):** **Mining, Woodcutting, Farming, Crafting and PvP only**.
- **Confirmed Q72–75:** Milestone-based mastery progression, **maximum level 10**, **one buff at every level**, baseline **+1% per eligible mastery level** for resource yield. Exact resource type and level thresholds are Open.
- **Confirmed Q76:** PvP mastery includes **both combat and noncombat** advantages, bounded for fairness. Exact magnitude Open.
- **Confirmed Q77:** Crafting mastery supports **all** proposed benefit types: ingredient savings, larger craft outputs, faster craft speeds and recipe unlocks; exact distribution Open.
- **Confirmed Q78:** Specific buffs/perks are **additive** and others **multiplicative**. Catalog must explicitly classify each; center portal still doubles carried materials and all run XP. It does not duplicate counted milestone actions.
- **Confirmed Q79–80:** Mastery milestones can grant cosmetics, titles and similar collectibles. **Mastery titles/levels may display in the lobby**; exact visibility layout Open.
- **Confirmed Q81–89:** Rebirth resets general level to **1** after a level requirement and challenge, with progressively harder costs; permanent perk token purchases, possible multirank perks, and **Gem/Robux/code** respec. Other saved protected systems remain preserved.
- **Rarity:** Common → Uncommon → Rare → Epic → Legendary → Mythic → Secret → Exclusive. Permanent remains a separate transferable gear property.
- **Rarest Permanent equipment:** Cannot be earned solely via passive farming/building. Rare boss/ritual/contested material sources remain gatekeepers. Acquisition through direct trade and possible special permissions stays Open.



### 36.5 Primitive art, adjustable camera and guided tutorials

**Art direction — Confirmed:** Retain the readable **blocky, primitive Booga Booga character and building language** while improving **environmental/map detail, structures, equipment and biomes**. Avoid visual clutter masking PvP projectiles, gathering nodes, totem influence, rare loot or extraction signals. Final palette/shape language, texture density, low-poly budget and reference art are Open.

**Camera — Confirmed:** The camera is **adjustable** by the user. Proposed options include third-person zoom and possibly first-person; exact boundaries, input mappings and fairness against corner-peeking in PvP are Open. Design mobile and controller affordances early.

**Tutorial and guided quests — Confirmed:** First-time users should receive a coherent tutorial and guided objectives. It must work with **random valid map spawning** and the **protected world main menu**, without quietly putting a loading avatar in danger. Suggested learning sequence:
1. Explain Health/Food/Sprint Stamina and movement/camera, then gathering wood, stone, iron and herbs.
2. Guide simple click melee, **slow craftable arrows**, instant medicine/post-heal cooldown and food healing-over-time.
3. Demonstrate structure placement, wood/stone/iron upgrades, tribe totems preventing decay and **publicly openable storage**; explain raids are possible any time.
4. Introduce tribe invites and the **60-second pauseable revive** for tribe members versus solo immediate death and lobby return.
5. Teach publicly announced weighted events, visible dangerous rare carrying, fixed extraction points, shared **120-second timer**, end-only small-area check and protected extraction animation.
6. Show the secure lobby vault and reassure that **all deposited gear/materials stay saved**, then preview Coins/Gems, XP/levels, eight rarity tiers, masteries and rebirth token perks.
7. Offer guided quests with early but balanced progression; exact quests, skips, rewards, tutorial location and whether new players get PvP protection remain Open.

### 36.6 Acceptance tests: v0.8 baseline updated by Q61–89

1. Empty world wipes **all temporary live-world state** but preserves **ordinary/rare vault items, Permanent gear, currencies, XP, mastery and entitlements**.
2. Center extraction of 1 rare ore/reagent banks **2** and awards **2× XP**. Repeated requests/reconnections **never repeat** this bonus.
3. One unique Legendary **equipment instance** remains one item, unless distinct future approval explicitly permits unique-gear multiplication.
4. Coins and Gems are saved persistently; Gems have an achievable in-game earn path.
5. In direct trade, ordinary raw material without the specific rare/Exclusive trade-eligible flag is blocked. A catalog-authorized special material and Permanent gear can transfer exactly once.
6. Each of the **eight ordered rarity classifications** appears correctly in inventory/UI/catalog where appropriate.
7. General XP and crafting/activity mastery advance separately. Reaching a legitimate milestone grants a **modest persistent buff/cosmetic exactly once**, remaining after death and world reset.
8. Farm/build mastery alone cannot manufacture the **rarest** Permanent conversion source requirements.
9. A rebirth displays an explicit state-reset preview and grants **one** verified token award; perk purchases consume tokens once, and no unapproved vault deletion is allowed.
10. Every monetized benefit has a discoverable **in-game currency/resource equivalent**. Roblox-native entitlement mappings and storefront requirements are reviewed before implementation.
11. Primitive low-poly artwork remains readable; camera is adjustable; first-use guided quests work across a randomized spawn, touch/controller and risky PvP world.
12. Admin safe-kicks, protected world admission, tribe revival, rare runes and ordinary extraction remain unaffected by the new account economy.

### 36.7 Remaining precise choices

- **Confirmed:** Center 2× applies to **all current-run player XP and mastery XP**, including XP saved before extraction; ordinary death preserves base progress. **Open:** Whether Coins/Gems also multiply, exact XP multiplier stacking and bonus interaction with other earned XP modifiers.
- Vault overflow handling when bonus stacks legitimately double and capacity is upgradeable.
- **Confirmed rebirth rules:** General level and completed challenge required, progressively harder/costlier; general level resets to **1**, protected vault/masteries/owned perks preserved. **Open:** threshold, challenge, cost curve, tokens per rebirth, optional effects on Coins/Gems and perk balance.
- Detailed Coin/Gem sources, premium earn rates, entitlement equivalence and platform purchase feasibility.
- **Confirmed mastery rules:** Exactly five milestone-based level-10 tracks, buffs every level, baseline +1% per level to applicable resource yields and both additive/multiplicative modifier types. **Open:** action-count milestones, PvP/other perk caps, crafting allocation and top-tier gear trade restrictions.
- Which exact rare/Exclusive raw materials may be traded, and whether currencies may be offered in direct trades.
- Secret and Exclusive acquisition rules, drop rates, cosmetic rarity presentation.
- Tutorial structure, safe training environment versus live-world risk, and adjustable camera bounds.


## 37. Owner-approved Q61–89: launch combat numbers, five masteries and rebirth

> **Status (2026-10-22):** This chapter is the normative owner-decision record for questions **61–89**. Values identified as tentative remain playtest starting points; exact unspecified durations and costs remain **Open**, not made-up defaults.

### 37.1 Core survival and fight balance (61–70)

| # | Topic | Owner-approved baseline | Open detail |
| --- | --- | --- | --- |
| **61** | Health | **100 base max HP**; equipment and approved upgrades can raise max HP | Bonus source/stat caps and gear interactions |
| **62** | Sprint | **3 seconds sprint on full bar; 5 seconds recovery from empty to full**; stamina used only for sprint | Regen delay, rates after partial sprint, actual sprint speed |
| **63** | Food | Full food meter **100% → 0% in 5 minutes**; **below 25% food** gives **−10% movement speed** | Refills, exact drain exceptions, zero-food additional effects |
| **64** | Instant medicine | **Basic +10 HP**, **advanced +25 HP**, **potion +50 HP**; immediately applied, then varying animation cooldowns | Each animation length, mobility during cooldown |
| **65** | Food HoT | Food-dependent total healing **over 10 seconds**. On each damage event, remaining HoT cut by **50%**; if *post-cut remainder ≤10 HP*, clear it completely | Food catalog/totals, overlapping food HoTs, tick granularity |
| **66** | Early melee | **Rock 5 raw damage per hit with high attack speed**; **wooden spear ~15** slower/longer range; **stone spear ~25** | Spear values are tentative, precise attack speed and reach Open |
| **67** | Armor | **Effective-HP multiplier (EHP)** rather than fixed reduction; early armor levels have modest but noticeable upgrades | Armor multiplier tier table, composition, max EHP |
| **68** | Revives | Tribe player downed at **0 normal HP** enters **20 downed HP** with armor retained; enemies can finish with enough damage; **10 seconds to revive**, pauses **60-second bleed-out** while actively reviving | HP after revive, revive interruption/crawling |
| **69** | Center XP | **2× ALL XP legitimately earned in that expedition** on center extraction, not just end extraction XP | Stacking with XP perks and action milestone progression |
| **70** | XP and mastery | **Always saved immediately as earned**, including when player dies; no successful extraction requirement | Save batching/technical availability (must meet durability) |

#### Food interruption examples — Confirmed rule / illustrative amounts

For an active food HoT with **40 HP remaining to be applied**, taking an attack leaves **20 pending HP**; a second attack halves the pending amount to **10 HP**, which reaches the **≤10 cutoff**, and so **no further food healing occurs**. This rule does not undo HP already restored; enemy attacks separately deal their normal armor-adjusted damage. Food healing is capped at the player's current maximum health (100 base, with valid gear/upgrade additions).

The word *overheal* in the user's description is interpreted as **unapplied remaining food regeneration**, not a shield or permission to exceed max HP. The total healing per food item varies; **every food HoT completes in 10 seconds absent interruptions**.

#### Armor mathematics — Confirmed intent with corrected units

Let the current actual health be H, and let A be the valid positive effective-HP armor factor (unarmored baseline A = 1). Then **EHP = H × A**; incoming raw attack D reduces effective health to max(0, EHP − D). **Actual HP after hit = max(0, (EHP − D)/A)**. This respects the requested EHP-based damage system while ensuring displayed/used HP units stay consistent. The downed **20-HP** pool receives the same armor factor. Hypothetical A=1.2 gives 100 HP = **120 EHP**, or 20 downed HP = **24 EHP**. This multiplier is an example, not the iron armor value.

#### XP on death versus center extraction — Confirmed / implementation rule

**Always credit base general XP and verified mastery progress as earned**, even during an at-risk run. The **center portal awards an additional bonus equal to the total legitimate XP earned within that current run**; this produces **2× current-run XP** overall without subtracting/regranting progress and without replaying milestone rewards. A failed extraction or death only forfeits ordinary **physical items**, not XP/mastery already stored.

**Confirmed later Q72:** The five mastery tracks advance on meaningful **milestone action criteria**. The center's XP doubling does **not** double the underlying number of actual mined nodes, chopped trees, crafted items, harvested crops or valid PvP encounters. If the internal economy awards *mastery XP* separately, its XP value may double but its effect on action-based milestone thresholds must be explicitly specified rather than assumed.

### 37.2 Five mastery systems and milestones (71–80)

| # | Topic | Confirmed response | Open |
| --- | --- | --- | --- |
| **71** | Mastery categories | **Mining, Woodcutting, Farming, Crafting and PvP** only | Future expansion beyond five |
| **72** | Advancement | **Milestones / meaningful action counters**, not time played | Threshold values and reward table |
| **73** | Level cap | **10 mastery levels per track** for now | Future expansion and exact starting level |
| **74** | Buff cadence | **Every mastery level** grants a buff | Per-level mapping |
| **75** | Resource benefits | **+1% yield per applicable mastery level** as starting balance | Which drop/resource classes apply and rounding |
| **76** | PvP mastery | **Both combat and noncombat rewards** | Power caps, PvP reward types |
| **77** | Crafting mastery | **All four:** material discounts, output/batch increases, crafting speed, recipe unlocks | Buff rates and individual levels |
| **78** | Modifier operations | **Specific additive and multiplicative multipliers** coexist | Each modifier's type and caps |
| **79** | Cosmetics | **Yes** to titles, cosmetics, animations and building decorations as milestone rewards | Exact milestones and content |
| **80** | Social display | Mastery levels/titles **may be visible in lobby** | Inspection/badges/privacy options |

**Numeric starting interpretation:** If a resource-specific buff is +1% per earned mastery level, achieving level 10 gives **+10%** from that mastery before permitted additive/multiplicative stacking. This is not a blanket claim that every PvP/combat perk grants 10% extra damage. Crafting mastery benefits may be different effect types and use server-authorized per-level configurations.

### 37.3 Rebirth and perk details (81–89)

| # | Topic | Confirmed response | Open |
| --- | --- | --- | --- |
| **81** | Eligibility | **Both general player-level requirement AND endgame challenge** | Level number and challenge details |
| **82** | Rebirth reset | **General level resets to 1**; already protected progression remains preserved | Coins/Gems and stored total XP treatment beyond the level reset |
| **83** | Rebirth payment | **Yes**, requires increasingly costly resources/currency/materials or ritual requirements | Exactly which and how much per rebirth |
| **84** | Token amount | Later rebirths **could grant additional tokens** | Whether token amount increases and its rate |
| **85** | Rebirth difficulty | **Progressively more expensive and harder** | Curve and maximum count |
| **86** | Perk examples | **XP, rare-drop luck, drop quantity, improved water walking speed**, plus possible others | Each rank/bonus/cost |
| **87** | Perk state | **Permanently active** once owned; no loadout slots required | Respec consequences |
| **88** | Multi-rank perks | **Some perks can have upgrades/ranks**; others one-time | Rank limits/prices |
| **89** | Respec payments | Can buy respec with **earned Gems, Robux, or redemption codes** | Cost, cooldown, refund mapping, code eligibility |

**Rebirth-preservation boundary:** Secure vault contents (including ordinary vaulted resources), legitimately owned Permanent gear, unlocked mastery milestone buffs and cosmetics remain **safe as intended**. The only explicitly confirmed rebirth reset is **general level → 1**. Rebirth should not silently destroy Coins/Gems, token purchases or account entitlements without later approval.

**No skill trees:** A rebirth token **perk catalog/shop** is confirmed, but it is not a branching prerequisite talent tree. Perks are permanently active, not slotted. Some have several upgrade ranks. Each effect must be classified **additive or multiplicative** so it stacks deterministically with mastery buffs and the center 2× material and XP bonuses.

**Respec parity:** Respec via Robux is permissible because an equivalent respec is obtainable using **gameplay-earned Gems** (and occasionally valid codes). Roblox purchase receipts and promo-code consumption must be idempotent. No respec may conjure extra perk tokens.

### 37.4 Verification and anti-exploit cases

1. Full HP defaults to **100**, but valid account/gear upgrades raise maximum HP; medicine cannot exceed the current modified max HP.
2. Full sprint runs **3 seconds**, stamina from empty fully returns in **5 seconds**; combat/crouching/gathering spend no stamina.
3. At food exactly 25%, the **below-25%** speed penalty has not yet triggered; 24.99% triggers **10% movement slow**; full meter empties in **300 seconds**.
4. Basic medicine immediately heals **10**, advanced **25**, potion **50**, followed by tier-specific animation/reuse lock. Spammed remotes do not repeat healing.
5. Food HoT completes after **10 seconds** absent hits, with food-dependent total. A hit halves remaining heal, and if post-hit remainder ≤10 HP, cancel rest, without retroactive health loss.
6. Rock deals **5 raw damage**, tentative wooden spear **~15** and stone spear **~25**; armor multiplies EHP rather than flat damage reduction. Actual HP/EHP conversion remains consistent for attack, heal and downed finishes.
7. Tribe character enters downed with **20 HP** at zero ordinary health. The 60-second bleed-out pauses during a valid **10-second** revive; enemies can finish through armor while revival is ongoing.
8. Revival cancellation resumes the old timer and does not reset 60 seconds. Solo players still die immediately with a 10-minute corpse and lobby ejection.
9. Legitimately earned general XP and mastery milestones persist **even after death**, while an unextracted material stack does not. No XP progress rolled back with lost loot.
10. Center extraction pays **exactly one additional set of current-run XP grants** and double materials; it does not retroactively double prior runs or invent extra milestone action counters.
11. UI and persisted schema contain **only five active mastery tracks**, each capped at **level 10**, with one-time buff at **every mastery level** and cosmetic milestones; lobby can show progress/titles.
12. Resource mastery +1% increments stack with catalog-classified **additive/multiplicative modifiers** in a deterministic order. Combat and noncombat PvP mastery bonuses are bounded and tested.
13. Crafting mastery supports ingredient savings, output batch, crafting speed and unlock milestones without allowing zero-cost infinite crafts.
14. Rebirth requires both level and completed challenge, increases future costs, sets **general level 1** but retains vault, Permanent equipment and permanent mastery/owned perks.
15. Rebirth perk purchases are permanently active; some perks have ranks, and their XP/luck/drop-volume/water movement effects cannot be client-forged.
16. Each Gem, Robux-receipted or redemption-code respec is a once-only entitlement. Player cannot duplicate tokens or avoid valid charges by disconnecting.
17. All new XP/mastery progress and stored items survive empty-world reset and unauthorized player teleport failures.

### 37.5 Remaining numerical decisions

- Each basic/advanced/potion **animation duration**, and whether use animation alters movement.
- Post-revive ordinary HP; reviver range, interruptions and multiple concurrent revivers.
- Precise wooden/stone spear attack speeds and ranges, arrow damage, enemy damage and armor tier **EHP multipliers**.
- Whether food replenishes hunger meter immediately and by what percentages; additional effects at **0% food**.
- Food HoT stacking, server tick resolution, exact application of repeated hits and whether remaining heal duration changes.
- Exact five mastery milestone targets for levels 1–10; category-specific yield buffs, combat perk cap and crafting milestone allocation.
- Rebirth general level and challenge threshold, increasing resource/currency costs, token awards and multirank perk catalog.
- Gem/Robux respec price, how codes are granted and what constitutes a valid refund/respec.
- Detailed buff additive/multiplicative ordering and caps, including XP stacking/center extraction.


## 38. Owner-approved Q90–115: economy, equipment and world balance (2026-10-22)

> These numbered answers supersede earlier proposed or Open design where contradictory. Approximate values are **playtest targets**, not hardcoded guarantees; unspecified details remain Open. Systems above (§§4, 6–10, 16, 19, 22–25) provide their implementation contracts.

### 38.1 Currency, merchants and trading (Q90–99)

| # | Owner answer — Confirmed except where marked tentative | Open details |
| --- | --- | --- |
| **90** | **Coins** primarily from quests, selling materials/items to NPC merchants and extracting | Individual rewards and merchant prices |
| **91** | **Gems** from quests, milestones, achievements, rebirths, rare enemies/resources and optional Robux | Earn rates by activity |
| **92** | **~10,000 Coins/hour** and **~100 Gems/hour** of active play (initial targets) | Player distribution and inflation |
| **93** | **Coin → Gem conversion undecided**; do not create a rate yet | Whether conversion exists |
| **94** | **Neither currency EVER drops on death**; account-safe | Physical currency tokens if separately approved |
| **95** | **NPC merchants buy materials, monster drops and crafted gear, including rare materials** | Quotes/locations and rare-sale confirmation |
| **96** | **25 starting vault slots**; buy **+25 slots per upgrade**, with **Robux or earned Gems** | Prices, cap, stack semantics, overflow |
| **97** | **~10 hours** to earn an equivalent to a *valuable* paid offer (adjust by strength) | Value per feature and starting offers |
| **98** | **Only lobby trades**; **eligible items + Gems** may trade; **Coins NEVER** | Eligible ordinary items, fraud controls |
| **99** | **No direct Robux-paid combat advantage**, only **progression acceleration/QoL**; **Roblox Premium +25% XP** proposed | Earnable parity XP perk, exact stacking, eligibility |

**10-hour economy appraisal:** Ten active hours is a defensible **mid/high-value purchase benchmark to playtest**, not a recommended minimum for every minor cosmetic or starter vault upgrade. At target **100 earned Gems/hour**, that represents **~1,000 Gems** before spending, **not** a finalized universal price. Test newcomer access and the earned-vs-paid benefit parity requirement.

**Roblox API/policy notes:** Detect eligible Premium membership using verified server-side player membership state, not a client claim. **+25% XP is a Flintborn benefit, not an automatic Roblox payout**; offer an earnable equivalent. Roblox-native Robux passes/products cannot literally be purchased with Gems; offer equivalent game-managed unlocks where appropriate. If purchased Gems or Robux-linked bonuses can affect randomized quality rolls, drops or luck, review Roblox's **paid random items** guidelines and regional eligibility/odds rules before launch. Official references: https://create.roblox.com/docs/reference/engine/enums/MembershipType ; https://create.roblox.com/docs/production/monetization ; https://create.roblox.com/docs/production/monetization/paid-random-items .

### 38.2 Launch items, crafting and carry capacity (Q100–110)

| # | Owner answer | Open |
| --- | --- | --- |
| **100** | Launch **Spears, Daggers, Swords and Bows** | Exact archetypes/speeds |
| **101** | Armor slots **Head, Chest, combined Legs/Boots**; **NO shields** | EHP values |
| **102** | Rarity is **fixed per item archetype** (e.g. Rare Iron Sword, Common Stone Sword), not randomly changed on identical named gear | Item rarity assignment |
| **103** | Same-named gear may have **small individual quality/stat rolls**; high crafting mastery improves favorable field-craft rolls | Numerical ranges and odds |
| **104** | **Small starter resource catalog** then grow with updates | Exact catalog |
| **105** | Basic gear **craftable anywhere**; advanced workbench needed; **public-world workbenches may yield better rolls**, lobby workbenches use **default quality** | Station tiers and RNG |
| **106** | **Few harvested materials**; **first gear set ~10 minutes or less** | Recipe counts, starter-set contents |
| **107** | **10 arrows per crafting recipe**, upgraded material arrow types can deal more damage | Ingredient inputs and power |
| **108** | **Fixed hotbar and fixed backpack slot counts**; **one consolidated resource stack/row per resource type** | Slot counts, quantity caps |
| **109** | **Only specifically designated gear** becomes Permanent; some special gear qualifies, other special gear cannot | Item allowlist |
| **110** | First Permanent conversion ≈ **a couple of successful extractions plus one rare event** | Exact materials/recipe/unlock |

**Catalog and quality invariant:** Item rarity is an immutable archetype property, but each *instance* can roll minimal stat variance. World workbench crafting can improve eligible rolls as Crafting mastery rises; **safe lobby crafting has baseline/default stats**. Permanent conversion preserves the source instance's rolled stats and grants no additional power. Only approved catalog entries are convertible, independent of rarity. Do not randomize rarity on every Iron Sword.

**Inventory invariant:** Same-type materials consolidate into one logical backpack entry; swords/gear with different rolls remain separate uniquely identified instances. Backpack/hotbar fixed capacity is separate from **vault's 25+25 slots**. Numeric stack maxima/overflow remain Open.

### 38.3 Events, totems, decay and scaling (Q111–115)

| # | Owner answer | Open |
| --- | --- | --- |
| **111** | Weighted non-Guardian event checks **about every 5 minutes**, **multiple events can coexist** if far enough apart | Weights, min distance, concurrency |
| **112** | Ordinary trees/stone/ore **~2-minute regrowth**; rare event resources spawn **once** until another event | Variation, exact implementation |
| **113** | **Totem radius depends on map size**, **totem areas may overlap** | Radius and claim conflict/priority |
| **114** | Unclaimed structures decay in **~5 minutes with ±1-minute randomness**. Working interpretation: fully expire in **4–6 minutes** | Confirm full lifetime versus decay tick semantics |
| **115** | Bosses start at an archetype **base level/difficulty plus scaling** | Input (player level/gear), curve and limits |

**Guardian special case:** Prior **15–20-minute** center Guardian schedule and **3-minute warning** are retained; Q111 applies to weighted *other* events. Guardian's physical Legendary loot at **25% HP** remains contested.

### 38.4 Acceptance and regression requirements

1. Coin sources are quests, NPC selling and successful extractions. Gems derive from all listed reward sources. Both persist and **neither appears in corpses**.
2. Target one-hour earning analytics separately for **10k Coins** and **100 Gems**, excluding AFK and fraudulent repeated sales.
3. NPC vendors may legitimately buy rare ingredients; restricted raw resource **player trading** remains blocked except catalog allowlist.
4. **Lobby-only** two-party trade permits Gems and eligible items but rejects Coins, forged world trades, stale owners and duplicate receipts.
5. Vault starts at **25 slots** and each correctly confirmed Gem/Robux purchase adds **exactly 25**, with idempotent payment/entitlement settlement.
6. Robux offers provide QoL/progression, not direct PvP damage/health/armor advantages; all paid benefits have earned-currency equivalents.
7. A valid Roblox Premium player receives intended **+25% XP**; server verifies status, free-play equivalent exists, center 2× XP receipt cannot be replayed.
8. Weapon family and armor slot catalog reflect launch decisions; no shield or player-magic items.
9. Same item type keeps its rarity while unique instances may have small quality rolls. In-world mastery crafting can favor small improvements; lobby crafting baseline does not.
10. Basic recipes craft anywhere with inexpensive inputs; first useful gear set targets **≤10 minutes**, arrow craft yields **10**.
11. Fixed hotbar/backpack obey capacity; identical raw material types aggregate; vault capacity is a separate property.
12. Permanent conversion checks catalog eligibility and vaulted inputs; starter conversion balances against a few extractions plus one rare event; ineligible special items fail.
13. Weighted event checks roughly every five minutes; multi-event spatial validator prevents too-close overlapping encounters, with public announcements.
14. Ordinary resources regrow in about **120 seconds**; rare nodes require a **new separate event**.
15. Totem influence areas can overlap. A structure with no valid totem decays in approximately **4–6 minutes** unless decay interpretation changes; raiding remains unrestricted.
16. Boss strength uses valid baseline plus an eventually defined scaling formula; cannot be made trivially easier by equipment swaps/alt joins.

### 38.5 Remaining targeted decisions

Exact NPC prices and vault tier costs/cap; Coin-to-Gem exchange; currency earn-source weighting; qualified item and rare-material trade allowlists; Premium vs Plus qualification and earnable XP equivalent; minute-to-Gem tuning per monetized feature; fixed hotbar/backpack sizes, stack limit and vault overflow; precise gear catalog/quality-roll range; mastery craft roll tables; ordinary/rare respawn spatial limits; overlapping totem ownership rules and whether ~5-minute decay means full disappearance or tick; boss scaling source/curve.


## 39. Design change log

| Revision | Date | Change |
| --- | --- | --- |
| **0.1** | 2026-10-21 | Created Flintborn GDD from the original primitive extraction handoff; recorded primitive-fantasy/no-firearms direction; added proposed systems, technical guardrails, vertical slice and decision backlog. |
| **0.2** | 2026-10-21 | Added confirmed extracted-material special crafting and expensive eligible-item Permanent conversion; expanded item taxonomy, Forge design, working death/recovery policy, resource/recipe catalog, cross-run economy and player journeys. Further implementation details in §22–28. |
| **0.3** | 2026-10-21 | Removed player-usable shields and added consumable healing progression, recipes and PvP interruption rules; kept Guardian shield-pillar boss mechanics. |
| **0.4** | 2026-10-21 | Confirmed 120-second telegraphed extraction hold, invulnerable and disconnect-safe animation, 600-second lootable bodies after active exit, admin update preservation, rare events, accessible building and diverse playstyle incentives. |
| **0.5** | 2026-10-21 | Established the mandatory **protected play-world loading/main menu** with explicit Play-to-spawn risk activation. Teleport, loading, pre-spawn kick, and failed admission cannot forfeit items. Added full state machine, recovery flows, detailed QA and cross-references in §29–33. |
| **0.6** | 2026-10-21 | Recorded answers 1–24: 30-player world target, empty-server reset, same-world rejoin/death kick, crash/update recovery, transferable same-stat Permanent items, vault upgrades and levels, server-shared 120-second end-only extraction, rare portable 30-second anywhere rune, and lobby return. Clarified unresolved reset-vault and payout semantics. |
| **0.7** | 2026-10-22 | Confirmed questions 25–48: health/stamina/food only; click melee and craft-arrow slow bows; sprint/crouch, no player magic or equipment wear; instant medical healing with post-use animation cooldown, food HoT partially interrupted by damage; 60-second pauseable tribe revives, solo immediate death and lobby ejection; random map spawns, PvP with designated safe-POI exceptions; 8-member tribes, totem-based structure decay, public storage, any-time normal-tool raids, wood/stone/iron, persistent-in-live-world farming/takeovers; weighted publicly announced events, biome-random rare nodes, three boss sources and level/gear-based scaling. Added §35 and revised affected launch/QA/technical sections. |
| **0.8** | 2026-10-22 | Resolved Q3 (all vault items permanently saved) and Q23 (center extraction **2× all material stacks including rare resources and 2× XP**). Confirmed Q49–60: persistent Coins/Gems, direct trading with rare/Exclusive material exceptions, eight rarity classifications, XP/levels/crafting mastery, small permanent playstyle mastery buffs/cosmetics, rarest Permanent gear requiring advanced contested resources, enhanced primitive Booga Booga art, adjustable camera, tutorial/guided quests, gameplay-earnable parity for all monetized features, and rebirth tokens spent on perks. Added §36 on technical/economic design and QA. |
| **0.9** | 2026-10-22 | Incorporated Q61–70: 100 base HP with gear/upgrade max, 3s sprint/5s recovery, five-minute food depletion and −10% speed below 25%, immediate medicine heals 10/25/50, 10s food HoT halved by hits with ≤10 HP cutoff, rock 5/wood spear ~15/stone spear ~25 raw damage targets, EHP multiplier armor, 20-HP downed tribe members, 10s revives and armor-based finishing, immediate persistence of XP/mastery on death and center 2× all current-run XP. Incorporated Q71–89: five milestone-based level-10 permanent masteries, per-level buffs (+1% resource yield baseline), combat/noncombat PvP and all four crafting benefit types, additive/multiplicative perk stacking and lobby visibility, increasing-cost level+challenge rebirth with general level reset to 1, permanently active one-time/multirank token perks and Gem/Robux/code respec. Added §37 and verification matrix. |
| **1.0** | 2026-10-22 | Recorded Q90–115: Coin/Gem earning targets/sources, death-safe balances, NPC sales, lobby Gem/item trades/no Coins, +25 slot vault upgrades by Gems/Robux, ~10-hour significant-offer benchmark, Premium +25% XP and no paid combat advantage; four launch weapons, three armor slots, fixed archetype rarity, small crafted quality rolls favoring unsafe workbenches/masters, 10 arrows, fixed inventory and early Permanent pacing; ~5-minute event rolls/multiple spatially separate events, ~2-minute ordinary node regen, one-time rare resources, overlapping totems, 4–6-minute unclaimed decay and base-plus-scaling bosses. Added §38 implementation and QA with platform policy citations. |

---

**Working principle:** Flintborn has protected Play admission, open-world PvP with rare safe POIs, random map spawn and death-triggered lobby ejection. Launch combat starts at **100 base HP** with effective-HP armor; rock 5 / wooden spear ~15 / stone spear ~25 raw hit targets, **3-second sprint / 5-second recovery**, five-minute food depletion, instant medical heals of **10/25/50 HP** and food healing over 10 seconds. Tribe members have **20 downed HP, a 60-second timer and 10-second revives**. Five permanent masteries cap at level 10, with a buff at each level. Rebirth resets general level to 1 and grants tokens for permanently active perks. Currencies never drop. Coin routes are quests/merchant sales/extraction (**~10k/h**), Gem routes include rare play rewards and Robux (**~100/h**). Trades use only **eligible items/Gems in the lobby**, never Coins. Vault starts at **25 slots**, +25 per Gem/Robux upgrade. Launch weapons are spears/daggers/swords/bows and three armor slots, arrows craft in tens. Weighted events roll **~5 min**, routine nodes respawn **~2 min**, totems overlap and unclaimed structures decay **~4–6 min**. Public islands have raidable totem-based buildings, weighted announced events and server-shared **120-second fixed extraction** or rare **30-second portable rune**. Center exit gives **2× materials and all current-run XP**, while all successfully vaulted gear remains saved across world resets. No player magic, firearms, shields or gear durability at launch. Remaining balances are Open.
