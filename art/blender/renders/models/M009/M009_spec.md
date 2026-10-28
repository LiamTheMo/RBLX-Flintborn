# 009 Iron Meteor — spec

Reworked at the user's request: cracks lacked depth.

User verdict (2026-10-28): "#09 iron meteor needs a rework, the crackes on the rock are not apparent and has no depth."
General direction for every model: colours "need to match the master reference and blend into the colors nearby. please
ensure all color and textures are being made and applied."

Reference: `art/blender/assets/references/009.png` (IRON METEOR, page 13, 1024 × 1536). Builder:
`art/blender/kit/mcp/m009.py` → `build()`. Procedure: `art/blender/kit/mcp/STAGES.md`, all seven stages, from scratch.
Model of a full stage run: `m011.py` and `M011_spec.md` (part builders, `_paste` into a shared build frame, self-union,
`_Paint` colour pass, `STUDIO_LIGHT`, `_vfx`).

Assets (collection `Kit/M009 Iron Meteor`). The names stay as before, because a kit sheet already owns `IronMeteor`:

- `IronMeteorDeposit` (hero).
- `IronMeteorShellPiece` (the reusable Rock Shell Piece).
- `IronMeteorCore` (Metal Core).
- `IronMeteorImpactRock` (Impact Rock, reusable).

Scratch study material (crops, sampler, crack scanner; pure Python, no Blender):
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m009_study\`.
It holds `png.py` (`crop`, `sample`), `measure.py` (orange-run scan per view; it prints crack position and width per
height row) and `mine.py` (the same scan on our renders). The crops there are `hero34.png`, `front.png`, `side.png`,
`rear.png`, `top.png`, `rear34.png`, `exploded.png`, `junction.png`, `shellpiece.png`, `thickness.png`, `xsec_zoom.png`
and `underside.png`.

## Why the old cracks read flat (diagnosis of the previous build)

Seen on `M009_views.png` and measured with `mine.py`:

1. **Painted stripes, not openings.** The cracks were boolean V-grooves (0.5 wide, 0.8 deep) carved into one solid convex
   hull. Both groove walls took the same emissive orange (`m009_core`, emission 1.5), so they render as one flat tone.
   - The crack pixels in `front34` span `#FF8236`–`#FFA149`, a range of about 30 levels.
   - On the sheet the same pixels run from a dark lip `#4E2B2A` through orange `#E34515` to a hot core `#FDBD40`.
   - With no dark lip, no shaded wall and no hotter floor, nothing tells the eye there is a hole.
2. **No shell, no core in the hero.** `hero()` was two convex hulls plus rocks. The shell was not hollow, the core part
   was never placed in the hero, and the shell pieces were not used. So the cracks open onto nothing, and the hero
   breaks STAGES ("assemble the hero strictly from those parts").
3. **The cracks sit in the middle of the balls, not on piece boundaries.** On the sheet the main crack is the seam where
   the front-left lobe piece meets the main mass. It makes a step and a notch in the silhouette. Ours ran across the
   lobe's own face and across the main's front face, and the silhouette stayed a smooth ball.
4. **A regular zigzag of even width.** The polylines alternated left and right every segment, with a constant 0.5 width.
   They read as a drawn lightning bolt, with "T" stubs where the overlapping segment wedges met (visible in `top`).
   The sheet's cracks are 2–4 long runs with 1–3 sharp jogs, widest at the jogs, and they taper to nothing at their ends.
5. **Too much orange.** The orange share of the dark meteor pixels was 4.7–13.1 % in our views, against 2.3–3.7 % on the
   sheet. There were too many cracks and they were too wide, yet none of them had depth.
6. **Wrong proportions and colours around them.**
   - The meteor was squat: 5.9 tall over 8.9 wide (W:H 1.5). The sheet is about 1.3.
   - The shell rendered too light and too even: `#6F676C`, with its dark quartile at `#665E63`. The sheet is `#5C575C`,
     dark `#3C383B`.
   - The rim rocks rendered peach. `front34` rocks were `#D8C0AA` and the rear rocks `#84746A`, against `#A18A7D` on the
     sheet. The `heat_glow` light sat inside the meteor and lit the whole ring orange.

## Study (2a)

- **Classification:** full asset (resource node: meteorite deposit). Budget is 4000 tris for the hero and 1000 for each
  part.
