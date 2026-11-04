# 048 Dock — spec

Reference: `art/blender/assets/references/048.png` (remade 2026-11-03; 1024 × 1536 px, "DOCK — BUILDING MODEL STUDY,
PAGE 048"). Builder: `art/blender/kit/mcp/m048.py` (`build()`, on `kit_parts` / `kit_build`). The earlier spec and
builder (a raised 10.6 × 19.2 × 8.3 pier on the old sheet) are in git history; nothing below depends on them except the
object names.

## Brief

- **Sheet:** 048 Dock (remake: yes). Family: none (shares only the timber/rope vocabulary of 050–052).
- **Class and budget:** structure (an open platform), ceiling 6,000, plan ≤ 5,400. Built: 3,890.
- **Size:** length = the tiling pitch, **16.0** (end planks at x ±8.000; the "MODULAR TILING (DOCK ENDS)" cell butts two
  modules end to end). Proportions from the hero f34 (posts 2 × 3, bay = 6.4, across 7.4, H / bay ≈ 1.1); the side
  cell's character (5 studs = 98 px) only sets the order of magnitude. Hero **16.0 × 9.69 × 7.20** (deck top 4.40,
  post tops 7.20, rope coils 5.82 / 6.12, swags dip to 5.12).
- **Hero view:** f34 at camera (−42, 18) (fit from the post caps: az −41.5, el ≈ 21). Other cells: r34 (−138, 18) is a
  redraw of the front (content only); FRONT, SIDE and REAR all draw the long side (content only; compared at az 0 /
  0 / 180); TOP is drawn with the long axis vertical (compared turned 90°).
- **Build frame:** long axis X (tiling axis), the open end (no rope) at −X, the roped end at +X, front −Y.
- **Parts:**
  | Part | What | Tris target / built |
  | --- | --- | --- |
  | TimberDockPost | mooring post ground → bevelled cap, bolt block, hex brass bolt, 2 rope turns | 400 / 368 |
  | TimberDockDeck | the 15 deck planks (0.9 thick, seams on the post faces) | 450 / 420 |
  | TimberDockBeam | one side-beam segment between two posts | 30 / 28 |
  | TimberDockCrossbeam | the end header across the deck under the end planks | 30 / 28 |
  | TimberDockBrace | one knee brace (post face → beam underside) | 12 / 12 |
  | TimberDockRope | one twisted sagging swag | 200 / 186 |
- **Palette** (calibrated; sheet medians in stage 4): `m048_wood` #914A16 matte (Timber Primary, swatch #B75C20);
  `m048_wood_deep` #673514 matte (Timber Secondary, swatch #7F421A: beams, header, braces; legs blend toward it);
  `m048_rope` #F4D486 matte, `m048_rope_dark` #CFA862 (one groove strand in five); `m048_brass` #EBA949 (bolts,
  rough 0.5, metal 0.2). In-between keys `m048_wood_x_deep_25` / `_50` (leg bands).
- **Lights / VFX:** none (the sheet shows none; its notes say "No baked effects").
- **Collision:** hero `precise` (walked on); Post `hull`, Deck / Beam / Crossbeam `box`, Brace `hull`, Rope `none`.
- **Checks to switch on in kit_verify:** `seams={"pitch": (16, 0, 0)}`; `walk` along the deck at y 0 and ±0.9 from
  x −7.6 to 5.4, feet at 4.40, ride on, planks skipped, a turning point at (4.6, 0) (the +X end rope closes the deck
  there, as drawn).
- **Cells (sheet px, for compare.py):** f34 (16,120,510,418); r34 (520,120,1010,418); front (17,520,262,712); side
  (270,520,520,712), character left out; rear (602,520,828,712); top (834,505,1010,718) rot90 1. Close-up
  (655,738,1012,1028); tiling (655,1032,1012,1262); swatches at (80,1345,140,1405), (220,1345,285,1405),
  (360,1345,425,1405).
