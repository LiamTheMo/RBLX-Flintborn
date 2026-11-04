# 071 Supply Crate — spec

Reference: `art/blender/assets/references/071.png` ("SUPPLY CRATE / INDIVIDUAL MODEL STUDY", page 70/132).
Builder: `art/blender/kit/mcp/m071.py` → `build()`, on the shared library (`kit_parts` / `kit_build`). Procedure:
`art/blender/kit/mcp/STAGES.md`; standing answers: `HOUSE_RULES.md`. A new build: no earlier builder or spec.

## Brief

- **Sheet:** 071 Supply Crate (remake: no). Family: none.
- **Class and budget:** prop, ceiling 1000, plan 900–960 (built 956). The 20 bolt heads take 432 of it, which is
  what the sheet's defining iron corners cost at 22 / 20 tris each. Every part is far under 1000.
- **Size:** HOUSE_RULES crate 2.30, taken as the bracket tops (wood rails 2.26, flat top bolts to 2.33). The
  footprint comes from the orthographic cells: front, side and rear content are 188 × 165 px (W : H 1.14, shadows
  excluded), top 177 × 172 (square), so the plan is square and W = 1.14 × 2.33 = 2.65 with the side bolts. Hero bbox
  **2.65 × 2.65 × 2.33**. The same px/stud gives posts 0.40, rails 0.36, brackets 0.45 × 0.41, bolt dia 0.22, brace
  boards 0.30.
