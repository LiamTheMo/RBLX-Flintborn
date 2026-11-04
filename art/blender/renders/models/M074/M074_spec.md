# 074 Fire and Light Station — spec

Reference: `art/blender/assets/references/074.png` (header "71 — FIRE AND LIGHT STATION", page 71/132; sheet 074).
Builder: `art/blender/kit/mcp/m074.py` → `build()`, on the shared library (`kit_parts` / `kit_build`). Procedure:
`art/blender/kit/mcp/STAGES.md`; standing answers: `HOUSE_RULES.md`. A new build: no earlier builder or spec.

## Brief

- **Sheet:** 074 Fire and Light Station (remake: no). Family: none.
- **Class and budget:** asset (a campfire station, nothing to walk into), ceiling 4000, plan about 2600 (built 2544).
  Every part far under 1000.
- **Size:** no house rule for campfires, so sized against the 5-stud character and the props: the front cell
  measures stone ring 233 px, tripod top 169 px over the ring centre, pot 58 px, stone height about 1.3 at the
  ring's px/stud. Stones at seat height (1.35, HOUSE_RULES seat 1.50), tripod top 5.98, pot 2.0 across with its rim
  at 3.40 (sheet 3.5). Hero bbox **8.69 × 8.95 × 5.98** (the ring is not round in plan: three wider gaps).
- **Hero view:** front three-quarter at az −30, el 20. The layout is drawn in a view frame facing that camera and
  turned −30° into the build frame, so the hero sees the tripod's front pair symmetric and a stone dead ahead, as
  the sheet draws it. The rear three-quarter (az 150) then shows the back pole centred, as the sheet does. Front,
  side, rear and top cells (az 0 / 90 / 180, el 12; top el 75): content only — all four draw the same symmetric A,
  which no three-pole tripod can show from four sides.
- **Parts:**
  | Part | What | Tris |
  | --- | --- | --- |
  | TripodCookfirePole | Tripod Pole: 0.46-square chamfered pole with three seam grooves, foot cut flat on z 0 | 64 |
  | TripodCookfireRopeBind | Rope Bind: three twisted turns and three crossing X wraps, as on the hero | 768 |
  | TripodCookfireHangingPot | Hanging Pot (+ hanger): cauldron, two lugs, bail, two chain links | 672 |
  | TripodCookfireLog | Log Piece: 2.40 × 0.64 × 0.56 split log with its split grooves | 52 |
  | TripodCookfireStone | Stone: one ring stone 2.2 × 2.0 × 1.35 | 84 |
- **Palette** (swatches → rendered medians → `MODEL.calibrate`): swatches wood #BA6520, rope #E4BA81, metal
  #494849, stone #8B898F, fire #FD7214 (VFX only). Keys: `m074_wood` **#8B5429** (calibrated #87572E on the target
  #A8642F, the log detail / exploded poles, then nudged redder to the sheet's pole class median), matte 0.85;
  `m074_wood_end` #B07443 (cut ends, pole tops); `m074_wood_deep` #4E2C15 (seam and split grooves); `m074_rope`
  **#BE9E68** (target #F0BE72) with `m074_rope_deep` #93744A on one strand in four; `m074_iron` **#383538** (target
  #403C3C, underside / exploded pot), rough 0.55, metal 0.35; `m074_iron_in` #1C1A1C inside the pot; `m074_stone`
  **#7A7A86** (calibrated #73747F on #8E8B91, then lifted to the class medians), matte 0.9.