- **Size target:** about 12.0 W × 11.4 D × 7.4 H studs over the rim rocks.
  - The meteor group (main plus lobe) is about 9.7 W × 8.5 D × 7.4 H. Height is about 1.35× the 5.5-stud character.
  - Sheet ratios: front view group W:H is about 1.27–1.4; side view about 1.17; the top view is nearly round (W:D about
    1.14). The rim rocks reach about 1.2–1.4× the meteor's width in the top view.
  - The old build was 11.8 × 11.0 × 5.9, too low.
- **Silhouette.**
  - A big dark faceted meteorite, nearly as tall as wide, with broad flat facets of about 40–50 on the visible
    hemisphere.
  - A smaller lobe is fused at the front left. It is one of the shell pieces. Its top is at about 0.63–0.70 of the
    meteor height, and it bulges out of the main mass with a clear step and notch at the seam.
  - Seams glow orange between the pieces. In every view exactly two cracks show, one in each half of the view.
  - A ring of pale faceted impact rocks hugs the foot. They cover the bottom 15–30 % of the meteor in the side views,
    and the biggest is at the front right.
  - The top of the meteor shows no crack.
- **Parts (exploded construction):**
  - **Rock Shell Piece**, 4–5 main pieces. The exploded view shows 5:
    - a chunky rounded piece (upper left);
    - a flattish top cap with an orange edge at one end (top centre);
    - a lower-left piece with a crack edge;
    - a big right piece;
    - a tall sliver piece behind it.
  - **Metal Core**, the central element. A faceted ball of about 20–30 broad facets, bright orange with a hot
    yellow-orange highlight patch.
  - **Impact Rim**, multiple rocks. The exploded view shows 13 (10 rocks and 3 small stones).
- **Shell Piece Detail:** each piece is a thick curved shell segment. The outside is dark rock; the inside (the hollow
  side) is orange "Inner Face (Metal Core)"; the cut ends show the shell thickness.
- **Shell Junction Close-up:** the seam is a real gap between Rock Shell A and Rock Shell B that reveals the core.
  - The gap floor is hot (`#FD911C`–`#FDAC22`); the walls are orange (`#F14E0D`–`#F75610`) going dark (`#743220`,
    `#4E2B2A`) up at the lips.
  - Shell B sits at a different height from A, and B's thickness wall shows as a dark face along the gap.
  - The gap is jagged: long straight runs with sharp jogs. Its width varies and is widest at the jogs.
- **Shell Thickness (cross-section):** a solid shell wall of constant thickness, about 5–6 % of the piece's width,
  following the outer facets. The cut face is the medium-grey "Metal Core / Inner Faces" swatch (`#877E7C`, renders
  about `#A39A93`). The inner surface is orange and lies directly on the core.
- **Underside view:** the shell is open at the bottom. The core's flat underside is a large orange disc, about 0.4 of the
  rock ring's width, ringed by the dark shell and tightly surrounded by about 12 impact rocks.
- **Impact Rock Detail:** a squat faceted stone with broad flat facets, about 30–40 tris, flat-bottomed, pale warm grey.
- **Effects:** the cracks and core glow (emissive). No particles, smoke or bloom are drawn. Heat shimmer and a few
  embers from the cracks are implied (see Stage 6).
- **Finish:** matte rock (roughness about 0.85–0.92); the core is emissive. Modelling notes say "simple solid colours,
  no textures or noise". The user's later direction (rich colour regions plus broad Tint mottling, never confetti) wins
  over that note. Keep the mottling broad and subtle.

### Crack positions and widths per view (measured on the sheet with `measure.py`)

- x is the fraction of the meteor's dark bounding box from the image's left edge.
- h is the fraction of the meteor's height above the ground (in `top`, the fraction from the image's bottom, which is
  the front).
- Widths are visible-orange pixels per row, and the % is of the dark bounding-box width.
- "Orange share" is orange pixels as a share of the dark meteor pixels.