- **Departures from HOUSE_RULES:**
  - Deck top **4.40**, not the raised-floor 2.60: a dock deck over water, scaled from the sheet (a 2.60 deck would put
    the posts below a player's head; the side cell puts them above). Not the old 5.6 either (below).
  - The front / side / rear orthographic cells are taller than the f34 for the same length (their W : H 1.89–1.96
    against ours 2.22); the hero wins, recorded as a miss.
- **Questions for the main session:**
  - The old model's ruling put the deck at 5.6, flush with M043's lower lawn and the 050–052 decks. The remade sheet's
    hero proportions give 4.4 at a 16-stud pitch; 5.6 would need a ~20-stud module or the orthographic cells' taller
    proportions. Keep 4.4, or rule 5.6?
  - The hero's +X end is roped, which blocks walking from one module into the next. A straight (both ends open)
    module is a one-line variant (`swags()` without `swag_end`) if Studio needs one.

## Stage 1 — Modelling

Every piece is its own closed shell from `kit_parts` or a small helper in `m048.py`; nothing is unioned. Pieces sink
0.02 (`SEAT`) into what carries them.
- **Posts** (6): 1.25 square, vertical edges chamfered 0.05, top ring inset 0.10 (a bevelled cap, close-up cell);
  centres x −6.4 / 0 / 6.4, y ±3.7. Rings at 2.25 and 2.75 for the leg colour bands.
- **Deck** (15 planks, 0.9 thick, chamfer 0.05, 0.04 seams, top 4.40): per bay three planks between the post faces
  (1.677 wide), under each post line one plank cut back to the posts' inner faces, and past each end post an end row
  of three pieces with butt joints on the post faces (f34 near corner). Bay planks end at y ±4.0, so the posts stand
  0.33 proud of them (close-up). Seams fall on the post faces, as the side cell draws them.
- **Beams** (4 segments): 0.725 × 0.76 at y 3.125–3.85 (mirrored), between the posts, under the plank ends.
- **Headers** (2, the exploded "Crossbeam ×2"): outside each end post (x 7.005–7.6), across the deck under the end
  row; their ends are the beam ends the side cell shows past the posts.
- **Bolt blocks** (6): 1.48 × 1.52 × 0.34 plates, front edges bevelled 0.07, on each post's outer face at z 2.74–4.26;
  **hex bolts** r 0.32, 0.18 proud, bevelled (close-up cell).
- **Knee braces** (4): on both long sides from each end post's inner face (z 0.70–1.75) up to the beam underside
  (1.55–2.75 from the post face), as the front / side cells.
- **X braces** (2, the exploded "Diagonal Brace ×2"): on the outer faces of each end's legs (r34 shows the −X one):
  member A whole, member B in two halves butted against A (no interpenetration), a small brass bolt at the crossing;
  tops seated under the header.
- **Rope:** two twisted turns per post (r 0.16, z 5.82 / 6.12), each a closed loop with 45° corner cuts so the coil
  reads round instead of a square collar; five twisted swags (r 0.15, 18 segments, sag to 5.12) along both long sides
  and the +X end, each end tucked 0.04 into the upper turn. The −X end is open, as the f34 and r34 draw it.
- Measured proportions (renders against the sheet, `compare.py`): f34 W : H 1.576 sheet / 1.487 ours, r34 1.696 /
  1.484, top 0.598 / 0.601, front 1.892 / 2.225, side 1.955 / 2.22, rear 1.698 / 2.226.

## Stage 2 — Optimisation and cleanup

kit_build cleanup (normals, ear-clipped caps, origin at the bottom centre, transforms applied). `kit_verify.run`
(structure class, seams and walk on): **problems list empty.**
- Tris: TimberDock 3,890 / 6,000 (posts 456, blocks 120, bolts 220, planks 420, beams 112, headers 56, braces 136,
  rope 2,370); Post 368, Deck 420, Beam 28, Crossbeam 28, Brace 12, Rope 186 (all < 1,000).
- Hero 68 shells: 0 non-manifold / boundary / wire / loose / zero-area / n-gons / duplicate verts / bowties; 0 winding
  errors, 0 self-hits, 0 parity-inward, 0 negative volume; min face corner 3.0° (0 under 3°).
- Contact: 0 floating, 0 unchained; bury: 0 buried, deepest 0.035 (rope into rope / post, joints 0.02).
- Seams at a 16-stud pitch: 0 crossing triangle pairs, nothing past ±8.000, gap at the seam 0.000, end sections the
  same (mismatch 0.000; three end-plank faces each end, z 3.55–4.35 inside the chamfers).
- Walk (deck, feet 4.40): no intersecting steps, no rises, clearance ≥ 0.36 (the end swag at the path ends); turning
  room at (4.6, 0) 0.55 clear at every yaw. No headroom limit (open sky).
- Sizes: hero 16.00 × 9.69 × 7.20 (target 16.0 × 9.69 × 7.20); offsets of the parts in the build frame stored as
  `m048_offset`.

## Stage 3 — UV

Smart UV (kit_build default, angle 45°, margin 0.008): 1,034 islands, 0 overlapping pairs, 0 flipped, min island gap
0.016, border 0.008, density 1.0, conformal stretch p95 1.03. The exporter writes its own palette UVs.

## Stage 4 — Materials, colour and texture

- **Sampled (sheet):** swatches Timber Primary #B75C20, Secondary #7F421A, Rope #E9BB75. Rendered regions: f34 wood
  median #9A4813 (dark tercile #6C320D, lit #E78537); side-cell wood #954815; plank tops lit #E88739–#EB8A3C, post /
  plank-end faces #9C4710 / #9E4D18; rope f34 #FCD275, side #FAC877; bolt (close-up) #F2A541.
- **Calibrated** with `MODEL.calibrate` (timber against the swatches, rope / groove / brass against the rendered
  medians), then trimmed against the final f34 render in linear light (wood less green and blue, rope green up,
  brass brighter). Final palette in the brief.
- **Re-measured on the final renders** (same masks on both images):

  | Region | Sheet | Ours |
  | --- | --- | --- |
  | f34 wood median / dark / lit | #9A4813 / #6C320D / #E78537 | #9C4713 / #6F3311 / #B85821 |
  | side-cell wood median | #954815 | #904312 |
  | f34 rope median | #FCD275 | #FFD072 |
  | side-cell rope median | #FAC877 | #F0C26E |
  | close-up post face | #9C4710 | #994614 |
  | close-up bolt | #F2A541 | #F6A740 |

- **Recorded (studio lighting, not scored):** the sheet lights horizontal faces much brighter than ours (f34 lit
  tercile #E78537 against #B85821; plank tops read brown-orange instead of bright orange). Rope lit facets clip
  toward #FFFD95.
- **Colour by role and position:** planks, posts and blocks timber; beams, headers and braces the secondary; legs
  blend timber → 25 % → 50 % secondary below the beams (rings at 2.75 and 2.25); one rope strand in five the groove
  key. Per-piece Tint ±0.05 (±0.03 rope, ±0.02 bolts) gives the subtle value variation the notes ask for ("solid
  colours only", so no mottling texture).

## Stage 5 — Lighting: skipped

The sheet shows no lamp, glow or emissive part. No Studio-side setting needed.

## Stage 6 — VFX: skipped

The sheet shows no effect (notes: "No baked effects"). Export STATS: 0 VFX sockets, 0 glow keys.

## Modeller's notes for the verifier

- Renders: `M048_views.png` (f34, r34, front, side (+X end), rear, top sheet views, exploded, scale) and close-ups
  `post_cu.png` and `xbrace_cu.png` (`build(close=True)`).
- compare cells are listed in the brief; the side cell is compared at az 0 (it draws the long side).
- Known misses (hero wins): orthographic cells taller than the f34; the rear cell's long-side X brace (ours: knee
  braces there, the X on the ends as the r34); the r34's bolt blocks on the corner posts' end faces (the f34 has end
  planks there instead); the top cell's side strips and missing rope.
- Library candidates (kept in `m048.py`): `pad` (a bevelled plate on any face), `hexbolt`, `clip` / `band` (a
  straight member clipped to a box, for X and knee braces), the corner-cut twisted rope turn, and a bevelled post cap
  (an option on `P.post`).

## Main session rulings (2026-11-04)

1. **Deck top 4.40** as the remade sheet's proportions give at the 16-stud pitch. It no longer matches the old 5.6
   ruling for M043 and 050–052; the remakes govern.
2. **The roped +X end stays** as the three-quarter views draw it. An open-ended variant for chaining docks is a later
   request, not part of this model.
3. The f34 governs over the taller front, side and rear cells (house rule); those are recorded misses.

## Stage 7 verification (round 1)

**Result: PASS, 8 / 10.** No blockers. The content of every cell is there and the technical checks are clean. The
misses below are minor, or they follow from the rulings (pitch 16, deck top 4.40, the hero governs).

Method: a read-only background session on the modeller's work-file copy (no `build()`, nothing saved).
`kit_verify.run` on all 7 objects and `compare.compare` on the six sheet cells (boxes and cameras from the brief). I
rendered my own close-ups (post, coil, both ends), and took colour medians from the sheet and the renders with the same
masks. Scratch output is in `<temp>/v048/`.

### Technical (kit_verify, re-run)

- `run(cls="structure", size=(16, 9.69, 7.2), seams=pitch 16, walk=` the brief's three lanes and the turn point `)`:
  **problems `[]`** (2.6 s).
- Hero TimberDock: 3,890 / 6,000 tris and 68 shells: post 6 / 456, block 6 / 120, bolt 8 / 220, rope 17 / 2,370,
  plank 15 / 420, beam 4 / 112, crossbeam 2 / 56, brace 10 / 136.
  - 0 non-manifold edges, boundary, wire, loose, zero-area faces, n-gons, duplicate verts or bowties.
  - 0 winding errors, self-hits, parity-inward faces or negative volumes. Thinnest corner 3.02°.
  - Contact: 0 floating, 0 unchained, 6 grounded. Bury: 0 buried, deepest 0.035 (rope in rope).
  - UV: 1,034 islands, 0 overlaps or flips, gap 0.016, border 0.008, stretch p95 1.03.
  - Tint against the normal: 0. Origin offset 0, transforms applied, no modifiers or custom normals.
  - 0 sockets and 0 glow keys, as the sheet shows none.
- Parts (all clean, all under 1,000): Post 368, Deck 420, Beam 28, Crossbeam 28, Brace 12, Rope 186.
- Collision: hero precise, Post hull, Deck / Beam / Crossbeam box, Brace hull, Rope none. Matches the brief.
- Seams at a 16 pitch: 0 crossing pairs, extent ±8.000, 0 past the seam, gap 0.000, end sections 3 / 3 faces at
  z 3.55–4.35, mismatch 0.000.
- Walk (feet 4.40):
  - Lanes y 0 / ±0.9: clearance ≥ 0.361 (the end swag at x 5.4), 0 intersecting steps, no rises.
  - Turning room: (4.6, 0) 0.554, (−6.4, 0) 0.99 and (0, 0) 1.67, 0 intersecting yaws.
  - Extra probes: a cross-deck path at x −3 has clearance 1.05. Lanes at y ±2.0 graze the end posts' rope turns
    (0.009). The turns stand 0.32 inside the post faces, so the 2-wide proxy has a clear lane of |y| ≤ 1.75. That is
    expected for a roped rail, not a problem.
- compare.py W : H (sheet / ours) reproduces the modeller's numbers: f34 1.576 / 1.487, r34 1.696 / 1.484, front
  1.892 / 2.225, side 1.955 / 2.220, rear 1.698 / 2.226, top 0.598 / 0.601.
- Housekeeping: the work file still holds 11 stale `FB_m048_*` materials from the old build (`wood_dark`,
  `wood_x_light_15`, `wood_x_deep_15`, `rope_x_dark_45` / `_90`, `wood_deep_x_wood_dark_*` / `_light_*`). Each has
  one user, but no TimberDock object uses them. If the GUI kit file has them too, purge them before export.

### Views against the sheet

- **f34 (hero), az −42 el 18.** Every part the sheet draws is there:
  - six posts, 2 × 3;
  - the open −X end and the roped +X end; swags along both long sides;
  - two turns on every post;
  - bolt blocks on the front faces of the three near posts;
  - knee braces from the end posts on the front long side;
  - the end planks past the end posts; 11 plank rows.

  The proportion misses. I measured the post-cap centres on both images; the method checked against our own render
  gives 1.76 against the true 1.73.
  - The sheet draws the two-bay span at about 2.2 × the across spacing (bay ≈ 1.1 × across). Ours is 1.73
    (bay 0.86 × across).
  - Height against across agrees (≈ 0.99 sheet, 0.97 ours).
  - So in the hero view the dock reads about 20 % short along its length.
  - The front cell (length / bay 2.52 sheet, 2.50 ours) and the top cell (W : H 0.598 / 0.601) agree with ours.
    Matching the hero would mean a longer pitch, or a lower deck than the 4.40 ruling, so this is a recorded miss.
  - The brief's "H / bay ≈ 1.1" doesn't reproduce from the f34: I measure about 0.9.
- **r34, az −138 el 18 (a redraw; content only).** Content matches:
  - the open −X end nearest the camera;
  - an X brace on that end with a bolt at the crossing;
  - knee braces on the rear long side;
  - swags on the other three sides.

  The end-face bolt blocks on the corner posts are a recorded miss. W : H 1.484 against 1.696 comes from the same
  length cause.
- **front / side / rear, az 0 / 0 / 180.** Content matches: three posts, the plank-end row, blocks with bolts, the
  side beam, two knee braces, and the swags with their lashings.
  - Plank thickness, beam depth, swag sag (26 % of the post above the deck, sheet 25 %) and coil height (56 %,
    sheet 54 %) all match.
  - The taller cells (ruled) and the rear cell's long-side X brace are recorded misses.
  - In these renders the back posts peek out beside the front ones because of the camera's 3.0 lens. That is the
    render, not the geometry.
- **top, rot90.** The 11 rows and W : H match. Misses:
  - the side strips (recorded);
  - our rope shows from above, where the sheet leaves it out (recorded);
  - the sheet's end posts sit almost flush with the deck ends. See Minors.
- **Close-up (post / rope joint).** Matches: the hex brass bolt on the block, the bevelled cap, posts standing proud
  of the planks, two turns, and the swag tucked into the upper turn. Our rope reads less like the sheet's round,
  twisted rope (see Minors).
- **Exploded.** All six parts are present. The sheet's "Longitudinal Beam ×2" is drawn full length; ours is a segment
  between posts, which the post footprint forces. Fine.
- **Colours** (medians with the same masks on both images):

  | Region | Sheet | Ours |
  | --- | --- | --- |
  | f34 wood median / dark / lit tercile | #9C4A13 / #6D320D / #E88738 | #9D4813 / #6F3311 / #B85922 |
  | r34 wood median / dark / lit | #954513 / #6B320F / #E78638 | #924413 / #662F11 / #B6571F |
  | front / rear cell wood median | #954815 / #964915 | #944612 / #8D4111 |
  | top cell wood median | #D26F26 | #B65517 |
  | front cell beam / brace | #7C3C13 / #854013 | #6E3211 / #6C3111 |
  | front cell plank-end face / bolt block | #C2621E / #C76119 | #9F4812 / #A14913 |
  | f34 rope (saturated mask) | #FCD476 | #FFD574 |
  | f34 rope, wide mask: shade p20 / median / lit p80 | #F1A943 / #FBCC6F / #FEEFA5 | #D2A85D / #FFD179 / #FFFF9F |
  | close-up rope: shade p20 / lit p80 | #F2A945 / #FEE698 | #CBA75B / #FFFF9C |

  The wood medians match within a few units. Lit tops and front faces are darker than the sheet's (#B85922 against
  #E88738, top cell #B65517 against #D26F26). That is studio lighting, recorded and not scored.

### Blockers

None.

### Minors

1. **Hero length.** In the f34 the dock reads about 20 % short along its length (bay 0.86 × across against the
   sheet's ≈ 1.1). The pitch and deck rulings force this, and the front and top cells agree with ours. Recorded.
   Correct the brief's "H / bay ≈ 1.1" (the f34 gives ≈ 0.9).
2. **Rope colour.** The shaded facets go olive-tan (#D2A85D against the sheet's #F1A943) and the lit facets clip to
   lemon #FFFF9F (sheet #FEEFA5). The rope reads paler and cooler than the sheet's golden rope, although the medians
   match. Fix: warm `m048_rope_dark` toward ≈ #D89A50, and take `m048_rope` down a touch (≈ #EEC77A) so the lit
   facets stay below clipping.
3. **Rope shape.** The 45° corner cuts make the turns flare into flat collars at the corners, and the twist reads as
   crumpled facets more than the close-up's spiral strands. Fix (optional): rounder turns (8 corners, or a bigger
   corner cut) and a regular strand twist with fewer, cleaner facets.
4. **Brace colour.** The braces read about 20 % darker than the sheet's (#6C3111 against #854013); the beam is
   closer (#6E3211 against #7C3C13). Fix (optional): blend the braces about halfway from `m048_wood_deep` toward
   `m048_wood`.
5. **Leg colour rings.** The rings at 2.25 / 2.75 show as faint horizontal steps on the legs in the f34; the sheet's
   legs are a single tone. Fix (optional): soften the steps with an extra in-between key, or start the blend lower.
6. **End overhang.** The deck runs 0.975 past the end posts' outer faces (0.78 post widths). The top cell puts the
   end posts almost flush with the deck ends, and the tiling cell gives about 0.4 post widths, so two butted modules
   show a 1.95-stud gap between the junction posts (sheet ≈ 0.5). The hero's near-corner overhang reads about the
   same, so this is recorded only.
7. **Seam slits.** The 0.04 through-gaps between planks show the ground as hairline light lines in a straight-down
   view (top render). Harmless in play. A shallow strip under the seams, or a narrower gap, would close them.
8. **Stale materials.** See Housekeeping above: purge the old `FB_m048_*` materials before export.

## Main session after round 1 (2026-11-04)

Passed 8/10. Minor 2 applied: `m048_rope` #F4D486 -> #EEC77A and `m048_rope_dark` #CFA862 -> #D89A50, so shaded rope
stops reading olive and lit rope stops clipping to lemon. The other minors stay recorded.