- **Lights / VFX:** no flame mesh (the sheet: "Fire is a separate VFX element, not modeled geometry"). Sockets at the
  fire centre: `campfire` at (0, 0, 0.30) (flames, sparks, smoke and its PointLight) and `heat_glow` at (0, 0, 0.55),
  both with the vfx.py defaults. No emissive keys; no warm glow baked into stones or logs (the sheet's orange tint is
  the fire's light; its log detail is plain wood).
- **Collision:** hero `hull` (HOUSE_RULES: nothing to walk on or into); Pole, HangingPot, Stone `hull`; Log `box`;
  RopeBind `none` (dressing).
- **Checks to switch on in kit_verify:** `cls="asset"`, `sockets={hero: [campfire, heat_glow]}`; the builder's
  `station_check` (nothing under z 0, placement numbers).
- **Departures from HOUSE_RULES:** none against the rules. Recorded choices:
  - the hero layout is turned −30° to face the hero camera (hero governs; the ortho cells' four identical A-frames
    are content only);
  - nine stones, not "about 10–11": the top cell and the exploded view both draw nine, and the hero shows nine;
  - pole feet stand on z 0 in three wider gaps of the ring (45° against 37.5°) rather than inside it: the sheet's
    tripod spreads about 33° from vertical, and only feet out at the ring (radius 3.28) give the pot's rim room
    between the poles. The six stones beside a foot are 0.92 wide so the leaning poles clear them.
- **Questions for the main session:** none.

## Stage 1 — Modelling

Build frame: front −Y, +X right, ground z 0, fire centre at the origin; the layout is written in the view frame
(front = hero camera) and placed through `P.frame(VIEW)`, a −30° turn about Z.
- **Stones:** nine closed hull shells (`stone()`): five rings of a superellipse footprint (exponent 0.75, boxy like
  the sheet's boulders) from a 0.88 base to a broad 0.58 top, the wide rings with a point on each side's middle so
  neighbours meet; 2.28 × 2.15 × 1.40 nominal (±5 % per stone), long side along the ring, centres on radius 3.45.
  One stone straight in front of the hero camera, gaps 37.5° except 45° at the three feet. 84 tris each.
- **Tripod:** three poles from feet at radius 3.28 (view az −150, −30, 90) through a crossing at z 5.30, each axis
  passing 0.25 to the side of the centre (a twisted tripod: the poles rest on each other, no interpenetration past
  0.05), 0.66 past the crossing (top 5.98). Section 0.46 square, chamfer 0.06, a 0.06-wide 0.045-deep V seam down the
  upper and both side faces (the sheet's split-timber line); foot cut flat on z 0, end grain on top; caps ear-clipped.
- **Rope bind:** three closed twisted 6-sided turns (r 0.14) at z 4.84 / 5.10 / 5.36, each round its own height's
  section of the three poles (hull, offset r − 0.02, corners rounded on arcs, so the coils read round), touching.
  Over them three crossing X wraps (the junction detail's crossings), one on each face between two poles: two
  4-sided twisted ropes (r 0.10, m051's variable-radius rope) from the bottom turn to the top turn across 56°, the
  second lifted at the crossing so the two lie on each other.
- **Chain, bail, pot:** the upper link's top rises 0.02 into the lowest of the poles' undersides over it (rays up
  through the crotch: 4.73); link 1 hangs in it at 90°; the bail's apex rests on link 1's bottom wire; a 6-sided bail
  arch (r 0.05, rise 0.80) ends 0.04 into two lugs seated 0.02 into the rim band; the cauldron is one 14-sided lathe
  shell (flat bottom, belly r 1.00, neck, thick rim band 0.90, then the inner wall and a floor 0.46 up), bottom at 1.81.
- **Logs:** split logs 0.64 × 0.56 (chamfer 0.05, V grooves along the top and one side, cut ends `wood_end`): the
  left one (2.17) and a short right one (1.15) on the ground, the third (2.26) with its foot edge on z 0 toward the
  camera-right and tilted 23.5° until it rests 0.02 into the left log (solved against that log's edges).
- **Parts:** each from the same piece functions as the hero (`pole`, `bind`, `hanging_pot`, `log_beam`, `stone`).

## Stage 2 — Optimisation and cleanup

kit_verify (`cls="asset"`, hero and five parts): **0 problems**. Hero **2544 / 4000** tris, 30 closed shells (stones
9 × 84, logs 3 × 52, poles 3 × 64, turns 552, wraps 216, links 2 × 64, pot 392, lugs 2 × 12, bail 128); 0 non-manifold
edges, bowties, boundary, wire, loose, zero-area faces, n-gons or duplicate verts; normals outward; 0 winding,
parity, self-intersection or negative-volume shells; min corner 4.1° (a pole cap's ear at a seam groove). Origin at
the bbox bottom centre, transforms applied, no modifiers or custom normals. Floating 0, unchained 0 (15 grounded);
buried 0, deepest 0.052 (wrap in a turn; rope-in-rope limit 0.08), then 0.048 bail in lug, 0.041 bail on a pole,
0.039 stone against a pole foot, 0.038 turn in a pole. Parts, each 0 problems: Pole 64 (3.85 × 2.14 × 5.98), RopeBind
768 (2.06 × 2.04 × 0.80), HangingPot 672 (2.12 × 2.00 × 2.90), Log 52 (2.40 × 0.64 × 0.56), Stone 84
(2.25 × 2.03 × 1.35).

## Stage 3 — UV

kit_build cleanup: angle-based unwrap, margin 0.008. Hero 698 islands, 0 overlaps or flips, min gap 0.016, border
0.008, density even, conformal stretch p95 1.04; all parts clean. The exporter writes its own palette UVs.

## Stage 4 — Materials and colour

Sheet medians (Blender numpy on the reference): log detail #AA6735 (lit #DA8C4B), exploded poles #A15B2A, junction
wood #B66D35; rope junction #F3BB6E, exploded #F3C57D; pot underside #47423F, exploded #383639; stones rock detail
#88868F, f34 #8C888E, top #978D92. `MODEL.calibrate` on the studio dome: wood #87572E, rope #BE9E68, iron #383538,
stone #73747F. Class medians of the compare pairs (sheet → ours) then moved wood to #8B5429 and stone to #7A7A86:
- f34: stone #938C92 → #8C8990, wood #9C501E → #9B5E2C, iron #393337 → #363232;
- front: stone #989198 → #858289, wood #984D1E → #965A2A, iron #373234 → #3B3B3E;
- top: stone #998E93 → #8B8891, wood #964B22 → #975D2F.
The sheet's wood and rope classes include fire-lit pixels (redder, and its rope class picks up flame pixels), so
those differences are the fire's light, not the base colour. Colour by role and position only: seam and split grooves
`wood_deep`, cut ends `wood_end`, one rope strand in four `rope_deep`, the pot's inside `iron_in`. Per-piece Tint
±0.02–0.05 and broad mottling on every piece. Tint against normal: worst −0.116 (stone), iron 0.21 (limit 0.3).

## Stage 5 — Lighting

No emissive geometry: the sheet's glow is the fire's, and the fire is VFX. The `campfire` socket carries its
PointLight (#FF8C2A, brightness 2.5, range 28, flicker) and `heat_glow` a second soft light (#FF7A22, 1.2, range
10), both vfx.py defaults. Studio: Requires Manual Validation that the two lights together don't over-brighten the
stones at night; drop `heat_glow`'s light if they do.

## Stage 6 — VFX

`FX = {TripodCookfire: [("campfire", (0, 0, 0.30)), ("heat_glow", (0, 0, 0.55))]}` at the fire centre (the build
frame's origin; hero-local (−0.10, 0.02, z) after recentring). kit_verify sockets: exactly campfire + heat_glow. Export
STATS: hero 2 sockets, no glow keys; parts none. The renders show the kit's VFX preview (flames, glow, smoke) from
these sockets; the compare renders are without it.

## Renders and compare

`build()` writes `art/blender/renders/models/M074/` (`M074_views.png`: f34, r34, front, side, rear, top, exploded,
scale with the 5.5-stud character; `build(close=True)` adds `junction_cu` and `pot_cu`). `m074.compare()` writes the
side-by-side sheet to `<temp>/RBLX-Flintborn/compare/M074/M074_compare.png` (or `out_dir`). Content W : H (sheet /
ours): f34 1.35 / 1.16, r34 1.27 / 1.16, front 1.16 / 1.21, side 1.11 / 1.23, rear 1.13 / 1.22, top 1.10 / 0.99.

Known misses, recorded:
- f34 / r34 W : H: the sheet's three-quarters are drawn with strong perspective (the near stones loom large); the
  square-on cells, which have little, agree within 5 %.
- Front, side and rear cells all draw the same symmetric A with the pot centred; a three-pole tripod shows that from
  one side only (content only, hero governs). The top cell is drawn with the tripod unrotated (back pole straight
  up); ours is turned −30° with the hero.
- The rope bind reads as a thick coil with X wraps; the sheet's is three neat thick turns with looser crossing
  loops. The chain is mostly hidden under the bind (the sheet shows about 0.5 of chain below it).
- The sheet's logs read as a denser pile with glowing ends; ours are three plain split logs (as the sheet's log
  detail and exploded view draw them).
- Studio light: the side cell reads darker than the sheet's (key light front-left; the sheet lights every face).

## Stage 7 — verification (R1)

**Result: FAIL, 6.5 / 10.** Fresh verifier, read-only, in a background session on the work-file copy
`wip/M074v.blend` (nothing rebuilt or saved). One blocker: the top junction. Everything else reads as the sheet's
station: the ring of nine boxy stones, the hanging cauldron, three split logs, tripod lean and the sockets.
Verifier renders and the compare sheet are in `M074/verify/`.

**kit_verify** (`cls="asset"`, sockets campfire + heat_glow, size 8.9 × 8.9 × 6.0 ± 0.3): **0 problems**. Hero 2544 /
4000 tris, 30 shells, 8.69 × 8.95 × 5.98; floating 0, unchained 0, buried 0 (deepest 0.052, a wrap in a turn, under
the 0.08 rope-in-rope limit); min corner 4.1°. Parts: Pole 64, RopeBind 768, HangingPot 672, Log 52, Stone 84, each 0
problems. Names unique (`TripodCookfire*` appears only in m074.py); collision hero / Pole / Pot / Stone `hull`, Log `box`,
RopeBind `none`; eight `FB_m074_*` keys; sockets `campfire` (0, 0, 0.30) and `heat_glow` (0, 0, 0.55) at the fire centre.

**compare.py** content W : H (sheet / ours): f34 1.35 / 1.16, r34 1.27 / 1.16, front 1.16 / 1.21, side 1.11 / 1.23,
rear 1.13 / 1.22, top 1.10 / 0.99. The three-quarter gap is the sheet's perspective (recorded). The ortho cells are
4–11 % too short for their width, which is the same junction miss (below).

**Colour** (class medians, sheet → ours): stone f34 #827F89 → #959199, front #8E8990 → #8D8991, top #827D86 → #949099;
wood f34 #8D4519 → #9F5927, rock and log detail #9D6033 → #A25A27 (the sheet's assembled wood is fire-lit); iron f34
#353034 → #353131, pot detail #3A3A3B → #322F2E; rope junction detail #FCD68C → #ECBC71 (our junction close-up), f34
#E1B46D. All within the recorded lighting differences except the rope, which is a little dark and orange (minor).

### Blocker

1. **Top junction reads as a crumpled nest with the pole tops buried in it.** The sheet's junction detail and all six
   assembled cells show three pole tops standing well clear of a neat three-turn rope bind, splayed outward with
   octagonal end grain (an X of tops over the bind). Ours (f34, `verify/v_junction_f34.png`, `v_junction_top.png`):
   - the bind sits below the crossing (turns at CROSS_Z − 0.46 / − 0.20 / + 0.06, bind z 4.70–5.50), where the poles
     have spread, so the bottom turn is r 0.94;
   - the tops are only POLE_EXT 0.66 past the crossing: outer corners at r 0.70, *inside* the bind's footprint, and
     0.48 above its top. They read as one stubby bundle, not three splayed ends;
   - the twisted 6-sided turns (`twist=True`) and the twisted 4-sided X wraps make faceted zig-zags, so the bind reads
     as straw, not as three round coils.

   Fix (in m074.py, measured from `pole_axis` / `pole_section` / `round_loop` without rebuilding):
   - `BIND_Z = (CROSS_Z - 0.26, CROSS_Z, CROSS_Z + 0.26)`: the bind is centred on the crossing (z 4.90–5.70), outer r
     0.85 / 0.78 / 0.88 (was 0.94 / 0.83 / 0.79). Its bottom then clears the chain's top (crotch 4.75), so the two
     links show under the rope as the pot-hanging detail draws them;
   - `POLE_EXT = 1.20` (from 0.66): top corners at r 0.95, clear of the bind's 0.88, and the top at z 6.44, 0.74 above
     the bind. Measured: 1.10 gives r 0.90 / z 6.36 and 1.30 gives r 0.99 / z 6.53. The ortho W : H goes from about 1.21
     to about 1.13, against the sheet's 1.11–1.16. Update `TARGET_SIZE` z to (6.45, 0.15) and the spec's sizes;
   - turns `twist=False` in `bind()` (the library's mode for turns round timber, aligned rings with spiral strands, as
     in m066 / m070), and in `vrope` drop the half-step per ring (`ang = 2π k / sides`), or use `sides=6`, for the X wraps.
     Estimated: 6-sided wraps take the bind from 768 to about 888 tris (part < 1000) and the hero to about 2664;
   - re-run the junction close-up and require the three tops to read as separate splayed ends in f34, front and top.
   Changing TWIST does not help: 0.18 or 0.12 narrows the bind only to r 0.82 / 0.78, and the poles then
   interpenetrate (axis distance 0.30 / 0.20 against 0.41 now).

### Minors (recorded, not blocking)

- **Stones** are rounder lumps than the sheet's angular, flat-topped boulders. The rock detail's W : H is about 1.9 with
  a top plane about 65 % of the width; ours is 1.67 with the top ring at 0.58. Cheap tweak: `STONE_H` 1.40 → 1.25 and the
  top ring (1.0, 0.58, 6) → (1.0, 0.70, 6). Check the leaning-pole clearance afterwards.
- **Stone tone** is about +0x13 light in f34 and top (front matches). Studio lighting; optional `m074_stone` #7A7A86 →
  #72727E.
- **Rope colour** is a little dark and orange against the junction detail (#ECBC71 against #FCD68C). Optional
  `m074_rope` #BE9E68 → #CCAE78.
- **Pole end grain** shows a "+" from the three seam grooves running out through the cap; the sheet's ends are plain
  chamfered octagons. Acceptable at game distance.
- **Logs** are sparse and mostly hidden under the pot (`v_logs.png`). The sheet's assembled cells read as a denser
  pile; its exploded view and notes say three pieces, so this is content-correct. The fire VFX covers the centre.
- **Chain** is hidden under the bind in f34 (fixed by the blocker's BIND_Z change).
- **Ring gaps** at the pole feet and the top cell's unrotated tripod are accepted departures (main-session ruling).

## Fix after R1

Fresh fix modeller, in `wip/M074.blend` (rebuilt from `m074.py`, saved). Builder changes:
- **Bind centred on the crossing:** `BIND_Z = (CROSS_Z - 0.26, CROSS_Z, CROSS_Z + 0.26)` (z 5.04 / 5.30 / 5.56, bind
  z 4.90–5.70). Turn outer radii 0.849 / 0.778 / 0.875 (were 0.94 / 0.83 / 0.79). The chain's top stays at the
  crotch (4.728), so both links now hang 0.17 below the rope instead of inside it.
- **Tops clear of the bind:** `POLE_EXT` 0.66 → 1.20. Top corners at r 0.945 (bind 0.875) and z 6.441, 0.74 above the
  bind's top; the three tops read as separate ends in f34, front and top (`junction_cu`, `junction_front_cu`,
  `junction_top_cu`). `TARGET_SIZE` z (6.45, 0.15). Hero bbox **8.69 × 8.95 × 6.44**.
- **Round coils:** the turns `twist=False` (aligned rings, spiral strand); `vrope` drops the half-step per ring and
  defaults to 6 sides.
- **Departure from the prescription: one diagonal wrap per face, not an X.** With round 6-sided X wraps the bind still
  read as a woven basket: six short straight diagonals over three turns, with their lifted crossings. Instead, one
  long diagonal per face (`FRAP_SG = (1,)`, `FRAP_SPAN` 28° → 40°, nine path samples `FRAP_T` so it follows the
  coils). The bind reads as three neat turns with crossing loops, as the junction detail draws it. RopeBind 864
  tris (the prescription's X version measured 888), 6 shells.
- **Minors:** `m074_rope` #BE9E68 → #CCAE78; `m074_stone` #7A7A86 → #72727E. Stones flatter-topped: `STONE_H` 1.40
  → 1.25, top ring 0.58 → 0.70 (Stone part 2.25 × 2.03 × 1.20). The leaning poles clear them better: stone in pole
  0.017 (was 0.039).
- `CLOSE`: the junction close-ups are framed on z 5.5 r 1.5 (f34, front and top), the pot close-up on z 3.9 r 1.9.

kit_verify (`cls="asset"`, sockets campfire + heat_glow): **0 problems**. Hero **2640 / 4000** tris, 27 shells (was
2544, 30); floating 0, unchained 0, buried 0; deepest 0.057 (frap in turn, under the 0.08 rope-in-rope limit), then
bail in lug 0.048, bail on pole 0.041, turn in pole 0.032; min corner 4.1°. Parts, each 0 problems: Pole 64
(4.10 × 2.26 × 6.44), RopeBind 864 (1.85 × 1.79 × 0.76), HangingPot 672 (2.12 × 2.00 × 2.90), Log 52, Stone 84.
Pole axes still 0.412 apart (TWIST unchanged).

compare.py content W : H (sheet / ours): f34 1.35 / 1.09, r34 1.27 / 1.09, front 1.16 / 1.13, side 1.11 / 1.16,
rear 1.13 / 1.14, top 1.10 / 0.99. The ortho cells now agree within 5 %. The three-quarter gap grew, from the taller
tripod and flatter stones. It is the sheet's perspective (recorded).

Still recorded, not fixed:
- The sheet draws the tops splayed at about 45° or more from vertical, wider than its own legs' lean. Ours follow the
  poles' straight 31.7° lean, so the X of tops above the bind is narrower than the sheet's. A straight timber can't
  splay more.
- In f34 the back pole's top sits 0.25 left of centre: the twisted tripod's offset. A centred back pole would need
  offsets of about 0.54 (searched) to keep the poles apart, and so a much fatter, off-centre bind.
- The chain hangs from the bare crotch just under the bind and is thin (wire r 0.035); it shows below the rope but
  reads small in f34.

## Stage 7 — verification (R2)

**Result: PASS, 8 / 10.** Fresh verifier, read-only, in a background session on the refreshed copy `wip/M074v.blend`
(nothing rebuilt or saved). The R1 blocker is fixed: the top junction now reads as the sheet's — three pole tops
standing clear above a neat round bind, the chain hanging below it. No blockers. Verifier renders and the compare
sheet are in `M074/verify/r2/`.

**kit_verify** (`cls="asset"`, sockets campfire + heat_glow, size 8.9 × 8.9 × 6.45 with the builder's tolerances):
**0 problems** in 4.3 s. Hero **2640 / 4000** tris, 27 shells, 8.689 × 8.951 × 6.441; floating 0, unchained 0, buried 0,
deepest 0.057 (rope in rope, under 0.08); min corner 4.1°. Parts, each 0 problems: Pole 64 (4.10 × 2.26 × 6.44),
RopeBind 864 (1.85 × 1.79 × 0.76), HangingPot 672 (2.12 × 2.00 × 2.90), Log 52 (2.40 × 0.64 × 0.56), Stone 84
(2.25 × 2.03 × 1.20). Sockets exactly `campfire` + `heat_glow`. The flatter stones (STONE_H 1.25) leave the poles
resting on them, not buried (deepest stone contact under the 0.05 limit; `verify/r2/foot_out.png`).

**compare.py** content W : H (sheet / ours): f34 1.35 / 1.09, r34 1.27 / 1.09, front 1.16 / 1.13, side 1.11 / 1.16,
rear 1.13 / 1.14, top 1.10 / 0.99. Ortho cells within 5 %; the three-quarter gap is the sheet's perspective
(recorded), the top is the accepted turned layout.

**Colour** (class medians, sheet → ours): stone f34 #85828B → #8B8891, front #8F8A91 → #87838B, rock detail #7D7980 →
#7A7985 (close-up); wood f34 #934819 → #9E5827 (the sheet's is fire-lit); iron f34 #353034 → #363131, front #353032 →
#3A393D; rope f34 #FBC08E → #F0C57D, junction detail #FBD389 → #FFD788. All within the recorded lighting differences;
the R1 rope and stone minors are fixed.

**Junction (R1 blocker), against the junction detail and its top view** (`verify/r2/j_f34_el25.png`, `j_r34.png`,
`j_side.png`, `j_top.png`): the bind is centred on the crossing, three round coils with one long diagonal per face;
the three tops stand 0.74 clear above it with end grain showing, an X of two tops plus the third in f34 and a
three-armed star from above, as the small top view draws. Fixer's departures, all accepted:
- one diagonal wrap per face instead of an X: closer to the sheet's loose crossing loops than the basket the X made;
- tops follow the poles' 31.7° lean (narrower splay than the drawing): a straight timber can't splay more;
- the back pole's top 0.25 off centre (twisted tripod): it still reads centred in r34;
- chain thickness: links 0.23 wide on a 0.035 wire are in proportion to the sheet's 2.0 pot.

### Minors (recorded, not blocking)

- **Chain hidden in the hero view.** It hangs on the centre line, which in f34 falls behind the front-left pole below
  the bind (`verify/r2/chain_f34.png`); it shows clearly in front (`junction_front_cu`) but not as the sheet's f34 and
  pot-hanging detail draw it. Optional: `LINK_R` 0.035 → 0.045 for a bolder chain where it does show (re-run kit_verify).
- **Bind edges:** from the side and rear the diagonals' turn-round loops stand a little proud of the coils
  (`j_r34`, `j_side`); they read as the sheet's loose loops at game distance.
- **Stones** are still somewhat rounder lumps than the sheet's boxy, flat-topped boulders, though better than R1.
- **Pole end grain** keeps the "+" of the seam grooves (R1 minor).
- **Logs** sparse under the pot (content-correct, R1 minor); the fire VFX covers the centre.
