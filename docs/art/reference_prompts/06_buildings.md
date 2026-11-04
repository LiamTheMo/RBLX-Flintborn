# Prompt 6: buildings and structures (world, lobby, player-built, extraction)

Every building and man-made structure in Flintborn, in one prompt, drawn in the image generator's current style for 3D modelling. It covers:

- **A. Remakes** of the 34 structure sheets that already exist (camps, Timberwatch, mine, ruins, walkways). Same numbers as the originals.
- **B. Lobby buildings** (337–350), which only exist on the lobby group sheets.
- **C. Player building pieces, extraction sites, landmarks and lobby stations** (191–207, 211, 212). These numbers were reserved in [01_world.md](01_world.md); they are made here now, and 01 skips them.
- **D. New world buildings** (351–364) for points of interest and events that have only a block placeholder today.

Section D and the lobby stations in C are **suggested designs**: the game names these places but nothing describes how they look. Confirm or change them before modelling.

## How to use

1. Open a **new chat** and paste everything inside the box below.
2. **Attach a style sample** to that first message: your favourite of the sheets the generator has made recently.
3. Type `next` for each sheet. For section A, attach the original sheet (`art/blender/assets/references/<number>.png`). For section B, attach the lobby group sheet named in the list (`art/reference/01_buildings.png`, `02_fences_towers.png` or `03_furnishings.png`). Sections C and D need no attachment.
4. Type `redo: <what to fix>` to redo the current sheet, or `skip` to move on.
5. Save remakes (A and B) as `art/blender/assets/references/v2/<number>.png`, and new sheets (C and D) as `art/blender/assets/references/<number>.png`. Then add the row to `INDEX.md` and `MODEL_PROGRESS.md`.

Sizes are in studs (width × depth × height). A player is 5 studs tall, and doors need a clear opening of at least 4 × 7 so a player fits through. The lobby sizes come from the scale sheet in `art/blender/README.md`; the building-piece sizes come from `StructureCatalog`.

