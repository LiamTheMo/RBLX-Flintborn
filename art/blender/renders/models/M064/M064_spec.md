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
