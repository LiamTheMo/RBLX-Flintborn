# 072 Timber Gate — spec

Reference: `art/blender/assets/references/072.png` ("TIMBER GATE / BUILDING MODEL STUDY", page 072, remade sheet).
Builder: `art/blender/kit/mcp/m072.py` → `build()`, on the shared library (`kit_parts` / `kit_build`). No earlier
builder or spec existed: this is a new build. Procedure: `art/blender/kit/mcp/STAGES.md`; standing answers:
`HOUSE_RULES.md`.

## Brief

- **Sheet:** 072 Timber Gate (remake: yes, first build). Family: none.
- **Class and budget:** structure (walk-through gate), ceiling 6000, plan 5450 (built 5448; the 10 % margin went to the
  sheet's rope bands over lintel and bolster). Every part under 1000. Large-model verification (one model per
  verifier, up to two rounds).
- **Size:** the front cell's R6 figure is 70 px = 5 studs → 14 px / stud (the same in the side and rear cells). From
  that: cap tops 11.08, lintel 8.22–9.66 and 16.6 long, bolster under it 7.40–8.24, leaves 4.2 wide and 7.3 tall (4
  planks each), posts' inner faces |x| 4.35 (opening 8.70), main post 1.70 square, banner 1.82 wide from 7.03 to tips
  2.30, lanterns 1.0 wide hanging 4.50–6.8, rock 2.5 × 1.8. Hero bbox **18.70 W × 4.87 D × 11.08 H**.
- **Hero view:** f34 (front three-quarter), compared at az −24, el 18. Front, side, rear: orthographic at az 0 / 90 /
  180. r34: the sheet's rear three-quarter is seen from back-left (near pillar on the image's right) → az −150, el 16.
  Side, rear, r34 and top are redraws: judged on content (they draw the rocks and lanterns at the same screen places
  in every cell, the hinge pins between the main and outer post in the rear cell, and lanterns on the pillar's side in
  the side cell).
- **Parts:**
  | Part | What | Tris |
  | --- | --- | --- |
  | TimberGate (hero) | the whole gate, closed | 5448 |
  | TimberGatePost | one pillar: main + outer post, bolster, rear rail, brace, collar, rail lashing | 638 |
  | TimberGateLintel | lintel, both cap blocks, the two inner wraps | 356 |
  | TimberGateLeafLeft / ...Right | planks, straps + bolts both faces, ring, keeper, hinge knuckles | 592 each |
  | TimberGateLatchBar | round drop bar with knobbed ends | 84 |
  | TimberGateRopeWrap | three-turn rope coil for a 1.70-square post | 360 |
  | TimberGateHinge | hinge block & pin: plate, two barrels, pin head | 72 |
  | TimberGateBanner | knobbed rod, hem sleeve, swallowtail, stripes, double diamond | 268 |
  | TimberGateLantern | dark iron lantern, Neon glass, ring and hook | 164 |
  | TimberGateRockBase | grey rock with two leaf clumps | 230 |
- **Palette** (sheet medians of the rendered cells, then `MODEL.calibrate`; swatches in brackets): timber #C26C21
  rendered [swatch #D47B2B] → `#9A5E21`; plank `#9A5F21`; dark timber [#85522F] `#6E4426`; cut ends `#C2843A`; iron
  straps #595D6A [#525867] → `#545866` (metal 0.4); lantern iron `#3A3C45`; glass #F9E03B → Neon `#F9D83A`; rope
  #F5C25F [#CBA06F] → `#C2A058`; banner #FD221B [#F3191A] → `#E81C1A`; cream emblem `#F2E6CF` (its calibration
  drifted pink, kept by hand); stone #9795A4 [#AFADB3] → `#797C8D`; foliage #89C60A [#81BE0B] → `#72A307`, lime
  `#8ABA0B`, dark `#3E6E04`. All matte (roughness 0.8–0.95) except the iron.
- **Lights / VFX:** four lanterns (the front cell) with Neon glass (emission 1.0) and a `heat_glow` socket each (the
  M064 / M068 halo); the Lantern part has one. No other light or effect on the sheet.
- **Collision:** hero precise; Lintel, both leaves box; Post, LatchBar, RockBase hull; RopeWrap, Hinge, Banner,
  Lantern none.
- **Checks switched on in kit_verify:** `cls="structure"`; `foliage` (5° sweep) on the hero and RockBase; sockets
  (4 / 1 `heat_glow`); stored `m072_hinges` (hero) and `m072_hinge` (leaves). The builder's `gate_check` builds the
  open variant (leaves swung 90° inward, no latch bar), runs kit_verify's `walk` through the opening (x 0, y −7 → 7)
  and measures the clear width between the open leaves and the headroom.