| View (`M.views` az, el) | Crack A (top → bottom), widest | Crack B (top → bottom), widest | Orange share |
| --- | --- | --- | --- |
| front34 (−28, 12) | (0.33, h0.68) → (0.38, h0.55) → (0.47, h0.45) → (0.48, h0.30) → (0.55, h0.15) into the rocks. Widest 3.5 % at h0.55 and 5 % at h0.26 (lower jog). | (0.85, h0.79) → (0.82, h0.72) → (0.80, h0.44), fades out. Widest 3 % at h0.70. | 3.6 % |
| rear34 (152, 12) | (0.22, h0.63) → (0.19, h0.56) → (0.30, h0.33). Widest 2.9 %. | (0.91, h0.65) → (0.86, h0.45) → (0.79, h0.28). Widest 3.2 %. | 2.3 % |
| front (0, 4) | (0.24, h0.63) → (0.34, h0.48) → (0.41, h0.24) → (0.49, h0.14). Widest 4.6 % and 5.5 % (at h0.24). | (0.80, h0.76) → (0.81, h0.56) → (0.79, h0.42), fades out. Widest 4 %. | 3.7 % |
| side (90, 4) | (0.33, h0.69) → (0.36, h0.58) → (0.49, h0.22). Widest 4.4 %. | (0.86, h0.69) → (0.83, h0.53) → (0.77, h0.33). Widest 2.9 %. | 3.6 % |
| rear (180, 4) | (0.22, h0.68) → (0.25, h0.55) → (0.32, h0.42). Widest 5 %. | (0.81, h0.68) → (0.84, h0.58) → (0.77, h0.21). Widest 3.7 %. | 2.4 % |
| top (0, 89) | (0.19, 0.50) → (0.24, 0.38) → (0.37, 0.20). Widest 3.8 %. | (0.87, 0.63) → (0.82, 0.48) → (0.78, 0.28). Widest 3.8 %. Nothing on the back half or the crown. | 2.3 % |

- Every view shows two cracks, each running from the upper shoulder (h about 0.63–0.79) down and slightly inward.
- In absolute terms, on the 9.7-stud group, the visible orange is typically 0.15–0.35 studs wide (1.5–3.5 %), with
  peaks of 0.45–0.55 at jogs and low on the lobe seam.

### Colours (sampled on the sheet, true sRGB; boxes are x0, y0, x1, y1 from the top left of the 1024 × 1536 sheet)

| Region | Box | Kind | Median | Dark / light quartile |
| --- | --- | --- | --- | --- |
| Swatch "Rock Shell" | (845, 145, 880, 180) | raw | `#3E3C41` | — |
| Swatch "Metal Core (Inner Faces)" | (845, 211, 880, 246) | raw | `#877E7C` | — |
| Swatch "Impact Rock" | (845, 277, 880, 312) | raw | `#AD998E` | — |
| Swatch "Crack / Core" | (845, 343, 880, 378) | raw | `#F55E21` | — |
| Shell, whole hero (rendered) | (100, 140, 470, 395) | stone | `#5C575C` | `#3C383B` / `#9C8986` (rim highlights) |
| Shell, front, side and rear views | (60,505,230,610), (300,510,480,610), (540,505,730,610) | stone | `#5E575B`, `#5B575D`, `#5A555B` | `#474040`–`#444044` / `#817476` |
| Shell top facets (hero) | (200, 150, 330, 215) | stone | `#68646D` | `#51515A` / `#7E757B` |
| Shell main front face (hero) | (300, 230, 420, 320) | stone | `#514C4E` | `#474143` / `#5B5457` |
| Shell top view | (820, 520, 950, 640) | stone | `#524E53` | `#3E3C3E` / `#797176` |
| Crack, hero lobe seam | (180, 220, 290, 375) | vivid | `#E34515` | `#532B26` / `#FC8917` |
| Crack, hero right seam | (380, 190, 420, 300) | vivid | `#E85221` | `#6A3028` / `#FDBD40` |
| Crack, upper lobe run (hero) | (150, 215, 215, 260) | vivid | `#743220` (ember) | `#4E2B2A` (lip) / `#F75610` |
| Crack, lower lobe run (hero) | (250, 300, 300, 375) | vivid | `#F14E0D` | `#4C1A14` / `#FD770E` |
| Junction close-up, gap floor | (820, 1000, 860, 1060) | vivid | `#FD911C` (hot) | `#FA580D` / `#FDAC22` |
| Junction close-up, whole crack | (790, 955, 880, 1125) | vivid | `#F76119` | `#913D2A` / `#FD981D` |
| Core (exploded) | (330, 860, 450, 980) | vivid | `#FA601D` | `#CD3F18` / `#FDAE4F` |
| Core underside | (130, 1240, 215, 1300) | vivid | `#E54A18` | `#B13014` / `#F1571C` |
| Shell piece inner face | (775, 800, 860, 890) | vivid | `#BB3813` | `#A0290E` / `#D74417` |
| Cross-section inner surface | (760, 1240, 840, 1320) | vivid | `#A32A13` | `#872011` / `#E34E14` |
| Cross-section cut wall (shell thickness) | (846, 1240, 856, 1290) | all | about `#A39A93` lit (strip is mixed: `#A4887C`) | — |
| Impact rocks, hero front | (340, 330, 470, 405) | stone | `#A18A7D` | `#625655` / `#C6AEA0` |
| Impact rocks, front view | (25, 615, 250, 660) | stone | `#877974` | `#3A3535` / `#C6B0A4` |
| Impact rocks, exploded | (200, 1030, 600, 1130) | stone | `#A49086` | `#6C5E59` / `#D1BFB3` |
| Impact Rock Detail | (420, 1200, 570, 1330) | stone | `#A28D85` | `#7B6E68` / `#D1BDB2` |

