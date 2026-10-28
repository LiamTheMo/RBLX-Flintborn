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

## Stage 1 — Modelling (rework)

Builder: `art/blender/kit/mcp/m009.py`, rewritten from scratch (`build()`). Renders: `art/blender/renders/models/M009/`
(the seven sheet views, `exploded`, `part_shell`, `part_shell_in`, `part_core`, `part_rock`, and `M009_views.png`).
`FlintbornWorldKit.blend` saved through the MCP.

### What was built

Everything is built in one build frame (studs; front is −Y; ground z = 0). Directions are `_dir(az, el)` from the main
mass's centre `C0`.

- **Masses.**
  - Main is a 40-point Fibonacci cloud (radii 4.8 × 4.7 × 4.6, upper half squashed to 0.97, wobble 0.90–1.07) round
    `C0 = (0.5, 0.6, 3.3)`.
  - Lobe is an 18-point cloud (radii 2.9 × 2.65 × 2.6) at (−3.1, −1.5, 2.35). It bulges about 1.4 out at the front
    left; its top is at 4.7 (0.63 H).
  - Both are convex hulls, unioned to form the outer.
  - Compared with the plan's starting values (4.1 × 3.8 × 4.2, a 2.3 lobe), the first builds read as a tall egg against
    the sheet's broad, squat boulder. The hero view's meteor is about 1.45× as wide as it is tall.
- **Core** (`IronMeteorCore`, 76 tris).
  - It is the Main hull with every facet plane moved in by T = 0.6. The cut is exact (`_inset`: the hull's polygons are
    clipped by each inset plane and each cut is capped). Near-coincident corners are then merged within 0.3 into broad
    facets.
  - Measured shell thickness along rays from C0 on the main mass: 0.60–0.68.
- **Seams** (`OPEN_SEAMS`; the crown ring is closed everywhere). Each seam is resampled to nodes at most 6° apart.
  - **Lobe seam.** Its upper run follows the crease along the lobe's top, (204, 14) → (230, 15), at el 15–18. The
    measured crease is el 15–18, not the plan's 24–32, which was set for a bigger lobe. It then descends the crease
    down the lobe's front right, az 230–243, and drifts onto the main below el −15 (az 249–258). It is open into the
    ground.
  - **Front-right seam:** az −52 → −65 (308 → 295). The jog is at el 18 (G 0.52). It tapers closed at el −8.
  - **Back-right seam:** az 38–46. **Back-left seam:** az 116–124. Both are open into the ground.
  - G runs from 0.32 to 0.55, widest at the jogs. Each run has 2–3 sharp jogs, with no alternating zigzag and no stubs.
- **Cutters** (`_tube`): one closed tube per open run.
  - The cross-section has an A side (main side, carrying the lip chamfer 0.12 deep, set back 0.08) and a B side. Each
    side has rows at depth fractions 0.25 and 0.55 of the local thickness. A deep row 0.4 inside the core continues the
    wall's slope, so the core shows a floor FLOOR_FRAC = 0.55 G wide. The lid sits 0.8 above the higher lip.
  - Ends with G = 0 close to a single line (no cap, no stub). Open ends are capped below ground.
  - Each tube's winding is checked by its signed volume. `recalc_face_normals` left the back-right tube inside out,
    which silently dropped that crack.
- **Shell pieces** (`piece_obj`):
  - Each piece = outer ∩ sector cone − hollow (the core inset a further CORE_GAP = 0.05) − cutters, then floor-cut.
  - The cone is star-shaped from C0 through the piece's boundary loop of seam centre lines, capped at radius 11.
  - There are five pieces: Crown, Lobe, Front, Right and Back. `IronMeteorShellPiece` is Right (the coordinator's
    choice). The other four are `_m009_piece_*` temporaries, used only in the exploded render and then deleted.
  - The hollow is subtracted before the cutters. In the other order the exact solver collapsed the Back piece to two
    faces.