- **Rulings (main session) and departures from HOUSE_RULES:**
  - The hero is the closed gate (the sheet's hero). The leaves are also separate parts whose **origin is on the
    hinge-pin axis** (axis |x| 4.20, y 0.30, the leaf's bottom 0.10 up), so the game can swing them; the open state
    is a variant render (`open_sheet`) and the walk check, not a model. kit_verify and K.check flag those two origins
    ("origin not at the bottom centre", "origin is not centred on the footprint"); `build()` moves exactly these four
    messages into `out["waived"]`. The exporter's own check (lowest point at z 0) passes.
  - Leaves hang 0.10 off the ground and open inward (+Y) 90°; the hinge records (axis bottom, closed / open yaw) are
    stored on the hero (`m072_hinges`, relative to its origin) and the leaves (`m072_hinge`).
  - Leaf clumps at the rock bases (HOUSE_RULES: no ground scatter): kept, the sheet draws them as part of the rock
    base (main session's part list).
  - The rope collar at the main post's foot is three open runs round the front, outer post and back, both ends turned
    into the post: the leaf hangs 0.13 off the post's inner face, so a full turn would pass through it.
  - The latch bar rests in keepers on the leaves' backs (the sheet shows it only in the exploded view); hinge blocks
    on the main post's inner face (the rear cell draws the pins between main and outer post).
  - Outer lanterns at |x| 8.25 (sheet 8.2), bolster ends 8.80 (sheet 8.5), lintel ends 8.32: room for the end
    wraps between banner knob and lantern hook.
- **Questions for the main session:** a leafless frame for a working gate would be over 1000 tris, so it cannot be a
  part; if the game needs one, it would be a second hero (TimberGateFrame) or a Studio-side split.

## Stage 1 — Modelling

Build frame: front −Y (lanterns, banners), +X right, ground z 0, gate centred on x 0, mirror-symmetric (pillars
built with s = ±1). Every piece is its own closed shell, seated 0.002–0.05 into what holds it (no booleans).
- **Pillars:** main post 1.70 × 1.70 (|x| 4.35–6.05, chamfer 0.06) and outer post 1.60 × 1.05 (|x| 6.03–7.65, y
  −0.50…0.55, front face 0.35 behind the main post's, a shade darker) from the ground into the bolster's underside
  (sunk 0.02). The **bolster** is a deep block on both posts (|x| 4.00–8.80, y −1.92…0.85, z 7.40–8.24): it carries
  the lintel (sunk 0.02 into its top) and, at its front, the lanterns and banner. Rear rail (|x| 4.30–7.74, y
  0.83–1.45, z 6.00–6.80) on the posts' backs; the rear cell's diagonal brace (0.62 wide) on the outer post's back
  from (|x| 7.70, z 2.70) up to the main post's outer face at z 5.05, ends cut vertical.
- **Lintel** |x| ≤ 8.32, 1.30 deep, 8.22–9.66, pale end grain; cap blocks 1.75 square, 9.64–11.08 with a bevelled
  top, standing on the lintel over the main posts.
- **Rope** (r 0.15, twisted, inner strands sunk 0.02): wraps round the lintel over the opening (|x| 3.55) and round
  the bolster's ends (|x| 8.55); bands (r 0.19) strapped over lintel and bolster at |x| 7.0 (front, over the top,
  down the back) and |x| 5.2 (from under the cap down the front), ends turned 0.04 into the timber; three collar
  runs at 0.95 / 1.23 / 1.51; a C-run over the rear rail at the post's centre.
- **Leaves** (right leaf modelled, the left its mirror): four planks 1.03 × 0.30 (chamfer 0.06, 0.02 apart, tops
  7.33–7.42, bottoms 0.10); front straps 0.71 tall (z 5.25–5.96 and 1.45–2.16, x 0.76–3.40) with taller end plates
  near the hinge side (x 3.38–3.98) and 3 + 2 bolts; back straps from x 0.76 to the hinge axis (into the knuckle)
  with end plates and 3 bolts; ring handle (R 0.50, tube 0.10) at x 0.72, z 3.16 on a round boss; the latch keeper
  (plate, lip, upright) on the back; two hinge knuckles (6-sided, r 0.11, 0.72 tall) on the axis.
- **Hinge blocks** (two per leaf): an iron plate on the main post's inner face, barrels above and below the knuckle
  (0.004 gaps) on the axis, the pin's head on the top barrel. **Latch bar** r 0.14 across both keepers (z 3.83) with
  knobs.
- **Lanterns** (`P.lantern` w 1.0, glass 0.74 × 1.05) at |x| 5.10 and 8.25, y −1.45, base 4.50, on iron hooks sunk
  0.02 into the bolster. **Banner** (m069 recipe): rod r 0.13 with knobs, a dark hem sleeve seated 0.02 into the
  bolster, cloth |x| 5.80–7.62 (top 7.03, tips 2.30, notch 3.00), two cream edge stripes and the cream double diamond
  on the front.
- **Rock base:** m069's faceted boulder (2.5 × 1.9 × 1.8) at |x| 6.65, slid from the front until it meets the
  pillar (y −1.86), the lowest 0.35 a darker stone; two leaf clumps of six broad tent leaves (an 8-point oval
  outline in the builder, the ivy's tent rise 0.22) rising 38–70° radially from a small ring, alternating steep and
  low; a leaf that would sink > 0.04 into the rock, the posts or a placed leaf is pushed out radially or left out.

## Stage 2 — Optimisation and cleanup

kit_verify clean (problems list empty; the four ruled origin messages waived):
- Tris: hero 5448 / 6000; parts 638, 356, 592, 592, 84, 360, 72, 268, 164, 230 (all < 1000).
- 0 non-manifold edges, bowties, boundary / wire / loose, zero-area faces, n-gons, duplicate verts; 0 winding errors,
  0 inward faces, 0 self-intersections; thinnest corner 6.97° (hero); 0 floating / unchained shells; 0 buried
  (deepest 0.043); no pierced thin sheets; transforms applied, no modifiers or custom normals.
- 205 shells in the hero. Origins: bottom centre (hero and parts); the leaf parts on their hinge axis (ruling).

## Stage 3 — UV

`kit_build.cleanup` (angle-based unwrap, margin 0.008): kit_verify's UV check clean on every object (no overlaps,
flips; island gap and border met).

## Stage 4 — Materials and colour

Sheet medians sampled with `M.sample` on the rendered cells (front, f34, rear) and `M.raw_sample` on the swatches;
`MODEL.calibrate` on timber, plank, rope, banner, stone, leaf, lime, iron (values in the Brief and `PALETTE`). Colour
by role: plank tints alternate a step toward dark timber; outer post a shade darker; brace and cap bevels toward the
cut-end colour; rock foot a darker stone; per-piece Tint ±0.05 and broad mottling on planks, cloth and rock. Compare
renders read close to the sheet's warm orange-brown; the iron straps read a little darker than the sheet's on the
vertical faces (studio lighting).

## Stage 5 — Lighting

Lantern glass `m072_glow` at emission 1.0 (exports as Neon), four in the hero, one in the Lantern part. Studio side:
the `heat_glow` socket's PointLight (range 10, warm #FFB347, flicker) per lantern.

## Stage 6 — VFX

`heat_glow` sockets at each lantern's glass centre (|x| 5.10 / 8.25, y −1.45, z 5.175) with the steady halo override
(M064 / M068); the export stats report 4 sockets on the hero and 1 on the Lantern. Nothing else on the sheet.

## Checks

- `gate_check` (open variant): walk x 0 from y −7 to 7 — min clearance 2.46, 0 intersecting steps, headroom 8.22;
  open clear width between the leaves 7.20–7.50 (≥ 3.6); headroom 8.22 under the lintel, 7.95 at |x| 3.6, 7.40 at
  |x| 4.1 (bolster ends, ≥ 6.9).
- Foliage sweep (5°, el 0 / 5 / 10 / 20): worst whole-leaf edge-on 0.0 % (hero, 23 leaves; RockBase, 12 leaves).
- Sockets 4 + 1 `heat_glow`; stored hinge records present.

## Renders and compare

`M072_views.png` (f34, r34, front, side, rear, top, the open state, exploded, scale) and close-ups (`hinge_cu`,
`pillar_cu`, `joint_cu`, `foliage_cu`; `build(close=True)`). `m072.compare()` writes the compare sheet to
`<temp>/RBLX-Flintborn/compare/M072/`. Content W : H, sheet / ours: f34 1.436 / 1.308, r34 1.246 / 1.304, front
1.553 / 1.669, side 0.429 / 0.434, rear 1.465 / 1.653, top 3.10 / 3.82 (ours wider in front and rear: our leaf
clumps reach |x| 9.35, the sheet's 9.1; the rear cell draws no lanterns).

Known minors: the sheet's banner rod shows its knobs and rope ties below the beam (ours sits up under the bolster,
no ties); its ring handles are heavier; the sheet's pillar top is layered from more blocks than lintel, bolster and
cap; its leaf clumps are fuller; the rear cell draws rocks and foliage behind the gate and hinge pins between the
posts (redraw).

## Rulings (main session, 2026-11-04)

- **Frame without leaves:** no second hero. TimberGate is the static closed gate. A working gate is assembled in
  Studio from the exported parts (two Posts, Lintel, RopeWrap, Hinge, LeafLeft/LeafRight swung about their origins,
  Banner, Lantern, RockBase). The leaf origins on the hinge axis and the four waived origin messages stand.
- **Departures in the brief are accepted** (bolster block, tucked rope runs, latch keepers on the leaf backs, hinges
  on the posts' inner faces, 0.10 ground gap, leaf clumps kept as part of the rock base, outer lantern spacing).

## Stage 7 — verification (R1)

**Result: PASS, 7.5 / 10.** Fresh verifier, read-only, in a background session on the work-file copy
`wip/M072v.blend` (nothing rebuilt or saved). No blockers. The model reads as the sheet's gate in every cell: two
pillars with cap blocks under a long lintel, rope bands over the pillar tops, two four-plank leaves with iron straps,
end plates, bolts and ring handles, a red swallowtail banner with the cream double diamond between two lanterns on each
pillar, rope collars and a grey rock with leaf clumps at each pillar's foot. Verifier renders and the compare sheet
are in `renders/models/M072/verify/` (gitignored).

### Technical

- **kit_verify** (the builder's `VERIFY`: `cls="structure"`, foliage sweep on hero and RockBase, sockets, stored
  hinges; hero and all ten parts): **0 problems** after the four ruled leaf-origin messages (waived, hinge-axis
  origins).
  - Hero TimberGate **5448 / 6000** tris, 205 shells, 18.70 × 4.87 × 11.08, origin bottom centre. Parts: Post 638,
    Lintel 356, LeafLeft / LeafRight 592 each, LatchBar 84, RopeWrap 360, Hinge 72, Banner 268, Lantern 164,
    RockBase 230 (all < 1000).
  - 0 non-manifold, bowties, boundary / wire / loose, zero-area faces, n-gons, duplicate verts; 0 winding / parity /
    self-intersection shells; floating 0, unchained 0, buried 0 (deepest 0.043, leaf hardware); min corner 6.97°.
    UV clean on every object.
  - Foliage 5° sweep: worst whole-leaf edge-on 0.0 % at el 0 / 5 / 10 / 20 (hero 23 leaves, RockBase 12).
  - Sockets: 4 `heat_glow` on the hero, 1 on the Lantern; `m072_hinges` / `m072_hinge` stored.
- **gate_check** (open variant, leaves 90° inward): walk x 0, y −7 → 7, min clearance 2.46, 0 intersecting steps,
  headroom 8.22; open clear width 7.20–7.50; headroom 7.95 at |x| 3.6, 7.40 at |x| 4.1 (≥ 6.9). The open variant also
  runs clean through kit_verify (0 buried, 0 floating; only "no UV layer", expected for a variant).
- **Scale.** Sheet front cell: figure 71 px = 5 studs (14.2 px / stud); gate 251 × 161 px = 17.7 × 11.3 studs against
  ours 18.7 × 11.08 (the extra width is the leaf clumps, |x| 9.35 against about 8.6). Measured on the front pair, in
  studs sheet / ours: cap top 11.2 / 11.08, lintel 8.46–9.85 / 8.22–9.66, leaf tops 7.6 / 7.42, opening about 8.6 /
  8.70, lantern bottom 4.7 / 4.50, banner tips 2.5 / 2.30, outer lantern edge 8.7 / 8.75, ring centre 3.4 / 3.16.
- **Names and collision.** Hero and parts `TimberGate<Part>`, materials `m072_*`; collision hero precise, Lintel and
  leaves box, Post / LatchBar / RockBase hull, the rest none, as the brief.

### Views against the sheet (compare.py, content W : H sheet / ours)

- **f34 (1.435 / 1.318).** Same layout and part placement. The sheet's pillar tops are layered from more blocks and
  carry the banner rod on a rope-tied stub; ours are cap, lintel and one deep bolster (ruled). The sheet's plank tops
  are visibly stepped; ours nearly level (minor 4). Rings heavier on the sheet (minor 2).
- **Front (1.554 / 1.671).** Matches in every height above; the W : H gap is the leaf clumps and our wider bolster
  ends (ruled).
- **r34 (1.243 / 1.298) and rear (1.459 / 1.645).** Redraws, judged on content. Rear rail, rope collars, back straps
  with end plates, hinge plates, latch bar and brace are all present. The sheet's diagonal brace is a chunky strut
  standing well proud of the posts; ours is 0.03 proud of the main post's back and almost disappears (minor 1). The
  sheet's gold "+" lashing on the rail reads as a thin C-run on ours. The sheet draws no lanterns, and rocks behind
  the gate (redraw).
- **Side (0.432 / 0.430).** Content matches: pillar, lantern hanging forward from the bolster, banner edge, rock in
  front, collar.
- **Top (3.102 / 3.828).** Caps, lintel, bolsters with rope bands, rocks and clumps at the front. The sheet's top cell
  is drawn with some tilt and shows the leaves; ours hides them under the lintel (redraw).
- **Exploded.** All sheet parts present (two posts → one Post part, lintel with caps, both leaves, latch bar, rope
  wrap, hinge block and pin, banner, lantern, rock base). The RopeWrap is a squared coil for the 1.70 post where the
  sheet draws a round coil: consistent with the post, accepted.
- **Hinge close-up.** Plate on the post, barrels and pin head on the axis, the leaf's strap into the knuckle, as the
  cell; the sheet's barrel is far chunkier than our r 0.11 six-sided knuckle (minor 5).
- **Gate states.** Closed is the hero; the open render swings both leaves inward with ring and straps facing the
  opening, as ruled.
- **Post joinery.** Cap on the lintel over the post, rope over the junction. The sheet's cell wraps a thick
  multi-turn coil; ours are single bands r 0.19 that read as twisted rope (not plates), but thinner than the cell.
- **Lanterns, banner, rock.** Lanterns: dark iron frame, Neon glass, ring and hook, socket at the glass centre.
  Banner: sleeve, swallowtail, edge stripes, double diamond; the rod's knobs and ties aren't visible (known minor).
  Rock: faceted grey, darker foot, about the sheet's size; clumps sparser than the sheet's.
- **Colour** (medians by hue class, sheet → ours; f34 / front):
  - timber #B9661E → #A75D1C / #BB6821 → #A75D1C (ours about 10 % darker; rear #BD6A22 → #99571B in studio shade);
  - rope #FCC360 → #EEBC5C; iron #565968 → #4A4B54 (front #565A68 → #54555E); banner #FA1816 → #FF1915;
  - stone #9594A3 → #8E8D9B; glass #FCDD3D → #FFE833; foliage #97D012 → #83B40D (front in shade #658B0C).

### Blockers

None.

### Minors (each with a measured fix)

1. **Rear brace barely reads.** `BRACE["y"]` (0.53, 0.88) puts its back 0.03 proud of the main post's back (0.85).
   Fix: `BRACE["y"] = (OP[3] - 0.02, 1.20)` (0.35 proud); its top (z ≤ 5.45) stays clear of the rear rail (z 6.00).
2. **Ring handles thin and octagonal** (outer 0.60, tube 0.10, 8 segments; sheet about 0.75 and 0.15). Fix:
   `RING = dict(x=0.80, z=3.16, R=0.52, r=0.14)` and 12 segments in `leaf_geo` (both `/ 8` and `range(8)`); spans x
   0.14–1.46, boss at z 3.93, about +32 tris per ring (hero about 5512).
3. **Timber about 10 % darker than the sheet's rendered timber.** Optional: lift `TIMBER` / `PLANK` one step (about
   `#A86826`) and re-run `MODEL.calibrate`.
4. **Plank tops nearly level, and the outer plank touches the bolster.** Tops 7.33–7.42 (0.09 stagger); the
   outermost plank's top (7.40) is flush with the bolster's underside (7.40) over x 4.00–4.22, zero clearance for a
   swinging leaf in Studio. Fix: `PL_TOPS = (7.34, 7.48, 7.24, 7.30)` (0.24 stagger, 0.10 under the bolster).
5. Hinge knuckles slimmer than the close-up's barrel; sheet's rear "+" rail lashing a thin C-run; banner rod knobs and
   ties hidden; leaf clumps sparser; pillar top layered less than the sheet (the last three already recorded).