### Conflicts and how they are resolved

- **The "Metal Core" swatch is medium grey, but the core is orange in every view.**
  - The swatch's own label is "Inner Faces", and the cross-section paints the shell's cut wall that grey.
  - So the core and the inner surface are orange (`Crack / Core`), and the grey is the shell-thickness cut face. It
    shows on the floor ring under the shell and on the part's non-seam cut ends.
- **The top view shows two cracks and none on the back half; the rear and side views show two each.**
  - Four meridian seams are used (front-left lobe seam, front-right, back-right, back-left).
  - The two back seams stop lower (their tops at elevation about 25–30°), so from above they sit near the limb and
    barely read.
- **The cross-section calls the shell "thin" (about 5–6 % of the piece's width, about 0.35 studs).**
  - The user's complaint is depth, so thickness T is 0.6 (allowed 0.5–0.7).
  - This is recorded as an interpretation in favour of the user.
- **The modelling notes say "no textures or noise".** The user's later direction (Tint mottling, blended regions) wins.
  Keep it broad.

## Rework plan

### Stage 1: Modelling (from scratch, in the m011 style)

Shared build frame: studs, front is −Y, ground z = 0. Spherical directions are measured about the main centre with
`_dir(az, el)`, where az −90 is the front, az 0 is +X (right), az 90 is the back and az 180 is the left. Write the 2a
study above into the spec first, then build each exploded part with its own function, check it against its cell, and
paste the hero from the finished part meshes (m011 `_paste` / `_frame` / `m011_offset` pattern). End with one exact
self-union and the floor cut.

**Masses (starting values; tune to the views):**

- **Main.** Centre (0.4, 0.5, 3.2), radii (4.1, 3.8, 4.2). That gives a top at about 7.4 and a floor circle of radius
  about 2.7.
  - Use a Fibonacci cloud of about 48 points with a 0.93–1.05 radial wobble (the old `_cloud`) and take its convex hull.
    That gives the outer facets: broad and flat.
- **Lobe.** Centre about (−2.9, −1.9, 2.2), radii about (2.3, 2.1, 2.3), so its top is at about 4.5 (0.61 of H).
  - Use its own cloud of about 26 points.
  - It bulges about 1.0–1.3 out of the main's surface at the front left.
- **Core hull C.** The main's own cloud scaled about the main centre so that every point lies T = 0.6 inside the outer
  hull along its ray (radius ρ − T). Its facets then run parallel to the shell's and the thickness stays constant.
  About 22–30 hull points are enough for the core part; the hero only ever sees it in the gaps and on the floor disc.

**Seam network.** Seams are polylines of nodes `(az, el, G)` on the main's sphere. G is the lip-to-lip surface gap in
studs; G < 0 means the two pieces overlap by |G| there (a closed seam that fuses in the union).

| Seam | Between | Path (az, el), top → bottom (starting values) | G profile |
| --- | --- | --- | --- |
| **Lobe seam, upper run** (part of the crown boundary) | Crown / Lobe | (−178, 32) → (−160, 30) → (−142, 27) → (−126, 24) | −0.1 at the far left end, rising over about 1 stud to 0.30, then 0.35 |
| **Lobe seam, descent** | Front / Lobe | (−126, 24) → (−116, 16) → (−108, 9), jog → (−100, 4) → (−104, −8) → (−101, −30), below ground | 0.40 at the corner, **0.55** at the jog, 0.40, **0.55** low (front34 h0.26), open into the ground |
| **Front-right seam** | Front / Right | (−46, 50) → (−50, 38) → (−56, 24), jog → (−49, 15) → (−57, 2) → (−60, −10) | −0.1 at the top (fuses into the crown), 0.30, **0.45** at the jog, 0.35, tapering to −0.1 over the last 1.2 studs (fades at front-view h0.42) |
| **Back-right seam** | Right / Back | (40, 28) → (36, 16), jog → (44, 6) → (38, −6) → (42, −30) | −0.1 at the top, 0.30, **0.40**, 0.30, open into the ground |
| **Back-left seam** | Back / Lobe | (150, 30) → (146, 18) → (154, 8), jog → (148, −4) → (152, −30) | −0.1 at the top, 0.30, **0.40**, 0.35, open into the ground |
| **Crown ring** (everything else) | Crown / each flank | Jagged ring at el 48–56° (8–10 nodes, ±4° jitter), dipping to meet the lobe seam's upper run | **−0.1 (closed) everywhere.** The sheet shows no crack on top. |

- Paths are starting values only. Tune them until every view's cracks land within about ±0.07 (x) and ±0.08 (h) of the
  table in 2a, with the same count (2 per view).
- Each open run is 2–4 long straight runs with 1–3 sharp jogs of 8–15° az. No alternating zigzag, and no stubs.

**Shell pieces (5).** Each is a thick shell segment cut to its sector.

- Pieces and their azimuth spans (main centre):
  - `Crown`: everything above the crown ring.
  - `Lobe`: front left, about 150 → 180 → −100, carrying the lobe bulge. The lobe's own centre is at az about −144.
  - `Front`: a narrow piece, about −100 → −52, roughly 50° wide.
  - `Right`: about −52 → 40.
  - `Back`: about 40 → 150.
- In the exploded render: the top cap is Crown, the chunky rounded piece is Lobe, the lower-left cracked piece is Right,
  the big right piece is Back and the tall sliver is Front.
- **Recommended construction: sector cones.**
  - Each piece's boundary is a closed loop on the sphere made from its seams. Every seam is offset toward the piece by
    G/2 at the outer surface. A closed seam (G < 0) is offset away from the piece by 0.05, so neighbours overlap by 0.1.
  - The cone is star-shaped from the main centre: the apex at the centre, then rings at increasing radius along each
    loop direction. Rings are set relative to the local outer radius ρ(d) (a ray to the outer hull):

    | Ring | Radius | Half-width offset |
    | --- | --- | --- |
    | Deep | ρ − T − 0.4 (inside the core) | g/2 |
    | Wall band 1 (floor side) | ρ − 0.55T | lerp(g, G) |
    | Wall band 2 | ρ − 0.25T | lerp(g, G) |
    | Lip chamfer | ρ − 0.12 | G/2 + 0.08, on ONE side of each open seam only (the side that is to read "lower") |
    | Outside | ρ + 0.8 | G/2 |

    Here g = 0.55 G, so the walls splay outward and are visible from oblique views.
  - piece = (outer hull ∩ cone) − (C scaled 0.05 smaller about the main centre).
    - Use an exact boolean. `M.carve` with an INTERSECT option is a one-argument generic change in `kit_models.py`;
      record it.
    - The piece's hollow is then 0.05 smaller than the core. The overlap lets the hero's union swallow every inner face.
  - **Lobe piece:** use (main outer hull ∪ lobe outer hull) ∩ cone_Lobe − C_shrunk. The lobe bulge belongs to this one
    piece, and the lobe seam runs along the crease where the lobe meets the main, so it gives the silhouette step and
    notch.
  - Each piece's open-seam walls get 3 face rows through the thickness: lip band (0–0.25T), mid band (0.25–0.55T) and
    floor band (0.55T–T). Stage 4 grades these bands. Keep the extra cone rings even if stage 2 is tempted to dissolve
    them.
- **Alternative if the cone intersect proves fragile:**
  - Build one hollow shell (outer hull − C_shrunk).
  - Cut the open seams with flared wedge cutters: per segment a convex hull with the same 5 rings, from ρ + 0.8 down to
    ρ − T − 0.4, overlapping 0.12 at joints. Taper the ends by shrinking G along the last segment. Do not leave stubs.
  - Make the parts by also cutting the closed seams with a 0.03 hairline and running `split_loose`.
  - Then the hero is not a strict paste. Record why if this route is taken.
- **Shell thickness check:** on every piece, a ray probe through the outer surface must find the inner surface at
  0.6 ± 0.05 everywhere except the lobe bulge. The bulge is thicker, and solid down to the core.

**Core (`IronMeteorCore`).** It is C itself. Only its gap-floor strips and the floor disc survive in the hero.

- The part shows the whole faceted ball (about 40–60 tris) at origin. Size it as the sheet's exploded core, about 0.45
  of the meteor's width.

**Impact Rock (`IronMeteorImpactRock`) and the rim.**

- The part is a squat `K.hull_rock` with `keep_bottom=True`: about 2.2 × 1.9 × 1.4, rings like the old `ROCK_RINGS`,
  about 30–40 tris, flat facets.
- In the hero, use about 12 transformed copies hugging the foot, plus 3–4 small stones. Vary them with non-uniform
  scale 0.6–1.35 per axis, a z-turn and mirroring.
  - Sizes 1.6–3.0 wide and 1.0–2.1 tall. The biggest (about 3.0 × 2.6 × 2.0) sits at the front right; the next biggest
    is front-centre.
  - Ring radius about 1.15–1.3× the meteor's floor radius, tucked 0.2–0.5 into the shell's foot so that they union.
  - The small stones (0.6–1.0) sit in gaps and just outside the ring; 1–3 of them may be separate shells, as on the
    sheet's top view.
  - If one base rock reads repetitive, allow up to 3 base variants and record it.
- Rock tops reach at most 0.3 of H (about 2.2). In the front view they cover the meteor's bottom 15–30 %.

**Hero (`IronMeteorDeposit`).**

1. `_paste` the 5 finished pieces, the core and the rock copies into the build frame.
2. One exact self-union (m011 `_self_union`), then `union_loose`, then `m004.floor_cut` at z = 0.
3. Result:
   - Outer shell surfaces.
   - Open seam slots whose floor is the core's surface, recessed 0.6–0.65 below the lips.
   - Fused closed seams.
   - The floor: the core disc (orange) ringed by the 0.6 shell cut (grey) and the rocks' bottoms.
   - Zero interior or hidden faces.
4. Delete the old `core_underside()` hack. The floor disc is core-coloured because it is the core.

**Proud step.** The lobe seam gets its step naturally (lobe surface above the main's). For the front-right seam,
optionally scale Front's outer hull 1.025 about the centre, which gives a step of about 0.1 at its open seams.
Drop this if the fused crown seam then shows a ledge line on top.

**Stage 1 acceptance (render and compare every view, then measure).**

1. **Count and position.** Two cracks per view, within about ±0.07 x and ±0.08 h of the table. Run `mine.py` (pointed at
   the new renders) or the same logic through `K.sample`.
2. **Width and depth, measured through the MCP** with BVH ray pairs across each open seam at 5 points per seam:
   - lip-to-lip opening 0.35–0.6 (peaks at the jogs);
   - floor opening about 0.55 of that;
   - depth from the lip to the core floor 0.6–0.65.
   - Ends taper to closed over 0.8–1.2 studs.
3. **Depth reads from every view:**
   - Front, side and rear: the floor is visible in the widest stretch of each crack; the walls are visible at the jogs;
     the lip lines read as dark edges.
   - front34 and rear34: the near wall of each seam shows as a band.
   - Top: the FL and FR seams show and the back seams are near the limb.
   - Underside: an orange disc in a dark ring, ringed by rocks.
4. **Silhouette.** The lobe step and notch are visible in front, front34 and side. The crown is smooth with no ring
   line.
5. **Orange share** (all orange incl. walls) is 2–5 % per view with placeholder colours. It falls into the sheet's
   2.3–3.7 % once stage 4 darkens the lips.
6. **Each part against its sheet cell:**
   - shell piece: a thick segment, orange inside, thickness visible at the cut, as in "Shell Piece Detail";
   - core;
   - rock.
7. **Exploded render (`build`'s `render_views`):** all 5 pieces (4 as temporary linked copies or temp objects, as m011
   did for the extra crystals), the core in the middle and about 10 rim rocks below, laid out as on the sheet.

**Placeholder keys (stage 1):** `m009_shell` (outer), `m009_shell_cut` (non-seam cut faces and the floor ring),
`m009_seam_lip`, `m009_seam_ember` and `m009_core` (the three wall bands), `m009_core_hot` (seam floor), `m009_impact`.
Stage 4 sets their colours.

**Parts export decision (coordinator):** keep the 4 export names. `IronMeteorShellPiece` = Right (the sheet's cracked
lower-left exploded piece); the other 4 pieces are build-only objects (`_m009_piece_*`), used for pasting and
the exploded render, then removed. Exporting all 5 is the alternative; it is the main session's call.

### Stage 2: Optimisation and cleanup

- Hero under 4000 tris (expect about 2000–3000: 5 pieces at about 150–250, the core strips, 15 rocks at about 35) and
  each part under 1000.
- Keep the 3 wall-band rows and the lip chamfer row; they are colour geometry, not waste.
- Shells: the meteor and its touching rocks are one; 1–3 loose stones may be separate (as before). No interior shells:
  the core must be fully absorbed except the gap floors and the floor disc.
- Remove the boolean slivers along the seam walls (m011 `_tidy` / `_desliver` pattern), but lock the lip rows and the
  ground plane.

### Stage 3: UV

Smart UV or seams, margin ≥ 0.008, no overlaps (m011's 45° ANGLE_BASED route worked). The seam walls are long thin
strips; check their stretch.

### Stage 4: Materials, colour and texture (plan)

Colour everything through position fields on the finished meshes (m011 `_Paint` pattern). Never colour by facing.
Calibrate every key with `K.calibrate` against the sheet as rendered; the targets are below. Blend neighbours with
`K.blend(mode="blend", steps=3)`. Use `mode="hard"` only for shell against rock, and for the core against shell outer
faces.

| Key | Target (sheet, sRGB) | Kind | Where | Finish |
| --- | --- | --- | --- | --- |
| `m009_shell` | `#5C575C` (hero median; front, side and rear `#5A555B`–`#5E575B`) | stone | The main shell surface | rough 0.88 |
| `m009_shell_light` | `#68646D` (hero top facets; cool violet-grey) | stone | Broad noise patches, about 25–30 % of the surface, 2–4 facets each | rough 0.88 |
| `m009_shell_dark` | `#474143` (main face dark quartile; top view `#3E3C3E` in shade) | stone | Broad patches. A soot band within about 0.5 of each open seam lip, blended. A ground band within about 1.0 above the rocks. | rough 0.9 |
| `m009_shell_cut` | `#877E7C` swatch, rendering about `#A39A93` | stone | Shell thickness: the floor ring under the shell, and the part's non-seam cut faces | rough 0.9 |
| `m009_seam_lip` | `#4E2B2A` (lip dark) | vivid | Wall band 0–0.25T, plus the lip chamfer | rough 0.8, no emission |
| `m009_seam_ember` | `#743220` → `#913D2A` | vivid | Wall band 0.25–0.55T | rough 0.7, emission < 1.0 (solid in Roblox) |
| `m009_core` | `#F55E21` swatch (renders `#E34515`–`#F76119`) | vivid | Wall band 0.55T–T, the core part, the floor disc | emission ≥ 1.0, so Neon |
| `m009_core_hot` | `#FD911C`–`#FDAC22` (junction floor; hero light quartile `#FC8917`–`#FDBD40`) | vivid | Seam floor strips (the core faces exposed in the gaps); the hot patch on the core part's upper facets (exploded `#FDAE4F`) | emission ≥ 1.0, so Neon |
| `m009_core_deep` | `#CD3F18` (exploded core dark) | vivid | The core part's lower facets only, by height. Not in the hero. | emission ≥ 1.0 |
| `m009_impact` | `#A49086` (exploded); hero front `#A18A7D` | stone | Rim rocks | rough 0.92 |
| `m009_impact_light` | `#B8A498`–`#C6AEA0` | stone | Broad noise patches on the rocks (not tops by facing) | rough 0.92 |
| `m009_impact_dark` | `#877974` (front-view rocks) | stone | A ground-contact band (bottom 25 % of each rock by height). A faint soot bleed within about 0.4 of the shell. | rough 0.92 |

**The gradient into the gap, from outside to inside:**

1. shell → `shell_dark` (soot near the lip);
2. `seam_lip`;
3. `seam_ember`;
4. `core` (the lower walls);
5. `core_hot` (the floor).

Grade it by depth below the local outer surface (ray to the outer hull), never by normal. The floor's `core_hot` fades
to `core` along the seam toward each tapered end over the last 25 %, so the crack ends cool.

**Texture.** Broad Tint mottling on the shell (amp about 0.07, scale about 0.45, as m011 stone) and the rocks. Very low
or none on the Neon keys, which Roblox renders flat anyway.

**Re-measure.** Re-sample the final views with the 2a boxes:

- shell median within about 8 levels of `#5C575C`;
- the crack's dark/median/light quartiles near `#532B26` / `#E34515` / `#FC8917`;
- rocks near `#A18A7D` in front34 with VFX on (see Stage 5).

**Shading waiver.** `K.check` may flag `baked_shading` on the wall bands, because depth correlates with facing on the
walls. Waive it with a reason (m011 `SHADING_OK`): "seam wall bands graded by depth below the lip (the sheet's
lip → ember → orange → hot gradient)".

**Neon.** Two to three glow keys means two to three Neon pieces in the export, which is acceptable. Check the export
STATS line.

### Stage 5: Lighting (observations)

- **Emissive:** `m009_core`, `m009_core_hot` and `m009_core_deep` at emission ≥ 1.0, which export as Neon glow pieces.
  The lip and ember keys stay solid.
- **The sheet shows no orange light spill on the rocks** (`#A18A7D`, neutral warm grey).
  - The old `heat_glow` light (`#FF7A22`, brightness 1.2, range 10) sat at the main centre, inside the meteor. In
    Roblox a PointLight without shadows shines through the mesh and tints the whole ring. In our previews the rocks came
    out `#D8C0AA`.
  - Recommendation: one warm PointLight just outside the lobe seam's widest jog (about 0.5 out from the lip), colour
    about `#FF7A22`, brightness 0.6–0.8, range 6–7, shadows on, gentle flicker.
  - Optionally a second, dimmer one (0.4, range 5) at the back-right seam for the rear views.
  - Record the hero-local position in Roblox axes (x, z, −y) as m011's `STUDIO_LIGHT` did.
- **Check:** front34 rock median stays within about 10 levels of `#A18A7D` with VFX on.

### Stage 6: VFX (observations; existing sockets `heat_glow` and `embers`)

- **`heat_glow`:** move it from the meteor centre to the seams. Use 1–2 sockets on the open seams (lobe-seam jog and
  front-right jog), each carrying the stage 5 light.
  - Emitter shape stretched along the seam: about 0.4 × run length × 0.3.
  - Size 0.6–1.0 (smaller than the default 1.0–1.4, so the glow never hides the crack), rate 2–3.
- **`embers`:** the old socket floated at z 6.2, inside the new 7.4-tall meteor. Put one socket at the lobe seam's upper
  run (or both main seams): rate 3–4, spread about 20, rising. Every spawn point must be within about 0.3 of a seam lip.
- **Preview:** render with `vfx=True` and check that the sockets show in the export STATS line.

### Pitfalls

1. **Never colour a shallow groove.** The gap must go right through the shell to a recessed core floor, and its walls
   must be graded. Depth reads from the dark lip, the shaded walls and the hot floor, not from the orange alone.
2. **Avoid even width and regular zigzags.** Use long runs, sharp jogs, widest at the jogs, tapered ends, and no wedge
   stubs at the joints.
3. **Cracks go on piece boundaries.** The main crack is the lobe seam, and it changes the silhouette.
4. **Exact boolean.** Coincident or coplanar faces break the result. Use overlaps (0.05 core, 0.1 closed seams), never
   exact contact (m011's 0.04-sink lesson). Keep seam elevations within −60..70° so cone loops never self-intersect
   near the pole.
5. **No hidden or interior faces.** The core is absorbed by the union; only the gap floors and the floor disc stay.
   Check the shell count after the union.
6. **Don't over-widen to compensate.** If a crack still looks flat, fix the band colours and the floor heat first.
   Gaps above about 0.6 make the orange share exceed the sheet's.
7. **Neon is flat in Roblox.** The gradient must come from separate keys on separate face bands, which is why stage 1
   must leave the 3 wall rows.
8. **Lights inside the mesh tint the rim.** Lights go at the seams with shadows on.
9. **Scale.** The meteor grows to about 7.4 tall. Re-place every socket and the floor cut.
10. **Naming.** `IronMeteor` belongs to a kit sheet; keep `IronMeteorDeposit` and the part names. `M.mk` guards against
    saving over another sheet's names.
11. **Only one agent drives Blender at a time.** No commits, pushes or exports in stage agents.
