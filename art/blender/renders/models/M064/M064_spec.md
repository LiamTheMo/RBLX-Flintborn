# 064 A-Frame Tent — spec

Reference: `art/blender/assets/references/064.png` (remade 2026-11-03; it replaces the sheet the earlier build
followed; git history keeps the old spec). Builder: `art/blender/kit/mcp/m064.py` on the shared library
(`kit_parts` / `kit_build`), `m064.build()`. Procedure: `art/blender/kit/mcp/STAGES.md`; defaults:
`art/blender/kit/mcp/HOUSE_RULES.md`.

## Brief

- **Sheet:** 064 A-Frame Tent (remake: yes). Family: none.
- **Class and budget:** structure (an enterable open-fronted shelter), ceiling 6000, plan ≤ 5400. Built 4068.
- **Size:** set by the house headroom, not by the sheet's scale figure. The sheet's side cell puts the tent at about
  1.9 × its R6 figure (≈ 9.7 studs), but its door stack (lantern at 0.46 H, roll at about 0.55 H) would then hang at
  head height. At tips **12.0** the roll underside is 7.02 and the lantern bottom 7.66 (headroom 6.9), with the front
  cell's proportions kept: crossing 0.855 H = 10.26, pole feet ±6.66 (33° half angle, frame W : H 1.20 against 1.19).
  Hero about **20.5 × 15.0 × 12.0** with the dressing; the tent alone 14.4 wide, feet 13.3 long.
- **Hero view:** front three-quarter (f34) at camera (−42, 25). Other cells:
  - "Side view (right)" is a front-left three-quarter (−22, 6) with the scale figure: content only.
  - "Rear view" is the true side elevation from +X (90, 0).
  - The top cell is a stylised square: content only.
  - The r34 (−138, 25) puts the crate at the back +X foot, against the f34's −X side: f34 governs.
  - The front cell draws the bedroll across X; the f34 and floor plan lay it along Y: f34 governs.
- **Parts:**
  | Part | What | Tris |
  | --- | --- | --- |
  | CanvasTentFrame | "A-Frame Pole": one X of two 0.9 poles, ridge lashing, foot bands | 782 |
  | CanvasTentPanel | "Canvas Panel": one sagging side panel slab, ridge cut square | 116 |
  | CanvasTentMat | "Tent Mat (Rolled + Flat)": the floor mat and the bedroll | 116 |
  | CanvasTentCrate | "Storage Crate": braced, lidded, iron bolts | 444 |
  | CanvasTentBarrel | "Barrel": ten staves, two hoops, lidded | 256 |
  | CanvasTentStone | "Stone (x2)": pale faceted block | 20 |
  | CanvasTentPeg | "Peg (x4)": square stake with a rope collar | 92 |
  | CanvasTentLantern | the hanging lantern with its ring | 144 |
- **Palette** (swatch medians; rendered targets in Stage 4): timber `#B85303`, canvas `#FADAAF`, stone `#A9978C`,
  rope `#CB975A`, tent mat `#5E8C80`, metal `#50504F`, lantern light `#FDC005`. Finishes: wood 0.85–0.9 rough, canvas and
  rope 0.95, metal 0.55 / 0.4 metal, glass Neon.
- **Lights / VFX:** two lanterns (the hanging one and the ground one on a stake): glass `m064_glow` at emission 1.0
  (Neon) and one `heat_glow` socket each, overridden to a steady warm halo (as M064 decision 13 / M068).
- **Collision:** hero `precise` (walk-in, Requires Manual Validation in Studio); Frame, Panel, Barrel, Stone `hull`;
  Crate `box`; Mat, Peg, Lantern `none`.
- **Checks to switch on in kit_verify:** `cls="structure"`; `walk` (two paths from y −9.5 through the doorway onto the
  mat, a turn point inside, the mat skipped as floor); `escape` (the inside over the mat, the front face allowed for
  the doorway and gable); `stored` (`m064_door`, `m064_inside`); `sockets` (2 heat_glow on the hero, 1 on the lantern).
  Model check `door_check`: headroom ≥ 6.9 over the walk lane and the doorway rays.