- **Hero view:** front three-quarter at az −40, el 22 (front face wider than the side, ratio 0.86; the el matches
  the cell's W : H 1.037 → ours 1.038). Front, side, rear, top: orthographic (az 0 / 90 / 180, el 0; top el 89.9).
  Rear three-quarter: a redraw of the hero (content only), compared at az 140.
- **Sheet conflict:** the side ortho draws the side as horizontal planks with no X brace; the hero (both visible
  sides), the rear three-quarter and the exploded "Side Panel (Frame + X Brace)" on both sides draw X braces. The hero
  governs: X braces on all four sides, with the side cell's horizontal planks kept as the backing behind them. The
  front and rear orthos' backing reads as vertical boards / blocks; the hero's as staggered blocks; the side cell's and
  the exploded core's as horizontal boards: horizontal boards (V seams) on all four, joints recorded as a miss.
- **Parts:**
  | Part | What | Tris |
  | --- | --- | --- |
  | BracedSupplyCrateFramePlank | Wooden Plank (Frame): one rail 1.66 × 0.40 × 0.36 | 12 |
  | BracedSupplyCratePanelPlank | Wooden Plank (Panel): one backing board 2.06 × 0.38 × 0.12, V-seam edges | 20 |
  | BracedSupplyCrateSidePanel | Side Panel (Frame + X Brace): the hero's front side with its posts, rails, braces, a backing slab, four brackets and face bolts | 360 |
  | BracedSupplyCrateTopPanel | Top / Bottom Panel (Planks): three planks on two cleats | 60 |
  | BracedSupplyCrateCornerBracket | Metal Corner Bracket (+ Bolt): foot bracket with two domed bolts | 56 |
- **Palette** (sheet swatches → rendered medians → `MODEL.calibrate`): swatches #AF6025 / #BE783A (oranges), #858484
  (iron), #FBD09B / #F2CF9F (creams). Keys: `m071_wood` frame, braces, planks (target the front cell's frame faces
  #CB7B31) → **#B0742F**, matte 0.85; `m071_wood_deep` backing (target #965522) → **#784B22**; top / bottom planks
  `wood × deep 40 %` (the top cell draws them a step darker than the rails); `m071_seam` #4E2712 in the V seams;
  `m071_iron` brackets (target #746B6F) → **#656068**, rough 0.6, metal 0.25; `m071_bolt` (target #6A6870) →
  **#61636F**, rough 0.5, metal 0.35. The two creams are the sheet's lit highlights and grain, not a separate material
  (no part of the crate is cream in any cell).
- **Lights / VFX:** none (no glow, smoke or effect in any cell).
- **Collision:** hero `hull` (a solid box players don't walk into; HOUSE_RULES "otherwise hull"); every part `box`.
- **Checks to switch on in kit_verify:** none beyond the defaults (`cls="prop"`); the builder's `crate_check`
  confirms the plan is square.
- **Departures from HOUSE_RULES:** none against the rules. Recorded choices: height 2.30 taken at the bracket tops
  (flat top bolts reach 2.33, as the top cell draws them); the footprint 2.65 square from the ortho cells' W : H
  rather than a 2.30 cube; the hero's X braces on the sides over the side cell's plain planks (hero governs).
- **Questions for the main session:** none.

## Stage 1 — Modelling

Build frame: front −Y, +X right, ground z 0, centred. Each side is built in a face frame (u along the face as seen from
outside, v = z, w = depth in from the frame face at ±1.21); `face(k)` for k = front, right, rear, left.
- **Frame:** four corner posts 0.40 square, **L section** (the inner corner notched to 1.01 so the backing seats 0.02
  into them without burying), z 0.02–2.27; eight rails 0.36 tall × 0.40 deep (the top cell's frame band) between the
  posts, seated 0.02: bottom 0.02–0.38, top 1.90–2.26. Wood starts 0.02 up: the iron brackets are the feet.
- **Backing (core):** one closed box, outer faces 0.18 behind the frame face (±1.03), z 0.37–1.91 (0.01 into the
  rails), its four faces cut into four horizontal boards by V seams at 0.76, 1.14, 1.52 (±0.03 wide, 0.035 deep,
  painted `m071_seam`): 84 tris for all four sides.
- **X braces** (front cell): parallelograms with horizontal ends seated 0.02 into the rails, their acute tips 0.01 into
  the posts at the opening's corners, 0.30 wide. Board A (continuous, bottom-left to top-right as seen from outside)
  at depth 0.04–0.14; board B the other way behind it at 0.12–0.20, 0.02 into A and the backing. From the front B
  reads as halved by A, as the sheet draws it, without a T-joint or interpenetration.
- **Top and bottom panels:** three planks along X (0.52 wide, 0.04 gaps, 0.16 thick) inside the top rails, tops 0.04
  under the rail tops; three more under the backing inside the bottom rails (the underside cell's bottom panel).
- **Corner brackets:** a 0.45 × 0.45 × 0.41 iron box on each of the 8 corners, 0.04 proud of the frame faces and over
  the rail tops, wrapping the post end and the rail ends; a domed hexagonal bolt (r 0.11, 0.04 proud, 0.035 dome,
  sunk 0.02) on both outer faces of every bracket (16), and a flat round bolt on top of the four top brackets (close-up
  and top cells).
- **Parts:** each built by the same piece functions as the hero (`rail`, `braces`, `post`, `bracket`,
  `top_planks`); the side panel uses the hero's corner posts and brackets, with a 0.12 backing slab (the core's face
  profile extruded across the side) in place of the core.

## Stage 2 — Optimisation and cleanup

kit_verify (`cls="prop"`), **0 problems**. Hero **956 / 1000** tris, 55 closed shells (core 84, rails 8 × 12, braces
8 × 12, posts 4 × 20, planks 6 × 12, brackets 8 × 12, bolts 432); 0 non-manifold edges, bowties, boundary, wire,
loose, zero-area faces, n-gons or duplicate verts; normals outward; 0 winding, parity, self-intersection or
negative-volume shells; min corner 30.0°. Origin at the bbox bottom centre (offset 0, 0, 0), transforms applied, no
modifiers or custom normals. Floating 0, unchained 0 (12 shells grounded: the brackets and bottom bolts); buried 0,
deepest 0.04 (core corner in a foot bracket), then 0.03 (rails, planks and posts in brackets), 0.028 (core in posts).
Parts, each 0 problems: FramePlank 12, PanelPlank 20, SidePanel 360 (2.65 × 0.53 × 2.30), TopPanel 60
(1.66 × 1.66 × 0.31), CornerBracket 56 (0.53 × 0.53 × 0.41).

## Stage 3 — UV

kit_build cleanup: angle-based unwrap, margin 0.008. Hero 356 islands, 0 overlaps or flips, min gap 0.016, border
0.008, density even, conformal stretch p95 1.08; all parts clean. The exporter writes its own palette UVs.

## Stage 4 — Materials and colour

Sheet medians with `K.sample` (brown / stone kinds): frame faces in the front cell #CB7B31 (posts #C0722F, rails
#CB7B31), backing between the braces #834C22–#A6712D (front cell; the hero's shaded side #572D0F), iron brackets #746B6F, bolts
#6C666B with blue-grey lights. `MODEL.calibrate` on the studio dome gave wood #A06930, deep #784B22, iron #656068,
bolt #61636F; wood was then raised to **#B0742F** after a class check of the compare renders: brown medians (sheet →
ours) front #BA6E2B → #C07528, top #BA6D2C → #C87A2E, f34 lit quartile #EB9644 → #DB8734. The side cell renders darker
(#AF6427 → #925A1E): the studio's key light is front-left and the sheet lights every face; recorded, not scored.
Colour by role and position only: backing deep with dark seam bands, top/bottom planks a 40 % mix toward deep (the top
cell's planks are darker than its rails), brace B 6 % darker than A. Per-piece Tint ±0.05 (iron ±0.02–0.03) and broad
mottling on the timber. Tint against normal: worst 0 (no material over 0.3). K.check clean.

## Stage 5 — Lighting

None: no emissive part or light in any cell. No Studio-side settings.

## Stage 6 — VFX

None: no glow, sparkle, dust or smoke in any cell. Export STATS: 0 sockets, no glow keys.

## Renders and compare

`build()` writes `art/blender/renders/models/M071/` (`M071_views.png`: f34, r34, front, side, rear, top, exploded,
scale with the 5.5-stud character; `build(close=True)` adds `under_cu`). `m071.compare()` writes the side-by-side
sheet to `<temp>/RBLX-Flintborn/compare/M071/M071_compare.png` (or `out_dir`). Content W : H (sheet / ours): f34
1.037 / 1.038, r34 1.014 / 1.049, front 1.186 / 1.119, side 1.180 / 1.119, rear 1.174 / 1.119, top 1.074 / 0.997 (the
sheet crops include the cast shadow on the left; without it front is 1.14 against our 1.12).

Known misses, recorded:
- Side cell: horizontal planks without an X brace (hero governs, see the Brief).
- Backing joints: horizontal boards only; the hero and front / rear orthos also draw vertical butt joints (blocks).
- Bolt heads are hexagonal domes (6 sides, the budget's limit at 20 heads); the sheet's are smooth round domes.
- Frame members are single blocks; the sheet paints each rail and post as two planks with a grain line, and draws
  small tabs at the middle of the top cell's left and right edges that no other cell shows.
- Studio light: side and rear faces read darker, the top bracket faces and top bolts lighter, than the sheet's.

## Stage 7 — verification (R1)

**Result: PASS, 7.5 / 10.** Fresh verifier, read-only, in a background session on the work-file copy
`wip/M071v.blend` (nothing rebuilt or saved). No blockers. The model reads as the sheet's crate in every cell: square
framed box, eight iron corner brackets with bolts on both faces, X braces over a recessed dark backing, three top
planks inside a raised rail frame. Verifier renders and the compare sheet are in `renders/models/M071/verify/`
(gitignored).

### Technical

- **kit_verify** (`cls="prop"`, hero and all five parts): **0 problems**.
  - Hero BracedSupplyCrate: **956 / 1000** tris (prop ceiling; 4 % headroom), 55 closed shells, 2.65 × 2.65 × 2.33,
    origin at the bottom centre (offset 0, 0, 0), transforms applied, no modifiers or custom normals.
  - 0 non-manifold edges, bowties, boundary, wire, loose, zero-area faces, n-gons or duplicate verts; normals outward;
    0 winding, parity, self-intersection or negative-volume shells; 0 register mismatches; min corner 30.0°.
  - Contact: floating 0, unchained 0, 12 grounded (foot brackets and their bolts). Buried 0, deepest 0.04 (core in a
    foot bracket), then 0.03 (rails, planks, posts in brackets), 0.028 (core in posts), all under 0.05.
  - UV: 356 islands, 0 overlaps or flips, gap 0.016, border 0.008, density even, conformal stretch p95 1.08. Tint
    against normal: worst 0. K.check clean. No sockets or glow keys, as the brief says.
  - Parts, each 0 problems: FramePlank 12 (1.66 × 0.40 × 0.36), PanelPlank 20 (2.06 × 0.12 × 0.38), SidePanel 360
    (2.65 × 0.53 × 2.30, min corner 5.7° at a brace tip), TopPanel 60 (1.66 × 1.66 × 0.31), CornerBracket 56
    (0.53 × 0.53 × 0.41).
- **Names and collision.** Hero and parts follow `<Hero><Part>`; `SupplyCrate` is taken (furnishings sheet, lobby,
  `art/roblox/lobby/meshes/SupplyCrate.glb`), so BracedSupplyCrate is right. Materials `m071_*`, collection
  `M071 Supply Crate`. Collision hero `hull`, parts `box`, as the house rules say for a prop nobody walks into.

### Views against the sheet (compare.py, content W : H sheet / ours)

- **f34 (1.037 / 1.038).** Same layout: front face wider than the side, near corner post and stacked brackets at
  the centre, X on both faces with the "/" board continuous, top planks recessed inside the rails. The sheet's braces
  sit a little closer to flush and its backing reads as staggered blocks; ours as horizontal boards.
- **r34 (1.014 / 1.049).** A redraw of the front, judged on content: matches.
- **Front (1.186 / 1.119; 1.14 without the sheet's cast shadow).** Rails, posts, X geometry (horizontal brace feet
  on the rails, tips into the post corners) and bracket height (0.17 of H both) match. The brackets read about 15 %
  wider than the sheet's (0.17 of W against 0.15, plus the side bolts showing as small ears at the outline).
- **Side (1.18 / 1.119).** The sheet's plain horizontal planks against our X brace: the hero, the rear
  three-quarter and the exploded "Side Panel (Frame + X Brace)" all brace the sides, so the hero governs (house
  rules). Recorded, not a blocker. Our side reads darker under the studio key light (recorded, not scored).
- **Rear (1.174 / 1.119).** Matches the front, as the sheet draws it.
- **Top (1.074 / 0.997).** Three planks inside the frame (the sheet draws three, each with a grain line), round
  bolts on the four top brackets (ours flat hex). The sheet's mid-edge tabs show in no other cell; omitting them is
  right. The sheet's extra width is the tabs.
- **Exploded / parts overview.** All five pieces present. Differences: the TopPanel adds two cleats the sheet doesn't
  draw (harmless, needed to make a standalone panel), and the PanelPlank is `wood_deep` where the parts cell paints it
  the same orange as the frame plank (it is the hero's backing board, which is dark there, so defensible).
- **Close-ups.** Corner bracket: a box wrapping the post end and rail ends with a bolt on each outer face and one on
  top, as the close-up cell. Plank join: our rails and posts are single blocks; the cell shows each rail as two stacked
  planks with a grain line. Underside: bottom planks inside the bottom rails, brackets as feet, as the cell.
- **Colour** (medians of orange pixels split into lit / mid / dark thirds, and the grey iron; sheet → ours):
  - front: lit #CD7E33 → #CC7C2B, mid #BA6F2B → #C27628, dark (backing) #693B19 → #7D471B, iron #6C6768 → #6B6366;
  - top: lit #D68335 → #E28C32, mid #B96D2B → #C8792D;
  - f34: lit #DF8A3B → #CC7D33, mid #A65F25 → #C07528, dark #603514 → #AB6824 (the sheet's painted shading and ink
    give it more contrast; studio lighting, recorded not scored);
  - side: #AF6427 → #925A1E (studio key light, recorded).
  Base colours sit within about 10 levels on the square-on front; the backing is a touch lighter than the sheet's.

### The modeller's choices

- BracedSupplyCrate name: correct (above).
- 2.65 square footprint × 2.30 tall rather than a cube: accepted. The ortho cells measure W : H 1.14 and the hero's
  W : H matches to 0.001; the house rules fix only the crate height (2.30), which is kept at the bracket tops.
- X braces on all four sides: accepted (hero governs over the side cell).
- Hex-dome bolts: accepted as the budget compromise (20 heads at 22 tris = 432); 8-sided heads would cost about
  160 more tris (1116) and break the 1000 ceiling. Minor.
- Backing with horizontal seams only: minor (the hero and front / rear orthos also draw vertical butt joints).
- Frame members as single blocks: minor.
- Top cell's mid-edge tabs omitted: accepted (no other cell shows them).

### Blockers

None.

### Minors (not required to ship)

1. Brackets about 15 % wider than the sheet's in the front ortho; a 0.40-wide face (`BR_IN = IN + 0.04`) would match
   the sheet, but it changes the bracket-to-post seating, so it is a fix-modeller change, not a ship-time one.
2. Bolt heads are faceted hex domes; the sheet's are smooth round domes (budget).
3. Backing reads as horizontal boards; the sheet's hero draws staggered blocks.
4. Rails and posts are single blocks; the sheet paints each as two planks with a grain line.
5. The f34 has less light-to-shade contrast than the painted sheet (studio lighting, not scored).
6. Text: the hero's `kit_notes` say "2.64 x 2.64 x 2.33" (measured 2.65 × 2.65 × 2.33), and the builder's module
   docstring and the CornerBracket note call the bolts "round domed" (they are hexagonal). One-line fixes at ship time.