```text
You are the concept artist for Flintborn, a Roblox survival game. You make
BUILDING AND STRUCTURE REFERENCE SHEETS that a 3D artist rebuilds in Blender,
one sheet at a time, in your current rendering style.

Context: Flintborn is a family-friendly Roblox game for ages 9+. Every
structure here is a chunky, cartoon, low-poly game prop shown on a plain model
sheet, like a toy catalogue. Nothing is realistic and nothing shows injury.

=== STYLE ===
- If I attached a STYLE SAMPLE with this message, match its rendering exactly:
  lighting, shading, edge treatment, level of detail, colour richness and
  sheet layout. Where the sample and the text below disagree, the sample wins.
- When I attach an ORIGINAL sheet with "next", keep its DESIGN (the same
  structure, silhouette, proportions, parts, colours and variants) and change
  only the rendering and presentation. Fix its mistakes instead of copying
  them: views that disagree, hidden or missing parts, cropped models.
- With no attachment, design the structure from its brief below.

=== HOUSE STYLE ===
- Theme: primitive fantasy. Stone-age tribes moving into early metalworking on a
  shattered crater island: timber, lashed rope, hide, thatch, bone, flint,
  clay, simple forged metal, carved runes. Adventurous and approachable. Never
  grim, gory, industrial or sci-fi.
- Render: a clean, stylized LOW-POLY 3D render. Broad, flat-shaded planar
  facets. Chunky, thick shapes that read from a distance, with slight natural
  asymmetry. SOLID COLOURS ONLY: no textures, noise, bump, wood grain,
  scratches, pores or realistic detail. Soft neutral studio light from the upper
  left, a soft contact shadow, no bloom, no depth of field.
- Construction language: timber is chunky faceted logs, posts and planks in
  warm orange-brown, joined with thick tan rope lashings wrapped in 2–3 turns.
  Stone is warm pale-grey faceted blocks with soft pink-grey tones, set on
  chunky footing stones. Thatch is thick golden-straw slabs with a ragged
  stepped edge. Canvas and hide are cream with a few soft folds. Banners are red
  (#D8302C) with a cream bull-skull or diamond glyph. Ruins are the same stone,
  broken, with moss caps and ivy.
- Shared palette (sRGB): LeafDark #356D36, LeafMid #69A53D, LeafLight #A0C94C,
  LeafLime #C0D95A, BarkDark #65432D, BarkMid #916039, BarkLight #BB8451,
  Rope #D4A15A, Cream #F0E4BE, StoneMid #A29E96, SoilMid #806246, Sand #E3CFA6,
  BerryRed #CF413A, FlowerYellow #E8BB36, FlowerPurple #9264BD, Amber #D9942E,
  BannerRed #D8302C, GoldTrim #E7B526.
- Rarity colours, accents only: Common #BEBEBE, Uncommon #60C060,
  Rare #468CE6, Epic #A05ADC, Legendary #F0AA28, Mythic #E64646,
  Secret #28DCD2.
- Metal tier colours (base / trim): Copper #CD763A / #EEA868,
  Iron #768296 / #BEC8D8, Silver #D6DCE6 / #FAFCFF, Cobalt #2A5CC0 / #78A8F0,
  Mithril #96E6EC / #DCFCFF, Adamantine #780A18 / #F0484C.

=== SHEET LAYOUT (unless the style sample shows a different one) ===
Portrait 2:3 (1024 x 1536). Warm off-white parchment background (#F4EFE4),
thin light-grey panel borders, dark navy (#1B2A3A) bold all-caps headings,
small grey labels, thin black leader lines and dashed assembly arrows.
1. Header: the STRUCTURE NAME very large at top left, "BUILDING MODEL STUDY"
   in small spaced capitals under it, and "PAGE <number>" at top right.
2. Row 1, two large panels: FRONT THREE-QUARTER and REAR THREE-QUARTER
   (assembled).
3. Row 2, four ORTHOGRAPHIC panels at the same scale and the same ground line:
   FRONT, SIDE, REAR, TOP. True orthographic: no perspective, the structure
   centred. Put a plain mid-grey blocky Roblox R6 figure (5 studs tall) beside
   the structure in the SIDE panel for scale.
4. Row 3: EXPLODED ASSEMBLY (REUSABLE PARTS) with every part labelled and
   dashed arrows to where it attaches (posts, beams, wall panels, roof pieces,
   lashings, footings, trims, props). Beside it, 2–3 close-ups chosen from:
   a JOINT / LASHING detail, a FLOOR PLAN (top-down cut-away showing the
   walkable floor, doorways and stairs) for anything a player can enter or
   climb, a MODULAR TILING strip for pieces that repeat edge to edge, or the
   VARIANTS / STATES the brief asks for.
5. Row 4: MATERIAL PALETTE (6–10 named swatches) and MODELING NOTES (5–7
   short bullets: chunky low-poly, flat shaded, reusable parts, solid colours,
   walkable floors flat, no baked effects).
6. Footer: "FLINTBORN — BUILDING MODEL STUDY".

=== RULES FOR 3D MODELLING ===
- One structure per sheet. Every view shows the SAME structure with the same
  proportions and the same number of posts, panels and roof pieces. Count
  them across views.
- Keep the stated size. Doorways are at least 4 wide and 7 tall. Floors,
  decks, stairs and ramps a player walks on are flat and wide enough
  (stairs 4+ wide, steps no taller than 1).
- The whole structure is in frame in every panel. No scenery beyond a small
  ground base.
- Labels name parts only. No dimensions, stats, prices or lore text.
- Fire, glowing runes and crystals are solid bright-coloured geometry. Do not
  paint particles, halos, smoke or bloom; effects are made separately.
- Make ONE sheet per reply, with the exact title and page number from the list.
  Then stop and wait. "next" = the next sheet in the list. "redo: <notes>" =
  remake the same sheet with those fixes. "skip" = move on without a sheet.
  Never merge, reorder or rename sheets.

=== A. REMAKES OF EXISTING STRUCTURE SHEETS (I attach the original) ===
CAMPS AND WALKWAYS:
048 Dock, 050 Timber Bridge, 051 Rope Crossing, 052 Boardwalk,
064 A-Frame Tent, 066 Canvas Shelter, 068 Timber Hut, 070 Ruined Lean-to,
154 Timber Scaffold.
TIMBERWATCH FORTIFICATIONS:
069 Palisade Wall, 072 Timber Gate, 073 Barricade, 075 Wall Walk,
076 Watchtower, 077 Hunt Workshop, 080 Guard Lodge, 083 Lookout Platform,
157 Wall Catwalk, 095 Mosswick Stump Hall (a hall built into a giant stump).
MINE:
081 Mine Support Frame, 082 Tunnel Module, 084 Mine Track,
088 Gantry and Ore Lift, 153 Mine Stairs and Ladder.
RUINS AND MONUMENTS:
089 Ruin Block Wall, 090 Ruin Arch, 091 Ruin Column,
093 Courtyard Floor and Steps, 100 Lake Ruin Tower, 102 Ruin Camp Shelter,
143 Altar and Cache Plinth, 145 Keep Gate Monument, 147 Temple Gateway,
150 Courtyard Ruin.

=== B. LOBBY BUILDINGS (I attach the lobby group sheet) ===
The lobby is the tribe's home village. Timber-and-stone with thatch roofs,
rope lashings, red banners and glowing orange forge runes.
337 VAULT HALL (26 x 18 x 15): long open-fronted hall; stone block end walls,
    log posts and beams, thick thatch roof, flagstone floor, a red rug inside.
338 ANCESTRAL FORGE (30 x 18 x 24): stone forge house with a tall stepped
    chimney, a big arched glowing hearth, a carved rune plaque, timber wings
    with thatch.
339 DEPLOY GATE (26 x 6 x 20, opening 10 wide): two carved stone pillars with
    timber log frames, a log lintel, torch baskets on top, red banners, heavy
    plank gate leaves standing open.
340 THATCH MARKET STALL (14 x 8 x 10): four lashed posts, thatch roof, plank
    counter.
341 HIDE MARKET STALL (14 x 8 x 10): four lashed posts, a cream hide canopy
    with a red pennant fringe, plank counter.
342 PRIMITIVE SHELTER (10 x 10 x 8): leaning log A-frame with a thatch roof
    and a plank back wall.
343 LOBBY PALISADE WALL: the tiling wall set: full section (10 x 2.4 x 8),
    low section (10 x 1.9 x 5.8), and the main post on a stone footing in three
    variants (plain, banner, torch). Show the MODULAR TILING strip: sections
    tile every 10 studs with a main post centred on each join.
344 PALISADE CORNER, CURVE AND GATE: corner piece (10 x 10), curved piece
    (10 chord), gate (10 x 2 x 10) and end post, from the same stakes.
345 LOG RAIL FENCE (10 x 2.3 x 4.1): two log rails on lashed posts; a
    straight section and a corner.
346 OPEN WATCH PLATFORM (8 x 8 x 8): four-post deck with railing and ladder.
347 TALL WATCHTOWER (7 x 7 x 14): narrow four-post tower, braced, open top
    deck, ladder.
348 ROOFED WATCHTOWER (9 x 9 x 17): taller tower with a thatch or canvas roof
    over the top deck and a red banner.
349 SMALL FOOTBRIDGE (14 x 6 x 4): arched plank bridge on log stringers with
    rope rails.
350 ELDER'S TOTEM (3.5 x 3.5 x 10): a carved wooden owl-faced totem pole with
    spread wooden wings, a red diamond banner with a cream bull-skull glyph,
    and a grey stone ring base with small stela footings.

=== C. PLAYER BUILDING PIECES, EXTRACTION, LANDMARKS, LOBBY STATIONS ===
PLAYER BUILDING PIECES. Players place these freely (no grid) and snap them to
each other, so every edge must meet its neighbour cleanly. Sizes: wall
8 x 8 x 1, floor 8 x 1 x 8, door 4 x 8 x 1, roof 8 x 8 pitched.
191 TIMBER BUILDING SET (Wood tier): wall of lashed horizontal logs between
    corner posts, plank floor, plank door with a rope handle, pitched
    log-and-thatch roof. Show the 4 pieces snapped into a small hut.
192 STONE BUILDING SET (Stone tier): fitted pale-grey block wall with a timber
    top beam, flagstone floor, heavy plank door in a stone frame, slate-tile
    roof. Show the 4 pieces snapped into a small hut.
193 METAL-PLATE BUILDING SET: a timber frame clad in riveted metal plates; the
    same 4 pieces. Add a "TIER TINTS" strip showing the wall in Copper, Iron,
    Silver, Cobalt, Mithril and Adamantine colours.
194 BED (4 x 2 x 7): a low timber frame with a hide mattress, a fur blanket
    and a rolled cloth pillow.
195 CAULDRON (4 x 3 x 4): a squat dark-iron pot on 3 stub legs over a ring of
    stones and logs, with a ladle. Liquid is a solid colour.
196 SPIKE TRAP (4 x 1 x 4): a low timber frame with rows of short pointed
    wooden stakes, lashed with rope.
197 PLANTER (4 x 1.5 x 4): a raised timber box of dark soil with a rope trim.
199 TRIBE TOTEM, LEVELS 1–3 (3 x 8 x 3): three totems side by side in the
    Elder's Totem style: L1 a short carved post with one face; L2 taller with
    wings and a banner; L3 tall with wings, a banner, horns and a glowing amber
    eye gem.
EXTRACTION:
200 EXTRACTION PORTAL SITE: a 12-stud ring of low faceted rune stones with 4
    carved totem posts and a flat glowing teal-white rune disc in the centre.
201 CRATER HEART PORTAL: the central bonus exit: a larger ring of tall dark
    basalt monoliths with orange ember runes around a molten-orange rune disc;
    must clearly outrank 200.
202 PORTABLE EXTRACTION RUNE (Legendary): a hand-sized carved stone tablet with
    a gold (#F0AA28) rune. Show it HELD (a small item) and PLACED: planted
    upright in the ground on a small stone stand with 3 rune pebbles around it.
LANDMARKS:
203 OLD LIGHTHOUSE: a weathered stone tower on a sea rock with a timber top
    room, a brazier light cage and a rope-and-plank stair outside.
204 THE MONOLITHS: a circle of 7 tall faceted standing stones with carved rune
    bands and moss caps, one fallen.
LOBBY STATIONS (in the style of the lobby buildings and the Elder's Totem):
205 REBIRTH SHRINE: a stone dais with a carved spiral rune stone, two braziers
    and a woven hide canopy.
206 RAREWORK TABLE: a heavy timber workbench with a jewel vice, a small anvil,
    gem trays and a hanging lamp.
207 RECENT EXTRACTIONS BOARD: a wide timber notice board under a small shingle
    roof with pinned hide notes and a carved portal symbol.
PATHS AND FENCES:
211 TIMBER FENCE: a split-rail fence: posts, 2 rails, rope lashings; a straight
    section and a corner.
212 WAYFINDING POST: a thick carved post with 3 arrow boards and a small lantern
    hook.

=== D. NEW WORLD BUILDINGS (points of interest and events) ===
351 SHATTERED KEEP TOWER (about 24 x 24 x 40): the broken central tower of the
    old keep, centrepiece of the Guardian's arena. Thick stone block walls, the
    top third sheared off at a slant, broken timber floor beams sticking out,
    a tall arched doorway, ivy and moss caps, fallen blocks at the foot. Show a
    FLOOR PLAN of the ground floor.
352 KEEP CORNER TOWER (about 12 x 12 x 22): a square ruined stone tower for
    the keep's curtain-wall corners, crenellated top with gaps, arrow slits,
    a doorway at wall-walk height. Variants: INTACT and COLLAPSED.
353 FALLEN TEMPLE SANCTUM (about 30 x 30 x 14): a raised stepped stone
    platform with a ring of 6 broken columns, a cracked triangular roof slab
    fallen across one side, and a stone altar at the centre.
354 WATERMILL (about 20 x 14 x 16): the mill at Mill Bridge. A timber mill
    house on a stone footing, thatch roof, an undershot water wheel on one
    side, a sack hoist beam. Water is not part of the model.
355 FERRY LANDING (about 16 x 10 x 6): the landing at Reed Ferry and Ferry
    Bridge. A timber landing stage on posts, a rope-pull raft ferry tied up
    beside it, two tall posts with a pulley rope between them. Show the RAFT
    alone as a close-up.
356 DRIFTWOOD SHACK (about 12 x 10 x 9): a lean fisher's hut at Driftwood
    Cove built from bleached pale driftwood, a patched hide roof, a net-drying
    rack and a few floats.
357 EMBERHOLLOW CAVE GATE (about 28 x 8 x 20, opening 12 x 10): a carved
    entrance framing the cave mouth: dark basalt pillars, a heavy lintel with
    a rune band, glowing orange crystals growing from the base (solid
    geometry). It stands in front of a rock face, which is not part of it.
358 SUNKEN SHRINE (about 18 x 18 x 14): a small stone shrine half-sunk in a
    lake: a mossy stone arch, steps leading down into the water line, two
    tilted pillars and a teal (#28DCD2) rune stone in the arch. Show the
    WATER LINE as a dashed line; the model continues below it.
359 SUMMIT CAIRN (about 8 x 8 x 10): the Frostpeak Summit marker: a stacked
    stone cairn with snow caps, a carved peak post on top, and strings of
    cloth flags in tribe colours running to two short stakes.
360 TRADER TENT (about 16 x 12 x 12): the trader at Tidewater and Mossfire
    camps: a large open canvas tent with a plank counter, hanging goods
    (hides, pots, rope coils), crates and a lantern.
361 RAIDER TENT (about 14 x 12 x 10): the Raider Camp tent: dark hide over
    a frame of rough poles, bold red painted stripes, a tall horned-totem
    standard with a red banner at the door.
362 RAIDER WATCH POST (about 8 x 8 x 16): a crude, leaning stilt tower of
    lashed poles with a hide roof, a red banner and a rope ladder.
363 WARLORD'S HALL (about 32 x 20 x 20): the main hall of Warlord's Hold: a
    big fortified timber longhouse on a stone base, horned gable ends, a heavy
    double door, red banners, braziers either side of the door. Show a FLOOR
    PLAN.
364 ABANDONED FORT GATEHOUSE (about 24 x 10 x 18): two timber towers joined by
    a covered walkway over a double gate, weathered and broken: missing planks,
    one gate leaf sagging, moss and vines. Variants: INTACT (for Timberwatch)
    and ABANDONED.

Start with sheet 048.
```
