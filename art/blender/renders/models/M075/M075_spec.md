# 075 Wall Walk — spec

Reference: `art/blender/assets/references/075.png` ("WALL WALK / BUILDING MODEL STUDY", page 075, remade sheet;
Timberwatch walls, gates & defenses set). Builder: `art/blender/kit/mcp/m075.py` → `build()`, on the shared library
(`kit_parts` / `kit_build`). No earlier builder or spec existed: this is a new build. Procedure:
`art/blender/kit/mcp/STAGES.md`; standing answers: `HOUSE_RULES.md`.

## Brief

- **Sheet:** 075 Wall Walk (remake: yes, first build). Family: none (same set as 069 Palisade, 072 Timber Gate, 073
  Barricade; helpers copied from m072 / m073 / m052).
- **Class and budget:** structure (walkable platform), ceiling 6000, plan 5400; built **5578** (the round rope turns
  cost 650 more than twisted 4-side turns, which read as flat plates). Every part under 1000. Large-model verification.
- **Size:** the side cell's R6 figure is 95.75 px = 5 studs → **19.15 sheet px / stud** (the front cell's post widths
  and heights give the same scale). Sheet: deck top 5.31–5.35, tall post tops 7.83–7.96, rail top 1.4 over the deck,
  posts 1.13–1.17 square, structure 9.9 (front) to 11.1 (top) long, 4.7–5.0 deep, stair 4.5 long (4 steps, rise
  ≈ 1.06). Built: deck top **5.22**, posts 1.10 square at x ±4.85 / ±1.617 and y ±1.95, tall posts 7.77, stubs 6.17,
  rail 6.02–6.72, stair 5 treads (rise 0.87, run 0.85) from x −5.105 to −9.355. Hero bbox **15.24 W × 8.27 D × 7.77 H**
  (rocks included; the timber is 14.6 × 5.0).
- **Deck height against the kit:** 5.22, against 048 Dock 4.40, 050 Bridge 2.60, 052 Boardwalk 3.00 (and the house
  rule's 2.60): the highest raised floor in the kit, as the sheet draws (deck above the figure's head). The 069
  Palisade's log tips stand 7.65–12.15 (most 8.65–10.3; the pointed tips start about 1.2 lower). A 5-stud character
  on this deck has its head top at 10.2 and eyes at about 10.0: it sees over every palisade log except the two
  posts (10.6, 12.15), L8 (11.65) and L12 (10.3) — i.e. a defender can look over a 069 wall standing behind it. On a
  4.40 dock-height deck (eyes ~9.2) it would see over the log shoulders but not most tips.
- **Hero view:** f34 cell (20, 180, 508, 512) at camera (−28, 26); r34 (520, 180, 1010, 512) at (−156, 22); front
  (18, 595, 300, 765) at (0, 0); side (316, 595, 450, 765) at (−90, 0) ("side view (left)"); rear (518, 595, 760,
  765); top (768, 595, 1012, 765). The f34 box starts under the cell label and clips the back-right post's top.
- **Stair placement (hero rule):** the f34, the front cell and the r34 all put the stair at the **−X short end**,
  treads running along Y between the −X corner posts, descending −X (tread edges and the stringer profile read so in
  all three). The top view, the floor plan, the side cell and the rear cell instead put it off the front long side at
  the left (and the rear cell then hides it). HOUSE_RULES: the hero governs; those four cells are recorded misses
  (content: the stair is there, at the left/front-left), not blockers. The older W12 WallWalk read it the same way.
- **Parts:**
  | Part | What | Tris |
  | --- | --- | --- |
  | TimberWallWalk (hero) | the whole wall walk | 5578 |
  | TimberWallWalkPost | Upright Post (Main): 7.77 post, foot band, bevelled cap, rim and rail rope collars | 540 |
  | TimberWallWalkRailPost | Railing Post (Top): stub top length (2.15) with cap and bolt | 58 |
  | TimberWallWalkRailBeam | Railing Beam: 3.0 × 0.48 × 0.70 rail | 28 |
  | TimberWallWalkRailSegment | Railing Segment: one bay's rail with baluster and bolt | 70 |
  | TimberWallWalkFloorPlank | Floor Plank: 8.0 × 0.61 × 0.30 | 28 |
  | TimberWallWalkWallPlank | Wall Plank (vertical): one bay's three planks, 4.18 tall | 60 |
  | TimberWallWalkBrace | Support Brace (diagonal) of one bay | 20 |
  | TimberWallWalkStairs | Stair Steps: five block treads, two solid stepped stringers | 236 |
  | TimberWallWalkBanner | Banner (optional): rod, knobs, hem, swallowtail, stripes, double diamond | 268 |
  | TimberWallWalkRock | Footing Rock: flat-topped faceted stone 2.1 × 1.6 × 1.15 | 44 |
