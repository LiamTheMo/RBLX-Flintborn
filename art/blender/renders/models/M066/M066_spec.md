# 066 Canvas Shelter — spec

Reference: `art/blender/assets/references/066.png` (remade sheet, 1024 × 1536; "PAGE 066", "CANVAS SHELTER — BUILDING
MODEL STUDY"). Builder: `art/blender/kit/mcp/m066.py` → `build()` on the shared library (kit_parts / kit_build). The
earlier build and its long study followed the old sheet; git history keeps them.

## Brief

- **Sheet:** 066 Canvas Shelter (remake: yes). Family: none.
- **Class and budget:** structure (open shelter), ceiling 6000, plan ≤ 5400; every part under 1000.
- **Size:** post height from the hero cell (front-right post 253 px foot to cap = 12.0, HOUSE_RULES tall post; front-left
  222 px → 10.4) and the footprint from the four footings (X : Y 1.35–1.43 after perspective). Post centres 14.0 × 10.4.
  Hero 18.15 W × 12.75 D × 12.00 H (the width includes the banner rod and barrel outside the posts).
- **Hero view:** front three-quarter, camera (az −30, el 20). The "rear three-quarter" is a redraw of the front
  (banner moved to the left post): rendered at its own camera (−22, 24), judged on content. Front, side, rear and top
  cells disagree with the hero and with each other (banner on the right post, lantern under the canvas middle, side
  cell's back post short, square top footprint, three crates in the top and plan): content only.
- **Parts:**
  | Part | What | Tris |
  | --- | --- | --- |
  | CanvasShelter (hero) | 4 posts on footings, 5 X-lashings, ridge beam, canvas, banner and rod, lantern on a bracket, table and items, 2 benches, crate, barrel | 4056 |
  | CanvasShelterPost | 1.0 square post, 12.0 from the footing top, with its X-lashing (sheet "Post", "Lashing") | 364 |
  | CanvasShelterFooting | tapered stone footing 1.8 × 0.9 | 44 |
  | CanvasShelterRidgePole | 0.8 square ridge beam, 12.6 long (sheet "Ridge Beam"; old part name kept) | 28 |
  | CanvasShelterCanopy | the sagging canvas, corners tied, X creases | 288 |
  | CanvasShelterBanner | rod, red hem sleeve, three-tailed banner, white emblem both faces | 260 |
  | CanvasShelterLantern | square dark lantern, Neon glass, ring; heat_glow | 144 |
  | CanvasShelterTable | three-plank table 7.0 × 3.0, top 2.60, paper and two bottles | 356 |
  | CanvasShelterBench | two-plank bench 6.4 × 1.3, seat 1.50 | 228 |
  | CanvasShelterStool | two-plank stool 1.4 × 1.3, seat 1.50 (exploded and plan only) | 216 |
  | CanvasShelterCrate | closed X-braced crate 2.30 | 220 |
  | CanvasShelterBarrel | lidded hooped barrel 2.72 | 204 |
- **Palette** (sheet: swatch / hero-render median; ours = hero-render median after stage 4), all matte unless noted:
  timber `#C0621E` / `#9B4A13`; canvas `#FDE5BA` / `#FCE9C7` (lit) with a deeper hem; rope `#EAAF61` / `#E8A130`;
  stone `#AC9F99` / `#988F8C`; banner `#DF2016` / `#D51E12`, emblem white; lantern glass `#FCA70C` (Neon);
  lantern frame dark brown metal `#5A4230`; furniture planks lighter orange, crate and barrel darker brown.
- **Lights / VFX:** lantern glass Neon (emission 1.0) and one `heat_glow` socket at its centre (hero and Lantern part).
  Nothing else on the sheet.
- **Collision:** hero `precise` (players walk under and among the furniture); Post `hull`, Footing / RidgePole / Table /
  Bench / Stool / Crate `box`, Barrel `hull`, Canopy / Banner / Lantern `none`.
- **Checks to switch on in kit_verify:** `walk` under the canopy from all four open sides (front x −4.85, left y −0.8,
  back x 4.45, right y 2.4; turning room at (−5.2, −0.8)); sockets and stored points; the model check `shelter_check`
  (canvas underside ≥ 6.9, table top 2.60, seats 1.50).
- **Departures from HOUSE_RULES:**
  - Canvas sag: the front, side and rear cells (and the side cell's figure) put the canopy belly near head height; the
    headroom rule wins (lowest underside 7.05). Recorded miss: canvas share in those cells 2–9 % against 20–27 %.
  - The sheet draws the barrel (about 3.8) and crate (about 3.3) bigger than the kit sizes; kit sizes kept (miss).
  - Banner faces front on a rod running along X across the front-left post's front face. The hero cell draws the rod
    running front to back, but its banner's width (35 px, a front-facing cloth at this camera) and every other cell
    show it face-on; a cloth along the rod would read half as wide.
  - Lantern hangs from a short iron bracket off the front-right post's inner face, just under the canvas tie (the sheet
    hooks it to the canvas corner, which is no load path and would pierce the cloth). Lantern bottom 5.53 (sheet about
    5.1) so heads clear it next to the post.
  - One crate (hero) rather than the plan / top cells' three; no stool in the hero (the hero shows none) — the stool is a
    part only.
  - The short posts (10.4) are the Post part cut in Studio; the part is the 12.0 post (one reusable post, as labelled).
- **Questions for the main session:** none.

**Sheet cells** (pixel boxes, `m066.COMPARE`): f34 (95, 125, 525, 482) at (−30, 20); r34 (565, 62, 1010, 470) at
(−22, 24); front (16, 530, 268, 705) at (0, 0); side (274, 530, 455, 705) at (90, 0), figure cropped out; rear (524, 530,
772, 705) at (180, 0); top (776, 530, 1010, 705) at (0, 89.9). Swatches: x 42–72, y 1329–1340 timber, 1354–1365 canvas,
1382–1393 rope, 1409–1420 stone, 1436–1447 banner, 1461–1472 lantern.

## Stage 1 — Modelling

One function per exploded part, the hero assembled from them (`hero_all`); every piece a closed shell seated
0.002–0.03 into or onto what holds it, no booleans, no subdivision.
- **Footings** (`footing`): 8-sided tapered blocks, 1.8 at the foot, 1.6 at 0.72, flat 1.36 top at 0.90 (close-up
  "Post & Footing"). **Posts** (`post`): 1.0 square, vertical edges chamfered 0.05, from 0.88 (seated 0.02) to 10.4
  (left pair) / 12.0 (right pair), top edge bevelled 0.06.
- **Ridge beam** (`ridge`): 0.8 square, chamfered, along Y on the tall posts' inner faces (sunk 0.01), z 10.15–10.95,
  y −6.6 to 6.0 (0.9 past the front-right post's front face, as the hero shows).
- **Lashings** (`lashing`, `turn`, `diagonals`): two corner-cut twisted turns (r 0.16, m048 / m050 language) and an X
  of 4-sided twisted diagonals (r 0.15) on each listed face; on faces carrying the rod or the beam the diagonals go
  round it (P.x_lashing's `over`). Front-left 8.40 / 9.60 (front face over the rod, left face); back-left 8.40 / 9.60;
  front-right two stacked lashings, 8.92 / 9.64 (canvas) and 9.99 / 11.11 (over the beam); back-right 9.62 / 11.11 (over
  the beam, back and right faces).
- **Canvas** (`canvas_sheet`, a local copy of P.canvas): one closed 0.10 slab on a 7 × 7 grid, corners at the posts'
  inner corners (front-left 9.10, back-left 9.10, front-right 9.35, back-right 10.12 up under the beam), sag front 1.95,
  left 1.70, back 1.60, right 1.50, centre 2.20; the sag is eased 45 % along the two diagonals (fading to nothing at the
  centre) so the X of tension creases from the tied corners reads; centre-pointing triangulation. Turns sit above and
  below each tied corner, never through the cloth.
- **Banner** (`banner`): round rod r 0.18 along X across the front-left post's front face at 8.85, 2.7 past the post's
  left face; red hem sleeve; three-tailed cloth 2.05 × 5.8 (tails at 2.75) facing front, 0.36 clear of the turns; white
  diamond emblem on both faces (P.banner / P.emblem).
- **Lantern** (`lantern`): P.lantern 1.0 wide, glass 0.72 × 1.15, base 5.53, ring up to an iron bracket (P.bracket) on
  the front-right post's inner face, arm at 8.35, hanging 1.6 inside the post at the front edge.
- **Furniture**: table 7.0 × 3.0 (three 0.4 planks on end cleats, four chamfered 0.54 legs, end rails, a stretcher),
  paper and two bottles; back bench 6.4 and front bench 5.8 (two planks on cleats, four legs, rails, stretcher); stool
  (part only); P.crate (closed, 2.30) and P.barrel (lidded, 2.72). Layout from the hero: table centre (−0.2, −0.9),
  benches at y 1.55 and −3.40, crate (4.90, −0.60), barrel (−7.30, 2.40) just outside the left side by the back-left
  post.

## Stage 2 — Optimisation and cleanup

`kit_verify.run(cls="structure")`: **0 problems**. Hero 4056 / 6000 (rope turns 1200, diagonals 512, legs 336, canvas
288, plank tops 196, …), 117 shells; parts 28–364. 0 non-manifold edges or verts, boundary, wire, loose, zero-area,
duplicate verts, n-gons or bowties; winding errors 0, parity-inward 0, self-intersections 0; normals outward; origin at
the bottom centre, transforms applied, no modifiers or custom normals. Thinnest corner 1.49° (29 under 3°: long rope
and canvas strips; floor 0.3°). Floating 0, unchained 0; deepest burial 0.072 (a diagonal end in its turn, rope-in-rope
limit 0.08), else ≤ 0.032; nothing passes through the canvas or banner. Two fixes on the way: the canvas rim quads
twisted where the sag is steep and read as inward faces (now two triangles each), and the diagonal ends were pulled out
of the turns (1.65 r) with the second diagonal lifted 0.24 where they cross.

**Walk check** (5.5 proxy, ground): front (−4.85, −10 → −0.5) clearance 0.15, headroom 7.11; left (−11, −0.8 → −4.5)
0.30, 7.15; back (4.45, 11 → 1.5) 0.43, 7.89; right (11, 2.4 → 3.9) 0.70, 7.83; 0 intersecting steps; turning room at
(−5.2, −0.8) 0.38. Canvas lowest underside 7.05 (top 7.15). Table top 2.60, all four seat points 1.50.

## Stage 3 — UV

kit_build's angle-based unwrap (margin 0.008): 0 overlaps, 0 flips, island gap 0.016, border 0.008, even density.

## Stage 4 — Materials, colour and texture

Swatches and hero-render medians sampled on the sheet (`<temp>/.../samp.py`, class masks on the compare cells).
`MODEL.calibrate()` set the woods and metal; the dome pulled the canvas salmon (`#F4BFAA`), so the canvas, rope, stone and
banner were then corrected against the hero render itself. Hero-cell class medians, sheet / ours: canvas `#FCE9C7` /
`#FFE9BD`, wood `#9B4A13` / `#9F4E14`, rope `#E8A130` / `#DE9C2B`, stone `#988F8C` / `#9C8D84`, banner `#D51E12` /
`#D51B10`; front cell canvas `#FDE7BB` / `#FFE6BC`, rope `#E7A640` / `#E2A028`. Recorded, not scored: the side and rear
cells see the canvas underside and the posts' shaded faces (canvas `#DFCCBC`, wood `#793B0E` in the side cell against the
sheet's painted-bright `#FBE1B7` / `#B45B19`); the crate and table sit in the canopy's shadow in the hero render.
Colour by role and position only: canvas hem by distance from the edge (P.canvas bands), footing foot band by height,
per-plank / per-stave / per-face Tint, broad mottling on canvas, stone and banner; the crate's hidden bottom and lid
take the mean Tint so nothing follows the face normal (kit_verify colour check clean).

## Stage 5 — Lighting

Lantern glass `m066_glow` at emission 1.0 → exports as Neon. Studio: the `heat_glow` socket's PointLight gives the
warm pool under the canopy (Requires Manual Validation in Studio).

## Stage 6 — VFX

One `heat_glow` socket at the glass centre (5.40, −5.20, 6.37) on the hero and on the Lantern part; export stats report 1
socket and the glow key on each. Nothing else on the sheet.

## Notes for the verifier

- Compare: `m066.compare()` → `<temp>/RBLX-Flintborn/compare/M066/M066_compare.png`. W : H sheet / ours: f34 1.20 / 1.11
  (the sheet box includes the title text), r34 1.10 / 1.07, front 1.45 / 1.51, side 1.08 / 1.05, rear 1.44 / 1.40, top
  1.11 / 1.40 (the sheet's top cell is square).
- Library candidates (in `m066.py`, for the main session): `canvas_sheet` (P.canvas plus tension-line ridges, and rim
  quads split into triangles: P.canvas's rim quads twist and fail the parity check when the sag is steep); `turn` +
  `diagonals` (P.x_lashing's X on corner-cut turns, on several faces, with `over`).
- Background renders: overwriting an existing PNG in `renders/models/M066/` sometimes failed with "cannot save"; deleting
  the old PNGs before a render run avoided it.

## Main session rulings (2026-11-04)

The departures noted in the brief stand and are not to be scored:
- the canvas kept at walk-under height against the side and rear cells' deeper sag (house headroom rule);
- the kit sizes for the barrel and crate;
- the banner facing front;
- the lantern hung from an iron bracket on the post;
- one crate in the hero;
- the stool as a part only.

## Stage 7 verification (round 1)

**Result: FAIL, 6/10.** Technically clean, and the layout, content and departures match the hero cell. Three visual blockers remain: the posts and footings are thinner than the sheet in three cells, the crate reads as a plain dark box, and the timber renders about 20 % darker than the sheet on matching lit faces.

### Technical (re-measured in a read-only copy, `M066v.blend`)

- `kit_verify.run(cls="structure", walk=m066.WALK, sockets, stored, size=(18.15, 12.75, 12.0))`: **0 problems** in 13.6 s.
  - Hero: 4056 / 6000 tris, 117 shells, size 18.153 × 12.750 × 12.000.
  - No non-manifold edges or verts, boundary, wire, loose, zero-area faces, n-gons, duplicate verts or bowties. Winding errors 0, parity-inward 0, self-intersections 0. Origin at bottom centre, transforms applied, no modifiers.
  - Min corner 1.49° (29 corners under 3°). Floating 0, unchained 0. Deepest burial 0.072 (rope diagonal in rope turn, within the 0.08 pair limit); everything else is ≤ 0.032. No pierces through the canvas or banner.
  - UV: 0 overlaps, 0 flips, gap 0.016, border 0.008. Colour-against-normal check clean. One `heat_glow` socket at (5.40, −5.20, 6.365), glow key `m066_glow`. Stored points present. K.check clean.
  - Parts are 28–364 tris and all clean.
- Walk (5.5 proxy):

  | Side | Clearance | Headroom |
  | --- | --- | --- |
  | Front | 0.15 | 7.11 |
  | Left | 0.30 | 7.15 |
  | Back | 0.43 | 7.89 |
  | Right | 0.70 | 7.83 |

  0 intersecting steps; turning room at (−5.2, −0.8) 0.38. One extra path of my own, along the back under the canvas (y 3.6, x −5 → 5.5), is clear (0.10, headroom 7.46).
  - Paths at x ±5.2 and y −4.75 clip the footings or the front bench. Those are my path choices, not defects: the open lanes are the modeller's four.
- Ray grid under the canopy: lowest canvas underside **7.053**, at (0.0, −2.9). Lantern lowest point 5.63. `shelter_check`: table 2.60, all four seats 1.50.
- `m066.compare()`, content W : H, sheet against ours:

  | Cell | Sheet | Ours |
  | --- | --- | --- |
  | f34 | 1.20 | 1.11 (sheet box includes text) |
  | r34 | 1.10 | 1.07 |
  | front | 1.45 | 1.51 |
  | side | 1.08 | 1.05 |
  | rear | 1.44 | 1.40 |
  | top | 1.10 | 1.40 (ruled square cell) |

  Re-rendered at 900 px into `<temp>/...`, with close-ups of every lashing, a footing, the crate, the table, the lantern, the banner and the barrel.

### Views against the sheet

- **f34 (hero).** The layout matches: beam on the tall right pair and past the front-right post, banner on the front-left post, lantern under the front-right corner, table with benches, crate right, barrel left by the back-left post, back-right corner high under the beam. The silhouette and canvas outline read right.
  - Posts are slender. Width : height above the footing is 1 : 7.7 against the sheet's 1 : 6.0 (front-left post).
  - The crate is a dark block jammed against the table end.
  - Timber is browner and darker.
  - Lashings are thinner, angular strands against the sheet's fat round coils.
- **r34 (redraw).** All content is present. It shows the same three differences as f34.
- **front.**
  - Post : spacing is 1 : 13.3 against the sheet's 1 : 10.9. At the sheet's 62 px per stud, the sheet's posts are 1.29 wide, its footings 2.0 wide × 1.37 tall, and its posts 12.2 / 11.0 tall. Ours: 1.0, 1.8 × 0.9, 12.0 / 10.4.
  - The barrel is hidden behind the front-left post, where the sheet shows it inside the post.
  - The crate face is flat dark: no X shows.
  - The canvas is shallow; this is ruled.
- **side.** The posts and footings repeat the front-view proportions (post : spacing 1 : 10.3 against 1 : 8.0). The lantern is hidden behind the front-right post; the sheet shows it. The ridge beam is visible; the sheet's ortho cells omit it, and the hero governs.
- **rear.** Content only. The crate and table read; the barrel is behind the back-left post.
- **top.** Content only (ruled).
- **Colours.** Hex medians of matching regions, sheet against ours:

  | Region | Sheet | Ours | Note |
  | --- | --- | --- | --- |
  | Front-left post, front cell | `#CC691E` | `#A04E14` | |
  | Front-right post, front cell | `#C36019` | `#9E4D13` | |
  | Post, side cell | `#CB681E` | `#783A0D` | shade face; recorded, not scored |
  | Front-left post, f34 | `#C86119` | `#A04E13` | |
  | Table, f34 | `#CE7B31` | `#AF642A` | |
  | Crate, f34 | `#9E4F16` | `#82411B` | |
  | Crate, front | `#9D4F17` | `#7B3911` | |
  | Barrel | `#984B16` | `#8C4415` | |
  | Footing, front | `#B7A7A0` | `#9D8D84` | |
  | Footing, f34 | `#AF9D94` | `#9C8E85` | |
  | Canvas, f34 | `#FDEBC3` | `#FFEABE` | |
  | Canvas, front | `#FDEBBF` | `#F2E8C3` | |
  | Banner | `#D61E13` | `#D51B10` | |
  | Rope, front-left | `#EDA144` | `#D4952F` | |
  | Rope, front-right | `#E58C27` | `#CF912D` | |

  The canvas and banner match in the same renders, so the exposure is right and the woods and stone are genuinely dark.

### Blockers

1. **Posts and footings are too slender.** Three cells agree (hero 1 : 6.0 against our 1 : 7.7; front and side as above), and the sheet notes ask for "chunky" forms.
   - Fix: set `PH` to 0.65 (1.3 square post) with the chamfer and cap scaled to match.
   - Set `FOOT_RINGS` to about (0, 1.05) / (1.10, 0.95) / (`FOOT_H` 1.30, 0.82), giving a 2.1 base, a 1.65 top and 1.30 high. `POST_Z0` follows.
   - Turns, diagonals, canvas corners, the rod and the beam all key off `PH`. Re-check the four walk paths and the turn point (the front lane loses about 0.15), the canvas underside (≥ 6.9) and the part sizes.
2. **The crate reads as a plain dark box.**
   - `crate()` passes `frame_t=(0.25, 0.25)`, so frame and panels share one key. The braces stand 0.05 proud. The key `m066_wood_dark` renders `#82411B` against the sheet's `#9E4F16`.
   - Fix: pass `frame_t=(0.0, 0.5)`, or draw the frame and braces in `m066_plank` over darker panels. Raise the braces to about 0.10 proud. Lighten the crate key until the rendered median reaches about `#9E4F16`.
   - Move the crate about 1 stud toward the front-right, around (5.0, −1.8), so it stands clear of the table end (gap now 0.45). Re-check the right walk path and the front-right footing clearance.
3. **Timber about 20 % too dark on lit faces** (front cell posts `#A04E14` against `#CC691E`; table `#AF642A` against `#CE7B31`). Footings are also dark (`#9D8D84` against `#B7A7A0`).
   - Fix: re-calibrate `m066_timber`, `m066_plank`, `m066_wood_dark` and `m066_stone` against matching lit faces (front cell, az 0), not whole-cell class medians. Re-check that the canvas stays clear of salmon.

### Minors (recorded; fix if cheap)

- **Canvas hem.** `m066_canvas_deep` shows as a salmon / peach outline round the canvas in every hero view. The sheet's edge is plain cream.
- **Lashings.** They read thinner and crumpled: 5-sided twisted turns and 4-sided diagonals, against the sheet's smooth fat coils with one clear X. The back-right corner shows only one turn above the beam. This is the accepted m048 / m050 rope language, so it is not scored.
- **Bottles.** About half the sheet's size (the sheet's green bottle is about 0.7 × 1.3).
- **Banner.**
  - The emblem has two side dots where the sheet has a horizontal arrow bar through the diamond.
  - The cloth hangs fully left of the post; the sheet's overlaps the post's left half.
  - The rod runs past the post's right face; the sheet's ends at about the post centre.
  - The sheet's red binding bands at the rod are missing.
- **Barrel.** Hidden behind the front-left post in the front cell and behind the back-left post in the rear cell. About 1.0 further out on −X would show it beside the posts, as the sheet's cells do.
- **Lantern.** Hidden behind the front-right post in the side cell.
- **Exploded render.** The crate is mostly behind the front-right post and the barrel behind the banner.
- **Text mismatches** in `m066.NOTES` and the spec:
  - hero "centres 13.2 x 9.2" (actual 14.0 × 10.4);
  - RidgePole "11.6 long" (actual 12.6);
  - Post "12.0 tall from the footing top" (the part is 11.12; 12.0 includes the footing);
  - Table "6.6 x 2.7" and Bench "6.0 x 1.2" (parts are 7.0 × 3.0 and 6.4 × 1.3);
  - spec "Lantern bottom 5.53" (measured 5.63).
- **Recorded, not scored.**
  - The canvas underside reads grey-taupe in the front, side and rear cells (studio shade).
  - The shallow canvas sag (ruled).
  - Kit sizes for the crate and barrel, and the single crate (ruled).
  - The top cell's square footprint.

## Main session after round 1 (2026-11-04)

Fix round, in this order:
1. **Blockers 1–3, as the verifier gives them:**
   - chunkier posts (1.3 square) and footings (about 2.1 base, 1.65 top, 1.30 high);
   - a crate with a lighter frame and braces standing about 0.10 proud, moved to about (5.0, −1.8);
   - timber, plank, dark wood and stone re-calibrated against the front cell's lit faces.
   Re-check the walk lanes, the turn point and the canvas underside (at least 6.9).
2. **Minors:**
   - plain cream canvas edge, no salmon hem;
   - bottles about twice the size;
   - the banner emblem's arrow bar, the cloth overlapping the post, the rod ending at the post, and the red binding
     bands;
   - the barrel moved about 1.0 further out on −X so it shows in the front and rear cells.
3. **Text:** bring the dimensions in `NOTES` and the spec in line with the model.

The lashing style and the studio-lit canvas underside stay recorded. Round 2 goes to a fresh verifier.