- **Hero** (`hero_obj`):
  1. Outer − cutters (exact, self-intersection on: the lids overlap at the lobe seam's corner), then ∪ core (`m009_core_hot`).
  2. Floor cut at z = 0. The floor is split along the core's z = 0 section (`_core_section`): the core's disc is
     `m009_core` (4.0 × 3.6), and the ring round it is `m009_shell_cut`.
  3. ∪ the impact rim: 12 transformed copies of `IronMeteorImpactRock` (non-uniform scale 0.82–1.35, turns, 6
     mirrored), tucked 0.35–0.45 into the foot at radii from `_foot`, plus 4 small stones (0.34–0.42).
  4. Then the sliver pass (m011 `_clean`; folded fin pairs dropped; `repair_nonmanifold`; m012 `_force_slivers` at 3°).
- **Not a literal paste of the five pieces.** Neighbouring pieces meet at the closed seams with coincident cut faces,
  the exact-boolean pitfall (pitfall 4). So the hero is built from the same outer, cutters and core, which makes every
  piece exactly a sub-volume of the hero's shell. The rock part is pasted literally.
- **Booleans.** `kit_models.carve` is unchanged. m009 has its own `_bool(o, other, op, self_x)` on build-frame
  temporaries, which covers INTERSECT.
- **Sockets** (kept for stage 6, moved out of the taller meteor):
  - `heat_glow` 0.5 outside the lobe seam's jog: hero-local (−1.54, −4.06, 3.56), scale 0.6.
  - `embers` 0.3 over the upper run: (−2.79, −2.53, 4.76).
  - Hero-local = build frame − (−0.248, 0.361, 0).
- **Placeholder keys:** `m009_shell`, `m009_shell_cut`, `m009_seam_lip`, `m009_seam_ember` (emit 0.5), `m009_core`
  (emit 1.5), `m009_core_hot` (emit 2.0) and `m009_impact`. The old `m009_shell_grey` and `m009_impact_cool` are dropped.

### Measured (MCP)

| Object | Tris / budget | Size (studs) | Shells | Non-manifold / boundary | Min corner | Keys |
| --- | --- | --- | --- | --- | --- | --- |
| IronMeteorDeposit | 2892 / 4000 | 12.62 × 11.13 × 7.41 | 4 (meteor with the 12 rim rocks, plus 3 loose stones) | 0 / 0 | 3.6° | all 7 |
| IronMeteorShellPiece | 528 / 1000 | 4.16 × 6.91 × 6.98 | 1 | 0 / 0 | 5.0° | shell, shell_cut, core, ember, lip |
| IronMeteorCore | 76 / 1000 | 8.34 × 8.07 × 7.14 (the whole ball, below-ground part included) | 1 | 0 / 0 | 26° | core |
| IronMeteorImpactRock | 44 / 1000 | 2.41 × 2.11 × 1.25 | 1 | 0 / 0 | 16.6° | impact |

- Meteor group (hull) bounds: x −5.76..5.25, y −4.0..5.4, z top 7.41.
- Normals are outward, there are no n-gons, UVMap exists on all four, and `K.check` reports no problems.
- Hero tris by key: shell 423, shell_cut 55, lip 504, ember 306, core 459, core_hot 279, impact 866.
- Shell piece thickness (rays from the outer facets straight in): median 0.66, p10–p90 0.65–0.71, minimum 0.51 (at a
  cut edge). It is 0.6 + CORE_GAP by design, and 69 of 70 rays land on the orange inner face.

### Crack geometry (ray profiles across each open seam, `m009_probe.py` in the study folder)

| Seam, el | G | Lip-to-lip | Hot floor seen radially | Depth (lip → core floor) | Lip step |
| --- | --- | --- | --- | --- | --- |
| Lobe, 18 | 0.32 | 0.32 | 0.22 | 0.62 | lobe side 0.11 proud |
| Lobe, 8 | 0.42 | 0.40 | 0.23 | 0.63 | lobe side 0.12 proud |
| Front-right, 41 / 32 / 18 / 6 | 0.34 / 0.41 / 0.52 / 0.42 | 0.33 / 0.39 / 0.58 / 0.41 | 0.22 / 0.22 / 0.33 / 0.23 | 0.66 / 0.66 / 0.62 / 0.63 | chamfer 0.05 |
| Back-right, −15 / −40 | 0.40 / 0.41 | 0.39 / 0.39 | 0.22 / 0.22 | 0.63 / 0.66 | 0.05 |
| Back-left, 9 / −15 | 0.46 / 0.41 | 0.46 / 0.40 | 0.30 / 0.22 | 0.65 / 0.68 | 0.05 |

- Depth is 0.62–0.68 (target 0.6–0.65) and the opening is 0.32–0.58 (target 0.35–0.6).
- The floor is about 0.55 G. The walls splay, so seen radially the bands show as thin rims (lip 0.01–0.03, ember
  0.03–0.08, core 0.02–0.06). Seen obliquely they read as bands: front34, front and rear in the renders.
- End tapers: front-right bottom about 1.0 stud; back tops about 0.85; lobe upper end and front-right top about 0.6
  (a little short).

### Cracks per view against the sheet (`mymeasure.py`, measure.py's scan on our renders, VFX on)

Positions are (x, h) as in the 2a table. The sheet's dark bounding boxes include the rocks' shaded sides; ours do
not (our rocks render pale). Positions are therefore approximate.

| View | Ours: crack A | Ours: crack B | Orange share, ours / sheet |
| --- | --- | --- | --- |
| front34 | (0.29, h0.68) upper run → (0.45, h0.58) → (0.47, h0.49) → (0.51, h0.40) → (0.56, h0.30). Widest 1.5–3 %, 4.5 % at the jog. Sheet: 0.33 → 0.55, h0.68 → 0.15. | Right limb, x ≈ 0.8, h0.62–0.76. Shaded dark red, so mostly under the scan's orange threshold. Sheet: 0.85 → 0.80. | 2.6 / 3.6 % (about 4.5 % with the hot yellow) |
| rear34 | (0.29, h0.68) → (0.31, h0.49) → (0.39, h0.17). Widest 3.3 %. Sheet: 0.22 → 0.30. | Not visible: the back-left seam is at the limb. Sheet: 0.91. | 1.9 / 2.3 % |
| front | (0.24, h0.77) → (0.32, h0.59) → jog (0.30, h0.53) → (0.34, h0.42) → (0.41, h0.24). Widest 3.8–4.8 %. Sheet: (0.24, h0.63) → (0.41, h0.24), 4.6–5.5 %. | (0.72, h0.83) → (0.76, h0.65) → (0.74, h0.53). Widest 3.3 %. Sheet: (0.80, h0.76) → (0.79, h0.42), 4 %. | 4.7 / 3.7 % |
| side | Front-right at the left limb (x ≈ 0.2, h0.72). | Back-right at the right limb, shaded. | 0.3 / 3.6 % |
| rear | Back-right (0.10, h0.60), short. Sheet: 0.22 → 0.32. | Back-left (0.62, h0.70) → (0.68, h0.55) → (0.66, h0.30) → (0.58, h0.10). Widest 3.0 %. Sheet: 0.81 → 0.77. | 2.0 / 2.4 % |
| top | Lobe seam near the front edge, x 0.16–0.32. Sheet: (0.19, 0.50) → (0.37, 0.20). | Front-right, x 0.75–0.77, front 0.09–0.19. Sheet: (0.87, 0.63) → (0.78, 0.28). No crack on the crown, as on the sheet. | 0.5 / 2.3 % |

- **Crack colour range** (mine.py, vivid quartiles, placeholders):
  - front: `#5F312C` / `#AA4C36` / `#FF963E`;
  - front34: `#693730` / `#C66F3F` / `#FFFF42` (the hot floor);
  - sheet: `#4E2B2A` / `#E34515` / `#FDBD40`.
  - Before this rework the range was a flat `#FF8236`–`#FFA149`. The dark lip, the ember and orange walls and the hot
    floor now separate, and the gaps visibly go through the shell.
- **The sheet's views cannot all be matched.** Every view repeats the hero's composition: a lobe at the lower left and
  two cracks, one in each half. Its side view even shows a lobe on the left.
  - The seams are placed for front34 (the hero), front, rear and rear34.
  - Side and top therefore show their cracks near the limbs or the front edge, with a low orange share.
  - This follows WorldModeling §1.1: the hero view controls.

### Decisions and deviations

- The hero is assembled from the same parts (outer, cutters, core, rock), not pasted from the five pieces; the reason
  is above.
- The core part is the true core: the hollow the shell closes round, 8.3 wide. The sheet's exploded core looks about
  0.45 of the meteor's width, but the reusable core should fit the reusable pieces.
- The exported shell piece (Right) is a tall curved segment, 4.2 × 6.9 × 7.0. The sheet's "Shell Piece Detail" is
  chunkier. Exporting the Lobe piece instead (the chunky rounded one) is the main session's call; it is one line
  (`EXPORT_PIECE`).
- Proud step: only the lobe seam has one (the lobe side stands 0.1–0.2 proud). The front-right seam's optional 1.025
  scale was not used. Its main-side lip chamfer (0.05 below the centre line) gives a small step instead.

### Left for later stages

- **Stage 2.**
  - The sliver pass is already in the build: minimum corner 3.6° on the hero and 5° on the piece.
  - Polish towards 5° if wanted, but keep the wall rows (0.25 / 0.55 thickness edge rows and the chamfer row). They are
    colour geometry.
  - The hero has 4 shells: the meteor with the 12 rim rocks, plus 3 loose stones, which is allowed.
- **Stage 3.** UVs are already made by `M.finish` (45°, ANGLE_BASED, margin 0.008). Check stretch on the long seam-wall
  strips.
- **Stage 4.**
  - Every key is a placeholder.
  - The rocks render peach (`#A49086` placeholder) and need calibrating to `#A18A7D`.
  - Grade the gap colours by depth: the key bands are already separate faces.
  - The heat sprite at the lobe jog brightens front34, so measure colours with VFX off as well.
  - The floor disc is 4.0 × 3.6, against the sheet's roughly 5. It is smaller because the meteor sits 3.3 deep in the
    ground. Recolouring will not change that; the only fix is a geometry change: lower C0 or flatten the core's bottom.
- **Stage 6.** The sockets are placed only roughly. `heat_glow` (scale 0.6) at the lobe jog, and `embers` over the
  upper run.

## Stage 2+3 — Cleanup and UV

Builder changes in `m009.py` (rebuilt through the MCP; `FlintbornWorldKit.blend` saved):

- **Export piece switched to Lobe** (`EXPORT_PIECE = "Lobe"`, main session's decision). `IronMeteorShellPiece` is now
  the chunky lobe piece: the solid lobe bulge plus the main shell's back-left sector up to the crown ring. It was the
  Right piece (528 tris, 4.16 × 6.91 × 6.98); it is now 672 tris, 5.91 × 8.25 × 6.56. The `part_shell` (−45°, outside)
  and `part_shell_in` (140°, the orange hollow) cameras are re-aimed for it.
- **Stage 2 `_polish(o)`** runs on all four objects after `M.finish(uv=False)`:
  - every face a triangle (`m012._tri_quads`);
  - each corner under `POLISH_LIM` = 5° is opened by a flip (`_flip_thin`: same key on both sides, the surface
    moving at most `POLISH_TOL` = 0.08 studs, both new triangles facing the same way) or by a nudge of at most 0.08
    studs (`_nudge_free`; ground verts stay on z = 0);
  - **wall rows locked:** every vert on an `m009_seam_lip` or `m009_seam_ember` face (lip line, chamfer row, the 0.25
    and 0.55 rows) never moves, and edges between two keys are never flipped;
  - the origin is put back at the bottom centre, with the sockets following.
  - Result: hero 2 flips and 1 nudge (0.01 studs, a rim rock's foot); shell piece 2 flips; core and rock unchanged.
    The last sliver (4.6°, an outer shell facet ending on the lobe seam's lip, on both the hero and the piece) needed
    a flip that moves a facet crease by 0.074 studs, hence the tolerance of 0.08.
- **Stage 3 `_uv(o)`:** `M.smart_uv` with `UV = dict(angle=45, method="ANGLE_BASED", margin=0.008, min_angle=45)`,
  then `m012._uv_unfold` cuts any faces the unwrap folds free. Before, smart_uv's fallback had silently dropped the hero
  to 35° (416 islands); at 45° with 5 faces cut free it has 348 islands, no overlaps and about the same stretch.
  Tried on the hero: 55° gives 220 islands, worst conformal stretch 1.27, area stretch 1.29; 66° gives 157 islands,
  1.41 and 1.68. The fill gain was small (0.28 → 0.32), so 45° stays.
- **New checks in `build()`:** `_inner_shells` (shells inside another shell, by ray parity) and `_self_hits`
  (crossing faces that share no vertex). `_drop_unused` now returns what it purged.

### Measured (MCP, after the final build)

| Object | Tris / budget | Size (studs) | Shells | Non-manifold / boundary / wire / loose | N-gons | Zero-area / dup verts | Inner shells / self-crossings | Min corner | Normals | Origin offset | Transforms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IronMeteorDeposit | 2892 / 4000 | 12.62 × 11.13 × 7.41 | 4 (meteor + 12 rim rocks, 3 loose stones) | 0 / 0 / 0 / 0 | 0 | 0 / 0 | 0 / 0 | 5.00° (was 3.64°) | outward | 0, 0, 0 | applied |
| IronMeteorShellPiece (Lobe) | 672 / 1000 | 5.91 × 8.25 × 6.56 | 1 | 0 / 0 / 0 / 0 | 0 | 0 / 0 | 0 / 0 | 5.01° (the Lobe piece before the polish: 4.58°) | outward | 0, 0, 0 | applied |
| IronMeteorCore | 76 / 1000 | 8.34 × 8.07 × 7.14 | 1 | 0 / 0 / 0 / 0 | 0 | 0 / 0 | 0 / 0 | 26.0° | outward | 0, 0, 0 | applied |
| IronMeteorImpactRock | 44 / 1000 | 2.41 × 2.11 × 1.25 | 1 | 0 / 0 / 0 / 0 | 0 | 0 / 0 | 0 / 0 | 16.7° | outward | 0, 0, 0 | applied |

- All faces are triangles. There are no modifiers or custom normals, shading is flat, and `K.check` reports no
  problems.
- Polish vertex moves: hero 1 vert of 1446 (0.01 studs); no locked (wall-row) vert moved on any object.
- Purge: 14 orphan M009 meshes went (the build's temporaries and the old datablocks). No `_m009_*` objects and no
  unused `FB_m009_*` materials are left, and every mesh is named after its object.
- **Cracks unchanged.** `m009_probe.py` gives identical results (all 20 seam rows: opening, depth, hot floor, bands
  and lip steps) with and without the polish. The values match the Stage 1 table. The hero renders are unchanged.

### UV (`M.uv_stats`, layer `UVMap`)

| Object | Islands | Overlaps | Flipped | Faces cut free | Min gap / border | Fill | Density (min / median / max) | Conformal worst / p95 | Area worst | Worst angle change | px / stud at 1024 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IronMeteorDeposit | 348 | 0 | 0 | 5 | 0.016 / 0.008 | 0.285 | 1 / 1 / 1 | 1.106 / 1.015 | 1.069 | 5.5° | 27 |
| IronMeteorShellPiece | 49 | 0 | 0 | 0 | 0.016 / 0.008 | 0.428 | 1 / 1 / 1 | 1.071 / 1.026 | 1.062 | 2.3° | 56 |
| IronMeteorCore | 12 | 0 | 0 | 0 | 0.016 / 0.008 | 0.432 | 1 / 1 / 1 | 1.062 / 1.058 | 1.031 | 2.9° | 50 |
| IronMeteorImpactRock | 8 | 0 | 0 | 0 | 0.016 / 0.008 | 0.451 | 1 / 1 / 1 | 1.090 / 1.070 | 1.092 | 4.6° | 194 |

Conformal stretch per key, worst / p95. The long seam-wall strips are among the least stretched faces.

| Key | Hero | Shell piece |
| --- | --- | --- |
| m009_seam_lip | 1.032 / 1.009 (504 tris) | 1.032 / 1.014 (153) |
| m009_seam_ember | 1.015 / 1.005 (306) | 1.031 / 1.011 (85) |
| m009_core | 1.008 / 1.002 (459) | 1.071 / 1.048 (214) |
| m009_core_hot | 1.000 / 1.000 (279) | — |
| m009_shell | 1.081 / 1.026 (423) | 1.030 / 1.019 (143) |
| m009_shell_cut | 1.018 / 1.001 (55) | 1.025 / 1.001 (77) |
| m009_impact | 1.106 / 1.057 (866) | — |

- The hero's fill is low (0.285, 27 px/stud) because 348 islands each carry the 0.008 margin. That doesn't matter for
  export: the GLB exporter writes its own palette-cell UVs, and this layer only has to exist and be clean.

### Left for later stages

- Stage 4 onwards as listed under Stage 1. The shell piece is now the Lobe piece: its keys are shell, shell_cut, core,
  ember and lip, and stage 4 colours it with the rest.

## Stage 4 — Materials, colour and texture

Builder: `m009.py` (`palette`, `TARGETS`, `calibrate`, `colour_all` and its `colour_*` passes), rebuilt through the MCP;
`FlintbornWorldKit.blend` saved. No geometry or UV change: tris 2892 / 672 / 76 / 44 and 1446 hero verts as stage 2,
0 non-manifold and 0 boundary edges on all four. The colour pass runs on the finished meshes after the polish and UVs
(m011 `_Paint` pattern). Every field is a build-frame position: mesh coords + `m009_offset` (each object's
bottom centre in the build frame, stored on the object). Nothing is chosen by which way a face points.

### Method

- **Sample.** Swatches with `M.raw_sample`, rendered regions with `M.sample` (stone) or `K.sample` (vivid), using the
  2a boxes. The crack was also sampled at luminance percentiles (5/15/30/50/70/90) per view, sheet against ours.
- **Calibrate.** `m009.calibrate()` wraps `K.calibrate` (test dome, studio, hero camera, VFX off), with two fixes:
  - Stone keys are sampled unfiltered. The box lies wholly on the dome. `K.sample`'s stone filter (sat < 0.18) drops
    the warm rock, which the studio renders peach at sat 0.28, so the loop chased the background (`#A18A7D` went to
    `#2C0C05`).
  - The Neon preview is kept on every round (below).
- **Neon preview (`_glow_mats`).** Every key with emission ≥ 1.0 renders as its emission only: BSDF base colour
  black, no specular. That is how Roblox shows a Neon part: one flat colour, unshaded.
  - Without it, emission plus the lit diffuse doubled the brightness, and calibration pushed the core's hex down to
    `#882400`. Roblox would then have shown a dim red Neon.
  - With it, every Neon hex sits within about 20 levels of its sheet colour.
- **Blend.** Each region is a ladder of quarter-step `K.mix_key` keys (via `_mix`, which keeps the emission of Neon
  parents). Shell: dark, plain, light. Rock: dark, plain, light. Floor: core, core_x_hot_50, hot. Each facet group
  (coplanar, connected faces) takes one step, so there is no per-triangle confetti.
- **Texture.** Broad Tint mottling, one value per facet group (no per-face jitter). Every Tint is reset to 1 first:
  the booleans had left 8 hero faces with uneven corner Tint.
  - Shell: amp 0.08, scale 0.42. Cut: 0.05, 0.5. Rock: 0.06, 0.9.
  - Rim copies: an extra per-rock factor of 0.92–1.07.
  - Neon keys ignore Tint.

### Regions

- **The crack, by depth below the local outer surface.** The cutters' face rows are the depth bands, so each band is one
  key along its whole length. Grading each band triangle by its centre's depth would alternate colours triangle by
  triangle.
  1. Shell soot: the shell fragments along an open seam lip, tone −0.35 within 0.3 studs, fading out by 0.9 and with
     the gap.
  2. `seam_lip`, 0–0.25 T plus the chamfer: a solid dark edge.
  3. `seam_ember`, 0.25–0.55 T: deep red, Neon.
  4. `core`, 0.55 T–T: the orange walls, Neon.
  5. Floor (the core's faces in the gap), graded along the seam by its local gap G (`HOT_G` 0.30 / 0.46): `core`
     where G ≤ 0.30, `core_x_hot_50` between, `core_hot` where G ≥ 0.46. The floor is hot at the wide jogs and cools
     to orange towards each tapered end. Tris: 115 hot, 109 mix, 55 core.
- **Shell.**
  - Broad light and dark patches: noise at each outer hull facet's centre (`SHELL_TONE` scale 0.3, amp 2.0, dead
    zone 0.1). The noise alone gives 29 % light, 41 % plain and 30 % dark.
  - Then soot along the open seams, and a darker foot (tone −0.25 below z 1.2, fading out by z 2.4, among the rocks).
  - Result by area: about 24 % light, 33 % plain and 43 % dark.
  - Keying the noise to the hull facet keeps the shell piece and the hero identical: 134 of 139 of the piece's shell
    faces carry the same key as the hero face under them.
- **Shell-thickness cut faces** (the floor ring and the piece's cut ends): `shell_cut`, the grey "Metal Core (Inner
  Faces)" colour as the cross-section's cut wall renders it, with Tint only.
- **Shell piece's inner (hollow) face:** `core_deep`, picked by lying on the hollow hull (ray from C0, within 0.03).
  The sheet's inner face is a darker orange than the core.
- **Core part:** height (0.4) plus broad noise (1.0), ranked by area, one key per facet.
  - Ranks: below 0.22 `core_deep`, then `core` to 0.76, then `core_x_hot_50` to 0.88, then `core_hot`.
  - Tris: 18 deep, 39 core, 10 mix, 9 hot.
  - With height weighted 1.0 the hot patch was a saw-toothed band; with 0.7 the big top facet went hot and the part
    rendered `#FF901C`.
- **Impact Rock part:** broad noise patches in its own frame (`ROCK_TONE` scale 0.75, amp 1.6, dead zone 0.08).
  - The planned darker ground band by height was dropped. On a 44-tri stone the low ring is the down-facing ring, so
    `K.check` read it as painted shade (corr 0.82).
  - Each hero rim copy takes the part's key and Tint face for face (nearest copy surface, then the part face under
    the point, through the copy's inverse transform), times its own factor.
- **`K.check`:** no problems; `kit_baked_shading` is 0.0 on all four objects, so no shading waiver is set.
  `SHADING_OK` is ready if a later change trips it.

### Palette (calibrated)

| Key | Target (sheet, as rendered) | Calibrated hex | Dome renders | Emission | Roughness | Used on |
| --- | --- | --- | --- | --- | --- | --- |
| `m009_shell` | `#5C575C` hero median | `#43424A` | `#5E595D` | 0 | 0.88 | hero, piece |
| `m009_shell_light` | `#68646D` hero top facets | `#4D4D58` | `#69666D` | 0 | 0.88 | via mixes |
| `m009_shell_dark` | `#474143` main face dark | `#322E33` | `#4A4445` | 0 | 0.9 | hero, piece |
| `m009_shell_cut` | `#998B81` (cross-section cut wall, stone filter; swatch `#877E7C`) | `#726B69` | `#988A81` | 0 | 0.9 | hero floor ring, piece cut ends |
| `m009_seam_lip` | `#6F332E` dome target: sheet lip `#4E2B2A` × (sheet / ours at the crack's 15th percentile, `#592D28` / `#3E2624`, linear) | `#500E0E` | `#6E312E` | 0 | 0.8 | hero, piece |
| `m009_seam_ember` | `#C33615` (sheet hero right seam, 30th percentile) | `#B73C1C` | `#C23515` | **1.0 Neon** | 0.7 | hero, piece |
| `m009_core` | `#F55E21` (Crack / Core swatch) | `#E5642A` | `#F86223` | **1.0 Neon** | 0.5 | hero, piece, core |
| `m009_core_hot` | `#FD911C` (junction gap floor) | `#FB8D24` | `#FF911D` | **1.0 Neon** | 0.5 | hero, core |
| `m009_core_x_hot_50` | mix | `#F07827` | — | **1.0 Neon** | 0.5 | hero, core |
| `m009_core_deep` | `#CD3F18` (exploded core dark) | `#BF4520` | `#CB3F19` | **1.0 Neon** | 0.5 | piece inner face, core |
| `m009_impact` | `#A18A7D` hero rocks | `#786A66` | `#A0887D` | 0 | 0.92 | hero, rock |
| `m009_impact_light` | `#B8A498` | `#887E7A` | `#B5A296` | 0 | 0.92 | via mixes |
| `m009_impact_dark` | `#877974` front-view rocks | `#645D5E` | `#857873` | 0 | 0.92 | via mixes |

Mixes in use: shell ×dark 25/50/75 and ×light 25/50/75; impact ×dark 25/50 and ×light 25/50/75. Each is solid, with
roughness interpolated.

**Targets that were tried and changed:**

- Ember first stayed solid and unlit (`#743220`, emission 0). It rendered `#3B2121`–`#542B26`, so the crack medians of
  the front, side, rear and rear34 views came out dark red-brown.
- Ember was then made Neon at the front view's 30th percentile, `#9D311A`. The medians were still ember red,
  `#8B2D1D`–`#9B2F1C`, against the sheet's `#C2441E`–`#DE400F`. That gave the final `#C33615`.
- The core was first calibrated to the hero crack's median, `#E34515`. The core part then rendered `#E24919` against
  the sheet's `#FA601D`, so the core now uses the swatch.
- The lip was first calibrated to `#4E2B2A` on the dome. It rendered `#2B1614`–`#3E2624` in the crack's shade, against
  the sheet's `#49211E`–`#592D28`.

### Neon decision (export: emission ≥ 1.0 becomes a Neon part, one flat colour, no Tint)

Neon keys:

- ember, core, core_x_hot_50 and hot on the hero (4 Neon pieces);
- ember, core and core_deep on the shell piece (3);
- core_deep, core, core_x_hot_50 and hot on the core (4).

Only the lip is solid in the crack.

**Why:** the depth must survive Neon's flattening. Each depth band is a separate key on separate faces, so the
gradient from dark solid lip through deep-red Neon and orange Neon to yellow-orange Neon shows in Roblox as four
distinct colours, with the unlit dark edge outlining the opening.

- Making the ember Neon too is what makes the walls read as glowing from the oblique views. The sheet's cracks are
  orange there, and its dark is only a thin edge.
- The cost is 4 Neon pieces on the hero (the plan said 2–3 were acceptable). The main session should check the export
  STATS line.

### Target vs got (VFX off unless stated; hero 480 × 400 cells; 2a boxes on the sheet)

| Region | Sheet median (dark / light quartile) | Ours median (dark / light) | Δ |
| --- | --- | --- | --- |
| Shell, hero (front34) | `#5C575D` (`#3C393B` / `#9C8885`) | `#595559` (`#4D4A4D` / `#635F64`) | −3. Within 8 ✓. Our quartile spread is narrower: the sheet's light quartile is rim highlights, which is lighting. |
| Shell, hero top facets | `#68646D` | `#5C585C` | −12. Lighting: the sheet's key light is stronger on top. Not painted, by rule. |
| Shell, front view | `#5E575B` | `#524F52` | −12 (lighting and the darker foot) |
| Shell, front34 with VFX on | — | `#5A5559` | heat sprite: +1 |
| Crack, lobe seam (front34) | `#E24515` (`#532B27` / `#FC8816`) | `#E85B1F` (`#4F2625` / `#FF911D`) | ✓ |
| Crack percentiles, front34 (5/15/30/50/70/90) | `#49211E #592D28 #5F3430 #EA410A #FA5E0F #FD9E1C` | `#401413 #502726 #683432 #EB5B20 #FF7820 #FF911D` | ✓ dark lip, then orange, then hot |
| Crack percentiles, front | `#462622 #57302B #9D311A #DE400F #F26011 #FB9E1C` | `#3D1817 #4D2120 #572A29 #AC351B #C33B17 #F86223` | median less orange: the view sees mostly the ember walls, and little hot floor |
| Crack percentiles, rear34 | `… #7E3B2E #D23C10 #F3570C #FA860F` | `… #582726 #C23515 #F76122 #FF7220` | ✓ |
| Crack percentiles, rear | `… #883C25 #C2441E #F06414 #F9A316` | `… #4D2120 #A73219 #C23515 #E15822` | close |
| Crack percentiles, side / top | median `#C94418` / `#C2481F` | `#4F2524` / `#5E2725` | the seams sit at the limbs in these views (stage 1 geometry); only the lips show |
| Crack, right seam (front34) | `#E75221` | `#713431` | that seam is at the limb in our front34, so its wall's lip shows (geometry) |
| Orange share front34 / front | 4.0 % / 4.5 % | 4.8 % / 4.8 % | ✓ (2–5 %) |
| Rocks, hero front | `#A0887B` (`#655855` / `#C6ADA0`) | `#99857A` (`#4F4A4E` / `#A49084`) | −7 / −3 / −1 ✓. VFX on: `#9A857A`, within 10 ✓. No longer peach (was `#D8C0AA`). |
| Rocks, front view | `#877973` | `#8B786E` | ✓ |
| Impact Rock part | `#A18D84` | `#A68E82` | ✓ |
| Core part (exploded) | `#FA601D` (`#CD3F18` / `#FDAE4F`) | `#F8631F` (`#F76122` / `#FF911D`) | ✓. The deep facets are low, under the camera. |
| Core underside (floor disc) | `#E54A18` | `#F76223` | +18 R (the disc is `core`; never seen in game) |
| Shell piece inner face | `#BB3813` | `#CB3F19` | +16 R (`core_deep`, flat) |

Renders: `art/blender/renders/models/M009/` (the build's renders, VFX on). The VFX-off measuring copies and
`measure_s4.py` are in the scratchpad `s4` folder.

### Left for later stages

- **Stage 5.**
  - The glow is now carried by 4 Neon keys. Keep the lip solid.
  - The seam PointLight should be placed as recommended (outside the lobe seam's jog, shadows on). It also lights the
    solid lip in game.
  - The rocks measure `#9A857A` with the heat sprite on, within 10 of `#A18A7D`.
- **Stage 6.** Sockets unchanged (`heat_glow` at the lobe jog, `embers` over the upper run).
- **Verifier.**
  - The side and top views' cracks, and the front34 right seam, read as dark lips. The seams sit at the limbs in those
    views. That is geometry, not colour.
  - The shell's top facets and front view are 12 levels darker than the sheet's: the sheet's lighting is brighter
    there. The hero median matches.

### Fixes after verifier round 1

These run on the Stage 1 fixes: crack B turned and widened, the rim pushed out, the Lobe piece re-cut, the core's
bottom flattened. No geometry or UV change: hero 3028 tris, 13.36 × 11.88 × 7.41. `K.check` reports nothing.
The `.blend` was saved through the MCP.

1. **Orange share.** It is counted as `mymeasure.py` counts it (orange: R > 170, R − B > 110, G < 200, R > G + 40),
   as a share of the dark meteor pixels. The script is `orange_s4.py` in the scratchpad `s4` folder.
   - With every key at its Stage 4 colour, nearly all the crack's Neon counted as orange. In front34 the ember band
     (#C23515) was 1.0 %, the core 2.6 %, the hot floor 1.7 % and the mix 0.7 %.
   - **New Neon key `m009_seam_deep`**, `#963623`, renders `#9B2F1C`. Its target is the sheet's crack at the 30th
     percentile in the front view, `#9D311A`. R < 170, so it does not count as orange.
   - **`SEAM_COOL`, lobe seam only, picked by nearest seam:**
     - its ember band → seam_deep all along;
     - its core band → seam_deep where the local gap G < 0.47, so the core band stays orange only at the widest jogs,
       over the hot floor;
     - its floor's orange ends (G ≤ 0.30) → seam_deep.
     - The lobe seam then reads, from the outside in: dark solid lip, deep-red walls, orange where widest, then the
       graded mix / hot floor. That is still a depth gradient.
   - Crack B (FrontRight) and the back seams keep lip → ember → core → hot. The rear views' share already matched.
   - **Tried:**

     | Change | front34 / front share (VFX on) | Lobe crack median |
     | --- | --- | --- |
     | Whole lobe walls deep red | 4.6 / 4.7 % | `#9B301D` |
     | Ember band only | 6.1 / 6.3 % (the ember counts as orange) | `#E25D20` |
     | Core-band threshold 0.40 / 0.43 / 0.47 / 0.52 | front34 5.1 / 4.9 / 4.7 / 4.5 % (VFX off) | — |

   - **Trade-off, for the verifier.** Any setting that roughly halves the excess turns the lobe crack's median deep
     red: `#9C3A1D` (VFX on) against the sheet's `#E24515`. Its 70th and 90th percentiles stay orange and hot
     (`#FF7820` / `#FF911D`). The sheet's crack is narrower and mostly orange; ours is wider, so covering a similar
     orange area means a cooler glow.
2. **Shell tone.**
   - `m009_shell_light` was re-calibrated 6 levels up: target `#6E6A73`, hex `#51505D`, renders `#6E6973`.
   - `SHELL_TONE["bias"]` = 0.15 lifts the whole position-noise field, so more facets take a light step: hero light
     tris 196 (was 76).
   - Tried bias 0.25 with the foot band at −0.15: the front view gained only +1, and the hero median overshot to
     `#5E5A5F`, so it was not kept.
3. **Underside disc** → `m009_core_deep` (`#CB3F19`, flat), matching the core part's lower facets.
4. **Orphans.**
   - `_drop_calib()` runs at the end of `calibrate()` and first in `_drop_unused()`. It purges zero-user `T_Calib*`
     meshes that carry only `FB_m009_*` keys.
   - The 147 orphans are gone, and with them the unused `FB_m009_impact_dark` / `_light` materials.
   - The keys stay in the palette. `_mi` recreates a material whenever the rocks use one (the rocks use their 25 / 50
     / 75 mixes).
5. **Neon count.**
   - hero: 6 — ember, core, core_x_hot_50, hot, seam_deep, core_deep (the disc);
   - shell piece: 3 — core, core_deep, seam_deep (its walls are the lobe seam's);
   - core: 4.
   - Putting the disc on ember (`#C23515`) instead would save one Neon piece on the hero, at Δ R −35 against the
     sheet's underside.

**Re-measured (VFX off / on; sheet in brackets):**

| Region | Off | On | Sheet |
| --- | --- | --- | --- |
| Orange share, front34 | 4.67 % | 4.99 % | 3.6 % (was 6.4 / 6.8) |
| Orange share, front | 4.77 % | 5.21 % | 3.7 % (was 7.0 / 7.3) |
| Orange share, rear34 / rear | 2.87 / 2.74 % | 2.93 / 2.81 % | 2.3 / 2.4 % |
| Orange share, side / top | 0.78 / 0.77 % | 0.82 / 0.85 % | 3.6 / 2.3 % (geometry) |
| Crack B, front34 (median / dark / light) | `#D65623` / `#70312B` / `#F76123` | `#D75723` | `#E75221` / `#6A3028` / `#FDBD40` (kept) |
| Lobe crack, front34 | `#9B341D` (dark `#4F2523`, light `#FF911D`) | `#9C3A1D` | `#E24515` (see the trade-off) |
| Shell, hero | `#5B565A` | `#5B565A` | `#5C575D` ✓ |
| Shell, top facets | `#646066` | `#646166` | `#68646D` (−4 / −4 / −7; was −12) |
| Shell, front view | `#545156` | `#565156` | `#5E575B` (−8..−10; was −12) |
| Rocks, hero front | `#99847A` | `#9A857A` | `#A0887B` ✓ |
| Rocks, front view | `#87766D` | `#88766D` | `#877973` ✓ |
| Core part | `#F8621D` | — | `#FA601D` ✓ |
| Underside disc | `#CB3F19` | `#CB3F19` | `#E54A18` (was `#F76223`; now Δ −26 R, the other way) |
| Shell piece inner face | `#CB3F19` | — | `#BB3813` |
| Impact Rock part | `#A68E82` | — | `#A18D84` ✓ |

**Final (coordinator's call): ember-only on the lobe seam; the disc on ember.** The user's complaint was that the cracks
were "not apparent", so a vivid orange lobe crack wins over matching the sheet's orange share. This supersedes the
`SEAM_COOL` and disc choices above:

- `SEAM_COOL = {"Lobe": {EMBER: (SEAM_DEEP, 9.0)}}`: the lobe seam's ember band is deep red. Its core band and floor
  ends are orange again.
- The underside disc is `m009_seam_ember` (renders `#C23515` against the sheet's `#E54A18`). That is one fewer Neon
  piece on the hero, on a face never seen in game.

| Measure | VFX off | VFX on | Sheet |
| --- | --- | --- | --- |
| Orange share, front34 | 5.73 % | 6.05 % | 3.6 % |
| Orange share, front | 5.89 % | 6.27 % | 3.7 % |
| Lobe crack median | `#E25D20` | `#C96020` (heat sprite) | `#E24515` |
| Crack B median | `#D65723` | `#D75723` | `#E75221` |
| Underside disc | `#C23515` | `#C23515` | `#E54A18` |

Neon keys:

- hero: 5 — ember, core, core_x_hot_50, hot, seam_deep;
- shell piece: 3 — core, core_deep, seam_deep;
- core: 4.

The floor is 132 hot, 110 mix and 57 core tris.

## Stage 5+6 — Lighting and VFX

Builder: `m009.py` (`SEAM_LIGHT`, `HEAT_FX`, `EMBER_FX`, `SOCKETS`, `_fx_point`, `_vfx`). No geometry, UV or colour
changes (hero 2892 tris, unchanged). Each socket is placed at `(az, el, out)` from C0: `out` studs past the main mass's
surface (`_rho`) along that direction, so it sits in the open just outside a seam lip.

### Stage 5: Lighting

- **Neon set confirmed** (read back via the MCP, emission ≥ 1.0):
  - hero: `m009_seam_ember` (306 tris), `m009_core` (514), `m009_core_x_hot_50` (109) and `m009_core_hot` (115);
  - shell piece: ember, core and core_deep;
  - core part: core_deep, core, core_x_hot_50 and hot.
  - `m009_seam_lip` stays solid (emission 0), as the dark edge round each opening.
  - The renders read right: a dark lip, then deep red, orange and hot-floor Neon. No halo.
- **One seam PointLight**, carried by the `heat_glow_1` socket at the lobe seam's widest jog `(242, 3, 0.8)`:
  - `#FF7A22`, brightness 0.7, range 6, flicker, **shadows on**;
  - 0.65 studs clear of the hero (BVH), outside the solid; the preview light (socket + 0.25 z) is 0.72 clear.
  - The shadows keep the light out of the meteor and off the rim behind it.
- **Rocks with VFX on:**
  - front34 front rocks `#9A857A` against the sheet's `#A18A7D`/`#A0887B` (Δ −7/−5/−3) ✓;
  - front34 lobe-side rocks `#8E7A70`.
  - Light off vs on, same views: rocks, shell and crack all changed by ≤ 1 level. No peach and no halo.
- **No back light.** A dimmer second light (`#FF7A22`, 0.4, range 5, shadows) outside the back-right seam's jog was
  tried. It changed the rear and rear34 shell, crack and rocks by ≤ 1 level, so it was dropped:
  - the Neon seams carry the rear views;
  - a shadowed PointLight is not free in Roblox.
  - That socket keeps its shimmer only.
- **Studio:**
  - The light is the socket's PointLight (Attachment at the socket):
    - Brightness 0.7, Range 6 × vfx_scale (1.0), Color `#FF7A22`, Shadows true;
    - flicker animated in game, around that brightness.
  - Neon pieces need no light; keep `Lighting` bloom low (the sheet draws none).

### Stage 6: VFX

- **Sheet:** glowing seams. No halo, smoke or bloom is drawn; heat shimmer and a few embers are implied.
- **heat_glow (shimmer):** faint `glow_soft` puffs drifting up off the seams.
  - Size 0.5–0.8 (the kind's default is 1.0–1.4); transparency 0.78 → 1; speed 0.4–0.7; spread 8; lifetime 0.8–1.3.
  - Colour `#FC8917` → `#F75610` (the sheet's crack hot and orange).
  - The crack always shows through: front34 lobe crack median `#D25E20` with VFX on (`#E85B1F` off; sheet `#E24515`).
- **embers:** sparse, small `ember_dot` sparks rising from the seams.
  - Size 0.18 → 0.05; colour `#FDBD40` → `#F75610`; speed 1–2; spread 20; drag 0.8; acceleration +0.8 up;
    lifetime 1–2.
  - Spawn box 0.3 cube, so every spawn point is within 0.26 of the socket, which is about 0.3 off the lip.
- **None inside the mesh:**
  - every socket is outside the hero (BVH parity);
  - each emitter box was sampled on a 5³ grid: 0 of 125 points inside, for every socket;
  - an earlier upper-run box at out 0.3 had 2 of 125 points inside, so it moved to out 0.4 and shrank to 0.5 × 0.3 × 0.5.

### Sockets (children of `IronMeteorDeposit`, vfx_scale 1.0)

Positions are hero-local Blender studs (x, y, z), with Roblox axes (x, z, −y) relative to the hero's origin.
Clear = BVH distance from the hero; box min = closest emitter-box grid point.

| Socket | Kind | Where `(az, el, out)` | Blender local | Roblox | Clear / box min | Emitter | Light |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `VFX_IronMeteorDeposit_heat_glow_1` | heat_glow | lobe seam, descent's widest jog `(242, 3, 0.8)` | (−1.711, −4.698, 3.571) | (−1.711, 3.571, 4.698) | 0.652 / 0.295 | rate 2.5, shape 0.5 × 0.4 × 0.5 | `#FF7A22` 0.7, range 6, flicker, shadows |
| `VFX_IronMeteorDeposit_heat_glow_2` | heat_glow | lobe seam, upper run `(222, 18, 0.4)` | (−2.648, −3.162, 4.771) | (−2.648, 4.771, 3.162) | 0.313 / 0.096 | rate 2.0, shape 0.5 × 0.3 × 0.5 | none |
| `VFX_IronMeteorDeposit_heat_glow_3` | heat_glow | back-right seam's jog `(406, 9, 0.6)` (rear views) | (4.242, 3.519, 4.104) | (4.242, 4.104, −3.519) | 0.588 / 0.316 | rate 1.5, shape 0.5 × 0.4 × 0.5 | none |
| `VFX_IronMeteorDeposit_embers_1` | embers | lobe seam, upper run `(218, 18, 0.3)` | (−2.823, −2.897, 4.759) | (−2.823, 4.759, 2.897) | 0.301 / 0.106 | rate 3.0, shape 0.3³ | none |
| `VFX_IronMeteorDeposit_embers_2` | embers | front-right seam, its top `(302, 42, 0.3)` | (2.516, −3.010, 6.356) | (2.516, 6.356, 3.010) | 0.310 / — | rate 1.5, shape 0.3³ | none |

Re-measured through the MCP after the Stage 1 fixes (verifier round 1). The hero's origin moved with the wider rim
(13.36 × 11.88), and embers_2 moved with the turned front-right seam. Clear is the BVH distance to the hero. The box
minimums are from Stage 5+6, before the move; embers_2's was not re-sampled.

The heat_glow light is null on sockets 2 and 3: an explicit override replacing the kind's default light.
In all, about 6 heat puffs a second and about 4.5 embers a second.

### Export (exporter code read; not exported)

- `export_kit_roblox.sockets()` writes every child of the hero that has `vfx_kind` into the asset's `vfx` list, with
  name, kind, Roblox position relative to the origin, vfx_scale and the full `roblox` spec. That is 5 entries here.
- STATS counts them in `vfxSockets` (`… N vfx sockets`).
- Keys with emission ≥ `GLOW_EMISSION` (1.0) become `glow:<key>` pieces (material Neon, the key's hex, no collision).
  Each one is under `MAX_TRIS` (10000), so none is split. The `glow` count in STATS comes from:
  - hero: 5 (ember, core, core_x_hot_50, hot, seam_deep);
  - shell piece: 3 (core, core_deep, seam_deep);
  - core: 4;
  - impact rock: 0.
  - That is 12 Neon glow pieces in all from M009. These counts are after Stage 4's final fix for verifier round 1;
    it was 4 / 3 / 4 = 11 before.

### Renders

`renders/models/M009/` (VFX on): faint shimmer at the lobe jog, the upper run and the back-right seam, and a few small
embers over the lobe and front-right seams. No halo, smoke or bloom. The `.blend` was saved through the MCP.

### Left for the verifier

- Check the shimmer and embers stay subtle against the sheet. The sheet only implies them.
- Check the front34 rocks stay within 10 of `#A18A7D` with VFX on (measured `#9A857A`).

### Stage 1 fixes (after verifier round 1)

Verifier round 1 scored 6.5/10. The one blocking issue was crack B (the front-right seam): it sat on the limb in
front34 and showed only its dark lip. Everything is changed in `m009.py`, keeping stage 2's `_polish` and `_uv`, stage
4's colour pass and stage 5+6's sockets.

The model was rebuilt with `m009.build()` and the `.blend` saved through the MCP. The last measured build and the saved
file have the same parameters.

**1. Crack B: the front-right seam faces the hero camera.**

- **Turned 6–7° towards front34.**
  - Its nodes moved from az −52..−65 to about −58..−71: `FR_SEAM` (302, 52) … (289, −72). The crown junction and
    the front-right embers socket (now (302, 42, 0.3)) moved with it.
  - 9° was tried first. It put the front view's crack at x 0.67–0.69, under the 0.70 floor. The front view caps the
    turn: at el 28–41 the crack needs cos(el)·cos(az) ≥ about 0.31.
- **Proud far side (`PROUD`, `proud()`).** Along the open run on side A (the side away from the camera), a lofted
  plate stands proud of the main surface.
  - It is 0.10 at the lip and falls flush 1.6 out. It is tapered with G and buried (−0.03) where the gap closes.
  - It is unioned into the outer in `_outer_obj`. A single `union_loose` over hulls and plate came out empty, so the
    plate gets its own union.
  - Measured at the lip: the far side is 0.04–0.10 above the centre line, the near side 0.03–0.11 below.
  - Lifts of 0.12–0.20 were tried. The extra riser only added dark lip or ember, not width.
- **Per-seam wall rows** (`SEAM_ROWS`, `SEAM_CHAMFER`, `SEAM_MATS`; the defaults are unchanged for the other three
  seams).
  - From front34, about 0.38 of the far wall shows (opening about 0.5, roughly 53° off the surface normal). With the
    default rows, that was all lip, the proud riser and ember.
  - The front-right seam's rows are therefore 0.07 T (lip) and 0.14 T (ember), with no lip chamfer.
  - A row 0.02 above the surface parts off the proud riser, which takes the ember key. The lip stays a thin dark line,
    and the gradient (lip → ember → orange core → hot floor) is unchanged.
- **Wider gap:** G up to 0.62 at el 14–28 (it was 0.58), and 0.52 at the top run.

**Crack B numbers** (`crackb2.py`: box x 0.78–0.88, h 0.40–0.90 of the dark box; widths per row as % of the box
width):

| View | Position (x, h) | Width | Colour (vivid median / dark / light) | Accept |
| --- | --- | --- | --- | --- |
| front34 | (0.77, h0.91) → (0.81, h0.77) → (0.84, h0.71) → (0.85, h0.50). At x 0.80–0.84 for h 0.50–0.80. | Median 1.9 %, max 3.3 %; 60 of 140 rows at or over 2 %. At x 0.80–0.84: 2.6–3.1 % at h0.74–0.80, 1.7–1.9 % at h0.59–0.71. | `#D75723` / `#70312B` / `#F86223` (Δ 16 / 5 / 2 from `#E75221`; the orange pixels' own median is `#F76122`) | Colour and position pass. Width is about 2 % (median 1.9 %). |
| front | (0.70, h0.88) → (0.69, h0.81) → (0.72, h0.69) → (0.70, h0.50) → (0.71, h0.38) | Median 4.3 %, max 5.0 % (sheet 4 %) | `#F76123` | x ≥ 0.70 except 2 rows at 0.69 (h0.77–0.81) |
| side | (0.19, h0.72) → (0.14, h0.53), 1.0–1.7 % | | | Sheet (0.33 → 0.49): not reconcilable (see Stage 1) |
| top | x 0.68–0.70 at front 0.12–0.21, 2.1–5.3 % | | | Sheet (0.87, 0.63 → 0.78, 0.28) |
| rear34 | Back-left at x 0.87–0.88, 0.5 % (crack B there) | | | Sheet 0.91 |

- **Before this round**, front34's crack B was a dark sliver at the limb (`#713431`, about 1 % wide, at most 0.5 %
  orange).
- **Probe across the front-right seam** (el / G / lip-to-lip / depth):
  - 42: 0.52 / 0.49 / 0.65.
  - 33: 0.59 / 0.55 / 0.69.
  - 14: 0.60 / 0.55 / 0.64.
  - 0: 0.42 / 0.39 / 0.66.
  - −9: 0.15 / 0.15 / 0.70.

**2. Side and top views; rim rocks ring outside the bulge.**

- **Orange share** (VFX on, `mymeasure.py`):
  - side 0.8 % (it was 0.9 % by the verifier's count; ours 0.6 % before);
  - top 0.9 % (it was 0.4 %);
  - against the sheet's 3.6 % and 2.3 %.
  - The front-right seam now shows in the top view (x 0.68–0.70, 2–5 % wide). The side view still sees both meridian
    seams at its limbs. The sheet's side view repeats the hero composition (a lobe on its left), so no one placement
    serves it. This is recorded, not chased.
- **Rim.** In the top view the rocks hid under the 10.7-wide meteor's bulge: from above, the rim reached only 1.15× the
  meteor's width, against the sheet's 1.2–1.4×.
  - Every rim rock's outer edge is now pushed out to at least `RIM_OUT` = 1.3 beyond the meteor's widest reach towards
    it (`_bulge`). The push is capped at 1.0, so the rocks at az −62 and −96, already 1.4–1.8 out, are unchanged.
  - Pushes: −128: 0.94; −158: 0.35; −188: 1.0 (capped, now 1.15 out); −30: 0.33; 0: 0.39; 32: 0.40; 63: 0.60; 95: 0.73;
    127: 0.49; 160: 0.93.
  - Each rock keeps its inner edge in the foot: its centre moves push / 2 and it grows by the push across.
  - The 4 small stones sit at least `STONE_OUT` = 0.8 beyond the bulge.
  - The hero is now 13.36 × 11.88 (the rim is 1.25× the meteor's width) and has 3 shells: the meteor with all 12 rim
    rocks, plus 2 loose stones.

**3. The Lobe shell piece is chunky.**

- The tail was the Lobe sector running on round the main mass's lower shell to the back-left seam (az 124 → 258): a
  long curved strip.
- **Lower ends.**
  - The back-left seam meets the crown ring at el 6, not 50. Above that, the seam (still cut: `BL_FULL`) parts the
    Crown from the Back.
  - `CROWN_LEFT` dips to el 0–6 behind the lobe. Trimming at el 20–26 still left a spike up the seam.
- **New closed seam.** `LOBE_BACK` runs down the lobe's back crease: (204, 14) → (196, 2) → (186, −12) → (180, −32) →
  the ground at az 179.
  - The Lobe piece is now the lobe's own sector, az about 180–258.
  - The strip from az 124 to 179 is a sixth piece, `BackLeft`, used only in the exploded render. So the exploded shot
    shows 6 pieces round the core; the sheet shows 5.
- `IronMeteorShellPiece` (Lobe) is now 5.84 × 4.47 × 4.52 and 386 tris: a chunky lobe block, dark faceted outside, a
  large orange inner face and thick cut ends (`part_shell`, `part_shell_in`). It was 5.84 × 8.26 × 4.52.

**4. The underside disc is larger.**

- `FLAT` and `_flatten`: the core's (and the hollow's) points below z 1.0 move out from the meteor's axis, by up to 1.7×
  at the ground. They are clamped 0.45 inside the main hull (0.50 for the hollow), so the shell ring round the disc
  stays at least 0.45 wide.
- The disc is 4.76 × 4.09, up from 4.0 × 3.6. That is 0.45 of the meteor's width, but only 0.36 of the new, wider rim
  (13.36). The clamp binds: at z = 0 the main hull is only about 2.9 from the axis.
- Flattening from z 2.0 was tried. The core's hull facets carried the bulge up to el −15, and the seams there lost depth
  (0.52–0.57). From z 1.0, depth above the rocks is back to 0.63–0.69. It is 0.47–0.54 only at el −40..−50, at and
  below the ground among the rocks.
- `_profile` clamps the thickness it uses for the wall rows at ≥ 0.55. Below ground, the thinner shell had folded the
  back-right tube, leaving 3 non-manifold edges after the core union.

**5. Exploded render:** `EXPL_PULL` 3.2 → 4.8 and `EXPL_CROWN` 2.8 → 4.2. The pieces now stand clear of the core.

**Checks (final build, MCP)**

| Object | Tris / budget | Size | Shells | Non-manifold / boundary | Inner shells / self-hits | Min corner | UV overlaps / flipped |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IronMeteorDeposit | 3028 / 4000 | 13.36 × 11.88 × 7.41 | 3 | 0 / 0 | 0 / 0 | 5.0° | 0 / 0 |
| IronMeteorShellPiece | 386 / 1000 | 5.84 × 4.47 × 4.52 | 1 | 0 / 0 | 0 / 0 | 5.06° | 0 / 0 |
| IronMeteorCore | 76 / 1000 | 8.34 × 8.07 × 7.14 | 1 | 0 / 0 | 0 / 0 | 13.8° | 0 / 0 |
| IronMeteorImpactRock | 44 / 1000 | 2.41 × 2.11 × 1.25 | 1 | 0 / 0 | 0 / 0 | 16.7° | 0 / 0 |

- Normals are outward, with no n-gons and no zero-area faces. `K.check` reports nothing.
- **Sockets.** All 5 are outside the solid (BVH parity). Nearest surface: embers_1 0.30, embers_2 (front-right top)
  0.31, heat_glow_1 0.65, heat_glow_2 0.31, heat_glow_3 0.59.
- **Other seams' probe** (depth): lobe 0.62–0.63; back-right 0.63–0.71 (0.54 at el −40); back-left 0.65–0.69.
- **Orange share per view** (ours / sheet):
  - front34: 6.8 / 3.6 %;
  - rear34: 2.9 / 2.3 %;
  - front: 7.3 / 3.7 %;
  - side: 0.8 / 3.6 %;
  - rear: 2.8 / 2.4 %;
  - top: 0.9 / 2.3 %.
  - front34 and front run high: the lobe seam, plus crack B's wider gap. Stage 4 could cool the lobe seam's floor if
    the verifier asks.

## Result

Verifier round 2: PASS, 7.5/10, no blocking issues. Round 1 had failed at 6.5 because crack B showed only its dark lip in the hero view.

The cracks are now real gaps through a 0.6-thick shell: openings of 0.32–0.55, depth of 0.62–0.70. Each runs from a dark lip, through deep-red and orange walls, to a hot floor.

The orange share is deliberately above the sheet's (about 6 % against 3.7 %), because the user asked for apparent cracks.

Open minors:
- **Side, top and rear34 views:** they show the cracks only at the limbs. This is recorded as a sheet conflict.
- **Crack B:** it has no hot floor and stays narrow (1.9 % against about 3 %).
- **Underside disc:** small and dull. It is never seen in game.
- **Thin rim from above.**
- **Part views:** `part_shell` shows no orange from outside, and the exploded render has 6 pieces where the sheet has 5.
- **Shell, front view:** about 8 levels dark.