- **Departures from HOUSE_RULES:**
  1. Doorway: the A-frame's poles converge above the door, so the clear opening is **3.6 wide to z 6.5** and 2.0 wide
     (x ±1.0) to 7.0, not a full 3.6 × 7.0 rectangle. The roll underside (7.02) and the lantern (7.66) clear 7.0.
  2. Size against the sheet's scale figure (12.0 tall, the sheet's figure suggests about 9.7): the headroom rule.
  3. Frames lean 4°, not the side cell's ≈ 10–13°: the hero view draws the tent as a near prism (ridge about as long as
     the hem); 4° keeps a visible lean in the side view.
  4. The floor mat covers the whole floor under the hems (the sheet's floor plan, "Walkable Floor (Tent Mat)"), so the
     canvas is closed at the bottom; the front cell's narrower mat is a recorded miss.
- **Questions for the main session:** none.

## Stage 1 — Modelling

Build frame: front −Y (doorway), +X right, ground z 0, ridge along Y on x 0. Each end frame is a plane leaning out
4° (top inward); `fp(end, x, h, w)` places points by in-plane (x, h) and normal offset w, `y_at(end, z, w)` gives a
parallel plane's y at height z.

- **Frames (2):** two 0.9 square poles (chamfer 0.06) per end, side by side at w ±0.455 (0.01 apart, touching at the
  crossing), each from a flat foot on z 0 (axis x ±6.66) through the in-plane crossing at z 10.26 to a square-cut tip
  whose highest corner is z 12.0; the tip caps in `end_grain`. Frame plane |y| 5.64 at z 0 (crossings at |y| 4.92).
- **Ridge lashing (joint detail):** three twisted wraps round both poles (one above the crossing, two below) and a
  turn square round each pole below them (the figure-eight's lobes), r 0.14. The canvas end sits right behind the inner
  pole, so each wrap is cut open where it would pass behind it (`wrap()`): the ends sit beside the inner pole's side
  face, flush with its back face. Foot bands: two touching turns square round each pole at z ≈ 1.7, r 0.13 (open the
  same way on the inner pole).
- **Canvas (closed 0.10 slabs):**
  - Roof: both side panels and the ridge fold as one chevron slab, outer ridge z 10.50, inner 10.32, hem z 0.205
    (0.005 over the mat), slope 0.649 (on the poles' line), 4 rows × 5 columns per panel, the columns spread between
    the leaning end caps, sagging 0.30 inward toward each panel's middle, quads split toward the panel centre (the X of
    creases). Ridge 7.97 long, hem 9.41, hem half-width 6.68.
  - Back: a closed triangle 0.02 behind the inner poles, its sloped edges tucked 0.02 into the roof, the centre sunk
    0.12.
  - Front: two door flaps from the hem corners up the roof line to z 6.95, the door edge from x ±3.30 at the hem to
    ±2.21 at 6.95, a turned-back strip along each door edge; the gable above is open.
  - Rolled door flap: a 10-sided roll Ø 0.76 × 3.13 across the doorway top (underside 7.02), its upper end corners
    stopped 0.008 short of the sagging roof (measured by rays), a darker core proud of each end, two rope bands.
- **Ties:** two hem-tie loops standing out of each side panel's hem (ends on the canvas, found by rays), a tie from
  each flap's door corner to the ground.
- **Lantern (hanging):** dark-metal lantern 1.05 wide, glass 0.78 × 0.95, ring top 9.78, bottom 7.66, hanging inside
  the gable at y −1.95 (just behind the roll) on a short rope from the ridge. In the front view it hangs below the
  crossing as the sheet draws it; it no longer shows past the frame in the side view (the earlier build's miss).
- **Interior:** the teal floor mat 13.5 × 9.4 × 0.20 under the hems and end pieces; the bedroll (Ø 1.1 × 3.5, tan with
  a teal band, a darker core at its front end) along Y at x −0.9, front end y −2.6; a plank chest 4.0 × 1.15 × 1.5 with
  a lid and two battens at the back (front cell, exploded).
- **Dressing (f34 layout):** crate (−9.6, 3.6) rot 12°; barrel A (−8.4, −1.6); barrel B (8.4, −4.4) rot 15°; stones
  S1 (−8.3, 1.2), S2 (−8.3, −6.0); ground lantern on a 1.0 stake (−7.3, −4.4); pegs (±5.0, ±7.1), 0.6 × 1.3 with a
  rope collar. House sizes: crate 2.30 × 2.20, barrel 2.72.
- **Stored points:** `m064_offset` (the origin in the build frame, (−0.746, 0.004, 0)), `m064_door` (the doorway on
  the ground), `m064_inside` (the mat centre).

## Stage 2 — Optimisation and cleanup

`kit_verify` (structure): **0 problems.** Every object: 0 non-manifold, bowtie, boundary, wire or loose elements, 0
zero-area faces, 0 n-gons, 0 duplicate verts, 0 winding errors or inward shells, origin at the bottom centre,
transforms applied, no modifiers or custom normals. Hero 107 shells: floating 0, unchained 0; deepest seat 0.048 (roll
band in the roll); nothing pierces a canvas sheet; smallest face corner 3.27° (none under 3°).

| Object | Tris | Size (W × D × H) |
| --- | --- | --- |
| CanvasTent | 4068 / 6000 | 20.50 × 15.03 × 12.00 |
| CanvasTentFrame | 782 | 14.43 × 2.78 × 12.00 |
| CanvasTentPanel | 116 | 6.68 × 9.41 × 10.30 |
| CanvasTentMat | 116 | 13.53 × 9.42 × 1.29 |
| CanvasTentCrate | 444 | 2.42 × 2.42 × 2.20 |
| CanvasTentBarrel | 256 | 2.10 × 2.21 × 2.72 |
| CanvasTentStone | 20 | 1.13 × 1.03 × 0.92 |
| CanvasTentPeg | 92 | 0.75 × 0.75 × 1.30 |
| CanvasTentLantern | 144 | 1.12 × 1.12 × 2.09 |

**Walk-in:** the 5.5-stud proxy walks both paths from y −9.5 through the doorway onto the mat (one rise of 0.20):
clearance 0.34 (to the bedroll), 0 intersecting steps, headroom 6.11 over the proxy's full width; turn point (1.4,
−0.2) clear 0.41 at every yaw. `door_check`: headroom over the lane (x 0.45–1.55) **7.01**; doorway rays clear 3.6
wide to 6.5 and ±1.0 to 7.0. The Studio walk-in with `precise` collision stays **Requires Manual Validation**.

**Light escape:** 148 interior points, 93,668 rays plus 15,436 seam points: **0 leaks**; every escaping ray leaves by
the front face (doorway and gable).

## Stage 3 — UV

Smart UV (angle 45, margin 0.008) with overlaps cut free: every object 0 overlaps, 0 flipped, island gap 0.016, border
0.008, conformal stretch p95 ≤ 1.04.

## Stage 4 — Materials, colour and texture

Calibrated with `K.calibrate` on the studio dome, then tuned on the f34 render against the same regions of the
sheet's f34 (`compare.py` cells, medians, paper dropped). Sheet / ours:

| Region | Sheet | Ours |
| --- | --- | --- |
| Pole lit face | `#DA6A0E` | `#DB6921` |
| Lashing rope | `#E49026` | `#DA842C` |
| Crate | `#8C4A1E` | `#80441A` |
| Barrel | `#914E1E` | `#934F1D` |
| Mat | `#4E7F6F` | `#518475` |
| Stone | `#ABA5A7` | `#AFA29D` |
| Lantern glass | `#F0A210` | `#EAAA1F` |
| Peg | `#CA620A` | `#CF5F0C` |
| Canvas, side view (az 90) | `#FDE3BB` | `#F2D7AB` |
| Canvas, f34 key-lit panel | `#FDDFB7` | `#FFFFDB` (clipped) |

Keys: timber `#B1580A`, end grain `#C47A35`, wood_dark `#7B481E`, wood_deep `#55301A`, canvas `#FDE4BC`, canvas_deep
`#E6C8A2`, rope `#EBB24A`, rope_deep `#C58A34`, mat `#457068`, bedroll `#9E784A`, metal `#4A4D50`, glow `#F8B80A`
(emission 1.0), stone `#908A8C`.
- The dome asks for a salmon canvas (`#F9B8A2`); the canvas keeps the hue-correct cream of the M064 ruling. The
  key-lit panel clipping toward white is a studio-lighting effect (recorded, not scored, HOUSE_RULES "Colour").
- Colour by role and position only: canvas hem bands and rims toward canvas_deep, the turned-back flap strips, the
  bedroll's teal band, the crate frame and panels, cut end grain. Canvas Tint mottling 0.03 (scale 0.18), per-piece
  Tint ±0.02–0.05 elsewhere. The crate body carries one Tint (per-face random tints read as facing on a box); the barrel
  is one wood key (a darker base read as painted shade).

## Stage 5 — Lighting

The sheet's lantern light is a separate effect: both lantern glasses are Neon (emission 1.0), previewed unshaded. The
dark interior of the sheet is lighting, not paint; the studio lights it. In Studio the tent needs nothing else; check
the canvas tone and the dark interior under game daylight (manual).

## Stage 6 — VFX

Two `heat_glow` sockets on the hero at the glass centres (hanging lantern (0.746, −1.954, 8.255) and ground lantern
(−6.554, −4.404, 1.598) in the object's frame), one on CanvasTentLantern; each overridden to a steady warm halo
(PointLight `#FFB347`, range 12 / 8). Export STATS: hero 2 sockets, lantern part 1, glow key `m064_glow`.

## Renders and comparison

`art/blender/renders/models/M064/`: `M064_views.png` (f34, r34, front, side (−22), rear (true side), top, exploded,
scale), close-ups `lash_cu.png`, `door_cu.png`, `inside_cu.png`. Side-by-side with the sheet: `m064.compare()`
(written to `<temp>/RBLX-Flintborn/compare/M064/` by default).

Recorded misses (judged against the sheet, view by view):
- f34 W : H 1.21 against 1.42: the sheet's f34 is drawn in strong perspective (its ridge as long as the near hem).
- The key-lit canvas clips pale in the studio (f34, r34); the side view is about 10 darker than the sheet.
- Front view W : H 1.62 against 1.28: the f34 layout spreads the dressing (crate, barrels, stones) wider than the front
  cell shows; the front cell's lantern hangs lower and larger (the headroom rule).
- The sheet's interior reads dark brown; the studio lights ours (lighting, not paint).
- Side (true side) view: the frames lean 4° against the cell's ≈ 10–13° (departure 3); the inner and outer poles of a
  frame show side by side.
- The exploded shot shows the panel near edge-on and the small parts small (presentation only).
- No canvas wrap bands round the front poles (exploded detail); the bedroll lies along Y (f34, floor plan) where the
  front cell draws it across.

## Main session rulings (2026-11-04)

The brief's departures stand and are not to be scored:
- the A-frame doorway narrowing above z 6.5, which the converging poles force;
- height 12.0, so the roll and lantern clear the 6.9 headroom;
- the 4° lean that the hero view's near-prism shape gives;
- the floor mat covering the whole floor;
- the f34 governing over the r34's and front cell's dressing positions.

## Stage 7 verification (round 1)

**Result: FAIL, 6/10.** Technically clean: everything re-measured matches the modeller's numbers. The hero view
(f34) and the side cell don't show the doorway's main features: the lantern hanging under the front lashing, the cream
rolled door flap and the bedroll in the opening. The tent body, frames, lashings, canvas, dressing layout and colours
otherwise follow the sheet. Read-only session on `wip/M064v.blend` (no build, no save); renders in `<temp>/...`.

### Technical (re-run)

- `kit_verify.run` (all 9 objects, `m064.VERIFY`, size 20.5 ± 0.3 × 15.0 ± 0.3 × 12.0 ± 0.02): **0 problems** in 3.2 s.
  Hero 4068 / 6000 tris, 20.499 × 15.026 × 12.000, 107 shells, every shell matched to the register. No non-manifold,
  bowtie, boundary, wire, loose, zero-area, n-gon or duplicate elements, and no winding, parity-inward,
  self-intersection or negative-volume shells. Smallest corner 3.27°. Floating 0, unchained 0, deepest seat 0.048
  (roll band in roll), 0 buried, 0 pierces of the 4 canvas shells. UV: 0 overlaps or flips, gap 0.016, border 0.008.
  Origin offset 0, transforms applied, no modifiers or custom normals, `K.check` clean.
- Parts: Frame 782, Panel 116, Mat 116, Crate 444, Barrel 256, Stone 20, Peg 92, Lantern 144 tris. All are clean, and the
  sizes match the spec's table.
- Sockets: hero 2 × `heat_glow` at (0, −1.95, 8.255) and (−7.3, −4.4, 1.598) build frame; Lantern part 1. Glow key
  `m064_glow`. Stored points: `m064_door` (0, −4.72, 0) on the front canvas plane, `m064_inside` (0, 0, 0.20) mat
  centre.
- Walk (proxy, both paths from y −9.5): clearance 0.34 (bedroll), 0 intersecting steps, one rise of 0.20, proxy-wide
  headroom 6.11 at (2.0, −4.4), which is the ruled A-frame narrowing. Turn point (1.4, −0.2): 0.41 at every yaw.
  `door_check`: headroom over the lane **7.01**, doorway rays all clear (3.6 to 6.5, ±1.0 to 7.0).
- Light escape (modeller's box): 148 points, 93,668 rays plus 15,436 seam points, **0 leaks**, all escapes through
  the door. Its box covers only y ±2.3, so I also scanned the **whole interior**: 4,756 points inside the canvas
  from z 0.26 to 10.05 and to the end pieces, 2.2 M rays. Escaping rays were allowed only if they cross the front
  plane inside the tent section. Result: 53 leaks, all grazing (≤ 1.2° below horizontal) from points within 0.1 of the
  floor. They slip through the 0.005 slit between the side and back hems (z 0.205) and the mat top (0.200). Invisible
  in practice; recorded as a minor.

### Views against the sheet (`compare.py`, all six cells, plus 1100 × 900 renders of f34, front, side and r34)

- **f34 (hero, −42 / 25).** The silhouette, X frames with crossing and tip overhang, ridge lashings, foot bands, pegs,
  crate, the two barrels, two stones and the ground lantern all read and sit where the sheet puts them. W : H 1.21
  against 1.42 is the recorded perspective miss. **Missing:** the sheet's doorway shows the lantern under the front
  lashing, the cream roll with two rope bands across the door top, and the tan / teal bedroll on the mat. A ray test
  of the shells' camera-facing area visible from this camera gives:
  - hanging lantern glass **0 %**;
  - roll **0 %**;
  - bedroll **2.6 %**;
  - chest 0 %.

  In our render the doorway shows only the mat and the inner canvas.
- **Side cell (−22 / 6).** In the sheet the lantern hangs below the lashing, above a lit cream roll. In ours:
  - lantern glass 0 % visible, with only its ring and hanger showing;
  - roll 93 % geometrically visible, but it sits behind the inner poles under the roof, so it renders a dull `#978465`
    against the sheet's `#FCE5BD`;
  - the roll reads as a grey band, not a roll.

  The bedroll shows (51 %), and its visible end reads dark brown (`#5B3B1B` against the sheet's tan `#A76D33`). The
  chest, mat, flaps and the turned-back flap strips read.
- **Front cell (0 / 0).** Content matches: the X, lashing, lantern under the crossing (small and high: the recorded
  headroom miss), the flaps, the chest at the back, the mat, and dressing on both sides. The roll shows only as a
  shaded beige strip with two hanging bands. W : H 1.62 against 1.28 is the recorded dressing spread.
- **r34 (−138 / 25).** Content matches. The crate on the right is the ruled f34 layout. The two hem ties per side are
  much smaller than the sheet's chunky rope loops.
- **Rear cell (true side, 90 / 0).** Trapezoid canvas, two hem ties, frames and lashings. The 4° lean and
  side-by-side poles are ruled or recorded.
- **Top.** Content only: canvas, both frames with lashings, crate, barrels, stones, pegs, lantern. Passes.
- **Exploded / scale / close-ups.**
  - The parts match the exploded cell's set.
  - The lashing close-up shows three wraps and two diagonal turns. They read as straight, flat-sided bars across the X
    rather than round rope hugging the crossing, as the joint-detail cell draws it (minor).
  - Inside: closed, with sagging facets, the chest, bedroll and mat.
- **Colours** (medians of matching regions, sheet f34 crop against our f34 render, sheet / ours):

  | Region | Sheet | Ours |
  | --- | --- | --- |
  | Front pole | `#DB6C10` | `#DA620D` |
  | Timber overall | `#C05F11` | `#CE5C0C` |
  | Front lashing | `#EC9E38` | `#EEA437` |
  | Back lashing | `#DE9336` | `#F9B240` |
  | Crate | `#8C491D` | `#7B4119` |
  | Barrel | `#964D1D` | `#924E1C` |
  | Mat | `#508272` | `#518576` |
  | Stone | `#989496` | `#A59994` |
  | Ground lantern glass | `#FBC920` | `#FFC306` |
  | Peg | `#C9610B` | `#C9590B` |
  | Bedroll band | `#375A4A` | `#456153` |

  Canvas, key-lit side `#FDE0B8` / `#FFFFDB` and lit right flap `#FDDBB2` / `#FFF8C0`: clipping (recorded, not
  scored). Interior: the sheet's dark brown against the studio-lit beige (recorded).

### Blockers

1. **The lantern and the rolled flap don't show in the hero view or the side cell.** The lantern hangs 3 studs
   inside at y −1.95. The roll sits 0.04 behind the inner pole face, where the roof's front edge hides it from the f34
   and leaves it in shade from the side. Fix:
   - **Roll.** Bring it forward into the doorway plane between the front poles, inside the poles' depth
     (w ≈ −0.45 … −0.1). Shorten it to fit between the pole edges at its height (about 2.3 long × Ø 0.76, underside
     still ≥ 7.02), with its ends seated 0.002–0.05 into the poles or stopped short of them.
   - **Lantern.** Hang it from the front lashing on a short rope or hook, just in front of the frame's outer face
     under the crossing, as the f34, side and front cells draw it. Keep its bottom ≥ 7.0 over the walk lane, and
     re-run `door_check` and the walk.
   - **Targets** (same ray test): lantern glass and roll ≥ 50 % visible at (−42, 25) and (−22, 6); the roll reads
     near the canvas cream (≈ `#FCE5BD`) in the side cell.
   - **Knock-on changes.** Move the hero `heat_glow` socket with the glass. If the lantern then shows past the frame
     in the true-side cell, record it as a miss (the hero view governs).
2. **The bedroll is hidden in the hero view** (2.6 % visible; the sheet's f34 draws it in the door opening). It
   lies at x −0.9, behind the left flap from the f34 camera. Fix:
   - Move it to the right half of the doorway (x ≈ +1.0 … +1.6, still along Y, front end about y −3.0), where the
     f34 camera sees through the door. The floor plan is a top cell, judged for content only.
   - Mirror the walk paths, the turn point and the `door_check` lane to x ≈ −1.0 so they keep their clearance.
   - Lighten the bedroll's tan and end toward the sheet (`#A76D33` shaded, `#C88E4E` target).
   - Target: ≥ 30 % visible at (−42, 25).

### Minors

- The hem sits 0.005 over the mat, which leaves a grazing light slit at the side and back hems (53 of 2.2 M rays,
  whole-interior scan). Seating the hems 0.005–0.01 into the mat (Z_HEM ≈ 0.195) closes it. The builder's escape box
  (y ±2.3, `floor: False`) doesn't reach the ends or the floor junction. Widen it to the whole interior.
- Lashing wraps read as straight flat bars across the X. Rounder rope sections that follow the poles would match the
  joint-detail cell better.
- The back lashing renders brighter and yellower than the sheet (`#F9B240` against `#DE9336`). The crate is a little
  dark (`#7B4119` against `#8C491D`).
- The hem ties are small against the sheet r34's chunky loops.
- The sheet's ground lantern hangs from a post with an iron arm; ours sits on top of a 1.0 stake.
- Recorded and not scored: canvas clipping, the dark interior, f34 / front W : H, the 4° lean, the side-by-side
  poles, the lantern's size in the front cell, and the r34 / front-cell dressing positions.

## Main session after round 1 (2026-11-04)

Fix round:
1. **Blockers 1 and 2, as the verifier gives them.** Move the roll into the doorway plane, shorter. Hang the lantern
   from the front lashing just outside the frame, with its socket moved. Move the bedroll to x about +1.0 to +1.6 and
   mirror the walk lanes and `door_check`. Targets:
   - glass and roll at least 50 % visible at f34 and side;
   - bedroll at least 30 % visible at f34;
   - roll underside and lantern bottom at 7.0 or higher.
2. **Minors:**
   - seat the hems 0.005–0.01 into the mat, and widen the escape box to the whole interior with the floor check on;
   - rounder lashing wraps;
   - back lashing toward `#DE9336`;
   - crate toward `#8C491D`;
   - bedroll tan toward `#C88E4E`.

Round 2 goes to a fresh verifier.

## Fixes after round 1

Fix modeller, 2026-11-04, on `wip/M064.blend` (light work file). Only the main session's fix list; everything else is
as before. No part was renamed or dropped. In the hero, the shells `roll_core-1`, `roll_core+1` and `hanger` are gone
and `hook` is new (105 shells, was 107).

### What changed (`m064.py`)

1. **Rolled door flap (blocker 1).** A custom 10-sided roll (`roll()`), Ø 0.74 (flat radius 0.37), underside **7.02**,
   top 7.76, now in the doorway plane between the front poles at w 0.21–0.99 (axis w 0.60, y −5.73), 2.70 long at mid
   height. Its −X end is cut along the outer pole A's side face and sunk 0.015 into it. Its +X end is cut along the
   mirrored face, so from the front it ends at the inner pole B's edge; it stands clear in front of B. That end is the
   darker rolled-canvas key. The two rope bands stay, at x ±0.55; the proud cores are gone.
   - Departure from the verifier's w −0.45 … −0.1: in the inner pole's depth (w −0.455, tried first), the leaning
     outer pole hid 83 % of it from the f34 camera (17.5 % visible).
   - In the outer pole's depth, moving it forward is what shows it: w 0.455 gives 61 % with no lantern, w 0.60 gives
     68 %. Its front is 0.08 proud of the pole's front face.
2. **Hanging lantern (blocker 1).** It now hangs just in front of the front frame's outer face under the crossing:
   axis (0.50, −6.55), bottom **8.30**, ring top 10.42. A new iron hook (`hook`, 4-sided tube r 0.045, `m064_metal`)
   runs from the second lashing wrap (`lo1`, its start sunk 0.02 into the rope) up over the lantern and down into its
   ring. The ring axis stays X.
   - **Why 0.5 right of centre and why so high.** The studio key light and the hero camera both come from the front
     left, so whatever the lantern stands in front of, it both hides and shades.
   - Centred, with bottom 7.91: it hid two thirds of the roll from the f34 (33 % visible), and its shadow covered 43 %
     of the roll's visible area. That made the roll read beige (`#DBBF93`) in the side cell.
   - At (0.50, 8.30): 63 % visible, 75 % / 72 % of the visible area key-lit at f34 / side (the rest faces away from
     the light), and the side cell reads `#F9D9A8`.
   - **Clearance.** The lantern's back clears the outer pole, the lashing and the inner pole's lower turn by at least
     0.10 (nearest vertex: the roof to pole A).
   - **Overlaps.** BVH overlap with other shells only where pieces are meant to seat: the hook into `lo1` and into the
     ring, and the roll into pole A.
   - **Socket.** The hero `heat_glow` moved with the glass, to (0.50, −6.55, 8.895) in the build frame.
3. **Bedroll (blocker 2).** Now at x **+1.30**, y −3.00 to 0.50 (along Y, front end −3.0), on the right of the doorway
   as the f34 camera sees it. Its tan is lightened (`m064_bedroll` `#9E784A` → `#AA814F`). The end key is
   mix(bedroll, wood_dark) 0.10 (was 0.25) and the core 0.30 (was 0.45). CanvasTentMat carries the same layout.
4. **Walk and door check** mirrored to the −X lane:
   - paths from (−1.0, −9.5) to (−1.0, 1.8), and through (−1.0, −3.0) to (−1.3, 1.0);
   - turn point (−1.4, −0.2);
   - `door_check` lane x −1.55 / −1.0 / −0.45.
5. **Hems (minor).** `Z_HEM` is 0.195: every canvas slab (roof, back, flaps) sits 0.005 into the 0.20 mat, which
   closes the grazing slit at the side and back hems.
6. **Escape box (minor).** The whole interior with the floor check on:
   - box x ±6.0, y ±3.85, z 0.25–10.2;
   - `floor: True`;
   - `wall: 1.0`, so seam rays cross every vertex line of the end pieces down to the hem junctions (|y| 4.6–4.7) and
     of the side hems;
   - y ±3.85 is inside both leaning end pieces at every height, so no grid point lies outside the canvas under the
     pole tips;
   - allowed: `door` (the whole front face), `gable` (the top face's front strip) and `sill` (grazing floor rays that
     leave by the doorway: x ±3.4, y up to −1.0, z 0.2–0.3).
7. **Lashing wraps (minor).** The three wraps round both poles are now 6-sided rope on a 12-point hull loop (was 5 on
   10), so the hull's chamfered corners stay. They read rounder in `lash_cu.png`. The runs between the poles are still
   straight (the hull is taut). The lower lobes and the foot bands are unchanged. The frame part went from 782 to 902.
8. **Colours (minors).**
   - The back frame's lashing uses mix(rope, rope_deep) 0.75, by position; the front lashing and every foot band keep
     `m064_rope`.
   - The crate body is mix(wood_dark, timber) 0.25 and its frame mix(wood_deep, wood_dark) 0.40, a step lighter than
     the barrel's wood (which is unchanged).

### Measured

**Visibility** (camera-facing area of the shell visible from the framed sheet camera, long lens, perspective rays,
area-weighted; the verifier's test):

| Shell | f34 (−42, 25) | side (−22, 6) | front (0, 0) | Target |
| --- | --- | --- | --- | --- |
| Lantern glass | 62.1 % | 81.7 % | 93.8 % | ≥ 50 % (f34, side) |
| Roll | 62.6 % | 79.8 % | 89.5 % | ≥ 50 % (f34, side) |
| Bedroll | 47.9 % | 89.5 % | 78.2 % | ≥ 30 % (f34) |

Round 1 for comparison: glass 0 / 0 %, roll 0 / 93 % (shaded), bedroll 2.6 % at f34. Roll underside 7.02, lantern
bottom 8.30 (both ≥ 7.0).

**`kit_verify` (structure): 0 problems** in 10.1 s.

| Object | Tris | Size (W × D × H) |
| --- | --- | --- |
| CanvasTent | 4268 / 6000 | 20.50 × 15.03 × 12.00 |
| CanvasTentFrame | 902 | 14.43 × 2.78 × 12.00 |
| CanvasTentPanel | 116 | 6.69 × 9.41 × 10.31 |
| CanvasTentMat | 116 | 13.54 × 9.42 × 1.29 |
| CanvasTentCrate | 444 | 2.42 × 2.42 × 2.20 |
| CanvasTentBarrel | 256 | 2.10 × 2.21 × 2.72 |
| CanvasTentStone | 20 | 1.13 × 1.03 × 0.92 |
| CanvasTentPeg | 92 | 0.75 × 0.75 × 1.30 |
| CanvasTentLantern | 144 | 1.12 × 1.12 × 2.09 |

- **Hero.** 105 shells; floating 0, unchained 0, buried 0; deepest seat 0.048; smallest corner 3.26°. No
  non-manifold, bowtie, boundary, winding, inward or self-intersecting shells. UV clean.
- **Sockets and points.** Sockets: hero 2 × `heat_glow`, Lantern 1. Glow key `m064_glow`. Stored points `m064_door`
  and `m064_inside`.
- **Walk.** Path 1: clearance 0.41 (chest lid). Path 2: clearance 0.56 (left flap). Both: 0 intersecting steps, one
  rise of 0.20, proxy-wide headroom 6.35 / 6.13 (the ruled A-frame narrowing). Turn point (−1.4, −0.2): 0.41 at every
  yaw (roof).
- **`door_check`.** Headroom over the lane 7.02, the roll's underside. Doorway rays all clear: 3.6 wide to 6.5, ±1.0
  to 7.0.
- **Escape scan.** 208 points, 101 floor points and 43,683 seam points; 213,769 rays, **0 leaks**. Allowed escapes:
  door 37,449, sill 16.
- **Independent whole-interior scan** (`<temp>/...`):
  - 6,567 points inside the canvas (sag allowed for) from z 0.26 to the ridge and to the end pieces;
  - 240 directions each, plus lower-hemisphere rays from the floor row: 1.64 M rays;
  - every escaping ray crosses the front canvas plane inside the doorway (|x| < the door edge, under 6.95) or the
    gable: **0 leaks** (round 1: 53 grazing leaks at the hems).

**Colours.** Sampled from long-lens renders of the hero at the sheet cameras: the medians of the visible, camera-facing
area of each region, lit and shaded together. That differs from the verifier's crop medians, so each row also gives
the same sampler on the round-1 keys:

| Region | Sheet target | Round-1 keys | Now |
| --- | --- | --- | --- |
| Back lashing (f34) | `#DE9336` | `#FFC247` (verifier: `#F9B240`) | `#ECA138` (≈ `#E29432` on the verifier's scale) |
| Crate (f34) | `#8C491D` | `#82451A` (verifier: `#7B4119`) | `#955126` (≈ `#8D4C24` on the verifier's scale) |
| Bedroll tan (f34) | `#C88E4E` | `#B98448` | `#C88F4E` |
| Bedroll end (side) | `#A76D33` | — | `#B77D41` |
| Roll (side) | `#FCE5BD` | (verifier: `#978465`) | `#F9D9A8` |
| Barrel (f34) | `#964D1D` | `#8F4C1C` | `#8F4C1C` (unchanged) |

### Renders and comparison

`build(close=True)` rewrote every file in `art/blender/renders/models/M064/`: `M064_views.png`, the six sheet views,
exploded, scale, and `lash_cu`, `door_cu`, `inside_cu`. `m064.compare()` wrote all six cells to
`<temp>/RBLX-Flintborn/compare/M064/M064_compare.png`.
- **f34:** the lantern hangs under the front lashing, the cream roll with its two bands spans the door top, and the
  tan bedroll lies on the mat in the doorway, seen mostly end-on.
- **Side:** the lantern hangs above a lit cream roll.
- **Front:** the lantern is under the crossing, the roll spans the poles, and the chest and bedroll are inside.
- W : H as before: f34 1.21 / 1.42, front 1.62 / 1.28, side 1.66 / 1.44.

New recorded misses (the hero view governs):
- **Front cell.** The lantern hangs 0.5 right of the crossing, not centred, and overlaps the right pole's inner edge.
  This is the placement that keeps the roll visible and lit in the hero view.
- **True side (rear cell, az 90).** The lantern and the roll's end show in front of the frame, as the round-1 ruling
  allows.
- **Roll seating.** The roll lies in the outer pole's depth, not behind it. Its front is 0.08 proud of the pole's
  front face, and its +X end stands clear in front of the inner pole.
- **Lashing.** The wraps still run straight between the poles (taut over the hull). They are rounder in section,
  not bulged.

## Stage 7 verification (round 2)

**Result: PASS, 8/10.** Both round-1 blockers are fixed and every target is met. The lantern hangs under the front
lashing, and the cream roll with its two bands spans the door top in the hero view and the side cell. The bedroll lies
on the mat in the doorway. Technically clean: 0 problems, 0 light leaks over the whole interior, the doorway walks and
the headroom holds. Left over, all minor: in the hero view the bedroll reads as a short tan stub, and its teal band is
lost against the mat; the hem ties are thin. Read-only session on `wip/M064v.blend` (no build, no save); renders and
scripts in `<temp>/...`.

### Technical (re-run)

- `kit_verify.run` (all 9 objects, `m064.VERIFY`, size 20.5 ± 0.3 × 15.0 ± 0.3 × 12.0 ± 0.02): **0 problems** in 12.9 s.
  - Hero 4268 / 6000 tris, 20.499 × 15.026 × 12.000, 105 shells, all matched to the register.
  - No non-manifold, bowtie, boundary, wire, loose, zero-area, n-gon or duplicate elements, and no winding,
    parity-inward, self-intersecting or negative-volume shells. Smallest corner 3.26°.
  - Floating 0, unchained 0, buried 0. Deepest seats: roll band in roll 0.048, hook in `front_lash_lo1` 0.046,
    roll in pole A 0.013. 0 pierces of the 4 canvas shells.
  - UV: 0 overlaps or flips, gap 0.016, border 0.008. Origin offset 0, transforms applied, no modifiers or custom
    normals, `K.check` clean. Tint against normal clean (canvas Tint 0.955–1.028).
- Parts: Frame 902, Panel 116, Mat 116, Crate 444, Barrel 256, Stone 20, Peg 92, Lantern 144 tris. All clean; sizes
  match the spec's table. Frame is 902 / 999, just inside the house rules' 10 % margin.
- **Sockets and stored points.**
  - Hero: 2 × `heat_glow`, at (0.50, −6.55, 8.895), the hanging glass's centre (glass box x 0.11–0.89, y −6.94 to
    −6.16, z 8.415–9.375), and at (−7.3, −4.4, 1.598).
  - Lantern part: 1 × `heat_glow` at its glass centre (0, 0, 0.595). Glow key `m064_glow`.
  - Stored points: `m064_offset`, `m064_door` on the front canvas plane and `m064_inside` at the mat centre.
- **Walk** (proxy, both −X paths from y −9.5):
  - clearance 0.414 (chest lid) and 0.562 (left flap), 0 intersecting steps, one rise of 0.20 each;
  - proxy-wide headroom 6.35 / 6.13, both at the ruled A-frame narrowing;
  - turn point (−1.4, −0.2): 0.41 at every yaw (roof).
- **`door_check`.** Headroom over the lane 7.02 (the roll's underside), and no doorway ray blocked (3.6 wide to 6.5,
  ±1.0 to 7.0). Measured heights: roll underside 7.02, lantern bottom 8.30, hook top 10.62.
- **Escape scan, builder's whole-interior box** (x ±6.0, y ±3.85, z 0.25–10.2, `floor: True`, `wall: 1.0`):
  - 208 points, 101 floor points, 43,683 seam points, 213,769 rays: **0 leaks**;
  - allowed escapes: door 37,449, sill 16.
  - Its `door` allow box is the box's whole front face, so I also scanned independently with a stricter rule.
- **Independent whole-interior scan:**
  - points: 5,726 on a 0.45 grid inside the sagging canvas, from z 0.26 to the ridge and out to both end pieces;
    858 points hugging the side hems and the back piece at z 0.21–0.8, with lower-hemisphere rays too; 682 floor
    points at the mat top, with downward rays;
  - 1.76 M rays in all;
  - an escaping ray passes only if it crosses the front canvas plane inside the doorway (|x| ≤ the door edge + 0.05,
    below 6.95) or the open gable above it.
  - Result: **0 leaks**. 111,753 escapes, all through the doorway or gable; round 1 had 53 grazing hem leaks.
- **New pieces against their neighbours** (BVH overlap and nearest distance). Overlaps only where the pieces seat:
  - roll into pole A, and the bands into the roll;
  - hook into `front_lash_lo1` and into the ring;
  - the lantern's own pieces;
  - bedroll and core into the mat.

  Nothing else comes within 0.08 of the lantern, the roll or the bedroll.

### Blocker check (round 1)

Area-weighted share of each shell's camera-facing area that is visible. Measured two ways: perspective rays from the
actual compare camera (lens 3×), and parallel rays at the sheet angle.

| Shell | f34 persp. / parallel | side persp. / parallel | Target |
| --- | --- | --- | --- |
| Hanging lantern glass | 68.1 % / 62.9 % | 80.9 % / 84.8 % | ≥ 50 % |
| Roll | 60.2 % / 55.7 % | 76.8 % / 81.2 % | ≥ 50 % |
| Bedroll | 47.2 % / 52.1 % (teal band 33.5 %) | 92.0 % / 86.6 % | ≥ 30 % at f34 |

- **Lantern: fixed.** In the f34 it hangs on its hook just right of the front lashing, in front of the gable, where the
  sheet's f34 draws it. In the side cell it hangs over the roll. Glass `#FFC306` against the sheet's
  `#D99721`–`#FBC920`; the brighter glass is Neon, previewed unshaded.
- **Roll: fixed.** A cream roll with two rope bands across the door top, key-lit:
  - f34 `#FFF0B7` against the sheet's `#FDE6BB`;
  - side `#EDCF9E` against `#FCE6BF`: a little darker, but cream, not round 1's grey `#978465`.

  In the f34 the near pole A still hides its left 40 %, and it is thinner than the sheet's chunky scroll (Ø 0.74).
  It reads as a roll.
- **Bedroll: target met, weak read (minor).**
  - In the f34 the camera sees the front 1–1.5 studs, end-on, as a tan stub. Its tan `#C78E4E` is on target
    (`#C88E4E`). The rest slides behind pole A and the left flap.
  - The teal band (`#495F4D`) is only a third visible, and it merges with the teal mat (`#508273`). The sheet's f34
    draws a full roll with a dark teal band (`#3C543C`) across the opening.
  - It reads as the sheet's bedroll in the side cell (tan, teal band, end) and in the front cell, end-on, as ruled.

### Views against the sheet (`compare.py`, all six cells at 360 and 900 px, plus doorway crops)

- **f34 (hero).**
  - Silhouette, X frames with crossings and tip overhang, ridge lashings, foot bands, pegs, crate, both barrels,
    stones and ground lantern all as before.
  - The doorway now shows the lantern, the roll and the bedroll (see above).
  - W : H 1.21 against 1.42 is the recorded perspective miss.
- **Side cell (−22 / 6).**
  - The lantern hangs above a lit cream roll with bands.
  - The bedroll shows tan with its teal band and a lighter end, the chest behind it, and the mat, flaps and turned-back
    strips.
  - The lantern hangs right of the crossing, not centred (recorded).
- **Front cell.**
  - Content matches: the X, the lashing, the lantern under the crossing (0.5 right, over the right pole's inner edge;
    recorded), the roll spanning the poles, the flaps, the chest, the mat and the dressing.
  - Bedroll end-on (ruled). W : H 1.61 against 1.28 is the recorded dressing spread.
- **r34.** Content matches; crate placement as ruled. The hem ties are thin rope hoops against the sheet's chunky loops
  (minor, from round 1).
- **Rear cell (true side).** The trapezoid canvas, frames, lashings and two hem ties all read. The lantern and the
  roll's end show in front of the frame (allowed by the round-1 ruling). 4° lean and side-by-side poles ruled.
- **Top.** Content only: passes.
- **Exploded, scale and close-ups.**
  - Part set as the exploded cell.
  - `lash_cu`: the wraps are rounder in section than in round 1, but still run straight between the poles (minor).
  - `door_cu`: the roll's darker +X end cap reads as a grey block from below (minor).
  - `inside_cu`: closed, with the chest, mat and bedroll.
- **Colours** (render medians of visible camera-facing area at the sheet cameras, against sheet crops, sheet / ours):

  | Region | Sheet | Ours |
  | --- | --- | --- |
  | Front pole | `#DB6C10` | `#D9610C` |
  | Back lashing (f34) | `#DE9336` | `#E49B39` / `#F6A83A` (hi / lo wrap) |
  | Crate (f34) | `#8C491D` | `#945127` |
  | Barrel (f34) | `#964D1D` | `#8F4E1E` |
  | Mat (f34) | `#508272` | `#508273` |
  | Bedroll tan (f34) | `#C88E4E` | `#C78E4E` |
  | Bedroll band (f34) | `#3C543C` | `#495F4D` |
  | Roll (side) | `#FCE6BF` | `#EDCF9E` |

  The round-1 colour minors are fixed: the back lashing, the crate and the bedroll tan.
  Recorded and not scored:
  - the key-lit canvas clips toward white;
  - the interior is studio-lit beige, not the sheet's dark brown;
  - soft dark smudges on the canvas near the hem ties and ridge in the top, rear and r34 renders. These were also in
    round 1 and are render-only: the canvas Tint is uniform, 0.955–1.028.

### Blockers

None. Nothing is broken, and the tent, its doorway and the round-1 blocker items read as the sheet draws them.

### Minors (none blocks committing)

1. **Bedroll in the hero view.** It reads as a short tan stub; its band disappears into the mat. Fix, one of:
   - move it to x ≈ +1.8, front end y ≈ −3.6, still along Y (parallel-ray side visibility 48 % → 77 %);
   - or yaw it about 20° with the back end toward +X (87–100 %).

   Then darken the band toward `#3C543C` so it separates from the mat. Keep the −X walk lane, the turn point and
   `door_check` as they are; the bedroll stays inside the right door edge and clear of the chest.
2. **Roll.** Thinner than the sheet's scroll (Ø 0.74), with its left 40 % behind pole A at f34. Its darker +X end cap
   reads grey from below and in the side cell's shade. Optional: Ø about 0.9 with the underside kept at 7.02, and a
   lighter end key.
3. **Hem ties** (round 1, not on the fix list). Thin hoops against the sheet r34's chunky loops: r 0.09 → about 0.14,
   standing out further.
4. **Ground lantern** (round 1). It sits on top of a 1.0 stake; the sheet hangs it from a post with an iron arm.
5. **Lashing.** The wraps are rounder in section but still straight between the poles. The joint-detail cell bulges
   them round the crossing.
6. **Side-cell roll** about 15 darker than the sheet's cream (`#EDCF9E` against `#FCE6BF`). Studio shading; the
   roll's key is the canvas cream.
7. Recorded, not scored (rulings and earlier records):
   - the lantern 0.5 right of centre in the front and side cells;
   - the lantern and the roll's end showing past the frame in the true side;
   - f34 / front W : H;
   - the 4° lean and the side-by-side poles;
   - the dressing positions in the r34 and the front cell;
   - canvas clipping;
   - the dark interior.
