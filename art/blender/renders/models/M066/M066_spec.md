# 066 Canvas Shelter — spec

Reference: `art/blender/assets/references/066.png` (remade sheet, 1024 × 1536; "PAGE 066", "CANVAS SHELTER — BUILDING
MODEL STUDY"). Builder: `art/blender/kit/mcp/m066.py` → `build()` on the shared library (kit_parts / kit_build). The
earlier build and its long study followed the old sheet; git history keeps them.

## Brief

- **Sheet:** 066 Canvas Shelter (remake: yes). Family: none.
- **Class and budget:** structure (open shelter), ceiling 6000, plan ≤ 5400; every part under 1000.
- **Size:** post height from the hero cell (front-right post 253 px foot to cap = 12.0, HOUSE_RULES tall post; front-left
  222 px → 10.4) and the footprint from the four footings (X : Y 1.35–1.43 after perspective). Post centres 14.0 × 10.4.
  Hero 17.60 W × 12.90 D × 12.00 H (the width runs from the banner rod's left end to the front-right footing; the depth
  from the ridge beam's front end to the back footings).
- **Hero view:** front three-quarter, camera (az −30, el 20). The "rear three-quarter" is a redraw of the front
  (banner moved to the left post): rendered at its own camera (−22, 24), judged on content. Front, side, rear and top
  cells disagree with the hero and with each other (banner on the right post, lantern under the canvas middle, side
  cell's back post short, square top footprint, three crates in the top and plan): content only.
- **Parts:**
  | Part | What | Tris |
  | --- | --- | --- |
  | CanvasShelter (hero) | 4 posts on footings, 5 X-lashings, ridge beam, canvas, banner and rod, lantern on a bracket, table and items, 2 benches, crate, barrel | 4104 |
  | CanvasShelterPost | 1.3 square post, 10.72 long (its top at 12.0 on the 1.30 footing), with its X-lashing (sheet "Post", "Lashing") | 364 |
  | CanvasShelterFooting | tapered stone footing, 2.1 base, 1.64 top, 1.30 high | 44 |
  | CanvasShelterRidgePole | 0.8 square ridge beam, 12.6 long (sheet "Ridge Beam"; old part name kept) | 28 |
  | CanvasShelterCanopy | the sagging canvas, corners tied, X creases | 288 |
  | CanvasShelterBanner | rod, two red bands, three-tailed banner, white diamond emblem and arrow bar both faces | 332 |
  | CanvasShelterLantern | square dark lantern, Neon glass, ring; heat_glow | 144 |
  | CanvasShelterTable | three-plank table 7.0 × 3.0, top 2.60, paper and two bottles | 356 |
  | CanvasShelterBench | two-plank bench 6.4 × 1.3, seat 1.50 | 228 |
  | CanvasShelterStool | two-plank stool 1.4 × 1.3, seat 1.50 (exploded and plan only) | 216 |
  | CanvasShelterCrate | closed X-braced crate 2.30: light frame, braces 0.10 proud, darker panels | 220 |
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
    hooks it to the canvas corner, which is no load path and would pierce the cloth). Lantern bottom 5.63 (sheet about
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
- **Footings** (`footing`): 8-sided tapered blocks, 2.1 at the foot, 1.9 at 1.10, flat 1.64 top at 1.30 (close-up
  "Post & Footing"). **Posts** (`post`): 1.3 square, vertical edges chamfered 0.065, from 1.28 (seated 0.02) to 10.4
  (left pair) / 12.0 (right pair), top edge bevelled 0.08. (Round 1 fix sizes; see "Fixes after round 1".)
- **Ridge beam** (`ridge`): 0.8 square, chamfered, along Y on the tall posts' inner faces (sunk 0.01), z 10.15–10.95,
  y −6.6 to 6.0 (0.9 past the front-right post's front face, as the hero shows).
- **Lashings** (`lashing`, `turn`, `diagonals`): two corner-cut twisted turns (r 0.16, m048 / m050 language) and an X
  of 4-sided twisted diagonals (r 0.15) on each listed face; on faces carrying the rod or the beam the diagonals go
  round it (P.x_lashing's `over`). Front-left 8.40 / 9.80 (front face: an X from the upper turn ending on the rod's top; left face); back-left 8.40 / 9.60;
  front-right two stacked lashings, 8.92 / 9.64 (canvas) and 9.99 / 11.11 (over the beam); back-right 9.62 / 11.11 (over
  the beam, back and right faces).
- **Canvas** (`canvas_sheet`, a local copy of P.canvas): one closed 0.10 slab on a 7 × 7 grid, corners at the posts'
  inner corners (front-left 9.10, back-left 9.10, front-right 9.35, back-right 10.12 up under the beam), sag front 1.95,
  left 1.70, back 1.60, right 1.50, centre 2.20; the sag is eased 45 % along the two diagonals (fading to nothing at the
  centre) so the X of tension creases from the tied corners reads; centre-pointing triangulation. Turns sit above and
  below each tied corner, never through the cloth.
- **Banner** (`banner`): round rod r 0.18 along X across the front-left post's front face at 8.85, from 1.85 past the
  post's left face to 0.45 right of its centre; two red bands round the rod; three-tailed cloth 2.05 × 6.0 (tails at
  2.75) facing front, its right edge 0.10 short of the post centre (over the post's left half), 0.07 clear of the lower
  turn; white diamond emblem with a horizontal arrow bar on both faces (P.banner / P.emblem, `arrow_bar`).
- **Lantern** (`lantern`): P.lantern 1.0 wide, glass 0.72 × 1.15, lowest point 5.63, ring up to an iron bracket (P.bracket) on
  the front-right post's inner face, arm at 8.35, hanging 1.6 inside the post at the front edge.
- **Furniture**: table 7.0 × 3.0 (three 0.4 planks on end cleats, four chamfered 0.54 legs, end rails, a stretcher),
  paper and two bottles (green 0.72 × 1.25, amber 0.62 × 1.06); back bench 6.4 and front bench 5.8 (two planks on cleats, four legs, rails, stretcher); stool
  (part only); P.crate (closed, 2.30) and P.barrel (lidded, 2.72). Layout from the hero: table centre (−0.2, −0.9),
  benches at y 1.55 and −3.40, crate (5.15, −1.75), barrel (−8.30, 2.40) just outside the left side by the back-left
  post (round 1 fix positions).

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

- Compare: `m066.compare()` → `<temp>/RBLX-Flintborn/compare/M066/M066_compare.png`. W : H sheet / ours (after the round 1
  fixes): f34 1.20 / 1.14 (the sheet box includes the title text), r34 1.10 / 1.10, front 1.45 / 1.46, side 1.08 / 1.06,
  rear 1.44 / 1.42, top 1.11 / 1.35 (the sheet's top cell is square).
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

## Fixes after round 1

The main session's fix list, applied in `m066.py` and rebuilt in the light work file (`wip/M066.blend`). No part was
renamed or dropped.

**Blockers.**
- **Posts and footings.** `PH` 0.65 (1.3 square post), vertical chamfer 0.065, top bevel 0.08. Footings 2.1 at the
  foot, 1.9 at 1.10, flat 1.64 top at 1.30 (`FOOT_RINGS`); posts seated 0.02 into the top (`POST_Z0` 1.28). Post :
  spacing in the front view is 1.3 : 14.0 (1 : 10.8; sheet 1 : 10.9). Turns, diagonals, canvas corners, rod and beam key
  off `PH` and moved with it. On the wider face the X runs flatter and the plain diagonals sank 0.12 into the turns (over
  the 0.08 rope-in-rope limit): their ends are now pulled 2.4 turn radii out of the turn (`PULL`, was 1.65); deepest
  rope-in-rope 0.065.
- **Crate.** P.crate with `frame_t=(0.0, 1.0)`: frame, lid and braces in `m066_plank` over `m066_wood_dark` panels, the
  braces thickened to stand 0.10 off the panels (`BRACE_PROUD`). Moved from (4.90, −0.60) to (5.15, −1.75): 0.70 clear
  of the table end, 0.20 past the front bench's end.
- **Timber, plank, dark wood and stone**, re-calibrated against lit faces in the front cell (az 0): the post front
  faces, the footing front, the table and bench front edges and the crate face. Linear-ratio steps from the render to
  the sheet, two rounds:

  | Key | Was | Now |
  | --- | --- | --- |
  | `m066_timber` | `#935018` | `#B96825` |
  | `m066_plank` | `#9A5E2A` | `#9A5621` |
  | `m066_wood_dark` | `#7D4316` | `#8B4C16` |
  | `m066_stone` / `m066_stone_deep` | `#908886` / `#726A68` | `#AAA4A4` / `#878080` |

  Re-measured, sheet against ours (medians of the same regions):

  | Region | Sheet | Ours before | Ours now |
  | --- | --- | --- | --- |
  | Front-left post, front cell | `#CD691F` | `#9F4D13` | `#CD681F` |
  | Footing, front cell | `#B5A69E` | `#998A81` | `#B7A9A1` |
  | Table front edge, front cell | `#A3561D` | `#AF6226` | `#AF581D` |
  | Bench front edge, front cell | `#AD591D` | `#A75D23` | `#A7541B` |
  | Crate, front cell | `#994C16` | `#8E4718` | `#9A4C15` |
  | Canvas, front cell | `#FDECC0` | `#F9E8C1` | `#F9E8C1` |
  | Front-right post, f34 | `#C4601A` | | `#CD681F` |
  | Crate, f34 | `#9F5017` | | `#AA551C` |
  | Footing, f34 | `#AE9C92` | | `#B6A8A0` |
  | Canvas, f34 | `#FDEFCC` | | `#FFEABE` |

  The canvas keeps its colour and shows no salmon. The table top in f34 renders `#C96929` (the verifier's sheet top
  `#CE7B31`).

**Minors.**
- Canvas edge plain cream: `canvas_sheet(..., deep=None)`, no hem colour.
- Bottles about twice the size: green 8-sided 0.72 × 1.25, amber square 0.62 × 1.06 (sheet's green about 0.7 × 1.3).
- Banner: a white horizontal arrow bar with arrowheads through the diamond on both faces (`arrow_bar`, replacing the
  side dots); the cloth's right edge 0.10 short of the post centre, so it overlaps the post's left half; the rod ends
  0.45 right of the post centre; two red bands round the rod. The front X of the front-left lashing ends on the rod's
  top (`rod_x`), so nothing crosses the cloth. The right band sits 0.33–0.65 left of the post's left face: at 0.15–0.47
  it touched the lower turn (one edge through a thin sheet).
- Barrel moved 1.0 out, to (−8.30, 2.40). It now shows left of the front-left post in the front cell (partly behind the
  banner) and right of the back-left post in the rear cell.

**Text.** `NOTES`: post 1.3 square and 10.72 long, footing 2.1 / 1.64 / 1.30, ridge beam 12.6, table 7.0 × 3.0, bench
6.4 × 1.3, post centres 14.0 × 10.4. In this spec: the brief's size, parts table and lantern bottom (5.63), stage 1's
footing, post, lashing, banner, bottle and layout numbers, and the verifier notes' W : H. `TARGET_SIZE` is now 17.60 ×
12.90 × 12.00 (the barrel and rod moved out; the footings grew).

**Checks.** `kit_verify` (structure, walk, sockets, stored points): **0 problems**. Hero 4104 / 6000 tris, 120
shells, 17.601 × 12.899 × 12.000. Parts: Post 364, Footing 44, RidgePole 28, Canopy 288, Banner 332, Lantern 144,
Table 356, Bench 228, Stool 216, Crate 220, Barrel 204. Floating 0, buried 0, deepest 0.065 (rope diagonal in a turn);
min corner 1.41°. One `heat_glow` socket at (5.40, −5.20, 6.365); stored seat and lantern points present.

| Walk | Clearance | Nearest | Headroom |
| --- | --- | --- | --- |
| Front, x −4.83 (was −4.85) | 0.12 | front-left footing | 7.12 |
| Left, y −0.8 | 0.30 | table top | 7.15 |
| Back, x 4.45 | 0.43 | table top | 7.92 |
| Right, y 2.4 | 0.70 | back bench | 7.85 |

0 intersecting steps; turning room at (−5.2, −0.8) 0.38. The bigger footing left the front lane 0.10 at x −4.85; at
−4.83 it is 0.12 from the footing and 0.13 from the table end. Canvas lowest underside 7.052 (top 7.152). Table top 2.60;
all four seats 1.50.

`m066.compare()` W : H, sheet / ours: f34 1.20 / 1.14, r34 1.10 / 1.10, front 1.45 / 1.46, side 1.08 / 1.06, rear
1.44 / 1.42, top 1.11 / 1.35 (ruled square cell).

**Left as they were (not on the fix list):** the exploded view still puts the crate behind the front-right post and the
barrel behind the banner; the lantern is hidden behind the front-right post in the side cell; the lashing style and the
studio-shaded canvas underside are recorded.

**For the main session.** In a hot palette swap (`MODEL.palette()` without a rebuild), kit_build does not resync the
mix keys whose second key shares the first's stem (`m066_stone_x_deep_35`, `m066_banner_x_deep_40`): it looks for
`m066_deep`. A rebuild sets them correctly.

## Stage 7 verification (round 2)

**Result: PASS, 8.5/10.** All three round-1 blockers are fixed. The posts and footings are chunky, the crate reads as a framed, X-braced crate, and lit timber matches the sheet within a few percent. The fixes are technically clean. No blocker remains. One fix moved something the wrong way: the barrel's move out on −X puts it directly under the back-left post in the hero and r34 views. It is a one-constant minor, listed first below.

### Technical (re-measured in a read-only copy, `M066v.blend`, taken after the round-1 fixes)

- `kit_verify.run(**m066.VERIFY, size=(17.60, 12.90, 12.0))` on the hero and its 11 parts: **0 problems**.
  - Hero 4104 / 6000 tris, 120 shells, 17.601 × 12.899 × 12.000. Parts: Post 364, Footing 44 (2.1 × 2.1 × 1.30), RidgePole 28, Canopy 288, Banner 332, Lantern 144, Table 356, Bench 228, Stool 216, Crate 220 (2.39 × 2.39 × 2.30), Barrel 204.
  - 0 non-manifold edges or verts, boundary, wire, loose, zero-area faces, n-gons, duplicate verts or bowties. Winding errors 0, parity-inward 0, self-intersections 0, negative volumes 0. Every shell matched to the register. Origin at the bottom centre, transforms applied, no modifiers or custom normals.
  - Min corner 1.41° (29 under 3°). Floating 0, unchained 0 (18 grounded). Deepest burial 0.065 (rope diagonal in a turn, within the 0.08 pair limit); every other pair ≤ 0.052. 0 pierces through the 14 thin shells.
  - UV: 0 overlaps, 0 flips, gap 0.016, border 0.008. Colour-against-normal check clean (worst 0.0).
  - Sockets: one `heat_glow` at (5.40, −5.20, 6.365), glow key `m066_glow`, on the hero and the Lantern part. Stored seat, lantern and centre points present on the hero, Bench and Stool. K.check clean.
- Walk (5.5 proxy, the spec's four lanes):

  | Side | Clearance | Nearest | Headroom |
  | --- | --- | --- | --- |
  | Front, x −4.83 | 0.12 | front-left footing | 7.12 |
  | Left, y −0.8 | 0.30 | table top | 7.15 |
  | Back, x 4.45 | 0.43 | table top | 7.92 |
  | Right, y 2.4 | 0.70 | back bench | 7.85 |

  0 intersecting steps. Turning room at (−5.2, −0.8) is 0.38. I also tried extra lanes and turn points of my own. Left at y 0.0: 0.39 from the barrel, headroom 7.14. Turn points at (4.45, 1.5) and (−4.0, 3.6): 0.36 and 0.35, 0 intersecting yaws. A front lane at x −3.0: 0.07 from the front bench. My back lane (y 3.6) and right-back lane (x 2.0) run into the back-right footing and the back bench at their ends. Those are my endpoint choices, not defects: the four open lanes are the modeller's.
- `shelter_check`: table top 2.60; all four seats 1.50. In a reopened file its canvas report is empty (`P.GEO` is filled only by a build), so its headroom test is skipped silently. My own up-ray grid from z 6.5 over x ±6.2, y ±4.4 (0.1 step) gives a lowest canvas underside of **7.053** at (0.0, −2.8), which meets the 6.9 headroom. Lantern lowest point 5.63.
- `m066.compare()`, content W : H, sheet / ours: f34 1.20 / 1.13 (the sheet box includes text), r34 1.09 / 1.10, front 1.45 / 1.46, side 1.07 / 1.06, rear 1.44 / 1.42, top 1.10 / 1.35 (ruled square cell). I re-rendered the pairs at 900 px into `<temp>/...`, plus close-ups of the crate, the front-left footing, the front-left and front-right lashings, the banner, the table and the lantern.

### Blocker check (round 1)

1. **Posts and footings: fixed.** In the 900 px front pair the posts are 87 px wide against 891 px between post centres (1 : 10.2); the sheet is 97 / 862 for the left post and 85 / 862 for the right (1 : 8.9 to 1 : 10.1). Footings are 138 × 85 px, against the sheet's 125 × 85. In the side pair, post : spacing is 1 : 7.3 against the sheet's 1 : 7.9. The footing close-up matches the "Post & Footing" close-up: a broad tapered stone block with a flat top. The hero now reads chunky.
2. **Crate: fixed.** It has a light plank frame and lid, braces standing proud in an X on every side face, and darker recessed panels. It reads as the sheet's crate in f34, r34, front and rear. At (5.15, −1.75) it stands 0.70 clear of the table end, with no contact with the front bench or the front-right footing.
3. **Timber colour: fixed.** Medians of matching regions, sheet / ours:

   | Region | Sheet | Ours |
   | --- | --- | --- |
   | Front-left post, front cell | `#CB671E` | `#CD681F` |
   | Front-right post, front cell | `#C3611A` | `#CD681F` |
   | Front-left post below the banner, f34 | `#C6611A` | `#CE691F` |
   | Footing, front cell | `#B6A69F` | `#B7A9A1` |
   | Footing, f34 | `#AE9C92` | `#B6A8A0` |
   | Crate face, front cell | `#9B4D16` | `#994B13` |
   | Crate front face, f34 | `#9A4C13` | `#9A4B13` |
   | Table front edge, front cell | `#A3541D` | `#AF581D` |
   | Barrel, f34 | `#9B4E19` | `#9E5215` |
   | Canvas, f34 | `#FDEBC1` | `#FFEABE` |
   | Banner, f34 | `#D71E14` | `#D51B10` |
   | Green bottle, front cell | `#909A4D` | `#879341` |

   The canvas shows no salmon, and its plain cream edge is in place.

**Fix-list minors:**
- Done: the cream canvas edge, the bigger bottles, and the banner's arrow bar, overlap, rod end and red bands (banner close-up). All of these read as the sheet.
- Done: the text. NOTES and the spec now give 1.3 posts, 10.72 Post part, 12.6 beam, 7.0 × 3.0 table, 6.4 × 1.3 bench, 14.0 × 10.4 post centres and lantern bottom 5.63, all matching the measurements.
- Barrel: half done, and it made the hero worse (Minor 1).

### Views against the sheet

- **f34 (hero).** The layout, silhouette and every part match: beam on the tall right pair and past the front-right post, banner on the front-left post, lantern on its bracket under the front-right corner, table with bottles and paper, two benches, crate right, back-right corner high under the beam.
  - The barrel stands directly under the back-left post. The post seems to rise out of the barrel and hides most of its footing. In the sheet, the barrel stands between the back-left and front-left posts, about 2 studs right of the back-left post on screen, with that footing showing.
  - The back-right post and footing are dark in the canopy's shadow; the sheet lights them. This is studio lighting: recorded.
  - Furniture tops are about 15 % darker than the sheet's (Minor 2).
- **r34 (redraw, content).** All content is present. The barrel again sits in front of the back-left post's foot. Same lighting notes.
- **front.** Post and footing proportions, crate X, table, bench and bottles all match.
  - The barrel shows only as a sliver left of the front-left post, under the banner tails. The sheet draws it whole, just inside that post.
  - Banner on the left (hero governs). Canvas shallow (ruled) and its underside grey-taupe (studio shade, recorded).
- **side.** Posts and footings match the cell.
  - The lantern is hidden behind the front-right post (known; not on the fix list).
  - The ridge beam crosses the top (hero governs). The crate stands in front of the table (content differs: ruled).
- **rear.** Content only. Crate, table, bench, bottles and lantern read. The barrel shows beside the back-left post.
- **top.** Content only (ruled square cell). The barrel sits outside the back-left corner, as in the sheet's top cell and floor plan.

### Blockers

None.

### Minors

1. **Barrel placement (introduced by the round-1 fix; cheap, fix before shipping).** At (−8.30, 2.40) the barrel is centred under the back-left post in the hero (camera screen x −8.39 against the post's −8.66) and in r34. It also stays mostly hidden in the front cell.
   - Fix: set `BARREL_C` to about (−5.7, 2.5), just inside the left posts. That puts it about 2.5 studs right of the back-left post in the hero (sheet about 2.1), in front of its footing without hiding it. It shows whole right of the front-left post in the front cell and beside the post in the rear cell, as the sheet's front, rear and three-quarter cells draw it.
   - It stays about 1.1 clear of the back bench end, 0.6 from the back-left footing, and about 1.2 from the proxy on the left lane (y −0.8) and at the turn point.
   - The rod's left end (x −9.5) already sets the hero's width, so `TARGET_SIZE` is unchanged. Re-run kit_verify with the walk, then compare.
2. **Furniture tops darker than the sheet.** In f34: table top `#C96929` against `#EC8B3C`, bench top `#C06323` against `#EE8E40`, crate lid `#C46729` against `#E2883E`. The front edges match (`#AF581D` against `#A3541D`), so most of the gap is the studio's flatter lit-top / side split, which is recorded, not scored. A lift of about 5–8 % on `m066_plank` would close part of it if wanted.
3. **Lashings.** The accepted m048 / m050 twisted-turn language reads crumpled against the sheet's smooth fat coils. The front-right post's two stacked lashings read as a busy cluster in the front and rear cells. Recorded, as ruled.
4. **Left as they were:** the lantern hidden behind the front-right post in the side cell; the exploded view still hides the crate behind the front-right post and the barrel behind the banner.
5. **Tooling.** `shelter_check` skips its canvas headroom test silently when `P.GEO` is empty (any verify-only call on a reopened file). It could fall back to an up-ray grid under the canvas, or report the missing data as a problem.
6. **Recorded, not scored:**
   - the studio shade on the canvas underside and the back-right post;
   - the shallow sag;
   - the kit sizes for the crate and barrel, and the single crate;
   - the ridge beam in the side cell;
   - the top cell's square footprint;
   - f34's W : H, whose box includes text.

## Main session after round 2 (2026-11-04)

Passed 8.5/10. Minor 1 applied: `BARREL_C` (-8.30, 2.40) -> (-5.70, 2.50), just inside the left posts, so the back-left
post no longer rises out of the barrel. The other minors stay recorded.
