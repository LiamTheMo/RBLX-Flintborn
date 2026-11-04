# 069 Palisade Wall — spec

Reference: `art/blender/assets/references/069.png` (1024 × 1536, remade 2026-11-03: "PALISADE WALL / BUILDING MODEL
STUDY", PAGE 069). Builder: `art/blender/kit/mcp/m069.py` on `kit_parts` / `kit_build` → `build()`. Procedure:
`art/blender/kit/mcp/STAGES.md`, `HOUSE_RULES.md`. The study of the earlier sheet is in git history.

## Brief

- **Sheet:** 069 Palisade wall (remake: yes). Family: none. One straight, tileable section of a sharpened-log palisade:
  twelve chamfered octagonal timbers of uneven height with pale pointed tips, two thick posts with two three-turn rope
  bands each, a lashed front rail with a stub past the left post, a short lashed beam at the right post's upper band,
  two lashed rear rails, a red swallowtail banner (cream stripes, cream double diamond) on a knobbed rod, grey chock
  rocks along both feet. No foliage is drawn (the palette's "Foliage (Accent)" swatch is unused), no glow or effect.
- **Class and budget:** asset (tiling wall), ceiling 4000, plan about 3600. Every part under 1000.
- **Size:** the 16-stud pitch sets the scale: the front cell's log row spans 256 px (x 27.5–283.5 of the cell) = 16.00
  studs, 0.0625 stud / px, ground at cell y 199.5. Tallest tip (P2) 199 px → 12.15 (HOUSE_RULES tall posts 12.0). The
  side cell's figure then stands about 5.9 studs (an R6 figure is 5–6). Hero 15.99 × 4.72 × 12.15.
- **Hero view:** f34 cell (12, 146, 512, 512) at camera (−20, 12). Front (12, 585, 312, 800) is a true elevation and
  sets x positions and heights; rear (508, 585, 766, 800) is a true elevation drawn 0.89 × narrower (its W : H 1.17
  against the front's 1.34, judged for content and rail levels); r34 is the f34 redrawn without the banner (content
  only; rendered as the f34 without banner); side (330, 585, 420, 800) and top (770, 585, 1012, 800, drawn as a high
  oblique) content only. Exploded (12, 840, 690, 1285), lashing detail (700, 840, 1014, 1030), tiling (705, 1080,
  1010, 1260); palette swatches y 1355–1400 at x 38–78 / 113–154 / 188–228 / 262–301 / 336–374 / 408–447 / 481–522.
- **Parts:**
  | Part | What | Tris target |
  | --- | --- | --- |
  | `Stockade` | hero: wall + banner + 7 rocks | ≤ 3600 (3594) |
  | `StockadeStraight` | tiling module: the wall without banner and rocks (variant) | ≤ 3100 (3036) |
  | `StockadeLog` | "Palisade Log": Ø 1.40, tip 9.0, one three-turn band | 334 |
  | `StockadePost` | P2 (Ø 1.80, tip 12.15) with both bands closed | 622 |
  | `StockadeRail` | "Horizontal Beam": 8.0 rail with a three-turn lashing near each end | 604 |
  | `StockadeBanner` | rod, knobs, hem sleeve, cloth, stripes, emblem | 268 |
  | `StockadeRock` | "Stone": one chock rock (F4) | 38 |
- **Palette** (rendered sheet medians, front / f34 cells; swatch in brackets): timber `#985517` (`#B06621`, matte 0.85);
  timber_end tips, rail ends, rod, knobs `#F2A241` (`#EC9C40`); rope `#FDD47C` (`#F5CD86`, 0.95); banner `#FB2120`
  (`#E81C1B`); cream `#FEF4D4` (`#F6E6BD`); rock `#908891` (`#8A8592`). All matte, no metal, no emission.
- **Lights / VFX:** none (the sheet shows no glow, light or effect).
- **Collision:** hero `precise`; `StockadeStraight` `box` (tiling module); Log, Post, Rail `box`; Banner `none`; Rock
  `hull`.
- **Checks to switch on in kit_verify:** `seams={"pitch": (16, 0, 0), "obj": "StockadeStraight", "with": "Stockade"}`
  (all four pairings). No foliage sweep (no foliage), no escape or walk (nothing to enter or walk on).
- **Departures from HOUSE_RULES and the sheet (each recorded as a miss, not a blocker):**
  - Flat-cut feet on z 0 (the exploded view draws pointed stakes): house rule.
  - The front cell's two slivers beside the posts (a 0.375 sliver between L1 and P1, 0.5 between P2 and L12) are not
    separate logs: L1 / L12 are the same Ø 1.55 (the seam needs identical end sections) and N4 is Ø 0.68; the middle
    timbers sit 0.1–0.4 left of their measured centres.
  - The front rail ends 0.36 inside P1's silhouette (its inner face lies on the 1.40 logs, so its end seats in P1's
    chamfer, not on P1's side face).
  - The rear lower rail enters the lower bands (rear cell) and is seated against them; the rear rails are at 2.75 /
    6.00 (rear cell 2.75 / 6.0); bands at 1.45–2.55 and 6.20 (P1) / 6.45 (P2) from the front cell.
  - The short front beam sits at P2's upper band as in the f34 and front cells; the tiling cell draws it at the main
    rail's level.
  - The banner is front only (the side cell draws cloth on both faces; f34 and r34 do not).
  - The lashing detail draws the coil round the log as well; the lashings are C-runs over the rail with both ends
    turned into the log behind (a closed loop would pass through the log).
- **Questions for the main session:** none.

## Stage 1 — Modelling

Every piece is its own closed shell from its own function, assembled from the parts' functions; no booleans.
- **Timbers** (`timber`, `P.post`): regular chamfered octagons (chamfer leg 0.586 × the flat radius), broad faces on
  the axes, rings at z 0, 0.6 (foot band) and the shoulder, an 8-facet pyramid tip 0.72 × Ø (± 5 % seeded; apex ± 0.04;
  the end logs exact). 46 tris each. Edge to edge 0.01 apart from −7.995 to +7.995:

  | Timber | x | Ø | tip | Timber | x | Ø | tip |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | L1 | −7.995 … −6.445 | 1.55 | 8.65 | L7 | 0.115 … 1.365 | 1.25 | 9.65 |
  | P1 | −6.435 … −4.635 | 1.80 | 10.60 | L8 | 1.375 … 2.775 | 1.40 | 11.65 |
  | N1 | −4.625 … −3.525 | 1.10 | 8.00 | N3 | 2.785 … 3.935 | 1.15 | 9.95 |
  | L4 | −3.515 … −2.115 | 1.40 | 8.90 | P2 | 3.945 … 5.745 | 1.80 | 12.15 |
  | L5 | −2.105 … −0.705 | 1.40 | 9.00 | N4 | 5.755 … 6.435 | 0.68 | 9.30 |
  | N2 | −0.695 … 0.105 | 0.80 | 7.65 | L12 | 6.445 … 7.995 | 1.55 | 10.30 |

  Tip heights are the front cell's skyline (± 0.05).
- **Bands** (`band_paths`, ported from the old builder): three turns, rope r 0.19, 0.36 apart, centreline 0.17 off the
  faces; each turn the mitred offset loop round the post, cut where it would pass within 0.17 of a neighbour (front and
  rear runs), both run ends carried square into the neighbour's surface and 0.04 into it. 24 runs. The Post part keeps
  closed turns.
- **Members** (`P.plank`, 0.90 × 0.75, chamfer 0.06, pale end faces): spans have their inner face 0.003 off the 1.40
  logs (|y| 0.703), stubs and the short beam 0.003 off the end logs (|y| 0.778). An end at a post is seated 0.02 into
  its chamfer, or, where a band is in the way, stepped in from 0.8 out until the next 0.004 would sink it more than
  0.015 into the rope (`member_x`). Result: RF z 5.30, −4.993 … 1.85 (behind the banner's left edge); RF_w −6.602 …
  −6.002; RS z 7.05, 5.78 … 7.05 (on P2's upper band); RR1 z 2.75, −4.529 … 3.839 (on both lower bands); RR2 z 6.00,
  −4.529 … 4.303 (on P1's upper band; P2's chamfer); RR2_w −7.066 … −6.466; RR2_e 5.312 … 5.912.
- **Lashings** (`lashing`): open C-runs (rope r 0.15, 0.28 apart) over the rail top, round the cut outer top corner,
  down the front and under; both ends turned square into the nearest timber's surface, 0.04 deep. RF at −4.10 and
  −1.24 (three turns), RS at 6.44 (two), RR1 and RR2 at −3.00 and 2.55 (two each): 16 turns.
- **Banner** (`banner`): rod Ø 0.42 (8-sided) at z 8.50, y −1.62, x 1.25 … 4.85, knob balls r 0.30; pegs 0.24 square
  from L8's chamfer and P2's broad face (0.04 in) to the rod (0.02 into its flat underside); an 8-sided hem sleeve
  (0.006 clear of the rod, 0.07 thick) over x 1.71 … 4.09; the cloth slab 0.08 thick, x 1.75 … 4.05, its top 0.015 into
  the sleeve wall, side tips z 1.70, notch 2.70; on the front face two cream stripes (0.09 wide, 0.12 in) and two
  cream diamond rings (1.40 × 3.00 line 0.15; 0.72 × 1.56 line 0.12) at z 5.40, each 0.005 into the cloth.
- **Rocks** (`rock_points`, `rock_place`): squat faceted boulders (6-point foot ring on z 0, 6-point waist at 0.45 h,
  5-point shoulder, 4-point flat-ish top), each slid toward the wall from 3.5 out by bisection until it meets it
  (0.002 off). Front F1 (−6.76, 2.11 × 1.67 × 1.55), F2 (−3.76, 1.67 × 1.35 × 1.00), F3 (−0.10, 1.67 × 1.40 × 1.34),
  F4 (6.53, 2.32 × 1.78 × 1.67); rear B1 (6.44), B2 (−2.05), B3 (−6.71); from the front and rear cells.
- **Rope language:** the first build used five-sided twisted rope (the old build's look) and read as flat twisted
  slats again in the close-ups; the rope is now six-sided, untwisted, with one spiral strand in rope_deep, and the
  lashings' outer top corner is cut: round coils (`band_cu`, `lash_cu`).
- **Rocks:** the old build's minor (upright, mauve) is answered: wider than tall, a broad top facet, base colour R ≈ B.

## Stage 2 — Optimisation and cleanup

kit_verify (`m069.build()`; 0 problems):

| Object | Tris / budget | Size (studs) | Shells | Floating / unchained | Buried | Min corner |
| --- | --- | --- | --- | --- | --- | --- |
| Stockade | 3594 / 4000 | 15.99 × 4.72 × 12.15 | 77 | 0 / 0 | 0 (deepest 0.062, rope in rope) | 1.06° |
| StockadeStraight | 3036 / 4000 | 15.99 × 3.54 × 12.15 | 59 | 0 / 0 | 0 | 1.06° |
| StockadeLog | 334 / 1000 | 2.12 × 2.12 × 9.00 | 4 | 0 / 0 | 0 | 12.8° |
| StockadePost | 622 / 1000 | 2.52 × 2.52 × 12.15 | 7 | 0 / 0 | 0 | 10.7° |
| StockadeRail | 604 / 1000 | 8.00 × 1.31 × 1.46 | 7 | 0 / 0 | 0 | 6.1° |
| StockadeBanner | 268 / 1000 | 4.73 × 0.57 × 7.10 | 9 | 0 / 0 | 0 | 7.6° |
| StockadeRock | 38 / 1000 | 2.11 × 1.73 × 1.67 | 1 | 0 / 0 | 0 | 25.1° |

- Every object: 0 non-manifold edges, bowties, boundary, wire, loose, zero-area faces, n-gons and duplicate verts; 0
  winding errors, 0 inward faces, 0 self-intersections; transforms applied, no modifiers or custom normals; origin at
  the bbox bottom centre (`m069_offset`: hero (0, −0.026, 0), module (0, −0.038, 0); x 0 on both, so the modules tile
  without a pivot offset).
- Hero tris by kind: logs 460, posts 92, bands 1200 (24 runs), rails 196 (7), lashings 1088 (16 turns), pegs 24, rod
  28, knobs 72, hem 64, cloth 16, stripes and emblem 88, rocks 266.
- The 32 corners under 3° (smallest 1.06°, floor 0.3°) are the short end segments of lashing runs where the run turns
  into the log; recorded.
- **Seams** (16-stud pitch, all four pairings of Stockade and StockadeStraight): 0 crossing triangle pairs, closest
  0.010, gap at the seam 0.010, end sections identical over z 0 … 7.534 (mismatch 0.000), extents exactly ±7.995, 0
  vertices past the seam planes. The tiling compare (hero + hero at +16) matches the sheet's tiling cell (W : H 2.62
  against 2.50).

## Stage 3 — UV

`kit_build` cleanup (Smart UV 45°, ANGLE_BASED, margin 0.008, overlaps cut free). Every object: 0 overlapping pairs,
0 flipped, min island gap 0.016, border 0.008, texel density 1.0, conformal stretch p95 1.00 (Banner 1.16). The
exporter writes its own palette UVs; this layer is clean.

## Stage 4 — Materials, colour and texture

`MODEL.calibrate` on the studio dome toward the sheet's rendered medians, then the keys scaled in linear light so the
compare renders of the front and f34 cells (same masks as the sheet) match the sheet's medians (the wall's vertical
faces take less light than the dome).

| Key | Hex | Sheet (front / f34) | Ours (front / f34) |
| --- | --- | --- | --- |
| m069_timber | `#8B551B` | `#985517` / `#8F4F17` | `#955316` / `#985516` |
| m069_timber_end | `#BF883E` | `#F2A241` / `#F6A23C` | `#F6AA49` / `#F6AA48` |
| m069_timber_deep | `#613810` | foot band only (30 %) | — |
| m069_rope | `#E8B470` | `#FDD47C` / `#FDD37B` | `#FFD276` / `#FFCC72` |
| m069_rope_deep | `#AB874D` | one strand in six | — |
| m069_banner | `#F01E1C` | `#FB201D` / `#FB2120` | `#FF1A17` / `#FF1A17` |
| m069_banner_deep | `#86100F` | the hem round the rod | — |
| m069_cream | `#E6DCBC` | emblem `#FEF4D4` | `#FFF1C2` |
| m069_rock | `#817E8C` | `#908891` / `#958C94` | `#7F7881` / `#9A919B` |

- By role and position, never by facing: tip facets, member end faces, rod and knobs timber_end; timber foot band to
  0.6 at 30 % toward timber_deep; rope one strand in six rope_deep (by place round the spiral); the hem banner_deep;
  stripes and emblem cream. Rocks one key with Tint mottling (a soil band read as painted light on the lone Rock part:
  kit check 0.80, now 0.00). Tint ± 0.05 per timber and member, 0.04 rock, 0.03 rope, 0.02 cloth; broad mottling on the
  cloth and rocks. Kit baked shading: hero 0.12, module 0.12, Log 0.08, Post 0.06, Rail 0.07, Banner 0.00, Rock 0.00.
- Recorded (studio lighting, not scored): the rear cell's timber renders `#8A4F16` against `#A75C19` and its rope
  `#D8A25C` against `#FDD47C` (the studio lights the front); the wood's lit quartile `#A95F1B` against `#C9711F`.

## Stage 5 — Lighting

Nothing: the sheet shows no emissive part and no light. No emission, no Neon. Studio check (Requires Manual
Validation): orange timber with pale tips in daylight, the rope reading pale yellow.

## Stage 6 — VFX

Nothing: no glow, smoke, dust or sparkle on the sheet; the banner hangs still. 0 sockets on every object (export
stats: 0 sockets, no glow keys).

## Views against the sheet (compare.py, `m069.compare()` / `m069.tile_compare()`)

| Cell | Camera | W : H sheet / ours | Notes |
| --- | --- | --- | --- |
| f34 | (−20, 12) | 1.31 / 1.16 | the sheet's perspective widens the near end and its cast shadow adds to the box; content and layout match |
| front | (0, 0) | 1.34 / 1.32 | skyline, bands, rail with stub, short beam, banner, four rocks |
| rear | (180, 0) | 1.17 / 1.31 | the rear cell is drawn narrower; rails, lashings, bands and three rocks match |
| side | (90, 0) | 0.43 / 0.39 | content: the end log with the post behind, rail stubs both faces, rocks; no rear banner (see Brief) |
| top | (0, 89.9) | 1.42 / 3.72 | the sheet's top cell is a high oblique; content: tops in a row, front rail with lashings, rod, corner rocks |
| tile | (0, 0) | 2.50 / 2.62 | two heroes at 16 studs: continuous wall, rocks meeting at the seam as drawn |

Renders in this folder: `M069_views.png` (f34, r34, front, side, rear, top sheet views, exploded, scale with a 5.5
marker), `lash_cu.png`, `band_cu.png`, `banner_cu.png`.

## Stages 1–6: open items

- Dropped part: `StockadeRosette` (the remade sheet has no foliage). The old kit-file object and its exported mesh
  should be removed before shipping. The old m069 material keys `m069_cloth_white`, `m069_leaf*`, `m069_rock_light`,
  `m069_rock_dark` and their mixes are no longer used.
- Recorded misses: see "Departures" in the Brief; the f34 and rear W : H differences; studio lighting on the rear.
- Candidate for `kit_parts` (main session): `member_x` / `_overlap` (seat a member end against rope bands by stepping
  in until a sampled sink limit) and `band_paths` (a band round a post between close neighbours as cut runs with ends
  turned into the neighbours).

## Main session rulings (2026-11-04)

The recorded departures stand and are not to be scored:
- flat feet;
- the end logs sharing a section for the seam;
- the rail seats;
- the front beam at P2's upper band;
- the banner on the front only;
- C-run lashings.

`StockadeRosette` is retired, because the remade sheet has no foliage. Asset class, so one verification round.

## Stage 7 verification (round 1)

**Result: PASS, 8.0 / 10.** No blockers. Asset class, so this is the only round. Re-measured in a separate background
session on a copy of the work file (`wip/M069v.blend`; nothing built into it, nothing saved). The saved hero is the
current builder's output: a temporary rebuild from `m069.hero_all` gave the same 1945 vertices, max difference 0.000.
Renders are in `<temp>/...`.

### Technical (kit_verify, re-run: 0 problems, 13.9 s)

| Object | Tris / ceiling | Size | Shells | Floating / unchained | Buried (deepest) | Min corner |
| --- | --- | --- | --- | --- | --- | --- |
| Stockade (asset) | 3594 / 3999 | 15.99 × 4.717 × 12.15 | 77 | 0 / 0 | 0 (0.062 rope in rope) | 1.057° |
| StockadeStraight (asset) | 3036 / 3999 | 15.99 × 3.541 × 12.15 | 59 | 0 / 0 | 0 (0.062) | 1.057° |
| StockadeLog | 334 / 999 | 2.12 × 2.12 × 9.00 | 4 | 0 / 0 | 0 (0.02) | 12.8° |
| StockadePost | 622 / 999 | 2.52 × 2.52 × 12.15 | 7 | 0 / 0 | 0 (0.02) | 10.7° |
| StockadeRail | 604 / 999 | 8.00 × 1.31 × 1.46 | 7 | 0 / 0 | 0 (0.02) | 6.1° |
| StockadeBanner | 268 / 999 | 4.73 × 0.572 × 7.10 | 9 | 0 / 0 | 0 (0.04) | 7.6° |
| StockadeRock | 38 / 999 | 2.105 × 1.727 × 1.665 | 1 | 0 / 0 | 0 | 25.1° |

- Every object: 0 non-manifold edges, bowties, boundary, wire, loose, zero-area faces, n-gons and duplicate verts; 0
  winding errors, parity-inward faces, self-intersections or negative volumes; transforms applied, no modifiers or custom
  normals, origin offset 0; UV 0 overlaps / 0 flipped, gap 0.016, border 0.008, density 1.0; 0 pierces of the cloth;
  K.check clean; 0 sockets, no glow keys. Tint against normal: rock −0.28 / −0.31 with a within-shell spread of 0.02
  (not flagged). Collision: hero precise, module, Log, Post and Rail box, Banner none, Rock hull.
- Seams at the 16-stud pitch, all four pairings (Straight|Straight, Straight|Stockade, Stockade|Straight,
  Stockade|Stockade): 0 crossing triangle pairs, closest 0.010, gap 0.010, extents exactly ±7.995, 0 vertices past
  ±8, end sections identical over z 0 … 7.534 (mismatch 0.000; L12's flat face runs on to 9.184, above L1's shoulder).
- 32 corners under 3° (lashing run ends): recorded, above the 0.3° floor.

### Views against the sheet (compare.py, re-run)

| Cell | Camera | W : H sheet / ours | Judgement |
| --- | --- | --- | --- |
| f34 | (−20, 12) | 1.317 / 1.169 | layout, skyline, rail with stub, short beam, banner, four front rocks all match; the gap is the sheet's perspective (az −35 gives 1.03, worse) |
| front | (0, 0) | 1.344 / 1.313 | skyline and every element in place (below) |
| rear | (180, 0) | 1.164 / 1.313 | content matches: two rails between the posts, upper stubs, bands, three rocks; the sheet's rear is drawn narrower and leaves out L8's height |
| side | (90, 0) | 0.432 / 0.392 | content: end log, P2 behind, bands, stubs, rocks both feet; banner front only (ruled) |
| top | (0, 89.9) | 1.419 / 3.719 | content: tip row with the two larger posts, front rail and lashings, rod with red hem, corner rocks; the sheet's cell is a high oblique |
| tile | (0, 0) | 2.498 / 2.624 | continuous wall, matching skyline repeat, rocks meeting at the seam as drawn |

- **Skyline** (front cell, scaled by content width; sheet / ours, studs): L1 8.54 / 8.72, P1 10.41 / 10.66, N1 8.05 /
  8.06, L4 8.80 / 8.95, L5 8.88 / 9.07, N2 7.65 / 7.71, L7 9.55 / 9.70, L8 11.42 / 11.70, N3 9.79 / 10.02, P2 11.91 /
  12.19, N4 9.18 / 9.36, L12 10.11 / 10.37. Every tip within 0.3 (ours runs about 2 % taller overall because the
  sheet's content box includes its ground shadow). Order, uneven heights and the two tall posts read as drawn.
- **Timbers:** twelve, widths as in the Brief (posts 1.80 against the sheet's ~1.68, logs ~1.26–1.40). The posts stand
  in the log line as in the sheet's top cell.
- **Bands, rails, lashings, banner, rocks:** two three-turn bands per post at the drawn heights; front rail at the
  drawn level with the stub past P1, short beam at P2's upper band (ruled), two rear rails with lashings; banner rod,
  knobs, swallowtail, stripes and double diamond at the drawn size and height (ours about 0.5 left of the sheet's in
  the front cell); front rocks F1–F4 at the drawn places and sizes, rear rocks under the posts and mid-wall.
- **Colours** (medians of matching pixel classes, sheet / ours): timber front `#A55C19` / `#9A5617`, f34 `#A25A18` /
  `#9A5617`, tile `#A35B18` / `#995517`; tips `#F1A140` / `#FBA944`; lit rope `#FDD179` / `#FFC06B` (front),
  `#FDD178` / `#FFC26C` (f34); banner `#FB211E` / `#FF1A17`; cream `#F4E5CB` / `#FFF1C3`; rock front `#928A92` /
  `#827A82`, f34 `#9A9198` / `#9A929C`. Rear and side differences are studio lighting (recorded, not scored).

### Blockers

None. Nothing is broken, and every cell reads as the sheet's wall.

### Minors (recorded; the first two are cheap and worth doing when the model is next touched)

1. **The pointed tips are about 20 % short.** The sheet's pale tips measure 0.85–0.93 × the diameter (front cell:
   L1 1.44, P1 1.47, L4 1.23, L8 1.36, P2 1.53, L12 1.34); ours are 0.72 × (1.10, 1.18, 0.92, 0.92, 1.16, 1.07). The
   tip share of the front cell is 3.6 % against the sheet's 6.6 %, and the sheet's points read longer and sharper.
   Fix: `TIP_K` 0.72 → 0.90 (apex heights unchanged, no tri cost; the seams' common range drops to about z 7.26 and
   stays identical, since the end logs share Ø 1.55).
2. **The post bands read as striped slats, not plump coils.** Each six-sided turn shows a broad flat lit top, a shaded
   underside and a dark gap, so the bands read as stacked chamfered slats with brown stripes. Rope covers 4.1 % of the
   front cell against the sheet's 6.4 %; the sheet's coils are packed and pale with thin grooves. Turning the section
   (phase 0, a flat facing out) was tried on a temporary copy and changed almost nothing. Suggested fix: pack the turns
   (`BAND_STEP` 0.36 → about 0.32, inside the 0.08 rope-in-rope limit) so each turn hides the underside of the one
   above, and keep `rope_deep` off the bands' outward faces. Check the rope share of the front cell again afterwards.
3. Rear lashings are two thin turns (about 0.58 wide); the sheet's rear cell draws three to four fat turns (about 1.0).
4. The banner hem reads as a dark maroon block (`#86100F`). The sheet draws a bright red loop over the rod, with a darker
   inside only.
5. Colours: the timber renders about 6 % darker than the sheet's medians, the lit rope is more amber (hue 34° against
   41°, saturation 0.58 against 0.52), and the front rocks are about 10 % darker. Each is within the calibration's
   spread, but all three lean darker or warmer.
6. Side cell: P2's band runs and the rail stubs show as comb-like blocks past the end log. This is content only and
   follows from the ruled cut runs and stubs.
7. Recorded, not scored (rulings, HOUSE_RULES): flat feet, the end logs' shared section, rail seats, the beam at P2's
   upper band, the banner on the front only, C-run lashings, the f34 and rear W : H, and the rear and side studio
   lighting.

## Main session after round 1 (2026-11-04)

Passed 8/10. Minor 1 applied: `TIP_K` 0.72 -> 0.90, so the pale tips are the sheet's length (apex heights, tris and seam sections
unchanged). The other minors stay recorded.
