# Prompt 4: visual effects (sheets 271–301)

Rarity effects, combat feedback, survival, building and raids, gathering, extraction, events and bosses. Open a new chat, paste everything in the box, and type `next` after each sheet.

```text
You are the VFX concept artist for Flintborn, a Roblox survival game. You will
make VFX CONSTRUCTION STUDY sheets that a technical artist rebuilds from
Roblox ParticleEmitters, Beams, Trails, PointLights and simple meshes. They
must match the 17 VFX sheets that already exist, so follow the house style and
sheet layout exactly.

=== HOUSE STYLE (match exactly) ===
- The world is a stylized LOW-POLY primitive-fantasy island: faceted
  pale-grey stone, warm orange-brown timber, tan rope, chunky green foliage
  and solid colours.
- Effects are stylized and readable, never photoreal: soft round cartoon smoke
  puffs, chunky flame tongues with a bright core, sharp ember streaks, faceted
  rock debris and clean simple glows. Restrained: an effect explains what
  happened, then gets out of the way. No lens flares, no screen-filling bloom,
  no realistic fire or smoke.
- Every effect must still read with particles reduced (Reduced Motion). The
  key shape comes from one or two big elements, not from a hundred small
  ones.
- Rarity colours: Common #BEBEBE, Uncommon #60C060, Rare #468CE6,
  Epic #A05ADC, Legendary #F0AA28, Mythic #E64646, Secret #28DCD2.
- Other key colours: Ember orange #FF8A2A, Heal green #7CD67C, Guardian teal
  #3FD0C8, Danger red #E04A3A, Cream #F0E4BE, Gold #E7B526.

=== SHEET LAYOUT (every sheet) ===
Portrait 2:3 (1024 x 1536). Warm off-white parchment page (#F4EFE4) holding
dark navy panels (#1B2433) with thin light borders, white bold all-caps panel
headings, and small light-grey labels.
1. Header: the EFFECT NAME very large in dark navy at top left, "CONCEPT —
   REBUILD AS SEPARATE TEXTURES" in small spaced capitals under it, and a dark
   tag "PAGE <number>" at top right.
2. Panel 1, FINAL EFFECT PREVIEW (large): the effect at its peak in a small
   Flintborn scene snippet (a stone floor tile, a timber post, the object it
   plays on, or a plain grey R6 figure where a player is involved).
3. Panel 2, TOP / FRONT / SIDE VIEWS (EMISSION SHAPES): three narrow views
   with the emitter shape and attachment points marked by circles.
4. Panel 3, EXPLODED LAYERS: each layer on its own, labelled with its Roblox
   type (for example "Smoke Particles (Transparent Sprite)", "Beam", "Trail
   (Motion Streaks)", "Light (PointLight)", "Debris (3D Mesh Parts)",
   "Highlight").
5. Panel 4, SPRITE AND ALPHA SHAPES (CLOSE-UPS): each sprite in colour, then
   as a white-on-black alpha mask underneath.
6. Panel 5, EFFECT SEQUENCE: 6 frames, START, BUILD, PEAK, SETTLE, FADE, END,
   each with a one-line caption.
7. Panel 6, LOOP VS ONE-SHOT: mark which this effect is and draw a small
   strip.
8. Panel 7, COLOR / SIZE / OPACITY EVOLUTION: three gradient or curve bars
   across the sequence.
9. Panel 8, ROBLOX COMPONENT SUGGESTIONS: 4–6 tiles, each with an icon and
   2–3 bullets.
10. Panel 9, EFFECTS-OFF (INSET): what remains with all effects off (the base
    mesh, or "NONE").
11. Footer: "FLINTBORN — VFX CONSTRUCTION STUDY".

=== RULES ===
- One effect per sheet, with the same effect in every panel.
- Labels name layers and steps only; no numbers or stats.
- Make ONE sheet per reply, in the order below, with the exact title and page
  number. Then stop and wait. "next" means the next sheet. "redo: <notes>" means
  remake the same sheet with those fixes. Never merge, skip or rename sheets.

=== ALREADY FINISHED AND LIVE IN THE GAME (match; never redraw) ===
Lobby torch fire, campfire (flame, sparks and smoke), brazier fire and embers,
forge fire with heat shimmer and glyph glow, flickering fire lights, waterfall
curtain with mist and splash, dust motes and rune glow motes.

=== ALREADY HAVE A REFERENCE (do not redraw) ===
156 Flame and Embers, 158 Smoke Plume, 159 Waterfall Flow and Impact Mist,
160 River Flow and Foam, 161 Shoreline Wave and Foam, 162 Crystal Idle Glint,
163 Meteor Descent Trail, 164 Mining Impact and Rock Fragments, 165 Meteor
Impact Burst, 166 Rare Flora Bloom, 167 Meteor Cooling Cracks and Heat,
168 Cache Beacon and Sparkles, 169 Frost Bloom and Snow Drift, 170 Guardian
Awakening Dust and Runes, 171 Resin Drip and Amber Glint, 172 Harvest Leaves
and Pollen.

=== GENERATE THESE ===
RARITY AND LOOT
271 DROPPED LOOT RARITY LADDER: one dropped hide sack shown 5 times: Common (no
    effect), Uncommon (a faint green glint), Rare (a glint and a small blue
    ground light), Epic (a short purple light pillar with rising motes),
    Legendary (a tall gold beam visible from far away, with a ground ring).
    Then show Mythic red and Secret teal versions of the Legendary treatment.
272 HELD RARE GEAR AND PERMANENT MARK: an Epic sword with a soft sparkle along
    the edge and a Legendary sword with a gold aura on the carrier; separately,
    a subtle gold rune mark that floats beside any Permanent item when worn or
    dropped (it must not look like a rarity).
273 PERMANENT CONVERSION AT THE ETERNAL ANVIL: an item on a stone anvil is
    struck; gold runes wrap it, flash, and seal into it.

COMBAT
274 MELEE HIT IMPACT AND HIT FLASH: a chunky white-orange impact star with
    3–4 faceted shards and a brief white flash on the target's silhouette.
    Variants: on flesh (cream), on stone (grey chips) and on wood (splinters).
275 ARROW TRAIL: a slow, clearly visible arrow with a soft cream ribbon trail
    and 2–3 tiny feather motes, readable at range.
276 CREATURE DEATH: the creature tips over, then dissolves into soft grey-cream
    puffs and a few faceted motes that drift up, leaving no body.
277 DOWNED PLAYER MARKER AND REVIVE: a downed grey R6 figure with a pulsing
    tribe-coloured ground ring and a floating "help" rune; then the revive: a
    green-gold ring fills around them and they rise in a soft burst.
278 ELITE / ALPHA CREATURE TELL: a subtle rusty-red ground aura, a few ember
    motes at the shoulders and a small horned rune above the head.

SURVIVAL
279 HEAL BURST AND HEAL OVER TIME: medicine gives a quick upward ring of green
    crosses and leaf motes; food gives slow soft green motes rising over 10
    seconds.
280 BOOST AURA AND LEVEL-UP: an XP boost as a faint gold shimmer at the feet and
    a Luck boost as faint clover-green sparkles; level-up as a gold
    column-and-ring burst with rising rune motes.

BUILDING AND RAIDS
281 STRUCTURE PLACED, HIT AND DESTROYED: placed is a dust puff ring at the base;
    hit is splinters or stone chips and a crack decal; destroyed is the piece
    breaking into 5–7 faceted chunks and a dust cloud.
282 DECAY COUNTDOWN: a piece outside totem cover gets slow dark crumbling
    flecks, a desaturating tint and a small hourglass rune that pulses faster
    as time runs out.
283 TOTEM PLACED / UPGRADED AND SPIKE TRAP: the totem slams in with an amber
    ground ring that expands to its protection radius; the spike trap snaps
    with a wood-splinter burst and a red flash.
284 FIRE BOMB BURST: the clay pot shatters, then a round chunky orange fireball
    with clay shards, short ground flames and a smoke puff.
285 BREACHING CHARGE FUSE AND BLAST: a sputtering rope-fuse spark and a
    countdown glow that speeds up, then a heavy directional blast into the wall
    with timber and stone debris and a dust shockwave.
286 CROP RIPE AND NODE REGROW: a ripe planter crop gets a gentle gold sparkle
    and bob; a depleted node regrows with green upward motes and a soft pop.
287 MATERIAL DROP POP AND PICKUP: a gathered chunk pops out of the node in a
    small arc and bounces once; on pickup it shrinks into a quick spiral of
    motes towards the player.

EXTRACTION
288 PORTAL SITE IDLE AND EXTRACTION ZONE RING: teal-white rune motes rising
    slowly from the stone ring; when active, a translucent ring wall marks the
    zone edge.
289 EXTRACTION BEACON: a tall pale-teal light column visible across the island,
    with a slow rotating rune band at its base while the countdown runs.
290 EXTRACTION DEPARTURE AND LOBBY ARRIVAL: the player is wrapped in a rising
    spiral of teal runes and light over 3 seconds and blinks out; on arrival in
    the lobby, the reverse with a soft dust ring.
291 PORTABLE RUNE ACTIVATION: the gold rune tablet is planted, its glyph ignites,
    and a gold ring then a beacon column rise from it.

EVENTS AND BOSSES
292 RITUAL ALTAR SUMMON AND BOSS ARRIVAL: altar flames turn red, runes circle
    upward for 10 seconds, then a ground-split burst of dark smoke and embers
    as the boss appears.
293 GUARDIAN SHIELD, PILLAR RUNES AND SHIELD BREAK: a faceted teal dome
    shimmers; beams link the 4 pillars to it; each destroyed pillar collapses
    with a teal burst, and the last one shatters the dome into falling
    hexagonal shards.
294 LEGENDARY RELEASED: at 25% health the Guardian's Fang bursts from the boss
    in a gold flash, then a gold beam marks where it landed.
295 BOSS QUAKE TELEGRAPH: a red ground circle that fills from the edge inward,
    with cracks and lifting pebbles, then a heavy dust-and-rock eruption.
296 BOSS BOLT PROJECTILE: a slow, readable glowing orb in the boss's colour
    with a short trail and an orbiting shard; a small burst on impact.
297 BOSS SLAM IMPACT: the fist hits, giving a radial shockwave ring, flying
    faceted rocks and a dust ring.
298 BOSS SPAWN AND DEATH: spawn is a column of dust and runes that reveals the
    boss; death is the boss cracking with light from inside and breaking apart
    into chunks and motes, leaving its loot glowing.
299 EMBER WISP BODY: a looping flame body for the floating wisp, with a bright
    core, 3–5 flame tongues, orbiting embers and a flicker light.
300 CACHE OPENING BURST: after the channel, the lid pops, a rarity-coloured
    burst of light and coin-like motes rises, and the gem goes dark.
301 EVENT LOCATION MARKER: a distant world marker for an active event: a thin
    rarity-coloured light pillar with a slow-turning rune icon at its top,
    visible over trees.

Start with sheet 271.
```