- **Palette** (sheet medians with `M.sample` / swatches with `M.raw_sample`, then `MODEL.calibrate`, then timber scaled
  in linear light so the compare render's brown median matches): timber rendered #B5611F [swatch #C06A22] →
  `#A26023` (f34 render median #B6621E); cut ends `#C2843A`; deep `#693F1A`; rope rendered #F6B74B [#F4BF72] →
  `#C29745`, deep strand `#93702F`; banner #FC1E16 [#CE2C24] → `#E81C1A`, hem `#8E1212`; cream `#F2E6CF` (calibration
  drifted pink #F0C1B0; kept by hand as on m072); rock #AAA29B [#888785] → `#8C8A8A` (render #A9A199), foot band
  `#6E6C6C` mix. All matte (roughness 0.8–0.95).
- **Lights / VFX:** none (the sheet shows no glow, light or effect).
- **Collision:** hero precise (walked on); Post, RailPost, RailBeam, RailSegment, FloorPlank, WallPlank box; Brace,
  Rock hull; Stairs precise; Banner none.
- **Checks switched on in kit_verify:** `cls="structure"`; `walk`: three paths (y −0.03 / 0 / 0.03) from the ground at
  x −11 up the stair and along the deck to x 3.6, ride on, floors skipped (`plank`, `rim`, `foot`), turning room at
  (−3, 0), (0, 0), (3, 0) on the deck. Model check `deck_check`: deck samples, tread tops, risers, rail height,
  stair-opening width.
- **Departures from HOUSE_RULES (ruled here):**
  - Deck at **5.22**, not 2.60: the sheet's wall-walk height (5.3), needed to see over a palisade (above).
  - **Five steps, not the sheet's four:** HOUSE_RULES' risers ≤ 0.87 at the sheet's deck height need six rises
    (5.22 = 6 × 0.87); four steps would be 1.04–1.06 risers (a Studio jump). Alternative if the main session prefers
    the sheet's step count: `N_STEPS = 4` gives deck 4.35 (≈ Dock 4.40, the sheet at 0.82 scale) with one constant.
  - Stair at the −X end (hero), not off the long side (top / plan / side / rear cells) — see above.
  - Front long side open above the deck (stub posts, no rail), as the f34 draws; back and +X end railed.
  - Rope collars are plain turns (no X diagonals of the lashing close-up): budget.
- **Questions for the main session:** the step count / deck height choice above (five steps at 5.22 built).

## Stage 1 — Modelling

Build frame: long axis X, front −Y (banner face), deck centred on x 0 / y 0; the origin is the bbox bottom centre
(`m075_offset` [−2.004…] carries the stair's shift). Every piece is its own closed shell, seated 0.002–0.05 into what
holds it (no booleans).
- **Posts** (1.10 square, chamfer 0.06, bevelled cut-wood cap 0.22 / inset 0.17): back row and front-right to 7.77
  (railing posts; the four corners' tall ones carry a pale 0.32 foot band, the r34's plinths), front-left / F2 / F3
  stubs to 6.17.
- **Rims:** long rims |y| 1.40–2.225 (inner face on the post inner faces), end rims |x| 4.30–5.125, z 4.16–5.21 (the
  −X end rim, the stair landing, to 5.22), ends 0.03 into the posts. **Deck:** five planks along X, 0.30 thick, top
  5.22, one staggered butt joint each, 0.02 into the long rims, 0.003 off the end rims.
- **Walls:** vertical planks (6-sided, outer edges chamfered 0.08 = the V seams) under the rims, 0.30 thick, outer
  faces |y| 2.30 / |x| 4.75, three per bay, four per end. **Braces** (0.50 × 0.28) on the long walls' outer faces,
  cut to the bay and to 0–4.14: front bays 1 and 3 "\" (f34), rear bays as the r34 (/ \ /).
- **Railing:** rail 0.48 × 0.70 (z 6.02–6.72) between the back posts and across the +X end; a 0.40 baluster under each
  back bay's middle with a bolt on the rail.
- **Rope collars** (P.rope, round 5-side turns with spiral strands, r 0.14, 0.22 apart): three turns at the rim
  (4.32 / 4.54 / 4.76) on every post and at the rail (6.15 / 6.37 / 6.59) on the railing posts. Each turn is the
  offset loop round the post, cut wherever a registered member (rim, rail, stringer, tread) enters the post, each run
  ending 0.04 inside it (m073's method, generalised to any axis box); runs under the deck and in the stair lane are
  left out.
- **Stair:** `P.stairs` (one board per tread, tread 0.84 thick = chunky blocks 0.03 over the next) in a frame turned
  to descend −X from the −X end rim; two solid stringers (|y| 1.40–1.75, in line with the −X posts) with stepped tops
  0.40 over each tread, a top block to 4.92 against the post, a sloped underside 1.60 under the nosing line, foot on
  the ground.
- **Banner:** m072 recipe on a rod (r 0.11, z 5.03, over the stub collars) in a hem sleeve 0.02 into the front rim of
  the middle bay; cloth 1.40 wide, tips 1.00, notch 1.70; cream stripes and double diamond.
- **Rocks:** six flat-topped faceted stones (m073 footing-stone outline, 2.1 × 1.6 × 1.15) slid against the post feet:
  front at x −4.85 / −2.05 / 4.85, rear at 3.20 / −1.40 / −4.85.

## Stage 2 — Optimisation and cleanup

kit_verify clean (problems list empty):
- Tris: hero 5578 / 6000; parts 540, 58, 28, 70, 28, 60, 20, 236, 268, 44.
- 0 non-manifold, bowties, boundary / wire / loose, zero-area, n-gons, duplicate verts; 0 winding errors, inward
  faces, self-intersections; 0 floating / unchained / buried shells; no pierced banner; transforms applied, origins
  bottom centre. The RailPost (cap) and Rock (darker foot) carry `kit_shading_ok` (cut-wood cap / ground grime by
  height, as m073 ruled).

## Stage 3 — UV

`kit_build.cleanup` (angle-based unwrap, margin 0.008): UV checks clean on every object.

## Stage 4 — Materials and colour

Values in the Brief and `PALETTE`. Colour by role: alternate deck planks and wall planks a step toward deep; caps and
plank ends cut wood; braces a touch toward cut wood; balusters a touch darker; rocks' lowest 0.30 darker; per-piece
Tint ±0.05 and broad mottling on planks, cloth and rocks. Compare renders: f34 / front brown medians #B6621E /
#B5611E against the sheet's #B5611F / #B35D1E; rock #A9A199 against #AAA29B. The rear faces render darker (#924F19
against #B56520): studio lighting, recorded.

## Stage 5 — Lighting

Nothing to do: the sheet shows no emissive part or light. No Studio-side setting.

## Stage 6 — VFX

None: the sheet shows no glow, smoke, dust or effect. No sockets.

## Checks

- `walk` (kit_verify): three paths up the stair and along the deck — min clearance 0.124–0.184 (back post rail
  collars), 0 intersecting steps, no headroom limit (open sky), rises 0.835 + 0.035 at each nosing chamfer then 0.87
  (all ≤ 1.0); turning room 0.297 / 0.435 / 0.297, 0 intersecting yaws.
- `deck_check`: 25 deck samples all at 5.220; tread tops 0.87 / 1.74 / 2.61 / 3.48 / 4.35, landing 5.22 → six even
  risers of 0.870 (HOUSE_RULES ≤ 0.87); rail top 1.50 over the deck (stops a character; the stair end has none);
  stair opening between the −X posts 2.80 at tread, rim and deck+0.5 heights (proxy 2.0 wide).

## Renders and compare

`M075_views.png` (f34, r34, front, side, rear, top, exploded, scale). `m075.compare()` writes the compare sheet to
`<temp>/RBLX-Flintborn/compare/M075/`. Content W : H, sheet / ours: f34 1.422 / 1.360, r34 1.562 / 1.387, front
1.734 / 1.934 (the fifth step and longer deck), side 0.831 / 0.992 and rear 1.336 / 1.899 and top 1.467 / 1.896 (those
cells draw the stair off the long side or omit it; recorded misses).

## Known minors

- Collars are three plain turns; the lashing close-up's crossing strands are not modelled (budget).
- Sheet "ortho" cells are drawn slightly from the left (end wall planks under the stair show); ours are true elevations.
- The sheet's stair stringer top blocks are chamfered caps in a lighter tone; ours are a plain sawtooth.

## Rulings (main session, 2026-11-04)

- **Five steps, deck 5.22:** kept. The sheet's deck height (5.3 at figure scale) and the house riser limit (0.87)
  govern over the labelled step count; four steps would either break the riser limit or drop the deck to 4.35.
  The step count is a recorded miss, not a blocker.
- **Stair off the −X short end:** the hero governs (f34, front and r34 agree); the four cells that draw it off the
  front long side are recorded misses.
- **Accepted as recorded:** no front rail above the deck (stub posts as the f34 draws), round 5-sided rope turns
  (hero 5578 over the 5400 plan, under the 6000 ceiling), plain three-turn collars, `kit_shading_ok` on RailPost and Rock.

## Stage 7 — verification (R1)

**Result: PASS, 8.0 / 10.** Fresh verifier, read-only, in a background session on the work-file copy
`wip/M075v.blend` (nothing rebuilt or saved). Verifier renders, compare pairs and close-ups (`cu_*`) are in
`renders/models/M075/verify/` (gitignored).

### Technical

- **kit_verify** (`cls="structure"`, the builder's `WALK`, hero and all ten parts): the builder's three walk paths and
  three turn points are clean; **0 problems** apart from the extra probe paths below.
  - Hero **5578 / 6000**, 137 shells, 15.239 × 8.27 × 7.77, origin bottom centre, transforms applied. Parts: Post 540,
    RailPost 58, RailBeam 28, RailSegment 70, FloorPlank 28, WallPlank 60, Brace 20, Stairs 236, Banner 268, Rock 44
    (all < 1000).
  - 0 non-manifold, boundary, bowties, n-gons, zero-area, duplicate verts; 0 winding, parity or self-intersection
    problems; floating 0, unchained 0, buried 0 (deepest 0.04); banner not pierced; UVs clean; min corner 7.42°.
  - **Walk** (builder's paths y −0.03 / 0 / 0.03): rises 0.835 + 0.035 at each nosing then 0.87, 0 intersecting
    steps, min clearance 0.124–0.184 (the back posts' rail collars), no headroom limit; turning room 0.297 / 0.435 /
    0.297 at x −3 / 0 / 3, 0 intersecting yaws.
  - Extra probes (lanes y ±0.3 / ±0.4 on stair and deck, turns at x −4.0 and 3.7): the 2.0-wide proxy touches the
    stringers at |y| 0.4 (stair lane 2.80 between them, slack ±0.40) and the back rail collars at y +0.3. Clear deck
    lane at the posts: front stub faces y −1.40 to back rail collars y +1.18–1.19 = **2.58** (2.80 between post faces
    at knee height; mid-bay the front is open and the balusters stand at y +1.75); the centre line has 0.15–0.40 slack
    each side. Walkable; noted, not a problem. The
    x 3.7 turn reaches the end rail (probe point too close to the end, not a defect).
- **deck_check** re-run: 25 deck samples all 5.220; treads 0.87 / 1.74 / 2.61 / 3.48 / 4.35, landing 5.22 → six
  risers of 0.870; rail top 1.50 over the deck (sheet 1.4); stair opening 2.80 at z 4.55 / 4.82 / 5.72.
- **Scale:** the side cell's figure is 96 px = 5 studs (19.2 px / stud); the side cell's posts are 153 px = 7.96
  (ours 7.77); deck 5.22 against the sheet's 5.3. Matches.
- **Naming / collision:** hero `TimberWallWalk`, unique in the repo; parts `TimberWallWalk<Part>`; collection
  `M075 Wall Walk`; collision hero precise, Stairs precise, Brace / Rock hull, Banner none, the rest box. Materials
  `FB_m075_*` only.

### Views against the sheet (compare.py, content W : H sheet / ours)

f34 1.422 / 1.36, r34 1.562 / 1.387, front 1.734 / 1.934, side 0.831 / 0.992, rear 1.336 / 1.899, top 1.467 / 1.896
(front, side, rear and top differ by the ruled stair placement and fifth step).

- **f34 (hero):** same layout and content: tall back row and front-right post, front stubs with bevelled caps, back
  rail with balusters and the +X end rail, rim collars on every post and rail collars on the railing posts, front bays
  1 and 3 "\" braces, banner in the middle bay, chunky five-block stair with stepped solid stringers off the −X end,
  three front rocks at the same posts as the sheet. Reads as the sheet.
- **r34:** rear bays "/ \ /" as the sheet; three rear rocks; stair on the right end. Ours looks more side-on and
  crowded (the front stubs and front-right post show between the back posts, and the sheet's r34 draws a railed far
  side); content matches the rulings.
- **front / rear orthos:** vertical wall planks with V seams and the diagonal braces read on both faces; brace width
  (0.50 against the 1.10 post, 0.45) matches the front cell (about 0.45). The rear cell's single inverted-V is a redraw
  of the r34; the r34 governs.
- **side / top / floor plan:** stair off the long side in the sheet; ruled miss. Top view: ours 10.8 × 5.0 (L : D
  2.16) against the sheet's 2.44: a little deeper than drawn, which buys the 2.8 deck lane.
- **Exploded:** all ten parts present and matching the sheet's labels; the sheet's Railing Segment is a rail between
  two post tops, ours a rail span with baluster and bolt.
- **Close-ups:** stair close-up matches (block treads, stepped stringers, collar at the corner post); the sheet's
  lighter chamfered stringer caps are recorded. Lashing close-up: ours are three faceted round turns, not the sheet's
  plump wraps with the crossing strand (ruled).
- **Colour** (medians over masks, sheet → ours): timber f34 #B0601E → #B6621E, front #B3631F → #B4611E; rope f34
  #FCB959 → #F0B147, front #FBBD5D → #F0B147; rock f34 #A9A19B → #A9A199, front #A9A29D → #A7A098; banner f34
  #FC1C17 → #FF1916. Rear faces darker (timber #B56420 → #A35A1C, rope #FABD5B → #CD9B3F): studio lighting,
  recorded.

### Blockers

None.

### Minors

1. **Rope collars** read as stacked faceted bands up close (5-sided section, the strands barely show) and as golden
   bands at hero distance; the sheet's wraps are fatter and pillowy. Ruled acceptable; if the budget is reopened,
   six sides on the rail collars only (the ones seen at eye level) would round them.
2. **Banner rod** is hidden in the dark red hem sleeve; the sheet shows a light wooden rod with gold knobs over the
   cloth. The knobs (r 0.12) are small and dark. Larger, lighter knobs (r ≈ 0.16, `TIMBER_END` or rope tone) would
   carry the read.
3. **Banner length:** cloth drop 0.81 of the deck height against about 0.9 on the sheet; `CLOTH["notch"]` and the
   tips could add about 0.4.
4. **Stair slits:** each tread block stops 0.03 above the tread below (`TREAD_T = RISE - 0.03`), so oblique light
   passes through a thin slit under each nose (ray probe: 308 rays through at x −8.21). Shows as faint streaks in
   the stair's shadow; not a hole a player can see through. Closing it needs `TREAD_T` and the foot block changed
   together (the foot block's top is `DECK - RISE * N_STEPS - TREAD_T`), not a one-liner.
5. **FloorPlank note** says 0.61 wide; the part is 0.552 (NOTES text).
6. Recorded, not scored: rear faces darker in the studio, the sheet's ortho cells drawn slightly from the left,
   plain sawtooth stringers, collars without the crossing strand, deck lane 2.58 at chest height at the back
   collars.
